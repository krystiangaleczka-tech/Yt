"""Montaż dokumentu z prawdziwymi materiałami: render_plan.json + media + lektor per beat -> MP4.

    ../pilot/.venv/bin/python -I render_doc.py PLAN.json --media DIR [--media DIR2 ...] --voice VOICE_DIR \
        --out film.mp4 [--lead B01=3.0] [--tail B11=6] [--cue B01:start:bloop.wav:1.0:10] [--credits licenses.json ...]

Ujęcia w shot liście wskazują pliki przez `FILE: nazwa` (porównanie: `FILES: a | b`), podpis przez `CAPTION: "..."`.
Szybkie cięcia (< 2 s) nie są rozciągane — nadmiar czasu lektora dostają tylko dłuższe ujęcia.
Audio (podkład, efekty, prawdziwe nagrania, lektor) miksowane jest w numpy, z przyciszaniem pod lektorem.
"""
import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # python -I nie dodaje katalogu skryptu

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageEnhance

import render_film as R  # wspólne narzędzia: fonty, spektrogramy, mapy, tytuły, karty

W, H, FPS, SR = R.W, R.H, R.FPS, 48000
MONO, MONO_B, SANS, ease, quoted = R.MONO, R.MONO_B, R.SANS, R.ease, R.quoted
VIDEO_EXT = {".webm", ".ogv", ".mp4", ".mov", ".mkv"}
FAST = 2.0  # ujęcia krótsze niż tyle sekund nie są rozciągane


# ───────────── media ─────────────

class Media:
    def __init__(self, dirs):
        self.index = {}
        for d in dirs:
            for p in Path(d).rglob("*"):
                if p.is_file():
                    self.index.setdefault(p.name, p)

    def __call__(self, name):
        p = self.index.get(name.strip())
        if not p:
            raise SystemExit(f"Brak pliku w mediach: {name}")
        return p


def field(desc, key):
    m = re.search(rf'{key}:\s*"?([^"(]+?)"?\s*(?=\b[A-Z]+:|\(|$)', desc)
    return m.group(1).strip() if m else ""


def caption_of(desc, framing, asset):
    c = re.search(r'CAPTION:\s*"([^"]+)"', desc)
    if c:
        return c.group(1)
    if asset == "AI_OBRAZ" or "REKONSTRUKCJA" in framing.upper():
        return "AI reconstruction"
    return ""


def add_caption(img, text):
    if not text:
        return img
    d = ImageDraw.Draw(img, "RGBA")
    f = MONO(30)
    tw = d.textlength(text, font=f)
    d.rectangle((48, H - 98, 48 + tw + 32, H - 50), fill=(0, 0, 0, 150))
    d.text((64, H - 92), text, font=f, fill=(220, 220, 210, 255))
    return img


def grade(im, color=0.3):
    im = ImageEnhance.Color(im.convert("RGB")).enhance(color)
    return ImageEnhance.Contrast(im).enhance(1.08)


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def photo_shot(path, k, cap):
    src = grade(Image.open(path))
    z0, z1, dx, dy = R.MOVES[k % len(R.MOVES)]
    if src.width < 900:  # mały skan -> "dokument na stole"
        desk = Image.new("RGB", (int(W * 1.1), int(H * 1.1)), (16, 16, 15))
        s = min(1300 / src.width, 700 / src.height, 3.2)
        card = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
        sh = Image.new("RGBA", (card.width + 60, card.height + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((30, 40, card.width + 30, card.height + 40), fill=(0, 0, 0, 170))
        x, y = (desk.width - card.width) // 2, (desk.height - card.height) // 2
        desk.paste(sh, (x - 30, y - 30), sh)
        desk.paste(card, (x, y))
        big, z0, z1, dx, dy = desk, 1.0, 1.06, dx * 0.3, dy * 0.3
    else:
        big = cover(src, int(W * 1.15), int(H * 1.15))

    def f(t, dur):
        return add_caption(R.ken_burns(big, t / dur, z0, z1, dx, dy), cap)
    f.still = big.resize((W, H))
    return f


class VideoShot:
    def __init__(self, path, start, cap):
        self.path, self.start, self.cap = path, start, cap
        self.proc, self.idx, self.last = None, -1, None
        self.still = Image.new("RGB", (W, H))

    def _open(self):
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
              "hue=s=0,eq=contrast=1.1")
        self.proc = subprocess.Popen(
            ["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-ss", f"{self.start:.2f}", "-i", str(self.path),
             "-vf", vf, "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

    def __call__(self, t, dur):
        target = min(int(t * FPS), int(dur * FPS) - 1)
        if self.proc is None and (self.last is None or target > self.idx):
            self._open()
        while self.idx < target and self.proc:
            buf = self.proc.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            self.last = Image.frombytes("RGB", (W, H), buf)
            self.idx += 1
            if self.idx == 0:
                self.still = self.last
        if self.idx >= int(dur * FPS) - 1 and self.proc:
            self.proc.kill()
            self.proc = None
        img = (self.last or self.still).copy()
        return add_caption(img, self.cap)


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if d.textlength(nxt, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = nxt
    return lines + [cur] if cur else lines


def press_shot(desc):
    q = quoted(desc)[0]
    src = desc.split("—", 1)[-1].strip() if "—" in desc else ""
    pub, _, date = src.partition(",")
    CW, CH = 1500, 700
    card = Image.new("RGB", (CW, CH), (236, 232, 220))
    d = ImageDraw.Draw(card)
    d.text((70, 50), " ".join(pub.upper()), font=SANS(50), fill=(20, 20, 20))
    d.text((72, 120), date.strip(), font=MONO(32), fill=(90, 90, 85))
    d.line((70, 175, CW - 70, 175), fill=(30, 30, 30), width=3)
    fq = MONO_B(50 if len(q) < 90 else 42)
    lines = wrap(d, f"“{q}”", fq, CW - 160)
    lh = fq.size + 18
    y0 = 230
    d.text((70, CH - 60), "Quoted from the original article", font=MONO(24), fill=(120, 120, 115))

    def f(t, dur):
        c = card.copy()
        cd = ImageDraw.Draw(c, "RGBA")
        sweep = ease((t - 0.35) / 1.3)  # marker przejeżdża po cytacie
        total = sum(cd.textlength(l, font=fq) for l in lines)
        done = sweep * total
        for i, l in enumerate(lines):
            lw = cd.textlength(l, font=fq)
            hw = max(0.0, min(lw, done))
            done -= lw
            if hw > 0:
                cd.rectangle((66, y0 + i * lh + 6, 74 + hw, y0 + i * lh + fq.size + 10), fill=(250, 220, 60, 150))
            cd.text((70, y0 + i * lh), l, font=fq, fill=(15, 15, 15))
        bg = Image.new("RGB", (int(W * 1.1), int(H * 1.1)), (18, 18, 17))
        rc = c.rotate(-1.2, expand=True, resample=Image.BICUBIC, fillcolor=(18, 18, 17))
        a = ease(t / 0.35)
        bg.paste(rc, ((bg.width - rc.width) // 2, (bg.height - rc.height) // 2 + int((1 - a) * 60)))
        return R.ken_burns(bg, t / dur, 1.0, 1.07)
    f.still = Image.new("RGB", (W, H), (18, 18, 17))
    return f


def lower_third(desc, bgf):
    name, _, role = quoted(desc)[0].partition("/")

    def f(t, dur):
        img = Image.eval(bgf(t, dur), lambda v: int(v * 0.6))
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(380):  # ciemny pas pod belką
            d.line((0, H - 380 + i, W, H - 380 + i), fill=(0, 0, 0, int(235 * min(1, i / 120))))
        a = ease((t - 0.3) / 0.5)
        x = 130 - int((1 - a) * 80)
        d.rectangle((x, H - 330, x + 14, H - 170), fill=(190, 30, 30))
        c = int(240 * a)
        d.text((x + 44, H - 335), name.strip(), font=SANS(72), fill=(c, c, c))
        d.text((x + 48, H - 240), role.strip(), font=MONO(36), fill=(int(c * .85),) * 3)
        return img
    f.still = bgf.still
    return f


def timeline_shot(desc):
    labels = [s.strip() for s in quoted(desc)[0].split("/")]

    def f(t, dur):
        img = Image.new("RGB", (W, H), (10, 10, 10))
        d = ImageDraw.Draw(img)
        x0, x1, y = 220, W - 220, H // 2
        p = t / dur
        d.line((x0, y, x0 + (x1 - x0) * ease(p * 1.6), y), fill=(200, 200, 190), width=4)
        for i, lab in enumerate(labels):
            x = x0 + (x1 - x0) * i / max(len(labels) - 1, 1)
            a = ease((p - 0.1 - i * 0.18) / 0.12)
            if a <= 0:
                continue
            col = (200, 40, 40) if i == len(labels) - 1 else (235, 235, 225)
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=col)
            tw = d.textlength(lab, font=MONO_B(64))
            d.text((x - tw / 2, y + 40), lab, font=MONO_B(64), fill=tuple(int(v * a) for v in col))
        return img
    f.still = Image.new("RGB", (W, H), (10, 10, 10))
    return f


def ne_pacific_map():
    """Ilustracyjna mapa NE Pacyfiku: grzbiet Juan de Fuca i Whidbey Island (w przybliżeniu)."""
    bg = R.grid_bg()
    d = ImageDraw.Draw(bg)
    lon0, lon1, lat0, lat1 = -136, -118, 40, 50.5
    P = lambda lon, lat: ((lon - lon0) / (lon1 - lon0) * W, (lat1 - lat) / (lat1 - lat0) * H)  # noqa: E731
    coast = [(-124.2, 40), (-124.4, 42), (-124.1, 44), (-123.95, 46), (-124.2, 47.5), (-124.7, 48.38),
             (-123.2, 48.15), (-122.6, 47.2), (-122.3, 48.9), (-118, 49.0), (-118, 40)]
    d.polygon([P(*c) for c in coast], fill=(40, 42, 44))
    for lab, (lo, la) in {"OREGON": (-121.5, 44), "WASHINGTON": (-120.8, 47.3), "PACIFIC OCEAN": (-134, 42.5)}.items():
        d.text(P(lo, la), lab, font=MONO_B(42), fill=(150, 150, 140))
    ridge = [P(-130.6, 44.4), P(-130.0, 45.9), P(-129.6, 47.0), P(-129.0, 48.5)]
    wh = P(-122.6, 48.3)

    def f(t, dur):
        fr = bg.copy()
        dd = ImageDraw.Draw(fr)
        g = ease(t / (dur * 0.5))
        n = max(2, int(len(ridge) * g + 0.999))
        dd.line(ridge[:n], fill=(210, 40, 40), width=8)
        if g > 0.6:
            dd.text((ridge[1][0] + 30, ridge[1][1]), "JUAN DE FUCA RIDGE", font=MONO_B(40), fill=(235, 235, 225))
        if t > dur * 0.35:
            dd.ellipse((wh[0] - 12, wh[1] - 12, wh[0] + 12, wh[1] + 12), fill=(235, 235, 225))
            dd.text((wh[0] - 380, wh[1] - 70), "WHIDBEY ISLAND", font=MONO_B(36), fill=(235, 235, 225))
        return add_caption(R.ken_burns(fr.resize((int(W * 1.1), int(H * 1.1))), t / dur, 1.0, 1.06), "Map approximate")
    f.still = bg
    return f


def compare_files(desc, media):
    labels = (quoted(desc) + ["", ""])[:2]
    files = [x.strip() for x in field(desc, "FILES").split("|")]
    CW, CH = 660, 420
    cards = [R.rounded(grade(Image.open(media(fn))), CW, CH) for fn in files]

    def f(t, dur):
        fr = Image.new("RGB", (W, H), (8, 8, 8))
        d = ImageDraw.Draw(fr)
        d.rectangle((W // 2, 0, W, H), fill=R.BORDO)
        for i, (img, mask) in enumerate(cards):
            a = ease((t - 0.1 - 0.3 * i) / 0.4)
            if a <= 0:
                continue
            cx = W // 4 if i == 0 else 3 * W // 4
            y = int(H / 2 - CH / 2 - 70 + (1 - a) * 40)
            fr.paste(img, (cx - CW // 2, y), mask.point(lambda v: int(v * a)))
            main, _, sub = labels[i].partition("—")
            c = int(235 * a)
            sp = " ".join(main.strip())
            tw = d.textlength(sp, font=SANS(44))
            d.text((cx - tw / 2, H / 2 + CH / 2 - 40), sp, font=SANS(44), fill=(c, c, c))
            if sub.strip():
                tw2 = d.textlength(sub.strip(), font=MONO(34))
                d.text((cx - tw2 / 2, H / 2 + CH / 2 + 30), sub.strip(), font=MONO(34), fill=(int(c * .8),) * 3)
        return R.ken_burns(fr.resize((int(W * 1.1), int(H * 1.1))), t / dur, 1.0, 1.04)
    f.still = Image.new("RGB", (W, H), (8, 8, 8))
    return f


def cards(desc):
    words = [w.strip() for w in desc.split("cards", 1)[-1].split("/")]
    guess = "guess" in desc.lower()

    def f(t, dur):
        i = min(int(t / dur * len(words)), len(words) - 1)
        fr = Image.new("RGB", (W, H), R.BORDO if i % 2 else (10, 10, 10))
        d = ImageDraw.Draw(fr)
        txt = " ".join(words[i])
        tw = d.textlength(txt, font=SANS(120))
        d.text(((W - tw) / 2, H / 2 - 80), txt, font=SANS(120), fill=(235, 235, 230))
        if guess:
            d.text((W / 2 - 90, H / 2 + 90), "GUESS?", font=MONO(44), fill=(190, 190, 185))
        return fr
    f.still = Image.new("RGB", (W, H), (10, 10, 10))
    f.n_cards = len(words)
    return f


# ───────────── ujęcia objaśniające (v4) ─────────────

def floats(desc, key):
    m = re.search(rf"{key}:\s*([\d.,\s]+)", desc)
    return [float(x) for x in m.group(1).replace(" ", "").split(",") if x] if m else []


def waveform_shot(desc, media):
    path = media(field(desc, "FILE"))
    x = load_audio(path)
    start = (floats(desc, "START") or [0.0])[0]
    label = (quoted(desc) or [""])[0]
    grid = R.grid_bg()

    def f(t, dur):
        img = grid.copy()
        d = ImageDraw.Draw(img)
        i0 = int(((start + t) % (x.size / SR)) * SR)
        win = x[i0: i0 + int(0.6 * SR)]
        if win.size < 10:
            win = x[: int(0.6 * SR)]
        step = max(1, win.size // W)
        pts = win[::step][:W]
        amp = 380 / (np.abs(x).max() + 1e-6)
        d.line([(i, H / 2 - v * amp) for i, v in enumerate(pts)], fill=(235, 235, 225), width=3)
        d.line((0, H / 2, W, H / 2), fill=(70, 70, 70))
        d.text((120, 100), label, font=MONO_B(54), fill=(235, 235, 225))
        return add_caption(img, "Real recording — NOAA PMEL")
    f.still = grid
    return f


def spectro_live(desc, media):
    """Spektrogram PRAWDZIWEGO nagrania odsłaniany w czasie rzeczywistym (zsynchronizowany z odtwarzanym dźwiękiem)."""
    path = media(field(desc, "FILE"))
    sr = 4000
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-ac", "1", "-ar", str(sr), tmp.name], check=True)
        x, _ = sf.read(tmp.name, dtype="float32")
    start = (floats(desc, "START") or [0.0])[0]
    span = (floats(desc, "SPAN") or [8.0])[0]
    maxhz = (floats(desc, "MAXHZ") or [700])[0]
    seg = x[int(start * sr): int((start + span) * sr)]
    n, hop = 512, 32
    win = np.hanning(n)
    frames = np.stack([seg[i:i + n] * win for i in range(0, max(seg.size - n, 1), hop)])
    spec = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)).T + 1e-7)
    spec = spec[: int(spec.shape[0] * maxhz / (sr / 2))][::-1]
    lo, hi = np.percentile(spec, 40), np.percentile(spec, 99.7)
    spec = np.clip((spec - lo) / (hi - lo), 0, 1) ** 1.2
    PW, PH = 1600, 720
    strip = Image.fromarray((spec * 255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC).convert("RGB")
    label = (quoted(desc) or [""])[0]
    base = Image.new("RGB", (W, H), (10, 10, 10))
    d0 = ImageDraw.Draw(base)
    d0.text((160, 110), label, font=MONO_B(50), fill=(235, 235, 225))
    for i in range(0, int(maxhz) + 1, 100 if maxhz <= 800 else 250):
        y = 200 + PH - PH * i / maxhz
        d0.text((60, y - 14), f"{i}", font=MONO(24), fill=(140, 140, 130))
    d0.text((160, 940), "time ->", font=MONO(30), fill=(150, 150, 140))

    def f(t, dur):
        img = base.copy()
        cut = int(PW * min(t / span, 1.0))
        if cut > 0:
            img.paste(strip.crop((0, 0, cut, PH)), (160, 200))
        d = ImageDraw.Draw(img)
        d.line((160 + cut, 195, 160 + cut, 925), fill=(210, 40, 40), width=3)
        return add_caption(img, "Spectrogram of the real recording (Hz) — NOAA PMEL")
    f.still = base
    return f


def lupa_shot(desc, media):
    src = grade(Image.open(media(field(desc, "FILE"))))
    zx, zy, zw = (floats(desc, "ZOOM") + [0.4, 0.4, 0.3])[:3]
    label = (quoted(desc) or [""])[0]
    big = cover(src, W, H)
    full = (0, 0, W, H)
    zh = zw * H / W * W / W
    box = (zx * W, zy * H, (zx + zw) * W, (zy + zw) * H)

    def f(t, dur):
        p = t / dur
        img = big.copy()
        d = ImageDraw.Draw(img, "RGBA")
        if p < 0.35:
            a = ease(p / 0.2)
            d.rectangle(box, outline=(230, 40, 40, int(255 * a)), width=6)
            return img
        z = ease((p - 0.35) / 0.4)
        crop = tuple(full[i] + (box[i] - full[i]) * z for i in range(4))
        cw, ch = crop[2] - crop[0], crop[3] - crop[1]
        cy = crop[1] + ch / 2  # utrzymaj proporcje 16:9
        ch = cw * H / W
        out = big.resize((W, H), Image.LANCZOS, box=(crop[0], cy - ch / 2, crop[2], cy + ch / 2))
        if z > 0.95 and label:
            dd = ImageDraw.Draw(out, "RGBA")
            tw = dd.textlength(label, font=MONO_B(44))
            dd.rectangle((100, H - 190, 140 + tw, H - 120), fill=(0, 0, 0, 180))
            dd.text((120, H - 185), label, font=MONO_B(44), fill=(240, 240, 230))
        return out
    f.still = big
    return f


def counter_shot(desc):
    txt = quoted(desc)[0]
    m = re.search(r"→\s*([\d,]+)\s*(.*)", txt)
    target, unit = int(m.group(1).replace(",", "")), m.group(2)
    sub = quoted(desc)[1] if len(quoted(desc)) > 1 else ""

    def f(t, dur):
        img = Image.new("RGB", (W, H), (10, 10, 10))
        d = ImageDraw.Draw(img)
        v = int(target * ease(min(t / (dur * 0.7), 1)))
        s = f"{v:,} {unit}".strip()
        tw = d.textlength(s, font=MONO_B(190))
        d.text(((W - tw) / 2, H / 2 - 150), s, font=MONO_B(190), fill=(235, 235, 225))
        if sub:
            tw2 = d.textlength(sub, font=SANS(46))
            d.text(((W - tw2) / 2, H / 2 + 90), sub, font=SANS(46), fill=(190, 40, 40))
        return img
    f.still = Image.new("RGB", (W, H), (10, 10, 10))
    return f


def sofar_diagram(desc):
    """Schemat kanału SOFAR (NOAA): dźwięk zagina się ku osi kanału i biegnie daleko."""
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    top = 180
    for y in range(top, H):
        v = int(70 - 55 * (y - top) / (H - top))
        d.line((0, y, W, y), fill=(v, v + 4, v + 8))
    d.rectangle((0, 0, W, top), fill=(18, 18, 18))
    d.line((0, top, W, top), fill=(200, 200, 190), width=3)
    axis = top + 330
    for x in range(0, W, 40):
        d.line((x, axis, x + 20, axis), fill=(210, 40, 40), width=3)
    d.text((260, axis - 55), "SOFAR CHANNEL AXIS (~1 km, varies)", font=MONO_B(30), fill=(235, 200, 200))
    for i, lab in enumerate(["0", "1 km", "2 km", "3 km"]):
        y = top + i * 300
        d.text((20, y - 16), lab, font=MONO(26), fill=(160, 160, 150))
    d.text((120, 60), "HOW SOUND CROSSES AN OCEAN", font=SANS(54), fill=(235, 235, 225))
    src, hyd = (140, axis + 40), (W - 160, axis - 20)
    path = [(x, axis + 170 * math.sin((x - src[0]) / 210) * math.exp(-(x - src[0]) / 2600)) for x in range(src[0], hyd[0], 6)]

    def f(t, dur):
        img = bg.copy()
        dd = ImageDraw.Draw(img)
        n = int(len(path) * ease(min(t / (dur * 0.75), 1)))
        if n > 1:
            dd.line(path[:n], fill=(240, 240, 230), width=5)
        dd.ellipse((src[0] - 18, src[1] - 18, src[0] + 18, src[1] + 18), fill=(230, 40, 40))
        dd.text((src[0] - 40, src[1] + 30), "SOURCE", font=MONO_B(26), fill=(235, 235, 225))
        dd.rectangle((hyd[0] - 14, hyd[1] - 30, hyd[0] + 14, hyd[1] + 30), fill=(235, 235, 225))
        dd.text((hyd[0] - 170, hyd[1] + 40), "HYDROPHONE", font=MONO_B(26), fill=(235, 235, 225))
        return add_caption(img, "Schematic — after NOAA")
    f.still = bg
    return f


def split_shot(desc, media):
    files = [x.strip() for x in field(desc, "FILES").split("|")]
    labels = (quoted(desc) + ["", ""])[:2]
    halves = [cover(grade(Image.open(media(fn))), W // 2, H) for fn in files]

    def f(t, dur):
        img = Image.new("RGB", (W, H))
        for i, hf in enumerate(halves):
            a = ease((t - 0.25 * i) / 0.4)
            off = int((1 - a) * (-200 if i == 0 else 200))
            img.paste(hf, (i * W // 2 + off, 0))
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle((W // 2 - 4, 0, W // 2 + 4, H), fill=(10, 10, 10))
        for i, lab in enumerate(labels):
            if lab:
                tw = d.textlength(lab, font=SANS(40))
                x = i * W // 2 + (W // 2 - tw) / 2
                d.rectangle((x - 20, H - 140, x + tw + 20, H - 80), fill=(0, 0, 0, 170))
                d.text((x, H - 135), lab, font=SANS(40), fill=(235, 235, 225))
        return img
    f.still = Image.new("RGB", (W, H))
    return f


def stack_shot(desc, media):
    files = [x.strip() for x in field(desc, "FILES").split("|")]
    rnd = np.random.default_rng(len(files))
    cards = []
    for fn in files:
        im = grade(Image.open(media(fn)))
        im.thumbnail((820, 560))
        pc = Image.new("RGB", (im.width + 40, im.height + 90), (238, 236, 228))
        pc.paste(im, (20, 20))
        ang = float(rnd.uniform(-8, 8))
        pc = pc.convert("RGBA").rotate(ang, expand=True, resample=Image.BICUBIC)
        pos = (int(W / 2 - pc.width / 2 + rnd.uniform(-380, 380)), int(H / 2 - pc.height / 2 + rnd.uniform(-160, 160)))
        cards.append((pc, pos))
    desk = Image.new("RGB", (W, H), (22, 20, 18))

    def f(t, dur):
        img = desk.copy()
        for i, (pc, (x, y)) in enumerate(cards):
            t0 = i * dur / (len(cards) + 0.5)
            a = ease((t - t0) / 0.35)
            if a <= 0:
                continue
            s = 1.25 - 0.25 * a
            c = pc.resize((int(pc.width * s), int(pc.height * s)))
            img.paste(c, (x - (c.width - pc.width) // 2, y - (c.height - pc.height) // 2), c)
        return img
    f.still = desk
    return f


def qa_shot(desc):
    q = re.search(r'Q:\s*"([^"]+)"', desc).group(1)
    ans = re.search(r'A:\s*"([^"]+)"', desc).group(1)
    src = desc.rsplit("—", 1)[-1].strip() if "—" in desc else ""

    def f(t, dur):
        img = Image.new("RGB", (W, H), (12, 12, 12))
        d = ImageDraw.Draw(img)
        d.text((150, 120), "IN HIS WORDS", font=MONO_B(30), fill=(150, 150, 140))
        d.text((150, 210), "Q", font=SANS(70), fill=(190, 40, 40))
        for i, l in enumerate(wrap(d, q, SANS(48), W - 420)):
            d.text((260, 220 + i * 64), l, font=SANS(48), fill=(225, 225, 215))
        a = ease((t - dur * 0.3) / 0.4)
        if a > 0:
            c = int(240 * a)
            d.text((150, 520), "A", font=SANS(70), fill=(int(190 * a), 40, 40))
            for i, l in enumerate(wrap(d, f"\u201c{ans}\u201d", MONO_B(50), W - 420)):
                d.text((260, 530 + i * 66), l, font=MONO_B(50), fill=(c, c, c))
            d.text((260, H - 150), "— " + src, font=MONO(32), fill=(int(170 * a),) * 3)
        return img
    f.still = Image.new("RGB", (W, H), (12, 12, 12))
    return f


def slogan_shot(desc):
    words = quoted(desc)[0].split()

    def f(t, dur):
        img = Image.new("RGB", (W, H), (10, 10, 10))
        d = ImageDraw.Draw(img)
        size = 130
        while size > 50 and d.textlength(" ".join(words), font=SANS(size)) > W - 240:
            size -= 6
        fnt = SANS(size)
        widths = [d.textlength(w + " ", font=fnt) for w in words]
        x = (W - sum(widths)) / 2
        for i, w in enumerate(words):
            a = ease((t - i * min(0.35, dur * 0.6 / len(words))) / 0.2)
            if a > 0:
                col = (200, 40, 40) if i == len(words) - 1 else (235, 235, 225)
                d.text((x, H / 2 - 90 + (1 - a) * 40), w, font=fnt, fill=tuple(int(v * a) for v in col))
            x += widths[i]
        return img
    f.still = Image.new("RGB", (W, H), (10, 10, 10))
    return f


# ───────────── biblioteka stylów napisów i porównań (v5) ─────────────

TEXT_STYLES = ["typewriter", "stamp", "lower-left", "top-right", "center-big", "side-bar", "highlight", "minimal"]
COMPARE_STYLES = ["cards", "split", "diagonal", "wipe", "pip"]


def text_card(desc, style, prev):
    lines = [x.strip() for x in ((quoted(desc) or [""])[0]).split("/")]
    over_black = "over black" in desc or prev is None or not hasattr(prev, "still")
    bg0 = Image.new("RGB", (W, H), (8, 8, 8)) if over_black else Image.eval(prev.still.convert("RGB"), lambda v: int(v * 0.45))
    if style == "typewriter":
        return R.title_shot(desc if "over black" in desc or not over_black else desc + " over black", prev)
    if style == "stamp":
        return R.title_shot(desc + " stamped", prev)

    def f(t, dur):
        img = R.ken_burns(bg0.resize((int(W * 1.06), int(H * 1.06))), t / dur, 1.0, 1.04)
        d = ImageDraw.Draw(img, "RGBA")
        a = ease(t / 0.45)
        c = int(240 * a)
        main, sub = lines[0], (lines[1] if len(lines) > 1 else "")
        if style == "lower-left":
            f1 = SANS(64)
            tw = d.textlength(main, font=f1)
            x = 110 - int((1 - a) * 60)
            d.rectangle((x - 20, H - 260, x + tw + 30, H - 170), fill=(0, 0, 0, int(190 * a)))
            d.text((x, H - 255), main, font=f1, fill=(c, c, c))
            if sub:
                d.text((x, H - 160), sub, font=MONO(36), fill=(int(c * .85),) * 3)
        elif style == "top-right":
            f1 = MONO_B(46)
            tw = d.textlength(main, font=f1)
            x = W - tw - 120
            d.rectangle((x - 24, 90, x + tw + 24, 160), fill=(190, 30, 30, int(230 * a)))
            d.text((x, 96), main, font=f1, fill=(255, 255, 255, int(255 * a)))
            if sub:
                tw2 = d.textlength(sub, font=MONO(32))
                d.text((W - tw2 - 120, 180), sub, font=MONO(32), fill=(c, c, c))
        elif style == "center-big":
            size = 170
            while size > 60 and d.textlength(main, font=SANS(size)) > W - 200:
                size -= 8
            f1 = SANS(size)
            tw = d.textlength(main, font=f1)
            d.text(((W - tw) / 2, H / 2 - size * 0.7 + (1 - a) * 30), main, font=f1, fill=(c, c, c))
            if sub:
                tw2 = d.textlength(sub, font=MONO(42))
                d.text(((W - tw2) / 2, H / 2 + size * 0.5), sub, font=MONO(42), fill=(200, 40, 40, int(255 * a)))
        elif style == "side-bar":
            d.rectangle((0, 0, 620, H), fill=(10, 10, 10, int(220 * a)))
            d.rectangle((600, 0, 612, H), fill=(190, 30, 30, int(255 * a)))
            y = H / 2 - 120
            for i, l in enumerate(wrap(d, main, SANS(62), 480)):
                d.text((80, y + i * 76), l, font=SANS(62), fill=(c, c, c))
            if sub:
                d.text((80, y + 260), sub, font=MONO(32), fill=(int(c * .8),) * 3)
        elif style == "highlight":
            f1 = MONO_B(84)
            tw = d.textlength(main, font=f1)
            x, y = (W - tw) / 2, H / 2 - 60
            sweep = ease((t - 0.3) / 0.8)
            d.rectangle((x - 10, y + 10, x - 10 + (tw + 20) * sweep, y + 100), fill=(250, 215, 60, 200))
            d.text((x, y), main, font=f1, fill=(240, 240, 230) if sweep < 0.5 else (15, 15, 15))
        else:  # minimal
            sp = " ".join(main.upper())
            f1 = SANS(40)
            tw = d.textlength(sp, font=f1)
            d.text(((W - tw) / 2, H / 2 - 20), sp, font=f1, fill=(c, c, c))
            d.line((W / 2 - 60 * a, H / 2 + 50, W / 2 + 60 * a, H / 2 + 50), fill=(200, 40, 40), width=3)
        return img
    f.still = bg0
    return f


def compare_variant(desc, media, style):
    files = [x.strip() for x in field(desc, "FILES").split("|")]
    labels = (quoted(desc) + ["", ""])[:2]
    labs = [l.partition("—")[0].strip() for l in labels]
    if style == "cards":
        return compare_files(desc, media)
    A, B = [cover(grade(Image.open(media(fn))), W, H) for fn in files[:2]]

    def label(d, text, x, y, align="left"):
        if not text:
            return
        f1 = SANS(42)
        tw = d.textlength(text, font=f1)
        x = x - tw if align == "right" else x - tw / 2 if align == "center" else x
        d.rectangle((x - 18, y - 8, x + tw + 18, y + 56), fill=(0, 0, 0, 180))
        d.text((x, y), text, font=f1, fill=(240, 240, 230))

    def f(t, dur):
        p = t / dur
        if style == "split":
            img = Image.new("RGB", (W, H))
            img.paste(A.crop((W // 4, 0, W // 4 + W // 2, H)), (0, 0))
            img.paste(B.crop((W // 4, 0, W // 4 + W // 2, H)), (W // 2, 0))
            d = ImageDraw.Draw(img, "RGBA")
            d.rectangle((W // 2 - 3, 0, W // 2 + 3, H), fill=(240, 240, 230))
            label(d, labs[0], W // 4, H - 150, "center")
            label(d, labs[1], 3 * W // 4, H - 150, "center")
        elif style == "diagonal":
            mask = Image.new("L", (W, H), 0)
            off = int(W * 0.15 * (1 - ease(p / 0.3)))
            ImageDraw.Draw(mask).polygon([(W * 0.6 + off, 0), (W, 0), (W, H), (W * 0.4 + off, H)], fill=255)
            img = Image.composite(B, A, mask)
            d = ImageDraw.Draw(img, "RGBA")
            d.line([(W * 0.6 + off, 0), (W * 0.4 + off, H)], fill=(200, 40, 40), width=8)
            label(d, labs[0], 100, 90)
            label(d, labs[1], W - 100, H - 150, "right")
        elif style == "wipe":
            x = int(W * (0.85 - 0.7 * ease(min(p / 0.8, 1))))
            img = A.copy()
            img.paste(B.crop((x, 0, W, H)), (x, 0))
            d = ImageDraw.Draw(img, "RGBA")
            d.rectangle((x - 3, 0, x + 3, H), fill=(240, 240, 230))
            d.ellipse((x - 26, H / 2 - 26, x + 26, H / 2 + 26), fill=(240, 240, 230))
            label(d, labs[0], 100, 90)
            label(d, labs[1], W - 100, 90, "right")
        else:  # pip
            img = R.ken_burns(A.resize((int(W * 1.08), int(H * 1.08))), p, 1.0, 1.05)
            a = ease((t - 0.4) / 0.4)
            pw, ph = int(W * 0.34), int(H * 0.34)
            small = B.resize((pw, ph), Image.LANCZOS)
            d = ImageDraw.Draw(img, "RGBA")
            x, y = W - pw - 90, H - ph - 90 + int((1 - a) * 60)
            if a > 0:
                d.rectangle((x - 8, y - 8, x + pw + 8, y + ph + 8), fill=(240, 240, 230, int(255 * a)))
                img.paste(small, (x, y))
                label(d, labs[1], x + pw / 2, y - 80, "center")
            label(d, labs[0], 100, 90)
        return img
    f.still = A
    return f


def build(s, k, media, prev, uses):
    desc, a, framing = s["desc"], s["asset"], s.get("framing", "")
    special = {"WAVEFORM": lambda: waveform_shot(desc, media), "SPEKTRO": lambda: spectro_live(desc, media),
               "LUPA": lambda: lupa_shot(desc, media), "LICZNIK": lambda: counter_shot(desc),
               "DIAGRAM": lambda: sofar_diagram(desc), "SPLIT": lambda: split_shot(desc, media),
               "STOS": lambda: stack_shot(desc, media), "QA": lambda: qa_shot(desc), "HASŁO": lambda: slogan_shot(desc)}
    style = s.get("style") or "auto"
    if a in ("TYTUŁ", "HASŁO") and style in TEXT_STYLES and style not in ("typewriter",) or (a == "TYTUŁ" and style == "typewriter"):
        return text_card(desc, style, prev)
    if a in ("PORÓWNANIE", "SPLIT") and style in COMPARE_STYLES and "FILES" in desc:
        return compare_variant(desc, media, style)
    if a in special:
        for fn in re.findall(r"[\w\-.]+\.(?:jpg|jpeg|png|gif|wav|webm|ogv)", desc, re.I):
            uses[fn] = uses.get(fn, 0) + 1
        return special[a]()
    cap = caption_of(desc, framing, a)
    fn = field(desc, "FILE")
    if not fn and a == "AI_OBRAZ" and f"{s['beat']}_wiz{s['wiz']:02d}.png" in media.index:
        fn = f"{s['beat']}_wiz{s['wiz']:02d}.png"  # kadr wygenerowany przez make_assets.py
    if a == "PODPIS":
        return lower_third(desc, build(dict(s, asset="ARCHIWUM"), k, media, prev, uses))
    if fn:
        p = media(fn)
        uses[fn] = uses.get(fn, 0) + 1
        if p.suffix.lower() in VIDEO_EXT:
            start = (floats(desc, "START") or [(uses[fn] - 1) * 9.0])[0]
            return VideoShot(p, start, cap)
        return photo_shot(p, k, cap)
    if a == "PRASA":
        return press_shot(desc)
    if a == "OŚ_CZASU":
        return timeline_shot(desc)
    if a == "MAPA" and "Juan de Fuca" in desc:
        return ne_pacific_map()
    if a == "PORÓWNANIE" and "FILES" in desc:
        return compare_files(desc, media)
    if a == "PORÓWNANIE" and "cards" in desc:
        return cards(desc)
    return R.build_shot(s, k, Path("/nonexistent"), prev)


# ───────────── dźwięk ─────────────

def load_audio(path):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), tmp.name], check=True)
        x, _ = sf.read(tmp.name, dtype="float32")
    return x


def env(n, attack, decay):
    t = np.arange(n) / SR
    return (1 - np.exp(-t / attack)) * np.exp(-t / decay)


def sfx():
    rng = np.random.default_rng(1)
    t = np.arange(int(SR * 1.6)) / SR
    boom = np.sin(2 * np.pi * (55 * t - 12 * t * t)) * env(t.size, 0.004, 0.45) * 0.9
    boom += rng.normal(0, 1, t.size) * env(t.size, 0.001, 0.03) * 0.25
    n = int(SR * 0.5)
    noise = rng.normal(0, 1, n)
    k = np.cumsum(noise) / 40  # brązowy szum = "whoosh"
    whoosh = (k - k.mean()) / np.abs(k).max() * np.linspace(0, 1, n) ** 2 * 0.5
    click = rng.normal(0, 1, int(SR * 0.018)) * env(int(SR * 0.018), 0.0005, 0.004) * 0.35
    st = np.arange(int(SR * 0.35)) / SR
    stamp = (np.sin(2 * np.pi * 90 * st) * 0.8 + rng.normal(0, 1, st.size) * 0.3) * env(st.size, 0.001, 0.06) * 0.8
    return dict(boom=boom.astype(np.float32), whoosh=whoosh.astype(np.float32),
                click=click.astype(np.float32), stamp=stamp.astype(np.float32))


def place(track, x, at, gain=1.0):
    i = int(at * SR)
    if i >= track.size or i + x.size <= 0:
        return
    j0 = max(0, -i)
    seg = x[j0: track.size - i]
    track[max(i, 0): max(i, 0) + seg.size] += seg * gain


# ───────────── main ─────────────

def kv(items, cast=float):
    out = {}
    for it in items:
        k, _, v = it.partition("=")
        out[k] = cast(v)
    return out


def credits_card(ledgers, extra, used=None):
    lines = []
    for lp in ledgers:
        for x in json.loads(Path(lp).read_text()):
            if used is not None and x["file"] not in used:
                continue
            title = re.sub(r"^File:", "", x["title"]).rsplit(".", 1)[0][:48]
            lines.append(f"{title} — {(x.get('artist') or x.get('credit') or 'unknown')[:28]} ({x['license']})")
    img = Image.new("RGB", (W, H), (8, 8, 8))
    d = ImageDraw.Draw(img)
    d.text((100, 60), "SOURCES & CREDITS", font=SANS(50), fill=(235, 235, 230))
    y = 140
    for s in extra:
        d.text((100, y), s, font=MONO(24), fill=(205, 205, 195))
        y += 32
    y += 16
    d.text((100, y), "Images & footage (Wikimedia Commons):", font=MONO_B(24), fill=(205, 205, 195))
    y += 38
    rows = math.ceil(len(lines) / 3) or 1
    fs = 17 if rows > 22 else 19
    for i, l in enumerate(lines):
        col, row = i // rows, i % rows
        d.text((100 + col * 600, y + row * (fs + 9)), l[:66], font=MONO(fs), fill=(170, 170, 160))
    return img


TRANSITIONS = ["cut", "dissolve", "dip", "slide", "whip", "zoom", "flash", "burn"]
RENDER_VERSION = "4"


def apply_transition(kind, prev_img, img, p):
    """p: 0..1 postęp przejścia z prev_img do img."""
    if kind == "dissolve":
        return Image.blend(prev_img, img, ease(p))
    if kind == "dip":
        black = Image.new("RGB", (W, H))
        return Image.blend(prev_img, black, ease(p * 2)) if p < 0.5 else Image.blend(black, img, ease(p * 2 - 1))
    if kind in ("slide", "whip"):
        e = ease(p)
        out = Image.new("RGB", (W, H))
        out.paste(prev_img, (int(-W * e), 0))
        out.paste(img, (int(W * (1 - e)), 0))
        if kind == "whip" and 0.1 < p < 0.9:
            out = out.resize((W // 24, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        return out
    if kind == "zoom":
        z = 1 + 0.6 * ease(p)
        cw, ch = W / z, H / z
        zp = prev_img.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        return Image.blend(zp, img, ease(p))
    if kind == "flash":
        white = Image.new("RGB", (W, H), (255, 255, 250))
        return Image.blend(prev_img, white, ease(p * 2)) if p < 0.5 else Image.blend(white, img, ease(p * 2 - 1))
    if kind == "burn":
        base = Image.blend(prev_img, img, ease(p))
        a = math.sin(math.pi * p)
        leak = Image.new("RGB", (W, H), (255, 150, 60))
        return Image.blend(base, leak, 0.55 * a)
    return img


def film_config(prj):
    return {"media": [], "voice": "voice", "lead": {}, "tail": {}, "cues": [], "credits": [], "credit_lines": [],
            "silence_before": "", **prj.get("render", {})}


def plan_film(prj, root, fps):
    """Oś czasu filmu: beaty (start, dur) i ujęcia (st, d, spec) — bez ładowania mediów."""
    import docos
    cfg = film_config(prj)
    plan = docos.render_plan(prj)
    voice = root / cfg["voice"]
    dyn = {b["id"]: docos.effective_dynamic(prj, b) for b in prj["beats"]}
    beats, t0 = [], 0.0
    for bid in dict.fromkeys(s["beat"] for s in plan["shots"]):
        vf = voice / f"{bid}.wav"
        v = sf.info(str(vf)).duration if vf.exists() else sum(s["dur"] for s in plan["shots"] if s["beat"] == bid)
        lead, tail = float(cfg["lead"].get(bid, 0.25)), float(cfg["tail"].get(bid, 0.35))
        beats.append(dict(id=bid, voice=vf if vf.exists() else None, lead=lead, start=t0, dur=lead + v + tail, dyn=dyn.get(bid)))
        t0 += lead + v + tail
    specs, events, counts = [], [], {}
    for b in beats:
        shots = [s for s in plan["shots"] if s["beat"] == b["id"]]
        durs = [s["dur"] for s in shots]
        extra = b["dur"] - sum(durs)
        flex = [i for i, d in enumerate(durs) if d >= FAST] or list(range(len(durs)))
        if extra > 0:
            fs = sum(durs[i] for i in flex)
            durs = [d + (extra * d / fs if i in flex else 0) for i, d in enumerate(durs)]
        else:
            durs = [d * b["dur"] / sum(durs) for d in durs]
        st = b["start"]
        for i, (s, d) in enumerate(zip(shots, durs)):
            fn = field(s["desc"], "FILE")
            use_idx = counts.get(fn, 0) if fn else 0
            if fn:
                counts[fn] = use_idx + 1
            tr = s.get("transition") or ("dissolve" if i == 0 and b["dyn"] != "ACTION" and specs else "cut")
            specs.append(dict(st=st, d=d, shot=s, beat=b["id"], use_idx=use_idx, transition=tr))
            if s["asset"] == "TYTUŁ":
                if "stamp" in s["desc"]:
                    events.append(("stamp", st + 0.02, 1.0))
                else:
                    txt = (quoted(s["desc"]) or [""])[0]
                    cps = max(len(txt) / max(d * 0.45, 0.3), 8)
                    events += [("click", st + 0.05 + j / cps, 0.8) for j, ch in enumerate(txt) if ch != " "]
            if s["asset"] in ("PRASA", "CYTAT", "QA"):
                events += [("click", st + 0.3 + j * 0.06, 0.5) for j in range(10)]
            st += d
        if b["dyn"] in ("ACTION", "EUREKA"):
            events += [("whoosh", b["start"] - 0.5, 0.8), ("boom", b["start"], 0.9)]
    credits = 9.0 if cfg["credits"] or cfg["credit_lines"] else 0.0
    return dict(cfg=cfg, beats=beats, specs=specs, events=events, credits=credits, total=t0 + credits)


def make_media(prj, root):
    return Media([root / m for m in film_config(prj)["media"]])


def shot_fn(spec, k, media, prev):
    uses = {}
    fn = field(spec["shot"]["desc"], "FILE")
    if fn:
        uses[fn] = spec["use_idx"]
    return build(dict(spec["shot"], beat=spec["beat"]), k, media, prev, uses)


def movavg(x, k):
    c = np.cumsum(np.concatenate([[0.0], x.astype(np.float64)]))
    y = (c[k:] - c[:-k]) / k
    pad = x.size - y.size
    return np.pad(y, (pad // 2, pad - pad // 2), mode="edge").astype(np.float32)


def mix_audio(fp, media, out_wav):
    cfg, beats, total = fp["cfg"], fp["beats"], fp["total"]
    n = int(total * SR) + SR
    voice = np.zeros(n, np.float32)
    for b in beats:
        if b["voice"]:
            place(voice, load_audio(b["voice"]), b["start"] + b["lead"])
    tt = np.arange(n) / SR
    bed = (0.05 * np.sin(2 * np.pi * 55 * tt) + 0.035 * np.sin(2 * np.pi * 82.5 * tt + 0.3 * np.sin(0.2 * tt))).astype(np.float32)
    rng = np.random.default_rng(3)
    brown = np.cumsum(rng.normal(0, 1, n)).astype(np.float32)
    brown -= movavg(brown, 4800)
    bed += brown / (np.abs(brown).max() + 1e-6) * 0.05
    if cfg["silence_before"]:
        bs = next(b for b in beats if b["id"] == cfg["silence_before"])
        g = np.ones(n, np.float32)
        s0, s1, s2 = bs["start"] - 1.8, bs["start"], bs["start"] + 5.0
        m1, m2 = (tt > s0) & (tt <= s1), (tt > s1) & (tt <= s2)
        g[m1] = np.clip(1 - (tt[m1] - s0) / (s1 - s0), 0, 1)
        g[m2] = np.clip((tt[m2] - s1) / (s2 - s1), 0, 1)
        bed *= g
    cues = np.zeros(n, np.float32)
    for c in cfg["cues"]:
        bid, where, fname, gain, *mx = c.split(":")
        b = next(x for x in beats if x["id"] == bid)
        x = load_audio(media(fname))
        if mx:
            x = x[: int(float(mx[0]) * SR)]
        fade = min(int(0.4 * SR), x.size // 4)
        x[-fade:] *= np.linspace(1, 0, fade)
        at = b["start"] if where == "start" else b["start"] + b["dur"] - x.size / SR
        place(cues, x / (np.abs(x).max() + 1e-6) * 0.8, at, float(gain))
    fx = np.zeros(n, np.float32)
    S = sfx()
    for name, at, g in fp["events"]:
        place(fx, S[name], at, g)
    e = movavg(np.abs(voice), int(0.25 * SR))
    duck = 1 - 0.65 * np.clip(e / (e.max() * 0.25 + 1e-6), 0, 1)
    mix = voice + (bed + cues) * duck + fx * 0.8
    mix[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
    sf.write(out_wav, (mix / (np.abs(mix).max() + 1e-6) * 0.9)[: int(total * SR)], SR)


def seg_key(fp, bid, q, media):
    idx = [i for i, s in enumerate(fp["specs"]) if s["beat"] == bid]
    prev = fp["specs"][idx[0] - 1]["shot"] if idx and idx[0] > 0 else None
    files = sorted({f for i in idx for f in re.findall(r"[\w\-.]+\.(?:jpg|jpeg|png|gif|wav|webm|ogv|JPEG)", fp["specs"][i]["shot"]["desc"])})
    mt = [media.index[f].stat().st_mtime if f in media.index else 0 for f in files]
    first, last = fp["beats"][0]["id"] == bid, fp["beats"][-1]["id"] == bid
    blob = json.dumps([RENDER_VERSION, q, [(fp["specs"][i]["shot"], round(fp["specs"][i]["d"], 3), fp["specs"][i]["transition"],
                                           fp["specs"][i]["use_idx"]) for i in idx], prev, mt, first, last, bool(fp["credits"])],
                      sort_keys=True, ensure_ascii=False, default=str)
    import hashlib
    return hashlib.sha1(blob.encode()).hexdigest()[:16]


def render_segment(job):
    """Worker: renderuje jeden beat (albo napisy końcowe) do pliku wideo bez dźwięku."""
    global FPS
    proj, bid, out, q = job["project"], job["beat"], job["out"], job["q"]
    FPS = q["fps"]
    root = Path(proj).parent
    prj = json.loads(Path(proj).read_text())
    fp = plan_film(prj, root, FPS)
    media = make_media(prj, root)
    if bid == "CREDITS":
        used = {f for sp in fp["specs"] for f in re.findall(r"[\w\-.]+\.(?:jpg|jpeg|png|gif|wav|webm|ogv|mp4|JPEG)", sp["shot"]["desc"])}
        used |= {c.split(":")[2] for c in fp["cfg"]["cues"]}
        img = credits_card([root / c for c in fp["cfg"]["credits"]], fp["cfg"]["credit_lines"], used)
        t_from, t_to = fp["total"] - fp["credits"], fp["total"]
        frames_of = lambda t: img  # noqa: E731
        idx = []
    else:
        b = next(x for x in fp["beats"] if x["id"] == bid)
        t_from, t_to = b["start"], b["start"] + b["dur"]
        idx = [i for i, s in enumerate(fp["specs"]) if s["beat"] == bid]
    fns = {}
    allowed = set(idx) | ({idx[0] - 1} if idx and idx[0] > 0 else set())

    def get(i):
        if i not in fns:
            prev = get(i - 1) if (i - 1) in allowed else None
            fns[i] = shot_fn(fp["specs"][i], i, media, prev)
        return fns[i]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vign = np.clip(1.12 - 0.5 * r ** 2, 0.3, 1.0)[..., None].astype(np.float32)
    g_rng = np.random.default_rng(7)
    grains = [np.asarray(Image.fromarray(g_rng.normal(128, 26, (H // 2, W // 2)).clip(0, 255).astype(np.uint8))
                         .resize((W, H), Image.BILINEAR), dtype=np.float32)[..., None] - 128 for _ in range(6)]
    total = fp["total"]
    scale = ["-vf", f"scale={q['scale']}"] if q.get("scale") else []
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", *scale, "-c:v", "libx264", "-preset", q.get("preset", "medium"), "-crf", str(q.get("crf", 22)),
           "-pix_fmt", "yuv420p", "-an", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    f0, f1 = round(t_from * FPS), round(t_to * FPS)
    cur = idx[0] if idx else None
    for fi in range(f0, f1):
        t = fi / FPS
        if idx:
            while cur < idx[-1] and t >= fp["specs"][cur]["st"] + fp["specs"][cur]["d"]:
                cur += 1
            sp = fp["specs"][cur]
            tl = max(0.0, min(t - sp["st"], sp["d"]))
            img = get(cur)(tl, sp["d"]).convert("RGB")
            tr = sp["transition"]
            tdur = 0.25 if tr == "flash" else 0.5
            if tr != "cut" and tl < tdur and cur > 0:
                pv = fp["specs"][cur - 1]
                img = apply_transition(tr, get(cur - 1)(pv["d"], pv["d"]).convert("RGB"), img, tl / tdur)
        else:
            img = frames_of(t)
        arr = np.asarray(img, dtype=np.float32) * vign
        arr *= 1.0 + 0.015 * math.sin(t * 23.0)
        arr += grains[fi % len(grains)] * 0.22
        arr *= min(ease(t / 0.5), ease((total - t) / 1.2))
        proc.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    return out


QUALITY = {"preview": dict(fps=12, scale="640:360", crf=30, preset="veryfast"),
           "final": dict(fps=25, scale="", crf=22, preset="medium")}


def render_film(project, out, quality="preview", workers=4, only=None, progress=print):
    """Renderuje film z cache segmentów. only=lista beatów do wymuszenia (reszta z cache, jeśli aktualna)."""
    import multiprocessing as mp
    q = QUALITY[quality]
    project = Path(project).resolve()
    root = project.parent
    prj = json.loads(project.read_text())
    fp = plan_film(prj, root, q["fps"])
    media = make_media(prj, root)
    cache = root / ".render_cache" / quality
    cache.mkdir(parents=True, exist_ok=True)
    jobs, segs = [], []
    ids = [b["id"] for b in fp["beats"]] + (["CREDITS"] if fp["credits"] else [])
    for bid in ids:
        key = seg_key(fp, bid, q, media) if bid != "CREDITS" else f"credits_{len(fp['cfg']['credit_lines'])}_{round(fp['total'], 2)}"
        seg = cache / f"{bid}_{key}.mp4"
        segs.append(seg)
        if not seg.exists() or (only and bid in only):
            jobs.append(dict(project=str(project), beat=bid, out=str(seg), q=q))
    progress(f"segmenty do renderu: {len(jobs)}/{len(ids)}")
    if jobs:
        with mp.get_context("spawn").Pool(min(workers, len(jobs))) as pool:
            for done in pool.imap_unordered(render_segment, jobs):
                progress(f"gotowy segment: {Path(done).name.split('_')[0]}")
    wav = cache / "_mix.wav"
    mix_audio(fp, media, wav)
    lst = cache / "_list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a",
                    "160k" if quality == "preview" else "192k", "-movflags", "+faststart", str(out)], check=True)
    progress(f"zapisano {out} ({fp['total']:.0f}s)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", help="projekt DocOS (.json) z sekcją 'render'")
    ap.add_argument("--out", required=True)
    ap.add_argument("--quality", choices=list(QUALITY), default="preview")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="append", default=[], help="wymuś ponowny render beatu")
    a = ap.parse_args()
    render_film(a.project, a.out, a.quality, a.workers, a.force)


if __name__ == "__main__":
    main()
