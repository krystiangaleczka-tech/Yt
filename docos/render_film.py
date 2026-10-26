"""Montaż filmu z planu DocOS: render_plan.json + kadry + lektor per beat -> MP4.

    ../pilot/.venv/bin/python -I render_film.py examples/bloop/bloop_render_plan.json \
        --assets examples/bloop/assets --voice examples/bloop/voice --out examples/bloop/bloop_film.mp4

Typy ujęć bez pliku kadru rysowane są proceduralnie (spektrogram, tabela, tytuł, mapa, porównanie, cytat).
Czas ujęć w beacie skalowany jest do rzeczywistej długości lektora.
"""
import argparse
import json
import math
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 25
HERE = Path(__file__).parent
FONTS = HERE.parent / "pilot" / "fonts"
BORDO, INK, PAPER = (74, 14, 18), (12, 12, 12), (226, 222, 210)
LEAD = {"B02": 1.4}           # sekundy ciszy przed lektorem (B02: najpierw słychać "bloop")
LEAD_DEFAULT, TAIL, XF = 0.3, 0.45, 0.3


def font(name, size, wght=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


MONO_B = lambda s: font("CourierPrime-Bold.ttf", s)  # noqa: E731
MONO = lambda s: font("CourierPrime-Regular.ttf", s)  # noqa: E731
SANS = lambda s: font("Montserrat.ttf", s, 600)  # noqa: E731


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def quoted(desc):
    return re.findall(r'"([^"]+)"', desc)


# ───────────── procedural sources ─────────────

def bloop_signal(sr=2000, dur=6.0, seed=3, rise=110.0, starts=(0.4, 2.3, 4.1)):
    t = np.arange(int(sr * dur)) / sr
    sig = np.zeros_like(t)
    for st in starts:
        tt = np.clip(t - st, 0, None)
        env = np.where(t >= st, np.exp(-tt * 1.6) * (1 - np.exp(-tt * 25)), 0)
        f = 30 + rise * (1 - np.exp(-tt * 1.4))
        ph = 2 * np.pi * np.cumsum(f) / sr
        sig += env * (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph))
    return sig + 0.08 * np.random.default_rng(seed).normal(size=t.size), sr


def spectrogram(w, h, seed=3, rise=110.0, label="HYDROPHONE / 1997 / 0-500 Hz"):
    sig, _ = bloop_signal(seed=seed, rise=rise)
    n, hop = 256, 16
    win = np.hanning(n)
    fr = np.stack([sig[i:i + n] * win for i in range(0, sig.size - n, hop)])
    spec = 20 * np.log10(np.abs(np.fft.rfft(fr, axis=1)).T + 1e-6)
    spec = spec[: spec.shape[0] // 2][::-1]
    spec = np.clip((spec - spec.max() + 55) / 55, 0, 1) ** 1.4
    im = Image.fromarray((spec * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(0.8)).convert("RGB")
    d = ImageDraw.Draw(im)
    for i in range(1, 5):
        d.line((0, h * i / 5, w, h * i / 5), fill=(60, 60, 60))
        d.line((w * i / 5, 0, w * i / 5, h), fill=(60, 60, 60))
    d.text((16, 12), label, font=MONO(max(18, w // 40)), fill=(170, 170, 170))
    return im


def rounded(src, w, h, rad=28):
    src = src.resize((w, int(w * src.height / src.width)), Image.LANCZOS)
    if src.height < h:
        src = src.resize((int(h * src.width / src.height), h), Image.LANCZOS)
    x0, y0 = (src.width - w) // 2, (src.height - h) // 2
    src = src.crop((x0, y0, x0 + w, y0 + h))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), rad, fill=255)
    return src, mask


def ken_burns(im, p, z0, z1, dx=0.0, dy=0.0):
    z = z0 + (z1 - z0) * p
    cw, ch = im.width / z, im.height / z
    cx = im.width / 2 + dx * p * (im.width - cw) / 2
    cy = im.height / 2 + dy * p * (im.height - ch) / 2
    return im.resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))


def typewriter(d, xy, text, f, t, start, cps, fill):
    n = int(max(0.0, t - start) * cps)
    if n:
        d.text(xy, text[:n], font=f, fill=fill)


# ───────────── shot renderers: f(t_local, dur) -> PIL RGB ─────────────

MOVES = [(1.0, 1.10, 0.0, 0.0), (1.12, 1.0, 0.0, 0.0), (1.06, 1.06, 0.8, 0.0), (1.06, 1.06, -0.8, 0.0), (1.0, 1.08, 0.3, 0.3)]


def image_shot(path, k):
    im = Image.open(path).convert("L").convert("RGB")
    im = im.resize((int(W * 1.15), int(H * 1.15)), Image.LANCZOS)
    z0, z1, dx, dy = MOVES[k % len(MOVES)]

    def f(t, dur):
        return ken_burns(im, t / dur, z0, z1, dx, dy)
    f.still = im.resize((W, H))
    return f


def spectro_shot(desc, k):
    if "beside" in desc:  # dwa wydruki obok siebie
        a, b = spectrogram(820, 560), spectrogram(820, 560, seed=9, rise=95, label="ICEQUAKE / SCOTIA SEA")
        base = Image.new("RGB", (W, H), PAPER)
        base.paste(a, (110, 260))
        base.paste(b, (990, 260))
        return image_like(base, k)
    if "Scotia" in desc:
        sp = spectrogram(1500, 820, seed=9, rise=95, label="ICEQUAKE / SCOTIA SEA")
    else:
        sp = spectrogram(1500, 820)
    reveal = "drawing itself" in desc
    bg = Image.new("RGB", (W, H), PAPER)

    def f(t, dur):
        fr = bg.copy()
        if reveal:
            cut = int(sp.width * ease(t / dur * 1.15))
            fr.paste(sp.crop((0, 0, max(cut, 1), sp.height)), (210, 130))
        else:
            fr.paste(sp, (210, 130))
        return ken_burns(fr.resize((int(W * 1.1), int(H * 1.1))), t / dur, 1.0, 1.06)
    f.still = bg
    return f


def image_like(still, k):
    big = still.resize((int(W * 1.1), int(H * 1.1)))
    z0, z1, dx, dy = MOVES[k % len(MOVES)]

    def f(t, dur):
        return ken_burns(big, t / dur, min(z0, 1.06), min(z1, 1.06), dx * 0.5, dy * 0.5)
    f.still = still
    return f


def logsheet_shot(k):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    fb, fr = MONO_B(54), MONO(46)
    cols = [240, 900, 1240, 1560]
    d.text((240, 120), "ACOUSTIC CONTACT LOG", font=fb, fill=INK)
    for x, h in zip(cols, ["SOURCE", "SEISMIC", "BIOLOGIC", "SHIP"]):
        d.text((x, 260), h, font=fb, fill=INK)
    d.line((220, 330, 1720, 330), fill=INK, width=3)
    rows = [("seafloor rumble", "X", "", ""), ("whale song", "", "X", ""),
            ("propeller churn", "", "", "X"), ("unidentified", "?", "?", "?")]
    for i, r in enumerate(rows):
        y = 380 + i * 110
        for x, v in zip(cols, r):
            d.text((x + (60 if x != 240 else 0), y), v, font=fr, fill=(150, 20, 20) if r[0] == "unidentified" else INK)
    return image_like(im, k)


def title_shot(desc, prev):
    texts = quoted(desc) or [desc]
    lines = [s.strip() for s in texts[0].split("/")]
    stamp = "stamp" in desc
    use_prev = prev is not None and hasattr(prev, "still") and "over black" not in desc
    bg = prev.still if use_prev else Image.new("RGB", (W, H), (8, 8, 8))
    bg = Image.eval(bg, lambda v: int(v * 0.35))

    def f(t, dur):
        fr = bg.copy()
        d = ImageDraw.Draw(fr)
        if stamp:
            a = ease(t / 0.18)
            if a > 0:
                txt = lines[0]
                fnt = MONO_B(150 if len(txt) < 12 else 110)
                tw = d.textlength(txt, font=fnt)
                lay = Image.new("RGBA", (int(tw) + 80, 220), (0, 0, 0, 0))
                ld = ImageDraw.Draw(lay)
                ld.rectangle((6, 6, lay.width - 6, 214), outline=(190, 30, 30, int(255 * a)), width=10)
                ld.text((40, 30), txt, font=fnt, fill=(190, 30, 30, int(255 * a)))
                lay = lay.rotate(-6, expand=True, resample=Image.BICUBIC)
                s = 1.25 - 0.25 * a
                lay = lay.resize((int(lay.width * s), int(lay.height * s)))
                fr.paste(lay, ((W - lay.width) // 2, (H - lay.height) // 2), lay)
        else:
            big = MONO_B(150)
            small = MONO(80)
            cps = max(len(lines[0]) / max(dur * 0.45, 0.3), 8)
            typewriter(d, (140, 120), lines[0], big, t, 0.05, cps, (235, 235, 230))
            if len(lines) > 1:
                typewriter(d, (148, 300), lines[1], small, t, dur * 0.3, cps, (200, 200, 195))
        return fr
    f.still = bg
    return f


def grid_bg():
    im = Image.new("RGB", (W, H), (10, 12, 14))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 80):
        d.line((x, 0, x, H), fill=(26, 30, 34))
    for y in range(0, H, 80):
        d.line((0, y, W, y), fill=(26, 30, 34))
    return im


def pacific_map(desc):
    """Equirectangular 120°E–280°E, 60°S–60°N. Kropki = ilustracyjna sieć hydrofonów (nie dokładne pozycje)."""
    bg = grid_bg()
    d = ImageDraw.Draw(bg)
    lon0, lon1, lat0, lat1 = 120, 280, -60, 60
    P = lambda lon, lat: ((lon - lon0) / (lon1 - lon0) * W, (lat1 - lat) / (lat1 - lat0) * H)  # noqa: E731
    for lat in range(-60, 61, 20):
        y = P(0 + lon0, lat)[1]
        d.line((0, y, W, y), fill=(60, 66, 72) if lat else (120, 120, 110), width=1 if lat else 2)
        d.text((14, y + 6), f"{abs(lat)}°{'N' if lat > 0 else 'S' if lat < 0 else ''}", font=MONO(26), fill=(110, 110, 105))
    for lon in range(140, 280, 20):
        x = P(lon, 0)[0]
        d.line((x, 0, x, H), fill=(40, 46, 52))
    d.text((P(170, 30)[0], P(170, 30)[1]), "PACIFIC OCEAN", font=MONO_B(48), fill=(150, 150, 140))
    d.text((P(232, 3)[0], P(232, 3)[1]), "EQUATOR", font=MONO(28), fill=(150, 150, 140))
    dots = [P(lon, lat) for lon, lat in [(250, 8), (255, -2), (262, 5), (248, -8), (258, -9), (266, -4)]]
    src = P(250, -58)
    rings = "rings" in desc

    def f(t, dur):
        fr = bg.copy()
        dd = ImageDraw.Draw(fr)
        p = t / dur
        if rings:
            for k in range(3):
                r = ((p * 1.3 + k / 3) % 1.0) * 1100
                c = int(200 * (1 - r / 1100))
                dd.ellipse((src[0] - r, src[1] - r, src[0] + r, src[1] + r), outline=(c, c, c), width=3)
            dd.text((src[0] + 20, src[1] - 50), "?", font=MONO_B(70), fill=(200, 40, 40))
        for i, (x, y) in enumerate(dots):
            if rings or p > i / len(dots):
                dd.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(235, 235, 225))
                dd.ellipse((x - 22, y - 22, x + 22, y + 22), outline=(235, 235, 225), width=2)
        return ken_burns(fr.resize((int(W * 1.1), int(H * 1.1))), p, 1.0, 1.06)
    f.still = bg
    return f


def polar_map():
    """Rzut azymutalny bieguna południowego. Strefa źródła wg NOAA: Bransfield Strait – Ross Sea / Cape Adare."""
    bg = grid_bg()
    d = ImageDraw.Draw(bg)
    cx, cy, R = W / 2 + 120, H / 2 + 60, 1000  # R = promień do 30°S (wychodzi poza kadr)

    def P(lat, lon):
        r = (90 + lat) / 60 * R
        a = math.radians(lon)
        return cx + r * math.sin(a), cy + r * math.cos(a)  # 0° w dół, Pacyfik u góry
    for lat in (-80, -70, -60, -50, -40):
        r = (90 + lat) / 60 * R
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(55, 60, 66), width=1)
        d.text((cx + 6, cy + r + 4), f"{-lat}°S", font=MONO(24), fill=(110, 110, 105))
    for lon in range(0, 360, 30):
        d.line((cx, cy, *P(-30, lon)), fill=(38, 44, 50))
    r70 = (90 - 70) / 60 * R
    d.ellipse((cx - r70, cy - r70, cx + r70, cy + r70), fill=(52, 54, 56))
    d.text((cx - 130, cy + 40), "ANTARCTICA", font=MONO_B(44), fill=(170, 170, 160))
    places = {"BRANSFIELD STRAIT": (-63, -59), "ROSS SEA": (-75, -175), "CAPE ADARE": (-71.3, 170.2)}
    offs = {"BRANSFIELD STRAIT": (18, -14), "ROSS SEA": (-230, -14), "CAPE ADARE": (18, -40)}
    pts = {k: P(*v) for k, v in places.items()}
    origin = P(-30, -110)  # kierunek, z którego słuchały hydrofony (Pacyfik)

    def f(t, dur):
        fr = bg.copy()
        dd = ImageDraw.Draw(fr, "RGBA")
        p = t / dur
        for i, (name, (x, y)) in enumerate(pts.items()):
            a = ease((p - 0.1 - 0.12 * i) / 0.15)
            if a <= 0:
                continue
            dd.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(200, 40, 40, int(255 * a)))
            ox, oy = offs[name]
            dd.text((x + ox, y + oy), name, font=MONO_B(34), fill=(235, 235, 225, int(255 * a)))
        g = ease((p - 0.5) / 0.35)
        if g > 0:
            for (x, y) in pts.values():
                dd.line((origin[0], origin[1], origin[0] + (x - origin[0]) * g, origin[1] + (y - origin[1]) * g),
                        fill=(220, 220, 210, 160), width=3)
        dd.text((150, 100), "ESTIMATED SOURCE AREA (NOAA)", font=MONO_B(40), fill=(220, 220, 210))
        return ken_burns(fr.resize((int(W * 1.1), int(H * 1.1))), p, 1.0, 1.08, 0, -0.2)
    f.still = bg
    return f


def cards_shot(desc):
    words = [w.strip() for w in desc.split("cards", 1)[-1].split("/")]

    def f(t, dur):
        i = min(int(t / dur * len(words)), len(words) - 1)
        fr = Image.new("RGB", (W, H), BORDO if i % 2 else (10, 10, 10))
        d = ImageDraw.Draw(fr)
        txt = " ".join(words[i])
        fnt = SANS(110)
        tw = d.textlength(txt, font=fnt)
        d.text(((W - tw) / 2, H / 2 - 70), txt, font=fnt, fill=(235, 235, 230))
        d.text((W / 2 - 90, H / 2 + 90), "GUESS?", font=MONO(44), fill=(190, 190, 185))
        return fr
    f.still = Image.new("RGB", (W, H), (10, 10, 10))
    return f


def compare_shot(desc, assets):
    labels = quoted(desc)
    left, right = (labels + ["", ""])[:2]
    CW, CH = 660, 420

    def card_for(label, side):
        if "WHALE" in label.upper() and (assets / "B04_wiz02.png").exists():
            return Image.open(assets / "B04_wiz02.png").convert("L").convert("RGB")
        if "ICEQUAKE" in label.upper():
            return spectrogram(CW, CH, seed=9, rise=95, label="ICEQUAKE")
        return spectrogram(CW, CH)
    cards = [rounded(card_for(left, 0), CW, CH), rounded(card_for(right, 1), CW, CH)]

    def split_label(s):
        parts = [p.strip() for p in s.split("—")]
        return parts[0], (parts[1] if len(parts) > 1 else "")

    def f(t, dur):
        fr = Image.new("RGB", (W, H), (8, 8, 8))
        d = ImageDraw.Draw(fr)
        d.rectangle((W // 2, 0, W, H), fill=BORDO)
        for i, (img, mask) in enumerate(cards):
            a = ease((t - 0.1 - 0.35 * i) / 0.5)
            if a <= 0:
                continue
            x = (W // 4 if i == 0 else 3 * W // 4) - CW // 2
            y = int(H / 2 - CH / 2 - 70 + (1 - a) * 40)
            m = mask.point(lambda v: int(v * a))
            fr.paste(img, (x, y), m)
            main, sub = split_label([left, right][i])
            c = int(235 * a)
            sp = " ".join(main)
            tw = d.textlength(sp, font=SANS(44))
            cxp = W // 4 if i == 0 else 3 * W // 4
            d.text((cxp - tw / 2, H / 2 + CH / 2 - 40), sp, font=SANS(44), fill=(c, c, c))
            if sub:
                tw2 = d.textlength(sub, font=MONO(34))
                d.text((cxp - tw2 / 2, H / 2 + CH / 2 + 30), sub, font=MONO(34), fill=(int(c * .8),) * 3)
        return ken_burns(fr.resize((int(W * 1.1), int(H * 1.1))), t / dur, 1.0, 1.04)
    f.still = Image.new("RGB", (W, H), (8, 8, 8))
    return f


def quote_shot(desc):
    q = quoted(desc)[0]
    attrib = desc.split("—", 1)[-1].strip() if "—" in desc else ""

    def f(t, dur):
        fr = Image.new("RGB", (W, H), (10, 10, 10))
        d = ImageDraw.Draw(fr)
        typewriter(d, (180, 380), f"“{q}”", MONO_B(84), t, 0.3, 18, (235, 235, 230))
        a = ease((t - 0.3 - len(q) / 18 - 0.3) / 0.6)
        if a > 0:
            d.text((185, 540), "— " + attrib, font=MONO(48), fill=(int(190 * a),) * 3)
        return fr
    f.still = Image.new("RGB", (W, H), (10, 10, 10))
    return f


def build_shot(s, k, assets, prev):
    desc = s["desc"]
    f = assets / f"{s['beat']}_wiz{s['wiz']:02d}.png"
    if re.search("spectrogram", desc, re.I):
        return spectro_shot(desc, k)
    if f.exists():
        return image_shot(f, k)
    if "log sheet" in desc:
        return logsheet_shot(k)
    a = s["asset"]
    if a == "TYTUŁ":
        return title_shot(desc, prev)
    if a == "MAPA":
        return polar_map() if re.search("Southern|Antarc|Bransfield", desc) else pacific_map(desc)
    if a == "PORÓWNANIE":
        return cards_shot(desc) if "cards" in desc and "left" not in desc else compare_shot(desc, assets)
    if a == "CYTAT":
        return quote_shot(desc)
    print("brak źródła dla", s["beat"], s["wiz"], "- czarna klatka")
    return title_shot('"' + desc[:30] + '"', None)


# ───────────── timeline ─────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--assets", required=True)
    ap.add_argument("--voice", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-seconds", type=float, default=0, help="render tylko początku (test)")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    assets, voice = Path(a.assets), Path(a.voice)

    beats = []
    for bid in dict.fromkeys(s["beat"] for s in plan["shots"]):
        vf = voice / f"{bid}.wav"
        vdur = sf.info(str(vf)).duration if vf.exists() else sum(s["dur"] for s in plan["shots"] if s["beat"] == bid)
        lead = LEAD.get(bid, LEAD_DEFAULT)
        beats.append(dict(id=bid, voice=vf if vf.exists() else None, lead=lead, dur=lead + vdur + TAIL))

    timeline, t0, prev, k = [], 0.0, None, 0
    for b in beats:
        shots = [s for s in plan["shots"] if s["beat"] == b["id"]]
        scale = b["dur"] / sum(s["dur"] for s in shots)
        b["start"] = t0
        st = t0
        for s in shots:
            fn = build_shot(s, k, assets, prev)
            d = s["dur"] * scale
            timeline.append((st, d, fn, b["id"]))
            st += d
            prev, k = fn, k + 1
        t0 += b["dur"]
    total = t0 if not a.max_seconds else min(t0, a.max_seconds)
    print(f"długość filmu: {t0:.1f}s, ujęć: {len(timeline)}")

    # efekty globalne
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vign = np.clip(1.15 - 0.55 * r ** 2, 0.25, 1.0)[..., None].astype(np.float32)
    rng = np.random.default_rng(7)
    grains = [np.asarray(Image.fromarray(rng.normal(128, 26, (H // 2, W // 2)).clip(0, 255).astype(np.uint8))
                         .resize((W, H), Image.BILINEAR), dtype=np.float32)[..., None] - 128 for _ in range(12)]
    beat_starts = [b["start"] for b in beats[1:]]

    def frame(t):
        idx = next(i for i, (st, d, _, _) in enumerate(timeline) if t < st + d or i == len(timeline) - 1)
        st, d, fn, _ = timeline[idx]
        img = fn(min(t - st, d), d)
        for bs in beat_starts:  # krótki crossfade na granicy beatów
            if bs <= t < bs + XF and idx > 0:
                pst, pd, pfn, _ = timeline[idx - 1]
                img = Image.blend(pfn(pd, pd), img, ease((t - bs) / XF))
        arr = np.asarray(img, dtype=np.float32) * vign
        arr *= 1.0 + 0.02 * math.sin(t * 23.0)
        arr += grains[int(t * FPS) % len(grains)] * 0.32
        arr *= min(ease(t / 0.6), ease((total - t) / 1.2))
        return np.clip(arr, 0, 255).astype(np.uint8)

    # audio: lektor per beat + drone + szum + ping na starcie + syntetyczny bloop w B02
    sig, sr = bloop_signal()
    sweep = sig[int(0.4 * sr): int(2.3 * sr)]
    bw = Path(a.out).with_name("_bloop.wav")
    with wave.open(str(bw), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((sweep / np.abs(sweep).max() * 0.9 * 32767).astype(np.int16).tobytes())
    inputs, chains, labels = [], [], []
    for b in beats:
        if b["voice"]:
            i = len(inputs) // 2 + 1
            inputs += ["-i", str(b["voice"])]
            ms = int((b["start"] + b["lead"]) * 1000)
            chains.append(f"[{i}:a]aresample=48000,highpass=f=80,acompressor=threshold=-18dB:ratio=3,volume=1.5,adelay={ms}|{ms}[v{i}]")
            labels.append(f"[v{i}]")
    ib = len(inputs) // 2 + 1
    inputs += ["-i", str(bw)]
    b02 = next((b for b in beats if b["id"] == "B02"), beats[0])
    ms = int((b02["start"] + 0.1) * 1000)
    chains.append(f"[{ib}:a]aresample=48000,lowpass=f=400,volume=1.0,adelay={ms}|{ms}[bl]")
    labels.append("[bl]")
    chains += [
        f"sine=f=55:d={total:.2f},volume=0.08[d1]",
        f"anoisesrc=d={total:.2f}:c=brown:a=0.25,lowpass=f=300,volume=0.30[n]",
        "sine=f=1180:d=0.9,afade=t=out:st=0.02:d=0.85,volume=0.3,aecho=0.8:0.7:420:0.35[p1]",
    ]
    labels += ["[d1]", "[n]", "[p1]"]
    mix = ";".join(chains) + ";" + "".join(labels) + (
        f"amix=inputs={len(labels)}:normalize=0,afade=t=in:d=0.5,afade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5,"
        "alimiter=limit=0.9,loudnorm=I=-14:TP=-1.5,aformat=channel_layouts=stereo[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *inputs,
           "-filter_complex", mix, "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", "-movflags", "+faststart", a.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS)
    for i in range(n):
        proc.stdin.write(frame(i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"  {i / FPS:.0f}s / {total:.0f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("zapisano", a.out)


if __name__ == "__main__":
    main()
