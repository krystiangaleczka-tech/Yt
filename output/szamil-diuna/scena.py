"""Świat filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune”: stan sceny, kamera, światło, lalki
i scenografie (kopia świata „Bonnie and Clyde” z 27.11.2026; scenografie tego filmu na końcu pliku).

Wzór: output/powstanie-japonii/scena.py (te same liczby lalek, kamery i światła). Stan świata liczy się z kamieni milowych
rozpiski (`po("palce")` = po ujęciu o kluczu „palce”), a nie z numerów ujęć. Ujęcie dostaje stan z początku, zmienia go
w czasie (swoje wydarzenie) i woła scenografię: `teatr_gazet()`, `preria()`, `miasto()`, `wnetrze()`, `eastham()`, `las()`,
`wawoz()`, `parawan()`, `drukarnia()`, `mapa_scena()`, `cmentarz()`, `jarmark()`, `kino()`, `ganek()`.

Lalki (`lalka`) to korpus z dwiema rękami na zawiasie w barku (zestaw_bc.Figura): `rece=(przód, tył)` w stopniach,
0 — ręka opuszczona, 90 — wyciągnięta przed siebie, 160 — wzniesiona. W dłoni przedniej ręki może być rekwizyt.
Auta (`auto`) jadą lewo–prawo; pasażerów widać przez szyby (stoją za karoserią, szkło kładzie się na wierzch).
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/szamil-diuna/ujecia"))

import zestaw_kz as J  # noqa: E402  (dokłada output/pierwszy-cesarz do ścieżki: papier.py, zestaw.py)
from dane import ujecia  # noqa: E402
from papier import CX, CY, H, W, Cam, back, clamp, ease, ease_out, noise, settle  # noqa: E402,F401

Z0 = J.Z0
P = J.P
KOL = [u[2] for u in ujecia()]
I = {k: n for n, k in enumerate(KOL)}

RAMPA = 676  # górna krawędź rampy: lalki stoją za nią
STOPY = 708  # linia stóp lalek na planie lalek (stopy chowają się za rampą)
DROGA_Y = 694  # linia kół aut na planie aut (P.auta)
BUDOWA = {"t": None}  # render: sekundy od początku budowania dekoracji w bieżącym ujęciu (None — dekoracja już stoi)
# Sekundy z uwag i markerów reżysera są na osi Studio, w ujęciu z prawdziwym nagraniem lektora; akcja ujęcia biegnie w rytmie
# tempa lektora (render.czas_akcji). render ustawia CZAS["akcji"]: (klucz ujęcia, sekunda na osi) → czas akcji.
CZAS = {"akcji": None}


def rs(klucz, s):
    """Sekunda reżysera w ujęciu `klucz` (oś Studio) → czas akcji ujęcia; bez renderu (np. testy) bez zmian."""
    f = CZAS["akcji"]
    return f(klucz, s) if f else s


def dekoracja(st, *a, **kw):
    """st.put dla kawałka dekoracji stawianego wprost w ujęciu (kurtyny przed ukłonami): stoi od początku budowy, nie czeka
    jak rekwizyt (render.po_budowie)."""
    st.put(*a, **kw)


def wejscie(d=1.0, dur=0.6):
    """Aktorzy i auta wchodzą dopiero, gdy dekoracja się zbuduje (ujęcie otwierające scenę)."""
    b = BUDOWA["t"]
    return 1.0 if b is None else pr(b, d, dur)
P.auta = 0.78
P.droga_dal = 0.58


class Stan(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def stan(i):
    """Stan świata na początku ujęcia i (od 0) — księga świata (szkic E): siwy Szamil od Gunibu, powaga od śmierci syna do pieczątki."""
    po = lambda k: i > I[k]
    f = lambda c: 1.0 if c else 0.0
    return Stan(build=None, noc=0.0, sun=1.0, sun_xy=(905, 110), moon=0.0, clouds=[1.0, 1.0, 1.0], zawieszki=[], kulisy=True,
                mgla=0.0, szamil=("szamil_stary" if i >= I["gunib"] else "szamil"), syn_wrocil=f(po("syn_wraca")),
                powaga=f(I["smierc"] <= i <= I["stempel"]))


# ---------- czas, kamera, światło ----------

def lerp(a, b, k):
    return a + (b - a) * k


def pr(t, a, d):
    """Postęp 0..1 wydarzenia, które zaczyna się w chwili a i trwa d sekund."""
    return clamp((t - a) / d)


def bk(w, d, dur=0.7):
    """Postęp wjazdu elementu dekoracji przy zmianie scenografii (w.build — sekundy od początku budowania)."""
    b = w.get("build")
    return 1.0 if b is None else pr(b, d, dur)


def kam(st, t, i, x, y, m, pf, lens=None, truck=0.6, drift=1.0, shake=0.0):
    """Kamera ujęcia: wózek jedzie bokiem (paralaksa), kierunek zmienia się co ujęcie, lekkie pływanie z ręki."""
    r = random.Random(int(t * 24) + i)
    T = st.__dict__.get("T", 6.0)
    side = 1 if i % 2 == 0 else -1
    slide = side * 34 * drift * (min(t, T) / max(T, 0.1) - 0.5) / max(1.0, m ** 0.5)
    st.cam = Cam(x, y, m, pf, lens, truck, dx=slide + 9 * drift * noise(t, 91 + i, 0.12) + 2.6 * drift * noise(t, 93 + i, 0.3)
                 + shake * r.uniform(-1, 1), dy=1.8 * drift * noise(t, 92 + i, 0.19) + shake * r.uniform(-1, 1), trucky=0.0)
    st.focus = pf


def swiatlo(st, w, t, extra=(1.0, 1.0, 1.0), dim=1.0):
    """Dzień albo noc (w.noc 0..1) + migotanie lampy sceny; od Grapevine chłodniejsze, przygaszone światło (powaga)."""
    n = w.noc
    g = (lerp(1.0, 0.62, n), lerp(1.0, 0.72, n), 1.0)
    pw = w.get("powaga", 0.0)
    g = (g[0] * lerp(1.0, 0.93, pw), g[1] * lerp(1.0, 0.95, pw), g[2])
    st.grade = tuple(a * b for a, b in zip(g, extra))
    st.dim = dim * (1 + 0.012 * noise(t, 5, 5.0)) * lerp(1.0, 0.9, n)


# ---------- lalki ----------

def _off(du, dv, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return c * du - s * dv, s * du + c * dv


OCZY = ((137, 124), (171, 122))  # środki oczu na arkuszu korpusu (zestaw_bc._korpus_img)
CZUBEK_GLOWY = (152, 70)
USTA = (174, 160)
SLOMA = {"gault"}  # źdźbło słomy w ustach we wszystkich ujęciach (marker reżysera 23.11, ujęcie „noc”)


def lalka(st, t, key, x, h=300, k=1.0, y=STOPY, p=None, flip=1.0, lean=0.0, sink=0.0, lift=0.0, rece=(0.0, 0.0), tint=None,
          trzyma=None, seed=None, hop=0.0, alpha=1.0, shadow=True, blur=None, oczy_x=0.0, gwiazdki=0.0, kuleje=0.0, siedzi=False,
          skrot=(1.0, 1.0), tyl_przed=False, trzyma_tyl=None, kapelusz_reka=False, kapelusz_rot=0.0):
    """Lalka na patyczku: wysuwa się zza rampy (k), opada pod nią (sink), obraca się (flip: 1 w prawo, -1 w lewo),
    pochyla (lean, stopnie). hop — podskok przy jeździe na listwie (z położenia x). kuleje — przy jeździe lalka kołysze się
    na jedną stronę (Bonnie po Wellington, Clyde po Eastham). trzyma = (sprite, wysokość, kotwica, obrót, za_ręką).
    oczy_x — śmierć: X na oczach; gwiazdki — zamroczenie (słownik znaków, wytyczne 1.20). skrot = (przednia, tylna) — skrót ręki
    zgiętej ku kamerze (dłoń przy ustach: ręka jest jednym odcinkiem, więc zgięcie w łokciu gra jej skrócenie); tyl_przed — tylna
    ręka przed tułowiem (sięga do ust albo przez pierś, kiedy przednia trzyma rewolwer; marker reżysera 21.11, ujęcie 12).
    trzyma_tyl — rzecz w tylnej dłoni (jedna ręka — jedna rzecz, 1.28; pióro i zeszyt Bonnie, marker 23.11).
    kapelusz_reka — nakrycie głowy zdjęte i trzymane w przedniej dłoni (tak, jak leżało na głowie, gdy dłoń była przy czubku
    głowy — zamiana w jednej klatce, 1.28), kapelusz_rot — jego przechył (uchylanie). Lalki z SLOMA mają źdźbło w ustach.
    Zwraca położenie dłoni."""
    seed = sum(map(ord, key)) if seed is None else seed
    k = k * wejscie(1.0 + 0.08 * (seed % 5))
    if k <= 0 or sink >= 1:
        return None
    f = J.figura(key)
    p = P.lalki + 0.01 if p is None else p
    sc = h / f.wys
    yy = y + (1 - back(k, 1.2)) * h * 1.1 + ease(sink) * h * 1.12 - lift - abs(math.sin(x / 26.0)) * hop
    rot = 0.5 * noise(t, seed, 0.45) + lean + settle((k - 0.75) / 0.25 if k < 1 else 0, 1.5, 3) + kuleje * 4 * math.sin(x / 30.0)
    flip = math.copysign(max(abs(flip), 0.035), flip)
    af = (f.cw / 2, f.stopa)
    ax, ay = af[0] / f.cw, af[1] / f.ch
    out = None
    kw = dict(tint=tint, alpha=alpha, shadow=shadow, blur=blur)
    for name, ang, sk in (("tyl", rece[1], skrot[1]), ("przod", rece[0], skrot[0])):
        bx, by = f.bark[name]
        dx, dy = _off((bx - af[0]) * sc * flip, (by - af[1]) * sc, rot)
        sx_, sy_ = x + dx, yy + dy
        arot = rot - flip * ang
        z = (0.03 if tyl_przed else -0.05) if name == "tyl" else 0.05
        st.put(f.arm, sx_, sy_, p, h=f.ah * sc, anchor=(f.zawias[0] / f.aw, f.zawias[1] / f.ah), rot=arot, sx=flip, sy=sk, z=z, **kw)
        hx, hy = _off(0, f.dlon * sc * sk, arot)
        if name == "przod":
            out = (sx_ + hx, sy_ + hy, arot)
        elif trzyma_tyl:
            spr_, ph_, anc_, orot_, follow_ = trzyma_tyl[:5]
            st.put(spr_, sx_ + hx, sy_ + hy, p, h=ph_, anchor=anc_, rot=(arot if follow_ else rot) + orot_ * flip, sx=flip,
                   z=z + 0.004, **kw)
    kap = f.kapelusz if kapelusz_reka else None
    st.put(f.siedzi if siedzi else (f.bez_kapelusza if kap else f.body), x, yy, p, h=f.ch * sc, anchor=(ax, ay), rot=rot, sx=flip, **kw)
    kk = f.s["szer"]
    na_ark = lambda u, v: _off((f.cw / 2 + (u - 150) * kk - af[0]) * sc * flip, (v - af[1]) * sc, rot)
    if kap and out:
        spr_k, (hxp, hyp) = kap
        gx, gy = f.cw / 2 + (CZUBEK_GLOWY[0] - 150) * kk, CZUBEK_GLOWY[1] + 22
        ox, oy = _off((hxp - gx) * sc * flip, (hyp - gy) * sc, rot + kapelusz_rot * flip)
        st.put(spr_k, out[0] + ox, out[1] + oy, p, h=spr_k.h * sc, anchor=(0.5, 0.5), rot=rot + kapelusz_rot * flip, sx=flip, z=0.06, **kw)
    if key in SLOMA and not siedzi:
        ux, uy = na_ark(*USTA)
        st.put(J.rek("slomka"), x + ux, yy + uy + 2 * sc, p, h=6 * sc / 0.9, anchor=(0.04, 0.5), rot=rot + 18 * flip, sx=flip, z=0.065,
               shadow=None, tint=tint, alpha=alpha)
    if oczy_x > 0:
        for u, v in OCZY:
            ex, ey = na_ark(u, v)
            st.put(Z0.prop("x_oko"), x + ex, yy + ey, p, h=24 * sc * back(min(1.0, oczy_x), 1.6), anchor=(0.5, 0.5), rot=rot,
                   shadow=None, z=0.07, alpha=alpha)
    if gwiazdki > 0:
        cx_, cy_ = na_ark(*CZUBEK_GLOWY)
        for n in range(4):
            a = t * 6.0 + n * math.pi / 2
            st.put(Z0.prop("gwiazdka"), x + cx_ + math.cos(a) * 70 * sc, yy + cy_ - 18 * sc + math.sin(a) * 16 * sc, p,
                   h=30 * sc * gwiazdki, anchor=(0.5, 0.5), rot=t * 200 + n * 40, shadow=(2, 3, 3, 0.35),
                   z=0.09 if math.sin(a) > 0 else -0.09)
    if trzyma and out:
        spr, ph, anc, orot, follow = trzyma[:5]
        zz = trzyma[5] if len(trzyma) > 5 else 0.08  # 0.08: przed ręką; 0.02: za dłonią (dłoń widać na rzeczy — gazeta)
        # rzecz z napisem (gazeta, zdjęcie, list) nie odbija się razem z lalką zwróconą w lewo — napis byłby lustrzany
        # (przegląd 19.11: „TEXAS TRIBUNE” i „DEPRESSION DEEPENS” od tyłu w rękach klienta kawiarni)
        napis = spr.name.startswith(("gazeta", "zdjecie", "rek-list", "rek-pardon", "rek-parole", "rek-plakat"))
        st.put(spr, out[0], out[1], p, h=ph, anchor=anc, rot=(out[2] if follow else rot) + orot * flip, sx=1.0 if napis else flip, z=zz, **kw)
    return out


# ---- biomechanika lalki (Wytyczne 1.28): ręka to jeden odcinek od barku do dłoni, więc dłoń sięga tylko punktów w odległości
# długości ręki od barku. Najpierw punkt (filiżanka, blat, dłoń partnera), potem kąt ręki z tego punktu — nigdy odwrotnie.
def bark(key, x, h=300, y=STOPY, flip=1.0, lean=0.0, sink=0.0, lift=0.0, ktora="przod", skrot=1.0):
    """Bark lalki w kadrze i długość ręki do dłoni: (x, y, L); skrot — ręka zgięta ku kamerze (lalka(skrot=…))."""
    f = J.figura(key)
    sc = h / f.wys
    yy = y + ease(sink) * h * 1.12 - lift
    af = (f.cw / 2, f.stopa)
    bx, by = f.bark[ktora]
    dx, dy = _off((bx - af[0]) * sc * flip, (by - af[1]) * sc, lean)
    return x + dx, yy + dy, f.dlon * sc * skrot


def siegnij(key, x, cel, h=300, y=STOPY, flip=1.0, lean=0.0, sink=0.0, lift=0.0, ktora="przod"):
    """Kąt ręki (do `rece`), przy którym dłoń wskazuje punkt `cel`; drugi wynik: czy dłoń go dosięga (odległość ≤ ręka)."""
    sx, sy, L = bark(key, x, h, y, flip, lean, sink, lift, ktora)
    dx, dy = cel[0] - sx, cel[1] - sy
    arot = math.degrees(math.atan2(-dx, dy))
    return (lean - arot) * flip, math.hypot(dx, dy) <= L * 1.06


def dlon(key, x, kat, h=300, y=STOPY, flip=1.0, lean=0.0, sink=0.0, lift=0.0, ktora="przod", skrot=1.0):
    """Położenie dłoni przy kącie ręki `kat` (także dla ręki tylnej, która nie ma `trzyma`)."""
    sx, sy, L = bark(key, x, h, y, flip, lean, sink, lift, ktora, skrot)
    hx, hy = _off(0, L, lean - flip * kat)
    return sx + hx, sy + hy


def do_punktu(key, x, cel, h=300, y=STOPY, flip=1.0, lean=0.0, sink=0.0, lift=0.0, ktora="przod"):
    """Kąt i skrót ręki (do `rece` i `skrot`), przy których dłoń leży dokładnie w punkcie `cel` bliżej barku niż długość ręki
    (dłoń przy ustach, na guziku, przy kieszeni): ręka zgina się ku kamerze, więc w rysunku jest krótsza."""
    sx, sy, L = bark(key, x, h, y, flip, lean, sink, lift, ktora)
    kat, _ = siegnij(key, x, cel, h, y, flip, lean, sink, lift, ktora)
    return kat, clamp(math.hypot(cel[0] - sx, cel[1] - sy) / L, 0.35, 1.0)


def stan_przy(key, cel, kat, h=300, y=STOPY, flip=1.0, lean=0.0, sink=0.0, lift=0.0):
    """x lalki, przy którym dłoń wyciągnięta pod kątem `kat` trafia w x punktu `cel` (lalka podchodzi do rzeczy,
    a nie rzecz przyskakuje do dłoni)."""
    sx, sy, L = bark(key, 0.0, h, y, flip, lean, sink, lift)
    arot = lean - flip * kat
    hx, _ = _off(0, L, arot)
    return cel[0] - sx - hx


def punkt(key, x, h, u, v, y=STOPY, flip=1.0, rot=0.0, lift=0.0):
    """Punkt (u, v) arkusza korpusu lalki w kadrze (np. usta — do cygara, ręka — do sztywnego rekwizytu)."""
    f = J.figura(key)
    sc = h / f.wys
    kk = f.s["szer"]
    af = (f.cw / 2, f.stopa)
    dx, dy = _off((f.cw / 2 + (u - 150) * kk - af[0]) * sc * flip, (v - af[1]) * sc, rot)
    return x + dx, y - lift + dy


def cien(st, t, key, x, h, y, p, **kw):
    """Sylwetka lalki w teatrze cieni (czarna, lekko rozmyta, bez własnego cienia)."""
    kw.setdefault("alpha", 1.0)  # pełna czerń: przy przezroczystości ręce rysowały „X” na tułowiu
    return lalka(st, t, key, x, h, y=y, p=p, tint=(0.08, 0.06, 0.05), shadow=None, blur=1.6, **kw)


def jazda(t, a, d, x0, x1, ease_fn=None):
    """Położenie w chwili t przy przejeździe z x0 do x1 w czasie [a, a + d] (łagodny start i koniec)."""
    k = pr(t, a, d)
    return lerp(x0, x1, (ease_fn or ease)(k)), k


# ---------- auta ----------

def auto(st, t, x, h=230, y=DROGA_Y, p=None, flip=1.0, kolor="szary", napis=None, dziury=0, droga=None, pasazerowie=(), tint=None,
         alpha=1.0, shadow=True, kurz=False, przechyl=0.0, lift=0.0, blur=None, szyby=True, kola=True):
    """Ford V8 z boku. (x, y) — środek między kołami na linii jezdni; h — wysokość auta w kadrze. droga — przejechana droga
    w px kadru (obraca koła; domyślnie z x). pasazerowie = [(klucz lalki, indeks miejsca 0 — tył, 1 — kierowca, ręce)]."""
    p = P.auta if p is None else p
    spr = J.ford(kolor, napis, dziury, kurz, lustro=bool(napis) and flip < 0)  # napis na drzwiach nigdy lustrzany
    k = h / 360.0
    kb = wejscie(0.9)
    if kb <= 0:
        return spr
    yb = y - lift + (1 - back(kb, 1.2)) * h * 1.3
    kw = dict(tint=tint, alpha=alpha, blur=blur)
    for poz in pasazerowie:  # (klucz, miejsce: 0/1 albo (x, y) głowy na arkuszu auta, ręce[, obrót: -1 — twarzą do tyłu])
        key, miejsce, rece = poz[:3]
        hx, hy = J.FORD_GLOWY[miejsce] if isinstance(miejsce, int) else miejsce
        dh = h * 0.92  # wysokość lalki
        sx_ = x + (hx - 450) * k * flip
        glowa_y = yb + (hy - 356) * k
        stopy = glowa_y + (676 - 128) / 614.0 * dh
        lalka(st, t, key, sx_, dh, y=stopy, p=p - 0.004, flip=flip * (poz[3] if len(poz) > 3 else 1), rece=rece, lean=przechyl, shadow=None,
              siedzi=True, trzyma=poz[4] if len(poz) > 4 else None, **kw)
    st.put(spr, x, yb, p, h=h, anchor=(0.5, 356 / 360.0), rot=przechyl, sx=flip, shadow=shadow, **kw)
    if szyby:
        st.put(J.ford_szyby(), x, yb, p + 0.001, h=h, anchor=(0.5, 356 / 360.0), rot=przechyl, sx=flip, shadow=None, alpha=0.42 * alpha,
               tint=tint, blur=blur)
    if kola:
        dr = x if droga is None else droga
        for kx, ky in J.KOLO_FORDA:
            ox, oy = _off((kx - 450) * k * flip, (ky - 356) * k, przechyl)
            st.put(J.kolo(), x + ox, yb + oy, p + 0.002, h=2 * J.KOLO_R * k, anchor=(0.5, 0.5),
                   rot=-dr / (J.KOLO_R * k) * 57.3 * flip, shadow=(3, 4, 4, 0.35), **kw)
    return spr


def motocykl(st, t, x, h=150, y=DROGA_Y, p=None, flip=1.0, jezdziec=None, droga=None, rot=0.0, tint=None, alpha=1.0, blur=None):
    """Motocykl policji drogowej; jezdziec — klucz lalki (siedzi: stoi za maszyną, widać go od pasa w górę)."""
    p = P.auta if p is None else p
    k = h / 300.0
    if jezdziec:
        dh = h * 1.55
        lalka(st, t, jezdziec, x - 30 * k * flip, dh, y=y + 0.25 * h - 40 * k, p=p - 0.004, flip=flip, rece=(70, 60), shadow=None, tint=tint,
              alpha=alpha, blur=blur, siedzi=True)
    st.put(J.motocykl(), x, y, p, h=h, anchor=(0.5, 296 / 300.0), rot=rot, sx=flip, tint=tint, alpha=alpha, blur=blur)
    dr = x if droga is None else droga
    for kx, ky in J.MOTO_KOLA:
        ox, oy = _off((kx - 260) * k * flip, (ky - 296) * k, rot)
        st.put(J.kolo(46), x + ox, y + oy, p + 0.002, h=92 * k, anchor=(0.5, 0.5),
               rot=-dr / (46 * k) * 57.3 * flip, tint=tint, alpha=alpha, blur=blur)


def ciezarowka(st, t, x, h=220, y=DROGA_Y, p=None, flip=1.0, lewarek=0.0, kierowca=None):
    """Ciężarówka Ivy'ego; lewarek 0..1 — podniesiona na lewarku pod kabiną. Markery reżysera 23.11 („niżej to koło w ziemię”,
    „podnieś wyżej przód auta i tył niżej”): obraca się wokół tylnego koła, które stoi na ziemi, a przód z przednim kołem
    wisi wyraźnie wyżej na lewarku."""
    p = P.auta if p is None else p
    k = h / 360.0
    przechyl = -7.0 * lewarek * flip
    kx0, ky0 = J.CIEZ_KOLA[0]
    tyl = (x + (kx0 - 410) * k * flip, y + (ky0 - 350) * k)  # oś tylnego koła: zostaje na ziemi
    ox, oy = _off((410 - kx0) * k * flip, (350 - ky0) * k, przechyl)
    bx, by = tyl[0] + ox, tyl[1] + oy + 3 * lewarek
    if kierowca:
        kx_, ky_ = _off((494 - 410) * k * flip, -230 * k, przechyl)
        lalka(st, t, kierowca, bx + kx_, h * 0.92, y=by + ky_ + (676 - 128) / 614 * h * 0.92, p=p - 0.004, flip=flip, shadow=None)
    st.put(J.ciezarowka(), bx, by, p, h=h, anchor=(0.5, 350 / 360.0), rot=przechyl, sx=flip)
    for n, (kx, ky) in enumerate(J.CIEZ_KOLA):
        wx, wy = _off((kx - 410) * k * flip, (ky - 350) * k, przechyl)
        st.put(J.kolo(52), bx + wx, by + wy + (4 * lewarek if n == 0 else 0), p + 0.002, h=104 * k, anchor=(0.5, 0.5))
    if lewarek > 0:
        jx, jy = _off((676 - 410) * k * flip, 0, przechyl)
        st.put(J.lewarek(), bx + jx, y + 4, p + 0.003, h=max(1.0, (y + 4) - (by + jy) + 6), anchor=(0.5, 1.0))


# ---------- znaki teatru ----------

def podpis(w, t, txt, x, y, t0, dur=2.8):
    """Tabliczka z imieniem i rolą nad postacią przy jej pierwszym pojawieniu się (wytyczne 1.15) albo okrzyk ze słownika
    znaków („HA HA!”, „AW!”; 1.20): zjeżdża na nitce w t0, po dur s odjeżdża w górę. (x, y) — środek górnej krawędzi."""
    w.zawieszki = list(w.zawieszki) + [(txt, x, y, pr(t, t0, 0.9) * (1 - pr(t, t0 + dur, 0.6)))]


def iks(st, x, y, t, t0, h=200, p=None, mig=2):
    """Czerwony krzyż nad postacią: miga mig razy od chwili t0 (wyrok, śmierć; słownik znaków 1.20)."""
    p = P.rekwizyty + 0.03 if p is None else p
    for n in range(mig):
        a = t0 + n * 0.48
        if a <= t < a + 0.3:
            k = pr(t, a, 0.08)
            st.put(Z0.prop("x"), x, y, p, h=h * (0.8 + 0.2 * back(k, 1.6)), anchor=(0.5, 0.5), rot=-4 + 8 * n, shadow=(4, 6, 6, 0.45))


def _w_kadrze(st, x, y, p, szer, wys=46, m=14):
    """Punkt zawieszenia tabliczki przesunięty tak, żeby cała tabliczka była w kadrze tej kamery (szkic E, 28.11: zawieszki
    miejsca na y = 40 uciekały za górną krawędź, kiedy kamera była przybliżona albo opuszczona)."""
    cam = getattr(st, "cam", None)
    if cam is None:
        return x, y
    a0, ax, ay = cam.screen(0, 0, p), cam.screen(1, 0, p), cam.screen(0, 1, p)
    kx, ky = ax[0] - a0[0], ay[1] - a0[1]
    if not kx or not ky:
        return x, y
    sw = lambda sx: (sx - a0[0]) / kx
    sh = lambda sy: (sy - a0[1]) / ky
    y = max(y, sh(m))
    y = min(y, sh(H - 70) - wys)  # nad pasem napisów
    lo, hi = sw(m) + szer / 2, sw(W - m) - szer / 2
    if lo < hi:
        x = min(max(x, lo), hi)
    return x, y


def zawieszki(st, t, w):
    for txt, x, y, k in w.zawieszki:
        spr = J.tag(txt)
        x, y = _w_kadrze(st, x, y, P.rekwizyty + 0.02, spr.w * 46 / spr.h)
        J.hang(st, spr, x, y, P.rekwizyty + 0.02, k, t, 90 + len(txt), drop=460, sway=1.6, h=46, shadow=(4, 6, 6, 0.4))


def blysk(st, x, y, p, t, t0, r=260, kolor=(1.0, 0.9, 0.6), dl=0.12):
    """Błysk (strzał, flesz): jasna plama światła dodana na chwilę."""
    if t0 <= t < t0 + dl:
        st.put(J.glow(), x, y, p, w=r, anchor=(0.5, 0.5), mode="add", alpha=0.9 * (1 - (t - t0) / dl), shadow=None, tint=kolor)


# ---------- wspólne kawałki scenografii ----------

def niebo(st, w, noc=None):
    n = w.noc if noc is None else noc
    if w.get("zmierzch") and 0.01 < n < 0.99:
        # noc zapada albo mija w trakcie ujęcia (reżyser 24.11, ujęcia 20–21: „w połowie zmieniłbym słońce na księżyc, ściemnił
        # na noc”, „z ciemności i księżyca zmienić na słońce”): papier nocy kładzie się na papier dnia coraz mocniej
        st.put(J.niebo_sp(False), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None)
        st.put(J.niebo_sp(True), CX, CY, P.niebo + 0.0005, w=1760, anchor=(0.5, 0.5), shadow=None, alpha=n)
        return
    st.put(J.niebo_sp(n > 0.5), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None)


def gwiazdy(st, t, k, seed=0, n=16, obszar=(70, 1210, 40, 250)):
    """Gwiazdy z papieru na nitkach (noc, reżyser 24.11: „dodał gwiazdy”): k 0..1 — zjeżdżają po kolei z góry (k maleje —
    wjeżdżają z powrotem w górę); migoczą, każda w swoim rytmie."""
    if k <= 0:
        return
    r = random.Random(seed)
    for i in range(n):
        x, y, sz, v = r.uniform(*obszar[:2]), r.uniform(*obszar[2:]), r.uniform(16, 30), r.uniform(2.5, 6.0)
        ki = clamp(k * 1.7 - 0.7 * i / n)
        if ki <= 0:
            continue
        mig = 0.78 + 0.22 * math.sin(t * v + i * 2.1)
        J.hang(st, Z0.prop("gwiazdka"), x, y, P.slonce + 0.0004 * i, ki, t, 600 + seed + i, h=sz * mig, drop=360 + y, sway=0.9,
               tint=(1.0, 0.96, 0.72), shadow=(2, 3, 4, 0.3))


def slonce(st, t, w, k=None, xy=None, alpha=1.0):
    k = w.sun if k is None else k
    x, y = xy or w.sun_xy
    if k > 0 and w.noc < 0.5:
        st.put(J.glow(), x, y + 85 - (1 - back(k, 1.1)) * 520, P.slonce, w=620, anchor=(0.5, 0.5), mode="add", alpha=0.30 * ease(k) * alpha,
               shadow=None, z=-1)
        J.hang(st, J.slonce_bc(), x, y, P.slonce, k, t, 1, w=140, shadow=(5, 7, 9, 0.30), haze=0.1)


def ksiezyc(st, t, k, x=980, y=150):
    if k > 0:
        st.put(J.glow(), x, y + 54 - (1 - back(k, 1.1)) * 480, P.slonce, w=560, anchor=(0.5, 0.5), mode="add", alpha=0.26 * ease(k),
               shadow=None, tint=(0.75, 0.85, 1.0), z=-1)
        J.hang(st, J.moon(), x, y, P.slonce, k, t, 2, drop=480, w=96, shadow=(5, 7, 9, 0.3))


def chmury(st, t, w, k=(1.0, 1.0, 1.0), haze=1.0):
    for i, (name, x, y, wd) in enumerate((("cloud_left", 230, 70, 520), ("cloud_center", 690, 34, 560), ("cloud_right", 1090, 120, 460))):
        J.hang(st, J.S(name, 0.5), x + 6 * noise(t, 30 + i, 0.08), y, P.chmury + i * 0.008, min(k[i], bk(w, 0.1 + 0.15 * i, 0.9)), t, 4 + i,
               w=wd, sway=0.5, strings=(0.3, 0.7), shadow=(7, 10, 11, 0.26), haze=0.08 * haze,
               tint=((lerp(1.0, 0.55, w.noc), lerp(1.0, 0.58, w.noc), lerp(1.0, 0.7, w.noc)) if w.get("zmierzch") and w.noc > 0.01
                     else (0.55, 0.58, 0.7) if w.noc > 0.5 else None))


def rampa(st, k=1.0):
    """Rampa sceny; w układzie (uklad.py) to obiekt „rampa” — chowa stopy lalek i jest dozwolonym zasłonięciem w kontroli
    „widać ≥ …” (Wytyczne 1.32)."""
    if k > 0:
        u = getattr(st, "uklad", None)
        if u is not None:
            u.put("rampa", J.stage_floor(), CX, RAMPA + (1 - ease_out(k)) * 90, P.rampa, w=2100, anchor=(0.5, 0.0), shadow=(0, -7, 9, 0.45))
            return
        st.put(J.stage_floor(), CX, RAMPA + (1 - ease_out(k)) * 90, P.rampa, w=2100, anchor=(0.5, 0.0), shadow=(0, -7, 9, 0.45))


def kulisy(st, t, w, dol=True, gora=True, gazeta=True):
    """Przedplan: róg pierwszej strony gazety zwisający z góry kadru i suche trawy przy rampie — nieostre, mijają kamerę
    najszybciej (rama „z papieru”, księga świata: teatr z gazet)."""
    if not w.kulisy:
        return
    if gora and gazeta:  # przedplan: gałąź z liśćmi zwisająca z góry kadru (nieostra)
        st.put(Z0.bough(1), -60, -120, 0.95, w=420, anchor=(0.0, 0.0), rot=-8 + 1.5 * noise(t, 301, 0.3), blur=4.0,
               shadow=(8, 12, 16, 0.35), tint=(0.62, 0.66, 0.52))
    if dol:
        st.put(Z0.reeds(1), 1270, 770, 0.94, h=230, rot=1.2 * noise(t, 302, 0.4), blur=3.5, shadow=None, tint=(0.80, 0.70, 0.46))
        st.put(Z0.reeds(2), 40, 776, 0.93, h=190, rot=1.0 * noise(t, 303, 0.4), blur=3.0, shadow=None, tint=(0.78, 0.68, 0.44))


def pas(st, t, name, y, p, k=1.0, seed=0, dx=0.0, haze=0.0, tint=None, w_=2000):
    """Pas prerii (trawa, horyzont) wysuwany od dołu; y — dolna krawędź arkusza."""
    spr = J.pasmo(name, seed)
    Z0.rise(st, spr, CX + dx, y, p, k, t, 700 + seed + len(name), w=w_, wob=0.0, lift=320, haze=haze, anchor=(0.5, 1.0), tint=tint)


# ---------- scenografie ----------

def teatr_gazet(st, t, w, k=1.0):
    """Scena teatru z gazet: tło z wielkich stron gazet na nitkach, podłoga sceny, rampa (tytuł, obietnica, puenta)."""
    st.put(J.niebo_sp(False), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None, tint=(0.82, 0.74, 0.64))
    for n, (x, y, rot) in enumerate(((150, -40, -4), (420, -70, 3), (690, -50, -2), (960, -72, 4), (1220, -44, -3))):
        J.hang(st, J.gazeta(J.NAGLOWKI[(n + 1) % len(J.NAGLOWKI)], 20 + n, 360, 480), x, y, P.miasto + 0.01 * n, min(k, bk(w, 0.1 + 0.1 * n)),
               t, 60 + n, w=300, rot0=rot, drop=600, sway=0.8, strings=(0.2, 0.8), shadow=(6, 9, 10, 0.3))
    Z0.rise(st, J.podloga((120, 86, 60)), CX, 790, P.droga, min(k, bk(w, 0.5)), t, 77, w=2000, anchor=(0.5, 1.0), lift=200, wob=0)
    rampa(st, min(k, bk(w, 0.7, 0.6)))


def preria(st, t, w, droga=1.0, slupy=True, wiatrak=False, plot=False, mesa=False, zielen=False, tablice=(), kolor_drogi=(186, 158, 116),
           kul=True, gazeta=True, noc=None):
    """Preria lat 30.: niebo, słońce albo księżyc, chmury, horyzont (stoliwa), pasy trawy, polna droga w poprzek sceny, słupy
    telegraficzne z drutami, wiatrak, płot. tablice = [(napis, x)] — tablice przy drodze."""
    niebo(st, w, noc)
    slonce(st, t, w)
    ksiezyc(st, t, w.moon)
    chmury(st, t, w)
    if mesa:
        pas(st, t, "mesa", 560, P.gory_dal, bk(w, 0.1), seed=1, haze=0.25)
    pas(st, t, "dal", 600, P.rownina, bk(w, 0.15), seed=2, haze=0.15)
    tr = "zielen" if zielen else "trawa"
    pas(st, t, tr + "1" if not zielen else "zielen", 640, P.gory, bk(w, 0.25), seed=3, haze=0.05)
    if wiatrak:
        k = bk(w, 0.45)
        Z0.rise(st, J.wiatrak("wieza"), 300, 600, P.miasto, k, t, 81, h=300, wob=0.2)
        st.put(J.wiatrak("kolo"), 300, 600 - 300 * 0.95 + (1 - back(k, 1.3)) * 320, P.miasto + 0.002, h=130, anchor=(0.5, 0.5),
               rot=t * 40, shadow=(3, 4, 4, 0.3)) if k > 0 else None
    if slupy:
        k = bk(w, 0.5)
        xs = (-80, 380, 840, 1300)
        if k > 0:
            for n, x in enumerate(xs):
                Z0.rise(st, J.slup(), x, 650, P.most, k, t, 82 + n, h=330, wob=0.15)
            for n in range(len(xs) - 1):
                a, b = xs[n], xs[n + 1]
                yt = 650 - 330 * 0.94 + (1 - back(k, 1.3)) * 330
                st.line([(a, yt), ((a + b) / 2, yt + 26), (b, yt)], P.most - 0.001, width=1.2, color=(50, 44, 40), alpha=0.7)
    if droga > 0:
        Z0.rise(st, J.droga(0, kolor_drogi), CX, 726, P.droga + 0.06, min(droga, bk(w, 0.35)), t, 83, w=2200, wob=0.0, lift=140,
                anchor=(0.5, 1.0))
    for n, (txt, x) in enumerate(tablice):
        Z0.rise(st, J.tablica(txt), x, 640, P.wzgorza, bk(w, 0.6 + 0.1 * n), t, 85 + n, h=210, wob=0.4)
    if plot:
        Z0.rise(st, J.plot(), CX, 664, P.wzgorza + 0.01, bk(w, 0.55), t, 84, w=1700, wob=0.0)
    pas(st, t, tr + "3" if not zielen else "zielen2", 1010 if droga > 0 else 900, P.lalki + 0.06, bk(w, 0.4), seed=4)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=gazeta)


def miasto(st, t, w, fasady=(("kawiarnia", 300), ("stacja", 900)), tyl=(("dom", 120), ("bank", 640), ("dom", 1140)), latarnie=(),
           noc=None, chodnik=True, kul=True, swiatlo_okien=None):
    """Miasteczko lat 30.: niebo, tylny rząd budynków (przymglony), główny rząd fasad z szyldami, chodnik, jezdnia."""
    niebo(st, w, noc)
    slonce(st, t, w)
    ksiezyc(st, t, w.moon)
    chmury(st, t, w)
    sw = (w.noc > 0.5) if swiatlo_okien is None else swiatlo_okien
    for n, (r, x) in enumerate(tyl):
        Z0.rise(st, J.fasada(r, n + 5, sw), x, 600, P.miasto - 0.03, bk(w, 0.15 + 0.08 * n), t, 90 + n, h=300, wob=0.0, haze=0.3,
                tint=(0.82, 0.8, 0.78))
    for n, (r, x) in enumerate(fasady):
        Z0.rise(st, J.fasada(r, n, sw), x, 652, P.most, bk(w, 0.3 + 0.1 * n), t, 95 + n, h=440, wob=0.0)
    for n, x in enumerate(latarnie):
        Z0.rise(st, J.latarnia(), x, 670, P.wzgorza, bk(w, 0.6), t, 99 + n, h=380, wob=0.2)
    if chodnik:
        Z0.rise(st, J.chodnik(), CX, 690, P.droga + 0.04, bk(w, 0.4), t, 98, w=2200, wob=0.0, lift=100, anchor=(0.5, 1.0))
    Z0.rise(st, J.droga(1, (110, 104, 98)), CX, 760, P.droga + 0.08, bk(w, 0.45), t, 97, w=2200, wob=0.0, lift=140, anchor=(0.5, 1.0))
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, dol=False)


def mruganie(t, t0, dl=None):
    """Jasność migającej lampy (markery reżysera 23.11: „zacznij mrugać lampą”, „lampa zamrugała”): 1 przed t0, potem
    nieregularne przygasanie przez dl s (None — do końca ujęcia)."""
    if t < t0 or (dl is not None and t > t0 + dl):
        return 1.0
    f = t - t0
    v = math.sin(f * 29) * math.sin(f * 7.3 + 1.0) + 0.4 * math.sin(f * 53)
    return 0.22 if v > 0.35 else 1.0


def wnetrze(st, t, w, sciana="kwiaty", podloga=(130, 96, 66), okna=(), drzwi=(), meble=(), zarowki=(), kul=True, noc_za_oknem=None,
            kolor_drzwi=(110, 76, 52), tint=None, jasnosc=1.0):
    """Wnętrze: ściana z tapetą (plan ściany), okna i drzwi, podłoga, meble na planie mebli, wisząca żarówka.
    meble = [(klucz, x, wysokość, plan albo None)] — mebel stoi na podłodze (dół na linii STOPY)."""
    st.put(J.sciana(sciana), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None, tint=tint)
    spod(st, podloga)
    noc = w.noc > 0.5 if noc_za_oknem is None else noc_za_oknem
    for n, x in enumerate(okna):
        J.hang(st, J.okno(noc), x, 150, P.miasto + 0.01, bk(w, 0.2 + 0.1 * n), t, 120 + n, h=300, drop=500, sway=0.3, strings=(0.1, 0.9))
    for n, x in enumerate(drzwi):
        Z0.rise(st, J.drzwi(kolor_drzwi), x, 690, P.miasto + 0.015, bk(w, 0.25 + 0.1 * n), t, 125 + n, h=440, wob=0.0)
    Z0.rise(st, J.podloga(podloga), CX, 820, P.droga, bk(w, 0.3), t, 128, w=2200, wob=0.0, lift=220, anchor=(0.5, 1.0))
    for n, (key, x, hh, pp) in enumerate(meble):
        Z0.rise(st, J.mebel(key), x, 712, pp or P.wzgorza, bk(w, 0.45 + 0.08 * n), t, 130 + n, h=hh, wob=0.1)
    for n, x in enumerate(zarowki):
        J.hang(st, J.zarowka(), x, -10, P.drzewa, bk(w, 0.6), t, 140 + n, h=300, drop=420, sway=1.0, string=False,
               tint=None if jasnosc >= 1 else (0.55, 0.52, 0.48))
        st.put(J.glow(), x, 250, P.drzewa, w=520, anchor=(0.5, 0.5), mode="add", alpha=0.18 * bk(w, 0.7) * jasnosc, shadow=None)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, dol=False)


def eastham(st, t, w, mgla=0.0, brama=0.0, wieza=True, kul=True):
    """Farma więzienna Eastham: preria, trzy rzędy bawełny, płot z drutem, wieża strażnicza, brama z szyldem; mgła (styczeń 1934)."""
    niebo(st, w)
    slonce(st, t, w, alpha=1 - mgla)
    chmury(st, t, w)
    pas(st, t, "dal", 590, P.rownina, bk(w, 0.15), seed=12, haze=0.2)
    if wieza:
        Z0.rise(st, J.wieza(), 1040, 600, P.miasto, bk(w, 0.3), t, 150, h=360, wob=0.1)
    for n, (y, p) in enumerate(((610, P.gory), (650, P.wzgorza), (700, P.drzewa))):
        Z0.rise(st, J.bawelna(n), CX + 40 * n, y, p, bk(w, 0.25 + 0.1 * n), t, 151 + n, w=2200, wob=0.0, lift=180, anchor=(0.5, 1.0))
    Z0.rise(st, J.plot(1), CX, 620, P.gory + 0.01, bk(w, 0.4), t, 155, w=1900, wob=0.0)
    if brama > 0:
        Z0.rise(st, J.brama_eastham(), CX, 690, P.wzgorza + 0.02, min(brama, bk(w, 0.5)), t, 156, h=430, wob=0.0)
    if mgla > 0:
        for n in range(3):
            st.put(J.glow(r=256, color=(236, 236, 232)), 300 + 400 * n + 40 * noise(t, 160 + n, 0.1), 560, P.wzgorza + 0.02 * n, w=900,
                   anchor=(0.5, 0.5), mode="over", alpha=0.55 * mgla, shadow=None)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w)


def las(st, t, w, rodzaj="sosny", droga=1.0, krzaki=True, noc=None, swit=0.0, kul=True):
    """Las: sosny Luizjany albo drzewa liściaste Iowy, droga, krzaki z przodu (w krzakach chowa się zasadzka)."""
    niebo(st, w, noc)
    if swit > 0:
        st.put(J.glow(r=256, color=(255, 200, 150)), 1000, 520, P.slonce, w=1400, anchor=(0.5, 0.5), mode="add", alpha=0.35 * swit, shadow=None)
    slonce(st, t, w)
    chmury(st, t, w)
    pas(st, t, "zielen", 620, P.rownina, bk(w, 0.15), seed=21, haze=0.2)
    fn = J.sosna if rodzaj == "sosny" else J.drzewo
    for n, x in enumerate((60, 330, 610, 890, 1170, 1420)):
        Z0.rise(st, fn(n), x, 640, P.gory + 0.01 * (n % 2), bk(w, 0.2 + 0.05 * n), t, 170 + n, h=620 if rodzaj == "sosny" else 420, wob=0.2,
                haze=0.12)
    if droga > 0:
        Z0.rise(st, J.droga(2, (160, 136, 100)), CX, 726, P.droga + 0.06, min(droga, bk(w, 0.35)), t, 178, w=2200, wob=0.0, lift=140,
                anchor=(0.5, 1.0))
    if krzaki:
        for n, x in enumerate((140, 560, 980, 1340)):
            Z0.rise(st, J.krzak(n), x, 700, P.drzewa, bk(w, 0.4 + 0.05 * n), t, 180 + n, h=150, wob=0.3)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False)


def wawoz(st, t, w, przeslo=1.0, kul=True):
    """Wellington nocą: dwa brzegi wąwozu, most bez przęsła, rzeka na dnie."""
    niebo(st, w)
    ksiezyc(st, t, w.moon)
    chmury(st, t, w)
    pas(st, t, "dal", 560, P.rownina, bk(w, 0.15), seed=31, haze=0.2, tint=(0.6, 0.6, 0.7))
    Z0.rise(st, J.rzeka_pas(True), CX, 780, P.wzgorza, bk(w, 0.25), t, 190, w=2200, wob=0.0, lift=160, anchor=(0.5, 1.0))
    Z0.rise(st, J.urwisko(-1), 120, 760, P.drzewa, bk(w, 0.3), t, 191, w=700, wob=0.0, tint=(0.62, 0.6, 0.7))
    Z0.rise(st, J.urwisko(1), 1180, 760, P.drzewa, bk(w, 0.35), t, 192, w=700, wob=0.0, tint=(0.62, 0.6, 0.7))
    if przeslo > 0:
        Z0.rise(st, J.przeslo(), 220, 360, P.drzewa + 0.01, bk(w, 0.4), t, 193, w=560, wob=0.0, tint=(0.62, 0.6, 0.7))
    if kul:
        kulisy(st, t, w, gazeta=False)


def ciemnosc(st, kolor=(0.05, 0.04, 0.04)):
    st.put(Z0.black(), CX, CY, P.niebo, w=2600, anchor=(0.5, 0.5), shadow=None, tint=kolor)


def parawan(st, t, w, pw=1000, y0=700, p0=0.79, swiatlo_k=1.0):
    """Teatr cieni: ciemna scena i podświetlony od tyłu papierowy parawan; zwraca (y0, p0, wysokość) do ustawiania cieni."""
    ciemnosc(st)
    ph = pw * 640 / 1500
    st.put(J.glow(), CX, y0 - ph * 0.5, p0 - 0.004, w=pw * 1.5, anchor=(0.5, 0.5), mode="add", alpha=0.35 * swiatlo_k, shadow=None,
           tint=(1.0, 0.8, 0.55))
    st.put(J.parawan(), CX, y0, p0, w=pw, anchor=(0.5, 1.0), shadow=(6, 8, 10, 0.45), tint=(swiatlo_k, swiatlo_k, swiatlo_k))
    st.spot = (CX, y0 - ph * 0.5, p0, pw * 0.62, 0.55)
    return y0, p0, ph


def drukarnia(st, t, w, obrot=0.0, kul=True, podskok=0.0):
    """Drukarnia gazety: ceglana ściana, maszyna z kręcącymi się wałkami, stos świeżych gazet. podskok — maszyna podskakuje
    (px w górę, razem z wałkami; marker reżysera 21.11: „zaczyna podskakiwać lekko maszyna”)."""
    st.put(J.sciana("cegla"), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    spod(st, (96, 90, 84))
    Z0.rise(st, J.podloga((96, 90, 84)), CX, 820, P.droga, bk(w, 0.2), t, 200, w=2200, wob=0.0, lift=220, anchor=(0.5, 1.0))
    k = bk(w, 0.3)
    Z0.rise(st, J.maszyna(), 600, 700 - podskok, P.wzgorza, k, t, 201, h=470, wob=0.0)
    if k > 0:
        s_ = 470 / 620.0
        for n, (wx, wy) in enumerate(((330, 315), (520, 315), (330, 435), (520, 435), (700, 435))):
            st.put(J.walek(), 600 + (wx - 450) * s_, 700 - podskok - (620 - wy) * s_ + (1 - back(k, 1.3)) * 500, P.wzgorza + 0.003, h=110 * s_ * 1.3,
                   anchor=(0.5, 0.5), rot=obrot * (1 if n % 2 else -1), shadow=(2, 3, 3, 0.3))
    for n, x in enumerate((1040, 1120)):
        Z0.rise(st, J.gazeta("EXTRA!", 40 + n, 360, 480, False), x, 712, P.drzewa, bk(w, 0.5 + 0.1 * n), t, 205 + n, h=170, wob=0.0)
    for n, x in enumerate((250, 980)):
        J.hang(st, J.zarowka(), x, -10, P.drzewa + 0.01, bk(w, 0.6), t, 207 + n, h=300, drop=420, sway=1.0, string=False)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, dol=False)


def spod(st, kolor=(130, 96, 66)):
    """Stały pas podłogi pod ścianą wnętrza: zanim wjedzie podłoga (budowa dekoracji), pod ścianą nie świeci puste płótno."""
    st.put(J.grunt(kolor), CX, 700, P.miasto - 0.002, w=2200, anchor=(0.5, 0.0), shadow=None, tint=(0.7, 0.7, 0.7))


def mapa_scena(st, t, w, k=1.0, x=640, y=40, wd=820, sciana="deski"):
    """Biuro Hamera: ściana z desek i mapa stanów na tablicy (zjeżdża na nitkach)."""
    st.put(J.sciana(sciana, 2), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    spod(st)
    J.hang(st, J.mapa_plansza(), x, y, P.wzgorza, min(k, bk(w, 0.2, 0.9)), t, 210, w=wd, drop=600, sway=0.4, strings=(0.08, 0.92))
    return x - wd / 2, y, wd / 1000.0  # lewy górny róg mapy i skala (do pinezek i nici)


def mapa_punkt(xy0, sk, miasto):
    mx, my = J.MIASTA[miasto]
    return xy0[0] + mx * sk, xy0[1] + my * sk


def cmentarz(st, t, w, kul=True):
    niebo(st, w)
    slonce(st, t, w)
    chmury(st, t, w)
    pas(st, t, "zielen", 620, P.rownina, bk(w, 0.15), seed=41, haze=0.15)
    for n, x in enumerate((120, 360, 600, 860, 1100)):
        Z0.rise(st, J.nagrobek(n), x, 670, P.wzgorza, bk(w, 0.25 + 0.06 * n), t, 220 + n, h=150, wob=0.0)
    Z0.rise(st, J.drzewo(4, (70, 100, 60)), 1180, 640, P.gory, bk(w, 0.2), t, 226, h=420, wob=0.2)
    pas(st, t, "zielen2", 900, P.lalki + 0.06, bk(w, 0.4), seed=42)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False)


def kino(st, t, w, ekran_k=1.0):
    """Kino: czerwone kurtyny, ekran z gazet (na nim film), rząd głów widzów najbliżej kamery."""
    ciemnosc(st, (0.12, 0.08, 0.08))
    Z0.rise(st, J.ekran_kina(), CX, 690, P.miasto, min(ekran_k, bk(w, 0.2)), t, 230, w=1240, wob=0.0)
    return (CX - 1240 / 2 + 130 * 1240 / 1300, 690 - 720 * 1240 / 1300 + 70 * 1240 / 1300, 1240 / 1300)  # lewy górny róg obrazu ekranu


def widownia(st, t, k=1.0):
    Z0.rise(st, J.widownia(0), CX, 800, P.rampa - 0.01, k, t, 231, w=2200, wob=0.0, blur=2.0, lift=200, anchor=(0.5, 1.0))


def west_dallas(st, t, w, woz=True, kul=True, slonce_k=None, chmury_k=1.0):
    """West Dallas lat 20. („Devil's Back Porch”): dymiące kominy cementowni, wiadukt, szałasy i namioty w błocie, wóz Barrowów.
    chmury_k < 1 — chmury unoszą się na nitkach (w nocy odsłaniają księżyc i gwiazdy)."""
    niebo(st, w)
    slonce(st, t, w, k=slonce_k, alpha=0.7)
    chmury(st, t, w, k=(chmury_k,) * 3, haze=1.6)
    for n, x in enumerate((180, 300, 1100)):
        k = bk(w, 0.1 + 0.05 * n)
        Z0.rise(st, J.komin(), x, 600, P.gory_dal, k, t, 240 + n, h=380, wob=0.0, haze=0.35)
        if k > 0.9:
            for m in range(5):
                f = (t * 0.25 + m / 5 + n * 0.3) % 1.0
                st.put(J.glow(r=256, color=(150, 140, 130)), x + 30 * f + 10 * noise(t, 250 + m, 0.3), 600 - 380 * 0.93 - 160 * f,
                       P.gory_dal - 0.005, w=90 + 160 * f, anchor=(0.5, 0.5), alpha=0.5 * (1 - f), shadow=None)
    Z0.rise(st, J.wiadukt(), CX, 590, P.rownina, bk(w, 0.15), t, 245, w=2200, wob=0.0, haze=0.3, lift=300, tint=(0.85, 0.83, 0.82))
    pas(st, t, "bloto", 640, P.gory, bk(w, 0.2), seed=51, haze=0.05)
    for n, (x, v) in enumerate(((90, 0), (420, 1), (980, 2), (1260, 0))):
        Z0.rise(st, J.szalas(v), x, 640, P.miasto, bk(w, 0.25 + 0.07 * n), t, 246 + n, h=230, wob=0.1, haze=0.08)
    Z0.rise(st, J.namiot(0), 760, 650, P.miasto + 0.02, bk(w, 0.45), t, 251, h=200, wob=0.2)
    if woz:
        Z0.rise(st, J.woz(), 560, 712, P.drzewa, bk(w, 0.55), t, 252, h=260, wob=0.0)
    pas(st, t, "bloto", 960, P.lalki + 0.06, bk(w, 0.4), seed=52)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w)


# =====================================================================================================================
# ---------- scenografie filmu o Szamilu (28.11.2026) ----------
# =====================================================================================================================

def _niebo_kz(st, w, kolor=None):
    st.put(J.niebo_sp(w.noc > 0.5), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None, tint=kolor)


def gory_pasmo(st, t, w, which, x, y, p, d=0.1, wd=2000, tint=None, haze=0.0, seed=0):
    Z0.rise(st, J.gory(which, seed), x, y, p, bk(w, d, 0.9), t, 800 + seed + len(which), w=wd, wob=0.0, lift=360, haze=haze,
            anchor=(0.5, 1.0), tint=tint, sy=GORY_SY[which])


GORY_SY = {"dal": 0.55, "srodek": 0.55, "blisko": 0.6}  # pasma niższe niż arkusz: niebo zostaje nad górami (przegląd 28.11)


def teatr_kz(st, t, w, lewa=1.0, prawa=1.0, wydma_k=1.0, gory_k=1.0, kul=True, pora=None):
    """Scena podzielona: z lewej wydma (Arrakis), z prawej ośnieżone góry Kaukazu (prolog i puenta). pora — „noc”, „zmierzch”
    albo None (dzień): akt VI pokazuje tę samą scenę o różnych porach (dekoracje 2, reżyser 28.11)."""
    if pora:
        niebo_pory(st, w, pora)
        if pora == "noc":
            ksiezyc(st, t, bk(w, 0.2), 980, 120)
            gwiazdy(st, t, bk(w, 0.3), seed=15)
        else:
            slonce(st, t, w, xy=(330, 380))
    else:
        _niebo_kz(st, w, (0.96, 0.9, 0.82))
        slonce(st, t, w, xy=(330, 120))
        chmury(st, t, w, k=(0.0, 1.0, 1.0))
    if gory_k > 0:
        Z0.rise(st, J.gory("dal", 2), 1180, 610, P.gory_dal, min(gory_k, prawa, bk(w, 0.1, 0.9)), t, 801, w=1500, wob=0.0, lift=420,
                haze=0.15, anchor=(0.5, 1.0), sy=0.6)
        Z0.rise(st, J.gory("srodek", 1), 1240, 700, P.gory, min(gory_k, prawa, bk(w, 0.3, 0.9)), t, 802, w=1400, wob=0.0, lift=420,
                anchor=(0.5, 1.0), sy=0.62)
    if wydma_k > 0:
        Z0.rise(st, J.wydma(0), 260, 700, P.wzgorza, min(wydma_k, lewa, bk(w, 0.2, 0.9)), t, 803, w=1150, wob=0.0, lift=460,
                anchor=(0.5, 1.0))
    Z0.rise(st, J.podloga((120, 86, 60)), CX, 800, P.droga, bk(w, 0.5), t, 77, w=2000, anchor=(0.5, 1.0), lift=200, wob=0)
    rampa(st, bk(w, 0.7, 0.6))


def kaukaz(st, t, w, aul=None, twierdza=False, rzeka_=False, namioty=0, kul=True, dal=True, blisko=True, gory_tint=None):
    """Góry Dagestanu: trzy pasma, opcjonalnie auł (x), skała Achulgo z twierdzą, rzeka u stóp, namioty oblężenia."""
    _niebo_kz(st, w)
    if w.noc > 0.5:
        ksiezyc(st, t, bk(w, 0.2), 1010, 120)
        gwiazdy(st, t, bk(w, 0.3), seed=7)
    else:
        slonce(st, t, w)
        chmury(st, t, w)
    if dal:
        gory_pasma = (("dal", 560, P.gory_dal, 0.1, 0.2), ("srodek", 620, P.gory, 0.25, 0.0))
        for which, y, p, d, hz in gory_pasma:
            gory_pasmo(st, t, w, which, CX, y, p, d, haze=hz, tint=gory_tint)
    if aul is not None:
        Z0.rise(st, J.aul(0), aul, 650, P.miasto, bk(w, 0.4, 0.8), t, 820, w=760, wob=0.0, lift=420, anchor=(0.5, 1.0))
    if twierdza:
        Z0.rise(st, J.skala(), 660, 700, P.most, bk(w, 0.35, 0.9), t, 821, w=470, wob=0.0, lift=480, anchor=(0.5, 1.0))
        Z0.rise(st, J.twierdza(), 660, 700 - 470 * 620 / 760 + 470 * 100 / 760 + 8, P.most - 0.002, bk(w, 0.55, 0.8), t, 822, w=320,
                wob=0.0, lift=260, anchor=(0.5, 1.0))
    for n in range(namioty):
        Z0.rise(st, J.rek_kz("namiot"), 200 + n * 190 - (n % 2) * 40, 690 + (n % 2) * 6, P.droga + 0.004 * n, bk(w, 0.5 + 0.05 * n),
                t, 830 + n, h=110 - (n % 2) * 14, wob=0.0, anchor=(0.5, 1.0))
    if blisko:
        gory_pasmo(st, t, w, "blisko", CX, 760, P.wzgorza, 0.45, tint=gory_tint)
    if rzeka_:
        Z0.rise(st, J.rzeka(w.noc > 0.5), CX, 772, P.drzewa, bk(w, 0.5), t, 840, w=2000, wob=0.0, lift=160, anchor=(0.5, 1.0))
    rampa(st, bk(w, 0.7, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False)


def gruzja(st, t, w, dwor_k=1.0, kul=True):
    """Cinandali: daleki Kaukaz, winnice, dwór z balkonem, kamienny mur na pierwszym planie."""
    _niebo_kz(st, w)
    slonce(st, t, w)
    chmury(st, t, w)
    gory_pasmo(st, t, w, "dal", CX, 520, P.gory_dal, 0.1, haze=0.3, seed=3)
    Z0.rise(st, J.dwor(), 820, 640, P.miasto, min(dwor_k, bk(w, 0.3, 0.9)), t, 850, w=560, wob=0.0, lift=420, anchor=(0.5, 1.0))
    for n, (y, p) in enumerate(((672, P.most), (716, P.droga))):
        Z0.rise(st, J.winnica(n), CX + (n * 2 - 1) * 120, y, p, bk(w, 0.45 + 0.1 * n), t, 851 + n, w=1500, wob=0.0, lift=200,
                anchor=(0.5, 1.0), sy=0.5)
    rampa(st, bk(w, 0.7, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False)


def mur_przod(st, t, w, x=640, k=1.0):
    Z0.rise(st, J.mur(), x, 740, P.drzewa, min(k, bk(w, 0.6)), t, 860, w=1500, wob=0.0, lift=160, anchor=(0.5, 1.0))


def petersburg(st, t, w, kul=False):
    """Petersburg zimą: szare niebo, złote iglice, śnieg."""
    _niebo_kz(st, w, (0.82, 0.86, 0.94))
    chmury(st, t, w, k=(1.0, 1.0, 1.0))
    Z0.rise(st, J.iglice(), CX, 640, P.miasto, bk(w, 0.2, 0.9), t, 870, w=1500, wob=0.0, lift=460, anchor=(0.5, 1.0))
    rampa(st, bk(w, 0.7, 0.6))


def sala_balowa(st, t, w):
    """Sala balowa: ściana z oknami i kolumnami, żyrandol na nitce, posadzka (pod spodem stała podłoga — przy budowie dekoracji
    test „końca świata” 28.11 znalazł puste płótno pod salą)."""
    spod(st, (130, 92, 62))
    st.put(J.sala(), CX, 740, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None)
    J.hang(st, J.zyrandol(), CX, -20, P.most, bk(w, 0.3), t, 871, w=300, drop=500, sway=0.6, shadow=(6, 9, 10, 0.3))
    rampa(st, bk(w, 0.7, 0.6))


MICZIK_SWIATLO = {"rzeka": 0.0, "przeprawa": 0.15, "syn_wraca": 0.45, "mundur": 0.7, "uscisk": 1.0}  # dzień → złoto → zachód


def miczik(st, t, w, swiatlo=None):
    """Rzeka Miczik: góry w marcu (śnieg na szczytach), dwa kamieniste brzegi, płytki bród pośrodku. swiatlo 0..1 — wymiana
    trwa od dnia do zachodu (dekoracje 2, reżyser 28.11: tę samą scenerię pokazać w inny sposób): niebo, słońce coraz niżej
    i cieplejsze barwy w kolejnych ujęciach sceny (MICZIK_SWIATLO)."""
    swiatlo = swiatlo or 0.0
    if swiatlo > 0.6:
        niebo_pory(st, w, "zmierzch")
    else:
        _niebo_kz(st, w, (lerp(0.92, 1.02, swiatlo / 0.6), lerp(0.94, 0.9, swiatlo / 0.6), lerp(0.98, 0.76, swiatlo / 0.6)))
    slonce(st, t, w, xy=(lerp(980, 1120, swiatlo), lerp(110, 380, swiatlo)))
    chmury(st, t, w)
    ciep = (lerp(1.0, 1.08, swiatlo), lerp(1.0, 0.84, swiatlo), lerp(1.0, 0.8, swiatlo))
    gory_pasmo(st, t, w, "dal", CX, 560, P.gory_dal, 0.1, haze=0.2, seed=5, tint=ciep)
    gory_pasmo(st, t, w, "srodek", CX, 620, P.gory, 0.2, seed=5, tint=ciep)
    Z0.rise(st, J.brzeg(-1), 200, 690, P.most, bk(w, 0.35), t, 880, w=760, wob=0.0, lift=200, anchor=(0.5, 1.0), tint=ciep)
    Z0.rise(st, J.brzeg(1), 1080, 690, P.most, bk(w, 0.35), t, 881, w=760, wob=0.0, lift=200, anchor=(0.5, 1.0), tint=ciep)
    Z0.rise(st, J.rzeka(False), CX, 740, P.droga, bk(w, 0.45), t, 882, w=2000, wob=0.0, lift=160, anchor=(0.5, 1.0), tint=ciep)
    rampa(st, bk(w, 0.7, 0.6))


def izba(st, t, w, okno_noc=False):
    """Kamienna izba w aule: ściana z kamieni, okienko, podłoga z desek (pod spodem ciemne tło: podłoga wyrasta przy budowie
    dekoracji, a kontrola „końca świata” 28.11 znalazła pusty pas pod nią w pierwszej klatce ujęcia „obcy”)."""
    ciemnosc(st, (0.22, 0.16, 0.11))
    st.put(J.mur(2000, 820), CX, 720, P.miasto, w=2000, anchor=(0.5, 1.0), shadow=None, tint=(0.86, 0.82, 0.78))
    st.put(J.okno(okno_noc), 900, 300, P.most, w=200, anchor=(0.5, 0.5))
    Z0.rise(st, J.podloga((110, 80, 56)), CX, 800, P.droga, bk(w, 0.3), t, 890, w=2000, anchor=(0.5, 1.0), lift=200, wob=0)
    rampa(st, bk(w, 0.6, 0.6))


def pustynia(st, t, w, k=1.0):
    """Pustynia: ciepłe niebo, dwie wydmy, słońce (pielgrzymka, puenta)."""
    _niebo_kz(st, w, (1.0, 0.9, 0.78))
    if w.noc > 0.5:
        ksiezyc(st, t, bk(w, 0.2), 980, 120)
        gwiazdy(st, t, bk(w, 0.3), seed=9)
    else:
        slonce(st, t, w)
    Z0.rise(st, J.wydma(1), 900, 640, P.gory, min(k, bk(w, 0.2, 0.9)), t, 895, w=1300, wob=0.0, lift=440, anchor=(0.5, 1.0),
            tint=(0.9, 0.86, 0.8))
    Z0.rise(st, J.wydma(0), 400, 720, P.wzgorza, min(k, bk(w, 0.35, 0.9)), t, 896, w=1300, wob=0.0, lift=460, anchor=(0.5, 1.0))
    rampa(st, bk(w, 0.7, 0.6))


# =====================================================================================================================
# ---------- scenografie szkicu E (przebudowa 28.11.2026) ----------
# Reżyser 28.11 o wersji D: „na każdym ujęciu praktycznie nic się nie dzieje”, a w tle prawie zawsze te same szare góry.
# Szkic E: pustynia Arrakis, Gimry z wieżą, gabinet w Petersburgu, bukowy las Czeczenii, Kaługa — każda scena ma swoje miejsce.
# =====================================================================================================================

def snieg(st, t, k=1.0, n=22, seed=0, p=None, wiatr=0.0):
    """Papierowy śnieg z bibuły: płatki spadają, każdy w swoim tempie; k 0..1 — ile płatków już pada (śnieg zaczyna się)."""
    if k <= 0:
        return
    p = P.rekwizyty - 0.01 if p is None else p
    r = random.Random(seed)
    for i in range(int(n * k)):
        v, x0, f0, sz = r.uniform(0.12, 0.22), r.uniform(-60, 1340), r.random(), r.uniform(7, 12)
        f = (t * v + f0) % 1.0
        st.put(Z0.prop("kulka"), (x0 + wiatr * f * 120 + 18 * math.sin(t * 1.3 + i)) % 1400 - 60, -30 + f * 790, p, h=sz,
               anchor=(0.5, 0.5), tint=(1.0, 1.0, 1.0), shadow=None)


def arrakis_sc(st, t, w, wydmy=1.0, skala=False, skala_x=980, kul=True, dwa_slonca=True):
    """Arrakis z papieru: ciepłe niebo, dwa słońca, trzy wydmy (daleka, środkowa, bliska); skala z jaskinią (sietch) opcjonalnie.
    wydmy 0..1 — wydmy stoją; mniej — zapadają się pod scenę (zwrot w „zamiana”)."""
    _niebo_kz(st, w, (1.0, 0.88, 0.72))
    if dwa_slonca:
        slonce(st, t, w, xy=(300, 110))
        slonce(st, t, w, xy=(420, 170), alpha=0.6)
    else:
        slonce(st, t, w, xy=(330, 120))
    zap = 1.0 - wydmy
    for n, (v, x, y, p, wd, tint) in enumerate(((1, 900, 600, P.gory_dal, 1500, (0.92, 0.86, 0.8)), (0, 300, 660, P.gory, 1400, None),
                                                 (1, 1000, 720, P.wzgorza, 1300, (1.04, 1.0, 0.94)))):
        k = min(1.0, bk(w, 0.1 + 0.15 * n, 0.9))
        if k <= 0 or zap >= 1:
            continue
        Z0.rise(st, J.wydma(v), x, y + ease(zap) * 520, p, k, t, 960 + n, w=wd, wob=0.0, lift=460, anchor=(0.5, 1.0), tint=tint)
    if skala and zap < 1:  # skała przed bliską wydmą (przegląd 28.11: za wydmą jej nie było widać)
        Z0.rise(st, J.skala(), skala_x, 740 + ease(zap) * 520, P.wzgorza + 0.002, bk(w, 0.35, 0.9), t, 965, w=380, wob=0.0, lift=480,
                anchor=(0.5, 1.0), sy=0.62, tint=(1.05, 0.86, 0.64))
    rampa(st, bk(w, 0.7, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False, gora=False)


def jaskinia(st, x, y, p, h=120):
    """Ciemne wejście do jaskini w skale (sietch): półokrągły otwór."""
    if h <= 1:
        return
    st.put(J.rek_kz("jaskinia"), x, y, p, h=h, anchor=(0.5, 1.0), shadow=None)


def gimry_sc(st, t, w, wieza_x=None, aul_x=980, potok=True, kul=True, zmierzch=0.0):
    """Gimry: wąwóz w górach, auł tarasami na zboczu, kamienna wieża przy ścieżce (obiekt „wieża”), potok w dole."""
    _niebo_kz(st, w, (lerp(1.0, 0.86, zmierzch), lerp(1.0, 0.78, zmierzch), lerp(1.0, 0.9, zmierzch)))
    slonce(st, t, w, alpha=1.0 - zmierzch)
    chmury(st, t, w)
    gory_pasmo(st, t, w, "dal", CX, 560, P.gory_dal, 0.1, haze=0.2, seed=7)
    gory_pasmo(st, t, w, "srodek", CX, 640, P.gory, 0.2, seed=8)
    if aul_x is not None:
        Z0.rise(st, J.aul(1), aul_x, 660, P.miasto, bk(w, 0.4, 0.8), t, 970, w=700, wob=0.0, lift=420, anchor=(0.5, 1.0))
    if wieza_x is not None:
        u = getattr(st, "uklad", None)
        if u is not None:
            with u.obiekt("wieża", "dekoracja"):
                Z0.rise(st, J.rek_kz("wieza"), wieza_x, 712, P.most, bk(w, 0.45, 0.8), t, 971, h=560, wob=0.0, lift=600, anchor=(0.5, 1.0))
        else:
            Z0.rise(st, J.rek_kz("wieza"), wieza_x, 712, P.most, bk(w, 0.45, 0.8), t, 971, h=560, wob=0.0, lift=600, anchor=(0.5, 1.0))
    if potok:
        Z0.rise(st, J.rzeka(False), CX, 772, P.drzewa, bk(w, 0.5), t, 972, w=2000, wob=0.0, lift=160, anchor=(0.5, 1.0), sy=0.6)
    rampa(st, bk(w, 0.7, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False)


def gabinet(st, t, w, okno_x=1010, biurko_x=None, noc=False, stol_mapa=False, kul=False):
    """Gabinet w Petersburgu: zielona tapeta, wysokie okno (za nim śnieg albo dzwony), podłoga, biurko urzędnika
    (biurko_x) albo stół z mapą (stol_mapa). Zwraca y blatu."""
    st.put(J.sciana("zielen"), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    spod(st, (110, 80, 56))
    J.hang(st, J.okno(noc), okno_x, 120, P.miasto + 0.01, bk(w, 0.2), t, 975, h=340, drop=500, sway=0.3, strings=(0.1, 0.9))
    Z0.rise(st, J.podloga((110, 80, 56)), CX, 820, P.droga, bk(w, 0.3), t, 976, w=2200, wob=0.0, lift=220, anchor=(0.5, 1.0))
    st.put(J.glow(), okno_x, 300, P.miasto + 0.012, w=700, anchor=(0.5, 0.5), mode="add", alpha=0.12, shadow=None)
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, dol=False)


def las_bukowy(st, t, w, ciemno=0.0, droga=True, kul=True, x0=0.0):
    """Bukowy las Czeczenii: dalszy rząd buków przymglony, bliższy rząd wysokich pni (korony wychodzą nad kadr, więc pod nimi
    widać lalki i drogę — przegląd 28.11: niskie korony robiły z lasu zieloną ścianę); ciemno 0..1 — las gęstnieje."""
    _niebo_kz(st, w, (lerp(1.0, 0.7, ciemno), lerp(1.0, 0.74, ciemno), lerp(1.0, 0.7, ciemno)))
    slonce(st, t, w, alpha=1.0 - ciemno)
    chmury(st, t, w)
    wzgorza(st, t, w, 18, CX, 590, P.gory_dal, (110, 130, 110), d=0.1, haze=0.4)
    for n in range(8):
        x = (-80 + n * 200 + x0 * 0.5) % 1600 - 160
        Z0.rise(st, J.rek_kz("buk"), x, 620, P.gory + 0.004 * n, bk(w, 0.15 + 0.04 * n), t, 980 + n, h=330, wob=0.2, anchor=(0.5, 1.0),
                haze=0.3, tint=(0.8, 0.86, 0.82))
    if droga:
        Z0.rise(st, J.droga(2, (150, 128, 96)), CX, 726, P.droga + 0.06, bk(w, 0.35), t, 988, w=2200, wob=0.0, lift=140, anchor=(0.5, 1.0))
    for n in range(4):
        x = (120 + n * 420 + x0) % 1700 - 200
        Z0.rise(st, J.rek_kz("buk"), x, 700, P.wzgorza + 0.003 * n, bk(w, 0.3 + 0.05 * n), t, 990 + n, h=980, wob=0.25, anchor=(0.5, 1.0),
                tint=(lerp(0.92, 0.55, ciemno), lerp(0.92, 0.58, ciemno), lerp(0.9, 0.55, ciemno)))
    rampa(st, bk(w, 0.7, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=True)


def kaluga_sc(st, t, w, kul=True):
    """Kaługa: niebo, łagodne zielone wzgórza, dom z kolumienkami; płot (obiekt „płot”) stawia ujęcie, bo gapie stoją za nim."""
    _niebo_kz(st, w, (0.96, 0.98, 1.0))
    slonce(st, t, w)
    chmury(st, t, w)
    gory_pasmo(st, t, w, "dal", CX, 560, P.gory_dal, 0.1, haze=0.3, seed=11, tint=(0.7, 0.86, 0.66))
    Z0.rise(st, J.rek_kz("dom_kaluga"), 760, 650, P.miasto, bk(w, 0.3, 0.9), t, 1000, w=760, wob=0.0, lift=460, anchor=(0.5, 1.0))
    rampa(st, bk(w, 0.7, 0.6))
    if kul:
        kulisy(st, t, w, gazeta=False)


# =====================================================================================================================
# ---------- dekoracje 2 (reżyser 28.11, po 2 minutach szkicu E): „od 40 s cały czas to samo, te góry… powinno ich być
# co najmniej 4 przez 2 minuty… jeśli to mają być góry, to pokazujemy je w jeden sposób, potem w inny”; „wziąłeś biuro
# z Bonnie i Clyde — ma być zupełnie inne”. Każde miejsce ma swoją dekorację, porę dnia i kompozycję; pasma gór
# (gory_pasmo) stoją tylko w planach ogólnych gór, nie w każdym tle.
# =====================================================================================================================

def niebo_pory(st, w, pora):
    st.put(J.niebo_pora(pora), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None)


def wzgorza(st, t, w, v, x, y, p, kolor, d=0.1, wd=2000, haze=0.0, sy=1.0):
    Z0.rise(st, J.wzgorza(v, kolor), x, y, p, bk(w, d, 0.9), t, 1300 + v, w=wd, wob=0.0, lift=300, haze=haze, anchor=(0.5, 1.0), sy=sy)


def klif(st, t, w, v, x, y, p, h=1000, d=0.2, kolor=(132, 116, 96), tint=None):
    Z0.rise(st, J.klif(v, kolor), x, y, p, bk(w, d, 0.9), t, 1310 + v, h=h, wob=0.0, lift=600, anchor=(0.5, 1.0), tint=tint)


def ziemia(st, t, w, kolor=(128, 112, 90), y=800, d=0.3, bruk=False):
    """Ziemia sceny pod lalkami (zamiast desek „Bonnie and Clyde”): ubita ziemia z kamykami albo (bruk) kamienna posadzka."""
    Z0.rise(st, (J.bruk if bruk else J.grunt)(kolor), CX, y, P.droga, bk(w, d), t, 1320, w=2200, anchor=(0.5, 1.0), lift=200, wob=0)


def rzeka_wieczor(st, t, w):
    """Rzeka o zmierzchu (hak: wymiana na rzece widziana z przyszłości): pomarańczowe niebo, nisko słońce, ciemnofioletowe
    łagodne wzgórza zamiast postrzępionych gór, brzegi i woda w ciepłym odblasku."""
    niebo_pory(st, w, "zmierzch")
    slonce(st, t, w, xy=(980, 380))
    wzgorza(st, t, w, 1, CX, 600, P.gory_dal, (96, 80, 120), d=0.1, haze=0.15)
    wzgorza(st, t, w, 2, CX + 200, 650, P.gory, (70, 58, 92), d=0.2)
    Z0.rise(st, J.brzeg(-1), 200, 690, P.most, bk(w, 0.35), t, 880, w=760, wob=0.0, lift=200, anchor=(0.5, 1.0), tint=(0.8, 0.66, 0.6))
    Z0.rise(st, J.brzeg(1), 1080, 690, P.most, bk(w, 0.35), t, 881, w=760, wob=0.0, lift=200, anchor=(0.5, 1.0), tint=(0.8, 0.66, 0.6))
    Z0.rise(st, J.rzeka(False), CX, 740, P.droga, bk(w, 0.45), t, 882, w=2000, wob=0.0, lift=160, anchor=(0.5, 1.0), tint=(1.15, 0.86, 0.7))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def wieza_sc(st, t, w, wieza_x, mrok=0.0):
    """Wieża w Gimry z bliska: niebo późnego popołudnia (mrok — zmierzch), za wieżą stromy stok wąwozu (klif), daleko tylko
    mglista łagodna linia; ziemia z kamieniami. Bez aułu i bez pasm gór (ujęcie „gimry” pokazuje całą wioskę)."""
    niebo_pory(st, w, "zmierzch" if mrok > 0.5 else "lato")
    if mrok <= 0.5:
        slonce(st, t, w, xy=(1080, 150), alpha=1.0 - mrok)
    wzgorza(st, t, w, 3, CX, 620, P.gory_dal, (150, 150, 170), d=0.1, haze=0.4)
    klif(st, t, w, 0, 1180, 780, P.gory, h=900, d=0.2)
    klif(st, t, w, 3, 40, 760, P.wzgorza, h=640, d=0.25, kolor=(112, 98, 82))
    u = getattr(st, "uklad", None)
    if u is not None:
        with u.obiekt("wieża", "dekoracja"):
            Z0.rise(st, J.rek_kz("wieza"), wieza_x, 712, P.most, bk(w, 0.45, 0.8), t, 971, h=560, wob=0.0, lift=600, anchor=(0.5, 1.0))
    else:
        Z0.rise(st, J.rek_kz("wieza"), wieza_x, 712, P.most, bk(w, 0.45, 0.8), t, 971, h=560, wob=0.0, lift=600, anchor=(0.5, 1.0))
    ziemia(st, t, w, (126, 110, 88))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def wawoz_sc(st, t, w):
    """Wąwóz o zmierzchu: dwie strome ściany skalne po bokach, między nimi pas nieba i mglista dal, potok na dnie."""
    niebo_pory(st, w, "zmierzch")
    wzgorza(st, t, w, 4, CX, 640, P.gory_dal, (120, 100, 140), d=0.1, haze=0.35, wd=1200)
    klif(st, t, w, 1, 130, 800, P.gory, h=1060, d=0.15, kolor=(104, 90, 80))
    klif(st, t, w, 2, 1180, 800, P.gory + 0.002, h=1100, d=0.2, kolor=(96, 84, 76))
    Z0.rise(st, J.rzeka(False), CX, 790, P.drzewa, bk(w, 0.4), t, 1330, w=2000, wob=0.0, lift=160, anchor=(0.5, 1.0), sy=0.45, tint=(0.8, 0.7, 0.8))
    ziemia(st, t, w, (96, 86, 76), y=810)
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def dziedziniec_sc(st, t, w):
    """Dziedziniec meczetu w aule: arkada z ostrymi łukami, drewniana galeria, minaret, kamienna posadzka; jasne letnie niebo."""
    niebo_pory(st, w, "lato")
    slonce(st, t, w, xy=(260, 120))
    chmury(st, t, w, k=(1.0, 0.0, 1.0))
    Z0.rise(st, J.arkady(), CX, 700, P.miasto, bk(w, 0.2, 0.9), t, 1340, w=1700, wob=0.0, lift=520, anchor=(0.5, 1.0))
    Z0.rise(st, J.minaret_szczyt(), CX + 1520 - 850, 700 - 760 + 2, P.miasto - 0.001, bk(w, 0.4, 0.8), t, 1341, w=140, wob=0.0, lift=300,
            anchor=(0.5, 1.0))
    ziemia(st, t, w, (170, 156, 132), bruk=True)
    rampa(st, bk(w, 0.7, 0.6))


def gabinet_cara(st, t, w, okno_x=1010, noc=False, portret_x=None, orzel_x=None):
    """Gabinet w Pałacu Zimowym (zamiast tapety i okna „Bonnie and Clyde”): szaroniebieska ściana z płycinami i złotymi
    pilastrami, łukowe okno z karmazynowymi zasłonami i widokiem na Newę, dwugłowy orzeł, portret w złotej ramie, parkiet."""
    st.put(J.sciana_palac(), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    spod(st, (150, 104, 66))
    J.hang(st, J.okno_palac(noc), okno_x, 80, P.miasto + 0.01, bk(w, 0.2), t, 1350, h=520, drop=520, sway=0.25, strings=(0.15, 0.85))
    if orzel_x is not None:
        J.hang(st, J.orzel(), orzel_x, 60, P.miasto + 0.011, bk(w, 0.35), t, 1351, h=170, drop=420, sway=0.3, strings=(0.3, 0.7))
    if portret_x is not None:
        J.hang(st, J.portret(), portret_x, 150, P.miasto + 0.012, bk(w, 0.45), t, 1352, h=230, drop=440, sway=0.3, strings=(0.25, 0.75))
    Z0.rise(st, J.parkiet(), CX, 820, P.droga, bk(w, 0.3), t, 1353, w=2200, wob=0.0, lift=220, anchor=(0.5, 1.0))
    st.put(J.glow(), okno_x, 330, P.miasto + 0.013, w=760, anchor=(0.5, 0.5), mode="add", alpha=0.12 if not noc else 0.05, shadow=None,
           tint=(1.0, 0.96, 0.86))
    rampa(st, bk(w, 0.6, 0.6))


def przelecz_sc(st, t, w):
    """Przełęcz: kamienista droga między dwiema ścianami skał, w przerwie mglista dal; ostre letnie słońce."""
    niebo_pory(st, w, "lato")
    slonce(st, t, w, xy=(640, 110))
    chmury(st, t, w, k=(1.0, 1.0, 0.0))
    wzgorza(st, t, w, 5, CX, 600, P.gory_dal, (150, 160, 176), d=0.1, haze=0.45, wd=1400)
    klif(st, t, w, 3, 140, 720, P.gory, h=820, d=0.15, kolor=(150, 130, 104))
    klif(st, t, w, 4, 1140, 720, P.gory + 0.002, h=760, d=0.2, kolor=(140, 122, 98))
    ziemia(st, t, w, (160, 140, 110))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def bateria_sc(st, t, w):
    """Rosyjska bateria pod Achulgo: szańce z koszami na pierwszym planie, w oddali mała skała z twierdzą w dymie."""
    niebo_pory(st, w, "dym")
    chmury(st, t, w, k=(1.0, 1.0, 1.0))
    wzgorza(st, t, w, 6, CX, 600, P.gory_dal, (150, 130, 110), d=0.1, haze=0.35)
    Z0.rise(st, J.skala(), 900, 610, P.gory, bk(w, 0.2, 0.9), t, 1360, w=300, wob=0.0, lift=480, anchor=(0.5, 1.0), haze=0.25)
    Z0.rise(st, J.twierdza(), 900, 610 - 300 * 620 / 760 + 300 * 100 / 760 + 4, P.gory - 0.001, bk(w, 0.35, 0.8), t, 1361, w=200, wob=0.0,
            lift=260, anchor=(0.5, 1.0), haze=0.25)
    Z0.rise(st, J.szance(), CX, 760, P.wzgorza, bk(w, 0.4, 0.9), t, 1362, w=1800, wob=0.0, lift=260, anchor=(0.5, 1.0))
    ziemia(st, t, w, (120, 100, 78))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def brama_sc(st, t, w):
    """Brama twierdzy Achulgo z bliska: mur z blankami i zamkniętymi wrotami wypełnia scenę; nad nim letnie niebo."""
    niebo_pory(st, w, "lato")
    chmury(st, t, w, k=(1.0, 1.0, 1.0))
    Z0.rise(st, J.brama_twierdzy(), CX, 740, P.miasto, bk(w, 0.25, 0.9), t, 1370, w=1500, wob=0.0, lift=560, anchor=(0.5, 1.0))
    ziemia(st, t, w, (140, 124, 98))
    rampa(st, bk(w, 0.7, 0.6))


SKALA_OBOZ = (1180, 785, 420)  # x, dół, szerokość skały w obozie: płaski szczyt na y ≈ 500 (tam stoi Szamil)


def oboz_sc(st, t, w, namioty=5):
    """Obóz oblężniczy: brązowe letnie wzgórza, z prawej skała Achulgo (na szczycie stoi Szamil), rzędy namiotów."""
    niebo_pory(st, w, "lato")
    slonce(st, t, w, xy=(300, 130))
    wzgorza(st, t, w, 7, CX, 620, P.gory_dal, (170, 146, 104), d=0.1, haze=0.2)
    x, y, wd = SKALA_OBOZ
    Z0.rise(st, J.skala(), x, y, P.gory, bk(w, 0.2, 0.9), t, 1380, w=wd, wob=0.0, lift=480, anchor=(0.5, 1.0))
    for n in range(namioty):
        Z0.rise(st, J.rek_kz("namiot"), 120 + n * 170 - (n % 2) * 40, 690 + (n % 2) * 6, P.droga + 0.004 * n, bk(w, 0.5 + 0.05 * n),
                t, 1381 + n, h=120 - (n % 2) * 14, wob=0.0, anchor=(0.5, 1.0))
    ziemia(st, t, w, (150, 128, 96))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


SKALA_SCIANA = (CX, 850, 1500)  # x, dół, szerokość skały z jaskiniami (ujęcie „upadek”): nad skałą widać mur i niebo


def skala_sc(st, t, w):
    """Skała Achulgo z bliska po upadku: ściana z jaskiniami wypełnia kadr, u góry płonący mur, niebo w dymie."""
    niebo_pory(st, w, "dym")
    x, y, wd = SKALA_SCIANA
    Z0.rise(st, J.skala_sciana(), x, y, P.most, bk(w, 0.2, 0.9), t, 1390, w=wd, wob=0.0, lift=560, anchor=(0.5, 1.0))
    Z0.rise(st, J.mur(1500, 120), CX, skala_szczyt() + 16, P.most - 0.002, bk(w, 0.4, 0.8), t, 1391, w=1300, wob=0.0, lift=200,
            anchor=(0.5, 1.0))
    ziemia(st, t, w, (110, 96, 80))
    rampa(st, bk(w, 0.7, 0.6))


def skala_szczyt():
    """y górnej krawędzi skały z jaskiniami na ekranie (mur twierdzy stoi na niej)."""
    x, y, wd = SKALA_SCIANA
    return y - 760 * wd / 1700 + 100 * wd / 1700


def skala_jaskinia(n):
    """Środek wejścia do n-tej jaskini na ekranie (sceny skala_sc) i szerokość otworu."""
    x, y, wd = SKALA_SCIANA
    s = wd / 1700
    cx, cy = J.SKALA_JASKINIE[n]
    return x - wd / 2 + cx * s, y - 760 * s + cy * s, 140 * s


def ostaniec_sc(st, t, w):
    """Ostaniec w zimie: skalna ściana z boku, za nią szara zimowa dal i łagodne zaśnieżone wzgórza, pada śnieg."""
    niebo_pory(st, w, "zima")
    wzgorza(st, t, w, 8, CX, 620, P.gory_dal, (226, 228, 234), d=0.1, haze=0.3)
    wzgorza(st, t, w, 9, CX - 300, 680, P.gory, (208, 212, 220), d=0.2)
    klif(st, t, w, 5, 160, 790, P.wzgorza, h=980, d=0.25, kolor=(120, 112, 108))
    ziemia(st, t, w, (220, 222, 228))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


# ---------- dekoracje 2, akty III–VI ----------

def sala_tyflis_sc(st, t, w):
    """Pałac namiestnika w Tyflisie (Woroncow): ochrowa sala z ostrołukowymi oknami i dywanem na ścianie, żyrandol."""
    spod(st, (96, 64, 44))
    st.put(J.sala_tyflis(), CX, 740, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None)
    rampa(st, bk(w, 0.7, 0.6))


def sala_tronowa_sc(st, t, w):
    """Sala tronowa: czerwone obicia, tron pod baldachimem, czerwony chodnik."""
    spod(st, (176, 150, 120))
    st.put(J.sala_tronowa(), CX, 740, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None)
    rampa(st, bk(w, 0.7, 0.6))


def namiot_sc(st, t, w):
    """Namiot polowy Woroncowa: płótno, maszty, odchylona poła z widokiem na las; ubita ziemia."""
    st.put(J.namiot_wnetrze(), CX, 740, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None)
    ziemia(st, t, w, (130, 112, 84), y=820)
    rampa(st)


def izba_kz(st, t, w, v=0, okno_x=None, noc=False):
    """Izba w aule, trzy różne pokoje jednego domu (zamiast muru i okna „Bonnie and Clyde”): 0 — izba Szamila z dywanem
    i niszą, 1 — pokój syna z półką rosyjskich książek, 2 — sypialnia nocą ze skrzynią; okienko z okiennicami, dywan na podłodze."""
    ciemnosc(st, (0.22, 0.16, 0.11))
    st.put(J.izba_sciana(v), CX, 730, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None, tint=(0.62, 0.58, 0.6) if noc else None)
    if okno_x is not None:
        st.put(J.okienko(noc), okno_x, 300, P.most, w=200, anchor=(0.5, 0.5))
    ziemia(st, t, w, (120, 92, 64), y=820)
    Z0.rise(st, J.dywan(v), CX, 800, P.droga + 0.01, bk(w, 0.4), t, 1400 + v, w=1500, wob=0.0, lift=120, anchor=(0.5, 1.0), sy=0.5)
    rampa(st, bk(w, 0.6, 0.6))


def przedgorze_sc(st, t, w):
    """Przedgórze Czeczenii (Tołstoj): zielone łagodne wzgórza, wąski Terek, kozacka strażnica na słupach, trawa."""
    niebo_pory(st, w, "lato")
    slonce(st, t, w, xy=(1000, 130))
    chmury(st, t, w)
    wzgorza(st, t, w, 10, CX, 600, P.gory_dal, (130, 150, 120), d=0.1, haze=0.3)
    wzgorza(st, t, w, 11, CX + 300, 660, P.gory, (104, 128, 76), d=0.2)
    Z0.rise(st, J.straznica(), 1040, 650, P.miasto, bk(w, 0.3, 0.9), t, 1410, h=300, wob=0.0, lift=360, anchor=(0.5, 1.0))
    Z0.rise(st, J.rzeka(False), CX, 700, P.most, bk(w, 0.35), t, 1411, w=2000, wob=0.0, lift=160, anchor=(0.5, 1.0), sy=0.3)
    ziemia(st, t, w, (118, 132, 80))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def polka_sc(st, t, w):
    """Półka nad przepaścią (księżne w drodze w góry): z lewej wysoka ściana skały, z prawej głęboka dolina z rzeką daleko
    w dole, chmury poniżej ścieżki."""
    niebo_pory(st, w, "lato")
    slonce(st, t, w, xy=(1050, 110))
    wzgorza(st, t, w, 12, CX + 200, 700, P.gory_dal, (140, 150, 170), d=0.1, haze=0.4)
    Z0.rise(st, J.rzeka(False), CX + 300, 690, P.gory_dal + 0.002, bk(w, 0.2), t, 1420, w=1200, wob=0.0, lift=120, anchor=(0.5, 1.0), sy=0.2,
            haze=0.4)
    chmury(st, t, w, k=(0.0, 1.0, 1.0))
    klif(st, t, w, 7, 120, 760, P.gory, h=1100, d=0.15, kolor=(138, 120, 98))
    ziemia(st, t, w, (140, 124, 100))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def wedeno_sc(st, t, w):
    """Wedeno: stolica Szamila w lesistych górach — ciemnozielone zalesione stoki zamiast skał, buki w oddali."""
    _niebo_kz(st, w)
    if w.noc > 0.5:
        gwiazdy(st, t, bk(w, 0.3), seed=13)
    else:
        slonce(st, t, w)
        chmury(st, t, w)
    wzgorza(st, t, w, 13, CX, 590, P.gory_dal, (78, 100, 80), d=0.1, haze=0.3)
    for n in range(7):
        x = 60 + n * 200
        Z0.rise(st, J.rek_kz("buk"), x, 640, P.gory + 0.003 * n, bk(w, 0.2 + 0.04 * n), t, 1430 + n, h=300, wob=0.15, anchor=(0.5, 1.0),
                haze=0.25, tint=(0.7, 0.8, 0.7))
    wzgorza(st, t, w, 14, CX - 200, 680, P.gory + 0.03, (70, 92, 60), d=0.25)
    ziemia(st, t, w, (110, 100, 80))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def kaluga_sc2(st, t, w):
    """Kaługa: rosyjska równina bez gór — płaskie zielone pola, brzozy, w oddali biała cerkiew ze złotymi kopułami."""
    niebo_pory(st, w, "lato")
    slonce(st, t, w)
    chmury(st, t, w)
    wzgorza(st, t, w, 15, CX, 600, P.gory_dal, (140, 160, 110), d=0.1, haze=0.3, sy=0.5)
    Z0.rise(st, J.cerkiew(), 300, 600, P.gory, bk(w, 0.2, 0.9), t, 1440, h=210, wob=0.0, lift=300, anchor=(0.5, 1.0), haze=0.2)
    for n, x in enumerate((90, 1180, 1260)):
        Z0.rise(st, J.rek_kz("brzoza"), x, 680, P.gory + 0.01 + 0.002 * n, bk(w, 0.3 + 0.05 * n), t, 1441 + n, h=420, wob=0.2, anchor=(0.5, 1.0))
    Z0.rise(st, J.rek_kz("dom_kaluga"), 760, 650, P.miasto, bk(w, 0.3, 0.9), t, 1000, w=760, wob=0.0, lift=460, anchor=(0.5, 1.0))
    ziemia(st, t, w, (110, 130, 80))
    rampa(st, bk(w, 0.7, 0.6))
    kulisy(st, t, w, gazeta=False)


def pracownia_sc(st, t, w, v=0):
    """Pracownia pisarza (zamiast tapety „Bonnie and Clyde”): 0 — Londyn 1960, regały z książkami i okno gilotynowe;
    1 — Herbert 1965, ściana z sęczastej sosny, żaluzje, korkowa tablica."""
    if v == 0:
        st.put(J.regaly(0), CX, 730, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None)
        J.hang(st, J.okno_londyn(), 1000, 130, P.miasto + 0.01, bk(w, 0.2), t, 1450, h=360, drop=500, sway=0.25, strings=(0.1, 0.9))
    else:
        st.put(J.panele_sosna(), CX, 730, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None)
    ziemia(st, t, w, (120, 92, 64), y=820)
    rampa(st, bk(w, 0.6, 0.6))


def biblioteka_sc(st, t, w, noc=False):
    """Biblioteka (akt VI, dowód ze słów): ściana regałów z książkami, ciepłe światło lampy."""
    st.put(J.regaly(0 if noc else 1), CX, 730, P.miasto, w=2100, anchor=(0.5, 1.0), shadow=None, tint=(0.8, 0.76, 0.72) if noc else None)
    st.put(J.glow(), 900, 300, P.miasto + 0.01, w=900, anchor=(0.5, 0.5), mode="add", alpha=0.16, shadow=None, tint=(1.0, 0.86, 0.6))
    ziemia(st, t, w, (110, 84, 60), y=820)
    rampa(st, bk(w, 0.6, 0.6))


def gran_wieczor_sc(st, t, w):
    """Grań o zmierzchu (puenta: biała flaga): ściana skały z boku, pomarańczowe niebo, ciemne łagodne pasma w dole."""
    niebo_pory(st, w, "zmierzch")
    slonce(st, t, w, xy=(300, 400))
    wzgorza(st, t, w, 16, CX, 640, P.gory_dal, (96, 76, 116), d=0.1, haze=0.2)
    wzgorza(st, t, w, 17, CX + 400, 700, P.gory, (64, 52, 82), d=0.2)
    klif(st, t, w, 8, 1260, 780, P.wzgorza, h=900, d=0.25, kolor=(98, 84, 86))
    ziemia(st, t, w, (90, 76, 80))
    rampa(st, bk(w, 0.7, 0.6))
