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


@lru_cache(None)
def postac(key, rece=(20.0, 10.0), lean=0.0, rzecz=None):
    """Lalka filmu w pozie, w kolorach (zestaw_bc.sylwetka(kolor=True)) — jeden wycinek, który dostaje biały obrys."""
    return Sprite(J.sylwetka(key, rece=rece, lean=lean, rzecz=rzecz, kolor=True), f"miniatura-{key}-{rece}-{lean}-{rzecz}", rim=2,
                  clean=False)


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


def kotwica_tulowia(key, spr):
    """Kotwica x środka tułowia w wycinku postaci z wyciągniętą ręką (wycinek jest przycięty do całej sylwetki, więc jego
    środek leży w stronę ręki): szerokość lalki z rękami w dół to tułów, który zaczyna się przy lewej krawędzi."""
    wn = J.sylwetka(key, rece=(0.0, 0.0), kolor=True).size[0]
    return (wn / 2) / spr.w


def stoi(st, key, x, y, h, p, rece, rzecz, flip=1.0, rot=0.0, gruby=9):
    """Postać z białym obrysem, która stoi stopami w (x, y) ekranu niezależnie od wyciągniętej ręki."""
    spr = postac(key, rece=rece, rzecz=rzecz)
    ax = kotwica_tulowia(key, spr)
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
    stoi(st, "bonnie_slub_beret", bx, by + 4, 300, P.auta - 0.005, (90.0, 10.0), ("rewolwer", 40, (0.3, 0.75)), flip=-1, rot=ROT_AUTA * 0.35)
    stoi(st, "clyde", kx, ky + 4, 330, P.auta - 0.004, (88.0, 10.0), ("karabin", 50, (0.3, 0.55)), rot=ROT_AUTA * 0.55)
    for (sx_, sy_, kier, wk) in STRZALY_D:
        strzal(st, sx_, sy_, kier, P.auta, wk)
    # kule z krzaków w stronę auta (smugi od łowców ku karoserii)
    for n, (x0, (u, v)) in enumerate(((300, (380, 230)), (495, (520, 200)), (785, (700, 200)), (980, (820, 230)))):
        ix, iy = na_aucie(u, v)
        f0 = 0.35 + 0.1 * n
        st.line([(lerp_(x0, ix, f0), lerp_(600, iy, f0)), (lerp_(x0, ix, f0 + 0.3), lerp_(600, iy, f0 + 0.3))], P.lalki + 0.01, width=3,
                color=(255, 236, 190), alpha=0.75)
    # pierwszy plan: sześciu łowców nisko w małych krzakach z ujęcia 104 (J.krzak(n), barwa z filmu) — kapelusze, oczy, lufy
    for n, ((key, _), x) in enumerate(zip(LOWCY_MIN, (90, 300, 495, 785, 980, 1190))):
        fl = 1 if x < 640 else -1
        spr = postac(key, rece=(75.0, 10.0), rzecz=("karabin", 46, (0.3, 0.55)))
        ax = kotwica_tulowia(key, spr)
        M0.poloz(st, spr, x, 838, P.lalki + 0.02 + 0.001 * n, h=300, anchor=(ax, 1.0), sx=fl, rot=-14 * fl, tint=(0.82, 0.82, 0.8))
    for n, x in enumerate((20, 175, 330, 485, 640, 795, 950, 1105, 1260)):
        M0.poloz(st, J.krzak(n % 6), x, 728, P.lalki + 0.03 + 0.001 * n, h=118, anchor=(0.5, 1.0))
    tab(st, "THE REAL ENDING", 975, 12, 66, rot=2)
    tab(st, "BANG!", 190, 190, 54, rot=-8, xs=(0.5,))
    tab(st, "BANG!", 1120, 170, 54, rot=7, xs=(0.5,))
    szyld(st)
    st.grade = (1.05, 0.98, 0.9)
    return st


def lerp_(a, b, f):
    return a + (b - a) * f


ROT_AUTA = -16  # przód auta w górę (tył w rowie)
AUTO_D = (640, 440, 300)  # środek auta na ekranie i jego wysokość
STOPY_D = ((385, 72), (598, 150))  # stopy na arkuszu Forda: Bonnie na dachu, Clyde na dole przedniej szyby, przy masce
STRZALY_D = ((408, 162, -1, 1.0), (950, 124, 1, 1.1))  # (x, y, kierunek, wielkość) błysków z końców luf
LOWCY_MIN = (("hamer", ""), ("gault", ""), ("alcorn", ""), ("hinton", ""), ("jordan", ""), ("oakley", ""))


SCENY = {"A": scena_a, "B": scena_b, "C": scena_c, "D": scena_d}


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
