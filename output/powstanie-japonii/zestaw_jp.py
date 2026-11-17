"""Zestaw filmu „Syn słońca — powstanie Japonii”: lalki w stylu kofun, front teatru w kształcie bramy torii i wycinanki
tego filmu.

Papiery, faktury, darte krawędzie, krajobraz (góry, chmury, sosny, słońce, fale), nitki i wysuwanie od dołu bierze
z output/pierwszy-cesarz/zestaw.py — ten sam styl i to samo światło. Postacie są wycinane kodem, bo wycinanki PNG to
chińscy uczeni (księga świata, D2).

Lalka = korpus (głowa, szata, nogi) + dwie ręce na zawiasie w barku. Wszystkie trzy arkusze mają stały układ
współrzędnych (crop=False), więc bark i dłoń liczą się z tych samych liczb co rysunek.
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
from zestaw import (FONT_PL, FONT_ZH, PL_IDX, ZH_IDX, S, black, ell, flame, glow, glue, glyphs, hang, moon, over,  # noqa: E402,F401
                    paper, piece, poly, prop, raw, rect, reeds, rise, rough_mask, sky, spears, stack, stage_floor, tag, tag_zh,
                    texture, waves, _sheet)

P = Z0.P
JEZYK = Z0.JEZYK


def tr(txt):
    """Napis na wycinku w języku filmu (JEZYK=en: kwestie_en.ETYKIETY tego filmu). Podmienia zestaw.tr, więc zawieszki
    i tabliczki z zestaw.tag też idą przez tłumaczenie Japonii, a nie „Pierwszego cesarza” (wytyczne 1.13)."""
    if JEZYK != "en":
        return txt
    sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"))
    from kwestie_en import ETYKIETY
    return ETYKIETY.get(txt, txt)


Z0.tr = tr
GOLD = (210, 168, 82)
SHU = (196, 64, 40)  # cynober bram torii
INK = (40, 28, 24)
SKORA = (236, 206, 170)


# ---------- lalki w stylu kofun ----------

FIG_W, FIG_H, STOPA, BIODRO, CZUBEK = 300, 690, 676, 412, 62
BARK = {"przod": (182, 222), "tyl": (120, 222)}  # zawias ręki na korpusie
RAMIE_W, RAMIE_H, RAMIE_ZAWIAS, DLON = 110, 300, (55, 26), (55, 232)

BAZA = dict(tunika=(236, 228, 210), pas=(170, 40, 34), spodnie=(222, 214, 198), wiazanie=None, buty=(74, 52, 38),
            wlosy=(34, 28, 28), fryzura="mizura", kobieta=False, broda=False, wasy=False, naszyjnik=(70, 140, 96), miecz=False,
            opaska=None, aureola=None, wzor=None, wzor_kolor=None, skora=SKORA, nogi=0, szer=1.0, oczy="otwarte",
            zbroja=None, kolnierz=None, rekaw=None)

LALKI = {
    "iwarebiko": dict(tunika=(238, 232, 214), pas=(176, 42, 34), wzor="trojkaty", wzor_kolor=(176, 42, 34), miecz=True),
    "jimmu": dict(tunika=(238, 232, 214), pas=(176, 42, 34), wzor="trojkaty", wzor_kolor=(176, 42, 34), miecz=True, opaska=GOLD, broda=True),
    "jimmu_stary": dict(tunika=(238, 232, 214), pas=(176, 42, 34), wzor="trojkaty", wzor_kolor=(176, 42, 34), miecz=True, opaska=GOLD,
                        broda=True, wlosy=(196, 192, 186)),
    "itsuse": dict(tunika=(70, 104, 156), pas=(220, 200, 150), spodnie=(212, 204, 186), miecz=True, wasy=True),
    # syn Jimmu (Suizei) — młody, bez opaski władcy, dopóki nie przejmie skarbów; cesarze w linii — każdy w innym stroju,
    # z opaską; cesarz z 2019 roku w brązowo-pomarańczowej szacie koronacyjnej i czarnym nakryciu głowy (wytyczne 1.6)
    "syn_cesarza": dict(tunika=(214, 196, 150), pas=(176, 42, 34), wzor="pasy", wzor_kolor=(176, 42, 34), miecz=True),
    "cesarz2": dict(tunika=(196, 170, 120), pas=(120, 40, 34), opaska=GOLD, wasy=True),
    "cesarz3": dict(tunika=(150, 120, 160), pas=(210, 168, 82), opaska=GOLD, broda=True),
    "cesarz126": dict(tunika=(150, 92, 44), pas=(120, 70, 30), spodnie=(236, 228, 210), opaska=(30, 26, 24)),
    "brat2": dict(tunika=(84, 128, 86), pas=(226, 206, 150), spodnie=(214, 206, 188), miecz=True),
    "brat3": dict(tunika=(146, 100, 62), pas=(60, 46, 40), spodnie=(214, 206, 188), miecz=True),
    "izanagi": dict(tunika=(240, 236, 224), pas=(120, 120, 150), wlosy=(200, 196, 190), broda=True, wasy=True, wzor="pasy",
                    wzor_kolor=(120, 120, 150)),
    "izanami": dict(tunika=(186, 52, 42), pas=(236, 210, 150), spodnie=(232, 206, 190), kobieta=True, fryzura="dlugie",
                    wzor="kropki", wzor_kolor=(236, 210, 150)),
    "amaterasu": dict(tunika=(232, 182, 72), pas=(186, 52, 42), spodnie=(244, 236, 220), kobieta=True, fryzura="dlugie",
                      aureola=(232, 150, 60), opaska=GOLD, wzor="kropki", wzor_kolor=(250, 236, 190)),
    "tsukuyomi": dict(tunika=(150, 166, 196), pas=(70, 80, 120), spodnie=(206, 210, 222), wlosy=(46, 44, 60)),
    "susanoo": dict(tunika=(40, 50, 96), pas=(150, 36, 30), spodnie=(176, 170, 160), fryzura="dzikie", broda=True, wasy=True, miecz=True),
    "uzume": dict(tunika=(226, 124, 50), pas=(60, 110, 90), spodnie=(246, 226, 196), kobieta=True, fryzura="kok", wzor="kropki",
                  wzor_kolor=(250, 226, 160)),
    "silacz": dict(tunika=(120, 84, 54), pas=(40, 34, 30), spodnie=(196, 182, 160), broda=True, szer=1.22, naszyjnik=None),
    "bog1": dict(tunika=(150, 120, 170), pas=(240, 220, 170), spodnie=(222, 214, 198)),
    "bog2": dict(tunika=(96, 140, 140), pas=(230, 210, 150), spodnie=(222, 214, 198), broda=True),
    "bog3": dict(tunika=(196, 160, 90), pas=(120, 50, 40), spodnie=(222, 214, 198), kobieta=True, fryzura="dlugie"),
    "bog4": dict(tunika=(124, 70, 60), pas=(220, 200, 150), spodnie=(222, 214, 198), wlosy=(180, 176, 170), broda=True),
    "starzec": dict(tunika=(150, 132, 104), pas=(90, 70, 50), spodnie=(196, 186, 166), wlosy=(206, 202, 196), broda=True,
                    naszyjnik=None),
    "starucha": dict(tunika=(120, 104, 120), pas=(90, 70, 60), spodnie=(196, 186, 176), kobieta=True, fryzura="dlugie",
                     wlosy=(210, 206, 200), naszyjnik=None),
    "kushinada": dict(tunika=(240, 190, 170), pas=(186, 60, 60), spodnie=(246, 232, 216), kobieta=True, fryzura="dlugie"),
    "ninigi": dict(tunika=(244, 238, 222), pas=(210, 168, 82), spodnie=(236, 228, 210), wzor="pasy", wzor_kolor=(210, 168, 82),
                   miecz=True),
    "kwiat": dict(tunika=(236, 150, 172), pas=(250, 232, 236), spodnie=(250, 226, 230), kobieta=True, fryzura="dlugie",
                  wzor="kropki", wzor_kolor=(255, 240, 244)),
    "skala": dict(tunika=(128, 124, 118), pas=(90, 86, 80), spodnie=(166, 160, 150), kobieta=True, fryzura="dlugie",
                  naszyjnik=None),
    "nagasune": dict(tunika=(94, 62, 42), pas=(30, 26, 24), spodnie=(150, 120, 90), wiazanie=(30, 26, 24), broda=True, wasy=True,
                     miecz=True, nogi=110, wzor="trojkaty", wzor_kolor=(36, 30, 26), naszyjnik=(150, 60, 40)),
    "nigihayahi": dict(tunika=(108, 62, 124), pas=(226, 200, 140), spodnie=(214, 204, 190), miecz=True, wasy=True,
                       wzor="pasy", wzor_kolor=(226, 200, 140)),
    "takakuraji": dict(tunika=(136, 132, 124), pas=(70, 60, 50), spodnie=(190, 182, 168), naszyjnik=None, wasy=True),
    "wodz": dict(tunika=(120, 86, 56), pas=(40, 34, 30), spodnie=(176, 156, 126), broda=True, miecz=True),
    "brat_wodza": dict(tunika=(150, 118, 76), pas=(40, 34, 30), spodnie=(186, 166, 136), naszyjnik=None),
    "zona": dict(tunika=(92, 140, 104), pas=(236, 214, 160), spodnie=(236, 228, 210), kobieta=True, fryzura="dlugie",
                 wzor="kropki", wzor_kolor=(236, 214, 160)),
    "himiko": dict(tunika=(244, 240, 230), pas=(176, 42, 34), spodnie=(186, 52, 42), kobieta=True, fryzura="kok",
                   naszyjnik=(60, 150, 110), wzor="trojkaty", wzor_kolor=(176, 42, 34)),
    "wojownik": dict(tunika=(204, 196, 178), pas=(60, 50, 44), spodnie=(196, 188, 170), fryzura="helm", zbroja=(96, 98, 108),
                     naszyjnik=None, miecz=True),
    "wojownik2": dict(tunika=(176, 160, 132), pas=(60, 50, 44), spodnie=(186, 176, 156), fryzura="helm", zbroja=(118, 92, 64),
                      naszyjnik=None, miecz=True),
    "mysliwy": dict(tunika=(150, 112, 74), pas=(96, 70, 46), spodnie=(170, 136, 96), fryzura="luzne", naszyjnik=(200, 190, 170),
                    wzor="pasy", wzor_kolor=(96, 70, 46)),
    "mysliwy2": dict(tunika=(120, 96, 70), pas=(80, 60, 40), spodnie=(156, 124, 90), fryzura="luzne", broda=True, naszyjnik=None),
}


def spec(key):
    out = dict(BAZA)
    out.update(LALKI[key])
    return out


def _magatama(cx, cy, r, rot=0.0):
    """Klejnot w kształcie przecinka (magatama): koło z ogonkiem."""
    pts = []
    for k in range(0, 25):
        a = math.pi * 2 * k / 24
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    tail = [(cx + r * 0.9, cy + r * 0.2), (cx + r * 0.6, cy + r * 1.8), (cx - r * 0.2, cy + r * 2.4), (cx - r * 0.1, cy + r * 1.4),
            (cx - r * 0.6, cy + r * 0.6)]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    rt = lambda p: (cx + (p[0] - cx) * c - (p[1] - cy) * s, cy + (p[0] - cx) * s + (p[1] - cy) * c)
    circle = [rt(p) for p in pts]
    tl = [rt(p) for p in tail]
    return lambda d, sc: (d.polygon([(x * sc, y * sc) for x, y in circle], fill=255),
                          d.polygon([(x * sc, y * sc) for x, y in tl], fill=255))


def _band(p0, p1, wd):
    """Pas (pochwa miecza, drzewce) między punktami p0 i p1 o szerokości wd."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / L * wd / 2, (x1 - x0) / L * wd / 2
    return poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])


def _shade(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c)


def _korpus_img(s):
    L = s["nogi"]
    w, h = FIG_W, FIG_H + L
    Y = lambda y: y + L if y >= BIODRO else y
    PL = lambda pts: poly([(x, Y(y)) for x, y in pts])
    parts = []
    hair = s["wlosy"]
    if s["aureola"]:
        parts += [(ell(150, 126, 102, 102), s["aureola"], dict(edge=4)), (ell(150, 126, 82, 82), (246, 206, 110), dict(kind="gladki"))]
    if s["fryzura"] in ("dlugie", "kok") and s["kobieta"]:
        parts.append((poly([(106, 96), (196, 96), (214, 250), (210, 372), (150, 396), (90, 372), (86, 250)]), hair))
    if s["fryzura"] == "dzikie":
        r = random.Random(5)
        pts = []
        for k in range(17):
            a = math.pi * (0.95 + 1.1 * k / 16)
            rr = 70 + (24 if k % 2 else 0) + r.uniform(-6, 6)
            pts.append((152 + rr * math.cos(a), 122 + rr * 1.05 * math.sin(a)))
        pts += [(214, 190), (200, 250), (150, 240), (96, 250), (88, 190)]
        parts.append((poly(pts), hair))
    if s["fryzura"] == "luzne":
        parts.append((poly([(108, 90), (196, 90), (206, 200), (190, 236), (112, 236), (96, 200)]), hair))
    parts.append((rect(136, 158, 166, 216), _shade(s["skora"], 0.92)))  # szyja
    sp = s["spodnie"]
    tie = s["wiazanie"] or s["pas"]
    if s["kobieta"]:
        parts.append((PL([(84, 372), (216, 372), (240, 672), (60, 672)]), sp, dict(edge=2, shade=0.15)))
        parts.append((PL([(108, 660), (150, 660), (162, 676), (106, 676)]), s["buty"]))
    else:
        parts += [(PL([(84, 404), (152, 404), (156, 528), (80, 528)]), sp, dict(edge=2)),
                  (PL([(148, 404), (218, 404), (222, 528), (146, 528)]), _shade(sp, 0.92), dict(edge=2)),
                  (PL([(98, 534), (140, 534), (136, 656), (102, 656)]), (226, 220, 206)),
                  (PL([(162, 534), (204, 534), (200, 656), (166, 656)]), (214, 208, 194)),
                  (PL([(86, 518), (152, 518), (150, 540), (88, 540)]), tie),
                  (PL([(150, 518), (216, 518), (214, 540), (152, 540)]), _shade(tie, 0.9)),
                  (PL([(92, 650), (142, 650), (160, 662), (156, 676), (92, 676)]), s["buty"]),
                  (PL([(156, 650), (206, 650), (224, 662), (220, 676), (156, 676)]), _shade(s["buty"], 0.9))]
    tun = s["tunika"]
    if s["kobieta"]:
        parts.append((poly([(98, 204), (202, 204), (210, 300), (218, 396), (82, 396), (90, 300)]), tun, dict(edge=2)))
    else:
        parts.append((poly([(96, 204), (204, 204), (214, 300), (226, 448), (74, 448), (86, 300)]), tun, dict(edge=2)))
    if s["zbroja"]:
        z = s["zbroja"]
        parts += [(poly([(92, 212), (208, 212), (214, 352), (86, 352)]), z, dict(contrast=1.2)),
                  (poly([(82, 352), (218, 352), (230, 452), (70, 452)]), _shade(z, 0.86), dict(contrast=1.2))]
    hem = 396 if s["kobieta"] else 448
    wz, wk = s["wzor"], s["wzor_kolor"] or s["pas"]
    if wz == "pasy":
        parts += [(rect(84, hem - 34, 216, hem - 26), wk, dict(rough=0.8)), (rect(84, hem - 18, 216, hem - 12), wk, dict(rough=0.8))]
    elif wz == "trojkaty" and not s["zbroja"]:
        for x in range(82, 214, 16):
            parts.append((poly([(x, hem - 4), (x + 8, hem - 20), (x + 16, hem - 4)]), wk, dict(rough=0.7)))
    elif wz == "kropki":
        r = random.Random(9)
        for k in range(16):
            yy = r.uniform(230, hem - 20)
            half = 50 + (yy - 204) * 0.1
            parts.append((ell(150 + r.uniform(-half, half), yy, 4.5, 4.5), wk, dict(kind="gladki", rough=0.5)))
    kol = s["kolnierz"] or _shade(tun, 0.78)
    parts += [(poly([(118, 198), (184, 198), (178, 214), (124, 214)]), kol),
              (poly([(126, 204), (152, 204), (180, 300), (166, 306)]), kol)]
    if s["fryzura"] != "helm" or True:
        parts.append((poly([(84, 330), (216, 330), (218, 352), (82, 352)]), s["pas"]))
        parts += [(ell(170, 341, 14, 11), _shade(s["pas"], 1.1)),
                  (poly([(162, 350), (176, 350), (184, 420), (170, 424)]), s["pas"]),
                  (poly([(176, 350), (190, 350), (204, 412), (192, 418)]), _shade(s["pas"], 0.9))]
    if s["naszyjnik"]:
        for k in range(7):
            f = k / 6
            x = 120 + 60 * f
            y = 214 + 26 * math.sin(math.pi * f)
            parts.append((_magatama(x, y, 5.5, 30 + 40 * f), s["naszyjnik"], dict(kind="gladki", rough=0.4)))
    if s["miecz"]:
        parts += [(_band((100, 344), (50, 480), 13), (44, 36, 34), dict(contrast=1.2)),
                  (_band((50, 480), (46, 490), 13), GOLD),
                  (_band((104, 336), (96, 354), 18), GOLD),
                  (ell(108, 328, 10, 10), GOLD, dict(edge=0))]
    sk = s["skora"]
    if s["fryzura"] == "mizura":
        parts.append((ell(192, 148, 9, 24), _shade(hair, 0.85)))
    parts += [(ell(118, 132, 9, 13), _shade(sk, 0.95)),
              (ell(152, 128, 38, 48), sk, dict(kind="gladki", contrast=0.6)),
              (poly([(184, 112), (200, 138), (186, 146)]), sk, dict(kind="gladki", contrast=0.6))]
    fr = s["fryzura"]
    if fr == "mizura":
        parts += [(poly([(112, 120), (114, 92), (130, 74), (158, 68), (182, 76), (194, 98), (192, 112), (176, 96), (150, 90),
                         (126, 100)]), hair),
                  (ell(110, 152, 13, 30), hair, dict(edge=2)),
                  (rect(98, 140, 122, 148), (236, 230, 214))]
    elif fr in ("dlugie", "kok"):
        parts += [(poly([(112, 124), (112, 90), (132, 72), (160, 66), (186, 76), (196, 104), (194, 122), (182, 100), (150, 94),
                         (124, 108)]), hair),
                  (poly([(108, 108), (124, 108), (126, 214), (106, 210)]), hair)]
        if fr == "kok":
            parts += [(ell(150, 62, 30, 22), hair, dict(edge=2)), (rect(118, 58, 184, 64), GOLD)]
    elif fr == "dzikie":
        parts.append((poly([(110, 124), (106, 88), (126, 66), (160, 58), (190, 70), (200, 104), (184, 94), (160, 86), (128, 98)]), hair))
    elif fr == "luzne":
        parts.append((poly([(110, 128), (112, 90), (132, 72), (160, 66), (186, 76), (196, 104), (190, 116), (176, 98), (150, 92),
                            (124, 104)]), hair))
    elif fr == "helm":
        z = s["zbroja"] or (90, 92, 100)
        parts += [(poly([(104, 172), (120, 172), (118, 112), (104, 116)]), _shade(z, 0.8)),
                  (poly([(108, 114), (112, 82), (150, 60), (190, 80), (198, 114)]), z, dict(contrast=1.2)),
                  (poly([(98, 112), (206, 112), (218, 122), (94, 122)]), _shade(z, 0.75)),
                  (poly([(146, 64), (156, 64), (160, 40), (142, 40)]), GOLD)]
    if s["broda"]:
        parts.append((poly([(140, 160), (176, 150), (194, 148), (190, 176), (172, 208), (150, 200), (136, 182)]), hair))
    if s["wasy"] or s["broda"]:
        parts.append((poly([(158, 154), (192, 146), (190, 156), (166, 160)]), hair))
    if s["opaska"]:
        parts += [(poly([(112, 98), (194, 92), (196, 104), (112, 110)]), s["opaska"]),
                  (poly([(170, 96), (180, 70), (190, 95)]), s["opaska"])]
    im = stack(w, h, parts, seed=sum(map(ord, str(sorted(s.items())))) % 997)
    d = ImageDraw.Draw(im)
    ink = INK + (235,)
    if s["oczy"] == "otwarte":
        for x0, x1, yy in ((130, 144, 124), (164, 178, 122)):
            d.line([(x0 - 2, yy - 9), (x1 + 2, yy - 11 if x0 > 150 else yy - 10)], fill=_shade(hair, 0.9) + (240,), width=4)  # brwi
            d.line([(x0, yy), (x1, yy)], fill=ink, width=3)
            d.ellipse([(x0 + x1) / 2 - 3.5 + 2, yy - 1, (x0 + x1) / 2 + 3.5 + 2, yy + 7], fill=ink)
    else:
        for x0, x1, yy in ((130, 144, 126), (164, 178, 124)):
            d.arc([x0, yy - 6, x1, yy + 6], 20, 160, fill=ink, width=3)
    d.line([(184, 128), (190, 140)], fill=_shade(sk, 0.75) + (200,), width=2)
    blush = Image.new("L", (w, h), 0)
    ImageDraw.Draw(blush).ellipse([160, 136, 184, 152], fill=70 if s["kobieta"] else 40)
    blush = blush.filter(ImageFilter.GaussianBlur(4))
    tint = Image.new("RGBA", (w, h), (220, 110, 100, 0))
    tint.putalpha(blush)
    im.alpha_composite(tint)
    if s["kobieta"]:
        d.line([(164, 162), (176, 161)], fill=(170, 50, 50, 230), width=4)
        for x in range(92, 228, 22):  # fałdy spódnicy
            d.line([(150 + (x - 150) * 0.62, Y(380)), (x, Y(666))], fill=_shade(sp, 0.78) + (150,), width=2)
    elif not (s["broda"] or s["wasy"]):
        d.line([(162, 162), (176, 160)], fill=ink, width=3)
    if s["zbroja"]:
        for yy in (236, 262, 288, 314):
            d.line([(92, yy), (210, yy)], fill=_shade(s["zbroja"], 0.6) + (230,), width=3)
        for xx in range(88, 226, 18):
            d.line([(150 + (xx - 150) * 0.85, 356), (xx, 450)], fill=_shade(s["zbroja"], 0.6) + (220,), width=2)
    if s["szer"] != 1.0:
        im = im.resize((round(w * s["szer"]), h), Image.LANCZOS)
    return im


def _ramie_img(s):
    w, h = RAMIE_W, RAMIE_H
    tun = s["rekaw"] or s["tunika"]
    if s["kobieta"]:
        sleeve = poly([(32, 22), (78, 22), (88, 214), (24, 214)])
    else:
        sleeve = poly([(34, 22), (76, 22), (72, 206), (38, 206)])
    parts = [(ell(55, 26, 25, 23), tun), (sleeve, tun, dict(edge=2, shade=0.2))]
    if s["zbroja"]:
        parts.append((poly([(30, 14), (80, 14), (84, 70), (26, 70)]), s["zbroja"], dict(contrast=1.2)))
    cuff = s["pas"] if not s["zbroja"] else s["zbroja"]
    parts += [(poly([(38, 196), (72, 196), (74, 210), (36, 210)]) if not s["kobieta"] else poly([(26, 204), (86, 204), (88, 216), (24, 216)]),
               cuff),
              (ell(56, 230, 15, 19), s["skora"], dict(kind="gladki", contrast=0.6))]
    im = stack(w, h, parts, seed=31 + len(str(tun)))
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
        self.cw, self.ch = body.size  # rozmiar arkusza korpusu
        self.stopa = STOPA + s["nogi"]
        self.wys = self.stopa - CZUBEK  # wysokość postaci w pikselach arkusza (od stóp do czubka głowy)
        k = s["szer"]
        self.bark = {n: (FIG_W * k / 2 + (x - FIG_W / 2) * k, y) for n, (x, y) in BARK.items()}
        self.aw, self.ah = arm.size
        self.zawias = (RAMIE_ZAWIAS[0] * k + (self.aw - RAMIE_W * k) / 2, RAMIE_ZAWIAS[1])
        self.dlon = DLON[1] - RAMIE_ZAWIAS[1]


@lru_cache(None)
def figura(key):
    return Figura(key)


# ---------- front teatru: brama torii ----------

@lru_cache(None)
def theatre():
    """Rama teatru (plan 1,0) w kształcie bramy torii: cynobrowe słupy, czarna belka kasagi z wygiętymi końcami, tabliczka z
    tytułem. Otwór sceny to dokładnie kadr wzorcowy 0..1280 × 0..720; układ arkusza: początek w (-760, -470)."""
    ox, oy, w, h = 760, 470, 2800, 1700
    R = lambda x0, y0, x1, y1: poly([(x0 + ox, y0 + oy), (x1 + ox, y0 + oy), (x1 + ox, y1 + oy), (x0 + ox, y1 + oy)])
    dark, wood, kuro = (18, 14, 13), (64, 36, 26), (30, 24, 24)
    im = piece(w, h, poly([(0, 0), (w, 0), (w, h), (0, h)]), dark, "gladki", rough=0, contrast=0.8)
    # skrzynia sceny: ciemne drewno wokół otworu
    im = glue(im, piece(w, h, R(-40, -40, 1320, 790), wood, "gnieciony", seed=2, contrast=0.9), shadow=0.8, off=(10, 14), soft=14)
    # podest pod sceną
    for i, (shape, col) in enumerate(((R(-160, 760, 1440, 800), kuro), (R(-160, 754, 1440, 762), GOLD), (R(-60, 800, 1340, 860), wood))):
        im = glue(im, piece(w, h, shape, col, "gnieciony", seed=10 + i, contrast=0.9), shadow=0.5)
    # słupy (lekko rozchylone ku dołowi) i czarne podstawy
    for i, x in enumerate((-86, 1366)):
        sh = poly([(x - 46 + ox, -170 + oy), (x + 46 + ox, -170 + oy), (x + 54 + ox, 900 + oy), (x - 54 + ox, 900 + oy)])
        im = glue(im, piece(w, h, sh, SHU, "gnieciony", seed=20 + i, contrast=0.9, shade=0.15), shadow=0.7, off=(8, 10), soft=10)
        im = glue(im, piece(w, h, R(x - 62, 820, x + 62, 900), kuro, "gnieciony", seed=24 + i), shadow=0.5)
    # nuki — dolna belka przez słupy
    im = glue(im, piece(w, h, R(-230, -74, 1510, -36), SHU, "gnieciony", seed=30, contrast=0.9), shadow=0.6, off=(6, 8), soft=8)
    # shimaki i kasagi — górna belka z końcami wygiętymi do góry
    xs = list(range(-330, 1611, 20))
    curve = lambda x, base, lift: base - lift * ((x - 640) / 970.0) ** 4
    top = [(x + ox, curve(x, -262, 70) + oy) for x in xs]
    bot = [(x + ox, curve(x, -214, 52) + oy) for x in reversed(xs)]
    im = glue(im, piece(w, h, poly([(x + ox, curve(x, -214, 40) + oy) for x in range(-280, 1561, 20)]
                                    + [(x + ox, curve(x, -182, 30) + oy) for x in range(1560, -281, -20)]), SHU, "gnieciony", seed=31),
              shadow=0.6, off=(6, 8), soft=8)
    im = glue(im, piece(w, h, poly(top + bot), kuro, "gnieciony", seed=32, contrast=1.0), shadow=0.7, off=(8, 10), soft=10)
    # łącznik i tabliczka z tytułem
    im = glue(im, piece(w, h, R(600, -186, 680, -74), kuro, "gnieciony", seed=40), shadow=0.6)
    im = glue(im, piece(w, h, R(330, -176, 950, -48), kuro, "gladki", seed=41, contrast=1.4), shadow=0.8, off=(6, 8), soft=8)
    for shape in (R(330, -176, 950, -168), R(330, -56, 950, -48), R(330, -176, 338, -48), R(942, -176, 950, -48)):
        im = glue(im, piece(w, h, shape, GOLD, "gnieciony", seed=43, contrast=0.9), shadow=0.4)
    title = glyphs(tr("SYN SŁOŃCA"), 58, FONT_PL, PL_IDX, (640 + ox, -124 + oy), "mm")
    im = glue(im, piece(w, h, title, (230, 190, 104), "gladki", rough=0.6, contrast=1.2), shadow=0.7, off=(2, 3), soft=1.5)
    sub = glyphs(tr("POWSTANIE JAPONII"), 22, FONT_PL, PL_IDX, (640 + ox, -78 + oy), "mm", spacing=4)
    im = glue(im, piece(w, h, sub, (210, 170, 96), "gladki", rough=0.5, contrast=1.2), shadow=0.6, off=(1, 2), soft=1)
    # czerwone słońca-pieczęcie po bokach tabliczki
    for i, x in enumerate((262, 1018)):
        im = glue(im, piece(w, h, ell(x + ox, -112 + oy, 34, 34), (196, 46, 36), "gnieciony", seed=50 + i), shadow=0.6)
    a = np.asarray(im.getchannel("A")).copy()
    a[oy:oy + H, ox:ox + W] = 0  # otwór sceny
    im.putalpha(Image.fromarray(a))
    return Sprite(im, "teatr-torii", rim=0, clean=False, pad=0)


def theatre_put(st, light=1.0):
    spr = theatre()
    st.put(spr, -760, -470, P.rama, w=2800, anchor=(0.0, 0.0), shadow=(0, 10, 18, 0.55), blur=0, tint=(light, light, light))  # w szkicu wycinek ma połowę pikseli


# ---------- krajobraz: pasma wzgórz w barwach Japonii, wyspy, cedry, wiśnia ----------

PASMA = {  # (wysokość arkusza, [(linia grzbietu, falowanie, barwa), ...] od najdalszego)
    "dal": (300, [(120, 40, (150, 166, 140)), (190, 28, (176, 180, 136))]),
    "srodek": (320, [(110, 40, (92, 126, 92)), (176, 34, (124, 148, 100)), (236, 26, (164, 162, 106))]),
    "blisko": (260, [(96, 22, (120, 150, 92)), (170, 18, (98, 128, 80))]),
    "przod": (300, [(96, 36, (56, 90, 66)), (150, 30, (80, 112, 76)), (214, 24, (44, 72, 56))]),
    "niebieskie": (300, [(100, 46, (98, 120, 150)), (180, 34, (120, 140, 160))]),
    "piasek": (220, [(110, 16, (214, 196, 150)), (160, 12, (196, 176, 130))]),
    "chmury": (320, [(80, 30, (244, 236, 222)), (150, 26, (236, 226, 208)), (220, 22, (226, 214, 194))]),
    "ciemne": (300, [(100, 40, (44, 40, 46)), (170, 30, (34, 30, 36))]),
}


@lru_cache(None)
def pasmo(which):
    h, sheets = PASMA[which]
    w, seed = 2200, sum(map(ord, which)) + 7
    im = None
    for i, (base, amp, color) in enumerate(sheets):
        sh = _sheet(w, h, seed + 17 * i, base, amp, color, edge=6 if which == "chmury" else 5)
        im = sh if im is None else over(im, sh)
    return Sprite(im, f"pasmo-{which}", rim=2, clean=False, pad=0)


def pasmo_top(which, x, cx, y_bottom, w=2000):
    spr = pasmo(which)
    hh = w * spr.h / spr.w
    return y_bottom - hh + spr.top((x - (cx - w / 2)) / w) * hh


@lru_cache(None)
def wyspa(v=0):
    """Wyspa z fal: skalisty kopiec z zielonym wierzchem, jasny brzeg i jedna do trzech sosen."""
    r = random.Random(40 + v)
    w, h = 620, 360
    base_y = 330
    peak = r.uniform(150, 210)
    pts = [(x, base_y - peak * math.exp(-((x - w / 2) / (150 + 40 * r.random())) ** 2) - 18 * math.sin(x / 40.0 + v) * 0.3)
           for x in range(20, w - 19, 12)]
    body = poly(pts + [(w - 20, base_y + 20), (20, base_y + 20)])
    top = poly([(x, y - 2) for x, y in pts] + [(x, y + 34 + 10 * math.sin(x / 23.0)) for x, y in reversed(pts)])
    im = stack(w, h, [(body, (120, 110, 92), dict(edge=3, shade=0.25)), (top, (82, 124, 76), dict(edge=2)),
                      (poly([(20, base_y - 4), (w - 20, base_y - 4), (w - 20, base_y + 20), (20, base_y + 20)]), (220, 204, 160))],
               seed=60 + v)
    for j in range(1 + v % 3):
        pine = _drzewo_img("zielone" if (v + j) % 2 else "wisnia", 2 + (v + j) % 2)[0]
        ph = r.uniform(80, 120)
        tw = round(pine.size[0] * ph / pine.size[1])
        p = pine.resize((tw, round(ph)), Image.LANCZOS)
        xx = int(w / 2 + r.uniform(-90, 90))
        yy = min(base_y - 30, int(min(y for x, y in pts if abs(x - xx) < 14) + 10)) if any(abs(x - xx) < 14 for x, y in pts) else 160
        im.alpha_composite(p, (xx - tw // 2, int(yy - ph + 8)))
    return Sprite(im, f"wyspa-{v}", rim=2, clean=False)


@lru_cache(None)
def cedr(v=0):
    """Cedr z Kumano: wąski, wysoki, z warstw ciemnozielonego papieru."""
    r = random.Random(70 + v)
    w, h = 240, 760
    parts = [(rect(110, 300, 130, 760), (90, 62, 46))]
    tiers = 9
    for k in range(tiers):
        f = k / (tiers - 1)
        y = 40 + f * 600
        half = 26 + 86 * f
        col = ((40, 70, 52), (52, 84, 60), (34, 60, 46))[k % 3]
        parts.append((poly([(120, y - 40), (120 + half, y + 70 + r.uniform(-8, 8)), (120 - half, y + 70 + r.uniform(-8, 8))]), col,
                      dict(edge=0)))
    return Sprite(stack(w, h, parts, seed=80 + v), f"cedr-{v}", rim=2, clean=False)


@lru_cache(None)
def platek(i):
    w = h = 40
    c = ((246, 196, 210), (240, 176, 196), (250, 220, 228))[i % 3]
    return Sprite(piece(w, h, ell(20, 20, 16, 10), c, "gladki", rough=0.6), f"platek-{i}", rim=1, clean=False)


@lru_cache(None)
def wzgorek(v=0, color=(104, 140, 90)):
    """Okrągłe wzgórze (trzy wzgórza Yamato, góra Unebi)."""
    w, h = 600, 300
    r = random.Random(90 + v)
    amp = r.uniform(200, 250)
    pts = [(x, 290 - amp * math.exp(-((x - 300) / 150.0) ** 2) ** 0.8) for x in range(0, w + 1, 10)]
    im = stack(w, h, [(poly(pts + [(w, h), (0, h)]), color, dict(edge=4, shade=0.25)),
                      (poly([(x, y + 40) for x, y in pts] + [(w, h), (0, h)]), _shade(color, 0.82), dict(edge=2))], seed=91 + v)
    return Sprite(im, f"wzgorek-{v}", rim=2, clean=False)


# ---------- niebo i bogowie ----------

@lru_cache(None)
def most_niebios():
    """Pływający most niebios: tęczowy łuk z papierowych pasów i cynobrowa poręcz."""
    w, h = 1200, 360
    cols = [(196, 64, 50), (226, 132, 60), (232, 196, 90), (110, 160, 96), (80, 130, 170), (100, 90, 160)]
    parts = []
    for i, c in enumerate(cols):
        R0, R1 = 560 - i * 16, 560 - (i + 1) * 16
        pts = [(600 + R0 * math.cos(a), 340 - 0.52 * R0 * math.sin(a)) for a in np.linspace(math.pi * 0.98, math.pi * 0.02, 60)]
        pts += [(600 + R1 * math.cos(a), 340 - 0.52 * R1 * math.sin(a)) for a in np.linspace(math.pi * 0.02, math.pi * 0.98, 60)]
        parts.append((poly(pts), c, dict(edge=0, contrast=0.8)))
    for k in range(13):  # słupki poręczy
        a = math.pi * (0.92 - 0.84 * k / 12)
        x, y = 600 + 562 * math.cos(a), 340 - 0.52 * 562 * math.sin(a)
        parts.append((rect(x - 4, y - 46, x + 4, y), SHU))
    rail = [(600 + 562 * math.cos(a), 340 - 0.52 * 562 * math.sin(a) - 46) for a in np.linspace(math.pi * 0.92, math.pi * 0.08, 50)]
    parts.append((lambda d, s: d.line([(x * s, y * s) for x, y in rail], fill=255, width=int(8 * s)), SHU))
    return Sprite(stack(w, h, parts, seed=101), "most-niebios", rim=2, clean=False, crop=False)


def most_y(x, cx, y0, w):
    """Wysokość pokładu mostu (górna krawędź tęczy, kadr wzorcowy) w punkcie x, gdy most stoi środkiem w cx, dołem
    arkusza w y0 i ma szerokość w (arkusz bez przycinania, crop=False)."""
    k = w / 1200
    c = clamp(((x - cx) / k) / 560, -0.999, 0.999)
    v = 340 - 0.52 * 560 * math.sqrt(1 - c * c)
    return y0 - (360 - v) * k


@lru_cache(None)
def wlocznia_bogow():
    """Włócznia wysadzana klejnotami (Ame-no-nuboko): długie drzewce, grot, klejnoty i frędzle."""
    w, h = 90, 640
    parts = [(rect(41, 80, 49, 636), (110, 74, 48)), (poly([(45, 2), (60, 70), (45, 96), (30, 70)]), (210, 214, 216), dict(kind="gladki")),
             (rect(32, 92, 58, 104), GOLD)]
    for k, c in enumerate(((60, 150, 110), (196, 60, 60), (70, 110, 180), (60, 150, 110))):
        parts.append((ell(45, 130 + k * 26, 10, 11), c, dict(kind="gladki", rough=0.5)))
    parts += [(poly([(40, 104), (24, 190), (32, 192), (44, 110)]), (196, 52, 42)), (poly([(50, 104), (64, 186), (56, 190), (46, 110)]),
                                                                                       (196, 52, 42))]
    return Sprite(stack(w, h, parts, seed=111), "wlocznia-bogow", rim=2, clean=False)


@lru_cache(None)
def kropla():
    w, h = 60, 90
    return Sprite(piece(w, h, poly([(30, 4)] + [(30 + 22 * math.sin(a), 62 - 22 * math.cos(a)) for a in np.linspace(0.6, 2 * math.pi - 0.6, 30)]),
                        (238, 244, 246), "gladki", rough=0.6), "kropla", rim=2, clean=False)


@lru_cache(None)
def meduza():
    w, h = 300, 360
    parts = [(lambda d, s: d.chord([30 * s, 20 * s, 270 * s, 220 * s], 180, 360, fill=255), (214, 196, 230), dict(kind="gladki"))]
    for k in range(7):
        x = 60 + k * 30
        pts = [(x + 10 * math.sin(y / 30.0 + k), y) for y in range(118, 340, 12)]
        parts.append((lambda d, s, pts=pts: d.line([(a * s, b * s) for a, b in pts], fill=255, width=int(5 * s)), (200, 176, 220)))
    im = stack(w, h, parts, seed=121)
    a = np.asarray(im.getchannel("A"), np.float32) * 0.62
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return Sprite(im, "meduza", rim=1, clean=False)


@lru_cache(None)
def glaz(v=0):
    r = random.Random(130 + v)
    w, h = 460, 380
    pts = [(230 + (190 + r.uniform(-24, 24)) * math.cos(a), 210 + (160 + r.uniform(-20, 20)) * math.sin(a))
           for a in np.linspace(0, 2 * math.pi, 22, endpoint=False)]
    parts = [(poly(pts), (110, 104, 98), dict(edge=3, contrast=1.3, shade=0.3)),
             (poly([(130, 90), (210, 60), (260, 110), (200, 150)]), (140, 134, 126), dict(contrast=1.2))]
    im = stack(w, h, parts, seed=131 + v)
    d = ImageDraw.Draw(im)
    d.line([(180, 120), (230, 210), (210, 300)], fill=(60, 54, 50, 200), width=4)
    return Sprite(im, f"glaz-{v}", rim=3, clean=False)


@lru_cache(None)
def skala():
    """Skała z jaskinią (Ama-no-Iwato): ogromny głaz z ciemnym otworem."""
    w, h = 820, 700
    r = random.Random(140)
    pts = [(40, 700), (60, 420), (120, 260), (230, 140), (380, 80), (520, 110), (660, 220), (760, 380), (790, 700)]
    pts = [(x + r.uniform(-10, 10), y + r.uniform(-10, 10)) for x, y in pts]
    parts = [(poly(pts), (104, 98, 92), dict(edge=3, contrast=1.3, shade=0.35)),
             (poly([(200, 260), (330, 170), (420, 200), (300, 300)]), (130, 124, 116), dict(contrast=1.2)),
             (poly([(560, 260), (680, 330), (640, 420), (540, 360)]), (88, 84, 80), dict(contrast=1.2)),
             (lambda d, s: d.chord([300 * s, 360 * s, 560 * s, 820 * s], 180, 360, fill=255), (20, 16, 16))]
    return Sprite(stack(w, h, parts, seed=141), "skala", rim=3, clean=False)


@lru_cache(None)
def sakaki():
    """Drzewko sakaki: pień, kępy ciemnych liści i białe zygzaki papieru shide."""
    w, h = 380, 560
    r = random.Random(150)
    parts = [(poly([(178, 560), (202, 560), (196, 300), (184, 300)]), (96, 66, 46)),
             (_band((190, 340), (110, 230), 12), (96, 66, 46)), (_band((190, 330), (280, 220), 12), (96, 66, 46))]
    for k in range(16):
        x, y = r.uniform(70, 310), r.uniform(70, 330)
        parts.append((ell(x, y, r.uniform(36, 60), r.uniform(22, 34)), ((44, 84, 56), (58, 100, 64), (36, 70, 48))[k % 3]))
    for x, y in ((110, 300), (280, 290), (190, 360)):
        z = [(x, y), (x + 14, y + 16), (x + 2, y + 26), (x + 16, y + 44), (x + 4, y + 54), (x + 18, y + 74), (x + 6, y + 74),
             (x - 8, y + 56), (x + 4, y + 46), (x - 10, y + 30), (x + 2, y + 20), (x - 10, y + 6)]
        parts.append((poly(z), (246, 244, 236), dict(kind="gladki", rough=0.4)))
    return Sprite(stack(w, h, parts, seed=151), "sakaki", rim=2, clean=False)


@lru_cache(None)
def lustro():
    """Lustro z brązu (Yata no kagami): wypolerowana tarcza z bogatym obrzeżem."""
    w = h = 300
    parts = [(ell(150, 150, 140, 140), (150, 118, 62), dict(edge=0, contrast=1.3)),
             (ell(150, 150, 116, 116), (232, 226, 206), dict(kind="gladki", contrast=0.5)),
             (ell(118, 116, 40, 28), (252, 250, 240), dict(kind="gladki", contrast=0.3))]
    for k in range(16):
        a = 2 * math.pi * k / 16
        parts.append((ell(150 + 128 * math.cos(a), 150 + 128 * math.sin(a), 6, 6), GOLD))
    return Sprite(stack(w, h, parts, seed=161), "lustro", rim=3, clean=False)


@lru_cache(None)
def lusterko():
    """Lustro z brązu od strony tylnej (dla Himiko): zielonkawa patyna i wzór."""
    w = h = 160
    parts = [(ell(80, 80, 74, 74), (100, 120, 90), dict(contrast=1.3)), (ell(80, 80, 56, 56), (126, 146, 104)),
             (ell(80, 80, 14, 14), (90, 108, 82))]
    im = stack(w, h, parts, seed=165)
    d = ImageDraw.Draw(im)
    for k in range(8):
        a = 2 * math.pi * k / 8
        d.line([(80 + 20 * math.cos(a), 80 + 20 * math.sin(a)), (80 + 50 * math.cos(a), 80 + 50 * math.sin(a))], fill=(70, 86, 64, 220), width=3)
    return Sprite(im, "lusterko", rim=2, clean=False)


@lru_cache(None)
def magatama_sznur():
    w, h = 320, 220
    parts = [(lambda d, s: d.arc([20 * s, -150 * s, 300 * s, 190 * s], 20, 160, fill=255, width=int(4 * s)), (230, 220, 200))]
    for k in range(9):
        a = math.radians(24 + 132 * k / 8)
        x, y = 160 + 140 * math.cos(a), 20 + 170 * math.sin(a)
        c = ((60, 150, 110), (80, 170, 130), (196, 60, 60))[1 if k % 2 else 0] if k != 4 else (196, 60, 60)
        parts.append((_magatama(x, y, 11 if k != 4 else 15, math.degrees(a) - 90), c, dict(kind="gladki", rough=0.4)))
    return Sprite(stack(w, h, parts, seed=171), "magatama", rim=2, clean=False)


@lru_cache(None)
def miecz_jp(blask=False):
    """Prosty obosieczny miecz (tsurugi) ostrzem do góry; rękojeść na dole."""
    w, h = 90, 560
    blade = (226, 230, 232) if blask else (196, 200, 204)
    parts = [(poly([(45, 4), (60, 40), (58, 420), (32, 420), (30, 40)]), blade, dict(kind="gladki", contrast=0.4)),
             (rect(44, 30, 47, 416), (150, 156, 162)),
             (poly([(14, 418), (76, 418), (70, 436), (20, 436)]), GOLD),
             (rect(36, 436, 54, 540), (60, 40, 30)), (ell(45, 546, 13, 13), GOLD)]
    return Sprite(stack(w, h, parts, seed=181 + blask), f"miecz-{blask}", rim=2, clean=False)


@lru_cache(None)
def luk():
    """Długi japoński łuk (yumi): uchwyt poniżej środka."""
    w, h = 140, 900
    outer = [(60 + 46 * math.sin(math.pi * f) ** 0.9, 10 + 880 * f) for f in np.linspace(0, 1, 50)]
    inner = [(x - 9, y) for x, y in reversed(outer)]
    parts = [(poly(outer + inner), (70, 40, 30), dict(contrast=1.2)),
             (lambda d, s: d.line([(60 * s, 12 * s), (60 * s, 888 * s)], fill=255, width=max(1, int(2 * s))), (236, 228, 210)),
             (rect(92, 560, 112, 620), (236, 228, 210))]
    return Sprite(stack(w, h, parts, seed=191), "luk", rim=1, clean=False, crop=False)


LUK_UCHWYT = (102 / 140, 590 / 900)  # uchwyt jako ułamek arkusza
LUK_CZUBEK = (60 / 140, 12 / 900)


@lru_cache(None)
def strzala_nieba():
    w, h = 300, 40
    parts = [(rect(20, 18, 262, 23), (120, 84, 54)), (poly([(258, 8), (296, 20), (258, 32)]), (180, 184, 190)),
             (poly([(4, 6), (60, 18), (60, 22), (4, 34), (20, 20)]), (250, 250, 246), dict(kind="gladki"))]
    return Sprite(stack(w, h, parts, seed=195), "strzala-nieba", rim=1, clean=False)


@lru_cache(None)
def kogut(v=0):
    w, h = 220, 230
    body = (236, 226, 210) if v == 0 else (176, 96, 52)
    parts = [(poly([(30, 70), (10, 20), (60, 50), (40, 10), (90, 70), (70, 30), (110, 90)]), (40, 60, 70) if v == 0 else (60, 40, 30)),
             (ell(110, 120, 70, 50), body, dict(edge=2)), (ell(170, 70, 24, 26), body),
             (poly([(160, 44), (168, 24), (176, 40), (184, 22), (190, 46)]), (200, 40, 34)),
             (poly([(190, 70), (214, 76), (190, 82)]), (220, 170, 60)), (ell(176, 96, 8, 12), (200, 40, 34)),
             (rect(96, 166, 102, 214), (220, 170, 60)), (rect(122, 166, 128, 214), (220, 170, 60))]
    im = stack(w, h, parts, seed=200 + v)
    ImageDraw.Draw(im).ellipse([174, 62, 182, 70], fill=INK + (255,))
    return Sprite(im, f"kogut-{v}", rim=2, clean=False)


@lru_cache(None)
def kadz(v=0):
    """Drewniana kadź z obręczami; otwarta góra z ciemnym sake."""
    w, h = 220, 220
    wood = ((150, 110, 70), (138, 100, 64), (160, 120, 78))[v % 3]
    parts = [(poly([(20, 40), (200, 40), (186, 214), (34, 214)]), wood, dict(edge=2, shade=0.2)),
             (ell(110, 40, 90, 18), _shade(wood, 1.1)), (ell(110, 42, 78, 12), (60, 40, 46)),
             (poly([(22, 80), (198, 80), (196, 92), (24, 92)]), (70, 60, 56)),
             (poly([(30, 170), (190, 170), (188, 182), (32, 182)]), (70, 60, 56))]
    im = stack(w, h, parts, seed=210 + v)
    d = ImageDraw.Draw(im)
    for x in range(44, 190, 22):
        d.line([(x, 54), (x + (x - 110) * 0.08, 210)], fill=_shade(wood, 0.7) + (160,), width=2)
    return Sprite(im, f"kadz-{v}", rim=2, clean=False)


@lru_cache(None)
def galazka():
    w, h = 160, 120
    parts = [(_band((10, 100), (150, 20), 6), (90, 64, 44))]
    for k in range(6):
        f = (k + 1) / 7
        parts.append((ell(10 + 140 * f, 100 - 80 * f + (14 if k % 2 else -14), 18, 9), (60, 110, 70)))
    return Sprite(stack(w, h, parts, seed=220), "galazka", rim=1, clean=False)


@lru_cache(None)
def shimenawa():
    w, h = 1000, 180
    parts = []
    for k in range(0, 1000, 40):
        parts.append((ell(k + 20, 40 + 8 * math.sin(k / 160.0), 26, 22), (214, 186, 120) if (k // 40) % 2 else (200, 170, 104)))
    for x in range(120, 900, 190):
        z = [(x, 56), (x + 18, 76), (x + 2, 90), (x + 20, 116), (x + 4, 128), (x + 22, 160), (x + 8, 160), (x - 8, 132), (x + 6, 118),
             (x - 10, 94), (x + 4, 80), (x - 10, 60)]
        parts.append((poly(z), (246, 244, 236), dict(kind="gladki", rough=0.4)))
    return Sprite(stack(w, h, parts, seed=230), "shimenawa", rim=2, clean=False)


@lru_cache(None)
def wir():
    """Wir wiatru: białe spirale z bibuły (Susanoo)."""
    w, h = 400, 400
    parts = []
    for k in range(3):
        pts = [(200 + (30 + 150 * f) * math.cos(f * 9 + k * 2.1), 200 + (30 + 150 * f) * math.sin(f * 9 + k * 2.1) * 0.7)
               for f in np.linspace(0, 1, 80)]
        parts.append((lambda d, s, pts=pts: d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(10 * s)), (232, 236, 240)))
    im = stack(w, h, parts, seed=240)
    a = np.asarray(im.getchannel("A"), np.float32) * 0.75
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return Sprite(im, "wir", rim=1, clean=False)


@lru_cache(None)
def poletko(v=0):
    """Poletko ryżu z papierowych pasków: 0 zielone, 1 złote, 2 ścierń."""
    w, h = 260, 70
    col = ((92, 150, 80), (214, 178, 80), (176, 150, 100))[v]
    parts = [(poly([(10, 10), (250, 10), (240, 66), (20, 66)]), (120, 100, 70) if v == 2 else _shade(col, 0.8), dict(edge=2))]
    for k in range(6):
        y = 16 + k * 9
        parts.append((rect(22 + k * 2, y, 238 - k * 2, y + 5 if v != 2 else y + 2), col, dict(rough=0.7)))
    return Sprite(stack(w, h, parts, seed=250 + v), f"poletko-{v}", rim=1, clean=False)


@lru_cache(None)
def tkalnia():
    """Tkalnia bogini: mały dom na palach z dachem z trzciny (dach osobno: `dach`)."""
    w, h = 420, 300
    wood = (150, 108, 72)
    parts = [(rect(60, 150, 360, 250), (196, 160, 112), dict(edge=2)), (rect(40, 240, 380, 254), wood)]
    for x in (64, 150, 270, 346):
        parts.append((rect(x, 150, x + 12, 296), wood))
    parts.append((rect(170, 170, 250, 240), (60, 40, 30)))
    return Sprite(stack(w, h, parts, seed=260), "tkalnia", rim=2, clean=False)


@lru_cache(None)
def dach(w=420, kolor=(176, 140, 80)):
    h = 180
    parts = [(poly([(0, 170), (w / 2, 20), (w, 170)]), kolor, dict(edge=3, shade=0.25)),
             (rect(w / 2 - 6, 10, w / 2 + 6, 40), (90, 64, 44)),
             (poly([(w / 2 - 60, 30), (w / 2 - 20, 30), (w / 2 + 70, -10 + 30), (w / 2 + 50, 0 + 30)]), (90, 64, 44))]
    im = stack(int(w), h, parts, seed=270 + int(w))
    d = ImageDraw.Draw(im)
    for k in range(1, 9):
        y = 20 + 150 * k / 9
        d.line([(w / 2 - (w / 2) * k / 9, y), (w / 2 + (w / 2) * k / 9, y)], fill=_shade(kolor, 0.7) + (140,), width=2)
    return Sprite(im, f"dach-{int(w)}-{kolor}", rim=2, clean=False)


@lru_cache(None)
def pochodnia():
    w, h = 40, 260
    return Sprite(stack(w, h, [(rect(14, 40, 26, 258), (90, 62, 44)), (poly([(8, 30), (32, 30), (28, 60), (12, 60)]), (176, 140, 80))],
                        seed=280), "pochodnia", rim=1, clean=False)


@lru_cache(None)
def krazek(kind):
    """Krążek: słońce (złote), księżyc (srebrny), chmura burzy (ciemna)."""
    w = h = 200
    if kind == "slonce":
        parts = [(ell(100, 100, 90, 90), (226, 70, 46), dict(edge=3)), (ell(84, 84, 30, 22), (246, 120, 80), dict(kind="gladki"))]
    elif kind == "ksiezyc":
        parts = [(ell(100, 100, 86, 86), (216, 220, 226), dict(edge=3)), (ell(130, 90, 70, 74), (40, 40, 46))]
    else:
        parts = [(ell(70, 110, 60, 46), (60, 62, 76)), (ell(120, 90, 66, 56), (70, 72, 86)), (ell(150, 120, 46, 36), (52, 54, 66))]
    im = stack(w, h, parts, seed=290 + len(kind))
    if kind == "ksiezyc":  # sierp: ciemne koło tylko wycina
        a = np.asarray(im, np.float32)
        dark = (a[..., 0] < 60) & (a[..., 3] > 0)
        a[dark, 3] = 0
        im = Image.fromarray(a.astype(np.uint8), "RGBA")
    return Sprite(im, f"krazek-{kind}", rim=2, clean=False)


# ---------- Izumo: wąż o ośmiu głowach ----------

@lru_cache(None)
def waz_glowa(v=0):
    """Głowa węża z profilu (pyskiem w prawo): otwarta paszcza, czerwone oko, łuski."""
    w, h = 300, 200
    body = ((70, 92, 70), (84, 100, 66), (64, 84, 72))[v % 3]
    parts = [(poly([(10, 70), (90, 40), (200, 50), (286, 84), (240, 100), (200, 104), (284, 120), (250, 140), (150, 150), (60, 140),
                    (10, 120)]), body, dict(edge=2, contrast=1.2)),
             (poly([(200, 100), (280, 86), (280, 92), (204, 108)]), (190, 50, 40)),
             (poly([(204, 108), (282, 120), (276, 126), (206, 116)]), (190, 50, 40)),
             (poly([(70, 40), (110, 10), (120, 44)]), _shade(body, 0.8)), (poly([(120, 44), (150, 16), (158, 48)]), _shade(body, 0.8)),
             (ell(176, 72, 14, 11), (230, 200, 60)), (ell(178, 72, 5, 9), (180, 30, 30))]
    im = stack(w, h, parts, seed=300 + v)
    d = ImageDraw.Draw(im)
    for x in (230, 248, 262):
        d.polygon([(x, 94), (x + 5, 104), (x + 9, 94)], fill=(244, 240, 226, 255))
    for k in range(8):
        d.arc([30 + k * 18, 80, 50 + k * 18, 104], 200, 340, fill=_shade(body, 0.6) + (200,), width=2)
    return Sprite(im, f"waz-glowa-{v}", rim=2, clean=False)


@lru_cache(None)
def waz_luska(v=0):
    w, h = 120, 120
    body = ((70, 92, 70), (84, 100, 66), (64, 84, 72))[v % 3]
    parts = [(ell(60, 60, 54, 54), body, dict(edge=2, contrast=1.2)), (ell(60, 76, 34, 26), (176, 120, 70))]
    im = stack(w, h, parts, seed=310 + v)
    d = ImageDraw.Draw(im)
    for x in (34, 60, 86):
        d.arc([x - 14, 30, x + 14, 58], 200, 340, fill=_shade(body, 0.55) + (200,), width=3)
    return Sprite(im, f"waz-luska-{v}", rim=2, clean=False)


@lru_cache(None)
def paleczki():
    w, h = 160, 40
    return Sprite(stack(w, h, [(_band((6, 14), (154, 10), 5), (150, 110, 70)), (_band((8, 26), (156, 30), 5), (140, 100, 64))], seed=320),
                  "paleczki", rim=1, clean=False)


@lru_cache(None)
def grzebien():
    w, h = 120, 70
    parts = [(lambda d, s: d.chord([4 * s, 0, 116 * s, 80 * s], 180, 360, fill=255), (196, 60, 50)), (rect(8, 36, 112, 48), (196, 60, 50))]
    im = stack(w, h, parts, seed=325)
    d = ImageDraw.Draw(im)
    for x in range(14, 110, 8):
        d.line([(x, 46), (x, 68)], fill=(170, 50, 40, 255), width=4)
    return Sprite(im, "grzebien", rim=1, clean=False)


# ---------- morze: łodzie ----------

@lru_cache(None)
def lodz(v=0):
    """Łódź z epoki kofun: długi kadłub z zadartym dziobem i rufą, wiosła, żagiel z maty (v = 1: bez żagla)."""
    w, h = 560, 420
    hull = (110, 74, 50)
    hull_pts = [(10, 250), (40, 290), (110, 330), (450, 330), (520, 290), (552, 220), (530, 230), (480, 290), (90, 296), (40, 270)]
    parts = []
    if v != 1:
        parts += [(rect(270, 60, 280, 300), (80, 56, 40)), (poly([(170, 80), (380, 80), (390, 250), (160, 250)]), (220, 200, 156),
                                                             dict(kind="gladki", edge=3, contrast=1.3))]
    parts += [(poly(hull_pts), hull, dict(edge=2, contrast=1.2)), (poly([(90, 296), (480, 290), (470, 306), (100, 310)]), (150, 104, 70)),
              (poly([(110, 314), (450, 314), (444, 324), (116, 324)]), (196, 64, 40))]
    im = stack(w, h, parts, seed=330 + v)
    d = ImageDraw.Draw(im)
    if v != 1:
        for y in (110, 140, 170, 200, 230):
            d.line([(168, y), (386, y)], fill=(150, 120, 80, 200), width=2)
        for x in (210, 250, 300, 340):
            d.line([(x, 82), (x + 2, 248)], fill=(150, 120, 80, 160), width=2)
    for x in (140, 210, 280, 350, 420):  # wiosła
        d.line([(x, 300), (x - 40, 400)], fill=(90, 62, 44, 255), width=6)
        d.polygon([(x - 40, 392), (x - 52, 418), (x - 34, 420), (x - 30, 396)], fill=(110, 76, 52, 255))
    return Sprite(im, f"lodz-{v}", rim=2, clean=False)


@lru_cache(None)
def szkielet_lodzi():
    w, h = 520, 240
    parts = [(_band((20, 200), (500, 200), 12), (150, 112, 74))]
    for k in range(9):
        x = 60 + k * 50
        parts.append((lambda d, s, x=x: d.arc([(x - 40) * s, 80 * s, (x + 40) * s, 280 * s], 180, 360, fill=255, width=int(8 * s)),
                      (140, 102, 66)))
    return Sprite(stack(w, h, parts, seed=340), "szkielet-lodzi", rim=1, clean=False)


# ---------- Kumano i ptaki ----------

@lru_cache(None)
def niedzwiedz():
    w, h = 560, 340
    pts = [(40, 250), (60, 150), (130, 90), (260, 70), (380, 80), (440, 100), (470, 70), (500, 90), (520, 140), (548, 170), (520, 196),
           (470, 196), (450, 240), (440, 330), (400, 330), (390, 260), (300, 250), (200, 260), (170, 330), (130, 330), (120, 270), (60, 300)]
    parts = [(poly(pts), (30, 28, 30), dict(edge=0, contrast=1.1)), (poly([(400, 170), (440, 190), (420, 214), (380, 200)]), (232, 226, 210)),
             (ell(494, 130, 6, 6), (200, 160, 60))]
    return Sprite(stack(w, h, parts, seed=350), "niedzwiedz", rim=2, clean=False)


def _ptak(color, f, three_legs=False, perch=False, seed=0, gold=False):
    w, h = 440, 300
    dark = _shade(color, 0.75)
    if perch:
        wing = [(150, 130), (300, 110), (330, 190), (180, 200)]
    elif f == 0:
        wing = [(170, 140), (120, 20), (40, 0), (250, 130)]
    else:
        wing = [(170, 140), (110, 260), (40, 290), (250, 150)]
    parts = [(poly([(60, 150), (160, 120), (300, 120), (380, 100), (420, 120), (390, 140), (330, 170), (200, 190), (60, 180), (10, 200),
                    (20, 160)]), color, dict(edge=0 if not gold else 2)),
             (poly([(392, 112), (436, 122), (396, 130)]), (60, 50, 40) if not gold else (200, 130, 40)),
             (poly(wing), dark, dict(edge=0))]
    if perch or three_legs:
        for x in ((230, 260, 290) if three_legs else (240, 280)):
            parts.append((rect(x, 180, x + 8, 260), (60, 50, 44) if not gold else (200, 140, 50)))
            parts.append((poly([(x - 14, 258), (x + 22, 258), (x + 4, 268)]), (60, 50, 44) if not gold else (200, 140, 50)))
    im = stack(w, h, parts, seed=360 + seed)
    ImageDraw.Draw(im).ellipse([378, 108, 388, 118], fill=(230, 200, 80, 255) if not gold else (60, 30, 20, 255))
    return im


@lru_cache(None)
def wrona(f=0, perch=False):
    return Sprite(_ptak((36, 34, 40), f, three_legs=True, perch=perch, seed=f + 2 * perch), f"wrona-{f}-{perch}", rim=2, clean=False)


@lru_cache(None)
def zloty_ptak(f=0, perch=False):
    return Sprite(_ptak((226, 180, 70), f, perch=perch, seed=10 + f + 2 * perch, gold=True), f"zloty-{f}-{perch}", rim=2, clean=False)


@lru_cache(None)
def spichlerz():
    """Spichlerz na palach z dachem z trzciny (Kumano, Takakuraji)."""
    w, h = 380, 420
    wood = (140, 100, 66)
    parts = [(rect(70, 200, 310, 330), (176, 140, 96), dict(edge=2))]
    for x in (80, 180, 290):
        parts.append((rect(x, 320, x + 14, 420), wood))
    parts += [(rect(60, 320, 320, 334), wood), (poly([(30, 210), (190, 60), (350, 210)]), (170, 136, 78), dict(edge=3, shade=0.2))]
    return Sprite(stack(w, h, parts, seed=370), "spichlerz", rim=2, clean=False)


@lru_cache(None)
def order():
    """Order Złotej Kani: ośmioramienna gwiazda, złoty ptak na tarczy, wstążka."""
    w, h = 300, 420
    parts = [(poly([(110, 10), (190, 10), (180, 150), (120, 150)]), (60, 110, 80)), (rect(140, 10, 160, 150), (230, 210, 150))]
    star = []
    for k in range(16):
        a = math.pi * 2 * k / 16 - math.pi / 2
        rr = 130 if k % 2 == 0 else 80
        star.append((150 + rr * math.cos(a), 280 + rr * math.sin(a)))
    parts += [(poly(star), (214, 176, 90), dict(edge=2)), (ell(150, 280, 62, 62), (170, 40, 40)), (ell(150, 280, 50, 50), (226, 196, 110))]
    im = stack(w, h, parts, seed=380)
    bird = Image.fromarray(np.asarray(_ptak((150, 100, 30), 0, seed=99, gold=True)))
    bird = bird.resize((96, 66), Image.LANCZOS)
    im.alpha_composite(bird, (102, 248))
    return Sprite(im, "order", rim=2, clean=False)


# ---------- Yamato: domy, pałac ----------

@lru_cache(None)
def dom():
    """Chata wodza z pułapką: ściany z desek, dach z trzciny; belka pułapki osobno."""
    w, h = 420, 360
    parts = [(rect(60, 170, 360, 350), (160, 124, 84), dict(edge=2, shade=0.2)), (rect(170, 220, 250, 350), (40, 28, 24)),
             (poly([(20, 190), (210, 30), (400, 190)]), (170, 136, 78), dict(edge=3, shade=0.2))]
    return Sprite(stack(w, h, parts, seed=390), "dom", rim=2, clean=False)


@lru_cache(None)
def belka():
    w, h = 220, 60
    return Sprite(stack(w, h, [(rect(4, 10, 216, 50), (90, 70, 56), dict(contrast=1.3))], seed=395), "belka", rim=2, clean=False)


PALAC_WH = (1000, 700)


@lru_cache(None)
def palac(czesc):
    """Pałac Kashihara w częściach o wspólnym układzie (crop=False): słupy, podłoga z gankiem i schodami, ściany, dach,
    zwieńczenie (skrzyżowane deski chigi i kłody katsuogi)."""
    w, h = PALAC_WH
    wood, roof = (172, 128, 84), (164, 128, 70)
    if czesc == "slupy":
        parts = [(rect(x, 400, x + 26, 690), _shade(wood, 0.9)) for x in (180, 330, 480, 630, 780)]
    elif czesc == "podloga":
        parts = [(rect(130, 400, 870, 430), wood, dict(edge=2)), (rect(120, 426, 880, 440), _shade(wood, 0.75))]
        for k in range(6):  # schody
            parts.append((rect(440 + k * 6, 440 + k * 40, 560 - k * 6, 454 + k * 40), _shade(wood, 1.0 - 0.04 * k)))
        parts += [(rect(150, 360, 158, 402), wood), (rect(842, 360, 850, 402), wood), (rect(150, 360, 850, 368), wood)]
    elif czesc == "sciany":
        parts = [(rect(220, 230, 780, 400), (226, 206, 168), dict(edge=2)), (rect(440, 270, 560, 400), (60, 40, 30))]
        for x in (220, 330, 660, 770):
            parts.append((rect(x, 230, x + 12, 400), wood))
    elif czesc == "dach":
        parts = [(poly([(120, 250), (500, 90), (880, 250), (850, 262), (150, 262)]), roof, dict(edge=4, shade=0.25))]
    else:  # zwieńczenie
        parts = [(rect(300, 80, 700, 98), (110, 80, 56))]
        for x in (340, 420, 500, 580, 660):
            parts.append((ell(x, 74, 22, 14), (130, 96, 64)))
        for x, sgn in ((300, -1), (700, 1)):
            parts.append((_band((x, 98), (x + sgn * 70, 10), 14), (120, 88, 60)))
            parts.append((_band((x + sgn * 40, 98), (x - sgn * 30 + sgn * 70, 10), 14), (110, 80, 56)))
    im = stack(w, h, parts, seed=400 + len(czesc))
    if czesc == "dach":
        d = ImageDraw.Draw(im)
        for k in range(1, 8):
            f = k / 8
            d.line([(500 - 380 * f, 90 + 160 * f), (500 + 380 * f, 90 + 160 * f)], fill=_shade(roof, 0.7) + (150,), width=3)
    return Sprite(im, f"palac-{czesc}", rim=2, clean=False, pad=0, crop=False)


@lru_cache(None)
def chata_jomon(v=0):
    w, h = 300, 260
    col = ((176, 140, 80), (160, 126, 74))[v % 2]
    parts = [(poly([(20, 250), (150, 20), (280, 250)]), col, dict(edge=3, shade=0.2)), (poly([(120, 250), (150, 170), (180, 250)]), (40, 28, 24))]
    im = stack(w, h, parts, seed=410 + v)
    d = ImageDraw.Draw(im)
    for k in range(1, 7):
        y = 20 + 230 * k / 7
        d.line([(150 - 130 * k / 7, y), (150 + 130 * k / 7, y)], fill=_shade(col, 0.7) + (140,), width=2)
    return Sprite(im, f"chata-jomon-{v}", rim=2, clean=False)


@lru_cache(None)
def garnek(v=0):
    """Gliniany garnek z epoki Jōmon: płomienisty brzeg, odciski sznura."""
    w, h = 200, 260
    clay = ((170, 116, 74), (150, 100, 66))[v % 2]
    rim_ = [(20, 70), (40, 20), (60, 60), (80, 10), (100, 56), (120, 10), (140, 60), (160, 20), (180, 70)]
    parts = [(poly([(30, 70), (170, 70), (180, 160), (140, 250), (60, 250), (20, 160)]), clay, dict(edge=2, shade=0.25)),
             (poly(rim_ + [(180, 80), (20, 80)]), _shade(clay, 1.1))]
    im = stack(w, h, parts, seed=420 + v)
    d = ImageDraw.Draw(im)
    for y in range(100, 240, 12):
        d.line([(30 + (y - 70) * 0.1, y), (170 - (y - 70) * 0.1, y + 4)], fill=_shade(clay, 0.7) + (170,), width=2)
    return Sprite(im, f"garnek-{v}", rim=2, clean=False)


# ---------- historia: mapa, pieczęć, kurhan, haniwa, tron ----------

MAPA_WH = (900, 640)
_GEO = {  # zarysy wysp: (długość, szerokość geograficzna) przylądków i zatok, uproszczone
    "hokkaido": [(141.9, 45.5), (143.0, 44.6), (145.3, 44.3), (145.6, 43.3), (144.4, 42.9), (143.2, 41.9), (141.6, 42.6), (140.9, 41.8),
                 (140.2, 41.4), (140.1, 42.2), (140.5, 42.6), (141.0, 43.2), (141.6, 43.9), (141.7, 44.9)],
    "honsiu": [(140.35, 41.25), (140.9, 41.5), (141.4, 41.3), (141.5, 40.5), (142.0, 39.6), (141.6, 38.9), (141.5, 38.3), (141.0, 38.2),
               (141.0, 37.0), (140.9, 35.7), (139.9, 34.9), (139.8, 35.4), (138.9, 34.6), (138.2, 34.6), (136.9, 34.3), (135.8, 33.4),
               (135.1, 34.2), (135.4, 34.6), (135.0, 34.7), (134.0, 34.6), (132.4, 34.3), (130.9, 33.95), (131.4, 34.4), (132.7, 35.4),
               (134.2, 35.5), (135.2, 35.75), (136.0, 35.65), (136.8, 36.8), (137.3, 37.5), (137.2, 36.75), (139.0, 37.9), (140.0, 39.7),
               (140.2, 40.8)],
    "sikoku": [(132.0, 33.3), (132.7, 33.85), (134.0, 34.35), (134.6, 34.2), (134.2, 33.25), (133.5, 33.5), (133.0, 32.7)],
    "kiusiu": [(130.9, 33.9), (130.4, 33.6), (129.9, 33.5), (129.8, 32.75), (130.0, 32.4), (130.2, 31.4), (130.65, 31.0), (131.45, 31.9),
               (131.7, 32.6), (131.65, 33.25), (131.7, 33.6)],
}


def geo(lon, lat):
    """Punkt mapy (arkusz 900 × 640) z długości i szerokości geograficznej."""
    return (40 + (lon - 129) * 48, 30 + (45.6 - lat) * 40)


MAPA_WH = (900, 640)
WYSPY = {k: [geo(*p) for p in v] for k, v in _GEO.items()}


@lru_cache(None)
def mapa_plansza():
    w, h = MAPA_WH
    sea = piece(w, h, rect(2, 2, w - 2, h - 2), (196, 214, 210), "gladki", edge=5, seed=430, contrast=1.3)
    return Sprite(sea, "mapa-plansza", rim=2, clean=False, pad=0, crop=False)


@lru_cache(None)
def mapa_wyspa(k):
    w, h = MAPA_WH
    im = piece(w, h, poly(WYSPY[k]), (214, 196, 150), "gnieciony", edge=3, seed=431 + len(k), contrast=0.9)
    return Sprite(im, f"mapa-{k}", rim=2, clean=False, pad=0, crop=False)


def _w_wielokacie(x, y, pts):
    inside, j = False, len(pts) - 1
    for i in range(len(pts)):
        (xi, yi), (xj, yj) = pts[i], pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def punkty_na_mapie(n, seed=0):
    """Losowe punkty wewnątrz wysp (bez Hokkaido) — do chorągiewek państewek Wa."""
    r = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = r.uniform(40, 760), r.uniform(160, 630)
        if any(_w_wielokacie(x, y, WYSPY[k]) for k in ("honsiu", "sikoku", "kiusiu")):
            out.append((x, y))
    return out


@lru_cache(None)
def choragiewka(v=0):
    """Mała chorągiewka: biała z czerwonym słońcem (v = 0) albo maleńka szpilka państewka (v = 1)."""
    if v == 0:
        w, h = 160, 240
        parts = [(rect(8, 10, 16, 236), (90, 64, 44)), (rect(16, 14, 150, 104), (246, 242, 232), dict(kind="gladki", edge=2)),
                 (ell(83, 59, 26, 26), (206, 44, 36))]
    else:
        w, h = 40, 80
        parts = [(rect(18, 20, 22, 80), (60, 44, 34)), (poly([(22, 20), (38, 28), (22, 36)]), (196, 64, 40))]
    return Sprite(stack(w, h, parts, seed=440 + v), f"choragiewka-{v}", rim=1, clean=False)


@lru_cache(None)
def pieczec():
    """Złota pieczęć króla Na: kostka z wężem zwiniętym na uchwycie."""
    w, h = 300, 320
    gold = (214, 172, 70)
    parts = [(rect(60, 180, 240, 300), gold, dict(edge=2, contrast=1.2)), (poly([(60, 180), (90, 160), (270, 160), (240, 180)]), _shade(gold, 1.12)),
             (poly([(240, 180), (270, 160), (270, 280), (240, 300)]), _shade(gold, 0.8)),
             (ell(160, 150, 76, 34), _shade(gold, 0.95), dict(edge=2)), (ell(150, 124, 56, 26), gold, dict(edge=2)),
             (ell(176, 98, 30, 22), _shade(gold, 1.08), dict(edge=2)), (poly([(196, 92), (232, 98), (200, 108)]), _shade(gold, 0.9))]
    im = stack(w, h, parts, seed=450)
    ImageDraw.Draw(im).ellipse([192, 90, 198, 96], fill=(60, 40, 20, 255))
    return Sprite(im, "pieczec", rim=2, clean=False)


@lru_cache(None)
def odcisk():
    """Czerwony odcisk pieczęci: 漢委奴國王 w trzech kolumnach czytanych od prawej, jak na prawdziwej pieczęci:
    漢 sam w prawej kolumnie (wydłużony), 委奴 w środkowej, 國王 w lewej."""
    w, h = 300, 300
    parts = [(rect(20, 20, 280, 280), (186, 40, 36), dict(kind="gladki", contrast=1.1))]
    im = stack(w, h, parts, seed=455)
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_ZH, 92, index=ZH_IDX)
    one = Image.new("L", (112, 112), 0)
    ImageDraw.Draw(one).text((56, 56), "漢", font=f, fill=255, anchor="mm")
    m.paste(one.resize((112, 224), Image.LANCZOS), (228 - 56, 150 - 112))
    for txt, x in (("委奴", 150), ("國王", 72)):
        for k, ch in enumerate(txt):
            d.text((x, 92 + k * 112), ch, font=f, fill=255, anchor="mm")
    a = np.asarray(im.getchannel("A"), np.float32) * (1 - np.asarray(m, np.float32) / 255 * 0.85)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return Sprite(im, "odcisk", rim=1, clean=False)


@lru_cache(None)
def kofun_plansza():
    """Kurhan w kształcie dziurki od klucza z lotu ptaka: zielony kopiec, dwie fosy, plansza z papieru."""
    w, h = 1000, 560
    key = lambda pad: (lambda d, s: (d.ellipse([(620 - 190 - pad) * s, (280 - 190 - pad) * s, (620 + 190 + pad) * s, (280 + 190 + pad) * s],
                                               fill=255),
                                     d.polygon([((220 - pad) * s, (120 - pad) * s), (620 * s, (200 - pad) * s), (620 * s, (360 + pad) * s),
                                                ((220 - pad) * s, (440 + pad) * s)], fill=255)))
    parts = [(rect(6, 6, w - 6, h - 6), (214, 200, 160), dict(kind="gladki", edge=5, contrast=1.3)),
             (key(70), (124, 160, 170)), (key(52), (184, 190, 150)), (key(34), (110, 150, 160)), (key(0), (74, 116, 70), dict(edge=3)),
             (ell(620, 280, 90, 90), (92, 134, 80)), (rect(260, 230, 560, 330), (92, 134, 80))]
    im = stack(w, h, parts, seed=460)
    m = Image.new("L", (w, h), 0)
    key(0)(ImageDraw.Draw(m), 1)
    ma = np.asarray(m)
    d = ImageDraw.Draw(im)
    r = random.Random(461)
    for k in range(420):  # drzewa porastające kopiec
        x, y = r.uniform(200, 820), r.uniform(80, 480)
        if ma[int(y), int(x)] > 0 and ma[int(y) - 9, int(x)] > 0 and ma[int(y) + 9, int(x)] > 0:
            g = r.choice(((56, 96, 58), (66, 108, 64), (48, 84, 52)))
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=g + (235,))
    return Sprite(im, "kofun", rim=2, clean=False)


@lru_cache(None)
def haniwa(kind):
    """Gliniana figurka haniwa: walec z otworami oczu i ust; wojownik, koń, dom, tancerz."""
    clay = (198, 132, 90)
    dk = (70, 40, 30)
    if kind == "kon":
        w, h = 360, 300
        parts = [(rect(60, 190, 90, 296), clay), (rect(110, 190, 140, 296), clay), (rect(230, 190, 260, 296), clay), (rect(280, 190, 310, 296), clay),
                 (ell(190, 160, 140, 60), clay, dict(edge=2)), (poly([(280, 140), (330, 40), (356, 56), (330, 170)]), clay),
                 (ell(338, 60, 22, 30), clay), (poly([(150, 100), (240, 100), (240, 130), (150, 130)]), _shade(clay, 0.85))]
        im = stack(w, h, parts, seed=470)
        ImageDraw.Draw(im).ellipse([336, 48, 346, 58], fill=dk + (255,))
        return Sprite(im, "haniwa-kon", rim=2, clean=False)
    if kind == "dom":
        w, h = 260, 300
        parts = [(rect(40, 150, 220, 296), clay, dict(edge=2)), (poly([(10, 160), (130, 40), (250, 160)]), _shade(clay, 0.9), dict(edge=2)),
                 (rect(110, 200, 150, 296), dk)]
        return Sprite(stack(w, h, parts, seed=471), "haniwa-dom", rim=2, clean=False)
    w, h = 200, 420
    parts = [(poly([(54, 160), (146, 160), (156, 416), (44, 416)]), clay, dict(edge=2, shade=0.2)), (ell(100, 100, 50, 60), clay, dict(edge=2))]
    if kind == "wojownik":
        parts += [(poly([(46, 70), (100, 30), (154, 70), (150, 92), (50, 92)]), _shade(clay, 0.9)), (rect(40, 220, 160, 300), _shade(clay, 0.92))]
    if kind == "tancerz":
        parts += [(_band((140, 190), (190, 70), 26), clay), (_band((60, 190), (20, 260), 26), clay)]
    if kind == "kobieta":
        parts += [(rect(66, 40, 134, 60), _shade(clay, 0.9)), (ell(100, 34, 40, 18), _shade(clay, 0.9))]
    im = stack(w, h, parts, seed=472 + len(kind))
    d = ImageDraw.Draw(im)
    holes = Image.new("L", (w, h), 0)
    hd = ImageDraw.Draw(holes)
    for x0 in (74, 112):  # oczy i usta to prawdziwe otwory w glinie: widać przez nie to, co za figurką
        d.ellipse([x0 - 3, 87, x0 + 19, 107], fill=_shade(clay, 0.6) + (255,))
        hd.ellipse([x0, 90, x0 + 16, 104], fill=255)
    d.ellipse([89, 119, 111, 137], fill=_shade(clay, 0.6) + (255,))
    hd.ellipse([92, 122, 108, 134], fill=255)
    a_ = np.asarray(im.getchannel("A"), np.float32) * (1 - np.asarray(holes, np.float32) / 255)
    im.putalpha(Image.fromarray(a_.astype(np.uint8)))
    if kind == "wojownik":
        for y in (236, 256, 276):
            d.line([(44, y), (156, y)], fill=_shade(clay, 0.7) + (200,), width=3)
    return Sprite(im, f"haniwa-{kind}", rim=2, clean=False)


@lru_cache(None)
def takamikura():
    """Tron pod ośmiokątnym baldachimem: czarny podest, purpurowe zasłony, złoty feniks na szczycie."""
    w, h = 640, 760
    lak = (34, 28, 30)
    parts = [(rect(60, 600, 580, 680), lak, dict(contrast=1.2)), (rect(40, 680, 600, 740), lak), (rect(60, 596, 580, 606), GOLD),
             (poly([(140, 210), (500, 210), (520, 600), (120, 600)]), (96, 52, 104), dict(edge=2, shade=0.25)),
             (poly([(300, 230), (340, 230), (350, 600), (290, 600)]), (226, 206, 160)),
             (poly([(90, 220), (320, 110), (550, 220), (530, 236), (110, 236)]), lak, dict(edge=2)),
             (rect(100, 230, 540, 244), GOLD), (poly([(296, 112), (344, 112), (320, 60)]), GOLD),
             (poly([(320, 60), (290, 20), (330, 36), (370, 6), (350, 50)]), GOLD)]
    for x in (130, 220, 410, 500):
        parts.append((rect(x, 244, x + 10, 600), lak))
    return Sprite(stack(w, h, parts, seed=480), "takamikura", rim=2, clean=False)


@lru_cache(None)
def skrzynka():
    """Skrzynka ze skarbem owinięta białym płótnem, na niskim stojaku."""
    w, h = 220, 260
    parts = [(rect(30, 190, 190, 210), (60, 40, 30)), (rect(46, 210, 58, 256), (60, 40, 30)), (rect(162, 210, 174, 256), (60, 40, 30)),
             (rect(40, 60, 180, 190), (246, 244, 236), dict(kind="gladki", edge=2)), (poly([(40, 60), (110, 20), (180, 60)]), (240, 238, 228)),
             (rect(100, 30, 120, 190), (226, 208, 150))]
    return Sprite(stack(w, h, parts, seed=490), "skrzynka", rim=2, clean=False)


@lru_cache(None)
def parawan():
    """Parawan z papieru ryżowego w ramie z listew (cień władcy pada na papier od tyłu)."""
    w, h = 760, 480
    parts = [(rect(10, 10, 750, 470), (246, 236, 210), dict(kind="gladki", contrast=1.1))]
    im = stack(w, h, parts, seed=495)
    return Sprite(im, "parawan", rim=0, clean=False, crop=False)


@lru_cache(None)
def parawan_rama():
    w, h = 760, 480
    wood = (86, 58, 40)
    parts = [(rect(0, 0, w, 16), wood), (rect(0, h - 16, w, h), wood), (rect(0, 0, 16, h), wood), (rect(w - 16, 0, w, h), wood)]
    parts += [(rect(x, 0, x + 6, h), wood) for x in range(126, 740, 126)]
    parts += [(rect(0, y, w, y + 6), wood) for y in range(118, 470, 118)]
    return Sprite(stack(w, h, parts, seed=496), "parawan-rama", rim=1, clean=False, crop=False)


@lru_cache(None)
def zwoj_jp():
    """Zwój papieru zapisany kolumnami znaków (kronika): rozwija się w prawo."""
    w, h = 720, 220
    parts = [(rect(20, 20, 700, 200), (240, 230, 204), dict(kind="gladki", edge=2)), (rect(4, 10, 30, 210), (120, 70, 40)),
             (rect(690, 10, 716, 210), (120, 70, 40))]
    im = stack(w, h, parts, seed=500)
    from PIL import ImageFont
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_ZH, 22, index=ZH_IDX)
    txt = "天地初發之時於高天原成神名天之御中主神次高御產巢日神次神產巢日神此三柱神者並獨神成坐而隱身也"
    k = 0
    for x in range(660, 60, -30):
        for y in range(40, 190, 26):
            d.text((x, y), txt[k % len(txt)], font=f, fill=(40, 30, 26, 230), anchor="mm")
            k += 1
    return Sprite(im, "zwoj-jp", rim=2, clean=False, crop=False)


@lru_cache(None)
def kalendarz():
    w, h = 220, 260
    parts = [(rect(10, 10, 210, 250), (246, 242, 232), dict(kind="gladki", edge=2)), (rect(10, 10, 210, 60), (196, 46, 36)),
             (glyphs("11", 110, FONT_PL, PL_IDX, (110, 150), "mm"), (40, 30, 26), dict(kind="gladki", rough=0.5)),
             (glyphs(tr("LUTEGO"), 30, FONT_PL, PL_IDX, (110, 222), "mm"), (40, 30, 26), dict(kind="gladki", rough=0.5))]
    return Sprite(stack(w, h, parts, seed=510), "kalendarz", rim=2, clean=False)


@lru_cache(None)
def grad():
    return Sprite(piece(24, 24, ell(12, 12, 9, 9), (240, 244, 248), "gladki", rough=0.5), "grad", rim=1, clean=False)


@lru_cache(None)
def proporzec(v=0):
    """Wysoki proporzec wodza (nobori) na drzewcu: barwne płótno z białym znakiem-krążkiem."""
    col = ((60, 40, 36), (120, 50, 40), (70, 80, 60), (240, 236, 224))[v % 4]
    w, h = 160, 520
    parts = [(rect(14, 10, 24, 516), (80, 56, 40)), (rect(24, 30, 130, 330), col, dict(edge=2, shade=0.15)), (rect(20, 24, 136, 32), (80, 56, 40)),
             (ell(77, 120, 34, 34), (236, 230, 214) if v != 3 else (196, 46, 36))]
    return Sprite(stack(w, h, parts, seed=520 + v), f"proporzec-{v}", rim=2, clean=False)


@lru_cache(None)
def wyspa_gola(v=0):
    """Wyspa bez sosen (stoją na niej bogowie): wierzch liczy się z alfy, więc stopy stają na ziemi."""
    r = random.Random(40 + v)
    w, h = 620, 300
    pts = [(x, 280 - 150 * math.exp(-((x - w / 2) / 210.0) ** 2) ** 0.7) for x in range(20, w - 19, 12)]
    body = poly(pts + [(w - 20, 300), (20, 300)])
    top = poly([(x, y - 2) for x, y in pts] + [(x, y + 30 + 8 * math.sin(x / 23.0)) for x, y in reversed(pts)])
    im = stack(w, h, [(body, (120, 110, 92), dict(edge=3, shade=0.25)), (top, (82, 124, 76), dict(edge=2)),
                      (poly([(20, 276), (w - 20, 276), (w - 20, 300), (20, 300)]), (220, 204, 160))], seed=66 + v + r.randint(0, 3))
    return Sprite(im, f"wyspa-gola-{v}", rim=2, clean=False)


# ---------- krajobraz Japonii ----------
# Reżyser 13.11: nie chińskie góry i sosny z „Pierwszego cesarza”, tylko Japonia tamtych czasów — Fuji, okrągłe pagórki
# z polanami, wiśnie, bambusy. Wszystko wycięte kodem; wycinków krajobrazu z poprzedniego filmu tu nie ma.

def _maska(w, h, shapes, rough=1.6, seed=0):
    """Jedna maska z wielu kształtów (poly/ell) — jeden arkusz papieru zamiast arkusza na każdy kształt."""
    return rough_mask(lambda d, s: [f(d, s) for f in shapes], w, h, rough=rough, seed=seed)


def _naklej(im, shapes, color, seed, kind="gnieciony", edge=0, shade=0.0, contrast=0.8, clip=None, shadow=0.42, rough=1.6):
    if not shapes:
        return im
    w, h = im.size
    m = _maska(w, h, shapes, rough=rough, seed=seed)
    if clip is not None:  # tylko tam, gdzie pod spodem jest już papier (nie zmienia obrysu)
        m = Image.fromarray((np.asarray(m, np.float32) * clip).astype(np.uint8))
    return glue(im, paper(m, color, kind, seed, edge=edge, shade=shade, contrast=contrast), shadow=shadow)


def _alfa(im):
    return np.asarray(im.getchannel("A"), np.float32) / 255.0


def _konar(x0, y0, x1, y1, w0, w1):
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    return poly([(x0 + nx * w0 / 2, y0 + ny * w0 / 2), (x1 + nx * w1 / 2, y1 + ny * w1 / 2),
                 (x1 - nx * w1 / 2, y1 - ny * w1 / 2), (x0 - nx * w0 / 2, y0 - ny * w0 / 2)])


def _lisc(x, y, ang, L, W):
    """Wąski, lancetowaty liść (bambus) od (x, y) w kierunku ang (radiany, y w dół)."""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    return poly([(x, y), (x + dx * L * 0.32 + nx * W / 2, y + dy * L * 0.32 + ny * W / 2), (x + dx * L, y + dy * L),
                 (x + dx * L * 0.32 - nx * W / 2, y + dy * L * 0.32 - ny * W / 2)])


@lru_cache(None)
def fuji(v=0):
    """Fuji z papieru: wklęsłe stoki, płaski szczyt z ząbkami krateru, czapa śniegu z jęzorami w żlebach; stok od światła
    jaśniejszy, drugi ciemniejszy. v=1: zielony stożek Takachiho, bez śniegu."""
    w, h = 1400, 620
    cx, top, base, ht, hb = 700, 80, 600, (70 if v == 0 else 24), 680
    k = 1.9 if v == 0 else 1.45
    r = random.Random(300 + v)

    def prof(x):
        d = clamp((abs(x - cx) - ht) / (hb - ht), 0, 1)
        y = top + (base - top) * (1 - (1 - d) ** k)
        if v == 0 and abs(x - cx) <= ht:
            y += 6 * math.sin((x - cx) / 12.0) ** 2
        return y

    pts = [(x, prof(x) + r.uniform(-1.2, 1.2)) for x in range(cx - hb, cx + hb + 1, 6)]
    light, dark = ((128, 138, 178), (100, 108, 152)) if v == 0 else ((98, 128, 96), (76, 104, 80))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im = _naklej(im, [poly(pts + [(cx + hb, h), (cx - hb, h)])], light, 310 + v, edge=4, shade=0.12, rough=2.0)
    right = [(cx + 12, prof(cx + 12) + 3)] + [(x, y + 3) for x, y in pts if x > cx + 12] + [(cx + hb, h), (cx + 170, h)]
    im = _naklej(im, [poly(right)], dark, 320 + v, contrast=0.7, clip=_alfa(im), shadow=0.2)
    if v == 0:
        ph = r.uniform(0, 6.28)
        jez = [(r.uniform(cx - 230, cx + 230), r.uniform(14, 72), r.uniform(4, 11)) for _ in range(16)]  # jęzory śniegu w żlebach
        low = lambda x: 228 + 14 * math.sin(x / 53.0 + ph) + max(L * math.exp(-((x - fx) / fw) ** 2) for fx, L, fw in jez)
        xs = [x for x in range(cx - hb, cx + hb + 1, 4) if prof(x) < low(x) - 4]
        snow = [(x, prof(x) - 1) for x in xs] + [(x, low(x)) for x in reversed(xs)]
        im = _naklej(im, [poly(snow)], (246, 244, 238), 330, kind="gladki", edge=3, clip=_alfa(im), shadow=0.3, rough=1.2)
        streaks = []
        for j in range(9):  # pojedyncze smugi śniegu niżej w żlebach
            x = cx + r.uniform(-260, 260)
            y0 = low(x) + r.uniform(4, 20)
            L = r.uniform(30, 80)
            streaks.append(_konar(x, y0, x + (x - cx) * 0.12, y0 + L, 6, 1))
        im = _naklej(im, streaks, (236, 236, 232), 335, kind="gladki", clip=_alfa(im), shadow=0.15, rough=0.8)
    return Sprite(im, f"fuji-{v}", rim=2, clean=False)


KOLORY_WZGORZ = {
    "zielone": dict(tyl=(102, 130, 106), przod=(130, 156, 108), kepy=(70, 102, 78), kepy2=(92, 124, 86), polany=(176, 190, 128),
                    wisnie=(240, 198, 210)),
    "niebieskie": dict(tyl=(96, 118, 152), przod=(120, 142, 164), kepy=(82, 102, 136), kepy2=(104, 126, 152), polany=None,
                       wisnie=(222, 198, 216)),
}


@lru_cache(None)
def wzgorza_jp(v=0, kolor="zielone"):
    """Okrągłe, zalesione pagórki (satoyama): dwa rzędy kopuł, grzbiet z kęp drzew, jasne polany na stokach i różowe
    kępy dzikich wiśni. kolor="niebieskie" — błękitne góry dookoła Yamato."""
    K = KOLORY_WZGORZ[kolor]
    w, h = 1600, 420
    r = random.Random(400 + 13 * v + len(kolor))

    def grzbiet(n, hmin, hmax, smin, smax, base):
        humps = [((i + r.uniform(0.2, 0.8)) * w / n, r.uniform(hmin, hmax), r.uniform(smin, smax)) for i in range(n)]
        return [(x, base - max(hh * math.exp(-((x - c) / s) ** 2) for c, hh, s in humps) - 8) for x in range(0, w + 1, 8)]

    if kolor == "niebieskie":  # pierścień błękitnych gór Yamato: wyższe kopuły
        back, front = grzbiet(5, 190, 300, 120, 200, 420), grzbiet(4, 90, 170, 150, 230, 420)
    elif v == 2:  # bliższe, łagodne pagórki z polanami
        back, front = grzbiet(3, 110, 170, 230, 330, 420), grzbiet(3, 50, 100, 270, 380, 420)
    else:  # dalekie pagórki pod Fuji: niższe i szersze, żeby góra stała ponad nimi
        back, front = grzbiet(4, 140, 220, 160, 240, 420), grzbiet(3, 70, 120, 220, 320, 420)
    yb = lambda x: back[min(len(back) - 1, max(0, int(x // 8)))][1]
    yf = lambda x: front[min(len(front) - 1, max(0, int(x // 8)))][1]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tufts_b, tufts_f = [], []
    x = 4
    while x < w:  # grzbiet z kęp drzew — guzowaty obrys lasu
        rr = r.uniform(9, 16)
        tufts_b.append(ell(x, yb(x) + rr * 0.55, rr, rr * 0.82))
        x += r.uniform(12, 22)
    im = _naklej(im, [poly(back + [(w, h), (0, h)])] + tufts_b, K["tyl"], 410 + v, edge=3, shade=0.1, rough=1.8)
    dots = []
    for _ in range(70):  # ciemniejsze kępy drzew na zboczach dalszego rzędu
        x = r.uniform(0, w)
        y = r.uniform(yb(x) + 20, 400)
        rr = r.uniform(8, 18)
        dots.append(ell(x, y, rr, rr * 0.8))
    im = _naklej(im, dots, K["kepy"], 415 + v, contrast=0.7, clip=_alfa(im), shadow=0.25, rough=1.0)
    x = 6
    while x < w:
        rr = r.uniform(7, 12)
        tufts_f.append(ell(x, yf(x) + rr * 0.6, rr, rr * 0.8))
        x += r.uniform(14, 30)
    im = _naklej(im, [poly(front + [(w, h), (0, h)])] + tufts_f, K["przod"], 420 + v, edge=3, shade=0.12, rough=1.8)
    fm = _maska(  # maska bliższego rzędu: polany nie wychodzą na dalszy
        w, h, [poly(front + [(w, h), (0, h)])], rough=0)
    front_a = np.asarray(fm, np.float32) / 255.0
    kep = []
    for _ in range(40):
        x = r.uniform(0, w)
        y = r.uniform(yf(x) + 16, 410)
        rr = r.uniform(7, 15)
        kep.append(ell(x, y, rr, rr * 0.8))
    im = _naklej(im, kep, K["kepy2"], 425 + v, contrast=0.7, clip=front_a, shadow=0.22, rough=1.0)
    if K["polany"]:
        gl = []
        for _ in range(11 if v == 2 else 6):
            x = r.uniform(80, w - 80)
            gl.append(ell(x, yf(x) + r.uniform(40, 90), r.uniform(60, 130), r.uniform(14, 26)))
        im = _naklej(im, gl, K["polany"], 430 + v, kind="gladki", clip=front_a, shadow=0.18, rough=2.2)
    sak = []
    for _ in range(9):  # dzikie wiśnie (yamazakura) — różowe kępy na stokach
        x = r.uniform(40, w - 40)
        y = r.uniform(min(yb(x), yf(x)) + 24, 380)
        for _ in range(3):
            rr = r.uniform(7, 13)
            sak.append(ell(x + r.uniform(-12, 12), y + r.uniform(-8, 8), rr, rr * 0.8))
    im = _naklej(im, sak, K["wisnie"], 435 + v, kind="gladki", edge=2, clip=_alfa(im), shadow=0.25, rough=1.0)
    return Sprite(im, f"wzgorza-{kolor}-{v}", rim=2, clean=False)


@lru_cache(None)
def gora_niebieska(v=0):
    """Błękitne góry Yamato (aoyama): okrągłe, zalesione pagórki w błękicie, wycięte kodem."""
    return wzgorza_jp(v, "niebieskie")


PALETY_DRZEW = {  # (pień, przetchlinki, korona: ciemna, średnia, jasna, drobne kwiatki?)
    "wisnia": ((78, 58, 56), (126, 102, 96), (226, 150, 178), (242, 186, 204), (252, 222, 230), True),
    "zielone": ((86, 64, 50), (120, 98, 80), (58, 96, 66), (82, 122, 80), (114, 150, 94), False),
}


@lru_cache(None)
def _drzewo_img(paleta, v):
    """Drzewo z papieru (rysunek, nie Sprite): pień z konarami rozchodzącymi się szeroko jak parasol i chmury korony.
    v: 0 duże (Konohanasakuya, d03), 1 kulisa z lewej (pochylona w prawo), 2 i 3 małe (wyspy), 4 gałąź-kulisa z rogu.
    Zwraca (obraz przycięty, kotwica nasady pnia w ułamkach)."""
    pien, przet, c_deep, c_mid, c_light, kwiatki = PALETY_DRZEW[paleta]
    #      płótno      nasada      kąt    długość grubość głębia  promień kiści
    cfg = {0: (1300, 1000, 650, 990, -0.04, 170, 70, 4, 60),
           1: (1100, 1000, 300, 990, 0.36, 195, 56, 4, 54),
           2: (420, 380, 210, 372, 0.06, 92, 18, 3, 24),
           3: (420, 380, 210, 372, -0.12, 88, 16, 3, 22),
           4: (1100, 760, 0, 260, 1.62, 170, 40, 4, 40)}[v]
    w, h, bx, by, ang0, L0, W0, depth, R = cfg
    r = random.Random(500 + 17 * v + len(paleta))
    trunk, lent, sites = [], [], []

    def grow(x, y, ang, L, W, d):
        x1, y1 = x + L * math.sin(ang), y - L * math.cos(ang)
        W1 = W * 0.64
        trunk.append(_konar(x, y, x1, y1, W, W1))
        trunk.append(ell(x1, y1, W1 / 2, W1 / 2))
        if W > 14:  # poziome przetchlinki na korze wiśni
            for k in range(int(L / 26)):
                f = (k + 0.5) / max(1, L / 26)
                px, py = x + (x1 - x) * f, y + (y1 - y) * f
                ww = (W + (W1 - W) * f) * 0.62
                lent.append(_konar(px - ww / 2 * math.cos(ang), py - ww / 2 * math.sin(ang),
                                   px + ww / 2 * math.cos(ang), py + ww / 2 * math.sin(ang), 2.4, 2.4))
        if d >= depth:
            sites.append((x1, y1, 1.0))
            return
        if d >= depth - 1 or (v == 4 and d >= 1):  # kulisa: kiście wzdłuż całej gałęzi
            sites.append((x1, y1, 0.8))
        n = 2 if d == 0 else r.choice((2, 2, 3))
        for j in range(n):
            a = ang + (j - (n - 1) / 2) * (0.85 if d == 0 else 0.78) + r.uniform(-0.2, 0.2)
            if v == 4:  # gałąź-kulisa idzie w prawo od rogu, lekko w dół — kiście wzdłuż niej, nie słup kwiecia
                a = clamp(a, 1.3, 2.05)
            else:  # konary wiśni rozkładają się szeroko na boki, ale nie opadają w dół
                a = clamp(a * (1.0 + 0.14 * d), -1.5, 1.5)
            grow(x1, y1, a, L * r.uniform(0.6, 0.78), W1, d + 1)

    grow(bx, by, ang0, L0, W0, 0)
    deep, mid, light = [], [], []
    for x, y, s in sites:
        for _ in range(r.randint(2, 3)):
            rr = R * s * r.uniform(0.75, 1.25)
            deep.append(ell(x + r.uniform(-0.8, 0.8) * R, y + r.uniform(-0.3, 0.6) * R, rr, rr * 0.8))
        for _ in range(r.randint(1, 3)):
            rr = R * s * r.uniform(0.55, 0.95)
            mid.append(ell(x + r.uniform(-0.7, 0.7) * R, y + r.uniform(-0.6, 0.3) * R, rr, rr * 0.8))
        rr = R * s * r.uniform(0.3, 0.55)
        light.append(ell(x + r.uniform(-0.6, 0.2) * R, y - r.uniform(0.2, 0.7) * R, rr, rr * 0.8))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    seed = 520 + 11 * v
    im = _naklej(im, deep, c_deep, seed, kind="gladki", edge=2, rough=1.4)
    im = _naklej(im, trunk, pien, seed + 1, contrast=0.9, rough=1.0)
    im = _naklej(im, lent, przet, seed + 2, kind="gladki", clip=_alfa(im), shadow=0.0, rough=0.4)
    im = _naklej(im, mid, c_mid, seed + 3, kind="gladki", edge=2, rough=1.4)
    im = _naklej(im, light, c_light, seed + 4, kind="gladki", edge=2, rough=1.2, shadow=0.3)
    if kwiatki:  # drobne kwiatki naklejone na kiście
        d = ImageDraw.Draw(im)
        a = _alfa(im)
        ys, xs = np.nonzero(a > 0.9)
        pink = [(xx, yy) for xx, yy in zip(xs[::37], ys[::37])]
        r.shuffle(pink)
        sc = max(1.0, R / 40)
        for xx, yy in pink[: 900 if v in (0, 1, 4) else 160]:
            px = im.getpixel((int(xx), int(yy)))
            if px[0] < 180:  # nie na pniu
                continue
            c = r.choice(((255, 238, 242), (250, 214, 226), (244, 190, 208), (255, 246, 248)))
            rr = r.uniform(2.2, 4.6) * sc
            d.ellipse([xx - rr, yy - rr, xx + rr, yy + rr], fill=c + (255,))
    bb = im.getchannel("A").getbbox()
    x0, y0, x1, y1 = max(0, bb[0] - 4), max(0, bb[1] - 4), min(w, bb[2] + 4), min(h, bb[3] + 4)
    im = im.crop((x0, y0, x1, y1))
    return im, ((bx - x0) / (x1 - x0), (by - y0) / (y1 - y0))


@lru_cache(None)
def wisnia(v=0):
    """Kwitnąca wiśnia wycięta kodem (v jak w _drzewo_img). Atrybut .pien — kotwica nasady pnia."""
    im, anchor = _drzewo_img("wisnia", v)
    s = Sprite(im, f"wisnia-{v}", rim=2, clean=False, crop=False)
    s.pien = anchor
    return s


@lru_cache(None)
def drzewko(v=2):
    """Zielone drzewko liściaste o okrągłej koronie (wyspy, pagórki)."""
    im, anchor = _drzewo_img("zielone", v)
    s = Sprite(im, f"drzewko-{v}", rim=2, clean=False, crop=False)
    s.pien = anchor
    return s


@lru_cache(None)
def galaz_wisni():
    """Kulisa: gałąź kwitnącej wiśni zwisająca z lewego górnego rogu kadru."""
    im, anchor = _drzewo_img("wisnia", 4)
    return Sprite(im, "galaz-wisni", rim=2, clean=False, crop=False)


@lru_cache(None)
def bambus(v=0):
    """Kępa bambusa: smukłe źdźbła z kolankami, wiotkie gałązki i wąskie liście zwisające na boki."""
    w, h = 640, 1000
    r = random.Random(600 + v)
    n = 7 if v == 0 else 5
    culms, nodes, twigs = [[], [], []], [], []
    leaves = [[], [], []]

    def liscie(x, y, side, cnt, L):
        for _ in range(cnt):
            a = r.uniform(0.15, 1.15)
            ang = a if side > 0 else math.pi - a
            leaves[r.randrange(3)].append(_lisc(x + r.uniform(-6, 6), y + r.uniform(-4, 4), ang, L * r.uniform(0.75, 1.2),
                                                L * r.uniform(0.13, 0.18)))

    for i in range(n):
        x0 = 80 + (i + r.uniform(0.15, 0.85)) * (w - 160) / n
        top = r.uniform(30, 230)
        lean = r.uniform(-60, 60)
        cw = r.uniform(14, 24)
        xa = lambda f: x0 + lean * f ** 1.6
        left, right = [], []
        for k in range(15):
            f = k / 14
            y = h - f * (h - top)
            ww = cw * (1 - 0.5 * f)
            left.append((xa(f) - ww / 2, y))
            right.append((xa(f) + ww / 2, y))
        culms[i % 3].append(poly(left + right[::-1]))
        y = h - r.uniform(40, 90)
        while y > top + 40:
            f = (h - y) / (h - top)
            x, ww = xa(f), cw * (1 - 0.5 * f)
            nodes.append(poly([(x - ww / 2 - 2, y - 2), (x + ww / 2 + 2, y - 2), (x + ww / 2 + 2, y + 2.5), (x - ww / 2 - 2, y + 2.5)]))
            if f > 0.38:
                for side in (-1, 1):
                    if r.random() < 0.55:
                        L = r.uniform(40, 95)
                        tx, ty = x + side * L, y - L * r.uniform(0.15, 0.45)
                        twigs.append(_konar(x, y, tx, ty, 3.2, 1.4))
                        liscie(tx, ty, side, r.randint(3, 6), r.uniform(55, 90))
                        liscie(x + side * L * 0.5, y - L * 0.15, side, r.randint(1, 3), r.uniform(45, 75))
            y -= r.uniform(70, 105)
        xt = xa(1.0)
        for side in (-1, 1):
            liscie(xt, top + 10, side, r.randint(3, 5), r.uniform(55, 85))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for k, c in enumerate(((118, 158, 86), (96, 140, 76), (138, 170, 98))):
        im = _naklej(im, culms[k], c, 610 + k, kind="gladki", contrast=0.7, rough=0.9, shadow=0.35)
    im = _naklej(im, nodes, (64, 96, 56), 615, kind="gladki", clip=_alfa(im), shadow=0.0, rough=0.4)
    im = _naklej(im, twigs, (88, 120, 64), 616, kind="gladki", rough=0.5, shadow=0.25)
    for k, c in enumerate(((52, 94, 58), (80, 126, 70), (120, 158, 86))):
        im = _naklej(im, leaves[k], c, 620 + k, kind="gladki", rough=0.7, shadow=0.3)
    return Sprite(im, f"bambus-{v}", rim=2, clean=False)
