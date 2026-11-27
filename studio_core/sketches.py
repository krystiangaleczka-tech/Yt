"""Szkice ujęć (``legacy.production_flow.sketches``).

Po zatwierdzeniu tytułu reżyser porównuje kilka całych, różnych podejść do opowieści.
Każdy wariant to scenariusz i lista ujęć (opis, kwestia, długość, opcjonalnie klatka),
przeglądana jak kartkowanie zeszytu. Zatwierdzony wariant zostaje zapisany jako migawka
z podpisem, więc każda późniejsza zmiana jest widoczna jako „zmieniony po zatwierdzeniu”.

Import czyta katalog ``docs/filmy/<film>/szkice/<wariant>/`` z plikiem ``szkic.json``
i klatkami obok; cały import (klatki jako materiały, warianty, wpis w dzienniku) to jedna
zmiana projektu, więc nie zapycha historii cofania.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

from PIL import Image, ImageOps
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .models import Asset
from .production_flow import validated_flow
from .store import Conflict, ProjectStore

DEFAULT_IDS = ("szkic_a", "szkic_b", "szkic_c")
MAX_VARIANTS = 12
MAX_SKETCH_JSON = 2 * 1024 * 1024
MAX_FRAME_BYTES = 40 * 1024 * 1024
FRAME_EXT = {".png", ".jpg", ".jpeg", ".webp"}
FRAME_SIZE = (1920, 1080)
THUMB_SIZE = (640, 360)
SHOT_FIELDS = ("nr", "key", "kadr", "seconds", "description", "line", "mark", "assetId")
SOURCE_PATTERNS = ("docs/filmy/*/szkice/*/szkic.json", "*/szkice/*/szkic.json", "szkice/*/szkic.json")
REPO = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def label(index: int) -> str:
    return "Wariant " + (chr(ord("A") + index) if 0 <= index < 26 else str(index + 1))


def empty_variant(variant_id: str) -> dict:
    return {"id": variant_id, "title": "", "scenario": "", "shots": [], "source": {}}


def normalize(state: object) -> dict:
    """Szkice z wartościami domyślnymi: brak wariantów = trzy puste o stałych id."""
    sketches = copy.deepcopy(state) if isinstance(state, dict) else {}
    sketches.setdefault("version", 1)
    sketches.setdefault("playSeconds", 25)
    if not isinstance(sketches.get("variants"), list) or not sketches["variants"]:
        sketches["variants"] = [empty_variant(i) for i in DEFAULT_IDS]
    if not isinstance(sketches.get("approved"), dict):
        sketches["approved"] = None
    return sketches


def is_empty(variant: dict) -> bool:
    return not str(variant.get("title") or "").strip() and not str(variant.get("scenario") or "").strip() \
        and not variant.get("shots")


def _shot_content(shot: dict) -> dict:
    return {"nr": int(shot.get("nr") or 0), "key": str(shot.get("key") or ""), "kadr": str(shot.get("kadr") or ""),
            "seconds": float(shot.get("seconds") if shot.get("seconds") is not None else 4),
            "description": str(shot.get("description") or ""), "line": str(shot.get("line") or ""),
            "mark": str(shot.get("mark") or ""), "assetId": str(shot.get("assetId") or "")}


def content(variant: dict) -> dict:
    """To, co reżyser zatwierdza: tytuł, scenariusz i ujęcia (bez identyfikatorów i źródła).

    Klient liczy to samo (sketchTypes.ts ``content``), żeby bez zapytania wiedzieć,
    czy wariant zmienił się po zatwierdzeniu.
    """
    return {"title": str(variant.get("title") or ""), "scenario": str(variant.get("scenario") or ""),
            "shots": [_shot_content(s) for s in variant.get("shots") or [] if isinstance(s, dict)]}


def _canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def signature(variant: dict) -> str:
    return hashlib.sha256(_canonical(content(variant)).encode()).hexdigest()


def approval_state(sketches: dict) -> str:
    """none / current / stale (zmieniony po zatwierdzeniu) / missing (wariant usunięty)."""
    approved = sketches.get("approved") if isinstance(sketches, dict) else None
    if not isinstance(approved, dict) or not approved.get("variantId"):
        return "none"
    variant = next((v for v in sketches.get("variants") or [] if v.get("id") == approved["variantId"]), None)
    if variant is None:
        return "missing"
    # Migawka przechodzi przez tę samą normalizację: zapis całego planu z przeglądarki zamienia 6.0 na 6.
    snapshot = approved.get("snapshot") if isinstance(approved.get("snapshot"), dict) else {}
    return "current" if _canonical(content(variant)) == _canonical(content(snapshot)) else "stale"


def _flow(project) -> dict:
    flow = project.legacy.get("production_flow", {})
    return copy.deepcopy(flow) if isinstance(flow, dict) else {}


def summary(flow: dict) -> dict:
    sketches = normalize(flow.get("sketches") if isinstance(flow, dict) else None)
    variants = []
    for index, variant in enumerate(sketches["variants"]):
        shots = [s for s in variant.get("shots") or [] if isinstance(s, dict)]
        variants.append({"id": variant.get("id"), "label": label(index), "title": variant.get("title") or "",
                         "shots": len(shots), "seconds": round(sum(_shot_content(s)["seconds"] for s in shots), 3),
                         "frames": sum(1 for s in shots if s.get("assetId")), "signature": signature(variant)})
    return {"sketches": sketches, "state": approval_state(sketches), "variants": variants}


def issues(flow: dict) -> list[dict]:
    """Uwagi do kontroli ciągłości (reguła „szkic”)."""
    raw = flow.get("sketches") if isinstance(flow, dict) else None
    if not isinstance(raw, dict):
        return []
    sketches = normalize(raw)
    state = approval_state(sketches)
    approved = sketches.get("approved") or {}
    base = {"rule": "szkic", "ref": "", "unit": None}
    if state == "stale":
        return [base | {"severity": 2, "message": f"Zatwierdzony szkic ujęć „{approved.get('title') or approved.get('variantId')}” "
                                                  "zmienił się po zatwierdzeniu.",
                        "hint": "Zatwierdź go ponownie w Szkicach ujęć albo cofnij zmianę."}]
    if state == "missing":
        return [base | {"severity": 2, "message": "Zatwierdzony szkic ujęć został usunięty.",
                        "hint": "Wybierz i zatwierdź szkic w Szkicach ujęć."}]
    if state == "none" and any(not is_empty(v) for v in sketches["variants"]):
        return [base | {"severity": 1, "message": "Szkice ujęć są wypełnione, ale żaden nie jest zatwierdzony.",
                        "hint": "Obejrzyj przeglądy i zatwierdź jeden szkic, zanim powstanie rozpiska."}]
    return []


def approved_brief(flow: dict) -> dict | None:
    """Zatwierdzony szkic dla AI: kierunek reżysera (migawka z chwili zatwierdzenia)."""
    raw = flow.get("sketches") if isinstance(flow, dict) else None
    if not isinstance(raw, dict) or not isinstance(raw.get("approved"), dict):
        return None
    approved = raw["approved"]
    snapshot = approved.get("snapshot") if isinstance(approved.get("snapshot"), dict) else {}
    shots = [s for s in snapshot.get("shots") or [] if isinstance(s, dict)][:400]
    return {"title": str(snapshot.get("title") or approved.get("title") or ""),
            "scenario": str(snapshot.get("scenario") or "")[:20000],
            "note": str(approved.get("note") or "")[:2000],
            "stale": approval_state(normalize(raw)) != "current",
            "shots": [{"nr": s.get("nr"), "seconds": s.get("seconds"), "kadr": str(s.get("kadr") or "")[:100],
                       "description": str(s.get("description") or "")[:400], "line": str(s.get("line") or "")[:400],
                       "mark": str(s.get("mark") or "")[:100]} for s in shots]}


def _log(flow: dict, who: str, summary_text: str, details: str = "", files: list[str] | None = None) -> None:
    log = flow.setdefault("log", [])
    log.append({"id": uuid.uuid4().hex[:12], "at": _now(), "who": who[:200], "unit": None, "kind": "szkic",
                "summary": summary_text[:2000], "details": details[:20000], "files": [str(f)[:300] for f in (files or [])][:100]})
    del log[:-5000]


def _duration(seconds: float) -> str:
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def approve(flow: dict, variant_id: str, who: str = "", note: str = "") -> dict:
    """Zatwierdza wariant: migawka treści + podpis + wpis w dzienniku. Zmienia ``flow`` w miejscu."""
    sketches = normalize(flow.get("sketches"))
    variant = next((v for v in sketches["variants"] if v.get("id") == variant_id), None)
    if variant is None:
        raise ValueError("Nie ma takiego wariantu szkicu")
    if is_empty(variant):
        raise ValueError("Pusty wariant: wklej scenariusz albo dodaj ujęcia, zanim go zatwierdzisz")
    snapshot = content(variant)
    who = (who or "reżyser").strip()[:200]
    title = snapshot["title"] or label(sketches["variants"].index(variant))
    sketches["approved"] = {"variantId": variant_id, "title": title, "at": _now(), "who": who,
                            "note": str(note or "")[:4000], "signature": signature(variant), "snapshot": snapshot}
    flow["sketches"] = sketches
    seconds = sum(s["seconds"] for s in snapshot["shots"])
    source = variant.get("source") or {}
    details = [f"Ujęć: {len(snapshot['shots'])}, długość filmu {_duration(seconds)}."]
    if source.get("path"):
        details.append(f"Źródło: {source['path']}")
    if note:
        details.append(f"Uwagi: {note}")
    _log(flow, who, f"Zatwierdzony szkic ujęć: {title}", "\n".join(details),
         [source["path"]] if source.get("path") else [])
    return sketches["approved"]


def withdraw(flow: dict, who: str = "") -> None:
    sketches = normalize(flow.get("sketches"))
    previous = sketches.get("approved") or {}
    if not previous:
        raise ValueError("Żaden szkic nie jest zatwierdzony")
    sketches["approved"] = None
    flow["sketches"] = sketches
    _log(flow, (who or "reżyser").strip(), f"Cofnięte zatwierdzenie szkicu ujęć: {previous.get('title') or previous.get('variantId')}")


def replace_editable(flow: dict, incoming: object) -> None:
    """Zapis edycji z interfejsu: warianty i czas przeglądu. ``approved`` zawsze z zapisanego stanu."""
    if not isinstance(incoming, dict):
        raise ValueError("Wymagane pole: sketches")
    current = normalize(flow.get("sketches"))
    variants = incoming.get("variants")
    if not isinstance(variants, list):
        raise ValueError("Szkice wymagają listy wariantów")
    current["variants"] = variants
    if "playSeconds" in incoming:
        current["playSeconds"] = incoming["playSeconds"]
    flow["sketches"] = current


# ---------------------------------------------------------------- import z plików

class _FileShot(BaseModel):
    model_config = ConfigDict(extra="allow", allow_inf_nan=False)
    nr: int | str | None = None
    klucz: str = Field(default="", max_length=200)
    kadr: str = Field(default="", max_length=300)
    sekundy: float = Field(default=4, ge=0.1, le=600)
    opis: str = Field(default="", max_length=4000)
    kwestia: str = Field(default="", max_length=4000)
    znacznik: str = Field(default="", max_length=200)
    klatka: str = Field(default="", max_length=500)

    @field_validator("klucz", "kadr", "opis", "kwestia", "znacznik", "klatka", mode="before")
    @classmethod
    def _text(cls, value):
        return "" if value is None else value

    @field_validator("sekundy", mode="before")
    @classmethod
    def _seconds(cls, value):
        return 4 if value is None or value == "" else value


class _SketchFile(BaseModel):
    model_config = ConfigDict(extra="allow", allow_inf_nan=False)
    film: str = Field(default="", max_length=200)
    wariant: str = Field(default="", max_length=200)
    tytul: str = Field(default="", max_length=300)
    scenariusz: str = Field(default="", max_length=120_000)
    ujecia: list[_FileShot] = Field(default_factory=list, max_length=600)


def _number(value, previous: int) -> int:
    if isinstance(value, bool):
        value = None
    if isinstance(value, int):
        return max(0, min(9999, value))
    match = re.search(r"\d+", str(value)) if value is not None else None
    return min(9999, int(match.group())) if match else previous + 1


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return value[:40] or "wariant"


def read_sketch(directory: Path) -> tuple[_SketchFile, Path]:
    path = directory / "szkic.json"
    if not path.is_file():
        raise ValueError(f"Brak pliku szkic.json w {_display(directory)}")
    if path.stat().st_size > MAX_SKETCH_JSON:
        raise ValueError(f"{_display(path)} przekracza 2 MB")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return _SketchFile.model_validate(data), path
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{_display(path)}: niepoprawny JSON ({error})") from None
    except ValidationError as error:
        first = error.errors()[0]
        where = ".".join(str(x) for x in first.get("loc", ()))
        raise ValueError(f"{_display(path)}: {where} — {first.get('msg')}") from None


def _frame(store: ProjectStore, project_id: str, directory: Path, relative: str, provenance: dict,
           known: dict[str, Asset]) -> tuple[Asset | None, str]:
    """Przygotowuje klatkę jako materiał (plik w media/, bez zmiany projektu). Zwraca (asset, ostrzeżenie)."""
    where = f"{provenance['wariant']} #{provenance['nr']}"
    candidate = (directory / relative).resolve()
    if not candidate.is_relative_to(directory.resolve()):
        return None, f"{where}: klatka „{relative}” leży poza katalogiem wariantu — pominięta, będzie karta"
    if candidate.suffix.lower() not in FRAME_EXT:
        return None, f"{where}: klatka „{relative}” musi być PNG, JPG albo WEBP — będzie karta"
    if not candidate.is_file():
        return None, f"{where}: brak pliku klatki „{relative}” — będzie karta"
    if candidate.stat().st_size > MAX_FRAME_BYTES:
        return None, f"{where}: klatka „{relative}” przekracza 40 MB — będzie karta"
    with candidate.open("rb") as stream:
        source_digest = hashlib.file_digest(stream, "sha256").hexdigest()
    asset_id = "asset_" + hashlib.sha256(
        (source_digest + json.dumps(provenance, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()[:20]
    folder = store.folder(project_id) / "media"
    if asset_id in known and (folder / known[asset_id].filename).is_file():
        return known[asset_id], ""
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / (asset_id + ".jpg")
    temporary = folder / (asset_id + ".jpg.part")
    try:
        with Image.open(candidate) as image:
            image.verify()
        with Image.open(candidate) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                rgba = image.convert("RGBA")
                flat = Image.new("RGB", rgba.size, (255, 255, 255))
                flat.paste(rgba, mask=rgba.getchannel("A"))
                image = flat
            else:
                image = image.convert("RGB")
            image.thumbnail(FRAME_SIZE)
            width, height = image.size
            image.save(temporary, "JPEG", quality=90)
            thumb = image.copy()
            thumb.thumbnail(THUMB_SIZE)
            thumb.save(folder / (asset_id + ".thumb.jpg"), "JPEG", quality=85)
        os.replace(temporary, destination)
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        temporary.unlink(missing_ok=True)
        return None, f"{where}: nie da się odczytać obrazu „{relative}” ({type(error).__name__}) — będzie karta"
    with destination.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    asset = Asset(id=asset_id, name=f"{provenance['wariant']}-{provenance['nr']:03d}-{candidate.name}"[:200], kind="image",
                  filename=destination.name, mime="image/jpeg", sha256=digest, width=width, height=height,
                  thumbnail=asset_id + ".thumb.jpg", provenance=provenance | {"source_sha256": source_digest})
    known[asset_id] = asset
    return asset, ""


def _variant_dirs(directory: Path) -> list[Path]:
    if directory.is_file() and directory.name == "szkic.json":
        directory = directory.parent
    if not directory.is_dir():
        raise ValueError(f"Nie ma katalogu {_display(directory)}")
    if (directory / "szkic.json").is_file():
        return [directory]
    found = sorted(p for p in directory.iterdir() if p.is_dir() and (p / "szkic.json").is_file())
    if not found:
        raise ValueError(f"W {_display(directory)} nie ma szkic.json ani podkatalogów ze szkicami")
    if len(found) > MAX_VARIANTS:
        raise ValueError(f"Za dużo wariantów w jednym imporcie (maks. {MAX_VARIANTS})")
    return found


def _prepare(store: ProjectStore, project_id: str, directory: Path, known: dict[str, Asset]) -> tuple[dict, list[Asset], list[str]]:
    sketch, path = read_sketch(directory)
    wariant = sketch.wariant.strip() or directory.name
    film = sketch.film.strip() or (directory.parent.parent.name if directory.parent.name == "szkice" else directory.parent.name)
    shots, assets, warnings, previous = [], [], [], 0
    for shot in sketch.ujecia:
        nr = _number(shot.nr, previous)
        previous = nr
        asset = None
        if shot.klatka.strip():
            provenance = {"kind": "sketch-frame", "film": film, "wariant": wariant, "nr": nr, "file": shot.klatka.strip()}
            asset, warning = _frame(store, project_id, directory, shot.klatka.strip(), provenance, known)
            if warning:
                warnings.append(warning)
            if asset:
                assets.append(asset)
        shots.append({"nr": nr, "key": shot.klucz, "kadr": shot.kadr, "seconds": shot.sekundy, "description": shot.opis,
                      "line": shot.kwestia, "mark": shot.znacznik, "assetId": asset.id if asset else ""})
    frames = sum(1 for s in shots if s["assetId"])
    variant = {"title": sketch.tytul, "scenario": sketch.scenariusz, "shots": shots,
               "source": {"film": film, "wariant": wariant, "path": _display(path.parent), "importedAt": _now(),
                          "frames": frames, "missing": sum(1 for s in sketch.ujecia if s.klatka.strip()) - frames}}
    return variant, assets, warnings


def place(sketches: dict, imported: dict) -> str:
    """Wstawia zaimportowany wariant: ten sam film+wariant → podmiana; inaczej pierwszy pusty; inaczej nowy."""
    variants = sketches["variants"]
    source = imported["source"]
    target = next((v for v in variants if isinstance(v.get("source"), dict)
                   and v["source"].get("film") == source["film"] and v["source"].get("wariant") == source["wariant"]), None)
    if target is None:
        target = next((v for v in variants if is_empty(v)), None)
    if target is None:
        if len(variants) >= MAX_VARIANTS:
            raise ValueError(f"Projekt ma już {MAX_VARIANTS} wariantów szkicu — usuń któryś przed importem")
        taken = {v.get("id") for v in variants}
        base = "szkic_" + _slug(source["wariant"])
        variant_id, n = base, 2
        while variant_id in taken:
            variant_id, n = f"{base}_{n}", n + 1
        target = {"id": variant_id}
        variants.append(target)
    variant_id = target["id"]
    target.clear()
    target.update({"id": variant_id, **imported,
                   "shots": [{"id": f"{variant_id}-{i:03d}", **shot} for i, shot in enumerate(imported["shots"], 1)]})
    return variant_id


def import_dirs(store: ProjectStore, project_id: str, directory: Path, revision: int | None = None,
                who: str = "import") -> dict:
    """Wczytuje katalog wariantu albo katalog ``szkice/`` z wariantami. Jedna zmiana projektu."""
    directory = Path(directory).resolve()
    dirs = _variant_dirs(directory)
    project = store.get(project_id)
    known = {a.id: a for a in project.assets}
    prepared, warnings = [], []
    for variant_dir in dirs:
        variant, assets, notes = _prepare(store, project_id, variant_dir, known)
        prepared.append((variant, assets))
        warnings += notes
    new_assets = {a.id: a for _, assets in prepared for a in assets}
    attempts = 3 if revision is None else 1
    for attempt in range(attempts):
        current = store.get(project_id).revision if revision is None else revision
        placed = []

        def change(p):
            present = {a.id for a in p.assets}
            p.assets.extend(a.model_copy(deep=True) for a in new_assets.values() if a.id not in present)
            flow = _flow(p)
            sketches = normalize(flow.get("sketches"))
            for variant, _ in prepared:
                placed.append({"variantId": place(sketches, copy.deepcopy(variant)), "title": variant["title"],
                               "shots": len(variant["shots"]), "frames": variant["source"]["frames"],
                               "missing": variant["source"]["missing"], "path": variant["source"]["path"]})
            flow["sketches"] = sketches
            titles = ", ".join(f"„{x['title'] or x['variantId']}”" for x in placed)
            details = "\n".join(f"{x['variantId']}: {x['shots']} ujęć, {x['frames']} klatek"
                                + (f", {x['missing']} bez obrazu (karty)" if x["missing"] else "") for x in placed)
            if warnings:
                details += "\nOstrzeżenia:\n" + "\n".join(warnings[:50])
            _log(flow, who, f"Import szkiców ujęć: {titles}", details, [x["path"] for x in placed])
            p.legacy = {**p.legacy, "production_flow": validated_flow(flow)}

        try:
            result = store.mutate(project_id, current, change)
        except Conflict:
            if attempt + 1 >= attempts:
                raise
            continue
        return {"project": result, "imported": placed, "warnings": warnings}
    raise Conflict("Projekt zmieniał się podczas importu szkiców")


def roots(extra: str | None = None) -> list[Path]:
    """Korzenie, z których wolno importować: repozytorium + DOCOS_SKETCH_ROOTS."""
    values = [REPO] + [Path(x) for x in (extra if extra is not None else os.environ.get("DOCOS_SKETCH_ROOTS", "")).split(os.pathsep) if x.strip()]
    result = []
    for value in values:
        resolved = value.expanduser().resolve()
        if resolved not in result:
            result.append(resolved)
    return result


def resolve_inside(path: str, allowed: list[Path]) -> Path:
    raw = Path(str(path or "").strip())
    if not str(raw) or str(raw) == ".":
        raise ValueError("Podaj katalog szkiców")
    candidate = (raw if raw.is_absolute() else REPO / raw).resolve()
    if not any(candidate.is_relative_to(root) for root in allowed):
        raise ValueError("Szkice można wczytać tylko z katalogów projektu (repozytorium albo DOCOS_SKETCH_ROOTS)")
    return candidate


def find_sources(allowed: list[Path]) -> list[dict]:
    seen, result = set(), []
    for root in allowed:
        for pattern in SOURCE_PATTERNS:
            for path in sorted(root.glob(pattern)):
                resolved = path.resolve()
                if resolved in seen or not path.is_file():
                    continue
                seen.add(resolved)
                item = {"path": _display(path.parent) if path.parent.is_relative_to(REPO) else str(path.parent),
                        "film": path.parent.parent.parent.name, "wariant": path.parent.name}
                try:
                    sketch, _ = read_sketch(path.parent)
                    item |= {"film": sketch.film or item["film"], "wariant": sketch.wariant or item["wariant"],
                             "tytul": sketch.tytul, "shots": len(sketch.ujecia),
                             "frames": sum(1 for s in sketch.ujecia if s.klatka.strip())}
                except ValueError as error:
                    item["error"] = str(error)[:300]
                result.append(item)
    return result[:200]
