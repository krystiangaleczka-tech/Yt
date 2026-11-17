"""Dźwięk filmu „Syn słońca — powstanie Japonii” bez lektora: muzyka (ścieżka Muzyka) i efekty (ścieżka Efekty), synteza w numpy.

Wzór: output/pierwszy-cesarz/efekty.py (te same dźwięki bazowe).
- Muzyka: szarpane struny w japońskiej skali in (Karplus-Strong, brzmienie zbliżone do koto) na burdonie; w aktach bitew
  bęben taiko; pod kwestiami lektora ściszona o 9 dB.
- Efekty: tło miejsca (wiatr, morze, las, burza, noc, wnętrze), papier i drewno teatru przy każdej zmianie dekoracji
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
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"))
from dane import okno_kwestii, ujecia  # noqa: E402

SR = 44100
OUT = HERE / "dzwiek"
RNG = np.random.default_rng(11)


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



def thunder(sec=2.5):
    n, t = N(sec), tt(N(sec))
    rum = band(RNG.normal(0, 1, n), 30, 220) * np.exp(-t / 0.9) * 1.4
    return rum + np.pad(crack(0.4), (0, max(0, n - N(0.4))))[:n] * 0.8


def crow_call(sec=0.45):
    """Krakanie: chrapliwy dźwięk z pasma szumu i tonu."""
    n, t = N(sec), tt(N(sec))
    tone = np.sin(2 * math.pi * (620 - 180 * t / sec) * t) * 0.4
    return (band(RNG.normal(0, 1, n), 500, 2400) * 0.5 + tone) * np.sin(np.pi * t / sec) ** 0.6 * 0.5


def rooster(sec=1.3):
    n, t = N(sec), tt(N(sec))
    f = 520 + 380 * np.sin(np.pi * np.clip(t / sec, 0, 1)) - 200 * (t > sec * 0.7)
    ph = 2 * math.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * (1 + 0.3 * np.sin(2 * math.pi * 30 * t))
    return x * np.sin(np.pi * t / sec) ** 0.5 * 0.18


def growl(sec=1.4):
    n, t = N(sec), tt(N(sec))
    return band(RNG.normal(0, 1, n), 60, 400) * (0.6 + 0.4 * np.sin(2 * math.pi * 7 * t)) * np.sin(np.pi * t / sec) * 0.8


def chime(sec=1.6):
    """Błysk światła: dzwoneczki."""
    n, t = N(sec), tt(N(sec))
    return sum(np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, d in ((1568, 0.8), (2093, 0.6), (2637, 0.5), (3136, 0.4))) * 0.08


def hail(sec):
    n = N(sec)
    out = np.zeros(n)
    for i in RNG.integers(0, n, int(sec * 90)):
        L = min(n - i, N(0.012))
        out[i:i + L] += RNG.uniform(0.1, 0.5) * np.exp(-tt(L) / 0.003) * RNG.choice((-1, 1))
    return band(out, 1500, 9000) * 1.2


def slurp(sec=1.0):
    n = N(sec)
    return band(RNG.normal(0, 1, n), 200, 1400) * (0.5 + 0.5 * np.sin(2 * math.pi * 5 * tt(n))) * env(n, 0.05, 0.5) * 0.4


SFX = {"gong": gong, "whoosh": whoosh, "knock": knock, "drum": drum, "crack": crack, "clash": clash, "coin": coin,
       "thud": thud, "splash": splash, "sword": sword, "gong_s": lambda: gong(2.5, 220) * 0.6, "thunder": thunder,
       "crow": crow_call, "rooster": rooster, "growl": growl, "chime": chime, "slurp": slurp}


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
    elif kind == "las":
        x = band(r.normal(0, 1, n), 200, 1200) * slow * 0.04
        for k in range(int(sec * 0.8)):
            i, L = int(r.uniform(0, n - N(0.3))), N(0.12)
            x[i:i + L] += np.sin(2 * math.pi * r.uniform(2600, 3600) * tt(L)) * np.sin(np.pi * tt(L) / 0.12) * 0.02
    elif kind == "burza":
        x = band(r.normal(0, 1, n), 80, 1800) * (0.6 + 0.4 * slow) * 0.16
    else:  # noc: świerszcze
        x = band(r.normal(0, 1, n), 150, 600) * 0.025
        for k in range(int(sec * 1.5)):
            i, L = int(r.uniform(0, n - N(0.4))), N(0.35)
            x[i:i + L] += np.sin(2 * math.pi * r.uniform(4200, 4800) * tt(L)) * (np.sin(2 * math.pi * 28 * tt(L)) > 0) * 0.012
    return x



MORZE = {"meduza", "most", "wlocznia", "kropla", "wyspy", "ogien", "flota", "itsuse", "sam", "nihon", "koniec"}
NOC = {"yomi", "ciemno", "koguty", "uzume", "lustro"}
LAS = {"las", "niedzwiedz", "takakuraji", "przebudzenie"}
WNETRZE = {"kronika", "rachunek", "odcisk", "himiko", "koronacja", "pieczec"}
BURZA = {"burza", "bitwa", "ptak", "blysk"}

# wydarzenia ujęć: (sekunda od początku ujęcia, dźwięk, głośność) — czasy z funkcji ujęć w ujecia_a.py / ujecia_b.py
ZDARZENIA = {
    "teatr": [(0.2, "gong", 1.0), (0.7, "knock", 0.6), (1.3, "whoosh", 0.6)],
    "luty": [(1.0, "whoosh", 0.4)] + [(1.8 + 0.45 * n, "knock", 0.5) for n in range(9)],
    "cien": [(0.3, "knock", 0.5), (1.4, "whoosh", 0.3), (3.9, "whoosh", 0.5)],
    "meduza": [(1.8, "water", 3.0)],
    "most": [(0.4, "whoosh", 0.6), (2.4, "whoosh", 0.4), (3.2, "whoosh", 0.4), (1.9, "knock", 0.4)],
    "wlocznia": [(0.6, "splash", 0.5), (1.4, "water", 6.0)],
    "kropla": [(2.55, "splash", 0.7), (2.8, "thud", 0.4)],
    "wyspy": [(0.7 + 0.55 * n, "thud", 0.35) for n in range(8)],
    "ogien": [(0.9, "fire", 6.0), (2.9, "whoosh", 0.4)],
    "yomi": [(0.0, "steps", 3.6), (3.4, "whoosh", 0.4), (5.6, "steps", 2.2), (7.4, "thud", 1.0)],
    "rzeka": [(0.3, "water", 9.0), (1.6, "splash", 0.5), (2.2, "chime", 1.0), (5.2, "splash", 0.5), (8.4, "splash", 0.5), (8.6, "thunder", 0.6)],
    "susanoo": [(0.9, "whoosh", 1.0), (1.6, "whoosh", 0.9), (2.6, "crack", 0.8), (3.0, "thud", 0.7), (4.0, "whoosh", 0.8)],
    "jaskinia": [(0.4, "steps", 2.6), (3.4, "thud", 0.9), (4.6, "whoosh", 0.5)],
    "ciemno": [(0.3, "fire", 2.5), (0.8, "knock", 0.3), (1.3, "knock", 0.3), (1.8, "knock", 0.3)],
    "koguty": [(0.4, "knock", 0.5), (2.0, "whoosh", 0.4), (3.0, "whoosh", 0.4), (5.6, "rooster", 1.0), (7.2, "rooster", 0.9)],
    "uzume": [(0.6 + 0.55 * n, "drum", 0.35) for n in range(14)] + [(2.0, "laugh", 6.0)],
    "lustro": [(0.6, "thud", 0.5), (2.4, "chime", 1.2), (5.0, "thud", 0.9), (6.2, "whoosh", 0.5)],
    "swit": [(0.2, "gong", 0.9), (0.4, "rooster", 0.9), (1.6, "rooster", 0.7)],
    "wygnanie": [(0.0, "water", 9.0), (0.7, "whoosh", 0.6), (3.3, "thud", 0.6)],
    "starcy": [(1.6, "growl", 2.0), (4.0, "growl", 1.4)],
    "kadzie": [(1.0, "chime", 0.6), (2.0, "whoosh", 0.4)] + [(3.6 + 0.35 * n, "knock", 0.45) for n in range(8)],
    "orochi": [(0.6 + 0.6 * n, "growl", 1.0) for n in range(8)] + [(0.4, "drum", 0.8)],
    "pije": [(0.3, "slurp", 1.2), (1.0, "slurp", 1.0), (2.2, "thud", 0.5), (2.7, "thud", 0.4)],
    "miecz": [(0.8, "sword", 1.2), (0.9, "clash", 0.5), (1.1, "thud", 1.0), (2.6, "chime", 1.4), (2.6, "gong_s", 0.6)],
    "skarby": [(2.6, "whoosh", 0.4), (3.8, "whoosh", 0.4), (5.0, "whoosh", 0.4), (5.4, "chime", 0.8)],
    "zejscie": [(0.2, "whoosh", 0.8), (2.0, "whoosh", 0.6), (4.0, "whoosh", 0.6), (6.0, "thud", 0.4)],
    "siostry": [(3.6, "whoosh", 0.3), (6.0, "thud", 0.4)],
    "platki": [(0.5, "chime", 0.5)],
    "prawnuk": [(2.2, "whoosh", 0.4), (3.2, "knock", 0.5), (4.4, "whoosh", 0.4)],
    "wschod": [(0.8, "whoosh", 0.3), (1.4, "thud", 0.5), (2.6, "gong_s", 0.7)],
    "bracia": [(0.6 + 0.6 * n, "knock", 0.5) for n in range(3)],
    "flota": [(0.0, "water", 9.0), (0.9, "oars", 8.0)],
    "postoje": [(0.0, "water", 9.0), (1.0, "dig", 8.0)],
    "naniwa": [(0.6, "water", 4.0), (0.6, "oars", 3.0), (3.2, "march", 6.0), (3.2, "drum", 0.7)],
    "nagasune": [(0.5, "thud", 0.6), (1.6, "march", 6.0), (1.6, "drum", 0.9), (2.8, "drum", 0.9)],
    "strzaly": [(0.0, "whoosh", 0.9), (0.15, "whoosh", 0.8), (0.3, "whoosh", 0.8), (0.9, "thud", 0.6), (1.1, "thud", 0.5)],
    "rana": [(0.4, "whoosh", 0.7), (0.9, "thud", 0.9)],
    "pod_slonce": [(0.8, "whoosh", 0.3), (4.6, "knock", 0.3)],
    "itsuse": [(0.0, "water", 8.0), (2.6, "thud", 0.4)],
    "burza": [(0.0, "storm", 7.0), (1.0, "thunder", 1.0), (3.3, "thunder", 1.0), (2.6, "crack", 0.7), (3.4, "splash", 0.8)],
    "sam": [(0.0, "water", 4.5)],
    "las": [(0.4, "whoosh", 0.4), (1.2, "march", 2.0)],
    "niedzwiedz": [(0.6, "growl", 2.4)] + [(4.4 + 0.35 * n, "thud", 0.5) for n in range(7)],
    "takakuraji": [(0.5, "whoosh", 0.6), (2.4, "crack", 0.5), (2.5, "chime", 0.8), (4.0, "steps", 5.0)],
    "przebudzenie": [(2.2, "sword", 0.8), (2.3, "chime", 0.9)] + [(3.0 + 0.6 * n, "knock", 0.4) for n in range(6)],
    "wrona": [(0.8, "crow", 1.0), (3.6, "crow", 0.8), (0.0, "march", 8.0)],
    "trzy_nogi": [(0.3, "whoosh", 0.5), (1.6, "knock", 0.4), (2.4, "crow", 0.9)],
    "yamato": [(2.2 + 0.6 * n, "knock", 0.5) for n in range(3)] + [(0.0, "drum", 0.4)],
    "pulapka": [(6.2, "steps", 1.0), (7.2, "whoosh", 0.4), (7.55, "thud", 1.2), (7.55, "crack", 0.8)],
    "bitwa": [(1.0, "march", 8.0), (1.0, "drum", 0.9), (3.0, "clash", 0.9), (3.4, "clash", 0.8), (2.6, "hail", 8.0), (2.0, "thunder", 0.7)],
    "ptak": [(0.4, "whoosh", 0.6), (2.6, "chime", 1.4), (2.8, "gong_s", 0.6), (0.0, "hail", 3.0)],
    "blysk": [(0.0, "thunder", 1.0), (0.05, "chime", 1.0), (0.4, "march", 1.5)],
    "order": [(0.4, "whoosh", 0.4), (1.8, "coin", 0.6)],
    "strzala_nieba": [(0.8, "whoosh", 0.4), (2.2, "whoosh", 0.4), (4.4, "knock", 0.5)],
    "zdrada": [(1.2, "sword", 1.1), (1.4, "thud", 0.9), (4.4, "knock", 0.4)],
    "palac": [(0.6, "thud", 0.6), (1.8, "thud", 0.6), (3.0, "knock", 0.6), (4.4, "whoosh", 0.5), (5.6, "thud", 0.7), (6.2, "whoosh", 0.4),
              (7.4, "knock", 0.6)],
    "tron": [(0.8, "whoosh", 0.4), (2.2, "chime", 0.6), (2.8, "chime", 0.5), (3.4, "chime", 0.5), (5.0, "gong", 0.8)],
    "imie": [(0.6, "whoosh", 0.4), (1.6, "gong_s", 0.6)],
    "zona": [(0.8, "whoosh", 0.3), (3.0, "chime", 0.4)],
    "pola": [(0.0, "wind_long", 9.0), (2.4, "whoosh", 0.4), (4.6, "whoosh", 0.4)],
    "smierc": [(0.6, "whoosh", 0.4), (3.0, "gong", 0.8)],
    "pusto": [(0.2, "chime", 0.5)],
    "linia": [(0.6 + 0.22 * n, "knock", 0.25) for n in range(26)],
    "kronika": [(0.3, "knock", 0.6), (0.8, "whoosh", 0.4), (1.6, "scroll", 6.0), (2.6, "whoosh", 0.4), (6.4, "whoosh", 0.4)],
    "rachunek": [(0.8, "whoosh", 0.4), (2.6, "whoosh", 0.4), (4.4, "whoosh", 0.4), (5.4, "gong_s", 0.5)],
    "jomon": [(2.4, "steps", 7.0), (1.6, "knock", 0.5), (1.9, "knock", 0.5)],
    "wa": [(0.3, "whoosh", 0.7)] + [(2.0 + 0.5 * n, "knock", 0.2) for n in range(12)],
    "pieczec": [(0.3, "whoosh", 0.5), (1.6, "coin", 0.6), (2.0, "whoosh", 0.4)],
    "odcisk": [(0.55, "knock", 1.0), (0.6, "thud", 0.5)],
    "chlop": [(0.0, "dig", 3.0), (3.0, "coin", 0.8), (4.0, "whoosh", 0.4)],
    "himiko": [(0.2, "whoosh", 0.4), (1.0, "knock", 0.5)] + [(2.2 + 0.4 * n, "chime", 0.25) for n in range(10)],
    "kofun": [(0.6, "whoosh", 0.7), (4.2, "whoosh", 0.4)],
    "haniwa": [(0.4 + 0.45 * n, "knock", 0.4) for n in range(20)],
    "tancerz": [(0.2, "chime", 0.7)],
    "nihon": [(0.4, "whoosh", 0.4), (2.2, "whoosh", 0.6), (4.2, "whoosh", 0.4), (4.6, "gong", 0.9)],
    "luty2": [(0.4, "whoosh", 0.4), (1.4, "whoosh", 0.4)] + [(3.0 + 0.4 * n, "knock", 0.45) for n in range(9)],
    "koronacja": [(0.6, "thud", 0.5), (2.6, "knock", 0.5), (3.2, "knock", 0.5), (5.0, "whoosh", 0.4), (5.2, "gong_s", 0.6)],
    "koniec": [(0.2, "water", 6.0), (9.0, "gong", 0.9)],
}


def long_sound(kind, sec):
    if kind == "march":
        return marching(sec)
    if kind == "hooves":
        return hooves(sec)
    if kind == "fire":
        return fire(sec)
    if kind == "storm":
        return band(RNG.normal(0, 1, N(sec)), 100, 3000) * 0.18 * (0.6 + 0.4 * np.sin(2 * math.pi * tt(N(sec)) / 1.7) ** 2)
    if kind == "hail":
        return hail(sec)
    if kind == "laugh":  # śmiech bogów: krótkie, nieregularne „ha” z pasma szumu
        n = N(sec)
        out = np.zeros(n)
        k = 0.0
        while k < sec - 0.3:
            L = N(RNG.uniform(0.08, 0.14))
            i = N(k)
            f = RNG.uniform(180, 320)
            s = (np.sin(2 * math.pi * f * tt(L)) * 0.5 + band(RNG.normal(0, 1, L), 400, 2500) * 0.6) * np.sin(np.pi * tt(L) / (L / SR))
            out[i:i + L] += s[:n - i] * RNG.uniform(0.15, 0.35)
            k += RNG.uniform(0.12, 0.3)
        return out
    if kind in ("wind_long",):
        return band(RNG.normal(0, 1, N(sec)), 150, 900) * 0.06
    if kind == "scroll":
        return band(RNG.normal(0, 1, N(sec)), 1500, 7000) * 0.025 * (0.5 + 0.5 * np.sin(2 * math.pi * 0.7 * tt(N(sec))))
    if kind == "water":
        return band(RNG.normal(0, 1, N(sec)), 200, 3000) * 0.08 * (0.6 + 0.4 * np.sin(2 * math.pi * tt(N(sec)) / 2.3) ** 2) \
            * np.minimum(1, tt(N(sec)) / 0.5)
    if kind in ("wagon", "steps", "dig", "roll", "oars"):
        n = N(sec)
        out = np.zeros(n)
        step = {"wagon": 0.32, "steps": 0.45, "dig": 0.5, "roll": 0.06, "oars": 1.1}[kind]
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



DLUGIE = ("march", "hooves", "fire", "water", "wagon", "steps", "dig", "roll", "oars", "storm", "hail", "laugh", "wind_long", "scroll")


def muzyka(total, voice_mask, acts):
    """Szarpane struny w skali in (D Es G A B) + burdon; gęstość, rejestr i taiko według nastroju aktu."""
    n = N(total)
    out = np.zeros(n)
    scale = [293.7, 311.1, 392.0, 440.0, 466.2, 587.3, 622.3, 784.0, 880.0]
    r = np.random.default_rng(5)
    for a0, a1, mood in acts:
        k, last = a0 + 0.5, 4
        while k < a1 - 0.5:
            last = int(np.clip(last + r.choice((-2, -1, -1, 1, 1, 2)), 0, len(scale) - 1))
            f = scale[last] * (0.5 if mood in ("noc", "mit") else 1.0)
            L = N(2.8)
            p = int(SR / f)
            buf = r.uniform(-1, 1, p)
            y = np.empty(L)
            for j in range(L):  # Karplus-Strong: struna szarpana (koto)
                y[j] = buf[j % p]
                buf[j % p] = 0.5 * (buf[j % p] + buf[(j + 1) % p]) * 0.997
            i = N(k)
            out[i:i + L] += y[:n - i] * 0.15
            k += r.choice((0.5, 0.75, 1.0, 1.5, 2.0)) * (1.7 if mood in ("noc", "mit") else 1.0)
        i0, i1 = N(a0), min(n, N(a1))
        tt_ = tt(i1 - i0)
        base = 73.4 if mood in ("noc", "mit") else 98.0
        drone = (np.sin(2 * math.pi * base * tt_) + 0.5 * np.sin(2 * math.pi * base * 1.5 * tt_)) * 0.025
        out[i0:i1] += drone * np.minimum(1, tt_ / 2) * np.minimum(1, (tt_[-1] - tt_) / 2)
        if mood == "wojna":  # taiko: mocny, rzadki
            k = a0
            while k < a1 - 1:
                for d, g in ((0.0, 0.4), (0.6, 0.25), (1.2, 0.3)):
                    s = drum(0.9, 52) * g
                    i = N(k + d)
                    out[i:i + len(s)] += s[:n - i]
                k += 2.4
    out *= np.where(voice_mask, 10 ** (-9 / 20), 1.0)
    return out


AKT_NASTROJ = {1: "mit", 2: "noc", 3: "wojna", 4: "spokoj", 5: "noc", 6: "wojna", 7: "spokoj", 8: "spokoj", 9: "spokoj"}


def zapisz(path, x):
    x = np.tanh(x * 1.2) * 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    import render as R
    import scena
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
        place = ("morze" if klucz in MORZE else "noc" if klucz in NOC else "las" if klucz in LAS else "sala" if klucz in WNETRZE
                 else "burza" if klucz in BURZA else "wiatr")
        amb = ambient(place, sec + 0.3, idx)
        i = N(t0)
        fx[i:i + len(amb)] += amb[:n - i]
        evs = list(ZDARZENIA.get(klucz, []))
        if klucz in R.BUDUJ:  # zmiana dekoracji: papier i drewno w rytm wjeżdżających elementów
            evs += [(d, "whoosh", 0.35) for d in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(d, "knock", 0.3) for d in (0.75, 1.05, 1.4, 1.7)]
        for at, kind, g in evs:
            if at >= sec:
                continue
            s = long_sound(kind, min(g, sec - at)) if kind in DLUGIE else SFX[kind]() * g
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


if __name__ == "__main__":
    main()
