"""Find new GTA 6 videos/streams and fetch what the picker needs (audio, metadata, chat).

Only audio is downloaded at this stage. Video is fetched later, and only for the
seconds that become Shorts.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import Workspace, read_json, write_json
from .transcribe import detect_language, transcribe
from .util import ToolError, hms, log, media_info, run, ytdlp_cmd

PLATFORM_URLS = {
    "youtube": ["https://www.youtube.com/@{name}/streams", "https://www.youtube.com/@{name}/videos"],
    "twitch": ["https://www.twitch.tv/{name}/videos?filter=archives&sort=time"],
    "kick": ["https://kick.com/{name}/videos"],
}


def platform_of(url: str) -> str:
    u = url.lower()
    if "twitch.tv" in u:
        return "twitch"
    if "kick.com" in u:
        return "kick"
    if "youtu" in u:
        return "youtube"
    return "file" if Path(url).exists() else "other"


def source_id(url_or_path: str, info: dict | None = None) -> str:
    if info and info.get("id"):
        pre = {"twitch": "tw_", "kick": "kk_"}.get(platform_of(url_or_path), "")
        return re.sub(r"[^A-Za-z0-9_-]", "_", pre + str(info["id"]))
    return "file_" + hashlib.sha1(str(Path(url_or_path).resolve()).encode()).hexdigest()[:10]


def streamer_from_input(text: str) -> dict:
    """'https://twitch.tv/xqc' / 'youtube.com/@IShowSpeed' / 'kick.com/x' / 'xqc' -> streamer dict."""
    t = text.strip()
    plat = platform_of(t) if "/" in t or "." in t else "twitch"
    name = t.rstrip("/").split("/")[-1].lstrip("@") if "/" in t else t.lstrip("@")
    return {"name": name, "platform": plat if plat in PLATFORM_URLS else "youtube", "enabled": True,
            "live_watch": False, "rules": "unknown", "note": ""}


# ----------------------------------------------------------------- listing
def _flat(url: str, limit: int) -> list[dict]:
    try:
        p = run(ytdlp_cmd() + ["--flat-playlist", "-J", "--playlist-end", str(limit), "--no-warnings", url],
                timeout=180)
    except ToolError as e:
        log(f"  pomijam {url}: {str(e).splitlines()[-1][:160]}")
        return []
    try:
        d = json.loads(p.stdout)
    except json.JSONDecodeError:
        return []
    return [e for e in d.get("entries") or [] if e]


def list_candidates(ws: Workspace, query: str | None, limit: int = 20) -> list[dict]:
    s = ws.settings()
    found = []
    q = query or s["query"]
    if q:
        for e in _flat(f"ytsearch{limit}:{q}", limit):
            e["_from"] = "search"
            found.append(e)
    for line in (ws.root / "channels.txt").read_text(encoding="utf-8").splitlines() if (ws.root / "channels.txt").exists() else []:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("search:"):
            for e in _flat(f"ytsearch{limit}:{line[7:].strip()}", limit):
                e["_from"] = "search"
                found.append(e)
        else:
            for e in _flat(line, 5):
                e["_from"] = "channel"
                found.append(e)
    for st in ws.streamers():
        if not st.get("enabled", True) or st.get("rules") == "no":
            continue
        for tpl in PLATFORM_URLS.get(st["platform"], []):
            for e in _flat(tpl.format(name=st["name"]), 5):
                e["_from"] = "streamer"
                e["_streamer"] = st["name"]
                found.append(e)
    seen, out = set(), []
    for e in found:
        url = e.get("url") or e.get("webpage_url")
        if not url and e.get("id"):
            url = f"https://www.youtube.com/watch?v={e['id']}"
        if not url or url in seen:
            continue
        seen.add(url)
        e["url"] = url
        out.append(e)
    return out


def past_streams(st: dict, n: int = 5) -> list[dict]:
    out = []
    for tpl in PLATFORM_URLS.get(st["platform"], [])[:1]:
        for e in _flat(tpl.format(name=st["name"]), n):
            out.append({"title": e.get("title"), "url": e.get("url") or e.get("webpage_url"),
                        "duration": e.get("duration"), "id": e.get("id")})
    return out


# --------------------------------------------------------------- metadata
def fetch_info(url: str) -> dict:
    p = run(ytdlp_cmd() + ["-J", "--no-warnings", "--no-playlist", url], timeout=240)
    return json.loads(p.stdout)


def _age_hours(info: dict) -> float | None:
    ts = info.get("release_timestamp") or info.get("timestamp")
    if ts:
        return (time.time() - ts) / 3600
    d = info.get("upload_date")
    if d:
        dt = datetime.strptime(d, "%Y%m%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    return None


def slim_meta(info: dict, url: str) -> dict:
    keep = ("id", "title", "channel", "uploader", "uploader_id", "channel_url", "duration", "view_count",
            "upload_date", "timestamp", "release_timestamp", "live_status", "was_live", "language",
            "webpage_url", "extractor_key", "heatmap", "chapters")
    m = {k: info.get(k) for k in keep if info.get(k) is not None}
    m["url"] = info.get("webpage_url") or url
    m["platform"] = platform_of(m["url"])
    m["name"] = info.get("channel") or info.get("uploader") or "Streamer"
    return m


# --------------------------------------------------------------- fetching
def _live_args(url: str, live: bool) -> list[str]:
    """A YouTube stream that is still live has to be read from its start (DVR); a Twitch VOD of a live
    stream is a normal growing video, so it needs nothing extra."""
    return ["--live-from-start"] if live and platform_of(url) == "youtube" else []


def fetch_audio(url: str, out_dir: Path, sid: str, window: tuple[float, float] | None = None,
                live: bool = False) -> Path:
    tmpl = str(out_dir / f"{sid}.%(ext)s")
    cmd = ytdlp_cmd() + _live_args(url, live) + ["-f", "bestaudio/best", "-x", "--audio-format", "m4a",
                                                 "--no-playlist", "--no-warnings", "-o", tmpl, url]
    if window:
        cmd[-1:-1] = ["--download-sections", f"*{window[0]:.0f}-{window[1]:.0f}"]
    run(cmd, timeout=6 * 3600)
    p = out_dir / f"{sid}.m4a"
    if not p.exists():
        cands = sorted(out_dir.glob(f"{sid}.*"), key=lambda x: x.stat().st_mtime)
        cands = [c for c in cands if c.suffix in (".m4a", ".opus", ".webm", ".mp3", ".aac", ".wav")]
        if not cands:
            raise ToolError("yt-dlp nie zapisał pliku audio")
        p = cands[-1]
    return p


def fetch_chat(url: str, out_dir: Path, sid: str) -> None:
    plat = platform_of(url)
    langs = {"youtube": "live_chat", "twitch": "rechat"}.get(plat)
    if not langs:
        return
    try:
        run(ytdlp_cmd() + ["--skip-download", "--write-subs", "--sub-langs", langs, "--no-warnings",
                           "-o", str(out_dir / f"{sid}.%(ext)s"), url], timeout=1800)
    except ToolError as e:
        log(f"  czat niedostępny ({str(e).splitlines()[-1][:120]})")


def _rx(pattern: str | None):
    return re.compile(pattern, re.I) if pattern else None


def topic_plan(info: dict, s: dict) -> dict:
    """Is this video (or which part of it) about the game? Looks at metadata, not only the title.

    Twitch VODs carry chapters with the game being played and its time range, so only the GTA
    parts of a long variety stream are taken. Kick has the stream category. YouTube only has
    title / description / tags; when they say nothing, the verdict is "unknown" and a short
    transcript probe decides later.
    Returns {"verdict": "yes" | "no" | "unknown", "windows": [(start, end), ...] or None (= whole), "why": str}."""
    game = _rx(s.get("game_regex"))
    title = _rx(s.get("title_regex"))
    plat = platform_of(info.get("webpage_url") or info.get("url") or "")
    dur = float(info.get("duration") or 0)
    chapters = [c for c in info.get("chapters") or [] if c.get("title")]
    timed = [c for c in chapters if c.get("start_time") is not None and c.get("end_time") is not None]
    if game and timed:
        hits = [c for c in timed if game.search(c["title"])]
        if not hits:
            return {"verdict": "no", "windows": [],
                    "why": "w streamie: " + ", ".join(dict.fromkeys(c["title"] for c in timed))[:140]}
        wins: list[tuple[float, float]] = []
        for c in sorted(hits, key=lambda c: c["start_time"]):
            a, b = float(c["start_time"]), float(c["end_time"])
            if b <= a:  # the chapter still running in an ongoing stream has end == start
                b = dur
            if wins and a - wins[-1][1] <= 600:  # short break between GTA parts -> one window
                wins[-1] = (wins[-1][0], max(wins[-1][1], b))
            else:
                wins.append((a, b))
        return {"verdict": "yes", "windows": wins,
                "why": "rozdziały z grą: " + ", ".join(dict.fromkeys(c["title"] for c in hits))}
    games = [c["title"] for c in chapters] + (info.get("categories") or [] if plat in ("twitch", "kick") else [])
    if game and any(game.search(g) for g in games):
        return {"verdict": "yes", "windows": None, "why": "gra: " + ", ".join(games)}
    text = " ".join(str(x or "") for x in (info.get("title"), info.get("description"), " ".join(info.get("tags") or [])))
    if (title and title.search(text)) or (game and game.search(text)):
        return {"verdict": "yes", "windows": None, "why": "tytuł / opis"}
    if games:  # Twitch / Kick told us the game and it is not GTA
        return {"verdict": "no", "windows": [], "why": "gra: " + ", ".join(dict.fromkeys(games))[:140]}
    return {"verdict": "unknown", "windows": None, "why": "brak informacji o grze"}


def plan_windows(wins: list[tuple[float, float]] | None, dur: float, max_len: float, done_until: float = 0.0,
                 live: bool = False, min_len: float = 300.0) -> list[tuple[float, float]]:
    """Cut the chosen parts into pieces of at most max_len, skipping what was already processed.
    For a stream that is still live, stop a minute before 'now' (the newest part is still being written)."""
    out = []
    end_cap = dur - 60 if live else dur
    for a, b in (wins if wins else [(0.0, dur)]):
        a, b = max(a, done_until, 0.0), min(b, end_cap)
        while b - a >= min_len:
            out.append((round(a, 1), round(min(b, a + max_len), 1)))
            a = out[-1][1]
    return out


def topic_probe(audio: Path, s: dict) -> tuple[bool, int]:
    """Listen to three 90 s samples and count GTA words ("gta", "vice city", "leonida"...)."""
    from .transcribe import _decode, _model

    words = [w.lower() for w in s.get("topic_words") or []]
    total = media_info(audio)["duration"]
    m = _model(s["whisper_model"], s["whisper_device"])
    lang = None if s.get("language") in (None, "any") else s.get("language")
    hits = 0
    for frac in (0.2, 0.5, 0.8):
        start = max(0.0, total * frac - 45)
        segs, _ = m.transcribe(_decode(audio, start, 90), language=lang, vad_filter=True)
        text = " ".join(x.text for x in segs).lower()
        hits += sum(text.count(w) for w in words)
    return hits >= int(s.get("topic_min_hits", 1)), hits


def ingest_source(ws: Workspace, url: str, info: dict | None = None, explicit: bool = False,
                  window: tuple[float, float] | None = None) -> list[str]:
    """Decide which parts of a video to take (game chapters, already processed parts, a stream that is
    still live) and ingest each part. Returns the source ids ready for picking."""
    s = ws.settings()
    if Path(url).exists():
        sid = ingest(ws, url, window=window, explicit=True)
        return [sid] if sid else []
    info = info if info and info.get("duration") is not None else fetch_info(url)
    meta = slim_meta(info, url)
    status = meta.get("live_status")
    if status == "is_upcoming":
        log(f"  jeszcze się nie zaczęło: {meta.get('title', '')[:60]}")
        return []
    live = status in ("is_live", "post_live")
    base = source_id(url, info)
    state_path = ws.src / f"{base}.state.json"
    state = read_json(state_path, {})
    if state.get("complete") and not explicit and not window:
        return []
    dur = float(info.get("duration") or 0)
    if live and not dur:  # YouTube live: no duration yet -> time since it started
        ts = info.get("release_timestamp") or info.get("timestamp")
        dur = max(0.0, time.time() - ts) if ts else 0.0
    plan = {"verdict": "yes", "windows": [window] if window else None, "why": "wskazany fragment"}
    if not window:
        plan = topic_plan(info, s)
        if plan["verdict"] == "no" and not explicit:
            log(f"  pomijam — to nie GTA ({plan['why']})")
            if not live:  # a live stream may still switch to GTA later
                write_json(state_path, {**state, "complete": True, "skipped": plan["why"]})
            return []
        if plan["verdict"] == "no":  # a link given by hand: take it anyway
            plan = {"verdict": "yes", "windows": None, "why": "link podany ręcznie"}
    wins = plan_windows(plan["windows"], dur, s["max_source_hours"] * 3600,
                        0.0 if (window or explicit) else state.get("done_until", 0.0), live)
    if not wins:
        log("  nic nowego do wzięcia" + (" (stream trwa — kolejna część przy następnym przebiegu)" if live else ""))
        return []
    if live:
        log(f"  stream trwa — biorę to, co już było ({hms(wins[0][0])}–{hms(wins[-1][1])})")
    elif plan["windows"]:
        log(f"  {plan['why']} → {', '.join(f'{hms(a)}–{hms(b)}' for a, b in wins)}")
    ready = []
    for a, b in wins:
        whole = a <= 1 and b >= dur - 1 and not live
        try:
            sid = ingest(ws, url, info=info, window=None if whole else (a, b), explicit=explicit, base_sid=base,
                         live=live, probe=plan["verdict"] == "unknown" and not explicit)
        except ToolError as e:
            log(f"  błąd: {e}")
            break
        state = {**read_json(state_path, {}), "done_until": b, "live": live}
        write_json(state_path, state)
        if sid:
            ready.append(sid)
    if not live and not explicit:
        write_json(state_path, {**read_json(state_path, {}), "complete": True})
    return ready


def ingest(ws: Workspace, url: str, info: dict | None = None, window: tuple[float, float] | None = None,
           force: bool = False, explicit: bool = False, base_sid: str | None = None, live: bool = False,
           probe: bool = False) -> str | None:
    """Fetch one source (or one part of it): audio + metadata + chat + transcript.
    Returns source id or None if skipped.

    explicit=True (a link or file the user gave by hand): no language filter, language is auto-detected.
    probe=True: first listen to a few samples and skip it if nobody mentions GTA."""
    s = ws.settings()
    ws.ensure()
    if Path(url).exists():  # local gameplay / stream file
        p = Path(url).resolve()
        sid = source_id(str(p))
        meta = {"id": sid, "title": p.stem, "name": s.get("watermark") or "Gameplay", "url": str(p),
                "platform": "file", "duration": media_info(p)["duration"], "local_file": str(p)}
        audio = ws.src / f"{sid}.m4a"
        old = read_json(ws.src / f"{sid}.meta.json", {})
        if (ws.src / f"{sid}.json").exists() and not force and not old.get("skipped"):
            log(f"  już jest: {sid}")
            return sid
        if not audio.exists() or force:
            run(["ffmpeg", "-y", "-v", "error", "-i", p, "-vn", "-ac", "1", "-c:a", "aac", "-b:a", "96k", audio])
    else:
        info = info if info and info.get("duration") is not None else fetch_info(url)
        base = base_sid or source_id(url, info)
        sid = f"{base}_{int(window[0])}" if window else base
        meta = slim_meta(info, url)
        if meta.get("live_status") == "is_upcoming":
            log(f"  jeszcze się nie zaczęło: {meta.get('title', '')[:60]}")
            return None
        live = live or meta.get("live_status") in ("is_live", "post_live")
        meta["live"] = live
        dur = meta.get("duration") or 0
        if not window and dur > s["max_source_hours"] * 3600:
            log(f"  za długie ({hms(dur)}). Podaj okno, np. --window 1:00:00-2:00:00")
            return None
        if (ws.src / f"{sid}.json").exists() and not force:
            log(f"  już jest: {sid}")
            return sid
        audio = fetch_audio(meta["url"], ws.src, sid, window, live=live)
        if not live:
            fetch_chat(meta["url"], ws.src, sid)
    if window:
        meta["window"] = list(window)
    meta["fetched_at"] = int(time.time())
    write_json(ws.src / f"{sid}.meta.json", meta)

    if probe:
        ok, hits = topic_probe(audio, s)
        if not ok:
            log("  w próbkach nie słychać GTA — pomijam (jeśli to jednak GTA, wklej link ręcznie)")
            meta["skipped"] = "topic"
            write_json(ws.src / f"{sid}.meta.json", meta)
            return None
        log(f"  w próbkach słychać GTA ({hits}×)")

    off = window[0] if window else 0.0
    lang = None if explicit else s.get("language")
    if lang and lang != "any":
        got = detect_language(audio, s["whisper_model"], s["whisper_device"])
        if got and got != lang:
            log(f"  inny język ({got} zamiast {lang}) — pomijam")
            meta["skipped"] = f"language {got}"
            write_json(ws.src / f"{sid}.meta.json", meta)
            return None
    # Twitch VOD chat comes from Twitch directly (yt-dlp has no Twitch chat); fetched while we transcribe
    chat_thread = None
    if meta.get("platform") == "twitch" and info and str(info.get("id", "")).lstrip("v").isdigit():
        from .chat import fetch_twitch_vod_chat

        a = off
        b = window[1] if window else float(meta.get("duration") or 0)
        chat_thread = threading.Thread(target=fetch_twitch_vod_chat, daemon=True,
                                       args=(str(info["id"]), a, b, ws.src / f"{sid}.chat.json"))
        chat_thread.start()
    tr = transcribe(audio, ws.src / sid, language=None if lang in (None, "any") else lang,
                    model=s["whisper_model"], device=s["whisper_device"])
    if chat_thread:
        chat_thread.join(timeout=1800)
    if off:  # sectioned download: shift to absolute stream time
        for seg in tr["segments"]:
            seg["start"] += off
            seg["end"] += off
            for w in seg["words"]:
                w["s"] = round(w["s"] + off, 2)
                w["e"] = round(w["e"] + off, 2)
        tr["offset"] = off
        write_json(ws.src / f"{sid}.json", tr)
    log(f"  ok {sid}: {len(tr['segments'])} zdań, język {tr['language']}")
    return sid


def find(ws: Workspace, query: str | None = None, count: int = 5, urls: list[str] | None = None,
         window: tuple[float, float] | None = None) -> list[str]:
    """Find & ingest up to `count` new sources. Returns source ids ready for picking."""
    s = ws.settings()
    ready = []
    if urls:
        for u in urls:
            log(f"• {u}")
            try:
                ready += ingest_source(ws, u, explicit=True, window=window)
            except ToolError as e:
                log(f"  błąd: {e}")
        return ready
    rx = re.compile(s["title_regex"], re.I) if s.get("title_regex") else None
    rules = {st["name"].lower(): st.get("rules", "unknown") for st in ws.streamers()}
    for e in list_candidates(ws, query):
        if len(ready) >= count:
            break
        title = e.get("title") or ""
        # general search: the title must say GTA. Your streamers / channels: the game is checked from
        # chapters / category / description / a short listen instead (titles like "🐝LIVE🐝DRAMA🐝").
        if e.get("_from") == "search" and rx and not rx.search(title):
            continue
        if e.get("live_status") == "is_upcoming":
            continue
        sid_guess = source_id(e["url"], e)
        if read_json(ws.src / f"{sid_guess}.state.json", {}).get("complete") or \
                (ws.src / f"{sid_guess}.meta.json").exists():
            continue
        try:
            info = fetch_info(e["url"])
        except ToolError as err:
            log(f"  pomijam {title[:50]}: {str(err).splitlines()[-1][:100]}")
            continue
        name = (info.get("channel") or info.get("uploader") or "").lower()
        if rules.get(name) == "no":
            log(f"  {name}: nie zezwala na klipowanie — pomijam")
            continue
        age = _age_hours(info)
        if age is not None and age > s["within_hours"]:
            continue
        log(f"• {info.get('channel') or info.get('uploader')} | {title[:70]}")
        try:
            ready += ingest_source(ws, e["url"], info=info)
        except ToolError as err:
            log(f"  błąd: {err}")
    log(f"{len(ready)} nowych źródeł z transkrypcją → {ws.src}")
    return ready


def fetch_section(meta: dict, start: float, end: float, out: Path, max_height: int = 1080) -> Path:
    """Download (or cut locally) only [start, end] of the source video."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if meta.get("local_file"):
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", meta["local_file"],
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", out])
        return out
    tmpl = str(out.with_suffix("")) + ".%(ext)s"
    run(ytdlp_cmd() + _live_args(meta["url"], bool(meta.get("live"))) +
        ["--download-sections", f"*{start:.2f}-{end:.2f}", "--force-keyframes-at-cuts",
                       "-f", f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b", "--merge-output-format", "mp4",
                       "--no-playlist", "--no-warnings", "-o", tmpl, meta["url"]], timeout=1800)
    if not out.exists():
        got = sorted(out.parent.glob(out.stem + ".*"))
        got = [g for g in got if g.suffix in (".mp4", ".mkv", ".webm")]
        if not got:
            raise ToolError("nie udało się pobrać fragmentu wideo")
        run(["ffmpeg", "-y", "-v", "error", "-i", got[0], "-c", "copy", out])
        got[0].unlink(missing_ok=True)
    return out


def load_sources(ws: Workspace, ids: list[str] | None = None) -> list[tuple[dict, dict]]:
    """[(meta, transcript)] for given ids (or all not yet used)."""
    out = []
    metas = sorted(ws.src.glob("*.meta.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for mp in metas:
        sid = mp.name[:-len(".meta.json")]
        if ids and sid not in ids:
            continue
        meta = read_json(mp, {})
        if meta.get("skipped"):
            continue
        tr = read_json(ws.src / f"{sid}.json", None)
        if not tr:
            continue
        if not ids and meta.get("used"):
            continue
        meta["sid"] = sid
        out.append((meta, tr))
    return out


def clean_old(ws: Workspace, days: int = 7) -> int:
    cut = time.time() - days * 86400
    n = 0
    for p in ws.src.iterdir():
        if p.is_file() and p.stat().st_mtime < cut and p.suffix in (".m4a", ".opus", ".webm", ".wav"):
            p.unlink()
            n += 1
    shutil.rmtree(ws.peek, ignore_errors=True)
    return n
