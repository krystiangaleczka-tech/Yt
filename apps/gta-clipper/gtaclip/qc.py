"""Self-check of every Short: PASS / WARN / FAIL with reasons (in Polish, shown in the app)."""
from __future__ import annotations

import re
from pathlib import Path

from .util import media_info, run


def _detect(video: Path, vf: str, key: str) -> float:
    p = run(["ffmpeg", "-hide_banner", "-v", "info", "-i", video, "-vf", vf, "-an", "-f", "null", "-"], check=False)
    total = 0.0
    for m in re.finditer(key + r"_duration:\s*([\d.]+)", p.stderr):
        total += float(m.group(1))
    return total


def mean_volume(video: Path) -> float | None:
    p = run(["ffmpeg", "-hide_banner", "-i", video, "-vn", "-af", "volumedetect", "-f", "null", "-"], check=False)
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", p.stderr)
    return float(m.group(1)) if m else None


def check(video: Path, info: dict, ws=None) -> dict:
    fails, warns = [], []
    video = Path(video)
    if not video.exists() or video.stat().st_size < 50_000:
        return {"status": "FAIL", "notes": ["brak pliku albo pusty plik"]}
    mi = media_info(video)
    d = mi["duration"]
    if (mi.get("width"), mi.get("height")) != (1080, 1920):
        fails.append(f"zły format {mi.get('width')}x{mi.get('height')}")
    if d < 8:
        fails.append(f"za krótki ({d:.0f} s)")
    elif d < 13:
        warns.append(f"krótki ({d:.0f} s)")
    if d > 60.5:
        fails.append(f"za długi na Shorts ({d:.0f} s)")
    vol = mean_volume(video) if mi["has_audio"] else None
    if vol is None or vol < -45:
        if info.get("muted"):  # silenced on purpose in a change: waits for the creator's voice line
            warns.append("dźwięk wyciszony celowo — dograj głos przyciskiem „Twój głos”")
        else:
            fails.append("brak dźwięku")
    elif vol < -30:
        warns.append(f"cichy dźwięk ({vol:.0f} dB)")
    black = _detect(video, "blackdetect=d=0.5:pix_th=0.08", "black")
    if black > d * 0.3:
        fails.append(f"czarny obraz przez {black:.0f} s")
    elif black > 1.0:
        warns.append(f"czarne klatki {black:.1f} s")
    frozen = _detect(video, "freezedetect=n=0.002:d=2", "freeze")
    if frozen > d * 0.5:
        fails.append(f"zamrożony obraz {frozen:.0f} s")
    elif frozen > 3:
        warns.append(f"stoi obraz {frozen:.0f} s")
    music = None
    if ws is not None and mi["has_audio"]:
        from .music import music_report
        music = music_report(ws, video)
        if music and music["warn"]:
            warns.append(f"w tle gra muzyka (ok. {music['seconds']:.0f} s) — ryzyko blokady Content ID od wytwórni; "
                         "odpuść ten klip albo wytnij/wycisz ten fragment")
    if info.get("words", 1) == 0:
        warns.append("brak napisów (nikt nie mówi?)")
    if info.get("layout") == "full":
        warns.append("nie znalazłem kamerki streamera — cały kadr na rozmyciu")
    if len((info.get("hook") or "").split()) > 6:
        warns.append("hook dłuższy niż 6 słów")
    if 0 < info.get("score", 100) < 50:
        warns.append(f"słaba ocena AI ({info['score']})")
    status = "FAIL" if fails else "WARN" if warns else "PASS"
    return {"status": status, "notes": fails + warns, "duration": round(d, 1), "volume": vol, "music": music}


def check_folder(ws, short_id: str | None = None) -> list[dict]:
    from .config import read_json, write_json

    out = []
    for mp in sorted(ws.shorts.glob("*/meta.json")):
        sm = read_json(mp, {})
        if short_id and sm.get("id") != short_id:
            continue
        v = sm["versions"][sm.get("current", 0)]
        v["qc"] = check(mp.parent / v["file"], {**v, "hook": sm["pick"].get("hook"), "score": sm["pick"].get("score", 0)}, ws)
        write_json(mp, sm)
        out.append({"id": sm["id"], **v["qc"]})
    return out
