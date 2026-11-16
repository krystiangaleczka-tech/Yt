"""Świat filmu „Pierwszy cesarz”: stan sceny w każdym ujęciu, lalki, rekwizyty i trzy scenografie (kraj, sala, morze).

Stan świata liczy się z kamieni milowych rozpiski (`po("mur")` = po ujęciu o kluczu „mur”), a nie z numerów ujęć —
dopisanie ujęcia niczego nie przesuwa. Ujęcie dostaje stan z początku, zmienia go w czasie (swoje wydarzenie)
i woła `swiat()`, `sala()` albo `morze()`; te rysują zawsze tę samą scenografię i te same lalki.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))

import zestaw as Z  # noqa: E402
from dane import ujecia  # noqa: E402
from papier import CX, CY, H, W, Cam, back, clamp, ease, ease_out, noise, settle  # noqa: E402

P = Z.P
KOL = [u[2] for u in ujecia()]  # klucze ujęć w kolejności filmu
I = {k: n for n, k in enumerate(KOL)}

# ---------- rozmieszczenie na scenie (kadr wzorcowy) ----------
PODBITE = ["han", "zhao", "wei", "chu", "yan", "qi"]  # kolejność podboju: 230–221 p.n.e.
BAN = {  # chorągiew: (x, plan, wysokość)
    "qin": (140, 0.615, 186), "han": (566, 0.625, 178), "zhao": (682, 0.61, 166), "wei": (798, 0.625, 180),
    "chu": (914, 0.61, 172), "yan": (1030, 0.625, 178), "qi": (1150, 0.615, 184)}
EMP = (300, 708, 352)  # cesarz: x, linia stóp (za rampą), wysokość
SMOKI = ((166, 0.765), (432, 0.775))  # dwie chorągwie ze smokiem za cesarzem: x, plan
STOL = (640, 738, 350)  # stół pisarzy: x, dół, szerokość
ZWOJ_BLAT = (0.67, 0.255)  # zwój bambusowy na blacie (ułamki szerokości i wysokości rysunku stołu)
ZWOJ_ROT = 3.5  # zwój leży równolegle do tylnej krawędzi stołu (marker reżysera 16.11, ujęcie 47)
URNA = (1092, 704, 150)  # trójnóg z brązu: x, dół, wysokość
POSAG = (1238, 268)  # posąg z brązu: x, wysokość (reżyser 15.11: „troszkę większy”)
KOPIEC = (1316, 602, 580)  # kopiec grobowca: x, dół, szerokość
PALAC = (250, 240)  # pałac: x, szerokość
RZEDY = [  # gliniana armia: plan, pasmo ziemi przed rzędem, wysokość, pierwszy x, odstęp, liczba
    (0.60, "droga", 92, 452, 61, 14), (0.70, "przod", 128, 478, 86, 10), (0.79, None, 178, 548, 114, 7)]
TRON = (380, 646)  # sala: król na podwyższeniu (x, linia stóp)
KOLUMNA = 700  # sala: kolumna, dookoła której ucieka król
MALY = 205  # wysokość małej lalki (Zheng jako chłopiec, Huhai)


ZAPAD = [0.0]  # o ile niżej stoją wozy, jeźdźcy i wojska, kiedy droga dopiero się wysuwa (zmiana dekoracji)


class Stan(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def stan(i):
    """Stan świata na początku ujęcia i (od 0) — co już stoi, co padło, co zgasło (księga świata)."""
    po = lambda k: i > I[k]
    f = lambda cond: 1.0 if cond else 0.0
    noc = po("zmierzch") and not po("cisza")
    dwor = po("pismo") and not po("zmierzch")
    return Stan(
        sun=f(not noc), sun_y=96.0, moon=f(noc), noc=f(noc), clouds=[1.0, 1.0, 1.0], far=1.0, land=1.0, mid=1.0, city=1.0,
        bridge=1.0, trees=[1.0, 1.0], road=1.0, front=1.0, floor=1.0,
        up={k: f(po("choragwie")) for k in BAN},
        fall={"han": f(po("han")), "zhao": f(po("zhao")), "wei": f(po("wei")), "chu": f(po("chu_yan")), "yan": f(po("chu_yan")),
              "qi": f(po("qi"))},
        black={k: f(po("czarne")) for k in PODBITE},
        bfall={k: f(po("powstanie") if k in ("han", "zhao", "wei") else po("upadek")) for k in PODBITE},
        qin_fall=f(po("upadek")), chwiej={},
        emp=f(po("dorosl") and not po("koniec")), flip=1.0, lean=0.0, sink=0.0, lift=0.0,
        smoki=[f(po("cesarz") and not po("upadek"))] * 2, smoki_fall=0.0,
        urna=f(po("posagi") and not po("zmierzch")),
        dwor=f(dwor), ksiega=f(dwor), pisze=f(I["pismo"] < i <= I["miara"]),
        moneta=f(po("moneta") and not po("zmierzch")), moneta_x=1.0, moneta_lez=1.0, moneta_chw=0.0, moneta_skok=0.0,
        waga=f(po("miara") and not po("zmierzch")), odwaznik=f(po("miara") and not po("zmierzch")), waga_rot=0.0,
        zwoj=f(po("pismo") and not po("ksiegi")), zwoj_lot=0.0,
        uczony=f(po("ksiegi") and not po("uczeni")), uczony_lean=0.0, ogien=0.0,
        mur=f(po("mur")), armia=f(po("armia") and not po("podroz")), armia_t=None,  # armia zapada się na początku podróży
        posag=f(po("posagi") and not po("upadek")), posag_fall=0.0,
        # kanały stoją od wykopania do ujęcia „pismo” (tam zwijają się przy zmianie dekoracji); reżyser 15.11: „zaś ten kanał
        # z wodą nie wiem, co tu robi” w aktach 7–8
        kanal=f(po("kanal") and not po("pismo")), kanal2=f(po("kanal2") and not po("pismo")),
        urzednicy=f(po("prowincje") and not po("powstanie")),
        stela=f(po("stela")), palac=f(po("palac") and not po("upadek")), kopiec=f(po("kopiec")),
        powoz=730.0 if po("podroz") and not po("ryby") else None, zaslona=f(po("spisek") and not po("ryby")),
        znaleziony=f(po("studnia")), sosna=f(po("grobowiec")),
        zawieszki=[], woz=None, jezdziec=None, wlocznie=None, build=None,
        galaz=1.0, kopiec_drz=0.0, bez_rzeczy=0.0, cyklopi=f(po("xufu")), oczy_x=0.0,
        waga_belka=-6.6 if po("miara") else None, waga_szale=(0.0, 0.0), odwaznik_szala=f(po("miara")))  # odważnik został w szali


# ---------- kamera, światło, czas ----------

def lerp(a, b, k):
    return a + (b - a) * k


def pr(t, a, d):
    """Postęp 0..1 wydarzenia, które zaczyna się w chwili a i trwa d sekund."""
    return clamp((t - a) / d)


def kam(st, t, i, x, y, m, pf, lens=None, truck=0.6, drift=1.0, shake=0.0):
    """Kamera ujęcia + lekkie pływanie (dalsze plany płyną wolniej, więc scena ma głębię także w bezruchu)."""
    r = random.Random(int(t * 24) + i)
    T = st.__dict__.get("T", 6.0)
    side = 1 if i % 2 == 0 else -1  # kierunek przejazdu zmienia się co ujęcie
    slide = side * 34 * drift * (min(t, T) / max(T, 0.1) - 0.5) / max(1.0, m ** 0.5)  # wózek jedzie bokiem: bliższe plany mijają dalsze
    st.cam = Cam(x, y, m, pf, lens, truck, dx=slide + 9 * drift * noise(t, 91 + i, 0.12) + 2.6 * drift * noise(t, 93 + i, 0.3)
                 + shake * r.uniform(-1, 1),
                 dy=1.8 * drift * noise(t, 92 + i, 0.19) + shake * r.uniform(-1, 1), trucky=0.0)
    st.focus = pf


def swiatlo(st, w, t, extra=(1.0, 1.0, 1.0), dim=1.0):
    """Dzień albo noc (w.noc 0..1) + migotanie lampy sceny."""
    n = w.noc
    g = (lerp(1.0, 0.70, n), lerp(1.0, 0.78, n), 1.0)
    st.grade = tuple(a * b for a, b in zip(g, extra))
    st.dim = dim * (1 + 0.012 * noise(t, 5, 5.0)) * lerp(1.0, 0.94, n)


# ---------- lalki i rekwizyty ----------

def lalka(st, t, key, x, h=292, k=1.0, y=708, p=None, flip=1.0, lean=0.0, sink=0.0, lift=0.0, seed=None, tint=None):
    """Lalka na patyczku: wysuwa się zza rampy (k), opada pod nią (sink), obraca się (flip: 1 w prawo, -1 w lewo)."""
    if k <= 0 or sink >= 1:
        return
    seed = sum(map(ord, key)) if seed is None else seed
    yy = y + (1 - back(k, 1.2)) * h * 1.1 + ease(sink) * h * 1.12 - lift
    rot = 0.5 * noise(t, seed, 0.45) + lean + settle((k - 0.75) / 0.25 if k < 1 else 0, 1.5, 3)
    flip = math.copysign(max(abs(flip), 0.035), flip)  # bokiem widać jeszcze grubość tektury
    st.put(Z.lalka(key), x, yy, P.lalki + 0.01 if p is None else p, h=h, anchor=(0.45, 1.0), rot=rot, sx=flip, tint=tint)


def choragiew(st, t, k, up, fall=0.0, czarna=False, wob=0.0):
    if up <= 0 or fall >= 1:
        return
    x, p, h = BAN[k]
    spr = Z.banner("qin" if czarna or k == "qin" else k)
    y = Z.ground("droga", x) + 14 + (1 - back(up, 1.5)) * h * 1.15
    seed = sum(map(ord, k)) + (50 if czarna else 0)
    rot = 1.0 * noise(t, seed, 0.45) + settle((up - 0.7) / 0.3 if up < 1 else 0, 2, 5) + wob
    if fall > 0:  # drzewce pęka przy ziemi: chorągiew kładzie się ku wschodowi, odbija i zsuwa za wzgórze
        rot += 86 * min(1.0, fall / 0.55) ** 2.4 - 7 * settle((fall - 0.55) / 0.3, 1.5)
        y += 80 * ease((fall - 0.72) / 0.28)
    st.put(spr, x, y, p, h=h, anchor=(0.07, 1.0), rot=rot)


def cesarz(st, t, w):
    if w.emp <= 0 or w.sink >= 1:
        return
    x, y, h = EMP
    yy = y + (1 - back(w.emp, 1.2)) * h * 1.08 + ease(w.sink) * h * 1.1 - w.lift
    rot = 0.45 * noise(t, 7, 0.4) + w.lean + settle((w.emp - 0.75) / 0.25 if w.emp < 1 else 0, 1.5, 3) - 9 * ease(w.sink / 0.35)
    st.put(Z.S("emperor"), x, yy, P.lalki, h=h, anchor=(0.42, 1.0), rot=rot, sx=w.flip)
    if w.get("oczy_x", 0.0) > 0:  # martwy: X na oczach (reżyser 15.11), jadą razem z głową lalki
        c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for dx, dy, hh in ((6.6, -312.0, 13), (16.0, -313.0, 10)):
            dx *= w.flip
            st.put(Z.prop("x_oko"), x + c * dx - s_ * dy, yy + s_ * dx + c * dy, P.lalki + 0.002, h=hh * w.oczy_x, anchor=(0.5, 0.5),
                   rot=rot, shadow=None)


def smoki(st, t, w):
    for n, ((x, p), k) in enumerate(zip(SMOKI, w.smoki)):
        f = clamp(w.smoki_fall * 1.4 - n * 0.4)
        if f >= 1:
            continue
        Z.hang(st, Z.S("palace_banner", 0.7), x, 118 + 760 * f * f, p, k, t, 60 + n, drop=560, sway=1.0, h=236, strings=(0.5,),
               string=f <= 0, rot0=(14 - 28 * n) * f)  # zerwana nitka: chorągiew spada i przekrzywia się


def mur(st, t, k):
    """Mur za granią góry i dalej za pasmem wzgórz: odcinki wysuwają się po kolei od zachodu. k = 0..1."""
    if k <= 0:
        return
    line = lambda x: (min(Z.ridge(x), Z.ground("dal", x) + 4), Z.ridge(x) < Z.ground("dal", x) + 4) \
        if Z.MF_X - 360 < x < Z.MF_X + 360 else (Z.ground("dal", x) + 4, False)
    xs = list(range(-10, 1300, 34))
    for n, x in enumerate(xs):
        gy, on_mountain = line(x)
        gy2 = line(x + 30)[0]
        pk = clamp(k * (len(xs) + 5) - n, 0, 4) / 4
        if pk <= 0:
            continue
        tower = n % 5 == 2
        spr = Z.wall("wieza" if tower else "mur")
        hh, up = (96, 46) if tower else (74, 15)
        pp = (P.gory if on_mountain else P.gory + 0.02) - 0.004
        rot = 0.0 if tower else clamp(math.degrees(math.atan2(gy2 - gy, 30)), -32, 32)
        st.put(spr, x, gy - up + (1 - back(pk, 1.4)) * (up + 70), pp, h=hh, anchor=(0.5, 0.0), rot=rot,
               haze=0.18, shadow=(3, 3, 5, 0.3), z=0.5 if tower else 0.0)


def jezdziec(st, t, x, p=0.645, h=100, k=1.0, flip=1.0):
    """Jeździec w galopie: łuk skoku i kołysanie zależą od przebytej drogi, nie od zegara."""
    ph = x / 34.0
    y = Z.ground("droga", x) + 8 - abs(math.sin(ph)) * 9 * k + ZAPAD[0]
    st.put(Z.S("rider", 0.6), x, y, p, h=h, rot=5 * math.sin(ph * 2 + 0.5) * k + 0.6 * noise(t, 81, 0.6), sx=flip)


def wlocznie(st, t, x, p=0.635, band="droga", h=124, n=2, flag=None, up=1.0, seed=0, lift=0.0):
    """Las włóczni idący za wzgórzem: widać groty, hełmy i proporce. x — prawy koniec kolumny."""
    for j in range(n):
        xx = x - j * 330 * h / 124
        ph = xx / 30.0
        spr = Z.spears(seed + j) if flag is None else Z.spears(seed + j, flag=flag)
        st.put(spr, xx, Z.ground(band, clamp(xx, -300, 1500)) + h * 0.5 - abs(math.sin(ph)) * 5 + (1 - back(up, 1.3)) * h + ZAPAD[0] - lift,
               p - j * 0.004, h=h, anchor=(1.0, 1.0), rot=0.8 * math.sin(ph * 0.7))


def woz(st, t, x, p=0.645, h=74, flip=1.0, sy=1.0, rot=0.0, ladunek=None, kon=True):
    """Wóz na drodze; ladunek — wycinek jadący na wozie (lalka, ryby, zasłona): (sprite, wysokość, przesunięcie x, y)
    albo lista takich wycinków. Wóz ciągnie koń z woźnicą na grzbiecie (wycinanka jeźdźca), dyszel sięga mu do boku."""
    ph = x / 21.0
    y = Z.ground("droga", clamp(x, -300, 1500)) + 10 - abs(math.sin(ph)) * 3.5 - 5 * max(0.0, math.sin(ph * 0.31)) ** 8 + ZAPAD[0]
    r = 1.6 * math.sin(ph * 0.9) + 0.5 * noise(t, 83, 0.7) + rot
    for spr, lh, dx, dy in ([ladunek] if isinstance(ladunek, tuple) else ladunek or []):
        st.put(spr, x + dx * flip, y - h * 0.62 + dy, p - 0.002, h=lh, rot=r * 1.5, sx=flip)
    st.put(Z.S("wagon", 0.6), x, y, p, h=h, rot=r, sx=flip, sy=sy)
    if kon:  # koń idzie stępa: kołysze się w rytm przebytej drogi, nie zegara
        s = h / 74.0
        hx = x + 66 * s * flip
        ph2 = hx / 30.0
        hy = Z.ground("droga", clamp(hx, -300, 1500)) + 8 * s - abs(math.sin(ph2)) * 4 * s + ZAPAD[0]
        st.put(Z.woznica(), hx, hy, p + 0.002, h=100 * s, rot=2.5 * math.sin(ph2 * 2 + 0.5) + 0.4 * noise(t, 82, 0.6), sx=flip)
    return y


def powoz(st, t, x, zaslona=0.0, h=84, p=0.645, cesarz=None, ryby=0.0):
    """Powóz cesarza: wóz z czarną chorągwią; zasłona opada na niego po śmierci cesarza.
    cesarz — lalka cesarza jadąca na powozie: (kąt przechyłu, przesunięcie w dół) albo None."""
    y = woz(st, t, x, p=p, h=h, ladunek=(Z.banner("qin"), 74, -34, 10))
    if cesarz is not None:  # cesarz stoi na powozie za skrzynią; kąt 90 = leży
        rot, dol = cesarz
        st.put(Z.S("emperor"), x + 14, y - h * 0.50 + dol, p - 0.0015, h=h * 0.95, anchor=(0.42, 1.0),
               rot=rot + 0.6 * noise(t, 84, 0.7))
    if zaslona > 0:  # ciemna płachta z frędzlem; reżyser 15.11: „minimalnie wyżej”
        top = y - h * 0.98 - (1 - ease_out(zaslona)) * 300
        st.put(Z.prop("zaslona"), x - 8, top, p + 0.002, w=h * 1.9, anchor=(0.5, 0.0), sy=0.7, shadow=(3, 4, 5, 0.4))
        if ryby > 0:  # solone ryby zjeżdżają na nitkach i układają się na płachcie (reżyser 15.11)
            for n, dx in enumerate((-52, -8, 36)):
                kk = clamp(ryby * 1.5 - n * 0.25)
                Z.hang(st, Z.prop("ryby"), x - 8 + dx, top - 26, p + 0.0025 + n * 0.0001, kk, t, 170 + n, drop=320, sway=0.4,
                       h=30, string=kk < 1, strings=(0.3, 0.7), shadow=(2, 3, 3, 0.35))


def urna(st, t, w, k):
    """Trójnóg z brązu z ogniem z bibuły (w.ogien)."""
    ux, uy, uh = URNA
    udown = (1 - back(k, 1.1)) * 300
    fy = uy - uh * 0.80 + udown  # wylot trójnogu
    if w.ogien > 0.02:
        ft = math.floor(t * 12) / 12  # ogień skacze poklatkowo, jak wycinany z bibuły
        for n in range(9):
            r = random.Random(500 + n)
            ox, sc = r.uniform(-40, 40), r.uniform(0.55, 1.0)
            hh = uh * 0.9 * sc * w.ogien * (0.8 + 0.3 * noise(ft, 600 + n, 9))
            if hh > 3:
                st.put(Z.flame(n), ux + ox, fy + 14, P.rekwizyty - 0.01 + n * 0.0008, h=hh, rot=9 * noise(ft, 700 + n, 7),
                       shadow=None, tint=(1.15, 1.1, 1.0))
        st.put(Z.glow(), ux, fy - 30, P.rekwizyty + 0.03, w=520 * min(1.3, w.ogien), anchor=(0.5, 0.5), mode="add",
               alpha=0.30 * min(1.0, w.ogien) * (0.85 + 0.15 * noise(ft, 9, 9)), shadow=None, tint=(1.0, 0.55, 0.25))
    st.put(Z.S("urn", 0.6), ux, uy + udown, P.rekwizyty, h=uh)
    return fy


def stol(st, t, w, k, sx=None, sw=None):
    """Niski stół z laki (stół pisarzy, stół z podarunkami). Zwraca funkcję punktu na blacie i przesunięcie w dół."""
    sx = STOL[0] if sx is None else sx
    sy, sw = STOL[1], sw or STOL[2]
    desk = Z.S("desk", 0.6)
    dh = sw * desk.h / desk.w
    top = sy - dh
    down = (1 - back(k, 1.1)) * 330
    on = lambda fx, fy: (sx - sw / 2 + fx * sw, top + fy * dh + down)
    st.put(desk, sx, sy + down, P.rekwizyty, w=sw)
    return on, down


WAGA_H = 104  # wysokość całej wagi w kadrze wzorcowym


def waga(st, t, w, bx, by, p):
    """Waga z czterech części: podstawa stoi nieruchomo (zjeżdża na nitce tylko na początku), belka kołysze się wokół osi,
    a każda szala wisi na swoim haku i buja się osobno (reżyser 15.11: „porusz osobno każdym odważnikiem”, „to ma stać
    nieruchomo”). w.waga_belka — kąt belki względem rysunku (None: jak na rysunku), w.waga_szale — wychylenia szal;
    w.odwaznik_szala — odważnik „斤” zjeżdżający do lewej szali (0..1)."""
    k = WAGA_H / 1016  # piksele kadru na piksel oryginału scale.png
    ys = by - ((1 - back(w.waga, 1.1)) * 470 if w.waga < 1 else 0.0)  # zjazd całości na nitce
    ax, ay = Z.WAGA_STOPA
    st.put(Z.waga_czesc("podstawa"), bx, ys, p, w=1536 * k, anchor=(ax / 1536, ay / 1024), shadow=(3, 5, 5, 0.42))
    if w.waga < 1:  # nitka trzyma wagę za czubek kolumny, dopóki nie stanie
        st.line([(bx - 10 * k, -220), (bx - 10 * k, ys - (ay - 12) * k)], p, width=1.1, color=(70, 56, 44), alpha=0.7, z=-0.5)
    ox_, oy_ = Z.WAGA_OS
    px, py = bx + (ox_ - ax) * k, ys + (oy_ - ay) * k  # oś belki w kadrze
    phi = w.get("waga_belka") or 0.0
    c, sn = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    st.put(Z.waga_czesc("belka"), px, py, p + 0.0004, w=1536 * k, anchor=(ox_ / 1536, oy_ / 1024), rot=phi, shadow=(3, 5, 5, 0.42))
    for n, nazwa in enumerate(("lewa", "prawa")):
        hx, hy = Z.WAGA_HAK[nazwa]
        dx, dy = (hx - ox_) * k, (hy - oy_) * k
        qx, qy = px + c * dx - sn * dy, py + sn * dx + c * dy  # hak po obrocie belki
        sz = w.get("waga_szale", (0.0, 0.0))[n]
        st.put(Z.waga_czesc(nazwa), qx, qy, p + 0.0008, w=1536 * k, anchor=(hx / 1536, hy / 1024), rot=sz, shadow=(3, 5, 5, 0.42))
        if nazwa == "lewa" and w.get("odwaznik_szala", 0.0) > 0:  # odważnik „斤” zjeżdża do lewej szali i jedzie z nią
            Z.hang(st, Z.weight(), qx - math.sin(math.radians(sz)) * 26, qy + 6, p + 0.0006, w.odwaznik_szala, t, 72, drop=300,
                   sway=0.0, h=26, rot0=sz, string=w.odwaznik_szala < 1, shadow=(2, 3, 3, 0.4))


def dwor(st, t, w):
    """Stół pisarzy z księgą, zwojem, monetami i wagą, klęczący pisarz, uczony i trójnóg z brązu."""
    k = w.dwor
    on = None
    if k > 0:
        on, down = stol(st, t, w, k)
        rzeczy = 1.0 - w.get("bez_rzeczy", 0.0)  # reżyser 15.11 (miara): zwoje i pieniądze zdjęte ze stołu, na nich miarka
        # pisarz klęczy z lewej, PRZED stołem (bliżej kamery): pędzel w jego dłoni sięga księgi na blacie, widać, że pisze
        # (reżyser 15.11: „żeby było widać, że on pisze, a nie że jest za tym stołem”)
        pis = w.pisze
        rot = 0.5 * noise(t, 21, 0.5) + pis * (1.8 * math.sin(t * 7.0) + 2.0)
        st.put(Z.S("scribe", 0.7), STOL[0] - 168 + pis * 3 * math.sin(t * 3.1), 676 + down * 1.25, P.rekwizyty + 0.014, h=200,
               anchor=(0.45, 1.0), rot=rot)
        if w.zwoj > 0 and w.zwoj_lot <= 0 and rzeczy > 0:  # zwój leży wzdłuż blatu (reżyser 15.11: „w tym kierunku”)
            # cały zwój leży NA blacie: wcześniej jego dalszy koniec wystawał poza tylną krawędź stołu i zwój wisiał
            # w powietrzu (reżyser 16.11, ujęcie 47); cień tuż pod nim, bo leży, a nie unosi się
            st.put(Z.S("bamboo", 0.5), *on(*ZWOJ_BLAT), P.rekwizyty + 0.004, w=104, anchor=(0.5, 0.5), rot=ZWOJ_ROT,
                   shadow=(2, 4, 4, 0.5))
        if w.ksiega > 0 and rzeczy > 0:
            lx, ly = on(0.20, 0.42)
            st.put(Z.S("ledger", 0.5), lx + (1 - ease_out(w.ksiega)) * 240, ly, P.rekwizyty + 0.006, w=150, anchor=(0.5, 0.5),
                   rot=4 - 14 * (1 - ease_out(w.ksiega)), shadow=(3, 5, 5, 0.4))
        if rzeczy > 0:
            st.put(Z.S("ink", 0.4), *on(0.42, 0.50), P.rekwizyty + 0.008, w=36, anchor=(0.5, 0.5), shadow=(2, 3, 4, 0.4))
            st.put(Z.S("coin_stack", 0.5), *on(0.47, 0.62), P.rekwizyty + 0.010, h=40, anchor=(0.5, 0.85), shadow=(3, 4, 4, 0.4))
        if w.moneta > 0 and rzeczy > 0:  # moneta wytacza się zza pisarza, toczy za kałamarzem i stosem, przewraca się
            # (reżyser 16.11: „nie może ten coin tak dziwnie animować”) — droga punktu styku z blatem; obrót wynika
            # z przebytej drogi (toczenie bez poślizgu), moneta stoi na blacie i jest ZA kałamarzem i stosem, bo toczy
            # się dalej od kamery niż one; w.moneta_lez — przewrócenie (0 stoi, 1 leży), w.moneta_chw — dygot po upadku
            roll, lez, chw = w.moneta_x, w.get("moneta_lez", 1.0), w.get("moneta_chw", 0.0)
            skok = w.get("moneta_skok", 0.0)  # podskok nad blat tuż przed położeniem się (reżyser 16.11), w pikselach
            (x0, y0), (x1, y1) = on(0.10, 0.25), on(0.60, 0.46)
            mx, my = lerp(x0, x1, roll), lerp(y0, y1, roll)
            r = 20.0  # promień monety w kadrze wzorcowym
            droga = math.hypot(x1 - x0, y1 - y0) * (1 - roll)
            st.put(Z.coin(), mx, my - r * (1 - lez) + 0.5 * r * lez - skok, P.rekwizyty + 0.007, h=2 * r, anchor=(0.5, 0.5),
                   rot=-math.degrees(droga / r) + 5 * chw, sy=1 - 0.5 * lez + 0.10 * abs(chw),
                   shadow=(3 + 0.3 * skok, 4 + 3 * (1 - lez) + skok, 4 + 0.3 * skok, 0.42))
        if rzeczy < 1:  # miarka i miara objętości zamiast zwojów i monet
            mk = 1 - rzeczy
            st.put(Z.prop("miarka"), *on(0.56, 0.66), P.rekwizyty + 0.012, w=150 * mk, anchor=(0.5, 0.5), rot=14,
                   shadow=(3, 5, 5, 0.42))
            st.put(Z.prop("sheng"), *on(0.42, 0.34), P.rekwizyty + 0.008, h=44 * mk, anchor=(0.5, 0.75), shadow=(3, 5, 5, 0.42))
        if w.waga > 0:  # waga zjeżdża na nitce na prawy róg blatu; stoi, a kołyszą się belka i szale
            bx, by = on(0.80, 0.40)
            waga(st, t, w, bx, by, P.rekwizyty + 0.012)
        if w.odwaznik > 0 and w.get("odwaznik_szala", 0.0) <= 0:
            bx, by = on(0.70, 0.52)
            Z.hang(st, Z.weight(), bx, by - 40, P.rekwizyty + 0.016, w.odwaznik, t, 71, drop=470, sway=0.2, h=40, shadow=(3, 5, 4, 0.42))
    if w.uczony > 0:  # uczony stoi między stołem a trójnogiem, twarzą do cesarza
        lalka(st, t, "uczony", 946, 292, w.uczony, flip=-1, lean=w.uczony_lean, seed=23)
    if w.urna > 0:
        fy = urna(st, t, w, w.urna)
        if w.zwoj_lot > 0 and on:  # zwój leci łukiem ze stołu do ognia, potem czernieje i zapada się
            f = w.zwoj_lot
            ax, ay = on(*ZWOJ_BLAT)  # startuje stąd, gdzie leżał, w tym samym rozmiarze i obrocie
            bx = ax + (URNA[0] - ax) * ease(min(f, 1.0))
            by = ay + (fy - 36 - ay) * min(f, 1.0) - 170 * math.sin(math.pi * min(f, 1.0))
            burn = ease((f - 1.0) / 0.9)
            c = 1 - 0.8 * burn
            if burn < 1:
                st.put(Z.S("bamboo", 0.5), bx, by + 70 * burn, P.rekwizyty - 0.004, w=104, anchor=(0.5, 0.5),
                       rot=ZWOJ_ROT + (254 - ZWOJ_ROT) * ease(min(f, 1.0)) + 6 * burn, tint=(c, c * 0.92, c * 0.85), shadow=(3, 5, 5, 0.4))


def armia(st, t, w):
    """Gliniani żołnierze: trzy rzędy, każdy żołnierz wysuwa się (albo zapada) we własnej chwili."""
    if w.armia <= 0 and w.armia_t is None:
        return
    lit = 1.0 if w.armia_t is None else clamp((w.armia_t - 0.8) / 3.0)
    st.put(Z.glow(), 860, 600, 0.81, w=1500, anchor=(0.5, 0.5), mode="add", alpha=0.16 * lit * w.noc, shadow=None,
           tint=(1.0, 0.62, 0.32))  # poświata pochodni nad armią (tylko nocą)
    for rn, (p, band, h, x0, step, n) in enumerate(RZEDY):
        for j in range(n):
            r = random.Random(900 + rn * 50 + j)
            x = x0 + j * step + r.uniform(-7, 7)
            hh = h * r.uniform(0.95, 1.05)
            gy = (Z.ground(band, x) + 20) if band else 714
            if w.armia_t is None:
                k = 1.0
            else:  # rząd dalszy pierwszy; ostatni żołnierz pierwszego rzędu spóźnia się
                late = 6.2 if (rn == 2 and j == n - 1) else 0.0
                k = clamp((w.armia_t - (0.7 + rn * 1.15 + r.uniform(0, 1.0) + late)) / 0.8)
            if w.armia_t is None and w.armia < 1:  # zapadanie się: każdy żołnierz w swojej chwili
                k = clamp(w.armia * 1.6 - r.uniform(0, 0.6))
            if k <= 0:
                continue
            tint = (lerp(1.0, 1.34, w.noc), lerp(1.0, 1.2, w.noc), 1.0)  # nocą glina w ciepłym świetle pochodni
            st.put(Z.soldier((rn * 5 + j) % 6), x, gy + (1 - back(k, 1.5)) * hh * 1.15, p, h=hh,
                   rot=0.4 * noise(t, 950 + rn * 20 + j, 0.4) + settle((k - 0.7) / 0.3 if k < 1 else 0, 1.5, 4), tint=tint)


def wstega(st, key, x0, x1, k, p=0.672, dy=20, band="droga", sy=1.0, blask=0.0):
    """Wstęga (kanał, rzeka rtęci) rozwijana od x0 do x1 wzdłuż pasma wzgórz. k = 0..1; blask > 0 — połysk (rtęć) nałożony addytywnie."""
    if k <= 0:
        return
    y0, y1 = Z.ground(band, x0) + dy, Z.ground(band, x1) + dy
    st.put(Z.ribbon(key), x0, y0, p, w=(x1 - x0), anchor=(0.0, 0.5), sx=max(0.02, ease_out(k)), sy=sy,
           rot=math.degrees(math.atan2(y1 - y0, x1 - x0)), shadow=None if blask else (2, 3, 4, 0.35),
           **({"mode": "add", "alpha": blask, "tint": (0.85, 0.9, 1.0)} if blask else {}))


def kraj_dodatki(st, t, w):
    """To, co cesarz dobudował: kanały z poletkami, urzędnicy w prowincjach, stela, pałac, kopiec, posąg."""
    for key, k, x0, x1 in (("kanal", w.kanal, 300, 760), ("kanal", w.kanal2, 790, 1250)):
        wstega(st, "brzeg", x0 - 14, x1 + 14, k, p=0.6715, dy=20, sy=1.0)  # nasyp z ziemi po obu stronach wody
        wstega(st, key, x0, x1, k, sy=1.15)
        if k > 0.05:  # woda płynie: połysk przesuwa się wzdłuż wstęgi
            wstega(st, key, x0, x1, k, p=0.6725, sy=1.15, blask=0.10 + 0.06 * math.sin(st.t * 2.3 + x0))
        for n in range(6):  # poletka wyskakują za rozwijającą się wstęgą
            fk = clamp(k * 8 - n - 1.5)
            x = x0 + (x1 - x0) * (n + 0.6) / 6.4
            if fk > 0:
                st.put(Z.prop("poletko"), x, Z.ground("droga", x) + 46 + (1 - back(fk, 1.6)) * 30, 0.674, w=62, shadow=(2, 2, 3, 0.3))
    if w.urzednicy:
        for n, kk in enumerate(PODBITE):
            x, p, _ = BAN[kk]
            k = w.urzednicy if isinstance(w.urzednicy, float) else w.urzednicy[n]
            lalka(st, t, "uczony" if n % 2 else "uczony2", x + 50, 104, k, y=Z.ground("droga", x + 50) + 12, p=p - 0.004,
                  flip=-1 if n % 2 else 1, seed=300 + n)
    if w.stela > 0:
        mg = Z.S("mountain_gold", 0.6)
        hh = 560 * mg.h / mg.w
        fx = min((0.3 + d * 0.02 for d in range(21)), key=mg.top)
        # duża stela (reżyser 15.11: „zrób ją większą”) wyrasta z grani i kołysze się, zanim stanie
        st.put(Z.prop("stela"), 1030 - 280 + fx * 560, 456 - hh + mg.top(fx) * hh + 30 + (1 - back(w.stela, 1.3)) * 120,
               P.gory_dal + 0.016, h=96, haze=0.12, rot=5 * settle((w.stela - 0.5) / 0.5 if w.stela < 1 else 0, 2.5, 1.0)
               + 6 * (1 - w.stela) * math.sin(st.t * 9))
    if w.palac > 0:
        st.put(Z.palace(), PALAC[0], Z.ground("dal", PALAC[0]) + 12 + (1 - w.palac) * 400, P.gory + 0.016, w=PALAC[1], haze=0.14)
    if w.kopiec > 0:
        kx, ky, kw = KOPIEC
        dr = w.get("kopiec_drz", 0.0)
        st.put(Z.mound(), kx + dr * 5 * noise(st.t, 610, 9.0), ky + (1 - back(w.kopiec, 1.05)) * 240 + dr * 3 * noise(st.t, 611, 11.0),
               P.miasto + 0.02, w=kw, haze=0.06, rot=dr * 0.8 * noise(st.t, 612, 8.0))
    if w.posag > 0 and w.posag_fall < 1:
        px, ph = POSAG
        f = w.posag_fall
        st.put(Z.giant(), px, Z.ground("droga", px) + 16 + (1 - back(w.posag, 1.1)) * ph * 1.1 + 200 * ease((f - 0.6) / 0.4), 0.60,
               h=ph, rot=80 * min(1.0, f / 0.6) ** 2.2)


def buduj(w):
    """Zmiana dekoracji na początku sceny: elementy, które stoją, wjeżdżają po kolei od nowa (niebo na nitkach, ziemia
    i budowle od dołu, chorągwie na końcu). w.build — sekundy od początku budowania; None — dekoracja już stoi."""
    b = w.get("build")
    if b is None:
        return
    for key, d in (("sun", 0.0), ("far", 0.1), ("land", 0.25), ("mid", 0.4), ("city", 0.6), ("road", 0.75), ("bridge", 0.85),
                   ("front", 1.0), ("kopiec", 0.7), ("palac", 0.7), ("kanal", 1.1), ("kanal2", 1.2)):
        w[key] = min(w[key], pr(b, d, 0.7)) if w[key] > 0 else 0.0
    w.clouds = [min(c, pr(b, 0.15 + 0.25 * i, 0.9)) for i, c in enumerate(w.clouds)]
    w.trees = [min(w.trees[0], pr(b, 1.25, 0.7)), min(w.trees[1], pr(b, 1.1, 0.7))]
    if w.mur > 0:
        w.mur = min(w.mur, pr(b, 0.5, 1.4))
    for n, k in enumerate(BAN):
        w.up[k] = min(w.up[k], pr(b, 1.3 + 0.1 * n, 0.55))
        if k in w.black:
            w.black[k] = min(w.black[k], pr(b, 1.3 + 0.1 * n, 0.55))
    if w.emp > 0:
        w.emp = min(w.emp, pr(b, 1.6, 0.9))
    if isinstance(w.urzednicy, float) and w.urzednicy > 0:
        w.urzednicy = [pr(b, 1.8 + 0.1 * n, 0.5) for n in range(6)]


def ptaki(st, t, w, seed=0):
    """Klucz ptaków z papieru przelatuje nad sceną (tylko za dnia)."""
    if w.noc > 0.5 or w.sun <= 0:
        return
    r = random.Random(seed)
    x0, y0, v = r.uniform(-300, -100), r.uniform(150, 260), r.uniform(70, 110)
    for j in range(5):
        x = x0 + v * t - (j % 3) * 34 - j * 20
        y = y0 + abs(j - 2) * 16 + 6 * math.sin(t * 1.3 + j)
        if -60 < x < 1340:
            st.put(Z.bird(int(t * 6 + j * 1.7) % 2), x, y, 0.26 + 0.004 * j, w=26 - j * 1.5, anchor=(0.5, 0.5), shadow=(2, 3, 3, 0.2), haze=0.2)


def wedrowcy(st, t, w):
    """Ludzie na moście i drodze (tło żyje); w czasie wojny i nocą ich nie ma."""
    if w.noc > 0.5 or w.wlocznie is not None or w.bridge < 1:
        return
    for j, (key, x0, v, band) in enumerate((("a", 470, 9, "most"), ("c", 760, -7, "most"), ("b", 300, 11, "droga"))):
        x = x0 + v * t
        if band == "most":
            spr_y = 648 - 450 * Z.S("bridge", 0.6).h / Z.S("bridge", 0.6).w * (1 - Z.S("bridge", 0.6).top(clamp((x - 375) / 450))) + 6
            p = P.most + 0.002
        else:
            spr_y, p = Z.ground("droga", x) + 10, P.droga + 0.01
        st.put(Z.walker(key), x, spr_y - abs(math.sin(x / 4.0)) * 1.5, p, h=34, sx=1 if v > 0 else -1, shadow=(1, 2, 2, 0.3))


def kulisy(st, t, w, dol=True):
    """Przedplan: gałąź sosny zwisa z góry kadru, kępy trzcin przy rampie — nieostre, mijają kamerę najszybciej."""
    if w.get("galaz", 1.0) > 0:
        st.put(Z.bough(-1), -60, -40, 0.95, w=520, anchor=(0.0, 0.0), rot=1.5 * noise(t, 301, 0.3), blur=4.0, shadow=(8, 12, 16, 0.35),
               tint=(0.72, 0.74, 0.70))
    if dol:
        st.put(Z.reeds(1), 1270, 770, 0.94, h=230, rot=1.2 * noise(t, 302, 0.4), blur=3.5, shadow=None, tint=(0.62, 0.66, 0.6))
        st.put(Z.reeds(2), 40, 776, 0.93, h=190, rot=1.0 * noise(t, 303, 0.4), blur=3.0, shadow=None, tint=(0.62, 0.66, 0.6))


def swiat(st, t, w):
    """Scenografia „kraj”: góry, miasto, droga, chorągwie, mur — i wszystko, co na niej w tej chwili stoi."""
    buduj(w)
    # przy zmianie dekoracji wozy, jeźdźcy i wojska wysuwają się razem z drogą (zza pasma wzgórz), nie wiszą w powietrzu
    ZAPAD[0] = 0.0 if w.get("build") is None else (1 - back(pr(w.build, 0.95, 0.6), 1.3)) * 170
    Z.plan(st, t, sun=w.sun, clouds=w.clouds, far=w.far, land=w.land, mid=w.mid, city=w.city, bridge=w.bridge,
           trees=w.trees, road=w.road, front=w.front, floor=w.floor, sun_xy=(905, w.sun_y), night=w.noc)
    ksiezyc(st, t, w.moon)
    mur(st, t, w.mur)
    kraj_dodatki(st, t, w)
    for k in BAN:
        if k == "qin":
            choragiew(st, t, k, w.up[k], w.qin_fall, wob=w.chwiej.get(k, 0.0))
            continue
        choragiew(st, t, k, w.up[k], w.fall[k], wob=w.chwiej.get(k, 0.0))
        choragiew(st, t, k, w.black[k], w.bfall[k], czarna=True, wob=w.chwiej.get("czarna-" + k, 0.0))
    if w.wlocznie is not None:
        wlocznie(st, t, w.wlocznie)
    if w.jezdziec is not None:
        jezdziec(st, t, *w.jezdziec) if isinstance(w.jezdziec, tuple) else jezdziec(st, t, w.jezdziec)
    if w.woz is not None:
        woz(st, t, w.woz)
    if w.powoz is not None:
        powoz(st, t, w.powoz, w.zaslona, ryby=w.get("ryby", 0.0))
    if w.znaleziony > 0:  # żołnierz wykopany przy studni i chłop, który go znalazł
        st.put(Z.prop("chlop"), 820, Z.ground("przod", 820) + 14, 0.70, h=120, rot=-6)
        st.put(Z.soldier(2), 912, Z.ground("przod", 912) + 20, 0.70, h=128)
    if w.sosna > 0:
        kx, ky, kw = KOPIEC
        dr = w.get("kopiec_drz", 0.0)
        st.put(Z.S("tree_right"), kx - 8 + dr * 5 * noise(st.t, 610, 9.0), ky - kw * 420 / 900 * 0.80 + 18 + (1 - back(w.sosna, 1.3)) * 110,
               P.miasto + 0.018, h=104, rot=dr * 2.5 * noise(st.t, 613, 8.0))
    ptaki(st, t, w, seed=int(st.seed))
    wedrowcy(st, t, w)
    armia(st, t, w)
    smoki(st, t, w)
    cesarz(st, t, w)
    dwor(st, t, w)
    zawieszki(st, t, w)
    kulisy(st, t, w, dol=w.dwor <= 0)


def ksiezyc(st, t, k, x=648, y=212):
    if k > 0:
        st.put(Z.glow(), x, y + 54 - (1 - back(k, 1.1)) * 480, P.slonce, w=560, anchor=(0.5, 0.5), mode="add", alpha=0.26 * ease(k),
               shadow=None, tint=(0.75, 0.85, 1.0), z=-1)
        Z.hang(st, Z.moon(), x, y, P.slonce, k, t, 2, drop=480, w=108, shadow=(5, 7, 9, 0.3))


def podpis(w, t, txt, x, y, t0, dur=2.8):
    """Tabliczka z imieniem nad postacią przy jej pierwszym pojawieniu się: zjeżdża na nitce w t0, po dur s odjeżdża w górę.
    (x, y) — środek górnej krawędzi tabliczki w kadrze wzorcowym, nad głową postaci."""
    w.zawieszki = list(w.zawieszki) + [(txt, x, y, pr(t, t0, 0.9) * (1 - pr(t, t0 + dur, 0.6)))]


def zawieszki(st, t, w):
    for txt, x, y, k in w.zawieszki:
        spr = Z.tag_zh(txt) if ord(txt[0]) > 0x2E80 else Z.tag(txt)
        Z.hang(st, spr, x, y, P.rekwizyty + 0.02, k, t, 90 + len(txt), drop=460, sway=1.6, h=44, shadow=(4, 6, 6, 0.4))


# ---------- sala tronowa ----------

def sala(st, t, w, okna=(1.0, 0.96, 0.86), lampy=(1.0, 1.0, 1.0), za_oknem=None, kolumna=True, tron=True):
    """Scenografia „sala”: ściana z oknami, kolumny, podwyższenie tronu. okna — barwa nieba za kratą;
    lampy — jasność trzech lamp; za_oknem — funkcja rysująca to, co widać przez okna (plan < 0.5)."""
    b = w.get("build")
    k = (lambda d, dur=0.7: pr(b, d, dur)) if b is not None else (lambda d, dur=0.7: 1.0)
    st.put(Z.sky(), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None, tint=okna)
    if za_oknem:
        za_oknem()
    if k(0.0) > 0:  # ściana zjeżdża z góry jak prospekt teatralny
        st.put(Z.hall_wall(), CX, 300 - (1 - back(k(0.0, 0.9), 1.05)) * 800, 0.5, w=2100, anchor=(0.5, 0.5), shadow=(0, 0, 14, 0.5))
    else:
        st.put(Z.black(), CX, CY, 0.49, w=2200, anchor=(0.5, 0.5), shadow=None, blur=0, tint=(0.12, 0.08, 0.07))
    for n, x in enumerate((40, 440, 840, 1240)):
        kk = k(0.5 + 0.15 * n)
        if kk > 0:
            st.put(Z.column(), x, 706 + (1 - back(kk, 1.2)) * 800, 0.6, h=770)
    for n, x in enumerate((240, 640, 1040)):  # latarnie wiszą między kolumnami
        Z.hang(st, Z.lantern(), x, 150, 0.62, k(1.0 + 0.15 * n), t, 140 + n, drop=420, sway=2.0, h=104, shadow=(6, 9, 10, 0.4))
    for n, x in enumerate((240, 640, 1040)):
        st.put(Z.glow(), x, 520, 0.61, w=420, anchor=(0.5, 0.5), mode="add", alpha=0.20 * lampy[n] * (0.9 + 0.1 * noise(t, 40 + n, 6)),
               shadow=None, tint=(1.0, 0.72, 0.4))
    if tron:
        Z.hang(st, Z.S("palace_banner", 0.7), TRON[0], 96, 0.74, k(1.4), t, 66, sway=0.5, h=300, strings=(0.5,))
        if k(1.2) > 0:
            st.put(Z.dais(), TRON[0], 704 + (1 - back(k(1.2), 1.3)) * 120, 0.795, w=340)
        for n, x in enumerate((TRON[0] - 200, TRON[0] + 200)):  # kadzielnice z brązu po obu stronach tronu
            kk = k(1.5 + 0.15 * n)
            if kk > 0:
                st.put(Z.S("urn", 0.6), x, 704 + (1 - back(kk, 1.3)) * 140, 0.79, h=96)
                smoke = 0.18 * kk * (0.8 + 0.2 * noise(t, 150 + n, 2))
                st.put(Z.glow(), x, 600 - 10 * math.sin(t * 0.7 + n), 0.789, w=120, anchor=(0.5, 0.5), mode="add", alpha=smoke, shadow=None,
                       tint=(0.9, 0.85, 0.75))
    if kolumna and k(0.9) > 0:
        st.put(Z.column(), KOLUMNA, 716 + (1 - back(k(0.9), 1.2)) * 800, P.lalki, h=790)
    st.put(Z.column(), -40, 760, 0.95, h=1000, blur=4.5, tint=(0.55, 0.45, 0.42), shadow=(10, 0, 18, 0.45))  # kulisa: bliska kolumna
    st.put(Z.stage_floor(), CX, 676, P.rampa, w=2100, anchor=(0.5, 0.0), shadow=(0, -7, 9, 0.45))
    zawieszki(st, t, w)
    st.grade, st.dim = (1.0, 0.93, 0.84), 0.96 * (1 + 0.012 * noise(t, 5, 5.0))


def urzednik(st, t, n, bow=0.0, lift=0.0, flip=-1.0, k=1.0):
    """Klęczący urzędnik w sali (n = 0, 1): wysuwa się (k), kłania się (bow) albo podnosi (lift)."""
    key, x, h = (("kleczy", 1010, 236), ("pisarz", 1168, 222))[n]
    lalka(st, t, key, x, h, k, y=700, flip=flip, lean=-bow if flip < 0 else bow, lift=lift, seed=400 + n)


# ---------- morze ----------

def morze(st, t, w, k=1.0, wyspa=1.0, wyspa_w=400):
    """Scenografia „morze”: papier nieba, wyspa na horyzoncie, cztery pasma fal kołysane w przeciwne strony."""
    n = w.noc
    st.put(Z.sky(), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None, tint=(1 - 0.62 * n, 1 - 0.54 * n, 1 - 0.28 * n))
    ksiezyc(st, t, w.moon, 420, 150)
    if wyspa > 0:
        wy = WYSPA_Y + (1 - back(wyspa, 1.2)) * wyspa_w * 0.62
        st.put(Z.S("mountain_gold", 0.6), 900, wy, 0.22, w=wyspa_w, haze=0.45,
               shadow=(4, 5, 8, 0.25), rot=1.5 * settle((wyspa - 0.6) / 0.4 if wyspa < 1 else 0, 1.5, 2))  # wyspa z górą (reżyser 15.11: większa)
        cyklopi(st, t, w, wy, wyspa_w)
    for i in range(4):
        kk = clamp(k * 2.2 - i * 0.4)
        if kk > 0:
            st.put(Z.waves(i), CX + (46 - i * 6) * math.sin(t * 0.9 + i * 1.9) * (1 if i % 2 else -1), fala(i, t) + (1 - back(kk, 1.2)) * 340,
                   FALE[i][0], w=2400, anchor=(0.5, 0.0), haze=0.3 - i * 0.09 if i < 3 else 0.0)
    st.put(Z.stage_floor(), CX, 676, P.rampa, w=2100, anchor=(0.5, 0.0), shadow=(0, -7, 9, 0.45))
    swiatlo(st, w, t)


FALE = [(0.30, 384), (0.45, 452), (0.60, 528), (0.75, 606)]  # pasma fal: plan, linia grzbietu
WYSPA_Y = 446  # dół wyspy (reżyser 15.11: „wyspa niżej”)


def cyklopi(st, t, w, wy, wyspa_w):
    """Jednoocy olbrzymi na stokach wyspy (reżyser 15.11: „narysuj cyklopów”). w.cyklopi — 0..1 wychodzą zza grani."""
    k = w.get("cyklopi", 0.0)
    if k <= 0:
        return
    mg = Z.S("mountain_gold", 0.6)
    hh = wyspa_w * mg.h / mg.w
    for n, fx in enumerate((0.36, 0.52, 0.66)):
        kk = clamp(k * 1.6 - n * 0.3)
        if kk <= 0:
            continue
        x = 900 + (fx - 0.5) * wyspa_w
        gy = wy - hh + mg.top(fx) * hh + 34
        h = (100, 114, 92)[n]
        st.put(Z.cyklop(n), x, gy + (1 - back(kk, 1.3)) * h * 1.1, 0.2205 + n * 0.0003, h=h, haze=0.25, shadow=(3, 4, 6, 0.25),
               rot=2.5 * math.sin(t * 1.3 + n * 2) + settle((kk - 0.7) / 0.3 if kk < 1 else 0, 1.5, 4))


def fala(i, t):
    return FALE[i][1] + 5 * math.sin(t * 1.3 + i * 1.1)


def dzonka(st, t, x, f, seed=0, flip=1):
    """Dżonka płynąca w głąb sceny: f = 0 (pierwsze pasmo fal, duża) … 1 (za ostatnim pasmem, mała). Pod koniec
    (f > 0,9) przechodzi za ostatnie pasmo fal i chowa się za jego grzbietem (reżyser 15.11: „skryj ich za tą falą”)."""
    f = clamp(f)
    p = lerp(0.74, 0.31, min(1.0, f / 0.9)) if f < 0.9 else 0.295
    y = lerp(FALE[3][1] + 4, FALE[0][1] - 2, min(1.0, f / 0.9)) + 20 + 5 * math.sin(t * 1.3 + seed) + 70 * ease((f - 0.9) / 0.1)
    st.put(Z.boat(), x, y, p, h=lerp(150, 34, min(1.0, f / 0.9)), rot=4 * math.sin(t * 1.1 + seed * 2.3), haze=0.35 * f, sx=flip)
