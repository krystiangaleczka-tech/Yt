"""Ujęcia aktów 5–8: Jeden kraj, Ogień i strach, Gliniana armia, Upadek."""
import math
import random

import zestaw as Z
from papier import CX, CY, back, clamp, ease, ease_out, noise, settle
from swiat import (BAN, EMP, KOPIEC, MALY, PODBITE, TRON, URNA, P, dzonka, kam, lalka, lerp, morze, powoz, pr, sala, swiat, swiatlo,
                   wlocznie, woz, wstega)
from ujecia1 import krol


# ---------- akt 5 · Jeden kraj ----------

def s_drogi(st, w, t, T):
    """Cesarz wskazuje drogę; wóz toczy się przez wzgórza, podskakuje na koleinach, mija czarne chorągwie."""
    w.lean = 3.5 * settle(t / 1.6, 1.2)
    w.woz = 440 + 500 * (t / T) ** 0.95
    kam(st, t, 40, lerp(520, 900, t / T), 520, 1.85, 0.645, lens=1.72, truck=0.85)
    st.dof = 1.5
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_prowincje(st, w, t, T):
    """Przy czarnych chorągwiach wysuwają się po kolei małe lalki urzędników."""
    w.urzednicy = [pr(t, 0.7 + n * 0.55, 0.7) for n in range(6)]
    kam(st, t, 41, lerp(800, 780, ease(t / T)), 470, lerp(1.25, 1.36, ease(t / T)), 0.62, truck=0.6)
    st.dof = 0.8
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_rody(st, w, t, T):
    """Trzy wozy ze skrzyniami, każdy dalej i mniejszy, ciągną ku bramie stolicy."""
    x = lerp(470, 880, (t / T) ** 0.95)
    kam(st, t, 42, x - 90, 522, 1.7, 0.645, lens=1.6, truck=0.85)
    st.dof = 1.4
    swiat(st, t, w)
    for j in range(3):
        woz(st, t, x - j * 176, p=0.645 - j * 0.004, h=74 - j * 9)
    swiatlo(st, w, t)


def s_stela(st, w, t, T):
    """Powóz staje pod górą; kamera unosi się na jej szczyt, gdzie wysuwa się kamienna stela."""
    w.stela = pr(t, 3.2, 1.3)
    x = lerp(540, 770, ease_out(pr(t, 0.0, 2.6)))
    k = ease(pr(t, 2.0, 2.6))
    kam(st, t, 43, lerp(730, 1000, k), lerp(520, 330, k), lerp(1.6, 1.9, k), lerp(0.62, 0.34, k), truck=0.5)
    st.dof = 1.2
    swiat(st, t, w)
    powoz(st, t, x)
    swiatlo(st, w, t)


def s_kanal2(st, w, t, T):
    """Druga wstęga kanału rozwija się wzdłuż drogi i wpływają na nią dwie papierowe łodzie."""
    w.kanal2 = pr(t, 0.4, T - 3.2)
    kam(st, t, 44, lerp(820, 880, ease(t / T)), 588, 2.0, 0.67, lens=1.78, truck=0.8)
    st.dof = 1.6
    swiat(st, t, w)
    for j in range(2):
        f = pr(t, T - 3.4 + j * 0.9, 2.6)
        if f > 0:
            x = lerp(790, 990 - j * 60, ease_out(f))
            st.put(Z.boat(), x, Z.ground("droga", x) + 22 + 2 * math.sin(t * 3 + j), 0.673, h=38, rot=3 * math.sin(t * 2.2 + j),
                   shadow=(2, 3, 3, 0.35))
    swiatlo(st, w, t)


def s_pismo(st, w, t, T):
    """Stół i pisarz wysuwają się zza rampy; księga wsuwa się pod pędzel; pisarz pisze."""
    w.dwor = pr(t, 0.4, 1.3)
    w.ksiega = pr(t, 2.2, 1.1)
    w.pisze = ease(pr(t, 3.5, 0.5))
    w.zwoj = 1.0
    w.lean = 3.0 * settle((t - 1.9) / 1.5, 1.2)
    kam(st, t, 45, lerp(690, 676, ease(t / T)), 520, lerp(1.4, 1.5, ease(t / T)), 0.84)
    st.dof = 1.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_moneta(st, w, t, T):
    """Detal blatu — moneta toczy się i kładzie przy stosie monet."""
    w.moneta = 1.0
    w.moneta_x = ease_out(pr(t, 0.3, 1.9))
    kam(st, t, 46, lerp(652, 660, t / T), 598, 3.4, 0.85, lens=2.7, truck=0.8)
    st.dof = 3.0
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_miara(st, w, t, T):
    """Waga zjeżdża na nitce na stół, zaraz po niej odważnik; waga kołysze się i staje."""
    w.waga = pr(t, 0.3, 1.0)
    w.odwaznik = pr(t, 1.3, 1.0)
    w.waga_rot = 5.0 * settle((t - 2.25) / 1.6, 2.5)
    kam(st, t, 47, 724, 560, 2.5, 0.85, lens=2.1, truck=0.8)
    st.dof = 2.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_mur(st, w, t, T):
    """Zza grani wysuwają się odcinki muru i wieże, od zachodu ku miastu; kamera idzie za murem."""
    w.mur = pr(t, 0.5, T - 1.3)
    k = ease(pr(t, 0.3, T - 0.8))
    kam(st, t, 48, lerp(330, 690, k), lerp(392, 420, k), 1.5, 0.43, lens=1.44, truck=0.5)
    st.dof = 1.0
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_robotnicy(st, w, t, T):
    """Po grani pod murem suną sylwetki z koszami; jedna po drugiej przystają i znikają za granią."""
    kam(st, t, 49, lerp(420, 600, ease(t / T)), 392, 2.0, 0.43, lens=1.9, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    for j in range(10):
        r = random.Random(70 + j)
        stop = 1.6 + j * 0.42 if j % 3 == 1 else None  # co trzeci zostaje pod murem
        tt = min(t, stop) if stop else t
        x = 250 + j * 46 + (26 + r.uniform(-4, 4)) * tt
        if not Z.MF_X - 350 < x < Z.MF_X + 350:
            continue
        sink = ease(pr(t, stop, 1.2)) * 40 if stop else 0.0
        st.put(Z.prop("robotnik"), x, Z.ridge(x) + 15 + sink - abs(math.sin(x / 7.0)) * 2.5 * (0 if stop and t > stop else 1), P.gory - 0.002,
               h=34, haze=0.16, shadow=(2, 2, 3, 0.25), rot=2 * math.sin(x / 9.0))
    swiatlo(st, w, t)


def s_ognie(st, w, t, T):
    """Na wieży strażniczej zapala się ogień sygnałowy; po chwili odpowiada mu ogień na następnej wieży."""
    kam(st, t, 78, lerp(470, 500, ease(t / T)), 388, lerp(2.3, 2.5, ease(t / T)), 0.43, lens=2.2, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    ft = math.floor(t * 12) / 12
    for n, (x, a) in enumerate(((568, 0.5), (398, 1.5))):  # wieże muru stoją co 170 px (co piąty odcinek)
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
    """Trzej uczeni po kolei opadają pod rampę; Fusu kłania się cesarzowi, odwraca i odjeżdża ze sceny."""
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
    """Noc: drogą jadą dwa powozy; żelazny młot miażdży pierwszy z nich, drugi staje w miejscu."""
    ti = 2.7
    x1 = lerp(520, 760, min(t, ti) / ti)
    x2 = x1 - 196 + 0  # drugi powóz (cesarski) jedzie za pierwszym i staje po uderzeniu
    hit = pr(t, ti, 0.16)
    kam(st, t, 54, lerp(640, 700, ease(t / T)), 520, 1.75, 0.645, lens=1.62, truck=0.85, shake=8 * hit * (1 - pr(t, ti + 0.1, 0.6)))
    st.dof = 1.3
    swiat(st, t, w)
    woz(st, t, x1, h=74, sy=1 - 0.58 * ease(hit), rot=7 * ease(hit))
    powoz(st, t, x2)
    f = pr(t, 1.7, ti - 1.7)
    if f > 0:
        hx = lerp(1180, x1 + 10, min(1.0, f)) + 90 * pr(t, ti, 0.5)
        hy = lerp(330, Z.ground("droga", x1) - 44, min(1.0, f)) - 190 * math.sin(math.pi * min(1.0, f)) + 150 * pr(t, ti, 0.5) ** 2
        st.put(Z.prop("mlot"), hx, hy, 0.648, h=54, anchor=(0.5, 0.5), rot=-520 * f)
    swiatlo(st, w, t)


def s_morze(st, w, t, T):
    """Cztery pasma fal wysuwają się od dołu, na horyzoncie wyrasta wyspa."""
    w.noc = 0.75
    kam(st, t, 55, 640, lerp(420, 400, ease(t / T)), lerp(1.0, 1.1, ease(t / T)), 0.6, truck=0.5)
    st.dof = 0.6
    morze(st, t, w, k=pr(t, 0.2, 2.4), wyspa=pr(t, 2.8, 1.5))


def s_xufu(st, w, t, T):
    """Trzy dżonki płyną po falach ku wyspie, maleją i znikają za horyzontem."""
    w.noc = 0.75
    kam(st, t, 56, lerp(600, 760, ease(t / T)), lerp(500, 440, ease(t / T)), lerp(1.2, 1.45, ease(t / T)), 0.5, truck=0.6)
    st.dof = 0.8
    morze(st, t, w)
    for j in range(3):
        f = pr(t, 0.1 + j * 0.55, T - 0.9)
        dzonka(st, t, lerp(260 + j * 120, 850 + j * 16, ease(f)), f, seed=j)


def s_puste(st, w, t, T):
    """Puste morze pod księżycem; ostatni żagiel znika za falą."""
    w.noc = 0.82
    kam(st, t, 57, 720, 440, lerp(1.32, 1.36, t / T), 0.5, truck=0.6)
    st.dof = 0.8
    morze(st, t, w)
    dzonka(st, t, 882, lerp(0.9, 1.0, pr(t, 0.2, 1.4)), seed=2)


def s_rtec(st, w, t, T):
    """Przy cesarzu wysuwa się czarka; srebrne kulki zjeżdżają do niej na nitkach, cesarz pochyla się."""
    w.lean = 6 * ease(pr(t, 3.4, 0.9))
    kam(st, t, 58, lerp(410, 420, ease(t / T)), 566, lerp(2.0, 2.25, ease(t / T)), 0.84, lens=1.8)
    st.dof = 2.2
    swiat(st, t, w)
    k = pr(t, 0.3, 0.8)
    st.put(Z.prop("czarka"), 500, 694 + (1 - back(k, 1.3)) * 90, P.rekwizyty, h=58, shadow=(3, 4, 4, 0.4))
    for j in range(3):
        kk = pr(t, 1.2 + j * 0.75, 0.8)
        if 0 < kk:
            Z.hang(st, Z.prop("kulka"), 500 + (j - 1) * 13, 640 + 30 * ease(pr(t, 2.0 + j * 0.75, 0.3)), P.rekwizyty - 0.004, kk, t,
                   120 + j, drop=420, sway=0.3, h=15, shadow=(2, 3, 3, 0.35))
    swiatlo(st, w, t)


# ---------- akt 7 · Gliniana armia ----------

NOCNE_OKNA = (0.30, 0.36, 0.60)


def s_przejscia(st, w, t, T):
    """Sala nocą: cesarz przesuwa się za kolumnami, znika i wychodzi zza następnej; lampy gasną za nim."""
    x = lerp(110, 1190, ease(t / T) * 0.5 + (t / T) * 0.5)
    lampy = [1 - ease(clamp((x - lx - 150) / 160)) for lx in (240, 640, 1040)]
    kam(st, t, 59, lerp(430, 880, ease(t / T)), 430, 1.3, 0.6, truck=0.7)
    st.dof = 0.8
    sala(st, t, w, okna=NOCNE_OKNA, lampy=lampy, kolumna=False)
    lalka(st, t, "zheng", x, 316, y=704, p=0.58, seed=7, lean=3)
    st.grade, st.dim = (0.86, 0.84, 0.92), 0.84


def s_meteor(st, w, t, T):
    """Noc: kamień z ognistym ogonem spada na wzgórze; przy nim zjeżdża zawieszka ze znakami."""
    f = pr(t, 0.7, 0.9)
    hit = pr(t, 1.6, 0.2)
    w.zawieszki = [("始皇帝死而地分", 1010, 300, pr(t, 3.0, 1.0))]
    kam(st, t, 60, lerp(860, 880, ease(t / T)), 430, lerp(1.25, 1.35, ease(t / T)), 0.53, truck=0.5,
        shake=9 * hit * (1 - pr(t, 1.7, 0.7)))
    st.dof = 0.8
    swiat(st, t, w)
    gx, gy = 850, Z.ground("srodek", 850) + 10
    if f > 0:
        x, y = lerp(250, gx, f * f), lerp(-80, gy, f * f)
        if f < 1:
            for n in range(3):  # ogon z bibuły ciągnie się za kamieniem
                st.put(Z.flame(n), x - 30 - n * 16, y - 26 - n * 12, 0.522, h=110 - n * 24, anchor=(0.5, 0.0), rot=-52, shadow=None,
                       tint=(1.15, 1.1, 1.0))
        st.put(Z.prop("kamien"), x, y, 0.524, h=46, anchor=(0.5, 0.7), rot=-200 * f)
        st.put(Z.glow(), x, y, 0.535, w=300 + 400 * hit * (1 - pr(t, 1.8, 1.2)), anchor=(0.5, 0.5), mode="add",
               alpha=0.3 * (1 - pr(t, 1.8, 2.5)), shadow=None, tint=(1.0, 0.6, 0.3))
    swiatlo(st, w, t)


def s_palac(st, w, t, T):
    """Za wzgórzami rośnie piętro po piętrze olbrzymi pałac, wyższy od góry."""
    w.palac = 0.36 * back(pr(t, 0.5, 0.9), 1.2) + 0.32 * back(pr(t, 2.2, 0.9), 1.2) + 0.32 * back(pr(t, 3.9, 0.9), 1.2)
    k = ease(t / T)
    kam(st, t, 61, lerp(340, 320, k), lerp(380, 320, k), lerp(1.2, 1.3, k), 0.5, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_kopiec(st, w, t, T):
    """Po prawej wyrasta kopiec grobowca, a po jego zboczu suną sylwetki ludzi z koszami."""
    w.kopiec = pr(t, 0.4, 2.2)
    kx, ky, kw = KOPIEC
    mound = Z.mound()
    hh = kw * mound.h / mound.w
    k = ease(t / T)
    kam(st, t, 62, lerp(980, 1150, k), lerp(460, 430, k), 1.5, 0.52, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
    for j in range(8):
        x = 1070 + j * 22 + 13 * max(0.0, t - 2.4)
        fx = (x - (kx - kw / 2)) / kw
        if t > 2.4 and 0.05 < fx < 0.5:
            st.put(Z.prop("robotnik"), x, ky - hh + mound.top(fx) * hh + 14 - abs(math.sin(x / 6.0)) * 2, P.miasto + 0.018, h=32,
                   shadow=(2, 2, 3, 0.25), rot=-8)
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
    """Kamera przesuwa się po twarzach pierwszego rzędu; ostatni żołnierz dojeżdża spóźniony."""
    w.armia_t = 7.0 + t  # czas biegnie dalej od poprzedniego ujęcia: spóźniony żołnierz wysuwa się teraz
    kam(st, t, 64, lerp(800, 1150, ease(t / T)), 590, 2.9, 0.79, lens=2.4, truck=0.9)
    st.dof = 2.6
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_rzeki(st, w, t, T):
    """Między rzędami żołnierzy rozwijają się srebrne wstęgi rzek z rtęci."""
    kam(st, t, 65, lerp(780, 900, ease(t / T)), 590, 1.7, 0.74, truck=0.8)
    st.dof = 1.4
    swiat(st, t, w)
    wstega(st, "rtec", 400, 1320, pr(t, 0.4, 2.6), p=0.672, dy=24)
    wstega(st, "rtec", 430, 1320, pr(t, 1.3, 2.6), p=0.735, dy=26, band="przod")
    swiatlo(st, w, t)
    st.spot = (850, 580, 0.74, 560, 0.3)


def s_podroz(st, w, t, T):
    """Noc: powóz cesarza toczy się drogą na wschód, coraz wolniej, i staje."""
    x = lerp(430, 730, ease_out(pr(t, 0.0, T - 1.2)))
    kam(st, t, 66, x + 70, 524, 1.8, 0.645, lens=1.68, truck=0.85)
    st.dof = 1.4
    swiat(st, t, w)
    powoz(st, t, x)
    swiatlo(st, w, t)


def s_koniec(st, w, t, T):
    """Zjeżdża zawieszka z rokiem; lalka cesarza przechyla się i powoli opada pod rampę."""
    w.zawieszki = [("210 p.n.e.", 560, 372, pr(t, 0.6, 1.0))]
    w.sink = pr(t, 1.9, T - 2.3) * 0.999
    k = ease(t / T)
    kam(st, t, 67, lerp(392, 400, k), lerp(520, 528, k), lerp(1.46, 1.4, k), 0.8)  # rampa ponad paskiem napisu
    st.dof = 1.6
    swiat(st, t, w)
    swiatlo(st, w, t)
    st.spot = (330, 500, 0.8, 440, 0.3)


# ---------- akt 8 · Upadek ----------

def s_spisek(st, w, t, T):
    """Przy powozie wysuwają się Li Si i Zhao Gao; pochylają się ku sobie, na powóz opada czarna zasłona."""
    w.zaslona = pr(t, 2.8, 1.1)
    k = ease(t / T)
    kam(st, t, 68, 730, lerp(530, 520, k), lerp(1.42, 1.52, k), 0.8)
    st.dof = 1.3
    swiat(st, t, w)
    lalka(st, t, "lisi", 590, 310, pr(t, 0.4, 1.1), lean=5 * ease(pr(t, 2.0, 0.7)))
    lalka(st, t, "zhaogao", 880, 310, pr(t, 0.9, 1.1), flip=-1, lean=-5 * ease(pr(t, 2.2, 0.7)))
    swiatlo(st, w, t)


def s_ryby(st, w, t, T):
    """Powóz jedzie dalej, a za nim wóz z górą ryb; kamera jedzie z nimi."""
    x = lerp(730, 1060, (t / T) ** 0.95)
    w.powoz, w.zaslona = x, 1.0
    kam(st, t, 69, x - 70, 528, 1.9, 0.645, lens=1.76, truck=0.85)
    st.dof = 1.4
    swiat(st, t, w)
    woz(st, t, x - 190, h=66, ladunek=(Z.prop("ryby"), 30, -6, 18))
    lalka(st, t, "lisi", 590, 310, lean=5)
    lalka(st, t, "zhaogao", 880, 310, flip=-1, lean=-5)
    swiatlo(st, w, t)


def s_list(st, w, t, T):
    """Pod murem: do Fusu zjeżdża na nitce zwój; Fusu pochyla się nad nim i opada za wzgórze."""
    x = 646
    gy = Z.ground("dal", x) + 14
    kam(st, t, 70, 650, 478, 2.3, 0.45, lens=2.1, truck=0.3)
    st.dof = 0.8
    swiat(st, t, w)
    lalka(st, t, "fusu", x, 112, pr(t, 0.2, 0.8), y=gy, p=0.448, flip=-1, lean=-9 * ease(pr(t, 2.4, 0.7)), sink=pr(t, 3.8, T - 4.2))
    Z.hang(st, Z.S("bamboo", 0.5), x - 34, 404, 0.449, pr(t, 1.0, 1.1), t, 130, drop=300, sway=1.5, w=36, shadow=(2, 3, 3, 0.3))
    swiatlo(st, w, t)


def s_huhai(st, w, t, T):
    """Sala: na podwyższeniu mała lalka w koronie, za nią wyrasta wielka szara lalka eunucha i zasłania lampę."""
    big = pr(t, 1.6, 1.8)
    k = ease(t / T)
    kam(st, t, 71, lerp(430, 440, k), lerp(500, 470, k), lerp(1.45, 1.66, k), 0.785)
    st.dof = 1.4
    sala(st, t, w, okna=NOCNE_OKNA, lampy=[1 - 0.85 * ease(big), 1.0, 1.0])
    lalka(st, t, "zhaogao", 520, 430, big, y=TRON[1], p=0.77, flip=-1, lean=-3 * ease(pr(t, 3.4, 0.8)))
    lalka(st, t, "huhai", TRON[0], MALY, pr(t, 0.3, 1.0), y=TRON[1], p=0.785)
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
    """Padają ostatnie czarne chorągwie i posąg, zrywają się chorągwie ze smokiem, miasto i pałac stają w łunie."""
    w.noc = 0.6
    for n, k in enumerate(("chu", "yan", "qi")):
        w.bfall[k] = pr(t, 0.4 + n * 0.5, 0.95)
    w.qin_fall = pr(t, 2.4, 0.95)
    w.posag_fall = pr(t, 1.0, 1.6)
    w.smoki_fall = pr(t, 2.9, 1.5)
    w.palac = 1 - pr(t, 3.6, 1.8)
    fire = ease(pr(t, 1.2, 1.6))
    k = ease(t / T)
    kam(st, t, 73, lerp(700, 640, k), lerp(420, 362, k), lerp(1.18, 1.0, k), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    _powstancy(st, t, 1 - pr(t, T - 1.5, 1.3), 20 * (T + t))
    ft = math.floor(t * 12) / 12
    for n in range(10):  # miasto płonie: języki ognia za murami
        r = random.Random(800 + n)
        st.put(Z.flame(n), 760 + n * 40 + r.uniform(-10, 10), 478, P.miasto - 0.004, h=(70 + r.uniform(0, 80)) * fire *
               (0.8 + 0.3 * noise(ft, 810 + n, 9)) + 0.1, rot=9 * noise(ft, 830 + n, 7), shadow=None, tint=(1.15, 1.1, 1.0))
    for gx, gy, gw in ((930, 430, 760), (250, 330, 520)):
        st.put(Z.glow(), gx, gy, 0.66, w=gw, anchor=(0.5, 0.5), mode="add", alpha=0.30 * fire * (0.85 + 0.15 * noise(ft, 9, 9)),
               shadow=None, tint=(1.0, 0.5, 0.22))
    swiatlo(st, w, t, extra=(1 + 0.10 * fire, 1 - 0.12 * fire, 1 - 0.22 * fire))


def s_cisza(st, w, t, T):
    """Świt: gliniani żołnierze zapadają się pod ziemię, księżyc odjeżdża, słońce wraca na nitce."""
    w.armia = 1 - pr(t, 0.3, 1.9)
    w.moon = 1 - pr(t, 0.4, 1.0)
    w.noc = 1 - ease(pr(t, 0.6, 2.6))
    w.sun = pr(t, 1.3, 1.6)
    kam(st, t, 74, 640, 368, lerp(1.02, 1.06, t / T), 0.62, truck=0.5)
    st.dof = 0.5
    swiat(st, t, w)
    swiatlo(st, w, t)


def s_studnia(st, w, t, T):
    """Dzień: chłop kopie motyką; spod ziemi wysuwa się gliniana głowa, potem cały żołnierz; zjeżdża zawieszka."""
    w.zawieszki = [("1974", 1010, 380, pr(t, 3.6, 1.0))]
    dig = 1 - pr(t, 2.0, 0.3)
    up = 0.40 * ease(pr(t, 2.0, 0.7)) + 0.60 * ease(pr(t, 4.2, 1.1))
    k = ease(t / T)
    kam(st, t, 75, lerp(860, 880, k), lerp(570, 556, k), lerp(1.7, 1.9, k), 0.7, truck=0.8)
    st.dof = 1.4
    swiat(st, t, w)
    st.put(Z.prop("chlop"), 820, Z.ground("przod", 820) + 14, 0.70, h=120, rot=11 * math.sin(t * 7) * dig - 6 * (1 - dig))
    hh = 128
    st.put(Z.soldier(2), 912, Z.ground("przod", 912) + 20 + (1 - up) * hh * 1.05, 0.70, h=hh,
           rot=settle((t - 5.3) / 1.2, 1.5, 3))
    swiatlo(st, w, t)


def s_grobowiec(st, w, t, T):
    """Kopiec grobowca w słońcu, nietknięty; na jego szczycie wyrasta sosna."""
    w.sosna = pr(t, 0.8, 1.6)
    k = ease(t / T)
    kam(st, t, 76, lerp(1090, 1150, k), lerp(450, 430, k), lerp(1.35, 1.6, k), 0.52, truck=0.5)
    st.dof = 0.8
    swiat(st, t, w)
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
    off = ease(pr(t, T - 2.3, 0.9))
    st.put(Z.black(), CX, CY, 0.992, w=1300, anchor=(0.5, 0.5), alpha=off, shadow=None, blur=0)
    Z.theatre_put(st, 0.9 - 0.4 * off)
    swiatlo(st, w, t)
