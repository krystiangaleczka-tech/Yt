"""Wariant A · dzień 7 „Przecięty przewód” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 7
NW = K.WHO["nowak"]
CABLE = (30, 30, 30)
COPPER = (200, 120, 60)


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def s_walk_in(p, t, T):
    K.cellar(p, t)
    k = t / T  # troje odchodzi w głąb, Nowak zostaje coraz bardziej w tyle
    for who, dx, lag in (("zosia", -150, 0.0), ("narrator", 120, 0.05), ("nowak", -20, 0.35)):
        f = max(0.0, k - lag) * (0.8 if who == "nowak" else 1.0)
        s = 1.1 - 0.55 * f
        K.figure_back(p, 640 + dx * s, 760 - 240 * f, s, t, who, walk=t * (0.5 if who == "nowak" else 0.7))


def s_nowak_wall(p, t, T):
    K.cellar(p, t)
    br = math.sin(t * 5.5)  # ciężki, szybki oddech; w połowie ujęcia osuwa się niżej po ścianie
    slide = 30 * ease((t - T * 0.5) / 0.8)
    h = K.figure(p, 980, 800 + slide, 1.1, t, "nowak", look=-0.6, lean=-0.3, mouth=0.5 + 0.3 * br,
                 arms={"r": (90, 20 + 6 * br)})
    p.ell(h["r"][0] + 10, h["r"][1], 16, 22, NW["skin"])  # dłoń oparta o ścianę


def s_cabinet(p, t, T):
    sp = 1.0 if T * 0.4 < t < T * 0.4 + 0.15 else (0.6 if T * 0.75 < t < T * 0.75 + 0.1 else 0.0)
    K.switch_room(p, t, spark=sp)


def cable_cut(p, t, gap):
    p.rect(0, 0, W, H, (60, 64, 64), w=0)
    for side in (-1, 1):
        x0 = 640 + side * gap
        p.rect(min(x0, x0 + side * 900), 300, max(x0, x0 + side * 900), 420, CABLE)
        p.ell(x0, 360, 18, 60, (40, 40, 40))
        for k in range(5):
            p.ell(x0 + side * 4, 318 + k * 21, 7, 7, COPPER, w=1.5)


def s_cut(p, t, T):
    cable_cut(p, t, 46)
    if (t % 0.9) < 0.12:  # resztka napięcia: mała iskra między żyłami
        p.line([(600, 350), (640, 330), (680, 370)], w=4, color=(250, 240, 160))


def s_cutters(p, t, T):
    p.rect(0, 0, W, H, (70, 72, 70), w=0)
    k = ease((t - 0.3) / 0.7)  # latarka sunie po podłodze i trafia na nożyce
    lx = 200 + 440 * k
    p.glow([(lx - 260, 220), (lx + 260, 220), (lx + 220, 520), (lx - 220, 520)], (255, 240, 170, 50))
    for side in (-1, 1):
        p.poly([(640, 370), (900, 370 + side * 60), (910, 380 + side * 60), (650, 384)], (150, 30, 30))
        p.poly([(640, 376), (380, 330 + side * 30), (370, 344 + side * 30), (640, 390)], (130, 130, 136))
    p.ell(640, 380, 16, 16, (90, 90, 90))
    p.rect(760, 400, 880, 440, (236, 232, 214), w=2)
    p.text(820, 420, "WARSZTAT", 16)


def s_realize(p, t, T):
    p.rect(0, 0, W, H, (60, 64, 64), w=0)
    k = ease((t - T * 0.35) / 0.6)  # podnosi wzrok znad kabla
    R.nurse_face(p, 640, 320, 1.0, 0.35 + 0.3 * k, t, gaze=(0.0, 0.9 - 1.2 * k))


def s_ask(p, t, T):
    K.cellar(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.8, 0.0))


def s_nowak_keys(p, t, T):
    K.cellar(p, t)
    k = ease((t - T * 0.7) / 0.4)  # na „lekarz dyżurny” wzrok mu ucieka
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(-0.2 - 0.6 * k, 0.6 * k), mouth=talk(t, T * 0.85), fear=0.3)


def s_sleeve(p, t, T):
    p.rect(0, 0, W, H, (60, 64, 64), w=0)
    grip = ease((t - 0.3) / 0.5)  # palce zaciskają się na rękawie
    K.limb(p, (-80, 560), (760, 420), 200, NW["top"], outline=4)  # rękaw fartucha
    p.ell(720, 420 + 20 * grip, 120, 90 - 20 * grip, NW["skin"])
    for i in range(4):
        x = 650 + i * 46
        p.line([(x, 360 + 30 * grip), (x + 6, 460)], w=3)
    for k in range(5):  # fałdy materiału ściągane palcami
        p.line([(560 - k * 30, 360 + 20 * grip), (600 - k * 30, 480 - 10 * grip)], w=2.5, color=(170, 170, 166))


def s_nowak_dead(p, t, T):
    K.cellar(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(0.0, 0.7), mouth=talk(t, T), fear=0.45)


def s_zosia_look(p, t, T):
    K.cellar(p, t)
    k = ease((t - T * 0.3) / 0.5)  # Zosia przenosi wzrok z narratora na Nowaka i zostaje
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.7 * k - 0.4 * (1 - k), 0.0), fear=0.2 * k)


def s_notes(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    K.paper(p, 600, 340, ["technik", "ochrona", "lekarz dyżurny"], w=500, h=260)
    for i in range(2):  # krzyżyki przy dwóch pierwszych; trzeci zostaje pusty
        x, y = 820, 260 + i * 54
        p.line([(x - 14, y - 14), (x + 14, y + 14)], w=4, color=(170, 40, 40))
        p.line([(x + 14, y - 14), (x - 14, y + 14)], w=4, color=(170, 40, 40))
    k = ease((t - 0.4) / 0.8)  # długopis zawisa nad trzecim nazwiskiem
    K.limb(p, (1300, 700), (880, 400 - 20 * k), 70, NW["top"], outline=4)
    p.ell(870, 395 - 20 * k, 34, 26, NW["skin"])
    p.line([(860, 380 - 20 * k), (836, 360 - 20 * k)], w=6, color=(40, 40, 120))


def s_back_walk(p, t, T):
    K.cellar(p, t)
    k = t / T  # wracają w stronę kamery
    for who, dx, lag in (("zosia", -90, 0.0), ("narrator", 40, 0.1), ("nowak", 150, 0.25)):
        f = min(1.0, max(0.0, k - lag) * 1.1)
        s = 0.55 + 0.4 * f
        K.figure(p, 640 + dx * s, 520 + 200 * f, s, t, who, walk=t * 0.6, look=-0.2)


def s_pipes_shake(p, t, T):
    p.rect(0, 0, W, H, (58, 62, 66), w=0)
    for k, (y, wd) in enumerate(((150, 60), (300, 46), (430, 70))):
        hit = (t * 3.1 + k * 0.37) % 1.0 < 0.16  # nierówne stuki, każda rura drga w innej chwili
        dy = 4 * math.sin(t * 80) if hit else 0
        p.rect(-20, y + dy, W + 20, y + wd + dy, (110 + k * 6, 104, 96))
        for x in range(80, W, 260):
            p.rect(x, y - 10 + dy, x + 30, y + wd + 10 + dy, (90, 90, 88))
        if hit:
            p.ell(300 + k * 300, y + wd + 10, 3, 3, (170, 170, 160), w=0)


def s_under_pipes(p, t, T):
    K.cellar(p, t)
    up = ease((t - 0.2) / 0.5)
    K.figure(p, 480, 760, 1.0, t, "zosia", look=0.3, gaze=(0.3, -1.0 * up), mouth=talk(t, T, 0.6, 0.5),
             arms={"r": (40, 95 - 160 * up)})
    K.figure(p, 820, 760, 1.0, t, "nowak", look=-0.2, gaze=(0.0, -1.0 * ease((t - 0.6) / 0.5)))


def pipe_vertical(p):
    p.rect(470, -20, 560, H + 20, (110, 104, 96))
    for y in (120, 520):
        p.rect(458, y, 572, y + 30, (90, 90, 88))


def s_ear(p, t, T):
    p.rect(0, 0, W, H, (58, 62, 66), w=0)
    lean = ease(t / 0.6)  # przykłada ucho do rury
    R.nurse_face(p, 760 - 80 * lean, 330, 1.0, 0.4, t, gaze=(-0.6, 0.0), body=(760, 330))
    pipe_vertical(p)


def s_key_tap(p, t, T):
    p.rect(0, 0, W, H, (58, 62, 66), w=0)
    p.rect(-20, 300, W + 20, 420, (110, 104, 96))
    hit = [0.5, 0.95]
    k = min(abs(t - h) for h in hit)
    lift = min(1.0, k / 0.18)  # klucz uderza dwa razy
    K.limb(p, (1300, 760), (740, 230 - 60 * lift), 110, K.narr_sleeve(), outline=4)
    p.ell(720, 230 - 60 * lift, 60, 46, K.SKIN)
    p.rect(640, 260 - 60 * lift, 700, 296 - 60 * lift, (170, 170, 176), w=3)
    if k < 0.08:
        for i in range(3):
            p.line([(600 - i * 30, 300 - 20 * i), (580 - i * 30, 270 - 20 * i)], w=3)


def s_wait(p, t, T):
    p.rect(0, 0, W, H, (58, 62, 66), w=0)
    R.nurse_face(p, 680, 330, 1.0, 0.45, t, gaze=(-0.4, 0.0), blink_k=0.0)  # nie mruga, czeka
    pipe_vertical(p)


def s_answer(p, t, T):
    p.rect(0, 0, W, H, (58, 62, 66), w=0)
    for k, h in enumerate((0.7, 1.15)):  # dwa stuknięcia z daleka: rura drga dwa razy
        if h < t < h + 0.14:
            dy = 4 * math.sin(t * 90)
            break
    else:
        dy = 0
    p.rect(-20, 300 + dy, W + 20, 420 + dy, (110, 104, 96))
    for x in range(80, W, 260):
        p.rect(x, 290 + dy, x + 30, 430 + dy, (90, 90, 88))
    if dy:
        p.ell(1000, 440, 3, 3, (170, 170, 160), w=0)


def s_zosia_go(p, t, T):
    K.cellar(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.0, 0.0), mouth=talk(t, T, 0.5, 0.6), fear=0.1)


def s_three_look(p, t, T):
    K.pharmacy_inside(p, t)
    turn = [ease((t - d) / 0.4) for d in (0.3, 0.55, 0.8)]  # odwracają się do Henryka, każde w swoim czasie
    K.figure(p, 300, 760, 1.0, t, "zosia", look=0.6 * turn[0], gaze=(0.8 * turn[0], 0.0))
    K.figure(p, 520, 760, 1.0, t, "narrator", look=0.6 * turn[1], gaze=(0.8 * turn[1], 0.0))
    K.figure(p, 720, 760, 1.0, t, "nowak", look=0.5 * turn[2], gaze=(0.8 * turn[2], 0.0))
    K.figure(p, 1060, 760, 1.0, t, "henryk", look=-0.5)


def s_henryk_nod(p, t, T):
    K.pharmacy_front(p, t)
    nod = 14 * max(0.0, math.sin((t - 0.7) * 3.0)) if 0.7 < t < 0.7 + math.pi / 3.0 else 0.0
    K.face_cu(p, 640, 330 + nod, 1.0, "henryk", t, gaze=(0.0, 0.2 + nod / 30))


def s_pack(p, t, T):
    K.pharmacy_inside(p, t, flick=0.85)
    k = t / T  # Zosia wkłada do torby kolejne latarki i bandaże
    reach = math.sin(min(1.0, k * 3 % 1.0) * math.pi)
    K.figure(p, 160, 600, 0.8, t, "zosia", look=0.5, gaze=(0.4, 1.0), arms={"r": (60 + 40 * reach, 30 + 30 * reach)})
    p.rect(-20, 430, 270, 600, (128, 98, 70))
    p.line([(-20, 430), (270, 430)], w=4)
    p.poly([(120, 400), (240, 400), (250, 440), (110, 440)], (100, 70, 50), w=3)  # torba na ladzie
    for i in range(min(4, 1 + int(k * 4))):
        p.rect(130 + i * 26, 386, 146 + i * 26, 402, (60, 60, 60) if i % 2 else (240, 238, 228), w=2)


FNS = [B.card("DZIEŃ 7"), s_walk_in, s_nowak_wall, s_cabinet, s_cut, s_cutters, s_realize, s_ask, s_nowak_keys,
       s_sleeve, s_nowak_dead, s_zosia_look, s_notes, s_back_walk, s_pipes_shake, s_under_pipes, s_ear, s_key_tap,
       s_wait, s_answer, s_zosia_go, s_three_look, s_henryk_nod, s_pack]
LOOK = [None] + [B.BASE] * 20 + [B.WARD] * 3
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
