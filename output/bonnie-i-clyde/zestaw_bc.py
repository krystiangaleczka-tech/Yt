"""Zestaw filmu „Bonnie and Clyde: The Outlaws Made of Paper”: lalki z lat 30., rama teatru oklejona gazetami
i wycinanki tego filmu (auta, gazety, drukarnia, preria, miasteczko, wnętrza, więzienie, las, teatr cieni).

Papiery, faktury, darte krawędzie, chmury, słońce, nitki i wysuwanie od dołu bierze z output/pierwszy-cesarz/zestaw.py —
ten sam styl i to samo światło. Krajobraz i postacie są wycinane kodem od nowa (księga świata D4: sceneria lat 30. w USA,
bez krajobrazu Chin i Japonii).

Lalka = korpus (głowa, strój, nogi) + dwie ręce na zawiasie w barku — ten sam układ arkusza co „Syn słońca”
(output/powstanie-japonii/zestaw_jp.py), więc scena.lalka składa ją tymi samymi liczbami (bark, dłoń, stopa, oczy).
"""
import math
import random
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "pierwszy-cesarz"))

import zestaw as Z0  # noqa: E402
from papier import CX, CY, H, W, Sprite, back, clamp, ease, ease_out, noise, settle  # noqa: E402,F401
from zestaw import (FONT_PL, PL_IDX, S, ell, flame, glow, glue, glyphs, hang, moon, over,  # noqa: E402,F401
                    paper, piece, poly, prop, rect, reeds, rise, rough_mask, sky, stack, stage_floor, tag, texture)

P = Z0.P
JEZYK = "en"


def tr(txt):
    """Napisy w kadrze są już po angielsku (księga świata D3, wytyczne 1.13)."""
    return txt


Z0.tr = tr
GOLD = (210, 168, 82)
INK = (40, 28, 24)
SKORA = (238, 206, 172)
GAZETA = (236, 228, 206)  # papier gazetowy
FARBA = (44, 38, 34)  # farba drukarska


def _shade(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c)


def _band(p0, p1, wd):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / L * wd / 2, (x1 - x0) / L * wd / 2
    return poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])


def _kolka(pts, r):
    """Kształt z kółek (loki, korona drzewa, dym): union kół o promieniu r w punktach pts."""
    return lambda d, s: [d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], fill=255) for x, y in pts]


# ---------- lalki z lat 30. ----------

FIG_W, FIG_H, STOPA, BIODRO, CZUBEK = 300, 690, 676, 412, 62
BARK = {"przod": (182, 222), "tyl": (120, 222)}  # zawias ręki na korpusie
RAMIE_W, RAMIE_H, RAMIE_ZAWIAS, DLON = 110, 300, (55, 26), (55, 232)

BAZA = dict(kobieta=False, skora=SKORA, wlosy=(70, 50, 36), fryzura="krotkie", kapelusz=None, kapelusz_kolor=(60, 56, 54),
            stroj="garnitur", gora=(78, 76, 82), dol=(70, 68, 74), koszula=(236, 232, 220), krawat=(130, 40, 36),
            wzor=None, wzor_kolor=None, kolnierzyk=None, fartuch=None, buty=(46, 34, 28), wasy=False, broda=False,
            okulary=False, odznaka=False, cygaro=False, szer=1.0, nogi=0, oczy="otwarte", rekaw=None, siwe=False,
            pas=None, kozaki=False, usta=None)

LALKI = {
    # Bonnie: drobna, jasne kręcone włosy, beret; sukienka do kolan (księga świata)
    "bonnie": dict(kobieta=True, wlosy=(214, 176, 104), fryzura="loki", kapelusz="beret", kapelusz_kolor=(150, 40, 46),
                   stroj="sukienka", gora=(84, 112, 150), dol=(84, 112, 150), wzor="kropki", wzor_kolor=(240, 232, 214),
                   kolnierzyk=(240, 234, 222), pas=(150, 40, 46), szer=0.94),
    "bonnie_cygaro": dict(kobieta=True, wlosy=(214, 176, 104), fryzura="loki", kapelusz="beret", kapelusz_kolor=(150, 40, 46),
                          stroj="sukienka", gora=(84, 112, 150), dol=(84, 112, 150), wzor="kropki", wzor_kolor=(240, 232, 214),
                          kolnierzyk=(240, 234, 222), pas=(150, 40, 46), szer=0.94, cygaro=True),
    "bonnie_kelnerka": dict(kobieta=True, wlosy=(214, 176, 104), fryzura="loki", stroj="sukienka", gora=(196, 160, 150),
                            dol=(196, 160, 150), fartuch=(244, 240, 230), kolnierzyk=(244, 240, 230), szer=0.94),
    "bonnie_czerwona": dict(kobieta=True, wlosy=(214, 176, 104), fryzura="loki", kapelusz=None, stroj="sukienka",
                            gora=(170, 40, 40), dol=(170, 40, 40), kolnierzyk=(240, 230, 220), szer=0.94),
    "bonnie_mala": dict(kobieta=True, wlosy=(222, 186, 114), fryzura="loki", stroj="sukienka", gora=(236, 200, 120),
                        dol=(236, 200, 120), kolnierzyk=(250, 246, 236), pas=(200, 60, 60), szer=0.92),
    "bonnie_slub": dict(kobieta=True, wlosy=(214, 176, 104), fryzura="loki", kapelusz="welon", stroj="sukienka",
                        gora=(246, 242, 232), dol=(246, 242, 232), kolnierzyk=(250, 248, 240), szer=0.94),
    "clyde": dict(fryzura="zaczesane", wlosy=(46, 34, 28), kapelusz="fedora", kapelusz_kolor=(64, 58, 54), gora=(82, 78, 86),
                  dol=(78, 74, 82), krawat=(140, 44, 40), szer=0.96),
    "clyde_maly": dict(fryzura="krotkie", wlosy=(52, 38, 30), stroj="ogrodniczki", gora=(150, 120, 96), dol=(86, 104, 140),
                       koszula=(196, 170, 140), szer=0.9),
    "clyde_nastolatek": dict(fryzura="krotkie", wlosy=(52, 38, 30), kapelusz="kaszkiet", kapelusz_kolor=(110, 96, 80),
                             stroj="koszula", gora=(196, 182, 160), dol=(96, 86, 76), koszula=(196, 182, 160), szer=0.94),
    "clyde_wiezien": dict(fryzura="krotkie", wlosy=(46, 34, 28), stroj="pasiak", gora=(236, 232, 220), dol=(236, 232, 220), szer=0.96),
    "buck": dict(fryzura="krotkie", wlosy=(62, 46, 34), kapelusz="kaszkiet", kapelusz_kolor=(96, 84, 70), stroj="kamizelka",
                 gora=(110, 92, 70), dol=(84, 80, 76), koszula=(222, 214, 196), wasy=True, szer=1.06),
    "buck_wiezien": dict(fryzura="krotkie", wlosy=(62, 46, 34), stroj="pasiak", gora=(236, 232, 220), dol=(236, 232, 220),
                         wasy=True, szer=1.06),
    "blanche": dict(kobieta=True, wlosy=(60, 40, 30), fryzura="fala", kapelusz="kapelusik", kapelusz_kolor=(60, 90, 70),
                    stroj="plaszcz", gora=(96, 130, 108), dol=(96, 130, 108), kolnierzyk=(226, 220, 206)),
    "wd": dict(fryzura="krotkie", wlosy=(120, 86, 52), kapelusz="kaszkiet", kapelusz_kolor=(130, 116, 92), stroj="koszula",
               gora=(176, 196, 214), dol=(110, 98, 84), koszula=(176, 196, 214), szer=0.88),
    "roy": dict(fryzura="zaczesane", wlosy=(80, 60, 40), stroj="garnitur", gora=(120, 104, 84), dol=(110, 96, 80),
                krawat=(60, 70, 110), szer=0.96),
    "hamer": dict(fryzura="krotkie", wlosy=(80, 70, 60), kapelusz="stetson", kapelusz_kolor=(196, 176, 140), stroj="plaszcz",
                  gora=(120, 98, 72), dol=(110, 92, 70), koszula=(230, 222, 204), krawat=(60, 50, 40), odznaka=True, szer=1.14,
                  nogi=20),
    "gault": dict(fryzura="krotkie", wlosy=(120, 110, 100), kapelusz="stetson", kapelusz_kolor=(150, 130, 100), stroj="kamizelka",
                  gora=(96, 84, 70), dol=(90, 82, 74), odznaka=True, szer=1.04),
    "alcorn": dict(kapelusz="fedora", kapelusz_kolor=(90, 84, 70), gora=(110, 100, 86), dol=(100, 92, 80), odznaka=True),
    "hinton": dict(kapelusz="fedora", kapelusz_kolor=(70, 66, 60), gora=(90, 92, 100), dol=(84, 86, 94), okulary=True, odznaka=True),
    "jordan": dict(kapelusz="stetson", kapelusz_kolor=(120, 104, 80), stroj="kamizelka", gora=(70, 70, 76), dol=(80, 80, 86),
                   odznaka=True, wasy=True, szer=1.06),
    "oakley": dict(kapelusz="fedora", kapelusz_kolor=(110, 96, 76), stroj="koszula", gora=(200, 190, 170), dol=(96, 90, 80),
                   koszula=(200, 190, 170), odznaka=True),
    "simmons": dict(fryzura="lysy", wlosy=(150, 140, 130), gora=(60, 60, 70), dol=(56, 56, 64), okulary=True, krawat=(30, 30, 40),
                    szer=1.12),
    "darby": dict(fryzura="zaczesane", wlosy=(40, 32, 28), gora=(30, 30, 34), dol=(28, 28, 32), krawat=(20, 20, 22),
                  koszula=(244, 242, 236), szer=0.94),
    "darby_fartuch": dict(fryzura="zaczesane", wlosy=(40, 32, 28), stroj="koszula", gora=(244, 242, 236), dol=(28, 28, 32),
                          fartuch=(230, 232, 228), koszula=(244, 242, 236), szer=0.94),
    "stone": dict(kobieta=True, wlosy=(110, 76, 50), fryzura="fala", kapelusz="kapelusik", kapelusz_kolor=(120, 70, 60),
                  stroj="plaszcz", gora=(150, 110, 90), dol=(150, 110, 90), kolnierzyk=(220, 210, 196)),
    "ivy": dict(fryzura="krotkie", wlosy=(130, 120, 110), kapelusz="slomkowy", kapelusz_kolor=(214, 188, 120), stroj="ogrodniczki",
                gora=(86, 104, 140), dol=(86, 104, 140), koszula=(200, 180, 150), broda=True, szer=1.04),
    "henry": dict(fryzura="krotkie", wlosy=(140, 100, 60), kapelusz="kaszkiet", kapelusz_kolor=(100, 90, 76), stroj="koszula",
                  gora=(214, 200, 176), dol=(90, 84, 76), koszula=(214, 200, 176), szer=0.92),
    "henry_wiezien": dict(fryzura="krotkie", wlosy=(140, 100, 60), stroj="pasiak", gora=(236, 232, 220), dol=(236, 232, 220),
                          szer=0.92),
    "boyd": dict(kapelusz="czapka", kapelusz_kolor=(40, 50, 76), stroj="mundur", gora=(46, 56, 84), dol=(46, 56, 84), odznaka=True,
                 pas=(70, 50, 36), szer=1.04),
    "campbell": dict(fryzura="siwe", wlosy=(200, 196, 190), kapelusz="stetson", kapelusz_kolor=(150, 140, 120), stroj="kamizelka",
                     gora=(90, 80, 70), dol=(90, 84, 78), odznaka=True, wasy=True, siwe=True),
    "murphy": dict(kapelusz="czapka", kapelusz_kolor=(150, 120, 80), stroj="mundur", gora=(170, 140, 96), dol=(170, 140, 96),
                   odznaka=True, pas=(90, 60, 36), kozaki=True, szer=0.96),
    "wheeler": dict(kapelusz="czapka", kapelusz_kolor=(150, 120, 80), stroj="mundur", gora=(162, 134, 92), dol=(162, 134, 92),
                    odznaka=True, pas=(90, 60, 36), kozaki=True, wasy=True),
    "tullis": dict(kobieta=True, wlosy=(80, 56, 38), fryzura="fala", kapelusz="welon", stroj="sukienka", gora=(246, 242, 232),
                   dol=(246, 242, 232), kolnierzyk=(250, 248, 240), szer=0.94),
    "policjant": dict(kapelusz="czapka", kapelusz_kolor=(36, 44, 66), stroj="mundur", gora=(40, 50, 76), dol=(40, 50, 76),
                      odznaka=True, pas=(70, 50, 36)),
    "policjant2": dict(kapelusz="czapka", kapelusz_kolor=(36, 44, 66), stroj="mundur", gora=(44, 54, 80), dol=(44, 54, 80),
                       odznaka=True, pas=(70, 50, 36), wasy=True, szer=1.08),
    "detektyw": dict(kapelusz="fedora", kapelusz_kolor=(90, 70, 54), stroj="plaszcz", gora=(120, 96, 70), dol=(90, 80, 70),
                     odznaka=True, wasy=True),
    "szeryf": dict(kapelusz="stetson", kapelusz_kolor=(160, 140, 110), stroj="kamizelka", gora=(110, 90, 64), dol=(96, 88, 80),
                   odznaka=True, wasy=True, szer=1.08),
    "straznik": dict(kapelusz="stetson", kapelusz_kolor=(140, 120, 90), stroj="koszula", gora=(170, 150, 112), dol=(110, 96, 80),
                     koszula=(170, 150, 112), odznaka=True, kozaki=True),
    "wiezien": dict(fryzura="krotkie", wlosy=(80, 60, 46), stroj="pasiak", gora=(236, 232, 220), dol=(236, 232, 220)),
    "wiezien2": dict(fryzura="krotkie", wlosy=(40, 30, 26), stroj="pasiak", gora=(236, 232, 220), dol=(236, 232, 220), szer=1.1),
    "olbrzym": dict(fryzura="lysy", wlosy=(60, 50, 40), stroj="pasiak", gora=(236, 232, 220), dol=(236, 232, 220), szer=1.24,
                    nogi=40, broda=True),
    "farmer": dict(fryzura="krotkie", wlosy=(110, 90, 70), kapelusz="slomkowy", kapelusz_kolor=(214, 188, 120), stroj="ogrodniczki",
                   gora=(86, 104, 140), dol=(86, 104, 140), koszula=(210, 120, 100), szer=1.04),
    "farmer2": dict(fryzura="krotkie", wlosy=(60, 50, 40), kapelusz="kaszkiet", kapelusz_kolor=(90, 80, 60), stroj="ogrodniczki",
                    gora=(120, 110, 90), dol=(120, 110, 90), koszula=(200, 200, 186), wasy=True),
    "farmerka": dict(kobieta=True, wlosy=(120, 90, 60), fryzura="kok", stroj="sukienka", gora=(180, 160, 120), dol=(180, 160, 120),
                     fartuch=(236, 230, 214), wzor="kwiatki", wzor_kolor=(200, 90, 80)),
    "matka_bonnie": dict(kobieta=True, wlosy=(170, 166, 160), fryzura="kok", stroj="sukienka", gora=(110, 90, 110),
                         dol=(110, 90, 110), fartuch=(232, 226, 210), siwe=True, okulary=True),
    "matka_clyde": dict(kobieta=True, wlosy=(150, 146, 140), fryzura="kok", stroj="sukienka", gora=(90, 96, 80), dol=(90, 96, 80),
                        fartuch=(224, 218, 200), siwe=True, szer=1.06),
    "przyjaciolka": dict(kobieta=True, wlosy=(60, 40, 30), fryzura="fala", stroj="sukienka", gora=(220, 170, 80), dol=(220, 170, 80),
                         wzor="kwiatki", wzor_kolor=(250, 236, 200)),
    "gazeciarz": dict(fryzura="krotkie", wlosy=(160, 110, 60), kapelusz="kaszkiet", kapelusz_kolor=(120, 96, 70), stroj="koszula",
                      gora=(220, 210, 190), dol=(110, 90, 70), koszula=(220, 210, 190), szer=0.86),
    "kasjer": dict(fryzura="lysy", wlosy=(100, 90, 80), stroj="koszula", gora=(230, 226, 214), dol=(80, 76, 72), koszula=(230, 226, 214),
                   okulary=True, krawat=(110, 40, 30)),
    "sprzedawca": dict(fryzura="krotkie", wlosy=(110, 100, 90), stroj="koszula", gora=(232, 228, 216), dol=(90, 86, 80),
                       fartuch=(236, 232, 220), wasy=True),
    "reporter": dict(kapelusz="fedora", kapelusz_kolor=(120, 100, 76), stroj="garnitur", gora=(150, 130, 100), dol=(120, 110, 96),
                     krawat=(150, 50, 40)),
    "fotograf": dict(kapelusz="kaszkiet", kapelusz_kolor=(80, 74, 66), stroj="kamizelka", gora=(96, 90, 80), dol=(80, 76, 72),
                     koszula=(236, 230, 214)),
    "drukarz": dict(fryzura="krotkie", wlosy=(80, 60, 40), kapelusz="papierowa", kapelusz_kolor=GAZETA, stroj="koszula",
                    gora=(220, 214, 200), dol=(90, 86, 80), fartuch=(160, 150, 130), koszula=(220, 214, 200)),
    "recepcjonista": dict(fryzura="zaczesane", wlosy=(50, 40, 34), stroj="kamizelka", gora=(110, 50, 44), dol=(70, 66, 64),
                          koszula=(236, 232, 220), krawat=(40, 40, 50)),
    "przechodzien": dict(kapelusz="fedora", kapelusz_kolor=(110, 100, 90), stroj="plaszcz", gora=(130, 116, 96), dol=(96, 90, 84)),
    "przechodzien2": dict(kapelusz="melonik", kapelusz_kolor=(40, 36, 34), stroj="garnitur", gora=(70, 70, 80), dol=(66, 66, 76),
                          wasy=True),
    "przechodzien3": dict(kapelusz="kaszkiet", kapelusz_kolor=(90, 80, 70), stroj="kamizelka", gora=(120, 100, 80), dol=(100, 90, 80),
                          koszula=(220, 214, 200)),
    "przechodnia": dict(kobieta=True, wlosy=(90, 60, 40), fryzura="fala", kapelusz="kapelusik", kapelusz_kolor=(150, 70, 70),
                        stroj="plaszcz", gora=(140, 120, 100), dol=(140, 120, 100), kolnierzyk=(220, 210, 196)),
    "przechodnia2": dict(kobieta=True, wlosy=(40, 30, 26), fryzura="fala", stroj="sukienka", gora=(90, 120, 110), dol=(90, 120, 110),
                         wzor="kropki", wzor_kolor=(240, 230, 210)),
    "bezrobotny": dict(kapelusz="fedora", kapelusz_kolor=(100, 92, 84), stroj="plaszcz", gora=(110, 104, 96), dol=(90, 86, 80),
                       wasy=True),
    "aktorka": dict(kobieta=True, wlosy=(232, 206, 150), fryzura="loki", kapelusz="beret", kapelusz_kolor=(60, 50, 70),
                    stroj="sukienka", gora=(220, 200, 150), dol=(220, 200, 150), kolnierzyk=(250, 246, 236), szer=0.94),
    "aktor": dict(fryzura="zaczesane", wlosy=(70, 50, 34), kapelusz="fedora", kapelusz_kolor=(200, 190, 170), gora=(206, 196, 176),
                  dol=(196, 186, 166), krawat=(200, 60, 50)),
    "aktor_hamer": dict(kapelusz="stetson", kapelusz_kolor=(196, 176, 140), stroj="plaszcz", gora=(120, 98, 72), dol=(110, 92, 70),
                        odznaka=True, szer=1.1),
    "blanche_stara": dict(kobieta=True, wlosy=(200, 196, 192), fryzura="kok", stroj="sukienka", gora=(120, 140, 170),
                          dol=(120, 140, 170), siwe=True, okulary=True),
    "crowson": dict(kapelusz="stetson", kapelusz_kolor=(150, 130, 100), stroj="koszula", gora=(176, 156, 120), dol=(110, 96, 80),
                    koszula=(176, 156, 120), odznaka=True),
    "bucher": dict(fryzura="siwe", wlosy=(190, 186, 180), stroj="koszula", gora=(230, 226, 214), dol=(90, 86, 80),
                   fartuch=(236, 232, 220), wasy=True, siwe=True),
    "moore": dict(kapelusz="stetson", kapelusz_kolor=(150, 130, 100), stroj="kamizelka", gora=(100, 86, 70), dol=(90, 84, 76),
                  odznaka=True),
}


def spec(key):
    out = dict(BAZA)
    out.update(LALKI[key])
    return out


def _wlosy_tyl(s, parts):
    """Włosy za głową (przed korpusem w kolejności arkusza): loki do ramion, fala, kok."""
    h = s["wlosy"]
    fr = s["fryzura"]
    if fr == "loki":
        pts = [(108, 150), (104, 176), (112, 200), (126, 210), (184, 206), (196, 190), (198, 166), (100, 128), (200, 136)]
        parts.append((_kolka(pts, 20), h, dict(edge=2)))
    elif fr == "fala":
        parts.append((poly([(106, 110), (198, 108), (204, 170), (186, 196), (118, 196), (100, 168)]), h))
    elif fr == "kok":
        parts.append((ell(110, 104, 18, 16), h, dict(edge=2)))


def _wlosy_przod(s, parts):
    h = s["wlosy"]
    fr = s["fryzura"]
    if fr in ("krotkie", "siwe"):
        parts.append((poly([(112, 120), (114, 92), (132, 76), (160, 70), (184, 78), (194, 100), (192, 112), (178, 100), (150, 94),
                            (126, 104)]), h))
    elif fr == "zaczesane":
        parts.append((poly([(112, 122), (112, 92), (130, 72), (166, 64), (192, 76), (198, 100), (190, 106), (170, 90), (146, 92),
                            (124, 106)]), h, dict(kind="gladki", contrast=0.7)))
    elif fr == "lysy":
        parts.append((poly([(112, 126), (114, 104), (124, 100), (124, 128)]), h))
    elif fr == "loki":
        pts = [(116, 102), (128, 84), (146, 76), (166, 76), (184, 86), (194, 104), (112, 124)]
        parts.append((_kolka(pts, 17), h, dict(edge=2)))
    elif fr in ("fala", "kok"):
        parts.append((poly([(110, 124), (112, 90), (134, 72), (162, 66), (188, 78), (198, 104), (192, 116), (176, 96), (150, 92),
                            (124, 106)]), h))


def _kapelusz(s, parts):
    k, c = s["kapelusz"], s["kapelusz_kolor"]
    dark = _shade(c, 0.6)
    if k == "fedora":
        parts += [(poly([(116, 92), (190, 92), (184, 58), (166, 50), (152, 58), (138, 50), (120, 58)]), c, dict(edge=2)),
                  (rect(116, 80, 190, 92), dark),
                  (ell(153, 94, 70, 11), c, dict(edge=2))]
    elif k == "stetson":
        parts += [(poly([(110, 94), (196, 94), (190, 50), (170, 38), (153, 48), (136, 38), (116, 50)]), c, dict(edge=2)),
                  (rect(110, 80, 196, 94), dark),
                  (poly([(66, 92), (100, 98), (206, 98), (240, 92), (232, 104), (204, 108), (102, 108), (74, 104)]), c, dict(edge=2))]
    elif k == "beret":
        parts += [(ell(138, 82, 58, 22), c, dict(edge=2)), (ell(132, 64, 5, 7), dark)]
    elif k == "kaszkiet":
        parts += [(poly([(108, 100), (112, 76), (140, 64), (178, 66), (198, 82), (200, 98)]), c, dict(edge=2)),
                  (poly([(176, 92), (226, 100), (222, 108), (186, 106)]), dark)]
    elif k == "czapka":
        parts += [(poly([(110, 60), (198, 60), (192, 96), (116, 96)]), c, dict(edge=2)),
                  (rect(114, 86, 194, 98), _shade(c, 0.7)),
                  (poly([(160, 96), (220, 102), (214, 110), (170, 108)]), (24, 22, 22)),
                  (ell(154, 76, 8, 9), GOLD)]
    elif k == "slomkowy":
        parts += [(poly([(116, 94), (190, 94), (186, 62), (152, 54), (120, 62)]), c, dict(edge=2)),
                  (rect(116, 82, 190, 94), (150, 60, 50)),
                  (ell(153, 96, 80, 13), c, dict(edge=2))]
    elif k == "kapelusik":
        parts += [(poly([(104, 124), (106, 92), (126, 70), (156, 62), (186, 70), (202, 92), (204, 120), (190, 110), (120, 110)]), c,
                   dict(edge=2)),
                  (rect(106, 100, 202, 110), dark),
                  (ell(184, 92, 9, 7), (230, 210, 170))]
    elif k == "melonik":
        parts += [(ell(153, 76, 40, 30), c, dict(edge=2)), (ell(153, 96, 56, 9), c, dict(edge=2))]
    elif k == "welon":
        parts += [(poly([(110, 96), (196, 96), (232, 300), (226, 420), (80, 420), (74, 300)]), (250, 250, 246),
                   dict(kind="gladki", contrast=0.5)),
                  (ell(153, 86, 46, 14), (250, 250, 246))]
    elif k == "papierowa":
        parts += [(poly([(108, 98), (198, 98), (153, 52)]), c, dict(edge=2))]


def _korpus_img(s):
    L = s["nogi"]
    w, h = FIG_W, FIG_H + L
    Y = lambda y: y + L if y >= BIODRO else y
    PL = lambda pts: poly([(x, Y(y)) for x, y in pts])
    parts = []
    if s["kapelusz"] == "welon":
        parts.append((poly([(116, 110), (190, 110), (236, 320), (230, 440), (76, 440), (70, 320)]), (246, 246, 240),
                      dict(kind="gladki", contrast=0.5)))
    _wlosy_tyl(s, parts)
    parts.append((rect(136, 158, 166, 216), _shade(s["skora"], 0.92)))  # szyja
    sk, g, d_, buty = s["skora"], s["gora"], s["dol"], s["buty"]
    st = s["stroj"]
    if s["kobieta"]:
        # nogi w pończochach pod spódnicą do kolan, buty na obcasie
        parts += [(PL([(112, 540), (136, 540), (134, 654), (116, 654)]), _shade(sk, 0.94)),
                  (PL([(164, 540), (188, 540), (186, 654), (168, 654)]), _shade(sk, 0.88)),
                  (PL([(108, 648), (140, 648), (150, 668), (148, 676), (108, 676)]), buty),
                  (PL([(162, 648), (194, 648), (204, 668), (202, 676), (162, 676)]), _shade(buty, 0.9))]
        if st == "plaszcz":
            parts.append((PL([(90, 300), (210, 300), (230, 576), (70, 576)]), g, dict(edge=2, shade=0.15)))
        else:
            parts.append((PL([(92, 330), (208, 330), (230, 566), (70, 566)]), d_, dict(edge=2, shade=0.15)))
        parts.append((poly([(98, 204), (202, 204), (208, 336), (92, 336)]), g, dict(edge=2)))
    else:
        if s["kozaki"]:
            parts += [(PL([(88, 404), (152, 404), (162, 470), (146, 540), (100, 540), (82, 470)]), d_, dict(edge=2)),
                      (PL([(148, 404), (212, 404), (218, 470), (200, 540), (154, 540), (140, 470)]), _shade(d_, 0.92), dict(edge=2)),
                      (PL([(100, 530), (146, 530), (144, 652), (102, 652)]), (60, 40, 30)),
                      (PL([(156, 530), (202, 530), (200, 652), (158, 652)]), (54, 36, 28))]
        else:
            parts += [(PL([(90, 404), (152, 404), (148, 654), (100, 654)]), d_, dict(edge=2)),
                      (PL([(150, 404), (210, 404), (206, 654), (156, 654)]), _shade(d_, 0.9), dict(edge=2))]
        parts += [(PL([(92, 648), (146, 648), (166, 664), (162, 676), (92, 676)]), buty),
                  (PL([(154, 648), (208, 648), (228, 664), (224, 676), (154, 676)]), _shade(buty, 0.9))]
        if st == "pasiak":
            pass  # paski dorysowane niżej, na całym ubraniu
        if st == "ogrodniczki":
            parts += [(poly([(96, 204), (204, 204), (210, 420), (90, 420)]), s["koszula"], dict(edge=2)),
                      (PL([(104, 300), (196, 300), (204, 420), (96, 420)]), g, dict(edge=2)),
                      (rect(116, 230, 184, 304), g), (_band((118, 230), (110, 204), 10), g), (_band((182, 230), (190, 204), 10), g)]
        elif st == "plaszcz":
            parts += [(PL([(86, 204), (214, 204), (226, 560), (74, 560)]), g, dict(edge=2, shade=0.12))]
        elif st in ("garnitur", "kamizelka", "mundur", "koszula", "pasiak"):
            dl = 452 if st in ("garnitur", "mundur") else 420
            parts.append((poly([(94, 204), (206, 204), (214, 300), (222, dl), (78, dl), (86, 300)]),
                          s["koszula"] if st in ("kamizelka", "koszula") else g, dict(edge=2)))
            if st == "kamizelka":
                parts.append((poly([(104, 214), (196, 214), (204, 420), (96, 420)]), g, dict(edge=2)))
    # pasiak: poziome czarne pasy na całym stroju więźnia
    if st == "pasiak":
        parts.append((poly([(94, 204), (206, 204), (214, 300), (218, 420), (82, 420), (86, 300)]), g, dict(edge=2)))
    # dekolt, koszula, krawat, klapy
    if not s["kobieta"] and st in ("garnitur", "plaszcz", "mundur"):
        parts += [(poly([(126, 204), (176, 204), (152, 262)]), s["koszula"])]
        if s["krawat"] and st != "mundur":
            parts.append((poly([(146, 212), (158, 212), (162, 284), (152, 296), (142, 284)]), s["krawat"]))
        kl = _shade(g, 0.82)
        parts += [(poly([(120, 204), (136, 204), (152, 270), (140, 300), (126, 250)]), kl),
                  (poly([(168, 204), (184, 204), (178, 250), (164, 300), (152, 270)]), kl)]
    if s["kobieta"] and s["kolnierzyk"]:
        parts += [(poly([(118, 200), (152, 208), (150, 232), (122, 226)]), s["kolnierzyk"]),
                  (poly([(152, 208), (186, 200), (182, 226), (154, 232)]), s["kolnierzyk"])]
    if s["fartuch"]:
        if s["kobieta"]:
            parts.append((PL([(108, 330), (192, 330), (204, 540), (96, 540)]), s["fartuch"], dict(kind="gladki", contrast=0.6)))
        else:
            parts.append((PL([(104, 250), (196, 250), (206, 560), (94, 560)]), s["fartuch"], dict(kind="gladki", contrast=0.6)))
    if s["pas"]:
        parts.append((poly([(92, 326), (208, 326), (210, 342), (90, 342)]), s["pas"]))
        parts.append((rect(146, 324, 160, 344), GOLD))
    if s["odznaka"]:
        gwiazda = [(176 + 13 * math.cos(math.radians(a)) * (1 if k % 2 == 0 else 0.45),
                    250 + 13 * math.sin(math.radians(a)) * (1 if k % 2 == 0 else 0.45)) for k, a in enumerate(range(-90, 270, 36))]
        parts.append((poly(gwiazda), GOLD, dict(kind="gladki", rough=0.5)))
    # głowa
    parts += [(ell(118, 132, 9, 13), _shade(sk, 0.95)),
              (ell(152, 128, 38, 48), sk, dict(kind="gladki", contrast=0.6)),
              (poly([(184, 112), (200, 138), (186, 146)]), sk, dict(kind="gladki", contrast=0.6))]
    _wlosy_przod(s, parts)
    if s["broda"]:
        parts.append((poly([(140, 160), (176, 150), (194, 148), (190, 176), (172, 202), (150, 196), (136, 180)]), s["wlosy"]))
    if s["wasy"] or s["broda"]:
        parts.append((poly([(160, 154), (192, 148), (190, 157), (166, 160)]), _shade(s["wlosy"], 0.8)))
    _kapelusz(s, parts)
    im = stack(w, h, parts, seed=sum(map(ord, str(sorted(s.items())))) % 997)
    d = ImageDraw.Draw(im)
    ink = INK + (235,)
    hair = s["wlosy"]
    if s["oczy"] == "otwarte":
        for x0, x1, yy in ((130, 144, 124), (164, 178, 122)):
            d.line([(x0 - 2, yy - 9), (x1 + 2, yy - 11 if x0 > 150 else yy - 10)], fill=_shade(hair, 0.8) + (240,), width=4)
            d.line([(x0, yy), (x1, yy)], fill=ink, width=3)
            d.ellipse([(x0 + x1) / 2 - 3.5 + 2, yy - 1, (x0 + x1) / 2 + 3.5 + 2, yy + 7], fill=ink)
    else:
        for x0, x1, yy in ((130, 144, 126), (164, 178, 124)):
            d.arc([x0, yy - 6, x1, yy + 6], 20, 160, fill=ink, width=3)
    if s["okulary"]:
        for cx in (137, 171):
            d.ellipse([cx - 13, 112, cx + 13, 136], outline=(30, 26, 24, 240), width=3)
        d.line([(150, 122), (158, 122)], fill=(30, 26, 24, 240), width=3)
    d.line([(184, 128), (190, 140)], fill=_shade(sk, 0.75) + (200,), width=2)
    blush = Image.new("L", (w, h), 0)
    ImageDraw.Draw(blush).ellipse([160, 136, 184, 152], fill=80 if s["kobieta"] else 36)
    blush = blush.filter(ImageFilter.GaussianBlur(4))
    tint = Image.new("RGBA", (w, h), (220, 110, 100, 0))
    tint.putalpha(blush)
    im.alpha_composite(tint)
    if s["kobieta"]:
        d.line([(164, 162), (176, 161)], fill=(180, 40, 50, 240), width=5)
    elif not (s["broda"] or s["wasy"]):
        d.line([(162, 162), (176, 160)], fill=ink, width=3)
    if s["cygaro"]:
        d.line([(172, 162), (214, 152)], fill=(96, 62, 40, 255), width=8)
        d.line([(210, 153), (216, 151)], fill=(190, 186, 180, 255), width=8)
    if s["stroj"] == "pasiak" or (s["stroj"] == "pasiak"):
        for yy in range(222, 650, 26):
            x0 = 84 if yy < 420 else 92
            x1 = 216 if yy < 420 else 208
            d.line([(x0, Y(yy)), (x1, Y(yy))], fill=(36, 34, 34, 230), width=9)
    if s["wzor"] == "kropki":
        r = random.Random(9)
        top = 336 if s["kobieta"] else 230
        for k in range(26):
            yy = r.uniform(214, 556)
            half = 46 + (yy - 204) * 0.12
            xx = 150 + r.uniform(-half, half)
            d.ellipse([xx - 4, Y(yy) - 4, xx + 4, Y(yy) + 4], fill=tuple(s["wzor_kolor"]) + (220,))
    elif s["wzor"] == "kwiatki":
        r = random.Random(11)
        for k in range(18):
            yy = r.uniform(214, 556)
            half = 46 + (yy - 204) * 0.12
            xx = 150 + r.uniform(-half, half)
            for a in range(0, 360, 72):
                d.ellipse([xx + 5 * math.cos(math.radians(a)) - 3, Y(yy) + 5 * math.sin(math.radians(a)) - 3,
                           xx + 5 * math.cos(math.radians(a)) + 3, Y(yy) + 5 * math.sin(math.radians(a)) + 3],
                          fill=tuple(s["wzor_kolor"]) + (210,))
    if s["kobieta"] and s["stroj"] != "plaszcz":
        for x in range(92, 228, 24):  # fałdy spódnicy
            d.line([(150 + (x - 150) * 0.66, Y(346)), (x, Y(560))], fill=_shade(s["dol"], 0.74) + (150,), width=2)
    if s["stroj"] in ("garnitur", "plaszcz", "mundur") and not s["kobieta"]:
        for yy in (316, 360, 404):
            d.ellipse([146, yy, 154, yy + 8], fill=_shade(s["gora"], 0.55) + (230,))
    if s["szer"] != 1.0:
        im = im.resize((round(w * s["szer"]), h), Image.LANCZOS)
    return im


def _ramie_img(s):
    w, h = RAMIE_W, RAMIE_H
    st = s["stroj"]
    rek = s["rekaw"] or (s["koszula"] if st in ("koszula", "kamizelka", "ogrodniczki") else s["gora"])
    if s["kobieta"] and st == "sukienka":
        parts = [(ell(55, 26, 25, 23), rek), (poly([(32, 22), (78, 22), (80, 120), (30, 120)]), rek, dict(edge=2, shade=0.2)),
                 (poly([(36, 112), (74, 112), (68, 214), (42, 214)]), s["skora"], dict(kind="gladki", contrast=0.6))]
    else:
        parts = [(ell(55, 26, 25, 23), rek), (poly([(32, 22), (78, 22), (74, 210), (36, 210)]), rek, dict(edge=2, shade=0.2))]
        if st == "pasiak":
            pass
        parts.append((poly([(38, 196), (72, 196), (74, 212), (36, 212)]), _shade(rek, 0.8) if st != "garnitur" else s["koszula"]))
    parts.append((ell(56, 230, 15, 19), s["skora"], dict(kind="gladki", contrast=0.6)))
    im = stack(w, h, parts, seed=31 + len(str(rek)))
    if st == "pasiak":
        d = ImageDraw.Draw(im)
        for yy in range(40, 200, 26):
            d.line([(30, yy), (80, yy)], fill=(36, 34, 34, 220), width=9)
        im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")),
                                               np.asarray(stack(w, h, parts[:2], seed=31).getchannel("A")) | 0).astype(np.uint8))
                    if False else im.getchannel("A"))
    if s["szer"] != 1.0:
        im = im.resize((round(w * s["szer"]), h), Image.LANCZOS)
    return im


class Figura:
    """Lalka: korpus i dwie ręce + liczby potrzebne do złożenia (bark, dłoń, stopa)."""

    def __init__(self, key):
        s = spec(key)
        self.key, self.s = key, s
        body = _korpus_img(s)
        arm = _ramie_img(s)
        self.body = Sprite(body, f"lalka-{key}", rim=2, clean=False, crop=False)
        self.arm = Sprite(arm, f"reka-{key}", rim=2, clean=False, crop=False)
        self.cw, self.ch = body.size
        self.stopa = STOPA + s["nogi"]
        self.wys = self.stopa - CZUBEK
        k = s["szer"]
        self.bark = {n: (FIG_W * k / 2 + (x - FIG_W / 2) * k, y) for n, (x, y) in BARK.items()}
        self.aw, self.ah = arm.size
        self.zawias = (RAMIE_ZAWIAS[0] * k + (self.aw - RAMIE_W * k) / 2, RAMIE_ZAWIAS[1])
        self.dlon = DLON[1] - RAMIE_ZAWIAS[1]


@lru_cache(None)
def figura(key):
    return Figura(key)


# ---------- rama teatru oklejona gazetami ----------

NAGLOWKI = ["BARROW GANG ESCAPES", "OUTLAW GIRL WITH CIGAR", "BANK ROBBED", "POLICE HUNT COUPLE", "EXTRA!", "REWARD $1000",
            "FIVE STATES SEARCH", "GUN MOLL", "BONNIE AND CLYDE SEEN", "FUGITIVES IN FORD", "WANTED", "DEPRESSION DEEPENS"]
TYTULY_GAZET = ["THE DALLAS DISPATCH", "JOPLIN GLOBE", "TEXAS HERALD", "DAILY STAR", "THE EVENING NEWS", "TULSA TRIBUNE"]


def _gazeta_img(w, h, naglowek, tytul, seed=0, zdjecie=True, kolor=GAZETA):
    """Strona gazety: papier gazetowy, winieta, nagłówek, zdjęcie (szara plama z sylwetkami), szpalty kresek."""
    r = random.Random(seed)
    parts = [(poly([(0, 0), (w, 0), (w, h), (0, h)]), kolor, dict(kind="gladki", edge=3, contrast=1.1, rough=1.0))]
    im = stack(w, h, parts, seed=seed)
    d = ImageDraw.Draw(im)
    from PIL import ImageFont
    f1 = ImageFont.truetype(FONT_PL, max(10, int(h * 0.06)), index=PL_IDX)
    f2 = ImageFont.truetype(FONT_PL, max(12, int(h * 0.10)), index=PL_IDX)
    d.text((w / 2, h * 0.07), tytul, font=f1, fill=FARBA + (240,), anchor="mm")
    d.line([(w * 0.05, h * 0.12), (w * 0.95, h * 0.12)], fill=FARBA + (220,), width=max(1, int(h * 0.006)))
    # nagłówek w jednym albo dwóch rzędach
    slowa, rzedy, rz = naglowek.split(), [], ""
    for s_ in slowa:
        if f2.getlength((rz + " " + s_).strip()) > w * 0.9 and rz:
            rzedy.append(rz)
            rz = s_
        else:
            rz = (rz + " " + s_).strip()
    rzedy.append(rz)
    y = h * 0.2
    for rz in rzedy[:2]:
        d.text((w / 2, y), rz, font=f2, fill=FARBA + (250,), anchor="mm")
        y += h * 0.11
    top = y - h * 0.02
    if zdjecie:
        x0, x1 = w * 0.08, w * 0.56
        y0, y1 = top, top + h * 0.36
        d.rectangle([x0, y0, x1, y1], fill=(120, 116, 110, 255))
        d.ellipse([x0 + (x1 - x0) * 0.32, y0 + (y1 - y0) * 0.16, x0 + (x1 - x0) * 0.46, y0 + (y1 - y0) * 0.4], fill=(70, 66, 62, 255))
        d.polygon([(x0 + (x1 - x0) * 0.26, y1), (x0 + (x1 - x0) * 0.3, y0 + (y1 - y0) * 0.42),
                   (x0 + (x1 - x0) * 0.48, y0 + (y1 - y0) * 0.42), (x0 + (x1 - x0) * 0.52, y1)], fill=(60, 56, 52, 255))
        d.rectangle([x0 + (x1 - x0) * 0.58, y0 + (y1 - y0) * 0.55, x0 + (x1 - x0) * 0.95, y1], fill=(84, 80, 76, 255))
        for k in range(int((y1 - top) / max(4, h * 0.03))):
            yy = top + k * h * 0.03 + 2
            d.line([(w * 0.6, yy), (w * (0.92 - 0.1 * r.random()), yy)], fill=(110, 104, 96, 200), width=max(1, int(h * 0.008)))
        top = y1 + h * 0.03
    while top < h * 0.94:
        for col in range(3):
            xa = w * (0.06 + col * 0.31)
            d.line([(xa, top), (xa + w * (0.26 - 0.06 * r.random()), top)], fill=(110, 104, 96, 200), width=max(1, int(h * 0.008)))
        top += h * 0.03
    return im


@lru_cache(None)
def gazeta(naglowek="EXTRA!", seed=0, w=360, h=480, zdjecie=True, tytul=None):
    tytul = tytul or TYTULY_GAZET[seed % len(TYTULY_GAZET)]
    return Sprite(_gazeta_img(w, h, naglowek, tytul, seed, zdjecie), f"gazeta-{naglowek}-{seed}", rim=2, clean=False)


@lru_cache(None)
def theatre():
    """Rama teatru (plan 1,0): ciemna widownia, rama oklejona pierwszymi stronami gazet z lat 30., u góry szyld art déco
    z tytułem. Otwór sceny to dokładnie kadr wzorcowy 0..1280 × 0..720; układ arkusza: początek w (-760, -470)."""
    ox, oy, w, h = 760, 470, 2800, 1700
    R = lambda x0, y0, x1, y1: poly([(x0 + ox, y0 + oy), (x1 + ox, y0 + oy), (x1 + ox, y1 + oy), (x0 + ox, y1 + oy)])
    dark, wood, bordo = (18, 14, 13), (60, 34, 26), (110, 30, 34)
    im = piece(w, h, poly([(0, 0), (w, 0), (w, h), (0, h)]), dark, "gladki", rough=0, contrast=0.8)
    im = glue(im, piece(w, h, R(-330, -330, 1610, 900), bordo, "gnieciony", seed=2, contrast=0.9), shadow=0.8, off=(10, 14), soft=14)
    # gazety naklejane na ramę: na słupach, na górnej belce i na podeście
    r = random.Random(7)
    miejsca = ([(x, y) for x in (-250, -110) for y in range(-240, 820, 170)] + [(x, y) for x in (1390, 1530) for y in range(-240, 820, 170)]
               + [(x, -250) for x in range(-40, 1330, 150)] + [(x, -120) for x in range(20, 1300, 210)])
    for n, (x, y) in enumerate(miejsca):
        gw, gh = 180, 240
        g = _gazeta_img(gw, gh, NAGLOWKI[n % len(NAGLOWKI)], TYTULY_GAZET[n % len(TYTULY_GAZET)], seed=n, zdjecie=n % 3 != 1)
        g = g.rotate(r.uniform(-7, 7), resample=Image.BICUBIC, expand=True)
        warstwa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        warstwa.alpha_composite(g, (int(x + ox - g.width / 2), int(y + oy - g.height / 2)))
        im = glue(im, warstwa, shadow=0.5, off=(4, 6), soft=4)
    # złota listwa wokół otworu i stopnie art déco nad nim
    for shape in (R(-28, -28, 1308, -12), R(-28, 732, 1308, 748), R(-28, -28, -12, 748), R(1292, -28, 1308, 748)):
        im = glue(im, piece(w, h, shape, GOLD, "gnieciony", seed=40, contrast=0.9), shadow=0.5)
    # szyld z tytułem: czarna tablica ze złotymi stopniami i promieniami
    stopnie = [(260, -150, 1020, -40), (330, -190, 950, -150), (420, -224, 860, -190)]
    for i, (x0, y0, x1, y1) in enumerate(stopnie):
        im = glue(im, piece(w, h, R(x0, y0, x1, y1), (24, 22, 24), "gladki", seed=50 + i, contrast=1.3), shadow=0.8, off=(6, 8), soft=8)
        for shape in (R(x0, y0, x1, y0 + 6), R(x0, y1 - 6, x1, y1)):
            im = glue(im, piece(w, h, shape, GOLD, "gnieciony", seed=55 + i, contrast=0.9), shadow=0.3)
    for k in range(9):
        a = math.radians(200 + k * 17.5)
        cx, cy = 640 + ox, -205 + oy
        pts = [(cx + 30 * math.cos(a - 0.05), cy + 30 * math.sin(a - 0.05)), (cx + 95 * math.cos(a), cy + 95 * math.sin(a)),
               (cx + 30 * math.cos(a + 0.05), cy + 30 * math.sin(a + 0.05))]
        im = glue(im, piece(w, h, poly(pts), GOLD, "gnieciony", seed=60 + k), shadow=0.3)
    title = glyphs("THE OUTLAWS MADE OF PAPER", 52, FONT_PL, PL_IDX, (640 + ox, -100 + oy), "mm")
    im = glue(im, piece(w, h, title, (236, 198, 110), "gladki", rough=0.6, contrast=1.2), shadow=0.7, off=(2, 3), soft=1.5)
    sub = glyphs("BONNIE AND CLYDE", 24, FONT_PL, PL_IDX, (640 + ox, -170 + oy), "mm", spacing=6)
    im = glue(im, piece(w, h, sub, (214, 176, 100), "gladki", rough=0.5, contrast=1.2), shadow=0.6, off=(1, 2), soft=1)
    # rampa ze światłami u dołu
    im = glue(im, piece(w, h, R(-200, 760, 1480, 820), wood, "gnieciony", seed=70, contrast=0.9), shadow=0.6)
    for x in range(-120, 1420, 110):
        im = glue(im, piece(w, h, ell(x + ox, 770 + oy, 16, 9), (250, 226, 160), "gladki", seed=71), shadow=0.3)
    a = np.asarray(im.getchannel("A")).copy()
    a[oy:oy + H, ox:ox + W] = 0  # otwór sceny
    im.putalpha(Image.fromarray(a))
    return Sprite(im, "teatr-gazety", rim=0, clean=False, pad=0)


def theatre_put(st, light=1.0):
    spr = theatre()
    st.put(spr, -760, -470, P.rama, w=2800, anchor=(0.0, 0.0), shadow=(0, 10, 18, 0.55), blur=0, tint=(light, light, light))
