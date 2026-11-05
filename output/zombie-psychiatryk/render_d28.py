"""Wariant A · dzień 28 „Pożegnanie” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 28
talk = K.talk
HK = K.WHO["henryk"]
WALL = (150, 166, 140)


def s_breakfast(p, t, T):
    K.staff_room(p, t)
    for i, x in enumerate((900, 960)):  # garnki na kuchence
        p.rect(x - 30, 300, x + 30, 330, (90, 90, 90), w=3)
        for k in range(3):
            y = 290 - ((t * 50 + k * 40 + i * 20) % 120)
            p.ell(x + 10 * math.sin(t * 2 + k), y, 16 + 4 * k, 8, None, w=2, color=(240, 240, 240))
    stir = 20 * math.sin(t * 4)
    K.figure(p, 760, 780, 1.0, t, "irena", look=0.6, gaze=(0.6, 0.6), arms={"r": (140 + stir, 20)})


def face(p, t, T, who, gaze, fear=0.1, speed=9, bg=K.staff_room):
    bg(p, t)
    K.face_cu(p, 640, 330, 1.0, who, t, gaze=gaze, mouth=talk(t, T, speed=speed) * (0.8 if who == "henryk" else 1.0), fear=fear)


def s_afraid(p, t, T):
    face(p, t, T, "kuba", (0.4, 0.0), 0.2)


def s_long(p, t, T):
    face(p, t, T, "henryk", (-0.4, 0.0), speed=5)


def s_four(p, t, T):
    K.listening(p, t, T, who="zosia", gaze=(-0.4, 0.2), speaking=True, fear=0.2)


def s_fifth(p, t, T):
    K.listening(p, t, T, who="zosia", gaze=(0.0, 0.4), speaking=t > T * 0.4, fear=0.3)


def window_faces(p, t):
    """Twarze pacjentów w okienkach drzwi sal (geometria z render.corridor)."""
    for k, f in enumerate((0.28, 0.55, 0.78)):
        ff = f + 0.04
        top, bot = 250 * ff, H + (410 - H) * ff
        y = top + (bot - top) * 0.38 + 16 * (1 - f)
        for side, x in ((-1, 520 * ff), (1, W + (760 - W) * ff)):
            s = 0.5 * (1 - f) + 0.12
            p.ell(x, y + 14 * s, 18 * s, 22 * s, K.ZSKIN, w=2)
            for e in (-1, 1):
                p.ell(x + e * 7 * s, y + 10 * s, 4 * s, 4 * s, (236, 238, 226), w=0)


def s_walk(p, t, T):
    R.corridor(p, t, 1.0)
    window_faces(p, t)
    k = t / T
    K.figure_back(p, 560, 820 - 80 * k, 1.05 - 0.2 * k, t * 0.5, "henryk", walk=t * 0.5)
    K.figure_back(p, 760, 840 - 80 * k, 1.1 - 0.2 * k, t * 0.5, "narrator", walk=t * 0.5)


def ward_door(p, t, T, hair, line_t):
    """Drzwi sali z okienkiem: w środku pacjent (hair: siwy kok / łysina); Henryk z boku mówi imię."""
    p.rect(0, 0, W, H, WALL, w=0)
    p.rect(-20, 600, W + 20, H + 20, (104, 124, 100))
    p.rect(360, 60, 760, 640, (124, 138, 122))
    p.rect(470, 140, 650, 320, (20, 24, 24))
    zx = 560 + 6 * math.sin(t * 0.7)
    p.ell(zx, 250, 60, 72, K.ZSKIN)  # twarz za szybką, bez mrugania
    for e in (-1, 1):
        p.ell(zx + e * 22, 240, 10, 9, (236, 238, 226), w=2)
    if hair == "kok":
        p.ell(zx, 172, 50, 26, (200, 200, 196))
        p.ell(zx, 150, 24, 18, (200, 200, 196))
    else:
        for e in (-1, 1):
            p.ell(zx + e * 56, 236, 10, 20, (176, 176, 170), w=2)
    door = (124, 138, 122)
    for a, b, c, d in ((360, 60, 760, 140), (360, 320, 760, 640), (360, 140, 470, 320), (650, 140, 760, 320)):
        p.rect(a, b, c, d, door, w=0, amp=0)
    p.rect(470, 140, 650, 320, None, w=5)
    K.figure(p, 980, 820, 1.15, t, "henryk", look=-0.7, gaze=(-0.9, -0.2), mouth=talk(t, T, line_t, 0.4, 5) * 0.8)


def s_jadzia(p, t, T):
    ward_door(p, t, T, "kok", 0.5)


def s_stas(p, t, T):
    ward_door(p, t, T, "łysy", 0.4)


def s_knew(p, t, T):
    R.corridor(p, t, 1.0)
    R.nurse_face(p, 640, 330, 1.0, 0.25, t, gaze=(0.7, 0.0))


def s_iso(p, t, T):
    K.iso_door(p, t, inner=lambda q: K.zombie_back(q, 640, 470, 1.0, t, 170, gown=(226, 226, 220)))
    k = ease((t - 0.3) / 0.6)  # Henryk przy drzwiach podnosi dłoń i kładzie ją na szybie; Nowak się nie odwraca
    s_ = 1.15
    K.figure_back(p, 470, 720, s_, t, "henryk", arms={"r": (40 + 23 * k, 60 - 227 * k)})
    if k > 0.9:
        hx, hy = 470 + 50 * s_ + 63 * s_, 720 - 268 * s_ - 167 * s_
        for i in range(4):  # palce rozłożone na szybie
            p.line([(hx - 16 + i * 11, hy - 8), (hx - 18 + i * 12, hy - 32)], w=8, color=HK["skin"])


def s_cradle(p, t, T):
    k = ease((t - 0.2) / (T * 0.5))
    hs = (520 + 120 * k, 538 - 228 * k, -0.32 * (1 - k))  # słuchawka z biurka na widełki
    K.phone_detail(p, t, False, handset=hs)
    hx, hy = hs[0] + 40, hs[1] - 10
    K.limb(p, (hx + 300, -40), (hx + 40, hy - 10), 90, HK["top"], outline=4)
    p.ell(hx, hy, 70, 52, HK["skin"])


def s_gather(p, t, T):
    K.piano_room(p, t)
    lift = 4 * math.sin(t * 2)
    K.sitting(p, 230, 720, 0.8, t, "irena", gaze=(0.8, -0.2))
    K.figure(p, 1060, 760, 0.9, t, "zosia", look=-0.6)
    K.figure(p, 1200, 770, 0.9, t, "narrator", look=-0.6)
    K.figure_back(p, 640, 840, 1.05, t, "henryk", arms={"l": (-30, -26 + lift), "r": (30, -26 - lift)})
    K.figure(p, 900, 780, 0.9, t, "kuba", look=-0.5, mouth=0.2)
    for i in range(3):  # Kuba nuci
        y = 380 - ((t * 40 + i * 30) % 90)
        p.ell(860 - i * 16, y, 8, 6, (230, 230, 220), w=2)
        p.line([(868 - i * 16, y), (868 - i * 16, y - 24)], w=3, color=(230, 230, 220))


def s_irena(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(0.3, 0.2), mouth=talk(t, T, speed=6), fear=0.2)
    for side in (-1, 1):  # łzy
        y = 360 + ((t * 40) % 120)
        p.poly([(640 + side * 46, y), (646 + side * 46, y + 14), (640 + side * 46, y + 20), (634 + side * 46, y + 14)], (190, 220, 235), w=2)


def s_hug(p, t, T):
    K.piano_room(p, t)
    k = ease(t / 0.6)
    K.figure(p, 700, 780, 1.1, t, "henryk", look=0.0, arms={"l": (-14, 110), "r": (14, 110)}, gaze=(0.0, -0.2))  # sztywnieje
    K.figure_back(p, 660 - 60 * (1 - k), 800, 1.05, t, "zosia", arms={"l": (30 + 20 * (1 - k), 20), "r": (40 + 20 * (1 - k), 20)})


def s_notes(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    lines = ["d18: Nazywam się Henryk.", "Uczyłem muzyki.", "Ostrzegałem, nie straszyłem.", "Oddychaj."]
    n = min(len(lines), int(t / (T * 0.8) * len(lines)) + 1)
    K.paper(p, 600, 340, lines[:n], w=640, h=330)
    x = 600 + 220
    K.limb(p, (x + 380, H + 80), (x + 30, 500), 80, K.narr_sleeve(), outline=4)
    p.ell(x + 20, 490, 40, 30, K.SKIN)
    p.line([(x, 470), (x - 30 - 6 * math.sin(t * 9), 440)], w=6, color=(40, 40, 120))


def s_monsters(p, t, T):
    face(p, t, T, "henryk", (0.0, 0.2), speed=5, bg=K.piano_room)


def s_believed(p, t, T):
    face(p, t, T, "henryk", (-0.3, 0.0), speed=5, bg=K.piano_room)


def s_flicker(p, t, T):
    on = [1.0 if (t * (3 + k) + k * 0.37) % 1 > 0.35 else 0.0 for k in range(4)]  # agregat przerywa
    R.corridor(p, t, on)


FNS = [B.card("DZIEŃ 28"), s_breakfast, s_afraid, s_long, s_four, s_fifth, s_walk, s_jadzia, s_stas, s_knew, s_iso, s_cradle,
       s_gather, s_irena, s_hug, s_notes, s_monsters, s_believed, s_flicker]
LOOK = [None] + [B.WARD] * 17 + [B.NIGHT]
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
