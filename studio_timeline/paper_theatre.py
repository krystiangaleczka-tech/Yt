"""Physical-looking, deterministic paper-cut entrance rigs.

All inputs use pre-cut transparent PNG layers placed on the final canvas.
No model, random physics, or frame-to-frame state is required, so arbitrary
preview frames and cached render segments have identical geometry.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter, ImageChops

RESAMPLE = Image.Resampling.BICUBIC


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _progress(seconds: float, duration: float) -> float:
    return _clamp(seconds / duration) if duration > 0 else 1.0


def _settle(seconds: float, duration: float, length: float) -> float:
    if seconds <= duration:
        return 1.0
    if length <= 0:
        return 0.0
    p = _clamp((seconds - duration) / length)
    return (1.0 - p) ** 2 * math.cos(2 * math.pi * p)


def _shadow(canvas: Image.Image, sprite: Image.Image) -> None:
    """Soft printed-paper edge, drawn behind the cutout."""
    width, height = canvas.size
    blur = max(1.0, width * .003)
    alpha = sprite.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    alpha = alpha.point(lambda value: round(value * .2))
    shade = Image.new("RGBA", (width, height), (40, 26, 17, 0))
    shade.putalpha(alpha)
    canvas.alpha_composite(shade, (max(1, round(width * .003)), max(1, round(height * .005))))


def _bbox(source: Image.Image) -> tuple[int, int, int, int] | None:
    return source.getchannel("A").getbbox()


def _place(source: Image.Image, y: int) -> Image.Image:
    result = Image.new("RGBA", source.size)
    result.alpha_composite(source, (0, y))
    return result


def _outlined(source: Image.Image, width: int, color: str) -> Image.Image:
    """Colored outline follows actual transparency, not a rectangular crop."""
    if width <= 0:
        return source
    alpha = source.getchannel("A")
    dilated = alpha.filter(ImageFilter.MaxFilter(2 * width + 1))
    border = ImageChops.subtract(dilated, alpha)
    stroke = Image.new("RGBA", source.size, color)
    stroke.putalpha(border)
    stroke.alpha_composite(source)
    return stroke


def layout_cutout(source: Image.Image, cue: dict, width: int, height: int) -> Image.Image:
    """Place an isolated RGBA object into a normalized, alpha-preserving scene.

    layout_x is the horizontal center of the silhouette, layout_y its bottom.
    layout_width is expressed in fractions of the final scene width. Z-order
    is controlled separately by the compositor, never by altering start time.
    """
    bounds = source.getchannel("A").getbbox()
    canvas = Image.new("RGBA", (width, height))
    if not bounds:
        return canvas
    cutout = source.crop(bounds)
    target_width = max(1, round(width * float(cue["layout_width"])))
    target_height = max(1, round(cutout.height * target_width / cutout.width))
    # Prevent unbounded output sizes for malformed tall source images.
    if target_height > height * 4:
        factor = height * 4 / target_height
        target_width = max(1, round(target_width * factor))
        target_height = height * 4
    resized = cutout.resize((target_width, target_height), RESAMPLE)
    x = round(width * float(cue["layout_x"]) - target_width / 2)
    y = round(height * float(cue["layout_y"]) - target_height)
    canvas.alpha_composite(resized, (x, y))
    return canvas


def rig_image(source: Image.Image, rig: str, cue: dict, elapsed: float, duration: float) -> Image.Image:
    """Return a full-size transparent layer positioned by one entrance rig.

    elapsed is relative to this layer's scheduled start. alpha, sprite shape,
    and destination coordinates are preserved. Rake lift hinges around the
    alpha-bounded cutout rather than rotating an entire transparent canvas.
    """
    width, height = source.size
    canvas = Image.new("RGBA", (width, height))
    bounds = _bbox(source)
    if elapsed < 0 or bounds is None:
        return canvas
    if cue.get("outline_px"):
        source = _outlined(source, int(cue["outline_px"]), cue.get("outline_color", "#362820"))
        # Outlining expands the visible silhouette. Recompute bounds before
        # rotating/cropping or the thick border will be cut back off.
        bounds = _bbox(source)
    if rig == "static":
        return source.copy()

    progress = _progress(elapsed, duration)
    ease = 1 - (1 - progress) ** 3
    settle_length = float(cue.get("settle_duration", .15))
    overshoot = float(cue.get("overshoot", .03))

    if rig == "hanging_drop":
        # The *whole* alpha sprite travels from above the frame. Never reveal
        # it with a mosaic wipe, patches, or a changing source mask.
        travel = bounds[3] + max(2, round(height * .06))
        dy = -travel * (1 - ease) + overshoot * height * progress ** 6
        if elapsed >= duration:
            dy = overshoot * height * _settle(elapsed, duration, settle_length)
        swing = float(cue.get("swing_deg", 3.0))
        decay = float(cue.get("swing_decay", 1.1))
        angle = swing * math.sin(elapsed * 8.0) * math.exp(-decay * elapsed)
        pivot_x = (bounds[0] + bounds[2]) / 2
        pivot_y = bounds[1] + dy
        sprite = _place(source, round(dy))
        if angle:
            sprite = sprite.rotate(angle, resample=RESAMPLE, center=(pivot_x, pivot_y))
        _shadow(canvas, sprite)

        # The cord must visibly CONNECT the ceiling and the moving cutout.
        # Draw behind paper, and retract it only after the cutout has landed.
        anchor_y = round(pivot_y)
        anchor_x = round(pivot_x)
        if cue.get("string_visible", False) and anchor_y > 0:
            # Explicit legacy string_length cues kept the cord in the final frame.
            # New planned cues omit that key and release it after landing.
            retract = (0.0 if "string_length" in cue else
                       _clamp((elapsed - duration) / max(.001, settle_length)))
            alpha = round(190 * (1 - retract))
            if alpha > 0:
                ImageDraw.Draw(canvas).line(
                    (anchor_x, 0, anchor_x, min(height - 1, anchor_y)),
                    fill=(62, 49, 38, alpha),
                    width=max(2, round(width / 720)),
                )
        canvas.alpha_composite(sprite)
        # A stationary ink pin is left when the cord has been released.
        if cue.get("string_visible", False) and elapsed >= duration and 0 <= anchor_y < height:
            radius = max(2, round(width / 480))
            ImageDraw.Draw(canvas).ellipse(
                (anchor_x - radius, anchor_y - radius,
                 anchor_x + radius, anchor_y + radius),
                fill=(50, 36, 28, 230),
            )
        return canvas

    if rig == "bottom_rise":
        # Translate the sprite fully below the frame before the rise begins.
        travel = height - bounds[1] + max(2, round(height * .05))
        dy = travel * (1 - ease) - overshoot * height * progress ** 6
        if elapsed >= duration:
            dy = -overshoot * height * _settle(elapsed, duration, settle_length)
        sprite = _place(source, round(dy))
        _shadow(canvas, sprite)
        canvas.alpha_composite(sprite)
        return canvas

    if rig == "rake_lift":
        # The cutout starts foreshortened at the ground and unfolds about
        # its lower pivot, like cardboard glued to a stick in a puppet theatre.
        start_angle = float(cue.get("start_rotation", 82))
        overshoot_angle = float(cue.get("overshoot_rotation", -5))
        pitch = start_angle * (1 - ease) + overshoot_angle * progress ** 6
        if elapsed >= duration:
            pitch = overshoot_angle * _settle(elapsed, duration, settle_length)
        scale_y = max(.025, math.cos(math.radians(pitch)))
        crop = source.crop(bounds)
        size = crop.size
        sprite_height = max(1, round(size[1] * scale_y))
        stretched = crop.resize((size[0], sprite_height), RESAMPLE)
        px = float(cue.get("pivot_x", .5))
        py = float(cue.get("pivot_y", 1))
        foot_x = bounds[0] + px * size[0]
        foot_y = bounds[1] + py * size[1]
        sprite = Image.new("RGBA", (width, height))
        sprite.alpha_composite(
            stretched,
            (round(bounds[0]), round(foot_y - py * sprite_height)),
        )
        # Turn a flattened cardboard standee upright around its foot.
        # The stronger sideways lean exposes the hinge instead of a pop-in.
        lean = -pitch * .22
        if lean:
            sprite = sprite.rotate(lean, resample=RESAMPLE, center=(foot_x, foot_y))
        _shadow(canvas, sprite)
        if cue.get("stick_visible", False):
            length = round(float(cue.get("stick_length", .12)) * height)
            if length > 0:
                ImageDraw.Draw(canvas).line(
                    (round(foot_x), round(foot_y), round(foot_x), round(foot_y + length)),
                    fill=(89, 62, 40, 200), width=max(1, round(width / 400)),
                )
        canvas.alpha_composite(sprite)
        return canvas

    raise ValueError("Nieznana mechanika papierowej warstwy: " + rig)


# ── Fast compositor ──────────────────────────────────────────────────────
# rig_image() above is the reference implementation and stays unchanged.
# composite_rig() writes the same pixels as
#     image.alpha_composite(rig_image(source, rig, cue, elapsed, duration), offset)
# but (1) works on the sprite's own region instead of the whole frame and
# (2) keeps per-layer work that never changes over time (alpha bounds, the
# outline) in a caller-owned memo. studio_tests/test_paper_theatre_speed.py
# compares both paths pixel by pixel. rig_motion() is the timing/geometry
# shared with the browser preview (apps/studio/src/paperTheatreMotion.ts);
# both are pinned to apps/studio/tests/fixtures/paper-theatre-motion.json.

def rig_motion(rig: str, cue: dict, elapsed: float, duration: float,
               bounds: tuple[int, int, int, int], width: int, height: int) -> dict:
    """Numbers that place one cutout at `elapsed` (same formulas as rig_image).

    `bounds` are the alpha bounds after the optional outline. Integer values
    are already rounded exactly as the renderer rounds them.
    """
    progress = _progress(elapsed, duration)
    ease = 1 - (1 - progress) ** 3
    settle_length = float(cue.get("settle_duration", .15))
    overshoot = float(cue.get("overshoot", .03))

    if rig == "hanging_drop":
        travel = bounds[3] + max(2, round(height * .06))
        dy = -travel * (1 - ease) + overshoot * height * progress ** 6
        if elapsed >= duration:
            dy = overshoot * height * _settle(elapsed, duration, settle_length)
        swing = float(cue.get("swing_deg", 3.0))
        decay = float(cue.get("swing_decay", 1.1))
        angle = swing * math.sin(elapsed * 8.0) * math.exp(-decay * elapsed)
        pivot_x = (bounds[0] + bounds[2]) / 2
        pivot_y = bounds[1] + dy
        anchor_x, anchor_y = round(pivot_x), round(pivot_y)
        string_alpha = 0
        if cue.get("string_visible", False) and anchor_y > 0:
            retract = (0.0 if "string_length" in cue else
                       _clamp((elapsed - duration) / max(.001, settle_length)))
            string_alpha = round(190 * (1 - retract))
        pin = bool(cue.get("string_visible", False) and elapsed >= duration
                   and 0 <= anchor_y < height)
        return {"dy": dy, "dy_px": round(dy), "angle": angle,
                "pivot_x": pivot_x, "pivot_y": pivot_y,
                "anchor_x": anchor_x, "anchor_y": anchor_y,
                "string_alpha": string_alpha, "pin": pin}

    if rig == "bottom_rise":
        travel = height - bounds[1] + max(2, round(height * .05))
        dy = travel * (1 - ease) - overshoot * height * progress ** 6
        if elapsed >= duration:
            dy = -overshoot * height * _settle(elapsed, duration, settle_length)
        return {"dy": dy, "dy_px": round(dy)}

    if rig == "rake_lift":
        start_angle = float(cue.get("start_rotation", 82))
        overshoot_angle = float(cue.get("overshoot_rotation", -5))
        pitch = start_angle * (1 - ease) + overshoot_angle * progress ** 6
        if elapsed >= duration:
            pitch = overshoot_angle * _settle(elapsed, duration, settle_length)
        scale_y = max(.025, math.cos(math.radians(pitch)))
        size = (bounds[2] - bounds[0], bounds[3] - bounds[1])
        sprite_height = max(1, round(size[1] * scale_y))
        px = float(cue.get("pivot_x", .5))
        py = float(cue.get("pivot_y", 1))
        foot_x = bounds[0] + px * size[0]
        foot_y = bounds[1] + py * size[1]
        stick = 0
        if cue.get("stick_visible", False):
            stick = max(0, round(float(cue.get("stick_length", .12)) * height))
        return {"pitch": pitch, "scale_y": scale_y, "sprite_height": sprite_height,
                "top": round(foot_y - py * sprite_height),
                "foot_x": foot_x, "foot_y": foot_y, "lean": -pitch * .22,
                "stick": stick}

    raise ValueError("Nieznana mechanika papierowej warstwy: " + rig)


def _clip_box(box, width, height):
    return (max(0, box[0]), max(0, box[1]), min(width, box[2]), min(height, box[3]))


def _grow(box, margin):
    return (box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin)


def _empty(box) -> bool:
    return box is None or box[2] <= box[0] or box[3] <= box[1]


def _union(*boxes):
    boxes = [box for box in boxes if not _empty(box)]
    if not boxes:
        return None
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def _rotated_box(box, angle: float, center: tuple[float, float]):
    """Integer box containing `box` rotated either way around `center`."""
    cx, cy = center
    rad = math.radians(angle)
    c, s = math.cos(rad), abs(math.sin(rad))
    xs, ys = [], []
    for x in (box[0], box[2]):
        for y in (box[1], box[3]):
            dx, dy = x - cx, y - cy
            for sign in (-1, 1):
                xs.append(cx + dx * c + sign * dy * s)
                ys.append(cy - sign * dx * s + dy * c)
    return (math.floor(min(xs)), math.floor(min(ys)), math.ceil(max(xs)), math.ceil(max(ys)))


def _prepare(source: Image.Image, cue: dict):
    """(sprite, bounds): the visible cutout after the optional outline.

    Constant for a layer, so composite_rig() computes it once per render.
    The outline is taken on a crop with a transparent margin wider than the
    filter, which yields the same pixels as filtering the whole frame.
    """
    bounds = _bbox(source)
    if bounds is None:
        return None, None
    stroke = int(cue["outline_px"]) if cue.get("outline_px") else 0
    if stroke <= 0:
        return source.crop(bounds), bounds
    width, height = source.size
    region = _clip_box(_grow(bounds, stroke + 2), width, height)
    outlined = _outlined(source.crop(region), stroke, cue.get("outline_color", "#362820"))
    local = outlined.getchannel("A").getbbox()
    bounds = (region[0] + local[0], region[1] + local[1],
              region[0] + local[2], region[1] + local[3])
    return outlined.crop(local), bounds


def _placed(sprite: Image.Image, at: tuple[int, int], region) -> Image.Image:
    """The frame-sized `_place` result, restricted to `region`."""
    canvas = Image.new("RGBA", (region[2] - region[0], region[3] - region[1]))
    canvas.alpha_composite(sprite, (at[0] - region[0], at[1] - region[1]))
    return canvas


_SHADOW_LUT = [round(value * .2) for value in range(256)]  # same table point() builds


def _shadow_box(region, width: int, height: int):
    blur = max(1.0, width * .003)
    return _clip_box(_grow(region, math.ceil(3 * (blur + 2)) + 4), width, height)


def _shadow_into(canvas: Image.Image, origin, sprite: Image.Image, region,
                 shade_box, width: int, height: int) -> None:
    """_shadow() limited to the sprite region plus the blur's reach."""
    blur = max(1.0, width * .003)
    alpha = Image.new("L", (shade_box[2] - shade_box[0], shade_box[3] - shade_box[1]))
    alpha.paste(sprite.getchannel("A"), (region[0] - shade_box[0], region[1] - shade_box[1]))
    alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
    alpha = alpha.point(_SHADOW_LUT)
    shade = Image.new("RGBA", alpha.size, (40, 26, 17, 0))
    shade.putalpha(alpha)
    canvas.alpha_composite(shade, (
        shade_box[0] + max(1, round(width * .003)) - origin[0],
        shade_box[1] + max(1, round(height * .005)) - origin[1]))


def _shadow_reach(shade_box, width: int, height: int):
    offset_x, offset_y = max(1, round(width * .003)), max(1, round(height * .005))
    return _clip_box((shade_box[0] + offset_x, shade_box[1] + offset_y,
                      shade_box[2] + offset_x, shade_box[3] + offset_y), width, height)


def _draw_rig(rig, sprite, bounds, motion, width, height):
    """Return (layer, box): the non-transparent part of rig_image's canvas."""
    if rig in ("hanging_drop", "bottom_rise"):
        dy = motion["dy_px"]
        placed = (bounds[0], bounds[1] + dy, bounds[2], bounds[3] + dy)
        angle = motion.get("angle", 0)
        center = (motion.get("pivot_x", 0), motion.get("pivot_y", 0))
        at = (bounds[0], bounds[1] + dy)
        source = sprite
    else:  # rake_lift
        source = sprite.resize((sprite.width, motion["sprite_height"]), RESAMPLE)
        at = (bounds[0], motion["top"])
        placed = (at[0], at[1], at[0] + source.width, at[1] + source.height)
        angle = motion["lean"]
        center = (motion["foot_x"], motion["foot_y"])
    if angle:
        region = _clip_box(_grow(_union(placed, _rotated_box(placed, angle, center)), 4), width, height)
    else:
        region = _clip_box(placed, width, height)
    moved = None
    if not _empty(region):
        moved = _placed(source, at, region)
        if angle:
            moved = moved.rotate(angle, resample=RESAMPLE,
                                 center=(center[0] - region[0], center[1] - region[1]))
    shade_box = _shadow_box(region, width, height) if moved is not None else None

    extras = []
    if rig == "hanging_drop":
        line = max(2, round(width / 720))
        ax, ay = motion["anchor_x"], motion["anchor_y"]
        if motion["string_alpha"] > 0:
            extras.append((ax - line - 2, 0, ax + line + 3, min(height - 1, ay) + line + 3))
        if motion["pin"]:
            radius = max(2, round(width / 480))
            extras.append((ax - radius - 2, ay - radius - 2, ax + radius + 3, ay + radius + 3))
    if rig == "rake_lift" and motion["stick"] > 0:
        line = max(1, round(width / 400))
        fx, fy = round(motion["foot_x"]), round(motion["foot_y"])
        extras.append((fx - line - 2, fy - line - 2, fx + line + 3,
                       round(motion["foot_y"] + motion["stick"]) + line + 3))
    box = _union(region if moved is not None else None,
                 _shadow_reach(shade_box, width, height) if shade_box else None,
                 *[_clip_box(extra, width, height) for extra in extras])
    if _empty(box):
        return None, None
    box = _clip_box(box, width, height)
    canvas = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]))
    if moved is not None:
        _shadow_into(canvas, box, moved, region, shade_box, width, height)
    draw = ImageDraw.Draw(canvas)
    if rig == "hanging_drop" and motion["string_alpha"] > 0:
        ax, ay = motion["anchor_x"] - box[0], motion["anchor_y"]
        draw.line((ax, -box[1], ax, min(height - 1, ay) - box[1]),
                  fill=(62, 49, 38, motion["string_alpha"]),
                  width=max(2, round(width / 720)))
    if rig == "rake_lift" and motion["stick"] > 0:
        fx, fy = round(motion["foot_x"]) - box[0], round(motion["foot_y"]) - box[1]
        draw.line((fx, fy, fx, round(motion["foot_y"] + motion["stick"]) - box[1]),
                  fill=(89, 62, 40, 200), width=max(1, round(width / 400)))
    if moved is not None:
        canvas.alpha_composite(moved, (region[0] - box[0], region[1] - box[1]))
    if rig == "hanging_drop" and motion["pin"]:
        radius = max(2, round(width / 480))
        ax, ay = motion["anchor_x"] - box[0], motion["anchor_y"] - box[1]
        ImageDraw.Draw(canvas).ellipse((ax - radius, ay - radius, ax + radius, ay + radius),
                                       fill=(50, 36, 28, 230))
    return canvas, box


def composite_rig(image: Image.Image, source, rig: str, cue: dict, elapsed: float,
                  duration: float, offset: tuple[int, int] = (0, 0), memo: dict | None = None,
                  size: tuple[int, int] | None = None) -> None:
    """Composite one rigged cutout onto `image` (see the block comment above).

    `source` is the full-frame layer or a zero-argument callable returning it;
    it is only materialised when the memo has no prepared sprite yet.
    `memo` must be private to one layer (same source pixels and cue).
    """
    if elapsed < 0:
        return
    memo = {} if memo is None else memo
    if "prep" not in memo:
        layer = source() if callable(source) else source
        memo["size"] = layer.size
        memo["prep"] = _prepare(layer, cue)
    sprite, bounds = memo["prep"]
    if sprite is None:
        return
    width, height = size or memo["size"]
    if rig == "static":
        image.alpha_composite(sprite, (offset[0] + bounds[0], offset[1] + bounds[1]))
        return
    motion = rig_motion(rig, cue, elapsed, duration, bounds, width, height)
    state = tuple(sorted(motion.items()))
    last = memo.get("last")
    if last is not None and last[0] == state:
        layer, box = last[1], last[2]
    else:
        layer, box = _draw_rig(rig, sprite, bounds, motion, width, height)
        memo["last"] = (state, layer, box)
    if layer is not None:
        image.alpha_composite(layer, (offset[0] + box[0], offset[1] + box[1]))
