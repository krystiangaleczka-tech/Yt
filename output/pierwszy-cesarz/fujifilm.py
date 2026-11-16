"""Wygląd zdjęcia z aparatu Fujifilm nałożony na gotowy obraz (reżyser 16.11.2026: „nałóż na miniaturkę, jakby była
zrobiona aparatem fujifilm”).

Symulacja w duchu Fujifilm Classic Negative: podniesiona czerń (lekko wyblakła), twardszy kontrast w środku skali,
miękko zaokrąglone światła, chłodne turkusowe cienie i ciepłe, żółtawe światła, przygaszona zieleń i błękit, głębsza
czerwień; ziarno filmowe (najmocniejsze w półcieniach), poświata wokół najjaśniejszych miejsc (halacja: ogień meteorytu)
i delikatna winieta. Czysty obraz zostaje nietknięty — wynik idzie do osobnych plików z dopiskiem _fuji.

  MOC=1.8 python3 fujifilm.py <obraz.png> [szerokość_mniejszej_wersji]   (MOC — siła efektu, 1 = delikatny)
    → <obraz>_fuji.png i _fuji.jpg w pełnym rozmiarze; z drugim argumentem (np. 1280) także zmniejszona wersja
      <obraz bez _4k>_fuji.jpg (ziarno dokładane osobno w każdym rozmiarze, żeby nie zniknęło przy zmniejszaniu)
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def _krzywa(x, pts):
    xs, ys = zip(*pts)
    return np.interp(x, xs, ys).astype(np.float32)


MOC = float(os.environ.get("MOC", "0.5"))  # reżyser 16.11: „mocniejszy” (1,8), „dużo mniejszy” (0,8), „może za dużo tego fuji” → 0,5
JASNOSC = float(os.environ.get("JASNOSC", "0.07"))  # reżyser 16.11: „minimalnie rozjaśnij” — półtony w górę o ok. 5%, biel bez zmian


def wyglad(img, m=1.0):
    """Barwa i tonacja Classic Negative (bez ziarna). img: RGB w dowolnym rozmiarze; m — siła (każda zmiana razy m)."""
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    H, W = a.shape[:2]
    s = W / 1280  # skala względem 1280 × 720: promienie poświaty i winiety rosną z rozmiarem

    # halacja: jasne miejsca świecą czerwono-pomarańczową poświatą (jak przez emulsję filmu)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    jasne = np.clip((lum - 0.72) / 0.28, 0, 1) ** 1.5
    pm = Image.fromarray((jasne * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9 * s))
    hal = np.asarray(pm, np.float32)[..., None] / 255.0
    a = a + hal * np.array([0.22, 0.08, 0.02], np.float32) * m

    # krzywe kanałów: czerń podniesiona, środek twardszy, światła zaokrąglone; niebieski w cieniach wyżej (turkus),
    # w światłach niżej (ciepło)
    a = np.clip(a, 0, 1)
    r = _krzywa(a[..., 0], [(0, 0.045), (0.18, 0.15), (0.5, 0.52), (0.82, 0.86), (1, 0.955)])
    g = _krzywa(a[..., 1], [(0, 0.055), (0.18, 0.165), (0.5, 0.51), (0.82, 0.85), (1, 0.95)])
    b = _krzywa(a[..., 2], [(0, 0.075), (0.18, 0.185), (0.5, 0.49), (0.82, 0.80), (1, 0.90)])
    a = a + (np.dstack([r, g, b]) - a) * m

    # kolor: przygaszona zieleń i błękit, czerwień głębsza; całość nieco mniej nasycona (jak negatyw)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    mx, mn = a.max(axis=2), a.min(axis=2)
    nas = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    zielen = np.clip((G - np.maximum(R, B)) * 4, 0, 1)  # gdzie zielony przeważa
    blekit = np.clip((B - np.maximum(R, G)) * 4, 0, 1)
    czerwien = np.clip((R - np.maximum(G, B)) * 3, 0, 1)
    k_nas = 1 - m * (0.14 + 0.16 * zielen + 0.10 * blekit - 0.10 * czerwien)
    a = lum[..., None] + (a - lum[..., None]) * k_nas[..., None]
    # zieleń lekko w stronę oliwki, błękit w stronę turkusu
    a[..., 0] += (0.025 * zielen - 0.035 * blekit) * m  # niebo bez fioletu: mniej czerwieni w błękicie
    a[..., 1] += 0.040 * blekit * m
    del nas

    # podział barwy: cienie turkusowe, światła ciepłe
    cien = np.clip(1 - lum / 0.45, 0, 1)[..., None] ** 1.4
    swiatlo = np.clip((lum - 0.55) / 0.45, 0, 1)[..., None] ** 1.2
    a = a + (cien * np.array([-0.025, 0.010, 0.022], np.float32) + swiatlo * np.array([0.030, 0.012, -0.030], np.float32)) * m

    # delikatna winieta obiektywu
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 0.5
    a = a * (1 - 0.13 * m * np.clip(d - 0.55, 0, 1) ** 1.6)[..., None]
    if JASNOSC:  # rozjaśnienie krzywą (gamma): czerń i biel stoją, półtony idą w górę
        a = np.clip(a, 0, 1) ** (1 / (1 + JASNOSC))
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def ziarno(img, sila=0.032, seed=7):
    """Ziarno filmowe: jednobarwne grudki (lekko rozmyty szum), najmocniejsze w półcieniach, słabsze w czerni i bieli."""
    a = np.asarray(img, np.float32) / 255.0
    H, W = a.shape[:2]
    s = W / 1280
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    c = min(0.5, 0.18 * s)  # grudki ziarna: w 4K większe (ok. 1,5 px), w 1280 prawie pojedyncze piksele
    for os_ in (0, 1):
        n = (1 - c) * n + c * 0.5 * (np.roll(n, 1, os_) + np.roll(n, -1, os_))
    n /= n.std() + 1e-6
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    waga = 0.45 + 0.55 * np.clip(1 - np.abs(lum - 0.45) / 0.55, 0, 1)
    kolor = rng.normal(0, 1, (H, W, 3)).astype(np.float32) * 0.15  # odrobina barwnego ziarna
    a = a + (n[..., None] + kolor) * (sila * waga)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def main():
    src = Path(sys.argv[1])
    maly_w = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    img = Image.open(src).convert("RGB")
    look = wyglad(img, MOC)
    stem = src.with_suffix("")
    duzy = ziarno(look, sila=0.032 * MOC)
    png, jpg = Path(f"{stem}_fuji.png"), Path(f"{stem}_fuji.jpg")
    duzy.save(png, optimize=True)
    duzy.save(jpg, quality=95, subsampling=0, optimize=True)
    out = [png, jpg]
    if maly_w:
        maly = ziarno(look.resize((maly_w, maly_w * 9 // 16), Image.LANCZOS), sila=0.026 * MOC)
        p = Path(str(stem).removesuffix("_4k") + "_fuji.jpg")
        maly.save(p, quality=92, optimize=True)
        out.append(p)
    for f in out:
        print(f, Image.open(f).size, f"{f.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
