"""Paper Theatre re-cut: pure image logic (numpy + OpenCV + Pillow, no models).

Imported by ``cutout_worker.py`` inside the image-model environment. Rules
(the owner's production guidelines):

* one object = one PNG cut along its real contour;
* the film starts from plain paper: every pixel of the final composition
  belongs to some cutout, the backdrop is procedural paper only;
* nothing is invented under characters: a layer behind a character keeps an
  empty hole there (paper shows through until the character arrives);
* hidden parts may be completed only for scenery/props that are covered by
  other scenery/props arriving later (sun behind clouds, coin under coin);
* the static final composition equals the source image pixel for pixel.
"""
from __future__ import annotations

import numpy as np
import cv2
from PIL import Image, ImageDraw

CHARACTER_GROUPS = ("characters", "hero")
SCENERY_GROUPS = ("sky", "landscape", "foundations", "vegetation", "props")


# ---------------------------------------------------------------- source ---
def compose(background: np.ndarray, layers: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Flatten the current scene. Returns RGB master and coverage of the cutouts."""
    canvas = Image.fromarray(background).convert("RGBA")
    coverage = np.zeros(background.shape[:2], np.float32)
    for rgba in layers:
        canvas.alpha_composite(Image.fromarray(rgba, "RGBA"))
        a = rgba[..., 3].astype(np.float32) / 255
        coverage = 1 - (1 - coverage) * (1 - a)
    return np.array(canvas.convert("RGB")), coverage


def seam_mask(coverage: np.ndarray) -> np.ndarray:
    """Feathered polygon seams of earlier cutouts let the old backdrop bleed through."""
    seam = (coverage > .02) & (coverage < .995)
    return cv2.dilate(seam.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0


def stroke_mask(shape, strokes) -> np.ndarray:
    mask = np.zeros(shape, np.uint8)
    for stroke in strokes or []:
        points = np.array(stroke["points"], np.int32)
        if len(points) == 1:
            cv2.circle(mask, tuple(int(v) for v in points[0]), max(1, int(stroke["width"]) // 2), 255, -1)
        else:
            cv2.polylines(mask, [points], False, 255, int(stroke["width"]), lineType=cv2.LINE_AA)
    return mask > 0


# ----------------------------------------------------------------- masks ---
def clean(soft: np.ndarray, *, threshold=.5) -> np.ndarray:
    """Drop speckles (<2% of the object), fill pin-holes; keep real holes (coins)."""
    hard = (soft > threshold).astype(np.uint8)
    h, w = hard.shape
    n, lab, st, _ = cv2.connectedComponentsWithStats(hard, 8)
    if n > 1:
        areas = st[1:, cv2.CC_STAT_AREA]
        keep = np.zeros(n, bool)
        keep[1:] = areas >= max(20, .02 * areas.sum())
        if not keep[1:].any():
            keep[1 + int(areas.argmax())] = True
        hard = keep[lab].astype(np.uint8)
    area = int(hard.sum())
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - hard, 4)
    for i in range(1, n):
        x, y, bw, bh, a = st[i]
        if x > 0 and y > 0 and x + bw < w and y + bh < h and a < max(12, .004 * area):
            hard[lab == i] = 1
    return hard.astype(bool)


def ownership(masks: dict[str, np.ndarray], depth: dict[str, float]) -> tuple[np.ndarray, list[str]]:
    """Every pixel belongs to the closest (highest depth) object whose mask covers it."""
    keys = list(masks)
    shape = next(iter(masks.values())).shape
    own = np.full(shape, -1, np.int32)
    best = np.full(shape, -np.inf, np.float32)
    for i, key in enumerate(keys):
        take = masks[key] & (depth[key] > best)
        own[take] = i
        best[take] = depth[key]
    return own, keys


def _grow_into(own, free, order, allowed, iterations):
    kernel = np.ones((3, 3), np.uint8)
    for _ in range(iterations):
        if not free.any():
            break
        for i in order:
            if i not in allowed:
                continue
            take = (cv2.dilate((own == i).astype(np.uint8), kernel) > 0) & free
            if take.any():
                own[take] = i
                free &= ~take
    return free


def absorb_slivers(own, keys, depth, *, edge_px=3, sliver=7, small=400):
    """Thin gaps and crumbs between objects, plus a 3 px paper edge, join the neighbours."""
    order = sorted(range(len(keys)), key=lambda i: depth[keys[i]])
    allowed = set(order)
    unowned = (own == -1).astype(np.uint8)
    opened = cv2.morphologyEx(unowned, cv2.MORPH_OPEN,
                              cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (sliver, sliver)))
    absorb = (unowned > 0) & (opened == 0)
    n, lab, st, _ = cv2.connectedComponentsWithStats(unowned, 8)
    tiny = np.zeros(n, bool)
    tiny[1:] = st[1:, cv2.CC_STAT_AREA] < small
    absorb |= tiny[lab] & (unowned > 0)
    _grow_into(own, absorb, order, allowed, 12)
    _grow_into(own, own == -1, order, allowed, edge_px)
    return own


def circle_claim(own, keys, index_of, name, circle):
    """Unowned pixels inside a disc (sun, moon) belong to the objects in front of it."""
    cx, cy, r = circle
    disc = np.zeros(own.shape, np.uint8)
    cv2.circle(disc, (int(cx), int(cy)), int(r) + 1, 1, -1)
    inside = (disc > 0) & (own == -1)
    later = {i for i, k in enumerate(keys) if index_of.get(k, -1) > index_of[name]}
    _grow_into(own, inside, sorted(later), later, 40)
    return own


def leftovers(own, keys, groups, mode, *, min_area):
    """Pixels still unowned. 'merge' gives them to the nearest scenery cutout,
    'layers' returns connected regions as new scenery cutouts, 'paper' keeps them out."""
    free = own == -1
    if not free.any() or mode == "paper":
        return own, []
    scenery = {i for i, k in enumerate(keys) if groups.get(k) in SCENERY_GROUPS}
    everyone = set(range(len(keys)))
    if mode == "merge":
        _grow_into(own, free, sorted(scenery), scenery, 2000)
        _grow_into(own, own == -1, sorted(everyone), everyone, 200)
        return own, []
    n, lab, st, _ = cv2.connectedComponentsWithStats(free.astype(np.uint8), 8)
    regions = []
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= min_area:
            regions.append(lab == i)
    big = np.zeros(free.shape, bool)
    for r in regions:
        big |= r
    _grow_into(own, free & ~big, sorted(scenery), scenery, 400)
    # pockets enclosed only by characters (no scenery neighbour) join them
    _grow_into(own, (own == -1) & ~big, sorted(everyone), everyone, 200)
    regions.sort(key=lambda r: (np.nonzero(r)[0].min(), np.nonzero(r)[1].min()))
    return own, regions


def hull_of(visible: np.ndarray, kind="auto", circle=None) -> np.ndarray:
    h, w = visible.shape
    if kind == "none":
        return visible.copy()
    if kind == "circle" and circle:
        m = np.zeros((h, w), np.uint8)
        cv2.circle(m, (int(circle[0]), int(circle[1])), int(circle[2]), 1, -1)
        return m > 0
    hm = np.zeros((h, w), np.uint8)
    n, lab = cv2.connectedComponents(visible.astype(np.uint8))
    for c in range(1, n):
        ys, xs = np.nonzero(lab == c)
        if len(ys) >= 3:
            cv2.fillPoly(hm, [cv2.convexHull(np.stack([xs, ys], 1).astype(np.int32))], 1)
    r = int(np.clip(.35 * np.sqrt(max(1, visible.sum())), 6, 60))
    near = cv2.dilate(visible.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    return (hm > 0) & (near > 0)


def fit_circle(visible: np.ndarray):
    ys, xs = np.nonzero(visible)
    if len(xs) < 10:
        return None
    (cx, cy), r = cv2.minEnclosingCircle(np.stack([xs, ys], 1).astype(np.float32))
    return [int(round(cx)), int(round(cy)), int(round(r))]


def front_occluders(index, keys, own, depth, groups, order_index):
    """Pixels of objects drawn later AND closer that are scenery/props (never characters)."""
    me = keys[index]
    mask = np.zeros(own.shape, bool)
    for j, k in enumerate(keys):
        if order_index.get(k, -1) > order_index[me] and depth[k] > depth[me] \
                and groups.get(k) not in CHARACTER_GROUPS:
            mask |= own == j
    return mask


def rgba_layer(master_rgb: np.ndarray, full: np.ndarray, fill: np.ndarray | None = None,
               extended: np.ndarray | None = None) -> np.ndarray:
    """Solid exact pixels inside, a 1 px anti-aliased fringe outside; RGB cleared far away."""
    rgb = master_rgb.copy()
    if fill is not None and extended is not None and extended.any():
        rgb[extended] = fill[extended]
    alpha = np.clip(cv2.GaussianBlur(full.astype(np.float32), (0, 0), .7) * 1.6, 0, 1)
    alpha[full] = 1.0
    a8 = (alpha * 255).round().astype(np.uint8)
    keep = cv2.dilate((a8 > 0).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    out = np.zeros(full.shape + (4,), np.uint8)
    out[..., :3] = np.where(keep[..., None], rgb, 0)
    out[..., 3] = a8
    return out


# ----------------------------------------------------------------- paper ---
def paper(width: int, height: int, base=(190, 166, 133), seed=7) -> np.ndarray:
    """Plain paper backdrop: soft blotches, grain and fibres. No scenery."""
    g = np.random.default_rng(seed)

    def noise(scale, sx, sy):
        return cv2.GaussianBlur(g.normal(0, 1, (height, width)).astype(np.float32), (0, 0),
                                sigmaX=sx, sigmaY=sy) * scale
    low = noise(1, 40, 40)
    low = low / max(1e-6, float(np.abs(low).max())) * 6
    texture = low + noise(4, 3, 3) + noise(3, 8, .8)
    return np.clip(np.array(base, np.float32) + texture[..., None], 0, 255).astype(np.uint8)


def paper_color(background: np.ndarray) -> list[int]:
    return [int(v) for v in np.median(background.reshape(-1, 3), axis=0)]


# ---------------------------------------------------------------- checks ---
def composite(paper_rgb: np.ndarray, layers: list[np.ndarray]) -> np.ndarray:
    canvas = Image.fromarray(paper_rgb).convert("RGBA")
    for rgba in layers:
        canvas.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return np.array(canvas.convert("RGB"))


def review_sheet(master: np.ndarray, items: list[tuple[str, np.ndarray]], columns=6,
                 tile=(260, 200)) -> Image.Image:
    """Each object: crop dimmed outside its mask + green contour, for a quick human check."""
    tw, th = tile
    rows = max(1, (len(items) + columns - 1) // columns)
    sheet = Image.new("RGB", (tw * columns, (th + 14) * rows), (200, 200, 200))
    for k, (name, mask) in enumerate(items):
        t = Image.new("RGB", (tw, th + 14), (255, 255, 255))
        ys, xs = np.nonzero(mask)
        if len(ys):
            pad = 20
            y0, y1 = max(0, ys.min() - pad), min(mask.shape[0], ys.max() + pad)
            x0, x1 = max(0, xs.min() - pad), min(mask.shape[1], xs.max() + pad)
            crop = master[y0:y1, x0:x1].astype(np.float32)
            mm = mask[y0:y1, x0:x1, None].astype(np.float32)
            dim = crop * (.35 + .65 * mm) + np.array([0, 0, 90]) * (1 - mm) * .5
            edge = cv2.Canny(mask[y0:y1, x0:x1].astype(np.uint8) * 255, 50, 150) > 0
            dim[edge] = [0, 255, 0]
            c = Image.fromarray(dim.clip(0, 255).astype(np.uint8))
            c.thumbnail((tw, th))
            t.paste(c, ((tw - c.width) // 2, 0))
        ImageDraw.Draw(t).text((2, th + 1), name[:40], fill=(0, 0, 0))
        sheet.paste(t, ((k % columns) * tw, (k // columns) * (th + 14)))
    return sheet
