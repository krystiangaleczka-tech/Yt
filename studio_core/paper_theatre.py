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
from .paper_theatre_quality import alpha_diagnostics, layout_warnings

GROUPS = (
    ("sky", "Niebo · słońce, księżyc, chmury", "hanging_drop"),
    ("landscape", "Krajobraz · góry, doliny", "hanging_drop"),
    ("foundations", "Fundamenty i architektura", "hanging_drop"),
    ("vegetation", "Roślinność · każde drzewo osobno", "hanging_drop"),
    ("props", "Rekwizyty i posągi", "hanging_drop"),
    ("characters", "Postacie · każda oddzielnie", "rake_lift"),
    ("hero", "Najważniejsza postać · ostatnia", "rake_lift"),
)
GROUP_INDEX = {item[0]: i for i, item in enumerate(GROUPS)}
GROUP_RIG = {item[0]: item[2] for item in GROUPS}
DEFAULT_DURATION = {"sky": .6, "landscape": .64, "foundations": .68,
                    "vegetation": .56, "props": .55, "characters": .68, "hero": .95}
DEFAULT_SETTLE = .22
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
                "bbox_fraction": coverage, "alpha_diagnostics": alpha_diagnostics(image)}


def plan(store, project, background_id: str, layers: list, *, gap: float = .12,
         group_gap: float = .22, hero_outline_px: int = 16) -> dict:
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
        layout_keys = {"layout_x", "layout_y", "layout_width", "z_index"}
        if not isinstance(item, dict) or not set(item) <= {"asset_id", "group", "duration", "pivot_x", "pivot_y", "rig"} | layout_keys:
            raise ValueError("Nieprawidłowa definicja wycinka numer " + str(index + 1))
        has_layout = any(key in item for key in layout_keys)
        if has_layout:
            if not all(key in item for key in ("layout_x", "layout_y", "layout_width")):
                raise ValueError("Layout Asset-first wymaga x, y i width")
            for key, low, high in (("layout_x", 0, 1), ("layout_y", 0, 1), ("layout_width", .01, 2)):
                v = item[key]
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not low <= v <= high:
                    raise ValueError("Niepoprawne współrzędne / skala wycinka: " + key)
            z = item.get("z_index", GROUP_INDEX.get(item.get("group"), 0) * 10)
            if type(z) is not int or not -100 <= z <= 100:
                raise ValueError("Głębokość z musi być liczbą całkowitą od -100 do 100")
        for key in ("pivot_x", "pivot_y"):
            if key in item and (isinstance(item[key], bool) or
                    not isinstance(item[key], (int, float)) or
                    not math.isfinite(item[key]) or not 0 <= item[key] <= 1):
                raise ValueError("Niepoprawny punkt zakotwiczenia: " + key)
        if "rig" in item and item["rig"] not in ("static", "hanging_drop", "bottom_rise", "rake_lift"):
            raise ValueError("Nieobsługiwana mechanika wejścia obiektu")
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
        if not has_layout and tuple(info["size"]) != tuple(backdrop["size"]):
            raise ValueError("PNG muszą mieć dokładnie rozmiar tła (przezroczyste płótno): " + info["name"])
        unique.add(aid)
        checked.append({"asset_id": aid, "group": group, "duration": float(length),
                        "source_order": index, "layout": {k: item[k] for k in layout_keys if k in item},
                        **{key: item[key] for key in ("rig", "pivot_x", "pivot_y") if key in item},
                        **info})

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
            "rig": item["rig"] if "rig" in item else GROUP_RIG[group], "start": round(start, 3),
            "duration": duration, "settle_duration": DEFAULT_SETTLE,
            "depth": round(1 + GROUP_INDEX[group] * .3, 2),
        }
        if cue["rig"] == "hanging_drop":
            cue.update(string_visible=True, swing_deg=3.2,
                       swing_decay=1.1, overshoot=.025)
        if cue["rig"] == "rake_lift":
            cue.update(pivot_x=.5, pivot_y=1, start_rotation=82,
                       overshoot_rotation=-5, stick_visible=True, stick_length=.1)
        if group in ("characters", "hero"):
            # Silhouettes must remain readable against busy architecture.
            cue.update(outline_px=max(6, round(hero_outline_px * .75)),
                       outline_color="#362820")
        if group == "hero":
            cue.update(start_rotation=88, duration=duration,
                       outline_px=hero_outline_px, outline_color="#362820")
        if cue["rig"] == "bottom_rise":
            cue["overshoot"] = .018
        if item["layout"]:
            cue.update(item["layout"])
        for key in ("pivot_x", "pivot_y"):
            if key in item:
                cue[key] = float(item[key])
        if item["bbox_fraction"] > .42 and not item["layout"]:
            warnings.append(item["name"] + ": rozległy wycinek; sprawdź, czy nie zawiera kilku obiektów")
        if item["alpha_diagnostics"]["regions"] > 1:
            warnings.append(item["name"] +
                ": kilka rozłącznych części alpha; upewnij się, że to jeden obiekt")
        cues.append(cue)
        start += duration + DEFAULT_SETTLE
        previous_group = group
    warnings.extend(layout_warnings(checked, tuple(backdrop["size"])))

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
