"""Wariant A · dzień 18 „Henryk mówi” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 18


def talk(t, T, a=0.3, b=0.4, speed=7):
    return 0.5 + 0.5 * math.sin(t * speed) if a < t < T - b else 0.0


def henryk_says(p, t, T, gaze=(0.3, 0.1), speed=6):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=gaze, mouth=talk(t, T, speed=speed) * 0.8)  # mówi powoli, chrapliwie


def s_wakes(p, t, T):
    K.staff_room(p, t)
    k = ease((t - 0.4) / 0.8)  # leży na kanapie, otwiera oczy
    p.poly([(420, 520), (780, 520), (780, 470), (420, 470)], K.WHO["henryk"]["top"], w=3)
    p.ell(400, 480, 44, 40, K.WHO["henryk"]["skin"])
    for side in (-1, 1):
        if k < 0.5:
            p.line([(390 + side * 14, 476), (402 + side * 14, 476)], w=3)
        else:
            p.ell(396 + side * 14, 476, 6, 5, (246, 246, 240), w=2)


def s_tea(p, t, T):
    p.rect(0, 0, W, H, (190, 186, 170), w=0)
    p.ell(760, 300, 120, 90, (220, 220, 216), w=4)  # czajnik z dyżurki
    p.poly([(640, 300), (560, 250), (550, 270), (630, 320)], (220, 220, 216), w=3)
    k = ease(t / (T * 0.7))
    p.line([(560, 262), (500, 430)], w=8 * (1 - k * 0.5), color=(170, 120, 70))  # strumień herbaty
    p.rect(420, 430, 580, 600, (236, 236, 232), w=4)  # kubek
    p.rect(426, 580 - 140 * k, 574, 596, (170, 120, 70), w=0)
    for i in range(4):
        y = 420 - ((t * 50 + i * 40) % 160)
        p.ell(500 + 20 * math.sin(t * 2 + i), y, 20 + 4 * i, 10, None, w=2, color=(240, 240, 240))


def s_drinks(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.0, 0.6))
    lift = math.sin(min(1.0, t / T) * math.pi)  # kubek wędruje do ust bardzo powoli
    p.rect(560, 520 - 100 * lift, 700, 660 - 100 * lift, (236, 236, 232), w=4)
    K.limb(p, (380, H + 80), (560, 600 - 100 * lift), 80, K.WHO["henryk"]["top"], outline=4)


def s_name(p, t, T):
    henryk_says(p, t, T, gaze=(0.0, 0.0), speed=5)


def s_music(p, t, T):
    henryk_says(p, t, T, gaze=(0.4, -0.2))


def s_wife(p, t, T):
    henryk_says(p, t, T, gaze=(-0.2, 0.7))


def s_saw(p, t, T):
    henryk_says(p, t, T, gaze=(0.6, 0.0))


def s_scream(p, t, T):
    henryk_says(p, t, T, gaze=(0.0, 0.5))


def s_sorry(p, t, T):
    K.staff_room(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(-0.6, 0.6))


def s_shakes(p, t, T):
    K.staff_room(p, t)
    shake = 14 * math.sin(t * 5) * (1 - ease((t - 0.8) / 0.4))
    K.face_cu(p, 640 + shake, 330, 1.0, "henryk", t, gaze=(0.4, 0.0), mouth=talk(t, T, 0.9, 0.3, 6) * 0.8)


def s_irena(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "irena", t, gaze=(0.6, 0.0), mouth=talk(t, T), fear=0.1)


def s_breath_music(p, t, T):
    henryk_says(p, t, T, gaze=(0.0, -0.3))


def s_diaphragm(p, t, T):
    K.staff_room(p, t)
    br = math.sin(t * 2 * math.pi / 4)  # wszyscy w jednym rytmie, dłonie na brzuchu
    for i, (who, x) in enumerate((("zosia", 220), ("narrator", 430), ("henryk", 640), ("kuba", 850), ("irena", 1060))):
        h = K.figure(p, x, 760, 0.9, t, who, look=0.0, arms={"l": (40, 160 + 6 * br), "r": (-40, 160 + 6 * br)})


def s_kuba_laughs(p, t, T):
    K.staff_room(p, t)
    laugh = 1 - ease((t - T * 0.4) / 0.5)  # najpierw śmiech, potem cisza i spokojny oddech
    K.face_cu(p, 640, 330 + 4 * math.sin(t * 14) * laugh, 1.0, "kuba", t, gaze=(0.0, -0.3 * laugh),
              mouth=(0.5 + 0.5 * abs(math.sin(t * 8))) * laugh, breath=math.sin(t * 1.5) * (1 - laugh))


def s_piano(p, t, T):
    p.rect(0, 0, W, H, (90, 92, 96), w=0)
    p.rect(-20, 560, W + 20, H + 20, (70, 70, 72))
    p.rect(420, 260, 860, 560, (70, 52, 40))  # pianino
    p.rect(420, 260, 860, 290, (84, 64, 50))
    p.rect(450, 400, 830, 430, (230, 226, 210))  # odsłonięte klawisze
    for i in range(1, 19):
        p.line([(450 + i * 21, 400), (450 + i * 21, 430)], w=1.5)
    k = ease(t / (T * 0.6))  # siada; dłonie zawisają nad klawiszami
    K.figure_back(p, 640, 760 + 60 * k, 1.0, t, "henryk", arms={"l": (-30, -10 - 20 * k), "r": (30, -10 - 20 * k)})


def s_play_when(p, t, T):
    p.rect(0, 0, W, H, (90, 92, 96), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.4, 0.4), mouth=talk(t, T, speed=5) * 0.8)


def s_note(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    K.paper(p, 600, 340, ["„Zagram, kiedy trzeba", "będzie was zawołać.”"], w=600, h=240)
    x = 820
    K.limb(p, (x + 380, H + 80), (x + 30, 460), 80, K.narr_sleeve(), outline=4)
    p.ell(x + 20, 450, 40, 30, K.SKIN)
    k = ease(t / T)
    p.line([(x, 430), (x - 30 - 6 * math.sin(t * 9), 400)], w=6, color=(40, 40, 120))
    p.line([(380, 420), (380 + 400 * k, 420)], w=3, color=(40, 40, 120))  # podkreśla


def s_silence(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    p.rect(300, 140, 980, 520, (20, 24, 34), w=8)
    for k in range(1, 4):
        p.line([(300 + k * 170, 140), (300 + k * 170, 520)], w=10, color=(46, 48, 50))
    if t > T * 0.5:  # w miejscu, gdzie zwykle grał megafon, tylko psy w oddali
        p.ell(900, 470, 4, 4, (200, 200, 190), w=0)


def s_trucks_leave(p, t, T):
    k = ease(t / T)  # dwie z trzech ciężarówek odjeżdżają w prawo, za kadr; zostaje jedna (księga świata)
    K.basement_window(p, lambda q: K.yard_trucks(q, t, soldiers=False, wire=1.0, trucks=(180,),
                                                 moving=(640 + 900 * k, 1000 + 900 * k)))


FNS = [B.card("DZIEŃ 18"), s_wakes, s_tea, s_drinks, s_name, s_music, s_wife, s_saw, s_scream, s_sorry, s_shakes, s_irena,
       s_breath_music, s_diaphragm, s_kuba_laughs, s_piano, s_play_when, s_note, s_silence, s_trucks_leave]
LOOK = [None] + [B.WARD] * 14 + [B.BASE] * 3 + [B.NIGHT] * 2
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
