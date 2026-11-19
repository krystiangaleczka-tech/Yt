"""Świat filmu „Bonnie and Clyde: The Outlaws Made of Paper”: stan sceny, kamera, światło, lalki, auta i scenografie.

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
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/bonnie-i-clyde/ujecia"))

import zestaw_bc as J  # noqa: E402  (dokłada output/pierwszy-cesarz do ścieżki: papier.py, zestaw.py)
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
    """Stan świata na początku ujęcia i (od 0) — księga świata (zasady i rekwizyty)."""
    po = lambda k: i > I[k]
    f = lambda c: 1.0 if c else 0.0
    return Stan(build=None, noc=0.0, sun=1.0, sun_xy=(905, 110), moon=0.0, clouds=[1.0, 1.0, 1.0], zawieszki=[], kulisy=True,
                mgla=0.0, bonnie_kuleje=f(po("wellington_bonnie")), clyde_kuleje=f(po("palce")),
                powaga=f(i >= I["grapevine"] and i <= I["pogrzeby"]))


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


def lalka(st, t, key, x, h=300, k=1.0, y=STOPY, p=None, flip=1.0, lean=0.0, sink=0.0, lift=0.0, rece=(0.0, 0.0), tint=None,
          trzyma=None, seed=None, hop=0.0, alpha=1.0, shadow=True, blur=None, oczy_x=0.0, gwiazdki=0.0, kuleje=0.0, siedzi=False):
    """Lalka na patyczku: wysuwa się zza rampy (k), opada pod nią (sink), obraca się (flip: 1 w prawo, -1 w lewo),
    pochyla (lean, stopnie). hop — podskok przy jeździe na listwie (z położenia x). kuleje — przy jeździe lalka kołysze się
    na jedną stronę (Bonnie po Wellington, Clyde po Eastham). trzyma = (sprite, wysokość, kotwica, obrót, za_ręką).
    oczy_x — śmierć: X na oczach; gwiazdki — zamroczenie (słownik znaków, wytyczne 1.20). Zwraca położenie dłoni."""
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
    for name, ang in (("tyl", rece[1]), ("przod", rece[0])):
        bx, by = f.bark[name]
        dx, dy = _off((bx - af[0]) * sc * flip, (by - af[1]) * sc, rot)
        sx_, sy_ = x + dx, yy + dy
        arot = rot - flip * ang
        z = -0.05 if name == "tyl" else 0.05
        st.put(f.arm, sx_, sy_, p, h=f.ah * sc, anchor=(f.zawias[0] / f.aw, f.zawias[1] / f.ah), rot=arot, sx=flip, z=z, **kw)
        if name == "przod":
            hx, hy = _off(0, f.dlon * sc, arot)
            out = (sx_ + hx, sy_ + hy, arot)
    st.put(f.siedzi if siedzi else f.body, x, yy, p, h=f.ch * sc, anchor=(ax, ay), rot=rot, sx=flip, **kw)
    kk = f.s["szer"]
    na_ark = lambda u, v: _off((f.cw / 2 + (u - 150) * kk - af[0]) * sc * flip, (v - af[1]) * sc, rot)
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
        spr, ph, anc, orot, follow = trzyma
        st.put(spr, out[0], out[1], p, h=ph, anchor=anc, rot=(out[2] if follow else rot) + orot * flip, sx=flip, z=0.08, **kw)
    return out


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
              siedzi=True, **kw)
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
    p = P.auta if p is None else p
    k = h / 360.0
    przechyl = -3.5 * lewarek * flip
    if kierowca:
        lalka(st, t, kierowca, x + (494 - 410) * k * flip, h * 0.92, y=y - 230 * k + (676 - 128) / 614 * h * 0.92 - 20 * lewarek,
              p=p - 0.004, flip=flip, shadow=None)
    st.put(J.ciezarowka(), x, y - 20 * lewarek, p, h=h, anchor=(0.5, 350 / 360.0), rot=przechyl, sx=flip)
    for n, (kx, ky) in enumerate(J.CIEZ_KOLA):
        uniesienie = 26 * lewarek if n == 1 else 0
        st.put(J.kolo(52), x + (kx - 410) * k * flip, y + (ky - 350) * k - uniesienie * k, p + 0.002, h=104 * k, anchor=(0.5, 0.5))
    if lewarek > 0:
        st.put(J.lewarek(), x + (676 - 410) * k * flip, y + 4, p + 0.003, h=140 * k * (0.6 + 0.4 * lewarek), anchor=(0.5, 1.0))


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


def zawieszki(st, t, w):
    for txt, x, y, k in w.zawieszki:
        J.hang(st, J.tag(txt), x, y, P.rekwizyty + 0.02, k, t, 90 + len(txt), drop=460, sway=1.6, h=46, shadow=(4, 6, 6, 0.4))


def blysk(st, x, y, p, t, t0, r=260, kolor=(1.0, 0.9, 0.6), dl=0.12):
    """Błysk (strzał, flesz): jasna plama światła dodana na chwilę."""
    if t0 <= t < t0 + dl:
        st.put(J.glow(), x, y, p, w=r, anchor=(0.5, 0.5), mode="add", alpha=0.9 * (1 - (t - t0) / dl), shadow=None, tint=kolor)


# ---------- wspólne kawałki scenografii ----------

def niebo(st, w, noc=None):
    n = w.noc if noc is None else noc
    st.put(J.niebo_sp(n > 0.5), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None)


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
               tint=(0.55, 0.58, 0.7) if w.noc > 0.5 else None)


def rampa(st, k=1.0):
    if k > 0:
        st.put(J.stage_floor(), CX, RAMPA + (1 - ease_out(k)) * 90, P.rampa, w=2100, anchor=(0.5, 0.0), shadow=(0, -7, 9, 0.45))


def kulisy(st, t, w, dol=True, gora=True, gazeta=True):
    """Przedplan: róg pierwszej strony gazety zwisający z góry kadru i suche trawy przy rampie — nieostre, mijają kamerę
    najszybciej (rama „z papieru”, księga świata: teatr z gazet)."""
    if not w.kulisy:
        return
    if gora and gazeta:
        st.put(J.gazeta("EXTRA!", 3), -130, -150, 0.95, w=300, anchor=(0.0, 0.0), rot=-14 + 1.5 * noise(t, 301, 0.3), blur=4.0,
               shadow=(8, 12, 16, 0.35), tint=(0.86, 0.84, 0.80))
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


def wnetrze(st, t, w, sciana="kwiaty", podloga=(130, 96, 66), okna=(), drzwi=(), meble=(), zarowki=(), kul=True, noc_za_oknem=None,
            kolor_drzwi=(110, 76, 52), tint=None):
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
        J.hang(st, J.zarowka(), x, -10, P.drzewa, bk(w, 0.6), t, 140 + n, h=300, drop=420, sway=1.0, string=False)
        st.put(J.glow(), x, 250, P.drzewa, w=520, anchor=(0.5, 0.5), mode="add", alpha=0.18 * bk(w, 0.7), shadow=None)
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


def drukarnia(st, t, w, obrot=0.0, kul=True):
    """Drukarnia gazety: ceglana ściana, maszyna z kręcącymi się wałkami, stos świeżych gazet."""
    st.put(J.sciana("cegla"), CX, 720, P.miasto, w=2200, anchor=(0.5, 1.0), shadow=None)
    spod(st, (96, 90, 84))
    Z0.rise(st, J.podloga((96, 90, 84)), CX, 820, P.droga, bk(w, 0.2), t, 200, w=2200, wob=0.0, lift=220, anchor=(0.5, 1.0))
    k = bk(w, 0.3)
    Z0.rise(st, J.maszyna(), 600, 700, P.wzgorza, k, t, 201, h=470, wob=0.0)
    if k > 0:
        s_ = 470 / 620.0
        for n, (wx, wy) in enumerate(((330, 315), (520, 315), (330, 435), (520, 435), (700, 435))):
            st.put(J.walek(), 600 + (wx - 450) * s_, 700 - (620 - wy) * s_ + (1 - back(k, 1.3)) * 500, P.wzgorza + 0.003, h=110 * s_ * 1.3,
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
    st.put(J.podloga(kolor), CX, 700, P.miasto - 0.002, w=2200, anchor=(0.5, 0.0), shadow=None, tint=(0.7, 0.7, 0.7))


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


def west_dallas(st, t, w, woz=True, kul=True):
    """West Dallas lat 20. („Devil's Back Porch”): dymiące kominy cementowni, wiadukt, szałasy i namioty w błocie, wóz Barrowów."""
    niebo(st, w)
    slonce(st, t, w, alpha=0.7)
    chmury(st, t, w, haze=1.6)
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
