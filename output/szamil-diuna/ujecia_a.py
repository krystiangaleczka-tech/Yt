"""Ujęcia prologu i aktów I–II filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (szkic E, 28.11.2026):
funkcja `s_<klucz>(st, w, t, T)` na ujęcie.

st — scena (papier.Stage), w — stan świata z początku ujęcia (scena.stan), t — czas akcji od początku ujęcia, T — długość.
Przebudowa 28.11 (reżyser: „na każdym ujęciu praktycznie nic się nie dzieje”, „przebuduj to”): w każdym ujęciu z kwestią
2–4 wydarzenia, a każde stoi na słowie lektora — `sl("klucz", "słowo")` daje chwilę, w której lektor je mówi (tempo
rozpiski; po nagraniu render.czas_akcji przekłada ją na prawdziwe nagranie). Gag stoi po kwestii (`po_kw`), w pauzie.
Zapowiedź (zap_*) render składa ze skrótów ujęć (render.WYCINEK).
"""
import math
import re

import uklad_kz as K  # silnik uklad.py: rzędy, przyczepianie, ręka z łokciem, kontrola każdej klatki (Wytyczne 1.32)
from dane import HAK, kwestia, okno_tempa, slownie, ujecia
from scena import (CX, CY, I, J, P, STOPY, Z0, _off, arrakis_sc, back, bk, blysk, cien, clamp, ease, ease_out, gabinet,  # noqa: F401
                   gimry_sc, gwiazdy, iks, izba, jaskinia, jazda, kam, kaukaz, ksiezyc, kulisy, lalka, las_bukowy, lerp, miczik,
                   mur_przod, noise, parawan, petersburg, podpis, pr, rampa, gruzja, sala_balowa, settle, siegnij, snieg, swiatlo,
                   teatr_kz, zawieszki, pustynia, ciemnosc, slonce, kaluga_sc, wnetrze, gory_pasmo)
from scena import (SKALA_OBOZ, bateria_sc, brama_sc, dziedziniec_sc, gabinet_cara, klif, oboz_sc, ostaniec_sc,  # noqa: F401,E402
                   przelecz_sc, rzeka_wieczor, skala_jaskinia, skala_sc, skala_szczyt, wawoz_sc, wieza_sc, cykl_dni, niebo_dni)

ZOLNIERZE = ("zolnierz", "zolnierz2", "zolnierz3", "zolnierz4", "zolnierz5", "zolnierz6")  # sześć różnych żołnierzy (1.6)
MURIDZI = ("murid", "murid2", "murid3", "murid4", "murid5", "sado")

_UJ = {u[2]: u for u in ujecia()}


def _slowa(klucz):
    return [re.sub(r"[^a-z0-9']", "", s.lower()) for s in slownie(kwestia(_UJ[klucz][7])).split()]


def sl(klucz, slowo, n=1):
    """Chwila (sekundy od początku ujęcia), w której lektor zaczyna mówić `slowo` (n-te wystąpienie) — według tempa
    rozpiski (dane.TEMPO_EN). Wytyczne 1.11: to, o czym mówi lektor, dzieje się wtedy albo tuż po."""
    start, dl = okno_tempa(_UJ[klucz][7], klucz in HAK)
    ws = _slowa(klucz)
    cel = re.sub(r"[^a-z0-9']", "", slowo.lower())
    trafy = [i for i, s in enumerate(ws) if s.startswith(cel)]
    i = trafy[min(n, len(trafy)) - 1]
    return start + dl * i / len(ws)


def po_kw(klucz, d=0.2):
    """Chwila tuż po końcu kwestii (gag w pauzie, Humor)."""
    start, dl = okno_tempa(_UJ[klucz][7], klucz in HAK)
    return start + dl + d


def koniec(st, w, t, dim=1.0, extra=(1.0, 1.0, 1.0)):
    swiatlo(st, w, t, extra=extra, dim=dim)
    zawieszki(st, t, w)


def _bump(t, t0, d=0.15):
    return max(0.0, 1.0 - abs(t - t0) / d)


def SZABLA(dl=150, rot=-90):
    """Szabla w dłoni ostrzem w górę (rot −90) albo przed siebie (0); arkusz 520 × 90, rękojeść (0.1, 0.5)."""
    return (J.rek_kz("szabla"), dl * 90 / 520, (0.1, 0.5), rot, False)


def FLAGA(dl=200):
    """Biała flaga na drzewcu trzymanym pionowo (arkusz 300 × 420, drzewce (0.053, 0.6))."""
    return (J.rek_kz("flaga_biala"), dl, (0.053, 0.6), 0, False)


def jezdziec(st, t, key, x, y=STOPY, p=None, flip=1.0, h=170, k=1.0, seed=0, rece=(10.0, 0.0), trzyma=None, galop=1.0,
             pasazer=None, dziecko=None):
    """Jeździec na silniku uklad.py (uklad_kz.jezdziec: koń jest obiektem, biodro w siodle z kontrolą); trzyma — szabla
    (SZABLA()) w przedniej dłoni za rękojeść, z kontrolą „w dłoni”."""
    p = P.lalki if p is None else p
    u = K.uk(st, t)
    rz = f"p{p:.4f}"
    u.rzedy[rz] = p
    nazwa = f"{key} (jeździec {seed})"
    szk = K.jezdziec(st, t, nazwa, key, x, y, rz, flip, h, k, seed, galop, przod=rece[0], tyl=rece[1], pasazer=pasazer, dziecko=dziecko)
    if trzyma and szk:
        K.w_dloni(st, t, f"szabla ({nazwa})", "szabla", szk, trzyma[1], rot=trzyma[3])
    return szk


def dym(st, x, y, p, t, t0, r=160, dl=2.2, seed=0, tint=(0.62, 0.6, 0.58)):
    """Kłąb dymu z bibuły po wystrzale: rośnie, unosi się i rzednie."""
    if t < t0 or t > t0 + dl:
        return
    k = pr(t, t0, dl)
    st.put(J.S("cloud_left", 0.3), x + 30 * k + 8 * noise(t, seed, 0.5), y - 60 * k, p, w=r * (0.4 + 0.8 * ease_out(k)), anchor=(0.5, 0.5),
           alpha=0.85 * (1 - k), tint=tint, shadow=None)


def plomien(st, x, y, p, t, h=90, seed=0):
    st.put(Z0.flame(int(t * 12 + seed) % 10), x, y, p, h=h, anchor=(0.5, 1.0), shadow=None, tint=(1.0, 0.72, 0.38))


def slowo(st, t, txt, x, y, k, seed=0, h=84, p=None, rot0=0.0):
    """Słowo z Diuny na karcie na nitce (KANLY, SIETCH…) — zjeżdża (k 0..1) i kołysze się."""
    if k > 0:
        J.hang(st, J.slowo(txt), x, y, (P.rekwizyty if p is None else p), k, t, 1100 + seed, h=h, drop=420, rot0=rot0,
               shadow=(5, 8, 8, 0.4))


def koza(st, t, nazwa, x, y=STOPY, p=None, h=110, flip=1.0, meh=False, k=1.0, hop=0.0):
    """Koza (gag powracający): stoi na linii stóp; meh — otwarty pysk (beczy)."""
    if k <= 0:
        return
    u = K.uk(st, t)
    p = P.lalki + 0.02 if p is None else p
    yy = y + (1 - back(k, 1.2)) * h * 1.1 - abs(math.sin(x / 22.0)) * hop
    u.put(nazwa, J.rek_kz("koza_meh" if meh else "koza"), x, yy, p, "zwierze", h=h, anchor=(0.5, 1.0), sx=flip,
          rot=1.2 * noise(t, 77, 0.6))


def robak(st, t, x, y, p, wys, h=520, flip=1.0, rot=0.0):
    """Robak z Diuny wynurza się zza wydmy: wys 0..1 — jak wysoko wystaje (dół sprite'u chowa się za bliższą wydmą)."""
    if wys <= 0:
        return None
    yy = y + (1 - wys) * h * 0.95
    st.put(J.rek_kz("robak"), x, yy, p, h=h, anchor=(0.5, 1.0), sx=flip, rot=rot + 3 * math.sin(t * 2.1), shadow=(6, 8, 10, 0.35))
    return x + (196 / 380 - 0.5) * h * 380 / 960 * flip, yy - h + 110 / 960 * h  # środek paszczy


def maszynista(st, t, k, y=420, cel_x=None):
    """Laska z hakiem maszynisty wysuwa się zza lewych kulis (k 0..1); koniec haka idzie do cel_x."""
    if k <= 0:
        return None
    dl = 620
    x0 = -dl - 40 + (cel_x + 40 if cel_x is not None else 520) * ease(k)
    st.put(J.rek_kz("laska_hak"), x0, y, P.rekwizyty + 0.03, w=dl, anchor=(0.0, 0.5), rot=2 * math.sin(t * 3), shadow=(6, 8, 10, 0.4))
    return x0 + dl * 0.97, y + 20


def kartki_kalendarza(st, t, t0, lata, x=640, y=150, dl=0.42, p=None):
    """Kartki kalendarza lecą jedna po drugiej (lata) — każda zjeżdża, staje na chwilę i odlatuje łukiem w bok."""
    p = P.rekwizyty if p is None else p
    for n, rok in enumerate(lata):
        a = t0 + n * dl
        if t < a:
            continue
        f = pr(t, a + dl * 0.6, 0.7)
        st.put(J.kalendarz_rok(rok), x + 520 * f * (1 if n % 2 else -1), y + 90 * pr(t, a, 0.15) - 260 * math.sin(math.pi * f * 0.5) + 400 * f ** 2,
               p + 0.001 * n, h=170, anchor=(0.5, 0.0), rot=(30 if n % 2 else -30) * f, shadow=(5, 7, 8, 0.4), alpha=1 - pr(t, a + dl + 0.5, 0.3))


def pieczatka(st, t, t0, raport_txt, x=640, y=520, p=None, stary=False, gag=True, h_rap=230, spada=None, podloga=STOPY):
    """Gag pieczątki (wątek „pieczatka”): raport leży na blacie, w t0 pieczątka spada z góry, odbija stempel, podskakuje
    i zostaje na raporcie (przegląd 28.11: wisiała w powietrzu). gag=False — trzecie podejście bez żartu: pieczątka opada
    powoli i zostaje. spada — chwila, w której pieczątkę zrzuca kamień (leci łukiem na podłogę)."""
    p = P.lalki + 0.03 if p is None else p
    st.put(J.raport(raport_txt if t >= t0 + (0.18 if gag else 0.9) else None, stary), x, y, p, h=h_rap, anchor=(0.5, 0.5),
           rot=-3, shadow=(4, 6, 8, 0.35))
    lezy = y + h_rap * 0.1
    if gag:
        k = pr(t, t0 - 0.25, 0.25)
        py = lerp(-200, lezy, k ** 2) - 90 * math.sin(math.pi * pr(t, t0 + 0.05, 0.45))
    else:
        py = lerp(lezy - 240, lezy, ease(pr(t, t0, 0.9)))
    px, rot = x + 10, 0.0
    if spada is not None and t > spada:
        f = pr(t, spada, 0.6)
        px, py, rot = px + 140 * f, lerp(lezy, podloga, f ** 2) - 60 * math.sin(math.pi * f), 120 * f
    if t > t0 - 0.3:
        st.put(J.rek_kz("pieczatka"), px, py, p + 0.002, h=h_rap * 0.6, anchor=(0.5, 1.0), rot=rot, shadow=(6, 8, 10, 0.4))


# ================================================================ prolog: Diuna, zwrot, Szamil, hak, pytanie

def s_tytul(st, w, t, T):
    """Kurtyna startu rozsuwa się na pustynię (render.KURTYNA_START): wydmy, dwa słońca, na grzbiecie wydmy fremen; szyld
    z tytułem zjeżdża; piasek na grzbiecie drga — coś jest pod spodem (zasiew robaka)."""
    kam(st, t, I["tytul"], 640, 380, lerp(1.0, 1.06, ease(t / T)), 0.8)
    arrakis_sc(st, t, w)
    K.lalka(st, t, "fremen", "fremen", 990, 230, y=STOPY - 70, flip=-1, przod=6)
    J.hang(st, J.tag("The Imam Who Fought Russia for 25 Years", 36), CX, 74, P.rekwizyty + 0.02, pr(t, 0.5, 1.0), t, 31, h=66, drop=360,
           sway=0.7, strings=(0.15, 0.85), shadow=(5, 8, 8, 0.4))
    if t > 2.6:  # piasek podskakuje na grzbiecie środkowej wydmy
        for n in range(6):
            f = (t * 2.2 + n * 0.17) % 1.0
            st.put(Z0.prop("kulka"), 380 + n * 26, 500 - 30 * math.sin(math.pi * f), P.gory + 0.002, h=8, anchor=(0.5, 0.5),
                   tint=(0.95, 0.8, 0.55), shadow=None)
    koniec(st, w, t)


def s_arrakis(st, w, t, T):
    """Diuna, którą widz zna: robak wynurza się zza wydmy; na „kindjal” fremen wyciąga kindżał (KINDJAL); na „houses” po bokach
    zjeżdżają dwie chorągwie rodów, między nimi KANLY (w Diunie kanly to wendeta wielkich rodów — sprawdzenie faktów 28.11);
    na „sietches” w skale otwiera się jaskinia (SIETCH); gag po kwestii: robak połyka kartę KANLY i beka chmurką piasku.
    Wszystko na słowach lektora (sl)."""
    kam(st, t, I["arrakis"], lerp(560, 720, ease(t / T)), 390, 1.08, 0.8)
    arrakis_sc(st, t, w, skala=True, skala_x=1080)
    u = K.uk(st, t)
    wys = ease(pr(t, 0.5, 0.9)) * (1 - ease(pr(t, 2.0, 0.8)))  # robak: wynurza się z lewej zaraz na początku i chowa się
    robak(st, t, 260, 640, P.gory - 0.003, wys, h=420)
    t_kindjal, t_houses, t_sietch = sl("arrakis", "kindjal"), sl("arrakis", "houses"), sl("arrakis", "sietches")
    f1 = K.lalka(st, t, "fremen 1", "fremen", 460, 300, flip=1, przod=lambda s: 8 + 112 * ease(pr(t, t_kindjal - 0.3, 0.4)))
    K.lalka(st, t, "fremen 2", "fremen2", 720, 300, flip=-1, przod=lambda s: 10 + 20 * ease(pr(t, t_kindjal, 0.4)))
    if f1:
        K.w_dloni(st, t, "kindżał fremena", "kindzal", f1, 70, rot=180 * ease(pr(t, t_kindjal - 0.3, 0.4)))  # ostrzem w górę
    slowo(st, t, "KINDJAL", 360, 210, pr(t, t_kindjal, 0.7), seed=3, h=62)
    # dwie chorągwie wielkich rodów (własne barwy, bez herbów z filmów — księga D5) i KANLY między nimi
    for n, (x, kolor) in enumerate(((520, (0.5, 1.4, 0.7)), (800, (0.6, 0.8, 1.6)))):
        k = pr(t, t_houses - 0.2 + 0.25 * n, 0.8)
        if k > 0:
            J.hang(st, J.rek_kz("choragiew"), x, 120, P.rekwizyty - 0.006, k, t, 1180 + n, h=190, drop=420, sx=1 if n == 0 else -1,
                   tint=kolor, strings=(0.1,), shadow=(5, 8, 8, 0.35))
    gag = po_kw("arrakis", 0.1)
    polyka = pr(t, gag + 0.7, 0.6)
    wys2 = ease(pr(t, gag, 0.7)) * (1 - ease(pr(t, gag + 1.3, 0.6)))
    usta = robak(st, t, 660, 700, P.wzgorza - 0.003, wys2, h=540, flip=-1)
    if polyka < 1:
        ky = 250 if not usta or polyka <= 0 else lerp(250, usta[1] + 30, ease(polyka))
        slowo(st, t, "KANLY", 660, ky, pr(t, t_houses + 0.4, 0.8), seed=2, h=74, rot0=-40 * polyka,
              p=(P.wzgorza - 0.0035) if polyka > 0 else None)  # połykana karta chowa się za robakiem
    jaskinia(st, 1080, 700, P.wzgorza + 0.003, h=90 * ease(pr(t, t_sietch - 0.2, 0.4)))
    slowo(st, t, "SIETCH", 1080, 330, pr(t, t_sietch, 0.8), seed=1, h=70)
    dym(st, 660, 560, P.wzgorza, t, gag + 1.5, r=260, dl=1.6, seed=5, tint=(0.95, 0.82, 0.6))
    if t > 1.5:  # po wejściu lalki (wejście kończy się ok. 1,4 s); wcześniej fremen dopiero wjeżdża na scenę (kontrola 28.11)
        u.widac("fremen 1", 0.9, "fremen 1: widać ≥ 90%")
    koniec(st, w, t)


def s_zamiana(st, w, t, T):
    """Zwrot: wydmy zapadają się pod scenę, wyrastają ośnieżone góry Kaukazu, pada śnieg, za granią auł; fremen, który został
    na scenie, trzęsie się z zimna („BRRR!”), a laska maszynisty z hakiem ściąga go za kołnierz za kulisy (teatr świadomy siebie)."""
    kam(st, t, I["zamiana"], 640, lerp(380, 400, ease(t / T)), lerp(1.0, 1.08, ease(t / T)), 0.75)
    t_made, t_cauc = sl("zamiana", "weren't"), sl("zamiana", "caucasus")
    zapada = ease(pr(t, t_made, 1.4))
    if zapada < 1:
        arrakis_sc(st, t, w, wydmy=1 - zapada, kul=False)
        for n in range(10):  # piasek sypie się z zapadających wydm
            f = (t * 1.6 + n * 0.1) % 1.0
            if 0.02 < zapada < 0.98:
                st.put(Z0.prop("kulka"), 140 + n * 110, 520 + f * 220, P.wzgorza + 0.002, h=9, anchor=(0.5, 0.5), tint=(0.95, 0.8, 0.55),
                       shadow=None)
    gory = ease(pr(t, t_made + 1.0, 1.4))
    if gory > 0:
        if zapada >= 1:
            st.put(J.niebo_sp(False), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None, tint=(0.9, 0.94, 1.0))
            chmury(st, t, w)
            rampa(st)
        for which, y, p, d, seed in (("dal", 560, P.gory_dal, 0.0, 2), ("srodek", 640, P.gory, 0.2, 1), ("blisko", 760, P.wzgorza - 0.01, 0.4, 3)):
            kk = ease(pr(t, t_made + 1.0 + d, 1.2))
            Z0.rise(st, J.gory(which, seed), CX, y, p, kk, t, 1200 + seed, w=2000, wob=0.0, lift=480, anchor=(0.5, 1.0), sy=GORY_SY[which])
        aul = ease(pr(t, t_cauc + 0.6, 0.9))
        Z0.rise(st, J.aul(0), 1000, 650, P.miasto, aul, t, 1205, w=640, wob=0.0, lift=400, anchor=(0.5, 1.0))
    snieg(st, t, pr(t, t_cauc - 0.3, 1.5), seed=4)
    # fremen marznie; po kwestii hak maszynisty ściąga go w lewo
    gag = po_kw("zamiana", 0.0)
    zjazd = ease(pr(t, gag + 0.9, 0.7))
    drzy = 4 * math.sin(t * 40) * pr(t, t_cauc, 0.5)
    fx = lerp(560, -160, zjazd) + drzy
    K.lalka(st, t, "fremen", "fremen", fx, 300, flip=-1, przod=150 if t > gag else 20, tyl=140 if t > gag else 10, lift=40 * zjazd,
            lean=-12 * zjazd)
    maszynista(st, t, pr(t, gag + 0.3, 0.6) * (1 - 0 * zjazd), y=420, cel_x=fx - 60)
    if zjazd < 0.3:
        podpis(w, t, "BRRR!", 560, 300, t_cauc + 0.6, 3.2)
    koniec(st, w, t, extra=(lerp(1.0, 0.94, gory), lerp(1.0, 0.98, gory), lerp(1.0, 1.06, gory)))


from scena import GORY_SY, chmury  # noqa: E402


def s_przedstawienie(st, w, t, T):
    """Kamera najeżdża na lalkę na grani; Szamil odwraca się do widza; przy imieniu podpis „Imam Shamil”; za nim po kolei
    wysuwają się muridzi; na „most wanted” spada tabliczka „WANTED BY THE TSAR”, a Szamil spokojnie odsuwa ją pochwą kindżału
    (gag: jego nigdy nie ma tam, gdzie celują)."""
    kam(st, t, I["przedstawienie"], lerp(700, 880, ease(pr(t, 0, 2.5))), lerp(400, 430, ease(pr(t, 0, 2.5))),
        lerp(1.05, 1.5, ease(pr(t, 0, 2.6))), 0.8)
    kaukaz(st, t, w, uklad=1, aul=300)
    snieg(st, t, 0.5, seed=4)
    t_imie, t_wanted = sl("przedstawienie", "shamil"), sl("przedstawienie", "wanted")
    u = K.uk(st, t)
    u.rzedy["muridzi"] = P.lalki - 0.015
    for n in range(4):
        K.lalka(st, t, f"murid {n + 1}", MURIDZI[n], 700 + n * 90 - (n % 2) * 30, 270, y=STOPY - 6, rzad="muridzi", flip=-1,
                k=ease(pr(t, t_imie + 0.8 + 0.35 * n, 0.5)), przod=lambda s, n=n: 10 + 150 * ease(pr(t, t_wanted - 1.2 + 0.1 * n, 0.4)))
    obrot = ease(pr(t, 0.4, 0.45))
    odsuwa = ease(pr(t, t_wanted + 1.0, 0.5)) * (1 - ease(pr(t, t_wanted + 2.6, 0.5)))
    K.lalka(st, t, "Szamil", w.szamil, 980, 330, flip=lerp(-1, 1, obrot), przod=4 + 120 * odsuwa)
    podpis(w, t, "Imam Shamil", 980, 250, t_imie, 3.0)
    spad = pr(t, t_wanted, 0.35)
    if spad > 0:  # tabliczka spada nad głowę, Szamil odsuwa ją w bok, odjeżdża krzywo
        x = 940 + 140 * ease(pr(t, t_wanted + 1.2, 0.6))  # odsunięta w stronę ręki Szamila, cała w kadrze
        J.hang(st, J.tag("WANTED BY THE TSAR", 40), x, 230, P.rekwizyty + 0.02, spad, t, 1210, h=62, drop=300,
               rot0=-14 * ease(pr(t, t_wanted + 1.2, 0.6)), strings=(0.2, 0.8), shadow=(5, 8, 8, 0.4))
    koniec(st, w, t)


RZEKA_LEWY, RZEKA_PRAWY = 300, 1000


def s_hak_syn(st, w, t, T):
    """Hak: rzeka w górach. Szamil oddaje małego syna (chłopiec idzie sam na lewy brzeg i chowa się za szeregiem Rosjan);
    kartki kalendarza przelatują nad rzeką („Sixteen years later”); młody mężczyzna w rosyjskim mundurze wjeżdża w bród
    i staje na środku. Bez imienia i bez podpisu (Wytyczne 1.26)."""
    kam(st, t, I["hak_syn"], lerp(760, 640, ease(t / T)), 420, lerp(1.08, 1.18, ease(t / T)), 0.75)
    rzeka_wieczor(st, t, w)
    u = K.uk(st, t)
    t_host, t_six, t_rode = sl("hak_syn", "hostage"), sl("hak_syn", "sixteen"), sl("hak_syn", "rode")
    u.rzedy["szereg"] = P.lalki - 0.01
    for n in range(3):  # czwarty przy x 80 stał cały czas poza kadrem (kontrola układu 28.11)
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], 170 + n * 85, 250, rzad="szereg", flip=1)
    for n in range(3):
        K.lalka(st, t, f"murid {n + 1}", MURIDZI[n + 1], 1260 - n * 80, 250, rzad="szereg", flip=-1)
    idzie = ease(pr(t, 0.6, t_host + 0.8 - 0.6))
    if t < t_six:
        K.lalka(st, t, "chłopiec", "dzamal_maly", lerp(980, 380, idzie), 160, flip=-1, hop=5 * (0 < idzie < 1),
                k=1 - pr(t, t_host + 1.0, 0.5), glebia=0.6)
        K.lalka(st, t, "Szamil", w.szamil, 1060, 300, flip=-1, przod=lambda s: 30 + 40 * (1 - idzie))
    else:
        K.lalka(st, t, "Szamil", w.szamil, 1060, 300, flip=-1, przod=6)
    kartki_kalendarza(st, t, t_six - 0.2, (1839, 1843, 1847, 1851, 1855), x=640, y=60, dl=0.32)
    jedzie = pr(t, t_rode - 0.4, 2.6)
    if jedzie > 0:
        x = lerp(220, 640, ease_out(jedzie))
        jezdziec(st, t, "dzamal_oficer", x, y=STOPY + 10, p=P.lalki + 0.01, flip=1, h=230, galop=1 - ease(pr(t, t_rode + 2.0, 0.6)), seed=3)
        for n in range(3):  # woda pryska spod kopyt
            if 0 < jedzie < 1:
                f = (t * 3 + n * 0.33) % 1.0
                st.put(Z0.prop("kulka"), x - 30 + n * 30, STOPY - 10 - 40 * math.sin(math.pi * f), P.lalki + 0.02, h=8, anchor=(0.5, 0.5),
                       tint=(0.7, 0.85, 1.0), shadow=None)
    koniec(st, w, t)


def s_pytanie(st, w, t, T):
    """Jedno pytanie prowadzi dalej w historię (otwarcie w akcji, 28.11: Gimry 1832 już było): rzeka zamiera, połowa gór zapada
    się w piasek, na chwilę wyrasta wydma i znika; na „Follow” kartki kalendarza lecą wstecz do 1834, ostatnia trafia
    maszynistę za kulisami („OUCH!”), a Szamil schodzi w lewo za kulisy; na „jump” zawieszka „Dagestan, 1834”; ściemnienie."""
    kam(st, t, I["pytanie"], 640, 390, lerp(1.1, 1.0, ease(t / T)), 0.75)
    t_des, t_starts, t_jump = sl("pytanie", "desert"), sl("pytanie", "follow"), sl("pytanie", "jump")
    wydma = ease(pr(t, t_des - 0.2, 0.8)) * (1 - ease(pr(t, t_des + 1.6, 0.8)))
    rzeka_wieczor(st, t, w)
    # na „Follow the man” Szamil schodzi w lewo za kulisy — widz idzie za nim (wcześniej znikał i scena stała pusta ~2 s, 28.11)
    idzie = ease(pr(t, t_starts + 0.2, max(1.0, t_jump - t_starts)))
    K.lalka(st, t, "Szamil", w.szamil, lerp(1060, -170, idzie), 300, flip=-1, przod=6, hop=6 * (0 < idzie < 1))
    jezdziec(st, t, "dzamal_oficer", 640, y=STOPY + 10, p=P.lalki + 0.01, flip=1, h=230, galop=0.0, seed=3,
             k=1 - pr(t, t_starts + 0.6, 0.6))
    Z0.rise(st, J.wydma(0), 360, 700, P.gory + 0.01, wydma, t, 1220, w=900, wob=0.0, lift=460, anchor=(0.5, 1.0))
    lata = (1855, 1850, 1845, 1839, 1834)
    kartki_kalendarza(st, t, t_starts - 0.1, lata, x=640, y=60, dl=0.36)
    trafia = t_starts - 0.1 + 4 * 0.36 + 0.36 * 0.6 + 0.7
    if t > trafia - 0.3:  # ostatnia kartka trafia w laskę maszynisty, która wysuwa się zza kulis
        maszynista(st, t, pr(t, trafia - 0.6, 0.4) * (1 - pr(t, trafia + 1.0, 0.4)), y=260, cel_x=60)
        podpis(w, t, "OUCH!", 150, 120, trafia, 1.4)
    podpis(w, t, "Dagestan, 1834", CX, 40, t_jump, T)
    koniec(st, w, t)


# ================================================================ prolog: otwarcie w akcji — Gimry, wieża, skok

WIEZA_X = 430


def s_gimry(st, w, t, T):
    """Wioska w wąwozie; na płaskim dachu staje Ghazi Muhammad (podpis), obok młody Szamil (podpis); za granią wysuwają się
    po kolei białe czapki żołnierzy; Szamil wskazuje je ręką, Ghazi odwraca głowę."""
    kam(st, t, I["gimry"], lerp(620, 700, ease(t / T)), 400, lerp(1.0, 1.15, ease(t / T)), 0.75)
    gimry_sc(st, t, w, wieza_x=WIEZA_X, aul_x=860)
    u = K.uk(st, t)
    t_ghazi, t_shamil = sl("gimry", "ghazi"), sl("gimry", "shamil")
    t_zol = sl("gimry", "friend")
    u.rzedy["dach"] = P.miasto + 0.012
    gh = K.lalka(st, t, "Ghazi Muhammad", "ghazi", 820, 230, y=520, rzad="dach", flip=lerp(1, -1, ease(pr(t, t_zol + 1.2, 0.4))),
                 k=ease(pr(t, t_ghazi - 0.3, 0.5)), przod=lambda s: 20 + 120 * _bump(t, t_ghazi + 0.8, 0.8))
    K.lalka(st, t, "Szamil", w.szamil, 920, 230, y=520, rzad="dach", flip=-1, k=ease(pr(t, t_shamil - 0.4, 0.5)),
            przod=lambda s: 10 + 90 * ease(pr(t, t_zol + 0.8, 0.4)))
    podpis(w, t, "Ghazi Muhammad, the first imam", 820, 340, t_ghazi, 2.8)
    podpis(w, t, "Shamil", 920, 340, t_shamil, 2.6)
    podpis(w, t, "Gimry, Dagestan, 1832", CX, 40, 0.6, T)  # otwarcie w akcji (28.11): miejsce i czas od pierwszej chwili
    u.rzedy["gran"] = P.gory + 0.006
    for n in range(7):  # białe czapki za granią z lewej, po kolei
        k = ease(pr(t, t_zol + 0.25 * n, 0.4))
        if k > 0:
            K.lalka(st, t, f"żołnierz za granią {n + 1}", ZOLNIERZE[n % 6], 90 + n * 48, 110, y=560 + (n % 2) * 6, rzad="gran", flip=1,
                    k=k, wejscie=False)
    koniec(st, w, t)


def s_wieza(st, w, t, T):
    """Wieża: Ghazi i Szamil w otworze okna (widać ich tylko przez okno), szereg żołnierzy dookoła; błyski i dymki z obu
    stron; na „killed” Ghazi znika z okna, a jego papacha spada z okna i zostaje na ziemi (ślad śmierci, bez gagu, 1.11);
    pod drzwiami żołnierze stają w szereg z bagnetami w górę."""
    kam(st, t, I["wieza"], 560, 380, 1.2, 0.75)
    wieza_sc(st, t, w, WIEZA_X, mrok=0.0)
    u = K.uk(st, t)
    t_trap, t_kill, t_door = sl("wieza", "trapped"), sl("wieza", "killed"), sl("wieza", "door")
    # okno wieży: otwór (108..192, 148..244) arkusza 300 × 900 przy h 560 → piksele kadru
    sx = 560 / 900
    ox0, oy0 = WIEZA_X + (108 - 150) * sx, 712 - 560 + 148 * sx
    ox1, oy1 = WIEZA_X + (192 - 150) * sx, 712 - 560 + 244 * sx
    u.rzedy["w_wiezy"] = P.most - 0.004
    zniknal = pr(t, t_kill, 0.4)
    if zniknal < 1:
        K.lalka(st, t, "Ghazi w oknie", "ghazi", (ox0 + ox1) / 2 - 8, 150, y=oy1 + 70, rzad="w_wiezy", flip=1, sink=zniknal, wejscie=False)
    spad = pr(t, t_kill + 0.1, 0.6)
    if spad > 0:  # papacha spada łukiem z okna i zostaje na ziemi
        px = lerp((ox0 + ox1) / 2, (ox0 + ox1) / 2 + 70, spad)
        py = lerp(oy0 + 20, STOPY - 10, spad ** 2)
        st.put(J.figura("ghazi").kapelusz[0], px, py, P.lalki + 0.03, h=40, anchor=(0.5, 0.5), rot=200 * spad if spad < 1 else 170)
    for n in range(5):  # szereg żołnierzy dookoła wieży (szósty stał poza kadrem — kontrola 28.11); strzelają, dymki
        x = 640 + n * 100
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], x, 230, glebia=(n % 2) * 2, flip=-1)
        s_ = 0.9 + 0.35 * n
        if s_ < t_kill:
            blysk(st, x - 50, STOPY - 160, P.lalki + 0.02, t, s_, r=160)
            dym(st, x - 60, STOPY - 170, P.lalki + 0.02, t, s_, r=110, seed=n)
    for n, s_ in enumerate((1.4, 2.6)):
        blysk(st, (ox0 + ox1) / 2, (oy0 + oy1) / 2, P.most, t, s_, r=140)
        dym(st, (ox0 + ox1) / 2 + 10, oy0, P.most + 0.002, t, s_, r=90, seed=10 + n)
    # pod drzwiami (próg u dołu wieży) szereg z bagnetami w górę na „door”
    u.rzedy["pod_drzwiami"] = P.lalki + 0.01
    for n in range(3):
        k = ease(pr(t, t_door - 0.6 + 0.2 * n, 0.4))
        K.zolnierz(st, t, f"bagnet {n + 1}", ZOLNIERZE[(n + 3) % 6], WIEZA_X + 70 + n * 70, 250, rzad="pod_drzwiami", flip=-1, k=k)
    koniec(st, w, t)


def s_skok(st, w, t, T):
    """Legenda: Szamil na progu wieży nad szeregiem bagnetów unosi szablę; na „jumped” skacze łukiem nad głowami żołnierzy,
    ląduje za ich plecami; żołnierze obracają się jeden po drugim w złą stronę („?!”), Szamil biegnie w wąwóz trzymając się
    za bok; ostatni żołnierz wciąż celuje w puste drzwi (gag po kwestii)."""
    t_jump = sl("skok", "jumped")
    t_land = t_jump + 1.2
    kam(st, t, I["skok"], lerp(480, 640, ease(pr(t, t_jump, 1.4))), 400, 1.25, 0.78, shake=6 * _bump(t, t_land, 0.15))
    wieza_sc(st, t, w, WIEZA_X, mrok=0.8)
    u = K.uk(st, t)
    prog = (WIEZA_X, 712 - 560 * (1 - 820 / 900) - 8)  # podwyższony próg drzwi wieży
    f = pr(t, t_jump, 1.2)
    if f <= 0:
        x, y, lean = prog[0], prog[1], 0.0
    else:
        x = lerp(prog[0], 820, ease(f) if f < 1 else 1.0)
        y = lerp(prog[1], STOPY, f) - 260 * math.sin(math.pi * min(f, 1.0))
        lean = 30 * math.sin(math.pi * min(f, 1.0))
    if t > t_land + 2.0:  # ucieka w prawo, w wąwóz, ręka przy boku
        x = lerp(820, 1420, ease(pr(t, t_land + 2.0, 1.6)))
    u.rzedy["skok"] = P.lalki + 0.03
    sz = K.lalka(st, t, "Szamil", w.szamil, x, 300, y=y, rzad="skok", flip=1, lean=lean, hop=6 * (t > t_land + 2.0),
                 przod=lambda s: 150 if t < t_land + 0.6 else (s["punkt"](140, 300) if t > t_land + 2.0 else 60))
    if sz and t < t_land + 2.0:
        K.w_dloni(st, t, "szabla Szamila", "szabla", sz, 30, rot=-90 if t < t_land else -20)
    for n in range(4):
        obrot = ease(pr(t, t_land + 0.5 + 0.35 * n, 0.3)) if n < 3 else 0.0  # ostatni się nie odwraca (gag)
        zx = 520 + n * 70
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], zx, 250, flip=lerp(-1, 1, obrot), glebia=(n % 2))
        if n < 3:
            podpis(w, t, "?!", zx, 300 - 30 * (n % 2), t_land + 0.6 + 0.35 * n, 1.6)
    podpis(w, t, "...", 730, 300, po_kw("skok", 0.4), 1.6)
    koniec(st, w, t)


def s_rana(st, w, t, T):
    """Wąwóz o zmierzchu: Szamil biegnie, zatacza się, ręka przy piersi; żołnierze strzelają w pusty wąwóz; Szamil chowa się
    w szałasie pasterza; z ciemności wychodzi koza, liże go po brodzie, Szamil kładzie palec na ustach („SHH!”) — zasiew kozy."""
    kam(st, t, I["rana"], lerp(520, 760, ease(t / T)), 410, 1.12, 0.78)
    wawoz_sc(st, t, w)
    u = K.uk(st, t)
    t_chest, t_hid = sl("rana", "chest"), sl("rana", "hid")
    u.put("szałas", J.rek_kz("szalas"), 960, STOPY + 4, u.p("lalki", -3), h=300, anchor=(0.5, 1.0))
    x = lerp(160, 930, ease(pr(t, 0.3, t_hid + 0.4)))
    zatacza = 6 * math.sin(t * 5) * (t < t_hid + 0.4)
    siada = ease(pr(t, t_hid + 0.6, 0.6))
    sz = K.lalka(st, t, "Szamil", w.szamil, x, 300, flip=1, lean=zatacza + 6, hop=5 * (t < t_hid + 0.4), lift=-40 * siada,
                 przod=lambda s: s["punkt"](150, 250), tyl=lambda s: (s["punkt"](178, 162) if t > po_kw("rana", 0.5) else 10))
    for n in range(2):  # żołnierze z lewej strzelają w pusty wąwóz (trzeci stał poza kadrem, a drugi przy x −30 też — kontrola 28.11)
        s_ = t_chest - 0.4 + 0.4 * n
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n + 2], 100 - n * 80, 240, flip=1, glebia=n)
        blysk(st, 160, STOPY - 150, P.lalki + 0.02, t, s_, r=150)
        dym(st, 180 + 40 * n, STOPY - 160, P.lalki + 0.02, t, s_, r=110, seed=n)
    gag = po_kw("rana", -0.6)
    kz = ease(pr(t, gag - 0.4, 0.6))
    koza(st, t, "koza", lerp(1100, 1010, kz), h=110, flip=-1, k=kz)
    podpis(w, t, "SHH!", 900, 260, gag + 0.6, 2.0)
    koniec(st, w, t, extra=(0.96, 0.9, 0.94))


def s_kanly_1834(st, w, t, T):
    """Teatr cieni: za podświetlonym parawanem sylwetka meczetu (szara, dalej); dwie czarne sylwetki z kindżałami podchodzą
    do trzeciej (drugi imam), trzecia opada za parawan — bez gagu; na „kanly” nad parawanem zjeżdża duże słowo KANLY.
    Przegląd 28.11: sylwetki zlewały się z czarnym meczetem, a parawan był mały w kadrze."""
    y0, p0, ph = parawan(st, t, w)
    kam(st, t, I["kanly_1834"], 640, y0 - ph * 0.5 - 20, 1.45, p0)
    st.put(J.rek_kz("meczet_cien"), 820, y0 - 30, p0 + 0.002, h=240, anchor=(0.5, 1.0), blur=3.0, shadow=None, tint=(0.42, 0.36, 0.3),
           alpha=0.75)
    t_kill, t_kanly = sl("kanly_1834", "killed"), sl("kanly_1834", "kanly")
    pad = pr(t, t_kill + 0.2, 0.8)
    if pad < 1:
        cien(st, t, "ghazi", 700, 230, y0 - 30, p0 + 0.004, flip=-1, sink=pad, lean=-25 * pad)
    for n in range(2):
        x = lerp(300 + n * 90, 560 + n * 60, ease(pr(t, 0.8 + 0.2 * n, t_kill - 0.8)))
        cien(st, t, ("murid2", "murid5")[n], x, 230, y0 - 30, p0 + 0.005, flip=1, rece=(30 + 80 * _bump(t, t_kill, 0.4), 0))
    podpis(w, t, "1834", 360, 200, 0.3, T)
    slowo(st, t, "KANLY", 640, 260, pr(t, t_kanly, 0.9), seed=4, h=84)
    koniec(st, w, t)


def s_imam(st, w, t, T):
    """Plac w aule: Szamil (zdrowy) wchodzi na kamień; muridzi wysuwają się po kolei zza rampy, każdy z własnym opóźnieniem;
    na „imam” unoszą szable falą; nad nimi „TO THE DEATH!”; gag: ostatni murid unosi szablę spóźniony i odwrotnie,
    sprawdza i poprawia."""
    kam(st, t, I["imam"], lerp(700, 620, ease(t / T)), 420, lerp(1.0, 1.12, ease(t / T)), 0.78)
    dziedziniec_sc(st, t, w)
    u = K.uk(st, t)
    t_imam, t_death = sl("imam", "imam"), sl("imam", "death")
    u.put("kamień", Z0.prop("kamien"), 660, STOPY + 6, u.p("lalki", -2), h=90, anchor=(0.5, 1.0))
    wchodzi = ease(pr(t, 0.6, 0.8))
    K.lalka(st, t, "Szamil", w.szamil, lerp(540, 660, wchodzi), 320, lift=70 * wchodzi, flip=1,
            przod=lambda s: 10 + 140 * ease(pr(t, t_imam, 0.4)), rzad="lalki", glebia=-1)
    u.rzedy["muridzi"] = P.lalki + 0.01
    xs = (180, 300, 420, 880, 1000, 1120)
    for n, x in enumerate(xs):
        k = ease(pr(t, 1.2 + 0.25 * n, 0.5))
        fala = ease(pr(t, t_imam + 0.15 * n, 0.35))
        if n == 5:  # gag: spóźniony, szabla odwrotnie, potem poprawia
            g = po_kw("imam", 0.2)
            fala = ease(pr(t, g, 0.4))
            odwr = 1 - ease(pr(t, g + 1.0, 0.3))
        szk = K.lalka(st, t, f"murid {n + 1}", MURIDZI[n], x, 290, rzad="muridzi", flip=1 if x < 640 else -1, k=k,
                      przod=lambda s, fala=fala: 10 + 150 * fala)
        if szk:
            rot = -90 if n < 5 else lerp(-90, 90, odwr if fala > 0.5 else 0)
            K.w_dloni(st, t, f"szabla murida {n + 1}", "szabla", szk, 28, rot=rot)
    if t > po_kw("imam", 0.6):
        podpis(w, t, "?", 1120, 260, po_kw("imam", 0.6), 1.0)
    J.hang(st, J.tag("TO THE DEATH!", 46), CX, 130, P.rekwizyty + 0.02, pr(t, t_death, 0.8), t, 1230, h=70, drop=360,
           strings=(0.2, 0.8), shadow=(5, 8, 8, 0.4))
    koniec(st, w, t)


def s_mapa(st, w, t, T):
    """Gabinet w Petersburgu: car Mikołaj I przy stole z mapą Kaukazu (podpis); generał wsuwa kijem rzędy cynowych żołnierzyków
    w doliny; na „valley” papierowa góra na mapie wstaje z łoskotem i żołnierzyki zjeżdżają z niej jak z sanek; generał
    łapie ostatniego, car marszczy brwi (silnik humoru: mapy imperium kontra góry)."""
    kam(st, t, I["mapa"], 640, 420, 1.15, 0.8)
    gabinet_cara(st, t, w, okno_x=1080, orzel_x=330)
    u = K.uk(st, t)
    t_tsar, t_valley = sl("mapa", "tsar"), sl("mapa", "valley")
    u.mebel("stół", "stol_palac", 640, 190, rzad="przod")
    _, blat = u.powierzchnia("stół", "blat", 0.5)
    mapa_w = 520
    st.put(J.mapa_kaukazu(), 640, blat - 2, u.p("przod", 0.5), w=mapa_w, anchor=(0.5, 1.0), sy=0.32, shadow=(3, 4, 6, 0.3))
    K.lalka(st, t, "car Mikołaj I", "nikolaj", 900, 330, flip=-1, rzad="lalki", przod=lambda s: 20 + 40 * _bump(t, po_kw("mapa", 0.5), 0.6))
    podpis(w, t, "Tsar Nicholas I", 900, 230, t_tsar, 2.8)
    gen = K.lalka(st, t, "generał", "general", 380, 320, flip=1, przod=lambda s: 60 + 20 * math.sin(t * 2) * (t < t_valley))
    if gen:
        K.w_dloni(st, t, "kij generała", "szabla", gen, 30, rot=-10)
    gora = ease(pr(t, t_valley, 0.35))
    gx = 700
    st.put(J.rek_kz("gora_mapy"), gx, blat - 12, u.p("przod", 0.6), h=110, anchor=(0.5, 1.0), sy=lerp(0.15, 1.0, gora),
           shadow=(4, 6, 8, 0.3))
    for n in range(6):  # żołnierzyki: jadą po mapie w prawo, z góry zjeżdżają w lewo i spadają ze stołu
        x = lerp(470 + n * 22, gx - 30 + n * 6, ease(pr(t, 1.0 + 0.1 * n, t_valley - 1.0)))
        zj = pr(t, t_valley + 0.1 + 0.08 * n, 0.6)
        x -= 260 * zj
        y = blat - 6 - 40 * gora * (1 - zj) + 300 * max(0.0, zj - 0.6) ** 2 * (n < 5)
        if n == 5:  # ostatniego łapie generał (zostaje przy krawędzi stołu)
            x = max(x, 470)
        st.put(J.rek_kz("zolnierzyk"), x, y, u.p("przod", 0.7), h=34, anchor=(0.5, 1.0), rot=-25 * zj)
    if gora > 0:
        podpis(w, t, "!", 900, 230, po_kw("mapa", 0.3), 1.6)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def s_marsz(st, w, t, T):
    """Dolina: kolumna piechoty, armata na wozie (koń i woźnica), chorągiew; na „struck” zza skał wyskakują muridzi, dymki,
    chowają się; na „vanished” pusto; gag: murid wysuwa się za plecami ostatniego żołnierza i stuka go w ramię, żołnierz się
    odwraca — pusto. Kurtyna w pauzie (render: „Act 2 · What would you give to buy time?”)."""
    kam(st, t, I["marsz"], lerp(560, 740, ease(t / T)), 410, 1.05, 0.75)
    przelecz_sc(st, t, w)
    u = K.uk(st, t)
    t_struck, t_van = sl("marsz", "struck"), sl("marsz", "vanished")
    for n in range(6):
        x = lerp(-200 + n * 150, 300 + n * 150, ease(pr(t, 0.0, T * 0.9)))
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], x, 240, glebia=(n % 2), flip=1, hop=5)
    xa = lerp(-560, -60, ease(pr(t, 0.0, T * 0.9)))
    if K.wjechal():
        u.put("armata", J.rek_kz("armata"), xa, STOPY - 2, u.p("lalki", -1), h=110, anchor=(0.5, 1.0))
        K.zaprzeg(st, t, "armata", xa + 110, STOPY - 2, u.p("lalki", -1), 1, h_kon=120, woznica=None)
    for n, (x, s_) in enumerate(((760, t_struck), (980, t_struck + 0.4), (1180, t_struck + 0.8))):
        k = ease(pr(t, s_ - 0.3, 0.3)) * (1 - ease(pr(t, s_ + 1.0, 0.3)))
        if k > 0:
            K.lalka(st, t, f"murid zza skał {n + 1}", MURIDZI[n], x, 220, y=STOPY - 50, rzad="lalki", glebia=-4, flip=-1, k=k, wejscie=False,
                    przod=90)
            blysk(st, x - 60, STOPY - 160, P.lalki, t, s_ + 0.1, r=150)
            dym(st, x - 70, STOPY - 170, P.lalki + 0.01, t, s_ + 0.1, r=110, seed=n)
    gag = po_kw("marsz", 0.0)
    ostatni_x = lerp(-200, 300, ease(pr(t, 0.0, T * 0.9)))
    mk = ease(pr(t, gag, 0.4)) * (1 - ease(pr(t, gag + 1.1, 0.3)))
    if mk > 0:
        K.lalka(st, t, "murid z gagu", "murid4", ostatni_x - 80, 250, rzad="lalki", glebia=2, flip=1, k=mk, wejscie=False,
                przod=lambda s: K.w_zasiegu(s, (ostatni_x - 20, STOPY - 190)))  # przy wejściu i zejściu ręka nie sięga (28.11)
    if t > gag + 1.2:
        podpis(w, t, "?!", ostatni_x, 330, gag + 1.2, 1.6)
    koniec(st, w, t)


# ================================================================ akt II: Achulgo, zakładnik, tratwa, raport, syn

def s_akhulgo(st, w, t, T):
    """Na skale wyrasta twierdza, zawieszka „Akhulgo, 1839”; u stóp wyrastają namioty; koń wciąga armatę na pozycję;
    na „eighty days” dni mijają na nitkach (reżyser 28.11: „słońce przesuwa się na lince w lewo za kadr, z prawej na lince
    jedzie księżyc, już ciemniając scenerię… znowu wyjeżdża słońce z prawej i rozjaśnia, i tak w kółko”) — scena.cykl_dni;
    wcześniej dekoracja rysowała własny księżyc i słońce, a ujęcie drugi księżyc, który przelatywał przez słońce."""
    kam(st, t, I["akhulgo"], 660, lerp(400, 360, ease(t / T)), lerp(1.0, 1.15, ease(t / T)), 0.62)
    ciala, noc = cykl_dni(t, sl("akhulgo", "eighty"), 2.6, cykle=2)
    kaukaz(st, t, w, twierdza=True, rzeka_=False, namioty=6, blisko=False, cialo=False)
    niebo_dni(st, t, w, ciala, noc)
    u = K.uk(st, t)
    xa = lerp(-160, 300, ease(pr(t, 2.6, 2.4)))
    if K.wjechal():
        u.put("armata", J.rek_kz("armata"), xa, STOPY + 4, u.p("lalki"), h=150, anchor=(0.5, 1.0))
        K.zaprzeg(st, t, "armata", xa + 150, STOPY + 4, u.p("lalki"), 1, h_kon=170, woznica=None, galop=0.6 * (t < 5.0))
    K.lalka(st, t, "artylerzysta", "zolnierz5", xa + 330, 250, flip=-1, hop=4 * (t < 5.0),
            przod=lambda s: K.w_zasiegu(s, (xa + 300, STOPY - 160)))
    podpis(w, t, "Akhulgo, 1839", 380, 40, 0.5, T)
    koniec(st, w, t, dim=1.0 - 0.45 * noc)


def s_armaty(st, w, t, T):
    """Armaty dają ognia po kolei (dym, kamienie od murów, wstrząs); na „attack” drabina przy skale, żołnierze się wspinają;
    gag: obrońca odpycha drabinę, która z wolna przechyla się do tyłu z żołnierzem uczepionym na górze („WHOA!”) i znika za
    skałą — bez upadku na oczach."""
    strzaly = (0.6, 1.1, 1.6, 2.3)
    kam(st, t, I["armaty"], 600, 380, 1.1, 0.7, shake=sum(6 * _bump(t, s_, 0.12) for s_ in strzaly))
    bateria_sc(st, t, w)
    klif(st, t, w, 6, 1230, 790, P.wzgorza, h=900, d=0.3)
    u = K.uk(st, t)
    for n, s_ in enumerate(strzaly[:3]):
        x = 140 + n * 150
        st.put(J.rek_kz("armata"), x, STOPY - 8, P.lalki + 0.01 * n, h=140, anchor=(0.5, 1.0), rot=-3 * _bump(t, s_, 0.2))
        blysk(st, x + 85, STOPY - 85, P.lalki + 0.02, t, s_, r=220)
        dym(st, x + 105, STOPY - 95, P.lalki + 0.02, t, s_, seed=n)
        kk = pr(t, s_ + 0.25, 0.6)
        if 0 < kk < 1:
            for m in range(3):
                st.put(Z0.prop("kamien"), 860 + m * 30 + 60 * kk, 250 + 120 * kk ** 2 - 40 * kk, P.most + 0.01, h=16, anchor=(0.5, 0.5),
                       rot=200 * kk, shadow=None)
    t_att = sl("armaty", "attack")
    gag = po_kw("armaty", 0.0)
    przechyl = ease(pr(t, gag + 0.3, 1.4))
    dx, dy = 1010, STOPY
    rot = 14 - 70 * przechyl
    dr = ease(pr(t, t_att - 0.5, 0.5))
    u.put("drabina", J.rek_kz("drabina"), dx, dy, P.lalki - 0.01, h=400 * dr if dr > 0 else 1, anchor=(0.5, 1.0), rot=rot)
    for n in range(2):
        wsp = ease(pr(t, t_att + 0.2 * n, 1.6))
        L = 120 + 200 * wsp - 90 * n
        ax = dx + math.sin(math.radians(rot)) * L
        ay = dy - math.cos(math.radians(rot)) * L
        if dr >= 1:
            K.lalka(st, t, f"żołnierz na drabinie {n + 1}", ZOLNIERZE[n + 1], ax - 6, 150, y=ay + 90, flip=1, glebia=0.5, wejscie=False,
                    lean=rot * 0.6, przod=150, tyl=130, alpha=1 - pr(t, gag + 1.4, 0.3))
    if przechyl > 0:
        podpis(w, t, "WHOA!", 960, 140, gag + 0.6, 1.8)
    koniec(st, w, t)


def s_amanat(st, w, t, T):
    """Brama twierdzy: nad murem unosi się biała flaga rozmów; Szamil wychodzi z małym chłopcem, dłoń na jego ramieniu; przy
    imieniu podpis „Jamal al-Din, Shamil's son”; dłoń Szamila zostaje jeszcze chwilę i powoli puszcza — bez gagu."""
    kam(st, t, I["amanat"], 640, 430, lerp(1.15, 1.3, ease(t / T)), 0.8)
    brama_sc(st, t, w)
    u = K.uk(st, t)
    t_host, t_name = sl("amanat", "hostage"), sl("amanat", "jamal")
    flaga = ease(pr(t, 0.6, 0.9))
    st.put(J.rek_kz("flaga_biala"), 1010, STOPY - 60 + (1 - flaga) * 300, P.lalki - 0.01, h=300, anchor=(0.04, 1.0), rot=2 * math.sin(t * 5))
    wych = ease(pr(t, sl("amanat", "unthinkable") - 0.4, 1.2))
    sx = lerp(700, 430, wych)  # z bramy (środek muru) w lewo
    syn = K.lalka(st, t, "chłopiec", "dzamal_maly", sx + 50, 190, flip=-1, glebia=0.5, hop=4 * (0 < wych < 1))
    kladzie = ease(pr(t, t_host - 0.4, 0.6)) * (1 - ease(pr(t, po_kw("amanat", -0.2), 1.2)))
    start = lambda s: K.U.Uklad.dlon_z_kata(s, 8)
    cel = (lambda s: (lerp(start(s)[0], syn["punkt"](120, 214)[0], kladzie), lerp(start(s)[1], syn["punkt"](120, 214)[1], kladzie))) if syn else 5
    sz = K.lalka(st, t, "Szamil", w.szamil, sx, 300, flip=-1 if wych < 1 else 1, hop=4 * (0 < wych < 1), przod=cel)
    if sz and syn and kladzie >= 0.999:
        u.dotyka("chłopiec", (*sz["przod"]["dlon"], sz["p"]), "dłoń Szamila na ramieniu chłopca", 6.0)
    podpis(w, t, "Jamal al-Din, Shamil's son", 500, 250, t_name, 3.0)
    koniec(st, w, t)


def s_chlopiec(st, w, t, T):
    """Chłopiec idzie sam ścieżką w dół, przed szeregiem bagnetów, do obozu; kamera jedzie za nim; w połowie drogi ogląda się
    za siebie — na górze Szamil zaciska dłoń na rękojeści kindżału; chłopiec znika między namiotami. Przegląd 28.11: chłopiec
    był mały i ginął między żołnierzami."""
    x = lerp(1060, 220, ease_out(pr(t, 0.0, T * 0.85)))
    kam(st, t, I["chlopiec"], lerp(900, 420, ease(pr(t, 0.0, T * 0.85))), 470, 1.35, 0.8)
    oboz_sc(st, t, w)
    u = K.uk(st, t)
    u.rzedy["gora"] = P.gory + 0.01
    zaciska = ease(pr(t, T * 0.45, 0.5))
    K.lalka(st, t, "Szamil na górze", w.szamil, 1180, 150, y=500, rzad="gora", flip=-1,
            przod=lambda s: (lerp(s["bark_przod"][0], s["punkt"](156, 336)[0], zaciska), lerp(s["bark_przod"][1] + sum(s["L"]), s["punkt"](156, 336)[1], zaciska)))
    u.rzedy["szereg"] = P.lalki - 0.015
    for n in range(7):
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n % 6], 160 + n * 140, 270, y=STOPY - 4, rzad="szereg", flip=-1 if n < 4 else 1)
    oglada = _bump(t, T * 0.45, 0.5) > 0
    u.rzedy["chlopiec"] = P.lalki + 0.025
    ch = K.lalka(st, t, "chłopiec", "dzamal_maly", x, 190, rzad="chlopiec", flip=1 if oglada else -1, hop=4 * (not oglada),
                 k=1 - pr(t, T - 1.0, 0.6))
    # oficer prowadzi chłopca za rękę (fakty 28.11: zakładnika odprowadzono, nie szedł sam)
    K.lalka(st, t, "oficer", "oficer_ros2", x - 90, 300, rzad="chlopiec", glebia=-0.3, flip=-1, hop=4 * (not oglada),
            k=1 - pr(t, T - 1.0, 0.6), przod=(lambda s: K.w_zasiegu(s, ch["przod"]["dlon"] if ch else (x - 40, STOPY - 100)))
            if not oglada else 10)
    koniec(st, w, t, dim=0.96)


def s_upadek(st, w, t, T):
    """Skała Achulgo z bliska (dekoracje 2, reżyser 28.11: „pokazujemy je w inny sposób”): u góry płonie mur twierdzy, dym;
    na „fell” na murze staje rosyjska chorągiew; na „searched” żołnierze z latarniami podchodzą po kolei do trzech jaskiń
    w skale i zaglądają do środka — bez gagu."""
    kam(st, t, I["upadek"], 640, lerp(370, 410, ease(t / T)), lerp(1.0, 1.08, ease(t / T)), 0.65)
    skala_sc(st, t, w)
    t_fell, t_search = sl("upadek", "fell"), sl("upadek", "searched")
    top = skala_szczyt()
    for n in range(9):  # płonący mur na krawędzi skały
        plomien(st, 260 + n * 95, top + 10 + (n % 2) * 6, P.most + 0.004, t, h=60 + 60 * pr(t, t_fell - 0.6, T) + 10 * (n % 2), seed=n * 3)
        dym(st, 270 + n * 90, top - 70, P.most + 0.006, t, (t * 0.7 + n * 0.37) % 2.0 + int(t / 2.0) * 2.0 - 2.0, r=150, dl=2.0, seed=n)
    k = ease(pr(t, t_fell + 0.4, 0.8))
    if k > 0:
        st.put(J.rek_kz("flaga_biala"), 700, top - 90 + (1 - k) * 120, P.most - 0.001, h=150, anchor=(0.04, 1.0), tint=(0.95, 0.4, 0.4))
    u = K.uk(st, t)
    u.rzedy["jaskinie"] = P.most + 0.008
    for n in range(3):
        jx, jy, jw = skala_jaskinia(n)
        podloga_j = jy + 80
        kk = ease(pr(t, t_search + 0.5 * n, 0.6))
        if kk > 0:
            zaglada = ease(pr(t, t_search + 0.5 * n + 0.8, 0.6))
            szk = K.lalka(st, t, f"żołnierz z latarnią {n + 1}", ZOLNIERZE[n], jx - 70 - 40 * (1 - kk), 160, y=podloga_j, rzad="jaskinie",
                          flip=1, k=kk, wejscie=False, przod=lambda s_, jx=jx, jy=jy: K.w_zasiegu(s_, (jx - 20, jy + 10)), lean=14 * zaglada)
            if szk:
                hx, hy = szk["przod"]["dlon"]
                st.put(J.glow(), hx, hy, szk["p"] + 0.001, w=120, anchor=(0.5, 0.5), mode="add", alpha=0.55, shadow=None, tint=(1.0, 0.8, 0.4))
    koniec(st, w, t, dim=0.94)


def s_tratwa(st, w, t, T):
    """Noc: po rzece płynie tratwa ze słomianymi kukłami; żołnierze z latarniami biegną brzegiem za nią („THERE!”), strzelają;
    w tle w przeciwną stronę po skale przemyka cień Szamila z rodziną; gag po kwestii: kukle odpada głowa i spada do wody,
    żołnierz z latarnią zastyga („…”)."""
    w.noc = 1.0
    kam(st, t, I["tratwa"], lerp(560, 760, t / T), 430, 1.2, 0.75)
    kaukaz(st, t, w, twierdza=True, rzeka_=True, blisko=True, dal=False)
    for n in range(4):
        if bk(w, 0.6) >= 1:
            plomien(st, 560 + n * 50, 312 + (n % 2) * 8, P.most + 0.004, t, h=40, seed=n * 3)
    u = K.uk(st, t)
    gag = po_kw("tratwa", 0.1)
    tx = lerp(300, 980, min(t, gag) / gag) if gag > 0 else 300
    st.put(J.rek_kz("tratwa"), tx, 690 + 4 * math.sin(t * 3), P.drzewa + 0.004, h=110, anchor=(0.5, 1.0), rot=2 * math.sin(t * 2.3))
    glowa = pr(t, gag + 0.3, 0.7)
    if glowa > 0:  # głowa kukły (kulka słomy w papasze) spada do wody
        st.put(Z0.prop("kulka"), tx + 60 + 30 * glowa, 610 + 90 * glowa ** 2, P.drzewa + 0.006, h=26, anchor=(0.5, 0.5),
               tint=(0.85, 0.72, 0.45), shadow=None, alpha=1 - pr(t, gag + 1.0, 0.2))
    zastyga = t > gag + 0.9
    for n in range(3):
        x = lerp(80 - n * 90, tx - 140 - n * 90, ease(pr(t, 0.2 + 0.1 * n, gag - 0.4))) if not zastyga else tx - 140 - n * 90
        szk = K.lalka(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], x, 200, y=STOPY + 6, glebia=n, flip=1, hop=8 * (not zastyga), przod=80)
        if szk:
            hx, hy = szk["przod"]["dlon"]
            st.put(J.rek_kz("swieca"), hx, hy, szk["p"] + 0.0005, h=40, anchor=(0.5, 0.88), z=0.08)
            st.put(J.glow(), hx, hy - 30, szk["p"] + 0.001, w=170, anchor=(0.5, 0.5), mode="add", alpha=0.5, shadow=None, tint=(1.0, 0.8, 0.4))
            plomien(st, hx, hy - 33, szk["p"] + 0.0006, t, h=14, seed=n)
        if n == 0 and t < gag:
            blysk(st, x + 60, STOPY - 160, P.lalki + 0.02, t, sl("tratwa", "chased") + 0.3, r=150)
    for n in range(3):
        cien(st, t, ("szamil", "murid", "dzamal_maly")[n], lerp(1100, 700, pr(t, sl("tratwa", "climbed") - 1.5, 4.0)) - n * 40, 60 - 20 * (n == 2),
             590, P.wzgorza - 0.01, flip=-1, hop=3, seed=n)
    podpis(w, t, "THERE!", 300, 150, sl("tratwa", "raft"), 1.8)
    podpis(w, t, "...", tx - 140, 300, gag + 1.0, 1.6)
    koniec(st, w, t)


def s_raport(st, w, t, T):
    """Gabinet w Petersburgu: urzędnik kładzie raport, wielka pieczątka uderza „SHAMIL: FINISHED” (zasiew gagu pieczątki),
    urzędnik zadowolony; za oknem kartka kalendarza 1840; przez okno wpada kamień z kartką „CHECHNYA RISES”, pieczątka spada
    z biurka („OOPS”)."""
    kam(st, t, I["raport"], 640, 430, 1.25, 0.8)
    gabinet_cara(st, t, w, okno_x=1000, portret_x=250)
    u = K.uk(st, t)
    u.mebel("biurko", "biurko_palac", 560, 170, rzad="przod")
    _, blat = u.powierzchnia("biurko", "blat", 0.5)
    t_stamp, t_year, t_rose = sl("raport", "stamped"), sl("raport", "year"), sl("raport", "rose")
    kladzie = ease(pr(t, 0.4, 0.6))
    urz = K.lalka(st, t, "urzędnik", "urzednik", 760, 300, flip=-1,
                  przod=lambda s: K.w_zasiegu(s, (lerp(s["bark_przod"][0] - 20, 600, kladzie), lerp(s["bark_przod"][1] + 120, blat - 20, kladzie)), f=1.0) if t < t_stamp
                  else 30 + 120 * _bump(t, t_stamp + 0.6, 0.6))
    pieczatka(st, t, t_stamp, "SHAMIL: FINISHED", x=560, y=blat - 30, p=u.p("przod", 0.6), h_rap=120, spada=t_rose + 0.5)
    if t > t_year:
        st.put(J.kalendarz_rok(1840), 1000, 160 + 30 * ease(pr(t, t_year, 0.4)), P.miasto + 0.011, h=110, anchor=(0.5, 0.0), shadow=(4, 6, 6, 0.3),
               alpha=ease(pr(t, t_year, 0.4)))
    leci = pr(t, t_rose, 0.5)
    if leci > 0:  # kamień z kartką wpada przez okno łukiem i ląduje na biurku
        kx = lerp(1000, 600, leci)
        ky = lerp(240, blat - 30, leci) - 120 * math.sin(math.pi * leci)
        st.put(J.rek_kz("kamien_kartka"), kx, ky, u.p("przod", 0.8), h=46, anchor=(0.5, 0.5), rot=-300 * leci if leci < 1 else 0)
        if leci >= 1:
            J.hang(st, J.tag("CHECHNYA RISES", 40), 600, 230, P.rekwizyty, pr(t, t_rose + 0.6, 0.6), t, 1240, h=62, drop=300,
                   strings=(0.2, 0.8), shadow=(5, 8, 8, 0.4))
        blysk(st, 1000, 260, P.miasto + 0.02, t, t_rose, r=200, kolor=(0.9, 0.95, 1.0))
    if t > t_rose + 0.5:
        podpis(w, t, "OOPS", 760, 200, t_rose + 0.6, 1.8)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def s_syn_na_polnoc(st, w, t, T):
    """Kryta kibitka (koń i woźnica) jedzie śnieżną drogą na północ, w okienku twarz chłopca (widać go tylko przez okno, 1.1);
    pada śnieg; na „Petersburg” wyrastają złote iglice; kibitka mija szlaban z budką, wartownik salutuje."""
    kam(st, t, I["syn_na_polnoc"], 640, 400, 1.05, 0.8)
    t_pet = sl("syn_na_polnoc", "petersburg")
    _niebo = J.niebo_sp(False)
    st.put(_niebo, CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None, tint=(0.82, 0.86, 0.94))
    chmury(st, t, w)
    Z0.rise(st, J.iglice(), CX, 640, P.miasto, ease(pr(t, t_pet, 1.2)), t, 870, w=1500, wob=0.0, lift=460, anchor=(0.5, 1.0))
    Z0.rise(st, J.grunt((236, 236, 240)), CX, 800, P.droga, 1.0, t, 1250, w=2000, anchor=(0.5, 1.0), lift=200, wob=0)  # śnieżna droga
    rampa(st)
    u = K.uk(st, t)
    u.put("szlaban", J.rek_kz("szlaban"), 980, STOPY - 4, u.p("lalki", -2), h=200, anchor=(0.5, 1.0))
    K.lalka(st, t, "wartownik", "zolnierz3", 900, 250, rzad="lalki", glebia=-1.5, flip=-1,
            przod=lambda s: (s["punkt"](186, 96) if t > T * 0.62 else 6))
    x = lerp(-200, 820, ease_out(pr(t, 0, T * 0.9)))
    hk = 200
    rot = 1.2 * math.sin(t * 7)
    if not K.wjechal():  # kibitka wjeżdża po budowie dekoracji (kontrola układu 28.11: woźnica bez kibitki)
        snieg(st, t, 1.0, seed=6)
        podpis(w, t, "St Petersburg", 980, 40, t_pet, T)
        koniec(st, w, t, extra=(0.94, 0.97, 1.04))
        return
    u.put("kibitka", J.rek_kz("kibitka_okno"), x, STOPY, P.lalki, h=hk, anchor=(0.5, 1.0), rot=rot)
    K.zaprzeg(st, t, "kibitka", K.pkt("kibitka_okno", 580, 238, x, STOPY, hk)[0], STOPY, P.lalki, 1,
              siedzisko=(K.pkt("kibitka_okno", 560, 232, x, STOPY, hk), "kibitka"), galop=0.6)
    ox0, oy0 = K.pkt("kibitka_okno", 262, 112, x, STOPY, hk)
    ox1, oy1 = K.pkt("kibitka_okno", 358, 178, x, STOPY, hk)
    u.rzedy["w_kibitce"] = P.lalki - 0.004
    K.lalka(st, t, "chłopiec w kibitce", "dzamal_maly", x + 4, 120, y=K.y_siedzi("dzamal_maly", 120, oy1 + 4), rzad="w_kibitce",
            flip=-1, siedzi=True, wejscie=False)
    u.w_otworze("chłopiec w kibitce", (ox0 - 3, oy0 - 3, ox1 + 3, oy1 + 3, P.lalki), "chłopca widać tylko przez okno kibitki")
    snieg(st, t, 1.0, seed=6)
    podpis(w, t, "St Petersburg", 980, 40, t_pet, T)
    koniec(st, w, t, extra=(0.94, 0.97, 1.04))


KRESKI_T0, KRESKA_DL = 1.4, 0.3  # pierwsza kreska na kamieniu i czas jednej kreski (kindżał ryje od góry w dół)


def s_kreski(st, w, t, T):
    """Szamil sam na grani, wiatr szarpie frędzlem turbanu; czubkiem kindżału ryje kreski na kamieniu (lata) — narzędzie liczy się
    od końca, który pracuje (1.28); potem podnosi wzrok na północ. Kurtyna zasuwa się w pauzie (render: „Act 3 · Can you win
    by burning your own capital?”)."""
    kam(st, t, I["kreski"], 700, 420, lerp(1.1, 1.35, ease(t / T)), 0.8)
    ostaniec_sc(st, t, w)
    snieg(st, t, 0.4, seed=8, wiatr=1.0)
    u = K.uk(st, t)
    u.put("kamień", J.rek_kz("kamien_kreski"), 820, STOPY, P.lalki + 0.02, h=150, anchor=(0.5, 1.0))
    n = int(clamp((t - KRESKI_T0) / KRESKA_DL, 0, 15))
    pozycja = lambda k: (796 + (k % 8) * 8, 588 + (k // 8) * 32)
    for k in range(n):
        x0, y0 = pozycja(k)
        with u.obiekt("kamień"):
            st.line([(x0, y0), (x0 + 2, y0 + 24)], P.lalki + 0.025, width=2.4, color=(60, 50, 44), alpha=0.9)
    ryje = KRESKI_T0 <= t < KRESKI_T0 + 15 * KRESKA_DL
    k_ = min(n, 14)
    f = pr(t, KRESKI_T0 + k_ * KRESKA_DL, KRESKA_DL) if ryje else 1.0
    x0, y0 = pozycja(k_)
    czubek = (x0 + 2 * f, y0 + 24 * f) if ryje else (x0 + 10, y0 - 20)
    hk, rot = 90, -40
    kk = hk / 420
    ox, oy = _off(0, (414 - 70) * kk, rot)
    dlon_ = (czubek[0] - ox, czubek[1] - oy)
    patrzy = ease(pr(t, sl("kreski", "back") - 0.6, 0.6))
    szk = K.lalka(st, t, "Szamil", w.szamil, 768, 300, flip=lerp(1, -1, patrzy),
                  przod=(lambda s: K.w_zasiegu(s, dlon_, f=1.0)) if patrzy < 0.5 else 8)
    if patrzy < 0.5:
        geo = K.w_dloni(st, t, "kindżał", "kindzal", szk, hk, rot=rot)
        if geo and ryje:
            u.dotyka("kamień", (*geo(40, 414), P.lalki + 0.02), "czubek kindżału na kamieniu", 5.0)
    koniec(st, w, t)
