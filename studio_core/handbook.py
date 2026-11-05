"""Podręcznik pracowni: zasady wspólne dla całej aplikacji, trzymane jako pliki Markdown w repozytorium.

Pliki leżą w ``docs/``, więc są w historii gita i każdy, kto przejmie pracę, ma te same zasady. Aplikacja je
pokazuje i pozwala edytować (zapis wprost do pliku). Zasady konkretnego filmu siedzą w planie filmu (``book``).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = [
    ("praca", "Jak pracujemy: od scenariusza do ujęcia", "docs/podrecznik/01_PRACA.md"),
    ("sekwencja", "Sekwencja, świat i ciągłość", "docs/podrecznik/02_SEKWENCJA_I_SWIAT.md"),
    ("rytm", "Rytm i tempo ujęć", "docs/podrecznik/03_RYTM.md"),
    ("kadr", "Wytyczne kadru (czego nie wolno)", "docs/WYTYCZNE_UJEC.md"),
    ("animacja", "Animacja rysowana kodem", "docs/podrecznik/04_ANIMACJA_KODEM.md"),
    ("recenzja", "Recenzja jednostki (dnia)", "docs/podrecznik/05_RECENZJA.md"),
    ("dziennik", "Dziennik pracy i zmiany w locie", "docs/podrecznik/06_DZIENNIK_I_ZMIANY.md"),
]


def _path(key: str) -> Path:
    found = next((p for k, _, p in MANIFEST if k == key), None)
    if not found:
        raise ValueError("Nie ma takiego rozdziału podręcznika")
    return ROOT / found


def chapters() -> list[dict]:
    out = []
    for key, title, rel in MANIFEST:
        path = ROOT / rel
        out.append({"key": key, "title": title, "path": rel,
                    "text": path.read_text(encoding="utf-8") if path.exists() else ""})
    return out


def save(key: str, text: str) -> dict:
    if not isinstance(text, str) or len(text) > 400_000:
        raise ValueError("Rozdział musi być tekstem do 400 tys. znaków")
    path = _path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return next(c for c in chapters() if c["key"] == key)
