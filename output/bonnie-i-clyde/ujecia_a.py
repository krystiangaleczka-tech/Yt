"""Ujęcia aktów 0–4 filmu „Bonnie and Clyde: The Outlaws Made of Paper”: funkcja `s_<klucz>(st, w, t, T)` na ujęcie.

st — scena (papier.Stage), w — stan świata z początku ujęcia (scena.stan), t — czas od początku ujęcia, T — długość ujęcia.
Rozpiska: docs/filmy/bonnie-i-clyde/ujecia/dane.py. Zapowiedź (zap_*) render składa sam ze skrótów tych ujęć (render.WYCINEK).
"""
import math
from functools import lru_cache

from scena import CY, USTA, _off, bark, dlon, do_punktu, gwiazdy, mruganie, rs, siegnij, stan_przy  # noqa: E402
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
    """Postać czyta gazetę trzymaną w dłoniach przed sobą, obok głowy — nie na głowie i nie w tułowiu (marker reżysera 21.11
    w kawiarni: „tak, żeby gazetę trzymał w ręku, gazeta za ręką, a nie w nim i na głowie”). Kartka stoi przed twarzą w kierunku
    patrzenia, jej bliższy brzeg dotyka nosa; obie dłonie leżą na bliższym brzegu (kartka za dłonią), ręce zgięte ku kamerze
    (skrót, Wytyczne 1.28). Zwraca położenie dłoni."""
    fx, fy = punkt(key, x, h, 152, 122, flip=flip, rot=lean)
    if sink:
        fy += ease(sink) * h * 1.12
    szer = hgaz * 360 / 480
    gx, gy = fx + flip * 0.21 * h, fy + 0.06 * h
    brzeg = (gx - flip * 0.40 * szer, gy)
    k1, s1 = do_punktu(key, x, brzeg, h=h, flip=flip, lean=lean, sink=sink)
    k2, s2 = do_punktu(key, x, (brzeg[0], brzeg[1] + 0.09 * h), h=h, flip=flip, lean=lean, sink=sink, ktora="tyl")
    st.put(gazeta, gx, gy, (P.lalki + 0.01 if p is None else p), h=hgaz, anchor=(0.5, 0.5), rot=lean, z=0.02)
    return lalka(st, t, key, x, h, flip=flip, lean=lean, sink=sink, p=p, rece=(k1, k2), skrot=(s1, s2), tyl_przed=True, **kw)


def PATELNIA(orot=0.0, dl=70):
    """Patelnia z kuchni w dłoni (markery reżysera 21.11, ujęcia 26–27): chwyt za koniec rączki (0.93, 0.5); orot — kierunek
    patelni jak przy rewolwerze (0: przed siebie, −90: w górę, jak do ciosu; 90: w dół). Na arkuszu patelnia leży rączką w prawo,
    więc „przed siebie” to obrót o 180°."""
    return (J.rek("patelnia"), dl * 90 / 300, (0.93, 0.5), 180 + orot, False)


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
    """Najazd na Bonnie; podpis „Bonnie Parker” przy imieniu. Markery reżysera 21.11 (4,1 s i 7,3 s): „w tej ręce cały czas trzyma
    pistolet”, „w drugiej ręce bierze z buzi papieros” (cygaro z ujęcia), „i go rzuca do tyłu”. Przednia ręka trzyma rewolwer przez
    całe ujęcie; tylna sięga do ust (4,1–4,6 s, ręka zgięta ku kamerze — skrót) i bierze cygaro (podmiana w jednej klatce: z ust
    do dłoni); Bonnie patrzy na nie, krzywi się („UGH!”) i na 7,33 s ciska je za siebie: cygaro koziołkuje w lewo i spada za rampę,
    skąd unosi się dymek."""
    kam(st, t, 2, lerp(640, 500, ease(pr(t, 0, 3))), lerp(380, 480, ease(pr(t, 0, 3))), lerp(1.0, 1.6, ease(pr(t, 0, 3.5))), 0.81)
    st.dof = 1.2
    teatr_gazet(st, t, w)
    auto(st, t, 700, 290)
    X, H, RZUT = 470, 320, 7.33

    def lean_(tt):
        return -6 + 4 * ease(pr(tt, 5.0, 0.5))

    def ramie(tt):
        """Tylna ręka: (kąt, skrót) — do ust, przed pierś z cygarem, zamach w przód, rzut za siebie, powrót."""
        ln = lean_(tt)
        srodek = punkt("bonnie_cygaro", X, H, 192, 157, flip=1, rot=ln)  # środek cygara w ustach: tu chwyta dłoń
        k_ust, s_ust = do_punktu("bonnie", X, srodek, h=H, flip=1, lean=ln, ktora="tyl")
        a1, a2, a3 = ease(pr(tt, 4.1, 0.5)), ease(pr(tt, 4.75, 0.55)), ease(pr(tt, 6.75, 0.35))
        a4, a5 = pr(tt, 7.1, RZUT - 7.1) ** 1.6, ease(pr(tt, 7.6, 0.6))
        kat, sk = lerp(10, k_ust, a1), lerp(1.0, s_ust, a1)
        kat, sk = lerp(kat, 62, a2), lerp(sk, 0.8, a2)
        kat, sk = lerp(kat, 118, a3), lerp(sk, 1.0, a3)
        kat = lerp(kat, 212, a4)
        return lerp(kat, 10, a5), sk

    ln = lean_(t)
    kat, sk = ramie(t)
    ma_w_ustach = t < 4.6
    lalka(st, t, "bonnie_cygaro" if ma_w_ustach else "bonnie", X, H, flip=1, lean=ln, rece=(70, kat), skrot=(1.0, sk),
          tyl_przed=kat > 25, trzyma=REV())
    if 4.6 <= t < RZUT:  # cygaro w palcach tylnej dłoni, przed ręką
        hx, hy = dlon("bonnie", X, kat, h=H, flip=1, lean=ln, ktora="tyl", skrot=sk)
        st.put(J.rek("cygaro"), hx, hy, P.lalki + 0.01, h=5.5, anchor=(0.5, 0.5), rot=-14 if t < 6.75 else -14 - 60 * pr(t, 6.75, 0.6), z=0.06)
    elif t >= RZUT:  # lot za siebie (w lewo), koziołkując; spada za rampę
        kr, skr = ramie(RZUT)
        rx, ry = dlon("bonnie", X, kr, h=H, flip=1, lean=lean_(RZUT), ktora="tyl", skrot=skr)
        dt = t - RZUT
        cx_, cy_ = rx - 300 * dt, ry - 380 * dt + 900 * dt * dt
        if cy_ < 720:
            st.put(J.rek("cygaro"), cx_, cy_, P.lalki + 0.02, h=5.5, anchor=(0.5, 0.5), rot=-14 - 1000 * dt)
        dl_ = (380 + math.sqrt(380 ** 2 + 4 * 900 * (700 - ry))) / 1800  # chwila upadku za rampę
        fd = pr(dt, dl_, 1.4)
        if 0 < fd < 1:  # dymek z miejsca, gdzie spadło
            for m in range(3):
                f_ = clamp(fd * 1.3 - m * 0.15)
                if 0 < f_ < 1:
                    st.put(J.glow(r=256, color=(214, 214, 214)), rx - 300 * dl_ + 6 * math.sin(f_ * 6 + m), 680 - 120 * f_, P.lalki + 0.02,
                           w=18 + 40 * f_, anchor=(0.5, 0.5), alpha=0.55 * (1 - f_), shadow=None)
    lalka(st, t, "clyde", 980, 350, flip=-1, rece=(35, 20), trzyma=KARABIN())
    podpis(w, t, "Bonnie Parker", 470, 250, 1.0, 3.2)
    if t > 5.6:
        tab(w, t, "UGH!", 560, 330, 5.6, 1.6)
    koniec(st, w, t)


class _Kam:
    """Sama kamera ujęcia w dowolnej chwili (do torów liczonych w kadrze ekranu)."""
    def __init__(self, T):
        self.T = T


def ekran_do_swiata(cam, sx, sy, p):
    """Punkt ekranu (1280 × 720) → kadr wzorcowy na planie p przy kamerze `cam` (odwrotność papier.Cam.screen)."""
    g = cam.mag(p)
    return (CX + p * ((sx - CX + cam.ox) / (p * g) + cam.X - CX), CY + p * ((sy - CY + cam.oy) / (p * g) + cam.Y - CY))


def tab_tu(st, w, t, txt, klucz, sx, sy, sek, dur=2.6):
    """Tabliczka z markera reżysera („tabliczka …”): (sx, sy) — środek kreski na ekranie, sek — sekunda markera na osi Studio.
    Tabliczka wisi już w tej sekundzie (zjeżdża 0,7 s wcześniej) w miejscu kreski; nad postacią, której dotyczy (1.20)."""
    x, y = ekran_do_swiata(st.cam, sx, sy, P.rekwizyty + 0.02)
    tab(w, t, txt, x, y - 26, rs(klucz, sek) - 0.7, dur)


# Ujęcie 13 — markery reżysera 21.11: „teraz strzel z końcówki rewolweru” (1,27 s), „tu się wbija kula” (5,37 s, punkt ekranu),
# „zaczyna lecieć ciurkiem paliwo i zalewa ziemię powoli aż do kolan” (5,63 s, kreska od baku w lewo na ziemię).
WPR2_STRZAL, WPR2_TRAF, WPR2_CIEK = 1.27, 5.37, 5.63
WPR2_CEL = (552.0, 524.0)       # dziura po kuli na ekranie w chwili trafienia (marker)
WPR2_ZIEMIA = (326.0, 560.0)    # tu strumień paliwa spada na ziemię (koniec kreski markera)
WPR2_RAMKA = (14.0, 1266.0, 34.0, 574.0)  # brzegi kadru, od których kula się odbija (dół: deski sceny nad pasem napisu)
P_KULA = P.auta + 0.006


def _kam_wpr2(st, t):
    k = ease(pr(t, 0, 4))
    zj = ease(pr(t, 6.2, 2.8))  # paliwo zalewa scenę: kamera schodzi niżej i bliżej, żeby zalew był nad pasem napisu
    kam(st, t, 3, lerp(900, 640, k) - 70 * zj, lerp(470, 390, k) + 60 * zj, lerp(1.6, 1.0, k) + 0.1 * zj, 0.81)


def _wpr2_reka(t):
    """Przednia ręka Bonnie: celuje (0,7–1,15 s), strzał 1,27 s z odrzutem, opuszcza rękę wzdłuż boku (1,9–2,4 s) — wtedy
    rewolwer wisi lufą w dół i nie zasłania dziury w baku, z której potem cieknie paliwo."""
    return lerp(20, 0, ease(pr(t, 1.9, 0.5))) + 62 * ease(pr(t, 0.7, 0.45)) * (1 - ease(pr(t, 1.9, 0.5))) + 16 * _bump(t, WPR2_STRZAL + 0.06, 0.12)


@lru_cache(None)
def _wpr2_tor(T):
    """Tor kuli w kadrze ekranu: z lufy, odbicia lustrzane od brzegów kadru jak w grze, koniec w punkcie markera w chwili trafienia.
    Zwraca (punkty ekranu, długości od startu, prędkość px/s, kąt lufy w stopniach)."""
    d = _Kam(T)
    _kam_wpr2(d, WPR2_STRZAL)
    L, R, Tp, B = WPR2_RAMKA
    sx0 = sy0 = None
    best = None
    for n in range(0, 2500):
        th = -10.0 - n * 0.02  # w górę i w prawo (10°–60°)
        # wylot lufy przy tym kącie (rewolwer podniesiony o th, chwyt za kolbę)
        hx, hy = dlon("bonnie", 470, _wpr2_reka(WPR2_STRZAL), h=320, flip=1, lean=-2)
        mx, my = _off(31.2, -13.4, th)
        sx0, sy0 = d.cam.screen(hx + mx, hy + my, P.lalki + 0.01)
        x, y = sx0, sy0
        dx, dy = math.cos(math.radians(th)), math.sin(math.radians(th))
        pts, dls, s_ = [(x, y)], [0.0], 0.0
        for _ in range(14):
            ts = [((L - x) / dx) if dx < 0 else ((R - x) / dx) if dx > 0 else 1e9, ((Tp - y) / dy) if dy < 0 else ((B - y) / dy) if dy > 0 else 1e9]
            k = min(ts)
            # najbliższy punkt odcinka od celu
            cx_, cy_ = WPR2_CEL
            u = clamp(((cx_ - x) * dx + (cy_ - y) * dy), 0, k)
            dd = math.hypot(x + dx * u - cx_, y + dy * u - cy_)
            if dd < 1.0 and 2600 < s_ + u < 4600 and 5 <= len(pts) + 1 <= 8:
                pts.append((cx_, cy_))
                dls.append(s_ + u)
                # lufa w górę ok. 30° (kula leci nad głową Clyde'a), najmniej odbić przy tym kącie
                if best is None or abs(th + 30) < abs(best[2] + 30):
                    best = (list(pts), list(dls), th)
                break
            x, y = x + dx * k, y + dy * k
            s_ += k
            pts.append((x, y))
            dls.append(s_)
            if ts[0] <= ts[1]:
                dx = -dx
            else:
                dy = -dy
    pts, dls, th = best
    return tuple(pts), tuple(dls), dls[-1] / (WPR2_TRAF - WPR2_STRZAL), th


def _wpr2_kula(T, t):
    """Położenie kuli na ekranie w chwili t (None przed strzałem i po trafieniu)."""
    pts, dls, v, _ = _wpr2_tor(T)
    s_ = (t - WPR2_STRZAL) * v
    if s_ < 0 or s_ > dls[-1]:
        return None
    for (a, b), (da, db) in zip(zip(pts, pts[1:]), zip(dls, dls[1:])):
        if s_ <= db:
            f = (s_ - da) / max(db - da, 1e-6)
            return lerp(a[0], b[0], f), lerp(a[1], b[1], f)
    return pts[-1]


@lru_cache(None)
def _wpr2_punkty(T):
    """Dziura w baku i miejsce, gdzie paliwo spada na ziemię — w kadrze wzorcowym (stałe na aucie i na scenie)."""
    d = _Kam(T)
    _kam_wpr2(d, WPR2_TRAF)
    dziura = ekran_do_swiata(d.cam, *WPR2_CEL, P_KULA)
    _kam_wpr2(d, WPR2_CIEK)
    ziemia = ekran_do_swiata(d.cam, *WPR2_ZIEMIA, P.auta + 0.004)
    return dziura, (ziemia[0], DROGA_Y)  # strumień spada na ziemię pod autem (linia kół), nie w powietrze nad deskami


def s_wprowadzenie2(st, w, t, T):
    """Odjazd na Clyde'a; podpis „Clyde Barrow”; za nimi z nitek zjeżdżają nagłówki gazet. Gag (marker reżysera 19.11) z markerami
    21.11: Bonnie celuje i na 1,27 s strzela — błysk na końcu lufy, rewolwer uniesiony w kierunku strzału; kula odbija się od
    brzegów kadru jak w grze (odbicia lustrzane, tor liczony na ekranie) i na 5,37 s wbija się w bak Forda w miejscu z markera;
    na 5,63 s z dziury leci ciurkiem paliwo, łukiem w lewo na ziemię, i powoli zalewa scenę do kolan lalek; „…” nad Bonnie."""
    _kam_wpr2(st, t)
    teatr_gazet(st, t, w)
    for n, (x, y, nag) in enumerate(((300, 140, "BANK ROBBED"), (640, 110, "POLICE HUNT COUPLE"), (980, 150, "OUTLAW GIRL WITH CIGAR"))):
        J.hang(st, J.gazeta(nag, 30 + n, 360, 300, False), x, y, P.wzgorza, pr(t, 3.0 + 1.3 * n, 1.0), t, 400 + n, w=270, drop=520,
               sway=1.2, strings=(0.2, 0.8))
    auto(st, t, 700, 290)
    _, _, _, th = _wpr2_tor(T)
    celuje = ease(pr(t, 0.7, 0.45)) * (1 - ease(pr(t, 1.9, 0.5)))
    orot = th * celuje + 90 * ease(pr(t, 1.9, 0.5))  # po strzale rewolwer opada lufą w dół
    rv = REV()
    out = lalka(st, t, "bonnie", 470, 320, flip=1, lean=-2, rece=(_wpr2_reka(t), 10), trzyma=(rv[0], rv[1], rv[2], orot, False))
    if out:
        mx, my = _off(31.2, -13.4, orot)
        if WPR2_STRZAL <= t < WPR2_STRZAL + 0.15:  # błysk na końcu lufy
            blysk(st, out[0] + mx, out[1] + my, P.lalki + 0.02, t, WPR2_STRZAL, r=90)
        fd = pr(t, WPR2_STRZAL + 0.05, 1.2)
        if 0 < fd < 1:  # dymek z lufy
            st.put(J.glow(r=256, color=(220, 220, 220)), out[0] + mx + 8 * fd, out[1] + my - 50 * fd, P.lalki + 0.02, w=10 + 26 * fd,
                   anchor=(0.5, 0.5), alpha=0.6 * (1 - fd), shadow=None)
    kul = _wpr2_kula(T, t)
    if kul:  # kula ze smugą (ostatnie 70 px toru), na planie auta
        bx, by = ekran_do_swiata(st.cam, *kul, P_KULA)
        smuga = [ekran_do_swiata(st.cam, *q, P_KULA) for q in (_wpr2_kula(T, max(WPR2_STRZAL, t - k * 0.02)) for k in range(5)) if q]
        if len(smuga) > 1:
            st.line(smuga, P_KULA, width=3, color=(250, 228, 150), alpha=0.8)
        st.put(J.glow(), bx, by, P_KULA + 0.001, w=26, anchor=(0.5, 0.5), mode="add", alpha=0.95, shadow=None, tint=(1.0, 0.9, 0.5))
    pts, dls, v, _ = _wpr2_tor(T)
    for q, dq in zip(pts[1:-1], dls[1:-1]):  # iskra przy każdym odbiciu
        tb = WPR2_STRZAL + dq / v
        if tb <= t < tb + 0.14:
            bx, by = ekran_do_swiata(st.cam, *q, P_KULA)
            st.put(J.glow(), bx, by, P_KULA, w=90, anchor=(0.5, 0.5), mode="add", alpha=0.9 * (1 - (t - tb) / 0.14), shadow=None,
                   tint=(1.0, 0.85, 0.4))
    (hx, hy), (gx, gy) = _wpr2_punkty(T)
    if t >= WPR2_TRAF:  # dziura po kuli w baku
        st.put(J.rek("dziura"), hx, hy, P.auta + 0.003, h=9, anchor=(0.5, 0.5), shadow=None)
        if t < WPR2_TRAF + 0.16:
            st.put(J.glow(), hx, hy, P_KULA, w=70, anchor=(0.5, 0.5), mode="add", alpha=0.9 * (1 - (t - WPR2_TRAF) / 0.16), shadow=None)
    zal = ease(pr(t, 5.95, 3.7))  # poziom paliwa na scenie: od desek do kolan lalek
    if t >= WPR2_CIEK:  # strumień: z dziury poziomo w lewo i łukiem w dół na ziemię
        u_max = ease(pr(t, WPR2_CIEK, 0.3))
        sl = []
        for m in range(17):
            u = u_max * m / 16
            sl.append((lerp(hx, gx, u) + 1.5 * math.sin(t * 17 + u * 9), hy + (gy - hy) * u * u))
        st.line(sl, P.auta + 0.004, width=5, color=(214, 164, 58), alpha=0.95)
        st.put(J.glow(r=256, color=(250, 220, 140)), hx, hy, P.auta + 0.005, w=14, anchor=(0.5, 0.5), alpha=0.7, shadow=None)
        for m in range(3):  # krople spadające wzdłuż strumienia
            u = ((t - WPR2_CIEK) * 1.7 + m / 3) % 1.0
            if u < u_max:
                st.put(J.glow(r=256, color=(214, 164, 58)), lerp(hx, gx, u), hy + (gy - hy) * u * u + 4, P.auta + 0.005, w=9,
                       anchor=(0.5, 0.5), alpha=0.9, shadow=None)
        if u_max >= 1:  # rozprysk tam, gdzie strumień trafia w ziemię albo w taflę
            st.put(J.glow(r=256, color=(226, 186, 96)), gx, gy - 70 * zal, P.auta + 0.005, w=30 + 6 * math.sin(t * 23), sy=0.4,
                   anchor=(0.5, 0.5), alpha=0.8, shadow=None)
    if zal > 0:  # paliwo zalewa scenę jak fale w teatrze: rząd za autem (zakrywa deski) i rząd przed lalkami — do kolan
        st.put(J.ciecz((176, 128, 48)), CX - 25 * math.sin(t * 1.1), lerp(712, 600, zal), P.auta - 0.01, w=2600, anchor=(0.5, 0.0),
               alpha=0.8, shadow=None)
        st.put(J.ciecz(), CX + 20 * math.sin(t * 1.3), lerp(712, 632, zal), P.lalki + 0.03, w=2600, anchor=(0.5, 0.0), alpha=0.66,
               shadow=None)
    lalka(st, t, "clyde", 980, 350, flip=-1, rece=(20, 15), trzyma=KARABIN())
    podpis(w, t, "Clyde Barrow", 980, 240, 1.0, 3.0)
    tab(w, t, "…", 470, 250, 9.0, 1.6)
    koniec(st, w, t)


def _mieszkanie_joplin(st, w, t, ruch=True):
    wnetrze(st, t, w, sciana="paski", okna=(260,), drzwi=(1050,), meble=(("stol", 640, 140, None), ("krzeslo", 470, 170, None),
                                                                       ("lozko", 230, 150, None)), zarowki=(640,))
    for n, (key, x, y, h, rot) in enumerate((("walizka", 860, 712, 90, 4), ("walizka", 930, 712, 70, -6), ("karabin", 640, 612, 34, 4),
                                            ("zeszyt", 700, 618, 50, 12), ("butelka", 560, 616, 70, 0))):
        k = bk(w, 0.5 + 0.05 * n)
        if k > 0:
            st.put(J.rek(key), x, y + (1 - back(k, 1.3)) * 140, P.lalki - 0.01, h=h, rot=rot)


# markery reżysera 24.11 (s na osi Studio): oczy policjanta jako „< <” na chwilę, kiedy patrzy na zdjęcia z kliszy
OCZY_ZACHWYT = {"hak_joplin_rzeczy": 7.07, "joplin_rzeczy": 5.7}


def s_joplin_rzeczy(st, w, t, T, klucz="joplin_rzeczy"):
    """Opuszczone mieszkanie w Joplin: policjant wchodzi drzwiami, rozgląda się, podnosi z podłogi aparat wysoko, do oczu,
    a z dołu aparatu wysuwa się w dół klisza (marker reżysera 19.11: „podnosi aparat wyżej, a film z kamery wylatuje od dołu
    w dół”). Markery 21.11 (ujęcie 14, hak): na klatkach kliszy mikro, czarne pozy Bonnie, każda inna („na tych klatkach z filmu
    są pozy czarne Bonnie, różne mikro”); od 7,8 s policjant lekko macha aparatem, klisza buja się za nim („macha tym lekko”),
    otwiera usta (lalka „detektyw_o”, podmiana w jednej klatce) i zjeżdża tabliczka „OOO…”."""
    kam(st, t, 4, lerp(760, 820, ease(t / T)), lerp(400, 470, ease(pr(t, 2.0, 4.0))), lerp(1.0, 1.45, ease(pr(t, 2.0, 4.0))), 0.81)
    st.dof = 1.0
    _mieszkanie_joplin(st, w, t)
    x, _ = jazda(t, 0.3, 2.2, 1120, 820)
    schyl = ease(pr(t, 3.0, 0.7)) * (1 - ease(pr(t, 4.2, 0.6)))
    wyzej = ease(pr(t, 4.2, 0.7))
    t_o = min(7.8, T - 2.4)  # „OOO…” (w haku 7,8 s jak w markerze; w krótszym ujęciu 49 wcześniej, żeby tabliczka zdążyła)
    macha = ease(pr(t, t_o - 0.2, 0.3))
    fala = macha * math.sin((t - t_o + 0.2) * 7.0)
    t_z = rs(klucz, OCZY_ZACHWYT[klucz])
    zachwyt = t_z <= t < t_z + 1.3
    out = lalka(st, t, ("detektyw_oo" if zachwyt else "detektyw_o") if t >= t_o or zachwyt else "detektyw", x, 330, flip=-1, lean=-18 * schyl,
                rece=(20 + 70 * schyl + 40 * ease(pr(t, 3.6, 0.6)) + 70 * wyzej + 6 * fala, 10), hop=6 * (t < 2.5))
    podnies = ease(pr(t, 3.6, 0.5))
    ax, ay = (720, 702) if podnies <= 0 or not out else (lerp(720, out[0], podnies), lerp(702, out[1], podnies))
    st.put(J.rek("aparat"), ax, ay, P.lalki + 0.02, h=50, anchor=(0.5, 0.5), rot=4 * fala)
    if t > 5.0 and out:
        f = ease(pr(t, 5.0, 1.4))
        buja = 6 * math.sin(t * 3) * (1 - macha) + 14 * macha * math.sin((t - t_o + 0.2) * 7.0 - 0.9)  # klisza buja się za ręką z opóźnieniem
        st.put(J.klisza_pozy(), ax - 4, ay + 22, P.lalki + 0.025, h=24, anchor=(0.0, 0.5), sx=0.12 + 0.88 * f, rot=90 + buja)
    if out:
        tab(w, t, "OOO…", x - 10, 250, t_o, 2.4)
    koniec(st, w, t)


def s_hak_joplin_rzeczy(st, w, t, T):
    s_joplin_rzeczy(st, w, t, T, klucz="hak_joplin_rzeczy")


@lru_cache(None)
def _zdjecie_x():
    """Gdzie Bonnie staje przy chłopaku, żeby jego wyciągnięta dłoń z cygarem sięgnęła jej ust (Wytyczne 1.28: lalka podchodzi,
    a rzecz nie przyskakuje). Dłoń chłopaka 3 px przed ustami."""
    bx_, by_, L = bark("wd", 1010, h=280, flip=-1)
    lo, hi = 700.0, 980.0
    for _ in range(40):
        mid = (lo + hi) / 2
        ux, uy = punkt("bonnie", mid, 300, 176, 160, flip=1)
        if math.hypot(ux - bx_, uy - by_) > L - 3:
            lo = mid
        else:
            hi = mid
    return lo


ZDJ_DO_UST, ZDJ_FLESZ = 2.03, 6.35  # marker reżysera 21.11: cygaro w ustach na 2,03 s; aparat z kieszeni ok. 5,67 s


def s_zdjecie(st, w, t, T):
    """Klatka z kliszy ożywa: przy Fordzie stoi chłopak (W.D.) z cygarem; Bonnie podchodzi, a chłopak wkłada jej cygaro do ust
    (marker reżysera 21.11: „chłopak daje jej papierosa do buzi” — podmiana w jednej klatce na 2,03 s, dłoń chłopaka przy jej
    ustach); Bonnie wraca, kręci rewolwerem i wsuwa go za pasek (marker 19.11), pozuje z cygarem; chłopak wyciąga z kieszeni
    stary aparat prasowy z wielką czaszą lampy (marker 21.11: „wyciąga z kieszeni aparat stary, ten z lampą taką dużą, i robi jej
    zdjęcie”), podnosi go do oka i błyska flesz z czaszy."""
    kam(st, t, 5, 700, 470, lerp(1.22, 1.32, ease(t / T)), 0.81)
    st.dof = 1.3
    miasto(st, t, w, fasady=(("garaz", 760),), tyl=(("dom", 200), ("dom", 1150)), kul=False)
    auto(st, t, 700, 250, kolor="szary")
    przy = _zdjecie_x()
    tam = ease(pr(t, 0.4, 1.3))
    wraca = ease(pr(t, 2.4, 1.1))
    bx = lerp(lerp(470, przy, tam), 470, wraca)
    idzie = (0.4 < t < 1.7) or (2.4 < t < 3.5)
    fl = 1 if t < 2.4 else -1 if t < 3.5 else 1
    ma_w_ustach = t >= ZDJ_DO_UST
    # chłopak: prawa (przednia) dłoń z cygarem do ust Bonnie, potem do kieszeni po aparat, aparat do oka
    usta_b = punkt("bonnie", przy, 300, 176, 160, flip=1)
    k_ust, _ = siegnij("wd", 1010, usta_b, h=280, flip=-1)
    kieszen = punkt("wd", 1010, 280, 196, 430, flip=-1)
    k_kie, s_kie = do_punktu("wd", 1010, kieszen, h=280, flip=-1)
    oko = punkt("wd", 1010, 280, 120, 150, flip=-1)  # aparat przed twarzą, obiektywem do Bonnie
    k_oko, s_oko = do_punktu("wd", 1010, (oko[0] - 18, oko[1] + 34), h=280, flip=-1)
    a1 = ease(pr(t, 1.15, 0.6)) * (1 - ease(pr(t, 2.15, 0.4)))     # cygaro do ust
    a2 = ease(pr(t, 4.9, 0.4)) * (1 - ease(pr(t, 5.67, 0.45)))     # ręka do kieszeni
    a3 = ease(pr(t, 5.67, 0.45))                                  # aparat do oka
    wd_kat = 10 + (k_ust - 10) * a1 + (k_kie - 10) * a2 + (k_oko - 10) * a3
    wd_sk = 1.0 + (s_kie - 1.0) * a2 + (s_oko - 1.0) * a3
    trz = None
    if t < ZDJ_DO_UST:
        trz = (J.rek("cygaro"), 5.5, (0.1, 0.5), 0, False)
    elif t >= 5.3:
        trz = (J.rek("aparat_lampa"), 56, (0.6, 0.95), 0, False)
    wd = lalka(st, t, "wd", 1010, 280, flip=-1, rece=(wd_kat, 0), skrot=(wd_sk, 1.0), trzyma=trz)
    krec = pr(t, 3.6, 0.6)
    za_pasem = t >= 4.25
    rv = REV()
    trz_b = None if za_pasem else (rv[0], rv[1], rv[2], 720 * ease(krec), False)
    lalka(st, t, "bonnie_cygaro" if ma_w_ustach else "bonnie", bx, 300, flip=fl, lean=-6 * (t > 4.6), lift=10 * (t > 4.6),
          rece=(20 + 25 * (3.6 < t < 4.25), 20), trzyma=trz_b, hop=5 * idzie)
    if za_pasem:  # rewolwer za paskiem: kolbą do góry, przy biodrze
        px_, py_ = punkt("bonnie_cygaro" if ma_w_ustach else "bonnie", bx, 300, 182, 420, flip=fl)
        st.put(rv[0], px_, py_, P.lalki + 0.015, h=rv[1], anchor=(0.3, 0.75), rot=100 * fl, sx=fl)
    if ma_w_ustach and t > 2.4:  # dym z cygara
        ux, uy = punkt("bonnie_cygaro", bx, 300, 176, 160, flip=fl)
        for m in range(3):
            f = ((t - 2.4) * 0.6 + m / 3) % 1.0
            st.put(J.glow(r=256, color=(220, 220, 220)), ux + 30 * fl + 20 * f, uy - 20 - 110 * f, P.lalki + 0.03, w=24 + 50 * f,
                   anchor=(0.5, 0.5), alpha=0.5 * (1 - f), shadow=None)
    fx = fy = None
    if wd and t >= 5.3:  # środek czaszy lampy (arkusz (44, 44), chwyt (0.6, 0.95), lustrzanie — chłopak patrzy w lewo)
        fx, fy = wd[0] + 24.6, wd[1] - 40.9
    fl_ = ZDJ_FLESZ <= t < ZDJ_FLESZ + 0.22
    if fx is not None:
        blysk(st, fx, fy, P.lalki + 0.04, t, ZDJ_FLESZ, r=1800, kolor=(1.0, 1.0, 0.95), dl=0.18)
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


PRASA_SKOK = 7.17


def s_prasa(st, w, t, T):
    """Wałki maszyny drukarskiej kręcą się, wylatują setki gazet ze zdjęciem Bonnie z cygarem i odlatują nad dachy."""
    kam(st, t, 7, 640, 380, lerp(1.05, 0.95, ease(t / T)), 0.72, shake=1.2)
    # marker reżysera 21.11 (7,17 s): „zaczyna podskakiwać lekko maszyna” — małe podskoki co 0,31 s do końca ujęcia
    drukarnia(st, t, w, obrot=t * 220, podskok=7 * abs(math.sin(math.pi * 3.2 * max(0.0, t - PRASA_SKOK))) * ease(pr(t, PRASA_SKOK, 0.3)))
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


# Ujęcie 19 — trasy aut z markerów reżysera 21.11 (kreski na ekranie w chwili 4,27 s): „autka mają driftować po mapie z dymem”
# (czarny Ford łowcy z kapeluszem w oknie) i „tak samo jak tamto, tylko inna trasa” (szary Ford Bonnie i Clyde'a).
OBIET_CHWILA = 4.27
OBIET_TRASY = {
    "czarny": ((591, 409), (553, 406), (532, 389), (536, 343), (552, 315), (575, 298), (599, 283), (626, 273), (656, 272), (688, 272),
               (720, 271), (745, 250), (762, 220), (775, 195), (762, 164), (732, 155), (705, 161), (690, 183), (690, 212), (700, 241),
               (722, 261), (751, 273), (782, 276), (812, 279), (822, 306), (820, 334), (797, 354), (768, 364), (741, 376), (715, 390),
               (700, 418), (696, 447), (700, 475), (730, 493), (759, 499), (789, 515), (792, 532)),
    "szary": ((675, 332), (654, 310), (626, 297), (596, 299), (554, 308), (528, 319), (500, 329), (469, 324), (449, 295), (445, 262),
              (455, 237), (484, 234), (520, 232), (553, 234), (580, 248), (608, 255), (647, 259), (679, 261), (707, 261), (736, 261),
              (766, 260), (798, 246), (815, 221), (827, 196), (829, 163), (809, 139), (780, 127), (748, 117), (722, 124), (708, 153),
              (706, 184), (719, 216), (738, 241), (762, 263), (782, 287), (763, 312), (733, 330), (714, 350), (693, 379), (674, 412),
              (664, 443), (662, 480), (676, 505), (697, 524), (723, 536), (752, 537), (780, 537), (812, 532), (846, 526)),
}
# (start, koniec jazdy): szary jedzie dłużej; łowca dojeżdża na miejsce pierwszy i czeka („catch them without ever chasing them”)
OBIET_CZAS = {"szary": (2.0, 11.2), "czarny": (2.4, 10.5)}
P_MAPA_AUTA = P.wzgorza + 0.01


def _kam_obietnica(st, t, T):
    kam(st, t, 9, 640, 360, lerp(0.95, 1.08, ease(t / T)), 0.62)


@lru_cache(None)
def _obietnica_trasa(kol, T):
    """Trasa w kadrze wzorcowym (na planie mapy): punkty, długości od startu, kąt jazdy i znak zwrotu auta (z opóźnieniem, żeby auto
    nie przerzucało się w pionowych odcinkach), skręt (do driftu)."""
    d = _Kam(T)
    _kam_obietnica(d, OBIET_CHWILA, T)
    pts = [ekran_do_swiata(d.cam, x, y, P_MAPA_AUTA) for x, y in OBIET_TRASY[kol]]
    # wygładzenie (kreska z ręki drży)
    for _ in range(2):
        pts = [pts[0]] + [((a[0] + 2 * b[0] + c[0]) / 4, (a[1] + 2 * b[1] + c[1]) / 4) for a, b, c in zip(pts, pts[1:], pts[2:])] + [pts[-1]]
    dl = [0.0]
    for a, b in zip(pts, pts[1:]):
        dl.append(dl[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    kat = [math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) for a, b in zip(pts, pts[1:])]
    kat.append(kat[-1])
    zwrot, sx = [], 1.0
    for k in kat:
        c = math.cos(math.radians(k))
        if abs(c) > 0.35:
            sx = 1.0 if c > 0 else -1.0
        zwrot.append(sx)
    skret = [0.0] + [((b - a + 180) % 360 - 180) for a, b in zip(kat, kat[1:])]
    return tuple(pts), tuple(dl), tuple(kat), tuple(zwrot), tuple(skret)


def _obietnica_auto(kol, T, t):
    """Położenie auta na trasie w chwili t: (x, y, obrót, zwrot, poślizg 0..1) albo None przed startem."""
    a, b = OBIET_CZAS[kol]
    if t < a:
        return None
    pts, dl, kat, zwrot, skret = _obietnica_trasa(kol, T)
    f = ease(pr(t, a, b - a))
    s_ = f * dl[-1]
    i = 0
    while i < len(dl) - 2 and dl[i + 1] < s_:
        i += 1
    u = (s_ - dl[i]) / max(dl[i + 1] - dl[i], 1e-6)
    x, y = lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u)
    # poślizg: tył wychodzi na zewnątrz zakrętu — suma skrętu na najbliższych odcinkach
    zakret = sum(skret[max(0, i - 1):i + 3])
    dr = clamp(zakret / 60.0, -1.0, 1.0) * (0 < f < 1)
    sx = zwrot[i]
    rot = (kat[i] if sx > 0 else kat[i] - 180)
    rot = clamp((rot + 180) % 360 - 180, -38, 38)  # wycinanka z boku: na pionowych odcinkach sunie bokiem, przechylona
    rot = (rot + 30 * dr) * (1 - ease(pr(t, b, 0.35)))  # na miejscu staje prosto
    return x, y, rot, sx, abs(dr)


def s_obietnica(st, w, t, T):
    """Gazety układają się w mapę pięciu stanów; po mapie driftują dwa papierowe Fordy, każdy swoją trasą, z dymem spod kół
    (markery reżysera 21.11: „autka mają driftować po mapie z dymem”, „tak samo jak tamto, tylko inna trasa” — trasy z kresek):
    szary Ford Bonnie i Clyde'a i czarny z kapeluszem łowcy w oknie. Obie trasy kończą się w tym samym miejscu na dole mapy;
    łowca dojeżdża pierwszy i czeka."""
    _kam_obietnica(st, t, T)
    teatr_gazet(st, t, w)
    J.hang(st, J.mapa_plansza(), 640, 40, P.wzgorza, pr(t, 0.2, 1.4), t, 420, w=900, drop=600, sway=0.4, strings=(0.08, 0.92))
    for n, kol in enumerate(("szary", "czarny")):
        for k in range(12, 0, -1):  # dym spod kół: kłęby z wcześniejszych chwil, rosną i bledną
            wiek = k * 0.09
            q = _obietnica_auto(kol, T, t - wiek)
            if q and t - wiek < OBIET_CZAS[kol][1] and k % 2 == 0:
                # uwaga reżysera 23.11: „auta mają być poziomo, a za nimi taki komiksowy dym” — kłęby jak w kreskówce
                x_, y_, _, sx_, dr_ = q
                st.put(J.rek("oblok"), x_ - 18 * sx_ - 10 * sx_ * wiek, y_ - 6 - 8 * wiek, P_MAPA_AUTA + 0.003, h=8 + 24 * wiek,
                       anchor=(0.5, 0.5), rot=40 * k, alpha=min(1.0, (0.5 + 0.6 * dr_)) * (1 - wiek / 1.1), shadow=None)
        q = _obietnica_auto(kol, T, t)
        if q:
            x, y, rot, sx, dr = q
            st.put(J.ford(kol), x, y, P_MAPA_AUTA + 0.002 * n, h=34, anchor=(0.5, 0.9), sx=sx, rot=0, shadow=(2, 3, 3, 0.3))
            if kol == "czarny":
                st.put(J.rek("kapelusz_fedora"), x + 2 * sx, y - 26, P_MAPA_AUTA + 0.004, h=12, anchor=(0.5, 1.0), tint=(1.0, 0.9, 0.7))
    koniec(st, w, t)


WAGON_SLONCE = 7.9   # s na osi Studio: słońce drży i ucieka w górę za kadr (marker reżysera 23.11)
WAGON_NOC = 8.5      # s na osi Studio: zapada noc (reżyser 24.11: „w połowie ujęcia 20 zmieniłbym słońce na księżyc, ściemnił na noc”)
WAGON_KSIEZYC = 9.1  # s na osi Studio: zjeżdża księżyc
WAGON_GWIAZDY = 9.5  # s na osi Studio: zjeżdżają gwiazdy („aha i jeszcze dodał gwiazdy”)
WAGON_PIEKLO = 6.6   # s na osi Studio: „…called it the Devil's Back Porch” — tabliczka nad szałasami


def wagon_noc(t):
    """Noc w West Dallas w chwili t ujęcia „wagon” (0 — dzień, 1 — noc); ujęcie „indyki” zaczyna się w tej nocy."""
    return ease(pr(t, rs("wagon", WAGON_NOC), rs("wagon", WAGON_NOC + 1.5) - rs("wagon", WAGON_NOC)))


def s_wagon(st, w, t, T):
    """West Dallas: dymiące kominy, wiadukt, szałasy w błocie; pod wozem śpi rodzina, mały Clyde wyczołguje się spod koła
    i przeciąga — a słońce, jakby się bało, ucieka za kadr i zapada noc: księżyc, gwiazdy na nitkach; Clyde otwiera puste
    pudełko na obiad i wylatuje z niego ćma, która leci prosto do księżyca.
    Reżyser 24.11: „na ujęciu 20 trzeba coś zrobić, bo jest zbyt nudne; w połowie ujęcia 20 zmieniłbym słońce na księżyc,
    ściemnił na noc, aha i jeszcze dodał gwiazdy” (i w ujęciu 21 z ciemności i księżyca robi się dzień). Marker 23.11
    (7,93 s): „dźwignij powoli słońce za kadr, bo ono też się boi”."""
    w.zmierzch = True
    w.noc = wagon_noc(t)
    kam(st, t, 10, lerp(600, 680, ease(t / T)), lerp(390, 360, ease(t / T)), lerp(1.0, 1.1, ease(t / T)), 0.72)
    w.zawieszki = [("West Dallas, 1920s", 640, 150, pr(t, 1.4, 1.0) * (1 - pr(t, rs("wagon", WAGON_PIEKLO) - 0.4, 0.6)))]
    ts = rs("wagon", WAGON_SLONCE)
    drzy = 4 * math.sin(t * 40) * (ts - 0.5 < t < ts + 0.1)
    west_dallas(st, t + drzy * 0.002, w, slonce_k=None if t < ts else 1 - 0.999 * ease(pr(t, ts, rs("wagon", WAGON_SLONCE + 1.4) - ts)),
                chmury_k=1 - 0.75 * w.noc)  # nocą chmury wjeżdżają w górę i odsłaniają księżyc i gwiazdy
    if w.noc > 0.01:
        ksiezyc(st, t, ease(pr(t, rs("wagon", WAGON_KSIEZYC), 1.3)), x=1010, y=140)
        gwiazdy(st, t, pr(t, rs("wagon", WAGON_GWIAZDY), 1.6), seed=20)
    # pranie na sznurku między szałasami: kołysze się na wietrze (życie w tle, 1.25)
    k_pr = bk(w, 0.7)
    if k_pr > 0:
        st.line([(860, 470), (990, 486), (1120, 470)], P.miasto + 0.025, width=1.3, color=(70, 60, 50), alpha=0.8 * k_pr)
        for n, x in enumerate((905, 960, 1030, 1080)):
            st.put(J.rek("pranie"), x, 478 + 6 * math.sin(n * 1.3) + (1 - k_pr) * 200, P.miasto + 0.026, h=54, anchor=(0.5, 0.0),
                   rot=5 * math.sin(t * 2.2 + n), tint=((0.92, 0.88, 0.8), (0.8, 0.74, 0.7))[n % 2])
    # rodzina Barrowów śpi pod wozem, między kołami — widać ją nad rampą (przegląd 24.11: leżała schowana za rampą)
    for n, (x, key, hh) in enumerate(((455, "matka_clyde", 150), (585, "dziecko1", 118))):
        lalka(st, t, key, x, hh, 1.0, y=652, flip=1, lean=88, p=P.drzewa + 0.003, rece=(0, 0), shadow=(2, 3, 4, 0.3))
    if t > 1.6:  # „Z” unoszą się znad głów śpiących i gasną (słownik znaków, 1.20)
        for n, (x, y) in enumerate(((560, 632), (665, 636))):
            for m in range(2):
                f_ = ((t - 1.6) * 0.45 + m * 0.5 + n * 0.25) % 1.0
                st.put(J.tag("Z"), x + 30 * f_ + 6 * math.sin(t * 3 + m), y - 70 * f_, P.drzewa + 0.004, h=14 + 10 * f_, anchor=(0.5, 0.5),
                       rot=-10, alpha=min(1.0, (t - 1.6) / 0.5) * math.sin(math.pi * f_), shadow=(2, 3, 3, 0.3))
    wy = ease(pr(t, 3.4, 1.6))
    # gag 31 (GAGI.md, W1 „pusta kasa” — zasiew): na „almost nothing” mały Clyde otwiera blaszane pudełko na obiad, wylatuje ćma
    # i leci prosto do księżyca (ćma do światła)
    pud = ease(pr(t, 10.2, 0.5))
    out_c = lalka(st, t, "clyde_maly", lerp(640, 780, wy), 200, 1.0, lean=lerp(85, 0, wy), lift=-40 * (1 - wy),
                  rece=(lerp(80, 160, ease(pr(t, 5.4, 0.8))) * (1 - ease(pr(t, 6.8, 0.6))) + 75 * pud,
                        lerp(20, 150, ease(pr(t, 5.4, 0.8))) * (1 - ease(pr(t, 6.8, 0.6)))), p=P.lalki,
                  trzyma=(J.rek("kasetka"), 34, (0.5, 0.3), 0, False) if pud > 0 else None)
    if t > 5.6:
        tab(w, t, "YAWN", 800, 330, 5.6, 1.5)
    # „Devil's Back Porch”: tabliczka zjeżdża nad szałasami; Clyde patrzy w górę na słońce, które drży i ucieka
    tab(w, t, "DEVIL'S BACK PORCH", 520, 250, rs("wagon", WAGON_PIEKLO), 2.4)
    if ts - 0.6 < t < ts + 1.2:
        tab(w, t, "!", 905, 240, ts - 0.6, 1.4)
    fc = pr(t, 10.9, 2.6)
    if out_c and 0 < fc < 1:
        mx, my = 1010, 160  # ćma leci spiralą do księżyca i krąży wokół niego
        dojscie = ease(min(1.0, fc / 0.7))
        a = t * 5.0
        r_ = lerp(0, 70, dojscie)
        st.put(J.rek("cma"), lerp(out_c[0], mx, dojscie) + r_ * math.cos(a) * dojscie + 25 * math.sin(fc * 18) * (1 - dojscie),
               lerp(out_c[1] - 10, my, dojscie) + 0.4 * r_ * math.sin(a) * dojscie, P.slonce + 0.02 if dojscie > 0.8 else P.rekwizyty,
               h=lerp(50, 34, dojscie), anchor=(0.5, 0.5), sx=0.3 + 0.7 * abs(math.sin(t * 22)), rot=10 * math.sin(t * 7), shadow=(2, 3, 3, 0.3))
    if t > 11.2:
        tab(w, t, "…", 820, 300, 11.3, 1.8)
    koniec(st, w, t)


INDYKI_SWIT = 0.25  # s akcji: noc z ujęcia 20 mija, wschodzi słońce


def s_indyki(st, w, t, T):
    """Ciężarówka z gdaczącymi indykami stoi przy drodze; nastoletni Clyde i Buck siedzą z tyłu razem z indykami; zza rogu
    wychodzi policjant z gwizdkiem, „STOP!”; chłopcy zeskakują na ziemię i podnoszą ręce, indyki wyfruwają (markery reżysera
    19.11: „podstaw tych ludzi tu na aucie z tyłu razem z tymi indykami”, „tu mają zeskoczyć”)."""
    kam(st, t, 11, 640, 380, 1.0, 0.76)
    # reżyser 24.11: „pamiętaj, w ujęciu 21 musisz z ciemności i księżyca zmienić na słońce” — ujęcie zaczyna się nocą
    # z ujęcia „wagon” (ta sama scena, zwykłe cięcie); księżyc i gwiazdy wjeżdżają w górę, słońce zjeżdża, robi się dzień,
    # a indyki budzą się gulgotem (INDYKI_SWIT, dźwięk w efekty.ZDARZENIA)
    w.zmierzch = True
    w.noc = 1 - ease(pr(t, INDYKI_SWIT, 1.1))
    west_dallas(st, t, w, woz=False, slonce_k=ease(pr(t, INDYKI_SWIT + 0.35, 0.9)), chmury_k=1 - 0.75 * w.noc)
    if w.noc > 0.01:
        ksiezyc(st, t, 1 - ease(pr(t, INDYKI_SWIT - 0.1, 0.8)), x=1010, y=140)
        gwiazdy(st, t, 1 - pr(t, INDYKI_SWIT - 0.2, 0.9), seed=20)
    x = 300
    ciezarowka(st, t, x, 210)
    px, _ = jazda(t, 1.6, 1.2, 1400, 1080)
    for n in range(4):
        uc = ease(pr(t, 3.4 + 0.2 * n, 1.2))
        ix, iy = x - 110 + 40 * n + 300 * uc * (1 if n % 2 else -0.6), 600 - 30 * math.sin(t * 9 + n) * (uc > 0) - 260 * uc
        irot, ip = 20 * uc * (1 if n % 2 else -1) + 6 * math.sin(t * 7 + n), P.auta + 0.004
        if n == 3:  # gag 3 (GAGI.md): ten indyk ląduje na czapce policjanta, stoi na niej, a potem z niej odlatuje za kadr
            lad = ease(pr(t, 4.5, 0.6))
            ucieka = ease(pr(t, 5.7, 0.9))
            hx, hy = punkt("policjant", px, 320, 150, 0)
            ix, iy = lerp(ix, hx - 4, lad), lerp(iy, hy + 36, lad) - 60 * math.sin(math.pi * lad)
            irot, ip = lerp(irot, 4 * math.sin(t * 5), lad), (P.lalki + 0.03 if lad > 0.5 else ip)
            if ucieka > 0:  # odlot z czapki: w górę i za prawą krawędź kadru; policjant stoi dalej
                ix, iy = lerp(hx - 4, 1500, ucieka), lerp(hy + 36, -250, ucieka) - 90 * math.sin(math.pi * ucieka)
                irot = irot + 25 * ucieka
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
    aktorka; z góry kadru spada indyk, który odleciał z czapki policjanta w poprzednim ujęciu, i siada jako jedyna widownia (1.21: wyskok z kadru →
    spadnięcie w następnym ujęciu); na „stage” Bonnie się kłania, indyk gulgocze."""
    kam(st, t, 131, 640, 430, lerp(1.02, 1.12, ease(t / T)), 0.78)
    w.zawieszki = [("Cement City, 1926", 640, 150, pr(t, 0.9, 1.0))]
    for n, x in enumerate((180, 1120)):  # kominy cementowni za szkołą
        Z0.rise(st, J.komin(), x, 600, P.gory_dal, bk(w, 0.1 + 0.05 * n), t, 540 + n, h=360, wob=0.0, haze=0.35)
    # podium z boku szkoły: wzniesiona ręka Bonnie nie zasłania szyldu
    miasto(st, t, w, fasady=(("szkola", 780),), tyl=(("dom", 200), ("dom", 1200)), chodnik=True)
    st.put(J.rek("podium"), 400, STOPY, P.lalki + 0.02, h=130, anchor=(0.5, 1.0))
    uklon = ease(pr(t, 6.1, 0.35)) * (1 - ease(pr(t, 6.9, 0.4)))
    # marker reżysera 23.11 (1,67 s): „daj jej pióro gołębia do pisania” — w wzniesionej ręce pióro (stalówką do zeszytu),
    # zeszyt w drugiej; jedna ręka — jedna rzecz (1.28)
    lalka(st, t, "bonnie", 400, 290, y=STOPY - 112, flip=1, lean=24 * uklon - 4,
          rece=(75, 150 + 12 * math.sin(t * 3) - 120 * uklon), trzyma=(J.rek("zeszyt"), 40, (0.5, 0.5), 0, False),
          trzyma_tyl=(J.rek("pioro"), 30, (0.12, 0.6), -150, False))
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


KAW_NALEWA = (1.45, 3.0)  # nalewanie: dzbanek w górę i w dół (marker reżysera 21.11)
KAW_HUK = 3.6             # dzbanek odstawiony z hukiem


def s_kawiarnia(st, w, t, T):
    """Bonnie w fartuszku trzyma dzbanek za ucho i nalewa kawę do filiżanki na ladzie (marker reżysera 19.11: „ta ma mieć to
    w rękach i ma lać kawę do tej filiżanki”); markery 21.11 (1,57 s): „tu wlewasz kawę” — strumień kończy się w filiżance, za
    jej przednią ścianką; „wlewając, ruszasz tym dzbankiem góra–dół” — dzbanek dwa razy w górę i w dół, strumień raz dłuższy,
    raz krótszy; „tego gościa cofnij w prawo minimalnie, tak żeby gazetę trzymał w ręku, gazeta za ręką, a nie w nim i na głowie”
    — klient stoi o 64 px dalej w prawo, gazeta zostaje tam, gdzie była (przed nim, nie na głowie), dłonie trzymają jej bliższy,
    prawy brzeg i leżą na kartce. Bonnie odstawia dzbanek z hukiem."""
    hk = KAW_HUK < t < KAW_HUK + 0.3
    kam(st, t, 15, 640, 390, 1.15, 0.8, shake=3.0 * hk)
    wnetrze(st, t, w, sciana="paski", okna=(260, 1020), meble=(("lada", 640, 150, P.drzewa),))
    blat = STOPY - 150
    # klient z gazetą: kartka przed nim (tam, gdzie dawniej miał twarz), on sam o 64 px w prawo; dłonie na bliższym brzegu kartki
    czyta_gazete(st, t, "przechodzien2", 884, J.gazeta("DEPRESSION DEEPENS", 5, 360, 480), h=300, flip=-1)
    filx = 700
    st.put(J.rek("kubek"), filx, blat + 2, P.drzewa + 0.01, h=34, anchor=(0.5, 1.0))
    # dzbanek (arkusz 150 × 150, h 60): ucho (0.107, 0.56), dzióbek o (52.8, -12.8) od ucha; przechył 45° → dzióbek nad filiżanką
    ucho = (filx - 56, blat - 96)
    bx = stan_przy("bonnie_kelnerka", ucho, 85, h=290, flip=1)
    kat_lej, _ = siegnij("bonnie_kelnerka", bx, ucho, h=290, flip=1)
    a, b_ = KAW_NALEWA
    podnosi = ease(pr(t, 0.6, 0.6)) * (1 - ease(pr(t, b_ + 0.1, 0.45)))
    przechyl = 45 * ease(pr(t, 1.2, 0.3)) * (1 - ease(pr(t, b_, 0.3)))
    goradol = 14 * math.sin(math.pi * 2 * pr(t, a, b_ - a) * 2) * (a < t < b_)  # dwa razy w górę i w dół
    odstawiony = t >= KAW_HUK
    patrzy = -1 if 7.2 < t < 8.0 else 1  # odprowadza wzrokiem toczące się zielsko
    out = lalka(st, t, "bonnie_kelnerka", bx, 290, flip=patrzy, rece=(lerp(25, kat_lej, podnosi) + goradol, 10),
                trzyma=None if odstawiony else (J.rek("dzbanek"), 60, (0.107, 0.56), przechyl, False))
    if out and a < t < b_ - 0.1:  # strumień kawy z dzióbka do środka filiżanki (koniec za przednią ścianką)
        sx_, sy_ = _off(52.8, -12.8, przechyl)
        st.line([(out[0] + sx_, out[1] + sy_), (filx - 3, blat - 12)], P.drzewa + 0.008, width=3, color=(86, 54, 30), alpha=0.95)
    if odstawiony:  # dzbanek stoi na ladzie tam, gdzie go odstawiła
        st.put(J.rek("dzbanek"), bx + 70, blat + 2, P.drzewa + 0.012, h=60, anchor=(0.36, 1.0), rot=-6 * _bump(t, KAW_HUK + 0.05, 0.2))
    # obrączka od Roya na palcu dłoni, która trzyma dzbanek (kwestia: „still wearing his ring”); idzie za dłonią
    if out and not odstawiony:
        rx_, ry_ = out[0] - 1, out[1] - 7
        st.line([(rx_ - 6, ry_ + 3), (rx_ + 6, ry_ - 3)], P.lalki + 0.035, width=3, color=(214, 178, 74), alpha=0.95)
    # gag 5 (GAGI.md): na „something exciting” przez kawiarnię toczy się kula stepowego zielska; Bonnie odprowadza ją wzrokiem
    tz = pr(t, 7.0, 2.6)
    if 0 < tz < 1:
        zx = lerp(-120, 1400, tz)
        st.put(J.rek("zielsko"), zx, 566 - 90 * abs(math.sin(tz * 9)), P.lalki + 0.03, h=86, anchor=(0.5, 1.0), rot=tz * 900)
    tab(w, t, "SIGH…", bx, 230, 3.2, 1.8)
    koniec(st, w, t)


GARNEK = (420, 544)  # garnek na kuchence (środek dna)


@lru_cache(None)
def _kuchnia_bx():
    """Bonnie stoi tak, żeby dłoń z łyżką była nad środkiem garnka (marker reżysera 21.11: „tu ma być łyżka i koniec ręki
    Bonnie, więc ją cofnij w prawo minimalnie”): dłoń 30 px nad brzegiem garnka, łyżka w dół, do środka."""
    return stan_przy("bonnie", (GARNEK[0], GARNEK[1] - 50 - 30), 113, h=290, flip=-1)


def s_kuchnia(st, w, t, T):
    """W ciasnej kuchni Bonnie miesza kakao (dłoń i łyżka nad środkiem garnka); drzwiami wchodzi Clyde w kapeluszu i uchyla go;
    z nitek zjeżdżają serca — jedno nad Bonnie, drugie nad Clyde'em (markery reżysera 21.11: „nad nią serce”, „nad nim serce”);
    na „he was arrested” serca odjeżdżają w górę, a na nitce nad Clyde'em zjeżdżają kajdanki („nad nim kajdanki”)."""
    kam(st, t, 16, 640, 390, 1.1, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(("kuchenka", 420, 170, None), ("stol", 760, 140, None)))
    # garnek przed łyżką: łyżka znika w garnku, kiedy Bonnie miesza (było: łyżka sterczała z ręki obok garnka)
    st.put(J.rek("garnek"), GARNEK[0], GARNEK[1], P.lalki + 0.03, h=50, anchor=(0.5, 1.0))
    st.put(J.rek("patelnia"), 470, 380, P.drzewa + 0.02, h=21, anchor=(0.93, 0.5), rot=-90)  # wisi na gwoździu; w areszcie w dłoni Bonnie
    lalka(st, t, "przyjaciolka", 640, 290, flip=1, rece=(10, 0))
    bx = _kuchnia_bx()
    lalka(st, t, "bonnie", bx, 290, flip=-1, rece=(113 + 5 * math.sin(t * 6), 0), trzyma=(J.rek("lyzka"), 50, (0.5, 0.9), 180, False))
    cx, _ = jazda(t, 1.2, 1.8, 1180, 900)
    lalka(st, t, "clyde", cx, 320, flip=-1, rece=(lerp(0, 160, ease(pr(t, 3.2, 0.4))) * (1 - ease(pr(t, 4.2, 0.4))), 0), hop=5 * (t < 3.0))
    for n, x in enumerate((bx, 900)):
        # gag 6 (GAGI.md): na „he was arrested” serca odjeżdżają w górę, a na nitce nad Clyde'em zjeżdżają kajdanki
        J.hang(st, J.serce(), x, 250, P.rekwizyty, pr(t, 4.4 + 0.3 * n, 1.0) * (1 - pr(t, 8.2 + 0.1 * n, 0.5)), t, 460 + n, h=60, drop=420)
    J.hang(st, J.rek("kajdanki"), 900, 260, P.rekwizyty, pr(t, 8.7, 0.9), t, 470, h=64, drop=420)
    koniec(st, w, t)


def s_areszt(st, w, t, T):
    """Do kuchni wchodzi policjant i zakuwa Clyde'a w kajdanki; Bonnie z patelnią w dłoni (marker reżysera 21.11: „daj jej
    patelnię!” — zamiast łyżki) woła „HEY!”, biegnie za nimi do drzwi, drzwi trzaskają jej przed nosem (reżyser 19.11: ujęcie
    było „turbo krótkie” — +2 s)."""
    kam(st, t, 17, 700, 390, 1.1, 0.8)
    wnetrze(st, t, w, sciana="kwiaty", okna=(300,), drzwi=(1060,), meble=(("kuchenka", 420, 170, None), ("stol", 760, 140, None)))
    st.put(J.rek("garnek"), GARNEK[0], GARNEK[1], P.lalki + 0.03, h=50, anchor=(0.5, 1.0))
    biegnie = ease(pr(t, 3.5, 0.9))
    # patelnia uniesiona jak do ciosu: rączka w dłoni, patelnia w górę (kreska markera od dłoni w górę)
    lalka(st, t, "bonnie", lerp(_kuchnia_bx(), 930, biegnie), 290, flip=1, rece=(70 + 60 * _bump(t, 4.3, 0.5), 0), hop=5 * (3.5 < t < 4.4),
          lean=-10 * _bump(t, 4.75, 0.25), trzyma=PATELNIA(-80))
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
    """Wnętrze aresztu w Waco: Bonnie (w płaszczu, z patelnią na plecach — ujęcie „waco_przed”, markery 21.11) wyjmuje spod
    płaszcza pistolet i od razu podaje go przez kraty (przemyciła go w ujęciu „waco_przed”);
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
    # w płaszczu i z patelnią na plecach, jak przed aresztem (ujęcie 27, markery 21.11); pistolet spod poły płaszcza od 0,3 s
    bxw, flw = lerp(430, -150, odchodzi), 1 if odchodzi <= 0 else -1
    patelnia_na_plecach(st, "bonnie_plaszcz", bxw, 290, flw)
    piers = punkt("bonnie_plaszcz", 430, 290, 176, 300, flip=1)
    k_pie, s_pie = do_punktu("bonnie_plaszcz", 430, piers, h=290, flip=1)
    do_krat = ease(pr(t, 0.3, 0.8))  # dłoń spod poły płaszcza prosto do krat, po podaniu opada
    kat_b = lerp(k_pie, 95, do_krat) if t < 1.4 else lerp(95, 10, ease(pr(t, 1.4, 0.4)))
    lalka(st, t, "bonnie_plaszcz", bxw, 290, flip=flw, rece=(kat_b, 0), skrot=(lerp(s_pie, 1.0, do_krat), 1.0),
          trzyma=REV() if 0.3 <= t < 1.3 else None, hop=5 * (0 < odchodzi < 1))
    koniec(st, w, t)


def patelnia_na_plecach(st, key, x, h, flip, alpha=1.0, p=None):
    """Patelnia z kuchni na plecach Bonnie (marker reżysera 21.11, ujęcie 27: „włóż patelnię na plecy”): za tułowiem, rączką
    w górę nad ramię; zostaje na plecach w następnych ujęciach tej sceny (Waco)."""
    px_, py_ = punkt(key, x, h, 84, 300, flip=flip)  # dno patelni wystaje za plecami, rączka nad ramieniem
    st.put(J.rek("patelnia"), px_, py_, (P.lalki + 0.01 if p is None else p), h=21, anchor=(0.25, 0.5), rot=-72 * flip, sx=flip, z=-0.08,
           alpha=alpha)


def s_waco_przed(st, w, t, T):
    """Ujęcie pośrednie (reżyser 19.11: „Bonnie jest w kawiarni, nagle jest w więzieniu — musi być jakieś ujęcie pomiędzy”):
    ulica w Waco przed aresztem, zawieszka „Waco, Texas, 1930”. Markery reżysera 21.11: Bonnie (w płaszczu) idzie z patelnią
    z kuchni zamiast rewolweru (1,7 s), zarzuca patelnię na plecy (2,33 s), bierze zza paska rewolwer do ręki (2,97 s), rozgląda się
    i chowa go pod płaszcz (3,97 s: dłoń przy piersi, rewolwer znika pod połą); poprawia beret i z niewinną miną wchodzi do
    środka; „♪”."""
    kam(st, t, 132, 640, 420, lerp(1.0, 1.08, ease(t / T)), 0.78)
    w.zawieszki = [("Waco, Texas, 1930", 640, 130, pr(t, 0.3, 1.0))]
    miasto(st, t, w, fasady=(("dom", 260), ("areszt", 760)), tyl=(("dom", 1180),), chodnik=True)
    K, H = "bonnie_plaszcz", 290
    bx = lerp(-120, 520, ease(pr(t, 0.4, 2.0))) + lerp(0, 230, ease(pr(t, 5.6, 1.0)))
    rozglada = 3.05 < t < 3.55
    fl = -1 if rozglada else 1
    NA_PLECY, BIERZE, CHOWA = 2.33, 2.97, 3.97
    pas = punkt(K, bx, H, 182, 420, flip=1)     # rewolwer za paskiem płaszcza
    piers = punkt(K, bx, H, 176, 300, flip=1)   # poła płaszcza na piersi
    k_pas, s_pas = do_punktu(K, bx, pas, h=H, flip=1)
    k_pie, s_pie = do_punktu(K, bx, piers, h=H, flip=1)
    zarzut = ease(pr(t, 2.0, NA_PLECY - 2.0))                                   # patelnia przez ramię na plecy
    opada = ease(pr(t, NA_PLECY, 0.25))
    do_pasa = ease(pr(t, 2.6, BIERZE - 2.6)) * (1 - ease(pr(t, BIERZE, 0.25)))  # dłoń do paska
    trzyma_rv = BIERZE <= t < CHOWA
    do_piersi = ease(pr(t, 3.6, CHOWA - 3.6)) * (1 - ease(pr(t, CHOWA + 0.05, 0.3)))
    kat = lerp(lerp(40, 200, zarzut), 20, opada) if t < 2.6 else 20
    kat = lerp(kat, k_pas, do_pasa)
    if trzyma_rv:
        kat = lerp(55, k_pie, do_piersi)
    elif t >= CHOWA:
        kat = lerp(k_pie, 10, ease(pr(t, CHOWA + 0.05, 0.3))) + 140 * _bump(t, 4.8, 0.4)
    sk = lerp(1.0, s_pas, do_pasa) if t < BIERZE else lerp(1.0, s_pie, do_piersi) if t < CHOWA + 0.35 else 1.0
    alpha = 1.0 - ease(pr(t, 6.3, 0.5))  # wchodzi w drzwi
    if t < NA_PLECY:
        trz = PATELNIA(lerp(30, -200, zarzut))
    elif trzyma_rv:
        rv = REV()
        trz = (rv[0], rv[1], rv[2], 70 * do_piersi, False)
    else:
        trz = None
    if t >= NA_PLECY:
        patelnia_na_plecach(st, K, bx, H, fl, alpha=alpha)
    lalka(st, t, K, bx, H, flip=fl, alpha=alpha, rece=(kat, 0), skrot=(sk, 1.0), hop=5 * (t < 2.4 or 5.6 < t < 6.6), trzyma=trz)
    if t < BIERZE:  # rewolwer za paskiem płaszcza, kolbą do góry
        rv = REV()
        st.put(rv[0], pas[0], pas[1], P.lalki + 0.015, h=rv[1], anchor=(0.3, 0.75), rot=100, alpha=alpha)
    if rozglada:
        tab(w, t, "…", bx, 230, 3.1, 0.8)
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


def s_po_bramie(st, w, t, T):
    """Przed zamkniętą bramą Eastham stoi Ford z Bonnie za kierownicą. Clyde o kulach dokuśtykuje do auta, wrzuca kulę na tylne
    siedzenie (leży tam potem w akcie II) i wskakuje łukiem do środka: od 3,9 s siedzi w tylnym oknie (marker reżysera 21.11:
    „clyde w aucie” — wcześniej znikał w przenikaniu). Od tej chwili jadą razem (szew: d01_15 → d02_01)."""
    kam(st, t, 133, 640, 400, 1.1, 0.8)
    _brama(st, w, t, 0.0)  # brama zamknięta: Clyde jest już za nią, na drodze (przysiega kończy się przy zamykaniu)
    AX, AH, W_AUCIE = 1080, 230, 3.9
    siedzi = t >= W_AUCIE
    auto(st, t, AX, AH, pasazerowie=[("bonnie", 1, (40, 0))] + ([("clyde", 0, (20, 0))] if siedzi else []))
    k_ = AH / 360.0
    okno_x = AX + (J.FORD_GLOWY[0][0] - 450) * k_
    kula_w = (AX - 120, DROGA_Y - 150)  # kula na tylnym siedzeniu (tak samo jak w ujęciu akt2)
    fk = pr(t, 3.05, 0.35)
    if fk >= 1:
        st.put(J.rek("kula"), kula_w[0], kula_w[1], P.auta - 0.003, h=150, anchor=(0.5, 0.5), rot=64)  # w środku: widać ją przez szybę
    cx = lerp(1000, 1040, ease(pr(t, 0.6, 2.4)))  # kilka kroków od bramy do auta
    if not siedzi:
        skok = pr(t, 3.5, W_AUCIE - 3.5)
        x_ = lerp(cx, okno_x, ease(skok))
        lalka(st, t, "clyde", x_, 320, flip=1, rece=(25 + 8 * math.sin(cx / 26.0) + 60 * (3.0 < t < 3.3), 25),
              trzyma=KULA() if t < 3.05 else None, kuleje=1.0, hop=3 * (0.6 < t < 3.0), lift=70 * math.sin(math.pi * skok))
        if 0 < fk < 1:  # kula leci łukiem przez okno na tylne siedzenie
            hx, hy = dlon("clyde", cx, 85, h=320, flip=1)
            st.put(J.rek("kula"), lerp(hx, kula_w[0], fk), lerp(hy, kula_w[1], fk) - 90 * math.sin(math.pi * fk), P.auta + 0.02, h=150,
                   anchor=(0.5, 0.5), rot=lerp(0, 64 + 360, fk))
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
    # kule Clyde'a (od Eastham) leżą na tylnym siedzeniu: widać je przez szybę (ślad kulawizny w akcie II)
    st.put(J.rek("kula"), x - 120, DROGA_Y - 150, P.auta - 0.003, h=150, anchor=(0.5, 0.5), rot=64)  # w środku auta, za karoserią
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
    lalka(st, t, "clyde", cx, 330, flip=1, rece=(90, 0), trzyma=REV(), hop=3 * (t < 1.6), kuleje=1.0)  # wchodzi kulejąc
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


BUCK_MIAU = 5.70  # s na osi Studio (marker reżysera 24.11)


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
    # marker reżysera 24.11 (5,70 s): „miauu! (i dźwięk dodaj)” — piesek Blanche miauczy jak kot: podskakuje jej w rękach,
    # nad nim tabliczka „MEOW!” (dźwięk kota w efekty.ZDARZENIA, BUCK_MIAU)
    tm = rs("buck", BUCK_MIAU)
    if out and fp <= 0:
        st.put(J.zwierze("piesek"), out[0] + 10, out[1] - 10 - 10 * _bump(t, tm + 0.1, 0.25), P.lalki + 0.03, h=46, anchor=(0.5, 0.6), sx=-1,
               rot=6 * math.sin(t * 4) + 12 * _bump(t, tm + 0.1, 0.3))
    elif out:
        # ląduje nad rampą (przy STOPY rampa zakryłaby pieska)
        st.put(J.zwierze("piesek"), lerp(out[0] + 10, bx + 90, ease(fp)), lerp(out[1] - 10, 652, fp) - 90 * math.sin(math.pi * fp),
               P.lalki + 0.03, h=46, anchor=(0.5, 1.0) if fp >= 1 else (0.5, 0.6), sx=-1, rot=-6 * math.sin(t * 20) * (fp >= 1))
        tab(w, t, "YAP!", bx + 110, 520, 11.5, 1.4)
    podpis(w, t, "Buck Barrow", bx, 230, 1.6, 3.0)
    podpis(w, t, "Blanche Barrow", 1020, 230, 4.6, 3.0)
    tab_tu(st, w, t, "MEOW!", "buck", 905, 372, BUCK_MIAU, dur=1.6)
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
    # marker reżysera 24.11 (0,00 s): „bierze do buzi i gra, a nad nim nuty” — Clyde podnosi saksofon ustnikiem do ust (pół
    # sekundy), dłoń trzyma korpus (ręka w skrócie, 1.28); kiedy gra, z czary wylatują nuty; po „SHHH!” sąsiadki milknie na
    # chwilę, potem gra dalej
    gra = not (3.1 < t < 4.1)
    lean_c = -6 + (4 * math.sin(t * 4) if gra else 0)
    ux, uy = punkt("clyde", 1000, 320, USTA[0], USTA[1] + 4, flip=-1, rot=lean_c)
    pod = 1 - ease(pr(t, 0.05, 0.45))
    mx, my = ux + 2, uy + 70 * pod  # ustnik przy ustach (na początku niżej, w dłoni)
    rs_ = 18 + 5 * math.sin(t * 4) * gra  # czara do przodu, w lewo (lalka patrzy w lewo: wycinek odbity)
    ks = 110 / 360.0
    # punkty na arkuszu saksofonu (160 × 360, ustnik (60, 0)): chwyt na szyjce, środek czary; odbicie sx=-1 → u ujemne
    ox, oy = _off(-(66 - 60) * ks, 170 * ks, rs_)
    gx, gy = mx + ox, my + oy
    ox, oy = _off(-(100 - 60) * ks, 300 * ks, rs_)
    cx_, cy_ = mx + ox, my + oy
    kat, sk = do_punktu("clyde", 1000, (gx, gy), h=320, flip=-1, lean=lean_c)
    lalka(st, t, "clyde", 1000, 320, flip=-1, lean=lean_c, rece=(kat, 20), skrot=(sk, 1.0))
    st.put(J.rek("saksofon"), mx, my, P.lalki + 0.01, h=110, anchor=(60 / 160, 0.0), rot=rs_, sx=-1, shadow=(3, 4, 5, 0.35), z=0.03)
    if t > 0.5:
        for n in range(8):
            f_ = ((t - 0.5) / 1.8 + n / 8) % 1.0
            t_ur = t - f_ * 1.8  # chwila, w której ta nuta wyleciała z czary
            if f_ * 1.8 > t - 0.5 or (3.1 < t_ur < 4.1):
                continue
            st.put(J.nuta(n % 2), cx_ - 40 - 50 * f_ + 18 * math.sin(f_ * 7 + n), cy_ - 30 - 260 * f_, P.rekwizyty, h=28 + 6 * (n % 3),
                   anchor=(0.5, 0.5), rot=12 * math.sin(t * 3 + n), alpha=min(1.0, f_ * 6) * (1 - max(0.0, f_ - 0.75) / 0.25),
                   shadow=(2, 3, 3, 0.3))
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


OFIARY_CZAPKI = (0.0, 0.45)  # s po zbudowaniu podwórka: pierwsza i druga czapka zaczyna spadać


def s_joplin_ofiary(st, w, t, T):
    """Na pustym podwórku przed garażem leżą dwie czapki policyjne; z nitek zjeżdżają podpisy; światło przygasa."""
    kam(st, t, 37, 640, 520, 1.3, 0.8)
    miasto(st, t, w, fasady=(("garaz", 640),), tyl=())
    # markery reżysera 24.11 (0,00 s): „spada czapka”, „spada druga czapka” — czapki spadają z góry po liniach z markerów
    # (kreski ekranu: skąd → dokąd), koziołkują i lądują na podwórku; druga chwilę po pierwszej (dźwięk: efekty.ZDARZENIA)
    t0 = 0.0 if w.get("build") is None else 0.9  # gdy dekoracja buduje się od nowa: czapki spadają, kiedy podwórko stoi
    for n, (x, (s0, s1)) in enumerate(((520, ((283, 100), (464, 547))), (780, ((908, 50), (807, 541))))):
        f = pr(t, t0 + OFIARY_CZAPKI[n], 0.6)
        if f <= 0:
            continue
        rot_k = -10 + 22 * n
        if f < 1:
            ax, ay = ekran_do_swiata(st.cam, *s0, P.lalki + 0.02)
            bx_, by_ = x, 690
            cx_, cy_ = lerp(ax, bx_, f), lerp(ay, by_, f * f)
            st.put(J.rek("czapka_policyjna"), cx_, cy_, P.lalki + 0.02, h=54, anchor=(0.5, 0.6), rot=rot_k + 540 * (1 - f) * (1 if n else -1))
        else:
            odb = 8 * _bump(t, t0 + OFIARY_CZAPKI[n] + 0.72, 0.12)
            st.put(J.rek("czapka_policyjna"), x, 690 - odb, P.lalki + 0.02, h=54, anchor=(0.5, 1.0), rot=rot_k)
    podpis(w, t, "Harry McGinnis", 520, 560, 1.0, T)
    podpis(w, t, "Wes Harryman", 780, 590, 1.8, T)
    koniec(st, w, t, dim=1.0 - 0.25 * ease(pr(t, 3.0, 3.0)))


def s_ciemnia(st, w, t, T):
    """W czerwonym świetle ciemni odbitka pływa w kuwecie; na papierze wyłania się Bonnie z rewolwerem i cygarem."""
    kam(st, t, 38, 640, 430, 1.25, 0.8)
    wnetrze(st, t, w, sciana="cegla", zarowki=(640,))
    # marker reżysera 24.11 (8,97 s): „u góry różne odbitki Bonnie, czarne” — na sznurku pod sufitem przez całą szerokość kadru
    # suszy się siedem odbitek, na każdej czarna Bonnie w innej pozie (kreska markera: ekran x 83–1253, y 37–143)
    pp = P.wzgorza
    (lx, ly), (rx, ry) = ekran_do_swiata(st.cam, 60, 34, pp), ekran_do_swiata(st.cam, 1270, 40, pp)
    st.line([(lx, ly), ((lx + rx) / 2, ly + 10), (rx, ry)], pp, width=1.6, color=(60, 40, 30))
    for n in range(7):
        sx_ = 120 + n * 170
        x, y = ekran_do_swiata(st.cam, sx_, 36 + 10 * math.sin(math.pi * (sx_ - 60) / 1210), pp)
        _, y2 = ekran_do_swiata(st.cam, sx_, 140, pp)
        st.put(J.odbitka_bonnie(n), x, y, pp + 0.001, h=y2 - y, anchor=(0.5, 0.0), rot=3 * math.sin(t * 0.9 + n * 1.7))
        st.put(J.rek("pinezka"), x, y + 2, pp + 0.0015, h=(y2 - y) * 0.12, anchor=(0.5, 0.5), shadow=None)
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
    # drugi samochód gangu (bordo) stoi przy krawężniku: Buck za kierownicą, Blanche obok (szew: Buck i Blanche w akcie III)
    auto(st, t, 1140, 200, kolor="bordo", p=P.auta - 0.012, tint=(0.8, 0.78, 0.82),
         pasazerowie=[("blanche", 0, (0, 0)), ("buck", 1, (40, 0))])
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


DARBY_BLOTO = (0.3, 2.2)  # s akcji: koła buksują, spod tylnego koła leci błoto (marker 24.11: 0,60 s)


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
    # marker reżysera 24.11 (0,60 s): „błoto spod kół wylatuje z buksowania” — koła buksują na starcie, spod tylnego koła
    # (kreska markera) leci w tył łukiem błoto, grudki rozbryzgują się i opadają (dźwięk: efekty.ZDARZENIA, DARBY_BLOTO)
    kq = 300 / 360.0
    for kx, ky in J.KOLO_FORDA[:1]:
        wx, wy = x + (kx - 450) * kq, DROGA_Y + (ky - 356) * kq + J.KOLO_R * kq * 0.7
        for n in range(16):
            f_ = ((t * 2.2 + n / 16) % 1.0)
            t_ur = t - f_ / 2.2
            if not (DARBY_BLOTO[0] <= t_ur < DARBY_BLOTO[1]):
                continue
            st.put(J.rek("plama"), wx - 30 - 260 * f_ - 20 * (n % 3), wy - 260 * f_ * (1 - f_) * (1 + 0.4 * (n % 2)), P.auta + 0.006,
                   h=10 + 8 * (n % 3), anchor=(0.5, 0.5), rot=n * 47 + 300 * f_, tint=(0.55, 0.42, 0.28), alpha=1 - max(0.0, f_ - 0.7) / 0.3,
                   shadow=None)
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


def kapelusz_reka(key, x, h, t, t0, flip=1.0, sink=0.0, lean=0.0, y=STOPY, wroc=True, dol=25.0, spocz=20.0):
    """Zdjęcie nakrycia głowy ręką (uwagi reżysera 23.11: Gault „ściąga ręką kapelusz z głowy i uchyla, i znowu odkłada na
    głowę, a rękę daje w dół przy ciele”; ukłony w finale: „ściąga ręką kapelusz i z nim w ręku przenosi go w dół”).
    Dłoń idzie do czubka głowy (ręka w skrócie, 1.28), kapelusz przechodzi do dłoni w jednej klatce; wroc=True — uchyla
    i odkłada go z powrotem, wroc=False — opuszcza go przy boku (kąt dol). Zwraca (kąt ręki, skrót, kapelusz w dłoni,
    przechył kapelusza) albo None przed t0 i po powrocie."""
    f = t - t0
    if f < 0:
        return None
    from scena import CZUBEK_GLOWY
    gx, gy = punkt(key, x, h, CZUBEK_GLOWY[0], CZUBEK_GLOWY[1] + 22, y=y, flip=flip, rot=lean)
    gy += ease(sink) * h * 1.12
    kat_g, sk_g = do_punktu(key, x, (gx, gy - 6), h=h, y=y, flip=flip, sink=sink, lean=lean)
    if f < 0.35:
        k = ease(f / 0.35)
        return lerp(spocz, kat_g, k), lerp(1.0, sk_g, k), False, 0.0
    if wroc:
        if f < 1.25:
            u = ease(pr(f, 0.35, 0.3)) * (1 - ease(pr(f, 0.95, 0.3)))
            kd, skd = do_punktu(key, x, (gx + 14 * flip * u, gy - 6 - 34 * u), h=h, y=y, flip=flip, sink=sink, lean=lean)
            return kd, skd, True, -24 * u
        if f < 1.6:
            k = ease((f - 1.25) / 0.35)
            return lerp(kat_g, spocz, k), lerp(sk_g, 1.0, k), False, 0.0
        return None
    k = ease(pr(f, 0.35, 0.6))
    return lerp(kat_g, dol, k), lerp(sk_g, 1.0, k), True, -10 * k


def miga(t, t0, n=3, okres=0.32):
    """Mruganie światłem auta (markery reżysera 23.11: „zamrugaj lampą”, „lampy zamrugały”): n błysków od t0 → 0 albo 1."""
    f = (t - t0) / okres
    return 1.0 if 0 <= f < n and f % 1.0 < 0.55 else 0.0


def swiatla(st, x, h=230, y=DROGA_Y, p=None, flip=1.0, przod=0.0, tyl=0.0, przechyl=0.0):
    """Światła Forda na arkuszu auta: reflektor (przód, 795 × 180) i czerwona lampa (tył, 90 × 226); jasność 0..1."""
    k = h / 360.0
    p = P.auta if p is None else p
    for (u, v), jas, kol in (((795, 180), przod, (255, 240, 190)), ((90, 226), tyl, (255, 70, 50))):
        if jas > 0:
            ox, oy = _off((u - 450) * k * flip, (v - 356) * k, przechyl)
            st.put(J.glow(r=256, color=kol), x + ox, y + oy, p + 0.004, w=230 * k, anchor=(0.5, 0.5), mode="add", alpha=0.75 * jas, shadow=None)
            st.put(J.glow(r=256, color=(255, 250, 235)), x + ox, y + oy, p + 0.0045, w=60 * k, anchor=(0.5, 0.5), mode="add", alpha=jas,
                   shadow=None)


def auto_srodek(st, t, cx, cy, h, rot, **kw):
    """Auto obrócone wokół własnego środka (dachowanie): auto() obraca się wokół linii kół."""
    ox, oy = _off(0, -h * 0.5, rot)
    auto(st, t, cx - ox, h, y=cy - oy, przechyl=rot, **kw)


WNOC_SWIATLA = 5.17  # s na osi Studio (marker reżysera 24.11)


def s_wellington_noc(st, w, t, T):
    """Nocna droga przez prerię, Ford pędzi z zapalonymi światłami; tablica „DETOUR” mija się w ciemności, nikt jej nie widzi."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 47, lerp(400, 900, ease(t / T)), 480, 1.1, 0.78, truck=1.0)
    preria(st, t, w, slupy=True, tablice=[("DETOUR", 900)], noc=1.0)
    x = lerp(-200, 1500, t / T)
    auto(st, t, x, 230, pasazerowie=[("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))], tint=(0.7, 0.72, 0.85))
    # marker reżysera 24.11 (5,17 s): „mrugają światła i po chwili się psują” — reflektory mrugają i gasną na dobre; Ford jedzie
    # dalej po ciemku, dlatego nikt nie widzi tablicy DETOUR (dźwięk: efekty.ZDARZENIA, WNOC_SWIATLA)
    tm = rs("wellington_noc", WNOC_SWIATLA)
    jas = 1.0 if t < tm else (mruganie(t, tm, 1.1) if t < tm + 1.1 else 0.0)
    if jas > 0:
        _reflektory(st, x, DROGA_Y, P.auta, k=jas)
        swiatla(st, x, 230, przod=jas)
    elif t < tm + 1.5:  # iskra z przepalonej żarówki
        blysk(st, x + 230 * 0.95, DROGA_Y - 140, P.auta + 0.005, t, tm + 1.15, r=60, kolor=(1.0, 0.85, 0.5), dl=0.15)
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
    # benzyna z dziury po kuli w baku (zasiew: gag w prologu, d00_13): krople spadają na jezdnię, zanim zajmie się wydech
    if t < uderzenie + 0.4:
        for n in range(4):
            gk = (t * 1.4 + n / 4.0) % 1.0
            yk = cy + 50 + 180 * gk
            st.line([(cx - 70 + 6 * n, yk), (cx - 70 + 6 * n, yk + 14)], P.drzewa + 0.03, width=3, color=(220, 175, 70),
                    alpha=0.9 * (1 - gk))
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
    # marker reżysera 24.11 (0,00 s): „przybliż go do nich dwóch” — Clyde stoi tuż przy Bonnie i W.D., jego dłoń trzyma Bonnie
    # pod ramię (stał metr dalej i ciągnął powietrze); dłoń sięga punktu na jej ramieniu (Wytyczne 1.28)
    cel = punkt("bonnie", bx, 290, 150, 250, flip=-1, rot=lerp(60, 10, wyciag))
    cx_ = bx - 62
    kat, _ = siegnij("clyde", cx_, cel, h=320, flip=1, lean=-10)
    lalka(st, t, "clyde", cx_, 320, flip=1, lean=-10, rece=(kat, 60))
    lalka(st, t, "wd", bx + 120, 280, flip=-1, lean=-10, rece=(90, 60))
    for n in range(3):
        g = ((t * 0.5 + n / 3) % 1.0)
        st.put(J.glow(r=256, color=(150, 140, 130)), bx + 20, 640 - 120 * g, P.lalki + 0.02, w=60 + 80 * g, anchor=(0.5, 0.5), alpha=0.5 * (1 - g),
               shadow=None)
    tab(w, t, "AAAA!", bx, 250, 1.4, 2.6)
    koniec(st, w, t, extra=(1.1, 0.9, 0.85))


def s_farma_auto(st, w, t, T):
    """Na podwórku farmy Clyde kuleje do szarego Forda farmera i wsiada za kierownicę; farmer z żoną patrzą z ganku.
    Szew: po zniszczeniu Forda (d04_02) gang potrzebuje auta — tu je bierze, a w d04_05 nim odjeżdża."""
    kam(st, t, 134, 640, 430, 1.05, 0.79)
    preria(st, t, w, slupy=True, plot=False)
    Z0.rise(st, J.fasada("dom"), 420, 660, P.most, bk(w, 0.4), t, 500, h=340, wob=0.0)
    for key, x0 in (("farmer", 180), ("farmerka", 330)):
        lalka(st, t, key, x0, 300, flip=1, rece=(30, 0))
    auto(st, t, 980, 210, p=P.auta)
    cx = lerp(560, 900, ease(pr(t, 0.8, 3.0)))
    wsiada = pr(t, 3.8, 0.4)
    lalka(st, t, "clyde", cx, 320, flip=1, rece=(25 + 8 * math.sin(cx / 26.0), 25), trzyma=KULA(), kuleje=1.0,
          hop=3 * (0.8 < t < 3.8), alpha=1.0 - ease(wsiada))
    koniec(st, w, t)


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


DRZ_WIAZE = (0.6, 2.8)  # s na osi Studio: Bonnie wiąże szeryfów drutem w obłoku bójki
DRZ_SKOK = 3.07  # Bonnie wskakuje do auta (marker 1,57 s + „po 1,5 s”)
DRZ_BYE2 = 2.3  # druga tabliczka „BYE!”
DRZ_ODJAZD = 3.6  # auto rusza, kiedy Bonnie siedzi


def s_drzewo(st, w, t, T):
    """Szeryf i marszałek przywiązani drutem kolczastym do drzewa; Clyde macha im z auta na pożegnanie; „BYE!”.
    Markery reżysera 23.11: „postaw Bonnie, jak rękami coś robi, tam gdzie przywiązani; na czas robienia ukryj środek ich
    ciała z drutami w takiej chmurze jak w bajkach i po 1,5 s Bonnie wskakuje do auta” (1,57 s), „więcej kolczatki na nich”
    (2,13 s), „jeszcze jedna tabliczka bye!” (2,30 s)."""
    kam(st, t, 51, 640, 430, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", krzaki=False)
    Z0.rise(st, J.drzewo(7), 420, 712, P.lalki - 0.004, bk(w, 0.3), t, 510, h=600, wob=0.0)
    w0, w1 = rs("drzewo", DRZ_WIAZE[0]), rs("drzewo", DRZ_WIAZE[1])
    wiaze = w0 < t < w1
    for n, (key, x) in enumerate((("szeryf", 350), ("detektyw", 490))):
        szarp = 4 * math.sin(t * 19 + n * 2) if wiaze else 0.0
        lalka(st, t, key, x + szarp, 300, flip=1 if n else -1, rece=(0, 0), lean=3 * math.sin(t * 3 + n) * (n or t < 8.9) + szarp)
    # gag 39 (GAGI.md): przywiązanemu szeryfowi siada na kapeluszu ptak i zostaje; szeryf: „…”
    fb = pr(t, 8.3, 0.7)
    if fb > 0:
        hx_, hy_ = punkt("szeryf", 350, 300, 152, 62, flip=-1)
        st.put(Z0.bird(int(t * 9) % 2 if fb < 1 else 0), lerp(-80, hx_, ease(fb)), lerp(260, hy_ - 8, ease(fb)) - 40 * math.sin(math.pi * fb),
               P.lalki + 0.03, h=40 if fb < 1 else 34, anchor=(0.5, 1.0), shadow=(2, 3, 3, 0.3))
    tab(w, t, "…", 300, 300, 9.4, 1.8)
    # drut kolczasty: po obłoku dużo więcej zwojów — poziome, ukośne na krzyż, gęste kolce (marker 2,13 s)
    gesto = t >= w1
    zwoje = [((290, y), (560, y + 6)) for y in ((500, 560, 620) if not gesto else (470, 500, 530, 560, 590, 620, 645))]
    if gesto:
        zwoje += [((290, 470), (560, 640)), ((290, 640), (560, 470)), ((300, 520), (550, 600)), ((300, 600), (550, 520))]
    for zn, ((x0, y0), (x1, y1)) in enumerate(zwoje):
        st.line([(x0, y0), (x1, y1)], P.lalki + 0.02, width=3.0, color=(170, 170, 176), alpha=0.95)
        for n in range(int(abs(x1 - x0) / 22)):
            f = (n + 0.5 + 0.3 * (zn % 2)) / (abs(x1 - x0) / 22)
            xx, yy = lerp(x0, x1, f), lerp(y0, y1, f)
            st.line([(xx - 5, yy - 6), (xx + 5, yy + 6)], P.lalki + 0.021, width=2.0, color=(150, 150, 156))
            st.line([(xx + 5, yy - 6), (xx - 5, yy + 6)], P.lalki + 0.021, width=1.6, color=(150, 150, 156))
    # Bonnie przy przywiązanych: ręce szybko w górę i w dół (wiąże), potem łukiem do tylnego okna auta
    sk = rs("drzewo", DRZ_SKOK)
    x, _ = jazda(t, rs("drzewo", DRZ_ODJAZD), 4.0, 900, 1700)
    w_aucie = t >= sk + 0.35
    if not w_aucie:
        # skok łukiem do tylnego okna: w locie lalka przechodzi w wielkość i miejsce pasażera (auto: głowa FORD_GLOWY[0],
        # lalka 0,92 wysokości auta), więc w aucie siedzi dalej ta sama, widoczna w oknie (1.28)
        fs = ease(pr(t, sk, 0.35))
        dh = 230 * 0.92
        stopy_aut = DROGA_Y + (128 - 356) * 230 / 360 + (676 - 128) / 614.0 * dh
        lalka(st, t, "bonnie", lerp(610, x + (372 - 450) * 230 / 360, fs), lerp(300, dh, fs), y=lerp(STOPY, stopy_aut, fs) - 140 * math.sin(math.pi * fs),
              p=lerp(P.lalki + 0.01, P.auta - 0.004, fs), flip=-1 if fs < 0.05 else 1, siedzi=fs > 0.6,
              rece=(60 + 55 * math.sin(t * 16), 70 + 55 * math.cos(t * 16)) if wiaze else (150 * fs, 120 * fs))
    if wiaze:  # obłok bójki: kłęby drgają, kręcą się gwiazdki i kawałki drutu
        k = ease(pr(t, w0, 0.25)) * (1 - ease(pr(t, w1 - 0.25, 0.25)))
        for n in range(7):  # tylko środek ciał (od pasa do kolan), głowy i Bonnie obok widać
            a = n * 0.785 + t * 3
            cx_ = 420 + 95 * math.cos(n * 2.4) + 10 * math.sin(t * 13 + n)
            cy_ = 548 + 22 * math.sin(n * 1.7) + 7 * math.cos(t * 11 + n)
            st.put(J.rek("oblok"), cx_, cy_, P.lalki + 0.03 + 0.001 * n, h=lerp(40, 92 + 12 * math.sin(t * 9 + n), k),
                   anchor=(0.5, 0.5), rot=20 * math.sin(a), shadow=(3, 4, 4, 0.3))
        for n in range(3):
            a = t * 7 + n * 2.1
            st.put(Z0.prop("gwiazdka"), 420 + 130 * math.cos(a), 545 + 30 * math.sin(a), P.lalki + 0.04, h=30 * k, anchor=(0.5, 0.5),
                   rot=t * 300, shadow=(2, 3, 3, 0.35))
    pas = [("clyde", 1, (120 + 30 * math.sin(t * 10), 0))] + ([("bonnie", 0, (110 + 30 * math.sin(t * 9 + 1), 0))] if w_aucie else [])
    auto(st, t, x, 230, pasazerowie=pas)
    tab(w, t, "BYE!", min(x, 1100), 300, 1.4, 3.0)
    tab(w, t, "BYE!", min(x + 136, 1180), 270, rs("drzewo", DRZ_BYE2), 2.4)
    koniec(st, w, t)


def s_noszenie(st, w, t, T):
    """Clyde niesie Bonnie na rękach z auta do pokoju motelu; noga w bandażu; Bonnie krzywi się przy każdym jego kroku."""
    kam(st, t, 52, 640, 450, 1.2, 0.79)
    miasto(st, t, w, fasady=(("motel", 900), ("motel", 380)), tyl=(), chodnik=True)
    auto(st, t, 220, 210, p=P.wzgorza + 0.03)
    x, _ = jazda(t, 0.4, 5.0, 300, 820)
    # markery reżysera 23.11 (1,67 s): „Bonnie połóż tak, głowa w dół na barkach Clyde'a” (kreska od pleców w dół-lewo
    # przez bark w górę-prawo) i „jedną rękę pozginaj w ten sposób na Bonnie” — niesie ją przez bark jak strażak: biodra
    # na barku, głowa zwisa za jego plecami, nogi przed nim; przednia ręka zgięta (skrót) trzyma ją za uda
    hop = 4 * abs(math.sin(x / 26))  # jak lalka(hop=4)
    bx_, by_, _ = bark("clyde", x, 320, flip=1, lift=hop)
    rot = -118 + 4 * math.sin(x / 26)
    biodro = (bx_ - 4, by_ - 8)
    ox, oy = _off(0, -0.46 * 260, rot)  # od stóp do bioder w obróconej lalce
    lalka(st, t, "bonnie", biodro[0] - ox, 260, y=biodro[1] - oy, flip=-1, lean=rot, p=P.lalki + 0.006,  # za jego głową
          rece=(165 + 8 * math.sin(t * 5), 150 + 8 * math.sin(t * 5 + 1)))
    uda = (biodro[0] + _off(0, 0.25 * 260, rot)[0], biodro[1] + _off(0, 0.25 * 260, rot)[1])
    kat, sk = do_punktu("clyde", x, uda, h=320, flip=1, lift=hop)
    lalka(st, t, "clyde", x, 320, flip=1, rece=(kat, 10), kuleje=1.0, hop=4, skrot=(sk, 1.0), p=P.lalki + 0.01)
    if int(x / 52) % 2 == 0:
        tab(w, t, "OW!", x, 260, 1.0, 0.6)
    koniec(st, w, t)


OBOZ_KSIEZYC = 6.8  # s na osi Studio: księżyc zjeżdża na nitce w prawy górny róg


def s_oboz(st, w, t, T):
    """Wieczór przy drodze: auto, pranie na sznurku, zimna puszka fasoli, Bonnie pisze, Clyde czyści karabin."""
    w.noc = 0.7
    kam(st, t, 53, 640, 440, 1.05, 0.79)
    preria(st, t, w, slupy=False, noc=1.0)
    ksiezyc(st, t, ease(pr(t, rs("oboz", OBOZ_KSIEZYC), 1.4)), x=950, y=215)  # marker reżysera 23.11 (7,23 s): „niech wjedzie tu księżyc”
    auto(st, t, 980, 220, p=P.wzgorza + 0.03, tint=(0.8, 0.8, 0.9))
    # drugi samochód gangu (bordo): Buck za kierownicą, Blanche obok; stoją przy ognisku, zaraz za praniem
    auto(st, t, 170, 200, kolor="bordo", p=P.wzgorza + 0.031, tint=(0.8, 0.8, 0.9),
         pasazerowie=[("blanche", 0, (0, 0)), ("buck", 1, (40, 0))])
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


RZEKA_RYBA = 6.9  # czas akcji: ryba wyskakuje po kwestii („po chwili”)


def s_rzeka(st, w, t, T):
    """Bonnie myje włosy w rzece; ryba wyskakuje jej spod ręki; „BRRR!”. Uwaga reżysera 23.11: „wydłuż scenę i daj narrację,
    oraz Ken Burns na myjący kadr głowy i wyskakującą rybę po chwili” — kamera powoli najeżdża na jej głowę, ryba wyskakuje
    w pauzie po kwestii, Bonnie odskakuje, „O!”."""
    e = ease(pr(t, 0.3, RZEKA_RYBA - 0.6))
    kam(st, t, 54, lerp(640, 740, e), lerp(470, 510, e), lerp(1.2, 1.9, e), 0.8, drift=0.3)  # najazd na głowę pochyloną nad wodą
    las(st, t, w, rodzaj="liscie", droga=0.0, krzaki=False, kul=False)
    st.put(J.rzeka_pas(), 640, 790, P.lalki - 0.004, w=2200, anchor=(0.5, 1.0))
    f = pr(t, RZEKA_RYBA, 1.0)
    odsk = math.sin(math.pi * pr(t, RZEKA_RYBA + 0.25, 0.5))
    lalka(st, t, "bonnie", 560, 290, flip=1, lean=40 - 25 * odsk, sink=0.1,
          rece=(130 + 14 * math.sin(t * 9) * (f <= 0) + 30 * odsk, 120 + 14 * math.sin(t * 9 + 1.3) * (f <= 0) + 30 * odsk))
    if 0 < f < 1:
        st.put(J.zwierze("ryba"), lerp(790, 880, f), 690 - 270 * math.sin(math.pi * f), P.lalki + 0.035, h=30, anchor=(0.5, 0.5),
               rot=-70 + 160 * f)
    tab(w, t, "BRRR!", 640, 300, 1.6, 2.2)
    tab(w, t, "O!", 720, 400, RZEKA_RYBA + 0.3, 1.6)
    koniec(st, w, t)


LIST_LOT = (0.4, 4.4)  # czas akcji: list leci 4 s, potem przykleja się do maski


def s_list_ford(st, w, t, T):
    """Na masce Forda leży list na papierze firmowym; zjeżdża podpis „Clyde?” i tabliczka ze znakiem zapytania."""
    kam(st, t, 55, 760, 440, 1.7, 0.8)
    st.dof = 1.4
    preria(st, t, w, slupy=False, kul=False)
    auto(st, t, 640, 300)
    # uwaga reżysera 23.11: „ta kartka ma latać w powietrzu 4 s i wlepić się tak jak teraz” — list frunie zygzakiem przez kadr
    # i przykleja się do maski w tym samym miejscu co wcześniej (plask)
    f = pr(t, LIST_LOT[0], LIST_LOT[1] - LIST_LOT[0])
    if f < 1:
        lx = lerp(420, 800, f) + 120 * math.sin(f * math.pi * 3) * (1 - f)
        ly = lerp(180, 512, f ** 1.4) - 40 * math.sin(f * math.pi * 5) * (1 - f)
        st.put(J.rek("list"), lx, ly, P.auta + 0.004, h=80, anchor=(0.5, 1.0), rot=lerp(20, -70, f) + 35 * math.sin(f * math.pi * 4) * (1 - f))
    else:
        st.put(J.rek("list"), 800, 512, P.auta + 0.004, h=80, anchor=(0.5, 1.0), rot=-70 + 4 * math.sin(math.pi * pr(t, LIST_LOT[1], 0.25)))
    podpis(w, t, "Clyde?", 800, 300, LIST_LOT[1] + 0.3, 3.6)
    tab(w, t, "?", 920, 330, LIST_LOT[1] + 1.0, 3.4)
    # gag 17 (GAGI.md): na „such a fine getaway car” Ford mruga reflektorem, jakby się zawstydził, i nieśmiało trąbi
    for c in (6.4, 6.8):
        if c <= t < c + 0.22:
            st.put(J.glow(), 640 + (842 - 450) * 300 / 360, DROGA_Y + (214 - 356) * 300 / 360, P.auta + 0.01, w=170, anchor=(0.5, 0.5),
                   mode="add", alpha=0.9 * math.sin(math.pi * (t - c) / 0.22), shadow=None, tint=(1.0, 0.95, 0.7))
    tab(w, t, "beep", 1060, 380, 7.2, 1.2)
    koniec(st, w, t)


PL_PANCERNY, PL_OGIEN, PL_GANG, PL_BUCK, PL_BLANCHE, PL_UCIECZKA = 5.6, 7.8, 8.6, 10.3, 12.2, 14.4  # czas akcji (kwestia 0,6–14 s)


def s_platte(st, w, t, T):
    """Teatr cieni, Platte City, lipiec 1933. Uwaga reżysera 23.11: „więcej wyjaśnień w tej scenie” — kwestia mówi kiedy, gdzie,
    co przywiozła policja i jak się wyrwali; w kadrze: zawieszka miejsca i czasu, policja przy dwóch domkach motelu, podjeżdża
    opancerzone auto (podpis „ARMORED CAR”, na słowo), błyski policji, potem gang odpowiada ogniem spod domków; Buck się
    chwieje (podpis), szyba pęka przed Blanche (podpis); Buck i Blanche dochodzą do Forda gangu, który wyrywa się w lewo."""
    w.zawieszki = [("Platte City, Missouri · July 1933", 640, 250, pr(t, 0.6, 1.0) * (1 - pr(t, 6.0, 0.6)))]  # niżej: nad nim rama parawanu
    ogien = PL_OGIEN < t < PL_GANG + 1.2
    kam(st, t, 56, 640, 450, 1.35, 0.79, lens=1.4, shake=3.0 * ogien)
    st.dof = 1.5
    y0, p0, ph = parawan(st, t, w)
    cien_ = dict(tint=(0.08, 0.06, 0.05), alpha=0.85, shadow=None, blur=1.6)
    for n, x in enumerate((420, 820)):
        st.put(J.fasada("motel"), x, y0 - 26, p0 + 0.0005, h=230, anchor=(0.5, 1.0), **cien_)
    # Ford gangu między domkami; po strzelaninie wyrywa się w lewo
    gx = jazda(t, PL_UCIECZKA + 0.8, 2.2, 620, -400)[0]
    auto(st, t, gx, 160, y=y0 - 26, p=p0 + 0.001, flip=-1, szyby=False, **cien_)
    ax, _ = jazda(t, PL_PANCERNY, 2.0, 1500, 1080)
    auto(st, t, ax, 180, y=y0 - 26, p=p0 + 0.0012, flip=-1, szyby=False, **cien_)
    podpis(w, t, "ARMORED CAR", 990, 300, PL_PANCERNY + 1.6, 3.4)
    chwiej = ease(pr(t, PL_BUCK, 1.0))
    idzie = ease(pr(t, PL_UCIECZKA, 0.8))
    if idzie < 1:
        cien(st, t, "buck", lerp(380, 600, idzie), 260, y0 - 26, p0 + 0.002, flip=1, rece=(40, 0),
             lean=-25 * chwiej * (1 - idzie) + 6 * math.sin(t * 6) * (t > PL_BUCK))
        szyba = ease(pr(t, PL_BLANCHE, 0.3))
        cien(st, t, "blanche", lerp(470, 640, idzie), 240, y0 - 26, p0 + 0.002, flip=-1 if idzie <= 0 else 1,
             rece=(120 * szyba * (1 - idzie), 90 * szyba * (1 - idzie)))
    podpis(w, t, "Buck Barrow", 380, 330, PL_BUCK - 0.2, 3.0)
    podpis(w, t, "Blanche", 470, 300, PL_BLANCHE + 0.3, 2.6)
    for n in range(5):  # policja zza opancerzonego auta
        blysk(st, 960 + 30 * n, y0 - 140, p0 + 0.003, t, PL_OGIEN + 0.16 * n, r=220)
    for n in range(4):  # gang odpowiada ogniem spod domków
        blysk(st, 560 + 50 * (n % 2), y0 - 110, p0 + 0.003, t, PL_GANG + 0.22 * n, r=200, kolor=(1.0, 0.85, 0.55))
    if t > PL_BLANCHE:
        for n in range(6):
            f = pr(t, PL_BLANCHE, 0.8)
            st.put(Z0.coin(), 470 + 80 * f * math.cos(n), y0 - 200 - 60 * f * math.sin(n * 2), p0 + 0.003, h=8, anchor=(0.5, 0.5),
                   tint=(0.08, 0.06, 0.05), alpha=0.8 * (1 - f), shadow=None)
    koniec(st, w, t, dim=0.9)


def s_dexfield(st, w, t, T):
    """Świt w lesie w Iowie: z krzaków wychodzą farmerzy i policjanci; Buck leży przy ognisku, Blanche klęczy przy nim i nie chce odejść."""
    kam(st, t, 57, 640, 450, 1.1, 0.79)
    las(st, t, w, rodzaj="liscie", droga=0.0, swit=1.0)
    for n in range(2):
        st.put(Z0.flame(int(t * 10 + 4 * n) % 10), 470 + 20 * n, 694, P.lalki + 0.02, h=80, anchor=(0.5, 1.0), shadow=None)
    lalka(st, t, "buck", 560, 300, flip=1, lean=86, lift=70, rece=(20, 0), p=P.lalki - 0.005)
    # markery reżysera 23.11: „uklęknij ją i zwróć w prawą stronę” (2,60 s) — Blanche klęczy przy Bucku, zwrócona w prawo, ku
    # jego głowie; „tabliczka aaaa” (9,13 s) — krzyk nad nią, kiedy obława podchodzi
    lalka(st, t, "blanche", 700, 290, flip=1, lean=14 + 2 * math.sin(t * 2), sink=0.3, rece=(70 + 6 * math.sin(t * 3), 50))
    tab_tu(st, w, t, "AAAA!", "dexfield", 830, 461, 9.13)
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
        # uwaga reżysera 23.11: „niech ruszają lekko rękami góra dół, jakby pływali”
        pl = math.sin(t * 4.2 + n * 1.3)
        lalka(st, t, key, x + dx + 8 * math.sin(t * 3 + n), h, flip=1, sink=0.32, lean=-6,
              rece=((70 if n < 2 else 40) + 22 * pl, (50 if n == 1 else 20) - 22 * pl))
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
    # markery reżysera 23.11: „tabliczka no way!” (2,07 s) nad Clyde'em za kierownicą i „tabliczka maminsynek po angielsku”
    # (4,53 s) nad Bonnie na tylnym siedzeniu
    tab_tu(st, w, t, "NO WAY!", "wd_odchodzi", 531, 379, 2.07)
    tab_tu(st, w, t, "MAMA'S BOY!", "wd_odchodzi", 445, 361, 4.53)
    koniec(st, w, t)


def s_rodziny(st, w, t, T):
    """Nocą przy polnej drodze stoją dwa auta z wygaszonymi światłami; matki podają przez okna koszyki, Bonnie oddaje pranie."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 60, 640, 440, 1.05, 0.79)
    preria(st, t, w, slupy=True, noc=1.0)
    # uwaga reżysera 23.11: „matki podchodzą do auta, ręce w dół, a Bonnie rzuca przez dach do góry im pranie na koszyki” —
    # matki idą od swojego auta z koszykami w opuszczonych rękach; na „bringing laundry” (gag 19) Bonnie wyrzuca z okna sztukę
    # za sztuką łukiem nad dachem i każda wpada do koszyka
    rzuty = [8.9 + 0.38 * n for n in range(8)]
    zamach = max([math.sin(math.pi * pr(t, c - 0.2, 0.35)) for c in rzuty] + [0.0])
    auto(st, t, 420, 220, pasazerowie=[("bonnie", 0, (80 + 80 * zamach, 0)), ("clyde", 1, (40, 0))], tint=(0.7, 0.72, 0.85))
    auto(st, t, 980, 210, kolor="czarny", flip=-1, p=P.auta + 0.005, tint=(0.7, 0.72, 0.85))
    kosze = []
    for n, (key, x) in enumerate((("matka_bonnie", 650), ("matka_clyde", 770))):
        d = ease(pr(t, 1.0 + 0.6 * n, 2.0))
        mx = lerp(1060 + 60 * n, x, d)
        out = lalka(st, t, key, mx, 280, flip=-1, rece=(14, 10), tint=(0.75, 0.75, 0.88), hop=4 * (0 < d < 1))
        if out:
            st.put(J.rek("koszyk"), out[0], out[1], P.lalki + 0.03, h=36, anchor=(0.5, 0.2), tint=(0.8, 0.8, 0.9))
            kosze.append((out[0], out[1] + 8))
    okno = (420 + (372 - 450) * 220 / 360 + 26, DROGA_Y + (128 - 356) * 220 / 360 - 6)
    for n, c in enumerate(rzuty):
        f = pr(t, c, 0.7)
        if f <= 0 or len(kosze) < 2:
            continue
        kx, ky = kosze[n % 2]
        tn = ((0.82, 0.8, 0.92), (0.9, 0.78, 0.8), (0.8, 0.86, 0.8))[n % 3]
        if f < 1:
            st.put(J.rek("pranie"), lerp(okno[0], kx, f), lerp(okno[1], ky, f) - 230 * math.sin(math.pi * f), P.lalki + 0.032, h=30,
                   anchor=(0.5, 0.5), rot=420 * f, tint=tn)
        else:  # leży w koszyku, wystaje nad brzeg
            st.put(J.rek("pranie"), kx + 6 * ((n // 2) % 3 - 1), ky - 4 - 3 * (n // 2), P.lalki + 0.031, h=22, anchor=(0.5, 1.0),
                   rot=10 * math.sin(n), tint=tn)
    ft = pr(t, 10.6, 0.8)
    if ft > 0:
        st.put(J.rek("kanapka"), lerp(650, 430, ease(ft)), 470 - 30 * math.sin(math.pi * min(1, ft)), P.lalki + 0.03, h=12, anchor=(0.5, 0.5),
               tint=(0.85, 0.8, 0.9))
    koniec(st, w, t)


SOWERS_DZIURY = ((4.53, (490.0, 482.0)), (4.93, (802.0, 476.0)))  # markery reżysera 23.11 „dziura w szybie”: sekunda, punkt ekranu


def s_sowers(st, w, t, T):
    """Sowers, listopad 1933: przy drodze czeka auto rodziny (matki, koszyk na „piknik”); Ford podjeżdża, z krzaków po obu
    stronach wyskakują ludzie szeryfa Dallas i strzelają za wcześnie; Ford z przestrzelonymi szybami ucieka; nad Bonnie i nad
    Clyde'em „OUCH!” — oboje mają kule w nogach. Uwaga reżysera 23.11: „zastanów się, czy dobrze jest narysowane całe to ujęcie
    według opisu sceny i narracji” (dodane: auto rodziny i koszyk — „family picnics”, podpis szeryfa — „the Dallas sheriff”,
    strzały z luf, dwa „OUCH!” — „both of them … in their legs”); markery: policjant „bardziej po lewej”, drugi „bardziej po
    prawej” (2,93 s), „dziura w szybie” (4,53 i 4,93 s)."""
    w.noc, w.moon = 1.0, 1.0
    kam(st, t, 61, 640, 440, 1.05, 0.79, shake=2.0 * (3.2 < t < 4.4))
    las(st, t, w, rodzaj="liscie", krzaki=True, noc=1.0)
    # auto rodzin na poboczu w głębi: matki w oknach, koszyk z jedzeniem na masce
    auto(st, t, 900, 190, p=P.wzgorza + 0.03, kolor="bordo", tint=(0.62, 0.62, 0.78),
         pasazerowie=[("matka_bonnie", 0, (0, 0)), ("matka_clyde", 1, (20 * (t > 3.2), 0))])
    st.put(J.rek("koszyk"), 960, DROGA_Y - 112, P.wzgorza + 0.032, h=40, anchor=(0.5, 1.0), tint=(0.7, 0.7, 0.85))

    def xc(tt):
        return jazda(tt, 0.0, 3.2, -200, 600)[0] if tt < 4.6 else jazda(tt, 4.6, 3.2, 600, 1700)[0]
    x = xc(t)
    traf = 3.4
    pas = [("bonnie", 0, (0, 0)), ("clyde", 1, (40, 0))]
    drg = 5 * math.sin(t * 30) * (traf < t < traf + 0.5)
    auto(st, t, x, 230, dziury=12 if t > traf else 0, pasazerowie=pas, tint=(0.7, 0.72, 0.85), przechyl=drg * 0.3)
    if t > traf:  # dziury po kulach w szybach, w miejscach z markerów (przyklejone do auta)
        for n, (sek, (sx, sy)) in enumerate(SOWERS_DZIURY):
            wx, wy = ekran_do_swiata(st.cam, sx, sy, P.auta)
            dx = wx - xc(rs("sowers", sek))
            if t > traf + 0.15 * n:
                st.put(J.rek("dziura"), x + dx, wy, P.auta + 0.003, h=26, anchor=(0.5, 0.5), shadow=None)
    # ludzie szeryfa w krzakach: jeden z lewej, drugi z prawej (markery), szeryf z lewej w głębi z podpisem
    for n, (key, kx) in enumerate((("szeryf", 150), ("policjant", 300), ("policjant2", 1100))):
        k = ease(pr(t, 1.2 if n == 0 else 2.6 + 0.2 * n, 0.4))  # szeryf wygląda z krzaków pierwszy, kiedy lektor go nazywa
        fl = -1 if kx > 640 else 1
        out = lalka(st, t, key, kx, 300, k, flip=fl, rece=(88, 0), trzyma=CEL(150), tint=(0.75, 0.75, 0.88),
                    p=P.drzewa - 0.01 - 0.004 * (n == 0))
        if out and k > 0.9:
            for m in range(3):  # strzał z końcówki lufy (1.28); punkt zaokrąglony — dłoń drga, a jeden błysk to jeden dźwięk
                blysk(st, round((out[0] + fl * 108) / 10) * 10, round((out[1] - 2) / 10) * 10, P.drzewa, t, 3.2 + 0.3 * m + 0.1 * n, r=170)
    podpis(w, t, "Dallas Sheriff Smoot Schmid", 270, 300, 1.6, 2.6)
    tab(w, t, "OUCH!", x - 70, 330, 4.0, 2.6)   # nad Bonnie (tylne siedzenie)
    tab(w, t, "OUCH!", x + 90, 300, 4.3, 2.4)   # nad Clyde'em (kierowca)
    koniec(st, w, t)
