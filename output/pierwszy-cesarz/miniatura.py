"""Miniaturka „Pierwszego cesarza” na YouTube, złożona silnikiem teatru z tych samych wycinków co film.
Jak robimy miniaturki: docs/WYTYCZNE_UJEC.md, sekcja 5. Zatwierdzona: koncepcja 1, wersja EN w 4K + fujifilm.py.

Po lewej duży cesarz z grubym białym obrysem i spiralami na oczach, przed miastem, wskazuje w prawo; przy nim tabliczka
„NO WAY?!”; po prawej scena z ujęcia „studnia”: dwaj chłopi z narzędziami w górze, między nimi gliniany żołnierz do góry
nogami, w rozkroku jak w pajacyku, w kopcu ziemi, nad nim tabliczka „OH!”, w tle spada meteoryt; u góry szyld z tytułem
(reżyser 16.11.2026).

  python3 miniatura.py [pl|en]      → miniatura/miniatura_<język>.jpg i .png (1280 × 720)
  KONCEPCJA=2 python3 miniatura.py … → miniatura/miniatura2_<język>.jpg: plan ogólny, cała scena (KADRY niżej)
  JAKOSC=1 python3 miniatura.py …   → szybki podgląd (rysowane w 1280 × 720 zamiast w 2560 × 1440)
  ROZMIAR=3840 python3 miniatura.py en → 4K dla YouTube (3840 × 2160, do 50 MB przy wgrywaniu z komputera):
                                         miniatura_<język>_4k.png (bez strat) i _4k.jpg, a z tego samego rysunku
                                         miniatura_<język>.jpg 1280 × 720 (do 2 MB: wgrywanie z telefonu)
"""
import math
import os
import random
import sys
from pathlib import Path

JEZ = sys.argv[1] if len(sys.argv) > 1 else "pl"
os.environ["JEZYK"] = JEZ  # zestaw czyta język przy imporcie: napisy na tabliczkach w języku wersji (wytyczne 1.13)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import papier  # noqa: E402

ROZMIAR = int(os.environ.get("ROZMIAR", "0"))  # szerokość pliku wynikowego rysowanego wprost (np. 3840 = 4K)
papier.Q = ROZMIAR / 1280 if ROZMIAR else float(os.environ.get("JAKOSC", "2"))  # domyślnie rysowane w 2× i zmniejszane
import zestaw as Z  # noqa: E402
from papier import Cam, Sprite, Stage  # noqa: E402

P = Z.P
OUT = HERE / "miniatura"
TYTUL = {"pl": "PIERWSZY CESARZ", "en": "THE FIRST EMPEROR"}[JEZ]

SKORA, SKORA_C = (206, 154, 112), (168, 118, 82)
INK = (40, 26, 22)


# ---------- kamera: kadr wzorcowy powiększony, wycinki z przodu kładzione we współrzędnych ekranu ----------

def ekran_na_swiat(st, sx, sy, p):
    """Punkt ekranu (kadr 1280 × 720) → punkt kadru wzorcowego na planie p (odwzorowanie jest liniowe w każdej osi)."""
    a0, ax, ay = st.cam.screen(0, 0, p), st.cam.screen(1, 0, p), st.cam.screen(0, 1, p)
    return (sx - a0[0]) / (ax[0] - a0[0]), (sy - a0[1]) / (ay[1] - a0[1])


def poloz(st, spr, ex, ey, p, h=None, w=None, **kw):
    """Wycinek w punkcie ekranu (ex, ey), rozmiar h/w w pikselach ekranu."""
    x, y = ekran_na_swiat(st, ex, ey, p)
    g = st.cam.mag(p)
    st.put(spr, x, y, p, h=h / g if h else None, w=w / g if w else None, **kw)


def nitki(st, spr, sx, sy, p, h, xs=(0.18, 0.82), rot=0.0):
    """Wycinek zawieszony na nitkach (punkt zawieszenia: środek górnej krawędzi na ekranie)."""
    g = st.cam.mag(p)
    ww = h * spr.w / spr.h
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for fx in xs:
        dx = (fx - 0.5) * ww
        ax, ay = sx + c * dx, sy + s * dx + 4
        x0, y0 = ekran_na_swiat(st, ax, -40, p)
        x1, y1 = ekran_na_swiat(st, ax, ay, p)
        st.line([(x0, y0), (x1, y1)], p, width=1.6 / g * 1.4, color=(70, 56, 44), alpha=0.8, z=-0.5)
    poloz(st, spr, sx, sy, p, h=h, anchor=(0.5, 0.0), rot=rot, shadow=(5, 8, 8, 0.45))


# ---------- wycinki miniaturki (większe i dokładniejsze niż w filmie: w miniaturce są duże) ----------
# Wycinki rysowane kodem powstają w skali k (k = 1 przy rysowaniu w 2560 × 1440): w 4K papier, litery i kreski tuszu są
# rysowane w pełnej rozdzielczości, a nie powiększane. Obrazy z plików (cesarz, brama) powiększa Lanczos przed sceną.

K_TAB = papier.Q  # tabliczki i szyld: w 4K trzykrotnie
K_POST = max(1.0, papier.Q / 2)  # chłopi, kopiec, grudy
K_ZOL = max(1.0, papier.Q * 0.67)  # gliniany żołnierz (mały arkusz w filmie)


def stack_k(w, h, parts, seed=0, k=1.0):
    """Z.stack w skali k: ten sam rysunek (kształty, poszarpane brzegi, cienie pod kawałkami), k razy większy."""
    W_, H_ = round(w * k), round(h * k)
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    for i, part in enumerate(parts):
        shape, color = part[0], part[1]
        opt = dict(part[2]) if len(part) > 2 else {}
        opt["edge"] = round(opt.get("edge", 0) * k)
        opt["rough"] = opt.get("rough", 1.3) * k
        im = Z.glue(im, Z.piece(W_, H_, lambda d, s, f=shape: f(d, s * k), color, seed=seed + i * 7, **opt),
                    off=(round(2 * k), round(3 * k)), soft=2.5 * k)
    return im


def wycinek_hd(name, f, dorysuj=None):
    """Wycinek z pliku powiększony Lanczosem (ostrzej niż dwuliniowe powiększenie w silniku); alfa wymnożona przy skalowaniu.
    dorysuj(obraz, f) — dorysowanie na powiększonym obrazie (np. spirale na oczach)."""
    im = Z.raw(name)
    if f > 1.0:
        im = im.convert("RGBa").resize((round(im.size[0] * f), round(im.size[1] * f)), Image.LANCZOS).convert("RGBA")
    if dorysuj:
        im = dorysuj(im.copy(), f)
    return Sprite(im, f"{name}-x{f:.2f}", rim=max(2, round(2 * f)))


# oczy cesarza na wycinku emperor.png (piksele pliku): spirala — środek, promienie, grubość kreski, liczba zwojów;
# oko — elipsa zakryta kolorem skóry pod spiralą; skóra — skąd wziąć kolor (policzek pod okiem). Dalsze oko węższe (trzy
# czwarte). Reżyser 16.11: „te spirale większe”, „grubsze i bez tego białego tła pod”, „grubsze i minimalnie większe jeszcze”.
OCZY_CESARZA = (
    dict(spirala=(460, 208, 23, 20), kreska=4.0, zwoje=2.4, oko=(462, 208, 13, 7), skora=(452, 222, 472, 232)),
    dict(spirala=(495, 210, 13, 18.5), kreska=3.0, zwoje=2.0, oko=(492, 211, 7, 6), skora=(488, 222, 496, 230)),
)


def spirale(im, f, oczy=OCZY_CESARZA):
    """Czarne spirale wprost na twarzy, jak w kreskówce: najpierw oko zakryte kolorem skóry z policzka (miękka krawędź,
    brwi zostają), potem gruba spirala rysowana w 4× nadpróbkowaniu i nakładana na powiększony wycinek."""
    ss = 4
    src = np.asarray(Z.raw("emperor").convert("RGB"), np.float32)
    for e in oczy:
        sx0, sy0, sx1, sy1 = e["skora"]
        kolor = tuple(int(c) for c in np.median(src[sy0:sy1, sx0:sx1].reshape(-1, 3), axis=0))
        ox, oy, orx, ory = e["oko"]
        m = 3  # zapas wokół oka na miękką krawędź (piksele pliku)
        bx0, by0 = round((ox - orx - m) * f), round((oy - ory - m) * f)
        bx1, by1 = round((ox + orx + m) * f), round((oy + ory + m) * f)
        maska = Image.new("L", (bx1 - bx0, by1 - by0), 0)
        ImageDraw.Draw(maska).ellipse([(ox - orx) * f - bx0, (oy - ory) * f - by0, (ox + orx) * f - bx0, (oy + ory) * f - by0], fill=255)
        maska = maska.filter(ImageFilter.GaussianBlur(1.2 * f))
        im.paste(kolor + (255,), (bx0, by0, bx1, by1), maska)

        cx, cy, rx, ry = e["spirala"]
        m = 4
        x0, y0 = round((cx - rx - m) * f), round((cy - ry - m) * f)
        x1, y1 = round((cx + rx + m) * f), round((cy + ry + m) * f)
        warstwa = Image.new("RGBA", ((x1 - x0) * ss, (y1 - y0) * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(warstwa)
        X = lambda x: (x * f - x0) * ss
        Y = lambda y: (y * f - y0) * ss
        pts = []
        for i in range(0, 481):
            t = i / 480
            th = t * e["zwoje"] * 2 * math.pi
            r = 0.06 + 0.86 * t
            pts.append((X(cx + r * rx * math.cos(th)), Y(cy + r * ry * math.sin(th))))
        szer = max(1, round(e["kreska"] * f * ss))
        d.line(pts, fill=(22, 15, 13, 255), width=szer, joint="curve")
        for kx, ky in (pts[0], pts[-1]):  # zaokrąglone końce kreski
            d.ellipse([kx - szer / 2, ky - szer / 2, kx + szer / 2, ky + szer / 2], fill=(22, 15, 13, 255))
        im.alpha_composite(warstwa.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    return im


def tabliczka(txt, size=64, k=1.0):
    """Z.tag w skali k (papierowa zawieszka z napisem w języku wersji)."""
    txt = Z.tr(txt)
    f = ImageFont.truetype(Z.FONT_PL, size * 2, index=Z.PL_IDX)
    tw = int(f.getlength(txt) / 2)
    w, h = tw + 64, size + 44
    parts = [(Z.poly([(4, 4), (w - 4, 4), (w - 4, h - 4), (4, h - 4)]), (240, 226, 194), dict(kind="gladki", edge=4, contrast=1.3)),
             (Z.glyphs(txt, size, Z.FONT_PL, Z.PL_IDX, (w / 2, h / 2 + 2), "mm"), (48, 30, 24), dict(kind="gladki", rough=0.5))]
    return Sprite(stack_k(w, h, parts, seed=len(txt), k=k), f"zawieszka-{txt}-{k:.2f}", rim=round(2 * k), clean=False)


def grudka(k=1.0):
    parts = [(Z.poly([(4, 18), (14, 4), (32, 6), (38, 22), (24, 32), (8, 30)]), (112, 86, 58), dict(edge=1))]
    return Sprite(stack_k(40, 34, parts, seed=sum(map(ord, "grudka")), k=k), "grudka-k", rim=round(2 * k), clean=False)


def zolnierz(v=0, k=1.0, rozkrok=0.0):
    """zestaw.soldier w skali k — ten sam gliniany żołnierz co w filmie, narysowany w rozdzielczości miniaturki
    (kopia rysunku: zestaw.py zostaje nietknięty, bo jego zmiana kazałaby rysować od nowa wszystkie klipy filmu).
    rozkrok — nogi rozłożone na boki o tyle stopni (każda wokół swojego biodra), jak w pajacyku (reżyser 16.11)."""
    r = random.Random(100 + v)
    kk = 0.92 + 0.16 * r.random()
    base, dark, light, deep = [tuple(int(c * kk) for c in col) for col in Z.CLAY]
    MX = 80 if rozkrok else 0  # zapas po bokach arkusza na rozstawione stopy
    w, h = 300 + 2 * MX, 660
    side = 1 if v % 2 == 0 else -1
    X = lambda x: MX + 150 + (x - 150) * side
    P_ = lambda pts: Z.poly([(X(x), y) for x, y in pts])
    ell = Z.ell  # środki elips podawane przez X(): zapas już w nich jest

    def obroc(pts, piv, a):  # noga obraca się wokół biodra; a > 0 — stopa w lewo
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        return [(piv[0] + (x - piv[0]) * c - (y - piv[1]) * s_, piv[1] + (x - piv[0]) * s_ + (y - piv[1]) * c) for x, y in pts]
    lew, praw = (126, 432), (174, 432)
    parts = [
        (P_(obroc([(106, 420), (147, 420), (146, 618), (102, 618)], lew, rozkrok)), dark),
        (P_(obroc([(153, 420), (194, 420), (198, 618), (154, 618)], praw, -rozkrok)), dark),
        (P_(obroc([(92, 610), (148, 610), (150, 646), (88, 646)], lew, rozkrok)), deep),
        (P_(obroc([(152, 610), (208, 610), (212, 646), (150, 646)], praw, -rozkrok)), deep),
        (P_([(90, 300), (210, 300), (226, 476), (74, 476)]), dark),
        (P_([(66, 182), (106, 172), (102, 330), (88, 398), (58, 394), (54, 300)]), dark),
        (P_([(234, 182), (194, 172), (198, 330), (212, 398), (242, 394), (246, 300)]), dark),
        (ell(X(72), 408, 16, 18), light), (ell(X(228), 408, 16, 18), light),
        (P_([(94, 166), (206, 166), (218, 380), (82, 380)]), base, dict(edge=2)),
        (P_([(62, 176), (108, 168), (112, 236), (70, 246)]), dark, dict(edge=2)),
        (P_([(238, 176), (192, 168), (188, 236), (230, 246)]), dark, dict(edge=2)),
        (P_([(134, 132), (166, 132), (170, 172), (130, 172)]), light),
        (ell(X(150), 170, 44, 17), light, dict(edge=2)),
        (ell(X(150), 102, 41, 52), light, dict(edge=2)),
        (P_([(108, 96), (112, 62), (136, 46), (168, 46), (190, 64), (192, 96), (172, 74), (128, 74)]), deep),
        (ell(X(176), 38, 23, 19), deep, dict(edge=2)),
    ]
    im = stack_k(w, h, parts, seed=200 + v, k=k)
    d = ImageDraw.Draw(im)
    q = lambda pts: [((x + MX) * k, y * k) for x, y in pts]
    W = lambda n: max(1, round(n * k))
    ink = deep + (230,)
    for yy in (214, 254, 294, 334):  # płytki pancerza
        d.line(q([(92 - (yy - 166) * 0.05, yy), (208 + (yy - 166) * 0.05, yy)]), fill=ink, width=W(3))
    for xx in (122, 150, 178):
        d.line(q([(xx, 176), (xx + (xx - 150) * 0.06, 376)]), fill=ink, width=W(2))
    for xx in (108, 136, 164, 192):
        for yy in (234, 274, 314, 354):
            d.ellipse(q([(xx - 3, yy - 3), (xx + 3, yy + 3)]), fill=ink)
    d.line(q([(123, 91), (144, 92)]), fill=ink, width=W(4))
    d.line(q([(156, 92), (177, 91)]), fill=ink, width=W(4))
    for ex in (134, 166):
        d.ellipse(q([(ex - 8, 99), (ex + 8, 109)]), fill=light + (255,), outline=ink, width=W(2))
        d.ellipse(q([(ex - 3, 101), (ex + 3, 107)]), fill=ink)
    d.line(q([(150, 100), (148, 122), (155, 123)]), fill=ink, width=W(3))
    d.line(q([(131, 134), (146, 129), (154, 129), (169, 134)]), fill=ink, width=W(4))
    d.line(q([(141, 143), (159, 143)]), fill=ink, width=W(2))
    return Sprite(im, f"zolnierz-{v}-{k:.2f}-{rozkrok:g}", rim=round(2 * k), clean=False)


def pas(a, b, wa, wb):
    """Kończyna: czworokąt od punktu a do b, szerokość wa przy a i wb przy b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n, dx / n
    return Z.poly([(a[0] + nx * wa / 2, a[1] + ny * wa / 2), (b[0] + nx * wb / 2, b[1] + ny * wb / 2),
                   (b[0] - nx * wb / 2, b[1] - ny * wb / 2), (a[0] - nx * wa / 2, a[1] - ny * wa / 2)])


def wzdluz(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def lokalnie(o, u, pts):
    """Punkty (wzdłuż trzonka, w poprzek) w układzie narzędzia: początek o, oś u (wektor jednostkowy)."""
    nx, ny = -u[1], u[0]
    return [(o[0] + u[0] * a + nx * b, o[1] + u[1] * a + ny * b) for a, b in pts]


def chlop(v, k=1.0):
    """Chłop z narzędziem uniesionym nad głowę, zaskoczony (oczy szeroko, usta „o”). Rysowany twarzą w prawo.
    Oba narzędzia są uniesione w przód, ku żołnierzowi między chłopami.
    v = 0: motyka, niebieska kurta, stożkowy kapelusz; v = 1: łopata, szarozielona kurta, płaski kapelusz,
    krótka broda — inna sylwetka, nie odbicie pierwszego (wytyczne 1.6)."""
    w, h = 760, 1320
    if v == 0:
        kurta, rekaw, spodnie, kap = (78, 104, 134), (62, 84, 110), (64, 50, 40), (204, 176, 112)
        B, T = (300, 380), (520, 46)  # trzonek: koniec przy dłoniach i koniec z ostrzem (motyka uniesiona w przód)
        bark_l, bark_p, lok_l, lok_p = (300, 604), (432, 604), (282, 430), (476, 446)
        glowa, szer = (366, 494), 1.0
    else:
        kurta, rekaw, spodnie, kap = (112, 122, 104), (92, 102, 86), (78, 60, 46), (190, 160, 100)
        B, T = (300, 380), (470, 176)  # ostrze łopaty mieści się w arkuszu wycinka
        bark_l, bark_p, lok_l, lok_p = (292, 612), (440, 612), (262, 452), (470, 430)
        glowa, szer = (368, 500), 1.12
    u = ((T[0] - B[0]), (T[1] - B[1]))
    n_ = math.hypot(*u)
    u = (u[0] / n_, u[1] / n_)
    d1, d2 = wzdluz(B, T, 0.16), wzdluz(B, T, 0.40)  # dłonie na trzonku (dolna — ręka bliższa, górna — dalsza)
    gx, gy = glowa
    parts = []
    # ręka dalsza (za głową i kapeluszem)
    parts += [(pas(bark_l, lok_l, 58, 50), rekaw), (pas(lok_l, d2, 40, 34), SKORA_C)]
    # narzędzie
    parts += [(pas(B, T, 16, 15), (132, 96, 58), dict(kind="gladki", contrast=1.1))]
    if v == 0:  # motyka: żelazne ostrze w poprzek trzonka, ostrzem w przód (w prawo)
        parts += [(Z.poly(lokalnie(T, u, [(14, -8), (-26, -8), (-30, 12), (10, 14)])), (70, 70, 76), dict(contrast=1.3)),
                  (Z.poly(lokalnie(T, u, [(8, 10), (-24, 10), (-34, 128), (-6, 134), (14, 70)])), (92, 94, 100), dict(contrast=1.3, edge=2))]
    else:  # łopata: szerokie ostrze na końcu trzonka
        parts += [(Z.poly(lokalnie(T, u, [(-14, -12), (6, -12), (6, 12), (-14, 12)])), (70, 70, 76), dict(contrast=1.3)),
                  (Z.poly(lokalnie(T, u, [(0, -40), (110, -44), (138, -20), (146, 0), (138, 20), (110, 44), (0, 40)])), (98, 98, 104),
                   dict(contrast=1.3, edge=2))]
    # nogi, kurta, pas
    nogi = [(gx - 70 * szer, 1000), (gx - 18 * szer, 1000), (gx + 12 * szer, 1000), (gx + 66 * szer, 1000)]
    parts += [(Z.poly([nogi[0], nogi[1], (gx - 22 * szer, 1214), (gx - 70 * szer, 1214)]), spodnie),
              (Z.poly([nogi[2], nogi[3], (gx + 80 * szer, 1208), (gx + 30 * szer, 1214)]), spodnie),
              (Z.poly([(gx - 66 * szer, 1206), (gx - 26 * szer, 1206), (gx - 28 * szer, 1282), (gx - 64 * szer, 1282)]), SKORA_C),
              (Z.poly([(gx + 34 * szer, 1204), (gx + 76 * szer, 1202), (gx + 80 * szer, 1278), (gx + 40 * szer, 1282)]), SKORA_C),
              (Z.ell(gx - 44 * szer, 1294, 44, 16), (110, 84, 56)), (Z.ell(gx + 66 * szer, 1290, 44, 16), (110, 84, 56)),
              (Z.poly([(gx - 82 * szer, 578), (gx + 72 * szer, 578), (gx + 112 * szer, 1018), (gx - 116 * szer, 1018)]), kurta, dict(edge=2)),
              (Z.poly([(gx - 98 * szer, 790), (gx + 92 * szer, 790), (gx + 95 * szer, 818), (gx - 100 * szer, 818)]), (180, 150, 96)),
              (Z.poly([(gx - 30, 576), (gx + 30, 576), (gx + 2, 640)]), SKORA),
              (Z.poly([(gx - 22, 520), (gx + 22, 520), (gx + 22, 586), (gx - 22, 586)]), SKORA_C)]
    if v == 0:  # łata na kurcie
        parts += [(Z.poly([(gx + 30, 880), (gx + 82, 876), (gx + 86, 930), (gx + 34, 934)]), (96, 122, 150))]
    # głowa: ucho, twarz
    parts += [(Z.ell(gx - 30, gy + 6, 11, 15), SKORA_C), (Z.ell(gx, gy, 48, 56), SKORA, dict(edge=2))]
    if v == 0:  # stożkowy kapelusz ze słomy
        parts += [(Z.poly([(gx - 140, gy - 40), (gx + 132, gy - 40), (gx + 120, gy - 28), (gx - 128, gy - 28)]), (150, 122, 76)),
                  (Z.poly([(gx - 144, gy - 42), (gx + 136, gy - 42), (gx - 2, gy - 126)]), kap, dict(edge=2))]
    else:  # płaski kapelusz
        parts += [(Z.poly([(gx - 150, gy - 44), (gx + 150, gy - 50), (gx + 120, gy - 64), (gx + 30, gy - 92), (gx - 40, gy - 92),
                           (gx - 124, gy - 60)]), kap, dict(edge=2))]
    # ręka bliższa (przed tułowiem), dłonie na trzonku
    parts += [(pas(bark_p, lok_p, 62, 52), rekaw), (pas(lok_p, d1, 42, 36), SKORA),
              (Z.ell(d1[0], d1[1], 25, 21), SKORA), (Z.ell(d2[0], d2[1], 23, 20), SKORA_C)]
    im = stack_k(w, h, parts, seed=600 + 40 * v, k=k)
    d = ImageDraw.Draw(im)
    q = lambda pts: [(x * k, y * k) for x, y in pts]
    W = lambda n: max(1, round(n * k))
    # twarz: oczy szeroko otwarte, brwi wysoko, usta „o”
    for ex in (gx + 10, gx + 34):
        d.ellipse(q([(ex - 10, gy - 6), (ex + 10, gy + 10)]), fill=(244, 236, 220, 255), outline=INK + (255,), width=W(3))
        d.ellipse(q([(ex - 1, gy - 2), (ex + 7, gy + 6)]), fill=INK + (255,))
    d.arc(q([(gx - 2, gy - 34), (gx + 22, gy - 12)]), 200, 330, fill=INK + (255,), width=W(4))
    d.arc(q([(gx + 24, gy - 36), (gx + 46, gy - 14)]), 210, 340, fill=INK + (255,), width=W(4))
    d.line(q([(gx + 40, gy + 6), (gx + 48, gy + 24), (gx + 38, gy + 26)]), fill=SKORA_C + (255,), width=W(4))
    d.ellipse(q([(gx + 18, gy + 30), (gx + 38, gy + 54)]), fill=(78, 30, 26, 255), outline=INK + (255,), width=W(2))
    if v == 1:  # krótka broda
        d.polygon(q([(gx - 10, gy + 50), (gx + 36, gy + 56), (gx + 20, gy + 70), (gx, gy + 66)]), fill=(52, 38, 30, 255))
    # palce na trzonku: kreski
    for (hx, hy), r in ((d1, 25), (d2, 23)):
        for dx in (-8, 0, 8):
            d.line(q([(hx + dx - 6, hy - r * 0.55), (hx + dx + 6, hy + r * 0.55)]), fill=SKORA_C + (200,), width=W(2))
    return Sprite(im, f"chlop-miniatura-{v}-{k:.2f}", rim=round(3 * k), clean=False)


def kopczyk(k=1.0):
    """Kopiec świeżej ziemi z dołkiem, w który wbił się żołnierz."""
    w, h = 900, 300
    r = random.Random(7)
    top = [(0, 300)] + [(x, 300 - 230 * math.sin(math.pi * x / 900) ** 0.7 + r.uniform(-14, 14)) for x in range(30, 900, 45)] + [(900, 300)]
    parts = [(Z.poly(top), (112, 84, 58), dict(edge=2, contrast=1.1)),
             (Z.ell(450, 92, 120, 30), (66, 46, 32))]
    for _ in range(22):  # grudy na zboczu (nie „k”: k to skala rysunku)
        x = r.uniform(80, 820)
        y = 300 - 210 * math.sin(math.pi * x / 900) ** 0.7 + r.uniform(10, 120)
        parts.append((Z.ell(x, y, r.uniform(14, 30), r.uniform(10, 20)), r.choice(((128, 98, 66), (96, 72, 50), (140, 108, 72)))))
    return Sprite(stack_k(w, h, parts, seed=77, k=k), f"kopczyk-{k:.2f}", rim=round(3 * k), clean=False)


def kamien_meteor():
    """Rozżarzony kamień: ciemna bryła z pomarańczowymi pęknięciami."""
    w, h = 420, 380
    parts = [(Z.poly([(40, 140), (150, 40), (300, 50), (396, 170), (360, 300), (230, 360), (90, 330), (24, 240)]), (58, 46, 44),
              dict(edge=3, contrast=1.5)),
             (Z.poly([(110, 120), (200, 76), (270, 120), (210, 170)]), (86, 70, 62)),
             (Z.ell(290, 250, 46, 34), (44, 36, 36)), (Z.ell(140, 260, 34, 24), (48, 40, 38))]
    im = Z.stack(w, h, parts, seed=91)
    d = ImageDraw.Draw(im)
    for pts in (((120, 180), (180, 210), (230, 196), (290, 236)), ((210, 110), (226, 160), (214, 214)), ((300, 130), (330, 190), (350, 230))):
        d.line(pts, fill=(250, 150, 60, 235), width=7, joint="curve")
        d.line(pts, fill=(255, 220, 140, 255), width=3, joint="curve")
    return Sprite(im, "meteor-kamien", rim=3, clean=False)


def lezka(R, L, kolor, seed, fale=5, amp=0.16):
    """Łezka ognia z bibuły leżąca wzdłuż osi x: okrągła głowa o promieniu R w (1,15 R, środek), ogon długości L
    w prawo, brzegi falują jak płomień. Zwraca (wycinek, kotwica środka głowy)."""
    w, h = int(L + 2.4 * R), int(2.8 * R)
    cx, cy = 1.15 * R, h / 2
    pts = []
    for k in range(0, 41):  # głowa: półkole od góry przez lewo do dołu
        th = math.pi / 2 + math.pi * k / 40
        pts.append((cx + R * math.cos(th), cy - R * math.sin(th)))
    for k in range(1, 61):  # dolny brzeg ogona do czubka
        f = k / 60
        r_ = R * (1 - f) ** 1.15 * (1 + amp * math.sin(f * math.pi * fale + seed) * (1 - f))
        pts.append((cx + L * f, cy + r_ + 0.12 * R * math.sin(f * math.pi * 2)))
    for k in range(59, 0, -1):  # górny brzeg z powrotem
        f = k / 60
        r_ = R * (1 - f) ** 1.15 * (1 + amp * math.sin(f * math.pi * fale + seed + 1.7) * (1 - f))
        pts.append((cx + L * f, cy - r_ + 0.12 * R * math.sin(f * math.pi * 2)))
    im = Z.piece(w, h, Z.poly(pts), kolor, "gnieciony", edge=0, seed=seed, rough=1.6, contrast=0.7)
    return Sprite(im, f"lezka-{seed}", rim=2, clean=False, crop=False), (cx / w, cy / h)


def szyld(txt, size=78, k=1.0):
    """Szyld z tytułem: czarna deska w złotej ramce, złote litery (jak szyld na gzymsie teatru)."""
    f = ImageFont.truetype(Z.FONT_PL, size * 2, index=Z.PL_IDX)
    tw = f.getlength(txt) / 2
    w, h = int(tw + 110), size + 70
    gold = (220, 178, 96)
    R = lambda x0, y0, x1, y1: Z.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    parts = [(R(4, 4, w - 4, h - 4), (30, 22, 20), dict(kind="gladki", contrast=1.5)),
             (R(4, 4, w - 4, 14), gold), (R(4, h - 14, w - 4, h - 4), gold), (R(4, 4, 14, h - 4), gold), (R(w - 14, 4, w - 4, h - 4), gold),
             (R(22, 22, w - 22, 26), (150, 116, 60)), (R(22, h - 26, w - 22, h - 22), (150, 116, 60)),
             (Z.glyphs(txt, size, Z.FONT_PL, Z.PL_IDX, (w / 2, h / 2 + 3), "mm"), (232, 192, 108), dict(kind="gladki", rough=0.5, contrast=1.2))]
    return Sprite(stack_k(w, h, parts, seed=13, k=k), f"szyld-miniatura-{k:.2f}", rim=round(3 * k), clean=False)


def z_obrysem(spr, r=7, kolor=(236, 224, 196), k=1.0):
    """Wycinek naklejony na jasny karton wycięty kilka pikseli szerzej (obrys): postać odcina się od tła w małej
    miniaturce. Zwraca (wycinek, przelicz), gdzie przelicz(anchor, h) daje kotwicę i wysokość nowego wycinka."""
    pm = np.asarray(spr.mips[0], np.float32) / 255.0
    al = pm[..., 3:4]
    rgb = np.where(al > 1e-3, pm[..., :3] / np.maximum(al, 1e-3), 0)
    src = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), al]) * 255 + 0.5).astype(np.uint8))
    W_, H_ = src.size
    big = Image.new("RGBA", (W_ + 2 * r, H_ + 2 * r), (0, 0, 0, 0))
    big.paste(src, (r, r))
    m = big.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    for _ in range(r // 2):  # rozrost maski o r pikseli: kroki po 2 px (jeden duży filtr przy grubym obrysie liczy się bardzo długo)
        m = m.filter(ImageFilter.MaxFilter(5))
    if r % 2:
        m = m.filter(ImageFilter.MaxFilter(3))
    m = m.filter(ImageFilter.GaussianBlur(1.0 * k))
    karton = Z.paper(m, kolor, "gladki", 31, contrast=1.2)
    out = Z.glue(karton, big, shadow=0.35, off=(round(k), round(2 * k)), soft=1.5 * k)
    przelicz = lambda anchor, h: (((anchor[0] * W_ + r) / (W_ + 2 * r), (anchor[1] * H_ + r) / (H_ + 2 * r)), h * (H_ + 2 * r) / H_)
    return Sprite(out, spr.name + "-obrys", rim=2, clean=False, crop=False), przelicz


def poloz_obrys(st, spr, ex, ey, p, h, anchor, r=7, kolor=(236, 224, 196), gruby=None, k=1.0, **kw):
    """r — grubość obrysu w pikselach wycinka narysowanego w skali 1 (w skali k: r·k); gruby — w pikselach ekranu."""
    r = max(1, round(gruby * spr.h / h)) if gruby else max(1, round(r * k))
    o, przelicz = z_obrysem(spr, r, kolor, k=max(1.0, k))
    a, hh = przelicz(anchor, h)
    poloz(st, o, ex, ey, p, h=hh, anchor=a, **kw)


# ---------- scena ----------

def scena(K):
    st = Stage(0.0, seed=4)
    st.T = 1.0
    cx, cy, m = K["kamera"]
    st.cam = Cam(cx, cy, m, 0.5, lens=m, truck=0.0)  # sam obiektyw: kadr wzorcowy powiększony m razy (bez paralaksy)
    st.focus, st.dof = P.lalki, 0.5  # ostrość na lalkach: cesarz, chłopi, tabliczki i szyld najostrzejsze
    p_l = P.lalki
    # tło jak w filmie: niebo, góry, wzgórza; zmierzch (ciemne niebo), bez słońca — na niebie jest meteoryt
    Z.plan(st, 0.0, sun=0.0, clouds=(0.0, 0.0, 0.0), trees=(0.0, K["sosna"]), city=0.0, bridge=0.0, night=NOC, floor=1.0)
    for i, (name, x, y, w) in enumerate((("cloud_left", 250, 64, 560), ("cloud_center", 700, 28, 620), ("cloud_right", 1080, 150, 500))):
        Z.hang(st, Z.S(name), x, y, P.chmury + i * 0.008, 1.0, 0.0, 4 + i, w=w, sway=0.5, strings=(0.3, 0.7),
               shadow=(7, 10, 11, 0.26), haze=0.04, tint=CHMURY)  # o zmierzchu chmury szarzeją razem z niebem
    # miasto za cesarzem: brama z wieżami, większa niż w kadrze wzorcowym, żeby wystawała nad ręką cesarza
    mia = K["miasto"]
    brama = wycinek_hd("city_gate", max(1.0, papier.Q * mia[2] / 1671 * K["kamera"][2] / 1.32))
    poloz(st, brama, mia[0], mia[1], P.miasto, w=mia[2], anchor=(0.5, 1.0), haze=0.05)

    # meteoryt w tle: kamień z ognistym ogonem (ogon w górę i w prawo, kamień leci w dół i w lewo)
    p_m = P.gory - 0.012
    mx, my, kat, dl, mh = K["meteor"]
    ux, uy = math.cos(math.radians(kat)), -math.sin(math.radians(kat))  # kierunek ogona na ekranie
    R = mh * 0.78
    poloz(st, Z.glow(), mx + ux * dl * 0.25, my + uy * dl * 0.25, p_m - 0.004, w=dl * 2.4, anchor=(0.5, 0.5), mode="add", alpha=0.40,
          shadow=None, tint=(1.0, 0.55, 0.25))
    for n, (kolor, kr, kl) in enumerate((((190, 46, 30), 1.0, 1.0), ((226, 98, 36), 0.80, 0.80), ((246, 166, 58), 0.62, 0.58),
                                         ((252, 222, 136), 0.46, 0.36))):
        spr, kot = lezka(R * kr * papier.Q, dl * kl * papier.Q, kolor, 11 + n)  # w rozdzielczości klatki: ostra bibuła
        poloz(st, spr, mx, my, p_m + 0.0005 * n, h=spr.h / papier.Q, anchor=kot, rot=-kat, shadow=None)
    poloz(st, kamien_meteor(), mx, my, p_m + 0.004, h=mh, anchor=(0.5, 0.5), rot=-20, shadow=None)
    poloz(st, Z.glow(), mx, my, p_m + 0.005, w=mh * 3.4, anchor=(0.5, 0.5), mode="add", alpha=0.45, shadow=None, tint=(1.0, 0.75, 0.4))

    # chłopi i żołnierz do góry nogami w kopcu ziemi
    (ax, ah, ad), (bx, bh, bd) = K["chlopi"]
    poloz_obrys(st, chlop(0, K_POST), ax, ad, p_l, ah, (0.5, 1.0), k=K_POST, rot=-3)
    poloz_obrys(st, chlop(1, K_POST), bx, bd, p_l + 0.002, bh, (0.5, 1.0), k=K_POST, sx=-1, rot=4)
    zx, zy, zh = K["zolnierz"]
    f = zh / 410  # grudy i kopiec w skali żołnierza
    poloz_obrys(st, zolnierz(2, K_ZOL, K.get("rozkrok", 0.0)), zx, zy, p_l - 0.004, zh, (0.5, 0.07), k=K_ZOL,
                rot=180 + K.get("zolnierz_kat", ZOLNIERZ_KAT), tint=(1.22, 1.02, 0.86))
    poloz(st, kopczyk(K_POST), zx - 4 * f, zy + 72 * f, p_l + 0.004, w=zh * 0.9, anchor=(0.5, 1.0))
    r = random.Random(3)
    for dx, dy, hh in GRUDY:  # grudy w powietrzu po bokach kopca — nie na żołnierzu ani na kurtach chłopów
        poloz(st, grudka(K_POST), zx + dx * f, zy + dy * f, p_l + 0.005, h=hh * f ** 0.5, anchor=(0.5, 0.5), rot=r.uniform(0, 360),
              shadow=(2, 3, 3, 0.35))
    # tabliczka „O!” nad żołnierzem
    ox, oy, oh = K["o_tab"]
    nitki(st, tabliczka("O!", 64, K_TAB), ox, oy, P.rekwizyty + 0.02, h=oh, xs=(0.5,), rot=-4)

    # cesarz po lewej, wskazuje palcem na wykopanego żołnierza; gruby biały obrys (reżyser 16.11: „zrób gruby biały obrys
    # cesarza”) i tabliczka z okrzykiem — w wersji EN „NO WAY?!” (kwestie_en.ETYKIETY)
    ex, ey, eh = K["cesarz"]
    fc = max(1.0, round(papier.Q * eh / 1493 * 4) / 4)  # w 4K: 2,5× — tyle pikseli, ile cesarz ma na ekranie
    poloz_obrys(st, wycinek_hd("emperor", fc, spirale if K.get("spirale") else None), ex, ey, p_l + 0.01, eh, (0.42, 1.0), kolor=(252, 250, 244), gruby=K["cesarz_obrys"], k=fc,
                rot=-1.5)
    tx, ty, th = K["cesarz_tab"]
    tab = tabliczka("NIEMOŻLIWE?!", 64, K_TAB)
    if K.get("cesarz_tab_od_lewej"):  # lewy brzeg tuż za koroną: dłuższy napis (PL) rośnie w prawo, nie na koronę
        tx += 0.5 * th * tab.w / tab.h
    nitki(st, tab, tx, ty, P.rekwizyty + 0.03, h=th, xs=(0.2, 0.8), rot=K.get("cesarz_tab_kat", 2.5))

    # szyld z tytułem na nitkach u góry
    sz = szyld(TYTUL, k=K_TAB)
    lx, gy, hs, maxw = K["szyld"]
    hs = min(hs, maxw * sz.h / sz.w)  # dłuższy tytuł (EN): szyld niższy, żeby zmieścił się w swoim miejscu
    nitki(st, sz, lx + 0.5 * hs * sz.w / sz.h if K.get("szyld_od_lewej", True) else lx, gy, 0.95, h=hs, xs=(0.1, 0.9), rot=-0.8)

    st.grade = (1.0, 0.98, 0.97)
    return st


NOC = 0.92  # niebo o zmierzchu (granat)
CHMURY = (0.66, 0.68, 0.82)
ZOLNIERZ_KAT = 14  # przechył: nogi w górze odchylone w prawo
GRUDY = ((-112, -52, 20), (-84, -96, 16), (-128, -10, 22), (-70, -140, 14), (96, -30, 18), (112, -74, 15), (84, 8, 22))  # przesunięcie od głowy żołnierza, wysokość

# Układ kadru w pikselach ekranu (1280 × 720). Dwie koncepcje (reżyser 16.11.2026):
#   1 — zbliżenie: duży cesarz do pasa, grupa przy rampie;
#   2 — plan ogólny („oddal to wszystko”): cała scena teatru, cesarz w całej postaci, chłopi i żołnierz w całości nad rampą.
KADRY = {
    1: dict(
        kamera=(640, 420, 1.32),  # punkt kadru wzorcowego w środku ekranu, powiększenie
        sosna=1.0,
        miasto=(500, 610, 860),  # brama miasta: x środka, dół, szerokość
        meteor=(826, 186, 36, 330, 70),  # kamień: x, y; kąt ogona nad poziomem; długość ogona; wielkość kamienia
        chlopi=((816, 590, 918), (1150, 620, 850)),  # x, wysokość wycinka (z narzędziem), dół wycinka
        zolnierz=(972, 654, 410),  # czubek głowy w kopcu: x, y; wysokość
        o_tab=(1000, 86, 104),  # tabliczka: x, góra, wysokość
        cesarz=(262, 1338, 1200),  # x, dół, wysokość
        cesarz_obrys=9,  # grubość białego obrysu (piksele ekranu)
        spirale=True,  # spirale na oczach cesarza
        rozkrok=28,  # nogi żołnierza rozłożone jak w pajacyku (stopnie od pionu, każda noga)
        zolnierz_kat=8,  # przy rozkroku mniejszy przechył: prawa stopa nie wchodzi w ręce chłopa z łopatą
        cesarz_tab=(340, 170, 74),  # tabliczka cesarza: lewy brzeg, góra, wysokość (nad głową jest szyld, więc obok głowy)
        cesarz_tab_od_lewej=True,
        cesarz_tab_kat=-7,  # reżyser 16.11: „przekrzyw lekko i minimalnie niżej” — prawy koniec w górę
        szyld=(40, 12, 122, 700),  # szyld: lewy brzeg, góra, wysokość, największa szerokość
    ),
    2: dict(
        kamera=(640, 372, 1.0),
        sosna=1.0,
        miasto=(560, 588, 640),
        meteor=(1118, 162, 34, 330, 66),
        chlopi=((728, 460, 716), (1070, 480, 708)),
        zolnierz=(898, 642, 326),
        o_tab=(900, 176, 98),
        cesarz=(232, 772, 640),
        cesarz_obrys=7,
        cesarz_tab=(196, 40, 62),  # nad głową cesarza: x środka, góra, wysokość
        szyld=(708, 14, 112, 700),
        szyld_od_lewej=False,  # szyld na środku u góry
    ),
}
KONCEPCJA = int(os.environ.get("KONCEPCJA", "1"))


def wyrownaj(img, ostrosc):
    """Kolor i kontrast jak w zatwierdzonej miniaturce, potem wyostrzenie (promień w pikselach tego obrazu)."""
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    return img.filter(ImageFilter.UnsharpMask(radius=ostrosc, percent=60, threshold=2))


def main():
    OUT.mkdir(exist_ok=True)
    img = scena(KADRY[KONCEPCJA]).render()
    nazwa = f"miniatura_{JEZ}" if KONCEPCJA == 1 else f"miniatura{KONCEPCJA}_{JEZ}"
    if ROZMIAR:  # duży plik wprost z rysunku, a 1280 × 720 zmniejszone z niego (przed wyostrzeniem)
        duzy = wyrownaj(img, 1.2 * papier.Q * 0.7)
        png, jpg = OUT / f"{nazwa}_{ROZMIAR // 960}k.png", OUT / f"{nazwa}_{ROZMIAR // 960}k.jpg"
        duzy.save(png, optimize=True)
        duzy.save(jpg, quality=95, subsampling=0, optimize=True)  # bez podpróbkowania barwy: ostre czerwienie i złoto
        maly = wyrownaj(img.resize((1280, 720), Image.LANCZOS), 1.2)
        maly.save(OUT / f"{nazwa}.png")
        maly.save(OUT / f"{nazwa}.jpg", quality=92, optimize=True)
        for f in (png, jpg, OUT / f"{nazwa}.jpg"):
            print(f, Image.open(f).size, f"{f.stat().st_size / 1e6:.2f} MB")
        return
    img = img.resize((1280, 720), Image.LANCZOS) if img.size != (1280, 720) else img
    img = wyrownaj(img, 1.2)
    png, jpg = OUT / f"{nazwa}.png", OUT / f"{nazwa}.jpg"
    img.save(png)
    img.save(jpg, quality=92, optimize=True)
    print(jpg, f"{jpg.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
