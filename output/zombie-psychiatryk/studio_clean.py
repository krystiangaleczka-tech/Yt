"""Próbka głosu „jak ze studia”: resemble-enhance zdejmuje szum i pogłos pokoju.

Chatterbox kopiuje akustykę referencji, więc pogłos w próbce = pogłos w lektorze.
uruchom: ../../pilot/.venv-enhance/bin/python studio_clean.py probka.m4a probka-studio.wav
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
import torchaudio
from huggingface_hub import snapshot_download
from resemble_enhance.enhancer.inference import enhance

# wagi przez huggingface_hub zamiast git-lfs, którego pakiet wymaga
RUN_DIR = Path(snapshot_download("ResembleAI/resemble-enhance", allow_patterns=["enhancer_stage2/*"])) / "enhancer_stage2"

src, dst = sys.argv[1], Path(sys.argv[2])
tmp = Path(tempfile.mkdtemp()) / "in.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "44100", str(tmp)], check=True)
wav, sr = torchaudio.load(str(tmp))
device = "cuda" if torch.cuda.is_available() else "cpu"
# lambd: siła odszumiania przed rekonstrukcją, tau: temperatura — niska = mniej „wymyślonych” detali
# kawałki po 8 s — cała próbka naraz nie mieści się w 8 GB RAM
mono, parts = wav.mean(0), []
for i in range(0, len(mono), 8 * sr):
    out, out_sr = enhance(mono[i:i + 8 * sr], sr, device, nfe=32, solver="midpoint", lambd=0.9, tau=0.5,
                          run_dir=RUN_DIR)
    parts.append(out.cpu())
    print(f"kawałek {i // (8 * sr) + 1}/{-(-len(mono) // (8 * sr))}", flush=True)
torchaudio.save(str(dst), torch.cat(parts).unsqueeze(0), out_sr)


def tail_ratio(path):
    """Ile energii zostaje 60–250 ms po końcu słów względem samej mowy (dB) — mniej = suchszy pokój."""
    y, r = torchaudio.load(str(path))
    y = y.mean(0).numpy()
    hop = int(r * 0.01)
    e = np.array([np.mean(y[i:i + hop] ** 2) + 1e-12 for i in range(0, len(y) - hop, hop)])
    db = 10 * np.log10(e)
    speech = db > db.max() - 25
    tails = []
    for i in range(1, len(speech) - 25):
        if speech[i - 1] and not speech[i]:
            tails.append(db[i + 6:i + 25].mean() - db[max(0, i - 20):i].mean())
    return float(np.median(tails)) if tails else float("nan")


print(f"zanik po słowach: przed {tail_ratio(tmp):.1f} dB, po {tail_ratio(dst):.1f} dB → {dst}")
