"""Dźwięk filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” bez lektora: muzyka (ścieżka Muzyka, a2)
i efekty (ścieżka Efekty, a3). Reżyser 28.11.2026: „po lektorze” (najpierw lektor, potem muzyka i efekty).

Synteza w numpy, wzór: output/bonnie-i-clyde/efekty.py (dźwięki bazowe, kurtyna, wyrównanie tematów, ściszanie pod
lektorem, tempo z cięć, przystanki na puentach gagów, podsłuch ujęć) — z brzmieniem Kaukazu XIX wieku i Diuny:
- Muzyka z tematów (CUES): góry (pandur, duduk albo zurna, cichy doli), lezginka (doli w 6/8, zurna, harmonia) w akcji
  i pościgach, imperium (marsz wojskowy: werbel, blacha, tuba) przy carze, raportach i pieczątkach, lament (duduk nad
  burdonem) przy zakładniku, synu i kapitulacji, Rosja (bałałajka) w drodze na północ i w Kałudze, walc w Petersburgu,
  pustynia (burdon, bendir, flet ney, frygijska skala) w Diunie, napięcie i mrok jak w „Bonnie and Clyde”. Motyw Szamila
  (A–G–F–E–D) wraca: przy przedstawieniu, w górach, w uścisku z synem (MOTYW) i nad białą flagą.
- Przed szczytami muzyka milknie (CISZA): skok w Gimry, zasadzka, uścisk na rzece, biała flaga na Gunibie.
- Efekty z podsłuchu ujęć (render.uloz co 0,08 s): konie i zaprzęgi (tętent i koła z prędkości), lalki (drewniane kroki),
  błyski (muszkiety, armaty, za parawanem przytłumione), podpisy i okrzyki (dźwięk według napisu), zawieszki, nitki,
  pieczątki, koza, robak z Diuny, laska maszynisty, kartki kalendarza, ogień; do tego tło miejsca (wiatr w górach, śnieg,
  pustynia, rzeka, las, dwór w Gruzji, gabinet z zegarem) i wydarzenia ręczne (ZDARZENIA) na słowach lektora (ujecia_a.sl).
- Bez głosów ludzi (wytyczne 1.14): nowe rodzaje dźwięków idą najpierw jako próbka do reżysera (probka_dzwieku.py).

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
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/szamil-diuna/ujecia"))
from dane import HAK, okno_kwestii, ujecia  # noqa: E402


class Sek(float):
    """Sekunda na osi Studio (z markera reżysera), nie w rytmie akcji ujęcia — nie przechodzi przez render.czas_ujecia."""


def rr(s):
    return Sek(s)


SR = 44100
OUT = Path(os.environ.get("DZWIEK_DO", HERE / "dzwiek_en"))
RNG = np.random.default_rng(27)


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


# ---------- dźwięki (z „Bonnie and Clyde” efekty.py) ----------

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


def s_walc(P, sec, r, o):
    """Walczyk salonowy na pianinie (Bonnie recytuje wiersze i marzy o scenie): um-pa-pa, melodia z ozdobnikiem."""
    b = 60.0 / o.get("bpm", 132)
    key = o.get("key", 62)
    prog = [(0, "M"), (0, "M"), (7, "7"), (7, "7"), (7, "7"), (7, "7"), (0, "M"), (5, "M")]
    last, bar = 76, 0
    while bar * 3 * b < sec:
        tb = bar * 3 * b
        root, q = prog[bar % 8]
        kr = (key + root) % 12
        P(tb, piano(40 + kr, b * 0.9, 0.42))
        for beat in (1, 2):
            for m in akord(kr, q, 55, 67)[:3]:
                P(tb + beat * b, piano(m, b * 0.45, 0.24))
        wz = ((0, 1), (1, 1), (2, 1)) if bar % 4 == 1 else ((0, 2), (2, 1)) if bar % 2 else ((0, 1.5), (1.5, 0.5), (2, 1))
        for pos, L in wz:
            last = _melodia(r, (kr, q), 69, 86, last)
            P(tb + pos * b, piano(last, L * b * 0.95, float(r.uniform(0.5, 0.62)), 3))
        bar += 1


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


def swierszcze(sec):
    """Świerszcze nocą — od chwili, w której zapada noc (tło miejsca liczy noc dla całego ujęcia, ujęcia 20–21 mają dzień i noc)."""
    n = N(sec)
    r = _r(int(sec * 100) + 7)
    x = np.zeros(n)
    for _ in range(int(sec * 2.2)):
        L = N(0.35)
        i = int(r.uniform(0, max(1, n - L)))
        x[i:i + L] += np.sin(2 * math.pi * r.uniform(4200, 4800) * tt(L)) * (np.sin(2 * math.pi * 28 * tt(L)) > 0) * 0.016
    t = tt(n)
    return x * np.minimum(1, t / 0.8) * np.clip((sec - t) / 0.4, 0, 1)


def pew():
    """Strzał w grze 8-bit: krótki zjazd prostokątnej fali z wysoka w dół (pikselowe kule, ujęcie 117)."""
    n = N(0.16)
    t = tt(n)
    f = 1800 * (300 / 1800) ** (t / 0.16)
    ph = 2 * math.pi * np.cumsum(f) / SR
    return np.sign(np.sin(ph)) * np.exp(-t / 0.08) * 0.1


def deszcz(sec):
    """Deszcz przy słońcu (ujęcie 112): szum kropli z pojedynczymi pacnięciami, wchodzi i wychodzi łagodnie."""
    n = N(sec)
    t = tt(n)
    r = _r(int(sec * 10) + 3)
    x = band(r.normal(0, 1, n), 900, 7000) * 0.05
    for _ in range(int(sec * 14)):
        L = N(0.03)
        i = int(r.uniform(0, max(1, n - L)))
        x[i:i + L] += band(r.normal(0, 1, L), 2000, 8000) * env(L, 0.001, 0.01) * r.uniform(0.05, 0.15)
    return x * np.minimum(1, t / 1.2) * np.clip((sec - t) / 0.6, 0, 1)


def tada():
    """Mała fanfara „ta-da!” (ukłon Bonnie na podium): dwa akordy blachy."""
    a = sum(blacha(m, 0.14, 0.5) for m in (67, 72, 76))
    b = sum(blacha(m, 0.7, 0.6) for m in (72, 76, 79))
    return np.concatenate([a, np.zeros(N(0.04)), b]) * 0.8


# =====================================================================================================================
# KAUKAZ I DIUNA: instrumenty (synteza addytywna jak wyżej; nuty w pamięci podręcznej)
# =====================================================================================================================

@lru_cache(maxsize=4096)
def _pandur(m, vel, krotki):
    """Pandur / czangur / bałałajka: szarpana struna, ciemniejsza i dłuższa od banjo; krotki — tremolo (bałałajka)."""
    f = mtof(m)
    L = N(0.35 if krotki else 1.4)
    t = tt(L)
    ph = np.random.default_rng(int(m) + 5).uniform(0, 6.28, 24)
    out = np.zeros(L)
    for k in range(1, 14):
        if k * f > 8000:
            break
        tau = (0.16 if krotki else 0.9) / (1 + 0.18 * k)
        out += (1 / k ** 1.05) * (1 + 0.5 * math.sin(k * 0.9)) * np.sin(2 * math.pi * k * f * 1.0006 ** k * t + ph[k]) * np.exp(-t / tau)
    npick = N(0.008)
    out[:npick] += band(np.random.default_rng(int(m) + 13).normal(0, 1, npick), 1500, 6000) * 0.4
    return out * np.minimum(1, t / 0.0015) * vel * 0.09


def pandur(m, vel=0.5, krotki=False):
    return _pandur(int(m), _q(vel), bool(krotki))


@lru_cache(maxsize=2048)
def _zurna(m, dur, vel):
    """Zurna: podwójny stroik, jasna i nosowa, szybki atak, wąskie vibrato."""
    return _dech(m, dur, vel, ((1150, 500, 1.0), (2400, 700, 0.85), (3600, 900, 0.45)), vib=9, atak=0.025, szum=0.025, seed=41) * 0.12


def zurna(m, dur=0.4, vel=0.6):
    return _zurna(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=2048)
def _duduk(m, dur, vel):
    """Duduk: ciepły, matowy stroik, wolny atak, szerokie vibrato i podjazd do nuty."""
    return _dech(m, dur, vel, ((520, 260, 1.0), (1150, 380, 0.4), (2400, 500, 0.08)), vib=16, bend=-35, atak=0.14, szum=0.05,
                 seed=43) * 0.17


def duduk(m, dur=1.0, vel=0.6):
    return _duduk(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=2048)
def _ney(m, dur, vel):
    """Flet ney (pustynia): dużo oddechu, mało alikwotów."""
    return _dech(m, dur, vel, ((750, 450, 1.0), (1600, 600, 0.2)), vib=7, atak=0.18, szum=0.2, seed=47) * 0.16


def ney(m, dur=1.0, vel=0.6):
    return _ney(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=2048)
def _akordeon(m, dur, vel):
    """Garmoszka: dwa lekko rozstrojone stroiki (piłowe), pasmo 180–5000 Hz, lekkie tremolo miecha."""
    f = mtof(m)
    L = N(dur + 0.1)
    t = tt(L)
    out = np.zeros(L)
    for c in (-7, 7):
        fc = f * 2 ** (c / 1200)
        out += sum((1 / k) * np.sin(2 * math.pi * k * fc * t) for k in range(1, 12) if k * fc < 7000)
    out = band(out, 180, 5000) * (1 + 0.05 * np.sin(2 * math.pi * 5.5 * t))
    return out / (np.abs(out).max() + 1e-9) * np.minimum(1, t / 0.03) * np.clip(1 - (t - dur) / 0.06, 0, 1) * vel * 0.07


def akordeon(m, dur=0.3, vel=0.5):
    return _akordeon(int(m), _q(dur), _q(vel))


@lru_cache(maxsize=None)
def dum(vel=0.6):
    """Doli: niskie uderzenie środka bębna."""
    return _s(drum(0.5, 78) * 0.55, knock(140, 0.2) * 0.3) * vel


@lru_cache(maxsize=None)
def tek(vel=0.5):
    """Doli: suche uderzenie brzegu."""
    n = N(0.12)
    t = tt(n)
    return _s(knock(780, 0.1) * 0.45, band(np.random.default_rng(52).normal(0, 1, n), 2500, 8000) * np.exp(-t / 0.015) * 0.2) * vel


@lru_cache(maxsize=None)
def bendir(vel=0.5):
    """Bęben ramowy (pustynia): głęboki, z długim szumem skóry."""
    n = N(1.1)
    return _s(drum(1.1, 58) * 0.6, band(np.random.default_rng(53).normal(0, 1, n), 100, 1500) * env(n, 0.005, 0.25) * 0.35) * vel


D_DORYCKA = (0, 2, 3, 5, 7, 9, 10)
FRYG_DOM = (0, 1, 4, 5, 7, 8, 10)
A_HARM = (0, 2, 3, 5, 7, 8, 11)
EOLSKA = (0, 2, 3, 5, 7, 8, 10)
JONSKA = (0, 2, 4, 5, 7, 9, 11)
# Motyw Szamila (D: A–G–F–E–D, w ćwierćnutach) i motyw syna (wznoszący); wracają w górach, w uścisku i nad białą flagą
MOTYW_OJCA = [(69, 1.0), (67, 0.5), (65, 0.5), (64, 1.0), (62, 2.0)]
MOTYW_SYNA = [(62, 0.5), (64, 0.5), (65, 1.0), (69, 2.5)]


def skala(key, tryb, lo, hi):
    return [m for m in range(lo, hi) if (m - key) % 12 in tryb]


def fraza(r, sk, start, n):
    """n nut melodii krokami po skali (1–2 stopnie), od dźwięku najbliższego `start`."""
    i = min(range(len(sk)), key=lambda j: abs(sk[j] - start))
    out = []
    for _ in range(n):
        out.append(sk[i])
        i = int(np.clip(i + int(r.choice((-2, -1, -1, 1, 1, 2))), 0, len(sk) - 1))
    return out


def _koniec_frazy(sk, m, key):
    """Fraza kończy się na toniką albo kwincie tematu (najbliższej)."""
    cele = [x for x in sk if (x - key) % 12 in (0, 7)]
    return min(cele, key=lambda x: abs(x - m)) if cele else m


def _graj_fraze(P, at, b, nuty, instr, vel=0.6, ozdoba=True):
    for j, (m, L) in enumerate(nuty):
        if ozdoba and j == 0:
            P(at - 0.07, instr(m + 2, 0.07, vel * 0.7))  # przednutka z góry
        P(at, instr(m, L * b * 0.95, vel))
        at += L * b
    return at


def s_gory(P, sec, r, o):
    """Góry: pandur w kwintach (D–A) na każdą ćwierćnutę, melodia duduka (albo zurny) frazami w doryckiej, cichy doli
    na opcję; motyw Szamila na początku tematu (opcja motyw)."""
    b = 60.0 / o.get("bpm", 76)
    key = o.get("key", 62)
    sk = skala(key, D_DORYCKA, 57, 81)
    instr = zurna if o.get("zurna") else duduk
    korzen = (0, 0, -2, 0, 5, 0, -2, -5)  # D D C D G D C A
    bar, last = 0, key + 7
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        r0 = key - 12 + korzen[bar % 8]
        for j, (d, v) in enumerate(((0, 0.5), (1.5, 0.28), (2, 0.4), (3, 0.3))):
            P(tb + d * b, pandur(r0 + (0, 7, 12, 7)[j], v))
        P(tb, pandur(r0 - 12, 0.32))
        if o.get("doli"):
            for d, s in ((0, dum(0.5)), (1.5, tek(0.35)), (2, dum(0.35)), (3, tek(0.3)), (3.5, tek(0.25))):
                P(tb + d * b, s)
        if bar % 2 == 0 and not o.get("bez_melodii"):
            if bar == 0 and o.get("motyw"):
                nuty = [(m - 62 + key, L) for m, L in MOTYW_OJCA]
            else:
                ms = fraza(r, sk, last, int(r.integers(3, 6)))
                Ls = [(1.5, 0.5, 2.0, 4.0), (1, 1, 1, 1, 4), (2, 1, 1, 4), (0.5, 0.5, 1, 2, 4), (1, 1, 2, 4)][int(r.integers(5))]
                nuty = list(zip(ms, Ls))
                nuty[-1] = (_koniec_frazy(sk, nuty[-1][0], key), nuty[-1][1])
            last = nuty[-1][0]
            _graj_fraze(P, tb + 0.05, b, nuty, instr, 0.62 if instr is zurna else 0.6)
        bar += 1


WZORY_LEZ = [((0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)), ((0, 2), (2, 1), (3, 2), (5, 1)), ((0, 3), (3, 1), (4, 1), (5, 1)),
             ((0, 1), (1, 1), (2, 1), (3, 3)), ((0, 1.5), (1.5, 0.5), (2, 1), (3, 1), (4, 2))]


def s_lezginka(P, sec, r, o):
    """Lezginka w 6/8: doli DUM–tek–DUM–tek–tek z przejściem co cztery takty, garmoszka na słabe części, bas pandura,
    zurna ósemkami w a-moll harmonicznej."""
    e = 60.0 / o.get("bpm", 150) / 3
    key = o.get("key", 57)
    sk = skala(key, A_HARM, 64, 88)
    prog = [(0, "m"), (0, "m"), (5, "m"), (7, "7"), (0, "m"), (5, "m"), (7, "7"), (0, "m")]
    bar, last = 0, key + 12
    while bar * 6 * e < sec:
        tb = bar * 6 * e
        root, q = prog[bar % 8]
        kr = (key + root) % 12
        for d, s in ((0, dum(0.75)), (2, tek(0.45)), (3, dum(0.6)), (4, tek(0.4)), (5, tek(0.5))):
            P(tb + d * e, s)
        if bar % 4 == 3:
            for d in (1, 3.5, 4.5):
                P(tb + d * e, tek(0.3))
        for d in (1, 2, 4, 5):
            for m in akord(kr, q, 57, 70)[:3]:
                P(tb + d * e, akordeon(m, e * 0.8, 0.3))
        bm = 40 + (kr - 40) % 12
        P(tb, pandur(bm, 0.5)), P(tb + 3 * e, pandur(bm + 7, 0.4))
        if not o.get("bez_zurny"):
            for pos, L in WZORY_LEZ[int(r.integers(len(WZORY_LEZ)))]:
                cand = [m for m in sk if abs(m - last) <= 4] or sk
                tony = [m for m in cand if (m - kr) % 12 in [(i) % 12 for i in Q_[q]]]
                last = int(r.choice(tony if tony and r.random() < 0.55 else cand))
                P(tb + pos * e, zurna(last, L * e * 0.92, float(r.uniform(0.5, 0.62))))
        bar += 1


def s_imperium(P, sec, r, o):
    """Imperium: marsz wojskowy 2/4 — bęben i werbel z werblem co cztery takty, tuba (bas) raz–dwa, akordy blachy na
    „i”, melodia blachy w kropkowanym rytmie; fanfara na wejście (opcja)."""
    b = 60.0 / o.get("bpm", 112)
    key = o.get("key", 60)
    prog = [(0, "M"), (0, "M"), (7, "7"), (7, "7"), (0, "M"), (5, "M"), (7, "7"), (0, "M")]
    t0 = 0.0
    if o.get("fanfara"):
        for d, m, L in ((0.0, 67, 0.12), (0.15, 67, 0.12), (0.3, 72, 0.9)):
            P(d, blacha(m - 60 + key, L, 0.7))
        for k in range(10):
            P(0.03 * k, werbel(0.2 + 0.05 * k))
        t0 = 1.3
    bar, last = 0, key + 16
    while t0 + bar * 2 * b < sec:
        tb = t0 + bar * 2 * b
        root, q = prog[bar % 8]
        kr = (key + root) % 12
        P(tb, stopa(0.6)), P(tb + b, werbel(0.45)), P(tb + 1.5 * b, werbel(0.22))
        if bar % 4 == 3:
            for k in range(6):
                P(tb + b + k * b / 6, werbel(0.18 + 0.05 * k))
        P(tb, bas(36 + kr, 0.55, b * 0.8)), P(tb + b, bas(36 + (kr + 7) % 12, 0.45, b * 0.8))
        for d in (0.5, 1.5):
            for m in akord(kr, q, 55, 67)[:3]:
                P(tb + d * b, blacha(m, b * 0.3, 0.3))
        if not o.get("bez_melodii"):
            for pos, L in [((0, .75), (.75, .25), (1, 1)), ((0, .5), (.5, .5), (1, .5), (1.5, .5)), ((0, 1.5), (1.5, .5))][int(r.integers(3))]:
                last = _melodia(r, (kr, q), 67, 84, last)
                P(tb + pos * b, blacha(last, L * b * 0.9, 0.55))
        bar += 1


def s_lament(P, sec, r, o):
    """Lament: duduk długimi nutami nad burdonem D–A, rzadki niski pandur; opcja nadzieja (jońska), motyw ojca albo syna
    na początku."""
    b = 60.0 / o.get("bpm", 60)
    key = o.get("key", 62)
    sk = skala(key, JONSKA if o.get("nadzieja") else EOLSKA, 57, 77)
    n = len(P.x)
    tl = tt(n)
    P.x += (np.sin(2 * math.pi * mtof(key - 24) * tl) + 0.5 * np.sin(2 * math.pi * mtof(key - 17) * tl)) * 0.02 * np.minimum(1, tl / 2)
    at, last = 0.4, key + 7
    if o.get("motyw"):
        at = _graj_fraze(P, at, b, MOTYW_SYNA if o["motyw"] == "syn" else MOTYW_OJCA, duduk, 0.62) + 2 * b
    k = 0
    while at < sec:
        ms = fraza(r, sk, last, int(r.integers(3, 5)))
        Ls = [(2, 1, 1, 4), (1.5, 0.5, 4), (3, 1, 4), (1, 1, 2, 4)][int(r.integers(4))]
        nuty = list(zip(ms, Ls))
        nuty[-1] = (_koniec_frazy(sk, nuty[-1][0], key), nuty[-1][1])
        last = nuty[-1][0]
        P(at, pandur(key - 12, 0.3))
        at = _graj_fraze(P, at, b, nuty, duduk, 0.55) + float(r.choice((1.0, 2.0))) * b
        k += 1


def s_rosja(P, sec, r, o):
    """Rosja: bałałajka — wolno (3/4) melodia tremolem nad akordami, żywo (2/4, opcja zywo) szarpane akordy i ósemki."""
    zywo = o.get("zywo")
    b = 60.0 / o.get("bpm", 132 if zywo else 84)
    key = o.get("key", 57)
    prog = ([(0, "m"), (7, "7"), (0, "m"), (7, "7"), (5, "m"), (0, "m"), (7, "7"), (0, "m")] if zywo else
            [(0, "m"), (0, "m"), (5, "m"), (0, "m"), (7, "7"), (7, "7"), (0, "m"), (0, "m")])
    beats = 2 if zywo else 3
    bar, last = 0, key + 12
    while bar * beats * b < sec:
        tb = bar * beats * b
        root, q = prog[bar % 8]
        kr = (key + root) % 12
        P(tb, pandur(40 + (kr - 40) % 12, 0.45))
        if zywo:
            for d in (0.5, 1.5):
                for m in akord(kr, q, 57, 70)[:3]:
                    P(tb + d * b, pandur(m, 0.3, True))
            for j in range(4):
                last = _melodia(r, (kr, q), 69, 86, last)
                P(tb + j * b / 2, pandur(last, 0.55, True))
        else:
            for d in (1, 2):
                for m in akord(kr, q, 57, 70)[:3]:
                    P(tb + d * b, pandur(m, 0.22, True))
            for pos, L in (((0, 2), (2, 1)) if bar % 2 == 0 else ((0, 3),)):
                last = _melodia(r, (kr, q), 69, 84, last)
                k = 0.0
                while k < L * b * 0.95:
                    P(tb + pos * b + k, pandur(last, 0.34 if k == 0 else 0.24, True))
                    k += 1 / 13
        bar += 1


def s_pustynia(P, sec, r, o):
    """Pustynia (Diuna): burdon D (fale co 9 s), bendir co takt, flet ney frazami we frygijskiej dominantowej; opcja
    zurna — motyw Szamila na zurnie nad pustynią (słowa z gór w Diunie)."""
    b = 60.0 / o.get("bpm", 60)
    key = o.get("key", 62)
    sk = skala(key, FRYG_DOM, 60, 81)
    n = len(P.x)
    tl = tt(n)
    fala = 0.75 + 0.25 * np.sin(2 * math.pi * tl / 9.0)
    P.x += (np.sin(2 * math.pi * mtof(key - 36) * tl) + 0.6 * np.sin(2 * math.pi * mtof(key - 29) * tl)
            + 0.25 * np.sin(2 * math.pi * mtof(key - 24) * tl + 0.3 * np.sin(2 * math.pi * 0.2 * tl))) * 0.03 * fala * np.minimum(1, tl / 2.5)
    bar, last = 0, key + 7
    while bar * 4 * b < sec:
        tb = bar * 4 * b
        P(tb, bendir(0.6)), P(tb + 2.5 * b, bendir(0.3)), P(tb + 3 * b, tek(0.15))
        if bar % 2 == 0 and not o.get("bez_melodii"):
            if o.get("zurna") and bar % 4 == 0:
                _graj_fraze(P, tb + 0.05, b, MOTYW_OJCA, zurna, 0.6)
            else:
                ms = fraza(r, sk, last, int(r.integers(3, 6)))
                Ls = [(1, 1, 2, 4), (2, 2, 4), (0.5, 0.5, 1, 2, 4), (1.5, 0.5, 2, 4)][int(r.integers(4))]
                nuty = list(zip(ms, Ls))
                nuty[-1] = (_koniec_frazy(sk, nuty[-1][0], key), nuty[-1][1])
                last = nuty[-1][0]
                _graj_fraze(P, tb + 0.05, b, nuty, ney, 0.6)
        bar += 1


# Styl → (funkcja, zamierzona różnica głośności w dB) — każdy temat wyrównany do MUZYKA_DB (Podręcznik → Dźwięk 6)
STYLE = {"gory": (s_gory, 0.0), "lezginka": (s_lezginka, 0.0), "imperium": (s_imperium, -0.5), "lament": (s_lament, -1.0),
         "rosja": (s_rosja, -0.5), "pustynia": (s_pustynia, 0.0), "napiecie": (s_napiecie, 0.5), "mrok": (s_mrok, -1.5),
         "walc": (s_walc, -0.5)}
MUZYKA_DB = -19.5
CICHO_DB = -2.5
POD_KWESTIA_MUZYKA, POD_KWESTIA_EFEKTY = -8.0, -5.0

# Od którego ujęcia gra który temat (do następnego wpisu). Opcje: bpm, key, motyw, zurna, doli, fanfara, cicho, zywo,
# nadzieja, bez_melodii, bez_zurny.
CUES = [
    ("zap_skok", "lezginka", {"bpm": 168}), ("tytul", "pustynia", {}), ("zamiana", "gory", {"zurna": True}),
    ("przedstawienie", "gory", {"motyw": True}), ("hak_syn", "lament", {"motyw": "syn"}), ("pytanie", "napiecie", {"bpm": 64}),
    ("gimry", "gory", {"bpm": 80}), ("wieza", "napiecie", {"bpm": (80, 104)}), ("skok", "lezginka", {"bpm": 156}),
    ("rana", "lament", {"bpm": 56}), ("kanly_1834", "mrok", {}), ("imam", "gory", {"doli": True, "zurna": True, "motyw": True}),
    ("mapa", "imperium", {"fanfara": True}), ("marsz", "imperium", {"bpm": 108, "key": 58}),
    ("akhulgo", "napiecie", {"bpm": (60, 72)}), ("armaty", "lezginka", {"bpm": 144, "bez_zurny": True}), ("amanat", "lament", {}),
    ("upadek", "mrok", {}), ("tratwa", "napiecie", {"bpm": (72, 92)}), ("raport", "imperium", {"bpm": 104}),
    ("syn_na_polnoc", "rosja", {}), ("kreski", "lament", {"motyw": True}),
    ("vorontsov", "imperium", {"fanfara": True, "key": 62}), ("pochod", "napiecie", {"bpm": (66, 82)}), ("dargo", "mrok", {}),
    ("zwyciestwo", "imperium", {"bpm": 116}), ("suchary", "napiecie", {"bpm": (58, 78)}), ("zasadzka", "cisza", {}),
    ("tolstoj", "lezginka", {"bpm": 160}), ("kadet", "walc", {}), ("tsinandali", "lezginka", {"bpm": 150, "key": 55}),
    ("ksiezne", "gory", {"bpm": 84}), ("wedeno", "gory", {"bpm": 70, "cicho": True}), ("cena", "gory", {"bpm": 76, "zurna": True}),
    ("rzeka", "napiecie", {"bpm": (56, 64)}), ("syn_wraca", "lament", {"motyw": "syn", "nadzieja": True}),
    ("uscisk", "cisza", {}), ("obcy", "walc", {"cicho": True, "key": 57}), ("smierc", "mrok", {"bpm": 50}),
    ("gunib", "gory", {"bpm": 66, "cicho": True}), ("liczby", "napiecie", {"bpm": (66, 84)}), ("szturm_gunib", "napiecie", {"bpm": (84, 100)}),
    ("kapitulacja", "lament", {}), ("stempel", "mrok", {"cicho": True}), ("car", "imperium", {"bpm": 84, "bez_melodii": False}),
    ("kaluga", "rosja", {"zywo": True}), ("medyna", "pustynia", {}), ("blanch", "walc", {"key": 65}), ("herbert", "pustynia", {}),
    ("slowa1", "pustynia", {"zurna": True}), ("zdanie", "napiecie", {"bpm": 60}), ("przyslowie", "pustynia", {}),
    ("zastrzezenie", "gory", {"bpm": 72, "cicho": True}), ("dwie_wojny", "pustynia", {"zurna": True}),
    ("biala_flaga", "lament", {"motyw": True}), ("dzieki", "lezginka", {"bpm": 150}),
]

# Motyw w ujęciu bez tematu (CUES „cisza”): (sekunda akcji, motyw) — uścisk ojca z synem (rozpiska: „4,6 s wraca motyw ojca”)
MOTYW = {"uscisk": (4.6, "ojciec")}
GAG_PRZYSTANEK_DB, GAG_PRZYSTANEK_S = -9.0, 0.6
# Okrzyki puent gagów (podpisy z podsłuchu): na nich muzyka robi przystanek (Podręcznik → Humor i gagi)
PUENTY = {"BRRR!", "OUCH!", "?!", "...", "…", "WHOA!", "OOPS", "CLINK!", "MEH", "MMPH!", "MEOW!", "*SHAKE SHAKE*", "SHH!", "!", "?"}


def czas_ujecia(klucz, ta):
    """Chwila ujęcia z prawdziwym nagraniem lektora dla chwili ta w rytmie akcji ujęcia (render.czas_ujecia)."""
    import render as R
    return R.czas_ujecia(R.KOL.index(klucz), ta) if klucz in R.KOL else ta


def cisza_ujec():
    """Cisza muzyki przed szczytem (od, do — sekundy akcji ujęcia; True — muzyka wraca głośniej)."""
    import ujecia_a as UA
    return {"skok": (UA.sl("skok", "jumped") - 0.3, UA.sl("skok", "landed") + 0.3, True),
            "wieza": (UA.sl("wieza", "killed") - 0.1, UA.sl("wieza", "killed") + 1.4, False),
            "smierc": (UA.sl("smierc", "died") - 0.1, UA.sl("smierc", "died") + 2.2, False),
            "szturm_gunib": (4.8, 30.0, False)}


def _wyrownaj(x, db):
    L = len(x)
    srodek = x[N(0.5):max(N(0.5) + 1, L - N(0.6))]
    return x * 10 ** (db / 20) / (float(np.sqrt(np.mean(srodek ** 2))) + 1e-9)


def muzyka(total, starts, voice, puenty):
    n = N(total)
    out = np.zeros(n)
    ciecia = sorted(starts.values())
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
        fn(P, dl_muz + 0.5, np.random.default_rng(200 + c), o)
        P(0.0, stopa(0.9) * 1.3)  # akcent na cięciu: nowy temat wchodzi mocną częścią taktu
        x = _wyrownaj(P.x[:N(sec)], MUZYKA_DB + odchyl + (CICHO_DB if o.get("cicho") else 0.0))
        tl = tt(len(x))
        fade = np.minimum(1, tl / CIECIE_WEJSCIE) * np.clip((sec - tl) / CIECIE_WYJSCIE, 0, 1)
        i0 = N(a0)
        out[i0:i0 + len(x)] += (x * fade)[:n - i0]
    for klucz, (at, ktory) in MOTYW.items():  # motyw w ciszy (bez burdonu i bębnów)
        if klucz in starts:
            P = Pasmo(8.0)
            _graj_fraze(P, 0.1, 60.0 / 58, MOTYW_OJCA if ktory == "ojciec" else MOTYW_SYNA, duduk, 0.62)
            x = _wyrownaj(P.x, MUZYKA_DB + 1.0)
            i0 = N(starts[klucz] + czas_ujecia(klucz, at) - 0.1)
            out[i0:i0 + len(x)] += x[:n - i0]
    gain = np.ones(n)
    for klucz, (a, b, powrot) in cisza_ujec().items():
        if klucz not in starts:
            continue
        a, b = [float(v) if isinstance(v, Sek) else czas_ujecia(klucz, v) for v in (a, b)]
        i0, i1 = max(0, N(starts[klucz] + a)), min(n, N(starts[klucz] + b))
        r_ = N(0.12)
        gain[i0:i1] = 0.0
        gain[max(0, i0 - r_):i0] = np.minimum(gain[max(0, i0 - r_):i0], np.linspace(1, 0, i0 - max(0, i0 - r_)))
        j = min(n, i1 + N(2.5))
        gain[i1:j] = (np.linspace(1.5, 1.0, j - i1) if powrot else np.linspace(0, 1, j - i1))
    out *= gain
    gg = np.ones(n)
    lo = 10 ** (GAG_PRZYSTANEK_DB / 20)
    for a in puenty:  # przystanek na puencie gagu
        i0, i1, i2 = N(a - 0.06), N(a + GAG_PRZYSTANEK_S), N(a + GAG_PRZYSTANEK_S + 0.5)
        if i0 < 0 or i2 >= n:
            continue
        gg[i0:i1] = np.minimum(gg[i0:i1], lo)
        gg[i1:i2] = np.minimum(gg[i1:i2], np.linspace(lo, 1.0, i2 - i1))
    out *= gg
    out *= sciszanie(voice, POD_KWESTIA_MUZYKA)
    return out


# =====================================================================================================================
# EFEKTY TEGO FILMU
# =====================================================================================================================

def armata():
    """Armata: głęboki huk, trzask prochu i długi pogłos w górach."""
    n = N(2.6)
    t = tt(n)
    x = np.zeros(n)
    b = boom()
    x[:len(b)] += b * 0.9
    c = crack(0.3)
    x[:len(c)] += c * 0.8
    x += band(_r(61).normal(0, 1, n), 60, 500) * np.exp(-t / 0.9) * 0.35
    return x * 0.9


def koza_snd(dl=0.9):
    """Beczenie kozy („MEH”): nosowy ton ok. 380 Hz z drżeniem 8,5 Hz i formantami „e”."""
    n = N(dl)
    t = tt(n)
    f0 = 380 * (1 + 0.04 * np.sin(2 * math.pi * 1.2 * t)) * (1 - 0.12 * t / dl)
    ph = 2 * math.pi * np.cumsum(f0) / SR
    x = band(sum((1 / k) * np.sin(k * ph) for k in range(1, 14)), 300, 3500)
    x = x + 0.6 * band(x, 450, 650) + 0.5 * band(x, 1700, 2100)
    e = np.minimum(1, t / 0.03) * np.clip((dl - t) / 0.15, 0, 1) * (0.55 + 0.45 * np.sin(2 * math.pi * 8.5 * t))
    return x / (np.abs(x).max() + 1e-9) * e * 0.33


def kot_snd():
    """Miauknięcie (kot Lesley Blanch): ton przesuwa się 520 → 820 → 450 Hz, formanty „i–a–u”."""
    dl = 0.75
    n = N(dl)
    t = tt(n)
    u = t / dl
    f0 = np.interp(u, (0, 0.35, 1.0), (520, 820, 450))
    ph = 2 * math.pi * np.cumsum(f0) / SR
    x = sum((1 / k ** 1.2) * np.sin(k * ph) for k in range(1, 10))
    x = band(x, 350, 4000)
    e = np.minimum(1, t / 0.05) * np.clip((dl - t) / 0.2, 0, 1)
    return x / (np.abs(x).max() + 1e-9) * e * 0.28


def gulp():
    """Robak połyka tabliczkę: głębokie „gulp”."""
    return _s(slide(True, 0.3) * 0.6, thud(0.4) * 0.5)


def bek():
    """Robak beka chmurką piasku: niski, chropowaty pomruk."""
    n = N(0.6)
    t = tt(n)
    x = sum(np.sin(2 * math.pi * 68 * k * t) / k for k in range(1, 8)) * (0.6 + 0.4 * np.sin(2 * math.pi * 24 * t))
    return (band(x, 60, 900) * np.sin(np.pi * t / 0.6) ** 0.7 * 0.45 + _szum(n, 2000, 7000, 72) * np.exp(-t / 0.3) * 0.1)


def piasek(sec):
    """Sypiący się piasek: szum wysoki i ziarenka."""
    n = N(sec)
    t = tt(n)
    x = _szum(n, 1800, 9000, 73) * 0.06
    r = _r(74)
    for _ in range(int(sec * 60)):
        i = int(r.uniform(0, n - N(0.004)))
        x[i:i + N(0.004)] += r.uniform(-0.04, 0.04)
    return x * np.minimum(1, t / 0.15) * np.clip((sec - t) / 0.3, 0, 1)


def kamien(sec=1.0):
    """Trący kamień (skała otwiera jaskinię, góry osiadają)."""
    n = N(sec)
    t = tt(n)
    x = _szum(n, 90, 1300, 75) * (0.6 + 0.4 * (np.sin(2 * math.pi * 13 * t) > 0)) * 0.5
    return x * np.sin(np.pi * np.clip(t / sec, 0, 1)) * 0.8


def gory_rosna(sec=1.6):
    """Wyrastające góry: niski łoskot ziemi i opadające kamyki."""
    n = N(sec)
    t = tt(n)
    x = _szum(n, 30, 220, 76) * np.sin(np.pi * t / sec) * 0.7
    r = _r(77)
    for _ in range(10):
        s = knock(r.uniform(200, 500), 0.12) * r.uniform(0.15, 0.35)
        i = int(r.uniform(N(0.3), n - len(s)))
        x[i:i + len(s)] += s
    return x


def szabla_wyj():
    """Kindżał albo szabla wyciągane z pochwy: metaliczne „sziiing”."""
    n = N(0.55)
    t = tt(n)
    x = _sweep(2600, 5200, 0.55, harm=((1, 1.0), (2.01, 0.4), (3.03, 0.2))) * np.exp(-t / 0.25) * 0.05
    return x + _szum(n, 3000, 9000, 78) * env(n, 0.02, 0.15) * 0.18


def szable():
    """Szable unoszą się falą: kilka świstów i brzęków po kolei."""
    out = np.zeros(N(1.4))
    r = _r(79)
    for k in range(6):
        s = _s(whoosh(0.35, 1500, 7000) * 0.5, clash(0.5) * 0.12)
        i = N(0.12 * k + r.uniform(0, 0.05))
        out[i:i + len(s)] += s[:len(out) - i]
    return out * 0.8


def flaga(sec):
    """Chorągiew na wietrze: łopot materiału."""
    n = N(sec)
    t = tt(n)
    am = 0.5 + 0.5 * np.abs(np.sin(2 * math.pi * 3.7 * t + 2 * np.sin(2 * math.pi * 0.6 * t)))
    return _szum(n, 400, 4000, 80) * am * 0.09 * np.minimum(1, t / 0.3) * np.clip((sec - t) / 0.4, 0, 1)


def krysztal():
    """Kryształki żyrandola: kilka wysokich, cichnących brzęków."""
    out = np.zeros(N(1.3))
    r = _r(81)
    for k in range(7):
        s = coin(0.9) * r.uniform(0.25, 0.5)
        i = N(0.07 * k + r.uniform(0, 0.03))
        out[i:i + len(s)] += s[:len(out) - i]
    return out


def maszyna(sec):
    """Maszyna do pisania: nierówne stuknięcia czcionek, co kilka sekund dzwonek i przesuw wałka."""
    n = N(sec)
    out = np.zeros(n)
    r = _r(82)
    k = 0.05
    while k < sec - 0.1:
        s = _s(knock(r.uniform(1500, 2100), 0.05) * 0.5, _szum(N(0.03), 2500, 8000, int(k * 100)) * env(N(0.03), 0.001, 0.006) * 0.3)
        i = N(k)
        out[i:i + len(s)] += s[:n - i] * r.uniform(0.6, 1.0)
        k += r.uniform(0.07, 0.16)
    return out * 0.5


def kola_wozu(sec):
    """Drewniane koła wozu po kamieniach."""
    n = N(sec)
    t = tt(n)
    x = _szum(n, 70, 600, 83) * (0.7 + 0.3 * np.sin(2 * math.pi * 2.3 * t)) * 0.12
    r = _r(84)
    for _ in range(int(sec * 5)):
        s = knock(r.uniform(160, 320), 0.1) * r.uniform(0.08, 0.18)
        i = int(r.uniform(0, max(1, n - len(s))))
        x[i:i + len(s)] += s
    return x


def lina(sec):
    """Liny na urwisku: skrzyp i szelest konopi."""
    return skrzyp(sec) * 0.7 + _szum(N(sec), 600, 3000, 85) * 0.02


def kopyto():
    return _s(knock(float(RNG.uniform(170, 240)), 0.13) * 0.55, thud(0.2) * 0.12)


KROTKIE = {
    "podpis": podpis_snd, "zawieszka": zawieszka_snd, "stempel": stempel, "nitka": nitka, "wahwah": wahwah,
    "wahwah_k": lambda: wahwah(True), "boing": boing, "boing_m": lambda: boing(True), "szklo": szklo, "boom": boom, "armata": armata,
    "strzal": strzal, "strzal_cien": lambda: strzal(True), "whoosh": whoosh, "thud": thud, "knock": knock, "coin": coin,
    "splash": splash, "plusk": lambda: splash(0.8) * 0.8, "kurtyna_z": kurtyna_zasuwa, "kurtyna_r": kurtyna_rozsuwa, "klaps": klaps,
    "skok": lambda: thud(0.3) * 0.5, "papier": lambda: whoosh(0.5, 1200, 7000) * 0.6, "strona": lambda: whoosh(1.4, 500, 6000) * 0.9,
    "pytanie": lambda: slide(False, 0.35) * 0.8, "slide_down": lambda: slide(True), "slide_up": lambda: slide(False, 0.45),
    "brr": brr, "stuk": stuk, "klik": klik, "krach": krach, "trzepot": trzepot, "dzwonek": dzwonek,
    "dzwon": lambda: band(dzwon(196), 60, 3000) * 0.9, "koza": koza_snd, "kot": kot_snd, "gulp": gulp, "bek": bek,
    "szabla_wyj": szabla_wyj, "szable": szable, "krysztal": krysztal, "kamien": lambda: kamien(1.0), "gory_rosna": lambda: gory_rosna(1.6),
    "dum": lambda: dum(1.0) * 1.4, "sting": sting, "pff": lambda: knock(500, 0.08) * 0.4, "syk_s": lambda: syk(0.8),
    "cios": lambda: np.concatenate([whoosh(0.3, 600, 4000) * 0.6, thud(0.5)]), "kopyto": kopyto,
}
DLUGIE = {
    "ogien": fire, "woda": woda, "brodzenie": brodzenie, "pisanie": pisanie, "oklaski": oklaski, "dzwony": dzwony, "zgrzyt": zgrzyt,
    "skrzyp": skrzyp, "zegar": zegar, "kola": kola_wozu, "piasek": piasek, "flaga": flaga, "maszyna": maszyna, "lina": lina,
    "dzwoneczki": lambda s: dzwoneczki(s, int(s * 6), 61), "kamien_d": kamien, "tlum": tlum,
}

# Dźwięk podpisu według napisu (słownik znaków 1.20); None — bez dźwięku (powaga); reszta (imiona, miejsca) → podpis
TAB_DZWIEK = {"BRRR!": "brr", "OUCH!": "boing", "?!": "pytanie", "?": "pytanie", "!": "pytanie", "!!": "pytanie", "WHOA!": "slide_down",
              "...": "wahwah_k", "…": "wahwah_k", "OOPS": "boing_m", "CLINK!": "krysztal", "MEH": "koza", "MMPH!": "wahwah_k",
              "MEOW!": "kot", "*SHAKE SHAKE*": "piasek_k", "SHH!": "pff", "THERE!": "podpis", "THE BISCUIT EXPEDITION": None,
              "TO THE DEATH!": "podpis"}
KROTKIE["piasek_k"] = lambda: piasek(0.9)


def zdarzenia():
    """Wydarzenia ręczne: (sekunda akcji ujęcia, dźwięk, głośność albo czas trwania) — chwile ze słów lektora (ujecia_a.sl,
    po_kw), w rytmie, w którym ułożono akcję (render.czas_ujecia przekłada je na nagranie)."""
    import ujecia_a as UA
    sl, po = UA.sl, UA.po_kw
    Z = {
        "tytul": [(0.1, "kurtyna_r", 1.0), (2.6, "piasek", 1.0)],
        "arrakis": [(sl("arrakis", "kindjal"), "szabla_wyj", 0.9), (sl("arrakis", "sietches"), "kamien", 0.7),
                    (po("arrakis", 0.1) + 0.7, "gulp", 1.0), (po("arrakis", 0.1) + 1.5, "bek", 1.0)],
        "zamiana": [(sl("zamiana", "weren't"), "piasek", 2.0), (sl("zamiana", "weren't") + 0.2, "kamien_d", 1.4),
                    (2.5, "gory_rosna", 1.0), (po("zamiana", 0.0) + 0.9, "whoosh", 0.5)],
        "przedstawienie": [(sl("przedstawienie", "most") + 0.7, "stuk", 0.8)],
        "pytanie": [(sl("pytanie", "desert"), "piasek", 1.4), (sl("pytanie", "desert") + 0.1, "kamien_d", 1.0),
                    (7.6, "gory_rosna", 1.0)],
        "wieza": [(sl("wieza", "killed") + 0.5, "thud", 0.35)],
        "skok": [(0.6, "szabla_wyj", 0.8), (sl("skok", "jumped"), "dum", 1.0), (sl("skok", "jumped") + 0.05, "whoosh", 0.7),
                 (sl("skok", "landed"), "thud", 0.7)],
        "rana": [(po("rana", -0.6) + 0.2, "koza", 0.5)],
        "kanly_1834": [(2.0, "whoosh", 0.4), (4.2, "thud", 0.35)],
        "imam": [(sl("imam", "imam"), "szable", 1.0), (po("imam", 0.2), "szabla_wyj", 0.6), (po("imam", 0.2) + 0.5, "klik", 0.6)],
        "mapa": [(sl("mapa", "valley"), "kamien", 0.6), (sl("mapa", "valley") + 0.4, "slide_down", 0.7), (po("mapa", 0.3), "klik", 0.6)],
        "marsz": [(po("marsz", 0.0) + 0.4, "stuk", 0.8), (po("marsz", 0.0) + 0.6, "stuk", 0.7)],
        "akhulgo": [(0.6, "gory_rosna", 0.8), (3.0, "kamien", 0.4)],
        "armaty": [(po("armaty", 0.0) + 0.3, "skrzyp", 1.4)],
        "amanat": [(0.6, "flaga", 3.0)],
        "tratwa": [(po("tratwa", 0.1) + 0.9, "plusk", 0.9)],
        "raport": [(0.6, "papier", 0.5), (sl("raport", "rose") + 0.05, "thud", 0.5)],
        "syn_na_polnoc": [(0.0, "kola", 10.0), (0.0, "dzwoneczki", 9.5), (6.0, "klik", 0.6)],
        "kreski": [(1.4 + 0.55 * k, "zgrzyt", 0.35) for k in range(6)],
        "vorontsov": [(0.6, "papier", 0.6)],
        "pochod": [(po("pochod", 0.0), "stuk", 0.8), (po("pochod", 0.0) + 0.2, "stuk", 0.8), (po("pochod", 0.0) + 0.7, "stuk", 0.6)],
        "zwyciestwo": [(0.6, "pisanie", 1.2), (sl("zwyciestwo", "eat") + 0.4, "papier", 0.5), (sl("zwyciestwo", "eat") + 0.8, "stuk", 0.7)],
        "zasadzka": [(0.3, "krach", 0.7), (0.8, "krach", 0.6), (1.3, "thud", 0.6)],
        "tolstoj": [(0.6, "pisanie", 2.0)] + [(po("tolstoj", -2.0) + 0.15 * k, "papier", 0.35) for k in range(8)],
        "tsinandali": [(5.2, "whoosh", 0.5), (5.3, "papier", 0.5), (5.5, "papier", 0.4)],
        "wedeno": [(sl("wedeno", "governess"), "pisanie", 2.0)],
        "cena": [(0.6, "pisanie", 1.8)] + [(sl("cena", "forty") + 0.25 * k, "coin", 0.6) for k in range(4)],
        "przeprawa": [(0.0, "brodzenie", 8.6), (6.0, "plusk", 0.6)],
        "syn_wraca": [(0.6, "brodzenie", 7.0)],
        "mundur": [(2.5, "klik", 0.6), (2.8, "klik", 0.5), (4.5, "whoosh", 0.3), (6.0, "whoosh", 0.4)],
        "obcy": [(1.0, "strona", 0.5), (7.0, "pff", 0.6)],
        "smierc": [(sl("smierc", "died"), "syk_s", 0.5)],
        "gunib": [(5.5, "flaga", 3.0), (7.0, "kamien", 0.5), (7.4, "stuk", 0.4), (7.7, "stuk", 0.3)],
        "szturm_gunib": [(0.6, "lina", 4.4), (5.0, "flaga", 3.4)],
        "stempel": [(0.6, "papier", 0.5), (3.6, "dzwony", 3.4)],
        "car": [(3.0, "klik", 0.4)],
        "kaluga": [(po("kaluga", 0.1) + 0.8, "koza", 0.7)],
        "blanch": [(0.6, "maszyna", 3.4), (4.0, "dzwonek", 0.8)] + [(4.2 + 0.25 * k, "papier", 0.35) for k in range(8)],
        "herbert": [(0.6, "maszyna", 2.4), (3.0, "piasek", 3.0)],
        "slowa1": [(sl("slowa1", "kindjal"), "szabla_wyj", 0.6)],
        "slowa2": [(0.6, "papier", 0.4), (1.0, "papier", 0.35), (1.4, "papier", 0.3)],
        "zdanie": [(3.0, "whoosh", 0.4), (7.0, "whoosh", 0.6), (7.25, "cios", 0.7)],
        "przyslowie": [(sl("przyslowie", "became"), "papier", 0.5), (5.0, "piasek", 1.5)],
        "zastrzezenie": [(5.0, "stuk", 0.5)],
        "biala_flaga": [(0.6, "flaga", 5.0), (3.5, "whoosh", 0.3)],
        "dzieki": [(0.3, "kurtyna_z", 1.0), (0.8, "oklaski", 3.6)],
    }
    return Z


SKAN_DT = 0.08
DEKORACJE = ("kaukaz", "gory_pasmo", "snieg", "pustynia", "arrakis_sc", "jaskinia", "gimry_sc", "gabinet", "las_bukowy", "kaluga_sc",
             "miczik", "izba", "petersburg", "sala_balowa", "gruzja", "teatr_kz", "parawan", "ciemnosc", "wnetrze", "plaskowyz",
             "polana", "pracownia")


def skan():
    """Przegląd filmu (render.uloz co SKAN_DT) z podsłuchem na funkcjach ujęć: znaki (podpisy, zawieszki, nitki, błyski,
    pieczątki, koza, laska maszynisty, kartki), tory ruchu (lalki, konie, zaprzęgi, robak, ogień) i dekoracje ujęć."""
    import bisect

    import render as R
    import scena
    import uklad as U
    import uklad_kz
    import ujecia_a as A
    import ujecia_b as B
    import zestaw_kz as J
    S = {"t": 0.0, "i": 0, "nl": {}}
    lalki, konie, jedno, dekor, noc, robaki, ogien = {}, {}, {}, {}, {}, {}, {}

    def pierwszy(klucz, at, rodzaj, extra=None):
        a, b = R.SCENES[S["i"]][:2]
        if not a - 0.05 <= at < b:  # skrót (WYCINEK) widzi też zdarzenia oryginału sprzed i po wycinku — nie te
            return
        if klucz not in jedno:
            jedno[klucz] = (at, rodzaj, extra, S["i"])

    def chwila(t, t0):
        """Chwila filmu dla zdarzenia w sekundzie t0 akcji ujęcia (t — czas akcji w tej klatce)."""
        i = S["i"]
        if R.KOL[i] in R.WYCINEK:
            return S["t"] - t + t0
        return R.SCENES[i][0] + R.czas_ujecia(i, t0)

    def tor(slownik, klucz, x, *extra):
        slownik.setdefault(klucz, []).append((S["t"], float(x), *extra))

    def w_podpis(w, t, txt, x, y, t0, dur=2.8):
        pierwszy(("p", S["i"], txt, round(t0, 2)), chwila(t, t0), "podpis", txt)

    def w_blysk(st, x, y, p, t, t0, r=260, kolor=(1.0, 0.9, 0.6), dl=0.12):
        pierwszy(("b", S["i"], round(t0, 1)), chwila(t, t0), "blysk", (r, tuple(kolor)))  # salwa = jeden strzał

    def w_koniec(st, w, t, *a, **kw):
        try:
            noc[S["i"]] = max(noc.get(S["i"], 0.0), float(w.get("noc") or 0.0))
        except Exception:
            pass
        for txt, x, y, k in getattr(w, "zawieszki", []):
            if k > 0:
                pierwszy(("z", S["i"], txt), S["t"], "zawieszka", txt)

    def w_pieczatka(st, t, t0, raport_txt, *a, gag=True, spada=None, **kw):
        pierwszy(("s", S["i"], raport_txt), chwila(t, t0 if gag else t0 + 0.9), "pieczatka", gag)
        if spada is not None:
            pierwszy(("sp", S["i"], raport_txt), chwila(t, spada + 0.6), "spada")

    def w_koza(st, t, nazwa, *a, meh=False, k=1.0, **kw):
        if meh and k > 0:
            pierwszy(("k", S["i"], nazwa), S["t"], "koza")

    orig_robak, orig_masz, orig_kartki = A.robak, A.maszynista, A.kartki_kalendarza

    def w_robak(st, t, x, y, p, wys, *a, **kw):
        if wys > 0:
            robaki.setdefault(S["i"], {}).setdefault(round(S["t"], 3), 0.0)
            robaki[S["i"]][round(S["t"], 3)] = max(robaki[S["i"]][round(S["t"], 3)], float(wys))
        return orig_robak(st, t, x, y, p, wys, *a, **kw)

    def w_masz(st, t, k, *a, **kw):
        if k > 0.05:
            pierwszy(("m", S["i"]), S["t"], "maszynista")
        return orig_masz(st, t, k, *a, **kw)

    def w_kartki(st, t, t0, lata, *a, dl=0.42, **kw):
        for n_ in range(len(lata)):
            pierwszy(("c", S["i"], n_), chwila(t, t0 + n_ * dl), "kartka")
        return orig_kartki(st, t, t0, lata, *a, dl=dl, **kw)

    def w_plomien(st, x, y, p, t, h=90, seed=0):
        if h > 4:
            ogien.setdefault(S["i"], [S["t"], S["t"]])
            ogien[S["i"]][1] = S["t"]

    def w_lalka_sc(orig):
        def f(st, t, key, x, h=300, *a, **kw):
            if not kw.get("siedzi"):
                n_ = S["nl"].get(key, 0)
                S["nl"][key] = n_ + 1
                tor(lalki, (S["i"], key, n_), x, h)
            return orig(st, t, key, x, h, *a, **kw)
        return f

    orig_ulalka = U.Uklad.lalka

    def w_ulalka(self, nazwa, key, x, h=300, *a, **kw):
        if not kw.get("siedzi"):
            tor(lalki, (S["i"], "u:" + nazwa), x, h)
        return orig_ulalka(self, nazwa, key, x, h, *a, **kw)

    orig_jezdziec, orig_zaprzeg = uklad_kz.jezdziec, uklad_kz.zaprzeg

    def w_jezdziec(st, t, nazwa, key, x, *a, **kw):
        if kw.get("k", 1.0) > 0:
            tor(konie, (S["i"], "j:" + nazwa), x, kw.get("h", 170), False)
        return orig_jezdziec(st, t, nazwa, key, x, *a, **kw)

    def w_zaprzeg(st, t, nazwa, x, *a, **kw):
        tor(konie, (S["i"], "z:" + nazwa), x, kw.get("h_kon", 120), True)
        return orig_zaprzeg(st, t, nazwa, x, *a, **kw)

    def w_dekor(nazwa, orig):
        def f(*a, **kw):
            d = dekor.setdefault(S["i"], {})
            d[nazwa] = d.get(nazwa, 0) + 1
            if kw.get("noc"):
                d["noc"] = 1
            return orig(*a, **kw)
        return f

    orig_hang = J.hang

    def w_hang(st, spr, x, y, p, k=1.0, t=0.0, seed=1, *a, **kw):
        b = scena.BUDOWA["t"]
        if 0 < k < 0.5 and (b is None or b > 1.8):
            pierwszy(("h", S["i"], seed), S["t"], "nitka")
        return orig_hang(st, spr, x, y, p, k, t, seed, *a, **kw)

    for M in (A, B):
        M.podpis, M.blysk, M.koniec = w_podpis, w_blysk, w_koniec
        M.pieczatka, M.koza, M.robak, M.maszynista, M.kartki_kalendarza, M.plomien = w_pieczatka, w_koza, w_robak, w_masz, w_kartki, w_plomien
        M.lalka = w_lalka_sc(scena.lalka)
        for nazwa in DEKORACJE:
            if hasattr(M, nazwa):
                setattr(M, nazwa, w_dekor(nazwa, getattr(M, nazwa)))
    scena.lalka = w_lalka_sc(scena.lalka)  # cienie (scena.cien)
    U.Uklad.lalka = w_ulalka
    uklad_kz.jezdziec, uklad_kz.zaprzeg = w_jezdziec, w_zaprzeg
    J.hang = w_hang
    starts = [a for a, b, *_ in R.SCENES]
    t = 0.0
    while t < R.DUR:
        i = max(0, bisect.bisect_right(starts, t) - 1)
        S.update(t=t, i=i, nl={})
        R.uloz(t)
        t += SKAN_DT
    J.hang, U.Uklad.lalka, uklad_kz.jezdziec, uklad_kz.zaprzeg = orig_hang, orig_ulalka, orig_jezdziec, orig_zaprzeg
    return lalki, konie, jedno, dekor, noc, robaki, ogien


def _gladko(v, k=3):
    if len(v) < k:
        return v
    return np.convolve(v, np.ones(k) / k, mode="same")


def _predkosc(rec):
    ts = np.array([r[0] for r in rec])
    xs = np.array([r[1] for r in rec], float)
    v = np.abs(np.diff(xs)) / np.maximum(np.diff(ts), 1e-3)
    v = np.where(np.diff(ts) > 0.2, 0, v)
    return ts, v


def kopyta(konie, n):
    """Tętent z prędkości konia na ekranie: stęp (pojedyncze stuknięcia), kłus i galop (trójki); zaprzęg dokłada koła."""
    out = np.zeros(n)
    ile = 0
    for (i, nazwa), rec in konie.items():
        if len(rec) < 3:
            continue
        ts, v = _predkosc(rec)
        v = _gladko(v, 3)
        zaprzeg = rec[0][3]
        faza, r = 0.0, _r(sum(map(ord, nazwa)) + i)
        g = 0.45 * float(np.clip(rec[0][2] / 170.0, 0.6, 1.2))
        for j, vj in enumerate(v):
            if vj < 30:
                faza = 0.0
                continue
            galop = vj > 260
            okres = 0.42 if galop else float(np.clip(0.55 - vj / 900, 0.3, 0.55))
            faza += SKAN_DT
            if faza >= okres:
                faza -= okres
                for d in ((0.0, 0.07, 0.14) if galop else (0.0,)):
                    s = kopyto() * g * r.uniform(0.7, 1.0)
                    a = N(ts[j] + d)
                    out[a:a + len(s)] += s[:max(0, n - a)]
                    ile += 1
        if zaprzeg:  # koła: szum wozu z obwiednią prędkości
            a0, a1 = ts[0], ts[-1] + SKAN_DT
            i0, L = N(a0), N(a1 - a0)
            L = min(L, n - i0)
            if L > N(0.3):
                e = np.clip(np.interp(a0 + tt(L), ts[1:], v) / 300.0, 0, 1)
                out[i0:i0 + L] += kola_wozu(L / SR)[:L] * e * 0.8
    print(f"kopyta: {ile}")
    return out


def kroki(lalki, n):
    """Drewniane kroki lalek: ruch po scenie stuka w deski teatru, tempo kroku rośnie z prędkością."""
    out = np.zeros(n)
    ile = 0
    for klucz, rec in lalki.items():
        if len(rec) < 3:
            continue
        ts, v = _predkosc(rec)
        h = rec[0][2]
        faza, r = 0.0, _r(sum(map(ord, str(klucz))))
        for j, vj in enumerate(v):
            if vj < 55:
                faza = 0.0
                continue
            krok = float(np.clip(0.48 - vj / 1800, 0.22, 0.48))
            faza += SKAN_DT
            if faza >= krok:
                faza -= krok
                s = knock(r.uniform(330, 520), 0.12) * 0.18 * float(np.clip(h / 300.0, 0.5, 1.3))
                a = N(ts[j])
                out[a:a + len(s)] += s[:max(0, n - a)]
                ile += 1
    print(f"kroki: {ile}")
    return out


def robak_tory(robaki, n):
    """Robak z Diuny: niski pomruk ziemi i szum piasku, głośność za tym, jak wysoko wystaje."""
    out = np.zeros(n)
    for i, rec in robaki.items():
        ts = np.array(sorted(rec))
        ws = np.array([rec[k] for k in sorted(rec)])
        a0, a1 = ts[0] - 0.3, ts[-1] + 0.5
        i0, L = max(0, N(a0)), N(a1 - a0)
        L = min(L, n - i0)
        if L <= 0:
            continue
        e = np.interp(a0 + tt(L), ts, ws, left=0, right=0)
        e = np.convolve(e, np.ones(N(0.15)) / N(0.15), mode="same")
        r = _r(90 + i)
        x = band(r.normal(0, 1, L), 25, 140) * 0.55 + band(r.normal(0, 1, L), 1800, 7000) * 0.1
        out[i0:i0 + L] += x * np.clip(e, 0, 1) * 0.9
    return out


def tlo(rodzaj, sec, seed, noc_):
    """Tło miejsca: wiatr w górach, śnieg, pustynia, rzeka, las, aul, dwór w Gruzji, miasto, gabinet, izba, sala."""
    n = N(sec)
    r = _r(seed)
    t = tt(n)
    wezly = max(2, int(sec * 0.5) + 2)
    slow = np.interp(t, np.linspace(0, sec, wezly), r.uniform(0.4, 1.0, wezly))

    def ptaki(gestosc, g):
        x = np.zeros(n)
        for _ in range(int(sec * gestosc)):
            L = N(r.uniform(0.08, 0.18))
            i = int(r.uniform(0, max(1, n - L)))
            f0 = r.uniform(2600, 4200)
            x[i:i + L] += _sweep(f0, f0 * r.uniform(0.8, 1.3), L / SR) * np.sin(np.pi * tt(L) / (L / SR)) * g
        return x

    def cykady(g):
        return band(r.normal(0, 1, n), 4000, 6500) * (0.5 + 0.5 * np.sin(2 * math.pi * 31 * t)) * g

    if rodzaj == "gory":
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.05 + band(r.normal(0, 1, n), 900, 2600) * slow ** 2 * 0.012
    elif rodzaj == "snieg":
        x = band(r.normal(0, 1, n), 300, 2500) * slow * 0.025
    elif rodzaj == "pustynia":
        x = band(r.normal(0, 1, n), 80, 600) * slow * 0.045 + band(r.normal(0, 1, n), 2000, 6000) * slow * 0.008
    elif rodzaj == "rzeka":
        x = woda(sec)[:n] * 0.8 + band(r.normal(0, 1, n), 150, 900) * slow * 0.02
    elif rodzaj == "las":
        x = band(r.normal(0, 1, n), 200, 1200) * slow * 0.03 + (ptaki(0.9, 0.012) if not noc_ else 0)
    elif rodzaj == "aul":
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.035 + (ptaki(0.25, 0.01) if not noc_ else 0)
    elif rodzaj == "gruzja":
        x = band(r.normal(0, 1, n), 150, 900) * slow * 0.02 + ptaki(1.2, 0.012) + cykady(0.01)
    elif rodzaj == "miasto":
        x = band(r.normal(0, 1, n), 60, 400) * 0.03 * (0.7 + 0.3 * slow)
    elif rodzaj in ("gabinet", "pracownia"):
        x = band(r.normal(0, 1, n), 60, 300) * 0.015 + zegar(sec)[:n] * 0.6
    elif rodzaj == "izba":
        x = band(r.normal(0, 1, n), 60, 300) * 0.015 + fire(sec)[:n] * 0.12
    elif rodzaj == "kaluga":
        x = band(r.normal(0, 1, n), 60, 500) * 0.02 + ptaki(0.4, 0.01)
    else:  # sala teatru, sala balowa, teatr cieni
        x = band(r.normal(0, 1, n), 80, 500) * 0.012
    if len(x) < n:
        x = np.concatenate([x, np.zeros(n - len(x))])
    if noc_ and rodzaj in ("gory", "las", "aul", "gruzja", "rzeka"):
        x = x * 0.7 + swierszcze(sec)[:n] * 0.5
    return x[:n]


def rodzaj_tla(d):
    for k, v in (("parawan", "sala"), ("ciemnosc", "sala"), ("gabinet", "gabinet"), ("pracownia", "pracownia"), ("izba", "izba"),
                 ("wnetrze", "izba"), ("sala_balowa", "sala"), ("petersburg", "miasto"), ("kaluga_sc", "kaluga"), ("miczik", "rzeka"),
                 ("las_bukowy", "las"), ("gruzja", "gruzja"), ("gimry_sc", "aul"), ("snieg", "snieg"), ("pustynia", "pustynia"),
                 ("arrakis_sc", "pustynia"), ("plaskowyz", "gory"), ("polana", "gory"), ("kaukaz", "gory"), ("gory_pasmo", "gory"),
                 ("teatr_kz", "sala")):
        if k in (d or {}):
            return v
    return "sala"


def zapisz(path, x):
    x = np.tanh(x * 1.2) * 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def dzwiek_znaku(rodzaj, extra, klucz, dekor_i):
    if rodzaj == "podpis":
        kind = TAB_DZWIEK.get(extra, "podpis")
        return KROTKIE[kind]() if kind else None
    if rodzaj == "zawieszka":
        return zawieszka_snd()
    if rodzaj == "nitka":
        return nitka()
    if rodzaj == "pieczatka":
        return _s(stempel(), boing(True) * 0.35) if extra else thud(0.5) * 0.4  # trzecia pieczątka: bez brzdęku
    if rodzaj == "spada":
        return _s(thud(0.4) * 0.5, knock(300, 0.15) * 0.4)
    if rodzaj == "koza":
        return koza_snd()
    if rodzaj == "maszynista":
        return _s(whoosh(0.4, 500, 3000) * 0.4, knock(260, 0.12) * 0.3)
    if rodzaj == "kartka":
        return whoosh(0.35, 1200, 7000) * 0.45
    if rodzaj == "blysk":
        r_, kolor = extra
        if klucz == "raport":
            return _s(szklo(), thud(0.4) * 0.4)
        if klucz in ("armaty", "zap_armaty"):
            return armata()
        return strzal("parawan" in dekor_i or "ciemnosc" in dekor_i)
    return None


def main():
    import render as R
    us = ujecia()
    total = R.DUR
    n = N(total)
    fx, voice = np.zeros(n), np.zeros(n, bool)
    starts = {}
    print("przegląd filmu (podsłuch ujęć)…", flush=True)
    lalki, konie, jedno, dekor, noc, robaki, ogien = skan()
    print(f"lalki: {len(lalki)} torów, konie: {len(konie)}, znaki: {len(jedno)}, robak w {len(robaki)} ujęciach, ogień w {len(ogien)}", flush=True)
    Z = zdarzenia()
    events = 0
    for idx, (a, b, *_) in enumerate(R.SCENES):
        klucz = R.KOL[idx]
        sec = b - a
        starts[klucz] = a
        vs, vl = okno_kwestii(us[idx][7], klucz in HAK)
        if vl:
            voice[N(a + vs):N(a + vs + vl)] = True
        d = dekor.get(idx, {})
        amb = tlo(rodzaj_tla(d), sec + 0.3, idx, bool(noc.get(idx, 0) > 0.5 or d.get("noc")))
        i = N(a)
        fx[i:i + len(amb)] += amb[:max(0, n - i)]
        src, od = (R.WYCINEK[klucz][0], R.WYCINEK[klucz][1]) if klucz in R.WYCINEK else (klucz, 0.0)
        if src == klucz:
            evs = [(R.czas_ujecia(idx, at), kind, g) for at, kind, g in Z.get(klucz, []) if 0 <= at < R.SZKIC_CZAS[idx][0]]
        else:  # skrót innego ujęcia gra akcję oryginału w jej rytmie od chwili `od`
            evs = [(at - od, kind, g) for at, kind, g in Z.get(src, []) if od <= at < od + sec]
        gr = R.GRANICE[idx]
        zam, dl, czekaj, otw = R.KURTYNA
        if gr["ostatnie_aktu"] and idx < len(R.SCENES) - 1 and gr["akt"] + 1 not in R.BEZ_KURTYNY:
            evs += [(sec - zam, "kurtyna_z", 1.0), (sec - zam + dl - 0.05, "klaps", 0.8)]
        elif gr["pierwsze_aktu"] and idx > 0 and gr["akt"] not in R.BEZ_KURTYNY:
            evs += [(czekaj, "kurtyna_r", 1.0)]
        if klucz in R.BUDUJ and klucz not in R.WYCINEK:
            evs += [(dd, "whoosh", 0.3) for dd in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(dd, "knock", 0.25) for dd in (0.75, 1.05, 1.4, 1.7)]
        if idx in ogien:  # ogień od pierwszego płomienia do końca ujęcia
            o0 = max(0.0, ogien[idx][0] - a)
            evs.append((o0, "ogien", max(0.5, min(sec, ogien[idx][1] - a + 0.4) - o0)))
        for at, kind, gg in evs:
            if at >= sec or at < 0:
                continue
            s = DLUGIE[kind](min(gg, sec - at + 0.3)) if kind in DLUGIE else KROTKIE[kind]() * gg
            j = N(a + at)
            fx[j:j + len(s)] += s[:max(0, n - j)]
            events += 1
    puenty = []
    for key, (at, rodzaj, extra, i) in jedno.items():
        s = dzwiek_znaku(rodzaj, extra, R.KOL[i], dekor.get(i, {}))
        if rodzaj == "podpis" and extra in PUENTY:
            puenty.append(at)
        if s is None:
            continue
        j = N(at)
        if 0 <= j < n:
            fx[j:j + len(s)] += s[:n - j]
            events += 1
    fx += kopyta(konie, n)
    fx += kroki(lalki, n)
    fx += robak_tory(robaki, n)
    fx *= sciszanie(voice, POD_KWESTIA_EFEKTY)
    mus = muzyka(total, starts, voice, puenty)
    OUT.mkdir(exist_ok=True)
    zapisz(OUT / "efekty.wav", fx)
    zapisz(OUT / "muzyka.wav", mus)
    rms = lambda x: 20 * math.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)  # noqa: E731
    print(f"efekty: {events} zdarzeń + tło, kopyta, kroki, robak | muzyka: {len(CUES)} wpisów | puent {len(puenty)} | {total:.1f} s | "
          f"RMS muzyka {rms(mus):.1f} dB, efekty {rms(fx):.1f} dB", flush=True)


if __name__ == "__main__":
    main()
