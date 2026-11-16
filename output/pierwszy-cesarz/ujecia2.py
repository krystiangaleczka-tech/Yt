"""Ujęcia aktów 5–8: Jeden kraj, Ogień i strach, Gliniana armia, Upadek."""
import math
import random

import zestaw as Z
from papier import CX, CY, back, clamp, ease, ease_out, noise, settle
from swiat import (podpis, BAN, EMP, KOPIEC, MALY, PODBITE, STOL, TRON, URNA, P, dzonka, kam, lalka, lerp, morze, powoz, pr, sala, swiat,
                   swiatlo, wlocznie, woz, wstega)
from ujecia1 import iks, krol


# ---------- akt 5 · Jeden kraj ----------

def s_drogi(st, w, t, T):
    """Cesarz wskazuje drogę; przed wozem rozwija się trakt z koleinami jednej szerokości, a wóz z dużymi kołami toczy
    się przez wzgórza i mija czarne chorągwie (reżyser 15.11: „bardziej pokaż tę drogę oraz powiększ te koła”)."""
    w.lean = 3.5 * settle(t / 1.6, 1.2)
    x = 440 + 500 * (t / T) ** 0.95
    kam(st, t, 40, lerp(520, 900, t / T), 520, 1.85, 0.645, lens=1.72, truck=0.85)
    st.dof = 1.5
    swiat(st, t, w)
    droga = pr(t, 0.6, T - 1.6)
    wstega(st, "trakt", 300, 1240, droga, p=0.6605, dy=4, sy=0.55)
    woz(st, t, x, h=100)
    swiatlo(st, w, t)


def s_prowincje(st, w, t, T):
    """Na nitkach zjeżdża mapa kraju i kawałek po kawałku układa się na niej 36 prowincji (komanderii) — siedziby
    w przybliżeniu jak naprawdę; mapa odjeżdża, a na wzgórzach całego kraju wyskakuje 36 czarnych chorągwi i małe lalki
    urzędników (reżyser 15.11)."""
    w.urzednicy = [pr(t, 5.4 + n * 0.45, 0.7) for n in range(6)]
    kam(st, t, 41, lerp(800, 780, ease(t / T)), lerp(430, 470, ease(pr(t, 4.0, 1.5))), lerp(1.25, 1.36, ease(t / T)), 0.62, truck=0.6)
    st.dof = 0.8
    swiat(st, t, w)
    for n in range(36):  # 36 czarnych chorągiewek na trzech pasmach wzgórz
        band, p, h = (("dal", 0.442, 46), ("srodek", 0.522, 56), ("droga", 0.632, 66))[n % 3]
        x = 120 + (n // 3) * 96 + (n % 3) * 30
        k = pr(t, 4.8 + n * 0.06, 0.5)
        if k > 0:
            st.put(Z.banner("qin"), x, Z.ground(band, x) + 10 + (1 - back(k, 1.5)) * h * 1.1, p, h=h, anchor=(0.07, 1.0),
                   rot=1.2 * noise(t, 400 + n, 0.5) + settle((k - 0.7) / 0.3 if k < 1 else 0, 2, 4))
    board, czesci = Z.mapa36()
    mk = pr(t, 0.3, 1.1)
    if mk > 0:  # mapa na dwóch nitkach
        wd, mx, top = 520, 790, 96
        yy = top - (1 - back(mk, 1.1)) * 620 - 760 * ease(pr(t, 4.3, 0.9))
        sc = wd / Z.MAPA36_WH[0]
        for sx_ in (mx - wd * 0.36, mx + wd * 0.36):
            st.line([(sx_, -260), (sx_, yy + 4)], 0.81, width=1.1, color=(70, 56, 44), alpha=0.7, z=-0.5)
        st.put(board, mx, yy, 0.81, w=wd, anchor=(0.5, 0.0), shadow=(6, 9, 9, 0.45), blur=0)
        for n, (spr, x0, y0) in enumerate(czesci):
            kk = pr(t, 1.3 + n * 0.075, 0.25)
            if kk > 0:
                st.put(spr, mx - wd / 2 + x0 * sc, yy + y0 * sc - 14 * (1 - kk), 0.8102 + n * 0.00002, w=spr.w * sc, anchor=(0.0, 0.0),
                       alpha=min(1.0, kk * 2), shadow=(2, 3, 3, 0.35), blur=0)
        Z.hang(st, Z.tag("36 komanderii", 40), mx, yy + Z.MAPA36_WH[1] * sc - 36, 0.8115, pr(t, 3.9, 0.5), t, 99, drop=200,
               sway=0.6, h=40, string=False, shadow=(3, 4, 4, 0.4))
    swiatlo(st, w, t)


def s_rody(st, w, t, T):
    """Dziesiątki wozów ze skrzyniami ciągną ku stolicy dwiema drogami — szybsze wyprzedzają wolniejsze, mijają się
    (reżyser 15.11: „dużo dużo więcej tych wozów, jeden na drugim, mijając się”)."""
    x = lerp(470, 880, (t / T) ** 0.95)
    kam(st, t, 42, x - 90, 522, 1.7, 0.645, lens=1.6, truck=0.85)
    st.dof = 1.4
    swiat(st, t, w)
    for j in range(8):  # droga bliższa: wozy w różnym tempie, szybszy jedzie bliżej kamery i wyprzedza
        r = random.Random(500 + j)
        v = r.uniform(26, 58)
        x0 = 200 + j * 120 - (j % 3) * 50
        woz(st, t, x0 + v * t, p=0.645 - 0.0004 * j + (0.0015 if v > 45 else 0.0), h=r.uniform(62, 78))
    for j in range(7):  # droga dalsza, pod murami: mniejsze wozy w przeciwną stronę i ku bramie
        r = random.Random(600 + j)
        v = r.uniform(18, 40) * (1 if j % 2 else -1)
        x0 = 380 + j * 130
        woz(st, t, x0 + v * t, p=0.535 + 0.0004 * j, h=r.uniform(38, 46), flip=1 if v > 0 else -1, kon=True)
    swiatlo(st, w, t)


def s_stela(st, w, t, T):
    """Powóz staje pod górą; kamera unosi się na jej szczyt i dopiero wtedy wyrasta z ziemi duża kamienna stela,
    kołysząc się (reżyser 15.11: „zrób ją większą i wysuń w poprawnym momencie zbliżenia”)."""
    x = lerp(540, 770, ease_out(pr(t, 0.0, 2.6)))
    k = ease(pr(t, 2.0, 2.6))
    w.stela = pr(t, 4.7, 1.4)
    kam(st, t, 43, lerp(730, 1030, k), lerp(520, 236, k), lerp(1.6, 2.0, k), lerp(0.62, 0.34, k), truck=0.5)
    st.dof = 1.2
    swiat(st, t, w)
    powoz(st, t, x)
    swiatlo(st, w, t)


def s_kanal2(st, w, t, T):
    """Druga wstęga kanału z nasypami rozwija się wzdłuż drogi i wpływają na nią dwie papierowe łodzie."""
    w.kanal2 = pr(t, 0.4, T - 3.2)
    podpis(w, t, "kanał Lingqu", 1010, 456, 1.2, 3.6)
    kam(st, t, 44, lerp(820, 880, ease(t / T)), 588, 2.0, 0.67, lens=1.78, truck=0.8)
    st.dof = 1.6
    swiat(st, t, w)
    for j in range(2):
        f = pr(t, T - 3.4 + j * 0.9, 2.6)
        if f > 0:
            x = lerp(790, 990 - j * 60, ease_out(f))
            st.put(Z.boat(), x, Z.ground("droga", x) + 22 + 2 * math.sin(t * 3 + j), 0.6728, h=38, rot=3 * math.sin(t * 2.2 + j),
                   shadow=(2, 3, 3, 0.35))
    swiatlo(st, w, t)


def s_pismo(st, w, t, T):
    """Kanały zwijają się przy zmianie dekoracji; stół i pisarz wysuwają się zza rampy; cesarz kiwa głową; księga
    wsuwa się pod pędzel i pisarz, klęcząc przed stołem, pisze."""
    w.kanal = w.kanal2 = 1 - pr(t, 0.1, 1.0)
    w.dwor = pr(t, 0.4, 1.3)
    w.ksiega = pr(t, 2.2, 1.1)
    w.pisze = ease(pr(t, 3.5, 0.5))
    w.zwoj = 1.0
    kiw = math.sin(math.pi * pr(t, 2.2, 0.5)) + math.sin(math.pi * pr(t, 2.9, 0.5))  # dwa skinienia głową (reżyser 15.11)
    w.lean = 3.0 * settle((t - 1.9) / 1.5, 1.2) + 5 * kiw
    w.lift = -9 * kiw
    kam(st, t, 45, lerp(690, 676, ease(t / T)), 520, lerp(1.4, 1.5, ease(t / T)), 0.84)
    st.dof = 1.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_moneta(st, w, t, T):
    """Detal blatu — moneta wytacza się zza pisarza i zwalnia; przy stosie podskakuje lekko nad blat (brzęk), w locie
    kładzie się na płask i od razu spada na stół (drugi brzęk), po czym krótko dygocze (reżyser 16.11)."""
    w.moneta = 1.0
    w.moneta_x = 1 - (1 - pr(t, 0.3, 1.9)) ** 2  # toczenie: równomierne wytracanie prędkości, dojeżdża w locie
    lot = pr(t, 1.8, 0.4)  # podskok 1,8–2,2 s; brzęki w efekty.ZDARZENIA["moneta"] w tych samych chwilach
    w.moneta_skok = 9.0 * 4 * lot * (1 - lot)
    w.moneta_lez = ease(lot)
    w.moneta_chw = settle((t - 2.2) / 0.6, 2.5, 0.6)
    kam(st, t, 46, lerp(652, 660, t / T), 598, 3.4, 0.85, lens=2.7, truck=0.8)
    st.dof = 3.0
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_miara(st, w, t, T):
    """Ze stołu znikają zwoje i monety, leży na nim miarka i miara objętości; zjeżdża waga — podstawa stoi, a belka
    i szale kołyszą się osobno; odważnik „斤” zjeżdża do lewej szali i belka wyrównuje się (reżyser 15.11)."""
    w.bez_rzeczy = max(0.001, ease(pr(t, 0.2, 0.7)))
    w.waga = pr(t, 0.3, 1.0)
    w.odwaznik = 0.0
    w.odwaznik_szala = pr(t, 1.7, 1.0)
    zaw = pr(t, 2.6, 0.01)  # chwila, w której odważnik siada w szali
    w.waga_belka = -6.6 * ease(pr(t, 2.6, 0.7)) + 3.2 * settle((t - 2.6) / 2.6, 2.5) * zaw
    w.waga_szale = (2.5 * settle((t - 1.3) / 2.0, 2.0) + 6 * settle((t - 2.6) / 2.4, 2.8) * zaw + 0.6 * noise(t, 77, 0.6),
                    -3 * settle((t - 1.3) / 2.2, 2.2) - 4.5 * settle((t - 2.9) / 2.6, 2.4) * zaw + 0.6 * noise(t, 78, 0.6))
    kam(st, t, 47, 724, 560, 2.5, 0.85, lens=2.1, truck=0.8)
    st.dof = 2.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_mur(st, w, t, T):
    """Zza grani wysuwają się odcinki muru i wieże, od zachodu ku miastu; kamera z bliska idzie za czołem budowy."""
    w.mur = 0.86 * pr(t, 0.5, T - 2.2)
    w.sink = pr(t, 0.2, 1.0)  # cesarz schodzi pod rampę: kamera patrzy na mur w górach, nic go nie zasłania
    front = -10 + 34 * (w.mur * 44 - 2)
    kam(st, t, 48, clamp(front - 40, 300, 980), lerp(400, 420, ease(t / T)), 1.95, 0.43, lens=1.8, truck=0.5)
    st.dof = 1.0
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_robotnicy(st, w, t, T):
    """Po grani pod murem suną sylwetki z koszami, a ostatnie odcinki muru wyrastają przed nimi; jedna sylwetka po
    drugiej przystaje i znika za granią."""
    w.mur = 0.86 + 0.14 * pr(t, 0.6, T - 2.5)
    w.emp = 0.0  # cesarz zszedł pod rampę w poprzednim ujęciu
    kam(st, t, 49, lerp(420, 700, ease(t / T)), 400, 2.15, 0.43, lens=2.0, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    for j in range(14):
        r = random.Random(70 + j)
        stop = 1.6 + j * 0.42 if j % 3 == 1 else None  # co trzeci zostaje pod murem
        tt = min(t, stop) if stop else t
        x = 360 + j * 46 + (26 + r.uniform(-4, 4)) * tt
        if not Z.MF_X - 350 < x < Z.MF_X + 350:
            continue
        sink = ease(pr(t, stop, 1.2)) * 40 if stop else 0.0
        st.put(Z.prop("robotnik"), x, Z.ridge(x) + 15 + sink - abs(math.sin(x / 7.0)) * 2.5 * (0 if stop and t > stop else 1), P.gory - 0.002,
               h=50, haze=0.1, shadow=(2, 2, 3, 0.25), rot=2 * math.sin(x / 9.0))
    swiatlo(st, w, t)


def s_ognie(st, w, t, T):
    """Na wieży strażniczej zapala się ogień sygnałowy; po chwili odpowiada mu ogień na następnej wieży i na kolejnej."""
    w.emp = 0.0
    kam(st, t, 78, lerp(470, 330, ease(t / T)), 388, lerp(2.3, 2.5, ease(t / T)), 0.43, lens=2.2, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    ft = math.floor(t * 12) / 12
    for n, (x, a) in enumerate(((568, 0.5), (398, 1.6), (228, 2.8))):  # wieże muru stoją co 170 px (co piąty odcinek)
        k = ease(pr(t, a, 0.5))
        if k <= 0:
            continue
        y = min(Z.ridge(x), Z.ground("dal", x) + 4) - 46 + 12
        for j in range(3):
            st.put(Z.flame(j + n), x + (j - 1) * 5, y, P.gory - 0.003, h=(20 + 8 * j) * k * (0.8 + 0.3 * noise(ft, 60 + j + n * 5, 9)),
                   rot=8 * noise(ft, 70 + j + n * 5, 7), shadow=None, tint=(1.15, 1.1, 1.0))
        st.put(Z.glow(), x, y - 14, P.gory + 0.005, w=150 * k, anchor=(0.5, 0.5), mode="add", alpha=0.35 * k, shadow=None,
               tint=(1.0, 0.6, 0.3))
    swiatlo(st, w, t)


# ---------- akt 6 · Ogień i strach ----------

def s_ksiegi(st, w, t, T):
    """Uczony wysuwa się z deszczułką; cesarz pochyla się z wyciągniętą ręką; zwój leci do ognia."""
    w.pisze = 0.0
    w.emp = pr(t, 0.0, 0.9)  # cesarz wraca zza rampy (zszedł przy budowie muru)
    w.uczony = pr(t, 0.2, 1.0)
    w.lean = 4.5 * ease(pr(t, 1.3, 0.5)) - 2.5 * ease(pr(t, 3.6, 1.0))
    w.zwoj_lot = pr(t, 2.0, 0.9)
    w.ogien = 0.32 * pr(t, 1.5, 0.6) + 0.88 * ease(pr(t, 2.85, 0.5))
    w.uczony_lean = 5.5 * ease(pr(t, 2.9, 0.5))
    hot = ease(pr(t, 2.85, 0.6))
    kam(st, t, 50, 790, 500, 1.34, 0.84, lens=1.28, truck=0.7)
    st.dof = 1.4
    swiat(st, t, w)
    swiatlo(st, w, t, extra=(1 + 0.10 * hot, 1 - 0.14 * hot, 1 - 0.24 * hot))


def s_popiol(st, w, t, T):
    """Detal trójnogu — zwój czernieje i zapada się, płomienie przygasają."""
    w.zwoj_lot = 1.0 + t / T * 1.0
    w.ogien = 1.2 * (1 - ease(pr(t, 0.5, T - 0.7)))
    w.lean, w.uczony_lean = 2.0, 5.5
    hot = 1 - ease(pr(t, 0.5, T - 0.7))
    kam(st, t, 51, 1086, 566, 2.5, 0.84, lens=2.2, truck=0.7)
    st.dof = 2.4
    swiat(st, t, w)
    swiatlo(st, w, t, extra=(1 + 0.10 * hot, 1 - 0.14 * hot, 1 - 0.24 * hot))


def s_uczeni(st, w, t, T):
    """Nad każdym z trzech uczonych miga dwa razy czerwony X i uczony opada pod rampę; Fusu kłania się cesarzowi,
    odwraca i odjeżdża ze sceny."""
    podpis(w, t, "Fusu, najstarszy syn", 510, 336, 5.2, 1.9)  # tabliczka: pierwsze pojawienie się
    w.uczony = 1 - pr(t, 2.3, 0.9)
    w.uczony_lean = 5.5 * (1 - ease(pr(t, 0.0, 1.0)))
    w.lean = 4.5 * ease(pr(t, 1.6, 0.5)) - 4.5 * ease(pr(t, 4.2, 0.8)) + 5 * ease(pr(t, 6.2, 0.5)) - 3 * ease(pr(t, 8.0, 0.8))
    turn = ease(pr(t, 6.8, 0.6))
    k = ease(t / T)
    kam(st, t, 52, lerp(800, 700, ease(pr(t, 3.8, 2.0))), 500, lerp(1.22, 1.3, k), 0.84, lens=1.2, truck=0.7)
    st.dof = 1.2
    swiat(st, t, w)
    lalka(st, t, "uczony2", 856, 286, pr(t, 0.2, 0.9) if t < 3.1 else 1 - pr(t, 3.1, 0.9), flip=-1, seed=24, p=P.lalki + 0.006)
    lalka(st, t, "kleczy", 1206, 236, pr(t, 0.5, 0.9) if t < 3.9 else 1 - pr(t, 3.9, 0.9), y=700, flip=-1, seed=25)
    for x, y, t0 in ((946, 540, 1.3), (856, 548, 2.1), (1206, 590, 2.9)):  # wyrok: X nad każdym, zanim opadnie
        iks(st, x, y, t, t0, h=170)
    lalka(st, t, "fusu", 510 + 1050 * ease(pr(t, 7.3, T - 7.4)) ** 1.2, 300, pr(t, 4.6, 0.9), p=P.lalki - 0.012,
          flip=math.cos(math.pi * turn) * -1, lean=-7 * ease(pr(t, 5.5, 0.5)) * (1 - turn))
    swiatlo(st, w, t)


def s_zmierzch(st, w, t, T):
    """Słońce zjeżdża za góry, scena sinieje; stół z pisarzem i trójnóg chowają się; cesarz sam, staje księżyc."""
    w.sun_y = 96 + 420 * ease(pr(t, 0.3, 3.0))
    w.noc = ease(pr(t, 0.8, 3.2))
    w.dwor = 1 - pr(t, 2.2, 1.1)
    w.urna = 1 - pr(t, 2.9, 1.0)
    w.zwoj = 0.0
    w.moon = pr(t, T - 2.3, 1.5)
    k = ease(t / T)
    kam(st, t, 53, lerp(560, 600, k), lerp(450, 392, k), lerp(1.4, 1.1, k), 0.8)
    st.dof = 1.2
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_mlot(st, w, t, T):
    """Noc: drogą jadą dwa powozy, na skrzyni drugiego stoi cesarz; żelazny młot miażdży pierwszy, drugi staje w miejscu,
    a cesarz przewraca się na płask na wieku skrzyni i zjeżdża nad nim tabliczka „AŁA!…” (reżyser 15.11 i 16.11)."""
    ti = 2.7
    w.emp = 0.0  # cesarz jedzie drugim powozem, nie stoi na rampie
    podpis(w, t, "AŁA!…", 520, 432, ti + 0.6, 3.2)  # reżyser 16.11: „tabliczka aw!...” nad leżącym cesarzem
    x1 = lerp(520, 760, min(t, ti) / ti)
    x2 = x1 - 196 + 0  # drugi powóz (cesarski) jedzie za pierwszym i staje po uderzeniu
    hit = pr(t, ti, 0.16)
    upad = pr(t, ti + 0.15, 0.55)
    kam(st, t, 54, lerp(640, 700, ease(t / T)), 520, 1.75, 0.645, lens=1.62, truck=0.85, shake=8 * hit * (1 - pr(t, ti + 0.1, 0.6)))
    st.dof = 1.3
    swiat(st, t, w)
    woz(st, t, x1, h=74, sy=1 - 0.58 * ease(hit), rot=7 * ease(hit))
    powoz(st, t, x2, cesarz=(-86 * ease(upad) + 6 * settle((upad - 0.7) / 0.3 if upad < 1 else (t - ti - 0.7) / 0.8, 1.5) * upad,
                             4 * ease(upad)), na_skrzyni=True)
    f = pr(t, 1.7, ti - 1.7)
    if f > 0:
        hx = lerp(1180, x1 + 10, min(1.0, f)) + 90 * pr(t, ti, 0.5)
        hy = lerp(330, Z.ground("droga", x1) - 44, min(1.0, f)) - 190 * math.sin(math.pi * min(1.0, f)) + 150 * pr(t, ti, 0.5) ** 2
        st.put(Z.prop("mlot"), hx, hy, 0.648, h=54, anchor=(0.5, 0.5), rot=-520 * f)
    swiatlo(st, w, t)


def s_morze(st, w, t, T):
    """Cztery pasma fal wysuwają się od dołu, na horyzoncie powoli wyrasta duża wyspa z górą (reżyser 15.11)."""
    w.noc = 0.75
    kam(st, t, 55, 640, lerp(420, 400, ease(t / T)), lerp(1.0, 1.1, ease(t / T)), 0.6, truck=0.5)
    st.dof = 0.6
    morze(st, t, w, k=pr(t, 0.2, 2.4), wyspa=pr(t, 2.6, 2.8))


def s_xufu(st, w, t, T):
    """Na stokach wyspy wychodzą zza grani jednoocy olbrzymi i prężą muskuły (reżyser 16.11); trzy dżonki płyną ku wyspie
    zakosami — w lewo, w prawo, w lewo, w prawo — maleją i chowają się za ostatnią falą (reżyser 15.11)."""
    w.noc = 0.75
    w.cyklopi = pr(t, 1.2, 1.8)

    def mm(n):  # reżyser 16.11: „zrób, że oni prężą muskuły” — każdy we własnej chwili, napina się trzy razy
        t0 = 3.1 + (0.0, 0.5, 0.25)[n]
        f = ease(pr(t, t0, 0.45)) * (1 - ease(pr(t, t0 + 3.6, 0.5)))
        return f * (0.86 + 0.14 * max(0.0, math.sin((t - t0) * 2 * math.pi / 1.2)) ** 2) if f > 0 else 0.0
    w.cyklopi_mm = mm
    kam(st, t, 56, lerp(600, 760, ease(t / T)), lerp(500, 440, ease(t / T)), lerp(1.2, 1.45, ease(t / T)), 0.5, truck=0.6)
    st.dof = 0.8
    morze(st, t, w)
    for j in range(3):
        a, d = 0.1 + j * 0.55, T - 1.4
        kurs = lambda f: lerp(260 + j * 120, 850 + j * 16, ease(f)) + 120 * (1 - f) * math.sin(2 * math.pi * 2 * ease(f))  # dwa zakosy
        f = pr(t, a, d)
        x = kurs(f)
        kier = 1 if kurs(min(1.0, f + 0.01)) >= kurs(max(0.0, f - 0.01)) else -1
        dzonka(st, t, x, f, seed=j, flip=kier)


def s_puste(st, w, t, T):
    """Puste morze pod księżycem; ostatni żagiel chowa się za ostatnią falą."""
    w.noc = 0.82
    kam(st, t, 57, 720, 440, lerp(1.32, 1.36, t / T), 0.5, truck=0.6)
    st.dof = 0.8
    morze(st, t, w)
    dzonka(st, t, 882, lerp(0.88, 1.0, pr(t, 0.2, 1.6)), seed=2)


def s_rtec(st, w, t, T):
    """Przy cesarzu wysuwa się czarka; srebrne kulki bardzo powoli opadają (bez nitek) i znikają w środku czarki,
    cesarz pochyla się nad nią (reżyser 15.11)."""
    w.lean = 6 * ease(pr(t, 7.0, 0.9))
    kam(st, t, 58, lerp(410, 420, ease(t / T)), 566, lerp(2.0, 2.25, ease(t / T)), 0.84, lens=1.8)
    st.dof = 2.2
    swiat(st, t, w)
    k = pr(t, 0.3, 0.8)
    up = 24  # reżyser 16.11: „podnieś trochę ten kielich” — cała czarka nad krawędzią rampy
    st.put(Z.prop("czarka"), 500, 694 - up + (1 - back(k, 1.3)) * 90, P.rekwizyty, h=58, shadow=(3, 4, 4, 0.4))
    for j in range(3):  # reżyser 15.11: „niech dużo wolniej zjeżdżają”, „usuń linie spuszczenia”, „kulki wychodzą poza wazę”
        kk = pr(t, 1.0 + j * 1.7, 2.4)
        wpada = pr(t, 3.6 + j * 1.7, 0.5)
        if 0 < kk and wpada < 1:
            Z.hang(st, Z.prop("kulka"), 500 + (j - 1) * 4, 606 - up + 44 * ease(wpada), P.rekwizyty - 0.004, kk, t, 120 + j, drop=420,
                   sway=0.2, h=15, string=False, shadow=(2, 3, 3, 0.35))
    swiatlo(st, w, t)


# ---------- akt 7 · Gliniana armia ----------

NOCNE_OKNA = (0.30, 0.36, 0.60)


def s_przejscia(st, w, t, T):
    """Sala nocą: cesarz przesuwa się za kolumnami w prawo, znika i wychodzi zza następnej, potem zawraca w lewo;
    lampy gasną za nim."""
    tam = 0.58  # część ujęcia na drogę w prawo
    if t < T * tam:
        u = t / (T * tam)
        x, flip = lerp(110, 1190, ease(u) * 0.5 + u * 0.5), 1.0
    else:
        u = (t - T * tam) / (T * (1 - tam))
        x, flip = lerp(1190, 520, ease(u) * 0.5 + u * 0.5), math.cos(math.pi * ease(pr(u, 0.0, 0.12)))  # w lewo: odbity w lewo
    xmax = lerp(110, 1190, min(1.0, t / (T * tam)))
    lampy = [1 - ease(clamp((xmax - lx - 150) / 160)) for lx in (240, 640, 1040)]
    kam(st, t, 59, clamp(x, 430, 880), 430, 1.3, 0.6, truck=0.7)
    st.dof = 0.8
    sala(st, t, w, okna=NOCNE_OKNA, lampy=lampy, kolumna=False)
    lalka(st, t, "zheng", x, 316, y=704, p=0.58, seed=7, lean=3 * flip, flip=flip)
    st.grade, st.dim = (0.86, 0.84, 0.92), 0.84


def s_meteor(st, w, t, T):
    """Noc: kamień z wielkim ognistym ogonem spada na wzgórze, kamera mocno się trzęsie; zjeżdża zawieszka ze znakami."""
    f = pr(t, 0.7, 0.9)
    hit = pr(t, 1.6, 0.2)
    w.zawieszki = [("Cesarz umrze, a ziemia się podzieli", 1010, 300, pr(t, 3.0, 1.0))]  # reżyser 16.11: „to po angielsku”
    kam(st, t, 60, lerp(860, 880, ease(t / T)), 430, lerp(1.25, 1.35, ease(t / T)), 0.53, truck=0.5,
        shake=26 * hit * (1 - pr(t, 1.7, 1.1)))
    st.dof = 0.8
    swiat(st, t, w)
    gx, gy = 850, Z.ground("srodek", 850) + 10
    ft = math.floor(t * 12) / 12
    if f > 0:
        x, y = lerp(500, gx, f * f), lerp(-60, gy, f * f)
        if f < 1:
            for n in range(6):  # wielki ogon z bibuły ciągnie się za kamieniem
                st.put(Z.flame(n), x - 30 - n * 22, y - 26 - n * 17, 0.522, h=(240 - n * 30) * (0.85 + 0.25 * noise(ft, 90 + n, 9)),
                       anchor=(0.5, 0.0), rot=-52 + 6 * noise(ft, 95 + n, 7), shadow=None, tint=(1.15, 1.1, 1.0))
        else:  # krater płonie
            for n in range(4):
                st.put(Z.flame(n), gx - 24 + n * 16, gy + 6, 0.523, h=(70 - n * 8) * (1 - pr(t, 4.0, 3.0)) * (0.8 + 0.3 * noise(ft, 98 + n, 9)) + 0.1,
                       rot=8 * noise(ft, 99 + n, 7), shadow=None, tint=(1.15, 1.1, 1.0))
        st.put(Z.prop("kamien"), x, y, 0.524, h=56, anchor=(0.5, 0.7), rot=-200 * f)
        st.put(Z.glow(), x, y, 0.535, w=420 + 700 * hit * (1 - pr(t, 1.8, 1.2)), anchor=(0.5, 0.5), mode="add",
               alpha=0.4 * (1 - pr(t, 1.8, 2.5)), shadow=None, tint=(1.0, 0.6, 0.3))
    swiatlo(st, w, t)


def s_palac(st, w, t, T):
    """Za wzgórzami rośnie piętro po piętrze olbrzymi pałac, wyższy od góry."""
    w.smoki_palac = 1.0  # chorągwie ze smokiem rozstępują się po bokach pałacu (reżyser 16.11)
    w.palac = 0.36 * back(pr(t, 0.5, 0.9), 1.2) + 0.32 * back(pr(t, 2.2, 0.9), 1.2) + 0.32 * back(pr(t, 3.9, 0.9), 1.2)
    w.galaz = 0.0  # reżyser 15.11: „usuń to drzewo” — gałąź kulisy zasłaniała chorągwie ze smokiem
    k = ease(t / T)
    kam(st, t, 61, lerp(340, 320, k), lerp(380, 320, k), lerp(1.2, 1.3, k), 0.5, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_kopiec(st, w, t, T):
    """Kamera jedzie od pałacu do kopca: po prawej wyrasta kopiec grobowca, a po jego zboczu suną dziesiątki ludzi
    z koszami (reżyser 15.11: „pałac niech tu będzie”, „zwiększ liczbę tych ludków”)."""
    w.kopiec = pr(t, 0.4, 2.2)
    kx, ky, kw = KOPIEC
    mound = Z.mound()
    hh = kw * mound.h / mound.w
    k = ease(t / T)
    kam(st, t, 62, lerp(540, 1140, k), lerp(430, 430, k), lerp(1.12, 1.5, k), 0.52, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    for j in range(30):
        r = random.Random(800 + j)
        gora = j % 2 == 0  # połowa idzie z koszami pod górę, połowa schodzi
        x = 1040 + (j // 2) * 16 + r.uniform(-6, 6) + (1 if gora else -1) * 13 * max(0.0, t - 2.4)
        fx = (x - (kx - kw / 2)) / kw
        if t > 2.2 + r.uniform(0, 0.8) and 0.05 < fx < 0.55:
            st.put(Z.prop("robotnik"), x, ky - hh + mound.top(fx) * hh + 14 - abs(math.sin(x / 6.0 + j)) * 2, P.miasto + 0.018 + 0.0001 * (j % 5),
                   h=40 + r.uniform(-4, 4), shadow=(2, 2, 3, 0.25), rot=-8 if gora else 6, sx=1 if gora else -1)
    swiatlo(st, w, t)


def s_armia(st, w, t, T):
    """Zza wzgórz i rampy wysuwają się rzędy glinianych żołnierzy, każdy we własnej chwili."""
    w.armia_t = t
    k = ease(t / T)
    kam(st, t, 63, lerp(830, 880, k), lerp(480, 500, k), lerp(1.25, 1.4, k), 0.7, truck=0.8)
    st.dof = 1.0
    swiat(st, t, w)
    swiatlo(st, w, t)
    st.spot = (850, 560, 0.7, 560, 0.3)


def s_twarze(st, w, t, T):
    """Kamera powoli przesuwa się po twarzach całego pierwszego rzędu; ostatni żołnierz dojeżdża spóźniony, gdy kamera
    do niego dochodzi (reżyser 15.11: „wydłuż 3×, niech przesuwa się po tych twarzach”)."""
    w.armia_t = 7.0 + max(0.0, (t - 4.0) * 1.4)
    kam(st, t, 64, lerp(520, 1240, ease(t / T) * 0.4 + (t / T) * 0.6), 590, 2.9, 0.79, lens=2.4, truck=0.9)
    st.dof = 2.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_rzeki(st, w, t, T):
    """Między rzędami żołnierzy rozwijają się srebrne wstęgi rzek z rtęci."""
    kam(st, t, 65, lerp(780, 900, ease(t / T)), 590, 1.7, 0.74, truck=0.8)
    st.dof = 1.4
    swiat(st, t, w)
    for k, p, dy, band, x0 in ((pr(t, 0.4, 2.6), 0.672, 24, "droga", 400), (pr(t, 1.3, 2.6), 0.735, 26, "przod", 430)):
        wstega(st, "rtec", x0, 1320, k, p=p, dy=dy, band=band, sy=1.7)
        wstega(st, "rtec", x0, 1320, k, p=p + 0.0005, dy=dy, band=band, sy=1.7, blask=0.35 + 0.15 * math.sin(t * 3.1 + p * 40))
    swiatlo(st, w, t)
    st.spot = (850, 580, 0.74, 560, 0.3)


def s_podroz(st, w, t, T):
    """Noc: gliniana armia zapada się pod ziemię; powóz z chorym cesarzem toczy się drogą na wschód, coraz wolniej,
    cesarz zgina się w kaszlu, powóz staje (reżyser 15.11: „postaw go tu i pokaż, że był chory”)."""
    w.armia = 1 - pr(t, 0.0, 1.6)  # zmiana dekoracji: gliniana armia zapada się pod ziemię, zostaje w grobowcu
    x = lerp(430, 730, ease_out(pr(t, 0.0, T - 1.2)))
    kaszel = sum(math.sin(math.pi * pr(t, a + d, 0.22)) for a in (2.2, 4.4, 6.6) for d in (0.0, 0.3, 0.6))
    kam(st, t, 66, x + 70, 524, 1.8, 0.645, lens=1.68, truck=0.85)
    st.dof = 1.4
    swiat(st, t, w)
    powoz(st, t, x, cesarz=(-6 - 9 * kaszel, 3 * kaszel))
    swiatlo(st, w, t)


def s_koniec(st, w, t, T):
    """Zjeżdża zawieszka z rokiem; cesarz zanosi się kaszlem, chwieje się, wydaje ostatnie tchnienie, przechyla się
    i powoli opada pod rampę (reżyser 15.11: „pokaż, że umiera”)."""
    w.zawieszki = [("210 p.n.e.", 560, 372, pr(t, 0.6, 1.0))]
    kaszel = sum(math.sin(math.pi * pr(t, a + d, 0.22)) for a in (0.9, 2.0) for d in (0.0, 0.3, 0.6))
    w.lean = 7 * kaszel + 3 * math.sin(t * 2.3) * pr(t, 2.6, 0.5) + 14 * ease(pr(t, 3.5, 1.2))
    w.oczy_x = ease(pr(t, 3.2, 0.3))  # umarł: X na oczach (reżyser 15.11)
    w.lift = -6 * kaszel
    w.sink = pr(t, 4.2, T - 4.6) * 0.999
    k = ease(t / T)
    kam(st, t, 67, lerp(392, 400, k), lerp(520, 528, k), lerp(1.46, 1.4, k), 0.8)  # rampa ponad paskiem napisu
    st.dof = 1.6
    swiat(st, t, w)
    swiatlo(st, w, t, dim=1 - 0.15 * ease(pr(t, 3.5, 2.0)))
    st.spot = (330, 500, 0.8, 440, 0.3 + 0.25 * ease(pr(t, 3.5, 2.0)))


# ---------- akt 8 · Upadek ----------

def s_spisek(st, w, t, T):
    """Przy powozie wysuwają się Li Si i Zhao Gao; pochylają się ku sobie, na powóz opada czarna zasłona."""
    podpis(w, t, "eunuch Zhao Gao", 880, 324, 1.6)  # tabliczka: pierwsze pojawienie się
    w.zaslona = pr(t, 2.8, 1.1)
    k = ease(t / T)
    kam(st, t, 68, 730, lerp(530, 520, k), lerp(1.42, 1.52, k), 0.8)
    st.dof = 1.3
    swiat(st, t, w)
    lalka(st, t, "lisi", 590, 310, pr(t, 0.4, 1.1), lean=5 * ease(pr(t, 2.0, 0.7)))
    lalka(st, t, "zhaogao", 880, 310, pr(t, 0.9, 1.1), flip=-1, lean=-5 * ease(pr(t, 2.2, 0.7)))
    swiatlo(st, w, t)


def s_ryby(st, w, t, T):
    """Li Si i Zhao Gao chowają się pod rampę; powóz jedzie dalej, a tuż za nim wóz z górą solonych ryb. Z ryb na płachcie
    powozu jedna odskakuje w górę i spada na drogę, gdzie zostaje i trzepocze (reżyser 16.11); później ryba wyskakuje
    z wozu i wpada z powrotem (reżyser 15.11); kamera jedzie z powozem."""
    x = lerp(730, 1060, (t / T) ** 0.95)
    w.powoz, w.zaslona = x, 1.0
    w.ryby = pr(t, 1.6, 1.4)  # po chwili na płachtę zjeżdżają solone ryby (reżyser 15.11)
    kam(st, t, 69, x - 80, 528, 1.9, 0.645, lens=1.76, truck=0.85)
    st.dof = 1.4
    swiat(st, t, w)
    xr = x - 200
    yr = woz(st, t, xr, h=80, p=0.6465, ladunek=[(Z.prop("ryby"), 46, -8, 16), (Z.prop("ryby"), 40, 14, 10)])
    f = pr(t, 7.4, 0.9)  # ryba wyskakuje łukiem z wozu i wpada z powrotem
    if 0 < f < 1:
        st.put(Z.prop("ryba"), xr - 10 - 40 * f, yr - 80 * 0.62 - 70 * math.sin(math.pi * f), 0.6468, h=18, anchor=(0.5, 0.5),
               rot=-(-60 + 120 * f), sx=-1, sy=1 + 0.15 * math.sin(t * 30), shadow=(2, 3, 3, 0.3))
    t0, lot = 4.9, 0.75  # ryba z płachty powozu: odskok w górę i upadek na drogę (reżyser 16.11)
    if t >= t0:
        xs = lerp(730, 1060, (t0 / T) ** 0.95)  # powóz w chwili odskoku: ryba zostaje tam, gdzie spadła
        sx0 = xs - 8 + 36
        sy0 = Z.ground("droga", xs) + 10 - 84 * 0.98 - 22  # wierzch ryb na płachcie
        lx = sx0 - 60
        gy = Z.ground("droga", lx) - 10  # leży na drodze przed kopytami (bliżej kamery niż konie), cała widoczna
        f = pr(t, t0, lot)
        fx, fy = lerp(sx0, lx, f), lerp(sy0, gy, f) - 110 * math.sin(math.pi * f)
        if f < 1:
            rot = -40 + 400 * f  # przekręca się w locie i ląduje na boku, płasko
        else:  # trzepocze na ziemi, coraz słabiej
            d = t - t0 - lot
            gas = math.exp(-1.3 * d)
            rot = 22 * math.sin(d * 15) * gas
            fy -= 7 * abs(math.sin(d * 7.5)) * gas
        st.put(Z.prop("ryba"), fx, fy, 0.6468 if f < 0.6 else 0.652, h=20, anchor=(0.5, 0.5), rot=rot, sx=-1, shadow=(2, 3, 3, 0.3))
    lalka(st, t, "lisi", 590, 310, lean=5, sink=pr(t, 0.2, 0.9))  # spiskowcy chowają się pod rampę, powóz jedzie dalej
    lalka(st, t, "zhaogao", 880, 310, flip=-1, lean=-5, sink=pr(t, 0.4, 0.9))
    swiatlo(st, w, t)


def s_list(st, w, t, T):
    """Pod murem: nad Fusu przelatuje ptak i zrzuca list, który spada mu na głowę — Fusu na sekundę zamroczony, gwiazdki
    krążą mu nad głową; list ląduje mu w dłoniach, Fusu czyta. Potem list odlatuje mu z rąk, przed nim pojawia się sztylet
    skierowany w niego, po chwili wbija się w pierś; Fusu kona i opada za wzgórze (reżyser 15.11 i 16.11)."""
    x = 646
    gy = Z.ground("dal", x) + 14
    p = 0.448
    kam(st, t, 70, 650, 478, 2.3, 0.45, lens=2.1, truck=0.3)
    st.dof = 0.8
    swiat(st, t, w)
    bx = lerp(380, 980, pr(t, 0.6, 3.6))  # ptak leci z lewa na prawo nad Fusu
    if 0.6 < t < 4.2:
        st.put(Z.bird(int(t * 7) % 2), bx, 372 + 6 * math.sin(t * 5), 0.447, w=40, anchor=(0.5, 0.5), shadow=(2, 3, 3, 0.25))
    glowa = (x - 7, gy - 112)  # czubek głowy Fusu
    dlonie = (x - 22, gy - 80)
    T_ZRZUT, T_GLOWA, T_DLON = 1.9, 2.6, 3.05
    stun = pr(t, T_GLOWA, 1.0)  # sekunda zamroczenia
    czyta = ease(pr(t, 3.6, 0.7))
    pchn = ease(pr(t, 6.6, 0.16))  # sztylet wbija się w pierś
    sink = pr(t, 7.6, T - 8.2)
    lean = -9 * czyta * (1 - pr(t, 5.2, 0.4)) + (7 * math.sin(t * 9) * (1 - stun) if 0 < stun < 1 else 0) + 6 * pchn \
        - 4 * settle((t - 6.75) / 0.8, 1.5)
    lx0 = lerp(380, 980, pr(T_ZRZUT, 0.6, 3.6)) + 2
    if 0.6 < t < T_ZRZUT:  # ptak niesie list
        st.put(Z.prop("list"), bx + 2, 382 + 6 * math.sin(t * 5), 0.4468, w=22, anchor=(0.5, 0.5), rot=-10, shadow=None)
    elif t < T_GLOWA:  # list spada coraz szybciej prosto na głowę
        f = pr(t, T_ZRZUT, T_GLOWA - T_ZRZUT)
        st.put(Z.prop("list"), lerp(lx0, glowa[0], f), lerp(382, glowa[1] - 4, f * f), 0.4485, w=22, anchor=(0.5, 0.5),
               rot=lerp(-10, 200, f), shadow=(2, 3, 3, 0.3))
    elif t < T_DLON:  # odbija się od głowy i spada mu w dłonie
        f = pr(t, T_GLOWA, T_DLON - T_GLOWA)
        st.put(Z.prop("list"), lerp(glowa[0], dlonie[0], f), lerp(glowa[1] - 4, dlonie[1], f) - 34 * math.sin(math.pi * f), 0.4485,
               w=22, anchor=(0.5, 0.5), rot=lerp(200, 370, f), shadow=(2, 3, 3, 0.3))
    else:  # w dłoniach; od 5,2 s list ktoś mu zabiera — odlatuje w górę, poza kadr
        f = ease(pr(t, 5.2, 0.6))
        if f < 1:
            st.put(Z.prop("list"), dlonie[0] + 60 * f, dlonie[1] + 6 * czyta * (1 - f) - 260 * f, 0.4485, w=22, anchor=(0.5, 0.5),
                   rot=10 - 9 * czyta + 300 * f, shadow=(2, 3, 3, 0.3))
    if 0 < stun < 1:  # gwiazdki krążą nad głową
        for n in range(3):
            a = t * 2 * math.pi * 1.1 + n * 2 * math.pi / 3
            st.put(Z.prop("gwiazdka"), glowa[0] + 20 * math.cos(a), glowa[1] - 6 + 5 * math.sin(a), p + (0.0004 if math.sin(a) > 0 else -0.0004),
                   h=9 * (1 - ease(pr(stun, 0.8, 0.2))), anchor=(0.5, 0.5), rot=t * 200 + n * 40, shadow=(1, 2, 2, 0.3))
    pojaw = ease(pr(t, 5.6, 0.5))  # sztylet pojawia się przed nim, ostrzem w jego stronę
    if pojaw > 0 and sink < 1:
        r = math.radians(lean)  # pierś jedzie z lalką: obrót wokół stóp i opadanie za wzgórze
        fy = gy + ease(sink) * 112 * 1.12
        cel = (x + math.cos(r) * -12 - math.sin(r) * -84, fy + math.sin(r) * -12 + math.cos(r) * -84)  # tu wchodzi czubek ostrza
        dx = lerp(70, 0, pchn) + 3 * math.sin(t * 13) * (1 - pchn) * pojaw
        st.put(Z.prop("sztylet"), cel[0] - dx, cel[1], p + 0.0012, w=48, anchor=(196 / 210, 0.5), rot=4 + lean * pchn,
               alpha=min(1.0, pojaw * 2), shadow=(2, 3, 3, 0.35))  # rękojeść od strony widza, czubek w niego
        if pchn <= 0:
            st.put(Z.glow(), cel[0] - dx - 20, cel[1], p + 0.0013, w=70, anchor=(0.5, 0.5), mode="add",
                   alpha=0.35 * math.sin(math.pi * pr(t, 5.6, 0.9)), shadow=None, tint=(1.0, 0.95, 0.85))
    lalka(st, t, "fusu", x, 112, pr(t, 0.2, 0.8), y=gy, p=p, flip=-1, lean=lean, sink=sink)
    swiatlo(st, w, t)


def s_huhai(st, w, t, T):
    """Sala: na podwyższeniu młody Huhai w koronie, za nim wysuwa się eunuch Zhao Gao (tabliczka), nachyla się i szepcze
    mu do ucha; jego cień gasi lampę (reżyser 15.11: „kto to jest i czemu on jest taki ogromny?”)."""
    podpis(w, t, "Huhai, młodszy syn", TRON[0] - 30, 380, 0.6, 2.2)  # tabliczka: pierwsze pojawienie się
    podpis(w, t, "eunuch Zhao Gao", 560, 300, 2.9, 2.4)
    big = pr(t, 1.6, 1.4)
    szept = ease(pr(t, 3.0, 0.7))
    k = ease(t / T)
    kam(st, t, 71, lerp(430, 450, k), lerp(500, 480, k), lerp(1.45, 1.6, k), 0.785)
    st.dof = 1.4
    sala(st, t, w, okna=NOCNE_OKNA, lampy=[1 - 0.85 * ease(big), 1.0, 1.0])
    lalka(st, t, "zhaogao", 548, 318, big, y=TRON[1], p=0.775, flip=-1, lean=-11 * szept + 1.5 * math.sin(t * 2.4) * szept)
    lalka(st, t, "huhai", TRON[0], MALY + 20, pr(t, 0.3, 1.0), y=TRON[1], p=0.785, lean=2 * szept)
    st.grade, st.dim = (0.94, 0.88, 0.86), 0.92 - 0.14 * ease(big)


def _powstancy(st, t, k=1.0, v=0.0):
    for n, (band, p, h, x) in enumerate((("dal", 0.444, 86, 760), ("srodek", 0.524, 106, 1330), ("droga", 0.635, 124, 960))):
        wlocznie(st, t, x + v * (1 + n * 0.3), p=p, band=band, h=h, n=3, flag=(176, 44, 36), seed=20 + n * 3,
                 up=clamp(k * 1.6 - n * 0.3))


def s_powstanie(st, w, t, T):
    """Zza wzgórz wyrastają włócznie z czerwonymi szmatami; urzędnicy znikają, czarne chorągwie zaczynają padać."""
    w.noc = 0.6
    w.urzednicy = [1 - pr(t, 1.2 + n * 0.3, 0.6) for n in range(6)]
    for n, k in enumerate(("han", "zhao", "wei")):
        w.bfall[k] = pr(t, 2.8 + n * 0.7, 0.95)
    kam(st, t, 72, 650, 386, lerp(1.0, 1.08, ease(t / T)), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    _powstancy(st, t, pr(t, 0.4, 2.4), 20 * t)
    swiatlo(st, w, t, extra=(1.04, 0.98, 0.94))


def s_upadek(st, w, t, T):
    """Padają ostatnie czarne chorągwie i posąg, zrywają się chorągwie ze smokiem, miasto i pałac stają w łunie, a pod
    koniec płonie coraz więcej (reżyser 15.11: „spal ją bardziej na końcu”)."""
    w.noc = 0.6
    for n, k in enumerate(("chu", "yan", "qi")):
        w.bfall[k] = pr(t, 0.4 + n * 0.5, 0.95)
    w.qin_fall = pr(t, 2.4, 0.95)
    w.posag_fall = pr(t, 1.0, 1.6)
    w.smoki_fall = pr(t, 2.9, 1.5)
    w.palac = 1 - pr(t, 3.6, 1.8)
    fire = ease(pr(t, 1.2, 1.6))
    wiecej = ease(pr(t, T - 5.0, 4.0))  # pożar rośnie do końca ujęcia
    k = ease(t / T)
    kam(st, t, 73, lerp(700, 640, k), lerp(420, 362, k), lerp(1.18, 1.0, k), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    _powstancy(st, t, 1 - pr(t, T - 1.5, 1.3), 20 * (T + t))
    ft = math.floor(t * 12) / 12
    for n in range(10):  # miasto płonie: języki ognia za murami
        r = random.Random(800 + n)
        st.put(Z.flame(n), 760 + n * 40 + r.uniform(-10, 10), 478, P.miasto - 0.004, h=(70 + r.uniform(0, 80)) * fire * (1 + 0.9 * wiecej) *
               (0.8 + 0.3 * noise(ft, 810 + n, 9)) + 0.1, rot=9 * noise(ft, 830 + n, 7), shadow=None, tint=(1.15, 1.1, 1.0))
    for n in range(18):  # pod koniec płoną też wzgórza, most i pałac
        r = random.Random(850 + n)
        x = 60 + n * 70 + r.uniform(-20, 20)
        band = ("dal", "srodek", "droga")[n % 3]
        kk = wiecej * clamp((wiecej * 18 - n * 0.6) / 4)
        if kk > 0.01:
            st.put(Z.flame(n), x, Z.ground(band, x) + 12, {"dal": 0.446, "srodek": 0.526, "droga": 0.637}[band],
                   h=(60 + r.uniform(0, 90)) * kk * (0.8 + 0.3 * noise(ft, 870 + n, 9)), rot=9 * noise(ft, 890 + n, 7), shadow=None,
                   tint=(1.15, 1.1, 1.0))
    for gx, gy, gw in ((930, 430, 760), (250, 330, 520), (640, 520, 1500)):
        st.put(Z.glow(), gx, gy, 0.66, w=gw, anchor=(0.5, 0.5), mode="add",
               alpha=(0.30 * fire + 0.22 * wiecej) * (0.85 + 0.15 * noise(ft, 9, 9)), shadow=None, tint=(1.0, 0.5, 0.22))
    hot = fire + 0.8 * wiecej
    swiatlo(st, w, t, extra=(1 + 0.10 * hot, 1 - 0.12 * hot, 1 - 0.22 * hot))


def s_cisza(st, w, t, T):
    """Świt: księżyc odjeżdża, słońce wraca na nitce."""
    w.moon = 1 - pr(t, 0.4, 1.0)
    w.noc = 1 - ease(pr(t, 0.6, 2.6))
    w.sun = pr(t, 1.3, 1.6)
    kam(st, t, 74, 640, 368, lerp(1.02, 1.06, t / T), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_studnia(st, w, t, T):
    """Dzień: dwaj chłopi kopią — jeden motyką, drugi łopatą, spod ziemi pryskają grudy; spod ziemi wysuwa się gliniana
    głowa, chłopi odskakują, nad pierwszym zjeżdża tabliczka „O!”; potem wychodzi cały żołnierz, oblepiony ziemią, a
    pierwszy chłop odkłada motykę, podchodzi i otrzepuje go szmatką — grudy odpadają, glina jaśnieje; zjeżdża zawieszka
    (reżyser 15.11: „pokaż, jak kopią”; 16.11: „tabliczka o! nad farmerem”, „otrzep go z ziemi”)."""
    w.zawieszki = [("1974", 1010, 380, pr(t, 5.0, 1.0))]
    kopia = 1 - pr(t, 3.2, 0.3)
    up = 0.40 * ease(pr(t, 3.2, 0.7)) + 0.60 * ease(pr(t, 5.6, 1.1))
    odskok = ease(pr(t, 3.3, 0.5))
    k = ease(t / T)
    kam(st, t, 75, lerp(860, 880, k), lerp(570, 556, k), lerp(1.7, 1.9, k), 0.7, truck=0.8)
    st.dof = 1.4
    w.znaleziony = 0.0
    podpis(w, t, "O!", 825, 500, 3.35, 2.2)  # nad głową chłopa z motyką, kiedy odskakuje
    idzie = ease(pr(t, 6.6, 0.6))  # chłop z motyką podchodzi do żołnierza
    trze = pr(t, 7.2, 1.8)  # otrzepywanie: sześć pociągnięć szmatką
    swiat(st, t, w)
    for n, (cx, narz, okres, faza) in enumerate(((812, "motyka", 0.9, 0.0), (1000, "lopata", 1.1, 0.4))):
        x = cx - (30 if n == 0 else -30) * odskok + (lerp(0, 72, idzie) if n == 0 else 0)
        otrz = n == 0 and t >= 6.6  # odłożył motykę, ma w dłoni szmatkę
        gy = Z.ground("przod", x) + 14
        flip = 1 if n == 0 else -1
        rot = (-4 + 6 * math.sin(2 * math.pi * (t / okres + faza))) * kopia * flip
        if otrz:  # krok przy podchodzeniu, potem pochyla się w rytm pociągnięć
            rot = 3 * math.sin(idzie * math.pi * 4) * (1 - idzie) + (5 + 3 * math.sin(trze * 6 * 2 * math.pi)) * ease(pr(t, 7.1, 0.2))
        st.put(Z.prop("chlop_cialo"), x, gy, 0.70, h=120, anchor=(0.5, 1.0), sx=flip, rot=rot)
        u = (t / okres + faza) % 1.0  # faza zamachu: 0 — w górze, 0,6 — uderzenie w ziemię
        kat = (lerp(-115, 32, ease(u / 0.6)) if u < 0.6 else lerp(32, -115, ease((u - 0.6) / 0.4))) if kopia > 0 else lerp(32, -60, odskok)
        hx, hy = x + 4 * flip, gy - 80
        if otrz:  # motyka leży na ziemi tam, gdzie ją odłożył
            mx = 812 - 30 + 4
            st.put(Z.prop(narz), mx - 10, Z.ground("przod", mx) + 10, 0.7005, w=96, anchor=(0.04, 0.5), rot=-4, shadow=(2, 3, 3, 0.35))
        else:
            st.put(Z.prop(narz), hx, hy, 0.7005, w=96, anchor=(0.04, 0.5), sx=flip, rot=kat * flip, shadow=(2, 3, 3, 0.35))
        for g in range(4):  # grudy ziemi pryskają po każdym uderzeniu
            uu = ((t / okres + faza) - 0.6) % 1.0
            if kopia > 0 and uu < 0.35:
                r = random.Random(int(t / okres + faza) * 10 + g + n * 100)
                gx = x + flip * (80 + r.uniform(-10, 10) + 60 * uu * r.uniform(0.4, 1.0))
                gy2 = gy - 4 - 140 * uu * r.uniform(0.6, 1.0) + 420 * uu * uu
                st.put(Z.prop("grudka"), gx, gy2, 0.7008, h=9, anchor=(0.5, 0.5), rot=r.uniform(0, 360) + 400 * uu, shadow=(1, 2, 2, 0.3))
    hh = 128
    sy0 = Z.ground("przod", 912) + 20
    brud = 1 - ease(trze)
    c = (lerp(1.0, 0.62, brud), lerp(1.0, 0.50, brud), lerp(1.0, 0.38, brud))  # glina oblepiona ziemią jaśnieje
    st.put(Z.soldier(2), 912, sy0 + (1 - up) * hh * 1.05, 0.6995, h=hh, rot=settle((t - 6.7) / 1.2, 1.5, 3), tint=c)
    for g in range(8):  # grudy przyklejone do żołnierza; każda odpada przy swoim pociągnięciu szmatki
        r = random.Random(990 + g)
        gx, gyy = 912 + r.uniform(-24, 18), sy0 - r.uniform(20, 112)
        odp = pr(t, 7.25 + g * 0.21, 0.5)
        if odp < 1 and gyy + (1 - up) * hh * 1.05 < sy0 - 6:
            st.put(Z.prop("grudka"), gx - 20 * odp, gyy + (1 - up) * hh * 1.05 + 160 * odp * odp, 0.6997, h=10 + r.uniform(0, 4),
                   anchor=(0.5, 0.5), rot=r.uniform(0, 360) + 300 * odp, shadow=(1, 2, 2, 0.3))
    if 0 < trze < 1 or (t >= 6.6 and trze <= 0):  # szmatka w dłoni chłopa, potem kółka po glinie
        ruch = trze * 6 * 2 * math.pi
        rx = lerp(812 - 30 + 30, 896 + 6 * math.cos(ruch), ease(pr(t, 6.6, 0.8)))
        ry = Z.ground("przod", 912) + 14 - 84 + 26 * math.sin(trze * math.pi) * (1 if trze > 0 else 0) + 6 * math.sin(ruch)
        st.put(Z.prop("szmatka"), rx, ry, 0.7009, h=14, anchor=(0.5, 0.5), rot=20 * math.sin(ruch), shadow=(1, 2, 2, 0.3))
    swiatlo(st, w, t)


def s_grobowiec(st, w, t, T):
    """Kopiec grobowca w słońcu, nietknięty; na jego szczycie wyrasta sosna, a przed nim z wykopu wychodzi rząd za rzędem
    glinianych żołnierzy; kopiec zaczyna drżeć (reżyser 15.11: „więcej clay soldiers”, „shaking tej tomb”)."""
    w.sosna = pr(t, 0.8, 1.6)
    w.kopiec_drz = ease(pr(t, 3.0, 0.6)) * (1 - 0.6 * ease(pr(t, T - 1.2, 1.0)))
    k = ease(t / T)
    kam(st, t, 76, lerp(1090, 1150, k), lerp(450, 430, k), lerp(1.35, 1.6, k), 0.52, truck=0.5, shake=2.5 * w.kopiec_drz)
    st.dof = 0.8
    swiat(st, t, w)
    for rz, (band, p, h, x0, n) in enumerate((("srodek", 0.527, 58, 760, 11), ("droga", 0.636, 74, 800, 10))):
        for j in range(n):
            r = random.Random(950 + rz * 20 + j)
            x = x0 + j * (46 if rz == 0 else 56) + r.uniform(-6, 6)
            kk = pr(t, 0.4 + rz * 0.5 + j * 0.16 + r.uniform(0, 0.3), 0.7)
            if kk > 0:
                st.put(Z.soldier((rz * 3 + j) % 6), x, Z.ground(band, x) + 18 + (1 - back(kk, 1.4)) * h * 1.1, p, h=h * r.uniform(0.95, 1.05),
                       rot=0.5 * noise(t, 960 + j, 0.4) + settle((kk - 0.7) / 0.3 if kk < 1 else 0, 1.5, 4) + 1.5 * w.kopiec_drz * noise(t, 970 + j, 9))
    swiatlo(st, w, t)


def s_qin(st, w, t, T):
    """Kamera wycofuje się z teatru; gliniana armia staje jeszcze raz, światło gaśnie, zostaje szyld z tytułem."""
    w.armia_t = max(0.0, t - 0.2) * 1.7
    w.znaleziony = 0.0
    k = ease(pr(t, 0.4, T - 2.6))
    m = math.exp(lerp(math.log(1.0), math.log(0.6), k))
    kam(st, t, 77, 640, lerp(360, 322, k), m, 1.0, lens=m ** 0.55, truck=1.0, drift=0.4)
    st.dof = 0.0
    swiat(st, t, w)
    off = ease(pr(t, T - 3.6, 0.9))  # scena gaśnie, a szyld z tytułem świeci jeszcze, zanim film zejdzie w czerń
    st.put(Z.black(), CX, CY, 0.992, w=1300, anchor=(0.5, 0.5), alpha=off, shadow=None, blur=0)
    Z.theatre_put(st, 0.9 - 0.2 * off)
    swiatlo(st, w, t)
