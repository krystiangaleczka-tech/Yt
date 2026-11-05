"""Wariant A · dzień 6 „Noc patrolu” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 6
NURSE = (226, 226, 218)


def talk(t, T):
    return 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0


def step_xy(k):
    """Środek k-tego stopnia klatki schodowej (kit_a.stairwell) — tu stoją stopy."""
    return 180 + k * 120, 300 + k * 52


def nurse(p, x, y, s, t, tilt=0.35):
    R.zombie(p, x, y, s, t, 60, gown=NURSE, tilt=tilt)
    p.rect(x + 8 * s, y - 170 * s, x + 30 * s, y - 154 * s, (240, 240, 236), w=2)  # identyfikator


def s_guard(p, t, T):
    K.pharmacy_inside(p, t, dark=0.8)
    nod = ease((t - T * 0.4) / 0.6) * (1 - ease((t - T * 0.75) / 0.2))  # przysypia i budzi się gwałtownie
    h = K.sitting(p, 780, 700, 0.95, t, "narrator", gaze=(0.6, -0.2 + 1.0 * nod), eyes=1 - 0.85 * nod,
                  arms={"l": (60, 150), "r": (-50, 150)})
    p.rect(h["l"][0] - 10, h["l"][1] - 20, h["r"][0] + 10, h["l"][1] - 2, (60, 60, 60), w=3)  # zgaszona latarka


def s_sleep(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    K.face_cu(p, 640 + 6 * math.sin(t * 2.4), 340, 1.0, "nowak", t, blink_k=1.0, fear=0.5, breath=math.sin(t * 3))


def s_stairs_dark(p, t, T):
    sh = (t - T * 0.55) / (T * 0.4)  # cień przechodzi w szparze światła na górze
    K.stair_door(p, t, shadow=(-0.8 + 1.6 * sh) if 0 < sh < 1 else 0.0)


def s_foot(p, t, T):
    p.rect(0, 0, W, H, (36, 40, 42), w=0)
    p.rect(-20, 420, W + 20, H + 20, (70, 74, 74))
    p.line([(-20, 420), (W + 20, 420)], w=5)
    p.glow([(380, 0), (900, 0), (1000, 420), (300, 420)], (230, 230, 190, 34))
    k = ease(t / (T * 0.7))
    y = 420 - 160 * (1 - k)
    K.limb(p, (640, -60), (650, y - 40), 90, K.ZSKIN, outline=4)
    p.ell(670, y - 20, 110, 34, K.ZSKIN)  # stopa staje płasko na stopniu
    for i in range(4):
        p.ell(752 - i * 4, y - 30 + i * 8, 10, 8, K.ZSKIN, w=2)


def s_nurse_landing(p, t, T):
    K.stairwell(p, t)
    x, y = step_xy(1)
    tilt = 0.2 + 0.25 * ease((t - T * 0.5) / 0.8)  # głowa przekrzywia się jeszcze bardziej — nasłuchuje
    nurse(p, x, y, 0.9, t, tilt=tilt)


def s_badge(p, t, T):
    p.rect(0, 0, W, H, NURSE, w=0)
    for i in range(5):
        p.ell(300 + i * 170, 520 + (i * 37) % 90, 40 + (i * 13) % 30, 20, (150, 120, 100), w=0)  # plamy
    p.rect(470, 220, 810, 420, (244, 244, 240), w=4)
    p.rect(500, 250, 600, 380, (190, 200, 210), w=2)
    p.text(700, 300, "E. KOWAL", 34)
    p.text(700, 350, "pielęgniarka", 22)
    p.line([(640, 220), (640, 140)], w=5)


def s_hold(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    k = ease(t / 0.5)  # wciąga powietrze i nie wypuszcza
    R.nurse_face(p, 640, 330, 1.0, 0.5 + 0.25 * k, t, gaze=(-0.6, -0.6), breath=1.5 * k, blink_k=0.0)


def s_moan(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    K.face_cu(p, 640, 340, 1.0, "nowak", t, blink_k=1.0, fear=0.6, mouth=talk(t, T))


def s_nurse_step(p, t, T):
    K.stairwell(p, t)
    k = ease((t - T * 0.35) / (T * 0.4))
    x0, y0 = step_xy(1)
    x1, y1 = step_xy(2)
    nurse(p, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k - 20 * math.sin(k * math.pi), 0.9, t, tilt=0.4)


def s_hand_mouth(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, blink_k=0.6, fear=0.6)
    k = ease(t / 0.45)  # dłoń wjeżdża z boku i zamyka usta
    hx = 640 - 420 * (1 - k)
    K.limb(p, (-80, 700), (hx - 80, 430), 110, K.narr_sleeve(), outline=4)  # rękaw narratora od lewej
    p.ell(hx, 420, 96, 52, K.SKIN)  # dłoń na ustach, przed twarzą
    for i in range(3):
        p.line([(hx - 40 + i * 34, 392), (hx - 36 + i * 34, 446)], w=2.5)


def s_rise(p, t, T):
    K.pharmacy_inside(p, t, dark=0.8)
    K.sitting(p, 420, 700, 0.95, t, "nowak", eyes=0.0)
    k = ease(t / (T * 0.5))  # Henryk podnosi się zza regału: wychodzi z cienia w lewo
    h = K.figure(p, 900 - 120 * k, 760, 1.05, t * 0.4, "henryk", walk=t * 0.4 if k < 0.95 else None, look=-0.3,
                 arms={"r": (30, 60)})
    K.bandage(p, h["r"][0] + 10, h["r"][1] - 10, r=22)


def s_throw(p, t, T):
    K.stairwell(p, t)
    x, y = step_xy(8)
    k = ease(min(1.0, t / (T * 0.35)))
    h = K.figure(p, x, y, 0.95, t, "henryk", look=-0.6, arms={"r": (-60 - 40 * k, 40 - 200 * k)})
    if t < T * 0.35:
        K.bandage(p, h["r"][0], h["r"][1], r=18)
    else:  # rolka leci łukiem w górę schodów
        f = (t - T * 0.35) / (T * 0.65)
        bx = h["r"][0] - 900 * f
        by = h["r"][1] - 380 * f + 260 * f * f
        K.bandage(p, bx, by, r=18 * (1 - 0.4 * f), rot=t * 8)


def s_bounce(p, t, T):
    p.rect(0, 0, W, H, (92, 106, 96), w=0)
    p.rect(-20, 520, W + 20, H + 20, (110, 118, 106))
    p.line([(-20, 520), (W + 20, 520)], w=4)
    f = t / T
    if f < 0.35:
        x, y = 200 + 1500 * f, 520 - 300 * math.sin(f / 0.35 * math.pi / 2)
    else:  # odbija się od ściany i turla po podeście
        g = (f - 0.35) / 0.65
        x, y = 725 - 260 * g, 220 + 280 * min(1, g * 2) ** 2
    K.bandage(p, x, min(y, 480), r=40, rot=t * 9)
    if 0.3 < f < 0.45:
        for k in range(4):
            a = k * 0.8 - 1.2
            p.line([(760 + 30 * math.cos(a), 220 + 30 * math.sin(a)), (760 + 70 * math.cos(a), 220 + 70 * math.sin(a))], w=4)


def s_nurse_up(p, t, T):
    K.stairwell(p, t)
    k = t / T
    pos = 2 - 2 * k
    i = int(math.floor(pos))
    fr = ease(pos - i)
    xa, ya = step_xy(i)
    xb, yb = step_xy(min(8, i + 1))
    K.zombie_back(p, xa + (xb - xa) * fr, ya + (yb - ya) * fr, 0.9, t, 61, gown=NURSE, walk=t * 0.6)


def s_nod(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    nod = 14 * max(0.0, math.sin((t - 0.6) * 3.0)) if 0.6 < t < 0.6 + math.pi / 3.0 else 0.0
    K.face_cu(p, 640, 330 + nod, 1.0, "henryk", t, gaze=(-0.4, 0.2 + nod / 30))


def s_cans(p, t, T):
    K.stairwell(p, t)
    sw = 6 * math.sin(t * 2)
    a, b = step_xy(3), step_xy(5)
    p.line([(a[0] - 60, a[1] - 40), (b[0] + 60, b[1] - 40)], w=2, color=(240, 240, 230), amp=0.4)
    for k in range(5):
        x = a[0] - 40 + k * 70
        y = a[1] - 40 + (b[1] - a[1]) * (x - a[0] + 60) / (b[0] - a[0] + 120)
        p.line([(x, y), (x + sw, y + 30)], w=1.5, color=(240, 240, 230))
        p.rect(x + sw - 16, y + 30, x + sw + 16, y + 70, (180, 186, 190), w=3)


def s_chalk(p, t, T):
    p.rect(0, 0, W, H, (96, 94, 86), w=0)
    for x in range(-200, W + 200, 200):
        p.line([(x, 0), (x - 160, H)], w=3, color=(70, 70, 64))
    for y in range(0, H, 160):
        p.line([(0, y), (W, y)], w=3, color=(70, 70, 64))
    for i, (x, y) in enumerate(((200, 600), (420, 450), (600, 300), (820, 170))):
        if t > i * 0.3:
            p.line([(x - 60, y + 40), (x + 60, y - 40)], w=7, color=(236, 236, 226))
            p.line([(x + 60, y - 40), (x + 20, y - 40), (x + 60, y - 40), (x + 44, y - 4)], w=7, color=(236, 236, 226))


def s_aside(p, t, T):
    K.pharmacy_inside(p, t)
    k = ease(t / T)
    hz = K.figure(p, 560 - 140 * k, 760, 1.05, t * 0.5, "zosia", walk=t * 0.5 if 0.1 < k < 0.9 else None, look=0.6,
                  mouth=talk(t, T), arms={"r": (90, 70)})
    K.figure(p, hz["r"][0] + 110, 760, 1.05, t * 0.5, "narrator", walk=t * 0.5 if 0.1 < k < 0.9 else None, look=-0.5,
             arms={"l": (-30, 70)})
    p.ell(hz["r"][0], hz["r"][1], 14, 14, K.WHO["zosia"]["skin"])  # dłoń Zosi na rękawie narratora (przed rękawem)


def s_brush(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - T * 0.5) / 0.4)  # odwraca wzrok, żeby nie patrzeć Zosi w oczy
    R.nurse_face(p, 640, 320, 1.0, 0.2, t, gaze=(-0.6 - 0.3 * k, 0.3 + 0.5 * k))


def s_doubt(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - T * 0.5) / 0.6)  # Zosia przenosi wzrok na śpiącego Nowaka
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.5 + 0.4 * k, 0.4 * k))


def s_tally(p, t, T):
    p.rect(0, 0, W, H, (142, 140, 128), w=0)
    for i in range(4):  # pięć kresek Henryka: cztery pionowe i piąta na ukos
        x = 340 + i * 70
        p.line([(x, 220), (x + 6, 460)], w=8)
    p.line([(320, 380), (600, 300)], w=8)
    k = ease(t / (T * 0.6))  # narrator dopisuje szóstą
    x, y0 = 680, 220
    y = y0 + 240 * k
    p.line([(x, y0), (x + 6 * k, y)], w=8, color=(236, 236, 226))
    K.limb(p, (x + 560, H + 120), (x + 40, y + 50), 110, K.narr_sleeve(), outline=4)
    p.ell(x + 30, y + 30, 54, 40, K.SKIN)
    p.rect(x - 6, y - 6, x + 18, y + 30, (240, 240, 232), w=2)  # kreda w palcach


def s_window(p, t, T):
    def inner(q):
        q.rect(0, 0, W, H, (170, 176, 176), w=0)
        q.poly([(0, 420), (W, 400), (W, H), (0, H)], (98, 110, 88))
        for x in range(0, W + 1, 36):
            q.line([(x, 420), (x + 36, 540)], w=1.5, color=(70, 76, 72), amp=0.4)
            q.line([(x + 36, 420), (x, 540)], w=1.5, color=(70, 76, 72), amp=0.4)
        q.line([(0, 420), (W, 420)], w=4, color=(60, 62, 60))
        for k in range(3):  # ptaki zrywają się z płotu na dźwięk megafonu
            f = ease((t - 0.8 - k * 0.2) / 1.6)
            bx, by = 400 + k * 160 + 300 * f, 410 - 260 * f
            q.line([(bx - 12, by - 6), (bx, by), (bx + 12, by - 6)], w=3)
    K.basement_window(p, inner)


FNS = [B.card("DZIEŃ 6 · noc"), s_guard, s_sleep, s_stairs_dark, s_foot, s_nurse_landing, s_badge, s_hold, s_moan,
       s_nurse_step, s_hand_mouth, s_rise, s_throw, s_bounce, s_nurse_up, s_nod,
       s_cans, s_chalk, s_aside, s_brush, s_doubt, s_tally, s_window]
LOOK = [None] + [B.NIGHT] * 15 + [B.BASE] * 7
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
