"""Paczki dla Claude (subskrypcja, bez API): prompt do wklejenia i import odpowiedzi JSON."""
from __future__ import annotations

import json
import re

from .config import AVAILABILITY

RISK_FLAGS = {"controversial", "graphic_violence", "legal", "medical_misinfo", "demonetization", "copyright", "none"}

# pole: (typ, min, max) — liczby są przycinane do zakresu, teksty i listy skracane
FIELDS = {
    "interest": ("int", 0, 100),
    "confidence": ("int", 0, 100),
    "hook": ("str", 0, 300),
    "video_title": ("str", 0, 80),
    "youtube_query": ("str", 0, 80),
    "wikipedia_article": ("str?", 0, 120),
    "central_question": ("str", 0, 300),
    "interesting_points": ("list", 0, 6),
    "layers": ("list", 0, 5),
    "research_leads": ("list", 0, 6),
    "difficulty": ("int", 1, 10),
    "difficulty_reasons": ("str", 0, 400),
    "visuals": ("int", 1, 10),
    "research_hours": ("num", 1, 200),
    "evergreen": ("int", 0, 100),
    "series_potential": ("int", 0, 100),
    "en_translation": ("bool?", 0, 0),
    "risk_flags": ("list", 0, 6),
    "shorts_ideas": ("list", 0, 3),
}
REQUIRED = ("interest", "video_title", "youtube_query", "difficulty")

INSTRUCTIONS = """Jesteś researcherem anglojęzycznego kanału YouTube z dokumentami faceless (~{minutes} min, \
narracja + materiały archiwalne). Poniżej {n} książek wylosowanych z katalogów bibliotek. Oceń każdą jako \
źródło na film.

Zasady:
- Jeśli znasz książkę, opieraj się na jej treści. Jeśli nie — oceniaj po tytule, autorze, roku, tematach, \
opisie i spisie treści, i obniż `confidence`.
- Nie zmyślaj faktów. `interesting_points` to wątki do sprawdzenia w książce, nie pewniki.
- `interest` mierzy, czy z książki da się zrobić film, który kliknie szeroka anglojęzyczna widownia \
(tajemnica, konflikt, ludzki dramat, zaskakujący zwrot, mało znana historia). Kotwice: 90+ hit z oczywistą \
historią; 70 mocny temat niszowy; 50 przeciętny; 30 sucha literatura fachowa; 10 katalog/podręcznik/poradnik.
- `difficulty` 1–10: dostęp do źródła (patrz „availability”), język, stary druk, złożoność, ilość researchu, \
brak materiałów wizualnych.
- `visuals` 1–10: ile materiałów archiwalnych, map, zdjęć z domeny publicznej da się realnie zdobyć.
- `youtube_query`: 2–6 słów po angielsku, jak widz szukałby tego tematu (do sprawdzenia konkurencji).
- `wikipedia_article`: dokładny tytuł najbliższego artykułu angielskiej Wikipedii albo null.
- Teksty dla widza (`hook`, `video_title` ≤ 60 znaków, `central_question`, `shorts_ideas`) po angielsku; \
uzasadnienia i wątki (`interesting_points`, `difficulty_reasons`, `layers`) po polsku.
- `en_translation`: dla książek nie po angielsku — czy istnieje angielskie wydanie (true/false), \
dla angielskich null.
- `risk_flags`: podzbiór [controversial, graphic_violence, legal, medical_misinfo, demonetization, copyright] \
albo ["none"].

Zwróć WYŁĄCZNIE tablicę JSON (bez komentarzy i tekstu dookoła), jeden obiekt na książkę, z polami:
{schema}

KSIĄŻKI:
{books}
"""

SCHEMA_EXAMPLE = {
    "id": "id dokładnie jak w danych",
    "interest": 0, "confidence": 0,
    "hook": "", "video_title": "", "youtube_query": "", "wikipedia_article": None,
    "central_question": "", "interesting_points": ["", "", ""], "layers": ["", "", ""],
    "research_leads": ["", ""], "difficulty": 1, "difficulty_reasons": "", "visuals": 1,
    "research_hours": 10, "evergreen": 0, "series_potential": 0, "en_translation": None,
    "risk_flags": ["none"], "shorts_ideas": [""],
}


def book_payload(book: dict) -> dict:
    return {
        "id": book["id"],
        "title": book["title"],
        "author": book.get("author") or None,
        "year": book.get("year"),
        "language": book.get("language"),
        "subjects": (book.get("subjects") or [])[:12],
        "description": (book.get("description") or "")[:700] or None,
        "toc": (book.get("toc") or [])[:25] or None,
        "availability": AVAILABILITY.get(book.get("availability") or "unknown", {}).get("label"),
    }


def build_prompt(books: list[dict], settings: dict) -> str:
    return INSTRUCTIONS.format(
        minutes=settings.get("video_minutes", 15), n=len(books),
        schema=json.dumps(SCHEMA_EXAMPLE, ensure_ascii=False),
        books=json.dumps([book_payload(b) for b in books], ensure_ascii=False, indent=1),
    )


def extract_json(text: str):
    """Wyciąga tablicę JSON z odpowiedzi — także z bloku ```json albo z tekstem dookoła."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("["), text.rfind("]")
        if start == -1 or end <= start:
            raise ValueError("Nie znalazłem tablicy JSON w odpowiedzi.")
        try:
            data = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"Niepoprawny JSON: {exc.msg} (linia {exc.lineno}).") from exc
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [data])
    if not isinstance(data, list):
        raise ValueError("Odpowiedź musi być tablicą obiektów JSON.")
    return data


def clean_rating(raw: dict) -> tuple[dict, list[str]]:
    """Normalizuje jedną ocenę; zwraca (ocena, ostrzeżenia)."""
    out, warnings = {}, []
    for name, (kind, lo, hi) in FIELDS.items():
        value = raw.get(name)
        if value is None:
            out[name] = None
            continue
        try:
            if kind in ("int", "num"):
                num = min(max(float(value), lo), hi)
                out[name] = int(round(num)) if kind == "int" else round(num, 1)
            elif kind in ("str", "str?"):
                text = str(value).strip()
                out[name] = text[:hi] if text and text.lower() != "null" else None
            elif kind == "list":
                items = value if isinstance(value, list) else [value]
                out[name] = [str(v).strip() for v in items if str(v).strip()][:hi]
            elif kind == "bool?":
                out[name] = value if isinstance(value, bool) else str(value).lower() in ("true", "yes", "tak")
        except (TypeError, ValueError):
            out[name] = None
            warnings.append(f"pole {name} ma złą wartość: {value!r}")
    if out.get("risk_flags"):
        out["risk_flags"] = [f for f in (x.lower() for x in out["risk_flags"]) if f in RISK_FLAGS] or ["none"]
    missing = [f for f in REQUIRED if out.get(f) in (None, "")]
    if missing:
        warnings.append("brak pól: " + ", ".join(missing))
    return out, warnings


def parse_response(text: str, expected_ids: list[str] | None = None) -> dict:
    """Zwraca {"ratings": {id: ocena}, "errors": [...], "warnings": [...]}."""
    result = {"ratings": {}, "errors": [], "warnings": []}
    try:
        items = extract_json(text)
    except ValueError as exc:
        result["errors"].append(str(exc))
        return result
    expected = set(expected_ids or [])
    failed = set()
    for i, raw in enumerate(items, 1):
        if not isinstance(raw, dict) or not raw.get("id"):
            result["errors"].append(f"Obiekt nr {i} nie ma pola id.")
            continue
        book_id = str(raw["id"]).strip()
        if expected and book_id not in expected:
            result["errors"].append(f"Nieznane id: {book_id}")
            continue
        rating, warnings = clean_rating(raw)
        if any(w.startswith("brak pól") for w in warnings):
            result["errors"].append(f"{book_id}: {'; '.join(warnings)}")
            failed.add(book_id)
            continue
        result["warnings"] += [f"{book_id}: {w}" for w in warnings]
        result["ratings"][book_id] = rating
    if expected:
        missing = expected - set(result["ratings"]) - failed
        if missing:
            result["warnings"].append(f"Brak ocen dla {len(missing)} książek — zostają w kolejce.")
    return result


FILE_HEADER = """<!-- Book Scout — paczka {batch_id}
Tryb Claude Code: przeczytaj ten plik, oceń książki zgodnie z instrukcją poniżej
i zapisz samą tablicę JSON do pliku: {response_name}
Następnie w Book Scout kliknij „Importuj z plików”. -->

"""


def response_name(batch_id: str) -> str:
    return f"{batch_id}.response.json"


def file_prompt(batch_id: str, prompt: str) -> str:
    return FILE_HEADER.format(batch_id=batch_id, response_name=response_name(batch_id)) + prompt
