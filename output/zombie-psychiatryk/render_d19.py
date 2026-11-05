"""Wariant A · dzień 19 „Głód” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 19
COOK = (236, 236, 232)  # fartuch kucharki


def talk(t, T, a=0.3, b=0.4, speed=9):
    return 0.5 + 0.5 * math.sin(t * speed) if a < t < T - b else 0.0


def basia(p, x, y, s, t, walk=None):
    R.zombie(p, x, y, s, t, 190, gown=COOK, tilt=0.12)
    gx, gy = x + 6 * s, y - 228 * s
    p.poly([(gx - 36 * s, gy - 30 * s), (gx + 36 * s, gy - 30 * s), (gx + 26 * s, gy - 62 * s), (gx - 26 * s, gy - 62 * s)], COOK, w=2)  # czepek


def s_fridge(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    p.rect(300, 60, 980, 680, (230, 232, 230), w=5)  # lodówka otwarta
    p.rect(330, 90, 950, 650, (210, 220, 220))
    for y in (250, 420):
        p.line([(330, y), (950, y)], w=4)
    n = 3 - min(2, int(t / T * 3))  # znika ostatnie jedzenie
    for i in range(n):
        p.rect(380 + i * 140, 180, 480 + i * 140, 246, (180, 140, 100), w=3)
    k = ease(t / T)
    p.glow([(330, 90), (950, 90), (950, 650), (330, 650)], (255, 255, 240, int(40 * (1 - 0.5 * k))))


def s_sheet(p, t, T):
    K.ward_room(p, t)
    K.sheet_on_pane(p, ease(t / (T * 0.6)))  # od d17 pięcioro, od d15 na parterze — nowy napis
    K.figure_back(p, 453, 780, 1.05, t, "zosia", arms={"l": (-60, -150), "r": (60, -150)})


def s_kuba(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(0.3, 0.6), mouth=talk(t, T), fear=0.3)


def s_zosia(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.4, 0.0), mouth=talk(t, T), fear=0.1)


def s_kitchen_in(p, t, T):
    K.kitchen(p, t)
    k = t / T
    for who, dx in (("narrator", -60), ("henryk", 80)):
        K.figure(p, 300 + dx + 260 * k, 780, 1.0, t * 0.5, who, walk=t * 0.5, look=0.6)


def s_cook_window(p, t, T):
    K.fridge_window(p, t)


def s_her_name(p, t, T):
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.7, 0.0), mouth=talk(t, T, 0.6, 0.4, 6) * 0.8)


def s_open_cold(p, t, T):
    K.kitchen(p, t)
    op = ease((t - 0.3) / 0.6)  # drzwi chłodni się otwierają: wypływa zimna mgła
    p.rect(880, 160, 1160, 600, (20, 30, 40))
    p.rect(880 + 260 * op, 160, 1160 + 40 * op, 600, (176, 184, 188))
    for i in range(int(8 * op)):
        p.ell(880 + i * 30, 560 - i * 10, 60, 20, (220, 232, 240), w=0)
    K.figure(p, 760, 780, 1.0, t, "narrator", look=0.6, arms={"r": (120, 0)})


def s_basia_out(p, t, T):
    K.kitchen(p, t)
    p.rect(880, 160, 1160, 600, (20, 30, 40))
    k = ease(t / T)  # wychodzi wolno, jakby była zmęczona
    basia(p, 1020 - 200 * k, 600 + 40 * k, 0.9 + 0.1 * k, t * 0.5)
    p.rect(1160, 160, 1200, 600, (176, 184, 188))  # skrzydło drzwi chłodni z przodu


def s_follow(p, t, T):
    K.kitchen(p, t)
    k = t / T
    K.figure_back(p, 300 - 80 * k, 780, 1.05, t * 0.4, "henryk", walk=t * 0.4)
    basia(p, 520 - 100 * k, 700, 0.9, t)
    if (t * 1.2) % 1.0 < 0.5:
        for i in range(3):
            p.ell(330 + i * 20, 400 - i * 8, 12 + 10 * i, 8 + 6 * i, None, w=2, color=(230, 236, 236))


def cart(p, x, y, s=1.0, load=1.0):
    p.rect(x - 140 * s, y - 120 * s, x + 140 * s, y - 20 * s, (170, 176, 180), w=4)
    for i in range(int(6 * load)):
        p.rect(x - 120 * s + (i % 3) * 80 * s, y - 180 * s + (i // 3) * 50 * s, x - 60 * s + (i % 3) * 80 * s, y - 130 * s + (i // 3) * 50 * s,
               ((180, 140, 100), (200, 80, 70), (120, 160, 90))[i % 3], w=2)
    for wx in (x - 110 * s, x + 110 * s):
        p.ell(wx, y, 22 * s, 22 * s, (40, 40, 40))


def s_load(p, t, T):
    K.kitchen(p, t)
    cart(p, 700, 680, 1.0, load=ease(t / T))
    reach = math.sin(t * 3) * 0.5 + 0.5
    K.figure(p, 980, 780, 1.0, t, "narrator", look=-0.6, arms={"l": (-80 - 60 * reach, 120)})


def s_squeak(p, t, T):
    p.rect(0, 0, W, H, (120, 124, 118), w=0)
    a = t * 6
    p.ell(640, 420, 180, 180, (40, 40, 40))
    p.ell(640, 420, 60, 60, (150, 150, 150), w=3)
    p.line([(640 + 160 * math.cos(a), 420 + 160 * math.sin(a)), (640 - 160 * math.cos(a), 420 - 160 * math.sin(a))], w=6, color=(80, 80, 80))
    if int(t * 8) % 2 == 0:
        for k in range(3):
            p.line([(860 + k * 30, 260 - k * 20), (900 + k * 30, 240 - k * 20)], w=4)


def s_moan_store(p, t, T):
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    p.rect(420, 80, 860, 640, (150, 156, 150))
    p.rect(800, 340, 830, 400, (110, 110, 110), w=2)
    if int(t * 3) % 2 == 0:  # stłumiony jęk zza drzwi magazynu
        for k in range(3):
            p.ell(640, 360, 60 + 40 * k, 40 + 26 * k, None, w=2, color=(150, 160, 150))


def s_butter(p, t, T):
    p.rect(0, 0, W, H, (120, 124, 118), w=0)
    p.ell(640, 420, 180, 180, (40, 40, 40))
    p.ell(640, 420, 60, 60, (150, 150, 150), w=3)
    k = ease(t / (T * 0.7))
    p.ell(640, 420, 70, 70, (240, 220, 140), w=0) if k > 0.5 else None  # masło na osi koła
    K.limb(p, (1200, 760), (700 - 40 * math.sin(t * 6), 440), 90, K.narr_sleeve(), outline=4)
    p.ell(690 - 40 * math.sin(t * 6), 430, 50, 36, K.SKIN)
    p.rect(640 - 40 * math.sin(t * 6), 400, 700 - 40 * math.sin(t * 6), 440, (240, 220, 140), w=2)


def s_lock_store(p, t, T):
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    p.rect(420, 80, 860, 640, (20, 22, 22))
    k = ease((t - 0.2) / 0.6)  # Henryk zamyka drzwi magazynu; Basia stoi w środku, nie stawia oporu
    basia(p, 640, 620, 0.85, t)
    p.rect(420 + 440 * (1 - k), 80, 860, 640, (150, 156, 150))
    p.rect(420, 80, 860, 640, None, w=6)
    K.figure(p, 1000, 800, 1.05, t, "henryk", look=-0.6, arms={"l": (-160 * (1 - 0.3 * k), 20)})


def s_cook(p, t, T):
    K.staff_room(p, t)
    p.rect(880, 290, 980, 330, (90, 90, 90), w=3)  # garnek na kuchence
    for i in range(5):
        y = 280 - ((t * 60 + i * 40) % 180)
        p.ell(930 + 20 * math.sin(t * 2 + i), y, 26 + 4 * i, 12, None, w=2, color=(240, 240, 240))
    stir = 20 * math.sin(t * 4)
    K.figure(p, 760, 780, 1.0, t, "irena", look=0.6, gaze=(0.6, 0.6), arms={"r": (140 + stir, 20)})


def kuba_cu(p, t, T, gaze):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=gaze, mouth=talk(t, T), fear=0.2)


def s_kuba1(p, t, T):
    kuba_cu(p, t, T, gaze=(0.0, 0.8))


def s_kuba2(p, t, T):
    kuba_cu(p, t, T, gaze=(0.4, -0.1))


def s_hand(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 760, 360, 0.9, "kuba", t, gaze=(-0.5, 0.4), fear=0.2)
    k = ease((t - 0.2) / 0.5)  # dłoń Zosi ląduje na jego ramieniu; nie strząsa jej
    K.limb(p, (200, H + 60), (600 + 120 * k, 600), 70, K.WHO["zosia"]["sleeve"], outline=4)
    p.ell(620 + 120 * k, 596, 44, 30, K.WHO["zosia"]["skin"])


def s_ring(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    shake = 4 * math.sin(t * 70) if (t % 1.0) < 0.6 else 0  # dzwoni
    p.rect(480 + shake, 140, 800 + shake, 560, (230, 228, 220), w=5)
    p.rect(520 + shake, 190, 760 + shake, 260, (60, 60, 60), w=3)
    if shake:
        for k in range(3):
            p.line([(840 + k * 30, 200 + k * 30), (880 + k * 30, 190 + k * 30)], w=4)


def s_third_ring(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    k = ease((t - T * 0.6) / 0.4)  # patrzy jak w noc wybuchu; za trzecim razem sięga
    R.nurse_face(p, 640, 330, 1.0, 0.6 - 0.2 * k, t, gaze=(0.8, -0.2), blink_k=0.0)


FNS = [B.card("DZIEŃ 19"), s_fridge, s_sheet, s_kuba, s_zosia, s_kitchen_in, s_cook_window, s_her_name, s_open_cold,
       s_basia_out, s_follow, s_load, s_squeak, s_moan_store, s_butter, s_lock_store, s_cook, s_kuba1, s_kuba2, s_hand,
       s_ring, s_third_ring]
LOOK = [None] + [B.WARD] * 4 + [B.DAY] * 11 + [B.WARD] * 6
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
