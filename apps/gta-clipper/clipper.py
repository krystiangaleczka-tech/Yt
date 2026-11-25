#!/usr/bin/env python3
"""GTA Clipper — command line.

  python clipper.py setup                       install tools, fonts, speech model
  python clipper.py doctor                      what is installed
  python clipper.py find [--count 5] [--query "GTA 6"] [--url URL ...] [--window 1:00:00-2:00:00]
  python clipper.py pick [--mode free|smart|deep|agent] [--count 10] | --from-raw
  python clipper.py peek                        4 frames per pick
  python clipper.py render [--workers 3]        picks.json -> finished Shorts
  python clipper.py make [--count 10] [--url URL ...]   find + pick + render in one go
  python clipper.py qc                          re-check all Shorts
  python clipper.py clip URL_OR_FILE START END [--hook "..."]   one Short by hand
  python clipper.py change SHORT_ID "end 2 seconds earlier"
  python clipper.py look SHORT_ID --style beast --flip --watermark "@me"
  python clipper.py voice SHORT_ID FILE [--at payoff|start|SECONDS]
  python clipper.py live CHANNEL [CHANNEL ...] [--ratio 2 --min 40] | live buffer CHANNEL
  python clipper.py schedule [--every 90] [--first 10:00]   spread approved Shorts
  python clipper.py autopilot on|off|run|preview
  python clipper.py posttext                    title + hashtags of approved Shorts
  python clipper.py app [--port 8765]           the review app in your browser
  python clipper.py clean [--days 7]            delete old source audio
  python clipper.py install-skill               install the Claude Code skill to ~/.claude/skills/gta-clipper
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from gtaclip.config import Workspace  # noqa: E402
from gtaclip.util import ToolError, parse_time  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(prog="clipper", description="GTA Clipper")
    ap.add_argument("--workspace", "-w", default=None, help="folder roboczy (domyślnie ~/gta-shorts)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("setup"); sp.add_argument("--no-packages", action="store_true")
    sub.add_parser("doctor")
    sp = sub.add_parser("find")
    sp.add_argument("--count", type=int, default=5); sp.add_argument("--query"); sp.add_argument("--url", nargs="*")
    sp.add_argument("--window")
    sp = sub.add_parser("pick")
    sp.add_argument("--mode", choices=["free", "smart", "deep", "agent"]); sp.add_argument("--count", type=int)
    sp.add_argument("--from-raw", action="store_true"); sp.add_argument("--sources", nargs="*")
    sub.add_parser("peek")
    sp = sub.add_parser("render"); sp.add_argument("--workers", type=int); sp.add_argument("--picks")
    sp = sub.add_parser("make")
    sp.add_argument("--count", type=int); sp.add_argument("--url", nargs="*"); sp.add_argument("--query")
    sp.add_argument("--mode", choices=["free", "smart", "deep"]); sp.add_argument("--window")
    sub.add_parser("qc")
    sp = sub.add_parser("clip")
    sp.add_argument("source"); sp.add_argument("start"); sp.add_argument("end")
    sp.add_argument("--hook", default=""); sp.add_argument("--title", default="")
    sp = sub.add_parser("change"); sp.add_argument("short_id"); sp.add_argument("request")
    sp = sub.add_parser("look"); sp.add_argument("short_id")
    sp.add_argument("--style"); sp.add_argument("--layout"); sp.add_argument("--flip", action="store_true")
    sp.add_argument("--watermark")
    sp = sub.add_parser("voice"); sp.add_argument("short_id"); sp.add_argument("file", nargs="?")
    sp.add_argument("--at", default="payoff")
    sp = sub.add_parser("live"); sp.add_argument("channels", nargs="+")
    sp.add_argument("--ratio", type=float); sp.add_argument("--min", type=float, dest="min_rate")
    sp = sub.add_parser("schedule"); sp.add_argument("--every", type=int); sp.add_argument("--first")
    sp.add_argument("--preview", action="store_true")
    sp = sub.add_parser("autopilot"); sp.add_argument("action", choices=["on", "off", "run", "preview"])
    sub.add_parser("posttext")
    sp = sub.add_parser("app"); sp.add_argument("--port", type=int, default=8765); sp.add_argument("--no-browser", action="store_true")
    sp = sub.add_parser("clean"); sp.add_argument("--days", type=int, default=7)
    sub.add_parser("install-skill")
    a = ap.parse_args(argv)
    ws = Workspace(a.workspace).ensure()

    def window():
        if not getattr(a, "window", None):
            return None
        x, y = a.window.split("-")
        return parse_time(x), parse_time(y)

    try:
        if a.cmd == "setup":
            from gtaclip.setup import setup
            setup(ws, packages=not a.no_packages)
        elif a.cmd == "doctor":
            from gtaclip.setup import doctor
            print(json.dumps(doctor(ws), indent=2, ensure_ascii=False))
        elif a.cmd == "find":
            from gtaclip.sources import find
            find(ws, a.query, a.count, a.url, window())
        elif a.cmd == "pick":
            from gtaclip.pick import from_raw, pick
            from_raw(ws) if a.from_raw else pick(ws, a.mode, a.count, a.sources)
        elif a.cmd == "peek":
            from gtaclip.peek import peek
            peek(ws)
        elif a.cmd == "render":
            from gtaclip.config import read_json
            from gtaclip.render import render_batch
            render_batch(ws, read_json(Path(a.picks) if a.picks else ws.path("picks.json"), []), a.workers)
        elif a.cmd == "make":
            from gtaclip.pick import pick
            from gtaclip.render import render_batch
            from gtaclip.sources import find
            s = ws.settings()
            count = a.count or s["shorts_per_run"]
            ids = find(ws, a.query, max(2, count // 2), a.url, window())
            picks = pick(ws, a.mode, count, ids if a.url else None)
            if picks:
                render_batch(ws, picks)
        elif a.cmd == "qc":
            from gtaclip.qc import check_folder
            for r in check_folder(ws):
                print(f"{r['status']:<5} {r['id']}  {'; '.join(r['notes'])}")
        elif a.cmd == "clip":
            from gtaclip.pick import short_name
            from gtaclip.render import render_pick
            from gtaclip.sources import ingest
            st, en = parse_time(a.start), parse_time(a.end)
            sid = ingest(ws, a.source, window=None, explicit=True)
            if not sid:
                raise ToolError("nie udało się wczytać źródła")
            from gtaclip.config import read_json
            meta = read_json(ws.src / f"{sid}.meta.json", {})
            p = {"sid": sid, "url": meta.get("url"), "name": meta.get("name"), "start": st, "end": en,
                 "peak": st + (en - st) * 0.7, "hook": a.hook.upper() or f"{short_name(meta.get('name'))} IN GTA 6",
                 "title": a.title or meta.get("title", "")[:70], "hashtags": ["#gta6", "#shorts"], "keywords": [],
                 "score": 0, "credit": f"Clip: {meta.get('name')} — {meta.get('url')}"}
            import time as _t
            render_pick(ws, p, 1, _t.strftime("%Y%m%d-%H%M") + "-hand")
        elif a.cmd == "change":
            from gtaclip.versions import change_by_words
            change_by_words(ws, a.short_id, a.request)
        elif a.cmd == "look":
            from gtaclip.versions import new_version
            look = {k: v for k, v in (("style", a.style), ("layout", a.layout), ("watermark", a.watermark)) if v is not None}
            if a.flip:
                look["flip"] = True
            new_version(ws, a.short_id, {"look": look}, f"wygląd: {look}")
        elif a.cmd == "voice":
            from gtaclip.versions import add_voice, newest_recording
            f = a.file or newest_recording()
            if not f:
                raise ToolError("Nie znalazłem nagrania. Podaj plik.")
            add_voice(ws, a.short_id, f, a.at)
        elif a.cmd == "live":
            from gtaclip.live import Hunt, run_cli
            if a.channels[0] == "buffer":
                print(Hunt(ws, a.channels[1]).buffer() or "brak nagranych segmentów")
            else:
                run_cli(ws, a.channels, a.ratio, a.min_rate)
        elif a.cmd == "schedule":
            from gtaclip.schedule import auto_schedule
            from gtaclip.versions import library
            ids = [x["id"] for x in library(ws) if x["status"] == "approved" and not x.get("scheduled_at")]
            for p in auto_schedule(ws, ids, a.every, a.first, preview=a.preview):
                print(p["label"], p["id"])
        elif a.cmd == "autopilot":
            from gtaclip import schedule as sch
            if a.action == "run":
                sch.autopilot_run(ws)
            elif a.action == "preview":
                print(json.dumps(sch.autopilot_commands(ws), indent=2, ensure_ascii=False))
            else:
                print(json.dumps(sch.autopilot_enable(ws, a.action == "on"), indent=2, ensure_ascii=False))
        elif a.cmd == "posttext":
            from gtaclip.versions import library
            for x in library(ws):
                if x["status"] == "approved":
                    print((ws.shorts / x["id"] / "post.txt").read_text(encoding="utf-8"))
                    print("-" * 40)
        elif a.cmd == "app":
            from gtaclip.app import serve
            serve(ws, a.port, open_browser=not a.no_browser)
        elif a.cmd == "install-skill":
            app_dir = Path(__file__).resolve().parent
            dst = Path.home() / ".claude" / "skills" / "gta-clipper" / "SKILL.md"
            dst.parent.mkdir(parents=True, exist_ok=True)
            text = (app_dir / "skill" / "SKILL.md").read_text(encoding="utf-8")
            dst.write_text(text.replace("{{APP_DIR}}", app_dir.as_posix()), encoding="utf-8")
            print(f"Skill zainstalowany: {dst}\nUruchom Claude Code ponownie i napisz np. „Zrób 10 Shortsów GTA 6 z najnowszych filmów”.")
        elif a.cmd == "clean":
            from gtaclip.sources import clean_old
            print(f"usunięto {clean_old(ws, a.days)} plików")
    except ToolError as e:
        print(f"BŁĄD: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
