"""Wariant A · dzień 2 „Kordon” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease, noise

DAY = 2



def walkie(p, x, y, s=1.0):
    p.rect(x - 14 * s, y - 30 * s, x + 14 * s, y + 30 * s, (40, 42, 46), w=3)
    p.line([(x + 8 * s, y - 30 * s), (x + 8 * s, y - 62 * s)], w=5 * s)
    p.rect(x - 9 * s, y - 20 * s, x + 9 * s, y - 4 * s, (120, 160, 120), w=2)

def s_wake(p, t, T):
    K.pharmacy_inside(p, t)
    p.glow([(90, 60), (250, 60), (560, 620), (300, 620)], (230, 236, 220, 40))
    up = ease(t / (T * 0.8))
    K.sitting(p, 560, 720 - 30 * (1 - up), 0.95, t, "narrator", look=-0.3, eyes=0.3 + 0.7 * up)


def s_three(p, t, T):
    K.pharmacy_inside(p, t)
    wr = math.sin(t * 7) * 10 if t < T * 0.7 else 0  # Zosia pisze przy ladzie
    K.figure(p, 150, 600, 0.8, t, "zosia", look=0.6, gaze=(0.6, 1.0), arms={"r": (70 + wr, 30)})
    p.rect(-20, 430, 270, 600, (128, 98, 70))  # lada przed Zosią
    p.line([(-20, 430), (270, 430)], w=4)
    K.sitting(p, 820, 640, 0.7, t, "henryk", look=0.8, gaze=(1.0, 0.0))
    turn = ease((t - T * 0.45) / 0.5)  # narrator odwraca głowę do Zosi
    K.sitting(p, 520, 680, 0.75, t, "narrator", look=-0.5 * turn, gaze=(-0.9 * turn, 0.0))


def s_list(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    lines = ["2 × woda", "suchary", "leki"]
    n = min(3, int(t / (T * 0.8) * 3) + 1)  # Zosia dopisuje kolejne linijki
    K.paper(p, 560, 330, lines[:n], hand=True)
    for k, x in enumerate((960, 1060)):
        p.rect(x - 34, 180, x + 34, 420, (190, 214, 226), w=3)
        p.rect(x - 20, 150, x + 20, 180, (60, 110, 160), w=3)
    p.rect(860, 470, 1100, 560, (210, 190, 150), w=3)


def s_count(p, t, T):
    K.pharmacy_front(p, t)
    talk = 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.0, 0.5), mouth=talk, fear=0.3)
    n = min(3, 1 + int(t / (T / 3)))  # liczy na palcach
    hx, hy = 860, 560
    p.ell(hx, hy, 50, 44, K.WHO["zosia"]["skin"])
    for i in range(n):
        p.line([(hx - 30 + i * 22, hy - 30), (hx - 34 + i * 22, hy - 90)], w=16, color=K.WHO["zosia"]["skin"])
        p.line([(hx - 30 + i * 22, hy - 30), (hx - 34 + i * 22, hy - 90)], w=2.5)
    K.limb(p, (hx + 60, H + 60), (hx + 20, hy + 30), 70, (52, 62, 92), outline=4)


def s_henryk_door(p, t, T):
    K.pharmacy_inside(p, t)
    snap = ease((t - T * 0.6) / 0.25)  # coś za drzwiami: wzrok skacze w bok, twarz zostaje
    K.face_cu(p, 640, 320, 1.0, "henryk", t, gaze=(0.8 * snap, 0.0), fear=0.0)


def s_trucks(p, t, T):
    def inner(q):
        K.yard_trucks(q, t)
        K.ambulance(q, 900, 560, 0.5)  # porzucona karetka przed wejściem (zasiew: dzień 10)
        x = 1500 - 420 * ease(t / (T * 0.85))  # ostatnia ciężarówka dojeżdża i staje
        q.rect(x - 130, 330, x + 60, 460, (86, 100, 70))
        q.rect(x - 220, 370, x - 130, 460, (78, 92, 64))
        for wx in (x - 180, x - 60, x + 30):
            q.ell(wx, 462, 26, 26, (36, 36, 34))
    K.basement_window(p, inner)


def s_wire(p, t, T):
    K.yard_trucks(p, t, soldiers=False, wire=0.3 + 0.7 * ease(t / T))
    hands = []
    for k, x0 in enumerate((260, 760)):
        x = x0 + 220 * ease(t / T)
        h = K.figure(p, x, 700, 0.85, t, "soldier", walk=t * 0.6, arms={"l": (-60, 40), "r": (60, 40)})
        hands += [h["l"], h["r"]]
    # rozwijany zasiek: zwoje drutu trzymane w dłoniach, ciągną się między żołnierzami
    for a, b in ((hands[0], hands[1]), (hands[1], hands[2]), (hands[2], hands[3])):
        n = 6
        for i in range(n):
            cx = a[0] + (b[0] - a[0]) * (i + 0.5) / n
            cy = a[1] + (b[1] - a[1]) * (i + 0.5) / n
            p.ell(cx, cy + 10, (b[0] - a[0]) / n * 0.6, 26, None, w=2.5)

def s_megaphone(p, t, T):
    K.yard_trucks(p, t, soldiers=False, wire=1.0)
    K.figure(p, 600, 1080, 2.0, t, "soldier", arms={"r": (20, -20)})
    mx, my = 600 + 50 * 2 + 20 * 2, 1080 - 268 * 2 - 20 * 2
    p.poly([(mx - 20, my - 30), (mx + 150, my - 90), (mx + 150, my + 60), (mx - 20, my + 20)], (200, 196, 180), w=4)
    if int(t * 4) % 2 == 0:
        for k in range(3):
            p.line([(mx + 180 + k * 30, my - 50 - k * 10), (mx + 200 + k * 30, my - 70 - k * 14)], w=4)


def s_zosia_up(p, t, T):
    K.pharmacy_front(p, t)
    talk = 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0
    K.face_cu(p, 640, 340, 1.0, "zosia", t, gaze=(-0.4, -1.0), mouth=talk, fear=0.5)


def s_walk_day(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0], doors_open=0.9)
    k = t / T
    for who, dx in (("henryk", -50), ("narrator", 60)):
        K.figure(p, 640 + dx, 470 + 200 * k, 0.5 + 0.3 * k, t * 0.6, who, walk=t * 0.6)


def s_room(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 520, W, H, (104, 124, 100), w=0)
    for i, (x, s) in enumerate(((420, 0.9), (640, 1.0), (860, 0.85))):  # twarzami do ściany, każdy inaczej
        K.zombie_back(p, x, 640, s, t + i * 0.7, 70 + i)
    for x0, x1 in ((0, 250), (1030, W)):  # framuga otwartych drzwi sali, przed nimi
        p.rect(x0, -20, x1, H + 20, (124, 138, 122))
    p.line([(250, -20), (250, H + 20)], w=5)
    p.line([(1030, -20), (1030, H + 20)], w=5)


def s_head_back(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    K.zombie_back(p, 640, 1120, 3.4, t, 72)


def s_sad(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    sw = math.sin(min(1.0, max(0.0, (t - T * 0.55) / 0.5)) * math.pi)  # przełyka ślinę
    R.nurse_face(p, 640, 320, 1.0, 0.3, t, gaze=(-0.6, 0.6), swallow=sw)


def s_point(p, t, T):
    R.corridor(p, t, [0, 0, 0, 0], doors_open=0.9)
    shake = math.sin(t * 7) * (1 - ease((t - 0.8) / 0.3))
    K.figure(p, 560, 760, 1.05, t, "henryk", look=shake * 0.6, arms={"r": (150, -30)} if t > 0.8 else None)
    K.figure(p, 900, 760, 1.0, t, "narrator", look=-0.7)


def s_handset_day(p, t, T):
    K.phone_detail(p, t, ring=False)
    x = 200 + 160 * t / T  # smuga słońca przesuwa się po blacie, kurz w powietrzu
    p.glow([(x, -20), (x + 260, -20), (x + 520, H + 20), (x + 200, H + 20)], (255, 246, 210, 26))
    for i in range(14):
        r = R.random.Random(i)
        px = x + 120 + r.uniform(0, 260) + 30 * math.sin(t * 0.7 + i)
        py = r.uniform(80, 640) - 20 * t
        p.ell(px, py % 720, 2.5, 2.5, (250, 244, 220), w=0)


def s_pack(p, t, T):
    K.duty_room(p, dark=False)
    k = ease(t / T)
    reach = math.sin(min(1.0, k * 3 % 1.0) * math.pi)  # sięga po kolejne rzeczy
    K.figure(p, 640, K.DESK_STAND, K.DESK_S, t, "narrator", look=0.0, gaze=(0, 1),
             arms={"l": (40, 60 - 10 * reach), "r": (-40 + 20 * reach, 60)})  # za biurkiem, stopy za przednimi nogami
    K.duty_desk(p)
    p.poly([(560, 420), (720, 420), (700, 360 + 20 * k), (580, 360 + 20 * k)], (110, 120, 96), w=3)  # torba
    if k < 0.35:
        p.ell(520, 400, 26, 22, (210, 210, 206), w=3)  # czajnik jeszcze na blacie
    if k < 0.7:  # dwie krótkofalówki w ładowarce (zasiew: dni 13, 14, 29)
        p.rect(730, 400, 790, 420, (60, 60, 60), w=2)
        walkie(p, 745, 380, 0.6)
        walkie(p, 772, 380, 0.6)


def s_bag(p, t, T):
    K.duty_room(p, dark=False)
    k = ease((t - 0.1) / (T * 0.7))  # zdejmuje kurtkę z wieszaka i ją zakłada (zasiew: dzień 10)
    p.line([(980, 250), (1000, 250)], w=6)
    if k < 0.3:
        p.poly([(960, 260), (1020, 260), (1040, 420), (940, 420)], (58, 66, 78))
    h = K.figure(p, 700, 680, 0.9, t, "narrator", look=0.3, arms={"r": (40 + 60 * (1 - k), 40 - 120 * (1 - k)), "l": (-14, 95)})
    if k >= 0.3:
        top, sh = 680 - 280 * 0.9, 50 * 0.9
        on = ease((k - 0.3) / 0.7)
        p.poly([(700 - sh - 6, top + 2), (700 + sh + 6, top + 2), (700 + 56 * 0.9 + 8, 680 - 108), (700 - 56 * 0.9 - 8, 680 - 108)],
               (58, 66, 78))  # kurtka na mundurku
        p.line([(700, top + 10), (700, 680 - 112)], w=2.5)
        if on > 0.5:
            for side in (-1, 1):
                p.poly([(700 + side * 40, top + 6), (700 + side * 18, top + 6), (700 + side * 10, top + 40)], (90, 98, 110), w=2)

def s_dusk(p, t, T):
    offs = (0.5, 1.4, 2.0, 2.9)  # świetlówki gasną jedna po drugiej, od najbliższej
    R.corridor(p, t, [1 if t < o else 0 for o in offs], doors_open=0.9)
    for x, y in ((300, 230), (980, 230), (640, 280)):
        p.rect(x - 22, y - 10, x + 22, y + 10, (120, 230, 150), w=2)


def s_note_dark(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    wr = 12 * math.sin(t * 8) if t < T * 0.75 else 0  # narrator zapisuje godzinę w notesie
    K.figure(p, 520, 720, 1.0, t, "narrator", look=0.2, gaze=(0.3, 1.0), arms={"l": (60, 10), "r": (-40 + wr, 20)})
    p.rect(520 - 40, 720 - 268 + 10, 520 + 40, 720 - 268 + 60, (236, 232, 214), w=2)  # notes
    h = K.figure(p, 800, 720, 1.0, t, "zosia", look=-0.4, mouth=0.4 if 0.4 < t < 1.6 else 0.0, arms={"l": (-60, 30)})
    lx, ly = h["l"]
    p.rect(lx - 16, ly - 34, lx + 16, ly + 6, (90, 92, 96), w=3)  # lampa akumulatorowa w dłoni Zosi
    p.rect(lx - 12, ly - 30, lx + 12, ly - 14, (250, 236, 170), w=2)
    fl = 54 + 10 * R.noise(t, 31, 3)
    p.glow([(lx - 40, ly - 40), (lx + 40, ly - 40), (lx + 220, 720), (lx - 260, 720)], (255, 240, 170, int(fl)))


def s_up(p, t, T):
    p.rect(0, 0, W, H, (30, 34, 40), w=0)
    k = ease((t - 0.3) / 1.0)  # wzrok podnosi się do sufitu, oczy się rozszerzają
    R.nurse_face(p, 640, 340, 1.0, 0.35 + 0.35 * k, t, gaze=(0.2, -1.0 * k), blink_k=0.0)


def s_crack(p, t, T):
    K.ceiling_crack(p, t)


def s_whisper(p, t, T):
    p.rect(0, 0, W, H, (30, 34, 40), w=0)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.0, 0.0), mouth=0.0, fear=0.5)
    k = ease(t / 0.6)  # palec wędruje do ust
    y0 = 470 + 200 * (1 - k)
    K.limb(p, (700, H + 60), (650, y0 + 10), 60, (52, 62, 92), outline=4)
    p.line([(640, y0 - 90), (640, y0 - 10)], w=18, color=K.WHO["zosia"]["skin"])
    p.line([(640, y0 - 90), (640, y0 - 10)], w=2.5)


def s_eyes(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    k = ease((t - T * 0.4) / 0.6)  # źrenice powoli schodzą prosto w kamerę
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.5 * (1 - k), -0.4 * (1 - k)))


def s_pray(p, t, T):
    p.rect(0, 0, W, H, (30, 34, 40), w=0)
    low = 14 * ease(t / T)  # głowa opada coraz niżej
    R.nurse_face(p, 640, 320 + low, 1.0, 0.25, t, gaze=(0, 0), blink_k=1.0, breath=B.breathing(t, 0.25) * 0.5,
                 body=(640, 320))


FNS = [B.card("DZIEŃ 2"), s_wake, s_three, s_list, s_count, s_henryk_door, s_trucks, s_wire, s_megaphone, s_zosia_up,
       s_walk_day, s_room, s_head_back, s_sad, s_point, s_handset_day, s_pack, s_bag,
       s_dusk, s_note_dark, s_up, s_crack, s_whisper, s_eyes, s_pray]
DAYL = ((1.25, 1.25, 1.2), None)  # dyżurka i telefon w dzień
LOOK = [None] + [B.BASE] * 5 + [B.DAY, B.DAY, B.DAY, B.BASE] + [B.WARD] * 5 + [DAYL, B.DAY, B.BASE] + \
       [B.NIGHT] * 7
CAM = {12: dict(cy=300)}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
