"""Kontrola urwanych słów w lektorze (Podręcznik → Lektor, zasada 9), zanim lektor pójdzie do odsłuchu albo do Studio.

Sprawdza każdą kwestię katalogu lektora (<klucz>.wav + <klucz>.json, jak z lektor_studio.py podejscia):
  1. model: wybrane podejście po obróbce (podejscia/<klucz>_s<z>.wav) kończy się głosem, a nie ciszą — Chatterbox
     urwał ostatnie słowo; obróbka tego nie naprawi, kwestię nagrywa się od nowa innym ziarnem (sam koniec surowego
     pliku nie wystarcza: bywa tam cichy oddech albo trzask po ciszy, które obróbka i tak usuwa);
  2. odbudowa pasma: w gotowym podejściu słowo spada z głosu do ciszy w 10 ms, a przed resemble-enhance (ten sam
     łańcuch FX, ta sama oś czasu) jeszcze wybrzmiewało — enhance wyciął ogon jak szum; też nowe ziarno;
  3. kwestia: cisza przed pierwszym i po ostatnim słowie, nagły spadek z głosu w ciszę w środku (pauzy, cięcia).
Kwestie autora (json z „zrodlo”: autor…) — tylko punkt 3.

uruchom:  pilot/.venv-enhance/bin/python -I docos/uciecia_lektora.py <katalog lektora> [klucz …]
Kod wyjścia 1, gdy coś znalazł (lista: kwestia, co, gdzie).
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I nie dokłada katalogu skryptu
import lektor_studio  # noqa: E402

KROK = 0.005          # ramka 5 ms
GLOS, CISZA = -38.0, -70.0   # spadek z głosu (> -38 dBFS) do ciszy (< -70) w 10 ms = ucięcie
KONIEC_MODELU = -45.0  # podejście po obróbce kończy się (ostatnie 15 ms) głośniej niż to = model urwał słowo
BRZEG = -60.0          # pierwsza / ostatnia ramka kwestii głośniej niż to = kwestia zaczyna się albo kończy cięciem


def ramki(path):
    y, sr = sf.read(str(path), dtype="float32")
    if y.ndim > 1:
        y = y.mean(1)
    h = int(sr * KROK)
    return np.array([10 * np.log10(np.mean(y[i:i + h] ** 2) + 1e-12) for i in range(0, len(y) - h + 1, h)])


def model_urwal(podejscie):
    d = ramki(podejscie)
    return float(d[-3:].max()) if d[-3:].max() > KONIEC_MODELU else None


def enhance_wycial(raw, gotowe):
    """Miejsca (s), w których gotowe podejście spada z głosu do ciszy, a wersja przed odbudową pasma jeszcze brzmi."""
    fx = Path(tempfile.mkdtemp()) / "fx.wav"
    lektor_studio._ffmpeg(raw, fx, lektor_studio.FX)
    a, b = ramki(fx), ramki(gotowe)
    n = min(len(a), len(b))
    return [round(i * KROK, 2) for i in range(1, n - 3)
            if b[i] > -35 and b[i] - b[i + 2] >= 30 and a[i + 2] - b[i + 2] >= 20 and a[i + 2] > -60]


def kwestia(path):
    d = ramki(path)
    zle = []
    if d[0] > BRZEG:
        zle.append(f"początek ucięty (pierwsza ramka {d[0]:.0f} dB)")
    if d[-1] > BRZEG:
        zle.append(f"koniec ucięty (ostatnia ramka {d[-1]:.0f} dB)")
    for i in range(1, len(d) - 2):
        if d[i] > GLOS and min(d[i + 1], d[i + 2]) < CISZA:
            zle.append(f"słowo ucięte w {i * KROK:.2f} s ({d[i]:.0f} → {min(d[i + 1], d[i + 2]):.0f} dB w 10 ms)")
    return zle


def sprawdz(katalog, klucze=()):
    katalog = Path(katalog)
    wynik = {}
    for meta_path in sorted(katalog.glob("*.json")):
        klucz = meta_path.stem
        wav = katalog / f"{klucz}.wav"
        if (klucze and klucz not in klucze) or not wav.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        zle = kwestia(wav)
        z = meta.get("podejscie")
        raw = katalog / "podejscia" / f"{klucz}_s{z}.raw.wav"
        gotowe = katalog / "podejscia" / f"{klucz}_s{z}.wav"
        if "autor" not in meta.get("zrodlo", "") and raw.exists():
            if (v := model_urwal(gotowe if gotowe.exists() else raw)) is not None:
                zle.insert(0, f"model urwał ostatnie słowo (podejście {z} kończy się przy {v:.0f} dB) — nowe ziarno")
            if gotowe.exists() and (m := enhance_wycial(raw, gotowe)):
                zle.insert(0, f"odbudowa pasma wycięła wybrzmienie w {m} s (podejście {z}) — nowe ziarno")
        if zle:
            wynik[klucz] = zle
    return wynik


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    w = sprawdz(sys.argv[1], set(sys.argv[2:]))
    for k, zle in w.items():
        for z in zle:
            print(f"{k:14s} {z}")
    print(f"-- z problemem: {len(w)} kwestii" if w else "-- bez urwanych słów")
    sys.exit(1 if w else 0)
