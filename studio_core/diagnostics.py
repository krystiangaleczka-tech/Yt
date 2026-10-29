"""Read-only environment diagnostics; no account secrets or sample contents."""
import importlib.metadata
import os
from pathlib import Path
import platform
import shutil
import subprocess


def diagnostics(repo):
    checks=[]
    for name,fix in (("ffmpeg","macOS: brew install ffmpeg · Windows: winget install Gyan.FFmpeg · Linux: apt install ffmpeg"),("ffprobe","Zainstaluj FFmpeg"),("pdftoppm","macOS: brew install poppler · Linux: apt install poppler-utils"),("tesseract","macOS: brew install tesseract tesseract-lang · Linux: apt install tesseract-ocr-pol")):
        path=shutil.which(name)
        checks.append({"id":name,"name":name,"ok":bool(path),"detail":"Dostępny w PATH" if path else fix})
    for name,env,default,modules in (("Obrazy","DOCOS_IMAGE_PYTHON","pilot/.venv/bin/python","torch,diffusers"),("Lektor","DOCOS_TTS_PYTHON","pilot/.venv-tts/bin/python","torch,chatterbox"),("Znaczniki słów","DOCOS_ALIGN_PYTHON",".venv-align/bin/python","faster_whisper")):
        python=Path(os.environ.get(env,repo/(default.replace("bin/python","Scripts/python.exe") if os.name=="nt" else default))); ok=False; detail="Brak środowiska: "+env
        if python.is_file():
            try:
                result=subprocess.run([str(python),"-I","-c","import "+modules],capture_output=True,text=True,timeout=45)
                ok=result.returncode==0; detail="Biblioteki importują się poprawnie. Gotowość wag potwierdza próbne generowanie." if ok else "Środowisko wymaga naprawy zależności; patrz docs/STUDIO.md"
            except subprocess.TimeoutExpired: detail="Przekroczono czas importu bibliotek"
        checks.append({"id":env,"name":name,"ok":ok,"detail":detail})
    cli=shutil.which("claude")
    checks.append({"id":"claude","name":"Claude CLI","ok":bool(cli),"detail":"CLI dostępne; logowanie i limit sprawdź testem połączenia AI" if cli else "Opcjonalne: zainstaluj CLI i wykonaj claude auth login albo skonfiguruj API"})
    return {"system":platform.platform(),"python":platform.python_version(),"checks":checks,"offline":"Pliki, redakcja, montaż i eksport działają bez dostępu do usług. Pierwsze użycie modelu może pobrać wagi."}
