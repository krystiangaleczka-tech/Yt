"""Strumień na telewizor (AirPlay z Safari): HLS z ujęć po kolei i z osi montażu.

Safari przekazuje telewizorowi adres strumienia, a telewizor sam pobiera playlistę i odcinki, więc Studio podaje
adres w sieci lokalnej (Vite nasłuchuje na 0.0.0.0 i przekazuje /api dalej). Nic nie trafia na dysk: odcinki powstają
na żądanie (z wyprzedzeniem o dwa) i czekają w pamięci.

- Ujęcia: jeden odcinek na ujęcie. Gotowy klip H.264 jest tylko przepakowany do MPEG-TS (bez kodowania); inne ujęcia
  (obraz z ruchem, szablon) renderuje ten sam kompozytor co eksport. Między ujęciami jest EXT-X-DISCONTINUITY,
  więc klipy mogą mieć różne parametry.
- Montaż: odcinki po 6 s renderowane z osi (slice_project + build_command). Przejście, które przecina granicę
  odcinka, wychodzi jako cięcie — to podgląd na telewizor, nie eksport.
"""
from __future__ import annotations

import math
import re
import socket
import subprocess
import tempfile
import threading
from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from fastapi import Response

from studio_core.media import asset_path, probe
from studio_core.models import Clip, duration, fps

SEGMENT_SECONDS = 6
PLAYLIST = "application/vnd.apple.mpegurl"
TS = "video/mp2t"
# Krycie 100% bez animacji: filtr geq liczy każdy piksel na jednym wątku i nic nie zmienia (render 6 s trwał 10 s,
# bez niego 0,7 s). Gdy kompozytor kiedyś zapisze to inaczej, wzorzec po prostu nie trafi i render idzie wolniej.
NOOP_OPACITY = re.compile(r"format=gbrap,geq=r='r\(X,Y\)':g='g\(X,Y\)':b='b\(X,Y\)':a='alpha\(X,Y\)\*\(min\(1,1\)\)',")


def lan_address() -> str | None:
    """Adres IPv4 tego komputera w sieci lokalnej (bez wysyłania pakietów: connect na UDP tylko wybiera trasę)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 9))
            address = s.getsockname()[0]
    except OSError:
        return None
    return None if address.startswith("127.") or address == "0.0.0.0" else address


class Segments:
    """Odcinki w pamięci: ten sam odcinek nie renderuje się dwa razy naraz, najwyżej dwa rendery jednocześnie."""

    def __init__(self, size=16):
        self.size = size
        self.lock = threading.Lock()
        self.done: OrderedDict[tuple, bytes] = OrderedDict()
        self.running: dict[tuple, Future] = {}
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="docos-tv")

    def _start(self, key, make) -> Future:
        future = self.pool.submit(self._run, key, make)
        self.running[key] = future
        return future

    def _run(self, key, make) -> bytes:
        try:
            data = make()
            with self.lock:
                self.done[key] = data
                while len(self.done) > self.size:
                    self.done.popitem(last=False)
            return data
        finally:
            with self.lock:
                self.running.pop(key, None)

    def get(self, key, make) -> bytes:
        with self.lock:
            if key in self.done:
                self.done.move_to_end(key)
                return self.done[key]
            future = self.running.get(key) or self._start(key, make)
        return future.result()

    def prefetch(self, key, make):
        with self.lock:
            if key not in self.done and key not in self.running:
                self._start(key, make)


def ffmpeg(command: list[str], timeout=180) -> bytes:
    result = subprocess.run(command, capture_output=True, timeout=timeout)
    if result.returncode:
        detail = result.stderr.decode(errors="replace")[-1500:].strip() or "brak komunikatu"
        raise ValueError(f"FFmpeg (strumień na TV, kod {result.returncode}): {detail}")
    return result.stdout


def to_ts(source: Path, offset: float | None = None) -> bytes:
    """Przepakowuje render (mkv z H.264) do MPEG-TS; dźwięk w AAC, jak wymaga HLS."""
    return ffmpeg(["ffmpeg", "-v", "error", "-i", str(source), "-map", "0:v:0", "-map", "0:a?", "-c:v", "copy",
                   "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
                   *(["-output_ts_offset", f"{offset:.6f}"] if offset else []), "-f", "mpegts", "pipe:1"])


def compose(store, draft, offset: float | None = None) -> bytes:
    """Renderuje szkic osi (jak eksport, w pełnej rozdzielczości sekwencji) i zwraca odcinek MPEG-TS."""
    from studio_timeline.render import build_command

    with tempfile.TemporaryDirectory(prefix="docos-tv-") as folder:
        work = Path(folder)
        output = work / "segment.mkv"
        command = build_command(store, draft, output, preview=False, temp=work / "layers")
        command = [x for x in command if x not in ("-progress", "pipe:1", "-nostats")]
        command[command.index("-filter_complex_threads") + 1] = "2"
        command[command.index("-filter_complex") + 1] = NOOP_OPACITY.sub("", command[command.index("-filter_complex") + 1])
        ffmpeg(command)
        return to_ts(output, offset)


def playlist(entries: list[tuple[float, str]], discontinuity: bool) -> str:
    lines = ["#EXTM3U", "#EXT-X-VERSION:3", "#EXT-X-PLAYLIST-TYPE:VOD",
             f"#EXT-X-TARGETDURATION:{max(1, math.ceil(max((d for d, _ in entries), default=1)))}",
             "#EXT-X-MEDIA-SEQUENCE:0"]
    if not discontinuity:
        lines.append("#EXT-X-INDEPENDENT-SEGMENTS")
    for index, (length, uri) in enumerate(entries):
        if discontinuity and index:
            lines.append("#EXT-X-DISCONTINUITY")
        lines += [f"#EXTINF:{length:.3f},", uri]
    lines.append("#EXT-X-ENDLIST")
    return "\n".join(lines) + "\n"


def register_tv(app, store):
    segments = Segments()
    codecs: dict[str, bool] = {}

    @app.get("/api/tv/address")
    def tv_address():
        return {"address": lan_address()}

    def copyable(path: Path, sha: str) -> bool:
        """Klip, który da się wysłać bez kodowania: H.264 w 4:2:0 (tak renderują się ujęcia animacji)."""
        if sha not in codecs:
            try:
                video = next((s for s in probe(path)["streams"] if s.get("codec_type") == "video"), {})
                codecs[sha] = video.get("codec_name") == "h264" and video.get("pix_fmt") in ("yuv420p", "yuvj420p")
            except (subprocess.SubprocessError, ValueError, KeyError):
                codecs[sha] = False
        return codecs[sha]

    def shot_segment(project, scene) -> bytes:
        rate = fps(project)
        seconds = scene.duration / rate
        asset = next((a for a in project.assets if a.id == scene.asset_id), None)
        if asset and asset.kind == "video" and scene.template in ("", "media"):
            path = asset_path(store, project.id, asset.id, project=project)
            if path.is_file() and asset.duration + 1 / rate >= seconds and copyable(path, asset.sha256):
                return ffmpeg(["ffmpeg", "-v", "error", "-i", str(path), "-t", f"{seconds:.6f}", "-map", "0:v:0", "-an",
                               "-c:v", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "mpegts", "pipe:1"])
        if asset or scene.template not in ("", "media"):
            clip = Clip(track_id="v1", scene_id=scene.id, asset_id=scene.asset_id, title=scene.title, start=0,
                        duration=scene.duration, animation=scene.animation, template=scene.template or "media",
                        parameters=scene.parameters, asset_ids=scene.asset_ids)
            draft = project.model_copy(update={
                "sequence": project.sequence.model_copy(update={"clips": [clip]}),
                "legacy": {**project.legacy, "_render_duration": scene.duration},
            })
            return compose(store, draft)
        # Ujęcie bez materiału: plansza w kolorze tła podglądu, żeby rytm sekwencji się zgadzał.
        s = project.sequence
        return ffmpeg(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                       f"color=c=0x101318:s={s.width}x{s.height}:r={s.fps_num}/{s.fps_den}:d={seconds:.6f}",
                       "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-f", "mpegts", "pipe:1"])

    @app.get("/api/projects/{project_id}/tv/shots.m3u8")
    def tv_shots(project_id: str, start: int = 0):
        project = store.get(project_id)
        rate = fps(project)
        scenes = project.scenes[max(0, start):]
        if not scenes:
            raise ValueError("Brak ujęć do odtworzenia")
        entries = [(scene.duration / rate, f"shot/{scene.id}.ts?r={project.revision}") for scene in scenes]
        return Response(playlist(entries, discontinuity=True), media_type=PLAYLIST, headers={"Cache-Control": "no-store"})

    @app.get("/api/projects/{project_id}/tv/shot/{scene_id}.ts")
    def tv_shot(project_id: str, scene_id: str):
        project = store.get(project_id)
        scene = next((s for s in project.scenes if s.id == scene_id), None)
        if scene is None:
            raise FileNotFoundError("Nie ma takiego ujęcia")
        data = segments.get(("shot", project.id, project.revision, scene.id), lambda: shot_segment(project, scene))
        return Response(data, media_type=TS)

    def montage_range(project, begin: int) -> tuple[int, int]:
        step = max(1, round(fps(project) * SEGMENT_SECONDS))
        return begin, min(duration(project), begin + step)

    def montage_segment(project, begin: int, end: int) -> bytes:
        from studio_timeline.cache import slice_project

        return compose(store, slice_project(project, begin, end), begin / fps(project))

    @app.get("/api/projects/{project_id}/tv/montage.m3u8")
    def tv_montage(project_id: str, start: int = 0):
        project = store.get(project_id)
        rate, total = fps(project), duration(project)
        if total <= 0:
            raise ValueError("Oś czasu jest pusta")
        begin, entries = max(0, min(int(start), total - 1)), []
        while begin < total:
            _, end = montage_range(project, begin)
            entries.append(((end - begin) / rate, f"montage/{begin}-{end}.ts?r={project.revision}"))
            begin = end
        return Response(playlist(entries, discontinuity=False), media_type=PLAYLIST, headers={"Cache-Control": "no-store"})

    @app.get("/api/projects/{project_id}/tv/montage/{begin}-{end}.ts")
    def tv_montage_segment(project_id: str, begin: int, end: int):
        project = store.get(project_id)
        total = duration(project)
        if not 0 <= begin < end <= total:
            raise ValueError("Odcinek poza osią")
        key = ("montage", project.id, project.revision)
        data = segments.get(key + (begin, end), lambda: montage_segment(project, begin, end))
        # Telewizor zaraz poprosi o następne odcinki: renderujemy je z wyprzedzeniem.
        ahead = end
        for _ in range(2):
            if ahead >= total:
                break
            first, last = montage_range(project, ahead)
            segments.prefetch(key + (first, last), lambda first=first, last=last: montage_segment(project, first, last))
            ahead = last
        return Response(data, media_type=TS)
