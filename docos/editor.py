"""DocOS Editor — lokalny edytor storyboardu w przeglądarce.

    ../pilot/.venv/bin/python -I editor.py PROJECT.json [--port 8765]
    -> http://localhost:8765

Edycja ujęć (typ, tekst, plik, czas, przejście, styl), narracji, podgląd miniatur i szybki render podglądu
(segmenty per beat z cache). Zapis trafia wprost do pliku projektu DocOS.
"""
import argparse
import hashlib
import json
import mimetypes
import re
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, str(Path(__file__).parent))

import docos  # noqa: E402
import render_doc as RD  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).parent
STYLES = ["auto", "typewriter", "stamp", "lower-left", "top-right", "center-big", "side-bar", "highlight", "minimal", "cards", "split", "diagonal", "wipe", "pip"]
LOCK = threading.Lock()


class App:
    def __init__(self, project: Path):
        self.project = project.resolve()
        self.root = self.project.parent
        self.thumbs = self.root / ".editor_cache" / "thumbs"
        self.mthumbs = self.root / ".editor_cache" / "media"
        self.out = self.root / ".editor_cache" / "out"
        for d in (self.thumbs, self.mthumbs, self.out):
            d.mkdir(parents=True, exist_ok=True)
        self.job = {"running": False, "log": [], "url": "", "kind": ""}
        self._media = None

    # ── projekt ──
    def load(self):
        return json.loads(self.project.read_text(encoding="utf-8"))

    def save(self, prj):
        with LOCK:
            for b in prj["beats"]:
                for i, s in enumerate(b.get("shots", []), start=1):
                    s["n"] = i
                    s["dur"] = float(s.get("dur") or 1)
            bak = self.project.with_suffix(".bak.json")
            bak.write_text(self.project.read_text(encoding="utf-8"), encoding="utf-8")
            docos.dump(self.project, prj)

    def media(self):
        if self._media is None:
            self._media = RD.make_media(self.load(), self.root)
        return self._media

    def media_list(self):
        lic = {}
        for lp in RD.film_config(self.load())["credits"]:
            p = self.root / lp
            if p.exists():
                for x in json.loads(p.read_text()):
                    lic[x["file"]] = f"{x['license']} — {(x.get('artist') or '')[:40]}"
        out = []
        for name, p in sorted(self.media().index.items()):
            ext = p.suffix.lower()
            kind = "video" if ext in RD.VIDEO_EXT else "audio" if ext in (".wav", ".mp3") else "image" if ext in (
                ".jpg", ".jpeg", ".png", ".gif") else None
            if kind:
                folder = p.parent.name
                out.append(dict(name=name, kind=kind, folder=folder,
                                license=lic.get(name, "NOAA — public domain" if folder == "noaa" else
                                                "AI" if folder == "ai" else "")))
        return out

    def state(self):
        prj = self.load()
        fp = RD.plan_film(prj, self.root, 12)
        timing = {b["id"]: dict(start=round(b["start"], 2), dur=round(b["dur"], 2)) for b in fp["beats"]}
        shot_times = {}
        for sp in fp["specs"]:
            shot_times[f"{sp['beat']}_{sp['shot']['wiz']}"] = dict(st=round(sp["st"], 2), d=round(sp["d"], 2),
                                                                 transition=sp["transition"])
        uses = {}
        for b in prj["beats"]:
            for s in b.get("shots", []):
                for f in re.findall(r"FILES?:\s*([^\s(]+)", s["desc"]):
                    uses[f] = uses.get(f, 0) + 1
        return dict(project=prj, media=self.media_list(), assets=docos.ASSETS, transitions=RD.TRANSITIONS,
                    styles=STYLES, check=[list(x) for x in docos.check(prj)], timing=timing, shots=shot_times,
                    total=round(fp["total"], 1), uses=uses, job=self.job)

    # ── miniatury ──
    def shot_thumb(self, bid, n):
        prj = self.load()
        fp = RD.plan_film(prj, self.root, 12)
        idx = next((i for i, sp in enumerate(fp["specs"]) if sp["beat"] == bid and sp["shot"]["wiz"] == n), None)
        if idx is None:
            return None
        sp = fp["specs"][idx]
        key = hashlib.sha1(json.dumps([RD.RENDER_VERSION, sp["shot"], sp["use_idx"],
                                       fp["specs"][idx - 1]["shot"] if idx else None], sort_keys=True).encode()).hexdigest()[:16]
        out = self.thumbs / f"{key}.jpg"
        if not out.exists():
            prev = RD.shot_fn(fp["specs"][idx - 1], idx - 1, self.media(), None) if idx else None
            fn = RD.shot_fn(sp, idx, self.media(), prev)
            d = max(sp["d"], 0.5)
            img = fn(d * 0.6, d).convert("RGB").resize((384, 216), Image.BILINEAR)
            img.save(out, quality=82)
        return out

    def media_thumb(self, name):
        p = self.media().index.get(name)
        if not p:
            return None
        out = self.mthumbs / (hashlib.sha1(str(p).encode()).hexdigest()[:12] + ".jpg")
        if not out.exists():
            if p.suffix.lower() in RD.VIDEO_EXT:
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "2", "-i", str(p), "-frames:v", "1",
                                "-vf", "scale=240:-1", str(out)])
            elif p.suffix.lower() in (".wav", ".mp3"):
                Image.new("RGB", (240, 135), (40, 40, 40)).save(out)
            else:
                im = Image.open(p).convert("RGB")
                im.thumbnail((240, 240))
                im.save(out, quality=80)
        return out

    # ── render ──
    def start_render(self, quality):
        if self.job["running"]:
            return False
        self.job = {"running": True, "log": [f"start: {quality}"], "url": "", "kind": quality, "t0": time.time()}

        def run():
            try:
                name = f"{quality}_{int(time.time())}.mp4"
                RD.render_film(self.project, self.out / name, quality=quality, workers=4,
                               progress=lambda m: self.job["log"].append(m))
                self.job["url"] = f"/out/{name}"
                self.job["log"].append(f"gotowe w {time.time() - self.job['t0']:.0f}s")
            except Exception as e:  # noqa: BLE001
                self.job["log"].append("BŁĄD: " + repr(e))
                self.job["log"].append(traceback.format_exc()[-800:])
            finally:
                self.job["running"] = False
        threading.Thread(target=run, daemon=True).start()
        return True

    def start_voice(self, bid):
        if self.job["running"]:
            return False
        self.job = {"running": True, "log": [f"lektor: {bid}"], "url": "", "kind": "voice", "t0": time.time()}
        cfg = RD.film_config(self.load())

        def run():
            try:
                ref = cfg.get("voice_ref") or str(HERE.parent / "pilot" / "assets" / "ref_clean.wav")
                cmd = [str(HERE.parent / "pilot" / ".venv-tts" / "bin" / "python"), "-I", str(HERE / "voice_beats.py"),
                       str(self.project), ref, str(self.root / cfg["voice"]), "--lang", "en", "--beat", bid]
                env = {"PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_OFFLINE": "1", "TQDM_DISABLE": "1", "PATH": "/opt/homebrew/bin:/usr/bin:/bin"}
                p = subprocess.run(cmd, capture_output=True, text=True, env=env)
                self.job["log"] += [l for l in (p.stdout + p.stderr).splitlines() if l.startswith(("B", "Error", "Trace"))][-6:]
                self.job["log"].append(f"gotowe w {time.time() - self.job['t0']:.0f}s")
            finally:
                self.job["running"] = False
        threading.Thread(target=run, daemon=True).start()
        return True


def make_handler(app: App):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send_json(self, obj, code=200):
            b = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def send_file(self, p: Path, ctype=None):
            if not p or not p.exists():
                self.send_error(404)
                return
            size = p.stat().st_size
            ctype = ctype or mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            rng = self.headers.get("Range")
            start, end = 0, size - 1
            if rng:
                m = re.match(r"bytes=(\d*)-(\d*)", rng)
                if m:
                    start = int(m.group(1) or 0)
                    end = int(m.group(2)) if m.group(2) else size - 1
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            else:
                self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            with open(p, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            try:
                if u.path in ("/", "/index.html"):
                    return self.send_file(HERE / "editor.html", "text/html; charset=utf-8")
                if u.path == "/api/state":
                    return self.send_json(app.state())
                if u.path == "/api/job":
                    return self.send_json(app.job)
                if u.path == "/thumb":
                    return self.send_file(app.shot_thumb(q["beat"][0], int(q["n"][0])), "image/jpeg")
                if u.path.startswith("/mthumb/"):
                    return self.send_file(app.media_thumb(unquote(u.path[8:])), "image/jpeg")
                if u.path.startswith("/media/"):
                    return self.send_file(app.media().index.get(unquote(u.path[7:])))
                if u.path.startswith("/out/"):
                    return self.send_file(app.out / Path(unquote(u.path[5:])).name, "video/mp4")
                self.send_error(404)
            except Exception as e:  # noqa: BLE001
                self.send_json({"error": repr(e), "trace": traceback.format_exc()[-1500:]}, 500)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            try:
                if self.path == "/api/save":
                    app.save(body["project"])
                    return self.send_json(app.state())
                if self.path == "/api/render":
                    return self.send_json({"ok": app.start_render(body.get("quality", "preview"))})
                if self.path == "/api/voice":
                    return self.send_json({"ok": app.start_voice(body["beat"])})
                self.send_error(404)
            except Exception as e:  # noqa: BLE001
                self.send_json({"error": repr(e), "trace": traceback.format_exc()[-1500:]}, 500)
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    app = App(Path(a.project))
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(app))
    print(f"DocOS Editor: http://localhost:{a.port}  ({app.project.name})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
