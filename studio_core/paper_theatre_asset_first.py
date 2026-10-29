"""Asset-first shot planning: describe objects before generating any pixels.

Drafts are explicit objects, never fabricated segmentations of one flattened image.
Paper Theatre is a shot technique independent of a film's genre or production
mode. Only separately verified alpha PNG cutouts may be assembled.
"""
from __future__ import annotations

import json
import math
import re

from .paper_theatre import GROUPS, GROUP_INDEX, MAX_CUTOUTS, plan

MAX_OBJECTS = min(MAX_CUTOUTS, 200)
DEFAULT_STYLE = ("Hand-cut textured rice paper, warm imperial parchment palette, "
                 "muted ink outlines, subtle fiber texture, consistent warm top-left light, "
                 "paper shadow edges. Consistent stylized 2.5D illustration, not photorealistic.")
DEFAULT_BRIEF = "Scena opowieści zbudowana z osobnych papierowych wycinków."


def _number(value, minimum, maximum):
    return type(value) in (int, float) and math.isfinite(value) and minimum <= value <= maximum


def normalize_manifest(data: dict) -> dict:
    """Untrusted assistant/user JSON -> bounded and deterministic object inventory."""
    if not isinstance(data, dict) or not isinstance(data.get("objects"), list):
        raise ValueError("Plan Asset-first wymaga listy objects")
    brief = data.get("brief", DEFAULT_BRIEF)
    style = data.get("style", DEFAULT_STYLE)
    if not isinstance(brief, str) or not brief.strip() or len(brief) > 4000:
        raise ValueError("Opis sceny nie może być pusty ani dłuższy niż 4000 znaków")
    if not isinstance(style, str) or not style.strip() or len(style) > 3000:
        raise ValueError("Styl musi być niepustym krótkim opisem")
    raw = data["objects"]
    if not 1 <= len(raw) <= MAX_OBJECTS:
        raise ValueError("Lista musi zawierać 1–200 indywidualnych obiektów")
    objects, seen = [], set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError("Obiekt musi mieć pola name, group, description i pozycję")
        if set(item) - {"id", "name", "group", "description", "x", "y", "width", "z", "asset_id", "duration", "pivot_x", "pivot_y", "rig"}:
            raise ValueError("Nieznane pole w obiekcie Asset-first")
        ident = item.get("id") or "object_" + str(index + 1).zfill(3)
        name, group = item.get("name"), item.get("group")
        description = item.get("description") or name
        if not isinstance(ident, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", ident) or ident in seen:
            raise ValueError("Każdy obiekt wymaga unikalnego identyfikatora")
        if not isinstance(name, str) or not name.strip() or len(name) > 120:
            raise ValueError("Podaj nazwę każdego obiektu (maks. 120 znaków)")
        if not isinstance(group, str) or group not in GROUP_INDEX:
            raise ValueError("Nieznana grupa obiektu " + name)
        if not isinstance(description, str) or not description.strip() or len(description) > 1000:
            raise ValueError("Opis obiektu jest niepoprawny")
        x, y, width = item.get("x", .5), item.get("y", .8), item.get("width", .18)
        if not _number(x, 0, 1) or not _number(y, 0, 1) or not _number(width, .01, 2):
            raise ValueError("Pozycja i szerokość obiektu wymagają liczb x/y 0–1 oraz width 0,01–2")
        z = item.get("z", GROUP_INDEX[group] * 10)
        if type(z) is not int or not -100 <= z <= 100:
            raise ValueError("Plan głębi z wymaga liczby całkowitej od -100 do 100")
        aid = item.get("asset_id", "")
        if not isinstance(aid, str) or len(aid) > 100:
            raise ValueError("Nieprawidłowy asset_id")
        duration = item.get("duration")
        if duration is not None and not _number(duration, .05, 10):
            raise ValueError("Nieprawidłowy czas wejścia")
        pivot_x, pivot_y = item.get("pivot_x", .5), item.get("pivot_y", 1.0)
        if not _number(pivot_x, 0, 1) or not _number(pivot_y, 0, 1):
            raise ValueError("Punkt obrotu pivot_x/pivot_y musi mieścić się w zakresie 0–1")
        rig = item.get("rig")
        if rig is not None and rig not in ("static", "hanging_drop", "bottom_rise", "rake_lift"):
            raise ValueError("Nieobsługiwany rodzaj wejścia wycinka")
        seen.add(ident)
        obj = {"id": ident, "name": name.strip(), "group": group,
               "description": description.strip(), "x": float(x), "y": float(y),
               "width": float(width), "z": z, "asset_id": aid}
        if duration is not None:
            obj["duration"] = float(duration)
        if "pivot_x" in item: obj["pivot_x"] = float(pivot_x)
        if "pivot_y" in item: obj["pivot_y"] = float(pivot_y)
        if rig is not None: obj["rig"] = rig
        objects.append(obj)

    hero = sum(item["group"] == "hero" for item in objects)
    if hero > 1 or (any(item["group"] == "characters" for item in objects) and hero != 1):
        raise ValueError("Jedna najważniejsza postać musi wejść na końcu po pozostałych")
    # Group order = entrance order; z is strictly visual occlusion, not cue timing.
    objects.sort(key=lambda item: GROUP_INDEX[item["group"]])
    mode = data.get("mode", "asset-first")
    if mode not in ("asset-first", "reference-guided"):
        raise ValueError("Nieznany tryb tworzenia sceny")
    reference_id = data.get("reference_asset_id", "")
    reference_notes = data.get("reference_notes", "")
    reference_approved = data.get("reference_approved", False)
    if not isinstance(reference_approved, bool):
        raise ValueError("Akceptacja obrazu referencyjnego musi być true/false")
    if not isinstance(reference_id, str) or len(reference_id) > 100:
        raise ValueError("Niepoprawne ID obrazu referencyjnego")
    if not isinstance(reference_notes, str) or len(reference_notes) > 3000:
        raise ValueError("Notatki o kompozycji przekraczają limit")
    return {"mode": mode, "brief": brief.strip(), "style": style.strip(), "objects": objects,
            "reference_asset_id": reference_id, "reference_notes": reference_notes.strip(),
            "reference_approved": reference_approved}


def drafting_prompt(brief: str, style: str = DEFAULT_STYLE) -> str:
    """Prompt for the user's connected chat model to propose a validated scene inventory."""
    if not isinstance(brief, str) or not 1 <= len(brief.strip()) <= 4000:
        raise ValueError("Najpierw opisz ujęcie")
    if not isinstance(style, str) or not 1 <= len(style.strip()) <= 3000:
        raise ValueError("Opisz spójny styl scenografii")
    schema = {
        "brief": brief[:160], "style": style[:160],
        "objects": [
            {"id": "cloud_01", "name": "Chmura 1", "group": "sky",
             "description": "Mała papierowa chmura z włóknistą krawędzią",
             "x": .32, "y": .18, "width": .16, "z": 0},
            {"id": "emperor", "name": "Cesarz", "group": "hero",
             "description": "Cesarz w czarno-złotych ceremonialnych szatach",
             "x": .34, "y": .85, "width": .26, "z": 70}
        ]
    }
    return (
        "Zaplanuj PAPER THEATRE 2.5D, produkcja ASSET-FIRST. Zwroc tylko poprawny JSON. "
        "Nie generuj finalnego obrazu ani nie udawaj segmentacji. Wypisz kazdy obiekt "
        "oddzielnie: chmury, ksiezyc, slonce, gory, mury, wieze, drzewa, krzaki, "
        "monety, choragwie, posagi i KAZDA postac oddzielnie (jesli wystepuje). "
        "Przydziel group z listy sky, landscape, foundations, vegetation, props, "
        "characters, hero. Grupa hero maksymalnie jedna, ostatnia, jesli sa postacie. "
        "Dopasuj pozycje x/y (0..1) i szerokosc width wzgledem kadru (0.01..2); "
        "y oznacza dolny srodek wycinka. z (-100..100) steruje PRZYSLANIANIEM, "
        "nie kolejnoscia wejsc. Zero wymyslonych identyfikatorow asset_id: zawsze ''. "
        "Podaj opisy konkretnych osobnych obiektow. Wszystkie utrzymaj w jednym stylu. "
        "Nie pisz Markdown. Limit 200 obiektow. Przyklad schematu: " +
        json.dumps(schema, ensure_ascii=False) +
        "\nOPIS SCENY: " + json.dumps(brief, ensure_ascii=False) +
        "\nWSPOLNY STYL: " + json.dumps(style, ensure_ascii=False)
    )


def image_prompts(manifest: dict) -> list[dict]:
    source = normalize_manifest(manifest)
    style = source["style"]
    notes = source.get("reference_notes", "")
    prompts = []
    for obj in source["objects"]:
        prompts.append({
            "id": obj["id"], "name": obj["name"], "group": obj["group"],
            "asset_id": obj["asset_id"], "reference_asset_id": source.get("reference_asset_id", ""),
            "placement": {
                "x": obj["x"], "y": obj["y"], "width": obj["width"], "z": obj["z"]},
            "prompt": (
                "ONE SINGLE ISOLATED PAPER CUTOUT OBJECT, not a complete scene. "
                + obj["description"] + ". Consistent art direction: " + style + ". "
                "Output a real RGBA PNG with transparent background, no extra objects, "
                "no surrounding scene, no background or text. Keep the entire silhouette "
                "inside the canvas with a narrow alpha margin. Light and texture must "
                "match all other objects in this shot. "
                + ("Match the approved reference composition, costume design, palette and lighting. "
                   "Reference notes: " + notes + ". " if source.get("reference_asset_id") else "")
            )
        })
    return prompts


def assemble_manifest(store, project, background_id: str, manifest: dict,
                      *, gap: float = .12, group_gap: float = .22,
                      hero_outline_px: int = 8) -> dict:
    """Validate all linked PNGs and translate authored layout into real render cues."""
    data = normalize_manifest(manifest)
    if data["mode"] == "reference-guided":
        ref_id = data.get("reference_asset_id")
        if not ref_id or not data["reference_approved"]:
            raise ValueError("Wybierz i zaakceptuj obraz referencyjny przed składaniem sceny")
        if ref_id == background_id or any(obj["asset_id"] == ref_id for obj in data["objects"]):
            raise ValueError("Draft referencyjny nie może być tłem ani osobnym wycinkiem")
        from .paper_theatre import _png
        _png(store, project, ref_id)
    missing = [obj["name"] for obj in data["objects"] if not obj["asset_id"]]
    if missing:
        raise ValueError("Brak wygenerowanych PNG dla: " + ", ".join(missing[:8]))
    layers = [{
        "asset_id": obj["asset_id"], "group": obj["group"],
        **{key: obj[key] for key in ("pivot_x", "pivot_y", "rig") if key in obj},
        "layout_x": obj["x"], "layout_y": obj["y"],
        "layout_width": obj["width"], "z_index": obj["z"],
        **({"duration": obj["duration"]} if "duration" in obj else {}),
    } for obj in data["objects"]]
    result = plan(store, project, background_id, layers,
                  gap=gap, group_gap=group_gap, hero_outline_px=hero_outline_px)
    result["mode"] = "asset-first"
    result["object_ids"] = [obj["id"] for obj in data["objects"]]
    return result
