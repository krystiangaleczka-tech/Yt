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
    def render(self, post=True):
        self.ow, self.oh = int(round(W * Q)), int(round(H * Q))
        canvas = np.empty((self.oh, self.ow, 3), np.float32)
        canvas[:] = np.array(self.void if self.void else (0, 0, 0), np.float32) / 255.0
        for kind, p, z, _, it in sorted(self.items, key=lambda i: (i[1], i[2], i[3])):
            g = self.cam.mag(p)
            if g is None:
                continue
            if kind == "spr":
                self._sprite(canvas, p, g, **it)
            else:
                self._line(canvas, p, g, **it)
        if post:
            canvas = self._post(canvas)
        return Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8))

    def _sprite(self, canvas, p, g, spr, x, y, k, anchor, rot, sx, sy, alpha, shadow, blur, tint, haze, mode):
        W, H = self.ow, self.oh  # rozmiar klatki wyjściowej (szkic albo pełna)
        S = self.cam.screen(x, y, p)
        S = (S[0] * Q, S[1] * Q)
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
        out = mip.transform((x1 - x0, y1 - y0), Image.AFFINE, coef, resample=Image.BILINEAR)  # mipmapa jest już bliska skali: dwuliniowe wystarcza, 2× szybciej
        if blur:
            out = out.filter(ImageFilter.GaussianBlur(blur))
        # widoczna część obszaru
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        if shadow and mode == "over":
            a_img = out.getchannel("A")
            q = 4 if min(a_img.size) > 48 else 1
            small = a_img.reduce(q) if q > 1 else a_img
            small = small.filter(ImageFilter.GaussianBlur(soft / q))
            sh = np.asarray(small.resize(a_img.size, Image.BILINEAR), np.float32) * (strength * alpha / 255.0)
            ox, oy = int(round(sdx)), int(round(sdy))
            # cień przesunięty o (ox, oy): piksel ekranu (X, Y) bierze cień z (X - ox, Y - oy)
            tx0, ty0, tx1, ty1 = max(0, x0 + ox), max(0, y0 + oy), min(W, x1 + ox), min(H, y1 + oy)
            if tx1 > tx0 and ty1 > ty0:
                part = sh[ty0 - oy - y0:ty1 - oy - y0, tx0 - ox - x0:tx1 - ox - x0, None]
                reg = canvas[ty0:ty1, tx0:tx1]
                reg += (SHADOW - reg) * part
        src = np.asarray(out.crop((cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0)), np.float32) * (1 / 255.0)
        rgb, a = src[..., :3], src[..., 3:]
        if tint is not None:
            rgb = rgb * np.asarray(tint, np.float32)
        if haze:
            rgb = rgb + (HAZE * a - rgb) * haze
        if alpha < 1:
            rgb, a = rgb * alpha, a * alpha
        reg = canvas[cy0:cy1, cx0:cx1]
        if mode == "add":
            reg += rgb
        elif mode == "mul":  # wycinek jako filtr: ciemnieje tam, gdzie jest
            reg *= 1 - a + rgb
        else:
            reg *= 1 - a
            reg += rgb

    def _line(self, canvas, p, g, pts, width, color, alpha):
        W, H = self.ow, self.oh
        q = [(a * Q, b * Q) for a, b in (self.cam.screen(x, y, p) for x, y in pts)]
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
        reg += (np.array(color, np.float32) / 255.0 - reg) * a

    def _post(self, arr):
        W, H = self.ow, self.oh
        CX, CY = W / 2, H / 2
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        if self.spot:
            sx, sy, sp, r, dark = self.spot
            px, py = (v * Q for v in self.cam.screen(sx, sy, sp))
            r = r * self.cam.mag(sp) * Q
            d = np.sqrt((xx - px) ** 2 + ((yy - py) * 1.15) ** 2) / r
            arr = arr * (1 - dark * np.clip(d - 0.35, 0, 1) ** 1.3)[..., None]
        # ciepłe światło z góry z lewej + winieta
        key = 1.05 - 0.13 * (xx / W) - 0.10 * (yy / H)
        vig = 1 - 0.34 * (((xx - CX) / CX) ** 2 + ((yy - CY) / CY) ** 2) ** 1.25
        arr = arr * (key * np.clip(vig, 0.3, 1))[..., None]
        arr = arr * (np.array(self.grade, np.float32) * self.dim)
        # lekki kontrast i ziarno zmieniane co 3 klatki (jak kreska w pozostałych filmach)
        arr = np.clip(arr, 0, 1)
        arr = arr + 0.10 * (arr * arr * (3 - 2 * arr) - arr)
        rng = np.random.default_rng(int(self.t * FPS) // 3 + 101 + self.seed)
        arr = arr + rng.normal(0, 0.011, (H, W, 1)).astype(np.float32)
        return arr
