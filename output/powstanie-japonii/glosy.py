"""Głos człowieka do efektów „Syna słońca” (wytyczne 1.14): śmiech bogów przy tańcu Uzume, jęk konających (Izanami,
Itsuse, Nagasunehiko, trafiony strzałą Itsuse) — z nagrania, nie z syntezy szumu. Chatterbox Turbo czyta sam znacznik
([laugh], [groan]) głosem z próbki lektora EN, skrypt przycina ciszę i zapisuje 44,1 kHz mono. Wzór: „Pierwszy cesarz”
kaszel.py (reżyser 16.11: kaszel z syntezy brzmiał „jak tłuczenie”).

uruchom (Mac: jeden ciężki proces naraz — po nagraniu lektora):
  LEKTOR_DEVICE=cpu PROMPT=<YT>/pilot/assets/ref_en_teatr_nizej_0.25pt.wav \
      <YT>/pilot/.venv-tts/bin/python -I output/powstanie-japonii/glosy.py nagraj   → build/glosy_proby/*.raw.wav
  python3 output/powstanie-japonii/glosy.py ocen                                     → długości podejść
  python3 output/powstanie-japonii/glosy.py wybierz smiech_t0_s7 jek_t1_s42 …        → dzwiek_probki/<rodzaj>_1..N.wav
Kolejne użycia w filmie biorą kolejne próbki danego rodzaju (efekty.glos). Pliki .wav nie idą do repo (głos autora).
Nowy rodzaj dźwięku: reżyser najpierw słyszy próbkę (fragment filmu + sam dźwięk), dopiero potem idzie do filmu.
"""
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROBY = HERE / "build" / "glosy_proby"
CEL = HERE / "dzwiek_probki"
PROMPT = Path(os.environ.get("PROMPT") or REPO / "pilot/assets/ref_en_teatr_nizej_0.25pt.wav")
TEKSTY = {"smiech": ["[laugh]", "[laugh] [laugh]", "Ha ha ha! [laugh]"],
          "jek": ["[groan]", "[gasp] [groan]"]}
ZIARNA = [7, 42, 123]
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
    for rodzaj, teksty in TEKSTY.items():
      for n, txt in enumerate(teksty):
        for z in ZIARNA:
            out = PROBY / f"{rodzaj}_t{n}_s{z}.raw.wav"
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


def ocen():
    for p in sorted(PROBY.glob("*.raw.wav")):
        y = wytnij(_wczytaj(p))
        print(f"{p.name:28s} {len(y) / SR:5.2f} s")


def wybierz(nazwy):
    import soundfile as sf
    CEL.mkdir(exist_ok=True)
    licz = {}
    for nazwa in nazwy:
        rodzaj = nazwa.split("_t")[0]
        if rodzaj not in licz:
            for f in CEL.glob(f"{rodzaj}_*.wav"):
                f.unlink()
        licz[rodzaj] = licz.get(rodzaj, 0) + 1
        y = wytnij(_wczytaj(PROBY / f"{nazwa}.raw.wav"))
        sf.write(CEL / f"{rodzaj}_{licz[rodzaj]}.wav", y, SR, subtype="PCM_16")
        print(f"{rodzaj}_{licz[rodzaj]}.wav ← {nazwa} ({len(y) / SR:.2f} s)")


if __name__ == "__main__":
    a = sys.argv[1:] or ["ocen"]
    {"nagraj": lambda: nagraj(), "ocen": lambda: ocen(), "wybierz": lambda: wybierz(a[1:])}[a[0]]()
