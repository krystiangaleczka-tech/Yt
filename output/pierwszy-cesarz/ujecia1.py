"""Ujęcia aktów 1–4: Zakładnik, Król chłopiec, Wojna i zamach, Koniec sześciu królestw.

Każda funkcja `s_<klucz>(st, w, t, T)` rysuje jedno ujęcie rozpiski: zmienia stan świata w czasie (wydarzenie ujęcia),
ustawia kamerę i woła scenografię. Czasy liczone od początku ujęcia.
"""
import math
import random

import zestaw as Z
from papier import CX, CY, back, clamp, ease, ease_out, noise, settle
from swiat import (BAN, EMP, I, KOLUMNA, MALY, PODBITE, TRON, URNA, P, jezdziec, kam, lalka, lerp, pr, sala, stol, swiat, swiatlo,
                   urzednik, wlocznie, woz)


# ---------- pomocnicze ----------

def krol(st, t, h=EMP[2], k=1.0, x=TRON[0], y=TRON[1], flip=1.0, lean=0.0, sink=0.0, lift=0.0, p=0.785):
    """Zheng w sali tronowej (na podwyższeniu albo na posadzce)."""
    lalka(st, t, "zheng", x, h, k, y=y, p=p, flip=flip, lean=lean, sink=sink, lift=lift, seed=7)


def za_oknem(st, x, flag=None, seed=3, h=250):
    """Włócznie widziane przez kraty okien sali (plan przed niebem, za ścianą)."""
    spr = Z.spears(seed) if flag is None else Z.spears(seed, flag=flag)
    st.put(spr, x, 430, 0.3, h=h, anchor=(1.0, 1.0), shadow=None)


def mapa(st, t, x, y, wd, k, covers=None, qin_dx=0.0, p=0.83, lift=0.0):
    """Mapa siedmiu królestw na dwóch nitkach. covers — które królestwa przykrył już czarny papier Qin (0..1)."""
    if k <= 0:
        return
    yy = y - (1 - back(k, 1.1)) * 620 - lift
    for sx in (x - wd * 0.36, x + wd * 0.36):
        st.line([(sx, -260), (sx, yy + 4)], p, width=1.1, color=(70, 56, 44), alpha=0.7, z=-0.5)
    st.put(Z.map_board(), x, yy, p, w=wd, anchor=(0.5, 0.0), shadow=(6, 9, 9, 0.45), blur=0)
    for n, kk in enumerate(Z.MAPA):
        st.put(Z.map_piece(kk), x + (qin_dx if kk == "qin" else 0), yy, p + 0.001 + n * 0.0002 + (0.004 if kk == "qin" else 0),
               w=wd, anchor=(0.5, 0.0), shadow=(2, 3, 3, 0.35), blur=0)
        c = (covers or {}).get(kk, 0.0)
        if c > 0:  # czarny arkusz nasuwa się od zachodu
            st.put(Z.map_piece(kk, True), x - (1 - ease_out(c)) * wd * 0.45, yy, p + 0.006 + n * 0.0002, w=wd, anchor=(0.5, 0.0),
                   alpha=min(1.0, c * 4), shadow=(2, 3, 3, 0.35), blur=0)


# ---------- akt 1 · Zakładnik ----------

def s_teatr(st, w, t, T):
    """Front teatru; światło, słońce na nitce, ziemia wysuwa się od dołu; wjazd do środka."""
    w.sun = pr(t, 1.3, 1.3)
    w.far, w.land, w.mid = pr(t, 2.3, 0.9), pr(t, 2.7, 0.9), pr(t, 3.1, 0.9)
    w.city, w.bridge, w.road, w.front = pr(t, 3.6, 0.9), pr(t, 4.1, 0.8), pr(t, 4.0, 0.8), pr(t, 4.5, 0.8)
    w.trees = [pr(t, 4.8, 0.8), pr(t, 4.5, 0.8)]
    w.clouds = [pr(t, 2.9, 1.1), pr(t, 3.5, 1.1), pr(t, 4.1, 1.1)]
    k = ease(pr(t, 1.6, T - 1.9))
    m = math.exp(lerp(math.log(0.6), math.log(1.0), k))
    kam(st, t, 0, 640, lerp(322, 360, k), m, 1.0, lens=m ** 0.55, truck=1.0, drift=0.4)
    st.dof = 0.0
    swiat(st, t, w)
    on = pr(t, 0.7, 0.5) * (0.75 + 0.25 * (math.sin(t * 43) > -0.6 or t > 1.25))  # lampa w skrzyni zapala się z mrugnięciem
    st.put(Z.black(), CX, CY, 0.992, w=1300, anchor=(0.5, 0.5), alpha=1 - on, shadow=None, blur=0)
    Z.theatre_put(st, 0.55 + 0.45 * pr(t, 0.2, 0.8))
    swiatlo(st, w, t)


def s_choragwie(st, w, t, T):
    """Siedem chorągwi wyskakuje po kolei; Qin na końcu."""
    for n, k in enumerate(["qi", "yan", "chu", "wei", "zhao", "han", "qin"]):
        w.up[k] = pr(t, 0.7 + n * 0.5 + (0.35 if k == "qin" else 0), 0.6)
    kam(st, t, 1, 640, 360, lerp(1.0, 1.06, ease(t / T)), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_handan(st, w, t, T):
    """Pod bramą Handanu wysuwa się ojciec-zakładnik, a obok mała lalka chłopca."""
    k = ease(t / T)
    kam(st, t, 2, lerp(900, 850, k), lerp(470, 500, k), lerp(1.2, 1.45, k), 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    lalka(st, t, "ojciec", 890, 286, pr(t, 1.3, 1.1), flip=-1)
    lalka(st, t, "zheng", 772, MALY, pr(t, 3.0, 1.0), seed=8)
    swiatlo(st, w, t)


def s_oblezenie(st, w, t, T):
    """Za wzgórzem idą włócznie Qin; ojciec i chłopiec cofają się pod bramę, chorągiew Zhao drży."""
    w.wlocznie = lerp(360, 900, (t / T) ** 0.9)
    w.chwiej = {"zhao": 5 * math.sin(t * 13) * pr(t, 1.0, 0.6)}
    back_ = 26 * ease(pr(t, 1.0, 1.4))
    kam(st, t, 3, lerp(790, 820, ease(t / T)), 500, 1.45, 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    lalka(st, t, "ojciec", 890 + back_, 286, flip=-1, lean=3 * ease(pr(t, 1.0, 1.0)))
    lalka(st, t, "zheng", 772 + back_ * 1.4, MALY, lean=4 * ease(pr(t, 1.2, 1.0)), seed=8)
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_kupiec(st, w, t, T):
    """Obok ojca wysuwa się kupiec, za nim wtacza się wóz ze skrzynią, na rampie rosną stosy monet."""
    k = ease(t / T)
    kam(st, t, 4, lerp(940, 960, k), 500, lerp(1.4, 1.52, k), 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    woz(st, t, lerp(1420, 1150, ease_out(pr(t, 1.6, 2.2))), flip=-1)
    lalka(st, t, "ojciec", 916, 286, flip=1, lean=2 * settle((t - 1.6) / 1.5, 1.2))
    lalka(st, t, "zheng", 808, MALY, seed=8)
    lalka(st, t, "kupiec", 1050, 300, pr(t, 0.6, 1.1), flip=-1, lean=-4 * ease(pr(t, 2.2, 0.7)))
    for n, x in enumerate((968, 1000, 984)):
        kk = pr(t, 3.4 + n * 0.5, 0.5)
        if kk > 0:
            st.put(Z.S("coin_stack", 0.5), x, 706 - (38 if n == 2 else 0) + (1 - back(kk, 1.5)) * 70, P.rekwizyty + n * 0.002, h=50,
                   shadow=(3, 4, 4, 0.4))
    swiatlo(st, w, t)


def _noc(w, n=0.85):
    w.noc, w.sun, w.moon = n, 0.0, 1.0


def s_ucieczka(st, w, t, T):
    """Noc: ojciec i kupiec znikają, wóz odjeżdża na zachód obok włóczni straży; chłopiec zostaje sam."""
    _noc(w)
    go = ease(pr(t, 1.4, T - 1.6))
    kam(st, t, 5, lerp(930, 700, ease(pr(t, 1.0, T - 1.2))), 520, 1.35, 0.72, truck=0.8)
    st.dof = 1.2
    swiat(st, t, w)
    woz(st, t, lerp(1150, 470, go), flip=-1, ladunek=(Z.lalka("kupiec"), 62, 4, 6) if t > 1.1 else None)
    wlocznie(st, t, 1100, n=1, h=104, seed=6)  # straż stoi za wzgórzem i nie rusza się
    lalka(st, t, "ojciec", 916, 286, sink=pr(t, 0.2, 0.9))
    lalka(st, t, "kupiec", 1050, 300, flip=-1, sink=pr(t, 0.4, 0.9))
    lalka(st, t, "zheng", 808, MALY, seed=8, flip=-1 if t > 2.2 else 1, lean=-3 * ease(pr(t, 2.2, 1.0)))
    swiatlo(st, w, t)


def s_sam(st, w, t, T):
    """Zbliżenie małej lalki pod bramą: za nią przechodzą włócznie straży, lalka cofa się."""
    _noc(w)
    w.wlocznie = lerp(1320, 760, t / T)
    kam(st, t, 6, 830, 590, 2.2, 0.8, lens=1.9)
    st.dof = 2.4
    swiat(st, t, w)
    lalka(st, t, "zheng", 808 + 30 * ease(pr(t, 0.6, 1.0)), MALY, seed=8, flip=-1, lean=5 * ease(pr(t, 0.6, 0.8)))
    swiatlo(st, w, t)


def s_powrot(st, w, t, T):
    """Dzień: wóz z małą lalką jedzie przez wzgórza na zachód, aż do czarnej chorągwi Qin."""
    x = lerp(820, 270, (t / T) ** 0.95)
    kam(st, t, 7, x + 30, 525, 1.8, 0.645, lens=1.68, truck=0.85)
    st.dof = 1.5
    swiat(st, t, w)
    woz(st, t, x, flip=-1, ladunek=(Z.lalka("zheng"), 70, 6, 8))
    swiatlo(st, w, t)


def s_krol13(st, w, t, T):
    """Mała lalka Zhenga wysuwa się zza rampy, zjeżdża zawieszka z rokiem; lalka unosi się i prostuje."""
    w.zawieszki = [("247 p.n.e.", 470, 440, pr(t, 2.2, 1.0))]
    k = ease(t / T)
    kam(st, t, 8, lerp(350, 360, k), lerp(580, 566, k), lerp(1.7, 1.95, k), 0.8)
    st.dof = 2.0
    swiat(st, t, w)
    lalka(st, t, "zheng", EMP[0], MALY, pr(t, 0.5, 1.2), seed=7, lift=10 * ease(pr(t, 3.6, 1.0)),
          lean=-2 * ease(pr(t, 3.6, 1.0)) + 1.5 * settle((t - 4.4) / 1.4, 1.5))
    swiatlo(st, w, t)


# ---------- akt 2 · Król chłopiec ----------

KANCLERZ = 604


def s_regent(st, w, t, T):
    """Sala: mały król na podwyższeniu, obok wyrasta kanclerz; urzędnicy kłaniają się kanclerzowi."""
    kam(st, t, 9, 690, 420, lerp(1.0, 1.08, ease(t / T)), 0.8)
    st.dof = 0.8
    sala(st, t, w)
    krol(st, t, MALY, k=pr(t, 1.9, 0.9))
    lalka(st, t, "kupiec", KANCLERZ, 344, pr(t, 2.6, 1.1), lean=3 * settle((t - 3.8) / 1.6, 1.2))
    for n in range(2):  # urzędnicy wysuwają się i kłaniają kanclerzowi, nie królowi
        urzednik(st, t, n, bow=11 * ease(pr(t, 4.2 + n * 0.5, 0.7)), k=pr(t, 3.2 + n * 0.3, 0.8))


def s_nauka(st, w, t, T):
    """Zbliżenie małego króla; za nim zjeżdżają zawieszki „nagroda” i „kara”."""
    w.zawieszki = [("nagroda", 262, 420, pr(t, 0.8, 1.0)), ("kara", 486, 446, pr(t, 2.4, 1.0))]
    k = ease(t / T)
    kam(st, t, 10, 392, lerp(530, 516, k), lerp(1.9, 2.2, k), 0.785)
    st.dof = 2.2
    sala(st, t, w)
    # pod „nagrodą” zjeżdża moneta, pod „karą” włócznia; chłopiec odwraca się raz ku jednej, raz ku drugiej
    Z.hang(st, Z.coin(), 262, 478, P.rekwizyty + 0.02, pr(t, 1.5, 0.9), t, 150, drop=420, sway=2.5, h=46, shadow=(4, 6, 6, 0.4))
    Z.hang(st, Z.prop("wlocznia"), 486, 500, P.rekwizyty + 0.02, pr(t, 3.1, 0.9), t, 151, drop=420, sway=2.0, h=96, rot0=-8,
           shadow=(4, 6, 6, 0.4))
    turn = math.cos(math.pi * ease(pr(t, 1.6, 0.4))) if t < 3.3 else -math.cos(math.pi * ease(pr(t, 3.3, 0.4)))
    krol(st, t, MALY, flip=turn, lean=2 * settle((t - 4.4) / 1.5, 1.2))
    lalka(st, t, "kupiec", KANCLERZ, 344, lean=-3 * ease(pr(t, 4.6, 0.8)))


def s_dorosl(st, w, t, T):
    """Mała lalka króla opada, na jej miejscu wysuwa się duża; w oknach łuna i włócznie buntu."""
    red = ease(pr(t, 3.0, 1.2))
    kam(st, t, 11, 560, 430, lerp(1.22, 1.3, ease(t / T)), 0.785)
    st.dof = 1.0
    def okno():
        za_oknem(st, lerp(-200, 900, pr(t, 3.2, T - 3.2)), flag=(170, 40, 34))
        ogien_za_oknem(st, t, red)
    sala(st, t, w, okna=(1.0, lerp(0.96, 0.5, red), lerp(0.86, 0.34, red)), za_oknem=okno)
    # chłopiec rośnie: mała lalka opada, wysuwa się średnia, potem duża — trzy wycinanki jak trzy lata
    krol(st, t, MALY, sink=pr(t, 0.4, 0.7))
    krol(st, t, 280, k=pr(t, 0.9, 0.6), sink=pr(t, 1.6, 0.6))
    krol(st, t, k=pr(t, 2.1, 1.0), lean=-3 * ease(pr(t, 3.6, 0.6)))
    lalka(st, t, "kupiec", KANCLERZ, 344, lean=-3 * ease(pr(t, 3.4, 0.8)))
    for n in range(2):  # urzędnicy podrywają się na odgłos buntu
        urzednik(st, t, n, lift=18 * ease(pr(t, 3.5 + 0.3 * n, 0.3)), bow=-6 * ease(pr(t, 3.5 + 0.3 * n, 0.3)))
    st.grade = (1.0 + 0.06 * red, 0.93 - 0.06 * red, 0.84 - 0.10 * red)


def ogien_za_oknem(st, t, k):
    """Płomienie z bibuły za oknami sali (plan za ścianą)."""
    if k <= 0:
        return
    ft = math.floor(t * 12) / 12
    for n, x in enumerate((210, 330, 640, 760, 1050)):
        st.put(Z.flame(n), x, 480, 0.32, h=(120 + 60 * noise(ft, 870 + n, 8)) * k, rot=8 * noise(ft, 880 + n, 6), shadow=None,
               tint=(1.15, 1.1, 1.0))


def s_bunt(st, w, t, T):
    """Okna sali: włócznie buntowników i straży zderzają się, łuna i ogień migoczą."""
    fl = 0.8 + 0.2 * noise(t, 3, 9)

    def okno():
        ogien_za_oknem(st, t, 1.0)
        za_oknem(st, lerp(500, 1150, t / T), flag=(170, 40, 34))
        za_oknem(st, lerp(1700, 1250, t / T), seed=4)
    kam(st, t, 12, 840, 250, 1.8, 0.5, lens=1.7, truck=0.3, shake=5)
    st.dof = 0.6
    sala(st, t, w, okna=(1.0 * fl, 0.5 * fl, 0.34 * fl), za_oknem=okno)
    st.grade = (1.06, 0.87, 0.74)


def s_odprawa(st, w, t, T):
    """Król wskazuje ręką; kanclerz odwraca się i odjeżdża ku wyjściu, urzędnicy kłaniają się królowi."""
    turn1, turn2 = ease(pr(t, 0.3, 0.6)), ease(pr(t, 2.3, 0.6))
    flip = math.cos(math.pi * turn1) if turn2 <= 0 else -math.cos(math.pi * turn2)
    kam(st, t, 13, 700, 430, lerp(1.1, 1.16, ease(t / T)), 0.8)
    st.dof = 0.8
    sala(st, t, w)
    krol(st, t, lean=5 * ease(pr(t, 1.1, 0.5)) - 3 * ease(pr(t, 4.0, 1.0)))
    lalka(st, t, "kupiec", KANCLERZ + 1000 * ease(pr(t, 3.0, T - 3.0)) ** 1.3, 344, flip=flip, lean=-3 * turn1 * (1 - turn2))
    for n in range(2):
        urzednik(st, t, n, bow=9 * ease(pr(t, 3.8 + n * 0.4, 0.6)))


def s_trucizna(st, w, t, T):
    """Kanclerz sam na skraju sceny, przed nim czarka; lalka powoli opada pod rampę, czarka zostaje."""
    w.noc, w.sun_y = 0.35, 260.0 + 90 * ease(t / T)  # zachód: słońce schodzi w czasie ujęcia
    kam(st, t, 14, lerp(1000, 960, ease(t / T)), lerp(520, 560, ease(t / T)), lerp(1.6, 2.0, ease(t / T)), 0.8, lens=1.6)
    st.dof = 2.0
    swiat(st, t, w)
    lalka(st, t, "kupiec", 1020, 330, pr(t, 0.2, 0.9), flip=-1, lean=-5 * ease(pr(t, 1.6, 0.8)), sink=pr(t, 2.6, T - 2.9) * 0.999)
    Z.hang(st, Z.prop("czarka"), 930, 640, P.rekwizyty, pr(t, 0.9, 0.9), t, 160, drop=440, sway=0.6, h=52, shadow=(3, 4, 4, 0.4))
    swiatlo(st, w, t)


def s_lisi(st, w, t, T):
    """Obok króla wysuwa się Li Si i kłania się; urzędnicy klęczą twarzą do króla."""
    k = ease(t / T)
    kam(st, t, 15, lerp(580, 560, k), 450, lerp(1.22, 1.38, k), 0.785)
    st.dof = 1.0
    sala(st, t, w)
    krol(st, t, lean=1.5 * settle((t - 3.2) / 1.5, 1.2))
    lalka(st, t, "lisi", KANCLERZ, 318, pr(t, 0.6, 1.1), flip=-1, lean=-8 * ease(pr(t, 2.4, 0.7)) + 5 * ease(pr(t, 4.2, 0.8)))
    for n in range(2):
        urzednik(st, t, n, bow=4)


def s_mapa(st, w, t, T):
    """Na nitkach zjeżdża mapa siedmiu królestw; Li Si odwraca się ku niej, czarny kawałek Qin nasuwa się na sąsiada."""
    turn = ease(pr(t, 1.9, 0.6))
    kam(st, t, 16, lerp(760, 800, ease(t / T)), 400, 1.22, 0.8)
    st.dof = 0.8
    sala(st, t, w)
    krol(st, t)
    lalka(st, t, "lisi", KANCLERZ, 318, flip=-math.cos(math.pi * turn), lean=4 * ease(pr(t, 2.8, 0.6)))
    mapa(st, t, 940, 156, 440, pr(t, 0.5, 1.2), qin_dx=18 * ease(pr(t, 3.4, 1.0)), p=0.81)


def s_machina(st, w, t, T):
    """Za wzgórzami wyrastają rząd za rzędem lasy włóczni z czarnymi proporcami."""
    w.lean = 3 * settle((t - 0.4) / 1.6, 1.2)
    kam(st, t, 17, 660, 390, lerp(1.0, 1.1, ease(t / T)), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    for n, (band, p, h, x) in enumerate((("dal", 0.444, 86, 1330), ("srodek", 0.524, 106, 1360), ("droga", 0.635, 124, 1330))):
        wlocznie(st, t, x, p=p, band=band, h=h, n=5, up=pr(t, 0.8 + n * 1.2, 1.1), seed=10 + n * 3)
    swiatlo(st, w, t)


def s_kusze(st, w, t, T):
    """Zza wzgórza wylatuje chmara strzał, zatacza łuk przez niebo i wbija się w zbocze góry."""
    kam(st, t, 18, lerp(680, 730, ease(t / T)), 360, 1.12, 0.5, truck=0.4)
    st.dof = 0.6
    swiat(st, t, w)
    wlocznie(st, t, 620, n=2, seed=10)
    for j in range(38):
        r = random.Random(40 + j)
        f = clamp((t - 0.6 - j * 0.03 - r.uniform(0, 0.25)) / 1.25)
        if f <= 0:
            continue
        x0, y0 = 330 + r.uniform(-90, 90), 590
        x1, y1 = 900 + r.uniform(-130, 150), 395 + r.uniform(-40, 50)
        pos = lambda q: (lerp(x0, x1, q), lerp(y0, y1, q) - (250 + r.uniform(-30, 30)) * math.sin(math.pi * q) * (1 - 0.25 * q))
        (xa, ya), (xb, yb) = pos(max(0.0, f - 0.02)), pos(min(1.0, f + 0.02) if f < 1 else 1.0)
        ang = math.degrees(math.atan2(yb - ya, xb - xa)) if f < 1 else 58 + r.uniform(-10, 10)
        st.put(Z.prop("strzala"), *pos(f), 0.47, w=40, anchor=(0.9, 0.5), rot=ang, shadow=(2, 3, 3, 0.3))
    swiatlo(st, w, t)


def s_kanal(st, w, t, T):
    """Wzdłuż drogi rozwija się niebieska wstęga kanału, a przy niej wyskakują zielone poletka."""
    w.kanal = pr(t, 0.5, T - 1.8)
    kam(st, t, 19, lerp(430, 640, ease(t / T)), 590, 1.9, 0.67, lens=1.7, truck=0.8)
    st.dof = 1.6
    swiat(st, t, w)
    swiatlo(st, w, t)


# ---------- akt 3 · Wojna i zamach ----------

def s_wymarsz(st, w, t, T):
    """Wojsko rusza na wschód — las włóczni za wzgórzem, jeździec na przedzie; kamera jedzie z nimi."""
    go = 0.12 * ease(pr(t, 0.3, 1.0)) + 0.88 * pr(t, 0.8, T - 0.8) ** 1.15
    x = 330 + 330 * go
    w.wlocznie, w.jezdziec = x - 40, x + 60
    w.lean = 3.0 * settle(t / 1.4, 1.0)
    kam(st, t, 20, lerp(505, 640, ease(t / T)), 532, 1.55, 0.64, lens=1.45, truck=0.85)
    st.dof = 1.2
    swiat(st, t, w)
    swiatlo(st, w, t)


def _pada(st, w, t, T, i, kto, start, cx, jx, m=2.0):
    for k, a in zip(kto, start):
        w.fall[k] = pr(t, a, 0.95)
    w.jezdziec = jx[0] + (jx[1] - jx[0]) * (t / T)
    w.wlocznie = w.jezdziec - 130
    kam(st, t, i, lerp(cx[0], cx[1], ease(t / T)), 520, m, 0.62, lens=m * 0.94, truck=0.7, drift=1.6)
    st.dof = 1.3
    swiat(st, t, w)
    swiatlo(st, w, t, extra=(1.04, 0.98, 0.93))


def s_han(st, w, t, T):
    """Jeździec mija chorągiew Han — chorągiew pada."""
    _pada(st, w, t, T, 21, ["han"], [0.5], (640, 660), (470, 650))


def s_zhao(st, w, t, T):
    """Pada chorągiew Zhao; pod bramą Handanu, tam gdzie stał mały chłopiec, staje duża lalka króla."""
    w.fall["zhao"] = pr(t, 0.6, 0.95)
    w.emp = 0.0  # król nie stoi teraz na swoim miejscu: jest w Handanie
    w.jezdziec, w.wlocznie = lerp(560, 760, pr(t, 0.0, 2.6)), lerp(430, 640, pr(t, 0.0, 2.6))
    k = ease(t / T)
    kam(st, t, 22, lerp(770, 800, k), lerp(500, 480, k), lerp(1.3, 1.5, k), 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    lalka(st, t, "zheng", 790, EMP[2], pr(t, 2.4, 1.3), seed=7, lean=2 * settle((t - 4.0) / 1.6, 1.2))
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_poselstwo(st, w, t, T):
    """Spod chorągwi Yan rusza na zachód wóz ze skrzynią; chorągiew kołysze się za nim."""
    x = lerp(1010, 540, (t / T) ** 0.95)
    w.chwiej = {"yan": 6 * math.sin(t * 2.4) * math.exp(-t * 0.5)}
    kam(st, t, 23, x - 20, 525, 1.8, 0.645, lens=1.68, truck=0.85)
    st.dof = 1.5
    swiat(st, t, w)
    woz(st, t, x, flip=-1, ladunek=(Z.prop("szkatula"), 34, 14, 14))
    swiatlo(st, w, t)


STOLIK = (930, 280)  # sala: stół z podarunkami (x, szerokość)
JINGKE, LEKARZ, LISI_X = 1096, 1, 150


def _sala_zamach(st, t, w, stolik=1.0, zwoj="zwiniety", szkatula=1.0, lisi=0.0, bow=0.0, lift=0.0):
    """Sala podczas zamachu: stół z podarunkami, Li Si po lewej, lekarz klęczy po prawej."""
    sala(st, t, w)
    lalka(st, t, "lisi", LISI_X, 318, lean=lisi)
    urzednik(st, t, LEKARZ, bow=bow, lift=lift)
    if stolik > 0:
        on, down = stol(st, t, w, stolik, sx=STOLIK[0], sw=STOLIK[1])
        if szkatula > 0:
            bx, by = on(0.74, 0.34)
            st.put(Z.prop("szkatula"), bx, by + (1 - back(szkatula, 1.3)) * 0 , P.rekwizyty + 0.006, h=44 * szkatula, shadow=(3, 4, 4, 0.4))
        if zwoj == "zwiniety":
            st.put(Z.S("bamboo", 0.5), *on(0.38, 0.30), P.rekwizyty + 0.004, w=84, anchor=(0.5, 0.5), rot=-8, shadow=(3, 5, 5, 0.4))
        return on
    return None


def s_dary(st, w, t, T):
    """Po prawej wysuwa się stół, za nim Jing Ke; na stole stają szkatuła i zwinięta mapa."""
    kam(st, t, 24, lerp(700, 720, ease(t / T)), 440, 1.08, 0.8)
    st.dof = 0.8
    _sala_zamach(st, t, w, stolik=pr(t, 0.4, 1.1), szkatula=pr(t, 2.0, 0.5), zwoj="zwiniety" if t > 2.6 else None)
    krol(st, t, lean=2 * settle((t - 3.0) / 1.6, 1.2))
    lalka(st, t, "jingke", JINGKE, 300, pr(t, 1.2, 1.1), flip=-1, lean=-7 * ease(pr(t, 3.4, 0.7)) + 5 * ease(pr(t, 4.8, 0.7)), p=0.812)


def s_sztylet(st, w, t, T):
    """Detal stołu: zwój rozwija się po blacie i na końcu odsłania sztylet."""
    k = ease(pr(t, 0.5, T - 1.5))
    on = _sala_zamach(st, t, w, zwoj=None)
    ax, ay = on(0.10, 0.44)
    bx, by = on(0.60, 0.26)
    kam(st, t, 25, lerp(ax, bx, 0.5), lerp(ay, by, 0.5) - 6, 3.1, 0.85, lens=2.5, truck=0.8)
    st.dof = 3.0
    wd = 150
    st.put(Z.S("ledger", 0.5), ax, ay, P.rekwizyty + 0.006, w=wd, anchor=(0.0, 0.62), sx=max(0.04, k), rot=-4, shadow=(3, 5, 5, 0.4))
    st.put(Z.prop("sztylet"), bx - 6, by + 12, P.rekwizyty + 0.008, w=58, anchor=(0.5, 0.5), rot=-22, alpha=pr(k, 0.86, 0.1),
           shadow=(2, 3, 3, 0.4))
    rx, ry = lerp(ax + 8, bx + 22, k), lerp(ay - 14, by - 2, k)
    st.put(Z.S("bamboo", 0.5), rx, ry, P.rekwizyty + 0.010, w=84 * (1 - 0.45 * k), anchor=(0.5, 0.5), rot=-8 - 300 * k, shadow=(3, 5, 5, 0.4))
    krol(st, t)
    lalka(st, t, "jingke", JINGKE, 300, flip=-1, lean=-6, p=0.812)


def s_atak(st, w, t, T):
    """Jing Ke rzuca się ze sztyletem przez salę, król odskakuje w tył."""
    go = ease(pr(t, 0.2, 0.9))
    x = lerp(JINGKE, 610, go)
    kam(st, t, 26, lerp(760, 600, go), 470, 1.3, 0.8, shake=6 * (1 - go) + 2)
    st.dof = 1.0
    _sala_zamach(st, t, w, zwoj=None, lift=16 * go)
    krol(st, t, x=TRON[0] - 46 * go, lean=-7 * go)
    lalka(st, t, "jingke", x, 300, flip=-1, lean=-12 * go, p=0.82, y=708)
    st.put(Z.prop("sztylet"), x - 74, 492, 0.822, w=60, anchor=(0.5, 0.5), sx=-1, rot=8)


def _poscig(a):
    """Miejsce na okręgu dookoła kolumny: (x, plan, zwrot) — z przodu lalka idzie w lewo, z tyłu w prawo."""
    return KOLUMNA + 148 * math.cos(a), P.lalki + (0.022 if math.sin(a) > 0 else -0.022), (-1.0 if math.sin(a) > 0 else 1.0)


def s_kolumna(st, w, t, T):
    """Król ucieka dookoła kolumny: znika za nią i wychodzi z drugiej strony, zamachowiec krok za nim."""
    a = 0.75 * math.pi + 2 * math.pi * 2.25 * (t / T) ** 1.05
    kam(st, t, 27, 670, 470, 1.3, 0.8)
    st.dof = 1.0
    _sala_zamach(st, t, w, zwoj=None, lift=16)
    kx, kp, kf = _poscig(a)
    jx, jp, jf = _poscig(a - 1.15)
    st.put(Z.prop("miecz"), kx - 24 * kf, 548, kp - 0.002, w=230, anchor=(0.12, 0.5), rot=-62 if kf > 0 else -118)  # miecz w pochwie na plecach
    lalka(st, t, "zheng", kx, EMP[2], p=kp, flip=kf, lean=5 * kf, seed=7)
    lalka(st, t, "jingke", jx, 300, p=jp, flip=jf, lean=9 * jf)
    st.put(Z.prop("sztylet"), jx + 74 * jf, 492, jp + 0.002, w=60, anchor=(0.5, 0.5), sx=jf, rot=8 * jf)


def s_lekarz(st, w, t, T):
    """Klęczący lekarz unosi się i ciska torbą z lekami: torba leci łukiem i trafia zamachowca."""
    f = pr(t, 2.0, 0.75)
    hit = pr(t, 2.75, 0.3)
    kam(st, t, 28, lerp(860, 800, ease(t / T)), 480, 1.2, 0.8)
    st.dof = 0.9
    _sala_zamach(st, t, w, zwoj=None, lift=16 + 30 * ease(pr(t, 0.8, 0.7)), bow=-8 * ease(pr(t, 1.6, 0.3)) + 12 * ease(pr(t, 1.95, 0.2)))
    krol(st, t, x=476, y=708, flip=-1, lean=-4, p=0.82)
    jx = 604 - 22 * ease(hit)
    lalka(st, t, "jingke", jx, 300, p=0.82, flip=-1, lean=-9 + 16 * settle((t - 2.75) / 1.6, 2.0) + 6 * ease(hit))
    st.put(Z.prop("sztylet"), jx - 74, 492, 0.822, w=60, anchor=(0.5, 0.5), sx=-1, rot=8 + 30 * ease(hit))
    if 0 < f:
        bx = lerp(1150, jx + 20, min(1.0, f)) + 60 * ease(pr(t, 2.75, 0.6))
        by = lerp(500, 470, min(1.0, f)) - 150 * math.sin(math.pi * min(1.0, f)) + 250 * ease(pr(t, 2.75, 0.7)) ** 2
        st.put(Z.prop("torba"), bx, by, 0.83, h=44, anchor=(0.5, 0.5), rot=-400 * f)


def s_cios(st, w, t, T):
    """Nad ramieniem króla wysuwa się miecz i zatacza łuk; Jing Ke przechyla się i osuwa pod kolumnę."""
    turn = ease(pr(t, 0.1, 0.3))
    cut = ease(pr(t, 0.55, 0.3))
    fall = ease(pr(t, 0.85, 0.6))
    kam(st, t, 29, 550, 480, 1.85, 0.8, shake=7 * pr(t, 0.75, 0.1) * (1 - pr(t, 0.85, 0.4)))
    st.dof = 1.8
    _sala_zamach(st, t, w, zwoj=None, lift=46)
    flip = -math.cos(math.pi * turn)
    krol(st, t, x=476, y=708, flip=flip, lean=4 * cut, p=0.82)
    st.put(Z.prop("miecz"), 476 + 70 * flip, 500, 0.826, w=240, anchor=(0.1, 0.5), rot=lerp(-118, 24, cut))
    lalka(st, t, "jingke", 600 + 26 * fall, 300, p=0.818, flip=-1, lean=7 + 80 * fall, sink=0.24 * fall)


def s_pretekst(st, w, t, T):
    """Jing Ke leży pod kolumną, sztylet tkwi w niej wbity; król stoi nieruchomo, urzędnicy podnoszą się."""
    k = ease(t / T)
    kam(st, t, 30, lerp(600, 660, k), lerp(480, 430, k), lerp(1.5, 1.06, k), 0.8)
    st.dof = 0.9
    _sala_zamach(st, t, w, zwoj=None, lift=46 - 30 * ease(pr(t, 1.6, 1.0)), lisi=4 * ease(pr(t, 2.4, 0.8)))
    krol(st, t, x=476, y=708, p=0.82, lean=0.0)
    st.put(Z.prop("miecz"), 546, 500, 0.826, w=240, anchor=(0.1, 0.5), rot=lerp(24, 82, ease(pr(t, 0.6, 1.2))))  # miecz opada
    lalka(st, t, "jingke", 626, 300, p=0.818, flip=-1, lean=87, sink=0.24)
    st.put(Z.prop("sztylet"), KOLUMNA - 6, 470, P.lalki + 0.002, w=60, anchor=(0.9, 0.5), rot=-24, shadow=(2, 3, 3, 0.4))


# ---------- akt 4 · Koniec sześciu królestw ----------

def s_ksiaze(st, w, t, T):
    """Jeździec staje pod chorągwią Yan; chorągiew pochyla się nisko, ale włócznie Qin idą dalej."""
    stop = ease_out(pr(t, 0.0, 1.8))
    w.jezdziec = (lerp(790, 968, stop), 0.645, 100, 1 - stop)
    w.wlocznie = lerp(640, 1040, t / T)
    w.chwiej = {"yan": 30 * ease(pr(t, 2.0, 0.8)) - 12 * ease(pr(t, 3.6, 0.9))}
    kam(st, t, 31, lerp(960, 1000, ease(t / T)), 506, 1.75, 0.62, lens=1.64, truck=0.7)
    st.dof = 1.2
    swiat(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_wei(st, w, t, T):
    """Miasto pod chorągwią Wei: woda z papieru zalewa mury, chorągiew przewraca się, potem woda opada."""
    w.fall["wei"] = pr(t, 3.9, 0.95)
    up = ease(pr(t, 0.8, 3.0)) * (1 - 0.75 * ease(pr(t, T - 1.6, 1.4)))
    k = ease(t / T)
    kam(st, t, 32, lerp(900, 880, k), lerp(480, 470, k), lerp(1.3, 1.5, k), 0.5, lens=1.38, truck=0.4)
    st.dof = 0.8
    swiat(st, t, w)
    for i in range(3):
        st.put(Z.waves(i), 930 + (24 - i * 5) * math.sin(t * 1.4 + i * 1.9) * (1 if i % 2 else -1),
               lerp(640, 500 + i * 28, up) + 4 * math.sin(t * 1.7 + i), 0.505 + i * 0.006, w=1700, anchor=(0.5, 0.0), haze=0.12,
               tint=(0.80, 0.88, 0.92))
    swiatlo(st, w, t)


def s_chu(st, w, t, T):
    """Przed chorągwią Chu przesuwają się cztery rzędy włóczni, aż zasłaniają wzgórza."""
    w.chwiej = {"chu": 3 * math.sin(t * 9) * pr(t, 1.5, 1.0)}
    kam(st, t, 33, lerp(780, 900, ease(t / T)), 500, 1.45, 0.62, lens=1.36, truck=0.8)
    st.dof = 1.0
    swiat(st, t, w)
    for n, (band, p, h, v) in enumerate((("dal", 0.444, 84, 150), ("srodek", 0.524, 104, 190), ("droga", 0.635, 124, 230),
                                         ("przod", 0.705, 150, 280))):
        wlocznie(st, t, 300 + n * 130 + v * t, p=p, band=band, h=h, n=4, seed=10 + n * 3, up=pr(t, 0.2 + n * 0.3, 0.8))
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_chu_yan(st, w, t, T):
    """Chu chwieje się dłużej niż inne i pada; Yan zaraz po niej."""
    w.chwiej = {"chu": 7 * math.sin(t * 14) * pr(t, 0.05, 0.3) * (1 - pr(t, 0.75, 0.15))}
    _pada(st, w, t, T, 34, ["chu", "yan"], [0.85, 1.45], (930, 1010), (850, 1130))


def s_qi(st, w, t, T):
    """Jeździec staje przed ostatnią chorągwią; zjeżdża zawieszka z rokiem; Qi kładzie się sama."""
    stop = ease_out(pr(t, 0.0, 1.5))
    w.jezdziec = (990 + 80 * stop, 0.645, 100, 1 - stop)
    w.wlocznie = 880 + 70 * stop
    w.zawieszki = [("221 p.n.e.", 968, 352, pr(t, 1.5, 1.0))]
    w.chwiej = {"qi": 4 * math.sin(t * 11) * pr(t, 2.6, 0.4) * (1 - pr(t, 3.2, 0.2))}
    w.fall["qi"] = pr(t, 3.2, 1.5) * 0.999
    k = ease(t / T)
    kam(st, t, 35, lerp(1040, 1050, k), lerp(486, 492, k), lerp(1.6, 1.7, k), 0.62, lens=1.55, truck=0.7)
    st.dof = 1.2
    swiat(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_mapa2(st, w, t, T):
    """Mapa na nitkach: czarny papier Qin nasuwa się po kolei na sześć królestw; potem mapa odjeżdża w górę."""
    kam(st, t, 36, 640, 340, lerp(1.4, 1.5, ease(t / T)), 0.83)
    st.dof = 1.6
    swiat(st, t, w)
    mapa(st, t, 640, 104, 620, pr(t, 0.2, 1.0), covers={k: pr(t, 1.3 + n * 0.36, 0.6) for n, k in enumerate(PODBITE)},
         lift=700 * ease(pr(t, T - 0.8, 0.8)))
    swiatlo(st, w, t)


def s_czarne(st, w, t, T):
    """W miejscach sześciu powalonych chorągwi wstają czarne chorągwie Qin."""
    for n, k in enumerate(PODBITE):
        w.black[k] = pr(t, 0.5 + n * 0.42, 0.6)
    k = ease(t / T)
    kam(st, t, 37, lerp(790, 640, k), lerp(450, 360, k), lerp(1.3, 1.0, k), 0.62, truck=0.6)
    st.dof = 0.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_cesarz(st, w, t, T):
    """Zbliżenie; za plecami zjeżdżają dwie chorągwie ze smokiem, lalka unosi się i prostuje."""
    w.smoki = [pr(t, 1.2, 1.1), pr(t, 1.75, 1.1)]
    w.lift = 14 * ease(pr(t, 2.9, 1.2))
    w.lean = -2.0 * ease(pr(t, 2.9, 1.2)) + 1.5 * settle((t - 4.1) / 1.4, 1.5)
    k = ease(t / T)
    kam(st, t, 38, lerp(318, 324, k), lerp(452, 418, k), lerp(1.85, 2.2, k), 0.8)
    st.dof = 2.6
    swiat(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 1.0, 0.95))


def s_posagi(st, w, t, T):
    """Trójnóg z brązu wysuwa się zza rampy, wpadają do niego włócznie pokonanych; za nim wyrasta posąg."""
    w.urna = pr(t, 0.3, 1.0)
    w.ogien = 0.75 * ease(pr(t, 1.7, 0.8)) * (1 - 0.6 * ease(pr(t, T - 1.5, 1.2)))
    w.posag = pr(t, 3.1, 1.7)
    k = ease(t / T)
    kam(st, t, 39, lerp(1100, 1130, k), lerp(470, 440, k), lerp(1.25, 1.38, k), 0.84, truck=0.7)
    st.dof = 1.2
    swiat(st, t, w)
    fy = URNA[1] - URNA[2] * 0.8
    for j in range(8):  # włócznie wpadają do trójnogu jedna po drugiej
        f = pr(t, 1.3 + j * 0.2, 0.55)
        if 0 < f < 1:
            r = random.Random(60 + j)
            st.put(Z.prop("wlocznia"), URNA[0] + r.uniform(-34, 34), lerp(-120, fy + 150, f * f), P.rekwizyty - 0.006, h=170,
                   rot=r.uniform(-14, 14), shadow=None)
    hot = min(1.0, w.ogien)
    swiatlo(st, w, t, extra=(1 + 0.05 * hot, 1 - 0.05 * hot, 1 - 0.1 * hot))
