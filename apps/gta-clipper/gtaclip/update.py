"""Self-update from git: check every few hours, update with one click, roll back on failure."""
from __future__ import annotations

import time

from .config import APP_DIR, Workspace
from .util import run


def _git(*args, check=True):
    return run(["git", "-C", APP_DIR, *args], check=check, timeout=120)


def check(ws: Workspace) -> dict:
    try:
        branch = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        _git("fetch", "--quiet", "origin", branch)
        local = _git("rev-parse", "HEAD").stdout.strip()
        remote = _git("rev-parse", "FETCH_HEAD").stdout.strip()
        behind = int(_git("rev-list", "--count", f"HEAD..{remote}").stdout.strip() or 0)
        res = {"available": behind > 0, "behind": behind, "branch": branch, "local": local[:7], "remote": remote[:7]}
    except Exception as e:
        res = {"available": False, "error": str(e)[-300:]}
    ws.save_settings({"updates": {"last_check": int(time.time()), "available": res.get("available", False)}})
    return res


def apply(ws: Workspace) -> dict:
    before = _git("rev-parse", "HEAD").stdout.strip()
    r = _git("pull", "--ff-only", check=False)
    if r.returncode != 0:
        _git("reset", "--keep", before, check=False)  # put the old files back, keep local edits
        return {"ok": False, "out": (r.stdout + r.stderr)[-500:]}
    ws.save_settings({"updates": {"available": False}})
    return {"ok": True, "from": before[:7], "to": _git("rev-parse", "HEAD").stdout.strip()[:7]}
