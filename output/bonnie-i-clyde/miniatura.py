"""Miniaturki „Bonnie and Clyde” na YouTube (EN), złożone silnikiem teatru z wycinków filmu, w układzie zatwierdzonej miniaturki
„Pierwszego cesarza” (docs/WYTYCZNE_UJEC.md, sekcja 5): duże postacie z grubym białym obrysem, tabliczki z okrzykiem, szyld
z tytułem u góry, 4K i wygląd zdjęcia Fujifilm. Funkcje tabliczki, szyldu, obrysu i nitek bierzemy z
output/pierwszy-cesarz/miniatura.py (gałąź film/pierwszy-cesarz), tak jak „Syn słońca”.

Reżyser 24.11.2026: „cała maszyna wydawania na YT: miniaturki trzy, trzy tytuły według obowiązujących trendów… na pewno jeden
tytuł musi być coś z GTA 6”. Każda miniaturka idzie w parze z jednym tytułem (test A/B, publikacja/PUBLIKACJA.md):
  A — „Before GTA 6: The REAL Bonnie and Clyde Ending”: zasadzka w Luizjanie o świcie — podziurawiony Ford w dymie, z lewej
      Hamer z karabinem w zbliżeniu, tabliczka „THE REAL ENDING”, „1934”;
  B — „One Joke Photo Made Bonnie & Clyde America's Most Hunted Couple”: Bonnie w zbliżeniu z cygarem i rewolwerem pozuje
      do zdjęcia, flesz, obok gazeta „OUTLAW GIRL WITH CIGAR”, tabliczka „IT WAS A JOKE!”;
  C — „The ENTIRE Bonnie and Clyde Story in 18 Minutes”: Bonnie i Clyde w zbliżeniu przed Fordem na drodze przez prerię,
      zza krawędzi wygląda Hamer, tabliczki „THE WHOLE STORY” i „18 MIN”.
Bez grafik z GTA 6 (znak towarowy) — gra jest tylko w tytule.
Reżyser 25.11.2026 (po 18 h: CTR 2,1 %, „musimy coś zrobić z miniaturkami, stworzyć jeszcze dwie różne do testów A/B”) —
zbliżenia twarzy z miną na ciemnym tle, jak miniaturki z najlepszą klikalnością kanału:
  E — zasadzka z bliska: Clyde i Bonnie do pasa, przerażeni, ręce w górze; w sosnach łowcy w krzakach, błyski z luf, „AMBUSH!”;
  F — Bonnie mruga z cygarem i rewolwerem na przyciemnionych gazetach, flesz aparatu, „IT WAS A JOKE!” (zapas);
  G — to samo w ciemni w czerwonym świetle („jedną miniaturkę zrób z tą ciemnią, tam gdzie jest to czerwone tło”).

  WARIANT=A python3 miniatura.py                → miniatura/miniatura_A_en.jpg i .png (1280 × 720, szybki podgląd: JAKOSC=1)
  ROZMIAR=3840 WARIANT=A python3 miniatura.py   → 4K dla YouTube: miniatura_A_en_4k.png i _4k.jpg (+ 1280 × 720 z tego rysunku)
  MOC=0.5 JASNOSC=0.07 python3 ../pierwszy-cesarz/fujifilm.py miniatura/miniatura_A_en_4k.png 1280 → wygląd Fujifilm (5.4)
"""
import importlib.util
import math
import os
import random
import sys
from functools import lru_cache
from pathlib import Path

os.environ["JEZYK"] = "en"
HERE = Path(__file__).resolve().parent
CESARZ = HERE.parent / "pierwszy-cesarz"
sys.path.insert(0, str(HERE))
sys.path.append(str(CESARZ))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/bonnie-i-clyde/ujecia"))

import papier  # noqa: E402

ROZMIAR = int(os.environ.get("ROZMIAR", "0"))
papier.Q = ROZMIAR / 1280 if ROZMIAR else float(os.environ.get("JAKOSC", "2"))

from PIL import Image  # noqa: E402

import scena as S  # noqa: E402
import zestaw_bc as J  # noqa: E402
from papier import Cam, Sprite, Stage  # noqa: E402

sys.argv = [sys.argv[0], "en"]  # miniatura „Cesarza” czyta język z argumentu
_spec = importlib.util.spec_from_file_location("miniatura_cesarza", CESARZ / "miniatura.py")
M0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M0)  # poloz, nitki, tabliczka, szyld, poloz_obrys, wyrownaj

P = J.P
OUT = HERE / "miniatura"
WARIANT = os.environ.get("WARIANT", "A").upper()
TYTUL = "BONNIE & CLYDE"
K_TAB = papier.Q  # tabliczki i szyld: w 4K trzykrotnie
BIALY = (252, 250, 244)


def _rozkrok(body, s, ang):
    """Korpus lalki z nogami w rozkroku: nogi (od dołu marynarki albo spódnicy) rozcięte w kroku i obrócone na boki o ang
    stopni wokół bioder; góra kładzie się na wierzch, więc szew pod biodrami nie widać. Tylko do miniaturki — arkusze lalek
    w filmie zostają z nogami razem."""
    from PIL import Image as _I
    W_, H_ = body.size
    cx = W_ / 2
    sy = int((566 if s["kobieta"] else 452) + s["nogi"])
    out = _I.new("RGBA", body.size, (0, 0, 0, 0))
    for strona, kat in ((-1, -ang), (1, ang)):
        noga = _I.new("RGBA", body.size, (0, 0, 0, 0))
        x0, x1 = (0, int(cx)) if strona < 0 else (int(cx), W_)
        noga.paste(body.crop((x0, sy, x1, H_)), (x0, sy))
        out.alpha_composite(noga.rotate(kat, resample=_I.BICUBIC, center=(cx + strona * 26, sy)))
    gora = _I.new("RGBA", body.size, (0, 0, 0, 0))
    gora.paste(body.crop((0, 0, W_, sy + 8)), (0, 0))
    out.alpha_composite(gora)
    return out


@lru_cache(None)
def postac(key, rece=(20.0, 10.0), lean=0.0, rzecz=None, rozkrok=0.0):
    """Lalka filmu w pozie, w kolorach (zestaw_bc.sylwetka(kolor=True)) — jeden wycinek, który dostaje biały obrys.
    rozkrok — kąt nóg na boki (reżyser 24.11: „zrób ich w rozkroku, Bonnie i Clyde'a”)."""
    korpus = J._korpus_img
    if rozkrok:
        J._korpus_img = lambda sp, seed_spec=None: _rozkrok(korpus(sp, seed_spec), sp, rozkrok)
    try:
        img = J.sylwetka(key, rece=rece, lean=lean, rzecz=rzecz, kolor=True)
    finally:
        J._korpus_img = korpus
    return Sprite(img, f"miniatura-{key}-{rece}-{lean}-{rzecz}-{rozkrok}", rim=2, clean=False)


def obrys(st, spr, x, y, h, p=P.lalki + 0.01, anchor=(0.5, 1.0), gruby=9, **kw):
    """Postać z grubym białym obrysem w punkcie ekranu (x, y), wysoka na h pikseli ekranu 1280 × 720."""
    M0.poloz_obrys(st, spr, x, y, p, h, anchor, kolor=BIALY, gruby=gruby, k=max(1.0, papier.Q), **kw)


def tab(st, txt, x, y, h, rot=0.0, size=64, xs=(0.2, 0.8), p=P.rekwizyty + 0.03):
    M0.nitki(st, M0.tabliczka(txt, size, K_TAB), x, y, p, h=h, xs=xs, rot=rot)


def szyld(st, x=40, y=26, h=78, maxw=520):
    sz = M0.szyld(TYTUL, k=K_TAB)
    h = min(h, maxw * sz.h / sz.w)
    M0.nitki(st, sz, x + 0.5 * h * sz.w / sz.h, y, 0.95, h=h, xs=(0.1, 0.9), rot=-0.8)


def scena_poczatek(i_ujecia):
    """Stage z kamerą bez paralaksy (kadr wzorcowy 1:1), świat z ujęcia filmu, dekoracja już stoi."""
    st = Stage(0.0, seed=7)
    st.T = 1.0
    st.cam = Cam(640, 360, 1.0, 0.5, lens=1.0, truck=0.0)
    st.focus, st.dof = P.lalki, 0.5
    S.BUDOWA["t"] = None
    return st, S.stan(S.I[i_ujecia])


def dym(st, x, y, n=7, h=110, seed=3):
    """Dym znad auta — za karoserią (plan dalszy niż auto), więc okna i pasażerowie zostają widoczni."""
    r = random.Random(seed)
    for k in range(n):
        st.put(J.rek("oblok"), x + r.uniform(-170, 170), y - r.uniform(0, 150), P.auta - 0.01 + 0.0005 * k, h=h * r.uniform(0.7, 1.3),
               anchor=(0.5, 0.5), rot=r.uniform(0, 360), tint=(0.7, 0.68, 0.66), alpha=0.6, shadow=None)


def scena_a():
    """Zasadzka pod Gibsland, 23 maja 1934 o świcie (ujęcie „zasadzka”): podziurawiony Ford, dym, Hamer z karabinem."""
    st, w = scena_poczatek("zasadzka")
    S.las(st, 0.0, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=1.0, kul=False)
    S.auto(st, 0.0, 860, 300, y=S.DROGA_Y - 10, dziury=90, przechyl=4, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    dym(st, 980, 360, seed=4)
    S.rampa(st)
    hamer = postac("hamer", rece=(92.0, 70.0), lean=-4.0, rzecz=("karabin", 46, (0.3, 0.55)))
    obrys(st, hamer, 250, 760, 610)
    tab(st, "THE REAL ENDING", 905, 150, 82, rot=2.5)
    tab(st, "1934", 1150, 300, 64, rot=-5, xs=(0.5,))
    tab(st, "?!", 800, 330, 58, rot=4, xs=(0.5,))
    szyld(st)
    st.grade = (1.03, 0.98, 0.92)
    return st


def scena_b():
    """Zdjęcie dla żartu (ujęcie „zdjecie”): Bonnie z cygarem i rewolwerem pozuje, z prawej błyska flesz aparatu, a niżej leży
    gazeta, która zrobiła z tego zdjęcia legendę."""
    st, w = scena_poczatek("zdjecie")
    S.teatr_gazet(st, 0.0, w)
    gz = J.gazeta("CIGAR GIRL!", 9, 360, 480)
    M0.poloz_obrys(st, Sprite(gz.mips[0], "gazeta-miniatura", rim=2, clean=False), 930, 470, P.lalki - 0.01, 420, (0.5, 0.5),
                   kolor=BIALY, gruby=7, k=1.0, rot=8)
    st.put(J.glow(), 1190, 300, P.rekwizyty, w=820, anchor=(0.5, 0.5), mode="add", alpha=0.8, shadow=None, tint=(1.0, 0.96, 0.85))
    st.put(J.rek("aparat_lampa"), 1185, 330, P.rekwizyty + 0.005, h=150, anchor=(0.5, 0.5), rot=-10, sx=-1)
    bonnie = postac("bonnie_cygaro", rece=(118.0, 25.0), lean=-4.0, rzecz=("rewolwer", 40, (0.3, 0.75)))
    obrys(st, bonnie, 400, 780, 660)
    tab(st, "IT WAS A JOKE!", 960, 60, 84, rot=3)
    tab(st, "SNAP!", 1160, 175, 58, rot=-6, xs=(0.5,))
    szyld(st)
    st.grade = (1.04, 0.99, 0.92)
    return st


def scena_c():
    """Cała historia: Bonnie i Clyde przed Fordem na drodze przez prerię, zza prawej krawędzi wygląda Hamer."""
    st, w = scena_poczatek("drzewo")
    S.preria(st, 0.0, w, slupy=True, kul=False, tablice=[("TEXAS", 160)])
    S.auto(st, 0.0, 700, 270, y=S.DROGA_Y - 30)
    S.rampa(st)
    obrys(st, postac("hamer", rece=(30.0, 10.0), lean=-12.0), 1235, 760, 520, p=P.lalki - 0.002)
    obrys(st, postac("clyde", rece=(30.0, 20.0), rzecz=("karabin", 46, (0.3, 0.55))), 800, 780, 600, p=P.lalki + 0.012)
    obrys(st, postac("bonnie", rece=(160.0, 20.0), rzecz=("rewolwer", 40, (0.3, 0.75))), 470, 780, 560, p=P.lalki + 0.014)
    tab(st, "THE WHOLE STORY", 905, 60, 76, rot=2)
    tab(st, "18 MIN", 170, 250, 64, rot=-4, xs=(0.5,))
    tab(st, "HMM…", 1160, 170, 52, rot=5, xs=(0.5,))
    szyld(st)
    st.grade = (1.03, 0.99, 0.93)
    return st


# Bonnie w białej sukni ślubnej i czerwonym berecie — wariant tylko do miniaturki D (w filmie takiej lalki nie ma)
J.LALKI["bonnie_slub_beret"] = dict(J.LALKI["bonnie_slub"], kapelusz="beret", kapelusz_kolor=(150, 40, 46))


def kule_w_tle(st, n=26, seed=11):
    """Pociski przelatujące przez całe tło: kula z jasną smugą za sobą, pod różnymi kątami (jak kule w ujęciach 13 i 78)."""
    r = random.Random(seed)
    for k in range(n):
        x, y = r.uniform(40, 1240), r.uniform(150, 470)
        kat = r.choice((r.uniform(-25, 25), 180 + r.uniform(-25, 25)))
        dl = r.uniform(70, 150)
        dx, dy = math.cos(math.radians(kat)), math.sin(math.radians(kat))
        p = P.miasto + 0.02 + 0.0004 * k
        st.line([(x - dx * dl, y - dy * dl), (x, y)], p, width=3.2, color=(255, 236, 190), alpha=0.75)
        st.put(J.glow(r=256, color=(255, 220, 150)), x, y, p, w=26, anchor=(0.5, 0.5), mode="add", alpha=0.9, shadow=None)
        st.put(J.rek("kula"), x, y, p + 0.0002, h=9, anchor=(0.5, 0.5), rot=kat, shadow=None)


def strzal(st, x, y, kierunek, p, wielkosc=1.0):
    """Błysk z lufy (strzał z końca lufy, 1.20) i krótka smuga kuli w kierunku strzału."""
    st.put(J.glow(r=256, color=(255, 200, 110)), x, y, p, w=150 * wielkosc, anchor=(0.5, 0.5), mode="add", alpha=0.95, shadow=None)
    st.put(J.glow(r=256, color=(255, 250, 230)), x, y, p + 0.0005, w=46 * wielkosc, anchor=(0.5, 0.5), mode="add", alpha=1.0, shadow=None)
    st.line([(x + kierunek * 30, y), (x + kierunek * 160 * wielkosc, y - 6)], p, width=4, color=(255, 236, 190), alpha=0.8)


def kotwica_tulowia(key, spr, rozkrok=0.0):
    """Kotwica x środka tułowia w wycinku postaci z wyciągniętą ręką (wycinek jest przycięty do całej sylwetki, więc jego
    środek leży w stronę ręki): szerokość lalki z rękami w dół to tułów, który zaczyna się przy lewej krawędzi."""
    wn = postac(key, rece=(0.0, 0.0), rozkrok=rozkrok).w
    return (wn / 2) / spr.w


def stoi(st, key, x, y, h, p, rece, rzecz, flip=1.0, rot=0.0, gruby=9, rozkrok=0.0):
    """Postać z białym obrysem, która stoi stopami w (x, y) ekranu niezależnie od wyciągniętej ręki."""
    spr = postac(key, rece=rece, rzecz=rzecz, rozkrok=rozkrok)
    ax = kotwica_tulowia(key, spr, rozkrok)
    M0.poloz_obrys(st, spr, x, y, p, h, (ax if flip > 0 else ax, 1.0), kolor=BIALY, gruby=gruby, k=max(1.0, papier.Q), sx=flip, rot=rot)


def na_aucie(u, v):
    """Punkt arkusza Forda (900 × 360: dach 300–560 × 70, przednia szyba do (600, 150), maska do (800, 168)) na ekranie, dla auta
    z AUTO_D obróconego o ROT_AUTA wokół środka (te same wzory co scena.auto i ujecia_a.auto_srodek)."""
    from scena import _off
    cx, cy, ah = AUTO_D
    k = ah / 360.0
    ox, oy = _off(0, -ah * 0.5, ROT_AUTA)
    x0, y0 = cx - ox, cy - oy  # kotwica auta: środek linii kół
    dx, dy = _off((u - 450) * k, (v - 356) * k, ROT_AUTA)
    return x0 + dx, y0 + dy


def tabliczka_gruba(txt, size=64, k=1.0):
    """Tabliczka jak M0.tabliczka, ale litery Baskerville Bold (reżyser 24.11: „napis po prawej minimalnie grubsze litery”)."""
    from PIL import ImageFont
    Z = M0.Z
    f = ImageFont.truetype(Z.FONT_PL, size * 2, index=1)
    tw = int(f.getlength(txt) / 2)
    w, h = tw + 64, size + 44
    parts = [(Z.poly([(4, 4), (w - 4, 4), (w - 4, h - 4), (4, h - 4)]), (240, 226, 194), dict(kind="gladki", edge=4, contrast=1.3)),
             (Z.glyphs(txt, size, Z.FONT_PL, 1, (w / 2, h / 2 + 2), "mm"), (44, 26, 20), dict(kind="gladki", rough=0.5))]
    return Sprite(M0.stack_k(w, h, parts, seed=len(txt), k=k), f"zawieszka-gruba-{txt}-{k:.2f}", rim=round(2 * k), clean=False)


@lru_cache(None)
def kaktus(v=0):
    """Saguaro z zielonego papieru: pień i dwa ramiona (tło miniaturki D, za słupami — reżyser 24.11: „z 3 kaktusy w tle,
    rozmyte”)."""
    r = random.Random(40 + v)
    w, h = 220, 420
    zl, ciemny = (92, 126, 74), (70, 100, 58)
    lo, po = r.uniform(150, 230), r.uniform(120, 200)
    parts = [(J.rect(86, 30, 134, 420), zl, dict(edge=2)), (J.ell(110, 34, 24, 24), zl),
             (J.rect(30, lo, 86, lo + 34), zl), (J.rect(30, lo - 90, 62, lo + 30), zl, dict(edge=2)), (J.ell(46, lo - 92, 16, 16), zl),
             (J.rect(134, po, 186, po + 34), zl), (J.rect(156, po - 100, 188, po + 30), zl, dict(edge=2)), (J.ell(172, po - 102, 16, 16), zl)]
    parts += [(J.rect(108, 50, 112, 410), ciemny)]
    return Sprite(J.stack(w, h, parts, seed=800 + v), f"kaktus-{v}", rim=2, clean=False)


def kapelusz_w_dloni(key):
    """Nakrycie głowy lalki jako rekwizyt do sylwetki (ten sam kształt i kolor co na głowie, w skali arkusza lalki) i lalka
    bez niego — łowcy na miniaturce D trzymają zdjęte kapelusze w uniesionej dłoni (reżyser 24.11)."""
    nazwa = f"kap_{key}"
    if nazwa not in J.REKWIZYTY:
        sp = J.spec(key)
        def czesci(sp=sp):
            p = []
            J._kapelusz(sp, p)  # dopisuje części kapelusza do listy (zwraca None)
            return p
        J.REKWIZYTY[nazwa] = (300, 120, czesci)
        J.LALKI[key + "_bez"] = dict(J.LALKI[key], kapelusz=None)
    return key + "_bez", (nazwa, 120, (0.51, 0.82))


def scena_d():
    """Ostatnia scena jako plakat (reżyser 24.11.2026): na pierwszym planie sześciu łowców w małych krzakach z ujęcia 104 —
    widać tylko kapelusze i oczy; za nimi cały podziurawiony Ford zapadnięty tyłem w rowie, przodem do góry; Bonnie (biała
    suknia ślubna, czerwony beret) stoi na opadającym dachu i strzela w lewo, Clyde stoi na przedniej szybie, jedną nogą na
    masce, i strzela w prawo; w tle Teksas, pełno pocisków, z krzaków lecą kule w auto, na karoserii iskry trafień, spod tylnego
    koła lecą grudy ziemi, za parą ciepła poświata świtu. W filmie nie zdążyli strzelić (kwestia „dym”) — na miniaturce to
    plakatowa przesada, za zgodą reżysera."""
    from ujecia_a import auto_srodek
    st, w = scena_poczatek("drzewo")
    S.preria(st, 0.0, w, slupy=True, kul=False, tablice=[("TEXAS", 1170)])
    for n, (x, hh) in enumerate(((235, 170), (95, 135), (1000, 185))):  # kaktusy w tle, za słupami, rozmyte
        M0.poloz(st, kaktus(n), x, 575, P.gory + 0.006, h=hh, anchor=(0.5, 1.0), blur=2.6, haze=0.22, shadow=None)
    kule_w_tle(st)
    cx, cy, ah = AUTO_D
    # poświata świtu za parą: postacie odcinają się od nieba (jak słońce za Iwarebiko w „Synu słońca”, miniaturka C)
    st.put(J.glow(r=256, color=(255, 214, 150)), cx - 10, cy - 240, P.auta - 0.03, w=760, anchor=(0.5, 0.5), mode="add", alpha=0.42,
           shadow=None)
    auto_srodek(st, 0.0, cx, cy, ah, ROT_AUTA, dziury=110, p=P.auta - 0.02)
    # grudy ziemi z rowu pod tylnym kołem
    r = random.Random(5)
    tx, ty = na_aucie(232, 330)
    for n in range(9):
        st.put(J.rek("plama"), tx - 40 - r.uniform(0, 150), ty - r.uniform(10, 120), P.auta - 0.015, h=r.uniform(10, 20), anchor=(0.5, 0.5),
               rot=r.uniform(0, 360), tint=(0.55, 0.42, 0.28), shadow=None)
    # iskry trafień na karoserii
    for u, v in ((380, 230), (520, 200), (700, 200), (820, 230), (300, 250), (640, 250)):
        ix, iy = na_aucie(u, v)
        st.put(J.glow(r=256, color=(255, 210, 120)), ix, iy, P.auta - 0.018, w=46, anchor=(0.5, 0.5), mode="add", alpha=0.95, shadow=None)
    # Bonnie na opadającym dachu, Clyde na przedniej szybie z jedną nogą na masce (stopy z geometrii auta)
    bx, by = na_aucie(*STOPY_D[0])
    kx, ky = na_aucie(*STOPY_D[1])
    stoi(st, "bonnie_slub_beret", bx, by + 4, 300, P.auta - 0.005, (90.0, 10.0), ("rewolwer", 40, (0.3, 0.75)), flip=-1, rot=ROT_AUTA * 0.35,
         rozkrok=ROZKROK[0])
    stoi(st, "clyde", kx, ky + 4, 330, P.auta - 0.004, (88.0, 10.0), ("karabin", 50, (0.3, 0.55)), rot=ROT_AUTA * 0.55, rozkrok=ROZKROK[1])
    for (sx_, sy_, kier, wk) in STRZALY_D:
        strzal(st, sx_, sy_, kier, P.auta, wk)
    # kule z krzaków w stronę auta (smugi od łowców ku karoserii)
    for n, (x0, (u, v)) in enumerate(((300, (380, 230)), (495, (520, 200)), (785, (700, 200)), (980, (820, 230)))):
        ix, iy = na_aucie(u, v)
        f0 = 0.35 + 0.1 * n
        st.line([(lerp_(x0, ix, f0), lerp_(600, iy, f0)), (lerp_(x0, ix, f0 + 0.3), lerp_(600, iy, f0 + 0.3))], P.lalki + 0.01, width=3,
                color=(255, 236, 190), alpha=0.75)
    # pierwszy plan: sześciu łowców nisko w małych krzakach z ujęcia 104 (J.krzak(n), barwa z filmu) — kapelusze, oczy, lufy
    # łowcy wynurzeni o ok. 10 % wyżej; każdy trzyma zdjęty kapelusz w dłoni uniesionej z boku pod kątem 45° (reżyser 24.11)
    for n, ((key, _), x) in enumerate(zip(LOWCY_MIN, (90, 300, 495, 785, 980, 1190))):
        fl = 1 if x < 640 else -1
        bez, kap = kapelusz_w_dloni(key)
        spr = postac(bez, rece=(135.0, 10.0), rzecz=kap)
        ax = kotwica_tulowia(bez, spr)
        # biały obrys (cieńszy niż u Bonnie i Clyde'a): kapelusze w dłoniach odcinają się od pola (reżyser 24.11: „czapki
        # bardziej odznacz, może biała obwódka”)
        M0.poloz_obrys(st, spr, x, 822, P.lalki + 0.02 + 0.001 * n, 300, (ax, 1.0), kolor=BIALY, gruby=6, k=max(1.0, papier.Q), sx=fl,
                       rot=-6 * fl, tint=(0.84, 0.84, 0.82))
    for n, x in enumerate((20, 175, 330, 485, 640, 795, 950, 1105, 1260)):
        M0.poloz(st, J.krzak(n % 6), x, 728, P.lalki + 0.03 + 0.001 * n, h=118, anchor=(0.5, 1.0))
    M0.nitki(st, tabliczka_gruba("THE REAL ENDING", 64, K_TAB), 1030, 14, P.rekwizyty + 0.03, h=64, xs=(0.2, 0.8), rot=2)
    tab(st, "BANG!", 170, 250, 54, rot=-8, xs=(0.5,))
    tab(st, "BANG!", 1150, 210, 54, rot=7, xs=(0.5,))
    szyld(st, x=22, y=12, h=SZYLD_D, maxw=820)  # reżyser 24.11: „dużo większy napis Bonnie i Clyde”
    st.grade = (1.05, 0.98, 0.9)
    return st


def lerp_(a, b, f):
    return a + (b - a) * f


ROT_AUTA = -16  # przód auta w górę (tył w rowie)
AUTO_D = (640, 518, 300)  # środek auta na ekranie i jego wysokość; nisko: tylne koło chowa się w krzakach (reżyser 24.11)
STOPY_D = ((385, 72), (598, 150))  # stopy na arkuszu Forda: Bonnie na dachu, Clyde na dole przedniej szyby, przy masce
STRZALY_D = ((408, 240, -1, 1.0), (950, 202, 1, 1.1))  # (x, y, kierunek, wielkość) błysków z końców luf
ROZKROK = (24.0, 13.0)  # kąt nóg na boki: Bonnie (spódnica), Clyde
SZYLD_D = 142  # wysokość szyldu z tytułem (w C i A–B 78; reżyser 24.11: „dużo większy”, potem „jeszcze troszkę większy”)
LOWCY_MIN = (("hamer", ""), ("gault", ""), ("alcorn", ""), ("hinton", ""), ("jordan", ""), ("oakley", ""))


# ---------- E i F: zbliżenia twarzy z miną (przepis „Syna słońca” i „Pierwszego cesarza”) ----------
# 25.11.2026, po pierwszych 18 h: CTR 2,1 % przy 3,2 % „Syna słońca”. Miniaturki C i D to plan ogólny w beżach — w 320 px
# nie widać twarzy. Miniaturki z najlepszą klikalnością kanału mają dużą twarz z miną do pasa w kadrze i ciemne, mocne tło.
# Lalki są rysowane od nowa w skali ekranu: _korpus_img i _ramie_img z zestaw_bc liczone przez zamienniki stack / Image /
# ImageDraw / ImageFilter w skali k (zestaw_bc.py zostaje nietknięty — 5.3).

import types  # noqa: E402
from contextlib import contextmanager  # noqa: E402

from PIL import ImageDraw, ImageFilter, ImageOps  # noqa: E402


class _DrawK:
    """ImageDraw.Draw, który mnoży współrzędne i grubości linii przez k."""

    def __init__(self, im, k):
        self.d, self.k = ImageDraw.Draw(im), k

    def _xy(self, xy):
        xy = list(xy)
        if xy and isinstance(xy[0], (tuple, list)):
            return [(x * self.k, y * self.k) for x, y in xy]
        return [v * self.k for v in xy]

    def _kw(self, kw):
        if "width" in kw:
            kw["width"] = max(1, round(kw["width"] * self.k))
        return kw

    def line(self, xy, **kw):
        self.d.line(self._xy(xy), **self._kw(kw))

    def ellipse(self, xy, **kw):
        self.d.ellipse(self._xy(xy), **self._kw(kw))

    def polygon(self, xy, **kw):
        self.d.polygon(self._xy(xy), **self._kw(kw))

    def arc(self, xy, a0, a1, **kw):
        self.d.arc(self._xy(xy), a0, a1, **self._kw(kw))


class _ImageK:
    def __init__(self, k):
        self.k = k

    def __getattr__(self, n):
        return getattr(Image, n)

    def new(self, mode, size, color=0):
        return Image.new(mode, (round(size[0] * self.k), round(size[1] * self.k)), color)


@contextmanager
def _skala(k):
    stare = J.stack, J.Image, J.ImageDraw, J.ImageFilter
    J.stack = lambda w, h, parts, seed=0: M0.stack_k(w, h, parts, seed=seed, k=k)
    J.Image = _ImageK(k)
    J.ImageDraw = types.SimpleNamespace(Draw=lambda im: _DrawK(im, k))
    J.ImageFilter = types.SimpleNamespace(GaussianBlur=lambda r: ImageFilter.GaussianBlur(r * k))
    try:
        yield
    finally:
        J.stack, J.Image, J.ImageDraw, J.ImageFilter = stare


def twarz(im, s, k, ox, oy, mina):
    """Mina na arkuszu korpusu (ox, oy — gdzie leży arkusz na obrazie, w jednostkach arkusza). Najpierw skóra zakrywa oczy
    i usta z filmu, potem:
      krzyk — brwi wysoko, oczy szeroko z małymi źrenicami, usta „O” (zasadzka: „to już?!”);
      chytra — jedno oko mruga (łuk), drugie szeroko, brew uniesiona, krzywy uśmiech (Bonnie do zdjęcia z cygarem);
      twardy — oczy przymrużone, brwi w „V”, usta prosto (Hamer)."""
    q = lambda pts: [((ox + x) * k, (oy + y) * k) for x, y in pts]
    W = lambda n: max(1, round(n * k))
    d = ImageDraw.Draw(im)
    ink = J.INK + (255,)
    sk, hair = s["skora"], s["wlosy"]
    brew = J._shade(hair, 0.8) + (255,)
    d.ellipse(q([(126, 108), (184, 136)]), fill=sk + (255,))  # oczy i brwi z filmu
    if not (s["wasy"] or s["broda"]):
        d.ellipse(q([(156, 154), (184, 168)]), fill=sk + (255,))  # usta z filmu
    oczy = ((137, 124, 8.5, 7.0), (171, 122, 8.0, 7.0))
    bialko = (250, 246, 236, 255)
    if mina == "krzyk":
        for cx, cy, rx, ry in oczy:
            d.ellipse(q([(cx - rx, cy - ry - 2), (cx + rx, cy + ry + 1)]), fill=bialko, outline=ink, width=W(2))
            d.ellipse(q([(cx + 1 - 2.4, cy - 2.4), (cx + 1 + 2.4, cy + 2.4)]), fill=ink)
            d.arc(q([(cx - rx - 2, cy - ry - 16), (cx + rx + 2, cy - ry + 0)]), 200, 340, fill=brew, width=W(3.5))
        usta = q([(162, 158), (180, 184)])
        d.ellipse(usta, fill=(96, 22, 20, 255), outline=ink, width=W(2))
        if s["kobieta"]:
            d.ellipse(usta, outline=(180, 40, 50, 255), width=W(3))
    elif mina == "chytra":
        (cx, cy, rx, ry), (cx2, cy2, rx2, ry2) = oczy
        d.arc(q([(cx - rx, cy - 6), (cx + rx, cy + 8)]), 195, 345, fill=ink, width=W(3))  # mrugnięcie
        d.line(q([(cx - rx - 2, cy - 10), (cx + rx + 2, cy - 8)]), fill=brew, width=W(3.5))
        d.ellipse(q([(cx2 - rx2, cy2 - ry2 - 1), (cx2 + rx2, cy2 + ry2)]), fill=bialko, outline=ink, width=W(2))
        d.ellipse(q([(cx2 + 1.5 - 3, cy2 - 2), (cx2 + 1.5 + 3, cy2 + 4)]), fill=ink)
        d.arc(q([(cx2 - rx2 - 2, cy2 - ry2 - 16), (cx2 + rx2 + 2, cy2 - ry2 + 0)]), 200, 340, fill=brew, width=W(3.5))
        if s["kobieta"]:
            for o in (0, 1):  # krzywy uśmiech: kącik przy cygarze wyżej
                d.line(q([(158, 164 - o), (168, 167 - o), (180, 158 - o)]), fill=(180, 40, 50, 255), width=W(5), joint="curve")
            if s["kobieta"] and s.get("_cygaro"):
                pass
        else:
            d.line(q([(158, 164), (168, 167), (180, 158)]), fill=ink, width=W(3), joint="curve")
    else:  # twardy
        for n, (cx, cy, rx, ry) in enumerate(oczy):
            d.ellipse(q([(cx - rx, cy - ry + 3), (cx + rx, cy + ry - 1)]), fill=bialko, outline=ink, width=W(2))
            d.ellipse(q([(cx + 1.5 - 2.6, cy - 1), (cx + 1.5 + 2.6, cy + 4.2)]), fill=ink)
            d.line(q([(cx - rx - 1, cy - 2), (cx + rx + 1, cy - 2)]), fill=ink, width=W(3))
        d.polygon(q([(124, 108), (128, 103), (151, 114), (148, 120)]), fill=brew)
        d.polygon(q([(160, 119), (157, 113), (182, 101), (186, 106)]), fill=brew)
        d.line(q([(151, 106), (153, 114)]), fill=J._shade(sk, 0.7) + (220,), width=W(2))
        if not (s["wasy"] or s["broda"]):
            d.line(q([(160, 164), (180, 163)]), fill=ink, width=W(3))
    if s.get("_cygaro"):  # cygaro w kąciku ust, żarzący się koniec
        d.line(q([(176, 160), (220, 148)]), fill=(96, 62, 40, 255), width=W(8))
        d.line(q([(216, 149), (223, 147)]), fill=(232, 110, 60, 255), width=W(8))
        d.line(q([(219, 140), (226, 120), (220, 104)]), fill=(214, 210, 204, 150), width=W(3), joint="curve")
    return im


def postac_k(key, k, rece=(0.0, 0.0), rzecz=None, mina="krzyk", lustro=False, cygaro=False):
    """Cała lalka w jednym arkuszu w skali k (ręce na zawiasach w barkach, przednia przed korpusem), twarzą w prawo;
    rzecz = (rekwizyt, wysokość w jednostkach arkusza, kotwica chwytu) w przedniej dłoni (jak zestaw_bc.sylwetka).
    Zwraca (wycinek, kotwica stóp jako ułamek wycinka, wysokość wycinka / wysokość postaci)."""
    s = dict(J.spec(key), szer=1.0, oczy="brak", cygaro=False)
    M, TOP = 330, 330
    CW, CH = J.FIG_W + 2 * M, J.FIG_H + s["nogi"] + TOP + 40
    im = Image.new("RGBA", (round(CW * k), round(CH * k)), (0, 0, 0, 0))
    with _skala(k):
        body, arm = J._korpus_img(s), J._ramie_img(s)
    zx, zy = J.RAMIE_ZAWIAS
    dl = J.DLON[1] - zy

    def reka(name, ang):
        bx, by = J.BARK[name]
        bx, by = (M + bx) * k, (TOP + by) * k
        L = Image.new("RGBA", im.size, (0, 0, 0, 0))
        L.alpha_composite(arm, (round(bx - zx * k), round(by - zy * k)))
        L = L.rotate(ang, resample=Image.BICUBIC, center=(bx, by))
        if name == "przod" and rzecz:
            a = math.radians(ang)
            hx, hy = bx + math.sin(a) * dl * k, by + math.cos(a) * dl * k
            nm, rh, anc = rzecz
            rw, rh_, fn = J.REKWIZYTY[nm]
            rk = M0.stack_k(rw, rh_, fn(), seed=300 + len(nm), k=k * rh / rh_)
            L.alpha_composite(rk, (round(hx - anc[0] * rk.size[0]), round(hy - anc[1] * rk.size[1])))
        return L

    def z_cieniem(top, sila=0.38):
        cien = Image.new("RGBA", top.size, (28, 16, 10, 0))
        cien.putalpha(top.getchannel("A").filter(ImageFilter.GaussianBlur(3 * k)).point(lambda v: int(v * sila)))
        im.alpha_composite(cien, (round(3 * k), round(5 * k)))
        im.alpha_composite(top)

    im.alpha_composite(reka("tyl", rece[1]))
    L = Image.new("RGBA", im.size, (0, 0, 0, 0))
    L.alpha_composite(body, (round(M * k), round(TOP * k)))
    z_cieniem(L)
    twarz(im, dict(s, _cygaro=cygaro), k, M, TOP, mina)
    z_cieniem(reka("przod", rece[0]))
    box = im.getbbox()
    im = im.crop(box)
    stopa = ((M + J.FIG_W / 2) * k - box[0], (TOP + J.STOPA + s["nogi"]) * k - box[1])
    if lustro:
        im, stopa = ImageOps.mirror(im), (im.size[0] - stopa[0], stopa[1])
    spr = Sprite(im, f"mini-k-{key}-{k:.2f}-{rece}-{rzecz}-{mina}-{lustro}-{cygaro}", rim=2, clean=False, crop=False)
    return spr, (stopa[0] / im.size[0], stopa[1] / im.size[1]), im.size[1] / (k * (J.STOPA + s["nogi"] - J.CZUBEK))


def duza(st, key, x, y, h, p, rece, mina, rzecz=None, lustro=False, cygaro=False, gruby=10, rot=0.0):
    """Duża lalka stopami w (x, y) ekranu (zwykle pod kadrem — w kadrze do pasa), h — od stóp do czubka głowy, px ekranu."""
    k = max(1.0, round(h / (J.STOPA - J.CZUBEK) * papier.Q * 4) / 4)
    spr, kot, ark = postac_k(key, k, rece, rzecz, mina, lustro, cygaro)
    M0.poloz_obrys(st, spr, x, y, p, h * ark, kot, kolor=BIALY, gruby=gruby, k=k, rot=rot)


@lru_cache(None)
def zaslona(kolor, srodek, brzeg):
    """Ciemna półprzezroczysta zasłona 16:9: krycie srodek w środku, brzeg w rogach (winieta) — tło ciemnieje, a postacie
    z białym obrysem przed nią świecą (J.glow w zwykłym trybie prawie nie kryje)."""
    import numpy as np
    w, h = 320, 180
    yy, xx = np.mgrid[:h, :w]
    r = np.clip(np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / 1.41, 0, 1)
    a = (255 * (srodek + (brzeg - srodek) * r ** 1.5)).astype(np.uint8)
    rgb = np.zeros((h, w, 3), np.uint8)
    rgb[:] = kolor
    return Sprite(Image.fromarray(np.dstack([rgb, a]), "RGBA"), f"zaslona-{kolor}-{srodek}-{brzeg}", rim=0, clean=False)


def scena_e():
    """Zasadzka z bliska: Clyde i Bonnie do pasa w kadrze, przerażeni („krzyk”), za nimi o świcie w sosnach Luizjany
    z krzaków błyskają lufy łowców i lecą kule. Ciemne, chłodne niebo — postacie z białym obrysem świecą na nim."""
    st, w = scena_poczatek("zasadzka")
    S.las(st, 0.0, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=0.6, noc=E_NOC, kul=False)
    # zaciemnienie świtu za łowcami: para z białym obrysem świeci na ciemnym tle
    M0.poloz(st, zaslona((10, 12, 22), *E_CIEMNO), 640, 360, P.droga + 0.07, w=1400, anchor=(0.5, 0.5), shadow=None)
    kule_w_tle(st, n=18, seed=23)
    # łowcy w krzakach po prawej: lufy w lewo, w stronę pary, z końców luf błyski
    for n, (key, x) in enumerate(zip(("hamer", "gault", "alcorn", "hinton"), E_LOWCY_X)):
        stoi(st, key, x, 742, 330, P.drzewa + 0.01 + 0.001 * n, (90.0, 10.0), ("karabin", 50, (0.3, 0.55)), flip=-1, gruby=5)
    for n, x in enumerate((690, 820, 950, 1080, 1210, 1340)):
        M0.poloz(st, J.krzak(n % 6), x, 742, P.drzewa + 0.02 + 0.001 * n, h=E_KRZAK_H, anchor=(0.5, 1.0))
    for x in E_LOWCY_X:  # błysk z końca lufy (1.20)
        strzal(st, x + E_LUFA[0], E_LUFA[1], -1, P.drzewa + 0.03, 1.1)
    bx, by, bh = E_BONNIE
    duza(st, "bonnie", bx, by, bh, P.lalki + 0.010, (150.0, 168.0), "krzyk", gruby=9)
    cx, cy, ch = E_CLYDE
    duza(st, "clyde", cx, cy, ch, P.lalki + 0.014, E_RECE_CLYDE, "krzyk", gruby=10)
    tab(st, "AMBUSH!", 1010, 190, 84, rot=4)
    tab(st, "1934", 1160, 330, 56, rot=-6, xs=(0.5,))
    szyld(st, x=22, y=12, h=110, maxw=620)
    st.grade = (1.02, 0.98, 0.96)
    return st


def scena_f():
    """Zdjęcie dla żartu z bliska: Bonnie do pasa, mruga, cygaro w kąciku ust, rewolwer w górę; z prawej wielki flesz
    aparatu na ciemnym tle i gazeta, która zrobiła z tego legendę."""
    st, w = scena_poczatek("zdjecie")
    S.teatr_gazet(st, 0.0, w)
    # zaciemnienie tła: flesz i postać świecą na ciemnym (jak burza za Susanoo)
    M0.poloz(st, zaslona((14, 10, 10), *F_CIEMNO), 640, 360, P.lalki - 0.02, w=1400, anchor=(0.5, 0.5), shadow=None)
    gz = J.gazeta("CIGAR GIRL!", 9, 360, 480)
    M0.poloz_obrys(st, Sprite(gz.mips[0], "gazeta-miniatura-f", rim=2, clean=False), *F_GAZETA, P.lalki - 0.01, 360, (0.5, 0.5),
                   kolor=BIALY, gruby=7, k=1.0, rot=9)
    st.put(J.glow(), 1180, 190, P.rekwizyty, w=1100, anchor=(0.5, 0.5), mode="add", alpha=0.95, shadow=None, tint=(1.0, 0.97, 0.88))
    st.put(J.rek("aparat_lampa"), 1185, 205, P.rekwizyty + 0.005, h=210, anchor=(0.5, 0.5), rot=-10, sx=-1)
    x, y, h = F_BONNIE
    duza(st, "bonnie", x, y, h, P.lalki + 0.014, (122.0, 25.0), "chytra", rzecz=("rewolwer", 40, (0.3, 0.75)), cygaro=True, gruby=10)
    tab(st, "IT WAS A JOKE!", 930, 40, 84, rot=3)
    tab(st, "SNAP!", 1200, 330, 58, rot=-6, xs=(0.5,))
    szyld(st, x=22, y=12, h=110, maxw=620)
    st.grade = (1.04, 0.99, 0.93)
    return st


def scena_g():
    """Zdjęcie dla żartu w ciemni (reżyser 25.11: „jedną miniaturkę zrób z tą ciemnią, tam gdzie jest to czerwone tło”,
    ujęcie „ciemnia”): ceglana ściana w czerwonym świetle, pod sufitem suszą się czarne odbitki Bonnie, w kuwecie wyłania się
    zdjęcie z cygarem, wywołującemu wypada papieros („O!”). Z przodu duża Bonnie w swoich kolorach — czerwień jest tylko
    na dekoracji (zasłona przed tłem), więc postać z białym obrysem świeci na niej."""
    st, w = scena_poczatek("ciemnia")
    S.wnetrze(st, 0.0, w, sciana="cegla", zarowki=(G_ZAROWKA,), kul=False)
    # sznurek z odbitkami pod sufitem (marker reżysera 24.11 w ujęciu „ciemnia”)
    pp = P.wzgorza
    st.line([M0.ekran_na_swiat(st, 0, 150, pp), M0.ekran_na_swiat(st, 640, 166, pp), M0.ekran_na_swiat(st, 1280, 150, pp)], pp, width=1.6,
            color=(60, 40, 30))
    for n, sx_ in enumerate(G_ODBITKI):
        sy_ = 150 + 16 * math.sin(math.pi * sx_ / 1280)
        M0.poloz(st, J.odbitka_bonnie(n), sx_, sy_, pp + 0.001, h=150, anchor=(0.5, 0.0), rot=(-4, 3, -2, 5, -3)[n % 5])
        M0.poloz(st, J.rek("pinezka"), sx_, sy_ + 3, pp + 0.0015, h=18, anchor=(0.5, 0.5), shadow=None)
    # wywołujący nad kuwetą: papieros wypada mu z ust
    fx, fy, fh = G_FOTOGRAF
    J.LALKI.setdefault("fotograf_o", dict(J.LALKI["fotograf"], usta="o"))  # „O!” — usta otwarte
    stoi(st, "fotograf_o", fx, fy, fh, P.wzgorza + 0.02, (95.0, 30.0), None, flip=-1, rot=-6, gruby=5)
    M0.poloz(st, J.rek("papieros"), *G_PAPIEROS, P.wzgorza + 0.025, h=16, anchor=(0.5, 0.5), rot=-70)
    M0.poloz(st, J.rek("kuweta"), G_KUWETA[0], G_KUWETA[1], P.wzgorza + 0.03, w=560, anchor=(0.5, 1.0))
    M0.poloz(st, J.zdjecie_bonnie(), *G_ODBITKA, P.wzgorza + 0.031, h=190, anchor=(0.5, 0.5), rot=-8, shadow=None)
    # czerwone światło ciemni na całej dekoracji (jak koniec(extra=(1.35, 0.62, 0.58)) w filmie), postać przed nim
    M0.poloz(st, zaslona(G_CZERWIEN, *G_KRYCIE), 640, 360, P.lalki - 0.02, w=1400, anchor=(0.5, 0.5), shadow=None)
    st.put(J.glow(r=256, color=(255, 90, 70)), *M0.ekran_na_swiat(st, G_ZAROWKA, 120, P.lalki - 0.015), P.lalki - 0.015, w=700,
           anchor=(0.5, 0.5), mode="add", alpha=0.6, shadow=None)
    x, y, h = F_BONNIE
    duza(st, "bonnie", x, y, h, P.lalki + 0.014, (122.0, 25.0), "chytra", rzecz=("rewolwer", 40, (0.3, 0.75)), cygaro=True, gruby=10)
    tab(st, "IT WAS A JOKE!", 930, 34, 84, rot=3)
    tab(st, "O!", *G_O, 58, rot=-6, xs=(0.5,))
    szyld(st, x=22, y=12, h=110, maxw=620)
    st.grade = (1.04, 0.98, 0.95)
    return st


G_ZAROWKA = 1000
G_ODBITKI = (120, 330, 540, 750, 960, 1170)
G_FOTOGRAF = (1140, 850, 560)  # stopy pod kadrem (nad krawędzią widać go do pasa), wysokość postaci
G_ODBITKA = (960, 520)  # odbitka z kuwety w wyciągniętej ręce wywołującego
G_PAPIEROS = (1030, 560)  # papieros w locie do kuwety
G_O = (1180, 250)
G_KUWETA = (900, 745)
G_CZERWIEN = (150, 14, 10)
G_KRYCIE = (0.5, 0.75)

E_NOC = 0.55
E_CIEMNO = (0.62, 0.85)
E_LOWCY_X = (800, 940, 1080, 1220)
E_LUFA = (-158, 490)  # koniec lufy względem stóp łowcy (x) i jego wysokość na ekranie (y)
E_KRZAK_H = 230
E_RECE_CLYDE = (-150.0, -165.0)  # dłonie w górę: „whoa!” (karabin nad głową wchodził w szyld)
E_BONNIE = (620, 1260, 1010)  # stopy x, y; wysokość postaci (pod kadrem: w kadrze do pasa)
E_CLYDE = (300, 1330, 1120)
F_CIEMNO = (0.66, 0.9)
F_BONNIE = (380, 1330, 1150)
F_GAZETA = (930, 480)


SCENY = {"A": scena_a, "B": scena_b, "C": scena_c, "D": scena_d, "E": scena_e, "F": scena_f, "G": scena_g}


def main():
    OUT.mkdir(exist_ok=True)
    img = SCENY[WARIANT]().render()
    nazwa = f"miniatura_{WARIANT}_en"
    if ROZMIAR:
        duzy = M0.wyrownaj(img, 1.2 * papier.Q * 0.7)
        png, jpg = OUT / f"{nazwa}_{ROZMIAR // 960}k.png", OUT / f"{nazwa}_{ROZMIAR // 960}k.jpg"
        duzy.save(png, optimize=True)
        duzy.convert("RGB").save(jpg, quality=93)
        maly = M0.wyrownaj(img.resize((1280, 720), Image.LANCZOS), 1.2)
    else:
        maly = M0.wyrownaj(img.resize((1280, 720), Image.LANCZOS), 1.2)
    maly.save(OUT / f"{nazwa}.png", optimize=True)
    maly.convert("RGB").save(OUT / f"{nazwa}.jpg", quality=92)
    print(OUT / f"{nazwa}.jpg")


if __name__ == "__main__":
    main()
