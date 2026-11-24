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


SCENY = {"A": scena_a, "B": scena_b, "C": scena_c}


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
