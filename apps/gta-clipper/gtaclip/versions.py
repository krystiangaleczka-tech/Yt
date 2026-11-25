"""Library of Shorts and new versions: AI-requested changes, new look, voice line.

The original is never overwritten: each change renders v1, v2, ... next to v0.
"""
from __future__ import annotations

import re
import shutil
import time
from pathlib import Path

from . import ai
from . import qc as qcmod
from .config import Workspace, read_json, write_json
from .render import produce
from .transcribe import text_between
from .util import ToolError, hms, log, media_info, run


def load(ws: Workspace, short_id: str) -> dict:
    sm = read_json(ws.shorts / short_id / "meta.json", None)
    if not sm:
        raise ToolError(f"Nie ma Shorta {short_id}")
    return sm


def save(ws: Workspace, sm: dict) -> None:
    write_json(ws.shorts / sm["id"] / "meta.json", sm)


def library(ws: Workspace) -> list[dict]:
    out = []
    for mp in ws.shorts.glob("*/meta.json"):
        sm = read_json(mp, None)
        if sm:
            out.append(sm)
    out.sort(key=lambda x: (x.get("created", 0), x["id"]), reverse=True)
    return out


def set_status(ws: Workspace, short_id: str, status: str) -> dict:
    sm = load(ws, short_id)
    sm["status"] = status
    sm["status_at"] = int(time.time())
    save(ws, sm)
    return sm


def new_version(ws: Workspace, short_id: str, patch: dict, note: str) -> dict:
    """patch may change: start, end (absolute), hook, keywords, look{...}."""
    sm = load(ws, short_id)
    folder = ws.shorts / short_id
    spec = dict(sm["spec"])
    cur = sm["versions"][sm.get("current", 0)]
    base = sm.get("spec_versions", {}).get(str(cur["v"]), {})
    spec.update(base)
    look = {**(spec.get("look") or {}), **(patch.get("look") or {})}
    spec.update({k: v for k, v in patch.items() if k != "look"})
    spec["look"] = look
    info = media_info(folder / "src.mp4")
    lo, hi = spec["src_t0"], spec["src_t0"] + info["duration"]
    spec["start"], spec["end"] = max(lo, float(spec["start"])), min(hi, float(spec["end"]))
    v = max(x["v"] for x in sm["versions"]) + 1
    res = produce(ws, folder, spec, f"v{v}.mp4")
    res["qc"] = qcmod.check(folder / res["file"], {**res, "hook": spec.get("hook"), "score": sm["pick"].get("score", 0)})
    sm = load(ws, short_id)  # re-read (other jobs may have changed status)
    sm["versions"].append({"v": v, "note": note, "created": int(time.time()), **res})
    sm.setdefault("spec_versions", {})[str(v)] = {k: spec[k] for k in ("start", "end", "hook", "keywords", "look")}
    sm["current"] = len(sm["versions"]) - 1
    save(ws, sm)
    log(f"v{v} gotowa: {res['qc']['status']} {'; '.join(res['qc']['notes'])}")
    return sm


# ------------------------------------------------------------- change by words
CHANGE_PROMPT = """You edit a vertical GTA 6 Short. Current settings (times are absolute seconds in the source):
start={start} end={end} hook="{hook}" keywords={keywords} look={look}
Source footage available from {lo:.1f} to {hi:.1f}.
Transcript around the Short:
{transcript}

Caption styles: {styles}. Layouts: auto, stack, bubble, full, facecrop.
The user asks: "{request}"

Answer with JSON only, containing just the fields to change, e.g.
{{"end": 123.4}} or {{"hook": "NEW HOOK"}} or {{"look": {{"style": "beast", "flip": true}}}}
"""


def simple_parse(request: str, spec: dict) -> dict:
    """Understands simple requests without AI (Polish and English)."""
    r = request.lower()
    out: dict = {}
    num = re.search(r"(\d+(?:[.,]\d+)?)\s*(s|sek|sec|second)", r)
    n = float(num.group(1).replace(",", ".")) if num else None
    if n is not None:
        if re.search(r"(koń|zakoń|end|finish|stop)", r):
            sign = -1 if re.search(r"(wcze|earlier|sooner|szybciej)", r) else 1
            out["end"] = spec["end"] + sign * n
        elif re.search(r"(zacz|start|begin|początek)", r):
            sign = -1 if re.search(r"(wcze|earlier|sooner)", r) else 1
            out["start"] = spec["start"] + sign * n
    m = re.search(r"hook[:\s]+[\"„']?(.+?)[\"”']?$", request, re.I)
    if m:
        out["hook"] = m.group(1).strip().upper()
    from .captions import THEMES
    for name in THEMES:
        if re.search(rf"\b{name}\b", r):
            out.setdefault("look", {})["style"] = name
    if re.search(r"(odwr|flip|kamer\w* na d|cam below)", r):
        out.setdefault("look", {})["flip"] = True
    return out


def change_by_words(ws: Workspace, short_id: str, request: str) -> dict:
    s = ws.settings()
    sm = load(ws, short_id)
    spec = {**sm["spec"], **sm.get("spec_versions", {}).get(str(sm["versions"][sm.get("current", 0)]["v"]), {})}
    patch = simple_parse(request, spec)
    if not patch and ai.available(s):
        from .captions import THEMES
        tr = read_json(ws.src / f"{spec['sid']}.json", {"segments": []})
        dur = media_info(ws.shorts / short_id / "src.mp4")["duration"]
        prompt = CHANGE_PROMPT.format(start=spec["start"], end=spec["end"], hook=spec.get("hook"),
                                      keywords=spec.get("keywords"), look=spec.get("look"), lo=spec["src_t0"],
                                      hi=spec["src_t0"] + dur, request=request, styles=", ".join(THEMES),
                                      transcript=text_between(tr, spec["src_t0"], spec["src_t0"] + dur))
        patch = ai.extract_json(ai.ask(s, prompt, timeout=600))
    if not patch:
        raise ToolError("Nie rozumiem tej zmiany. Wybierz AI w Ustawieniach albo napisz np. „zakończ 2 s wcześniej”.")
    log(f"zmiana: {patch}")
    return new_version(ws, short_id, patch, request)


# ------------------------------------------------------------------- voice
def add_voice(ws: Workspace, short_id: str, voice_file: str, at: str | float = "payoff") -> dict:
    """Put the user's voice line on the Short; game audio ducks under it and comes back."""
    sm = load(ws, short_id)
    folder = ws.shorts / short_id
    cur = sm["versions"][sm.get("current", 0)]
    src = folder / cur["file"]
    dur = media_info(src)["duration"]
    vf = folder / f"voice_{int(time.time())}{Path(voice_file).suffix or '.wav'}"
    shutil.copy(voice_file, vf)
    vlen = media_info(vf)["duration"]
    if at == "payoff":
        spec = sm["spec"]
        peak = spec.get("peak") or (spec["start"] + (spec["end"] - spec["start"]) * 0.7)
        t = min(max(0.5, peak - spec["start"] + 1.0), max(0.5, dur - vlen - 0.3))
    elif at == "start":
        t = 0.3
    else:
        t = float(at)
    v = max(x["v"] for x in sm["versions"]) + 1
    out = f"v{v}.mp4"
    ms = int(t * 1000)
    graph = (f"[1:a]aresample=48000,loudnorm=I=-14:TP=-1.5,adelay={ms}:all=1,apad[vo];"
             f"[vo]asplit=2[vo1][vo2];"
             f"[0:a][vo1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[duck];"
             f"[duck][vo2]amix=inputs=2:normalize=0:duration=first[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", src.name, "-i", vf.name, "-filter_complex", graph, "-map", "0:v",
         "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], cwd=folder)
    cover = out.replace(".mp4", "_cover.jpg")
    shutil.copy(folder / cur["cover"], folder / cover)
    res = {**cur, "file": out, "cover": cover}
    res["qc"] = qcmod.check(folder / out, {**res, "hook": sm["pick"].get("hook")})
    sm["versions"].append({**res, "v": v, "note": f"głos lektora od {hms(t)}", "created": int(time.time())})
    sm["spec_versions"] = {**sm.get("spec_versions", {}), str(v): sm.get("spec_versions", {}).get(str(cur["v"]), {})}
    sm["current"] = len(sm["versions"]) - 1
    save(ws, sm)
    log(f"v{v}: głos dodany od {t:.1f} s")
    return sm


def newest_recording() -> str | None:
    """Newest file in Documents/Sound recordings (Windows Sound Recorder) or similar."""
    home = Path.home()
    dirs = [home / "Documents" / "Sound recordings", home / "Documents" / "Nagrania dźwiękowe",
            home / "Music" / "Recordings", home / "Documents"]
    files = []
    for d in dirs:
        if d.exists():
            files += [p for p in d.glob("*") if p.suffix.lower() in (".m4a", ".wav", ".mp3", ".ogg", ".webm")]
    return str(max(files, key=lambda p: p.stat().st_mtime)) if files else None
