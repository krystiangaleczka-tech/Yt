"""Wariant A · dzień 11 „Okno” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 11
SHEET = (238, 236, 228)


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def s_paint(p, t, T):
    K.pharmacy_inside(p, t)
    p.poly([(300, 600), (980, 590), (1000, 700), (280, 712)], SHEET, w=3)  # prześcieradło na podłodze
    n = min(3, 1 + int(t / (T * 0.8) * 3))
    for k, txt in enumerate(("6 ŻYWYCH", "APTEKA", "PIWNICA")[:n]):
        p.text(450 + k * 200, 650, txt, 26, fill=(30, 30, 30))
    stroke = 20 * math.sin(t * 7)
    K.figure(p, 640, 620, 0.85, t, "zosia", look=0.0, gaze=(0, 1), arms={"r": (60 + stroke, 120)})


def s_dry(p, t, T):
    p.rect(0, 0, W, H, SHEET, w=0)
    for x in range(0, W, 90):
        p.line([(x, 0), (x + 30, H)], w=1.5, color=(220, 218, 210), amp=0.4)
    p.text(640, 340, "PIWNICA", 150, fill=(30, 30, 30))
    k = ease(t / T)  # ostatnia litera jeszcze mokra — farba ścieka coraz niżej
    p.line([(1010, 410), (1010, 420 + 120 * k)], w=8, color=(30, 30, 30))


def s_corridor(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0], doors_open={(0, -1): 0.8, (1, 1): 0.7})
    k = t / T
    for who, dx in (("narrator", -70), ("henryk", 70)):
        s = 0.55 + 0.4 * k
        K.figure(p, 640 + dx * s, 520 + 200 * k, s, t * 0.5, who, walk=t * 0.5, look=0.2 if who == "narrator" else -0.2)


def s_room_patients(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 520, W, H, (104, 124, 100), w=0)
    for i, (x, s) in enumerate(((440, 0.9), (680, 1.0), (880, 0.85))):
        sway = 1.0 if i == 1 else 0.3  # jeden kołysze się mocniej
        K.zombie_back(p, x, 640, s, t * sway + i * 0.7, 140 + i)
    for x0, x1 in ((0, 250), (1030, W)):
        p.rect(x0, -20, x1, H + 20, (124, 138, 122))
    p.line([(250, -20), (250, H + 20)], w=5)
    p.line([(1030, -20), (1030, H + 20)], w=5)


def s_handset(p, t, T):
    K.phone_detail(p, t, ring=False)
    if t < T * 0.3:  # ostatnie piknięcie… i cisza
        p.line([(300, 520), (340, 500)], w=3)


def s_canisters(p, t, T):
    K.bathroom(p, t)
    p.rect(360, 300, 420, 330, (170, 176, 180), w=3)  # kran
    p.line([(400, 330), (400, 440)], w=10, color=(170, 200, 220))
    for i, x in enumerate((340, 480)):
        lvl = ease((t - i * T * 0.45) / (T * 0.45))
        p.rect(x, 440, x + 110, 600, (200, 210, 230), w=3)
        p.rect(x + 4, 596 - 150 * lvl, x + 106, 596, (150, 186, 214), w=0)
    K.figure(p, 700, 780, 1.05, t, "narrator", look=-0.6, gaze=(-0.6, 0.6), arms={"l": (-150, 30)})


def s_room8(p, t, T):
    K.ward_room(p, t)
    k = ease(t / T)  # kamera wchodzi z narratorem: kurz unosi się w smudze światła
    for i in range(12):
        x = 200 + (i * 97) % 380 + 20 * math.sin(t + i)
        y = 400 - ((t * 30 + i * 40) % 300)
        p.ell(x, y, 2.5, 2.5, (240, 240, 230), w=0)


def s_sheet(p, t, T):
    K.ward_room(p, t, sheet=ease(t / (T * 0.7)))
    K.figure_back(p, 360, 780, 1.1, t, "narrator", arms={"l": (-60, -150), "r": (60, -150)})


def s_six(p, t, T):
    K.yard_trucks(p, t, soldiers=False, wire=1.0)
    up = ease((t - 0.4) / 0.6)  # żołnierz z lornetką podnosi dłoń: sześć palców
    h = K.figure(p, 640, 900, 1.6, t, "soldier", arms={"l": (40, -30), "r": (60, 95 - 260 * up)})
    if up > 0.5:
        hx, hy = h["r"]
        for i in range(5):
            K.limb(p, (hx - 20 + i * 10, hy), (hx - 34 + i * 17, hy - 50), 9, K.WHO["soldier"]["skin"], outline=2)
        K.limb(p, (hx + 30, hy - 30), (hx + 70, hy - 70), 9, K.WHO["soldier"]["skin"], outline=2)  # szósty palec: druga dłoń
    for x in range(0, W + 1, 60):
        p.line([(x, 300), (x + 60, 720)], w=2.5, color=(70, 76, 72), amp=0.4)
        p.line([(x + 60, 300), (x, 720)], w=2.5, color=(70, 76, 72), amp=0.4)


def s_relief(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    k = ease((t - 0.2) / 1.0)
    R.nurse_face(p, 640, 320, 1.0, 0.4 - 0.3 * k, t, gaze=(-0.5, -0.2), breath=-1.5 * k)


def s_listen(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    tilt = 16 * ease((t - 0.3) / 0.6)  # przekrzywia głowę
    K.face_cu(p, 640 + tilt, 330 + tilt * 0.3, 1.0, "henryk", t, gaze=(0.8 * ease((t - 0.3) / 0.6), 0.0))


def s_wardrobe(p, t, T):
    k = ease((t - 0.3) / (T * 0.6))
    K.ward_room(p, t, wardrobe=0.15 + 0.6 * k)
    if k > 0.2:  # zarażony wychodzi z szafy (szafa przycina, dopóki jest w środku)
        R.zombie(p, 1060 - 40 * k, 560, 0.95, t, 150, tilt=0.2)
        p.rect(1115 + 100 * (0.15 + 0.6 * k) * 0.2, 140, 1220, 560, (124, 108, 86), w=0, amp=0)
        p.rect(1010, 120, 1220, 140, (150, 166, 140), w=0, amp=0)


def s_jump(p, t, T):
    K.ward_room(p, t, sheet=1.0)
    k = ease(t / 0.35)  # odskok jak sylwetka z pierwszego ujęcia
    K.figure(p, 360 + 260 * k, 760, 1.05, t, "narrator", look=0.8, lean=0.5 * k, arms={"l": (-40, 40), "r": (60, 30)})


def s_shield(p, t, T):
    K.ward_room(p, t, sheet=1.0, wardrobe=0.75)
    k = t / T
    R.zombie(p, 920 - 60 * k, 600, 0.95, t, 150, tilt=0.2)
    K.figure_back(p, 700 + 100 * k, 760, 1.1, t, "henryk", walk=t * 0.4)
    if (t * 1.2) % 1.0 < 0.5:
        for i in range(3):
            p.ell(760 + 100 * k + i * 20, 330 - i * 8, 12 + 10 * i, 8 + 6 * i, None, w=2, color=(230, 236, 236))


def s_out(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0])
    k = ease(t / 0.6)
    K.figure(p, 360 + 300 * k, 800, 1.15, t * 1.6, "narrator", walk=t * 1.6 if k < 1 else None, look=-0.7)


def s_realize(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(900, -20, W + 20, H + 20, (124, 138, 122))  # drzwi sali 8 za nim
    k = ease((t - T * 0.35) / 0.6)
    R.nurse_face(p, 560, 320, 1.0, 0.4 + 0.3 * k, t, gaze=(0.9 * k, 0.0))


def s_door_sounds(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(420, 60, 860, 640, (124, 138, 122))
    p.rect(800, 350, 830, 380, (150, 150, 140), w=2)
    p.text(640, 120, "8", 50)
    slam = T * 0.7
    if t < slam:  # długi oddech zza drzwi
        r = 30 + 20 * math.sin(t * 2)
        p.ell(640, 360, r, r * 0.6, None, w=2, color=(230, 236, 236))
    elif t < slam + 0.15:
        for k in range(6):
            a = k * 1.05
            p.line([(640 + 230 * math.cos(a), 360 + 200 * math.sin(a)), (640 + 280 * math.cos(a), 360 + 240 * math.sin(a))], w=4)


def s_scratch(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0])
    k = ease(t / T)
    h = K.figure(p, 640, 520 + 200 * k, 0.6 + 0.35 * k, t * 0.4, "henryk", walk=t * 0.4, arms={"l": (-30, 80)})
    hx, hy = h["l"]
    s = 0.6 + 0.35 * k
    for i in range(3):  # zadrapanie na przedramieniu
        p.line([(hx + 4 * s, hy - (40 + i * 8) * s), (hx + 18 * s, hy - (60 + i * 8) * s)], w=2.5, color=(170, 40, 40))


def s_check(p, t, T):
    p.rect(0, 0, W, H, (150, 146, 120), w=0)
    K.limb(p, (-80, 520), (900, 380), 160, K.WHO["henryk"]["top"], outline=4)  # przedramię Henryka
    p.ell(940, 370, 80, 60, K.WHO["henryk"]["skin"])
    for i in range(3):
        p.line([(560 + i * 30, 340), (620 + i * 30, 300)], w=4, color=(170, 40, 40))
    k = ease((t - 0.2) / 0.6)  # palce Zosi rozchylają skórę przy zadrapaniu
    for side in (-1, 1):
        p.ell(600 + side * (60 + 20 * k), 400, 40, 26, K.WHO["zosia"]["skin"])
        K.limb(p, (600 + side * 200, H + 60), (600 + side * (60 + 20 * k), 420), 60, K.WHO["zosia"]["sleeve"], outline=4)


def s_nowak_asks(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(-0.7, 0.2), mouth=talk(t, T), fear=0.45)


def s_turn_away(p, t, T):
    K.pharmacy_inside(p, t, dark=0.6)
    k = ease((t - T * 0.4) / 0.8)  # odwraca się do ściany
    if k < 0.5:
        K.sitting(p, 640, 690, 0.95, t, "nowak", look=-0.6 * (1 - k), gaze=(-0.5, 0.2))
    else:  # leży na boku plecami do nas, koc pod brodę — udaje, że śpi
        c = K.WHO["nowak"]
        br = 3 * math.sin(t * 1.6)
        dy = -110
        p.poly([(480, 690 + dy - br), (880, 680 + dy - br), (900, 740 + dy), (460, 744 + dy)], c["top"])  # biały fartuch na plecach
        p.poly([(620, 676 + dy - br), (920, 668 + dy - br), (930, 742 + dy), (600, 746 + dy)], (120, 110, 100))  # koc
        p.ell(440, 690 + dy, 54, 48, c["skin"])  # tył głowy
        p.poly([(394, 680 + dy), (412, 650 + dy), (440, 642 + dy), (470, 650 + dy), (488, 680 + dy), (470, 700 + dy), (412, 702 + dy)],
               (170, 170, 166))  # siwy wianek
        p.ell(412, 668 + dy, 12, 22, (170, 170, 166), w=2.5)


FNS = [B.card("DZIEŃ 11"), s_paint, s_dry, s_corridor, s_room_patients, s_handset, s_canisters, s_room8, s_sheet, s_six,
       s_relief, s_listen, s_wardrobe, s_jump, s_shield, s_out, s_realize, s_door_sounds, s_scratch, s_check,
       s_nowak_asks, s_turn_away]
LOOK = [None] + [B.BASE] * 2 + [B.DAY] * 16 + [B.BASE] * 3
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
