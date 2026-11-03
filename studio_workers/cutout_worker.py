"""Paper Theatre re-cut worker. Runs only in the user's image-model environment.

    python -I cutout_worker.py JOB_DIR

Reads ``JOB_DIR/input.json`` (written by ``studio_core.paper_theatre_recut``),
writes ``JOB_DIR/out/``: one RGBA PNG per object, ``background.png`` (plain
paper), optional ``extra_*.png`` / ``leftover_*.png``, ``report.json`` and
``review.jpg``. Progress lines: ``PROGRESS <0..1> <message>``.

Models are free and local (Apache-2.0): MobileSAM for contours, LaMa for the
few hidden scenery parts. They are downloaded once and verified by SHA-256.
Peak memory stays around 2 GB: LaMa and MobileSAM never live together.
"""
from __future__ import annotations

import gc
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cutout_core as core  # noqa: E402

MODELS = {
    "mobile_sam": ("mobile_sam.pt",
                   "https://raw.githubusercontent.com/ChaoningZhang/MobileSAM/"
                   "f706ad9c4eb7f219c00d9050e46328518ffb65d2/weights/mobile_sam.pt",
                   "6dbb90523a35330fedd7f1d3dfc66f995213d81b29a5ca8108dbcdd4e37d6c2f"),
    "lama": ("big-lama.pt",
             "https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt",
             "7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c"),
}


def progress(value: float, message: str):
    print(f"PROGRESS {value:.3f} {message}", flush=True)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ensure_model(folder: Path, key: str) -> Path:
    name, url, digest = MODELS[key]
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    if target.is_file() and sha256(target) == digest:
        return target
    progress(.02, f"Pobieranie modelu {name} (jednorazowo)")
    partial = target.with_suffix(".part")
    with urllib.request.urlopen(url, timeout=120) as response, partial.open("wb") as out:
        while chunk := response.read(1 << 20):
            out.write(chunk)
    if sha256(partial) != digest:
        partial.unlink(missing_ok=True)
        raise ValueError(f"Suma kontrolna modelu {name} nie zgadza się; pobieranie przerwane")
    os.replace(partial, target)
    return target


# ---------------------------------------------------------------- models ---
class Lama:
    def __init__(self, path: Path):
        import torch
        torch.set_num_threads(max(1, (os.cpu_count() or 2)))
        self.torch = torch
        self.model = torch.jit.load(str(path), map_location="cpu").eval()

    def __call__(self, img: np.ndarray, mask: np.ndarray, max_side=1024) -> np.ndarray:
        import cv2
        if not mask.any():
            return img.copy()
        h, w = mask.shape
        scale = min(1.0, max_side / max(h, w))
        im, m = img, mask.astype(np.uint8) * 255
        if scale < 1:
            im = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
            m = cv2.dilate(cv2.resize(m, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_NEAREST),
                           np.ones((3, 3), np.uint8))
        sh, sw = m.shape
        ph, pw = (8 - sh % 8) % 8, (8 - sw % 8) % 8
        imp = np.pad(im, ((0, ph), (0, pw), (0, 0)), mode="reflect")
        mp = np.pad(m, ((0, ph), (0, pw)), mode="reflect")
        t = self.torch.from_numpy(imp).permute(2, 0, 1)[None].float() / 255
        mt = (self.torch.from_numpy(mp)[None, None].float() > 127).float()
        with self.torch.inference_mode():
            out = self.model(t, mt)
        out = (out[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8)[:sh, :sw]
        if scale < 1:
            out = cv2.resize(out, (w, h), interpolation=cv2.INTER_CUBIC)
        result = img.copy()
        result[mask] = out[mask]
        return result

    def crop(self, img, mask, margin=48):
        ys, xs = np.nonzero(mask)
        if not len(ys):
            return img.copy()
        h, w = mask.shape
        y0, y1 = max(0, ys.min() - margin), min(h, ys.max() + 1 + margin)
        x0, x1 = max(0, xs.min() - margin), min(w, xs.max() + 1 + margin)
        result = img.copy()
        result[y0:y1, x0:x1] = self(img[y0:y1, x0:x1], mask[y0:y1, x0:x1])
        return result


class Segmenter:
    def __init__(self, path: Path):
        import torch
        from mobile_sam import sam_model_registry, SamPredictor
        device = os.environ.get("DOCOS_CUTOUT_DEVICE", "cpu")
        model = sam_model_registry["vit_t"](checkpoint=str(path)).to(device).eval()
        self.predictor = SamPredictor(model)
        self.torch = torch

    def __call__(self, img, box, pos=(), neg=(), up=4, margin=24):
        """MobileSAM on an upscaled crop around the box: sharper contours on small objects."""
        import cv2
        h, w = img.shape[:2]
        bx0, by0, bx1, by1 = box
        cx0, cy0 = max(0, int(bx0 - margin)), max(0, int(by0 - margin))
        cx1, cy1 = min(w, int(bx1 + margin)), min(h, int(by1 + margin))
        crop = img[cy0:cy1, cx0:cx1]
        ch, cw = crop.shape[:2]
        f = max(1.0, min(up, 1024 / max(ch, cw)))
        self.predictor.set_image(cv2.resize(crop, (round(cw * f), round(ch * f)), interpolation=cv2.INTER_CUBIC))
        kw = {"box": np.array([(bx0 - cx0) * f, (by0 - cy0) * f, (bx1 - cx0) * f, (by1 - cy0) * f], np.float32)}
        points = list(pos) + list(neg)
        if points:
            kw["point_coords"] = np.array([[(x - cx0) * f, (y - cy0) * f] for x, y in points], np.float32)
            kw["point_labels"] = np.array([1] * len(pos) + [0] * len(neg), np.int32)
        masks, scores, _ = self.predictor.predict(multimask_output=True, return_logits=True, **kw)
        logits = masks[int(np.argmax(scores))]
        soft = 1 / (1 + np.exp(-np.clip(logits, -30, 30) * 2))
        out = np.zeros((h, w), np.float32)
        out[cy0:cy1, cx0:cx1] = cv2.resize(soft.astype(np.float32), (cw, ch), interpolation=cv2.INTER_AREA)
        return out


def segment_object(seg, master, prompt) -> np.ndarray:
    box = prompt["box"]
    soft = np.zeros(master.shape[:2], np.float32)
    parts = prompt.get("parts") or [prompt.get("pos", [])]
    for pts in parts:
        soft = np.maximum(soft, seg(master, box, pts, prompt.get("neg", [])))
    for extra in prompt.get("extra", []):
        soft = np.maximum(soft, seg(master, extra["box"], extra.get("pos", []), extra.get("neg", [])))
    return soft


# ------------------------------------------------------------------ main ---
def run(job: Path):
    started = time.monotonic()
    data = json.loads((job / "input.json").read_text())
    out_dir = Path(data["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    options = data.get("options", {})
    models = Path(data["models_dir"])
    width, height = int(data["width"]), int(data["height"])
    progress(.01, "Sprawdzanie modeli")
    lama_path = ensure_model(models, "lama")
    sam_path = ensure_model(models, "mobile_sam")

    progress(.05, "Składanie obrazu źródłowego")
    background = np.array(Image.open(data["background"]).convert("RGB").resize((width, height)))
    layers = data["layers"]
    rgba = [np.array(Image.open(item["path"]).convert("RGBA").resize((width, height))) for item in layers]
    master, coverage = core.compose(background, rgba)
    del rgba
    gc.collect()

    clean_mask = np.zeros((height, width), bool)
    if options.get("fix_seams", True):
        clean_mask |= core.seam_mask(coverage)
    clean_mask |= core.stroke_mask((height, width), options.get("smear_strokes", []))
    lama = None
    if clean_mask.any():
        progress(.08, "Usuwanie szwów i smug ze źródła")
        lama = Lama(lama_path)
        master = lama(master, clean_mask, max_side=max(width, height))
        del lama
        lama = None
        gc.collect()
    Image.fromarray(master).save(out_dir / "master.png")

    objects = list(layers) + list(data.get("extra_objects", []))
    groups = {o["key"]: o["group"] for o in objects}
    depth = {o["key"]: float(o["depth"]) for o in objects}
    order_index = {o["key"]: int(o.get("order", i)) for i, o in enumerate(objects)}

    progress(.12, "Wczytywanie MobileSAM")
    seg = Segmenter(sam_path)
    masks: dict[str, np.ndarray] = {}
    polys = []
    for n, obj in enumerate(objects):
        prompt = obj["prompt"]
        if prompt.get("poly"):
            polys.append(obj)
            continue
        progress(.12 + .5 * n / max(1, len(objects)), "Kontur: " + obj["name"])
        masks[obj["key"]] = core.clean(segment_object(seg, master, prompt))
    del seg
    gc.collect()
    import cv2
    for obj in polys:
        region = np.zeros((height, width), np.uint8)
        cv2.fillPoly(region, [np.array(obj["prompt"]["poly"], np.int32)], 1)
        taken = np.zeros((height, width), bool)
        for m in masks.values():
            taken |= m
        masks[obj["key"]] = core.clean(((region > 0) & ~taken).astype(np.float32))

    progress(.64, "Rozstrzyganie przesłaniania")
    own, keys = core.ownership(masks, depth)
    del masks
    gc.collect()
    own = core.absorb_slivers(own, keys, depth)
    circles = {}
    for obj in objects:
        p = obj["prompt"]
        if p.get("hull") == "circle":
            circle = p.get("circle") or core.fit_circle(own == keys.index(obj["key"]))
            if circle:
                circles[obj["key"]] = circle
                own = core.circle_claim(own, keys, order_index, obj["key"], circle)
    mode = options.get("leftover", "layers")
    own, regions = core.leftovers(own, keys, groups, mode, min_area=int(.002 * width * height))

    progress(.70, "Dopełnianie zasłoniętej scenografii")
    complete = options.get("complete_scenery", True)
    if complete:
        lama = Lama(lama_path)
    report_layers = {}
    written = []
    for i, key in enumerate(keys):
        obj = next(o for o in objects if o["key"] == key)
        visible = own == i
        extended = np.zeros_like(visible)
        fill = None
        if complete and visible.any() and groups[key] in core.SCENERY_GROUPS:
            occluders = core.front_occluders(i, keys, own, depth, groups, order_index)
            hull = core.hull_of(visible, obj["prompt"].get("hull", "auto"), circles.get(key))
            extended = hull & occluders
            if extended.sum() >= 20:
                if key in circles:
                    cx, cy, r = circles[key]
                    disc = np.zeros(visible.shape, np.uint8)
                    cv2.circle(disc, (cx, cy), r + 2, 1, -1)
                    source = master.copy()
                    colour = np.median(master[visible], axis=0).astype(np.uint8)
                    source[(disc == 0) | ((disc > 0) & ~visible)] = colour
                    fill = lama.crop(source, (disc > 0) & ~visible, margin=30)
                else:
                    hole = cv2.dilate(occluders.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
                    hole &= ~visible
                    ys, xs = np.nonzero(visible | extended)
                    box = np.zeros_like(hole)
                    box[max(0, ys.min() - 40):ys.max() + 40, max(0, xs.min() - 40):xs.max() + 40] = True
                    fill = lama.crop(master, hole & box, margin=48)
            else:
                extended[:] = False
        full = visible | extended
        layer = core.rgba_layer(master, full, fill, extended)
        Image.fromarray(layer, "RGBA").save(out_dir / f"{key}.png", compress_level=6)
        written.append((order_index[key], layer))
        report_layers[key] = {"visible": int(visible.sum()), "extended": int(extended.sum()),
                              "empty": not bool(visible.any())}
        progress(.70 + .22 * (i + 1) / len(keys), "Warstwa: " + obj["name"])
    if lama is not None:
        del lama
        gc.collect()
    leftover_files = []
    for n, region in enumerate(regions):
        layer = core.rgba_layer(master, region)
        name = f"leftover_{n + 1:02d}"
        Image.fromarray(layer, "RGBA").save(out_dir / f"{name}.png")
        ys, xs = np.nonzero(region)
        leftover_files.append({"key": name, "area": int(region.sum()),
                               "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]})
        written.append((-1000 + n, layer))

    progress(.94, "Papierowe tło i kontrola")
    colour = options.get("paper_color") or core.paper_color(background)
    backdrop = core.paper(width, height, tuple(colour))
    Image.fromarray(backdrop).save(out_dir / "background.png")
    # same draw order as the Studio compositor: leftovers first, then asset order
    final = core.composite(backdrop, [layer for _, layer in sorted(written, key=lambda x: x[0])])
    diff = np.abs(final.astype(np.int16) - master.astype(np.int16)).max(-1)
    covered = np.zeros(own.shape, bool)
    for region in regions:
        covered |= region
    unowned = int(((own == -1) & ~covered).sum())
    warnings = []
    for key, info in report_layers.items():
        if info["empty"]:
            warnings.append(next(o["name"] for o in objects if o["key"] == key) +
                            ": kontur nie objął żadnego widocznego piksela; popraw punkty")
    if unowned and mode == "paper":
        warnings.append(f"{unowned} px nie należy do żadnego wycinka: w ostatniej klatce będzie tam papier")
    report = {
        "layers": report_layers, "leftovers": leftover_files, "leftover_mode": mode,
        "unowned_px": unowned, "paper_color": [int(v) for v in colour],
        "final_mean_abs_diff": round(float(np.abs(final.astype(np.int16) - master.astype(np.int16)).mean()), 4),
        "final_px_over_20": int((diff > 20).sum()), "warnings": warnings,
        "holes_under_characters": True, "completed_scenery": bool(complete),
        "seconds": round(time.monotonic() - started, 1),
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    items = [(next(o["name"] for o in objects if o["key"] == k), own == i) for i, k in enumerate(keys)]
    core.review_sheet(master, items).save(out_dir / "review.jpg", quality=86)
    progress(1.0, "Gotowe")


if __name__ == "__main__":
    run(Path(sys.argv[1]))
