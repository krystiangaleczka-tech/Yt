"""Wariant A · dzień 27 „Plan” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 27
talk = K.talk
HK = K.WHO["henryk"]
PENCIL = (70, 70, 80)


def plan(p, route=1.0):
    """Plan budynku Nowaka (z dnia 12): budynek, boczne drzwi, podwórze, brama; ołówkiem droga."""
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    p.poly([(140, 70), (1140, 60), (1150, 660), (130, 670)], (236, 232, 214), w=3)
    p.rect(220, 120, 760, 330, None, w=3, color=PENCIL)  # budynek
    for x in (320, 420, 520, 620):
        p.line([(x, 120), (x, 330)], w=1.5, color=PENCIL)
    p.text(490, 160, "SZPITAL", 26, fill=PENCIL)
    p.rect(700, 300, 760, 330, (236, 232, 214), w=3, color=PENCIL)  # boczne drzwi
    p.text(730, 360, "BOK", 22, fill=PENCIL)
    p.line([(200, 600), (1100, 600)], w=3, color=PENCIL)  # płot
    p.rect(860, 585, 960, 615, (236, 232, 214), w=3, color=PENCIL)
    p.text(910, 640, "BRAMA", 22, fill=PENCIL)
    p.text(440, 470, "PODWÓRZE", 26, fill=PENCIL)
    pts = [(730, 330), (760, 400), (820, 470), (870, 530), (910, 585)]
    n = max(2, int(len(pts) * route + 0.999))
    p.line(pts[:n], w=5, color=(60, 60, 140))
    if route >= 1:
        p.text(960, 470, "100 m", 26, fill=(60, 60, 140))
    return pts[n - 1]


def s_plan(p, t, T):
    end = plan(p, ease(t / (T * 0.7)))
    K.limb(p, (end[0] + 360, H + 80), (end[0] + 30, end[1] + 40), 70, K.narr_sleeve(), outline=4)
    p.ell(end[0] + 22, end[1] + 30, 36, 26, K.SKIN)
    p.line([(end[0], end[1]), (end[0] + 22, end[1] + 26)], w=8, color=(200, 160, 60))


def s_crowd(p, t, T):
    K.yard_view(p, t)
    K.crowd(p, t, n=44, seed=27, turn=0.2, area=(60, 1220, 320, 700))


def henryk(p, t, T, gaze=(0.2, 0.2), bg=None):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=gaze, mouth=talk(t, T, speed=5) * 0.8)


def s_alarm(p, t, T):
    henryk(p, t, T, (0.3, 0.3))


def s_finger(p, t, T):
    k = ease(t / (T * 0.8))
    plan(p, 1.0)
    pts = [(730, 330), (760, 400), (820, 470), (870, 530), (910, 585)]
    i = min(len(pts) - 2, int(k * (len(pts) - 1)))
    f = k * (len(pts) - 1) - i
    x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
    y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
    K.limb(p, (x - 400, H + 80), (x - 20, y + 40), 80, HK["top"], outline=4)
    p.ell(x - 14, y + 26, 34, 26, HK["skin"])
    p.line([(x - 10, y + 10), (x, y)], w=12, color=HK["skin"])


def s_minute(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.5, 0.1), mouth=talk(t, T), fear=0.3)


def s_hold(p, t, T):
    henryk(p, t, T, (-0.4, 0.0))


def s_me(p, t, T):
    K.staff_room(p, t)
    R.nurse_face(p, 640, 330, 1.0, 0.4 if 0.3 < t < T - 0.4 else 0.3, t, gaze=(0.5, 0.0))


def s_no(p, t, T):
    K.staff_room(p, t)
    sh = 20 * math.sin(t * 5) * (1 - ease((t - 0.8) / 0.4))
    K.face_cu(p, 640 + sh, 330, 1.0, "henryk", t, gaze=(-0.5, 0.0), mouth=talk(t, T, 0.9, 0.4, 5) * 0.8)


def s_you_too(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.5, 0.0), mouth=talk(t, T), fear=0.4)


def s_scar(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    K.limb(p, (-80, 560), (1000, 380), 200, HK["skin"], outline=4)  # przedramię
    p.ell(1060, 370, 110, 90, HK["skin"])
    k = ease(t / (T * 0.6))  # rękaw piżamy podjeżdża w górę
    K.limb(p, (-80, 600), (220 + 500 * (1 - k), 520 - 120 * (1 - k)), 230, HK["top"], outline=4)
    if k > 0.6:
        p.line([(560, 450), (700, 420)], w=9, color=(196, 130, 130))  # blizna po paznokciu (d11)
        p.line([(580, 476), (690, 452)], w=6, color=(196, 130, 130))


def s_scar_talk(p, t, T):
    henryk(p, t, T, (0.0, 0.4))


def s_mouth(p, t, T):
    K.staff_room(p, t)
    m = 0.6 if 0.4 < t < T * 0.6 else 0.0  # otwiera usta i zamyka je bez słowa
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.4, 0.2), mouth=m, fear=0.4)


def s_kuba(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(-0.3, 0.0), mouth=talk(t, T), fear=0.1)


def s_smile(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.4, 0.0), mouth=talk(t, T, 1.2, 0.4, 5) * 0.8)
    k = ease((t - 0.2) / 0.6)
    for side in (-1, 1):  # uśmiech, zanim powie
        p.line([(640 + side * 18, 412), (640 + side * (24 + 6 * k), 412 - 8 * k)], w=4)


def s_lodge(p, t, T):
    k = ease(t / T)
    K.porter_lodge(p, t, wires=0.2 + 0.8 * k)
    K.figure(p, 760, 780, 0.95, t, "kuba", look=0.6, arms={"r": (100, -40), "l": (60, -20)})
    K.figure(p, 1120, 780, 0.95, t, "narrator", look=-0.6, arms={"l": (-80, -10)})


def s_cable(p, t, T):
    k = ease(t / T)
    K.piano_room(p, t, wire=k)
    p.rect(1040, 580, 1240, 620, (40, 40, 40))  # otwarty kanał w podłodze
    K.figure(p, 1100, 760, 0.95, t * 0.4, "kuba", look=-0.6, lean=-0.3, arms={"l": (-120, 100 + 10 * math.sin(t * 4))})


def s_test(p, t, T):
    p.rect(0, 0, W, H, (70, 52, 40), w=0)
    p.rect(-20, 300, W + 20, 620, (236, 232, 216))
    for i in range(1, 16):
        p.line([(i * 85, 300), (i * 85, 620)], w=3)
    for i in (1, 2, 4, 5, 6, 8, 9, 11, 12, 13):
        p.rect(i * 85 - 22, 300, i * 85 + 22, 480, (30, 28, 26))
    down = 0.3 < t < 1.3  # klawisz w dół na sekundę
    p.rect(595, 300 + (20 if down else 0), 680, 620, (220, 216, 200) if down else (236, 232, 216), w=3)
    K.limb(p, (900, H + 60), (650, 420 + (20 if down else 0)), 80, K.WHO["kuba"]["sleeve"], outline=4)
    p.ell(640, 410 + (20 if down else 0), 40, 30, K.WHO["kuba"]["skin"])
    p.line([(1000, 330), (1120, 330), (1140, 280)], w=4, color=(200, 60, 60))  # kabel do alarmu
    if down:
        for k in range(4):
            a = -1.2 + k * 0.5
            p.line([(1000 + 60 * math.cos(a), 160 + 60 * math.sin(a)), (1000 + 110 * math.cos(a), 160 + 110 * math.sin(a))], w=6,
                   color=(220, 60, 50))


def s_turn(p, t, T):
    K.yard_view(p, t, night=True, dawn=0.55)
    K.crowd(p, t, n=44, seed=27, turn=ease((t - 0.2) / (T * 0.7)) * 1.4, area=(60, 1220, 320, 700))


def s_window(p, t, T):
    K.staff_room(p, t, night=True)
    k = ease((t - 0.4) / 1.4)
    R.nurse_face(p, 640, 330, 1.0, 0.3 + 0.25 * k, t, gaze=(-0.7, 0.0 + 0.4 * k))


FNS = [B.card("DZIEŃ 27"), s_plan, s_crowd, s_alarm, s_finger, s_minute, s_hold, s_me, s_no, s_you_too, s_scar, s_scar_talk, s_mouth,
       s_kuba, s_smile, s_lodge, s_cable, s_test, s_turn, s_window]
LOOK = [None] + [B.WARD] + [B.DAY] + [B.WARD] * 15 + [B.NIGHT] * 2
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
