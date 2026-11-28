"""Zestaw filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune”: lalki kaukaskie, rosyjskie i gruzińskie,
dekoracje Kaukazu, Petersburga i pustyni, karty z maszynopisem i rekwizyty.

Podstawa to kopia zestawu „Bonnie and Clyde” (output/bonnie-i-clyde/zestaw_bc.py, 27.11.2026): ten sam układ arkusza lalki
(korpus + dwie ręce na zawiasie w barku), więc scena.lalka składa ją tymi samymi liczbami. Na końcu pliku część kaukaska:
nakrycia głowy (papacha, turban Szamila, czepiec gruzińskich księżnych, furażka), gazyry i kindżał na czerkiesce, długie
suknie, epolety, nowa sceneria (Kaukaz, Gruzja, Petersburg, pustynia — księga świata: nic z poprzednich filmów) i rekwizyty.
Funkcje z „Bonnie and Clyde” (auta, gazety, preria) zostają w pliku, ale ten film ich nie używa.
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
    # Waco 1930: płaszcz, pod który Bonnie chowa rewolwer (marker reżysera 21.11, ujęcie 27: „skryj go pod płaszcz”)
    "bonnie_plaszcz": dict(kobieta=True, wlosy=(214, 176, 104), fryzura="loki", kapelusz="beret", kapelusz_kolor=(150, 40, 46),
                           stroj="plaszcz", gora=(150, 112, 78), dol=(150, 112, 78), kolnierzyk=(236, 226, 206), szer=0.96),
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
    "darby_czapka": dict(fryzura="zaczesane", wlosy=(40, 32, 28), gora=(30, 30, 34), dol=(28, 28, 32), krawat=(20, 20, 22),
                         koszula=(244, 242, 236), szer=0.94, kapelusz="kaszkiet", kapelusz_kolor=(40, 40, 46)),  # ukłony: czapka z daszkiem (marker 23.11)
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
    # ta sama lalka z otwartymi ustami (marker reżysera 21.11, ujęcie 14: „otwiera buzię i tabliczkę ooo..”) — podmiana w jednej klatce
    "detektyw_o": dict(kapelusz="fedora", kapelusz_kolor=(90, 70, 54), stroj="plaszcz", gora=(120, 96, 70), dol=(90, 80, 70),
                       odznaka=True, wasy=True, usta="o"),
    "detektyw_oo": dict(kapelusz="fedora", kapelusz_kolor=(90, 70, 54), stroj="plaszcz", gora=(120, 96, 70), dol=(90, 80, 70),
                        odznaka=True, wasy=True, usta="o", oczy="mniejszosc"),
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


LALKI["hamer_bez"] = dict(LALKI["hamer"], kapelusz=None)  # Hamer z kapeluszem w ręce (po zasadzce, ukłon)


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


def _korpus_img(s, seed_spec=None):
    """seed_spec — spec, z którego liczy się ziarno faktury (korpus bez kapelusza ma tę samą fakturę co z kapeluszem)."""
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
    im = stack(w, h, parts, seed=sum(map(ord, str(sorted((seed_spec or s).items())))) % 997)
    d = ImageDraw.Draw(im)
    ink = INK + (235,)
    hair = s["wlosy"]
    if s["oczy"] == "otwarte":
        for x0, x1, yy in ((130, 144, 124), (164, 178, 122)):
            d.line([(x0 - 2, yy - 9), (x1 + 2, yy - 11 if x0 > 150 else yy - 10)], fill=_shade(hair, 0.8) + (240,), width=4)
            d.line([(x0, yy), (x1, yy)], fill=ink, width=3)
            d.ellipse([(x0 + x1) / 2 - 3.5 + 2, yy - 1, (x0 + x1) / 2 + 3.5 + 2, yy + 7], fill=ink)
    elif s["oczy"] == "mniejszosc":
        # oczy jak dwa znaki „<” (markery reżysera 24.11, ujęcia 14 i 49: „zrób mu z kulek oczu na chwilę takie znaki
        # mniejszości, jakby patrzał na te zdjęcia, że woo < <”); na arkuszu „>”, bo policjant patrzy w lewo (lustro)
        for x0, x1, yy in ((130, 144, 124), (164, 178, 122)):
            d.line([(x0 - 1, yy - 8), (x1 + 1, yy), (x0 - 1, yy + 8)], fill=ink, width=4, joint="curve")
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
    if s["usta"] == "o":  # okrągłe, otwarte usta pod wąsem („OOO…”)
        d.ellipse([163, 160, 179, 180], fill=(70, 26, 26, 245), outline=INK + (235,), width=2)
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
    def bez_kapelusza(self):
        """Korpus bez nakrycia głowy, z tą samą fakturą (kapelusz w dłoni — uwagi reżysera 23.11 w ujęciach 104 i 119)."""
        if getattr(self, "_bez", None) is None:
            self._bez = Sprite(_korpus_img(dict(self.s, kapelusz=None), seed_spec=self.s), f"lalka-bez-{self.key}", rim=2, clean=False,
                               crop=False)
        return self._bez

    @property
    def kapelusz(self):
        """Samo nakrycie głowy (te same części i ziarno co w korpusie): (wycinek, środek w pikselach arkusza) albo None
        (bez nakrycia albo welon, który się nie zdejmuje)."""
        if getattr(self, "_kap", None) is None:
            self._kap = False
            if self.s.get("kapelusz") and self.s["kapelusz"] != "welon":
                L = self.s["nogi"]
                parts = []
                _kapelusz(self.s, parts)
                im = stack(FIG_W, FIG_H + L, parts, seed=sum(map(ord, str(sorted(self.s.items())))) % 997)
                if self.s["szer"] != 1.0:
                    im = im.resize((round(FIG_W * self.s["szer"]), FIG_H + L), Image.LANCZOS)
                bb = im.getchannel("A").point(lambda v: 255 if v > 30 else 0).getbbox()
                if bb:
                    spr = Sprite(im.crop(bb), f"kapelusz-{self.key}", rim=2, clean=False, crop=False)
                    self._kap = (spr, ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2))
        return self._kap or None

    @property
    def siedzi(self):
        """Korpus bez nóg (ucięty tuż pod biodrami): pasażer w aucie, lalka za stołem — nogi nie wystają spod karoserii."""
        if self._siedzi is None:
            im = _korpus_img(self.s).copy()
            a = im.getchannel("A")
            a.paste(0, (0, BIODRO + 10, im.size[0], im.size[1]))
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


def _buzia_bonnie(d, cx, cy, r):
    """Duża śmiejąca się buzia Bonnie na stronie gazety (marker reżysera 23.11, ujęcie „gazety_zle”): blond loki, czerwony beret,
    oczy zmrużone ze śmiechu, szeroko otwarte usta."""
    d.ellipse([cx - r * 1.08, cy - r * 1.02, cx + r * 1.08, cy + r * 0.7], fill=(222, 186, 96, 255))  # włosy
    d.ellipse([cx - r * 0.82, cy - r * 0.8, cx + r * 0.82, cy + r * 0.86], fill=(238, 204, 176, 255))  # twarz
    d.ellipse([cx - r * 1.05, cy - r * 1.32, cx + r * 0.55, cy - r * 0.62], fill=(184, 40, 38, 255))  # beret
    for sx in (-1, 1):  # oczy zmrużone (łuki)
        d.arc([cx + sx * r * 0.42 - r * 0.2, cy - r * 0.28, cx + sx * r * 0.42 + r * 0.2, cy - r * 0.02], 200, 340, fill=(40, 30, 26, 255),
              width=max(2, int(r * 0.07)))
    d.chord([cx - r * 0.48, cy + r * 0.0, cx + r * 0.48, cy + r * 0.66], 0, 180, fill=(70, 20, 20, 255))  # usta
    d.chord([cx - r * 0.26, cy + r * 0.34, cx + r * 0.26, cy + r * 0.64], 180, 360, fill=(200, 70, 70, 255))  # język
    d.rectangle([cx - r * 0.36, cy + r * 0.02, cx + r * 0.36, cy + r * 0.1], fill=(250, 248, 240, 255))  # zęby


def _gazeta_img(w, h, naglowek, tytul, seed=0, zdjecie=True, kolor=GAZETA, buzia=False):
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
    if buzia:
        r_ = min(w * 0.3, (h * 0.94 - top) * 0.42)
        _buzia_bonnie(d, w / 2, top + (h * 0.94 - top) * 0.52, r_)
        return im
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
def gazeta(naglowek="EXTRA!", seed=0, w=360, h=480, zdjecie=True, tytul=None, buzia=False):
    tytul = tytul or TYTULY_GAZET[seed % len(TYTULY_GAZET)]
    return Sprite(_gazeta_img(w, h, naglowek, tytul, seed, zdjecie, buzia=buzia), f"gazeta-{naglowek}-{seed}{'-buzia' if buzia else ''}",
                  rim=2, clean=False)


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
    # tablica szersza od napisu (przegląd 19.11: „THE” i „PAPER” wystawały poza czarną tablicę)
    stopnie = [(170, -150, 1110, -40), (330, -190, 950, -150), (420, -224, 860, -190)]
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
    # glyphs ze spacing stawia każdą literę od punktu startu, więc środek liczymy sami (wcześniej napis zaczynał się
    # na środku i wystawał za tablicę z prawej)
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_PL, 24, index=PL_IDX)
    szer = sum(f.getlength(ch) for ch in "BONNIE AND CLYDE") + 6 * 15
    sub = glyphs("BONNIE AND CLYDE", 24, FONT_PL, PL_IDX, (640 - szer / 2 + ox, -170 + oy), "lm", spacing=6)
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
def ford(kolor="szary", napis=None, dziury=0, kurz=False, lustro=False):
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
        if lustro:  # auto jedzie w lewo (sx=-1): napis rysujemy odbity, żeby po odbiciu auta czytał się normalnie
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((362, 220), napis, font=f, fill=(240, 236, 226, 255), anchor="mm")
            lay = lay.transpose(Image.FLIP_LEFT_RIGHT)
            im.alpha_composite(lay, (2 * 362 - im.size[0], 0)) if 2 * 362 - im.size[0] >= 0 else im.alpha_composite(
                lay.crop((im.size[0] - 2 * 362, 0, im.size[0], im.size[1])), (0, 0))
        else:
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
        # kurz na dole karoserii kładzie się NA wierzch (alpha_composite) i tylko tam, gdzie jest blacha. ImageDraw.rectangle
        # z półprzezroczystym kolorem podmieniał piksele razem z kanałem alfa: dół auta robił się przezroczysty i spod
        # karoserii wystawały nogi pasażerów (reżyser 24.11: „napraw spód auta bo zniknął”, „w kilku nadal nie ma spodów aut”).
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle([60, 240, 870, 290], fill=(190, 170, 130, 70))
        lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(im.getchannel("A")))))
        im.alpha_composite(lay)
    return Sprite(im, f"ford-{c}-{napis}-{dziury}-{kurz}-{lustro}", rim=2, clean=False, crop=False)


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
    # dzbanek z uchem po lewej (chwyt: ucho, ok. (0.08, 0.45)), dzióbek po prawej u góry (ok. (0.97, 0.38))
    "dzbanek": (150, 150, lambda: [(_kolka([(16, 66), (14, 84), (18, 100)], 12), (190, 190, 196)), (ell(18, 84, 9, 16), (90, 110, 90)),
                                   (poly([(50, 40), (120, 40), (130, 146), (44, 146)]), (210, 210, 214)), (ell(85, 40, 36, 10), (180, 180, 186)),
                                   (poly([(122, 70), (148, 52), (144, 64), (126, 84)]), (210, 210, 214))]),
    "kubek": (80, 80, lambda: [(rect(10, 10, 60, 76), (244, 240, 230)), (ell(64, 40, 12, 16), (244, 240, 230))]),
    "kajdanki": (160, 80, lambda: [(ell(40, 40, 30, 30), (150, 150, 156)), (ell(120, 40, 30, 30), (150, 150, 156)), (rect(64, 34, 96, 46), (150, 150, 156))]),
    "olowek": (220, 26, lambda: [(rect(4, 6, 190, 20), (190, 40, 36)), (poly([(190, 6), (216, 13), (190, 20)]), (230, 200, 160))]),
    # pióro gołębia do pisania (marker reżysera 23.11, ujęcie „poezja”): szare piórko z ciemną końcówką, stosina i stalówka
    "pioro": (260, 70, lambda: [(poly([(40, 38), (92, 16), (170, 8), (236, 14), (256, 30), (238, 46), (164, 60), (92, 56)]), (182, 184, 194)),
                                (poly([(176, 8), (236, 14), (256, 30), (238, 46), (196, 56), (206, 30)]), (104, 106, 122)),
                                (poly([(60, 34), (120, 16), (126, 22), (70, 40)]), (226, 228, 236)),
                                (_band((10, 40), (250, 30), 3), (240, 236, 224)), (poly([(0, 42), (16, 35), (20, 44)]), (40, 36, 34))]),
    # obłok bójki jak w kreskówce (marker reżysera 23.11, ujęcie „drzewo”): papierowy kłąb z kilku kul
    "oblok": (240, 170, lambda: [(ell(120, 92, 112, 72), (214, 208, 198), dict(edge=2)), (ell(70, 70, 60, 54), (236, 232, 224), dict(edge=2)),
                                 (ell(160, 58, 66, 52), (240, 236, 228), dict(edge=2)), (ell(116, 112, 70, 50), (228, 224, 214)),
                                 (ell(190, 110, 46, 40), (232, 228, 220)), (ell(52, 118, 44, 38), (226, 222, 212))]),
    # odznaka strażnika Teksasu na piersi Hamera (marker reżysera 23.11): gwiazda w kole
    "odznaka": (60, 60, lambda: [(ell(30, 30, 28, 28), (206, 172, 82), dict(edge=2)), (ell(30, 30, 21, 21), (176, 142, 60)),
                                 (poly([(30 + 19 * math.cos(-math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.42),
                                         30 + 19 * math.sin(-math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.42)) for k in range(10)]),
                                  (232, 204, 120))]),
    # złamany ołówek (marker reżysera 23.11, ujęcie „podkreslenie”: „trzask i niech ten grafit gdzieś poleci, kredka się łamie”)
    "olowek_zlamany": (190, 26, lambda: [(rect(4, 6, 176, 20), (190, 40, 36)), (poly([(176, 6), (186, 9), (180, 12), (188, 16), (176, 20)]),
                                                                                (230, 200, 160))]),
    "olowek_czubek": (46, 26, lambda: [(poly([(2, 6), (8, 9), (3, 12), (9, 16), (2, 20), (30, 13)]), (230, 200, 160)),
                                       (poly([(24, 10), (44, 13), (24, 16)]), (50, 48, 52))]),
    # suknia ślubna rozciągnięta w dzwon (marker reżysera 23.11, ujęcie „tullis”: „tak jej rozciągnij tę suknię”)
    "suknia_slub": (220, 140, lambda: [(poly([(84, 0), (136, 0), (214, 134), (6, 134)]), (246, 244, 238), dict(edge=2)),
                                       (poly([(40, 96), (180, 96), (196, 110), (24, 110)]), (232, 228, 220)),
                                       (poly([(60, 60), (160, 60), (170, 68), (50, 68)]), (236, 232, 226))]),
    # suknia ślubna Maree w jednym kawałku: stanik od linii ramion, wcięcie w talii i dzwon do ziemi (marker reżysera 24.11,
    # ujęcie 90: „napraw suknię, ona ma być w jednej całości, a nie w dwóch częściach”); arkusz w skali lalki (614 px wzrostu)
    "suknia_cala": (260, 470, lambda: [(poly([(104, 0), (156, 0), (172, 40), (166, 190), (256, 466), (4, 466), (94, 190), (88, 40)]),
                                        (246, 244, 238), dict(edge=2)),
                                       (poly([(96, 182), (164, 182), (168, 196), (92, 196)]), (232, 228, 220)),
                                       (poly([(30, 420), (230, 420), (240, 440), (20, 440)]), (234, 230, 222)),
                                       (poly([(60, 330), (200, 330), (208, 342), (52, 342)]), (238, 234, 228))]),
    "kwiatek": (40, 120, lambda: [(rect(18, 40, 22, 118), (80, 120, 60)), (ell(20, 22, 16, 16), (250, 250, 244)), (ell(20, 22, 6, 6), (230, 190, 70))]),
    # źdźbło słomy w ustach Gaulta (marker reżysera 23.11, ujęcie „noc”: „ma słomę w ustach i na następnych ujęciach też”)
    "slomka": (70, 10, lambda: [(rect(2, 3, 68, 7), (226, 200, 110)), (rect(50, 2, 68, 8), (206, 176, 90))]),
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
    # dziura po kuli w karoserii (ujęcie 13, marker reżysera 21.11: „tu się wbija kula”)
    "dziura": (40, 40, lambda: [(ell(20, 20, 17, 17), (150, 150, 156)), (ell(20, 20, 11, 11), (22, 20, 20))]),
    # patelnia z kuchni (marker reżysera 21.11, ujęcia 26–27: „daj jej patelnię!”): chwyt za koniec rączki (0.93, 0.5)
    "patelnia": (300, 90, lambda: [(poly([(4, 30), (150, 30), (140, 70), (14, 70)]), (54, 52, 56), dict(edge=2)),
                                   (ell(77, 32, 73, 9), (84, 82, 86)), (rect(146, 38, 290, 54), (54, 52, 56), dict(edge=2)),
                                   (ell(284, 46, 9, 9), (40, 38, 40))]),
    # stary aparat prasowy z wielką czaszą lampy błyskowej z boku (marker reżysera 21.11, ujęcie 15); chwyt: spód korpusu (0.6, 0.95),
    # środek czaszy (0.2, 0.22) — stamtąd błyska flesz
    "aparat_lampa": (220, 200, lambda: [(rect(78, 92, 196, 188), (46, 42, 40), dict(edge=2)), (rect(178, 104, 214, 176), (70, 64, 58)),
                                        (ell(206, 140, 16, 20), (30, 34, 44)), (rect(100, 76, 150, 94), (60, 56, 52)),
                                        (rect(36, 70, 52, 148), (150, 146, 140)), (rect(36, 132, 84, 148), (150, 146, 140)),
                                        (ell(44, 44, 40, 40), (214, 214, 218), dict(kind="gladki", edge=2)),
                                        (ell(44, 44, 26, 26), (186, 186, 192), dict(kind="gladki")), (ell(44, 44, 11, 11), (250, 248, 236))]),
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
    # gagi (reżyser 19.11.2026: „gagi robimy wszystkie”, docs/filmy/bonnie-i-clyde/GAGI.md)
    "cma": (130, 90, lambda: [(ell(38, 44, 34, 26), (156, 146, 126), dict(edge=2)), (ell(92, 44, 34, 26), (156, 146, 126), dict(edge=2)),
                              (ell(65, 46, 9, 24), (92, 82, 70)), (_band((60, 22), (50, 6), 3), (92, 82, 70)), (_band((70, 22), (80, 6), 3), (92, 82, 70))]),
    "zielsko": (170, 170, lambda: [(ell(85, 85, 80, 76), (176, 146, 96), dict(edge=2)), (ell(85, 85, 58, 54), (146, 116, 72)),
                                   (ell(85, 85, 36, 34), (176, 146, 96)), (_band((20, 70), (150, 100), 5), (120, 92, 58)),
                                   (_band((40, 140), (130, 30), 5), (120, 92, 58)), (_band((85, 10), (85, 160), 4), (120, 92, 58))]),
    "miarka": (320, 50, lambda: [(rect(40, 16, 316, 34), (232, 202, 72), dict(edge=1))] + [(rect(x, 16, x + 2, 24), (60, 50, 30)) for x in range(52, 312, 16)]
                                + [(ell(26, 25, 24, 22), (196, 60, 52), dict(edge=2)), (ell(26, 25, 8, 8), (120, 40, 36))]),
    "salata": (100, 70, lambda: [(ell(50, 35, 46, 28), (130, 190, 86), dict(edge=2)), (_band((10, 36), (92, 32), 3), (96, 150, 62)),
                                 (_band((40, 34), (30, 14), 2), (96, 150, 62)), (_band((60, 34), (72, 56), 2), (96, 150, 62))]),
    "plama": (70, 60, lambda: [(ell(35, 26, 24, 18), (246, 246, 240)), (ell(16, 38, 9, 8), (246, 246, 240)), (ell(54, 40, 8, 7), (246, 246, 240)),
                               (ell(36, 50, 6, 8), (246, 246, 240))]),
    "kasetka": (190, 120, lambda: [(rect(8, 36, 182, 116), (112, 72, 50), dict(edge=2)), (rect(8, 18, 182, 40), (134, 88, 62), dict(edge=2)),
                                   (rect(78, 56, 112, 72), (222, 200, 120))]),
    "woz_siano": (440, 280, lambda: [(ell(220, 92, 200, 86), (222, 192, 102), dict(edge=2)), (rect(30, 140, 410, 190), (132, 92, 60), dict(edge=2)),
                                     (_band((410, 170), (480, 150), 10), (110, 76, 50)), (ell(104, 214, 52, 52), (92, 66, 46), dict(edge=2)),
                                     (ell(330, 214, 52, 52), (92, 66, 46), dict(edge=2)), (ell(104, 214, 14, 14), (162, 132, 92)),
                                     (ell(330, 214, 14, 14), (162, 132, 92))]),
    "kulka": (90, 80, lambda: [(poly([(10, 40), (22, 14), (46, 6), (70, 12), (84, 34), (80, 60), (60, 76), (30, 74), (12, 60)]), (226, 220, 206),
                                dict(kind="gnieciony", edge=2, contrast=1.6)),
                               (poly([(30, 30), (52, 22), (62, 40), (40, 52)]), (196, 190, 176), dict(kind="gnieciony", contrast=1.6))]),
    "motyka": (60, 260, lambda: [(_band((40, 6), (40, 220), 8), (130, 96, 62)), (poly([(10, 214), (58, 218), (56, 252), (8, 246)]), (120, 120, 126),
                                 dict(edge=2))]),
    "laska": (40, 220, lambda: [(_band((20, 214), (20, 30), 8), (96, 64, 42)), (_band((20, 30), (34, 10), 8), (96, 64, 42))]),
}


def sylwetka(key, rece=(0.0, 0.0), lean=0.0, rzecz=None, kolor=False):
    """Czarna sylwetka lalki w pozie (obraz PIL, wysokość arkusza korpusu): ręce pod kątami jak w scena.lalka (flip=1),
    rzecz = (nazwa rekwizytu, wysokość w px arkusza, kotwica chwytu) w przedniej dłoni. Do mikro-klatek na kliszy."""
    s = spec(key)
    body, arm = _korpus_img(s), _ramie_img(s)
    cw, ch = body.size
    k = s["szer"]
    can = Image.new("RGBA", (cw + 600, ch + 600), (0, 0, 0, 0))
    ox, oy = 300, 300
    zaw = (RAMIE_ZAWIAS[0] * k + (arm.size[0] - RAMIE_W * k) / 2, RAMIE_ZAWIAS[1])
    dl = DLON[1] - RAMIE_ZAWIAS[1]
    for nazwa, ang in (("tyl", rece[1]), ("przod", rece[0])):
        bx, by = BARK[nazwa]
        bx = cw / 2 + (bx - FIG_W / 2) * k
        R = max(arm.size) * 2
        tmp = Image.new("RGBA", (R, R), (0, 0, 0, 0))
        tmp.paste(arm, (int(R / 2 - zaw[0]), int(R / 2 - zaw[1])), arm)
        tmp = tmp.rotate(ang, resample=Image.BICUBIC)
        can.alpha_composite(tmp, (int(ox + bx - R / 2), int(oy + by - R / 2)))
        if nazwa == "przod" and rzecz:
            a = math.radians(ang)
            hx, hy = ox + bx + math.sin(a) * dl, oy + by + math.cos(a) * dl
            nm, rh, anc = rzecz
            rw, rh_, fn = REKWIZYTY[nm]
            im = stack(rw, rh_, fn(), seed=300 + len(nm))
            im = im.resize((max(1, int(im.size[0] * rh / im.size[1])), int(rh)))
            can.alpha_composite(im, (int(hx - anc[0] * im.size[0]), int(hy - anc[1] * im.size[1])))
        if nazwa == "tyl":
            can.alpha_composite(body, (ox, oy))
    if lean:
        can = can.rotate(-lean, resample=Image.BICUBIC, center=(ox + cw / 2, oy + STOPA))
    if kolor:  # lalka w pozie w kolorach (zdjęcie „pajacyk”), nie czarna sylwetka
        return can.crop(can.getbbox())
    a = can.getchannel("A")
    out = Image.new("RGBA", can.size, (14, 12, 12, 0))
    out.putalpha(a)
    return out.crop(out.getbbox())


@lru_cache(None)
def ciecz(kolor=(196, 148, 60)):
    """Tafla cieczy (paliwo zalewające scenę, ujęcie 13): pas z falistym brzegiem i jaśniejszą linią powierzchni; kotwica u góry."""
    w, h = 1300, 160
    a = np.zeros((h, w), np.uint8)
    yy, xx = np.mgrid[:h, :w]
    fala = 14 + 5 * np.sin(xx / 47.0) + 3 * np.sin(xx / 13.0 + 1.3)
    a[yy >= fala] = 255
    rgb = np.zeros((h, w, 3), np.uint8)
    rgb[:] = kolor
    jasna = (yy >= fala) & (yy < fala + 5)
    rgb[jasna] = tuple(min(255, int(c * 1.35)) for c in kolor)
    im = Image.fromarray(np.dstack([rgb, a]), "RGBA")
    return Sprite(im, f"ciecz-{kolor}", rim=0, clean=False)


@lru_cache(None)
def klisza_pozy():
    """Klisza z aparatu z Joplin: w każdej klatce czarna, mikro sylwetka Bonnie w innej pozie (marker reżysera 21.11, ujęcie 14:
    „na tych klatkach z filmu są pozy czarne Bonnie, różne mikro”). Arkusz jak „klisza” (360 × 90, cztery klatki)."""
    w, h = 360, 90
    base = stack(w, h, [(rect(0, 10, 360, 80), (40, 34, 30))] + [(rect(20 + k * 84, 22, 84 + k * 84, 68), (196, 174, 132)) for k in range(4)]
                 + [(rect(8 + k * 22, 13, 16 + k * 22, 19), (210, 200, 180)) for k in range(16)]
                 + [(rect(8 + k * 22, 71, 16 + k * 22, 77), (210, 200, 180)) for k in range(16)], seed=1931)
    pozy = [dict(rece=(90, 10), rzecz=("rewolwer", 70, (0.3, 0.75))),   # z rewolwerem
            dict(rece=(150, 30), lean=-6),                               # macha
            dict(rece=(35, 35)),                                         # ręce na biodrach
            dict(rece=(120, 160), lean=6)]                               # obie ręce w górze
    for kk, pz in enumerate(pozy):
        # klisza wisi pionowo (obrót 90° w kadrze), więc sylwetka leży na arkuszu głową w lewo — w kadrze stoi prosto
        sil = sylwetka("bonnie", **pz).rotate(90, expand=True)
        sc = min(56 / sil.size[0], 42 / sil.size[1])
        sil = sil.resize((max(1, int(sil.size[0] * sc)), max(1, int(sil.size[1] * sc))), Image.LANCZOS)
        base.alpha_composite(sil, (20 + kk * 84 + (64 - sil.size[0]) // 2, 22 + (46 - sil.size[1]) // 2))
    return Sprite(base, "rek-klisza-pozy", rim=2, clean=False)


@lru_cache(None)
def odbitka_bonnie(v=0):
    """Odbitka z ciemni (marker reżysera 24.11, ujęcie 50: „u góry różne odbitki Bonnie, czarne”): papier fotograficzny
    z białym marginesem, na nim czarna sylwetka Bonnie — każda odbitka w innej pozie (jak mikro-pozy na kliszy z Joplin)."""
    w, h = 150, 190
    base = stack(w, h, [(rect(2, 2, w - 2, h - 2), (238, 232, 218), dict(kind="gladki", edge=2)),
                        (rect(14, 14, w - 14, h - 30), (214, 204, 184), dict(kind="gladki"))], seed=1940 + v)
    pozy = [dict(rece=(90, 10), rzecz=("rewolwer", 70, (0.3, 0.75))), dict(rece=(150, 30), lean=-6), dict(rece=(35, 35)),
            dict(rece=(120, 160), lean=6), dict(rece=(70, 20), rzecz=("cygaro", 30, (0.1, 0.5))), dict(rece=(160, 160)),
            dict(rece=(100, 60), rzecz=("karabin", 40, (0.3, 0.55)), lean=-4)]
    sil = sylwetka("bonnie", **pozy[v % len(pozy)])
    sc = min((w - 40) / sil.size[0], (h - 58) / sil.size[1])
    sil = sil.resize((max(1, int(sil.size[0] * sc)), max(1, int(sil.size[1] * sc))), Image.LANCZOS)
    base.alpha_composite(sil, ((w - sil.size[0]) // 2, 16 + (h - 46 - sil.size[1]) // 2))
    return Sprite(base, f"odbitka-bonnie-{v}", rim=2, clean=False)


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
              # szyld pod napisem: biały napis ginął na białych pasach namiotu (przegląd 19.11)
              (rect(250, 226, 650, 276), (40, 30, 26), dict(edge=2)),
              _tekst("SEE THE DEATH CAR", 32, (450, 252), (250, 230, 170))]
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
def nuta(v=0):
    """Nuta z czarnego papieru (gra saksofonu, marker reżysera 24.11): v=0 — ósemka z chorągiewką, v=1 — dwie ósemki z belką."""
    w, h = (90, 130) if v == 0 else (150, 130)
    ink = (34, 28, 26)
    if v == 0:
        parts = [(ell(30, 106, 22, 16), ink, dict(kind="gladki", edge=1)), (rect(46, 10, 56, 106), ink),
                 (poly([(56, 10), (84, 44), (78, 60), (56, 36)]), ink)]
    else:
        parts = [(ell(30, 106, 22, 16), ink, dict(kind="gladki", edge=1)), (ell(110, 96, 22, 16), ink, dict(kind="gladki", edge=1)),
                 (rect(46, 14, 56, 106), ink), (rect(126, 4, 136, 96), ink), (poly([(46, 14), (136, 4), (136, 22), (46, 32)]), ink)]
    return Sprite(stack(w, h, parts, seed=720 + v), f"nuta-{v}", rim=2, clean=False)


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
def ramka(w=620, h=280, b=22):
    """Złota rama zdjęcia rodzinnego z pustym środkiem (gag „normal family” w Joplin)."""
    zl = (206, 168, 84)
    parts = [(rect(0, 0, w, b), zl, dict(edge=2)), (rect(0, h - b, w, h), zl, dict(edge=2)), (rect(0, 0, b, h), zl, dict(edge=2)),
             (rect(w - b, 0, w, h), zl, dict(edge=2))]
    return Sprite(stack(w, h, parts, seed=905), "ramka-zdjecia", rim=2, clean=False, crop=False)


@lru_cache(None)
def wstega_luk(txt="HAPPY EVER AFTER", w=520, h=160, cx=260, cy=232, rx=205, ry=205, a0=0.21, a1=0.79, size=29):
    """Wstęga po łuku z napisem (ślub Bonnie i Roya: „HAPPY EVER AFTER” pod łukiem z kwiatów; marker reżysera 19.11).
    Łuk to elipsa o środku (cx, cy); a0..a1 — część półokręgu (w ułamkach π) od lewej do prawej. Litery stoją wzdłuż łuku."""
    from PIL import ImageChops, ImageFont
    ss = 2
    pt = lambda a, r=0.0: (cx - (rx + r) * math.cos(math.pi * a), cy - (ry + r) * math.sin(math.pi * a))

    def band(d, s_):
        n = 80
        aa = [a0 - 0.03 + (a1 - a0 + 0.06) * i / n for i in range(n + 1)]
        d.polygon([(x * s_, y * s_) for x, y in [pt(a, 22) for a in aa] + [pt(a, -22) for a in aa[::-1]]], fill=255)
    im = stack(w, h, [(band, (240, 228, 204), dict(kind="gladki", edge=3, contrast=1.2))], seed=901)
    # litery: równo po długości łuku, wyśrodkowane
    f = ImageFont.truetype(FONT_PL, size * ss, index=PL_IDX)
    szer = [f.getlength(ch) / ss + 3 for ch in txt]
    aa = np.linspace(a0, a1, 2000)
    pts = np.array([pt(a) for a in aa])
    dl = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    start = (dl[-1] - sum(szer)) / 2
    mask = Image.new("L", (w * ss, h * ss), 0)
    pos = start
    for ch, sw in zip(txt, szer):
        c = pos + sw / 2
        pos += sw
        if ch == " ":
            continue
        a = float(np.interp(c, dl, aa))
        x, y = pt(a)
        dx, dy = rx * math.sin(math.pi * a), -ry * math.cos(math.pi * a)
        kat = -math.degrees(math.atan2(dy, dx))
        L = Image.new("L", (size * ss * 2, size * ss * 2), 0)
        ImageDraw.Draw(L).text((size * ss, size * ss), ch, font=f, fill=255, anchor="mm")
        L = L.rotate(kat, resample=Image.BICUBIC)
        ox, oy = int(x * ss - size * ss), int(y * ss - size * ss)
        tlo = Image.new("L", mask.size, 0)
        tlo.paste(L, (ox, oy))
        mask = ImageChops.lighter(mask, tlo)
    litery = paper(mask.resize((w, h), Image.LANCZOS), (168, 40, 48), "gladki", seed=902, contrast=1.1)
    im = glue(im, litery, shadow=0.25, off=(1, 1), soft=1)
    return Sprite(im, f"wstega-{txt}", rim=2, clean=False, crop=False)  # bez przycięcia: w=520 to cały arkusz łuku


@lru_cache(None)
def sylwetka_w_oknie(key, reka, rzecz=None, ar=0.9):
    """Czarna sylwetka postaci za szybą (głowa, ramiona i ręka z rzeczą), przycięta do prostokąta o proporcjach okna ar
    (szerokość / wysokość) — rysuje się w obrębie otworu (1.1). Marker reżysera 23.11, ujęcie „shreveport”."""
    im = sylwetka(key, rece=(reka, 15), rzecz=rzecz)
    ref = sylwetka(key, rece=(30, 15), rzecz=rzecz)  # ta sama ramka dla każdej pozy ręki: postać nie zmienia wielkości
    rw, rh = ref.size
    cw = int(rh * 0.62 * ar)
    ch = int(cw / ar)
    w_, h_ = im.size
    x0 = int(rw / 2 - cw / 2)  # od lewej krawędzi (plecy) — ręka wyciągnięta w prawo nie przesuwa postaci
    y0 = h_ - rh  # wyrównanie do stóp: ręka w górze nie przesuwa głowy
    can = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    can.alpha_composite(im.crop((max(0, x0), max(0, y0), min(w_, x0 + cw), min(h_, y0 + ch))), (max(0, -x0), max(0, -y0)))
    return Sprite(can, f"sylw-okno-{key}-{reka}-{rzecz}", rim=1, clean=False)


@lru_cache(None)
def zdjecie_pajacyk(faza, w=420, h=320):
    """Zdjęcie Bonnie, która na nim robi pajacyka (uwaga reżysera 23.11, ujęcie 84): faza 0 — ręce w dół, 1 — ręce w górę
    i podskok. Ta sama odbitka co zdjecie_bonnie (biała ramka, sepia)."""
    im = Image.new("RGBA", (w, h), (244, 240, 230, 255))
    foto = Image.new("RGBA", (w - 40, h - 40), (150, 146, 138, 255))
    body = sylwetka("bonnie", rece=(170, 170) if faza else (28, 28), kolor=True)
    bh = int((h - 50) * (0.86 if faza else 0.8))
    body = body.resize((int(body.width * bh / body.height), bh), Image.LANCZOS)
    foto.alpha_composite(body, (int((w - 40) / 2 - body.width / 2), (h - 40) - bh + 10 - (22 if faza else 0)))
    g = np.asarray(foto.convert("L"), np.float32)
    sep = np.dstack([g * 1.05, g * 0.95, g * 0.8, np.full_like(g, 255)]).clip(0, 255).astype(np.uint8)
    im.alpha_composite(Image.fromarray(sep, "RGBA"), (20, 20))
    return Sprite(im, f"zdjecie-pajacyk-{faza}", rim=2, clean=False)


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


@lru_cache(None)
def platek(kolor=(244, 200, 210)):
    """Płatek kwiatu (spadające płatki na cmentarzu w Alto, kwitnące drzewa w Grapevine)."""
    return Sprite(stack(40, 24, [(ell(20, 12, 18, 9), kolor)], seed=780), f"platek-{kolor}", rim=1, clean=False)


@lru_cache(None)
def teczka_akt(txt="BONNIE & CLYDE"):
    """Duża teczka akt Hamera z dużym napisem (markery reżysera 23.11, ujęcie „koniec”: „wjeżdża ta duża teczka z dużym napisem
    Bonnie & Clyde”, „większa teczka”)."""
    w, h = 420, 210
    parts = [(rect(8, 26, 412, 206), (196, 160, 100), dict(edge=2)), (rect(8, 10, 150, 36), (196, 160, 100)),
             (rect(40, 78, 380, 158), (240, 232, 214), dict(edge=2)),
             (glyphs(tr(txt), 40, FONT_PL, PL_IDX, (210, 120), "mm"), (120, 30, 26), dict(kind="gladki", rough=0.5))]
    return Sprite(stack(w, h, parts, seed=71), f"teczka-akt-{txt}", rim=2, clean=False)


@lru_cache(None)
def karta_akt(txt="BARROW · PARKER"):
    """Karta z aktami (marker reżysera 23.11: „powoli zjeżdża karta z ich aktami”): biała karta, nagłówek, wiersze pisma."""
    w, h = 300, 200
    parts = [(rect(4, 4, 296, 196), (244, 240, 228), dict(edge=2)), (rect(4, 4, 296, 44), (210, 70, 60)),
             (glyphs(tr(txt), 24, FONT_PL, PL_IDX, (150, 24), "mm"), (250, 246, 236), dict(kind="gladki", rough=0.4))]
    parts += [(rect(24, 62 + 22 * k, 276 - 40 * (k % 3), 66 + 22 * k), (90, 84, 78)) for k in range(6)]
    return Sprite(stack(w, h, parts, seed=73), f"karta-akt-{txt}", rim=2, clean=False)


@lru_cache(None)
def gra_postac(kto):
    """Pikselowa postać z gry (marker reżysera 23.11, ujęcie „gra”: „pikselowa Bonnie / Clyde wyskakuje z auta”)."""
    px = {"bonnie": ["..RRR.", ".RRRR.", ".YYYY.", ".YSSY.", ".YSSY.", "..BB..", ".BBBB.", "BBBBBB", ".BBBB.", ".S..S."],
          "clyde": ["..DD..", ".DDDD.", "DDDDDD", ".SSSS.", ".SSSS.", "..NN..", ".NNNN.", "NNNNNN", ".NNNN.", ".N..N."]}[kto]
    kol = {"R": (230, 60, 70), "Y": (250, 220, 80), "B": (80, 160, 240), "S": (250, 200, 160), "D": (50, 50, 60), "N": (60, 90, 200)}
    c = 24
    im = Image.new("RGBA", (len(px[0]) * c, len(px) * c), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y, row in enumerate(px):
        for x, ch in enumerate(row):
            if ch in kol:
                d.rectangle([x * c, y * c, x * c + c - 2, y * c + c - 2], fill=kol[ch] + (255,))
    return Sprite(im, f"gra-postac-{kto}", rim=0, clean=False)


@lru_cache(None)
def gra_piksele(pusty=False):
    """Gra wideo 2026 na ekranie kina: pikselowe auto i para uciekinierów w jaskrawych kolorach (pusty — auto bez nich)."""
    px = [
        "..........RRRRRR..........",
        ".........R.YY.BB.R........" if not pusty else ".........R.......R........",
        "........R..YY.BB..R......." if not pusty else "........R.........R.......",
        "..KKKKKKKKKKKKKKKKKKKKK...",
        ".KKKKKKKKKKKKKKKKKKKKKKKW.",
        ".KKKKKKKKKKKKKKKKKKKKKKKK.",
        "...GG............GG.......",
        "..GGGG..........GGGG......",
        "...GG............GG.......",
    ]
    kol = {"R": (230, 60, 70), "Y": (250, 220, 80), "B": (80, 160, 240), "K": (40, 200, 230), "W": (255, 250, 200), "G": (60, 60, 70)}
    c = 24
    im = Image.new("RGBA", (len(px[0]) * c, len(px) * c), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y, row in enumerate(px):
        for x, ch in enumerate(row):
            if ch in kol:
                d.rectangle([x * c, y * c, x * c + c - 2, y * c + c - 2], fill=kol[ch] + (255,))
    return Sprite(im, f"gra-piksele{'-pusty' if pusty else ''}", rim=0, clean=False)


# =====================================================================================================================
# ---------- część kaukaska (film „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune”, 28.11.2026) ----------
# =====================================================================================================================

JEZYK = "en"
CZERN = (34, 32, 34)  # czarna czerkieska muridów
SREBRO = (206, 206, 198)
KOSC = (232, 222, 196)  # gazyry: kościane główki ładunków

BAZA.update(gazyry=False, kindzal=False, dluga=False, epolety=None, wiek=None)

_kapelusz_bc = _kapelusz


def _kapelusz(s, parts):  # noqa: F811 — nakrycia głowy tego filmu, reszta jak w „Bonnie and Clyde”
    k, c = s["kapelusz"], s["kapelusz_kolor"]
    futro = dict(kind="gnieciony", contrast=1.5, edge=2)
    if k == "papacha":  # wysoka futrzana czapa górali
        parts += [(poly([(110, 102), (196, 102), (200, 56), (188, 40), (152, 34), (118, 40), (106, 56)]), c, futro),
                  (poly([(118, 44), (188, 44), (184, 54), (122, 54)]), _shade(c, 0.75))]
    elif k == "turban":  # papacha owinięta białym turbanem — znak imama (portrety Szamila z 1859)
        parts += [(poly([(116, 92), (190, 92), (192, 40), (180, 26), (152, 22), (126, 26), (114, 40)]), c, futro),
                  (poly([(104, 104), (202, 104), (206, 84), (198, 62), (152, 56), (108, 62), (100, 84)]), (244, 240, 228),
                   dict(kind="gladki", contrast=0.7, edge=2)),
                  (poly([(108, 80), (200, 70), (202, 78), (110, 90)]), (222, 216, 200)),
                  (poly([(102, 96), (204, 86), (204, 94), (104, 104)]), (222, 216, 200))]
    elif k == "furazka":  # biała letnia czapka piechoty rosyjskiej z daszkiem
        parts += [(poly([(108, 70), (200, 64), (196, 96), (114, 98)]), c, dict(edge=2)),
                  (rect(112, 86, 196, 98), (170, 40, 36)),
                  (poly([(162, 96), (222, 102), (216, 110), (170, 108)]), (24, 22, 22))]
    elif k == "czepiec":  # gruzińska lechaki: biały welon na głowie, spływa za plecy, aksamitna opaska z perłami na czole
        parts += [(poly([(108, 98), (112, 70), (138, 56), (176, 58), (196, 76), (198, 94), (176, 86), (124, 94), (118, 150),
                         (114, 240), (96, 272), (88, 210), (96, 140)]), (248, 246, 240), dict(kind="gladki", contrast=0.5, edge=2)),
                  (poly([(110, 96), (200, 88), (200, 100), (112, 108)]), c)]
    elif k == "kapelusz_damski":  # kapelusz z szerokim rondem (pisarka, 1960)
        parts += [(poly([(118, 92), (190, 92), (182, 62), (152, 54), (124, 62)]), c, dict(edge=2)),
                  (ell(153, 94, 66, 10), c, dict(edge=2)), (rect(118, 82, 190, 92), _shade(c, 0.7))]
    else:
        _kapelusz_bc(s, parts)


_korpus_img_bc = _korpus_img


def _korpus_img(s, seed_spec=None):  # noqa: F811 — dokłada długą suknię, gazyry, kindżał i epolety
    im = _korpus_img_bc(s, seed_spec)
    if not (s["dluga"] or s["gazyry"] or s["kindzal"] or s["epolety"]):
        return im
    k = s["szer"]
    w, h = im.size
    L = s["nogi"]
    X = lambda x: w / 2 + (x - 150) * k
    Y = lambda y: y + L if y >= BIODRO else y
    parts = []
    if s["dluga"]:  # suknia do ziemi (XIX w.): zakrywa nogi, spod spodu tylko czubki butów
        parts += [(poly([(X(98), Y(336)), (X(202), Y(336)), (X(236), Y(670)), (X(64), Y(670))]), s["dol"], dict(edge=2, shade=0.18)),
                  (poly([(X(96), Y(664)), (X(132), Y(664)), (X(132), Y(676)), (X(92), Y(676))]), s["buty"])]
    if s["gazyry"]:  # ładownice z kościanymi główkami na piersi czerkieski, po obu stronach
        for x0 in (100, 172):
            parts.append((poly([(X(x0), 226), (X(x0 + 30), 226), (X(x0 + 30), 292), (X(x0), 292)]), _shade(s["gora"], 0.8)))
            for n in range(5):
                parts.append((rect(X(x0 + 3 + n * 5.4), 214, X(x0 + 7.4 + n * 5.4), 234), KOSC, dict(kind="gladki", rough=0.4)))
    if s["kindzal"]:  # kindżał przy pasie, na środku przodu: rękojeść z głowicą, pochwa ze srebrnym okuciem
        parts += [(poly([(X(150), 330), (X(162), 330), (X(162), 352), (X(150), 352)]), (60, 46, 38)),
                  (ell(X(156), 326, 9, 7), SREBRO),
                  (poly([(X(147), 352), (X(165), 352), (X(162), 452), (X(156), 466), (X(150), 452)]), (40, 34, 30), dict(edge=1)),
                  (poly([(X(149), 438), (X(163), 438), (X(156), 466)]), SREBRO)]
    if s["epolety"]:
        for x0 in (90, 176):
            parts += [(poly([(X(x0), 204), (X(x0 + 36), 204), (X(x0 + 40), 220), (X(x0 - 4), 220)]), s["epolety"]),
                      (rect(X(x0 - 2), 218, X(x0 + 38), 226), _shade(s["epolety"], 0.8))]
    over_ = stack(w, h, parts, seed=37 + len(parts))
    im = im.copy()
    im.alpha_composite(over_)
    return im


LALKI.update({
    # Szamil: orli profil, czarna broda (siwa od kapitulacji), papacha z białym turbanem, czarna czerkieska z gazyrami, kindżał
    "szamil": dict(fryzura="krotkie", wlosy=(40, 32, 28), broda=True, wasy=True, kapelusz="turban", kapelusz_kolor=(46, 40, 36),
                   stroj="plaszcz", gora=CZERN, dol=(46, 42, 40), koszula=(110, 84, 60), krawat=None, buty=(28, 24, 22),
                   gazyry=True, kindzal=True, pas=(70, 64, 56)),
    "szamil_stary": dict(fryzura="krotkie", wlosy=(214, 210, 204), broda=True, wasy=True, kapelusz="turban",
                         kapelusz_kolor=(46, 40, 36), stroj="plaszcz", gora=CZERN, dol=(46, 42, 40), koszula=(110, 84, 60),
                         krawat=None, buty=(28, 24, 22), gazyry=True, pas=(70, 64, 56)),
    "murid": dict(wlosy=(44, 34, 30), broda=True, wasy=True, kapelusz="papacha", kapelusz_kolor=(36, 32, 30), stroj="plaszcz",
                  gora=CZERN, dol=(40, 38, 36), koszula=(96, 74, 56), krawat=None, buty=(28, 24, 22), gazyry=True, kindzal=True,
                  pas=(70, 64, 56)),
    "murid2": dict(wlosy=(70, 50, 36), wasy=True, kapelusz="papacha", kapelusz_kolor=(60, 52, 46), stroj="plaszcz",
                   gora=(58, 54, 56), dol=(40, 38, 36), koszula=(120, 92, 64), krawat=None, buty=(28, 24, 22), gazyry=True,
                   kindzal=True, pas=(70, 64, 56)),
    "murid3": dict(wlosy=(30, 26, 24), broda=True, wasy=True, kapelusz="papacha", kapelusz_kolor=(196, 190, 180), stroj="plaszcz",
                   gora=(44, 42, 46), dol=(40, 38, 36), koszula=(96, 74, 56), krawat=None, buty=(28, 24, 22), gazyry=True,
                   kindzal=True, pas=(70, 64, 56)),
    "ghazi": dict(wlosy=(40, 32, 28), wasy=True, kapelusz="papacha", kapelusz_kolor=(36, 32, 30), stroj="plaszcz",
                  gora=(84, 80, 86), dol=(40, 38, 36), koszula=(120, 92, 64), krawat=None, buty=(28, 24, 22), gazyry=True,
                  kindzal=True, pas=(70, 64, 56)),
    "mysliwy": dict(wlosy=(80, 60, 44), broda=True, kapelusz="papacha", kapelusz_kolor=(150, 140, 126), stroj="plaszcz",
                    gora=(120, 92, 62), dol=(90, 72, 54), koszula=(170, 150, 120), krawat=None, buty=(50, 38, 30), pas=(70, 60, 50)),
    # Dżamaluddin: chłopiec w papasze (1839), kadet, oficer z wąsikiem (ta sama twarz), po wymianie czarna czerkieska
    "dzamal_maly": dict(wlosy=(40, 32, 28), kapelusz="papacha", kapelusz_kolor=(60, 50, 44), stroj="plaszcz", gora=(126, 92, 60),
                        dol=(80, 64, 50), koszula=(200, 180, 150), krawat=None, buty=(40, 32, 26), szer=0.92),
    "dzamal_kadet": dict(wlosy=(40, 32, 28), fryzura="zaczesane", kapelusz="czapka", kapelusz_kolor=(40, 46, 70), stroj="mundur",
                         gora=(40, 46, 70), dol=(40, 46, 70), koszula=(200, 40, 40), krawat=None, buty=(24, 22, 22), pas=(236, 232, 220),
                         szer=0.94),
    "dzamal_oficer": dict(wlosy=(40, 32, 28), fryzura="zaczesane", wasy=True, kapelusz="czapka", kapelusz_kolor=(40, 58, 48),
                          stroj="mundur", gora=(40, 58, 48), dol=(40, 46, 52), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22),
                          epolety=GOLD, pas=(236, 232, 220)),
    "dzamal_gorski": dict(wlosy=(40, 32, 28), fryzura="zaczesane", wasy=True, kapelusz="papacha", kapelusz_kolor=(36, 32, 30),
                          stroj="plaszcz", gora=CZERN, dol=(40, 38, 36), koszula=(96, 74, 56), krawat=None, buty=(28, 24, 22),
                          gazyry=True, pas=(70, 64, 56)),
    # strona rosyjska
    "zolnierz": dict(wlosy=(110, 84, 56), wasy=True, kapelusz="furazka", kapelusz_kolor=(236, 234, 226), stroj="mundur",
                     gora=(232, 228, 216), dol=(60, 70, 64), koszula=(200, 50, 44), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30)),
    "zolnierz2": dict(wlosy=(150, 110, 70), kapelusz="furazka", kapelusz_kolor=(236, 234, 226), stroj="mundur", gora=(70, 88, 70),
                      dol=(60, 70, 64), koszula=(200, 50, 44), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30)),
    "oficer_ros": dict(wlosy=(90, 70, 50), wasy=True, kapelusz="czapka", kapelusz_kolor=(40, 58, 48), stroj="mundur",
                       gora=(40, 58, 48), dol=(40, 46, 52), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD),
    "bariatinski": dict(wlosy=(120, 96, 70), wasy=True, kapelusz="czapka", kapelusz_kolor=(236, 234, 226), stroj="mundur",
                        gora=(36, 52, 44), dol=(170, 40, 40), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD,
                        pas=GOLD, szer=1.06),
    "car": dict(fryzura="lysy", wlosy=(140, 110, 80), wasy=True, stroj="mundur", gora=(36, 46, 76), dol=(236, 232, 220),
                koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD, pas=GOLD, odznaka=True, szer=1.04),
    # warianty do grup — w jednym kadrze żadne dwie postacie nie są tą samą wycinanką (Wytyczne 1.6)
    "murid4": dict(wlosy=(90, 64, 44), broda=True, kapelusz="papacha", kapelusz_kolor=(110, 96, 84), stroj="plaszcz", gora=(70, 60, 54),
                   dol=(40, 38, 36), koszula=(140, 110, 70), krawat=None, buty=(28, 24, 22), gazyry=True, kindzal=True, pas=(70, 64, 56),
                   szer=1.06),
    "murid5": dict(wlosy=(24, 22, 22), wasy=True, kapelusz="papacha", kapelusz_kolor=(24, 22, 22), stroj="plaszcz", gora=(96, 90, 80),
                   dol=(40, 38, 36), koszula=(80, 70, 60), krawat=None, buty=(28, 24, 22), gazyry=True, kindzal=True, pas=(70, 64, 56),
                   szer=0.94),
    "zolnierz3": dict(wlosy=(60, 46, 36), broda=True, wasy=True, kapelusz="furazka", kapelusz_kolor=(236, 234, 226), stroj="mundur",
                      gora=(232, 228, 216), dol=(60, 70, 64), koszula=(200, 50, 44), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30),
                      szer=1.05),
    "zolnierz4": dict(wlosy=(190, 150, 100), kapelusz="furazka", kapelusz_kolor=(236, 234, 226), stroj="mundur", gora=(70, 88, 70),
                      dol=(60, 70, 64), koszula=(200, 50, 44), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30), szer=0.95),
    "zolnierz5": dict(wlosy=(40, 32, 28), wasy=True, kapelusz="furazka", kapelusz_kolor=(236, 234, 226), stroj="mundur", gora=(226, 224, 214),
                      dol=(60, 70, 64), koszula=(200, 50, 44), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30), szer=0.98),
    "zolnierz6": dict(wlosy=(120, 90, 60), broda=True, kapelusz="furazka", kapelusz_kolor=(236, 234, 226), stroj="mundur", gora=(64, 80, 66),
                      dol=(60, 70, 64), koszula=(200, 50, 44), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30), szer=1.03),
    "oficer_ros2": dict(wlosy=(60, 46, 36), wasy=True, broda=True, kapelusz="czapka", kapelusz_kolor=(236, 234, 226), stroj="mundur",
                        gora=(232, 228, 216), dol=(40, 46, 52), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD),
    "oficer_ros3": dict(wlosy=(170, 130, 90), kapelusz="czapka", kapelusz_kolor=(40, 46, 70), stroj="mundur", gora=(40, 46, 70),
                        dol=(40, 46, 52), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=SREBRO, szer=1.05),
    "oficer_ros4": dict(wlosy=(200, 196, 190), wasy=True, fryzura="lysy", stroj="mundur", gora=(40, 58, 48), dol=(170, 40, 40),
                        koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD, szer=1.08),
    "dama2": dict(kobieta=True, wlosy=(60, 44, 32), fryzura="kok", stroj="sukienka", gora=(150, 170, 200), dol=(150, 170, 200),
                  kolnierzyk=(250, 244, 232), dluga=True, buty=(60, 40, 30)),
    "dama3": dict(kobieta=True, wlosy=(210, 170, 110), fryzura="fala", stroj="sukienka", gora=(196, 120, 130), dol=(196, 120, 130),
                  kolnierzyk=(250, 244, 232), dluga=True, buty=(60, 40, 30)),
    "woznica": dict(wlosy=(110, 84, 56), broda=True, kapelusz="kaszkiet", kapelusz_kolor=(80, 64, 50), stroj="plaszcz",
                    gora=(110, 86, 60), dol=(70, 60, 50), koszula=(200, 180, 150), krawat=None, buty=(40, 32, 26)),
    # Cinandali: księżne w czepcach (lechaki) i długich sukniach, dzieci, guwernantka
    "anna": dict(kobieta=True, wlosy=(40, 30, 26), fryzura="fala", kapelusz="czepiec", kapelusz_kolor=(40, 30, 40), stroj="sukienka",
                 gora=(112, 36, 44), dol=(112, 36, 44), kolnierzyk=(240, 232, 214), dluga=True, buty=(40, 30, 26)),
    "warwara": dict(kobieta=True, wlosy=(50, 38, 30), fryzura="fala", kapelusz="czepiec", kapelusz_kolor=(40, 30, 40), stroj="sukienka",
                    gora=(78, 76, 92), dol=(78, 76, 92), kolnierzyk=(240, 232, 214), dluga=True, buty=(40, 30, 26)),
    "guwernantka": dict(kobieta=True, wlosy=(120, 90, 60), fryzura="kok", stroj="sukienka", gora=(60, 60, 64), dol=(60, 60, 64),
                        kolnierzyk=(244, 240, 230), dluga=True, buty=(40, 30, 26)),
    "dziecko_g": dict(kobieta=True, wlosy=(60, 44, 32), fryzura="loki", stroj="sukienka", gora=(236, 226, 206), dol=(236, 226, 206),
                      kolnierzyk=(250, 246, 236), pas=(112, 36, 44), szer=0.92),
    "dziecko_g2": dict(wlosy=(60, 44, 32), stroj="koszula", koszula=(200, 214, 226), gora=(200, 214, 226), dol=(60, 66, 80),
                       krawat=None, buty=(40, 30, 26), szer=0.92),
    "dama": dict(kobieta=True, wlosy=(150, 110, 70), fryzura="kok", stroj="sukienka", gora=(222, 196, 168), dol=(222, 196, 168),
                 kolnierzyk=(250, 244, 232), dluga=True, buty=(60, 40, 30)),
    # 1960–1965: pisarka i autor Diuny
    "blanch": dict(kobieta=True, wlosy=(110, 76, 50), fryzura="fala", kapelusz="kapelusz_damski", kapelusz_kolor=(60, 84, 110),
                   stroj="sukienka", gora=(92, 116, 140), dol=(92, 116, 140), kolnierzyk=(240, 236, 226)),
    "herbert": dict(wlosy=(110, 84, 64), fryzura="krotkie", broda=True, wasy=True, okulary=True, stroj="koszula",
                    koszula=(150, 120, 90), gora=(150, 120, 90), dol=(70, 66, 62), krawat=None, buty=(40, 32, 26)),
})


# ---------- teksty na kartach (maszynopis) ----------

FONT_MASZ = next((p for p in ("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", "C:/Windows/Fonts/courbd.ttf",
                              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf") if Path(p).exists()), FONT_PL)


def _maszynopis(lines, size, w, h, kolor=INK, y0=None):
    """Kształt tekstu z maszyny do pisania (wiersze wyśrodkowane)."""
    f = ImageFont.truetype(FONT_MASZ, int(size * 2))
    lh = size * 1.35
    y0 = h / 2 - lh * (len(lines) - 1) / 2 if y0 is None else y0

    def draw(d, sc):
        for n, ln in enumerate(lines):
            d.text((w / 2 * sc, (y0 + n * lh) * sc), ln, font=ImageFont.truetype(FONT_MASZ, int(size * sc)), fill=255, anchor="mm")
    return draw


from PIL import ImageFont  # noqa: E402


@lru_cache(None)
def karta(tekst, podpis="", stara=False, w=960, h=300):
    """Karta z maszynopisem: biała (Diuna, 1965) albo pożółkła z plamami (książka z 1960). tekst — wiersze rozdzielone „|”."""
    tlo = (226, 204, 150) if stara else (246, 242, 232)
    lines = tekst.split("|")
    parts = [(poly([(6, 8), (w - 8, 4), (w - 4, h - 8), (4, h - 4)]), tlo, dict(kind="gladki", edge=4, contrast=1.4 if stara else 0.8)),
             (_maszynopis(lines, 42, w, h - 50), (36, 30, 28), dict(kind="gladki", rough=0.4))]
    if podpis:
        parts.append((_maszynopis([podpis], 30, w, h, y0=h - 46), (110, 60, 40), dict(kind="gladki", rough=0.4)))
    if stara:
        parts += [(ell(w * 0.82, h * 0.22, 40, 26), _shade(tlo, 0.88), dict(kind="gnieciony")),
                  (ell(w * 0.12, h * 0.78, 30, 20), _shade(tlo, 0.9), dict(kind="gnieciony"))]
    return Sprite(stack(w, h, parts, seed=len(tekst) + (7 if stara else 3)), f"karta-{tekst[:20]}-{stara}", rim=2, clean=False)


@lru_cache(None)
def slowo(txt, size=64, kolor=(244, 232, 200), farba=(46, 30, 24)):
    """Duża karta ze słowem z Diuny (KANLY, KINDJAL…) — zjeżdża na nitce jak zawieszka."""
    f = ImageFont.truetype(FONT_PL, size, index=PL_IDX)
    tw = int(f.getlength(txt) + 4 * len(txt))
    w, h = tw + 110, size + 70
    parts = [(poly([(6, 6), (w - 6, 4), (w - 4, h - 6), (4, h - 4)]), kolor, dict(kind="gladki", edge=4, contrast=1.2)),
             (poly([(16, 16), (w - 16, 14), (w - 14, h - 16), (14, h - 14)]), _shade(kolor, 0.9)),
             (glyphs(txt, size, FONT_PL, PL_IDX, (w / 2, h / 2 + 2), "mm"), farba, dict(kind="gladki", rough=0.5))]
    return Sprite(stack(w, h, parts, seed=len(txt) * 13), f"slowo-{txt}", rim=2, clean=False)


@lru_cache(None)
def okladka():
    """Okładka „The Sabres of Paradise · 1960”: płótno w kolorze wina, góry i dwie skrzyżowane szable (rysunek własny)."""
    w, h = 620, 860
    parts = [(rect(8, 8, w - 8, h - 8), (120, 40, 44), dict(kind="gladki", edge=5, contrast=1.1)),
             (rect(40, 40, w - 40, h - 40), (136, 50, 52)),
             (poly([(60, 640), (170, 470), (240, 540), (330, 400), (420, 520), (480, 450), (560, 640)]), (224, 204, 160)),
             (poly([(300, 420), (330, 400), (360, 425), (345, 440), (315, 438)]), (250, 246, 236)),
             (_band((150, 600), (470, 300), 12), SREBRO), (_band((470, 600), (150, 300), 12), SREBRO),
             (rect(132, 590, 176, 616), GOLD), (rect(444, 590, 488, 616), GOLD),
             (glyphs("THE SABRES", 58, FONT_PL, PL_IDX, (w / 2, 130), "mm"), (240, 222, 170)),
             (glyphs("OF PARADISE", 58, FONT_PL, PL_IDX, (w / 2, 200), "mm"), (240, 222, 170)),
             (glyphs("1960", 50, FONT_PL, PL_IDX, (w / 2, 740), "mm"), (240, 222, 170))]
    return Sprite(stack(w, h, parts, seed=71), "okladka", rim=2, clean=False)


# ---------- krajobraz: Kaukaz, pustynia ----------

GORY = {  # (wysokość arkusza, wierzchołki x co 100 px jako wysokość, barwa skały, śnieg)
    "dal": (520, [120, 300, 180, 420, 260, 480, 300, 360, 200, 440, 280, 380, 160, 330, 220, 400, 260, 300, 180, 340, 200], (152, 162, 180), 0.32),
    "srodek": (460, [90, 220, 140, 330, 200, 280, 380, 240, 160, 300, 210, 360, 190, 250, 320, 180, 260, 140, 230, 170, 110],
               (122, 112, 104), 0.25),
    "blisko": (360, [60, 140, 90, 200, 150, 120, 210, 170, 110, 190, 130, 220, 160, 120, 180, 100, 150, 90, 170, 120, 80], (98, 88, 78), 0.0),
}


@lru_cache(None)
def gory(which, seed=0):
    """Pasmo gór Kaukazu: postrzępione szczyty, na wyższych śnieg (biała bibuła); szerokość 2000."""
    h, szczyty, kolor, snieg = GORY[which]
    r = random.Random(seed + len(which))
    w = 2000
    pts = [(0, h)]
    for n, v in enumerate(szczyty):
        x = n * w / (len(szczyty) - 1)
        y = h - v * (h / 500) - r.uniform(-12, 12)
        pts.append((x, y))
        if n < len(szczyty) - 1:
            pts.append((x + 50, y + r.uniform(30, 90)))
    pts.append((w, h))
    parts = [(poly(pts), kolor, dict(edge=3, shade=0.18, contrast=1.1))]
    for n in range(1, len(pts) - 2, 2):
        x, y = pts[n]
        if snieg and (h - y) > h * (0.55 if which == "dal" else 0.62):
            parts.append((poly([(x - 46, y + 56), (x, y), (x + 46, y + 56), (x + 18, y + 44), (x - 4, y + 64), (x - 22, y + 48)]),
                          (246, 246, 244), dict(kind="gladki", contrast=0.6)))
        parts.append((poly([(x, y), (x + 14, y + 4), (pts[n + 1][0] - 10, pts[n + 1][1]), (pts[n + 1][0], pts[n + 1][1] + 160)]),
                      _shade(kolor, 0.86)))
    return Sprite(stack(w, h, parts, seed=seed + 300), f"gory-{which}-{seed}", rim=3, clean=False)


@lru_cache(None)
def wydma(v=0):
    """Wydma z piasku (Arrakis po lewej stronie sceny): miękki grzbiet, jasna grań, cień po zawietrznej."""
    w, h = 1300, 420
    r = random.Random(v)
    top = [(x, 230 - 150 * math.exp(-((x - 520 - 60 * v) / 300) ** 2) + 18 * math.sin(x / 140 + v) + r.uniform(-3, 3)) for x in range(0, w + 20, 20)]
    parts = [(poly(top + [(w, h), (0, h)]), (214, 172, 104), dict(kind="gladki", edge=3, contrast=0.9, shade=0.12))]
    grz = [p for p in top if p[0] >= 520 + 60 * v]
    parts.append((poly(grz + [(w, h), (520 + 60 * v, h)]), (186, 140, 80), dict(kind="gladki", contrast=0.7)))
    for n in range(5):
        y0 = 260 + n * 30
        parts.append((poly([(80 + n * 90, y0), (420 + n * 120, y0 - 14), (430 + n * 120, y0 - 8), (90 + n * 90, y0 + 6)]), (232, 196, 132)))
    return Sprite(stack(w, h, parts, seed=50 + v), f"wydma-{v}", rim=3, clean=False)


@lru_cache(None)
def skala():
    """Skała Achulgo: stromy blok nad zakolem rzeki, płaski szczyt pod twierdzę."""
    w, h = 760, 620
    parts = [(poly([(40, h), (90, 300), (150, 160), (220, 110), (560, 100), (630, 160), (680, 330), (720, h)]), (150, 128, 100),
              dict(edge=3, shade=0.2, contrast=1.2)),
             (poly([(150, 160), (220, 110), (300, 200), (260, 420), (180, h)]), (128, 108, 86)),
             (poly([(560, 100), (630, 160), (680, 330), (600, 300), (520, 160)]), (170, 148, 118))]
    for n in range(7):
        parts.append((_band((160 + n * 70, 260 + (n % 3) * 70), (200 + n * 70, 420 + (n % 2) * 80), 6), (118, 98, 78)))
    return Sprite(stack(w, h, parts, seed=61), "skala", rim=3, clean=False)


@lru_cache(None)
def twierdza():
    """Kamienna twierdza na skale: mury z blankami, dwie baszty, wąskie strzelnice."""
    w, h = 540, 260
    kam = (184, 166, 134)
    parts = [(poly([(20, h), (20, 120), (520, 120), (520, h)]), kam, dict(edge=2, shade=0.15))]
    for x in range(20, 520, 40):
        parts.append((rect(x, 100, x + 24, 124), kam))
    for x0 in (40, 400):
        parts += [(rect(x0, 30, x0 + 100, h), _shade(kam, 0.94), dict(edge=2)), (poly([(x0 - 8, 36), (x0 + 108, 36), (x0 + 50, 0)]), (140, 110, 84))]
        for yy in (80, 150):
            parts.append((rect(x0 + 44, yy, x0 + 56, yy + 30), (50, 40, 34)))
    for x in range(170, 380, 60):
        parts.append((rect(x, 160, x + 10, 190), (50, 40, 34)))
    return Sprite(stack(w, h, parts, seed=63), "twierdza", rim=2, clean=False)


@lru_cache(None)
def aul(v=0):
    """Auł: kamienne domy z płaskimi dachami stopniami na zboczu, ciemne okienka, mały minaret."""
    r = random.Random(v)
    w, h = 900, 420
    parts = [(poly([(0, h), (0, 300), (300, 220), (600, 140), (900, 120), (900, h)]), (140, 122, 98), dict(edge=3, shade=0.15))]
    domy = []
    for n in range(9):
        x = 40 + n * 96 + r.uniform(-10, 10)
        y = 330 - n * 22 + r.uniform(-14, 14)
        dw, dh = r.uniform(80, 110), r.uniform(60, 90)
        domy.append((x, y, dw, dh))
    for x, y, dw, dh in domy:
        kol = _shade((196, 178, 148), r.uniform(0.86, 1.05))
        parts += [(rect(x, y - dh, x + dw, y), kol, dict(edge=2)), (rect(x - 4, y - dh - 8, x + dw + 4, y - dh + 2), _shade(kol, 0.75)),
                  (rect(x + dw * 0.3, y - dh * 0.6, x + dw * 0.3 + 12, y - dh * 0.6 + 16), (60, 46, 38))]
    mx = domy[5][0] + 40
    parts += [(rect(mx, 60, mx + 22, domy[5][1] - domy[5][3]), (214, 200, 170), dict(edge=2)), (poly([(mx - 6, 64), (mx + 28, 64), (mx + 11, 30)]), (120, 140, 110))]
    return Sprite(stack(w, h, parts, seed=80 + v), f"aul-{v}", rim=2, clean=False)


@lru_cache(None)
def rzeka(noc=False):
    """Rzeka górska: pas wody z jaśniejszymi falami (Achulgo nocą, Miczik w marcu)."""
    w, h = 2000, 170
    woda = (54, 74, 104) if noc else (98, 138, 156)
    parts = [(poly([(0, 30), (w, 10), (w, h), (0, h)]), woda, dict(kind="gladki", edge=2, contrast=0.8))]
    r = random.Random(3)
    for n in range(26):
        x, y = r.uniform(0, w), r.uniform(40, 150)
        parts.append((poly([(x, y), (x + 70, y - 6), (x + 140, y), (x + 70, y + 4)]), _shade(woda, 1.35)))
    return Sprite(stack(w, h, parts, seed=90 + noc), f"rzeka-{noc}", rim=2, clean=False)


@lru_cache(None)
def brzeg(strona=1):
    """Kamienisty brzeg z trawą (wymiana na rzece)."""
    w, h = 900, 200
    parts = [(poly([(0, 60), (900, 30), (900, h), (0, h)]), (128, 120, 92), dict(edge=2, shade=0.15))]
    r = random.Random(strona)
    for n in range(18):
        x, y = r.uniform(20, 880), r.uniform(70, 180)
        parts.append((ell(x, y, r.uniform(12, 30), r.uniform(8, 16)), (166, 158, 144)))
    im = stack(w, h, parts, seed=95 + strona)
    if strona < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return Sprite(im, f"brzeg-{strona}", rim=2, clean=False)


# ---------- Gruzja (Cinandali), Petersburg ----------

@lru_cache(None)
def dwor():
    """Dwór w Cinandali: dwupiętrowy, jasne mury, drewniany balkon z łukami, czerwony dach."""
    w, h = 820, 520
    sciana, drewno = (232, 220, 196), (130, 84, 54)
    parts = [(rect(40, 150, 780, h), sciana, dict(edge=2, shade=0.1)), (poly([(10, 160), (410, 40), (810, 160)]), (166, 70, 52), dict(edge=2)),
             (rect(40, 300, 780, 320), drewno), (rect(40, 300, 780, 312), _shade(drewno, 1.2))]
    for n in range(7):
        x = 80 + n * 100
        parts += [(poly([(x, 300), (x, 200), (x + 40, 178), (x + 80, 200), (x + 80, 300)]), (90, 120, 140)),
                  (rect(x - 8, 180, x + 2, 300), drewno), (rect(x + 82, 180, x + 92, 300), drewno)]
        parts.append((rect(x + 10, 360, x + 60, 460), (90, 120, 140)))
    for x in range(40, 780, 18):
        parts.append((rect(x, 270, x + 6, 300), drewno))
    return Sprite(stack(w, h, parts, seed=101), "dwor", rim=2, clean=False)


@lru_cache(None)
def winnica(v=0):
    """Rząd winorośli na palikach (zielone kiście, fioletowe grona)."""
    w, h = 1000, 220
    r = random.Random(v)
    parts = []
    for n in range(12):
        x = 30 + n * 82
        parts.append((rect(x - 3, 60, x + 3, h), (110, 80, 54)))
        for k in range(4):
            parts.append((ell(x + r.uniform(-30, 30), 70 + r.uniform(-30, 40), r.uniform(26, 40), r.uniform(20, 30)), _shade((88, 126, 64), r.uniform(0.85, 1.1))))
        parts.append((ell(x + 12, 112, 9, 14), (96, 50, 96)))
    parts.append((rect(0, 96, w, 100), (110, 80, 54)))
    return Sprite(stack(w, h, parts, seed=110 + v), f"winnica-{v}", rim=2, clean=False)


@lru_cache(None)
def mur(w=1400, h=120):
    """Kamienny mur (winnica w Cinandali)."""
    r = random.Random(7)
    parts = [(rect(0, 10, w, h), (170, 154, 126), dict(edge=2, shade=0.15))]
    for n in range(int(w / 60)):
        for row in range(2):
            x = n * 60 + (30 if row else 0) + r.uniform(-6, 6)
            parts.append((ell(x, 40 + row * 44, 26, 16), _shade((170, 154, 126), r.uniform(0.85, 1.1))))
    return Sprite(stack(w, h, parts, seed=120), "mur", rim=2, clean=False)


@lru_cache(None)
def iglice():
    """Panorama Petersburga: złote iglice (Admiralicja, Twierdza Pietropawłowska), kopuła, niskie fasady w śniegu."""
    w, h = 1600, 520
    fas = (214, 196, 164)
    parts = [(rect(0, 360, w, h), fas, dict(edge=2, shade=0.1))]
    for n in range(14):
        x = n * 115
        parts.append((rect(x + 10, 330 + (n % 3) * 10, x + 105, 360), _shade(fas, 0.9 + 0.05 * (n % 2))))
        for k in range(3):
            parts.append((rect(x + 20 + k * 28, 380, x + 34 + k * 28, 410), (90, 100, 120)))
    for cx, top in ((380, 20), (1180, 60)):
        parts += [(rect(cx - 50, 250, cx + 50, 362), (232, 214, 170), dict(edge=2)), (rect(cx - 22, 180, cx + 22, 252), GOLD),
                  (poly([(cx - 14, 182), (cx + 14, 182), (cx, top)]), GOLD)]
    parts += [(ell(800, 260, 90, 80), (196, 170, 100)), (rect(720, 260, 880, 362), (226, 210, 176), dict(edge=2)),
              (poly([(796, 184), (804, 184), (800, 130)]), GOLD)]
    parts.append((rect(0, 470, w, h), (244, 244, 240), dict(kind="gladki", contrast=0.5)))
    return Sprite(stack(w, h, parts, seed=130), "iglice", rim=2, clean=False)


@lru_cache(None)
def sala():
    """Sala balowa: jasna ściana, wysokie okna z zasłonami, kolumny, posadzka (tło na planie miasta)."""
    w, h = 2000, 900
    parts = [(rect(0, 0, w, h), (232, 214, 180), dict(kind="gladki", contrast=0.7))]
    for n in range(6):
        x = 120 + n * 330
        parts += [(rect(x, 140, x + 150, 620), (176, 196, 210)), (rect(x - 30, 120, x + 10, 640), (160, 40, 44)),
                  (rect(x + 140, 120, x + 180, 640), (160, 40, 44)), (rect(x + 230, 60, x + 290, 760), (244, 236, 220), dict(edge=2)),
                  (rect(x + 220, 60, x + 300, 90), GOLD), (rect(x + 220, 730, x + 300, 760), GOLD)]
    parts.append((rect(0, 760, w, h), (150, 110, 74)))
    for n in range(40):
        parts.append((poly([(n * 50, 760), (n * 50 + 25, 760), (n * 50 - 40, h), (n * 50 - 65, h)]), (130, 92, 62)))
    return Sprite(stack(w, h, parts, seed=140), "sala", rim=2, clean=False)


@lru_cache(None)
def zyrandol():
    w, h = 420, 320
    parts = [(rect(204, 0, 216, 90), GOLD), (ell(210, 170, 170, 40), GOLD, dict(edge=2)), (ell(210, 200, 120, 30), _shade(GOLD, 0.85))]
    for n in range(9):
        x = 50 + n * 40
        parts += [(rect(x - 4, 110, x + 4, 150), (250, 246, 236)), (ell(x, 104, 6, 10), (255, 210, 120))]
    for n in range(7):
        parts.append((ell(80 + n * 43, 240 + (n % 2) * 20, 6, 14), (220, 236, 246)))
    return Sprite(stack(w, h, parts, seed=141), "zyrandol", rim=2, clean=False)


# ---------- rekwizyty ----------

_REK_IMG = {}  # arkusze rekwizytów (PIL) — uklad.Ark liczy z nich punkty chwytu i dno (Wytyczne 1.28, 1.32)


def _rek(name, w, h, parts, seed=0, dziura=None):
    """Rekwizyt sklejony z kawałków; dziura — prostokąt (x0, y0, x1, y1) wycięty w arkuszu (okno, przez które widać to,
    co za rzeczą — Wytyczne 1.1)."""
    img = stack(w, h, parts, seed=seed or len(name) * 7)
    if dziura:
        a = img.getchannel("A")
        a.paste(0, tuple(int(v) for v in dziura))
        img.putalpha(a)
    _REK_IMG[name] = img
    return Sprite(img, f"kz-{name}", rim=2, clean=False)


def rek_kz_img(key):
    rek_kz(key)
    return _REK_IMG[key]


@lru_cache(None)
def rek_kz(key):
    """Rekwizyty tego filmu (arkusze w pikselach; kotwice podane przy użyciu w ujęciach)."""
    if key == "kindzal":  # pionowo, ostrzem w dół: głowica (0.5, 0.04)
        return _rek(key, 80, 420, [(ell(40, 16, 18, 14), SREBRO), (rect(30, 24, 50, 120), (70, 52, 40)), (rect(10, 116, 70, 132), SREBRO),
                                   (poly([(24, 132), (56, 132), (52, 360), (40, 414), (28, 360)]), (214, 218, 222), dict(kind="gladki")),
                                   (_band((40, 140), (40, 380), 3), (170, 176, 184))])
    if key == "karabin":  # karabin skałkowy z bagnetem, poziomo lufą w prawo; chwyt (0.3, 0.55) jak w poprzednich filmach
        return _rek(key, 520, 90, [(poly([(10, 44), (150, 36), (170, 60), (20, 70)]), (110, 76, 48), dict(edge=2)),
                                   (rect(150, 38, 420, 50), (58, 56, 58), dict(kind="gladki")), (rect(200, 50, 240, 58), (150, 120, 70)),
                                   (poly([(420, 42), (512, 40), (420, 48)]), (210, 214, 218), dict(kind="gladki"))])
    if key == "szabla":
        return _rek(key, 520, 90, [(rect(10, 34, 110, 54), (70, 52, 40)), (rect(100, 24, 116, 64), SREBRO),
                                   (poly([(116, 36), (360, 30), (480, 50), (510, 76), (470, 60), (360, 46), (116, 52)]), (214, 218, 222), dict(kind="gladki"))])
    if key == "choragiew":  # czarna chorągiew na drzewcu: drzewce (0.06, 1.0)
        return _rek(key, 360, 520, [(rect(14, 0, 26, 520), (110, 80, 54)), (ell(20, 8, 12, 12), SREBRO),
                                    (poly([(26, 24), (340, 40), (300, 120), (346, 200), (26, 190)]), (28, 26, 28), dict(edge=2, shade=0.2)),
                                    (ell(170, 110, 30, 30), (70, 120, 80))])
    if key == "flaga_biala":
        return _rek(key, 300, 420, [(rect(10, 0, 22, 420), (110, 80, 54)),
                                    (poly([(22, 18), (280, 30), (250, 90), (290, 150), (22, 140)]), (248, 246, 238), dict(kind="gladki", edge=2))])
    if key == "armata":
        return _rek(key, 420, 220, [(poly([(60, 90), (380, 40), (396, 76), (70, 130)]), (56, 56, 60), dict(kind="gladki", edge=2)),
                                    (ell(130, 160, 56, 56), (110, 80, 54)), (ell(130, 160, 18, 18), (70, 52, 40)),
                                    (poly([(40, 120), (260, 110), (250, 140), (30, 150)]), (120, 86, 56))])
    if key == "drabina":
        p = [(_band((20, 0), (40, 600), 12), (130, 96, 60)), (_band((120, 0), (140, 600), 12), (130, 96, 60))]
        p += [(_band((24 + k * 2, 30 + k * 60), (126 + k * 2, 30 + k * 60), 8), (150, 112, 72)) for k in range(10)]
        return _rek(key, 160, 600, p)
    if key == "tratwa":
        p = [(rect(0, 120, 520, 160), (150, 116, 72), dict(edge=2))] + [(rect(n * 52, 116, n * 52 + 6, 164), (120, 90, 56)) for n in range(10)]
        for x in (90, 250, 410):  # słomiane kukły w papachach
            p += [(poly([(x - 34, 122), (x + 34, 122), (x + 24, 40), (x - 24, 40)]), (210, 182, 110), dict(kind="gnieciony")),
                  (ell(x, 26, 22, 24), (220, 194, 120), dict(kind="gnieciony")), (rect(x - 24, -4, x + 24, 14), (40, 36, 34))]
        return _rek(key, 520, 170, [(f, c, *o) for f, c, *o in p])
    if key == "kibitka":
        return _rek(key, 620, 360, [(poly([(60, 230), (90, 70), (520, 70), (560, 230)]), (70, 60, 56), dict(edge=2, shade=0.2)),
                                    (rect(260, 110, 360, 180), (210, 200, 170)), (rect(40, 226, 580, 250), (100, 74, 50)),
                                    (ell(140, 290, 60, 60), (90, 66, 44)), (ell(480, 290, 60, 60), (90, 66, 44)),
                                    (ell(140, 290, 16, 16), (60, 44, 30)), (ell(480, 290, 16, 16), (60, 44, 30))])
    if key == "kibitka_okno":  # kibitka z otworem okna: twarz pasażera widać przez otwór (pasażer stoi za wozem)
        rama = (120, 100, 80)
        return _rek(key, 620, 360, [(poly([(60, 230), (90, 70), (520, 70), (560, 230)]), (70, 60, 56), dict(edge=2, shade=0.2)),
                                    (rect(250, 100, 370, 190), rama), (rect(40, 226, 580, 250), (100, 74, 50)),
                                    (ell(140, 290, 60, 60), (90, 66, 44)), (ell(480, 290, 60, 60), (90, 66, 44)),
                                    (ell(140, 290, 16, 16), (60, 44, 30)), (ell(480, 290, 16, 16), (60, 44, 30))],
                    dziura=(262, 112, 358, 178))
    if key == "woz":  # otwarty wóz z niską burtą: siedzący pasażerowie stoją za burtą, burta zasłania ich od pasa
        return _rek(key, 620, 300, [(rect(30, 120, 590, 200), (120, 86, 56), dict(edge=2, shade=0.2)),
                                    (rect(30, 112, 590, 124), (150, 110, 72)),
                                    (ell(140, 236, 60, 60), (90, 66, 44)), (ell(480, 236, 60, 60), (90, 66, 44)),
                                    (ell(140, 236, 16, 16), (60, 44, 30)), (ell(480, 236, 16, 16), (60, 44, 30))])
    if key == "ksiazka_ros":  # oprawiona w skórę książka (syn czyta po rosyjsku) — bez napisów; chwyt (24, 160)
        return _rek(key, 220, 300, [(rect(4, 4, 216, 296), (110, 64, 40), dict(edge=2, shade=0.15)), (rect(20, 20, 200, 280), (124, 74, 46)),
                                    (rect(20, 20, 200, 30), GOLD), (rect(20, 270, 200, 280), GOLD)])
    if key == "pioro":  # gęsie pióro: stalówka (0, 42), chwyt (170, 30)
        return _rek(key, 260, 70, [(poly([(40, 38), (92, 16), (170, 8), (236, 14), (256, 30), (238, 46), (164, 60), (92, 56)]), (236, 232, 222)),
                                   (_band((10, 40), (250, 30), 3), (200, 190, 170)), (poly([(0, 42), (16, 35), (20, 44)]), (40, 36, 34))])
    if key == "czerkieska":  # złożona czarna czerkieska z gazyrami (podawana z rąk do rąk); chwyt (20, 60)
        return _rek(key, 180, 120, [(poly([(10, 30), (170, 20), (176, 100), (14, 110)]), CZERN, dict(edge=2, shade=0.2))] +
                    [(rect(40 + n * 12, 28, 48 + n * 12, 50), KOSC, dict(kind="gladki")) for n in range(5)])
    if key == "sciana_okno":  # kamienna ściana domu w Wedeno z wyciętym oknem (otwór 300..520 × 150..330)
        r = random.Random(7)
        p = [(rect(0, 0, 900, 560), (170, 154, 126), dict(edge=2, shade=0.15))]
        for n in range(15):
            for row in range(9):
                x = n * 62 + (31 if row % 2 else 0) + r.uniform(-6, 6)
                p.append((ell(x, 30 + row * 62, 28, 18), _shade((170, 154, 126), r.uniform(0.85, 1.1))))
        p += [(rect(286, 136, 534, 150), (120, 86, 56)), (rect(286, 330, 534, 346), (120, 86, 56)),
              (rect(286, 136, 300, 346), (120, 86, 56)), (rect(520, 136, 534, 346), (120, 86, 56))]
        return _rek(key, 900, 560, p, dziura=(300, 150, 520, 330))
    if key == "namiot":
        return _rek(key, 300, 220, [(poly([(10, 220), (150, 10), (290, 220)]), (236, 232, 216), dict(kind="gladki", edge=2, shade=0.15)),
                                    (poly([(130, 220), (150, 120), (170, 220)]), (90, 80, 70))])
    if key == "brzoza":
        p = [(poly([(130, 600), (140, 160), (160, 160), (172, 600)]), (238, 236, 226), dict(kind="gladki"))]
        p += [(rect(138 + k % 2 * 10, 200 + k * 46, 152 + k % 2 * 10, 208 + k * 46), (40, 36, 34)) for k in range(8)]
        p += [(ell(150 + dx, 120 + dy, 80, 60), (110, 150, 80)) for dx, dy in ((-60, 30), (50, 20), (0, -20), (-20, 60), (70, 70))]
        return _rek(key, 320, 600, p)
    if key == "wielblad":
        return _rek(key, 440, 380, [(ell(220, 170, 130, 70), (196, 160, 110), dict(edge=2)), (ell(190, 110, 50, 40), (196, 160, 110)),
                                    (ell(260, 110, 46, 36), (196, 160, 110)), (_band((330, 160), (390, 70), 34), (196, 160, 110)),
                                    (ell(400, 64, 30, 18), (196, 160, 110))] +
                    [(_band((x, 220), (x, 372), 16), (180, 146, 100)) for x in (130, 170, 280, 320)])
    if key == "worek":
        return _rek(key, 160, 180, [(poly([(30, 60), (130, 60), (150, 170), (10, 170)]), (184, 168, 140), dict(edge=2)),
                                    (rect(60, 40, 100, 64), (150, 130, 100)), (glyphs("₽", 40, FONT_PL, PL_IDX, (80, 120), "mm"), (90, 70, 50))])
    if key == "perly":
        return _rek(key, 260, 120, [(ell(20 + n * 22, 20 + 70 * math.sin(n / 10 * math.pi), 10, 10), (246, 242, 232), dict(kind="gladki"))
                                    for n in range(11)])
    if key == "perla":
        return _rek(key, 24, 24, [(ell(12, 12, 10, 10), (246, 242, 232), dict(kind="gladki"))])
    if key == "swieca":  # knot na górze: (0.5, 0.0)
        return _rek(key, 90, 240, [(rect(30, 20, 60, 200), (244, 236, 214), dict(kind="gladki")), (rect(10, 196, 80, 220), (150, 120, 70)),
                                   (rect(43, 0, 47, 22), (40, 34, 30))])
    if key == "maszyna":
        return _rek(key, 420, 240, [(poly([(30, 230), (60, 110), (360, 110), (390, 230)]), (50, 50, 54), dict(kind="gladki", edge=2)),
                                    (rect(70, 70, 350, 112), (40, 40, 44)), (rect(90, 10, 330, 80), (246, 242, 232))] +
                    [(ell(90 + k * 26, 170 + (k % 2) * 24, 10, 10), (220, 214, 200)) for k in range(10)])
    if key == "stol_niski":
        return _rek(key, 360, 120, [(rect(10, 20, 350, 44), (120, 84, 54), dict(edge=2)), (rect(30, 44, 50, 120), (100, 70, 46)),
                                    (rect(310, 44, 330, 120), (100, 70, 46))])
    if key == "kartka_list":
        return _rek(key, 220, 160, [(rect(6, 6, 214, 154), (240, 230, 206), dict(kind="gladki", edge=2))])
    if key == "kamien_kreski":  # kamień z wyrytymi kreskami (lata)
        return _rek(key, 260, 200, [(poly([(10, 200), (30, 40), (130, 10), (230, 50), (250, 200)]), (150, 140, 124), dict(edge=2, shade=0.2))])
    if key == "ksiazki":
        p = []
        for n in range(6):
            p.append((rect(20 + n * 6, 200 - n * 32, 300 - n * 10, 230 - n * 32), [(120, 40, 44), (60, 84, 110), (200, 170, 110), (80, 110, 70)][n % 4], dict(edge=2)))
        return _rek(key, 320, 240, p)
    if key == "mapa_pustyni":
        return _rek(key, 420, 300, [(rect(10, 10, 410, 290), (226, 200, 150), dict(kind="gladki", edge=3)),
                                    (poly([(60, 220), (150, 120), (260, 160), (360, 80)]), (180, 130, 80)), (ell(250, 200, 40, 20), (200, 160, 100))])
    if key == "lupa":
        return _rek(key, 300, 300, [(ell(120, 120, 110, 110), (110, 80, 54), dict(edge=2)), (ell(120, 120, 94, 94), (230, 240, 246)),
                                    (_band((200, 200), (290, 290), 26), (110, 80, 54))])
    if key == "kalendarz":
        return _rek(key, 240, 300, [(rect(10, 10, 230, 290), (240, 236, 226), dict(kind="gladki", edge=2)), (rect(10, 10, 230, 60), (170, 40, 40))])
    if key == "rama_obrazu":
        return _rek(key, 900, 620, [(rect(0, 0, 900, 620), GOLD, dict(edge=3)), (rect(40, 40, 860, 580), (210, 190, 150))])
    raise KeyError(key)


@lru_cache(None)
def kalendarz_rok(rok):
    w, h = 240, 300
    parts = [(rect(10, 10, 230, 290), (240, 236, 226), dict(kind="gladki", edge=2)), (rect(10, 10, 230, 60), (170, 40, 40)),
             (glyphs(str(rok), 76, FONT_PL, PL_IDX, (w / 2, 180), "mm"), INK)]
    return Sprite(stack(w, h, parts, seed=rok), f"kalendarz-{rok}", rim=2, clean=False)


@lru_cache(None)
def obraz(nazwa):
    """Obraz w złotej ramie jako wycinek (zastępuje prawdziwe pliki z Commons do czasu ich pobrania — ujęcia Ken Burns).
    „horschelt”: kapitulacja pod brzozami, „portret”: Szamil w turbanie."""
    w, h = 900, 620
    parts = [(rect(0, 0, w, h), GOLD, dict(edge=3)), (rect(40, 40, w - 40, h - 40), (174, 168, 140))]
    if nazwa == "horschelt":
        parts += [(poly([(40, 420), (300, 300), (520, 360), (860, 280), (860, 580), (40, 580)]), (120, 120, 90)),
                  (poly([(40, 300), (200, 160), (360, 240), (520, 120), (700, 220), (860, 140), (860, 300), (40, 380)]), (150, 160, 170))]
        for x in (200, 620, 700):
            parts += [(rect(x, 200, x + 14, 470), (236, 232, 220)), (ell(x + 7, 190, 60, 50), (96, 130, 80))]
        parts += [(ell(640, 450, 30, 60), (40, 58, 48)), (ell(640, 380, 16, 18), (236, 206, 172)),
                  (ell(420, 440, 28, 70), CZERN), (ell(420, 360, 18, 20), (236, 206, 172)), (ell(420, 338, 22, 12), (244, 240, 228))]
        for x in range(80, 360, 40):
            parts.append((ell(x, 470, 12, 40), (60, 70, 60)))
    else:
        parts += [(ell(450, 330, 220, 260), (110, 96, 80)), (ell(450, 270, 90, 110), (226, 196, 160)),
                  (ell(450, 170, 110, 50), (244, 240, 228)), (poly([(380, 320), (520, 320), (500, 440), (450, 470), (400, 440)]), (60, 50, 44)),
                  (poly([(330, 420), (570, 420), (620, 580), (280, 580)]), CZERN)]
    return Sprite(stack(w, h, parts, seed=150 + len(nazwa)), f"obraz-{nazwa}", rim=3, clean=False)


@lru_cache(None)
def kurtyna_kz(strona):
    """Kurtyna z ciemnego bordowego aksamitu (ta sama budowa co w poprzednich filmach)."""
    return Z0.Z0.kurtyna(strona) if hasattr(Z0, "Z0") else Z0.kurtyna(strona)


# =====================================================================================================================
# ---------- szkic E (przebudowa 28.11.2026): nowe lalki i wycinki ----------
# Reżyser 28.11: „przebuduj to… przecież to ma być zajebiste”. Gimry 1832, gabinet w Petersburgu z mapą i pieczątką,
# bukowy las Czeczenii, Dargo, Tołstoj, Kaługa, robak z Diuny i fremeni (własne wycinanki, nic z filmów — księga D5).
# =====================================================================================================================

_kapelusz_d = _kapelusz


def _kapelusz(s, parts):  # noqa: F811 — kaptur fremena i dwurożny kapelusz z pióropuszem (Woroncow)
    k, c = s["kapelusz"], s["kapelusz_kolor"]
    if k == "kaptur":  # kaptur płaszcza pustyni: obejmuje głowę, spływa na ramiona; twarz odsłonięta
        parts += [(poly([(100, 120), (104, 70), (126, 46), (152, 40), (180, 46), (202, 70), (206, 120), (212, 200), (186, 214),
                         (190, 120), (186, 84), (152, 70), (120, 84), (116, 120), (120, 214), (94, 200)]), c,
                   dict(kind="gnieciony", contrast=1.1, edge=2)),
                  (poly([(124, 150), (188, 146), (186, 176), (126, 178)]), _shade(c, 0.6))]  # zasłona na usta, pod oczami
    elif k == "dwurozny":  # czarny dwurożny kapelusz z ogromnym białym pióropuszem (gag z żyrandolem)
        parts += [(poly([(84, 96), (222, 96), (196, 70), (152, 58), (110, 70)]), c, dict(edge=2)),
                  (ell(152, 80, 10, 10), GOLD)]  # pióropusz osobno: rek_kz("pioropusz") w ujęciu, nad czubkiem głowy
    elif k == "kepi":  # czapka kadeta / ochotnika (Tołstoj, młody Dżamaluddin)
        parts += [(poly([(112, 92), (196, 92), (192, 62), (116, 62)]), c, dict(edge=2)),
                  (rect(112, 84, 196, 92), (190, 40, 40)), (poly([(160, 92), (214, 98), (206, 104), (166, 100)]), (24, 22, 22))]
    else:
        _kapelusz_d(s, parts)


PIASEK = (196, 170, 120)
LALKI.update({
    # fremeni — własne wycinanki: piaskowe płaszcze z kapturem, ciemna zasłona na usta (bez twarzy aktorów, D5)
    "fremen": dict(wlosy=(60, 44, 32), kapelusz="kaptur", kapelusz_kolor=(150, 124, 86), stroj="plaszcz", gora=(170, 140, 98),
                   dol=(120, 98, 70), koszula=(90, 74, 56), krawat=None, buty=(80, 64, 48), pas=(70, 56, 40), dluga=True),
    "fremen2": dict(wlosy=(40, 30, 24), kapelusz="kaptur", kapelusz_kolor=(120, 104, 80), stroj="plaszcz", gora=(144, 122, 90),
                    dol=(110, 90, 64), koszula=(90, 74, 56), krawat=None, buty=(80, 64, 48), pas=(70, 56, 40), dluga=True, szer=1.05),
    # car Mikołaj I (biały mundur, wąsy) — inny niż Aleksander II („car”)
    "nikolaj": dict(wlosy=(150, 120, 86), fryzura="zaczesane", wasy=True, stroj="mundur", gora=(236, 232, 220), dol=(40, 46, 70),
                    koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD, pas=GOLD, odznaka=True, szer=1.06),
    "general": dict(wlosy=(220, 216, 210), wasy=True, broda=True, kapelusz="czapka", kapelusz_kolor=(40, 58, 48), stroj="mundur",
                    gora=(40, 58, 48), dol=(170, 40, 40), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD, szer=1.08),
    # urzędnik z pieczątką (gag powracający): czarny frak, okulary; w 1859 siwy
    "urzednik": dict(wlosy=(60, 46, 36), fryzura="zaczesane", okulary=True, stroj="garnitur", gora=(34, 34, 40), dol=(34, 34, 40),
                     koszula=(240, 236, 226), krawat=(30, 30, 34)),
    "urzednik_stary": dict(wlosy=(214, 210, 204), fryzura="zaczesane", okulary=True, wasy=True, stroj="garnitur", gora=(34, 34, 40),
                           dol=(34, 34, 40), koszula=(240, 236, 226), krawat=(30, 30, 34)),
    "vorontsov": dict(wlosy=(200, 190, 176), wasy=True, kapelusz="dwurozny", kapelusz_kolor=(30, 28, 30), stroj="mundur",
                      gora=(36, 52, 44), dol=(236, 232, 220), koszula=(190, 40, 40), krawat=None, buty=(24, 22, 22), epolety=GOLD,
                      pas=GOLD, szer=1.02),
    "tolstoj": dict(wlosy=(80, 60, 44), wasy=True, kapelusz="kepi", kapelusz_kolor=(70, 76, 70), stroj="mundur", gora=(96, 100, 92),
                    dol=(60, 64, 60), koszula=(200, 40, 40), krawat=None, buty=(28, 24, 22), pas=(40, 34, 30)),
    "sado": dict(wlosy=(30, 26, 24), wasy=True, kapelusz="papacha", kapelusz_kolor=(150, 130, 110), stroj="plaszcz", gora=(110, 90, 70),
                 dol=(60, 52, 44), koszula=(200, 180, 150), krawat=None, buty=(28, 24, 22), gazyry=True, pas=(70, 64, 56), szer=0.96),
    "dzamal_sredni": dict(wlosy=(40, 32, 28), fryzura="zaczesane", kapelusz="kepi", kapelusz_kolor=(40, 46, 70), stroj="mundur",
                          gora=(40, 46, 70), dol=(40, 46, 70), koszula=(200, 40, 40), krawat=None, buty=(24, 22, 22), pas=(236, 232, 220),
                          szer=0.97),
    "gap1": dict(kobieta=True, wlosy=(120, 80, 50), fryzura="kok", kapelusz="kapelusik", kapelusz_kolor=(120, 60, 90), stroj="sukienka",
                 gora=(170, 120, 150), dol=(170, 120, 150), kolnierzyk=(250, 244, 232), dluga=True),
    "gap2": dict(wlosy=(150, 110, 70), wasy=True, kapelusz="melonik", kapelusz_kolor=(40, 36, 34), stroj="garnitur", gora=(90, 80, 70),
                 dol=(70, 64, 60), koszula=(236, 232, 220), krawat=(110, 40, 40)),
    "gap3": dict(wlosy=(200, 160, 100), fryzura="loki", stroj="koszula", koszula=(220, 200, 170), gora=(220, 200, 170),
                 dol=(80, 70, 60), krawat=None, szer=0.9),
})


@lru_cache(None)
def raport(stempel=None, stary=False, w=620, h=420):
    """Raport z gór na biurku urzędnika: linie maszynopisu, podpis; stempel — czerwony napis pieczątki ukośnie."""
    papier = (232, 220, 190) if stary else (244, 236, 214)
    parts = [(rect(6, 6, w - 6, h - 6), papier, dict(kind="gladki", edge=3)),
             (glyphs("REPORT FROM THE CAUCASUS", 30, FONT_MASZ, 0, (w / 2, 46), "mm"), INK)]
    r = random.Random(w + h)
    for n in range(7):
        parts.append((rect(50, 92 + n * 34, 50 + r.uniform(380, 520), 100 + n * 34), _shade(INK, 1.8)))
    if stempel:
        f = ImageFont.truetype(FONT_PL, 64, index=PL_IDX)
        tw = f.getlength(stempel)
        sc = min(1.0, (w - 90) / max(tw, 1))
        parts += [(poly([(w / 2 - tw * sc / 2 - 24, 190), (w / 2 + tw * sc / 2 + 24, 170), (w / 2 + tw * sc / 2 + 30, 270),
                         (w / 2 - tw * sc / 2 - 18, 290)]), (196, 40, 40), dict(kind="gladki", edge=0, contrast=0.6)),
                  (poly([(w / 2 - tw * sc / 2 - 14, 200), (w / 2 + tw * sc / 2 + 14, 182), (w / 2 + tw * sc / 2 + 20, 260),
                         (w / 2 - tw * sc / 2 - 8, 278)]), papier),
                  (glyphs(stempel, int(64 * sc), FONT_PL, PL_IDX, (w / 2, 230), "mm"), (196, 40, 40), dict(kind="gladki", rough=0.8))]
    return Sprite(stack(w, h, parts, seed=17 + len(stempel or "")), f"raport-{stempel}", rim=2, clean=False)


@lru_cache(None)
def mapa_kaukazu(w=1000, h=560):
    """Papierowa mapa Kaukazu na stole: morza, grzbiety gór, rzeki, napis CAUCASUS, strzałka do DARGO (osobno)."""
    parts = [(rect(6, 6, w - 6, h - 6), (230, 212, 168), dict(kind="gladki", edge=4)),
             (poly([(6, 6), (150, 6), (110, 250), (150, 554), (6, 554)]), (150, 176, 190)),
             (poly([(w - 6, 6), (w - 130, 6), (w - 90, 300), (w - 140, 554), (w - 6, 554)]), (150, 176, 190))]
    for n in range(9):
        x = 230 + n * 66
        y = 300 - 60 * math.sin(n / 8 * math.pi)
        parts.append((poly([(x - 46, y + 40), (x, y - 40), (x + 46, y + 40)]), (150, 120, 90)))
        parts.append((poly([(x - 14, y - 16), (x, y - 40), (x + 14, y - 16)]), (246, 244, 238)))
    parts += [(_band((300, 380), (500, 520), 5), (110, 150, 180)), (_band((620, 360), (560, 540), 5), (110, 150, 180)),
              (glyphs("CAUCASUS", 50, FONT_PL, PL_IDX, (w / 2, 120), "mm"), INK)]
    return Sprite(stack(w, h, parts, seed=303), "mapa-kaukazu", rim=2, clean=False)


@lru_cache(None)
def rek_e(key):
    """Wycinki szkicu E (arkusze w pikselach; kotwice podane przy użyciu w ujęciach)."""
    if key == "robak":  # robak z Diuny: łuk z pierścieni, okrągła paszcza z zębami u góry; dół (0.5, 1.0)
        p = []
        for n in range(9):
            y = 900 - n * 92
            x = 180 + 40 * math.sin(n / 3.0)
            r = 118 - n * 3
            p.append((ell(x, y, r, 60), _shade((176, 140, 100), 0.86 + 0.06 * (n % 2)), dict(edge=2, kind="gnieciony")))
            p.append((ell(x, y - 30, r - 10, 18), _shade((150, 116, 80), 0.9)))
        p += [(ell(196, 110, 120, 100), (150, 112, 78), dict(edge=3)), (ell(196, 110, 92, 74), (60, 30, 26)),
              (ell(196, 110, 56, 42), (24, 12, 12))]
        for a in range(0, 360, 30):  # zęby w paszczy
            cx, cy = 196 + 80 * math.cos(math.radians(a)), 110 + 62 * math.sin(math.radians(a))
            ix, iy = 196 + 58 * math.cos(math.radians(a + 8)), 110 + 44 * math.sin(math.radians(a + 8))
            p.append((poly([(cx, cy), (ix, iy), (196 + 76 * math.cos(math.radians(a + 16)), 110 + 60 * math.sin(math.radians(a + 16)))]),
                      (240, 232, 206)))
        return _rek(key, 380, 960, p)
    if key == "koza":  # koza z bródką i rogami, zwrócona w prawo; stopy (0.5, 1.0)
        return _rek(key, 300, 240, [(ell(130, 120, 96, 52), (232, 228, 218), dict(edge=2)), (_band((200, 100), (236, 50), 34), (232, 228, 218)),
                                    (ell(248, 46, 34, 24), (232, 228, 218)), (poly([(236, 24), (220, -4), (232, 2), (246, 26)]), (120, 104, 84)),
                                    (poly([(268, 58), (262, 92), (254, 60)]), (160, 150, 136)), (ell(256, 38, 4, 4), (20, 20, 20)),
                                    (poly([(224, 30), (206, 20), (222, 42)]), (210, 200, 186))] +
                    [(_band((x, 160), (x, 236), 14), (210, 204, 192)) for x in (70, 100, 160, 190)] +
                    [(poly([(36, 104), (14, 84), (30, 116)]), (210, 204, 192))])
    if key == "koza_meh":  # ta sama koza z otwartym pyskiem
        im = rek_e("koza")
        return _rek(key, 300, 240, [(ell(130, 120, 96, 52), (232, 228, 218), dict(edge=2)), (_band((200, 100), (236, 50), 34), (232, 228, 218)),
                                    (ell(248, 46, 34, 24), (232, 228, 218)), (poly([(236, 24), (220, -4), (232, 2), (246, 26)]), (120, 104, 84)),
                                    (poly([(268, 58), (262, 92), (254, 60)]), (160, 150, 136)), (ell(256, 38, 4, 4), (20, 20, 20)),
                                    (poly([(262, 50), (290, 44), (290, 62), (264, 60)]), (90, 40, 40)),
                                    (poly([(224, 30), (206, 20), (222, 42)]), (210, 200, 186))] +
                    [(_band((x, 160), (x, 236), 14), (210, 204, 192)) for x in (70, 100, 160, 190)] +
                    [(poly([(36, 104), (14, 84), (30, 116)]), (210, 204, 192))]) if im else None
    if key == "kot":
        return _rek(key, 200, 150, [(ell(90, 96, 70, 36), (60, 56, 56), dict(edge=2)), (ell(160, 70, 30, 28), (60, 56, 56)),
                                    (poly([(140, 50), (146, 22), (158, 46)]), (60, 56, 56)), (poly([(166, 46), (180, 20), (184, 50)]), (60, 56, 56)),
                                    (ell(170, 66, 4, 4), (230, 210, 80)), (_band((24, 90), (4, 30), 10), (60, 56, 56))] +
                    [(_band((x, 120), (x, 148), 10), (60, 56, 56)) for x in (50, 70, 110, 130)])
    if key == "pieczatka":  # drewniana rączka, metalowa podstawa; dół (0.5, 1.0)
        return _rek(key, 160, 220, [(ell(80, 34, 40, 30), (120, 80, 50), dict(edge=2)), (rect(66, 50, 94, 150), (130, 90, 56)),
                                    (rect(20, 150, 140, 184), (70, 70, 76), dict(kind="gladki")), (rect(16, 184, 144, 214), (170, 40, 40))])
    if key == "gora_mapy":  # papierowa góra wstająca z mapy (zawias u dołu)
        return _rek(key, 260, 220, [(poly([(10, 214), (130, 10), (250, 214)]), (150, 120, 90), dict(edge=2, shade=0.2)),
                                    (poly([(96, 70), (130, 10), (164, 70), (146, 62), (130, 78), (114, 62)]), (246, 244, 238))])
    if key == "zolnierzyk":  # cynowy żołnierzyk na podstawce
        return _rek(key, 40, 100, [(rect(6, 88, 34, 100), (120, 120, 126)), (rect(12, 40, 28, 90), (236, 232, 220)),
                                   (ell(20, 30, 9, 9), (230, 200, 170)), (rect(11, 14, 29, 24), (236, 234, 226)), (rect(30, 4, 33, 70), (90, 90, 96))])
    if key == "wieza":  # kamienna wieża w Gimry: okno u góry (otwór), drzwi na podwyższonym progu u dołu
        r = random.Random(11)
        p = [(poly([(30, 900), (50, 60), (250, 60), (270, 900)]), (168, 152, 126), dict(edge=3, shade=0.18))]
        for row in range(20):
            for n in range(5):
                p.append((ell(60 + n * 46 + (23 if row % 2 else 0) + r.uniform(-4, 4), 90 + row * 42, 20, 13),
                          _shade((168, 152, 126), r.uniform(0.84, 1.08))))
        p += [(poly([(40, 60), (150, 0), (260, 60)]), (120, 96, 70), dict(edge=2)), (rect(100, 140, 200, 250), (40, 30, 26)),
              (rect(96, 640, 204, 820), (60, 44, 34)), (rect(80, 820, 220, 860), (140, 126, 104))]
        return _rek(key, 300, 900, p, dziura=(108, 148, 192, 244))
    if key == "szalas":  # szałas pasterza z kamienia i gałęzi, ciemne wejście
        return _rek(key, 460, 320, [(poly([(20, 316), (40, 120), (230, 20), (420, 120), (440, 316)]), (130, 110, 84), dict(edge=2, shade=0.2)),
                                    (poly([(10, 140), (230, 6), (450, 140), (420, 150), (230, 40), (40, 150)]), (90, 70, 46)),
                                    (poly([(170, 316), (180, 190), (230, 160), (280, 190), (290, 316)]), (30, 24, 20))])
    if key == "meczet_cien":  # sylwetka meczetu z kopułą i minaretem (teatr cieni)
        return _rek(key, 800, 480, [(rect(120, 220, 680, 480), (20, 16, 14)), (ell(400, 220, 170, 150), (20, 16, 14)),
                                    (rect(392, 40, 408, 80), (20, 16, 14)), (rect(700, 60, 740, 480), (20, 16, 14)),
                                    (poly([(690, 70), (720, 0), (750, 70)]), (20, 16, 14))])
    if key == "buk":  # buk: gładki szary pień, okrągła korona
        p = [(poly([(150, 700), (160, 260), (196, 260), (210, 700)]), (150, 150, 146), dict(edge=2, kind="gladki"))]
        p += [(ell(178 + dx, 180 + dy, 110, 90), _shade((96, 128, 70), 0.9 + 0.05 * (i % 3)), dict(edge=2))
              for i, (dx, dy) in enumerate(((-90, 40), (80, 30), (0, -40), (-40, 90), (60, 100), (0, 40)))]
        return _rek(key, 360, 700, p)
    if key == "pien_lezacy":  # ścięty buk w poprzek drogi
        return _rek(key, 700, 140, [(poly([(10, 70), (640, 50), (690, 80), (650, 110), (20, 120)]), (150, 150, 146), dict(edge=2)),
                                    (ell(40, 95, 30, 26), (200, 180, 140))] +
                    [(ell(500 + dx, 50 + dy, 70, 50), (96, 128, 70)) for dx, dy in ((0, 0), (90, 20), (40, -20))])
    if key == "worek_suchary":
        return _rek(key, 170, 190, [(poly([(30, 60), (140, 60), (160, 184), (10, 184)]), (196, 176, 136), dict(edge=2)),
                                    (rect(62, 40, 108, 66), (160, 138, 100)),
                                    (glyphs("SUKHARI", 26, FONT_MASZ, 0, (85, 130), "mm"), (90, 60, 40))])
    if key == "suchar":
        return _rek(key, 70, 50, [(poly([(6, 10), (64, 4), (66, 44), (4, 46)]), (214, 176, 110), dict(edge=2)),
                                  (ell(24, 22, 3, 3), (170, 130, 80)), (ell(44, 30, 3, 3), (170, 130, 80))])
    if key == "zeszyt":  # zeszyt otwarty; chwyt (14, 60)
        return _rek(key, 160, 110, [(rect(4, 6, 156, 104), (90, 70, 56), dict(edge=2)), (rect(10, 10, 78, 100), (244, 238, 222)),
                                    (rect(82, 10, 150, 100), (244, 238, 222))] +
                    [(rect(16, 24 + n * 12, 70, 27 + n * 12), (120, 110, 100)) for n in range(6)])
    if key == "kartka":
        return _rek(key, 90, 110, [(poly([(4, 6), (86, 2), (88, 104), (2, 108)]), (244, 238, 222), dict(kind="gladki", edge=2))] +
                    [(rect(12, 18 + n * 14, 74, 21 + n * 14), (120, 110, 100)) for n in range(6)])
    if key == "dom_kaluga":  # parterowy dom z kolumienkami i mezaninem (Kaługa)
        p = [(rect(40, 150, 760, 440), (226, 206, 160), dict(edge=3, shade=0.12)), (poly([(20, 160), (400, 40), (780, 160)]), (110, 120, 110), dict(edge=2)),
             (poly([(300, 150), (400, 90), (500, 150)]), (236, 220, 180), dict(edge=2))]
        p += [(rect(x, 170, x + 22, 440), (246, 240, 226)) for x in (300, 350, 430, 480)]
        p += [(rect(x, 230, x + 70, 330), (110, 140, 160)) for x in (80, 180, 580, 680)]
        p += [(rect(370, 300, 430, 440), (110, 76, 52)), (rect(260, 430, 540, 450), (200, 190, 170))]
        return _rek(key, 800, 450, p)
    if key == "plot":  # drewniany płot z desek (zza niego wychylają się gapie)
        p = [(rect(0, 60, 1400, 80), (150, 112, 72)), (rect(0, 120, 1400, 140), (150, 112, 72))]
        p += [(poly([(x, 160), (x, 20), (x + 20, 4), (x + 40, 20), (x + 40, 160)]), _shade((176, 136, 90), 0.9 + 0.08 * ((x // 48) % 3)),
               dict(edge=2)) for x in range(4, 1396, 48)]
        return _rek(key, 1400, 160, p)
    if key == "laska_hak":  # ręka maszynisty zza kulis: rękaw, dłoń, długa laska z hakiem; poziomo, rękaw z lewej
        return _rek(key, 900, 120, [(poly([(0, 30), (170, 40), (176, 90), (0, 100)]), (50, 48, 52), dict(edge=2)),
                                    (ell(196, 64, 30, 26), (226, 196, 164)), (_band((200, 64), (820, 60), 10), (130, 96, 60)),
                                    (_band((820, 60), (870, 70), 10), (130, 96, 60)), (_band((870, 70), (880, 104), 10), (130, 96, 60)),
                                    (_band((880, 104), (850, 110), 10), (130, 96, 60))])
    if key == "rekawica":  # dłoń w rękawicy z herbem (strona Diuny w akcie VI); chwyt (120, 60)
        return _rek(key, 200, 130, [(poly([(0, 30), (90, 30), (96, 100), (0, 100)]), (40, 40, 60), dict(edge=2)),
                                    (ell(130, 64, 44, 40), (90, 70, 50), dict(edge=2)), (ell(50, 64, 20, 20), GOLD)])
    if key == "kamien_kartka":
        return _rek(key, 90, 80, [(ell(40, 46, 34, 28), (130, 124, 116), dict(edge=2)), (rect(40, 6, 90, 50), (244, 238, 222))])
    if key == "szlaban":  # szlaban w biało-czarne pasy i budka wartownika
        p = [(rect(10, 60, 110, 300), (236, 232, 220), dict(edge=2)), (poly([(0, 60), (60, 10), (120, 60)]), (40, 36, 34))]
        p += [(rect(10, 80 + n * 44, 110, 102 + n * 44), (30, 28, 28)) for n in range(5)]
        p += [(rect(110, 170, 380, 186), (236, 232, 220))] + [(rect(130 + n * 50, 170, 152 + n * 50, 186), (30, 28, 28)) for n in range(5)]
        return _rek(key, 380, 300, p)
    if key == "list_szamila":  # list z pieczęcią i arabskim pismem (kreski)
        p = [(rect(6, 6, 314, 214), (240, 226, 196), dict(kind="gladki", edge=2))]
        r = random.Random(5)
        p += [(rect(r.uniform(30, 60), 30 + n * 26, r.uniform(240, 290), 34 + n * 26), (60, 50, 70)) for n in range(6)]
        p += [(ell(270, 190, 18, 18), (170, 40, 40))]
        return _rek(key, 320, 220, p)
    if key == "jaskinia":  # ciemny łuk wejścia do jaskini w skale (sietch); dół (0.5, 1.0)
        return _rek(key, 220, 180, [(poly([(10, 180), (14, 110), (40, 50), (110, 14), (180, 50), (206, 110), (210, 180)]), (40, 26, 20),
                                     dict(edge=2)), (poly([(40, 180), (44, 120), (70, 74), (110, 50), (150, 74), (176, 120), (180, 180)]), (18, 12, 10))])
    if key == "pioropusz":  # ogromny biały pióropusz Woroncowa; dół (0.5, 1.0) wpięty w kapelusz
        return _rek(key, 160, 420, [(poly([(70, 420), (40, 300), (30, 180), (60, 70), (110, 0), (120, 90), (130, 200), (110, 320),
                                          (96, 420)]), (250, 248, 240), dict(kind="gnieciony", contrast=0.8, edge=2)),
                                    (poly([(80, 400), (70, 260), (84, 120), (100, 40)]), (226, 222, 214))])
    raise KeyError(key)


_rek_kz_d = rek_kz


def rek_kz(key):  # noqa: F811 — najpierw wycinki szkicu E, potem dawne
    try:
        return rek_e(key)
    except KeyError:
        return _rek_kz_d(key)


@lru_cache(None)
def cyfra(txt, size=110, kolor=(40, 28, 24)):
    """Pojedyncze cyfry i znaki liczby na liście Szamila (gag: zera odpadają); bez tła."""
    f = ImageFont.truetype(FONT_PL, size, index=PL_IDX)
    w = int(f.getlength(txt)) + 16
    h = size + 30
    return Sprite(stack(w, h, [(glyphs(txt, size, FONT_PL, PL_IDX, (w / 2, h / 2), "mm"), kolor, dict(kind="gladki", rough=0.6))],
                        seed=len(txt) + size), f"cyfra-{txt}-{size}", rim=1, clean=False)


# =====================================================================================================================
# ---------- duże arkusze z wieloma kawałkami: liczone raz i trzymane na dysku ----------
_WYCINKI = Path(__file__).resolve().parent / "build" / "wycinki"


def stack_d(w, h, parts, seed=0, detale=None):
    """stack z pamięcią na dysku (build/wycinki): duży arkusz (np. 2200 × 900) z dziesiątkami kawałków liczył się do 2 min
    (regały), a podgląd na żywo i każdy proces renderu liczyłby go od nowa. Klucz: kod funkcji, która woła, jej argumenty
    i wymiary — zmiana rysunku daje nowy klucz. detale(draw, im) — drobiazgi (książki, kamienie, klepki) rysowane wprost na
    arkuszu, bez osobnego kawałka papieru na każdy."""
    import hashlib
    import inspect
    fr = sys._getframe(1)
    co = fr.f_code
    src = inspect.getsource(co)
    args = [(k, fr.f_locals.get(k)) for k in co.co_varnames[:co.co_argcount]]
    stale = [(k, fr.f_globals.get(k)) for k in co.co_names
             if isinstance(fr.f_globals.get(k), (int, float, str, tuple, list, dict)) and k.isupper()]  # SKALA_JASKINIE, PORY…
    klucz = hashlib.sha1((src + repr(args) + repr(stale) + f"{w}x{h}-{seed}").encode()).hexdigest()[:20]
    path = _WYCINKI / f"{co.co_name}-{klucz}.png"
    if path.exists():
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            pass
    im = stack(w, h, parts, seed=seed)
    if detale is not None:
        detale(ImageDraw.Draw(im), im)
    _WYCINKI.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".{random.randint(0, 10 ** 9)}.tmp.png")
    im.save(tmp)
    tmp.replace(path)
    return im


# ---------- dekoracje 2 (reżyser 28.11 po 2 minutach szkicu E): „od 40 s cały czas te góry… co najmniej 4 scenografie
# na 2 minuty”, „wziąłeś biuro z Bonnie i Clyde… ma być zupełnie inne”. Nowe niebo pór dnia, ściany wąwozu, niskie
# wzgórza, dziedziniec meczetu, gabinet w Pałacu Zimowym, szańce baterii, brama twierdzy, skała z jaskiniami — bez
# arkuszy „Bonnie and Clyde” (tapeta, okno, deski, meble) i bez ciągłych pasm gór w tle.
# =====================================================================================================================

PORY = {"zmierzch": ((64, 56, 104), (244, 152, 92)), "swit": ((118, 148, 198), (248, 200, 172)), "noc": ((16, 20, 46), (58, 64, 102)),
        "lato": ((150, 190, 214), (252, 242, 212)), "zima": ((150, 160, 178), (228, 230, 234)), "dym": ((120, 100, 96), (232, 176, 120)),
        "palac": ((200, 212, 226), (240, 236, 226))}


@lru_cache(None)
def niebo_pora(pora):
    """Niebo pory dnia (2080 × 1280): u góry ciemniej, przy horyzoncie (ok. 70 % wysokości) najjaśniej."""
    w, h = 2080, 1280
    lum = texture("gladki", w, h, 17)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    top, dol = (np.array(c, np.float32) for c in PORY[pora])
    k = np.clip(yy / 0.7, 0, 1) ** 1.4
    rgb = (top + (dol - top) * k)[:, None, :].reshape(h, 1, 3) / 255.0 * lum[..., None]
    out = np.dstack([np.clip(rgb, 0, 1), np.ones((h, w), np.float32)])
    return Sprite(Image.fromarray((out * 255).astype(np.uint8), "RGBA"), f"niebo-{pora}", rim=0, clean=False, pad=0)


@lru_cache(None)
def wzgorza(v=0, kolor=(110, 118, 86)):
    """Niskie, zaokrąglone wzgórza (przedgórze, równina; 2000 × 320) — miękka linia zamiast postrzępionych szczytów."""
    w, h = 2000, 320
    r = random.Random(v)
    f = [r.uniform(0, 6.28) for _ in range(3)]
    top = [(x, 150 - 60 * math.sin(x / 330 + f[0]) - 30 * math.sin(x / 140 + f[1]) - 12 * math.sin(x / 60 + f[2])) for x in range(0, w + 20, 20)]
    parts = [(poly(top + [(w, h), (0, h)]), kolor, dict(kind="gladki", edge=3, shade=0.14, contrast=0.9))]
    for n in range(7):
        x0 = r.uniform(0, w - 300)
        parts.append((poly([(x0, 210 + r.uniform(-30, 30)), (x0 + 260, 196 + r.uniform(-30, 30)), (x0 + 270, 214), (x0 + 10, 226)]),
                      _shade(kolor, 1.12)))
    return Sprite(stack_d(w, h, parts, seed=170 + v), f"wzgorza-{v}-{kolor}", rim=3, clean=False)


@lru_cache(None)
def klif(v=0, kolor=(132, 116, 96)):
    """Pionowa ściana skalna (640 × 1100): wewnętrzny brzeg po lewej stronie arkusza, półki i pęknięcia; v nieparzyste — lustro
    (brzeg po prawej). Wąwóz w Gimry, przełęcz, ostaniec z kreskami."""
    w, h = 640, 1100
    r = random.Random(40 + v)
    kraw, y, x = [], 0.0, 240.0
    while y < h:
        kraw.append((x, y))
        y += r.uniform(70, 130)
        x = clamp(x + r.uniform(-70, 60), 60, 360)
    kraw.append((x, h))
    parts = [(poly(kraw + [(w, h), (w, 0)]), kolor, dict(edge=3, shade=0.24, contrast=1.25))]
    for n in range(len(kraw) - 1):  # półki: jasny pas pod załamaniem brzegu
        (x0, y0), (x1, y1) = kraw[n], kraw[n + 1]
        parts.append((poly([(x0, y0), (x0 + 160, y0 + 30), (x0 + 150, y0 + 44), (x0 - 4, y0 + 18)]), _shade(kolor, 1.18)))
        parts.append((_band((x0 + 60, y0 + 40), (x1 + 120, y1 - 10), 7), _shade(kolor, 0.7)))
    for n in range(10):  # pęknięcia
        x0, y0 = r.uniform(300, 600), r.uniform(40, 1040)
        parts.append((_band((x0, y0), (x0 + r.uniform(-40, 40), y0 + r.uniform(80, 180)), 5), _shade(kolor, 0.66)))
    im = stack_d(w, h, parts, seed=180 + v)
    if v % 2:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return Sprite(im, f"klif-{v}-{kolor}", rim=3, clean=False)


@lru_cache(None)
def bruk(kolor=(150, 138, 118)):
    """Kamienna posadzka dziedzińca (2200 × 200): nieregularne płyty."""
    w, h = 2200, 200
    r = random.Random(5)
    parts = [(rect(0, 0, w, h), _shade(kolor, 0.8), dict(shade=0.2))]
    for row in range(5):
        x = -r.uniform(0, 60)
        while x < w:
            dw = r.uniform(70, 130)
            parts.append((rect(x + 3, row * 40 + 3, x + dw - 3, row * 40 + 37), _shade(kolor, r.uniform(0.9, 1.1))))
            x += dw
    return Sprite(stack_d(w, h, parts, seed=190), f"bruk-{kolor}", rim=0, clean=False, pad=0)


@lru_cache(None)
def arkady():
    """Dziedziniec meczetu w aule (1700 × 760): kamienna ściana z arkadą ostrych łuków, drewniana galeria nad nią, płaski
    dach, z prawej smukły minaret z balkonikiem."""
    w, h = 1700, 760
    kam, drewno = (198, 180, 150), (128, 88, 56)
    parts = [(rect(0, 250, w, h), kam, dict(edge=3, shade=0.14)), (rect(0, 230, w, 256), _shade(kam, 0.8))]
    for n in range(6):  # arkada
        x0 = 70 + n * 230
        parts += [(poly([(x0, h), (x0, 480), (x0 + 30, 420), (x0 + 75, 392), (x0 + 120, 420), (x0 + 150, 480), (x0 + 150, h)]), (64, 50, 40)),
                  (poly([(x0 - 10, 480), (x0 + 30, 410), (x0 + 75, 380), (x0 + 120, 410), (x0 + 160, 480), (x0 + 150, 482), (x0 + 120, 422),
                         (x0 + 75, 394), (x0 + 30, 422), (x0, 482)]), _shade(kam, 1.15))]
    parts += [(rect(0, 150, 1380, 236), drewno, dict(edge=2)), (rect(0, 140, 1390, 156), _shade(drewno, 0.8))]  # galeria
    for x in range(10, 1380, 26):
        parts.append((rect(x, 176, x + 8, 232), _shade(drewno, 1.25)))
    for n in range(5):  # drzwi na galerię
        x0 = 120 + n * 260
        parts.append((rect(x0, 40, x0 + 90, 150), (84, 60, 40)))
    parts.append((rect(0, 20, 1380, 44), _shade(kam, 0.75)))  # płaski dach
    mx = 1520  # minaret
    parts += [(rect(mx - 34, 0, mx + 34, h), _shade(kam, 1.05), dict(edge=2, shade=0.18)),
              (rect(mx - 56, 120, mx + 56, 140), drewno), (rect(mx - 50, 96, mx + 50, 122), (84, 60, 40))]
    for yy in (240, 400, 560):
        parts.append((rect(mx - 8, yy, mx + 8, yy + 40), (60, 46, 38)))
    return Sprite(stack_d(w, h, parts, seed=200), "arkady", rim=2, clean=False)


@lru_cache(None)
def minaret_szczyt():
    """Szczyt minaretu nad dachem (stożek z półksiężycem byłby symbolem — tylko kamienny stożek, Wytyczne 1.6)."""
    return Sprite(stack_d(140, 160, [(poly([(10, 160), (70, 0), (130, 160)]), (150, 120, 90), dict(edge=2))], seed=201), "minaret-szczyt", rim=2,
                  clean=False)


# ---------- Pałac Zimowy (gabinet cara i urzędu) ----------

@lru_cache(None)
def sciana_palac():
    """Ściana gabinetu w Pałacu Zimowym (2200 × 900): szaroniebieski tynk, białe płyciny, złocone pilastry z kapitelami,
    fryz pod sufitem, ciemnoczerwony cokół ze złotą listwą."""
    w, h = 2200, 900
    base = (184, 198, 210)
    parts = [(rect(0, 0, w, h), base, dict(kind="gladki", edge=0, shade=0.1, contrast=0.7))]
    for n in range(8):
        x = 40 + n * 275
        parts += [(rect(x + 34, 150, x + 236, 600), (230, 232, 228), dict(edge=2)), (rect(x + 48, 164, x + 222, 586), base)]
    for n in range(9):
        x = 32 + n * 275
        parts += [(rect(x - 18, 90, x + 18, 760), (236, 226, 200), dict(edge=2)), (rect(x - 26, 70, x + 26, 100), GOLD),
                  (rect(x - 26, 740, x + 26, 772), GOLD), (rect(x - 5, 110, x + 5, 736), _shade(GOLD, 0.92))]
    parts += [(rect(0, 0, w, 64), (236, 226, 200)), (rect(0, 54, w, 68), GOLD), (rect(0, 764, w, h), (112, 48, 42), dict(edge=2)),
              (rect(0, 760, w, 774), GOLD)]
    for x in range(0, w, 44):  # meander fryzu
        parts.append((rect(x + 8, 14, x + 30, 22), _shade(GOLD, 0.9)))
    return Sprite(stack_d(w, h, parts, seed=210), "sciana-palac", rim=0, clean=False, pad=0)


@lru_cache(None)
def okno_palac(noc=False):
    """Wysokie okno zakończone łukiem (440 × 720) z karmazynowymi zasłonami i złotymi chwostami; za szybą Newa, drugi brzeg
    i złota iglica twierdzy (Pietropawłowskiej)."""
    w, h = 440, 720
    niebo = (40, 46, 82) if noc else (196, 210, 226)
    woda = (30, 40, 70) if noc else (120, 140, 160)
    parts = [(poly([(70, h - 40), (70, 200), (110, 110), (220, 60), (330, 110), (370, 200), (370, h - 40)]), (236, 230, 214), dict(edge=2)),
             (poly([(90, h - 60), (90, 210), (124, 130), (220, 86), (316, 130), (350, 210), (350, h - 60)]), niebo, dict(kind="gladki")),
             (rect(90, 470, 350, h - 60), woda, dict(kind="gladki")), (rect(90, 430, 350, 474), (150, 140, 120)),
             (rect(200, 300, 232, 436), (214, 196, 160)), (rect(208, 210, 224, 302), GOLD), (poly([(210, 212), (222, 212), (216, 130)]), GOLD)]
    parts += [(rect(214, 86, 226, h - 60), (236, 230, 214)), (rect(90, 330, 350, 342), (236, 230, 214))]  # szprosy
    for x0, x1, kier in ((0, 120, 1), (320, 440, -1)):  # zasłony
        parts += [(poly([(x0, 20), (x1, 20), (x1 - 30 * kier if kier > 0 else x0 + 30, h), (x0 if kier > 0 else x1, h)]), (150, 30, 42),
                   dict(edge=2, shade=0.25)),
                  (ell((x0 + x1) / 2, 420, 26, 40), GOLD)]
    parts += [(rect(-10, 0, w + 10, 36), GOLD), (rect(40, h - 44, w - 40, h - 24), (236, 226, 200))]
    return Sprite(stack_d(w, h, parts, seed=211 + noc), f"okno-palac-{noc}", rim=2, clean=False)


@lru_cache(None)
def orzel():
    """Złoty dwugłowy orzeł w owalnym kartuszu (herb imperium; 320 × 320)."""
    w = h = 320
    g = GOLD
    parts = [(ell(160, 160, 150, 150), (120, 30, 36), dict(edge=2)), (ell(160, 160, 134, 134), (150, 40, 44)),
             (poly([(160, 110), (40, 70), (60, 140), (30, 170), (90, 190), (120, 230), (160, 250), (200, 230), (230, 190), (290, 170),
                    (260, 140), (280, 70)]), g, dict(edge=2)),
             (ell(120, 96, 20, 18), g), (ell(200, 96, 20, 18), g), (poly([(100, 94), (84, 100), (100, 104)]), g), (poly([(220, 94), (236, 100), (220, 104)]), g),
             (poly([(136, 60), (160, 30), (184, 60)]), g), (rect(150, 230, 170, 290), g), (poly([(140, 290), (160, 270), (180, 290)]), g)]
    return Sprite(stack_d(w, h, parts, seed=212), "orzel", rim=2, clean=False)


@lru_cache(None)
def portret():
    """Portret w złotej ramie (260 × 340): ciemne tło, popiersie w zielonym mundurze z epoletami, twarz bez rysów (nie konkretna
    osoba)."""
    w, h = 260, 340
    parts = [(rect(0, 0, w, h), GOLD, dict(edge=2)), (rect(18, 18, w - 18, h - 18), (52, 44, 40)),
             (poly([(50, h - 18), (70, 230), (130, 206), (190, 230), (210, h - 18)]), (40, 70, 54)), (rect(60, 222, 92, 236), GOLD),
             (rect(168, 222, 200, 236), GOLD), (ell(130, 170, 36, 44), (210, 184, 160)), (ell(130, 132, 38, 20), (120, 100, 80))]
    return Sprite(stack_d(w, h, parts, seed=213), "portret", rim=2, clean=False)


@lru_cache(None)
def parkiet():
    """Parkiet w jodełkę (2200 × 220); klepki rysowane wprost na arkuszu."""
    w, h = 2200, 220
    kol = (150, 104, 66)

    def detale(d, im):
        for row in range(6):
            for n in range(56):
                x, y = n * 40, row * 40
                if (n + row) % 2:
                    d.polygon([(x, y), (x + 36, y + 18), (x + 36, y + 36), (x, y + 18)], fill=_shade(kol, 1.05) + (255,),
                              outline=_shade(kol, 0.7) + (255,))
                else:
                    d.polygon([(x, y + 18), (x + 36, y), (x + 36, y + 18), (x, y + 36)], fill=_shade(kol, 0.92) + (255,),
                              outline=_shade(kol, 0.7) + (255,))
    return Sprite(stack_d(w, h, [(rect(0, 0, w, h), _shade(kol, 0.8))], seed=214, detale=detale), "parkiet", rim=0, clean=False, pad=0)


MEBLE["biurko_palac"] = (460, 230, [(rect(0, 0, 460, 30), (44, 112, 86)), (rect(0, 26, 460, 34), GOLD), (rect(10, 34, 150, 230), (74, 38, 30)),
                                    (rect(310, 34, 450, 230), (74, 38, 30)), (rect(30, 70, 130, 100), (96, 52, 40)), (rect(330, 70, 430, 100), (96, 52, 40)),
                                    (ell(80, 85, 6, 6), GOLD), (ell(380, 85, 6, 6), GOLD)])
MEBLE["stol_palac"] = (360, 200, [(rect(0, 0, 360, 24), (50, 96, 62)), (rect(0, 20, 360, 30), GOLD), (rect(20, 30, 40, 200), (74, 38, 30)),
                                  (rect(320, 30, 340, 200), (74, 38, 30)), (ell(30, 196, 14, 6), GOLD), (ell(330, 196, 14, 6), GOLD)])


# ---------- oblężenie Achulgo ----------

@lru_cache(None)
def szance():
    """Szańce baterii (1800 × 230): nasyp z ziemi, na nim rząd koszy faszynowych (pionowa wiklina) z ziemią na górze."""
    w, h = 1800, 230
    ziemia, wik = (120, 96, 66), (150, 118, 70)
    parts = [(poly([(0, h), (0, 150), (200, 120), (1600, 120), (1800, 150), (1800, h)]), ziemia, dict(edge=3, shade=0.2))]
    for n in range(24):
        x0 = 30 + n * 74
        parts += [(rect(x0, 40, x0 + 64, 132), wik, dict(edge=2)), (ell(x0 + 32, 42, 32, 10), _shade(ziemia, 0.9))]
        for k in range(5):
            parts.append((rect(x0 + 6 + k * 12, 50, x0 + 9 + k * 12, 128), _shade(wik, 0.72)))
    return Sprite(stack_d(w, h, parts, seed=220), "szance", rim=2, clean=False)


@lru_cache(None)
def brama_twierdzy():
    """Mur twierdzy z bramą (1500 × 560): kamienie, blanki, strzelnice, łukowa brama z drewnianymi wrotami (zamknięta)."""
    w, h = 1500, 560
    kam = (176, 158, 128)
    parts = [(rect(0, 80, w, h), kam, dict(edge=3, shade=0.16))]
    parts += [(rect(x + 6, 40, x + 46, 84), kam) for x in range(0, w, 70)]
    parts += [(poly([(600, h), (600, 300), (650, 230), (750, 200), (850, 230), (900, 300), (900, h)]), (90, 70, 52)),
              (poly([(620, h), (620, 310), (660, 250), (750, 222), (840, 250), (880, 310), (880, h)]), (120, 82, 52), dict(edge=2))]

    def detale(d, im):
        r = random.Random(9)
        for row in range(10):
            for n in range(22):
                cx, cy = n * 70 + (35 if row % 2 else 0) + r.uniform(-5, 5), 110 + row * 46
                if 590 < cx < 910 and cy > 190:
                    continue
                c = _shade(kam, r.uniform(0.86, 1.08))
                d.ellipse([cx - 30, cy - 18, cx + 30, cy + 18], fill=c + (255,), outline=_shade(kam, 0.7) + (255,))
        for x in (200, 420, 1080, 1300):
            d.rectangle([x, 180, x + 14, 240], fill=(50, 40, 34, 255))
        d.rectangle([746, 230, 754, h], fill=(80, 56, 38, 255))
        for yy in (330, 420, 500):
            d.rectangle([620, yy, 880, yy + 10], fill=(80, 56, 38, 255))
    return Sprite(stack_d(w, h, parts, seed=221, detale=detale), "brama-twierdzy", rim=2, clean=False)


SKALA_JASKINIE = ((380, 390), (760, 430), (1140, 380))  # środki wejść do jaskiń na arkuszu skala_sciana (1700 × 760)


@lru_cache(None)
def skala_sciana():
    """Skała Achulgo z bliska (1700 × 760): ściana z półkami, trzy ciemne wejścia do jaskiń (SKALA_JASKINIE), u góry płaska
    krawędź pod mur twierdzy."""
    w, h = 1700, 760
    kol = (146, 124, 98)
    r = random.Random(13)
    parts = [(poly([(0, h), (0, 120), (300, 90), (900, 70), (1500, 96), (1700, 130), (1700, h)]), kol, dict(edge=3, shade=0.22, contrast=1.2))]
    for n in range(12):
        x0, y0 = r.uniform(0, w - 200), r.uniform(150, 700)
        parts.append((_band((x0, y0), (x0 + r.uniform(120, 260), y0 + r.uniform(-20, 20)), 8), _shade(kol, 1.18)))
        parts.append((_band((x0 + 20, y0 + 12), (x0 + r.uniform(100, 220), y0 + 16), 5), _shade(kol, 0.7)))
    for cx, cy in SKALA_JASKINIE:
        parts += [(poly([(cx - 70, cy + 80), (cx - 64, cy - 10), (cx - 30, cy - 60), (cx + 30, cy - 62), (cx + 66, cy - 8), (cx + 72, cy + 80)]),
                   (34, 26, 22)), (rect(cx - 90, cy + 76, cx + 92, cy + 92), _shade(kol, 1.2))]
    return Sprite(stack_d(w, h, parts, seed=222), "skala-sciana", rim=3, clean=False)


@lru_cache(None)
def grunt(kolor=(128, 112, 90)):
    """Ubita ziemia sceny (2200 × 200): nierówny wierzch, rozrzucone kamyki i kępki — bez siatki płyt (bruk wyglądał jak murek)."""
    w, h = 2200, 200
    r = random.Random(21)
    top = [(x, 14 + 8 * math.sin(x / 90) + r.uniform(-3, 3)) for x in range(0, w + 20, 20)]
    parts = [(poly(top + [(w, h), (0, h)]), kolor, dict(edge=2, shade=0.22, contrast=0.9))]
    for _ in range(70):
        x, y = r.uniform(0, w), r.uniform(30, 190)
        parts.append((ell(x, y, r.uniform(5, 14), r.uniform(3, 8)), _shade(kolor, r.uniform(0.75, 1.25))))
    return Sprite(stack_d(w, h, parts, seed=230), f"grunt-{kolor}", rim=0, clean=False, pad=0)


# ---------- dekoracje 2, akty III–VI ----------

@lru_cache(None)
def sala_tyflis():
    """Sala pałacu namiestnika w Tyflisie (2100 × 900): ochrowa ściana, trzy okna z ostrym łukiem i drewnianą kratką,
    wielki dywan na ścianie, belkowany strop — inna niż sala balowa w Petersburgu."""
    w, h = 2100, 900
    sc, drewno = (214, 172, 112), (112, 72, 44)
    parts = [(rect(0, 0, w, h), sc, dict(kind="gladki", shade=0.12, contrast=0.8))]
    for n in range(9):
        parts.append((rect(n * 240, 0, n * 240 + 40, 70), drewno))
    parts.append((rect(0, 60, w, 84), _shade(drewno, 0.85)))
    for x0 in (220, 1630):
        parts += [(poly([(x0, 640), (x0, 300), (x0 + 50, 220), (x0 + 125, 180), (x0 + 200, 220), (x0 + 250, 300), (x0 + 250, 640)]), (150, 186, 200)),
                  (poly([(x0 - 14, 300), (x0 + 50, 206), (x0 + 125, 166), (x0 + 200, 206), (x0 + 264, 300), (x0 + 250, 304), (x0 + 196, 222),
                         (x0 + 125, 186), (x0 + 54, 222), (x0, 304)]), drewno)]
        for k in range(1, 6):
            parts.append((rect(x0 + k * 42 - 3, 230, x0 + k * 42 + 3, 640), drewno))
        for k in range(1, 8):
            parts.append((rect(x0, 300 + k * 44 - 3, x0 + 250, 300 + k * 44 + 3), drewno))
    parts += [(rect(780, 160, 1320, 640), (150, 44, 40), dict(edge=2)), (rect(810, 190, 1290, 610), (170, 64, 50))]  # dywan
    for k in range(5):
        cx = 900 + k * 75
        parts.append((poly([(cx, 300), (cx + 30, 400), (cx, 500), (cx - 30, 400)]), (40, 54, 100) if k % 2 else (220, 180, 90)))
    for x in range(810, 1290, 24):
        parts += [(rect(x, 640, x + 6, 668), (220, 196, 150)), (rect(x, 162, x + 6, 190), (220, 196, 150))]
    parts.append((rect(0, 760, w, h), (96, 64, 44)))
    return Sprite(stack_d(w, h, parts, seed=240), "sala-tyflis", rim=2, clean=False)


@lru_cache(None)
def sala_tronowa():
    """Sala tronowa (2100 × 900): czerwone obicia ścian ze złotymi ramami, pośrodku tron pod baldachimem z dwugłowym orłem,
    czerwony chodnik — inna niż sala balowa kadetów."""
    w, h = 2100, 900
    czer = (150, 36, 40)
    parts = [(rect(0, 0, w, h), (226, 214, 190), dict(kind="gladki", contrast=0.7))]
    for n in range(7):
        x = 40 + n * 300
        parts += [(rect(x, 120, x + 240, 700), GOLD, dict(edge=2)), (rect(x + 14, 134, x + 226, 686), czer)]
    parts += [(poly([(800, 80), (1300, 80), (1340, 160), (760, 160)]), czer, dict(edge=2)), (rect(760, 150, 1340, 170), GOLD),
              (poly([(800, 160), (830, 640), (780, 640)]), _shade(czer, 0.8)), (poly([(1300, 160), (1320, 640), (1270, 640)]), _shade(czer, 0.8))]
    parts += [(rect(960, 380, 1140, 700), GOLD, dict(edge=2)), (rect(980, 300, 1120, 400), GOLD), (rect(990, 410, 1110, 640), czer),
              (ell(1050, 300, 70, 40), GOLD)]  # tron
    parts += [(rect(0, 700, w, h), (176, 150, 120)), (poly([(900, 700), (1200, 700), (1500, h), (600, h)]), czer)]
    return Sprite(stack_d(w, h, parts, seed=241), "sala-tronowa", rim=2, clean=False)


IZBY = {0: ((214, 200, 176), "dywan"), 1: ((226, 222, 210), "polka"), 2: ((150, 132, 112), "skrzynia")}


@lru_cache(None)
def izba_sciana(v=0):
    """Ściana izby w aule (2100 × 860), trzy różne pokoje jednego domu: 0 — izba Szamila (bielony kamień, nisza, dywan na
    ścianie), 1 — pokój syna (biała ściana, półka z rosyjskimi książkami), 2 — sypialnia nocą (ciemny kamień, rzeźbiona
    skrzynia przy ścianie)."""
    w, h = 2100, 860
    sc, akc = IZBY[v]
    r = random.Random(60 + v)
    parts = [(rect(0, 0, w, h), sc, dict(shade=0.18, contrast=1.0))]
    for _ in range(40):
        x, y = r.uniform(0, w), r.uniform(0, h - 120)
        parts.append((ell(x, y, r.uniform(30, 60), r.uniform(18, 30)), _shade(sc, r.uniform(0.92, 1.04))))
    parts += [(rect(0, 0, w, 50), (90, 62, 42)), (rect(0, h - 110, w, h), _shade(sc, 0.7))]
    if akc == "dywan":
        parts += [(rect(300, 160, 760, 620), (130, 40, 36), dict(edge=2)), (rect(326, 186, 734, 594), (166, 70, 48))]
        for k in range(4):
            cy = 240 + k * 100
            parts.append((poly([(530, cy - 40), (600, cy), (530, cy + 40), (460, cy)]), (220, 180, 90) if k % 2 else (40, 60, 100)))
        parts += [(poly([(1300, 560), (1300, 300), (1350, 240), (1400, 300), (1400, 560)]), _shade(sc, 0.6)),
                  (rect(1300, 420, 1400, 432), (120, 84, 54))]
    elif akc == "polka":
        parts += [(rect(260, 240, 760, 260), (120, 84, 54)), (rect(260, 420, 760, 440), (120, 84, 54))]
        for k in range(14):
            x = 270 + k * 34
            parts.append((rect(x, 160 + (k % 3) * 8, x + 28, 240), [(150, 40, 40), (40, 70, 110), (60, 100, 70), (170, 140, 80)][k % 4]))
            parts.append((rect(x, 340 + (k % 2) * 10, x + 28, 420), [(60, 100, 70), (150, 40, 40), (170, 140, 80), (40, 70, 110)][k % 4]))
    else:
        parts += [(rect(1240, 520, 1640, 750), (100, 64, 40), dict(edge=2)), (rect(1240, 500, 1640, 530), (80, 50, 30))]
        for k in range(5):
            parts.append((ell(1300 + k * 80, 640, 26, 40), (130, 90, 58)))
    return Sprite(stack_d(w, h, parts, seed=242 + v), f"izba-{v}", rim=0, clean=False, pad=0)


@lru_cache(None)
def okienko(noc=False):
    """Małe okienko izby w aule (220 × 260): gruba drewniana rama, okiennice, za szybą góry albo noc."""
    w, h = 220, 260
    szyba = (40, 48, 80) if noc else (176, 200, 214)
    parts = [(rect(30, 30, 190, 230), (110, 74, 46), dict(edge=2)), (rect(46, 46, 174, 214), szyba, dict(kind="gladki")),
             (rect(106, 46, 114, 214), (110, 74, 46)), (rect(46, 126, 174, 134), (110, 74, 46)),
             (rect(0, 20, 34, 240), (130, 90, 58), dict(edge=2)), (rect(186, 20, 220, 240), (130, 90, 58), dict(edge=2))]
    if not noc:
        parts.append((poly([(46, 214), (46, 150), (90, 110), (130, 150), (174, 120), (174, 214)]), (220, 226, 236)))
    return Sprite(stack_d(w, h, parts, seed=245 + noc), f"okienko-{noc}", rim=2, clean=False)


@lru_cache(None)
def dywan(v=0):
    """Dywan na podłodze izby (1500 × 130), wzór w romby."""
    w, h = 1500, 130
    baza = ((140, 44, 40), (60, 70, 110), (120, 70, 40))[v % 3]
    parts = [(rect(0, 0, w, h), baza, dict(edge=2)), (rect(14, 12, w - 14, h - 12), _shade(baza, 1.15))]
    for k in range(18):
        cx = 50 + k * 80
        parts.append((poly([(cx, 30), (cx + 30, 65), (cx, 100), (cx - 30, 65)]), (220, 180, 90) if k % 2 else _shade(baza, 0.7)))
    return Sprite(stack_d(w, h, parts, seed=248 + v), f"dywan-{v}", rim=1, clean=False)


@lru_cache(None)
def straznica():
    """Kozacka strażnica nad Terekiem (300 × 620): drewniana budka na wysokich słupach, drabina, daszek."""
    d = (120, 88, 58)
    parts = [(rect(40, 220, 60, 620), d), (rect(240, 220, 260, 620), d), (_band((50, 620), (250, 300), 14), d), (_band((250, 620), (50, 300), 14), d),
             (rect(20, 120, 280, 230), (150, 112, 74), dict(edge=2)), (poly([(0, 130), (150, 30), (300, 130)]), (100, 76, 50), dict(edge=2)),
             (rect(120, 150, 180, 200), (50, 40, 32)), (rect(70, 380, 76, 620), d), (rect(110, 380, 116, 620), d)]
    for y in range(400, 620, 36):
        parts.append((rect(70, y, 116, y + 6), d))
    return Sprite(stack_d(300, 620, parts, seed=250), "straznica", rim=2, clean=False)


@lru_cache(None)
def cerkiew():
    """Cerkiew w oddali (Kaługa, 420 × 380): biała bryła, zielone dachy, złote cebulaste kopuły z krzyżami — tło miasta."""
    bial, ziel = (236, 232, 222), (90, 130, 96)
    parts = [(rect(80, 200, 340, 380), bial, dict(edge=2)), (rect(150, 120, 270, 210), bial), (ell(210, 110, 50, 44), GOLD),
             (poly([(170, 100), (210, 30), (250, 100)]), GOLD), (rect(206, 0, 214, 34), GOLD), (rect(196, 10, 224, 16), GOLD)]
    for cx in (110, 310):
        parts += [(rect(cx - 26, 170, cx + 26, 230), bial), (ell(cx, 162, 26, 24), ziel), (poly([(cx - 18, 156), (cx, 118), (cx + 18, 156)]), ziel)]
    for x in (120, 180, 240, 300):
        parts.append((rect(x, 260, x + 20, 320), (90, 100, 120)))
    return Sprite(stack_d(420, 380, parts, seed=251), "cerkiew", rim=2, clean=False)


@lru_cache(None)
def regaly(v=0):
    """Ściana regałów z książkami (2100 × 860): biblioteka i pracownie pisarzy; v — układ i barwa drewna. Grzbiety książek
    rysowane wprost na arkuszu (setki kawałków papieru liczyły się 2 minuty)."""
    w, h = 2100, 860
    drewno = ((96, 62, 40), (150, 110, 70))[v % 2]
    parts = [(rect(0, 0, w, h), _shade(drewno, 0.7), dict(shade=0.15))]
    parts += [(rect(0, 30 + row * 130 + 110, w, 30 + row * 130 + 126), drewno) for row in range(6)]
    parts += [(rect(x, 0, x + 20, h), drewno) for x in range(0, w, 350)]

    def detale(d, im):
        r = random.Random(70 + v)
        kolory = [(150, 40, 40), (40, 70, 110), (60, 100, 70), (170, 140, 80), (90, 60, 50), (200, 190, 160)]
        for row in range(6):
            y0 = 30 + row * 130
            x = 24.0
            while x < w - 30:
                bw, bh = r.uniform(18, 34), r.uniform(70, 106)
                if int(x) % 350 > 330:
                    x += 24
                    continue
                c = _shade(r.choice(kolory), r.uniform(0.8, 1.05))
                d.rectangle([x, y0 + 110 - bh, x + bw - 3, y0 + 110], fill=c + (255,), outline=_shade(c, 0.7) + (255,))
                d.line([(x + 3, y0 + 118 - bh), (x + bw - 6, y0 + 118 - bh)], fill=(220, 200, 140, 200), width=2)
                x += bw
    return Sprite(stack_d(w, h, parts, seed=252 + v, detale=detale), f"regaly-{v}", rim=0, clean=False, pad=0)


@lru_cache(None)
def namiot_wnetrze():
    """Wnętrze namiotu polowego (2100 × 860): płótno ze szwami, dwa maszty, odchylona poła z widokiem na las."""
    w, h = 2100, 860
    pl = (214, 200, 164)
    parts = [(rect(0, 0, w, h), pl, dict(kind="gnieciony", shade=0.15, contrast=0.9))]
    for x in range(0, w, 170):
        parts.append((rect(x, 0, x + 6, h), _shade(pl, 0.82)))
    parts += [(rect(560, 0, 590, h), (110, 80, 52)), (rect(1510, 0, 1540, h), (110, 80, 52)),
              (poly([(1700, h), (1760, 360), (1860, 300), (1960, 360), (2020, h)]), (70, 96, 64)),
              (poly([(1680, h), (1760, 340), (1800, 330), (1740, h)]), _shade(pl, 0.9)), (rect(0, h - 90, w, h), (120, 100, 74))]
    return Sprite(stack_d(w, h, parts, seed=253), "namiot-wnetrze", rim=0, clean=False, pad=0)


@lru_cache(None)
def okno_londyn():
    """Okno gilotynowe pracowni w Londynie (300 × 420): białe szprosy, za szybą szare niebo i dachy z kominami."""
    w, h = 300, 420
    parts = [(rect(0, 0, w, h), (236, 232, 222), dict(edge=2)), (rect(20, 20, w - 20, h - 20), (176, 186, 196), dict(kind="gladki")),
             (poly([(20, 300), (80, 260), (120, 280), (160, 240), (220, 270), (280, 250), (280, h - 20), (20, h - 20)]), (120, 110, 104))]
    for x in (100, 200):
        parts.append((rect(x - 4, 20, x + 4, h - 20), (236, 232, 222)))
    parts += [(rect(20, 206, w - 20, 216), (236, 232, 222)), (rect(130, 210, 146, 250), (110, 80, 70))]
    return Sprite(stack_d(w, h + 10, parts, seed=254), "okno-londyn", rim=2, clean=False)


@lru_cache(None)
def panele_sosna():
    """Ściana pracowni Herberta (2100 × 860): pionowe deski sęczastej sosny, okno z żaluzjami, korkowa tablica z kartkami."""
    w, h = 2100, 860
    sos = (196, 150, 96)
    parts = [(rect(0, 0, w, h), sos, dict(shade=0.12)), (rect(1500, 120, 1900, 520), (236, 232, 222), dict(edge=2)),
             (rect(300, 160, 760, 460), (176, 134, 90), dict(edge=2))]

    def detale(d, im):
        r = random.Random(77)
        for x in range(0, w, 90):
            if 1496 < x < 1904 and False:
                continue
            d.line([(x, 0), (x, h)], fill=_shade(sos, 0.7) + (255,), width=4)
            for _ in range(2):
                cx, cy = x + r.uniform(20, 70), r.uniform(40, 800)
                d.ellipse([cx - 7, cy - 10, cx + 7, cy + 10], fill=_shade(sos, 0.6) + (255,))
        d.rectangle([1500, 120, 1900, 520], fill=(236, 232, 222, 255))
        for y in range(136, 506, 22):
            d.rectangle([1516, y, 1884, y + 14], fill=(220, 214, 200, 255), outline=(190, 184, 170, 255))
        d.rectangle([300, 160, 760, 460], fill=(176, 134, 90, 255))
        for k in range(6):
            x0, y0 = 330 + (k % 3) * 140, 190 + (k // 3) * 130
            d.rectangle([x0, y0, x0 + 100, y0 + 100], fill=(240, 236, 222, 255), outline=(200, 190, 170, 255))
            d.ellipse([x0 + 44, y0 + 4, x0 + 56, y0 + 16], fill=(170, 40, 40, 255))
    return Sprite(stack_d(w, h, parts, seed=255, detale=detale), "panele-sosna", rim=0, clean=False, pad=0)


MEBLE["stol_polowy"] = (360, 200, [(rect(0, 0, 360, 18), (170, 140, 100)), (_band((40, 18), (320, 200), 14), (120, 90, 60)),
                                   (_band((320, 18), (40, 200), 14), (120, 90, 60))])
MEBLE["biurko_pisarza"] = (460, 230, [(rect(0, 0, 460, 26), (176, 130, 84)), (rect(10, 26, 170, 230), (150, 108, 68)), (rect(400, 26, 440, 230), (150, 108, 68)),
                                      (rect(30, 60, 150, 110), (176, 130, 84)), (rect(30, 130, 150, 180), (176, 130, 84))])
MEBLE["lozko_kz"] = (520, 200, [(rect(0, 70, 520, 170), (140, 50, 44), dict(edge=2)), (rect(0, 60, 520, 84), (220, 180, 90)), (rect(0, 20, 24, 200), (96, 64, 40)),
                                (rect(496, 50, 520, 200), (96, 64, 40)), (ell(80, 64, 60, 26), (230, 224, 206))])
MEBLE["skrzynka"] = (220, 160, [(rect(0, 0, 220, 20), (110, 70, 42)), (rect(6, 20, 214, 160), (96, 60, 36), dict(edge=2)),
                                (ell(60, 90, 26, 40), (130, 88, 56)), (ell(160, 90, 26, 40), (130, 88, 56)), (rect(100, 70, 120, 110), GOLD)])
