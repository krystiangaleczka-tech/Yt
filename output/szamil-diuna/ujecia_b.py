"""Ujęcia aktów III–VI filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (szkic E, 28.11.2026):
Dargo i Tołstoj, syn i księżne, Gunib i Kaługa, słowa i puenta. Funkcja `s_<klucz>(st, w, t, T)` na ujęcie, jak w ujecia_a.py;
wydarzenia na słowach lektora (`sl`), gagi po kwestii (`po_kw`).
"""
import math

from ujecia_a import (CX, CY, I, J, K, MURIDZI, P, STOPY, ZOLNIERZE, Z0, _bump, _off, back, bk, blysk, cien, ciemnosc, clamp,  # noqa: F401
                     dym, ease, ease_out, gabinet, gimry_sc, izba, jaskinia, jezdziec, kam, kaukaz, koniec, koza, ksiezyc, lalka,
                     las_bukowy, lerp, miczik, mur_przod, noise, parawan, pieczatka, plomien, po_kw, podpis, pr, pustynia, robak,
                     sala_balowa, sl, slowo, snieg, teatr_kz, gruzja, kaluga_sc, wnetrze, arrakis_sc, SZABLA, FLAGA, gory_pasmo, rampa)
from scena import MICZIK_SWIATLO, chmury, cykl_dni, niebo_dni, spod, swiatlo, wejscie  # noqa: F401
from scena import (biblioteka_sc, gabinet_cara, gran_wieczor_sc, izba_kz, kaluga_sc2, namiot_sc, polka_sc, pracownia_sc,  # noqa: F401,E402
                   przedgorze_sc, sala_tronowa_sc, sala_tyflis_sc, wedeno_sc)


def pioropusz(st, szk, lean=0.0, p=None):
    """Ogromny pióropusz Woroncowa wpięty w kapelusz (nad czubkiem głowy); zwraca czubek pióropusza."""
    if not szk:
        return None
    hx, hy = szk["punkt"](152, 64)
    h = 190
    rot = lean
    st.put(J.rek_kz("pioropusz"), hx, hy, (szk["p"] if p is None else p) + 0.001, h=h, anchor=(0.5, 1.0), rot=rot, sx=szk["flip"],
           shadow=(4, 6, 8, 0.3))
    ox, oy = _off(0, -h, rot)
    return hx + ox, hy + oy


# ================================================================ akt III: Dargo, suchary, Tołstoj

def woz_z_workami(st, t, u, xw):
    """Wóz z workami sucharów jadący w prawo, z koniem i woźnicą (pochód na Dargo)."""
    u.put("wóz", J.rek_kz("woz"), xw, STOPY + 2, u.p("lalki", -2), h=120, anchor=(0.5, 1.0), sx=1, rot=1.2 * math.sin(t * 6))
    by = K.pkt("woz", 310, 112, xw, STOPY + 2, 120)[1]
    for m in range(2):
        u.put(f"worek {m + 1}", J.rek_kz("worek_suchary"), xw - 40 + m * 60, by + 12, u.p("lalki", -2.2), h=56, anchor=(0.5, 1.0))
    K.zaprzeg(st, t, "wóz", K.pkt("woz", 590, 160, xw, STOPY + 2, 120)[0], STOPY + 2, u.p("lalki", -2), 1, h_kon=110, h_w=96,
              siedzisko=((K.pkt("woz", 550, 112, xw, STOPY + 2, 120)[0], by + 6), "wóz"))


def s_vorontsov(st, w, t, T):
    """Pałac w Tyflisie: hrabia Woroncow w kapeluszu z ogromnym pióropuszem bierze z rąk posłańca rozkaz cara (podpis przy
    nazwisku); na mapie na ścianie zjeżdża strzałka do „DARGO”; gag po kwestii: Woroncow się kłania, pióropusz zahacza
    o żyrandol, żyrandol się kołysze, Woroncow prostuje się dumnie."""
    kam(st, t, I["vorontsov"], 640, 420, 1.12, 0.8)
    sala_tyflis_sc(st, t, w)
    u = K.uk(st, t)
    t_name, t_dargo = sl("vorontsov", "vorontsov"), sl("vorontsov", "dargo")
    gag = po_kw("vorontsov", 0.1)
    uklon = ease(pr(t, gag, 0.5)) * (1 - ease(pr(t, gag + 1.0, 0.5)))
    trafia = gag + 0.4
    kolys = math.exp(-max(0.0, t - trafia) * 1.6) * math.sin((t - trafia) * 7) * 14 if t > trafia else 0.0
    J.hang(st, J.zyrandol(), 640, -20, P.most, 1.0, t, 871, w=300, drop=500, sway=0.6, rot0=kolys, shadow=(6, 9, 10, 0.3))
    J.hang(st, J.mapa_kaukazu(), 1030, 120, P.miasto + 0.01, bk(w, 0.3), t, 1300, w=380, drop=500, strings=(0.1, 0.9))
    strz = ease(pr(t, t_dargo - 0.2, 0.6))
    if strz > 0:
        st.line([(900, 300), (lerp(900, 1080, strz), lerp(300, 230, strz))], P.miasto + 0.012, width=5, color=(190, 30, 30), alpha=0.95)
        podpis(w, t, "DARGO", 1090, 150, t_dargo + 0.2, T)
    bierze = ease(pr(t, 0.6, 0.7))
    pos = K.lalka(st, t, "posłaniec", "zolnierz2", lerp(300, 420, bierze), 300, flip=1, przod=lambda s: 80 * bierze, k=1 - pr(t, 3.2, 0.5))
    if pos and t < 1.4:
        K.w_dloni(st, t, "rozkaz", "kartka_list", pos, 50, rot=0)
    wor = K.lalka(st, t, "Woroncow", "vorontsov", 640, 320, flip=-1, lean=-26 * uklon + (4 if t > gag + 1.4 else 0),
                  przod=lambda s: 70 if 1.2 < t < 3.0 else 10)
    if wor and t >= 1.4:
        K.w_dloni(st, t, "rozkaz w dłoni", "kartka_list", wor, 50, rot=0)
    pioropusz(st, wor, lean=26 * uklon * -1 * -1)
    podpis(w, t, "Count Vorontsov", 640, 210, t_name, 2.8)
    if t > trafia:
        podpis(w, t, "CLINK!", 760, 110, trafia, 1.2)
    koniec(st, w, t, extra=(1.04, 1.0, 0.94))


def s_pochod(st, w, t, T):
    """Bukowy las: kolumna wojska, wozy z workami, armata; zza buków wychylają się muridzi, dymki strzałów, chowają się;
    gag po kwestii: żołnierz puka w pień, z dziupli murid puka go w czapkę i znika; żołnierz patrzy na kolegów („?!”)."""
    jedzie = t * 26
    kam(st, t, I["pochod"], 640, 410, 1.05, 0.72)
    las_bukowy(st, t, w, x0=-jedzie)
    u = K.uk(st, t)
    t_fired = sl("pochod", "fired")
    gag = po_kw("pochod", 0.0)
    for n in range(5):
        x = 140 + n * 170 + (0 if t < gag else 0)
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], x, 230, glebia=(n % 2), flip=1, hop=5 * (t < gag))
    xw = 1040
    if K.wjechal():
        woz_z_workami(st, t, u, xw)
    u.rzedy["za_drzewami"] = P.wzgorza - 0.006
    for n, (x, s_) in enumerate(((330, t_fired), (690, t_fired + 0.5), (1000, t_fired + 1.0))):
        wych = ease(pr(t, s_ - 0.4, 0.3)) * (1 - ease(pr(t, s_ + 0.9, 0.3)))
        if wych > 0:
            K.lalka(st, t, f"murid za bukiem {n + 1}", MURIDZI[n], x + 40 * wych, 200, y=STOPY - 30, rzad="za_drzewami", flip=-1, wejscie=False,
                    przod=90)
            blysk(st, x - 20, STOPY - 160, P.wzgorza, t, s_ + 0.1, r=140)
            dym(st, x - 30, STOPY - 170, P.wzgorza + 0.01, t, s_ + 0.1, r=100, seed=n)
    # gag: pień buka przed żołnierzem 2 z dziuplą (wycinek pnia blisko), żołnierz puka, z dziupli wychyla się murid
    pien_x = 440
    st.put(J.rek_kz("buk"), pien_x, STOPY + 30, P.lalki + 0.02, h=1100, anchor=(0.5, 1.0), shadow=(6, 8, 10, 0.35), tint=(0.78, 0.76, 0.72))
    st.put(Z0.black(), pien_x + 6, STOPY - 170, P.lalki + 0.021, w=34, h=48, anchor=(0.5, 0.5), shadow=None, alpha=0.9)
    puk = gag + 0.2
    if t > puk:
        wych = ease(pr(t, puk + 0.6, 0.25)) * (1 - ease(pr(t, puk + 1.3, 0.25)))
        if wych > 0:
            st.put(J.figura("murid5").kapelusz[0], pien_x + 4, STOPY - 196 + 20 * (1 - wych), P.lalki + 0.0215, h=46 * wych, anchor=(0.5, 0.5))
        podpis(w, t, "KNOCK KNOCK", pien_x, 230, puk, 1.0)
        podpis(w, t, "?!", 310, 260, puk + 1.5, 1.6)
    koniec(st, w, t)


def s_dargo(st, w, t, T):
    """Kolumna wchodzi do Dargo: domy płoną, dym; żołnierze zaglądają do domów — puste; na „fire” płomienie rosną; gag po
    kwestii: z dymu wychodzi koza, jedyna mieszkanka, staje przed Woroncowem i beczy „MEH” (koza: powtórka)."""
    kam(st, t, I["dargo"], lerp(600, 700, ease(t / T)), 410, lerp(1.0, 1.12, ease(t / T)), 0.75)
    las_bukowy(st, t, w, droga=False, kul=False)
    u = K.uk(st, t)
    t_empty, t_fire = sl("dargo", "empty"), sl("dargo", "fire")
    Z0.rise(st, J.aul(0), 820, 690, P.droga + 0.03, bk(w, 0.4, 0.8), t, 1310, w=820, wob=0.0, lift=420, anchor=(0.5, 1.0), tint=(0.7, 0.62, 0.56))
    rosnie = 1 + 1.2 * ease(pr(t, t_fire, 1.4))
    for n in range(7):
        if bk(w, 0.8) < 1:
            break
        plomien(st, 520 + n * 90, 560 + (n % 3) * 30, P.droga + 0.032, t, h=(50 + 10 * (n % 2)) * rosnie, seed=n * 5)
        dym(st, 540 + n * 85, 470, P.droga + 0.034, t, (t + n * 0.31) % 2.2 + int(t / 2.2) * 2.2 - 2.2, r=160, dl=2.2, seed=n)
    for n in range(4):
        x = lerp(-120 + n * 140, 340 + n * 140, ease(pr(t, 0.3, 2.6)))
        zaglada = t > t_empty - 0.4 and n < 2
        K.zolnierz(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], x, 240, glebia=(n % 2), flip=1, hop=5 * (t < 2.9))
        if zaglada:
            podpis(w, t, "EMPTY", x, 300, t_empty + 0.3 * n, 1.8)
    gag = po_kw("dargo", 0.0)
    kz = ease(pr(t, gag, 0.9))
    meh = t > gag + 1.0
    koza(st, t, "koza", lerp(1220, 900, kz), h=110, flip=-1, meh=meh, k=1.0 if t > gag else 0.0)
    K.lalka(st, t, "Woroncow", "vorontsov", 760, 300, flip=1, k=ease(pr(t, 1.2, 0.6)), lean=-8 * (t > gag + 1.0))
    if meh:
        podpis(w, t, "MEH", 900, 330, gag + 1.0, 1.8)
    koniec(st, w, t, extra=(1.06, 0.96, 0.88))


def s_zwyciestwo(st, w, t, T):
    """Namiot Woroncowa: pisze raport, pieczątka uderza „DARGO TAKEN! VICTORY!” (powtórka gagu); na „eat” adiutant przynosi
    pusty worek i odwraca go do góry dnem — wypada jeden suchar; Woroncow patrzy na suchar."""
    kam(st, t, I["zwyciestwo"], 640, 440, 1.25, 0.8)
    namiot_sc(st, t, w)
    u = K.uk(st, t)
    u.mebel("stół", "stol_polowy", 560, 180, rzad="przod")
    _, blat = u.powierzchnia("stół", "blat", 0.5)
    t_stamp, t_eat = sl("zwyciestwo", "reported"), sl("zwyciestwo", "eat")
    wor = K.lalka(st, t, "Woroncow", "vorontsov", 420, 320, flip=1, przod=lambda s: 40 + 100 * _bump(t, t_stamp + 0.9, 0.5),
                  lean=6 * ease(pr(t, t_eat + 0.6, 0.4)))
    pioropusz(st, wor)
    pieczatka(st, t, t_stamp + 1.0, "DARGO TAKEN! VICTORY!", x=560, y=blat - 30, p=u.p("przod", 0.6), h_rap=120)
    przych = ease(pr(t, t_eat - 1.0, 0.8))
    odwraca = ease(pr(t, t_eat + 0.1, 0.4))
    ad = K.lalka(st, t, "adiutant", "oficer_ros3", lerp(1120, 820, przych), 300, flip=-1, przod=lambda s: 80 + 70 * odwraca)
    if ad:
        hx, hy = ad["przod"]["dlon"]
        st.put(J.rek_kz("worek"), hx, hy, ad["p"] + 0.002, h=90, anchor=(0.5, 0.2), rot=180 * odwraca, sy=0.7)
        f = pr(t, t_eat + 0.5, 0.5)
        if f > 0:
            st.put(J.rek_kz("suchar"), hx, lerp(hy + 30, STOPY - 6, f ** 2), P.lalki + 0.03, h=28, anchor=(0.5, 1.0), rot=240 * f if f < 1 else 0)
    if t > po_kw("zwyciestwo", 0.0):
        podpis(w, t, "...", 420, 210, po_kw("zwyciestwo", 0.0), 2.0)
    koniec(st, w, t, extra=(1.04, 0.98, 0.9))


def s_suchary(st, w, t, T):
    """Bukowy las: kolumna z wozami wraca po zaopatrzenie (worki „SUKHARI”); las gęstnieje, robi się ciemniej; na „waiting”
    w koronach buków pojawiają się oczy i lufy — bez gagu."""
    kam(st, t, I["suchary"], 640, 410, lerp(1.0, 1.12, ease(t / T)), 0.72)
    ciem = ease(pr(t, 2.0, 4.0))
    las_bukowy(st, t, w, ciemno=0.5 * ciem, x0=t * 30)
    u = K.uk(st, t)
    for n in range(2 if K.wjechal() else 0):
        xw = lerp(1300 + n * 420, 300 + n * 420, pr(t, 0, T))
        u.put(f"wóz {n + 1}", J.rek_kz("woz"), xw, STOPY + 2, u.p("lalki", -2), h=120, anchor=(0.5, 1.0), sx=-1, rot=1.2 * math.sin(t * 6 + n))
        by = K.pkt("woz", 310, 112, xw, STOPY + 2, 120)[1]
        for m in range(2):
            u.put(f"worek {n + 1}.{m + 1}", J.rek_kz("worek_suchary"), xw - 40 + m * 60, by + 12, u.p("lalki", -2.2), h=56, anchor=(0.5, 1.0))
        K.zaprzeg(st, t, f"wóz {n + 1}", K.pkt("woz", 590, 160, xw, STOPY + 2, 120, sx=-1)[0], STOPY + 2, u.p("lalki", -2), -1, h_kon=110,
                  h_w=96, woznica=("zolnierz4", "zolnierz6")[n],
                  siedzisko=((K.pkt("woz", 550, 112, xw, STOPY + 2, 120, sx=-1)[0], by + 6), f"wóz {n + 1}"))
        K.zolnierz(st, t, f"eskorta {n + 1}", ZOLNIERZE[n + 1], xw + 220, 230, flip=-1, hop=5)
    t_wait = sl("suchary", "waiting")
    for n in range(6):  # oczy i lufy w koronach buków
        k = ease(pr(t, t_wait + 0.2 * n, 0.4))
        if k > 0:
            x, y = 160 + n * 200, 160 + (n % 3) * 50
            for d in (-9, 9):
                st.put(Z0.prop("kulka"), x + d, y, P.wzgorza + 0.01, h=10 * k, anchor=(0.5, 0.5), tint=(1.0, 1.0, 0.85), shadow=None)
            st.line([(x + 20, y + 20), (x + 20 + 40 * k, y + 30)], P.wzgorza + 0.011, width=4, color=(40, 40, 44), alpha=k)
    koniec(st, w, t, dim=lerp(1.0, 0.82, ciem))


def s_zasadzka(st, w, t, T):
    """Teatr cieni: buki padają w poprzek drogi, wozy stają; błyski strzałów, sylwetki padają za parawan; cisza, worek
    z sucharami leży na drodze; na „Biscuit” zjeżdża tabliczka „THE BISCUIT EXPEDITION” — bez dźwięku gagu (powaga)."""
    y0, p0, ph = parawan(st, t, w)
    kam(st, t, I["zasadzka"], 640, y0 - ph * 0.5 - 20, 1.4, p0)
    t_cut, t_bisc = sl("zasadzka", "cut"), sl("zasadzka", "biscuit")
    for n, x in enumerate((300, 960)):
        pad = ease(pr(t, 0.6 + 0.5 * n, 0.6))
        st.put(J.rek_kz("buk"), x, y0 - 40, p0 + 0.003, h=330, anchor=(0.5, 1.0), rot=(-78 if n else 78) * pad, tint=(0.08, 0.06, 0.05),
               blur=1.6, shadow=None)
    st.put(J.rek_kz("woz"), 640, y0 - 40, p0 + 0.002, h=110, anchor=(0.5, 1.0), tint=(0.08, 0.06, 0.05), blur=1.6, shadow=None)
    for n in range(4):
        pad = pr(t, t_cut + 0.3 * n, 0.6)
        if pad < 1:
            cien(st, t, ZOLNIERZE[n], 460 + n * 110, 200, y0 - 40, p0 + 0.004, flip=1 if n % 2 else -1, sink=pad)
        blysk(st, 200 + n * 300, y0 - 260, p0 + 0.006, t, t_cut - 0.4 + 0.3 * n, r=180)
    if t > t_cut + 1.6:
        st.put(J.rek_kz("worek_suchary"), 640, y0 - 40, p0 + 0.005, h=70, anchor=(0.5, 1.0), tint=(0.08, 0.06, 0.05), blur=1.4, shadow=None)
    J.hang(st, J.tag("THE BISCUIT EXPEDITION", 44), CX, y0 - ph - 10, P.rekwizyty, pr(t, t_bisc, 0.9), t, 1330, h=70, drop=360, strings=(0.2, 0.8),
           shadow=(5, 8, 8, 0.4))
    koniec(st, w, t)


def s_tolstoj(st, w, t, T):
    """Droga między fortami: młody ochotnik w czapce kadeta jedzie konno i pisze w zeszycie (podpis „Leo Tolstoy, 24”); na
    „captured” zza wzgórza wypadają jeźdźcy w czerni; Tołstoj i jego czeczeński przyjaciel (Sado) galopują w prawo; gag:
    z zeszytu wylatują kartki i lecą za nim jak ogon, jedna przykleja się do twarzy goniącego. Kurtyna w pauzie."""
    t_name, t_capt, t_stories = sl("tolstoj", "leo"), sl("tolstoj", "captured"), sl("tolstoj", "stories")
    galop = pr(t, t_capt, 0.3)
    kam(st, t, I["tolstoj"], 640 + 80 * ease(galop), 410, 1.08, 0.75)
    przedgorze_sc(st, t, w)
    u = K.uk(st, t)
    x_t = lerp(300, 560, ease(pr(t, 0, t_capt))) + 900 * ease_out(pr(t, t_capt, 4.0))
    szk = jezdziec(st, t, "tolstoj", x_t, STOPY, P.lalki + 0.01, flip=1, h=230, galop=0.3 + 0.7 * galop, seed=7,
                   rece=(60 if t < t_capt else 20, 40))
    if szk and t < t_capt:
        K.w_dloni(st, t, "zeszyt", "zeszyt", szk, 46, rot=0)
    jezdziec(st, t, "sado", x_t - 170 + 40 * galop, STOPY + 4, P.lalki + 0.005, flip=1, h=225, galop=0.3 + 0.7 * galop, seed=8)
    podpis(w, t, "Leo Tolstoy, 24", 500, 250, t_name, 2.8)
    for n in range(3):  # pościg
        k = ease(pr(t, t_capt + 0.2 * n, 0.4))
        xg = lerp(-200, 900, ease_out(pr(t, t_capt + 0.2 * n, 4.6))) - n * 170
        if k > 0:
            jezdziec(st, t, ("murid2", "murid5", "murid4")[n], xg, STOPY + 2 * n, P.lalki - 0.004 * n, flip=1, h=220, galop=1.0, seed=20 + n,
                     k=k, trzyma=SZABLA(110, -60))
    gag = po_kw("tolstoj", -2.0)
    for n in range(8):  # kartki z zeszytu lecą za nim
        f = pr(t, gag + 0.15 * n, 1.6)
        if 0 < f < 1 or (n == 3 and f >= 1):
            kx = x_t - 60 - 300 * f
            ky = STOPY - 230 - 80 * math.sin(math.pi * f) + 30 * math.sin(t * 6 + n)
            if n == 3 and f >= 1:  # jedna kartka przykleja się do twarzy pierwszego goniącego
                xg = lerp(-200, 900, ease_out(pr(t, t_capt, 4.6)))
                kx, ky = xg + 18, STOPY - 300
            st.put(J.rek_kz("kartka"), kx, ky, P.rekwizyty, h=40, anchor=(0.5, 0.5), rot=300 * f if f < 1 else 8)
    if t > t_stories:
        podpis(w, t, "MMPH!", lerp(-200, 900, ease_out(pr(t, t_capt, 4.6))) + 20, 220, gag + 1.8, 1.6)
    koniec(st, w, t)


# ================================================================ akt IV: syn i księżne

def s_kadet(st, w, t, T):
    """Sala balowa: mały kadet salutuje, chowa się w dół, wysuwa się wyższy kadet, potem wysoki oficer z wąsikiem (ta sama
    twarz, zmiana wieku w kadrze — 1.15); podpis przy imieniu; za nim pary wirują, żyrandol migocze; oficer kłania się damie
    i rusza do tańca."""
    kam(st, t, I["kadet"], lerp(640, 700, ease(t / T)), 430, lerp(1.25, 1.1, ease(t / T)), 0.8)
    sala_balowa(st, t, w)
    u = K.uk(st, t)
    t_name, t_off, t_mount = sl("kadet", "jamal"), sl("kadet", "officer"), sl("kadet", "mountains")
    K.lalka(st, t, "mały kadet", "dzamal_kadet", 640, 190, flip=1, sink=ease(pr(t, t_name - 0.3, 0.5)),
            przod=lambda s: s["punkt"](186, 96) if t > 0.6 else 6)
    K.lalka(st, t, "średni kadet", "dzamal_sredni", 640, 250, flip=1, k=ease(pr(t, t_name, 0.5)), sink=ease(pr(t, t_off - 0.2, 0.5)))
    of = K.lalka(st, t, "Dżamaluddin", "dzamal_oficer", 640, 320, flip=1, k=ease(pr(t, t_off, 0.6)), lean=-18 * _bump(t, po_kw("kadet", -0.8), 0.5),
                 przod=lambda s: 20 * _bump(t, po_kw("kadet", -0.8), 0.5) + 70 * ease(pr(t, po_kw("kadet", 0.0), 0.4)))
    podpis(w, t, "Jamal al-Din", 640, 230, t_name, 3.0)
    u.rzedy["pary"] = P.lalki - 0.03
    tance = ease(pr(t, t_mount - 0.6, 0.8))
    for n in range(3):
        a = t * 2.2 + n * 2.1
        x = 300 + n * 340 + 60 * math.cos(a)
        prawo = math.sin(a) > 0
        reka = (x + 20, STOPY - 30 - 230 * 0.55)
        if tance > 0:
            d = K.lalka(st, t, f"dama {n + 1}", ("dama", "dama2", "dama3")[n], x, 230, y=STOPY - 30, rzad="pary", flip=1 if prawo else -1,
                        przod=lambda s: K.w_zasiegu(s, reka), k=tance, wejscie=False)  # przy wejściu pary ręka nie sięga (28.11)
            o = K.lalka(st, t, f"oficer {n + 1}", ("oficer_ros", "oficer_ros2", "oficer_ros3")[n], x + 40, 240, y=STOPY - 30, rzad="pary",
                        flip=-1 if prawo else 1, przod=lambda s: K.w_zasiegu(s, reka), k=tance, wejscie=False)
            if d and o and tance >= 1:
                u.kontakt((*d["przod"]["dlon"], d["p"]), (*o["przod"]["dlon"], o["p"]), f"para {n + 1}: dłonie razem", 4.0)
    if t > po_kw("kadet", -0.8):  # dama, której się kłania
        K.lalka(st, t, "dama do tańca", "gap1", 820, 300, flip=-1, k=ease(pr(t, po_kw("kadet", -1.2), 0.4)), wejscie=False,
                przod=lambda s: 50 * ease(pr(t, po_kw("kadet", 0.0), 0.4)))
    st.put(J.glow(), CX, 120, P.most, w=600, anchor=(0.5, 0.5), mode="add", alpha=0.18 + 0.05 * math.sin(t * 9), shadow=None)
    koniec(st, w, t, extra=(1.04, 1.0, 0.92))


def s_tsinandali(st, w, t, T):
    """Dwór wśród winnic, zawieszka „Tsinandali, Georgia, 1854”; na grzbiecie za murem wyrastają jeźdźcy, podpis „Shamil's
    second son”; jeźdźcy przeskakują mur winnicy, liście fruwają; na balkonie dwie damy w czepcach odskakują („!!”)."""
    t_son, t_raid = sl("tsinandali", "second"), sl("tsinandali", "raided")
    skok = pr(t, t_raid + 0.3, 1.4)
    kam(st, t, I["tsinandali"], lerp(640, 720, ease(t / T)), 400, lerp(1.0, 1.12, ease(t / T)), 0.7, shake=3 * _bump(t, t_raid + 1.0, 0.2))
    gruzja(st, t, w)
    mur_przod(st, t, w)
    u = K.uk(st, t)
    u.rzedy["balkon"] = P.miasto + 0.012
    odskok = ease(pr(t, t_raid + 0.6, 0.3))
    for n, key in enumerate(("anna", "warwara")):
        K.lalka(st, t, f"{key} na balkonie", key, 780 + n * 60 + 20 * odskok * (1 if n else -1), 92, y=505, rzad="balkon", flip=-1,
                lean=-8 * odskok, przod=150 * odskok)
    if odskok > 0:
        podpis(w, t, "!!", 810, 330, t_raid + 0.6, 2.0)
    for n in range(4):
        k = ease(pr(t, t_son - 1.0 + 0.2 * n, 0.6))
        if skok <= 0:
            jezdziec(st, t, ("ghazi", "murid", "murid2", "murid3")[n], 200 + n * 120, 600, P.most + 0.01, flip=1, h=110, k=k, seed=n, galop=0.3)
        else:
            f = clamp(skok - 0.12 * n, 0, 1)
            x = lerp(200 + n * 120, 700 + n * 150, f)
            y = lerp(600, STOPY, f) - 160 * math.sin(math.pi * clamp(f * 1.5)) * (f < 0.66)
            jezdziec(st, t, ("ghazi", "murid", "murid2", "murid3")[n], x, y, P.lalki + 0.02 * n, flip=1, h=lerp(110, 200, f), seed=n * 2,
                     trzyma=SZABLA(110, -60) if f > 0.3 else None)
    if skok > 0:
        for n in range(12):
            f = (t * 1.3 + n * 0.17) % 1.0
            st.put(Z0.prop("kulka"), 300 + n * 70 + 60 * f, 520 - 200 * f + 260 * f * f, P.rekwizyty, h=14, anchor=(0.5, 0.5),
                   tint=(0.4, 0.7, 0.3), shadow=None, rot=300 * f)
    podpis(w, t, "Tsinandali, Georgia, 1854", 420, 40, 0.5, T)
    podpis(w, t, "Shamil's second son", 300, 330, t_son, 2.6)
    koniec(st, w, t)


def s_ksiezne(st, w, t, T):
    """Górska droga: księżne w czepcach na koniach za jeźdźcami (podpisy przy imionach), dzieci przed nimi, guwernantka
    na ostatnim koniu trzyma kapelusz. Każdy siedzący ma kontrolę siodła (uklad_kz.jezdziec)."""
    kam(st, t, I["ksiezne"], lerp(520, 760, t / T), 420, 1.1, 0.8)
    polka_sc(st, t, w)
    t_anna, t_var, t_gov = sl("ksiezne", "anna"), sl("ksiezne", "varvara"), sl("ksiezne", "governess")
    grupy = [("ghazi", "anna", "dziecko_g"), ("murid", "warwara", "dziecko_g2"), ("murid2", "guwernantka", None)]
    for n, (jezdzc, pani, dziecko) in enumerate(grupy):
        x = lerp(-120 - n * 330, 1100 - n * 330, pr(t, 0, T))
        szk = jezdziec(st, t, jezdzc, x, STOPY - n * 4, P.lalki + 0.006 * (2 - n), flip=1, h=200, seed=n * 5, galop=0.6, pasazer=pani,
                       dziecko=dziecko)
    podpis(w, t, "Princess Anna Chavchavadze", 360, 250, t_anna, 2.0)
    podpis(w, t, "Princess Varvara Orbeliani", 820, 250, t_var, 2.4)
    podpis(w, t, "the governess", lerp(-120 - 660, 1100 - 660, t_gov / T) + 60, 300, t_gov, 2.2)
    koniec(st, w, t)


OKNO_WEDENO = (300, 150, 520, 330)  # otwór okna w arkuszu ściany 900 × 560 (zestaw_kz.rek_kz("sciana_okno"))


def s_wedeno(st, w, t, T):
    """Wedeno: kamienny dom, w oknie księżne (widać je tylko przez okno, 1.1), przed domem wartownik; zawieszka „Vedeno”; na
    „eight months” nad domem przesuwają się księżyc i słońce, śnieg pada i topnieje; na „governess” w oknie guwernantka pisze
    w zeszycie i zerka na wartownika."""
    kam(st, t, I["wedeno"], lerp(640, 700, ease(t / T)), 420, lerp(1.0, 1.18, ease(t / T)), 0.75)
    t_eight, t_gov = sl("wedeno", "eight"), sl("wedeno", "governess")
    mies = pr(t, t_eight, 3.6)
    ciala, noc = cykl_dni(t, t_eight, 3.6, cykle=3)  # miesiące mijają: słońce i księżyc na nitkach po kolei (ujęcie 24, 28.11)
    wedeno_sc(st, t, w, cialo=False)
    niebo_dni(st, t, w, ciala, noc, gwiazdy_seed=13)
    if 0 < mies < 1:
        snieg(st, t, math.sin(math.pi * mies), seed=12)
    u = K.uk(st, t)
    sw, sx0, sy1 = 620, 700, STOPY
    sk = sw / 900
    u.put("ściana domu", J.rek_kz("sciana_okno"), sx0, sy1, u.p("sciana_domu"), w=sw, anchor=(0.5, 1.0))
    x0, y0 = sx0 + (OKNO_WEDENO[0] - 450) * sk, sy1 - (560 - OKNO_WEDENO[1]) * sk
    x1, y1 = sx0 + (OKNO_WEDENO[2] - 450) * sk, sy1 - (560 - OKNO_WEDENO[3]) * sk
    guw = t > t_gov - 0.4
    obsada = (("anna", -50, 1), ("warwara", 10, -1)) + ((("guwernantka", 64, -1),) if guw else ())
    for n, (key, dx, fl) in enumerate(obsada):
        szk = K.lalka(st, t, key, key, sx0 + dx, 190, y=y1 + 150, rzad="dom", flip=fl, glebia=n,
                      przod=(lambda s: (s["bark_przod"][0] - 30, s["bark_przod"][1] + 40)) if key == "guwernantka" else 4)
        if key == "guwernantka" and szk:
            K.w_dloni(st, t, "zeszyt guwernantki", "zeszyt", szk, 30, rot=0)
        u.w_otworze(key, (x0 - 2, y0 - 2, x1 + 2, y1 + 2, u.p("sciana_domu")), f"{key}: widać tylko przez okno")
    K.zolnierz(st, t, "strażnik", "murid2", 420, 290, flip=lerp(1, -1, _bump(t, po_kw("wedeno", 0.2), 0.6)))
    podpis(w, t, "Vedeno", 380, 40, 0.5, T)
    koniec(st, w, t, dim=1.0 - 0.45 * noc)


def s_cena(st, w, t, T):
    """Izba: Szamil przy niskim stoliku pisze list gęsim piórem (stalówka na kartce, 1.28); na „padishah” nad listem PADISHAH;
    na „son” obok rysunek chłopca; na „million” wielka liczba „1,000,000”; gag na „forty thousand”: cyfry odpadają po kolei
    i spadają z brzękiem, zjeżdża „40,000”; Szamil gładzi brodę."""
    kam(st, t, I["cena"], 640, 470, 1.35, 0.8)
    izba_kz(st, t, w, 0, okno_x=1040)
    u = K.uk(st, t)
    t_pad, t_son, t_mil, t_forty = sl("cena", "padishah"), sl("cena", "son"), sl("cena", "million"), sl("cena", "forty")
    u.rzecz("stolik", K.ark("stol_niski"), 560, STOPY + 10, u.p("przod"), (180, 120), 100)
    blat_y = K.pkt("stol_niski", 180, 20, 560, STOPY + 10, 100)[1]
    u.rzecz("list", K.ark("kartka_list"), 600, blat_y, u.p("przod", 0.3), (110, 160), 60, rot=-4)
    pisze = 0.6 < t < t_mil
    nib = (lerp(572, 608, ((t - 0.6) * 0.8) % 1.0), blat_y - 12 + 4 * math.sin(t * 9)) if pisze else (590, blat_y - 30)
    hp, rot = 22, -112
    kk = hp / 70
    ox, oy = _off((0 - 170) * kk, (42 - 30) * kk, rot)
    gladzi = t > t_forty + 1.4
    szk = K.lalka(st, t, "Szamil", w.szamil, 516, 300, flip=1, siedzi=True, nogi=STOPY, y=K.y_siedzi(w.szamil, 300, blat_y + 14),
                  przod=(lambda s: s["punkt"](176, 196)) if gladzi else (lambda s: K.w_zasiegu(s, (nib[0] - ox, nib[1] - oy), f=1.0)))
    if not gladzi:
        geo = K.w_dloni(st, t, "pióro", "pioro", szk, hp, rot=rot)
        if geo and pisze and wejscie(1.0) >= 1:  # w chwili wejścia lalki (wysuwa się zza rampy) pióro jeszcze nie pisze
            u.dotyka("list", (*geo(0, 42), u.p("przod", 0.3)), "stalówka na kartce", 6.0)
    slowo(st, t, "PADISHAH", 560, 60, pr(t, t_pad, 0.8), seed=20, h=66)
    if t > t_son:  # rysunek chłopca na kartce obok, zjeżdża na nitce
        J.hang(st, J.rek_kz("kartka_list"), 250, 250, P.rekwizyty, pr(t, t_son, 0.7), t, 1340, h=150, drop=300)
        K.lalka(st, t, "rysunek chłopca", "dzamal_maly", 250, 90, y=390 - 300 * (1 - back(pr(t, t_son, 0.7), 1.1)), rzad="rekwizyty",
                flip=1, wejscie=False, shadow=None)
    cyfry = list("1,000,000")
    x0 = 540 - 32 * len(cyfry) / 2
    if t > t_mil:
        k = pr(t, t_mil, 0.6)
        for n, c in enumerate(cyfry):
            spad = pr(t, t_forty + 0.12 * n, 0.5)
            if spad < 1:
                st.put(J.cyfra(c, 70), x0 + n * 32, 330 + 400 * spad ** 2 - 320 * (1 - back(k, 1.1)), P.rekwizyty + 0.01, h=60,
                       anchor=(0.5, 0.5), rot=160 * spad * (1 if n % 2 else -1), shadow=(3, 4, 4, 0.35))
    k40 = pr(t, t_forty + 1.2, 0.7)
    if k40 > 0:
        J.hang(st, J.cyfra("40,000", 80), 540, 290, P.rekwizyty + 0.012, k40, t, 1341, h=80, drop=320, shadow=(4, 6, 6, 0.35))
    koniec(st, w, t, extra=(1.02, 0.98, 0.92))


def brzegi_oddzialy(st, t, w, k=1.0, szamil=True, srebro=0.0, kadr=(-999, 9999)):
    """Dwa oddziały na brzegach rzeki: Rosjanie z lewej (biała flaga rozmów), muridzi z prawej (czarna chorągiew). kadr — zakres
    x, w którym jeźdźcy są w kadrze przy zbliżonej kamerze (jeździec przez całe ujęcie poza kadrem to kontrola, której nie da się
    sprawdzić — kontrola układu 28.11)."""
    for n in range(4):
        x = 90 + n * 90
        if kadr[0] <= x <= kadr[1]:
            jezdziec(st, t, ("oficer_ros", "zolnierz", "oficer_ros2", "zolnierz3")[n], x, 640 - n * 4, P.most + 0.006 * n, flip=1, h=120,
                     k=ease(pr(t, 0.2 * n, 0.7)) * k, seed=n, galop=0.15)
        key = w.szamil if (n == 0 and szamil) else ("murid", "murid2", "murid3", "murid4")[n]
        x = 1190 - n * 90
        if kadr[0] <= x <= kadr[1]:
            jezdziec(st, t, key, x, 640 - n * 4, P.most + 0.006 * n, flip=-1, h=120, k=ease(pr(t, 0.2 * n + 0.1, 0.7)) * k,
                     seed=n + 9, galop=0.15)
    st.put(J.rek_kz("choragiew"), 1240, 650, P.most + 0.03, h=230, anchor=(0.04, 1.0), sx=-1, rot=1.5 * math.sin(t * 6))
    st.put(J.rek_kz("flaga_biala"), 40, 650, P.most + 0.03, h=200, anchor=(0.04, 1.0), rot=1.5 * math.sin(t * 6 + 1))


def woz_srebra(st, t, u, xs, y=726, p=None):
    p = P.droga + 0.008 if p is None else p
    u.put("wóz ze srebrem", J.rek_kz("woz"), xs, y, p, h=100, anchor=(0.5, 1.0), rot=1.5 * math.sin(t * 6 + 1))
    burta2 = K.pkt("woz", 310, 112, xs, y, 100)[1]
    for m in range(2):
        u.put(f"worek {m + 1}", J.rek_kz("worek"), xs - 30 + m * 46, burta2 + 10, p - 0.0005, h=52, anchor=(0.5, 1.0))
    K.zaprzeg(st, t, "wóz ze srebrem", K.pkt("woz", 590, 160, xs, y, 100)[0], y, p, 1, h_kon=100, woznica="murid2",
              h_w=90, siedzisko=((K.pkt("woz", 550, 112, xs, y, 100)[0], burta2 + 6), "wóz ze srebrem"))


def s_rzeka(st, w, t, T):
    """Rzeka Miczik: na brzegach ustawiają się dwa oddziały, zawieszka „River Michik, March 1855”; chorągwie; konie przestępują
    z nogi na nogę; z lewej wjeżdża wóz z workami srebra."""
    kam(st, t, I["rzeka"], CX, lerp(400, 470, ease(t / T)), lerp(1.0, 1.15, ease(t / T)), 0.62)
    miczik(st, t, w, swiatlo=MICZIK_SWIATLO['rzeka'])
    brzegi_oddzialy(st, t, w)
    u = K.uk(st, t)
    if K.wjechal():
        woz_srebra(st, t, u, lerp(-200, 220, ease(pr(t, sl("rzeka", "exchange") - 0.4, 2.0))), y=650, p=P.most + 0.03)
    podpis(w, t, "River Michik, March 1855", CX, 40, sl("rzeka", "march"), T)
    koniec(st, w, t)


def s_przeprawa(st, w, t, T):
    """Wóz z księżnymi, dziećmi i guwernantką przejeżdża bród w lewo (siedzą za burtą); na „silver” wóz z workami jedzie w prawo;
    jeńcy przechodzą pieszo; dziecko na wozie macha; koń strząsa wodę z grzywy."""
    kam(st, t, I["przeprawa"], CX, 520, 1.35, 0.66)
    miczik(st, t, w, swiatlo=MICZIK_SWIATLO['przeprawa'])
    brzegi_oddzialy(st, t, w, kadr=(170, 1110))
    u = K.uk(st, t)
    t_silver = sl("przeprawa", "silver")
    x = lerp(900, 380, ease(pr(t, 0.4, T - 0.8)))
    u.rzedy["wóz"], u.rzedy["w wozie"] = P.droga + 0.012, P.droga + 0.010
    hw = 120
    u.put("wóz", J.rek_kz("woz"), x, 724, P.droga + 0.012, h=hw, anchor=(0.5, 1.0), sx=-1, rot=1.5 * math.sin(t * 6))
    burta = K.pkt("woz", 310, 112, x, 724, hw)[1]
    K.zaprzeg(st, t, "wóz", K.pkt("woz", 590, 160, x, 724, hw, sx=-1)[0], 724, P.droga + 0.012, -1, h_kon=110, h_w=96,
              siedzisko=((K.pkt("woz", 550, 112, x, 724, hw, sx=-1)[0], burta + 6), "wóz"))
    for n, key in enumerate(("anna", "warwara", "guwernantka", "dziecko_g")):
        hh = 96 if n < 3 else 64
        szk = K.lalka(st, t, f"{key} w wozie", key, x - 20 + n * 38, hh, y=K.y_siedzi(key, hh, burta + 8), rzad="w wozie", flip=-1,
                      siedzi=True, glebia=n * 0.2, przod=140 * (_bump(t, t_silver + 1.4, 0.4) + _bump(t, t_silver + 2.2, 0.4)) if n == 3 else 4)
        K.siedzi_na(st, t, f"{key} w wozie", szk, "wóz", 10.0)
    woz_srebra(st, t, u, lerp(220, 900, ease(pr(t, t_silver - 0.3, T - t_silver))))
    u.rzedy["jeńcy"] = P.droga + 0.006
    for n in range(3):
        K.lalka(st, t, f"jeniec {n + 1}", ("murid3", "murid4", "murid5")[n], lerp(100, 700, ease(pr(t, t_silver, T - t_silver))) - n * 50, 90,
                y=730, rzad="jeńcy", flip=1, hop=4)
    koniec(st, w, t)


def s_syn_wraca(st, w, t, T):
    """Z lewego brzegu wjeżdża w bród młody oficer w rosyjskim mundurze; przy imieniu podpis „Jamal al-Din”; zatrzymuje konia
    na środku rzeki, patrzy na góry; po chwili rusza dalej w prawo."""
    t_name = sl("syn_wraca", "jamal")
    staje, rusza = po_kw("syn_wraca", -1.2), po_kw("syn_wraca", 1.0)
    x = lerp(240, 640, ease_out(pr(t, 0.4, staje - 0.4))) + 400 * ease(pr(t, rusza, T - rusza))
    kam(st, t, I["syn_wraca"], lerp(540, 700, ease(t / T)), lerp(500, 470, ease(pr(t, staje, 1.4))), lerp(1.3, 1.6, ease(pr(t, staje, 1.4))), 0.66)
    miczik(st, t, w, swiatlo=MICZIK_SWIATLO['syn_wraca'])
    brzegi_oddzialy(st, t, w, kadr=(-999, 1150))
    stoi = staje < t < rusza
    jezdziec(st, t, "dzamal_oficer", x, 732, P.droga + 0.01, flip=-1 if _bump(t, (staje + rusza) / 2, 0.4) > 0 else 1, h=160, seed=4,
             galop=0.0 if stoi else 0.4)
    for n in range(3):
        if not stoi and t < T - 0.3:
            f = (t * 3 + n * 0.33) % 1.0
            st.put(Z0.prop("kulka"), x - 30 + n * 30, 720 - 30 * math.sin(math.pi * f), P.droga + 0.02, h=7, anchor=(0.5, 0.5),
                   tint=(0.7, 0.85, 1.0), shadow=None)
    podpis(w, t, "Jamal al-Din", 560, 340, t_name, 3.0)
    koniec(st, w, t, dim=0.98)


def s_mundur(st, w, t, T):
    """Prawy brzeg: młody oficer zsiada z konia, zdejmuje epolety (dłoń do barku), murid podaje mu złożoną czarną czerkieskę,
    syn chwyta ją i na moment znika za koniem — wychodzi w czerkiesce (zmiana stroju w kadrze, 1.28)."""
    kam(st, t, I["mundur"], 760, 470, 1.4, 0.8)
    miczik(st, t, w, swiatlo=MICZIK_SWIATLO['mundur'])
    u = K.uk(st, t)
    t_off, t_put = sl("mundur", "take"), sl("mundur", "put")
    u.put("koń syna", J.zwierze("kon"), 1000, STOPY, u.p("lalki", 2), "zwierze", h=230, anchor=(0.5, 1.0), sx=-1)
    zrywa = _bump(t, t_off + 0.5, 0.4)
    zmiana = t > t_put + 0.4
    podaje = ease(pr(t, t_put - 1.0, 0.55))
    murid = K.lalka(st, t, "murid", "murid", 560, 290, flip=1,
                    przod=lambda s: K.w_zasiegu(s, (lerp(600, 650, podaje), 560)) if t < t_put + 0.3 else 8)
    geo = K.w_dloni(st, t, "czerkieska", "czerkieska", murid, 50, rot=0) if t < t_put else None
    wolny = geo(160, 60) if geo else (660, 560)
    chwyta = ease(pr(t, t_put - 0.4, 0.3))
    xs = lerp(1000, 760, ease(pr(t, 0.4, 0.8)))
    za_koniem = _bump(t, t_put + 0.4, 0.35) > 0  # na chwilę za koniem: lalki nie ma (przebiera się)
    syn = None if za_koniem else K.lalka(st, t, "syn", "dzamal_gorski" if zmiana else "dzamal_oficer", xs, 300, flip=-1,
                  przod=(8 + 140 * zrywa) if t < t_put - 0.4 else  # ręka do barku po epoletę (kątem — zawsze w zasięgu)
                  (lambda s: K.w_zasiegu(s, (lerp(K.U.Uklad.dlon_z_kata(s, 8)[0], wolny[0], chwyta),
                                             lerp(K.U.Uklad.dlon_z_kata(s, 8)[1], wolny[1], chwyta)))))
    if t_off < t < t_off + 1.5:  # zerwana epoleta leci w bok i zostaje na ziemi
        f = pr(t, t_off + 0.5, 0.8)
        st.put(J.tag("", 10), 760 + 100 * f, 420 + 280 * f * f, P.lalki + 0.03, h=14, anchor=(0.5, 0.5), tint=(1.0, 0.8, 0.3), rot=400 * f,
               shadow=None)
    if syn and geo and chwyta >= 1:
        u.dotyka("czerkieska", (*syn["przod"]["dlon"], syn["p"]), "syn chwyta czerkieskę (dłoń na niej)", 6.0)
    koniec(st, w, t)


def s_uscisk(st, w, t, T):
    """Muzyka milknie, zostaje szum rzeki; Szamil podchodzi, dłoń puszcza rękojeść kindżału; obejmuje syna — dłonie każdego na
    plecach drugiego (kontrola); kamera bardzo wolno dojeżdża (emocjonalny szczyt, Wytyczne 1.23)."""
    kam(st, t, I["uscisk"], 640, 470, lerp(1.6, 1.95, t / T), 0.8)
    miczik(st, t, w, swiatlo=MICZIK_SWIATLO['uscisk'])
    u = K.uk(st, t)
    zbliz = ease(pr(t, 0.8, 1.4))
    xs, xd = lerp(460, 600, zbliz), lerp(760, 690, zbliz)
    f_s, f_d = J.figura(w.szamil), J.figura("dzamal_gorski")
    plecy = lambda x, flip, f: (x + (110 - 150) * (300 / f.wys) * flip, STOPY - (f.stopa - 250) * 300 / f.wys)
    cel_s, cel_d = plecy(xd, -1, f_d), plecy(xs, 1, f_s)
    od = lambda s: K.U.Uklad.dlon_z_kata(s, 8)
    puszcza = ease(pr(t, 0.6, 0.4))
    sz = K.lalka(st, t, "Szamil", w.szamil, xs, 300, flip=1,
                 przod=lambda s: (s["punkt"](156, 336) if puszcza < 1 else K.w_zasiegu(s, (lerp(od(s)[0], cel_s[0], zbliz), lerp(od(s)[1], cel_s[1], zbliz)))))
    syn = K.lalka(st, t, "syn", "dzamal_gorski", xd, 300, flip=-1, glebia=4,
                  przod=lambda s: K.w_zasiegu(s, (lerp(od(s)[0], cel_d[0], zbliz), lerp(od(s)[1], cel_d[1], zbliz))))
    if sz and syn and zbliz >= 1:
        u.dotyka("syn", (*sz["przod"]["dlon"], sz["p"]), "dłoń Szamila na plecach syna", 8.0)
        u.dotyka("Szamil", (*syn["przod"]["dlon"], syn["p"]), "dłoń syna na plecach ojca", 8.0)
    koniec(st, w, t, dim=0.97)


def s_obcy(st, w, t, T):
    """Izba: syn w czerkiesce siedzi nad rosyjską książką, za oknem śnieg; nad nim obłok z miniaturą Petersburga (iglice);
    Szamil w drzwiach patrzy na syna; obłok pęka i znika."""
    kam(st, t, I["obcy"], 640, 460, 1.3, 0.8)
    izba_kz(st, t, w, 1, okno_x=1000)
    u = K.uk(st, t)
    t_str, t_miss = sl("obcy", "stranger"), sl("obcy", "missed")
    u.rzecz("stolik", K.ark("stol_niski"), 690, STOPY + 10, u.p("przod"), (180, 120), 90)
    blat_y = K.pkt("stol_niski", 180, 20, 690, STOPY + 10, 90)[1]
    szk = K.lalka(st, t, "syn", "dzamal_gorski", 600, 290, flip=1, siedzi=True, nogi=STOPY, y=K.y_siedzi("dzamal_gorski", 290, blat_y + 12),
                  przod=lambda s: K.w_zasiegu(s, (700, blat_y - 70), f=1.0))  # przy wejściu lalki ręka sięga, ile może
    K.w_dloni(st, t, "książka", "ksiazka_ros", szk, 70, rot=0)
    k = ease(pr(t, t_miss - 0.4, 0.8)) * (1 - ease(pr(t, po_kw("obcy", 0.1), 0.3)))
    if k > 0:
        J.hang(st, J.rek("oblok"), 760, 90, P.rekwizyty, k, t, 61, h=200, drop=300)
        J.hang(st, J.iglice(), 760, 150, P.rekwizyty + 0.004, k, t, 62, w=230, drop=300, string=False)
    K.lalka(st, t, "Szamil w drzwiach", w.szamil, 260, 300, flip=1, k=ease(pr(t, t_str - 0.4, 0.6)), wejscie=False)
    if szk and szk["k"] >= 1:
        u.widac("książka", 0.85, "książka: widać ≥ 85%", oprocz=("rampa", "syn"))
    koniec(st, w, t, extra=(0.98, 0.98, 1.02))


def s_smierc(st, w, t, T):
    """Syn leży w łóżku pod kołdrą, oparty o poduszkę; przy nim świeca na szafce; Szamil stoi przy łóżku, dłoń na kołdrze;
    syn kaszle; na „died” syn osuwa się na poduszkę, płomień świecy drży i gaśnie, smużka dymu — bez gagu; kurtyna w pauzie
    (render: „Act 5 · How does a 25-year war end?”). Lalka siedząca to korpus bez nóg — na łóżku przodem do widza wyglądała
    jak ucięta (reżyser 28.11: „w 51 oni nie mają nóg”), więc syn jest pod kołdrą, a Szamil stoi."""
    kam(st, t, I["smierc"], 640, 470, lerp(1.3, 1.45, ease(t / T)), 0.8)
    izba_kz(st, t, w, 2, okno_x=980, noc=True)
    w.noc = 0.6
    u = K.uk(st, t)
    t_died = sl("smierc", "died")
    u.mebel("łóżko", "lozko_kz", 640, 150, rzad="przy_scianie")
    u.mebel("szafka", "skrzynka", 900, 110, rzad="przy_scianie")
    u.na("świeca", K.ark("swieca"), "szafka", "blat", 0.5, 80)
    sx, sy = u.powierzchnia("szafka", "blat", 0.5)
    _, my = u.powierzchnia("łóżko", "materac", 0.5)
    kaszel = sum(_bump(t, a, 0.2) for a in (0.7, 1.3, 2.2))
    lezy = ease(pr(t, t_died - 0.6, 0.8))
    # syn LEŻY (reżyser 28.11: „jak on leży pod kołdrą, to weź go połóż”): lalka obrócona o 90° wokół stóp, głowa na
    # poduszce u wezgłowia, ciało pod kołdrą; kaszel unosi pierś, na „died” głowa opada
    syn = K.lalka(st, t, "syn", "dzamal_gorski", 742, 260, y=600, flip=1, lean=-90 - 4 * kaszel + 3 * lezy, rzad="lalki")
    u.rzedy["kołdra"] = P.lalki + 0.02
    u.mebel("kołdra", "koldra_kz", 680, 96, rzad="kołdra", seed=131, y=650)  # od szyi po stopy, zwisa trochę na bok łóżka
    sz = K.lalka(st, t, "Szamil", w.szamil, 425, 300, flip=1, lean=6 * lezy, rzad="przod",
                 przod=lambda s: K.w_zasiegu(s, (500, 600)))
    gasnie = pr(t, t_died + 0.3, 0.3)
    if gasnie < 1:
        plomien(st, sx + 3 * math.sin(t * 20) * pr(t, t_died, 0.3), sy - 80 * 0.9, u.p("przy_scianie") + 0.003, t, h=26 * (1 - gasnie))
        st.put(J.glow(), sx, sy - 90, P.lalki + 0.013, w=420, anchor=(0.5, 0.5), mode="add", alpha=0.3 * (1 - gasnie), shadow=None,
               tint=(1.0, 0.8, 0.5))
    dym(st, sx, sy - 90, P.lalki + 0.014, t, t_died + 0.5, r=60, dl=1.2)
    koniec(st, w, t, dim=lerp(0.9, 0.62, gasnie), extra=(1.04, 0.96, 0.88))


# ================================================================ akt V: Gunib, kapitulacja, Kaługa, Medyna

def plaskowyz(st, t, w, x=700, k=1.0, wd=560):
    """Gunib: skała-płaskowyż (obiekt „skała Gunib”) z wioską na szczycie (zwraca y szczytu)."""
    u = K.uk(st, t)
    with u.obiekt("skała Gunib", "dekoracja"):
        Z0.rise(st, J.skala(), x, 712, P.most, min(k, bk(w, 0.35, 0.9)), t, 901, w=wd, wob=0.0, lift=480, anchor=(0.5, 1.0), sy=0.62)
    top = 712 - wd * 620 / 760 * 0.62 + wd * 110 / 760 * 0.62
    Z0.rise(st, J.aul(1), x + 20, top + 30, P.most - 0.003, min(k, bk(w, 0.55, 0.8)), t, 902, w=wd * 0.7, wob=0.0, lift=200,
            anchor=(0.5, 1.0), sy=0.6)
    return top


def s_gunib(st, w, t, T):
    """Płaskowyż z wioską wyrasta z mgły, zawieszka „Gunib, 1859”; na „sixty-two” na krawędzi staje Szamil z siwą brodą;
    wiatr szarpie czarną chorągwią; kamień obsuwa się z urwiska."""
    kam(st, t, I["gunib"], 700, lerp(420, 380, ease(t / T)), lerp(1.0, 1.25, ease(t / T)), 0.6)
    kaukaz(st, t, w, blisko=False, uklad=2)
    top = plaskowyz(st, t, w)
    u = K.uk(st, t)
    t_62 = sl("gunib", "sixty")
    u.rzedy["na skale"] = P.most + 0.004
    K.lalka(st, t, "Szamil na krawędzi", w.szamil, 640, 70, y=top + 26, rzad="na skale", flip=1, k=ease(pr(t, t_62 - 0.3, 0.5)), wejscie=False)
    st.put(J.rek_kz("choragiew"), 760, top + 30, P.most + 0.005, h=90, anchor=(0.04, 1.0), rot=3 * math.sin(t * 8), sx=1 + 0.06 * math.sin(t * 11))
    f = pr(t, po_kw("gunib", -0.4), 1.0)
    if 0 < f < 1:
        st.put(Z0.prop("kamien"), 520 - 20 * f, top + 40 + 300 * f * f, P.most + 0.006, h=18, anchor=(0.5, 0.5), rot=300 * f, shadow=None)
    mgla = 1 - ease(pr(t, 0.0, 2.4))
    st.put(J.S("cloud_center", 0.4), 700, 560, P.most + 0.01, w=1400, anchor=(0.5, 0.5), alpha=0.6 * mgla + 0.2, tint=(0.92, 0.92, 0.96),
           shadow=None)
    podpis(w, t, "Gunib, 1859", 380, 40, 0.5, T)
    koniec(st, w, t, extra=(0.96, 0.97, 1.02))


def s_liczby(st, w, t, T):
    """Kamera odjeżdża: garstka obrońców na górze, tabliczka „400”; dookoła góry wysuwają się rzędy wojska aż po horyzont,
    każdy rząd z opóźnieniem; tabliczka „16,000” (potęga = liczba i przestrzeń, 1.17)."""
    kam(st, t, I["liczby"], 700, 420, lerp(1.4, 0.98, ease(pr(t, 0, T * 0.7))), 0.6)
    kaukaz(st, t, w, blisko=False, uklad=2)
    top = plaskowyz(st, t, w)
    u = K.uk(st, t)
    t_400, t_16 = sl("liczby", "four"), sl("liczby", "sixteen")
    u.rzedy["na skale"] = P.most + 0.004
    for n in range(7):
        K.lalka(st, t, f"obrońca {n + 1}", ("szamil_stary", "murid2", "murid3", "murid4", "murid5", "ghazi", "mysliwy")[n], 600 + n * 30, 46,
                y=top + 26, rzad="na skale", flip=1 if n < 4 else -1)
    for r, (p, y, h, n_) in enumerate(((0.62, 640, 64, 22), (0.70, 680, 90, 16), (0.80, STOPY, 130, 11))):
        u.rzedy[f"szereg{r}"] = p
        for n in range(n_):
            # od x 60 (pierwszy szereg, najwięksi: od 130): skrajni przy x −40 stali cały czas poza kadrem (kontrola 28.11)
            x = (130 if r == 2 else 60) + n * ((1220 if r == 2 else 1300) / n_) + (r % 2) * 30
            if 560 < x < 840 and r == 0:
                continue
            K.zolnierz(st, t, f"żołnierz {r}.{n}", ZOLNIERZE[(n + 2 * r) % 6], x, h, y=y, rzad=f"szereg{r}",
                       flip=1 if x < 700 else -1, k=ease(pr(t, t_400 + 0.6 + 0.04 * n + 0.35 * r, 0.5)))
    podpis(w, t, "400", 700, 150, t_400, T)
    podpis(w, t, "16,000", 230, 300, t_16, T)
    koniec(st, w, t, extra=(0.96, 0.97, 1.02))


def s_szturm_gunib(st, w, t, T):
    """Świt: żołnierze wspinają się po urwisku na linach, jeden za drugim (dłonie na linie); pierwszy dosięga krawędzi;
    na górze unosi się biała flaga i powiewa; cisza."""
    kam(st, t, I["szturm_gunib"], 660, 460, 1.15, 0.66)
    kaukaz(st, t, w, blisko=False, uklad=2)
    top = plaskowyz(st, t, w, wd=640)
    u = K.uk(st, t)
    u.rzedy["urwisko"] = P.most + 0.006
    for n in range(5):
        x0, y0, x1, y1 = 470 + n * 40, top + 20, 480 + n * 40, 712
        lina = f"lina {n + 1}"
        with u.obiekt(lina, "rzecz"):
            st.line([(x0, y0), (x1, y1)], P.most + 0.0055, width=1.6, color=(220, 200, 160), alpha=0.9)
        f = pr(t, 0.3 + 0.25 * n, 3.4)
        y = lerp(700, top + 70, ease(f))
        # dłoń zawsze na odcinku liny: nad górnym końcem liny (przy krawędzi urwiska) chwyta jej koniec (kontrola 28.11)
        na_linie = lambda yy, x0=x0, x1=x1, y0=y0, y1=y1: (x0 + (x1 - x0) * (max(yy, y0 + 4) - y0) / (y1 - y0), max(yy, y0 + 4))
        xl = na_linie(y)[0]
        szk = K.lalka(st, t, f"żołnierz {n + 1}", ZOLNIERZE[n], xl + 8, 70, y=y, rzad="urwisko", flip=-1, wejscie=False,
                      przod=lambda s, f_=na_linie: f_(s["bark_przod"][1] - 8), tyl=lambda s, f_=na_linie: f_(s["bark_tyl"][1] + 4))
        if szk:
            u.dotyka(lina, (*szk["przod"]["dlon"], szk["p"]), f"żołnierz {n + 1}: dłoń na linie", 4.0)
    t_flag = po_kw("szturm_gunib", -0.6)
    k = ease(pr(t, t_flag, 0.8))
    if k > 0:
        st.put(J.rek_kz("flaga_biala"), 760, top + 40 + (1 - k) * 160, P.most + 0.005, h=130, anchor=(0.04, 1.0),
               sx=1 + 0.05 * math.sin(t * 9), rot=2 * math.sin(t * 6))
    koniec(st, w, t, extra=(1.06, 0.94, 0.86))


def polana(st, t, w):
    """Polana pod brzozami pod Gunibem (obraz Horschelta: kapitulacja pod brzozą)."""
    kaukaz(st, t, w, blisko=False, kul=False)
    plaskowyz(st, t, w, x=1050, wd=520)
    for n, x in enumerate((180, 420)):
        Z0.rise(st, J.rek_kz("brzoza"), x, STOPY + 6, P.drzewa - 0.01 * n, bk(w, 0.4 + 0.1 * n), t, 910 + n, h=460, wob=0.3, anchor=(0.5, 1.0))


def s_kapitulacja(st, w, t, T):
    """Szamil, siwy, schodzi ścieżką do księcia siedzącego na kamieniu pod brzozą (biodro na kamieniu — kontrola), za nim kilku
    muridów; przy nazwisku podpis „Prince Baryatinsky”; Szamil staje przed księciem; na „siridar” nad księciem SIRIDAR — bez gagu."""
    kam(st, t, I["kapitulacja"], lerp(720, 600, ease(t / T)), 440, lerp(1.05, 1.2, ease(t / T)), 0.8)
    polana(st, t, w)
    u = K.uk(st, t)
    t_bar, t_sir = sl("kapitulacja", "baryatinsky"), sl("kapitulacja", "siridar")
    kh = 90
    # kamień ZA księciem: jego nogi zwisają przed kamieniem (przed kamieniem książę był samym korpusem — reżyser 28.11)
    u.put("kamień", Z0.prop("kamien"), 360, STOPY + 6, u.p("lalki", -2), h=kh, anchor=(0.5, 1.0))
    ks = K.lalka(st, t, "Bariatinski", "bariatinski", 360, 300, flip=1, siedzi=True, nogi=STOPY, y=K.y_siedzi("bariatinski", 300, STOPY + 6 - kh * 0.8),
                 przod=20 + 50 * _bump(t, t_sir + 0.8, 1.0))
    if ks and ks["k"] >= 1:
        K.siedzi_na(st, t, "Bariatinski", ks, "kamień", 8.0)
    u.rzedy["sztab"] = P.lalki - 0.01
    for n in range(3):
        K.lalka(st, t, f"oficer {n + 1}", ("oficer_ros", "oficer_ros2", "oficer_ros3")[n], 200 - n * 70, 290, flip=1, rzad="sztab", y=STOPY - 4)
    x = lerp(1180, 560, ease(pr(t, 0.6, t_bar + 1.4)))
    idzie = 0.6 < t < t_bar + 2.0
    K.lalka(st, t, "Szamil", w.szamil, x, 300, flip=-1, hop=4 * idzie, przod=4)
    u.rzedy["murid"] = P.lalki + 0.005
    for n in range(2):
        K.lalka(st, t, f"murid {n + 1}", MURIDZI[n + 1], x + 150 + n * 110, 280, flip=-1, hop=4 * idzie, rzad="murid")
    if x < 1080:
        u.widac("Szamil", 0.95, "Szamil: widać ≥ 95%")
    podpis(w, t, "Prince Baryatinsky", 360, 280, t_bar, 2.6)
    slowo(st, t, "SIRIDAR", 360, 200, pr(t, t_sir, 0.6), seed=30, h=74)
    koniec(st, w, t, extra=(0.98, 0.98, 1.0))


def s_stempel(st, w, t, T):
    """Gabinet w Petersburgu, ten sam urzędnik co w 1839, siwy; kładzie raport; pieczątka opada powoli: „SHAMIL: CAPTURED” —
    trzecie podejście gagu bez żartu (bez brzdęku), urzędnik tylko patrzy; za oknem biją dzwony."""
    kam(st, t, I["stempel"], 600, 470, lerp(1.4, 1.55, ease(t / T)), 0.8)
    gabinet_cara(st, t, w, okno_x=1000, portret_x=250)
    u = K.uk(st, t)
    u.mebel("biurko", "biurko_palac", 560, 170, rzad="przod")
    _, blat = u.powierzchnia("biurko", "blat", 0.5)
    t_true = sl("stempel", "true")
    K.lalka(st, t, "urzędnik", "urzednik_stary", 760, 300, flip=-1, przod=lambda s: 30 + 40 * ease(pr(t, 0.4, 0.6)) * (1 - ease(pr(t, 1.4, 0.6))))
    pieczatka(st, t, 1.0, "SHAMIL: CAPTURED", x=560, y=blat - 30, p=u.p("przod", 0.6), stary=True, gag=False, h_rap=120)
    for n in range(2):  # dzwony za oknem
        k = pr(t, t_true + 0.4 * n, 0.4)
        if k > 0:
            st.put(J.tag("DONG", 26), 960 + 80 * n, 200 + 20 * math.sin(t * 6 + n), P.miasto + 0.012, h=40, anchor=(0.5, 0.5),
                   alpha=ease(k), rot=8 * math.sin(t * 5 + n))
    koniec(st, w, t, dim=0.95, extra=(0.98, 0.98, 1.02))


def s_car(st, w, t, T):
    """Sala z kolumnami: Szamil staje przed carem Aleksandrem II (podpis); car podaje mu rękę — dłonie w jednym punkcie
    (kontrola); na „Kaluga” obok zjeżdża domek z kolumienkami i zawieszka „Kaluga”."""
    kam(st, t, I["car"], 640, 430, 1.15, 0.8)
    sala_tronowa_sc(st, t, w)
    u = K.uk(st, t)
    t_tsar, t_hon, t_kal = sl("car", "tsar"), sl("car", "honours"), sl("car", "kaluga")
    xs = lerp(380, 600, ease(pr(t, 0.4, 1.8)))
    uscisk = ease(pr(t, t_hon - 0.3, 0.6))
    punkt_ = ((xs + 760) / 2, STOPY - 160)
    cel = lambda s: (lerp(K.U.Uklad.dlon_z_kata(s, 8)[0], punkt_[0], uscisk), lerp(K.U.Uklad.dlon_z_kata(s, 8)[1], punkt_[1], uscisk))
    car = K.lalka(st, t, "car", "car", 760, 320, flip=-1, przod=cel)
    sz = K.lalka(st, t, "Szamil", w.szamil, xs, 300, flip=1, przod=cel)
    if car and sz and uscisk >= 1:
        u.kontakt((*car["przod"]["dlon"], car["p"]), (*sz["przod"]["dlon"], sz["p"]), "uścisk dłoni: dłonie razem", 4.0)
    u.rzedy["dwór"] = P.lalki - 0.02
    for n in range(4):
        K.lalka(st, t, f"oficer {n + 1}", ("oficer_ros", "oficer_ros2", "oficer_ros3", "oficer_ros4")[n], 200 + n * 300 if n < 2 else 900 + n * 60,
                270, flip=1 if n < 2 else -1, rzad="dwór")
    podpis(w, t, "Tsar Alexander II", 760, 240, t_tsar, 2.6)
    k = pr(t, t_kal, 0.8)
    if k > 0:
        J.hang(st, J.rek_kz("dom_kaluga"), 1020, 80, P.rekwizyty, k, t, 1350, w=280, drop=360, strings=(0.15, 0.85))
        podpis(w, t, "Kaluga", 1020, 40, t_kal + 0.3, T)
    koniec(st, w, t, extra=(1.04, 1.0, 0.94))


def s_kaluga(st, w, t, T):
    """Kaługa: Szamil na ganku domu z kolumienkami; zza płotu wychylają się głowy gapiów, jedna po drugiej (damy, pan
    w meloniku, dziecko, żołnierz); Szamil uprzejmie macha, gapie chowają się i wysuwają; gag po kwestii: zza płotu wychyla
    się koza — Szamil i koza patrzą na siebie (koza: puenta)."""
    kam(st, t, I["kaluga"], 640, 440, lerp(1.0, 1.12, ease(t / T)), 0.75)
    kaluga_sc2(st, t, w)
    u = K.uk(st, t)
    t_guest, t_look = sl("kaluga", "guest"), sl("kaluga", "look")
    K.lalka(st, t, "Szamil", w.szamil, 760, 260, y=650, rzad="dom", flip=-1, przod=lambda s: 20 + 130 * _bump(t, t_look + 0.6, 0.6))
    u.rzedy["gapie"] = P.lalki - 0.004
    gapie = ("gap1", "gap2", "dama2", "gap3", "zolnierz4", "dama3")
    chowa = _bump(t, t_look + 0.7, 0.5)
    for n, key in enumerate(gapie):
        k = ease(pr(t, t_guest - 1.6 + 0.35 * n, 0.4))
        if k > 0:
            K.lalka(st, t, f"gap {n + 1}", key, 140 + n * 180 + (n % 2) * 30, 250 if key != "gap3" else 190, y=STOPY + 70 * chowa,
                    rzad="gapie", flip=1 if n < 3 else -1, k=k, wejscie=False)
    gag = po_kw("kaluga", 0.1)
    kz = ease(pr(t, gag, 0.5))
    if kz > 0:
        koza(st, t, "koza za płotem", 1200, y=STOPY - 70 + 80 * (1 - kz), p=P.lalki - 0.003, h=110, flip=-1)
    u.put("płot", J.rek_kz("plot"), CX, STOPY + 20, P.lalki + 0.01, w=1500, anchor=(0.5, 1.0))
    koniec(st, w, t)


def s_medyna(st, w, t, T):
    """Pustynia pod księżycem: karawana, Szamil na wielbłądzie (biodro na grzbiecie — kontrola); zawieszka „Medina, 1871”;
    na „desert” karawana staje, Szamil zsiada i patrzy na wydmy. Kurtyna w pauzie (render: „Act 6 · How did his war get into
    Dune?”)."""
    w.noc = 1.0
    kam(st, t, I["medyna"], lerp(700, 560, t / T), 430, 1.05, 0.8)
    pustynia(st, t, w)
    u = K.uk(st, t)
    t_med, t_des = sl("medyna", "medina"), sl("medyna", "desert")
    staje = pr(t, t_des - 1.0, 0.8)
    for n in range(3):
        x = lerp(1250 + n * 230, 300 + n * 230, min(pr(t, 0, T), pr(t, 0, t_des - 0.2) * (t_des - 0.2) / T))
        hw = 210
        u.put(f"wielbłąd {n + 1}", J.rek_kz("wielblad"), x, STOPY, P.lalki + 0.004 * n, "zwierze", h=hw, anchor=(0.5, 1.0), sx=-1,
              rot=1.5 * math.sin(t * 4 + n) * (1 - staje))
        if n == 0:
            grzbiet = K.pkt("wielblad", 220, 104, x, STOPY, hw, sx=-1)[1]
            u.rzedy["na wielbłądzie"] = P.lalki + 0.002
            zsiada = ease(pr(t, t_des, 0.8))
            if zsiada < 0.5:
                sz = K.lalka(st, t, "Szamil", w.szamil, x + 6, 200, y=K.y_siedzi(w.szamil, 200, grzbiet + 6), rzad="na wielbłądzie", flip=-1,
                             siedzi=True, wejscie=False)
                K.siedzi_na(st, t, "Szamil", sz, "wielbłąd 1", 10.0)
            else:
                K.lalka(st, t, "Szamil", w.szamil, x - 130, 260, flip=-1, wejscie=False)
    podpis(w, t, "Medina, 1871", CX, 40, t_med, T)
    koniec(st, w, t, extra=(0.9, 0.92, 1.05))


# ================================================================ akt VI: słowa i puenta

def pracownia(st, t, w, rok, kto, x=600, sciana="paski"):
    """Pracownia pisarza: ściana, okno, biurko z maszyną do pisania na blacie; pisarz siedzi za biurkiem, palce na klawiszach
    (kontrola: dłoń na maszynie)."""
    pracownia_sc(st, t, w, 0 if kto == "blanch" else 1)
    u = K.uk(st, t)
    u.mebel("biurko", "biurko_pisarza", 660, 160, rzad="przod")
    geo = u.na("maszyna", K.ark("maszyna"), "biurko", "blat", 0.5, 90)
    stuk = lambda faza: 6 * max(0.0, math.sin(t * 16 + faza))
    _, blat_y = u.powierzchnia("biurko", "blat", 0.5)
    stoi = wejscie(1.0) >= 1  # przy budowie dekoracji maszyna jeszcze wyrasta: dłonie opuszczone (kontrola 28.11)
    szk = K.lalka(st, t, kto, kto, x, 290, flip=1, siedzi=True, nogi=STOPY, y=K.y_siedzi(kto, 290, blat_y + (40 if kto == "blanch" else 8)),
                  przod=(lambda s: (geo(250, 112)[0], geo(250, 112)[1] - 4 + stuk(0))) if stoi else 8,
                  tyl=(lambda s: (geo(160, 112)[0], geo(160, 112)[1] - 4 + stuk(1.6))) if stoi else 6)
    if szk and stoi:
        u.dotyka("maszyna", (*szk["przod"]["dlon"], u.p("przod") + 0.002), f"{kto}: dłoń na klawiszach", 10.0)
    podpis(w, t, rok, 1000, 40, 0.4, 99)
    return geo, blat_y


def s_blanch(st, w, t, T):
    """Pisarka w kapeluszu przy maszynie, zawieszka „London, 1960”; podpis przy nazwisku; dzwonek maszyny, kartki wylatują
    jak ptaki i składają się w książkę z szablami na okładce; gag: ostatnia kartka ląduje na kocie, który miauczy i ucieka."""
    kam(st, t, I["blanch"], 640, 430, 1.2, 0.8)
    geo, blat_y = pracownia(st, t, w, "London, 1960", "blanch", sciana="kwiaty")
    t_name, t_book = sl("blanch", "lesley"), sl("blanch", "book")
    wx, wy = geo(210, 20)
    for n in range(6):
        f = pr(t, t_book - 1.4 + 0.3 * n, 1.2)
        if 0 < f < 1:
            st.put(J.rek_kz("kartka"), lerp(wx, 920, f), lerp(wy, STOPY - 150, f) - 160 * math.sin(math.pi * f), P.lalki + 0.05, h=50,
                   anchor=(0.5, 0.5), rot=200 * f + 30 * math.sin(t * 10 + n))
    Z0.rise(st, J.okladka(), 920, STOPY - 150, P.lalki + 0.045, ease(pr(t, t_book + 0.4, 0.8)), t, 931, h=150, lift=180, anchor=(0.5, 1.0))
    gag = po_kw("blanch", 0.0)
    f = pr(t, gag, 0.9)
    kot_x = 330 - 600 * ease(pr(t, gag + 1.1, 0.8))
    u = K.uk(st, t)
    u.put("kot", J.rek_kz("kot"), kot_x, STOPY + 2, u.p("lalki", 2), "zwierze", h=80, anchor=(0.5, 1.0), sx=-1 if t > gag + 1.0 else 1)
    if 0 < f:
        lx = lerp(wx, kot_x + 20, min(f, 1.0))
        ly = lerp(wy, STOPY - 70, min(f, 1.0)) - 120 * math.sin(math.pi * min(f, 1.0))
        if t < gag + 1.1:
            st.put(J.rek_kz("kartka"), lx, ly, P.lalki + 0.05, h=50, anchor=(0.5, 0.5), rot=220 * min(f, 1.0))
        podpis(w, t, "MEOW!", 330, 330, gag + 0.9, 1.6)
    podpis(w, t, "Lesley Blanch", 560, 280, t_name, 2.6)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def s_herbert(st, w, t, T):
    """Mężczyzna z brodą przy maszynie, zawieszka „1965”, podpis; z maszyny zamiast kartek sypie się piasek, usypuje wydmę,
    zasypuje mu buty; z wydmy wynurza się mały robak i rozgląda się; gag: Herbert wytrząsa piasek z buta."""
    kam(st, t, I["herbert"], 680, 430, lerp(1.1, 1.25, ease(t / T)), 0.8)
    geo, blat_y = pracownia(st, t, w, "1965", "herbert")
    t_name, t_dune = sl("herbert", "frank"), sl("herbert", "dune")
    wx, wy = geo(210, 20)
    if t > t_dune - 0.6:
        for n in range(14):
            f = (t * 1.4 + n * 0.071) % 1.0
            st.put(Z0.prop("kulka"), lerp(wx, 900, f) + 6 * math.sin(n), wy + f * (STOPY - wy) - 60 * math.sin(math.pi * f), P.lalki + 0.05,
                   h=7, anchor=(0.5, 0.5), tint=(0.95, 0.75, 0.45), shadow=None)
    wyd = ease(pr(t, t_dune - 0.4, T - t_dune - 1.0))
    Z0.rise(st, J.wydma(1), 900, STOPY + 10, P.lalki + 0.045, wyd, t, 932, w=520, lift=150, anchor=(0.5, 1.0), wob=0.0)
    wys = ease(pr(t, po_kw("herbert", -1.2), 0.6)) * (1 - ease(pr(t, po_kw("herbert", 1.0), 0.5)))
    robak(st, t, 920, STOPY - 30, P.lalki + 0.044, wys, h=170, flip=-1, rot=10 * math.sin(t * 3))
    Z0.rise(st, J.wydma(0), 640, STOPY + 40, P.lalki + 0.046, wyd, t, 933, w=700, lift=120, anchor=(0.5, 1.0), wob=0.0, sy=0.4)
    podpis(w, t, "Frank Herbert", 560, 280, t_name, 2.6)
    if t > po_kw("herbert", 0.2):
        podpis(w, t, "*SHAKE SHAKE*", 560, 330, po_kw("herbert", 0.2), 1.4)
    koniec(st, w, t, extra=(1.02, 1.0, 0.96))


def s_slowa1(st, w, t, T):
    """Scena podzielona (wydma z lewej, góry z prawej): KANLY wisi nad górami (to samo co w 1834) i przelatuje na nitce nad wydmę,
    gdzie dwaj fremeni zwracają się do siebie; na „kindjal” murid z gór podaje kindżał, który przechodzi nad sceną do dłoni
    w rękawicy z herbem po stronie pustyni."""
    kam(st, t, I["slowa1"], lerp(700, 580, ease(t / T)), 390, 1.02, 0.8)
    teatr_kz(st, t, w)
    t_kanly, t_feud2, t_kindjal = sl("slowa1", "kanly"), sl("slowa1", "feud", 2), sl("slowa1", "kindjal")
    przelot = ease(pr(t, t_kanly + 0.8, t_feud2 - t_kanly - 0.6))
    slowo(st, t, "KANLY", lerp(1000, 300, przelot), 140, pr(t, 0.2, 0.6), seed=40, h=80)
    zwrot = ease(pr(t, t_feud2 - 0.2, 0.4))
    K.lalka(st, t, "fremen 1", "fremen", 220, 260, flip=lerp(-1, 1, zwrot))
    K.lalka(st, t, "fremen 2", "fremen2", 420, 260, flip=-1)
    murid = K.lalka(st, t, "murid", "murid", 1060, 280, flip=-1, przod=lambda s: 20 + 60 * ease(pr(t, t_kindjal - 0.6, 0.4)))
    prz = pr(t, t_kindjal, 1.6)
    if prz <= 0:
        K.w_dloni(st, t, "kindżał", "kindzal", murid, 90, rot=-90)
    else:
        k = ease(prz)
        st.put(J.rek_kz("kindzal"), lerp(990, 380, k), lerp(540, 470, k) - 120 * math.sin(math.pi * k), P.lalki + 0.03, h=90, anchor=(0.5, 0.5),
               rot=lerp(0, 360, k) if k < 1 else -90)
        st.put(J.rek_kz("rekawica"), 330, 500, P.lalki + 0.031, h=60, anchor=(0.2, 0.5), alpha=ease(pr(t, t_kindjal + 0.6, 0.4)))
    koniec(st, w, t)


def s_slowa2(st, w, t, T):
    """Na „Chakobsa” dwaj myśliwi w górach szepczą, z ust wylatują litery i lecą nad wydmę, gdzie składają się w CHAKOBSA; na
    „Sietch and tabr” słowa SIETCH i TABR zjeżdżają osobno i sklejają się nad jaskinią w skale pustyni; gag po kwestii: z jaskini
    wygląda robak, tabliczka się chwieje."""
    kam(st, t, I["slowa2"], lerp(640, 520, ease(t / T)), 390, 1.02, 0.8)
    teatr_kz(st, t, w, pora="noc")
    t_ch, t_si, t_home = sl("slowa2", "chakobsa"), sl("slowa2", "sietch"), sl("slowa2", "home")
    lalka(st, t, "mysliwy", 920, 290, flip=1, lean=-6 * _bump(t, t_ch + 0.6, 0.8), seed=5)
    lalka(st, t, "mysliwy", 1100, 280, flip=-1, seed=6)
    for n, ch in enumerate("CHAKOBSA"):
        f = pr(t, t_ch + 0.15 * n, 1.8)
        if 0 < f < 1:
            st.put(J.tag(ch, 26), lerp(980, 300 + n * 22, f), lerp(470, 150, f) - 60 * math.sin(math.pi * f), P.rekwizyty - 0.01, h=40,
                   anchor=(0.5, 0.5), rot=20 * math.sin(t * 4 + n) * (1 - f))
    slowo(st, t, "CHAKOBSA", 380, 110, pr(t, t_ch + 1.6, 0.4), seed=41, h=64)
    Z0.rise(st, J.skala(), 330, STOPY, P.lalki - 0.03, ease(pr(t, t_si - 0.8, 0.8)), t, 950, h=260, lift=300, anchor=(0.5, 1.0),
            tint=(1.1, 0.95, 0.75), wob=0.0)
    st.put(Z0.black(), 330, STOPY - 40, P.lalki - 0.028, w=70, h=80, anchor=(0.5, 1.0), shadow=None, alpha=0.85 * ease(pr(t, t_si - 0.4, 0.4)))
    gag = po_kw("slowa2", 0.0)
    chwieje = 12 * math.exp(-max(0.0, t - gag - 0.6) * 2) * math.sin((t - gag) * 9) if t > gag + 0.6 else 0.0
    razem = ease(pr(t, t_home, 0.8))
    if razem < 1:
        J.hang(st, J.slowo("SIETCH", 44), lerp(180, 270, razem), 300, P.rekwizyty, pr(t, t_si, 0.6), t, 951, h=62, drop=380)
        J.hang(st, J.slowo("TABR", 44), lerp(500, 410, razem), 300, P.rekwizyty + 0.002, pr(t, t_si + 0.5, 0.6), t, 952, h=62, drop=380)
    else:
        J.hang(st, J.slowo("SIETCH TABR", 44), 340, 300, P.rekwizyty, 1.0, t, 953, h=62, drop=380, rot0=chwieje)
    wys = ease(pr(t, gag, 0.4)) * (1 - ease(pr(t, gag + 1.4, 0.4)))
    if wys > 0:
        robak(st, t, 330, STOPY - 30, P.lalki - 0.029, wys * 0.6, h=200)
    koniec(st, w, t)


def s_slowa3(st, w, t, T):
    """Na „padishah” nad lalką cara (Aleksander II, ta sama co w 1859) zjeżdża PADISHAH; na „siridar” nad księciem Bariatinskim
    SIRIDAR; obie tabliczki odjeżdżają na nitkach nad wydmę; car i książę patrzą za nimi i poprawiają mundury."""
    kam(st, t, I["slowa3"], CX, 400, 1.0, 0.8)
    teatr_kz(st, t, w, pora="zmierzch")
    t_pad, t_sir, t_end = sl("slowa3", "padishah"), sl("slowa3", "siridar"), sl("slowa3", "ended")
    patrza = ease(pr(t, t_end + 0.4, 0.5))
    K.lalka(st, t, "car", "car", 880, 300, flip=-1, lean=-4 * patrza, przod=lambda s: 30 * patrza)
    K.lalka(st, t, "Bariatinski", "bariatinski", 1100, 290, flip=-1, lean=-4 * patrza, przod=lambda s: 30 * patrza)
    przejazd = ease(pr(t, t_end, 2.0))
    slowo(st, t, "PADISHAH", lerp(880, 260, przejazd), 170, pr(t, t_pad, 0.6), seed=42, h=70)
    slowo(st, t, "SIRIDAR", lerp(1100, 360, przejazd), 270, pr(t, t_sir, 0.6), seed=43, h=70)
    koniec(st, w, t)


KARTA_W = 560


def s_zdanie(st, w, t, T):
    """Dwie karty na nitkach: z lewej pożółkła „To kill with the point lacked artistry.” (1960), z prawej biała z maszynopisem
    z Diuny (TEKST DO SPRAWDZENIA W WYDANIU, księga D7); ramka lupy przesuwa się po obu zdaniach, wspólne słowa podświetlają
    się na złoto; kindżał spada ostrzem w dół i wbija się w deskę między kartami."""
    kam(st, t, I["zdanie"], CX, 300, 1.08, 0.84)
    biblioteka_sc(st, t, w)
    st.spot = (CX, 300, P.rekwizyty, 620, 0.45)
    t_bl, t_dune = sl("zdanie", "blanch"), sl("zdanie", "dune")
    J.hang(st, J.karta("To kill with the point|lacked artistry.", "1960", True), 360, 130, P.rekwizyty, pr(t, t_bl - 0.2, 0.8), t, 1360,
           w=KARTA_W * 0.95, drop=500, strings=(0.2, 0.8), shadow=(6, 9, 10, 0.35))
    J.hang(st, J.karta("Killing with the tip|lacks artistry.", "Dune, 1965"), 920, 130, P.rekwizyty + 0.004, pr(t, t_dune - 0.2, 0.8), t, 1361,
           w=KARTA_W * 0.95, drop=500, strings=(0.2, 0.8), shadow=(6, 9, 10, 0.35))
    lupa = pr(t, t_dune + 1.0, 2.0)
    if lupa > 0:
        lx = lerp(260, 1020, ease(lupa))
        st.put(J.rek_kz("lupa"), lx, 250, P.rekwizyty + 0.03, h=170, anchor=(0.4, 0.4), rot=-10, shadow=(8, 10, 12, 0.4))
        for n, cx in enumerate((340, 940)):
            a = ease(pr(t, t_dune + 1.2 + 0.9 * n, 0.4))
            if a > 0:
                st.put(J.glow(), cx, 210, P.rekwizyty + 0.02, w=520, anchor=(0.5, 0.5), mode="add", alpha=0.35 * a, shadow=None, tint=(1.0, 0.82, 0.4))
    t0 = po_kw("zdanie", 0.2)
    k = pr(t, t0, 0.32)
    if k > 0:
        y = lerp(-260, STOPY - 40, k ** 2)
        drga = 6 * math.sin((t - t0) * 40) * math.exp(-(t - t0 - 0.32) * 5) if t > t0 + 0.32 else 0.0
        st.put(J.rek_kz("kindzal"), 640, y, P.rekwizyty + 0.01, h=200, anchor=(0.5, 0.86), rot=drga, shadow=(5, 7, 8, 0.4))
    koniec(st, w, t, dim=0.96)


def s_przyslowie(st, w, t, T):
    """Karta „…wisdom from the hills.”; na „became” słowo „hills” odkleja się z jednej nitki i spada; na jego miejsce zjeżdża
    „desert”; z dołu sypie się trochę piasku."""
    kam(st, t, I["przyslowie"], CX, 300, 1.1, 0.84)
    pustynia(st, t, w)
    st.spot = (CX, 300, P.rekwizyty, 620, 0.4)
    t_bec = sl("przyslowie", "became")
    J.hang(st, J.karta("Polish comes from the city,|wisdom from the", "1960", True), CX, 120, P.rekwizyty, pr(t, 0.1, 0.8), t, 1370,
           w=640, drop=500, strings=(0.2, 0.8))
    f = pr(t, t_bec, 1.0)
    if f < 1:
        rot = 60 * ease(pr(t, t_bec, 0.3))
        J.hang(st, J.slowo("hills", 40), 860, 240 + 500 * max(0.0, f - 0.3) ** 2, P.rekwizyty + 0.01, pr(t, 0.4, 0.8), t, 1371, h=56,
               drop=400, strings=(0.15,), rot0=rot)
    k = pr(t, t_bec + 1.0, 0.7)
    if k > 0:
        J.hang(st, J.slowo("desert", 40), 860, 240, P.rekwizyty + 0.012, k, t, 1372, h=56, drop=400, shadow=(4, 6, 6, 0.35))
        for n in range(8):
            ff = (t * 1.2 + n * 0.125) % 1.0
            st.put(Z0.prop("kulka"), 820 + n * 12, 300 + ff * 360, P.rekwizyty + 0.005, h=6, anchor=(0.5, 0.5), tint=(0.95, 0.78, 0.5),
                   shadow=None, alpha=k)
    koniec(st, w, t, dim=0.96)


def s_zastrzezenie(st, w, t, T):
    """Kamera odjeżdża: stosy innych książek i map pustyni; na „Paul is not Shamil” lalka Szamila stoi z boku i kręci głową;
    na „his war” kładzie dłoń na stosie książek (Herbert czerpał z wielu źródeł — księga D4)."""
    kam(st, t, I["zastrzezenie"], CX, 400, lerp(1.4, 1.0, ease(t / T)), 0.8)
    biblioteka_sc(st, t, w, noc=True)
    t_paul, t_war = sl("zastrzezenie", "paul"), sl("zastrzezenie", "war")
    for n, (x, key) in enumerate(((330, "ksiazki"), (520, "mapa_pustyni"), (720, "ksiazki"), (900, "ksiazki"))):
        st.put(J.rek_kz(key), x, STOPY + 4, P.lalki + 0.01 * (n % 2), h=140 if key == "ksiazki" else 120, anchor=(0.5, 1.0), rot=4 * (n % 2 - 0.5))
    krec = math.sin((t - t_paul) * 12) * _bump(t, t_paul + 0.5, 0.6)
    kladzie = ease(pr(t, t_war - 0.3, 0.5))
    K.lalka(st, t, "Szamil", w.szamil, 1060, 290, flip=-1, lean=6 * krec,
            przod=lambda s: K.w_zasiegu(s, (lerp(K.U.Uklad.dlon_z_kata(s, 8)[0], 930, kladzie), lerp(K.U.Uklad.dlon_z_kata(s, 8)[1], STOPY - 130, kladzie))))
    koniec(st, w, t)


def s_dwie_wojny(st, w, t, T):
    """Wydma i góry obok siebie; nad wydmą wschodzi złote słońce, fremeni unoszą ręce; nad górami zbierają się szare chmury
    i pada śnieg."""
    kam(st, t, I["dwie_wojny"], CX, 380, 1.0, 0.8)
    teatr_kz(st, t, w)
    t_won = sl("dwie_wojny", "won")
    st.put(J.glow(), 330, 160, P.slonce, w=700, anchor=(0.5, 0.5), mode="add", alpha=0.25 * ease(pr(t, 0.5, 1.5)), shadow=None)
    for n, key in enumerate(("fremen", "fremen2")):
        K.lalka(st, t, f"fremen {n + 1}", key, 200 + n * 180, 250, flip=1, przod=lambda s, n=n: 10 + 150 * ease(pr(t, t_won + 0.2 * n, 0.4)))
    for n in range(2):
        J.hang(st, J.S("cloud_right", 0.5), 980 + n * 200, 60 + n * 40, P.chmury + 0.01 * n, pr(t, t_won - 0.6 + 0.4 * n, 1.0), t, 970 + n,
               w=420, tint=(0.6, 0.62, 0.68), shadow=(6, 9, 10, 0.3))
    if t > t_won:
        for n in range(10):
            f = (t * 0.25 + n * 0.1) % 1.0
            st.put(Z0.prop("kulka"), 820 + (n * 47) % 460, 120 + f * 560, P.rekwizyty - 0.01, h=8, anchor=(0.5, 0.5), tint=(1, 1, 1), shadow=None)
    koniec(st, w, t)


def s_biala_flaga(st, w, t, T):
    """Szamil na grani podnosi białą flagę (drzewce w dłoni — kontrola); obok cień syna w mundurze rozwiewa się jak dym; Szamil
    opuszcza flagę i patrzy na wydmę."""
    kam(st, t, I["biala_flaga"], 980, 430, lerp(1.2, 1.5, ease(t / T)), 0.8)
    gran_wieczor_sc(st, t, w)
    t_flag, t_son = sl("biala_flaga", "white"), sl("biala_flaga", "son")
    opuszcza = ease(pr(t, po_kw("biala_flaga", 0.2), 0.8))
    szk = K.lalka(st, t, "Szamil", w.szamil, 960, 300, flip=-1, przod=lerp(10, 150, ease(pr(t, t_flag - 1.2, 1.0))) - 120 * opuszcza,
                  lokiec=("gora", "dol"))
    K.w_dloni(st, t, "biała flaga", "flaga_biala", szk, 180, rot=0)
    a = 1 - ease(pr(t, t_son + 0.2, 2.0))
    if a > 0:
        cien(st, t, "dzamal_oficer", 1120, 290, STOPY, P.lalki - 0.01, flip=-1, alpha=a * 0.85)
        dym(st, 1120, STOPY - 200, P.lalki - 0.005, t, t_son + 0.3, r=220, dl=1.8, tint=(0.3, 0.28, 0.28))
    koniec(st, w, t, dim=0.94)


def s_dzieki(st, w, t, T):
    """Kurtyna zasuwa się; na niej szyld „Paper Theatre”; spod kurtyny wychyla się mały robak i chowa się z powrotem (robak:
    puenta); napis w kadrze — bez napisu lektora."""
    kam(st, t, I["dzieki"], CX, CY, 1.0, 0.8, drift=0.0)
    teatr_kz(st, t, w)
    k = ease(pr(t, 0.3, 0.9))
    for strona in (-1, 1):
        przes = (1 - k) * 760
        st.put(J.Z0.kurtyna(strona), CX - 30 * strona + strona * przes, -70, 0.975, w=700, anchor=(1.0 if strona < 0 else 0.0, 0.0),
               shadow=(8 * strona, 0, 14, 0.45))
    J.hang(st, J.tag("Paper Theatre", 56), CX, 280, 0.978, pr(t, 0.9, 0.7), t, 990, h=100, drop=520, shadow=(5, 8, 8, 0.45))
    wys = ease(pr(t, 1.6, 0.5)) * (1 - ease(pr(t, 3.0, 0.4)))
    if wys > 0:
        st.put(J.rek_kz("robak"), 860, 760 - 120 * wys, 0.977, h=200, anchor=(0.5, 0.0), rot=8 * math.sin(t * 4), shadow=(4, 6, 8, 0.4))
    koniec(st, w, t)
