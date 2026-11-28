"""Ujęcia aktów 0–2 filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune”: funkcja `s_<klucz>(st, w, t, T)`.

st — scena (papier.Stage), w — stan świata z początku ujęcia (scena.stan), t — czas od początku ujęcia, T — długość ujęcia.
Rozpiska: docs/filmy/szamil-diuna/ujecia/dane.py (zatwierdzony szkic D, reżyser 28.11.2026: „Zatwierdzam”). Zapowiedź (zap_*)
render składa sam ze skrótów tych ujęć (render.WYCINEK). Kwestia lektora zaczyna się ok. 0,6 s (w haku 0,4 s) — to, o czym
mówi, dzieje się wtedy albo tuż po (Wytyczne 1.11, 1.19).
"""
import math

import uklad_kz as K  # silnik uklad.py: rzędy, przyczepianie, ręka z łokciem, kontrola każdej klatki (Wytyczne 1.32)
from scena import (CX, CY, I, J, P, STOPY, Z0, _off, back, bk, blysk, cien, clamp, ease, ease_out, gwiazdy, iks, izba, jazda,  # noqa: F401
                   kam, kaukaz, ksiezyc, kulisy, lalka, lerp, miczik, mur_przod, noise, petersburg, podpis, pr, rampa, gruzja,
                   sala_balowa, settle, siegnij, swiatlo, teatr_kz, zawieszki, pustynia, ciemnosc, slonce)


ZOLNIERZE = ("zolnierz", "zolnierz2", "zolnierz3", "zolnierz4", "zolnierz5", "zolnierz6")  # sześć różnych żołnierzy (1.6), w wojsku po kolei


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


def KARABIN_PION(dl=150):
    """Karabin z bagnetem pionowo przy boku, lufą w górę (własny arkusz 520 × 90 — karabin z „Bonnie and Clyde” z przyrządami
    celowniczymi wyglądał z daleka jak czerwony krzyż, a tego w filmie o Szamilu nie wolno pokazać; przegląd 28.11)."""
    return (J.rek_kz("karabin"), dl * 90 / 520, (0.3, 0.55), -90, False)


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


def dym(st, x, y, p, t, t0, r=160, dl=2.2, seed=0):
    """Kłąb dymu z bibuły po wystrzale: rośnie, unosi się i rzednie."""
    if t < t0 or t > t0 + dl:
        return
    k = pr(t, t0, dl)
    st.put(J.S("cloud_left", 0.3), x + 30 * k + 8 * noise(t, seed, 0.5), y - 60 * k, p, w=r * (0.4 + 0.8 * ease_out(k)), anchor=(0.5, 0.5),
           alpha=0.85 * (1 - k), tint=(0.62, 0.6, 0.58), shadow=None)


def plomien(st, x, y, p, t, h=90, seed=0):
    st.put(Z0.flame(int(t * 12 + seed) % 10), x, y, p, h=h, anchor=(0.5, 1.0), shadow=None, tint=(1.0, 0.72, 0.38))


# ---------------------------------------------------------------- prolog: kurtyna, wprowadzenie, dwa zdania, pytanie

KARTA_DIUNA = ("Killing with the tip|lacks artistry.", "Dune, 1965")  # brzmienie do sprawdzenia w wydaniu (księga D7)
KARTA_1960 = ("To kill with the point|lacked artistry.", "1960")
KARTA_W = 640  # szerokość kart w kadrze (arkusz 960 × 300)
KARTA_Y = (96, 340)  # górne krawędzie: karta z Diuny, karta z 1960


def karta_diuny(st, t, y, k=1.0, seed=11, x=CX):
    J.hang(st, J.karta(*KARTA_DIUNA), x, y, P.rekwizyty, k, t, seed, w=KARTA_W, drop=520, sway=0.8, strings=(0.2, 0.8),
           shadow=(6, 9, 10, 0.35))


def karta_1960(st, t, y, k=1.0, seed=12, x=CX):
    J.hang(st, J.karta(*KARTA_1960, True), x, y, P.rekwizyty + 0.004, k, t, seed, w=KARTA_W, drop=560, sway=0.8,
           strings=(0.2, 0.8), shadow=(6, 9, 10, 0.35))


def kindzal_w_desce(st, t, t0=-10.0, x=1040):
    """Kindżał wbity w deskę sceny obok kart (spada ostrzem w dół w t0, drży po uderzeniu)."""
    k = pr(t, t0, 0.32)
    y = lerp(-260, STOPY - 40, k ** 2)
    drga = 6 * math.sin((t - t0) * 40) * math.exp(-(t - t0 - 0.32) * 5) if t > t0 + 0.32 else 0.0
    st.put(J.rek_kz("kindzal"), x, y, P.rekwizyty + 0.01, h=200, anchor=(0.5, 0.86), rot=drga, shadow=(5, 7, 8, 0.4))


def s_tytul(st, w, t, T):
    """Kurtyna startu rozsuwa się na teatr: z lewej wydma, z prawej góry; na grani stoi Szamil zwrócony ku wydmie; z góry
    zjeżdża szyld z tytułem (Podręcznik → Rytm: kurtyna ok. 2,5 s z kwestią, potem ≥1 s obrazu)."""
    kam(st, t, I["tytul"], 660, 380, lerp(1.0, 1.06, ease(t / T)), 0.8)
    teatr_kz(st, t, w)
    lalka(st, t, w.szamil, 990, 310, flip=-1, rece=(4, 0))
    J.hang(st, J.tag("The Imam Who Fought Russia for 25 Years", 36), CX, 74, P.rekwizyty + 0.02, pr(t, 0.5, 1.0), t, 31, h=66, drop=360,
           sway=0.7, strings=(0.15, 0.85), shadow=(5, 8, 8, 0.4))
    koniec(st, w, t)


def s_przedstawienie(st, w, t, T):
    """Kamera najeżdża na lalkę na grani; Szamil odwraca się do widza (orli profil, broda, turban); przy imieniu zjeżdża
    podpis „Imam Shamil” (wprowadzenie przed akcją, Wytyczne 1.26)."""
    kam(st, t, I["przedstawienie"], lerp(700, 960, ease(pr(t, 0, 2.5))), lerp(380, 470, ease(pr(t, 0, 2.5))),
        lerp(1.06, 1.7, ease(pr(t, 0, 2.6))), 0.8)
    teatr_kz(st, t, w)
    obrot = ease(pr(t, 0.5, 0.45))
    lalka(st, t, w.szamil, 990, 310, flip=lerp(-1, 1, obrot), rece=(4 + 14 * ease(pr(t, 2.6, 0.6)), 0))
    podpis(w, t, "Imam Shamil", 990, 250, 1.0, 3.2)
    koniec(st, w, t)


def tlo_kart(st, t, w, m=1.0):
    """Tło kart: ten sam teatr, przyciemniony, z plamą światła na kartach."""
    teatr_kz(st, t, w)
    st.spot = (CX, 300, P.rekwizyty, 560, 0.45)


def s_cytat_diuna(st, w, t, T):
    """Na nitce zjeżdża biała karta z maszynopisem — zdanie z Diuny o zabijaniu sztychem (tekst do sprawdzenia w wydaniu,
    księga D7); karta kołysze się i staje."""
    kam(st, t, I["cytat_diuna"], CX, 250, lerp(1.25, 1.32, t / T), 0.84)
    tlo_kart(st, t, w)
    karta_diuny(st, t, 150, pr(t, 0.0, 0.9))
    koniec(st, w, t, dim=0.96)


def s_kindzal(st, w, t, T):
    """Papierowy kindżał spada ostrzem w dół i wbija się w deskę sceny obok karty; drży; wstrząs kamery przy uderzeniu."""
    uderza = 0.25 + 0.32
    kam(st, t, I["kindzal"], 820, 330, 1.25, 0.84, shake=5 * _bump(t, uderza, 0.12))
    tlo_kart(st, t, w)
    karta_diuny(st, t, 150)
    kindzal_w_desce(st, t, 0.25)
    koniec(st, w, t, dim=0.96)


def s_cytat_1960(st, w, t, T):
    """Karta z Diuny podjeżdża wyżej, pod nią zjeżdża pożółkła karta z 1960 — to samo zdanie; kamera dojeżdża do obu."""
    kam(st, t, I["cytat_1960"], CX, lerp(300, 290, t / T), lerp(1.0, 1.1, ease(t / T)), 0.84)
    tlo_kart(st, t, w)
    karta_diuny(st, t, lerp(150, KARTA_Y[0], ease(pr(t, 0.2, 0.8))))
    karta_1960(st, t, KARTA_Y[1], pr(t, 0.5, 1.0))
    kindzal_w_desce(st, t)
    koniec(st, w, t, dim=0.96)


def s_ramka(st, w, t, T):
    """Ramka lupy przesuwa się po obu zdaniach; powtarzające się słowa podświetlają się po kolei na złoto (dwa dzwonki)."""
    kam(st, t, I["ramka"], CX, 300, 1.12, 0.84)
    tlo_kart(st, t, w)
    karta_diuny(st, t, KARTA_Y[0])
    karta_1960(st, t, KARTA_Y[1])
    kindzal_w_desce(st, t)
    gora, dol = (640, KARTA_Y[0] + 78), (640, KARTA_Y[1] + 78)
    k = ease(pr(t, 0.2, 1.4))
    lx, ly = lerp(gora[0] - 140, dol[0] + 140, k), lerp(gora[1], dol[1], k)
    for n, (cx, cy) in enumerate((gora, dol)):
        a = ease(pr(t, 0.4 + 0.7 * n, 0.3))
        if a > 0:
            st.put(J.glow(), cx, cy, P.rekwizyty + 0.02, w=560, anchor=(0.5, 0.5), mode="add", alpha=0.35 * a, shadow=None,
                   tint=(1.0, 0.82, 0.4))
    st.put(J.rek_kz("lupa"), lx, ly, P.rekwizyty + 0.03, h=190, anchor=(0.4, 0.4), rot=-10, shadow=(8, 10, 12, 0.4))
    koniec(st, w, t, dim=0.96)


def s_ksiazka(st, w, t, T):
    """Karty odjeżdżają w górę; z dołu wysuwa się okładka „The Sabres of Paradise · 1960” z górami i szablami; za nią cień
    lalki Szamila; kamera odjeżdża."""
    kam(st, t, I["ksiazka"], CX, lerp(300, 360, ease(t / T)), lerp(1.12, 1.0, ease(t / T)), 0.82)
    teatr_kz(st, t, w)
    st.spot = (CX, 360, P.rekwizyty, 620, 0.4)
    gora = 1 - ease(pr(t, 0.1, 0.8))
    karta_diuny(st, t, KARTA_Y[0], gora)
    karta_1960(st, t, KARTA_Y[1], gora)
    kindzal_w_desce(st, t)
    cien(st, t, w.szamil, 900, 360, STOPY - 40, P.lalki - 0.02, k=ease(pr(t, 1.2, 0.8)), flip=-1)
    Z0.rise(st, J.okladka(), CX, STOPY - 20, P.rekwizyty, ease(pr(t, 0.6, 0.9)), t, 41, h=380, lift=460, anchor=(0.5, 1.0),
            shadow=(8, 10, 12, 0.4))
    koniec(st, w, t)


def s_pytanie(st, w, t, T):
    """Wydma z lewej zapada się pod scenę (sypie się piasek), w jej miejscu wyrastają ośnieżone góry z mgłą; ściemnienie
    i zawieszka „Dagestan, 1834” (most w retrospekcję, bez kurtyny przed aktem I — Wytyczne 1.26)."""
    kam(st, t, I["pytanie"], lerp(640, 520, ease(t / T)), 380, lerp(1.0, 1.08, ease(t / T)), 0.8)
    zapada = ease(pr(t, 0.6, 1.6))
    teatr_kz(st, t, w, lewa=1 - zapada)
    for n in range(10):  # piasek sypie się z krawędzi zapadającej się wydmy
        if 0.6 < t < 2.4:
            f = (t * 1.7 + n * 0.11) % 1.0
            st.put(Z0.prop("kulka"), 120 + n * 52, 520 + f * 200, P.wzgorza + 0.003, h=8, anchor=(0.5, 0.5), tint=(0.95, 0.75, 0.45),
                   shadow=None, alpha=1 - f)
    Z0.rise(st, J.gory("blisko", 4), 320, 720, P.wzgorza - 0.004, ease(pr(t, 2.0, 1.4)), t, 44, w=1200, wob=0.0, lift=420,
            anchor=(0.5, 1.0))
    if t > 2.6:  # mgła z bibuły u stóp nowych gór
        st.put(J.S("cloud_center", 0.4), 320 + 20 * noise(t, 45, 0.3), 640, P.wzgorza + 0.006, w=900, anchor=(0.5, 0.5),
               alpha=0.55 * ease(pr(t, 2.6, 1.0)), tint=(0.92, 0.92, 0.96), shadow=None)
    podpis(w, t, "Dagestan, 1834", CX, 40, T - 2.2, 4.0)
    koniec(st, w, t)


# ---------------------------------------------------------------- akt I: imam, Achulgo, syn na północ

def s_slowo_kindjal(st, w, t, T):
    """Nad górami na nitce zjeżdża słowo KINDJAL, obraca się i zmienia w kindżał, który wsuwa się za pas Szamila na grani
    (słowo z Diuny otwiera akt I — szkic D)."""
    kam(st, t, I["slowo_kindjal"], 700, 380, 1.15, 0.8)
    kaukaz(st, t, w, aul=1080)
    sx = 700
    lalka(st, t, w.szamil, sx, 280, flip=1, rece=(6, 0))
    obrot = pr(t, 0.75, 0.35)
    if obrot < 1:
        J.hang(st, J.slowo("KINDJAL"), sx, 150, P.rekwizyty, pr(t, 0.0, 0.6), t, 51, h=86, sx=max(0.05, math.cos(obrot * math.pi / 2)),
               drop=420, shadow=(5, 8, 8, 0.4))
    else:  # kindżał spada z miejsca karty do pasa lalki (pas ok. 0,58 wysokości lalki nad stopami)
        k = ease(pr(t, 1.1, 0.5))
        st.put(J.rek_kz("kindzal"), sx + 6, lerp(200, STOPY - 280 * 0.6, k), P.lalki + 0.03, h=lerp(140, 70, k), anchor=(0.5, 0.1),
               rot=lerp(25, 0, k), alpha=1 - pr(t, 1.55, 0.15), shadow=(4, 6, 6, 0.35))
    podpis(w, t, "Dagestan, 1834", CX, 40, -2.0, 2.4)
    koniec(st, w, t)


def s_imam(st, w, t, T):
    """Jeźdźcy w czerni wjeżdżają po kolei (każdy z własnym opóźnieniem), na czele Szamil; zawieszka „Dagestan, 1834”
    odjeżdża w górę; przy „Shamil” kamera trzyma go w środku."""
    kam(st, t, I["imam"], lerp(560, 760, ease(t / T)), 400, 1.08, 0.8)
    kaukaz(st, t, w, aul=1060)
    jada = [("murid3", 0.9), ("murid2", 0.55), ("murid", 0.25), (w.szamil, 0.0)]
    for n, (key, d) in enumerate(jada):
        x = lerp(-200 - n * 40, 980 - n * 190, ease_out(pr(t, d, 3.2)))
        jezdziec(st, t, key, x, STOPY - 4 + (n % 2) * 6, P.lalki + 0.004 * (3 - n), flip=1, h=190, seed=n * 3,
                 galop=1 - pr(t, d + 2.8, 0.6), trzyma=SZABLA(120) if key.startswith("murid") else None, rece=(12, 0))
    koniec(st, w, t)


def s_twarz(st, w, t, T):
    """Zbliżenie: Szamil unosi wzrok; wiatr szarpie frędzlem turbanu (zbliżenie twarzy, kamera dojeżdża)."""
    kam(st, t, I["twarz"], 650, STOPY - 280 * 0.86, lerp(3.4, 3.7, t / T), 0.8)
    kaukaz(st, t, w, kul=False)
    lalka(st, t, w.szamil, 640, 280, flip=1, rece=(8, 0), lean=-4 * ease(pr(t, 0.4, 0.6)))
    koniec(st, w, t)


def s_muridzi(st, w, t, T):
    """Muridzi w czarnych czerkieskach jeden po drugim unoszą szable (fala, jeden spóźniony); nad nimi „TO THE DEATH!”.
    Szabla w dłoni za rękojeść, ręka z łokciem (uklad.py)."""
    kam(st, t, I["muridzi"], CX, 400, 1.1, 0.8)
    kaukaz(st, t, w, aul=1100)
    ludzie = ["murid", "murid2", "murid3", "ghazi", "murid4", "murid5"]  # każdy inny (1.6)
    for n, key in enumerate(ludzie):
        d = 0.7 + 0.22 * n + (0.5 if n == 4 else 0.0)  # piąty się spóźnia
        up = ease(pr(t, d, 0.35))
        nazwa = f"murid {n + 1}"
        szk = K.lalka(st, t, nazwa, key, 170 + n * 190, 270 - (n % 2) * 16, flip=1 if n < 3 else -1, y=STOPY - (n % 2) * 6,
                      glebia=n % 2, przod=lerp(10, 165, up), lokiec=("gora", "dol"))
        K.w_dloni(st, t, f"szabla ({nazwa})", "szabla", szk, 130 * 90 / 520, rot=-90)
    podpis(w, t, "TO THE DEATH!", CX, 70, 2.2, T)
    koniec(st, w, t)


def s_choragiew(st, w, t, T):
    """Czarna chorągiew imamatu rozwija się na wietrze nad aułem (łopot)."""
    kam(st, t, I["choragiew"], 700, 300, 1.6, 0.75)
    kaukaz(st, t, w, aul=820)
    k = ease_out(pr(t, 0.1, 0.9))
    st.put(J.rek_kz("choragiew"), 600, 560, P.drzewa, h=430, anchor=(0.04, 1.0), sx=max(0.15, k) * (1 + 0.04 * math.sin(t * 11)),
           rot=1.5 * math.sin(t * 7), shadow=(6, 8, 10, 0.35))
    koniec(st, w, t)


def s_armia(st, w, t, T):
    """Kamera odjeżdża: z północy w doliny wchodzą rzędy piechoty w białych czapkach aż po horyzont, działa na wozach; mała
    lalka Szamila patrzy z grani (potęga = liczba i przestrzeń, Wytyczne 1.17). Karabiny w tylnej dłoni (uklad_kz.zolnierz)."""
    kam(st, t, I["armia"], CX, 400, lerp(1.5, 0.98, ease(pr(t, 0, T * 0.8))), 0.7)
    kaukaz(st, t, w, blisko=False)
    u = K.uk(st, t)
    rzedy = [(0.50, 470, 40, 16), (0.56, 520, 54, 13), (0.63, 580, 74, 10), (0.71, 650, 100, 8), (0.80, STOPY, 150, 6)]
    for r, (p, y, h, n_) in enumerate(rzedy):
        u.rzedy[f"szereg{r}"] = p
        for n in range(n_):
            d = 0.2 * r + n * 0.12
            x = lerp(-120, 1400, ((t - d) * (70 + 10 * r) / 1500 + n / n_) % 1.0) if t > d else -999
            if x < -100:
                continue
            K.zolnierz(st, t, f"żołnierz {r}.{n}", ZOLNIERZE[(n + 2 * r) % 6], x, h, y=y, rzad=f"szereg{r}", flip=-1, hop=4)
    u.rzedy["armaty"] = 0.66
    for n in range(2):  # działa ciągną konie, na koniu artylerzysta (Wytyczne 1.6: pojazd ma to, co go napędza)
        xa = lerp(1500, -200, ((t * 60 + n * 700) % 1700) / 1700)
        u.put(f"armata {n + 1}", J.rek_kz("armata"), xa, 640, 0.66, h=60, anchor=(0.5, 1.0))
        xk = xa - 57 - 40
        K.jezdziec(st, t, f"artylerzysta {n + 1}", ("zolnierz3", "zolnierz5")[n], xk, 640, "armaty", -1, 64, galop=0.3, seed=n)
        with u.obiekt(f"uprząż {n + 1}", "rzecz"):
            st.line([(xa - 50, 622), (xk + 20, 610)], 0.661, width=1.6, color=(70, 50, 36), alpha=0.9)
    u.rzedy["gran"] = P.gory + 0.01
    K.lalka(st, t, "Szamil na grani", w.szamil, 1180, 80, y=430, rzad="gran", flip=-1)
    koniec(st, w, t)


def s_akhulgo(st, w, t, T):
    """Kamera dojeżdża do skały: na szczycie wyrasta twierdza z kamieni, kołysze się i osiada; u stóp rozstawiają się namioty;
    zawieszka „Akhulgo, 1839”."""
    kam(st, t, I["akhulgo"], 660, lerp(400, 360, ease(t / T)), lerp(1.0, 1.2, ease(t / T)), 0.62)
    kaukaz(st, t, w, twierdza=True, rzeka_=True, namioty=6, blisko=False)
    podpis(w, t, "Akhulgo, 1839", 380, 40, 0.5, T)
    koniec(st, w, t)


def s_armaty(st, w, t, T):
    """Armaty dają ognia po kolei; dym z bibuły; kamienie odpryskują od murów; wstrząs kamery."""
    strzaly = (0.15, 0.55, 0.95)
    kam(st, t, I["armaty"], 600, 380, 1.1, 0.7, shake=sum(6 * _bump(t, s_, 0.12) for s_ in strzaly))
    kaukaz(st, t, w, twierdza=True, namioty=4, blisko=False)
    for n, s_ in enumerate(strzaly):
        x = 180 + n * 170
        st.put(J.rek_kz("armata"), x, STOPY - 8, P.lalki + 0.01 * n, h=150, anchor=(0.5, 1.0), rot=-3 * _bump(t, s_, 0.2))
        blysk(st, x + 90, STOPY - 90, P.lalki + 0.02, t, s_, r=220)
        dym(st, x + 110, STOPY - 100, P.lalki + 0.02, t, s_, seed=n)
        kk = pr(t, s_ + 0.25, 0.6)
        if 0 < kk < 1:  # kamienie odpryskują od muru twierdzy
            for m in range(3):
                st.put(Z0.prop("kamien"), 640 + m * 30 + 80 * kk, 250 + 120 * kk ** 2 - 40 * kk, P.most + 0.01, h=16,
                       anchor=(0.5, 0.5), rot=200 * kk, shadow=None)
    koniec(st, w, t)


def s_szturm(st, w, t, T):
    """Drabiny przystawione do skały; żołnierze wspinają się po szczeblach (dłonie na szczeblach), pierwszy spada („AAA!”),
    reszta się cofa."""
    kam(st, t, I["szturm"], 640, 360, 1.3, 0.75)
    kaukaz(st, t, w, twierdza=True, blisko=False)
    u = K.uk(st, t)
    drabiny = []
    for n, x in enumerate((430, 760)):
        rot = 12 - 24 * n
        u.put(f"drabina {n + 1}", J.rek_kz("drabina"), x, STOPY, P.lalki - 0.01, h=420, anchor=(0.5, 1.0), rot=rot)
        drabiny.append((x, rot))

    def szczebel(nr, x, rot, yy):
        """Punkt na środku drabiny na wysokości yy (drabina 160 × 600 → h 420, obrót wokół stopy)."""
        L = STOPY - yy
        return x + math.sin(math.radians(rot)) * L, yy
    for n in range(3):
        wspina = ease(pr(t, 0.05 * n, 0.8))
        cofa = ease(pr(t, 1.0, 0.6))
        dr = 0 if n != 1 else 1
        dx, rot = drabiny[dr]
        y = STOPY - wspina * 180 + cofa * 180
        if n == 0 and t > 0.7:  # pierwszy spada (puszcza drabinę)
            f = pr(t, 0.7, 0.5)
            K.lalka(st, t, "żołnierz 1", "zolnierz", 470 - 40 * f, 150, y=STOPY - 230 + 230 * f ** 2, flip=1, lean=-80 * f,
                    przod=150, tyl=120)
            continue
        x = szczebel(dr, dx, rot, y)[0] - 8 * (1 if dr == 0 else -1)
        szk = K.lalka(st, t, f"żołnierz {n + 1}", "zolnierz2" if n else "zolnierz", x, 150, y=y, flip=1 if dr == 0 else -1,
                      glebia=0.5, przod=lambda s, dr=dr, dx=dx, rot=rot: szczebel(dr, dx, rot, s["bark_przod"][1] - 30),
                      tyl=lambda s, dr=dr, dx=dx, rot=rot: szczebel(dr, dx, rot, s["bark_tyl"][1] - 10))
        if szk:
            u.dotyka(f"drabina {dr + 1}", (*szk["przod"]["dlon"], szk["p"]), f"żołnierz {n + 1}: dłoń na drabinie", 6.0)
    podpis(w, t, "AAA!", 470, 300, 0.75, 1.0)
    koniec(st, w, t)


def s_zakladnik(st, w, t, T):
    """Na murze unosi się biała flaga; Szamil kładzie dłoń na ramieniu chłopca; przy imieniu zjeżdża podpis
    „Jamal al-Din, Shamil's son”. Dłoń idzie do barku chłopca (cel z jego szkieletu), kontrola: dłoń na chłopcu."""
    kam(st, t, I["zakladnik"], 640, 420, 1.2, 0.8)
    kaukaz(st, t, w, twierdza=True, blisko=False)
    u = K.uk(st, t)
    u.put("mur", J.mur(900, 120), CX, STOPY + 40, P.lalki + 0.02, w=1300, sy=0.6, anchor=(0.5, 1.0))
    flaga = ease(pr(t, 0.2, 0.9))
    st.put(J.rek_kz("flaga_biala"), 330, STOPY - 60 + (1 - flaga) * 300, P.lalki - 0.01, h=300, anchor=(0.04, 1.0),
           rot=2 * math.sin(t * 5))
    # chłopiec 8–12 lat: lalka 190 (0,63 dorosłego) — przy 160 bark dziecka był niżej, niż sięga dłoń dorosłego (kontrola 28.11)
    syn = K.lalka(st, t, "chłopiec", "dzamal_maly", 700, 190, flip=-1, glebia=0.5)
    kladzie = ease(pr(t, 1.2, 0.6))
    start = lambda s: K.U.Uklad.dlon_z_kata(s, 8)  # ruch zaczyna się od opuszczonej ręki (zawsze w zasięgu)
    cel = (lambda s: lerp(start(s)[0], syn["punkt"](120, 214)[0], kladzie) if syn else 0,
           lambda s: lerp(start(s)[1], syn["punkt"](120, 214)[1], kladzie) if syn else 0)
    # Szamil stoi tak, żeby bark chłopca był ok. 85% zasięgu jego ręki (postać podchodzi do celu, Wytyczne 1.28)
    sz = K.lalka(st, t, "Szamil", w.szamil, 650, 300, flip=1, przod=(lambda s: (cel[0](s), cel[1](s))) if syn else 5)
    if sz and syn and kladzie >= 1:
        u.dotyka("chłopiec", (*sz["przod"]["dlon"], sz["p"]), "dłoń Szamila na ramieniu chłopca", 6.0)
    u.widac("chłopiec", 0.95, "chłopiec: widać ≥ 95% (poza murem, który zasłania go od pasa)", oprocz=("rampa", "mur", "Szamil"))
    podpis(w, t, "Jamal al-Din, Shamil's son", 720, 250, 4.7, 2.8)  # na imię (1.27)
    koniec(st, w, t)


def s_chlopiec(st, w, t, T):
    """Mały chłopiec idzie ścieżką między bagnetami w dół, do obozu; w połowie drogi ogląda się za siebie."""
    kam(st, t, I["chlopiec"], lerp(520, 760, t / T), 420, 1.25, 0.8)
    kaukaz(st, t, w, namioty=5, blisko=False)
    u = K.uk(st, t)
    for n in range(6):
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], 280 + n * 150, 260, y=STOPY + (n % 2) * 8,
                   glebia=(n % 2) * 3, flip=-1 if n < 3 else 1)
    x = lerp(240, 940, ease_out(pr(t, 0.0, T * 0.95)))
    oglada = _bump(t, T * 0.5, 0.35) > 0
    u.rzedy["chlopiec"] = P.lalki + 0.025
    K.lalka(st, t, "chłopiec", "dzamal_maly", x, 160, rzad="chlopiec", flip=-1 if oglada else 1, hop=4)
    u.widac("chłopiec", 0.95, "chłopiec: widać ≥ 95% (idzie przed żołnierzami)")
    koniec(st, w, t)


def s_ojciec(st, w, t, T):
    """Zbliżenie: Szamil odwraca twarz, zaciska dłoń na rękojeści kindżału (dłoń do punktu rękojeści na pasie)."""
    kam(st, t, I["ojciec"], 640, STOPY - 280 * 0.72, 2.8, 0.8)
    kaukaz(st, t, w, twierdza=True, blisko=False, kul=False)
    obrot = ease(pr(t, 0.3, 0.4))
    zaciska = ease(pr(t, 0.6, 0.5))
    K.lalka(st, t, "Szamil", w.szamil, 640, 280, flip=lerp(1, -1, obrot), lean=-3 * obrot,
            przod=(lambda s: (lerp(s["bark_przod"][0], s["punkt"](156, 336)[0], zaciska),
                              lerp(s["bark_przod"][1] + s["L"][0] + s["L"][1], s["punkt"](156, 336)[1], zaciska))))
    koniec(st, w, t, dim=0.92)


def s_ucieczka(st, w, t, T):
    """Noc, księżyc na nitce; twierdza płonie; maleńkie postacie spuszczają się na linach po skale do jaskini nad rzeką.
    Dłonie na linie (cel na linie, kontrola: dłoń przy linie)."""
    w.noc = 1.0
    kam(st, t, I["ucieczka"], 660, 360, 1.2, 0.62)
    kaukaz(st, t, w, twierdza=True, rzeka_=True, blisko=False)
    u = K.uk(st, t)
    for n in range(5):
        if bk(w, 0.6) >= 1:
            plomien(st, 540 + n * 60, 312 + (n % 2) * 8, P.most + 0.004, t, h=40 + 36 * pr(t, 0, T) + 8 * (n % 2), seed=n * 3)
    u.rzedy["skala"] = P.most + 0.008
    for n in range(3):
        x0, y0, x1, y1 = 560 + n * 60, 250, 570 + n * 60, 600
        lina = f"lina {n + 1}"
        with u.obiekt(lina, "rzecz"):
            st.line([(x0, y0), (x1, y1)], P.most + 0.006, width=1.8, color=(220, 200, 160), alpha=0.9)
        y = lerp(300, 560, ease(pr(t, 0.5 + 0.5 * n, T - 1.5)))
        xl = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
        na_linie = lambda yy, x0=x0, x1=x1: (x0 + (x1 - x0) * (yy - y0) / (y1 - y0), yy)
        szk = K.lalka(st, t, f"uciekinier {n + 1}", "szamil" if n == 0 else "murid", xl + 9, 42, y=y, rzad="skala", flip=-1,
                      przod=lambda s, f=na_linie: f(s["bark_przod"][1] - 6), tyl=lambda s, f=na_linie: f(s["bark_tyl"][1] + 4))
        if szk:
            u.dotyka(lina, (*szk["przod"]["dlon"], szk["p"]), f"uciekinier {n + 1}: dłoń na linie", 3.0)
    koniec(st, w, t)


def s_tratwa(st, w, t, T):
    """Gag: po rzece płynie tratwa ze słomianymi kukłami w papachach; żołnierze z latarniami (światło w dłoni) biegną brzegiem
    za nią („THERE!”); w tle w drugą stronę przemyka cień prawdziwych uciekinierów."""
    w.noc = 1.0
    kam(st, t, I["tratwa"], lerp(560, 760, t / T), 430, 1.2, 0.75)
    kaukaz(st, t, w, rzeka_=True, blisko=True)
    tx = lerp(300, 980, t / T)
    st.put(J.rek_kz("tratwa"), tx, 690 + 4 * math.sin(t * 3), P.drzewa + 0.004, h=110, anchor=(0.5, 1.0), rot=2 * math.sin(t * 2.3))
    for n in range(3):
        x = lerp(80 - n * 90, tx - 140 - n * 90, ease(pr(t, 0.2 + 0.1 * n, T - 0.4)))
        szk = K.lalka(st, t, f"żołnierz {n + 1}", "zolnierz", x, 200, y=STOPY + 6, glebia=n, flip=1, hop=8, przod=80)
        if szk:
            hx, hy = szk["przod"]["dlon"]
            st.put(J.rek_kz("swieca"), hx, hy, szk["p"] + 0.0005, h=40, anchor=(0.5, 0.88), z=0.08)
            st.put(J.glow(), hx, hy - 30, szk["p"] + 0.001, w=170, anchor=(0.5, 0.5), mode="add", alpha=0.5, shadow=None,
                   tint=(1.0, 0.8, 0.4))
            plomien(st, hx, hy - 33, szk["p"] + 0.0006, t, h=14, seed=n)
    for n in range(3):  # cień prawdziwych uciekinierów w tle, w drugą stronę
        cien(st, t, "murid", lerp(1100, 700, pr(t, 0.4, T)) - n * 40, 60, 590, P.wzgorza - 0.01, flip=-1, hop=3, seed=n)
    podpis(w, t, "THERE!", 300, 150, 0.6, 1.5)
    koniec(st, w, t)


def s_petersburg(st, w, t, T):
    """Kryta kibitka jedzie śnieżną drogą na północ; w okienku twarz chłopca (chłopiec siedzi ZA wozem, widać go przez
    otwór okna — Wytyczne 1.1); na horyzoncie wyrastają złote iglice; zawieszka „St Petersburg”."""
    kam(st, t, I["petersburg"], 640, 400, 1.05, 0.8)
    petersburg(st, t, w)
    u = K.uk(st, t)
    x = lerp(-200, 760, ease_out(pr(t, 0, T * 0.85)))
    hk = 200
    rot = 1.2 * math.sin(t * 7)
    u.put("kibitka", J.rek_kz("kibitka_okno"), x, STOPY, P.lalki, h=hk, anchor=(0.5, 1.0), rot=rot)
    K.zaprzeg(st, t, "kibitka", K.pkt("kibitka_okno", 580, 238, x, STOPY, hk)[0], STOPY, P.lalki, 1,
              siedzisko=(K.pkt("kibitka_okno", 560, 232, x, STOPY, hk), "kibitka"), galop=0.6)
    ox0, oy0 = K.pkt("kibitka_okno", 262, 112, x, STOPY, hk)
    ox1, oy1 = K.pkt("kibitka_okno", 358, 178, x, STOPY, hk)
    u.rzedy["w_kibitce"] = P.lalki - 0.004
    K.lalka(st, t, "chłopiec w kibitce", "dzamal_maly", x + 4, 120, y=K.y_siedzi("dzamal_maly", 120, oy1 + 4), rzad="w_kibitce",
            flip=-1, siedzi=True, wejscie=False)
    u.w_otworze("chłopiec w kibitce", (ox0 - 3, oy0 - 3, ox1 + 3, oy1 + 3, P.lalki), "chłopca widać tylko przez okno kibitki")
    for n in range(14):  # śnieg z bibuły
        f = (t * 0.25 + n * 0.13) % 1.0
        st.put(Z0.prop("kulka"), (n * 97 + 40 * math.sin(t + n)) % 1300, -20 + f * 760, P.rekwizyty, h=9, anchor=(0.5, 0.5),
               tint=(1.0, 1.0, 1.0), shadow=None)
    podpis(w, t, "St Petersburg", 980, 40, 1.4, T)
    koniec(st, w, t, extra=(0.94, 0.97, 1.04))


KRESKI_T0, KRESKA_DL = 0.8, 0.3  # pierwsza kreska na kamieniu i czas jednej kreski (kindżał ryje od góry w dół)


def s_koniec_aktu1(st, w, t, T):
    """Szamil sam na grani; czubkiem kindżału ryje kreskę na kamieniu, za nią następne (lata). Narzędzie liczy się od końca,
    który pracuje (Wytyczne 1.28): czubek na kamieniu → rękojeść → dłoń → miejsce lalki. Kurtyna zasuwa się w pauzie
    (render: „Act 2 — KANLY · How do you buy back a son?”)."""
    kam(st, t, I["koniec_aktu1"], 700, 420, lerp(1.1, 1.35, ease(t / T)), 0.8)
    kaukaz(st, t, w, aul=1100)
    u = K.uk(st, t)
    u.put("kamień", J.rek_kz("kamien_kreski"), 820, STOPY, P.lalki + 0.02, h=150, anchor=(0.5, 1.0))
    n = int(clamp((t - KRESKI_T0) / KRESKA_DL, 0, 15))
    pozycja = lambda k: (796 + (k % 8) * 8, 588 + (k // 8) * 32)  # w zasięgu ręki (kontrola 28.11)
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
    szk = K.lalka(st, t, "Szamil", w.szamil, 768, 300, flip=1, przod=dlon_)
    geo = K.w_dloni(st, t, "kindżał", "kindzal", szk, hk, rot=rot)
    if geo and ryje:
        u.dotyka("kamień", (*geo(40, 414), P.lalki + 0.02), "czubek kindżału na kamieniu", 5.0)
    koniec(st, w, t)


# ---------------------------------------------------------------- akt II: syn i księżne

def s_kadet(st, w, t, T):
    """Mała lalka chłopca w mundurze kadeta chowa się w dół, na jej miejsce wysuwa się wysoki młody oficer z wąsikiem (ta sama
    twarz); podpis „Jamal al-Din” na chwilę (zmiana wieku widoczna w kadrze, Wytyczne 1.15)."""
    kam(st, t, I["kadet"], CX, 420, 1.15, 0.8)
    sala_balowa(st, t, w)
    lalka(st, t, "dzamal_kadet", 640, 200, flip=1, sink=ease(pr(t, 1.2, 0.6)), seed=5)
    lalka(st, t, "dzamal_oficer", 640, 310, flip=1, k=ease(pr(t, 1.7, 0.7)), seed=6)
    podpis(w, t, "Jamal al-Din", 640, 260, 2.6, 2.4)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def s_bal(st, w, t, T):
    """Oficer kłania się na balu, pary wirują za nim (partnerzy trzymają się za ręce — dłonie w jednym punkcie), żyrandol
    migocze."""
    kam(st, t, I["bal"], lerp(560, 720, t / T), 420, 1.2, 0.8)
    sala_balowa(st, t, w)
    u = K.uk(st, t)
    u.rzedy["pary"] = P.lalki - 0.03
    for n in range(3):
        a = t * 2.2 + n * 2.1
        x = 420 + n * 230 + 60 * math.cos(a)
        prawo = math.sin(a) > 0
        reka = (x + 20, STOPY - 30 - 230 * 0.55)
        d = K.lalka(st, t, f"dama {n + 1}", ("dama", "dama2", "dama3")[n], x, 230, y=STOPY - 30, rzad="pary", flip=1 if prawo else -1, przod=reka, glebia=0.2)
        o = K.lalka(st, t, f"oficer {n + 1}", ("oficer_ros", "oficer_ros2", "oficer_ros3")[n], x + 40, 240, y=STOPY - 30, rzad="pary", flip=-1 if prawo else 1, przod=reka)
        if d and o:
            u.kontakt((*d["przod"]["dlon"], d["p"]), (*o["przod"]["dlon"], o["p"]), f"para {n + 1}: dłonie razem", 4.0)
    K.lalka(st, t, "Dżamaluddin", "dzamal_oficer", 640, 310, flip=1, lean=-18 * _bump(t, 1.0, 0.5), przod=20 * _bump(t, 1.0, 0.5))
    st.put(J.glow(), CX, 120, P.most, w=600, anchor=(0.5, 0.5), mode="add", alpha=0.18 + 0.05 * math.sin(t * 9), shadow=None)
    koniec(st, w, t, extra=(1.04, 1.0, 0.92))


def s_kalendarz(st, w, t, T):
    """Kartki zdzieranego kalendarza lecą jedna po drugiej: 1840… 1848… 1854."""
    kam(st, t, I["kalendarz"], CX, 330, 1.4, 0.84)
    kaukaz(st, t, w, aul=1000)
    lata = (1840, 1844, 1848, 1851, 1854)
    n = min(len(lata) - 1, int(t / 0.36))
    st.put(J.kalendarz_rok(lata[n]), CX, 180, P.rekwizyty, h=260, anchor=(0.5, 0.0), shadow=(6, 9, 10, 0.4))
    if n > 0:  # poprzednia kartka odlatuje
        f = (t - n * 0.36) / 0.36
        st.put(J.kalendarz_rok(lata[n - 1]), CX - 260 * f, 180 - 160 * f, P.rekwizyty + 0.01, h=260, anchor=(0.5, 0.0), rot=-50 * f,
               alpha=1 - f, shadow=(6, 9, 10, 0.3))
    koniec(st, w, t)


def s_tsinandali(st, w, t, T):
    """Kamera dojeżdża do dworu wśród winnic; zawieszka „Tsinandali, Georgia, 1854”; na grzbiecie za murem wyrastają jeźdźcy;
    podpis „Ghazi Muhammad, Shamil's son” przy imieniu."""
    kam(st, t, I["tsinandali"], lerp(640, 760, ease(t / T)), 400, lerp(1.0, 1.15, ease(t / T)), 0.7)
    gruzja(st, t, w)
    mur_przod(st, t, w)
    for n in range(4):
        jezdziec(st, t, "ghazi" if n == 0 else ("murid", "murid2", "murid3")[n - 1], 260 + n * 120, 600, P.most + 0.01, flip=1, h=110,
                 k=ease(pr(t, 2.2 + 0.2 * n, 0.6)), seed=n, galop=0.3)
    podpis(w, t, "Tsinandali, Georgia, 1854", 420, 40, 0.5, T)
    podpis(w, t, "Ghazi Muhammad, Shamil's son", 560, 330, 3.8, 3.0)
    koniec(st, w, t)


def s_jezdzcy(st, w, t, T):
    """Jeźdźcy przeskakują mur winnicy, liście winorośli fruwają."""
    kam(st, t, I["jezdzcy"], 640, 400, 1.15, 0.75, shake=3 * _bump(t, 0.5, 0.2))
    gruzja(st, t, w, kul=False)
    mur_przod(st, t, w)
    for n in range(3):
        f = pr(t, 0.1 * n, 1.2)
        x = lerp(200 + n * 150, 760 + n * 170, f)
        y = STOPY - 160 * math.sin(math.pi * clamp(f * 1.6)) * (f < 0.62)
        jezdziec(st, t, ("ghazi", "murid", "murid2")[n], x, y, P.lalki + 0.02 * n, flip=1, h=210, seed=n * 2, trzyma=SZABLA(120, -60))
    for n in range(12):  # liście winorośli
        f = (t * 1.3 + n * 0.17) % 1.0
        st.put(Z0.prop("kulka"), 300 + n * 70 + 60 * f, 520 - 200 * f + 260 * f * f, P.rekwizyty, h=14, anchor=(0.5, 0.5),
               tint=(0.4, 0.7, 0.3), shadow=None, rot=300 * f)
    koniec(st, w, t)


def s_ksiezne(st, w, t, T):
    """Dwie księżne w białych czepcach na koniach jeźdźców (za jeźdźcem), dzieci przed nimi, guwernantka na trzecim koniu;
    podpisy „Princess Anna Chavchavadze” i „Princess Varvara Orbeliani” po kolei, za kwestią. Każdy siedzący ma kontrolę
    siodła (uklad_kz.jezdziec)."""
    kam(st, t, I["ksiezne"], lerp(520, 760, t / T), 420, 1.1, 0.8)
    gruzja(st, t, w)
    grupy = [("ghazi", "anna", "dziecko_g"), ("murid", "warwara", "dziecko_g2"), ("murid2", "guwernantka", None)]
    for n, (jezdzc, pani, dziecko) in enumerate(grupy):
        x = lerp(-120 - n * 330, 1000 - n * 330, pr(t, 0, T))
        jezdziec(st, t, jezdzc, x, STOPY - n * 4, P.lalki + 0.006 * (2 - n), flip=1, h=200, seed=n * 5, galop=0.6, pasazer=pani,
                 dziecko=dziecko)
    podpis(w, t, "Princess Anna Chavchavadze", 330, 250, 2.7, 1.0)  # na imię (1.27)
    podpis(w, t, "Princess Varvara Orbeliani", 800, 250, 3.8, 2.6)
    koniec(st, w, t)


OKNO_WEDENO = (300, 150, 520, 330)  # otwór okna w arkuszu ściany 900 × 560 (zestaw_kz.rek_kz("sciana_okno"))


def s_perly(st, w, t, T):
    """Sznur pereł pęka, perły toczą się po pyle i zostają."""
    kam(st, t, I["perly"], CX, 640, 2.6, 0.84)
    gruzja(st, t, w, kul=False)
    if t < 0.35:
        st.put(J.rek_kz("perly"), CX, 560 + 200 * pr(t, 0, 0.35) ** 2, P.rekwizyty, h=120, anchor=(0.5, 0.5), rot=20 * t)
    else:
        for n in range(11):
            f = ease_out(pr(t, 0.35, 0.9))
            x = CX - 110 + n * 22 + (n - 5) * 28 * f
            st.put(J.rek_kz("perla"), x, 690 - 40 * math.sin(math.pi * pr(t, 0.35, 0.3)) * (n % 2), P.rekwizyty, h=20,
                   anchor=(0.5, 1.0), shadow=(2, 3, 3, 0.4))
    koniec(st, w, t)


def s_vedeno(st, w, t, T):
    """Auł Wedeno w górach; księżne w kamiennym domu — stoją ZA ścianą, widać je tylko przez otwór okna (Wytyczne 1.1);
    przed domem straż z karabinem; zawieszka „Vedeno”."""
    kam(st, t, I["vedeno"], lerp(640, 700, ease(t / T)), 420, lerp(1.0, 1.2, ease(t / T)), 0.75)
    kaukaz(st, t, w, aul=640, blisko=False)
    u = K.uk(st, t)
    sw, sx0, sy1 = 620, 700, STOPY
    sk = sw / 900
    u.put("ściana domu", J.rek_kz("sciana_okno"), sx0, sy1, u.p("sciana_domu"), w=sw, anchor=(0.5, 1.0))
    x0, y0 = sx0 + (OKNO_WEDENO[0] - 450) * sk, sy1 - (560 - OKNO_WEDENO[1]) * sk
    x1, y1 = sx0 + (OKNO_WEDENO[2] - 450) * sk, sy1 - (560 - OKNO_WEDENO[3]) * sk
    for n, (key, dx, fl) in enumerate((("anna", -30, 1), ("warwara", 34, -1))):
        K.lalka(st, t, key, key, sx0 + dx, 190, y=y1 + 150, rzad="dom", flip=fl, glebia=n)
        u.w_otworze(key, (x0 - 2, y0 - 2, x1 + 2, y1 + 2, u.p("sciana_domu")), f"{key}: widać tylko przez okno")
    K.zolnierz(st, t, "strażnik", "murid2", 420, 290)
    podpis(w, t, "Vedeno", 380, 40, 0.5, T)
    koniec(st, w, t)


def s_cena(st, w, t, T):
    """Szamil siedzi za niskim stolikiem i pisze piórem list: stalówka na kartce (narzędzie od końca, który pracuje — 1.28);
    pierwsza liczba jest ogromna, przekreśla ją i pisze „40,000”, obok rysunek chłopca i rządek jeńców."""
    kam(st, t, I["cena"], 640, 540, 1.7, 0.8)
    izba(st, t, w)
    u = K.uk(st, t)
    stol = K.ark("stol_niski")
    u.rzecz("stolik", stol, 640, STOPY + 10, u.p("przod"), (180, 120), 100)
    blat_y = K.pkt("stol_niski", 180, 20, 640, STOPY + 10, 100)[1]
    kartka = u.rzecz("list", K.ark("kartka_list"), 680, blat_y, u.p("przod", 0.3), (110, 160), 60, rot=-4)
    pisze = 0.8 < t < 4.6
    # stalówka nisko na kartce, pióro małe i stromo: pióro nie przechodzi przez twarz (arkusz dłoni 28.11)
    nib = (lerp(652, 688, ((t - 0.8) * 0.8) % 1.0), blat_y - 12 + 4 * math.sin(t * 9)) if pisze else (670, blat_y - 30)
    hp, rot = 22, -112
    kk = hp / 70
    ox, oy = _off((0 - 170) * kk, (42 - 30) * kk, rot)
    szk = K.lalka(st, t, "Szamil", w.szamil, 596, 300, flip=1, siedzi=True, y=K.y_siedzi(w.szamil, 300, blat_y + 14),
                  przod=(nib[0] - ox, nib[1] - oy))
    geo = K.w_dloni(st, t, "pióro", "pioro", szk, hp, rot=rot)
    if geo and pisze:
        u.dotyka("list", (*geo(0, 42), u.p("przod", 0.3)), "stalówka na kartce", 5.0)
    with u.obiekt("list"):  # to, co napisane, jest częścią kartki (bufor identyfikatorów)
        st.put(J.tag("000000", 20), 680, STOPY - 132, P.lalki + 0.05, h=40, anchor=(0.5, 0.5), alpha=ease(pr(t, 0.8, 0.4)), shadow=None)
        if t > 2.2:
            st.line([(615, STOPY - 132), (745, STOPY - 132)], P.lalki + 0.052, width=4, color=(170, 30, 30), alpha=1.0)
        st.put(J.tag("40,000", 22), 680, STOPY - 96, P.lalki + 0.05, h=42, anchor=(0.5, 0.5), alpha=ease(pr(t, 3.0, 0.4)), shadow=None)
    u.widac("list", 0.6, "list: widać ≥ 60% (dłoń i pióro na kartce)", oprocz=("rampa", "Szamil", "pióro"))
    koniec(st, w, t, extra=(1.02, 0.98, 0.92))


def s_monety(st, w, t, T):
    """Na szalę spadają worki ze srebrnymi rublami, szala opada (brzęk monet)."""
    kam(st, t, I["monety"], CX, 560, 2.0, 0.84)
    izba(st, t, w)
    opad = 0.0
    for n in range(4):
        f = pr(t, 0.15 + 0.25 * n, 0.3)
        y = lerp(120, 650 - (n // 2) * 50, f ** 2)
        if f > 0:
            st.put(J.rek_kz("worek"), 560 + (n % 2) * 140 + (n // 2) * 60, y, P.rekwizyty + 0.004 * n, h=110, anchor=(0.5, 1.0),
                   rot=6 * (n % 2 - 0.5))
            opad += 6 * ease(f)
    st.put(J.rek_kz("stol_niski"), 640, 700 + opad, P.rekwizyty - 0.01, w=560, anchor=(0.5, 0.15))
    koniec(st, w, t, extra=(1.02, 0.98, 0.92))


def brzegi_oddzialy(st, t, w, k=1.0, szamil=True):
    """Dwa oddziały na brzegach rzeki: Rosjanie z lewej (biała flaga rozmów), muridzi z prawej (czarna chorągiew)."""
    for n in range(4):
        jezdziec(st, t, ("oficer_ros", "zolnierz", "oficer_ros2", "zolnierz3")[n], 90 + n * 90, 640 - n * 4, P.most + 0.006 * n, flip=1, h=120,
                 k=ease(pr(t, 0.2 * n, 0.7)) * k, seed=n, galop=0.15)
        key = w.szamil if (n == 0 and szamil) else ("murid", "murid2", "murid3", "murid4")[n]
        jezdziec(st, t, key, 1190 - n * 90, 640 - n * 4, P.most + 0.006 * n, flip=-1, h=120, k=ease(pr(t, 0.2 * n + 0.1, 0.7)) * k,
                 seed=n + 9, galop=0.15)
    st.put(J.rek_kz("choragiew"), 1240, 650, P.most + 0.03, h=230, anchor=(0.04, 1.0), sx=-1, rot=1.5 * math.sin(t * 6))
    st.put(J.rek_kz("flaga_biala"), 40, 650, P.most + 0.03, h=200, anchor=(0.04, 1.0), rot=1.5 * math.sin(t * 6 + 1))


def s_rzeka(st, w, t, T):
    """Kamera dojeżdża do rzeki; z lewej i prawej ustawiają się dwa oddziały; zawieszka „River Michik, March 1855”
    (wzór rysunku: ilustracja wymiany z 1855, Met nr 423472)."""
    kam(st, t, I["rzeka"], CX, lerp(400, 470, ease(t / T)), lerp(1.0, 1.15, ease(t / T)), 0.62)
    miczik(st, t, w)
    brzegi_oddzialy(st, t, w)
    podpis(w, t, "River Michik, March 1855", CX, 40, 0.5, T)
    koniec(st, w, t)


def s_brzegi(st, w, t, T):
    """Dwa szeregi jeźdźców na brzegach, chorągwie — czarna i biała; konie przestępują z nogi na nogę."""
    kam(st, t, I["brzegi"], CX, 500, 1.3, 0.6)
    miczik(st, t, w)
    brzegi_oddzialy(st, t, w)
    koniec(st, w, t)


def s_przeprawa_ksiezne(st, w, t, T):
    """Otwarty wóz z księżnymi, dziećmi i służbą przejeżdża bród w stronę Rosjan (siedzą ZA burtą, burta zasłania je od pasa),
    za nim wozy z workami srebra jadą w drugą stronę, a jeńcy przechodzą pieszo; dziecko macha."""
    kam(st, t, I["przeprawa_ksiezne"], CX, 520, 1.35, 0.66)
    miczik(st, t, w)
    brzegi_oddzialy(st, t, w)
    u = K.uk(st, t)
    x = lerp(900, 380, ease(pr(t, 0, T)))
    u.rzedy["wóz"], u.rzedy["w wozie"] = P.droga + 0.012, P.droga + 0.010
    hw = 120
    u.put("wóz", J.rek_kz("woz"), x, 724, P.droga + 0.012, h=hw, anchor=(0.5, 1.0), sx=-1, rot=1.5 * math.sin(t * 6))
    burta = K.pkt("woz", 310, 112, x, 724, hw)[1]
    # wóz jedzie w lewo (odbity): przód to prawy brzeg arkusza (u = 590), który po odbiciu jest z lewej
    K.zaprzeg(st, t, "wóz", K.pkt("woz", 590, 160, x, 724, hw, sx=-1)[0], 724, P.droga + 0.012, -1, h_kon=110, h_w=96,
              siedzisko=((K.pkt("woz", 550, 112, x, 724, hw, sx=-1)[0], burta + 6), "wóz"))
    for n, key in enumerate(("anna", "warwara", "dziecko_g")):
        hh = 96 if n < 2 else 64
        szk = K.lalka(st, t, f"{key} w wozie", key, x - 10 + n * 44, hh, y=K.y_siedzi(key, hh, burta + 8), rzad="w wozie", flip=-1,
                      siedzi=True, glebia=n * 0.2, przod=140 * _bump(t, 1.2, 0.5) if n == 2 else 4)
        K.siedzi_na(st, t, f"{key} w wozie", szk, "wóz", 10.0)
    xs = lerp(380, 900, ease(pr(t, 0, T)))
    u.put("wóz ze srebrem", J.rek_kz("woz"), xs, 726, P.droga + 0.008, h=100, anchor=(0.5, 1.0), rot=1.5 * math.sin(t * 6 + 1))
    burta2 = K.pkt("woz", 310, 112, xs, 726, 100)[1]
    for m in range(2):
        u.put(f"worek {m + 1}", J.rek_kz("worek"), xs - 30 + m * 46, burta2 + 10, P.droga + 0.0075, h=52, anchor=(0.5, 1.0))
    K.zaprzeg(st, t, "wóz ze srebrem", K.pkt("woz", 590, 160, xs, 726, 100)[0], 726, P.droga + 0.008, 1, h_kon=100, woznica="murid2",
              h_w=90, siedzisko=((K.pkt("woz", 550, 112, xs, 726, 100)[0], burta2 + 6), "wóz ze srebrem"))
    u.rzedy["jeńcy"] = P.droga + 0.006
    for n in range(3):
        K.lalka(st, t, f"jeniec {n + 1}", ("murid3", "murid4", "murid5")[n], xs - 150 - n * 50, 90, y=730, rzad="jeńcy", flip=1, hop=4)
    koniec(st, w, t)


def s_przeprawa_syn(st, w, t, T):
    """Młody oficer w rosyjskim mundurze przejeżdża bród w drugą stronę, ku górom."""
    kam(st, t, I["przeprawa_syn"], lerp(520, 760, t / T), 520, 1.35, 0.66)
    miczik(st, t, w)
    brzegi_oddzialy(st, t, w)
    jezdziec(st, t, "dzamal_oficer", lerp(300, 900, ease(pr(t, 0.2, T - 0.4))), 732, P.droga + 0.01, flip=1, h=150, seed=4, galop=0.4)
    koniec(st, w, t)


def s_syn_brzeg(st, w, t, T):
    """Zbliżenie: młody oficer zatrzymuje konia na środku brodu i patrzy na góry, z których wyjechał jako dziecko; waha się."""
    kam(st, t, I["syn_brzeg"], 640, 560, 2.6, 0.66)
    miczik(st, t, w)
    obejrz = _bump(t, 1.3, 0.35) > 0
    jezdziec(st, t, "dzamal_oficer", 640, 732, P.droga + 0.01, flip=-1 if obejrz else 1, h=150, seed=4, galop=0.0)
    koniec(st, w, t, dim=0.96)


def s_mundur(st, w, t, T):
    """Na brzegu zrywa epolety (dłoń do własnego barku), murid podaje mu złożoną czarną czerkieskę, syn chwyta jej wolny
    koniec i już stoi w czerkiesce (zmiana stroju w kadrze; rzecz przechodzi z dłoni do dłoni w chwili dotyku — 1.28)."""
    kam(st, t, I["mundur"], 760, 470, 1.4, 0.8)
    miczik(st, t, w)
    u = K.uk(st, t)
    zrywa = _bump(t, 0.5, 0.35)
    zmiana = t > 1.25
    podaje = ease(pr(t, 0.4, 0.55))
    murid = K.lalka(st, t, "murid", "murid", 900, 290, flip=-1, przod=(lerp(860, 818, podaje), 560))
    geo = K.w_dloni(st, t, "czerkieska", "czerkieska", murid, 50, rot=0) if t < 1.25 else None
    wolny = geo(160, 60) if geo else (812, 560)  # wolny koniec złożonej czerkieski (arkusz 180 × 120)
    chwyta = ease(pr(t, 0.95, 0.25))
    syn = K.lalka(st, t, "syn", "dzamal_gorski" if zmiana else "dzamal_oficer", 720, 300, flip=1,
                  przod=(lambda s: (lerp(K.U.Uklad.dlon_z_kata(s, 8)[0], s["punkt"](196, 212)[0], zrywa),
                                    lerp(K.U.Uklad.dlon_z_kata(s, 8)[1], s["punkt"](196, 212)[1], zrywa))) if t < 0.95 else
                  (lambda s: K.w_zasiegu(s, (lerp(K.U.Uklad.dlon_z_kata(s, 8)[0], wolny[0], chwyta),
                                             lerp(K.U.Uklad.dlon_z_kata(s, 8)[1], wolny[1], chwyta)))))
    if 0.5 < t < 1.5:  # zerwana epoleta leci w bok
        f = pr(t, 0.5, 1.0)
        st.put(J.tag("", 10), 720 + 160 * f, 420 + 260 * f * f, P.lalki + 0.03, h=14, anchor=(0.5, 0.5), tint=(1.0, 0.8, 0.3),
               rot=400 * f, shadow=None)
    if syn and geo and chwyta >= 1:
        u.dotyka("czerkieska", (*syn["przod"]["dlon"], syn["p"]), "syn chwyta czerkieskę (dłoń na niej)", 6.0)
    koniec(st, w, t)


def s_ojciec_brzeg(st, w, t, T):
    """Zbliżenie: Szamil na drugim brzegu; dłoń puszcza rękojeść kindżału (dłoń z punktu rękojeści opada)."""
    kam(st, t, I["ojciec_brzeg"], 640, STOPY - 300 * 0.75, 2.6, 0.8)
    miczik(st, t, w)
    puszcza = ease(pr(t, 1.2, 0.8))
    K.lalka(st, t, "Szamil", w.szamil, 640, 300, flip=-1,
            przod=(lambda s: (lerp(s["punkt"](156, 336)[0], s["bark_przod"][0] - 4, puszcza),
                              lerp(s["punkt"](156, 336)[1], s["bark_przod"][1] + sum(s["L"]) * 0.95, puszcza))))
    koniec(st, w, t, dim=0.97)


def s_uscisk(st, w, t, T):
    """Muzyka milknie, zostaje szum rzeki; Szamil obejmuje syna: dłonie każdego leżą na plecach drugiego (cel z jego
    szkieletu, kontrola: dłoń na partnerze); kamera bardzo wolno dojeżdża (emocjonalny szczyt, Wytyczne 1.23)."""
    kam(st, t, I["uscisk"], 640, 470, lerp(1.6, 1.9, t / T), 0.8)
    miczik(st, t, w)
    u = K.uk(st, t)
    zbliz = ease(pr(t, 0.2, 1.0))
    xs, xd = lerp(520, 600, zbliz), lerp(780, 690, zbliz)
    f_s, f_d = J.figura(w.szamil), J.figura("dzamal_gorski")
    plecy = lambda key, x, flip, f: (x + (110 - 150) * (300 / f.wys) * flip, STOPY - (f.stopa - 250) * 300 / f.wys)
    cel_s = plecy("dzamal_gorski", xd, -1, f_d)
    cel_d = plecy(w.szamil, xs, 1, f_s)
    od = lambda s: K.U.Uklad.dlon_z_kata(s, 8)
    sz = K.lalka(st, t, "Szamil", w.szamil, xs, 300, flip=1, przod=lambda s: K.w_zasiegu(s, (lerp(od(s)[0], cel_s[0], zbliz),
                                                                                                lerp(od(s)[1], cel_s[1], zbliz))))
    syn = K.lalka(st, t, "syn", "dzamal_gorski", xd, 300, flip=-1, glebia=4,
                  przod=lambda s: K.w_zasiegu(s, (lerp(od(s)[0], cel_d[0], zbliz), lerp(od(s)[1], cel_d[1], zbliz))))
    if sz and syn and zbliz >= 1:
        u.dotyka("syn", (*sz["przod"]["dlon"], sz["p"]), "dłoń Szamila na plecach syna", 8.0)
        u.dotyka("Szamil", (*syn["przod"]["dlon"], syn["p"]), "dłoń syna na plecach ojca", 8.0)
    koniec(st, w, t, dim=0.97)


def s_obcy(st, w, t, T):
    """Syn w czerkiesce siedzi za niskim stolikiem w kamiennej izbie i trzyma rosyjską książkę; za oknem śnieg i góry;
    w myślach (obłok) zjeżdża miniaturka Petersburga."""
    kam(st, t, I["obcy"], 640, 460, 1.3, 0.8)
    izba(st, t, w)
    u = K.uk(st, t)
    u.rzecz("stolik", K.ark("stol_niski"), 690, STOPY + 10, u.p("przod"), (180, 120), 90)
    blat_y = K.pkt("stol_niski", 180, 20, 690, STOPY + 10, 90)[1]
    szk = K.lalka(st, t, "syn", "dzamal_gorski", 600, 290, flip=1, siedzi=True, y=K.y_siedzi("dzamal_gorski", 290, blat_y + 12),
                  przod=(700, blat_y - 70))
    K.w_dloni(st, t, "książka", "ksiazka_ros", szk, 70, rot=0)
    k = ease(pr(t, 1.6, 0.8))
    if k > 0:
        J.hang(st, J.rek("oblok"), 760, 90, P.rekwizyty, k, t, 61, h=200, drop=300)
        J.hang(st, J.iglice(), 760, 150, P.rekwizyty + 0.004, k, t, 62, w=230, drop=300, string=False)
    if szk and szk["k"] >= 1:  # kiedy syn już siedzi (przy budowie dekoracji lalka dopiero się wysuwa — pominięte z powodu)
        u.widac("książka", 0.85, "książka: widać ≥ 85%", oprocz=("rampa", "syn"))
    koniec(st, w, t, extra=(0.98, 0.98, 1.02))


def s_choroba(st, w, t, T):
    """Syn kaszle, siedząc na łóżku (biodro na materacu); przy nim świeca na szafce; Szamil podchodzi i siada obok na brzegu
    łóżka (choroba: zgięcie i kaszel — słownik znaków 1.20)."""
    kam(st, t, I["choroba"], 640, 470, 1.35, 0.8)
    izba(st, t, w, okno_noc=True)
    w.noc = 0.6
    u = K.uk(st, t)
    u.mebel("łóżko", "lozko", 640, 150, rzad="przy_scianie")
    u.mebel("szafka", "szafka", 900, 120, rzad="przy_scianie")
    u.na("świeca", K.ark("swieca"), "szafka", "blat", 0.5, 80)
    sx, sy = u.powierzchnia("szafka", "blat", 0.5)
    _, my = u.powierzchnia("łóżko", "materac", 0.5)
    kaszel = sum(_bump(t, a, 0.2) for a in (0.9, 1.5, 2.6))
    syn = K.lalka(st, t, "syn", "dzamal_gorski", 680, 260, flip=1, siedzi=True, y=K.y_siedzi("dzamal_gorski", 260, my + 4), lean=20 * kaszel,
                  rzad="lalki")
    K.siedzi_na(st, t, "syn", syn, "łóżko", 8.0)
    siada = t > 2.0
    xs = lerp(300, 520, ease(pr(t, 0.8, 1.2)))
    sz = K.lalka(st, t, "Szamil", w.szamil, xs, 300, flip=1, siedzi=siada, y=K.y_siedzi(w.szamil, 300, my + 4) if siada else STOPY)
    if siada:
        K.siedzi_na(st, t, "Szamil", sz, "łóżko", 8.0)
    plomien(st, sx, sy - 80 * 0.9, u.p("przy_scianie") + 0.003, t, h=26)
    st.put(J.glow(), sx, sy - 90, P.lalki + 0.013, w=420, anchor=(0.5, 0.5), mode="add", alpha=0.3, shadow=None, tint=(1.0, 0.8, 0.5))
    koniec(st, w, t, dim=0.9, extra=(1.04, 0.96, 0.88))


def s_swieca(st, w, t, T):
    """Płomień świecy drży i gaśnie; smużka dymu (światło jako dramaturgia, Rytm 7)."""
    kam(st, t, I["swieca"], 860, STOPY - 120, 3.4, 0.82)
    izba(st, t, w, okno_noc=True)
    w.noc = 0.6
    st.put(J.rek_kz("swieca"), 860, STOPY - 60, P.lalki + 0.01, h=80, anchor=(0.5, 1.0))
    gasnie = pr(t, 0.9, 0.25)
    if gasnie < 1:
        plomien(st, 860 + 3 * math.sin(t * 20), STOPY - 136, P.lalki + 0.012, t, h=26 * (1 - gasnie))
        st.put(J.glow(), 860, STOPY - 150, P.lalki + 0.013, w=420, anchor=(0.5, 0.5), mode="add", alpha=0.3 * (1 - gasnie), shadow=None,
               tint=(1.0, 0.8, 0.5))
    dym(st, 860, STOPY - 150, P.lalki + 0.014, t, 1.1, r=60, dl=0.9)
    koniec(st, w, t, dim=lerp(0.9, 0.55, gasnie), extra=(1.04, 0.96, 0.88))


def s_samotny(st, w, t, T):
    """Szamil sam na grani w deszczu z bibuły; kamera odjeżdża; kurtyna zasuwa się w pauzie
    (render: „Act 3 — SIRIDAR · How does a 25-year war end?”)."""
    kam(st, t, I["samotny"], 760, 420, lerp(1.5, 1.05, ease(t / T)), 0.8)
    w.clouds = [1.0, 1.0, 1.0]
    kaukaz(st, t, w, aul=None)
    lalka(st, t, w.szamil, 900, 280, flip=-1, lean=4)
    for n in range(40):  # deszcz: ukośne nitki
        f = (t * 1.6 + n * 0.077) % 1.0
        x = (n * 37) % 1400 - 60 + 120 * f
        st.line([(x, -40 + f * 800), (x + 10, -10 + f * 800)], P.rekwizyty, width=1.2, color=(200, 210, 230), alpha=0.55)
    koniec(st, w, t, dim=0.85, extra=(0.9, 0.94, 1.04))
