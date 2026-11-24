"""Teatr papierowy rysowany kodem: wycinki na planach głębi, kamera wieloplanowa, cienie między planami, światło.

Jedna klatka powstaje tak:
1. ujęcie (funkcja `s_nazwa(st, t, T)`) ustawia kamerę `st.cam` i kładzie wycinki `st.put(...)` w układzie kadru
   wzorcowego 1280 × 720 (to, co widać, gdy kamera stoi przed otworem sceny), każdy na swoim planie głębi `p`;
2. `Stage.render()` rysuje plany od najdalszego: cień wycinka pada na wszystko za nim, potem sam wycinek;
3. na koniec światło (plama reflektora, winieta), barwa ujęcia i ziarno.

Plan głębi `p` to odwrotność odległości od kamery (1 = rama sceny, 0,8 = lalki, 0,14 = papier nieba). Kamera jedzie
naprawdę (wózek) i ma obiektyw: bliższe plany rosną i przesuwają się szybciej niż dalsze — stąd paralaksa.
Wycinki trzymane są z alfą wymnożoną (premultiplied), żeby krawędzie nie łapały obwódek przy skalowaniu.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1280, 720, 24
Q = 1.0  # jakość: 1 = pełne 1280 × 720, 0.5 = szkic 640 × 360 do przeglądu w Studio (ta sama geometria)
CX, CY = W / 2, H / 2
VOID = (255, 0, 255)  # nienarysowane miejsce: kontrola „końca świata” szuka tej barwy
SHADOW = np.array([0.16, 0.09, 0.05], np.float32)  # ciepły cień, nie czarny
HAZE = np.array([0.93, 0.83, 0.66], np.float32)  # mgiełka dali: barwa papieru nieba


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def back(x, s=1.6):
    """Dojście z lekkim przestrzeleniem (papier na patyczku nie staje od razu)."""
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def noise(t, seed, speed=1.0):
    """Gładki szum -1..1 — ruch „z ręki”, nie z sinusa (jak w render.py Oddziału C)."""
    x = t * speed
    i = math.floor(x)
    f = x - i
    a = random.Random(seed * 7919 + i).uniform(-1, 1)
    b = random.Random(seed * 7919 + i + 1).uniform(-1, 1)
    return a + (b - a) * f * f * (3 - 2 * f)


def settle(x, swings=2.5, amp=1.0):
    """Gasnące kołysanie po dojściu na miejsce: 0 przed, wahnięcia po, 0 na końcu. x = czas od dojścia / czas gaśnięcia."""
    if x <= 0 or x >= 1:
        return 0.0
    return amp * math.sin(x * swings * 2 * math.pi) * (1 - x) ** 2


class Sprite:
    """Jeden wycinek z papieru: obraz z alfą wymnożoną, w kilku rozdzielczościach (mipmapy)."""

    def __init__(self, img, name="", rim=2, clean=True, pad=2, crop=True):
        if Q <= 0.5 and min(img.size) > 96:  # szkic: wycinki w połowie rozdzielczości — 4× mniej pamięci (8 GB RAM)
            img = img.convert("RGBA").reduce(2)
            rim = max(1, rim // 2) if rim else rim
        a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255.0
        al = a[..., 3]
        if clean:  # generator zostawia niemal przezroczyste marginesy i poświatę — odcinamy je
            al = np.clip((al - 0.10) / 0.82, 0, 1)
        ys, xs = np.where(al > 0.03)
        if len(xs) == 0:
            raise ValueError(f"pusty wycinek: {name}")
        x0, x1 = max(0, xs.min() - pad), min(al.shape[1], xs.max() + 1 + pad)
        y0, y1 = max(0, ys.min() - pad), min(al.shape[0], ys.max() + 1 + pad)
        if not crop:  # arkusz zostaje w całości: kawałki tej samej układanki (mapa) dzielą jeden układ współrzędnych
            x0, y0, x1, y1 = 0, 0, al.shape[1], al.shape[0]
        al, rgb = al[y0:y1, x0:x1], a[y0:y1, x0:x1, :3].copy()
        if rim:  # grubość papieru: jasna krawędź od strony światła (góra-lewo), ciemna po przeciwnej
            hi = np.clip(al - np.roll(al, (rim, rim), (0, 1)), 0, 1)[..., None]
            lo = np.clip(al - np.roll(al, (-rim, -rim), (0, 1)), 0, 1)[..., None]
            rgb = rgb + (np.array([1.0, 0.95, 0.84], np.float32) - rgb) * hi * 0.55
            rgb = rgb * (1 - 0.45 * lo)
        pm = np.dstack([np.clip(rgb, 0, 1) * al[..., None], al])
        base = Image.fromarray((pm * 255 + 0.5).astype(np.uint8), "RGBA")
        self.name, (self.w, self.h) = name, base.size
        self.mips = [base]
        while min(self.mips[-1].size) > 40:
            self.mips.append(self.mips[-1].reduce(2))
        small = base.getchannel("A").resize((max(8, self.w // 4), max(8, self.h // 4)), Image.BILINEAR)
        self._alpha = np.asarray(small)

    def top(self, fx):
        """Górna krawędź wycinka w kolumnie fx (0..1) jako ułamek wysokości — np. grań, zza której wychodzi mur."""
        col = self._alpha[:, int(clamp(fx, 0, 0.9999) * self._alpha.shape[1])]
        hit = np.nonzero(col > 128)[0]
        return 1.0 if len(hit) == 0 else hit[0] / self._alpha.shape[0]

    def bottom(self, fx):
        col = self._alpha[:, int(clamp(fx, 0, 0.9999) * self._alpha.shape[1])]
        hit = np.nonzero(col > 128)[0]
        return 0.0 if len(hit) == 0 else (hit[-1] + 1) / self._alpha.shape[0]


class Cam:
    """Kamera patrzy na punkt (x, y) kadru wzorcowego na planie `pf` — ten punkt jest w środku ekranu.
    m — powiększenie planu `pf` względem kadru wzorcowego;
    lens — ile z tego robi obiektyw (reszta to dojazd wózkiem: bliskie plany rosną szybciej niż dalekie);
    truck — jaka część przesunięcia w bok to jazda kamery (paralaksa), a jaka zwykły obrót (bez paralaksy);
    trucky — to samo w pionie (domyślnie 0: kamera stoi na wysokości sceny, więc linie ziemi zostają jak we wzorcu).
    lens = m i truck = 0 daje dokładny wycinek kadru wzorcowego (długi obiektyw ze statywu)."""

    def __init__(self, x=CX, y=CY, m=1.0, pf=0.8, lens=None, truck=0.6, dx=0.0, dy=0.0, trucky=0.0):
        self.x, self.y, self.m, self.pf, self.truck, self.dx, self.dy, self.trucky = x, y, m, pf, truck, dx, dy, trucky
        L = lens if lens else m ** 0.7
        zi = 1 - (1 - L / m) / pf
        if zi < 0.05:  # wózek nie przejeżdża przez plan ostrości: resztę robi obiektyw
            zi = 0.05
            L = m * (1 - pf * (1 - zi))
        self.lens, self.L, self.zi = L, L, zi
        self.X = CX + truck * (x - CX) / pf + dx
        self.Y = CY + trucky * (y - CY) / pf + dy  # wysokość kamery stała: w pionie kamera się pochyla
        gf = m  # powiększenie planu ostrości
        self.ox = (CX + (x - CX) / pf - self.X + dx) * pf * gf  # obrót kamery: reszta drogi do punktu, bez paralaksy
        self.oy = (CY + (y - CY) / pf - self.Y + dy) * pf * gf

    def mag(self, p):
        d = 1 - p + p * self.zi
        return self.L / d if d > 0.06 else None  # None: plan jest za kamerą

    def screen(self, x, y, p):
        g = self.mag(p)
        return (CX + (CX + (x - CX) / p - self.X) * p * g - self.ox, CY + (CY + (y - CY) / p - self.Y) * p * g - self.oy)

    @staticmethod
    def mix(a, b, k):
        """Płynne przejście między dwoma kadrami (k = 0..1)."""
        f = lambda u, v: u + (v - u) * k
        g = lambda u, v: math.exp(f(math.log(u), math.log(v)))
        return Cam(f(a.x, b.x), f(a.y, b.y), g(a.m, b.m), f(a.pf, b.pf), g(a.lens, b.lens), f(a.truck, b.truck),
                   f(a.dx, b.dx), f(a.dy, b.dy), f(a.trucky, b.trucky))


_SWIATLO = {}

# ---- pamięć wycinków i cieni ----
# Wycinek, który w kolejnych klatkach stoi na ekranie dokładnie w tym samym miejscu (statyczna kamera, dekoracja,
# lalka w bezruchu), dawał co klatkę od nowa to samo: przekształcenie, rozmycie głębi i rozmyty cień. Pamięć trzyma
# gotowy obraz i cień pod kluczem z dokładnych liczb (mipmapa, ramka, współczynniki przekształcenia, rozmycie), więc
# trafienie daje ten sam obraz piksel w piksel; wycinek, który drgnie choćby o ułamek piksela, liczy się od nowa.
# Rozmiar: PAMIEC_MB (domyślnie 300 MB na proces; 0 = wyłączona). Najdawniej użyte wypadają pierwsze.
from collections import OrderedDict  # noqa: E402
import os as _os  # noqa: E402

_PAMIEC = OrderedDict()  # klucz → [mipmapa, obraz po przekształceniu i rozmyciu, {miękkość: cień uint8}]
_PAMIEC_BAJTY = [0]
_PAMIEC_MAX = int(float(_os.environ.get("PAMIEC_MB", "300")) * 2 ** 20)


def _zapamietaj(klucz, mip, out, hit):
    if hit is not None:
        return hit
    hit = [mip, out, {}]
    if _PAMIEC_MAX <= 0:
        return hit
    old = _PAMIEC.pop(klucz, None)
    if old is not None:
        _PAMIEC_BAJTY[0] -= _bajty(old)
    _PAMIEC[klucz] = hit
    _PAMIEC_BAJTY[0] += out.size[0] * out.size[1] * 4
    while _PAMIEC_BAJTY[0] > _PAMIEC_MAX and len(_PAMIEC) > 1:
        _PAMIEC_BAJTY[0] -= _bajty(_PAMIEC.popitem(last=False)[1])
    return hit


def _bajty(hit):
    return hit[1].size[0] * hit[1].size[1] * 4 + sum(c.nbytes for c in hit[2].values())


class Stage:
    def __init__(self, t=0.0, seed=0):
        self.t, self.seed = t, seed
        self.cam = Cam()
        self.items = []
        self.focus, self.dof = 0.8, 1.0  # plan ostrości i siła głębi ostrości
        self.spot = None  # (x, y, p, promień, ciemność poza plamą 0..1)
        self.grade = (1.0, 1.0, 1.0)
        self.dim = 1.0  # jasność całej sceny (gaszenie światła)
        self.void = None  # barwa pustki; kontrola podaje VOID
        self._off = (0.0, 0.0)  # początek płótna w pikselach ekranu (warstwa stała bywa większa od kadru)

    # ---- kładzenie wycinków ----
    def put(self, spr, x, y, p, h=None, w=None, anchor=(0.5, 1.0), rot=0.0, sx=1.0, sy=1.0, alpha=1.0, shadow=True,
            blur=None, tint=None, haze=None, mode="over", z=0.0):
        """Wycinek `spr` kotwicą `anchor` w punkcie (x, y) kadru wzorcowego na planie p; h albo w — rozmiar w kadrze
        wzorcowym. shadow: True (domyślny cień planu), None albo (dx, dy, miękkość, siła). mode: over / add / mul."""
        if alpha <= 0.003 or abs(sx) < 0.012 or abs(sy) < 0.012:
            return
        k = (h / spr.h) if h else (w / spr.w)
        self.items.append(("spr", p, z, len(self.items), dict(
            spr=spr, x=x, y=y, k=k, anchor=anchor, rot=rot, sx=sx, sy=sy, alpha=alpha, shadow=shadow, blur=blur,
            tint=tint, haze=haze, mode=mode)))

    def line(self, pts, p, width=1.4, color=(60, 48, 40), alpha=0.9, z=0.0):
        """Nitka albo patyczek: łamana w kadrze wzorcowym na planie p."""
        self.items.append(("line", p, z, len(self.items), dict(pts=pts, width=width, color=color, alpha=alpha)))

    # ---- rysowanie ----
    def _plotno(self):
        self.ow, self.oh = int(round(W * Q)), int(round(H * Q))
        canvas = np.empty((self.oh, self.ow, 3), np.float32)
        canvas[:] = np.array(self.void if self.void else (0, 0, 0), np.float32) / 255.0
        return canvas

    def _rysuj(self, canvas, kind, p, g, it):
        if kind == "spr":
            self._sprite(canvas, p, g, **it)
        else:
            self._line(canvas, p, g, **it)

    def _obraz(self, canvas, post):
        if post:
            canvas = self._post(canvas)
        return Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8))

    def ulozone(self):
        """Wycinki w kolejności rysowania (od najdalszego planu), bez planów za kamerą: (rodzaj, p, g, parametry)."""
        out = []
        for kind, p, z, _, it in sorted(self.items, key=lambda i: (i[1], i[2], i[3])):
            g = self.cam.mag(p)
            if g is not None:
                out.append((kind, p, z, g, it))
        return out

    def render(self, post=True):
        canvas = self._plotno()
        for kind, p, z, g, it in self.ulozone():
            self._rysuj(canvas, kind, p, g, it)
        return self._obraz(canvas, post)

    def _sprite(self, canvas, p, g, spr, x, y, k, anchor, rot, sx, sy, alpha, shadow, blur, tint, haze, mode):
        W, H = self.ow, self.oh  # rozmiar płótna (klatka szkicu albo pełna, albo warstwa stała)
        S = self.cam.screen(x, y, p)
        S = (S[0] * Q - self._off[0], S[1] * Q - self._off[1])
        g = g * Q
        kk = k * g  # piksele ekranu na piksel wycinka
        lvl = min(len(spr.mips) - 1, max(0, int(math.floor(math.log2(1.25 / max(kk * max(abs(sx), abs(sy)), 1e-6))))))
        mip = spr.mips[lvl]
        fx, fy = mip.size[0] / spr.w, mip.size[1] / spr.h
        kx, ky = kk * sx / fx, kk * sy / fy
        au, av = anchor[0] * mip.size[0], anchor[1] * mip.size[1]
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        if blur is None:
            blur = min(5.0, self.dof * abs(math.log(p / self.focus)) * (self.cam.L ** 0.5))
        blur *= Q
        if blur < 0.35:
            blur = 0.0
        if shadow is True:
            d = 6 + 14 * p
            shadow = (d * 0.75, d, 5 + 9 * p, 0.42)
        pad = int(math.ceil(3 * blur + 2))
        if shadow and mode == "over":
            sdx, sdy, soft, strength = shadow
            sdx, sdy, soft = sdx * g, sdy * g, max(0.8, soft * g)
            pad = max(pad, int(math.ceil(2.5 * soft + max(abs(sdx), abs(sdy)) + 2)))
        xs, ys = [], []
        for u, v in ((0, 0), (mip.size[0], 0), (mip.size[0], mip.size[1]), (0, mip.size[1])):
            du, dv = (u - au) * kx, (v - av) * ky
            xs.append(S[0] + c * du - s * dv)
            ys.append(S[1] + s * du + c * dv)
        x0, x1 = max(-pad, int(math.floor(min(xs))) - pad), min(W + pad, int(math.ceil(max(xs))) + pad)
        y0, y1 = max(-pad, int(math.floor(min(ys))) - pad), min(H + pad, int(math.ceil(max(ys))) + pad)
        if x1 - x0 < 1 or y1 - y0 < 1 or x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
            return
        # odwzorowanie piksel ekranu → piksel wycinka (PIL liczy od środka piksela)
        coef = (c / kx, s / kx, au + (c * (x0 - S[0]) + s * (y0 - S[1])) / kx,
                -s / ky, c / ky, av + (-s * (x0 - S[0]) + c * (y0 - S[1])) / ky)
        klucz = (id(mip), x1 - x0, y1 - y0, coef, blur)  # te same liczby = ten sam obraz, piksel w piksel
        hit = _PAMIEC.get(klucz)
        if hit is not None and hit[0] is mip:
            _PAMIEC.move_to_end(klucz)
            out = hit[1]
        else:
            hit = None
            out = mip.transform((x1 - x0, y1 - y0), Image.AFFINE, coef, resample=Image.BILINEAR)  # mipmapa jest już bliska skali: dwuliniowe wystarcza, 2× szybciej
            if blur:
                out = out.filter(ImageFilter.GaussianBlur(blur))
        # widoczna część obszaru
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        if shadow and mode == "over":
            cien = hit[2].get(soft) if hit is not None else None
            if cien is None:
                a_img = out.getchannel("A")
                q = 4 if min(a_img.size) > 48 else 1
                small = a_img.reduce(q) if q > 1 else a_img
                small = small.filter(ImageFilter.GaussianBlur(soft / q))
                cien = np.asarray(small.resize(a_img.size, Image.BILINEAR))
                hit = _zapamietaj(klucz, mip, out, hit)
                hit[2][soft] = cien
                if _PAMIEC.get(klucz) is hit:
                    _PAMIEC_BAJTY[0] += cien.nbytes
            sh = cien.astype(np.float32) * (strength * alpha / 255.0)
            ox, oy = int(round(sdx)), int(round(sdy))
            # cień przesunięty o (ox, oy): piksel ekranu (X, Y) bierze cień z (X - ox, Y - oy)
            tx0, ty0, tx1, ty1 = max(0, x0 + ox), max(0, y0 + oy), min(W, x1 + ox), min(H, y1 + oy)
            if tx1 > tx0 and ty1 > ty0:
                part = sh[ty0 - oy - y0:ty1 - oy - y0, tx0 - ox - x0:tx1 - ox - x0, None]
                reg = canvas[ty0:ty1, tx0:tx1]
                if reg.shape[2] == 4:  # warstwa stała: cień to zwykłe „over” barwy SHADOW z alfą part
                    reg[..., 3:] += (1 - reg[..., 3:]) * part
                    reg = reg[..., :3]
                reg += (SHADOW - reg) * part
        if hit is None:
            _zapamietaj(klucz, mip, out, None)
        src = np.asarray(out.crop((cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0)), np.float32) * (1 / 255.0)
        rgb, a = src[..., :3], src[..., 3:]
        if tint is not None:
            rgb = rgb * np.asarray(tint, np.float32)
        if haze:
            rgb = rgb + (HAZE * a - rgb) * haze
        if alpha < 1:
            rgb, a = rgb * alpha, a * alpha
        reg = canvas[cy0:cy1, cx0:cx1]
        if reg.shape[2] == 4:  # warstwa stała (tylko tryb over): alfa warstwy jak w premultiplied over
            reg[..., 3:] *= 1 - a
            reg[..., 3:] += a
            reg = reg[..., :3]
        if mode == "add":
            reg += rgb
        elif mode == "mul":  # wycinek jako filtr: ciemnieje tam, gdzie jest
            reg *= 1 - a + rgb
        else:
            reg *= 1 - a
            reg += rgb

    def _line(self, canvas, p, g, pts, width, color, alpha):
        W, H = self.ow, self.oh
        q = [(a * Q - self._off[0], b * Q - self._off[1]) for a, b in (self.cam.screen(x, y, p) for x, y in pts)]
        wd = max(0.8 * Q ** 0.5, width * g * Q)
        pad = int(wd + 3)
        x0 = max(0, int(min(a for a, _ in q)) - pad)
        x1 = min(W, int(max(a for a, _ in q)) + pad + 1)
        y0 = max(0, int(min(b for _, b in q)) - pad)
        y1 = min(H, int(max(b for _, b in q)) + pad + 1)
        if x1 <= x0 or y1 <= y0:
            return
        ss = 3
        m = Image.new("L", ((x1 - x0) * ss, (y1 - y0) * ss), 0)
        ImageDraw.Draw(m).line([((a - x0) * ss, (b - y0) * ss) for a, b in q], fill=255, width=max(1, int(round(wd * ss))),
                               joint="curve")
        a = np.asarray(m.reduce(ss), np.float32)[..., None] * (alpha / 255.0)
        reg = canvas[y0:y1, x0:x1]
        if reg.shape[2] == 4:
            reg[..., 3:] += (1 - reg[..., 3:]) * a
            reg = reg[..., :3]
        reg += (np.array(color, np.float32) / 255.0 - reg) * a

    def _post(self, arr):
        W, H = self.ow, self.oh
        CX, CY = W / 2, H / 2
        if (W, H) not in _SWIATLO:  # ciepłe światło z góry z lewej + winieta: zależą tylko od rozmiaru klatki
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            key = 1.05 - 0.13 * (xx / W) - 0.10 * (yy / H)
            vig = 1 - 0.34 * (((xx - CX) / CX) ** 2 + ((yy - CY) / CY) ** 2) ** 1.25
            _SWIATLO[(W, H)] = (yy, xx, (key * np.clip(vig, 0.3, 1))[..., None])
        yy, xx, swiatlo = _SWIATLO[(W, H)]
        if self.spot:
            sx, sy, sp, r, dark = self.spot
            px, py = (v * Q for v in self.cam.screen(sx, sy, sp))
            r = r * self.cam.mag(sp) * Q
            d = np.sqrt((xx - px) ** 2 + ((yy - py) * 1.15) ** 2) / r
            arr = arr * (1 - dark * np.clip(d - 0.35, 0, 1) ** 1.3)[..., None]
        arr = arr * swiatlo
        arr = arr * (np.array(self.grade, np.float32) * self.dim)
        # lekki kontrast i ziarno zmieniane co 3 klatki (jak kreska w pozostałych filmach)
        arr = np.clip(arr, 0, 1)
        arr = arr + 0.10 * (arr * arr * (3 - 2 * arr) - arr)
        rng = np.random.default_rng(int(self.t * FPS) // 3 + 101 + self.seed)
        arr = arr + rng.normal(0, 0.011, (H, W, 1)).astype(np.float32)
        return arr


# ---- warstwy stałe: to, co w ujęciu stoi, rysuje się raz i potem tylko przesuwa ----
# Pomiar profilerem (14.11.2026, 3 ujęcia „Pierwszego cesarza”, ok. 450 ms na klatkę 1280 × 720): 71–77% czasu klatki
# szło na wycinki, które w ujęciu stoją (niebo, równina, wzgórza, góry, brama) — co klatkę od nowa: przekształcenie,
# rozmycie głębi, cień i nałożenie. Kamera jedzie, więc każdy plan przesuwa się inaczej (paralaksa), ale sąsiednie
# plany przez wiele klatek przesuwają się prawie tak samo. Warstwa = kolejne w porządku rysowania wycinki, które
# stoją (te same parametry), narysowane raz (z cieniami i rozmyciem) do jednego obrazu RGBA i potem co klatkę tylko
# przesunięte i przeskalowane jak jej pierwszy wycinek. Warstwa żyje tylko tak długo, jak każdy jej wycinek
# (i jego rozmycie) jest najwyżej TOL piksela od miejsca, w którym narysowałby go pełny render — potem powstaje nowa.

def _klucz(kind, p, z, it):
    """Tożsamość wycinka w ujęciu: te same parametry = ten sam papier w tym samym miejscu sceny."""
    if kind == "spr":
        if it["mode"] != "over":
            return None
        fz = lambda v: tuple(np.asarray(v, np.float64).ravel().tolist()) if isinstance(v, (list, tuple, np.ndarray)) else v
        return ("spr", p, z, id(it["spr"]), it["x"], it["y"], it["k"], tuple(it["anchor"]), it["rot"], it["sx"], it["sy"],
                it["alpha"], fz(it["shadow"]), it["blur"], fz(it["tint"]), it["haze"])
    return ("line", p, z, tuple(map(tuple, it["pts"])), it["width"], tuple(it["color"]), it["alpha"])


def _geom(st, kind, p, g, it):
    """(Sx, Sy, skala, rozmycie, ramka) wycinka na ekranie — te same wzory co w Stage._sprite / _line."""
    if kind != "spr":
        q = [(a * Q, b * Q) for a, b in (st.cam.screen(x, y, p) for x, y in it["pts"])]
        pad = max(0.8 * Q ** 0.5, it["width"] * g * Q) + 3
        xs, ys = [a for a, _ in q], [b for _, b in q]
        return q[0][0], q[0][1], g * Q, 0.0, (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
    spr, k, sx, sy = it["spr"], it["k"], it["sx"], it["sy"]
    S = st.cam.screen(it["x"], it["y"], p)
    S = (S[0] * Q, S[1] * Q)
    gq = g * Q
    kk = k * gq
    blur = it["blur"]
    if blur is None:
        blur = min(5.0, st.dof * abs(math.log(p / st.focus)) * (st.cam.L ** 0.5))
    blur *= Q
    if blur < 0.35:
        blur = 0.0
    shadow = it["shadow"]
    if shadow is True:
        d = 6 + 14 * p
        shadow = (d * 0.75, d, 5 + 9 * p, 0.42)
    pad = 3 * blur + 2
    if shadow:
        pad = max(pad, 2.5 * max(0.8, shadow[2] * gq) + max(abs(shadow[0]), abs(shadow[1])) * gq + 2)
    au, av = it["anchor"][0] * spr.w, it["anchor"][1] * spr.h
    c, s = math.cos(math.radians(it["rot"])), math.sin(math.radians(it["rot"]))
    xs, ys = [], []
    for u, v in ((0, 0), (spr.w, 0), (spr.w, spr.h), (0, spr.h)):
        du, dv = (u - au) * kk * sx, (v - av) * kk * sy
        xs.append(S[0] + c * du - s * dv)
        ys.append(S[1] + s * du + c * dv)
    return S[0], S[1], gq, blur, (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


class Warstwy:
    """Plan rysowania całego ujęcia (lista Stage, po jednym na klatkę, już ułożonych) z warstwami stałymi.
    render(f) daje tę samą klatkę co stages[f].render(), z dokładnością do TOL piksela w położeniu wycinków."""
    KMIN = 6  # warstwa opłaca się, gdy posłuży co najmniej tylu klatkom
    TOL = 0.2  # px: najdalej tyle wycinek warstwy może odjechać od swojego prawdziwego miejsca
    TOLB = 0.25  # px: tyle może się różnić rozmycie głębi
    SMAX = 0.04  # warstwa nie rośnie ani nie maleje o więcej niż 4% (przy najeździe powstaje nowa, ostra)
    FAZA = 4  # przy samym przesunięciu warstwa jest rysowana w ćwiartkach piksela i tylko kopiowana (błąd ≤ 1/8 px)
    BMIN = 1.0  # px: przy najeździe/odjeździe (warstwa się skaluje, więc próbkuje drugi raz) tylko plany co najmniej tak rozmyte
    FAZY_MAX = 8  # tyle faz jednej warstwy trzymanych naraz w pamięci

    def __init__(self, stages):
        self.st = stages
        self.ow, self.oh = int(round(W * Q)), int(round(H * Q))
        self.L = []
        for st in stages:
            rows = []
            for kind, p, z, g, it in st.ulozone():
                key = _klucz(kind, p, z, it)
                rows.append((kind, p, g, it, key, _geom(st, kind, p, g, it) if key else None))
            self.L.append(rows)
        self.pos = []
        for rows in self.L:
            d, dup = {}, set()
            for j, r in enumerate(rows):
                if r[4] is not None:
                    (dup.add(r[4]) if r[4] in d else d.__setitem__(r[4], j))
            self.pos.append({k: v for k, v in d.items() if k not in dup})  # powtórzony wycinek: bez warstwy
        self.grupy, self.plan, self.ile_klatek = [], [], 0
        self._planuj()

    # -- plan --
    def _mapa(self, gr, f):
        """Przesunięcie i skala warstwy grupy gr w klatce f (z jej pierwszego wycinka)."""
        r0 = self.L[gr["ref"]][gr["start"]][5]
        n0 = self.L[f][gr["at"][f]][5]
        s = n0[2] / r0[2]
        return s, n0[0] - s * r0[0], n0[1] - s * r0[1]

    def _pasuje(self, ref, j, m, f, at):
        """Czy wycinki ref[j:j+m] w klatce f (od pozycji at) przesuwają się razem jak pierwszy z nich."""
        R, N = self.L[ref], self.L[f]
        r0, n0 = R[j][5], N[at][5]
        s0 = n0[2] / r0[2]
        if abs(s0 - 1) > self.SMAX:
            return False
        t0x, t0y = n0[0] - s0 * r0[0], n0[1] - s0 * r0[1]
        for k in range(m):
            r, n = R[j + k][5], N[at + k][5]
            sk = n[2] / r[2]
            tkx, tky = n[0] - sk * r[0], n[1] - sk * r[1]
            x0, y0, x1, y1 = r[4]
            x0, y0, x1, y1 = max(x0, -60), max(y0, -60), min(x1, self.ow + 60), min(y1, self.oh + 60)
            for X in (x0, x1):
                if abs((sk - s0) * X + tkx - t0x) > self.TOL:
                    return False
            for Y in (y0, y1):
                if abs((sk - s0) * Y + tky - t0y) > self.TOL:
                    return False
            if abs(n[3] - s0 * r[3]) > self.TOLB:
                return False
            if abs(s0 - 1) > 1e-9 and min(r[3], n[3]) < self.BMIN:  # ostry plan nie zniesie drugiego próbkowania
                return False
        return True

    def _planuj(self):
        n = len(self.L)
        zajete = [dict() for _ in range(n)]  # klatka → {pozycja startu: (grupa, długość)}
        pokryte = [set() for _ in range(n)]
        for f in range(n):
            rows, ops, j = self.L[f], [], 0
            while j < len(rows):
                if j in zajete[f]:
                    gi, m = zajete[f][j]
                    ops.append(("g", gi))
                    j += m
                    continue
                best = None  # (zysk, m, klatki {f: pozycja})
                frames = list(range(f, n))
                m = 0
                while j + m < len(rows) and rows[j + m][4] is not None and (j + m) not in pokryte[f]:
                    m += 1
                    ok = {}
                    for f2 in frames:
                        at = self.pos[f2].get(rows[j][4])
                        if at is None or any(self.pos[f2].get(rows[j + k][4]) != at + k or (at + k) in pokryte[f2]
                                             for k in range(m)):
                            break
                        if f2 > f and not self._pasuje(f, j, m, f2, at):
                            break
                        ok[f2] = at
                    frames = list(ok)
                    if len(ok) < self.KMIN:
                        break
                    if best is None or m * len(ok) > best[0]:
                        best = (m * len(ok), m, ok)
                if best is None:
                    ops.append(("i", j))
                    j += 1
                    continue
                _, m, ok = best
                gi = len(self.grupy)
                gr = {"ref": f, "start": j, "m": m, "at": ok, "koniec": max(ok), "fazy": {}}
                self.grupy.append(gr)
                for f2, at in ok.items():
                    zajete[f2][at] = (gi, m)
                    pokryte[f2].update(range(at, at + m))
                ops.append(("g", gi))
                j += m
            self.plan.append(ops)
        for gr in self.grupy:  # obszar warstwy: to, co przez jej życie wjeżdża w kadr (w pikselach klatki odniesienia)
            bx0 = by0 = math.inf
            bx1 = by1 = -math.inf
            for f2 in gr["at"]:
                s, tx, ty = self._mapa(gr, f2)
                bx0, by0 = min(bx0, -tx / s), min(by0, -ty / s)
                bx1, by1 = max(bx1, (self.ow - tx) / s), max(by1, (self.oh - ty) / s)
            rows = self.L[gr["ref"]][gr["start"]:gr["start"] + gr["m"]]
            ux0, uy0 = min(r[5][4][0] for r in rows), min(r[5][4][1] for r in rows)
            ux1, uy1 = max(r[5][4][2] for r in rows), max(r[5][4][3] for r in rows)
            gr["obszar"] = (math.floor(max(bx0, ux0)) - 2, math.floor(max(by0, uy0)) - 2,
                            math.ceil(min(bx1, ux1)) + 2, math.ceil(min(by1, uy1)) + 2)

    # -- rysowanie --
    def _warstwa(self, gr, qx=0.0, qy=0.0):
        """Rysuje raz wycinki grupy (z cieniami i rozmyciem) do tablicy RGBa uint8 (alfa wymnożona) w klatce odniesienia,
        przesuniętej o (qx, qy) piksela — faza podpikselowa, żeby przy kopiowaniu nie próbkować obrazu drugi raz."""
        st = self.st[gr["ref"]]
        x0, y0, x1, y1 = gr["obszar"]
        lay = np.zeros((y1 - y0 + 1, x1 - x0 + 1, 4), np.float32)
        st._off, st.ow, st.oh = (x0 + qx, y0 + qy), x1 - x0 + 1, y1 - y0 + 1
        try:
            for kind, p, g, it, _, _ in self.L[gr["ref"]][gr["start"]:gr["start"] + gr["m"]]:
                st._rysuj(lay, kind, p, g, it)
        finally:
            st._off = (0.0, 0.0)
            st.ow, st.oh = self.ow, self.oh
        lay = (np.clip(lay, 0, 1) * 255 + 0.5).astype(np.uint8)
        lay[..., :3] = np.minimum(lay[..., :3], lay[..., 3:])  # premultiplied: barwa nie jaśniejsza niż krycie
        return lay

    def _faza(self, gr, qx, qy):
        fz = gr["fazy"]
        if (qx, qy) in fz:
            fz[(qx, qy)] = fz.pop((qx, qy))  # ostatnio używana na koniec
        else:
            if len(fz) >= self.FAZY_MAX:
                fz.pop(next(iter(fz)))
            fz[(qx, qy)] = self._warstwa(gr, qx, qy)
        return fz[(qx, qy)]

    @staticmethod
    def _over(reg, src):
        """reg (float, RGB) ← src (uint8 RGBa) nałożone „over”, z jak najmniejszą liczbą tablic pośrednich."""
        om = src[..., 3:].astype(np.float32)
        om *= -1 / 255.0
        om += 1.0
        reg *= om
        rgb = src[..., :3].astype(np.float32)
        rgb *= 1 / 255.0
        reg += rgb

    def _naloz(self, canvas, f, gr):
        s, tx, ty = self._mapa(gr, f)
        lx0, ly0, lx1, ly1 = gr["obszar"]
        if lx1 <= lx0 or ly1 <= ly0:
            return
        if abs(s - 1) < 1e-9:  # samo przesunięcie: warstwa we właściwej fazie, kopiowana co do piksela
            u, v = -tx - lx0, -ty - ly0  # położenie piksela (0, 0) klatki w warstwie
            qx, qy = (round((u - math.floor(u)) * self.FAZA) / self.FAZA, round((v - math.floor(v)) * self.FAZA) / self.FAZA)
            iu, iv = math.floor(u) + (1 if qx >= 1 else 0), math.floor(v) + (1 if qy >= 1 else 0)
            qx, qy = qx % 1.0, qy % 1.0
            lay = self._faza(gr, qx, qy)
            h, w = lay.shape[:2]
            cx0, cy0, cx1, cy1 = max(0, -iu), max(0, -iv), min(self.ow, w - iu), min(self.oh, h - iv)
            if cx1 > cx0 and cy1 > cy0:
                self._over(canvas[cy0:cy1, cx0:cx1], lay[cy0 + iv:cy1 + iv, cx0 + iu:cx1 + iu])
        else:  # najazd/odjazd: warstwa (tylko plany rozmyte) przeskalowana
            lay = self._faza(gr, 0.0, 0.0)
            h, w = lay.shape[:2]
            cx0, cy0 = max(0, math.floor(s * lx0 + tx)), max(0, math.floor(s * ly0 + ty))
            cx1, cy1 = min(self.ow, math.ceil(s * (lx0 + w) + tx)), min(self.oh, math.ceil(s * (ly0 + h) + ty))
            if cx1 > cx0 and cy1 > cy0:
                img = Image.frombuffer("RGBa", (w, h), lay.tobytes(), "raw", "RGBa", 0, 1)
                u0, v0 = (cx0 - tx) / s - lx0, (cy0 - ty) / s - ly0
                out = img.transform((cx1 - cx0, cy1 - cy0), Image.AFFINE, (1 / s, 0, u0, 0, 1 / s, v0), resample=Image.BILINEAR)
                self._over(canvas[cy0:cy1, cx0:cx1], np.asarray(out))
        if gr["koniec"] <= f:
            gr["fazy"] = {}  # warstwa już się nie przyda: pamięć wraca od razu

    def render(self, f, post=True):
        st = self.st[f]
        canvas = st._plotno()
        rows = self.L[f]
        for op, v in self.plan[f]:
            if op == "i":
                kind, p, g, it, _, _ = rows[v]
                st._rysuj(canvas, kind, p, g, it)
            else:
                self._naloz(canvas, f, self.grupy[v])
        return st._obraz(canvas, post)

    def opis(self):
        uzyte = sum(1 for ops in self.plan for op, _ in ops if op == "g")
        wycinki = sum(self.grupy[v]["m"] for ops in self.plan for op, v in ops if op == "g")
        wszystkie = sum(len(r) for r in self.L)
        return f"warstw {len(self.grupy)}, wycinków z warstw {wycinki}/{wszystkie} ({wycinki / max(1, wszystkie):.0%}), nałożeń {uzyte}"
