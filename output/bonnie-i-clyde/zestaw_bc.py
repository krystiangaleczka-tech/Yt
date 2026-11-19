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
                        gora=(236, 226, 206), dol=(236, 226, 206), kolnierzyk=(250, 248, 240), pas=(200, 170, 120), szer=0.94),
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
    "dziecko1": dict(fryzura="krotkie", wlosy=(90, 60, 40), stroj="ogrodniczki", gora=(140, 90, 70), dol=(86, 104, 140),
                     koszula=(220, 200, 160), szer=0.9),
    "dziecko2": dict(kobieta=True, wlosy=(60, 40, 30), fryzura="fala", stroj="sukienka", gora=(150, 180, 120), dol=(150, 180, 120),
                     kolnierzyk=(250, 246, 236), szer=0.9),
    "dziecko3": dict(fryzura="krotkie", wlosy=(170, 120, 70), stroj="koszula", gora=(200, 210, 230), dol=(110, 96, 80),
                     koszula=(200, 210, 230), szer=0.9),
    "nauczycielka": dict(kobieta=True, wlosy=(110, 90, 70), fryzura="kok", stroj="sukienka", gora=(70, 80, 100), dol=(70, 80, 100),
                         kolnierzyk=(240, 236, 226), okulary=True),
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
        parts += [(ell(153, 84, 46, 14), (250, 250, 246)), (ell(118, 92, 12, 10), (240, 200, 210)), (ell(186, 90, 12, 10), (240, 200, 210))]
    elif k == "papierowa":
        parts += [(poly([(108, 98), (198, 98), (153, 52)]), c, dict(edge=2))]


def _korpus_img(s):
    L = s["nogi"]
    w, h = FIG_W, FIG_H + L
    Y = lambda y: y + L if y >= BIODRO else y
    PL = lambda pts: poly([(x, Y(y)) for x, y in pts])
    parts = []
    if s["kapelusz"] == "welon":  # welon za głową, do łopatek (nie zakrywa sukienki)
        parts.append((poly([(104, 96), (100, 260), (86, 330), (120, 300), (126, 140)]), (246, 246, 240), dict(kind="gladki", contrast=0.5)))
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
        self._siedzi = None

    @property
    def siedzi(self):
        """Korpus bez nóg (ucięty tuż pod biodrami): pasażer w aucie, lalka za stołem — nogi nie wystają spod karoserii."""
        if self._siedzi is None:
            im = _korpus_img(self.s).copy()
            a = im.getchannel("A")
            a.paste(0, (0, BIODRO + 40, im.size[0], im.size[1]))
            im.putalpha(a)
            self._siedzi = Sprite(im, f"lalka-siedzi-{self.key}", rim=2, clean=False, crop=False)
        return self._siedzi


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


# ---------- preria i drogi (Teksas, Oklahoma, Kansas lat 30.) ----------

from zestaw import _sheet  # noqa: E402


@lru_cache(None)
def niebo_sp(noc=False):
    """Papier nieba prerii: wysoki, jasny przy horyzoncie (w nocy granatowy)."""
    w, h = 2080, 1280
    lum = texture("gladki", w, h, 13)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    if noc:
        top, mid = np.array([40, 46, 78], np.float32), np.array([86, 92, 120], np.float32)
    else:
        top, mid = np.array([150, 186, 210], np.float32), np.array([246, 232, 196], np.float32)
    k = np.clip(1 - np.abs(yy - 0.56) / 0.56, 0, 1) ** 1.3
    rgb = (top + (mid - top) * k)[:, None, :].reshape(h, 1, 3) / 255.0 * lum[..., None]
    out = np.dstack([np.clip(rgb, 0, 1), np.ones((h, w), np.float32)])
    return Sprite(Image.fromarray((out * 255).astype(np.uint8), "RGBA"), "niebo-prerii" + ("-noc" if noc else ""), rim=0, clean=False,
                  pad=0)


PRERIA = {  # pasmo: (wysokość arkusza, linia grzbietu, falowanie, barwa)
    "dal": (300, 70, 10, (190, 170, 120)), "mesa": (360, 120, 6, (176, 132, 104)), "trawa1": (320, 60, 14, (210, 178, 104)),
    "trawa2": (320, 52, 16, (196, 160, 86)), "trawa3": (340, 50, 18, (180, 146, 76)), "zielen": (320, 56, 16, (122, 140, 84)),
    "zielen2": (330, 50, 18, (98, 122, 70)), "bloto": (300, 40, 10, (120, 98, 76)), "pole": (300, 40, 8, (150, 126, 90)),
}


@lru_cache(None)
def pasmo(which, seed=0):
    h, base, amp, col = PRERIA[which]
    im = _sheet(2000, h, 600 + seed + len(which) * 7, base, amp, col, edge=4)
    if which.startswith("trawa") or which.startswith("zielen"):
        d = ImageDraw.Draw(im)
        r = random.Random(seed + 3)
        for _ in range(420):  # kępki trawy: krótkie pociągnięcia
            x = r.uniform(0, 2000)
            y = r.uniform(base + 10, h - 6)
            c = _shade(col, r.uniform(0.7, 1.15))
            d.line([(x, y), (x + r.uniform(-5, 5), y - r.uniform(8, 18))], fill=c + (170,), width=2)
    if which == "mesa":  # stoliwa: płaskie szczyty na horyzoncie
        im = _mesy(seed)
    return Sprite(im, f"pasmo-{which}-{seed}", rim=2, clean=False, pad=0)


def _mesy(seed):
    w, h = 2000, 360
    r = random.Random(seed + 41)
    pts, x = [(0, 300)], 0
    while x < w:
        dl = r.uniform(120, 300)
        top = r.uniform(120, 220)
        pts += [(x + 20, 300), (x + 50, top), (x + dl - 50, top + r.uniform(-6, 6)), (x + dl - 20, 300)]
        x += dl + r.uniform(40, 160)
    pts += [(w, 300), (w, h), (0, h)]
    m = rough_mask(lambda d, s: d.polygon([(a * s, b * s) for a, b in pts], fill=255), w, h, rough=2.2, seed=seed)
    return paper(m, (186, 140, 112), "gnieciony", seed, edge=4, shade=0.2)


@lru_cache(None)
def droga(v=0, kolor=(186, 158, 116)):
    """Polna droga biegnąca w poprzek sceny: pas ziemi z koleinami (auta jadą lewo–prawo)."""
    w, h = 2200, 120
    parts = [(poly([(0, 10), (w, 4), (w, h - 4), (0, h)]), kolor, dict(edge=3, shade=0.2))]
    im = stack(w, h, parts, seed=80 + v)
    d = ImageDraw.Draw(im)
    for yy, c in ((40, 0.78), (82, 0.74)):
        pts = [(x, yy + 3 * math.sin(x / 90.0 + v)) for x in range(0, w + 20, 20)]
        d.line(pts, fill=_shade(kolor, c) + (200,), width=6)
    r = random.Random(v)
    for _ in range(140):
        x, y = r.uniform(0, w), r.uniform(14, h - 10)
        d.ellipse([x - 2, y - 1.5, x + 2, y + 1.5], fill=_shade(kolor, 0.7) + (160,))
    return Sprite(im, f"droga-{v}", rim=2, clean=False, pad=0)


@lru_cache(None)
def slup():
    """Słup telegraficzny z poprzeczką i izolatorami."""
    w, h = 120, 600
    parts = [(rect(52, 20, 68, 600), (92, 68, 50)), (rect(10, 40, 110, 54), (92, 68, 50)), (rect(22, 84, 98, 96), (92, 68, 50))]
    for x in (18, 46, 74, 102):
        parts.append((ell(x, 36, 5, 7), (120, 150, 140)))
    return Sprite(stack(w, h, parts, seed=91), "slup", rim=2, clean=False)


@lru_cache(None)
def wiatrak(czesc="wieza"):
    """Wiatrak z prerii: kratownica (wieza) i koło z łopatkami (kolo, obraca się)."""
    if czesc == "wieza":
        w, h = 260, 620
        parts = [(_band((70, 600), (118, 40), 10), (110, 104, 100)), (_band((190, 600), (142, 40), 10), (110, 104, 100))]
        for k in range(1, 7):
            y = 600 - k * 88
            parts.append((_band((70 + 48 * k / 7, y), (190 - 48 * k / 7, y - 60), 6), (120, 114, 110)))
            parts.append((_band((190 - 48 * k / 7, y), (70 + 48 * k / 7, y - 60), 6), (120, 114, 110)))
        parts += [(rect(110, 20, 150, 50), (90, 84, 80)), (poly([(150, 26), (240, 18), (240, 46), (150, 40)]), (150, 50, 44))]
        return Sprite(stack(w, h, parts, seed=92), "wiatrak-wieza", rim=2, clean=False)
    w = h = 300
    parts = [(ell(150, 150, 20, 20), (90, 84, 80))]
    for k in range(16):
        a = math.radians(k * 22.5)
        parts.append((poly([(150 + 26 * math.cos(a - 0.06), 150 + 26 * math.sin(a - 0.06)),
                            (150 + 146 * math.cos(a - 0.1), 150 + 146 * math.sin(a - 0.1)),
                            (150 + 146 * math.cos(a + 0.1), 150 + 146 * math.sin(a + 0.1)),
                            (150 + 26 * math.cos(a + 0.06), 150 + 26 * math.sin(a + 0.06))]), (196, 192, 184)))
    return Sprite(stack(w, h, parts, seed=93), "wiatrak-kolo", rim=2, clean=False)


@lru_cache(None)
def plot(v=0, drut=True):
    """Płot z drewnianych słupków i drutu kolczastego."""
    w, h = 1400, 160
    parts = []
    for x in range(20, w, 140):
        parts.append((poly([(x - 7, 150), (x + 7, 150), (x + 6, 20), (x - 6, 26)]), (110, 86, 62)))
    im = stack(w, h, parts, seed=94 + v)
    if drut:
        d = ImageDraw.Draw(im)
        for yy in (44, 82, 120):
            d.line([(0, yy), (w, yy + 4)], fill=(70, 66, 62, 230), width=2)
            for x in range(10, w, 36):
                d.line([(x - 4, yy - 4), (x + 4, yy + 6)], fill=(70, 66, 62, 230), width=2)
    return Sprite(im, f"plot-{v}", rim=2, clean=False)


@lru_cache(None)
def tablica(txt, kolor=(236, 226, 196), farba=(40, 34, 30), w=None, h=110, slupek=True):
    """Tablica przy drodze na słupku (DETOUR, STATE LINE, WELLINGTON 2 MI)."""
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_PL, 64, index=PL_IDX)
    tw = int(f.getlength(txt) / 2) + 50
    w = w or tw
    H_ = h + (260 if slupek else 0)
    parts = []
    if slupek:
        parts.append((rect(w / 2 - 10, h - 10, w / 2 + 10, H_), (100, 78, 56)))
    parts += [(rect(4, 4, w - 4, h - 4), kolor, dict(kind="gladki", edge=3, contrast=1.2)),
              (glyphs(txt, 32, FONT_PL, PL_IDX, (w / 2, h / 2 + 2), "mm"), farba, dict(kind="gladki", rough=0.5))]
    return Sprite(stack(int(w), int(H_), parts, seed=len(txt)), f"tablica-{txt}", rim=2, clean=False)


# ---------- miasteczko: fasady z szyldami ----------

FASADY = {  # rodzaj: (szerokość, wysokość, ściana, szyld, napis, markiza)
    "stacja": (520, 380, (226, 220, 200), (180, 40, 36), "GAS · OIL", None),
    "sklep": (460, 420, (176, 92, 70), (40, 50, 70), "HARDWARE", (90, 120, 80)),
    "kawiarnia": (440, 400, (220, 196, 150), (120, 40, 34), "CAFE", (180, 60, 50)),
    "bank": (480, 460, (196, 186, 170), (40, 40, 44), "BANK", None),
    "kiosk": (300, 330, (110, 80, 56), (200, 170, 90), "NEWS", (40, 80, 60)),
    "garaz": (560, 520, (190, 120, 90), (60, 50, 44), "GARAGE", None),
    "drukarnia": (520, 480, (150, 90, 70), (30, 30, 34), "JOPLIN GLOBE", None),
    "motel": (420, 320, (236, 226, 204), (40, 90, 120), "MOTEL", None),
    "areszt": (480, 440, (170, 160, 150), (50, 50, 54), "COUNTY JAIL", None),
    "zaklad": (460, 420, (220, 214, 200), (30, 30, 32), "FUNERAL HOME", None),
    "meble": (460, 420, (180, 150, 110), (80, 50, 34), "FURNITURE", (130, 60, 50)),
    "apteka": (420, 420, (200, 210, 196), (40, 70, 60), "DRUGS · SODA", (60, 100, 90)),
    "dom": (420, 380, (210, 200, 180), None, "", None),
    "dworzec": (620, 440, (176, 150, 120), (40, 60, 50), "MIDDLETOWN · OHIO", (110, 70, 50)),
    "szkola": (560, 440, (190, 110, 90), (60, 60, 60), "CEMENT CITY SCHOOL", None),
    "wiezienie": (900, 480, (186, 170, 150), (50, 50, 54), "STATE PENITENTIARY · HUNTSVILLE", None),
}


def _okno_parts(x0, y0, x1, y1, rama=(236, 232, 220), szyba=(110, 140, 156), szczeble=True):
    parts = [(rect(x0, y0, x1, y1), rama), (rect(x0 + 8, y0 + 8, x1 - 8, y1 - 8), szyba, dict(kind="gladki", contrast=0.5))]
    if szczeble:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        parts += [(rect(mx - 3, y0 + 8, mx + 3, y1 - 8), rama), (rect(x0 + 8, my - 3, x1 - 8, my + 3), rama)]
    return parts


@lru_cache(None)
def fasada(rodzaj, v=0, swiatlo=False):
    """Fasada budynku z miasteczka z lat 30.: ściana, gzyms, okna, drzwi, szyld z napisem, markiza w pasy."""
    w, h, sc, szyld, napis, mark = FASADY[rodzaj]
    r = random.Random(v * 7 + len(rodzaj))
    szyba = (250, 220, 150) if swiatlo else (110, 140, 156)
    parts = [(rect(6, 60, w - 6, h), sc, dict(edge=3, shade=0.15)),
             (rect(0, 40, w, 74), _shade(sc, 0.75)),  # gzyms
             (rect(20, 20, w - 20, 46), _shade(sc, 0.85))]
    if rodzaj == "dom":
        parts = [(rect(20, 150, w - 20, h), sc, dict(edge=3, shade=0.15)),
                 (poly([(0, 160), (w / 2, 30), (w, 160)]), (110, 70, 56), dict(edge=2)),
                 (rect(w / 2 - 40, 250, w / 2 + 40, h), (120, 84, 60))]
        parts += _okno_parts(50, 210, 140, 300, szyba=szyba) + _okno_parts(w - 140, 210, w - 50, 300, szyba=szyba)
        parts.append((rect(0, h - 16, w, h), (110, 92, 70)))
    elif rodzaj == "stacja":
        parts += [(rect(40, 150, 300, h), (240, 236, 222), dict(edge=2)), (rect(300, 190, w - 20, h), (210, 204, 186))]
        parts += _okno_parts(70, 190, 190, 290, szyba=szyba)
        parts += [(rect(210, 220, 280, h), (130, 90, 60))]
        for x in (360, 440):  # dystrybutory
            parts += [(rect(x - 22, 250, x + 22, h - 10), (200, 40, 36)), (ell(x, 240, 20, 20), (250, 240, 220))]
    else:
        parts += _okno_parts(40, 170, w / 2 - 50, 320, szyba=szyba) + _okno_parts(w / 2 + 50, 170, w - 40, 320, szyba=szyba)
        parts += [(rect(w / 2 - 36, 200, w / 2 + 36, h), (110, 76, 52)), (rect(w / 2 - 28, 214, w / 2 + 28, 290), szyba)]
        if rodzaj == "garaz":
            parts += [(rect(40, 340, w - 40, h), (120, 100, 80)), (rect(50, 350, w - 50, h), (96, 80, 66))]
            for x in range(70, w - 50, 60):
                parts.append((rect(x, 350, x + 4, h), (80, 66, 54)))
            parts += [(rect(w - 70, 120, w - 50, h), (90, 70, 56))]  # schody na piętro
        if rodzaj == "bank":
            for x in (30, w - 60):
                parts.append((rect(x, 80, x + 30, h), (220, 214, 204)))
        if rodzaj == "areszt":
            for x in range(60, w - 40, 26):
                parts.append((rect(x, 170, x + 5, 320), (50, 50, 54)))
    if mark:
        for k in range(0, w - 40, 40):
            parts.append((poly([(20 + k, 150), (60 + k, 150), (64 + k, 196), (24 + k, 196)]), mark if (k // 40) % 2 == 0 else (240, 232, 214)))
    im = stack(w, h, parts, seed=100 + v + len(rodzaj))
    if szyld and napis:
        from PIL import ImageFont
        f = ImageFont.truetype(FONT_PL, 40, index=PL_IDX)
        tw = min(w - 40, int(f.getlength(napis)) + 40)
        sz = stack(tw, 64, [(rect(2, 2, tw - 2, 62), szyld, dict(edge=2)),
                            (glyphs(napis, 34, FONT_PL, PL_IDX, (tw / 2, 33), "mm"), (240, 226, 190), dict(kind="gladki", rough=0.5))],
                   seed=110 + v)
        im = glue(im, Image.new("RGBA", im.size, (0, 0, 0, 0)).__class__.paste(im, im, (0, 0)) if False else im, shadow=0)
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        lay.alpha_composite(sz, (int(w / 2 - tw / 2), 82 if rodzaj != "stacja" else 90))
        im = glue(im, lay, shadow=0.5)
    return Sprite(im, f"fasada-{rodzaj}-{v}-{swiatlo}", rim=2, clean=False)


@lru_cache(None)
def chodnik():
    w, h = 2200, 90
    parts = [(rect(0, 0, w, 24), (170, 164, 152)), (rect(0, 24, w, h), (140, 128, 112))]
    im = stack(w, h, parts, seed=121)
    d = ImageDraw.Draw(im)
    for x in range(0, w, 110):
        d.line([(x, 0), (x, 24)], fill=(120, 114, 104, 200), width=2)
    return Sprite(im, "chodnik", rim=1, clean=False, pad=0)


@lru_cache(None)
def latarnia():
    w, h = 120, 560
    parts = [(rect(54, 60, 66, 560), (40, 40, 44)), (rect(40, 540, 80, 560), (40, 40, 44)), (poly([(30, 70), (90, 70), (76, 20), (44, 20)]), (40, 40, 44)),
             (rect(44, 30, 76, 66), (250, 230, 170))]
    return Sprite(stack(w, h, parts, seed=122), "latarnia", rim=2, clean=False)


# ---------- wnętrza ----------

TAPETY = {"kwiaty": ((206, 186, 150), (170, 110, 90)), "paski": ((196, 200, 170), (160, 170, 136)), "deski": ((150, 116, 82), (124, 94, 66)),
          "cegla": ((150, 86, 64), (120, 66, 50)), "tynk": ((200, 196, 184), (180, 176, 164)), "czerwien": ((90, 30, 30), (60, 20, 20)),
          "zielen": ((120, 140, 110), (96, 116, 90))}


@lru_cache(None)
def sciana(wzor="kwiaty", v=0):
    """Ściana wnętrza (2200 × 820) z tapetą albo deskami, listwą u dołu."""
    w, h = 2200, 820
    base, akc = TAPETY[wzor]
    im = stack(w, h, [(rect(0, 0, w, h), base, dict(edge=0, shade=0.12, contrast=0.8))], seed=130 + v)
    d = ImageDraw.Draw(im)
    r = random.Random(v)
    if wzor in ("paski",):
        for x in range(0, w, 60):
            d.rectangle([x, 0, x + 18, h], fill=akc + (120,))
    elif wzor == "kwiaty":
        for y in range(30, h, 90):
            for x in range((y // 90) % 2 * 45, w, 90):
                for a in range(0, 360, 72):
                    cx, cy = x + 8 * math.cos(math.radians(a)), y + 8 * math.sin(math.radians(a))
                    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=akc + (130,))
    elif wzor in ("deski",):
        for x in range(0, w, 70):
            d.line([(x, 0), (x, h)], fill=akc + (200,), width=4)
    elif wzor == "cegla":
        for y in range(0, h, 40):
            for x in range((y // 40) % 2 * 45, w, 90):
                d.rectangle([x, y, x + 84, y + 34], outline=akc + (200,), width=3)
    d.rectangle([0, h - 60, w, h], fill=_shade(base, 0.6) + (255,))
    return Sprite(im, f"sciana-{wzor}-{v}", rim=0, clean=False, pad=0)


@lru_cache(None)
def podloga(kolor=(130, 96, 66)):
    w, h = 2200, 200
    im = stack(w, h, [(rect(0, 0, w, h), kolor, dict(shade=0.25))], seed=140)
    d = ImageDraw.Draw(im)
    for y in range(0, h, 26):
        d.line([(0, y), (w, y)], fill=_shade(kolor, 0.75) + (200,), width=2)
    return Sprite(im, f"podloga-{kolor}", rim=0, clean=False, pad=0)


@lru_cache(None)
def okno(noc=False, kolor_ramy=(236, 230, 214)):
    w, h = 260, 320
    szyba = (40, 50, 80) if noc else (170, 200, 214)
    parts = _okno_parts(0, 0, w, h, rama=kolor_ramy, szyba=szyba)
    parts.append((rect(-10, h - 10, w + 10, h + 4), _shade(kolor_ramy, 0.8)))
    return Sprite(stack(w, h + 6, parts, seed=150 + noc), f"okno-{noc}", rim=2, clean=False)


@lru_cache(None)
def drzwi(kolor=(110, 76, 52), szyba=True):
    w, h = 200, 420
    parts = [(rect(0, 0, w, h), _shade(kolor, 0.8)), (rect(12, 12, w - 12, h), kolor, dict(edge=2))]
    if szyba:
        parts.append((rect(40, 40, w - 40, 170), (170, 196, 206), dict(kind="gladki", contrast=0.5)))
    parts.append((ell(w - 34, 230, 9, 9), GOLD))
    return Sprite(stack(w, h, parts, seed=151), f"drzwi-{kolor}-{szyba}", rim=2, clean=False)


MEBLE = {
    "stol": (360, 200, [(rect(0, 0, 360, 22), (140, 100, 70)), (rect(20, 22, 40, 200), (120, 86, 60)), (rect(320, 22, 340, 200), (120, 86, 60))]),
    "stol_obrus": (360, 200, [(poly([(0, 0), (360, 0), (370, 90), (-10, 90)]), (236, 226, 206)), (rect(20, 22, 40, 200), (120, 86, 60)),
                              (rect(320, 22, 340, 200), (120, 86, 60))]),
    "krzeslo": (120, 260, [(rect(10, 0, 26, 260), (120, 86, 60)), (rect(10, 130, 110, 148), (130, 94, 66)), (rect(96, 140, 110, 260), (120, 86, 60)),
                           (rect(10, 20, 26, 140), (120, 86, 60))]),
    "kuchenka": (260, 300, [(rect(0, 60, 260, 300), (60, 58, 60)), (rect(0, 40, 260, 70), (80, 78, 80)), (rect(180, 0, 210, 50), (60, 58, 60)),
                            (ell(70, 54, 30, 8), (40, 38, 40)), (ell(150, 54, 30, 8), (40, 38, 40))]),
    "biurko": (460, 230, [(rect(0, 0, 460, 30), (110, 76, 52)), (rect(10, 30, 150, 230), (96, 66, 46)), (rect(310, 30, 450, 230), (96, 66, 46)),
                          (rect(30, 60, 130, 90), (120, 84, 58)), (rect(330, 60, 430, 90), (120, 84, 58))]),
    "lada": (700, 220, [(rect(0, 0, 700, 30), (150, 110, 80)), (rect(10, 30, 690, 220), (120, 84, 58))]),
    "lozko": (520, 200, [(rect(0, 60, 520, 160), (236, 230, 214)), (rect(0, 0, 30, 200), (110, 76, 52)), (rect(490, 40, 520, 200), (110, 76, 52))]),
    "szafka": (220, 300, [(rect(0, 0, 220, 300), (130, 94, 66)), (rect(10, 20, 210, 140), (150, 110, 80)), (rect(10, 160, 210, 290), (150, 110, 80))]),
    "kanapa": (520, 220, [(rect(0, 60, 520, 200), (140, 60, 54)), (rect(0, 0, 520, 80), (120, 50, 46)), (rect(0, 40, 50, 210), (120, 50, 46)),
                          (rect(470, 40, 520, 210), (120, 50, 46))]),
    "fotel_bujany": (220, 300, [(rect(20, 0, 40, 220), (110, 76, 52)), (rect(20, 150, 200, 170), (120, 84, 58)), (rect(180, 120, 196, 220), (110, 76, 52)),
                                (lambda d, s: d.arc([-40 * s, 180 * s, 260 * s, 320 * s], 20, 160, fill=255, width=int(12 * s)), (100, 70, 48))]),
}


@lru_cache(None)
def mebel(key):
    w, h, parts = MEBLE[key]
    return Sprite(stack(w + 20, h + 20, [(lambda d, s, f=p[0]: f(d, s), p[1]) + ((p[2],) if len(p) > 2 else ()) for p in parts], seed=160 + len(key)),
                  f"mebel-{key}", rim=2, clean=False)


@lru_cache(None)
def listwa(w=50, h=800, kolor=(96, 70, 48)):
    """Pionowa listwa / słupek ściany działowej."""
    return Sprite(stack(w, h, [(rect(0, 0, w, h), kolor)], seed=777), f"listwa-{w}-{h}", rim=2, clean=False)


@lru_cache(None)
def kraty(w=520, h=640, krok=52):
    parts = [(rect(0, 0, w, 24), (60, 60, 64)), (rect(0, h - 24, w, h), (60, 60, 64))]
    for x in range(10, w, krok):
        parts.append((rect(x, 0, x + 14, h), (70, 70, 74), dict(kind="gladki", contrast=0.7)))
    parts.append((rect(0, h / 2 - 10, w, h / 2 + 10), (60, 60, 64)))
    return Sprite(stack(w, h, parts, seed=170), f"kraty-{w}-{h}-{krok}", rim=2, clean=False)


@lru_cache(None)
def zarowka(kolor=(255, 236, 170)):
    w, h = 80, 300
    parts = [(rect(38, 0, 42, 220), (40, 36, 34)), (rect(30, 210, 50, 236), (80, 76, 70)), (ell(40, 256, 22, 28), kolor, dict(kind="gladki"))]
    return Sprite(stack(w, h, parts, seed=171), f"zarowka-{kolor}", rim=2, clean=False)


# ---------- pojazdy: Ford V8 z 1934 roku, radiowóz, motocykl, ciężarówka, wóz konny ----------

FORDY = {"szary": (120, 126, 132), "czarny": (40, 40, 44), "piaskowy": (184, 166, 128), "granat": (52, 64, 96), "bordo": (110, 40, 44),
         "zielony": (70, 96, 80)}
KOLO_FORDA = [(232, 292), (692, 292)]  # środki kół na arkuszu Forda (900 × 360)
KOLO_R = 64


@lru_cache(None)
def ford(kolor="szary", napis=None, dziury=0, kurz=False):
    """Ford V8 z 1934 roku z boku (przodem w prawo): błotniki, maska z atrapą, kabina z oknami, stopień; koła osobno (kolo)."""
    c = FORDY.get(kolor, kolor) if isinstance(kolor, str) else kolor
    w, h = 900, 360
    dark, light = _shade(c, 0.72), _shade(c, 1.15)
    parts = [
        (poly([(70, 250), (120, 160), (250, 92), (300, 70), (560, 70), (600, 150), (800, 168), (850, 200), (858, 270), (70, 276)]), c,
         dict(edge=2, shade=0.18)),
        (poly([(60, 286), (100, 210), (232, 196), (330, 228), (330, 276)]), dark, dict(edge=2)),  # tylny błotnik
        (poly([(560, 276), (600, 214), (692, 196), (800, 214), (870, 270), (870, 290), (560, 290)]), dark, dict(edge=2)),  # przedni
        (rect(300, 272, 600, 288), (40, 38, 38)),  # stopień
        (poly([(310, 88), (420, 88), (420, 160), (300, 160)]), (150, 180, 196), dict(kind="gladki", contrast=0.5)),
        (poly([(434, 88), (548, 88), (582, 160), (434, 160)]), (150, 180, 196), dict(kind="gladki", contrast=0.5)),
        (poly([(140, 160), (250, 102), (296, 92), (292, 160)]), (150, 180, 196), dict(kind="gladki", contrast=0.5)),
        (poly([(820, 176), (856, 190), (862, 262), (826, 266)]), (196, 196, 190)),  # atrapa
        (ell(796, 180, 22, 20), (236, 232, 200)), (ell(796, 180, 14, 12), (250, 246, 220)),  # reflektor
        (rect(588, 168, 816, 176), light),  # listwa maski
        (poly([(830, 276), (890, 276), (890, 292), (830, 292)]), (196, 196, 190)),  # zderzak
        (poly([(30, 270), (90, 270), (90, 286), (30, 286)]), (196, 196, 190)),
    ]
    im = stack(w, h, parts, seed=200 + len(str(c)))
    # szyby są otworami: pasażerowie stoją za autem i widać ich przez okna; szkło kładzie się na wierzch (ford_szyby)
    dziury_okien = Image.new("L", (w, h), 0)
    dd = ImageDraw.Draw(dziury_okien)
    for pts in FORD_OKNA:
        dd.polygon(pts, fill=255)
    a_ = np.asarray(im.getchannel("A")).copy()
    a_[np.asarray(dziury_okien) > 0] = 0
    im.putalpha(Image.fromarray(a_))
    d = ImageDraw.Draw(im)
    for x in (300, 426, 590):
        d.line([(x, 80), (x, 268)], fill=_shade(c, 0.6) + (200,), width=3)  # drzwi
    d.ellipse([400, 190, 412, 198], fill=(200, 196, 180, 255))
    if napis:
        from PIL import ImageFont
        f = ImageFont.truetype(FONT_PL, 34, index=PL_IDX)
        d.text((362, 220), napis, font=f, fill=(240, 236, 226, 255), anchor="mm")
    if dziury:
        r = random.Random(dziury)
        a = np.asarray(im.getchannel("A"))
        n = 0
        while n < dziury:
            x, y = r.uniform(80, 840), r.uniform(80, 270)
            if a[int(y), int(x)] > 200:
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(26, 22, 20, 255))
                d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(220, 214, 200, 160), width=1)
                n += 1
    if kurz:
        d.rectangle([60, 240, 870, 290], fill=(190, 170, 130, 70))
    return Sprite(im, f"ford-{c}-{napis}-{dziury}-{kurz}", rim=2, clean=False, crop=False)


FORD_OKNA = [[(310, 88), (420, 88), (420, 160), (300, 160)], [(434, 88), (548, 88), (582, 160), (434, 160)],
             [(140, 160), (250, 102), (296, 92), (292, 160)]]
FORD_GLOWY = [(372, 128), (500, 126)]  # gdzie na arkuszu Forda są głowy pasażerów: tylne siedzenie, kierowca


@lru_cache(None)
def ford_szyby():
    w, h = 900, 360
    parts = [(poly(pts), (190, 214, 226), dict(kind="gladki", contrast=0.4, rough=0.4)) for pts in FORD_OKNA]
    return Sprite(stack(w, h, parts, seed=205), "ford-szyby", rim=0, clean=False, crop=False)


@lru_cache(None)
def kolo(r=KOLO_R, kolpak=(200, 196, 190)):
    w = h = 2 * r + 8
    c = w / 2
    parts = [(ell(c, c, r, r), (30, 28, 28), dict(kind="gladki", contrast=0.6)), (ell(c, c, r * 0.62, r * 0.62), (70, 68, 68)),
             (ell(c, c, r * 0.32, r * 0.32), kolpak)]
    im = stack(int(w), int(h), parts, seed=210)
    d = ImageDraw.Draw(im)
    for k in range(8):
        a = math.radians(k * 45)
        d.line([(c + r * 0.34 * math.cos(a), c + r * 0.34 * math.sin(a)), (c + r * 0.6 * math.cos(a), c + r * 0.6 * math.sin(a))],
               fill=(150, 146, 140, 230), width=3)
    return Sprite(im, f"kolo-{r}-{kolpak}", rim=1, clean=False)


@lru_cache(None)
def motocykl():
    """Motocykl policji drogowej z lat 30. z boku (przodem w prawo); koła osobno: kolo(46)."""
    w, h = 520, 300
    parts = [(_band((120, 230), (250, 150), 16), (40, 40, 44)), (_band((250, 150), (400, 230), 14), (40, 40, 44)),
             (poly([(200, 110), (330, 110), (340, 150), (190, 150)]), (60, 70, 96), dict(edge=2)),  # bak
             (poly([(120, 120), (200, 116), (196, 140), (116, 140)]), (50, 40, 34)),  # siodełko
             (_band((380, 90), (410, 236), 10), (150, 146, 140)), (rect(368, 80, 430, 92), (40, 40, 44)),
             (ell(420, 112, 16, 14), (236, 232, 200)), (poly([(220, 170), (330, 170), (320, 220), (230, 220)]), (90, 90, 96)),
             (poly([(60, 196), (180, 196), (170, 214), (70, 214)]), (60, 70, 96))]
    return Sprite(stack(w, h, parts, seed=220), "motocykl", rim=2, clean=False, crop=False)


MOTO_KOLA = [(120, 236), (404, 236)]


@lru_cache(None)
def ciezarowka():
    """Ford A pickup Ivy'ego Methvina z boku (przodem w prawo); koła osobno (kolo(52))."""
    w, h = 820, 360
    c = (90, 96, 80)
    parts = [(poly([(40, 170), (420, 170), (420, 276), (40, 276)]), (120, 100, 76), dict(edge=2)),  # skrzynia
             (poly([(420, 90), (560, 90), (590, 170), (780, 186), (800, 276), (420, 276)]), c, dict(edge=2, shade=0.18)),
             (poly([(440, 104), (548, 104), (566, 162), (440, 162)]), (150, 180, 196), dict(kind="gladki", contrast=0.5)),
             (poly([(140, 280), (200, 220), (280, 220), (330, 280)]), _shade(c, 0.7)), (poly([(580, 280), (630, 220), (710, 220), (770, 280)]), _shade(c, 0.7)),
             (ell(770, 196, 18, 16), (236, 232, 200)), (rect(780, 190, 806, 270), (180, 176, 170))]
    im = stack(w, h, parts, seed=230)
    d = ImageDraw.Draw(im)
    for x in range(60, 420, 50):
        d.line([(x, 176), (x, 270)], fill=(90, 74, 56, 200), width=3)
    return Sprite(im, "ciezarowka", rim=2, clean=False, crop=False)


CIEZ_KOLA = [(236, 286), (676, 286)]


@lru_cache(None)
def lewarek():
    w, h = 90, 140
    parts = [(rect(10, 120, 80, 140), (60, 58, 56)), (rect(38, 20, 52, 124), (80, 78, 76)), (rect(20, 10, 70, 24), (60, 58, 56)),
             (_band((52, 70), (88, 40), 6), (90, 88, 86))]
    return Sprite(stack(w, h, parts, seed=231), "lewarek", rim=2, clean=False)


@lru_cache(None)
def woz():
    """Wóz konny Barrowów w West Dallas (bez konia — stoi; śpi się pod nim)."""
    w, h = 760, 380
    parts = [(poly([(40, 120), (720, 120), (700, 230), (60, 230)]), (130, 96, 66), dict(edge=2)),
             (poly([(70, 60), (690, 60), (720, 120), (40, 120)]), (220, 206, 176), dict(edge=2, shade=0.2)),  # plandeka
             (_band((720, 200), (760, 260), 10), (110, 80, 56))]
    for cx in (170, 600):
        parts += [(ell(cx, 290, 80, 80), (100, 74, 52)), (ell(cx, 290, 60, 60), (0, 0, 0))]
    im = stack(w, h, parts, seed=240)
    a = np.asarray(im).copy()
    for cx in (170, 600):  # szprychy: dziura w kole i szprychy na wierzchu
        yy, xx = np.ogrid[:h, :w]
        m = (xx - cx) ** 2 + (yy - 290) ** 2 < 58 ** 2
        a[m] = 0
    im = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(im)
    for cx in (170, 600):
        for k in range(10):
            ang = math.radians(k * 36)
            d.line([(cx, 290), (cx + 60 * math.cos(ang), 290 + 60 * math.sin(ang))], fill=(100, 74, 52, 255), width=7)
        d.ellipse([cx - 12, 278, cx + 12, 302], fill=(80, 60, 44, 255))
    return Sprite(im, "woz", rim=2, clean=False)


# ---------- rekwizyty ----------

def _tekst(txt, size, xy, kolor=FARBA, anchor="mm"):
    return (glyphs(txt, size, FONT_PL, PL_IDX, xy, anchor), kolor, dict(kind="gladki", rough=0.4))


REKWIZYTY = {
    "aparat": (170, 130, lambda: [(rect(10, 20, 160, 124), (50, 46, 44)), (rect(30, 4, 90, 24), (60, 56, 52)),
                                  (ell(110, 72, 34, 34), (90, 88, 90)), (ell(110, 72, 20, 20), (30, 34, 44)), (rect(20, 30, 50, 46), (150, 146, 140))]),
    "cygaro": (120, 26, lambda: [(rect(4, 6, 104, 20), (110, 70, 44)), (rect(100, 6, 116, 20), (196, 190, 184)), (rect(30, 6, 44, 20), (190, 40, 40))]),
    "rewolwer": (180, 110, lambda: [(rect(70, 20, 176, 40), (60, 60, 64)), (ell(80, 46, 26, 22), (70, 70, 74)),
                                    (poly([(40, 40), (90, 40), (70, 108), (30, 104)]), (110, 76, 52)), (rect(84, 50, 100, 72), (60, 60, 64))]),
    "karabin": (520, 90, lambda: [(rect(160, 30, 516, 46), (60, 60, 64)), (poly([(10, 40), (180, 30), (200, 60), (40, 80)]), (110, 76, 52)),
                                  (rect(230, 44, 300, 70), (60, 60, 64))]),
    "siekiera": (300, 120, lambda: [(rect(10, 52, 260, 68), (150, 110, 70)), (poly([(240, 10), (296, 30), (296, 90), (240, 110), (250, 60)]),
                                                                              (150, 156, 160), dict(kind="gladki"))]),
    "rura": (300, 40, lambda: [(rect(4, 10, 296, 30), (110, 110, 116), dict(kind="gladki"))]),
    "kula": (90, 560, lambda: [(rect(40, 60, 52, 556), (150, 110, 70)), (rect(10, 40, 80, 60), (150, 110, 70)), (rect(30, 300, 62, 314), (150, 110, 70))]),
    "saksofon": (160, 360, lambda: [(_band((60, 20), (70, 260), 26), GOLD), (ell(100, 300, 50, 46), GOLD), (ell(104, 296, 30, 28), (150, 110, 40)),
                                    (rect(54, 0, 66, 30), (40, 40, 40))]),
    "karty": (180, 120, lambda: [(poly([(80, 110), (20 + 40 * k, 10), (50 + 40 * k, 14)]), (244, 240, 230)) for k in range(4)]),
    "butelka": (60, 200, lambda: [(poly([(10, 70), (50, 70), (52, 196), (8, 196)]), (90, 120, 70)), (rect(22, 10, 38, 74), (90, 120, 70)),
                                  (rect(12, 110, 48, 150), (230, 220, 190))]),
    "puszka": (90, 110, lambda: [(rect(6, 10, 84, 106), (180, 60, 50)), (rect(6, 40, 84, 80), (236, 226, 196)), (ell(45, 10, 39, 8), (180, 180, 184))]),
    "kanapka": (140, 70, lambda: [(poly([(4, 40), (136, 30), (130, 50), (8, 60)]), (220, 190, 130)), (poly([(8, 30), (132, 22), (136, 32), (6, 42)]),
                                                                                                     (120, 160, 80)),
                                  (poly([(6, 18), (130, 10), (134, 24), (4, 34)]), (226, 196, 136)), (rect(30, 30, 110, 66), (244, 240, 230))]),
    "list": (200, 260, lambda: [(rect(4, 4, 196, 256), (244, 238, 222), dict(kind="gladki", edge=2))] +
             [(rect(24, 40 + k * 22, 170 - (k % 3) * 20, 46 + k * 22), (90, 80, 90)) for k in range(8)] + [_tekst("Dear Mr. Ford", 16, (100, 22))]),
    "teczka": (360, 260, lambda: [(rect(10, 30, 350, 256), (196, 160, 100), dict(edge=2)), (rect(10, 14, 140, 40), (196, 160, 100)),
                                  (rect(30, 20, 330, 60), (236, 228, 206)), (rect(40, 6, 320, 40), (226, 218, 196)),
                                  _tekst("BARROW · PARKER", 24, (180, 150))]),
    "teczka_otwarta": (620, 300, lambda: [(rect(4, 20, 310, 296), (196, 160, 100), dict(edge=2)), (rect(310, 20, 616, 296), (186, 150, 92), dict(edge=2)),
                                          (rect(30, 40, 290, 280), GAZETA), (rect(330, 40, 590, 280), GAZETA),
                                          _tekst("BARROW", 30, (160, 70)), _tekst("PARKER", 30, (460, 70))]),
    "zabawka": (220, 110, lambda: [(poly([(10, 70), (40, 30), (150, 26), (190, 50), (210, 74), (10, 80)]), (40, 40, 44)),
                                   (ell(50, 86, 20, 20), (20, 20, 20)), (ell(170, 86, 20, 20), (20, 20, 20)), _tekst("POLICE", 18, (100, 60), (240, 236, 220))]),
    "pardon": (280, 360, lambda: [(rect(4, 4, 276, 356), (244, 236, 214), dict(kind="gladki", edge=3)), _tekst("PARDON", 40, (140, 60)),
                                  (ell(200, 290, 44, 44), (170, 40, 36))] + [(rect(30, 110 + k * 26, 250, 116 + k * 26), (90, 80, 80)) for k in range(5)]),
    "plakat": (420, 560, lambda: [(rect(4, 4, 416, 556), (240, 228, 196), dict(kind="gladki", edge=3)), _tekst("WANTED", 64, (210, 66)),
                                  (rect(36, 120, 196, 320), (130, 126, 120)), (rect(224, 120, 384, 320), (130, 126, 120)),
                                  (ell(116, 190, 40, 50), (90, 86, 82)), (ell(304, 190, 40, 50), (90, 86, 82)),
                                  _tekst("BONNIE PARKER", 22, (116, 344)), _tekst("CLYDE BARROW", 22, (304, 344)), _tekst("REWARD", 46, (210, 420)),
                                  _tekst("$ 1000", 52, (210, 490), (150, 40, 36))]),
    "kuweta": (360, 90, lambda: [(poly([(0, 10), (360, 10), (340, 86), (20, 86)]), (230, 226, 216)), (rect(20, 14, 340, 40), (170, 60, 50))]),
    "klisza": (360, 90, lambda: [(rect(0, 10, 360, 80), (40, 34, 30))] + [(rect(20 + k * 84, 22, 84 + k * 84, 68), (120, 96, 70)) for k in range(4)]),
    "banknot": (160, 72, lambda: [(rect(4, 4, 156, 68), (170, 196, 150), dict(kind="gladki", edge=2)), (ell(80, 36, 18, 22), (120, 150, 110)),
                                  _tekst("5", 24, (24, 24), (60, 90, 60))]),
    "dyplom": (220, 160, lambda: [(rect(4, 4, 216, 156), (250, 244, 226), dict(kind="gladki", edge=2)), _tekst("1st PRIZE", 26, (110, 50)),
                                  (ell(110, 110, 26, 26), (196, 60, 60))]),
    "walizka": (240, 180, lambda: [(rect(10, 40, 230, 176), (120, 80, 50), dict(edge=2)), (rect(90, 10, 150, 44), (80, 56, 36)),
                                   (rect(10, 100, 230, 110), (90, 60, 40))]),
    "dzbanek": (120, 150, lambda: [(poly([(20, 40), (90, 40), (100, 146), (14, 146)]), (210, 210, 214)), (ell(55, 40, 36, 10), (180, 180, 186)),
                                   (poly([(92, 70), (118, 52), (114, 64), (96, 84)]), (210, 210, 214))]),
    "kubek": (80, 80, lambda: [(rect(10, 10, 60, 76), (244, 240, 230)), (ell(64, 40, 12, 16), (244, 240, 230))]),
    "kajdanki": (160, 80, lambda: [(ell(40, 40, 30, 30), (150, 150, 156)), (ell(120, 40, 30, 30), (150, 150, 156)), (rect(64, 34, 96, 46), (150, 150, 156))]),
    "olowek": (220, 26, lambda: [(rect(4, 6, 190, 20), (190, 40, 36)), (poly([(190, 6), (216, 13), (190, 20)]), (230, 200, 160))]),
    "pinezka": (40, 40, lambda: [(ell(20, 20, 16, 16), (190, 40, 36))]),
    "kwiaty": (200, 260, lambda: [(rect(90, 120, 110, 256), (80, 120, 60))] + [(ell(100 + 50 * math.cos(a), 90 + 40 * math.sin(a), 30, 30), c)
                                                                               for a, c in zip((0, 1.3, 2.6, 3.9, 5.2), ((236, 236, 230), (240, 200, 210),
                                                                                                                     (236, 236, 230), (250, 220, 120), (240, 200, 210)))]),
    "trumna": (560, 160, lambda: [(poly([(0, 40), (120, 10), (560, 30), (560, 150), (120, 156), (0, 120)]), (90, 60, 44), dict(edge=2)),
                                  (rect(140, 70, 500, 84), GOLD)]),
    "ksiazka": (240, 320, lambda: [(rect(4, 4, 236, 316), (150, 40, 36), dict(edge=2)), _tekst("FUGITIVES", 30, (120, 80), (240, 220, 170)),
                                   _tekst("1934", 24, (120, 260), (240, 220, 170))]),
    "zeszyt": (220, 280, lambda: [(rect(4, 4, 216, 276), (60, 80, 110), dict(edge=2)), (rect(16, 30, 204, 90), (236, 228, 206))]),
    "pad": (160, 90, lambda: [(poly([(10, 40), (40, 10), (120, 10), (150, 40), (140, 86), (110, 70), (50, 70), (20, 86)]), (60, 60, 66))]),
    "kapelusz_fedora": (200, 90, lambda: [(poly([(40, 60), (160, 60), (150, 10), (50, 10)]), (64, 58, 54)), (ell(100, 64, 96, 14), (64, 58, 54))]),
    "parole": (280, 360, lambda: [(rect(4, 4, 276, 356), (244, 236, 214), dict(kind="gladki", edge=3)), _tekst("PAROLE", 40, (140, 60)),
                                  (ell(200, 290, 44, 44), (40, 80, 150))] + [(rect(30, 110 + k * 26, 250, 116 + k * 26), (90, 80, 80)) for k in range(5)]),
    "garnek": (160, 110, lambda: [(rect(20, 20, 140, 106), (150, 150, 156), dict(kind="gladki")), (rect(0, 30, 24, 40), (60, 60, 64)),
                                  (ell(80, 22, 62, 10), (90, 60, 40))]),
    "lyzka": (40, 160, lambda: [(rect(16, 40, 24, 156), (190, 190, 196)), (ell(20, 24, 14, 22), (190, 190, 196))]),
    "gwizdek": (80, 50, lambda: [(ell(36, 26, 22, 18), (200, 196, 180)), (rect(50, 18, 78, 30), (200, 196, 180))]),
    "papieros": (60, 14, lambda: [(rect(2, 3, 50, 11), (244, 240, 230)), (rect(48, 3, 58, 11), (230, 120, 60))]),
    "wiadro": (110, 120, lambda: [(poly([(6, 20), (104, 20), (94, 116), (16, 116)]), (150, 150, 156)), (lambda d, s: d.arc([10 * s, -20 * s, 100 * s, 50 * s], 180, 360, fill=255, width=int(5 * s)), (90, 90, 96))]),
    "tablica_szkolna": (700, 400, lambda: [(rect(0, 0, 700, 400), (110, 80, 56)), (rect(20, 20, 680, 380), (50, 70, 60)),
                                           _tekst("SPELLING BEE  1922", 40, (350, 120), (236, 236, 226)), _tekst("C-A-T", 36, (350, 240), (236, 236, 226))]),
    "podium": (300, 200, lambda: [(rect(0, 40, 300, 200), (140, 100, 70), dict(edge=2)), (rect(0, 20, 300, 50), (160, 120, 84))]),
    "czapka_policyjna": (160, 80, lambda: [(poly([(20, 10), (140, 10), (130, 56), (30, 56)]), (36, 44, 66)), (poly([(60, 52), (156, 60), (150, 74), (70, 70)]), (24, 22, 22)),
                                           (ell(80, 30, 9, 10), GOLD)]),
    "koszyk": (160, 120, lambda: [(poly([(10, 40), (150, 40), (136, 116), (24, 116)]), (180, 140, 90)), (lambda d, s: d.arc([30 * s, 0, 130 * s, 80 * s], 180, 360, fill=255, width=int(8 * s)), (150, 110, 70)),
                                  (ell(60, 40, 22, 12), (236, 226, 200)), (ell(100, 38, 20, 12), (200, 150, 90))]),
    "pranie": (180, 140, lambda: [(poly([(10, 4), (170, 4), (160, 136), (20, 136)]), (236, 226, 206), dict(kind="gladki", edge=2))]),
    "mapa_zwoj": (300, 200, lambda: [(rect(4, 4, 296, 196), (230, 216, 180), dict(edge=2))]),
}


@lru_cache(None)
def rek(key):
    w, h, fn = REKWIZYTY[key]
    return Sprite(stack(w, h, fn(), seed=300 + len(key)), f"rek-{key}", rim=2, clean=False)


# ---------- zwierzęta ----------

@lru_cache(None)
def zwierze(key, faza=0):
    if key == "indyk":
        w, h = 200, 200
        ogon = [(70 + 60 * math.cos(math.radians(a)), 90 + 60 * math.sin(math.radians(a))) for a in range(150, 300, 20)]
        parts = [(_kolka(ogon, 22), (110, 70, 44)), (ell(110, 120, 50, 40), (90, 60, 40)), (_band((140, 100), (160, 50), 16), (110, 80, 60)),
                 (ell(164, 44, 14, 14), (150, 110, 90)), (poly([(174, 40), (194, 46), (174, 50)]), (220, 180, 80)), (ell(168, 60, 6, 12), (200, 40, 40)),
                 (_band((100, 156), (96, 196), 5), (200, 160, 80)), (_band((124, 156), (128, 196), 5), (200, 160, 80))]
    elif key == "mul":
        w, h = 520, 420
        parts = [(ell(250, 200, 160, 80), (120, 100, 84), dict(edge=2)), (_band((380, 170), (460, 90), 60), (120, 100, 84)),
                 (ell(470, 80, 40, 28), (120, 100, 84)), (poly([(456, 40), (470, 0), (480, 44)]), (110, 90, 76)), (poly([(440, 46), (446, 4), (460, 50)]), (110, 90, 76)),
                 (ell(480, 70, 4, 4), (20, 20, 20))]
        for x in (150, 200, 320, 370):
            parts.append((_band((x, 250), (x + (8 if faza else 0), 410), 22), (110, 90, 76)))
        parts.append((_band((92, 190), (60, 300), 12), (90, 74, 62)))
    elif key == "piesek":
        w, h = 160, 120
        parts = [(ell(70, 70, 50, 28), (246, 244, 238)), (ell(124, 46, 24, 22), (246, 244, 238)), (ell(130, 30, 8, 12), (230, 226, 220)),
                 (ell(134, 44, 3, 3), (20, 20, 20))] + [(rect(x, 86, x + 10, 116), (240, 236, 228)) for x in (36, 56, 90, 104)]
    elif key == "ryba":
        w, h = 120, 60
        parts = [(ell(54, 30, 44, 18), (150, 160, 170)), (poly([(96, 30), (118, 10), (118, 50)]), (130, 140, 150))]
    elif key == "kon":
        w, h = 560, 440
        parts = [(ell(260, 200, 170, 80), (130, 90, 60), dict(edge=2)), (_band((390, 170), (470, 80), 56), (130, 90, 60)),
                 (ell(486, 76, 46, 28), (130, 90, 60)), (poly([(470, 40), (482, 10), (494, 44)]), (110, 76, 52))]
        for x in (150, 200, 330, 380):
            parts.append((_band((x, 250), (x, 430), 22), (120, 84, 56)))
        parts.append((_band((92, 180), (60, 310), 16), (70, 50, 36)))
    return Sprite(stack(w, h, parts, seed=400 + len(key) + faza), f"zwierze-{key}-{faza}", rim=2, clean=False)


# ---------- więzienie, wąwóz, las, rzeka ----------

@lru_cache(None)
def bawelna(v=0):
    """Rząd krzaków bawełny z białymi kłębkami."""
    w, h = 2200, 180
    r = random.Random(v + 7)
    pts = [(x, 90 + r.uniform(-18, 18)) for x in range(0, w + 40, 46)]
    parts = [(_kolka(pts, 46), (96, 110, 70), dict(edge=2)), (rect(0, 90, w, h), (110, 96, 70))]
    im = stack(w, h, parts, seed=500 + v)
    d = ImageDraw.Draw(im)
    for _ in range(260):
        x, y = r.uniform(0, w), r.uniform(46, 120)
        d.ellipse([x - 7, y - 6, x + 7, y + 6], fill=(246, 244, 238, 240))
    return Sprite(im, f"bawelna-{v}", rim=2, clean=False, pad=0)


@lru_cache(None)
def wieza():
    w, h = 300, 640
    parts = [(_band((70, 640), (110, 200), 12), (110, 90, 70)), (_band((230, 640), (190, 200), 12), (110, 90, 70)),
             (_band((80, 560), (220, 360), 8), (110, 90, 70)), (_band((220, 560), (80, 360), 8), (110, 90, 70)),
             (rect(60, 120, 240, 210), (130, 104, 80), dict(edge=2)), (poly([(40, 124), (150, 50), (260, 124)]), (90, 70, 56)),
             (rect(90, 140, 210, 180), (40, 36, 34))]
    return Sprite(stack(w, h, parts, seed=510), "wieza", rim=2, clean=False)


@lru_cache(None)
def brama_eastham():
    w, h = 900, 520
    parts = [(rect(40, 60, 90, 520), (110, 90, 70)), (rect(810, 60, 860, 520), (110, 90, 70)), (rect(20, 40, 880, 120), (90, 74, 58), dict(edge=2)),
             _tekst("EASTHAM PRISON FARM", 40, (450, 82), (236, 226, 200))]
    return Sprite(stack(w, h, parts, seed=511), "brama-eastham", rim=2, clean=False)


@lru_cache(None)
def skrzydlo_bramy():
    w, h = 400, 420
    parts = [(rect(0, 0, 400, 20), (100, 84, 64)), (rect(0, 400, 400, 420), (100, 84, 64)), (rect(0, 0, 20, 420), (100, 84, 64)),
             (rect(380, 0, 400, 420), (100, 84, 64)), (_band((10, 10), (390, 410), 14), (100, 84, 64))]
    im = stack(w, h, parts, seed=512)
    d = ImageDraw.Draw(im)
    for y in range(40, 400, 40):
        d.line([(20, y), (380, y)], fill=(80, 76, 72, 220), width=2)
    return Sprite(im, "skrzydlo-bramy", rim=2, clean=False)


@lru_cache(None)
def urwisko(strona=1):
    """Brzeg wąwozu pod Wellington: stroma czerwona ziemia (strona 1 — prawy brzeg, -1 lewy)."""
    w, h = 900, 520
    pts = [(0, 40), (420, 30), (520, 140), (600, 300), (700, 520), (0, 520)]
    if strona < 0:
        pts = [(w - x, y) for x, y in pts]
    parts = [(poly(pts), (170, 96, 66), dict(edge=3, shade=0.3))]
    return Sprite(stack(w, h, parts, seed=520 + strona), f"urwisko-{strona}", rim=2, clean=False)


@lru_cache(None)
def przeslo():
    w, h = 760, 160
    parts = [(rect(0, 20, 760, 46), (130, 104, 80))] + [(rect(x, 40, x + 16, 160), (110, 86, 64)) for x in range(20, 760, 120)]
    parts += [(_band((x, 46), (x + 120, 150), 8), (110, 86, 64)) for x in range(20, 640, 120)]
    return Sprite(stack(w, h, parts, seed=521), "przeslo", rim=2, clean=False)


@lru_cache(None)
def rzeka_pas(noc=False):
    w, h = 2200, 160
    c = (60, 80, 100) if noc else (110, 150, 166)
    im = stack(w, h, [(poly([(0, 20), (w, 10), (w, h), (0, h)]), c, dict(edge=3, shade=0.25))], seed=530)
    d = ImageDraw.Draw(im)
    r = random.Random(3)
    for _ in range(90):
        x, y = r.uniform(0, w), r.uniform(30, h - 10)
        d.line([(x, y), (x + r.uniform(20, 60), y)], fill=(220, 234, 236, 150), width=2)
    return Sprite(im, f"rzeka-{noc}", rim=2, clean=False, pad=0)


@lru_cache(None)
def sosna(v=0):
    """Sosna z Luizjany: wysoki prosty pień, korona wysoko."""
    r = random.Random(v + 11)
    w, h = 360, 980
    pts = [(180 + r.uniform(-120, 120), r.uniform(40, 360)) for _ in range(22)]
    parts = [(_band((180, 980), (176, 120), 34), (96, 70, 52)), (_kolka(pts, 54), (54, 84, 56), dict(edge=2)),
             (_kolka([(x + 10, y + 16) for x, y in pts[::2]], 40), (70, 104, 66))]
    return Sprite(stack(w, h, parts, seed=540 + v), f"sosna-{v}", rim=2, clean=False)


@lru_cache(None)
def drzewo(v=0, kolor=(90, 120, 70)):
    r = random.Random(v + 21)
    w, h = 520, 640
    pts = [(260 + r.uniform(-170, 170), 200 + r.uniform(-140, 120)) for _ in range(26)]
    parts = [(_band((260, 640), (256, 260), 40), (96, 70, 52)), (_band((256, 330), (170, 200), 14), (96, 70, 52)),
             (_kolka(pts, 70), kolor, dict(edge=2)), (_kolka([(x + 12, y + 20) for x, y in pts[::2]], 50), _shade(kolor, 1.15))]
    return Sprite(stack(w, h, parts, seed=550 + v), f"drzewo-{v}-{kolor}", rim=2, clean=False)


@lru_cache(None)
def krzak(v=0, kolor=(70, 100, 60)):
    r = random.Random(v + 31)
    w, h = 460, 220
    pts = [(r.uniform(50, 410), r.uniform(80, 170)) for _ in range(16)]
    parts = [(_kolka(pts, 54), kolor, dict(edge=2)), (rect(30, 170, 430, 220), _shade(kolor, 0.7))]
    return Sprite(stack(w, h, parts, seed=560 + v), f"krzak-{v}-{kolor}", rim=2, clean=False)


@lru_cache(None)
def wiadukt():
    w, h = 2200, 420
    parts = [(rect(0, 60, w, 96), (112, 104, 96), dict(edge=2))]
    for x in range(80, w, 300):
        parts.append((poly([(x, 92), (x + 40, 92), (x + 46, h), (x - 6, h)]), (104, 96, 88)))
        parts.append((lambda d, s, x=x: d.arc([(x + 40) * s, 70 * s, (x + 300) * s, 330 * s], 180, 360, fill=255, width=int(14 * s)), (104, 96, 88)))
    im = stack(w, h, parts, seed=570)
    return Sprite(im, "wiadukt", rim=2, clean=False)


@lru_cache(None)
def komin():
    w, h = 140, 620
    parts = [(poly([(30, 620), (110, 620), (96, 40), (44, 40)]), (150, 130, 110), dict(edge=2)), (rect(38, 30, 102, 52), (110, 96, 84))]
    return Sprite(stack(w, h, parts, seed=571), "komin", rim=2, clean=False)


@lru_cache(None)
def szalas(v=0):
    """Szałas z desek i blachy w West Dallas."""
    w, h = 420, 300
    c = [(120, 100, 80), (100, 90, 76), (140, 110, 84)][v % 3]
    parts = [(rect(20, 100, 400, 300), c, dict(edge=2, shade=0.2)), (poly([(0, 110), (210, 40), (420, 110)]), (130, 126, 120), dict(edge=2)),
             (rect(170, 180, 250, 300), (60, 46, 36)), (rect(290, 150, 360, 210), (180, 170, 140))]
    im = stack(w, h, parts, seed=580 + v)
    d = ImageDraw.Draw(im)
    for x in range(40, 400, 34):
        d.line([(x, 104), (x, 300)], fill=_shade(c, 0.7) + (200,), width=3)
    return Sprite(im, f"szalas-{v}", rim=2, clean=False)


@lru_cache(None)
def namiot(v=0):
    w, h = 420, 300
    parts = [(poly([(10, 300), (210, 30), (410, 300)]), (220, 210, 186), dict(edge=2, shade=0.2)), (poly([(170, 300), (210, 140), (250, 300)]), (60, 50, 44))]
    return Sprite(stack(w, h, parts, seed=590 + v), f"namiot-{v}", rim=2, clean=False)


# ---------- teatr cieni, drukarnia, mapa, epilog ----------

@lru_cache(None)
def parawan(w=1500, h=640):
    """Parawan teatru cieni: drewniana rama i podświetlony od tyłu papier."""
    parts = [(rect(0, 0, w, h), (94, 66, 44)), (rect(30, 30, w - 30, h - 30), (250, 226, 170), dict(kind="gladki", contrast=0.4))]
    im = stack(w, h, parts, seed=600)
    a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    k = 1 - 0.35 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    inside = (xx > 30) & (xx < w - 30) & (yy > 30) & (yy < h - 30)
    a[..., :3][inside] *= np.clip(k[inside], 0.5, 1)[:, None]
    return Sprite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), f"parawan-{w}-{h}", rim=2, clean=False)


WALEK = 70


@lru_cache(None)
def maszyna():
    """Maszyna drukarska: żeliwny korpus, koło zamachowe, stół z papierem (wałki osobno: walek())."""
    w, h = 900, 620
    c = (60, 62, 66)
    parts = [(rect(80, 200, 820, 560), c, dict(edge=2, shade=0.2)), (rect(40, 540, 860, 620), _shade(c, 0.8)),
             (ell(140, 260, 110, 110), _shade(c, 0.9)), (ell(140, 260, 30, 30), (150, 146, 140)), (rect(500, 120, 860, 200), (236, 228, 206)),
             (rect(260, 300, 760, 330), (40, 40, 44)), (rect(260, 420, 760, 450), (40, 40, 44))]
    return Sprite(stack(w, h, parts, seed=610), "maszyna", rim=2, clean=False)


@lru_cache(None)
def walek():
    w = h = 2 * WALEK + 8
    c = w / 2
    parts = [(ell(c, c, WALEK, WALEK), (50, 50, 54)), (ell(c, c, WALEK * 0.4, WALEK * 0.4), (150, 146, 140))]
    im = stack(int(w), int(h), parts, seed=611)
    d = ImageDraw.Draw(im)
    d.line([(c - WALEK * 0.9, c), (c + WALEK * 0.9, c)], fill=(110, 106, 100, 220), width=6)
    return Sprite(im, "walek", rim=1, clean=False)


STANY = {  # uproszczone zarysy stanów na planszy 1000 × 700 (Teksas na dole, Iowa u góry)
    "TEXAS": [(120, 360), (420, 360), (430, 420), (560, 450), (600, 560), (520, 660), (420, 690), (340, 600), (240, 560), (180, 480), (120, 470)],
    "OKLAHOMA": [(150, 290), (560, 290), (580, 440), (430, 420), (420, 340), (150, 340)],
    "KANSAS": [(200, 170), (560, 170), (560, 290), (200, 290)],
    "MISSOURI": [(560, 160), (760, 150), (800, 330), (760, 420), (580, 420), (560, 290)],
    "ARKANSAS": [(580, 420), (760, 420), (750, 540), (600, 560)],
    "LOUISIANA": [(600, 560), (750, 540), (760, 600), (840, 640), (760, 690), (620, 680)],
    "IOWA": [(560, 40), (780, 40), (800, 150), (560, 160)],
}
STANY_KOLOR = {"TEXAS": (214, 190, 140), "OKLAHOMA": (200, 170, 120), "KANSAS": (220, 204, 150), "MISSOURI": (190, 196, 150),
               "ARKANSAS": (180, 190, 140), "LOUISIANA": (170, 186, 150), "IOWA": (200, 206, 160)}
MIASTA = {"Dallas": (420, 480), "Joplin": (590, 300), "Wellington": (270, 380), "Platte City": (610, 190), "Dexfield": (640, 100),
          "Grapevine": (400, 470), "Commerce": (560, 310), "Ruston": (650, 590), "Gibsland": (640, 580), "Shreveport": (620, 575),
          "Eastham": (500, 590), "Atoka": (480, 400), "Kaufman": (450, 495)}


@lru_cache(None)
def mapa_plansza():
    w, h = 1000, 700
    parts = [(rect(0, 0, w, h), (232, 222, 196), dict(kind="gladki", edge=4, contrast=1.1))]
    for n, (k, pts) in enumerate(STANY.items()):
        parts.append((poly(pts), STANY_KOLOR[k], dict(edge=2)))
    im = stack(w, h, parts, seed=620)
    d = ImageDraw.Draw(im)
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_PL, 26, index=PL_IDX)
    for k, pts in STANY.items():
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        d.text((cx, cy), k, font=f, fill=(90, 70, 50, 200), anchor="mm")
    return Sprite(im, "mapa-stanow", rim=2, clean=False)


@lru_cache(None)
def nagrobek(v=0):
    w, h = 220, 300
    c = [(170, 168, 164), (150, 148, 146), (186, 182, 176)][v % 3]
    parts = [(poly([(20, 300), (20, 80), (110, 10), (200, 80), (200, 300)]), c, dict(edge=2, shade=0.2))]
    if v % 2:
        parts = [(poly([(30, 300), (30, 60), (110, 20), (190, 60), (190, 300)]), c, dict(edge=2, shade=0.2))]
    return Sprite(stack(w, h, parts, seed=630 + v), f"nagrobek-{v}", rim=2, clean=False)


@lru_cache(None)
def namiot_jarmark():
    w, h = 900, 560
    parts = []
    for k in range(9):
        x0 = 40 + k * 91
        parts.append((poly([(x0, 200), (x0 + 91, 200), (x0 + 91, 560), (x0, 560)]), (200, 50, 46) if k % 2 == 0 else (240, 232, 214), dict(edge=1)))
    parts += [(poly([(20, 210), (450, 20), (880, 210)]), (200, 50, 46), dict(edge=2)), (rect(330, 300, 570, 560), (40, 30, 26)),
              _tekst("SEE THE DEATH CAR", 34, (450, 250), (250, 230, 170))]
    return Sprite(stack(w, h, parts, seed=640), "namiot-jarmark", rim=2, clean=False)


@lru_cache(None)
def kolo_mlynskie():
    w = h = 700
    c = 350
    parts = [(lambda d, s: d.ellipse([20 * s, 20 * s, 680 * s, 680 * s], outline=255, width=int(14 * s)), (200, 60, 60))]
    for k in range(12):
        a = math.radians(k * 30)
        parts.append((_band((c, c), (c + 330 * math.cos(a), c + 330 * math.sin(a)), 8), (220, 210, 190)))
    parts.append((ell(c, c, 30, 30), (200, 60, 60)))
    return Sprite(stack(w, h, parts, seed=641), "kolo-mlynskie", rim=2, clean=False)


@lru_cache(None)
def ekran_kina():
    w, h = 1300, 720
    parts = [(rect(0, 0, w, h), (110, 30, 34), dict(edge=2)), (rect(120, 60, w - 120, h - 140), (40, 38, 40)),
             (rect(130, 70, w - 130, h - 150), GAZETA, dict(kind="gladki", contrast=0.6))]
    for k in range(10):
        parts.append((rect(k * 12, 0, k * 12 + 8, h), (140, 40, 44)))
        parts.append((rect(w - k * 12 - 8, 0, w - k * 12, h), (140, 40, 44)))
    return Sprite(stack(w, h, parts, seed=650), "ekran-kina", rim=2, clean=False)


@lru_cache(None)
def widownia(v=0):
    """Rząd głów widzów od tyłu (sylwetki) — plan najbliżej kamery w kinie."""
    w, h = 2200, 200
    r = random.Random(v)
    pts = [(x + r.uniform(-10, 10), 70 + r.uniform(-8, 8)) for x in range(30, w, 76)]
    parts = [(_kolka(pts, 34), (40, 34, 34)), (rect(0, 90, w, h), (50, 40, 40))]
    kapelusze = [(x, y - 30) for x, y in pts[::3]]
    parts.append((_kolka(kapelusze, 22), (30, 26, 26)))
    return Sprite(stack(w, h, parts, seed=660 + v), f"widownia-{v}", rim=2, clean=False)


@lru_cache(None)
def ganek():
    """Ganek domu Hamera w Austin: weranda z dachem i balustradą."""
    w, h = 1300, 620
    parts = [(rect(0, 120, w, 620), (214, 204, 182), dict(edge=2)), (poly([(-20, 140), (w / 2, 20), (w + 20, 140)]), (110, 76, 60), dict(edge=2)),
             (rect(0, 470, w, 500), (150, 120, 90))]
    parts += [(rect(x, 140, x + 24, 500), (236, 230, 214)) for x in (40, 420, 860, 1240)]
    parts += _okno_parts(560, 240, 760, 420)
    im = stack(w, h, parts, seed=670)
    d = ImageDraw.Draw(im)
    for x in range(60, w - 40, 30):
        d.line([(x, 420), (x, 470)], fill=(236, 230, 214, 255), width=6)
    d.line([(40, 420), (w - 40, 420)], fill=(236, 230, 214, 255), width=10)
    return Sprite(im, "ganek", rim=2, clean=False)


@lru_cache(None)
def slonce_bc():
    """Złote słońce prerii z papieru (czerwony krążek „Pierwszego cesarza” wyglądał jak flaga Japonii)."""
    w = h = 220
    parts = [(ell(110, 110, 104, 104), (236, 176, 70), dict(edge=4)), (ell(110, 110, 78, 78), (246, 204, 104), dict(kind="gladki"))]
    return Sprite(stack(w, h, parts, seed=700), "slonce-bc", rim=2, clean=False)


@lru_cache(None)
def serce(kolor=(200, 50, 60), w=120):
    h = int(w * 0.9)
    k = w / 120.0
    pts = [(60 * k, 104 * k), (8 * k, 50 * k), (14 * k, 18 * k), (40 * k, 8 * k), (60 * k, 26 * k), (80 * k, 8 * k), (106 * k, 18 * k),
           (112 * k, 50 * k)]
    parts = [(_kolka([(36 * k, 34 * k), (84 * k, 34 * k)], 28 * k), kolor, dict(edge=2)), (poly(pts), kolor, dict(edge=2))]
    return Sprite(stack(w, h, parts, seed=710), f"serce-{kolor}-{w}", rim=2, clean=False)


@lru_cache(None)
def tatuaz():
    """Tabliczka-tatuaż Bonnie: dwa serca z imionami „BONNIE” i „ROY” (księga świata: tatuaż na udzie — pokazany jako znak)."""
    w, h = 420, 200
    parts = [(rect(4, 4, w - 4, h - 4), (240, 226, 194), dict(kind="gladki", edge=4, contrast=1.3))]
    im = stack(w, h, parts, seed=711)
    for n, (x, txt) in enumerate(((110, "BONNIE"), (310, "ROY"))):
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sz = stack(160, 144, [(_kolka([(48, 46), (112, 46)], 38), (196, 50, 60), dict(edge=2)),
                              (poly([(80, 138), (12, 70), (20, 22), (80, 40), (140, 22), (148, 70)]), (196, 50, 60), dict(edge=2)),
                              (glyphs(txt, 24, FONT_PL, PL_IDX, (80, 66), "mm"), (250, 240, 220), dict(kind="gladki", rough=0.4))], seed=712 + n)
        lay.alpha_composite(sz, (int(x - 80), 28))
        im = glue(im, lay, shadow=0.4)
    return Sprite(im, "tatuaz", rim=2, clean=False)


@lru_cache(None)
def zdjecie_bonnie(w=420, h=320):
    """Odbitka zdjęcia z Joplin: biała ramka, szare tło, Bonnie z cygarem (z arkusza lalki) przy błotniku Forda — w sepii."""
    im = Image.new("RGBA", (w, h), (244, 240, 230, 255))
    foto = Image.new("RGBA", (w - 40, h - 40), (150, 146, 138, 255))
    auto_ = ford("szary").img if hasattr(ford("szary"), "img") else None
    body = _korpus_img(spec("bonnie_cygaro"))
    bh = int((h - 50) * 1.0)
    body = body.resize((int(body.width * bh / body.height), bh), Image.LANCZOS)
    foto.alpha_composite(body, (int((w - 40) * 0.25), (h - 40) - bh + 10))
    g = np.asarray(foto.convert("L"), np.float32)
    sep = np.dstack([g * 1.05, g * 0.95, g * 0.8, np.full_like(g, 255)]).clip(0, 255).astype(np.uint8)
    im.alpha_composite(Image.fromarray(sep, "RGBA"), (20, 20))
    return Sprite(im, "zdjecie-bonnie", rim=2, clean=False)
