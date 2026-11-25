"""One-time setup and health check: tools, Python packages, fonts, sound effects."""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
import urllib.request

from .config import APP_DIR, Workspace
from .util import have, log, run

FONT_CDN = "https://cdn.jsdelivr.net/gh/google/fonts@main/"
FONTS = {
    "Poppins-Black.ttf": "ofl/poppins/Poppins-Black.ttf",
    "Anton-Regular.ttf": "ofl/anton/Anton-Regular.ttf",
    "Bangers-Regular.ttf": "ofl/bangers/Bangers-Regular.ttf",
    "LuckiestGuy-Regular.ttf": "apache/luckiestguy/LuckiestGuy-Regular.ttf",
    "BebasNeue-Regular.ttf": "ofl/bebasneue/BebasNeue-Regular.ttf",
}
PACKAGES = {"faster_whisper": "faster-whisper", "cv2": "opencv-python-headless<5", "numpy": "numpy",
            "PIL": "Pillow", "yt_dlp": "yt-dlp", "streamlink": "streamlink"}


def doctor(ws: Workspace) -> dict:
    res = {"python": sys.version.split()[0], "ffmpeg": have("ffmpeg"), "ffprobe": have("ffprobe")}
    for mod in PACKAGES:
        try:
            importlib.import_module(mod)
            res[mod] = True
        except Exception:
            res[mod] = False
    res["fonts"] = all((ws.fonts / f).exists() for f in FONTS)
    res["deno"] = have("deno") or have("node")
    s = ws.settings()
    from . import ai
    res["ai"] = f"{s['ai']}: {'jest' if ai.available(s) else 'brak na tym PC'}"
    res["workspace"] = str(ws.root)
    return res


def install_packages() -> None:
    missing = []
    for mod, pkg in PACKAGES.items():
        try:
            importlib.import_module(mod)
        except Exception:
            missing.append(pkg)
    if missing:
        log(f"Instaluję: {', '.join(missing)}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", *missing], check=False)
    else:
        log("Pakiety Pythona: komplet")


def ffmpeg_hint() -> str:
    if sys.platform == "win32":
        return "winget install Gyan.FFmpeg   (potem zamknij i otwórz terminal)"
    if sys.platform == "darwin":
        return "brew install ffmpeg"
    return "sudo apt install ffmpeg"


def fonts(ws: Workspace) -> None:
    ws.fonts.mkdir(parents=True, exist_ok=True)
    bundled = APP_DIR / "fonts"
    for name, path in FONTS.items():
        dst = ws.fonts / name
        if dst.exists():
            continue
        if (bundled / name).exists():
            shutil.copy(bundled / name, dst)
            continue
        try:
            urllib.request.urlretrieve(FONT_CDN + path, dst)
            log(f"  czcionka {name}")
        except Exception as e:
            log(f"  nie pobrałem {name}: {e}")


def sounds(ws: Workspace) -> None:
    """Small original sound effects, synthesised with ffmpeg (no copyrighted memes)."""
    ws.sounds.mkdir(parents=True, exist_ok=True)
    recipes = {
        "whoosh.wav": "anoisesrc=d=0.45:c=pink:a=0.6,highpass=f=400,lowpass=f=4000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2",
        "boom.wav": "sine=f=55:d=0.7,volume=2.5,afade=t=out:st=0.1:d=0.6",
        "ding.wav": "sine=f=1320:d=0.5,afade=t=out:st=0.05:d=0.45",
        "riser.wav": "sine=f=200:d=1.2,vibrato=f=12:d=0.3,afade=t=in:d=1.0,afade=t=out:st=1.0:d=0.2",
    }
    for name, f in recipes.items():
        dst = ws.sounds / name
        if not dst.exists():
            run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f, "-ar", "48000", "-ac", "2", dst], check=False)


def setup(ws: Workspace, packages: bool = True) -> dict:
    ws.ensure()
    if not have("ffmpeg"):
        log(f"Brak ffmpeg. Zainstaluj: {ffmpeg_hint()}")
    if packages:
        install_packages()
    fonts(ws)
    if have("ffmpeg"):
        sounds(ws)
    for name in ("channels.txt",):
        src = APP_DIR / name
        if src.exists() and not (ws.root / name).exists():
            shutil.copy(src, ws.root / name)
    if not ws.path("streamers.json").exists():
        ws.save_streamers([])
    if packages:
        try:  # warm up the speech model once (downloads ~0.5 GB the first time)
            from .transcribe import _model
            s = ws.settings()
            log(f"Pobieram model mowy Whisper '{s['whisper_model']}' (tylko raz)…")
            _model(s["whisper_model"], s["whisper_device"])
        except Exception as e:
            log(f"  Whisper: {e}")
    d = doctor(ws)
    for k, v in d.items():
        log(f"  {k:<15} {v}")
    return d
