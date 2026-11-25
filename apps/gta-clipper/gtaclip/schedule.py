"""Posting plan (spread approved Shorts over the day) and Autopilot (daily automatic run)."""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from .config import APP_DIR, Workspace
from .util import log, run

TASK = "GTAClipperAutopilot"


def auto_schedule(ws: Workspace, ids: list[str], every_min: int | None = None, first_at: str | None = None,
                  day: str | None = None, preview: bool = False) -> list[dict]:
    from .versions import load, save

    s = ws.settings()
    every = every_min or s["post_every_min"]
    hh, mm = (first_at or s["post_first_at"]).split(":")
    base = datetime.strptime(day, "%Y-%m-%d") if day else datetime.now()
    first = base.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
    t = first
    if not day and t < datetime.now():
        t = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=15)
        if t.hour >= 22:  # too late today -> start tomorrow morning
            t = first + timedelta(days=1)
    plan = []
    for sid in ids:
        plan.append({"id": sid, "at": int(t.timestamp()), "label": t.strftime("%a %d.%m %H:%M")})
        t += timedelta(minutes=every)
        if t.hour >= 23 or t.date() > (t - timedelta(minutes=every)).date():  # no night posts
            nxt = t if t.date() > (t - timedelta(minutes=every)).date() else t + timedelta(days=1)
            t = nxt.replace(hour=int(hh), minute=int(mm))
    if not preview:
        for p in plan:
            sm = load(ws, p["id"])
            sm["scheduled_at"] = p["at"]
            save(ws, sm)
    return plan


def set_slot(ws: Workspace, short_id: str, at: int | None) -> None:
    from .versions import load, save

    sm = load(ws, short_id)
    sm["scheduled_at"] = at
    save(ws, sm)


# ------------------------------------------------------------------ autopilot
def _python() -> str:
    exe = Path(sys.executable)
    if sys.platform == "win32" and exe.name.lower() == "python.exe" and (exe.parent / "pythonw.exe").exists():
        return str(exe.parent / "pythonw.exe")
    return str(exe)


def autopilot_commands(ws: Workspace) -> dict:
    """What would be installed (shown as a dry preview before turning it on)."""
    ap = ws.settings()["autopilot"]
    hh, mm = ap["time"].split(":")
    script = APP_DIR / "clipper.py"
    run_cmd = f'"{_python()}" "{script}" --workspace "{ws.root}" autopilot run'
    days = ap.get("days") or list(range(7))
    if sys.platform == "win32":
        names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        # schtasks /TR is limited to 261 chars -> point it at a small .cmd in the workspace
        cmd_file = ws.root / "autopilot.cmd"
        install = ["schtasks", "/Create", "/F", "/TN", TASK, "/SC", "WEEKLY", "/D", ",".join(names[d] for d in days),
                   "/ST", f"{int(hh):02d}:{int(mm):02d}", "/TR", f'"{cmd_file}"']
        remove = ["schtasks", "/Delete", "/F", "/TN", TASK]
        return {"kind": "Harmonogram zadań Windows", "install": install, "remove": remove, "run": run_cmd}
    if sys.platform == "darwin":
        plist = Path.home() / "Library/LaunchAgents/com.gtaclipper.autopilot.plist"
        ints = "".join(f"<dict><key>Weekday</key><integer>{(d + 1) % 7}</integer><key>Hour</key><integer>{int(hh)}</integer>"
                       f"<key>Minute</key><integer>{int(mm)}</integer></dict>" for d in days)
        args = "".join(f"<string>{a}</string>" for a in [_python(), str(script), "--workspace", str(ws.root), "autopilot", "run"])
        body = (f'<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key>'
                f"<string>com.gtaclipper.autopilot</string><key>ProgramArguments</key><array>{args}</array>"
                f"<key>StartCalendarInterval</key><array>{ints}</array></dict></plist>")
        return {"kind": "launchd (macOS)", "plist": str(plist), "plist_body": body,
                "install": ["launchctl", "load", str(plist)], "remove": ["launchctl", "unload", str(plist)], "run": run_cmd}
    cron_days = ",".join(str((d + 1) % 7) for d in days)
    line = f"{int(mm)} {int(hh)} * * {cron_days} {run_cmd} >> \"{ws.logs / 'autopilot.log'}\" 2>&1 # {TASK}"
    return {"kind": "crontab", "line": line, "run": run_cmd}


def autopilot_enable(ws: Workspace, on: bool) -> dict:
    cmds = autopilot_commands(ws)
    ws.save_settings({"autopilot": {"enabled": on}})
    if sys.platform == "win32":
        if on:
            (ws.root / "autopilot.cmd").write_text(
                f'@echo off\r\n{cmds["run"]} >> "{ws.logs / "autopilot.log"}" 2>&1\r\n', encoding="utf-8")
        r = run(cmds["install"] if on else cmds["remove"], check=False)
        return {"ok": r.returncode == 0 or not on, "out": (r.stdout + r.stderr)[-400:], **cmds}
    if sys.platform == "darwin":
        p = Path(cmds["plist"])
        if on:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(cmds["plist_body"], encoding="utf-8")
            run(cmds["remove"], check=False)
            r = run(cmds["install"], check=False)
        else:
            r = run(cmds["remove"], check=False)
            p.unlink(missing_ok=True)
        return {"ok": True, "out": (r.stdout + r.stderr)[-400:], **cmds}
    cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout if _has("crontab") else ""
    lines = [ln for ln in cur.splitlines() if TASK not in ln]
    if on:
        lines.append(cmds["line"])
    if _has("crontab"):
        subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n", text=True)
        return {"ok": True, **cmds}
    return {"ok": False, "out": "brak crontab na tym systemie", **cmds}


def _has(x: str) -> bool:
    from shutil import which
    return which(x) is not None


def autopilot_run(ws: Workspace) -> None:
    """The daily run: find new sources, pick, render. Never posts anything."""
    from .pick import pick
    from .render import render_batch
    from .sources import find

    s = ws.settings()
    ap = s["autopilot"]
    log(f"Autopilot {time.strftime('%Y-%m-%d %H:%M')}: {ap['count']} Shortsów")
    find(ws, count=max(3, ap["count"] // 2))
    picks = pick(ws, count=ap["count"])
    if picks:
        render_batch(ws, picks)
