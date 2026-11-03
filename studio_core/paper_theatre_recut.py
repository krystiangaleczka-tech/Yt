"""Re-cut an existing Paper Theatre scene into clean per-object cutouts.

The heavy work (MobileSAM contours, LaMa for hidden scenery, plain paper
backdrop) runs in ``studio_workers/cutout_worker.py`` inside the separate
image-model environment. This module only prepares prompts, validates user
settings, imports results as *new* assets and swaps them in on explicit
acceptance. Nothing is overwritten: the previous assets and cues are kept and
can be restored.

Production rules (owner's guidelines): one object = one PNG along its real
contour; the film starts from plain paper; nothing is blurred or invented
under characters (an empty hole shows paper until the character arrives);
hidden parts are completed only for scenery covered by later scenery.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from .media import asset_path, import_media
from .paper_theatre import DEFAULT_DURATION, GROUP_RIG, GROUP_INDEX

KEY = "paper_theatre_recut"
LEFTOVER_MODES = ("layers", "merge", "paper")
MAX_POINTS = 12
MAX_PARTS = 8
MAX_EXTRA_BOXES = 6
MAX_EXTRA_OBJECTS = 40
MAX_STROKES = 60


def scene_of(project, sid):
    scene = next((s for s in project.scenes if s.id == sid and s.template == "paper-theatre"), None)
    if scene is None:
        raise ValueError("Wybierz ujęcie Paper Theatre")
    if not scene.asset_id or not scene.asset_ids:
        raise ValueError("Ujęcie nie ma jeszcze tła i wycinków do ponownego rozcięcia")
    return scene


def layer_groups(scene) -> dict[str, str]:
    cues = {c.get("layer"): c for c in scene.parameters.get("layer_cues", []) if isinstance(c, dict)}
    return {aid: cues.get(i + 1, {}).get("group", "props") for i, aid in enumerate(scene.asset_ids)}


def frame_size(store, project, scene) -> tuple[int, int]:
    with Image.open(asset_path(store, project.id, scene.asset_id, project=project)) as im:
        return im.size


# -------------------------------------------------------------- prompts ---
def auto_prompt(path: Path, group: str) -> dict:
    """Box = opaque bounds of the current cutout, point = its deepest interior pixel.
    Characters get one prompt per point later in the worker (multi-point MobileSAM
    prompts on people are unreliable)."""
    with Image.open(path) as image:
        alpha = image.convert("RGBA").getchannel("A")
    box = alpha.getbbox()
    if box is None:
        return {"box": [0, 0, alpha.width, alpha.height], "pos": [], "neg": [], "hull": "auto", "auto": True}
    x0, y0, x1, y1 = box
    crop = alpha.crop(box).point(lambda v: 255 if v >= 128 else 0)
    scale = min(1.0, 160 / max(crop.size))
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.Resampling.NEAREST)
    # 1 px transparent frame so erosion also eats from the crop edges
    current = ImageOps.expand(small, border=1, fill=0)
    for _ in range(200):  # erode until the next step would erase everything: deepest region remains
        nxt = current.filter(ImageFilter.MinFilter(3))
        if nxt.getbbox() is None:
            break
        current = nxt
    arr = np.array(current)[1:-1, 1:-1]
    ys, xs = np.nonzero(arr)
    if len(xs):
        cx, cy = xs.mean(), ys.mean()
        k = int(np.argmin((xs - cx) ** 2 + (ys - cy) ** 2))
        px, py = x0 + (xs[k] + .5) / scale, y0 + (ys[k] + .5) / scale
    else:
        px, py = (x0 + x1) / 2, (y0 + y1) / 2
    hull = "circle" if _round(alpha.crop(box)) and group == "sky" else "auto"
    return {"box": [x0, y0, x1, y1], "pos": [[round(px), round(py)]], "neg": [], "hull": hull, "auto": True}


def _round(alpha: Image.Image) -> bool:
    """A big, nearly circular opaque shape (sun/moon) gets a full-disc completion."""
    a = np.array(alpha) >= 128
    h, w = a.shape
    if min(h, w) < 40 or not .8 < w / h < 1.25:
        return False
    yy, xx = np.mgrid[:h, :w]
    disc = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2 <= 1
    return (a & disc).sum() / max(1, disc.sum()) > .85 and (a & ~disc).sum() / max(1, a.sum()) < .08


def _num(v, lo, hi):
    return type(v) in (int, float) and math.isfinite(v) and lo <= v <= hi


def _points(values, w, h, limit=MAX_POINTS):
    if values is None:
        return []
    if not isinstance(values, list) or len(values) > limit:
        raise ValueError(f"Maksymalnie {limit} punktów na obiekt")
    out = []
    for p in values:
        if not isinstance(p, list) or len(p) != 2 or not _num(p[0], 0, w) or not _num(p[1], 0, h):
            raise ValueError("Punkt musi mieć współrzędne [x, y] w kadrze")
        out.append([round(p[0]), round(p[1])])
    return out


def _box(value, w, h):
    if not isinstance(value, list) or len(value) != 4 or not all(_num(v, -w, 2 * w) for v in value):
        raise ValueError("Ramka obiektu wymaga [x0, y0, x1, y1]")
    x0, y0, x1, y1 = (round(v) for v in value)
    x0, x1 = sorted((max(0, min(w, x0)), max(0, min(w, x1))))
    y0, y1 = sorted((max(0, min(h, y0)), max(0, min(h, y1))))
    if x1 - x0 < 2 or y1 - y0 < 2:
        raise ValueError("Ramka obiektu jest za mała")
    return [x0, y0, x1, y1]


def normalize_prompt(value, w, h) -> dict:
    if not isinstance(value, dict) or set(value) - {"box", "pos", "neg", "parts", "extra", "hull", "circle", "poly", "auto"}:
        raise ValueError("Nieprawidłowy opis konturu obiektu")
    out = {"hull": value.get("hull", "auto")}
    if out["hull"] not in ("auto", "circle", "none"):
        raise ValueError("Dopełnienie: auto, circle lub none")
    if value.get("poly"):
        poly = _points(value["poly"], w, h, 64)
        if len(poly) < 3:
            raise ValueError("Wielokąt wymaga co najmniej 3 punktów")
        out["poly"] = poly
        out["box"] = _box([min(p[0] for p in poly), min(p[1] for p in poly),
                           max(p[0] for p in poly), max(p[1] for p in poly)], w, h)
        return out
    out["box"] = _box(value.get("box"), w, h)
    out["pos"] = _points(value.get("pos", []), w, h)
    out["neg"] = _points(value.get("neg", []), w, h)
    parts = value.get("parts")
    if parts:
        if not isinstance(parts, list) or len(parts) > MAX_PARTS:
            raise ValueError(f"Maksymalnie {MAX_PARTS} części obiektu")
        out["parts"] = [_points(p, w, h) for p in parts]
    extra = value.get("extra")
    if extra:
        if not isinstance(extra, list) or len(extra) > MAX_EXTRA_BOXES:
            raise ValueError(f"Maksymalnie {MAX_EXTRA_BOXES} dodatkowych ramek")
        out["extra"] = []
        for item in extra:
            if not isinstance(item, dict):
                raise ValueError("Dodatkowa ramka wymaga box i punktów")
            out["extra"].append({"box": _box(item.get("box"), w, h), "pos": _points(item.get("pos", []), w, h),
                                 "neg": _points(item.get("neg", []), w, h)})
    if value.get("circle") is not None:
        c = value["circle"]
        if not isinstance(c, list) or len(c) != 3 or not all(_num(v, 0, 2 * max(w, h)) for v in c):
            raise ValueError("Koło wymaga [cx, cy, r]")
        out["circle"] = [round(v) for v in c]
    if value.get("auto"):
        out["auto"] = True
    if not out["pos"] and not out.get("parts") and not out.get("extra"):
        raise ValueError("Zaznacz co najmniej jeden punkt na obiekcie")
    return out


def normalize_settings(data, scene, w, h) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Ustawienia rozcięcia muszą być obiektem")
    ids = set(scene.asset_ids)
    prompts, depth = {}, {}
    for aid, prompt in (data.get("prompts") or {}).items():
        if aid not in ids:
            raise ValueError("Kontur wskazuje wycinek spoza ujęcia")
        prompts[aid] = normalize_prompt(prompt, w, h)
    for aid, value in (data.get("depth") or {}).items():
        if aid not in ids or not _num(value, -1000, 1000):
            raise ValueError("Głębokość przesłaniania musi być liczbą dla wycinka z ujęcia")
        depth[aid] = float(value)
    extras = data.get("extra_objects") or []
    if not isinstance(extras, list) or len(extras) > MAX_EXTRA_OBJECTS:
        raise ValueError(f"Maksymalnie {MAX_EXTRA_OBJECTS} nowych obiektów")
    seen, extra_out = set(), []
    for item in extras:
        if not isinstance(item, dict):
            raise ValueError("Nowy obiekt wymaga nazwy, grupy i konturu")
        key = item.get("key")
        name = item.get("name")
        group = item.get("group")
        if not isinstance(key, str) or not key.startswith("extra_") or len(key) > 40 or key in seen:
            raise ValueError("Nowy obiekt wymaga unikalnego klucza extra_…")
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError("Podaj nazwę nowego obiektu")
        if group not in GROUP_INDEX or group == "hero":
            raise ValueError("Nowy obiekt nie może być drugą najważniejszą postacią")
        if "depth" in item and not _num(item["depth"], -1000, 1000):
            raise ValueError("Niepoprawna głębokość nowego obiektu")
        seen.add(key)
        extra_out.append({"key": key, "name": name.strip(), "group": group,
                          "depth": float(item.get("depth", len(scene.asset_ids) + len(extra_out))),
                          "prompt": normalize_prompt(item.get("prompt"), w, h)})
    options = data.get("options") or {}
    if not isinstance(options, dict):
        raise ValueError("Opcje muszą być obiektem")
    leftover = options.get("leftover", "layers")
    if leftover not in LEFTOVER_MODES:
        raise ValueError("Reszta sceny: layers, merge albo paper")
    strokes = options.get("smear_strokes") or []
    if not isinstance(strokes, list) or len(strokes) > MAX_STROKES:
        raise ValueError(f"Maksymalnie {MAX_STROKES} pociągnięć smug")
    clean_strokes = []
    for s in strokes:
        if not isinstance(s, dict) or not _num(s.get("width"), 2, 80):
            raise ValueError("Smuga wymaga punktów i szerokości 2–80 px")
        pts = _points(s.get("points"), w, h, 64)
        if not pts:
            raise ValueError("Smuga wymaga co najmniej jednego punktu")
        clean_strokes.append({"points": pts, "width": round(s["width"])})
    colour = options.get("paper_color")
    if colour is not None and (not isinstance(colour, list) or len(colour) != 3 or not all(_num(v, 0, 255) for v in colour)):
        raise ValueError("Kolor papieru wymaga [r, g, b]")
    return {"prompts": prompts, "depth": depth, "extra_objects": extra_out,
            "options": {"leftover": leftover, "fix_seams": bool(options.get("fix_seams", True)),
                        "complete_scenery": bool(options.get("complete_scenery", True)),
                        "smear_strokes": clean_strokes,
                        "paper_color": [round(v) for v in colour] if colour else None}}


def state(store, project, scene) -> dict:
    """Everything the panel needs: per-object prompt (saved or automatic), options, result."""
    saved = scene.generation.get(KEY, {})
    settings = saved.get("settings", {})
    groups = layer_groups(scene)
    names = {a.id: a.name for a in project.assets}
    objects = []
    for i, aid in enumerate(scene.asset_ids):
        automatic = auto_prompt(asset_path(store, project.id, aid, project=project), groups[aid])
        prompt = settings.get("prompts", {}).get(aid) or automatic
        objects.append({"key": aid, "asset_id": aid, "name": names.get(aid, aid), "group": groups[aid],
                        "order": i, "depth": settings.get("depth", {}).get(aid, float(i)),
                        "prompt": prompt, "auto_prompt": automatic})
    w, h = frame_size(store, project, scene)
    return {"width": w, "height": h, "objects": objects,
            "extra_objects": settings.get("extra_objects", []),
            "options": settings.get("options", {"leftover": "layers", "fix_seams": True,
                                                 "complete_scenery": True, "smear_strokes": [],
                                                 "paper_color": None}),
            "result": saved.get("result"), "applied": bool(saved.get("applied")),
            "base_revision": project.revision}


# ------------------------------------------------------------------ job ---
def runtime(repo: Path) -> dict:
    python = Path(os.environ.get("DOCOS_IMAGE_PYTHON",
                  repo / "pilot" / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")))
    models = Path(os.environ.get("DOCOS_CUTOUT_MODELS", repo / "pilot" / "models" / "paper-cutout"))
    return {"python": str(python), "python_ready": python.is_file(), "models_dir": str(models),
            "models": {name: (models / name).is_file() for name in ("mobile_sam.pt", "big-lama.pt")},
            "local": True, "paid": False}


def write_job_input(store, project, scene, job_dir: Path, models_dir: str) -> Path:
    st = state(store, project, scene)
    settings = scene.generation.get(KEY, {}).get("settings", {})
    layers = []
    for obj in st["objects"]:
        prompt = dict(obj["prompt"])
        if obj["group"] in ("characters", "hero") and not prompt.get("parts") and len(prompt.get("pos", [])) > 1:
            prompt["parts"] = [[p] for p in prompt["pos"]]
        layers.append({"key": obj["key"], "name": obj["name"], "group": obj["group"], "order": obj["order"],
                       "depth": obj["depth"], "prompt": prompt,
                       "path": str(asset_path(store, project.id, obj["asset_id"], project=project))})
    extras = []
    for n, item in enumerate(settings.get("extra_objects", [])):
        prompt = dict(item["prompt"])
        if item["group"] == "characters" and not prompt.get("parts") and len(prompt.get("pos", [])) > 1:
            prompt["parts"] = [[p] for p in prompt["pos"]]
        extras.append({**item, "prompt": prompt, "order": len(layers) + n})
    payload = {"width": st["width"], "height": st["height"],
               "background": str(asset_path(store, project.id, scene.asset_id, project=project)),
               "layers": layers, "extra_objects": extras, "options": st["options"],
               "models_dir": models_dir, "output_dir": str(job_dir / "out")}
    job_dir.mkdir(parents=True, exist_ok=True)
    path = job_dir / "input.json"
    path.write_text(json.dumps(payload, ensure_ascii=False))
    return path


def import_outputs(store, pid: str, sid: str, out_dir: Path, *, job_id: str, base_revision: int) -> dict:
    """New PNGs become new library assets; nothing in the scene changes until accepted."""
    project = store.get(pid)
    scene = scene_of(project, sid)
    names = {a.id: a.name for a in project.assets}
    report = json.loads((out_dir / "report.json").read_text())
    common = {"kind": "paper-theatre-recut", "scene_id": sid, "job_id": job_id, "source_revision": base_revision}
    mapping = {}
    for aid in scene.asset_ids:
        png = out_dir / f"{aid}.png"
        if not png.is_file():
            raise ValueError("Worker nie zwrócił wycinka " + names.get(aid, aid))
        asset, _ = import_media(store, pid, png, names.get(aid, aid),
                                {"provenance": {**common, "source_asset_id": aid}})
        mapping[aid] = asset.id
    background, _ = import_media(store, pid, out_dir / "background.png", "papier_tlo.png",
                                 {"provenance": {**common, "role": "paper-backdrop",
                                                 "source_asset_id": scene.asset_id}})
    extras = []
    job_input = json.loads((out_dir.parent / "input.json").read_text())
    for item in job_input.get("extra_objects", []):
        asset, _ = import_media(store, pid, out_dir / f"{item['key']}.png", item["name"] + ".png",
                                {"provenance": {**common, "role": "extra-object", "key": item["key"]}})
        extras.append({"key": item["key"], "name": item["name"], "group": item["group"], "asset_id": asset.id})
    leftovers = []
    for item in report.get("leftovers", []):
        asset, _ = import_media(store, pid, out_dir / f"{item['key']}.png", "reszta_sceny_" + item["key"][-2:] + ".png",
                                {"provenance": {**common, "role": "leftover", "key": item["key"]}})
        leftovers.append({**item, "asset_id": asset.id})
    review, _ = import_media(store, pid, out_dir / "review.jpg", "kontrola_wycinkow.jpg",
                             {"provenance": {**common, "role": "review-sheet"}})
    result = {"job_id": job_id, "source_revision": base_revision, "map": mapping,
              "background": background.id, "extra": extras, "leftovers": leftovers,
              "review_asset_id": review.id, "report": report}
    current = store.get(pid)

    def attach(p):
        target = next(s for s in p.scenes if s.id == sid)
        data = dict(target.generation.get(KEY, {}))
        data["result"] = result
        target.generation = {**target.generation, KEY: data}
    store.mutate(pid, current.revision, attach)
    return result


# --------------------------------------------------------- apply/revert ---
def _new_cue(layer: int, group: str, start: float, **extra) -> dict:
    rig = GROUP_RIG[group]
    cue = {"layer": layer, "group": group, "rig": rig, "start": round(start, 3),
           "duration": round(DEFAULT_DURATION[group], 3), "settle_duration": .14,
           "depth": round(1 + GROUP_INDEX[group] * .3, 2)}
    if rig == "hanging_drop":
        cue.update(string_visible=False, swing_deg=.35, swing_decay=.9, overshoot=.004)
    else:
        cue.update(pivot_x=.5, pivot_y=1, start_rotation=82, overshoot_rotation=-5, stick_visible=False)
    cue.update(extra)
    return cue


def accept(project, sid: str) -> None:
    scene = next((s for s in project.scenes if s.id == sid), None)
    if scene is None or scene.template != "paper-theatre":
        raise ValueError("Wybierz ujęcie Paper Theatre")
    if scene.locked or scene.lock_media:
        raise ValueError("Odblokuj media tego ujęcia przed podmianą wycinków")
    data = dict(scene.generation.get(KEY, {}))
    result = data.get("result")
    if not result:
        raise ValueError("Najpierw uruchom ponowne rozcięcie")
    if data.get("applied"):
        raise ValueError("Te wycinki są już zastosowane")
    if set(result["map"]) != set(scene.asset_ids):
        raise ValueError("Ujęcie zmieniło się od rozcięcia; uruchom je ponownie")
    have = {a.id for a in project.assets}
    needed = list(result["map"].values()) + [result["background"]] + \
        [e["asset_id"] for e in result["extra"]] + [x["asset_id"] for x in result["leftovers"]]
    if any(aid not in have for aid in needed):
        raise ValueError("Brakuje plików wyniku w bibliotece")
    cues = [dict(c) for c in scene.parameters.get("layer_cues", [])]
    data["previous"] = {"asset_id": scene.asset_id, "asset_ids": list(scene.asset_ids),
                        "layer_cues": [dict(c) for c in cues]}
    ids = [result["map"][aid] for aid in scene.asset_ids]
    for item in result["extra"]:
        same = [c for c in cues if c.get("group") == item["group"]]
        start = max((c["start"] + c.get("duration", .5) for c in same), default=0) + .05
        ids.append(item["asset_id"])
        cues.append(_new_cue(len(ids), item["group"], start))
    for n, item in enumerate(result["leftovers"]):
        ids.append(item["asset_id"])
        # Remaining scenery (sky, river, walls) is the stage itself: it arrives
        # first and is drawn behind every object.
        cues.append(_new_cue(len(ids), "landscape", .02 + .08 * n, z_index=-100 + n))
    if len(ids) > 1000:
        raise ValueError("Zbyt wiele warstw w ujęciu")
    scene.asset_id = result["background"]
    scene.asset_ids = ids
    scene.parameters = {**scene.parameters, "layer_cues": cues}
    data["applied"] = True
    scene.generation = {**scene.generation, KEY: data}


def revert(project, sid: str) -> None:
    scene = next((s for s in project.scenes if s.id == sid), None)
    if scene is None:
        raise ValueError("Nie ma takiego ujęcia")
    if scene.locked or scene.lock_media:
        raise ValueError("Odblokuj media tego ujęcia przed przywróceniem")
    data = dict(scene.generation.get(KEY, {}))
    previous = data.get("previous")
    if not data.get("applied") or not previous:
        raise ValueError("Nie ma czego przywracać")
    scene.asset_id = previous["asset_id"]
    scene.asset_ids = list(previous["asset_ids"])
    scene.parameters = {**scene.parameters, "layer_cues": previous["layer_cues"]}
    data["applied"] = False
    scene.generation = {**scene.generation, KEY: data}
