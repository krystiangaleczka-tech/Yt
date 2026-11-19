"""Dźwięk filmu „Bonnie and Clyde: The Outlaws Made of Paper” bez lektora: muzyka (ścieżka Muzyka) i efekty (ścieżka Efekty).

Synteza w numpy, wzór: output/powstanie-japonii/efekty.py (kurtyna, klapki, dźwięki bazowe) — ale z brzmieniem Ameryki lat 30.
- Muzyka z tematów, nie z jednego tła: ragtime (fortepian stride, banjo, kontrabas, miotełki) w ucieczkach i żartach,
  blues (fortepian, harmonijka) w dzieciństwie i żałobie, folk (banjo, harmonijka) w drodze, temat łowcy Hamera (pizzicato
  w d-moll, tykanie zegara, trzy nuty fortepianu), napięcie (bicie serca, burdon), kataryniarski walc na jarmarku,
  bluegrass przy filmie z 1967, 8-bit przy grze. Tematy zmieniają się z akcją (CUES), przed szczytami muzyka milknie (CISZA).
- Efekty zsynchronizowane z rysunkiem bez przepisywania czasów: skrypt „przegląda” film (render.uloz co 0,08 s) z podsłuchem
  na funkcjach ujęć — auta (prędkość → silnik, syrena radiowozu), lalki (ruch → drewniane kroki lalek), błyski (strzał za
  parawanem albo flesz), tabliczki i podpisy (dźwięk zależny od napisu: „AGAIN?!” → wah-wah, „BEEP” → klakson),
  zawieszki dni, rekwizyty na nitkach. Do tego tło miejsca (dekoracja ujęcia + noc) i wydarzenia ręczne (ZDARZENIA).
- Głosu człowieka (śmiech, krzyk, tłum) tu nie ma: wytyczne 1.14 — tylko z nagrania/modelu mowy, osobno, po akceptacji.

uruchom:  python3 -I efekty.py      → dzwiek_en/muzyka.wav, dzwiek_en/efekty.wav (cały film, 44,1 kHz mono)
"""
import math
import os
import sys
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/bonnie-i-clyde/ujecia"))
from dane import okno_kwestii, ujecia  # noqa: E402

SR = 44100
OUT = Path(os.environ.get("DZWIEK_DO", HERE / "dzwiek_en"))
RNG = np.random.default_rng(19)


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


def kurtyna_zasuwa():
    return kurtyna_nowa(True)


def kurtyna_rozsuwa():
    return kurtyna_nowa(False)




# =====================================================================================================================
# INSTRUMENTY (synteza addytywna, wektorowo; nuty w pamięci podręcznej — te same wysokości wracają setki razy)
# =====================================================================================================================

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def _q(x, s=0.05):
    return round(round(x / s) * s, 3)


@lru_cache(maxsize=8192)
def _piano(m, dur, vel, honky):
    f = mtof(m)
    L = N(dur + 0.35)
    t = tt(L)
    tau0 = float(np.clip(1.5 * (262 / f) ** 0.6, 0.25, 3.0))
    ph = np.random.default_rng(int(m) * 7 + 1).uniform(0, 6.28, 40)
    out = np.zeros(L)
    for k in range(1, 13):
        fk = k * f * math.sqrt(1 + 0.0004 * k * k)
        if fk > 9000:
            break
        a = (0.45 + 0.5 * vel) ** (k - 1) / k ** 1.1
        tau = tau0 / (1 + 0.35 * (k - 1))
        for j, c in enumerate((-honky, honky) if honky else (0.0,)):
            out += a * np.sin(2 * math.pi * fk * 2 ** (c / 1200) * t + ph[2 * k + j]) * np.exp(-t / tau) * (0.5 if honky else 1.0)
    nh = N(0.02)
    out[:nh] += band(np.random.default_rng(int(m)).normal(0, 1, nh), 800, 5000) * env(nh, 0.001, 0.004) * 0.25
    out *= np.minimum(1, t / 0.002) * np.clip(1 - (t - dur) / 0.25, 0, 1)
    return out * vel * 0.2


def piano(m, dur=0.4, vel=0.6, honky=0.0):
    return _piano(int(m), _q(dur), _q(vel), float(honky))


@lru_cache(maxsize=4096)
def _banjo(m, vel):
    f = mtof(m)
    L = N(0.9)
    t = tt(L)
    ph = np.random.default_rng(int(m) + 3).uniform(0, 6.28, 20)
    out = np.zeros(L)
    for k in range(1, 17):
        if k * f > 10000:
            break
        out += (1 / k ** 0.7) * (1 + 0.6 * math.sin(k * 1.3)) * np.sin(2 * math.pi * k * f * t + ph[k]) * np.exp(-t / (0.45 / (1 + 0.22 * k)))
    npick = N(0.012)
    out[:npick] += band(np.random.default_rng(int(m) + 9).normal(0, 1, npick), 2000, 7000) * 0.5
    return out * np.minimum(1, t / 0.001) * vel * 0.085


def banjo(m, vel=0.5):
    return _banjo(int(m), _q(vel))


@lru_cache(maxsize=4096)
def _bas(m, vel, dur):
    f = mtof(m)
    L = N(max(dur, 0.3) + 0.2)
    t = tt(L)
    out = sum(a * np.sin(2 * math.pi * k * f * t) * np.exp(-t / (0.6 / (1 + 0.5 * (k - 1)))) for k, a in ((1, 1.0), (2, 0.5), (3, 0.25), (4, 0.12)))
    out += np.sin(2 * math.pi * 2 * f * t) * np.exp(-t / 0.02) * 0.3
    out *= np.minimum(1, t / 0.006) * np.clip(1 - (t - dur) / 0.15, 0, 1)
    return out * vel * 0.3


def bas(m, vel=0.6, dur=0.5):
    return _bas(int(m), _q(vel), _q(dur))


def _dech(m, dur, vel, formanty, vib=14.0, bend=0.0, atak=0.07, szum=0.04, seed=0):
    """Instrument dęty (harmonijka, saksofon, puzon): fala z harmonicznych ważonych formantami, vibrato, podciągnięcie."""
    f0 = mtof(m)
    L = N(dur + 0.15)
    t = tt(L)
    cents = vib * np.sin(2 * math.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    if bend:
        cents += bend * np.clip(1 - t / 0.18, 0, 1)
    f = f0 * 2 ** (cents / 1200)
    ph = 2 * math.pi * np.cumsum(f) / SR
    out = np.zeros(L)
    for k in range(1, 18):
        if k * f0 > 9000:
            break
        w = sum(g * math.exp(-((k * f0 - fc) / bw) ** 2) for fc, bw, g in formanty) + 0.25 / k
        out += w * np.sin(k * ph)
    out /= np.abs(out).max() + 1e-9
    out += band(np.random.default_rng(seed + int(m)).normal(0, 1, L), 900, 4000) * szum
    e = np.minimum(1, t / atak) * np.clip(1 - (t - dur) / 0.12, 0, 1)
    return out * e * vel


@lru_cache(maxsize=2048)
def _harmonijka(m, dur, vel, bend):
    return _dech(m, dur, vel, ((1400, 900, 1.0), (2600, 700, 0.5)), bend=-100 if bend else 0, seed=11) * 0.16


def harmonijka(m, dur=1.0, vel=0.5, bend=True):
    return _harmonijka(int(m), _q(dur), _q(vel), bool(bend))


@lru_cache(maxsize=1024)
def _saks(m, dur, vel):
    return _dech(m, dur, vel, ((650, 300, 1.0), (1500, 500, 0.6), (2800, 600, 0.25)), vib=18, bend=-60, atak=0.04, szum=0.06, seed=21) * 0.17


def saks(m, dur=0.4, vel=0.6):
    return _saks(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=1024)
def _calliope(m, dur, vel):
    f = mtof(m)
    L = N(dur + 0.1)
    t = tt(L)
    out = sum(a * np.sin(2 * math.pi * k * f * t) for k, a in ((1, 1.0), (2, 0.55), (3, 0.3), (4, 0.12)))
    out *= 1 + 0.12 * np.sin(2 * math.pi * 6.5 * t)
    out += band(np.random.default_rng(int(m)).normal(0, 1, L), 1500, 6000) * 0.05
    return out * np.minimum(1, t / 0.02) * np.clip(1 - (t - dur) / 0.06, 0, 1) * vel * 0.12


def calliope(m, dur=0.4, vel=0.5):
    return _calliope(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=1024)
def _chip(m, dur, vel, duty):
    f = mtof(m)
    L = N(dur + 0.03)
    t = tt(L)
    x = np.where((t * f) % 1.0 < duty, 1.0, -1.0)
    return x * np.minimum(1, t / 0.003) * np.clip(1 - (t - dur) / 0.03, 0, 1) * np.exp(-t / 1.5) * vel * 0.08


def chip(m, dur=0.2, vel=0.5, duty=0.5):
    return _chip(int(m), _q(dur, 0.02), _q(vel), duty)


@lru_cache(maxsize=512)
def _blacha(m, dur, vel):
    """Trąbka fanfary: jasność rośnie przy ataku."""
    f = mtof(m)
    L = N(dur + 0.12)
    t = tt(L)
    vib = 1 + 0.004 * np.sin(2 * math.pi * 5.5 * t) * np.clip((t - 0.2) / 0.2, 0, 1)
    ph = 2 * math.pi * np.cumsum(f * vib) / SR
    out = sum((1 / k) * (1 - np.exp(-t / (0.012 * k))) * np.sin(k * ph) for k in range(1, 13) if k * f < 9000)
    return out * np.minimum(1, t / 0.015) * np.clip(1 - (t - dur) / 0.1, 0, 1) * vel * 0.14


def blacha(m, dur=0.3, vel=0.6):
    return _blacha(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=None)
def miotelka(vel=0.5):
    n = N(0.18)
    return band(np.random.default_rng(31).normal(0, 1, n), 2500, 9000) * env(n, 0.025, 0.07) * 0.12 * vel


@lru_cache(maxsize=None)
def werbel(vel=0.5):
    n, t = N(0.22), tt(N(0.22))
    return (band(np.random.default_rng(32).normal(0, 1, n), 1500, 7000) * np.exp(-t / 0.07) * 0.32
            + np.sin(2 * math.pi * 190 * t) * np.exp(-t / 0.04) * 0.2) * vel


@lru_cache(maxsize=None)
def stopa(vel=0.5):
    return drum(0.4, 52) * 0.5 * vel


@lru_cache(maxsize=None)
def obrecz(vel=0.5):
    return knock(1700, 0.06) * 0.6 * vel


@lru_cache(maxsize=None)
def tyk(vel=0.5, f=2600):
    return knock(f, 0.05) * 0.3 * vel


# =====================================================================================================================
# MUZYKA: tematy (style) na siatce taktów; CUES mówią, który temat gra od którego ujęcia
# =====================================================================================================================

Q_ = {"M": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "o7": (0, 3, 6, 9), "m7": (0, 3, 7, 10)}


def akord(root, q, lo, hi):
    """Dźwięki akordu w przedziale [lo, hi) (wszystkie oktawy)."""
    pc = {(root + i) % 12 for i in Q_[q]}
    return [m for m in range(lo, hi) if m % 12 in pc]


class Pasmo:
    """Bufor tematu: nuty wstawiane w czasie bezwzględnym (sekundy od początku tematu). mapa — funkcja „czas muzyczny →
    czas filmu”: temat przyspiesza i zwalnia bez zmiany wysokości nut (nuta trwa tyle samo, zmienia się odstęp między nutami)."""

    def __init__(self, sec, mapa=None):
        self.x = np.zeros(N(sec + 3.0))
        self.mapa = mapa

    def __call__(self, at, s, g=1.0):
        if at < 0:
            return
        if self.mapa is not None:
            at = self.mapa(at)
        i = N(at)
        n = len(self.x)
        if i >= n:
            return
        self.x[i:i + len(s)] += s[:n - i] * g


def _melodia(r, chord, lo, hi, last):
    pool = akord(*chord, lo, hi)
    if not pool:
        return last
    near = sorted(pool, key=lambda m: abs(m - last))[:4]
    return int(r.choice(near))


WZORY_RAG = [((0, .5), (.5, .5), (1.5, 1), (3, .5), (3.5, .5)), ((.5, 1), (1.5, .5), (2, .5), (2.5, 1), (3.5, .5)),
             ((0, .75), (.75, .75), (1.5, .5), (2, 1.5), (3.5, .5)), ((0, .5), (.5, .5), (1, .5), (1.5, .5), (2, .5), (2.5, .5), (3, 1)),
             ((0, 1.5), (1.5, .5), (2, .5), (2.5, .5), (3, 1))]


def s_rag(P, sec, r, o):
    """Ragtime: stride fortepianu (bas–akord), synkopowana melodia, banjo na słabe części, kontrabas, miotełki."""
    bpm, key = o.get("bpm", 152), o.get("key", 60)
    b = 60.0 / bpm
    prog = [(0, "M"), (0, "M"), (5, "M"), (6, "o7"), (0, "M"), (9, "7"), (2, "7"), (7, "7")]
    t0 = 0.0
    if o.get("fanfara"):
        for d, m, L in ((0.0, 67, 0.16), (0.2, 67, 0.16), (0.4, 67, 0.16), (0.6, 72, 1.3)):
            P(d, blacha(m, L, 0.7))
        for m in (76, 79):
            P(0.6, blacha(m, 1.3, 0.55))
        for k in range(12):
            P(0.05 * k, werbel(0.25 + 0.04 * k))
        P(0.6, stopa(0.9))
        t0 = 2.2
    last, bar = 76, 0
    while t0 + bar * 4 * b < sec:
        tb = t0 + bar * 4 * b
        root, q = prog[bar % 8]
        kr = (key + root) % 12
        brk = bar % 16 == 15  # co 16 taktów takt „stop-time”: sama melodia
        if not brk:
            for beat in (0, 2):
                bm = 36 + kr + (7 if beat == 2 and q != "o7" else 0)
                P(tb + beat * b, piano(bm, b * 0.9, 0.5))
            voic = akord(kr, q, 52, 65)[:4]
            for beat in (1, 3):
                for m in voic:
                    P(tb + beat * b, piano(m, b * 0.45, 0.32, 6))
            for beat in range(4):
                for j, m in enumerate(akord(kr, q, 55, 68)[:3]):
                    P(tb + (beat + 0.5) * b + 0.012 * j, banjo(m, 0.32))
            walk = [36 + kr + 12, 36 + kr + 12 + (Q_[q][1]), 36 + kr + 12 + 7, 36 + (key + prog[(bar + 1) % 8][0]) % 12 + 12 - 1]
            for beat, m in enumerate(walk):
                P(tb + beat * b, bas(m, 0.45, b * 0.85))
            for beat in range(4):
                P(tb + beat * b, miotelka(0.6))
                if beat in (1, 3):
                    P(tb + beat * b, werbel(0.32))
        for pos, L in WZORY_RAG[int(r.integers(len(WZORY_RAG)))]:
            last = _melodia(r, (kr, q), 67, 86, last)
            P(tb + pos * b, piano(last, L * b * 0.95, float(r.uniform(0.55, 0.72)), 4))
            if r.random() < 0.3:
                P(tb + pos * b, piano(last - 12, L * b * 0.9, 0.4, 4))
        bar += 1


def s_folk(P, sec, r, o):
    """W drodze: banjo w rolkach, kontrabas na raz i trzy, harmonijka długimi nutami co kilka taktów."""
    bpm, key = o.get("bpm", 104), o.get("key", 55)
    b = 60.0 / bpm
    prog = [(0, "M"), (0, "M"), (5, "M"), (0, "M"), (7, "7"), (7, "7"), (0, "M"), (0, "M")]
    if o.get("szybko"):
        prog = [(0, "M")] * 4 + [(9, "m"), (9, "m"), (7, "M"), (7, "M")]
    bar = 0
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        root, q = prog[bar % 8]
        kr = (key + root) % 12
        tony = akord(kr, q, 62, 80)[:4]
        rolka = (0, 1, 2, 0, 1, 2, 0, 3) if bar % 2 else (0, 2, 1, 3, 0, 2, 1, 2)
        for j, idx in enumerate(rolka):
            P(tb + j * b / 2, banjo(tony[idx % len(tony)], 0.42 if j % 2 == 0 else 0.3))
        for beat, d in ((0, 0), (2, 7)):
            P(tb + beat * b, bas(31 + kr + d + 12, 0.5, b * 0.9))
        if o.get("szybko"):
            for beat in (1, 3):
                P(tb + beat * b, miotelka(0.5))
        elif not o.get("bez_harmonijki"):
            if bar % 4 == 0:
                P(tb + 0.1, harmonijka(int(r.choice(akord(kr, q, 67, 80))), 2.6 * b, 0.4))
            elif bar % 4 == 2 and r.random() < 0.7:
                m = int(r.choice(akord(kr, q, 67, 80)))
                for j, d in enumerate((0, 2, -1)):
                    P(tb + j * 0.5 * b, harmonijka(m + d, 0.45 * b if j < 2 else 1.4 * b, 0.32, j == 0))
        bar += 1


BLUES = [0, 0, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7]
SKALA_BLUES = (0, 3, 5, 6, 7, 10)


def s_blues(P, sec, r, o):
    """Powolny blues z harmonijką: shuffle lewej ręki, zagrywki prawej, harmonijka z podciągnięciem w taktach 1, 5, 9."""
    bpm, key = o.get("bpm", 66), o.get("key", 53)
    b = 60.0 / bpm
    sw = 2.0 / 3.0
    bar = 0
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        kr = (key + BLUES[bar % 12]) % 12
        for beat in range(4):
            for d, v in ((0, 0.28), (sw, 0.2)):
                P(tb + (beat + d) * b, piano(41 + kr, b * 0.5, v))
                P(tb + (beat + d) * b, piano(41 + kr + (7 if (beat + (d > 0)) % 2 == 0 else 9), b * 0.5, v * 0.8))
            P(tb + beat * b, bas(29 + kr + 12 + (0, 4, 7, 9)[beat], 0.32, b * 0.9))
        if bar % 4 == 0 and not o.get("bez_harmonijki"):
            m = 65 + (kr + int(r.choice((7, 10, 12))) - 65) % 12
            P(tb + 0.05, harmonijka(m, 2.6 * b, 0.42))
        elif r.random() < 0.65:
            sk = [m for m in range(65, 80) if (m - key) % 12 in SKALA_BLUES]
            m = int(r.choice(sk))
            for j in range(int(r.integers(3, 6))):
                m = int(sk[int(np.clip(sk.index(m) + r.choice((-2, -1, -1, 1)), 0, len(sk) - 1))])
                P(tb + (1 + j * sw) * b, piano(m, b * (0.6 if j < 3 else 1.5), float(r.uniform(0.38, 0.5))))
        bar += 1


def s_lowca(P, sec, r, o):
    """Temat Hamera: pizzicato w d-moll ósemkami, zegar na każdą ćwierćnutę, trzy nuty fortepianu co dwa takty."""
    bpm, key = o.get("bpm", 84), o.get("key", 50)
    b = 60.0 / bpm
    prog = [(0, "m"), (0, "m"), (8, "M"), (7, "7")]
    bar = 0
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        root, q = prog[bar % 4]
        r0 = 38 + (key + root - 2) % 12
        t3 = Q_[q][1]
        for j, d in enumerate((0, 0, t3, 0, -5, 0, t3, 7)):
            P(tb + j * b / 2, bas(r0 + d, 0.5 if j % 2 == 0 else 0.36, b * 0.35))
        for beat in range(4):
            P(tb + beat * b, tyk(0.6 if beat % 2 == 0 else 0.45, 2600 if beat % 2 == 0 else 2150))
        P(tb + 3 * b, obrecz(0.28))
        if bar % 2 == 0 and not o.get("cicho"):
            motyw = {0: (57, 62, 65), 8: (58, 62, 65), 7: (57, 61, 64)}[root]
            for j, m in enumerate(motyw):
                P(tb + j * 0.5 * b, piano(m, b * (0.45 if j < 2 else 2.4), 0.5))
        bar += 1
    n = len(P.x)
    tl = tt(n)
    P.x += np.sin(2 * math.pi * mtof(38) * tl) * 0.012 * np.minimum(1, tl / 2)


def s_napiecie(P, sec, r, o):
    """Napięcie: bicie serca (lub-dub), burdon D2+A2 z dudnieniem, tremolo klastra, rzadkie wysokie nuty; narasta."""
    bpm0, bpm1 = o.get("bpm", (60, 60)) if isinstance(o.get("bpm"), tuple) else (o.get("bpm", 60),) * 2
    t, k = 0.0, 0
    while t < sec:
        bpm = bpm0 + (bpm1 - bpm0) * t / max(sec, 1)
        b = 60.0 / bpm
        cr = 0.6 + 0.4 * t / max(sec, 1)
        P(t, stopa(0.75 * cr))
        P(t + 0.28 * b, stopa(0.45 * cr))
        if k % 8 == 4:
            P(t, piano(int(r.choice((74, 75, 81))), 2.0, 0.26))
        t += b
        k += 1
    n = len(P.x)
    tl = tt(n)
    cres = np.clip(0.55 + 0.45 * tl / max(sec, 1), 0, 1) * np.minimum(1, tl / 1.5)
    dr = (np.sin(2 * math.pi * mtof(38) * tl) + 0.6 * np.sin(2 * math.pi * (mtof(45) + 0.7) * tl)) * 0.02
    tr = (np.sin(2 * math.pi * mtof(62) * tl) + np.sin(2 * math.pi * mtof(63) * tl)) * 0.008 * (0.5 + 0.5 * np.sin(2 * math.pi * 8 * tl))
    P.x += (dr + tr) * cres


def s_mrok(P, sec, r, o):
    """Mrok: rzadkie akordy molowe nisko (a–F–d–E), burdon."""
    b = 60.0 / o.get("bpm", 56)
    prog = [(57, "m"), (53, "M"), (50, "m"), (52, "M")]
    bar = 0
    while bar * 4 * b < sec:
        root, q = prog[bar % 4]
        for m in akord(root % 12, q, 45, 61)[:4]:
            P(bar * 4 * b, piano(m, 3.6 * b, 0.33))
        P(bar * 4 * b, bas(root - 12 if root - 12 >= 33 else root, 0.32, 3.6 * b))
        bar += 1
    n = len(P.x)
    tl = tt(n)
    P.x += np.sin(2 * math.pi * mtof(33) * tl) * 0.014 * np.minimum(1, tl / 2)


def s_praca(P, sec, r, o):
    """Pieśń przy pracy (Eastham): ciężkie uderzenia na raz i trzy, burdon E, harmonijka woła frazami pentatoniki."""
    b = 60.0 / o.get("bpm", 72)
    penta = (64, 67, 69, 71, 74)
    bar = 0
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        for beat in (0, 2):
            P(tb + beat * b, thud(0.5) * 0.55)
            P(tb + beat * b, knock(170, 0.2) * 0.4)
        P(tb, bas(40, 0.45, 3.6 * b))
        if bar % 2 == 0:
            fr = [int(r.choice(penta)) for _ in range(3)]
            for j, m in enumerate(fr):
                P(tb + (0.5 + j) * b, harmonijka(m, b * (0.8 if j < 2 else 1.8), 0.34, j == 0))
        bar += 1


def s_jarmark(P, sec, r, o):
    """Kataryniarski walc (diabelski młyn): um-pa-pa i melodia organów parowych."""
    b = 60.0 / o.get("bpm", 168)
    prog = [(0, "M"), (0, "M"), (7, "7"), (7, "7"), (7, "7"), (7, "7"), (0, "M"), (0, "M")]
    last, bar = 76, 0
    while bar * 3 * b < sec:
        tb = bar * 3 * b
        root, q = prog[bar % 8]
        kr = (60 + root) % 12
        P(tb, calliope(48 + kr, b * 0.9, 0.5))
        for beat in (1, 2):
            for m in akord(kr, q, 60, 72)[:3]:
                P(tb + beat * b, calliope(m, b * 0.5, 0.28))
        for pos, L in ((0, 1), (1, 2)) if bar % 2 else ((0, 2), (2, 1)):
            last = _melodia(r, (kr, q), 72, 88, last)
            P(tb + pos * b, calliope(last, L * b * 0.95, 0.42))
        bar += 1


def s_chip(P, sec, r, o):
    """Gra 8-bit: arpeggio szesnastkami, melodia ósemkami, perkusja z szumu."""
    b = 60.0 / o.get("bpm", 150)
    prog = [(0, "M"), (9, "m"), (5, "M"), (7, "M")]
    last, bar = 76, 0
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        root, q = prog[bar % 4]
        kr = (60 + root) % 12
        arp = akord(kr, q, 60, 76)[:3]
        for j in range(16):
            P(tb + j * b / 4, chip(arp[j % 3], b / 4 * 0.9, 0.35, 0.25))
        for j in range(8):
            if r.random() < 0.8:
                last = _melodia(r, (kr, q), 72, 90, last)
                P(tb + j * b / 2, chip(last, b / 2 * 0.85, 0.5, 0.5))
        for beat in range(4):
            P(tb + beat * b, stopa(0.5) if beat % 2 == 0 else werbel(0.4))
        bar += 1


# Styl → (funkcja, zamierzona różnica głośności w dB). Każdy temat jest najpierw wyrównany do tej samej głośności
# (MUZYKA_DB), dopiero potem dostaje swoją różnicę: tematy różnią się najwyżej o ok. 3 dB i tylko celowo
# (przegląd 19.11: „czemu muzyka raz gra ciszej, raz głośniej?” — rag grał o 6–7 dB głośniej od folku i mroku).
STYLE = {"rag": (s_rag, 0.0), "folk": (s_folk, 0.0), "blues": (s_blues, 0.0), "lowca": (s_lowca, 0.0), "napiecie": (s_napiecie, 0.5),
         "mrok": (s_mrok, -1.5), "praca": (s_praca, 0.0), "jarmark": (s_jarmark, 0.0), "chip": (s_chip, -0.5)}
MUZYKA_DB = -19.5     # RMS tematu poza kwestią lektora
CICHO_DB = -2.5       # opcja „cicho” (zasiew motywu łowcy)
POD_KWESTIA_MUZYKA, POD_KWESTIA_EFEKTY = -8.0, -5.0

# Od którego ujęcia gra który temat (do następnego wpisu). Opcje: bpm, key, fanfara, szybko, cicho, bez_harmonijki.
CUES = [
    ("zap_wellington_most", "cisza", {}), ("tytul", "rag", {"fanfara": True}), ("obietnica", "lowca", {"cicho": True}),
    ("wagon", "blues", {}), ("ohio", "rag", {"bpm": 132, "key": 62}), ("eastham", "praca", {}), ("eastham_rura", "napiecie", {}),
    ("palce", "praca", {}), ("parol", "blues", {"bez_harmonijki": True}),
    ("akt2", "rag", {"bpm": 156, "key": 55}), ("hillsboro", "mrok", {}), ("matka_obietnica", "folk", {}), ("atoka", "rag", {"bpm": 160, "key": 57}),
    ("wd", "rag", {"bpm": 150, "key": 55}),
    ("joplin_walka", "napiecie", {"bpm": (84, 100)}), ("joplin_ofiary", "mrok", {}), ("kiosk", "rag", {"bpm": 160}), ("teczka_zasiew", "lowca", {"cicho": True}),
    ("plakaty", "rag", {"bpm": 150}),
    ("wellington_noc", "napiecie", {"bpm": (70, 96)}), ("wellington_bonnie", "mrok", {}), ("farma", "folk", {"bez_harmonijki": True}),
    ("drzewo", "rag", {"bpm": 150, "key": 55}), ("noszenie", "folk", {}), ("platte", "napiecie", {"bpm": (90, 110)}), ("dexfield", "mrok", {}),
    ("przeprawa", "napiecie", {"bpm": (80, 90)}), ("wd_odchodzi", "blues", {}), ("sowers", "rag", {"bpm": 168, "key": 57}),
    ("odbicie", "napiecie", {"bpm": (80, 110)}), ("straznik", "mrok", {}), ("simmons", "lowca", {"cicho": True}), ("hamer", "lowca", {}),
    ("poscigi", "rag", {"bpm": 170, "key": 55}), ("hak_szuflada", "lowca", {}),
    ("grapevine", "folk", {"bpm": 92, "bez_harmonijki": True}), ("grapevine_cien", "cisza", {}), ("tullis", "blues", {"bpm": 60}),
    ("gazety_zle", "mrok", {}), ("listy_gon", "lowca", {}), ("commerce", "mrok", {}), ("boyd", "folk", {"bpm": 96}), ("prasa_cygaro", "lowca", {}),
    ("methvin", "lowca", {}), ("wiersz", "blues", {"bpm": 60}), ("shreveport", "lowca", {}), ("noc", "napiecie", {"bpm": (54, 60)}),
    ("zasadzka_rano", "napiecie", {"bpm": (62, 92)}), ("zasadzka", "cisza", {}), ("dym", "mrok", {"bpm": 48}),
    ("pamiatki", "mrok", {}), ("pogrzeby", "blues", {"bpm": 56, "bez_harmonijki": True}), ("auto_jarmark", "jarmark", {}),
    ("blanche_po", "blues", {"bpm": 62}), ("hamer_ganek", "lowca", {}), ("film_hamer", "folk", {"bpm": 176, "szybko": True}),
    ("gra", "chip", {}), ("koniec", "blues", {"bpm": 58}), ("dzieki", "rag", {"bpm": 156}),
]

# Cisza muzyki przed szczytem (od, do — sekundy od początku ujęcia); po niej muzyka wraca głośniej (powrot=True) albo zwyczajnie.
CISZA = {"wellington_most": (0.0, 1.5, True), "eastham_rura": (4.3, 6.4, False), "hillsboro": (3.6, 6.0, False),
         "atoka": (5.8, 9.5, False), "joplin_walka": (3.9, 5.6, False), "dym": (0.0, 6.0, False), "odbicie": (3.0, 4.6, False),
         "commerce_cien": (0.0, 7.0, False), "przysiega": (2.1, 2.9, True)}


# ---- tempo z cięć (reżyser 20.11: „powinno liczyć tempo cięć”) ----
# Tempo montażu (60 / długość ujęcia, wygładzone) względem mediany filmu daje mnożnik tempa tematu:
# szybkie cięcia → temat szybciej, długie ujęcia → wolniej. Wysokość nut się nie zmienia (Pasmo.mapa).
TEMPO_WYKL, TEMPO_MIN, TEMPO_MAX = 0.5, 0.85, 1.2


def gestosc_ciec(ciecia, total, krok=0.25, sigma=5.0):
    """Tempo montażu w czasie filmu (siatka co `krok` s): 60 / długość bieżącego ujęcia, wygładzone gaussem (sigma s).
    W obrębie ujęcia stałe, między ujęciami przechodzi płynnie — muzyka nie „kołysze się” od cięcia do cięcia."""
    tg = np.arange(0.0, total + krok, krok)
    c = np.asarray(sorted(ciecia) + [total])
    dl = np.diff(c)
    idx = np.clip(np.searchsorted(c, tg, side="right") - 1, 0, len(dl) - 1)
    raw = 60.0 / np.maximum(dl[idx], 0.3)
    k = np.arange(-int(3 * sigma / krok), int(3 * sigma / krok) + 1) * krok
    g = np.exp(-0.5 * (k / sigma) ** 2)
    g /= g.sum()
    pad = len(k) // 2
    sm = np.convolve(np.pad(raw, pad, mode="edge"), g, mode="valid")
    return tg, sm


def mapa_tempa(a0, sec, tg, cpm, ref):
    """(czas muzyczny potrzebny na odcinek, funkcja czas muzyczny → czas od początku tematu)."""
    t_real = np.arange(0.0, sec + 0.05, 0.05)
    r = np.clip((np.interp(a0 + t_real, tg, cpm) / ref) ** TEMPO_WYKL, TEMPO_MIN, TEMPO_MAX)
    m = np.concatenate([[0.0], np.cumsum((r[1:] + r[:-1]) / 2 * np.diff(t_real))])
    return float(m[-1]), (lambda at: float(np.interp(at, m, t_real, right=t_real[-1] + (at - m[-1]))))


# ---- zmiana tematu na cięciu (reżyser 20.11: „zmiana tematu też powinna być”): stary temat kończy się na cięciu, nowy
# zaczyna się na nim od mocnej części taktu z akcentem; wcześniej przenikały się przez pół sekundy niezależnie od obrazu ----
CIECIE_WYJSCIE, CIECIE_WEJSCIE = 0.12, 0.03

# ---- gagi: muzyka robi przystanek na puencie gagu, żeby jego dźwięk wybrzmiał (Podręcznik → Humor i gagi). Sekundy od
# początku ujęcia — chwila puenty, a nie początek gagu. Lekko: −9 dB na 0,6 s, bez muzycznych „mickey-mousingów” na każdym
# kroku (przy 46 gagach muzyka by się jąkała).
GAG_PRZYSTANEK_DB, GAG_PRZYSTANEK_S = -9.0, 0.6
GAG_PUENTA = {"wprowadzenie2": 1.6, "zdjecie": 4.25, "hak_cygaro": 2.6, "indyki": 5.0, "poezja": 2.3, "slub": 7.7, "kawiarnia": 7.0,
              "kuchnia": 9.5, "akt2": 7.3, "stacja": 6.6, "wd": 6.4, "joplin_dom": 9.2, "ciemnia": 5.0, "kiosk": 9.9, "darby_auto": 2.0,
              "darby_tyl": 9.6, "darby_puszczeni": 5.3, "oboz": 4.4, "list_ford": 6.4, "wd_odchodzi": 6.4, "rodziny": 9.0, "dzien1": 4.6,
              "hamer_motel": 8.85, "dzien20": 11.45, "mapa": 6.1, "listy_gon": 9.4, "prasa_cygaro": 5.6, "noc": 10.6, "kanapka": 5.3,
              "auto_jarmark": 8.0, "gra": 6.85, "dzieki": 8.25, "wagon": 11.3, "prasa": 6.9, "matka_obietnica": 9.8, "buck": 11.5,
              "joplin_karty": 10.0, "plakaty": 5.0, "farma": 5.15, "drzewo": 8.9, "simmons": 3.25, "hamer": 7.4, "podkreslenie": 6.2,
              "methvin": 11.9, "pozegnanie": 3.8, "shreveport": 11.1, "posse": 11.75}


def muzyka(total, starts, durs, voice, ciecia=None):
    n = N(total)
    out = np.zeros(n)
    ciecia = sorted(starts.values()) if ciecia is None else ciecia
    tg, cpm = gestosc_ciec(ciecia, total)
    ref = float(np.median(cpm[(tg > 10) & (tg < total - 10)]))
    global TEMPA
    TEMPA = {}
    for c, (klucz, styl, o) in enumerate(CUES):
        if klucz not in starts or styl == "cisza":
            continue
        a0 = starts[klucz]
        nast = [starts[k] for k, _, _ in CUES[c + 1:] if k in starts]
        a1 = min(nast) if nast else total
        fn, odchyl = STYLE[styl]
        sec = a1 - a0 + CIECIE_WYJSCIE
        dl_muz, mapa = mapa_tempa(a0, sec, tg, cpm, ref)
        TEMPA[klucz] = round(dl_muz / sec, 3)
        P = Pasmo(sec, mapa)
        fn(P, dl_muz + 0.5, np.random.default_rng(100 + c), o)
        P(0.0, stopa(0.9) * 1.3)  # akcent na cięciu: nowy temat wchodzi mocną częścią taktu
        x = P.x[:N(sec)]
        L = len(x)
        # wyrównanie: każdy temat tak samo głośny (RMS bez cichych brzegów), plus zamierzona różnica stylu
        srodek = x[N(0.5):max(N(0.5) + 1, L - N(0.6))]
        rms = float(np.sqrt(np.mean(srodek ** 2))) + 1e-9
        g = 10 ** ((MUZYKA_DB + odchyl + (CICHO_DB if o.get("cicho") else 0.0)) / 20) / rms
        tl = tt(L)
        fade = np.minimum(1, tl / CIECIE_WEJSCIE) * np.clip((sec - tl) / CIECIE_WYJSCIE, 0, 1)
        i0 = N(a0)
        out[i0:i0 + L] += (x * fade * g)[:n - i0]
    # cisza przed szczytami
    gain = np.ones(n)
    for klucz, (a, b, powrot) in CISZA.items():
        if klucz not in starts:
            continue
        i0, i1 = max(0, N(starts[klucz] + a)), min(n, N(starts[klucz] + b))
        r = N(0.12)
        gain[i0:i1] = 0.0
        gain[max(0, i0 - r):i0] = np.minimum(gain[max(0, i0 - r):i0], np.linspace(1, 0, i0 - max(0, i0 - r)))
        j = min(n, i1 + N(2.5))
        gain[i1:j] = (np.linspace(1.5, 1.0, j - i1) if powrot else np.linspace(0, 1, j - i1))
    out *= gain
    # przystanek na puencie gagu
    gg = np.ones(n)
    lo = 10 ** (GAG_PRZYSTANEK_DB / 20)
    for klucz, tp in GAG_PUENTA.items():
        if klucz not in starts:
            continue
        a = starts[klucz] + tp
        i0, i1, i2 = N(a - 0.06), N(a + GAG_PRZYSTANEK_S), N(a + GAG_PRZYSTANEK_S + 0.5)
        if i0 < 0 or i2 >= n:
            continue
        gg[i0:i1] = np.minimum(gg[i0:i1], lo)
        gg[i1:i2] = np.minimum(gg[i1:i2], np.linspace(lo, 1.0, i2 - i1))
    out *= gg
    out *= sciszanie(voice, POD_KWESTIA_MUZYKA)
    return out


TEMPA = {}


def sciszanie(voice, db, przerwa=3.0, przed=0.25, wejscie=0.3, wyjscie=0.9):
    """Łagodne ściszenie pod kwestie lektora: przerwy krótsze niż `przerwa` s zostają ściszone (muzyka nie podskakuje
    między zdaniami), ściszenie zaczyna się `przed` s przed kwestią i schodzi w `wejscie` s, wraca w `wyjscie` s.
    Wcześniej był twardy przeskok o 8 dB na każdym brzegu kwestii (190 razy w filmie; przegląd 19.11)."""
    krok = 441                                   # obwiednia co 10 ms
    m = voice[::krok].astype(bool).copy()
    k = len(m)
    d = np.diff(m.astype(np.int8))
    on, off = np.flatnonzero(d == 1) + 1, np.flatnonzero(d == -1) + 1
    for o in off:                                # zasypanie krótkich przerw
        nx = on[on > o]
        if len(nx) and nx[0] - o < przerwa * 100:
            m[o:nx[0]] = True
    for o in np.flatnonzero(np.diff(m.astype(np.int8)) == 1) + 1:
        m[max(0, o - int(przed * 100)):o] = True
    cel = np.where(m, 10 ** (db / 20), 1.0)
    g = np.empty(k)
    v = 1.0
    a_dol, a_gora = 1 / (wejscie * 100), 1 / (wyjscie * 100)
    lo = 10 ** (db / 20)
    for i in range(k):                          # liniowo w dół i w górę, bez skoków
        if cel[i] < v:
            v = max(cel[i], v - (1 - lo) * a_dol)
        elif cel[i] > v:
            v = min(cel[i], v + (1 - lo) * a_gora)
        g[i] = v
    return np.interp(np.arange(len(voice)), np.arange(k) * krok, g)


# =====================================================================================================================
# EFEKTY: dźwięki krótkie (gain) i długie (czas w sekundach)
# =====================================================================================================================

def _s(*xs):
    """Suma dźwięków różnej długości (krótsze dopełnione ciszą)."""
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[:len(x)] += x
    return out


def _r(seed):
    return np.random.default_rng(seed)


def _szum(n, lo, hi, seed=0):
    return band(_r(seed).normal(0, 1, n), lo, hi)


def _sweep(f0, f1, sec, harm=((1, 1.0),), curve=1.0):
    n = N(sec)
    t = tt(n)
    f = f0 + (f1 - f0) * (t / sec) ** curve
    ph = 2 * math.pi * np.cumsum(f) / SR
    return sum(a * np.sin(k * ph) for k, a in harm)


def tab_snd():
    """Tabliczka z okrzykiem: suchy klik drewna i papier."""
    out = np.zeros(N(0.4))
    out[:N(0.25)] += whoosh(0.25, 1500, 6000) * 0.45
    s = _s(knock(900, 0.12) * 0.7, knock(1350, 0.1) * 0.3)
    out[N(0.14):N(0.14) + len(s)] += s
    return out


def podpis_snd():
    out = np.zeros(N(0.6))
    out[:N(0.5)] += whoosh(0.5, 600, 3000) * 0.3
    s = knock(620, 0.1) * 0.22
    out[N(0.36):N(0.36) + len(s)] += s
    return out


def zawieszka_snd():
    out = np.zeros(N(0.75))
    out[:N(0.6)] += whoosh(0.6, 400, 2500) * 0.35
    s = knock(420, 0.15) * 0.4
    out[N(0.46):N(0.46) + len(s)] += s
    return out


def stempel():
    """Pieczątka dnia polowania (DAY 1, DAY 20…): ciężkie, suche „tump”."""
    n, t = N(0.5), tt(N(0.5))
    return _s(thud(0.5) * 0.6, knock(220, 0.3) * 0.7, _szum(n, 400, 4000, 3) * np.exp(-t / 0.01) * 0.4)


def nitka():
    out = np.zeros(N(0.6))
    out[:N(0.45)] += whoosh(0.45, 800, 4000) * 0.25
    s = knock(700, 0.1) * 0.14
    out[N(0.42):N(0.42) + len(s)] += s
    return out


def wahwah(krotko=False):
    """Puzon z tłumikiem: „łaa-łaa-łaa-łaaa” (porażka, komiczny zawód)."""
    nuty = ((55, 0.32), (54, 0.32), (53, 0.32), (52, 1.1)) if not krotko else ((52, 0.25), (50, 0.6))
    out = np.zeros(N(sum(d for _, d in nuty) + 0.3))
    t0 = 0.0
    for j, (m, d) in enumerate(nuty):
        s = _dech(m, d, 0.6, ((500, 250, 1.0), (1100, 400, 0.5)), vib=25 if j == len(nuty) - 1 else 6, atak=0.03, szum=0.03, seed=40 + j)
        L = len(s)
        wah = 0.55 + 0.45 * np.sin(np.pi * np.clip(tt(L) / max(d, 0.1), 0, 1))
        out[N(t0):N(t0) + L] += (s * wah)[:len(out) - N(t0)]
        t0 += d
    return out * 0.32


def smiech_p():
    """„HA HA!” fortepianem: szybki, opadający chichot nut."""
    out = np.zeros(N(1.2))
    for j, m in enumerate((84, 88, 83, 86, 81, 84, 79, 83)):
        s = piano(m, 0.09, 0.55)
        out[N(0.075 * j):N(0.075 * j) + len(s)] += s[:len(out) - N(0.075 * j)]
    return out * 1.3


def klakson():
    """Klakson Forda lat 30.: „a-uuu-ga”."""
    sec = 0.75
    n = N(sec)
    t = tt(n)
    f = np.interp(t, (0, 0.14, 0.5, 0.75), (200, 360, 350, 255))
    ph = 2 * math.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * math.pi * 31 * t))) / SR
    x = sum(np.sin(k * ph) / k ** 0.6 for k in range(1, 14))
    x = band(x, 300, 3200)
    return x / (np.abs(x).max() + 1e-9) * env(n, 0.02, 2.0) * np.clip((sec - t) / 0.06, 0, 1) * 0.42


def beep(ile=1):
    out = np.zeros(N(0.32 * ile + 0.1))
    for j in range(ile):
        n = N(0.22)
        t = tt(n)
        x = sum(np.sin(2 * math.pi * f * k * t) / k for f in (330, 415) for k in range(1, 8))
        x = band(x, 250, 3000)
        x = x / (np.abs(x).max() + 1e-9) * np.minimum(1, t / 0.01) * np.clip((0.22 - t) / 0.03, 0, 1) * 0.35
        out[N(0.32 * j):N(0.32 * j) + n] += x
    return out


def pisk():
    """Pisk opon."""
    sec = 0.9
    n = N(sec)
    t = tt(n)
    x = _sweep(2600, 1900, sec, ((1, 1.0), (2, 0.3))) * (0.6 + 0.4 * np.sin(2 * math.pi * 23 * t)) * 0.4
    x += _szum(n, 2000, 7000, 5) * 0.5
    return x * env(n, 0.02, 0.5) * np.clip((sec - t) / 0.2, 0, 1) * 0.5


def szklo():
    n = N(1.0)
    t = tt(n)
    r = _r(7)
    out = _szum(n, 2500, 9000, 8) * np.exp(-t / 0.05) * 0.5
    for _ in range(22):
        i = int(r.uniform(0, N(0.5)))
        L = N(0.25)
        out[i:i + L] += np.sin(2 * math.pi * r.uniform(3000, 8000) * tt(L)) * np.exp(-tt(L) / r.uniform(0.03, 0.1)) * r.uniform(0.05, 0.15)
    return out * 0.9


def krach():
    """Zgniatany metal: uderzenie, brzęk blach, opadające części."""
    n = N(1.6)
    t = tt(n)
    out = thud(0.6) * 1.0
    out = np.concatenate([out, np.zeros(n - len(out))])
    out += _szum(n, 150, 4000, 9) * np.exp(-t / 0.25) * 0.6
    out[:N(0.8)] += clash(0.8) * 0.6
    r = _r(10)
    for _ in range(9):
        i = int(r.uniform(N(0.15), N(1.2)))
        s = knock(r.uniform(300, 900), 0.2) * r.uniform(0.2, 0.45)
        out[i:i + len(s)] += s[:n - i]
    return out * 0.8


def boom():
    return drum(1.4, 42) * 1.1 + np.concatenate([thud(0.6), np.zeros(N(1.4) - N(0.6))]) * 0.7


def strzal(cien=False):
    """Strzał; za parawanem przytłumiony, z pogłosem sali."""
    n = N(1.2)
    t = tt(n)
    x = np.zeros(n)
    x[:N(0.35)] += crack(0.35) * 1.0
    x[:N(0.5)] += drum(0.5, 95) * 0.6
    x += _szum(n, 200, 3000, 12) * np.exp(-t / 0.35) * 0.18
    if cien:
        x = band(x, 60, 1800) * 0.75
    return x * 0.85


def flesz():
    """Flesz lat 30.: trzask żarówki i syk."""
    n = N(0.6)
    t = tt(n)
    x = _szum(n, 400, 5000, 13) * np.exp(-t / 0.08) * 0.35 + np.sin(2 * math.pi * 3400 * t) * np.exp(-t / 0.25) * 0.04
    k = knock(1800, 0.05) * 0.5
    x[:len(k)] += k
    return x


def aparat():
    out = np.zeros(N(0.15))
    for d, f in ((0, 2000), (0.04, 1400)):
        s = knock(f, 0.05) * 0.4
        out[N(d):N(d) + len(s)] += s
    return out


def drzwi():
    n = N(0.7)
    out = np.zeros(n)
    sk = _sweep(300, 520, 0.4, ((1, 1.0), (2, 0.5), (3, 0.3))) * (0.6 + 0.4 * np.sign(np.sin(2 * math.pi * 38 * tt(N(0.4))))) * 0.06
    out[:len(sk)] += sk * env(len(sk), 0.05, 0.4)
    s = _s(thud(0.3) * 0.5, knock(240, 0.2) * 0.3)
    out[N(0.42):N(0.42) + len(s)] += s[:n - N(0.42)]
    return out


def kajdanki():
    out = np.zeros(N(0.6))
    for d, f in ((0, 2900), (0.08, 3300), (0.25, 3000), (0.33, 3500)):
        s = knock(f, 0.06) * 0.35
        out[N(d):N(d) + len(s)] += s
    return out + np.concatenate([coin(0.6) * 0.3])


def kasa():
    """Kasa sklepowa: szuflada i „dzyń”."""
    n = N(1.4)
    out = np.zeros(n)
    out[:N(0.3)] += _szum(N(0.3), 300, 2500, 14) * env(N(0.3), 0.02, 0.1) * 0.25
    t = tt(N(1.2))
    bell = sum(a * np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, a, d in ((2093, 1, 0.8), (4186, 0.4, 0.4), (5300, 0.2, 0.2)))
    out[N(0.18):N(0.18) + len(bell)] += bell[:n - N(0.18)] * 0.18
    return out


def indyk():
    """Gulgotanie indyka: szybkie wibrato krtaniowe."""
    sec = 0.55
    n = N(sec)
    t = tt(n)
    f = 420 + 160 * np.sin(2 * math.pi * 24 * t) * np.exp(-t / 0.4) + 80 * (1 - t / sec)
    ph = 2 * math.pi * np.cumsum(f) / SR
    x = band(sum(np.sin(k * ph) / k for k in range(1, 10)), 300, 3000)
    return x / (np.abs(x).max() + 1e-9) * env(n, 0.01, 0.35) * 0.3


def osiol():
    """Muł: „ii-oo” — wdech wysoko z szumem, wydech nisko, nosowo."""
    out = np.zeros(N(2.0))
    t0 = 0.0
    for j in range(3):
        for f0, f1, d, s in ((900, 1100, 0.28, 0.5), (330, 260, 0.38, 0.15)):
            x = band(_sweep(f0, f1, d, tuple((k, 1 / k) for k in range(1, 9))), 250, 3500)
            x = x / (np.abs(x).max() + 1e-9) * np.sin(np.pi * tt(len(x)) / d) ** 0.5 * 0.3
            x += _szum(len(x), 1000, 5000, 15 + j) * s * 0.3
            out[N(t0):N(t0) + len(x)] += x[:len(out) - N(t0)]
            t0 += d + 0.02
    return out


def gwizdek():
    """Gwizdek policjanta z kulką: dwa tony i trel."""
    sec = 0.9
    n = N(sec)
    t = tt(n)
    x = (np.sin(2 * math.pi * 2800 * t) + 0.8 * np.sin(2 * math.pi * 3150 * t)) * (0.6 + 0.4 * np.sin(2 * math.pi * 26 * t))
    return x * env(n, 0.02, 2.0) * np.clip((sec - t) / 0.05, 0, 1) * 0.12


def skrzydla():
    n = N(1.4)
    t = tt(n)
    return _szum(n, 300, 2500, 16) * (np.sin(2 * math.pi * 6.5 * t) > 0.3) * np.exp(-t / 0.9) * 0.35


def oklaski(sec):
    n = N(sec)
    out = np.zeros(n)
    r = _r(17)
    cl = _szum(N(0.025), 800, 5000, 18) * env(N(0.025), 0.001, 0.006)
    for _ in range(int(sec * 34)):
        i = int(r.uniform(0, n - len(cl)))
        out[i:i + len(cl)] += cl * r.uniform(0.15, 0.35)
    t = tt(n)
    return out * np.minimum(1, t / 0.4) * np.clip((sec - t) / 0.8, 0, 1) * 0.6


def boing(maly=False):
    sec = 0.6 if not maly else 0.35
    n = N(sec)
    t = tt(n)
    f = (180 if not maly else 320) * (1 + 0.35 * np.sin(2 * math.pi * 13 * t) * np.exp(-t / 0.25)) * (1 + 0.6 * t)
    ph = 2 * math.pi * np.cumsum(f) / SR
    return (np.sin(ph) + 0.3 * np.sin(2 * ph)) * env(n, 0.003, 0.25) * (0.28 if not maly else 0.16)


def dzwoneczki(sec=1.0, n_=5, seed=19):
    n = N(sec + 0.6)
    out = np.zeros(n)
    r = _r(seed)
    for j in range(n_):
        i = N(j * sec / max(1, n_))
        L = N(0.6)
        f = r.uniform(1800, 3200)
        out[i:i + L] += sum(a * np.sin(2 * math.pi * f * k * tt(L)) for k, a in ((1, 1), (2.76, 0.3))) * np.exp(-tt(L) / 0.25) * 0.06
    return out


def brama(sec=1.4):
    """Skrzypienie ciężkich zawiasów bramy."""
    n = N(sec)
    t = tt(n)
    f = 110 + 50 * np.sin(2 * math.pi * 0.6 * t) + 30 * _r(20).uniform(-1, 1, 1)[0]
    ph = 2 * math.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 20)) * (0.5 + 0.5 * (np.sin(2 * math.pi * 17 * t) > 0))
    return band(x, 200, 2500) * np.sin(np.pi * t / sec) * 0.12


def brama_hit():
    n = N(2.2)
    t = tt(n)
    x = sum(a * np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, a, d in ((147, 1, 1.2), (311, 0.6, 0.8), (587, 0.4, 0.5), (1210, 0.2, 0.3)))
    x[:N(0.6)] += thud(0.6) * 1.2
    return x * 0.45


def chop():
    return np.concatenate([thud(0.4) * 0.8, np.zeros(N(0.1))])[:N(0.5)] + np.concatenate([crack(0.35) * 0.5, np.zeros(N(0.15))])[:N(0.5)]


def bloto(sec):
    n = N(sec)
    t = tt(n)
    return (_szum(n, 100, 900, 21) * (0.5 + 0.5 * np.sin(2 * math.pi * 6 * t)) * 0.18 + _szum(n, 1500, 5000, 22) * 0.05) * np.minimum(1, t / 0.2)


def pisanie(sec, glosno=0.05):
    n = N(sec)
    t = tt(n)
    am = np.clip(np.interp(t, np.linspace(0, sec, int(sec * 9) + 2), _r(23).uniform(0, 1, int(sec * 9) + 2)), 0, 1)
    return _szum(n, 2000, 7000, 24) * am * glosno


def trzepot():
    n = N(0.6)
    t = tt(n)
    return _szum(n, 1000, 6000, 25) * (0.5 + 0.5 * np.sin(2 * math.pi * 21 * t)) * np.sin(np.pi * t / 0.6) * 0.2


def saks_riff():
    out = np.zeros(N(3.2))
    for j, (m, d, L) in enumerate(((65, 0.0, 0.3), (68, 0.33, 0.3), (70, 0.66, 0.2), (71, 0.88, 0.2), (72, 1.1, 0.9), (70, 2.1, 0.25), (65, 2.4, 0.7))):
        s = saks(m, L, 0.6)
        out[N(d):N(d) + len(s)] += s[:len(out) - N(d)]
    return out


def karty():
    n = N(0.9)
    out = np.zeros(n)
    k = 0.0
    r = _r(26)
    while k < 0.75:
        s = _szum(N(0.01), 2000, 8000, int(k * 1000)) * env(N(0.01), 0.001, 0.003) * r.uniform(0.15, 0.3)
        out[N(k):N(k) + len(s)] += s
        k += r.uniform(0.012, 0.03)
    return out


def klik():
    return knock(2400, 0.04) * 0.3


def plask():
    n = N(0.15)
    return _szum(n, 500, 5000, 27) * env(n, 0.001, 0.02) * 0.4 + np.concatenate([thud(0.1)[:n] * 0.2, np.zeros(max(0, n - N(0.1)))])[:n]


def slide(w_dol=True, sec=0.7):
    t = tt(N(sec))
    f0, f1 = (1400, 380) if w_dol else (380, 1400)
    x = _sweep(f0, f1, sec, ((1, 1.0), (2, 0.08)), 0.8) * (1 + 0.02 * np.sin(2 * math.pi * 6 * t))
    return x * np.minimum(1, t / 0.03) * np.clip((sec - t) / 0.08, 0, 1) * 0.13


def sting(ciemny=True):
    """Dramatyczny akcent: niski oktawowy fortepian + akord + kocioł."""
    out = np.zeros(N(3.0))
    for m in ((38, 50, 57, 62, 65) if ciemny else (45, 57, 64, 69, 72)):
        s = piano(m, 2.4, 0.75)
        out[:len(s)] += s
    out[:N(1.4)] += drum(1.4, 46) * 0.7
    return out


def sting_tajemnica():
    out = np.zeros(N(3.0))
    for j, m in enumerate((69, 72, 76, 83)):
        s_ = piano(m, 2.0, 0.4)
        out[N(0.06 * j):N(0.06 * j) + len(s_)] += s_[:len(out) - N(0.06 * j)]
    d = dzwoneczki(1.2, 4, 33)[:len(out)]
    out[:len(d)] += d
    return out


def sting_lowcy():
    out = np.zeros(N(3.0))
    for j, m in enumerate((45, 50, 53)):
        s = piano(m, 0.35 if j < 2 else 2.0, 0.6)
        out[N(0.3 * j):N(0.3 * j) + len(s)] += s[:len(out) - N(0.3 * j)]
    return out


def syk(sec):
    n = N(sec)
    t = tt(n)
    return _szum(n, 3000, 9000, 28) * (0.6 + 0.4 * np.sin(2 * math.pi * 11 * t)) * np.sin(np.pi * t / sec) * 0.12


def wiadro():
    t = tt(N(0.5))
    return sum(a * np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, a, d in ((640, 1, 0.2), (1130, 0.6, 0.12), (1790, 0.3, 0.08))) * 0.15 + thud(0.5) * 0.2


def lanie(sec):
    n = N(sec)
    t = tt(n)
    return _szum(n, 400, 3000, 29) * (0.7 + 0.3 * np.sin(2 * math.pi * 9 * t)) * np.sin(np.pi * t / sec) ** 0.5 * 0.12


def drut():
    sec = 0.7
    t = tt(N(sec))
    return np.sin(2 * math.pi * (1900 + 200 * np.sin(2 * math.pi * 7 * t)) * t) * np.sin(np.pi * t / sec) * 0.05


def metal():
    out = np.zeros(N(0.35))
    for d, f in ((0, 1500), (0.15, 2200)):
        s = knock(f, 0.08) * 0.35
        out[N(d):N(d) + len(s)] += s
    return out


def zamek():
    """Przeładowanie karabinu: zgrzyt zamka i dwa trzaski."""
    out = np.zeros(N(0.5))
    out[N(0.05):N(0.25)] += _szum(N(0.2), 1500, 6000, 30) * 0.12
    for d, f in ((0.0, 1500), (0.27, 2200)):
        s = knock(f, 0.08) * 0.5
        out[N(d):N(d) + len(s)] += s
    return out


def krzaki():
    n = N(0.7)
    t = tt(n)
    return _szum(n, 1000, 6000, 31) * (0.5 + 0.5 * np.sin(2 * math.pi * 17 * t)) * env(n, 0.03, 0.3) * 0.3


def lomot():
    out = np.concatenate([thud(0.5) * 0.9, np.zeros(N(0.3))])
    c = coin(0.6) * 0.5
    out[N(0.05):N(0.05) + len(c)] += c[:len(out) - N(0.05)]
    return out


def szuflada():
    n = N(0.6)
    out = _szum(n, 300, 2000, 32) * env(n, 0.05, 0.25) * 0.25
    out[N(0.4):N(0.4) + N(0.2)] += thud(0.2) * 0.4
    return out


def stuk():
    return knock(300, 0.15) * 0.45


def teczka():
    n = N(0.4)
    return _szum(n, 200, 2000, 33) * env(n, 0.005, 0.06) * 0.4 + np.concatenate([thud(0.3) * 0.3, np.zeros(N(0.1))])[:n]


def kubek():
    return knock(900, 0.1) * 0.4 + np.concatenate([coin(0.6) * 0.15])[:N(0.1)]


def krzeslo():
    sec = 0.5
    t = tt(N(sec))
    return band(_sweep(150, 230, sec, tuple((k, 1 / k) for k in range(1, 12))), 300, 2500) * (np.sin(2 * math.pi * 30 * t) > 0) * np.sin(np.pi * t / sec) * 0.05


def dzwonek():
    t = tt(N(1.6))
    return sum(a * np.sin(2 * math.pi * f * t) * np.exp(-t / d) for f, a, d in ((2093, 1, 0.9), (5650, 0.35, 0.4), (4186, 0.2, 0.5))) * 0.14


def dzwon(f=196):
    t = tt(N(5.0))
    return sum(a * np.sin(2 * math.pi * f * k * t) * np.exp(-t / d) for k, a, d in ((0.5, 0.5, 4), (1, 1, 3), (1.19, 0.6, 2.2), (1.5, 0.4, 1.6), (2.0, 0.5, 1.2), (2.66, 0.2, 0.8))) * 0.12


def dzwony(sec):
    out = np.zeros(N(sec + 5))
    k, j = 0.0, 0
    while k < sec:
        s = band(dzwon((392, 523, 440)[j % 3]), 100, 2500) * 0.35
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 1.1
        j += 1
    return out[:N(sec)] * np.clip((sec - tt(N(sec))) / 1.0, 0, 1)


def zgniot():
    n = N(0.7)
    out = np.zeros(n)
    r = _r(34)
    for _ in range(60):
        i = int(r.uniform(0, n - N(0.01)))
        out[i:i + N(0.01)] += _szum(N(0.01), 1000, 8000, int(i)) * r.uniform(0.05, 0.2)
    return out


def komary(sec):
    n = N(sec)
    t = tt(n)
    f = 610 + 40 * np.sin(2 * math.pi * 0.7 * t) + 15 * np.sin(2 * math.pi * 9 * t)
    ph = 2 * math.pi * np.cumsum(f) / SR
    return sum(np.sin(k * ph) / k for k in (1, 2, 3)) * (0.3 + 0.7 * np.sin(2 * math.pi * 0.23 * t) ** 2) * 0.012


def klaps_reka():
    n = N(0.15)
    return _szum(n, 800, 5000, 35) * env(n, 0.001, 0.015) * 0.5


def lewarek(sec):
    out = np.zeros(N(sec))
    k = 0.0
    while k < sec - 0.05:
        s = knock(1200, 0.05) * 0.3
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 0.16
    return out


def papierek(sec):
    out = np.zeros(N(sec))
    k = 0.5
    while k < sec - 0.7:
        s = zgniot() * 0.35
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 2.2
    return out


def zwir(sec):
    n = N(sec)
    out = _szum(n, 80, 600, 36) * 0.06
    r = _r(37)
    for _ in range(int(sec * 120)):
        i = int(r.uniform(0, n - N(0.005)))
        out[i:i + N(0.005)] += _szum(N(0.005), 1000, 5000, i % 997) * r.uniform(0.02, 0.08)
    return out * np.clip((sec - tt(n)) / 0.5, 0, 1)


def zgrzyt(sec):
    n = N(sec)
    t = tt(n)
    x = _szum(n, 300, 3000, 38) * 0.15 + band(np.sign(np.sin(2 * math.pi * (380 + 30 * np.sin(2 * math.pi * 3 * t)) * t)), 300, 2000) * 0.04
    return x * np.sin(np.pi * t / sec) ** 0.5


def nozyczki():
    out = np.zeros(N(0.4))
    for d in (0.0, 0.16):
        s = _s(_szum(N(0.08), 3000, 9000, 39) * env(N(0.08), 0.005, 0.03) * 0.3, knock(3200, 0.05) * 0.2)
        out[N(d):N(d) + len(s)] += s
    return out


def tlum(sec):
    """Szuranie tłumu (bez głosów)."""
    n = N(sec)
    out = _szum(n, 200, 1500, 40) * 0.03
    r = _r(41)
    for _ in range(int(sec * 9)):
        s = knock(r.uniform(300, 500), 0.1) * r.uniform(0.04, 0.09)
        i = int(r.uniform(0, n - len(s)))
        out[i:i + len(s)] += s
    return out


def rekawiczka():
    n = N(0.12)
    return _szum(n, 800, 6000, 42) * env(n, 0.001, 0.02) * 0.35


def karuzela(sec):
    out = np.zeros(N(sec))
    k = 0.3
    while k < sec - 0.6:
        s = krzeslo() * 0.6
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 2.4
    return out


def podlewanie(sec):
    n = N(sec)
    t = tt(n)
    out = _szum(n, 2000, 8000, 43) * 0.04
    r = _r(44)
    for _ in range(int(sec * 30)):
        i = int(r.uniform(0, n - N(0.02)))
        out[i:i + N(0.02)] += np.sin(2 * math.pi * r.uniform(1500, 3500) * tt(N(0.02))) * np.exp(-tt(N(0.02)) / 0.006) * 0.05
    return out * np.minimum(1, t / 0.3) * np.clip((sec - t) / 0.5, 0, 1)


def szum_ekranu(sec):
    n = N(sec)
    t = tt(n)
    return _szum(n, 500, 8000, 45) * (0.5 + 0.5 * (np.sin(2 * math.pi * 12 * t) > 0)) * 0.08


def chip_start():
    out = np.zeros(N(0.7))
    for j, m in enumerate((60, 64, 67, 72, 76, 79, 84)):
        s = chip(m, 0.07, 0.8, 0.5)
        out[N(0.07 * j):N(0.07 * j) + len(s)] += s[:len(out) - N(0.07 * j)]
    return out * 1.6


def gwizdanie(sec):
    """Gwizdana melodyjka (♪): czysty ton z wibrato, bez szumu głosu."""
    out = np.zeros(N(sec))
    nuty = ((79, 0.3), (76, 0.3), (79, 0.3), (81, 0.6), (79, 0.3), (76, 0.3), (72, 0.9), (74, 0.3), (76, 0.3), (79, 0.6))
    k = 0.0
    for m, d in nuty:
        if k > sec - d:
            break
        t = tt(N(d))
        f = mtof(m) * (1 + 0.006 * np.sin(2 * math.pi * 6 * t))
        x = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.03) * np.clip((d - t) / 0.05, 0, 1) * 0.06
        out[N(k):N(k) + len(x)] += x[:len(out) - N(k)]
        k += d
    return out


def skrzyp(sec):
    out = np.zeros(N(sec))
    k = 0.2
    while k < sec - 0.6:
        s = krzeslo() * 0.7
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 0.8
    return out


def nalewanie(sec):
    n = N(sec)
    t = tt(n)
    x = _szum(n, 500, 3000, 46) * 0.08 + np.sin(2 * math.pi * (400 + 600 * t / sec) * t) * 0.01
    return x * np.sin(np.pi * t / sec) ** 0.4


def mieszanie(sec):
    out = np.zeros(N(sec))
    k = 0.1
    while k < sec - 0.3:
        s = coin(0.3) * 0.25
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 0.36
    return out


def ziew():
    return slide(True, 1.1) * 0.8


def brr():
    t = tt(N(0.9))
    return (np.sin(2 * math.pi * 98 * t) + 0.5 * np.sin(2 * math.pi * 196 * t)) * (0.5 + 0.5 * np.sin(2 * math.pi * 28 * t)) * np.sin(np.pi * t / 0.9) * 0.08


def zegar(sec):
    out = np.zeros(N(sec))
    k, j = 0.0, 0
    while k < sec:
        s = tyk(0.5, 2600 if j % 2 == 0 else 2150)
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 0.5
        j += 1
    return out


def prasa(sec):
    """Maszyna rotacyjna: łoskot w rytmie wałków i szum papieru."""
    n = N(sec)
    out = _szum(n, 300, 4000, 47) * 0.04
    k = 0.0
    while k < sec:
        for d, f, g in ((0, 120, 0.55), (0.22, 180, 0.3)):
            s = knock(f, 0.2) * g + _szum(N(0.2), 600, 3000, int(k * 10)) * env(N(0.2), 0.002, 0.04) * 0.15
            if N(k + d) < n:
                out[N(k + d):N(k + d) + len(s)] += s[:n - N(k + d)]
        k += 0.45
    return out * np.minimum(1, tt(n) / 0.3)


def projektor(sec):
    n = N(sec)
    t = tt(n)
    return (_szum(n, 1000, 5000, 48) * (np.sin(2 * math.pi * 24 * t) > 0.6) * 0.05 + np.sin(2 * math.pi * 120 * t) * 0.006)


def kola(sec):
    out = np.zeros(N(sec))
    k, d = 0.0, 0.08
    while k < sec:
        s = knock(1500, 0.03) * 0.15
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += d
        d *= 1.04
    return out


def brodzenie(sec):
    out = np.zeros(N(sec + 1.3))
    k = 0.0
    while k < sec:
        s = splash(1.2) * 0.35
        out[N(k):N(k) + len(s)] += s
        k += 0.7
    return out[:N(sec)]


def woda(sec):
    n = N(sec)
    return band(RNG.normal(0, 1, n), 200, 3000) * 0.07 * (0.6 + 0.4 * np.sin(2 * math.pi * tt(n) / 2.3) ** 2) * np.minimum(1, tt(n) / 0.5)


def bujak(sec):
    out = np.zeros(N(sec))
    k = 0.0
    while k < sec - 0.4:
        s = krzeslo() * 0.8
        out[N(k):N(k) + len(s)] += s[:len(out) - N(k)]
        k += 0.95
    return out


def kopanie(sec):
    out = np.zeros(N(sec))
    k = 0.0
    while k < sec - 0.3:
        s = _szum(N(0.25), 300, 3000, int(k * 100)) * env(N(0.25), 0.01, 0.08) * 0.2
        out[N(k):N(k) + len(s)] += s
        k += 0.35
    return out


def silnik_jalowy(sec):
    n = N(sec)
    t = tt(n)
    ph = 2 * math.pi * 26 * t
    return (sum(np.sin(k * ph) / k for k in range(1, 7)) * 0.02 + _szum(n, 80, 600, 49) * 0.01) * np.minimum(1, t / 0.5)


# ---------- głos człowieka z modelu mowy (wytyczne 1.14), bez głosu reżysera ----------
# glosy.py → dzwiek_probki/<rodzaj>_N.wav (Chatterbox Turbo na referencjach z syntetycznych głosów Kokoro); kolejne użycia
# biorą kolejne próbki. Bez próbek — cisza i ostrzeżenie (nigdy szum udający człowieka).
PROBKI = HERE / "dzwiek_probki"
_GLOSY, _ILE = {}, {}


def _probki(rodzaj):
    if os.environ.get("BEZ_GLOSOW") == "1":  # wersja bez głosów (zanim reżyser zatwierdzi próbkę głosów)
        return []
    if rodzaj not in _GLOSY:
        _GLOSY[rodzaj] = []
        for f in sorted(PROBKI.glob(f"{rodzaj}_*.wav"), key=lambda f: int(f.stem.rsplit("_", 1)[1])):
            with wave.open(str(f)) as w:
                x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
            _GLOSY[rodzaj].append(x / (np.abs(x).max() + 1e-9))
        if not _GLOSY[rodzaj]:
            print(f"UWAGA: brak próbek {rodzaj}_*.wav w {PROBKI} (glosy.py) — w tym miejscu cisza", flush=True)
    return _GLOSY[rodzaj]


def glos(rodzaj, g=0.5):
    pr_ = _probki(rodzaj)
    if not pr_:
        return np.zeros(N(0.1))
    n = _ILE.get(rodzaj, 0)
    _ILE[rodzaj] = n + 1
    return pr_[n % len(pr_)] * g


def _sala(x, mokro=0.35):
    """Pogłos sali (kilka odbić) i pasmo jak z drugiego planu."""
    y = band(np.concatenate([x, np.zeros(N(0.4))]), 180, 3500)
    out = y.copy()
    for d, g in ((0.023, 0.5), (0.041, 0.4), (0.067, 0.32), (0.11, 0.22), (0.17, 0.15)):
        i = N(d)
        out[i:] += y[:len(y) - i] * g * mokro / 0.5
    return out


def gwar(sec, gestosc=2.2, g=0.16):
    """Gwar tłumu: krótkie zdania różnymi głosami, gęsto i stłumione — słychać ludzi, nie słowa."""
    pr_ = _probki("gwar")
    n = N(sec)
    out = np.zeros(n + N(6))
    if not pr_:
        return np.zeros(n)
    r = _r(61 + int(sec * 10))
    for _ in range(int(sec * gestosc)):
        x = pr_[int(r.integers(len(pr_)))] * r.uniform(0.5, 1.0)
        i = int(r.uniform(-0.5 * len(x), n))
        a, b = max(0, i), min(len(out), i + len(x))
        out[a:b] += x[a - i:b - i]
    out = _sala(out[:n], 0.45)[:n]
    t = tt(n)
    return out / (np.abs(out).max() + 1e-9) * g * np.minimum(1, t / 0.6) * np.clip((sec - t) / 0.8, 0, 1)


def smiech_tlum():
    """Widownia się śmieje: kilka śmiechów naraz, z pogłosem sali."""
    pr_ = _probki("smiech_m")
    out = np.zeros(N(4.0))
    r = _r(62)
    for j, x in enumerate(pr_):
        i = N(r.uniform(0, 0.45))
        out[i:i + len(x)] += x[:len(out) - i] * r.uniform(0.35, 0.6)
    return _sala(out, 0.5)[:N(4.0)] / (np.abs(out).max() + 1e-9) * 0.55


def wiwat_tlum(sec):
    pr_ = _probki("wiwat")
    n = N(sec)
    out = np.zeros(n + N(4))
    r = _r(63)
    for _ in range(int(sec * 1.4)) if pr_ else ():
        x = pr_[int(r.integers(len(pr_)))] * r.uniform(0.4, 0.8)
        i = int(r.uniform(0, max(1, n - N(1.0))))
        out[i:i + len(x)] += x[:len(out) - i]
    return _sala(out[:n], 0.5)[:n] / (np.abs(out).max() + 1e-9) * 0.3 * np.clip((sec - tt(n)) / 1.0, 0, 1)


def kaszel_silnika():
    """Gag 13: Ford gaśnie — trzy niskie kaszlnięcia silnika i pyknięcie z rury."""
    n = N(0.6)
    t = tt(n)
    out = np.zeros(n)
    r = np.random.default_rng(1301)
    for i, c in enumerate((0.0, 0.15, 0.31)):
        j, m = N(c), N(0.13)
        seg = band(r.normal(0, 1, m), 45, 480) * np.exp(-tt(m) / 0.045) * (1.0 - 0.25 * i)
        seg += np.sin(2 * math.pi * (58 - 6 * i) * tt(m)) * np.exp(-tt(m) / 0.06) * 0.9
        out[j:j + m] += seg[:n - j]
    out += band(r.normal(0, 1, n), 300, 2600) * np.exp(-((t - 0.47) / 0.05) ** 2) * 0.35
    return out / (np.abs(out).max() + 1e-9) * 0.7


def zapalka():
    """Gag 25: pocieranie zapałki o draskę i krótki płomień."""
    n = N(0.6)
    t = tt(n)
    r = np.random.default_rng(2501)
    drask = band(r.normal(0, 1, n), 2200, 9000) * np.clip(t / 0.02, 0, 1) * np.exp(-np.clip(t - 0.03, 0, None) / 0.05) * (t < 0.16)
    plomien = band(r.normal(0, 1, n), 250, 1800) * np.clip((t - 0.12) / 0.04, 0, 1) * np.exp(-np.clip(t - 0.16, 0, None) / 0.18)
    out = drask * 0.8 + plomien * 0.6
    return out / (np.abs(out).max() + 1e-9) * 0.55


# Nowe rodzaje dźwięku gagów (reżyser 19.11: „gagi robimy wszystkie”). Zgodnie z zasadą „nowy rodzaj dźwięku → próbka”
# są w filmie dopiero po akceptacji reżysera: NOWE_DZWIEKI=1 (próbka) albo wpis do NOWE_ZATWIERDZONE.
NOWE = {"kaszel_silnika", "werbel_fx", "zapalka"}
NOWE_ZATWIERDZONE = set()


KROTKIE = {
    "tab": tab_snd, "podpis": podpis_snd, "zawieszka": zawieszka_snd, "stempel": stempel, "nitka": nitka, "wahwah": wahwah,
    "wahwah_k": lambda: wahwah(True), "smiech_p": smiech_p, "klakson": klakson, "beep": beep, "beep2": lambda: beep(2), "pisk": pisk,
    "szklo": szklo, "krach": krach, "boom": boom, "strzal": strzal, "strzal_cien": lambda: strzal(True), "flesz": flesz,
    "aparat": aparat, "drzwi": drzwi, "kajdanki": kajdanki, "kasa": kasa, "indyk": indyk, "osiol": osiol, "gwizdek": gwizdek,
    "skrzydla": skrzydla, "boing": boing, "boing_m": lambda: boing(True), "gwiazdka": lambda: dzwoneczki(0.6, 4, 50),
    "brama_hit": brama_hit, "chop": chop, "cios": lambda: np.concatenate([whoosh(0.3, 600, 4000) * 0.6, thud(0.5)]), "kula": lambda: knock(220, 0.15) * 0.45,
    "trzepot": trzepot, "saks": saks_riff, "karty": karty, "klik": klik, "plask": plask, "slide_down": lambda: slide(True),
    "slide_up": lambda: slide(False, 0.45), "sting": sting, "sting_t": sting_tajemnica, "sting_l": sting_lowcy, "wiadro": wiadro,
    "drut": drut, "metal": metal, "zamek": zamek, "krzaki": krzaki, "lomot": lomot, "szuflada": szuflada, "stuk": stuk,
    "teczka": teczka, "kubek": kubek, "krzeslo": krzeslo, "dzwonek": dzwonek, "dzwon": lambda: band(dzwon(110), 60, 3000) * 0.9,
    "zgniot": zgniot, "klaps_reka": klaps_reka, "nozyczki": nozyczki, "rekawiczka": rekawiczka, "chip_start": chip_start,
    "ziew": ziew, "brr": brr, "pytanie": lambda: slide(False, 0.35) * 0.8, "pff": lambda: knock(500, 0.08) * 0.4,
    "whoosh": whoosh, "thud": thud, "knock": knock, "coin": coin, "splash": splash, "plusk": lambda: splash(0.8) * 0.8,
    "kurtyna_z": kurtyna_zasuwa, "kurtyna_r": kurtyna_rozsuwa, "klaps": klaps, "skok": lambda: thud(0.3) * 0.5,
    "papier": lambda: whoosh(0.5, 1200, 7000) * 0.6, "strona": lambda: whoosh(1.4, 500, 6000) * 0.9,
    "kaszel_silnika": kaszel_silnika, "werbel_fx": lambda: werbel(0.9) * 1.3, "zapalka": zapalka,
}
DLUGIE = {
    "ogien": fire, "woda": woda, "brodzenie": brodzenie, "bloto": bloto, "pisanie": pisanie, "oklaski": oklaski, "brama": brama,
    "lanie": lanie, "syk": syk, "dzwony": dzwony, "komary": komary, "lewarek": lewarek, "papierek": papierek, "zwir": zwir,
    "zgrzyt": zgrzyt, "tlum": tlum, "karuzela": karuzela, "podlewanie": podlewanie, "szum_ekranu": szum_ekranu,
    "gwizdanie": gwizdanie, "skrzyp": skrzyp, "nalewanie": nalewanie, "mieszanie": mieszanie, "zegar": zegar, "prasa": prasa,
    "projektor": projektor, "kola": kola, "bujak": bujak, "kopanie": kopanie, "silnik_jalowy": silnik_jalowy, "kopyta": hooves,
    "olowek": lambda s: pisanie(s, 0.07), "gwar": gwar, "gwar_cichy": lambda s: gwar(s, 1.4, 0.09), "wiwat": wiwat_tlum, "gwiazdki": lambda s: dzwoneczki(s, int(s * 4), 51),
}

# Dźwięk tabliczki według napisu (słownik znaków 1.20): porażka → wah-wah, śmiech → chichot fortepianu, klakson…
TAB_DZWIEK = {"AGAIN?!": "wahwah", "THAT'S IT?": "wahwah", "OH NO": "wahwah", "...": "wahwah_k", "...?": "wahwah_k",
              "THAT'S NOT ME!": "wahwah", "NOT MY STATE...": "wahwah_k", "UGH!": "wahwah_k", "HA HA!": "smiech_p", "HA HA HA!": "smiech_p",
              "BEEP": "beep", "BEEP BEEP!": "beep2", "SCREECH!": "pisk", "AW!": "boing", "OW!": "boing_m", "OUCH!": "boing",
              "NEVER AGAIN": "sting", "HE WON'T GO BACK": "sting", "NO MORE CHASING": "sting_l", "HOME": "sting", "AAAA!": "sting",
              "YAWN": "ziew", "SIGH…": "ziew", "BRRR!": "brr", "?": "pytanie", "♪": None, "STOP!": None,
              # gagi (GAGI.md)
              "SERIOUSLY?": "wahwah_k", "OOF!": "thud", "O!": "pytanie", "…": "wahwah_k", "beep": "beep",
              "MMPH!": "wahwah_k", "YAP!": "boing_m", "!": "pytanie", "OVER HERE!": "tab", "SNAP!": "boing_m", "HMM…": "wahwah_k",
              "GOBBLE!": "indyk"}

# Głos postaci pod tabliczką (napis → rodzaj z glosy.py); wyjątki dla ujęcia, gdy ten sam napis mówi kto inny.
TAB_GLOS = {"HA HA!": "smiech_b", "AAAA!": "krzyk_b", "UGH!": "ugh_b", "SIGH…": "westchnienie_b", "BRRR!": "brr_b", "OW!": "au_b",
            "HEY!": "hej_b", "SHHH!": "shh", "STOP!": "stop", "GO!": "go", "OH NO": "ojnie", "AW!": "au_c", "OUCH!": "ouch", "BYE!": "bye",
            "THAT'S IT?": "thats_it", "BACK OFF!": "back_off", "EXTRA!": "extra", "HA HA HA!": "*smiech_tlum"}
TAB_GLOS_UJ = {("darby_auto", "HEY!"): "hej_m"}
TAB_DZWIEK.update({"HA HA!": "tab", "SIGH…": "tab", "BRRR!": "tab", "HA HA HA!": "tab"})  # śmiech i westchnienie robi teraz głos
GLOS_G = {"extra": 0.35, "krzyk_b": 0.6, "smiech_b": 0.6}

# =====================================================================================================================
# ZDARZENIA RĘCZNE (sekunda od początku ujęcia, dźwięk, głośność — albo czas trwania dla dźwięków długich)
# =====================================================================================================================

ZDARZENIA = {
    "tytul": [(0.1, "kurtyna_r", 1.0), (1.5, "klakson", 0.9)],
    "wprowadzenie": [(4.7, "whoosh", 0.25)],
    "wprowadzenie2": [(1.3, "zamek", 0.5), (0.5, "kula", 0.7), (0.95, "kula", 0.7), (1.6, "metal", 0.7), (1.65, "lanie", 3.5)],
    "joplin_rzeczy": [(0.3, "drzwi", 0.8), (3.7, "aparat", 0.8), (4.6, "papier", 0.5)],
    "zdjecie": [(0.7, "whoosh", 0.3), (2.5, "whoosh", 0.25)],
    "hak_pomost": [(0.1, "strona", 1.0)],
    "prasa": [(0.0, "prasa", 9.0)] + [(0.6 + 0.4 * n, "papier", 0.25) for n in range(8)],
    "hak_cygaro": [(2.6, "pff", 0.6), (3.6, "zgniot", 0.9)],
    "obietnica": [(0.2, "papier", 0.6), (3.6, "sting_l", 0.8)],
    "wagon": [(4.0, "whoosh", 0.25)],
    "indyki": [(0.3, "indyk", 0.8), (1.3, "indyk", 0.7), (2.2, "indyk", 0.8), (2.7, "gwizdek", 1.0),
               (3.4, "skrzydla", 1.0), (3.5, "indyk", 1.0), (3.8, "indyk", 0.9), (4.1, "indyk", 0.8)],
    "szkola": [(2.6, "boing_m", 0.8), (3.0, "oklaski", 3.2), (4.4, "gwiazdka", 1.0)],
    "slub": [(5.5, "gwiazdka", 0.8)],
    "poezja": [(1.6, "whoosh", 0.4), (2.3, "thud", 0.5), (2.4, "indyk", 0.7)],
    "roy": [(3.0, "drzwi", 0.7)],
    "kawiarnia": [(1.45, "nalewanie", 0.85), (2.95, "lomot", 0.9)],
    "kuchnia": [(0.0, "mieszanie", 3.0), (1.2, "drzwi", 0.6), (3.3, "whoosh", 0.25)],
    "areszt": [(0.85, "kajdanki", 1.0), (4.75, "drzwi", 0.9)],
    "waco": [(0.4, "whoosh", 0.3), (1.2, "metal", 0.6), (2.2, "skrzyp", 0.6), (6.3, "boing_m", 0.5)],
    "waco_przed": [(3.6, "papier", 0.3), (6.3, "drzwi", 0.6)],
    "ohio": [(1.0, "gwizdanie", 1.6)],
    "eastham": [(0.0, "kopyta", 12.0)] + [(0.8 + 0.9 * n, "chop", 0.22) for n in range(9)],
    "eastham_rura": [(4.7, "cios", 1.0), (6.4, "thud", 0.8)],
    "palce": [(1.0, "whoosh", 0.5), (1.45, "chop", 1.0), (1.6, "gwiazdki", 2.4)],
    "parol": [(0.2, "brama", 1.0)] + [(1.0 + 0.5 * n, "kula", 0.6) for n in range(6)],
    "przysiega": [(1.6, "brama", 0.6), (2.2, "brama_hit", 1.0)] + [(5.2 + 0.62 * n, "kula", 0.5) for n in range(8)],
    "stacja": [(2.4, "kasa", 1.0), (2.95, "coin", 0.5)],
    "kaufman": [(1.4, "bloto", 2.2), (3.7, "drzwi", 0.5), (6.6, "osiol", 1.0), (8.6, "osiol", 0.7)],
    "cela": [(0.0, "pisanie", 11.0)] + [(2.0 + 0.9 * n, "trzepot", 0.7) for n in range(6)],
    "hillsboro": [(5.0, "thud", 0.6)],
    "atoka": [(7.4, "thud", 0.7)],
    "wd": [(5.6, "whoosh", 0.4)],  # gag 9: skok przez okno (OOF! → thud z tabliczki)
    "buck": [(0.3, "brama", 1.2)],
    "joplin_dom": [(4.6, "drzwi", 0.5), (5.0, "drzwi", 0.5), (6.9, "klik", 0.7)],
    "joplin_karty": [(0.3, "saks", 1.0), (1.0, "karty", 0.9), (4.2, "saks", 1.0), (6.2, "karty", 0.8)],
    "joplin_walka": [(5.0, "thud", 0.6), (5.4, "thud", 0.6), (7.2, "pisk", 0.9)],
    "ciemnia": [(0.0, "woda", 10.0), (2.4, "sting_t", 0.9)],
    "kiosk": [(1.0 + 1.25 * n, "plask", 0.5) for n in range(7)] + [(0.0, "gwar", 12.0)],
    "cygaro_zlosc": [(2.2, "zgniot", 0.7), (2.6, "slide_down", 0.7)],
    "darby_auto": [(7.1, "drzwi", 0.6), (7.3, "drzwi", 0.5), (7.7, "pisk", 0.6)],
    "darby_smiech": [(1.6, "slide_down", 0.5), (1.7, "g:gasp_m", 0.45)],
    "darby_puszczeni": [(2.8, "papier", 0.5)],
    "teczka_zasiew": [(0.0, "zegar", 12.0)] + [(2.2 + 1.3 * n, "plask", 0.4) for n in range(7)],
    "plakaty": [(1.25 + 0.6 * n, "stuk", 0.7) for n in range(5)],
    "wellington_most": [(0.3, "pisk", 1.0), (0.6, "whoosh", 0.8), (1.55, "krach", 1.3), (1.55, "boom", 1.0), (1.7, "ogien", 8.0), (1.9, "szklo", 0.6)],
    "wellington_bonnie": [(0.0, "ogien", 10.0), (1.0, "syk", 1.6)],
    "farma": [(0.4, "wiadro", 0.5), (2.0, "wiadro", 0.5), (3.6, "lanie", 1.0)],
    "drzewo": [(0.3, "drut", 0.7), (3.0, "klakson", 0.9)],
    "oboz": [(1.0 + 1.6 * n, "metal", 0.35) for n in range(6)],  # bez ogniska: zimna fasola
    "rzeka": [(0.0, "woda", 3.0), (0.6, "plusk", 0.9), (1.1, "plusk", 0.6)],
    "platte": [(4.4, "szklo", 1.0)],
    "dexfield": [(1.6, "krzaki", 0.7), (3.0, "zamek", 0.6), (3.4, "zamek", 0.5)],
    "przeprawa": [(0.0, "brodzenie", 9.0)],
    "rodziny": [(1.0, "drzwi", 0.4), (4.0, "whoosh", 0.3)],
    "sowers": [(2.6, "krzaki", 0.9), (3.4, "szklo", 0.8), (4.6, "pisk", 0.8)],
    "odbicie": [(1.2, "kopanie", 1.4), (8.1, "skok", 0.5), (8.3, "skok", 0.5), (8.5, "skok", 0.5)],
    "simmons": [(1.6, "lomot", 1.0), (2.4, "lomot", 0.9), (3.2, "lomot", 1.0)],
    "hamer": [(0.0, "bujak", 1.9), (6.0, "zamek", 1.0)],
    "poscigi": [(5.0, "pisk", 1.0), (5.1, "whoosh", 0.8), (6.15, "krach", 1.0), (6.5, "kola", 4.0)],
    "hak_szuflada": [(1.2, "szuflada", 0.9), (2.3, "stuk", 0.6)],
    "hak_teczka": [(1.0, "teczka", 0.8)] + [(1.8 + 0.5 * n, "trzepot", 0.4) for n in range(8)] + [(2.8 + 0.5 * n, "stuk", 0.35) for n in range(8)]
                  + [(6.6, "kubek", 0.8), (7.2, "krzeslo", 0.7)],
    "podkreslenie": [(2.0, "olowek", 2.0), (4.6, "olowek", 1.8)],
    "hamer_motel": [(0.4, "dzwonek", 0.9), (1.0, "whoosh", 0.3)],
    "mapa": [(1.4 + 1.2 * n, "stuk", 0.7) for n in range(4)] + [(1.6 + 1.2 * n, "nitka", 0.8) for n in range(1, 4)],
    "petle": [(0.8, "olowek", 8.5), (9.6, "stuk", 0.5), (9.9, "stuk", 0.5)],
    "grapevine": [(0.5, "dzwony", 6.0)],
    "grapevine_cien": [(2.0, "thud", 0.7), (2.3, "thud", 0.6), (2.5, "krach", 0.8), (2.6, "boom", 0.9)],
    "tullis": [(0.6, "dzwon", 1.0), (6.0, "dzwon", 0.8)],
    "gazety_zle": [(2.4 + 0.4 * n, "zgniot", 0.6) for n in range(5)] + [(3.3 + 0.4 * n, "plask", 0.3) for n in range(5)] + [(0.0, "gwar", 10.0)],
    "listy_gon": [(0.8 + 1.0 * n, "stuk", 0.6) for n in range(4)] + [(0.8 + 1.0 * n, "papier", 0.4) for n in range(4)] + [(8.7, "zamek", 0.7)],
    "commerce": [(0.0, "bloto", 9.5)],
    "commerce_cien": [(2.6, "thud", 0.6), (5.6, "drzwi", 0.6)],
    "prasa_cygaro": [(0.0, "prasa", 7.6), (8.2, "zegar", 7.0), (9.8, "plask", 0.6)],
    "methvin": [(3.0, "papier", 0.7), (6.0, "krzeslo", 0.4)],
    "wiersz": [(0.6, "papier", 0.5), (0.0, "silnik_jalowy", 12.0)],
    "shreveport": [(3.4, "drzwi", 0.7), (9.6, "drzwi", 0.5), (0.0, "gwar_cichy", 13.5)],
    "noc": [(0.0, "komary", 12.5), (7.0, "klaps_reka", 0.7)],
    "zasadzka_rano": [(1.0, "lewarek", 1.5)],
    "kanapka": [(0.0, "papierek", 7.6)],
    "zwolnienie": [(0.6, "zwir", 1.6)],
    "zasadzka": [(0.5, "szklo", 0.8), (1.4, "szklo", 0.7), (2.6, "zgrzyt", 1.6), (3.7, "thud", 0.4)],
    "dym": [(1.5, "krzaki", 1.0), (6.6, "whoosh", 0.25)],
    "pamiatki": [(0.0, "gwar", 13.5), (0.0, "tlum", 13.5), (3.0, "nozyczki", 0.7), (4.2, "nozyczki", 0.7), (7.0, "gwizdek", 0.9)],
    "darby_zaklad": [(1.6, "rekawiczka", 0.7), (3.0, "rekawiczka", 0.7), (0.0, "zegar", 8.5)],
    "pogrzeby": [(0.5, "dzwon", 1.0), (5.5, "dzwon", 0.8)],
    "auto_jarmark": [(1.5, "coin", 0.5), (2.6, "coin", 0.5), (4.0, "coin", 0.4), (0.0, "tlum", 10.5), (0.0, "karuzela", 10.5), (0.0, "gwar", 10.5)],
    "blanche_po": [(0.6, "podlewanie", 9.0)],
    "hamer_ganek": [(2.0, "papier", 0.6), (3.4, "whoosh", 0.3)],
    "gra": [(0.0, "szum_ekranu", 1.6), (1.6, "chip_start", 0.9)] + [(2.0 + 0.25 * n, "klik", 0.25) for n in range(22)],
    "koniec": [(3.0, "papier", 0.8), (4.6, "plask", 0.6), (4.9, "plask", 0.6), (7.0, "teczka", 0.9), (10.0, "kurtyna_z", 1.0)],
    "dzieki": [(0.6, "oklaski", 5.6), (1.0, "wiwat", 5.2)] + [(1.2 + 0.45 * n, "stuk", 0.25) for n in range(8)],
}
# Gagi (docs/filmy/bonnie-i-clyde/GAGI.md; reżyser 19.11: „gagi robimy wszystkie”): dźwięk w tej samej chwili co gag.
GAGI_DZWIEK = {
    "zdjecie": [(2.05, "papier", 0.2), (3.6, "whoosh", 0.22), (3.85, "whoosh", 0.2), (4.25, "klik", 0.6)],
    "hak_cygaro": [(1.1, "slide_down", 0.45), (5.05, "whoosh", 0.4), (6.1, "boing_m", 0.6)],
    "indyki": [(5.0, "indyk", 0.9), (3.9, "skok", 0.8), (4.05, "skok", 0.8)],
    "slub": [(7.7, "nitka", 1.0), (7.85, "wahwah_k", 0.45), (4.4, "gwiazdka", 0.35)],
    "kawiarnia": [(7.0 + 0.55 * n, "papier", 0.45) for n in range(5)],
    "kuchnia": [(8.2, "slide_up", 0.4), (9.5, "kajdanki", 0.7)],
    "akt2": [(9.05, "klakson", 0.6)],
    "stacja": [(6.6, "trzepot", 0.7)],
    "joplin_dom": [(9.25, "slide_up", 0.4), (9.85, "slide_down", 0.4)],
    "ciemnia": [(5.6, "plusk", 0.6)],
    "kiosk": [(9.6, "papier", 0.3), (9.9, "trzepot", 0.6), (11.4, "coin", 0.7)],
    "darby_auto": [(1.6, "klik", 0.4)] + [(c, "kaszel_silnika", 0.9) for c in (2.0, 2.7, 3.4, 4.6)] + [(6.0, "pisk", 0.8)],
    "darby_tyl": [(9.6, "slide_up", 0.5)],
    "darby_puszczeni": [(5.3, "whoosh", 0.5), (5.6, "whoosh", 0.3)],
    "oboz": [(1.5, "gwiazdki", 2.9), (4.4, "slide_down", 0.5), (4.7, "boing", 0.7)],
    "rodziny": [(9.0, "papier", 0.5), (10.6, "klik", 0.3)],
    "hamer_motel": [(8.85 + 0.15 * n, "metal", 0.7 - 0.06 * n) for n in range(6)],
    "dzien20": [(10.6, "skrzydla", 0.6), (11.45, "plask", 0.8)],
    "mapa": [(6.1, "nitka", 0.7), (6.6, "klik", 0.4)],
    "listy_gon": [(8.8, "kopyta", 4.0), (8.8, "kola", 4.0)] + [(c, "werbel_fx", 0.8) for c in (9.4, 9.85, 10.3)],
    "prasa_cygaro": [(3.0, "papier", 0.4), (5.6, "zapalka", 0.8)],
    "noc": [(9.7 + 0.3 * n, "plask", 0.45) for n in range(3)] + [(10.6, "plask", 0.95)],
    "kanapka": [(5.3, "plask", 0.3)],
    "auto_jarmark": [(c + 0.5, "coin", 0.45) for c in (3.9, 4.5, 5.1, 5.6, 6.0, 6.4, 6.7, 7.0)] + [(8.0, "kasa", 0.6)]
                    + [(8.0 + 0.04 * n, "coin", 0.35) for n in range(14)],
    "gra": [(6.3, "chip_start", 0.6), (6.85, "thud", 0.4)],
    "dzieki": [(6.4, "kurtyna_z", 0.9), (7.0, "zgrzyt", 1.0), (8.0, "kurtyna_z", 0.8), (8.25, "lomot", 0.8), (8.4, "whoosh", 0.3)],
    # druga seria gagów 31–46 (reżyser 19.11: „więcej gagów”) — same zatwierdzone rodzaje dźwięku
    "wagon": [(11.2, "klik", 0.5), (11.3, "trzepot", 0.6)],
    "prasa": [(6.5, "whoosh", 0.4), (6.9, "plask", 0.8), (8.0, "papier", 0.5)],
    "cela": [(1.6 + 0.55 * n, "zgniot", 0.35) for n in range(12)],
    "matka_obietnica": [(8.3 + 0.45 * n, "zawieszka", 0.5) for n in range(3)] + [(9.8, "whoosh", 0.5), (10.25, "drzwi", 0.5)],
    "buck": [(11.0, "whoosh", 0.4)],
    "joplin_karty": [(10.0, "karty", 0.6), (10.45, "knock", 0.3)],
    "plakaty": [(5.0, "boing", 0.7)],
    "farma": [(5.15, "wiadro", 0.7)],
    "drzewo": [(8.3, "skrzydla", 0.6)],
    "simmons": [(3.25, "nitka", 0.8)],
    "hamer": [(4.2, "bujak", 4.6)],
    "podkreslenie": [(6.2, "klik", 0.7)],
    "methvin": [(11.3, "papier", 0.4)],
    "pozegnanie": [(3.8, "nitka", 0.4)],
    "shreveport": [(11.1, "drzwi", 0.5)],
    "posse": [(11.7, "knock", 0.5)],
}
for _k, _ev in GAGI_DZWIEK.items():
    ZDARZENIA.setdefault(_k, []).extend(_ev)
ZDARZENIA["hak_joplin_rzeczy"] = ZDARZENIA["joplin_rzeczy"]
# Zapowiedź: każde cięcie akcentuje uderzenie (jak w zwiastunie), pierwsze mocniej.
for _k in ("zap_wellington_most", "zap_zdjecie", "zap_prasa", "zap_kiosk", "zap_kaufman", "zap_poscigi", "zap_boyd", "zap_sowers",
           "zap_hamer", "zap_zasadzka"):
    ZDARZENIA.setdefault(_k, []).append((0.0, "boom", 0.55))
ZDARZENIA["zap_wellington_most"].append((0.0, "whoosh", 0.6))


# =====================================================================================================================
# PRZEGLĄD FILMU: podsłuch funkcji ujęć (auta, lalki, błyski, tabliczki, zawieszki, nitki, dekoracje)
# =====================================================================================================================

SKAN_DT = 0.08


def skan():
    import render as R
    import scena
    import ujecia_a as A
    import ujecia_b as B
    import zestaw_bc as J
    S = {"t": 0.0, "i": 0, "na": 0, "nl": {}}
    auta, lalki, jedno, dekor, noc = {}, {}, {}, {}, {}

    def pierwszy(klucz, at, rodzaj, extra=None):
        if klucz not in jedno:
            jedno[klucz] = (at, rodzaj, extra, S["i"])

    def w_auto(orig, rodzaj):
        def f(st, t, x, h=230, *a, **kw):
            k = S["na"]
            S["na"] += 1
            dr = kw.get("droga")
            auta.setdefault((S["i"], k), []).append((S["t"], x if dr is None else dr, h, rodzaj, kw.get("napis")))
            return orig(st, t, x, h, *a, **kw)
        return f

    def w_lalka(orig):
        def f(st, t, key, x, h=300, *a, **kw):
            if not kw.get("siedzi"):
                n = S["nl"].get(key, 0)
                S["nl"][key] = n + 1
                lalki.setdefault((S["i"], key, n), []).append((S["t"], x, h))
            return orig(st, t, key, x, h, *a, **kw)
        return f

    def w_blysk(st, x, y, p, t, t0, r=260, kolor=(1.0, 0.9, 0.6), dl=0.12):
        at = S["t"] - t + t0
        pierwszy(("b", S["i"], round(t0, 2), round(x)), at, "flesz" if min(kolor) > 0.94 else "strzal")

    def w_podpis(w, t, txt, x, y, t0, dur=2.8):
        pierwszy(("p", S["i"], txt, round(t0, 2)), S["t"] - t + t0, "podpis", txt)

    def w_tab(w, t, txt, x, y, t0, dur=2.2):
        pierwszy(("t", S["i"], txt, round(t0, 2)), S["t"] - t + t0, "tab", txt)

    def w_koniec(st, w, t, *a, **kw):
        noc[S["i"]] = max(noc.get(S["i"], 0.0), float(w.get("noc") or 0.0))
        for txt, x, y, k in w.zawieszki:
            if k > 0:
                pierwszy(("z", S["i"], txt), S["t"], "zawieszka", txt)

    orig_hang = J.hang

    def w_hang(st, spr, x, y, p, k=1.0, t=0.0, seed=1, *a, **kw):
        b = scena.BUDOWA["t"]
        if 0 < k < 0.5 and (b is None or b > 1.8):
            pierwszy(("h", S["i"], seed), S["t"], "nitka")
        return orig_hang(st, spr, x, y, p, k, t, seed, *a, **kw)

    def w_dekor(nazwa, orig):
        def f(*a, **kw):
            d = dekor.setdefault(S["i"], {})
            d[nazwa] = d.get(nazwa, 0) + 1
            if nazwa == "las" and kw.get("swit"):
                d["swit"] = 1
            if kw.get("noc"):
                d["noc"] = 1
            return orig(*a, **kw)
        return f

    for M in (A, B):
        M.auto = w_auto(scena.auto, "auto")
        M.lalka = w_lalka(scena.lalka)
        M.blysk = w_blysk
        M.podpis = w_podpis
        M.tab = w_tab
        M.koniec = w_koniec
        for nazwa in ("preria", "miasto", "wnetrze", "eastham", "las", "wawoz", "parawan", "drukarnia", "mapa_scena", "cmentarz", "kino",
                      "teatr_gazet", "west_dallas", "ciemnosc"):
            if hasattr(M, nazwa):
                setattr(M, nazwa, w_dekor(nazwa, getattr(scena, nazwa)))
    B.motocykl = w_auto(scena.motocykl, "moto")
    scena.lalka = w_lalka(scena.lalka)  # cienie (scena.cien) i pasażerowie (siedzą — pomijani)
    J.hang = w_hang
    starts = [a for a, b, *_ in R.SCENES]
    import bisect
    t = 0.0
    while t < R.DUR:
        i = max(0, bisect.bisect_right(starts, t) - 1)
        S.update(t=t, i=i, na=0, nl={})
        R.uloz(t)
        t += SKAN_DT
    J.hang = orig_hang
    return auta, lalki, jedno, dekor, noc


def _gladko(v, k=3):
    if len(v) < k:
        return v
    return np.convolve(v, np.ones(k) / k, mode="same")


def silniki(auta, n):
    """Silnik każdego auta z prędkości na ekranie (wolno: cicho, szybko: wyżej i głośniej); radiowóz z syreną; pisk przy
    gwałtownym hamowaniu."""
    out = np.zeros(n)
    piski = []
    for (i, k), rec in auta.items():
        if len(rec) < 3:
            continue
        ts = np.array([r[0] for r in rec])
        xs = np.array([r[1] for r in rec], float)
        h = rec[0][2]
        rodzaj, napis = rec[0][3], rec[0][4]
        v = np.abs(np.diff(xs)) / np.maximum(np.diff(ts), 1e-3)
        v = np.where(np.diff(ts) > 0.2, 0, v)
        v = _gladko(np.concatenate([v[:1], v]), 4)
        if v.max() < 60:
            continue
        a0, a1 = ts[0], ts[-1] + SKAN_DT
        i0 = N(a0)
        L = min(n - i0, N(a1 - a0))
        if L <= 0:
            continue
        tl = a0 + tt(L)
        s = np.clip(np.interp(tl, ts, v) / 650.0, 0, 1.6)
        f = (30.0 if rodzaj == "auto" else 58.0) * (1 + 0.85 * s)
        ph = 2 * math.pi * np.cumsum(f) / SR
        x = sum(np.sin(k_ * ph + 0.7 * k_) / k_ for k_ in range(1, 8)) + 0.5 * np.sin(0.5 * ph)
        x += _szum(L, 150, 1800, int(i * 10 + k)) * (0.4 + s) * 0.5
        glos = np.clip(s * 2.0, 0, 1) ** 1.5 * (0.13 if rodzaj == "auto" else 0.1) * np.clip(h / 230.0, 0.6, 1.3)
        glos *= np.minimum(1, tt(L) / 0.15) * np.clip((tl[-1] - tl) / 0.15, 0, 1)
        out[i0:i0 + L] += x * glos
        if napis == "SHERIFF":
            fs = 760 + 380 * (0.5 + 0.5 * np.sin(2 * math.pi * tl / 1.4))
            phs = 2 * math.pi * np.cumsum(fs) / SR
            out[i0:i0 + L] += (np.sin(phs) + 0.3 * np.sin(2 * phs)) * np.clip(s * 2, 0, 1) * 0.035
        for j in range(5, len(v)):  # gwałtowne hamowanie
            if v[j - 5] > 520 and v[j] < 140 and (not piski or ts[j] - piski[-1] > 1.5):
                piski.append(ts[j] - 0.3)
    for at in piski:
        s = pisk() * 0.55
        i = N(at)
        out[i:i + len(s)] += s[:n - i]
    return out


def kroki(lalki, n):
    """Drewniane kroki lalek: ruch po scenie stuka w deski teatru, tempo kroku rośnie z prędkością."""
    out = np.zeros(n)
    ile = 0
    for (i, key, nr), rec in lalki.items():
        if len(rec) < 3:
            continue
        ts = np.array([r[0] for r in rec])
        xs = np.array([r[1] for r in rec], float)
        h = rec[0][2]
        v = np.abs(np.diff(xs)) / np.maximum(np.diff(ts), 1e-3)
        v = np.where(np.diff(ts) > 0.2, 0, v)
        faza = 0.0
        r = _r(sum(map(ord, key)) + nr)
        for j, vj in enumerate(v):
            if vj < 55:
                faza = 0.0
                continue
            krok = float(np.clip(0.48 - vj / 1800, 0.22, 0.48))
            faza += SKAN_DT
            if faza >= krok:
                faza -= krok
                s = knock(r.uniform(330, 520), 0.12) * 0.2 * float(np.clip(h / 300.0, 0.5, 1.3))
                a = N(ts[j])
                out[a:a + len(s)] += s[:n - a]
                ile += 1
    print(f"kroki: {ile}")
    return out


def tlo(rodzaj, sec, seed, noc_, swit=False):
    """Tło miejsca: wiatr prerii, ulica, pokój, las (ptaki / świt / świerszcze), wąwóz, pole w upale, kino, cisza sali."""
    n = N(sec)
    r = _r(seed)
    t = tt(n)
    slow = np.interp(t, np.linspace(0, sec, max(2, int(sec * 0.5) + 2)), r.uniform(0.4, 1.0, max(2, int(sec * 0.5) + 2)))

    def ptaki(gestosc, g):
        x = np.zeros(n)
        for _ in range(int(sec * gestosc)):
            L = N(r.uniform(0.08, 0.18))
            i = int(r.uniform(0, max(1, n - L)))
            f0 = r.uniform(2600, 4200)
            x[i:i + L] += _sweep(f0, f0 * r.uniform(0.8, 1.3), L / SR) * np.sin(np.pi * tt(L) / (L / SR)) * g
        return x

    def swierszcze(g):
        x = np.zeros(n)
        for _ in range(int(sec * 1.6)):
            L = N(0.35)
            i = int(r.uniform(0, max(1, n - L)))
            x[i:i + L] += np.sin(2 * math.pi * r.uniform(4200, 4800) * tt(L)) * (np.sin(2 * math.pi * 28 * tt(L)) > 0) * g
        return x

    if rodzaj == "preria":
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.045 + (ptaki(0.25, 0.01) if not noc_ else 0)
    elif rodzaj == "miasto":
        x = band(r.normal(0, 1, n), 60, 400) * 0.03 * (0.7 + 0.3 * slow)
    elif rodzaj == "pokoj":
        x = band(r.normal(0, 1, n), 60, 300) * 0.018
    elif rodzaj == "las":
        x = band(r.normal(0, 1, n), 200, 1200) * slow * 0.03 + (ptaki(2.2 if swit else 0.8, 0.012) if not noc_ else 0)
    elif rodzaj == "wawoz":
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.05 + band(r.normal(0, 1, n), 300, 3000) * 0.02
    elif rodzaj == "pole":  # Eastham w upale: wiatr i cykady
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.03 + band(r.normal(0, 1, n), 4000, 6500) * (0.5 + 0.5 * np.sin(2 * math.pi * 31 * t)) * 0.012
    elif rodzaj == "kino":
        x = projektor(sec)
    elif rodzaj == "drukarnia":
        x = prasa(sec)
    elif rodzaj == "fabryka":
        x = band(r.normal(0, 1, n), 40, 220) * 0.05 + band(r.normal(0, 1, n), 2000, 6000) * 0.005
    elif rodzaj == "cmentarz":
        x = band(r.normal(0, 1, n), 150, 800) * slow * 0.03 + ptaki(0.15, 0.008)
    elif rodzaj == "sala":
        x = band(r.normal(0, 1, n), 80, 500) * 0.012
    else:
        x = np.zeros(n)
    if noc_ and rodzaj in ("preria", "las", "miasto", "wawoz", "cmentarz", "pole"):
        x = x * 0.7 + swierszcze(0.012)
    return x


def rodzaj_tla(d):
    if not d:
        return "sala"
    for k, v in (("drukarnia", "drukarnia"), ("kino", "kino"), ("parawan", "sala"), ("ciemnosc", "sala"), ("wnetrze", "pokoj"),
                 ("mapa_scena", "pokoj"), ("wawoz", "wawoz"), ("las", "las"), ("eastham", "pole"), ("cmentarz", "cmentarz"),
                 ("west_dallas", "fabryka"), ("miasto", "miasto"), ("preria", "preria"), ("teatr_gazet", "sala")):
        if k in d:
            return v
    return "sala"


def zapisz(path, x):
    x = np.tanh(x * 1.2) * 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    import render as R
    us = ujecia()
    total = R.DUR
    n = N(total)
    fx, voice = np.zeros(n), np.zeros(n, bool)
    starts, durs = {}, {}
    print("przegląd filmu (podsłuch ujęć)…", flush=True)
    auta, lalki, jedno, dekor, noc = skan()
    print(f"auta: {len(auta)} torów, lalki: {len(lalki)} torów, znaki: {len(jedno)}", flush=True)
    events = 0
    for idx, (a, b, *_) in enumerate(R.SCENES):
        klucz = R.KOL[idx]
        sec = b - a
        starts[klucz], durs[klucz] = a, sec
        u = us[idx]
        vs, vl = okno_kwestii(u[7], klucz in R.HAK if hasattr(R, "HAK") else False)
        if vl:
            voice[N(a + vs):N(a + vs + vl)] = True
        src, od = (R.WYCINEK[klucz][0], R.WYCINEK[klucz][1]) if klucz in R.WYCINEK else (klucz, 0.0)
        d = dekor.get(idx, {})
        if klucz != "prasa_cygaro":
            amb = tlo(rodzaj_tla(d), sec + 0.3, idx, noc.get(idx, 0) > 0.5 or d.get("noc"), d.get("swit"))
            i = N(a)
            fx[i:i + len(amb)] += amb[:n - i]
        evs = [(at - od, kind, g) for at, kind, g in ZDARZENIA.get(src, []) if od <= at < od + sec]
        if src != klucz:
            evs += [e for e in ZDARZENIA.get(klucz, [])]
        g = R.GRANICE[idx]
        zam, dl, czekaj, otw = R.KURTYNA
        if g["ostatnie_aktu"] and idx < len(R.SCENES) - 1 and g["akt"] + 1 not in R.BEZ_KURTYNY:
            evs += [(sec - zam, "kurtyna_z", 1.0), (sec - zam + dl - 0.05, "klaps", 0.8)]
        elif g["pierwsze_aktu"] and idx > 0 and g["akt"] not in R.BEZ_KURTYNY:
            evs += [(czekaj, "kurtyna_r", 1.0)]
        if klucz in R.BUDUJ and klucz not in R.WYCINEK:
            evs += [(dd, "whoosh", 0.3) for dd in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(dd, "knock", 0.25) for dd in (0.75, 1.05, 1.4, 1.7)]
        for at, kind, gg in evs:
            if at >= sec or at < 0:
                continue
            if kind in NOWE and kind not in NOWE_ZATWIERDZONE and os.environ.get("NOWE_DZWIEKI") != "1":
                continue  # nowy rodzaj dźwięku czeka na zgodę reżysera (próbka)
            if kind.startswith("g:"):
                s = glos(kind[2:], gg)
            elif kind in DLUGIE:
                s = DLUGIE[kind](min(gg, sec - at))
            else:
                s = KROTKIE[kind]() * gg
            j = N(a + at)
            fx[j:j + len(s)] += s[:n - j]
            events += 1
    # znaki z podsłuchu: tabliczki, podpisy, zawieszki, nitki, błyski
    for key, (at, rodzaj, extra, i) in jedno.items():
        if rodzaj == "tab":
            kind = TAB_DZWIEK.get(extra, "tab")
            s = KROTKIE[kind]() * (0.9 if kind == "tab" else 1.0) if kind else np.zeros(1)
            g_ = TAB_GLOS_UJ.get((R.KOL[i], extra)) or TAB_GLOS.get(extra)
            if g_:
                v = smiech_tlum() if g_ == "*smiech_tlum" else glos(g_, GLOS_G.get(g_, 0.5))
                if kind in ("wahwah", "wahwah_k"):  # najpierw głos, potem puzon
                    s = np.concatenate([np.zeros(N(0.7)), s])
                s = _s(s, np.concatenate([np.zeros(N(0.05)), v]))
        elif rodzaj == "podpis":
            s = podpis_snd()
        elif rodzaj == "zawieszka":
            s = stempel() if str(extra).startswith("DAY") else zawieszka_snd()
        elif rodzaj == "nitka":
            s = nitka()
        elif rodzaj == "flesz":
            s = flesz() * 0.9
        else:  # strzał: za parawanem przytłumiony
            s = strzal("parawan" in dekor.get(i, {}))
        j = N(at)
        if 0 <= j < n:
            fx[j:j + len(s)] += s[:n - j]
            events += 1
    fx += silniki(auta, n)
    fx += kroki(lalki, n)
    fx *= sciszanie(voice, POD_KWESTIA_EFEKTY)
    mus = muzyka(total, starts, durs, voice)
    OUT.mkdir(exist_ok=True)
    zapisz(OUT / "efekty.wav", fx)
    zapisz(OUT / "muzyka.wav", mus)
    rms = lambda x: 20 * math.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    print(f"efekty: {events} zdarzeń + tło, silniki, kroki | muzyka: {len(CUES)} tematów | {total:.1f} s | "
          f"RMS muzyka {rms(mus):.1f} dB, efekty {rms(fx):.1f} dB", flush=True)


if __name__ == "__main__":
    main()
