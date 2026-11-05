"""Wariant A · dzień 4 „Kuchnia” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease, noise

DAY = 4
CAN = (196, 70, 60)


def can(p, x, y, r=40, rot=0.0):
    p.ell(x, y, r, r * 1.2, CAN, rot=rot)
    p.ell(x, y, r * 0.55, r * 0.66, (210, 210, 200), w=2, rot=rot)


def sack(p, x, y, s=1.0):
    p.poly([(x - 90 * s, y - 120 * s), (x + 90 * s, y - 120 * s), (x + 120 * s, y + 60 * s), (x - 120 * s, y + 60 * s)],
           (176, 158, 120), w=4)
    p.line([(x - 70 * s, y - 112 * s), (x + 70 * s, y - 112 * s)], w=6, color=(120, 100, 70))



def s_piano(p, t, T):
    p.rect(0, 0, W, H, (150, 160, 150), w=0)
    p.rect(-20, 560, W + 20, H + 20, (110, 112, 104))
    p.rect(300, 120, 980, 600, (40, 44, 42))  # uchylone drzwi świetlicy: w środku ciemno
    p.rect(420, 300, 860, 560, (70, 52, 40))  # pianino
    p.rect(420, 300, 860, 330, (84, 64, 50))
    p.rect(450, 420, 830, 450, (90, 70, 54))  # zamknięta klapa
    for x0, y0, x1, y1 in ((-50, -50, 300, H + 50), (980, -50, W + 50, H + 50), (300, -50, 980, 120)):
        p.rect(x0, y0, x1, y1, (150, 160, 150), w=0, amp=0)
    p.rect(300, 120, 980, 600, None, w=8)
    k = ease((t - 0.3) / (T * 0.7))  # palec Henryka przesuwa się po klapie
    fx = 470 + 300 * k
    K.limb(p, (fx - 520, H + 80), (fx - 20, 440), 90, K.WHO["henryk"]["top"], outline=4)
    p.ell(fx, 432, 44, 28, K.WHO["henryk"]["skin"])
    p.line([(fx + 30, 430), (fx + 60, 428)], w=12, color=K.WHO["henryk"]["skin"])
    p.line([(470, 418), (fx, 418)], w=2, color=(120, 100, 80))  # ślad w kurzu

def s_to_phone(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1], doors_open=0.9)
    p.rect(610, 290, 670, 330, (182, 200, 168), w=3)
    for i, (dx, s, ph) in enumerate(((-120, 0.7, 0.0), (60, 0.62, 0.4), (-10, 0.55, 0.8), (130, 0.5, 0.3))):
        k = ease((t - ph * 0.5) / T)
        K.zombie_back(p, 640 + dx * (1 - 0.6 * k), 720 - 200 * s - 120 * k, s * (1 - 0.35 * k), t + ph, 90 + i, walk=t * 0.7)


def s_last_in(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 560, W, H, (104, 124, 100), w=0)
    p.rect(470, 120, 810, 600, (40, 50, 60))  # wnętrze dyżurki za drzwiami
    k = ease(t / T)
    K.zombie_back(p, 640, 640 - 60 * k, 1.2 - 0.5 * k, t, 95, walk=t * 0.7)
    for x0, y0, x1, y1 in ((0, 0, 470, H), (810, 0, W, H), (470, 0, 810, 120)):  # ściana wokół drzwi zasłania wchodzącego
        p.rect(x0, y0, x1, y1, (150, 166, 140), w=0, amp=0)
    p.rect(0, 560, 470, H, (104, 124, 100), w=0, amp=0)
    p.rect(810, 560, W, H, (104, 124, 100), w=0, amp=0)
    p.rect(450, 100, 830, 600, None, w=8)
    p.rect(520, 160, 760, 300, (182, 200, 168), w=4)  # szyba w otwartym skrzydle — tu odbija się korytarz


def s_conn_walk(p, t, T):
    K.connector(p, t)
    k = t / T
    for who, dx in (("henryk", -40), ("narrator", 70)):
        K.figure(p, 760 + dx - 120 * k, 470 + 230 * k, 0.5 + 0.35 * k, t * 0.6, who, walk=t * 0.6)


def tall_window(p, inner):
    inner(p)
    wall = (130, 146, 132)
    for x0, y0, x1, y1 in ((-50, -50, 340, H + 50), (940, -50, W + 50, H + 50), (340, -50, 940, 60), (340, 640, 940, H + 50)):
        p.rect(x0, y0, x1, y1, wall, w=0, amp=0)
    p.line([(640, 60), (640, 640)], w=10, color=(90, 96, 90))
    p.rect(340, 60, 940, 640, None, w=10)


def s_pov_soldiers(p, t, T):
    def inner(q):
        K.yard_trucks(q, t, soldiers=False, wire=1.0)
        for k, x in enumerate((520, 760)):
            low = ease((t - T * (0.45 + 0.2 * k)) / 0.4)  # opuszczają lornetki, każdy w swoim czasie
            K.figure(q, x, 610, 0.6, t, "soldier", arms={"l": (40 - 30 * low, -30 + 120 * low), "r": (-40 + 30 * low, -30 + 120 * low)})
            if low < 0.5:
                q.rect(x - 22, 610 - 268 * 0.6 - 30, x + 22, 610 - 268 * 0.6 - 10, (40, 40, 40), w=2)
    tall_window(p, inner)


def s_soldier_hand(p, t, T):
    K.yard_trucks(p, t, soldiers=False, wire=1.0)
    up = ease((t - 0.4) / 0.6)
    K.figure(p, 640, 1000, 1.7, t, "soldier", arms={"r": (40 + 20 * up, 95 - 230 * up)})
    for x in range(0, W + 1, 70):  # siatka płotu przed nim
        p.line([(x, 380), (x + 70, 720)], w=2.5, color=(70, 76, 72), amp=0.4)
        p.line([(x + 70, 380), (x, 720)], w=2.5, color=(70, 76, 72), amp=0.4)


def s_kitchen(p, t, T):
    K.kitchen(p, t)
    for i in range(3):  # muchy nad kotłami
        a = t * (2.3 + i * 0.7) + i * 2
        p.ell(400 + i * 120 + 70 * math.cos(a), 200 + 40 * math.sin(a * 1.3), 4, 3, (30, 30, 30), w=0)
    if T * 0.55 < t < T * 0.55 + 0.25:  # pokrywka kotła podskakuje
        p.ell(400, 244, 92, 20, (140, 146, 150), w=3)


def s_pack_cans(p, t, T):
    K.kitchen(p, t)
    K.figure(p, 420, 780, 1.05, t, "narrator", look=0.4, gaze=(0.4, 1.0), arms={"r": (60 + 30 * math.sin(t * 4), 170)})
    sack(p, 560, 640)
    for k in range(int(3 + 4 * ease(t / T))):
        can(p, 520 + (k % 3) * 40, 560 - (k // 3) * 30, r=18)


def s_tap(p, t, T):
    K.kitchen(p, t)
    p.rect(700, 300, 760, 330, (170, 176, 180), w=3)
    cough = 0.4 + 0.6 * abs(R.noise(t, 41, 5))  # woda charczy: strumień rwie się i wraca
    p.line([(740, 330), (740, 430)], w=max(3, 12 * cough), color=(170, 200, 220))
    p.rect(690, 430, 800, 600, (200, 210, 230), w=3)  # kanister
    lvl = 590 - 140 * ease(t / T)
    p.rect(694, lvl, 796, 596, (150, 186, 214), w=0)  # poziom wody rośnie
    K.figure(p, 560, 800, 1.05, t, "henryk", look=0.6, gaze=(0.6, 0.6), arms={"r": (150, 40)})


def s_tap_off(p, t, T):
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    for x in range(0, W, 80):
        p.line([(x, 0), (x, H)], w=1.5, color=(160, 168, 162), amp=0.4)
    p.rect(300, 250, 980, 330, (170, 176, 180), w=4)  # rura
    p.rect(860, 330, 920, 430, (170, 176, 180), w=3)  # wylewka
    flow = 1 - 0.6 * ease(t / T)
    p.line([(890, 430), (890, H + 10)], w=max(3, 26 * flow), color=(170, 200, 220))
    ang = ease(t / T) * 1.0
    cx, cy = 600, 220  # pokrętło: krzyżak na trzpieniu
    p.rect(585, 220, 615, 250, (150, 156, 160), w=3)
    for a in (ang, ang + math.pi / 2):
        p.line([(cx - 70 * math.cos(a), cy - 22 * math.sin(a)), (cx + 70 * math.cos(a), cy + 22 * math.sin(a))], w=16, color=(200, 60, 60))
        p.line([(cx - 70 * math.cos(a), cy - 22 * math.sin(a)), (cx + 70 * math.cos(a), cy + 22 * math.sin(a))], w=2.5)
    skin = K.WHO["henryk"]["skin"]  # dłoń obejmuje pokrętło od góry
    K.limb(p, (cx - 420, -60), (cx - 40, cy - 40), 80, K.WHO["henryk"]["top"], outline=4)
    p.ell(cx - 10, cy - 30, 66, 40, skin)
    for i in range(4):
        K.limb(p, (cx - 50 + i * 30, cy - 30), (cx - 44 + i * 30, cy + 10), 22, skin, outline=2.5)

def s_fridge_bang(p, t, T):
    j = 8 if int(t * 6) % 3 == 0 else 0
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    p.rect(300 + j, 60, 980 + j, H + 20, (176, 184, 188))
    p.rect(560 + j, 160, 720 + j, 300, (40, 54, 70), w=5)
    p.rect(900 + j, 360, 940 + j, 460, (90, 90, 90))
    if j:
        for k in range(4):
            a = k * math.pi / 2 + 0.6
            p.line([(640 + 220 * math.cos(a), 420 + 180 * math.sin(a)), (640 + 280 * math.cos(a), 420 + 230 * math.sin(a))], w=5)


def s_fridge_win(p, t, T):
    K.fridge_window(p, t)


def s_handle(p, t, T):
    p.rect(0, 0, W, H, (176, 184, 188), w=0)
    p.rect(700, 260, 780, 520, (90, 90, 90), w=4)
    reach = ease(t / T)
    hx = 360 + 280 * reach
    K.limb(p, (-60, 560), (hx - 60, 400), 110, K.narr_sleeve(), outline=4)
    p.ell(hx, 390, 70, 52, K.SKIN)


def s_no(p, t, T):
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(math.sin(t * 6) * 0.8, 0.0))


def s_can_falls(p, t, T):
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    p.rect(-20, 520, W + 20, H + 20, (150, 156, 150))
    sack(p, 640, 280, s=1.6)
    k = ease(t / (T * 0.8))
    can(p, 700 + 60 * k, 360 + 300 * k * k, r=46, rot=3 * k)


def s_can_rolls(p, t, T):
    p.rect(0, 0, W, H, (186, 190, 184), w=0)
    for x in range(-200, W + 200, 160):
        p.line([(x, 0), (x - 120, H)], w=3, color=(140, 146, 140))
    for y in range(0, H, 140):
        p.line([(0, y), (W, y)], w=3, color=(140, 146, 140))
    k = t / T
    x = 200 + 900 * k
    can(p, x, 420, r=60, rot=8 * k)
    for i in range(3):
        p.line([(x - 90 - i * 30, 380 + i * 30), (x - 140 - i * 30, 380 + i * 30)], w=4)


def s_moan(p, t, T):
    K.connector(p, t)
    if int(t * 3) % 2 == 0:
        for k in range(3):
            p.ell(820, 330, 40 + k * 26, 30 + k * 20, None, w=3)


def s_run(p, t, T):
    K.connector(p, t)
    k = t / T
    h = K.figure(p, 700 - 80 * k, 560 + 160 * k, 0.75 + 0.3 * k, t * 1.8, "narrator", walk=t * 1.8, arms={"r": (40, 60)})
    sack(p, h["r"][0] + 40, h["r"][1] + 30, s=0.5)


def s_calm(p, t, T):
    K.connector(p, t)
    k = t / T
    K.figure(p, 760 - 40 * k, 520 + 80 * k, 0.65 + 0.12 * k, t * 0.5, "henryk", walk=t * 0.5)


def s_press(p, t, T):
    p.rect(0, 0, W, H, (130, 146, 132), w=0)
    k = ease(t / 0.35)  # ręka Henryka wjeżdża i dociska go do ściany
    R.nurse_face(p, 700 + 26 * k, 320, 1.0, 0.8, t, gaze=(-0.8, 0.0), body=(700 + 20 * k, 320))
    K.limb(p, (-60, 520), (360 + 200 * k, 600), 80, K.WHO["henryk"]["top"], outline=4)
    p.ell(400 + 180 * k, 600, 60, 46, K.WHO["henryk"]["skin"])


def s_pass(p, t, T):
    K.connector(p, t)
    K.figure(p, 260, 760, 1.0, t, "narrator", look=0.8, arms={"l": (-20, 70), "r": (10, 90)})
    K.figure(p, 120, 760, 1.0, t, "henryk", look=0.8)
    for i, (dl, s) in enumerate(((0.0, 0.8), (0.9, 0.75), (1.7, 0.7))):
        k = ease((t - dl) / 2.2)
        if 0 < k < 1:
            R.zombie(p, 1100 - 700 * k, 720 - 20 * i, s, t + i, 120 + i, tilt=0.1 * i)


def s_face_pass(p, t, T):
    p.rect(0, 0, W, H, (130, 146, 132), w=0)
    R.nurse_face(p, 460, 320, 1.0, 0.6, t, gaze=(1.0, 0.0), blink_k=0.0)
    k = t / T
    K.zombie_profile(p, 1300 - 700 * k, 320, 1.1, t, seed=12)


def s_profile_pass(p, t, T):
    p.rect(0, 0, W, H, (130, 146, 132), w=0)
    k = t / T
    K.zombie_profile(p, 1000 - 500 * k, 300, 1.2, t, seed=13)


def s_feet(p, t, T):
    p.rect(0, 0, W, H, (110, 112, 104), w=0)
    for side, x in ((0, 260), (1, 420)):
        p.poly([(x - 80, 560), (x + 90, 560), (x + 100, 610), (x - 80, 610)], (240, 240, 236), w=3)
        K.limb(p, (x, 560), (x - 10, 200), 90, K.TROUSERS, outline=3)
    for i in range(2):
        x = 1300 - 1100 * (((t + i * 0.6) / T) % 1.0)
        lift = 30 * max(0, math.sin(t * 5 + i))
        p.ell(x, 580 - lift, 70, 30, K.ZSKIN)
        K.limb(p, (x + 10, 560 - lift), (x + 30, 160), 70, K.ZSKIN, outline=3)


def s_back(p, t, T):
    K.connector(p, t)
    k = t / T
    h = K.figure(p, 780 - 80 * k, 500 + 200 * k, 0.55 + 0.3 * k, t * 0.6, "narrator", walk=t * 0.6, arms={"r": (40, 60)})
    sack(p, h["r"][0] + 30, h["r"][1] + 20, s=0.35)
    h2 = K.figure(p, 640 - 80 * k, 500 + 200 * k, 0.55 + 0.3 * k, t * 0.6, "henryk", walk=t * 0.6, arms={"l": (-40, 60)})
    p.rect(h2["l"][0] - 30, h2["l"][1], h2["l"][0] + 20, h2["l"][1] + 60, (200, 210, 230), w=2)


def s_count_cans(p, t, T):
    K.pharmacy_inside(p, t)
    K.figure(p, 640, 760, 1.05, t, "zosia", look=0.0, gaze=(0, 1), arms={"l": (60, 150), "r": (-60, 150)})
    p.rect(300, 560, 980, 640, (128, 98, 70))
    for k in range(min(9, 3 + int(t * 3))):
        can(p, 380 + k * 64, 530, r=24)


def s_list(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    K.paper(p, 520, 340, ["jedzenie: tydzień", "woda: 2 tygodnie"], w=480, h=240)
    for k in range(6):
        can(p, 900 + (k % 2) * 90, 520 - (k // 2) * 110, r=44)


def s_look_up(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - T * 0.35) / 0.8)  # kaszel z góry: głowa i wzrok idą w górę
    R.nurse_face(p, 640, 340 - 14 * k, 1.0, 0.3 + 0.3 * k, t, gaze=(0.2, -1.0 * k), body=(640, 340))


FNS = [B.card("DZIEŃ 4"), s_to_phone, s_last_in, s_conn_walk, s_piano, s_pov_soldiers, s_soldier_hand,
       s_kitchen, s_pack_cans, s_tap, s_tap_off, s_fridge_bang, s_fridge_win, s_handle, s_no,
       s_can_falls, s_can_rolls, s_moan, s_run, s_calm, s_press, s_pass, s_face_pass, s_profile_pass, s_feet,
       s_back, s_count_cans, s_list, s_look_up]
LOOK = [None, B.WARD, B.WARD] + [B.DAY] * 4 + [B.DAY] * 8 + [B.DAY] * 11 + [B.BASE] * 3
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
