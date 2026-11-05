"""Wariant A · dzień 12 „Plan agregatu” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 12
NW = K.WHO["nowak"]
INK_BLUE = (40, 40, 90)
ROOMS = ((260, 180, 520, 320, "APTEKA"), (560, 160, 820, 300, "AGREGAT"), (300, 380, 600, 560, "ROZDZIELNIA"),
         (680, 380, 1000, 560, "ODDZIAŁ C"), (860, 160, 1040, 300, "PRALNIA"))


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def plan(p):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    p.poly([(200, 120), (1080, 100), (1100, 620), (180, 640)], (236, 232, 214), w=4)
    for (x0, y0, x1, y1, txt) in ROOMS:
        p.rect(x0, y0, x1, y1, None, w=3, color=INK_BLUE)
        p.text((x0 + x1) / 2, (y0 + y1) / 2, txt, 22, fill=INK_BLUE)


def finger(p, x, y, who="narrator"):
    c = K.WHO[who]
    sleeve = K.narr_sleeve() if who == "narrator" else c["sleeve"]
    K.limb(p, (x + 380, H + 100), (x + 40, y + 60), 100, sleeve, outline=4)
    p.ell(x + 40, y + 50, 50, 38, c["skin"])
    p.line([(x + 20, y + 30), (x - 6, y - 4)], w=16, color=c["skin"])
    p.line([(x + 20, y + 30), (x - 6, y - 4)], w=2.5)


def s_megaphone(p, t, T):
    def inner(q):
        q.rect(0, 0, W, H, (170, 176, 176), w=0)
        q.poly([(0, 420), (W, 400), (W, H), (0, H)], (98, 110, 88))
        if int(t * 3) % 2 == 0:  # megafon za płotem — fale dźwięku
            for k in range(3):
                q.ell(900, 380, 40 + 30 * k, 24 + 18 * k, None, w=2)
    K.basement_window(p, inner)


def s_cough(p, t, T):
    K.pharmacy_front(p, t)
    c = 12 * math.sin(t * 25) if (t % 1.4) < 0.5 else 0  # ataki kaszlu
    K.face_cu(p, 640, 330 + c * 0.4, 1.0, "irena", t, gaze=(0.0, 0.6), mouth=0.7 if c else 0.0, fear=0.3)
    p.ell(600, 418, 30, 8, (120, 110, 150), w=2)  # sine usta


def s_zosia(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.5, 0.2), mouth=talk(t, T), fear=0.3)


def s_plan_gen(p, t, T):
    plan(p)
    k = ease((t - 0.2) / 0.7)
    finger(p, 400 + 290 * k, 300 - 70 * k)  # palec jedzie od apteki do agregatu


def s_plan_rooms(p, t, T):
    plan(p)
    n = min(4, int(t / (T * 0.8) * 4) + 1)  # sale zakreślane jedna po drugiej
    for i in range(n):
        x = 700 + i * 70
        p.line([(x, 400), (x + 50, 540)], w=4, color=(170, 40, 40))
        p.line([(x + 50, 400), (x, 540)], w=4, color=(170, 40, 40))


def s_nowak_up(p, t, T):
    K.pharmacy_front(p, t)
    up = ease(t / 0.3)
    K.face_cu(p, 640, 360 - 30 * up, 1.0, "nowak", t, gaze=(-0.4, -0.2 * up), mouth=talk(t, T, 0.4), fear=0.5)


def s_zosia_asks(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.8, 0.0), mouth=talk(t, T), fear=0.1)


def s_nowak_down(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - 0.2) / 0.5)
    K.face_cu(p, 640, 330 + 12 * k, 1.0, "nowak", t, gaze=(0.0, 0.9 * k), mouth=talk(t, T, 0.6), fear=0.6)


def s_route(p, t, T):
    plan(p)
    k = ease((t - 0.2) / (T * 0.7))  # narrator rysuje trasę ołówkiem
    pts = [(390, 320), (450, 470), (640, 470), (690, 300)]
    seg = k * 3
    drawn = [pts[0]]
    for i in range(3):
        f = min(1.0, max(0.0, seg - i))
        if f > 0:
            a, b = pts[i], pts[i + 1]
            drawn.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    p.line(drawn, w=5, color=(170, 40, 40))
    for i in range(3):  # trzech w korytarzu rozdzielni
        p.ell(470 + i * 40, 500, 10, 10, (170, 40, 40), w=2)
    finger(p, drawn[-1][0], drawn[-1][1])


def s_kuba(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(-0.3, 0.0), mouth=talk(t, T), fear=0.05)


def s_chute_plan(p, t, T):
    plan(p)
    p.line([(930, 120), (930, 160)], w=10, color=INK_BLUE)  # zsyp z C do pralni
    k = ease((t - 0.2) / 0.6)
    finger(p, 940 - 40 * k, 120 + 80 * k, "henryk")


def s_trays(p, t, T):
    K.pharmacy_inside(p, t)
    p.poly([(520, 520), (760, 520), (780, 640), (500, 640)], (176, 158, 120), w=4)  # worek
    for who, x, side in (("narrator", 400, 1), ("kuba", 880, -1)):
        reach = math.sin(t * 3 + x) * 0.5 + 0.5
        K.figure(p, x, 760, 1.0, t, who, look=0.5 * side, gaze=(0.6 * side, 0.8), arms={"r" if side > 0 else "l": (side * (80 + 40 * reach), 130)})
    if int(t * 3) % 2 == 0:
        p.rect(600, 480, 700, 500, (190, 194, 198), w=2)  # tacka wpada do worka


def s_sew(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    p.poly([(200, 260), (1080, 240), (1100, 560), (180, 580)], (176, 158, 120), w=4)
    n = int(t / T * 14)
    for i in range(n):  # ścieg rośnie
        x = 260 + i * 56
        p.line([(x, 400), (x + 30, 430)], w=4, color=(60, 40, 30))
    x = 260 + n * 56
    p.line([(x, 360), (x + 20, 460)], w=3, color=(200, 200, 200))  # igła
    K.limb(p, (x + 360, H + 60), (x + 40, 470), 80, K.WHO["irena"]["sleeve"], outline=4)
    p.ell(x + 30, 460, 40, 30, K.WHO["irena"]["skin"])


def s_no_food(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 300, 1.0, "nowak", t, gaze=(0.0, 0.8), fear=0.5)
    p.ell(640, 650, 120, 30, (220, 220, 214), w=4)  # nietknięta miska
    p.ell(640, 642, 90, 18, (170, 130, 90))
    for side in (-1, 1):
        K.limb(p, (640 + side * 280, H + 60), (640 + side * 140, 600), 110, NW["top"], outline=4)
        p.ell(640 + side * 140, 600, 56, 40, NW["top"], w=4)  # dłonie w rękawach


def s_temp(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    K.sitting(p, 800, 690, 0.9, t, "nowak", eyes=0.0)
    k = ease((t - 0.2) / 0.6)  # Zosia wsuwa mu termometr pod pachę
    K.figure(p, 520, 760, 1.0, t, "zosia", look=0.6, gaze=(0.6, 0.8), arms={"r": (80 + 60 * k, 140)})


def s_thermo(p, t, T):
    K.thermometer(p, t, 39.0, rise=ease(t / (T * 0.7)))


def s_whisper(p, t, T):
    p.rect(0, 0, W, H, (30, 34, 40), w=0)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.8, 0.0), mouth=talk(t, T) * 0.5, fear=0.4)


def s_keys(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 48), w=0)
    p.rect(-20, 120, W + 20, 300, NW["top"])  # fartuch śpiącego
    p.rect(-20, 290, W + 20, 340, (60, 60, 60))  # pasek
    sway = 6 * math.sin(t * 2)
    p.ell(560, 360, 44, 44, None, w=8, color=(170, 170, 160))
    for i, a in enumerate((-0.6, -0.2, 0.25)):
        x, y = 560 + 300 * math.sin(a) + sway, 390 + 260 * math.cos(a)
        p.line([(560, 400), (x, y)], w=16, color=(170, 170, 160))
        p.line([(560, 400), (x, y)], w=2.5)
    k = ease((t - 0.3) / 0.5)  # latarka trafia na żółtą przywieszkę
    p.glow([(600, 330), (1100, 330), (1100, 720), (600, 720)], (255, 240, 170, int(70 * k)))
    tx, ty = 820 + sway, 520
    p.line([(640, 470), (tx - 80, ty - 40)], w=4)
    p.poly([(tx - 120, ty - 70), (tx + 120, ty - 80), (tx + 130, ty + 70), (tx - 110, ty + 80)], (230, 200, 40), w=4)
    p.text(tx, ty, "ROZDZIELNIA", 30, fill=(40, 30, 10))


def s_looks(p, t, T):
    p.rect(0, 0, W, H, (30, 34, 40), w=0)
    k = ease((t - 0.3) / 0.8)
    R.nurse_face(p, 640, 320, 1.0, 0.3 + 0.35 * k, t, gaze=(0.7, 0.4 - 0.4 * k))


FNS = [B.card("DZIEŃ 12"), s_megaphone, s_cough, s_zosia, s_plan_gen, s_plan_rooms, s_nowak_up, s_zosia_asks, s_nowak_down,
       s_route, s_kuba, s_chute_plan, s_trays, s_sew, s_no_food, s_temp, s_thermo, s_whisper, s_keys, s_looks]
LOOK = [None] + [B.BASE] * 14 + [B.NIGHT] * 5
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
