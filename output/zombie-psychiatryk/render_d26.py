"""Wariant A · dzień 26 „Miasto gaśnie” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import random
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 26
talk = K.talk
COLD = ((0.86, 0.96, 0.98), None)  # barwa pierwszego ujęcia filmu (render.GRADE[0])


def s_irena_all(p, t, T):
    K.staff_room(p, t)
    K.figure(p, 640, K.TABLE_STAND, 0.95 * K.TABLE_S, t, "irena", look=0.0, mouth=talk(t, T, speed=6))  # za stołem
    K.staff_table(p)
    K.figure_back(p, 240, 900, 1.2, t, "zosia")
    K.figure_back(p, 1050, 900, 1.2, t, "kuba")


def s_zosia(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.5, 0.0), mouth=talk(t, T), fear=0.3)


def s_irena(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(-0.4, 0.1), mouth=talk(t, T, speed=6), fear=0.0)


def s_promise(p, t, T):
    K.staff_room(p, t)
    R.nurse_face(p, 640, 330, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.5, 0.1))


def s_pat(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(0.0, 0.3), fear=0.0)
    with K.on_face(p, "irena"):
        for side in (-1, 1):  # smutny uśmiech
            p.line([(640 + side * 18, 412), (640 + side * 28, 404)], w=4)
    pat = 12 * abs(math.sin(t * 4)) if t < T * 0.7 else 0
    K.limb(p, (W + 60, H + 40), (820, 650), 80, K.narr_sleeve(), outline=4)  # dłoń narratora
    p.ell(800, 640, 50, 32, K.SKIN)
    K.limb(p, (300, H + 60), (760, 620 - pat), 70, K.WHO["irena"]["sleeve"], outline=4)  # klepie go po dłoni
    p.ell(770, 616 - pat, 40, 28, K.WHO["irena"]["skin"])


def s_city_dark(p, t, T):
    K.city_far(p, t, fire=1.0, dark=ease(t / T))


def runner(p, x, y, s, ph):
    """Obcy człowiek biegnący ulicą: ciemna sylwetka, bez twarzy (to nie nasi bohaterowie)."""
    ink = (24, 24, 30)
    st = math.sin(ph)
    for sg in (-1, 1):
        p.line([(x, y - 50 * s), (x + sg * st * 18 * s, y)], w=6 * s, color=ink)
        p.line([(x, y - 100 * s), (x - sg * st * 20 * s, y - 70 * s)], w=5 * s, color=ink)
    p.poly([(x - 12 * s, y - 104 * s), (x + 12 * s, y - 104 * s), (x + 14 * s, y - 50 * s), (x - 10 * s, y - 50 * s)], ink, w=0)
    p.ell(x + 4 * s, y - 116 * s, 11 * s, 12 * s, ink, w=0)


def binocular_mask(p, r=330, cy=360, cxs=(410, 870)):
    """Czerń poza dwoma kręgami lornetki (sumą dwóch kół)."""
    xa, xb = cxs[0] - r, cxs[1] + r

    def edge(x, sign):
        ys = [cy + sign * math.sqrt(max(0.0, r * r - (x - c) ** 2)) for c in cxs if abs(x - c) <= r]
        return (min(ys) if sign < 0 else max(ys)) if ys else cy
    xs = [xa + (xb - xa) * i / 80 for i in range(81)]
    p.poly([(xa, -60)] + [(x, edge(x, -1)) for x in xs] + [(xb, -60)], (0, 0, 0), w=0, amp=0)
    p.poly([(xa, H + 60)] + [(x, edge(x, 1)) for x in xs] + [(xb, H + 60)], (0, 0, 0), w=0, amp=0)
    p.rect(-60, -60, xa + 1, H + 60, (0, 0, 0), w=0, amp=0)
    p.rect(xb - 1, -60, W + 60, H + 60, (0, 0, 0), w=0, amp=0)


def s_binoculars(p, t, T):
    p.rect(0, 0, W, H, (40, 40, 52), w=0)
    p.rect(-20, 360, W + 20, 460, (70, 70, 76))  # ulica
    for i in range(10):  # ludzie biegną w stronę rzeki (w prawo)
        x = (i * 140 + t * (180 + 30 * (i % 3))) % (W + 200) - 100
        runner(p, x, 440, 0.9 + 0.1 * (i % 3), t * 9 + i)
    for x in range(0, W, 220):
        p.rect(x, 120, x + 160, 360, (56, 56, 70), w=3)
    binocular_mask(p)


def s_flash(p, t, T):
    K.city_far(p, t, fire=0.6, dark=0.85)
    f = 1 - ease(abs(t - T * 0.3) / 0.25)  # jeden daleki błysk, potem cisza
    if f > 0:
        p.glow([(800, 200), (1100, 200), (1100, 340), (800, 340)], (255, 250, 220, int(120 * f)))
        p.ell(950, 320, 30 * f, 14 * f, (255, 250, 220), w=0)


def s_malec(p, t, T):
    K.listening(p, t, T, fear=0.45, gaze=(-0.5, 0.2))


def s_where(p, t, T):
    K.listening(p, t, T, gaze=(0.2, 0.2), speaking=True)


def s_healthy(p, t, T):
    K.listening(p, t, T, fear=0.55, gaze=(0.0, 0.4))


def s_hang(p, t, T):
    K.staff_room(p, t)
    k = ease((t - 0.3) / 0.9)
    R.nurse_face(p, 640, 330, 1.0, 0.45 + 0.2 * k, t, gaze=(0.0, 0.8 * k))
    K.handset(p, 500 - 40 * k, 360 + 170 * k, who="narrator")  # słuchawka w dłoni opada w dół, obok twarzy


def s_barrels(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    K.figure(p, 1000, 760, 0.9, t, "zosia", look=0.4, arms={"r": (40 - 20 * abs(math.sin(t * 5)), 60)})
    for i, x in enumerate((960, 1060, 1160)):
        if int(t * 2.5) % 3 == i:  # stuknięcie: puste beczki dudnią
            for k in range(3):
                p.line([(x + 50 + k * 10, 380 - k * 12), (x + 70 + k * 10, 374 - k * 12)], w=3)


def s_four_days(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.4, 0.1), mouth=talk(t, T), fear=0.35)


def s_count(p, t, T):
    K.staff_room(p, t)
    k = t / T
    nxt = min(4, int(k * 5))
    for m in range(26, 26 + nxt):  # palec odlicza cztery puste miejsca dalej
        g, kk = divmod(m, 5)
        row, col = divmod(g, 3)
        x0, y0 = 520 + col * 70 - row * 10, 120 + row * 80
        p.ell(x0 + kk * 12 + 2, y0 + 30, 5, 5, (120, 116, 100), w=0)
    m = 25 + nxt
    g, kk = divmod(m, 5)
    row, col = divmod(g, 3)
    hx, hy = 520 + col * 70 - row * 10 + kk * 12, 120 + row * 80 + 40
    K.limb(p, (hx + 300, hy + 420), (hx + 20, hy + 24), 60, K.narr_sleeve(), outline=4)
    p.ell(hx + 14, hy + 16, 26, 20, K.SKIN)
    p.line([(hx + 4, hy + 6), (hx, hy - 10)], w=10, color=K.SKIN)


def s_good(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.2, 0.0), mouth=talk(t, T, speed=5) * 0.8)


def s_tune(p, t, T):
    K.piano_room(p, t, lights=False)
    p.poly([(420, 260), (860, 260), (880, 200), (400, 200)], (84, 64, 50), w=4)  # uniesiona pokrywa
    K.figure_back(p, 640, 820, 1.05, t, "henryk", arms={"l": (-40, -150), "r": (20, -170)})
    if int(t * 1.5) % 2 == 0:  # pojedyncze ciche dźwięki
        p.ell(900, 220 - (t * 30) % 40, 10, 8, (200, 200, 190), w=2)
        p.line([(910, 220 - (t * 30) % 40), (910, 190 - (t * 30) % 40)], w=3, color=(200, 200, 190))


def s_gate(p, t, T):
    K.window8_close(p, t)
    K.figure_back(p, 300, 900, 1.35, t, "soldier", arms={"r": (40, -120)})
    glow = 0.6 + 0.4 * math.sin(t * 2)  # żar papierosa
    p.ell(300 + 54 * 1.35 + 40, 900 - 268 * 1.35 - 120 * 1.35 + 10, 6, 6, (255, int(120 + 80 * glow), 60), w=0)
    for k in range(3):
        y = 380 - ((t * 30 + k * 30) % 90)
        p.ell(400 + 8 * math.sin(t + k), y, 10 + k * 4, 6 + k * 2, (150, 150, 150), w=1.5)


FNS = [B.card("DZIEŃ 26"), s_irena_all, s_zosia, s_irena, s_promise, s_pat, s_city_dark, s_binoculars, s_flash, s_malec, s_where,
       s_healthy, s_hang, s_barrels, s_four_days, s_count, s_good, s_tune, s_gate]
LOOK = [None] + [B.WARD] * 5 + [COLD] * 3 + [B.WARD] * 8 + [B.NIGHT] + [COLD]
CAM = {15: {"zoom": 2.2, "cx": 620, "cy": 210}}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
