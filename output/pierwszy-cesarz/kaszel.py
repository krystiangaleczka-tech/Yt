"""Próbki prawdziwego kaszlu do efektów (efekty.cough): Chatterbox Turbo czyta sam znacznik [cough] głosem z próbki
lektora, a skrypt wycina z nagrania kaszlnięcia, przycina ciszę, wygasza brzegi i zapisuje 44,1 kHz mono.

Reżyser 16.11.2026: „tam, gdzie cesarz kona, jest dźwięk tłuczenia, a nie kaszlenia” — kaszel z syntezy (szum przez
formanty) brzmiał jak tłuczone naczynie. Nagranie z modelu brzmi jak człowiek.

uruchom (Mac: LEKTOR_DEVICE=mps; najpierw zamknij inne ciężkie procesy — 8 GB RAM):
  pilot/.venv-tts/bin/python -I output/pierwszy-cesarz/kaszel.py nagraj        → build/kaszel_proby/*.raw.wav
  pilot/.venv-tts/bin/python -I output/pierwszy-cesarz/kaszel.py ocen          → lista podejść: długość, kaszlnięcia
  pilot/.venv-tts/bin/python -I output/pierwszy-cesarz/kaszel.py wybierz t0_s123 t0_s42 … → dzwiek_probki/kaszel_1..N.wav
Kolejne kaszlnięcia w filmie biorą kolejne próbki (efekty.cough), więc kolejność w „wybierz” to kolejność w filmie.
16.11.2026: t0_s123 t0_s42 t1_s5 t2_s42 t1_s42 t1_s7 t2_s7 t0_s5 — trucizna, młot, podróż ×3, koniec ×2 (krótsze, bo
kaszlnięcia są blisko siebie), list. Pliki .wav nie idą do repo (jak lektor) — paczka dźwięku na PC jest z Maca.
"""
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROBY = HERE / "build" / "kaszel_proby"
CEL = HERE / "dzwiek_probki"
PROMPT = Path(os.environ.get("PROMPT") or REPO / "pilot/assets/ref_en_teatr_nizej_0.25pt.wav")
TEKSTY = ["[cough] [cough]", "[cough] [cough] [cough]", "[cough]... [cough] [cough]"]
ZIARNA = [7, 42, 123, 5]
SR = 44100


def _turbo(device):
    import glob
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    sciezka = os.environ.get("TURBO") or sorted(glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--ResembleAI--chatterbox-turbo/snapshots/*")))[-1]
    return ChatterboxTurboTTS.from_local(sciezka, device)


def nagraj():
    import random

    import soundfile as sf
    import torch
    device = os.environ.get("LEKTOR_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
    orig = torch.load
    torch.load = lambda *a, **kw: orig(*a, **{**kw, "map_location": torch.device(device)})
    PROBY.mkdir(parents=True, exist_ok=True)
    m = _turbo(device)
    for n, txt in enumerate(TEKSTY):
        for z in ZIARNA:
            out = PROBY / f"t{n}_s{z}.raw.wav"
            if out.exists():
                continue
            torch.manual_seed(z), random.seed(z), np.random.seed(z)
            wav = m.generate(txt, audio_prompt_path=str(PROMPT), temperature=0.8).detach().cpu().numpy().squeeze()
            sf.write(out, wav.astype(np.float32), m.sr)
            print(f"{out.name}: {len(wav) / m.sr:.2f} s", flush=True)


def _wczytaj(p):
    import soundfile as sf
    from scipy.signal import resample_poly
    x, sr = sf.read(str(p), dtype="float64")
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = resample_poly(x, SR // g, sr // g)
    return x


def _obwiednia(x, krok=0.01):
    h = int(SR * krok)
    return np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9) for i in range(0, len(x) - h, h)])


def wytnij(x):
    """Od pierwszego do ostatniego dźwięku powyżej −40 dB względem szczytu, z zapasem 0,05 s i łagodnymi brzegami."""
    e = _obwiednia(x)
    glosne = np.where(e > e.max() - 40)[0]
    if not len(glosne):
        return x
    a = max(0, int((glosne[0] * 0.01 - 0.05) * SR))
    b = min(len(x), int((glosne[-1] * 0.01 + 0.12) * SR))
    y = x[a:b].copy()
    f1, f2 = int(0.01 * SR), int(0.08 * SR)
    y[:f1] *= np.linspace(0, 1, f1)
    y[-f2:] *= np.linspace(1, 0, f2)
    return y / (np.abs(y).max() + 1e-9) * 0.9


def kaszlniecia(y):
    """Ile osobnych wybuchów (kaszlnięć): odcinki powyżej −18 dB od szczytu przedzielone ciszą ≥ 60 ms."""
    e = _obwiednia(y)
    glos = e > e.max() - 18
    n, cisza, w = 0, 99, False
    for g in glos:
        if g and not w and cisza >= 6:
            n += 1
        w = g if g else (w and cisza < 6)
        cisza = 0 if g else cisza + 1
    return n


def ocen():
    for p in sorted(PROBY.glob("*.raw.wav")):
        y = wytnij(_wczytaj(p))
        e = _obwiednia(y)
        dzwieczne = float(np.mean(e > e.max() - 18))  # udział głośnych ramek: mowa ciągnie się, kaszel to krótkie wybuchy
        print(f"{p.name:22s} {len(y) / SR:5.2f} s  kaszlnięć {kaszlniecia(y)}  głośne ramki {dzwieczne:.0%}")


def wybierz(nazwy):
    import soundfile as sf
    CEL.mkdir(exist_ok=True)
    for f in CEL.glob("kaszel_*.wav"):
        f.unlink()
    for n, nazwa in enumerate(nazwy, 1):
        y = wytnij(_wczytaj(PROBY / f"{nazwa}.raw.wav"))
        sf.write(CEL / f"kaszel_{n}.wav", y, SR, subtype="PCM_16")
        print(f"kaszel_{n}.wav ← {nazwa} ({len(y) / SR:.2f} s)")


if __name__ == "__main__":
    a = sys.argv[1:] or ["ocen"]
    {"nagraj": lambda: nagraj(), "ocen": lambda: ocen(), "wybierz": lambda: wybierz(a[1:])}[a[0]]()
