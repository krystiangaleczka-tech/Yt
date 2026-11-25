"""Small helpers: running tools, ffprobe, time formatting, slugs."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path


class ToolError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list, cwd=None, check=True, capture=True, timeout=None, input_text=None) -> subprocess.CompletedProcess:
    cmd = [str(c) for c in cmd]
    try:
        p = subprocess.run(
            cmd, cwd=cwd, capture_output=capture, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, input=input_text,
        )
    except FileNotFoundError as e:
        raise ToolError(f"Brak programu: {cmd[0]} ({e})") from e
    if check and p.returncode != 0:
        tail = (p.stderr or p.stdout or "")[-1500:]
        raise ToolError(f"{Path(cmd[0]).name} zakończył się błędem {p.returncode}:\n{tail}")
    return p


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def ytdlp_cmd() -> list[str]:
    if have("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


def ffprobe(path) -> dict:
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    return json.loads(p.stdout)


def media_info(path) -> dict:
    info = ffprobe(path)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
    out = {"duration": float(info["format"].get("duration") or 0), "has_audio": a is not None, "has_video": v is not None}
    if v:
        out["width"], out["height"] = int(v["width"]), int(v["height"])
        num, _, den = (v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1").partition("/")
        try:
            out["fps"] = float(num) / float(den or 1) or 30.0
        except (ValueError, ZeroDivisionError):
            out["fps"] = 30.0
    return out


def hms(sec: float) -> str:
    sec = max(0, int(sec))
    h, m, s = sec // 3600, (sec // 60) % 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_time(v) -> float:
    """'1:02:03' / '62:03' / '3723' / 3723.5 -> seconds."""
    if isinstance(v, (int, float)):
        return float(v)
    v = str(v).strip()
    if re.fullmatch(r"[\d.]+", v):
        return float(v)
    parts = [float(p) for p in v.split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def slug(text: str, n: int = 40) -> str:
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_").lower()
    return (t[:n].rstrip("_")) or "short"


def hex_to_ass(color: str, alpha: int = 0) -> str:
    """#RRGGBB -> &HAABBGGRR (ASS colour)."""
    c = color.lstrip("#")
    if len(c) != 6:
        c = "FFFFFF"
    r, g, b = c[0:2], c[2:4], c[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ffmpeg_escape_path(p: str) -> str:
    """Escape a path for use inside an ffmpeg filter option value."""
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
