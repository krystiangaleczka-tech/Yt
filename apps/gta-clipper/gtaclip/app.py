"""The Clipper app: a local web page (http://localhost:8765) to review, tweak, plan and run everything.

Runs only on this PC (bound to 127.0.0.1). Heavy work (find/pick/render/new versions)
runs as background jobs = `python clipper.py ...` subprocesses with their own log.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import __version__
from . import ai
from .captions import THEMES
from .config import APP_DIR, Workspace
from .live import HuntManager
from .sources import past_streams, streamer_from_input
from .util import have

WEB = APP_DIR / "web"
CLI = APP_DIR / "clipper.py"

SUGGESTED = [
    ("xQc", "twitch"), ("KaiCenat", "twitch"), ("IShowSpeed", "youtube"), ("summit1g", "twitch"),
    ("shroud", "twitch"), ("sodapoppin", "twitch"), ("adinross", "kick"), ("Ninja", "twitch"),
    ("Valkyrae", "youtube"), ("TimTheTatman", "twitch"), ("Jynxzi", "twitch"), ("Esfand", "twitch"),
    ("Penguinz0", "youtube"), ("Amouranth", "twitch"),
]


class Jobs:
    def __init__(self, ws: Workspace):
        self.ws = ws
        self.items: dict[str, dict] = {}
        self.lock = threading.Lock()

    def start(self, kind: str, label: str, args: list[str], short_id: str | None = None) -> dict:
        jid = time.strftime("%H%M%S") + "-" + uuid.uuid4().hex[:4]
        log = self.ws.logs / f"job-{jid}.log"
        cmd = [sys.executable, str(CLI), "--workspace", str(self.ws.root), *args]
        job = {"id": jid, "kind": kind, "label": label, "cmd": cmd, "status": "running", "started": int(time.time()),
               "ended": None, "log": str(log), "short_id": short_id}
        with self.lock:
            self.items[jid] = job

        def run():
            env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
            with open(log, "w", encoding="utf-8") as f:
                f.write("$ " + " ".join(cmd[1:]) + "\n")
                f.flush()
                flags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW
                p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=str(APP_DIR),
                                     creationflags=flags)
                job["pid"] = p.pid
                rc = p.wait()
            job["status"] = "done" if rc == 0 else "failed"
            job["ended"] = int(time.time())

        threading.Thread(target=run, daemon=True).start()
        return job

    def list(self) -> list[dict]:
        with self.lock:
            items = sorted(self.items.values(), key=lambda j: j["id"], reverse=True)[:30]
        out = []
        for j in items:
            out.append({k: v for k, v in j.items() if k != "cmd"} | {"tail": tail(j["log"], 6)})
        return out

    def busy_shorts(self) -> set[str]:
        return {j["short_id"] for j in self.items.values() if j["status"] == "running" and j.get("short_id")}


def tail(path: str, n: int) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [ln.rstrip() for ln in f.readlines() if ln.strip() and "HF Hub" not in ln]
        return lines[-n:]
    except OSError:
        return []


class App:
    def __init__(self, ws: Workspace):
        self.ws = ws.ensure()
        self.jobs = Jobs(self.ws)
        self.live = HuntManager(self.ws)
        self.update_info: dict = {}
        threading.Thread(target=self._update_loop, daemon=True).start()

    # ------------------------------------------------------------ state
    def state(self) -> dict:
        from .versions import library

        s = self.ws.settings()
        lib = library(self.ws)
        counts = {"new": 0, "approved": 0, "rejected": 0, "scheduled": 0, "published": 0}
        for x in lib:
            counts[x["status"]] = counts.get(x["status"], 0) + 1
            if x.get("scheduled_at") and not x.get("published"):
                counts["scheduled"] += 1
            if x.get("published"):
                counts["published"] += 1
        return {
            "version": __version__, "settings": s, "streamers": self.ws.streamers(), "counts": counts,
            "live": self.live.status(), "jobs": self.jobs.list(), "themes": THEMES,
            "ai_available": ai.available(s), "ffmpeg": have("ffmpeg"), "workspace": str(self.ws.root),
            "update": self.update_info, "suggested": [{"name": n, "platform": p} for n, p in SUGGESTED],
            "platform": sys.platform,
        }

    def shorts(self) -> list[dict]:
        from .versions import library

        busy = self.jobs.busy_shorts()
        out = []
        for sm in library(self.ws):
            cur = sm["versions"][sm.get("current", 0)]
            post = (self.ws.shorts / sm["id"] / "post.txt")
            out.append({
                "id": sm["id"], "status": sm["status"], "created": sm["created"], "batch": sm.get("batch"),
                "source": sm.get("source", "vod"), "name": sm["pick"].get("name"), "hook": sm["pick"].get("hook"),
                "title": sm["pick"].get("title"), "hashtags": sm["pick"].get("hashtags", []),
                "credit": sm["pick"].get("credit", ""), "score": sm["pick"].get("score", 0),
                "why": sm["pick"].get("why") or " ".join(sm["pick"].get("tags", [])),
                "source_title": sm["pick"].get("source_title"), "url": sm["pick"].get("url"),
                "start": sm["pick"].get("start"), "current": sm.get("current", 0),
                "versions": [{"v": v["v"], "note": v["note"], "file": f"/media/shorts/{sm['id']}/{v['file']}",
                              "cover": f"/media/shorts/{sm['id']}/{v['cover']}", "duration": v["duration"],
                              "layout": v["layout"], "qc": v["qc"], "created": v["created"]} for v in sm["versions"]],
                "qc": cur["qc"], "duration": cur["duration"], "cover": f"/media/shorts/{sm['id']}/{cur['cover']}",
                "file": f"/media/shorts/{sm['id']}/{cur['file']}", "scheduled_at": sm.get("scheduled_at"),
                "published": sm.get("published", False), "busy": sm["id"] in busy,
                "post": post.read_text(encoding="utf-8") if post.exists() else "",
                "look": (sm.get("spec_versions", {}).get(str(cur["v"]), {}) or {}).get("look", {}),
            })
        return out

    # ------------------------------------------------------------ updates
    def _update_loop(self):
        from . import update

        while True:
            s = self.ws.settings()
            if s["updates"]["auto_check"] and time.time() - s["updates"].get("last_check", 0) > 5 * 3600:
                self.update_info = update.check(self.ws)
            time.sleep(600)

    # ------------------------------------------------------------ actions
    def post(self, path: str, body: dict):  # noqa: C901 — a flat router is easiest to read
        from . import schedule as sch
        from . import update
        from .versions import load, save, set_status

        ws = self.ws
        m = re.match(r"/api/shorts/([^/]+)/(\w+)$", path)
        if m:
            sid, act = m.group(1), m.group(2)
            if act == "status":
                return set_status(ws, sid, body["status"])
            if act == "current":
                sm = load(ws, sid)
                sm["current"] = int(body["index"])
                save(ws, sm)
                return {"ok": True}
            if act == "change":
                return self.jobs.start("change", f"Zmiana: {body['request'][:40]}", ["change", sid, body["request"]], sid)
            if act == "look":
                args = ["look", sid]
                lk = body.get("look", {})
                if lk.get("style"):
                    args += ["--style", lk["style"]]
                if lk.get("layout"):
                    args += ["--layout", lk["layout"]]
                if lk.get("flip"):
                    args += ["--flip"]
                if lk.get("watermark") is not None:
                    args += ["--watermark", lk["watermark"]]
                return self.jobs.start("look", "Nowy wygląd", args, sid)
            if act == "voice":
                raw = base64.b64decode(body["data"].split(",", 1)[-1])
                ext = Path(body.get("name") or "voice.webm").suffix or ".webm"
                f = ws.shorts / sid / f"upload_{int(time.time())}{ext}"
                f.write_bytes(raw)
                return self.jobs.start("voice", "Głos lektora", ["voice", sid, str(f), "--at", str(body.get("at", "payoff"))], sid)
            if act == "post":
                sm = load(ws, sid)
                for k in ("title", "hashtags", "credit"):
                    if k in body:
                        sm["pick"][k] = body[k]
                save(ws, sm)
                from .render import post_text
                (ws.shorts / sid / "post.txt").write_text(post_text(sm["pick"]), encoding="utf-8")
                return {"ok": True}
            if act == "schedule":
                sch.set_slot(ws, sid, body.get("at"))
                return {"ok": True}
            if act == "published":
                sm = load(ws, sid)
                sm["published"] = bool(body.get("published", True))
                sm["published_at"] = int(time.time()) if sm["published"] else None
                save(ws, sm)
                return {"ok": True}
        if path == "/api/settings":
            return ws.save_settings(body)
        if path == "/api/setup/finish":
            items = []
            for st in body.get("streamers", []):
                items.append({"name": st["name"], "platform": st.get("platform", "twitch"), "enabled": True,
                              "live_watch": False, "rules": st.get("rules", "unknown"), "note": ""})
            ws.save_streamers(items)
            return ws.save_settings({"language": body.get("language", "en"), "ai": body.get("ai", "claude"),
                                     "setup_done": True})
        if path == "/api/streamers":
            ws.save_streamers(body["items"])
            return {"ok": True}
        if path == "/api/streamers/add":
            st = streamer_from_input(body["text"])
            items = ws.streamers()
            if not any(x["name"].lower() == st["name"].lower() for x in items):
                items.append(st)
                ws.save_streamers(items)
            return st
        if path == "/api/streamers/past":
            st = next((x for x in ws.streamers() if x["name"] == body["name"]), None)
            return past_streams(st) if st else []
        if path in ("/api/make", "/api/make/preview"):
            args = ["make"]
            if body.get("count"):
                args += ["--count", str(int(body["count"]))]
            if body.get("mode"):
                args += ["--mode", body["mode"]]
            urls = [u.strip() for u in re.split(r"[\s,]+", body.get("urls") or "") if u.strip()]
            if urls:
                args += ["--url", *urls]
            if body.get("query"):
                args += ["--query", body["query"]]
            if body.get("window"):
                args += ["--window", body["window"]]
            if path.endswith("preview"):
                return {"cmd": "python clipper.py " + " ".join(f'"{a}"' if " " in a else a for a in args)}
            label = f"Zrób Shorty ({body.get('count') or 'domyślnie'})" + (f" · linki: {len(urls)}" if urls else "")
            return self.jobs.start("make", label, args)
        if path == "/api/live/start":
            chans = body.get("channels") or [x["name"] for x in ws.streamers() if x.get("live_watch") and x["platform"] == "twitch"]
            self.live.start(chans)
            return {"ok": True, "channels": chans}
        if path == "/api/live/stop":
            self.live.stop(body.get("channels"))
            return {"ok": True}
        if path == "/api/schedule/auto":
            return sch.auto_schedule(ws, body["ids"], body.get("every"), body.get("first"), body.get("day"),
                                     preview=bool(body.get("preview")))
        if path == "/api/autopilot":
            ws.save_settings({"autopilot": {k: body[k] for k in ("time", "count", "days") if k in body}})
            if "enabled" in body:
                return sch.autopilot_enable(ws, bool(body["enabled"]))
            return {"ok": True}
        if path == "/api/autopilot/preview":
            return sch.autopilot_commands(ws)
        if path == "/api/autopilot/run":
            return self.jobs.start("autopilot", "Autopilot (ręcznie)", ["autopilot", "run"])
        if path == "/api/update/check":
            self.update_info = update.check(ws)
            return self.update_info
        if path == "/api/update/apply":
            res = update.apply(ws)
            if res.get("ok"):
                threading.Timer(1.0, restart).start()
            return res
        if path == "/api/propose":
            s = ws.settings()
            q = urllib.parse.urlencode({"title": f"[GTA Clipper] {body['text'][:60]}", "body": body["text"]})
            return {"url": f"{s['repo_issue_url']}?{q}"}
        if path == "/api/ai/check":
            return {"available": ai.available({**ws.settings(), **body})}
        raise KeyError(path)


def restart():
    os.execv(sys.executable, [sys.executable, *sys.argv])


class Handler(BaseHTTPRequestHandler):
    app: App = None  # set in serve()

    def log_message(self, fmt, *args):  # quiet
        pass

    def _json(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _file(self, p: Path, cache=False):
        if not p.exists() or not p.is_file():
            return self.send_error(HTTPStatus.NOT_FOUND)
        size = p.stat().st_size
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        if p.suffix in (".js", ".css", ".html"):
            ctype += "; charset=utf-8"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng and (m := re.match(r"bytes=(\d*)-(\d*)", rng)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = size - int(m.group(2))
            end = min(end, size - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "max-age=3600" if cache else "no-cache")
        self.end_headers()
        with open(p, "rb") as f:
            f.seek(start)
            left = end - start + 1
            try:
                while left > 0:
                    chunk = f.read(min(1 << 16, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(u.path)
        a = self.app
        try:
            if path in ("/", "/index.html"):
                return self._file(WEB / "index.html")
            if path.startswith("/static/"):
                return self._file(_safe(WEB, path[len("/static/"):]))
            if path.startswith("/media/"):
                return self._file(_safe(a.ws.root, path[len("/media/"):]), cache=True)
            if path == "/api/state":
                return self._json(a.state())
            if path == "/api/shorts":
                return self._json(a.shorts())
            if path == "/api/posttext":
                st = urllib.parse.parse_qs(u.query).get("status", ["approved"])[0]
                txt = "\n\n-----\n\n".join(x["post"] for x in a.shorts() if st == "all" or x["status"] == st)
                return self._json({"text": txt})
            if m := re.match(r"/api/jobs/([\w-]+)/log$", path):
                j = a.jobs.items.get(m.group(1))
                return self._json({"lines": tail(j["log"], 400) if j else []})
            self.send_error(HTTPStatus.NOT_FOUND)
        except PermissionError:
            self.send_error(HTTPStatus.FORBIDDEN)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "zły JSON"}, 400)
        try:
            return self._json(self.app.post(path, body))
        except KeyError as e:
            return self._json({"error": f"nieznane: {e}"}, 404)
        except Exception as e:
            return self._json({"error": str(e)}, 500)


def _safe(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    if root.resolve() not in p.parents and p != root.resolve():
        raise PermissionError(rel)
    return p


def serve(ws: Workspace, port: int = 8765, open_browser: bool = True) -> None:
    from .setup import fonts

    ws.ensure()
    fonts(ws)
    Handler.app = App(ws)
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"GTA Clipper działa: {url}  (Ctrl+C kończy)", flush=True)
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        Handler.app.live.stop()
