"""Paper Theatre 2.5D: a distinct, explicit, auditable film production format.

The format never claims that one flattened illustration has been segmented.
The editor must supply a clean background and *individual*, transparent PNG
cutouts. Each cutout receives an independent cue; groups are sequential and
the protagonist (if present) is the last, outlined character.
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

from PIL import Image

from .media import asset_path

GROUPS = (
    ("sky", "Niebo · słońce, księżyc, chmury", "hanging_drop"),
    ("landscape", "Krajobraz · góry, doliny", "bottom_rise"),
    ("foundations", "Fundamenty i architektura", "bottom_rise"),
    ("vegetation", "Roślinność · każde drzewo osobno", "rake_lift"),
    ("props", "Rekwizyty i posągi", "rake_lift"),
    ("characters", "Postacie · każda oddzielnie", "rake_lift"),
    ("hero", "Najważniejsza postać · ostatnia", "rake_lift"),
)
GROUP_INDEX = {item[0]: i for i, item in enumerate(GROUPS)}
GROUP_RIG = {item[0]: item[2] for item in GROUPS}
DEFAULT_DURATION = {"sky": .42, "landscape": .45, "foundations": .5,
                    "vegetation": .33, "props": .3, "characters": .32, "hero": .55}
DEFAULT_SETTLE = .14
MAX_CUTOUTS = 500


def _png(store, project, asset_id: str, *, cutout: bool = False) -> dict:
    asset = next((a for a in project.assets if a.id == asset_id), None)
    if not asset or asset.kind != "image" or Path(asset.filename).suffix.lower() != ".png":
        raise ValueError("Każdy element Paper Theatre musi być osobnym plikiem PNG")
    path = asset_path(store, project.id, asset_id, project=project)
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError("Materiał nie jest prawdziwym plikiem PNG")
        size = image.size
        if not cutout:
            return {"asset_id": asset_id, "size": size}
        if image.mode != "RGBA" and "transparency" not in image.info:
            raise ValueError("Wycinek wymaga kanału przezroczystości PNG: " + asset.name)
        alpha = image.convert("RGBA").getchannel("A")
        bounds = alpha.getbbox()
        lo, hi = alpha.getextrema()
        if not bounds or lo == 255 or hi == 0:
            raise ValueError("Wycinek musi mieć widoczne piksele i przezroczyste tło: " + asset.name)
        coverage = round((bounds[2]-bounds[0])*(bounds[3]-bounds[1])/(size[0]*size[1]), 4)
        return {"asset_id": asset_id, "name": asset.name, "size": size, "bounds": bounds,
                "bbox_fraction": coverage}


def plan(store, project, background_id: str, layers: list, *, gap: float = .12,
         group_gap: float = .22, hero_outline_px: int = 8) -> dict:
    """Return a deterministic plan, without editing project state."""
    if not isinstance(background_id, str) or not background_id:
        raise ValueError("Wybierz osobne tło sceny bez postaci i rekwizytów")
    backdrop = _png(store, project, background_id)
    if not isinstance(layers, list) or not 1 <= len(layers) <= MAX_CUTOUTS:
        raise ValueError("Podaj od 1 do 500 osobnych wycinków PNG")
    if any(isinstance(v, bool) or not isinstance(v, (float, int))
           or not math.isfinite(v) or v < 0 or v > 5 for v in (gap, group_gap)):
        raise ValueError("Odstępy muszą wynosić 0–5 sekund")
    if isinstance(hero_outline_px, bool) or not isinstance(hero_outline_px, int) or not 1 <= hero_outline_px <= 24:
        raise ValueError("Obrys bohatera: 1–24 piksele")

    checked, unique = [], {background_id}
    for index, item in enumerate(layers):
        if not isinstance(item, dict) or not set(item) <= {"asset_id", "group", "duration"}:
            raise ValueError("Nieprawidłowa definicja wycinka numer " + str(index + 1))
        aid = item.get("asset_id")
        group = item.get("group")
        if not isinstance(aid, str) or aid in unique:
            raise ValueError("Każdy obiekt ma być osobnym wycinkiem, bez powtórzonych plików")
        if group not in GROUP_INDEX:
            raise ValueError("Nieznana grupa scenografii")
        length = item.get("duration", DEFAULT_DURATION[group])
        if isinstance(length, bool) or not isinstance(length, (int, float)) or not math.isfinite(length) or not .05 <= length <= 10:
            raise ValueError("Czas wejścia wycinka: 0,05–10 sekund")
        info = _png(store, project, aid, cutout=True)
        if tuple(info["size"]) != tuple(backdrop["size"]):
            raise ValueError("PNG muszą mieć dokładnie rozmiar tła (przezroczyste płótno): " + info["name"])
        unique.add(aid)
        checked.append({"asset_id": aid, "group": group, "duration": float(length),
                        "source_order": index, **info})

    counts = Counter(item["group"] for item in checked)
    if counts["hero"] > 1:
        raise ValueError("Najważniejsza postać ma być jedna i wejść ostatnia")
    if counts["characters"] and counts["hero"] != 1:
        raise ValueError("Dodaj jedną najważniejszą postać; wejdzie jako ostatnia")
    checked.sort(key=lambda item: (GROUP_INDEX[item["group"]], item["source_order"]))
    start, previous_group, cues, warnings = .25, None, [], []
    for item in checked:
        group = item["group"]
        if previous_group is not None:
            start += group_gap if previous_group != group else gap
        duration = item["duration"]
        cue = {
            "layer": len(cues) + 1, "group": group,
            "rig": GROUP_RIG[group], "start": round(start, 3),
            "duration": duration, "settle_duration": DEFAULT_SETTLE,
            "depth": round(1 + GROUP_INDEX[group] * .3, 2),
        }
        if group == "sky":
            cue.update(string_visible=True, string_length=.16, swing_deg=1.8,
                       swing_decay=.9, overshoot=.025)
        if group in ("vegetation", "props", "characters", "hero"):
            cue.update(pivot_x=.5, pivot_y=1, start_rotation=82,
                       overshoot_rotation=-5, stick_visible=True, stick_length=.1)
        if group == "hero":
            cue.update(start_rotation=88, duration=duration,
                       outline_px=hero_outline_px, outline_color="#e7c26d")
        if group in ("landscape", "foundations"):
            cue["overshoot"] = .018
        if item["bbox_fraction"] > .42:
            warnings.append(item["name"] + ": rozległy wycinek; sprawdź, czy nie zawiera kilku obiektów")
        cues.append(cue)
        start += duration + DEFAULT_SETTLE
        previous_group = group

    total = round(start + .4, 3)
    return {
        "background_id": background_id,
        "asset_ids": [item["asset_id"] for item in checked],
        "layer_cues": cues, "groups": [item["group"] for item in checked],
        "cutouts": len(checked), "hero_last": bool(counts["hero"]),
        "total_seconds": total, "warnings": warnings,
        "quality": {"individual_assets": True, "alpha_validated": True,
                    "occluded_pixels_reconstructed": False,
                    "reference_match_confirmed": False},
    }
