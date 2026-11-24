"""Wariant A · dzień 29 „Ostatnia noc” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 29
talk = K.talk
HK = K.WHO["henryk"]
KB = K.WHO["kuba"]


def lights_on(t, k=0):
    """Agregat przerywa: światło gaśnie na ułamek sekundy, nierówno."""
    return 0.0 if (t * (1.3 + 0.2 * k) + 0.37 * k) % 1 < 0.18 else 1.0


def s_blink(p, t, T):
    on = [lights_on(t, k) for k in range(4)]
    loose = 0.06 if lights_on(t) < 0.5 else 0.0  # zamki puszczają na sekundę: drzwi drgają
    R.corridor(p, t, on, doors_open=loose)
    if loose:
        for i in range(3):
            p.line([(200 + i * 400, 300), (230 + i * 400, 290)], w=4)


def s_doors(p, t, T):
    dark = lights_on(t) < 0.5
    p.rect(0, 0, W, H, (150, 166, 140) if not dark else (50, 56, 50), w=0)
    p.rect(-20, 600, W + 20, H + 20, (104, 124, 100))
    push = 14 if dark else 0
    p.rect(360, 60, 760, 640, (20, 24, 24))
    p.rect(360 + push, 60, 760 + push, 640, (124, 138, 122) if not dark else (60, 66, 60))  # skrzydło napiera
    p.rect(470 + push, 140, 650 + push, 320, (20, 24, 24))
    p.ell(560 + push, 250, 60, 72, K.ZSKIN)
    for e in (-1, 1):
        p.ell(560 + push + e * 22, 240, 10, 9, (236, 238, 226), w=2)
    p.rect(470 + push, 140, 650 + push, 320, None, w=5)
    if dark:
        for i in range(3):
            p.line([(780 + i * 26, 300 - i * 16), (810 + i * 26, 290 - i * 16)], w=4)


def s_six(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.4, -0.3), mouth=talk(t, T), fear=0.45)


def s_four(p, t, T):
    K.listening(p, t, T, who="zosia", gaze=(-0.3, 0.2), fear=0.3)


def s_pack(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    p.poly([(340, 260), (940, 260), (980, 680), (300, 680)], (70, 80, 60), w=4)  # plecak
    p.poly([(340, 260), (940, 260), (900, 200), (380, 200)], (60, 70, 52), w=4)
    k = ease(t / (T * 0.6))
    p.rect(480, 120 + 200 * k, 700, 260 + 200 * k, (40, 40, 120), w=4)  # notes
    if t > T * 0.5:
        k2 = ease((t - T * 0.5) / (T * 0.4))
        p.rect(560, 100 + 160 * k2, 820, 200 + 160 * k2, (236, 236, 230), w=3)  # przepustka Nowaka
        p.text(690, 150 + 160 * k2, "dr NOWAK", 26)
    p.poly([(300, 600), (980, 600), (980, 720), (300, 720)], (70, 80, 60), w=0, amp=0)  # przód plecaka zasłania


def s_wires(p, t, T):
    p.rect(0, 0, W, H, (40, 32, 26), w=0)  # pod klawiaturą
    p.rect(-20, -20, W + 20, 160, (84, 64, 50))
    for i in range(12):
        p.line([(80 + i * 100, 160), (80 + i * 100, 260)], w=6, color=(120, 100, 80))  # młoteczki
    p.line([(W + 20, 600), (900, 560), (720, 260)], w=6, color=(200, 60, 60))  # kabel do jednego klawisza
    p.ell(720, 250, 16, 12, (200, 180, 90), w=3)
    k = 0.5 + 0.5 * math.sin(t * 3)
    K.limb(p, (200, H + 60), (680, 330 + 20 * k), 100, KB["sleeve"], outline=4)
    p.ell(690, 320 + 20 * k, 46, 34, KB["skin"])


def s_keycap(p, t, T):
    p.rect(0, 0, W, H, (70, 52, 40), w=0)
    p.rect(-20, 300, W + 20, 620, (236, 232, 216))
    for i in range(1, 16):
        p.line([(i * 85, 300), (i * 85, 620)], w=3)
    for i in (1, 2, 4, 5, 6, 8, 9, 11, 12, 13):
        p.rect(i * 85 - 22, 300, i * 85 + 22, 480, (30, 28, 26))
    k = ease(t / (T * 0.6))
    p.rect(1020, 480, 1105, 620, (180, 170, 150), w=3)  # goła drewniana dźwignia pod zdjętą nakładką
    cx, cy = 1062 - 420 * k, 550 - 120 * k
    p.rect(cx - 42, cy - 20, cx + 42, cy + 20, (246, 244, 236), w=3)  # nakładka klawisza wędruje do Kuby
    K.limb(p, (W + 60, -60), (cx + 40, cy - 10), 90, K.SHIRT, outline=4)  # rękaw czystej koszuli Henryka
    p.ell(cx + 30, cy - 4, 40, 30, HK["skin"])
    K.limb(p, (200, H + 60), (cx - 80, cy + 60), 100, KB["sleeve"], outline=4)
    p.ell(cx - 60, cy + 40, 60, 40, KB["skin"])


def s_sandwiches(p, t, T):
    K.staff_room(p, t)
    K.figure(p, 640, K.TABLE_STAND, 0.95 * K.TABLE_S, t, "irena", look=0.0, gaze=(0.0, 0.8),
             arms={"r": (60, 120), "l": (-60, 120)})  # za stołem: stół i kanapki przed nią
    K.staff_table(p)
    n = min(6, int(t / (T * 0.7) * 7))
    for i in range(n):
        x = 380 + i * 90
        p.poly([(x - 34, 556), (x + 34, 556), (x + 28, 536), (x - 28, 536)], (220, 190, 140), w=3)


def s_shirt(p, t, T):
    K.piano_room(p, t)
    K.sitting(p, 900, 700, 0.95, t, "henryk", gaze=(-0.6, 0.0))


def s_no_words(p, t, T):
    K.piano_room(p, t)
    m = 0.3 if T * 0.3 < t < T * 0.7 else 0.0  # otwiera usta i nic nie mówi
    R.nurse_face(p, 640, 330, 1.0, 0.25 + m, t, gaze=(0.5, 0.3))


def s_breathe(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.4, 0.0), mouth=talk(t, T, speed=4) * 0.7)


def s_together(p, t, T):
    K.piano_room(p, t)
    br = math.sin(t * 2 * math.pi / 4.0)  # ten sam rytm
    K.sitting(p, 520, 700 - 4 * br, 0.95, t, "narrator", gaze=(0.6, 0.0))
    K.sitting(p, 820, 700 - 4 * br, 0.95, t, "henryk", gaze=(-0.6, 0.0))


def s_dont_look(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.5, 0.2), mouth=talk(t, T, speed=5) * 0.8)


def s_promise(p, t, T):
    K.piano_room(p, t)
    R.nurse_face(p, 640, 330, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.3, t, gaze=(0.5, 0.0))


def s_group(p, t, T):
    p.rect(0, 0, W, H, (50, 54, 56), w=0)  # korytarz parteru przy bocznych drzwiach, ciemno
    p.rect(-20, 600, W + 20, H + 20, (36, 38, 40))
    K.figure(p, 300, 880, 1.25, t, "kuba", look=0.4, arms={"r": (80, 80)})
    K.figure(p, 480, 880, 1.15, t, "irena", look=-0.2)
    K.figure(p, 800, 880, 1.25, t, "zosia", look=0.0, arms={"l": (40, 40)})
    K.sling(p, 800, 880, 1.25)
    K.figure(p, 1060, 880, 1.3, t, "narrator", look=-0.3, arms={"r": (30, 40)})
    p.text(1160, 120, "3:40", 40, fill=(200, 200, 190))


def dark_yard(q, t, lights=0.0, turn=1.4, walk=0.0):
    K.yard_view(q, t, night=True, gate_lights=lights)
    K.crowd(q, t, n=46, seed=29, turn=turn, area=(60, 1220, 320, 700), walk=walk, toward=(640, 300))


def s_window(p, t, T):
    def inner(q):  # przez szybę: dziesiątki małych postaci w ciemności, w obrębie szyby
        K.yard_view(q, t, night=True)
        K.crowd(q, t, n=40, seed=29, turn=0.6, area=(500, 780, 296, 372), smax=0.26)
    K.side_door(p, t, inner=inner, lights=False)


def s_headlights(p, t, T):
    dark_yard(p, t, lights=ease((t - 0.4) / 0.8), turn=0.8)
    p.text(1160, 80, "4:00", 40, fill=(220, 220, 210))


def s_first_step(p, t, T):
    dark_yard(p, t, lights=1.0, turn=1.4 * (1 - ease(t / (T * 0.6))), walk=0.3 * ease((t - T * 0.4) / (T * 0.6)))


def s_now(p, t, T):
    p.rect(0, 0, W, H, (30, 32, 36), w=0)
    R.nurse_face(p, 700, 230, 1.3, 0.6, t, gaze=(0.0, 0.6))
    p.rect(300, 330, 470, 720, (40, 40, 44), w=4)  # krótkofalówka przy ustach
    p.rect(330, 370, 440, 470, (90, 110, 100), w=3)
    p.line([(330, 330), (330, 200)], w=10, color=(40, 40, 44))
    K.limb(p, (200, H + 60), (390, 560), 140, K.UNI, outline=4)
    p.ell(400, 540, 80, 60, K.SKIN)
    if t > 0.5:  # wciśnięty przycisk: zielona dioda
        p.ell(420, 350, 8, 8, (120, 230, 140), w=0)


FNS = [B.card("DZIEŃ 29"), s_blink, s_doors, s_six, s_four, s_pack, s_wires, s_keycap, s_sandwiches, s_shirt, s_no_words, s_breathe,
       s_together, s_dont_look, s_promise, s_group, s_window, s_headlights, s_first_step, s_now]
LOOK = [None] + [B.NIGHT] * 2 + [B.WARD] * 12 + [B.DARK] + [B.NIGHT] * 4
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
