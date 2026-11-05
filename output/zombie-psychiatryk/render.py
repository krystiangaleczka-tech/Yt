"""15 s: zombie w szpitalu psychiatrycznym — płaska animacja 2D z odręczną kreską.

Uruchom: python3 render.py   (wynik: zombie-psychiatryk.mp4 obok skryptu)
"""
import math
import os
import random
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
W, H, SS, FPS, DUR = 1280, 720, 2, 24, 27.5
INK = (22, 20, 20)
_FONTS = [("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
          ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
          ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]
FONT, FONT_B = next((f for f in _FONTS if Path(f[0]).exists()), _FONTS[0])
# FILM_LANG=en → lektor z voice/en/, angielskie napisy i tabliczki, pliki z sufiksem -en
LANG = os.environ.get("FILM_LANG", "pl")
VOICE_DIR = HERE / "voice" if LANG == "pl" else HERE / "voice" / LANG
SUFFIX = "" if LANG == "pl" else f"-{LANG}"
EN = {
    "l1.wav": "At the asylum on Forest Road,\nsomeone was always screaming.",
    "l2.wav": "But that night,\nall of Ward C went silent.",
    "l3.wav": "Mr. Henry stood at the isolation window.\nHe didn't blink.",
    "l4.wav": "That's when I realized\nthe doors behind me were open.",
    "l5.wav": "All of them.",
    "p2_l1.wav": "I ran for the nurses' station\nat the end of the hall.",
    "p2_l2.wav": "I locked the door\nand turned off the light.",
    "p2_l3.wav": "Through the glass,\nI watched them shuffle past.",
    "p2_l4.wav": "Then the phone rang.",
    "p2_l5.wav": "And every head\nturned at once.",
}


def localize(scenes):
    return scenes if LANG == "pl" else [(a, b, fn, vs, EN[fn]) for a, b, fn, vs, _ in scenes]

# (start, koniec, plik lektora, start lektora, napis) — ujęcia mają oddech: pauzę przed i po kwestii
SCENES = [
    (0.0, 7.0, "l1.wav", 1.00, "W szpitalu przy Leśnej\nzawsze ktoś krzyczał."),
    (7.0, 12.0, "l2.wav", 7.90, "Ale tej nocy\ncały oddział C ucichł."),
    (12.0, 17.6, "l3.wav", 13.20, "W okienku izolatki stał pan Henryk.\nNie mrugał."),
    (17.6, 23.4, "l4.wav", 19.50, "Wtedy zrozumiałem,\nże drzwi za mną są otwarte."),
    (23.4, 27.5, "l5.wav", 25.40, "Wszystkie."),
]
SCENES = localize(SCENES)
SLAM_T = SCENES[2][0] + 2.9  # twarz uderza w szybę izolatki
WALK_STOP = (1.8, 3.4)  # pielęgniarz staje w korytarzu i się rozgląda
FACE_PUSH = 2.9 + 1.5  # w scenie 3: szybki najazd +25% na twarz pana Henryka
WINDOW = (285 + 8 * 72, 320 + 72)  # okno, w którym ktoś stoi (kolumna 8, rząd 1)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def noise(t, seed, speed=1.0):
    """Gładki szum -1..1: losowe wartości co 1/speed s, płynnie łączone — ruch „z ręki”, nie z sinusa."""
    x = t * speed
    i = math.floor(x)
    f = x - i
    a = random.Random(seed * 7919 + i).uniform(-1, 1)
    b = random.Random(seed * 7919 + i + 1).uniform(-1, 1)
    return a + (b - a) * f * f * (3 - 2 * f)


def blink(t, seed, every=3.0):
    """0 — oko otwarte, 1 — zamknięte. Mrugnięcia w nieregularnych odstępach."""
    k = math.floor(t / every)
    for kk in (k - 1, k):
        d = t - (kk * every + random.Random(seed * 31 + kk).uniform(0.2, every - 0.3))
        if 0 <= d < 0.16:
            return 1 - abs(d - 0.08) / 0.08
    return 0.0


def voice_len(fn):
    try:
        with wave.open(str(VOICE_DIR / fn)) as w:
            return w.getnframes() / w.getframerate()
    except FileNotFoundError:
        return 2.0


class Pen:
    """Rysuje w układzie 1280x720 przez kamerę; kreska lekko „gotuje się” 8 razy na sekundę."""

    def __init__(self, img, t, zoom=1.0, cx=640, cy=360, shake=(0, 0)):
        self.img, self.d = img, ImageDraw.Draw(img)
        self.boil = int(t * 8)
        self.zoom, self.cx, self.cy, self.shake = zoom, cx, cy, shake

    def tp(self, p):
        x = ((p[0] - self.cx) * self.zoom + W / 2 + self.shake[0]) * SS
        y = ((p[1] - self.cy) * self.zoom + H / 2 + self.shake[1]) * SS
        return (x, y)

    def wob(self, pts, amp=1.6, closed=False):
        if closed:
            pts = list(pts) + [pts[0]]
        rnd = random.Random(hash((self.boil, round(pts[0][0]), round(pts[0][1]), len(pts))))
        out = []
        for a, b in zip(pts, pts[1:]):
            n = max(1, int(math.dist(a, b) / 45))
            for i in range(n):
                f = i / n
                out.append((a[0] + (b[0] - a[0]) * f + rnd.uniform(-amp, amp),
                            a[1] + (b[1] - a[1]) * f + rnd.uniform(-amp, amp)))
        out.append(out[0] if closed else pts[-1])
        return out

    def line(self, pts, w=4, color=INK, amp=1.6):
        q = [self.tp(p) for p in self.wob(pts, amp)]
        self.d.line(q, fill=color, width=max(1, int(w * self.zoom * SS)), joint="curve")

    def poly(self, pts, fill, w=4, color=INK, amp=1.6):
        q = [self.tp(p) for p in self.wob(pts, amp, closed=True)]
        if fill is not None:
            self.d.polygon(q, fill=fill)
        if w:
            self.d.line(q, fill=color, width=max(1, int(w * self.zoom * SS)), joint="curve")

    def rect(self, x0, y0, x1, y1, fill, w=4, **k):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, w, **k)

    def ell(self, cx, cy, rx, ry, fill, w=4, n=26, rot=0.0, **k):
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = rx * math.cos(a), ry * math.sin(a)
            pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
        self.poly(pts, fill, w, **k)

    def glow(self, pts, rgba):
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon([self.tp(p) for p in pts], fill=rgba)
        self.img.alpha_composite(layer)

    def text(self, x, y, s, size, fill=INK):
        f = ImageFont.truetype(FONT_B, int(size * self.zoom * SS))
        self.d.text(self.tp((x, y)), s, font=f, fill=fill, anchor="mm")


# ---------- postacie ----------

def zombie(p, x, y, s, t, seed, gown=(168, 178, 172), tilt=0.0, arms=0.0, legs=True):
    """Pacjent-zombie w koszuli szpitalnej, ręce do przodu, kołysze się. tilt — głowa przekrzywiona na stałe;
    arms 0..1 — ręce unoszą się nad głowę; legs=False — nogi rysuje kto inny (schody: kit_a.st_person)."""
    sway = math.sin(t * 3.1 + seed) * 6 * s
    lean = math.sin(t * 3.1 + seed) * 0.08 + tilt
    skin = (139, 156, 128)
    # nogi
    step = math.sin(t * 6.2 + seed) * 10 * s
    if legs:
        p.poly([(x - 22 * s, y - 70 * s), (x - 6 * s, y - 70 * s), (x - 8 * s + step, y), (x - 26 * s + step, y)], skin)
        p.poly([(x + 6 * s, y - 70 * s), (x + 22 * s, y - 70 * s), (x + 26 * s - step, y), (x + 8 * s - step, y)], skin)
    # koszula
    hx = x + sway
    p.poly([(hx - 42 * s, y - 190 * s), (hx + 42 * s, y - 190 * s), (x + 50 * s, y - 62 * s), (x - 50 * s, y - 62 * s)], gown)
    p.line([(x - 10 * s, y - 120 * s), (x - 18 * s, y - 70 * s)], w=2.5)
    # ręce wyciągnięte w stronę kamery (skrót perspektywy); arms → uniesione nad głowę
    for side in (-1, 1):
        ax = hx + side * 40 * s
        ex, ey = ax + side * (18 + 20 * arms) * s, y - (128 + 182 * arms) * s
        p.poly([(ax - 10 * s, y - 182 * s), (ax + 10 * s, y - 182 * s), (ex + 12 * s, ey + 8 * s * (1 - arms)),
                (ex - 12 * s, ey + 8 * s * (1 - arms))], gown)
        p.ell(ex, ey + 8 * s * (1 - arms), 15 * s, 13 * s, skin)
    # głowa
    gx, gy = hx + lean * 60 * s, y - 228 * s
    p.ell(gx, gy, 36 * s, 42 * s, skin)
    p.line([(gx - 30 * s, gy - 22 * s), (gx - 12 * s, gy - 40 * s), (gx + 4 * s, gy - 30 * s), (gx + 24 * s, gy - 38 * s)], w=3)
    for side in (-1, 1):
        p.ell(gx + side * 14 * s, gy - 4 * s, 8 * s, 9 * s, (236, 238, 226), w=3)
    p.ell(gx, gy + 20 * s, 9 * s, 11 * s, (40, 22, 22), w=3)


def nurse_back(p, x, y, s, t, head=0.0, breath=0.0):
    """t — zegar chodu (stoi w miejscu, gdy nie rośnie); head -1..1 — obrót głowy; breath — oddech."""
    bob = abs(math.sin(t * 5.0)) * 5 * s + breath * 2 * s
    y -= bob
    leg = (118, 148, 160)
    step = math.sin(t * 5.0) * 8 * s
    p.poly([(x - 26 * s, y - 80 * s), (x - 6 * s, y - 80 * s), (x - 8 * s, y - 10 * s + step), (x - 24 * s, y - 10 * s + step)], leg)
    p.poly([(x + 6 * s, y - 80 * s), (x + 26 * s, y - 80 * s), (x + 24 * s, y - 10 * s - step), (x + 8 * s, y - 10 * s - step)], leg)
    p.ell(x - 16 * s, y - 6 * s + step, 14 * s, 8 * s, (240, 240, 236), w=3)
    p.ell(x + 16 * s, y - 6 * s - step, 14 * s, 8 * s, (240, 240, 236), w=3)
    uni = (150, 180, 190)
    p.poly([(x - 52 * s, y - 232 * s), (x + 52 * s, y - 232 * s), (x + 54 * s, y - 74 * s), (x - 54 * s, y - 74 * s)], uni)
    p.poly([(x - 52 * s, y - 228 * s), (x - 68 * s, y - 150 * s), (x - 52 * s, y - 145 * s), (x - 40 * s, y - 200 * s)], uni)
    p.poly([(x + 52 * s, y - 228 * s), (x + 76 * s, y - 175 * s), (x + 64 * s, y - 165 * s), (x + 40 * s, y - 200 * s)], uni)
    p.poly([(x - 14 * s, y - 236 * s), (x + 14 * s, y - 236 * s), (x + 12 * s, y - 252 * s), (x - 12 * s, y - 252 * s)], (226, 192, 166), w=3)
    hx = x + head * 10 * s
    # przy obrocie widać policzek i nos z jednej strony
    for side in (-1, 1):
        p.ell(hx + side * 37 * s - head * 6 * s, y - 274 * s, 7 * s, 11 * s, (226, 192, 166), w=3)
    if abs(head) > 0.25:
        sd = 1 if head > 0 else -1
        p.ell(hx + sd * 30 * s, y - 268 * s, 10 * s * abs(head), 20 * s, (226, 192, 166), w=3)
        p.poly([(hx + sd * 38 * s, y - 276 * s), (hx + sd * (38 + 12 * abs(head)) * s, y - 266 * s),
                (hx + sd * 38 * s, y - 262 * s)], (226, 192, 166), w=2.5)
    p.ell(hx, y - 280 * s, 36 * s, 38 * s, (58, 46, 38))
    p.line([(hx - 22 * s, y - 250 * s), (hx + 22 * s, y - 250 * s)], w=2.5, color=(40, 32, 26))


def nurse_face(p, x, y, s, fear, t, gaze=(0.0, 0.0), blink_k=0.0, swallow=0.0, breath=0.0, body=None):
    """gaze -1..1 — gdzie patrzą źrenice; blink_k — zamknięcie powiek; swallow — przełknięcie śliny;
    breath — oddech unosi ramiona; body — (x, y) tułowia, gdy głowa porusza się osobno."""
    skin = (232, 200, 174)
    bx, by = body or (x, y)
    by -= breath * 5 * s
    p.poly([(bx - 120 * s, by + 150 * s), (bx + 120 * s, by + 150 * s), (bx + 150 * s, by + 400 * s + breath * 5 * s),
            (bx - 150 * s, by + 400 * s + breath * 5 * s)], (150, 180, 190))
    p.poly([(x - 30 * s, y + 90 * s), (x + 30 * s, y + 90 * s), (bx + 34 * s, by + 160 * s), (bx - 34 * s, by + 160 * s)], skin)
    if swallow > 0:
        p.line([(x - 8 * s, y + 140 * s - swallow * 22 * s), (x + 8 * s, y + 138 * s - swallow * 22 * s)], w=3)
    p.poly([(bx - 40 * s, by + 150 * s), (bx, by + 200 * s), (bx + 40 * s, by + 150 * s)], (244, 244, 240), w=3)
    hair = (58, 46, 38)
    for side in (-1, 1):
        p.ell(x + side * 122 * s, y + 14 * s, 18 * s, 30 * s, skin)
    p.ell(x, y + 6 * s, 120 * s, 132 * s, skin, n=34)
    p.poly([(x - 126 * s, y - 10 * s), (x - 120 * s, y - 100 * s), (x - 60 * s, y - 150 * s), (x + 40 * s, y - 156 * s),
            (x + 112 * s, y - 120 * s), (x + 126 * s, y - 20 * s), (x + 100 * s, y - 70 * s), (x + 20 * s, y - 92 * s),
            (x - 70 * s, y - 80 * s)], hair)
    for i in range(9):  # zarost
        a = math.pi * (0.15 + 0.7 * i / 8)
        p.line([(x + math.cos(a) * 92 * s, y + 40 * s + math.sin(a) * 80 * s),
                (x + math.cos(a) * 96 * s, y + 44 * s + math.sin(a) * 82 * s)], w=3, color=(120, 100, 88))
    # oczy: od zmęczonych, przymkniętych do szeroko otwartych; źrenice błądzą
    open_ = (0.4 + 0.6 * ease(fear)) * (1 - blink_k)
    for side in (-1, 1):
        ex, ey = x + side * 46 * s, y + 6 * s
        r = 14 + 8 * ease(fear)
        ry = (r + 3) * open_
        if ry < 3:
            p.line([(ex - r * s, ey), (ex + r * s, ey)], w=4)
        else:
            p.ell(ex, ey, r * s, ry * s, (246, 246, 240), w=3.5)
            pr = min(5.5, ry * 0.7)
            p.ell(ex + gaze[0] * (r - 6) * s, ey + gaze[1] * ry * 0.35 * s, pr * s, pr * s, INK, w=0)
            if open_ < 0.75:  # ciężka powieka
                p.line([(ex - r * s, ey - ry * 0.4 * s), (ex, ey - ry * s - 3 * s), (ex + r * s, ey - ry * 0.4 * s)], w=4)
        bl = 16 + 18 * ease(fear)
        p.line([(ex - 22 * s, ey - bl * s - side * 4 * s * fear), (ex + 20 * s, ey - bl * s + side * 6 * s * fear)], w=4)
    p.line([(x - 4 * s, y + 30 * s), (x - 10 * s, y + 52 * s), (x + 2 * s, y + 54 * s)], w=3)
    if fear < 0.3:
        p.line([(x - 18 * s, y + 82 * s), (x + 18 * s, y + 82 * s)], w=4)
    else:
        p.ell(x, y + 84 * s, (8 + 6 * fear) * s, (8 + 12 * fear) * s, (70, 30, 30), w=3.5)
        dy = (t * 40) % 40
        p.poly([(x + 104 * s, y - 40 * s + dy), (x + 112 * s, y - 20 * s + dy), (x + 104 * s, y - 12 * s + dy), (x + 96 * s, y - 20 * s + dy)],
               (190, 220, 235), w=2.5)


# ---------- tła ----------

def corridor(p, t, flicker, vp=(640, 330), doors_open=0.0):
    """doors_open — jedna wartość dla wszystkich drzwi albo {(k, strona): wartość}; pozostałe zamknięte."""
    vx, vy = vp
    bx0, by0, bx1, by1 = vx - 120, vy - 80, vx + 120, vy + 80
    p.rect(0, 0, W, H, (110, 122, 104), w=0)
    p.poly([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], (168, 172, 156))
    p.poly([(0, H), (W, H), (bx1, by1), (bx0, by1)], (92, 104, 92))
    p.poly([(0, 0), (bx0, by0), (bx0, by1), (0, H)], (150, 166, 140))
    p.poly([(W, 0), (bx1, by0), (bx1, by1), (W, H)], (150, 166, 140))
    # dolny ciemniejszy pas ścian (lamperia)
    for sgn, edge in ((-1, 0), (1, W)):
        bx = bx0 if sgn < 0 else bx1
        p.poly([(edge, 430), (bx, vy + 20), (bx, by1), (edge, H)], (104, 124, 100))
    p.rect(bx0, by0, bx1, by1, (130, 144, 122))
    p.rect(vx - 30, vy - 40, vx + 30, by1, (70, 78, 70), w=3)
    # płytki na podłodze
    for i in range(1, 8):
        f = (i / 8) ** 1.8
        yy = by1 + (H - by1) * f
        xl = bx0 + (0 - bx0) * f
        xr = bx1 + (W - bx1) * f
        p.line([(xl, yy), (xr, yy)], w=2, color=(60, 70, 62))
    for i in range(-5, 6):
        p.line([(vx + i * 24, by1), (vx + i * 260, H)], w=2, color=(60, 70, 62))
    # drzwi sal po bokach
    for k, f in enumerate((0.28, 0.55, 0.78)):
        for side in (-1, 1):
            edge = 0 if side < 0 else W
            bx = bx0 if side < 0 else bx1

            def at(ff, yy_top, yy_bot):
                xx = edge + (bx - edge) * ff
                top = 0 + (by0 - 0) * ff
                bot = H + (by1 - H) * ff
                return xx, top + (bot - top) * yy_top, top + (bot - top) * yy_bot

            xa, ta, ba = at(f, 0.30, 0.88)
            xb, tb, bb = at(f + 0.12, 0.30, 0.88)
            p.poly([(xa, ta), (xb, tb), (xb, bb), (xa, ba)], (60, 66, 60))
            op = doors_open.get((k, side), 0.0) if isinstance(doors_open, dict) else doors_open
            xo = xa + (xb - xa) * (1 - op)
            p.poly([(xa, ta), (xo, tb + (ta - tb) * op * 0.6), (xo, bb + (ba - bb) * op * 0.6), (xa, ba)], (124, 138, 122))
            xm, tm, _ = at(f + 0.04, 0.38, 0)
            if op < 0.2:
                p.rect(xm - 8 * (1 - f) - 2, tm, xm + 8 * (1 - f) + 2, tm + 30 * (1 - f) + 6, (28, 32, 30), w=2)
    # świetlówki
    for k, f in enumerate((0.2, 0.45, 0.68, 0.85)):
        yy = by0 * (f ** 1.4)
        half = 30 + 90 * (1 - f)
        th = 4 + 14 * (1 - f)
        on = flicker[k] if isinstance(flicker, (list, tuple)) else flicker
        col = (236, 240, 214) if on > 0.5 else (90, 96, 88)
        p.rect(vx - half, yy, vx + half, yy + th, col, w=3)


def light_mask(arr, cx, cy, r, ambient):
    yy, xx = np.ogrid[:H, :W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    m = ambient + (1 - ambient) * np.clip(1 - d, 0, 1) ** 0.7
    return arr * m[..., None]


# ---------- sceny ----------

def scene1(p, t, T):
    p.rect(0, 0, W, H, (44, 58, 56), w=0)
    p.ell(1020, 130, 52, 52, (214, 216, 190), w=3)
    for cx, cy, rx in ((300, 120, 220), (760, 80, 260), (1100, 190, 200), (150, 250, 160)):
        x = cx + t * 12
        p.ell(x, cy, rx, 42, (62, 78, 72), w=3)
        p.line([(x - rx * 0.7, cy + 10), (x - rx * 0.2, cy - 8), (x + rx * 0.5, cy + 6)], w=2.5)
    p.poly([(0, 560), (300, 540), (700, 550), (1280, 530), (1280, 720), (0, 720)], (40, 58, 44))
    # budynek
    p.rect(250, 280, 1030, 560, (132, 128, 112))
    p.poly([(230, 290), (640, 200), (1050, 290)], (62, 66, 70))
    p.rect(560, 150, 720, 300, (124, 120, 104))
    p.poly([(545, 160), (640, 90), (735, 160)], (62, 66, 70))
    p.ell(640, 215, 32, 32, (214, 210, 186), w=3)
    p.line([(640, 215), (640, 193)], w=3)
    p.line([(640, 215), (655, 222)], w=3)
    red_window = (8, 1)
    for row in range(3):
        for col in range(10):
            x0 = 285 + col * 72
            y0 = 320 + row * 72
            if 4 <= col <= 5 and row == 2:
                continue
            fill = (30, 36, 38)
            if (col, row) == red_window:
                fl = 0.5 + 0.5 * math.sin(t * 23) * math.sin(t * 7.3)
                fill = (int(150 + 90 * fl), int(40 + 30 * fl), 30)
            p.rect(x0, y0, x0 + 40, y0 + 46, fill, w=3)
            if (col, row) == red_window and 3.0 < t < 6.1:
                # gdy kamera jest już blisko: ktoś podchodzi do okna, staje, przekrzywia głowę — i nagle odskakuje
                sx = x0 - 10 + 30 * ease((t - 3.0) / 0.9) + 34 * ease((t - 5.9) / 0.15)
                tilt = 3 * ease((t - 4.2) / 0.6)
                p.ell(sx + tilt, y0 + 18, 8, 9, INK, w=0)
                p.rect(sx - 9, y0 + 26, sx + 9, y0 + 46, INK, w=0)
                # sylwetka tylko w szybie: ściana wokół okna zasłania resztę
                for mx0, my0, mx1, my1 in ((x0 - 24, y0 - 4, x0, y0 + 54), (x0 + 40, y0 - 4, x0 + 66, y0 + 54),
                                           (x0, y0 + 46, x0 + 40, y0 + 54)):
                    p.rect(mx0, my0, mx1, my1, (132, 128, 112), w=0, amp=0)
                p.rect(x0, y0, x0 + 40, y0 + 46, None, w=3)
            for k in range(1, 4):
                p.line([(x0 + k * 10, y0), (x0 + k * 10, y0 + 46)], w=2)
    p.rect(600, 470, 680, 560, (64, 52, 44))
    p.line([(640, 470), (640, 560)], w=3)
    p.poly([(580, 560), (700, 560), (720, 590), (560, 590)], (110, 108, 98))
    # drzewa
    for bx, dirn in ((120, 1), (1180, -1)):
        p.poly([(bx - 14, 600), (bx + 14, 600), (bx + 8, 320), (bx - 6, 320)], (30, 30, 28))
        for k in range(5):
            yy = 340 + k * 50
            sw = 7 * noise(t, bx + k, 0.9) + 4 * noise(t, bx + k + 50, 2.3)  # wiatr, nierówne podmuchy
            p.line([(bx, yy), (bx + dirn * (120 - k * 15), yy - 70 + sw * 0.5),
                    (bx + dirn * (150 - k * 15) + sw, yy - 110 + sw)], w=5)
    # brama i płot
    p.line([(0, 600), (W, 600)], w=7)
    p.line([(0, 640), (W, 640)], w=5)
    for x in range(10, W, 46):
        if 560 < x < 720:
            continue
        p.line([(x, 720), (x, 560)], w=6)
        p.poly([(x - 8, 566), (x, 545), (x + 8, 566)], INK, w=2)
    gate = ease((t - 0.8) / 3.0) * 30 - 6 * ease((t - 3.9) / 0.8) + 2 * noise(t, 9, 1.2)
    for side in (-1, 1):
        gx = 640 + side * (80 - gate * 0.0)
        for k in range(4):
            x = 640 + side * (14 + k * 20 + gate * (k + 1) / 4)
            p.line([(x, 720), (x, 520)], w=6)
    p.rect(588, 505, 692, 535, (150, 150, 138), w=3)
    p.text(640, 520, "OD. C" if LANG == "pl" else "WARD C", 18)


def walk_clock(t):
    """Sekundy faktycznego chodu: idzie, staje i się rozgląda, rusza wolniej."""
    a, b = WALK_STOP
    return min(t, a) + max(0.0, t - b) * 0.75


def scene2(p, t, T):
    a, b = WALK_STOP
    fl = [1, 1, 1 if (math.sin(t * 31) > -0.2 or t < 1.0) else 0, 1]
    if t > 3.8:
        fl = [0, 1, 0, 1 if math.sin(t * 40) > 0 else 0]
    corridor(p, t, fl)
    wt, span = walk_clock(t), walk_clock(T)
    s = 1.05 - 0.15 * wt / span
    x, y = 430 + 40 * wt / span, 640 - 30 * wt / span
    # rozgląda się: latarka w lewo, potem w prawo, z powrotem na wprost; ręka nie jest idealnie nieruchoma
    look = -ease((t - a - 0.1) / 0.4) + 1.6 * ease((t - a - 0.7) / 0.5) - 0.6 * ease((t - b + 0.2) / 0.4)
    look += 0.06 * noise(t, 17, 2.0)
    stopped = ease((t - a) / 0.3) * (1 - ease((t - b) / 0.3))
    nurse_back(p, x, y, s, wt, head=look * 0.9, breath=stopped * math.sin(t * 2 * math.pi * 0.45))
    hx, hy = x + 66 * s, y - 170 * s
    sx = 260 * look
    p.glow([(hx, hy), (560 + sx, 300), (760 + sx, 300), (740 + sx, 420), (620 + sx, 430)], (255, 240, 170, 55))
    p.ell(hx, hy, 9 * s, 9 * s, (60, 60, 60), w=3)


def scene3(p, t, T):
    sl = SLAM_T - SCENES[2][0]
    slam = t >= sl
    p.rect(0, 0, W, H, (88, 96, 86), w=0)
    p.rect(330, -20, 950, 760, (112, 126, 112))
    p.line([(340, 0), (340, 720)], w=3)
    for k in range(6):
        y = 90 + k * 110
        p.line([(380 + (k * 37) % 60, y), (430 + (k * 53) % 70, y + 26)], w=2, color=(70, 80, 70))
    # okienko z siatką
    p.rect(500, 140, 780, 340, (16, 20, 20), w=6)
    if not slam and 1.5 < t < 2.4:
        # coś w ciemności: dwa bliki oczu, przez moment, jakby się przesunęło
        a = ease((t - 1.5) / 0.2) * (1 - ease((t - 2.2) / 0.2))
        ex = 610 + 30 * noise(t, 7, 1.3)
        for dx in (0, 26):
            p.ell(ex + dx, 236, 3.5 * a, 2.5 * a, (150, 160, 140), w=0)
    if slam:
        k = t - sl
        sc = 1.0 + 0.15 * max(0, 1 - k * 8)
        # po uderzeniu głowa powoli przekrzywia się na bok, oczy się nie ruszają
        lean = ease((k - 0.8) / 2.2)
        gx, gy = 640 + 12 * lean + 2 * noise(k, 8, 0.7), 268 + 8 * lean
        skin = (154, 170, 140)
        p.ell(gx, gy, 92 * sc, 112 * sc, skin, w=5, rot=0.12 * lean)
        p.line([(gx - 80, gy - 70), (gx - 30, gy - 100), (gx + 10, gy - 80), (gx + 60, gy - 104), (gx + 84, gy - 60)], w=4)
        for side in (-1, 1):
            p.ell(gx + side * 36, gy - 14 + side * 4 * lean, 22, 24, (238, 240, 228), w=4)
            p.ell(gx + side * 36, gy - 12 + side * 4 * lean, 5, 5, INK, w=0)
        p.ell(gx, gy + 54, 22, 30 - 6 * lean, (36, 18, 18), w=4)
        # dłoń zsuwa się po szybie
        fy = 18 * ease((k - 0.6) / 2.5)
        p.ell(gx + 120, 200 + fy, 40, 46, skin, w=4)
        for i in range(4):
            p.line([(gx + 96 + i * 14, 168 + fy), (gx + 98 + i * 15, 140 + fy)], w=8, color=skin)
            p.line([(gx + 96 + i * 14, 168 + fy), (gx + 98 + i * 15, 140 + fy)], w=2)
        drip = min(k * 120, 160)
        p.poly([(gx + 100, 210), (gx + 140, 220), (gx + 136, 230 + drip), (gx + 108, 222 + drip * 0.7)], (120, 22, 22), w=0)
        # oddech paruje na szybie — jedyny dowód, że żyje
        fog = max(0.0, math.sin(2 * math.pi * 0.35 * (k - 0.6))) * ease((k - 0.6) / 0.3)
        if fog > 0.02:
            pts = [(gx + 46 * math.cos(a), gy + 82 + 22 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24)]
            p.glow(pts, (225, 232, 225, int(70 * fog)))
    for i in range(-6, 12):
        p.line([(500 + i * 40, 140), (500 + i * 40 + 200, 340)], w=1.5, color=(80, 90, 84), amp=0.6)
        p.line([(500 + i * 40 + 200, 140), (500 + i * 40, 340)], w=1.5, color=(80, 90, 84), amp=0.6)
    p.rect(470, 341, 810, 520, (112, 126, 112), w=0, amp=0)  # żuchwa nie wychodzi pod okienko
    p.rect(470, 120, 810, 360, None, w=8)
    p.rect(470, 120, 500, 360, (112, 126, 112), w=0)
    p.rect(780, 120, 810, 360, (112, 126, 112), w=0)
    p.rect(0, 120, 330, 360, (88, 96, 86), w=0)
    p.rect(950, 120, W, 360, (88, 96, 86), w=0)
    p.rect(498, 138, 782, 342, None, w=6)
    p.rect(560, 400, 720, 450, (196, 196, 180), w=3)
    p.text(640, 425, "IZOLATKA 3" if LANG == "pl" else "ISOLATION 3", 22)
    p.rect(860, 440, 900, 560, (60, 62, 58))
    p.rect(820, 480, 900, 500, (60, 62, 58))


CREAK = 1.2  # w scenie 4: skrzypnięcie drzwi za plecami


def scene4(p, t, T):
    fear = ease((t - 2.7) / 1.0)
    # otwierają się tylko najdalsze drzwi po prawej; bliższe zostają zamknięte
    corridor(p, t, [1, 0, 1, 0], vp=(250, 300), doors_open={(2, 1): ease((t - CREAK) / 2.6) * 0.8})
    if t > 2.9:
        # z otwartych drzwi wychodzi jeden pacjent — z progu w głąb korytarza, w stronę kamery
        out = ease((t - 2.9) / 2.6)
        zombie(p, 505 - 80 * out, 404 + 70 * out, 0.5 + 0.18 * out, t, 2.1, gown=(150, 160, 152), tilt=0.15)
    # wzrok: znudzony błądzi w dół → skrzypnięcie, oczy w lewo → zastyga, myśli → znów w lewo, już w panice
    lazy = (0.3 * noise(t, 11, 0.8), 0.35 + 0.25 * noise(t, 12, 0.6))
    k1, k2, k3 = ease((t - CREAK - 0.25) / 0.18), ease((t - 2.5) / 0.6), ease((t - 3.45) / 0.15)
    gx = lazy[0] + (-1.0 - lazy[0]) * k1
    gx += (-0.1 - gx) * k2
    gx += (-1.0 - gx) * k3
    gy = lazy[1] * (1 - k1) + 0.05 * noise(t, 14, 5)
    gx += 0.05 * noise(t, 13, 6)  # mikrosakkady
    # mruga, póki się nie boi; w chwili namysłu jedno powolne mrugnięcie
    bk = blink(t, 5, 2.4) if fear < 0.4 else 0.0
    if 2.45 < t < 2.85:
        bk = max(bk, 1 - abs(t - 2.65) / 0.2)
    swallow = max(0.0, 1 - abs(t - 2.2) / 0.18)
    # oddech: wstrzymany, kiedy nasłuchuje; potem coraz szybszy
    held = ease((t - CREAK - 0.2) / 0.2) * (1 - ease((t - 2.4) / 0.3))
    breath = math.sin(2 * math.pi * (0.3 * t + 0.6 * max(0.0, t - 2.7))) * (1 - held) * (1 + fear)
    hx = 820 + 6 * noise(t, 3, 0.6) - 14 * k1 * (1 - k2) - 22 * k3
    hy = 360 + 4 * noise(t, 4, 0.5)
    nurse_face(p, hx, hy, 1.0, fear, t, gaze=(gx, gy), blink_k=bk, swallow=swallow, breath=breath, body=(820, 360))


ZOMBIE_START = (0.0, 0.45, 0.2, 0.9, 0.6, 0.1)  # nierówno — każdy rusza kiedy indziej


def scene5(p, t, T):
    fl = [1 if t < 0.5 + k * 0.35 else 0 for k in (3, 2, 1, 0)]
    corridor(p, t, fl, doors_open=0.9)
    # najpierw stoją i tylko się kołyszą, potem ruszają
    zt = 0.3 * min(t, 1.4) + max(0.0, t - 1.4)
    for i, (dx, delay) in enumerate(((-260, 0.0), (220, 0.15), (-60, 0.35), (380, 0.5), (-420, 0.6), (60, 0.05))):
        k = 0.05 * ease(t / 1.4) + 0.95 * ease((t - 1.4 - ZOMBIE_START[i]) / 2.4)
        k += 0.02 * max(0.0, noise(t, 40 + i, 3))  # szarpnięcia
        s = 0.35 + 1.0 * k + (0.2 if i == 5 else 0)
        x = 640 + dx * (0.3 + 0.9 * k)
        y = 420 + 300 * k
        zombie(p, x, y, s, zt + i * 0.4, i * 1.7, tilt=random.Random(i).uniform(-0.25, 0.25))


SCENE_FN = [scene1, scene2, scene3, scene4, scene5]

CAMERAS = [
    # powolny najazd przez cały plan aż do okna, w którym ktoś stoi
    lambda t, T: dict(zoom=1.0 + 2.4 * ease(t / T) ** 1.3, cx=640 + (WINDOW[0] + 20 - 640) * ease(t / T),
                      cy=360 + (WINDOW[1] + 23 - 360) * ease(t / T)),
    lambda t, T: dict(zoom=1.0 + 0.06 * t / T),
    lambda t, T: dict(zoom=(1.05 + 0.1 * ease(t / 2.8) + 0.08 * ease((t - 2.95) / 0.25) + 0.04 * ease((t - 3.5) / 2.0))
                      * (1 + 0.25 * ease((t - FACE_PUSH) / 0.2)), cy=300),
    lambda t, T: dict(zoom=1.0 + 0.18 * ease(t / T), cx=700, cy=360),
    lambda t, T: dict(zoom=1.0 + 0.05 * t / T),
]
VOICE_LEN = [voice_len(fn) for _, _, fn, _, _ in SCENES]

GRADE = [  # mnożnik RGB — chłodny, zielonkawy mrok
    (0.86, 0.96, 0.98), (0.92, 1.0, 0.94), (0.88, 0.98, 0.92), (0.95, 0.98, 0.96), (0.9, 0.98, 0.92),
]


def shake_at(t):
    amp = 0.0
    if SLAM_T <= t < SLAM_T + 0.45:
        amp = 14 * (1 - (t - SLAM_T) / 0.45)
    s5 = SCENES[4][0]
    if s5 + 2.0 <= t < s5 + 2.8:
        amp = 5
    return handheld(t, amp)


def framed(cam, shake):
    """Kamera nigdy nie pokazuje pustki poza narysowanym światem (0..W × 0..H), także w chwili wstrząsu:
    przesuwa środek kadru do środka, a jeśli to nie wystarcza — minimalnie dobliża."""
    z, cx, cy = cam.get("zoom", 1.0), cam.get("cx", W / 2), cam.get("cy", H / 2)
    mx, my = W / 2 + abs(shake[0]) + 1, H / 2 + abs(shake[1]) + 1
    z = max(z, mx / (W / 2), my / (H / 2))
    return dict(zoom=z, cx=min(max(cx, mx / z), W - mx / z), cy=min(max(cy, my / z), H - my / z), shake=shake)


def handheld(t, amp, seed=0):
    """Wstrząs + stałe, delikatne pływanie kamery z ręki."""
    r = random.Random(int(t * FPS) + seed)
    return (r.uniform(-amp, amp) + 2.5 * noise(t, 91 + seed, 0.35), r.uniform(-amp, amp) + 2.0 * noise(t, 92 + seed, 0.3))


def subtitle(img, txt):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 30)
    lines = txt.split("\n")
    y = H - 40 - 40 * len(lines)
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.rectangle([W / 2 - w / 2 - 8, y - 2, W / 2 + w / 2 + 8, y + 38], fill=(0, 0, 0))
        d.text((W / 2, y + 18), ln, font=f, fill=(255, 255, 255), anchor="mm")
        y += 40


def frame(t):
    for i, (a, b, _, vs, txt) in enumerate(SCENES):
        if a <= t < b or i == len(SCENES) - 1:
            break
    lt, T = t - a, b - a
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255))
    p = Pen(img, t, **framed(CAMERAS[i](lt, T), shake_at(t)))
    SCENE_FN[i](p, lt, T)
    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    arr *= np.array(GRADE[i], dtype=np.float32)
    if i == 1:
        dim = 1.0 if (lt < 3.8 or math.sin(lt * 40) > 0) else 0.72
        arr *= dim
    if i == 2:
        sl = SLAM_T - a
        # przed uderzeniem: krąg latarki drży na szybie
        arr = light_mask(arr, 640 + 14 * noise(lt, 23, 1.1) * (lt < sl), 260 if lt < sl else 280, 520, 0.35)
    if i == 4:
        dark = ease((lt - 2.3) / 0.6)
        lum = arr.mean(axis=2, keepdims=True)
        eyes = (lum > 215).astype(np.float32)
        arr = arr * (1 - dark) + arr * eyes * dark
        arr[..., 0] += 30 * max(0, math.sin(lt * 9)) * (1 - dark)
    # winieta + ziarno
    yy, xx = np.ogrid[:H, :W]
    vig = 1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
    arr *= np.clip(vig, 0.35, 1)[..., None]
    arr += np.random.default_rng(int(t * FPS)).normal(0, 5, (H, W, 1))
    # krótkie wejście z czerni i cięcia przez czerń
    fade = min(1.0, t / 0.4, max(0.0, (DUR - 0.15 - t) / 0.3))
    arr *= fade
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    if vs - 0.05 <= t < min(b - 0.05, vs + VOICE_LEN[i] + 0.8) and t < DUR - 0.2:
        subtitle(img, txt)
    return img


# ---------- dźwięk ----------

def breath_snd(out, sr, rng, t0, length, amp, inhale=True, low=False):
    """Oddech: szum w paśmie ok. 0,5–3 kHz (niżej dla „low”), narasta i opada."""
    i0 = int(t0 * sr)
    L = min(int(length * sr), len(out) - i0)
    if L <= 0:
        return
    nz = rng.normal(0, 1, L + 200)
    a, b = (24, 120) if low else (6, 40)
    band = np.convolve(nz, np.ones(a) / a, mode="same") - np.convolve(nz, np.ones(b) / b, mode="same")
    env = np.sin(np.pi * np.arange(L) / L) ** (1.6 if inhale else 0.7)
    out[i0:i0 + L] += amp * 4 * band[100:100 + L] * env


def creak(out, sr, t0, length, amp, f0):
    i0 = int(t0 * sr)
    L = min(int(length * sr), len(out) - i0)
    tt = np.arange(L) / sr
    out[i0:i0 + L] += amp * np.sin(2 * np.pi * (f0 + 0.6 * f0 * np.sin(tt * 5)) * tt) * np.sin(np.pi * tt / length)


def audio(path):
    sr = 44100
    n = int(DUR * sr)
    ts = np.arange(n) / sr
    rng = np.random.default_rng(7)
    out = np.zeros(n)
    S = [sc[0] for sc in SCENES]
    # niski dron + szum wiatru
    out += 0.06 * np.sin(2 * np.pi * 49 * ts) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * ts))
    out += 0.04 * np.sin(2 * np.pi * 73.4 * ts + np.sin(ts * 1.3))
    wind = np.convolve(rng.normal(0, 1, n), np.ones(400) / 400, mode="same")
    gust = 0.7 + 0.3 * np.interp(ts, np.arange(0, DUR + 1, 0.5), rng.uniform(-1, 1, len(np.arange(0, DUR + 1, 0.5))))
    out += 0.25 * wind * gust * (ts < S[1])
    creak(out, sr, 0.9, 2.6, 0.05, 210)  # brama
    # bzyczenie świetlówek w korytarzu
    hum = 0.03 * np.sign(np.sin(2 * np.pi * 100 * ts)) * ((ts > S[1]) & (ts < S[2]))
    out += hum * (np.sin(ts * 31) > -0.2)
    # kroki tylko kiedy idzie; po zatrzymaniu wolniejsze
    a, b = WALK_STOP
    steps = list(np.arange(0.1, a, 0.31)) + list(np.arange(b + 0.15, S[2] - S[1], 0.41))
    for k in steps:
        i0 = int((S[1] + k + rng.uniform(-0.02, 0.02)) * sr)
        L = int(0.08 * sr)
        out[i0:i0 + L] += rng.uniform(0.18, 0.28) * rng.normal(0, 1, L) * np.exp(-np.arange(L) / 500)
    breath_snd(out, sr, rng, S[1] + a + 0.3, 0.9, 0.05)
    breath_snd(out, sr, rng, S[1] + a + 1.4, 1.0, 0.04, inhale=False)
    # izolatka: cisza, uderzenie w szybę, potem jego powolny oddech
    i0 = int(SLAM_T * sr)
    L = int(1.2 * sr)
    e = np.exp(-np.arange(L) / (0.12 * sr))
    out[i0:i0 + L] += 0.9 * (rng.normal(0, 1, L) * e * 0.6 + np.sin(2 * np.pi * 42 * np.arange(L) / sr) * e)
    for k in np.arange(SLAM_T + 0.6, S[3] - 0.5, 1 / 0.35):
        breath_snd(out, sr, rng, k, 1.3, 0.05, inhale=False, low=True)
    # scena 4: skrzypnięcie, wstrzymany oddech, gwałtowny wdech, szybkie oddechy
    creak(out, sr, S[3] + CREAK, 1.4, 0.08, 300)
    breath_snd(out, sr, rng, S[3] + 2.55, 0.35, 0.09)
    for k in np.arange(S[3] + 3.2, S[4] - 0.2, 0.75):
        breath_snd(out, sr, rng, k, 0.35, 0.05, inhale=bool(int((k - S[3]) / 0.75) % 2))
    # narastający chór jęków + uderzenie na „Wszystkie”
    m = (ts > S[4]) & (ts < DUR - 0.8)
    moan = sum(np.sin(2 * np.pi * f * ts + 3 * np.sin(ts * (0.7 + j))) for j, f in enumerate((110, 131, 147, 98)))
    out += 0.05 * moan * m * np.clip((ts - S[4]) / 2.2, 0, 1)
    i0 = int((S[4] + 2.0) * sr)
    L = int(1.3 * sr)
    e = np.exp(-np.arange(L) / (0.3 * sr))
    out[i0:i0 + L] += 0.7 * (np.sin(2 * np.pi * 36 * np.arange(L) / sr) + 0.4 * rng.normal(0, 1, L)) * e
    out[int((DUR - 0.25) * sr):] *= 0.0
    # lektor
    for _, _, fn, vs, _ in SCENES:
        with wave.open(str(VOICE_DIR / fn)) as w:
            v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        i0 = int(vs * sr)
        v = v[: n - i0]
        out[i0:i0 + len(v)] += 0.95 * v
    out = np.tanh(out * 1.1) * 0.85
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


def main(stills=None):
    if stills:
        for t in stills:
            frame(t).save(HERE / f"klatka{SUFFIX}-{t:05.2f}s.png")
        return
    wav = HERE / f"audio{SUFFIX}.wav"
    audio(wav)
    out = HERE / f"zombie-psychiatryk{SUFFIX}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        proc.stdin.write(frame(k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(out)


if __name__ == "__main__":
    import sys
    main([float(a) for a in sys.argv[1:]] or None)
