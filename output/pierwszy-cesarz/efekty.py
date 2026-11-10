"""Dźwięk filmu „Pierwszy cesarz” bez lektora: muzyka (ścieżka Muzyka) i efekty (ścieżka Efekty), synteza w numpy.

- Muzyka: szarpane struny w skali pentatonicznej (Karplus-Strong, brzmienie zbliżone do guzhengu) na burdonie;
  nastrój aktu (spokojny, wojenny z bębnami, nocny) z AKT_NASTROJ; pod kwestiami lektora ściszona o 9 dB.
- Efekty: tło miejsca (wiatr, sala, morze, noc ze świerszczami), papier i drewno teatru przy każdej zmianie dekoracji
  (ujęcia z render.BUDUJ), wydarzenia ujęć z ZDARZENIA (czasy od początku ujęcia — te same co w funkcjach ujęć).

uruchom:  python3 efekty.py            → dzwiek/muzyka.wav, dzwiek/efekty.wav (cały film, 44,1 kHz mono)
"""
import math
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
from dane import okno_kwestii, ujecia  # noqa: E402

SR = 44100
OUT = HERE / "dzwiek"
RNG = np.random.default_rng(7)


def N(sec):
    return max(1, int(round(sec * SR)))


def tt(n):
    return np.arange(n) / SR


def band(x, lo, hi):
    """Filtr pasmowy przez FFT (wystarcza dla krótkich dźwięków i tła liczonego kawałkami)."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X = np.fft.rfft(x)
    X *= np.clip((f - lo * 0.7) / (lo * 0.3 + 1), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3 + 1), 0, 1)
    return np.fft.irfft(X, n)


def env(n, a=0.005, d=0.3):
    t = tt(n)
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


# ---------- dźwięki ----------

def gong(sec=4.0, f0=110):
    n, t = N(sec), tt(N(sec))
    out = sum(a * np.sin(2 * math.pi * f0 * r * t + 3 * np.sin(2 * math.pi * 0.7 * t) * (r > 2)) * np.exp(-t / d)
              for r, a, d in ((1, 1, 2.5), (2.32, 0.6, 1.8), (2.98, 0.5, 1.4), (4.1, 0.3, 0.9), (5.4, 0.2, 0.6)))
    return out * np.minimum(1, t / 0.01) * 0.5


def whoosh(sec=0.5, lo=400, hi=3000):
    n = N(sec)
    x = band(RNG.normal(0, 1, n), lo, hi)
    e = np.sin(np.linspace(0, math.pi, n)) ** 2
    return x / (np.abs(x).max() + 1e-9) * e * 0.35


def knock(f=260, sec=0.25):
    n, t = N(sec), tt(N(sec))
    return (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.05) + band(RNG.normal(0, 1, n), 1500, 5000) * np.exp(-t / 0.008) * 0.4) * 0.5


def drum(sec=0.9, f=70):
    n, t = N(sec), tt(N(sec))
    ph = 2 * math.pi * np.cumsum(f * (1 + 1.2 * np.exp(-t / 0.04))) / SR
    return (np.sin(ph) * np.exp(-t / 0.35) + band(RNG.normal(0, 1, n), 80, 600) * np.exp(-t / 0.05) * 0.5) * 0.8


def crack(sec=0.35):
    n, t = N(sec), tt(N(sec))
    return band(RNG.normal(0, 1, n), 300, 6000) * np.exp(-t / 0.04) * 0.7 + knock(140, sec) * 0.6


def clash(sec=0.8):
    n, t = N(sec), tt(N(sec))
    return sum(np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, d in ((1870, 0.3), (2630, 0.22), (3410, 0.15), (4950, 0.1))) * 0.18 \
        + band(RNG.normal(0, 1, n), 2000, 9000) * np.exp(-t / 0.02) * 0.4


def coin(sec=0.9):
    n, t = N(sec), tt(N(sec))
    return sum(np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, d in ((2340, 0.4), (3790, 0.25), (5120, 0.15))) * 0.15


def thud(sec=0.6):
    n, t = N(sec), tt(N(sec))
    return (np.sin(2 * math.pi * 55 * t) * np.exp(-t / 0.15) + band(RNG.normal(0, 1, n), 60, 400) * np.exp(-t / 0.08) * 0.6) * 0.9


def fire(sec):
    n = N(sec)
    x = band(RNG.normal(0, 1, n), 200, 2500) * 0.12
    clicks = np.zeros(n)
    for i in RNG.integers(0, n, int(sec * 25)):
        L = min(n - i, N(0.01))
        clicks[i:i + L] += RNG.uniform(0.2, 0.8) * np.exp(-tt(L) / 0.002) * RNG.choice((-1, 1))
    return (x + band(clicks, 800, 8000) * 0.6) * np.minimum(1, tt(n) / 0.3) * np.minimum(1, (sec - tt(n)) / 0.4)


def hooves(sec, rate=6.0):
    n = N(sec)
    out = np.zeros(n)
    k = 0.0
    while k < sec - 0.2:
        for dt in (0, 0.07, 0.15):
            i = N(k + dt)
            s = knock(RNG.uniform(180, 240), 0.15) * RNG.uniform(0.5, 0.9)
            out[i:i + len(s)] += s[:n - i]
        k += 1 / rate * 3
    return out * 0.6


def marching(sec):
    n = N(sec)
    out = np.zeros(n)
    k = 0.0
    while k < sec - 0.3:
        s = thud(0.3) * 0.25 + band(RNG.normal(0, 1, N(0.3)), 300, 3000) * env(N(0.3), 0.002, 0.04) * 0.25
        i = N(k)
        out[i:i + len(s)] += s[:n - i]
        k += 0.42
    return out + 0.15 * clash(sec)[:n] * 0  # bez metalu: sam krok


def splash(sec=1.2):
    n = N(sec)
    return band(RNG.normal(0, 1, n), 300, 5000) * env(n, 0.02, 0.35) * 0.5


def sword(sec=0.4):
    return whoosh(sec, 1500, 8000) * 1.3


SFX = {"gong": gong, "whoosh": whoosh, "knock": knock, "drum": drum, "crack": crack, "clash": clash, "coin": coin,
       "thud": thud, "splash": splash, "sword": sword, "gong_s": lambda: gong(2.5, 220) * 0.6}


# ---------- tło miejsca ----------

def ambient(kind, sec, seed):
    n = N(sec)
    r = np.random.default_rng(seed)
    slow = np.interp(tt(n), np.linspace(0, sec, max(2, int(sec * 0.5) + 2)), r.uniform(0.4, 1.0, max(2, int(sec * 0.5) + 2)))
    if kind == "wiatr":
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.05
    elif kind == "sala":
        x = band(r.normal(0, 1, n), 60, 300) * 0.03 + np.sin(2 * math.pi * 50 * tt(n)) * 0.002
    elif kind == "morze":
        sw = 0.5 + 0.5 * np.sin(2 * math.pi * tt(n) / 6.5) ** 2
        x = band(r.normal(0, 1, n), 100, 2500) * sw * 0.09
    else:  # noc: świerszcze
        x = band(r.normal(0, 1, n), 150, 600) * 0.025
        for k in range(int(sec * 1.5)):
            i, L = int(r.uniform(0, n - N(0.4))), N(0.35)
            x[i:i + L] += np.sin(2 * math.pi * r.uniform(4200, 4800) * tt(L)) * (np.sin(2 * math.pi * 28 * tt(L)) > 0) * 0.012
    return x


SALA = {"regent", "nauka", "dorosl", "bunt", "odprawa", "lisi", "mapa", "dary", "sztylet", "atak", "kolumna", "lekarz", "cios",
        "pretekst", "przejscia", "huhai"}
MORZE = {"morze", "xufu", "puste"}

# wydarzenia ujęć: (sekunda od początku ujęcia, dźwięk, głośność) — czasy z funkcji ujęć w ujecia1.py / ujecia2.py
ZDARZENIA = {
    "teatr": [(0.2, "gong", 1.0), (0.7, "knock", 0.6), (1.3, "whoosh", 0.6)],
    "choragwie": [(0.7 + n * 0.5 + (0.35 if n == 6 else 0), "knock", 0.7) for n in range(7)] + [(3.9, "drum", 0.5)],
    "oblezenie": [(0.5, "march", 4.0)],
    "kupiec": [(1.6, "wagon", 2.2)] + [(3.4 + n * 0.5, "coin", 0.6) for n in range(3)],
    "ucieczka": [(1.4, "wagon", 4.5)],
    "sam": [(0.0, "march", 2.4)],
    "powrot": [(0.0, "wagon", 6.0)],
    "krol13": [(2.2, "whoosh", 0.5), (3.0, "gong_s", 0.8)],
    "nauka": [(1.5, "coin", 0.8), (3.1, "knock", 0.6)],
    "dorosl": [(3.4, "drum", 0.8), (3.6, "fire", 3.0)],
    "bunt": [(0.0, "fire", 1.8), (0.2, "clash", 0.9), (0.8, "clash", 0.7), (1.3, "clash", 0.9), (0.0, "drum", 0.7)],
    "odprawa": [(1.1, "whoosh", 0.4), (3.0, "march", 2.0)],
    "trucizna": [(1.8, "coin", 0.4), (2.6, "thud", 0.5)],
    "lisi": [(0.6, "whoosh", 0.4)],
    "mapa": [(0.5, "whoosh", 0.7), (3.4, "whoosh", 0.4)],
    "machina": [(0.8, "drum", 0.8), (2.0, "drum", 0.8), (3.2, "drum", 0.9), (0.8, "march", 6.0)],
    "kusze": [(0.6, "whoosh", 0.9), (0.75, "whoosh", 0.8), (0.9, "whoosh", 0.8), (1.9, "thud", 0.6)],
    "kanal": [(0.5, "water", 5.0)],
    "wymarsz": [(0.3, "drum", 0.9), (0.3, "hooves", 6.0), (0.8, "march", 6.0)],
    "han": [(0.0, "hooves", 1.5), (0.5, "crack", 1.0)],
    "zhao": [(0.0, "hooves", 2.6), (0.6, "crack", 1.0), (2.4, "drum", 0.7)],
    "poselstwo": [(0.0, "wagon", 6.0)],
    "dary": [(2.0, "knock", 0.6), (2.6, "knock", 0.5)],
    "sztylet": [(0.5, "whoosh", 0.5), (3.0, "sword", 0.6)],
    "atak": [(0.2, "sword", 1.0), (0.3, "drum", 0.8)],
    "kolumna": [(0.0, "steps", 7.0)],
    "lekarz": [(2.0, "whoosh", 0.7), (2.75, "thud", 0.8)],
    "cios": [(0.55, "sword", 1.2), (0.75, "clash", 0.6), (0.9, "thud", 1.0)],
    "pretekst": [(0.6, "gong_s", 0.7)],
    "ksiaze": [(0.0, "hooves", 1.8), (2.0, "crack", 0.5), (0.0, "march", 6.0)],
    "wei": [(0.8, "water", 6.5), (3.9, "crack", 0.8)],
    "chu": [(0.2, "march", 6.0), (0.2, "drum", 0.9), (1.4, "drum", 0.9), (2.6, "drum", 0.9)],
    "chu_yan": [(0.85, "crack", 1.0), (1.45, "crack", 0.9), (0.0, "hooves", 2.5)],
    "qi": [(0.0, "hooves", 1.5), (1.5, "whoosh", 0.4), (3.2, "crack", 0.6)],
    "mapa2": [(0.2, "whoosh", 0.6)] + [(1.3 + n * 0.36, "knock", 0.5) for n in range(6)],
    "czarne": [(0.5 + n * 0.42, "drum", 0.8) for n in range(6)],
    "cesarz": [(1.2, "whoosh", 0.6), (1.75, "whoosh", 0.6), (2.9, "gong", 0.9)],
    "posagi": [(1.3 + j * 0.2, "clash", 0.35) for j in range(8)] + [(1.7, "fire", 3.0), (3.1, "thud", 0.9)],
    "drogi": [(0.0, "wagon", 6.0)],
    "prowincje": [(0.7 + n * 0.55, "knock", 0.5) for n in range(6)],
    "rody": [(0.0, "wagon", 8.0)],
    "stela": [(0.0, "wagon", 2.6), (3.2, "thud", 0.6)],
    "kanal2": [(0.4, "water", 6.0)],
    "pismo": [(0.4, "knock", 0.6), (2.2, "whoosh", 0.4)],
    "moneta": [(0.3, "roll", 1.9), (2.2, "coin", 0.9)],
    "miara": [(0.3, "whoosh", 0.4), (1.3, "whoosh", 0.4), (2.25, "coin", 0.7), (2.3, "knock", 0.4)],
    "mur": [(0.5 + n * 0.25, "knock", 0.35) for n in range(20)],
    "robotnicy": [(0.0, "steps", 7.0)],
    "ognie": [(0.5, "fire", 2.0), (1.5, "fire", 1.0)],
    "ksiegi": [(1.5, "fire", 4.0), (2.0, "whoosh", 0.7), (2.85, "whoosh", 0.9)],
    "popiol": [(0.0, "fire", 2.0)],
    "uczeni": [(2.3, "thud", 0.4), (3.1, "thud", 0.4), (3.9, "thud", 0.4), (7.3, "steps", 2.0)],
    "zmierzch": [(0.3, "whoosh", 0.5), (2.2, "knock", 0.5), (2.9, "knock", 0.5)],
    "mlot": [(0.0, "wagon", 2.7), (1.7, "whoosh", 1.0), (2.7, "crack", 1.2), (2.7, "thud", 1.2)],
    "morze": [(0.2, "whoosh", 0.6), (2.8, "whoosh", 0.4)],
    "xufu": [(0.0, "water", 6.0)],
    "rtec": [(0.3, "knock", 0.5), (1.6, "coin", 0.5), (2.35, "coin", 0.5), (3.1, "coin", 0.5)],
    "przejscia": [(0.0, "steps", 7.0)],
    "meteor": [(0.7, "whoosh", 1.0), (1.6, "thud", 1.3), (1.6, "crack", 0.8), (3.0, "whoosh", 0.4)],
    "palac": [(0.5, "thud", 0.6), (2.2, "thud", 0.6), (3.9, "thud", 0.6)],
    "kopiec": [(0.4, "thud", 0.5), (2.4, "steps", 4.0)],
    "armia": [(0.7 + n * 0.5, "knock", 0.4) for n in range(10)] + [(0.0, "drum", 0.6)],
    "twarze": [(6.2 - 7.0 + 2.4, "knock", 0.6)],
    "rzeki": [(0.4, "water", 6.0)],
    "podroz": [(0.0, "wagon", 6.0)],
    "koniec": [(1.9, "gong", 0.8)],
    "spisek": [(2.8, "whoosh", 0.5)],
    "ryby": [(0.0, "wagon", 7.0)],
    "list": [(1.0, "whoosh", 0.4), (3.8, "thud", 0.3)],
    "huhai": [(1.6, "drum", 0.5)],
    "powstanie": [(0.4, "march", 7.0), (0.4, "drum", 0.9), (2.8, "crack", 0.8), (3.5, "crack", 0.8), (4.2, "crack", 0.8)],
    "upadek": [(0.4, "crack", 0.9), (0.9, "crack", 0.9), (1.4, "crack", 0.9), (1.0, "thud", 1.0), (1.2, "fire", 6.0),
               (2.4, "crack", 1.0), (2.9, "whoosh", 0.6)],
    "cisza": [(0.3, "whoosh", 0.3)],
    "studnia": [(0.0, "dig", 2.0), (2.0, "thud", 0.4), (3.6, "whoosh", 0.4)],
    "grobowiec": [(0.8, "whoosh", 0.3)],
    "qin": [(0.2, "march", 2.0), (6.0, "gong", 0.9)],
}


def long_sound(kind, sec):
    if kind == "march":
        return marching(sec)
    if kind == "hooves":
        return hooves(sec)
    if kind == "fire":
        return fire(sec)
    if kind == "water":
        return band(RNG.normal(0, 1, N(sec)), 200, 3000) * 0.08 * (0.6 + 0.4 * np.sin(2 * math.pi * tt(N(sec)) / 2.3) ** 2) \
            * np.minimum(1, tt(N(sec)) / 0.5)
    if kind in ("wagon", "steps", "dig", "roll"):
        n = N(sec)
        out = np.zeros(n)
        step = {"wagon": 0.32, "steps": 0.45, "dig": 0.5, "roll": 0.06}[kind]
        k = 0.0
        while k < sec - 0.1:
            s = knock(RNG.uniform(120, 200) if kind != "roll" else 900, 0.2) * (0.35 if kind != "roll" else 0.15)
            if kind == "wagon":
                s = s + band(RNG.normal(0, 1, len(s)), 400, 2500) * env(len(s), 0.01, 0.08) * 0.1
            i = N(k)
            out[i:i + len(s)] += s[:n - i]
            k += step * RNG.uniform(0.85, 1.15)
        return out
    return None


def muzyka(total, voice_mask, acts):
    """Szarpane struny w skali pentatonicznej + burdon; gęstość i bęben według nastroju aktu."""
    n = N(total)
    out = np.zeros(n)
    scale = [196.0, 220.0, 261.6, 293.7, 329.6, 392.0, 440.0, 523.3, 587.3]  # G A C D E (pentatonika)
    r = np.random.default_rng(3)
    for a0, a1, mood in acts:
        k, last = a0 + 0.5, 4
        while k < a1 - 0.5:
            last = int(np.clip(last + r.choice((-2, -1, -1, 1, 1, 2)), 0, len(scale) - 1))
            f = scale[last] * (0.5 if mood == "noc" else 1.0)
            L = N(2.5)
            p = int(SR / f)
            buf = r.uniform(-1, 1, p)
            y = np.empty(L)
            for j in range(L):  # Karplus-Strong: struna szarpana
                y[j] = buf[j % p]
                buf[j % p] = 0.5 * (buf[j % p] + buf[(j + 1) % p]) * 0.996
            i = N(k)
            out[i:i + L] += y[:n - i] * 0.16
            k += r.choice((0.5, 0.75, 1.0, 1.5)) * (1.6 if mood == "noc" else 1.0)
        i0, i1 = N(a0), min(n, N(a1))
        tt_ = tt(i1 - i0)
        base = 98.0 if mood != "noc" else 73.4
        drone = (np.sin(2 * math.pi * base * tt_) + 0.5 * np.sin(2 * math.pi * base * 1.5 * tt_)) * 0.025
        out[i0:i1] += drone * np.minimum(1, tt_ / 2) * np.minimum(1, (tt_[-1] - tt_) / 2)
        if mood == "wojna":
            k = a0
            while k < a1 - 1:
                s = drum(0.8, 60) * 0.35
                i = N(k)
                out[i:i + len(s)] += s[:n - i]
                k += 0.9
    out *= np.where(voice_mask, 10 ** (-9 / 20), 1.0)
    return out


AKT_NASTROJ = {1: "spokoj", 2: "spokoj", 3: "wojna", 4: "wojna", 5: "spokoj", 6: "noc", 7: "noc", 8: "wojna"}


def zapisz(path, x):
    x = np.tanh(x * 1.2) * 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    import render as R
    us = ujecia()
    total = sum(u[5] for u in us)
    n = N(total)
    fx, voice = np.zeros(n), np.zeros(n, bool)
    t0, acts, events = 0.0, [], 0
    for idx, (akt, _, klucz, kadr, ruch, sec, opis, snd) in enumerate(us):
        vs, vl = okno_kwestii(snd)
        if vl:
            voice[N(t0 + vs):N(t0 + vs + vl)] = True
        if not acts or acts[-1][2] != akt:
            acts.append([t0, t0 + sec, akt])
        acts[-1][1] = t0 + sec
        place = "sala" if klucz in SALA else "morze" if klucz in MORZE else "noc" if swiat_noc(idx) else "wiatr"
        amb = ambient(place, sec + 0.3, idx)
        i = N(t0)
        fx[i:i + len(amb)] += amb[:n - i]
        evs = list(ZDARZENIA.get(klucz, []))
        if klucz in R.BUDUJ:  # zmiana dekoracji: papier i drewno w rytm wjeżdżających elementów
            evs += [(d, "whoosh", 0.35) for d in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(d, "knock", 0.3) for d in (0.75, 1.05, 1.4, 1.7)]
        for at, kind, g in evs:
            if at >= sec:
                continue
            s = long_sound(kind, min(g, sec - at)) if kind in ("march", "hooves", "fire", "water", "wagon", "steps", "dig", "roll") \
                else SFX[kind]() * g
            j = N(t0 + at)
            fx[j:j + len(s)] += s[:n - j]
            events += 1
        t0 += sec
    fx *= np.where(voice, 10 ** (-6 / 20), 1.0)
    mus = muzyka(total, voice, [(a0, a1, AKT_NASTROJ[a]) for a0, a1, a in acts])
    OUT.mkdir(exist_ok=True)
    zapisz(OUT / "efekty.wav", fx)
    zapisz(OUT / "muzyka.wav", mus)
    print(f"efekty: {events} zdarzeń + tło, muzyka: {len(acts)} aktów, {total:.1f} s")


def swiat_noc(idx):
    import swiat
    return swiat.stan(idx).noc > 0.5


if __name__ == "__main__":
    main()
