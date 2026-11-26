"""Library of Shorts and new versions: AI-requested changes, new look, voice line.

The original is never overwritten: each change renders v1, v2, ... next to v0.
"""
from __future__ import annotations

import contextlib
import fcntl
import re
import shutil
import time
from pathlib import Path

from . import ai
from . import qc as qcmod
from .config import Workspace, read_json, write_json
from .render import out_to_src, plan_pieces, produce, spec_segments, src_to_out, timeline
from .transcribe import words_between
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


EDIT_KEYS = ("start", "end", "hook", "keywords", "look", "segments", "zoom_at", "mute", "mute_all", "noise", "texts")
LOOK_KEYS = ("style", "layout", "flip", "accent", "keyword_color", "punch_zooms", "cut_dead_air", "sfx", "watermark",
             "cap_pos", "hook_secs", "censor_on_screen")


@contextlib.contextmanager
def short_lock(folder: Path):
    """One change at a time per Short: two requests sent quickly used to write the same v1.mp4 together."""
    with open(folder / ".lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def current_spec(sm: dict) -> dict:
    cur = sm["versions"][sm.get("current", 0)]
    return {**sm["spec"], **sm.get("spec_versions", {}).get(str(cur["v"]), {})}


def new_version(ws: Workspace, short_id: str, patch: dict, note: str) -> dict:
    """patch (absolute source seconds) may change: start, end, hook, keywords, look{...}, segments, zoom_at, mute,
    mute_all, noise, texts."""
    if not isinstance(patch, dict):
        raise ToolError("Zmiana ma zły format — spróbuj napisać ją inaczej.")
    folder = ws.shorts / short_id
    with short_lock(folder):
        sm = load(ws, short_id)
        spec = current_spec(sm)
        if spec.get("segments") and "segments" not in patch and ("start" in patch or "end" in patch):
            segs = [dict(x) for x in spec["segments"]]  # "end 2 s earlier" on a re-cut Short moves its last piece
            if "start" in patch:
                segs[0]["a"] = float(patch["start"])
            if "end" in patch:
                segs[-1]["b"] = float(patch["end"])
            patch = {**patch, "segments": segs}
        look = {**(spec.get("look") or {}), **(patch.get("look") or {})}
        spec.update({k: v for k, v in patch.items() if k != "look"})
        spec["look"] = look
        info = media_info(folder / "src.mp4")
        lo, hi = spec["src_t0"], spec["src_t0"] + info["duration"]
        spec["start"], spec["end"] = max(lo, float(spec["start"])), min(hi, float(spec["end"]))
        v = max(x["v"] for x in sm["versions"]) + 1
        res = produce(ws, folder, spec, f"v{v}.mp4")
        res["qc"] = qcmod.check(folder / res["file"], {**res, "hook": spec.get("hook"), "score": sm["pick"].get("score", 0)}, ws)
        sm = load(ws, short_id)  # re-read (status may have changed meanwhile)
        sm["versions"].append({"v": v, "note": note, "created": int(time.time()), **res})
        sm.setdefault("spec_versions", {})[str(v)] = {k: spec[k] for k in EDIT_KEYS if k in spec}
        sm["current"] = len(sm["versions"]) - 1
        save(ws, sm)
    log(f"v{v} gotowa: {res['qc']['status']} {'; '.join(res['qc']['notes'])}")
    return sm


# ------------------------------------------------------------- change by words
def current_timeline(ws: Workspace, sm: dict) -> list[list[float]]:
    """Where each piece of source footage sits in the current version (older versions: recomputed)."""
    cur = sm["versions"][sm.get("current", 0)]
    if cur.get("timeline"):
        return cur["timeline"]
    spec = current_spec(sm)
    src = ws.shorts / sm["id"] / "src.mp4"
    info = media_info(src)
    cut = {"cut_dead_air": ws.settings()["cut_dead_air"], **(spec.get("look") or {})}["cut_dead_air"]
    return timeline(plan_pieces(src, spec, info["duration"], cut, info["has_audio"]))


def short_transcript(tr: dict, tl: list[list[float]]) -> str:
    """Transcript as the viewer hears it, stamped with seconds of the Short."""
    lines = []
    for o0, _o1, a, b, sp in tl:
        words = [w for w in words_between(tr, a, b) if w["s"] >= a]
        cur, t_cur = [], None
        for w in words:
            t = o0 + (w["s"] - a) / sp
            if t_cur is None:
                t_cur = t
            cur.append(w["w"])
            if len(cur) >= 10 or w["w"].endswith((".", "!", "?")):
                lines.append(f"[{t_cur:5.1f}s] {' '.join(cur)}")
                cur, t_cur = [], None
        if cur:
            lines.append(f"[{t_cur:5.1f}s] {' '.join(cur)}")
    return "\n".join(lines) or "(no speech)"


def out_range_to_src(tl: list[list[float]], f: float, t: float) -> list[tuple[float, float, float]]:
    """Seconds f..t of the Short -> source pieces [(a, b, speed)] (a range may cross several cuts)."""
    out = []
    for o0, o1, a, _b, sp in tl:
        x0, x1 = max(f, o0), min(t, o1)
        if x1 - x0 > 0.05:
            out.append((round(a + (x0 - o0) * sp, 3), round(a + (x1 - o0) * sp, 3), sp))
    return out


CHANGE_PROMPT = """You edit a vertical GTA 6 Short (1080x1920) on the creator's request.
The Short now lasts {length:.1f} s. ALL times you read and write are seconds of the Short as the viewer sees it (0 = first frame).
Extra footage exists outside the Short: {before:.1f} s before its start and {after:.1f} s after its end.

What is said (seconds of the Short):
{transcript}

Edits already on it: {edits}
Settings: hook="{hook}" look={look}
Caption styles: {styles}. Layouts: auto, stack (streamer cam on top, game below), bubble, full (whole frame on blur), facecrop.

The creator asks (usually Polish): "{request}"

You cannot see the picture, only the words and times. Map words like "zbliżenie na auto / na nią / na telefon" to a zoom
at that time; guess x/y (0..1 of the frame, 0.5/0.5 = centre) only when the request says where (top-left etc.).

Answer with ONE JSON object only, with just the fields you need:
{{
  "segments": [[from, to, speed], ...],   // the Short rebuilt from its own seconds, in play order: leave out parts to cut,
                                         // repeat or reorder parts, speed 1 = normal, 2 = twice as fast, 0.5 = slow motion.
                                         // Omit when the order/length does not change.
  "extend": {{"before": s, "after": s}},   // pull extra footage in at the start / end (up to the amounts above)
  "zooms": [{{"at": s, "dur": s, "scale": 1.1-2.0, "x": 0-1, "y": 0-1}}],   // added zooms
  "auto_zooms": true/false,              // automatic punch zooms on the loudest reactions
  "mute": [[from, to]], "mute_all": true/false,   // silence parts / all of the original sound
  "noise": 0-1,                          // pink noise over the muted parts (0 = none)
  "texts": [{{"text": "...", "at": s, "dur": s, "color": "#RRGGBB", "size": 60-200, "pos": "top|middle|bottom"}}],
  "hook": "NEW HOOK", "keywords": ["..."],
  "look": {{"style": "...", "layout": "...", "flip": bool, "accent": "#RRGGBB", "cap_pos": "top|middle|bottom",
           "hook_secs": s, "cut_dead_air": bool, "sfx": bool}},
  "clear": ["zooms" | "mute" | "texts" | "segments"],   // drop edits made earlier
  "unsupported": "short Polish note on any part you cannot do"
}}
Examples: "od 12s do 15s przyspiesz" -> {{"segments": [[0,12,1],[12,15,2],[15,{length:.1f},1]]}};
"w 14s obetnij do 21s" -> {{"segments": [[0,14,1],[21,{length:.1f},1]]}};
"napisy u góry" -> {{"look": {{"cap_pos": "top"}}}};
"w 1s duży niebieski napis X" -> {{"texts": [{{"text": "X", "at": 1, "dur": 2.5, "color": "#1E90FF", "size": 140, "pos": "top"}}]}};
"wycisz muzykę od 3 do 9 s" -> {{"mute": [[3, 9]]}}.
A voice-over is recorded with the "Twój głos" button, not here: say so in "unsupported".
"""


def to_spec_patch(edit: dict, spec: dict, tl: list[list[float]], src_dur: float) -> tuple[dict, str]:
    """AI answer in seconds of the Short -> patch in absolute source seconds (what produce() reads)."""
    if not isinstance(edit, dict):
        raise ToolError("AI odpowiedziało w złym formacie (nie obiekt JSON).")
    length = tl[-1][1] if tl else spec["end"] - spec["start"]
    lo, hi = spec["src_t0"], spec["src_t0"] + src_dur
    patch: dict = {}
    clear = set(edit.get("clear") or [])
    for k in ("hook", "keywords"):
        if edit.get(k):
            patch[k] = edit[k]
    look = {k: v for k, v in (edit.get("look") or {}).items() if k in LOOK_KEYS}
    if "auto_zooms" in edit:
        look["punch_zooms"] = bool(edit["auto_zooms"])
    if look:
        patch["look"] = look

    segs = None
    if edit.get("segments"):
        segs = []
        for item in edit["segments"]:
            f, t = float(item[0]), float(item[1])
            sp = float(item[2]) if len(item) > 2 and item[2] else 1.0
            segs += [{"a": a, "b": b, "speed": round(min(4.0, max(0.25, psp * sp)), 3)}
                     for a, b, psp in out_range_to_src(tl, max(0.0, f), min(length, t))]
    elif "segments" in clear:
        segs = [{"a": spec["start"], "b": spec["end"], "speed": 1.0}]
    ext = edit.get("extend") or {}
    if ext.get("before") or ext.get("after"):
        if segs is None:
            segs = [{"a": a, "b": b, "speed": sp} for a, b, sp in spec_segments(spec, src_dur)]
        if segs:
            segs[0]["a"] = max(lo, segs[0]["a"] - float(ext.get("before") or 0))
            segs[-1]["b"] = min(hi, segs[-1]["b"] + float(ext.get("after") or 0))
    if segs is not None:
        if not segs:
            raise ToolError("Po tej zmianie nic by nie zostało z filmu.")
        patch["segments"] = segs
        patch["start"] = min(x["a"] for x in segs)
        patch["end"] = max(x["b"] for x in segs)

    def keep(key: str) -> list:
        return [] if key in clear else list(spec.get(key) or [])

    if edit.get("zooms") or "zooms" in clear:
        patch["zoom_at"] = [] if "zooms" in clear else list(spec.get("zoom_at") or [])
        for z in edit.get("zooms") or []:
            patch["zoom_at"].append({"t": out_to_src(tl, float(z["at"])), "dur": float(z.get("dur") or 1.5),
                                     "z": float(z.get("scale") or 1.35), "x": float(z.get("x", 0.5)), "y": float(z.get("y", 0.5))})
    if edit.get("mute") or "mute" in clear:
        patch["mute"] = keep("mute")
        for f, t in edit.get("mute") or []:
            patch["mute"] += [[a, b] for a, b, _ in out_range_to_src(tl, float(f), float(t))]
    if "mute_all" in edit:
        patch["mute_all"] = bool(edit["mute_all"])
    if edit.get("noise") is not None:
        patch["noise"] = min(1.0, max(0.0, float(edit["noise"])))
    if edit.get("texts") or "texts" in clear:
        patch["texts"] = keep("texts")
        for t in edit.get("texts") or []:
            patch["texts"].append({"text": str(t.get("text", "")), "t": out_to_src(tl, float(t.get("at") or 0)),
                                   "dur": float(t.get("dur") or 2.5), "color": t.get("color") or "#FFFFFF",
                                   "size": t.get("size") or 120, "pos": t.get("pos") or "top"})
    return patch, str(edit.get("unsupported") or "").strip()


def describe_edits(spec: dict, tl: list[list[float]]) -> str:
    parts = []
    for z in spec.get("zoom_at") or []:
        o = src_to_out(tl, z["t"])
        if o is not None:
            parts.append(f"zoom at {o:.1f}s")
    for a, b in spec.get("mute") or []:
        x, y = src_to_out(tl, a), src_to_out(tl, b)
        if x is not None and y is not None:
            parts.append(f"muted {x:.1f}-{y:.1f}s")
    if spec.get("mute_all"):
        parts.append("all original sound muted")
    for t in spec.get("texts") or []:
        o = src_to_out(tl, t["t"])
        if o is not None:
            parts.append(f'text "{t["text"]}" at {o:.1f}s')
    if any(abs(p[4] - 1) > 1e-3 for p in tl):
        parts += [f"{p[0]:.1f}-{p[1]:.1f}s at speed {p[4]:g}" for p in tl if abs(p[4] - 1) > 1e-3]
    return "; ".join(parts) or "none"


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
    spec = current_spec(sm)
    patch, unsupported = None, ""
    if ai.available(s):  # AI first: the simple parser below only knows "end/start N s earlier", hook and style
        from .captions import THEMES
        tl = current_timeline(ws, sm)
        src_dur = media_info(ws.shorts / short_id / "src.mp4")["duration"]
        segs = spec_segments(spec, src_dur)
        lo, hi = spec["src_t0"], spec["src_t0"] + src_dur
        tr = read_json(ws.src / f"{spec['sid']}.json", {"segments": []})
        prompt = CHANGE_PROMPT.format(length=tl[-1][1] if tl else 0, before=max(0.0, segs[0][0] - lo) if segs else 0,
                                      after=max(0.0, hi - segs[-1][1]) if segs else 0, transcript=short_transcript(tr, tl),
                                      edits=describe_edits(spec, tl), hook=spec.get("hook"), look=spec.get("look"),
                                      styles=", ".join(THEMES), request=request)
        try:
            edit = ai.extract_json(ai.ask(s, prompt, timeout=600))
            patch, unsupported = to_spec_patch(edit, spec, tl, src_dur)
        except (ToolError, ValueError, TypeError, KeyError, IndexError) as e:
            log(f"AI nie dało rady tej zmiany ({e}) — próbuję prostych reguł")
            patch = None
    if patch is None:
        patch = simple_parse(request, spec)
    if unsupported:
        log(f"Tego nie umiem zrobić: {unsupported}")
    if not patch:
        raise ToolError(f"Tego nie umiem zrobić: {unsupported}" if unsupported else
                        "Nie rozumiem tej zmiany. Napisz np. „od 12 s do 15 s przyspiesz”, „w 10 s zbliżenie”, "
                        "„wytnij od 14 s do 21 s”, „napisy u góry”, „wycisz od 3 do 9 s”.")
    log(f"zmiana: {patch}")
    return new_version(ws, short_id, patch, request + (f" (bez: {unsupported})" if unsupported else ""))


# ------------------------------------------------------------------- voice
def add_voice(ws: Workspace, short_id: str, voice_file: str, at: str | float = "payoff") -> dict:
    """Put the user's voice line on the Short; game audio ducks under it and comes back."""
    folder = ws.shorts / short_id
    with short_lock(folder):
        return _add_voice(ws, short_id, voice_file, at)


def _add_voice(ws: Workspace, short_id: str, voice_file: str, at: str | float) -> dict:
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
    res["qc"] = qcmod.check(folder / out, {**res, "hook": sm["pick"].get("hook")}, ws)
    sm["versions"].append({**res, "v": v, "note": f"głos lektora od {hms(t)}", "created": int(time.time())})
    sm["spec_versions"] = {**sm.get("spec_versions", {}), str(v): sm.get("spec_versions", {}).get(str(cur["v"]), {})}
    sm["current"] = len(sm["versions"]) - 1
    save(ws, sm)
    log(f"v{v}: głos dodany od {t:.1f} s")
    return sm


def newest_recording() -> str | None:
    """Newest voice recording: macOS Voice Memos (Dyktafon), AirDrop from iPhone (Downloads), QuickTime, Desktop."""
    home = Path.home()
    dirs = [home / "Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings",  # macOS 14+
            home / "Library/Application Support/com.apple.voicememos/Recordings",            # older macOS
            home / "Downloads", home / "Desktop", home / "Movies", home / "Music", home / "Documents"]
    exts = (".m4a", ".qta", ".wav", ".mp3", ".aiff", ".caf", ".ogg", ".webm")  # .qta = newer Voice Memos
    files = []
    for d in dirs:
        try:
            files += [p for p in d.glob("*") if p.suffix.lower() in exts]
        except PermissionError:
            if "VoiceMemos" in str(d) or "voicememos" in str(d):
                log("macOS nie dał dostępu do Dyktafonu. Kliknij „Pozwól”, gdy zapyta, albo: Ustawienia systemowe → "
                    "Prywatność i ochrona → Pełny dostęp do dysku → włącz Terminal.")
        except OSError:
            continue
    return str(max(files, key=lambda p: p.stat().st_mtime)) if files else None
