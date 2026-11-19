"""Ujęcia aktów 0–4 filmu „Bonnie and Clyde: The Outlaws Made of Paper”: funkcja `s_<klucz>(st, w, t, T)` na ujęcie.

st — scena (papier.Stage), w — stan świata z początku ujęcia (scena.stan), t — czas od początku ujęcia, T — długość ujęcia.
Rozpiska: docs/filmy/bonnie-i-clyde/ujecia/dane.py. Zapowiedź (zap_*) render składa sam ze skrótów tych ujęć (render.WYCINEK).
"""
import math

from scena import (CX, DROGA_Y, J, P, STOPY, Z0, auto, back, bk, blysk, cien, ciezarowka, clamp, ease, ease_out, eastham, iks, jazda,
                   kam, kulisy, lalka, lerp, miasto, noise, parawan, podpis, pr, preria, punkt, rampa, settle, swiatlo, teatr_gazet,
                   west_dallas, wnetrze, zawieszki, drukarnia)


def koniec(st, w, t, dim=1.0, extra=(1.0, 1.0, 1.0)):
    swiatlo(st, w, t, extra=extra, dim=dim)
    zawieszki(st, t, w)


def tab(w, t, txt, x, y, t0, dur=2.2):
    """Tabliczka z okrzykiem (słownik znaków 1.20)."""
    podpis(w, t, txt, x, y, t0, dur)


def REV(dl=46):
    """Rewolwer w dłoni: dl — długość w kadrze (arkusz 180 × 110)."""
    return (J.rek("rewolwer"), dl * 110 / 180, (0.3, 0.75), -80, True)


def KARABIN(dl=170):
    """Karabin w dłoni: dl — długość w kadrze (arkusz 520 × 90)."""
    return (J.rek("karabin"), dl * 90 / 520, (0.3, 0.55), -78, True)


# ===================== AKT 0 · PROLOG =====================

def _teatr_obsada(st, w, t, k=1.0, cygaro=True, kamera=True):
    teatr_gazet(st, t, w, k)
    auto(st, t, 700, 290)
    kb = ease(pr(t, 0.4, 0.8)) if w.get("build") is not None else 1.0
    lalka(st, t, "bonnie_cygaro" if cygaro else "bonnie", 470, 320, kb, flip=1, lean=-6, rece=(70, 10), trzyma=REV())
    kc = ease(pr(t, 0.7, 0.8)) if w.get("build") is not None else 1.0
    lalka(st, t, "clyde", 980, 350, kc, flip=-1, rece=(35, 20), trzyma=KARABIN())


def s_tytul(st, w, t, T):
    """Kurtyna startu (render.KURTYNA_START) na teatr z gazet: Ford, Bonnie z cygarem i rewolwerem, Clyde z karabinem; szyld."""
    m = lerp(0.62, 1.0, ease(pr(t, 1.6, 3.2)))
    kam(st, t, 1, 640, lerp(300, 380, ease(pr(t, 1.6, 3.2))), m, 0.8, drift=0.4)
    J.theatre_put(st)
    _teatr_obsada(st, w, t)
    koniec(st, w, t)


def s_wprowadzenie(st, w, t, T):
    """Najazd na Bonnie; podpis „Bonnie Parker” przy imieniu; Bonnie wyjmuje cygaro z ust i krzywi się."""
    kam(st, t, 2, lerp(640, 500, ease(pr(t, 0, 3))), lerp(380, 480, ease(pr(t, 0, 3))), lerp(1.0, 1.6, ease(pr(t, 0, 3.5))), 0.81)
    st.dof = 1.2
    wyjmuje = t > 5.2
    teatr_gazet(st, t, w)
    auto(st, t, 700, 290)
    out = lalka(st, t, "bonnie" if wyjmuje else "bonnie_cygaro", 470, 320, flip=1, lean=-6 + 4 * ease(pr(t, 5.0, 0.5)),
                rece=(70 + 60 * ease(pr(t, 4.6, 0.6)) * (1 - ease(pr(t, 6.6, 0.6))), 10), trzyma=REV() if not (4.6 < t < 7.2) else None)
    if 4.6 < t < 7.2 and out:
        st.put(J.rek("cygaro"), out[0], out[1], P.lalki + 0.02, h=10, anchor=(0.1, 0.5), rot=out[2] - 90)
    lalka(st, t, "clyde", 980, 350, flip=-1, rece=(35, 20), trzyma=KARABIN())
    podpis(w, t, "Bonnie Parker", 470, 250, 1.0, 3.2)
    if t > 5.6:
        tab(w, t, "UGH!", 560, 330, 5.6, 1.6)
    koniec(st, w, t)


def s_wprowadzenie2(st, w, t, T):
    """Odjazd na Clyde'a; podpis „Clyde Barrow”; za nimi z nitek zjeżdżają nagłówki gazet jeden za drugim."""
    kam(st, t, 3, lerp(900, 640, ease(pr(t, 0, 4))), lerp(470, 390, ease(pr(t, 0, 4))), lerp(1.6, 1.0, ease(pr(t, 0, 4))), 0.81)
    teatr_gazet(st, t, w)
    for n, (x, y, nag) in enumerate(((300, 140, "BANK ROBBED"), (640, 110, "POLICE HUNT COUPLE"), (980, 150, "OUTLAW GIRL WITH CIGAR"))):
        J.hang(st, J.gazeta(nag, 30 + n, 360, 300, False), x, y, P.wzgorza, pr(t, 3.0 + 1.3 * n, 1.0), t, 400 + n, w=270, drop=520,
               sway=1.2, strings=(0.2, 0.8))
    auto(st, t, 700, 290)
    lalka(st, t, "bonnie", 470, 320, flip=1, lean=-2, rece=(20, 10), trzyma=REV())
    lalka(st, t, "clyde", 980, 350, flip=-1, rece=(35 + 20 * ease(pr(t, 1.2, 0.5)), 20), trzyma=KARABIN())
    podpis(w, t, "Clyde Barrow", 980, 240, 1.0, 3.0)
    koniec(st, w, t)


def _mieszkanie_joplin(st, w, t, ruch=True):
    wnetrze(st, t, w, sciana="paski", okna=(260,), drzwi=(1050,), meble=(("stol", 640, 140, None), ("krzeslo", 470, 170, None),
                                                                       ("lozko", 230, 150, None)), zarowki=(640,))
    for n, (key, x, y, h, rot) in enumerate((("walizka", 860, 712, 90, 4), ("walizka", 930, 712, 70, -6), ("karabin", 640, 612, 34, 4),
                                            ("zeszyt", 700, 618, 50, 12), ("butelka", 560, 616, 70, 0))):
        k = bk(w, 0.5 + 0.05 * n)
        if k > 0:
            st.put(J.rek(key), x, y + (1 - back(k, 1.3)) * 140, P.lalki - 0.01, h=h, rot=rot)


def s_joplin_rzeczy(st, w, t, T):
    """Opuszczone mieszkanie w Joplin: policjant wchodzi drzwiami, rozgląda się, podnosi z podłogi aparat, z kasety wysuwa się klisza."""
    kam(st, t, 4, lerp(760, 820, ease(t / T)), lerp(400, 470, ease(pr(t, 2.0, 4.0))), lerp(1.0, 1.45, ease(pr(t, 2.0, 4.0))), 0.81)
    st.dof = 1.0
    _mieszkanie_joplin(st, w, t)
    x, _ = jazda(t, 0.3, 2.2, 1120, 820)
    schyl = ease(pr(t, 3.0, 0.7)) * (1 - ease(pr(t, 4.2, 0.6)))
    out = lalka(st, t, "detektyw", x, 330, flip=-1, lean=-18 * schyl, rece=(20 + 70 * schyl + 40 * ease(pr(t, 4.2, 0.6)), 10), hop=6 * (t < 2.5))
    podnies = ease(pr(t, 3.6, 0.5))
    ax, ay = (720, 702) if podnies <= 0 or not out else (lerp(720, out[0], podnies), lerp(702, out[1], podnies))
    st.put(J.rek("aparat"), ax, ay, P.lalki + 0.02, h=50, anchor=(0.5, 0.5))
    if t > 4.6:
        f = ease(pr(t, 4.6, 1.4))
        st.put(J.rek("klisza"), ax - 30, ay + 12 + 10 * f, P.lalki + 0.03, h=26, anchor=(1.0, 0.5), sx=0.15 + 0.85 * f, rot=-8)
    koniec(st, w, t)


def s_hak_joplin_rzeczy(st, w, t, T):
    s_joplin_rzeczy(st, w, t, T)


def s_zdjecie(st, w, t, T):
    """Klatka z kliszy ożywa: Bonnie opiera nogę o zderzak Forda, ktoś zza kadru podaje jej cygaro, ona pozuje z rewolwerem; flesz."""
    kam(st, t, 5, 640, 470, lerp(1.3, 1.45, ease(t / T)), 0.81)
    st.dof = 1.3
    miasto(st, t, w, fasady=(("garaz", 760),), tyl=(("dom", 200), ("dom", 1150)), kul=False)
    auto(st, t, 760, 250, kolor="szary")
    podaje = ease(pr(t, 0.6, 0.8)) * (1 - ease(pr(t, 2.0, 0.6)))
    # ręka W.D. zza kadru z cygarem
    if podaje > 0:
        st.put(J.figura("wd").arm, lerp(1000, 760, podaje), 470, P.lalki + 0.03, h=150, anchor=(0.5, 0.1), rot=95)
        st.put(J.rek("cygaro"), lerp(900, 660, podaje), 476, P.lalki + 0.04, h=14, anchor=(0.5, 0.5))
    ma = t > 2.1
    out = lalka(st, t, "bonnie_cygaro" if ma else "bonnie", 560, 300, flip=1, lean=-8, lift=12,
                rece=(30 + 90 * ease(pr(t, 2.4, 0.6)), 20 + 30 * ease(pr(t, 0.8, 0.5))), trzyma=REV())
    blysk(st, 640, 360, 0.95, t, 4.4, r=2200, kolor=(1.0, 1.0, 0.95), dl=0.18)
    if 4.4 <= t < 4.62:
        st.dim = 1.6
    koniec(st, w, t, dim=1.0 if not (4.4 <= t < 4.62) else 1.7)


def s_hak_pomost(st, w, t, T):
    """Pomost: wielka strona gazety przewraca się przez cały kadr jak kurtyna (szelest papieru)."""
    kam(st, t, 6, 640, 360, 1.0, 0.9, drift=0.2)
    teatr_gazet(st, t, w)
    k = ease(pr(t, 0.1, T - 0.3))
    sx = math.cos(math.pi * k)
    st.put(J.gazeta("EXTRA!", 50, 640, 760), CX, 760, 0.93, h=900, anchor=(0.0 if sx >= 0 else 0.0, 1.0), sx=sx if abs(sx) > 0.02 else 0.02,
           tint=(1.0 - 0.3 * abs(math.sin(math.pi * k)),) * 3)
    koniec(st, w, t)


def s_prasa(st, w, t, T):
    """Wałki maszyny drukarskiej kręcą się, wylatują setki gazet ze zdjęciem Bonnie z cygarem i odlatują nad dachy."""
    kam(st, t, 7, 640, 380, lerp(1.05, 0.95, ease(t / T)), 0.72, shake=1.2)
    drukarnia(st, t, w, obrot=t * 220)
    lalka(st, t, "drukarz", 1000, 310, flip=-1, rece=(70 + 15 * math.sin(t * 5), 40))
    for n in range(14):
        f = ((t * 0.6 + n / 14) % 1.0)
        if t < 0.4 + n * 0.12:
            continue
        x = 820 + f * 900 + 40 * math.sin(n)
        y = 300 - f * 520 + 80 * math.sin(f * 3 + n)
        st.put(J.gazeta("OUTLAW GIRL WITH CIGAR", n % 4, 360, 480), x, y, P.drzewa + 0.02 * (n % 3), h=110, anchor=(0.5, 0.5),
               rot=f * 200 + n * 30, sx=math.cos(f * 6 + n), shadow=(4, 6, 6, 0.3))
    koniec(st, w, t)


def s_hak_cygaro(st, w, t, T):
    """Bonnie przy aucie czyta gazetę ze swoim zdjęciem, wypluwa papierosa i zgniata gazetę; tabliczka „I DON'T SMOKE CIGARS!”."""
    kam(st, t, 8, 640, 480, 1.6, 0.81)
    st.dof = 1.4
    w.noc = 0.5
    preria(st, t, w, slupy=False, kul=False)
    auto(st, t, 900, 250, kolor="szary")
    gniot = ease(pr(t, 3.6, 0.8))
    out = lalka(st, t, "bonnie", 600, 300, flip=1, rece=(95 - 20 * gniot, 80 - 30 * gniot))
    if out:
        st.put(J.gazeta("OUTLAW GIRL WITH CIGAR", 2, 360, 480), out[0] + 30, out[1] - 20, P.lalki + 0.03, h=lerp(150, 50, gniot),
               anchor=(0.3, 0.6), rot=-8 + 40 * gniot, sx=lerp(1.0, 0.5, gniot))
    f = pr(t, 2.6, 0.7)
    if 0 < f < 1:
        ux, uy = punkt("bonnie", 600, 300, 176, 160)
        st.put(J.rek("papieros"), ux + 60 * f, uy + 200 * f * f, P.lalki + 0.04, h=8, anchor=(0.5, 0.5), rot=400 * f)
    tab(w, t, "I DON'T SMOKE CIGARS!", 640, 260, 4.2, 3.6)
    koniec(st, w, t)


def s_obietnica(st, w, t, T):
    """Gazety układają się w mapę pięciu stanów; po mapie sunie papierowy Ford, a za nim drugi, z kapeluszem Hamera w oknie."""
    kam(st, t, 9, 640, 360, lerp(0.95, 1.08, ease(t / T)), 0.62)
    teatr_gazet(st, t, w)
    J.hang(st, J.mapa_plansza(), 640, 40, P.wzgorza, pr(t, 0.2, 1.4), t, 420, w=900, drop=600, sway=0.4, strings=(0.08, 0.92))
    x0, y0, sk = 640 - 450, 40, 0.9
    trasa = [(420, 480), (480, 400), (590, 300), (610, 190), (640, 100), (560, 310), (650, 590)]
    def na_trasie(f):
        f = clamp(f) * (len(trasa) - 1)
        i = min(int(f), len(trasa) - 2)
        a, b = trasa[i], trasa[i + 1]
        u = f - i
        return x0 + lerp(a[0], b[0], u) * sk, y0 + lerp(a[1], b[1], u) * sk
    for n, (dt, kol) in enumerate(((0.0, "szary"), (1.6, "czarny"))):
        f = pr(t, 2.0 + dt, T - 4.0)
        if f > 0:
            x, y = na_trasie(f)
            st.put(J.ford(kol), x, y, P.wzgorza + 0.01 + 0.002 * n, h=34, anchor=(0.5, 0.9), sx=1, shadow=(2, 3, 3, 0.3))
            if n == 1:
                st.put(J.rek("kapelusz_fedora"), x + 2, y - 26, P.wzgorza + 0.014, h=12, anchor=(0.5, 1.0), tint=(1.0, 0.9, 0.7))
    koniec(st, w, t)


# ===================== AKT I · KIM BYLI PRZED NAGŁÓWKAMI =====================

def s_wagon(st, w, t, T):
    """West Dallas: dymiące kominy, wiadukt, szałasy w błocie; pod wozem śpi rodzina, mały Clyde wyczołguje się spod koła i przeciąga."""
    kam(st, t, 10, 640, 380, lerp(0.96, 1.12, ease(t / T)), 0.72)
    west_dallas(st, t, w)
    for n, (x, key) in enumerate(((470, "matka_clyde"), (600, "dziecko1"))):
        lalka(st, t, key, x, 120, 1.0, y=708, flip=1, lean=88, p=P.drzewa + 0.002, rece=(0, 0))
    wy = ease(pr(t, 4.0, 1.6))
    lalka(st, t, "clyde_maly", lerp(640, 760, wy), 200, 1.0, lean=lerp(85, 0, wy), lift=-40 * (1 - wy), rece=(lerp(80, 160, ease(pr(t, 6.0, 0.8))) *
          (1 - ease(pr(t, 7.4, 0.6))), lerp(20, 150, ease(pr(t, 6.0, 0.8))) * (1 - ease(pr(t, 7.4, 0.6)))), p=P.lalki)
    if t > 6.2:
        tab(w, t, "YAWN", 800, 330, 6.2, 1.6)
    koniec(st, w, t)


def s_indyki(st, w, t, T):
    """Nastoletni Clyde i Buck pchają ciężarówkę z gdaczącymi indykami; wchodzi policjant z gwizdkiem, indyki wyfruwają; „STOP!”."""
    kam(st, t, 11, 640, 380, 1.0, 0.76)
    west_dallas(st, t, w, woz=False)
    x, _ = jazda(t, 0.0, 6.0, 300, 560)
    ciezarowka(st, t, x, 210)
    for n in range(4):
        uc = ease(pr(t, 6.5 + 0.2 * n, 1.2))
        st.put(J.zwierze("indyk"), x - 110 + 40 * n + 300 * uc * (1 if n % 2 else -0.6), 600 - 30 * math.sin(t * 9 + n) * (uc > 0) - 260 * uc,
               P.auta + 0.004, h=70, anchor=(0.5, 1.0), rot=20 * uc * (1 if n % 2 else -1) + 6 * math.sin(t * 7 + n))
    lalka(st, t, "clyde_nastolatek", x - 250, 270, flip=1, lean=12, rece=(90, 80), hop=4)
    lalka(st, t, "buck", x - 340, 300, flip=1, lean=14, rece=(90, 80), hop=4)
    px, _ = jazda(t, 4.8, 1.4, 1400, 1080)
    out = lalka(st, t, "policjant", px, 320, flip=-1, rece=(40 + 90 * ease(pr(t, 5.8, 0.4)), 10), hop=5 * (t < 6.2))
    if out and t > 5.8:
        st.put(J.rek("gwizdek"), out[0] - 10, out[1] - 30, P.lalki + 0.03, h=16, anchor=(0.5, 0.5))
    tab(w, t, "STOP!", 1080, 220, 6.0, 2.0)
    koniec(st, w, t)


def s_szkola(st, w, t, T):
    """Mała Bonnie wbiega na podium po dyplom; klasa klaszcze, z nitki zjeżdża złota gwiazdka."""
    kam(st, t, 12, 640, 380, lerp(1.0, 1.1, ease(t / T)), 0.78)
    wnetrze(st, t, w, sciana="zielen", okna=(200, 1080), meble=(("szafka", 1180, 200, None),))
    J.hang(st, J.rek("tablica_szkolna"), 640, 80, P.miasto + 0.01, bk(w, 0.3), t, 430, w=520, drop=520, sway=0.3, strings=(0.1, 0.9))
    Z0.rise(st, J.rek("podium"), 640, 712, P.drzewa, bk(w, 0.4), t, 431, h=90, wob=0.0)
    lalka(st, t, "nauczycielka", 860, 300, flip=-1, rece=(70, 0), trzyma=(J.rek("dyplom"), 60, (0.5, 0.5), 80, True) if t < 3.6 else None)
    bx, _ = jazda(t, 0.5, 2.4, 300, 620)
    on = ease(pr(t, 2.6, 0.4))
    lalka(st, t, "bonnie_mala", bx, 200, flip=1, lift=46 * on, hop=8 * (t < 2.9), rece=(lerp(0, 150, ease(pr(t, 3.6, 0.5))), 0),
          trzyma=(J.rek("dyplom"), 60, (0.5, 0.5), 80, True) if t >= 3.6 else None)
    for n, (x, key) in enumerate(((180, "dziecko1"), (300, "dziecko2"), (1000, "dziecko3"), (1110, "dziecko2"))):
        kl = (math.sin(t * 9 + n) > 0) * (t > 4.0)
        lalka(st, t, key, x, 170, 1.0, flip=1 if x < 640 else -1, rece=(60 + 30 * kl, 60 + 30 * kl), p=P.lalki + 0.02)
    J.hang(st, Z0.prop("gwiazdka"), 640, 140, P.rekwizyty, pr(t, 4.4, 1.0), t, 432, h=70, drop=420)
    koniec(st, w, t)


def s_slub(st, w, t, T):
    """Piętnastoletnia Bonnie i Roy Thornton pod łukiem z papierowych kwiatów; z góry zjeżdża tabliczka-tatuaż z dwoma sercami."""
    kam(st, t, 13, 640, 380, lerp(1.0, 1.18, ease(t / T)), 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(240, 1040))
    for n in range(9):
        a = math.pi * (0.1 + 0.8 * n / 8)
        J.hang(st, J.rek("kwiaty"), 640 - 260 * math.cos(a), 470 - 300 * math.sin(a), P.drzewa, bk(w, 0.3 + 0.05 * n), t, 440 + n, h=70,
               drop=400, sway=0.6, string=False)
    lalka(st, t, "bonnie_slub", 560, 270, flip=1, rece=(30, 10))
    lalka(st, t, "roy", 730, 320, flip=-1, rece=(30, 10))
    J.hang(st, J.tatuaz(), 640, 120, P.rekwizyty, pr(t, 3.2, 1.0), t, 450, w=300, drop=480)
    podpis(w, t, "Roy Thornton", 730, 150, 1.2, 2.4)
    koniec(st, w, t)


def s_roy(st, w, t, T):
    """Roy wychodzi z walizką drzwiami, które zostają otwarte; Bonnie przy oknie obraca obrączkę; zjeżdża zawieszka „1929”."""
    kam(st, t, 14, 640, 380, 1.05, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(330,), drzwi=(1040,), meble=(("stol", 640, 140, None),))
    rx, kr = jazda(t, 0.4, 2.6, 720, 1060)
    lalka(st, t, "roy", rx, 320, 1.0 - ease(pr(t, 3.0, 0.5)), flip=1, rece=(0, 0), trzyma=(J.rek("walizka"), 70, (0.5, 0.15), 0, False), hop=5)
    lalka(st, t, "bonnie", 360, 290, flip=-1 + 2 * ease(pr(t, 4.0, 0.6)), rece=(70 + 8 * math.sin(t * 3), 50))
    w.zawieszki = [("1929", 640, 150, pr(t, 5.0, 1.0))]
    koniec(st, w, t)


def s_kawiarnia(st, w, t, T):
    """Bonnie w fartuszku nalewa kawę; klient za gazetą nie podnosi wzroku; Bonnie przewraca oczami i odstawia dzbanek z hukiem."""
    hk = 3.2 < t < 3.5
    kam(st, t, 15, 640, 390, 1.15, 0.8, shake=3.0 * hk)
    wnetrze(st, t, w, sciana="paski", okna=(260, 1020), meble=(("lada", 640, 150, P.drzewa),))
    lalka(st, t, "przechodzien2", 820, 300, flip=-1, rece=(90, 90), trzyma=(J.gazeta("DEPRESSION DEEPENS", 5, 360, 480), 130, (0.5, 0.7), 90, True))
    lalka(st, t, "bonnie_kelnerka", 520, 290, flip=1, lean=-6 * ease(pr(t, 0.6, 0.5)) * (1 - ease(pr(t, 2.6, 0.4))),
          rece=(80 + 10 * ease(pr(t, 0.6, 0.5)) - 30 * ease(pr(t, 2.9, 0.3)), 10), trzyma=(J.rek("dzbanek"), 60, (0.5, 0.2), 30 * (t < 2.6), True))
    st.put(J.rek("kubek"), 700, 610, P.drzewa + 0.01, h=30, anchor=(0.5, 1.0))
    tab(w, t, "SIGH…", 520, 230, 2.4, 1.8)
    koniec(st, w, t)


def s_kuchnia(st, w, t, T):
    """W ciasnej kuchni Bonnie miesza kakao; drzwiami wchodzi Clyde w kapeluszu i uchyla go; z nitki zjeżdżają dwa serduszka."""
    kam(st, t, 16, 640, 390, 1.1, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(("kuchenka", 420, 220, None), ("stol", 760, 140, None)))
    st.put(J.rek("garnek"), 420, 494, P.wzgorza + 0.01, h=50, anchor=(0.5, 1.0))
    out = lalka(st, t, "przyjaciolka", 640, 290, flip=1, rece=(10, 0))
    lalka(st, t, "bonnie", 500, 290, flip=-1, rece=(70 + 15 * math.sin(t * 6), 0), trzyma=(J.rek("lyzka"), 50, (0.5, 0.9), 180, True))
    cx, _ = jazda(t, 1.2, 1.8, 1180, 900)
    lalka(st, t, "clyde", cx, 320, flip=-1, rece=(lerp(0, 160, ease(pr(t, 3.2, 0.4))) * (1 - ease(pr(t, 4.2, 0.4))), 0), hop=5 * (t < 3.0))
    for n in range(2):
        J.hang(st, J.serce(), 620 + 90 * n, 160 + 20 * n, P.rekwizyty, pr(t, 4.4 + 0.3 * n, 1.0), t, 460 + n, h=60, drop=420)
    koniec(st, w, t)


def s_areszt(st, w, t, T):
    """Do kuchni wchodzi policjant i zakuwa Clyde'a w kajdanki; Bonnie zostaje z łyżką w ręce; „HEY!”."""
    kam(st, t, 17, 700, 390, 1.1, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(("kuchenka", 420, 220, None), ("stol", 760, 140, None)))
    lalka(st, t, "bonnie", 500, 290, flip=1, rece=(60, 0), trzyma=(J.rek("lyzka"), 50, (0.5, 0.9), 180, True))
    px, _ = jazda(t, 0.2, 1.4, 1200, 1000)
    wyprow = ease(pr(t, 3.4, 2.2))
    lalka(st, t, "policjant", px + 160 * wyprow, 320, flip=-1 if wyprow == 0 else 1, rece=(80, 0), hop=5 * (t < 1.6))
    out = lalka(st, t, "clyde", 880 + 180 * wyprow, 320, 1.0 - ease(pr(t, 5.2, 0.4)), flip=1 if wyprow > 0 else -1, rece=(40, 40))
    if out and t > 1.8:
        st.put(J.rek("kajdanki"), out[0], out[1], P.lalki + 0.03, h=26, anchor=(0.5, 0.5))
    tab(w, t, "HEY!", 500, 240, 2.2, 2.0)
    koniec(st, w, t)


def s_waco(st, w, t, T):
    """Przy kratach Bonnie wyjmuje spod płaszcza pistolet i podaje go przez pręty; strażnik w tle ziewa i patrzy w drugą stronę."""
    kam(st, t, 18, 640, 380, 1.2, 0.8)
    wnetrze(st, t, w, sciana="tynk", meble=(("krzeslo", 1080, 170, None),), zarowki=(900,), noc_za_oknem=True)
    lalka(st, t, "straznik", 1080, 310, flip=1, lean=-6 * math.sin(t * 1.2), rece=(150 * ease(pr(t, 2.0, 0.5)) * (1 - ease(pr(t, 3.2, 0.5))), 0))
    if 2.0 < t < 3.6:
        tab(w, t, "YAWN", 1080, 200, 2.0, 1.4)
    lalka(st, t, "clyde_wiezien", 720, 320, flip=-1, rece=(70 * ease(pr(t, 3.6, 0.5)), 0), p=P.wzgorza + 0.02)
    st.put(J.kraty(560, 640), 660, 712, P.drzewa, h=470, anchor=(0.5, 1.0))
    d = ease(pr(t, 2.4, 1.2))
    lalka(st, t, "blanche" if False else "bonnie", 460, 290, flip=1, rece=(lerp(10, 95, d), 0), trzyma=REV() if t > 1.4 else None)
    koniec(st, w, t)


def s_ohio(st, w, t, T):
    """Clyde w nowym kapeluszu przechadza się po peronie w Ohio i gwiżdże; z obu stron wchodzą policjanci; „OH NO”."""
    kam(st, t, 19, 640, 380, 1.0, 0.76)
    miasto(st, t, w, fasady=(("dworzec", 640),), tyl=(("dom", 160), ("dom", 1120)))
    cx = 560 + 70 * math.sin(t * 0.8)
    lalka(st, t, "clyde", cx, 320, flip=math.copysign(1, math.cos(t * 0.8)), rece=(10, 0), hop=4 * (t < 4.0))
    if t < 4.0:
        tab(w, t, "♪", cx + 40, 230, 0.6, 3.0)
    lx, _ = jazda(t, 3.4, 1.6, -100, 300)
    rx, _ = jazda(t, 3.6, 1.6, 1400, 840)
    lalka(st, t, "policjant", lx, 320, flip=1, rece=(60, 0), hop=5 * (t < 5.0))
    lalka(st, t, "policjant2", rx, 330, flip=-1, rece=(60, 0), hop=5 * (t < 5.2))
    tab(w, t, "OH NO", cx, 210, 5.0, 2.2)
    koniec(st, w, t)


def s_eastham(st, w, t, T):
    """Eastham: więźniowie w pasiakach tną bawełnę, każdy w swoim rytmie; strażnik na koniu jedzie wzdłuż rzędu; słońce praży."""
    kam(st, t, 20, 640, 380, lerp(0.98, 1.08, ease(t / T)), 0.76)
    eastham(st, t, w)
    for n, (x, key) in enumerate(((200, "wiezien"), (380, "clyde_wiezien"), (560, "wiezien2"), (920, "wiezien"), (1100, "wiezien2"))):
        tempo = 2.0 + 0.4 * n
        mach = 0.5 + 0.5 * math.sin(t * tempo + n * 1.3)
        lalka(st, t, key, x, 300, bk(w, 0.6 + 0.05 * n), flip=1, lean=10 * mach, rece=(40 + 60 * mach, 20 + 30 * mach), p=P.drzewa + 0.01,
              trzyma=(J.rek("siekiera"), 60, (0.1, 0.5), 0, True) if n != 1 else None)
    kx = 1300 - (t / T) * 900
    st.put(J.zwierze("kon", int(t * 4) % 2), kx, 712, P.lalki + 0.01, h=230, anchor=(0.5, 1.0), sx=-1, rot=2 * math.sin(t * 6))
    lalka(st, t, "straznik", kx + 20, 300, y=712 - 150, flip=-1, rece=(40, 0), p=P.lalki + 0.005, trzyma=KARABIN(150))
    koniec(st, w, t, extra=(1.04, 1.0, 0.92))


def s_eastham_rura(st, w, t, T):
    """Teatr cieni w baraku: cień rosłego więźnia pochyla się nad Clyde'em; Clyde chwyta rurę, cień przeciwnika pada."""
    kam(st, t, 21, 640, 470, 1.55, 0.79, lens=1.4, shake=4.0 * (5.0 < t < 5.3))
    st.dof = 1.6
    y0, p0, ph = parawan(st, t, w)
    pochyl = ease(pr(t, 0.5, 1.8))
    cios = ease(pr(t, 4.6, 0.4))
    padnie = ease(pr(t, 5.3, 1.2))
    cien(st, t, "olbrzym", 720, 330, y0 - 26, p0 + 0.001, flip=-1, lean=-18 * pochyl + 40 * padnie, rece=(80 * pochyl, 60 * pochyl),
         sink=0.9 * padnie)
    out = cien(st, t, "clyde_wiezien", 540, 260, y0 - 26, p0 + 0.001, flip=1, lean=6 * pochyl, rece=(lerp(30, 170, ease(pr(t, 3.4, 0.6))) - 120 * cios, 20))
    if out and t > 3.4:
        st.put(J.rek("rura"), out[0], out[1], p0 + 0.002, h=11, anchor=(0.1, 0.5), rot=out[2] - 90, tint=(0.08, 0.06, 0.05), alpha=0.85,
               shadow=None, blur=1.6)
    koniec(st, w, t, dim=0.92)


def s_palce(st, w, t, T):
    """Na polu cień siekiery opada poza kadrem; Clyde łapie się za but i podskakuje na jednej nodze; „AW!” i gwiazdki."""
    kam(st, t, 22, 600, 420, 1.45, 0.8)
    st.dof = 1.3
    eastham(st, t, w, wieza=False, kul=False)
    f = pr(t, 1.0, 0.45)
    if 0 < f < 1:
        st.put(J.rek("siekiera"), 520, 400 + 300 * f * f, P.lalki + 0.03, h=90, anchor=(0.1, 0.5), rot=-60 + 120 * f, tint=(0.1, 0.08, 0.07),
               alpha=0.7, shadow=None, blur=2.0)
    hop = t > 1.5
    lalka(st, t, "clyde_wiezien", 600 + 20 * math.sin(t * 6) * hop, 320, flip=1, lean=-12 * hop, lift=30 * abs(math.sin(t * 7)) * hop,
          rece=(50 + 60 * hop, 60 + 40 * hop), gwiazdki=ease(pr(t, 1.6, 0.4)) * (1 - ease(pr(t, 4.0, 0.5))))
    tab(w, t, "AW!", 640, 230, 1.6, 2.0)
    koniec(st, w, t, extra=(1.04, 1.0, 0.92))


def _brama(st, w, t, otw):
    eastham(st, t, w, brama=1.0, wieza=True, kul=False)
    for strona in (-1, 1):
        x = 640 + strona * (210 + 190 * ease(otw))
        st.put(J.skrzydlo_bramy(), x, 700, P.wzgorza + 0.025, h=300, anchor=(0.5, 1.0), sx=strona * (1 - 0.7 * ease(otw)))


def s_parol(st, w, t, T):
    """Brama się otwiera; Clyde wychodzi o kulach; strażnik macha za nim kartką „PAROLE”; Clyde patrzy na bandaż na stopie."""
    kam(st, t, 23, 640, 400, 1.15, 0.8)
    _brama(st, w, t, pr(t, 0.4, 1.6))
    cx, _ = jazda(t, 1.6, 3.6, 640, 900)
    lalka(st, t, "clyde", cx, 320, flip=1, rece=(30, 30), trzyma=(J.rek("kula"), 210, (0.5, 0.1), 0, False), kuleje=1.0, hop=6 * (1.6 < t < 5.2))
    lalka(st, t, "straznik", 560, 320, flip=1, rece=(120 + 30 * math.sin(t * 8), 0), trzyma=(J.rek("parole"), 70, (0.5, 0.2), 70, True))
    koniec(st, w, t)


def s_przysiega(st, w, t, T):
    """Clyde o kulach odwraca się do bramy, która zamyka się za nim z hukiem; tabliczka „NEVER AGAIN”."""
    hk = 2.2 < t < 2.5
    kam(st, t, 24, 820, 380, 1.5, 0.81, shake=5.0 * hk)
    st.dof = 1.3
    _brama(st, w, t, 1 - pr(t, 1.6, 0.6))
    lalka(st, t, "clyde", 900, 320, flip=1 - 2 * ease(pr(t, 0.6, 0.6)), rece=(30, 30), trzyma=(J.rek("kula"), 210, (0.5, 0.1), 0, False))
    tab(w, t, "NEVER AGAIN", 900, 200, 3.0, 5.0)
    koniec(st, w, t)
