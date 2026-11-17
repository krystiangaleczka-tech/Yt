"""Ujęcia aktów 5–9: Wrona z gór Kumano, Złoty ptak, Pierwszy cesarz, Kronika i ziemia, Źródło słońca."""
import math
import random

import zestaw_jp as J
from papier import CX, CY, back, clamp, ease, ease_out, noise, settle
from scena import (FALE, P, STOPY, Z0, choragiewki, czubek_luku, gora_wyspy, iks, kam, kraj, lalka, lerp, lodz, mapa_scena,  # noqa: F401
                   morze, niebo_papier, podpis, poklad_lodzi, pr, punkt, rampa, slonce, swiatlo, ziemia, zawieszki)
from ujecia_a import nad
from ujecia_a import LUK, MIECZ, WYSPY_JP

SPEAR = lambda h: (Z0.prop("wlocznia"), h * 1.05, (0.5, 0.6), 0.0, False)  # zwykła włócznia myśliwego


def _wojsko(st, t, x, flag, p=None, band="blisko", h=150, up=1.0, seed=11):
    """Las włóczni z proporcami idący za pasmem wzgórz (x — prawy koniec kolumny)."""
    if up <= 0:
        return
    xx = clamp(x - 300, -300, 1500)
    st.put(Z0.spears(seed, flag=flag), x, ziemia(band, xx) + 70 - abs(math.sin(x / 30.0)) * 5 + (1 - back(up, 1.3)) * 150,
           (P.droga + 0.012) if p is None else p, h=h, anchor=(1.0, 1.0), rot=0.8 * math.sin(x / 40.0))


BIALE, CIEMNE = (238, 234, 222), (56, 40, 34)


# ---------- akt 5 · Wrona z gór Kumano ----------

KII = (1.05, 0.9, 0.82)  # wieczór przy Kii


ITSUSE_SMIERC = 2.4  # Itsuse kona: X na oczach; ten sam czas w efekty.ZDARZENIA (jęk z nagrania)


def s_itsuse(st, w, t, T):
    """Na łodzi ranny Itsuse słabnie, przechyla się, dostaje X na oczach (śmierć widać, wytyczne 1.11 i 1.20; przegląd
    17.11: znikał bez śmierci) i powoli opada pod burtę; Iwarebiko pochyla się nad nim."""
    kam(st, t, 38, 640, 470, lerp(1.45, 1.55, ease(t / T)), 0.75, lens=1.35)
    st.dof = 1.2
    morze(st, t, w, wyspy=[(220, 1, 360, 4, 1.0), (1100, 2, 460, 6, 1.0)], tint=KII)
    sk = 1 - ease(pr(t, 0.8, 0.9))
    x = 640
    for key, dx, lh, rc, extra in (("itsuse", 70, 150, (20, 60), "itsuse"), ("iwarebiko", -60, 155, (40, 0), None)):
        px, py, rot, p = poklad_lodzi(t, x, 3, 240, dx, lh, sink=sk, seed=2)
        if key == "itsuse":
            lalka(st, t, key, px, lh, y=py, p=p, flip=-1, lean=rot - 22 * ease(pr(t, 1.8, 1.6)), sink=pr(t, ITSUSE_SMIERC + 0.9, 2.4),
                  rece=rc, oczy_x=pr(t, ITSUSE_SMIERC, 0.35))
        else:
            lalka(st, t, key, px, lh, y=py, p=p, flip=1, lean=rot + 14 * ease(pr(t, 2.4, 1.2)), rece=(70 * ease(pr(t, 2.6, 1.0)), 0))
    lodz(st, t, x, 3, h=240, v=1, seed=2, sink=sk)
    swiatlo(st, w, t, extra=KII)


def s_burza(st, w, t, T):
    """Burza: fale rosną, łodzie podskakują, dwie przechylają się i znikają za falą."""
    w.sun = 0.0
    flash = max(settle((t - 1.0) / 0.5, 0.5, 1.0), settle((t - 3.3) / 0.5, 0.5, 1.0), 0.0)
    kam(st, t, 39, 640, 430, 1.08, 0.6, shake=4.0)
    st.dof = 0.6
    morze(st, t, w, burza=1.0, tint=(0.6, 0.64, 0.78), chmury_k=(1.0, 1.0, 1.0))
    for j, (x, b, d, key) in enumerate(((380, 1, 2.2, "brat2"), (880, 1, 3.0, "brat3"), (620, 2, 99.0, "iwarebiko"))):
        tip = ease(pr(t, d, 0.8))
        sink = ease(pr(t, d + 0.5, 1.2))
        lodz(st, t, x + 30 * math.sin(t * 1.3 + j), b, h=150 if b == 1 else 180, v=1, burza=1.0, seed=j, przechyl=38 * tip * (1 if j else -1),
             sink=sink, ladunek=[(key, 0, 110 if b == 1 else 128, (100 if key != "iwarebiko" else 60, 30))])
    if flash > 0:
        st.put(J.glow(), 640, 120, 0.2, w=2600, anchor=(0.5, 0.5), mode="add", alpha=0.6 * flash, shadow=None, tint=(0.8, 0.85, 1.0))
    swiatlo(st, w, t, extra=(0.72, 0.76, 0.9), dim=1 + 0.5 * flash)


def s_sam(st, w, t, T):
    """Zbliżenie: Iwarebiko sam na łodzi, za nim puste morze i ciemne chmury."""
    w.sun = 0.0
    kam(st, t, 40, 640, 470, lerp(1.9, 2.05, ease(t / T)), 0.75, lens=1.8)
    st.dof = 1.8
    morze(st, t, w, burza=0.2, tint=(0.66, 0.7, 0.8), kul=False)
    for n, x in enumerate((420, 760, 1000)):
        J.hang(st, J.krazek("chmura"), x, 140 + 30 * n, P.chmury + 0.02, 1.0, t, 560 + n, w=260, sway=1.0, haze=0.2)
    px, py, rot, p = poklad_lodzi(t, 640, 3, 240, 0, 160, seed=4, burza=0.2)
    lalka(st, t, "iwarebiko", px, 160, y=py, p=p, flip=1, lean=rot + 4 * math.sin(t * 0.7), rece=(10, 0))
    lodz(st, t, 640, 3, h=240, v=1, seed=4, burza=0.2)
    swiatlo(st, w, t, extra=(0.74, 0.78, 0.9))


def mgla(st, t, alpha=0.18):
    for n in range(3):
        st.put(J.glow(), CX + 300 * math.sin(t * 0.13 + n * 2), 560 - 40 * n, 0.6 + 0.08 * n, w=1600, anchor=(0.5, 0.5), sy=0.25, mode="add",
               alpha=alpha, shadow=None, tint=(0.9, 0.92, 0.95))


def s_las(st, w, t, T):
    """Zmiana dekoracji: wyrastają cedry Kumano, snuje się mgła; wojsko — wojownicy z włóczniami na przodzie, za nimi
    las włóczni z białymi proporcami — wchodzi w las (przegląd 17.11: były same włócznie, bez ludzi)."""
    kam(st, t, 41, 640, 420, lerp(1.02, 1.1, ease(t / T)), 0.66, truck=0.6)
    st.dof = 0.6
    kraj(st, t, w, cedry=1.0, sosny=(0.0, 0.0), tint=(0.92, 0.98, 0.94))
    marsz = ease(pr(t, 1.2, T - 1.2))
    _wojsko(st, t, lerp(-60, 420, marsz), BIALE, p=P.wzgorza + 0.045, band="przod", h=210, up=pr(t, 1.2, 0.6))
    _wojsko(st, t, lerp(-480, 0, marsz), BIALE, p=P.wzgorza + 0.044, band="przod", h=200, up=pr(t, 1.5, 0.6), seed=12)
    for n in range(6):  # wojownicy z włóczniami wchodzą w las zza lewej kulisy, każdy we własnym kroku (1.7)
        lalka(st, t, ("wojownik", "wojownik2")[n % 2], -110 - n * 105 + 560 * marsz, 220 - 6 * (n % 3), pr(t, 0.9 + 0.12 * n, 0.5), flip=1,
              rece=(15, 0), hop=6, seed=990 + n, trzyma=SPEAR(220))
    mgla(st, t, 0.2 * pr(t, 0.8, 1.0))
    swiatlo(st, w, t, extra=(0.92, 0.98, 0.95))


WOJ = [(170, "wojownik"), (300, "wojownik2"), (560, "wojownik"), (690, "wojownik2"), (1060, "wojownik"), (1190, "wojownik2")]
WOJ_TYL = [(240, "wojownik2"), (440, "wojownik"), (620, "wojownik2"), (880, "wojownik"), (980, "wojownik2"), (1130, "wojownik")]


def _lezacy(st, t, fall, rise_=None, dim=1.0):
    """Wojownicy w dwóch rzędach padają (fall) albo wstają (rise_) — każdy we własnej chwili (1.7). Padając, przez
    chwilę mają gwiazdki nad głową: zamroczenie, „padli jak zaczarowani” (słownik znaków 1.20)."""
    for row, lista in enumerate((WOJ_TYL, WOJ)):
        for n, (x, key) in enumerate(lista):
            r = random.Random(970 + n + 40 * (1 - row))
            side = 1 if n % 2 else -1
            d = r.uniform(0, 0.5) + 0.25 * (1 - row)
            f = ease(pr(fall, d, 0.5)) if rise_ is None else 1 - ease(pr(rise_, r.uniform(0, 0.55), 0.45))
            gw = pr(fall, d + 0.4, 0.3) * (1 - pr(fall, d + 1.9, 0.4)) if rise_ is None else 0.0
            hh = (240 + 20 * r.random()) if row else (196 + 14 * r.random())
            lalka(st, t, key, x, hh, flip=side, lean=side * 82 * f, sink=0.22 * f, rece=(20 + 40 * f, 0), seed=980 + n + 40 * (1 - row),
                  tint=(dim * (1 - 0.1 * (1 - row)),) * 3, trzyma=SPEAR(hh), y=STOPY - (0 if row else 34),
                  p=(P.lalki + 0.01) if row else (P.lalki - 0.02), gwiazdki=gw)


def s_niedzwiedz(st, w, t, T):
    """Spomiędzy cedrów wychodzi czarny niedźwiedź i znika; wojownicy przewracają się po kolei."""
    kam(st, t, 42, lerp(660, 700, ease(t / T)), 450, 1.15, 0.7)
    st.dof = 0.7
    kraj(st, t, w, cedry=1.0, sosny=(0.0, 0.0), tint=(0.88, 0.94, 0.9))
    bx = lerp(1150, 820, ease(pr(t, 0.6, 2.6)))
    ba = 1 - pr(t, 4.0, 1.0)
    if ba > 0:
        st.put(J.niedzwiedz(), bx, ziemia("blisko", bx) + 86 + 4 * abs(math.sin(bx / 18)), P.droga + 0.034, w=300, alpha=ba, sx=-1)
    _lezacy(st, t, pr(t, 4.4, 2.4))
    lalka(st, t, "iwarebiko", 430, 290, flip=1, lean=-82 * ease(pr(t, 5.2, 0.6)), sink=0.22 * ease(pr(t, 5.2, 0.6)), trzyma=LUK(290),
          gwiazdki=pr(t, 5.6, 0.3) * (1 - pr(t, 7.1, 0.4)))
    mgla(st, t, 0.16 + 0.1 * pr(t, 4.0, 1.0))
    swiatlo(st, w, t, extra=(0.88, 0.94, 0.9), dim=lerp(1.0, 0.8, pr(t, 4.0, 2.0)))


SPICH = (1020, 260)


def s_takakuraji(st, w, t, T):
    """Miecz zjeżdża z nieba przez dach spichlerza; Takakuraji chwyta go i niesie do leżącego Iwarebiko."""
    kam(st, t, 43, lerp(780, 700, ease(t / T)), 450, 1.2, 0.7)
    st.dof = 0.8
    kraj(st, t, w, cedry=1.0, sosny=(0.0, 0.0), tint=(0.86, 0.92, 0.88))
    x, hh = SPICH
    yb = ziemia("przod", x) + 40
    st.put(J.spichlerz(), x, yb, P.wzgorza + 0.06, h=hh)
    sd = pr(t, 0.5, 2.0)
    if sd > 0 and t < 3.2:  # miecz na nitce znika za dachem spichlerza
        J.hang(st, J.miecz_jp(True), x - 10, yb - hh * 0.75, P.wzgorza + 0.058, sd, t, 570, drop=700, sway=0.4, h=150)
        st.put(J.glow(), x - 10, yb - hh * 0.6, P.wzgorza + 0.059, w=260, anchor=(0.5, 0.5), mode="add", alpha=0.3 * sd, shadow=None)
    go = ease(pr(t, 4.0, T - 4.6))
    lalka(st, t, "takakuraji", lerp(960, 600, go), 270, pr(t, 3.0, 0.9), flip=-1, rece=(60, 0), trzyma=MIECZ(270, True), hop=6 * (0 < go < 1))
    _lezacy(st, t, 3.0, dim=0.85)
    lalka(st, t, "iwarebiko", 430, 290, flip=1, lean=-82, sink=0.22, trzyma=LUK(290))
    podpis(w, t, "Takakuraji", 880, nad(270), 3.6, 2.6)
    zawieszki(st, t, w)
    mgla(st, t, 0.22)
    swiatlo(st, w, t, extra=(0.88, 0.94, 0.9), dim=0.82)


def s_przebudzenie(st, w, t, T):
    """Iwarebiko podnosi się z mieczem, za nim wstają wojownicy, jeden po drugim; cienie lasu cofają się."""
    kam(st, t, 44, 640, 450, lerp(1.2, 1.12, ease(t / T)), 0.7)
    st.dof = 0.8
    light = ease(pr(t, 2.0, T - 3.0))
    kraj(st, t, w, cedry=1.0, sosny=(0.0, 0.0), tint=(lerp(0.86, 1.0, light), lerp(0.92, 1.0, light), lerp(0.88, 0.98, light)))
    up = ease(pr(t, 0.6, 1.4))
    lalka(st, t, "iwarebiko", 430, 290, flip=1, lean=-82 * (1 - up), sink=0.22 * (1 - up), rece=(160 * ease(pr(t, 2.2, 0.8)), 0),
          trzyma=MIECZ(290, True))
    lalka(st, t, "takakuraji", 620, 270, flip=-1, rece=(10, 0), lean=-6 * ease(pr(t, 2.4, 0.8)))
    _lezacy(st, t, 3.0, rise_=pr(t, 3.0, T - 3.6))
    mgla(st, t, 0.2 * (1 - light))
    swiatlo(st, w, t, dim=lerp(0.82, 1.0, light))


def s_wrona(st, w, t, T):
    """Nad górami przelatuje wielka czarna wrona, pod nią wojsko z białymi proporcami idzie przełęczą."""
    f = t / T
    cx = lerp(-80, 1420, f)
    kam(st, t, 45, lerp(420, 880, f), 400, 1.1, 0.6, truck=0.85)
    st.dof = 0.6
    kraj(st, t, w, cedry=0.6, sosny=(0.0, 1.0), kul=False)  # bez kulisy z gałęzią: zasłaniała lot wrony
    # wojsko przed wszystkimi rzędami cedrów (pasmo „przod”): lektor mówi o nim, więc musi być widać ludzi, nie same czubki włóczni
    _wojsko(st, t, cx - 120, BIALE, p=P.wzgorza + 0.045, band="przod", h=210)
    _wojsko(st, t, cx - 560, BIALE, p=P.wzgorza + 0.045, band="przod", h=210, seed=12)
    _wojsko(st, t, cx - 1000, BIALE, p=P.wzgorza + 0.044, band="przod", h=200, seed=13)
    st.put(J.wrona(int(t * 5) % 2), cx, 250 + 30 * math.sin(t * 1.6), 0.52, w=190, anchor=(0.5, 0.5), rot=-4 + 6 * math.sin(t * 1.6),
           shadow=(8, 12, 12, 0.3))
    podpis(w, t, "Yatagarasu", cx - 20, 120, 0.3 * T, 3.0)  # tabliczka leci razem z wroną
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_trzy_nogi(st, w, t, T):
    """Zbliżenie: wrona siada na gałęzi i składa skrzydła — ma trzy nogi."""
    kam(st, t, 46, 780, 380, 2.0, 0.8, lens=1.8)
    st.dof = 1.8
    kraj(st, t, w, cedry=0.6, sosny=(0.0, 1.0), kul=False)
    pts = [(1400, 360), (1100, 392), (900, 410), (720, 424)]
    st.line(pts, 0.8, width=16, color=(84, 60, 44), alpha=1.0, z=-0.2)
    for n, (x, y) in enumerate(((1180, 370), (1000, 384), (860, 396), (760, 404))):
        st.put(J.galazka(), x, y, 0.8, w=150, anchor=(0.1, 0.85), rot=-30 + 14 * n + 2 * noise(t, 590 + n, 0.5), sy=-1 if n % 2 else 1)
    land = pr(t, 0.2, 1.6)
    if land < 1:
        x, y = lerp(300, 820, ease_out(land)), lerp(200, 330, ease_out(land)) - 60 * math.sin(math.pi * land)
        st.put(J.wrona(int(t * 7) % 2), x, y, 0.81, w=230, anchor=(0.5, 0.5), shadow=(6, 8, 8, 0.3))
    else:
        fold = settle((t - 1.8) / 1.0, 1.2, 1.0)
        st.put(J.wrona(0, True), 820, 418, 0.81, w=230, anchor=(0.55, 0.88), rot=2 * fold + 1.5 * noise(t, 595, 0.6), shadow=(6, 8, 8, 0.3))
    swiatlo(st, w, t)


# ---------- akt 6 · Złoty ptak ----------

HILLS = [(330, 380), (760, 330), (1060, 300)]


def _proporce(st, t, ks):
    for n, ((x, wd), k) in enumerate(zip(HILLS, ks)):
        if k <= 0:
            continue
        top = gora_wyspy(J.wzgorek(n), x, x, 606, wd)
        Z0.rise(st, J.proporzec(n), x + 6, top + 26, P.miasto - 0.012 + 0.004 * n, k, t, 650 + n, h=130, wob=1.0)


def s_yamato(st, w, t, T):
    """Kotlina Yamato: w kręgu niebieskich gór wyrastają trzy wzgórza, na każdym staje proporzec innego wodza."""
    k = ease(t / T)
    kam(st, t, 47, 680, lerp(420, 400, k), lerp(1.0, 1.1, k), 0.56, truck=0.5)
    st.dof = 0.5
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0)
    _proporce(st, t, [pr(t, 2.2 + 0.6 * n, 0.6) for n in range(3)])
    swiatlo(st, w, t)


PULAPKA_BELKA = 7.2  # belka spada; te same czasy w efekty.ZDARZENIA (huk, X)


def s_pulapka(st, w, t, T):
    """Wódz zaprasza do chaty; brat go wydaje (tabliczka „PUŁAPKA!”); wódz wchodzi do chaty, z dachu spada belka
    pułapki, a nad chatą miga dwa razy czerwony X — wódz zginął we własnej pułapce (słownik znaków 1.20)."""
    kam(st, t, 48, lerp(560, 620, ease(t / T)), 470, 1.25, 0.75)
    st.dof = 0.9
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0)
    _proporce(st, t, (1.0, 1.0, 1.0))
    hx = 860
    hy = ziemia("przod", hx) + 70
    st.put(J.dom(), hx, hy, P.wzgorza + 0.06, h=300)
    inn = ease(pr(t, 6.2, 1.0))
    lalka(st, t, "wodz", lerp(760, hx, inn), 270, flip=-1, rece=(70 * (1 - inn) * abs(math.sin(t * 2)) + 20, 0), alpha=1 - pr(t, 6.9, 0.4),
          lean=-4)
    warn = ease(pr(t, 2.6, 0.8))
    lalka(st, t, "brat_wodza", 560, 250, pr(t, 1.8, 1.0), flip=-1 if t < 4.6 else math.cos(math.pi * ease(pr(t, 4.6, 0.5))) * -1,
          rece=(110 * warn, 0), lean=-6 * warn)
    lalka(st, t, "iwarebiko", 330, 290, flip=1, trzyma=LUK(290), rece=(20, 0), lean=-3 * warn)
    podpis(w, t, "PUŁAPKA!", 560, nad(250), 2.8, 2.0)
    zawieszki(st, t, w)
    iks(st, hx, hy - 170, t, PULAPKA_BELKA + 0.4, h=180)  # wódz zginął we własnej pułapce: X miga dwa razy
    drop = pr(t, PULAPKA_BELKA, 0.35)
    if drop > 0:
        st.put(J.belka(), hx, lerp(hy - 300, hy - 30, drop * drop), P.wzgorza + 0.061, w=120, anchor=(0.5, 1.0), rot=6 * (1 - drop))
        if drop >= 1:
            dust = pr(t, PULAPKA_BELKA + 0.35, 1.2)
            st.put(J.glow(), hx, hy - 40, P.wzgorza + 0.062, w=300 * (0.6 + dust), anchor=(0.5, 0.5), mode="add", alpha=0.25 * (1 - dust),
                   shadow=None, tint=(0.8, 0.65, 0.45))
    swiatlo(st, w, t)


def _grad(st, t, k, n=70):
    for j in range(n):
        r = random.Random(1100 + j)
        p = 0.3 + 0.6 * r.random()
        sp = r.uniform(380, 560)
        y = ((t * sp + r.uniform(0, 900)) % 900) - 120
        x = r.uniform(-100, 1400) - y * 0.15
        if r.random() < k:
            st.put(J.grad(), x, y, p, w=lerp(5, 13, p), anchor=(0.5, 0.5), shadow=None, alpha=0.9)


def s_bitwa(st, w, t, T):
    """Dwa lasy włóczni, po trzy rzędy, ścierają się na wzgórzach i pchają w tę i z powrotem; w chwili starcia mocny
    wstrząs; niebo ciemnieje, a papierowy grad gęstnieje do końca ujęcia (potęga i kulminacja, wytyczne 1.17, 1.23)."""
    w.noc = 0.45 * ease(pr(t, 2.0, 2.0))
    clash = pr(t, 3.0, 0.4)
    kam(st, t, 49, lerp(560, 760, ease(t / T)), 420, 1.08, 0.66, shake=3.0 * (clash > 0) + 6.0 * (3.0 < t < 3.5))
    st.dof = 0.6
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0, tint=(lerp(1, 0.8, w.noc), lerp(1, 0.84, w.noc), lerp(1, 0.95, w.noc)))
    _proporce(st, t, (1.0, 1.0, 1.0))
    sway = 30 * math.sin(t * 3.0) * clash  # pchnięcia w tę i z powrotem: bitwa długo się nie rozstrzyga
    adv = ease(pr(t, 1.0, 2.0))
    for n, (dx, seed, band, p, hh) in enumerate(((0, 11, "przod", P.wzgorza + 0.045, 210), (-260, 14, "srodek", P.miasto + 0.032, 120),
                                                 (-520, 15, "srodek", P.miasto + 0.031, 112))):
        _wojsko(st, t, lerp(200, 640, adv) + dx + sway * hh / 210, BIALE, p=p, band=band, h=hh, up=pr(t, 1.0 + 0.25 * n, 0.5), seed=seed)
    for n, (dx, seed, band, p, hh) in enumerate(((0, 22, "przod", P.wzgorza + 0.046, 210), (260, 24, "srodek", P.miasto + 0.033, 120),
                                                 (520, 26, "srodek", P.miasto + 0.0325, 112))):
        up = pr(t, 1.0 + 0.25 * n, 0.5)
        if up > 0:
            st.put(Z0.spears(seed, flag=CIEMNE), lerp(1500, 1080, adv) + dx - sway * hh / 210,
                   ziemia(band, 900 + dx) + (80 if band == "przod" else 66) + (1 - back(up, 1.3)) * 200, p, h=hh, anchor=(0.0, 1.0),
                   sx=-1, rot=0.8 * math.sin(t + n))
    _grad(st, t, pr(t, 2.6, T - 2.6), n=120)  # grad gęstnieje do końca ujęcia (1.23)
    swiatlo(st, w, t, extra=(0.86, 0.88, 0.96))


def _iw_z_lukiem(st, t, x=420, rece=55, lean=0.0):
    h = 300
    hand = lalka(st, t, "iwarebiko", x, h, flip=1, rece=(rece, 0), trzyma=LUK(h), lean=lean)
    return czubek_luku(hand, h * 1.12, lean + 0.5 * noise(t, sum(map(ord, "iwarebiko")), 0.45), 1.0) if hand else (x, 300)


def s_ptak(st, w, t, T):
    """Z chmur zlatuje złoty ptak i siada na czubku łuku Iwarebiko; ptak rozbłyskuje."""
    w.noc = 0.45
    k = ease(t / T)
    kam(st, t, 50, lerp(520, 480, k), 380, lerp(1.4, 1.6, k), 0.8)
    st.dof = 1.2
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0, tint=(0.8, 0.84, 0.95))
    _grad(st, t, 0.5 * (1 - pr(t, 2.0, 1.0)), n=40)
    tip = _iw_z_lukiem(st, t)
    land = pr(t, 0.4, 2.4)
    glow = ease(pr(t, 2.6, 1.6))
    if land < 1:
        x, y = lerp(1250, tip[0], ease_out(land)), lerp(80, tip[1] - 30, ease_out(land)) - 80 * math.sin(math.pi * land)
        st.put(J.zloty_ptak(int(t * 7) % 2), x, y, 0.815, w=170, anchor=(0.5, 0.5), sx=-1, shadow=(6, 8, 8, 0.3))
    else:
        st.put(J.zloty_ptak(0, True), tip[0], tip[1] + 6, 0.815, w=170, anchor=(0.6, 0.97), sx=-1, shadow=(6, 8, 8, 0.3))
    if glow > 0:
        for n, (wd, a) in enumerate(((260, 0.55), (700, 0.35), (1600, 0.2))):
            st.put(J.glow(), tip[0], tip[1] - 30, 0.816 + 0.001 * n, w=wd * (0.8 + 0.2 * glow), anchor=(0.5, 0.5), mode="add",
                   alpha=a * glow * (0.9 + 0.1 * noise(t, 600 + n, 6)), shadow=None, tint=(1.0, 0.85, 0.45))
    swiatlo(st, w, t, extra=(0.84, 0.86, 0.95), dim=1 + 0.25 * glow)


def s_blysk(st, w, t, T):
    """Błysk: ciemne włócznie chwieją się i cofają za wzgórze."""
    w.noc = 0.45
    fl = settle(t / 0.9, 0.5, 1.0) if t < 0.9 else 0.0
    kam(st, t, 51, 760, 420, 1.15, 0.66, shake=6.0 * (t < 0.8))
    st.dof = 0.6
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0, tint=(0.82, 0.86, 0.96))
    back_ = ease(pr(t, 0.4, 1.4))
    st.put(Z0.spears(22, flag=CIEMNE), 1080 + 260 * back_, ziemia("przod", 900) + 80 + 160 * back_, P.wzgorza + 0.046, h=210, anchor=(0.0, 1.0),
           sx=-1, rot=8 * math.sin(t * 9) * (1 - back_))
    _wojsko(st, t, 700, BIALE, p=P.wzgorza + 0.045, band="przod", h=210)
    tip = _iw_z_lukiem(st, t, x=330)
    st.put(J.zloty_ptak(0, True), tip[0], tip[1] + 6, 0.815, w=170, anchor=(0.6, 0.97), sx=-1)
    st.put(J.glow(), tip[0], tip[1], 0.9, w=3000, anchor=(0.5, 0.5), mode="add", alpha=0.85 * max(fl, 0.25), shadow=None, tint=(1.0, 0.92, 0.7))
    swiatlo(st, w, t, extra=(0.86, 0.88, 0.96), dim=1 + 0.6 * max(fl, 0))


def s_order(st, w, t, T):
    """Detal: na nitce zjeżdża złoty order z ptakiem i kołysze się, aż stanie."""
    kam(st, t, 52, 640, 380, 2.0, 0.84, lens=1.8)
    st.dof = 2.4
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0, tint=(0.8, 0.76, 0.72), kul=False)
    J.hang(st, J.order(), 640, 230, 0.84, pr(t, 0.4, 1.6), t, 610, drop=600, sway=2.2, w=150)
    st.put(J.glow(), 640, 420, 0.841, w=380, anchor=(0.5, 0.5), mode="add", alpha=0.18 * pr(t, 1.5, 1.0), shadow=None, tint=(1.0, 0.85, 0.5))
    swiatlo(st, w, t, extra=(0.86, 0.82, 0.78))
    st.spot = (640, 380, 0.84, 260, 0.6)


NAGA_X = 900


def s_strzala_nieba(st, w, t, T):
    """Nagasunehiko i Iwarebiko unoszą po strzale z niebiańskim upierzeniem; za wodzem wysuwa się Nigihayahi."""
    kam(st, t, 53, lerp(640, 680, ease(t / T)), 430, 1.18, 0.8)
    st.dof = 1.0
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0)
    _proporce(st, t, (1.0, 1.0, 1.0))
    a1 = ease(pr(t, 0.8, 0.8))
    a2 = ease(pr(t, 2.2, 0.8))
    arrow = lambda h: (J.strzala_nieba(), h * 0.16, (0.5, 0.5), 0.0, False)
    lalka(st, t, "nagasune", NAGA_X, 440, flip=-1, rece=(150 * a1, 0), trzyma=arrow(440) if a1 > 0.05 else None)
    lalka(st, t, "iwarebiko", 380, 300, flip=1, rece=(150 * a2, 0), trzyma=arrow(300) if a2 > 0.05 else None)
    lalka(st, t, "nigihayahi", 1080, 300, pr(t, 4.4, 1.2), flip=-1, rece=(10, 0), p=P.lalki + 0.005)
    podpis(w, t, "Nigihayahi", 1080, nad(300), 5.3, 2.6)
    zawieszki(st, t, w)
    swiatlo(st, w, t)


ZDRADA_CIOS = 1.4  # miecz Nigihayahiego spada na Nagasunehiko; te same czasy w efekty.ZDARZENIA (świst, cios, X)


def s_zdrada(st, w, t, T):
    """Zabójstwo w fazach (wytyczne 1.21): Nigihayahi unosi miecz (zamach), tnie (cios — wstrząs), Nagasunehiko chwieje
    się, ma X na oczach, nad nim miga czerwony X (śmierć i wyrok, 1.20), i opada pod rampę; jego proporzec pada.
    Nigihayahi przechodzi na stronę Iwarebiko i kłania mu się (przegląd 17.11: wódz znikał bez ciosu)."""
    c = ZDRADA_CIOS
    kam(st, t, 54, 700, 440, 1.2, 0.8, shake=7.0 * (c < t < c + 0.4))
    st.dof = 1.0
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0)
    _proporce(st, t, (1.0, 1.0, 1.0 - pr(t, c + 1.4, 0.6)))
    raise_ = ease(pr(t, 0.3, 0.8))
    sw = ease(pr(t, c - 0.15, 0.25))
    arm = 165 * raise_ - 140 * sw
    walk = ease(pr(t, c + 2.2, 1.6))
    bow_ = ease(pr(t, c + 3.9, 0.9))
    lalka(st, t, "nagasune", NAGA_X, 440, flip=-1, lean=14 * ease(pr(t, c + 0.1, 0.8)) - 4 * math.sin(t * 10) * pr(t, c, 0.2) * (1 - pr(t, c + 0.7, 0.3)),
          sink=pr(t, c + 1.1, 1.8), oczy_x=pr(t, c + 0.3, 0.3))
    iks(st, NAGA_X - 20, 300, t, c + 0.35, h=200)
    lalka(st, t, "nigihayahi", lerp(1080, 760, walk), 300, flip=-1, rece=(arm if t < c + 2.0 else lerp(30, 70, bow_), 0), lean=-18 * bow_,
          trzyma=MIECZ(300), hop=5 * (0 < walk < 1))
    lalka(st, t, "iwarebiko", 380, 300, flip=1, rece=(20, 0), trzyma=LUK(300))
    swiatlo(st, w, t)


# ---------- akt 7 · Pierwszy cesarz ----------

PAL = (700, 640)  # pałac: x, szerokość


def palac_baza():
    return ziemia("blisko", PAL[0]) + 70


def palac(st, t, ks=(1.0,) * 5, k_all=1.0):
    """Pałac Kashihara z części: słupy, podłoga, ściany (od dołu), dach i zwieńczenie (z góry na nitkach)."""
    x, wd = PAL
    yb = palac_baza()
    sc = wd / J.PALAC_WH[0]
    p = P.droga + 0.03
    anc = (0.5, 690 / 700)
    for n, (cz, k, z) in enumerate((("slupy", ks[0], 0.0), ("sciany", ks[2], 0.1), ("podloga", ks[1], 0.6))):
        k = min(k, k_all)
        if k > 0:
            st.put(J.palac(cz), x, yb + (1 - back(k, 1.2)) * (260 if cz != "slupy" else 200), p, w=wd, anchor=anc, z=z, shadow=(4, 6, 8, 0.4))
    for cz, k in (("dach", ks[3]), ("szczyt", ks[4])):
        k = min(k, k_all)
        if k > 0:
            st.put(J.palac(cz), x, yb - (1 - back(k, 1.1)) * 600, p, w=wd, anchor=anc, z=0.3 if cz == "dach" else 0.35, shadow=(5, 7, 9, 0.45))
            if k < 1:
                st.line([(x - wd * 0.3, -300), (x - wd * 0.3, yb - (1 - back(k, 1.1)) * 600 - 450 * sc)], p, width=1.1, color=(70, 56, 44), alpha=0.7)
                st.line([(x + wd * 0.3, -300), (x + wd * 0.3, yb - (1 - back(k, 1.1)) * 600 - 450 * sc)], p, width=1.1, color=(70, 56, 44), alpha=0.7)
    return yb - (690 - 400) * sc  # wysokość podłogi ganku


def na_ganku(st, t, key, x, h, k=1.0, **kw):
    """Lalka na ganku pałacu: między ścianami a podłogą (podłoga zasłania jej stopy)."""
    p = P.droga + 0.03
    yb = palac_baza()
    floor = yb - (690 - 400) * PAL[1] / J.PALAC_WH[0]
    return lalka(st, t, key, x, h, k, y=floor + 18, p=p + 0.0, **kw) if k > 0 else None


def _ganek_z(st, fn):
    """Lalki na ganku rysuje się z z = 0,4 (za podłogą z = 0,6, przed ścianami z = 0,1)."""
    n0 = len(st.items)
    out = fn()
    for i in range(n0, len(st.items)):
        kind, p, z, idx, it = st.items[i]
        st.items[i] = (kind, p, 0.4 + z * 0.1, idx, it)
    return out


def skarby_nad(st, t, x, y, p, k=(1.0, 1.0, 1.0), sc=0.7):
    J.hang(st, J.lustro(), x - 70, y, p, k[0], t, 620, drop=520, sway=1.0, w=70 * sc / 0.7)
    J.hang(st, J.magatama_sznur(), x + 10, y + 8, p, k[1], t, 621, drop=520, sway=1.0, w=96 * sc / 0.7, strings=(0.1, 0.9))
    J.hang(st, J.miecz_jp(True), x + 90, y - 14, p, k[2], t, 622, drop=520, sway=0.8, h=150 * sc / 0.7)


def s_palac(st, w, t, T):
    """U stóp góry Unebi wysuwają się słupy, podłoga, ściany, zjeżdża dach i skrzyżowane belki."""
    k = ease(t / T)
    kam(st, t, 55, lerp(660, 700, k), lerp(430, 410, k), lerp(1.05, 1.14, k), 0.66, truck=0.6)
    st.dof = 0.6
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0)
    palac(st, t, (pr(t, 0.6, 1.0), pr(t, 1.8, 1.0), pr(t, 3.0, 1.0), pr(t, 4.4, 1.4), pr(t, 6.2, 1.4)))
    swiatlo(st, w, t)


def s_tron(st, w, t, T):
    """Iwarebiko wysuwa się na ganek; zjeżdżają za nim lustro, klejnoty i miecz, a obok zawieszka „660 p.n.e.”."""
    w.zawieszki = [("660 p.n.e.", 540, 330, pr(t, 5.0, 1.0))]
    k = ease(t / T)
    floor = palac_baza() - (690 - 400) * PAL[1] / J.PALAC_WH[0]
    kam(st, t, 56, 690, lerp(floor - 60, floor - 80, k), lerp(1.7, 1.85, k), 0.66, lens=1.5)
    st.dof = 1.2
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0)
    palac(st, t)
    _ganek_z(st, lambda: na_ganku(st, t, "jimmu", 700, 170, pr(t, 0.8, 1.2), flip=1, rece=(40 * ease(pr(t, 3.0, 0.8)), 0)))
    skarby_nad(st, t, 700, floor - 250, P.droga + 0.031, (pr(t, 2.2, 1.2), pr(t, 2.8, 1.2), pr(t, 3.4, 1.2)))
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_imie(st, w, t, T):
    """Zbliżenie: przed cesarzem zjeżdża zawieszka ze znakami 神武."""
    floor = palac_baza() - (690 - 400) * PAL[1] / J.PALAC_WH[0]
    kam(st, t, 57, 700, floor - 100, lerp(2.8, 3.0, ease(t / T)), 0.66, lens=2.4)
    st.dof = 1.8
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, kul=False)
    palac(st, t)
    _ganek_z(st, lambda: na_ganku(st, t, "jimmu", 700, 170, flip=1, rece=(20, 0)))
    skarby_nad(st, t, 700, floor - 250, P.droga + 0.031)
    J.hang(st, J.tag_zh("神武", 46), 640, floor - 170, 0.72, pr(t, 0.6, 1.2), t, 630, drop=500, sway=1.4, h=60, shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t)


def s_zona(st, w, t, T):
    """Obok cesarza wysuwa się księżniczka w zielonym; oboje kłaniają się sobie."""
    floor = palac_baza() - (690 - 400) * PAL[1] / J.PALAC_WH[0]
    kam(st, t, 58, 730, floor - 80, lerp(1.9, 2.0, ease(t / T)), 0.66, lens=1.7)
    st.dof = 1.4
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0)
    palac(st, t)
    bow_ = ease(pr(t, 3.0, 0.9)) * (1 - ease(pr(t, 5.6, 0.8)))
    _ganek_z(st, lambda: (na_ganku(st, t, "jimmu", 680, 170, flip=1, lean=12 * bow_, rece=(20, 0)),
                          na_ganku(st, t, "zona", 790, 160, pr(t, 0.8, 1.2), flip=-1, lean=-12 * bow_, rece=(30, 0))))
    skarby_nad(st, t, 700, floor - 250, P.droga + 0.031)
    swiatlo(st, w, t)


def s_pola(st, w, t, T):
    """Pola ryżowe zielenieją, złocą się i znów zielenieją; słońce i księżyc mijają się na nitkach."""
    f = t / T
    w.pola_v = 0 if f < 0.35 else (1 if f < 0.7 else 0)
    night = ease(pr(t, 2.4, 1.0)) * (1 - ease(pr(t, 4.6, 1.0)))
    w.sun = 1 - night
    w.moon = night
    w.noc = 0.7 * night
    kam(st, t, 59, lerp(420, 900, ease(f)), 420, 1.12, 0.62, truck=0.7)
    st.dof = 0.6
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, pola=1.0)
    palac(st, t)
    swiatlo(st, w, t)


def s_smierc(st, w, t, T):
    """Zawieszka „127 lat”; cesarz przechyla się i opada, a lustro, klejnoty i miecz zostają nad pustym miejscem."""
    w.zawieszki = [("127 lat", 520, 300, pr(t, 0.6, 1.0))]
    floor = palac_baza() - (690 - 400) * PAL[1] / J.PALAC_WH[0]
    kam(st, t, 60, 690, floor - 90, lerp(1.75, 1.85, ease(t / T)), 0.66, lens=1.55)
    st.dof = 1.2
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, tint=(1.04, 0.96, 0.88))
    palac(st, t)
    s = pr(t, 3.0, 2.6)
    _ganek_z(st, lambda: na_ganku(st, t, "jimmu_stary", 700, 165, flip=1, lean=-10 * ease(pr(t, 2.2, 0.9)), sink=s * 0.7, alpha=1 - pr(t, 4.2, 1.2),
                                  rece=(10, 0)))
    skarby_nad(st, t, 700, floor - 250, P.droga + 0.031)
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(1.04, 0.96, 0.9))


def s_pusto(st, w, t, T):
    """Detal: pusty ganek; lustro kołysze się na nitce i łapie ostatni promień słońca."""
    floor = palac_baza() - (690 - 400) * PAL[1] / J.PALAC_WH[0]
    kam(st, t, 61, 650, floor - 190, 2.6, 0.66, lens=2.2)
    st.dof = 1.6
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, tint=(1.06, 0.94, 0.84), kul=False)
    palac(st, t)
    skarby_nad(st, t, 700, floor - 250, P.droga + 0.031)
    st.put(J.glow(), 630, floor - 220, P.droga + 0.032, w=260, anchor=(0.5, 0.5), mode="add", alpha=0.45 * max(0.0, math.sin(t * 2.4)) ** 3,
           shadow=None, tint=(1.0, 0.85, 0.55))
    swiatlo(st, w, t, extra=(1.06, 0.94, 0.86))


def s_linia(st, w, t, T):
    """Wzdłuż wzgórz wysuwa się długi szereg małych lalek cesarzy, coraz mniejszych w głębi."""
    k = ease(t / T)
    kam(st, t, 62, 640, lerp(440, 400, k), lerp(1.15, 1.0, k), 0.62, truck=0.6)
    st.dof = 0.6
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, pola=1.0)
    palac(st, t)
    n = 0
    for band, p, h, xs in (("przod", P.wzgorza + 0.045, 120, range(1180, 60, -110)), ("blisko", P.droga + 0.012, 74, range(80, 1240, 80))):
        for x in xs:
            kk = pr(t, 0.6 + 0.22 * n, 0.6)
            lalka(st, t, "jimmu" if n % 3 else "jimmu_stary", x, h, kk, y=ziemia(band, x) + h * 0.22, p=p + 0.0002 * n, flip=-1 if band == "przod" else 1,
                  seed=700 + n)
            n += 1
    swiatlo(st, w, t)


# ---------- akt 8 · Kronika i ziemia ----------

STOL = (660, 742, 420)  # stół pisarza: x, dół, szerokość


def stol(st, t, k=1.0):
    desk = J.S("desk", 0.6)
    sx, sy, sw = STOL
    dh = sw * desk.h / desk.w
    down = (1 - back(k, 1.1)) * 330
    st.put(desk, sx, sy + down, P.rekwizyty, w=sw)
    return lambda fx, fy: (sx - sw / 2 + fx * sw, sy - dh + fy * dh + down)


def s_kronika(st, w, t, T):
    """Stół i pisarz w dworskiej szacie; zwój rozwija się i pokrywa znakami; zawieszki „712” i „720”."""
    w.zawieszki = [("712", 420, 300, pr(t, 2.6, 1.0)), ("720", 880, 300, pr(t, 6.4, 1.0))]
    kam(st, t, 63, lerp(640, 660, ease(t / T)), 500, lerp(1.4, 1.5, ease(t / T)), 0.84)
    st.dof = 1.8
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, kul=False)
    palac(st, t)
    kd = pr(t, 0.3, 1.2)
    on = stol(st, t, kd)
    st.put(J.S("scribe", 0.7), 520, 664 + (1 - back(pr(t, 0.8, 1.2), 1.2)) * 300, P.lalki + 0.02, h=230, anchor=(0.45, 1.0),
           rot=0.5 * noise(t, 21, 0.5) + (1.5 * math.sin(t * 5.2) + 1.0) * pr(t, 2.4, 0.5))
    if kd >= 1:
        x, y = on(0.36, 0.30)
        st.put(J.zwoj_jp(), x, y, P.rekwizyty + 0.006, w=230, anchor=(0.0, 0.5), sx=max(0.04, ease(pr(t, 1.6, T - 3.0))), rot=-3,
               shadow=(3, 5, 5, 0.4))
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_rachunek(st, w, t, T):
    """Detal: zjeżdżają po kolei zawieszki „601”, „− 1260 lat” i „660 p.n.e.”."""
    kam(st, t, 64, 640, 420, 1.75, 0.84, lens=1.6)
    st.dof = 2.4
    kraj(st, t, w, niebieskie=1.0, unebi=1.0, gory=0.0, kul=False)
    palac(st, t)
    stol(st, t)
    for n, (txt, x) in enumerate((("601", 470), ("− 1260 lat", 640), ("660 p.n.e.", 830))):
        J.hang(st, J.tag(txt), x, 330, 0.86, pr(t, 0.8 + 1.8 * n, 1.0), t, 640 + n, drop=480, sway=1.4, h=50, shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t)


def s_jomon(st, w, t, T):
    """Zmiana dekoracji: wzgórza bez pałacu i pól; wyrastają chaty z trzciny i garnki, przechodzą myśliwi."""
    kam(st, t, 65, lerp(600, 700, ease(t / T)), 450, 1.12, 0.66)
    st.dof = 0.7
    kraj(st, t, w, chaty=1.0, tint=(0.96, 1.0, 0.95))
    for n, x in enumerate((960, 1080)):
        k = pr(t, 1.6 + 0.3 * n, 0.6)
        if k > 0:
            st.put(J.garnek(n), x, 712 + (1 - back(k, 1.3)) * 120, P.rekwizyty, h=110 - 14 * n)
    for n, (key, x0, sp) in enumerate((("mysliwy", -120, 110), ("mysliwy2", -340, 100))):
        x = x0 + sp * max(0.0, t - 2.4)
        if -200 < x < 1500:
            lalka(st, t, key, x, 260, flip=1, hop=8, rece=(30, 0), trzyma=SPEAR(260), seed=720 + n)
    swiatlo(st, w, t, extra=(0.97, 1.0, 0.95))


MAPA_WD = 820


def s_wa(st, w, t, T):
    """Na nitkach zjeżdża papierowa mapa wysp; wyskakują na niej dziesiątki maleńkich chorągiewek."""
    kam(st, t, 66, 640, 360, lerp(1.08, 1.14, ease(t / T)), 0.82)
    st.dof = 0.6
    to = mapa_scena(st, t, w, k=pr(t, 0.3, 1.4), x=640, y=40, wd=MAPA_WD)
    pts = J.punkty_na_mapie(110, seed=5)
    for n, (mx, my) in enumerate(pts):
        r = random.Random(1300 + n)
        k = pr(t, 2.0 + r.uniform(0, T - 3.2), 0.4)
        if k > 0:
            x, y = to(mx, my)
            st.put(J.choragiewka(1), x, y + (1 - back(k, 1.6)) * 8, 0.823, h=18 * min(1.0, k * 1.5), anchor=(0.5, 1.0), shadow=(1, 2, 2, 0.3))
    swiatlo(st, w, t)


def _mapa_tlo(st, t, w):
    mapa_scena(st, t, w, k=1.0, x=640, y=40, wd=MAPA_WD)


def s_pieczec(st, w, t, T):
    """Detal: złota pieczęć z wężem na uchwycie zjeżdża na nitce i obraca się; zawieszka „57”."""
    k = ease(t / T)
    kam(st, t, 67, 640, 360, lerp(1.7, 1.9, k), 0.86, lens=1.6)
    st.dof = 2.6
    _mapa_tlo(st, t, w)
    spin = math.cos(t * 1.6)
    J.hang(st, J.pieczec(), 640, 250, 0.86, pr(t, 0.3, 1.6), t, 650, drop=520, sway=1.0, w=170, sx=spin if abs(spin) > 0.06 else 0.06)
    st.put(J.glow(), 640, 340, 0.861, w=300, anchor=(0.5, 0.5), mode="add", alpha=0.16 * pr(t, 1.6, 1.0), shadow=None, tint=(1.0, 0.85, 0.4))
    J.hang(st, J.tag("57 r."), 860, 300, 0.87, pr(t, 2.0, 1.0), t, 651, drop=480, sway=1.4, h=50, shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t)


def s_odcisk(st, w, t, T):
    """Pieczęć opada na papier i unosi się, a na papierze zostaje czerwony odcisk pięciu znaków."""
    kam(st, t, 68, 640, 470, 2.4, 0.86, lens=2.1)
    st.dof = 2.4
    _mapa_tlo(st, t, w)
    st.put(J.parawan(), 640, 700, 0.85, w=520, shadow=(4, 6, 8, 0.4))
    down = ease(pr(t, 0.2, 0.4)) * (1 - ease(pr(t, 1.1, 0.6)))
    if pr(t, 0.55, 0.01) > 0:
        st.put(J.odcisk(), 640, 520, 0.851, w=120, anchor=(0.5, 0.5), alpha=0.92, shadow=None)
    st.put(J.pieczec(), 640, lerp(380, 590, down), 0.86, w=150, anchor=(0.5, 1.0), shadow=(4, 6 + 30 * (1 - down), 8, 0.4))
    swiatlo(st, w, t)


def s_chlop(st, w, t, T):
    """Chłop kopie motyką rów na polu; spod ziemi wysuwa się złota pieczęć, zjeżdża zawieszka „1784”."""
    w.zawieszki = [("1784", 860, 300, pr(t, 4.0, 1.0))]
    w.pola_v = 2
    kam(st, t, 69, lerp(640, 680, ease(t / T)), 480, 1.35, 0.8)
    st.dof = 1.0
    kraj(st, t, w, morze_k=1.0, pola=1.0)
    dig = math.sin(t * 4.2)
    st.put(Z0.prop("chlop"), 560, 712, P.lalki + 0.01, h=230, rot=-8 + 9 * dig * (1 - pr(t, 3.0, 0.4)) + 0.5 * noise(t, 731, 0.5), anchor=(0.5, 1.0))
    k = pr(t, 3.0, 1.4)
    if k > 0:
        st.put(J.pieczec(), 700, 704 + (1 - back(k, 1.3)) * 120, P.rekwizyty, w=90)
        st.put(J.glow(), 700, 640, P.rekwizyty + 0.001, w=240, anchor=(0.5, 0.5), mode="add", alpha=0.25 * k, shadow=None, tint=(1.0, 0.85, 0.4))
    zawieszki(st, t, w)
    swiatlo(st, w, t)


def s_himiko(st, w, t, T):
    """Przed parawanem wysuwa się królowa Himiko; zjeżdżają do niej rzędy błyszczących luster."""
    k = ease(t / T)
    kam(st, t, 70, 640, lerp(440, 420, k), lerp(1.3, 1.42, k), 0.82)
    st.dof = 1.0
    kraj(st, t, w, niebieskie=1.0, wzgorza=1.0, gory=0.0, kul=False, tint=(0.96, 0.92, 0.88))
    st.put(J.parawan(), 640, 704 + (1 - back(pr(t, 0.2, 1.0), 1.2)) * 380, 0.78, w=720, shadow=(6, 8, 10, 0.45))
    st.put(J.parawan_rama(), 640, 704 + (1 - back(pr(t, 0.2, 1.0), 1.2)) * 380, 0.7805, w=720)
    lalka(st, t, "himiko", 640, 320, pr(t, 1.0, 1.2), p=0.815, flip=1, rece=(60 * ease(pr(t, 2.4, 0.8)), 0))
    n = 0
    for row, y in enumerate((150, 230, 310)):
        for j in range(6):
            x = 300 + j * 136 + (row % 2) * 68 - 34
            if 560 < x < 720 and row == 2:
                continue
            kk = pr(t, 2.2 + 0.18 * n, 0.9)
            J.hang(st, J.lusterko(), x, y, 0.83 + 0.0005 * n, kk, t, 660 + n, drop=420, sway=1.6, w=54)
            if kk >= 1 and noise(t, 670 + n, 1.4) > 0.55:
                st.put(J.glow(), x, y + 27, 0.832 + 0.0005 * n, w=90, anchor=(0.5, 0.5), mode="add", alpha=0.35, shadow=None, tint=(1.0, 0.95, 0.8))
            n += 1
    swiatlo(st, w, t, extra=(0.98, 0.94, 0.9))


# ---------- akt 9 · Źródło słońca ----------

def _kofun_tlo(st, t, w, k=1.0, y=70, wd=820, p=0.62):
    niebo_papier(st, w, (0.98, 0.96, 0.9))
    from scena import chmury
    chmury(st, t, w, k=(min(1.0, k * 2), 0.0, min(1.0, k * 2)))
    J.hang(st, J.kofun_plansza(), 640, y, p, k, t, 680, drop=640, sway=0.3, w=wd, strings=(0.12, 0.88))


def s_kofun(st, w, t, T):
    """Na nitkach zjeżdża plansza z kurhanem w kształcie dziurki od klucza; zawieszka „486 m”."""
    w.zawieszki = [("486 m", 980, 470, pr(t, 4.2, 1.0))]
    k = ease(t / T)
    kam(st, t, 71, 640, lerp(380, 360, k), lerp(1.05, 1.15, k), 0.8)
    st.dof = 0.6
    _kofun_tlo(st, t, w, pr(t, 0.6, 1.8), p=0.8)
    rampa(st, pr(t, 0.0, 0.6))
    zawieszki(st, t, w)
    swiatlo(st, w, t)


HANIWA = ["wojownik", "kon", "tancerz", "dom", "kobieta", "wojownik", "cylinder", "kon", "tancerz", "wojownik", "dom", "kobieta"]


def s_haniwa(st, w, t, T):
    """Przed kurhanem wysuwają się rzędy glinianych figurek, każda we własnej chwili; kamera jedzie wzdłuż nich."""
    f = t / T
    kam(st, t, 72, lerp(420, 880, f), 430, 1.25, 0.8, truck=0.8)
    st.dof = 1.0
    _kofun_tlo(st, t, w, 1.0, y=40, wd=760, p=0.5)
    Z0.rise(st, J.pasmo("przod"), CX + 20, 836, P.wzgorza + 0.05, 1.0, t, 613, w=2000, wob=0.0)
    for n in range(14):  # drugi rząd na grzbiecie pasma
        r = random.Random(1400 + n)
        x = -60 + n * 110 + r.uniform(-10, 10)
        kk = pr(t, 0.4 + r.uniform(0, 3.0), 0.6)
        if kk > 0:
            kind = HANIWA[(n + 3) % len(HANIWA)]
            hh = (95 if kind in ("kon", "dom") else 120) * r.uniform(0.9, 1.05)
            Z0.rise(st, J.haniwa(kind), x, ziemia("przod", clamp(x, -200, 1500)) + 30, P.wzgorza + 0.045, kk, t, 1450 + n, h=hh, wob=0.3)
    for n in range(10):  # pierwszy rząd przy rampie
        r = random.Random(1500 + n)
        x = 40 + n * 140 + r.uniform(-12, 12)
        kk = pr(t, 1.2 + r.uniform(0, 4.5), 0.6)
        if kk > 0:
            kind = HANIWA[n % len(HANIWA)]
            hh = (150 if kind in ("kon", "dom") else 210) * r.uniform(0.9, 1.05)
            Z0.rise(st, J.haniwa(kind), x, 712, P.lalki + 0.002 * (n % 3), kk, t, 1550 + n, h=hh, wob=0.4)
    rampa(st)
    swiatlo(st, w, t)


def s_tancerz(st, w, t, T):
    """Zbliżenie: gliniany tancerz haniwa z uniesioną ręką; przez jego puste oczy prześwieca słońce."""
    kam(st, t, 73, 640, 420, lerp(2.0, 2.15, ease(t / T)), 0.8, lens=1.8)
    st.dof = 2.6
    _kofun_tlo(st, t, w, 1.0, y=40, wd=760, p=0.5)
    sun = ease(pr(t, 0.2, 1.4))
    hx, hy = 640, 712 - 380 * (420 - 104) / 416  # głowa tancerza (oczy) w kadrze wzorcowym
    st.put(J.glow(), hx, hy, 0.55, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.5 * sun, shadow=None, tint=(1.0, 0.7, 0.45))
    st.put(J.S("sun", 0.5), hx - 6, hy + 6 + (1 - sun) * 220, 0.56, w=200, anchor=(0.5, 0.5))
    st.put(J.haniwa("tancerz"), 640, 712, 0.8, h=380, rot=0.6 * noise(t, 1600, 0.4))
    rampa(st)
    swiatlo(st, w, t)


def s_nihon(st, w, t, T):
    """Zawieszka 倭 obraca się na nitce i odjeżdża, zjeżdża 日本; za nią wschodzi czerwone słońce."""
    kam(st, t, 74, 640, 420, lerp(1.12, 1.2, ease(t / T)), 0.62, truck=0.5)
    st.dof = 0.6
    morze(st, t, w, wyspy=[(x, b, wd, v if v < 9 else 1, 1.0) for x, b, wd, v in WYSPY_JP], slonce_k=0.0)
    sr = ease(pr(t, 4.6, 3.0))
    if sr > 0:
        st.put(J.glow(), 640, 420 - 180 * sr, P.slonce, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.4 * sr, shadow=None, tint=(1.0, 0.7, 0.45))
        st.put(J.S("sun", 0.5), 640, 470 - 250 * sr, P.slonce + 0.002, w=230, anchor=(0.5, 0.5))
    off = ease(pr(t, 2.8, 1.2))
    spin = math.cos(math.pi * 3 * pr(t, 2.2, 1.0))
    if off < 1:
        J.hang(st, J.tag_zh("倭", 60), 640, 250 - 700 * off, 0.86, pr(t, 0.4, 1.0), t, 690, drop=480, sway=1.2, h=96,
               sx=spin if abs(spin) > 0.05 else 0.05, shadow=(4, 6, 6, 0.4))
    J.hang(st, J.tag_zh("日本", 60), 640, 250, 0.86, pr(t, 4.2, 1.2), t, 691, drop=600, sway=1.2, h=96, shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t)


def s_luty2(st, w, t, T):
    """Kartka kalendarza „11 lutego” zjeżdża obok zawieszki „1873”; na wzgórzach znów wyskakują chorągiewki."""
    k = ease(t / T)
    kam(st, t, 75, 640, lerp(400, 380, k), lerp(1.06, 1.12, k), 0.62, truck=0.5)
    st.dof = 0.5
    kraj(st, t, w, pola=1.0)
    choragiewki(st, t, [pr(t, 3.0 + 0.4 * n, 0.5) for n in range(9)])
    J.hang(st, J.kalendarz(), 560, 200, 0.84, pr(t, 0.4, 1.2), t, 700, drop=520, sway=1.4, w=130, shadow=(4, 6, 6, 0.4))
    J.hang(st, J.tag("1873"), 740, 260, 0.85, pr(t, 1.4, 1.0), t, 701, drop=480, sway=1.4, h=50, shadow=(4, 6, 6, 0.4))
    swiatlo(st, w, t)


def s_koronacja(st, w, t, T):
    """Na stojakach stają dwie skrzynki owinięte płótnem, za nimi wyrasta tron pod baldachimem; zawieszka „126”."""
    w.zawieszki = [("126", 1010, 280, pr(t, 5.0, 1.0))]
    k = ease(t / T)
    kam(st, t, 76, 640, lerp(440, 420, k), lerp(1.2, 1.3, k), 0.8)
    st.dof = 1.0
    st.put(J.black(), CX, CY, P.niebo, w=2000, anchor=(0.5, 0.5), shadow=None, blur=0, tint=(0.30, 0.16, 0.12))
    for n, x in enumerate((240, 640, 1040)):
        st.put(J.glow(), x, 300, 0.4, w=700, anchor=(0.5, 0.5), mode="add", alpha=0.18, shadow=None, tint=(1.0, 0.8, 0.5))
    for n, x in enumerate((-40, 1320)):  # złote parawany po bokach
        st.put(J.parawan(), x, 700, 0.7, w=520, tint=(1.0, 0.86, 0.5), shadow=(6, 8, 10, 0.45))
    Z0.rise(st, J.takamikura(), 640, 712, 0.78, pr(t, 0.6, 1.6), t, 710, h=470, wob=0.0)
    for n, x in enumerate((440, 840)):
        Z0.rise(st, J.skrzynka(), x, 712, P.rekwizyty, pr(t, 2.6 + 0.6 * n, 1.0), t, 712 + n, h=150, wob=0.2)
    rampa(st)
    zawieszki(st, t, w)
    swiatlo(st, w, t, extra=(1.04, 0.96, 0.88))


def s_koniec(st, w, t, T):
    """Kamera wycofuje się z teatru: nad wyspami czerwone słońce, światło w skrzyni gaśnie, zostaje szyld z tytułem."""
    k = ease(pr(t, 0.4, T - 2.6))
    m = math.exp(lerp(math.log(1.0), math.log(0.6), k))
    kam(st, t, 77, 640, lerp(360, 322, k), m, 1.0, lens=m ** 0.55, truck=1.0, drift=0.4)
    st.dof = 0.0
    morze(st, t, w, wyspy=[(x, b, wd, v if v < 9 else 1, 1.0) for x, b, wd, v in WYSPY_JP])
    off = ease(pr(t, T - 2.3, 0.9))
    st.put(J.black(), CX, CY, 0.992, w=1300, anchor=(0.5, 0.5), alpha=off, shadow=None, blur=0)
    J.theatre_put(st, 0.9 - 0.4 * off)
    swiatlo(st, w, t)


DZIEKI = (0.5, 1.5)  # tabliczki „DZIĘKUJĘ / za obejrzenie” zjeżdżają od a, „Wesprzyj mnie…” wysuwa się od dołu od b


def s_dzieki(st, w, t, T):
    """Ciemna scena pod szyldem, kadr jak na końcu ujęcia „koniec”. W otwór sceny zjeżdżają na nitkach duże papierowe
    tabliczki z podziękowaniem dla widzów, oświetlone z góry jak w teatrze; film schodzi w czerń (render). Wzór:
    „Pierwszy cesarz” s_dzieki (reżyser 16.11: „Duże — THANK YOU for watching, Support me and I'll do my best.”)."""
    kam(st, t, 78, 640, 322, 0.6, 1.0, lens=0.6 ** 0.55, truck=1.0, drift=0.4)
    st.dof = 0.0
    st.put(J.black(), CX, CY, 0.992, w=1300, anchor=(0.5, 0.5), shadow=None, blur=0)
    a, b = DZIEKI
    p = 0.995  # przed ciemnością sceny, za ramą teatru
    st.put(J.glow(), CX, 340, p - 0.002, w=1500, anchor=(0.5, 0.5), mode="add", alpha=0.22 * ease(pr(t, a - 0.1, 0.8)),
           shadow=None, tint=(1.0, 0.85, 0.6))
    J.hang(st, J.tag("DZIĘKUJĘ", 120), CX, 96, p + 0.001, pr(t, a, 1.0), t, 311, drop=620, sway=0.9, h=222,
           strings=(0.25, 0.75), shadow=(5, 8, 10, 0.5))
    J.hang(st, J.tag("za obejrzenie", 60), CX, 336, p + 0.0005, pr(t, a + 0.3, 1.0), t, 312, drop=620, sway=1.1, h=112,
           strings=(0.2, 0.8), shadow=(4, 6, 8, 0.45))
    J.rise(st, J.tag("Wesprzyj mnie, a dam z siebie wszystko.", 60), CX, 612, p, pr(t, b, 1.0), t, 313, lift=270, wob=0.4,
           h=118, shadow=(4, 6, 8, 0.45))
    J.theatre_put(st, 0.5)
    swiatlo(st, w, t)
