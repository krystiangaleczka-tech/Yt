"""Zestaw filmu „Pierwszy cesarz”: wycinki, papiery i scena wzorcowa teatru.

Wycinki postaci i scenografii to PNG z poprzedniego podejścia (output/imperium-papierowe/assets) — jeden styl,
jedno światło. Brakujące elementy (pasma wzgórz, mur, chorągwie królestw, gliniani żołnierze, płomienie, rama sceny)
są wycinane kodem z papierów pobranych z tych samych wycinków, żeby nic nie odstawało.

Układ: kadr wzorcowy 1280 × 720 = cały otwór sceny. Plany głębi (p): patrz PLANY.
"""
import math
import random
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import os
import sys

from papier import CX, CY, H, W, Sprite, back, clamp, ease, ease_out, noise, settle

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "imperium-papierowe" / "assets"

# plany głębi: odwrotność odległości od kamery
PLANY = dict(niebo=0.14, slonce=0.17, chmury=0.21, gory_dal=0.30, rownina=0.36, gory=0.43, miasto=0.50, most=0.57,
             droga=0.64, wzgorza=0.68, drzewa=0.72, lalki=0.80, rekwizyty=0.84, rampa=0.88, rama=1.0)
P = type("P", (), PLANY)


# ---------- wycinki z plików ----------

@lru_cache(None)
def S(name, scale=1.0, rim=2):
    """Wycinek z pliku (raz na proces). scale < 1 zmniejsza duże pliki, których nigdy nie widać z bliska."""
    im = Image.open(ASSETS / f"{name}.png").convert("RGBA")
    if scale != 1.0:
        im = im.resize((round(im.size[0] * scale), round(im.size[1] * scale)), Image.LANCZOS)
    return Sprite(im, name, rim=rim)


@lru_cache(None)
def raw(name):
    return Image.open(ASSETS / f"{name}.png").convert("RGBA")


# ---------- papiery ----------

@lru_cache(None)
def _lum(kind):
    """Faktura papieru (jasność wokół 1,0) do barwienia własnych wycinków."""
    if kind == "gladki":  # gładki papier ryżowy z tła
        im = Image.open(ASSETS / "00-tlo.png").convert("L").crop((0, 0, 1672, 340))
    elif kind == "gnieciony":  # gnieciona bibuła ze słońca
        im = raw("sun").convert("L").crop((500, 250, 1040, 760))
    else:  # „lisc”: fasetki z gór
        im = raw("middle_hill").convert("L").crop((640, 470, 900, 640))
    src = np.asarray(im, np.float32)
    big = np.asarray(im.filter(ImageFilter.GaussianBlur(40)), np.float32)
    lum = src / np.maximum(big, 1)  # bez plam światła, sama faktura
    return np.clip(lum, 0.6, 1.4)


def texture(kind, w, h, seed=0):
    """Faktura w × h: płytki z odbiciem lustrzanym, żeby nie było szwów."""
    lum = _lum(kind)
    th, tw = lum.shape
    tile = np.block([[lum, lum[:, ::-1]], [lum[::-1], lum[::-1, ::-1]]])
    r = random.Random(seed)
    ox, oy = r.randrange(tw * 2), r.randrange(th * 2)
    ys = (np.arange(h) + oy) % (th * 2)
    xs = (np.arange(w) + ox) % (tw * 2)
    return tile[np.ix_(ys, xs)]


def rough_mask(draw_fn, w, h, rough=2.2, seed=0, ss=2):
    """Maska wycięta „ręcznie”: kształt z draw_fn(ImageDraw, skala), krawędź lekko poszarpana jak darty papier."""
    m = Image.new("L", (w * ss, h * ss), 0)
    draw_fn(ImageDraw.Draw(m), ss)
    m = m.resize((w, h), Image.LANCZOS)
    if rough:
        rng = np.random.default_rng(seed)
        n = rng.normal(0, 1, (h // 3 + 2, w // 3 + 2)).astype(np.float32)
        n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC), np.float32)
        soft = np.asarray(m.filter(ImageFilter.GaussianBlur(rough)), np.float32) / 255.0
        n = n * np.clip(8 * soft * (1 - soft), 0, 1)  # szarpie tylko krawędź, nie sypie kropek po tle
        m = Image.fromarray((np.clip((soft - 0.5 + n * 0.16) * 6 + 0.5, 0, 1) * 255).astype(np.uint8))
        m = m.filter(ImageFilter.GaussianBlur(0.6))
    return m


def paper(mask, color, kind="gladki", seed=0, edge=0, edge_color=(244, 232, 205), shade=0.0, contrast=1.0):
    """Barwiony papier w kształcie maski. edge > 0: jasny, darty brzeg (rdzeń papieru), jak w chmurach i górach."""
    w, h = mask.size
    lum = 1 + (texture(kind, w, h, seed) - 1) * contrast
    rgb = np.asarray(color, np.float32)[None, None, :] / 255.0 * lum[..., None]
    if shade:  # delikatne przyciemnienie ku dołowi: arkusz nie jest płaską plamą
        rgb = rgb * (1 - shade * np.linspace(0, 1, h, dtype=np.float32)[:, None, None])
    a = np.asarray(mask, np.float32) / 255.0
    if edge:
        inner = np.asarray(mask.filter(ImageFilter.MinFilter(edge * 2 + 1)).filter(ImageFilter.GaussianBlur(0.8)),
                           np.float32) / 255.0
        band = np.clip(a - inner, 0, 1)[..., None]
        ec = np.asarray(edge_color, np.float32) / 255.0 * (1 + (texture("gladki", w, h, seed + 5) - 1))[..., None]
        rgb = rgb + (ec - rgb) * band * 0.9
    out = np.dstack([np.clip(rgb, 0, 1), a])
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def over(base, top, xy=(0, 0)):
    """Nakleja arkusz na arkusz (z cienkim cieniem pod naklejanym)."""
    sh = Image.new("RGBA", top.size, (30, 18, 10, 0))
    sh.putalpha(top.getchannel("A").filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.45)))
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(sh, (xy[0] + 2, xy[1] + 3))
    layer.alpha_composite(top, xy)
    # naklejka nie wychodzi poza arkusz pod spodem
    a = ImageChops.multiply(layer.getchannel("A"), base.getchannel("A"))
    layer.putalpha(a)
    out = base.copy()
    out.alpha_composite(layer)
    return out


# ---------- scenografia wycinana kodem ----------

@lru_cache(None)
def sky():
    """Papier nieba: duży arkusz, jaśniejszy przy horyzoncie."""
    w, h = 2080, 1280
    lum = texture("gladki", w, h, 3)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    top, mid = np.array([232, 204, 158], np.float32), np.array([248, 228, 188], np.float32)
    k = np.clip(1 - np.abs(yy - 0.52) / 0.5, 0, 1) ** 1.4
    rgb = (top + (mid - top) * k)[:, None, :].reshape(h, 1, 3) / 255.0 * lum[..., None]
    out = np.dstack([np.clip(rgb, 0, 1), np.ones((h, w), np.float32)])
    return Sprite(Image.fromarray((out * 255).astype(np.uint8), "RGBA"), "niebo", rim=0, clean=False, pad=0)


@lru_cache(None)
def plain():
    """Równina z rzeką: dolna część tła, górą dartą linią pod horyzontem."""
    src = Image.open(ASSETS / "00-tlo.png").convert("RGB").crop((0, 400, 1672, 941))
    w, h = src.size
    r = random.Random(11)
    edge = [(x, 34 + 16 * math.sin(x / 190.0) + 9 * math.sin(x / 61.0 + 1) + r.uniform(-3, 3)) for x in range(0, w + 40, 40)]
    m = rough_mask(lambda d, s: d.polygon([(x * s, y * s) for x, y in edge] + [(w * s, h * s), (0, h * s)], fill=255), w, h,
                   rough=2.0, seed=4)
    im = src.convert("RGBA")
    im.putalpha(m)
    return Sprite(im, "rownina", rim=2, clean=False, pad=0)


def _wave(w, seed, base, amp, step=24):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    return [(x, base - amp * (0.6 * math.sin(x / 330.0 + ph[0]) + 0.28 * math.sin(x / 120.0 + ph[1])
                              + 0.12 * math.sin(x / 47.0 + ph[2]))) for x in range(0, w + step, step)]


def _sheet(w, h, seed, base, amp, color, edge=5, contrast=0.9):
    pts = _wave(w, seed, base, amp)
    m = rough_mask(lambda d, s: d.polygon([(x * s, y * s) for x, y in pts] + [(w * s, h * s), (0, h * s)], fill=255), w, h,
                   rough=2.4, seed=seed)
    im = paper(m, color, "gnieciony", seed, edge=edge, shade=0.18, contrast=contrast)
    fine = 1 + (texture("gladki", w, h, seed + 9) - 1) * 1.2  # drobne włókna na gniecionym arkuszu
    arr = np.asarray(im, np.float32)
    arr[..., :3] = np.clip(arr[..., :3] * fine[..., None], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


HILLS = {  # pasmo: (wysokość arkusza, [(linia grzbietu, falowanie, barwa), ...] od najdalszego arkusza)
    "dal": (300, [(120, 44, (168, 170, 128)), (190, 30, (196, 176, 122))]),
    "srodek": (320, [(110, 40, (104, 128, 94)), (176, 34, (140, 150, 104)), (236, 26, (188, 160, 100))]),
    "droga": (260, [(96, 22, (190, 156, 98)), (170, 18, (160, 132, 84))]),
    "przod": (300, [(96, 36, (62, 92, 70)), (150, 30, (88, 114, 80)), (214, 24, (48, 74, 58))]),
}


@lru_cache(None)
def hills(which):
    """Pasma wzgórz na cały kadr, każde z kilku naklejonych arkuszy. Zza nich wychodzą lalki, wozy i mur."""
    h, sheets = HILLS[which]
    w, seed = 2200, sum(map(ord, which))
    im = None
    for i, (base, amp, color) in enumerate(sheets):
        sh = _sheet(w, h, seed + 17 * i, base, amp, color)
        im = sh if im is None else over(im, sh)
    return Sprite(im, f"wzgorza-{which}", rim=2, clean=False, pad=0)


def hill_top(which, x, cx, y_bottom, w=2000):
    """Wysokość (y kadru wzorcowego) górnej krawędzi pasma w punkcie x, gdy pasmo leży środkiem w cx i dołem w y_bottom."""
    spr = hills(which)
    hh = w * spr.h / spr.w
    return y_bottom - hh + spr.top((x - (cx - w / 2)) / w) * hh


@lru_cache(None)
def stage_floor():
    """Rampa sceny: deska na pierwszym planie, zza której wystają lalki."""
    src = raw("table-v3").rotate(12, resample=Image.BICUBIC, expand=False).crop((450, 630, 1250, 790)).convert("RGB")
    w, h = 2400, 150
    tile = Image.new("RGB", (w, h))
    strip = src.resize((800, h), Image.LANCZOS)
    for i, x in enumerate(range(0, w, 800)):
        tile.paste(strip if i % 2 == 0 else strip.transpose(Image.FLIP_LEFT_RIGHT), (x, 0))
    arr = np.asarray(tile, np.float32) / 255.0
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    arr = arr * (1.0 - 0.5 * np.clip((yy - 0.13) / 0.05, 0, 1))  # czoło deski ciemniejsze niż jej wierzch
    arr[:3] = arr[:3] * 1.35 + 0.06  # światło na krawędzi
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return Sprite(im, "rampa", rim=0, clean=False, pad=0)


@lru_cache(None)
def glow(r=256, color=(255, 214, 150)):
    """Miękka poświata (dokładana światłem, mode='add')."""
    yy, xx = np.mgrid[0:r * 2, 0:r * 2].astype(np.float32)
    d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2.2
    rgb = np.asarray(color, np.float32)[None, None] / 255.0 * np.ones((r * 2, r * 2, 1), np.float32)
    out = np.dstack([rgb, a])
    return Sprite(Image.fromarray((out * 255).astype(np.uint8), "RGBA"), "poswiata", rim=0, clean=False, pad=0)


# ---------- scena wzorcowa ----------

GROUND = {"dal": (CX, 690), "srodek": (CX + 60, 766), "droga": (CX - 40, 761), "przod": (CX + 20, 836)}  # środek i dół pasma
MF_X, MF_Y, MF_W = 520, 560, 760  # góra, zza której grani wychodzi mur
RAMPA = 676  # górna krawędź rampy: wszystko na planie lalek stoi za nią


def ground(name, x):
    """Linia ziemi (górna krawędź pasma wzgórz) w punkcie x kadru wzorcowego — tam stoją chorągwie, jeźdźcy i wozy."""
    cx, yb = GROUND[name]
    return hill_top(name, x, cx, yb)


def ridge(x):
    """Grań góry po lewej (wygładzona) — linia, po której idzie mur."""
    spr = S("mountain_front", 0.6)
    hh = MF_W * spr.h / spr.w
    fx = (x - (MF_X - MF_W / 2)) / MF_W
    return MF_Y - hh + sum(spr.top(fx + d) for d in (-0.03, -0.015, 0, 0.015, 0.03)) / 5 * hh


@lru_cache(None)
def moon():
    im = piece(300, 300, ell(150, 150, 140, 140), (236, 228, 204), "gnieciony", edge=0, seed=77, contrast=0.9)
    return Sprite(im, "ksiezyc", rim=2, clean=False)


@lru_cache(None)
def black():
    return Sprite(Image.new("RGBA", (64, 36), (0, 0, 0, 255)), "ciemnosc", rim=0, clean=False, pad=0)

def hang(st, spr, x, y, p, k=1.0, t=0.0, seed=1, drop=520, sway=1.2, string=True, anchor=(0.5, 0.0), strings=(0.5,),
         rot0=0.0, **kw):
    """Wycinek na nitce z góry. k = 0..1 zjazd na miejsce (z przestrzeleniem i gasnącym kołysaniem); potem lekko
    kołysze się sam. (x, y) to punkt zawieszenia: środek górnej krawędzi wycinka."""
    if k <= 0:
        return
    yy = y - (1 - back(k, 1.1)) * drop
    rot = rot0 + settle((k - 0.7) / 0.3 if k < 1 else 0, 2, 3.5) + sway * 0.5 * noise(t, seed, 0.35) + (1 - k) * 4 * math.sin(k * 9)
    hh = kw.get("h") or kw["w"] * spr.h / spr.w
    ww = hh * spr.w / spr.h
    if string:
        for fx in strings:
            fx = min((fx + d * 0.01 for d in range(-9, 10)), key=spr.top)  # nitka trzyma za najwyższy punkt w okolicy
            ax = x + (fx - anchor[0]) * ww * math.cos(math.radians(rot))
            ay = yy + (fx - anchor[0]) * ww * math.sin(math.radians(rot)) + (spr.top(fx) - anchor[1]) * hh + 4
            st.line([(ax, -220), (ax, ay)], p, width=1.1, color=(70, 56, 44), alpha=0.7, z=-0.5)
    st.put(spr, x, yy, p, anchor=anchor, rot=rot, **kw)


def rise(st, spr, x, y, p, k=1.0, t=0.0, seed=1, lift=None, wob=0.5, **kw):
    """Wycinek wysuwany od dołu na patyczku (zza bliższego planu). k = 0..1 wyjście; potem lekko drży."""
    if k <= 0:
        return
    hh = kw.get("h") or kw["w"] * spr.h / spr.w
    lift = lift if lift is not None else hh * 1.08
    yy = y + (1 - back(k, 1.3)) * lift
    rot = settle((k - 0.75) / 0.25 if k < 1 else 0, 1.5, 2.5) + wob * noise(t, seed, 0.5)
    st.put(spr, x, yy, p, rot=rot, **kw)


def plan(st, t, sun=1.0, clouds=(1.0, 1.0, 1.0), far=1.0, land=1.0, mid=1.0, city=1.0, bridge=1.0, trees=(1.0, 1.0),
         road=1.0, front=1.0, floor=1.0, sun_xy=(905, 96), city_x=930, haze=1.0, night=0.0):
    """Stała scenografia teatru. Każdy element ma stopień obecności 0..1 (0 — jeszcze go nie ma, 1 — stoi):
    niebo wisi na nitkach, ziemia i budowle wysuwają się od dołu. Ujęcia dokładają lalki i rekwizyty."""
    hz = lambda v: v * haze
    st.put(sky(), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None,
           tint=(1 - 0.62 * night, 1 - 0.54 * night, 1 - 0.28 * night))  # nocą papier nieba ciemnieje najmocniej
    if sun > 0:
        st.put(glow(), sun_xy[0], sun_xy[1] + 85 - (1 - back(sun, 1.1)) * 520, P.slonce, w=620, anchor=(0.5, 0.5),
               mode="add", alpha=0.30 * ease(sun), shadow=None, z=-1)
    hang(st, S("sun", 0.5), sun_xy[0], sun_xy[1], P.slonce, sun, t, 1, w=176, shadow=(5, 7, 9, 0.30), haze=hz(0.10))
    for i, (name, x, y, w) in enumerate((("cloud_left", 250, 64, 560), ("cloud_center", 700, 28, 620),
                                         ("cloud_right", 1080, 150, 500))):
        hang(st, S(name, 0.5), x + 6 * noise(t, 30 + i, 0.08), y, P.chmury + i * 0.008, clouds[i], t, 4 + i, w=w,
             sway=0.5, strings=(0.3, 0.7), shadow=(7, 10, 11, 0.26), haze=hz(0.08))
    rise(st, S("mountain_dark", 0.6), 430, 446, P.gory_dal, far, t, 11, w=980, wob=0.0, haze=hz(0.46),
         shadow=(6, 6, 10, 0.25))
    rise(st, S("mountain_gold", 0.6), 1030, 456, P.gory_dal + 0.02, far, t, 12, w=560, wob=0.0, haze=hz(0.38),
         shadow=(6, 6, 10, 0.25))
    rise(st, plain(), CX, 1030, P.rownina, land, t, 13, w=1960, wob=0.0, lift=420, haze=hz(0.20), shadow=(4, -5, 10, 0.3))
    rise(st, S("mountain_front", 0.6), MF_X, MF_Y, P.gory, mid, t, 14, w=MF_W, wob=0.0, haze=hz(0.18))
    for name, pp, k in (("dal", P.gory + 0.02, mid), ("srodek", P.miasto + 0.03, city), ("droga", P.droga + 0.02, road),
                        ("przod", P.wzgorza + 0.05, front)):
        if name == "srodek":
            rise(st, S("city_gate"), city_x, 590, P.miasto, city, t, 16, w=430, wob=0.0, haze=hz(0.08))
        if name == "droga":
            rise(st, S("bridge", 0.6), 600, 648, P.most, bridge, t, 18, w=450, wob=0.0, haze=hz(0.04))
        if name == "droga":  # sosna za chorągwiami i drogą: nie zasłania tego, co się na niej dzieje
            rise(st, S("tree_right"), 1196, 654, P.most + 0.015, trees[1], t, 21, h=240, wob=0.35, haze=hz(0.03))
        cx, yb = GROUND[name]
        rise(st, hills(name), cx, yb, pp, k, t, 15 + len(name), w=2000, wob=0.0, lift=320,
             haze=hz({"dal": 0.16, "srodek": 0.06}.get(name, 0.0)))
    rise(st, S("tree_left"), 4, 700, P.drzewa + 0.02, trees[0], t, 22, h=300, wob=0.35)
    if floor > 0:
        st.put(stage_floor(), CX, 676 + (1 - ease_out(floor)) * 90, P.rampa, w=2100, anchor=(0.5, 0.0),
               shadow=(0, -7, 9, 0.45))


# ---------- wycinanki składane z kawałków papieru ----------

def _font(cands):
    """Pierwsza istniejąca czcionka z listy (macOS, potem Windows): (ścieżka, indeks w pliku .ttc)."""
    for path, idx in cands:
        if Path(path).exists():
            return path, idx
    raise FileNotFoundError(f"Brak czcionki: {cands}")


# znaki chińskie i napisy: na macOS Songti i Baskerville, na Windows SimSun i Georgia (pogrubiona)
FONT_ZH, ZH_IDX = _font([("/System/Library/Fonts/Supplemental/Songti.ttc", 1), ("C:/Windows/Fonts/simsun.ttc", 0),
                         ("C:/Windows/Fonts/msyh.ttc", 0), ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 0)])
FONT_PL, PL_IDX = _font([("/System/Library/Fonts/Supplemental/Baskerville.ttc", 4), ("C:/Windows/Fonts/georgiab.ttf", 0),
                         ("C:/Windows/Fonts/timesbd.ttf", 0), ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 0)])


def poly(pts):
    return lambda d, s: d.polygon([(x * s, y * s) for x, y in pts], fill=255)


def ell(cx, cy, rx, ry):
    return lambda d, s: d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=255)


def glyphs(txt, size, font=FONT_PL, index=0, xy=(0, 0), anchor="la", spacing=0):
    def fn(d, s):
        f = ImageFont.truetype(font, int(size * s), index=index)
        if spacing:
            x = xy[0] * s
            for ch in txt:
                d.text((x, xy[1] * s), ch, font=f, fill=255, anchor=anchor)
                x += d.textlength(ch, font=f) + spacing * s
        else:
            d.text((xy[0] * s, xy[1] * s), txt, font=f, fill=255, anchor=anchor)
    return fn


def piece(w, h, shape, color, kind="gnieciony", edge=0, seed=0, rough=1.3, contrast=0.8, shade=0.0):
    return paper(rough_mask(shape, w, h, rough, seed), color, kind, seed, edge=edge, contrast=contrast, shade=shade)


def glue(base, top, shadow=0.42, off=(2, 3), soft=2.5):
    """Nakleja kawałek na wycinankę; pod kawałkiem zostaje cienki cień — widać, że to osobny papier."""
    out = base.copy()
    if shadow:
        sh = Image.new("RGBA", top.size, (28, 16, 10, 0))
        sh.putalpha(top.getchannel("A").filter(ImageFilter.GaussianBlur(soft)).point(lambda v: int(v * shadow)))
        clip = Image.new("RGBA", base.size, (0, 0, 0, 0))
        clip.alpha_composite(sh, off)
        clip.putalpha(ImageChops.multiply(clip.getchannel("A"), base.getchannel("A")))  # cień tylko na papierze pod spodem
        out.alpha_composite(clip)
    out.alpha_composite(top)
    return out


def stack(w, h, parts, seed=0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i, part in enumerate(parts):
        shape, color = part[0], part[1]
        opt = part[2] if len(part) > 2 else {}
        im = glue(im, piece(w, h, shape, color, seed=seed + i * 7, **opt))
    return im


# chorągwie siedmiu królestw: ta sama chorągiew ze smokiem, płótno w barwie królestwa, znak na krążku
KINGDOMS = {"qin": ("秦", (46, 44, 50)), "han": ("韓", (74, 124, 88)), "zhao": ("趙", (60, 98, 156)),
            "wei": ("魏", (206, 160, 70)), "chu": ("楚", (178, 52, 44)), "yan": ("燕", (64, 138, 146)),
            "qi": ("齊", (128, 78, 150))}


@lru_cache(None)
def banner(kingdom):
    src = raw("banner").crop((270, 0, 760, 1536))
    arr = np.asarray(src, np.float32) / 255.0
    rgb, a = arr[..., :3], arr[..., 3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cloth = np.clip((r - np.maximum(g, b) * 1.45) * 6, 0, 1)  # czerwone płótno; złoty smok i drzewce zostają
    sign, color = KINGDOMS[kingdom]
    lum = r / max(float((r * cloth).sum() / max(cloth.sum(), 1)), 0.05)
    new = np.asarray(color, np.float32)[None, None] / 255.0 * np.clip(lum, 0.35, 1.7)[..., None]
    rgb = rgb + (new - rgb) * cloth[..., None]
    im = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a]) * 255).astype(np.uint8), "RGBA")
    w, h = im.size
    disc = piece(w, h, ell(248, 330, 120, 120), (240, 226, 196), "gladki", edge=5, seed=3, contrast=1.2)
    disc = glue(disc, piece(w, h, glyphs(sign, 168, FONT_ZH, ZH_IDX, (248, 334), "mm"), (30, 24, 22), "gladki", rough=0.8))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    lay.alpha_composite(disc)
    sh = Image.new("RGBA", im.size, (20, 10, 6, 0))
    sh.putalpha(disc.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.5)))
    im.alpha_composite(sh, (5, 7))
    im.alpha_composite(lay)
    return Sprite(im, f"choragiew-{kingdom}", rim=2)


@lru_cache(None)
def wall(which):
    """Kawałki muru wycięte z bramy miasta: odcinek z blankami i wieża strażnicza."""
    box = {"mur": (1130, 428, 1282, 700), "wieza": (350, 262, 598, 700), "wieza2": (66, 284, 345, 700)}[which]
    im = raw("city_gate").crop(box)
    a = np.asarray(im.getchannel("A"), np.float32).copy()
    if which == "wieza":
        a[:70, 222:] = 0  # róg dachu sąsiedniej wieży
    fade = np.clip((im.size[1] - np.arange(im.size[1], dtype=np.float32)) / 40.0, 0, 1)[:, None]
    im.putalpha(Image.fromarray((a * fade).astype(np.uint8)))  # dół i tak chowa się za granią
    return Sprite(im, f"mur-{which}", rim=2)


CLAY = ((186, 128, 92), (150, 100, 70), (212, 160, 122), (118, 78, 56))


@lru_cache(None)
def soldier(v=0):
    """Gliniany żołnierz: wycinanka z kilku kawałków papieru w barwie terakoty. v — odmiana (kok, odcień, postura)."""
    r = random.Random(100 + v)
    k = 0.92 + 0.16 * r.random()
    base, dark, light, deep = [tuple(int(c * k) for c in col) for col in CLAY]
    w, h = 300, 660
    side = 1 if v % 2 == 0 else -1
    X = lambda x: 150 + (x - 150) * side
    P_ = lambda pts: poly([(X(x), y) for x, y in pts])
    parts = [
        (P_([(106, 420), (147, 420), (146, 618), (102, 618)]), dark), (P_([(153, 420), (194, 420), (198, 618), (154, 618)]), dark),
        (P_([(92, 610), (148, 610), (150, 646), (88, 646)]), deep), (P_([(152, 610), (208, 610), (212, 646), (150, 646)]), deep),
        (P_([(90, 300), (210, 300), (226, 476), (74, 476)]), dark),
        (P_([(66, 182), (106, 172), (102, 330), (88, 398), (58, 394), (54, 300)]), dark),
        (P_([(234, 182), (194, 172), (198, 330), (212, 398), (242, 394), (246, 300)]), dark),
        (ell(X(72), 408, 16, 18), light), (ell(X(228), 408, 16, 18), light),
        (P_([(94, 166), (206, 166), (218, 380), (82, 380)]), base, dict(edge=2)),
        (P_([(62, 176), (108, 168), (112, 236), (70, 246)]), dark, dict(edge=2)),
        (P_([(238, 176), (192, 168), (188, 236), (230, 246)]), dark, dict(edge=2)),
        (P_([(134, 132), (166, 132), (170, 172), (130, 172)]), light),
        (ell(150, 170, 44, 17), light, dict(edge=2)),
        (ell(150, 102, 41, 52), light, dict(edge=2)),
        (P_([(108, 96), (112, 62), (136, 46), (168, 46), (190, 64), (192, 96), (172, 74), (128, 74)]), deep),
        (ell(X(176), 38, 23, 19), deep, dict(edge=2)),
    ]
    im = stack(w, h, parts, seed=200 + v)
    d = ImageDraw.Draw(im)
    ink = deep + (230,)
    for yy in (214, 254, 294, 334):  # płytki pancerza
        d.line([(92 - (yy - 166) * 0.05, yy), (208 + (yy - 166) * 0.05, yy)], fill=ink, width=3)
    for xx in (122, 150, 178):
        d.line([(xx, 176), (xx + (xx - 150) * 0.06, 376)], fill=ink, width=2)
    for xx in (108, 136, 164, 192):
        for yy in (234, 274, 314, 354):
            d.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=ink)
    d.line([(123, 91), (144, 92)], fill=ink, width=4)  # brwi, oczy, nos, wąsy: spokojna, nieruchoma twarz
    d.line([(156, 92), (177, 91)], fill=ink, width=4)
    for ex in (134, 166):
        d.ellipse([ex - 8, 99, ex + 8, 109], fill=light + (255,), outline=ink, width=2)
        d.ellipse([ex - 3, 101, ex + 3, 107], fill=ink)
    d.line([(150, 100), (148, 122), (155, 123)], fill=ink, width=3)
    d.line([(131, 134), (146, 129), (154, 129), (169, 134)], fill=ink, width=4)
    d.line([(141, 143), (159, 143)], fill=ink, width=2)
    return Sprite(im, f"zolnierz-{v}", rim=2, clean=False)


@lru_cache(None)
def spears(seed=0, n=40, w=1000, h=300, flag=(30, 28, 32)):
    """Las włóczni: wojsko idące za wzgórzem — widać tylko groty i proporce."""
    r = random.Random(seed)
    ss = 2
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(n):
        x = (20 + (w - 40) * (i + r.uniform(-0.3, 0.3)) / n) * ss
        top = r.uniform(10, 120) * ss
        lean = r.uniform(-9, 9) * ss
        col = (38, 30, 28, 255)
        d.line([(x, h * ss), (x + lean, top)], fill=col, width=3 * ss)
        d.polygon([(x + lean, top - 26 * ss), (x + lean - 6 * ss, top), (x + lean + 6 * ss, top)], fill=(64, 56, 50, 255))
        if i % 4 == 1:
            fy = top + r.uniform(14, 40) * ss
            d.polygon([(x + lean * 0.9, fy), (x + lean * 0.9 + 44 * ss, fy + 9 * ss), (x + lean * 0.9, fy + 26 * ss)],
                      fill=flag + (255,))
    for i in range(n // 2):  # hełmy między włóczniami
        x = (30 + (w - 60) * (i + r.uniform(-0.3, 0.3)) / (n // 2)) * ss
        y = (h - r.uniform(8, 34)) * ss
        d.ellipse([x - 13 * ss, y - 15 * ss, x + 13 * ss, y + 15 * ss], fill=(52, 44, 40, 255))
        d.polygon([(x - 4 * ss, y - 13 * ss), (x, y - 27 * ss), (x + 4 * ss, y - 13 * ss)], fill=(120, 34, 30, 255))
    im = im.resize((w, h), Image.LANCZOS)
    tex = texture("gladki", w, h, seed)
    arr = np.asarray(im, np.float32)
    arr[..., :3] = np.clip(arr[..., :3] * (1 + (tex[..., None] - 1) * 2), 0, 255)
    return Sprite(Image.fromarray(arr.astype(np.uint8), "RGBA"), "wlocznie", rim=1, clean=False)


@lru_cache(None)
def flame(i):
    """Język ognia z bibuły: czerwony, pomarańczowy albo żółty."""
    color = ((196, 52, 34), (228, 104, 40), (244, 170, 60), (250, 220, 130))[i % 4]
    r = random.Random(300 + i)
    w, h = 220, 420
    bend = r.uniform(-0.5, 0.5)
    pts = []
    for k in range(0, 21):  # lewa krawędź w górę, prawa w dół: łezka z wygiętym czubkiem
        f = k / 20
        pts.append((110 - 78 * math.sin(f * math.pi) ** 0.8 * (1 - f * 0.45) + bend * 70 * f * f, 410 - 400 * f))
    for k in range(20, -1, -1):
        f = k / 20
        pts.append((110 + 78 * math.sin(f * math.pi) ** 0.8 * (1 - f * 0.6) + bend * 70 * f * f, 410 - 400 * f))
    im = piece(w, h, poly(pts), color, "gnieciony", edge=0, seed=i, rough=1.6, contrast=0.7)
    return Sprite(im, f"plomien-{i}", rim=2, clean=False)


@lru_cache(None)
def coin():
    """Moneta banliang: krążek z kwadratową dziurką i dwoma znakami 半兩."""
    w = h = 420
    im = piece(w, h, ell(210, 210, 196, 196), (176, 138, 66), "gnieciony", edge=0, seed=5, contrast=1.1)
    ring = rough_mask(ell(210, 210, 180, 180), w, h, 1.0, 6)
    field = paper(ring, (150, 118, 58), "gnieciony", 7, contrast=1.2)
    im = glue(im, field, shadow=0.5, off=(3, 4))
    for ch, x in (("半", 322), ("兩", 98)):
        im = glue(im, piece(w, h, glyphs(ch, 112, FONT_ZH, ZH_IDX, (x, 214), "mm"), (206, 170, 92), "gladki", rough=0.7),
                  shadow=0.6, off=(2, 3), soft=1.5)
    a = np.asarray(im.getchannel("A")).copy()
    hole = np.asarray(rough_mask(poly([(168, 168), (252, 168), (252, 252), (168, 252)]), w, h, 1.0, 8))
    im.putalpha(Image.fromarray((a * (1 - hole / 255.0)).astype(np.uint8)))
    return Sprite(im, "moneta", rim=3, clean=False)


@lru_cache(None)
def weight():
    """Odważnik z brązu: dzwon z uchem, na boku znak wagi."""
    w, h = 300, 330
    body = [(96, 120), (204, 120), (246, 300), (54, 300)]
    parts = [(lambda d, s: d.arc([116 * s, 62 * s, 184 * s, 176 * s], 180, 360, fill=255, width=int(18 * s)), (74, 92, 74)),
             (poly(body), (92, 112, 88), dict(edge=0, contrast=1.3)),
             (poly([(92, 136), (208, 136), (212, 152), (88, 152)]), (136, 150, 110)),
             (poly([(60, 276), (240, 276), (246, 300), (54, 300)]), (60, 78, 62)),
             (glyphs("斤", 104, FONT_ZH, ZH_IDX, (150, 214), "mm"), (170, 176, 128), dict(kind="gladki", rough=0.7))]
    return Sprite(stack(w, h, parts, seed=40), "odwaznik", rim=2, clean=False)


JEZYK = os.environ.get("JEZYK", "pl")


def tr(txt):
    """Napis na wycinku w języku filmu (JEZYK=en: kwestie_en.ETYKIETY)."""
    if JEZYK != "en":
        return txt
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "docs/filmy/pierwszy-cesarz/ujecia"))
    from kwestie_en import ETYKIETY
    return ETYKIETY.get(txt, txt)


@lru_cache(None)
def tag(txt, size=44):
    """Papierowa zawieszka z napisem (rok, nazwa) — zjeżdża na nitce."""
    txt = tr(txt)
    f = ImageFont.truetype(FONT_PL, size * 2, index=PL_IDX)
    tw = int(f.getlength(txt) / 2)
    w, h = tw + 64, size + 44
    parts = [(poly([(4, 4), (w - 4, 4), (w - 4, h - 4), (4, h - 4)]), (240, 226, 194), dict(kind="gladki", edge=4, contrast=1.3)),
             (glyphs(txt, size, FONT_PL, PL_IDX, (w / 2, h / 2 + 2), "mm"), (48, 30, 24), dict(kind="gladki", rough=0.5))]
    return Sprite(stack(w, h, parts, seed=len(txt)), f"zawieszka-{txt}", rim=2, clean=False)


@lru_cache(None)
def theatre():
    """Rama teatru (plan 1,0): ciemność widowni, czerwona skrzynia sceny ze złotą listwą i szyld z tytułem.
    Otwór sceny to dokładnie kadr wzorcowy 0..1280 × 0..720; układ arkusza: początek w (-760, -470)."""
    ox, oy, w, h = 760, 470, 2800, 1700
    R = lambda x0, y0, x1, y1: poly([(x0 + ox, y0 + oy), (x1 + ox, y0 + oy), (x1 + ox, y1 + oy), (x0 + ox, y1 + oy)])
    red, red2, gold, dark = (126, 30, 26), (94, 22, 20), (206, 164, 84), (20, 15, 13)
    im = piece(w, h, poly([(0, 0), (w, 0), (w, h), (0, h)]), dark, "gladki", rough=0, contrast=0.8)
    box = piece(w, h, R(-124, -214, 1404, 846), red, "gnieciony", edge=0, seed=1, contrast=0.9)
    im = glue(im, box, shadow=0.8, off=(10, 14), soft=14)
    parts = [(R(-124, -214, 1404, -196), gold), (R(-124, 828, 1404, 846), gold), (R(-124, -214, -106, 846), gold),
             (R(1386, -214, 1404, 846), gold),
             (R(-64, -52, 1344, -30), gold), (R(-30, -30, 1310, -8), red2), (R(-30, 728, 1310, 750), red2),
             (R(-30, -30, -8, 750), red2), (R(1288, -30, 1310, 750), red2),
             (R(-64, 750, 1344, 772), gold),
             (R(-10, -10, 1290, 0), gold), (R(-10, 720, 1290, 730), gold), (R(-10, -10, 0, 730), gold),
             (R(1280, -10, 1290, 730), gold)]
    for i, (shape, color) in enumerate(parts):
        im = glue(im, piece(w, h, shape, color, "gnieciony", seed=20 + i, contrast=0.9), shadow=0.5)
    # szyld z tytułem na gzymsie
    sign = piece(w, h, R(250, -176, 1030, -74), (30, 22, 20), "gladki", edge=0, seed=50, contrast=1.5)
    im = glue(im, sign, shadow=0.7, off=(5, 7), soft=6)
    for shape in (R(250, -176, 1030, -168), R(250, -82, 1030, -74), R(250, -176, 258, -74), R(1022, -176, 1030, -74)):
        im = glue(im, piece(w, h, shape, gold, "gnieciony", seed=61, contrast=0.9), shadow=0.4)
    title = glyphs(tr("PIERWSZY CESARZ"), 58, FONT_PL, PL_IDX, (640 + ox, -122 + oy), "mm", spacing=0)
    im = glue(im, piece(w, h, title, (226, 186, 104), "gladki", rough=0.6, contrast=1.2), shadow=0.7, off=(2, 3), soft=1.5)
    a = np.asarray(im.getchannel("A")).copy()
    a[oy:oy + H, ox:ox + W] = 0  # otwór sceny
    im.putalpha(Image.fromarray(a))
    return Sprite(im, "teatr", rim=0, clean=False, pad=0)


def theatre_put(st, light=1.0):
    """Rama teatru przed wszystkim. light — ile światła pada na front (0 = sama sylwetka w ciemności)."""
    spr = theatre()
    st.put(spr, -760, -470, P.rama, w=spr.w, anchor=(0.0, 0.0), shadow=(0, 10, 18, 0.55), blur=0,
           tint=(light, light, light))


# ---------- lalki przebarwione: ta sama wycinanka, inne obszycie szaty = inna postać ----------

LALKI = {"zheng": ("emperor", None), "uczony": ("scholar_left", None), "uczony2": ("scholar_back", None),
         "kleczy": ("scholar_center", None), "pisarz": ("scribe", None),
         "ojciec": ("scholar_back", (132, 104, 74)), "kupiec": ("scholar_back", (132, 62, 146)),
         "lisi": ("scholar_left", (56, 130, 86)), "zhaogao": ("scholar_back", (108, 114, 130)),
         "jingke": ("scholar_left", (222, 208, 176)), "fusu": ("scholar_left", (60, 104, 176)),
         "huhai": ("emperor", (70, 120, 160))}


@lru_cache(None)
def lalka(key):
    if key == "zheng_dziecko":  # przed koronacją: prosta granatowa szata bez smoków
        return Sprite(stroj(dziecko(korona=False), "dziecko", **STROJE["zheng_dziecko"][1]), f"lalka-{key}", rim=2)
    if key == "zheng_krol":
        return Sprite(dziecko(korona=True), f"lalka-{key}", rim=2)
    if key in STROJE:  # cała szata w innym materiale i barwie (nie tylko obszycie): postać nie wygląda jak urzędnik dworu
        name, kw = STROJE[key]
        im = stroj(raw(name), name, **kw)
        im = im.resize((round(im.size[0] * 0.7), round(im.size[1] * 0.7)), Image.LANCZOS)
        return Sprite(im, f"lalka-{key}", rim=2)
    name, color = LALKI[key]
    scale = 1.0 if name == "emperor" else 0.7
    if color is None:
        return S(name, scale)
    arr = np.asarray(raw(name), np.float32) / 255.0
    rgb, a = arr[..., :3], arr[..., 3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cloth = np.clip((r - np.maximum(g, b) * 1.45) * 6, 0, 1)
    lum = r / max(float((r * cloth).sum() / max(cloth.sum(), 1)), 0.05)
    new = np.asarray(color, np.float32)[None, None] / 255.0 * np.clip(lum, 0.35, 1.7)[..., None]
    rgb = rgb + (new - rgb) * cloth[..., None]
    im = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a]) * 255).astype(np.uint8), "RGBA")
    im = im.resize((round(im.size[0] * scale), round(im.size[1] * scale)), Image.LANCZOS)
    return Sprite(im, f"lalka-{key}", rim=2)


# ---------- sala tronowa ----------

GOLD, LAKA = (206, 164, 84), (140, 38, 30)


def rect(x0, y0, x1, y1):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


@lru_cache(None)
def hall_wall():
    """Tylna ściana sali: ciemna laka, złoty fryz, pięć okien z kratą (otwory — widać przez nie niebo i to, co za murem)."""
    w, h = 2100, 800
    im = piece(w, h, rect(0, 0, w, h), (92, 34, 30), "gnieciony", rough=0, contrast=0.8, shade=0.25)
    for i, (y0, y1, col) in enumerate(((70, 82, GOLD), (104, 112, GOLD), (560, 572, GOLD), (572, 800, (62, 24, 22)))):
        im = glue(im, piece(w, h, rect(0, y0, w, y1), col, "gnieciony", seed=i, rough=0.6, contrast=0.9), shadow=0.4)
    a = np.asarray(im.getchannel("A")).copy()
    wins = [(250 + i * 400 - 80, 170, 250 + i * 400 + 80, 470) for i in range(5)]
    for x0, y0, x1, y1 in wins:
        a[y0:y1, x0:x1] = 0
    im.putalpha(Image.fromarray(a))
    bars = []
    for x0, y0, x1, y1 in wins:
        bars += [rect(x0 - 10, y0 - 10, x1 + 10, y0), rect(x0 - 10, y1, x1 + 10, y1 + 10), rect(x0 - 10, y0, x0, y1), rect(x1, y0, x1 + 10, y1)]
        bars += [rect(x, y0, x + 6, y1) for x in range(x0 + 37, x1 - 10, 40)] + [rect(x0, y, x1, y + 6) for y in range(y0 + 46, y1 - 10, 50)]
    def all_bars(d, s):
        for b in bars:
            b(d, s)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lay.alpha_composite(piece(w, h, all_bars, GOLD, "gnieciony", seed=9, rough=0.5, contrast=0.9))
    im.alpha_composite(lay)
    return Sprite(im, "sala-sciana", rim=0, clean=False, pad=0)


@lru_cache(None)
def column():
    w, h = 130, 900
    im = piece(w, h, rect(8, 0, w - 8, h), LAKA, "gnieciony", rough=1.0, contrast=0.9)
    arr = np.asarray(im, np.float32)
    xx = np.abs(np.linspace(-1, 1, w, dtype=np.float32))[None, :, None]
    arr[..., :3] *= 1 - 0.42 * xx ** 1.6  # walec: ciemniejszy przy krawędziach
    im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    for i, (y0, y1) in enumerate(((0, 34), (44, 52), (822, 830), (840, 900))):
        im = glue(im, piece(w, h, rect(0, y0, w, y1), GOLD, "gnieciony", seed=i, rough=0.6), shadow=0.5)
    return Sprite(im, "kolumna", rim=2, clean=False)


@lru_cache(None)
def dais():
    w, h = 460, 96
    parts = [(rect(0, 46, w, h), (70, 26, 22)), (rect(0, 46, w, 54), GOLD), (rect(44, 0, w - 44, 50), LAKA), (rect(44, 0, w - 44, 9), GOLD)]
    return Sprite(stack(w, h, parts, seed=70), "podwyzszenie", rim=2, clean=False)


# ---------- morze ----------

@lru_cache(None)
def waves(i):
    """Pasmo fal z papieru: ząbkowany grzbiet z jasną pianą."""
    color = ((64, 116, 132), (46, 92, 116), (78, 132, 140), (36, 74, 100))[i % 4]
    w, h = 2500, 230
    pts = [(x, 34 + 20 * (1 - abs(math.sin(math.pi * (x + i * 37) / 104))) ** 1.6) for x in range(0, w + 8, 8)]
    m = rough_mask(lambda d, s: d.polygon([(x * s, y * s) for x, y in pts] + [(w * s, h * s), (0, h * s)], fill=255), w, h, rough=1.2, seed=i)
    return Sprite(paper(m, color, "gnieciony", 30 + i, edge=4, shade=0.3, contrast=0.9), f"fale-{i}", rim=2, clean=False, pad=0)


@lru_cache(None)
def boat():
    w, h = 280, 260
    parts = [(lambda d, s: d.line([(140 * s, 34 * s), (140 * s, 196 * s)], fill=255, width=int(7 * s)), (60, 44, 34)),
             (poly([(84, 44), (204, 54), (212, 168), (76, 168)]), (226, 206, 168), dict(kind="gladki", edge=3, contrast=1.3)),
             (poly([(14, 176), (40, 190), (236, 190), (268, 166), (238, 232), (46, 232)]), (86, 56, 40), dict(edge=2)),
             (poly([(140, 18), (184, 28), (140, 40)]), (170, 46, 40))]
    im = stack(w, h, parts, seed=80)
    d = ImageDraw.Draw(im)
    for y in (76, 106, 136):  # listwy żagla
        d.line([(80, y + 2), (210, y + 8)], fill=(96, 70, 50, 230), width=3)
    return Sprite(im, "dzonka", rim=2, clean=False)


# ---------- mapa siedmiu królestw ----------

MAPA = {"qin": [(24, 96), (176, 60), (204, 210), (176, 330), (44, 360)], "zhao": [(186, 52), (334, 40), (342, 152), (210, 164)],
        "yan": [(346, 30), (506, 22), (524, 122), (354, 142)], "qi": [(446, 132), (594, 122), (602, 244), (454, 252)],
        "wei": [(214, 172), (344, 162), (444, 258), (352, 244), (218, 252)], "han": [(218, 258), (336, 250), (326, 314), (214, 322)],
        "chu": [(184, 336), (336, 322), (446, 264), (604, 252), (594, 402), (194, 402)]}
MAPA_WH = (628, 424)


@lru_cache(None)
def map_board():
    w, h = MAPA_WH
    return Sprite(piece(w, h, rect(2, 2, w - 2, h - 2), (236, 220, 186), "gladki", edge=5, seed=90, contrast=1.4), "mapa", rim=2,
                  clean=False, pad=0, crop=False)


@lru_cache(None)
def map_piece(k, czarny=False):
    w, h = MAPA_WH
    pts = MAPA[k]
    color = KINGDOMS["qin"][1] if czarny else KINGDOMS[k][1]
    im = piece(w, h, poly(pts), color, "gnieciony", edge=3, seed=91 + len(k) + czarny, contrast=0.9)
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    sign = KINGDOMS["qin" if czarny else k][0]
    ink = (226, 214, 184) if (czarny or k == "qin") else (30, 24, 22)
    im = glue(im, piece(w, h, glyphs(sign, 44, FONT_ZH, ZH_IDX, (cx, cy), "mm"), ink, "gladki", rough=0.5), shadow=0)
    return Sprite(im, f"mapa-{k}-{czarny}", rim=2, clean=False, pad=0, crop=False)


# ---------- drobne rekwizyty wycinane kodem ----------

@lru_cache(None)
def prop(key):
    if key == "sztylet":
        w, h, parts = 210, 60, [(poly([(70, 22), (196, 30), (70, 40)]), (206, 208, 204), dict(kind="gladki")),
                               (rect(8, 24, 64, 38), (58, 40, 30)), (rect(60, 14, 72, 48), GOLD)]
    elif key == "miecz":
        w, h, parts = 440, 44, [(poly([(96, 14), (430, 22), (96, 30)]), (208, 210, 206), dict(kind="gladki")),
                               (rect(8, 16, 90, 28), (58, 40, 30)), (rect(84, 4, 98, 40), GOLD)]
    elif key == "szkatula":
        w, h, parts = 170, 130, [(rect(6, 30, 164, 126), (120, 34, 28)), (rect(0, 14, 170, 40), (150, 44, 34)),
                                (rect(0, 36, 170, 44), GOLD), (rect(74, 44, 96, 70), GOLD)]
    elif key == "torba":
        w, h, parts = 120, 120, [(ell(60, 72, 50, 42), (176, 140, 84), dict(edge=2)), (poly([(44, 36), (76, 36), (86, 8), (34, 8)]), (176, 140, 84)),
                                (rect(40, 30, 80, 40), (120, 44, 36))]
    elif key == "czarka":
        w, h, parts = 120, 110, [(poly([(10, 10), (110, 10), (88, 76), (32, 76)]), (96, 116, 92), dict(contrast=1.3)),
                                (rect(8, 6, 112, 18), (140, 152, 112)), (rect(46, 76, 74, 96), (74, 92, 74)), (rect(30, 94, 90, 106), (74, 92, 74))]
    elif key == "kulka":
        w, h, parts = 64, 64, [(ell(32, 32, 28, 28), (198, 204, 212), dict(kind="gladki")), (ell(23, 22, 9, 8), (244, 246, 250), dict(kind="gladki"))]
    elif key == "strzala":
        w, h, parts = 150, 18, [(rect(10, 7, 132, 11), (70, 52, 38)), (poly([(128, 2), (148, 9), (128, 16)]), (60, 60, 64)),
                               (poly([(2, 2), (26, 9), (2, 16)]), (226, 214, 190))]
    elif key == "wlocznia":
        w, h, parts = 22, 260, [(rect(9, 30, 13, 258), (58, 42, 32)), (poly([(11, 2), (19, 34), (3, 34)]), (150, 152, 150))]
    elif key == "poletko":
        w, h, parts = 96, 28, [(poly([(8, 2), (94, 2), (88, 26), (2, 26)]), (120, 150, 84), dict(edge=2))]
    elif key == "kamien":
        w, h, parts = 110, 92, [(poly([(14, 30), (52, 6), (96, 22), (104, 60), (70, 86), (24, 78), (6, 54)]), (74, 68, 66), dict(edge=2, contrast=1.3))]
    elif key == "stela":
        w, h, parts = 84, 140, [(poly([(10, 136), (10, 34), (24, 12), (60, 12), (74, 34), (74, 136)]), (150, 146, 136), dict(contrast=1.2)),
                               (glyphs("皇", 30, FONT_ZH, ZH_IDX, (42, 50), "mm"), (56, 52, 48), dict(kind="gladki", rough=0.5)),
                               (glyphs("帝", 30, FONT_ZH, ZH_IDX, (42, 92), "mm"), (56, 52, 48), dict(kind="gladki", rough=0.5))]
    elif key == "mlot":
        w, h, parts = 110, 110, [(rect(48, 4, 62, 60), (70, 52, 38)), (ell(55, 72, 36, 34), (46, 44, 48), dict(contrast=1.3)),
                                (ell(44, 60, 9, 7), (96, 96, 102))]
    elif key == "ryby":
        fish = lambda x, y, r: [(poly([(x - 34, y), (x - 10, y - 11), (x + 22, y - 5), (x + 40, y - 14), (x + 36, y + 12), (x + 22, y + 5),
                                       (x - 10, y + 11)]), (150 + r, 164 + r, 172 + r), dict(kind="gladki", edge=1))]
        w, h, parts = 220, 96, sum((fish(x, y, r) for x, y, r in ((60, 70, 0), (118, 74, 14), (166, 68, -10), (88, 48, 20), (140, 46, -4),
                                                                   (112, 24, 10))), [])
    elif key == "zaslona":
        w, h, parts = 210, 130, [(poly([(4, 4), (206, 4), (206, 110), (172, 126), (138, 110), (104, 126), (70, 110), (36, 126), (4, 110)]),
                                 (26, 24, 30)), (rect(4, 4, 206, 16), GOLD)]
    elif key == "robotnik":
        c = (104, 80, 58)  # jaśniejszy brąz: sylwetka ma być widoczna na ciemnym zboczu
        w, h, parts = 110, 130, [(ell(55, 22, 13, 15), c), (poly([(40, 38), (70, 38), (76, 92), (34, 92)]), c),
                                (rect(42, 90, 52, 128), c), (rect(58, 90, 68, 128), c), (rect(4, 40, 106, 46), (120, 90, 60)),
                                (poly([(2, 50), (26, 50), (22, 84), (6, 84)]), (184, 148, 92)), (poly([(84, 50), (108, 50), (104, 84), (88, 84)]), (184, 148, 92))]
    elif key == "list_pieczec":  # zwój z czerwoną pieczęcią
        w, h, parts = 96, 44, [(rect(10, 8, 86, 36), (226, 212, 180)), (rect(2, 4, 14, 40), (120, 82, 50)), (rect(82, 4, 94, 40), (120, 82, 50)),
                               (ell(48, 22, 10, 10), LAKA)]
    elif key == "chlop":
        w, h, parts = 170, 180, [(ell(70, 30, 15, 17), (70, 50, 36)), (poly([(40, 14), (100, 14), (70, 2)]), (176, 150, 96)),
                                (poly([(52, 48), (90, 48), (98, 120), (46, 120)]), (96, 110, 120)), (rect(54, 118, 68, 176), (70, 50, 36)),
                                (rect(78, 118, 92, 176), (70, 50, 36)), (poly([(84, 56), (150, 30), (154, 38), (90, 70)]), (96, 72, 50)),
                                (poly([(140, 22), (166, 40), (156, 62), (146, 40)]), (70, 70, 74))]
    elif key == "chlop_cialo":  # chłop bez narzędzia: motyka jest osobnym wycinkiem i obraca się w dłoniach
        w, h, parts = 170, 180, [(ell(70, 30, 15, 17), (70, 50, 36)), (poly([(40, 14), (100, 14), (70, 2)]), (176, 150, 96)),
                                (poly([(52, 48), (90, 48), (98, 120), (46, 120)]), (96, 110, 120)), (rect(54, 118, 68, 176), (70, 50, 36)),
                                (rect(78, 118, 92, 176), (70, 50, 36)), (poly([(80, 54), (104, 62), (100, 74), (78, 66)]), (96, 110, 120))]
    elif key == "motyka":  # trzonek z żelaznym ostrzem; uchwyt (dłonie) na lewym końcu
        w, h, parts = 200, 60, [(rect(6, 26, 170, 34), (110, 80, 52)), (poly([(160, 8), (192, 14), (190, 54), (170, 50), (172, 26)]), (70, 70, 76),
                                                                       dict(contrast=1.3))]
    elif key == "lopata":  # łopata: trzonek i szerokie ostrze; uchwyt na lewym końcu
        w, h, parts = 220, 70, [(rect(6, 31, 160, 39), (110, 80, 52)), (poly([(156, 14), (214, 18), (214, 52), (156, 56)]), (82, 80, 84),
                                                                       dict(contrast=1.3))]
    elif key == "grudka":  # grudka ziemi spod motyki
        w, h, parts = 40, 34, [(poly([(4, 18), (14, 4), (32, 6), (38, 22), (24, 32), (8, 30)]), (112, 86, 58), dict(edge=1))]
    elif key == "x":  # czerwony krzyż malowany pędzlem: wyrok (migocze nad postacią)
        w, h, parts = 300, 300, [(poly([(22, 46), (58, 18), (284, 250), (250, 284)]), (198, 26, 24), dict(kind="gladki", contrast=1.2)),
                                (poly([(244, 16), (282, 50), (52, 282), (16, 248)]), (214, 34, 28), dict(kind="gladki", contrast=1.2))]
    elif key == "flaga_biala":  # biała flaga kapitulacji (płótno; drzewce rysuje kod osobno)
        w, h, parts = 220, 150, [(poly([(4, 8), (120, 16), (214, 4), (206, 72), (214, 140), (110, 128), (4, 142)]), (238, 234, 222),
                                 dict(kind="gladki", edge=3, contrast=1.3))]
    elif key == "miarka":  # drewniana miarka Qin (chi) z podziałką
        w, h, parts = 420, 54, [(rect(4, 10, 416, 44), (176, 128, 72), dict(edge=2, contrast=1.2))]
        parts += [(rect(14 + 40 * i, 10, 18 + 40 * i, 26 if i % 5 else 34), (70, 44, 30), dict(kind="gladki", rough=0.4)) for i in range(11)]
        parts += [(rect(34 + 40 * i, 10, 36 + 40 * i, 20), (90, 60, 40), dict(kind="gladki", rough=0.4)) for i in range(10)]
    elif key == "sheng":  # brązowa miarka objętości (sheng Shang Yanga): prostokątne naczynie z rączką
        w, h, parts = 260, 150, [(rect(120, 56, 256, 74), (92, 112, 88)), (poly([(10, 30), (130, 30), (122, 144), (18, 144)]), (96, 116, 92),
                                                                         dict(contrast=1.3)),
                                (rect(4, 22, 136, 36), (140, 152, 112)),
                                (glyphs("升", 56, FONT_ZH, ZH_IDX, (70, 92), "mm"), (170, 176, 128), dict(kind="gladki", rough=0.6))]
    elif key == "x_oko":  # mały X z tuszu na zamkniętym oku (śmierć)
        w, h, parts = 100, 100, [(poly([(8, 20), (20, 8), (92, 80), (80, 92)]), (34, 26, 24), dict(kind="gladki", rough=0.6)),
                                (poly([(80, 8), (92, 20), (20, 92), (8, 80)]), (34, 26, 24), dict(kind="gladki", rough=0.6))]
    elif key == "ryba":  # jedna solona ryba (wyskakuje z wozu)
        w, h, parts = 120, 50, [(poly([(6, 25), (30, 10), (74, 14), (96, 6), (114, 4), (104, 25), (114, 46), (96, 42), (74, 36), (30, 40)]),
                                 (164, 176, 182), dict(kind="gladki", edge=2)), (ell(26, 22, 4, 4), (40, 40, 44))]
    elif key == "gwiazdka":  # gwiazdka z papieru (zamroczenie po uderzeniu)
        pts = [(30 + (26 if k % 2 == 0 else 11) * math.cos(math.pi / 2 + k * math.pi / 5),
                30 - (26 if k % 2 == 0 else 11) * math.sin(math.pi / 2 + k * math.pi / 5)) for k in range(10)]
        w, h, parts = 60, 60, [(poly(pts), (244, 210, 96), dict(kind="gladki", edge=1))]
    elif key == "list":  # zwinięty list z pieczęcią (niesie go ptak)
        w, h, parts = 96, 44, [(rect(10, 8, 86, 36), (226, 212, 180)), (rect(2, 4, 14, 40), (120, 82, 50)), (rect(82, 4, 94, 40), (120, 82, 50)),
                               (ell(48, 22, 10, 10), (40, 34, 36))]
    else:
        raise KeyError(key)
    return Sprite(stack(w, h, parts, seed=sum(map(ord, key))), f"rekwizyt-{key}", rim=2, clean=False)




# ---------- stroje: cała szata w innym materiale, a nie tylko obszycie ----------
# Wszystkie wycinanki postaci mają czarną dworską szatę ze złotym haftem; przebarwione samo obszycie dawało „dwóch
# cesarzy” (ojciec i kupiec, 15.11.2026). stroj() zmienia barwę całej szaty, obszycia i siłę haftu; głowa (kapelusz,
# włosy, broda) i zwój w ręku zostają (współrzędne wielokątów w pikselach oryginalnych PNG).
STROJ_CHRON = {
    "scholar_back": [[(350, 0), (650, 0), (650, 220), (625, 340), (575, 340), (470, 250), (350, 235)],
                     [(770, 330), (1024, 330), (1024, 640), (770, 640)]],
    "scholar_left": [[(430, 0), (670, 0), (670, 200), (612, 365), (535, 365), (470, 262), (430, 245)],
                     [(700, 300), (1024, 300), (1024, 620), (700, 620)]],
    "scholar_center": [[(420, 140), (690, 140), (690, 300), (650, 390), (625, 492), (558, 492), (520, 420), (440, 332), (420, 280)],
                       [(780, 300), (1024, 300), (1024, 620), (780, 620)]],
    "rider": [[(750, 75), (880, 75), (880, 215), (790, 225), (752, 170)]],
    "dziecko": [[(338, 78), (512, 78), (512, 298), (440, 304), (338, 272)]],
}
STROJ_CIALO = {"rider": [(700, 15), (870, 15), (905, 300), (885, 460), (945, 700), (905, 790), (770, 790), (560, 570),
                         (395, 455), (400, 345), (560, 250), (690, 150)]}  # sam jeździec, bez konia
STROJE = {
    # zakładnik w obcym mieście, zubożały książę: klęczy (inna postawa i twarz niż kupiec), spłowiała szata z niebarwionego
    # płótna, haft prawie znika
    "ojciec": ("scholar_center", dict(szata=(122, 106, 84), obszycie=(118, 84, 60), zloto=0.25)),
    # bogaty kupiec, potem kanclerz Lü Buwei: cała szata z fioletowego jedwabiu, złoty haft (bogactwo), obszycie złotawe
    "kupiec": ("scholar_back", dict(szata=(84, 38, 92), obszycie=(176, 136, 62), zloto=1.0)),
    # chłopiec zakładnika w Handanie: prosta granatowa szata, smoki prawie znikają
    "zheng_dziecko": ("dziecko", dict(szata=(58, 72, 102), obszycie=None, zloto=0.15)),
}


def _hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(mx)
    k = d > 1e-6
    rm = k & (mx == r)
    gm = k & (mx == g) & ~rm
    bm = k & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    return h * 60, d / np.maximum(mx, 1e-6), mx


def stroj(img, nazwa, szata, obszycie=None, zloto=1.0):
    """szata — nowa barwa czarnej szaty (faktura i cienie zostają); obszycie — barwa czerwonego obszycia (None: bez
    zmian); zloto — ile złotego haftu zostaje (1 — cały, 0 — haft znika w barwie szaty)."""
    a = np.asarray(img.convert("RGBA"), np.float32) / 255
    rgb, al = a[..., :3].copy(), a[..., 3]
    H_, W_ = al.shape
    def wielokat(pts):
        m = Image.new("L", (W_, H_), 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        return np.asarray(m) > 127
    tu = al > 0.02
    if nazwa in STROJ_CIALO:
        tu &= wielokat(STROJ_CIALO[nazwa])
    for pts in STROJ_CHRON.get(nazwa, []):
        tu &= ~wielokat(pts)
    h, s, v = _hsv(rgb)
    czern = tu & (v < 0.34) & (s < 0.62)
    zl = tu & (h > 30) & (h < 58) & (s > 0.32) & (v > 0.3)
    czerw = tu & ((h < 16) | (h > 338)) & (s > 0.45) & (v > 0.18)
    sz = np.asarray(szata, np.float32) / 255
    rgb = np.where(czern[..., None], sz * np.clip(0.62 + (v - 0.13) * 2.4, 0.35, 1.35)[..., None], rgb)
    if obszycie is not None:
        rgb = np.where(czerw[..., None], np.asarray(obszycie, np.float32) / 255 * np.clip(v / 0.55, 0.4, 1.4)[..., None], rgb)
    if zloto < 1:
        cel = sz * np.clip(0.95 + (v - 0.5) * 0.8, 0.7, 1.35)[..., None]
        rgb = np.where(zl[..., None], rgb * zloto + cel * (1 - zloto), rgb)
    return Image.fromarray((np.dstack([np.clip(rgb, 0, 1), al]) * 255).astype(np.uint8))


@lru_cache(None)
def woznica():
    """Woźnica przy wozach: wycinanka jeźdźca w szacie z niebarwionego płótna (jeździec-posłaniec Qin zostaje czarny)."""
    im = stroj(raw("rider"), "rider", szata=(116, 92, 66), obszycie=(110, 80, 58), zloto=0.2)
    im = im.resize((round(im.size[0] * 0.6), round(im.size[1] * 0.6)), Image.LANCZOS)
    return Sprite(im, "woznica", rim=2)

# ---------- chłopiec Zheng: wycinanka cesarza przerobiona na dziecko ----------

def _maska(size, pts, blur=0.0):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255.0


def _naloz(pm, rgb, m):
    m = m[..., None]
    pm[..., :3] = pm[..., :3] * (1 - m) + np.asarray(rgb, np.float32) * m
    pm[..., 3:4] = pm[..., 3:4] * (1 - m) + m


def _dwuliniowo(arr, ys, xs):
    h, w = arr.shape[:2]
    x0 = np.clip(np.floor(xs).astype(int), 0, w - 1)
    y0 = np.clip(np.floor(ys).astype(int), 0, h - 1)
    x1, y1 = np.clip(x0 + 1, 0, w - 1), np.clip(y0 + 1, 0, h - 1)
    wx, wy = (xs - np.floor(xs))[..., None], (ys - np.floor(ys))[..., None]
    out = (arr[y0, x0] * (1 - wx) + arr[y0, x1] * wx) * (1 - wy) + (arr[y1, x0] * (1 - wx) + arr[y1, x1] * wx) * wy
    out[(xs < 0) | (xs > w - 1) | (ys < 0) | (ys > h - 1)] = 0
    return out


def _rozmyj(m, r):
    return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


@lru_cache(None)
def dziecko(korona=False, seed=5):
    """Zheng jako chłopiec: ta sama wycinanka cesarza bez brody i wąsów, z większą głową (tułów krótszy i węższy).
    korona=False — przed koronacją: zamiast korony włosy dziecka z dwoma kokami przewiązanymi czerwoną wstążką."""
    a = np.asarray(raw("emperor"), np.float32) / 255.0
    H_, W_ = a.shape[:2]
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4]
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H_, 0:W_]
    lum = a[..., :3] @ np.array([0.3, 0.59, 0.11], np.float32)
    szum = lambda: (1 + 0.04 * rng.standard_normal((H_, W_, 1))).astype(np.float32)
    size = (W_, H_)

    # zarost: wąsy, broda i bokobrody — ciemne piksele w obrysie zarostu
    obrys = _maska(size, [(456, 243), (500, 243), (504, 268), (506, 300), (506, 340), (502, 398), (466, 400), (458, 360), (450, 322),
                          (438, 292), (440, 282), (456, 268)]) > 0.5
    broda = np.asarray(Image.fromarray(((obrys & (lum < 0.42)) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), bool) & obrys
    profil = np.interp(yy, [243, 250, 256, 262, 270, 279, 286, 292, 300, 330], [492, 495, 496, 493, 493, 488, 478, 470, 467, 466])
    kol = _maska(size, [(438, 300), (452, 308), (466, 314), (478, 314), (488, 310), (500, 322), (506, 342), (497, 398), (466, 400),
                        (457, 362), (448, 322)])
    dz_c = broda & (kol > 0.5)  # pod brodą: kołnierz
    dz_s = broda & ~dz_c & (xx <= profil + 0.5)  # podbródek i szyja chłopca
    dz_t = broda & ~dz_c & ~dz_s  # przed twarzą: tło
    pm[broda] = 0
    # skóra: dyfuzja tylko z sąsiedniej skóry (policzek, nos, szyja), potem faktura
    x0, x1, y0, y1 = 396, 524, 220, 340
    win = pm[y0:y1, x0:x1].copy()
    aw = a[y0:y1, x0:x1]
    ok = (aw[..., 3] > 0.9) & (aw[..., 0] > 0.5) & (aw[..., 0] - aw[..., 2] > 0.2) & (lum[y0:y1, x0:x1] > 0.33) & ~broda[y0:y1, x0:x1]
    hole = dz_s[y0:y1, x0:x1]
    K = (ok | hole).astype(np.float32)[..., None]
    V = win * K
    V[hole] = win[ok].mean(0)
    for _ in range(1400):
        VK = V * K
        Vn = np.roll(VK, 1, 0) + np.roll(VK, -1, 0) + np.roll(VK, 1, 1) + np.roll(VK, -1, 1)
        Kn = np.roll(K, 1, 0) + np.roll(K, -1, 0) + np.roll(K, 1, 1) + np.roll(K, -1, 1)
        V = np.where(hole[..., None], Vn / np.maximum(Kn, 1e-6), V)
    V[..., :3] *= (1 + 0.035 * rng.standard_normal(V[..., :3].shape)).astype(np.float32)
    win[hole] = V[hole]
    win[hole, 3] = 1.0
    pm[y0:y1, x0:x1] = win
    # kołnierz: biała spodnia szata z cieniem przy szyi i czerwona lamówka
    t = np.clip((yy - 302) / 30.0, 0, 1)[..., None]
    _naloz(pm, (np.array([176, 156, 128], np.float32) * (1 - t) + np.array([224, 206, 174], np.float32) * t) / 255 * szum(), dz_c * 1.0)
    lam = _maska(size, [(484, 306), (500, 322), (508, 342), (503, 398), (495, 398), (500, 342), (494, 326), (481, 310)], 0.8)
    _naloz(pm, np.array([150, 42, 32], np.float32) / 255 * szum(), lam * (broda | (kol > 0.5)))
    # usta i dolna warga
    pm[..., :3] *= (1 - 0.45 * _maska(size, [(484, 257), (495, 255), (495, 257.5), (485, 259.5)], 0.6))[..., None]
    warga = _maska(size, [(485, 259), (494, 258), (493, 263), (487, 263)], 1.0)[..., None] * 0.25
    pm[..., :3] = pm[..., :3] * (1 - warga) + np.array([0.70, 0.40, 0.34], np.float32) * warga
    # brwi dziecka: cieńsze i jaśniejsze
    brwi = _maska(size, [(440, 180), (476, 181), (500, 186), (500, 201), (476, 196), (440, 203)], 1.0) * (lum < 0.3)
    pm[..., :3] = pm[..., :3] * (1 - 0.4 * brwi[..., None]) + np.array([0.62, 0.44, 0.32], np.float32) * 0.4 * brwi[..., None] * pm[..., 3:4]
    # miękka krawędź profilu i wygładzone szwy
    pm[dz_t] = 0
    strefa = dz_s & (xx > profil - 1.5)
    pm[strefa] *= np.clip(profil + 0.8 - xx, 0, 1)[strefa][..., None]
    szew = np.asarray(Image.fromarray((broda * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), bool) & ~dz_t & (~broda | dz_c)
    roz = np.dstack([_rozmyj(pm[..., c], 0.9) for c in range(4)])
    pm[szew] = pm[szew] * 0.5 + roz[szew] * 0.5

    if not korona:  # korona → włosy dziecka; nowe włosy leżą pod spodem, twarz, ucho i stare włosy zostają na wierzchu
        linia = np.interp(np.arange(W_), [330, 340, 355, 380, 400, 420, 440, 470, 490, 505, 540],
                          [240, 196, 188, 180, 172, 166, 163, 164, 167, 172, 172])
        usun = ((yy < linia[None, :] + 2) & (xx >= 330) & (xx < 540)) | ((xx < 346) & (yy < 240))
        pm[usun] = 0
        wl = piece(W_, H_, poly([(493, 168), (488, 156), (474, 138), (452, 123), (428, 116), (404, 118), (382, 128), (366, 146), (355, 170),
                                 (349, 200), (351, 232), (360, 262), (392, 262), (420, 220), (440, 180)]), (24, 22, 26), seed=seed, contrast=0.7)
        for n, (cx_, cy_, rx, ry) in enumerate(((396, 114, 17, 15), (450, 107, 16, 14))):  # dwa koki
            wl = glue(wl, piece(W_, H_, ell(cx_, cy_, rx, ry), (28, 26, 30), seed=seed + 3 + n, contrast=0.9, shade=0.35), shadow=0.35)
        for n, pts in enumerate(([(381, 123), (409, 119), (411, 127), (383, 131)], [(436, 115), (463, 112), (465, 120), (438, 123)])):
            wl = glue(wl, piece(W_, H_, poly(pts), LAKA, seed=seed + 9 + n, contrast=0.7), shadow=0.35)  # wstążki
        d = ImageDraw.Draw(wl)
        for r0, a0, a1 in ((40, 205, 262), (52, 214, 270), (61, 200, 248), (70, 222, 266)):  # pasma zaczesane do tyłu
            d.arc((450 - r0 * 1.25, 182 - r0, 450 + r0 * 1.25, 182 + r0), a0, a1, fill=(70, 78, 98, 70), width=2)
        w_ = np.asarray(wl, np.float32) / 255.0
        w_[..., :3] *= w_[..., 3:4]
        pm = pm + w_ * (1 - pm[..., 3:4])
        gr = piece(W_, H_, poly([(426, 162), (494, 160), (496, 168), (490, 174), (484, 170), (478, 177), (470, 172), (462, 179), (454, 173),
                                 (446, 180), (438, 174), (430, 178), (424, 170)]), (24, 22, 26), seed=seed + 21, contrast=0.7)  # grzywka
        g = np.asarray(gr, np.float32) / 255.0
        g[..., :3] *= g[..., 3:4]
        pm = g + pm * (1 - g[..., 3:4])

    # proporcje dziecka: głowa bez zmian, tułów o 40% krótszy i u dołu o 20% węższy (wokół osi lalki)
    cut, sy, sx_min, cx = 300, 0.6, 0.8, 461.0
    yo, xo = np.mgrid[0:int(cut + (H_ - cut) * sy), 0:W_].astype(np.float32)
    ys = np.where(yo < cut, yo, cut + (yo - cut) / sy)
    k = np.clip((ys - cut) / 160.0, 0, 1)
    out = _dwuliniowo(pm, ys, cx + (xo - cx) / (1 - (1 - sx_min) * (k * k * (3 - 2 * k))))
    al = np.clip(out[..., 3:4], 1e-6, 1)
    return Image.fromarray((np.dstack([np.clip(out[..., :3] / al, 0, 1), out[..., 3]]) * 255).astype(np.uint8))

@lru_cache(None)
def ribbon(key):
    """Wstęga z papieru: kanał (niebieska) albo rzeka rtęci (srebrna)."""
    if key in ("brzeg", "trakt"):  # brzeg kanału (nasyp z ziemi) albo droga z koleinami: szerszy pas pod wstęgą
        w, h = 1400, 70
        pts = [(x, 6 + 5 * math.sin(x / 70.0)) for x in range(0, w + 20, 20)] + [(x, 62 + 5 * math.sin(x / 53.0 + 2)) for x in range(w, -20, -20)]
        im = piece(w, h, poly(pts), (154, 128, 86) if key == "brzeg" else (170, 140, 98), "gnieciony", edge=3, seed=4, contrast=1.0)
        if key == "trakt":
            d = ImageDraw.Draw(im)
            for y0 in (26, 44):  # dwie koleiny jednej szerokości (osie wozów)
                d.line([(x, y0 + 3 * math.sin(x / 90.0)) for x in range(10, w - 10, 20)], fill=(104, 80, 52, 230), width=4)
        return Sprite(im, f"wstega-{key}", rim=1, clean=False)
    color = {"kanal": (58, 120, 172), "rtec": (200, 206, 214)}[key]
    w, h = 1400, 44
    pts = [(x, 8 + 4 * math.sin(x / 60.0)) for x in range(0, w + 20, 20)] + [(x, 36 + 4 * math.sin(x / 47.0 + 1)) for x in range(w, -20, -20)]
    im = piece(w, h, poly(pts), color, "gnieciony", edge=3, seed=3, contrast=0.9)
    if key == "kanal":  # fale na wodzie: jasne kreski, żeby wstęga czytała się jako płynąca woda
        d = ImageDraw.Draw(im)
        r = random.Random(11)
        for _ in range(70):
            x, y = r.uniform(20, w - 60), r.uniform(16, 28)
            d.arc([x, y - 4, x + 26, y + 6], 200, 340, fill=(206, 230, 244, 210), width=2)
    return Sprite(im, f"wstega-{key}", rim=1, clean=False)


@lru_cache(None)
def mound():
    """Kopiec grobowca: szeroki, łagodny pagórek z dwóch arkuszy."""
    w, h = 900, 420
    bell = lambda amp, base: [(x, base - amp * math.exp(-((x - w / 2) / 230.0) ** 2)) for x in range(0, w + 20, 20)]
    im = None
    for i, (amp, base, color) in enumerate(((330, 380, (166, 146, 96)), (236, 402, (124, 120, 78)))):
        pts = bell(amp, base)
        m = rough_mask(lambda d, s, pts=pts: d.polygon([(x * s, y * s) for x, y in pts] + [(w * s, h * s), (0, h * s)], fill=255), w, h, 2.2, 60 + i)
        sh = paper(m, color, "gnieciony", 61 + i, edge=4, shade=0.2, contrast=0.9)
        im = sh if im is None else over(im, sh)
    return Sprite(im, "kopiec", rim=2, clean=False, pad=0)


@lru_cache(None)
def palace():
    """Olbrzymi pałac: trzy piętra tej samej wieży, coraz węższe ku górze."""
    tier = raw("city_gate").crop((588, 20, 1208, 446))
    w, h = 620, 960
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for scale, y in ((1.0, 534), (0.82, 262), (0.64, 30)):
        t = tier.resize((round(620 * scale), round(426 * scale)), Image.LANCZOS)
        im.alpha_composite(t, ((w - t.size[0]) // 2, y))
    return Sprite(im, "palac", rim=2)


@lru_cache(None)
def giant():
    """Posąg z brązu: ta sama wycinanka co gliniany żołnierz, w barwie patyny."""
    arr = np.asarray(soldier(0).mips[0], np.float32) / 255.0
    lum = arr[..., :3].mean(axis=2, keepdims=True) / 0.55
    arr[..., :3] = np.clip(lum * np.array([0.40, 0.52, 0.42], np.float32) * arr[..., 3:], 0, 1)
    return Sprite(Image.fromarray((arr * 255).astype(np.uint8), "RGBA"), "posag", rim=0, clean=False)


@lru_cache(None)
def tag_zh(txt, size=40):
    w, h = size * len(txt) + 40, size + 36
    parts = [(rect(4, 4, w - 4, h - 4), (240, 226, 194), dict(kind="gladki", edge=4, contrast=1.3)),
             (glyphs(txt, size, FONT_ZH, ZH_IDX, (w / 2, h / 2), "mm"), (48, 30, 24), dict(kind="gladki", rough=0.5))]
    return Sprite(stack(w, h, parts, seed=len(txt) + 7), f"zawieszka-zh-{txt}", rim=2, clean=False)


# ---------- życie sceny i kulisy (przedplan) ----------

@lru_cache(None)
def bird(f):
    """Ptak z czarnego papieru, dwie fazy skrzydeł (f = 0 skrzydła w górze, 1 w dole)."""
    w, h = 120, 70
    wing = [(60, 40), (30, 6 if f == 0 else 58), (4, 14 if f == 0 else 50), (38, 36)] if True else []
    parts = [(poly([(60, 40)] + [(x, y) for x, y in wing[1:]]), (34, 30, 32)),
             (poly([(60, 40)] + [(120 - x, y) for x, y in wing[1:]]), (34, 30, 32)),
             (ell(60, 40, 14, 8), (40, 34, 36))]
    return Sprite(stack(w, h, parts, seed=500 + f), f"ptak-{f}", rim=1, clean=False)


@lru_cache(None)
def reeds(seed=0):
    """Kępa trzcin i traw z ciemnozielonego papieru (kulisa na przedplanie)."""
    r = random.Random(seed)
    w, h = 520, 420
    parts = []
    for i in range(14):
        x0 = 60 + r.uniform(0, 400)
        lean = r.uniform(-120, 120)
        top = r.uniform(10, 220)
        wd = r.uniform(10, 22)
        col = r.choice(((44, 70, 50), (60, 88, 58), (36, 58, 44), (82, 104, 62)))
        pts = [(x0 - wd, h), (x0 + lean * 0.5 - wd * 0.4, (h + top) / 2), (x0 + lean, top),
               (x0 + lean * 0.5 + wd * 0.5, (h + top) / 2 + 10), (x0 + wd, h)]
        parts.append((poly(pts), col, dict(edge=0, contrast=1.0)))
    return Sprite(stack(w, h, parts, seed=600 + seed), f"trzciny-{seed}", rim=2, clean=False)


@lru_cache(None)
def bough(side=1):
    """Gałąź sosny z wycinka drzewa (kulisa zwisająca z góry kadru). side = 1 — z prawej, -1 — z lewej."""
    im = raw("tree_right").crop((0, 0, 900, 560))
    if side < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return Sprite(im, f"galaz-{side}", rim=2)


@lru_cache(None)
def lantern():
    """Czerwona papierowa latarnia ze złotymi denkami i frędzlem."""
    w, h = 160, 300
    parts = [(rect(76, 0, 84, 60), (60, 44, 34)), (rect(40, 50, 120, 70), GOLD),
             (ell(80, 140, 66, 80), (178, 40, 30), dict(edge=0, contrast=0.8)),
             (rect(40, 210, 120, 230), GOLD), (poly([(66, 230), (94, 230), (100, 296), (60, 296)]), (196, 60, 40))]
    im = stack(w, h, parts, seed=77)
    d = ImageDraw.Draw(im)
    for x in (44, 62, 80, 98, 116):  # żebra lampionu
        d.arc([x - 36 - (x - 80) * 0.2, 62, x + 36 + (x - 80) * 0.2, 218], 250, 290, fill=(120, 26, 20, 200), width=3)
    return Sprite(im, "latarnia", rim=2, clean=False)


@lru_cache(None)
def walker(key, h=60):
    """Mała postać wędrowca (zmniejszona wycinanka uczonego) — ludzie na drodze i moście."""
    name = {"a": "scholar_back", "b": "scholar_center", "c": "scholar_left"}[key]
    im = raw(name)
    k = h * 4 / im.size[1]
    return Sprite(im.resize((max(8, round(im.size[0] * k)), round(im.size[1] * k)), Image.LANCZOS), f"wedrowiec-{key}", rim=1)


# ---------- waga w częściach: podstawa stoi, belka się kołysze, szale wiszą osobno ----------
# Współrzędne w pikselach scale.png (1536 × 1024). Każda część zostaje w układzie całego arkusza (crop=False),
# więc kotwica w pikselach oryginału ustawia ją dokładnie tam, gdzie była w całej wadze.
WAGA_OS = (758, 240)  # oś belki (środek bloku na kolumnie)
WAGA_HAK = {"lewa": (308, 174), "prawa": (1242, 309)}  # gdzie szala wisi na belce
WAGA_STOPA = (772, 1004)  # środek dolnej krawędzi podstawy
_WAGA_MASKI = {
    "podstawa": [(693, 12), (822, 12), (825, 357), (810, 375), (819, 760), (915, 784), (1060, 1015), (485, 1015), (618, 784), (708, 760),
                 (717, 375), (693, 357)],
    "belka": [(150, 96), (705, 144), (705, 357), (822, 357), (822, 174), (1443, 252), (1443, 333), (822, 300), (705, 252), (150, 180)],
    "lewa": [(54, 162), (570, 162), (570, 720), (54, 720)],
    "prawa": [(975, 294), (1488, 294), (1488, 858), (975, 858)],
}


@lru_cache(None)
def waga_czesc(nazwa):
    im = raw("scale")
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(_WAGA_MASKI[nazwa], fill=255)
    if nazwa == "belka":  # belka nie zabiera kolumny ani szal: tylko to, czego nie ma w innych częściach
        for inna in ("podstawa",):
            ImageDraw.Draw(m).polygon(_WAGA_MASKI[inna], fill=0)
        ImageDraw.Draw(m).polygon([(693, 144), (822, 144), (822, 357), (693, 357)], fill=255)  # blok osi kołysze się z belką
    if nazwa == "podstawa":
        ImageDraw.Draw(m).polygon([(693, 144), (822, 144), (822, 357), (693, 357)], fill=0)
    if nazwa in ("lewa", "prawa"):  # szala bez kawałka belki nad hakiem
        ImageDraw.Draw(m).polygon(_WAGA_MASKI["belka"], fill=0)
    out = im.copy()
    out.putalpha(ImageChops.multiply(im.getchannel("A"), m))
    return Sprite(out.resize((768, 341), Image.LANCZOS), f"waga-{nazwa}", rim=2, clean=False, pad=0, crop=False)


# ---------- zwój mapy rozwinięty płasko na blacie (ukos jak blat stołu w kadrze) ----------

ZWOJ_A, ZWOJ_B = (-36.0, 36.0), (64.0, 34.0)  # zwój na stole z podarunkami: wzdłuż wałka i kierunek rozwijania (marker reżysera)
ZWOJ_SKALA = 1 / 3.2  # zwój na blacie rysowany w 3,2 px na piksel kadru wzorcowego (zbliżenie detalu)


@lru_cache(None)
def zwoj_plaski(n=16):
    """Rozwinięta część zwoju (n/16) leżąca na blacie: równoległobok o bokach jak krawędzie blatu w ujęciu ze sztyletem
    (długi bok wzdłuż wałka — w głąb stołu, krótki — w stronę rozwijania). spr.origin — kotwica rogu przy wałku."""
    S_ = 1 / ZWOJ_SKALA
    (ax, ay), (bx, by) = (ZWOJ_A[0] * S_, ZWOJ_A[1] * S_), (ZWOJ_B[0] * S_, ZWOJ_B[1] * S_)
    f = max(1, n) / 16
    bx, by = bx * f, by * f
    src = raw("ledger").crop((80, 260, 1600, 700))
    src = src.crop((0, 0, max(8, int(src.size[0] * f)), src.size[1])).resize((max(8, int(380 * f)), 110), Image.LANCZOS)
    pad = 6
    xs, ys = [0, ax, bx, ax + bx], [0, ay, by, ay + by]
    x0, y0 = min(xs) - pad, min(ys) - pad
    W_, H_ = int(max(xs) - x0 + pad), int(max(ys) - y0 + pad)
    # obraz zwoju: oś u (szerokość obrazka, czytana w stronę rozwijania) → wektor b, oś v (wysokość) → wektor a
    det = bx * ay - by * ax
    su, sv = src.size
    # piksel wyniku (X, Y) = róg + u/su·b + v/sv·a  →  u, v z odwrotności macierzy [b a]
    cu = (ay / det * su, -ax / det * su)
    cv = (-by / det * sv, bx / det * sv)
    coef = (cu[0], cu[1], cu[0] * x0 + cu[1] * y0, cv[0], cv[1], cv[0] * x0 + cv[1] * y0)
    out = src.transform((W_, H_), Image.AFFINE, coef, resample=Image.BICUBIC)
    spr = Sprite(out, f"zwoj-plaski-{n}", rim=1, clean=False, pad=0, crop=False)
    spr.origin = (-x0 / W_, -y0 / H_)
    return spr


# ---------- mapa 36 prowincji (komanderii) Qin po zjednoczeniu ----------
# Siedziby komanderii (długość, szerokość geograficzna) — w przybliżeniu, według listy 36 komanderii z komentarza do
# Shiji; granice to podział Woronoja wokół siedzib w obrysie państwa Qin (prawdziwe granice znamy tylko z grubsza).
KOMANDERIE = [(108.7, 34.4), (104.4, 35.4), (107.6, 36.0), (109.6, 37.6), (109.8, 40.6), (111.3, 40.6), (112.4, 39.9), (114.6, 39.9),
              (112.5, 37.8), (113.0, 36.2), (111.1, 35.1), (112.4, 34.7), (113.5, 34.2), (112.5, 33.0), (112.2, 30.4), (110.3, 29.0),
              (107.0, 33.1), (106.6, 29.6), (104.1, 30.7), (113.0, 28.2), (116.8, 32.6), (119.7, 30.6), (120.6, 31.3), (115.6, 34.4),
              (116.8, 33.9), (117.0, 35.6), (118.3, 34.6), (119.6, 35.6), (118.3, 36.8), (115.5, 40.4), (116.8, 40.4), (118.5, 41.0),
              (120.5, 41.3), (123.2, 41.3), (115.0, 37.2), (114.5, 36.6)]
QIN_OBRYS = [(103.5, 36.5), (104.6, 38.2), (106.6, 39.2), (108.0, 41.3), (111.0, 41.6), (114.0, 41.3), (117.0, 41.9), (120.0, 42.3),
             (123.0, 42.6), (125.2, 41.6), (124.3, 40.0), (122.2, 39.6), (121.3, 39.0), (121.9, 40.6), (120.2, 40.2), (118.6, 39.2),
             (117.8, 38.5), (118.8, 37.4), (120.3, 37.7), (122.4, 37.2), (121.0, 36.1), (119.4, 35.1), (119.2, 34.4), (120.3, 33.4),
             (121.0, 32.1), (121.8, 31.2), (121.0, 30.3), (122.0, 29.8), (121.4, 28.5), (120.3, 27.6), (118.0, 27.5), (115.5, 26.4),
             (113.5, 25.4), (111.5, 25.6), (110.0, 26.2), (108.5, 27.4), (106.5, 27.8), (105.0, 28.0), (103.5, 28.6), (102.8, 30.0),
             (103.0, 31.6), (103.6, 33.0), (103.2, 34.5)]
MAPA36_WH = (640, 560)


def _m36(lon, lat):
    w, h = MAPA36_WH
    return 30 + (lon - 102.5) * 0.83 * 30.0, 22 + (43.2 - lat) * 30.0


@lru_cache(None)
def mapa36():
    """Arkusz mapy (morze i obrys kraju) oraz 36 kawałków prowincji: [(Sprite, x0, y0)] — x0, y0 to lewy górny róg
    kawałka w pikselach arkusza. Kawałki są przycięte do siebie, więc kładzie się je kotwicą (0, 0) w tym punkcie."""
    w, h = MAPA36_WH
    board = piece(w, h, rect(2, 2, w - 2, h - 2), (226, 214, 184), "gladki", edge=5, seed=93, contrast=1.4)
    obrys = [_m36(*p) for p in QIN_OBRYS]
    km = Image.new("L", (w, h), 0)
    ImageDraw.Draw(km).polygon(obrys, fill=255)
    yy_, xx_ = np.mgrid[0:h, 0:w]
    morze_ = (np.asarray(km) < 128) & (xx_ > 420) & (yy_ > 110) & ~((yy_ > 480) & (xx_ < 470)) & (xx_ < w - 4) & (yy_ < h - 4)
    sea = paper(Image.fromarray((morze_ * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), (150, 178, 186), "gnieciony", 94,
                contrast=0.9)
    board = glue(board, sea, shadow=0.2)
    kraj = rough_mask(poly(obrys), w, h, 1.2, 95)
    board = glue(board, paper(kraj, (196, 182, 150), "gnieciony", 96, edge=3, contrast=0.9), shadow=0.45)
    # podział Woronoja wewnątrz obrysu
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    seats = np.array([_m36(*p) for p in KOMANDERIE], np.float32)
    d = (xx[None] - seats[:, 0, None, None]) ** 2 + (yy[None] - seats[:, 1, None, None]) ** 2
    lab = d.argmin(0)
    inside = np.asarray(Image.new("L", (w, h), 0)) > 0
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(obrys, fill=255)
    inside = np.asarray(m) > 127
    paleta = [(58, 54, 60), (84, 74, 70), (46, 46, 54), (96, 84, 72), (70, 62, 66), (52, 58, 62)]
    czesci = []
    for n in range(len(KOMANDERIE)):
        mask = (lab == n) & inside
        ys, xs = np.nonzero(mask)
        if len(xs) == 0:
            continue
        x0, x1, y0, y1 = xs.min() - 3, xs.max() + 4, ys.min() - 3, ys.max() + 4
        mm = Image.fromarray((mask[y0:y1, x0:x1] * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))
        mm = mm.filter(ImageFilter.GaussianBlur(0.7))
        kaw = paper(mm, paleta[n % len(paleta)], "gnieciony", 100 + n, edge=2, edge_color=(226, 206, 160), contrast=0.9)
        sx, sy = seats[n]
        dd = ImageDraw.Draw(kaw)
        cx, cy = sx - x0, sy - y0
        dd.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(206, 164, 84, 255))  # siedziba komanderii: złota kropka
        czesci.append((Sprite(kaw, f"prowincja-{n}", rim=1, clean=False, pad=0, crop=False), int(x0), int(y0)))
    return Sprite(board, "mapa36", rim=2, clean=False, pad=0, crop=False), czesci


@lru_cache(None)
def cyklop(v=0):
    """Jednooki olbrzym z wyspy nieśmiertelnych (reżyser 15.11: „narysuj cyklopów”): wycinanka z kawałków papieru,
    duża głowa z jednym okiem, przepaska, maczuga. v — odmiana (barwa przepaski, maczuga w lewej albo prawej ręce)."""
    r = random.Random(700 + v)
    skin = ((176, 132, 96), (160, 120, 92), (186, 142, 104))[v % 3]
    cloth = ((92, 70, 50), (70, 84, 60), (104, 62, 48))[v % 3]
    dark = tuple(int(c * 0.7) for c in skin)
    w, h = 300, 520
    side = 1 if v % 2 == 0 else -1
    X = lambda x: 150 + (x - 150) * side
    P_ = lambda pts: poly([(X(x), y) for x, y in pts])
    parts = [
        (P_([(110, 360), (142, 360), (140, 500), (104, 500)]), dark), (P_([(158, 360), (190, 360), (196, 500), (160, 500)]), dark),
        (P_([(96, 492), (144, 492), (146, 516), (90, 516)]), (70, 52, 40)), (P_([(156, 492), (204, 492), (210, 516), (154, 516)]), (70, 52, 40)),
        (P_([(84, 190), (216, 190), (232, 300), (68, 300)]), skin, dict(edge=2)),
        (P_([(70, 280), (230, 280), (242, 380), (58, 380)]), cloth, dict(edge=2)),
        (P_([(70, 196), (40, 210), (20, 330), (44, 336), (66, 250)]), skin), (P_([(230, 196), (262, 210), (282, 320), (258, 326), (234, 250)]), skin),
        (P_([(262, 300), (296, 120), (280, 112), (244, 300)]), (96, 70, 46)), (ell(X(288), 116, 22, 26), (110, 80, 52), dict(edge=1)),
        (ell(150, 110, 78, 84), skin, dict(edge=2)),
        (ell(150, 98, 34, 28), (240, 236, 222), dict(kind="gladki", edge=1)),
        (ell(150 + 4 * side, 100, 15, 15), (44, 70, 40), dict(kind="gladki")), (ell(150 + 4 * side, 100, 7, 7), (16, 14, 14), dict(kind="gladki")),
        (P_([(110, 62), (190, 62), (186, 70), (114, 70)]), (60, 40, 30)),  # jedna gruba brew
        (P_([(118, 150), (182, 150), (176, 160), (124, 160)]), (90, 40, 34)),
        (P_([(78, 60), (100, 20), (130, 40), (150, 14), (172, 40), (200, 20), (222, 60), (190, 46), (150, 34), (110, 46)]), (52, 40, 34)),
    ]
    return Sprite(stack(w, h, parts, seed=720 + v), f"cyklop-{v}", rim=2, clean=False)


# ---------- kurtyna teatru (przejście między aktami) ----------

@lru_cache(None)
def kurtyna(strona=-1):
    """Połowa czerwonej kurtyny z fałdami i złotą frędzlą u dołu. strona -1 — lewa (fałdy zbiegają się w prawo), 1 — prawa.
    Arkusz 760 × 860: zakrywa pół otworu sceny z zapasem na zakładkę i ruch."""
    w, h = 760, 860
    m = rough_mask(rect(0, 0, w, h - 24), w, h, 1.2, 81)
    im = paper(m, (150, 26, 30), "gnieciony", 82, contrast=0.8)
    a = np.asarray(im, np.float32)
    xx = np.arange(w, dtype=np.float32)
    faldy = 0.72 + 0.28 * (0.5 + 0.5 * np.cos(xx / 46.0 * math.pi)) ** 0.8  # pionowe fałdy: jasny grzbiet, ciemna dolina
    brzeg = np.clip((xx if strona > 0 else (w - 1 - xx)) / 60.0, 0.55, 1.0)  # ciemniej przy brzegu, który się schodzi
    a[..., :3] *= (faldy * brzeg)[None, :, None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    fr = piece(w, h, rect(0, h - 40, w, h - 8), GOLD, "gnieciony", seed=83, rough=0.8, contrast=0.9)
    im = glue(im, fr, shadow=0.5)
    d = ImageDraw.Draw(im)
    for x in range(6, w, 14):  # frędzle
        d.line([(x, h - 10), (x + 2, h - 1)], fill=(176, 132, 60, 255), width=4)
    return Sprite(im, f"kurtyna-{strona}", rim=2, clean=False, pad=0)
