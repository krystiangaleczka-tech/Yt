"""Wariant A · dzień 25 „Kuba” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 25
talk = K.talk
KB = K.WHO["kuba"]
HK = K.WHO["henryk"]


def s_five_days(p, t, T):
    K.listening(p, t, T, fear=0.35, gaze=(-0.5, 0.1))


def s_roof_way(p, t, T):
    K.listening(p, t, T, fear=0.4, gaze=(0.2, -0.4))


def s_irena_cant(p, t, T):
    K.listening(p, t, T, gaze=(0.0, 0.3), speaking=True)


def s_no_army(p, t, T):
    K.listening(p, t, T, fear=0.5, gaze=(-0.3, 0.4))


def s_grab(p, t, T):
    K.staff_room(p, t)
    k = ease(t / 0.35)
    K.figure(p, 420, 780, 1.0, t, "narrator", look=0.6, arms={"r": (90 - 40 * k, -40)}, eyes=1.0)
    K.figure(p, 780, 780, 1.05, t, "kuba", look=-0.3, lean=-0.3, mouth=0.9 if t > 0.4 else 0.2,
             arms={"l": (-30 - 60 * (1 - k), -170 + 40 * (1 - k))})
    s_ = 1.05
    hx = 780 - 50 * s_ + (-30 - 60 * (1 - k)) * s_
    hy = 780 - 268 * s_ + (-170 + 40 * (1 - k)) * s_
    K.handset(p, hx + 8, hy + 58, 0.45)  # słuchawka w jego dłoni, obok twarzy
    if t > 0.4:  # krzyk
        for i in range(4):
            a = -0.8 + i * 0.5
            p.line([(800 + 80 * math.cos(a), 350 + 60 * math.sin(a)), (840 + 110 * math.cos(a), 350 + 80 * math.sin(a))], w=5)


def s_kitchen(p, t, T):
    K.kitchen(p, t)
    for i, x in enumerate((300, 560, 820)):
        k = ease((t - 0.2 - i * 0.25) / 0.5)  # głowy podnoszą się na krzyk, jedna po drugiej
        R.zombie(p, x, 680, 0.95, t, 140 + i, tilt=0.35 * (1 - k) - 0.05 * k)


def s_corridor(p, t, T):
    R.corridor(p, t, 1.0)
    for i in range(4):
        k = (t / T + i * 0.15) % 1.0
        R.zombie(p, 560 + i * 60 - 40, 420 + 220 * k, 0.4 + 0.6 * k, t, 150 + i)


def s_shake(p, t, T):
    K.staff_room(p, t)
    sh = 6 * math.sin(t * 40) * min(1, t / 0.5)
    br = math.sin(t * 2 * math.pi * 1.4)  # oddech coraz szybszy
    K.face_cu(p, 640 + sh, 330, 1.0, "kuba", t, gaze=(0.6, 0.0), mouth=0.3 + 0.3 * abs(br), fear=0.8, breath=br * 2)


def shadows(p, t, speed, n=3):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    p.rect(-20, 560, W + 20, H + 20, (140, 137, 123))
    p.rect(300, 40, 980, 560, (150, 146, 130), w=4)  # futryna
    p.rect(320, 60, 960, 560, (110, 100, 90))
    p.rect(860, 300, 900, 330, (170, 170, 160), w=3)  # klamka
    p.rect(320, 556, 960, 572, (200, 200, 170), w=0)
    for i in range(n):
        x = 340 + ((t * speed * (1 + 0.2 * i) + i * 190) % 560)
        p.rect(x, 556, x + 40, 572, (20, 20, 22), w=0)


def s_feet_fast(p, t, T):
    shadows(p, t, 60 + 160 * ease(t / T))


def s_hold(p, t, T):
    """Zza ramienia Kuby: Henryk trzyma go za ramiona i liczy szeptem."""
    K.staff_room(p, t)
    K.face_cu(p, 640, 300, 0.9, "henryk", t, gaze=(0.0, 0.1), mouth=talk(t, T, speed=5) * 0.8)
    hands = []
    for side in (-1, 1):  # ręce Henryka do ramion Kuby
        a_, b_ = (640 + side * 120, 450), (640 + side * 240, 570)
        K.limb(p, a_, b_, 70, HK["top"], outline=4)
        hands.append(b_)
    br = 4 * math.sin(t * 2 * math.pi / 4.0)
    p.poly([(300, H + 20), (360, 600 + br), (510, 550 + br), (770, 550 + br), (920, 600 + br), (980, H + 20)], KB["top"])  # barki Kuby
    p.ell(640, 545 + br, 105, 115, (46, 36, 30))  # tył głowy Kuby
    for hx, hy in hands:
        p.ell(hx, hy + br, 46, 32, HK["skin"])


def s_slow(p, t, T):
    K.staff_room(p, t)
    rate = 1.4 - 1.15 * ease(t / T)  # oddech zwalnia do rytmu Henryka (cztery, cztery, cztery)
    br = math.sin(2 * math.pi * (t * rate))
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(0.0, 0.0), mouth=0.2 * abs(br), fear=0.6 - 0.4 * ease(t / T), breath=br * 2)


def s_feet_stop(p, t, T):
    shadows(p, min(t, 0.5) * 0, 1)  # cienie stoją
    for i in range(3):
        p.rect(400 + i * 170, 556, 440 + i * 170, 572, (20, 20, 22), w=0)


def s_cry(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(0.0, 0.5), mouth=talk(t, T, speed=6) * 0.6, fear=0.4)
    for side in (-1, 1):  # łzy
        y = 360 + ((t * 50) % 120)
        with K.on_face(p, "kuba"):
            p.poly([(640 + side * 46, y), (646 + side * 46, y + 14), (640 + side * 46, y + 20), (634 + side * 46, y + 14)], (190, 220, 235), w=2)


def s_me_too(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.2, 0.4), mouth=talk(t, T, speed=5) * 0.8)


def s_teach_me(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(-0.5, -0.1), mouth=talk(t, T), fear=0.1)


def keys(p):
    p.rect(0, 0, W, H, (70, 52, 40), w=0)
    p.rect(-20, 300, W + 20, 620, (236, 232, 216))
    for i in range(1, 16):
        p.line([(i * 85, 300), (i * 85, 620)], w=3)
    for i in (1, 2, 4, 5, 6, 8, 9, 11, 12, 13):
        p.rect(i * 85 - 22, 300, i * 85 + 22, 480, (30, 28, 26))
    p.rect(-20, 280, W + 20, 300, (84, 64, 50))


def s_place(p, t, T):
    keys(p)
    k = ease(t / (T * 0.7))
    K.limb(p, (300, H + 60), (520, 560), 110, KB["sleeve"], outline=4)
    p.ell(560, 540, 110, 60, KB["skin"])  # dłoń Kuby nad klawiszami, nie naciska
    for i in range(5):
        p.ell(470 + i * 45, 500, 16, 30, KB["skin"])
    K.limb(p, (W + 60, -60), (720, 420 + 60 * k), 90, HK["top"], outline=4)  # dłoń Henryka układa palce
    p.ell(680, 440 + 60 * k, 70, 44, HK["skin"])


def s_air(p, t, T):
    keys(p)
    K.limb(p, (300, H + 60), (520, 500), 110, KB["sleeve"], outline=4)
    p.ell(560, 470, 110, 60, KB["skin"])
    cur = int(t * 2.4) % 5  # pięć nut w powietrzu, palec po palcu
    for i in range(5):
        dy = 30 if i == cur else 0
        p.ell(470 + i * 45, 420 + dy, 16, 30, KB["skin"])


def s_lullaby(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.3, 0.6), mouth=talk(t, T, speed=5) * 0.8)


def s_irena(p, t, T):
    K.staff_room(p, t, night=True)
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(0.4, 0.3), mouth=talk(t, T, speed=6), fear=0.0)


FNS = [B.card("DZIEŃ 25"), s_five_days, s_roof_way, s_irena_cant, s_no_army, s_grab, s_kitchen, s_corridor, s_shake, s_feet_fast,
       s_hold, s_slow, s_feet_stop, s_cry, s_me_too, s_teach_me, s_place, s_air, s_lullaby, s_irena]
LOOK = [None] + [B.WARD] * 18 + [B.NIGHT]
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
