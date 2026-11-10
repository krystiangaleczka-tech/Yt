"""Miniatury YouTube filmu „Oddział C” (1280 × 720) rysowane tym samym kodem co film — trzy wersje do porównania.

1 izolatka — okienko izolatki 3 z panem Henrykiem (render.scene3 po uderzeniu w szybę), sanitariusz z przodu: „30 NOCY”
2 korytarz — otwarte sale i pacjenci idący korytarzem (render.scene5), sanitariusz z przodu: „ZA TOBĄ”
3 dyżurka  — sylwetki za szybą dyżurki z głowami odwróconymi do widza (render2.window_view), sanitariusz zasłania
             usta dłonią: „ANI DŹWIĘKU”

Napisy są poza rysunkiem, nakładane na końcu.

    python3 miniatura.py          # wszystkie trzy → miniatura-1-izolatka.png, miniatura-2-korytarz.png, …
    python3 miniatura.py 2        # tylko wersja 2
"""
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import render as R
import render2 as R2

HERE = Path(__file__).parent
W, H = R.W, R.H
FONT = HERE.parents[1] / "pilot/fonts/Montserrat.ttf"
DOOR = (112, 126, 112)
YELLOW, WHITE, RED = (255, 222, 74), (250, 250, 244), (196, 30, 30)
SKIN = (232, 200, 174)  # skóra sanitariusza w render.nurse_face


def limb(p, a, b, w, col, outline=3):
    """Odcinek ręki albo palec: gruba kreska w kolorze z konturem (jak kit_a.limb)."""
    p.line([a, b], w=w + 2 * outline, amp=0.8)
    p.line([a, b], w=w, color=col, amp=0.8)


def canvas():
    R.SS = 3
    return Image.new("RGBA", (W * R.SS, H * R.SS), (0, 0, 0, 255))


def small(img):
    return img.convert("RGB").resize((W, H), Image.LANCZOS)


def light(img, grade, spots, amb=0.3, red=0.0):
    """Barwa ujęcia z filmu, kręgi światła (x, y, promień, moc), winieta, świecące białka oczu, ziarno."""
    arr = np.asarray(img).astype(np.float32) * np.array(grade, dtype=np.float32)
    yy, xx = np.ogrid[:H, :W]
    m = np.zeros((H, W), dtype=np.float32)
    for cx, cy, r, power in spots:
        m = np.maximum(m, power * np.clip(1 - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r, 0, 1) ** 0.7)
    arr *= (amb + (1 - amb) * m)[..., None]
    arr[..., 0] += red  # czerwony odcień z ujęcia „Wszystkie.”
    vig = 1 - 0.4 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
    arr *= np.clip(vig, 0.4, 1)[..., None]
    arr = (arr - 128) * 1.12 + 132  # miniatura jest oglądana w małym rozmiarze: trochę więcej kontrastu
    # białka oczu świecą w mroku (motyw „tylko oczy” z końca zimnego otwarcia)
    lum = np.clip(arr, 0, 255).mean(axis=2)
    eyes = Image.fromarray(((lum > 205) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
    arr += (np.asarray(eyes).astype(np.float32) / 255 * 46)[..., None]
    arr += np.random.default_rng(7).normal(0, 2.5, (H, W, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def font(size):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_name("Black")
    return f


def titles(img, big1, big2, side="l", tag="ODDZIAŁ C", width=500):
    """Napisy: czerwona tabliczka z tytułem i dwa duże wiersze z grubym konturem, lekko przekrzywione.
    side — róg kadru: „l” lewy górny, „r” prawy górny; width — najszersze miejsce na napis."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    left = side == "l"
    x, y = (40 if left else W - 40), 34
    if tag:
        f = font(46)
        w = d.textlength(tag, font=f) + 36
        x0 = x if left else x - w
        d.rectangle([x0, y, x0 + w, y + 66], fill=RED, outline=R.INK, width=5)
        d.text((x0 + 18, y + 33), tag, font=f, fill=WHITE, anchor="lm")
        y += 66 + 14
    for txt, size, col in ((big1, 190, YELLOW), (big2, 138, WHITE)):
        if not txt:
            continue
        f = font(size)
        while d.textlength(txt, font=f) > width:  # dłuższy napis zmniejsza się, zamiast wchodzić na rysunek
            size -= 4
            f = font(size)
        top = f.getbbox(txt, anchor="ls")[1]
        d.text((x - 4 if left else x + 4, y - top), txt, font=f, fill=col, anchor="ls" if left else "rs",
               stroke_width=max(7, size // 14), stroke_fill=R.INK)
        y += 26 - top
    layer = layer.rotate(3.0 if left else -3.0, resample=Image.BICUBIC, center=(x, 34))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 255), (8, 10), layer.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    out = img.convert("RGBA")
    out.alpha_composite(shadow)
    out.alpha_composite(layer)
    return out.convert("RGB")


def izolatka():
    """Drzwi izolatki z okienkiem, przed nimi (bliżej kamery) twarz sanitariusza."""
    img = canvas()
    t = R.SLAM_T - R.SCENES[2][0] + 2.2  # 2,2 s po uderzeniu: głowa przekrzywiona, krew spłynęła, szyba bez pary
    # okienko po prawej, lewa strona na napis i sanitariusza; tabliczka „IZOLATKA 3” poza kadrem
    p = R.Pen(img, t, **R.framed(dict(zoom=2.1, cx=520, cy=224), (0, 0)))
    R.scene3(p, t, 5.6)
    # siatka jest tylko w okienku (WYTYCZNE 1.1): drzwi po obu stronach ramy zasłaniają jej końce
    p.rect(331, 100, 468, 380, DOOR, w=0, amp=0)
    p.rect(812, 100, 950, 380, DOOR, w=0, amp=0)
    p.line([(340, 0), (340, 720)], w=3)
    p.rect(470, 120, 810, 360, None, w=8)
    R.nurse_face(R.Pen(img, 0.3), 262, 545, 1.0, 1.0, 0.3, gaze=(1.0, -0.15))
    img = light(small(img), R.GRADE[2], [(900, 330, 600, 1.0), (262, 535, 330, 0.9)])
    return titles(img, "30", "NOCY")


def korytarz():
    """„Wszystkie.” — sale otwarte, pacjenci idą korytarzem, każdy we własnym tempie; sanitariusz z przodu zerka za siebie."""
    img = canvas()
    t = 2.75
    # kadr przesunięty w prawo i w dół: głowy pacjentów zostają pod napisem, nie za nim
    p = R.Pen(img, t, **R.framed(dict(zoom=1.12, cx=575, cy=335), (0, 0)))
    R.corridor(p, t, [0, 0, 0, 0], doors_open=0.9)
    # pacjenci z render.scene5 (te same miejsca i opóźnienia), ale rysowani od najdalszego do najbliższego (WYTYCZNE 1.5)
    zt, people = 0.3 * min(t, 1.4) + max(0.0, t - 1.4), []
    for i, dx in enumerate((-260, 220, -60, 380, -420, 60)):
        k = 0.05 * R.ease(t / 1.4) + 0.95 * R.ease((t - 1.4 - R.ZOMBIE_START[i]) / 2.4)
        people.append((420 + 300 * k, 640 + dx * (0.3 + 0.9 * k), 0.35 + k + (0.2 if i == 5 else 0), i))
    for y, x, s, i in sorted(people):
        R.zombie(p, x, y, s, zt + i * 0.4, i * 1.7, tilt=random.Random(i).uniform(-0.25, 0.25))
    R.nurse_face(R.Pen(img, 0.3), 1030, 440, 1.2, 1.0, 0.3, gaze=(-1.0, 0.1))
    img = light(small(img), R.GRADE[4], [(640, 480, 640, 1.0), (1030, 430, 380, 0.95)], amb=0.26, red=24)
    return titles(img, "ZA", "TOBĄ")


def dyzurka():
    """Ciemna dyżurka: za szybą sylwetki, wszystkie głowy odwrócone do widza; sanitariusz zasłania usta dłonią."""
    img = canvas()
    turn = 2.0  # sekundy po dzwonku: odwrócili się już wszyscy, także spóźniony
    p = R.Pen(img, 0.0, **R.framed(dict(zoom=1.62, cx=780, cy=285), (0, 0)))
    R2.window_view(p, 1.3 + turn, 5.0, turn, R2.WALKERS5)
    x, y, s = 1040, 532, 0.92
    p = R.Pen(img, 0.3)
    R.nurse_face(p, x, y, s, 1.0, 0.3, gaze=(-0.9, -0.5))
    # dłoń na ustach, jak w ujęciu „Pod szybą” — bliżej kamery niż twarz, więc rysowana po niej (WYTYCZNE 1.5);
    # przedramię wychodzi spod dolnej krawędzi kadru, palce leżą na policzku
    limb(p, (x + 120 * s, y + 330 * s), (x + 34 * s, y + 112 * s), 54 * s, SKIN)
    p.ell(x + 14 * s, y + 92 * s, 58 * s, 40 * s, SKIN)
    for k in range(4):
        yy = y + (58 + k * 20) * s
        limb(p, (x - 4 * s, yy + 4 * s), (x - (84 - 7 * abs(k - 1.5)) * s, yy - 4 * s), 19 * s, SKIN, outline=2.5)
    limb(p, (x + 50 * s, y + 84 * s), (x + 66 * s, y + 44 * s), 20 * s, SKIN, outline=2.5)
    img = light(small(img), R2.GRADE[4], [(430, 330, 620, 1.0), (x, y + 20, 320, 0.85)], amb=0.24)
    return titles(img, "ANI", "DŹWIĘKU", side="r", width=470)


VERSIONS = {"1": ("izolatka", izolatka), "2": ("korytarz", korytarz), "3": ("dyzurka", dyzurka)}


def main(*which):
    for n in which or VERSIONS:
        name, fn = VERSIONS[n]
        out = HERE / f"miniatura-{n}-{name}.png"
        fn().save(out)
        print(out)


if __name__ == "__main__":
    main(*sys.argv[1:])
