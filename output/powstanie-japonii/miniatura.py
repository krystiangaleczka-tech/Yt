"""Miniaturki „Son of the Sun” na YouTube, złożone silnikiem teatru z wycinków filmu, w układzie zatwierdzonej
miniaturki „Pierwszego cesarza” (docs/WYTYCZNE_UJEC.md, sekcja 5; wzór: output/pierwszy-cesarz/miniatura.py —
tabliczki, szyld i biały obrys bierzemy stamtąd).

Reżyser 21.11.2026 („zrób miniaturkę w podobnym stylu co Pierwszy cesarz, bo miała dobrą klikalność”):
  A — „w tle ujęcie, jak walą te pioruny w nich 2, po lewej Susanoo z tym wiatrem czy kołem z ujęcia 26, mina, że jest
      zły”: burza na morzu, pioruny trafiają łodzie dwóch braci, po lewej duży Susanoo w wirze wiatru;
  B — „na ujęciu 26, ale wkładamy te łódki z piorunami na te pole ryżowe, że się zatapiają jak w bagnie, a w tle burza”:
      niebiańska równina z ujęcia „susanoo”, łodzie z piorunami toną w polu ryżowym, nad nimi burza, Susanoo jak w A.
Reżyser 21.11.2026 („2 kompletnie inne miniatury do A/B”):
  C — czterech braci, przeżył jeden: świt nad Yamato, słońce za Iwarebiko, trzej bracia przekreśleni, „AM I NEXT?!”;
  D — wąż o ośmiu głowach w nocy nad Izumo: najbliższa głowa w zbliżeniu, mały Susanoo z mieczem, „8 HEADS?!”.

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
from PIL import Image, ImageDraw, ImageFilter, ImageOps  # noqa: E402

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


def postac(key, k, rece=(0.0, 0.0), mina="zly", palec=False, napis=None, miecz=False, lustro=False):
    """Cała lalka w jednym arkuszu (ręce na zawiasach w barkach, przednia przed korpusem, tylna za nim), twarzą w prawo.
    rece — kąt przedniej i tylnej ręki w stopniach (0 opuszczona, 90 przed siebie, 180 w górę, 200 w górę i do tyłu).
    miecz — miecz w pięści przedniej ręki, ostrze przedłużeniem ręki (jak scena.MIECZ); lustro — twarzą w lewo.
    Zwraca (wycinek, kotwica stóp jako ułamek arkusza, wysokość arkusza / wysokość postaci)."""
    s = J.spec(key)
    M, TOP = (400, 580) if miecz else (270, 230)  # zapas wokół korpusu na uniesione ręce (i miecz nad głową)
    CW, CH = J.FIG_W + 2 * M, J.FIG_H + TOP + 10
    im = Image.new("RGBA", (round(CW * k), round(CH * k)), (0, 0, 0, 0))
    body = korpus_k(s, k, mina, napis)
    arm = {n: ramie_k(s, k, palec and n == "przod") for n in ("przod", "tyl")}

    def reka(name, ang):
        bx, by = J.BARK[name]
        bx, by = (M + bx) * k, (TOP + by) * k
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        zx, zy = J.RAMIE_ZAWIAS
        if miecz and name == "przod":  # rękojeść pod pięścią: ręka przykrywa uchwyt (wytyczne 1.28: chwyt za uchwyt)
            mi = miecz_k(k)
            hx, hy = bx + (56 - zx) * k, by + (230 - zy) * k
            layer.alpha_composite(mi, (round(hx - mi.size[0] / 2), round(hy - 40 * k)))
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
    if lustro:
        im, stopa = ImageOps.mirror(im), (im.size[0] - stopa[0], stopa[1])
    spr = Sprite(im, f"mini-{key}-{k:.2f}-{rece}-{mina}-{palec}-{napis}-{miecz}-{lustro}", rim=2, clean=False, crop=False)
    return spr, (stopa[0] / im.size[0], stopa[1] / im.size[1]), im.size[1] / (k * (J.STOPA - J.CZUBEK))


def postaw(st, key, x, y, h, p, rece, mina, obrys, palec=False, rot=0.0, kolor=(252, 250, 244), napis=None, miecz=False, lustro=False, **kw):
    """Lalka stopami w (x, y) ekranu, h — wysokość postaci (od stóp do czubka głowy) w pikselach ekranu; obrys w px ekranu."""
    k = max(1.0, round(h / (J.STOPA - J.CZUBEK) * papier.Q * 4) / 4)
    spr, kot, ark = postac(key, k, rece, mina, palec, napis, miecz, lustro)
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


# ---------- C i D: dwie zupełnie inne miniaturki do testu A/B (reżyser 21.11: „2 kompletnie inne miniatury do A/B”) ----------

def miecz_k(k):
    """Prosty miecz (jak zestaw_jp.miecz_jp) w skali k, pionowo: głowica u góry, uchwyt, jelec, ostrze w dół."""
    parts = [(ell(30, 8, 9, 8), J.GOLD), (rect(24, 12, 36, 68), (52, 38, 32)), (rect(6, 66, 54, 80), J.GOLD),
             (poly([(21, 80), (39, 80), (37, 336), (30, 362), (23, 336)]), (214, 222, 230), dict(kind="gladki", contrast=1.3)),
             (rect(29, 84, 31, 330), (168, 178, 190))]
    return M0.stack_k(60, 366, parts, seed=61, k=k)


def glowa_k(k, v=0, bohater=False):
    """zestaw_jp.waz_glowa w skali k (pyskiem w prawo). bohater — głowa z pierwszego planu: paszcza rozwarta szerzej,
    kły, brew nad okiem, rozwidlony język."""
    body = ((70, 92, 70), (84, 100, 66), (64, 84, 72))[v % 3]
    if not bohater:
        w, h = 300, 200
        parts = [(poly([(10, 70), (90, 40), (200, 50), (286, 84), (240, 100), (200, 104), (284, 120), (250, 140), (150, 150),
                        (60, 140), (10, 120)]), body, dict(edge=2, contrast=1.2)),
                 (poly([(200, 100), (280, 86), (280, 92), (204, 108)]), (190, 50, 40)),
                 (poly([(204, 108), (282, 120), (276, 126), (206, 116)]), (190, 50, 40)),
                 (poly([(70, 40), (110, 10), (120, 44)]), shade(body, 0.8)), (poly([(120, 44), (150, 16), (158, 48)]), shade(body, 0.8)),
                 (ell(176, 72, 14, 11), (230, 200, 60)), (ell(178, 72, 5, 9), (180, 30, 30))]
        im = M0.stack_k(w, h, parts, seed=300 + v, k=k)
        d = ImageDraw.Draw(im)
        q = lambda pts: [(x * k, y * k) for x, y in pts]
        for x in (230, 248, 262):
            d.polygon(q([(x, 94), (x + 5, 104), (x + 9, 94)]), fill=(244, 240, 226, 255))
        for n in range(8):
            d.arc(q([(30 + n * 18, 80), (50 + n * 18, 104)]), 200, 340, fill=shade(body, 0.6) + (200,), width=max(1, round(2 * k)))
        return im
    w, h = 380, 200
    parts = [(poly([(340, 112), (300, 116), (238, 112)]), (200, 40, 50)),  # język (pod głową, wychodzi z paszczy)
             (poly([(236, 110), (300, 112), (346, 98), (352, 104), (316, 116), (356, 124), (350, 130), (300, 120), (236, 118)]),
              (206, 44, 54), dict(kind="gladki")),
             (poly([(222, 100), (290, 84), (294, 146), (226, 116)]), (120, 22, 22), dict(kind="gladki", contrast=0.7)),  # wnętrze
             (poly([(10, 70), (90, 36), (200, 44), (292, 74), (290, 86), (222, 100), (226, 116), (292, 144), (276, 160), (150, 162),
                    (60, 150), (10, 122)]), body, dict(edge=3, contrast=1.25)),
             (poly([(40, 52), (64, 14), (84, 46)]), shade(body, 0.75)), (poly([(84, 44), (112, 4), (128, 42)]), shade(body, 0.75)),
             (poly([(128, 42), (156, 10), (166, 46)]), shade(body, 0.75)),
             (ell(178, 76, 19, 15), (244, 196, 52)), (ell(180, 76, 6, 13), (176, 22, 22)),
             (poly([(148, 54), (210, 60), (214, 70), (150, 66)]), shade(body, 0.55)),  # brew zmarszczona nad okiem
             (ell(270, 78, 6, 4), shade(body, 0.45))]
    im = M0.stack_k(w, h, parts, seed=340 + v, k=k)
    d = ImageDraw.Draw(im)
    q = lambda pts: [(x * k, y * k) for x, y in pts]
    for x0, x1, dl in ((228, 238, 14), (244, 254, 16), (262, 272, 20), (278, 288, 22)):  # kły u góry
        f = (x0 - 222) / 70
        y = 100 - 16 * f
        d.polygon(q([(x0, y), (x1, y - 2), ((x0 + x1) / 2, y + dl)]), fill=(248, 244, 230, 255), outline=INK + (255,))
    for x0, x1, dl in ((234, 244, 12), (254, 264, 16), (274, 284, 18)):  # kły na dole
        f = (x0 - 226) / 68
        y = 118 + 26 * f
        d.polygon(q([(x0, y), (x1, y + 4), ((x0 + x1) / 2, y - dl)]), fill=(248, 244, 230, 255), outline=INK + (255,))
    for n in range(8):
        d.arc(q([(24 + n * 22, 92), (48 + n * 22, 122)]), 200, 340, fill=shade(body, 0.6) + (210,), width=max(1, round(2.5 * k)))
    return im


def luska_k(k, v=0):
    body = ((70, 92, 70), (84, 100, 66), (64, 84, 72))[v % 3]
    parts = [(ell(60, 60, 54, 54), body, dict(edge=2, contrast=1.2)), (ell(60, 76, 34, 26), (176, 120, 70))]
    im = M0.stack_k(120, 120, parts, seed=310 + v, k=k)
    d = ImageDraw.Draw(im)
    for x in (34, 60, 86):
        d.arc([(x - 14) * k, 30 * k, (x + 14) * k, 58 * k], 200, 340, fill=shade(body, 0.55) + (200,), width=max(1, round(3 * k)))
    return im


def _obroc_pkt(x, y, cx, cy, ang):
    """Punkt po PIL rotate(ang) wokół (cx, cy) — obrót przeciwny do wskazówek zegara na ekranie."""
    a = math.radians(ang)
    dx, dy = x - cx, y - cy
    return cx + dx * math.cos(a) + dy * math.sin(a), cy - dx * math.sin(a) + dy * math.cos(a)


def waz_bohater(k, K):
    """Najbliższa głowa węża razem z szyją z łusek w jednym arkuszu (gruby biały obrys idzie dookoła całej sylwetki).
    Jednostki arkusza = piksele ekranu 1280 × 720. Zwraca (wycinek, oko w ułamkach arkusza)."""
    W_, H_ = K["bohater_ark"]
    (b0, b1, b2), sh, kat, v = K["bohater_szyja"], K["bohater_skala"], K["bohater_kat"], 0
    im = Image.new("RGBA", (round(W_ * k), round(H_ * k)), (0, 0, 0, 0))
    duza = luska_k(k * 2.3, v)
    n = 15
    for j in range(n + 1):  # szyja: łuski od dołu (spod kadru) ku głowie, coraz mniejsze
        u = j / n
        x = (1 - u) ** 2 * b0[0] + 2 * (1 - u) * u * b1[0] + u * u * b2[0]
        y = (1 - u) ** 2 * b0[1] + 2 * (1 - u) * u * b1[1] + u * u * b2[1]
        sz = S.lerp(1.0, 0.68, u)
        l = duza.resize((round(duza.size[0] * sz), round(duza.size[1] * sz)), Image.LANCZOS)
        im.alpha_composite(l, (round(x * k - l.size[0] / 2), round(y * k - l.size[1] / 2)))
    g = glowa_k(k * sh, v, True)
    zaw = (52, 100)  # nasada głowy na arkuszu głowy (tył czaszki)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ox, oy = b2[0] * k - zaw[0] * k * sh, b2[1] * k - zaw[1] * k * sh
    layer.alpha_composite(g, (round(ox), round(oy)))
    layer = layer.rotate(kat, resample=Image.BICUBIC, center=(b2[0] * k, b2[1] * k))
    im.alpha_composite(layer)
    ex, ey = _obroc_pkt(ox + 180 * k * sh, oy + 76 * k * sh, b2[0] * k, b2[1] * k, kat)
    return Sprite(im, f"waz-bohater-{k:.2f}", rim=2, clean=False, crop=False), (ex / im.size[0], ey / im.size[1])


def szyja_k(st, base, head, hh, v, p, seed):
    """scena.szyja w skali ekranu (nieruchoma): łuk łusek od nasady za wzgórzem do głowy o wysokości hh."""
    kk = max(1.0, round(hh / 74 * papier.Q * 0.9 * 4) / 4)
    lus = Sprite(luska_k(kk, v), f"luska-{v}-{kk:.2f}", rim=2, clean=False)
    (bx, by), (hx, hy) = base, head
    cx, cy = (bx + hx) / 2 + 80 * math.sin(seed), min(by, hy) - 170
    pts, n = [], 30  # szyja cieńsza niż w filmie, więc łusek gęściej: zachodzą na siebie, nie stoją jak stos monet
    for j in range(n + 1):
        u = j / n
        pts.append(((1 - u) ** 2 * bx + 2 * (1 - u) * u * cx + u * u * hx, (1 - u) ** 2 * by + 2 * (1 - u) * u * cy + u * u * hy))
    for j, (x, y) in enumerate(pts[:-1]):
        M0.poloz(st, lus, x, y, p + 0.0002 * j, h=S.lerp(78, 50, j / n) * hh / 74 * 0.72, anchor=(0.5, 0.5), shadow=(3, 4, 5, 0.3))
    (ax, ay), (zx, zy) = pts[-2], pts[-1]
    face = 1 if zx >= ax else -1
    ang = math.degrees(math.atan2(zy - ay, zx - ax))
    rot = ang if face > 0 else ang - 180
    gk = max(1.0, round(hh / 140 * papier.Q * 4) / 4)
    gl = Sprite(glowa_k(gk, v), f"glowa-{v}-{gk:.2f}", rim=2, clean=False)
    M0.poloz(st, gl, zx, zy, p + 0.006, h=hh, anchor=(0.18, 0.5), rot=rot, sx=face, shadow=(3, 4, 5, 0.35))


def iks_k(k):
    """Czerwony krzyż (słownik znaków 1.20: wyrok, śmierć) z dwóch pasków papieru, w skali k."""
    def pasek(a):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        return poly([(100 + c * x - s_ * y, 100 + s_ * x + c * y) for x, y in ((-96, -15), (96, -13), (94, 15), (-95, 13))])
    parts = [(pasek(45), (196, 34, 30), dict(edge=2, contrast=1.2)), (pasek(-45), (210, 40, 34), dict(edge=2, contrast=1.2))]
    return Sprite(M0.stack_k(200, 200, parts, seed=91, k=k), f"iks-{k:.2f}", rim=2, clean=False)


def strzala_k(k):
    """Strzała wbita grotem (grotu nie widać): drzewce w prawo, lotki na końcu. Kotwica: lewy koniec (w ramieniu)."""
    parts = [(rect(0, 21, 300, 29), (156, 114, 72), dict(edge=1)),
             (poly([(240, 24), (296, 24), (310, 4), (262, 6)]), (238, 232, 220)), (poly([(240, 26), (296, 26), (310, 46), (262, 44)]),
                                                                                    (196, 52, 40)),
             (rect(294, 20, 304, 30), (60, 44, 36))]
    return Sprite(M0.stack_k(312, 50, parts, seed=93, k=k), f"strzala-{k:.2f}", rim=2, clean=False)


def kropla_k(k):
    """Kropla potu (słownik znaków: strach, nerwy) — błękitna łezka z białym odblaskiem."""
    parts = [(poly([(50, 0)] + [(50 + 34 * math.sin(a), 74 + 34 * math.cos(a)) for a in np.linspace(math.pi * 0.62, -math.pi * 0.62, 28)]),
              (96, 170, 232), dict(edge=4, contrast=1.1)),
             (ell(40, 82, 8, 13), (246, 250, 255), dict(kind="gladki"))]
    return Sprite(M0.stack_k(100, 112, parts, seed=95, k=k), f"kropla-{k:.2f}", rim=2, clean=False)


def slonce_k(k):
    """Wielkie słońce z papieru (promienie, tarcza) — za głową Iwarebiko jak aureola („Son of the Sun”)."""
    parts = []
    for n in range(18):
        a = 2 * math.pi * n / 18
        b = 0.09
        parts.append((poly([(200 + 120 * math.cos(a - b), 200 + 120 * math.sin(a - b)), (200 + 196 * math.cos(a), 200 + 196 * math.sin(a)),
                            (200 + 120 * math.cos(a + b), 200 + 120 * math.sin(a + b))]), (246, 196, 92) if n % 2 else (240, 172, 70)))
    parts += [(ell(200, 200, 134, 134), (232, 120, 52), dict(edge=3)), (ell(200, 200, 112, 112), (246, 176, 72), dict(kind="gladki")),
              (ell(186, 186, 70, 70), (252, 214, 120), dict(kind="gladki", contrast=0.6))]
    return Sprite(M0.stack_k(400, 400, parts, seed=97, k=k), f"slonce-mini-{k:.2f}", rim=2, clean=False)


def scena_c(st, K):
    """C: czterech braci, przeżył jeden — świt nad Yamato, wielkie słońce za Iwarebiko; trzej bracia przekreśleni
    czerwonymi krzyżami (najstarszy ze strzałą w ramieniu), Iwarebiko z kroplą potu: „AM I NEXT?!”."""
    w = S.stan(S.I["yamato"])
    w.sun = 0.0
    S.kraj(st, K["t"], w, niebieskie=1.0, wzgorza=1.0, slonce_k=0.0, tint=K["tint"], kul=False)
    sx, sy, sw = K["slonce"]
    M0.poloz(st, J.glow(), sx, sy, P.slonce - 0.001, w=sw * 2.2, anchor=(0.5, 0.5), mode="add", alpha=0.55, shadow=None, tint=(1.0, 0.8, 0.5))
    M0.poloz(st, slonce_k(max(1.0, sw / 400 * papier.Q)), sx, sy, P.slonce, w=sw, anchor=(0.5, 0.5), shadow=(5, 7, 9, 0.3))
    ki = max(1.0, papier.Q * 0.75)
    for key, x, h, rece, kat in K["bracia"]:
        postaw(st, key, x, S.STOPY, h, P.lalki - 0.01, rece, "krzyk", 5, rot=kat, kolor=(236, 224, 196), tint=K["szarosc"])
        if key == "itsuse":  # strzała w barku (ujęcie 13: przyszła ze wschodu, z prawej)
            s_ = h / (J.STOPA - J.CZUBEK)
            ax, ay = x + (182 - 150) * s_, S.STOPY - (J.STOPA - 232) * s_
            M0.poloz(st, strzala_k(max(1.0, papier.Q * 0.6)), ax, ay, P.lalki - 0.005, w=h * 0.34, anchor=(0.03, 0.5), rot=40,
                     shadow=(2, 3, 3, 0.4), tint=K["szarosc"])
        M0.poloz(st, iks_k(ki), x + 4, S.STOPY - h * 0.64, P.rekwizyty + 0.01, h=h * 0.52, anchor=(0.5, 0.5), rot=kat - 4,
                 shadow=(4, 6, 6, 0.45))
    ix, iy, ih = K["iwarebiko"]
    postaw(st, "iwarebiko", ix, iy, ih, P.lalki + 0.01, K["rece"], "krzyk", K["obrys"], palec=True, rot=-2)
    kx, ky, kh = K["kropla"]
    M0.poloz(st, kropla_k(max(1.0, kh / 112 * papier.Q)), kx, ky, P.lalki + 0.02, h=kh, anchor=(0.5, 0.5), rot=-14, shadow=(3, 4, 4, 0.35))


def scena_d(st, K):
    """D: wąż o ośmiu głowach w nocy nad Izumo — najbliższa głowa w zbliżeniu po lewej (paszcza, kły, język), siedem
    głów nad wzgórzami, po prawej mały Susanoo z mieczem nad głową: „8 HEADS?!”."""
    w = S.stan(S.I["orochi"])
    w.noc, w.sun, w.moon = K["noc"], 0.0, 1.0
    S.kraj(st, K["t"], w, rzeka=1.0, slonce_k=0.0, sosny=(0.0, 1.0), kul=False)  # bez wiśni: różowe kwiaty za szyją
    for n, (bx, hx, hy, hh) in enumerate(K["glowy"]):
        szyja_k(st, (bx, S.ziemia("srodek", bx) + 70), (hx, hy), hh, n % 3, P.miasto + 0.012 + 0.0015 * n, n)
    ux, uy, uh, lustro, rece = K["susanoo_d"]
    postaw(st, "susanoo", ux, uy, uh, P.lalki, rece, "krzyk", 6, rot=K.get("susanoo_kat_d", 4), miecz=True, lustro=lustro)
    bx_, by_ = K["bohater_xy"]
    kb = papier.Q
    spr, (ex, ey) = waz_bohater(kb, K)
    W_, H_ = K["bohater_ark"]
    M0.poloz_obrys(st, spr, bx_, by_, P.lalki + 0.01, H_, (0.0, 0.0), kolor=(252, 250, 244), gruby=K["obrys"], k=kb)
    M0.poloz(st, J.glow(), bx_ + ex * W_, by_ + ey * H_, P.lalki + 0.02, w=150, anchor=(0.5, 0.5), mode="add", alpha=0.75, shadow=None,
             tint=(1.0, 0.45, 0.2))


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
    {"A": scena_a, "B": scena_b, "C": scena_c, "D": scena_d}[WARIANT](st, K)

    if K.get("susanoo"):
        susanoo_z_wirem(st, K)
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


def susanoo_z_wirem(st, K):
    # Susanoo po lewej: wir wiatru za nim, gruby biały obrys, mina złości, palcem wskazuje łodzie, druga pięść w górze
    sx, sy, sh = K["susanoo"]
    wx, wy, ww = K["wir"]
    M0.poloz(st, wir_k(max(1.0, ww / 400 * papier.Q)), wx, wy, P.lalki + 0.004, w=ww, anchor=(0.5, 0.5), rot=K.get("wir_kat", -20),
             shadow=None, alpha=0.95)
    postaw(st, "susanoo", sx, sy, sh, P.lalki + 0.01, K["rece"], "zly", K["obrys"], palec=True, rot=K.get("susanoo_kat", -3),
           napis=K.get("napis"))
    zx, zy, zh = K["zylka"]
    M0.poloz(st, zylka_k(max(1.0, zh / 120 * papier.Q)), zx, zy, P.lalki + 0.02, h=zh, anchor=(0.5, 0.5), rot=12, shadow=(3, 4, 4, 0.35))


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
BAZA = {k: WSPOLNE[k] for k in ("kamera", "obrys", "szyld", "made_in")}
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
    # C i D — dwie zupełnie inne miniaturki do testu A/B (reżyser 21.11), z tym samym szyldem i „made in JAPAN” co A,
    # żeby test porównywał scenę, a nie markę. C pasuje do tytułu „Four Brothers Set Out to Rule Japan. Only One Survived.”,
    # D do „Japanese Mythology, Told in Paper Theatre”.
    "C": dict(BAZA, t=2.0, tint=(1.06, 0.9, 0.78), grade=(1.03, 0.98, 0.94),
              slonce=(330, 300, 470),  # środek i szerokość słońca za głową Iwarebiko
              iwarebiko=(300, 1250, 1000), rece=(100, 0),  # przednia wskazuje braci, tylna schowana za plecami
              kropla=(378, 292, 72),
              bracia=(("itsuse", 700, 400, (25, 0), -3), ("brat2", 905, 385, (160, 200), 3), ("brat3", 1100, 370, (150, 190), -2)),
              szarosc=(0.8, 0.8, 0.86),
              tabliczki={{"en": "AM I NEXT?!", "pl": "JA NASTĘPNY?!"}[JEZ]: (575, 150, 64, 5)}),
    "D": dict(BAZA, t=2.0, noc=0.6, grade=(0.84, 0.88, 1.02),
              # siedem głów za wzgórzami: nasada x, głowa x, y, wysokość głowy
              glowy=((560, 500, 250, 84), (660, 640, 175, 80), (780, 780, 250, 84), (880, 900, 175, 78), (1000, 1060, 230, 84),
                     (1130, 1190, 180, 76), (1230, 1240, 300, 80)),
              bohater_ark=(920, 560), bohater_xy=(-60, 200), bohater_szyja=((150, 620), (40, 360), (250, 250)),
              bohater_skala=2.1, bohater_kat=8,
              susanoo_d=(1040, 708, 400, True, (145, 25)),  # x, y stóp, wysokość, twarzą w lewo, ręce (miecz w górze)
              tabliczki={{"en": "8 HEADS?!", "pl": "8 GŁÓW?!"}[JEZ]: (1110, 36, 62, -5)}),
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
