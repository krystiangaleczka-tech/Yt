"""Look before rendering: 4 frames per pick (low-res section download), saved as one strip per pick."""
from __future__ import annotations

from pathlib import Path

from .config import Workspace, read_json
from .sources import fetch_section
from .util import log, media_info, run


def peek(ws: Workspace, picks_file: Path | None = None) -> list[Path]:
    picks = read_json(picks_file or ws.path("picks.json"), [])
    ws.peek.mkdir(parents=True, exist_ok=True)
    out = []
    for i, p in enumerate(picks, 1):
        meta = read_json(ws.src / f"{p['sid']}.meta.json", {"url": p["url"]})
        clip = ws.peek / f"{i:02d}.mp4"
        try:
            fetch_section(meta, p["start"], p["end"], clip, max_height=360)
            d = media_info(clip)["duration"]
            strip = ws.peek / f"{i:02d}.jpg"
            n = 4
            run(["ffmpeg", "-y", "-v", "error", "-i", clip, "-vf",
                 f"fps={n / max(d, 1):.4f},scale=320:-2,tile={n}x1", "-frames:v", "1", strip])
            out.append(strip)
            log(f"  {i:02d} {p['hook']} → {strip}")
        except Exception as e:
            log(f"  {i:02d} błąd: {e}")
        finally:
            clip.unlink(missing_ok=True)
    return out
