"""Miniaturki „Son of the Sun” na YouTube, złożone silnikiem teatru z wycinków filmu, w układzie zatwierdzonej
miniaturki „Pierwszego cesarza” (docs/WYTYCZNE_UJEC.md, sekcja 5; wzór: output/pierwszy-cesarz/miniatura.py —
tabliczki, szyld i biały obrys bierzemy stamtąd).

Reżyser 21.11.2026 („zrób miniaturkę w podobnym stylu co Pierwszy cesarz, bo miała dobrą klikalność”):
  A — „w tle ujęcie, jak walą te pioruny w nich 2, po lewej Susanoo z tym wiatrem czy kołem z ujęcia 26, mina, że jest
      zły”: burza na morzu, pioruny trafiają łodzie dwóch braci, po lewej duży Susanoo w wirze wiatru;
  B — „na ujęciu 26, ale wkładamy te łódki z piorunami na te pole ryżowe, że się zatapiają jak w bagnie, a w tle burza”:
      niebiańska równina z ujęcia „susanoo”, łodzie z piorunami toną w polu ryżowym, nad nimi burza, Susanoo jak w A.

  WARIANT=A python3 miniatura.py [en|pl]     → miniatura/miniatura_A_<język>.jpg i .png (1280 × 720)
  JAKOSC=1 …                                 → szybki podgląd (rysowane w 1280 × 720 zamiast w 2560 × 1440)
  ROZMIAR=3840 WARIANT=A python3 miniatura.py en → 4K dla YouTube: miniatura_A_en_4k.png i _4k.jpg, a z tego samego
                                                rysunku miniatura_A_en.jpg 1280 × 720
  python3 ../pierwszy-cesarz/fujifilm.py miniatura/miniatura_A_en_4k.png 1280 → wygląd zdjęcia Fujifilm (5.4)

Duże postacie (Susanoo, bracia) są rysowane od nowa w skali ekranu (`korpus_k`, kopia zestaw_jp._korpus_img z miną) —
zestaw_jp.py zostaje nietknięty, bo jego zmiana zmieniłaby wszystkie ujęcia filmu.
"""
import importlib.util
import math
import os
import random
import sys
from pathlib import Path

JEZ = sys.argv[1] if len(sys.argv) > 1 else "en"
os.environ["JEZYK"] = JEZ  # tabliczki w języku wersji (wytyczne 1.13)
HERE = Path(__file__).resolve().parent
CESARZ = HERE.parent / "pierwszy-cesarz"
sys.path.insert(0, str(HERE))
sys.path.append(str(CESARZ))

import papier  # noqa: E402

ROZMIAR = int(os.environ.get("ROZMIAR", "0"))
papier.Q = ROZMIAR / 1280 if ROZMIAR else float(os.environ.get("JAKOSC", "2"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import scena as S  # noqa: E402
import zestaw_jp as J  # noqa: E402
from papier import Cam, Sprite, Stage  # noqa: E402

_spec = importlib.util.spec_from_file_location("miniatura_cesarza", CESARZ / "miniatura.py")
M0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M0)  # poloz, nitki, stack_k, tabliczka, szyld, poloz_obrys, wyrownaj

P = J.P
OUT = HERE / "miniatura"
WARIANT = os.environ.get("WARIANT", "A").upper()
TYTUL = {"pl": "SYN SŁOŃCA", "en": "SON OF THE SUN"}[JEZ]
INK = J.INK
poly, ell, rect, shade = J.poly, J.ell, J.rect, J._shade


# ---------- lalki w skali ekranu, z miną ----------

def korpus_k(s, k, mina, napis=None):
    """zestaw_jp._korpus_img w skali k (mężczyzna: fryzura mizura albo dzikie, broda, wąsy, miecz, naszyjnik, wzór), bez
    oczu — oczy i usta rysuje twarz() według miny. napis — złote litery wycięte z papieru, naklejone na pierś (imię)."""
    w, h = J.FIG_W, J.FIG_H
    hair, sk, sp = s["wlosy"], s["skora"], s["spodnie"]
    tie = s["wiazanie"] or s["pas"]
    parts = []
    if s["fryzura"] == "dzikie":
        r = random.Random(5)
        pts = []
        for i in range(17):
            a = math.pi * (0.95 + 1.1 * i / 16)
            rr = 70 + (24 if i % 2 else 0) + r.uniform(-6, 6)
            pts.append((152 + rr * math.cos(a), 122 + rr * 1.05 * math.sin(a)))
        pts += [(214, 190), (200, 250), (150, 240), (96, 250), (88, 190)]
        parts.append((poly(pts), hair))
    parts.append((rect(136, 158, 166, 216), shade(sk, 0.92)))  # szyja
    parts += [(poly([(84, 404), (152, 404), (156, 528), (80, 528)]), sp, dict(edge=2)),
              (poly([(148, 404), (218, 404), (222, 528), (146, 528)]), shade(sp, 0.92), dict(edge=2)),
              (poly([(98, 534), (140, 534), (136, 656), (102, 656)]), (226, 220, 206)),
              (poly([(162, 534), (204, 534), (200, 656), (166, 656)]), (214, 208, 194)),
              (poly([(86, 518), (152, 518), (150, 540), (88, 540)]), tie),
              (poly([(150, 518), (216, 518), (214, 540), (152, 540)]), shade(tie, 0.9)),
              (poly([(92, 650), (142, 650), (160, 662), (156, 676), (92, 676)]), s["buty"]),
              (poly([(156, 650), (206, 650), (224, 662), (220, 676), (156, 676)]), shade(s["buty"], 0.9))]
    tun = s["tunika"]
    parts.append((poly([(96, 204), (204, 204), (214, 300), (226, 448), (74, 448), (86, 300)]), tun, dict(edge=2)))
    hem, wz, wk = 448, s["wzor"], s["wzor_kolor"] or s["pas"]
    if wz == "pasy":
        parts += [(rect(84, hem - 34, 216, hem - 26), wk, dict(rough=0.8)), (rect(84, hem - 18, 216, hem - 12), wk, dict(rough=0.8))]
    elif wz == "trojkaty":
        for x in range(82, 214, 16):
            parts.append((poly([(x, hem - 4), (x + 8, hem - 20), (x + 16, hem - 4)]), wk, dict(rough=0.7)))
    kol = s["kolnierz"] or shade(tun, 0.78)
    parts += [(poly([(118, 198), (184, 198), (178, 214), (124, 214)]), kol),
              (poly([(126, 204), (152, 204), (180, 300), (166, 306)]), kol),
              (poly([(84, 330), (216, 330), (218, 352), (82, 352)]), s["pas"]),
              (ell(170, 341, 14, 11), shade(s["pas"], 1.1)),
              (poly([(162, 350), (176, 350), (184, 420), (170, 424)]), s["pas"]),
              (poly([(176, 350), (190, 350), (204, 412), (192, 418)]), shade(s["pas"], 0.9))]
    if s["naszyjnik"]:
        for i in range(7):
            f = i / 6
            parts.append((J._magatama(120 + 60 * f, 214 + 26 * math.sin(math.pi * f), 5.5, 30 + 40 * f), s["naszyjnik"],
                          dict(kind="gladki", rough=0.4)))
    if napis:  # między naszyjnikiem a pasem; ten sam krój i złoto co szyld z tytułem
        parts.append((M0.Z.glyphs(napis, 22, M0.Z.FONT_PL, M0.Z.PL_IDX, (150, 288), "mm"), (232, 192, 108),
                      dict(kind="gladki", edge=1, rough=0.5, contrast=1.2)))
    if s["miecz"]:
        parts += [(J._band((100, 344), (50, 480), 13), (44, 36, 34), dict(contrast=1.2)), (J._band((50, 480), (46, 490), 13), J.GOLD),
                  (J._band((104, 336), (96, 354), 18), J.GOLD), (ell(108, 328, 10, 10), J.GOLD, dict(edge=0))]
    if s["fryzura"] == "mizura":
        parts.append((ell(192, 148, 9, 24), shade(hair, 0.85)))
    parts += [(ell(118, 132, 9, 13), shade(sk, 0.95)),
              (ell(152, 128, 38, 48), sk, dict(kind="gladki", contrast=0.6)),
              (poly([(184, 112), (200, 138), (186, 146)]), sk, dict(kind="gladki", contrast=0.6))]
    if s["fryzura"] == "mizura":
        parts += [(poly([(112, 120), (114, 92), (130, 74), (158, 68), (182, 76), (194, 98), (192, 112), (176, 96), (150, 90),
                         (126, 100)]), hair),
                  (ell(110, 152, 13, 30), hair, dict(edge=2)),
                  (rect(98, 140, 122, 148), (236, 230, 214))]
    elif s["fryzura"] == "dzikie":
        parts.append((poly([(110, 124), (106, 88), (126, 66), (160, 58), (190, 70), (200, 104), (184, 94), (160, 86), (128, 98)]), hair))
    if s["broda"]:
        parts.append((poly([(140, 160), (176, 150), (194, 148), (190, 176), (172, 208), (150, 200), (136, 182)]), hair))
    if s["wasy"] or s["broda"]:
        parts.append((poly([(158, 154), (192, 146), (190, 156), (166, 160)]), hair))
    return M0.stack_k(w, h, parts, seed=sum(map(ord, str(sorted(s.items())))) % 997, k=k)


def twarz(im, s, k, ox, oy, mina):
    """Oczy, brwi i usta na arkuszu korpusu (ox, oy — gdzie leży arkusz na obrazie, w pikselach arkusza).
    zly — brwi ściągnięte w „V”, przymrużone oczy z małymi źrenicami, otwarte usta z zębami, wypieki;
    krzyk — brwi wysoko, oczy szeroko, usta „o” (przerażenie)."""
    q = lambda pts: [((ox + x) * k, (oy + y) * k) for x, y in pts]
    W = lambda n: max(1, round(n * k))
    d = ImageDraw.Draw(im)
    ink = INK + (255,)
    sk, hair = s["skora"], s["wlosy"]
    rumieniec = Image.new("L", im.size, 0)
    ImageDraw.Draw(rumieniec).ellipse(q([(156, 134), (188, 154)]), fill=120 if mina == "zly" else 50)
    rumieniec = rumieniec.filter(ImageFilter.GaussianBlur(5 * k))
    tint = Image.new("RGBA", im.size, (214, 80, 64, 0))
    tint.putalpha(rumieniec)
    im.alpha_composite(tint)
    d = ImageDraw.Draw(im)
    oczy = ((137, 124, 8.5, 6.5), (171, 122, 8.0, 6.5))  # środek, promienie (dalsze oko w 3/4 węższe)
    if mina == "zly":
        for n, (cx, cy, rx, ry) in enumerate(oczy):
            d.ellipse(q([(cx - rx, cy - ry), (cx + rx, cy + ry)]), fill=(250, 246, 236, 255), outline=ink, width=W(2))
            d.ellipse(q([(cx + 1.5 - 2.8, cy + 1 - 2.8), (cx + 1.5 + 2.8, cy + 1 + 2.8)]), fill=ink)
            # powieka przymrużona ukosem: wewnętrzny kącik (bliżej nosa) niżej
            wew, zew = (cx + rx + 1, cy - 1) if n == 0 else (cx - rx - 1, cy - 1), (cx - rx - 2, cy - ry - 3) if n == 0 else (cx + rx + 2, cy - ry - 3)
            d.polygon(q([zew, wew, (wew[0], cy - ry - 6), (zew[0], cy - ry - 6)]), fill=sk + (255,))
            d.line(q([zew, wew]), fill=ink, width=W(3))
        # brwi: grube, ściągnięte do nosa
        d.polygon(q([(124, 106), (128, 101), (151, 113), (148, 119)]), fill=shade(hair, 0.9) + (255,))
        d.polygon(q([(160, 118), (157, 112), (182, 99), (186, 104)]), fill=shade(hair, 0.9) + (255,))
        d.line(q([(150, 106), (153, 114)]), fill=shade(sk, 0.7) + (220,), width=W(2))  # zmarszczka między brwiami
        # usta otwarte w krzyku złości, zęby u góry i u dołu (na brodzie)
        usta = [(157, 162), (171, 158), (187, 157), (185, 170), (175, 181), (161, 178)]
        d.polygon(q(usta), fill=(96, 22, 20, 255), outline=ink)
        d.polygon(q([(159, 162), (171, 159), (185, 158), (184, 164), (171, 165), (160, 167)]), fill=(250, 246, 236, 255))
        d.polygon(q([(164, 176), (175, 178), (182, 172), (181, 169), (174, 173), (164, 172)]), fill=(250, 246, 236, 255))
        d.line(q(usta + [usta[0]]), fill=ink, width=W(2))
        d.line(q([(184, 128), (190, 140)]), fill=shade(sk, 0.7) + (220,), width=W(2))
    else:
        for cx, cy, rx, ry in oczy:
            d.ellipse(q([(cx - rx, cy - ry - 1), (cx + rx, cy + ry + 1)]), fill=(250, 246, 236, 255), outline=ink, width=W(2))
            d.ellipse(q([(cx + 1 - 2.6, cy - 2.6), (cx + 1 + 2.6, cy + 2.6)]), fill=ink)
            d.arc(q([(cx - rx - 2, cy - ry - 12), (cx + rx + 2, cy - ry + 2)]), 200, 340, fill=shade(hair, 0.9) + (255,), width=W(3.5))
        d.ellipse(q([(160, 157), (178, 181)]), fill=(96, 22, 20, 255), outline=ink, width=W(2))
        d.line(q([(184, 128), (190, 140)]), fill=shade(sk, 0.75) + (200,), width=W(2))
    return im


def ramie_k(s, k, palec=False):
    """zestaw_jp._ramie_img w skali k; palec — wyciągnięty palec wskazujący (wskazuje wzdłuż ręki)."""
    w, h = J.RAMIE_W, J.RAMIE_H
    tun = s["rekaw"] or s["tunika"]
    parts = [(ell(55, 26, 25, 23), tun), (poly([(34, 22), (76, 22), (72, 206), (38, 206)]), tun, dict(edge=2, shade=0.2)),
             (poly([(38, 196), (72, 196), (74, 210), (36, 210)]), s["pas"]),
             (ell(56, 230, 15, 19), s["skora"], dict(kind="gladki", contrast=0.6))]
    if palec:
        parts += [(poly([(51, 238), (61, 238), (61, 280), (51, 280)]), s["skora"], dict(kind="gladki", contrast=0.6)),
                  (ell(56, 280, 5, 5), s["skora"], dict(kind="gladki", contrast=0.6))]
    return M0.stack_k(w, h, parts, seed=31 + len(str(tun)), k=k)


def postac(key, k, rece=(0.0, 0.0), mina="zly", palec=False, napis=None):
    """Cała lalka w jednym arkuszu (ręce na zawiasach w barkach, przednia przed korpusem, tylna za nim), twarzą w prawo.
    rece — kąt przedniej i tylnej ręki w stopniach (0 opuszczona, 90 przed siebie, 180 w górę, 200 w górę i do tyłu).
    Zwraca (wycinek, kotwica stóp jako ułamek arkusza, wysokość arkusza / wysokość postaci)."""
    s = J.spec(key)
    M, TOP = 270, 230  # zapas wokół korpusu na uniesione ręce
    CW, CH = J.FIG_W + 2 * M, J.FIG_H + TOP + 10
    im = Image.new("RGBA", (round(CW * k), round(CH * k)), (0, 0, 0, 0))
    body = korpus_k(s, k, mina, napis)
    arm = {n: ramie_k(s, k, palec and n == "przod") for n in ("przod", "tyl")}

    def reka(name, ang):
        bx, by = J.BARK[name]
        bx, by = (M + bx) * k, (TOP + by) * k
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        zx, zy = J.RAMIE_ZAWIAS
        layer.alpha_composite(arm[name], (round(bx - zx * k), round(by - zy * k)))
        return layer.rotate(ang, resample=Image.BICUBIC, center=(bx, by))

    def z_cieniem(base, top, sila=0.38):
        cien = Image.new("RGBA", top.size, (28, 16, 10, 0))
        cien.putalpha(top.getchannel("A").filter(ImageFilter.GaussianBlur(3 * k)).point(lambda v: int(v * sila)))
        base.alpha_composite(cien, (round(3 * k), round(5 * k)))
        base.alpha_composite(top)

    im.alpha_composite(reka("tyl", rece[1]))
    z_cieniem(im, (lambda L: (L.alpha_composite(body, (round(M * k), round(TOP * k))), L)[1])(Image.new("RGBA", im.size, (0, 0, 0, 0))))
    twarz(im, s, k, M, TOP, mina)
    z_cieniem(im, reka("przod", rece[0]))
    box = im.getbbox()
    im = im.crop(box)
    stopa = ((M + J.FIG_W / 2) * k - box[0], (TOP + J.STOPA) * k - box[1])
    spr = Sprite(im, f"mini-{key}-{k:.2f}-{rece}-{mina}-{palec}-{napis}", rim=2, clean=False, crop=False)
    return spr, (stopa[0] / im.size[0], stopa[1] / im.size[1]), im.size[1] / (k * (J.STOPA - J.CZUBEK))


def postaw(st, key, x, y, h, p, rece, mina, obrys, palec=False, rot=0.0, kolor=(252, 250, 244), napis=None, **kw):
    """Lalka stopami w (x, y) ekranu, h — wysokość postaci (od stóp do czubka głowy) w pikselach ekranu; obrys w px ekranu."""
    k = max(1.0, round(h / (J.STOPA - J.CZUBEK) * papier.Q * 4) / 4)
    spr, kot, ark = postac(key, k, rece, mina, palec, napis)
    M0.poloz_obrys(st, spr, x, y, p, h * ark, kot, kolor=kolor, gruby=obrys, k=k, rot=rot, **kw)


# ---------- rekwizyty w skali ekranu ----------

def lodz_k(k):
    """zestaw_jp.lodz(1) w skali k: kadłub z zadartym dziobem i rufą, wiosła (bez żagla)."""
    w, h = 560, 420
    hull_pts = [(10, 250), (40, 290), (110, 330), (450, 330), (520, 290), (552, 220), (530, 230), (480, 290), (90, 296), (40, 270)]
    parts = [(poly(hull_pts), (110, 74, 50), dict(edge=2, contrast=1.2)),
             (poly([(90, 296), (480, 290), (470, 306), (100, 310)]), (150, 104, 70)),
             (poly([(110, 314), (450, 314), (444, 324), (116, 324)]), (196, 64, 40))]
    im = M0.stack_k(w, h, parts, seed=331, k=k)
    d = ImageDraw.Draw(im)
    q = lambda pts: [(x * k, y * k) for x, y in pts]
    for x in (140, 210, 280, 350, 420):  # wiosła porzucone, krzywo
        bx, by = x - 40 + (x % 3) * 14, 400 - (x % 4) * 10
        d.line(q([(x, 300), (bx, by)]), fill=(90, 62, 44, 255), width=max(1, round(6 * k)))
        d.polygon(q([(bx, by - 8), (bx - 12, by + 18), (bx + 6, by + 20), (bx + 10, by - 4)]), fill=(110, 76, 52, 255))
    return Sprite(im, f"lodz-mini-{k:.2f}", rim=2, clean=False, crop=False)


def wir_k(k):
    """zestaw_jp.wir w skali k: białe spirale wiatru z bibuły (Susanoo, ujęcie 26)."""
    parts = []
    for i in range(3):
        pts = [(200 + (30 + 150 * f) * math.cos(f * 9 + i * 2.1), 200 + (30 + 150 * f) * math.sin(f * 9 + i * 2.1) * 0.7)
               for f in np.linspace(0, 1, 120)]
        parts.append((lambda d, s, pts=pts: d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(10 * s), joint="curve"),
                      (236, 240, 244)))
    im = M0.stack_k(400, 400, parts, seed=240, k=k)
    a = np.asarray(im.getchannel("A"), np.float32) * 0.85
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return Sprite(im, f"wir-mini-{k:.2f}", rim=1, clean=False, crop=False)


def chmura_k(k, v=0):
    """Ciemna chmura burzy (zestaw_jp.krazek('chmura')) w skali k, szersza."""
    r = random.Random(40 + v)
    parts = []
    for i in range(6):
        x = 70 + i * 62 + r.uniform(-14, 14)
        parts.append((ell(x, 110 + r.uniform(-20, 14), 58 + r.uniform(-8, 18), 44 + r.uniform(-6, 12)),
                      r.choice(((52, 54, 68), (62, 64, 80), (44, 46, 58), (70, 72, 88)))))
    return Sprite(M0.stack_k(480, 200, parts, seed=290 + v, k=k), f"chmura-mini-{v}-{k:.2f}", rim=2, clean=False)


def zylka_k(k):
    """Znak złości z komiksu (czerwona „żyłka”): cztery łuki w rogach kwadratu, wygięte do środka — nowy znak słownika
    (wytyczne 1.20: złość)."""
    im = Image.new("RGBA", (round(120 * k), round(120 * k)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, dd, szer = 60, 30, max(2, round(10 * k))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ox, oy = c + sx * dd, c + sy * dd  # środek łuku w rogu
            a0 = math.atan2(-sy, -sx)  # łuk patrzy do środka znaku
            pts = [((ox + dd * 0.8 * math.cos(a0 + f)) * k, (oy + dd * 0.8 * math.sin(a0 + f)) * k)
                   for f in np.linspace(-0.85, 0.85, 16)]
            d.line(pts, fill=(212, 34, 28, 255), width=szer, joint="curve")
            for x, y in (pts[0], pts[-1]):
                d.ellipse([x - szer / 2, y - szer / 2, x + szer / 2, y + szer / 2], fill=(212, 34, 28, 255))
    return Sprite(im, f"zylka-{k:.2f}", rim=1, clean=False)


def pole_k(k, przod=False):
    """Pole ryżowe (bagno) w skali k. Tył: błotnista woda z odbiciami nieba i rzędami kępek ryżu; przód: rzędy kępek
    i błotny wał — łodzie stoją między tyłem a przodem, więc toną w polu."""
    w, h = 1500, 300
    r = random.Random(77 if przod else 76)
    parts = []
    if not przod:
        parts.append((poly([(0, 40), (w, 20), (w, h), (0, h)]), (96, 92, 62), dict(edge=2, contrast=1.1)))
        for i in range(9):  # tafla wody między kępkami, odbija burzowe niebo
            x, y = r.uniform(60, w - 60), r.uniform(70, 250)
            parts.append((ell(x, y, r.uniform(90, 200), r.uniform(10, 22)), (124, 134, 140), dict(kind="gladki")))
        rzedy, kolory = (60, 110, 170, 230), ((70, 118, 62), (82, 132, 70), (92, 146, 76), (104, 156, 82))
    else:
        parts.append((poly([(0, 150)] + [(x, 132 + 14 * math.sin(x / 70)) for x in range(0, w + 1, 50)] + [(w, h), (0, h)]),
                      (104, 86, 58), dict(edge=2, contrast=1.15)))
        rzedy, kolory = (140, 200, 262), ((96, 150, 78), (108, 162, 86), (118, 170, 90))
    for y0, kol in zip(rzedy, kolory):
        kepki = []
        for x in range(10, w, 34):
            cx, cy = x + r.uniform(-8, 8), y0 + r.uniform(-5, 5)
            hh = r.uniform(30, 46) * (1.25 if przod else 1.0)
            for a in (-0.42, -0.15, 0.12, 0.4):  # kępka: cztery źdźbła
                tx, ty = cx + math.sin(a) * hh, cy - math.cos(a) * hh
                kepki.append([(cx - 3, cy), (tx, ty), (cx + 3, cy)])
        parts.append((lambda d, s, kp=kepki: [d.polygon([(x * s, y * s) for x, y in t], fill=255) for t in kp], kol,
                      dict(kind="gladki", rough=0.6)))
    return Sprite(M0.stack_k(w, h, parts, seed=88 + przod, k=k), f"pole-{przod}-{k:.2f}", rim=2, clean=False, crop=False)


def poletko_k(k):
    """Oderwane poletko ryżu (zestaw_jp.poletko(0)) w skali k — fruwa w wietrze Susanoo jak w ujęciu 26."""
    col = (92, 150, 80)
    parts = [(poly([(10, 10), (250, 10), (240, 66), (20, 66)]), shade(col, 0.8), dict(edge=2))]
    for i in range(6):
        y = 16 + i * 9
        parts.append((rect(22 + i * 2, y, 238 - i * 2, y + 5), col, dict(rough=0.7)))
    return Sprite(M0.stack_k(260, 70, parts, seed=250, k=k), f"poletko-mini-{k:.2f}", rim=1, clean=False)


def grudka_k(k, kolor=(84, 70, 46)):
    parts = [(poly([(4, 18), (14, 4), (32, 6), (38, 22), (24, 32), (8, 30)]), kolor, dict(edge=1))]
    return Sprite(M0.stack_k(40, 34, parts, seed=7, k=k), f"bloto-{k:.2f}", rim=1, clean=False)


def traba_k(k, przod=False):
    """Trąba powietrzna nad morzem (reżyser 21.11: „trzecią łódkę na środku w trąbie powietrznej”): lejek z półprzezroczystej
    szarej bibuły, szeroki pod chmurą, w dół wijący się cienki „sznur” do fal, owinięty cienkimi pasami wiru; u dołu piana.
    Tył — lejek i tylne pasy; przód — przednie pasy i piana przed łodzią, którą trąba porwała (łódź siedzi w wirze)."""
    w, h, cx = 600, 640, 300
    szer = lambda y: 34 + 190 * math.exp(-y / (0.27 * h))  # pół szerokości: rozszerza się pod chmurą
    srodek = lambda y: cx + 46 * math.sin(y / h * 3.4 + 0.3)  # lejek się wije
    r = random.Random(63)
    parts = []
    if not przod:
        ys = list(range(0, h + 1, 16))
        lewa = [(srodek(y) - szer(y) * (1 + 0.05 * r.uniform(-1, 1)), y) for y in ys]
        prawa = [(srodek(y) + szer(y) * (1 + 0.05 * r.uniform(-1, 1)), y) for y in reversed(ys)]
        parts.append((poly(lewa + prawa), (104, 112, 132), dict(kind="gladki", edge=0, contrast=0.9, rough=1.6)))
        parts.append((poly([(srodek(y) - szer(y) * 0.72, y) for y in ys] + [(srodek(y) - szer(y) * 0.12, y) for y in reversed(ys)]),
                      (138, 146, 166), dict(kind="gladki", rough=1.4)))
    for i in range(14):  # pasy wiru: cienkie łuki owinięte wokół lejka, na przemian z przodu i z tyłu
        if (i % 2 == 1) != przod:
            continue
        y0 = 18 + i * 44
        sz = szer(y0) * 1.06
        t0, t1 = (0.2, 2.9) if przod else (3.3, 6.0)
        gr = 4 + 5 * (1 - y0 / h)
        pts = [(srodek(y0) + sz * math.cos(t), y0 + 0.22 * sz * math.sin(t) + 0.3 * sz * math.cos(t)) for t in np.linspace(t0, t1, 26)]
        pts += [(srodek(y0) + sz * math.cos(t), y0 + gr + 0.22 * sz * math.sin(t) + 0.3 * sz * math.cos(t)) for t in np.linspace(t1, t0, 26)]
        parts.append((poly(pts), (238, 242, 248) if przod else (176, 186, 204), dict(kind="gladki", rough=0.8)))
    if przod:  # piana u stóp trąby
        for _ in range(10):
            parts.append((ell(srodek(h) + r.uniform(-80, 80), h - r.uniform(0, 34), r.uniform(24, 44), r.uniform(10, 20)), (236, 240, 246),
                          dict(kind="gladki")))
    im = M0.stack_k(w, h, parts, seed=71 + przod, k=k)
    a = np.asarray(im.getchannel("A"), np.float32) * (0.92 if przod else 0.86)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return Sprite(im, f"traba-{przod}-{k:.2f}", rim=2, clean=False, crop=False)


def trzecia_lodz(st, K):
    """Trzecia łódź (Iwarebiko) porwana przez trąbę powietrzną na środku kadru, przechylona, z wiosłami w powietrzu."""
    tx, ty_gora, th, lx, ly, wl, lh, kat = K["traba"]
    kt = max(1.0, round(th / 640 * papier.Q * 4) / 4)
    p = 0.5  # między pasmami fal 1 i 2: stopa trąby chowa się za falą
    M0.poloz(st, traba_k(kt), tx, ty_gora, p, h=th, anchor=(0.5, 0.0), shadow=None)
    kl = max(1.0, round(wl / 542 * papier.Q * 4) / 4)
    poklad = (0.74 * 420 - 290) / 560 * wl
    ux, uy = S._off(0.0, -poklad, kat)
    postaw(st, "iwarebiko", lx + ux, ly + uy + 0.24 * lh, lh, p + 0.002, (165, 200), "krzyk", 4, rot=kat * 0.6, kolor=(236, 224, 196))
    M0.poloz(st, lodz_k(kl), lx, ly, p + 0.004, w=wl, anchor=(0.5, 0.74), rot=kat)
    M0.poloz(st, traba_k(kt, True), tx, ty_gora, p + 0.006, h=th, anchor=(0.5, 0.0), shadow=None)
    r = random.Random(17)
    for n in range(3):  # wiosła wyrwane z łodzi krążą w wirze
        a_ = 1.2 + n * 2.1
        ox, oy = lx + math.cos(a_) * wl * 0.62, ly - 40 + math.sin(a_) * wl * 0.22
        dl = wl * 0.26
        kk = r.uniform(0, 180)
        st.line([(ox - dl / 2 * math.cos(math.radians(kk)), oy - dl / 2 * math.sin(math.radians(kk))),
                 (ox + dl / 2 * math.cos(math.radians(kk)), oy + dl / 2 * math.sin(math.radians(kk)))], p + 0.007, width=5,
                color=(96, 66, 46), alpha=1.0)
    kc = max(1.0, papier.Q * 1.2)  # góra lejka ginie w chmurze
    M0.poloz(st, chmura_k(kc, 7), tx + 10, ty_gora - 26, p + 0.0065, w=th * 0.95, anchor=(0.5, 0.5), shadow=(6, 9, 10, 0.3))


def piorun(st, x0, y0, x1, y1, p, seed, gr=1.0, odnogi=2):
    """Piorun (scena.piorun) grubszy, z odnogami: błękitna poświata, biały rdzeń, poświata w miejscu uderzenia."""
    r = random.Random(900 + seed)
    pts, n = [(x0, y0)], 10
    for i in range(1, n):
        f = i / n
        pts.append((S.lerp(x0, x1, f) + r.uniform(-34, 34) * (1 - f * 0.6), S.lerp(y0, y1, f) + r.uniform(-8, 8)))
    pts.append((x1, y1))
    galezie = []
    for _ in range(odnogi):
        i = r.randint(2, n - 4)
        bx, by = pts[i]
        dl = r.uniform(70, 130)
        a = r.choice((-1, 1)) * r.uniform(0.5, 0.9)
        galezie.append([(bx, by), (bx + math.sin(a) * dl * 0.5 + r.uniform(-10, 10), by + dl * 0.5),
                        (bx + math.sin(a) * dl, by + dl * 0.9)])
    for g in [pts] + galezie:
        sz = 1.0 if g is pts else 0.5
        st.line(g, p, width=30 * gr * sz, color=(120, 170, 255), alpha=0.30)
        st.line(g, p + 0.0003, width=15 * gr * sz, color=(190, 220, 255), alpha=0.55)
        st.line(g, p + 0.0006, width=6 * gr * sz, color=(255, 255, 255), alpha=1.0)
    st.put(J.glow(), x1, y1, p + 0.001, w=320 * gr, anchor=(0.5, 0.5), mode="add", alpha=0.75, shadow=None, tint=(0.85, 0.9, 1.0))


def szyld_made_in(k):
    """Druga tabliczka jak szyld z tytułem (czarna deska, złota ramka, złote litery): u góry małe „made in” kursywą,
    pod nim duże „JAPAN”; pod deską dwie drewniane nóżki, którymi stoi za rampą."""
    Z = M0.Z
    mal, duz, NOGA = 40, 88, 70
    f = Z.ImageFont.truetype(Z.FONT_PL, duz * 2, index=Z.PL_IDX)
    w = int(f.getlength("JAPAN") / 2 + 110)
    hd = mal + duz + 78  # wysokość deski
    h = hd + NOGA
    gold, ciemne = (220, 178, 96), (150, 116, 60)
    R = lambda x0, y0, x1, y1: poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    parts = [(R(0.2 * w - 9, hd - 20, 0.2 * w + 9, h - 2), (70, 50, 36)), (R(0.8 * w - 9, hd - 20, 0.8 * w + 9, h - 2), (62, 44, 32)),
             (R(4, 4, w - 4, hd - 4), (30, 22, 20), dict(kind="gladki", contrast=1.5)),
             (R(4, 4, w - 4, 14), gold), (R(4, hd - 14, w - 4, hd - 4), gold), (R(4, 4, 14, hd - 4), gold), (R(w - 14, 4, w - 4, hd - 4), gold),
             (R(22, 22, w - 22, 26), ciemne), (R(22, hd - 26, w - 22, hd - 22), ciemne),
             (Z.glyphs("made in", mal, Z.FONT_PL, Z.PL_IDX + 1, (w / 2, 30 + mal / 2), "mm"), (232, 192, 108),
              dict(kind="gladki", rough=0.5, contrast=1.2)),
             (Z.glyphs("JAPAN", duz, Z.FONT_PL, Z.PL_IDX, (w / 2, 38 + mal + duz / 2), "mm"), (232, 192, 108),
              dict(kind="gladki", rough=0.5, contrast=1.2))]
    return Sprite(M0.stack_k(w, h, parts, seed=17, k=k), f"szyld-made-in-{k:.2f}", rim=round(3 * k), clean=False)


# ---------- scena ----------

def burza_niebo(st, K):
    """Ciemne chmury u góry kadru (stąd walą pioruny) i błysk na niebie."""
    kc = max(1.0, papier.Q * 1.2)
    for v, (x, y, wd) in enumerate(K["chmury"]):
        M0.poloz(st, chmura_k(kc, v), x, y, P.chmury + 0.02 + 0.004 * v, w=wd, anchor=(0.5, 0.5), shadow=(6, 9, 10, 0.3))
    fx, fy, fw = K["blysk"]
    M0.poloz(st, J.glow(), fx, fy, 0.2, w=fw, anchor=(0.5, 0.5), mode="add", alpha=0.55, shadow=None, tint=(0.8, 0.85, 1.0))
    for n in range(26):  # deszcz: ukośne nitki
        r = random.Random(500 + n)
        x, y = r.uniform(420, 1300), r.uniform(-40, 520)
        st.line([(x, y), (x - 26, y + 120)], P.gory_dal + 0.01, width=1.6, color=(190, 205, 230), alpha=0.35)


def bracia_w_lodziach(st, K, p_pole=None):
    """Dwie łodzie braci przechylone uderzeniem pioruna; bracia z rękami w górze krzyczą; pioruny w każdą łódź.
    K["lodzie"]: (lalka, x, y kotwicy łodzi, szerokość łodzi, wysokość brata, przechył, ręce, plan)."""
    for n, (key, x, y, wl, lh, przechyl, rece, p_lodz) in enumerate(K["lodzie"]):
        kl = max(1.0, round(wl / 542 * papier.Q * 4) / 4)
        poklad = (0.74 * 420 - 290) / 560 * wl  # pokład nad kotwicą łodzi (arkusz lodz_k: 560 × 420)
        ux, uy = S._off(-0.03 * wl if n == 0 else 0.05 * wl, -poklad, przechyl)
        bx, by = x + ux, y + uy + 0.24 * lh  # stopy schowane za burtą
        postaw(st, key, bx, by, lh, p_lodz - 0.003, rece, "krzyk", 4, rot=przechyl * 0.5, kolor=(236, 224, 196))
        M0.poloz(st, lodz_k(kl), x, y, p_lodz, w=wl, anchor=(0.5, 0.74), rot=przechyl)
        px, py = K["pioruny"][n]
        piorun(st, px, -30, bx + 6, by - lh * 1.02, p_lodz + 0.002, seed=20 + n, gr=K.get("gr", 1.0))
        if p_pole:  # błoto pryska spod kadłuba
            r = random.Random(30 + n)
            for _ in range(9):
                a = r.uniform(-2.6, -0.5)
                d_ = r.uniform(0.25, 0.6) * wl
                M0.poloz(st, grudka_k(max(1.0, papier.Q)), x + math.cos(a) * d_, y - 10 + math.sin(a) * d_ * 0.45, p_pole + 0.006,
                         h=r.uniform(14, 26), anchor=(0.5, 0.5), rot=r.uniform(0, 360), shadow=(2, 3, 3, 0.3))


def scena_a(st, K):
    """A: burza na morzu (ujęcie „burza”) — wzburzone fale, łodzie braci, pioruny."""
    w = S.stan(S.I["burza"])
    w.sun = 0.0
    S.morze(st, K["t"], w, burza=1.0, tint=K["tint"], chmury_k=(0.0, 0.0, 0.0), kul=False)
    burza_niebo(st, K)
    if K.get("traba"):
        trzecia_lodz(st, K)
    bracia_w_lodziach(st, K)


def scena_b(st, K):
    """B: niebiańska równina z ujęcia „susanoo” w burzy; łodzie toną w polu ryżowym."""
    w = S.stan(S.I["susanoo"])
    w.sun = 0.0
    # z ujęcia „susanoo” zostaje papier nieba i daleki pas chmur, na których leży niebiańska równina; bliższe pasy chmur
    # zasłaniałyby pole ryżowe (wyglądały jak śnieg), a złote chmurki — jak pogoda
    S.niebo_papier(st, w, K["tint"])
    J.Z0.rise(st, J.pasmo("chmury"), S.CX, 560, P.gory, 1.0, K["t"], 501, w=2000, wob=0.0, lift=300, haze=0.15)
    burza_niebo(st, K)
    kp = max(1.0, round(K["pole"][2] / 1500 * papier.Q * 4) / 4)
    x, y, wd = K["pole"]
    p_lodz = K["lodzie"][0][7]
    M0.poloz(st, pole_k(kp), x, y, P.most + 0.01, w=wd, anchor=(0.5, 0.0), shadow=None)
    M0.poloz(st, pole_k(kp, True), x, y + K["pole_przod"], p_lodz + 0.01, w=wd, anchor=(0.5, 0.0), shadow=(4, 6, 8, 0.3))
    bracia_w_lodziach(st, K, p_pole=p_lodz)
    S.rampa(st, 1.0)
    kk = max(1.0, papier.Q)
    for n, (px, py, rot) in enumerate(K["poletka"]):  # poletka zerwane wiatrem (ujęcie 26)
        M0.poloz(st, poletko_k(kk), px, py, P.gory + 0.05 + 0.002 * n, w=150, anchor=(0.5, 0.5), rot=rot, shadow=(3, 5, 5, 0.3))


def scena(K):
    st = Stage(0.0, seed=7)
    st.T = 1.0
    cx, cy, m = K["kamera"]
    st.cam = Cam(cx, cy, m, 0.8, lens=m, truck=0.0)
    st.focus, st.dof = P.lalki, K.get("dof", 0.35)
    (scena_a if WARIANT == "A" else scena_b)(st, K)

    # Susanoo po lewej: wir wiatru za nim, gruby biały obrys, mina złości, palcem wskazuje łodzie, druga pięść w górze
    sx, sy, sh = K["susanoo"]
    wx, wy, ww = K["wir"]
    M0.poloz(st, wir_k(max(1.0, ww / 400 * papier.Q)), wx, wy, P.lalki + 0.004, w=ww, anchor=(0.5, 0.5), rot=K.get("wir_kat", -20),
             shadow=None, alpha=0.95)
    postaw(st, "susanoo", sx, sy, sh, P.lalki + 0.01, K["rece"], "zly", K["obrys"], palec=True, rot=K.get("susanoo_kat", -3),
           napis=K.get("napis"))
    zx, zy, zh = K["zylka"]
    M0.poloz(st, zylka_k(max(1.0, zh / 120 * papier.Q)), zx, zy, P.lalki + 0.02, h=zh, anchor=(0.5, 0.5), rot=12, shadow=(3, 4, 4, 0.35))

    # tabliczki z okrzykami (słownik znaków) i szyld z tytułem
    for txt, (tx, ty, th, kat) in K["tabliczki"].items():
        M0.nitki(st, M0.tabliczka(txt, 64, M0.K_TAB), tx, ty, P.rekwizyty + 0.03, h=th, xs=(0.2, 0.8), rot=kat)
    sz = M0.szyld(TYTUL, k=M0.K_TAB)
    lx, gy, hs, maxw = K["szyld"]
    hs = min(hs, maxw * sz.h / sz.w)
    M0.nitki(st, sz, lx + 0.5 * hs * sz.w / sz.h, gy, 0.95, h=hs, xs=(0.1, 0.9), rot=-0.8)
    if K.get("made_in"):  # tabliczka „made in JAPAN” na nóżkach za rampą (reżyser 21.11)
        mx, my, mh = K["made_in"]
        M0.poloz(st, szyld_made_in(M0.K_TAB), mx, my, P.rampa - 0.01, h=mh, anchor=(0.5, 1.0), rot=1.2, shadow=(5, 8, 8, 0.45))
    st.grade = K["grade"]
    return st


# Układ kadru w pikselach ekranu (1280 × 720); kamera 1:1 z kadrem wzorcowym filmu (morze, niebo jak w ujęciach)
WSPOLNE = dict(
    kamera=(640, 360, 1.0),
    susanoo=(285, 1250, 1000),  # stopy: x, y; wysokość postaci (do pasa w kadrze)
    rece=(72, 196),  # przednia wskazuje łodzie, tylna pięść w górze, z boku głowy
    obrys=9,
    wir=(250, 380, 900),  # środek wiru i szerokość
    zylka=(372, 196, 60),
    szyld=(40, 12, 104, 600),
    napis="SUSANOO",  # na piersi Susanoo (reżyser 21.11)
    # „made in JAPAN” w samym prawym dolnym rogu, z takim odstępem od krawędzi jak szyld z tytułem po lewej (reżyser 21.11:
    # „prawy dolny róg, a nie odsunięte od krawędzi” — czas filmu YouTube położy na tabliczce, decyzja reżysera);
    # środek u dołu nóżek, wysokość z nóżkami
    made_in=(1138, 700, 150),
    chmury=((700, 20, 560), (1050, 40, 620), (860, 150, 520), (1240, 170, 420), (470, 110, 460)),
    blysk=(900, 160, 1500),
    grade=(0.96, 0.98, 1.04),
)
KADRY = {
    "A": dict(WSPOLNE, t=2.3, tint=(0.46, 0.5, 0.66),
              # reżyser 21.11: „łódki trochę wyżej i trzecia na środku w trąbie powietrznej”
              lodzie=(("brat2", 730, 556, 420, 160, -16, (160, 205), 0.66), ("brat3", 1170, 508, 340, 134, 15, (150, 190), 0.52)),
              pioruny=((650, 0), (1215, 0)),
              traba=(950, 90, 470, 962, 330, 290, 104, 24),  # trąba: x, góra, wysokość; łódź: x, y, szerokość; Iwarebiko; przechył
              # trzy łodzie i trąba: „BROTHER!” zdjęte, żeby kadr się nie tłoczył (najwyżej 3–4 napisy, 5.1)
              tabliczki={"GRRR!": (470, 168, 72, -7), "AAAA!": (560, 280, 62, 6)}),
    "B": dict(WSPOLNE, t=2.0, tint=(0.56, 0.6, 0.74),
              pole=(860, 440, 1500), pole_przod=70,
              lodzie=(("brat2", 790, 640, 470, 168, -16, (160, 205), 0.66), ("brat3", 1080, 590, 380, 140, 14, (150, 190), 0.62)),
              pioruny=((700, 0), (1180, 0)),
              poletka=((470, 330, -30), (560, 230, 40)),
              tabliczki={"GRRR!": (470, 150, 72, -7), "AAAA!": (650, 270, 62, 6), "BRACIE!": (1040, 230, 58, -5)}),
}


def pustka():
    """Test pustki (wytyczne 1.3, 5.2): płótno w barwie magenty bez obróbki — ile pikseli kadru nie zakrywa dekoracja."""
    from papier import VOID
    st = scena(KADRY[WARIANT])
    st.void = VOID
    arr = np.asarray(st.render(post=False)).astype(np.int16)
    n = int(((arr[..., 0] > 250) & (arr[..., 1] < 6) & (arr[..., 2] > 250)).sum())
    print(f"wariant {WARIANT}: pustka {n} px")


def main():
    if os.environ.get("PUSTKA") == "1":
        return pustka()
    OUT.mkdir(exist_ok=True)
    img = scena(KADRY[WARIANT]).render()
    nazwa = f"miniatura_{WARIANT}_{JEZ}"
    if ROZMIAR:  # duży plik wprost z rysunku, a 1280 × 720 zmniejszone z niego (przed wyostrzeniem)
        duzy = M0.wyrownaj(img, 1.2 * papier.Q * 0.7)
        png, jpg = OUT / f"{nazwa}_{ROZMIAR // 960}k.png", OUT / f"{nazwa}_{ROZMIAR // 960}k.jpg"
        duzy.save(png, optimize=True)
        duzy.save(jpg, quality=95, subsampling=0, optimize=True)
        maly = M0.wyrownaj(img.resize((1280, 720), Image.LANCZOS), 1.2)
        maly.save(OUT / f"{nazwa}.png")
        maly.save(OUT / f"{nazwa}.jpg", quality=92, optimize=True)
        for f in (png, jpg, OUT / f"{nazwa}.jpg"):
            print(f, Image.open(f).size, f"{f.stat().st_size / 1e6:.2f} MB")
        return
    img = img.resize((1280, 720), Image.LANCZOS) if img.size != (1280, 720) else img
    img = M0.wyrownaj(img, 1.2)
    img.save(OUT / f"{nazwa}.png")
    img.save(OUT / f"{nazwa}.jpg", quality=92, optimize=True)
    print(OUT / f"{nazwa}.jpg")


if __name__ == "__main__":
    main()
