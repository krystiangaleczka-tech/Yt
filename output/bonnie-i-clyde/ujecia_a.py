"""Ujęcia aktów 0–4 filmu „Bonnie and Clyde: The Outlaws Made of Paper”: funkcja `s_<klucz>(st, w, t, T)` na ujęcie.

st — scena (papier.Stage), w — stan świata z początku ujęcia (scena.stan), t — czas od początku ujęcia, T — długość ujęcia.
Rozpiska: docs/filmy/bonnie-i-clyde/ujecia/dane.py. Zapowiedź (zap_*) render składa sam ze skrótów tych ujęć (render.WYCINEK).
"""
import math

from scena import _off, bark, dlon, siegnij, stan_przy  # noqa: E402
from scena import (CX, DROGA_Y, J, P, STOPY, Z0, auto, back, bk, blysk, cien, ciezarowka, clamp, ease, ease_out, eastham, iks, jazda,
                   kam, kulisy, lalka, lerp, miasto, noise, parawan, podpis, pr, preria, punkt, rampa, settle, swiatlo, teatr_gazet,
                   west_dallas, wnetrze, zawieszki, drukarnia)


def koniec(st, w, t, dim=1.0, extra=(1.0, 1.0, 1.0)):
    swiatlo(st, w, t, extra=extra, dim=dim)
    zawieszki(st, t, w)


def _bump(t, t0, d=0.15):
    return max(0.0, 1.0 - abs(t - t0) / d)


def tab(w, t, txt, x, y, t0, dur=2.2):
    """Tabliczka z okrzykiem (słownik znaków 1.20)."""
    podpis(w, t, txt, x, y, t0, dur)


def REV(dl=46):
    """Rewolwer w dłoni lufą do przodu, poziomo, niezależnie od kąta ręki (marker reżysera 19.11 na ujęciu 12: „w tę stronę
    ma być skierowany rewolwer, i w następnych ujęciach też”). Chwyt: kolba (0.3, 0.75)."""
    return (J.rek("rewolwer"), dl * 110 / 180, (0.3, 0.75), 0, False)


def KARABIN(dl=170):
    """Karabin noszony przy nodze lufą w dół (marker reżysera 19.11 na ujęciu 12: „tak ma być skierowana broń, i w następnych
    ujęciach też”); dl — długość w kadrze (arkusz 520 × 90). Do strzału — CEL()."""
    return (J.rek("karabin"), dl * 90 / 520, (0.3, 0.55), 90, False)


def CEL(dl=170):
    """Karabin do strzału: poziomo przed siebie, ręka ok. 90° (tylko w chwili strzału albo celowania)."""
    return (J.rek("karabin"), dl * 90 / 520, (0.3, 0.55), 0, False)


# Chwyty (reżyser 19.11: „musisz poprawić ich umiejscowienie w rękach”): rzecz w dłoni ma kierunek, jaki ma w życiu —
# nie przedłuża ręki jak patyk. Sprawdzone na arkuszu zbliżeń dłoni (scratchpad rece.py).
def KARABIN_PION(dl=170):
    """Karabin pionowo przy boku, lufą w górę (łowcy w krzakach, warta, musztra) — sąsiednie karabiny się nie krzyżują."""
    return (J.rek("karabin"), dl * 90 / 520, (0.3, 0.55), -90, False)


def GAZETA(spr, h, flip):
    """Gazeta czytana przed twarzą: dłonie uniesione ok. 150° trzymają bliższy brzeg, kartka (h ok. 130 przy lalce 300)
    zasłania twarz, a dłoń leży NA kartce (kartka za dłonią — reżyser 19.11: „gazeta z rękami”)."""
    return (spr, h, (0.12 if flip < 0 else 0.88, 0.5), 0, False, 0.02)


def czyta_gazete(st, t, key, x, gazeta, h=300, flip=1.0, hgaz=130, lean=0.0, sink=0.0, p=None, **kw):
    """Postać czyta gazetę: kartka zasłania twarz (środek kartki na środku twarzy), obie dłonie trzymają jej bliższy brzeg
    (kąt rąk liczony z punktu brzegu — Wytyczne 1.28); dłonie leżą na kartce. Zwraca położenie dłoni."""
    fx, fy = punkt(key, x, h, 152, 122, flip=flip, rot=lean)
    if sink:
        fy += ease(sink) * h * 1.12
    szer = hgaz * 360 / 480
    brzeg = (fx + flip * 0.36 * szer, fy)  # bliższy brzeg = po stronie, w którą patrzy postać
    kat, _ = siegnij(key, x, brzeg, h=h, flip=flip, lean=lean, sink=sink)
    st.put(gazeta, fx, fy, (P.lalki + 0.01 if p is None else p), h=hgaz, anchor=(0.5, 0.5), rot=lean, z=0.02)
    return lalka(st, t, key, x, h, flip=flip, lean=lean, sink=sink, p=p, rece=(kat, kat - 6), **kw)


def KULA(dl=210):
    """Kula pod pachą: dłoń na rączce (ok. 45% od góry), górna podpórka pod pachą, dół na ziemi."""
    return (J.rek("kula"), dl, (0.5, 0.45), 0, False)


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
    """Odjazd na Clyde'a; podpis „Clyde Barrow”; za nimi z nitek zjeżdżają nagłówki gazet. Gag (marker reżysera 19.11): Bonnie
    strzela, kula odbija się od brzegów kadru jak w grze i po sekundzie trafia w bak Forda; z baku cieknie paliwo pod auto."""
    kam(st, t, 3, lerp(900, 640, ease(pr(t, 0, 4))), lerp(470, 390, ease(pr(t, 0, 4))), lerp(1.6, 1.0, ease(pr(t, 0, 4))), 0.81)
    teatr_gazet(st, t, w)
    for n, (x, y, nag) in enumerate(((300, 140, "BANK ROBBED"), (640, 110, "POLICE HUNT COUPLE"), (980, 150, "OUTLAW GIRL WITH CIGAR"))):
        J.hang(st, J.gazeta(nag, 30 + n, 360, 300, False), x, y, P.wzgorza, pr(t, 3.0 + 1.3 * n, 1.0), t, 400 + n, w=270, drop=520,
               sway=1.2, strings=(0.2, 0.8))
    auto(st, t, 700, 290)
    out = lalka(st, t, "bonnie", 470, 320, flip=1, lean=-2, rece=(70 if t < 1.2 else 20, 10), trzyma=REV())
    if out and 0.15 <= t < 0.3:
        blysk(st, out[0] + 30, out[1] - 4, P.rekwizyty, t, 0.15, r=120)
    # tor kuli: od lufy, odbicie od górnego i prawego brzegu kadru, w bak (punkt na arkuszu Forda ok. (200, 240))
    # bak z tyłu Forda, z lewej od pasa napisów (pod napisem kałuży nie byłoby widać)
    tor = ((0.15, 520, 512), (0.5, 820, 262), (0.95, 1240, 470), (1.6, 404, 598))
    for (t0, x0, y0), (t1, x1, y1) in zip(tor, tor[1:]):
        if t0 <= t < t1:
            f = (t - t0) / (t1 - t0)
            bx, by = lerp(x0, x1, f), lerp(y0, y1, f)
            fs = max(0.0, f - 0.3)
            st.line([(lerp(x0, x1, fs), lerp(y0, y1, fs)), (bx, by)], P.rekwizyty, width=3, color=(250, 228, 150), alpha=0.85)
            st.put(J.glow(), bx, by, P.rekwizyty + 0.001, w=30, anchor=(0.5, 0.5), mode="add", alpha=0.95, shadow=None, tint=(1.0, 0.9, 0.5))
    for tb, xb, yb in tor[1:]:
        if tb <= t < tb + 0.14:
            st.put(J.glow(), xb, yb, P.rekwizyty, w=110, anchor=(0.5, 0.5), mode="add", alpha=0.9 * (1 - (t - tb) / 0.14), shadow=None,
                   tint=(1.0, 0.85, 0.4))
    if t >= 1.6:  # paliwo z baku: strumyk i rosnąca kałuża (nad rampą i obok pasa napisów)
        st.line([(404, 598), (398, 664)], P.auta + 0.004, width=4, color=(200, 150, 60), alpha=0.9)
        k_ = ease(pr(t, 1.7, 4.0))
        st.put(J.glow(r=256, color=(170, 120, 40)), 360, 668, P.auta + 0.003, w=50 + 200 * k_, sy=0.22, anchor=(0.5, 0.5), alpha=0.85,
               shadow=None)
    lalka(st, t, "clyde", 980, 350, flip=-1, rece=(20, 15), trzyma=KARABIN())
    podpis(w, t, "Clyde Barrow", 980, 240, 1.0, 3.0)
    tab(w, t, "…", 700, 470, 4.6, 1.6)
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
    """Opuszczone mieszkanie w Joplin: policjant wchodzi drzwiami, rozgląda się, podnosi z podłogi aparat wysoko, do oczu,
    a z dołu aparatu wysuwa się w dół klisza (marker reżysera 19.11: „podnosi aparat wyżej, a film z kamery wylatuje od dołu
    w dół”)."""
    kam(st, t, 4, lerp(760, 820, ease(t / T)), lerp(400, 470, ease(pr(t, 2.0, 4.0))), lerp(1.0, 1.45, ease(pr(t, 2.0, 4.0))), 0.81)
    st.dof = 1.0
    _mieszkanie_joplin(st, w, t)
    x, _ = jazda(t, 0.3, 2.2, 1120, 820)
    schyl = ease(pr(t, 3.0, 0.7)) * (1 - ease(pr(t, 4.2, 0.6)))
    wyzej = ease(pr(t, 4.2, 0.7))
    out = lalka(st, t, "detektyw", x, 330, flip=-1, lean=-18 * schyl,
                rece=(20 + 70 * schyl + 40 * ease(pr(t, 3.6, 0.6)) + 70 * wyzej, 10), hop=6 * (t < 2.5))
    podnies = ease(pr(t, 3.6, 0.5))
    ax, ay = (720, 702) if podnies <= 0 or not out else (lerp(720, out[0], podnies), lerp(702, out[1], podnies))
    st.put(J.rek("aparat"), ax, ay, P.lalki + 0.02, h=50, anchor=(0.5, 0.5))
    if t > 5.0 and out:
        f = ease(pr(t, 5.0, 1.4))
        st.put(J.rek("klisza"), ax - 4, ay + 22, P.lalki + 0.025, h=24, anchor=(0.0, 0.5), sx=0.12 + 0.88 * f, rot=90 + 6 * math.sin(t * 3))
    koniec(st, w, t)


def s_hak_joplin_rzeczy(st, w, t, T):
    s_joplin_rzeczy(st, w, t, T)


def s_zdjecie(st, w, t, T):
    """Klatka z kliszy ożywa (marker reżysera 19.11: „skąd ta ręka? tu ma stać gościu, do którego Bonnie podchodzi, bierze mu
    z ręki cygaro i odchodzi z powrotem, rewolwer daje do pasa i pali cygaro”): przy Fordzie stoi chłopak z cygarem; Bonnie
    podchodzi, bierze cygaro, wraca, kręci rewolwerem i wsuwa go za pasek, wkłada cygaro do ust; błyska flesz."""
    kam(st, t, 5, 700, 470, lerp(1.22, 1.32, ease(t / T)), 0.81)
    st.dof = 1.3
    miasto(st, t, w, fasady=(("garaz", 760),), tyl=(("dom", 200), ("dom", 1150)), kul=False)
    auto(st, t, 700, 250, kolor="szary")
    tam = ease(pr(t, 0.4, 1.3))
    wraca = ease(pr(t, 2.3, 1.2))
    bx = lerp(lerp(470, 870, tam), 470, wraca)
    idzie = (0.4 < t < 1.7) or (2.3 < t < 3.5)
    fl = 1 if t < 2.3 else -1 if t < 3.5 else 1
    # chłopak (W.D.) z cygarem w wyciągniętej dłoni
    wd_kat = 75 * ease(pr(t, 1.2, 0.4)) * (1 - ease(pr(t, 2.2, 0.3)))
    lalka(st, t, "wd", 1010, 280, flip=-1, rece=(wd_kat, 0),
          trzyma=(J.rek("cygaro"), 10, (0.15, 0.5), 0, False) if t < 2.05 else None)
    # Bonnie: tylną ręką bierze cygaro z dłoni chłopaka, przednią trzyma rewolwer
    wd_dlon = dlon("wd", 1010, wd_kat, h=280, flip=-1)
    if 1.6 <= t < 2.3:
        kat_t, _ = siegnij("bonnie", bx, wd_dlon, h=300, flip=1)
    else:
        kat_t = 20
    ma_w_ustach = t >= 4.4
    krec = pr(t, 3.6, 0.6)
    za_pasem = t >= 4.25
    rv = REV()
    trz = None if za_pasem else (rv[0], rv[1], rv[2], 720 * ease(krec), False)
    out = lalka(st, t, "bonnie_cygaro" if ma_w_ustach else "bonnie", bx, 300, flip=fl, lean=-6 * (t > 4.6), lift=10 * (t > 4.6),
                rece=(20 + 25 * (3.6 < t < 4.25), kat_t), trzyma=trz, hop=5 * idzie)
    if 2.05 <= t < 4.4:  # cygaro w tylnej dłoni Bonnie (w ustach od 4,4 s — podmiana w jednej klatce)
        hx, hy = dlon("bonnie", bx, kat_t, h=300, flip=fl, ktora="tyl")
        st.put(J.rek("cygaro"), hx, hy, P.lalki + 0.012, h=10, anchor=(0.15, 0.5), sx=fl, z=0.06)
    if za_pasem:  # rewolwer za paskiem: kolbą do góry, przy biodrze
        px_, py_ = punkt("bonnie_cygaro" if ma_w_ustach else "bonnie", bx, 300, 182, 420, flip=fl)
        st.put(rv[0], px_, py_, P.lalki + 0.015, h=rv[1], anchor=(0.3, 0.75), rot=100 * fl, sx=fl)
    if ma_w_ustach:  # dym z cygara
        ux, uy = punkt("bonnie_cygaro", bx, 300, 176, 160, flip=fl)
        for m in range(3):
            f = ((t - 4.5) * 0.6 + m / 3) % 1.0
            if t > 4.5:
                st.put(J.glow(r=256, color=(220, 220, 220)), ux + 30 * fl + 20 * f, uy - 20 - 110 * f, P.lalki + 0.03, w=24 + 50 * f,
                       anchor=(0.5, 0.5), alpha=0.5 * (1 - f), shadow=None)
    blysk(st, 640, 360, 0.95, t, 5.9, r=2200, kolor=(1.0, 1.0, 0.95), dl=0.18)
    fl_ = 5.9 <= t < 6.12
    if fl_:
        st.dim = 1.6
    koniec(st, w, t, dim=1.0 if not fl_ else 1.7)


def s_hak_pomost(st, w, t, T):
    """Pomost: wielka strona gazety przewraca się przez cały kadr jak kurtyna (szelest papieru)."""
    kam(st, t, 6, 640, 360, 1.0, 0.9, drift=0.2)
    teatr_gazet(st, t, w)
    k = ease(pr(t, 0.1, T - 0.3))
    sx = math.cos(math.pi * k)
    # po przewróceniu widać drugą stronę (inną gazetę), nie lustrzane „EXTRA!” (przegląd 19.11)
    strona = J.gazeta("EXTRA!", 50, 640, 760) if sx >= 0 else J.gazeta("WANTED", 51, 640, 760)
    st.put(strona, CX, 760, 0.93, h=900, anchor=(0.0 if sx >= 0 else 1.0, 1.0), sx=max(0.02, abs(sx)),
           tint=(1.0 - 0.3 * abs(math.sin(math.pi * k)),) * 3)
    koniec(st, w, t)


def s_prasa(st, w, t, T):
    """Wałki maszyny drukarskiej kręcą się, wylatują setki gazet ze zdjęciem Bonnie z cygarem i odlatują nad dachy."""
    kam(st, t, 7, 640, 380, lerp(1.05, 0.95, ease(t / T)), 0.72, shake=1.2)
    drukarnia(st, t, w, obrot=t * 220)
    # gag 32 (GAGI.md): po „gun girl” jedna gazeta wraca z wiatrem i przykleja się drukarzowi do twarzy; po chwili ją odkleja
    odkl = ease(pr(t, 8.0, 0.4))
    lalka(st, t, "drukarz", 1000, 310, flip=-1, rece=(70 + 15 * math.sin(t * 5) * (t < 6.6) + 80 * _bump(t, 8.0, 0.5), 40))
    fg = pr(t, 6.5, 0.4)
    if fg > 0:
        gx, gy = punkt("drukarz", 1000, 310, 160, 140, flip=-1)
        st.put(J.gazeta("OUTLAW GIRL WITH CIGAR", 9, 360, 480), lerp(1300, gx, ease(fg)) - 60 * odkl, lerp(200, gy, ease(fg)) + 260 * odkl * odkl,
               P.lalki + 0.03, h=lerp(110, 90, fg), anchor=(0.5, 0.5), rot=lerp(-60, 4, ease(fg)) + 60 * odkl)
    tab(w, t, "MMPH!", 1000, 250, 7.0, 1.0)
    for n in range(14):
        f = ((t * 0.6 + n / 14) % 1.0)
        if t < 0.4 + n * 0.12:
            continue
        x = 820 + f * 900 + 40 * math.sin(n)
        y = 300 - f * 520 + 80 * math.sin(f * 3 + n)
        st.put(J.gazeta("OUTLAW GIRL WITH CIGAR", n % 4, 360, 480), x, y, P.drzewa + 0.02 * (n % 3), h=110, anchor=(0.5, 0.5),
               rot=f * 200 + n * 30, sx=max(0.08, abs(math.cos(f * 6 + n))), shadow=(4, 6, 6, 0.3))  # bez lustrzanych napisów
    koniec(st, w, t)


def s_hak_cygaro(st, w, t, T):
    """Bonnie przy aucie czyta gazetę ze swoim zdjęciem; cygaro opada i wypada z ust; gazeta znika w jednej klatce, a w dłoni
    jest zgnieciona kulka (bez przemiany jednej rzeczy w drugą — marker reżysera 19.11); Bonnie wyrzuca kulkę; tabliczka
    „I DON'T SMOKE CIGARS!”; Bonnie raz podskakuje z przerażenia."""
    kam(st, t, 8, 640, 480, 1.6, 0.81)
    st.dof = 1.4
    w.noc = 0.5
    preria(st, t, w, slupy=False, kul=False)
    auto(st, t, 900, 250, kolor="szary")
    rzut = ease(pr(t, 5.0, 0.25)) * (1 - ease(pr(t, 5.25, 0.4)))
    skok = 46 * math.sin(math.pi * pr(t, 6.1, 0.35))
    if t < 3.6:
        trz = (J.gazeta("OUTLAW GIRL WITH CIGAR", 2, 360, 480), 150, (0.3, 0.6), -8, False)
        rece = (95, 80)
    elif t < 5.05:
        trz = (J.rek("kulka"), 30, (0.5, 0.5), 0, False)
        rece = (75 + 70 * rzut, 40)
    else:
        trz, rece = None, (40 + 70 * rzut, 30)
    lalka(st, t, "bonnie", 600, 300, flip=1, rece=rece, trzyma=trz, lift=skok)
    fk = pr(t, 5.05, 0.8)
    if 0 < fk < 1:
        st.put(J.rek("kulka"), lerp(690, 1250, fk), 430 - 180 * math.sin(math.pi * fk) + 150 * fk, P.lalki + 0.03, h=30, anchor=(0.5, 0.5),
               rot=600 * fk)
    # gag 2 (GAGI.md): cygaro z gazetowej legendy smętnie opada w jej ustach jak zwiędły kwiat, potem Bonnie je wypluwa
    f = pr(t, 2.6, 0.7)
    ux, uy = punkt("bonnie", 600, 300, 176, 160, lift=skok)
    if t < 2.6:
        st.put(J.rek("cygaro"), ux - 2, uy, P.lalki + 0.04, h=12, anchor=(0.04, 0.5), rot=4 + 62 * ease(pr(t, 1.0, 1.4)))
    if 0 < f < 1:
        st.put(J.rek("cygaro"), ux + 60 * f, uy + 200 * f * f, P.lalki + 0.04, h=12, anchor=(0.5, 0.5), rot=400 * f)
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
    # gag 31 (GAGI.md, W1 „pusta kasa” — zasiew): na „almost nothing” mały Clyde otwiera blaszane pudełko na obiad, wylatuje ćma
    pud = ease(pr(t, 10.2, 0.5))
    out_c = lalka(st, t, "clyde_maly", lerp(640, 760, wy), 200, 1.0, lean=lerp(85, 0, wy), lift=-40 * (1 - wy),
                  rece=(lerp(80, 160, ease(pr(t, 6.0, 0.8))) * (1 - ease(pr(t, 7.4, 0.6))) + 75 * pud,
                        lerp(20, 150, ease(pr(t, 6.0, 0.8))) * (1 - ease(pr(t, 7.4, 0.6)))), p=P.lalki,
                  trzyma=(J.rek("kasetka"), 34, (0.5, 0.3), 0, False) if pud > 0 else None)
    fc = pr(t, 11.3, 2.4)
    if out_c and 0 < fc < 1:
        st.put(J.rek("cma"), out_c[0] + 140 * fc + 25 * math.sin(fc * 18), out_c[1] - 10 - 300 * fc, P.rekwizyty, h=50, anchor=(0.5, 0.5),
               sx=0.3 + 0.7 * abs(math.sin(t * 22)), rot=10 * math.sin(t * 7))
    if t > 11.5:
        tab(w, t, "…", 820, 300, 11.6, 1.8)
    if t > 6.2:
        tab(w, t, "YAWN", 800, 330, 6.2, 1.6)
    koniec(st, w, t)


def s_indyki(st, w, t, T):
    """Ciężarówka z gdaczącymi indykami stoi przy drodze; nastoletni Clyde i Buck siedzą z tyłu razem z indykami; zza rogu
    wychodzi policjant z gwizdkiem, „STOP!”; chłopcy zeskakują na ziemię i podnoszą ręce, indyki wyfruwają (markery reżysera
    19.11: „podstaw tych ludzi tu na aucie z tyłu razem z tymi indykami”, „tu mają zeskoczyć”)."""
    kam(st, t, 11, 640, 380, 1.0, 0.76)
    west_dallas(st, t, w, woz=False)
    x = 300
    ciezarowka(st, t, x, 210)
    px, _ = jazda(t, 1.6, 1.2, 1400, 1080)
    for n in range(4):
        uc = ease(pr(t, 3.4 + 0.2 * n, 1.2))
        ix, iy = x - 110 + 40 * n + 300 * uc * (1 if n % 2 else -0.6), 600 - 30 * math.sin(t * 9 + n) * (uc > 0) - 260 * uc
        irot, ip = 20 * uc * (1 if n % 2 else -1) + 6 * math.sin(t * 7 + n), P.auta + 0.004
        if n == 3:  # gag 3 (GAGI.md): ten indyk ląduje na czapce policjanta i zostaje
            lad = ease(pr(t, 4.5, 0.6))
            hx, hy = punkt("policjant", px, 320, 150, 0)
            ix, iy = lerp(ix, hx - 4, lad), lerp(iy, hy + 36, lad) - 60 * math.sin(math.pi * lad)
            irot, ip = lerp(irot, 4 * math.sin(t * 5), lad), (P.lalki + 0.03 if lad > 0.5 else ip)
        st.put(J.zwierze("indyk"), ix, iy, ip, h=70, anchor=(0.5, 1.0), rot=irot)
    # chłopcy na pace: siedzą (biodra na podłodze paki, ok. y 600), zeskakują łukiem na ziemię po lewej i podnoszą ręce
    for key, h, sx_, lx, t0 in (("buck", 300, x - 150, 110, 3.55), ("clyde_nastolatek", 270, x - 75, 190, 3.4)):
        sk = pr(t, t0, 0.5)
        rece = (160, 160) if t > t0 + 0.8 else (40 + 50 * math.sin(t * 3 + h), 20)
        if sk <= 0:
            lalka(st, t, key, sx_, h, y=600 + 0.383 * h, flip=1, p=P.auta + 0.002, rece=rece, siedzi=True, shadow=None)
        else:
            lalka(st, t, key, lerp(sx_, lx, sk), h, y=lerp(600 + 30, STOPY, sk) - 90 * math.sin(math.pi * sk), flip=-1 if sk < 1 else 1,
                  p=P.lalki + 0.005, rece=rece, lean=-14 * math.sin(math.pi * sk))
    out = lalka(st, t, "policjant", px, 320, flip=-1, rece=(40 + 90 * ease(pr(t, 2.7, 0.3)), 10), hop=5 * (t < 2.9))
    if out and t > 2.7:
        st.put(J.rek("gwizdek"), out[0] - 10, out[1] - 30, P.lalki + 0.03, h=16, anchor=(0.5, 0.5))
    tab(w, t, "STOP!", 1080, 220, 2.9, 2.0)
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


def s_poezja(st, w, t, T):
    """Pomost z historii Clyde'a do historii Bonnie (reżyser 19.11: „dlaczego z ujęcia o indykach robi się nagle ślub?”):
    Cement City, szkoła i kominy cementowni; piętnastoletnia Bonnie na szkolnym podium recytuje z zeszytu i wznosi rękę jak
    aktorka; z góry kadru spada indyk, który uciekł w poprzednim ujęciu, i siada jako jedyna widownia (1.21: wyskok z kadru →
    spadnięcie w następnym ujęciu); na „stage” Bonnie się kłania, indyk gulgocze."""
    kam(st, t, 131, 640, 430, lerp(1.02, 1.12, ease(t / T)), 0.78)
    w.zawieszki = [("Cement City, 1926", 640, 150, pr(t, 0.9, 1.0))]
    for n, x in enumerate((180, 1120)):  # kominy cementowni za szkołą
        Z0.rise(st, J.komin(), x, 600, P.gory_dal, bk(w, 0.1 + 0.05 * n), t, 540 + n, h=360, wob=0.0, haze=0.35)
    # podium z boku szkoły: wzniesiona ręka Bonnie nie zasłania szyldu
    miasto(st, t, w, fasady=(("szkola", 780),), tyl=(("dom", 200), ("dom", 1200)), chodnik=True)
    st.put(J.rek("podium"), 400, STOPY, P.lalki + 0.02, h=130, anchor=(0.5, 1.0))
    uklon = ease(pr(t, 6.1, 0.35)) * (1 - ease(pr(t, 6.9, 0.4)))
    lalka(st, t, "bonnie", 400, 290, y=STOPY - 112, flip=1, lean=24 * uklon - 4,
          rece=(75, 150 + 12 * math.sin(t * 3) - 120 * uklon), trzyma=(J.rek("zeszyt"), 40, (0.5, 0.5), 0, False))
    # indyk z ujęcia „indyki” spada z góry kadru i zostaje jako widownia, przodem do Bonnie (nad rampą)
    fi = pr(t, 1.6, 0.7)
    if fi > 0:
        lad = fi >= 1
        st.put(J.zwierze("indyk"), lerp(680, 620, fi), lerp(-150, 652, min(1.0, fi * fi)) - (14 * back(pr(t, 2.3, 0.4), 2.0) - 14) * lad,
               P.lalki + 0.03, h=110, anchor=(0.5, 1.0), sx=-1, rot=(360 * (1 - fi)) if not lad else 5 * math.sin(t * 7) * (6.6 < t < 7.3))
    tab(w, t, "GOBBLE!", 640, 440, 6.7, 1.3)
    koniec(st, w, t)


def s_slub(st, w, t, T):
    """Piętnastoletnia Bonnie i Roy Thornton pod łukiem z papierowych kwiatów; przy „married” pod kwiatami zjeżdża wstęga
    „HAPPY EVER AFTER” po łuku, przy „tattooed in two hearts” nad łukiem tabliczka-tatuaż z dwoma sercami (marker reżysera
    19.11: tabliczka zasłaniała górę łuku — „znika to i po łuku napis pod tymi kwiatkami Happy Ever After”)."""
    kam(st, t, 13, 640, 360, lerp(1.0, 1.08, ease(t / T)), 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(240, 1040))
    for n in range(9):
        a = math.pi * (0.1 + 0.8 * n / 8)
        J.hang(st, J.rek("kwiaty"), 640 - 260 * math.cos(a), 470 - 300 * math.sin(a), P.drzewa, bk(w, 0.3 + 0.05 * n), t, 440 + n, h=70,
               drop=400, sway=0.6, string=False)
    # pocałunek (marker reżysera 19.11: „zbliżają się i dają se buzi i wracają do tych pozycji”) — po „married a boy named Roy”
    buzi = ease(pr(t, 4.0, 0.45)) * (1 - ease(pr(t, 5.0, 0.45)))
    # zbliżają się tylko tyle, żeby głowy się zetknęły (Roy pochyla się do niższej Bonnie) — dalej jedno zasłaniało drugie
    lalka(st, t, "bonnie_slub", 560 + 22 * buzi, 270, flip=1, rece=(30 + 40 * buzi, 10), lean=6 * buzi, lift=8 * buzi)
    lalka(st, t, "roy", 730 - 26 * buzi, 320, flip=-1, rece=(30 + 40 * buzi, 10), lean=-16 * buzi)
    if 4.4 < t < 5.2:
        st.put(J.serce(), 645, 330 - 40 * pr(t, 4.4, 0.8), P.rekwizyty, h=34 * back(pr(t, 4.4, 0.3), 1.6), anchor=(0.5, 0.5), shadow=None)
    # gag 4 (GAGI.md, W3 „nitka teatru”, pomysł reżysera): na „a very permanent decision” pęka prawa nitka, wstęga obraca się
    # na lewej i zwisa krzywo do końca; Roy zerka w górę
    peka = pr(t, 7.7, 0.7)
    J.hang(st, J.wstega_luk(), 640 - 0.3 * 520, 238, P.drzewa + 0.01, pr(t, 1.9, 1.0), t, 451, w=520, drop=420, sway=0.4,
           anchor=(0.2, 0.0), strings=(0.2,) if peka > 0 else (0.2, 0.8), rot0=16 * back(peka, 1.4))
    tab(w, t, "?", 760, 200, 8.0, 1.6)
    J.hang(st, J.tatuaz(), 640, 34, P.rekwizyty, pr(t, 5.5, 1.0), t, 450, w=240, drop=420)
    podpis(w, t, "Roy Thornton", 730, 150, 3.3, 1.9)  # przy „Roy Thornton”, zjeżdża, zanim spadnie tabliczka
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
    """Bonnie w fartuszku trzyma dzbanek za ucho i nalewa kawę do filiżanki na ladzie (marker reżysera 19.11: „ta ma mieć to
    w rękach i ma lać kawę do tej filiżanki”); klient czyta gazetę trzymaną w dłoniach; Bonnie odstawia dzbanek z hukiem."""
    hk = 2.95 < t < 3.25
    kam(st, t, 15, 640, 390, 1.15, 0.8, shake=3.0 * hk)
    wnetrze(st, t, w, sciana="paski", okna=(260, 1020), meble=(("lada", 640, 150, P.drzewa),))
    blat = STOPY - 150
    czyta_gazete(st, t, "przechodzien2", 820, J.gazeta("DEPRESSION DEEPENS", 5, 360, 480), h=300, flip=-1)
    filx = 700
    st.put(J.rek("kubek"), filx, blat + 2, P.drzewa + 0.01, h=34, anchor=(0.5, 1.0))
    # dzbanek (arkusz 150 × 150, h 60): ucho (0.107, 0.56), dzióbek o (52.8, -12.8) od ucha; przechył 45° → dzióbek nad filiżanką
    ucho = (filx - 56, blat - 96)
    bx = stan_przy("bonnie_kelnerka", ucho, 85, h=290, flip=1)
    kat_lej, _ = siegnij("bonnie_kelnerka", bx, ucho, h=290, flip=1)
    podnosi = ease(pr(t, 0.6, 0.6)) * (1 - ease(pr(t, 2.4, 0.45)))
    przechyl = 45 * ease(pr(t, 1.2, 0.3)) * (1 - ease(pr(t, 2.2, 0.3)))
    odstawiony = t >= 2.95
    patrzy = -1 if 7.2 < t < 8.0 else 1  # odprowadza wzrokiem toczące się zielsko
    out = lalka(st, t, "bonnie_kelnerka", bx, 290, flip=patrzy, rece=(lerp(25, kat_lej, podnosi), 10),
                trzyma=None if odstawiony else (J.rek("dzbanek"), 60, (0.107, 0.56), przechyl, False))
    if out and 1.45 < t < 2.3:  # strumień kawy z dzióbka do filiżanki
        sx_, sy_ = _off(52.8, -12.8, przechyl)
        st.line([(out[0] + sx_, out[1] + sy_), (filx, blat - 30)], P.drzewa + 0.012, width=3, color=(86, 54, 30), alpha=0.95)
    if odstawiony:  # dzbanek stoi na ladzie tam, gdzie go odstawiła
        st.put(J.rek("dzbanek"), bx + 70, blat + 2, P.drzewa + 0.012, h=60, anchor=(0.36, 1.0), rot=-6 * _bump(t, 3.0, 0.2))
    # gag 5 (GAGI.md): na „something exciting” przez kawiarnię toczy się kula stepowego zielska; Bonnie odprowadza ją wzrokiem
    tz = pr(t, 7.0, 2.6)
    if 0 < tz < 1:
        zx = lerp(-120, 1400, tz)
        st.put(J.rek("zielsko"), zx, 566 - 90 * abs(math.sin(tz * 9)), P.lalki + 0.03, h=86, anchor=(0.5, 1.0), rot=tz * 900)
    tab(w, t, "SIGH…", bx, 230, 2.4, 1.8)
    koniec(st, w, t)


def s_kuchnia(st, w, t, T):
    """W ciasnej kuchni Bonnie miesza kakao; drzwiami wchodzi Clyde w kapeluszu i uchyla go; z nitki zjeżdżają dwa serduszka."""
    kam(st, t, 16, 640, 390, 1.1, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(("kuchenka", 420, 170, None), ("stol", 760, 140, None)))
    # garnek przed łyżką: łyżka znika w garnku, kiedy Bonnie miesza (było: łyżka sterczała z ręki obok garnka)
    st.put(J.rek("garnek"), 420, 544, P.lalki + 0.03, h=50, anchor=(0.5, 1.0))
    out = lalka(st, t, "przyjaciolka", 640, 290, flip=1, rece=(10, 0))
    lalka(st, t, "bonnie", 500, 290, flip=-1, rece=(113 + 5 * math.sin(t * 6), 0), trzyma=(J.rek("lyzka"), 50, (0.5, 0.9), 180, False))
    cx, _ = jazda(t, 1.2, 1.8, 1180, 900)
    lalka(st, t, "clyde", cx, 320, flip=-1, rece=(lerp(0, 160, ease(pr(t, 3.2, 0.4))) * (1 - ease(pr(t, 4.2, 0.4))), 0), hop=5 * (t < 3.0))
    for n in range(2):
        # gag 6 (GAGI.md): na „he was arrested” serduszka odjeżdżają w górę, a na tej samej nitce zjeżdżają kajdanki
        J.hang(st, J.serce(), 620 + 90 * n, 160 + 20 * n, P.rekwizyty, pr(t, 4.4 + 0.3 * n, 1.0) * (1 - pr(t, 8.2 + 0.1 * n, 0.5)), t,
               460 + n, h=60, drop=420)
    J.hang(st, J.rek("kajdanki"), 665, 170, P.rekwizyty, pr(t, 8.7, 0.9), t, 470, h=64, drop=420)
    koniec(st, w, t)


def s_areszt(st, w, t, T):
    """Do kuchni wchodzi policjant i zakuwa Clyde'a w kajdanki; Bonnie z łyżką woła „HEY!”, biegnie za nimi do drzwi, drzwi
    trzaskają jej przed nosem (reżyser 19.11: ujęcie było „turbo krótkie” — +2 s)."""
    kam(st, t, 17, 700, 390, 1.1, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(("kuchenka", 420, 170, None), ("stol", 760, 140, None)))
    st.put(J.rek("garnek"), 420, 544, P.lalki + 0.03, h=50, anchor=(0.5, 1.0))
    biegnie = ease(pr(t, 3.5, 0.9))
    lalka(st, t, "bonnie", lerp(500, 930, biegnie), 290, flip=1, rece=(70 + 60 * _bump(t, 4.3, 0.5), 0), hop=5 * (3.5 < t < 4.4),
          lean=-10 * _bump(t, 4.75, 0.25), trzyma=(J.rek("lyzka"), 50, (0.5, 0.9), 180, False))
    px, _ = jazda(t, 0.0, 0.8, 1200, 1000)
    wyprow = ease(pr(t, 1.8, 1.4))
    lalka(st, t, "policjant", px + 160 * wyprow, 320, 1.0 - ease(pr(t, 3.2, 0.4)), flip=-1 if wyprow == 0 else 1, rece=(80, 0),
          hop=5 * (t < 0.8 or 1.8 < t < 3.2))
    out = lalka(st, t, "clyde", 880 + 180 * wyprow, 320, 1.0 - ease(pr(t, 3.0, 0.4)), flip=1 if wyprow > 0 else -1, rece=(40, 40),
                hop=5 * (1.8 < t < 3.2))
    if out and t > 0.9:
        st.put(J.rek("kajdanki"), out[0], out[1], P.lalki + 0.03, h=26, anchor=(0.5, 0.5))
    tab(w, t, "HEY!", 500, 240, 1.0, 2.0)
    tab(w, t, "…", 930, 250, 4.9, 1.2)
    koniec(st, w, t)


def s_waco(st, w, t, T):
    """Wnętrze aresztu w Waco: Bonnie od razu podaje przez kraty pistolet spod płaszcza (przemyciła go w ujęciu „waco_przed”);
    strażnik ziewa i zasypia; na „Clyde broke out” Clyde otwiera drzwi celi i wychodzi z kadru; Bonnie odchodzi; strażnik budzi
    się przed pustą celą, „?!”."""
    kam(st, t, 18, 660, 380, 1.15, 0.8)
    wnetrze(st, t, w, sciana="tynk", meble=(("krzeslo", 1080, 170, None),), zarowki=(900,), noc_za_oknem=True)
    spi = 1.6 < t < 6.2
    lalka(st, t, "straznik", 1080, 310, flip=1 if t < 6.2 else -1, lean=-6 * math.sin(t * 1.2) + 14 * spi,
          rece=(150 * ease(pr(t, 0.5, 0.4)) * (1 - ease(pr(t, 1.3, 0.4))), 0))
    tab(w, t, "YAWN", 1080, 200, 0.5, 1.1)
    if spi:
        tab(w, t, "ZZZ", 1120, 220, 1.7, 4.3)
    tab(w, t, "?!", 1060, 220, 6.3, 1.8)
    otw = ease(pr(t, 2.2, 0.6))
    st.put(J.kraty(360, 640), 455, 712, P.drzewa, h=470, anchor=(0.0, 1.0))
    st.put(J.kraty(200, 640), 719, 712, P.drzewa, h=470, anchor=(0.0, 1.0), sx=1 - 0.8 * otw)
    wyj = pr(t, 2.6, 2.0)
    cx = lerp(640, 800, ease(min(1.0, wyj * 2))) + 600 * max(0.0, wyj - 0.5) * 2
    na_zewnatrz = wyj > 0.45
    lalka(st, t, "clyde_wiezien", cx, 320, flip=-1 if wyj <= 0 else 1, rece=(70 * ease(pr(t, 1.2, 0.4)) * (wyj <= 0) + 20, 0),
          p=P.lalki if na_zewnatrz else P.wzgorza + 0.02, hop=5 * (0 < wyj < 1),
          trzyma=(J.rek("rewolwer"), 28, (0.3, 0.75), 90, False) if t > 1.3 else None)
    d = ease(pr(t, 0.3, 0.8)) * (1 - ease(pr(t, 1.4, 0.4)))
    odchodzi = ease(pr(t, 4.8, 1.6))
    lalka(st, t, "bonnie", lerp(430, -150, odchodzi), 290, flip=1 if odchodzi <= 0 else -1, rece=(lerp(10, 95, d), 0),
          trzyma=REV() if t < 1.3 else None, hop=5 * (0 < odchodzi < 1))
    koniec(st, w, t)


def s_waco_przed(st, w, t, T):
    """Ujęcie pośrednie (reżyser 19.11: „Bonnie jest w kawiarni, nagle jest w więzieniu — musi być jakieś ujęcie pomiędzy”):
    ulica w Waco przed aresztem, zawieszka „Waco, Texas, 1930”; Bonnie podchodzi, rozgląda się, chowa rewolwer pod płaszcz
    (ręka do biodra, rewolwer znika), poprawia beret i z niewinną miną wchodzi do środka; „♪”."""
    kam(st, t, 132, 640, 420, lerp(1.0, 1.08, ease(t / T)), 0.78)
    w.zawieszki = [("Waco, Texas, 1930", 640, 130, pr(t, 0.3, 1.0))]
    miasto(st, t, w, fasady=(("dom", 260), ("areszt", 760)), tyl=(("dom", 1180),), chodnik=True)
    bx = lerp(-120, 520, ease(pr(t, 0.4, 2.0))) + lerp(0, 230, ease(pr(t, 5.6, 1.0)))
    rozglada = 2.5 < t < 3.4
    chowa = ease(pr(t, 3.6, 0.4))
    znika = t > 4.0
    alpha = 1.0 - ease(pr(t, 6.3, 0.5))  # wchodzi w drzwi
    lalka(st, t, "bonnie", bx, 290, flip=-1 if rozglada else 1, alpha=alpha,
          rece=(lerp(60, 10, chowa) if not znika else 10 + 140 * _bump(t, 4.8, 0.4), 0), hop=5 * (t < 2.4 or 5.6 < t < 6.6),
          trzyma=REV() if not znika else None)
    if rozglada:
        tab(w, t, "…", bx, 230, 2.6, 0.8)
    tab(w, t, "♪", bx + 40, 230, 4.6, 1.4)
    koniec(st, w, t)



def s_ohio(st, w, t, T):
    """Tydzień później, Middletown w Ohio: Clyde przechadza się po peronie i gwiżdże; z obu stron wchodzą policjanci, „OH NO”;
    policjant wskazuje więźniarkę z kratami: „BACK TO TEXAS!” (reżyser 19.11: „policjant mówi you will go to texas! i wskazuje
    na klatkę”) i prowadzą go do niej; +2 s."""
    kam(st, t, 19, 700, 380, 1.0, 0.76)
    w.zawieszki = [("One week later", 640, 120, pr(t, 0.2, 0.9) * (1 - pr(t, 2.2, 0.4)))]
    miasto(st, t, w, fasady=(("dworzec", 600),), tyl=(("dom", 160), ("dom", 1120)))
    # więźniarka: czarny Ford z kratami w tylnym oknie
    wx_ = 1130
    auto(st, t, wx_, 220, kolor="czarny", napis="POLICE")
    k_ = 220 / 360.0
    st.put(J.kraty(160, 72, krok=26), wx_ + (218 - 450) * k_, DROGA_Y + (126 - 356) * k_, P.auta + 0.002, h=40, anchor=(0.5, 0.5))
    prowadza = ease(pr(t, 4.4, 1.8))
    cx = 560 + 70 * math.sin(min(t, 2.4) * 0.8) + 300 * prowadza
    lalka(st, t, "clyde", cx, 320, flip=1 if t > 4.4 else math.copysign(1, math.cos(min(t, 2.4) * 0.8)),
          rece=(160, 160) if t > 2.8 else (10, 0), hop=4 * (t < 2.4 or 4.4 < t < 6.2))
    if t < 2.4:
        tab(w, t, "♪", cx + 40, 230, 1.0, 1.6)
    lx, _ = jazda(t, 1.4, 1.2, -100, 300)
    rx, _ = jazda(t, 1.5, 1.2, 1400, 840)
    lalka(st, t, "policjant", lx + 300 * prowadza, 320, flip=1, rece=(60, 0), hop=5 * (t < 2.6 or 4.4 < t < 6.2))
    wskazuje = ease(pr(t, 3.3, 0.3))
    lalka(st, t, "policjant2", rx + 120 * prowadza, 330, flip=-1 if wskazuje < 0.5 else 1, rece=(60 + 35 * wskazuje, 0),
          hop=5 * (t < 2.7 or 4.4 < t < 6.2))
    tab(w, t, "OH NO", cx, 210, 2.6, 1.6)
    tab(w, t, "BACK TO TEXAS!", 980, 240, 3.5, 2.2)
    koniec(st, w, t)


def s_eastham(st, w, t, T):
    """Eastham: więźniowie w pasiakach okopują bawełnę motykami, każdy w swoim rytmie (motyka od dłoni w dół, ostrze uderza
    w ziemię przed stopami); strażnik siedzi na koniu i jedzie wzdłuż rzędu; słońce praży."""
    kam(st, t, 20, 640, 380, lerp(0.98, 1.08, ease(t / T)), 0.76)
    eastham(st, t, w)
    for n, (x, key) in enumerate(((200, "wiezien"), (380, "clyde_wiezien"), (560, "wiezien2"), (920, "wiezien"), (1100, "wiezien2"))):
        tempo = 2.0 + 0.4 * n
        mach = 0.5 + 0.5 * math.sin(t * tempo + n * 1.3)
        lalka(st, t, key, x, 300, bk(w, 0.6 + 0.05 * n), flip=1, lean=8 * mach, rece=(35 + 30 * mach, 25 + 25 * mach), p=P.drzewa + 0.01,
              trzyma=(J.rek("motyka"), 170, (0.5, 0.03), -(18 + 22 * mach), False))
    kx = 1300 - (t / T) * 900
    st.put(J.zwierze("kon", int(t * 4) % 2), kx, 712, P.lalki + 0.01, h=230, anchor=(0.5, 1.0), sx=-1, rot=2 * math.sin(t * 6))
    # jeździec siedzi na grzbiecie konia (biodra na grzbiecie ok. y 548), nogi zakrywa koń
    lalka(st, t, "straznik", kx + 10, 300, y=556 + 0.383 * 300, flip=-1, rece=(30, 0), p=P.lalki + 0.012, trzyma=KARABIN(150),
          siedzi=True, lift=3 * abs(math.sin(t * 6)))
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
    """Na polu Clyde podnosi ręce i zaciska oczy; z góry, z prawej, spada siekiera prosto na jego stopę i wbija się w ziemię;
    Clyde łapie się za but i podskakuje na jednej nodze; „AW!” i gwiazdki (markery reżysera 19.11: „ręce podnieś”, „stąd spada
    siekiera”)."""
    kam(st, t, 22, 600, 420, 1.45, 0.8)
    st.dof = 1.3
    eastham(st, t, w, wieza=False, kul=False)
    f = pr(t, 1.0, 0.45)
    ax_ = 690
    if f > 0:  # siekiera ostrzem w dół, spada pionowo i zostaje wbita (trzonek wystaje nad rampę)
        st.put(J.rek("siekiera"), ax_, lerp(-120, 700, min(1.0, f * f)), P.lalki + 0.03, h=46, anchor=(0.93, 0.5), rot=90 - 8 * (1 - f),
               blur=2.0 if f < 1 else None)
    hop = t > 1.5
    reka_gora = ease(pr(t, 0.0, 0.4)) * (1 - ease(pr(t, 1.45, 0.25)))
    lalka(st, t, "clyde_wiezien", 600 - 40 * hop * ease(pr(t, 1.5, 0.5)) + 20 * math.sin(t * 6) * hop, 320, flip=1, lean=-12 * hop,
          lift=30 * abs(math.sin(t * 7)) * hop,
          rece=(lerp(50 + 60 * hop, 160, reka_gora), lerp(60 + 40 * hop, 160, reka_gora)),
          gwiazdki=ease(pr(t, 1.6, 0.4)) * (1 - ease(pr(t, 4.0, 0.5))))
    tab(w, t, "AW!", 640, 230, 1.6, 2.0)
    koniec(st, w, t, extra=(1.04, 1.0, 0.92))


def _brama(st, w, t, otw):
    eastham(st, t, w, brama=1.0, wieza=True, kul=False)
    for strona in (-1, 1):
        x = 640 + strona * (210 + 190 * ease(otw))
        st.put(J.skrzydlo_bramy(), x, 700, P.wzgorza + 0.025, h=300, anchor=(0.5, 1.0), sx=strona * (1 - 0.7 * ease(otw)))


def s_parol(st, w, t, T):
    """Brama się otwiera; Clyde wychodzi o kulach (kula pod pachą, dłoń na rączce); strażnik macha za nim kartką „PAROLE”."""
    kam(st, t, 23, 640, 400, 1.15, 0.8)
    _brama(st, w, t, pr(t, 0.2, 1.0))
    cx, _ = jazda(t, 0.9, 3.0, 640, 900)
    krok = math.sin(cx / 30.0)
    lalka(st, t, "clyde", cx, 320, flip=1, rece=(25 + 8 * krok, 25), trzyma=KULA(), kuleje=1.0, hop=4 * (0.9 < t < 3.9))
    lalka(st, t, "straznik", 560, 320, flip=1, rece=(120 + 30 * math.sin(t * 8), 0), trzyma=(J.rek("parole"), 70, (0.5, 0.2), 70, True))
    koniec(st, w, t)


def s_przysiega(st, w, t, T):
    """Brama zamyka się za Clyde'em z hukiem; Clyde o kulach odwraca się do niej, „NEVER AGAIN”; od 5 s idzie powoli o kulach
    od lewej do prawej przez kadr (reżyser 19.11: „od 5 s przechadzaj go, ale wolno, bo ma kule… i skróć ten kadr do 10 s”)."""
    hk = 2.2 < t < 2.5
    idzie = pr(t, 5.0, max(0.5, T - 5.3))
    cx = lerp(560, 1060, idzie)
    kam(st, t, 24, lerp(640, 820, ease(idzie)), 390, 1.35, 0.81, shake=5.0 * hk)
    st.dof = 1.3
    _brama(st, w, t, 1 - pr(t, 1.6, 0.6))
    krok = math.sin(cx / 26.0)
    lalka(st, t, "clyde", cx, 320, flip=1 - 2 * ease(pr(t, 0.6, 0.6)) * (1 - ease(pr(t, 4.6, 0.4))), rece=(25 + 10 * krok * (idzie > 0), 25),
          trzyma=KULA(), kuleje=1.0 * (idzie > 0), hop=3 * (0 < idzie < 1))
    tab(w, t, "NEVER AGAIN", 640, 200, 2.6, 2.4)
    koniec(st, w, t)


# ===================== AKT II · JAK ZOSTAĆ NAJBARDZIEJ POSZUKIWANYM =====================

from scena import ciemnosc, las, wawoz, mapa_scena, mapa_punkt, motocykl, ksiezyc, _off  # noqa: E402


def s_akt2(st, w, t, T):
    """Droga wśród pól; z ziemi wyrasta stacja benzynowa z jednym dystrybutorem; Ford wjeżdża z lewej i staje przy niej."""
    kam(st, t, 25, 640, 400, lerp(0.95, 1.05, ease(t / T)), 0.76)
    preria(st, t, w, slupy=True, wiatrak=True)
    Z0.rise(st, J.fasada("stacja"), 960, 650, P.most, bk(w, 0.9, 0.9), t, 470, h=330, wob=0.0)
    x, k = jazda(t, 1.4, 4.0, -300, 640)
    # gag 7 (GAGI.md): na „keep driving” auto rusza bez Bonnie — zostaje tam, gdzie siedziała — i wraca po nią tyłem
    x += 1100 * ease(pr(t, 6.9, 0.6)) - 1100 * ease(pr(t, 8.0, 0.9))
    bez_niej = 6.9 < t < 9.0
    auto(st, t, x, pasazerowie=[("clyde", 1, (40, 0))] + ([] if bez_niej else [("bonnie", 0, (0, 0))]))
    if bez_niej:
        lalka(st, t, "bonnie", 560, 290, flip=1, rece=(10 + 60 * ease(pr(t, 7.3, 0.3)), 0), siedzi=False)
        tab(w, t, "SERIOUSLY?", 560, 240, 7.3, 1.5)
    koniec(st, w, t)


def s_stacja(st, w, t, T):
    """Clyde wpada do budki stacji z rewolwerem; kasjer otwiera szufladę: kilka monet i guzik; „THAT'S IT?”."""
    kam(st, t, 26, 640, 450, 1.25, 0.8)
    miasto(st, t, w, fasady=(("stacja", 640),), tyl=(), chodnik=True)
    rozklada = ease(pr(t, 6.9, 0.4))
    out_k = lalka(st, t, "kasjer", 760, 300, flip=-1, rece=(lerp(10, 80, ease(pr(t, 2.4, 0.6))) + 70 * rozklada,
                                                         60 * ease(pr(t, 1.2, 0.3)) + 80 * rozklada))
    cx, _ = jazda(t, 0.2, 1.4, 200, 520)
    lalka(st, t, "clyde", cx, 330, flip=1, rece=(90, 0), trzyma=REV(), hop=6 * (t < 1.6))
    if out_k and t > 2.9:
        for n in range(3):
            st.put(Z0.coin(), out_k[0] - 20 + 14 * n, out_k[1] - 6, P.lalki + 0.03, h=12, anchor=(0.5, 0.5))
        st.put(J.rek("pinezka"), out_k[0] + 26, out_k[1] - 4, P.lalki + 0.03, h=10, anchor=(0.5, 0.5), tint=(0.5, 0.4, 0.3))
    tab(w, t, "THAT'S IT?", 560, 250, 3.4, 2.6)
    # gag 8 (GAGI.md, W1 „pusta kasa”): na „only a few dollars” z kasy wylatuje ćma; kasjer rozkłada ręce
    fc = pr(t, 6.6, 2.2)
    if out_k and 0 < fc < 1:
        st.put(J.rek("cma"), out_k[0] + 160 * fc + 30 * math.sin(fc * 20), out_k[1] - 20 - 300 * fc, P.rekwizyty, h=50,
               anchor=(0.5, 0.5), sx=0.3 + 0.7 * abs(math.sin(t * 22)), rot=10 * math.sin(t * 7))
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
    # gag 33 (GAGI.md): wiersz o Suicide Sal nie wychodzi — stos zgniecionych kartek przy pryczy rośnie aż do kolan Bonnie
    for n in range(int(min(14, max(0, (t - 1.2) * 1.8)))):
        st.put(J.rek("list"), 470 + 34 * math.sin(n * 2.3) + 6 * (n % 3), 676 - 9 * n, P.lalki + 0.025 + 0.0003 * n, h=34, anchor=(0.5, 1.0),
               rot=n * 47 % 360, sx=0.55 + 0.2 * math.sin(n), tint=(0.95, 0.93, 0.88))
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
    podpis(w, t, "John Bucher", 540, 300, 5.4, 3.0)  # przy zbliżeniu 1,5 kadr zaczyna się ok. y 230 (przegląd 19.11)
    koniec(st, w, t, dim=0.9)


def s_matka_obietnica(st, w, t, T):
    """Bonnie wychodzi z aresztu prosto w objęcia matki i kiwa głową; za płotem stoi Ford, Clyde cicho trąbi."""
    kam(st, t, 30, 640, 430, 1.1, 0.8)
    miasto(st, t, w, fasady=(("dom", 420), ("areszt", 1040)), tyl=(("dom", 200),), chodnik=True)
    Z0.rise(st, J.plot(2, False), 640, 690, P.drzewa, bk(w, 0.5), t, 480, w=1500, wob=0.0)
    # gag 34 (GAGI.md): na „for a few weeks” zawieszka WEEK 1 → 2 → 3, klakson, a Bonnie już biegnie do Forda;
    # matka zostaje z otwartymi ramionami
    w_aucie = t > 10.3
    auto(st, t, 900, 220, y=660, p=P.wzgorza + 0.02, pasazerowie=[("clyde", 1, (40 + 30 * (9.5 < t < 10.4), 0))]
         + ([("bonnie", 0, (0, 0))] if w_aucie else []))
    bx, _ = jazda(t, 0.4, 2.0, 1060, 640)
    bx += 300 * ease(pr(t, 9.8, 0.5))
    przytul = ease(pr(t, 2.4, 0.6)) * (1 - ease(pr(t, 6.0, 0.5)))
    if not w_aucie:
        lalka(st, t, "bonnie", bx, 290, 1.0 - ease(pr(t, 10.1, 0.2)), flip=-1 if t < 9.8 else 1,
              lean=-8 * przytul + 4 * math.sin(t * 6) * (3.6 < t < 4.6), rece=(90 * przytul, 70 * przytul), hop=6 * (t > 9.8))
    puste = ease(pr(t, 9.9, 0.3))
    lalka(st, t, "matka_bonnie", 560, 290, flip=1, lean=8 * przytul, rece=(90 * max(przytul, puste), 70 * max(przytul, puste)))
    for n, txt in enumerate(("WEEK 1", "WEEK 2", "WEEK 3")):
        k_ = pr(t, 8.3 + 0.45 * n, 0.4) * (1 - pr(t, 8.7 + 0.45 * n, 0.15)) if n < 2 else pr(t, 9.2, 0.4) * (1 - pr(t, 10.6, 0.3))
        if k_ > 0:
            J.hang(st, J.tag(txt), 640, 140, P.rekwizyty, k_, t, 520 + n, h=46, drop=300, sway=0.8)
    tab(w, t, "BEEP", 900, 360, 9.6, 1.6)
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
    # chłopak stoi przy aucie, kiedy lektor go nazywa, i wsiada dopiero przy „joined them” (przegląd 19.11: podpis
    # zjeżdżał, gdy był już w aucie)
    # gag 9 (GAGI.md): po „sounded exciting” W.D. tak się spieszy, że wskakuje do auta szczupakiem przez okno
    w_srodku = t > 6.4
    auto(st, t, 640, pasazerowie=[("clyde", 1, (40, 0))] + ([("wd", 0, (0, 0))] if w_srodku else []))
    if not w_srodku:
        x, _ = jazda(t, 0.4, 2.4, 1100, 760)
        f = pr(t, 5.6, 0.8)
        lalka(st, t, "wd", lerp(x, 600, ease(f)), 280, flip=-1, rece=(20 + 140 * f, 10 + 120 * f), hop=5 * (t < 2.4),
              lean=-95 * ease(f), lift=200 * math.sin(math.pi * min(1.0, f * 1.15)), p=P.auta - 0.004 if f > 0.55 else None)
    podpis(w, t, "W.D. Jones, 16", 640, 220, 2.6, 2.8)
    tab(w, t, "OOF!", 560, 300, 6.4, 1.2)
    koniec(st, w, t)


def s_buck(st, w, t, T):
    """Z bramy więzienia wychodzi Buck z ułaskawieniem w ręku; czeka Blanche w kapelusiku, z białym pieskiem na rękach."""
    kam(st, t, 33, 640, 430, 1.05, 0.8)
    miasto(st, t, w, fasady=(("wiezienie", 640),), tyl=(), chodnik=True)
    bx, _ = jazda(t, 0.6, 2.6, 640, 820)
    bx -= 70 * ease(pr(t, 11.5, 0.3))
    lalka(st, t, "buck", bx, 320, flip=1, rece=(110 + 50 * ease(pr(t, 11.5, 0.3)), 0), trzyma=(J.rek("pardon"), 60, (0.5, 0.2), 70, True),
          hop=5 * (t < 3.2), lift=30 * _bump(t, 11.6, 0.3), lean=-10 * ease(pr(t, 11.5, 0.3)))
    out = lalka(st, t, "blanche", 1020, 290, flip=-1, rece=(70, 70))
    # gag 35 (GAGI.md): po „family visit” piesek Blanche wyskakuje z jej rąk i obszczekuje Bucka, Buck odskakuje
    fp = pr(t, 11.0, 0.5)
    if out and fp <= 0:
        st.put(J.zwierze("piesek"), out[0] + 10, out[1] - 10, P.lalki + 0.03, h=46, anchor=(0.5, 0.6), sx=-1, rot=6 * math.sin(t * 4))
    elif out:
        # ląduje nad rampą (przy STOPY rampa zakryłaby pieska)
        st.put(J.zwierze("piesek"), lerp(out[0] + 10, bx + 90, ease(fp)), lerp(out[1] - 10, 652, fp) - 90 * math.sin(math.pi * fp),
               P.lalki + 0.03, h=46, anchor=(0.5, 1.0) if fp >= 1 else (0.5, 0.6), sx=-1, rot=-6 * math.sin(t * 20) * (fp >= 1))
        tab(w, t, "YAP!", bx + 110, 520, 11.5, 1.4)
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
    # gag 10 (GAGI.md): na „normal family” zjeżdża rama zdjęcia rodzinnego, w niej pięć uśmiechów; z boku wsuwa się lufa
    # karabinu, Bonnie ją wypycha, uśmiechy zostają
    kr = pr(t, 7.8, 0.8) * (1 - pr(t, 11.0, 0.5))
    if kr > 0:
        J.hang(st, J.ramka(), 640, 250, P.rekwizyty + 0.01, kr, t, 480, w=620, drop=420, sway=0.3, strings=(0.1, 0.9))
        for n, key in enumerate(("buck", "blanche", "bonnie", "clyde", "wd")):
            lalka(st, t, key, 420 + 110 * n, 150, ease(pr(t, 8.3 + 0.08 * n, 0.4)) * (1 - pr(t, 11.0, 0.3)), y=505,
                  p=P.rekwizyty, flip=1 if n < 2 else -1, rece=(10 + 60 * (key == "bonnie") * ease(pr(t, 9.7, 0.2)), 0))
        lufa = ease(pr(t, 9.2, 0.4)) * (1 - ease(pr(t, 9.8, 0.3)))
        if lufa > 0:
            st.put(J.rek("karabin"), lerp(1060, 880, lufa), 420, P.rekwizyty + 0.005, w=200, anchor=(0.0, 0.5), sx=-1)
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
    out_b = lalka(st, t, "buck", 620, 300, flip=1, sink=0.15, rece=(70 + 10 * math.sin(t * 3) - 25 * _bump(t, 10.0, 0.4), 40),
                  trzyma=(J.rek("karty"), 40, (0.5, 0.8), 0, True))
    # gag 36 (GAGI.md): Buckowi wypada z rękawa as i ląduje na stole; Blanche patrzy na niego, „!”
    fa = pr(t, 10.0, 0.5)
    if out_b and fa > 0:
        st.put(J.tag("ACE", 30), lerp(out_b[0] - 20, 690, ease(fa)), lerp(out_b[1] + 10, STOPY - 136, fa * fa), P.lalki + 0.03, h=24,
               anchor=(0.5, 1.0), rot=lerp(40, -6, fa), shadow=(2, 3, 3, 0.3))
    tab(w, t, "!", 790, 230, 10.5, 1.4)
    lalka(st, t, "blanche", 790, 290, flip=-1, sink=0.15, rece=(70, 40), trzyma=(J.rek("karty"), 36, (0.5, 0.8), 0, True), lean=-8 * ease(pr(t, 10.4, 0.3)))
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
    # gag 11 (GAGI.md): kiedy na odbitce wyłania się Bonnie z cygarem, wywołującemu wypada papieros z ust prosto do kuwety, „O!”
    ux, uy = punkt("fotograf", 1010, 330, 176, 160, flip=-1, rot=-14)
    fp = pr(t, 5.0, 0.6)
    if fp < 1:
        st.put(J.rek("papieros"), ux - 10 - 50 * fp, uy + 230 * fp * fp, P.lalki + 0.03, h=10, anchor=(0.9, 0.5), rot=-10 - 300 * fp)
    tab(w, t, "O!", 1010, 280, 5.1, 1.6)
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
    # gag 12 (GAGI.md, W1 „pusta kasa”): pierwszy w kolejce wywraca puste kieszenie — wylatuje ćma — i i tak płaci ostatnią monetą
    kx = 560 - 60 * ease(pr(t, 2.0, 1.0))
    kies = ease(pr(t, 9.6, 0.3)) * (1 - ease(pr(t, 11.0, 0.3)))
    for u in (112, 188):  # kieszenie na biodrach (arkusz korpusu), białe podszewki zwisają
        if kies > 0:
            px_, py_ = punkt("bezrobotny", kx, 300, u, 430, flip=-1)
            st.put(J.rek("pranie"), px_, py_, P.lalki + 0.012, h=24 * kies, anchor=(0.5, 0.0), tint=(1.0, 1.0, 0.95))
    fc = pr(t, 9.9, 2.0)
    if 0 < fc < 1:
        st.put(J.rek("cma"), kx + 30 + 120 * fc + 25 * math.sin(fc * 18), 560 - 320 * fc, P.rekwizyty, h=46, anchor=(0.5, 0.5),
               sx=0.3 + 0.7 * abs(math.sin(t * 22)), rot=10 * math.sin(t * 7))
    fm = pr(t, 11.4, 0.6)
    if 0 < fm < 1:
        st.put(Z0.coin(), lerp(kx - 20, 410, fm), 470 - 80 * math.sin(math.pi * fm), P.lalki + 0.03, h=16, anchor=(0.5, 0.5), sx=abs(math.cos(fm * 12)))
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
    # gag 13 (GAGI.md, pomysł reżysera „auto robi wrr wrr”): skradziony Ford gaśnie i kaszle, Darby wybiega i prawie dobiega,
    # auto rusza z piskiem tuż przed jego ręką; potem Darby i Stone biegną do swojego auta i ruszają w pościg
    x1 = 700 + 1000 * ease(pr(t, 6.0, 0.8))
    kaszel = sum(max(0.0, 1 - abs(t - c) / 0.15) for c in (2.0, 2.7, 3.4, 4.6))
    auto(st, t, x1, 210, kolor="granat", pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], lift=10 * kaszel,
         przechyl=2 * kaszel)
    for c in (2.0, 2.7, 3.4, 4.6):
        f = pr(t, c, 0.9)
        if 0 < f < 1:
            st.put(J.glow(r=256, color=(96, 92, 90)), x1 - 270 - 60 * f, 600 - 90 * f, P.auta + 0.02, w=120 + 260 * f, anchor=(0.5, 0.5),
                   alpha=0.9 * (1 - f), shadow=None)
    for n, key in enumerate(("darby", "stone")):
        dobieg = lerp(380, 610 - 90 * n, ease(pr(t, 4.2 + 0.3 * n, 1.6)))
        x = lerp(dobieg, 220 - 60 * n, ease(pr(t, 6.4 + 0.2 * n, 0.8)))
        lalka(st, t, key, x, 300 - 10 * n, ease(pr(t, 4.0 + 0.3 * n, 0.4)) * (1.0 - ease(pr(t, 7.0 + 0.2 * n, 0.4))),
              flip=1 if t < 6.4 else -1, rece=(150 * (n == 0) * (t < 6.5), 0), hop=6)
    x2, _ = jazda(t, 7.6, 3.4, 160, 1700)
    auto(st, t, x2, 200, kolor="zielony", p=P.auta + 0.004, pasazerowie=([("stone", 0, (0, 0)), ("darby", 1, (60, 0))] if t > 7.3 else []))
    tab(w, t, "HEY!", 600, 300, 6.1, 1.6)
    koniec(st, w, t)


def s_darby_tyl(st, w, t, T):
    """Darby i Stone siedzą ściśnięci na tylnym siedzeniu; Bonnie odwraca się do nich i pyta; podpisy."""
    kam(st, t, 42, 640, 470, 1.55, 0.79)
    st.dof = 1.3
    preria(st, t, w, slupy=True, kul=False)
    x = 640 + 6 * math.sin(t * 9)
    obrot = -1 if t > 1.6 else 1
    mi = ease(pr(t, 9.6, 0.6))
    auto(st, t, x, 300, droga=t * 400, pasazerowie=[
        ("stone", (330, 132), (0, 0)),
        # gag 14: Darby z nawyku rozwija miarkę i mierzy głowę Bonnie (miarka w jego dłoni, taśma do jej głowy)
        # dłoń z kasetką miarki nad głową Bonnie, taśma zwisa w dół wzdłuż jej twarzy („od czubka głowy”)
        ("darby", (410, 126), (140 * mi, 0), 1, (J.rek("miarka"), 15, (0.06, 0.5), 90, False) if mi > 0.4 else None),
        ("bonnie", (505, 126), (60 * ease(pr(t, 2.0, 0.4)), 0), obrot)])
    podpis(w, t, "Dillard Darby", 560, 250, 1.0, 3.6)
    podpis(w, t, "Sophia Stone", 440, 320, 2.0, 2.8)
    # puenta dopiero na „undertaker” (przegląd 19.11: podpis zdradzał ją 8 s wcześniej)
    podpis(w, t, "Dillard Darby, undertaker", 560, 250, 8.7, 2.0)
    # gag 14 (GAGI.md, czarny humor za zgodą reżysera): na „undertaker” Darby z nawyku rozwija miarkę i mierzy Bonnie od czubka
    # głowy w dół; Bonnie patrzy na miarkę („…”). Zasiew klamry z ujęcia darby_zaklad.
    if mi > 0:
        k = 300 / 360.0
        tab(w, t, "…", x + (505 - 450) * k + 40, DROGA_Y + (126 - 356) * k - 110, 10.4, 1.3)
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
    # gag 15 (GAGI.md): na „five dollars” wiatr porywa banknot z ręki Darby'ego, a Darby goni go tak, jak przedtem gonił auto
    fb = pr(t, 5.3, 2.6)
    dx = lerp(380, 1180, ease(pr(t, 5.6, 2.6)))
    out = lalka(st, t, "darby", dx, 300, d, flip=1, rece=(lerp(0, 90, ease(pr(t, 2.2, 0.5))) + 50 * (t > 5.4), 0), hop=6 * (t > 5.6))
    lalka(st, t, "stone", 250, 290, d, flip=1, rece=(10, 0))
    if out and 2.8 < t and fb <= 0:
        st.put(J.rek("banknot"), out[0], out[1], P.lalki + 0.03, h=22, anchor=(0.3, 0.5), rot=-8)
    elif 0 < fb < 1:
        st.put(J.rek("banknot"), lerp(420, 1450, fb), 450 - 120 * math.sin(math.pi * fb) + 30 * math.sin(fb * 17), P.lalki + 0.03, h=22,
               anchor=(0.5, 0.5), rot=fb * 720, sx=abs(math.cos(fb * 11)) * 0.8 + 0.2)
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
            # gag 37 (GAGI.md): ostatni plakat zjeżdża do góry nogami i po chwili przekręca się z „boing”
            obr = 180 * (1 - back(pr(t, 5.0, 0.5), 1.4)) if n == 4 else 0
            J.hang(st, J.rek("plakat"), px, py - 70, P.wzgorza + 0.01 + 0.001 * n, k, t, 490 + n, h=90, drop=300, string=False,
                   rot0=obr, anchor=(0.5, 0.0) if not obr else (0.5, 0.5))
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
        # gag 38 (GAGI.md): na „somebody called the sheriff” farmerka upuszcza wiadro i macha na radiowóz „OVER HERE!”
        macha = n == 1 and t > 5.0
        x = x0 + 60 * math.sin(min(t, 5.0) * 1.2 + n) if n == 1 else x0 + 60 * math.sin(t * 1.2 + n)
        lalka(st, t, key, x, 300, flip=1 if macha else math.copysign(1, math.cos(t * 1.2 + n)),
              rece=((150 + 25 * math.sin(t * 12), 150 + 25 * math.sin(t * 12 + 1.5)) if macha else (30, 0)),
              trzyma=None if macha else (J.rek("wiadro"), 40, (0.5, 0.1), 0, False), hop=4 * macha)
        if n == 1 and t > 5.0:
            st.put(J.rek("wiadro"), x + 16, STOPY - 2, P.lalki + 0.015, h=40, anchor=(0.5, 1.0), rot=-70 * back(pr(t, 5.0, 0.3), 1.2))
    tab(w, t, "OVER HERE!", 760, 250, 5.3, 2.2)
    x, _ = jazda(t, 4.2, 3.6, 1600, 1000)
    auto(st, t, x, 210, kolor="czarny", napis="SHERIFF", flip=-1, pasazerowie=[("szeryf", 0, (0, 0)), ("detektyw", 1, (40, 0))])
    koniec(st, w, t)


def s_drzewo(st, w, t, T):
    """Szeryf i marszałek przywiązani drutem kolczastym do drzewa; Clyde macha im z auta na pożegnanie; „BYE!”."""
    kam(st, t, 51, 640, 430, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", krzaki=False)
    Z0.rise(st, J.drzewo(7), 420, 712, P.lalki - 0.004, bk(w, 0.3), t, 510, h=600, wob=0.0)
    for n, (key, x) in enumerate((("szeryf", 350), ("detektyw", 490))):
        lalka(st, t, key, x, 300, flip=1 if n else -1, rece=(0, 0), lean=3 * math.sin(t * 3 + n) * (n or t < 8.9))
    # gag 39 (GAGI.md): przywiązanemu szeryfowi siada na kapeluszu ptak i zostaje; szeryf: „…”
    fb = pr(t, 8.3, 0.7)
    if fb > 0:
        hx_, hy_ = punkt("szeryf", 350, 300, 152, 62, flip=-1)
        st.put(Z0.bird(int(t * 9) % 2 if fb < 1 else 0), lerp(-80, hx_, ease(fb)), lerp(260, hy_ - 8, ease(fb)) - 40 * math.sin(math.pi * fb),
               P.lalki + 0.03, h=40 if fb < 1 else 34, anchor=(0.5, 1.0), shadow=(2, 3, 3, 0.3))
    tab(w, t, "…", 300, 300, 9.4, 1.8)
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
    # Bonnie leży na jego wyciągniętych rękach, przed nim (przegląd 19.11: wisiała za jego plecami, ręce trzymały powietrze)
    lalka(st, t, "bonnie", x + 35, 260, flip=-1, lean=80, lift=150 + 6 * abs(math.sin(x / 26)), rece=(150, 20), p=P.lalki + 0.015)
    if int(x / 52) % 2 == 0:
        tab(w, t, "OW!", x, 260, 1.0, 0.6)
    koniec(st, w, t)


def s_oboz(st, w, t, T):
    """Wieczór przy drodze: auto, pranie na sznurku, zimna puszka fasoli, Bonnie pisze, Clyde czyści karabin."""
    w.noc = 0.7
    kam(st, t, 53, 640, 440, 1.05, 0.79)
    preria(st, t, w, slupy=False, noc=1.0)
    auto(st, t, 980, 220, p=P.wzgorza + 0.03, tint=(0.8, 0.8, 0.9))
    st.line([(200, 470), (480, 486), (760, 470)], P.wzgorza + 0.035, width=1.4, color=(80, 70, 60))
    for n, x in enumerate((280, 380, 560, 660)):
        st.put(J.rek("pranie"), x, 474 + 6 * math.sin(n), P.wzgorza + 0.036, h=60, anchor=(0.5, 0.0), rot=3 * math.sin(t * 2 + n), tint=((0.9, 0.85, 1.0), (1.0, 0.8, 0.8))[n % 2])
    # zimna fasola (kwestia: „eating cold beans”): bez ogniska — puszka stoi na kamieniu
    st.put(J.rek("puszka"), 640, 640, P.lalki + 0.025, h=40, anchor=(0.5, 1.0))
    # gag 16 (GAGI.md): na „glamorous” złote iskry i blask jak w Hollywood; na „cold beans” blask gaśnie, a łyżka staje
    # w zimnej fasoli na sztorc
    gl = ease(pr(t, 1.5, 0.4)) * (1 - ease(pr(t, 4.4, 0.35)))
    if gl > 0:
        st.put(J.glow(), 640, 380, P.rekwizyty, w=1600, anchor=(0.5, 0.5), mode="add", alpha=0.28 * gl, shadow=None, tint=(1.0, 0.85, 0.45))
        for n in range(14):
            mig = 0.5 + 0.5 * math.sin(t * 9 + n * 1.7)
            st.put(Z0.prop("gwiazdka"), 160 + (n * 173) % 980, 160 + (n * 97) % 380, P.rekwizyty + 0.01, h=(22 + 10 * (n % 3)) * gl * mig,
                   anchor=(0.5, 0.5), rot=t * 60 + n * 30, tint=(1.0, 0.86, 0.4), shadow=None)
    ly = back(pr(t, 4.7, 0.35), 2.0)
    if ly > 0:
        st.put(J.rek("lyzka"), 640, 622, P.lalki + 0.024, h=64 * ly, anchor=(0.5, 1.0), rot=0)  # trzon w puszce
    lalka(st, t, "bonnie", 420, 280, flip=1, lean=6, rece=(80 + 5 * math.sin(t * 8), 60), trzyma=(J.rek("zeszyt"), 40, (0.5, 0.5), 80, True), kuleje=0)
    # Clyde stoi, więc karabin trzyma w dłoni lufą w górę i przeciera ją szmatką (przegląd 19.11: karabin wisiał w powietrzu
    # na wysokości kolan stojącego Clyde'a; lufa nie celuje w Bonnie)
    out = lalka(st, t, "clyde", 860, 320, flip=-1, lean=8, sink=0.15, rece=(60 + 14 * math.sin(t * 5), 40),
                trzyma=KARABIN(170))
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
    # gag 17 (GAGI.md): na „such a fine getaway car” Ford mruga reflektorem, jakby się zawstydził, i nieśmiało trąbi
    for c in (6.4, 6.8):
        if c <= t < c + 0.22:
            st.put(J.glow(), 640 + (842 - 450) * 300 / 360, DROGA_Y + (214 - 356) * 300 / 360, P.auta + 0.01, w=170, anchor=(0.5, 0.5),
                   mode="add", alpha=0.9 * math.sin(math.pi * (t - c) / 0.22), shadow=None, tint=(1.0, 0.95, 0.7))
    tab(w, t, "beep", 1060, 380, 7.2, 1.2)
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
        # obława strzela: karabin poziomo przed siebie, ręka ok. 90° (CEL) — poza strzałem broń w dół (marker 19.11)
        lalka(st, t, key, x, 300, k, flip=-1 if x0 > 640 else 1, rece=(88, 0), trzyma=CEL(150))
    koniec(st, w, t, extra=(1.06, 0.98, 0.92))


def s_przeprawa(st, w, t, T):
    """Clyde, Bonnie i W.D. brną przez rzekę; Clyde ciągnie Bonnie za rękę; na brzegu za nimi błyski."""
    kam(st, t, 58, 640, 480, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", droga=0.0, krzaki=True, swit=0.8)  # zaraz po obławie w Dexfield, o świcie (ciągłe cięcie)
    x, _ = jazda(t, 0.0, T, 300, 900)
    for n, (key, dx, h) in enumerate((("clyde", 0, 320), ("bonnie", -120, 280), ("wd", -230, 280))):
        lalka(st, t, key, x + dx + 8 * math.sin(t * 3 + n), h, flip=1, sink=0.32, lean=-6, rece=(70 if n < 2 else 40, 50 if n == 1 else 20))
    st.put(J.rzeka_pas(), 640, 745, P.lalki + 0.03, w=2200, anchor=(0.5, 1.0))
    for n in range(3):
        blysk(st, 120 + 60 * n, 560, P.drzewa, t, 1.4 + 1.1 * n, r=200)
    koniec(st, w, t, extra=(1.04, 1.0, 0.94))


def s_wd_odchodzi(st, w, t, T):
    """Nocą W.D. wymyka się na palcach; ręka matki wyciąga go z kadru za ucho; Bonnie patrzy za nim przez szybę."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 59, 640, 450, 1.2, 0.79)
    preria(st, t, w, slupy=True, noc=1.0)
    auto(st, t, 520, 240, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.7, 0.72, 0.85))
    # gag 18 (GAGI.md): W.D. wymyka się na palcach przesadnym krokiem z kreskówki; z prawej krawędzi wysuwa się ręka matki
    # i wyciąga go z kadru za ucho
    x = lerp(720, 1060, ease(pr(t, 0.6, 5.0))) + 420 * ease(pr(t, 6.4, 0.7))
    krok = abs(math.sin(t * 3.2)) * (0.6 < t < 6.2)
    lalka(st, t, "wd", x, 270, 1.0, flip=1, rece=(60 + 30 * krok, 40), lean=14 * (t < 6.3), lift=36 * krok, tint=(0.7, 0.72, 0.85))
    ra = ease(pr(t, 5.6, 0.6))
    if ra > 0:
        st.put(J.figura("farmerka").arm, lerp(1420, x + 120, ra) + 420 * ease(pr(t, 6.4, 0.7)) * 0, 385, P.lalki + 0.03, h=160,
               anchor=(0.5, 0.1), rot=95, tint=(0.75, 0.75, 0.88))
    tab(w, t, "AW!", 1000, 300, 6.4, 1.4)
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
    # gag 19 (GAGI.md): na „bringing laundry” Bonnie podaje matce stos prania wyższy od auta, matka oddaje maleńki talerzyk
    fs = ease(pr(t, 8.9, 1.3))
    if t > 8.9:
        lean_m = 8 * math.sin(t * 5) * (fs >= 1)
        for n in range(10):
            st.put(J.rek("pranie"), lerp(400, 650, fs) + 6 * math.sin(n * 1.7) + lean_m * n * 0.6, 560 - 26 * n, P.lalki + 0.03 + 0.0005 * n, h=34,
                   anchor=(0.5, 1.0), rot=4 * math.sin(n * 2.1), tint=((0.82, 0.8, 0.92), (0.9, 0.78, 0.8), (0.8, 0.86, 0.8))[n % 3])
    ft = pr(t, 10.6, 0.8)
    if ft > 0:
        st.put(J.rek("kanapka"), lerp(650, 430, ease(ft)), 470 - 30 * math.sin(math.pi * min(1, ft)), P.lalki + 0.03, h=12, anchor=(0.5, 0.5),
               tint=(0.85, 0.8, 0.9))
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
        lalka(st, t, key, kx, 300, k, flip=-1 if kx > 640 else 1, rece=(88, 0), trzyma=CEL(150), tint=(0.75, 0.75, 0.88), p=P.drzewa - 0.01)
        for m in range(3):
            blysk(st, kx - 80, 520, P.drzewa, t, 3.2 + 0.3 * m + 0.1 * n, r=200)
    tab(w, t, "OUCH!", 640, 300, 4.0, 2.6)
    koniec(st, w, t)
