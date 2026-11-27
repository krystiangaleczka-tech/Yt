"""Ujęcia aktów 1–4: Zakładnik, Król chłopiec, Wojna i zamach, Koniec sześciu królestw.

Każda funkcja `s_<klucz>(st, w, t, T)` rysuje jedno ujęcie rozpiski: zmienia stan świata w czasie (wydarzenie ujęcia),
ustawia kamerę i woła scenografię. Czasy liczone od początku ujęcia.
"""
import math
import random

import zestaw as Z
from papier import CX, CY, back, clamp, ease, ease_out, noise, settle
from swiat import (podpis, BAN, EMP, I, KOLUMNA, MALY, PODBITE, TRON, URNA, ZAPAD, P, jezdziec, kam, lalka, lerp, pr, sala, stol, swiat, swiatlo,
                   urzednik, wlocznie, woz)


# ---------- pomocnicze ----------

def krol(st, t, h=EMP[2], k=1.0, x=TRON[0], y=TRON[1], flip=1.0, lean=0.0, sink=0.0, lift=0.0, p=0.785):
    """Zheng w sali tronowej (na podwyższeniu albo na posadzce); mała lalka to król-chłopiec bez brody."""
    lalka(st, t, "zheng_krol" if h <= MALY else "zheng", x, h, k, y=y, p=p, flip=flip, lean=lean, sink=sink, lift=lift, seed=7)


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


def iks(st, x, y, t, t0, h=200, p=P.rekwizyty + 0.03, mig=2):
    """Czerwony krzyż nad postacią: miga mig razy od chwili t0 (0,3 s widać, 0,18 s nie), potem gaśnie
    (reżyser 15.11: „czerwony X migoczący 2 razy z dźwiękiem”)."""
    for n in range(mig):
        a = t0 + n * 0.48
        if a <= t < a + 0.3:
            k = pr(t, a, 0.08)
            st.put(Z.prop("x"), x, y, p, h=h * (0.8 + 0.2 * back(k, 1.6)), anchor=(0.5, 0.5), rot=-4 + 8 * n, shadow=(4, 6, 6, 0.45))


def sztylet_w_dloni(st, x, flip, p, lean=0.0, y=507):
    """Sztylet Jing Ke w dłoni (reżyser 15.11: większy, ostrze ku górze przed nim). x — oś lalki, flip — zwrot lalki."""
    st.put(Z.prop("sztylet"), x + 65 * flip, y, p + 0.003, w=120, anchor=(36 / 210, 0.5), sx=flip, rot=(-14 + lean * 0.6) * flip,
           shadow=(2, 3, 3, 0.4))


def miecz_w_dloni(st, x, flip, kat, p=0.826, y=454):
    """Miecz króla rękojeścią w dłoni wyciągniętej ręki (reżyser 15.11: „aby był przy dłoni rękojeść”).
    kat — kierunek ostrza względem twarzy postaci: 0 przed siebie poziomo, ujemny w górę, dodatni w dół."""
    st.put(Z.prop("miecz"), x + 114 * flip, y, p, w=230, anchor=(0.12, 0.5), sx=flip, rot=kat * flip, shadow=(3, 4, 4, 0.4))


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


OJCIEC = 196  # ojciec-zakładnik klęczy: lalka niższa niż stojąca (286)


def s_handan(st, w, t, T):
    """Pod bramą Handanu wysuwa się ojciec-zakładnik, a obok mała lalka chłopca."""
    podpis(w, t, "ojciec Zhenga, książę Qin", 890, 436, 1.6, 1.5)  # tabliczka: pierwsze pojawienie się
    podpis(w, t, "Zheng", 772, 424, 4.2)  # tabliczka: pierwsze pojawienie się
    k = ease(t / T)
    kam(st, t, 2, lerp(900, 850, k), lerp(470, 500, k), lerp(1.2, 1.45, k), 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    lalka(st, t, "ojciec", 890, OJCIEC, pr(t, 1.3, 1.1), flip=-1)
    lalka(st, t, "zheng_dziecko", 772, MALY, pr(t, 3.0, 1.0), seed=8)
    swiatlo(st, w, t)


def s_oblezenie(st, w, t, T):
    """Za wzgórzem idą włócznie Qin; ojciec i chłopiec cofają się pod bramę, chorągiew Zhao drży."""
    w.wlocznie = lerp(360, 900, (t / T) ** 0.9)
    w.chwiej = {"zhao": 5 * math.sin(t * 13) * pr(t, 1.0, 0.6)}
    back_ = 26 * ease(pr(t, 1.0, 1.4))
    kam(st, t, 3, lerp(790, 820, ease(t / T)), 500, 1.45, 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    lalka(st, t, "ojciec", 890 + back_, OJCIEC, flip=-1, lean=3 * ease(pr(t, 1.0, 1.0)))
    lalka(st, t, "zheng_dziecko", 772 + back_ * 1.4, MALY, lean=4 * ease(pr(t, 1.2, 1.0)), seed=8)
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_kupiec(st, w, t, T):
    """Obok ojca wysuwa się kupiec, za nim wtacza się wóz ze skrzynią, na rampie rosną stosy monet."""
    podpis(w, t, "kupiec Lü Buwei", 1050, 334, 1.8)  # tabliczka: pierwsze pojawienie się
    k = ease(t / T)
    kam(st, t, 4, lerp(940, 960, k), 500, lerp(1.4, 1.52, k), 0.8)
    st.dof = 1.4
    swiat(st, t, w)
    woz(st, t, lerp(1420, 1150, ease_out(pr(t, 1.6, 2.2))), flip=-1)
    lalka(st, t, "ojciec", 916, OJCIEC, flip=1, lean=2 * settle((t - 1.6) / 1.5, 1.2))
    lalka(st, t, "zheng_dziecko", 808, MALY, seed=8)
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
    """Noc: ojciec i kupiec chowają się pod rampę i wyrastają na wozie; koń ciągnie wóz na zachód obok włóczni straży,
    chłopiec zostaje sam."""
    _noc(w)
    go = ease(pr(t, 1.4, T - 1.6))
    kam(st, t, 5, lerp(930, 700, ease(pr(t, 1.0, T - 1.2))), 520, 1.35, 0.72, truck=0.8)
    st.dof = 1.2
    swiat(st, t, w)
    na_wozie = [(Z.lalka(k), hh, dx, 6 + 46 * (1 - back(pr(t, t0, 0.6), 1.3)))  # wyrastają zza skrzyni na wozie
                for k, hh, dx, t0 in (("ojciec", 42, -34, 1.05), ("kupiec", 62, -10, 1.25)) if t > t0]
    woz(st, t, lerp(1150, 470, go), flip=-1, ladunek=na_wozie)
    wlocznie(st, t, 1100, n=1, h=104, seed=6)  # straż stoi za wzgórzem i nie rusza się
    lalka(st, t, "ojciec", 916, OJCIEC, sink=pr(t, 0.2, 0.9))
    lalka(st, t, "kupiec", 1050, 300, flip=-1, sink=pr(t, 0.4, 0.9))
    lalka(st, t, "zheng_dziecko", 808, MALY, seed=8, flip=-1 if t > 2.2 else 1, lean=-3 * ease(pr(t, 2.2, 1.0)))
    swiatlo(st, w, t)


SKOK_SAM = 1.25  # chwila odbicia chłopca w ujęciu „sam” (dźwięk: efekty.ZDARZENIA["sam"])


def s_sam(st, w, t, T):
    """Zbliżenie małej lalki pod bramą: za nią przechodzą włócznie straży, lalka cofa się, przysiada i wyskakuje w górę
    za kadr (reżyser 16.11: „zrób, że wyskakuje do góry za kadr”; w następnym ujęciu spada z góry do wozu)."""
    _noc(w)
    w.wlocznie = lerp(1320, 760, t / T)
    kam(st, t, 6, 830, 590, 2.2, 0.8, lens=1.9)
    st.dof = 2.4
    swiat(st, t, w)
    przysiad = 0.07 * ease(pr(t, 0.85, 0.3)) * (1 - pr(t, SKOK_SAM, 0.06))  # ugina kolana przed skokiem
    tau = max(0.0, t - SKOK_SAM)
    lift = 760 * tau + 300 * tau * tau  # wybicie: szybko w górę, za górną krawędź kadru w ok. 0,4 s
    lalka(st, t, "zheng_dziecko", 808 + 30 * ease(pr(t, 0.4, 0.6)), MALY, seed=8, flip=-1,
          lean=5 * ease(pr(t, 0.4, 0.5)) * (1 - ease(pr(t, 0.85, 0.3))) - 4 * ease(pr(t, SKOK_SAM, 0.2)), sink=przysiad, lift=lift)
    swiatlo(st, w, t)


SPADA_POWROT = (0.12, 0.5)  # chłopiec spada z góry kadru do wozu: początek i czas spadania (dźwięk: efekty.ZDARZENIA)


def s_powrot(st, w, t, T):
    """Dzień: chłopiec, który w poprzednim ujęciu wyskoczył za kadr, spada z góry prosto do wozu (reżyser 16.11: „zrób,
    że on z góry kadru wpada do tego powozu”), podskakuje na skrzyni i wóz jedzie przez wzgórza na zachód, aż do czarnej
    chorągwi Qin."""
    x = lerp(820, 270, (t / T) ** 0.95)
    kam(st, t, 7, x + 30, 525, 1.8, 0.645, lens=1.68, truck=0.85)
    st.dof = 1.5
    swiat(st, t, w)
    a, d = SPADA_POWROT
    f = pr(t, a, d)
    spad = 330 * (1 - f * f) if t >= a else 330  # swobodny spadek: coraz szybciej, z wysokości ponad górną krawędzią kadru
    odbicie = 9 * abs(settle((t - a - d) / 0.6, 1.5))  # po uderzeniu w skrzynię dwa małe podskoki
    if t >= a:
        woz(st, t, x, flip=-1, ladunek=(Z.lalka("zheng_dziecko"), 70, 6, 8 - spad - odbicie),
            sy=1 - 0.05 * abs(settle((t - a - d) / 0.35, 1.0)))
    else:
        woz(st, t, x, flip=-1)
    swiatlo(st, w, t)


def s_krol13(st, w, t, T):
    """Mała lalka Zhenga wysuwa się zza rampy, zjeżdża zawieszka z rokiem; lalka unosi się i prostuje."""
    w.zawieszki = [("247 p.n.e.", 470, 440, pr(t, 2.2, 1.0))]
    k = ease(t / T)
    kam(st, t, 8, lerp(350, 360, k), lerp(580, 566, k), lerp(1.7, 1.95, k), 0.8)
    st.dof = 2.0
    swiat(st, t, w)
    lalka(st, t, "zheng_krol", EMP[0], MALY, pr(t, 0.5, 1.2), seed=7, lift=10 * ease(pr(t, 3.6, 1.0)),
          lean=-2 * ease(pr(t, 3.6, 1.0)) + 1.5 * settle((t - 4.4) / 1.4, 1.5))
    swiatlo(st, w, t)


# ---------- akt 2 · Król chłopiec ----------

KANCLERZ = 604


def s_regent(st, w, t, T):
    """Sala: mały król na podwyższeniu, obok wyrasta kanclerz; urzędnicy kłaniają się kanclerzowi."""
    podpis(w, t, "król Zheng", TRON[0], 372, 2.6, 2.4)  # tabliczka: pierwsze pojawienie się
    podpis(w, t, "kanclerz Lü Buwei", KANCLERZ, 290, 4.6)  # tabliczka: pierwsze pojawienie się
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
    podpis(w, t, "król Zheng, dorosły", TRON[0], 222, 3.2, 2.6)  # tabliczka: pierwsze pojawienie się
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
    """Król wskazuje ręką; nad kanclerzem miga dwa razy czerwony X; kanclerz odwraca się i odjeżdża ku wyjściu,
    urzędnicy kłaniają się królowi."""
    turn1, turn2 = ease(pr(t, 0.3, 0.6)), ease(pr(t, 2.6, 0.6))
    flip = math.cos(math.pi * turn1) if turn2 <= 0 else -math.cos(math.pi * turn2)
    kam(st, t, 13, 700, 430, lerp(1.1, 1.16, ease(t / T)), 0.8)
    st.dof = 0.8
    sala(st, t, w)
    krol(st, t, lean=5 * ease(pr(t, 1.1, 0.5)) - 3 * ease(pr(t, 4.2, 1.0)))
    kx = KANCLERZ + 1000 * ease(pr(t, 3.3, T - 3.3)) ** 1.3
    lalka(st, t, "kupiec", kx, 344, flip=flip, lean=-3 * turn1 * (1 - turn2))
    iks(st, KANCLERZ, 520, t, 1.5)
    for n in range(2):
        urzednik(st, t, n, bow=9 * ease(pr(t, 4.0 + n * 0.4, 0.6)))


def s_trucizna(st, w, t, T):
    """Kanclerz sam na skraju sceny; kielich zjeżdża na nitce do wysokości jego głowy i przechyla się, a z niego
    leje się zielona trucizna prosto do ust (reżyser 15.11); kielich odjeżdża w górę, kanclerz zgina się i opada pod rampę."""
    w.noc, w.sun_y = 0.35, 260.0 + 90 * ease(t / T)  # zachód: słońce schodzi w czasie ujęcia
    kam(st, t, 14, lerp(1000, 960, ease(t / T)), lerp(520, 560, ease(t / T)), lerp(1.6, 2.0, ease(t / T)), 0.8, lens=1.6)
    st.dof = 2.0
    swiat(st, t, w)
    przechyl = ease(pr(t, 2.0, 0.6)) * (1 - ease(pr(t, 3.9, 0.4)))
    leje = pr(t, 2.4, 0.15) * (1 - pr(t, 3.8, 0.15))
    sink = pr(t, 4.9, T - 5.2) * 0.999
    lean = -5 * ease(pr(t, 1.2, 0.8)) + 7 * ease(pr(t, 2.2, 0.4)) * (1 - ease(pr(t, 3.9, 0.3))) - 12 * ease(pr(t, 4.3, 0.5)) * (1 - sink)
    lalka(st, t, "kupiec", 1020, 330, pr(t, 0.2, 0.9), flip=-1, lean=lean, sink=sink)
    kx, ky = 925, 390  # kielich wisi na wysokości głowy, na lewo od twarzy (marker reżysera)
    zjazd = pr(t, 0.3, 0.9) if t < 3.95 else 1 - pr(t, 3.95, 0.6)
    rot = 72 * przechyl
    Z.hang(st, Z.prop("czarka"), kx, ky, P.lalki + 0.016, zjazd, t, 160, drop=440, sway=0.4 * (1 - przechyl), h=52, rot0=rot,
           shadow=(3, 4, 4, 0.4))
    if leje > 0:  # strumień z brzegu kielicha do ust, lekko faluje; krople kapią
        # reżyser 16.11 (markery w ujęciu 15): „stąd ma się wylewać” — z górnego brzegu przechylonego kielicha, nie z jego
        # dolnego rogu; „trochę wyżej do jego ust” — strumień kończy się na ustach, nie na brodzie
        c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        lx, ly = kx + c * 12 - s_ * 2, ky + s_ * 12 + c * 2
        mx, my = 997, 428
        pts = []
        for j in range(9):
            q = j / 8 * leje
            pts.append((lerp(lx, mx, q) + 3 * math.sin(t * 17 + j), lerp(ly, my, q) - 14 * math.sin(math.pi * q) * (1 - q)))
        st.line(pts, P.lalki + 0.015, width=4.5, color=(84, 168, 58), alpha=0.92)
        st.line(pts, P.lalki + 0.0151, width=1.6, color=(170, 230, 120), alpha=0.7)
        for j in range(3):
            q = (t * 1.7 + j / 3) % 1.0
            st.put(Z.prop("kulka"), mx - 6 + 4 * j, my + 10 + 60 * q * q, P.lalki + 0.015, h=5, anchor=(0.5, 0.5),
                   tint=(0.45, 0.95, 0.35), alpha=leje * (1 - q), shadow=None)
    swiatlo(st, w, t)


def s_lisi(st, w, t, T):
    """Obok króla wysuwa się Li Si i kłania się; urzędnicy klęczą twarzą do króla."""
    podpis(w, t, "Li Si, doradca", KANCLERZ, 318, 1.6)  # tabliczka: pierwsze pojawienie się
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
    """Za wzgórzami wyrastają rząd za rzędem lasy włóczni z czarnymi proporcami; potem całe wojsko trzy razy unosi
    włócznie (reżyser 15.11: „wszystkie włócznie podnoszą się na 0,6 s do góry 3×”)."""
    w.lean = 3 * settle((t - 0.4) / 1.6, 1.2)
    kam(st, t, 17, 660, 390, lerp(1.0, 1.1, ease(t / T)), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    unies = sum(math.sin(math.pi * pr(t, a, 0.6)) for a in (4.9, 6.2, 7.5))
    for n, (band, p, h, x) in enumerate((("dal", 0.444, 86, 1330), ("srodek", 0.524, 106, 1360), ("droga", 0.635, 124, 1330))):
        wlocznie(st, t, x, p=p, band=band, h=h, n=5, up=pr(t, 0.8 + n * 1.2, 1.1), seed=10 + n * 3, lift=0.34 * h * unies)
    swiatlo(st, w, t)


def s_kusze(st, w, t, T):
    """Zza wzgórza wylatuje chmara strzał, zatacza łuk przez niebo i wbija się w zbocze góry; zaraz po niej druga salwa
    (reżyser 15.11: „dodaj jeszcze jedną salwę”)."""
    kam(st, t, 18, lerp(680, 730, ease(t / T)), 360, 1.12, 0.5, truck=0.4)
    st.dof = 0.6
    swiat(st, t, w)
    wlocznie(st, t, 620, n=2, seed=10)
    for salwa, (t0, dx, dy, seed) in enumerate(((0.6, 0, 0, 40), (2.7, 70, -30, 140))):
        for j in range(38):
            r = random.Random(seed + j)
            f = clamp((t - t0 - j * 0.03 - r.uniform(0, 0.25)) / 1.25)
            if f <= 0:
                continue
            x0, y0 = 330 + r.uniform(-90, 90), 590
            x1, y1 = 900 + dx + r.uniform(-130, 150), 395 + dy + r.uniform(-40, 50)
            pos = lambda q: (lerp(x0, x1, q), lerp(y0, y1, q) - (250 + r.uniform(-30, 30)) * math.sin(math.pi * q) * (1 - 0.25 * q))
            (xa, ya), (xb, yb) = pos(max(0.0, f - 0.02)), pos(min(1.0, f + 0.02) if f < 1 else 1.0)
            ang = math.degrees(math.atan2(yb - ya, xb - xa)) if f < 1 else 58 + r.uniform(-10, 10)
            st.put(Z.prop("strzala"), *pos(f), 0.47 + 0.002 * salwa, w=40, anchor=(0.9, 0.5), rot=ang, shadow=(2, 3, 3, 0.3))
    swiatlo(st, w, t)


def s_kanal(st, w, t, T):
    """Robotnicy kopią kanał: przed nimi rozwija się niebieska wstęga wody między nasypami, za nią wyskakują zielone
    poletka, a gdy woda płynie, sunie po niej łódź z ziarnem (reżyser 15.11: „wyraźniej to pokaż, bo nie wiadomo,
    o co chodzi”)."""
    w.kanal = pr(t, 0.6, T - 3.6)
    podpis(w, t, "kanał Zhengguo", 520, 452, 1.4, 4.0)
    kam(st, t, 19, lerp(430, 640, ease(t / T)), 590, 1.9, 0.67, lens=1.7, truck=0.8)
    st.dof = 1.6
    swiat(st, t, w)
    front = 300 + 460 * ease_out(w.kanal)  # czoło wykopu
    for j in range(4):  # kopacze przy czole wykopu: idą za wodą, pochylają się nad ziemią
        x = front + 10 + j * 26 + 6 * math.sin(t * 2 + j)
        if w.kanal < 1 or t < T - 2.6:
            st.put(Z.prop("robotnik"), x, Z.ground("droga", x) + 30 - abs(math.sin(t * 5 + j)) * 3, 0.6705, h=40,
                   rot=8 * math.sin(t * 4.5 + j * 1.3), shadow=(2, 2, 3, 0.3))
    f = pr(t, T - 3.2, 3.0)  # łódź z workami ziarna płynie kanałem
    if f > 0:
        x = lerp(320, 700, f)
        st.put(Z.boat(), x, Z.ground("droga", x) + 22 + 1.5 * math.sin(t * 3), 0.6728, h=34, rot=2 * math.sin(t * 2.2),
               shadow=(2, 3, 3, 0.35))
    swiatlo(st, w, t)


# ---------- akt 3 · Wojna i zamach ----------

def s_wymarsz(st, w, t, T):
    """Król odwraca się w lewo, po chwili w prawo i wskazuje wschód; wojsko rusza — las włóczni za wzgórzem, jeździec
    na przedzie; kamera jedzie z nimi."""
    go = 0.12 * ease(pr(t, 0.3, 1.0)) + 0.88 * pr(t, 0.8, T - 0.8) ** 1.15
    x = 330 + 330 * go
    w.wlocznie, w.jezdziec = x - 40, x + 60
    w.flip = math.cos(math.pi * ease(pr(t, 1.7, 0.45))) if t < 2.9 else -math.cos(math.pi * ease(pr(t, 2.9, 0.45)))
    w.lean = 3.0 * settle(t / 1.4, 1.0) + 4.0 * ease(pr(t, 3.4, 0.4)) * (1 - 0.4 * ease(pr(t, 5.0, 1.0)))
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
    """Pada chorągiew Zhao; pod bramą Handanu stoi przez chwilę mały chłopiec, a na niego spada z góry duża lalka króla
    i go zasłania (reżyser 15.11) — dorosły król wrócił tam, gdzie był dzieckiem."""
    w.fall["zhao"] = pr(t, 0.6, 0.95)
    w.emp = 0.0  # król nie stoi teraz na swoim miejscu: jest w Handanie
    w.jezdziec, w.wlocznie = lerp(560, 760, pr(t, 0.0, 2.6)), lerp(430, 640, pr(t, 0.0, 2.6))
    spad = pr(t, 2.5, 0.42)
    hit = pr(t, 2.92, 0.12)
    k = ease(t / T)
    kam(st, t, 22, lerp(770, 800, k), lerp(500, 480, k), lerp(1.3, 1.5, k), 0.8, shake=7 * hit * (1 - pr(t, 3.0, 0.5)))
    st.dof = 1.4
    swiat(st, t, w)
    lalka(st, t, "zheng_dziecko", 784, MALY, pr(t, 0.1, 0.6), seed=8, p=P.lalki + 0.004, sink=pr(t, 2.95, 0.2))
    if t >= 2.5:  # duża lalka spada z góry na nitkach i ląduje z przysiadem
        lalka(st, t, "zheng", 790, EMP[2], 1.0, seed=7, lift=640 * (1 - spad) ** 2 - 10 * math.sin(math.pi * pr(t, 2.92, 0.35)),
              lean=2 * settle((t - 4.0) / 1.6, 1.2))
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_poselstwo(st, w, t, T):
    """Spod turkusowej chorągwi Yan rusza na zachód wóz ze skrzynią; chorągiew kołysze się za nim, a nad wozem zjeżdża
    tabliczka „ZABIĆ KRÓLA!” (reżyser 15.11)."""
    x = lerp(1010, 540, (t / T) ** 0.95)
    w.chwiej = {"yan": 10 * math.sin(t * 2.6) * (1 - 0.55 * pr(t, 0.0, T))}
    kam(st, t, 23, x - 20, 525, 1.8, 0.645, lens=1.68, truck=0.85)
    st.dof = 1.5
    swiat(st, t, w)
    woz(st, t, x, flip=-1, ladunek=(Z.prop("szkatula"), 34, 14, 14))
    Z.hang(st, Z.tag("ZABIĆ KRÓLA!"), x + 6, Z.ground("droga", x) - 150, P.rekwizyty + 0.02, pr(t, 5.0, 0.9), t, 95, drop=460, sway=1.6,
           h=46, shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t)


STOLIK = (930, 280)  # sala: stół z podarunkami (x, szerokość)
JINGKE, LEKARZ, LISI_X = 1096, 1, 150
ZWOJ = (862.5, 601.5)  # środek zwiniętej mapy na stole z podarunkami (z markera reżysera w ujęciu ze sztyletem)
ZWOJ_A, ZWOJ_B = Z.ZWOJ_A, Z.ZWOJ_B  # wzdłuż wałka (głąb blatu) i kierunek rozwijania (wzdłuż blatu)
LEZY = 70  # o ile unieść leżącą lalkę Jing Ke, żeby leżała na posadzce nad rampą, a nie pod nią
MAPA = (ZWOJ[0] + 24, ZWOJ[1] + 6 - 31)  # rozwinięta mapa na stole: środek górnej krawędzi (od ujęcia ze sztyletem)


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
        if zwoj == "zwiniety":  # wzdłuż głębi blatu, jak w ujęciu ze sztyletem
            st.put(Z.S("bamboo", 0.5), *ZWOJ, P.rekwizyty + 0.004, w=58, anchor=(0.5, 0.5), rot=-45, shadow=(3, 5, 5, 0.4))
        elif zwoj == "mapa":  # rozwinięta mapa leży dalej na stole po zamachu (reżyser 16.11: „zwój z poprzedniego ujęcia
            # ma tu leżeć”) — to samo miejsce, rozmiar i obrót co na końcu ujęcia ze sztyletem
            st.put(Z.S("ledger", 0.5), *MAPA, P.rekwizyty + 0.006, w=116, anchor=(0.5, 0.0), rot=6, shadow=(3, 5, 5, 0.4))
        return on
    return None


def s_dary(st, w, t, T):
    """Po prawej wysuwa się stół, za nim Jing Ke; na stole staje szkatuła (mapa dopiero w następnym ujęciu)."""
    podpis(w, t, "Jing Ke z Yan", JINGKE, 336, 2.2)  # tabliczka: pierwsze pojawienie się
    kam(st, t, 24, lerp(700, 720, ease(t / T)), 440, 1.08, 0.8)
    st.dof = 0.8
    # bez zwiniętej mapy na stole (reżyser 16.11: „usuń ten zwój ze stołu, bo on będzie w następnym dopiero”) — rozwinięta
    # mapa zjeżdża na pusty blat w ujęciu ze sztyletem
    _sala_zamach(st, t, w, stolik=pr(t, 0.4, 1.1), szkatula=pr(t, 2.0, 0.5), zwoj=None)
    krol(st, t, lean=2 * settle((t - 3.0) / 1.6, 1.2))
    lalka(st, t, "jingke", JINGKE, 300, pr(t, 1.2, 1.1), flip=-1, lean=-7 * ease(pr(t, 3.4, 0.7)) + 5 * ease(pr(t, 4.8, 0.7)), p=0.812)


def s_sztylet(st, w, t, T):
    """Detal stołu: na pusty blat zjeżdża na nitkach gotowa, rozwinięta mapa z deszczułek; po chwili z jej środka
    wyłania się sztylet (reżyser 15.11: „po prostu połóż na nowo rozwinięty zwój”; 16.11: zwinięty zwój usunięty
    z początku ujęcia)."""
    on = _sala_zamach(st, t, w, zwoj=None)
    mx, my = ZWOJ[0] + 24, ZWOJ[1] + 6  # środek rozwiniętej mapy na blacie
    kam(st, t, 25, mx + 4, my - 10, 3.3, 0.85, lens=2.6, truck=0.8)
    st.dof = 3.0
    roz = pr(t, 0.9, 1.0)  # rozwinięta mapa zjeżdża na dwóch nitkach i kładzie się na blacie
    Z.hang(st, Z.S("ledger", 0.5), *MAPA, P.rekwizyty + 0.006, roz, t, 181, drop=420, sway=0.15, w=116, rot0=6,
           string=roz < 1, strings=(0.2, 0.8), shadow=(3, 5, 5, 0.4))
    f = ease(pr(t, 2.6, 0.6))  # sztylet wyłania się ze środka mapy
    if f > 0:
        st.put(Z.prop("sztylet"), mx + 4, my + 1 + 2 * (1 - f), P.rekwizyty + 0.008, w=54 * (0.5 + 0.5 * back(f, 1.4)), anchor=(0.5, 0.5),
               rot=-12, alpha=min(1.0, f * 2), shadow=(2, 3, 3, 0.4))
        st.put(Z.glow(), mx + 4, my + 1, P.rekwizyty + 0.009, w=110, anchor=(0.5, 0.5), mode="add",
               alpha=0.35 * math.sin(math.pi * pr(t, 2.6, 1.0)), shadow=None, tint=(1.0, 0.95, 0.85))
    krol(st, t)
    lalka(st, t, "jingke", JINGKE, 300, flip=-1, lean=-6, p=0.812)


def s_atak(st, w, t, T):
    """Jing Ke rzuca się ze sztyletem przez salę, król odskakuje w tył."""
    go = ease(pr(t, 0.2, 0.9))
    x = lerp(JINGKE, 610, go)
    kam(st, t, 26, lerp(760, 600, go), 470, 1.3, 0.8, shake=6 * (1 - go) + 2)
    st.dof = 1.0
    _sala_zamach(st, t, w, zwoj="mapa", lift=16 * go)
    krol(st, t, x=TRON[0] - 46 * go, lean=-7 * go)
    lalka(st, t, "jingke", x, 300, flip=-1, lean=-12 * go, p=0.82, y=708)
    sztylet_w_dloni(st, x, -1, 0.82, lean=-12 * go)


def _poscig(a):
    """Miejsce na elipsie dookoła kolumny (przez pół sali, reżyser 15.11: „biegaj bardziej po tym pokoju”):
    (x, plan, zwrot) — z przodu lalka biegnie w lewo, z tyłu w prawo."""
    return KOLUMNA + 300 * math.cos(a), P.lalki + (0.022 if math.sin(a) > 0 else -0.022), (-1.0 if math.sin(a) > 0 else 1.0)


def s_kolumna(st, w, t, T):
    """Król ucieka dookoła kolumny przez całą salę: znika za nią i wychodzi z drugiej strony, zamachowiec daleko za nim
    ze sztyletem w dłoni; miecz króla w pochwie wisi ostrzem w dół."""
    a = 0.75 * math.pi + 2 * math.pi * 1.6 * (t / T) ** 1.05
    kam(st, t, 27, 680, 470, 1.18, 0.8)
    st.dof = 1.0
    _sala_zamach(st, t, w, zwoj="mapa", lift=16)
    kx, kp, kf = _poscig(a)
    jx, jp, jf = _poscig(a - 2.1)
    st.put(Z.prop("miecz"), kx - 20 * kf, 488, kp - 0.002, w=230, anchor=(0.12, 0.5), rot=92 + 10 * kf)  # miecz w pochwie u pasa, ostrzem w dół
    lalka(st, t, "zheng", kx, EMP[2], p=kp, flip=kf, lean=5 * kf, seed=7)
    lalka(st, t, "jingke", jx, 300, p=jp, flip=jf, lean=9 * jf)
    sztylet_w_dloni(st, jx, jf, jp, lean=9)


def s_lekarz(st, w, t, T):
    """Jing Ke rozpędza się ku królowi, dobiega na 80% drogi i dwa razy pchnięciem dochodzi do niego (80→100→80→100%);
    lekarz ciska torbą z lekami, torba trafia zamachowca w głowę i krąży mu nad nią jak przy zamroczeniu (reżyser 15.11)."""
    podpis(w, t, "nadworny lekarz", 1168, 404, 0.3, 2.4)  # tabliczka: pierwsze pojawienie się
    kx, cel = 476, 566  # król i miejsce, z którego sztylet sięga króla (100%)
    start = 800
    p80 = start + (cel - start) * 0.8
    if t < 1.0:
        jx = lerp(start, p80, ease(pr(t, 0.0, 1.0)))
    else:
        u = t - 1.0  # dwa pchnięcia: 80 → 100 → 80 → 100 %
        faza = [(0.35, p80, cel), (0.4, cel, p80), (0.35, p80, cel)]
        jx = cel
        for d, a, b in faza:
            if u < d:
                jx = lerp(a, b, ease(u / d))
                break
            u -= d
    hit = pr(t, 2.65, 0.25)
    jx += 70 * ease(hit)  # cofa się po uderzeniu torbą
    zamr = pr(t, 2.65, 0.3)
    kam(st, t, 28, lerp(780, 700, ease(t / T)), 480, 1.18, 0.8)
    st.dof = 0.9
    _sala_zamach(st, t, w, zwoj="mapa", lift=16 + 30 * ease(pr(t, 0.8, 0.7)), bow=-8 * ease(pr(t, 1.5, 0.3)) + 12 * ease(pr(t, 1.85, 0.2)))
    pchn = max(0.0, 1 - abs(jx - cel) / (p80 - cel))
    krol(st, t, x=kx, y=708, flip=-1, lean=-4 - 6 * pchn, p=0.82)
    lean = -9 * (1 - zamr) + zamr * (8 * math.sin(t * 3.1) - 2)  # zamroczony kołysze się
    lalka(st, t, "jingke", jx, 300, p=0.82, flip=-1, lean=lean - 5 * pchn)
    sztylet_w_dloni(st, jx, -1, 0.82, lean=lean)
    f = pr(t, 1.95, 0.7)
    if 0 < f < 1:  # torba leci łukiem do głowy zamachowca
        bx = lerp(1150, jx - 10, f)
        by = lerp(500, 448, f) - 150 * math.sin(math.pi * f)
        st.put(Z.prop("torba"), bx, by, 0.83, h=44, anchor=(0.5, 0.5), rot=-400 * f)
    elif f >= 1:  # torba i gwiazdki krążą mu nad głową
        hx, hy = jx - 10, 392
        for n in range(4):
            a = t * 2 * math.pi * 0.9 + n * math.pi / 2
            ox, oy = 46 * math.cos(a), 11 * math.sin(a)
            pz = 0.821 if math.sin(a) > 0 else 0.815
            if n == 0:
                st.put(Z.prop("torba"), hx + ox, hy + oy - 4, pz, h=36, anchor=(0.5, 0.5), rot=12 * math.sin(a), shadow=(2, 3, 3, 0.3))
            else:
                st.put(Z.prop("gwiazdka"), hx + ox, hy + oy, pz, h=18, anchor=(0.5, 0.5), rot=t * 200 + n * 40, shadow=(1, 2, 2, 0.3))


def s_cios(st, w, t, T):
    """Król odwraca się do zamachowca z mieczem w dłoni, miecz zatacza łuk; Jing Ke przechyla się i osuwa pod kolumnę."""
    turn = ease(pr(t, 0.1, 0.3))
    cut = ease(pr(t, 0.55, 0.3))
    fall = ease(pr(t, 0.85, 0.6))
    kam(st, t, 29, 550, 480, 1.85, 0.8, shake=7 * pr(t, 0.75, 0.1) * (1 - pr(t, 0.85, 0.4)))
    st.dof = 1.8
    _sala_zamach(st, t, w, zwoj="mapa", lift=46)
    flip = -math.cos(math.pi * turn)
    krol(st, t, x=476, y=708, flip=flip, lean=4 * cut, p=0.82)
    if abs(flip) > 0.05:
        miecz_w_dloni(st, 476, flip, lerp(-75, 35, cut))
    lalka(st, t, "jingke", 600 + 26 * fall, 300, p=0.818, flip=-1, lean=7 + 80 * fall, lift=LEZY * fall)  # osuwa się i leży na posadzce


def s_pretekst(st, w, t, T):
    """Król wbija miecz w serce leżącego pod kolumną Jing Ke; sztylet zamachowca od początku koziołkuje w powietrzu
    i na końcu spada, dobijając go (reżyser 15.11); urzędnicy podnoszą się."""
    k = ease(t / T)
    kam(st, t, 30, lerp(600, 660, k), lerp(480, 430, k), lerp(1.5, 1.06, k), 0.8)
    st.dof = 0.9
    _sala_zamach(st, t, w, zwoj="mapa", lift=46 - 30 * ease(pr(t, 1.6, 1.0)), lisi=4 * ease(pr(t, 2.4, 0.8)))
    pch = ease(pr(t, 0.4, 0.4))
    krol(st, t, x=476, y=708, p=0.82, lean=6 * pch * (1 - 0.6 * ease(pr(t, 1.4, 0.8))))
    serce = (806, 606)
    if pch < 1:  # miecz idzie z dłoni w pierś leżącego
        hx, hy = 476 + 114, 454
        st.put(Z.prop("miecz"), lerp(hx, serce[0] - 30, pch), lerp(hy, serce[1] - 150, pch), 0.826, w=230, anchor=(0.12, 0.5),
               rot=lerp(20, 78, pch), shadow=(3, 4, 4, 0.4))
    else:  # miecz tkwi w piersi: ostrze schodzi za ciało
        st.put(Z.prop("miecz"), serce[0] - 30, serce[1] - 150, 0.8175, w=230, anchor=(0.12, 0.5), rot=78 + 1.5 * settle((t - 0.8) / 0.8, 2),
               shadow=(3, 4, 4, 0.4))
    dob = pr(t, T - 2.0, 0.6)
    lalka(st, t, "jingke", 626, 300, p=0.818, flip=-1, lean=87 + 3 * math.sin(math.pi * pr(t, 0.8, 0.3)) + 3 * math.sin(math.pi * pr(t, T - 1.4, 0.3)),
          lift=LEZY)
    if dob < 1:  # sztylet koziołkuje w powietrzu, potem spada w zamachowca
        x = lerp(lerp(700, 760, 0.5 + 0.5 * math.sin(t * 1.3)), serce[0] - 40, ease(dob))
        y = lerp(300 + 14 * math.sin(t * 2.1), serce[1] - 40, dob * dob)
        st.put(Z.prop("sztylet"), x, y, 0.83, w=96, anchor=(0.5, 0.5), rot=t * 540 * (1 - dob) + lerp(0, 100, dob), shadow=(3, 4, 4, 0.35))
    else:
        st.put(Z.prop("sztylet"), serce[0] - 40, serce[1] - 40, 0.8172, w=96, anchor=(0.62, 0.5), rot=100, shadow=(3, 4, 4, 0.35))


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
    jx, _, _, jk = w.jezdziec  # zwój z pieczęcią w uniesionej ręce jeźdźca
    jy = Z.ground("droga", jx) + 8 - abs(math.sin(jx / 34.0)) * 9 * jk + ZAPAD[0]
    st.put(Z.prop("list_pieczec"), jx + 17, jy - 60 - 6 * ease(pr(t, 1.8, 0.6)), 0.647, w=30, rot=-14 + 10 * ease(pr(t, 1.8, 0.6)),
           shadow=(2, 3, 3, 0.35))
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_wei(st, w, t, T):
    """Miasto pod chorągwią Wei o świcie: wschodzi słońce, kopacze Qin przekopują brzeg rzeki, woda z papieru
    podnosi się i zalewa mury, chorągiew przewraca się, zjeżdża tabliczka „trzy miesiące później”, potem woda opada
    (reżyser 15.11: „niech się więcej dzieje”, „słońce wschodzi!”)."""
    w.sun_y = lerp(470, 96, ease(pr(t, 0.0, 2.6)))
    w.fall["wei"] = pr(t, 5.6, 0.95)
    w.wlocznie = 470 + 30 * ease(pr(t, 0.5, 2.0))  # wojsko Qin przygląda się z lewej
    up = ease(pr(t, 2.6, 3.0)) * (1 - 0.75 * ease(pr(t, T - 1.6, 1.4)))
    w.zawieszki = [("trzy miesiące później", 860, 300, pr(t, 6.6, 0.9) * (1 - pr(t, T - 1.4, 0.6)))]
    k = ease(t / T)
    kam(st, t, 32, lerp(860, 880, k), lerp(470, 470, k), lerp(1.25, 1.45, k), 0.5, lens=1.34, truck=0.4,
        shake=3 * pr(t, 5.6, 0.2) * (1 - pr(t, 5.8, 0.6)))
    st.dof = 0.8
    swiat(st, t, w)
    for j in range(6):  # kopacze z koszami przekopują brzeg, zanim woda ruszy
        x = 520 + j * 46 + 8 * math.sin(t * 1.7 + j)
        zejdz = ease(pr(t, 2.4 + j * 0.1, 0.8))
        st.put(Z.prop("robotnik"), x, Z.ground("srodek", x) + 22 + 40 * zejdz - abs(math.sin(t * 5 + j)) * 3, 0.5395, h=44,
               rot=9 * math.sin(t * 4 + j * 1.4), shadow=(2, 2, 3, 0.3))
    for i in range(3):
        st.put(Z.waves(i), 930 + (24 - i * 5) * math.sin(t * 1.4 + i * 1.9) * (1 if i % 2 else -1),
               lerp(660, 500 + i * 28, up) + 4 * math.sin(t * 1.7 + i), 0.505 + i * 0.006, w=1700, anchor=(0.5, 0.0), haze=0.12,
               tint=(0.80, 0.88, 0.92))
    swiatlo(st, w, t)


def s_chu(st, w, t, T):
    """Przed chorągwią Chu szybko przesuwa się sześć rzędów włóczni, jeden za drugim, aż zasłaniają wzgórza
    (reżyser 15.11: „jeszcze więcej chorągwi i szybciej”)."""
    w.chwiej = {"chu": 3 * math.sin(t * 9) * pr(t, 1.5, 1.0)}
    kam(st, t, 33, lerp(780, 900, ease(t / T)), 500, 1.45, 0.62, lens=1.36, truck=0.8)
    st.dof = 1.0
    swiat(st, t, w)
    for n, (band, p, h, v) in enumerate((("dal", 0.444, 84, 260), ("dal", 0.448, 90, 300), ("srodek", 0.524, 104, 330),
                                         ("srodek", 0.528, 110, 360), ("droga", 0.635, 124, 400), ("przod", 0.705, 150, 460))):
        wlocznie(st, t, 260 + n * 110 + v * t, p=p, band=band, h=h, n=6, seed=10 + n * 3, up=pr(t, 0.2 + n * 0.22, 0.7))
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.94))


def s_chu_yan(st, w, t, T):
    """Chu chwieje się dłużej niż inne i pada; Yan zaraz po niej; za wzgórzami idzie gęsto wojsko Qin."""
    w.chwiej = {"chu": 7 * math.sin(t * 14) * pr(t, 0.05, 0.3) * (1 - pr(t, 0.75, 0.15))}
    for n, (band, p, h, x0) in enumerate((("dal", 0.444, 84, 900), ("srodek", 0.524, 104, 1000), ("srodek", 0.53, 110, 760))):
        wlocznie(st, t, x0 + 260 * t, p=p, band=band, h=h, n=5, seed=30 + n * 3)
    _pada(st, w, t, T, 34, ["chu", "yan"], [0.85, 1.45], (930, 1010), (850, 1130))


def s_qi(st, w, t, T):
    """Jeździec staje przed ostatnią chorągwią, za nim gęsto włócznie; zjeżdża zawieszka z rokiem; Qi kładzie się sama,
    a jeździec wyciąga białą flagę, która powiewa (reżyser 15.11)."""
    stop = ease_out(pr(t, 0.0, 1.5))
    w.jezdziec = (990 + 80 * stop, 0.645, 100, 1 - stop)
    w.wlocznie = 880 + 70 * stop
    w.zawieszki = [("221 p.n.e.", 968, 352, pr(t, 1.5, 1.0))]
    w.chwiej = {"qi": 4 * math.sin(t * 11) * pr(t, 2.6, 0.4) * (1 - pr(t, 3.2, 0.2))}
    w.fall["qi"] = pr(t, 3.2, 1.5) * 0.999
    k = ease(t / T)
    kam(st, t, 35, lerp(1040, 1050, k), lerp(486, 492, k), lerp(1.6, 1.7, k), 0.62, lens=1.55, truck=0.7)
    st.dof = 1.2
    for n, (band, p, h, x0) in enumerate((("dal", 0.444, 84, 760), ("srodek", 0.524, 104, 830))):
        wlocznie(st, t, x0 + 40 * stop, p=p, band=band, h=h, n=4, seed=40 + n * 3)
    swiat(st, t, w)
    f = ease(pr(t, 3.7, 0.6))  # biała flaga wyciągnięta w górę z ręki jeźdźca
    if f > 0:
        jx = 990 + 80 * stop
        hx, hy = jx + 14, Z.ground("droga", jx) - 46
        top = hy - 118 * f
        st.line([(hx, hy + 30), (hx + 4, top)], 0.6455, width=2.2, color=(96, 70, 46), alpha=1.0)
        fal = math.sin(t * 7.5)
        st.put(Z.prop("flaga_biala"), hx + 4, top + 2, 0.6457, w=62 * f, anchor=(0.0, 0.05), sx=0.82 + 0.18 * fal,
               sy=1 + 0.06 * math.sin(t * 7.5 + 1.2), rot=4 * fal + 6, shadow=(2, 3, 4, 0.3))
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
    """W miejscach sześciu powalonych chorągwi wstają czarne chorągwie Qin, za wzgórzami wyrasta wojsko, a kamera
    odjeżdża aż za ramę teatru: cały kraj jednego władcy (reżyser 15.11: „większy obszar, pokazując potęgę”)."""
    for n, k in enumerate(PODBITE):
        w.black[k] = pr(t, 0.5 + n * 0.42, 0.6)
    k = ease(pr(t, 0.3, T - 0.8))
    m = math.exp(lerp(math.log(1.3), math.log(0.74), k))
    kam(st, t, 37, lerp(790, 640, k), lerp(450, 296, k), m, lerp(0.62, 1.0, k), lens=m ** lerp(0.7, 0.55, k), truck=lerp(0.6, 1.0, k),
        drift=0.5)
    st.dof = lerp(0.6, 0.0, k)
    swiat(st, t, w)
    for n, (band, p, h, x) in enumerate((("dal", 0.444, 80, 1330), ("srodek", 0.524, 96, 1360))):
        wlocznie(st, t, x, p=p, band=band, h=h, n=5, up=pr(t, 3.0 + n * 0.5, 0.9), seed=50 + n * 3)
    if m < 1.02:
        Z.theatre_put(st, 1.0)
    swiatlo(st, w, t)


def s_cesarz(st, w, t, T):
    """Zbliżenie; nad głową zjeżdża tabliczka „KRÓL”, cesarz ją odrzuca i zjeżdża większa „PIERWSZY CESARZ”
    (reżyser 15.11); za plecami zjeżdżają chorągwie ze smokiem, lalka unosi się i prostuje."""
    w.smoki = [pr(t, 1.2, 1.1), pr(t, 1.75, 1.1)]
    w.lift = 14 * ease(pr(t, 2.9, 1.2))
    w.lean = -2.0 * ease(pr(t, 2.9, 1.2)) + 1.5 * settle((t - 4.1) / 1.4, 1.5) + 7 * math.sin(math.pi * pr(t, 2.7, 0.5))
    k = ease(t / T)
    kam(st, t, 38, lerp(318, 324, k), lerp(452, 418, k), lerp(1.85, 2.2, k), 0.8)
    st.dof = 2.6
    swiat(st, t, w)
    rzut = pr(t, 2.85, 0.9)
    if rzut <= 0:
        Z.hang(st, Z.tag("KRÓL", 60), 330, 278, P.rekwizyty + 0.02, pr(t, 0.8, 0.9), t, 97, drop=480, sway=1.4, h=74, shadow=(4, 6, 6, 0.4))
    elif rzut < 1:  # odrzucona: nitka pęka, tabliczka leci w lewo i w górę, kręcąc się
        st.put(Z.tag("KRÓL", 60), 330 - 520 * ease_out(rzut), 278 - 160 * math.sin(math.pi * rzut * 0.8) + 260 * rzut * rzut,
               P.rekwizyty + 0.02, h=74, anchor=(0.5, 0.0), rot=-260 * rzut, shadow=(4, 6, 6, 0.4))
    Z.hang(st, Z.tag("Pierwszy Cesarz", 60), 330, 262, P.rekwizyty + 0.021, pr(t, 3.15, 1.0), t, 98, drop=520, sway=1.2, h=92,
           shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t, extra=(1.03, 1.0, 0.95))


def s_posagi(st, w, t, T):
    """Trójnóg z brązu wysuwa się zza rampy, wpada do niego deszcz włóczni pokonanych; za nim wyrasta posąg."""
    w.urna = pr(t, 0.3, 1.0)
    w.ogien = 0.75 * ease(pr(t, 1.7, 0.8)) * (1 - 0.6 * ease(pr(t, T - 1.5, 1.2)))
    w.posag = pr(t, 3.4, 1.7)
    k = ease(t / T)
    kam(st, t, 39, lerp(1100, 1130, k), lerp(470, 440, k), lerp(1.25, 1.38, k), 0.84, truck=0.7)
    st.dof = 1.2
    swiat(st, t, w)
    fy = URNA[1] - URNA[2] * 0.8
    for j in range(22):  # włócznie wpadają do trójnogu jedna po drugiej (reżyser 15.11: „jeszcze więcej włóczni”)
        r = random.Random(60 + j)
        f = pr(t, 1.2 + j * 0.11 + r.uniform(0, 0.08), 0.5)
        if 0 < f < 1:
            st.put(Z.prop("wlocznia"), URNA[0] + r.uniform(-40, 40), lerp(-140, fy + 150, f * f), P.rekwizyty - 0.006, h=170,
                   rot=r.uniform(-16, 16), shadow=None)
    hot = min(1.0, w.ogien)
    swiatlo(st, w, t, extra=(1 + 0.05 * hot, 1 - 0.05 * hot, 1 - 0.1 * hot))


