"""One-time setup and health check: tools, Python packages, fonts, sound effects."""
from __future__ import annotations

import importlib
from functools import lru_cache
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
            "PIL": "Pillow", "yt_dlp": "yt-dlp[default]", "yt_dlp_ejs": "yt-dlp-ejs", "streamlink": "streamlink",
            "ai_edge_litert": "ai-edge-litert"}


def doctor(ws: Workspace) -> dict:
    res = {"python": sys.version.split()[0], "ffmpeg": have("ffmpeg"), "ffprobe": have("ffprobe")}
    for mod in PACKAGES:
        try:
            importlib.import_module(mod)
            res[mod] = True
        except Exception:
            res[mod] = False
    eng = ws.settings().get("caption_engine", "pil")
    res["napisy"] = ("ffmpeg (libass)" if eng == "ass" or (eng == "auto" and ffmpeg_has_ass())
                     else "kod (Pillow)")
    res["fonts"] = all((ws.fonts / f).exists() for f in FONTS)
    from .music import available as music_ok
    res["muzyka"] = "wykrywanie działa (YAMNet)" if music_ok(ws) else "brak — uruchom setup"
    res["deno"] = have("deno")  # yt-dlp needs a JS runtime for YouTube; deno is the one enabled by default
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
        p = subprocess.run([sys.executable, "-m", "pip", "install", "-U", *missing], capture_output=True, text=True)
        out = p.stdout + p.stderr
        if p.returncode != 0:
            if "externally-managed" in out:  # Homebrew Python (PEP 668): needs a venv
                log("Python z Homebrew nie pozwala instalować pakietów globalnie.\n"
                    "Uruchom aplikację przez ./start_clipper.command — sam zrobi środowisko .venv i wszystko zainstaluje.")
            else:
                log(out[-1500:])
    else:
        log("Pakiety Pythona: komplet")


@lru_cache(maxsize=1)
def ffmpeg_has_ass() -> bool:
    """Captions are burned with ffmpeg's libass filter — some ffmpeg builds ship without it."""
    if not have("ffmpeg"):
        return False
    p = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return any(ln.split()[1:2] == ["ass"] for ln in p.stdout.splitlines() if ln.strip())


def ffmpeg_hint() -> str:
    if sys.platform == "darwin":
        return "brew install ffmpeg"
    if sys.platform == "win32":
        return "winget install Gyan.FFmpeg   (potem zamknij i otwórz terminal)"
    return "sudo apt install ffmpeg"


def ffmpeg_ass_hint() -> str:
    return "ffmpeg nie ma filtra napisów (libass) — nic nie szkodzi, napisy rysuje kod (Pillow)."


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
    elif not ffmpeg_has_ass():
        log(ffmpeg_ass_hint())
    if not have("deno"):
        log("Brak deno — bez niego yt-dlp nie pobierze z YouTube. Zainstaluj: "
            + ("brew install deno" if sys.platform == "darwin" else "https://deno.com"))
    if packages:
        install_packages()
    fonts(ws)
    from .music import download_model
    if not download_model(ws):
        log("  nie pobrałem modelu do wykrywania muzyki (YAMNet) — kontrola muzyki będzie pominięta")
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
