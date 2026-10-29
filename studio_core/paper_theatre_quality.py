"""Conservative alpha-cutout diagnostics for Paper Theatre asset review.

These measurements flag suspicious files. They do not certify that a PNG
matches its approved storyboard reference or that occluded pixels exist.
"""
from __future__ import annotations

from collections import deque

from PIL import Image


def alpha_diagnostics(image: Image.Image) -> dict:
    """Count substantial disconnected opaque islands on a low-resolution mask.

    Small decorative islands and antialias noise are ignored. A warning is
    advisory: clouds, leaves and multi-part costumes may be legitimately split.
    """
    alpha = image.convert("RGBA").getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return {"regions": 0, "coverage": 0.0}
    pixels = alpha.crop(bbox).resize((64, 64), Image.Resampling.NEAREST)
    active = {(x, y) for y in range(64) for x in range(64)
              if pixels.getpixel((x, y)) >= 96}
    occupied = len(active)
    count = 0
    while active:
        start = active.pop()
        pending = deque([start])
        area = 1
        while pending:
            x, y = pending.popleft()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in active:
                    active.remove(neighbor)
                    pending.append(neighbor)
                    area += 1
        if area >= max(8, occupied * .025):
            count += 1
    return {"regions": count, "coverage": round(occupied / 4096, 4)}


def layout_warnings(cutouts: list[dict], scene_size: tuple[int, int]) -> list[str]:
    """Advisory off-canvas and strong alpha-bbox overlap warnings.

    Intended occlusion is allowed. These are only coarse silhouette bounding
    rectangles, not collision detection on rendered video frames.
    """
    width, height = scene_size
    boxes = []
    warnings = []
    for item in cutouts:
        layout = item.get("layout", {})
        if not layout:
            continue
        bounds = item["bounds"]
        source_width = max(1, bounds[2] - bounds[0])
        source_height = bounds[3] - bounds[1]
        w = layout["layout_width"]
        h = w * source_height / source_width * width / height
        x, y = layout["layout_x"], layout["layout_y"]
        box = (x - w / 2, y - h, x + w / 2, y)
        if box[0] < -.03 or box[1] < -.03 or box[2] > 1.03 or box[3] > 1.03:
            warnings.append(item["name"] + ": sylwetka wykracza poza kadr; sprawdź zamierzony crop")
        for other, previous in boxes:
            overlap_w = max(0.0, min(box[2], previous[2]) - max(box[0], previous[0]))
            overlap_h = max(0.0, min(box[3], previous[3]) - max(box[1], previous[1]))
            intersection = overlap_w * overlap_h
            area = min((box[2] - box[0]) * (box[3] - box[1]),
                       (previous[2] - previous[0]) * (previous[3] - previous[1]))
            if area > 0 and intersection / area > .65:
                warnings.append(item["name"] + " / " + other +
                                ": duże nakładanie obrysów, zweryfikuj przesłanianie Z")
        boxes.append((item["name"], box))
    return warnings
