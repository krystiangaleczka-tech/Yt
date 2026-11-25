"""Pick the moments that become Shorts.

Modes
  free   no AI: best HEAT windows, hook built from the moment label
  smart  AI reads only the best ~30 candidate windows (default, cheap)
  deep   AI reads whole transcripts (expensive, finds quiet-but-good moments)
  agent  write AGENT_TASK.md and stop — the AI running the skill (e.g. Claude Code)
         reads it and writes picks.json itself
"""
from __future__ import annotations

import re
import sys

from . import ai
from .config import APP_DIR, Workspace, read_json, write_json
from .signals import candidates as build_candidates
from .sources import load_sources
from .transcribe import text_between
from .util import hms, log

RULES = """You pick moments from GTA 6 streams/videos that become vertical Shorts (15-59 s).

Rules:
- A pick needs a PEAK and a PREMISE: something the viewer can name must be shown or said before the peak.
  Shouting with no premise scores 0.
- Score 0-100 = how likely a stranger scrolling at 1 a.m. keeps watching. Best 80-95, weak under 50.
- Stranger test (answer yes/no): 1) do I get what is happening in 3 s? 2) is there a question I want answered?
  3) does the end pay it off? Under 2 of 3 yes -> replace it.
- At most {max_per_source} Shorts per source video. Setup longer than ~8 s -> start later.
- The payoff happens in the last 40% and the Short ENDS on it. Never end on a logo, end card, sponsor or credits.
- Hook: max 6 words, ALL CAPS, streamer name first (e.g. "SPEED FOUND KFC IN GTA 6").
- Title: up to 70 characters. 3-5 hashtags. 1-3 keywords (single words from the speech, shown in green).
- Language of hook/title/hashtags: {language}.
- Only use start/end times inside the given text (seconds, absolute in the source).
"""

ANSWER = """Answer with JSON only: a list of up to {count} objects, best first:
[{{"cid": <candidate number or null>, "sid": "<source id>", "start": <sec>, "end": <sec>, "hook": "...",
  "title": "...", "hashtags": ["#gta6", "..."], "keywords": ["..."], "score": 0-100, "why": "short reason"}}]
"""

LABEL_HOOK = {
    "chase": "GETS CHASED BY COPS", "crash": "CRASHES HARD", "fight": "STARTS A FIGHT",
    "stunt": "PULLS OFF A STUNT", "reaction": "CAN'T BELIEVE THIS", "funny": "LOSES IT",
}


def short_name(name: str) -> str:
    n = re.sub(r"(?i)\b(live|tv|official|yt|ttv)\b", "", name or "").strip()
    return (n.split()[0] if n else "THIS").upper()


def _hashtags(lang: str) -> list[str]:
    return ["#gta6", "#gtavi", "#gaming", "#shorts"]


def _free_pick(c: dict, lang: str) -> dict:
    lab = (c.get("labels") or ["reaction"])[0]
    hook = f"{short_name(c['name'])} {LABEL_HOOK.get(lab, 'IN GTA 6')}"
    words = re.findall(r"[A-Za-z']{5,}", c.get("transcript", ""))
    kw = sorted(set(w.lower() for w in words), key=lambda w: -c["transcript"].lower().count(w))[:2]
    return {"cid": c["cid"], "sid": c["sid"], "start": c["start"], "end": c["end"], "hook": " ".join(hook.split()[:6]),
            "title": f"{c['name']} {LABEL_HOOK.get(lab, 'in GTA 6').lower()} in GTA 6"[:70],
            "hashtags": _hashtags(lang), "keywords": kw, "score": int(min(95, 40 + c["heat"] * 0.5)),
            "why": " ".join(c["tags"])}


def build_prompt(ws: Workspace, cands: list[dict], count: int, deep: bool = False,
                 sources: list | None = None) -> str:
    s = ws.settings()
    head = RULES.format(max_per_source=s["max_per_source"], language=s["language"])
    if deep and sources:
        body = ["# Full transcripts"]
        for meta, tr in sources:
            body.append(f"## source {meta['sid']} — {meta.get('name')} — {meta.get('title', '')[:80]}")
            body.append(text_between(tr, 0, 10 ** 9)[:60000])
        body.append("\n# Signal hints (best windows found without AI)")
        body.append(ws.path("candidates.md").read_text(encoding="utf-8")[:20000])
        data = "\n".join(body)
    else:
        data = ws.path("candidates.md").read_text(encoding="utf-8")
    return f"{head}\n{ANSWER.format(count=count)}\n\n{data}"


def normalize(ws: Workspace, raw: list[dict], cands: list[dict], count: int) -> list[dict]:
    s = ws.settings()
    by_cid = {c["cid"]: c for c in cands}
    metas = {m.name[:-10]: read_json(m, {}) for m in ws.src.glob("*.meta.json")}
    out, per = [], {}
    for r in raw:
        c = by_cid.get(r.get("cid")) if r.get("cid") is not None else None
        sid = r.get("sid") or (c or {}).get("sid")
        meta = metas.get(sid)
        if not meta:
            continue
        try:
            st, en = float(r.get("start", c["start"] if c else 0)), float(r.get("end", c["end"] if c else 0))
        except (TypeError, ValueError):
            continue
        if en - st < s["min_len"] - 3 or en - st > s["max_len"] + 1:
            en = min(max(en, st + s["min_len"]), st + s["max_len"])
        if per.get(sid, 0) >= s["max_per_source"]:
            continue
        if any(p["sid"] == sid and not (en <= p["start"] or st >= p["end"]) for p in out):
            continue
        per[sid] = per.get(sid, 0) + 1
        hook = " ".join(str(r.get("hook", "")).upper().split()[:6])
        out.append({
            "sid": sid, "url": meta.get("url"), "name": meta.get("name"), "source_title": meta.get("title"),
            "platform": meta.get("platform"), "start": round(st, 2), "end": round(en, 2),
            "peak": (c or {}).get("peak", round(st + (en - st) * 0.7, 1)),
            "hook": hook or f"{short_name(meta.get('name'))} IN GTA 6",
            "title": str(r.get("title") or hook.title())[:70],
            "hashtags": r.get("hashtags") or _hashtags(s["language"]),
            "keywords": [k.lower() for k in (r.get("keywords") or [])][:3],
            "score": int(r.get("score") or 0), "why": r.get("why", ""),
            "tags": (c or {}).get("tags", []),
            "credit": f"Clip: {meta.get('name')} — {meta.get('url')}",
            "transcript": (c or {}).get("transcript", ""),
        })
        if len(out) >= count:
            break
    return out


def pick(ws: Workspace, mode: str | None = None, count: int | None = None, ids: list[str] | None = None) -> list[dict]:
    s = ws.settings()
    mode = mode or s["pick_mode"]
    count = count or s["shorts_per_run"]
    sources = load_sources(ws, ids)
    if not sources:
        log("Brak nowych źródeł z transkrypcją. Najpierw: find")
        return []
    cands = build_candidates(ws, sources, s["candidates"])
    if not cands:
        log("Nie znalazłem żadnego gorącego momentu.")
        return []
    if mode == "agent":
        prompt = build_prompt(ws, cands, count)
        ws.path("AGENT_TASK.md").write_text(
            prompt + f"\n\nWrite the JSON list to {ws.path('picks_raw.json')} and run:\n"
            f'"{sys.executable}" "{APP_DIR / "clipper.py"}" --workspace "{ws.root}" pick --from-raw\n', encoding="utf-8")
        log(f"Zadanie dla AI → {ws.path('AGENT_TASK.md')}")
        return []
    raw = None
    if mode in ("smart", "deep") and ai.available(s):
        log(f"AI ({s['ai']}) czyta {'całe transkrypcje' if mode == 'deep' else f'{len(cands)} kandydatów'}…")
        try:
            raw = ai.extract_json(ai.ask(s, build_prompt(ws, cands, count, mode == "deep", sources)))
            if isinstance(raw, dict):
                raw = raw.get("picks", [])
        except Exception as e:  # fall back to free picks
            log(f"AI nie odpowiedziało poprawnie ({e}) — wybieram bez AI")
            raw = None
    elif mode in ("smart", "deep"):
        log(f"AI '{s['ai']}' niedostępne na tym PC — wybieram bez AI (tryb free)")
    if raw is None:
        raw = [_free_pick(c, s["language"]) for c in cands]
    picks = normalize(ws, raw, cands, count)
    for meta, _ in sources:
        m = read_json(ws.src / f"{meta['sid']}.meta.json", {})
        m["used"] = True
        write_json(ws.src / f"{meta['sid']}.meta.json", m)
    write_json(ws.path("picks.json"), picks)
    print_table(picks)
    return picks


def from_raw(ws: Workspace) -> list[dict]:
    s = ws.settings()
    raw = read_json(ws.path("picks_raw.json"), [])
    cands = read_json(ws.path("candidates.json"), [])
    picks = normalize(ws, raw, cands, s["shorts_per_run"])
    write_json(ws.path("picks.json"), picks)
    print_table(picks)
    return picks


def print_table(picks: list[dict]) -> None:
    log(f"\nOto {len(picks)} wybranych momentów:\n")
    log(f"{'#':>2}  {'moment':<22} {'hook':<34} dlaczego")
    for i, p in enumerate(picks, 1):
        mom = f"{(p.get('name') or '')[:12]} {hms(p['start'])}"
        log(f"{i:>2}  {mom:<22} {p['hook'][:34]:<34} {p.get('score', 0):>3} · {(p.get('why') or ' '.join(p.get('tags', [])))[:60]}")
