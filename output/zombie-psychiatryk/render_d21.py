"""Wariant A · dzień 21 „Rój” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import random
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 21
talk = K.talk
PYJAMA = (176, 186, 196)  # piżama zarażonego z szafy (zimne otwarcie: sylwetka w oknie sali 8)


def city_night(q, t):
    K.city_far(q, t, fire=0.8, y=330)


def s_wardrobe(p, t, T):
    k = ease(t / (T * 0.6))  # drzwi szafy otwierają się na oścież, zarażony wychodzi
    K.ward_room(p, t, wardrobe=k, inner=lambda q: city_night(q, t))
    K.sheet_on_pane(p)
    if k > 0.3:
        R.zombie(p, 1060 - 120 * ease((t - 0.3) / T), 600, 0.95, t, 31, gown=PYJAMA, tilt=0.1)
    K.figure_back(p, 260, 800, 1.1, t, "narrator")


def s_hook(p, t, T):
    p.rect(0, 0, W, H, (124, 108, 86), w=0)  # drzwiczki szafy z bliska
    p.rect(-20, -20, 560, H + 20, (20, 22, 22))  # szpara: w środku ciemno
    p.line([(560, -20), (560, H + 20)], w=5)
    p.rect(700, 330, 820, 390, (150, 150, 140), w=3)  # blaszka z oczkiem
    p.ell(760, 360, 26, 26, (124, 108, 86), w=6)
    sw = 0.6 + 0.25 * math.sin(t * 5) * (1 - ease(t / T))  # haczyk kołysze się, wygięty
    p.line([(760, 360), (760 - 160 * math.cos(sw), 360 + 160 * math.sin(sw)), (760 - 190 * math.cos(sw) + 20, 360 + 150 * math.sin(sw))],
           w=14, color=(150, 150, 142))


def s_slam(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)  # korytarz C, ściana z drzwiami sali 8
    p.rect(-20, 600, W + 20, H + 20, (104, 124, 100))
    p.rect(460, 80, 860, 620, (20, 22, 22))
    k = ease(t / 0.45)
    p.poly([(460, 80), (460 + 400 * k, 80 + 30 * (1 - k)), (460 + 400 * k, 620 - 30 * (1 - k)), (460, 620)], (124, 138, 122))
    p.text(660, 50, "8", 40, fill=(40, 40, 40))
    K.figure(p, 960 - 80 * k, 800, 1.15, t, "narrator", look=-0.6, arms={"l": (-140 + 60 * k, -20)}, eyes=1.0)
    if k > 0.95:  # szczęk zamka elektromagnetycznego
        for i in range(3):
            p.line([(880 + i * 26, 300 - i * 16), (910 + i * 26, 290 - i * 16)], w=4)


def s_lean(p, t, T):
    p.rect(0, 0, W, H, (124, 138, 122), w=0)  # drzwi sali 8 od korytarza
    p.rect(300, 90, 560, 300, (20, 24, 24))
    R.zombie(p, 430, 520, 1.2, t, 31, gown=PYJAMA, tilt=0.15)  # za szybą, przycięty przez drzwi
    door = (124, 138, 122)
    for a, b, c, d in ((-50, -50, 300, H + 50), (560, -50, W + 50, H + 50), (300, -50, 560, 90), (300, 300, 560, H + 50)):
        p.rect(a, b, c, d, door, w=0, amp=0)
    p.rect(300, 90, 560, 300, None, w=6)
    br = 1.5 * math.sin(t * 7)  # oddycha szybko, plecami do drzwi
    R.nurse_face(p, 820, 380, 0.9, 0.7, t, gaze=(-0.2, 0.3), breath=br)


def s_army_gen(p, t, T):
    def gen(q):
        j = 2 * math.sin(t * 40)
        q.rect(700 + j, 255, 780 + j, 290, (90, 110, 70), w=3)  # agregat wojska przy bramie
        for k in range(5):
            y = 250 - ((t * 60 + k * 24) % 120)
            q.ell(770 + 10 * math.sin(t * 2 + k), y, 10 + k * 3, 6 + k * 2, (110, 110, 106), w=2)
    K.yard_view(p, t, beyond=gen)


def s_press(p, t, T):
    def mob(q):
        for i in range(16):
            x = 60 + i * 76
            push = 6 * math.sin(t * (2.2 + (i % 4) * 0.4) + i)  # każdy napiera w swoim rytmie
            R.zombie(q, x + push, 292, 0.2 + 0.03 * (i % 3), t, 40 + i)
    K.yard_view(p, t, beyond=mob)


def s_shots(p, t, T):
    def mob(q):
        for i in range(9):
            x = -60 + (i * 70 + t * 40) % 560  # nadchodzą drogą od lewej
            R.zombie(q, x, 288, 0.17, t, 70 + i)
        for k, x in enumerate((536, 742, 790)):  # żołnierze przy bramie, obok ciężarówki
            K.figure(q, x, 292, 0.16, t, "soldier", arms={"r": (-60, -10) if k == 0 else (40, -10)})
            if int(t * 9 + k * 3) % 4 == 0:  # błysk z lufy
                q.ell(x + (-14 if k == 0 else 12), 248, 7, 5, (255, 230, 120), w=0)
    K.yard_view(p, t, beyond=mob)


def s_hole(p, t, T):
    def mob(q):
        for i in range(4):
            x = 70 + i * 26
            R.zombie(q, x, 292, 0.2, t, 90 + i)
    K.yard_view(p, t, beyond=mob, hole=True)
    for i in range(3):  # przeszli przez dziurę i idą trawnikiem w stronę budynku
        k = ease((t - i * 0.6) / T)
        R.zombie(p, 140 + 60 * i + 120 * k, 320 + 200 * k, 0.24 + 0.4 * k, t, 95 + i)


def s_dusk(p, t, T):
    K.yard_view(p, t, night=True, dawn=0.5)
    K.crowd(p, t, n=43, seed=21, turn=0.5, area=(60, 1220, 320, 690))


def s_malec(p, t, T):
    K.listening(p, t, T, fear=0.4, gaze=(-0.6, 0.0))


def s_malec2(p, t, T):
    K.listening(p, t, T, fear=0.35, gaze=(0.3, 0.3))


def s_kuba_window(p, t, T):
    K.staff_room(p, t)
    hands = K.figure(p, 230, 760, 1.0, t, "kuba", look=-0.8, arms={"r": (-20, -70), "l": (40, 60)})
    hx, hy = 230 - 30, 760 - 336 + 6
    p.rect(hx - 40, hy - 14, hx + 10, hy + 18, (40, 40, 40), w=3)  # lornetka przy oczach
    n = min(4, int(t / T * 5))
    lx, ly = hands["l"]
    for k in range(n):  # odlicza na palcach
        p.line([(lx - 8 + k * 6, ly - 8), (lx - 8 + k * 6, ly - 26)], w=4, color=K.WHO["kuba"]["skin"])


def s_sill(p, t, T):
    p.rect(0, 0, W, H, (216, 214, 204), w=0)  # parapet z bliska
    p.rect(-20, 520, W + 20, H + 20, (190, 188, 178))
    n = min(43, int(43 * t / (T * 0.7)))
    for m in range(n):
        g, k = divmod(m, 5)
        x0, y0 = 120 + (g % 5) * 150, 140 + (g // 5) * 120
        if k < 4:
            p.line([(x0 + k * 20, y0), (x0 + 4 + k * 20, y0 + 70)], w=3, color=(70, 70, 70))
        else:
            p.line([(x0 - 10, y0 + 50), (x0 + 80, y0 + 20)], w=3, color=(70, 70, 70))
    if n >= 43:
        p.text(1000, 290, "43", 90, fill=(60, 60, 60))
    p.rect(880, 560, 1180, 660, (40, 40, 40), w=3)  # lornetka
    p.ell(940, 610, 40, 40, (70, 80, 90), w=3)
    p.ell(1120, 610, 40, 40, (70, 80, 90), w=3)


def s_zosia(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.3, 0.2), mouth=talk(t, T), fear=0.35)


def s_piano(p, t, T):
    K.piano_room(p, t)
    lift = 4 * math.sin(t * 2)  # palce dotykają klawiszy, nie naciskają
    K.figure_back(p, 640, 840, 1.05, t, "henryk", arms={"l": (-30, -26 + lift), "r": (30, -26 - lift)})


def s_ask(p, t, T):
    K.piano_room(p, t)
    R.nurse_face(p, 640, 330, 1.0, 0.4 if 0.3 < t < T - 0.4 else 0.3, t, gaze=(0.5, 0.2))


def s_henryk(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.5, 0.1), mouth=talk(t, T, speed=6) * 0.8)


def s_wires(p, t, T):
    K.porter_lodge(p, t, wires=0.0)
    sw = 6 * math.sin(t * 1.4)
    for k in range(5):  # końcówki wyrwanych przewodów kołyszą się
        x = 820 + k * 50 + 20
        p.line([(x, 560 + 40), (x + sw, 640)], w=6, color=((200, 60, 60), (60, 60, 200), (220, 220, 220), (60, 160, 60), (40, 40, 40))[k])


def s_henryk2(p, t, T):
    K.piano_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.2, 0.0), mouth=talk(t, T, speed=6) * 0.8)
    k = ease((t - T * 0.5) / 0.5)  # unosi palec
    K.limb(p, (880, H + 60), (840, 560 - 120 * k), 70, K.WHO["henryk"]["top"], outline=4)
    p.ell(840, 556 - 120 * k, 30, 26, K.WHO["henryk"]["skin"])
    p.line([(840, 540 - 120 * k), (842, 490 - 120 * k)], w=12, color=K.WHO["henryk"]["skin"])


def s_understand(p, t, T):
    K.piano_room(p, t)
    k = ease((t - 0.4) / 1.2)
    R.nurse_face(p, 640, 330, 1.0, 0.3 + 0.35 * k, t, gaze=(0.0, 0.7 * k))


FNS = [B.card("DZIEŃ 21"), s_wardrobe, s_hook, s_slam, s_lean, s_army_gen, s_press, s_shots, s_hole, s_dusk, s_malec, s_malec2,
       s_kuba_window, s_sill, s_zosia, s_piano, s_ask, s_henryk, s_wires, s_henryk2, s_understand]
LOOK = [None] + [B.NIGHT] * 4 + [B.DAY] * 4 + [B.NIGHT] + [B.WARD] * 11
CAM = {5: {"zoom": 2.2, "cx": 720, "cy": 280}, 6: {"zoom": 2.0, "cx": 420, "cy": 300}, 7: {"zoom": 2.3, "cx": 600, "cy": 270},
       8: {"zoom": 1.9, "cx": 300, "cy": 360}, 18: {"zoom": 1.5, "cx": 930, "cy": 470}}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
