"""Physical-looking, deterministic paper-cut entrance rigs.

All inputs use pre-cut transparent PNG layers placed on the final canvas.
No model, random physics, or frame-to-frame state is required, so arbitrary
preview frames and cached render segments have identical geometry.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

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
    if rig == "static":
        return source.copy()

    progress = _progress(elapsed, duration)
    ease = 1 - (1 - progress) ** 3
    settle_length = float(cue.get("settle_duration", .15))
    overshoot = float(cue.get("overshoot", .03))

    if rig == "hanging_drop":
        # At t=0 the whole cutout is above the top edge, not merely faded out.
        travel = bounds[3] + max(2, round(height * .06))
        dy = -travel * (1 - ease) + overshoot * height * progress ** 6
        if elapsed >= duration:
            dy = overshoot * height * _settle(elapsed, duration, settle_length)
        sprite = _place(source, round(dy))
        swing = float(cue.get("swing_deg", 2.0))
        decay = float(cue.get("swing_decay", .7))
        angle = swing * math.sin(elapsed * 7.0) * math.exp(-decay * elapsed)
        pivot_x = (bounds[0] + bounds[2]) / 2
        pivot_y = bounds[1] + dy
        if angle:
            sprite = sprite.rotate(angle, resample=RESAMPLE, center=(pivot_x, pivot_y))
        _shadow(canvas, sprite)
        if cue.get("string_visible", False):
            # The thread is subtle and sits behind the paper, not over it.
            end_y = round(pivot_y)
            end_x = round(pivot_x)
            span = round(float(cue.get("string_length", .16)) * height)
            if span > 0 and end_y > 0:
                ImageDraw.Draw(canvas).line(
                    (end_x, max(0, end_y - span), end_x, end_y + 1),
                    fill=(80, 66, 51, 115), width=max(1, round(width / 900)),
                )
        canvas.alpha_composite(sprite)
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
        # A small sideways lean suggests the cutout is settling on its base.
        lean = -pitch * .09
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
