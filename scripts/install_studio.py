"""Install and optionally start Studio without touching existing model environments."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def main():
    parser = argparse.ArgumentParser(description="Instalacja DocOS Studio")
    parser.add_argument("--run", action="store_true", help="uruchom aplikację po instalacji")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if sys.version_info < (3, 11):
        raise SystemExit("Wymagany Python 3.11 lub nowszy; zalecany 3.12.")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise SystemExit("Zainstaluj Node.js 22 LTS (co najmniej 22.12) i ponów instalację.")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("Zainstaluj FFmpeg i dodaj do PATH. macOS: brew install ffmpeg; Windows: winget install Gyan.FFmpeg; Linux: sudo apt install ffmpeg.")
    env = root / ".venv-studio"
    python = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        print("Przygotowuję środowisko Studio…", flush=True)
        venv.EnvBuilder(with_pip=True).create(env)
    for command in ([str(python), "-m", "pip", "install", "-r", "requirements-studio.lock"],
                    [npm, "--prefix", "apps/studio", "ci"], [npm, "--prefix", "apps/studio", "run", "build"]):
        subprocess.run(command, cwd=root, check=True)
    print("Studio gotowe. Adres: http://127.0.0.1:8876", flush=True)
    if args.run:
        subprocess.run([str(python), "-m", "studio_api"], cwd=root, check=True)
    else:
        print("Uruchom: .venv-studio/bin/python -m studio_api (Windows: .venv-studio\\Scripts\\python -m studio_api)")


if __name__ == "__main__":
    main()
