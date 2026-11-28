"""Pomocnicze funkcje filmu o Szamilu na silniku uklad.py (Wytyczne 1.28 i 1.32, reżyser 28.11.2026: „miałeś się zastosować
do wszystkich wytycznych od najnowszych po najstarsze obowiązujące”).

Każda rzecz w dłoni, każdy jeździec i każdy siedzący ma właściciela w buforze identyfikatorów i swoją kontrolę:
- rzecz w dłoni — `w_dloni` (punkt chwytu arkusza w dłoni + kontrola „w dłoni”);
- żołnierz — karabin w TYLNEJ dłoni, pionowo za plecami (karabin trzymany przednią ręką zasłaniał twarz, a z daleka
  z czerwoną opaską czapki wyglądał jak krzyż — przegląd 28.11);
- jeździec — koń jest obiektem, biodro lalki siedzi w siodle (kontrola „siedzi w siodle”: maska konia przy biodrze);
- siedzący na kamieniu, łóżku, w wozie — ta sama kontrola z maską siedziska.
Kontrolę każdej klatki robi `kontrola_ukladu.py`.
"""
import math
from functools import lru_cache

import scena as SW
import uklad as U
import zestaw_kz as J
from papier import back
from scena import P, STOPY

RZEDY = dict(U.RZEDY_WNETRZA, gory=P.gory, most=P.most, droga=P.droga, wzgorza=P.wzgorza, drzewa=P.drzewa,
             tlo=P.lalki - 0.02, dom=P.lalki - 0.03, sciana_domu=P.lalki - 0.02)
BIODRO = (150, 414)  # punkt arkusza korpusu na spodzie tułowia lalki siedzącej (korpus ucięty pod biodrami)

# punkty chwytu (piksele arkusza rek_kz): rękojeść, drzewce, róg kartki
CHWYT = {"szabla": (60, 44), "karabin": (156, 49), "kindzal": (40, 70), "flaga_biala": (16, 250), "choragiew": (20, 300),
         "czerkieska": (24, 64), "kartka_list": (30, 80), "lupa": (240, 240), "ksiazka_ros": (24, 160),
         "pioro": (170, 30), "swieca": (45, 210)}


def uk(st, t):
    """Układ tej klatki (jeden na Stage)."""
    u = getattr(st, "uklad", None)
    return u if u is not None and u.st is st else U.Uklad(st, t, RZEDY)


@lru_cache(None)
def ark(key):
    return U.Ark(J.rek_kz(key), J.rek_kz_img(key))


def w_dloni(st, t, nazwa, key, szk, h, rot=0.0, reka="przod", z=None, **kw):
    """Rekwizyt filmu w dłoni lalki za punkt chwytu; rot — kierunek rzeczy w kadrze (dla lalki zwróconej w prawo)."""
    if szk is None:
        return None
    u = uk(st, t)
    z = (0.08 if reka == "przod" else -0.046) if z is None else z
    return u.w_dloni(nazwa, ark(key), szk, CHWYT[key], h, rot * szk["flip"], reka=reka, z=z, **kw)


def lalka(st, t, nazwa, key, x, h=300, **kw):
    return uk(st, t).lalka(nazwa, key, x, h, **kw)


def zolnierz(st, t, nazwa, key, x, h, y=STOPY, rzad="lalki", flip=1.0, glebia=0.0, hop=0.0, k=1.0, dl=None):
    """Żołnierz z karabinem z bagnetem w tylnej dłoni, pionowo za plecami (lufa nad ramieniem)."""
    szk = lalka(st, t, nazwa, key, x, h, y=y, rzad=rzad, flip=flip, glebia=glebia, hop=hop, k=k, przod=4, tyl=-6)
    w_dloni(st, t, f"karabin ({nazwa})", "karabin", szk, (dl or h * 0.62) * 90 / 520, rot=-90, reka="tyl")
    return szk


def jezdziec(st, t, nazwa, key, x, y=STOPY, rzad="lalki", flip=1.0, h=170, k=1.0, seed=0, galop=1.0, glebia=0.0, przod=10.0,
             tyl=0.0, pasazer=None, dziecko=None):
    """Koń (obiekt „koń (nazwa)”) i jeździec w siodle; pasazer / dziecko — klucze lalek siedzących za i przed jeźdźcem.
    Każdy siedzący ma kontrolę „siedzi w siodle” (maska konia przy biodrze). Zwraca szkielet jeźdźca."""
    if k <= 0:
        return None
    u = uk(st, t)
    hk = h * 0.95
    sk = hk / 440
    yy = y + (1 - back(k, 1.2)) * hk * 1.2 - abs(math.sin(t * 9 + seed)) * 6 * galop
    rot = 2.2 * math.sin(t * 9 + seed) * galop
    kon = f"koń ({nazwa})"
    p = u.p(rzad, glebia)
    u.put(kon, J.zwierze("kon"), x, yy, p - 0.001, "zwierze", h=hk, anchor=(0.5, 1.0), sx=flip, rot=rot, z=-0.02)
    siodlo_y = yy - 300 * sk

    def siedzacy(nazwa_, key_, dx, h_, gl):
        f = J.figura(key_)
        sc = h_ / f.wys
        # jeździec wjeżdża RAZEM z koniem: jego położenie liczy się z siodła (yy konia ma już wysunięcie), więc k = 1 —
        # osobne wysuwanie lalki rozjeżdżało biodro i siodło o 18–99 px w pierwszych 0,3–0,9 s (kontrola 28.11)
        szk_ = u.lalka(nazwa_, key_, x + dx * flip, h_, rzad=rzad, glebia=glebia + gl, y=siodlo_y + (f.stopa - BIODRO[1]) * sc,
                       flip=flip, siedzi=True, k=1.0, wejscie=False, przod=przod if nazwa_ == nazwa else 30, tyl=tyl)
        if szk_:
            u.dotyka(kon, (*szk_["punkt"](*BIODRO), p), f"{nazwa_} siedzi w siodle", 4.0)
        return szk_
    szk = siedzacy(nazwa, key, -7, h, 0.4)
    if pasazer:
        siedzacy(f"{pasazer} (za {nazwa})", pasazer, -56, h * 0.95, 0.2)
    if dziecko:
        siedzacy(f"{dziecko} (przed {nazwa})", dziecko, 34, h * 0.62, 0.6)
    return szk


def siedzi_na(st, t, kto, szk, na, tol=4.0):
    """Kontrola: biodro siedzącej lalki leży na masce siedziska (kamień, łóżko, wóz, wielbłąd)."""
    if szk:
        uk(st, t).dotyka(na, (*szk["punkt"](*BIODRO), szk["p"]), f"{kto} siedzi na: {na}", tol)


def y_siedzi(key, h, y_siedziska):
    """Linia stóp lalki siedzącej (korpus bez nóg), przy której biodro leży na wysokości y_siedziska."""
    f = J.figura(key)
    return y_siedziska + (f.stopa - BIODRO[1]) * h / f.wys


def zaprzeg(st, t, nazwa, x, y, p, flip, h_kon=120, woznica="woznica", h_w=150, siedzisko=None, dx_kon=None, galop=0.5, seed=0):
    """Koń w zaprzęgu przed pojazdem (wóz, kibitka, armata) i woźnica na koźle (Wytyczne 1.6: „wóz i powóz ciągnie koń,
    a ktoś nim powozi”). x — przód pojazdu (dyszel), flip — kierunek jazdy; siedzisko = (x, y) kozła i nazwa pojazdu."""
    u = uk(st, t)
    hk = h_kon * 0.95
    yy = y - abs(math.sin(t * 7 + seed)) * 3 * galop
    xk = x + (dx_kon if dx_kon is not None else hk * 560 / 440 * 0.5) * flip
    u.put(f"koń ({nazwa})", J.zwierze("kon"), xk, yy, p + 0.002, "zwierze", h=hk, anchor=(0.5, 1.0), sx=flip,
          rot=1.5 * math.sin(t * 7 + seed) * galop)
    with u.obiekt(f"uprząż ({nazwa})", "rzecz"):
        st.line([(x, y - hk * 0.45), (xk - hk * 0.3 * flip, yy - hk * 0.55)], p + 0.003, width=2.2, color=(70, 50, 36), alpha=0.95)
    if siedzisko and woznica:
        (sx, sy), pojazd = siedzisko
        u.rzedy[f"kozioł ({nazwa})"] = p - 0.001
        szk = u.lalka(f"woźnica ({nazwa})", woznica, sx, h_w, rzad=f"kozioł ({nazwa})", y=y_siedzi(woznica, h_w, sy), flip=flip,
                      siedzi=True, wejscie=False, przod=lambda s_: w_zasiegu(s_, (xk - hk * 0.3 * flip, yy - hk * 0.6)))
        siedzi_na(st, t, f"woźnica ({nazwa})", szk, pojazd, 6.0)
        if szk:
            with u.obiekt(f"lejce ({nazwa})", "rzecz"):
                st.line([szk["przod"]["dlon"], (xk + hk * 0.35 * flip, yy - hk * 0.75)], p + 0.003, width=1.4, color=(50, 36, 26), alpha=0.9)


def pkt(key, u, v, x, y, h, anchor=(0.5, 1.0), sx=1.0):
    """Punkt (u, v) arkusza rekwizytu w kadrze, gdy wycinek stoi kotwicą `anchor` w (x, y) i ma wysokość h. Wycinek jest
    przycięty do papieru (Sprite crop), więc liczy się z arkusza Ark, a nie z pełnego płótna — burta wozu liczona
    z nieprzyciętego arkusza wypadała o połowę niżej i wóz zasłaniał księżne w całości (przegląd 28.11)."""
    a = ark(key)
    fu, fv = a.ulamek(u, v)
    w = h * a.ws / a.hs
    return x + (fu - anchor[0]) * w * sx, y + (fv - anchor[1]) * h


def w_zasiegu(s, cel, f=0.92, reka="przod"):
    """Cel dłoni przycięty do zasięgu ręki (ramię + przedramię × f): dłoń idzie w stronę celu, ale nie dalej, niż sięga —
    póki postacie dopiero podchodzą (uścisk, lejce), ręka wyciąga się ku partnerowi zamiast wyrywać się z barku."""
    bx, by = s["bark_" + reka]
    L = sum(s["L"]) * f
    dx, dy = cel[0] - bx, cel[1] - by
    d = math.hypot(dx, dy)
    return cel if d <= L or d == 0 else (bx + dx * L / d, by + dy * L / d)
