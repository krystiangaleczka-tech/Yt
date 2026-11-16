"""Czyszczenie nagrania autora po obróbce studyjnej (lektor_studio.obrob): miękka bramka w pauzach (czysta cisza
między zdaniami) i wycięcie wskazanych śmieci w ciszy („brrr”, szelest). Ramka 220 próbek — czas liczony z hop/sr.

uruchom:  pilot/.venv-enhance/bin/python -I output/pierwszy-cesarz/czysc_nagranie.py <wejście.wav> <wyjście.wav> [od-do …]
"""
import sys

import numpy as np
import soundfile as sf


def czysc(src, dst, smieci):
    y, sr = sf.read(src, dtype="float32")
    hop = int(sr * 0.005)
    dt = hop / sr
    db = np.array([10 * np.log10(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y), hop)])
    st, cich, g = False, 0, np.zeros(len(db), np.float32)
    for i, v in enumerate(db):  # bramka z histerezą: otwiera > -40 dB, zamyka po 150 ms < -50 dB
        if v > -40:
            st, cich = True, 0
        elif st:
            cich = cich + 1 if v < -50 else 0
            if cich * dt >= 0.15:
                st = False
        g[i] = st
    g2 = g.copy()
    pre, post = round(0.04 / dt), round(0.10 / dt)
    for i in np.where(np.diff(g) > 0)[0]:
        g2[max(0, i - pre):i + 1] = 1
    for i in np.where(np.diff(g) < 0)[0]:
        g2[i:i + post] = 1
    for a, b in smieci:
        g2[int(a / dt):int(b / dt)] = 0
    k = round(0.02 / dt)
    gs = np.convolve(g2, np.ones(k) / k, mode="same")
    env = np.maximum(np.repeat(gs, hop)[:len(y)], 10 ** (-90 / 20))
    sf.write(dst, y * env, sr, subtype="PCM_16")


if __name__ == "__main__":
    czysc(sys.argv[1], sys.argv[2], [tuple(map(float, x.split("-"))) for x in sys.argv[3:]])
