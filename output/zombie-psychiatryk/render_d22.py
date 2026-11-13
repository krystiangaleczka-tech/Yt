"""Wariant A · dzień 22 „Woda” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 22
talk = K.talk
CAN = (70, 110, 150)  # niebieskie kanistry z dnia 11


def canister(p, x, y, s=1.0, col=CAN):
    p.rect(x - 40 * s, y - 100 * s, x + 40 * s, y, col, w=3)
    p.rect(x - 14 * s, y - 120 * s, x + 14 * s, y - 100 * s, col, w=3)


def s_tap(p, t, T):
    p.rect(0, 0, W, H, (196, 210, 210), w=0)
    for x in range(0, W, 64):
        p.line([(x, 0), (x, H)], w=1.5, color=(150, 166, 166), amp=0.4)
    p.rect(560, 140, 720, 220, (180, 184, 186), w=4)  # kran
    p.rect(680, 200, 720, 300, (180, 184, 186), w=4)
    k = t / T
    flow = max(0.0, 1 - k * 1.3)
    if flow > 0:
        p.line([(700, 300), (700, 300 + 380 * flow)], w=4 + 16 * flow, color=(130, 90, 50))  # brązowa ciecz
    elif int(t * 5) % 3 == 0:
        p.ell(700, 320 + (t * 200) % 200, 6, 8, (130, 90, 50), w=0)  # ostatnie krople
    if k > 0.5 and int(t * 8) % 2 == 0:  # charczenie powietrza
        for i in range(3):
            p.line([(740 + i * 24, 280 - i * 14), (770 + i * 24, 270 - i * 14)], w=4)
    p.rect(420, 600, 860, H + 20, (220, 224, 224), w=4)  # zlew


def s_count(p, t, T):
    K.staff_room(p, t)
    K.figure(p, 640, K.TABLE_STAND, 1.0 * K.TABLE_S, t, "zosia", look=0.0, gaze=(0.0, 0.8), mouth=talk(t, T))  # za stołem
    K.staff_table(p)
    n = min(6, int(t / (T * 0.7) * 7))  # przesuwa butelki, licząc
    for i in range(6):
        x = 360 + i * 60 + (30 if i < n else 0)
        p.rect(x - 14, 480, x + 14, 560, (180, 210, 220), w=3)
    for i in range(2):
        canister(p, 820 + i * 100, 560, 0.7)


def s_tank_idea(p, t, T):
    K.staff_room(p, t)
    R.nurse_face(p, 640, 330, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(-0.2, -0.7))  # patrzy w sufit


def s_irena_fever(p, t, T):
    K.staff_room(p, t)
    K.irena_lying(p, t)
    k = ease((t - 0.3) / 0.8)
    K.figure(p, 220, 780, 1.0, t, "henryk", look=0.6, gaze=(0.6, 0.8), arms={"r": (60 + 150 * k, 150 - 30 * k)})


def s_top_floor(p, t, T):
    hit = [1.0 if (t * (1.5 + 0.4 * k) + k) % 1 < 0.3 else 0.0 for k in range(4)]
    R.corridor(p, t, [1, 1, 0, 1], doors_open=0.0)
    for k, (x, y) in enumerate(((150, 300), (1130, 300), (330, 330), (950, 330))):  # drzwi sal drżą od uderzeń
        if hit[k]:
            for i in range(3):
                p.line([(x + i * 12, y - 30 + i * 16), (x + 30 + i * 12, y - 36 + i * 16)], w=4)
    k = t / T
    for who, x in (("narrator", 560), ("kuba", 760)):
        K.figure_back(p, x, 800 - 60 * k, 1.0 - 0.15 * k, t * 0.7, who, walk=t * 0.7, arms={"r": (40, 130)})
        canister(p, x + 66 - 6 * k, 800 - 60 * k - 120, 0.5)


def s_hatch(p, t, T):
    p.rect(0, 0, W, H, (60, 66, 64), w=0)
    p.rect(-20, -20, W + 20, 200, (70, 76, 74))
    k = ease((t - 0.3) / 0.8)
    p.rect(460, 60, 820, 200, (40, 44, 44))
    p.rect(460, 60 + 140 * k, 820, 200, (220, 230, 236) if k > 0.1 else (40, 44, 44), w=0)  # niebo przez klapę
    p.poly([(460, 60), (820, 60), (820 - 40 * k, 60 - 150 * k), (460 + 40 * k, 60 - 150 * k)], (110, 110, 108), w=4)
    if k > 0.1:
        p.glow([(460, 200), (820, 200), (980, H), (300, H)], (240, 246, 250, int(60 * k)))
    for i in range(8):  # drabina
        p.line([(560, 220 + i * 70), (720, 220 + i * 70)], w=6)
    p.line([(560, 200), (560, H + 20)], w=8)
    p.line([(720, 200), (720, H + 20)], w=8)
    K.figure_back(p, 640, 760, 1.0, t, "kuba", arms={"l": (-30, -200 + 40 * k), "r": (30, -220 + 40 * k)})


def s_city(p, t, T):
    K.roof(p, t, dusk=0.1, fire=1.0)


def s_fill(p, t, T):
    K.roof(p, t, dusk=0.15)
    dip = 30 * math.sin(min(1.0, t / T) * math.pi)
    K.figure(p, 800, 640, 0.9, t, "narrator", look=0.6, arms={"r": (130, 60 + dip)})
    canister(p, 940, 470 + dip, 0.55)
    if dip > 10:
        for i in range(4):
            p.ell(920 + i * 18, 236 - (t * 40 + i * 9) % 30, 6, 4, (180, 210, 230), w=2)


def s_kuba_city(p, t, T):
    p.rect(0, 0, W, H, (170, 186, 196), w=0)
    for i, cx in enumerate((200, 1080)):
        p.glow([(cx - 160, 200), (cx + 160, 200), (cx + 160, 420), (cx - 160, 420)], (255, 140, 60, 40))
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(-0.7, -0.1), mouth=talk(t, T), fear=0.3)


def s_first_out(p, t, T):
    p.rect(0, 0, W, H, (170, 186, 196), w=0)
    R.nurse_face(p, 640, 330, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.6, 0.1))


def s_rope(p, t, T):
    p.rect(0, 0, W, H, (150, 160, 166), w=0)  # pod krawędzią dachu: ściana i rynna
    p.rect(-20, -20, W + 20, 220, (90, 90, 92))
    p.rect(-20, 200, W + 20, 260, (150, 150, 146), w=4)  # rynna
    sw = 14 * math.sin(t * 3.5)
    p.line([(640, -20), (640 + sw * 0.2, 230), (650 + sw, 600)], w=6, color=(200, 180, 130))
    canister(p, 650 + sw, 720, 0.9)
    if int(t * 6) % 2 == 0:  # lina szoruje o rynnę
        for i in range(3):
            p.line([(600 - i * 30, 190 - i * 10), (570 - i * 30, 180 - i * 10)], w=4)


def s_faces_up(p, t, T):
    p.rect(0, 0, W, H, (40, 52, 40), w=0)  # podwórze z góry
    for i in range(14):
        x = 120 + (i * 173) % 1080
        y = 120 + (i * 97) % 500
        k = ease((t - (i % 5) * 0.25) / 0.6)  # twarze podnoszą się jedna po drugiej
        p.ell(x, y + 30, 60, 40, (150, 160, 152))  # barki
        p.ell(x, y, 34, 34 * (0.5 + 0.5 * k), K.ZSKIN)
        if k > 0.5:
            for side in (-1, 1):
                p.ell(x + side * 12, y - 4, 6, 7, (236, 238, 226), w=2)
            p.ell(x, y + 14, 6, 7, (40, 22, 22), w=2)


def s_grip(p, t, T):
    p.rect(0, 0, W, H, (90, 90, 92), w=0)
    p.line([(640, -20), (640, H + 20)], w=10, color=(200, 180, 130))
    sq = 4 * math.sin(t * 2)  # dłoń zaciska się mocniej
    K.limb(p, (W + 80, 600), (700, 380), 110, K.narr_sleeve(), outline=4)
    p.ell(650, 370, 70 - sq, 56, K.SKIN)
    for k in range(4):
        p.line([(600, 330 + k * 22), (690, 330 + k * 22)], w=3)


def lying(p, x, y, s, who):
    c = K.WHO[who]
    for dy in (-12, 2):  # nogi w spodniach i buty — leży na brzuchu, głową do zbiornika
        p.poly([(x + 110 * s, y + dy * s - 8 * s), (x + 250 * s, y + dy * s - 6 * s), (x + 250 * s, y + dy * s + 8 * s),
                (x + 110 * s, y + dy * s + 8 * s)], c["bottom"], w=3)
        p.ell(x + 262 * s, y + dy * s, 14 * s, 9 * s, c["shoes"], w=3)
    p.poly([(x - 120 * s, y - 20 * s), (x + 120 * s, y - 20 * s), (x + 130 * s, y + 10 * s), (x - 130 * s, y + 10 * s)], c["top"])
    p.ell(x - 160 * s, y - 6 * s, 36 * s, 30 * s, K.HAIR_BACK.get(c["hair"]) or c["skin"])  # tył głowy: włosy


def s_dusk(p, t, T):
    K.roof(p, t, dusk=0.4 + 0.5 * t / T)
    lying(p, 760, 560, 1.0, "narrator")
    lying(p, 600, 620, 1.0, "kuba")


def s_down(p, t, T):
    """Schodzą z dachu w ostatnim świetle (okno półpiętra): Kuba z dwoma kanistrami, wolno, krok po kroku;
    za nim narrator z trzecim kanistrem i dłonią na poręczy."""
    K.stair_flight(p, t, top="okno", sky=(200, 124, 98), dark=0.35)
    br = math.sin(t * 2 * math.pi / 4)  # wolny oddech, jak uczył Henryk
    hands = K.st_group(p, t, [dict(who="kuba", a=13, b=3, step=0.55, x=0.25, look=0.1, eyes=0.8,
                                   arms={"l": (-34, 116 + 4 * br), "r": (34, 116 + 4 * br)}),
                              dict(who="narrator", a=15, b=6, step=0.5, t0=0.5, lead="r", x=-0.74, rail=True,
                                   arms={"r": (30, 112)})])
    for i, keys in ((1, ("r",)), (0, ("l", "r"))):  # kanistry wiszą w dłoniach, uchwytem w dłoni
        h = hands[i]
        for key in keys:
            canister(p, h[key][0], h[key][1] + 120 * 0.55 * h["s"], 0.55 * h["s"])


def s_boil(p, t, T):
    K.staff_room(p, t)
    p.rect(880, 290, 980, 330, (90, 90, 90), w=3)  # garnek na kuchence
    for i in range(5):
        y = 280 - ((t * 60 + i * 40) % 180)
        p.ell(930 + 20 * math.sin(t * 2 + i), y, 26 + 4 * i, 12, None, w=2, color=(240, 240, 240))
    K.figure(p, 760, 780, 1.0, t, "zosia", look=0.6, gaze=(0.7, 0.4), arms={"r": (150, 20)})


def s_thermo(p, t, T):
    K.thermometer(p, t, value=39.5, rise=ease(t / (T * 0.7)))


def s_towel(p, t, T):
    K.staff_room(p, t)
    K.irena_lying(p, t, fever=0.8)
    K.sitting(p, 200, 720, 0.9, t, "henryk", gaze=(0.8, 0.4), arms={"r": (180, 60), "l": (60, 120)})
    p.rect(410, 490, 490, 520, (230, 236, 240), w=3)  # mokry ręcznik na czole
    if int(t * 2) % 2 == 0:
        p.ell(450, 525 + (t * 30) % 20, 4, 6, (180, 210, 230), w=0)


def s_confess(p, t, T):
    K.staff_room(p, t, night=True)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.6, 0.4), mouth=talk(t, T, speed=6), fear=0.3)


def s_wound(p, t, T):
    p.rect(0, 0, W, H, (60, 50, 40), w=0)
    p.glow([(300, 0), (980, 0), (1100, H), (180, H)], (255, 230, 170, 50))  # światło lampy
    K.limb(p, (-80, H + 40), (480, 460), 170, K.WHO["zosia"]["sleeve"], outline=4)
    p.ell(640, 400, 210, 150, K.WHO["zosia"]["skin"])  # dłoń wnętrzem do góry
    for k in range(4):
        p.line([(820, 300 + k * 50), (920, 290 + k * 50)], w=28, color=K.WHO["zosia"]["skin"])
    p.line([(520, 430), (720, 380)], w=10, color=(170, 50, 50))  # rana
    p.ell(620, 404, 40, 14, (220, 200, 90), w=2, rot=-0.25)  # ropa
    p.ell(620, 410, 120, 70, None, w=3, color=(200, 90, 80))  # zaczerwienienie


FNS = [B.card("DZIEŃ 22"), s_tap, s_count, s_tank_idea, s_irena_fever, s_top_floor, s_hatch, s_city, s_fill, s_kuba_city,
       s_first_out, s_rope, s_faces_up, s_grip, s_dusk, s_down, s_boil, s_thermo, s_towel, s_confess, s_wound]
LOOK = [None] + [B.WARD] * 4 + [B.WARD] * 2 + [B.DAY] * 7 + [B.NIGHT] + [B.WARD] * 4 + [B.NIGHT] * 2
CAM = {8: {"zoom": 1.5, "cx": 880, "cy": 420}, 14: {"zoom": 1.5, "cx": 700, "cy": 500}}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
