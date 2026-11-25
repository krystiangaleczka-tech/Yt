"""Live hunt: record a Twitch stream, read its public chat, cut the moment when chat explodes.

  streamlink -> ffmpeg -> 10-second .ts segments (only the last N minutes are kept)
  anonymous IRC chat -> SpikeDetector (distinct chatters in 10 s vs. baseline)
  spike at T -> wait `after` s -> join segments [T-before, T+after] -> transcribe ->
  (smart: AI says keep/drop + writes the hook) -> render a Short with status "new"

Twitch only. Kick and YouTube Live: make Shorts from the VOD link after the stream.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from . import ai
from .chat import SpikeDetector, TwitchChat
from .config import Workspace, write_json
from .pick import short_name
from .render import render_pick
from .transcribe import text_between, transcribe
from .util import log, media_info, run

SEG = 10


def streamlink_cmd() -> list[str]:
    return ["streamlink"] if shutil.which("streamlink") else [sys.executable, "-m", "streamlink"]


class Hunt:
    def __init__(self, ws: Workspace, channel: str):
        self.ws = ws
        self.channel = channel.lower()
        cfg = ws.settings()["live"]
        self.cfg = cfg
        self.dir = ws.live / self.channel
        self.buf = self.dir / "buf"
        self.buf.mkdir(parents=True, exist_ok=True)
        self.det = SpikeDetector(cfg["ratio"], cfg["min_per_min"])
        self.chat = TwitchChat(self.channel, self.det.add)
        self.stop_flag = threading.Event()
        self.proc: subprocess.Popen | None = None
        self.events: list[dict] = []
        self.recording = False
        self.thread = threading.Thread(target=self._run, daemon=True)

    # ------------------------------------------------------------ control
    def start(self):
        self.chat.start()
        self.thread.start()
        return self

    def stop(self):
        self.stop_flag.set()
        self.chat.stop_flag.set()
        if self.proc:
            self.proc.terminate()

    def status(self) -> dict:
        st = self.det.stats()
        return {"channel": self.channel, "chat": self.chat.connected, "recording": self.recording,
                "per_min": st["per_min"], "distinct": st["distinct"], "baseline": st["baseline"],
                "events": self.events[-20:]}

    # ------------------------------------------------------------ recorder
    def _record(self):
        sl = streamlink_cmd() + ["--stdout", "--twitch-disable-ads", f"https://www.twitch.tv/{self.channel}",
                                 "720p60,720p,best"]
        ff = ["ffmpeg", "-v", "error", "-i", "-", "-c", "copy", "-f", "segment", "-segment_time", str(SEG),
              "-reset_timestamps", "1", "-strftime", "1", str(self.buf / "%Y%m%d-%H%M%S.ts")]
        p1 = subprocess.Popen(sl, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.proc = subprocess.Popen(ff, stdin=p1.stdout, stderr=subprocess.DEVNULL)
        p1.stdout.close()
        return p1

    def _segments(self) -> list[tuple[float, Path]]:
        out = []
        for p in self.buf.glob("*.ts"):
            try:
                out.append((datetime.strptime(p.stem, "%Y%m%d-%H%M%S").timestamp(), p))
            except ValueError:
                continue
        return sorted(out)

    def _cleanup(self):
        keep = self.cfg["keep_minutes"] * 60
        for t, p in self._segments():
            if t < time.time() - keep - SEG:
                p.unlink(missing_ok=True)

    def _run(self):
        p1 = None
        pending: list[dict] = []
        while not self.stop_flag.is_set():
            if p1 is None or p1.poll() is not None:
                self.recording = False
                p1 = self._record()
                time.sleep(8)
                if p1.poll() is not None:   # offline: try again in a minute
                    self.stop_flag.wait(60)
                    continue
            self.recording = True
            sp = self.det.check()
            if sp:
                sp["cut_at"] = sp["t"] + self.cfg["after"] + SEG + 2
                pending.append(sp)
                self.events.append({"t": int(sp["t"]), "what": f"czat x{sp['ratio']} ({sp['distinct']} osób / 10 s)"})
                log(f"[{self.channel}] skok czatu x{sp['ratio']} {sp['tokens']}")
            for sp in [x for x in pending if time.time() >= x["cut_at"]]:
                pending.remove(sp)
                threading.Thread(target=self._process, args=(sp,), daemon=True).start()
            self._cleanup()
            self.stop_flag.wait(1)
        if p1:
            p1.terminate()

    # ------------------------------------------------------------ cutting
    def cut(self, t_from: float, t_to: float, out: Path) -> Path | None:
        segs = [(t, p) for t, p in self._segments() if t + SEG >= t_from and t <= t_to]
        if not segs:
            return None
        lst = out.with_suffix(".txt")
        lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for _, p in segs), encoding="utf-8")
        joined = out.with_name(out.stem + "_join.ts")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
        off = max(0.0, t_from - segs[0][0])
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{off:.2f}", "-i", joined, "-t", f"{t_to - t_from:.2f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "aac", "-b:a", "192k", out])
        joined.unlink(missing_ok=True)
        lst.unlink(missing_ok=True)
        return out

    def buffer(self) -> Path | None:
        now = time.time()
        out = self.dir / f"buffer_{datetime.now():%Y%m%d-%H%M%S}.mp4"
        return self.cut(now - self.cfg["keep_minutes"] * 60, now, out)

    def _process(self, sp: dict):
        ws = self.ws
        s = ws.settings()
        stamp = datetime.fromtimestamp(sp["t"]).strftime("%Y%m%d-%H%M%S")
        sid = f"live_{self.channel}_{stamp}"
        out = self.dir / f"{sid}.mp4"
        try:
            if not self.cut(sp["t"] - self.cfg["before"], sp["t"] + self.cfg["after"], out):
                return
            audio = ws.src / f"{sid}.m4a"
            run(["ffmpeg", "-y", "-v", "error", "-i", out, "-vn", "-ac", "1", "-c:a", "aac", audio])
            tr = transcribe(audio, ws.src / sid, language=None if s["language"] == "any" else s["language"],
                            model=s["whisper_model"], device=s["whisper_device"])
            dur = media_info(out)["duration"]
            meta = {"id": sid, "title": f"{self.channel} live", "name": self.channel, "platform": "twitch",
                    "url": f"https://www.twitch.tv/{self.channel}", "local_file": str(out), "duration": dur,
                    "live_spike": sp | {"tokens": sp.get("tokens")}, "used": True}
            write_json(ws.src / f"{sid}.meta.json", meta)
            hook = f"{short_name(self.channel)} CHAT WENT CRAZY"
            title = f"{self.channel} live moment in GTA 6"
            keep = True
            if self.cfg.get("mode", "smart") != "free" and ai.available(s):
                prompt = (f"A Twitch chat spiked (x{sp['ratio']}, top words {sp['tokens']}) during {self.channel}'s "
                          f"GTA 6 stream. Transcript of the {dur:.0f}-second clip:\n{text_between(tr, 0, dur)}\n\n"
                          f"Is it a Short a stranger would keep watching? Answer JSON only: "
                          f'{{"keep": true/false, "hook": "MAX 6 WORDS CAPS NAME FIRST", "title": "<=70 chars", '
                          f'"keywords": ["..."], "score": 0-100}}. Language: {s["language"]}.')
                try:
                    ans = ai.extract_json(ai.ask(s, prompt, timeout=300))
                    keep = bool(ans.get("keep", True))
                    hook, title = ans.get("hook") or hook, ans.get("title") or title
                    sp["keywords"], sp["score"] = ans.get("keywords", []), ans.get("score", 0)
                except Exception as e:
                    log(f"[{self.channel}] AI: {e}")
            if not keep:
                self.events.append({"t": int(time.time()), "what": "AI: odrzucone"})
                return
            pick = {"sid": sid, "url": meta["url"], "name": self.channel, "platform": "twitch", "start": 0.0,
                    "end": round(dur, 2), "peak": float(self.cfg["before"]), "hook": " ".join(hook.upper().split()[:6]),
                    "title": title[:70], "hashtags": ["#gta6", "#twitch", "#shorts", f"#{self.channel}"],
                    "keywords": sp.get("keywords", []), "score": sp.get("score", 0),
                    "why": f"skok czatu x{sp['ratio']}", "credit": f"Clip: {self.channel} — twitch.tv/{self.channel}"}
            sm = render_pick(ws, pick, len(self.events), f"live-{stamp}", extra={"source": "live"})
            self.events.append({"t": int(time.time()), "what": f"Short gotowy: {sm['id']}"})
        except Exception as e:
            self.events.append({"t": int(time.time()), "what": f"błąd: {e}"})
            log(f"[{self.channel}] błąd: {e}")


class HuntManager:
    def __init__(self, ws: Workspace):
        self.ws = ws
        self.hunts: dict[str, Hunt] = {}

    def start(self, channels: list[str]):
        for c in channels:
            if c.lower() not in self.hunts:
                self.hunts[c.lower()] = Hunt(self.ws, c).start()

    def stop(self, channels: list[str] | None = None):
        for c in list(channels or self.hunts):
            h = self.hunts.pop(c.lower(), None)
            if h:
                h.stop()

    def status(self) -> list[dict]:
        return [h.status() for h in self.hunts.values()]


def run_cli(ws: Workspace, channels: list[str], ratio: float | None = None, min_rate: float | None = None):
    if ratio or min_rate:
        ws.save_settings({"live": {k: v for k, v in (("ratio", ratio), ("min_per_min", min_rate)) if v}})
    mgr = HuntManager(ws)
    mgr.start(channels)
    log(f"Polowanie na żywo: {', '.join(channels)}. Ctrl+C kończy.")
    try:
        while True:
            time.sleep(30)
            for st in mgr.status():
                log(f"  {st['channel']}: czat {'ok' if st['chat'] else '—'}, nagrywanie {'ok' if st['recording'] else 'offline'}, "
                    f"{st['per_min']} wiad./min, baza {st['baseline']}")
    except KeyboardInterrupt:
        mgr.stop()
