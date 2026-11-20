"""Ujęcia aktów 1–4: Kropla z włóczni, Słońce w jaskini, Miecz w ogonie węża, Na wschód.

Każda funkcja `s_<klucz>(st, w, t, T)` rysuje jedno ujęcie rozpiski: zmienia stan świata w czasie (wydarzenie ujęcia),
ustawia kamerę i woła scenografię. Czasy liczone od początku ujęcia.
"""
import math
import random

import zestaw_jp as J
from scena import piorun, plomien, poklad_lodzi  # noqa: E402
from papier import CX, CY, back, clamp, ease, ease_out, noise, settle
from scena import (FALE, P, SAKAKI, SKALA, STOPY, Z0, bk, choragiewki, czubek_luku, gora_wyspy, grzebien_we_wlosach, iks, kam, kraj,  # noqa: F401
                   kulisy, lalka, lerp, lodz, morze, niebo, niebo_papier, pochodnia, podpis, pr, punkt, rampa, slonce, strzala_w_ramieniu,
                   swiatlo, yomi, ziemia, zawieszki, zjazd)


def nad(h, y=STOPY):
    """Górna krawędź tabliczki z imieniem nad głową lalki o wysokości h stojącej stopami w y."""
    return y - h - 74

LUK = lambda h: (J.luk(), h * 1.12, J.LUK_UCHWYT, 0.0, False)  # łuk w przedniej dłoni (pionowo)
WLOCZNIA = lambda h, rot=0.0: (J.wlocznia_bogow(), h * 1.7, (0.5, 0.6), rot, False)
MIECZ = lambda h, blask=False: (J.miecz_jp(blask), h * 0.62, (0.5, 0.93), 180.0, True)  # ostrze idzie przedłużeniem ręki


# ---------- akt 1 · Kropla z włóczni ----------

def s_teatr(st, w, t, T):
    """Front teatru; lampa w skrzyni, słońce na nitce, kraj wysuwa się od dołu; wjazd do środka."""
    w.build = t - 1.5
    w.sun = pr(t, 1.2, 1.3)
    k = ease(pr(t, 1.6, T - 1.9))
    m = math.exp(lerp(math.log(0.6), math.log(1.0), k))
    kam(st, t, 0, 640, lerp(322, 360, k), m, 1.0, lens=m ** 0.55, truck=1.0, drift=0.4)
    st.dof = 0.0
    kraj(st, t, w, pola=1.0)
    on = pr(t, 0.7, 0.5) * (0.75 + 0.25 * (math.sin(t * 43) > -0.6 or t > 1.25))
    bracia_na_polanie(st, t)
    st.put(J.black(), CX, CY, 0.992, w=1300, anchor=(0.5, 0.5), alpha=1 - on, shadow=None, blur=0)
    J.theatre_put(st, 0.55 + 0.45 * pr(t, 0.2, 0.8))
    swiatlo(st, w, t)


# Otwarcie filmu (reżyser 18.11.2026): w teatrze na polanie stoi ludek z ujęcia strzały (Itsuse), w następnym ujęciu kamera
# najeżdża na niego. Bracia stoją tak, żeby przy najeździe zostać poza kadrem zbliżenia (zbliżenie „hak_rana”: x 300–900).
BRACIA = (("itsuse", 600, 280, 2.0, None), ("iwarebiko", 1000, 290, 2.2, "luk"), ("brat2", 185, 270, 2.4, None),
          ("brat3", 1115, 265, 2.6, None))  # w krótkiej kurtynie tytułu (2,5 s od 1,4 s oryginału) wszyscy zdążą wyjść


def bracia_na_polanie(st, t, wstaja=True):
    """Czterech braci na polanie: wysuwają się zza rampy po kolei (wstaja=False: już stoją), patrzą na wschód."""
    for key, x, h, t0, rzecz in BRACIA:
        k = ease(pr(t, t0, 0.7)) if wstaja else 1.0
        if k <= 0:
            continue
        lalka(st, t, key, x, h, k, flip=1, rece=(8, 0), trzyma=LUK(h) if rzecz == "luk" else None)


def s_hak_najazd(st, w, t, T):
    """Kamera najeżdża z całej sceny na Iwarebiko i stojącego obok najstarszego brata (przegląd 18.11.2026: lektor mówi
    o przyszłym cesarzu, więc widz ma go zobaczyć, a nie wziąć brata za cesarza). Podpis „Iwarebiko, przyszły cesarz” zjeżdża
    przy imieniu (ok. 1,7 s). Księga D14 (20.11.2026): brat w haku nie ma imienia ani podpisu — „Itsuse” pada w akcie IV."""
    k = ease(t / T)
    m = math.exp(lerp(math.log(1.0), math.log(1.55), k))
    kam(st, t, 36, lerp(640, 800, k), lerp(360, 455, k), m, lerp(1.0, 0.8, k), lens=lerp(1.0, 1.5, k), truck=0.8, drift=0.3)
    st.dof = lerp(0.3, 1.4, k)
    kraj(st, t, w, pola=1.0)
    bracia_na_polanie(st, t, wstaja=False)
    podpis(w, t, "Iwarebiko, przyszły cesarz", 1000, nad(290), 1.6, 0.42 * T)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


# Teatr cieni między strzałą a burzą (reżyser 18.11.2026: „ujęcie, jak jest ziomek za kurtyną, ale dokładamy, że strzela
# ktoś strzałą w niego”; księga D14: trafienie widać raz, w „hak_rana”). Reżyser 20.11.2026, uwaga do ujęcia 14: „on ma leżeć
# z tą strzałą na ziemi, a ten gość ma próbować ją mu wyciągnąć” — cień najstarszego brata leży na ziemi ze strzałą w ramieniu,
# z lewej wchodzi cień Iwarebiko (łucznik to wróg, więc strzałę ciągnie brat), pochyla się, chwyta drzewce i szarpie trzy
# razy: strzała nie puszcza, ciało podrywa się przy każdym szarpnięciu; ręka leżącego opada (śmierć), Iwarebiko puszcza
# i zwiesza głowę. Te same czasy w efekty.DODATKI.
CIEN_CHWYT = 0.9  # dłoń Iwarebiko na drzewcu
CIEN_SZARP = (1.15, 1.65, 2.15)  # szarpnięcia: ciągnie 0,15 s, puszcza 0,2 s
CIEN_SMIERC = 3.0  # ręka leżącego opada
CIEN_PUSZCZA = 3.3  # Iwarebiko puszcza strzałę i zwiesza głowę


class _BezRysunku:
    """Scena, która niczego nie rysuje: lalka() liczy na niej tylko położenie dłoni."""
    def put(self, *a, **k):
        pass


def kat_do(t, key, x, h, cel, **kw):
    """Kąt przedniej ręki, przy którym dłoń lalki jest najbliżej punktu cel (wytyczne 1.28: dłoń na uchwycie)."""
    def odl(a):
        d = lalka(_BezRysunku(), t, key, x, h, rece=(a, 0.0), **kw)
        return (d[0] - cel[0]) ** 2 + (d[1] - cel[1]) ** 2
    best = min(range(-80, 200, 4), key=odl)
    return min((best + d / 4 for d in range(-8, 9)), key=odl)


def s_hak_cien(st, w, t, T):
    """Parawan podświetlony od tyłu: cień brata leży ze strzałą w ramieniu, cień Iwarebiko próbuje ją wyciągnąć, brat umiera."""
    kam(st, t, 2, 640, 458, lerp(1.62, 1.7, ease(t / T)), 0.84, lens=1.42)
    st.dof = 1.6
    kraj(st, t, w, pola=1.0, kul=False)
    pw = 600
    ph = pw * 480 / 760
    y0, p0 = 704, 0.83
    cien = dict(tint=(0.10, 0.07, 0.06), shadow=None, blur=1.6, p=p0 + 0.001)
    st.put(J.glow(), 640, y0 - ph * 0.5, p0 - 0.004, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.35, shadow=None, tint=(1.0, 0.8, 0.55))
    st.put(J.parawan(), 640, y0, p0, w=pw, anchor=(0.5, 1.0), shadow=(6, 8, 10, 0.45))
    # szarpnięcia: 0..1 ciągnięcie, potem powrót (strzała nie puszcza)
    sz = max(math.sin(math.pi * min(1.0, pr(t, a, 0.15) * 0.5 + pr(t, a + 0.15, 0.2) * 0.5)) for a in CIEN_SZARP)
    # brat leży głową w lewo (stopy w lx), podnosi się lekko przy każdym szarpnięciu; ręka leżącego opada w chwili śmierci
    lx, hh, ly = 800, 250, y0 - 26 - 38
    lean_l = -90 + 8 * sz - 2 * ease(pr(t, CIEN_SMIERC, 0.5))
    reka_l = 28 * (1 - ease(pr(t, CIEN_SMIERC, 0.35))) + 5 * math.sin(t * 2.0) * (t < CIEN_SMIERC)  # nisko: nie myli się ze strzałą
    lalka(st, t, "itsuse", lx, hh, 1.0, y=ly, flip=1, lean=lean_l, rece=(reka_l, 0), alpha=0.82, **cien)
    ax, ay = punkt("itsuse", lx, hh, 196, 236, y=ly, rot=lean_l)  # grot w ramieniu
    kier = math.radians(62)  # strzała wbita z góry, lotka w stronę Iwarebiko
    dl = hh * 0.42
    wyj = 18 * sz  # strzała wysuwa się kawałek i wraca (nie puszcza)
    tip = (ax - math.cos(kier) * wyj, ay - math.sin(kier) * wyj)
    st.put(Z0.prop("strzala"), tip[0], tip[1], p0 + 0.002, w=dl, anchor=(0.95, 0.5), rot=62, tint=(0.10, 0.07, 0.06), alpha=0.8,
           shadow=None, blur=1.6)
    chwyt = (tip[0] - math.cos(kier) * dl * 0.62, tip[1] - math.sin(kier) * dl * 0.62)  # dłoń na drzewcu
    # Iwarebiko wchodzi z lewej, pochyla się nad bratem, przy szarpnięciach odchyla się do tyłu; po śmierci brata zwiesza głowę
    wej = ease(pr(t, 0.0, 0.6))
    ix = lerp(250, 470, wej)
    lean_i = 28 * ease(pr(t, 0.4, 0.5)) - 12 * sz + 10 * ease(pr(t, CIEN_PUSZCZA, 1.0))
    trzyma = pr(t, 0.55, CIEN_CHWYT - 0.55) * (1 - ease(pr(t, CIEN_PUSZCZA, 0.5)))  # 0..1: ręka w drodze do drzewca i z powrotem
    kw = dict(y=y0 - 26, flip=1, lean=lean_i)
    kat = lerp(8, kat_do(t, "iwarebiko", ix, 260, chwyt, **kw), ease(trzyma))
    lalka(st, t, "iwarebiko", ix, 260, 1.0, rece=(kat, -6), alpha=0.82 * wej, **kw, **cien)  # wchodzi bokiem, nie zza rampy
    st.put(J.parawan_rama(), 640, y0, p0 + 0.003, w=pw, anchor=(0.5, 1.0), shadow=(2, 3, 4, 0.4))
    swiatlo(st, w, t, dim=0.92)
    st.spot = (640, y0 - ph * 0.5, p0, 560, 0.5)


def s_luty(st, w, t, T):
    """Na wzgórzach wyskakują chorągiewki ze słońcem, zjeżdża zawieszka „11 lutego”."""
    w.zawieszki = [("11 lutego", 640, 300, pr(t, 1.0, 1.0))]
    kam(st, t, 1, 640, 380, lerp(1.0, 1.08, ease(t / T)), 0.62, truck=0.5)
    st.dof = 0.5
    kraj(st, t, w, pola=1.0)
    choragiewki(st, t, [pr(t, 1.8 + 0.45 * n, 0.5) for n in range(9)])
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_cien(st, w, t, T):
    """Parawan podświetlony od tyłu; rośnie na nim cień władcy z łukiem, przelatuje cień ptaka."""
    k = ease(t / T)
    kam(st, t, 2, 640, lerp(468, 458, k), lerp(1.5, 1.66, k), 0.84, lens=1.42)
    st.dof = 1.6
    kraj(st, t, w, pola=1.0, kul=False)
    kp = pr(t, 0.3, 1.0)
    pw = 600
    ph = pw * 480 / 760
    y0 = 704 + (1 - back(kp, 1.2)) * ph * 1.1
    p0 = 0.83
    st.put(J.glow(), 640, y0 - ph * 0.5, p0 - 0.004, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.35 * kp, shadow=None, tint=(1.0, 0.8, 0.55))
    st.put(J.parawan(), 640, y0, p0, w=pw, anchor=(0.5, 1.0), shadow=(6, 8, 10, 0.45))
    g = ease(pr(t, 1.4, 2.6))
    if g > 0:  # lampa za parawanem podjeżdża: cień rośnie i ostrzeje
        hh = lerp(150, 290, g)
        lalka(st, t, "iwarebiko", 600, hh, 1.0, y=y0 - 26, p=p0 + 0.001, rece=(25, 0), tint=(0.10, 0.07, 0.06), alpha=0.82 * min(1, g * 2),
              shadow=None, blur=lerp(6, 1.6, g), trzyma=(J.luk(), hh * 1.08, J.LUK_UCHWYT, 0.0, False))
    b = pr(t, 3.9, 2.6)
    if 0 < b < 1:
        st.put(J.zloty_ptak(int(t * 6) % 2), lerp(400, 880, b), lerp(470, 420, b) - 40 * math.sin(b * math.pi), p0 + 0.0015, w=110,
               anchor=(0.5, 0.5), tint=(0.1, 0.07, 0.06), alpha=0.8, shadow=None, blur=2.5)
    st.put(J.parawan_rama(), 640, y0, p0 + 0.003, w=pw, anchor=(0.5, 1.0), shadow=(2, 3, 4, 0.4))
    swiatlo(st, w, t, dim=0.92)
    st.spot = (640, y0 - ph * 0.5, p0, 560, 0.5)


MEDUZA_HOP = 4.9  # gag: fala podbija meduzę tuż po kwestii (ten sam czas w efektach; D14: kwestia krótsza)
# Reżyser 20.11.2026: „w ujęciu 18 jellyfish ma się powiększać na 70% kadru” — mała meduza wynurza się przy przedniej fali,
# a przy „young earth… drifted like a jellyfish” rośnie i unosi się, aż zajmie ok. 70% wysokości kadru (czubek kopuły ok. 0,14
# wysokości, macki chowają się za przednią falą); ten sam czas w efektach
MEDUZA_ROSNIE = (2.4, 2.3)  # start, czas wzrostu


def s_meduza(st, w, t, T):
    """Zmiana dekoracji: same fale pod chmurami; przy przedniej fali wynurza się papierowa meduza i rośnie do 70% kadru."""
    k = ease(t / T)
    kam(st, t, 3, 640, lerp(420, 400, k), lerp(1.0, 1.06, k), 0.66, truck=0.5)
    st.dof = 0.6
    morze(st, t, w, tint=(0.9, 0.94, 0.98))
    # zawieszka czasu najpierw: podpis „BLUB!” dopisuje się do listy (wcześniej przypisanie listy po gagu kasowało tabliczkę);
    # zawieszka odjeżdża, zanim meduza urośnie pod nią
    w.zawieszki = [("Wiek bogów", 640, 250, pr(t, 0.5, 1.0) * (1 - pr(t, 2.2, 0.8)))]  # 20.11.2026, „jeden początek”: zawieszka czasu zamiast kurtyny aktu
    km = pr(t, 1.0, 1.2)
    if km > 0:
        g = ease(pr(t, *MEDUZA_ROSNIE))
        hm = lerp(150, 585, g)  # wysokość arkusza meduzy (kopuła to górne 28%, kotwica na dole kopuły); 70% kadru zmierzone 20.11
        x = lerp(lerp(470, 560, pr(t, 1.0, MEDUZA_ROSNIE[0] - 1.0)), 640, g) + 10 * math.sin(t * 0.9)
        y = lerp(612, 346, g) + lerp(8, 12, g) * math.sin(t * 1.4)
        # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): grzbiet fali podbija meduzę — podskakuje, spłaszcza się przy lądowaniu, „BLUB!”
        hop = math.sin(math.pi * pr(t, MEDUZA_HOP, 0.7))
        squash = 0.18 * math.sin(math.pi * pr(t, MEDUZA_HOP + 0.7, 0.35))
        st.put(J.meduza(), x, y + (1 - ease(km)) * 40 - lerp(90, 60, g) * hop, 0.68, h=hm, anchor=(0.5, 0.35),
               sy=1 + 0.05 * math.sin(t * 3.2) - squash, sx=1 + squash, rot=4 * math.sin(t * 0.9) + lerp(20, 6, g) * hop, alpha=0.9 * ease(km),
               shadow=(3, 4, 6, 0.2))
        podpis(w, t, "BLUB!", 960, 150, MEDUZA_HOP + 0.4, 1.4)
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(0.95, 0.98, 1.02))


MOST = (640, 262, 900, 0.5)  # most niebios: x, góra arkusza, szerokość, plan


def most(st, t, k):
    x, y, wd, p = MOST
    J.hang(st, J.most_niebios(), x, y, p, k, t, 120, drop=560, sway=0.25, w=wd, strings=(0.14, 0.86))


def poklad(x):
    x0, y0, wd, _ = MOST
    return J.most_y(x, x0, y0 + 360 * wd / 1200, wd)


# D14 (20.11.2026): kwestia krótsza, więc ruch też — most spada od 0,2 s, bogowie zjeżdżają, kiedy lektor ich nazywa
# (ok. 1,3 i 2,0 s), tabliczki po wylądowaniu; te same czasy w efekty.ZDARZENIA
MOST_SPAD = (0.2, 1.2)  # most niebios zjeżdża na nitkach: start, czas
MOST_ZJAZD = {"izanami": 1.0, "izanagi": 1.6}  # początek zjazdu bogów po moście (zjazd trwa 1,4 s)
MOST_LAD = MOST_ZJAZD["izanagi"] + 1.4  # gag: Izanagi ląduje na moście z potknięciem (ten sam czas w efektach)


def s_most(st, w, t, T):
    """Z chmur zjeżdża tęczowy most; na nitkach schodzą na niego Izanagi z włócznią i Izanami — nad każdym, kiedy stanie,
    zjeżdża tabliczka z imieniem (wytyczne 1.15, przegląd 17.11)."""
    k = ease(t / T)
    kam(st, t, 4, 640, lerp(380, 370, k), lerp(1.2, 1.32, k), 0.5, truck=0.5)
    st.dof = 0.7
    morze(st, t, w, tint=(0.92, 0.95, 0.98))
    most(st, t, pr(t, *MOST_SPAD))
    for key, x0, x1, fl, rc, tr in (("izanami", 610, 560, 1.0, (10, 0), None),
                                    ("izanagi", 700, 670, -1.0, (55, 0), WLOCZNIA(150))):
        d = MOST_ZJAZD[key]
        kk = pr(t, d, 1.4)
        x = lerp(x0, x1, ease(pr(t, d + 1.6, 1.6)))
        # gag (GAGI.md, reżyser 20.11.2026: „wykonaj wszystkie poprawki w ujęciach”): Izanagi ląduje za mocno — chwieje się do przodu i do tyłu, macha ręką; Izanami ląduje lekko
        chw = math.sin(math.pi * 2 * pr(t, MOST_LAD, 0.7)) * (1 - pr(t, MOST_LAD, 0.9)) if key == "izanagi" else 0.0
        zjazd(st, t, key, x, poklad(x) + 6, 150, kk, p=MOST[3] + 0.005, flip=fl, rece=(rc[0], 140 * abs(chw)) if key == "izanagi" else rc,
              trzyma=tr, lean=18 * chw)
    # bogowie stoją na szczycie łuku, blisko górnej krawędzi kadru: tabliczki wiszą obok nich, na wysokości głów
    podpis(w, t, "Izanami", 455, poklad(560) - 130, MOST_ZJAZD["izanami"] + 1.5, 2.4)
    podpis(w, t, "OJEJ!", 800, poklad(690) - 150, MOST_LAD - 0.1, 0.8)
    podpis(w, t, "Izanagi", 815, poklad(690) - 130, MOST_LAD + 1.4, 2.4)
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(0.95, 0.98, 1.02))


def _kregi(st, t, x, y, p, t0, n=3):
    """Kręgi na wodzie wokół drzewca: rozchodzące się elipsy."""
    for j in range(n):
        f = ((t - t0) * 0.6 + j / n) % 1.0 if t > t0 else 0.0
        if f <= 0:
            continue
        rx, ry = 20 + 110 * f, 5 + 24 * f
        pts = [(x + rx * math.cos(a), y + ry * math.sin(a)) for a in [i * math.pi / 18 for i in range(37)]]
        st.line(pts, p, width=2.2, color=(236, 242, 240), alpha=0.7 * (1 - f), z=0.2)


def s_wlocznia(st, w, t, T):
    """Izanagi pochyla się z mostu i miesza włócznią w falach; wokół drzewca rozchodzą się kręgi."""
    kam(st, t, 5, lerp(660, 690, ease(t / T)), 372, 1.45, 0.5, lens=1.35)
    st.dof = 1.0
    morze(st, t, w, tint=(0.92, 0.95, 0.98))
    most(st, t, 1.0)
    lean = 16 * ease(pr(t, 0.4, 1.0))
    stir = 9 * math.sin(t * 2.4) * pr(t, 1.6, 0.8)
    lalka(st, t, "izanami", 560, 150, y=poklad(560) + 6, p=MOST[3] + 0.005, rece=(30 * ease(pr(t, 2.0, 1.0)), 0), lean=4 * ease(pr(t, 2.0, 1.0)))
    otrze = ease(pr(t, T - 1.8, 0.4)) * (1 - ease(pr(t, T - 0.6, 0.4)))  # ociera czoło wolną ręką
    lalka(st, t, "izanagi", 670, 150, y=poklad(670) + 6, p=MOST[3] + 0.006, flip=1.0, lean=lean - 10 * otrze,
          rece=(60 + 8 * math.sin(t * 2.4), 160 * otrze),
          trzyma=(J.wlocznia_bogow(), 300, (0.5, 0.86), 180 - 22 + stir, False))
    _kregi(st, t, 760, 520, 0.47, 1.4)
    podpis(w, t, "UFF…", 800, poklad(670) - 120, T - 1.7, 1.5)  # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): Izanagi zmęczony mieszaniem
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(0.95, 0.98, 1.02))


def s_kropla(st, w, t, T):
    """Grot włóczni unosi się nad falę, skapuje z niego kropla; tam, gdzie spadła, wyrasta mała wysepka."""
    kam(st, t, 6, 690, 470, 2.4, 0.56, lens=2.1)
    st.dof = 1.8
    morze(st, t, w, tint=(0.92, 0.95, 0.98), kul=False)
    up = ease(pr(t, 0.2, 1.4))
    tip = (700, lerp(560, 420, up) + 3 * math.sin(t * 1.7))
    st.put(J.wlocznia_bogow(), tip[0], tip[1], 0.53, h=420, anchor=(0.5, 0.0), rot=180 + 6 * math.sin(t * 0.8), shadow=(4, 6, 8, 0.3))
    d = pr(t, 1.8, 0.75)
    if 0 < d < 1:  # kropla odrywa się od grotu i spada
        st.put(J.kropla(), tip[0], tip[1] + 8 + 120 * d * d, 0.531, h=lerp(10, 22, min(1.0, d * 3)), anchor=(0.5, 0.2), shadow=(2, 3, 3, 0.3))
    sp = pr(t, 2.55, 0.6)
    if 0 < sp < 1:  # rozprysk
        for j in range(6):
            a = math.pi * (0.15 + 0.7 * j / 5)
            st.put(J.kropla(), 700 + math.cos(a) * 60 * sp, 532 - math.sin(a) * 50 * sp + 60 * sp * sp, 0.531, h=10, alpha=1 - sp)
    _kregi(st, t, 700, 534, 0.47, 2.55, n=2)
    Z0.rise(st, J.wyspa(2), 700, FALE[2][1] + 26, FALE[2][0] - 0.012, pr(t, 2.8, 1.6), t, 72, w=230, wob=0.0, lift=140)
    podpis(w, t, "TA-DA!", 700, 404, 4.4, 2.0)  # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): pierwsza wyspa gotowa
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(0.95, 0.98, 1.02))


WYSPY_JP = [(640, 2, 330, 9), (210, 1, 300, 0), (420, 2, 380, 1), (880, 1, 280, 2), (1080, 2, 420, 3), (1220, 1, 300, 4), (330, 3, 560, 5),
            (980, 3, 600, 6), (1300, 3, 380, 7)]  # x, pasmo za wyspą, szerokość, odmiana (9 = Onogoro bez sosen)


def wyspy_lista(ks):
    return [(x, b, wd, v if v < 9 else 1, k) for (x, b, wd, v), k in zip(WYSPY_JP, ks)]


def s_wyspy(st, w, t, T):
    """Spomiędzy fal wysuwają się po kolei wyspy z sosnami; bogowie stoją na pierwszej."""
    k = ease(t / T)
    m = lerp(1.16, 1.0, k)
    kam(st, t, 7, 660, lerp(410, 380, k), m, 0.6, truck=0.6)
    st.dof = 0.6
    ks = [1.0] + [pr(t, 0.7 + 0.55 * n, 0.9) for n in range(len(WYSPY_JP) - 1)]
    morze(st, t, w, wyspy=[], tint=(0.95, 0.97, 1.0))
    for (x, b, wd, v), kk in zip(WYSPY_JP, ks):
        spr = J.wyspa_gola(0) if v == 9 else J.wyspa(v)
        Z0.rise(st, spr, x, FALE[b][1] + 26, FALE[b][0] - 0.012, kk, t, 70 + v, w=wd, wob=0.0, lift=wd * 0.5, haze=0.35 * (3 - b) / 3,
                shadow=(5, 6, 8, 0.28))
    on = J.wyspa_gola(0)
    for key, x, fl in (("izanami", 615, 1.0), ("izanagi", 665, -1.0)):
        y = gora_wyspy(on, x, 640, FALE[2][1] + 26, 330) + 4
        lalka(st, t, key, x, 70, 1.0, y=y, p=FALE[2][0] - 0.008, flip=fl, rece=(20, 0))
    swiatlo(st, w, t)


# ---------- akt 2 · Słońce w jaskini ----------

ONO = (640, FALE[3][1] + 200, 1100, FALE[3][0] - 0.012)  # Onogoro z bliska: x, dół, szerokość, plan


def onogoro(st, t, w):
    x, yb, wd, p = ONO
    st.put(J.wyspa_gola(0), x, yb, p, w=wd)


def na_onogoro(x):
    x0, yb, wd, _ = ONO
    return gora_wyspy(J.wyspa_gola(0), x, x0, yb, wd) + 6


OGIEN_SMIERC = 2.6  # chwila śmierci Izanami: X na oczach; ten sam czas w efekty.ZDARZENIA (jęk z nagrania)


def s_ogien(st, w, t, T):
    """Przy Izanami wybuchają płomienie z bibuły; bogini drży w ogniu, przechyla się, dostaje X na oczach (śmierć widać,
    wytyczne 1.11 i 1.20, przegląd 17.11) i opada pod rampę; Izanagi wyciąga do niej rękę."""
    kam(st, t, 8, 640, 440, lerp(1.4, 1.5, ease(t / T)), 0.74, lens=1.35)
    st.dof = 1.4
    morze(st, t, w, tint=(0.95, 0.96, 0.98), slonce_k=0.0)
    onogoro(st, t, w)
    p = ONO[3] + 0.004
    fire = pr(t, 0.9, 0.9) * (1 - 0.6 * pr(t, T - 2.5, 2.0))
    if fire > 0:
        ft = math.floor(t * 12) / 12
        for n in range(8):
            r = random.Random(500 + n)
            hh = 150 * fire * (0.6 + 0.4 * noise(ft, 600 + n, 9)) * r.uniform(0.6, 1.0)
            x = 520 + r.uniform(-70, 70)
            st.put(J.flame(n), x, na_onogoro(x) + 6, p + 0.002 + n * 0.0003, h=hh, rot=9 * noise(ft, 700 + n, 7), shadow=None,
                   tint=(1.15, 1.1, 1.0))
        st.put(J.glow(), 520, na_onogoro(520) - 60, p + 0.004, w=520, anchor=(0.5, 0.5), mode="add", alpha=0.32 * fire, shadow=None,
               tint=(1.0, 0.55, 0.25))
    lalka(st, t, "izanami", 520, 240, y=na_onogoro(520), p=p, lean=-14 * ease(pr(t, 1.6, 1.2)) - 3 * math.sin(t * 9) * pr(t, 1.6, 0.4) *
          (1 - pr(t, 2.6, 0.3)), sink=pr(t, OGIEN_SMIERC + 0.6, 2.6), oczy_x=pr(t, OGIEN_SMIERC, 0.35))
    reach = ease(pr(t, 2.2, 1.0))
    lalka(st, t, "izanagi", 760, 240, y=na_onogoro(760), p=p + 0.001, flip=-1, lean=-9 * reach, rece=(95 * reach, 10))
    swiatlo(st, w, t, extra=(1.04, 0.97, 0.92))


def s_yomi(st, w, t, T):
    """Ciemność: Izanagi z pochodnią schodzi w głąb, z mroku wyłania się sina Izanami, Izanagi ucieka, głaz zamyka przejście."""
    w.noc = 1.0
    back_ = ease(pr(t, 5.6, 2.2))
    x = lerp(240, 560, ease(pr(t, 0.6, 3.6))) - 260 * back_
    fl = 1.0 if t < 5.5 else math.cos(math.pi * ease(pr(t, 5.4, 0.4)))
    kam(st, t, 9, lerp(480, 560, ease(t / T)), 470, 1.25, 0.8)
    st.dof = 0.9
    yomi(st, t, w, glaz_k=pr(t, T - 3.2, 1.6), swiatlo_x=x + 40)
    z = ease(pr(t, 3.4, 1.8)) * (1 - ease(pr(t, T - 2.2, 1.2)))
    if z > 0:
        lalka(st, t, "izanami", 880, 270, y=STOPY, alpha=z, tint=(0.55, 0.66, 0.58), flip=-1, rece=(70 * z, 0), lean=-4)
    hand = lalka(st, t, "izanagi", x, 270, y=STOPY, flip=fl, rece=(55, 0), lean=-8 * back_ * fl, hop=7 if back_ > 0 else 3)
    if hand:
        pochodnia(st, t, hand[0], hand[1] + 34, P.lalki + 0.016, h=120, seed=1)
    swiatlo(st, w, t, extra=(1.0, 0.9, 0.85), dim=0.9)


def s_rzeka(st, w, t, T):
    """Izanagi pochyla się nad rzeką; z wody wynurzają się słońce, księżyc i chmura, a za nimi troje bogów — każde
    z tabliczką z imieniem i rolą (wytyczne 1.15)."""
    k = ease(t / T)
    kam(st, t, 10, lerp(660, 700, k), 470, lerp(1.2, 1.32, k), 0.72, truck=0.6)
    st.dof = 1.0
    kraj(st, t, w, rzeka=1.0, slonce_k=pr(t, 4.2, 1.6))
    lalka(st, t, "izanagi", 300, 290, lean=14 * ease(pr(t, 0.3, 1.0)), rece=(40, 0))
    for n, (kind, x, d, god) in enumerate((("slonce", 610, 1.6, "amaterasu"), ("ksiezyc", 830, 5.2, "tsukuyomi"), ("chmura", 1050, 8.4, "susanoo"))):
        kd = pr(t, d, 1.1)
        if kd > 0:
            y0 = ziemia("blisko", x) + 40
            yy = y0 - 120 * back(kd, 1.4) - 60 * ease(pr(t, d + 1.4, 2.0)) + 6 * math.sin(t * 1.3 + n)
            st.put(J.krazek(kind), x, yy, P.droga + 0.008, h=96, anchor=(0.5, 0.5), rot=4 * noise(t, 40 + n, 0.4))
            if kind == "slonce":
                st.put(J.glow(), x, yy, P.droga + 0.009, w=320, anchor=(0.5, 0.5), mode="add", alpha=0.28 * kd, shadow=None)
        lalka(st, t, god, x + 20, 280, pr(t, d + 1.0, 1.1), flip=-1 if n < 2 else 1, rece=(20, 0))
        podpis(w, t, ("Amaterasu, bogini słońca", "bóg księżyca", "Susanoo, bóg burzy")[n], x + 20 - 90 * (n == 2), nad(280) - 6,
               d + 1.4, 2.4)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_susanoo(st, w, t, T):
    """Niebiańska równina: Susanoo przelatuje w wirze wiatru, poletka fruwają, dach tkalni pęka i spada."""
    f = pr(t, 0.9, T - 1.8)
    sx = lerp(-160, 1460, f)
    kam(st, t, 11, lerp(520, 760, f), 430, 1.08, 0.7, shake=4.0 * (0.2 < f < 0.95))
    st.dof = 0.7
    poles = [1.0 if sx < 120 + n * 120 else 0.0 for n in range(5)]
    roof_t = 0.9 + (300 + 160) / 1620 * (T - 1.8)  # chwila, w której wir mija tkalnię
    niebo(st, t, w, pola=poles, dach=1.0 if t < roof_t else 0.0)
    for n in range(5):  # oderwane poletka koziołkują w górę
        x0 = 120 + n * 120
        tn = 0.9 + (x0 + 160) / 1620 * (T - 1.8)
        if t > tn:
            d = t - tn
            st.put(J.poletko(0), x0 + 260 * d, 600 - 240 * d + 60 * d * d, P.gory + 0.04, w=140, rot=200 * d * (1 if n % 2 else -1),
                   alpha=clamp(2.2 - d), shadow=(3, 4, 4, 0.3))
    if t > roof_t:  # dach pęka na dwie połowy i spada za chmury
        d = t - roof_t
        for side in (-1, 1):
            st.put(J.dach(420), 300 + side * (30 + 70 * d), 520 - 120 * d + 260 * d * d, P.most + 0.014, w=270 * 0.55,
                   anchor=(0.5 + 0.5 * side, 1.0), rot=side * (25 * d + 40 * d * d), alpha=clamp(2.4 - d))
    y = 400 + 50 * math.sin(f * 7)
    st.put(J.wir(), sx, y - 120, P.lalki + 0.02, w=380, anchor=(0.5, 0.5), rot=-t * 420, shadow=None, alpha=0.8)
    lalka(st, t, "susanoo", sx, 280, y=y + 150, p=P.lalki + 0.021, lean=20 * math.sin(t * 3), flip=1, rece=(130, 40), hop=0)
    swiatlo(st, w, t, extra=(0.96, 0.96, 1.0))


def s_jaskinia(st, w, t, T):
    """Amaterasu wchodzi do jaskini, głaz zasuwa wejście, słońce odjeżdża w górę i scena gaśnie."""
    w.sun = 1 - pr(t, 4.6, 1.6)
    dark = ease(pr(t, 4.8, 1.8))
    w.noc = dark
    kam(st, t, 12, lerp(760, 820, ease(t / T)), 420, 1.08, 0.68, truck=0.5)
    st.dof = 0.6
    niebo(st, t, w, drzwi=pr(t, 3.4, 1.3), dach=0.0, pola=(0.0,) * 5)
    xa = lerp(720, 975, ease(pr(t, 0.4, 2.8)))
    lalka(st, t, "amaterasu", xa, 150, y=SKALA[1] - 20, p=P.wzgorza + 0.002, alpha=1 - pr(t, 2.9, 0.6), hop=3)
    swiatlo(st, w, t, dim=lerp(1.0, 0.42, dark))


def _bogowie(st, t, rozbaw=0.0, dim=1.0, t0=0.0, spada=None):
    """Rząd bogów przy rampie; rozbawieni kołyszą się ze śmiechu, każdy w swoim rytmie. spada = (numer boga, chwila):
    ten bóg ze śmiechu przewraca się do tyłu za rampę i po chwili wysuwa się z powrotem (gag przy tańcu Uzume)."""
    for n, (key, x, fl) in enumerate((("bog1", 170, 1), ("bog2", 290, 1), ("bog3", 1000, -1), ("bog4", 1110, -1), ("silacz", 1230, -1))):
        r = random.Random(60 + n)
        late = r.uniform(0, 1.2)
        laugh = rozbaw * ease(pr(t, t0 + late, 0.6))
        lean = laugh * (8 + 4 * r.random()) * math.sin(t * (5.5 + 2.5 * r.random()) + n)
        upadek = 0.0
        if spada and spada[0] == n:
            upadek = ease(pr(t, spada[1], 0.4)) * (1 - ease(pr(t, spada[1] + 1.4, 0.6)))
        lalka(st, t, key, x, 250 + 20 * r.random(), flip=fl, lean=lean - laugh * 5 * fl + 60 * upadek * fl, sink=0.75 * upadek,
              rece=(30 + 60 * laugh * abs(math.sin(t * 3 + n)) + 90 * upadek, 0), tint=(dim, dim * 0.95, dim * 0.9), seed=70 + n)


def s_ciemno(st, w, t, T):
    """Ciemność: zapalają się po kolei pochodnie, w ich świetle widać zarysy bogów."""
    w.sun, w.noc = 0.0, 1.0
    kam(st, t, 13, 700, 430, 1.04, 0.7)
    st.dof = 0.6
    niebo(st, t, w, drzwi=1.0, dach=0.0, pola=(0.0,) * 5)
    _bogowie(st, t, dim=0.55)
    for n, x in enumerate((230, 520, 830, 1140)):
        pochodnia(st, t, x, 720, P.rekwizyty + 0.002 * n, k=pr(t, 0.3 + 0.5 * n, 0.5), seed=n)
    swiatlo(st, w, t, dim=0.42)


def _sakaki(st, t, k=1.0, lustro=1.0, klejnoty=1.0, blysk=0.0):
    x, yb, hh = SAKAKI
    Z0.rise(st, J.sakaki(), x, yb, P.wzgorza + 0.02, k, t, 505, h=hh, wob=0.4)
    if k >= 1:
        J.hang(st, J.lustro(), x + 52, 420, P.wzgorza + 0.024, lustro, t, 506, drop=420, sway=1.2, w=74)
        J.hang(st, J.magatama_sznur(), x - 40, 450, P.wzgorza + 0.023, klejnoty, t, 507, drop=420, sway=1.0, w=120, strings=(0.1, 0.9))
        if blysk > 0:
            st.put(J.glow(), x + 52, 458, P.wzgorza + 0.025, w=420 * (0.6 + blysk), anchor=(0.5, 0.5), mode="add", alpha=0.55 * blysk,
                   shadow=None, tint=(1.0, 0.9, 0.6))


def _koguty(st, t, k=1.0, pieje=()):
    st.line([(470, 660), (470, 590)], 0.74, width=5, color=(90, 64, 44), alpha=1.0)
    st.line([(640, 660), (640, 590)], 0.74, width=5, color=(90, 64, 44), alpha=1.0)
    st.line([(450, 590), (660, 590)], 0.74, width=6, color=(110, 78, 52), alpha=1.0)
    for n, x in enumerate((510, 600)):
        kk = pr(k, n * 0.3, 0.7) if k < 1 else 1.0
        crow = max([0.0] + [settle((t - a) / 0.9, 1.5, 1.0) for a in pieje])
        if kk > 0:
            st.put(J.kogut(n), x, 592 + (1 - back(kk, 1.3)) * 60, 0.741, h=88, rot=-14 * crow * (1 if n else 0.8) + 1.0 * noise(t, 530 + n, 0.6),
                   sx=-1 if n else 1)


def s_koguty(st, w, t, T):
    """Przed jaskinią wyrasta sakaki; zjeżdżają na nie lustro i klejnoty, na grzędzie stają koguty i pieją."""
    w.sun, w.noc = 0.0, 1.0
    k = ease(t / T)
    kam(st, t, 14, lerp(640, 680, k), 480, lerp(1.35, 1.5, k), 0.72, lens=1.3)
    st.dof = 1.0
    niebo(st, t, w, drzwi=1.0, dach=0.0, pola=(0.0,) * 5)
    _sakaki(st, t, pr(t, 0.4, 1.0), lustro=pr(t, 2.0, 1.1), klejnoty=pr(t, 3.0, 1.1))
    _koguty(st, t, pr(t, 4.2, 1.0), pieje=(5.6, 7.2))
    for n, x in enumerate((230, 1140)):
        pochodnia(st, t, x, 720, P.rekwizyty, seed=n)
    podpis(w, t, "KUKURYKU!", 555, 452, 5.4, 1.6)  # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): koguty pieją w środku nocy
    zawieszki(st, t, w)
    swiatlo(st, w, t, dim=0.5)


UZUME_SPADA = 3.8  # gag: bóg ze śmiechu przewraca się za rampę (ten sam czas w efektach)
UZUME_SMIECH = 2.0  # bogowie wybuchają śmiechem; ten sam czas w efekty.ZDARZENIA (śmiech z nagrania, nie z szumu — 1.14)


def s_uzume(st, w, t, T):
    """Uzume tańczy na odwróconej kadzi; bogowie kołyszą się ze śmiechu, każdy w swoim rytmie, a nad nimi zjeżdżają
    tabliczki „HA HA!” (słownik znaków 1.20). Scena jaśniejsza niż reszta nocy, żeby taniec było widać (1.19;
    przegląd 17.11: ciemno i drobno)."""
    w.sun, w.noc = 0.0, 1.0
    kam(st, t, 15, 660, 480, lerp(1.14, 1.24, ease(t / T)), 0.8)
    st.dof = 0.9
    niebo(st, t, w, drzwi=1.0, dach=0.0, pola=(0.0,) * 5)
    _sakaki(st, t)
    _koguty(st, t)
    st.put(J.kadz(1), 640, 716, 0.83, h=130, sy=-1, anchor=(0.5, 0.0))
    dance = pr(t, 0.6, 0.6)
    beat = math.floor(t / 0.55)
    up = abs(math.sin(t * math.pi / 0.55)) * 16 * dance
    lalka(st, t, "uzume", 640, 240, y=596, p=0.835, lift=up, flip=1 if beat % 2 else -1, lean=6 * math.sin(t * 5.7) * dance,
          rece=(150 if beat % 2 else 40, 40 if beat % 2 else 150), trzyma=(J.galazka(), 70, (0.1, 0.85), 180, True))
    _bogowie(st, t, rozbaw=1.0, dim=0.9, t0=UZUME_SMIECH, spada=(1, UZUME_SPADA))  # gag (GAGI.md, reżyser 20.11.2026: „wykonaj wszystkie poprawki w ujęciach”): bóg spada ze śmiechu
    for n, x in enumerate((90, 1250)):
        pochodnia(st, t, x, 720, P.rekwizyty, seed=n + 3)
    podpis(w, t, "bogini tańca", 640, nad(240, 596) - 24, 0.8, 2.2)
    for n, (txt, x, d) in enumerate((("HA HA!", 270, 0.0), ("HA HA HA!", 1020, 0.5), ("HA HA!", 400, 1.4), ("HA HA HA!", 900, 2.0))):
        podpis(w, t, txt, x, 330 + 40 * (n % 2), UZUME_SMIECH + 0.3 + d, 1.6)
    zawieszki(st, t, w)
    st.spot = (640, 560, 0.83, 620, 0.55)  # pochodnie oświetlają tańczącą
    swiatlo(st, w, t, dim=0.8)


def s_lustro(st, w, t, T):
    """Głaz się uchyla, Amaterasu wygląda, lustro rozbłyskuje, siłacz odsuwa głaz."""
    w.sun, w.noc = 0.0, 1.0
    kam(st, t, 16, lerp(880, 900, ease(t / T)), 520, 2.0, 0.68, lens=1.8)
    st.dof = 1.6
    drzwi = 1.0 - 0.18 * ease(pr(t, 0.6, 1.0)) - 0.82 * ease(pr(t, T - 4.0, 2.2))
    crack = 1 - drzwi
    niebo(st, t, w, drzwi=drzwi, dach=0.0, pola=(0.0,) * 5)
    x0 = SKALA[0] - 0.07 * SKALA[2]
    st.put(J.glow(), x0 + 40, 560, P.wzgorza + 0.003, w=320 + 600 * crack, anchor=(0.5, 0.5), mode="add", alpha=0.25 + 0.5 * crack, shadow=None,
           tint=(1.0, 0.85, 0.5))
    peek = ease(pr(t, 1.4, 1.2))
    lalka(st, t, "amaterasu", lerp(1000, 958, peek) - 90 * ease(pr(t, T - 2.0, 1.4)), 150, y=SKALA[1] - 20, p=P.wzgorza + 0.002, lean=-8 * peek)
    _sakaki(st, t, blysk=ease(pr(t, 2.4, 0.5)) * (1 - 0.5 * pr(t, 4.0, 1.0)))
    push = ease(pr(t, T - 4.4, 1.0))
    lalka(st, t, "silacz", lerp(1330, 1150, push), 300, flip=-1, rece=(100 * push, 80 * push), lean=-10 * push)
    podpis(w, t, "najsilniejszy z bogów", 1030, 372, T - 4.0, 2.4)  # zbliżenie: górna krawędź kadru ok. 340
    podpis(w, t, "OCH!", 900, 400, 2.6, 1.8)  # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): Amaterasu zachwyca się sobą w lustrze
    zawieszki(st, t, w)
    swiatlo(st, w, t, dim=0.55 + 0.3 * crack)


def s_swit(st, w, t, T):
    """Słońce wraca na nitce, scena jaśnieje; przed jaskinią zjeżdża gruby sznur z białymi paskami papieru."""
    w.sun = pr(t, 0.2, 1.4)
    w.noc = 1 - ease(pr(t, 0.3, 1.6))
    k = ease(t / T)
    kam(st, t, 17, 800, lerp(440, 410, k), lerp(1.25, 1.06, k), 0.68)
    st.dof = 0.7
    niebo(st, t, w, drzwi=0.0, dach=0.0, pola=(0.0,) * 5)
    _sakaki(st, t)
    x0 = SKALA[0] - 0.07 * SKALA[2]
    lalka(st, t, "amaterasu", x0 - 120, 160, y=SKALA[1] - 20, p=P.wzgorza + 0.003, rece=(60, 0))
    st.put(J.glow(), x0 - 120, SKALA[1] - 120, P.wzgorza + 0.004, w=360, anchor=(0.5, 0.5), mode="add", alpha=0.4 * w.sun, shadow=None)
    J.hang(st, J.shimenawa(), x0 + 10, 470, P.wzgorza + 0.006, pr(t, 1.1, 1.2), t, 540, drop=420, sway=0.6, w=330, strings=(0.05, 0.95))
    _koguty(st, t, pieje=(0.4, 1.6))
    swiatlo(st, w, t, dim=lerp(0.5, 1.0, ease(pr(t, 0.3, 1.6))))


# ---------- akt 3 · Miecz w ogonie węża ----------

SUS_X = 230  # Susanoo w Izumo


def rzeka_y(x):
    return ziemia("blisko", 300) + 18 + (x - 120) * math.tan(math.radians(-1.0))


def s_wygnanie(st, w, t, T):
    """Susanoo zjeżdża na nitce z chmur nad rzekę; rzeką spływają dwie pałeczki."""
    land = pr(t, 0.7, 2.6)
    kam(st, t, 18, lerp(380, 520, ease(t / T)), lerp(380, 500, ease(land)), lerp(1.2, 1.4, ease(t / T)), 0.75)
    st.dof = 1.0
    kraj(st, t, w, rzeka=1.0)
    x = lerp(1180, 520, t / T)
    st.put(J.paleczki(), x, rzeka_y(x) - 4 + 2 * math.sin(t * 2.2), P.droga + 0.006, w=70, rot=4 * math.sin(t * 1.3), shadow=(2, 2, 3, 0.3))
    # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): Susanoo ląduje za mocno — gwiazdki nad głową i „AŁA!”
    zjazd(st, t, "susanoo", 420, STOPY, 290, land, flip=1, rece=(30 + 60 * pr(t, 3.3, 0.2) * (1 - pr(t, 4.6, 0.4)), 10),
          lean=4 * settle((t - 3.3) / 1.4, 1.5) - 9 * pr(t, 3.3, 0.15) * (1 - pr(t, 4.4, 0.5)),
          gwiazdki=pr(t, 3.35, 0.2) * (1 - pr(t, 4.5, 0.3)))
    podpis(w, t, "AŁA!…", 560, 330, 3.4, 1.6)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def waz_cien(st, t, x0, p, n=18, tint=(0.12, 0.12, 0.14)):
    """Grzbiet węża sunący za wzgórzem: widać tylko garby łusek nad grzbietem pasma."""
    for j in range(n):
        x = x0 + j * 54
        y = ziemia("srodek", clamp(x, -200, 1500)) + 34 + 20 * math.sin(j * 0.9 + t * 2.4)
        st.put(J.waz_luska(j % 3), x, y, p + 0.0002 * j, h=86, anchor=(0.5, 0.5), tint=tint, shadow=None)


def s_starcy(st, w, t, T):
    """W górze rzeki płaczą starcy z córką; za wzgórzem przesuwa się cień ogromnego węża."""
    kam(st, t, 19, lerp(700, 740, ease(t / T)), 470, 1.3, 0.8)
    st.dof = 1.0
    kraj(st, t, w, rzeka=1.0)
    waz_cien(st, t, lerp(1400, -900, pr(t, 1.6, T - 2.0)), P.miasto + 0.02)
    for n, (key, x) in enumerate((("starzec", 760), ("starucha", 880))):
        lalka(st, t, key, x, 270, flip=-1, lean=-8 + 5 * math.sin(t * (2.0 + 0.4 * n) + n), rece=(60 + 20 * math.sin(t * 2.6 + n), 0))
    flinch = ease(pr(t, 4.0, 0.6)) * (1 - ease(pr(t, 6.0, 1.0)))
    lalka(st, t, "kushinada", 1010, 250, flip=-1, lean=8 * flinch, rece=(40 + 60 * flinch, 0))
    lalka(st, t, "susanoo", 430, 290, flip=1, rece=(20, 0), lean=3 * ease(pr(t, 2.0, 1.0)))
    grzebien_we_wlosach(st, "susanoo", 430, 290, k=0.0)
    podpis(w, t, "starcy z Izumo", 820, nad(270) - 4, 0.9, 2.6)
    podpis(w, t, "ostatnia córka", 1010, nad(250) - 4, T - 4.2, 2.4)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


KADZIE = [330 + n * 120 for n in range(8)]


def kadzie(st, t, ks):
    for n, x in enumerate(KADZIE):
        k = ks[n] if isinstance(ks, (list, tuple)) else ks
        if k > 0:
            st.put(J.kadz(n), x, 694 + (1 - back(k, 1.3)) * 150, P.rekwizyty, h=100)


KADZIE_MRUG = 3.3  # gag: grzebień mruga (ten sam czas w efektach)


def s_kadzie(st, w, t, T):
    """Dziewczyna kurczy się w grzebień, który wskakuje Susanoo we włosy; wysuwa się rząd ośmiu kadzi."""
    kam(st, t, 20, lerp(640, 700, ease(t / T)), 480, 1.18, 0.8)
    st.dof = 0.9
    kraj(st, t, w, rzeka=1.0)
    for n, (key, x) in enumerate((("starzec", 760), ("starucha", 880))):
        lalka(st, t, key, x, 270, flip=-1, lean=-6, sink=pr(t, 2.6 + 0.3 * n, 1.2))
    shrink = ease(pr(t, 0.8, 1.2))
    kh = 250 * (1 - shrink)
    if kh > 8:
        lalka(st, t, "kushinada", 1010, kh, flip=-1, alpha=1 - 0.6 * shrink)
    fly = pr(t, 2.0, 1.2)
    tx, ty = punkt("susanoo", SUS_X, 290, 130, 66)
    if 0 < fly < 1:  # grzebień leci łukiem
        gx, gy = lerp(1010, tx, ease(fly)), lerp(560, ty, ease(fly)) - 180 * math.sin(math.pi * fly)
        st.put(J.grzebien(), gx, gy, P.lalki + 0.02, w=46, anchor=(0.5, 0.5), rot=540 * fly)
    elif shrink > 0.5 and fly <= 0:
        st.put(J.grzebien(), 1010, 600, P.lalki + 0.02, w=46 * (shrink - 0.5) * 2, anchor=(0.5, 0.5))
    lalka(st, t, "susanoo", SUS_X, 290, flip=1, rece=(90 * ease(pr(t, 4.0, 0.8)), 0), lean=2 * settle((t - 3.2) / 1.2, 1.5))
    grzebien_we_wlosach(st, "susanoo", SUS_X, 290, k=1.0 if fly >= 1 else 0.0)
    mrug = math.sin(math.pi * pr(t, KADZIE_MRUG, 0.5))  # gag (GAGI.md, reżyser 20.11.2026: „wykonaj wszystkie poprawki w ujęciach”): grzebień we włosach „mruga” do widza błyskiem
    if mrug > 0:
        st.put(J.glow(), tx, ty, P.lalki + 0.03, w=110, anchor=(0.5, 0.5), mode="add", alpha=0.7 * mrug, shadow=None, tint=(1.0, 0.95, 0.7))
        st.put(Z0.prop("gwiazdka"), tx + 10, ty - 8, P.lalki + 0.031, h=46 * mrug, anchor=(0.5, 0.5), rot=90 * mrug, shadow=None)
    kadzie(st, t, [pr(t, 3.6 + 0.35 * n, 0.6) for n in range(8)])
    swiatlo(st, w, t)


GLOWY = [(300, 300), (420, 250), (540, 330), (650, 230), (760, 300), (880, 240), (1000, 320), (1120, 260)]  # nasada szyi x, wysokość głowy y


def szyja(st, t, base, head, k, v, p, seed, tint=None, lezy=0.0, p_blisko=None):
    """Szyja węża z krążków łusek po łuku od nasady (za wzgórzem) do głowy; k = 0..1 wysuwanie."""
    if k <= 0:
        return
    bx, by = base
    hx, hy = head
    hy = by + (hy - by) * back(k, 1.2)
    cx, cy = (bx + hx) / 2 + 80 * math.sin(seed), min(by, hy) - 170
    n = 16
    pts = []
    for j in range(n + 1):
        u = j / n
        x = (1 - u) ** 2 * bx + 2 * (1 - u) * u * cx + u * u * hx
        y = (1 - u) ** 2 * by + 2 * (1 - u) * u * cy + u * u * hy
        pts.append((x + 6 * math.sin(t * 1.8 + seed + u * 3) * u, y))
    for j, (x, y) in enumerate(pts[:-1]):  # p_blisko: druga połowa szyi przechodzi nad przednim pasmem wzgórz
        pj = p_blisko if (p_blisko and j > n * 0.45) else p
        st.put(J.waz_luska(v), x, y, pj + 0.0003 * j, h=lerp(78, 50, j / n), anchor=(0.5, 0.5), tint=tint, shadow=(3, 4, 5, 0.3))
    if p_blisko:
        p = p_blisko
    (ax, ay), (zx, zy) = pts[-2], pts[-1]
    ang = math.degrees(math.atan2(zy - ay, zx - ax))
    face = 1 if zx >= ax else -1
    rot = ang if face > 0 else ang - 180
    rot = rot * (1 - lezy)
    st.put(J.waz_glowa(v), zx, zy, p + 0.006, h=74, anchor=(0.18, 0.5), rot=rot, sx=face, tint=tint, shadow=(3, 4, 5, 0.35))


OROCHI_GRYZ = (5.6, 6.4)  # głowa 2 kłapie na głowę 3, potem 3 oddaje (ten sam czas w efektach)


def s_orochi(st, w, t, T):
    """Zza gór wychylają się po kolei osiem głów na długich szyjach, z czerwonymi oczami. Jako skrót w haku („hak_waz”,
    księga D14) sam wąż: bez gagu z gryzieniem, bez Susanoo i kadzi (lektor mówi tylko o wężu i mieczu)."""
    hak = st.__dict__.get("skrot") == "hak_waz"
    k = ease(t / T)
    kam(st, t, 21, 700, lerp(420, 400, k), lerp(1.0, 1.1, k), 0.6, truck=0.5)
    st.dof = 0.6
    w.noc = 0.25
    kraj(st, t, w, rzeka=1.0)
    # marker reżysera 20.11.2026: głowy się ruszają (każda w swoim rytmie), a dwie gryzą się nawzajem; skrót w zapowiedzi bierze to samo
    gryz = [0.0 if hak else math.sin(math.pi * pr(t, a, 0.45)) for a in OROCHI_GRYZ]
    for n, (x, hy) in enumerate(GLOWY):
        base = (x, ziemia("srodek", x) + 70)
        hx = x + (40 if n % 2 else -40) + 26 * math.sin(t * (1.3 + 0.17 * n) + n)
        hy_ = hy + 16 * math.sin(t * (1.9 + 0.13 * n) + 2 * n)
        if n in (2, 3):  # głowa 2 kłapie na 3, potem 3 oddaje
            atak = gryz[0] if n == 2 else gryz[1]
            odskok = gryz[1] if n == 2 else gryz[0]
            hx += (70 if n == 2 else -70) * atak - (30 if n == 2 else -30) * odskok
            hy_ += -20 * atak + 16 * odskok
        szyja(st, t, base, (hx, hy_), pr(t, 0.6 + 0.6 * n, 1.0), n % 3, P.miasto + 0.012 + 0.0015 * n, n)
    if not hak:
        podpis(w, t, "KŁAP!", 600, 150, OROCHI_GRYZ[0] + 0.1, 1.6)
    zawieszki(st, t, w)
    if not hak:
        kadzie(st, t, 1.0)
        lalka(st, t, "susanoo", SUS_X, 290, flip=1, rece=(20, 0), lean=-3 * ease(pr(t, 3.0, 1.0)))
        grzebien_we_wlosach(st, "susanoo", SUS_X, 290)
    swiatlo(st, w, t)


def s_pije(st, w, t, T):
    """Głowy zanurzają się w kadziach, piją, kiwają się i jedna po drugiej opadają na wzgórza."""
    kam(st, t, 22, 720, 460, 1.12, 0.7)
    st.dof = 0.7
    w.noc = 0.25
    kraj(st, t, w, rzeka=1.0)
    for n, (x, hy) in enumerate(GLOWY):
        base = (x, ziemia("srodek", x) + 70)
        dip = ease(pr(t, 0.1 * n, 0.8))
        drop = ease(pr(t, 1.8 + 0.18 * n, 0.9))
        vx = KADZIE[n]
        up = (x + (40 if n % 2 else -40), hy)
        drink = (vx, 578 + 6 * math.sin(t * 9 + n) * (1 - drop))
        sleep = (x + 60 * (1 if n % 2 else -1), ziemia("przod", x) + 14)
        hx = lerp(lerp(up[0], drink[0], dip), sleep[0], drop)
        hy_ = lerp(lerp(up[1], drink[1], dip), sleep[1], drop)
        szyja(st, t, base, (hx, hy_), 1.0, n % 3, P.miasto + 0.012 + 0.0015 * n, n, lezy=drop, p_blisko=P.wzgorza + 0.062 + 0.001 * n)
    kadzie(st, t, 1.0)
    lalka(st, t, "susanoo", SUS_X, 290, flip=1, rece=(10, 0))
    grzebien_we_wlosach(st, "susanoo", SUS_X, 290)
    podpis(w, t, "HIK!", 900, 430, 0.9, 1.4)  # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): pijana głowa czka
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_miecz(st, w, t, T):
    """Susanoo tnie mieczem: szyje opadają, z ogona wysuwa się błyszczący miecz i wznosi się nad scenę."""
    slash = pr(t, 0.8, 0.35)
    kam(st, t, 23, lerp(560, 620, ease(t / T)), 470, 1.32, 0.8, shake=7.0 * (0 < slash < 1 or 0.8 < t < 1.6))
    st.dof = 1.0
    w.noc = 0.25 * (1 - pr(t, 3.0, 2.0))
    kraj(st, t, w, rzeka=1.0)
    for n, (x, hy) in enumerate(GLOWY):
        base = (x, ziemia("srodek", x) + 70)
        fall = ease(pr(t, 1.0 + 0.12 * n, 0.8))
        sleep = (x + 60 * (1 if n % 2 else -1), ziemia("przod", x) + 14 + 140 * fall)
        if n == 3:  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): „porusz go troszkę” — ścięta głowa jeszcze drga
            sleep = (sleep[0], sleep[1] - 14 * abs(math.sin(t * 7.0)) * pr(t, 8.4, 0.3) * (1 - pr(t, 11.0, 0.4)))
        szyja(st, t, base, sleep, 1.0, n % 3, P.miasto + 0.012 + 0.0015 * n, n, lezy=1.0, p_blisko=P.wzgorza + 0.062 + 0.001 * n)
    kadzie(st, t, 1.0)
    arm = 160 - 150 * ease(slash) if t > 0.3 else 160 * ease(pr(t, 0.0, 0.3))
    lalka(st, t, "susanoo", SUS_X + 160, 290, flip=1, rece=(arm, 20), lean=10 * ease(slash) - 4, trzyma=MIECZ(290))
    grzebien_we_wlosach(st, "susanoo", SUS_X + 160, 290, rot=10 * ease(slash) - 4)
    # marker reżysera 20.11.2026: „pojawia się ogon, a z niego ten miecz” — ogon z łusek wysuwa się zza wzgórza, z jego czubka wysuwa się miecz
    og = ease(pr(t, 1.0, 0.8))
    tipx, tipy = 870, ziemia("przod", 870) - 30 - 150 * og  # w kadrze (kamera ok. 560–620, ×1,32)
    if og > 0:
        for j in range(11):
            u = j / 10
            x = 880 - 10 * u + 10 * math.sin(u * 3.0 + t * 1.2) * u  # ogon prawie pionowy: miecz jedzie w nim od dołu
            y = ziemia("przod", 880) + 60 - (ziemia("przod", 880) + 60 - tipy) * u
            st.put(J.waz_luska(j % 3), x, y, P.wzgorza + 0.06 + 0.0003 * j, h=lerp(70, 30, u), anchor=(0.5, 0.5), shadow=(3, 4, 5, 0.3))
    # reżyser 20.11.2026: „miecz ma wyjechać od dołu przez ten ogon” — miecz jedzie w górę za przednim pasmem wzgórz (spod
    # ziemi) i wewnątrz ogona (za łuskami), a ostrze wychodzi z czubka ogona
    rs = pr(t, 2.0, 2.4)
    if rs > 0:
        dol = ziemia("przod", 880) + 260
        y = lerp(dol, tipy - 20, ease(rs))  # dolny koniec rękojeści
        st.put(J.glow(), tipx, y - 200, P.wzgorza + 0.0605, w=420, anchor=(0.5, 0.5), mode="add", alpha=0.45 * ease(pr(t, 3.2, 1.0)), shadow=None,
               tint=(1.0, 0.95, 0.75))
        st.put(J.miecz_jp(True), tipx, y, P.wzgorza + 0.049, h=240, anchor=(0.5, 1.0), rot=2 * math.sin(t * 0.9))
    podpis(w, t, "POMOCY!", 250, 440, 1.5, 2.4)  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): pierwsza ścięta głowa woła o pomoc
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def skarby_w_niebie(st, t, k=(1.0, 1.0, 1.0), x0=560, y=330, p=P.lalki + 0.03):
    J.hang(st, J.lustro(), x0, y, p, k[0], t, 550, drop=520, sway=1.0, w=90)
    J.hang(st, J.magatama_sznur(), x0 + 140, y + 10, p, k[1], t, 551, drop=520, sway=1.0, w=130, strings=(0.1, 0.9))
    if k[2] > 0:
        J.hang(st, J.miecz_jp(True), x0 + 280, y - 20, p, k[2], t, 552, drop=520, sway=0.8, h=200)
        st.put(J.glow(), x0 + 280, y + 70, p + 0.001, w=240, anchor=(0.5, 0.5), mode="add", alpha=0.25 * k[2], shadow=None)


SKARBY_MACH = 9.0  # Ninigi wymachuje mieczem (ten sam czas w efektach)


def s_skarby(st, w, t, T):
    """Na chmurach Amaterasu i wnuk Ninigi; zjeżdżają lustro, klejnoty i miecz, Ninigi unosi ręce."""
    k = ease(t / T)
    kam(st, t, 24, lerp(600, 640, k), 480, lerp(1.25, 1.38, k), 0.8)
    st.dof = 1.0
    niebo(st, t, w, drzwi=0.0, dach=0.0, pola=(1.0,) * 5, lina=1.0)
    lalka(st, t, "amaterasu", 360, 300, pr(t, 1.0, 1.0), flip=1, rece=(70 * ease(pr(t, 2.4, 0.8)), 0))
    # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): „miecz ma być tutaj” — Ninigi, unosząc ręce, bierze wiszący miecz do dłoni (6,4–7,0 s) i trzyma go w górze
    chwyt = ease(pr(t, 6.4, 0.6))
    mach = math.sin(2 * math.pi * 3 * pr(t, SKARBY_MACH, 1.2)) * (0 < t - SKARBY_MACH < 1.2)  # marker reżysera 20.11.2026: szybko góra-dół ×3
    dlon = lalka(st, t, "ninigi", 880, 280, pr(t, 1.4, 1.0), flip=-1,
                 rece=(120 * ease(pr(t, 6.6, 1.0)) + 45 * mach, 120 * ease(pr(t, 6.8, 1.0))),
                 trzyma=MIECZ(280, True) if chwyt >= 1 else None)
    podpis(w, t, "HAJA!", 1010, 230, SKARBY_MACH, 1.8)
    skarby_w_niebie(st, t, (pr(t, 2.6, 1.2), pr(t, 3.8, 1.2), pr(t, 5.0, 1.2) if chwyt <= 0 else 0.0))
    if 0 < chwyt < 1 and dlon:
        st.put(J.miecz_jp(True), lerp(840, dlon[0], chwyt), lerp(310, dlon[1] - 110, chwyt), P.lalki + 0.03, h=200 * lerp(1.0, 0.87, chwyt),
               anchor=(0.5, 0.0))
    podpis(w, t, "Ninigi, wnuk Amaterasu", 880, nad(280) - 4, 1.8, 2.6)
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 1.0, 0.94))


def s_zejscie(st, w, t, T):
    """Ninigi zjeżdża na chmurze przez kolejne warstwy chmur aż na szczyt góry."""
    f = t / T
    kam(st, t, 25, 640, 420, 1.15, 0.8, drift=0.6)
    st.dof = 1.1
    tint = (lerp(1.04, 1.0, f), lerp(0.98, 1.0, f), lerp(0.86, 1.0, f))
    niebo_papier(st, w, tint)
    slonce(st, t, w)
    r = random.Random(25)
    for j in range(14):  # warstwy chmur przelatują w górę: bliższe szybciej (paralaksa)
        p = 0.3 + 0.62 * r.random()
        name = ("cloud_left", "cloud_center", "cloud_right")[j % 3]
        y = 900 + r.uniform(0, 500) - (t + r.uniform(0, 3)) * 420 * p % 1500
        x = r.uniform(-100, 1380)
        st.put(J.S(name, 0.5), x, y, p, w=lerp(400, 900, p), anchor=(0.5, 0.5), haze=0.2 * (1 - p), shadow=(6, 8, 10, 0.2),
               alpha=0.95, blur=None)
    peak = ease(pr(t, T - 5.6, 2.6))  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): „wydłuż końcówkę, jak już jest na ziemi” — ląduje 3 s przed końcem
    na_ziemi = ease(pr(t, T - 2.6, 0.9))
    st.put(J.fuji(1), 660, 1200 - 520 * peak, 0.62, w=900, haze=0.1)  # zielony stożek Takachiho
    ry = 470 + 8 * math.sin(t * 1.6) + 70 * peak
    st.put(J.S("cloud_center", 0.5), 640, ry + 40, 0.8, w=420, anchor=(0.5, 0.5), shadow=(6, 8, 10, 0.3))
    lalka(st, t, "ninigi", 640, 250, y=ry + 30, p=0.801, rece=(40 + 110 * na_ziemi, 20 + 60 * na_ziemi),
          lean=3 * math.sin(t * 1.3) * (1 - na_ziemi))
    rampa(st)
    swiatlo(st, w, t, extra=tint)


def s_siostry(st, w, t, T):
    """Pod wiśnią księżniczka kwiatów, przy głazie księżniczka skał; Ninigi wybiera wiśnię, szara lalka opada."""
    kam(st, t, 26, 660, 470, lerp(1.18, 1.26, ease(t / T)), 0.8)
    st.dof = 1.0
    kraj(st, t, w, sosny=(0.0, 1.0))
    st.put(J.wisnia(), 300, 712, P.drzewa, h=420, anchor=J.wisnia().pien)
    st.put(J.glaz(2), 1040, 716, 0.76, w=300)
    lalka(st, t, "kwiat", 390, 270, flip=1, lean=2 * math.sin(t * 0.8), rece=(30, 0))
    lalka(st, t, "skala", 950, 270, flip=-1, sink=pr(t, T - 4.4, 2.6), lean=-4 * ease(pr(t, T - 5.0, 1.0)))
    turn = math.cos(math.pi * ease(pr(t, 3.6, 0.6)))
    lalka(st, t, "ninigi", 670, 280, flip=turn, rece=(70 * ease(pr(t, 4.4, 0.8)), 0))
    for j in range(8):
        r = random.Random(800 + j)
        f = ((t * 0.12 + r.random()) % 1.0)
        st.put(J.platek(j), 260 + r.uniform(-80, 160) + 60 * math.sin(t * 1.4 + j), 360 + f * 360, P.drzewa + 0.02, w=11,
               rot=t * 160 + j * 40, shadow=None)
    podpis(w, t, "księżniczka kwiatów", 390, nad(270) - 4, 1.0, 2.6)
    podpis(w, t, "księżniczka skał", 950, nad(270) - 4, 1.6, min(2.6, T - 4.4 - 1.6))
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_platki(st, w, t, T):
    """Detal: z wiśni sypią się płatki na rampę, kwiaty na gałęziach gasną."""
    fade = ease(pr(t, 1.0, T - 1.4))
    kam(st, t, 27, 330, 470, 2.4, 0.74, lens=2.1)
    st.dof = 2.0
    kraj(st, t, w, sosny=(0.0, 1.0), kul=False)
    c = lerp(1.0, 0.72, fade)
    st.put(J.wisnia(), 300, 712, P.drzewa, h=420, anchor=J.wisnia().pien, tint=(c, c * lerp(1.0, 0.86, fade), c * lerp(1.0, 0.8, fade)))
    for j in range(22):
        r = random.Random(820 + j)
        t0 = r.uniform(0, T - 1.5)
        f = pr(t, t0, r.uniform(2.6, 3.6))
        if f <= 0:
            continue
        x = 240 + r.uniform(-40, 220) + 40 * math.sin(t * 1.8 + j) * (1 - f)
        y = lerp(380 + r.uniform(0, 80), 690, f)
        st.put(J.platek(j), x, y, P.drzewa + 0.03 + 0.001 * (j % 5), w=14, rot=t * 200 * (1 if j % 2 else -1) * (1 - f), shadow=(2, 2, 3, 0.3))
    rampa(st)
    swiatlo(st, w, t)


# ---------- akt 4 · Na wschód ----------

IW = 300  # Iwarebiko stoi z lewej, twarzą na wschód
WSCHOD_STRZAL = 3.6
BRACIA_SKOK = (6.5, 7.15, 7.8)  # najmłodszy brat podskakuje z radości (marker reżysera 18.11.2026)  # strzała w stronę gór (marker reżysera 18.11.2026)


def s_prawnuk(st, w, t, T):
    """Ninigi opada pod rampę, na jego miejscu wysuwa się Iwarebiko z łukiem; zjeżdża zawieszka „Kiusiu” (przegląd 18.11.2026:
    mniej imion — bez krainy Hyūga)."""
    w.zawieszki = [("Kiusiu", 580, 330, pr(t, 4.4, 1.0))]
    k = ease(t / T)
    kam(st, t, 28, lerp(470, 500, k), 500, lerp(1.48, 1.62, k), 0.8)
    st.dof = 1.3
    kraj(st, t, w, morze_k=1.0)
    lalka(st, t, "ninigi", 420, 280, pr(t, 1.2, 0.8), flip=1, sink=pr(t, 2.2, 1.4), lean=-4 * ease(pr(t, 2.0, 0.8)))  # wchodzi razem z rampą
    hh = lerp(230, 290, ease(pr(t, 3.6, T - 4.0)))  # marker reżysera 20.11.2026: „zrób go troszkę mniejszego na początku” — młody książę rośnie
    lalka(st, t, "iwarebiko", 420, hh, pr(t, 3.2, 1.2), flip=1, rece=(15, 0), trzyma=LUK(hh))
    podpis(w, t, "książę Iwarebiko", 300, nad(290), 4.0, 2.8)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_wschod(st, w, t, T):
    """Iwarebiko patrzy na zachód, obraca się na wschód i wskazuje go (zwrot lalki, wytyczne 1.16): po prawej wysuwają
    się błękitne góry, nad nimi wschodzi słońce."""
    k = ease(t / T)
    kam(st, t, 29, lerp(620, 700, k), 430, lerp(1.0, 1.08, k), 0.62, truck=0.6)
    st.dof = 0.6
    kraj(st, t, w, morze_k=1.0, slonce_k=0.0, tint=(1.04, 0.97, 0.9))
    sr = pr(t, 2.6, 2.2)
    if sr > 0:
        st.put(J.glow(), 1090, 320 - 160 * ease(sr), P.slonce, w=700, anchor=(0.5, 0.5), mode="add", alpha=0.35 * sr, shadow=None, tint=(1.0, 0.7, 0.45))
        st.put(J.S("sun", 0.5), 1090, 470 - 220 * ease(sr), P.slonce + 0.002, w=170, anchor=(0.5, 0.5))
    for n, (x, wd) in enumerate(((1000, 520), (1190, 600))):
        Z0.rise(st, J.gora_niebieska(n % 2), x, 470, P.gory_dal + 0.03 + 0.004 * n, pr(t, 1.4 + 0.4 * n, 0.9), t, 640 + n, w=wd, wob=0.0, haze=0.2)
    turn = -math.cos(math.pi * ease(pr(t, 0.3, 0.5)))  # zwrot lalki: z zachodu (dom, Kiusiu) na wschód
    point = ease(pr(t, 1.0, 0.8))
    dlon = lalka(st, t, "iwarebiko", IW, 300, flip=turn, rece=(85 * point, 0), lean=-2 * point, trzyma=LUK(300))
    # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): tabliczka „HMM…”, potem Iwarebiko strzela w stronę niebieskich gór (strzała wbija się w zbocze)
    podpis(w, t, "HMM…", IW, nad(300), 1.8, 1.5)
    lot = pr(t, WSCHOD_STRZAL, 0.55)
    if dlon and lot > 0:
        cel = (873, 404)
        x0, y0 = dlon[0] + 30, dlon[1] - 10
        ang = math.degrees(math.atan2(cel[1] - y0, cel[0] - x0))
        if lot < 1:
            st.put(Z0.prop("strzala"), lerp(x0, cel[0], lot), lerp(y0, cel[1], lot) - 50 * math.sin(math.pi * lot), P.lalki + 0.013, w=96,
                   anchor=(0.95, 0.5), rot=-ang + 12 * (1 - 2 * lot), shadow=(2, 3, 3, 0.4))
        else:
            st.put(Z0.prop("strzala"), cel[0], cel[1], P.gory_dal + 0.036, w=60, anchor=(0.95, 0.5), rot=-ang - 10, shadow=(2, 3, 3, 0.3))
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 0.98, 0.93))


def bracia(st, t, ks=(1.0, 1.0, 1.0), turns=(1.0, 1.0, 1.0), x0=470, lifts=(0.0, 0.0, 0.0)):
    for n, key in enumerate(("itsuse", "brat2", "brat3")):
        lalka(st, t, key, x0 + n * 125, 285 - 8 * n, ks[n], flip=turns[n], rece=(10 + 2 * lifts[n], 0), seed=150 + n, lift=lifts[n])


def s_bracia(st, w, t, T):
    """Obok Iwarebiko wysuwają się trzej bracia; wszyscy obracają się na wschód."""
    kam(st, t, 30, lerp(560, 600, ease(t / T)), 490, 1.36, 0.8)
    st.dof = 1.0
    kraj(st, t, w, morze_k=1.0, tint=(1.03, 0.98, 0.93))
    lalka(st, t, "iwarebiko", IW, 300, flip=1, rece=(30, 0), trzyma=LUK(300))
    turns = [-math.cos(math.pi * ease(pr(t, 3.4 + 0.5 * n, 0.5))) for n in range(3)]
    skok = sum(55 * math.sin(math.pi * pr(t, a0, 0.45)) for a0 in BRACIA_SKOK)  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): „porusz go, niech skacze”
    bracia(st, t, [pr(t, 0.6 + 0.6 * n, 1.0) for n in range(3)], turns, lifts=(0.0, 0.0, skok))
    podpis(w, t, "Itsuse, najstarszy brat", 470, nad(285), 1.7, 2.6)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


# łodzie wyprawy (1 + 16): potęga to liczba (wytyczne 1.17; przegląd 17.11 — w ujęciu była jedna łódź)


FLOTA_PIORUN = 4.2  # piorun w stateczek w oddali (ten sam czas w efektach)
FLOTA_MEWA = 6.6  # gag: mewa nad łodzią wodza (ten sam czas w efektach)


def s_flota(st, w, t, T):
    """Flota łodzi z wiosłami i żaglami z maty płynie na wschód między wyspami, na trzech pasmach fal; szybsze mijają
    wolniejsze, kamera płynie z łodzią wodza (Iwarebiko i Itsuse na pokładzie)."""
    x = lerp(380, 900, t / T)
    kam(st, t, 31, x + 120, 430, 1.28, 0.6, truck=0.85)
    st.dof = 0.7
    isl = [(-200, 1, 380, 0, 1.0), (260, 2, 420, 3, 1.0), (720, 1, 300, 4, 1.0), (1150, 2, 460, 6, 1.0), (1560, 1, 360, 2, 1.0),
           (1900, 2, 420, 5, 1.0), (40, 3, 520, 7, 1.0), (1320, 3, 560, 1, 1.0)]
    morze(st, t, w, wyspy=isl)
    flota = [(0.0, 2, 150, 0.0)]  # (odstęp od łodzi wodza, pasmo fal, wysokość, prędkość względem niej w px na całe ujęcie)
    r = random.Random(310)
    for b, hb, n, gap in ((2, 138, 5, 340), (1, 110, 6, 300), (0, 82, 5, 330)):  # łodzie na pasmie w równych odstępach
        for i in range(n):
            dx = -1300 + gap * 0.5 * (b % 2) + i * gap + r.uniform(-50, 50)
            if b == 2 and abs(dx) < 200:  # miejsce łodzi wodza
                dx -= 260
            flota.append((dx, b, hb * r.uniform(0.92, 1.05), r.uniform(-240, 200)))
    # marker reżysera 20.11.2026: nadlatuje ciemna chmurka, piorun wali w stateczek w oddali, który płonie i tonie — „WHY ME?!”
    xp = lerp(380, 900, FLOTA_PIORUN / T)
    cel = min((j for j, (dx, b, h, v) in enumerate(flota) if b < 2 and j % 2 == 0),
              key=lambda j: abs(xp + flota[j][0] + flota[j][3] * FLOTA_PIORUN / T - 680))
    for j, (dx, b, h, v) in sorted(enumerate(flota), key=lambda e: (e[1][1], e[0])):  # dalsze pasma rysuje się najpierw
        t0 = 0.9 + 0.08 * j
        if pr(t, t0, 0.1) <= 0:  # łodzie wypływają dopiero na postawione fale
            continue
        lad = ([("iwarebiko", -40, 120, (20, 0)), ("itsuse", 50, 116, (10, 0))] if j == 0 else
               [("wojownik", -25, h * 0.7, (0, 0)), ("wojownik", 30, h * 0.66, (0, 0))] if b == 2 else
               [("wojownik", 0, h * 0.7, (0, 0))] if b == 1 else [])
        if j == 0:  # gag (reżyser 20.11.2026: „dołóż gagi”, Podręcznik „Humor i gagi”, lista w docs/filmy/powstanie-japonii/GAGI.md): mewa przelatuje nisko nad łodzią wodza, Itsuse się uchyla
            lad = [("iwarebiko", -40, 120, (20, 0)), ("itsuse", 50, 116 - 18 * math.sin(math.pi * pr(t, FLOTA_MEWA + 0.5, 0.9)), (10, 0))]
        tonie = ease(pr(t, FLOTA_PIORUN + 1.2, 2.4)) if j == cel else 0.0
        bx = x + dx + v * t / T
        lodz(st, t, bx, b, h=h, seed=j, sink=max(1 - ease(pr(t, t0, 0.8)), tonie), ladunek=lad, v=j % 2, wiosla=True)
        if j == cel:
            px, py, _, pp = poklad_lodzi(t, bx, b, h, 0, 0, seed=j, sink=tonie)
            chm = pr(t, FLOTA_PIORUN - 1.0, 0.9) * (1 - pr(t, FLOTA_PIORUN + 1.2, 0.8))
            if chm > 0:
                J.hang(st, J.krazek("chmura"), px + 260 * (1 - chm), py - 230, pp + 0.002, chm, t, 312, w=150, sway=1.0, haze=0.1)
            piorun(st, t, px, py - 200, px, py - 20, 1 - pr(t, FLOTA_PIORUN, 0.25) if t >= FLOTA_PIORUN else 0.0, pp + 0.003, seed=4)
            ogien = pr(t, FLOTA_PIORUN + 0.1, 0.3) * (1 - pr(t, FLOTA_PIORUN + 3.0, 0.4))
            if ogien > 0:
                plomien(st, t, px, py - 10, pp + 0.001, 42 * ogien, seed=9)
            podpis(w, t, "CZEMU JA?!", px + 20, py - 190, FLOTA_PIORUN + 0.5, 1.8)  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN)
    m = pr(t, FLOTA_MEWA, 1.6)
    if 0 < m < 1:
        st.put(Z0.bird(int(t * 9) % 2), lerp(x + 760, x - 520, m), 300 + 140 * math.sin(math.pi * m), P.lalki + 0.02, w=90, sx=-1,
               shadow=(4, 6, 6, 0.3))
    podpis(w, t, "EJ!", lerp(380, 900, (FLOTA_MEWA + 0.6) / T) + 170, 250, FLOTA_MEWA + 0.6, 1.5)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_postoje(st, w, t, T):
    """Przy brzegu stoją łodzie; ryż wyrasta, żółknie i zostaje ścięty, a na brzegu rośnie szkielet nowej łodzi."""
    f = t / T
    w.sun_xy = (lerp(150, 1150, (f * 2) % 1.0), 110 + 30 * math.sin(math.pi * ((f * 2) % 1.0)) * -1)
    w.pola_v = 0 if f < 0.36 else (1 if f < 0.68 else 2)
    kam(st, t, 32, lerp(600, 660, ease(f)), 480, 1.18, 0.66)
    st.dof = 0.8
    kraj(st, t, w, morze_k=1.0, pola=1.0)
    for j in range(2):
        st.put(J.lodz(1), 120 + j * 170, 600 + 4 * math.sin(t * 1.6 + j) + j * 16, Z0.P.rownina + 0.012 + 0.01 * j, h=110,
               rot=2 * math.sin(t * 1.2 + j))
    g = ease(pr(t, 1.0, T - 2.0))
    st.put(J.szkielet_lodzi(), 900, ziemia("blisko", 900) + 40, P.droga + 0.03, w=300, anchor=(0.0, 1.0), sx=max(0.04, g))
    lalka(st, t, "wojownik", 840, 220, flip=1, rece=(60 + 40 * abs(math.sin(t * 4)), 0), seed=160)
    swiatlo(st, w, t)


NANIWA_WJAZD = 3.5  # gag: łódź wjeżdża na brzeg (ten sam czas w efektach)


def s_naniwa(st, w, t, T):
    """Sześć łodzi wpływa do zatoki Naniwa i staje przy brzegu; rzędy włóczni z białymi proporcami i wojownicy wychodzą
    na brzeg, każdy we własnej chwili, i ruszają na wschód, ku górom (potęga liczbą, wytyczne 1.17; przegląd 17.11:
    w ujęciu stały tylko dwie lalki)."""
    k = ease(t / T)
    kam(st, t, 33, lerp(430, 660, k), 450, lerp(1.1, 1.18, k), 0.66)  # od zatoki z łodziami ku brzegowi z wojskiem
    st.dof = 0.7
    kraj(st, t, w, gora_x=900, sosny=(0.0, 1.0))  # bez wiśni na lewej kulisie: zasłaniała zatokę
    # zatoka na przodzie sceny: pasma fal wysuwają się od dołu z lewej, kończą się przy skałach brzegu (x ≈ 560)
    zat = bk(w, 0.3, 0.8)
    for i, (y, pp) in enumerate(((592, P.wzgorza + 0.052), (640, P.wzgorza + 0.058))):
        st.put(J.waves(2 + i), -80 + 26 * math.sin(t * 0.9 + i) * (1 if i else -1), y + (1 - back(zat, 1.2)) * 260, pp, w=1400,
               anchor=(0.5, 0.0))
    for j in range(6):  # łodzie wpływają do zatoki jedna za drugą i stają przy brzegu
        x = lerp(-340 - j * 200, 10 + j * 92, ease(pr(t, 0.6 + 0.24 * j, 2.6)))
        wjazd = ease(pr(t, NANIWA_WJAZD, 0.35)) if j == 5 else 0.0  # gag (GAGI.md, reżyser 20.11.2026: „wykonaj wszystkie poprawki w ujęciach”): ostatnia łódź przybija za mocno i wjeżdża na skały
        st.put(J.lodz(j % 2), x + 46 * wjazd, 628 + 4 * math.sin(t * 1.6 + j) - (j % 2) * 22 - 34 * wjazd, P.wzgorza + 0.054 + 0.0004 * j,
               h=146 - 14 * (j % 2), rot=2 * math.sin(t * 1.2 + j) * (1 - wjazd) - 14 * wjazd, alpha=min(1.0, zat * 3))
    podpis(w, t, "BUM!", 560, 470, NANIWA_WJAZD + 0.1, 1.4)
    Z0.rise(st, J.glaz(1), 640, 724, P.wzgorza + 0.062, bk(w, 0.9), t, 335, w=230, wob=0.0, tint=(0.88, 0.86, 0.82),
            shadow=(4, 6, 8, 0.35))  # skały brzegu zasłaniają koniec pasm fal
    marsz = 70 * ease(pr(t, 5.2, T - 5.2))  # wojsko rusza na wschód, ku górom
    for n, (x, band, p, hh, seed) in enumerate(((560, "srodek", P.miasto + 0.032, 96, 13), (980, "srodek", P.miasto + 0.033, 92, 17),
                                                (700, "blisko", P.droga + 0.012, 130, 11), (1140, "blisko", P.droga + 0.013, 124, 19))):
        up = pr(t, 2.6 + 0.35 * n, 1.2)
        if up > 0:  # rzędy włóczni z białymi proporcami wychodzą zza grzbietów, jeden po drugim
            st.put(Z0.spears(seed, flag=(238, 234, 222)), x + marsz * (1.0 - 0.3 * (band == "srodek")),
                   ziemia(band, x - 120) + (80 if band == "blisko" else 64) + (1 - back(up, 1.3)) * 140, p, h=hh, anchor=(1.0, 1.0),
                   rot=0.8 * math.sin(t + n))
    for n in range(5):  # wojownicy na brzegu, każdy z własnym opóźnieniem (1.7)
        r = random.Random(330 + n)
        stop = ease(pr(t, 10.4, 0.4)) if n == 0 else 0.0  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): tabliczka „STOP!” i ręka do góry
        lalka(st, t, "wojownik", 830 + n * 92 + marsz, 230 - 4 * n, pr(t, 3.4 + r.uniform(0, 1.2), 0.9), flip=1, rece=(10 + 150 * stop, 0),
              hop=4 if marsz > 1 else 0, seed=170 + n)
    podpis(w, t, "STOP!", 830 + marsz, nad(230) - 10, 10.5, 1.8)
    lalka(st, t, "iwarebiko", 640, 290, pr(t, 4.4, 1.0), flip=1, trzyma=LUK(290), rece=(20, 0))
    lalka(st, t, "itsuse", 740, 280, pr(t, 4.8, 1.0), flip=1, rece=(10, 0))
    zawieszki(st, t, w)
    swiatlo(st, w, t)


NAGA = (930, 520)  # Nagasunehiko: x, wysokość lalki


NAGA_RYTM = (3.6, 4.4, 5.2)  # włócznie wojska Nagasunehiko unoszą się na 0,6 s trzy razy (wytyczne 1.17); te same czasy w efektach


NAGA_SZTYLET = 6.2  # wódz wyciąga sztylet (ten sam czas w efektach)


def s_nagasune(st, w, t, T):
    """Zza grani wyrasta wielki wódz na długich nogach z tabliczką z imieniem, za nim cztery rzędy ciemnych włóczni aż
    po dalsze wzgórza; włócznie trzy razy unoszą się w rytmie, a wódz podnosi rękę; słońce zza jego pleców."""
    w.sun_xy = (1080, 250)
    kam(st, t, 34, lerp(800, 840, ease(t / T)), 430, 1.28, 0.72)
    st.dof = 1.0
    kraj(st, t, w, gora_x=900, tint=(1.04, 0.97, 0.9))
    rytm = sum(24 * math.sin(math.pi * pr(t, a, 0.6)) for a in NAGA_RYTM)  # włócznie w górę trzy razy, wszystkie razem
    for n, (xr, seed, band, p, hh) in enumerate(((1100, 25, "srodek", P.miasto + 0.032, 120), (560, 27, "srodek", P.miasto + 0.033, 116),
                                                 (1360, 21, "przod", P.wzgorza + 0.035, 230), (720, 23, "przod", P.wzgorza + 0.033, 230))):
        up = pr(t, 1.6 + 0.3 * n, 1.2)
        if up > 0:  # wojsko za wodzem: dalsze rzędy na środkowym paśmie, bliższe przed pasmem przednim (1.5)
            st.put(Z0.spears(seed, flag=(56, 40, 34)), xr, ziemia(band, xr - 250) + (40 if band == "przod" else 60)
                   + (1 - back(up, 1.3)) * 200 - rytm * hh / 230, p, h=hh, anchor=(1.0, 1.0), rot=0.8 * math.sin(t + n))
    x, h = NAGA
    # marker reżysera 20.11.2026: wyciąga ręką sztylet zza pasa i wymachuje nim: raz, dwa, raz
    szt = pr(t, NAGA_SZTYLET, 0.4)
    mach = sum(math.sin(math.pi * pr(t, NAGA_SZTYLET + 0.5 + 0.45 * i, 0.4)) for i in range(3))
    reka = 30 + 60 * (rytm > 4) if szt <= 0 else lerp(30, 100, ease(szt)) + 50 * mach
    lalka(st, t, "nagasune", x, h, pr(t, 0.5, 1.6), y=ziemia("przod", x) + 120, p=P.wzgorza + 0.04, flip=-1, rece=(reka, 0),
          lean=2 * settle((t - 2.2) / 1.6, 1.5), trzyma=(J.miecz_jp(False), h * 0.26, (0.5, 0.93), 180.0, True) if szt > 0 else None)
    podpis(w, t, "wódz Nagasunehiko", 760, 300, 2.2, 2.8)
    podpis(w, t, "NIE MA MOWY!", 830, 230, 5.3, 2.2)  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN)
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 0.97, 0.92))


def s_strzaly(st, w, t, T):
    """Spod wschodzącego słońca nadlatuje chmara strzał i wbija się w brzeg."""
    w.sun_xy = (1080, 250)
    kam(st, t, 35, 620, 430, 1.12, 0.7, shake=4.0)
    st.dof = 0.7
    kraj(st, t, w, gora_x=900, tint=(1.04, 0.97, 0.9))
    for j in range(16):
        r = random.Random(900 + j)
        t0 = r.uniform(0.0, 0.6)
        f = pr(t, t0, 0.9)
        if f <= 0:
            continue
        x0, y0 = 1240 + r.uniform(-60, 120), 160 + r.uniform(-60, 80)
        x1 = r.uniform(240, 760)
        y1 = ziemia("przod", x1) + r.uniform(10, 40)
        x = lerp(x0, x1, f)
        y = lerp(y0, y1, f) - 160 * math.sin(math.pi * f)
        dxdt, dydt = x1 - x0, (y1 - y0) - 160 * math.pi * math.cos(math.pi * f)
        ang = math.atan2(dydt, dxdt)
        st.put(Z0.prop("strzala"), x, y, P.wzgorza + 0.06, w=110, anchor=(0.95, 0.5), rot=math.degrees(ang),
               shadow=(3, 4, 4, 0.35))
        # reżyser 20.11.2026 (ujęcie 4, zapowiedź): „lecą strzały, ale z ogniem” — płonący grot, po wbiciu pali się dalej
        fx, fy = x - 16 * math.cos(ang), y - 16 * math.sin(ang)
        ft = t * 14 + j * 3
        hh = (58 if f < 1 else 42) * (0.85 + 0.15 * math.sin(ft))
        st.put(J.glow(), fx, fy - 14, P.wzgorza + 0.0605, w=160, anchor=(0.5, 0.5), mode="add", alpha=0.55, shadow=None, tint=(1.0, 0.6, 0.3))
        for m in range(3):
            st.put(J.flame((int(ft) + m + j) % 8), fx + (m - 1) * 4, fy + 6, P.wzgorza + 0.0602 + 0.0002 * m, h=hh * (1 - 0.2 * m),
                   rot=10 * noise(ft, 800 + j * 3 + m, 7) - 12 * (f < 1), shadow=None)
    swiatlo(st, w, t, extra=(1.03, 0.97, 0.92))


def s_rana(st, w, t, T):
    """Strzała trafia Itsuse w ramię; lalka zatacza się i przyciska rękę."""
    w.sun_xy = (1080, 250)
    kam(st, t, 36, 600, 480, 2.1, 0.8, lens=1.85, shake=5.0 * (0.9 < t < 1.3))
    st.dof = 2.0
    kraj(st, t, w, gora_x=900, kul=False)
    hit = pr(t, 0.4, 0.5)
    stag = ease(pr(t, 0.9, 0.5))
    lean = -12 * stag + 3 * settle((t - 1.4) / 1.4, 1.5)
    lalka(st, t, "itsuse", 600, 280, flip=1, lean=lean, rece=(28 * stag, -10 * stag))  # dłoń przy brzuchu, ramię przyciśnięte
    # marker reżysera 20.11.2026: w oddali lecą płonące strzały, a Itsuse też dostaje płonącą
    for j in range(7):
        r = random.Random(960 + j)
        f = pr(t, r.uniform(0.0, 2.2), 1.1)
        if 0 < f < 1:
            x, y = lerp(1250, r.uniform(200, 700), f), lerp(r.uniform(160, 260), r.uniform(420, 470), f) - 60 * math.sin(math.pi * f)
            st.put(Z0.prop("strzala"), x, y, P.wzgorza + 0.05, w=70, anchor=(0.95, 0.5), rot=165, shadow=None, haze=0.2)
            plomien(st, t, x + 8, y, P.wzgorza + 0.0502, 22, seed=j)
    if hit < 1:
        ax, ay = punkt("itsuse", 600, 280, 196, 236, rot=lean)
        x, y = lerp(ax + 600, ax, hit), lerp(ay - 200, ay, hit)
        st.put(Z0.prop("strzala"), x, y, P.lalki + 0.013, w=118, anchor=(0.95, 0.5), rot=160, shadow=(2, 3, 3, 0.4))
        plomien(st, t, x + 20, y - 7, P.lalki + 0.014, 34, seed=31)
    else:
        strzala_w_ramieniu(st, "itsuse", 600, 280, rot=lean, ogien=True, t=t)
    podpis(w, t, "AŁA!…", 470, 352, 0.95, 1.8)
    podpis(w, t, "AAA!", 500, 350, 5.2, 2.0)  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): Itsuse krzyczy z bólu
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(1.03, 0.97, 0.92))


def s_pod_slonce(st, w, t, T):
    """Ranny Itsuse wskazuje słońce nad górami; Iwarebiko odwraca się ku słońcu i opuszcza łuk."""
    k = ease(t / T)
    w.sun_xy = (lerp(1010, 975, k), lerp(262, 236, k) + 4 * math.sin(t * 1.1))  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): słońce w kadrze i powoli się podnosi
    kam(st, t, 37, lerp(600, 660, ease(t / T)), 450, 1.4, 0.8)
    st.dof = 1.2
    kraj(st, t, w, gora_x=900, tint=(1.04, 0.97, 0.9))
    point = ease(pr(t, 0.8, 1.0))
    lalka(st, t, "itsuse", 560, 280, flip=1, lean=-6 + 3 * point, rece=(130 * point, 60))
    strzala_w_ramieniu(st, "itsuse", 560, 280, rot=-6 + 3 * point, ogien=True, t=t)  # marker reżysera 20.11.2026: „pali się ta strzała”
    low = ease(pr(t, 4.6, 1.4))
    zwrot = -math.cos(math.pi * ease(pr(t, 1.9, 0.5)))  # # uwagi i markery reżysera 18.11.2026 (Studio, projekt EN): od początku patrzy w lewo, przy geście Itsuse zwraca się ku słońcu
    lalka(st, t, "iwarebiko", 380, 290, flip=zwrot, rece=(70 * (1 - low) + 8, 0), trzyma=LUK(290), lean=2 * low)
    swiatlo(st, w, t, extra=(1.04, 0.96, 0.9))
