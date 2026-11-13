"""Wgrywa „Pierwszy cesarz” (wersja angielska, lektor z output/pierwszy-cesarz/lektor_en) do DocOS Studio ujęcie po ujęciu,
żeby reżyser obejrzał lektora i rytm w Studio przed renderem 1440p.

uruchom (Studio musi działać, ffmpeg w PATH):
  set JEZYK=en
  python -I output/pierwszy-cesarz/studio_pc.py [--port 8876] [--klipy klipy_en_1440p] [--projekt prj_…] [--tytul …]
- długości ujęć liczy dane.ujecia() z nagrań lektora (lektor_en/*.json), tak jak przyszły render;
- obraz: gotowe klipy ujęć (--klipy, stary render) zmniejszone do 720p i dopasowane tempem do nowej długości ujęcia
  (setpts) — animacje ujęć i tak rozciągają się na długość ujęcia, więc podgląd ruchu odpowiada przyszłemu renderowi;
- ścieżka Lektor (a1): kwestie w swoich oknach (start ujęcia + 0,6 s), w opisie ujęcia tekst ze znacznikami emocji;
- bez muzyki i efektów (na PC ich nie ma), bez eksportu. Kopie klipów: build/studio_klipy (można skasować).
"""
import argparse
import json
import math
import mimetypes
import os
import re
import subprocess
import sys
import urllib.request
import uuid
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "docs/filmy/pierwszy-cesarz/ujecia"))
FPS_IN, FPS = 24, 30
KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta"}
RUCH = {"stat": "statyczna", "naj": "najazd", "odj": "odjazd", "pan": "panorama", "jaz": "jazda", "szarp": "szarpnięcie"}


class Api:
    def __init__(self, port):
        self.base = f"http://127.0.0.1:{port}/api"

    def call(self, path, body=None, method=None):
        req = urllib.request.Request(self.base + path, method=method or ("POST" if body is not None else "GET"),
                                     headers={"Content-Type": "application/json", "X-Docos-Request": "1"},
                                     data=None if body is None else json.dumps(body).encode())
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit(f"{path}: {e.code} {e.read().decode('utf-8', 'replace')[:600]}")

    def upload(self, pid, path, name):
        b = uuid.uuid4().hex
        head = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
                f"Content-Type: {mimetypes.guess_type(name)[0] or 'application/octet-stream'}\r\n\r\n").encode()
        req = urllib.request.Request(self.base + f"/projects/{pid}/media", method="POST",
                                     data=head + Path(path).read_bytes() + f"\r\n--{b}--\r\n".encode(),
                                     headers={"Content-Type": f"multipart/form-data; boundary={b}", "X-Docos-Request": "1"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)["asset"]["id"]


def title_of(desc):
    head = re.split(r"[:;]", desc)[0].strip()
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


def wav_len(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def klatki(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def dopasuj(job):
    """Stary klip ujęcia → 720p o długości nowego ujęcia (tempo obrazu × nowa/stara długość), zapas 0,25 s na końcu."""
    src, dur, out = job
    if out.exists() and out.stat().st_size > 0:
        return out
    old = klatki(src) / FPS_IN
    k = dur / old
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-vf",
                    f"setpts=PTS*{k:.6f},fps={FPS_IN},scale=1280:720:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.25",
                    "-an", "-t", f"{dur + 0.25:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-threads", "2",
                    "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def main():
    from dane import LEKTOR, kwestia, okno_kwestii, ujecia
    aktorskie = json.loads((HERE / "aktorskie_en.json").read_text(encoding="utf-8"))
    api = Api(ARGS.port)
    tmp = HERE / "build" / "studio_klipy"
    tmp.mkdir(parents=True, exist_ok=True)
    if ARGS.projekt:
        pid = ARGS.projekt
    else:
        found = [p for p in api.call("/projects") if p["title"] == ARGS.tytul]
        pid = found[0]["id"] if found else api.call("/projects", {"title": ARGS.tytul, "language": "en", "production_mode": "documentary"})["id"]
    p = api.call(f"/projects/{pid}")
    have = {s["id"] for s in p["scenes"]}
    UJ = ujecia()
    meta, jobs, t = [], [], 0.0
    for akt, k, klucz, kadr, ruch, sec, opis, dzwiek in UJ:
        f0, f1 = round(t * FPS), round((t + sec) * FPS)
        t += sec
        sid = f"scene_d{akt:02d}_{k:02d}"
        if sid in have:
            continue
        out = tmp / f"d{akt:02d}_{k:02d}.mp4"
        jobs.append((Path(ARGS.klipy) / f"d{akt:02d}_{k:02d}.mp4", (f1 - f0) / FPS, out))
        meta.append((akt, k, klucz, kadr, ruch, opis, dzwiek, f0, f1 - f0, out))
    print(f"projekt {pid}: ujęć {len(UJ)}, film {t:.1f} s, do wgrania {len(meta)}", flush=True)
    with ThreadPoolExecutor(ARGS.j) as ex:
        for n, _ in enumerate(ex.map(dopasuj, jobs), 1):
            if n % 20 == 0:
                print(f"  klipy: {n}/{len(jobs)}", flush=True)
    scenes, clips = [], []
    for akt, k, klucz, kadr, ruch, opis, dzwiek, f0, fd, out in meta:
        sid = f"scene_d{akt:02d}_{k:02d}"
        txt = kwestia(dzwiek) or ""
        aid = api.upload(pid, out, f"d{akt:02d}_{k:02d} {klucz}.mp4")
        description = f"({KADR.get(kadr, kadr)} · {RUCH.get(ruch, ruch)}) {opis}"
        if txt and klucz in aktorskie:
            description += f"\nLektor (Chatterbox Turbo, znaczniki emocji): {aktorskie[klucz]}"
        elif dzwiek and not txt:
            description += f"\nDźwięk: {dzwiek}"
        sc = {"id": sid, "title": ("Karta · " if kadr == "TYT" else "") + title_of(opis), "narration": txt,
              "description": description[:3000], "start": f0, "duration": fd, "timing": "measured", "mode": "upload",
              "animation": "static", "asset_id": aid, "role": "reconstruction",
              "legacy": {"flow_section_id": f"seq_a{akt:02d}", "akt": akt, "ujecie": k, "klucz": klucz,
                         "zrodlo": "output/pierwszy-cesarz/ujecia1.py, ujecia2.py (render.py)", "lektor": "Chatterbox Turbo"}}
        clips.append({"track_id": "v1", "asset_id": aid, "scene_id": sid, "title": sc["title"][:120], "start": f0, "duration": fd})
        wav = LEKTOR / f"{klucz}.wav"
        if txt and wav.exists():
            vaid = api.upload(pid, wav, f"lektor {klucz}.wav")
            sc["voice_asset_id"] = vaid
            clips.append({"track_id": "a1", "asset_id": vaid, "scene_id": sid, "title": f"Lektor · {txt[:80]}",
                          "start": f0 + round(okno_kwestii(dzwiek)[0] * FPS), "duration": max(1, math.ceil(wav_len(wav) * FPS))})
        scenes.append(sc)
    p = api.call(f"/projects/{pid}")
    p = api.call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": p["scenes"] + scenes}}, "PATCH")
    ops = [{"type": "add_clip", "clip": c} for c in clips]
    for k in range(0, len(ops), 200):
        p = api.call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[k:k + 200]})
    print(f"gotowe: ujęć {len(p['scenes'])}, klipów na osi {len(p['sequence']['clips'])}, rewizja {p['revision']}", flush=True)
    try:
        api.call(f"/projects/{pid}/flow/log", {"entry": {
            "who": "studio_pc.py", "kind": "wgranie",
            "summary": f"Pierwszy cesarz EN do akceptacji: {len(scenes)} ujęć, nowy lektor Chatterbox Turbo ze znacznikami emocji "
                       f"(film {t:.0f} s); obraz ze starego renderu 1440p dopasowany tempem do nowych długości ujęć",
            "details": "Render 1440p dopiero po akceptacji reżysera. Teksty ze znacznikami: output/pierwszy-cesarz/aktorskie_en.json; "
                       "poprzedni lektor (VoxCPM2): output/pierwszy-cesarz/lektor_en_voxcpm.",
            "files": ["output/pierwszy-cesarz/aktorskie_en.json", "output/pierwszy-cesarz/lektor_en.py", "output/pierwszy-cesarz/studio_pc.py"]}})
    except SystemExit as e:
        print("dziennik:", e)
    print(pid)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8876)
    ap.add_argument("--klipy", default=str(REPO / "klipy_en_1440p"))
    ap.add_argument("--projekt", default="")
    ap.add_argument("-j", type=int, default=3)
    ap.add_argument("--tytul", default="Pierwszy cesarz · The First Emperor (EN, lektor Turbo)")
    ARGS = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if os.environ.get("JEZYK") != "en":
        raise SystemExit("ustaw JEZYK=en (wersja angielska: kwestie_en.py, lektor_en/)")
    main()
