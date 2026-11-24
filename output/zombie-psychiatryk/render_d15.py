"""Wariant A · dzień 15 „Cisza po alarmie” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import random
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 15
NW = K.WHO["nowak"]


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def s_morning(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    hit = (t % 1.6) < 0.15  # raz po raz uderzenie w drzwi sali
    if hit:
        for k in range(3):
            p.line([(240, 380 + k * 40), (200, 370 + k * 40)], w=3)


def s_losses(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    lines = ["woda: połowa", "latarka", "bandaże"]
    n = min(3, int(t / (T * 0.7) * 3) + 1)
    K.paper(p, 600, 340, lines[:n], w=480, h=260, hand=True)


def s_stitches(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    K.limb(p, (-80, 600), (760, 420), 160, K.WHO["kuba"]["sleeve"], outline=4)
    p.ell(820, 400, 110, 80, K.WHO["kuba"]["skin"])
    p.line([(760, 380), (900, 430)], w=4, color=(170, 40, 40))
    n = int(t / T * 6)  # kolejne szwy
    for i in range(n):
        x = 770 + i * 22
        p.line([(x, 370 + i * 8), (x + 10, 400 + i * 8)], w=3, color=(30, 30, 60))
    x = 770 + n * 22  # igła w palcach Zosi
    K.limb(p, (W + 100, H + 60), (x + 60, 460 + n * 8), 80, K.WHO["zosia"]["sleeve"], outline=4)
    p.ell(x + 40, 450 + n * 8, 40, 30, K.WHO["zosia"]["skin"])


def s_irena_calm(p, t, T):
    K.pharmacy_front(p, t)
    br = math.sin(t * 2 * math.pi / 4)  # spokojny, równy oddech
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(0.2, 0.1), breath=br * 2, fear=0.0)


def s_megaphone(p, t, T):
    def inner(q):
        q.rect(0, 0, W, H, (190, 200, 206), w=0)
        q.poly([(0, 420), (W, 400), (W, H), (0, H)], (98, 110, 88))
        if int(t * 3) % 2 == 0:
            for k in range(3):
                q.ell(900, 380, 40 + 30 * k, 24 + 18 * k, None, w=2)
    K.basement_window(p, inner)


def s_move(p, t, T):
    K.staff_room(p, t)
    k = t / T  # grupa wnosi rzeczy: każdy w swoim tempie
    for who, x0, lag in (("zosia", -100, 0.0), ("kuba", -260, 0.2), ("irena", -420, 0.4)):
        f = max(0.0, k - lag)
        K.figure(p, x0 + 900 * f, 780, 0.95, t * 0.6, who, walk=t * 0.6, look=0.6)


def s_warm_water(p, t, T):
    K.bathroom(p, t)
    p.rect(560, 260, 720, 300, (170, 176, 180), w=3)
    p.line([(640, 300), (640, 500)], w=14, color=(170, 200, 220))
    for i in range(6):  # para
        y = 480 - ((t * 60 + i * 50) % 300)
        p.ell(600 + 20 * math.sin(t + i) + i * 10, y, 30 + i * 4, 14, None, w=2, color=(240, 240, 240))
    for side in (-1, 1):  # dłonie pod strumieniem
        p.ell(640 + side * 60, 520, 60, 36, K.SKIN)


def s_pocket(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    p.rect(300, 300, 900, 720, K.UNI, w=4)  # kieszeń mundurka
    p.line([(300, 380), (900, 380)], w=4)
    k = ease((t - 0.2) / 0.6)  # przepustka znika w kieszeni
    y = 200 + 260 * k
    p.rect(480, y - 80, 720, y + 80, (236, 232, 214), w=3)
    p.text(600, y - 30, "dr J. NOWAK", 22)
    p.rect(300, 380, 900, 720, K.UNI, w=0, amp=0)
    p.rect(300, 380, 900, 720, None, w=4)
    # dłoń trzyma górną krawędź przepustki i wpycha ją do kieszeni, potem odchodzi w górę — z ręką, nie sama
    # (przegląd 13.11.2026: dłoń bez ręki zostawała na kieszeni)
    away = ease((t - 0.95) / 0.5)
    hx, hy = 640 + 360 * away, y - 92 - 380 * away
    K.limb(p, (W + 140, -160), (hx + 20, hy - 10), 90, K.narr_sleeve(), outline=4)
    p.ell(hx, hy, 52, 38, K.SKIN)


def s_aside(p, t, T):
    K.staff_room(p, t)
    K.figure(p, 560, 780, 1.05, t, "narrator", look=0.5, mouth=talk(t, T))
    K.figure(p, 780, 780, 1.05, t, "zosia", look=-0.5)


def s_zosia_fever(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.5, 0.2), mouth=talk(t, T), fear=0.3)


def s_put_pass(p, t, T):
    p.rect(0, 0, W, H, (190, 186, 170), w=0)  # blat przy kuchence
    k = ease((t - 0.1) / 0.5)
    x = 1100 - 460 * k
    p.rect(x - 120, 260, x + 120, 420, (236, 232, 214), w=3)
    p.text(x, 320, "dr J. NOWAK", 26)
    K.limb(p, (x + 600, H + 60), (x + 100, 400), 110, K.UNI, outline=4)
    p.ell(x + 90, 390, 56, 40, K.SKIN)


def s_silent(p, t, T):
    K.staff_room(p, t)
    k = ease((t - T * 0.6) / 0.4)  # długo milczy, potem odpowiada
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.0, 0.8 - 0.7 * k), mouth=talk(t, T, T * 0.6) * k, fear=0.4)


def s_narrator_point(p, t, T):
    K.staff_room(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.7, 0.0))


def s_henryk_window(p, t, T):
    K.staff_room(p, t)
    K.sitting(p, 980, 690, 0.8, t, "nowak", eyes=0.0)  # śpi na kanapie (z prawej)
    K.figure(p, 230, 760, 1.0, t, "henryk", look=0.8, gaze=(1.0, 0.2))  # przy oknie, nie odrywa wzroku


def s_tally(p, t, T):
    p.rect(0, 0, W, H, (70, 72, 74), w=0)
    for g in range(3):
        for i in range(4):
            x = 200 + g * 280 + i * 44
            p.line([(x, 220), (x + 4, 440)], w=8, color=(236, 236, 226))
        p.line([(180 + g * 280, 380), (360 + g * 280, 300)], w=8, color=(236, 236, 226))
    k = ease(t / (T * 0.5))  # piętnasta kreska — ostatnia w trzeciej piątce
    p.line([(740, 380), (740 + 180 * k, 380 - 80 * k)], w=0.1, color=(70, 72, 74))


def s_nowak_rises(p, t, T):
    K.staff_room(p, t, lights=False, night=True)
    k = ease((t - 0.3) / (T * 0.6))
    if k < 0.4:
        K.sitting(p, 980, 690, 0.8, t, "nowak")
    else:
        K.figure_back(p, 980 - 300 * (k - 0.4), 760, 0.95, t * 0.4, "nowak", walk=t * 0.4)


def s_crack(p, t, T):
    p.rect(0, 0, W, H, (20, 22, 24), w=0)
    p.rect(560, -20, 720, H + 20, (190, 196, 196))  # szpara w drzwiach łazienki — tylko w niej widać
    def inside(q):
        roll = ease((t - 0.3) / 0.8)
        K.limb(q, (560, 260), (700, 480), 90, NW["top"], outline=4)
        q.rect(600, 380 - 60 * roll, 720, 400 - 60 * roll, NW["top"], w=3)  # podwijany rękaw
        q.ell(700, 480, 40, 30, NW["skin"])
    inside(p)
    p.rect(-20, -20, 560, H + 20, (20, 22, 24), w=0, amp=0)
    p.rect(720, -20, W + 20, H + 20, (20, 22, 24), w=0, amp=0)
    p.rect(560, -20, 720, H + 20, None, w=3)


def s_bite(p, t, T):
    p.rect(0, 0, W, H, (160, 170, 170), w=0)
    K.limb(p, (-80, 520), (W + 80, 300), 260, NW["skin"], outline=4)
    p.ell(640, 410, 150, 90, (110, 90, 120), w=0)  # sina opuchlizna
    for i in range(7):  # odcisk zębów
        a = math.pi * (0.1 + 0.8 * i / 6)
        for r in (110, 70):
            p.ell(640 + r * math.cos(a), 410 - 0.5 * r * math.sin(a) * (1 if r == 110 else -1), 9, 6, (80, 40, 50), w=0)
    k = ease(t / T)
    p.ell(640, 410, 150 * (0.95 + 0.05 * k), 90, None, w=3, color=(60, 30, 40))


def s_spirit(p, t, T):
    p.rect(0, 0, W, H, (160, 170, 170), w=0)
    pain = ease((t - 0.4) / 0.3)  # zaciska zęby na ręczniku, oczy się zamykają
    K.face_cu(p, 640, 320, 1.0, "nowak", t, gaze=(0.0, 0.0), blink_k=0.8 * pain, fear=0.6 + 0.3 * pain)
    p.poly([(520, 410), (760, 400), (770, 440), (510, 450)], (236, 236, 232), w=3)  # ręcznik w zębach


def s_back_off(p, t, T):
    p.rect(0, 0, W, H, (18, 20, 22), w=0)
    k = ease(t / (T * 0.6))
    K.figure_back(p, 560, 760 + 40 * k, 1.05 + 0.1 * k, t, "narrator")
    if k > 0.6:  # za nim, w ciemności, wynurza się Henryk
        a = (k - 0.6) / 0.4
        K.figure(p, 880, 760, 1.05, t, "henryk", look=-0.4, gaze=(-0.8, 0.0))
        p.rect(800, -20, W + 20, H + 20, (18, 20, 22), w=0, amp=0) if a < 0.3 else None


def s_henryk_saw(p, t, T):
    p.rect(0, 0, W, H, (18, 20, 22), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.4, 0.0))


FNS = [B.card("DZIEŃ 15"), s_morning, s_losses, s_stitches, s_irena_calm, s_megaphone, s_move, s_warm_water, s_pocket,
       s_aside, s_zosia_fever, s_put_pass, s_silent, s_narrator_point, s_henryk_window, s_tally, s_nowak_rises, s_crack,
       s_bite, s_spirit, s_back_off, s_henryk_saw]
LOOK = [None] + [B.WARD] * 14 + [B.NIGHT] * 7
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
