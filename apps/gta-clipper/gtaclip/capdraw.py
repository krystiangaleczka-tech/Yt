"""Captions drawn in code (Pillow) — used when ffmpeg has no libass ("ass" filter).

The same events as the libass path (captions.caption_events) are drawn into transparent
1080x1920 PNGs, one per on-screen state, and handed to ffmpeg as an image sequence with
exact durations (concat demuxer). ffmpeg then only overlays them — no text rendering needed.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .captions import THEMES

W, H = 1080, 1920
STEP = 1 / 30
FONT_FILES = {
    "Poppins Black": "Poppins-Black.ttf", "Anton": "Anton-Regular.ttf", "Bangers": "Bangers-Regular.ttf",
    "Luckiest Guy": "LuckiestGuy-Regular.ttf", "Bebas Neue": "BebasNeue-Regular.ttf",
}
SYSTEM_BOLD = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def _rgba(hex_color: str, opacity: float = 1.0) -> tuple[int, int, int, int]:
    c = hex_color.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(round(255 * opacity))


@lru_cache(maxsize=32)
def _ass_metrics(path: str) -> tuple[float, float] | None:
    """(unitsPerEm / (usWinAscent + usWinDescent), usWinAscent / (usWinAscent + usWinDescent)).

    libass sizes a font so that winAscent + winDescent = ASS font size (that is also its line box),
    Pillow sizes by the em — this converts between them and gives the baseline inside the line box."""
    import struct

    try:
        data = Path(path).read_bytes()
        n = struct.unpack(">H", data[4:6])[0]
        tables = {data[12 + 16 * i:16 + 16 * i]: struct.unpack(">I", data[20 + 16 * i:24 + 16 * i])[0] for i in range(n)}
        upem = struct.unpack(">H", data[tables[b"head"] + 18:tables[b"head"] + 20])[0]
        os2 = tables[b"OS/2"]
        win_asc, win_desc = struct.unpack(">HH", data[os2 + 74:os2 + 78])
        tot = win_asc + win_desc
        return (upem / tot, win_asc / tot) if tot else None
    except (OSError, KeyError, struct.error):
        return None


@lru_cache(maxsize=256)
def _font(fonts_dir: str, family: str, ass_size: float):
    """(Pillow font, line height, baseline offset) matching libass at the same ASS font size."""
    from PIL import ImageFont

    path = Path(fonts_dir) / FONT_FILES.get(family, "Poppins-Black.ttf")
    cands = [str(path)] + [p for p in SYSTEM_BOLD if Path(p).exists()]
    for p in cands:
        if Path(p).exists():
            m = _ass_metrics(p)
            if m is None:  # fall back to hhea metrics
                asc, desc = ImageFont.truetype(p, 100).getmetrics()
                m = (100 / (asc + desc), asc / (asc + desc))
            return ImageFont.truetype(p, max(6, round(ass_size * m[0]))), ass_size, ass_size * m[1]
    f = ImageFont.load_default()
    return f, ass_size, ass_size * 0.8


def _tw(font, text: str, sp: float) -> float:
    """Text width with ASS letter spacing (extra pixels after every character)."""
    return font.getlength(text) + sp * len(text)


def _wrap(words: list[tuple[str, tuple]], font, max_w: float, sp: float = 0) -> list[list[tuple[str, tuple]]]:
    space = _tw(font, " ", sp)
    lines, cur, cur_w = [], [], 0.0
    for t, col in words:
        w = _tw(font, t, sp)
        if cur and cur_w + space + w > max_w:
            lines.append(cur)
            cur, cur_w = [], 0.0
        cur_w += (space if cur else 0) + w
        cur.append((t, col))
    if cur:
        lines.append(cur)
    return lines


def _draw_block(img, words, fm, cy: float, *, stroke=0, stroke_col=None, shadow=0, shadow_col=None,
                box_col=None, box_pad=0, max_w=W - 120, bottom: float | None = None, spacing: float = 0):
    """Centered block of coloured words (alignment 5 like the ASS styles; `bottom` = alignment 2)."""
    from PIL import Image, ImageDraw

    font, lh, asc = fm
    sp = spacing
    lines = _wrap(words, font, max_w, sp)
    space = _tw(font, " ", sp)
    total = lh * len(lines)
    top = (bottom - total) if bottom is not None else cy - total / 2
    layer_box = Image.new("RGBA", img.size)
    layer_shadow = Image.new("RGBA", img.size)
    layer_stroke = Image.new("RGBA", img.size)
    layer_fill = Image.new("RGBA", img.size)
    db, ds, dst, df = (ImageDraw.Draw(x) for x in (layer_box, layer_shadow, layer_stroke, layer_fill))
    for n, line in enumerate(lines):
        lw = sum(_tw(font, t, sp) for t, _ in line) + space * (len(line) - 1)
        x = W / 2 - lw / 2
        y = top + n * lh
        base = y + asc
        if box_col:  # like libass BorderStyle 3: line box grown by the border on every side
            db.rectangle([x - box_pad, y - box_pad, x + lw + box_pad, y + lh + box_pad], fill=box_col)
        for t, col in line:
            # with letter spacing each character is placed on its own; without it whole words keep kerning
            pieces = [(c, font.getlength(c) + sp) for c in t] if sp else [(t, font.getlength(t))]
            for piece, adv in pieces:
                if shadow and not box_col:
                    ds.text((x + shadow, base + shadow), piece, font=font, fill=shadow_col, stroke_width=stroke,
                            stroke_fill=shadow_col, anchor="ls")
                if stroke and not box_col:
                    dst.text((x, base), piece, font=font, fill=stroke_col, stroke_width=stroke, stroke_fill=stroke_col,
                             anchor="ls")
                df.text((x, base), piece, font=font, fill=col, anchor="ls")
                x += adv
            x += space
    for layer in (layer_box, layer_shadow, layer_stroke, layer_fill):
        img.alpha_composite(layer)


def _scale(kind: str, t: float) -> float:
    """Scale animation at time t since the element appeared (mirrors the \\t tags of the ASS path)."""
    if kind == "hook":
        if t < 0.14:
            return 0.6 + (1.04 - 0.6) * t / 0.14
        if t < 0.22:
            return 1.04 + (1.0 - 1.04) * (t - 0.14) / 0.08
        return 1.0
    if kind == "pop":
        return 1.12 + (1.0 - 1.12) * t / 0.09 if t < 0.09 else 1.0
    return 1.0


def draw_state(state: tuple, events: list[dict], theme: dict, accent: str, fonts_dir: str):
    from PIL import Image

    img = Image.new("RGBA", (W, H))
    for idx, sc in state:
        e = events[idx]
        if e["kind"] == "hook":
            fm = _font(fonts_dir, "Poppins Black", 78 * sc)
            lh = fm[1]
            for k, ln in enumerate(e["lines"]):  # one box per line, lines stacked like \N
                cy = e["y"] - lh * (len(e["lines"]) - 1) / 2 + k * lh
                _draw_block(img, [(ln, _rgba("#111111"))], fm, cy, box_col=_rgba(accent), box_pad=22 * sc,
                            max_w=10_000)
        elif e["kind"] == "mark":
            fm = _font(fonts_dir, "Poppins Black", 40)
            _draw_block(img, [(e["text"], _rgba("#FFFFFF", 0.6))], fm, 0, stroke=2, stroke_col=_rgba("#000000", 0.4),
                        bottom=H - 70, spacing=1)
        else:
            fm = _font(fonts_dir, theme["font"], theme["size"] * sc)
            words = [(t, _rgba(c)) for t, c in e["parts"]]
            box = theme.get("box")
            _draw_block(img, words, fm, e["y"], stroke=theme["ow"], stroke_col=_rgba(theme["outline"]),
                        shadow=theme["shadow"], shadow_col=_rgba("#000000", 0.41),
                        box_col=_rgba(box) if box else None, box_pad=theme["ow"], spacing=sc)
    return img


def build_layer(events: list[dict], duration: float, theme_name: str, accent: str, fonts_dir: Path,
                out_dir: Path) -> Path | None:
    """Render all states to PNGs + an ffconcat list. Returns the list path (None if nothing to show)."""
    if not events:
        return None
    theme = THEMES.get(theme_name, THEMES["classic"])
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    # breakpoints: every start/end plus animation sub-steps
    pts = {0.0, round(duration, 3)}
    for e in events:
        pts.update((round(e["start"], 3), round(min(e["end"], duration), 3)))
        anim = 0.22 if e["kind"] == "hook" else 0.09 if e.get("pop") else 0
        k = 1
        while anim and k * STEP < anim:
            pts.add(round(e["start"] + k * STEP, 3))
            k += 1
        if anim:
            pts.add(round(e["start"] + anim, 3))
    pts = sorted(p for p in pts if 0 <= p <= duration)
    files: dict[tuple, str] = {}
    entries: list[tuple[str, float]] = []
    for a, b in zip(pts, pts[1:]):
        if b - a < 1e-3:
            continue
        mid = (a + b) / 2
        state = []
        for i, e in enumerate(events):
            if e["start"] <= mid < e["end"]:
                kind = "hook" if e["kind"] == "hook" else "pop" if e.get("pop") else "none"
                state.append((i, round(_scale(kind, a - e["start"]), 3)))
        key = tuple(state)
        if key not in files:
            name = f"s{len(files):04d}.png"
            draw_state(key, events, theme, accent, str(fonts_dir)).save(out_dir / name, compress_level=1)
            files[key] = name
        if entries and entries[-1][0] == files[key]:
            entries[-1] = (files[key], entries[-1][1] + (b - a))
        else:
            entries.append((files[key], b - a))
    lst = out_dir / "caps.txt"
    body = ["ffconcat version 1.0"]
    for name, d in entries:
        body += [f"file '{name}'", f"duration {d:.4f}"]
    body.append(f"file '{entries[-1][0]}'")  # the concat demuxer needs the last image repeated
    lst.write_text("\n".join(body) + "\n", encoding="utf-8")
    return lst
