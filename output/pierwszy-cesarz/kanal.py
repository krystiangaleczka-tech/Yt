"""Baner i zdjęcie profilowe kanału, złożone silnikiem teatru z tych samych wycinków co film i miniaturka
(papier.py, zestaw.py, miniatura.py; wygląd Fujifilm jak miniaturka, fujifilm.py).

Baner 2560 × 1440 (zalecenie YouTube). Telewizor pokazuje całość, komputer pas 2560 × 423 przez środek, telefon tylko
środek 1546 × 423 — tam stoi szyld z nazwą kanału i podpis. Po bokach czerwona kurtyna, u góry lambrekin, w głębi
scena z filmu: niebo, słońce na nitce, góry i wzgórza.
Zdjęcie profilowe 800 × 800: ta sama scena w kwadracie — kurtyna po bokach, słońce na nitce nad górami. YouTube
pokazuje je jako kółko (98 px przy kanale, 40 px przy komentarzu), więc bez napisów: ma się czytać jako „scena”.

  python3 kanal.py ["Told in Paper Theatre"]   → kanal/baner_<nazwa>.png (+ _fuji), kanal/profil.png (+ _fuji),
                                                 kanal/podglad_*.png (strefy: telefon, komputer; kółko 98 px)
  JAKOSC=1 python3 kanal.py …                  → szybki podgląd (rysowane w 1280 × 720 zamiast 2560 × 1440)
"""
import math
import os
import sys
from pathlib import Path

NAZWA = sys.argv[1] if len(sys.argv) > 1 else "Told in Paper Theatre"
PODPIS = "History, staged in paper"
sys.argv = [sys.argv[0], "en"]  # miniatura.py czyta język z argumentów: napisy po angielsku (kanał EN)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import miniatura as M  # noqa: E402  (ustawia papier.Q: JAKOSC=2 domyślnie → 2560 × 1440)
from miniatura import P, Z, papier, poloz, nitki, szyld, tabliczka, stack_k  # noqa: E402
from papier import Cam, Sprite, Stage  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "kanal"
K = M.K_TAB  # skala wycinków rysowanych kodem (w 2560 × 1440: 2)

# strefy banera w układzie ekranu 1280 × 720 (baner 2560 × 1440 to dwa razy więcej)
TELEFON = (640 - 1546 / 4, 360 - 423 / 4, 640 + 1546 / 4, 360 + 423 / 4)  # 253..1027 × 254..466
KOMPUTER = (0, 360 - 423 / 4, 1280, 360 + 423 / 4)


def lambrekin(szer=1400, wys=92):
    """Lambrekin nad sceną: czerwony pas z fałdami, złota listwa i frędzle (jak kurtyna z filmu, Z.kurtyna)."""
    R = lambda x0, y0, x1, y1: Z.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    zab = [(x, wys - 26 + (14 if (x // 70) % 2 else 0)) for x in range(0, szer + 70, 70)]  # dolny brzeg w łuki
    dol = Z.poly([(0, 0), (szer, 0)] + [(min(x, szer), y) for x, y in reversed(zab)])
    parts = [(dol, (138, 26, 28), dict(kind="gnieciony", contrast=0.8)),
             (R(0, 6, szer, 14), (206, 164, 84)), (R(0, 0, szer, 4), (150, 116, 60))]
    im = stack_k(szer, wys, parts, seed=91, k=K)
    a = np.asarray(im, np.float32)
    xx = np.arange(im.size[0], dtype=np.float32) / K
    faldy = 0.80 + 0.20 * (0.5 + 0.5 * np.cos(xx / 35.0 * np.pi)) ** 0.8  # pionowe fałdy jak na kurtynie
    a[..., :3] *= faldy[None, :, None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    for x, y in zab[:-1]:  # złote frędzle pod każdym łukiem
        for dx in range(8, 64, 9):
            yy = (y + (14 if ((x + dx) // 70) % 2 != (x // 70) % 2 else 0)) * K
            d.line([((x + dx) * K, yy - 2 * K), ((x + dx + 1) * K, yy + 9 * K)], fill=(196, 152, 70, 255), width=max(1, round(2 * K)))
    return Sprite(im, "lambrekin", rim=round(2 * K), clean=False, pad=0)


def sznur(dl=230):
    """Złoty sznur, którym związana jest kurtyna, z chwostem na końcu (arkusz: sznur od lewej, chwost po prawej)."""
    w, h = dl + 40, 150
    gold, ciemny = (214, 170, 86), (150, 112, 52)
    luk = [(x, 30 + 26 * math.sin(math.pi * x / dl)) for x in range(0, dl + 1, 10)]
    band = Z.poly([(x, y - 8) for x, y in luk] + [(x, y + 8) for x, y in reversed(luk)])
    kx, ky = dl, 30
    galka = Z.poly([(kx + 15 * math.cos(a / 12 * 2 * math.pi), ky + 15 * math.sin(a / 12 * 2 * math.pi)) for a in range(12)])
    chwost = Z.poly([(kx - 10, ky + 12), (kx + 10, ky + 12), (kx + 22, ky + 100), (kx - 22, ky + 100)])
    parts = [(band, gold, dict(kind="gnieciony", contrast=0.9)), (chwost, gold, dict(kind="gnieciony", contrast=0.9)),
             (galka, ciemny, dict(kind="gnieciony", contrast=0.9))]
    im = stack_k(w, h, parts, seed=97, k=K)
    d = ImageDraw.Draw(im)
    for i in range(-3, 4):  # nitki chwostu
        x0, x1 = (kx + i * 3) * K, (kx + i * 6.5) * K
        d.line([(x0, (ky + 22) * K), (x1, (ky + 98) * K)], fill=(*ciemny, 255), width=max(1, round(1.5 * K)))
    return Sprite(im, "sznur", rim=round(2 * K), clean=False, pad=0)


def kurtyna_faldy(strona):
    """Kurtyna z filmu (Z.kurtyna) z głębszymi fałdami: na banerze stoi duża i bliżej, płaska wyglądała jak zwykły
    czerwony papier. Kopia tutaj, nie zmiana zestaw.py — odcisk zestawu wymusiłby rysowanie wszystkich klipów od nowa."""
    im = Z.kurtyna(strona).mips[0]
    pm = np.asarray(im, np.float32) / 255.0
    al = pm[..., 3:4]
    rgb = np.where(al > 1e-3, pm[..., :3] / np.maximum(al, 1e-3), 0)
    xx = np.arange(rgb.shape[1], dtype=np.float32) * 760 / rgb.shape[1]
    faldy = 0.62 + 0.38 * (0.5 + 0.5 * np.cos(xx / 31.0 * np.pi)) ** 0.9
    rgb = rgb * faldy[None, :, None]
    out = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), al]) * 255 + 0.5).astype(np.uint8))
    return Sprite(out, f"kurtyna-faldy-{strona}", rim=2, clean=False, pad=0)


def kurtyny(st, wew_l, wew_p, h=860, y_sznura=None):
    """Dwie połowy czerwonej kurtyny zebrane do boków: wewnętrzne brzegi na ekranie w x = wew_l i wew_p; złoty sznur
    z chwostem na wysokości y_sznura (na banerze: w pasie, który widać na komputerze)."""
    for strona, x in ((-1, wew_l), (1, wew_p)):
        spr = kurtyna_faldy(strona)
        poloz(st, spr, x, -40, P.rama - 0.03, h=h, anchor=(1.0 if strona < 0 else 0.0, 0.0), sx=0.70, blur=0,
              shadow=(10 * strona, 0, 16, 0.45))
        if y_sznura:
            s = sznur()
            poloz(st, s, x + 14 * strona, y_sznura, P.rama - 0.025, w=200, anchor=(1.0 - 40 / s.w * 0.5, 0.2),
                  sx=1 if strona < 0 else -1, blur=0, shadow=(4 * strona, 6, 6, 0.4))


# Słońce złote, nie czerwone: czerwone koło na jasnym tle czyta się jak flaga Japonii — nie na kanale, który zaczyna
# od Chin. Ten sam papierowy wycinek co w filmie, przebarwiony.
ZLOTE_SLONCE = (1.04, 1.45, 0.7)


def slonce(st, x, y, w):
    """Słońce na nitce (punkt zawieszenia x, y; szerokość w) z ciepłą poświatą."""
    poloz(st, Z.glow(), x, y + w * 0.5, P.slonce, w=w * 3.0, anchor=(0.5, 0.5), mode="add", alpha=0.32, shadow=None,
          tint=(1.0, 0.85, 0.5))
    Z.hang(st, Z.S("sun", 0.5), x, y, P.slonce, 1.0, 0.0, 1, w=w, shadow=(5, 7, 9, 0.30), tint=ZLOTE_SLONCE)


def scena(baner=True):
    st = Stage(0.0, seed=7)
    st.T = 1.0
    st.cam = Cam(640, 360, 1.0, 0.5, lens=1.0, truck=0.0)
    st.focus, st.dof = P.rekwizyty, 0.35
    if baner:
        # słońce nad szyldem między chmurami (środkowej chmury nie ma, żeby go nie zasłaniała); miasto i most to
        # dekoracje Chin, na kanale ich nie ma
        Z.plan(st, 0.0, sun=0.0, clouds=(1.0, 0.0, 1.0), city=0.0, bridge=0.0, trees=(1.0, 1.0), floor=1.0)
        slonce(st, 660, 56, 180)
        kurtyny(st, 290, 990, y_sznura=372)
        poloz(st, lambrekin(), 640, -6, P.rama - 0.02, w=1400, anchor=(0.5, 0.0), blur=0, shadow=(0, 8, 12, 0.45))
        # szyld z nazwą kanału i zawieszka z podpisem: w środku 1546 × 423, który widać także na telefonie
        sz = szyld(NAZWA.upper(), k=K)
        h = min(96, 560 * sz.h / sz.w)
        nitki(st, sz, 640, 276, P.rekwizyty + 0.03, h=h, xs=(0.12, 0.88), rot=-0.6)
        tab = tabliczka(PODPIS, 56, K)
        nitki(st, tab, 640, 276 + h + 24, P.rekwizyty + 0.02, h=50, xs=(0.2, 0.8), rot=1.5)
    else:
        # kwadrat 720 × 720 ze środka kadru: słońce na nitce nad górami, kurtyna po bokach, lambrekin u góry
        Z.plan(st, 0.0, sun=0.0, city=0.0, bridge=0.0, trees=(0.0, 0.0), floor=1.0)
        slonce(st, 640, 150, 330)
        kurtyny(st, 420, 860, h=900)
        poloz(st, lambrekin(), 640, -6, P.rama - 0.02, w=1400, anchor=(0.5, 0.0), blur=0, shadow=(0, 8, 12, 0.45))
    st.grade = (1.0, 0.98, 0.97)
    return st


def strefy(img):
    """Podgląd banera ze strefami: telefon (żółta ramka) i komputer (biała)."""
    q = img.size[0] / 1280
    im = img.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1), kolor in ((KOMPUTER, (255, 255, 255)), (TELEFON, (255, 214, 0))):
        d.rectangle([x0 * q, y0 * q, x1 * q - 1, y1 * q - 1], outline=kolor, width=max(2, round(3 * q)))
    return im


def kolko(img, d=98):
    """Zdjęcie profilowe tak, jak pokazuje je YouTube: kółko d × d na białym tle."""
    mal = img.convert("RGB").resize((d, d), Image.LANCZOS)
    tlo = Image.new("RGB", (d + 20, d + 20), (255, 255, 255))
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * 4 - 1, d * 4 - 1], fill=255)
    tlo.paste(mal, (10, 10), m.resize((d, d), Image.LANCZOS))
    return tlo


def main():
    OUT.mkdir(exist_ok=True)
    slug = NAZWA.lower().replace(" ", "_")
    baner = M.wyrownaj(scena(True).render(), 1.2 * papier.Q * 0.7)
    if baner.size[0] < 2560:  # szybki podgląd JAKOSC=1
        baner = baner.resize((2560, 1440), Image.LANCZOS)
    pb = OUT / f"baner_{slug}.png"
    baner.save(pb, optimize=True)
    strefy(baner).resize((1280, 720), Image.LANCZOS).save(OUT / f"podglad_baner_{slug}.png")
    w, h = baner.size  # to, co widać na telefonie i na komputerze
    baner.crop((round(TELEFON[0] * w / 1280), round(TELEFON[1] * h / 720), round(TELEFON[2] * w / 1280), round(TELEFON[3] * h / 720))) \
        .resize((773, 212), Image.LANCZOS).save(OUT / f"podglad_telefon_{slug}.png")
    print(pb, baner.size, f"{pb.stat().st_size / 1e6:.1f} MB")

    prof = M.wyrownaj(scena(False).render(), 1.2 * papier.Q * 0.7)
    q = prof.size[0] / 1280
    prof = prof.crop((round(280 * q), 0, round(1000 * q), round(720 * q))).resize((800, 800), Image.LANCZOS)
    pp = OUT / "profil.png"
    prof.save(pp, optimize=True)
    kolko(prof, 98).save(OUT / "podglad_profil_98.png")
    kolko(prof, 40).save(OUT / "podglad_profil_40.png")
    print(pp, prof.size)


if __name__ == "__main__":
    main()
