"""Wariant A · dzień 24 „Gorączka” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 24
talk = K.talk
ZS = K.WHO["zosia"]


def room(p, t, **kw):
    """Pokój socjalny w dniu 24: na ścianie 23 kreski — dwudziesta czwarta przybywa dopiero rano (d24_19)."""
    K.staff_room(p, t, marks=23, **kw)


def door_right(p, t, shadows=1.0, leave=0.0):
    """Drzwi pokoju socjalnego na prawej ścianie; w szparze pod nimi cienie stóp (leave 0..1 — odchodzą)."""
    p.rect(1080, 150, 1260, 560, (110, 100, 90))
    p.rect(1090, 330, 1110, 350, (170, 170, 160), w=2)
    p.rect(1080, 556, 1260, 566, (200, 200, 170), w=0)
    for i in range(3):
        x = 1100 + i * 50 + 260 * leave * (1 + 0.3 * i)
        if shadows and x < 1240:
            p.rect(x, 556, x + 26, 566, (20, 20, 22), w=0)


def s_shot(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    K.limb(p, (-80, 300), (900, 420), 200, ZS["skin"], outline=4)  # ramię Zosi
    K.limb(p, (-80, 300), (300, 340), 230, ZS["sleeve"], outline=4)
    k = ease(t / (T * 0.6))
    x = 700 + 60 * (1 - k)  # igła wchodzi, tłok idzie w dół
    p.rect(x, 200, x + 50, 380, (230, 236, 240), w=3)
    p.rect(x + 6, 200 + 120 * k, x + 44, 380, (240, 220, 200), w=0)
    p.line([(x + 25, 380), (x + 25, 430)], w=3, color=(150, 150, 150))
    p.rect(x - 10, 160 + 120 * k, x + 60, 200 + 120 * k, (200, 200, 200), w=3)


def s_barricade(p, t, T):
    room(p, t, couch=False)
    door_right(p, t)
    k = ease(t / T)
    dx = 300 * k  # kanapa jedzie pod drzwi
    p.poly([(420 + dx, 560), (760 + dx, 560), (780 + dx, 470), (400 + dx, 470)], (120, 90, 110))
    p.rect(400 + dx, 440, 780 + dx, 480, (110, 80, 100))
    K.figure(p, 300 + dx, 780, 1.0, t * 0.6, "kuba", walk=t * 0.6, look=0.5, lean=0.5, arms={"l": (90, 140), "r": (110, 140)})


def s_henryk_door(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    p.rect(-20, 560, W + 20, H + 20, (140, 137, 123))
    p.rect(560, 80, 980, 560, (110, 100, 90))  # drzwi z bliska, za barykadą
    p.rect(560, 556, 980, 570, (200, 200, 170), w=0)
    for i in range(3):  # stoją i nasłuchują: cienie bez ruchu
        p.rect(620 + i * 110, 556, 660 + i * 110, 570, (20, 20, 22), w=0)
    br = math.sin(t * 2 * math.pi / 5.0)
    K.sitting(p, 330, 740 - 4 * br, 1.0, t, "henryk", gaze=(0.8, 0.2))


def note(p, lines, hand_col, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    n = min(len(lines), int(t / (T * 0.7) * len(lines)) + 1)
    K.paper(p, 600, 340, lines[:n], w=640, h=260)
    x = 860
    K.limb(p, (x + 380, H + 80), (x + 30, 470), 80, hand_col, outline=4)
    p.ell(x + 20, 460, 40, 30, K.SKIN if hand_col != ZS["sleeve"] else ZS["skin"])
    p.line([(x, 440), (x - 30 - 6 * math.sin(t * 9), 410)], w=6, color=(40, 40, 120))


def s_note_knee(p, t, T):
    note(p, ["KOLANO —", "PRZEJDZIE?"], K.narr_sleeve(), t, T)


def s_note_cut(p, t, T):
    note(p, ["ROZCIĘCIE", "TO NIE UGRYZIENIE"], ZS["sleeve"], t, T)


def s_irena_sleeps(p, t, T):
    room(p, t)
    K.face_cu(p, 640, 340, 1.0, "irena", t, gaze=(0.0, 0.0), blink_k=1.0, breath=math.sin(t * 1.2) * 2)


def s_forty(p, t, T):
    K.thermometer(p, t, value=40.0, rise=ease(t / (T * 0.7)))


def zosia_fever(p, t, T, mouth=True):
    room(p, t, night=True)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.4, 0.2), mouth=talk(t, T, speed=5) * 0.7 if mouth else 0.0, fear=0.45)
    for k in range(3):  # pot
        y = 220 + ((t * 30 + k * 60) % 180)
        p.poly([(560 + k * 70, y), (566 + k * 70, y + 12), (560 + k * 70, y + 18), (554 + k * 70, y + 12)], (190, 220, 235), w=2)


def s_leave_me(p, t, T):
    zosia_fever(p, t, T)


def s_no(p, t, T):
    room(p, t, night=True)
    sh = 30 * math.sin(t * 7) * (1 - ease((t - 0.9) / 0.5))  # kręci głową
    R.nurse_face(p, 640 + sh, 330, 1.0, 0.45, t, gaze=(-0.3, 0.1), body=(640, 330))


def s_three(p, t, T):
    zosia_fever(p, t, T)


def s_ice(p, t, T):
    p.rect(0, 0, W, H, (190, 186, 170), w=0)
    p.poly([(300, 300), (980, 280), (1000, 560), (280, 580)], (230, 236, 240), w=4)  # ręcznik
    k = ease(t / T)
    for i in range(6):
        x, y = 520 + (i % 3) * 90, 380 + (i // 3) * 80
        p.rect(x, y, x + 60, y + 50, (200, 230, 240), w=3)
    p.poly([(300 + 300 * k, 300 + 140 * k), (980, 280), (1000, 560), (280, 580)], (230, 236, 240), w=4)  # zawija
    for side in (-1, 1):
        K.limb(p, (640 + side * 700, H + 60), (640 + side * (380 - 120 * k), 500), 100, K.WHO["kuba"]["sleeve"], outline=4)
        p.ell(640 + side * (370 - 120 * k), 495, 46, 34, K.WHO["kuba"]["skin"])


def s_compress(p, t, T):
    room(p, t, night=True)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.3, 0.6))  # nie zamyka oczu
    k = math.sin(min(1.0, t / T) * math.pi)
    p.rect(300, 560 - 60 * k, 460, 610 - 60 * k, (230, 236, 240), w=3)  # okład w dłoni
    K.limb(p, (900, H + 60), (440, 600 - 60 * k), 80, K.WHO["henryk"]["top"], outline=4)


def blinks(t):
    """Nerwowe mruganie w gorączce: co ok. 0,6 s, nierówno."""
    ph = (t * 1.7 + 0.3 * math.sin(t * 3)) % 1.0
    return 1.0 if ph < 0.12 else 0.0


def s_eyes(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    K.face_cu(p, 640, 470, 2.6, "zosia", t, gaze=(0.0, 0.0), blink_k=blinks(t), fear=0.3)


def s_tally_blinks(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    K.paper(p, 600, 340, [], w=700, h=300)
    n = int(t * 1.7)  # jedna kreska na każde mrugnięcie
    for m in range(n):
        g, k = divmod(m, 5)
        x0, y0 = 300 + g * 80, 270
        if k < 4:
            p.line([(x0 + k * 12, y0), (x0 + 2 + k * 12, y0 + 60)], w=4, color=(40, 40, 120))
        else:
            p.line([(x0 - 8, y0 + 40), (x0 + 46, y0 + 20)], w=4, color=(40, 40, 120))
    x = 300 + (n // 5) * 80 + (n % 5) * 12
    K.limb(p, (x + 380, H + 80), (x + 30, 380), 80, K.narr_sleeve(), outline=4)
    p.ell(x + 20, 370, 40, 30, K.SKIN)


def s_leave(p, t, T):
    room(p, t, couch=False)
    door_right(p, t, leave=ease(t / T))
    p.poly([(720, 560), (1060, 560), (1080, 470), (700, 470)], (120, 90, 110))  # kanapa pod drzwiami
    p.rect(700, 440, 1080, 480, (110, 80, 100))
    if int(t * 4) % 2 == 0:  # szum agregatu chłodni z kuchni
        for i in range(3):
            p.line([(1200, 300 + i * 20), (1240, 296 + i * 20)], w=3, color=(150, 150, 150))


def s_thirty_eight(p, t, T):
    K.thermometer(p, t, value=38.0, rise=ease(t / (T * 0.7)))


def s_asks(p, t, T):
    room(p, t)
    k = ease(t / 0.6)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.3, -0.3), blink_k=1 - k, mouth=talk(t, T, 0.6) * 0.7, fear=0.1)


def s_mark(p, t, T):
    k = t / T
    n = 23 + (1 if k > 0.35 else 0)
    K.staff_room(p, t, marks=n)
    if k > 0.35:
        K.tally(p, 0, note=k > 0.75)
    hx, hy = (642, 270) if k < 0.6 else (600 + 40 * math.sin(t * 6), 300)
    who = "narrator" if k < 0.6 else "henryk"
    col = K.narr_sleeve() if who == "narrator" else K.WHO["henryk"]["top"]
    skin = K.SKIN if who == "narrator" else K.WHO["henryk"]["skin"]
    K.limb(p, (hx + 300, hy + 400), (hx + 20, hy + 20), 60, col, outline=4)
    p.ell(hx + 14, hy + 14, 26, 20, skin)
    p.line([(hx, hy), (hx + 8, hy + 10)], w=8, color=(236, 236, 226))  # kreda


FNS = [B.card("DZIEŃ 24"), s_shot, s_barricade, s_henryk_door, s_note_knee, s_note_cut, s_irena_sleeps, s_forty, s_leave_me, s_no,
       s_three, s_ice, s_compress, s_eyes, s_tally_blinks, s_leave, s_thirty_eight, s_asks, s_mark]
LOOK = [None] + [B.WARD] * 6 + [B.WARD] + [B.NIGHT] * 7 + [B.WARD] * 4
CAM = {18: {"zoom": 2.4, "cx": 620, "cy": 230}}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
