"""Teatr papierowy na żywo w Studio: ujęcia rysowane kodem (output/<film>/na_zywo.py) zamiast klipów mp4.

Ujęcie ma w `legacy.teatr` {"film": "pierwszy-cesarz", "jezyk": "en", "odn": "d01_06"}. Studio uruchamia wtedy w tle
serwer teatru tego filmu (jeden na film i język) i przekazuje przeglądarce ruch ujęcia (JSON) i wycinki (PNG); rysuje
je karta graficzna (apps/studio/src/teatr.ts). Klipy mp4 zostają na osi jako zapas i do renderu końcowego.
"""
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastapi.responses import FileResponse, JSONResponse, Response

REPO = Path(__file__).resolve().parents[1]
_SERWERY = {}  # (film, język) → (proces, port)
_LOCK = threading.Lock()


def _film(project):
    for s in project.scenes:
        t = (s.legacy or {}).get("teatr")
        if isinstance(t, dict) and re.fullmatch(r"[a-z0-9-]+", str(t.get("film", ""))) and \
                re.fullmatch(r"[a-z]{2}", str(t.get("jezyk", ""))):
            return t["film"], t["jezyk"]
    return None


def _wolny_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port, path, timeout=60.0):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "application/octet-stream")


def _serwer(root, film, jezyk):
    """Port działającego serwera teatru; uruchamia go, jeśli nie działa."""
    skrypt = REPO / "output" / film / "na_zywo.py"
    if not skrypt.exists():
        raise ValueError(f"Film {film} nie ma podglądu na żywo ({skrypt.relative_to(REPO)})")
    with _LOCK:
        proc, port = _SERWERY.get((film, jezyk), (None, None))
        if proc and proc.poll() is None:
            return port
        port = _wolny_port()
        logi = Path(root) / "logs"
        logi.mkdir(parents=True, exist_ok=True)
        log = open(logi / f"teatr-{film}-{jezyk}.log", "ab")
        proc = subprocess.Popen([sys.executable, "-I", str(skrypt), "--port", str(port), "--rodzic", str(os.getpid())],
                                cwd=REPO, env={**os.environ, "JEZYK": jezyk, "PYTHONUNBUFFERED": "1"}, stdout=log,
                                stderr=subprocess.STDOUT)
        _SERWERY[(film, jezyk)] = (proc, port)
    for _ in range(150):  # import silnika trwa ułamek sekundy, ale pierwsze uruchomienie bywa wolniejsze
        try:
            _get(port, "/wersja", 1.0)
            return port
        except (urllib.error.URLError, ConnectionError, OSError):
            if proc.poll() is not None:
                raise RuntimeError(f"Serwer teatru {film} ({jezyk}) nie wystartował — log: logs/teatr-{film}-{jezyk}.log")
            time.sleep(0.2)
    raise TimeoutError("Serwer teatru nie odpowiada")


def register_teatr(app, store, root):
    def port_dla(pid):
        film = _film(store.get(pid))
        if not film:
            return None, None
        return film, _serwer(root, *film)

    @app.get("/api/projects/{pid}/teatr/stan")
    def teatr_stan(pid: str):
        film, port = port_dla(pid)
        if not port:
            return {"dostepny": False}
        body, _ = _get(port, "/wersja", 10.0)
        return {"dostepny": True, "film": film[0], "jezyk": film[1], **json.loads(body)}

    @app.get("/api/projects/{pid}/teatr/ujecie/{odn}")
    def teatr_ujecie(pid: str, odn: str):
        if not re.fullmatch(r"d\d\d_\d\d", odn):
            return JSONResponse({"detail": "Złe ujęcie"}, 400)
        film, port = port_dla(pid)
        if not port:
            return JSONResponse({"detail": "Ten projekt nie ma podglądu na żywo"}, 404)
        try:
            body, typ = _get(port, f"/ujecie/{odn}.json", 120.0)
        except urllib.error.HTTPError as e:
            return Response(e.read(), e.code, media_type="text/plain; charset=utf-8")
        return Response(body, media_type=typ, headers={"Cache-Control": "no-store"})

    @app.get("/api/projects/{pid}/teatr/wycinki/{plik}")
    def teatr_wycinek(pid: str, plik: str):
        if not re.fullmatch(r"[0-9a-f]{16}\.png", plik):
            return JSONResponse({"detail": "Zły plik"}, 400)
        film = _film(store.get(pid))
        path = REPO / "output" / film[0] / "build" / f"na_zywo_{film[1]}" / "wycinki" / plik if film else None
        if not path or not path.exists():
            return JSONResponse({"detail": "Nie ma takiego wycinka"}, 404)
        return FileResponse(path, media_type="image/png", headers={"Cache-Control": "max-age=31536000, immutable"})
