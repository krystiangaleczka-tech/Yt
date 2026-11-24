"""Wersja angielska (US) wariantu A: kto mówi, tekst kwestii, plik głosu i jego miejsce w ujęciu.

Wspólne dla rysunku (napisy w dzien_base / render_d01) i dźwięku (film_en.py), żeby napis i głos zawsze się zgadzały.
Głosy: voice/en/dni/dNN_II.wav (dzień, ujęcie) — robi je glosy_en.py. Postać bez głosu ma sam napis.
"""
import math
import re
import sys
import wave
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
from kwestie_en import EN  # noqa: E402

VOICE = HERE / "voice" / "en" / "dni"
WPS = 2.7  # słowa na sekundę — długość napisu postaci, która nie ma jeszcze głosu


def speaker(sound):
    """(postać, sposób) z kwestii rozpiski: 'L: …' → narrator; 'Zosia (radio): „…”' → ('zosia', 'radio')."""
    if sound.startswith("L:"):
        return "narrator", ""
    m = re.match(r"\s*([^„:(]+?)\s*(?:\(([^)]*)\))?\s*:\s*„", sound)
    if not m:
        return None, ""
    who = m.group(1).strip().lower()
    how = (m.group(2) or "").strip().lower()
    if who.startswith("megafon"):
        return "megafon", "megafon"
    return who, how


def text(day, i, sound):
    """Napis ujęcia po angielsku (dialog z myślnikiem, jak w polskiej wersji)."""
    who, _ = speaker(sound)
    if who is None:
        return ""
    en = EN.get(f"{day}.{i}")
    if en is None:
        raise KeyError(f"brak tłumaczenia kwestii {day}.{i}: {sound}")
    return en if who == "narrator" else "— " + en


def voice_file(day, i):
    return VOICE / f"d{day:02d}_{i:02d}.wav"


def _dur(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def placement(day, i, sound, T, vs, vl):
    """(start w ujęciu, długość) kwestii: start z rozpiski (oddech przed), ale tak, żeby głos skończył się
    przed cięciem; dłuższa kwestia zaczyna się wcześniej (nie przed 0,15 s) i najwyżej wychodzi za cięcie."""
    f = voice_file(day, i)
    if f.exists():
        d = _dur(f)
    elif speaker(sound)[0]:
        d = max(vl, len(EN.get(f"{day}.{i}", "").split()) / WPS)
    else:
        return vs, vl
    start = max(0.15, min(vs, T - d - 0.25))
    return start, d


# Oddech przed kwestią i pauza po niej w wersji EN (Podręcznik → Rytm 2: 0,5–1,2 s przed, 0,3–1,2 s po).
# Rozpiska liczyła ujęcia pod polskie kwestie; angielskie nagrania są często dłuższe i placement() ściskał je pod cięcie:
# 124 z 287 kwestii kończyło się 0,25 s przed cięciem, 27 zaczynało bez oddechu, d01_18 wychodziła za cięcie
# (reżyser, 13.11.2026: „za szybko się kończą zaraz po kwestii, albo mówi i w połowie się ucina”).
PRE_MIN, POST_MIN, POST_MAX = 0.5, 0.6, 1.2
STEP = 1 / 6  # długości ujęć w pełnych klatkach przy 24 i 30 kl./s (jak tempo.py)


def timing(day, i, sound, sec, vs, vl):
    """(długość ujęcia, start kwestii, długość kwestii) w wersji EN. Dłuższa kwestia wydłuża swoje ujęcie (WYTYCZNE 1.9):
    oddech przed z rozpiski (co najmniej PRE_MIN), nagranie, pauza po z rozpiski (POST_MIN…POST_MAX).
    Ujęcie nigdy się nie skraca — krótsza kwestia dostaje po prostu dłuższą pauzę."""
    f = voice_file(day, i)
    if f.exists():
        d = _dur(f)
    elif speaker(sound)[0]:
        d = max(vl, len(EN.get(f"{day}.{i}", "").split()) / WPS)
    else:
        return sec, vs, vl
    pre = max(PRE_MIN, vs)
    post = min(POST_MAX, max(POST_MIN, sec - vs - vl))
    need = math.ceil((pre + d + post) / STEP - 1e-6) * STEP
    return max(sec, round(need, 4)), pre, d


def separate(secs, changed):
    """Sąsiednie ujęcia różnią się co najmniej o ¼ s (Rytm 2): wydłużone ujęcie odsuwa się w górę od sąsiadów."""
    out = list(secs)
    for k in sorted(changed):
        near = [out[j] for j in (k - 1, k + 1) if 0 <= j < len(out)]
        while any(abs(out[k] - n) < 0.25 - 1e-6 for n in near):
            out[k] = round(out[k] + STEP, 4)
    return out
