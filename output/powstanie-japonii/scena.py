"""Świat filmu „Syn słońca”: stan sceny w każdym ujęciu, kamera, światło, lalki i scenografie.

Wzór: output/pierwszy-cesarz/swiat.py. Stan świata liczy się z kamieni milowych rozpiski (`po("tron")` = po ujęciu
o kluczu „tron”), a nie z numerów ujęć. Ujęcie dostaje stan z początku, zmienia go w czasie (swoje wydarzenie)
i woła scenografię: `morze()`, `niebo()`, `kraj()`, `yomi()` albo `mapa_scena()`.

Lalki (`lalka`) to korpus z dwiema rękami na zawiasie w barku (zestaw_jp.Figura): `rece=(przód, tył)` w stopniach,
0 — ręka opuszczona, 90 — wyciągnięta przed siebie, 160 — wzniesiona. W dłoni przedniej ręki może być rekwizyt.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"))

import zestaw_jp as J  # noqa: E402  (dokłada output/pierwszy-cesarz do ścieżki: papier.py, zestaw.py)
from dane import ujecia  # noqa: E402
from papier import CX, CY, H, W, Cam, back, clamp, ease, ease_out, noise, settle  # noqa: E402,F401

Z0 = J.Z0
P = J.P
KOL = [u[2] for u in ujecia()]
I = {k: n for n, k in enumerate(KOL)}

RAMPA = 676  # górna krawędź rampy: lalki stoją za nią
STOPY = 708  # linia stóp lalek na planie lalek (stopy chowają się za rampą)
GR = {"dal": (CX, 690), "srodek": (CX + 60, 766), "blisko": (CX - 40, 761), "przod": (CX + 20, 836)}  # środek i dół pasm
FALE = [(0.30, 384), (0.45, 452), (0.60, 528), (0.75, 606)]  # pasma fal: plan, linia grzbietu


class Stan(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def stan(i):
    """Stan świata na początku ujęcia i (od 0) — księga świata (zasady i rekwizyty)."""
    po = lambda k: i > I[k]
    f = lambda c: 1.0 if c else 0.0
    return Stan(
        build=None, noc=0.0, sun=f(not (po("cien") and not po("rzeka"))), sun_xy=(905, 96),  # przed Amaterasu nie ma słońca
        moon=0.0, clouds=[1.0, 1.0, 1.0],
        ciemnosc=f(po("jaskinia") and not po("lustro")),  # słońce w jaskini
        cesarz=f(po("tron") and not po("smierc")), choragiewki=0.0, zawieszki=[], kulisy=True,
        izanami=f(po("most") and not po("ogien")))


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
    """Dzień albo noc (w.noc 0..1) + migotanie lampy sceny."""
    n = w.noc
    g = (lerp(1.0, 0.66, n), lerp(1.0, 0.76, n), 1.0)
    st.grade = tuple(a * b for a, b in zip(g, extra))
    st.dim = dim * (1 + 0.012 * noise(t, 5, 5.0)) * lerp(1.0, 0.92, n)


# ---------- lalki ----------

def _off(du, dv, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return c * du - s * dv, s * du + c * dv


def lalka(st, t, key, x, h=300, k=1.0, y=STOPY, p=None, flip=1.0, lean=0.0, sink=0.0, lift=0.0, rece=(0.0, 0.0), tint=None,
          trzyma=None, seed=None, hop=0.0, alpha=1.0, shadow=True, blur=None):
    """Lalka na patyczku: wysuwa się zza rampy (k), opada pod nią (sink), obraca się (flip: 1 w prawo, -1 w lewo),
    pochyla (lean, stopnie). hop — podskok przy jeździe na listwie (liczony z położenia x, nie z zegara).
    trzyma = (sprite, wysokość, kotwica, obrót, za_ręką): rekwizyt w przedniej dłoni. Zwraca położenie dłoni."""
    if k <= 0 or sink >= 1:
        return None
    f = J.figura(key)
    seed = sum(map(ord, key)) if seed is None else seed
    p = P.lalki + 0.01 if p is None else p
    sc = h / f.wys  # piksele kadru na piksel arkusza
    yy = y + (1 - back(k, 1.2)) * h * 1.1 + ease(sink) * h * 1.12 - lift - abs(math.sin(x / 26.0)) * hop
    rot = 0.5 * noise(t, seed, 0.45) + lean + settle((k - 0.75) / 0.25 if k < 1 else 0, 1.5, 3)
    flip = math.copysign(max(abs(flip), 0.035), flip)
    af = (f.cw / 2, f.stopa)  # kotwica korpusu: środek stóp
    ax, ay = af[0] / f.cw, af[1] / f.ch
    out = None
    kw = dict(tint=tint, alpha=alpha, shadow=shadow, blur=blur)
    for n, (name, ang) in enumerate((("tyl", rece[1]), ("przod", rece[0]))):
        bx, by = f.bark[name]
        dx, dy = _off((bx - af[0]) * sc * flip, (by - af[1]) * sc, rot)
        sx_, sy_ = x + dx, yy + dy
        arot = rot - flip * ang
        z = -0.05 if name == "tyl" else 0.05
        st.put(f.arm, sx_, sy_, p, h=f.ah * sc, anchor=(f.zawias[0] / f.aw, f.zawias[1] / f.ah), rot=arot, sx=flip, z=z, **kw)
        if name == "przod":
            hx, hy = _off(0, f.dlon * sc, arot)
            out = (sx_ + hx, sy_ + hy, arot)
    st.put(f.body, x, yy, p, h=f.ch * sc, anchor=(ax, ay), rot=rot, sx=flip, **kw)
    if trzyma and out:
        spr, ph, anc, orot, follow = trzyma
        st.put(spr, out[0], out[1], p, h=ph, anchor=anc, rot=(out[2] if follow else rot) + orot * flip, sx=flip, z=0.08, **kw)
    return out


# ---------- scenografie ----------

def zawieszki(st, t, w):
    for txt, x, y, k in w.zawieszki:
        spr = J.tag_zh(txt, 46) if ord(txt[0]) > 0x2E80 else J.tag(txt)
        J.hang(st, spr, x, y, P.rekwizyty + 0.02, k, t, 90 + len(txt), drop=460, sway=1.6, h=46, shadow=(4, 6, 6, 0.4))


def niebo_papier(st, w, tint=(1.0, 1.0, 1.0)):
    n = w.noc
    st.put(J.sky(), CX, CY, P.niebo, w=1760, anchor=(0.5, 0.5), shadow=None,
           tint=(tint[0] * (1 - 0.62 * n), tint[1] * (1 - 0.54 * n), tint[2] * (1 - 0.28 * n)))


def slonce(st, t, w, k=None, xy=None, alpha=1.0):
    k = w.sun if k is None else k
    x, y = xy or w.sun_xy
    if k > 0:
        st.put(J.glow(), x, y + 85 - (1 - back(k, 1.1)) * 520, P.slonce, w=620, anchor=(0.5, 0.5), mode="add", alpha=0.30 * ease(k) * alpha,
               shadow=None, z=-1)
        J.hang(st, J.S("sun", 0.5), x, y, P.slonce, k, t, 1, w=176, shadow=(5, 7, 9, 0.30), haze=0.1)


def ksiezyc(st, t, k, x=648, y=212):
    if k > 0:
        st.put(J.glow(), x, y + 54 - (1 - back(k, 1.1)) * 480, P.slonce, w=560, anchor=(0.5, 0.5), mode="add", alpha=0.26 * ease(k),
               shadow=None, tint=(0.75, 0.85, 1.0), z=-1)
        J.hang(st, J.moon(), x, y, P.slonce, k, t, 2, drop=480, w=108, shadow=(5, 7, 9, 0.3))


def chmury(st, t, w, k=(1.0, 1.0, 1.0), haze=1.0):
    for i, (name, x, y, wd) in enumerate((("cloud_left", 250, 64, 560), ("cloud_center", 700, 28, 620), ("cloud_right", 1080, 150, 500))):
        J.hang(st, J.S(name, 0.5), x + 6 * noise(t, 30 + i, 0.08), y, P.chmury + i * 0.008, k[i], t, 4 + i, w=wd, sway=0.5,
               strings=(0.3, 0.7), shadow=(7, 10, 11, 0.26), haze=0.08 * haze)


def rampa(st, k=1.0):
    if k > 0:
        st.put(J.stage_floor(), CX, RAMPA + (1 - ease_out(k)) * 90, P.rampa, w=2100, anchor=(0.5, 0.0), shadow=(0, -7, 9, 0.45))


def kulisy(st, t, w, dol=True, gora=True, chmura=False):
    """Przedplan: gałąź kwitnącej wiśni albo chmura z góry kadru, trzciny przy rampie — nieostre, mijają kamerę najszybciej."""
    if not w.kulisy:
        return
    if gora and not chmura:
        st.put(J.galaz_wisni(), -60, -50, 0.95, w=560, anchor=(0.0, 0.0), rot=1.5 * noise(t, 301, 0.3), blur=4.0,
               shadow=(8, 12, 16, 0.35), tint=(0.84, 0.80, 0.82))
    if chmura:
        st.put(J.S("cloud_left", 0.5), -120, 20, 0.95, w=760, anchor=(0.0, 0.5), rot=1.0 * noise(t, 305, 0.3), blur=4.5, shadow=None,
               tint=(0.86, 0.84, 0.80))
    if dol:
        st.put(Z0.reeds(1), 1270, 770, 0.94, h=230, rot=1.2 * noise(t, 302, 0.4), blur=3.5, shadow=None, tint=(0.62, 0.66, 0.6))
        st.put(Z0.reeds(2), 40, 776, 0.93, h=190, rot=1.0 * noise(t, 303, 0.4), blur=3.0, shadow=None, tint=(0.62, 0.66, 0.6))


def fala(i, t, burza=0.0):
    return FALE[i][1] + (5 + 16 * burza) * math.sin(t * (1.3 + 1.6 * burza) + i * 1.1)


def morze(st, t, w, fale=1.0, wyspy=(), tint=(1.0, 1.0, 1.0), burza=0.0, chmury_k=(1.0, 1.0, 1.0), slonce_k=None, kul=True):
    """Morze: papier nieba, chmury, cztery pasma fal (kołysane w przeciwne strony), wyspy między pasmami.
    wyspy = [(x, pasmo za wyspą 1..3, szerokość, odmiana, k)] — wyspa wysuwa się zza pasma fal przed nią."""
    niebo_papier(st, w, tint)
    if slonce_k is None:
        slonce(st, t, w)
    elif slonce_k > 0:
        slonce(st, t, w, slonce_k)
    ksiezyc(st, t, w.moon)
    chmury(st, t, w, k=tuple(min(a, bk(w, 0.1 + 0.2 * n, 0.9)) for n, a in enumerate(chmury_k)))
    for x, b, wd, v, k in wyspy:
        k = min(k, bk(w, 0.4 + 0.15 * v, 0.8))
        if k > 0:
            Z0.rise(st, J.wyspa(v), x, FALE[b][1] + 26, FALE[b][0] - 0.012, k, t, 70 + v, w=wd, wob=0.0, lift=wd * 0.5,
                    haze=0.35 * (3 - b) / 3, shadow=(5, 6, 8, 0.28))
    for i in range(4):
        kk = clamp(fale * 2.2 - i * 0.4) * bk(w, 0.0 + 0.12 * i, 0.7)
        if kk > 0:
            amp = 46 + 70 * burza
            st.put(J.waves(i), CX + (amp - i * 6) * math.sin(t * (0.9 + 1.2 * burza) + i * 1.9) * (1 if i % 2 else -1),
                   fala(i, t, burza) + (1 - back(kk, 1.2)) * 340, FALE[i][0], w=2400, anchor=(0.5, 0.0),
                   haze=0.3 - i * 0.09 if i < 3 else 0.0, rot=burza * 1.5 * math.sin(t * 2.1 + i))
    rampa(st, bk(w, 0.6, 0.6))
    if kul:
        kulisy(st, t, w, dol=False, chmura=True)


def lodz(st, t, x, pasmo_i, h=150, flip=1.0, v=0, burza=0.0, seed=0, przechyl=0.0, sink=0.0, ladunek=()):
    """Łódź na paśmie fal pasmo_i (płynie razem z nim); ladunek = [(klucz lalki, dx, wysokość, rece)] — lalki na pokładzie."""
    p = FALE[pasmo_i][0] + 0.006
    y = fala(pasmo_i, t, burza) + 40 + (3 + 10 * burza) * math.sin(t * 2.0 + seed) + ease(sink) * h * 1.3
    rot = (2 + 7 * burza) * math.sin(t * (1.1 + burza) + seed * 2.3) + przechyl
    for key, dx, lh, rc in ladunek:
        hx, hy = _off(dx * flip, -h * 0.30, rot)
        lalka(st, t, key, x + hx, lh, 1.0, y=y + hy + lh * 0.2, p=p - 0.003, flip=flip, lean=rot, rece=rc)
    st.put(J.lodz(v), x, y, p, h=h, anchor=(0.5, 0.74), rot=rot, sx=flip, haze=0.25 * (3 - pasmo_i) / 3)


# ---- niebiańska równina ----

SKALA = (1010, 690, 560)  # skała z jaskinią: x, dół, szerokość
SAKAKI = (760, 700, 330)


def niebo(st, t, w, skala=1.0, drzwi=0.0, sakaki=0.0, tkalnia=1.0, dach=1.0, pola=(1.0,) * 5, tint=(1.04, 0.98, 0.86), lina=0.0):
    """Niebiańska równina: złocisty papier nieba, ziemią są chmury wysuwane od dołu; poletka ryżu bogów, tkalnia, skała
    z jaskinią i głazem (drzwi: 0 — otwarte, 1 — zasunięte)."""
    niebo_papier(st, w, tint)
    slonce(st, t, w)
    chmury(st, t, w, k=(bk(w, 0.1, 0.9), bk(w, 0.3, 0.9), bk(w, 0.5, 0.9)))
    Z0.rise(st, J.pasmo("chmury"), CX, 640, P.gory, bk(w, 0.2), t, 501, w=2000, wob=0.0, lift=300, haze=0.15)
    for n, kk in enumerate(pola):
        k = min(kk, bk(w, 0.5 + 0.08 * n, 0.5))
        if k > 0:
            x = 120 + n * 120
            st.put(J.poletko(0), x, 600 + (1 - back(k, 1.4)) * 60 - n * 4, P.gory + 0.03, w=150, shadow=(2, 3, 3, 0.3), haze=0.1)
    Z0.rise(st, J.pasmo("chmury"), CX + 80, 742, P.most, bk(w, 0.4), t, 502, w=2000, wob=0.0, lift=300, haze=0.05)
    tk = min(tkalnia, bk(w, 0.7))
    if tk > 0:
        Z0.rise(st, J.tkalnia(), 300, 610, P.most + 0.01, tk, t, 503, w=260, wob=0.0)
        if dach > 0:
            st.put(J.dach(420), 300, 520 + (1 - back(tk, 1.2)) * 220, P.most + 0.012, w=270 * dach ** 0.0, anchor=(0.5, 1.0))
    sk = min(skala, bk(w, 0.6))
    if sk > 0:
        x, yb, wd = SKALA
        Z0.rise(st, J.skala(), x, yb, P.wzgorza, sk, t, 504, w=wd, wob=0.0, lift=500)
        if drzwi > 0:  # głaz zasuwa otwór jaskini (otwór: środek w x - 0,07 szerokości)
            gx = x - 0.07 * wd + (1 - ease(drzwi)) * 300
            st.put(J.glaz(1), gx, yb - 10 + (1 - back(sk, 1.2)) * 500, P.wzgorza + 0.004, w=wd * 0.5)
        if lina > 0:  # po świcie przed jaskinią wisi sznur shimenawa (ciągłość z ujęciem „swit”)
            J.hang(st, J.shimenawa(), x - 0.07 * wd + 10, 470, P.wzgorza + 0.006, min(lina, sk), t, 540, drop=420, sway=0.6, w=330,
                   strings=(0.05, 0.95))
    if sakaki > 0:
        x, yb, hh = SAKAKI
        Z0.rise(st, J.sakaki(), x, yb, P.wzgorza + 0.02, sakaki, t, 505, h=hh, wob=0.4)
    Z0.rise(st, J.pasmo("chmury"), CX - 30, 840, P.wzgorza + 0.05, bk(w, 0.9), t, 506, w=2000, wob=0.0, lift=300)
    rampa(st, bk(w, 1.0, 0.6))


# ---- kraj ----

def pasmo(st, t, name, k, p, seed, haze=0.0, dx=0.0, kolor=None):
    cx, yb = GR.get(name, (CX, 760))
    Z0.rise(st, J.pasmo(kolor or name), cx + dx, yb, p, k, t, seed, w=2000, wob=0.0, lift=320, haze=haze)


def ziemia(name, x, kolor=None):
    """Linia grzbietu pasma (y kadru wzorcowego) w punkcie x."""
    cx, yb = GR[name]
    return J.pasmo_top(kolor or name, x, cx, yb)


def kraj(st, t, w, wariant="", gory=1.0, rzeka=0.0, pola=0.0, cedry=0.0, wzgorza=0.0, unebi=0.0, niebieskie=0.0, chaty=0.0,
         sosny=(1.0, 1.0), slonce_k=None, tint=(1.0, 1.0, 1.0), gora_x=520, morze_k=0.0, kul=True):
    """Kraj na scenie: papier nieba, słońce, chmury, góry, pasma wzgórz, sosny i rampa — oraz odmiany miejsc:
    rzeka (Izumo), pola ryżu, cedry (Kumano), trzy wzgórza i Unebi (Yamato), niebieskie góry, chaty z trzciny, morze."""
    niebo_papier(st, w, tint)
    if slonce_k is None:
        slonce(st, t, w, min(w.sun, bk(w, 0.0, 0.9)))
    elif slonce_k > 0:
        slonce(st, t, w, slonce_k)
    ksiezyc(st, t, w.moon)
    chmury(st, t, w, k=(bk(w, 0.15, 0.9), bk(w, 0.4, 0.9), bk(w, 0.65, 0.9)))
    hz = 1.0
    if niebieskie > 0:  # krąg błękitnych gór Yamato
        for n, (x, wd, v) in enumerate(((200, 760, 0), (700, 900, 1), (1160, 700, 0))):
            Z0.rise(st, J.gora_niebieska(v), x, 470, P.gory_dal + 0.005 * n, min(niebieskie, bk(w, 0.1 + 0.1 * n)), t, 600 + n, w=wd,
                    wob=0.0, haze=0.25)
    else:
        # Fuji nad okrągłymi, zalesionymi pagórkami (reżyser 13.11: nie chińskie góry z „Pierwszego cesarza”)
        Z0.rise(st, J.fuji(0), 760, 478, P.gory_dal, min(gory, bk(w, 0.1)), t, 11, w=820, wob=0.0, haze=0.40 * hz,
                shadow=(6, 6, 10, 0.2))
        Z0.rise(st, J.wzgorza_jp(0), 300, 490, P.gory_dal + 0.02, min(gory, bk(w, 0.2)), t, 12, w=1000, wob=0.0, haze=0.30,
                shadow=(6, 6, 10, 0.2))
        Z0.rise(st, J.wzgorza_jp(1), 1150, 496, P.gory_dal + 0.022, min(gory, bk(w, 0.25)), t, 13, w=900, wob=0.0, haze=0.30,
                shadow=(6, 6, 10, 0.2))
    if morze_k > 0:  # zatoka: pasma fal z lewej, przed górami
        for i in range(2):
            st.put(J.waves(i), 200 + 30 * math.sin(t * 0.9 + i) * (1 if i else -1), 560 + i * 40 + (1 - back(min(morze_k, bk(w, 0.3)), 1.2)) * 300,
                   P.rownina + 0.01 * i, w=1500, anchor=(0.5, 0.0), haze=0.2)
    Z0.rise(st, J.wzgorza_jp(2), gora_x, 572, P.gory, min(gory, bk(w, 0.35)), t, 14, w=1150, wob=0.0, haze=0.16)
    pasmo(st, t, "dal", bk(w, 0.4), P.gory + 0.02, 610, haze=0.16)
    if wzgorza > 0:  # trzy wzgórza Yamato
        for n, (x, wd) in enumerate(((330, 380), (760, 330), (1060, 300))):
            Z0.rise(st, J.wzgorek(n), x, 606, P.miasto - 0.01 + 0.004 * n, min(wzgorza, bk(w, 0.5 + 0.1 * n)), t, 620 + n, w=wd, wob=0.0,
                    haze=0.08)
    if unebi > 0:
        Z0.rise(st, J.wzgorek(5, (92, 136, 84)), 560, 640, P.miasto + 0.01, min(unebi, bk(w, 0.5)), t, 626, w=520, wob=0.0, haze=0.05)
    pasmo(st, t, "srodek", bk(w, 0.6), P.miasto + 0.03, 611, haze=0.06)
    if rzeka > 0:  # rzeka Izumo: wstęga wije się od gór ku rampie
        k = min(rzeka, bk(w, 0.8))
        y0 = ziemia("blisko", 300) + 18
        st.put(Z0.ribbon("kanal"), 120, y0, P.droga + 0.004, w=1080, anchor=(0.0, 0.5), sx=max(0.02, ease_out(k)), rot=-1.0,
               shadow=(2, 3, 4, 0.35))
    pasmo(st, t, "blisko", bk(w, 0.75), P.droga + 0.02, 612)
    if pola > 0:  # pola ryżu na pasmie bliskim
        for n in range(7):
            k = min(1.0, pola * 1.6 - n * 0.08) * bk(w, 0.9 + 0.06 * n, 0.5)
            if k > 0:
                x = 120 + n * 170
                v = 0 if not isinstance(w.get("pola_v"), int) else w.pola_v
                st.put(J.poletko(v), x, ziemia("blisko", x) + 44 + (1 - back(k, 1.5)) * 40, P.droga + 0.025, w=160, shadow=(2, 3, 3, 0.3))
    if chaty > 0:
        for n, x in enumerate((260, 520, 880, 1100)):
            k = min(chaty, bk(w, 0.9 + 0.1 * n))
            Z0.rise(st, J.chata_jomon(n), x, ziemia("blisko", x) + 30, P.droga + 0.03 + 0.002 * n, clamp(k * 1.4 - n * 0.15), t, 630 + n,
                    h=110 - n * 6, wob=0.0)
    if sosny[1] > 0:  # kępa bambusa z prawej (sosny = (lewa kulisa, prawa kępa) — nazwa została z pierwszej wersji)
        Z0.rise(st, J.bambus(0), 1200, 662, P.most + 0.015, min(sosny[1], bk(w, 1.1)), t, 21, h=360, wob=0.35, haze=0.03)
    if cedry > 0:  # las cedrów Kumano: trzy rzędy
        r = random.Random(77)
        for row, (p, yb, hh, n) in enumerate(((P.most + 0.02, 650, 360, 9), (P.droga + 0.04, 690, 470, 7), (P.wzgorza + 0.03, 730, 560, 5))):
            for j in range(n):
                x = -40 + (j + r.uniform(0.1, 0.9)) * 1360 / n
                k = min(cedry, bk(w, 0.5 + 0.2 * row + 0.05 * j, 0.6))
                Z0.rise(st, J.cedr(j % 4), x, yb + r.uniform(-10, 10), p + 0.001 * j, k, t, 700 + row * 20 + j, h=hh * r.uniform(0.85, 1.1),
                        wob=0.3, haze=0.12 * (2 - row) / 2)
    pasmo(st, t, "przod", bk(w, 1.0), P.wzgorza + 0.05, 613)
    if sosny[0] > 0:  # kwitnąca wiśnia na lewej kulisie
        spr = J.wisnia(1)
        Z0.rise(st, spr, 30, 704, P.drzewa + 0.02, min(sosny[0], bk(w, 1.25)), t, 22, h=330, wob=0.35, anchor=spr.pien)
    rampa(st, bk(w, 1.2, 0.6))
    if kul:
        kulisy(st, t, w)


def yomi(st, t, w, glaz_k=0.0, swiatlo_x=640):
    """Kraina zmarłych: ciemność, skały z dwóch stron, głaz zamykający przejście z prawej; światło z pochodni."""
    st.put(J.black(), CX, CY, P.niebo, w=2000, anchor=(0.5, 0.5), shadow=None, blur=0, tint=(0.10, 0.08, 0.10))
    for n, (x, y, wd, v) in enumerate(((140, 620, 520, 0), (1160, 640, 560, 2), (420, 700, 380, 3), (900, 720, 420, 4))):
        Z0.rise(st, J.glaz(v), x, y, 0.5 + 0.06 * n, bk(w, 0.1 * n, 0.7), t, 800 + n, w=wd, wob=0.0, tint=(0.42, 0.40, 0.46))
    if glaz_k > 0:
        st.put(J.glaz(5), 1500 - 560 * ease(glaz_k), 700 + 6 * math.sin(glaz_k * 30) * (1 - glaz_k), P.lalki + 0.03, w=520,
               rot=-200 * ease(glaz_k), tint=(0.6, 0.56, 0.6))
    rampa(st, 1.0)
    st.spot = (swiatlo_x, 520, P.lalki, 430, 0.82)


def pochodnia(st, t, x, y, p, k=1.0, seed=0, h=150):
    """Pochodnia z płomieniem z bibuły (płomień skacze poklatkowo)."""
    if k <= 0:
        return
    yy = y + (1 - back(k, 1.3)) * h
    st.put(J.pochodnia(), x, yy, p, h=h)
    ft = math.floor(t * 12) / 12
    for n in range(4):
        hh = h * 0.42 * (0.75 + 0.35 * noise(ft, 600 + n + seed * 7, 9))
        st.put(J.flame(n), x + (n - 1.5) * 4, yy - h * 0.86, p + 0.0005 * n, h=hh, rot=8 * noise(ft, 700 + n + seed, 7), shadow=None,
               tint=(1.15, 1.1, 1.0))
    st.put(J.glow(), x, yy - h, p + 0.003, w=360, anchor=(0.5, 0.5), mode="add", alpha=0.32 * (0.85 + 0.15 * noise(ft, 9 + seed, 9)),
           shadow=None, tint=(1.0, 0.6, 0.3))


def mapa_scena(st, t, w, k=1.0, x=640, y=60, wd=780, wyspy=1.0):
    """Mapa wysp na dwóch nitkach przed papierem nieba. Zwraca funkcję: punkt arkusza mapy → kadr wzorcowy."""
    niebo_papier(st, w, (0.98, 0.95, 0.88))
    chmury(st, t, w, k=(1.0, 0.0, 1.0))
    sc = wd / J.MAPA_WH[0]
    yy = y - (1 - back(k, 1.1)) * 700
    for sx in (x - wd * 0.36, x + wd * 0.36):
        st.line([(sx, -260), (sx, yy + 4)], 0.82, width=1.1, color=(70, 56, 44), alpha=0.7, z=-0.5)
    st.put(J.mapa_plansza(), x, yy, 0.82, w=wd, anchor=(0.5, 0.0), shadow=(6, 9, 9, 0.45), blur=0)
    for n, kk in enumerate(J.WYSPY):
        f = clamp(wyspy * 1.6 - n * 0.2)
        if f > 0:
            st.put(J.mapa_wyspa(kk), x, yy - (1 - back(f, 1.3)) * 30, 0.821 + 0.0003 * n, w=wd, anchor=(0.5, 0.0), alpha=min(1.0, f * 3),
                   shadow=(2, 3, 3, 0.35), blur=0)
    rampa(st, 1.0)
    return lambda mx, my: (x - wd / 2 + mx * sc, yy + my * sc)


# ---------- pomocnicze: punkty na lalkach, wyspy, zjazd na nitkach ----------

def punkt(key, x, h, u, v, y=STOPY, flip=1.0, rot=0.0, lift=0.0):
    """Punkt (u, v) arkusza korpusu lalki (np. czubek głowy 152, 70) w kadrze wzorcowym, gdy lalka stoi w x, y."""
    f = J.figura(key)
    sc = h / f.wys
    u = u * f.s["szer"]
    dx, dy = _off((u - f.cw / 2) * sc * flip, (v - f.stopa) * sc, rot)
    return x + dx, y - lift + dy


def czubek_luku(dlon, bow_h, rot, flip):
    """Górny koniec łuku trzymanego w dłoni (dlon = wynik lalka(): x, y, obrót ręki)."""
    (gx, gy), (tx, ty) = J.LUK_UCHWYT, J.LUK_CZUBEK
    spr = J.luk()
    bw = bow_h * spr.w / spr.h
    dx, dy = _off((tx - gx) * bw * flip, (ty - gy) * bow_h, rot)
    return dlon[0] + dx, dlon[1] + dy


def gora_wyspy(spr, x, cx, yb, wd):
    """Wierzch wycinka postawionego kotwicą (0,5; 1,0) w (cx, yb) o szerokości wd — w punkcie x."""
    hh = wd * spr.h / spr.w
    return yb - hh + spr.top((x - (cx - wd / 2)) / wd) * hh


def zjazd(st, t, key, x, y, h, k, p=None, flip=1.0, rece=(0.0, 0.0), trzyma=None, lean=0.0, nitki=1.0, seed=None):
    """Lalka zjeżdża na dwóch nitkach z góry (z nieba) i staje w y; po wylądowaniu nitki bledną."""
    if k <= 0:
        return None
    yy = y - (1 - back(k, 1.1)) * 640
    rot = lean + (1 - k) * 5 * math.sin(k * 8)
    out = lalka(st, t, key, x, h, 1.0, y=yy, p=p, flip=flip, rece=rece, trzyma=trzyma, lean=rot, seed=seed)
    a = 0.7 * nitki * (1.0 if k < 1 else 0.5)
    if a > 0.02:
        for u in (128, 176):
            hx, hy = punkt(key, x, h, u, 76, y=yy, flip=flip, rot=rot)
            st.line([(hx, -240), (hx, hy)], (P.lalki + 0.01) if p is None else p, width=1.1, color=(70, 56, 44), alpha=a, z=-0.5)
    return out


FLAGI = [(170, "blisko"), (330, "srodek"), (470, "blisko"), (610, "srodek"), (760, "blisko"), (900, "srodek"), (1040, "blisko"),
         (1180, "srodek"), (1250, "blisko")]


def choragiewki(st, t, ks):
    """Białe chorągiewki z czerwonym słońcem wyskakują zza grzbietów wzgórz."""
    for n, (x, band) in enumerate(FLAGI):
        k = ks[n] if n < len(ks) else 0.0
        if k <= 0:
            continue
        y = ziemia(band, x) + 18
        p = (P.droga + 0.012) if band == "blisko" else (P.miasto + 0.022)
        Z0.rise(st, J.choragiewka(0), x, y, p, k, t, 900 + n, h=92 if band == "blisko" else 70, wob=1.4)


def grzebien_we_wlosach(st, key, x, h, flip=1.0, rot=0.0, y=STOPY, p=None, k=1.0):
    if k <= 0:
        return
    gx, gy = punkt(key, x, h, 130, 66, y=y, flip=flip, rot=rot)
    st.put(J.grzebien(), gx, gy, (P.lalki + 0.012) if p is None else p, w=h * 0.16, anchor=(0.5, 0.7), rot=rot - 20 * flip, sx=flip)


def strzala_w_ramieniu(st, key, x, h, flip=1.0, rot=0.0, y=STOPY, p=None):
    ax, ay = punkt(key, x, h, 196, 236, y=y, flip=flip, rot=rot)
    st.put(Z0.prop("strzala"), ax, ay, (P.lalki + 0.013) if p is None else p, w=h * 0.42, anchor=(0.95, 0.5), rot=rot + 160,
           shadow=(2, 3, 3, 0.4))  # strzała przyszła ze wschodu (z prawej): grot w barku, drzewce w prawo i w górę


def poklad_lodzi(t, x, pasmo_i, h, dx, lh, flip=1.0, burza=0.0, seed=0, przechyl=0.0, sink=0.0):
    """Miejsce lalki na pokładzie łodzi (te same liczby co w lodz()): x, y stóp, obrót, plan."""
    p = FALE[pasmo_i][0] + 0.006
    y = fala(pasmo_i, t, burza) + 40 + (3 + 10 * burza) * math.sin(t * 2.0 + seed) + ease(sink) * h * 1.3
    rot = (2 + 7 * burza) * math.sin(t * (1.1 + burza) + seed * 2.3) + przechyl
    hx, hy = _off(dx * flip, -h * 0.30, rot)
    return x + hx, y + hy + lh * 0.2, rot, p - 0.003
