"""Dźwięk filmu „Syn słońca — powstanie Japonii” bez lektora: muzyka (ścieżka Muzyka) i efekty (ścieżka Efekty), synteza w numpy.

Wzór: output/pierwszy-cesarz/efekty.py (te same dźwięki bazowe).
- Muzyka: szarpane struny w japońskiej skali in (Karplus-Strong, brzmienie zbliżone do koto) na burdonie; w aktach bitew
  bęben taiko; pod kwestiami lektora ściszona o 9 dB.
- Efekty: tło miejsca (wiatr, morze, las, burza, noc, wnętrze), papier i drewno teatru przy każdej zmianie dekoracji
  (ujęcia z render.BUDUJ), wydarzenia ujęć z ZDARZENIA (czasy od początku ujęcia — te same co w funkcjach ujęć).

uruchom:  python3 efekty.py            → dzwiek/muzyka.wav, dzwiek/efekty.wav (cały film, 44,1 kHz mono)
          JEZYK=en python3 efekty.py   → dzwiek_en/ (długości ujęć z lektora EN)
Przegląd 17.11 (wytyczne 1.12, 1.14, Rytm 7): kurtyna z dźwiękiem między aktami (zatwierdzony dźwięk z „Pierwszego
cesarza”), migający X z brzęczykiem, cios w fazach, rytm włóczni; głos człowieka (śmiech bogów, jęk konających) z
nagrań w dzwiek_probki/ (glosy.py — Chatterbox Turbo, znaczniki [laugh], [groan]), nie z szumu. Czasy zdarzeń
z nazwanych stałych w ujęciach (OGIEN_SMIERC, UZUME_SMIECH, NAGA_RYTM, ZDRADA_CIOS…).
"""
import math
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"))
from dane import JEZYK, okno_kwestii, ujecia  # noqa: E402

SR = 44100
OUT = HERE / ("dzwiek_en" if JEZYK == "en" else "dzwiek")
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


# ---------- z „Pierwszego cesarza”: kurtyna (zatwierdzona przez reżysera 16.11), klapki, brzęczyk X, rzężenie, okrzyk ----------

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


# ---------- głos człowieka z nagrania (wytyczne 1.14) ----------
# Próbki z Chatterbox Turbo głosem lektora (glosy.py → dzwiek_probki/<rodzaj>_*.wav, 44,1 kHz mono); kolejne użycia
# biorą kolejne próbki. Bez próbek — cisza i ostrzeżenie (nigdy synteza szumu udająca człowieka).
PROBKI = HERE / "dzwiek_probki"
_GLOSY, _ILE = {}, {}


def glos(rodzaj, g=0.55):
    if rodzaj not in _GLOSY:
        _GLOSY[rodzaj] = []
        for f in sorted(PROBKI.glob(f"{rodzaj}_*.wav")):
            with wave.open(str(f)) as w:
                x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
            _GLOSY[rodzaj].append(x / (np.abs(x).max() + 1e-9))
        if not _GLOSY[rodzaj]:
            print(f"UWAGA: brak próbek {rodzaj}_*.wav w {PROBKI} (glosy.py) — w tym miejscu cisza", flush=True)
    probki = _GLOSY[rodzaj]
    if not probki:
        return np.zeros(N(0.1))
    n = _ILE.get(rodzaj, 0)
    _ILE[rodzaj] = n + 1
    return probki[n % len(probki)] * g


SFX = {"gong": gong, "whoosh": whoosh, "knock": knock, "drum": drum, "crack": crack, "clash": clash, "coin": coin,
       "thud": thud, "splash": splash, "sword": sword, "gong_s": lambda: gong(2.5, 220) * 0.6, "thunder": thunder,
       "crow": crow_call, "rooster": rooster, "growl": growl, "chime": chime, "slurp": slurp,
       "kurtyna_z": kurtyna_zasuwa, "kurtyna_r": kurtyna_rozsuwa, "klaps": klaps, "buzz": buzz, "rattle": rattle, "shout": shout,
       "smiech": lambda: glos("smiech", 0.6), "jek": lambda: glos("jek", 0.55), "okrzyk": lambda: glos("okrzyk", 0.5)}
# głosy postaci z modelu mowy (glosy.py, rodzaje z NAGRANIA) pod tabliczkami: rodzaj „g:<rodzaj>”
for _r in ("au", "aaa", "nie_moge", "pomocy", "hmm", "stop", "nie_ma_mowy", "aaaa", "bracie", "bu", "oh", "pulapka", "placz", "gasp",
           "hura", "uff", "tada", "wow", "au_s", "hik", "ej", "moje", "taka_sama", "starsze", "zloto", "ups"):
    SFX["g:" + _r] = (lambda r: lambda: glos(r, 0.6))(_r)


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
import ujecia_a as A  # noqa: E402  czasy zdarzeń z ujęć (te same stałe co w rysunku, wytyczne 1.12)
import ujecia_b as B  # noqa: E402

B_NAGA_RYTM = A.NAGA_RYTM

ZDARZENIA = {
    "teatr": [(0.2, "gong", 1.0), (0.7, "knock", 0.6), (1.3, "whoosh", 0.6)],
    "luty": [(1.0, "whoosh", 0.4)] + [(1.8 + 0.45 * n, "knock", 0.5) for n in range(9)],
    "cien": [(0.3, "knock", 0.5), (1.4, "whoosh", 0.3), (3.9, "whoosh", 0.5)],
    "meduza": [(1.0, "water", 3.0), (A.MEDUZA_ROSNIE[0], "whoosh", 0.35)],  # meduza wynurza się, potem rośnie
    "most": [(A.MOST_SPAD[0], "whoosh", 0.6), (A.MOST_ZJAZD["izanami"], "whoosh", 0.4), (A.MOST_ZJAZD["izanagi"], "whoosh", 0.4),
             (sum(A.MOST_SPAD) - 0.1, "knock", 0.4)],
    "wlocznia": [(0.6, "splash", 0.5), (1.4, "water", 6.0)],
    "kropla": [(2.55, "splash", 0.7), (2.8, "thud", 0.4)],
    "wyspy": [(0.7 + 0.55 * n, "thud", 0.35) for n in range(8)],
    "ogien": [(0.9, "fire", 6.0), (2.9, "whoosh", 0.4), (A.OGIEN_SMIERC - 0.1, "jek", 1.0)],
    "yomi": [(0.0, "steps", 3.6), (3.4, "whoosh", 0.4), (5.6, "steps", 2.2), (7.4, "thud", 1.0)],
    "rzeka": [(0.3, "water", 9.0), (1.6, "splash", 0.5), (2.2, "chime", 1.0), (5.2, "splash", 0.5), (8.4, "splash", 0.5), (8.6, "thunder", 0.6)],
    "susanoo": [(0.9, "whoosh", 1.0), (1.6, "whoosh", 0.9), (2.6, "crack", 0.8), (3.0, "thud", 0.7), (4.0, "whoosh", 0.8)],
    "jaskinia": [(0.4, "steps", 2.6), (3.4, "thud", 0.9), (4.6, "whoosh", 0.5)],
    "ciemno": [(0.3, "fire", 2.5), (0.8, "knock", 0.3), (1.3, "knock", 0.3), (1.8, "knock", 0.3)],
    "koguty": [(0.4, "knock", 0.5), (2.0, "whoosh", 0.4), (3.0, "whoosh", 0.4), (5.6, "rooster", 1.0), (7.2, "rooster", 0.9)],
    "uzume": [(0.6 + 0.55 * n, "drum", 0.35) for n in range(14)] + [(A.UZUME_SMIECH, "smiech", 1.0), (A.UZUME_SMIECH + 1.3, "smiech", 1.0), (A.UZUME_SMIECH + 2.6, "smiech", 1.0)] + [(A.UZUME_SMIECH + 0.3 + d, "whoosh", 0.25) for d in (0.0, 0.5, 1.4, 2.0)],
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
    "flota": [(0.0, "water", 9.0), (0.9, "oars", 8.0), (2.4, "oars", 7.0)],
    "postoje": [(0.0, "water", 9.0), (1.0, "dig", 8.0)],
    "naniwa": [(0.4, "water", 5.0), (0.6, "oars", 3.5), (2.6, "march", 7.0), (2.6, "drum", 0.7), (3.4, "shout", 0.8)],
    "nagasune": [(0.5, "thud", 0.6), (1.6, "march", 6.0), (1.6, "drum", 0.9), (2.2, "whoosh", 0.3)] + [(a, "shout", 0.9) for a in B_NAGA_RYTM] + [(a + 0.3, "drum", 0.8) for a in B_NAGA_RYTM],
    "strzaly": [(0.0, "whoosh", 0.9), (0.15, "whoosh", 0.8), (0.3, "whoosh", 0.8), (0.9, "thud", 0.6), (1.1, "thud", 0.5),
                (0.0, "fire", 2.2)],  # płonące strzały (reżyser 20.11.2026)
    "rana": [(0.4, "whoosh", 0.7), (0.9, "thud", 0.9), (0.95, "jek", 1.0), (0.95, "whoosh", 0.25)],
    "pod_slonce": [(0.8, "whoosh", 0.3), (4.6, "knock", 0.3)],
    "itsuse": [(0.0, "water", 8.0), (B.ITSUSE_SMIERC - 0.2, "jek", 1.0), (B.ITSUSE_SMIERC + 0.9, "thud", 0.4)],
    "burza": [(0.0, "storm", 7.0), (1.0, "thunder", 1.0), (3.3, "thunder", 1.0), (2.6, "crack", 0.7), (3.4, "splash", 0.8)],
    "sam": [(0.0, "water", 4.5)],
    "las": [(0.4, "whoosh", 0.4), (1.2, "march", 2.0)],
    "niedzwiedz": [(0.6, "growl", 2.4)] + [(4.4 + 0.3 * n, "thud", 0.5) for n in range(13)] + [(4.9 + 0.5 * n, "chime", 0.35) for n in range(4)],
    "takakuraji": [(0.5, "whoosh", 0.6), (2.4, "crack", 0.5), (2.5, "chime", 0.8), (4.0, "steps", 5.0)],
    "przebudzenie": [(2.2, "sword", 0.8), (2.3, "chime", 0.9)] + [(3.0 + 0.6 * n, "knock", 0.4) for n in range(6)],
    "wrona": [(0.8, "crow", 1.0), (3.6, "crow", 0.8), (0.0, "march", 8.0)],
    "trzy_nogi": [(0.3, "whoosh", 0.5), (1.6, "knock", 0.4), (2.4, "crow", 0.9)],
    "yamato": [(2.2 + 0.6 * n, "knock", 0.5) for n in range(3)] + [(0.0, "drum", 0.4)],
    "pulapka": [(2.8, "whoosh", 0.3), (6.2, "steps", 1.0), (B.PULAPKA_BELKA, "whoosh", 0.4), (B.PULAPKA_BELKA + 0.35, "thud", 1.2), (B.PULAPKA_BELKA + 0.35, "crack", 0.8)] + [(B.PULAPKA_BELKA + 0.4 + 0.48 * n, "buzz", 1.0) for n in range(2)],
    "bitwa": [(1.0, "march", 8.0), (1.0, "drum", 0.9), (3.0, "clash", 1.0), (3.0, "shout", 0.9), (3.4, "clash", 0.8), (4.6, "clash", 0.7), (6.0, "clash", 0.7), (2.6, "hail", 9.0), (2.0, "thunder", 0.7), (5.5, "thunder", 0.8)],
    "ptak": [(0.4, "whoosh", 0.6), (2.6, "chime", 1.4), (2.8, "gong_s", 0.6), (0.0, "hail", 3.0)],
    "blysk": [(0.0, "thunder", 1.0), (0.05, "chime", 1.0), (0.4, "march", 1.5)],
    "order": [(0.4, "whoosh", 0.4), (1.8, "coin", 0.6)],
    "strzala_nieba": [(0.8, "whoosh", 0.4), (2.2, "whoosh", 0.4), (4.4, "knock", 0.5)],
    "zdrada": [(0.3, "whoosh", 0.4), (B.ZDRADA_CIOS - 0.15, "sword", 1.1), (B.ZDRADA_CIOS, "thud", 1.0), (B.ZDRADA_CIOS + 0.3, "jek", 1.0)] + [(B.ZDRADA_CIOS + 0.35 + 0.48 * n, "buzz", 1.0) for n in range(2)] + [(B.ZDRADA_CIOS + 1.4, "thud", 0.5), (B.ZDRADA_CIOS + 2.2, "steps", 1.6), (B.ZDRADA_CIOS + 3.9, "knock", 0.4)],
    "palac": [(0.6, "thud", 0.6), (1.8, "thud", 0.6), (3.0, "knock", 0.6), (4.4, "whoosh", 0.5), (5.6, "thud", 0.7), (6.2, "whoosh", 0.4),
              (7.4, "knock", 0.6)],
    "tron": [(0.8, "whoosh", 0.4), (2.2, "chime", 0.6), (2.8, "chime", 0.5), (3.4, "chime", 0.5), (5.0, "gong", 0.8)],
    "imie": [(0.6, "whoosh", 0.4), (1.6, "gong_s", 0.6)],
    "zona": [(0.8, "whoosh", 0.3), (3.0, "chime", 0.4)],
    "pola": [(0.0, "wind_long", 9.0), (2.4, "whoosh", 0.4), (4.6, "whoosh", 0.4)],
    "smierc": [(0.6, "whoosh", 0.4), (B.SMIERC_CESARZA - 0.1, "rattle", 1.0), (B.SMIERC_CESARZA + 0.6, "gong", 0.8), (B.SMIERC_CESARZA + 2.4, "whoosh", 0.35), (B.SMIERC_CESARZA + 3.2, "whoosh", 0.25)],
    "pusto": [(0.2, "chime", 0.5)],
    "linia": [(0.6 + 0.22 * n, "knock", 0.25) for n in range(26)] + [(4.6 + 0.07 * n, "knock", 0.08) for n in range(22)],
    "kronika": [(0.3, "knock", 0.6), (0.8, "whoosh", 0.4), (1.6, "scroll", 6.0), (2.6, "whoosh", 0.4), (6.4, "whoosh", 0.4)],
    "rachunek": [(0.8, "whoosh", 0.4), (2.6, "whoosh", 0.4), (4.4, "whoosh", 0.4), (5.4, "gong_s", 0.5)],
    "jomon": [(2.4, "steps", 7.0), (1.6, "knock", 0.5), (1.9, "knock", 0.5)],
    "wa": [(0.3, "whoosh", 0.7)] + [(2.0 + 0.5 * n, "knock", 0.2) for n in range(12)],
    "pieczec": [(0.3, "whoosh", 0.5), (1.6, "coin", 0.6), (2.0, "whoosh", 0.4)],
    "odcisk": [(0.55, "knock", 1.0), (0.6, "thud", 0.5)],
    "chlop": [(0.0, "dig", 3.0), (3.0, "coin", 0.8), (3.6, "chime", 0.5), (3.6, "whoosh", 0.25), (4.0, "whoosh", 0.4)],
    "himiko": [(0.2, "whoosh", 0.4), (1.0, "knock", 0.5)] + [(2.2 + 0.4 * n, "chime", 0.25) for n in range(10)],
    "kofun": [(0.6, "whoosh", 0.7), (4.2, "whoosh", 0.4)],
    "haniwa": [(0.4 + 0.45 * n, "knock", 0.4) for n in range(20)] + [(0.2 + 0.12 * n, "knock", 0.12) for n in range(22)],
    "tancerz": [(0.2, "chime", 0.7)],
    "nihon": [(0.4, "whoosh", 0.4), (2.2, "whoosh", 0.6), (4.2, "whoosh", 0.4), (4.6, "gong", 0.9)],
    "luty2": [(0.4, "whoosh", 0.4), (1.4, "whoosh", 0.4)] + [(3.0 + 0.4 * n, "knock", 0.45) for n in range(9)],
    "koronacja": [(0.6, "thud", 0.5), (1.8, "knock", 0.5), (2.6, "knock", 0.5), (3.2, "knock", 0.5), (5.0, "whoosh", 0.4), (5.2, "gong_s", 0.6)],
    "koniec": [(0.2, "water", 6.0), (9.0, "gong", 0.9)],
    "dzieki": [(0.5, "whoosh", 0.5), (0.8, "whoosh", 0.4), (1.5, "whoosh", 0.4), (1.6, "gong_s", 0.5)],
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



DLUGIE = ("march", "hooves", "fire", "water", "wagon", "steps", "dig", "roll", "oars", "storm", "hail", "wind_long", "scroll")


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


AKT_NASTROJ = {0: "wojna", 1: "mit", 2: "noc", 3: "wojna", 4: "spokoj", 5: "noc", 6: "wojna", 7: "spokoj", 8: "spokoj", 9: "spokoj"}


def zapisz(path, x):
    x = np.tanh(x * 1.2) * 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


# Dźwięki dokładane do skrótów (akt 0, render.WYCINEK): mocne uderzenie na start zapowiedzi i gong pod tytuł teatru.
DODATKI = {"zap_jaskinia": [(0.0, "gong", 1.0), (0.0, "drum", 0.9)], "zap_blysk": [(0.0, "drum", 0.9), (0.0, "gong", 0.8)],
           # zapowiedź ma uderzenie na każdym cięciu, jak zwiastun (Podręcznik, Dźwięk; 20.11.2026)
           **{k: [(0.0, "drum", 0.8)] for k in ("zap_susanoo", "zap_miecz", "zap_strzaly", "zap_uzume", "zap_pulapka", "zap_niedzwiedz",
                                              "zap_wrona", "zap_bitwa")},
           "teatr": [(0.1, "kurtyna_r", 1.0), (0.9, "gong", 0.9), (1.9, "whoosh", 0.4)] + [(1.6 + 0.3 * n, "knock", 0.35) for n in range(4)],
           "hak_najazd": [(0.3, "whoosh", 0.25), (1.6, "whoosh", 0.2)],  # podpis Iwarebiko (D14: brat w haku bez podpisu)
           # szczyty (przegląd 18.11.2026): po ciszy muzyki mocne uderzenie — ósma głowa węża, pierwsze krakanie wrony
           "orochi": [(4.8, "drum", 1.0), (4.8, "gong", 0.8)], "wrona": [(0.8, "gong", 0.6)],
           # markery reżysera 18.11.2026: strzała w góry, skoki brata, łuk napięty w zwrocie ku słońcu
           "wschod": [(3.6, "whoosh", 0.55), (4.15, "thud", 0.4)], "luty2": [(7.0, "whoosh", 0.4), (8.6, "whoosh", 0.4), (8.8, "knock", 0.4)], "bracia": [(6.5, "knock", 0.4), (7.15, "knock", 0.4), (7.8, "knock", 0.4)],
           # teatr cieni (reżyser 20.11.2026, ujęcie 14): wejście Iwarebiko, trzy szarpnięcia strzały, jęk brata, opadająca ręka
           "hak_cien": [(0.1, "whoosh", 0.25)] + [(a, "knock", 0.3 + 0.05 * n) for n, a in enumerate(A.CIEN_SZARP)]
                       + [(A.CIEN_SZARP[0] + 0.05, "jek", 0.6), (A.CIEN_SMIERC, "thud", 0.3)],
           # wąż w haku: ósma głowa tuż przed pytaniem — bęben i gong jak w ujęciu „orochi”
           "hak_waz": [(0.6 + 0.6 * 7, "drum", 1.0), (0.6 + 0.6 * 7, "gong", 0.8)]}
# Skróty, które biorą oryginał bez gagu (s_orochi w haku): dźwięki gagu wypadają z ich fragmentu (sekundy oryginału)
BEZ_GAGU = {"hak_waz": (A.OROCHI_GRYZ[0], A.OROCHI_GRYZ[1] + 0.5)}


# Głos pod tabliczką i dźwięk gagu (Podręcznik, „Dźwięk”, Głosy ludzi 4; „Humor i gagi”, Dźwięk gagu): sekunda od początku
# ujęcia = chwila, gdy tabliczka zaczyna zjeżdżać, + ok. 0,3 s. Klucz to ujęcie źródłowe — skróty (render.WYCINEK) biorą to,
# co wypada w ich fragmencie. Reżyser 20.11.2026: „dołóż głosy, efekty, gagi”.
GLOSY_UJ = {
    "wschod": [(2.1, "g:hmm", 1.0)],
    "itsuse": [(1.7, "g:nie_moge", 1.0)],
    "starcy": [(1.2, "g:placz", 1.0), (3.0, "g:placz", 0.8)],
    "bitwa": [(3.0, "g:hura", 0.7), (3.3, "g:hura", 0.6), (7.5, "g:hura", 0.5)],
    "blysk": [(0.3, "g:gasp", 1.0)],
    # gagi (GAGI.md)
    "meduza": [(A.MEDUZA_HOP, "splash", 0.5), (A.MEDUZA_HOP + 0.7, "knock", 0.4)],
    "wlocznia": [(5.9, "g:uff", 1.0)],
    "kropla": [(4.7, "g:tada", 1.0), (4.6, "chime", 0.6)],
    "lustro": [(2.9, "g:wow", 1.0)],
    "wygnanie": [(3.5, "g:au_s", 1.0), (3.45, "chime", 0.35)],
    "pije": [(1.2, "g:hik", 1.0)],
    "yamato": [(2.9, "g:moje", 1.0), (3.5, "g:moje", 1.0), (4.1, "g:moje", 1.0)],
    "strzala_nieba": [(3.2, "g:taka_sama", 1.0)],
    "kronika": [(4.6, "g:starsze", 1.0), (4.4, "whoosh", 0.3)],
    "haniwa": [(B.HANIWA_UPADEK + 0.45, "thud", 0.8), (B.HANIWA_UPADEK + 0.7, "g:ups", 1.0)],
    # gagi 17–25 (GAGI.md, 20.11.2026): dźwięki z istniejących rodzajów
    "most": [(A.MOST_LAD, "thud", 0.6), (A.MOST_LAD + 0.2, "whoosh", 0.3), (A.MOST_LAD + 0.5, "knock", 0.3)],
    "uzume": [(A.UZUME_SPADA + 0.35, "thud", 0.7), (A.UZUME_SPADA + 1.4, "whoosh", 0.3)],
    "kadzie": [(A.KADZIE_MRUG + 0.2, "chime", 0.5)],
    "naniwa": [(A.NANIWA_WJAZD, "thud", 0.9), (A.NANIWA_WJAZD + 0.05, "crack", 0.5), (10.8, "g:stop", 1.0)],
    "wrona": [(B.WRONA_ZGUBA, "steps", 3.0)],
    "order": [(B.ORDER_MRUG + 0.2, "chime", 0.6)],
    "jomon": [(B.JOMON_WACH + 0.2, "whoosh", 0.2)],
    "rachunek": [(B.RACHUNEK_PEK, "knock", 0.5), (B.RACHUNEK_PEK + 0.05, "whoosh", 0.2)],
    "kofun": [(2.2, "whoosh", 0.3), (4.6, "whoosh", 0.5), (4.65, "knock", 0.3), (B.KOFUN_POCHOWEK, "steps", 3.0)],
    # markery i uwagi reżysera 20.11.2026
    "orochi": [(A.OROCHI_GRYZ[0] + 0.2, "clash", 0.5), (A.OROCHI_GRYZ[1] + 0.2, "clash", 0.5), (A.OROCHI_GRYZ[0] + 0.3, "growl", 1.0)],
    "miecz": [(1.0, "whoosh", 0.4), (1.2, "growl", 0.8), (2.0, "chime", 0.8), (1.8, "g:pomocy", 1.0)],
    "skarby": [(A.SKARBY_MACH + 0.2 * n, "sword", 0.6) for n in range(6)] + [(A.SKARBY_MACH + 0.3, "g:hura", 0.8)],
    "flota": [(A.FLOTA_PIORUN, "thunder", 1.0), (A.FLOTA_PIORUN + 0.1, "fire", 2.8), (A.FLOTA_PIORUN + 1.2, "splash", 0.8),
              (A.FLOTA_MEWA, "whoosh", 0.5), (A.FLOTA_MEWA + 0.9, "g:ej", 1.0)],
    "nagasune": [(A.NAGA_SZTYLET, "sword", 0.6)] + [(A.NAGA_SZTYLET + 0.5 + 0.45 * i, "whoosh", 0.4) for i in range(3)] + [(5.6, "g:nie_ma_mowy", 1.0)],
    "rana": [(0.3, "fire", 2.4), (5.5, "g:aaa", 1.0)],
    "pod_slonce": [(0.0, "fire", 11.0)],
    "burza": [(B.BURZA_PIORUN[0], "thunder", 1.0), (B.BURZA_PIORUN[1], "thunder", 1.0), (2.8, "g:aaaa", 1.0), (B.BURZA_PIORUN[1] + 0.4, "g:bracie", 1.0)],
    "sam": [(1.1, "chime", 0.6), (B.SAM_PIORUN, "thunder", 1.0), (B.SAM_PIORUN + 0.05, "gong_s", 0.8), (B.SAM_PIORUN + 0.4, "g:hmm", 0.6)],
    "las": [(B.LAS_WIEWIORKA + 0.3 * n, "knock", 0.15) for n in range(8)],
    "niedzwiedz": [(B.NIEDZ_STAJE, "growl", 1.6), (B.NIEDZ_STAJE + 1.0, "g:bu", 1.0)],
    "przebudzenie": [(B.PRZEB_MIECZ[0], "sword", 0.4), (B.PRZEB_MIECZ[1], "whoosh", 0.8), (B.PRZEB_MIECZ[2], "knock", 0.5), (B.PRZEB_MIECZ[2] + 0.05, "chime", 0.9)],
    "trzy_nogi": [(B.WRONA_PILKA[0] + 0.4 * n, "chime", 0.35) for n in range(3)] + [(B.WRONA_PILKA[1], "knock", 0.7), (B.WRONA_PILKA[1] + 0.05, "whoosh", 0.5),
                  (B.WRONA_PILKA[2], "whoosh", 0.5), (B.WRONA_PILKA[2] + 0.45, "thud", 0.7), (B.WRONA_PILKA[2] + 0.5, "crow", 0.9)]
                 + [(B.WRONA_PILKA[2] + 0.9 + 0.5 * n, "chime", 0.3) for n in range(3)],
    "pulapka": [(B.PULAPKA_BELKA + 0.3, "thud", 1.0), (B.PULAPKA_BELKA + 0.7, "thud", 0.5), (3.1, "g:pulapka", 1.0)],
    "zdrada": [(B.ZDRADA_RZUT, "whoosh", 0.6)],
    "palac": [(8.3, "g:tada", 1.0), (8.2, "chime", 0.6), (B.PALAC_FILAR, "knock", 0.6), (B.PALAC_FILAR + 0.1, "thud", 0.4)],
    "imie": [(1.6, "chime", 0.8)],
    "pusto": [(0.6, "chime", 0.4)],
    "chlop": [(3.9, "g:oh", 1.0), (5.8, "g:zloto", 1.0), (3.2, "chime", 0.6)],
    "himiko": [(6.9, "g:wow", 1.0), (0.6, "whoosh", 0.4)],
    "nihon": [(6.3, "gong_s", 0.6)],
    "luty2": [(B.LUTY2_WULKAN, "thud", 0.5), (B.LUTY2_WULKAN + 0.05, "crack", 0.3)],
    "koronacja": [(0.6, "whoosh", 0.3)],
}
# Puenta gagu: muzyka cichnie o 9 dB na 0,6 s i wraca w 0,5 s, żeby dźwięk gagu wybrzmiał (Podręcznik, „Dźwięk”, Muzyka 9)
GAG_PUENTA = {"meduza": A.MEDUZA_HOP + 0.6, "wlocznia": 5.9, "kropla": 4.6, "lustro": 2.9, "wygnanie": 3.4, "pije": 1.2,
              "flota": A.FLOTA_MEWA + 0.9, "trzy_nogi": 2.4, "yamato": 4.1, "strzala_nieba": 3.2, "palac": 8.2, "kronika": 4.5,
              "himiko": 6.9, "haniwa": B.HANIWA_UPADEK + 0.45, "miecz": 1.8, "niedzwiedz": 2.5, "chlop": 5.8, "nagasune": 5.6,
              "naniwa": 10.8, "most": A.MOST_LAD, "uzume": A.UZUME_SPADA + 0.35, "kadzie": A.KADZIE_MRUG + 0.2,
              "order": B.ORDER_MRUG + 0.2, "rachunek": B.RACHUNEK_PEK, "kofun": 4.6, "jomon": B.JOMON_WACH + 0.2}


def sciszanie(voice, db, przed=0.25, w_dol=0.3, w_gore=0.9, przerwa=3.0):
    """Łagodne ściszanie pod lektorem (Podręcznik, „Dźwięk”, Muzyka 5): w dół w 0,3 s, zaczyna 0,25 s przed kwestią, w górę
    w 0,9 s; przerwy krótsze niż 3 s zostają ściszone. Liczone w 100 Hz i rozciągnięte na próbki."""
    hop = SR // 100
    m = voice[::hop].astype(float)
    on = np.flatnonzero(np.diff(np.r_[0, m, 0]) == 1)
    off = np.flatnonzero(np.diff(np.r_[0, m, 0]) == -1)
    cel = np.zeros(len(m))
    for i, (a, b) in enumerate(zip(on, off)):
        a = max(0, a - int(przed * 100))
        if i + 1 < len(on) and on[i + 1] - b < przerwa * 100:
            b = on[i + 1]
        cel[a:b] = 1.0
    g, x = np.zeros(len(m)), 0.0
    for i, c in enumerate(cel):
        x += (c - x) * (1 - math.exp(-1 / (100 * (w_dol if c > x else w_gore) / 3)))
        g[i] = x
    return np.interp(np.arange(len(voice)) / hop, np.arange(len(m)), 10 ** (db * g / 20))


def przystanki(n, starts):
    hop = SR // 100
    g = np.ones(n // hop + 1)
    for klucz, sec in GAG_PUENTA.items():
        if klucz not in starts:
            continue
        i = int((starts[klucz] + sec) * 100)
        prof = np.r_[np.linspace(1, 0.355, 6), np.full(54, 0.355), np.linspace(0.355, 1, 50)]  # −9 dB na 0,6 s, powrót 0,5 s
        j = min(len(g), i + len(prof))
        g[i:j] = np.minimum(g[i:j], prof[:j - i])
    return np.interp(np.arange(n) / hop, np.arange(len(g)), g)


# Cisza muzyki przed szczytem (przegląd 18.11.2026: „za mało ciszy i muzyki przy szczytach”): w oknie (od, do) sekund od początku
# ujęcia muzyka milknie (zostają efekty: syk głów, grad), po nim wraca głośniej i przez 3 s opada do zwykłej głośności.
CISZA = {"orochi": (0.0, 4.7), "wrona": (-1.0, 0.8), "ptak": (0.0, 2.5)}


def cisza_muzyki(n, starts):
    g = np.ones(n)
    r = N(0.15)
    for klucz, (a, b) in CISZA.items():
        if klucz not in starts:
            continue
        i0, i1 = max(0, N(starts[klucz] + a)), min(n, N(starts[klucz] + b))
        g[i0:i1] = 0.0
        g[max(0, i0 - r):i0] = np.minimum(g[max(0, i0 - r):i0], np.linspace(1, 0, i0 - max(0, i0 - r)))
        j = min(n, i1 + N(3.0))
        g[i1:j] = np.linspace(1.6, 1.0, j - i1) * np.minimum(1, np.arange(j - i1) / max(1, N(0.08)))
    return g


def main():
    import render as R
    import scena
    us = ujecia()
    total = sum(u[5] for u in us)
    n = N(total)
    fx, voice = np.zeros(n), np.zeros(n, bool)
    t0, acts, events, starts = 0.0, [], 0, {}
    for idx, (akt, _, klucz, kadr, ruch, sec, opis, snd) in enumerate(us):
        starts[klucz] = t0
        vs, vl = okno_kwestii(snd)
        if vl:
            voice[N(t0 + vs):N(t0 + vs + vl)] = True
        if not acts or acts[-1][2] != akt:
            acts.append([t0, t0 + sec, akt])
        acts[-1][1] = t0 + sec
        # skrót innego ujęcia (render.WYCINEK): tło i zdarzenia oryginału z tego samego fragmentu, przesunięte do początku
        src, od = (R.WYCINEK[klucz][0], R.WYCINEK[klucz][1]) if klucz in R.WYCINEK else (klucz, 0.0)
        place = ("morze" if src in MORZE else "noc" if src in NOC else "las" if src in LAS else "sala" if src in WNETRZE
                 else "burza" if src in BURZA else "wiatr")
        amb = ambient(place, sec + 0.3, idx)
        i = N(t0)
        fx[i:i + len(amb)] += amb[:n - i]
        gag = BEZ_GAGU.get(klucz, (1e9, 1e9))
        evs = [(at - od, kind, g) for at, kind, g in ZDARZENIA.get(src, []) + GLOSY_UJ.get(src, [])
               if od <= at < od + sec and not gag[0] <= at <= gag[1]] + DODATKI.get(klucz, [])
        g = R.GRANICE[idx]  # przejścia: kurtyna między aktami (render.przejscie), klapki przy tytule aktu
        zam, dl, czekaj, otw = R.KURTYNA
        if g["ostatnie_aktu"] and idx < len(us) - 1 and g["akt"] + 1 not in R.BEZ_KURTYNY:
            evs += [(sec - zam, "kurtyna_z", 1.0), (sec - zam + dl - 0.05, "klaps", 0.8)]
        elif g["pierwsze_aktu"] and idx > 0 and g["akt"] not in R.BEZ_KURTYNY:
            evs += [(czekaj, "kurtyna_r", 1.0)]
        if klucz in R.BUDUJ and klucz not in R.WYCINEK:  # zmiana dekoracji: papier i drewno w rytm wjeżdżających elementów
            evs += [(d, "whoosh", 0.35) for d in (0.0, 0.25, 0.45, 0.65, 0.9)] + [(d, "knock", 0.3) for d in (0.75, 1.05, 1.4, 1.7)]
        for at, kind, g in evs:
            if at >= sec:
                continue
            s = long_sound(kind, min(g, sec - at)) if kind in DLUGIE else SFX[kind]() * g
            j = N(t0 + at)
            fx[j:j + len(s)] += s[:n - j]
            events += 1
        t0 += sec
    fx *= sciszanie(voice, -5.0)
    mus = muzyka(total, np.zeros(n, bool), [(a0, a1, AKT_NASTROJ[a]) for a0, a1, a in acts]) * cisza_muzyki(n, starts) \
        * sciszanie(voice, -8.0) * przystanki(n, starts)
    OUT.mkdir(exist_ok=True)
    zapisz(OUT / "efekty.wav", fx)
    zapisz(OUT / "muzyka.wav", mus)
    print(f"efekty: {events} zdarzeń + tło, muzyka: {len(acts)} aktów, {total:.1f} s")


if __name__ == "__main__":
    main()
