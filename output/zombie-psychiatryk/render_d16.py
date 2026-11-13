"""Wariant A · dzień 16 „Konfrontacja” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 16
NW = K.WHO["nowak"]


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def table(p):
    p.poly([(240, 600), (1040, 600), (1120, 720), (160, 720)], (150, 120, 90), w=4)


def s_put(p, t, T):
    K.staff_room(p, t)
    for who, x, lk in (("zosia", 260, 0.5), ("kuba", 420, 0.4), ("irena", 860, -0.4), ("nowak", 1040, -0.6)):
        K.figure(p, x, 760, 0.95, t, who, look=lk, gaze=(0.0, 0.9))
    table(p)
    k = ease((t - 0.2) / 0.6)
    p.rect(560, 640 - 60 * (1 - k), 720, 690 - 60 * (1 - k), (236, 232, 214), w=3)  # przepustka ląduje na stole
    if k < 1:
        K.limb(p, (640, H + 80), (640, 680 - 60 * (1 - k)), 80, K.narr_sleeve(), outline=4)


def s_knows(p, t, T):
    K.staff_room(p, t)
    k = ease((t - 0.4) / 0.6)  # patrzy na przepustkę, potem podnosi wzrok — wie
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(0.0, 0.9 - 1.1 * k), fear=0.4 + 0.2 * k, blink_k=0.0)


def s_sleeve(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    K.limb(p, (-80, 440), (W + 80, 400), 240, NW["skin"], outline=4)  # przedramię w poprzek kadru
    p.ell(560, 420, 150, 86, (70, 50, 70), w=0)  # ugryzienie czarne na brzegach
    p.ell(560, 420, 100, 52, (110, 80, 110), w=0)
    for i in range(7):
        a = math.pi * (0.1 + 0.8 * i / 6)
        p.ell(560 + 80 * math.cos(a), 420 - 40 * math.sin(a), 8, 5, (50, 30, 40), w=0)
    roll = ease(t / (T * 0.6))  # rękaw zsuwa się w stronę łokcia i odsłania ugryzienie
    edge = 300 + 700 * roll
    K.limb(p, (W + 120, 396), (edge, 410), 290, NW["top"], outline=4)
    K.limb(p, (W + 120, 396), (edge, 410), 290, (40, 44, 56), outline=0)  # ciemna bluza pod fartuchem
    p.line([(edge, 270), (edge + 10, 550)], w=5)


def nowak_cu(p, t, T, gaze=(0.0, 0.4), fear=0.6, y=330):
    K.staff_room(p, t)
    K.face_cu(p, 640, y, 1.0, "nowak", t, gaze=gaze, mouth=talk(t, T), fear=fear)


def s_bitten(p, t, T):
    nowak_cu(p, t, T, gaze=(0.0, 0.6))


def s_wanted(p, t, T):
    nowak_cu(p, t, T, gaze=(-0.6, 0.2))


def s_cut(p, t, T):
    k = ease(t / T)  # mówi ciszej — kamera bliżej
    nowak_cu(p, t, T, gaze=(0.0, 0.9), fear=0.7, y=330 + 10 * k)


def s_whole(p, t, T):
    nowak_cu(p, t, T, gaze=(0.5, 0.3), fear=0.8)


def s_lunge(p, t, T):
    K.staff_room(p, t)
    k = ease(t / 0.3)
    pull = ease((t - 0.4) / 0.4)  # Kuba rzuca się, Zosia odciąga go za ramię
    K.figure(p, 900, 760, 1.0, t, "nowak", look=-0.5, lean=-0.3 * k)
    K.figure(p, 500 + 280 * k - 200 * pull, 760, 1.0, t, "kuba", look=0.6, lean=0.5 * (1 - pull), arms={"r": (120, 0)})
    K.figure(p, 300 + 160 * pull, 760, 1.0, t, "zosia", look=0.6, arms={"r": (120 * pull, 30)})


def s_irena(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(0.6, 0.0), mouth=talk(t, T), fear=0.6)
    tear = (t * 0.7) % 1.0  # łza spływa po policzku
    with K.on_face(p, "irena"):
        p.poly([(560, 360 + 140 * tear), (568, 376 + 140 * tear), (560, 384 + 140 * tear), (552, 376 + 140 * tear)], (190, 220, 235), w=2)


def s_everyone(p, t, T):
    nowak_cu(p, t, T, gaze=(0.0, 0.0), fear=0.3)


def s_how_long(p, t, T):
    K.staff_room(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.7, 0.0))


def s_nothing(p, t, T):
    k = ease((t - 0.5) / 0.5)  # po słowach spuszcza głowę
    nowak_cu(p, t, T, gaze=(0.0, 0.9 * k), fear=0.5, y=330 + 14 * k)


def s_verdict(p, t, T):
    K.staff_room(p, t)
    up = ease((t - 0.2) / 0.4)
    K.figure(p, 380, 760, 1.0, t, "kuba", look=-0.6, arms={"r": (-60, 95 - 220 * up)}, mouth=0.5 if t < T * 0.5 else 0)
    K.figure(p, 860, 760, 1.0, t, "zosia", look=0.6, arms={"r": (120, 95 - 200 * ease((t - T * 0.5) / 0.4))},
             mouth=0.5 if t > T * 0.5 else 0)


def s_henryk_takes(p, t, T):
    K.staff_room(p, t)
    k = ease(t / (T * 0.7))
    K.figure(p, 840, 760, 1.0, t, "nowak", look=-0.4)
    h = K.figure(p, 520 + 140 * k, 760, 1.0, t * 0.5, "henryk", walk=t * 0.5 if k < 0.95 else None, look=0.5,
                 arms={"r": (40 + 60 * k, 95)})


def s_lead(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    k = t / T
    K.figure_back(p, 600, 700 - 160 * k, 0.8 - 0.35 * k, t * 0.4, "henryk", walk=t * 0.4, arms={"r": (40, 90)})
    K.figure_back(p, 690, 700 - 160 * k, 0.8 - 0.35 * k, t * 0.4 + 0.2, "nowak", walk=t * 0.4 + 0.2, arms={"l": (-40, 90)})
    K.figure_back(p, 640, 860 - 120 * k, 1.1 - 0.2 * k, t * 0.4 + 0.4, "narrator", walk=t * 0.4 + 0.4)


def s_unlock(p, t, T):
    op = ease((t - T * 0.5) / 0.5)  # klucz zgrzyta, drzwi się uchylają do środka
    K.iso_door(p, t, open_=op)
    if op < 0.05:
        p.rect(790, 390, 830, 410, (170, 170, 160), w=2)  # klucz w zamku
    # dłoń z kluczem na zamku (815, 400), po otwarciu ręka opada (przegląd 13.11.2026: dłoń wisiała pod zamkiem)
    s = 1.05
    sh = (1000 - 50 * s, 780 - 268 * s)
    lock = ((815 - sh[0]) / s, (400 - sh[1]) / s)
    down = ease((t - T * 0.5 - 0.15) / 0.45)
    K.figure(p, 1000, 780, s, t, "henryk", look=-0.6,
             arms={"l": (lock[0] + (-14 - lock[0]) * down, lock[1] + (95 - lock[1]) * down)})


def s_inside(p, t, T):
    p.rect(0, 0, W, H, (150, 160, 150), w=0)
    p.rect(-20, 560, W + 20, H + 20, (110, 116, 110))
    p.rect(700, 420, 1100, 520, (200, 200, 196), w=3)  # łóżko izolatki
    p.line([(720, 520), (720, 600)], w=6)
    p.line([(1080, 520), (1080, 600)], w=6)
    k = ease(t / (T * 0.7))  # wchodzi sam i siada
    if k < 0.7:
        K.figure(p, 300 + 500 * k, 760, 1.0, t * 0.4, "nowak", walk=t * 0.4, look=0.4)
    else:
        K.sitting(p, 900, 600, 0.9, t, "nowak", gaze=(0.0, 0.6))


def s_sits_outside(p, t, T):
    K.iso_door(p, t)
    k = ease(t / (T * 0.6))  # Henryk zamyka drzwi i osuwa się po ścianie pod okienkiem
    if k < 0.6:
        K.figure(p, 980, 780, 1.05, t, "henryk", look=-0.6, arms={"l": (-120, -10)})
    else:
        K.sitting(p, 960, 700, 0.95, t, "henryk", gaze=(-0.3, -0.4))


def s_ask(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.3, 0.7))


def s_nod(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    nod = 14 * max(0.0, math.sin((t - 0.6) * 3.0)) if 0.6 < t < 0.6 + math.pi / 3 else 0.0
    K.face_cu(p, 640, 330 + nod, 1.0, "henryk", t, gaze=(-0.3, -0.5 + nod / 30))


FNS = [B.card("DZIEŃ 16"), s_put, s_knows, s_sleeve, s_bitten, s_wanted, s_cut, s_whole, s_lunge, s_irena, s_everyone,
       s_how_long, s_nothing, s_verdict, s_henryk_takes, s_lead, s_unlock, s_inside, s_sits_outside, s_ask, s_nod]
LOOK = [None] + [B.WARD] * 14 + [B.WARD] * 6
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
