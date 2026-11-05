"""Gotowy lektor bez „zamulenia”: resemble-enhance odbudowuje pasmo powyżej ~8 kHz, którego Chatterbox nie generuje.

Oryginały idą do <katalog>-raw/, długość zdań się nie zmienia, więc ujęcia w render*.py pasują dalej.
uruchom: ../../pilot/.venv-enhance/bin/python studio_lines.py voice voice/en
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import torch
import torchaudio
from huggingface_hub import snapshot_download
from resemble_enhance.enhancer.inference import enhance

RUN_DIR = Path(snapshot_download("ResembleAI/resemble-enhance", allow_patterns=["enhancer_stage2/*"])) / "enhancer_stage2"
# po rekonstrukcji: lekka kompresja, „powietrze” w górze i ta sama głośność co wcześniej
POST = ("acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80:makeup=1.5,"
        "equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=1.5,"
        "highshelf=f=9000:g=2,loudnorm=I=-16:TP=-2,"
        "agate=threshold=0.012:ratio=4:attack=3:release=150")   # cisza między słowami bez szumu rekonstrukcji
device = "cuda" if torch.cuda.is_available() else "cpu"

for d in map(Path, sys.argv[1:]):
    raw = d.parent / f"{d.name}-raw" if d.name != "en" else d.parent.parent / "voice-raw" / "en"
    raw.mkdir(parents=True, exist_ok=True)
    for f in sorted(d.glob("*.wav")):
        src = raw / f.name
        if not src.exists():          # ponowne uruchomienie zawsze startuje z oryginału
            shutil.copy2(f, src)
        wav, sr = torchaudio.load(str(src))
        # lambd niska: próbka jest już czysta, chodzi o pasmo, nie o odszumianie
        out, out_sr = enhance(wav.mean(0), sr, device, nfe=32, solver="midpoint", lambd=0.1, tau=0.5,
                              run_dir=RUN_DIR)
        tmp = Path(tempfile.mkdtemp()) / "e.wav"
        torchaudio.save(str(tmp), out.cpu().unsqueeze(0), out_sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af", POST,
                        "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(f)], check=True)
        print(f"{f}  {wav.shape[-1] / sr:.2f} s", flush=True)
