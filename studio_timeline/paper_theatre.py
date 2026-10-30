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
            retract = _clamp((elapsed - duration) / max(.001, settle_length))
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
