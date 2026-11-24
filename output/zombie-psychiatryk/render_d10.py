"""Wariant A · dzień 10 „Paczka” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 10
NW = K.WHO["nowak"]
CROWD = [(180, 470, 0.42, 0.1), (330, 520, 0.5, -0.2), (480, 455, 0.38, 0.25), (820, 470, 0.42, -0.1),
         (960, 540, 0.55, 0.3), (700, 600, 0.62, -0.25), (260, 640, 0.7, 0.15)]  # (x, y, skala, przechylenie)


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def crowd(p, t, toward=0.0):
    """Zarażeni na trawniku twarzami do szpitala, każdy inaczej przechylony; toward 0..1 — ruszają do karetki."""
    for i, (x, y, s, tilt) in enumerate(sorted(CROWD, key=lambda c: c[1])):
        dx = 260 * ease(toward - i * 0.05) * (1 if x < 1040 else 0)
        R.zombie(p, x + dx, y, s, t + i * 0.7, 100 + i, tilt=tilt)


def s_drone(p, t, T):
    K.yard(p, t)
    crowd(p, t)
    x = -150 + 1500 * t / T
    K.drone(p, x, 110, 1.0, t)
    drop = T * 0.47  # zrzut tak, żeby paczka wylądowała tam, gdzie leży w następnych ujęciach (640, 560; ciągłość 1.6)
    if t < drop:
        K.parcel(p, x, 150, 0.5)
    else:  # paczka spada i ląduje na trawie
        f = min(1.0, (t - drop) / 0.6)
        x0 = -150 + 1500 * drop / T
        K.parcel(p, x0 + (640 - x0) * f, 150 + 410 * f * f, 0.5)


def s_window_view(p, t, T):
    def inner(q):
        K.yard(q, t)
        K.parcel(q, 700, 470, 0.35)
        crowd(q, t)
    K.basement_window(p, inner)


def s_crowd(p, t, T):
    K.yard(p, t)
    K.parcel(p, 640, 560, 0.5)
    crowd(p, t)


def s_kuba(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(0.0, 0.0), mouth=talk(t, T), fear=0.25)


def s_narrator(p, t, T):
    K.pharmacy_front(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.2, t, gaze=(-0.6, 0.0))


def s_zosia(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.3, 0.0), mouth=talk(t, T), fear=0.15)


def s_wrap_shoes(p, t, T):
    p.rect(0, 0, W, H, (96, 94, 86), w=0)
    p.poly([(380, 520), (820, 520), (880, 600), (360, 600)], (240, 240, 236), w=4)  # but
    K.limb(p, (560, 520), (560, 120), 150, K.TROUSERS, outline=4)
    n = min(5, int(t / (T * 0.8) * 5) + 1)  # kolejne zwoje bandaża
    for i in range(n):
        x = 420 + i * 80
        p.poly([(x, 510), (x + 50, 510), (x + 70, 604), (x + 20, 604)], (236, 234, 224), w=2)
    k = (t * 1.5) % 1.0
    for side in (-1, 1):  # dłonie pana Henryka owijają
        hx = 600 + side * 220 + 30 * math.sin(t * 6)
        K.limb(p, (hx + side * 300, H + 80), (hx, 560), 90, K.WHO["henryk"]["top"], outline=4)
        p.ell(hx, 556, 50, 36, K.WHO["henryk"]["skin"])


def s_side_door(p, t, T):
    p.rect(0, 0, W, H, (150, 160, 150), w=0)
    p.rect(420, 60, 860, 660, (124, 138, 122))
    p.rect(780, 340, 820, 420, (150, 150, 140), w=3)
    p.ell(800, 440, 10, 16, (20, 20, 20), w=2)  # dziurka od klucza
    a = math.pi / 2 * ease((t - 0.4) / 0.6)  # klucz się obraca
    p.line([(800, 440), (800 - 60 * math.sin(a), 440 + 60 * math.cos(a) - 60)], w=8, color=(170, 170, 160))
    K.limb(p, (1300, 760), (860, 470), 100, NW["top"], outline=4)
    p.ell(840, 450, 54, 40, NW["skin"])  # dłoń zasłania dziurkę, bliżej kamery
    for dx, dy in ((-10, 60), (0, 66), (12, 58)):  # pęk kluczy zwisa z dłoni
        p.line([(830, 480), (830 + dx, 480 + dy)], w=4, color=(170, 170, 160))
    p.rect(840, 530, 858, 548, (220, 190, 40), w=2)  # żółta przywieszka rozdzielni


def s_walk_lawn(p, t, T):
    K.yard(p, t)
    K.parcel(p, 640, 520, 0.42)
    crowd(p, t)
    k = t / T  # idą krokiem pana Henryka — powoli
    for who, dx in (("narrator", -70), ("kuba", 70)):
        s = 1.0 - 0.3 * k
        K.figure_back(p, 640 + dx * s, 820 - 160 * k, s, t * 0.35, who, walk=t * 0.35)


def s_sweat(p, t, T):
    p.rect(0, 0, W, H, (118, 150, 96), w=0)
    p.rect(0, 0, W, 260, (176, 196, 206), w=0)
    R.nurse_face(p, 640, 320, 1.0, 0.55, t, gaze=(0.8 * math.sin(t * 1.3), 0.0))


def s_feet(p, t, T):
    p.rect(0, 0, W, H, (118, 150, 96), w=0)
    for i in range(30):
        x = (i * 97) % W
        p.line([(x, 720), (x + 10, 640)], w=3, color=(80, 120, 70))
    for side, ph in ((-1, 0.0), (1, 0.5)):
        lift = 40 * max(0.0, math.sin((t / 1.2 + ph) * math.pi * 2))  # powolne kroki
        x = 640 + side * 170 + 140 * ((t / T + ph) % 1.0) * 0
        p.poly([(x - 120, 560 - lift), (x + 110, 560 - lift), (x + 140, 620 - lift), (x - 120, 620 - lift)], (236, 234, 224), w=4)
        K.limb(p, (x, 560 - lift), (x - 20, 120), 110, K.TROUSERS if side < 0 else K.WHO["kuba"]["bottom"], outline=4)


def soldier_rifle(p, x, y, s, t, aim=0.0, thumb=0.0, pulled=0.0):
    hands = K.figure(p, x, y, s, t, "soldier", arms={"l": (60, 10 - 20 * aim), "r": (40 - 20 * thumb + 40 * pulled, 20 - 160 * thumb * (1 - pulled))})
    p.line([(hands["l"][0] - 40 * s, hands["l"][1] + 6), (hands["l"][0] + 140 * s, hands["l"][1] - 20 * aim)], w=10 * s, color=(40, 40, 38))
    if thumb > 0.5 and pulled < 0.5:
        p.line([hands["r"], (hands["r"][0], hands["r"][1] - 30 * s)], w=8 * s, color=K.WHO["soldier"]["skin"])
    return hands


def fence_front(p):
    for x in range(0, W + 1, 60):
        p.line([(x, 200), (x + 60, 720)], w=2.5, color=(70, 76, 72), amp=0.4)
        p.line([(x + 60, 200), (x, 720)], w=2.5, color=(70, 76, 72), amp=0.4)
    p.line([(0, 200), (W, 200)], w=6, color=(60, 62, 60))


def s_aim(p, t, T):
    p.rect(0, 0, W, H, (176, 196, 206), w=0)
    p.rect(-20, 520, W + 20, H + 20, (98, 110, 88))
    soldier_rifle(p, 460, 820, 1.2, t, aim=0.2 + 0.3 * ease((t - 1.0) / 0.6))  # jeden poprawia celownik
    soldier_rifle(p, 860, 820, 1.2, t + 0.5, aim=0.4)
    fence_front(p)


def s_parcel_hands(p, t, T):
    p.rect(0, 0, W, H, (118, 150, 96), w=0)
    sway = 10 * math.sin(t * 5)
    K.parcel(p, 640 + sway, 560, 3.0)
    for i in range(4):  # butelki stukają o siebie
        x = 520 + i * 80 + sway
        p.rect(x - 22, 300, x + 22, 410, (190, 214, 226), w=3)
        p.rect(x - 12, 280, x + 12, 300, (60, 110, 160), w=2)
    if int(t * 4) % 2 == 0:
        for k in range(3):
            p.line([(600 + k * 40, 270), (590 + k * 40, 250)], w=3)
    for side in (-1, 1):
        p.ell(640 + side * 200 + sway, 520, 56, 40, K.WHO["kuba"]["skin"])


def s_turning(p, t, T):
    K.yard(p, t)
    k = ease((t - 0.3) / (T * 0.8))  # najbliższy zarażony odwraca się, bardzo powoli
    x, y, s = 640, 760, 1.6
    K.zombie_back(p, x, y, s, t, 109)
    # środek głowy jak w _zombie_back (kołysze się z tułowiem) — oko i nos idą za głową, nie stoją w miejscu
    hx, hy = x + math.sin(t * 3.1 + 109) * 5 * s, y - 228 * s
    if k > 0.3:  # z boku głowy wyłania się oko i nos
        f = (k - 0.3) / 0.7
        p.ell(hx + 30 * s * f, hy - 4 * s, 9 * s * f, 10 * s * f, (236, 238, 226), w=3)
        p.poly([(hx + 36 * s, hy + 8 * s), (hx + (36 + 10 * f) * s, hy + 18 * s), (hx + 34 * s, hy + 22 * s)], K.ZSKIN, w=2)


def s_throw(p, t, T):
    K.yard(p, t)
    crowd(p, t)
    k = ease(t / (T * 0.4))
    h = K.figure(p, 420, 760, 1.05, t, "narrator", look=0.7, arms={"r": (60 + 60 * k, 40 - 200 * k)})
    if t < T * 0.4:
        p.poly([(h["r"][0] - 30, h["r"][1] - 10), (h["r"][0] + 40, h["r"][1] - 20), (h["r"][0] + 30, h["r"][1] + 60)], (58, 66, 78), w=3)
    else:  # kurtka leci łukiem w stronę karetki
        f = (t - T * 0.4) / (T * 0.6)
        x = h["r"][0] + 560 * f
        y = h["r"][1] - 160 * math.sin(f * math.pi) + 60 * f
        p.poly([(x - 40, y - 10), (x + 40, y - 30), (x + 50, y + 30), (x - 30, y + 40)], (58, 66, 78), w=3)


def s_alarm(p, t, T):
    K.yard(p, t, amb_light=t)
    p.poly([(980, 300), (1080, 290), (1090, 330), (990, 340)], (58, 66, 78), w=3)  # kurtka na masce
    if int(t * 6) % 2 == 0:
        for k in range(3):
            p.ell(1040, 300, 60 + 40 * k, 30 + 20 * k, None, w=3, color=(230, 230, 230))
    crowd(p, t, toward=0.0)


def s_run(p, t, T):
    K.yard(p, t, amb_light=t)
    crowd(p, t, toward=t / T * 1.6)
    k = t / T  # biegną z paczką do drzwi, w stronę kamery
    for who, dx in (("narrator", -90), ("kuba", 90)):
        s = 0.6 + 0.5 * k
        h = K.figure(p, 640 + dx * s, 520 + 260 * k, s, t * 1.8, who, walk=t * 1.8, look=0.4 if who == "kuba" else -0.4)
        if who == "kuba":
            K.parcel(p, h["r"][0], h["r"][1] + 10, 0.45 * s)


def s_thumb(p, t, T):
    p.rect(0, 0, W, H, (176, 196, 206), w=0)
    p.rect(-20, 520, W + 20, H + 20, (98, 110, 88))
    pull = ease((t - T * 0.55) / 0.3)  # drugi żołnierz szarpie go za rękę
    soldier_rifle(p, 460, 820, 1.2, t, thumb=ease(t / 0.4), pulled=pull)
    h2 = soldier_rifle(p, 860, 820, 1.2, t + 0.5, aim=0.3)
    if pull > 0:
        K.limb(p, (860 - 50 * 1.2, 820 - 268 * 1.2), (620 - 40 * pull, 620 - 100 * (1 - pull)), 24 * 1.2, K.WHO["soldier"]["sleeve"])
    fence_front(p)


def s_slam(p, t, T):
    j = 10 * math.sin(t * 70) if 0.35 < t < 0.6 else 0
    p.rect(0, 0, W, H, (150, 160, 150), w=0)
    k = ease(t / 0.35)  # drzwi zatrzaskują się od środka
    p.rect(300, 60, 980, 660, (230, 236, 240))  # jasne podwórze w otworze
    p.rect(300 + j, 60, 300 + 680 * k + j, 660, (124, 138, 122))
    p.rect(300, 60, 980, 660, None, w=8)
    if k >= 1:
        p.rect(880 + j, 340, 920 + j, 420, (150, 150, 140), w=3)


def s_laugh(p, t, T):
    p.rect(0, 0, W, H, (124, 138, 122), w=0)
    shake = 6 * math.sin(t * 14)
    K.face_cu(p, 640, 340 + shake, 1.0, "kuba", t, gaze=(0.0, -0.3), mouth=0.6 + 0.4 * abs(math.sin(t * 8)), fear=0.3, breath=2 * math.sin(t * 8))


def s_bottles(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    n = min(12, 2 + int(t / (T * 0.8) * 10))  # Kuba wyjmuje kolejne butelki
    for i in range(n):
        x = 180 + (i % 6) * 160
        y = 300 + (i // 6) * 220
        p.rect(x - 30, y - 90, x + 30, y + 80, (190, 214, 226), w=3)
        p.rect(x - 16, y - 116, x + 16, y - 90, (60, 110, 160), w=3)


def s_note(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    K.paper(p, 640, 360, ["ILE WAS JEST?", "POKAŻCIE W OKNIE"], w=620, h=260)
    k = ease((t - 0.3) / 0.8)  # racje zsuwają się z kartki
    for i in range(3):
        x = 460 + i * 180 + 500 * k * (1 if i == 2 else -0.6 if i == 0 else 0.3)
        y = 320 + 420 * k * (1 if i == 1 else 0.2)
        p.rect(x - 80, y - 50, x + 80, y + 50, (120, 130, 90), w=3)
        p.text(x, y, "RACJA", 22)


def s_look_up(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - T * 0.45) / 0.6)  # znad kartki w górę — tam, gdzie jest sala 8
    R.nurse_face(p, 640, 330 - 10 * k, 1.0, 0.3 + 0.2 * k, t, gaze=(0.0, 0.8 - 1.7 * k), body=(640, 330))


FNS = [B.card("DZIEŃ 10"), s_drone, s_window_view, s_crowd, s_kuba, s_narrator, s_zosia, s_wrap_shoes,
       s_side_door, s_walk_lawn, s_sweat, s_feet, s_aim, s_parcel_hands, s_turning, s_throw, s_alarm, s_run,
       s_thumb, s_slam, s_laugh, s_bottles, s_note, s_look_up]
LOOK = [None] + [B.DAY] * 3 + [B.BASE] * 4 + [B.DAY] * 13 + [B.BASE] * 3
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
