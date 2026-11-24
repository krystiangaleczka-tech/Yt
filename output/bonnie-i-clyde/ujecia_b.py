"""Ujęcia aktów 5–8 filmu „Bonnie and Clyde: The Outlaws Made of Paper”: funkcja `s_<klucz>(st, w, t, T)` na ujęcie.

Akt V — łowca (Hamer), VI — Ameryka przestaje kibicować, VII — pułapka, VIII — kto ma legendę. Rozpiska: docs/filmy/bonnie-i-clyde/ujecia/dane.py.
Śmierć i strzały pokazujemy tylko w teatrze cieni (parawan) albo przez ślady (kapelusz, czapki), nigdy ciał.
"""
import math
import sys

import scena as swiat  # noqa: E402
from scena import USTA, _off, bark, dlon, do_punktu, mruganie, rs, siegnij, stan_przy  # noqa: E402
from scena import (CX, DROGA_Y, J, OCZY, P, STOPY, Z0, auto, back, bk, blysk, cien, ciezarowka, cmentarz, drukarnia, ease, ease_out,
                   eastham, jazda, kam, kino, lalka, las, lerp, mapa_punkt, mapa_scena, miasto, motocykl, noise, parawan, podpis, pr,
                   preria, punkt, teatr_gazet, widownia, wnetrze)
from ujecia_a import CEL, GAZETA, czyta_gazete, KARABIN, KARABIN_PION, KULA, REV, _reflektory, auto_srodek, koniec, tab, tab_tu, ekran_do_swiata, miga, swiatla, kapelusz_reka

NOC = (0.7, 0.72, 0.85)
LOWCY = (("hamer", "Frank Hamer"), ("gault", "Manny Gault"), ("alcorn", "Bob Alcorn"), ("hinton", "Ted Hinton"),
         ("jordan", "Henderson Jordan"), ("oakley", "Prentiss Oakley"))


def _bump(t, t0, d=0.15):
    return max(0.0, 1.0 - abs(t - t0) / d)


BIURO_MAPA_Y = 150  # górna krawędź mapy na ścianie biura Hamera (przed 23.11: 60)


def _biuro(st, t, w, kapelusz=False, mapa=True, jasnosc=1.0, kapelusz_rot=0.0):
    """Biuro Hamera w Austin (jak w akcie III: zielona ściana, biurko, krzesło); mapa stanów na ścianie po lewej.
    kapelusz — kapelusz Hamera z dziurą po kuli na oparciu krzesła (marker reżysera 23.11 w ujęciu 97); kapelusz_rot — przechył."""
    wnetrze(st, t, w, sciana="zielen", okna=(1080,), meble=(("biurko", 560, 170, P.lalki + 0.02), ("krzeslo", 820, 200, P.lalki + 0.005)),
            zarowki=(560,), jasnosc=jasnosc)
    if kapelusz:
        st.put(J.rek("kapelusz_fedora"), 826, 520, P.lalki + 0.006, h=40, anchor=(0.5, 1.0), tint=(1.0, 0.95, 0.75), rot=kapelusz_rot)
        dx, dy = _off(-6, -22, kapelusz_rot)
        st.put(J.rek("dziura"), 826 + dx, 520 + dy, P.lalki + 0.0065, h=10, anchor=(0.5, 0.5), shadow=None)
    if mapa:
        # markery reżysera 23.11 („Ma poniżej i po niej cały czas driftuje Bonnie i Clyde”, „Mapa niżej” — ujęcia 80 i 81): mapa
        # wisi niżej, a po niej cały czas jeździ w poślizgu mały szary Ford Bonnie i Clyde'a
        km = bk(w, 0.3, 0.9)
        J.hang(st, J.mapa_plansza(), 280, BIURO_MAPA_Y, P.miasto + 0.01, km, t, 610, w=380, drop=500, sway=0.2, strings=(0.08, 0.92))
        if km >= 1:
            a = t * 0.8
            cx_, cy_ = 280 + 130 * math.sin(a), BIURO_MAPA_Y + 125 + 62 * math.sin(2 * a)
            vx, vy = 130 * math.cos(a), 124 * math.cos(2 * a)
            kier = 1 if vx >= 0 else -1
            kat = math.degrees(math.atan2(vy, abs(vx)))
            st.put(J.ford("szary"), cx_, cy_, P.miasto + 0.012, h=26, anchor=(0.5, 0.75), sx=kier, rot=kier * (kat + 18 * math.sin(a * 3)),
                   shadow=(2, 2, 2, 0.3))
            for n in range(3):  # kurz z kół w poślizgu
                ff = (t * 2.5 + n / 3) % 1.0
                st.put(J.glow(r=256, color=(200, 180, 150)), cx_ - kier * (18 + 30 * ff), cy_ + 6, P.miasto + 0.011, w=10 + 18 * ff,
                       anchor=(0.5, 0.5), alpha=0.5 * (1 - ff), shadow=None)


def _ganek(st, t, w):
    """Ganek domu Hamera w Austin: preria za domem, weranda z balustradą (podłoga ganku na linii stóp)."""
    preria(st, t, w, droga=0.0, slupy=False, wiatrak=True)
    Z0.rise(st, J.ganek(), 640, STOPY + 120, P.drzewa, bk(w, 0.35), t, 620, w=1300, wob=0.0)


# ===================== AKT V · KTO W KOŃCU RUSZYŁ ZA NIMI =====================

ODB_OBROT, ODB_STRZAL = 2.83, 4.0  # s na osi Studio (uwaga i marker reżysera 23.11)


def s_odbicie(st, w, t, T):
    """Mgła nad Eastham; więźniowie wyciągają broń z rowu, strażnik pada; z mgły trąbi Ford, więźniowie wskakują na stopnie."""
    # uwaga reżysera 23.11: „dopiero w 4 s strzel do niego”; marker 2,83 s: „przekręć go w tym momencie w prawo” — trzeci
    # więzień obraca się do strażnika i dopiero w 4 s strzela z lufy rewolweru (1.28); strażnik pada po strzale
    strz, obr = rs("odbicie", ODB_STRZAL), rs("odbicie", ODB_OBROT)
    kam(st, t, 70, 640, 420, 1.0, 0.77, shake=2.0 * (strz < t < strz + 0.4))
    eastham(st, t, w, mgla=1.0 - 0.4 * ease(pr(t, 6.0, 4.0)))
    ax = jazda(t, 5.6, 2.4, -400, 620, ease_out)[0] if t < 9.0 else jazda(t, 9.0, 3.0, 620, 1900, ease)[0]
    auto(st, t, ax, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.88, 0.88, 0.92), kurz=t > 9.0)
    for n, (key, x0, off) in enumerate((("wiezien", 280, -200), ("henry_wiezien", 450, -60), ("wiezien2", 980, 110))):
        schyl = ease(pr(t, 1.2 + 0.3 * n, 0.6)) * (1 - ease(pr(t, 2.2 + 0.3 * n, 0.5)))
        wsk = ease(pr(t, 8.0 + 0.2 * n, 0.7))
        x = ax + off if wsk >= 1 else lerp(x0, 620 + off, wsk)
        fl = 1 if x0 < 640 else (-1 if n < 2 else lerp(-1, 1, ease(pr(t, obr, 0.25))))
        celuje = n == 2 and obr + 0.25 < t < strz + 0.6
        out = lalka(st, t, key, x, 290, flip=fl, lean=30 * schyl, lift=30 * wsk + 60 * math.sin(math.pi * wsk),
                    rece=(88 if celuje else 50 + 40 * schyl, 30), trzyma=REV() if t > 2.4 + 0.3 * n else None, hop=4 * (0 < wsk < 1))
        if celuje and out:
            blysk(st, round((out[0] + 34) / 10) * 10, round((out[1] - 12) / 10) * 10, P.lalki, t, strz, r=220)
    pad = ease(pr(t, strz + 0.15, 1.2))
    lalka(st, t, "crowson", 1160, 310, flip=-1, rece=(40, 0), trzyma=KARABIN(150) if pad < 0.3 else None, sink=0.9 * pad, lean=25 * pad)
    tab(w, t, "BEEP BEEP!", 220, 260, 5.4, 2.4)
    koniec(st, w, t, extra=(0.95, 0.97, 1.02))


STR_KAPELUSZ = (0.2, 2.1)  # s na osi Studio: kapelusz spada od … do


def s_straznik(st, w, t, T):
    """Mgła rzednie; na drodze zostaje kapelusz strażnika; podpis „Major Joe Crowson”; światło przygasa."""
    kam(st, t, 71, 700, 540, 1.4, 0.8)
    st.dof = 1.3
    eastham(st, t, w, mgla=lerp(0.6, 0.2, ease(t / T)), kul=False)
    # marker reżysera 23.11 (1,47 s): „niech ta czapka tak fruwa na ziemię z postrzeloną dziurą” — kapelusz spada zygzakiem
    # jak liść (kreska od lewej góry) i kładzie się na drodze; w rondzie dziura po kuli
    f = pr(t, rs("straznik", STR_KAPELUSZ[0]), rs("straznik", STR_KAPELUSZ[1]) - rs("straznik", STR_KAPELUSZ[0]))
    x0, y0 = ekran_do_swiata(st.cam, 446, 160, P.rampa - 0.01)
    hx = lerp(x0, 700, f) + 80 * math.sin(f * math.pi * 3) * (1 - f)
    hy = lerp(y0, 655, f ** 1.3)
    hr = -12 * f + 28 * math.sin(f * math.pi * 3) * (1 - f)
    st.put(J.rek("kapelusz_fedora"), hx, hy, P.rampa - 0.01, h=64, anchor=(0.5, 1.0), rot=hr, tint=(0.95, 0.9, 0.8))
    dx, dy = _off(-8, -30, hr)
    st.put(J.rek("dziura"), hx + dx, hy + dy, P.rampa - 0.009, h=14, anchor=(0.5, 0.5), rot=hr, shadow=None)
    podpis(w, t, "Major Joe Crowson", 700, 520, rs("straznik", STR_KAPELUSZ[1] + 0.2), T)  # po upadku kapelusza, na nazwisko
    koniec(st, w, t, dim=1.0 - 0.3 * ease(pr(t, 3.0, 4.0)))


def s_simmons(st, w, t, T):
    """Szef więziennictwa wali pięścią w biurko, aż podskakuje kałamarz; podpis „Lee Simmons, Texas prisons chief”."""
    kam(st, t, 72, 640, 470, 1.3, 0.8)
    wnetrze(st, t, w, sciana="deski", okna=(1050,), meble=(("biurko", 640, 170, P.lalki + 0.02),), zarowki=(640,))
    # gag 40 (GAGI.md, W3 „nitka teatru”): po trzecim uderzeniu w biurko pęka prawa nitka szyldu, szyld zwisa krzywo
    peka = pr(t, 3.25, 0.6)
    J.hang(st, J.tag("TEXAS PRISON SYSTEM"), 640 - 0.4 * 300, 150, P.miasto + 0.01, 1.0, t, 530, h=44, drop=300, sway=0.3,
           anchor=(0.1, 0.0), strings=(0.1,) if peka > 0 else (0.1, 0.9), rot0=14 * back(peka, 1.4))
    b = sum(_bump(t, t0) for t0 in (1.6, 2.4, 3.2))
    lalka(st, t, "simmons", 600, 320, flip=1, sink=0.15, lean=4 * b, rece=(100 - 70 * b, 30))
    st.put(J.rek("butelka"), 730, 538 - 30 * b, P.lalki + 0.025, h=34, anchor=(0.5, 1.0), tint=(0.25, 0.25, 0.35), rot=10 * b)
    # markery reżysera 23.11 (6,23 s): „to idzie do góry” — podpis odjeżdża w górę; „tabliczka give him to me!” przy pięści
    podpis(w, t, "Lee Simmons, Texas prisons chief", 600, 290, 4.0, rs("simmons", 6.23) - 4.3)
    tab_tu(st, w, t, "GIVE HIM TO ME!", "simmons", 688, 267, 6.23 + 0.7)
    koniec(st, w, t)


HAM_KROKI = "LRRLRRL"  # uwaga reżysera 23.11: „chodzi lewo prawo prawo lewo prawo prawo lewo dół góra”
HAM_START, HAM_KROK = 0.9, 0.62  # s na osi Studio: pierwszy krok, długość kroku
HAM_RZUT, HAM_LAP, HAM_EASY = 8.0, 9.1, 9.97  # „w klatce 240 wrzuca broń do góry … w klatce 273 łapie”; tabliczka „easy.”
HAM_SZCZYT, HAM_DLON = (695.0, 142.0), (972.0, 380.0)  # markery: dokąd leci broń (ekran) i gdzie wpada do ręki
HAM_KULE = [(0.7 + 0.55 * n, 190 + (n * 137) % 330, 1 if n % 2 == 0 else -1) for n in range(13)]  # kule w tle: s, y, kierunek


def _hamer_ruch(t):
    """Pozycja Hamera (x, zwrot, przysiad) w czasie akcji t — kroki z uwagi reżysera, potem dojście po karabin."""
    pts = [(rs("hamer", HAM_START), 560.0)]
    for n, c in enumerate(HAM_KROKI):
        pts.append((rs("hamer", HAM_START + HAM_KROK * (n + 1)), pts[-1][1] + (-85 if c == "L" else 85)))
    d0 = HAM_START + HAM_KROK * len(HAM_KROKI)
    pts.append((rs("hamer", d0 + 2 * HAM_KROK + 0.1), pts[-1][1]))
    pts.append((rs("hamer", HAM_RZUT - 0.6), 860.0))
    x, fl = pts[0][1], 1.0
    for (t0, x0), (t1, x1) in zip(pts, pts[1:]):
        if t >= t1:
            x = x1
            fl = fl if x1 == x0 else (1.0 if x1 > x0 else -1.0)
        elif t > t0:
            x = lerp(x0, x1, ease((t - t0) / (t1 - t0)))
            fl = fl if x1 == x0 else (1.0 if x1 > x0 else -1.0)
            break
    sink = 0.22 * math.sin(math.pi * pr(t, rs("hamer", d0), rs("hamer", d0 + 2 * HAM_KROK) - rs("hamer", d0)))
    idzie = any(t0 < t < t1 and x0 != x1 for (t0, x0), (t1, x1) in zip(pts, pts[1:]))
    return x, fl, sink, idzie


def s_hamer(st, w, t, T):
    """Ganek Hamera w Austin. Uwaga reżysera 23.11: „od początku szeryf chodzi lewo prawo prawo lewo prawo prawo lewo dół góra
    i w tle latają kule pocisków takich jak w ujęciu na początku filmu; w klatce 240 wrzuca broń do góry, po czym obraca się
    i w klatce 273 łapie tak, jak jest narysowane”; markery: „odznaka szeryfa”, „podnieś na chwilę rękę do góry” (3,03 s),
    „rzuca broń tu i się kręci” (7,97 s), „i spada mu do ręki z tej strony” (9,07 s), „tabliczka easy.” (9,97 s).
    Kule w tle to „dozens of gunfights” z kwestii; pusty fotel buja się sam (gag 41)."""
    kam(st, t, 73, 640, 450, 1.1, 0.8)
    _ganek(st, t, w)
    if bk(w, 0.6) >= 1:
        sam = ease(pr(t, 0.8, 1.0)) * (1 - ease(pr(t, 8.6, 0.6)))
        st.put(J.mebel("fotel_bujany"), 380, STOPY, P.lalki - 0.005, h=240, anchor=(0.5, 1.0), rot=8 * sam * math.sin(t * 3.2))
    # kule w tle: smuga i błysk, przelatują za Hamerem przed ścianą domu
    for n, (s0, y, kier) in enumerate(HAM_KULE):
        a, b = rs("hamer", s0), rs("hamer", s0 + 0.55)
        if a < t < b:
            f = (t - a) / (b - a)
            bx = lerp(-80, 1360, f) if kier > 0 else lerp(1360, -80, f)
            st.line([(bx - kier * 70, y + 3), (bx, y)], P.drzewa + 0.01, width=3, color=(250, 228, 150), alpha=0.8)
            st.put(J.glow(), bx, y, P.drzewa + 0.011, w=24, anchor=(0.5, 0.5), mode="add", alpha=0.95, shadow=None, tint=(1.0, 0.9, 0.5))
    rz, lp = rs("hamer", HAM_RZUT), rs("hamer", HAM_LAP)
    ma = t > rs("hamer", HAM_RZUT - 0.6) and not (rz <= t < lp)
    if t <= rs("hamer", HAM_RZUT - 0.6) and bk(w, 0.6) >= 1:
        st.put(J.rek("karabin"), 930, STOPY - 6, P.lalki - 0.004, w=210, anchor=(0.0, 0.5), rot=-80)
    hx, fl, sink, idzie = _hamer_ruch(t)
    if rz <= t < lp:  # dwa obroty, kiedy broń jest w powietrzu
        fl = math.cos(2 * math.pi * 2 * pr(t, rz, lp - rz))
    reka = 165 if rs("hamer", 2.75) < t < rs("hamer", 3.35) else (40 if ma else 20)
    lalka(st, t, "hamer", hx, 340, flip=fl, sink=sink, rece=(reka, 10), trzyma=KARABIN(180) if ma else None, hop=3 * idzie)
    if abs(fl) > 0.3:  # odznaka na piersi (marker 3,03 s)
        ox, oy = punkt("hamer", hx, 340, 126, 252, flip=fl)
        st.put(J.rek("odznaka"), ox, oy + sink * 340 * 1.12, P.lalki + 0.02, h=24, anchor=(0.5, 0.5), sx=abs(fl), shadow=None)
    if rz <= t < lp:  # broń leci w górę, kręci się i spada do ręki z prawej strony
        f = (t - rz) / (lp - rz)
        p0 = (860 + 50, 430)
        p1 = ekran_do_swiata(st.cam, *HAM_SZCZYT, P.lalki)
        p2 = ekran_do_swiata(st.cam, *HAM_DLON, P.lalki)
        bx = (1 - f) ** 2 * p0[0] + 2 * f * (1 - f) * (2 * p1[0] - 0.5 * (p0[0] + p2[0])) + f * f * p2[0]
        by = (1 - f) ** 2 * p0[1] + 2 * f * (1 - f) * (2 * p1[1] - 0.5 * (p0[1] + p2[1])) + f * f * p2[1]
        st.put(J.rek("karabin"), bx, by, P.lalki + 0.02, w=180, anchor=(0.5, 0.5), rot=720 * f + 90)
    podpis(w, t, "Frank Hamer, retired Texas Ranger", 640, 250, 3.6, 5.0)
    tab_tu(st, w, t, "EASY.", "hamer", 953, 171, HAM_EASY)
    koniec(st, w, t)


def s_poscigi(st, w, t, T):
    """Radiowóz goni Forda; Ford znika, radiowóz wylatuje z zakrętu i ląduje w rowie kołami do góry; „AGAIN?!”."""
    kam(st, t, 74, 640, 440, lerp(1.1, 0.95, ease(t / T)), 0.78, shake=6.0 * (6.1 < t < 6.5))
    preria(st, t, w, slupy=True, mesa=True)
    fx = jazda(t, 0.8, 2.6, -400, 1800)[0]
    auto(st, t, fx, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], kurz=True)
    h = 220
    if t < 5.0:
        px = jazda(t, 1.8, 3.2, -500, 900)[0]
        auto_srodek(st, t, px, DROGA_Y - h * 0.5, h, 0, kolor="czarny", napis="SHERIFF", pasazerowie=[("policjant", 1, (40, 0))])
    else:
        f = ease(pr(t, 5.0, 1.2))
        cx = lerp(900, 1060, f)
        cy = lerp(DROGA_Y - h * 0.5, DROGA_Y - h * 0.5 + 24, f) - 200 * math.sin(math.pi * f)
        auto_srodek(st, t, cx, cy, h, 180 * f, kolor="czarny", napis="SHERIFF", droga=t * 500)
    tab(w, t, "AGAIN?!", 1040, 290, 6.6, 3.0)
    koniec(st, w, t)


def s_hak_szuflada(st, w, t, T):
    """Hamer zdejmuje z biurka zabawkowy radiowóz i chowa go do szuflady; tabliczka „NO MORE CHASING”."""
    kam(st, t, 75, 580, 470, 1.45, 0.8)
    st.dof = 1.2
    _biuro(st, t, w)
    f = ease(pr(t, 1.2, 1.0))
    # marker reżysera 23.11 (4,53 s): „podnieść rękę i machaj tak, jakbyś odmawiał” — dłoń w górze, macha na boki: nie
    mach = ease(pr(t, rs("hak_szuflada", 4.2), 0.3)) * (1 - ease(pr(t, rs("hak_szuflada", 5.8), 0.3)))
    lalka(st, t, "hamer", 650, 330, flip=-1, sink=0.15,
          rece=(lerp(lerp(30, 70, ease(pr(t, 0.8, 0.4))) - 40 * f, 140 + 22 * math.sin(t * 13), mach), 20))
    if f < 1 and bk(w, 0.5) >= 1:
        st.put(J.rek("zabawka"), lerp(520, 600, f), 538 + 30 * f, P.lalki + 0.025 - 0.01 * (f > 0.5), h=34, anchor=(0.5, 1.0), alpha=1 - f * f)
    tab(w, t, "NO MORE CHASING", 600, 280, 2.4, 2.8)
    koniec(st, w, t)


TECZKA_PRZESUW, TECZKA_LAMPA, TECZKA_KAWA, TECZKA_PODNOSI = 5.03, 5.17, (5.0, 6.2), 6.7  # s na osi Studio (markery 23.11)


def s_hak_teczka(st, w, t, T):
    """Hamer otwiera grubą teczkę; wycinki wyfruwają i same przypinają się do mapy; Hamer stawia kubek kawy i siada wygodnie.
    Markery reżysera 23.11: „mapa niżej” (0 s, wspólne _biuro), „przesuwa boks w to miejsce” (5,03 s), „zacznij mrugać lampą”
    (5,17 s), „od 5. s zjeżdża na nitce kawa aż do 6,20, a po 0,5 s podnosi ją” (5,97 s)."""
    kam(st, t, 76, 480, 430, 1.2, 0.8)
    _biuro(st, t, w, jasnosc=mruganie(t, rs("hak_teczka", TECZKA_LAMPA)))
    otw = t > 1.0
    tx_ = ekran_do_swiata(st.cam, 631, 0, P.lalki + 0.025)[0]
    bx_ = lerp(540, tx_, ease(pr(t, rs("hak_teczka", TECZKA_PRZESUW - 0.5), rs("hak_teczka", TECZKA_PRZESUW) - rs("hak_teczka", TECZKA_PRZESUW - 0.5))))
    st.put(J.rek("teczka_otwarta" if otw else "teczka"), bx_, 538, P.lalki + 0.025, h=46 if otw else 60, anchor=(0.5, 1.0))
    for n in range(8):
        f = ease(pr(t, 1.8 + 0.5 * n, 1.0))
        if f <= 0:
            continue
        tx, ty = 160 + 60 * (n % 4), 120 + 90 * (n // 4) + (BIURO_MAPA_Y - 60)
        x, y = lerp(bx_, tx, f), lerp(510, ty, f) - 120 * math.sin(math.pi * f)
        st.put(J.gazeta(J.NAGLOWKI[n % len(J.NAGLOWKI)], 80 + n, 360, 300, False), x, y, P.miasto + 0.012, h=lerp(30, 54, f), anchor=(0.5, 0.5),
               rot=(1 - f) * 300 + 6 * (n % 3 - 1), shadow=(3, 4, 4, 0.3))
        if f >= 1:
            st.put(J.rek("pinezka"), x, y - 22, P.miasto + 0.013, h=10, anchor=(0.5, 0.5))
    # kawa zjeżdża na nitce na biurko przy dłoni Hamera, po 0,5 s Hamer podnosi ją do ust (dłoń do ust: ręka w skrócie, 1.28)
    k0, k1 = rs("hak_teczka", TECZKA_KAWA[0]), rs("hak_teczka", TECZKA_KAWA[1])
    kx, ky = ekran_do_swiata(st.cam, 747, 487, P.lalki + 0.025)
    podn = ease(pr(t, rs("hak_teczka", TECZKA_PODNOSI), 0.5))
    lean = -8 * ease(pr(t, 7.2, 0.8))
    if podn <= 0:
        J.hang(st, J.rek("kubek"), kx, ky - 30, P.lalki + 0.025, pr(t, k0, k1 - k0), t, 77, h=30, drop=560, sway=0.4,
               string=t < k1 + 0.3)
        lalka(st, t, "hamer", 690, 330, flip=-1, sink=0.15, lean=lean, rece=(60, 20))
    else:
        usta = punkt("hamer", 690, 330, 174, 170, flip=-1, rot=lean)
        usta = (usta[0], usta[1] + ease(0.15) * 330 * 1.12)  # siedzi (sink 0,15)
        cel = (lerp(kx, usta[0] - 10, podn), lerp(ky - 18, usta[1] + 8, podn))
        kat, sk = do_punktu("hamer", 690, cel, h=330, flip=-1, sink=0.15, lean=lean)
        lalka(st, t, "hamer", 690, 330, flip=-1, sink=0.15, lean=lean, rece=(kat, 20), skrot=(sk, 1.0),
              trzyma=(J.rek("kubek"), 30, (0.5, 0.6), 0, False))
    koniec(st, w, t)


PODK_TRZASK = 5.8  # s na osi Studio: ołówek pęka (marker 23.11)


def s_podkreslenie(st, w, t, T):
    """W aktach jedno zdanie: czerwony ołówek podkreśla je dwa razy; zjeżdża tabliczka „HE WON'T GO BACK”."""
    kam(st, t, 77, 640, 400, 1.0, 0.8)
    st.put(J.sciana("zielen"), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    st.put(J.rek("teczka_otwarta"), 640, 420, P.drzewa, w=1400, anchor=(0.5, 0.5))
    for n, (txt, y) in enumerate((("CLYDE CHAMPION BARROW", 250), ("PAROLED FEB. 2, 1932", 320))):
        st.put(J.tag(txt), 330, y + 60, P.drzewa + 0.002, h=44, anchor=(0.5, 0.5), shadow=None)
    st.put(J.tag("\"I'LL NEVER GO BACK TO EASTHAM\""), 330, 430, P.drzewa + 0.002, h=56, anchor=(0.5, 0.5), shadow=None)
    # markery reżysera 23.11: „tutaj kredka” (2,10 s) — ołówek grafitem na linii, a trzonem w dół w prawo (jak w dłoni piszącego);
    # „trzask i niech ten grafit gdzieś poleci, kredka się łamie” (5,80 s) — przy drugim podkreśleniu ołówek pęka: czubek
    # z grafitem odlatuje łukiem za kadr, a złamany ołówek podskakuje i zostaje chwilę na linii (gag 42)
    x0, x1 = 80, 580
    tr = rs("podkreslenie", PODK_TRZASK)
    for n, (a, d, dy) in enumerate(((2.0, 2.0, 0), (4.6, 1.8, 10))):
        f = ease(pr(t, a, d))
        if n == 1:
            f = min(f, ease(pr(tr, a, d)))  # po trzasku linia już nie rośnie
        if f > 0:
            st.line([(x0, 468 + dy), (lerp(x0, x1, f), 468 + dy + 3 * math.sin(f * 9))], P.drzewa + 0.003, width=5, color=(190, 40, 36))
        gx, gy = lerp(x0, x1, f), 468 + dy
        if n == 0 and 0 < f < 1:
            st.put(J.rek("olowek"), gx, gy, P.drzewa + 0.01, w=200, anchor=(0.95, 0.5), rot=215, shadow=(4, 6, 6, 0.35))
        if n == 1 and 0 < f and t < tr:
            st.put(J.rek("olowek"), gx, gy, P.drzewa + 0.01, w=200, anchor=(0.95, 0.5), rot=215, shadow=(4, 6, 6, 0.35))
        if n == 1 and tr <= t < tr + 1.0:
            skok = 34 * _bump(t, tr + 0.08, 0.22)
            ox, oy = _off(-26, 0, 215)
            st.put(J.rek("olowek_zlamany"), gx + ox, gy + oy - skok, P.drzewa + 0.01, w=176, anchor=(0.97, 0.5), rot=215 - 8 * (skok > 0),
                   shadow=(4, 6, 6, 0.35))
            fg = pr(t, tr, 0.8)
            if fg < 1:
                st.put(J.rek("olowek_czubek"), gx + 260 * fg, gy - 230 * math.sin(math.pi * fg * 0.8) - 60 * fg, P.drzewa + 0.012, w=42,
                       anchor=(0.5, 0.5), rot=215 + 900 * fg, shadow=(3, 4, 4, 0.3))
    tab(w, t, "SNAP!", 700, 360, tr + 0.05, 1.2)
    tab(w, t, "HE WON'T GO BACK", 640, 150, 8.0, 4.0)
    koniec(st, w, t)


def s_dzien1(st, w, t, T):
    """Zawieszka „DAY 1”; Hamer jedzie starym autem przez prerię z mapą na kolanach."""
    x = lerp(200, 1100, t / T)
    kam(st, t, 78, x, 450, 1.15, 0.78, truck=1.0)
    w.zawieszki = [("DAY 1", x, 160, pr(t, 0.8, 1.0))]
    preria(st, t, w, slupy=True, mesa=True)
    uchyla = ease(pr(t, 4.6, 0.3)) * (1 - ease(pr(t, 5.6, 0.4)))
    kap = uchyla > 0.3
    auto(st, t, x, 240, kolor="czarny", kurz=True,
         # kapelusz uniesiony przed twarzą, w oknie (dalej wystawał nad maską)
         pasazerowie=[("hamer_bez" if kap else "hamer", 1, (60 + 70 * uchyla, 30), 1,
                       (J.rek("kapelusz_fedora"), 28, (0.5, 0.85), 0, False) if kap else None)])
    st.put(J.rek("mapa_zwoj"), x - 70, DROGA_Y - 150, P.auta + 0.003, h=40, anchor=(0.5, 0.5), rot=-8)
    # gag 20 (GAGI.md): Hamer jedzie tak wolno, że wyprzedza go starsza pani z laską; Hamer uchyla kapelusza
    lx = x - 420 + 230 * (t - 2.0)
    if 2.0 < t and lx < x + 900:
        lalka(st, t, "farmerka", lx, 270, flip=1, lean=10, rece=(28 + 6 * math.sin(t * 6), 50), hop=3,
              trzyma=(J.rek("laska"), 130, (0.5, 0.05), 0, False))
    koniec(st, w, t)


MOTEL_PUSZKA = 5.8  # s na osi Studio: górna puszka się przewraca (marker 23.11)


def s_hamer_motel(st, w, t, T):
    """Hamer pokazuje recepcjoniście zdjęcie Bonnie; recepcjonista kiwa głową i wskazuje drogę; na ladzie piramida puszek po fasoli."""
    kam(st, t, 79, 620, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(1050,), meble=(("lada", 700, 150, P.lalki + 0.02),), zarowki=(700,))
    # gag 21 (GAGI.md): na „a pile of empty cans” Hamer dotyka jednej puszki i cała piramida się rozsypuje; Hamer nawet nie mrugnie
    # marker reżysera 23.11 (5,80 s): „puszka się przewraca” — górna puszka przechyla się i kładzie na boku (z podskokiem), zanim
    # piramida rozsypie się na „a pile of empty cans”
    przew = rs("hamer_motel", MOTEL_PUSZKA)
    for n, (x, r) in enumerate(((560, 0), (594, 0), (628, 0), (577, 1), (611, 1), (594, 2))):
        if bk(w, 0.6) >= 1:
            f = pr(t, 8.8 + 0.07 * (2 - r) + 0.03 * n, 0.9)
            kier = (-1, 0.4, 1, -0.7, 0.8, 0.1)[n]
            y0 = STOPY - 150 - 36 * r
            rot0, dx0 = 0.0, 0.0
            if n == 5:
                fp = pr(t, przew, 0.35)
                rot0 = 90 * fp * fp
                dx0 = 16 * fp
                y0 += 8 * fp - 6 * _bump(t, przew + 0.4, 0.12)
            st.put(J.rek("puszka"), x + dx0 + 170 * kier * f, y0 + (130 + 36 * r) * min(1.0, f * f * 1.6) - 40 * math.sin(math.pi * min(1, f * 1.6)),
                   P.lalki + 0.025, h=36, anchor=(0.5, 0.6), rot=rot0 + f * 300 * kier)
    tab(w, t, "…", 800, 280, 9.6, 1.4)
    kiwa = 5 * math.sin(t * 9) * (3.0 < t < 5.0)
    lalka(st, t, "recepcjonista", 800, 300, flip=-1, sink=0.08, lean=kiwa, rece=(lerp(20, 120, ease(pr(t, 5.4, 0.5))), 0))
    dotyk = ease(pr(t, 8.4, 0.3)) * (1 - ease(pr(t, 9.0, 0.3)))
    # uwaga reżysera 23.11: „narysuj Bonnie na tym zdjęciu, jakby robiła pajacyka”; marker 4,80 s: „porusz zdjęciem”
    rusz = 9 * math.sin(t * 15) * (rs("hamer_motel", 4.5) < t < rs("hamer_motel", 5.4))
    lalka(st, t, "hamer", 420, 340, flip=1, rece=(lerp(20, 90, ease(pr(t, 0.8, 0.6))) + rusz * 0.3, 10 + 70 * dotyk),
          trzyma=(J.zdjecie_pajacyk(int(t * 4) % 2), 70, (0.5, 0.8), 90 + rusz, True) if t > 1.0 else None)
    tab_tu(st, w, t, "YEAH, I SAW!", "hamer_motel", 821, 239, 7.4)
    koniec(st, w, t)


def linia_granicy(st, w, a, b):
    """Granica stanów: biała linia namalowana w poprzek drogi przy tablicy (markery reżysera 23.11 w ujęciach 85 i 96);
    a, b — końce kreski markera na ekranie."""
    if bk(w, 0.5) >= 1:
        a_ = ekran_do_swiata(st.cam, *a, P.droga + 0.062)
        b_ = ekran_do_swiata(st.cam, *b, P.droga + 0.062)
        st.line([a_, b_], P.droga + 0.062, width=9, color=(238, 234, 222), alpha=0.95)


D20_STOP = 8.73  # s na osi Studio: tabliczka „STOP!!!” (marker 23.11)


def s_dzien20(st, w, t, T):
    """Zawieszka „DAY 20”; tablica „STATE LINE”; Ford przemyka przez granicę, radiowóz hamuje przed nią z piskiem."""
    kam(st, t, 80, 640, 460, 1.0, 0.78)
    w.zawieszki = [("DAY 20", 640, 160, pr(t, 0.6, 1.0))]
    preria(st, t, w, slupy=True, tablice=[("STATE LINE", 760)])
    # marker reżysera 23.11 (1,03 s): „narysuj to linię białą” — granica stanów to biała linia namalowana w poprzek drogi
    linia_granicy(st, w, (790, 506), (800, 594))
    # marker 2,57 s: „Bonnie ma jedną rękę w górze i macha nią”
    auto(st, t, jazda(t, 1.2, 2.6, -400, 1800)[0], 230, pasazerowie=[("bonnie", 0, (150 + 25 * math.sin(t * 14), 0)), ("clyde", 1, (40, 0))],
         kurz=True)
    px = jazda(t, 2.4, 3.4, -500, 520, ease_out)[0]
    auto(st, t, px, 220, kolor="czarny", napis="SHERIFF", p=P.auta + 0.004, przechyl=3 * math.sin(math.pi * pr(t, 5.2, 0.6)),
         pasazerowie=[("policjant", 1, (40 + 80 * (t > 7.0), 0))])
    if 5.0 < t < 7.2:
        for n in range(4):
            f = pr(t, 5.0 + 0.2 * n, 1.4)
            st.put(J.glow(r=256, color=(200, 180, 140)), px + 200 - 80 * n, DROGA_Y - 20 - 40 * f, P.auta + 0.01, w=120 + 160 * f,
                   anchor=(0.5, 0.5), alpha=0.5 * (1 - f), shadow=None)
    tab(w, t, "SCREECH!", 520, 300, 5.0, 2.0)
    # marker 8,73 s: „tabliczka stop!!! a następna dopiero po 1,5 s”
    tab_tu(st, w, t, "STOP!!!", "dzien20", 586, 374, D20_STOP, dur=1.6)
    tab(w, t, "NOT MY STATE...", 520, 300, rs("dzien20", D20_STOP + 1.5) - 0.7, 2.6)
    # gag 22 (GAGI.md, pomysł reżysera): szeryf stoi przed granicą; przelatuje ptak — plask na szybie tuż przed jego nosem;
    # szeryf zastyga, „…”
    fb = pr(t, 10.6, 2.0)
    if 0 < fb < 1:
        st.put(Z0.bird(int(t * 8) % 2), lerp(1400, -100, fb), 300 + 20 * math.sin(fb * 9), P.rekwizyty, h=40, anchor=(0.5, 0.5), sx=-1)
    k_ = 220 / 360.0
    sx_, sy_ = px + (500 - 450) * k_, DROGA_Y + (126 - 356) * k_
    fp = pr(t, 11.1, 0.35)
    if fp > 0:
        st.put(J.rek("plama"), lerp(560, sx_, fp), lerp(310, sy_, fp * fp), P.auta + 0.006, h=lerp(14, 34, fp), anchor=(0.5, 0.5))
    tab(w, t, "…", 520, 330, 11.8, 1.6)
    koniec(st, w, t)


MAPA_KROPKI = ((4.23, (493.0, 182.0)), (4.57, (732.0, 155.0)), (5.70, (694.0, 307.0)), (6.27, (697.0, 464.0)))  # markery 23.11
MAPA_NIC_PEKA, MAPA_SUPEL = 6.7, 7.2  # s na osi Studio: nić do dużej kropki pęka, Hamer bez patrzenia zawiązuje supeł


def s_mapa(st, w, t, T):
    """Hamer przypina do mapy znaczniki i łączy je czerwoną nicią. Markery reżysera 23.11: „tu narysuj kropkę i połącz” (4,23;
    4,57; 5,70 s), „tu narysuj dużą kropkę i połącz” (6,27 s) — kropki tam, gdzie wracali (Kansas, Missouri, Arkansas) i duża
    w Luizjanie, gdzie zamknie się pułapka; gag 23: ostatnia nić pęka, Hamer bez patrzenia zawiązuje supeł."""
    kam(st, t, 81, 640, 400, 1.0, 0.72)
    x0, y0, sk = mapa_scena(st, t, w, sciana="zielen", wd=780, x=560)
    P_ = P.wzgorza + 0.02
    pkt = [(mapa_punkt((x0, y0), sk, m), t0, 18) for m, t0 in (("Dallas", 1.4), ("Atoka", 2.6), ("Joplin", 3.8))]
    pkt += [(ekran_do_swiata(st.cam, sx, sy, P_), rs("mapa", sek), 30 if n == 3 else 18) for n, (sek, (sx, sy)) in enumerate(MAPA_KROPKI)]
    peka, supel_t = rs("mapa", MAPA_NIC_PEKA), rs("mapa", MAPA_SUPEL)
    for n, ((px, py), t0, hh) in enumerate(pkt):
        k = pr(t, t0, 0.3)
        if k > 0:
            st.put(J.rek("pinezka"), px, py, P_, h=max(1.0, hh * back(k, 1.6)), anchor=(0.5, 0.5))
        if n > 0:
            f = ease(pr(t, t0 + 0.15, 0.5))
            if f > 0:
                a = pkt[n - 1][0]
                if n == len(pkt) - 1 and peka < t < supel_t + 0.3:
                    # marker reżysera 24.11 (6,87 s): „linia ma być prowadzona z jednej kropki, a nie z dwóch” — pęknięta nić
                    # zsuwa się z dużej kropki i zwisa tylko z górnej; po supełku Hamera biegnie znowu od tej jednej kropki
                    # do dużej
                    dl = math.hypot(px - a[0], py - a[1])
                    if t < supel_t:
                        zw = ease(pr(t, peka, 0.35))
                        kat = math.atan2(py - a[1], px - a[0]) * (1 - zw) + math.radians(90 + 12 * math.sin(t * 5)) * zw
                        L = dl * lerp(1.0, 0.55, zw)
                        st.line([a, (a[0] + math.cos(kat) * L, a[1] + math.sin(kat) * L)], P_ - 0.001, width=3, color=(190, 40, 36))
                    else:
                        g = ease(pr(t, supel_t, 0.3))
                        st.line([a, (lerp(a[0], px, g), lerp(a[1], py, g))], P_ - 0.001, width=3, color=(190, 40, 36))
                else:
                    st.line([a, (lerp(a[0], px, f), lerp(a[1], py, f))], P_ - 0.001, width=3, color=(190, 40, 36))
                    if n == len(pkt) - 1 and t >= supel_t + 0.3:
                        st.put(Z0.coin(), (a[0] + px) / 2, (a[1] + py) / 2, P_ - 0.0005, h=9, anchor=(0.5, 0.5),
                               tint=(0.75, 0.15, 0.13), shadow=None)
    supel = _bump(t, supel_t, 0.35)
    lalka(st, t, "hamer", 1060, 340, flip=-1, rece=(110 + 20 * math.sin(t * 2), 20 + 60 * supel))
    koniec(st, w, t)


def s_petle(st, w, t, T):
    """Czerwona nić na mapie układa się w pętle wzdłuż granic stanów; każda pętla wraca do Dallas, do dwóch małych domków."""
    x0, y0, sk = mapa_scena(st, t, w, sciana="zielen", wd=900, x=640, y=20)
    dx, dy = mapa_punkt((x0, y0), sk, "Dallas")
    zb = ease(pr(t, 9.5, 4.0))
    kam(st, t, 82, lerp(640, dx, zb), lerp(360, dy, zb), lerp(1.05, 1.7, zb), 0.72)
    for n, m in enumerate(("Atoka", "Joplin", "Commerce", "Ruston", "Wellington")):
        cx, cy = mapa_punkt((x0, y0), sk, m)
        f = pr(t, 0.8 + 1.7 * n, 1.6)
        if f <= 0:
            continue
        vx, vy = cx - dx, cy - dy
        dl = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / dl, vx / dl
        pts = []
        for i in range(int(40 * f) + 1):
            s = i / 40
            a, b = math.sin(math.pi * s), 0.35 * dl * math.sin(2 * math.pi * s)
            pts.append((dx + vx * a + nx * b, dy + vy * a + ny * b))
        if len(pts) > 1:
            st.line(pts, P.wzgorza + 0.019, width=3, color=(190, 40, 36))
    for n in range(2):
        k = ease(pr(t, 9.6 + 0.3 * n, 0.6))
        if k > 0:
            st.put(J.fasada("dom"), dx - 16 + 32 * n, dy, P.wzgorza + 0.021, h=max(1.0, 34 * back(k, 1.5)), anchor=(0.5, 1.0), shadow=(2, 3, 3, 0.3))
    tab(w, t, "HOME", dx, dy - 120, 11.0, 3.4)
    koniec(st, w, t)


# ===================== AKT VI · KIEDY AMERYKA PRZESTAŁA KIBICOWAĆ =====================

GRAPE_SWIATLA = 10.9  # s na osi Studio (markery 23.11)
GRAPE_GWIZDKI = 7.17  # s na osi Studio (marker 24.11)


def s_grapevine(st, w, t, T):
    """„DAY 50 · Easter Sunday”; wiejska droga, kwitnące drzewa, Ford na poboczu; nadjeżdżają dwaj motocykliści i zwalniają."""
    kam(st, t, 83, lerp(560, 700, ease(t / T)), 450, 1.05, 0.78)
    w.zawieszki = [("DAY 50 · Easter Sunday", 640, 160, pr(t, 0.8, 1.0))]
    preria(st, t, w, slupy=False, zielen=True)
    for n, x in enumerate((180, 1160, 620)):
        Z0.rise(st, J.drzewo(n + 3, (236, 186, 200)), x, 690, P.wzgorza + 0.02, bk(w, 0.3 + 0.05 * n), t, 630 + n, h=360 + 40 * n, wob=0.1)
    for n in range(10):
        y = (t * 30 + n * 83) % 520 + 120
        st.put(J.platek(), (n * 137) % 1280 + 30 * math.sin(t + n), y, P.drzewa + 0.02, h=10, anchor=(0.5, 0.5), rot=t * 90 + n * 40)
    auto(st, t, 920, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    # markery reżysera 23.11 (10,90 s): „zaświeć lampami z tyłu” i „zamrugaj lampą” — Ford daje znak, że ktoś w nim siedzi
    gs = rs("grapevine", GRAPE_SWIATLA)
    swiatla(st, 920, tyl=1.0 if t >= gs else 0.0, przod=miga(t, gs, 3))
    # marker reżysera 24.11 (7,17 s): „zrób, że mają gwizdki i dźwięk gwizdka” — obaj motocykliści mają gwizdki w ustach
    # i dmuchają w nie (drugi chwilę po pierwszym); przy gwizdku podmuch (dźwięk: efekty.ZDARZENIA, GRAPE_GWIZDKI)
    tg = rs("grapevine", GRAPE_GWIZDKI)
    for n, key in enumerate(("murphy", "wheeler")):
        mx = jazda(t, 2.0 + 0.4 * n, 4.0, -300 - 200 * n, 360 - 220 * n, ease_out)[0]
        motocykl(st, t, mx, 190, jezdziec=key, p=P.auta + 0.004 * n)
        k_ = 190 / 300.0
        ux, uy = punkt(key, mx - 30 * k_, 190 * 1.55, USTA[0], USTA[1] + 2, y=DROGA_Y + 0.25 * 190 - 40 * k_, flip=1)
        st.put(J.rek("gwizdek"), ux - 2, uy, P.auta + 0.004 * n - 0.0035, h=13, anchor=(0.08, 0.5), rot=-8, shadow=None, z=0.07)
        for b0 in (tg + 0.25 * n, tg + 0.8 + 0.25 * n):
            d = pr(t, b0, 0.35)
            if 0 < d < 1:
                for m in range(3):
                    st.line([(ux + 30 + 14 * d, uy - 8 + 8 * m), (ux + 42 + 30 * d, uy - 12 + 12 * m)], P.auta + 0.004 * n,
                            width=2.2, color=(250, 246, 236), alpha=0.9 * (1 - d))
    koniec(st, w, t)


def s_grapevine_cien(st, w, t, T):
    """Za parawanem dwa błyski, dwie sylwetki przy motocyklach padają; motocykl przewraca się z łoskotem (szczyt 2)."""
    kam(st, t, 84, 640, 460, 1.3, 0.79, lens=1.4, shake=5.0 * (2.4 < t < 2.8))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    sil = dict(tint=(0.08, 0.06, 0.05), alpha=1.0, blur=1.6)
    motocykl(st, t, 330, 130, y=y0 - 26, p=p0 + 0.001, **sil)
    motocykl(st, t, 560, 130, y=y0 - 26, p=p0 + 0.0012, rot=-75 * ease(pr(t, 2.4, 0.4)), **sil)
    auto(st, t, 1000, 170, y=y0 - 26, p=p0 + 0.0008, flip=-1, shadow=None, szyby=False, **sil)
    for n, (key, x) in enumerate((("murphy", 430), ("wheeler", 680))):
        pad = ease(pr(t, 1.8 + 0.3 * n, 1.2))
        cien(st, t, key, x, 250, y0 - 26, p0 + 0.002, flip=1, rece=(20, 0), sink=0.9 * pad, lean=-22 * pad)
    blysk(st, 900, y0 - 150, p0 + 0.003, t, 1.5, r=260)
    blysk(st, 920, y0 - 140, p0 + 0.003, t, 1.8, r=240)
    koniec(st, w, t, dim=0.88)


TULLIS_KWIAT = 8.43  # s na osi Studio: Maree kładzie kwiatek na trumnie (marker 23.11)


def s_tullis(st, w, t, T):
    """Przy trumnie młoda kobieta w białej sukni ślubnej; z góry powoli spadają płatki; podpis „Maree Tullis”."""
    kam(st, t, 85, 600, 470, 1.25, 0.8)
    cmentarz(st, t, w)
    if bk(w, 0.6) >= 1:
        st.put(J.rek("trumna"), 700, 676, P.lalki + 0.07, w=320, anchor=(0.5, 1.0))
        st.put(J.rek("kwiaty"), 700, 610, P.lalki + 0.075, h=70, anchor=(0.5, 1.0))
    # markery reżysera 23.11: „tak jej rozciągnij tę suknię” (2,20 s) — biała suknia ślubna w dzwon od pasa do ziemi;
    # „idzie w tym kierunku i daje kwiatka na grób” (8,43 s) — podchodzi do trumny i kładzie kwiatek obok bukietu;
    # „tabliczka oh lord!” (10,63 s)
    idzie = pr(t, rs("tullis", TULLIS_KWIAT - 1.9), rs("tullis", TULLIS_KWIAT - 0.4) - rs("tullis", TULLIS_KWIAT - 1.9))
    tx = lerp(460, 590, ease(idzie))
    kl = rs("tullis", TULLIS_KWIAT)
    reka = lerp(30, 72, ease(pr(t, kl - 0.4, 0.4))) * (1 - ease(pr(t, kl + 0.5, 0.5)))
    # marker reżysera 24.11 (8,47 s): „tu połóż tego kwiatka” — kwiatek ląduje na wieku trumny w punkcie z kreski markera,
    # dłoń Maree sięga tam w chwili położenia
    kw_x, kw_y = ekran_do_swiata(st.cam, 766, 548, P.lalki + 0.076)
    if t > kl - 0.5 and t < kl + 0.5:
        reka = siegnij("tullis", tx, (kw_x - 10, kw_y - 18), h=290, flip=1, lean=6)[0]
    out = lalka(st, t, "tullis", tx, 290, flip=1, lean=6, rece=(reka, 20), hop=3 * (0 < idzie < 1),
                trzyma=(J.rek("kwiatek"), 50, (0.5, 0.75), -90, False) if t < kl else None)
    # suknia ślubna w jednym kawałku (marker 24.11, 1,80 s: „ma być w jednej całości, a nie w dwóch częściach”): stanik od
    # linii ramion i dzwon do linii trawy (marker 23.11, 2,20 s: „tak jej rozciągnij tę suknię”) — przed tułowiem, za przednią
    # ręką, z tym samym pochyleniem co lalka
    sc_ = 290 / 614.0
    gx_, gy_ = punkt("tullis", tx, 290, 150, 206, flip=1, rot=6)
    gy_ -= abs(math.sin(tx / 26.0)) * 3 * (0 < idzie < 1)
    st.put(J.rek("suknia_cala"), gx_, gy_, P.lalki + 0.01, h=470 * sc_, anchor=(0.5, 0.0), rot=6, shadow=(3, 4, 4, 0.3), z=0.02)
    if t >= kl and bk(w, 0.6) >= 1:
        st.put(J.rek("kwiatek"), kw_x, kw_y, P.lalki + 0.076, h=50, anchor=(0.5, 0.5), rot=-75)
    tab_tu(st, w, t, "OH LORD!", "tullis", 618, 222, 10.63)
    for n in range(14):
        if t < 0.6 + 0.2 * n:
            continue
        y = (t * 36 + n * 97) % 760 - 40
        st.put(J.platek((248, 236, 240)), 200 + (n * 83) % 900 + 20 * math.sin(t + n), y, P.rekwizyty, h=12, anchor=(0.5, 0.5),
               rot=t * 70 + n * 30, sx=math.cos(t * 2 + n))
    podpis(w, t, "Maree Tullis", 460, 240, 2.5, min(4.0, rs("tullis", TULLIS_KWIAT - 1.9) - 2.5))
    koniec(st, w, t, dim=0.92)


def s_gazety_zle(st, w, t, T):
    """Nowe gazety o bezlitosnej Bonnie; ludzie zgniatają je i rzucają na ziemię; kolejka przy kiosku się rozchodzi.
    Marker reżysera 23.11 (2,07 s): „na każdej gazecie duża śmiejąca się buzia Bonnie” (J.gazeta(buzia=True))."""
    kam(st, t, 86, 680, 430, lerp(1.1, 0.95, ease(t / T)), 0.79)
    miasto(st, t, w, fasady=(("kiosk", 380), ("apteka", 900)), tyl=(("dom", 160), ("bank", 700)))
    lalka(st, t, "gazeciarz", 380, 240, flip=1, rece=(lerp(130, 20, ease(pr(t, 5.0, 1.0))), 0))
    for n, key in enumerate(("bezrobotny", "przechodnia", "przechodzien3", "przechodzien", "przechodnia2")):
        x0 = 560 + 120 * n
        odch = ease(pr(t, 5.5 + 0.3 * n, 3.0))
        x = x0 + (1 if n % 2 else -1) * 900 * odch
        g = ease(pr(t, 2.4 + 0.4 * n, 0.5))
        out = lalka(st, t, key, x, 300 - 6 * (n % 2), flip=(-1 if n % 2 == 0 else 1) if odch > 0 else -1, rece=(lerp(80, 20, ease(pr(t, 3.0 + 0.4 * n, 0.3))), 0),
                    hop=4 * (0 < odch < 1))
        f = pr(t, 3.0 + 0.4 * n, 0.5)
        if g < 1 and out:
            st.put(J.gazeta("BONNIE LAUGHED AS HE DIED", 90 + n, 360, 420, False, buzia=True), out[0], out[1], P.lalki + 0.03, h=lerp(96, 30, g), anchor=(0.5, 0.6),
                   sy=lerp(1.0, 0.6, g), rot=40 * g)
        elif f > 0:
            st.put(J.gazeta("BONNIE LAUGHED AS HE DIED", 90 + n, 360, 420, False, buzia=True), x0 + 20, lerp(560, STOPY - 24, f * f), P.rampa - 0.01, h=22,
                   anchor=(0.5, 1.0), sy=0.6, rot=60 * n)
    koniec(st, w, t)


def s_listy_gon(st, w, t, T):
    """Na słupie wyrastają kolejne listy gończe z nagrodą; farmer z dubeltówką przystaje, czyta i odwraca się w stronę drogi."""
    kam(st, t, 87, 640, 440, 1.15, 0.8)
    preria(st, t, w, slupy=False)
    st.put(J.slup(), 600, STOPY, P.lalki - 0.01, h=620, anchor=(0.5, 1.0))
    for n, (x, y, nag) in enumerate(((556, 230, "$500"), (650, 300, "$1000"), (560, 400, "$1000"), (648, 470, "$2500"))):
        k = pr(t, 0.8 + 1.0 * n, 0.4)
        if k > 0:
            s_ = max(0.02, back(k, 1.6))
            st.put(J.rek("plakat"), x, y, P.lalki - 0.008 + 0.0005 * n, h=120 * s_, anchor=(0.5, 0.5), rot=-4 + 3 * n)
            st.put(J.tag("REWARD " + nag), x, y + 70 * s_, P.lalki - 0.007 + 0.0005 * n, h=24 * s_, anchor=(0.5, 0.5), shadow=None)
    fx = jazda(t, 3.4, 3.0, 1400, 800, ease_out)[0]
    # gag 24 (GAGI.md, pomysł reżysera): na widok pojazdu farmer robi musztrę jak na paradzie — na ramię, prezentuj broń,
    # na ramię, w takt werbla — a to tylko wóz z sianem i koniem
    # karabin pionowo w dłoni: prezentuj broń (przed piersią) → w górę → prezentuj → baczność (kolba przy nodze)
    if 9.4 <= t < 10.75:
        ang, kb = (80, 165, 80)[int((t - 9.4) / 0.45)], KARABIN_PION(160)
    elif t >= 10.75:
        ang, kb = 12, KARABIN_PION(160)
    else:
        ang, kb = 50, KARABIN(160)
    lalka(st, t, "farmer", fx, 310, flip=-1 if t < 8.6 else 1, lean=-6 * (6.4 < t < 8.6), rece=(ang, 15), trzyma=kb, hop=4 * (3.4 < t < 6.4))
    wx = lerp(-520, 1700, pr(t, 8.8, 4.2))
    if 8.8 < t:
        st.put(J.rek("woz_siano"), wx, DROGA_Y + 10, P.auta, h=200, anchor=(0.5, 1.0))
        st.put(J.zwierze("kon", int(t * 4) % 2), wx + 330, DROGA_Y + 10, P.auta + 0.001, h=190, anchor=(0.5, 1.0))
    koniec(st, w, t)


COMM_LAMPY = 7.63  # s na osi Studio (marker 23.11)


def s_commerce(st, w, t, T):
    """Ford ugrzązł w rowie pod Commerce; dwaj stróże prawa idą przez pole, żeby pomóc."""
    kam(st, t, 88, 680, 450, 1.05, 0.78)
    preria(st, t, w, slupy=True, plot=True)
    auto(st, t, 480, 230, y=DROGA_Y + 40, przechyl=-14, droga=t * 300, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    # markery reżysera 23.11: „tabliczka need help?!” (5,47 s), „lampy zamrugały” (7,63 s) — reflektor Forda w rowie mruga
    swiatla(st, 480, y=DROGA_Y + 40, przechyl=-14, przod=miga(t, rs("commerce", COMM_LAMPY), 3))
    tab_tu(st, w, t, "NEED HELP?!", "commerce", 897, 244, 5.47)
    for n, key in enumerate(("campbell", "boyd")):
        x = jazda(t, 1.0 + 0.3 * n, 6.0, 1400 + 90 * n, 900 + 120 * n)[0]
        lalka(st, t, key, x, 300 - 10 * n, flip=-1, rece=(20 + 50 * (n == 1) * (t > 6), 0), hop=4 * (1.0 < t < 7.3))
    koniec(st, w, t)


def s_commerce_cien(st, w, t, T):
    """Za parawanem błysk, starszy konstabl pada; komendant podnosi ręce i wsiada do Forda."""
    kam(st, t, 89, 640, 460, 1.3, 0.79, lens=1.4, shake=3.0 * (1.5 < t < 1.8))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    auto(st, t, 420, 170, y=y0 - 6, p=p0 + 0.0008, przechyl=-12, tint=(0.08, 0.06, 0.05), alpha=1.0, shadow=None, blur=1.6, szyby=False)
    pad = ease(pr(t, 1.8, 1.2))
    cien(st, t, "campbell", 760, 250, y0 - 26, p0 + 0.002, flip=-1, rece=(20, 0), sink=0.9 * pad, lean=22 * pad)
    bx = lerp(900, 560, ease(pr(t, 3.4, 2.0)))
    cien(st, t, "boyd", bx, 260, y0 - 26, p0 + 0.002, k=1.0 - ease(pr(t, 5.4, 0.5)), flip=-1, rece=(170 * ease(pr(t, 2.0, 0.4)),) * 2,
         hop=4 * (3.4 < t < 5.4))
    blysk(st, 540, y0 - 170, p0 + 0.003, t, 1.5, r=240)
    koniec(st, w, t, dim=0.9)


def s_boyd(st, w, t, T):
    """Komendant na tylnym siedzeniu z rękami w górze; Bonnie odwraca się do niego z uniesionym palcem; podpis."""
    kam(st, t, 90, 600, 470, 1.55, 0.79)
    st.dof = 1.3
    preria(st, t, w, slupy=True, kul=False)
    x = 640 + 6 * math.sin(t * 9)
    auto(st, t, x, 300, droga=t * 400, pasazerowie=[("boyd", (372, 128), (170, 165)),
                                                   ("bonnie", (505, 126), (lerp(0, 150, ease(pr(t, 2.4, 0.4))) + 8 * math.sin(t * 8) * (t > 3), 0), -1)])
    podpis(w, t, "Percy Boyd, police chief", 560, 250, 1.0, 3.6)
    koniec(st, w, t)


def s_boyd_tab(st, w, t, T):
    """Boyd stoi przy drodze i patrzy za odjeżdżającym Fordem; tabliczka „SHE DOESN'T SMOKE CIGARS!”."""
    kam(st, t, 91, 640, 450, 1.05, 0.79)
    preria(st, t, w, slupy=True, tablice=[("KANSAS", 1100)])
    linia_granicy(st, w, (1112, 528), (1124, 599))  # marker 23.11: „linia koloru granicy przekroczenia Kansas” (jak w ujęciu 85)
    auto(st, t, jazda(t, 1.2, 3.0, 760, 1900, ease)[0], 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], kurz=t > 1.2)
    lalka(st, t, "boyd", 460, 300, flip=1, rece=(lerp(10, 160, ease(pr(t, 5.0, 0.5))) + 10 * math.sin(t * 9) * (t > 5.5), 0))
    tab_tu(st, w, t, "REMEMBER, I DON'T SMOKE CIGARS!", "boyd_tab", 680, 331, 0.97, dur=2.0)  # marker 23.11, nad Bonnie
    tab(w, t, "SHE DOESN'T SMOKE CIGARS!", 480, 230, 3.0, 5.5)
    koniec(st, w, t)


PRASA_LAMPA, PRASA_KAPELUSZ = 11.07, 12.33  # s na osi Studio (markery 23.11)


def s_prasa_cygaro(st, w, t, T):
    """Maszyna wypluwa gazety „BONNIE: NO CIGARS!”; stronica gazety zasłania scenę, a za nią jedna gazeta ląduje na biurku Hamera."""
    zmiana = 7.6
    if t < zmiana:
        kam(st, t, 92, 640, 380, 1.0, 0.72, shake=1.0)
        drukarnia(st, t, w, obrot=t * 220)
        # gag 25 (GAGI.md): drukarz czyta świeży nagłówek „BONNIE: NO CIGARS!” i zapala sobie cygaro
        czyta = 3.0 < t < 5.4
        if czyta:
            czyta_gazete(st, t, "drukarz", 1000, J.gazeta("BONNIE: NO CIGARS!", 3, 360, 480), h=310, flip=-1)
        else:
            lalka(st, t, "drukarz", 1000, 310, flip=-1, rece=(70 + 15 * math.sin(t * 5), 40))
        if t > 5.4:
            ux, uy = punkt("drukarz", 1000, 310, 176, 160, flip=-1)
            st.put(J.rek("cygaro"), ux + 2, uy, P.lalki + 0.03, h=12, anchor=(0.96, 0.5), rot=6)
            if 5.6 < t < 5.95:
                st.put(J.glow(), ux - 40, uy, P.lalki + 0.035, w=60, anchor=(0.5, 0.5), mode="add", alpha=0.9, shadow=None,
                       tint=(1.0, 0.8, 0.4))
            for m in range(3):
                f = ((t - 6.0) * 0.5 + m / 3) % 1.0
                if t > 6.0:
                    st.put(J.glow(r=256, color=(210, 210, 210)), ux - 50 - 20 * f, uy - 20 - 120 * f, P.lalki + 0.035, w=30 + 60 * f,
                           anchor=(0.5, 0.5), alpha=0.5 * (1 - f), shadow=None)
        for n in range(12):
            f = ((t * 0.6 + n / 12) % 1.0)
            if t < 0.6 + n * 0.15:
                continue
            st.put(J.gazeta("BONNIE: NO CIGARS!", n % 4, 360, 480), 820 + f * 900 + 40 * math.sin(n), 300 - f * 520 + 80 * math.sin(f * 3 + n),
                   P.drzewa + 0.02 * (n % 3), h=110, anchor=(0.5, 0.5), rot=f * 200 + n * 30, sx=max(0.08, abs(math.cos(f * 6 + n))), shadow=(4, 6, 6, 0.3))  # bez lustrzanych napisów
    else:
        kam(st, t, 93, 520, 460, 1.3, 0.8)
        # markery reżysera 23.11: „mapa niżej” (7,47 s, wspólne _biuro), „lampa zaświeciła” (11,07 s) — do tej chwili lampa nie
        # świeci, potem mrugnie i zostaje zapalona; „czapka z dziurą przekręca się minimalnie w dół” (12,33 s)
        lz = rs("prasa_cygaro", PRASA_LAMPA)
        jas = 0.22 if t < lz else (mruganie(t, lz, 0.4) if t < lz + 0.4 else 1.0)
        _biuro(st, t, w, kapelusz=True, jasnosc=jas, kapelusz_rot=7 * ease(pr(t, rs("prasa_cygaro", PRASA_KAPELUSZ), 0.4)))
        st.put(J.rek("teczka"), 470, 538, P.lalki + 0.025, h=56, anchor=(0.5, 1.0))
        f = pr(t, zmiana + 0.5, 1.6)
        if f > 0:
            st.put(J.gazeta("BONNIE: NO CIGARS!", 7, 360, 480), lerp(760, 610, f) + 40 * math.sin(f * 9) * (1 - f), lerp(-120, 538, ease(f)),
                   P.lalki + 0.026, h=lerp(130, 70, f), anchor=(0.5, 1.0), rot=lerp(30, -8, f), sy=lerp(1.0, 0.5, ease(pr(t, zmiana + 2.0, 0.3))))
    k = ease(pr(t, zmiana - 0.6, 0.6)) * (1 - ease(pr(t, zmiana, 0.6)))  # szybkie ściemnienie: zmiana dekoracji w ciemności
    koniec(st, w, t, dim=1.0 - 0.95 * k)


# ===================== AKT VII · JAK ZASTAWIĆ PUŁAPKĘ NA DUCHA =====================

METH_BIERZE = 7.43  # s na osi Studio: Ivy zabiera papier ze stołu (marker 23.11)


def s_methvin(st, w, t, T):
    """Hamer przy stole naprzeciw brodatego farmera, między nimi papier „PARDON”; farmer kiwa głową; podpis „Ivy Methvin”."""
    kam(st, t, 93, 640, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="deski", okna=(1080,), meble=(("stol", 640, 130, P.lalki + 0.02),), zarowki=(640,), noc_za_oknem=True)
    lalka(st, t, "hamer", 450, 340, flip=1, sink=0.15, rece=(lerp(30, 70, ease(pr(t, 2.8, 0.4))) * (t < 4.4) + 20, 10))
    # markery reżysera 23.11: „tabliczka We need to make a trap!” (1,57 s) nad Hamerem; „farmer podchodzi i zabiera kartkę,
    # odchodzi z powrotem na miejsce i po 1 s ją podnosi do góry” (7,43 s); „okay! let's try” (12,03 s) nad Ivym.
    # Gag 43: Ivy podnosi PARDON pod żarówkę i sprawdza go jak banknot; „HMM…”
    tab_tu(st, w, t, "WE NEED TO MAKE A TRAP!", "methvin", 373, 195, 1.57)
    r = lambda s_: rs("methvin", s_)
    tam = ease(pr(t, r(METH_BIERZE - 0.75), r(METH_BIERZE) - r(METH_BIERZE - 0.75)))
    wraca = ease(pr(t, r(METH_BIERZE + 0.25), r(METH_BIERZE + 1.0) - r(METH_BIERZE + 0.25)))
    ix = lerp(lerp(840, 745, tam), 840, wraca)
    ma = t >= r(METH_BIERZE)
    fl = 1 if 0 < wraca < 0.98 else -1
    pod = ease(pr(t, r(METH_BIERZE + 2.0), 0.5))
    siega = ease(pr(t, r(METH_BIERZE - 0.3), 0.3)) * (1 - ease(pr(t, r(METH_BIERZE + 0.1), 0.3)))
    lalka(st, t, "ivy", ix, 310, flip=fl, sink=0.15 * (1 - tam) * (1 - wraca) + 0.15 * wraca * (wraca >= 0.98) - 8 * pod * 0,
          lean=5 * math.sin(t * 9) * (6.0 < t < 7.0) - 8 * pod, rece=(30 + 55 * siega + 135 * pod, 10), hop=4 * (0 < tam < 1 or 0 < wraca < 1),
          trzyma=(J.rek("pardon"), 50, (0.5, 0.9), 0, False) if ma else None)
    if not ma:
        st.put(J.rek("pardon"), lerp(560, 670, ease(pr(t, 3.0, 1.2))), STOPY - 130, P.lalki + 0.025, h=60, anchor=(0.5, 1.0))
    tab(w, t, "HMM…", 840, 200, r(METH_BIERZE + 2.6), 1.6)
    tab_tu(st, w, t, "OKAY! LET'S TRY", "methvin", 911, 226, 12.03)
    podpis(w, t, "Ivy Methvin", 840, 260, 2.4, 3.6)
    koniec(st, w, t)


WIERSZ_WYCHODZI = 6.77  # s na osi Studio (marker 23.11)


def s_wiersz(st, w, t, T):
    """Bonnie wręcza matce zeszyt; matka czyta przy lampie, a za oknem czekają światła Forda."""
    w.noc = 1.0
    kam(st, t, 94, 680, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(1000,), meble=(("stol", 520, 130, P.lalki + 0.02),), zarowki=(520,), noc_za_oknem=True)
    for n in range(2):
        # światła Forda za oknem zapalają się dopiero, gdy stoi ściana (przegląd 19.11: świeciły na pustym płótnie)
        st.put(J.glow(r=128, color=(255, 240, 190)), 975 + 50 * n, 420, P.miasto + 0.03, w=70, anchor=(0.5, 0.5), mode="add",
               alpha=0.8 * bk(w, 0.9, 0.5), shadow=None)
    podala = t > 2.2
    zesz = (J.rek("zeszyt"), 40, (0.5, 0.5), 80, True)
    lalka(st, t, "matka_bonnie", 520, 290, flip=1, sink=0.12, lean=6 * podala, rece=(lerp(20, 80, ease(pr(t, 1.6, 0.6))), 60 * podala),
          trzyma=zesz if podala else None)
    # Bonnie po Sowers kuleje (noga z Wellington): od drzwi idzie do matki, kuśtykając; markery reżysera 23.11: „tabliczka
    # what's that?” (2,40 s) nad matką, „tabliczka Do not forget. i Bonnie idzie w prawo za kadr” (6,77 s)
    od = rs("wiersz", WIERSZ_WYCHODZI)
    bx = lerp(900, 760, ease(pr(t, 0.0, 2.2))) + 900 * pr(t, od + 0.3, 3.2)
    lalka(st, t, "bonnie", bx, 290, flip=-1 if t < od else 1, kuleje=1.0,
          rece=(lerp(80, 10, ease(pr(t, 2.2, 0.5))), 0), trzyma=zesz if not podala else None)
    tab_tu(st, w, t, "WHAT'S THAT?", "wiersz", 440, 284, 2.40)
    tab_tu(st, w, t, "DO NOT FORGET.", "wiersz", 802, 250, WIERSZ_WYCHODZI, dur=2.4)
    koniec(st, w, t)


def s_pozegnanie(st, w, t, T):
    """Ford przejeżdża powoli obok dwóch domów; w oknach dwie matki machają; Ford znika za zakrętem."""
    w.noc = 0.5
    kam(st, t, 95, 640, 440, 1.0, 0.78)
    miasto(st, t, w, fasady=(("dom", 380), ("dom", 900)), tyl=(), chodnik=True, swiatlo_okien=True)
    for n, (key, x) in enumerate((("matka_bonnie", 380), ("matka_clyde", 900))):
        lalka(st, t, key, x, 250, flip=1, p=P.drzewa, rece=(120 + 30 * math.sin(t * 6 + n), 0))
    x = jazda(t, 0.4, 6.6, -300, 1700)[0]
    auto(st, t, x, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.85, 0.82, 0.9))
    # gag 44 (GAGI.md): na „the only home” w tylnej szybie Forda kołysze się tabliczka HOME SWEET HOME
    # marker reżysera 23.11 (2,97 s): „duża tabliczka z tym napisem” — duża, czytelna, wisi w tylnej szybie przed szkłem
    kt = pr(t, rs("pozegnanie", 2.97) - 0.5, 0.5)
    if kt > 0:
        k = 230 / 360.0
        st.put(J.tag("HOME SWEET HOME", 26), x + (225 - 450) * k, DROGA_Y + (96 - 356) * k, P.auta + 0.003, h=32 * back(kt, 1.4),
               anchor=(0.5, 0.0), rot=5 * math.sin(t * 5), shadow=(2, 3, 3, 0.3))
    _reflektory(st, x, DROGA_Y, P.auta, k=0.6)
    koniec(st, w, t)


def s_henry_wsiada(st, w, t, T):
    """Na poboczu drogi pod Shreveport chłopak w kaszkiecie macha do Forda; Ford zwalnia, chłopak wsiada na tylne siedzenie
    (podpis „Henry Methvin”). Pierwsze pokazanie Henry'ego w gangu: w akcie V był jednym z uwolnionych w Eastham."""
    kam(st, t, 135, 640, 440, 1.05, 0.79)
    preria(st, t, w, slupy=True, plot=False)
    if t < 2.6:
        x = jazda(t, 0.0, 2.6, -320, 640, ease_out)[0]
    else:
        x = 640 + 1400 * ease(pr(t, 4.4, 1.4))
    wsiada = pr(t, 2.9, 0.4)
    pas = [("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))] + ([("henry", (410, 128), (0, 0))] if wsiada > 0.5 else [])
    auto(st, t, x, 230, pasazerowie=pas)
    if wsiada < 1:
        lalka(st, t, "henry", 800, 290, flip=-1, rece=(120 + 40 * math.sin(t * 8), 0), alpha=1.0 - wsiada)
    podpis(w, t, "Henry Methvin", 800, 240, 3.2, 3.0)
    koniec(st, w, t)


SHREV_SYLWETKA = (6.8, 10.4)  # s na osi Studio: sylwetka Henry'ego za szybą kawiarni


def s_shreveport(st, w, t, T):
    """Przed kawiarnią w Shreveport chłopak wysiada z Forda i znika w tłumie; podpis „Henry Methvin”; Ford odjeżdża bez niego."""
    kam(st, t, 96, 640, 440, lerp(1.1, 0.98, ease(t / T)), 0.79)
    miasto(st, t, w, fasady=(("bank", 220), ("kawiarnia", 700), ("apteka", 1160)), chodnik=True)
    x = jazda(t, 0.4, 2.4, -300, 480, ease_out)[0] if t < 10.0 else jazda(t, 10.0, 3.0, 480, 1800, ease)[0]
    pas = [("bonnie", (330, 132), (0, 0)), ("clyde", (505, 126), (40, 0))] + ([("henry", (410, 128), (0, 0))] if t < 3.4 else [])
    auto(st, t, x, 230, pasazerowie=pas)
    if 3.4 <= t < 6.6:
        hx = jazda(t, 3.6, 2.0, 560, 700)[0]
        lalka(st, t, "henry", hx, 290, flip=1, hop=4 * (t < 5.6), alpha=1.0 - ease(pr(t, 5.8, 0.8)))  # wchodzi do kawiarni
    # marker reżysera 23.11 (8,00 s): „za szybą jego czarna sylwetka troszkę niżej, podnosi rękę z kawą” — Henry w kawiarni,
    # widać go tylko w oknie (1.1)
    s0, s1 = rs("shreveport", SHREV_SYLWETKA[0]), rs("shreveport", SHREV_SYLWETKA[1])
    if s0 < t < s1:
        # marker reżysera 24.11 (8,13 s): „tu go postaw i za tymi białymi kreskami” — sylwetka stoi w lewej części okna (kreska
        # x 782–820) i chowa się za białymi szczeblami okna; punkty ekranu z chwili markera przeliczone kamerą z tej chwili,
        # więc sylwetka i szczeble stoją w oknie fasady, a nie w miejscu ekranu (kamera się oddala)
        class _K:
            pass
        km = _K()
        km.T = T
        kam(km, rs("shreveport", 8.13), 96, 640, 440, lerp(1.1, 0.98, ease(rs("shreveport", 8.13) / T)), 0.79)
        na_sw = lambda sx, sy: ekran_do_swiata(km.cam, sx, sy, P.most + 0.001)
        (ax, ay), (bx_, by_) = na_sw(770, 386), na_sw(848, 471)
        kawa = ease(pr(t, rs("shreveport", 7.7), 0.3)) * (1 - ease(pr(t, rs("shreveport", 9.0), 0.3)))
        reka = int(round(lerp(30, 115, kawa) / 15) * 15)
        spr = J.sylwetka_w_oknie("henry", reka, ("kubek", 26, (0.5, 0.6)), (bx_ - ax) / (by_ - ay))
        # wycinek przycina się do postaci: skala z wysokości okna, lewa krawędź (plecy) stoi w miejscu
        sk_ = (by_ - ay) / spr.h
        lewa = (ax + bx_) / 2 - J.sylwetka("henry", rece=(30, 15), rzecz=("kubek", 26, (0.5, 0.6))).size[0] / 2 * sk_
        st.put(spr, lewa, by_ - 2, P.most + 0.001, h=by_ - ay, anchor=(0.0, 1.0), alpha=0.85 * ease(pr(t, s0, 0.3)) * (1 - ease(pr(t, s1 - 0.3, 0.3))),
               shadow=None)
        for (x1, y1), (x2, y2) in ((na_sw(831, 343), na_sw(831, 478)), (na_sw(764, 396.5), na_sw(899, 396.5))):  # szczeble przed sylwetką
            st.line([(x1, y1), (x2, y2)], P.most + 0.0015, width=5.6, color=(236, 232, 220), alpha=1.0)
    # gag 45 (GAGI.md): Henry wychodzi z kawiarni z dwiema kanapkami, a Forda już nie ma; rozgląda się w lewo i w prawo
    # (marker reżysera 23.11, 12,70 s: „jeszcze 2× go zrób lewo prawo”)
    if t >= 11.1:
        r0 = rs("shreveport", 12.7)
        rozg = (-1 if 11.7 < t < 12.4 else 1) if t < r0 else (-1 if int((t - r0) / 0.36) % 2 == 0 and t < r0 + 4 * 0.36 else 1)
        lalka(st, t, "henry", 700, 290, ease(pr(t, 11.1, 0.4)), flip=rozg, rece=(70, 70), trzyma=(J.rek("kanapka"), 22, (0.5, 0.5), 0, False))
    for n, key in enumerate(("przechodzien", "przechodnia", "przechodzien2", "przechodnia2", "przechodzien3")):
        kier = 1 if n % 2 else -1
        px = (300 + n * 260 + kier * t * 70) % 1600 - 160
        lalka(st, t, key, px, 290 + 8 * (n % 2), flip=kier, p=P.lalki + 0.02, hop=4)
    podpis(w, t, "Henry Methvin", 700, 250, 3.8, 3.6)
    tab(w, t, "...?", 700, 250, 12.4, 1.8)
    koniec(st, w, t)


def _krzaki_lowcow(st, t, sink, tint=None, karabiny=False, xs=None):
    xs = xs or [170 + 188 * n for n in range(6)]
    for n, ((key, _), x) in enumerate(zip(LOWCY, xs)):
        # karabiny pionowo, wszyscy po jednej stronie drogi patrzą w tę samą stronę (było: sąsiedzi twarzą w twarz, karabiny w X)
        lalka(st, t, key, x, 300, flip=(1 if x < 640 else -1) if karabiny else (-1 if n % 2 else 1), sink=sink, tint=tint,
              rece=(15, 10) if karabiny else (20, 10), trzyma=KARABIN_PION(150) if karabiny else None)
        st.put(J.krzak(n), x, STOPY + 4, P.lalki + 0.02, h=130, anchor=(0.5, 1.0), tint=tint)
    return xs


def s_noc(st, w, t, T):
    """„DAY 101”; noc w lesie, sześciu mężczyzn kuli się w krzakach; nad kapeluszami krążą komary, jeden bezgłośnie klepie się w kark."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 97, 640, 500, 1.15, 0.79)
    w.zawieszki = [("DAY 101", 640, 220, pr(t, 0.8, 1.0))]
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, noc=1.0)
    xs = [170 + 188 * n for n in range(6)]
    for n, ((key, _), x) in enumerate(zip(LOWCY, xs)):
        # gag 26 (GAGI.md): na „swatting mosquitoes” szeryfowie po kolei klepią komary; Hinton klepie sąsiada w policzek,
        # obaj zastygają, Hamer: „SHHH!”
        klap = (_bump(t, 7.0, 0.25) if n == 2 else 0.0) + _bump(t, 9.7 + 0.3 * n, 0.18) * (n < 3)
        do_sasiada = ease(pr(t, 10.6, 0.15)) * (1 - ease(pr(t, 12.4, 0.4))) * (n == 3)
        lalka(st, t, key, x, 300, flip=-1 if n % 2 else 1, sink=0.22, tint=NOC, rece=(20 + 150 * min(1.0, klap) + 140 * do_sasiada, 10),
              lean=-14 * do_sasiada)
        st.put(J.krzak(n), x, STOPY + 4, P.lalki + 0.02, h=130, anchor=(0.5, 1.0), tint=NOC)
        tab(w, t, "SHHH!", xs[0], 300, 11.2, 1.8) if n == 0 else None
        if n == 4:  # marker reżysera 23.11 (7,00 s): „tabliczka yaw” — Jordan ziewa
            tab_tu(st, w, t, "YAWN", "noc", 933, 276, 7.0)
        for m in range(2):
            a = t * 7 + m * 3 + n
            st.put(J.rek("pinezka"), x + 40 * math.cos(a), 440 + 14 * math.sin(a * 1.3), P.lalki + 0.03, h=6, anchor=(0.5, 0.5),
                   tint=(0.1, 0.1, 0.1), shadow=None)
    koniec(st, w, t)


def s_posse(st, w, t, T):
    """W krzakach sześciu mężczyzn; nad każdym po kolei zjeżdża podpis; Hinton przeciera okulary."""
    w.noc, w.moon = 0.75, 0.6
    kam(st, t, 98, lerp(320, 960, ease(t / T)), 520, 1.35, 0.79)
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, noc=0.75)
    xs = [170 + 188 * n for n in range(6)]
    for n, ((key, imie), x) in enumerate(zip(LOWCY, xs)):
        okul = n == 3 and 6.5 < t < 9.0
        # gag 46 (GAGI.md): ostatni podpis spada za nisko i stuka młodego Oakleya w kapelusz; Oakley się kuli, „OUCH!”
        stuk = 0.22 * _bump(t, 11.75, 0.35) if n == 5 else 0.0
        fl = -1 if n % 2 else 1
        rk, sk, kap, krot = ((110 + 20 * math.sin(t * 10)) if okul else 15), 1.0, False, 0.0
        if n == 1:  # uwaga reżysera 23.11: Gault zdejmuje kapelusz ręką, uchyla go i odkłada na głowę, ręka wraca w dół przy ciele
            u = kapelusz_reka(key, x, 300, t, 1.0 + 2.0 * n + 0.4, flip=fl, sink=0.18, spocz=15)
            if u:
                rk, sk, kap, krot = u
        if n == 4:  # marker reżysera 23.11 (11,47 s): „niech podniesie broń góra dół”
            rk = 15 + 70 * math.sin(math.pi * pr(t, rs("posse", 11.2), 0.5)) + 70 * math.sin(math.pi * pr(t, rs("posse", 11.75), 0.5))
        lalka(st, t, key, x, 300, flip=fl, sink=0.18 + stuk, tint=(0.82, 0.82, 0.92), rece=(rk, 10), skrot=(sk, 1.0),
              kapelusz_reka=kap, kapelusz_rot=krot, trzyma=None if (okul or n == 1 and kap) else KARABIN_PION(150))
        st.put(J.krzak(n), x, STOPY + 4, P.lalki + 0.02, h=130, anchor=(0.5, 1.0), tint=(0.82, 0.82, 0.92))
        podpis(w, t, imie, x, 360 + (50 * _bump(t, 11.75, 0.35) if n == 5 else 0), 1.0 + 2.0 * n, 2.6)
    tab(w, t, "OUCH!", xs[5] - 60, 300, 11.8, 1.4)
    koniec(st, w, t)


def s_zasadzka_rano(st, w, t, T):
    """„DAY 102”; świt na leśnej drodze; ciężarówka Ivy'ego stoi na lewarku; w krzakach sześć kapeluszy i luf."""
    kam(st, t, 99, 640, 450, 1.0, 0.78)
    w.zawieszki = [("DAY 102", 640, 160, pr(t, 0.8, 1.0))]
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=1.0)
    ciezarowka(st, t, 640, 260, lewarek=ease(pr(t, 1.0, 1.5)))
    lalka(st, t, "ivy", 900, 300, y=STOPY + 46, flip=-1, rece=(20, 0), p=P.lalki + 0.03)  # marker 23.11: „farmera przesuń w dół kadru”
    _krzaki_lowcow(st, t, 0.3, karabiny=True, xs=[-20, 90, 200, 1080, 1190, 1300])
    koniec(st, w, t, extra=(1.06, 0.98, 0.9))


def s_kanapka(st, w, t, T):
    """Wnętrze Forda: Bonnie w czerwonej sukience je kanapkę z papierka; Clyde prowadzi w ciemnych okularach."""
    kam(st, t, 100, 640, 480, 1.6, 0.79)
    st.dof = 1.3
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=0.6, kul=False)
    h = 330
    x = 640 + 4 * math.sin(t * 9)
    gryz = 0.5 + 0.5 * math.sin(t * 2.2)
    auto(st, t, x, h, droga=t * 300, pasazerowie=[("bonnie_czerwona", (372, 128), (lerp(70, 110, gryz), 70)), ("clyde", (505, 126), (60, 40))])
    k = h / 360.0
    # kanapka przy ustach, w oknie przed szybą (przegląd 19.11: leżała za karoserią i nie było jej widać)
    # marker reżysera 23.11 (0 s): „przesuń kanapkę w tym miejscu” — trochę dalej od twarzy, przed nią
    # marker reżysera 24.11 (0 s): „przesuń kanapkę w tym miejscu minimalnie w lewo, do ust” — lewy koniec kanapki przy ustach
    st.put(J.rek("kanapka"), x + (372 - 450) * k + 29 + 4 * gryz, DROGA_Y + (128 - 356) * k + 22 - 6 * gryz, P.auta + 0.0015, h=26,
           anchor=(0.5, 0.5), rot=-10)
    dh = h * 0.92
    sx_ = x + (505 - 450) * k
    stopy = DROGA_Y + (126 - 356) * k + (676 - 128) / 614.0 * dh
    oczy = []
    for u, v in OCZY:
        ex, ey = punkt("clyde", sx_, dh, u, v, y=stopy)
        oczy.append((ex, ey))
        st.put(J.listwa(30, 18, (24, 22, 24)), ex, ey, P.auta - 0.0035, h=14 * dh / 300, anchor=(0.5, 0.5), shadow=None)
    # gag 27 (GAGI.md): liść sałaty z kanapki Bonnie spada Clyde'owi na okulary; Clyde go nie zdejmuje i prowadzi dalej
    fs = pr(t, 4.8, 0.5)
    if fs > 0:
        kx_, ky_ = x + (372 - 450) * k + 34, DROGA_Y + (128 - 356) * k + 14
        ox_, oy_ = (oczy[0][0] + oczy[1][0]) / 2, (oczy[0][1] + oczy[1][1]) / 2
        st.put(J.rek("salata"), lerp(kx_, ox_, ease(fs)), lerp(ky_, oy_, fs) - 40 * math.sin(math.pi * fs), P.auta + 0.0016, h=24,
               anchor=(0.5, 0.5), rot=lerp(40, -6, fs))
    koniec(st, w, t, extra=(1.04, 0.98, 0.92))


def s_zwolnienie(st, w, t, T):
    """Ford zwalnia przy ciężarówce; Ivy macha z pobocza; Clyde wychyla się przez okno."""
    kam(st, t, 101, 700, 460, 1.1, 0.79)
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=0.8, kul=False)
    ciezarowka(st, t, 1060, 210, lewarek=1.0)
    lalka(st, t, "ivy", 860, 300, flip=-1, rece=(130 + 30 * math.sin(t * 10), 0))
    tab_tu(st, w, t, "HEY, HELP ME!", "zwolnienie", 681, 214, 0.67, dur=1.8)  # marker reżysera 23.11 (0,67 s)
    auto(st, t, jazda(t, 0.0, 1.8, 200, 560, ease_out)[0], 240, pasazerowie=[("bonnie_czerwona", 0, (0, 0)), ("clyde", 1, (40 + 60 * ease(pr(t, 1.2, 0.5)), 0))])
    koniec(st, w, t, extra=(1.04, 0.98, 0.92))


ZAS_KAPELUSZ = (2.87, 4.0)  # s na osi Studio: kapelusz wylatuje z auta … ląduje na ziemi


def s_zasadzka(st, w, t, T):
    """Za parawanem dziesiątki błysków jeden po drugim, papierowy Ford drży i powoli zjeżdża do rowu; spada kapelusz; cisza (szczyt 3)."""
    kam(st, t, 102, 640, 460, 1.25, 0.79, lens=1.4, shake=2.5 * (0.3 < t < 2.6))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    f = ease(pr(t, 2.6, 1.6))
    x = 640 + 6 * math.sin(t * 40) * (0.3 < t < 2.6) + 120 * f
    auto(st, t, x, 190, y=y0 - 26 + 40 * f, p=p0 + 0.001, przechyl=10 * f, tint=(0.08, 0.06, 0.05), alpha=1.0, shadow=None, blur=1.6, szyby=False)
    for n in range(28):
        bx = 150 + 40 * (n % 4) if n % 2 == 0 else 1130 - 40 * (n % 4)
        blysk(st, bx, y0 - 120 - 30 * (n % 3), p0 + 0.003, t, 0.3 + 0.075 * n, r=160)
    # marker reżysera 23.11 (2,87 s): „kapelusz stąd leci do góry w tym kierunku i spada na ziemię w 4 s” — wylatuje z okna
    # auta, łukiem w górę i w prawo, kręci się i ląduje na ziemi w 4 s (punkty z kreski markera)
    k0, k1 = rs("zasadzka", ZAS_KAPELUSZ[0]), rs("zasadzka", ZAS_KAPELUSZ[1])
    f2 = pr(t, k0, k1 - k0)
    if f2 > 0:
        a_ = ekran_do_swiata(st.cam, 697, 456, p0 + 0.003)
        b_ = ekran_do_swiata(st.cam, 800, 265, p0 + 0.003)
        c_ = ekran_do_swiata(st.cam, 1085, 598, p0 + 0.003)  # przed maską auta, nad dolną ramą parawanu — widać, że leży
        q = min(1.0, f2)
        hx = (1 - q) ** 2 * a_[0] + 2 * q * (1 - q) * (2 * b_[0] - 0.5 * (a_[0] + c_[0])) + q * q * c_[0]
        hy = (1 - q) ** 2 * a_[1] + 2 * q * (1 - q) * (2 * b_[1] - 0.5 * (a_[1] + c_[1])) + q * q * c_[1]
        st.put(J.rek("kapelusz_fedora"), hx, hy, p0 + 0.003, h=36, anchor=(0.5, 0.6), rot=540 * q if q < 1 else 15,
               tint=(0.08, 0.06, 0.05), shadow=None, blur=1.6)
    koniec(st, w, t, dim=0.88 * (1 - 0.3 * ease(pr(t, 3.6, 1.0))))


DYM_KAPELUSZ = 5.5  # s na osi Studio: Hamer sięga do kapelusza (marker 23.11: 5,77 s — ręka przy kapeluszu)
DYM_TABLICZKI = 6.7  # s na osi Studio: sześć tabliczek „WE GOT THEM!”


def s_dym(st, w, t, T):
    """Dym opada; mężczyźni wychodzą z krzaków z bronią; jeden zdejmuje kapelusz; nikt nic nie mówi."""
    kam(st, t, 103, 640, 450, 1.05, 0.79)
    las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=False, swit=1.0)
    # markery reżysera 23.11: „więcej dziur” (0 s) — auto podziurawione gęsto; „dym stąd” (0 s) — dym unosi się znad auta, z prawej;
    # „ręka do kapelusza i ściąga go, i w dół go w ręce” (5,77 s) — Hamer zdejmuje kapelusz ręką i trzyma go przy boku
    auto(st, t, 960, 230, y=DROGA_Y + 30, przechyl=8, dziury=90)
    for n, (key, _) in enumerate(LOWCY):
        x = 120 + 110 * n
        wyj = ease(pr(t, 1.5 + 0.3 * n, 1.2))
        if key == "hamer":
            x = 760
            sink = 0.5 * (1 - wyj)
            u = kapelusz_reka("hamer", x, 340, t, rs("dym", DYM_KAPELUSZ), flip=1, sink=sink, wroc=False)
            rk, sk, kap, krot = u if u else (20, 1.0, False, 0.0)
            lalka(st, t, "hamer", x, 340, flip=1, sink=sink, rece=(rk, 0), skrot=(sk, 1.0), kapelusz_reka=kap, kapelusz_rot=krot)
        else:
            lalka(st, t, key, x, 300, flip=1, sink=0.5 * (1 - wyj), rece=(20, 0), trzyma=KARABIN(150))
        # marker reżysera 23.11 (6,70 s): „6 tabliczek we got them!” — nad każdym z sześciu po kolei, na przemian wyżej i niżej
        kt = pr(t, rs("dym", DYM_TABLICZKI) - 0.7 + 0.15 * n, 0.9) * (1 - pr(t, rs("dym", DYM_TABLICZKI) + 2.6, 0.6))
        if kt > 0:
            J.hang(st, J.tag("WE GOT THEM!", 24), x, 170 + 62 * (n % 2), P.rekwizyty + 0.02, kt, t, 700 + n, drop=460, sway=1.4, h=32,
                   shadow=(4, 6, 6, 0.4))
    # marker reżysera 24.11 (3,77 s): „dłużej dym” — dym znad auta (marker 23.11: „dym stąd”) unosi się przez całe ujęcie: nowe
    # kłęby wychodzą z auta do końca, gęstnieją w pierwszych sekundach i dopiero pod koniec rzedną
    gest = 1.0 - 0.55 * ease(pr(t, 6.5, T - 6.5))
    for n in range(14):
        f = ((t * 0.22 + n / 14) % 1.0)
        sx_, sy_ = ekran_do_swiata(st.cam, 1150 + 40 * math.sin(n * 2.1), 560 - 10 * (n % 5), P.lalki + 0.03)
        st.put(J.rek("oblok"), sx_ + 70 * f + 15 * math.sin(t + n), sy_ - 330 * f, P.lalki + 0.03 + 0.0002 * n,
               h=70 + 150 * f, anchor=(0.5, 0.5), rot=n * 37 + 20 * t, tint=(0.62, 0.6, 0.58),
               alpha=0.8 * gest * math.sin(math.pi * min(1.0, f * 1.15)), shadow=None)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96), dim=1.0 - 0.15 * ease(pr(t, 8.0, 3.0)))


def clamp_(v):
    return max(0.0, min(1.0, v))


# ===================== AKT VIII · DO KOGO NALEŻY LEGENDA =====================

PAM_LATAJA = 3.4  # s na osi Studio: rzeczy Bonnie zaczynają latać nad tłumem (marker 23.11: 3,67 s)


def s_pamiatki(st, w, t, T):
    """Tłum otacza podziurawionego Forda w Arcadii; ktoś odchodzi ze skrawkiem sukienki, ktoś z puklem włosów; szeryf odgania ludzi."""
    kam(st, t, 104, 640, 440, lerp(1.15, 0.95, ease(t / T)), 0.79)
    miasto(st, t, w, fasady=(("meble", 300), ("zaklad", 960)), tyl=(("dom", 640),), chodnik=True)
    auto(st, t, 640, 230, dziury=30)
    for n, (key, x0) in enumerate((("przechodzien", 250), ("przechodnia", 430), ("przechodzien2", 540), ("farmer", 660), ("przechodnia2", 780),
                                   ("przechodzien3", 990), ("farmer2", 1080))):
        x = x0 + 10 * math.sin(t * 3 + n)
        za_autem = 400 < x0 < 880  # tłum za autem: widać go nad dachem, auto zostaje widoczne
        lalka(st, t, key, x, 300 + 10 * (n % 3), flip=1 if x < 640 else -1, p=(P.auta - 0.006 - 0.001 * (n % 3)) if za_autem else P.lalki + 0.01,
              lean=(8 if x < 640 else -8) * (0.5 + 0.5 * math.sin(t * 2 + n)), rece=(60 + 30 * math.sin(t * 4 + n), 20), hop=3)
    for n, (key, x0, x1, spr, tint) in enumerate((("przechodnia", 560, 120, J.rek("pranie"), (0.9, 0.3, 0.3)), ("przechodzien", 760, 1200, J.platek((240, 210, 120)), None))):
        f = ease(pr(t, 5.6 + 0.6 * n, 3.0))
        if f > 0:
            out = lalka(st, t, key, lerp(x0, x1, f), 290, flip=1 if x1 > x0 else -1, p=P.lalki + 0.03, rece=(100, 0), hop=4)
            if out:
                st.put(spr, out[0], out[1], P.lalki + 0.035, h=20, anchor=(0.5, 0.3), tint=tint)
    # marker reżysera 23.11 (3,67 s): „latają te rzeczy Bonnie w powietrzu między ludźmi” — pukle włosów, skrawki czerwonej
    # sukienki i beret przelatują łukami od auta do rąk ludzi i między nimi (kreski: łuki nad głowami tłumu)
    r0 = rs("pamiatki", PAM_LATAJA)
    rzeczy = ((J.platek((236, 204, 120)), 34, None), (J.rek("pranie"), 40, (0.95, 0.25, 0.25)), (J.platek((226, 192, 110)), 30, None),
              (J.rek("pranie"), 36, (0.85, 0.2, 0.22)), (J.platek((240, 212, 130)), 32, None), (J.rek("pranie"), 34, (0.9, 0.3, 0.3)))
    luki = ((640, 250), (600, 1100), (250, 900), (980, 430), (430, 1080), (1080, 250), (780, 300), (300, 780))
    if t > r0:
        for n in range(8):
            a_, b_ = luki[n]
            okres = 1.5 + 0.2 * (n % 3)
            f = ((t - r0) / okres + n * 0.37) % 1.0
            if t - r0 < n * 0.25:
                continue
            spr, hh, tn = rzeczy[n % len(rzeczy)]
            st.put(spr, lerp(a_, b_, f), 440 - 190 * math.sin(math.pi * f), P.lalki + 0.04, h=hh, anchor=(0.5, 0.5),
                   rot=360 * f * (1 if b_ > a_ else -1), tint=tn, shadow=(3, 4, 4, 0.3))
    lalka(st, t, "szeryf", 1120, 320, flip=-1, rece=(90 + 50 * math.sin(t * 8) * (t > 7.0), 60 * (t > 7.0)))
    tab(w, t, "BACK OFF!", 1100, 260, 7.4, 3.0)
    koniec(st, w, t)


DARBY_IDZIE = 6.27  # s na osi Studio (markery 23.11)


def s_darby_zaklad(st, w, t, T):
    """W zakładzie pogrzebowym młody mężczyzna w fartuchu zakłada rękawice; zjeżdża jego stary podpis."""
    kam(st, t, 105, 600, 460, 1.25, 0.8)
    # markery reżysera 23.11 (6,27 s): „zamrugał lampą” i „undertaker podchodzi w to miejsce” — lampa mruga, Darby idzie w prawo
    # do miejsca z kreski (przy stole)
    dz = rs("darby_zaklad", DARBY_IDZIE)
    wnetrze(st, t, w, sciana="paski", okna=(1050,), meble=(("stol_obrus", 800, 120, P.lalki + 0.02),), zarowki=(640,), tint=(0.85, 0.88, 0.9),
            jasnosc=mruganie(t, dz, 1.2))
    cel_x = ekran_do_swiata(st.cam, 672, 0, P.lalki + 0.01)[0]
    idz = ease(pr(t, dz - 0.6, 1.2))
    lalka(st, t, "darby_fartuch", lerp(520, cel_x, idz), 300, flip=1, rece=(80 + 12 * math.sin(t * 7) * (1.0 < t < 3.6), 70), hop=4 * (0 < idz < 1))
    podpis(w, t, "Dillard Darby, undertaker", 520, 230, 2.0, 5.0)
    koniec(st, w, t, extra=(0.94, 0.97, 1.02))


POGRZEB_DESZCZ = 6.43  # s na osi Studio (marker reżysera 24.11)


def s_pogrzeby(st, w, t, T):
    """Dwa osobne pogrzeby na dwóch cmentarzach, między nimi droga; tłumy przy obu; matka Bonnie odwraca się plecami."""
    kam(st, t, 106, 640, 440, lerp(1.1, 0.95, ease(t / T)), 0.79)
    cmentarz(st, t, w)
    # nazwy cmentarzy wiszą nad każdym z dwóch tłumów (przegląd 19.11: tablice na słupkach przy krawędziach kadru
    # zasłaniali żałobnicy, a „buried in different cemeteries” to puenta ujęcia)
    for n, (txt, x) in enumerate((("Fishtrap Cemetery", 370), ("Western Heights", 995))):
        J.hang(st, J.tag(txt), x, 190, P.wzgorza + 0.03, bk(w, 0.5 + 0.15 * n), t, 640 + n, h=50, drop=420, sway=0.5)
    for x in (330, 980):
        if bk(w, 0.6) >= 1:
            st.put(J.rek("trumna"), x, 676, P.lalki + 0.07, w=240, anchor=(0.5, 1.0))
    for n, (key, x) in enumerate((("przechodnia", 230), ("przechodzien", 300), ("matka_bonnie", 440), ("przechodnia2", 510),
                                  ("przechodzien2", 860), ("matka_clyde", 930), ("przechodzien3", 1060), ("farmer", 1130))):
        fl = 1 if x < 640 else -1
        if key == "matka_bonnie":
            fl = 1 - 2 * ease(pr(t, 6.0, 0.8))
        lalka(st, t, key, x, 280 + 10 * (n % 2), flip=fl, lean=5 * fl, rece=(10, 0))
    # marker reżysera 24.11 (6,43 s): „zaczyna padać deszcz, ale jest słonecznie nadal” — deszcz przy słońcu: z góry całej sceny
    # lecą skośne krople na nitkach światła, słońce i światło zostają (dźwięk deszczu: efekty.ZDARZENIA, POGRZEB_DESZCZ)
    td = rs("pogrzeby", POGRZEB_DESZCZ)
    if t > td:
        g = ease(pr(t, td, 1.2))
        for n in range(110):
            f = ((t - td) * 1.5 + n * 0.0917) % 1.0
            if (t - td) * 1.5 < (n * 0.0917) % 1.0 * 0.3 + (n % 4) * 0.15:
                continue
            x0, y0 = ekran_do_swiata(st.cam, (n * 97.3) % 1340 - 30, -30 + 780 * f, P.rekwizyty)
            st.line([(x0, y0), (x0 - 8, y0 + 40)], P.rekwizyty, width=2.2, color=(214, 230, 244), alpha=0.75 * g)
    koniec(st, w, t, dim=0.95)


JAR_RZUTY = ((3.6, (876.0, 420.0)), (4.23, (981.0, 433.0)))  # markery 23.11: sekunda, skąd leci moneta (ekran)


def s_auto_jarmark(st, w, t, T):
    """Na jarmarku pod namiotem stoi podziurawiony Ford; kolejka płaci za wejście i zagląda w dziury; obok kręci się diabelski młyn."""
    kam(st, t, 107, 640, 430, lerp(1.1, 0.95, ease(t / T)), 0.78)
    preria(st, t, w, droga=0.0, slupy=False, zielen=True)
    if bk(w, 0.3) > 0:
        st.put(J.kolo_mlynskie(), 1080, 360 + (1 - back(bk(w, 0.3), 1.2)) * 700, P.miasto, h=560, anchor=(0.5, 0.5), rot=t * 15)
    Z0.rise(st, J.namiot_jarmark(), 580, STOPY, P.wzgorza, bk(w, 0.4), t, 651, h=440, wob=0.0)
    auto(st, t, 580, 220, dziury=30)
    if bk(w, 0.6) >= 1:
        st.line([(300, 610), (860, 612)], P.auta + 0.01, width=3, color=(180, 40, 40))
    lalka(st, t, "przechodzien3", 200, 290, flip=1, rece=(60, 0))
    podpis(w, t, "10¢ A LOOK", 200, 300, 0.8, T)
    # gag 28 (GAGI.md, W1 „pusta kasa” — puenta): monety wpadają do kasetki, aż pęka i dziesiątki monet sypią się na trawę
    if bk(w, 0.6) >= 1:
        drzy = 3 * math.sin(t * 40) * (7.0 < t < 8.0)
        st.put(J.rek("kasetka"), 300 + drzy, 640, P.lalki + 0.02, h=70, anchor=(0.5, 1.0), rot=drzy * 0.6)
        # markery reżysera 23.11: „stąd rzuć monetę” (3,60 s — kobieta, 4,23 s — farmer): pierwsze dwie monety lecą z ich dłoni
        rzuty = [(rs("auto_jarmark", JAR_RZUTY[0][0]), ekran_do_swiata(st.cam, *JAR_RZUTY[0][1], P.lalki + 0.03)),
                 (rs("auto_jarmark", JAR_RZUTY[1][0]), ekran_do_swiata(st.cam, *JAR_RZUTY[1][1], P.lalki + 0.03))]
        for n, c in enumerate((3.9, 4.5, 5.1, 5.6, 6.0, 6.4, 6.7, 7.0)):
            c0, (sx0, sy0) = rzuty[n] if n < 2 else (c, (900 - 40 * n, 520))
            f = pr(t, c0, 0.6)
            if 0 < f < 1:
                st.put(Z0.coin(), lerp(sx0, 300, f), lerp(sy0, 580, f) - 150 * math.sin(math.pi * f), P.lalki + 0.03, h=14,
                       anchor=(0.5, 0.5), sx=abs(math.cos(f * 14)) * 0.8 + 0.2)
        if t > 8.0:
            for n in range(26):
                f = min(1.0, (t - 8.0) / (0.6 + 0.02 * n))
                ang = -math.pi * (0.15 + 0.7 * ((n * 37) % 26) / 26)
                v = 160 + (n * 53) % 120
                st.put(Z0.coin(), 300 + math.cos(ang) * v * f, 590 + math.sin(ang) * v * f + 260 * f * f, P.lalki + 0.03, h=13,
                       anchor=(0.5, 0.5), sx=abs(math.cos(f * 10 + n)) * 0.8 + 0.2)
    for n, key in enumerate(("przechodnia", "farmer", "dziecko1", "przechodzien", "przechodnia2")):
        x = lerp(1400 + 120 * n, 900 + 100 * n, ease(pr(t, 0.6 + 0.6 * n, 3.0)))
        rzut = math.sin(math.pi * pr(t, rs("auto_jarmark", JAR_RZUTY[n][0]) - 0.25, 0.5)) if n < 2 else 0.0
        lalka(st, t, key, x, 290 if "dziecko" not in key else 200, flip=-1, lean=-10 * ease(pr(t, 3.8 + 0.6 * n, 0.5)), hop=4 * (t < 3.6 + 0.6 * n),
              rece=(20 + 110 * rzut, 0))
    koniec(st, w, t)


def s_blanche_po(st, w, t, T):
    """Starsza Blanche w okularach podlewa kwiaty przed domkiem; zjeżdża zawieszka „1988”."""
    kam(st, t, 108, 680, 460, 1.2, 0.8)
    w.zawieszki = [("1988", 640, 160, pr(t, 1.0, 1.0))]
    miasto(st, t, w, fasady=(("dom", 560),), tyl=(), chodnik=False)
    for n, x in enumerate((800, 880, 960) if bk(w, 0.6) >= 1 else ()):
        st.put(J.rek("kwiaty"), x, STOPY + 4, P.lalki + 0.02, h=90, anchor=(0.5, 1.0), rot=3 * math.sin(t + n))
    # marker reżysera 23.11 (1,83 s): „chodzi powoli lewo prawo i podlewa” — wzdłuż grządki kwiatów w tę i z powrotem
    xa, xb = ekran_do_swiata(st.cam, 760, 0, P.lalki + 0.01)[0], ekran_do_swiata(st.cam, 990, 0, P.lalki + 0.01)[0]
    fz = 0.5 - 0.5 * math.cos(t * 2 * math.pi / 5.0)
    bx = lerp(xa, xb, fz)
    kier = 1 if math.sin(t * 2 * math.pi / 5.0) >= 0 else -1
    out = lalka(st, t, "blanche_stara", bx - 70, 290, flip=kier, rece=(70, 10), trzyma=(J.rek("dzbanek"), 40, (0.3, 0.3), 40, True), hop=2)
    if out:
        for n in range(5):
            f = (t * 1.4 + n / 5) % 1.0
            st.put(J.platek((150, 190, 230)), out[0] + kier * (60 + 40 * f), out[1] + 10 + 140 * f * f, P.lalki + 0.03, h=8, anchor=(0.5, 0.5),
                   shadow=None)
    koniec(st, w, t)


def s_hamer_ganek(st, w, t, T):
    """Hamer na ganku odkłada gazetę o zasadzce, zakłada kapelusz i odwraca się od reporterów."""
    kam(st, t, 109, 600, 450, 1.1, 0.8)
    _ganek(st, t, w)
    odl = ease(pr(t, 2.0, 0.6))
    kap = t > 3.5
    hx = lerp(640, 960, ease(pr(t, 5.0, 2.2)))
    fl_h = -1 if t < 4.5 else 1
    if odl < 0.5:
        czyta_gazete(st, t, "hamer" if kap else "hamer_bez", hx, J.gazeta("OUTLAWS DIE IN AMBUSH", 5, 360, 480), h=340, flip=fl_h, hgaz=140)
    else:
        lalka(st, t, "hamer" if kap else "hamer_bez", hx, 340, flip=fl_h, rece=(20, 20), hop=3 * (5.0 < t < 7.2))
    if odl >= 1:
        st.put(J.gazeta("OUTLAWS DIE IN AMBUSH", 5, 360, 480), 800, STOPY - 120, P.lalki - 0.004, h=60, anchor=(0.5, 1.0), rot=-6)
    lalka(st, t, "reporter", 220, 300, flip=1, lean=6, rece=(80, 30))
    lalka(st, t, "fotograf", 360, 300, flip=1, rece=(90, 80), trzyma=(J.rek("aparat"), 50, (0.5, 0.5), 90, True))
    for t0 in (1.6, 3.0, 5.4):
        blysk(st, 420, 470, P.lalki + 0.02, t, t0, r=200, kolor=(1.0, 1.0, 1.0))
    koniec(st, w, t)


def _ekran(sx0, sy0, s):
    return sx0, sy0, 1060 * s, 520 * s


FILM_SCENA3 = 10.0  # s na osi Studio: trzecia scena na płótnie (uwaga reżysera 24.11)


def s_film_hamer(st, w, t, T):
    """Ekran kina: piękna para z filmu z 1967 roku, potem aktor-Hamer związany, a filmowa Bonnie robi sobie z nim zdjęcie; widownia
    się śmieje; obok ekranu prawdziwy Hamer z tabliczką „THAT'S NOT ME!”."""
    kam(st, t, 110, 640, 390, 0.95, 0.78)
    ex, ey, ew, eh = _ekran(*kino(st, t, w))
    pe = P.miasto + 0.003
    film = dict(tint=(0.82, 0.82, 0.86), shadow=None, p=pe, y=ey + eh - 8)
    # uwaga reżysera 23.11: „poruszaj tymi postaciami, obiektami na tym płótnie kina tak, jakby film po prostu leciał” — auto
    # wjeżdża, para idzie do siebie, tańczy i się obraca; w drugiej scenie związany Hamer szarpie się, a filmowa Bonnie krąży
    # wokół niego z aparatem i pozuje do kilku zdjęć; obraz lekko migocze jak z projektora
    # uwaga reżysera 24.11: „od 10 s daj jeszcze jedno jakieś ujęcie na płótno” — trzecia scena filmu na kwestię „so his family
    # sued the studio”: kronika filmowa, wirująca gazeta „HAMERS SUE STUDIO” zatrzymuje się przodem do widowni
    t3 = rs("film_hamer", FILM_SCENA3)
    if t >= t3:
        k3 = pr(t, t3, 0.9)
        st.put(J.gazeta("HAMERS SUE STUDIO", 61, 360, 480, tytul="THE DAILY NEWSREEL"), ex + ew / 2, ey + eh * 0.52, pe,
               h=eh * 0.86 * lerp(0.12, 1.0, ease(k3)), anchor=(0.5, 0.5), rot=720 * (1 - ease(k3)) + 2 * math.sin(t * 1.3),
               tint=(0.84, 0.84, 0.86), shadow=None)
    elif t < 5.6:
        cx_ = jazda(t, 0.3, 1.8, 1.15, 0.78, ease_out)[0]
        auto(st, t, ex + cx_ * ew, 150, y=ey + eh - 8, p=pe - 0.0005, tint=(0.8, 0.8, 0.84), shadow=None, droga=cx_ * 900)
        do = ease(pr(t, 1.2, 1.6))
        obrot = math.cos(math.pi * 2 * pr(t, 3.4, 0.8))
        lalka(st, t, "aktor", ex + lerp(0.22, 0.36, do) * ew, 280, flip=1, rece=(lerp(20, 70, do) + 10 * math.sin(t * 3), 40), hop=3 * (0 < do < 1),
              lean=4 * math.sin(t * 2.6) * (do >= 1), **film)
        lalka(st, t, "aktorka", ex + lerp(0.6, 0.47, do) * ew, 260, flip=-1 if t < 3.4 or t > 4.2 else obrot, lean=-6 + 5 * math.sin(t * 2.6),
              rece=(70 + 20 * math.sin(t * 3), 50), hop=3 * (0 < do < 1), **film)
    else:
        hx = ex + 0.4 * ew
        szarp = 5 * math.sin(t * 11) * (int(t * 1.5) % 2)
        lalka(st, t, "aktor_hamer", hx, 290, flip=1, rece=(0, 0), lean=szarp, **film)
        for n in range(3):
            yy = ey + eh - 8 - 120 - 40 * n
            st.line([(hx - 30 + szarp, yy), (hx + 30 + szarp, yy + 6)], pe + 0.0005, width=3, color=(200, 190, 170))
        bx_ = ex + (0.62 + 0.08 * math.sin((t - 5.6) * 0.9)) * ew
        lalka(st, t, "aktorka", bx_, 260, flip=-1, lean=-6 * math.sin(t * 1.7), rece=(90, 70),
              trzyma=(J.rek("aparat"), 40, (0.5, 0.5), 90, True), hop=2, **film)
        for c in (7.0, 8.0, 9.2):  # flesz w miejscu, w którym stoi w chwili zdjęcia (stały punkt: jeden błysk = jeden dźwięk)
            bxc = ex + (0.62 + 0.08 * math.sin((c - 5.6) * 0.9)) * ew
            blysk(st, bxc - 0.04 * ew, ey + eh - 200, pe + 0.001, t, c, r=220, kolor=(1.0, 1.0, 1.0))
    st.put(J.glow(r=256, color=(255, 250, 235)), ex + ew / 2, ey + eh / 2, pe + 0.002, w=ew * 1.1, anchor=(0.5, 0.5), mode="add",
           alpha=0.05 + 0.04 * abs(math.sin(t * 23) * math.sin(t * 7.1)), shadow=None)
    if 5.4 < t < 5.8 or t3 - 0.2 < t < t3 + 0.15:  # cięcie w filmie: błysk taśmy
        st.dim = 0.3
    widownia(st, t)
    tab(w, t, "HA HA HA!", 780, 150, 8.6, 2.6)  # nad śmiejącą się aktorką; przy y 560 chował się pod napisami (przegląd 19.11)
    lalka(st, t, "hamer", 1200, 330, ease(pr(t, 9.6, 0.6)), flip=-1, rece=(20, 0))
    tab(w, t, "THAT'S NOT ME!", 1130, 240, 10.4, 4.0)
    koniec(st, w, t)


GRA_WYSKOK = 5.4  # s na osi Studio: pikselowi Bonnie i Clyde wyskakują z auta (marker 23.11: 7,20 s; 24.11 jazda krótsza — wcześniej)
GRA_ROW = 4.4      # s akcji: pikselowe auto wpada do rowu (było 6,3 — uwaga 24.11: „troszkę skróć tę jazdę auta”)
GRA_STRZALY = 6.2  # s na osi Studio: oboje strzelają pikselowymi kulami („na końcu wyskakują i strzelają oboje”)


def s_gra(st, w, t, T):
    """Ekran migocze; zamiast filmu pikselowa para uciekinierów w aucie z gry wideo; widzowie w pierwszym rzędzie trzymają pady."""
    kam(st, t, 111, 640, 420, 1.0, 0.78)
    ex, ey, ew, eh = _ekran(*kino(st, t, w))
    pe = P.miasto + 0.003
    if t < 1.6:
        for n in range(40):
            r = (int(t * 24) * 7 + n * 13) % 97 / 97.0
            st.put(J.listwa(40, 12, (210, 210, 210)), ex + ew * ((n * 0.137 + r) % 1.0), ey + eh * ((n * 0.071 + r * 0.5) % 1.0), pe, w=30,
                   anchor=(0.5, 0.5), alpha=0.6, shadow=None)
    else:
        # gag 29 (GAGI.md, W2 „rów” — puenta): pikselowe auto podskakuje i ląduje w pikselowym rowie; „AGAIN?!” jak przy radiowozach
        # uwaga reżysera 24.11: „na końcu wyskakują i strzelają oboje kulami pikselowymi, i troszkę skróć tę jazdę auta” —
        # jazda krótsza (2,8 s zamiast 4,6 s), rów i wyskok wcześniej, a na końcu oboje strzelają pikselowymi kulami w prawo
        x = ex + ew * lerp(0.25, 0.6, ease(pr(t, 1.6, GRA_ROW - 1.7)))
        sk = pr(t, GRA_ROW, 0.5)
        x += ew * 0.12 * sk
        y = ey + eh * 0.62 + 6 * abs(math.sin(t * 6)) * (sk <= 0) - eh * 0.18 * math.sin(math.pi * min(1, sk * 1.3)) + eh * 0.12 * max(0, sk - 0.6) / 0.4
        st.put(J.listwa(60, 20, (60, 44, 30)), ex + ew * 0.78, ey + eh * 0.78, pe - 0.0005, w=0.24 * ew, anchor=(0.5, 0.5), shadow=None)
        # markery reżysera 23.11 (7,20 s): „pikselowa Bonnie / Clyde wyskakuje z auta” — łukami w lewo, na dno ekranu
        wy = rs("gra", GRA_WYSKOK)
        st.put(J.gra_piksele(pusty=t >= wy), x, y, pe, w=0.4 * ew, anchor=(0.5, 0.5), rot=-24 * min(1.0, max(0.0, sk - 0.5) / 0.3), shadow=None)
        if t >= wy:
            for n, (kto, a_, b_) in enumerate((("bonnie", (822, 316), (400, 403)), ("clyde", (879, 292), (520, 403)))):
                fj = min(1.0, (t - wy - 0.12 * n) / 0.7)
                if fj > 0:
                    A = ekran_do_swiata(st.cam, *a_, pe + 0.0005)
                    B = ekran_do_swiata(st.cam, *b_, pe + 0.0005)
                    px_, py_ = lerp(A[0], B[0], fj), lerp(A[1], B[1], fj) - 0.22 * eh * math.sin(math.pi * fj)
                    zw = -1 if kto == "bonnie" and fj >= 1 else 1  # plecami do siebie: Bonnie strzela w lewo, Clyde w prawo
                    st.put(J.gra_postac(kto), px_, py_, pe + 0.0005, h=0.2 * eh, anchor=(0.5, 1.0), sx=zw, shadow=None)
                    if fj >= 1:  # pikselowy pistolet w dłoni i strzały: kula leci przez ekran, przy lufie błysk
                        hx, hy = px_ + 0.045 * eh * zw, py_ - 0.1 * eh
                        st.put(J.listwa(40, 16, (60, 60, 70)), hx, hy, pe + 0.0006, w=0.05 * eh, anchor=(0.0, 0.5), sx=zw, shadow=None)
                        kraw = ex + 10 if zw < 0 else ex + ew - 10
                        for m in range(8):
                            ts_ = rs("gra", GRA_STRZALY) + 0.32 * m + 0.16 * n
                            fk = (t - ts_) / 0.55
                            if 0 <= fk < 1:
                                st.put(J.listwa(20, 20, (255, 240, 90)), lerp(hx + 0.05 * eh * zw, kraw, fk), hy, pe + 0.0007,
                                       w=0.028 * eh, anchor=(0.5, 0.5), shadow=None)
                            if 0 <= fk < 0.12:
                                st.put(J.listwa(30, 30, (255, 150, 60)), hx + 0.06 * eh * zw, hy, pe + 0.0007, w=0.05 * eh, anchor=(0.5, 0.5),
                                       shadow=None)
        tab(w, t, "AGAIN?!", ex + ew * 0.5, ey + eh * 0.2, GRA_ROW + 0.6, 1.6)
    widownia(st, t)
    for n, x in enumerate((300, 560, 820, 1020)):
        st.put(J.rek("pad"), x, 600, P.rampa - 0.005, h=46, anchor=(0.5, 0.5), rot=8 * math.sin(t * 8 + n), shadow=None)
    koniec(st, w, t)


KON_TECZKA, KON_KARTA, KON_SWIATLA, KON_DO_TECZKI = 5.0, 7.27, 8.33, 9.5  # s na osi Studio (markery 23.11)
KON_CZAPKI = 5.6    # s akcji: „…nine dead lawmen…” — dziewięć czapek policyjnych zjeżdża na nitkach
KON_KIESZEN = 2.3   # s akcji: „two broke kids” — z pustej kieszeni Clyde'a wylatuje ćma (ta sama co w West Dallas)
KON_STEMPEL = 11.5  # s akcji: „…brought them down” — na teczce pieczątka CASE CLOSED
KON_KURTYNA = 11.7  # s akcji: kurtyna zaczyna się zasuwać (zasunięta, kiedy kończy się kwestia)


def s_koniec(st, w, t, T):
    """Papierowa Bonnie z cygarem i Clyde stoją przy aucie, potem kładą się płasko w stronę gazety; zjeżdża duża teczka Hamera,
    nad nią powoli karta z ich aktami, która zsuwa się na linkach do teczki; na teczce pieczątka; kurtyna się zasuwa.
    Markery reżysera 23.11: „w tym momencie wjeżdża ta duża teczka z dużym napisem Bonnie & Clyde” (5,37 s), „większa teczka”
    (6,47 s; obrys ekranu x 459–759, y 290–441), „powoli zjeżdża karta z ich aktami” (7,27 s; x 583–733, y 189–294), „zamrugaj
    światłami” (8,33 s), „i te akta zjeżdżają w dół za nią do karty” (9,50 s). Uwaga 24.11: „napraw to ściąganie w dół na linkach,
    to co napisałem w markerach” — karta schodzi na linkach za teczkę i zostaje w niej (linki dalej ją trzymają), teczka ma
    rozmiar z obrysu; czat 24.11: „118/119 jest statyczne, jakby coś się zepsuło, bo nikt się nie rusza” — w każdej części kwestii
    coś się dzieje (ćma z pustej kieszeni, dziewięć czapek, mruganie, pieczątka)."""
    def _kam(obj, tt):
        kam(obj, tt, 112, 640, lerp(380, 400, ease(tt / T)), lerp(1.0, 0.92, ease(tt / T)), 0.8, drift=0.4)

    class _K:
        pass

    def ekran_w(tt, sx, sy, p):  # punkt ekranu z chwili markera → stałe miejsce w kadrze wzorcowym
        km = _K()
        km.T = T
        _kam(km, tt)
        return ekran_do_swiata(km.cam, sx, sy, p)

    _kam(st, t)
    teatr_gazet(st, t, w)
    auto(st, t, 700, 290)
    swiatla(st, 700, 290, przod=miga(t, rs("koniec", KON_SWIATLA), 3))
    kl = ease(pr(t, 3.0, 2.5))
    lalka(st, t, "bonnie_cygaro", 470, 320, flip=1, lean=-85 * kl, sink=0.4 * kl, rece=(70 * (1 - kl), 10), trzyma=REV() if kl < 0.5 else None)
    lalka(st, t, "clyde", 980, 350, flip=-1, lean=85 * kl, sink=0.4 * kl, rece=(35 * (1 - kl), 20), trzyma=KARABIN() if kl < 0.5 else None)
    fc = pr(t, KON_KIESZEN, 2.2)  # ćma z pustej kieszeni Clyde'a (W1 „pusta kasa” — klamra z West Dallas)
    if 0 < fc < 1:
        kx_, ky_ = punkt("clyde", 980, 350, 170, 430, flip=-1)
        st.put(J.rek("cma"), kx_ - 160 * fc + 22 * math.sin(fc * 17), ky_ - 330 * fc, P.rekwizyty, h=40, anchor=(0.5, 0.5),
               sx=0.3 + 0.7 * abs(math.sin(t * 22)), rot=10 * math.sin(t * 7), shadow=(2, 3, 3, 0.3))
    for n in range(9):  # „nine dead lawmen”: dziewięć czapek policyjnych w rzędzie, po kolei na nitkach
        cx_ = 170 + 117.5 * n
        k_ = pr(t, KON_CZAPKI + 0.13 * n, 0.8)
        if k_ > 0:
            J.hang(st, J.rek("czapka_policyjna"), cx_, 112 + 16 * (n % 2), P.rekwizyty + 0.01, k_, t, 790 + n, h=58, drop=340, sway=0.8,
                   shadow=(3, 4, 5, 0.35))
    r = lambda s_: rs("koniec", s_)
    pt = P.rekwizyty
    (x1, y1), (x2, y2) = ekran_w(r(6.47), 459, 290, pt), ekran_w(r(6.47), 759, 441, pt)
    J.hang(st, J.teczka_akt(), (x1 + x2) / 2, y1, pt, pr(t, r(KON_TECZKA), 1.0), t, 777, h=y2 - y1, drop=460, sway=0.4, shadow=(5, 7, 8, 0.4))
    kk = pr(t, r(KON_KARTA), 1.8)  # powoli
    if kk > 0:
        (k1, l1), (k2, l2) = ekran_w(r(7.27), 583, 189, pt - 0.002), ekran_w(r(7.27), 733, 294, pt - 0.002)
        # na koniec karta schodzi na linkach za teczkę: jej górna krawędź chowa się tuż pod górną krawędzią teczki
        wpada = ease(pr(t, r(KON_DO_TECZKI), 1.0))
        dol = (y1 + (y2 - y1) * 0.16) - l1
        J.hang(st, J.karta_akt(), (k1 + k2) / 2, l1 + dol * wpada, pt - 0.002, kk, t, 778, h=l2 - l1, drop=380, sway=0.3 * (1 - wpada),
               shadow=(4, 6, 6, 0.35), strings=(0.2, 0.8))
    ks = pr(t, KON_STEMPEL, 0.25)
    if ks > 0:
        st.put(J.tag("CASE CLOSED", 34), (x1 + x2) / 2 + 40, y1 + (y2 - y1) * 0.62, pt + 0.003, h=(y2 - y1) * 0.26 * back(ks, 2.0),
               anchor=(0.5, 0.5), rot=-11, tint=(1.0, 0.55, 0.5), shadow=(3, 4, 4, 0.4))
    R = sys.modules.get("render") or sys.modules.get("__main__")
    if R is not None and hasattr(R, "kurtyna"):
        R.kurtyna(st, ease(pr(t, KON_KURTYNA, T - KON_KURTYNA - 0.4)))
    koniec(st, w, t)


DZ_WEJSCIE, DZ_UKLON, DZ_KWIATY, DZ_SERCA = 0.4, 1.6, 2.6, 3.7  # s akcji (24.11)


def s_dzieki(st, w, t, T):
    """Przed kurtyną wychodzą wszystkie lalki filmu i kłaniają się po kolei; Hamer zdejmuje kapelusz, Bonnie macha."""
    kam(st, t, 113, 640, 400, 1.0, 0.8, drift=0.4)
    for strona in (-1, 1):
        # tło przyciemnione: kurtyna, która na końcu zasuwa się i zacina (gag 30), musi odcinać się od tła
        swiat.dekoracja(st, Z0.kurtyna(strona), CX, -60, P.drzewa, h=1000, anchor=(1.0 if strona < 0 else 0.0, 0.0), shadow=None,
                        tint=(0.55, 0.42, 0.42))
    swiat.dekoracja(st, J.glow(), CX, 700, P.drzewa + 0.01, w=1800, anchor=(0.5, 0.5), mode="add", alpha=0.25, shadow=None, tint=(1.0, 0.85, 0.6))
    # czat reżysera 24.11: „118/119 jest statyczne, jakby coś się zepsuło, bo nikt się nie rusza”, uwaga w ujęciu: „napraw to ujęcie,
    # bo nic się nie dzieje” — lalki wchodzą z obu stron na swoje miejsca, kłaniają się falą (zdejmują nakrycie głowy ręką
    # i trzymają je przy boku — uwaga 23.11), z widowni lecą kwiaty i lądują im pod nogami, na „support me” nad każdym
    # unosi się serce, Bonnie macha beretem; potem gag z kurtyną
    for n, key in enumerate(("buck", "blanche", "wd", "bonnie", "clyde", "hamer", "darby", "boyd")):
        xc = 120 + 148 * n
        lewa = n < 4
        te = DZ_WEJSCIE + 0.14 * (3 - n if lewa else n - 4)  # najpierw środek, potem brzegi
        wj = ease(pr(t, te, 1.0))
        x = lerp(-140 if lewa else 1420, xc, wj)
        t0 = DZ_UKLON + 0.25 * n
        uklon = ease(pr(t, t0, 0.35)) * (1 - ease(pr(t, t0 + 0.7, 0.45)))
        fl = (1 if lewa else -1) if wj < 1 else (1 if xc < CX else -1)
        h = 330 if key in ("clyde", "hamer", "buck") else 300
        key = "darby_czapka" if key == "darby" else key  # marker 23.11 (1,27 s): „jej narysuj czapkę z daszkiem” (Darby)
        lean = 22 * fl * uklon
        u = kapelusz_reka(key, x, h, t, t0 - 0.55, flip=fl, lean=lean, wroc=False) if J.figura(key).kapelusz and wj >= 1 else None
        rk, sk, kap, krot = u if u else (20 + 25 * (0 < wj < 1) * abs(math.sin(t * 8)), 1.0, False, 0.0)
        mach = key == "bonnie" and t0 + 1.2 < t < 6.9
        szarp = key in ("bonnie", "clyde") and 7.0 < t < 8.0
        if szarp:
            rk, sk = 160, 1.0
        elif mach:
            rk, sk = 130 + 30 * math.sin(t * 8), 1.0
        lalka(st, t, key, x, h, flip=fl, lean=lean + (8 * math.sin(t * 14) * szarp), rece=(rk, 10), skrot=(sk, 1.0), hop=6 * (0 < wj < 1),
              kapelusz_reka=kap, kapelusz_rot=krot, seed=sum(map(ord, "darby")) if key == "darby_czapka" else None)
        # kwiat z widowni: leci łukiem spod rampy i ląduje przed lalką
        fk = pr(t, DZ_KWIATY + 0.17 * ((n * 5) % 8), 0.7)
        if fk > 0:
            kx0, ky0 = xc + (60 if lewa else -60), 860
            st.put(J.rek("kwiatek"), lerp(kx0, xc + 22, fk), lerp(ky0, 652, fk) - 220 * math.sin(math.pi * fk), P.lalki + 0.04,
                   h=60, anchor=(0.5, 0.5), rot=lerp(0, 600 + 30 * n, fk) if fk < 1 else -80 + 10 * n % 30, shadow=(2, 3, 3, 0.3))
        fs = pr(t, DZ_SERCA + 0.12 * n, 1.6)  # „support me”: serce unosi się nad każdym i gaśnie
        if 0 < fs < 1:
            st.put(J.serce(), xc + 10 * math.sin(t * 3 + n), 260 - 150 * fs, P.rekwizyty, h=34 * back(min(1.0, fs * 3), 1.6),
                   anchor=(0.5, 0.5), alpha=1 - max(0.0, fs - 0.7) / 0.3, shadow=(2, 3, 3, 0.3))
    # gag 30 (GAGI.md, W3 „nitka teatru” — puenta): kurtyna zasuwa się i zacina w połowie; Bonnie i Clyde szarpią ją razem,
    # kurtyna zjeżdża z łoskotem i przykrywa wszystkich; zza kulis macha ręka maszynisty
    R = sys.modules.get("render") or sys.modules.get("__main__")
    if R is not None and hasattr(R, "kurtyna"):
        kz = 0.5 * ease(pr(t, 6.4, 0.6)) + 0.03 * math.sin(t * 30) * (7.0 < t < 8.0) + 0.5 * back(pr(t, 8.0, 0.35), 1.4)
        R.kurtyna(st, min(1.05, kz))
    rm = ease(pr(t, 8.4, 0.4))
    if rm > 0:
        lalka(st, t, "przechodzien", lerp(-160, 190, rm), 330, p=0.985, flip=1, lean=-18 * rm, rece=(150 + 20 * math.sin(t * 9), 20))
    koniec(st, w, t)
