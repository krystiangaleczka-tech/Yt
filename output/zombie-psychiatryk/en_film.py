"""Wersja angielska (US) wariantu A: kto mówi, tekst kwestii, plik głosu i jego miejsce w ujęciu.

Wspólne dla rysunku (napisy w dzien_base / render_d01) i dźwięku (film_en.py), żeby napis i głos zawsze się zgadzały.
Głosy: voice/en/dni/dNN_II.wav (dzień, ujęcie) — robi je glosy_en.py. Postać bez głosu ma sam napis.
"""
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
