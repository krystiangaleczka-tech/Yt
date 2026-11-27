"""Układ sceny teatru papierowego: głębia, przyczepianie, ręka z łokciem i kontrola — bez Blendera.

Dotąd wykonawca (człowiek albo AI) wpisywał przy każdym wycinku x, y, plan p i z i sam „wyobrażał sobie”, co stoi przed
czym, co kto trzyma i czy dłoń sięga rzeczy. Ten moduł przenosi te decyzje do silnika (nakładka na papier.Stage
i scena.lalka; niczego w nich nie zmienia):

1. **Rzędy sceny** — lalka, mebel i rzecz stoją w nazwanym rzędzie (`korytarz` za ścianą, `lalki`, `przod` — bliżej widza
   niż aktorzy). Plan głębi i kolejność rysowania wynikają z rzędu. Przejście z rzędu do rzędu (wejście przez drzwi) to
   krotka (rząd_a, rząd_b, postęp 0..1).
2. **Przyczepianie** — rzecz jest *na* blacie mebla, *w* naczyniu, *w dłoni* (za punkt chwytu) albo *na głowie*. Położenie
   liczy się w każdej klatce z tego, do czego rzecz jest przyczepiona (garnek jedzie razem z wyrastającą kuchenką).
   Przepięcie (z głowy do dłoni) dzieje się w jednej klatce, w chwili, gdy dłoń dotyka punktu chwytu (wytyczne 1.28).
3. **Ręka z łokciem** — ramię i przedramię na spince, jak w prawdziwej lalce papierowej; dłoń idzie do punktu, a kąty barku
   i łokcia liczy odwrotna kinematyka dwóch odcinków. Sztywna ręka z jednym zawiasem nie dosięga własnej głowy
   (bark–kapelusz ≈ 0,75 długości ręki), dlatego „uchylanie kapelusza” było machaniem pustą dłonią nad głową.
4. **Kontrola** — każdy wycinek ma właściciela. Po ułożeniu klatki bufor identyfikatorów mówi, ile każdego obiektu widać,
   czy dłoń dotyka chwytu, czy rzecz stoi na blacie, czy nic nie wychodzi poza otwór drzwi ani spod brzegu naczynia,
   czy dłoń sięga celu. Do tego **rzut sceny z góry**: rzędy, obiekty, przyczepienia i kamera — do obejrzenia obok klatki.

Użycie w ujęciu: `u = Uklad(st, t)`, potem `u.mebel(...)`, `u.na(...)`, `u.lalka(...)`, `u.rzecz(...)` zamiast st.put;
kontrole dopisuje ujęcie (`u.widac`, `u.punkt`, `u.kontakt`, `u.na_powierzchni`, `u.w_otworze`, `u.w_naczyniu`).
Sprawdza je `kontrola(st)` po ułożeniu klatki; `rzut(st, ...)` rysuje plan z góry.
"""
import math
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import papier
import scena as SW
import zestaw as Z0
import zestaw_bc as J
from papier import Sprite, back, clamp, ease, noise, settle

P = J.P
_off = SW._off
FONT = str(Path(__file__).resolve().parents[2] / "pilot/fonts/Montserrat.ttf")

# ---------- rzędy sceny ----------

RZEDY_WNETRZA = {
    "korytarz": P.miasto - 0.012,  # za ścianą: widać tylko przez otwór drzwi (ściana ma wycięty otwór)
    "sciana": P.miasto,
    "drzwi": P.miasto + 0.015,
    "podloga": P.droga,
    "przy_scianie": P.wzgorza,
    "lalki": P.lalki + 0.01,  # aktorzy (jak domyślny plan scena.lalka)
    "przod": P.lalki + 0.03,  # meble i sprzęty bliżej widza niż aktorzy: kto stoi w rzędzie „lalki”, stoi ZA nimi
    "rekwizyty": P.rekwizyty,
    "rampa": P.rampa,
}
NAZWY_RZEDOW = {"korytarz": "korytarz (za ścianą)", "sciana": "ściana", "drzwi": "drzwi", "podloga": "podłoga",
                "przy_scianie": "przy ścianie", "lalki": "aktorzy", "przod": "przód (przed aktorami)",
                "rekwizyty": "nitki i znaki", "rampa": "rampa"}

# powierzchnie mebli w układzie arkusza zestaw_bc.MEBLE: nazwa → (u od, u do, v)
POWIERZCHNIE = {"stol": {"blat": (0, 360, 0)}, "stol_obrus": {"blat": (0, 360, 0)}, "biurko": {"blat": (0, 460, 0)},
                "lada": {"blat": (0, 700, 0)}, "kuchenka": {"plyta": (0, 175, 40)}, "szafka": {"blat": (0, 220, 0)}}

LOKIEC_V = 120  # staw łokciowy na arkuszu ramienia (bark v = 26, dłoń v = 232): ramię 94, przedramię 112
R_DLONI = 19  # promień dłoni na arkuszu ramienia (elipsa 15 × 19 wokół (56, 230))


# ---------- arkusze: punkt arkusza → punkt w kadrze ----------

class Geo:
    """Położenie wycinka: punkt (u, v) jego arkusza → punkt w kadrze wzorcowym. k — piksele kadru na piksel arkusza,
    kotw — punkt arkusza, który leży w (x, y); obrót i odbicie jak w Stage.put."""

    def __init__(self, x, y, k, kotw, rot=0.0, sx=1.0, p=0.8):
        self.x, self.y, self.k, self.kotw, self.rot, self.sx, self.p = x, y, k, kotw, rot, sx, p

    def __call__(self, u, v):
        dx, dy = _off((u - self.kotw[0]) * self.k * self.sx, (v - self.kotw[1]) * self.k, self.rot)
        return self.x + dx, self.y + dy


class Ark:
    """Wycinek razem z położeniem przycięcia (Sprite obcina przezroczyste marginesy), żeby punkty chwytu, dna i brzegu
    liczyć w układzie arkusza, na którym rzecz narysowano. Wszystko w pikselach arkusza."""

    def __init__(self, spr, img, pad=2, crop=True):
        f = 1
        im = img.convert("RGBA")
        if papier.Q <= 0.5 and min(img.size) > 96:  # szkic: Sprite zmniejsza arkusz o połowę
            im, f = im.reduce(2), 2
        al = np.asarray(im)[..., 3] / 255.0
        ys, xs = np.where(al > 0.03)
        self.spr = spr
        self.x0 = max(0, xs.min() - pad) * f if crop else 0
        self.y0 = max(0, ys.min() - pad) * f if crop else 0
        self.ws, self.hs = spr.w * f, spr.h * f
        self.dol = (ys.max() + 1) * f  # dolna krawędź papieru (na tym rzecz stoi)
        self.srodek = (xs.min() + xs.max() + 1) / 2 * f

    def ulamek(self, u, v):
        return (u - self.x0) / self.ws, (v - self.y0) / self.hs


@lru_cache(None)
def ark_rek(key):
    w, h, fn = J.REKWIZYTY[key]
    return Ark(J.rek(key), Z0.stack(w, h, fn(), seed=300 + len(key)))


@lru_cache(None)
def ark_mebel(key):
    w, h, parts = J.MEBLE[key]
    img = Z0.stack(w + 20, h + 20, [(lambda d, s, f=p[0]: f(d, s), p[1]) + ((p[2],) if len(p) > 2 else ()) for p in parts],
                   seed=160 + len(key))
    return Ark(J.mebel(key), img)


# ---------- lalka: korpus bez kapelusza, kapelusz osobno, ramię w dwóch kawałkach ----------

def _korpus_z_ziarnem(spec, seed):
    """_korpus_img z narzuconym ziarnem papieru: korpus bez kapelusza ma te same piksele co lalka z kapeluszem
    (kawałki kapelusza są na końcu listy, więc ziarna wcześniejszych kawałków się nie zmieniają)."""
    orig = J.stack

    def wymuszone(w, h, parts, seed=0, _s=seed):
        return orig(w, h, parts, seed=_s)
    J.stack = wymuszone
    try:
        return J._korpus_img(spec)
    finally:
        J.stack = orig


def _kawalki(spec):
    """Lista kawałków, z których _korpus_img skleja korpus (i ziarno), bez rysowania."""
    zap = {}
    orig = J.stack

    def lapka(w, h, parts, seed=0):
        zap.update(parts=list(parts), seed=seed, wh=(w, h))
        return orig(w, h, parts, seed=seed)
    J.stack = lapka
    try:
        J._korpus_img(spec)
    finally:
        J.stack = orig
    return zap


@lru_cache(None)
def bez_kapelusza(key):
    """Klucz lalki bez kapelusza na głowie (te same piksele korpusu) i wycinek samego kapelusza na arkuszu korpusu
    (crop=False: kapelusz na głowie leży dokładnie tam, gdzie był)."""
    spec = J.spec(key)
    pelny = _kawalki(spec)
    nowy = f"{key}__bez_kapelusza"
    J.LALKI[nowy] = dict(J.LALKI[key], kapelusz=None)
    goly = _kawalki(J.spec(nowy))
    n0 = len(goly["parts"])
    f = J.figura(nowy)
    f.body = Sprite(_korpus_z_ziarnem(J.spec(nowy), pelny["seed"]), f"lalka-{nowy}", rim=2, clean=False, crop=False)
    w, h = pelny["wh"]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(n0, len(pelny["parts"])):  # te same kawałki i ziarna co w pełnej lalce
        part = pelny["parts"][i]
        im = Z0.glue(im, Z0.piece(w, h, part[0], part[1], seed=pelny["seed"] + i * 7, **(part[2] if len(part) > 2 else {})))
    if spec["szer"] != 1.0:
        im = im.resize((round(w * spec["szer"]), h), Image.LANCZOS)
    return nowy, Sprite(im, f"kapelusz-{key}", rim=2, clean=False, crop=False)


@lru_cache(None)
def ramie(key):
    """Ramię i przedramię lalki z arkusza całej ręki (ten sam arkusz, crop=False); oba kończą się w łokciu półkolem —
    staw na spince."""
    f = J.figura(key)
    img = J._ramie_img(f.s)
    al = np.asarray(img.getchannel("A")).astype(np.float32)
    hh, ww = al.shape
    yy, xx = np.mgrid[0:hh, 0:ww]
    ex, ey = f.zawias[0], LOKIEC_V
    kolo = ((xx - ex) / (23 * f.s["szer"])) ** 2 + ((yy - ey) / 23.0) ** 2 <= 1
    out = []
    for nazwa, keep in (("ramie", (yy <= ey) | kolo), ("przedramie", (yy >= ey) | kolo)):
        im = img.copy()
        im.putalpha(Image.fromarray(np.where(keep, al, 0).astype(np.uint8)))
        out.append(Sprite(im, f"{nazwa}-{key}", rim=2, clean=False, crop=False))
    return tuple(out)


def _ik(S, T, L1, L2, strona, flip):
    """Odwrotna kinematyka ręki z łokciem: bark S, cel dłoni T. Zwraca łokieć, dłoń, kąty obu kawałków (jak rot w
    Stage.put: 0 — kawałek zwisa w dół), czy cel jest w zasięgu i o ile dłoń mija cel (px)."""
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = math.hypot(dx, dy)
    lo, hi = abs(L1 - L2) + 1e-3, L1 + L2 - 1e-3
    ok = lo - 0.5 <= d <= hi + 0.5
    dc = clamp(d, lo, hi)
    base = math.atan2(dy, dx)
    a = math.acos(clamp((L1 * L1 + dc * dc - L2 * L2) / (2 * L1 * dc), -1.0, 1.0))
    kand = [(S[0] + L1 * math.cos(base + s * a), S[1] + L1 * math.sin(base + s * a)) for s in (1, -1)]
    ocena = {"dol": lambda e: e[1], "gora": lambda e: -e[1], "przod": lambda e: flip * e[0], "tyl": lambda e: -flip * e[0]}
    E = max(kand, key=ocena[strona])
    ux, uy = (dx / d, dy / d) if d > 1e-6 else (0.0, 1.0)
    Tc = (S[0] + ux * dc, S[1] + uy * dc)
    ex, ey = Tc[0] - E[0], Tc[1] - E[1]
    n = math.hypot(ex, ey) or 1.0
    Hd = (E[0] + ex / n * L2, E[1] + ey / n * L2)
    r1 = math.degrees(math.atan2(-(E[0] - S[0]), E[1] - S[1]))
    r2 = math.degrees(math.atan2(-(Hd[0] - E[0]), Hd[1] - E[1]))
    return E, Hd, r1, r2, ok, math.hypot(Hd[0] - T[0], Hd[1] - T[1])


# ---------- układ ----------

class Uklad:
    """Rejestr obiektów jednej klatki: kto jest w jakim rzędzie, z czego się składa (wycinki Stage), do czego jest
    przyczepiony i co trzeba sprawdzić."""

    def __init__(self, st, t, rzedy=None):
        self.st, self.t = st, t
        self.rzedy = dict(rzedy or RZEDY_WNETRZA)
        self.obiekty = {}  # nazwa → dane (rodzaj, rzad, p, ...)
        self.wl = {}  # indeks wycinka w st.items → nazwa obiektu
        self.kontrole = []  # (rodzaj, opis, dane) — sprawdza kontrola() po ułożeniu klatki
        self.wiezy = []  # (opis, ok, wartość) — sprawdzone od razu (zasięg ręki)
        self.relacje = []  # (a, b, opis) — do rzutu z góry
        self.dlonie = {}  # nazwa lalki → (x, y, p) dłoni przedniej ręki (zbliżenia dłoni w kontroli)
        st.uklad = self

    # ---- rzędy ----
    def p(self, rzad, glebia=0.0):
        """Plan głębi rzędu; (rząd_a, rząd_b, k) — przejście; glebia — kolejność w obrębie rzędu (0..1)."""
        if isinstance(rzad, tuple):
            a, b, k = rzad
            return self.p(a) + (self.p(b) - self.p(a)) * clamp(k) + 0.003 * glebia
        return self.rzedy[rzad] + 0.003 * glebia

    @contextmanager
    def obiekt(self, nazwa, rodzaj="rzecz", **meta):
        """Wszystko, co położy się na scenie w tym bloku, należy do obiektu `nazwa` (bufor identyfikatorów, rzut)."""
        n0 = len(self.st.items)
        try:
            yield
        finally:
            for i in range(n0, len(self.st.items)):
                self.wl.setdefault(i, nazwa)
            o = self.obiekty.setdefault(nazwa, dict(rodzaj=rodzaj))
            o.update(meta)

    def put(self, nazwa, spr, x, y, p, rodzaj="dekoracja", **kw):
        with self.obiekt(nazwa, rodzaj, p=p):
            self.st.put(spr, x, y, p, **kw)

    # ---- meble i rzeczy ----
    def mebel(self, nazwa, key, x, h, rzad="przod", k=1.0, seed=130, y=712, wob=0.0):
        """Mebel wyrasta od dołu (jak Z0.rise) w swoim rzędzie; zwraca położenie arkusza (do blatów)."""
        ark = ark_mebel(key)
        p = self.p(rzad)
        with self.obiekt(nazwa, "mebel", rzad=rzad, p=p, k=k):
            Z0.rise(self.st, ark.spr, x, y, p, k, self.t, seed, wob=wob, h=h)
        yy = y + (1 - back(k, 1.3)) * h * 1.08
        rot = settle((k - 0.75) / 0.25 if k < 1 else 0, 1.5, 2.5) + wob * noise(self.t, seed, 0.5)
        geo = Geo(x, yy, h / ark.hs, (ark.x0 + 0.5 * ark.ws, ark.y0 + ark.hs), rot, 1.0, p)
        self.obiekty[nazwa].update(geo=geo, key=key)
        return geo

    def powierzchnia(self, mebel, nazwa, fu):
        """Punkt na powierzchni mebla (blat, płyta) w ułamku jej szerokości fu."""
        o = self.obiekty[mebel]
        u0, u1, v = POWIERZCHNIE[o["key"]][nazwa]
        return o["geo"](u0 + (u1 - u0) * fu, v)

    def rzecz(self, nazwa, ark, x, y, p, kotw, h, rot=0.0, sx=1.0, z=0.0, **kw):
        """Rzecz z arkusza `ark` punktem arkusza `kotw` w (x, y) planu p; h — wysokość całego wycinka w kadrze."""
        fa = ark.ulamek(*kotw)
        with self.obiekt(nazwa, "rzecz", p=p):
            self.st.put(ark.spr, x, y, p, h=h, anchor=fa, rot=rot, sx=sx, z=z, **kw)
        return Geo(x, y, h / ark.hs, kotw, rot, sx, p)

    def na(self, nazwa, key, mebel, pow_, fu, h, **kw):
        """Rzecz stoi na powierzchni mebla: dno na blacie, plan tuż przed meblem (wytyczne 1.28)."""
        ark = ark_rek(key)
        x, y = self.powierzchnia(mebel, pow_, fu)
        p = self.obiekty[mebel]["p"] + 0.002
        geo = self.rzecz(nazwa, ark, x, y, p, (ark.srodek, ark.dol), h, **kw)
        self.relacje.append((nazwa, mebel, "na " + pow_))
        self.na_powierzchni(nazwa, (x, y, p), f"{nazwa} stoi na: {mebel}")
        return geo

    # ---- lalka ----
    def lalka(self, nazwa, key, x, h=300, rzad="lalki", y=SW.STOPY, flip=1.0, lean=0.0, sink=0.0, lift=0.0, hop=0.0, k=1.0,
              wejscie=True, przod=0.0, tyl=0.0, lokiec=("dol", "dol"), glebia=0.0, kapelusz=None, siedzi=False, tint=None,
              alpha=1.0, shadow=True, blur=None):
        """Lalka na patyczku (te same liczby co scena.lalka: wejście zza rampy, chwianie, obrót), ale:
        - ręce z łokciem: przod / tyl to kąt w stopniach (0 — opuszczona, 90 — przed siebie) albo cel dłoni (x, y)
          w kadrze, albo funkcja szkieletu zwracająca cel (cel liczony z położenia korpusu w tej klatce);
        - kapelusz osobno: None — lalka jak w zestawie; {"gdzie": "glowa"} albo {"gdzie": "dlon", "chwyt": (u, v),
          "przechyl": stopnie} — kapelusz w dłoni przedniej ręki, trzymany za punkt chwytu (u, v) arkusza korpusu 300 × 690.
        Zwraca szkielet: barki, łokcie, dłonie, `punkt(u, v)` korpusu, plan p, flip; None, gdy lalki nie ma na scenie."""
        st, t = self.st, self.t
        seed = sum(map(ord, key))
        if wejscie:
            k = k * SW.wejscie(1.0 + 0.08 * (seed % 5))
        p = self.p(rzad, glebia)
        self.obiekty.setdefault(nazwa, dict(rodzaj="lalka"))
        self.obiekty[nazwa].update(rzad=rzad, p=p, k=k)
        if k <= 0 or sink >= 1:
            return None
        cialo, hat = bez_kapelusza(key) if kapelusz is not None else (key, None)
        f = J.figura(cialo)
        sc = h / f.wys
        yy = y + (1 - back(k, 1.2)) * h * 1.1 + ease(sink) * h * 1.12 - lift - abs(math.sin(x / 26.0)) * hop
        rot = 0.5 * noise(t, seed, 0.45) + lean + settle((k - 0.75) / 0.25 if k < 1 else 0, 1.5, 3)
        flip = math.copysign(max(abs(flip), 0.035), flip)
        af = (f.cw / 2, f.stopa)
        korpus = Geo(x, yy, sc, af, rot, flip, p)
        kk = f.s["szer"]
        szk = dict(korpus=korpus, punkt=lambda u, v: korpus(f.cw / 2 + (u - 150) * kk, v), p=p, flip=flip, rot=rot, sc=sc,
                   x=x, yy=yy, h=h, k=k)
        for name in ("tyl", "przod"):
            bx, by = f.bark[name]
            szk["bark_" + name] = korpus(bx, by)
        L1, L2 = (LOKIEC_V - J.RAMIE_ZAWIAS[1]) * sc, (J.DLON[1] - LOKIEC_V) * sc
        szk["L"] = (L1, L2)
        szk["r_dloni"] = R_DLONI * sc
        gora, dol_ = ramie(cialo)
        kw = dict(tint=tint, alpha=alpha, shadow=shadow, blur=blur)
        with self.obiekt(nazwa, "lalka"):
            for name, cel, strona in (("tyl", tyl, lokiec[1]), ("przod", przod, lokiec[0])):
                S_ = szk["bark_" + name]
                if callable(cel):
                    cel = cel(szk)
                if isinstance(cel, (int, float)):
                    r1 = rot - flip * cel
                    r2 = r1 - flip * 6  # ręka opuszczona albo uniesiona — lekko zgięta w łokciu
                    E = (S_[0] + _off(0, L1, r1)[0], S_[1] + _off(0, L1, r1)[1])
                    Hd = (E[0] + _off(0, L2, r2)[0], E[1] + _off(0, L2, r2)[1])
                else:
                    E, Hd, r1, r2, ok, blad = _ik(S_, cel, L1, L2, strona, flip)
                    self.wiezy.append((f"{nazwa}: dłoń ({'przednia' if name == 'przod' else 'tylna'}) sięga celu",
                                       ok and blad < 2.0, blad))
                z = -0.05 if name == "tyl" else 0.05
                st.put(gora, S_[0], S_[1], p, h=f.ah * sc, anchor=(f.zawias[0] / f.aw, f.zawias[1] / f.ah), rot=r1, sx=flip,
                       z=z, **kw)
                st.put(dol_, E[0], E[1], p, h=f.ah * sc, anchor=(f.zawias[0] / f.aw, LOKIEC_V / f.ah), rot=r2, sx=flip,
                       z=z + 0.001, **kw)
                szk[name] = dict(bark=S_, lokiec=E, dlon=Hd, r1=r1, r2=r2)
            self.dlonie[nazwa] = (*szk["przod"]["dlon"], p)
            body = f.siedzi if siedzi else f.body
            if hat is not None and kapelusz.get("gdzie") == "glowa":  # cień kapelusza na ścianę (korpus go zasłoni)
                st.put(hat, x, yy, p, h=f.ch * sc, anchor=(af[0] / f.cw, af[1] / f.ch), rot=rot, sx=flip, z=-0.001, **kw)
            st.put(body, x, yy, p, h=f.ch * sc, anchor=(af[0] / f.cw, af[1] / f.ch), rot=rot, sx=flip, **kw)
        if hat is not None:
            hn = kapelusz.get("nazwa", f"kapelusz ({nazwa})")
            kw_h = dict(kw, shadow=(2, 3, 2.5, 0.42))  # cień jak przy sklejaniu wycinanki
            if kapelusz.get("gdzie") == "glowa":
                self.put(hn, hat, x, yy, p, "rzecz", h=f.ch * sc, anchor=(af[0] / f.cw, af[1] / f.ch), rot=rot, sx=flip,
                         z=0.03, **kw_h)
                self.relacje.append((hn, nazwa, "na głowie"))
                szk["kapelusz"] = korpus
            else:
                u, v = kapelusz["chwyt"]
                us = f.cw / 2 + (u - 150) * kk
                hx, hy = szk["przod"]["dlon"]
                hrot = rot + kapelusz.get("przechyl", 0.0)
                self.put(hn, hat, hx, hy, p, "rzecz", h=f.ch * sc, anchor=(us / f.cw, v / f.ch), rot=hrot, sx=flip, z=0.045,
                         **dict(kw, shadow=True))
                self.relacje.append((hn, nazwa, "w dłoni"))
                szk["kapelusz"] = Geo(hx, hy, sc, (us, v), hrot, flip, p)
                self.dotyka(hn, (hx, hy, p), f"{nazwa}: dłoń trzyma kapelusz (wycinek przy dłoni)", 3.0)
        return szk

    def w_dloni(self, nazwa, ark, szk, chwyt, h, rot, p=None, z=0.08, reka="przod", **kw):
        """Rzecz w dłoni: punkt chwytu arkusza leży w dłoni; kierunek rzeczy podaje ujęcie (do czego służy, a nie za ręką).
        p — plan rzeczy (domyślnie plan lalki, przed dłonią); rzecz w naczyniu dostaje plan naczynia."""
        hx, hy = szk[reka]["dlon"]
        pp = szk["p"] if p is None else p
        geo = self.rzecz(nazwa, ark, hx, hy, pp, chwyt, h, rot=rot, sx=szk["flip"], z=z, **kw)
        self.dotyka(nazwa, (hx, hy, szk["p"]), f"{nazwa}: w dłoni (wycinek przy dłoni)", 3.0)
        return geo

    @staticmethod
    def dlon_z_kata(szk, kat, reka="przod"):
        """Gdzie byłaby dłoń przy kącie ręki `kat` (ręka lekko zgięta jak w lalka()) — początek i koniec ruchu do celu."""
        L1, L2 = szk["L"]
        S_ = szk["bark_" + reka]
        r1 = szk["rot"] - szk["flip"] * kat
        r2 = r1 - szk["flip"] * 6
        e = _off(0, L1, r1)
        d = _off(0, L2, r2)
        return S_[0] + e[0] + d[0], S_[1] + e[1] + d[1]

    # ---- kontrole (sprawdza kontrola() po ułożeniu klatki) ----
    def widac(self, nazwa, ile, opis=None, oprocz=("rampa",)):
        """Widać co najmniej `ile` obiektu; zasłonięcie przez obiekty z `oprocz` (rampa chowa stopy, własna dłoń kapelusz)
        jest zamierzone i się nie liczy — liczy się to, co zasłania coś innego."""
        self.kontrole.append(("widac", opis or f"{nazwa}: widać ≥ {ile:.0%}", (nazwa, ile, tuple(oprocz))))

    def punkt(self, nazwa, xyp, opis, r=7, ile=0.3):
        """W kółku o promieniu r wokół punktu (x, y, p) co najmniej `ile` pikseli należy do obiektu (głowa, dłoń)."""
        self.kontrole.append(("punkt", opis, (nazwa, xyp, r, ile)))

    def kontakt(self, a, b, opis, tol=2.0):
        self.kontrole.append(("kontakt", opis, (a, b, tol)))

    def dotyka(self, nazwa, xyp, opis, tol=3.0):
        """Narysowany wycinek obiektu (pełna maska, także część zasłonięta) leży najdalej `tol` px od punktu — dłoń
        naprawdę trzyma rzecz, a nie tylko liczby się zgadzają."""
        self.kontrole.append(("dotyka", opis, (nazwa, xyp, tol)))

    def na_powierzchni(self, nazwa, xyp, opis, tol=2.0):
        self.kontrole.append(("na", opis, (nazwa, xyp, tol)))

    def w_otworze(self, nazwa, prost, opis):
        """Widoczne piksele obiektu leżą w prostokącie otworu (x0, y0, x1, y1, p) — wytyczne 1.1."""
        self.kontrole.append(("otwor", opis, (nazwa, prost)))

    def w_naczyniu(self, nazwa, brzeg, opis):
        """Nic z obiektu nie jest widoczne poniżej brzegu naczynia (x0, x1, y, p) — wytyczne 1.22."""
        self.kontrole.append(("naczynie", opis, (nazwa, brzeg)))


# ---------- bufor identyfikatorów i kontrola ----------

def _ekran(st, x, y, p):
    sx, sy = st.cam.screen(x, y, p)
    return sx * papier.Q, sy * papier.Q


def bufor(st):
    """Bufor identyfikatorów klatki: dla każdego piksela — który obiekt jest na wierzchu (−1 pustka, −2 bez właściciela),
    i pełne maski obiektów (także części zasłonięte). Cienie i światło (tryb add) się nie liczą."""
    u = st.uklad
    st._plotno()
    st._off = (0.0, 0.0)
    nazwy = sorted(set(u.wl.values()))
    kod = {n: i for i, n in enumerate(nazwy)}
    H_, W_ = st.oh, st.ow
    idb = np.full((H_, W_), -1, np.int32)
    pelne = {}
    plotno = np.ones((H_, W_, 3), np.float32)
    for kind, p, z, n, it in sorted(st.items, key=lambda i: (i[1], i[2], i[3])):
        g = st.cam.mag(p)
        if g is None or (kind == "spr" and it["mode"] != "over") or it["alpha"] < 0.3:
            continue  # światło, i to, czego jeszcze prawie nie ma (wyłania się przy budowie dekoracji)
        if kind == "spr":  # kształt bez przezroczystości wejścia: pojawiający się garnek ma już swoje dno
            st._sprite(plotno, p, g, **dict(it, tint=(0.0, 0.0, 0.0), shadow=None, blur=0.0, haze=None, alpha=1.0))
        else:
            st._line(plotno, p, g, **dict(it, color=(0, 0, 0)))
        m = plotno[..., 0] < 0.5
        if not m.any():
            continue
        plotno[m] = 1.0
        plotno[(plotno[..., 0] < 1.0)] = 1.0
        wl = u.wl.get(n)
        idb[m] = kod[wl] if wl is not None else -2
        if wl is not None:
            pelne[wl] = pelne[wl] | m if wl in pelne else m
    return idb, pelne, kod


def kontrola(st):
    """Sprawdza kontrole ułożonej klatki: [(opis, ok, wartość)] + bufor (do rzutu)."""
    u = st.uklad
    idb, pelne, kod = bufor(st)
    H_, W_ = idb.shape
    wyn = [(o, ok, w) for o, ok, w in u.wiezy]
    widac = {n: float((idb == kod[n]).sum()) / max(1, int(m.sum())) for n, m in pelne.items()}
    for rodzaj, opis, d in u.kontrole:
        if rodzaj == "widac":
            n, ile, oprocz = d
            m = pelne.get(n)
            if m is None:
                wyn.append((opis, False, "nie ma w kadrze"))
                continue
            dozw = [kod[o] for o in oprocz if o in kod] + [kod[n]]
            v = float(np.isin(idb[m], dozw).mean())
            wyn.append((opis, v >= ile, f"{v:.0%}"))
        elif rodzaj == "punkt":
            n, (x, y, p), r, ile = d
            sx, sy = _ekran(st, x, y, p)
            yy, xx = np.ogrid[0:H_, 0:W_]
            kolo = (xx - sx) ** 2 + (yy - sy) ** 2 <= r * r
            v = float((idb[kolo] == kod.get(n, -9)).mean()) if kolo.any() else 0.0
            wyn.append((opis, v >= ile, f"{v:.0%} kółka"))
        elif rodzaj == "kontakt":
            (ax, ay, ap), (bx, by, bp), tol = d
            a, b = _ekran(st, ax, ay, ap), _ekran(st, bx, by, bp)
            v = math.hypot(a[0] - b[0], a[1] - b[1])
            wyn.append((opis, v <= tol, f"{v:.1f} px"))
        elif rodzaj == "dotyka":
            n, (x, y, p), tol = d
            m = pelne.get(n)
            if m is None:
                wyn.append((opis, False, "rzeczy nie ma w kadrze"))
                continue
            sx, sy = _ekran(st, x, y, p)
            r = int(tol + 40)
            y0, x0 = max(0, int(sy) - r), max(0, int(sx) - r)
            okno = m[y0:int(sy) + r + 1, x0:int(sx) + r + 1]
            ys_, xs_ = np.nonzero(okno)
            v = float(np.min(np.hypot(xs_ + x0 - sx, ys_ + y0 - sy))) if len(xs_) else 99.0
            wyn.append((opis, v <= tol, f"{v:.1f} px"))
        elif rodzaj == "na":
            n, (x, y, p), tol = d
            m = pelne.get(n)
            if m is None:
                wyn.append((opis, True, "jeszcze nie ma"))
                continue
            dno = np.nonzero(m.any(axis=1))[0][-1] + 1
            v = dno - _ekran(st, x, y, p)[1]
            wyn.append((opis, abs(v) <= tol, f"dno {v:+.1f} px"))
        elif rodzaj == "otwor":
            n, (x0, y0, x1, y1, p) = d
            a, b = _ekran(st, x0, y0, p), _ekran(st, x1, y1, p)
            wid = idb == kod.get(n, -9)
            poza = wid.copy()
            poza[max(0, int(a[1]) - 2):int(b[1]) + 3, max(0, int(a[0]) - 2):int(b[0]) + 3] = False
            v = int(poza.sum())
            wyn.append((opis, v == 0, f"{v} px poza otworem"))
        elif rodzaj == "naczynie":
            n, (x0, x1, y, p) = d
            sy = _ekran(st, x0, y, p)[1]
            wid = idb == kod.get(n, -9)
            v = int(wid[int(math.ceil(sy + 1.5)):].sum())
            wyn.append((opis, v == 0, f"{v} px pod brzegiem"))
    return wyn, idb, pelne, kod, widac


# ---------- rzut z góry ----------

BARWY = {"lalka": (70, 110, 170), "mebel": (150, 104, 64), "rzecz": (214, 140, 40), "dekoracja": (150, 150, 150)}


def rzut(st, pelne, widac, wyniki=None, w=640, h=360, pokaz=None):
    """Plan sceny z góry: rzędy od ściany (u góry) do rampy (na dole), obiekty w swoich rzędach na szerokości, jaką
    zajmują w kadrze, przyczepienia liniami i kamera. Do obejrzenia obok klatki — kto stoi za kim i co do czego
    jest przyczepione."""
    u = st.uklad
    im = Image.new("RGB", (w, h), (246, 241, 230))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 11)
    fb = ImageFont.truetype(FONT, 13)
    rz = sorted(u.rzedy.items(), key=lambda kv: kv[1])
    top, bot = 22, h - 58
    ys = {n: top + (bot - top) * i / max(1, len(rz) - 1) for i, (n, _) in enumerate(rz)}
    ps = [p for _, p in rz]

    def y_od_p(p):
        if p <= ps[0]:
            return ys[rz[0][0]]
        for (n0, p0), (n1, p1) in zip(rz, rz[1:]):
            if p0 <= p <= p1:
                return ys[n0] + (ys[n1] - ys[n0]) * (p - p0) / max(1e-6, p1 - p0)
        return ys[rz[-1][0]]
    for n, _ in rz:
        d.line([(0, ys[n]), (w, ys[n])], fill=(222, 214, 200))
        d.text((4, ys[n] - 13), NAZWY_RZEDOW.get(n, n), font=f, fill=(150, 140, 125))
    sk = w / (st.ow or 1280)
    srodki = {}
    for n, o in u.obiekty.items():
        if pokaz and n not in pokaz:
            continue
        m = pelne.get(n)
        if m is None or "p" not in o:
            continue
        cols = np.nonzero(m.any(axis=0))[0]
        x0, x1 = cols[0] * sk, (cols[-1] + 1) * sk
        y = y_od_p(o["p"])
        kol = BARWY.get(o.get("rodzaj"), (150, 150, 150))
        hh = 9 if o.get("rodzaj") in ("lalka", "mebel") else 6
        d.rectangle([x0, y - hh, x1, y + hh], fill=kol, outline=(40, 34, 30))
        etk = f"{n} {widac.get(n, 0):.0%}"
        if o.get("rodzaj") == "rzecz":  # rzeczy podpisane pod pudełkiem, lalki i meble nad — mniej nakładania
            d.text(((x0 + x1) / 2, y + hh + 1), etk, font=f, fill=(150, 90, 10), anchor="ma")
        else:
            d.text(((x0 + x1) / 2, y - hh - 2), etk, font=f, fill=(40, 34, 30), anchor="md")
        srodki[n] = ((x0 + x1) / 2, y)
    for a, b, opis in u.relacje:
        if a in srodki and b in srodki:
            (ax, ay), (bx, by) = srodki[a], srodki[b]
            d.line([(ax, ay), (bx, by)], fill=(190, 40, 40), width=2)
            d.text((max(ax, bx) + 4, (ay + by) / 2 - 6), opis, font=f, fill=(190, 40, 40))
    cx = w / 2
    d.polygon([(cx - 12, h - 8), (cx + 12, h - 8), (cx, h - 30)], fill=(40, 34, 30))
    d.line([(cx, h - 30), (0, top)], fill=(200, 190, 175))
    d.line([(cx, h - 30), (w, top)], fill=(200, 190, 175))
    d.text((cx + 16, h - 22), "kamera", font=f, fill=(40, 34, 30))
    if wyniki is not None:
        zle = [o for o, ok, _ in wyniki if not ok]
        d.text((w - 6, h - 22), f"kontrole: {len(wyniki) - len(zle)}/{len(wyniki)} OK", font=fb,
               fill=(30, 120, 50) if not zle else (190, 40, 40), anchor="ra")
    return im
