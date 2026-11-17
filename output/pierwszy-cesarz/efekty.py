"""Dźwięk filmu „Pierwszy cesarz” bez lektora: muzyka (ścieżka Muzyka) i efekty (ścieżka Efekty), synteza w numpy.

- Muzyka: szarpane struny w skali pentatonicznej (Karplus-Strong, brzmienie zbliżone do guzhengu) na burdonie;
  nastrój aktu (spokojny, wojenny z bębnami, nocny) z AKT_NASTROJ; pod kwestiami lektora ściszona o 9 dB.
- Efekty: tło miejsca (wiatr, sala, morze, noc ze świerszczami), papier i drewno teatru przy każdej zmianie dekoracji
  (ujęcia z render.BUDUJ), wydarzenia ujęć z ZDARZENIA (czasy od początku ujęcia — te same co w funkcjach ujęć).

uruchom:  python3 efekty.py            → dzwiek/muzyka.wav, dzwiek/efekty.wav (cały film, 44,1 kHz mono)
          JEZYK=en python efekty.py → dzwiek_en/ (wersja angielska: czasy z nagrań lektor_en/)
"""
import math
import sys
import os
import wave
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
from dane import JEZYK, okno_kwestii, ujecia  # noqa: E402

SR = 44100
OUT = HERE / ("dzwiek_en" if JEZYK == "en" else "dzwiek")  # JEZYK=en: czasy z lektor_en/, polska wersja zostaje w dzwiek/
OUT = Path(os.environ.get("DZWIEK_DO", OUT))  # DZWIEK_DO=katalog: próba obok plików wgranych do Studio (porównanie próbek)
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


def kurtyna(sec=0.9):
    """Szum ciężkiego materiału kurtyny przesuwanej na drążku, z cichym stukiem kółek."""
    n, t = N(sec), tt(N(sec))
    x = band(RNG.normal(0, 1, n), 120, 1400) * np.sin(np.linspace(0, math.pi, n)) ** 1.5 * 0.5
    for k in range(int(sec / 0.09)):
        i = N(k * 0.09 + RNG.uniform(0, 0.03))
        s_ = knock(RNG.uniform(500, 700), 0.05) * 0.08
        x[i:i + len(s_)] += s_[:n - i]
    return x


def _dzwon_kolka(r, g):
    """Jedno kółko kurtyny stuka o drążek: krótki, nieharmoniczny brzęk metalu (ok. 2–6 kHz, 15–35 ms)."""
    L = N(0.06)
    t = tt(L)
    f0 = r.uniform(1900, 2600)
    x = sum(a * np.sin(2 * math.pi * f0 * m * t + r.uniform(0, 6)) * np.exp(-t / d)
            for m, a, d in ((1.0, 1.0, 0.03), (1.62, 0.6, 0.02), (2.27, 0.4, 0.014), (3.1, 0.2, 0.01)))
    return x * np.minimum(1, t / 0.0008) * g


def _rozowy(r, n, lo, hi):
    """Szum z naturalnym spadkiem wysokich tonów (ok. −3 dB na oktawę) w paśmie lo–hi — jak szelest materiału."""
    X = np.fft.rfft(r.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / np.sqrt(np.maximum(f, lo)) * np.clip((f - lo * 0.6) / (lo * 0.4), 0, 1) * np.clip((hi * 1.4 - f) / (hi * 0.4), 0, 1)
    x = np.fft.irfft(X, n)
    return x / (np.abs(x).max() + 1e-9)


def kurtyna_nowa(zasuwa, sec=1.25):
    """Kurtyna teatru (reżyser 16.11: „dodaj wszędzie, gdzie jest kurtyna, dźwięk zaciągania i rozciągania kurtyny”):
    ciężki aksamit sunie po scenie (szelest materiału rośnie i opada z prędkością kurtyny, nieregularnie faluje na
    fałdach), kółka stukają o drążek tym gęściej, im szybciej kurtyna jedzie, a drążek turkocze. Zasuwanie
    (zasuwa=True) kończy się miękkim „fump” spotykających się połów i ostatnim brzękiem kółek; rozsuwanie zaczyna się
    szarpnięciem kółek. Czas ruchu jak w render.KURTYNA (0,8 s zasuwa, 0,85 s rozsuwa). Własne losowanie."""
    r = np.random.default_rng(311 if zasuwa else 312)
    n = N(sec)
    t = tt(n)
    ruch = 0.8 if zasuwa else 0.85
    v = np.sin(math.pi * np.clip(t / ruch, 0, 1)) ** 1.3  # prędkość kurtyny 0 → 1 → 0
    wezly = r.uniform(0.55, 1.0, int(sec * 18) + 2)  # fałdy aksamitu: nieregularne falowanie szelestu
    fald = np.interp(t, np.linspace(0, sec, len(wezly)), wezly)
    material = _rozowy(r, n, 120, 5500) * v ** 0.8 * fald * 0.75
    material += band(r.normal(0, 1, n), 3000, 8000) * v ** 2.2 * fald * 0.05  # szelest brzegu materiału
    turkot = band(r.normal(0, 1, n), 1400, 4200) * (np.sin(2 * math.pi * 34 * t) > 0.2) * v ** 1.2 * 0.10  # kółka toczą się
    out = material + turkot
    k = 0.02 if not zasuwa else 0.05
    while k < ruch:  # kółka: do ok. 30 stuknięć na sekundę przy pełnej prędkości
        vk = math.sin(math.pi * min(1.0, k / ruch)) ** 1.3
        if vk > 0.08:
            s_ = _dzwon_kolka(r, (0.10 + 0.16 * vk) * r.uniform(0.5, 1.0))
            i = N(k)
            out[i:i + len(s_)] += s_[:n - i]
        k += 1 / (8 + 30 * vk) * r.uniform(0.6, 1.4)
    if zasuwa:  # połowy spotykają się na środku: miękkie uderzenie ciężkiego materiału i ostatnie kółka
        i = N(ruch - 0.03)
        L = n - i
        tl = tt(L)
        fump = (np.sin(2 * math.pi * 80 * tl) * np.exp(-tl / 0.10) * 0.55
                + _rozowy(r, L, 70, 900) * np.exp(-tl / 0.08) * 0.5)
        out[i:] += fump
        for d in (0.0, 0.03, 0.065):
            s_ = _dzwon_kolka(r, 0.18)
            j = N(ruch - 0.06 + d)
            out[j:j + len(s_)] += s_[:n - j]
    else:  # szarpnięcie na starcie: kółka ruszają naraz
        for d in (0.0, 0.022, 0.045, 0.075):
            s_ = _dzwon_kolka(r, 0.2)
            j = N(d)
            out[j:j + len(s_)] += s_[:n - j]
    return out / (np.abs(out).max() + 1e-9) * 0.68


def kurtyna_zasuwa():
    kurtyna()  # dawna synteza tylko dla losowań wspólnego RNG (wytyczne 1.12)
    return kurtyna_nowa(True)


def kurtyna_rozsuwa():
    kurtyna()
    return kurtyna_nowa(False)


def klaps():
    """Drewniane klapki teatru (hyoshigi): dwa suche uderzenia przy tytule aktu."""
    a = knock(1150, 0.18) + knock(1600, 0.18) * 0.5
    out = np.zeros(N(0.5))
    for d in (0.0, 0.22):
        i = N(d)
        out[i:i + len(a)] += a[:len(out) - i]
    return out * 1.1


def buzz(sec=0.32):
    """Brzęczyk „źle”: czerwony X nad postacią."""
    n, t = N(sec), tt(N(sec))
    sq = np.sign(np.sin(2 * math.pi * 110 * t)) * 0.5 + np.sign(np.sin(2 * math.pi * 165 * t)) * 0.3
    return band(sq, 90, 2400) * env(n, 0.005, 0.25) * np.minimum(1, (sec - t) / 0.04) * 0.35


def gulp(sec=0.35):
    n, t = N(sec), tt(N(sec))
    f = 180 * np.exp(-t / 0.12) + 70
    return np.sin(2 * math.pi * np.cumsum(f) / SR) * env(n, 0.01, 0.12) * 0.5


def _rezonans(x, f, bw):
    """Rezonator dwubiegunowy (formant głosu): częstotliwość f, szerokość pasma bw [Hz]."""
    r = math.exp(-math.pi * bw / SR)
    a1, a2 = 2 * r * math.cos(2 * math.pi * f / SR), -r * r
    y = np.zeros_like(x)
    y1 = y2 = 0.0
    g = (1 - r)
    for i in range(len(x)):
        v = g * x[i] + a1 * y1 + a2 * y2
        y[i] = v
        y2, y1 = y1, v
    return y


def _kaszlniecie(sec, f0, glos, g):
    """Jedno kaszlnięcie: twardy start z krtani, chrapliwy szum i krótki dźwięczny ton, przepuszczone przez formanty
    otwartego „a” w gardle (ok. 650 / 1150 / 2600 Hz) — brzmi jak człowiek, nie jak szum."""
    n, t = N(sec), tt(N(sec))
    e = np.minimum(1, t / 0.004) * np.exp(-t / 0.055) + 0.35 * np.exp(-t / 0.16) * np.minimum(1, t / 0.02)
    szum = RNG.normal(0, 1, n) * e
    f = f0 * (1 - 0.25 * t / sec)
    impulsy = (np.diff(np.floor(np.cumsum(f) / SR), prepend=0) > 0).astype(np.float64)  # ciąg impulsów krtani
    ton = np.convolve(impulsy, np.exp(-np.arange(60) / 8.0))[:n] * np.exp(-t / 0.09) * glos
    zrodlo = szum * 0.8 + ton * 2.5
    out = sum(a * _rezonans(zrodlo, fr, bw) for fr, bw, a in ((650, 180, 1.0), (1150, 220, 0.7), (2600, 320, 0.35)))
    out += band(RNG.normal(0, 1, n), 2500, 7000) * np.exp(-t / 0.02) * 0.15  # trzask na początku
    return out / (np.abs(out).max() + 1e-9) * g


# Kaszel z nagrania zamiast syntezy (reżyser 16.11: „tam, gdzie cesarz kona, jest dźwięk tłuczenia, a nie kaszlenia”):
# próbki prawdziwego kaszlu z Chatterbox Turbo (znacznik [cough], kaszel.py → dzwiek_probki/kaszel_*.wav), kolejne
# kaszlnięcia w filmie biorą kolejne próbki. Synteza niżej liczy się dalej i jest wyrzucana, żeby wspólne losowania
# (RNG) zostały te same co w pliku w Studio — inaczej zmieniłyby się efekty całej reszty filmu (wytyczne 1.12).
PROBKI = HERE / "dzwiek_probki"
_KASZEL = []


def _probki_kaszlu():
    if not _KASZEL:
        for f in sorted(PROBKI.glob("kaszel_*.wav")):
            with wave.open(str(f)) as w:
                if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (SR, 1, 2):
                    raise SystemExit(f"{f}: potrzebny 44,1 kHz mono 16 bit (kaszel.py)")
                x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
            _KASZEL.append(x / (np.abs(x).max() + 1e-9))
        if not _KASZEL:
            raise SystemExit(f"brak próbek kaszlu w {PROBKI} — uruchom kaszel.py")
    return _KASZEL


_ILE_KASZLU = [0]


def cough(sec=1.2):
    """Kaszel chorego z nagrania (próbki kaszel.py); synteza tylko po to, żeby zużyć te same losowania co dawniej."""
    _cough_synteza(sec)
    probki = _probki_kaszlu()
    x = probki[_ILE_KASZLU[0] % len(probki)]
    _ILE_KASZLU[0] += 1
    return x * 0.55


def _cough_synteza(sec=1.2):
    """Dawny kaszel z syntezy (trzy kaszlnięcia przez formanty) — brzmiał jak tłuczenie; zostaje dla losowań RNG."""
    n = N(sec)
    out = np.zeros(n)
    for d, f0, glos, g in ((0.0, 150, 1.0, 0.9), (0.27, 138, 0.8, 0.75), (0.52, 128, 0.6, 0.55)):
        s_ = _kaszlniecie(0.24, f0 * RNG.uniform(0.95, 1.05), glos, g)
        i = N(d)
        out[i:i + len(s_)] += s_[:n - i]
    L = N(0.35)  # wdech
    wd = band(RNG.normal(0, 1, L), 1800, 5000) * np.sin(np.linspace(0, math.pi, L)) ** 2 * 0.12
    i = N(0.82)
    out[i:i + L] += wd[:n - i]
    return out * 0.6


def rattle(sec=1.4):
    """Ostatnie tchnienie: niski, rzężący wydech."""
    n, t = N(sec), tt(N(sec))
    x = band(RNG.normal(0, 1, n), 90, 900) * (0.5 + 0.5 * np.sin(2 * math.pi * 22 * t) ** 2)
    return x * np.sin(np.linspace(0, math.pi, n)) ** 1.5 * np.exp(-t / 0.9) * 0.45


def shout(sec=0.6):
    """Okrzyk wojska przy uniesieniu włóczni: wiele gardeł naraz."""
    n, t = N(sec), tt(N(sec))
    x = sum(band(np.sign(np.sin(2 * math.pi * f * t + RNG.uniform(0, 6))), 250, 1600) for f in (118, 131, 147, 165))
    return x * env(n, 0.04, 0.3) * 0.12 + clash(sec)[:n] * 0.3


SFX = {"gong": gong, "whoosh": whoosh, "knock": knock, "drum": drum, "crack": crack, "clash": clash, "coin": coin,
       "thud": thud, "splash": splash, "sword": sword, "gong_s": lambda: gong(2.5, 220) * 0.6,
       "kurtyna": kurtyna, "kurtyna_z": kurtyna_zasuwa, "kurtyna_r": kurtyna_rozsuwa, "klaps": klaps, "buzz": buzz, "gulp": gulp, "cough": cough, "rattle": rattle, "shout": shout, "tick": lambda: knock(900, 0.08) * 0.5}


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
    "moneta": [(0.3, "roll", (1.9, 1.5)), (1.8, "coin", 0.7), (2.2, "coin", 0.9)],
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


# Uwagi reżysera w Studio 15.11.2026: nowe wydarzenia ujęć mają swój dźwięk (X, picie trucizny, okrzyk wojska, pisanie,
# kaszel i rzężenie, zamroczenie, łopot skrzydeł i flagi, plusk ryb, dudnienie kopca); czasy jak w ujecia1.py / ujecia2.py.
ZDARZENIA.update({
    "odprawa": [(1.1, "whoosh", 0.4), (1.5, "buzz", 1.0), (1.98, "buzz", 1.0), (3.3, "march", 2.0)],
    "trucizna": [(0.9, "whoosh", 0.3), (2.0, "whoosh", 0.3), (3.0, "gulp", 0.9), (3.4, "gulp", 0.8), (4.45, "coin", 0.7),
                 (4.55, "knock", 0.6), (4.7, "cough", 0.6), (5.0, "thud", 0.5)],
    "machina": [(0.8, "drum", 0.8), (2.0, "drum", 0.8), (3.2, "drum", 0.9), (0.8, "march", 9.0)]
               + [(a, "shout", 1.0) for a in (4.9, 6.2, 7.5)] + [(a, "drum", 1.0) for a in (4.9, 6.2, 7.5)],
    "kusze": [(a + d, "whoosh", 0.8) for a in (0.6, 2.7) for d in (0.0, 0.15, 0.3)] + [(1.9, "thud", 0.6), (4.0, "thud", 0.7)],
    "kanal": [(0.6, "water", 11.0), (0.6, "dig", 8.0), (9.3, "water", 3.0)],
    "wymarsz": [(0.3, "drum", 0.9), (0.3, "hooves", 8.0), (0.8, "march", 8.0), (1.7, "whoosh", 0.3), (2.9, "whoosh", 0.3)],
    "zhao": [(0.0, "hooves", 2.6), (0.6, "crack", 1.0), (2.5, "whoosh", 0.8), (2.92, "thud", 1.2), (3.0, "drum", 0.7)],
    "poselstwo": [(0.0, "wagon", 10.0), (5.0, "whoosh", 0.5), (5.6, "drum", 0.6)],
    "sztylet": [(0.9, "whoosh", 0.4), (1.85, "knock", 0.5), (2.6, "sword", 0.8)],
    "lekarz": [(0.0, "steps", 1.0), (1.0, "sword", 0.7), (1.75, "sword", 0.7), (1.95, "whoosh", 0.7), (2.65, "thud", 1.0),
               (2.68, "knock", 0.8), (2.8, "stun", 6.0)],
    "pretekst": [(0.4, "sword", 0.8), (0.8, "thud", 0.9), (0.0, "whoosh", 0.3), (2.0, "whoosh", 0.25), (4.0, "whoosh", 0.25),
                 (6.0, "whoosh", 0.4), (6.6, "thud", 0.8), (6.8, "gong_s", 0.6)],
    "wei": [(0.3, "gong_s", 0.4), (0.5, "dig", 2.0), (2.6, "water", 8.0), (5.6, "crack", 0.9), (5.65, "rumble", 2.0), (6.6, "whoosh", 0.4)],
    "chu": [(0.2, "march", 7.5), (0.2, "drum", 0.9), (1.2, "drum", 0.9), (2.2, "drum", 0.9), (3.2, "drum", 0.9), (4.2, "drum", 0.9)],
    "chu_yan": [(0.85, "crack", 1.0), (1.45, "crack", 0.9), (0.0, "hooves", 2.5), (0.0, "march", 2.5)],
    "qi": [(0.0, "hooves", 1.5), (0.0, "march", 1.6), (1.5, "whoosh", 0.4), (3.2, "crack", 0.6), (3.7, "whoosh", 0.5), (3.8, "flap", 2.4)],
    "czarne": [(0.5 + n * 0.42, "drum", 0.8) for n in range(6)] + [(3.0, "march", 4.0), (5.6, "gong", 0.8)],
    "cesarz": [(0.8, "whoosh", 0.6), (1.2, "whoosh", 0.5), (1.75, "whoosh", 0.5), (2.85, "whoosh", 1.0), (3.15, "whoosh", 0.6),
               (3.6, "gong", 1.0)],
    "posagi": [(1.2 + j * 0.11, "clash", 0.25) for j in range(22)] + [(1.7, "fire", 5.0), (3.4, "thud", 0.9), (3.4, "rumble", 1.6)],
    "drogi": [(0.0, "wagon", 7.3), (0.6, "roll", 1.5)],
    "prowincje": [(0.3, "whoosh", 0.7)] + [(1.3 + n * 0.075, "tick", 0.6) for n in range(36)] + [(4.3, "whoosh", 0.7)]
                 + [(4.8 + n * 0.06, "tick", 0.4) for n in range(36)] + [(5.4 + n * 0.45, "knock", 0.4) for n in range(6)],
    "rody": [(0.0, "wagon", 15.5), (0.3, "wagon", 15.0), (0.0, "hooves", 15.0)],
    "stela": [(0.0, "wagon", 2.6), (4.7, "rumble", 1.6), (4.8, "thud", 0.7)],
    "kanal2": [(0.4, "water", 8.0), (1.2, "whoosh", 0.4)],
    "pismo": [(0.1, "roll", 1.0), (0.4, "knock", 0.6), (2.2, "whoosh", 0.4), (3.5, "pisanie", 4.8)],
    "moneta": [(0.3, "roll", (1.9, 1.5)), (1.8, "coin", 0.7), (2.2, "coin", 0.9), (0.0, "pisanie", 4.4)],
    "miara": [(0.2, "whoosh", 0.3), (0.3, "whoosh", 0.4), (1.3, "knock", 0.5), (1.7, "whoosh", 0.4), (2.6, "coin", 0.8), (2.65, "knock", 0.4),
              (3.4, "tick", 0.5), (4.2, "tick", 0.4)],
    "mur": [(0.2, "whoosh", 0.3)] + [(0.5 + n * 0.28, "knock", 0.35) for n in range(30)],
    "robotnicy": [(0.0, "steps", 13.0)] + [(0.6 + n * 1.6, "knock", 0.35) for n in range(7)],
    "ognie": [(0.5, "fire", 4.0), (1.6, "fire", 3.0), (2.8, "fire", 1.8)],
    "ksiegi": [(0.0, "whoosh", 0.3), (1.5, "fire", 4.0), (2.0, "whoosh", 0.7), (2.85, "whoosh", 0.9)],
    "popiol": [(0.0, "fire", 3.6)],
    "uczeni": [(a + d, "buzz", 0.9) for a in (1.3, 2.1, 2.9) for d in (0.0, 0.48)] + [(2.3, "thud", 0.4), (3.1, "thud", 0.4),
                                                                                     (3.9, "thud", 0.4), (7.3, "steps", 3.0)],
    "zmierzch": [(0.3, "whoosh", 0.5), (2.2, "knock", 0.5), (2.9, "knock", 0.5), (6.7, "whoosh", 0.4)],
    "mlot": [(0.0, "wagon", 2.7), (1.7, "whoosh", 1.0), (2.7, "crack", 1.2), (2.7, "thud", 1.2), (2.95, "thud", 0.6), (3.0, "cough", 0.4)],
    "morze": [(0.2, "whoosh", 0.6), (2.6, "rumble", 2.8)],
    "xufu": [(0.0, "water", 10.8)],
    "rtec": [(0.3, "knock", 0.5), (3.6, "coin", 0.5), (5.3, "coin", 0.5), (7.0, "coin", 0.5)],
    "przejscia": [(0.0, "steps", 11.9)],
    "meteor": [(0.7, "whoosh", 1.0), (1.6, "thud", 1.4), (1.6, "crack", 0.9), (1.6, "rumble", 2.4), (1.7, "fire", 4.0), (3.0, "whoosh", 0.4)],
    "kopiec": [(0.4, "thud", 0.5), (0.4, "rumble", 2.2), (2.2, "steps", 6.0)],
    "twarze": [(5.8, "knock", 0.7)],
    "podroz": [(0.0, "wagon", 8.0), (2.2, "cough", 0.8), (4.4, "cough", 0.8), (6.6, "cough", 0.9)],
    "koniec": [(0.9, "cough", 1.0), (2.0, "cough", 1.0), (2.9, "rattle", 1.0), (4.2, "gong", 0.8)],
    "ryby": [(0.0, "wagon", 12.0), (4.9, "whoosh", 0.3), (5.65, "splash", 0.55), (5.95, "splash", 0.25), (6.3, "splash", 0.15),
             (7.4, "whoosh", 0.3), (8.25, "splash", 0.5)],
    "list": [(0.6, "flap", 3.6), (1.9, "whoosh", 0.4), (2.6, "knock", 0.7), (2.65, "stun", 1.0), (5.2, "whoosh", 0.35),
             (5.6, "sword", 0.45), (6.6, "sword", 0.9), (6.65, "thud", 0.5), (6.85, "rattle", 1.2), (7.9, "cough", 0.4)],
    "huhai": [(1.6, "drum", 0.5), (1.6, "whoosh", 0.4)],
    "powstanie": [(0.4, "march", 11.0), (0.4, "drum", 0.9), (2.8, "crack", 0.8), (3.5, "crack", 0.8), (4.2, "crack", 0.8), (6.0, "drum", 0.8)],
    "upadek": [(0.4, "crack", 0.9), (0.9, "crack", 0.9), (1.4, "crack", 0.9), (1.0, "thud", 1.0), (1.2, "fire", 9.0),
               (2.4, "crack", 1.0), (2.9, "whoosh", 0.6), (5.5, "fire", 5.0), (6.0, "rumble", 4.0)],
    "cisza": [(0.3, "whoosh", 0.3), (1.3, "whoosh", 0.3)],
    "studnia": [(0.54 + 0.9 * k, "thud", 0.5) for k in range(3)] + [(0.22 + 1.1 * k, "thud", 0.4) for k in range(3)]
               + [(3.2, "thud", 0.6), (3.3, "whoosh", 0.4), (5.0, "whoosh", 0.4), (5.6, "rumble", 1.2), (6.65, "thud", 0.3),
                  (7.2, "flap", 1.8)],
    "grobowiec": [(0.8, "whoosh", 0.3)] + [(0.4 + j * 0.16, "knock", 0.3) for j in range(14)] + [(3.0, "rumble", 4.0)],
})

# Markery i uwagi reżysera 16.11.2026 wieczorem; czasy jak w ujecia1.py / ujecia2.py (SKOK_SAM, SPADA_POWROT, OGNIE,
# SKOKI_PUSTE, QIN_TAB, DZIEKI).
ZDARZENIA.update({
    "sam": [(0.0, "march", 2.4), (1.25, "whoosh", 0.8)],  # chłopiec wyskakuje w górę za kadr
    "powrot": [(0.0, "wagon", 6.0), (0.12, "whoosh", 0.5), (0.62, "thud", 0.8), (0.62, "knock", 0.6)],  # spada do wozu
    "dary": [(2.0, "knock", 0.6)],  # bez zwoju na stole: tylko szkatuła
    "ognie": [(1.0, "fire", 5.0), (3.3, "fire", 4.0), (4.6, "fire", 3.0), (1.0, "whoosh", 0.3), (3.3, "whoosh", 0.25),
              (4.6, "whoosh", 0.2)],
    # cyklopi podskakują, odbijają się (stuk) i skaczą do wody (świst), plusk w chwili, gdy znikają za falą
    # (swiat._pod_woda dla ujecia2.NUREK_PUSTE: 1,00 s i 1,44 s)
    "puste": [(0.5, "thud", 0.25), (0.5, "whoosh", 0.35), (0.95, "thud", 0.25), (0.95, "whoosh", 0.35), (1.0, "splash", 0.7),
              (1.44, "splash", 0.75)],
    "qin": [(0.2, "march", 2.0), (3.1, "whoosh", 0.35), (3.35, "whoosh", 0.3), (6.0, "gong", 0.9), (6.2, "whoosh", 0.6),
            (6.4, "whoosh", 0.3)],
    "dzieki": [(0.35, "whoosh", 0.4), (0.65, "whoosh", 0.3), (1.25, "klaps", 0.35), (1.9, "whoosh", 0.4), (2.8, "klaps", 0.3)],
    # przegląd efektów (reżyser 16.11: „sprawdź, czy nie trzeba dodać kilku dźwięków efektów”): lalki wysuwające się zza
    # rampy i tabliczki z imionami szeleszczą papierem, wielki kanclerz wyrasta z niskim uderzeniem, płachta opada na
    # powóz z miękkim stukiem, o świcie dzwoni mały gong, cyklopi prężą muskuły z głuchym „bum”
    "handan": [(1.3, "whoosh", 0.25), (1.6, "whoosh", 0.15), (3.0, "whoosh", 0.2), (4.2, "whoosh", 0.15)],
    "regent": [(1.9, "whoosh", 0.2), (2.6, "whoosh", 0.35), (2.95, "drum", 0.35), (4.2, "whoosh", 0.15), (4.6, "whoosh", 0.15),
               (4.7, "whoosh", 0.15)],
    "spisek": [(0.4, "whoosh", 0.2), (0.9, "whoosh", 0.2), (1.6, "whoosh", 0.15), (2.8, "whoosh", 0.5), (3.85, "thud", 0.3)],
    "cisza": [(0.3, "whoosh", 0.3), (1.3, "whoosh", 0.3), (2.6, "gong_s", 0.35)],
    "xufu": [(0.0, "water", 10.8), (3.1, "drum", 0.25), (3.35, "drum", 0.22), (3.6, "drum", 0.25)],
})


# Dźwięk poprawia się punktowo (wytyczne 1.12): wszystkie zdarzenia filmu losują szum z jednego RNG po kolei, więc nowe
# zdarzenie w jednym ujęciu zmieniłoby efekty całej reszty filmu. Tu stoją zdarzenia ujęcia w takiej postaci, w jakiej
# były w pliku efektów wgranym do Studio przed pierwszą poprawką tego ujęcia: main() syntezuje je wspólnym RNG (te same
# losowania co w Studio), zostawia te, które są dalej w ZDARZENIA, a nowe zdarzenia ujęcia losuje z osobnego RNG
# (ziarno z klucza ujęcia). Wpis dopisuje się raz, przy pierwszej poprawce dźwięku ujęcia, i już się go nie zmienia —
# to on trzyma losowania reszty filmu; kolejne poprawki tego ujęcia zmieniają tylko ZDARZENIA.
W_STUDIO = {
    # markery i uwagi reżysera 16.11.2026 wieczorem (ujęcia 7, 8, 25, 51, 59, 79); stan pliku w Studio: efekty.py z c76c921
    "sam": [(0.0, "march", 2.4)],
    "powrot": [(0.0, "wagon", 6.0)],
    "dary": [(2.0, "knock", 0.6), (2.6, "knock", 0.5)],
    "ognie": [(0.5, "fire", 4.0), (1.6, "fire", 3.0), (2.8, "fire", 1.8)],
    "puste": [],
    "qin": [(0.2, "march", 2.0), (6.0, "gong", 0.9)],
    "handan": [], "regent": [], "spisek": [(2.8, "whoosh", 0.5)], "cisza": [(0.3, "whoosh", 0.3), (1.3, "whoosh", 0.3)],
    "xufu": [(0.0, "water", 10.8)],  # przegląd efektów 16.11 wieczorem (reżyser: „czy nie trzeba dodać kilku dźwięków”)
    "dzieki": [],  # nowe ujęcie 80: jego dźwięki z osobnego RNG, żeby bęben w muzyce (wspólny RNG po efektach) się nie zmienił
    # markery reżysera 16.11.2026 (ujęcia 26, 71, 72, 77); stan pliku w Studio: efekty.py z bfb55a5
    "sztylet": [(0.3, "whoosh", 0.35), (0.9, "whoosh", 0.4), (1.85, "knock", 0.5), (2.6, "sword", 0.8)],
    "ryby": [(0.0, "wagon", 12.0), (3.2, "whoosh", 0.3), (4.05, "splash", 0.5), (7.4, "whoosh", 0.3), (8.25, "splash", 0.5)],
    "list": [(0.6, "flap", 3.6), (1.9, "whoosh", 0.5), (2.8, "knock", 0.3), (6.6, "thud", 0.3)],
    "studnia": [(0.54 + 0.9 * k, "thud", 0.5) for k in range(3)] + [(0.22 + 1.1 * k, "thud", 0.4) for k in range(3)]
               + [(3.2, "thud", 0.6), (3.3, "whoosh", 0.4), (5.0, "whoosh", 0.4), (5.6, "rumble", 1.2)],
}


# Długość ujęcia w pliku w Studio, kiedy ujęcie trafiło do W_STUDIO, a potem zmieniło długość: długie dźwięki (ogień,
# marsz…) przycina koniec ujęcia, a liczba losowań zależy od długości dźwięku (np. int(2,9999 × 25) ≠ int(3,0 × 25)),
# więc stare zdarzenia trzeba policzyć ze starą długością, żeby reszta filmu miała te same losowania (16.11 wieczorem:
# ognie 4,6 → 9,0 s zmieniały szum w trzech następnych ujęciach).
W_STUDIO_SEC = {"ognie": 4.6, "qin": 12.2}


DLUGIE = ("march", "hooves", "fire", "water", "wagon", "steps", "dig", "roll", "rumble", "flap", "pisanie", "stun")


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
    if kind == "rumble":  # dudnienie ziemi (kopiec, wyspa, meteoryt)
        x = band(RNG.normal(0, 1, N(sec)), 30, 140) * 0.5
        return x * np.minimum(1, tt(N(sec)) / 0.4) * np.minimum(1, (sec - tt(N(sec))) / 0.6)
    if kind in ("flap", "pisanie", "stun"):
        n = N(sec)
        out = np.zeros(n)
        k = 0.0
        step = {"flap": 0.16, "pisanie": 0.22, "stun": 0.35}[kind]
        while k < sec - 0.1:
            if kind == "flap":  # skrzydła albo płótno flagi
                L = N(0.09)
                s_ = band(RNG.normal(0, 1, L), 300, 2500) * env(L, 0.01, 0.04) * 0.25
            elif kind == "pisanie":  # pędzel po deszczułce
                L = N(0.16)
                s_ = band(RNG.normal(0, 1, L), 2500, 7000) * np.sin(np.linspace(0, math.pi, L)) * 0.12
            else:  # ćwierkanie gwiazdek nad głową zamroczonego
                L = N(0.25)
                f = 2400 + 900 * np.sin(np.linspace(0, math.pi, L))
                s_ = np.sin(2 * math.pi * np.cumsum(f) / SR) * env(L, 0.01, 0.1) * 0.08
            i = N(k)
            out[i:i + len(s_)] += s_[:n - i]
            k += step * RNG.uniform(0.8, 1.2)
        return out
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


def dzwiek(at, kind, g, sec):
    if isinstance(g, tuple):  # (długość syntezy, ile z niej słychać): skrócenie dźwięku bez zmiany losowań reszty filmu
        s = long_sound(kind, min(g[0], sec - at))[:N(g[1])].copy()
        s[-N(0.05):] *= np.linspace(1, 0, N(0.05))
        return s
    return long_sound(kind, min(g, sec - at)) if kind in DLUGIE else SFX[kind]() * g


def dzwieki_ujecia(klucz, evs, sec):
    """Dźwięki zdarzeń ujęcia [(at, kind, g, próbki)]. Ujęcie z W_STUDIO: najpierw jego stare zdarzenia wspólnym RNG
    (zostają te, które są dalej w evs), potem nowe zdarzenia z osobnego RNG — reszta filmu ma te same losowania."""
    global RNG
    evs = [e for e in evs if e[0] < sec]
    if klucz not in W_STUDIO:
        return [(*e, dzwiek(*e, sec)) for e in evs]
    from collections import Counter
    dodatki = evs[len([e for e in ZDARZENIA.get(klucz, []) if e[0] < sec]):]  # przejścia i zmiana dekoracji
    zostaje, out = Counter(evs), []
    stary = W_STUDIO_SEC.get(klucz, sec)  # długość ujęcia, z jaką stare zdarzenia są w pliku w Studio
    for e in [e for e in W_STUDIO[klucz] if e[0] < stary] + dodatki:
        s = dzwiek(*e, stary if e not in dodatki else sec)
        if zostaje[e] and stary == sec:
            zostaje[e] -= 1
            out.append((*e, s))
        elif zostaje[e] and e in dodatki:
            zostaje[e] -= 1
            out.append((*e, s))
    wspolny, RNG = RNG, np.random.default_rng([7, zlib.crc32(klucz.encode())])
    try:
        for e in evs:
            if zostaje[e]:
                zostaje[e] -= 1
                out.append((*e, dzwiek(*e, sec)))
    finally:
        RNG = wspolny
    return out


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
        g = R.GRANICE[idx]  # przejścia: kurtyna między aktami, ściemnienie przy zmianie miejsca (render.przejscie)
        zam, dl, czekaj, otw = R.KURTYNA
        if g["ostatnie_aktu"] and idx < len(us) - 1:
            evs += [(sec - zam, "kurtyna_z", 1.0), (sec - zam + dl - 0.05, "klaps", 0.8)]
        elif g["pierwsze_aktu"] and idx > 0:
            evs += [(czekaj, "kurtyna_r", 1.0)]
        elif g["ostatnie_sceny"] and idx < len(us) - 1:
            evs += [(sec - R.CIEMNO, "whoosh", 0.18)]
        if klucz in R.BUDUJ:  # zmiana dekoracji: papier i drewno w rytm wjeżdżających elementów
            evs += [(d, "whoosh", 0.35) for d in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(d, "knock", 0.3) for d in (0.75, 1.05, 1.4, 1.7)]
        for at, kind, g, s in dzwieki_ujecia(klucz, evs, sec):
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
