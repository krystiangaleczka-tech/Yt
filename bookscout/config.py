"""Ścieżki, ustawienia domyślne i mapa kategorii Book Scout."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("BOOKSCOUT_DATA", ROOT / "data"))
DB_PATH = DATA_DIR / "scout.db"
BATCH_DIR = DATA_DIR / "batches"
EXPORT_DIR = DATA_DIR / "exports"
STATIC_DIR = ROOT / "static"
# Wikimedia odrzuca zapytania bez adresu kontaktowego w User-Agent (403, polityka botów).
USER_AGENT = "BookScout/0.1 (https://github.com/krystiangaleczka-tech/Yt; local research tool) httpx"

DEFAULT_SETTINGS = {
    "channel_subs": 1000,      # obecni subskrybenci kanału
    "rpm_usd": 5.0,            # przychód na 1000 wyświetleń (EN, historia/edukacja)
    "monetized": True,         # czy kanał jest w programie partnerskim
    "hourly_rate_usd": 20.0,   # wycena godziny Twojej pracy
    "fixed_cost_usd": 40.0,    # muzyka, stocki, skany, dojazdy na film
    "video_minutes": 15,       # docelowa długość filmu
}


def load_env() -> None:
    """Wczytuje bookscout/.env (KEY=VALUE) bez nadpisywania zmiennych środowiska."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def google_api_key() -> str:
    return os.environ.get("GOOGLE_API_KEY", "").strip()


@dataclass(frozen=True)
class Category:
    key: str
    label: str
    ol: str                                   # fragment zapytania Open Library
    bn: dict = field(default_factory=dict)    # filtry API Biblioteki Narodowej


CATEGORIES = [
    Category("history", "Historia ogólna", 'subject:"history"', {"domain": "Historia"}),
    Category("military", "Wojny i bitwy", 'subject:"military history"', {"subject": "Wojna"}),
    Category("mysteries", "Zagadki i niewyjaśnione", 'subject:"curiosities and wonders"',
             {"subject": "Zjawiska paranormalne"}),
    Category("crime", "Zbrodnie i śledztwa", 'subject:"murder"', {"subject": "Zabójstwo"}),
    Category("exploration", "Wyprawy i odkrywcy", 'subject:"voyages and travels"', {"subject": "Wyprawy"}),
    Category("sea", "Morze i katastrofy statków", 'subject:"shipwrecks"', {"subject": "Katastrofy morskie"}),
    Category("disasters", "Katastrofy", 'subject:"disasters"', {"subject": "Katastrofy"}),
    Category("espionage", "Szpiegostwo", 'subject:"espionage"', {"subject": "Szpiegostwo"}),
    Category("archaeology", "Archeologia", 'subject:"archaeology"', {"domain": "Archeologia"}),
    Category("ancient", "Starożytność", 'subject:"civilization, ancient"', {"subject": "Starożytność"}),
    Category("medieval", "Średniowiecze", 'subject:"middle ages"', {"subject": "Średniowiecze"}),
    Category("biography", "Biografie i postacie", 'subject:"biography"', {"genre": "Biografia"}),
    Category("science", "Historia nauki", 'subject:"science" subject:"history"', {"subject": "Nauka"}),
    Category("medicine", "Historia medycyny", 'subject:"medicine" subject:"history"',
             {"subject": "Historia medycyny"}),
    Category("inventions", "Wynalazki i technika", 'subject:"inventions"', {"subject": "Wynalazki"}),
    Category("folklore", "Folklor i legendy", 'subject:"folklore"', {"subject": "Folklor"}),
    Category("occult", "Okultyzm i sekty", 'subject:"occultism"', {"subject": "Okultyzm"}),
    Category("coldwar", "Zimna wojna", 'subject:"cold war"', {"subject": "Zimna wojna"}),
    Category("economy", "Pieniądze i gospodarka", 'subject:"economic history"',
             {"subject": "Historia gospodarcza"}),
    Category("poland", "Polska i Europa Środkowa", 'subject:"poland" subject:"history"', {"domain": "Historia"}),
]
CATEGORY_BY_KEY = {c.key: c for c in CATEGORIES}

# Kolejność od najmniej do najbardziej dostępnej w sieci.
AVAILABILITY = {
    "none": {"label": "Brak wersji cyfrowej", "factor": 1.0, "access_hours": 4},
    "unknown": {"label": "Nieznana (sprawdź Polonę)", "factor": 0.85, "access_hours": 4},
    "restricted": {"label": "Zeskanowana, bez dostępu", "factor": 0.8, "access_hours": 3},
    "partial": {"label": "Fragmenty online", "factor": 0.6, "access_hours": 1},
    "borrow": {"label": "Wypożyczenie cyfrowe", "factor": 0.5, "access_hours": 1},
    "full": {"label": "Pełny tekst online", "factor": 0.3, "access_hours": 0},
}
AVAILABILITY_RANK = ["none", "unknown", "restricted", "partial", "borrow", "full"]
