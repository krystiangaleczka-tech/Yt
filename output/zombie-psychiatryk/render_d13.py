"""Wariant A · dzień 13 „Zsyp” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import random
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 13
NW = K.WHO["nowak"]
SACK = (176, 158, 120)


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def s_carry(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0])
    k = t / T
    s = 0.55 + 0.4 * k
    hn = K.figure(p, 640 - 80 * s, 520 + 200 * k, s, t * 0.5, "narrator", walk=t * 0.5, arms={"r": (40, 70)})
    hk = K.figure(p, 640 + 80 * s, 520 + 200 * k, s, t * 0.5 + 0.3, "kuba", walk=t * 0.5 + 0.3, arms={"l": (-40, 70)})
    x0, x1, y = hn["r"][0], hk["l"][0], (hn["r"][1] + hk["l"][1]) / 2
    p.poly([(x0, y - 20 * s), (x1, y - 20 * s), (x1 - 10 * s, y + 70 * s), (x0 + 10 * s, y + 70 * s)], SACK, w=3)  # worek niesiony we dwóch


def s_chute(p, t, T):
    K.chute(p, t, 0.0)
    p.rect(900, 140, 1240, 600, (124, 138, 122))  # drzwi dyżurki obok
    p.rect(960, 200, 1180, 360, (182, 200, 168), w=4)
    k = ease(t / T)  # kamera przesuwa wzrok na dyżurkę — światło pada przez jej szybę
    p.glow([(960, 200), (1180, 200), (1180 - 40 * k, 600), (960 - 40 * k, 600)], (255, 255, 240, int(30 * k)))


def s_prints(p, t, T):
    p.rect(0, 0, W, H, (182, 200, 168), w=0)  # szyba dyżurki
    rnd = random.Random(7)
    n = int(40 + 160 * ease(t / T))  # im dłużej patrzy, tym więcej odcisków widzi
    for i in range(n):
        x, y, rot = rnd.uniform(40, 1240), rnd.uniform(40, 680), rnd.uniform(-0.6, 0.6)
        p.ell(x, y, 26, 32, (150, 168, 140), w=1.5, rot=rot)
        for f in range(4):
            p.ell(x - 18 + f * 12, y - 40, 6, 12, (150, 168, 140), w=1.5)


def s_look_prints(p, t, T):
    p.rect(0, 0, W, H, (182, 200, 168), w=0)
    for i in range(30):
        r = random.Random(i)
        p.ell(r.uniform(40, 1240), r.uniform(40, 680), 24, 30, (160, 178, 150), w=1.5)
    k = ease((t - 0.3) / 0.8)
    R.nurse_face(p, 640, 330, 1.0, 0.3 + 0.3 * k, t, gaze=(-0.4 + 0.8 * k, -0.2))


def s_open_hatch(p, t, T):
    K.chute(p, t, ease(t / 0.6))
    if t > 0.4:
        for i in range(12):  # kurz z dołu
            r = random.Random(i)
            y = 440 - ((t - 0.4) * r.uniform(80, 160)) % 260
            p.ell(r.uniform(500, 780), y, 3, 3, (200, 200, 190), w=0)
    K.limb(p, (1300, 700), (790, 300 - 300 * ease(t / 0.6) * 0.5), 90, K.WHO["kuba"]["sleeve"], outline=4)


def s_count(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    R.nurse_face(p, 560, 320, 1.0, 0.4, t, gaze=(0.6, 0.0))
    n = min(3, int(t / (T * 0.8) * 3) + 1)  # palce: raz, dwa, trzy
    hx, hy = 960, 560
    K.limb(p, (hx + 200, H + 80), (hx, hy + 40), 100, K.narr_sleeve(), outline=4)
    p.ell(hx, hy, 60, 50, K.SKIN)
    for i in range(n):
        p.line([(hx - 30 + i * 30, hy - 30), (hx - 34 + i * 30, hy - 110)], w=20, color=K.SKIN)
        p.line([(hx - 30 + i * 30, hy - 30), (hx - 34 + i * 30, hy - 110)], w=2.5)


def s_drop(p, t, T):
    p.rect(0, 0, W, H, (30, 30, 32), w=0)  # widok w głąb szybu
    for k in range(8):
        f = k / 8
        p.rect(640 - 400 * (1 - f), 360 - 300 * (1 - f), 640 + 400 * (1 - f), 360 + 300 * (1 - f), None, w=3, color=(90, 90, 90))
    f = ease(t / T)
    s = 1.0 - 0.9 * f
    p.poly([(640 - 120 * s, 360 - 90 * s), (640 + 120 * s, 360 - 90 * s), (640 + 100 * s, 360 + 90 * s), (640 - 100 * s, 360 + 90 * s)], SACK, w=3)


def s_impact(p, t, T):
    p.rect(0, 0, W, H, (60, 62, 60), w=0)
    p.rect(-20, 520, W + 20, H + 20, (80, 80, 76))
    p.poly([(440, 520), (840, 520), (820, 440), (460, 440)], SACK, w=3)
    if t < 0.4:  # worek pęka, tacki rozsypują się
        pass
    for i in range(7):
        r = random.Random(i)
        f = ease(t / 0.6)
        x = 640 + r.uniform(-1, 1) * 420 * f
        y = 480 - 160 * math.sin(f * math.pi) * r.uniform(0.4, 1)
        p.rect(x - 40, y - 8, x + 40, y + 8, (190, 194, 198), w=2)
    if t < 0.25:
        for k in range(8):
            a = k * 0.8
            p.line([(640 + 200 * math.cos(a), 480 + 120 * math.sin(a)), (640 + 260 * math.cos(a), 480 + 150 * math.sin(a))], w=5)


def s_moans(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0], doors_open=0.0)
    if int(t * 4) % 2 == 0:  # jęk zza zamkniętych drzwi — nikt nie wychodzi (dzień)
        for side, x in ((-1, 260), (1, 1020)):
            for k in range(3):
                p.ell(x, 380, 30 + 20 * k, 20 + 14 * k, None, w=2, color=(200, 210, 200))


def s_three_go(p, t, T):
    K.cellar(p, t, flick=0.7)
    k = t / T  # trzech z korytarza rozdzielni idzie w głąb, do pralni
    for i, (dl, s0) in enumerate(((0.0, 0.85), (0.25, 0.8), (0.45, 0.9))):
        f = max(0.0, k - dl * 0.5)
        K.zombie_back(p, 600 + 50 * i + 120 * f, 720 - 230 * f, s0 * (1 - 0.5 * f), t + i, 160 + i, walk=t * 0.6)


def s_radio(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    K.limb(p, (W + 100, H + 100), (700, 470), 140, K.narr_sleeve(), outline=4)
    p.ell(660, 450, 80, 60, K.SKIN)
    p.rect(590, 230, 690, 470, (40, 42, 46), w=4)
    p.line([(670, 230), (670, 120)], w=10)
    led = int(t * 6) % 2 == 0 and 0.3 < t < T - 0.3  # Zosia mówi — dioda mruga
    p.rect(610, 260, 670, 300, (120, 220, 120) if led else (60, 90, 60), w=2)


def s_soldier_sky(p, t, T):
    K.connector(p, t)
    up = ease((t - 0.3) / 0.5)

    def win(q):
        pass
    p.rect(60, 180, 300, 440, (200, 190, 160), w=4)  # okno łącznika (zachód)
    K.figure(p, 180, 440, 0.3, t, "soldier", arms={"r": (30, 95 - 200 * up)})
    for x in range(60, 300, 20):  # siatka płotu przed nim
        p.line([(x, 360), (x + 20, 440)], w=1.5, color=(70, 76, 72), amp=0.3)
    p.rect(60, 180, 300, 440, None, w=6)
    K.figure(p, 700, 760, 1.0, t * 0.5, "narrator", walk=t * 0.5, look=-0.8, gaze=(-1.0, -0.2))
    K.figure(p, 900, 760, 1.0, t * 0.5 + 0.3, "kuba", walk=t * 0.5 + 0.3, look=-0.8, gaze=(-1.0, -0.2))


def s_ready(p, t, T):
    K.pharmacy_inside(p, t)
    zip_ = ease(t / 0.6)  # zapina bluzę pod szyję
    h = K.figure(p, 980, 760, 1.05, t, "nowak", look=-0.4, mouth=talk(t, T, 0.6), arms={"r": (-20, 40 - 20 * zip_)})
    K.grille(p, 1060, 60, W + 40, 600, gap=60, bar=10)


def s_zosia_yields(p, t, T):
    K.pharmacy_front(p, t)
    shake = 16 * math.sin(t * 6) * (1 - ease((t - T * 0.5) / 0.4))  # kręci głową… i przestaje
    K.face_cu(p, 640 + shake, 330, 1.0, "zosia", t, gaze=(0.6, 0.2 + 0.5 * ease((t - T * 0.5) / 0.4)), fear=0.3)


def s_henryk_joins(p, t, T):
    K.pharmacy_inside(p, t)
    K.figure(p, 900, 760, 1.0, t, "nowak", look=-0.3)
    K.figure(p, 700, 760, 1.0, t, "narrator", look=0.3)
    K.figure(p, 520, 760, 1.0, t, "kuba", look=0.3)
    k = ease(t / (T * 0.7))  # Henryk podnosi się spod ściany i staje obok: siedzi → kuca z kolanami → stoi
    if k < 0.25:
        K.sitting(p, 300, 700, 0.95, t, "henryk")
    elif k < 0.6:
        u = (k - 0.25) / 0.35  # wstawanie: biodra idą w górę, kolana się prostują
        c = K.WHO["henryk"]
        foot_y = 752
        hip_y = 610 - 40 * u
        for side in (-1, 1):
            hip = (300 + side * 18, hip_y)
            foot = (300 + side * 22, foot_y)
            knee = (300 + side * 20 + 60 * (1 - u), (hip_y + foot_y) / 2 - 30 * (1 - u))
            K.limb(p, hip, knee, 30, c["skin"])
            K.limb(p, knee, foot, 28, c["skin"])
            p.ell(foot[0], foot[1] - 4, 18, 10, c["shoes"], w=3)
        K.figure(p, 300, hip_y + 112, 1.0, t, "henryk", legs=False, look=0.3, arms={"l": (40, 60), "r": (60, 40)})
    else:
        K.figure(p, 300 + 40 * k, 760, 1.0, t * 0.4, "henryk", walk=t * 0.4 if k < 1 else None, look=0.4)


def s_four(p, t, T):
    K.cellar(p, t, flick=0.5)
    k = t / T
    for who, dx, lag in (("narrator", -230, 0.0), ("kuba", -80, 0.05), ("nowak", 70, 0.2), ("henryk", 220, 0.1)):
        f = max(0.0, k - lag)
        s = 1.05 - 0.5 * f
        K.figure_back(p, 640 + dx * s, 760 - 230 * f, s, t * 0.5, who, walk=t * 0.5)


def s_generator(p, t, T):
    lift = ease((t - 0.3) / 0.8)  # zsuwają plandekę
    K.tech_room(p, t, tarp=1 - 0.7 * lift)


def s_fuel(p, t, T):
    K.tech_room(p, t, tarp=0.3)
    k = ease((t - 0.2) / 0.6)
    p.line([(960, 380), (960, 300 + 120 * k)], w=6, color=(200, 200, 190))  # miarka w beczce
    K.figure(p, 860, 780, 1.1, t, "nowak", look=0.5, mouth=talk(t, T, 0.6), arms={"r": (90, 40 - 30 * k)})


def s_switch(p, t, T):
    p.rect(0, 0, W, H, (130, 130, 126), w=0)
    p.rect(420, 120, 860, 620, (100, 100, 96), w=4)
    p.rect(580, 220, 700, 520, (40, 40, 40), w=4)
    p.rect(600, 300, 680, 360, (200, 60, 50), w=3)  # dźwignia — jeszcze nie przekręcona
    sq = 6 * math.sin(t * 2)  # palce zaciskają się i rozluźniają
    K.limb(p, (1300, 760), (720, 360), 140, K.narr_sleeve(), outline=4)
    p.ell(680, 340, 80 + sq, 60, K.SKIN)


def s_hesitate(p, t, T):
    p.rect(0, 0, W, H, (70, 74, 76), w=0)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(0.6 * math.sin(t * 2), 0.3), fear=0.6, blink_k=0.0)


def s_steps(p, t, T):
    K.cellar(p, t, flick=0.35)
    k = t / T  # w ciemności korytarza wracają sylwetki
    for i, dl in enumerate((0.2, 0.45, 0.6)):
        f = max(0.0, k - dl)
        if f > 0:
            R.zombie(p, 600 + 60 * i, 440 + 80 * f, 0.3 + 0.2 * f, t + i, 160 + i, tilt=0.1 * (i - 1))


FNS = [B.card("DZIEŃ 13"), s_carry, s_chute, s_prints, s_look_prints, s_open_hatch, s_count, s_drop, s_impact, s_moans,
       s_three_go, s_radio, s_soldier_sky, s_ready, s_zosia_yields, s_henryk_joins, s_four, s_generator, s_fuel, s_switch,
       s_hesitate, s_steps]
LOOK = [None] + [B.DAY] * 9 + [B.BASE] + [B.DAY] * 2 + [B.BASE] * 3 + [B.DARK] * 6
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
