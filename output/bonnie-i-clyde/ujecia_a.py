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
    w.zawieszki = [("West Dallas, 1920s", 640, 150, pr(t, 1.4, 1.0))]  # miejsce i czas zamiast kurtyny aktu I (retrospekcja)
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


# ===================== AKT II · JAK ZOSTAĆ NAJBARDZIEJ POSZUKIWANYM =====================

from scena import ciemnosc, las, wawoz, mapa_scena, mapa_punkt, motocykl, ksiezyc, _off  # noqa: E402


def s_akt2(st, w, t, T):
    """Droga wśród pól; z ziemi wyrasta stacja benzynowa z jednym dystrybutorem; Ford wjeżdża z lewej i staje przy niej."""
    kam(st, t, 25, 640, 400, lerp(0.95, 1.05, ease(t / T)), 0.76)
    preria(st, t, w, slupy=True, wiatrak=True)
    Z0.rise(st, J.fasada("stacja"), 960, 650, P.most, bk(w, 0.9, 0.9), t, 470, h=330, wob=0.0)
    x, k = jazda(t, 1.4, 4.0, -300, 640)
    auto(st, t, x, pasazerowie=[("clyde", 1, (40, 0))])
    koniec(st, w, t)


def s_stacja(st, w, t, T):
    """Clyde wpada do budki stacji z rewolwerem; kasjer otwiera szufladę: kilka monet i guzik; „THAT'S IT?”."""
    kam(st, t, 26, 640, 450, 1.25, 0.8)
    miasto(st, t, w, fasady=(("stacja", 640),), tyl=(), chodnik=True)
    out_k = lalka(st, t, "kasjer", 760, 300, flip=-1, rece=(lerp(10, 80, ease(pr(t, 2.4, 0.6))), 60 * ease(pr(t, 1.2, 0.3))))
    cx, _ = jazda(t, 0.2, 1.4, 200, 520)
    lalka(st, t, "clyde", cx, 330, flip=1, rece=(90, 0), trzyma=REV(), hop=6 * (t < 1.6))
    if out_k and t > 2.9:
        for n in range(3):
            st.put(Z0.coin(), out_k[0] - 20 + 14 * n, out_k[1] - 6, P.lalki + 0.03, h=12, anchor=(0.5, 0.5))
        st.put(J.rek("pinezka"), out_k[0] + 26, out_k[1] - 4, P.lalki + 0.03, h=10, anchor=(0.5, 0.5), tint=(0.5, 0.4, 0.3))
    tab(w, t, "THAT'S IT?", 560, 250, 3.4, 2.6)
    koniec(st, w, t)


def s_kaufman(st, w, t, T):
    """Nocą Ford grzęźnie w błocie po kołpaki; Clyde i Bonnie wskakują na dwa muły, muły ani drgną; „GO!”."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 27, 700, 500, 1.15, 0.78)
    preria(st, t, w, slupy=False, kolor_drogi=(110, 90, 70), noc=1.0)
    x, _ = jazda(t, 0.0, 1.8, -300, 400, ease_out)
    zapada = ease(pr(t, 1.4, 1.4))
    buksuje = 1.4 < t < 3.4
    w_aucie = t < 3.7
    auto(st, t, x + 4 * math.sin(t * 30) * buksuje, y=DROGA_Y + 40 * zapada, droga=x + 900 * pr(t, 1.4, 2.0), przechyl=-3 * zapada,
         pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))] if w_aucie else ())
    st.put(J.pasmo("bloto", 1), 400, 800, P.auta + 0.006, w=1100, anchor=(0.5, 1.0), shadow=None)
    if buksuje:
        for n in range(5):
            f = (t * 2.2 + n / 5) % 1.0
            st.put(J.glow(r=256, color=(90, 70, 50)), 300 - 200 * f, 690 - 120 * math.sin(math.pi * f), P.auta + 0.008, w=26, anchor=(0.5, 0.5),
                   alpha=0.9, shadow=None)
    for n, (key, mx) in enumerate((("clyde", 860), ("bonnie", 1090))):
        st.put(J.zwierze("mul"), mx, 712, P.lalki + 0.006, h=210, anchor=(0.5, 1.0))
        if not w_aucie:
            sk = ease(pr(t, 3.9 + 0.5 * n, 0.9))
            xx = lerp(440 + 70 * n, mx - 10, sk)
            lalka(st, t, key, xx, 300 - 24 * n, flip=1, lift=lerp(0, 12, sk) + 110 * math.sin(math.pi * sk),
                  rece=(60 + 40 * math.sin(t * 8) * (t > 5.6), 40), p=P.lalki + (0.004 if sk > 0.5 else 0.012))
    tab(w, t, "GO!", 980, 250, 5.6, 2.2)
    tab(w, t, "...", 980, 250, 8.2, 2.4)
    koniec(st, w, t)


def s_cela(st, w, t, T):
    """Bonnie w celi siedzi na pryczy i pisze w zeszycie; zapisane kartki odrywają się i fruwają po celi jak ptaki."""
    kam(st, t, 28, 640, 460, 1.2, 0.8)
    wnetrze(st, t, w, sciana="tynk", meble=(("lozko", 640, 120, P.lalki + 0.02),), okna=(), zarowki=(640,))
    lalka(st, t, "bonnie", 600, 290, flip=1, sink=0.15, lean=4, rece=(80 + 8 * math.sin(t * 9), 70), trzyma=(J.rek("zeszyt"), 46, (0.5, 0.5), 80, True))
    for n in range(6):
        f = pr(t, 2.0 + 0.9 * n, 3.4)
        if 0 < f < 1:
            x = 660 + 420 * f * math.cos(n * 1.7 + 0.4) + 30 * math.sin(t * 3 + n)
            y = 470 - 300 * f + 30 * math.sin(t * 5 + n)
            st.put(J.rek("list"), x, y, P.rekwizyty - 0.02, h=70, anchor=(0.5, 0.5), rot=20 * math.sin(t * 6 + n), sx=0.25 + 0.75 * abs(math.cos(t * 7 + n)),
                   shadow=(3, 4, 4, 0.3))
    st.put(J.kraty(1500, 760, krok=170), 640, 790, 0.9, h=800, anchor=(0.5, 1.0), blur=2.0)
    koniec(st, w, t, dim=0.95)


def s_hillsboro(st, w, t, T):
    """Teatr cieni: napad w sklepie w Hillsboro, błysk, sylwetka sprzedawcy opada za ladę; muzyka cichnie."""
    kam(st, t, 29, 640, 470, 1.5, 0.79, lens=1.4, shake=3.0 * (4.0 < t < 4.3))
    st.dof = 1.6
    y0, p0, ph = parawan(st, t, w)
    st.put(J.mebel("lada"), 560, y0 - 30, p0 + 0.001, h=110, anchor=(0.5, 1.0), tint=(0.08, 0.06, 0.05), alpha=0.85, shadow=None, blur=1.6)
    padnie = ease(pr(t, 4.2, 1.2))
    cien(st, t, "bucher", 540, 270, y0 - 60, p0 + 0.0005, flip=1, rece=(60, 0), sink=0.9 * padnie, lean=-20 * padnie)
    rx, _ = jazda(t, 0.6, 2.4, 1000, 800)
    cien(st, t, "clyde", rx, 300, y0 - 26, p0 + 0.002, flip=-1, rece=(90, 0), trzyma=REV())
    blysk(st, 760, y0 - 200, p0 + 0.003, t, 4.0, r=300)
    podpis(w, t, "John Bucher", 540, 200, 5.4, 3.0)
    koniec(st, w, t, dim=0.9)


def s_matka_obietnica(st, w, t, T):
    """Bonnie wychodzi z aresztu prosto w objęcia matki i kiwa głową; za płotem stoi Ford, Clyde cicho trąbi."""
    kam(st, t, 30, 640, 430, 1.1, 0.8)
    miasto(st, t, w, fasady=(("dom", 420), ("areszt", 1040)), tyl=(("dom", 200),), chodnik=True)
    Z0.rise(st, J.plot(2, False), 640, 690, P.drzewa, bk(w, 0.5), t, 480, w=1500, wob=0.0)
    auto(st, t, 900, 220, y=660, p=P.wzgorza + 0.02, pasazerowie=[("clyde", 1, (40 + 30 * (t > 5.5), 0))])
    bx, _ = jazda(t, 0.4, 2.0, 1060, 640)
    przytul = ease(pr(t, 2.4, 0.6)) * (1 - ease(pr(t, 6.0, 0.5)))
    lalka(st, t, "bonnie", bx, 290, flip=-1, lean=-8 * przytul + 4 * math.sin(t * 6) * (3.6 < t < 4.6), rece=(90 * przytul, 70 * przytul))
    lalka(st, t, "matka_bonnie", 560, 290, flip=1, lean=8 * przytul, rece=(90 * przytul, 70 * przytul))
    tab(w, t, "BEEP", 900, 360, 5.6, 1.8)
    koniec(st, w, t)


def s_atoka(st, w, t, T):
    """Teatr cieni: pary wirują na potańcówce w Atoce; dwaj stróże prawa podchodzą do auta; błyski, jedna sylwetka pada."""
    kam(st, t, 31, 640, 470, 1.45, 0.79, lens=1.4, shake=3.0 * (6.0 < t < 6.3))
    st.dof = 1.6
    y0, p0, ph = parawan(st, t, w)
    for n, (x, a, b) in enumerate(((290, "przechodnia2", "przechodzien"), (560, "przechodnia", "przechodzien3"))):
        fl = math.cos(t * 2.4 + 1.3 * n)  # para wiruje: zamienia się miejscami, przy obrocie sylwetki chudną
        sk = 6 * math.sin(t * 4.8 + n)
        cien(st, t, a, x - 44 * fl, 230, y0 - 26 - abs(sk), p0 + 0.001 + 0.0004 * (fl < 0), flip=fl, rece=(80, 100), lean=sk)
        cien(st, t, b, x + 44 * fl, 250, y0 - 26 - abs(sk), p0 + 0.0012 - 0.0004 * (fl < 0), flip=-fl, rece=(80, 100), lean=-sk)
    auto(st, t, 860, 170, y=y0 - 26, p=p0 + 0.0008, tint=(0.08, 0.06, 0.05), alpha=0.85, shadow=None, blur=1.6, szyby=False)
    lx, _ = jazda(t, 2.0, 3.0, 1200, 980)
    padnie = ease(pr(t, 6.2, 1.2))
    cien(st, t, "moore", lx, 260, y0 - 26, p0 + 0.002, flip=-1, rece=(40, 0), sink=0.9 * padnie, lean=20 * padnie)
    cien(st, t, "szeryf", lx + 90, 270, y0 - 26, p0 + 0.0015, flip=-1, rece=(40, 0))
    blysk(st, 900, y0 - 160, p0 + 0.003, t, 6.0, r=280)
    blysk(st, 920, y0 - 150, p0 + 0.003, t, 6.25, r=240)
    podpis(w, t, "Eugene Moore", lx, 200, 7.6, 3.0)
    koniec(st, w, t, dim=0.9)


def s_wd(st, w, t, T):
    """Do auta wsiada chudy chłopak z nieśmiałym uśmiechem i zatrzaskuje drzwi; podpis „W.D. Jones, 16”."""
    kam(st, t, 32, 640, 440, 1.2, 0.79)
    preria(st, t, w, slupy=True)
    w_srodku = t > 3.4
    auto(st, t, 640, pasazerowie=[("clyde", 1, (40, 0))] + ([("wd", 0, (0, 0))] if w_srodku else []))
    if not w_srodku:
        x, _ = jazda(t, 0.4, 2.6, 1100, 640)
        lalka(st, t, "wd", x, 280, 1.0 - ease(pr(t, 2.9, 0.5)), flip=-1, rece=(20, 0), hop=5)
    podpis(w, t, "W.D. Jones, 16", 640, 220, 3.6, 3.0)
    if 3.4 < t < 3.7:
        st.dim = 1.0
    koniec(st, w, t)


def s_buck(st, w, t, T):
    """Z bramy więzienia wychodzi Buck z ułaskawieniem w ręku; czeka Blanche w kapelusiku, z białym pieskiem na rękach."""
    kam(st, t, 33, 640, 430, 1.05, 0.8)
    miasto(st, t, w, fasady=(("wiezienie", 640),), tyl=(), chodnik=True)
    bx, _ = jazda(t, 0.6, 2.6, 640, 820)
    lalka(st, t, "buck", bx, 320, flip=1, rece=(110, 0), trzyma=(J.rek("pardon"), 60, (0.5, 0.2), 70, True), hop=5 * (t < 3.2))
    out = lalka(st, t, "blanche", 1020, 290, flip=-1, rece=(70, 70))
    if out:
        st.put(J.zwierze("piesek"), out[0] + 10, out[1] - 10, P.lalki + 0.03, h=46, anchor=(0.5, 0.6), sx=-1, rot=6 * math.sin(t * 4))
    podpis(w, t, "Buck Barrow", bx, 230, 1.6, 3.0)
    podpis(w, t, "Blanche Barrow", 1020, 230, 4.6, 3.0)
    koniec(st, w, t)


def s_joplin_dom(st, w, t, T):
    """Dwa auta zajeżdżają pod garaż z mieszkaniem na piętrze; zawieszka „Joplin, Missouri, 1933”; w oknach zapalają się światła."""
    w.noc = 0.6
    kam(st, t, 34, 640, 400, 1.0, 0.78)
    miasto(st, t, w, fasady=(("dom", 260), ("garaz", 760), ("dom", 1180)), swiatlo_okien=t > 7.0, latarnie=(520,))
    x1, _ = jazda(t, 0.4, 3.0, -300, 600)
    x2, _ = jazda(t, 1.4, 3.2, -500, 1000)
    auto(st, t, x1, 220, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    auto(st, t, x2, 210, kolor="bordo", p=P.auta + 0.005, pasazerowie=[("blanche", 0, (0, 0)), ("buck", 1, (40, 0))])
    w.zawieszki = [("Joplin, Missouri, 1933", 640, 120, pr(t, 2.0, 1.0))]
    koniec(st, w, t)


def s_joplin_karty(st, w, t, T):
    """Buck i Blanche grają w karty, Clyde dmucha w saksofon, Bonnie pisze; za ścianą sąsiadka przykłada ucho; „SHHH!”."""
    kam(st, t, 35, 680, 450, 1.1, 0.8)
    w.noc = 1.0
    wnetrze(st, t, w, sciana="paski", okna=(1150,), meble=(("stol", 700, 130, P.lalki + 0.02),), zarowki=(700,))
    st.put(J.sciana("zielen"), 330, 720, P.miasto + 0.004, h=760, anchor=(1.0, 1.0), shadow=(8, 0, 12, 0.5))
    st.put(J.listwa(60, 900), 330, 760, P.lalki + 0.03, h=900, anchor=(0.5, 1.0))
    lalka(st, t, "przechodnia2", 236, 280, flip=1, lean=10 + 2 * math.sin(t * 2), rece=(150, 0))
    lalka(st, t, "bonnie", 450, 290, flip=1, lean=4, rece=(80 + 6 * math.sin(t * 9), 60), trzyma=(J.rek("zeszyt"), 40, (0.5, 0.5), 80, True))
    lalka(st, t, "buck", 620, 300, flip=1, sink=0.15, rece=(70 + 10 * math.sin(t * 3), 40), trzyma=(J.rek("karty"), 40, (0.5, 0.8), 0, True))
    lalka(st, t, "blanche", 790, 290, flip=-1, sink=0.15, rece=(70, 40), trzyma=(J.rek("karty"), 36, (0.5, 0.8), 0, True))
    out = lalka(st, t, "clyde", 1000, 320, flip=-1, lean=-6 + 6 * math.sin(t * 4), rece=(110, 90))
    if out:
        st.put(J.rek("saksofon"), out[0] - 10, out[1] - 60, P.lalki + 0.03, h=110, anchor=(0.5, 0.2), rot=-20 + 8 * math.sin(t * 4))
    tab(w, t, "SHHH!", 200, 250, 3.0, 3.0)
    koniec(st, w, t)


# ===================== AKT III · JAK ŻART ZROBIŁ Z NICH GWIAZDY =====================

def s_joplin_walka(st, w, t, T):
    """Teatr cieni: garaż w Joplin; dwaj policjanci podchodzą, z okien błyski, obaj padają; gang zbiega do auta i wyjeżdża."""
    strzaly = 4.2
    kam(st, t, 36, 640, 450, 1.3, 0.79, lens=1.4, shake=3.0 * (strzaly - 0.1 < t < strzaly + 1.0))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    st.put(J.fasada("garaz"), 470, y0 - 26, p0 + 0.0005, h=340, anchor=(0.5, 1.0), tint=(0.08, 0.06, 0.05), alpha=0.95, shadow=None, blur=1.6)
    for n, (x0, key) in enumerate(((1250, "detektyw"), (1330, "policjant"))):
        x, _ = jazda(t, 0.4 + 0.4 * n, 3.2, x0, 820 + 110 * n)
        pad = ease(pr(t, strzaly + 0.7 + 0.4 * n, 1.3))
        cien(st, t, key, x, 260, y0 - 26, p0 + 0.002, flip=-1, rece=(30 + 60 * (t > strzaly), 0), sink=0.9 * pad, lean=22 * pad)
    for n in range(6):
        blysk(st, 410 + 120 * (n % 2), y0 - 250, p0 + 0.003, t, strzaly + 0.2 * n, r=200)
    if t > 7.0:
        ax, _ = jazda(t, 7.2, 3.0, 470, -400, ease)
        auto(st, t, ax, 170, y=y0 - 26, p=p0 + 0.0025, tint=(0.08, 0.06, 0.05), alpha=0.95, shadow=None, blur=1.6, szyby=False, flip=-1)
    koniec(st, w, t, dim=0.9)


def s_joplin_ofiary(st, w, t, T):
    """Na pustym podwórku przed garażem leżą dwie czapki policyjne; z nitek zjeżdżają podpisy; światło przygasa."""
    kam(st, t, 37, 640, 520, 1.3, 0.8)
    miasto(st, t, w, fasady=(("garaz", 640),), tyl=())
    for n, x in enumerate((520, 780)):
        st.put(J.rek("czapka_policyjna"), x, 690, P.lalki + 0.02, h=54, anchor=(0.5, 1.0), rot=-10 + 22 * n)
    podpis(w, t, "Harry McGinnis", 520, 560, 1.0, T)
    podpis(w, t, "Wes Harryman", 780, 590, 1.8, T)
    koniec(st, w, t, dim=1.0 - 0.25 * ease(pr(t, 3.0, 3.0)))


def s_ciemnia(st, w, t, T):
    """W czerwonym świetle ciemni odbitka pływa w kuwecie; na papierze wyłania się Bonnie z rewolwerem i cygarem."""
    kam(st, t, 38, 640, 430, 1.25, 0.8)
    wnetrze(st, t, w, sciana="cegla", zarowki=(640,))
    st.line([(120, 150), (1160, 160)], P.wzgorza, width=1.6, color=(60, 40, 30))
    for n, x in enumerate((260, 420, 900, 1060)):  # suszące się odbitki na sznurku
        st.put(J.rek("klisza"), x, 154, P.wzgorza + 0.001, h=110, anchor=(0.5, 0.0), rot=3 * math.sin(t + n))
    lalka(st, t, "fotograf", 1010, 330, flip=-1, lean=-14, rece=(70, 30))
    st.put(J.rek("kuweta"), 600, 790, P.rekwizyty, w=760, anchor=(0.5, 1.0))
    f = ease(pr(t, 1.2, 4.5))
    plyw = 4 * math.sin(t * 1.3)
    st.put(J.zdjecie_bonnie(), 600 + plyw, 690, P.rekwizyty + 0.002, h=300, anchor=(0.5, 1.0), rot=-2 + plyw * 0.3,
           alpha=0.1 + 0.9 * f, tint=(0.75 + 0.25 * f,) * 3, shadow=None)
    koniec(st, w, t, extra=(1.35, 0.62, 0.58), dim=0.95)


def s_kiosk(st, w, t, T):
    """Gazeciarz macha gazetą; kolejka ludzi w łatanych płaszczach kupuje; sterta gazet rośnie aż do markizy; „EXTRA!”."""
    kam(st, t, 39, 640, 430, 1.05, 0.79)
    miasto(st, t, w, fasady=(("kiosk", 380), ("apteka", 900)), tyl=(("dom", 160), ("bank", 700)))
    lalka(st, t, "gazeciarz", 380, 240, flip=1, rece=(130 + 25 * math.sin(t * 8), 0), trzyma=(J.gazeta("OUTLAW GIRL WITH CIGAR", 7), 70, (0.5, 0.8), 90, True))
    for n in range(int(min(8, 1 + t * 0.8))):
        st.put(J.gazeta("EXTRA!", 60 + n, 360, 120, False), 250, 700 - 18 * n, P.lalki + 0.002, h=28, anchor=(0.5, 1.0), rot=3 * math.sin(n))
    for n, key in enumerate(("bezrobotny", "przechodnia", "przechodzien3", "przechodzien", "przechodnia2")):
        x = 560 + 120 * n - 60 * ease(pr(t, 2.0 + n * 0.3, 1.0))
        lalka(st, t, key, x, 300 - 6 * (n % 2), flip=-1, rece=(30 + 40 * (n == 0) * (t > 3), 0), hop=3 * (1 < t < 4))
    tab(w, t, "EXTRA!", 380, 240, 1.0, 3.0)
    koniec(st, w, t)


def s_cygaro_zlosc(st, w, t, T):
    """Bonnie w aucie czyta gazetę, marszczy brwi i wyrzuca cygaro przez okno; „CIGARETTES!”."""
    kam(st, t, 40, 560, 470, 1.5, 0.79)
    st.dof = 1.3
    preria(st, t, w, slupy=False, kul=False)
    auto(st, t, 640, 300, pasazerowie=[("bonnie", 1, (90, 80))])
    zgniata = ease(pr(t, 2.2, 0.5))
    st.put(J.gazeta("GUN MOLL WITH CIGAR", 9), 590, 540, P.auta + 0.003, h=lerp(96, 60, zgniata), anchor=(0.5, 0.5), rot=-6 + 30 * zgniata,
           sy=lerp(1.0, 0.6, zgniata))
    f = pr(t, 2.6, 1.0)
    if 0 < f < 1:
        st.put(J.rek("cygaro"), 760 + 300 * f, 470 - 120 * f + 260 * f * f, P.auta + 0.01, h=10, anchor=(0.5, 0.5), rot=720 * f)
    tab(w, t, "CIGARETTES!", 700, 300, 3.2, 3.0)
    koniec(st, w, t)


def s_darby_auto(st, w, t, T):
    """Gang odjeżdża cudzym autem sprzed domu; z domu wybiegają młody mężczyzna w garniturze i kobieta i wskakują do drugiego auta."""
    kam(st, t, 41, 640, 430, 1.0, 0.78)
    miasto(st, t, w, fasady=(("dom", 380), ("dom", 1000)), tyl=(("dom", 700),))
    x1, _ = jazda(t, 1.6, 3.4, 700, 1700)
    auto(st, t, x1, 210, kolor="granat", pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))])
    for n, key in enumerate(("darby", "stone")):
        x, _ = jazda(t, 4.2 + 0.3 * n, 1.8, 380, 220 - 60 * n)
        lalka(st, t, key, x, 300 - 10 * n, ease(pr(t, 4.0 + 0.3 * n, 0.4)) * (1.0 - ease(pr(t, 6.6 + 0.2 * n, 0.4))), flip=-1,
              rece=(120 * (n == 0), 0), hop=6)
    x2, _ = jazda(t, 7.4, 3.4, 160, 1700)
    auto(st, t, x2, 200, kolor="zielony", p=P.auta + 0.004, pasazerowie=([("stone", 0, (0, 0)), ("darby", 1, (60, 0))] if t > 7.0 else []))
    tab(w, t, "HEY!", 360, 300, 4.4, 2.2)
    koniec(st, w, t)


def s_darby_tyl(st, w, t, T):
    """Darby i Stone siedzą ściśnięci na tylnym siedzeniu; Bonnie odwraca się do nich i pyta; podpisy."""
    kam(st, t, 42, 640, 470, 1.55, 0.79)
    st.dof = 1.3
    preria(st, t, w, slupy=True, kul=False)
    x = 640 + 6 * math.sin(t * 9)
    obrot = -1 if t > 1.6 else 1
    auto(st, t, x, 300, droga=t * 400, pasazerowie=[("stone", (330, 132), (0, 0)), ("darby", (410, 126), (0, 0)),
                                                    ("bonnie", (505, 126), (60 * ease(pr(t, 2.0, 0.4)), 0), obrot)])
    podpis(w, t, "Dillard Darby, undertaker", 560, 250, 1.0, 3.6)
    podpis(w, t, "Sophia Stone", 440, 320, 2.0, 2.8)
    koniec(st, w, t)


def s_darby_smiech(st, w, t, T):
    """Bonnie wybucha śmiechem i klepie się po kolanie; Darby blednie; „HA HA!”."""
    kam(st, t, 43, 640, 470, 1.6, 0.8)
    st.dof = 1.3
    preria(st, t, w, slupy=False, kul=False)
    smiech = t > 0.8
    lalka(st, t, "bonnie", 560, 300, flip=1, lean=-10 * math.sin(t * 10) * smiech, rece=(40 + 50 * abs(math.sin(t * 6)) * smiech, 20))
    lalka(st, t, "darby", 760, 300, flip=-1, tint=(1.0 - 0.15 * ease(pr(t, 1.5, 1.0)), 1.0, 1.0 - 0.1 * ease(pr(t, 1.5, 1.0))), rece=(10, 0))
    tab(w, t, "HA HA!", 560, 250, 0.9, 3.0)
    koniec(st, w, t)


def s_darby_puszczeni(st, w, t, T):
    """Porwani wysiadają na poboczu; Clyde wręcza im przez okno banknot; Ford odjeżdża w kurzu, Darby zostaje z banknotem w ręce."""
    kam(st, t, 44, 640, 430, 1.1, 0.79)
    preria(st, t, w, tablice=[("WALDO 3 MI", 1060)])
    x, _ = jazda(t, 3.6, 3.0, 640, 1700)
    auto(st, t, x, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40 + 50 * (2.0 < t < 3.4), 0))], kurz=t > 3.6)
    if t > 3.6:
        for n in range(4):
            f = pr(t, 3.7 + 0.2 * n, 1.6)
            st.put(J.glow(r=256, color=(200, 180, 140)), x - 200 - 120 * f * n, 660 - 40 * f, P.auta + 0.01, w=160 + 180 * f, anchor=(0.5, 0.5),
                   alpha=0.5 * (1 - f), shadow=None)
    d = ease(pr(t, 0.4, 0.8))
    out = lalka(st, t, "darby", 380, 300, d, flip=1, rece=(lerp(0, 90, ease(pr(t, 2.2, 0.5))), 0))
    lalka(st, t, "stone", 250, 290, d, flip=1, rece=(10, 0))
    if out and t > 2.8:
        st.put(J.rek("banknot"), out[0], out[1], P.lalki + 0.03, h=22, anchor=(0.3, 0.5), rot=-8)
    koniec(st, w, t)


def _biuro_hamera(st, t, w, teczka=1.0):
    """Biuro w Austin: zielona ściana, puste biurko, krzesło z kapeluszem na oparciu, gruba teczka (zasiew łowcy)."""
    wnetrze(st, t, w, sciana="zielen", okna=(1080,), meble=(("biurko", 560, 170, None), ("krzeslo", 820, 200, None)), zarowki=(560,))
    st.put(J.rek("kapelusz_fedora"), 826, 520, P.wzgorza + 0.01, h=40, anchor=(0.5, 1.0), tint=(1.0, 0.95, 0.75))
    if teczka > 0:
        st.put(J.rek("teczka"), 560, 545, P.wzgorza + 0.012, h=70 * teczka, anchor=(0.5, 1.0))


def s_teczka_zasiew(st, w, t, T):
    """Wycinki z gazet odfruwają i jeden po drugim wpadają do grubej teczki na pustym biurku; na oparciu krzesła wisi kapelusz."""
    kam(st, t, 45, 640, 480, 1.45, 0.8)
    st.dof = 1.2
    _biuro_hamera(st, t, w)
    for n in range(7):
        f = pr(t, 0.6 + 1.3 * n, 1.6)
        if 0 < f < 1:
            st.put(J.gazeta(J.NAGLOWKI[n % len(J.NAGLOWKI)], 70 + n, 360, 300, False), lerp(1150, 560, f), lerp(380 - 10 * n, 520, f) - 90 * math.sin(math.pi * f),
                   P.rekwizyty - 0.02, h=lerp(130, 30, f), anchor=(0.5, 0.5), rot=360 * f + n * 40, shadow=(3, 4, 4, 0.3))
    koniec(st, w, t)


def s_plakaty(st, w, t, T):
    """Mapa z gazet: pinezki w Teksasie, Oklahomie, Missouri i Luizjanie; na mapie wyrastają ich twarze z listów gończych."""
    kam(st, t, 46, 640, 380, lerp(0.95, 1.05, ease(t / T)), 0.68)
    xy0x, xy0y, sk = mapa_scena(st, t, w)
    for n, miasto_ in enumerate(("Dallas", "Joplin", "Ruston", "Atoka", "Wellington")):
        k = pr(t, 1.2 + 0.6 * n, 0.8)
        px, py = mapa_punkt((xy0x, xy0y), sk, miasto_)
        if k > 0:
            J.hang(st, J.rek("plakat"), px, py - 70, P.wzgorza + 0.01 + 0.001 * n, k, t, 490 + n, h=90, drop=300, string=False)
            st.put(J.rek("pinezka"), px, py - 72, P.wzgorza + 0.02, h=14, anchor=(0.5, 0.5))
    koniec(st, w, t)


# ===================== AKT IV · ŻYCIE W UCIECZCE =====================

def _reflektory(st, x, y, p, flip=1.0, k=1.0):
    st.put(J.glow(r=256, color=(255, 240, 190)), x + 260 * flip, y - 80, p + 0.003, w=520, anchor=(0.5, 0.5), mode="add", alpha=0.45 * k, shadow=None)


def auto_srodek(st, t, cx, cy, h, rot, **kw):
    """Auto obrócone wokół własnego środka (dachowanie): auto() obraca się wokół linii kół."""
    ox, oy = _off(0, -h * 0.5, rot)
    auto(st, t, cx - ox, h, y=cy - oy, przechyl=rot, **kw)


def s_wellington_noc(st, w, t, T):
    """Nocna droga przez prerię, Ford pędzi z zapalonymi światłami; tablica „DETOUR” mija się w ciemności, nikt jej nie widzi."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 47, lerp(400, 900, ease(t / T)), 480, 1.1, 0.78, truck=1.0)
    preria(st, t, w, slupy=True, tablice=[("DETOUR", 900)], noc=1.0)
    x = lerp(-200, 1500, t / T)
    auto(st, t, x, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.7, 0.72, 0.85))
    _reflektory(st, x, DROGA_Y, P.auta)
    koniec(st, w, t)


def s_wellington_most(st, w, t, T):
    """Ford wjeżdża na rozebrany most, leci w wąwóz, przewraca się i bucha płomieniem; mocny wstrząs (szczyt 1)."""
    w.noc, w.moon = 1.0, 1.0
    uderzenie = 1.55
    h = 190
    kam(st, t, 48, 640, 420, 1.0, 0.75, shake=10.0 * (uderzenie < t < uderzenie + 0.5))
    wawoz(st, t, w)
    f = pr(t, 0.0, uderzenie)
    jazda_k = min(1.0, f / 0.35)
    spad = max(0.0, (f - 0.35) / 0.65)
    cx = lerp(120, 470, jazda_k) + 300 * spad
    cy = 235 + 382 * spad ** 2
    rot = 170 * spad ** 1.5 + 6 * math.sin(t * 20) * (uderzenie < t < uderzenie + 0.4)
    auto_srodek(st, t, cx, cy, h, rot, p=P.drzewa + 0.02, tint=(0.7, 0.72, 0.85), szyby=False, droga=cx + 600 * min(t, uderzenie))
    if t > uderzenie:
        g = ease(pr(t, uderzenie, 1.0))
        for n in range(3):
            st.put(Z0.flame(int(t * 12 + 3 * n) % 10), 800 + 45 * n, 640, P.drzewa + 0.025, h=(110 + 50 * n) * g, anchor=(0.5, 1.0), shadow=None)
        st.put(J.glow(), 760, 620, P.drzewa + 0.04, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.45 * g, shadow=None)
    koniec(st, w, t)


def s_wellington_bonnie(st, w, t, T):
    """Clyde i W.D. wyciągają Bonnie z płonącego auta; jej noga dymi; „AAAA!”."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 49, 640, 450, 1.25, 0.79)
    wawoz(st, t, w, przeslo=1.0)
    for n in range(3):
        st.put(Z0.flame(int(t * 12 + 3 * n) % 10), 720 + 60 * n, 640, P.auta - 0.004, h=150, anchor=(0.5, 1.0), shadow=None)
    auto_srodek(st, t, 790, 602, 220, 174, szyby=False, tint=(0.5, 0.45, 0.45), kola=True)
    st.put(J.glow(), 780, 560, P.auta + 0.02, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.4, shadow=None)
    wyciag = ease(pr(t, 0.6, 2.4))
    bx = lerp(640, 400, wyciag)
    lalka(st, t, "bonnie", bx, 290, flip=-1, lean=lerp(60, 10, wyciag), rece=(60, 40), kuleje=0.0)
    lalka(st, t, "clyde", bx - 110, 320, flip=1, lean=-10, rece=(90, 60))
    lalka(st, t, "wd", bx + 120, 280, flip=-1, lean=-10, rece=(90, 60))
    for n in range(3):
        g = ((t * 0.5 + n / 3) % 1.0)
        st.put(J.glow(r=256, color=(150, 140, 130)), bx + 20, 640 - 120 * g, P.lalki + 0.02, w=60 + 80 * g, anchor=(0.5, 0.5), alpha=0.5 * (1 - g),
               shadow=None)
    tab(w, t, "AAAA!", bx, 250, 1.4, 2.6)
    koniec(st, w, t, extra=(1.1, 0.9, 0.85))


def s_farma(st, w, t, T):
    """Rodzina farmerów nosi wiadra i opatruje Bonnie na ganku; drogą nadjeżdżają szeryf i marszałek."""
    kam(st, t, 50, 640, 430, 1.05, 0.79)
    preria(st, t, w, slupy=True, plot=False)
    Z0.rise(st, J.fasada("dom"), 420, 660, P.most, bk(w, 0.4), t, 500, h=340, wob=0.0)
    lalka(st, t, "bonnie", 420, 280, flip=1, lean=-4, rece=(20, 0))
    for n, (key, x0) in enumerate((("farmer", 120), ("farmerka", 700))):
        x = x0 + 60 * math.sin(t * 1.2 + n)
        lalka(st, t, key, x, 300, flip=math.copysign(1, math.cos(t * 1.2 + n)), rece=(30, 0), trzyma=(J.rek("wiadro"), 40, (0.5, 0.1), 0, False))
    x, _ = jazda(t, 4.2, 3.6, 1600, 1000)
    auto(st, t, x, 210, kolor="czarny", napis="SHERIFF", flip=-1, pasazerowie=[("szeryf", 0, (0, 0)), ("detektyw", 1, (40, 0))])
    koniec(st, w, t)


def s_drzewo(st, w, t, T):
    """Szeryf i marszałek przywiązani drutem kolczastym do drzewa; Clyde macha im z auta na pożegnanie; „BYE!”."""
    kam(st, t, 51, 640, 430, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", krzaki=False)
    Z0.rise(st, J.drzewo(7), 420, 712, P.lalki - 0.004, bk(w, 0.3), t, 510, h=600, wob=0.0)
    for n, (key, x) in enumerate((("szeryf", 350), ("detektyw", 490))):
        lalka(st, t, key, x, 300, flip=1 if n else -1, rece=(0, 0), lean=3 * math.sin(t * 3 + n))
    for y in (500, 560, 620):  # drut kolczasty: jasny drut i kolce co kawałek
        st.line([(290, y), (550, y + 6)], P.lalki + 0.02, width=3.0, color=(170, 170, 176), alpha=0.95)
        for n in range(9):
            xx = 300 + 30 * n
            yy = y + 6 * (xx - 290) / 260
            st.line([(xx - 5, yy - 6), (xx + 5, yy + 6)], P.lalki + 0.021, width=2.0, color=(150, 150, 156))
    x, _ = jazda(t, 2.4, 4.6, 900, 1700)
    auto(st, t, x, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (120 + 30 * math.sin(t * 10), 0))])
    tab(w, t, "BYE!", min(x, 1100), 300, 1.4, 3.0)
    koniec(st, w, t)


def s_noszenie(st, w, t, T):
    """Clyde niesie Bonnie na rękach z auta do pokoju motelu; noga w bandażu; Bonnie krzywi się przy każdym jego kroku."""
    kam(st, t, 52, 640, 450, 1.2, 0.79)
    miasto(st, t, w, fasady=(("motel", 900), ("motel", 380)), tyl=(), chodnik=True)
    auto(st, t, 220, 210, p=P.wzgorza + 0.03)
    x, _ = jazda(t, 0.4, 5.0, 300, 820)
    lalka(st, t, "clyde", x, 320, flip=1, rece=(90, 80), kuleje=1.0, hop=4)
    lalka(st, t, "bonnie", x + 10, 260, flip=1, lean=-80, lift=150 + 6 * abs(math.sin(x / 26)), rece=(150, 20), p=P.lalki + 0.015)
    if int(x / 52) % 2 == 0:
        tab(w, t, "OW!", x, 260, 1.0, 0.6)
    koniec(st, w, t)


def s_oboz(st, w, t, T):
    """Wieczór przy drodze: auto, pranie na sznurku, puszka fasoli na ognisku, Bonnie pisze, Clyde czyści karabin."""
    w.noc = 0.7
    kam(st, t, 53, 640, 440, 1.05, 0.79)
    preria(st, t, w, slupy=False, noc=1.0)
    auto(st, t, 980, 220, p=P.wzgorza + 0.03, tint=(0.8, 0.8, 0.9))
    st.line([(200, 470), (480, 486), (760, 470)], P.wzgorza + 0.035, width=1.4, color=(80, 70, 60))
    for n, x in enumerate((280, 380, 560, 660)):
        st.put(J.rek("pranie"), x, 474 + 6 * math.sin(n), P.wzgorza + 0.036, h=60, anchor=(0.5, 0.0), rot=3 * math.sin(t * 2 + n), tint=((0.9, 0.85, 1.0), (1.0, 0.8, 0.8))[n % 2])
    for n in range(3):
        st.put(Z0.flame(int(t * 12 + 3 * n) % 10), 622 + 18 * n, 694, P.lalki + 0.02, h=90, anchor=(0.5, 1.0), shadow=None)
    st.put(J.rek("puszka"), 640, 640, P.lalki + 0.025, h=40, anchor=(0.5, 1.0))
    st.put(J.glow(), 640, 640, P.lalki + 0.03, w=600, anchor=(0.5, 0.5), mode="add", alpha=0.35, shadow=None)
    lalka(st, t, "bonnie", 420, 280, flip=1, lean=6, rece=(80 + 5 * math.sin(t * 8), 60), trzyma=(J.rek("zeszyt"), 40, (0.5, 0.5), 80, True), kuleje=0)
    out = lalka(st, t, "clyde", 860, 320, flip=-1, lean=8, sink=0.15, rece=(60 + 14 * math.sin(t * 5), 40))
    st.put(J.rek("karabin"), 860, 600, P.lalki + 0.02, w=250, anchor=(0.5, 0.5), rot=-4, sx=-1)  # karabin na kolanach, lufą w bok
    if out:
        st.put(J.rek("pranie"), out[0], out[1], P.lalki + 0.022, h=22, anchor=(0.5, 0.5), tint=(1.0, 1.0, 0.9))
    koniec(st, w, t)


def s_rzeka(st, w, t, T):
    """Bonnie myje włosy w rzece; ryba wyskakuje jej spod ręki; „BRRR!”."""
    kam(st, t, 54, 640, 470, 1.4, 0.8)
    las(st, t, w, rodzaj="liscie", droga=0.0, krzaki=False, kul=False)
    st.put(J.rzeka_pas(), 640, 790, P.lalki - 0.004, w=2200, anchor=(0.5, 1.0))
    lalka(st, t, "bonnie", 560, 290, flip=1, lean=40, sink=0.1, rece=(130, 120))
    f = pr(t, 0.6, 0.9)
    if 0 < f < 1:
        st.put(J.zwierze("ryba"), 680 + 140 * f, 680 - 160 * math.sin(math.pi * f), P.lalki + 0.035, h=26, anchor=(0.5, 0.5), rot=-60 + 160 * f)
    tab(w, t, "BRRR!", 600, 300, 0.4, 1.8)
    koniec(st, w, t)


def s_list_ford(st, w, t, T):
    """Na masce Forda leży list na papierze firmowym; zjeżdża podpis „Clyde?” i tabliczka ze znakiem zapytania."""
    kam(st, t, 55, 760, 440, 1.7, 0.8)
    st.dof = 1.4
    preria(st, t, w, slupy=False, kul=False)
    auto(st, t, 640, 300)
    st.put(J.rek("list"), 800, 512, P.auta + 0.004, h=80, anchor=(0.5, 1.0), rot=-70)
    podpis(w, t, "Clyde?", 800, 300, 1.4, 4.0)
    tab(w, t, "?", 920, 330, 3.0, 4.0)
    koniec(st, w, t)


def s_platte(st, w, t, T):
    """Teatr cieni: policja otacza dwa domki motelu, podjeżdża opancerzone auto; błyski, sylwetka Bucka chwieje się, szyba pęka przed Blanche."""
    kam(st, t, 56, 640, 450, 1.35, 0.79, lens=1.4, shake=3.0 * (4.2 < t < 4.6))
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    for n, x in enumerate((420, 820)):
        st.put(J.fasada("motel"), x, y0 - 26, p0 + 0.0005, h=230, anchor=(0.5, 1.0), tint=(0.08, 0.06, 0.05), alpha=0.85, shadow=None, blur=1.6)
    ax, _ = jazda(t, 0.4, 2.6, 1500, 1080)
    auto(st, t, ax, 180, y=y0 - 26, p=p0 + 0.0012, flip=-1, tint=(0.08, 0.06, 0.05), alpha=0.85, shadow=None, blur=1.6, szyby=False)
    chwiej = ease(pr(t, 4.5, 1.0))
    cien(st, t, "buck", 380, 260, y0 - 26, p0 + 0.002, flip=1, rece=(40, 0), lean=-25 * chwiej + 6 * math.sin(t * 6) * (t > 4.5))
    cien(st, t, "blanche", 470, 240, y0 - 26, p0 + 0.002, flip=-1, rece=(120 * ease(pr(t, 4.4, 0.3)), 90 * ease(pr(t, 4.4, 0.3))))
    for n in range(5):
        blysk(st, 900 + 30 * n, y0 - 140, p0 + 0.003, t, 4.0 + 0.18 * n, r=220)
    if t > 4.4:
        for n in range(6):
            f = pr(t, 4.4, 0.8)
            st.put(Z0.coin(), 470 + 80 * f * math.cos(n), y0 - 200 - 60 * f * math.sin(n * 2), p0 + 0.003, h=8, anchor=(0.5, 0.5), tint=(0.08, 0.06, 0.05),
                   alpha=0.8 * (1 - f), shadow=None)
    koniec(st, w, t, dim=0.9)


def s_dexfield(st, w, t, T):
    """Świt w lesie w Iowie: z krzaków wychodzą farmerzy i policjanci; Buck leży przy ognisku, Blanche klęczy przy nim i nie chce odejść."""
    kam(st, t, 57, 640, 450, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", droga=0.0, swit=1.0)
    for n in range(2):
        st.put(Z0.flame(int(t * 10 + 4 * n) % 10), 470 + 20 * n, 694, P.lalki + 0.02, h=80, anchor=(0.5, 1.0), shadow=None)
    lalka(st, t, "buck", 560, 300, flip=1, lean=86, lift=70, rece=(20, 0), p=P.lalki - 0.005)
    lalka(st, t, "blanche", 760, 290, flip=-1, lean=-20, sink=0.12, rece=(80, 60))
    for n, (key, x0) in enumerate((("farmer", 1000), ("policjant", 1120), ("farmer2", 1230), ("szeryf", 160))):
        k = ease(pr(t, 1.6 + 0.5 * n, 1.0))
        x = lerp(x0, x0 - 120 * (1 if x0 > 640 else -1), ease(pr(t, 3.0 + 0.4 * n, 2.0)))
        lalka(st, t, key, x, 300, k, flip=-1 if x0 > 640 else 1, rece=(70, 0), trzyma=KARABIN(150))
    koniec(st, w, t, extra=(1.06, 0.98, 0.92))


def s_przeprawa(st, w, t, T):
    """Clyde, Bonnie i W.D. brną przez rzekę; Clyde ciągnie Bonnie za rękę; na brzegu za nimi błyski."""
    kam(st, t, 58, 640, 480, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", droga=0.0, krzaki=True)
    x, _ = jazda(t, 0.0, T, 300, 900)
    for n, (key, dx, h) in enumerate((("clyde", 0, 320), ("bonnie", -120, 280), ("wd", -230, 280))):
        lalka(st, t, key, x + dx + 8 * math.sin(t * 3 + n), h, flip=1, sink=0.32, lean=-6, rece=(70 if n < 2 else 40, 50 if n == 1 else 20))
    st.put(J.rzeka_pas(), 640, 745, P.lalki + 0.03, w=2200, anchor=(0.5, 1.0))
    for n in range(3):
        blysk(st, 120 + 60 * n, 560, P.drzewa, t, 1.4 + 1.1 * n, r=200)
    koniec(st, w, t, extra=(1.04, 1.0, 0.94))


def s_wd_odchodzi(st, w, t, T):
    """Nocą W.D. wysiada po cichu i odchodzi w ciemność; Bonnie patrzy za nim przez szybę."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 59, 640, 450, 1.2, 0.79)
    preria(st, t, w, slupy=True, noc=1.0)
    auto(st, t, 520, 240, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.7, 0.72, 0.85))
    x, _ = jazda(t, 0.6, T - 1.0, 720, 1300)
    lalka(st, t, "wd", x, 270, 1.0, flip=1, rece=(10, 0), hop=4, alpha=1.0 - 0.8 * ease(pr(t, 3.0, 3.0)), tint=(0.7, 0.72, 0.85))
    koniec(st, w, t)


def s_rodziny(st, w, t, T):
    """Nocą przy polnej drodze stoją dwa auta z wygaszonymi światłami; matki podają przez okna koszyki, Bonnie oddaje pranie."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 60, 640, 440, 1.05, 0.79)
    preria(st, t, w, slupy=True, noc=1.0)
    auto(st, t, 420, 220, pasazerowie=[("bonnie", 0, (80, 0)), ("clyde", 1, (40, 0))], tint=(0.7, 0.72, 0.85))
    auto(st, t, 980, 210, kolor="czarny", flip=-1, p=P.auta + 0.005, tint=(0.7, 0.72, 0.85))
    for n, (key, x) in enumerate((("matka_bonnie", 650), ("matka_clyde", 770))):
        d = ease(pr(t, 1.0 + 0.6 * n, 1.0))
        out = lalka(st, t, key, x, 280, flip=-1, rece=(90 * d, 20), tint=(0.75, 0.75, 0.88))
        if out:
            st.put(J.rek("koszyk"), out[0], out[1], P.lalki + 0.03, h=36, anchor=(0.5, 0.2), tint=(0.8, 0.8, 0.9))
    if t > 4.0:
        f = ease(pr(t, 4.0, 1.4))
        st.put(J.rek("pranie"), lerp(500, 640, f), 520 + 30 * math.sin(math.pi * f), P.lalki + 0.03, h=40, anchor=(0.5, 0.5), tint=(0.8, 0.8, 0.9))
    koniec(st, w, t)


def s_sowers(st, w, t, T):
    """Nocą przy drodze z krzaków wyskakują policjanci; strzelają za wcześnie, Ford z przestrzelonymi szybami odjeżdża; „OUCH!”."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 61, 640, 440, 1.05, 0.79, shake=2.0 * (3.2 < t < 4.4))
    las(st, t, w, rodzaj="liscie", krzaki=True, noc=1.0)
    x, _ = jazda(t, 0.0, 3.2, -200, 600)
    x2, _ = jazda(t, 4.6, 3.2, 600, 1700)
    auto(st, t, x if t < 4.6 else x2, 230, dziury=12 if t > 3.4 else 0, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))],
         tint=(0.7, 0.72, 0.85))
    for n, (key, kx) in enumerate((("policjant", 560), ("policjant2", 980), ("szeryf", 1260))):
        k = ease(pr(t, 2.6 + 0.2 * n, 0.4))
        lalka(st, t, key, kx, 300, k, flip=-1 if kx > 640 else 1, rece=(90, 0), trzyma=KARABIN(150), tint=(0.75, 0.75, 0.88), p=P.drzewa - 0.01)
        for m in range(3):
            blysk(st, kx - 80, 520, P.drzewa, t, 3.2 + 0.3 * m + 0.1 * n, r=200)
    tab(w, t, "OUCH!", 640, 300, 4.0, 2.6)
    koniec(st, w, t)
