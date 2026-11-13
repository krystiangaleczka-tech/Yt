"""Wariant A · dzień 3 „Zasady” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease, noise

DAY = 3
RULES = [("DŹWIĘK", 70, 0), ("ODDECH", 70, 6), ("PARAMI", 70, -4), ("NIE OTWIERAJ PO ZMROKU", 44, 10)]


def marker_hand(p, x, y, sleeve, skin, t):
    """Dłoń z markerem przy końcu pisanego słowa (bliżej kamery niż ściana)."""
    jx, jy = x + 6 * math.sin(t * 20), y + 4 * math.cos(t * 17)
    K.limb(p, (jx + 260, H + 80), (jx + 40, jy + 50), 90, sleeve, outline=4)
    p.ell(jx + 30, jy + 40, 46, 36, skin)
    p.line([(jx, jy), (jx + 34, jy + 30)], w=12, color=(30, 30, 30))


def writing(n, sleeve, skin):
    def fn(p, t, T):
        k = ease(t / (T * 0.85))
        x, y = K.wall_text(p, RULES[:n], k)
        marker_hand(p, x, y + 10, sleeve, skin, t)
    return fn


def s_rules_wide(p, t, T):
    K.wall_text(p, RULES, 1.0)
    k = ease((t - T * 0.35) / 0.7)  # Zosia podchodzi krok i pokazuje pierwszą zasadę
    K.figure(p, 360 + 40 * k, 900, 1.0, t * 0.5, "zosia", walk=t * 0.5 if 0.05 < k < 0.95 else None, look=0.2,
             arms={"r": (40 + 60 * k, 95 - 280 * k)})
    K.figure(p, 640, 900, 1.0, t, "narrator", look=0.2)
    K.figure(p, 920, 900, 1.0, t, "henryk", look=-0.2)
    for i in range(3):  # trzy kreski Henryka z boku ściany (zasiew: dzień 6)
        p.line([(1120 + i * 26, 470), (1124 + i * 26, 560)], w=6)


def s_ask(p, t, T):
    K.pharmacy_front(p, t)
    talk = 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.9, 0.0), mouth=talk, fear=0.3)


def s_away(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-1.0, 0.4 * ease(t / T)))


def s_supplies(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    K.paper(p, 600, 340, ["woda: 1 dzień", "jedzenie: 3 dni"], w=480, h=240)
    k = ease((t - 0.4) / (T * 0.6))  # ołówek podkreśla wodę
    p.line([(420, 300), (420 + 300 * k, 304)], w=4, color=(170, 40, 40))
    K.limb(p, (420 + 300 * k + 300, H + 80), (430 + 300 * k, 330), 80, (52, 62, 92), outline=4)
    p.ell(420 + 300 * k + 20, 320, 40, 30, K.WHO["zosia"]["skin"])
    for x in (1000, 1090):
        p.rect(x - 34, 200, x + 34, 440, (190, 214, 226), w=3)
        p.rect(x - 20, 170, x + 20, 200, (60, 110, 160), w=3)


def s_plan(p, t, T):
    K.pharmacy_inside(p, t)
    k = ease(t / (T * 0.7))  # palec Zosi jedzie po planie do kuchni
    K.figure(p, 470, 760, 1.0, t, "zosia", look=0.3, gaze=(0.3, 1.0), arms={"r": (60 + 120 * k, 150)}, mouth=0.4 if 0.5 < t < T - 0.6 else 0)
    K.figure(p, 800, 760, 1.0, t, "narrator", look=-0.3, gaze=(-0.3, 1.0), lean=-0.4)
    p.rect(200, 560, 1080, 640, (128, 98, 70))  # lada przed nimi
    p.poly([(420, 548), (840, 548), (870, 590), (390, 590)], (236, 232, 214), w=3)  # plan na ladzie
    fx = 580 + 120 * k  # tam, gdzie jest dłoń Zosi (bark 520 + ręka)
    p.line([(460, 566), (fx, 572)], w=2, color=(40, 40, 90))
    p.ell(fx, 568, 12, 9, K.WHO["zosia"]["skin"])  # opuszek palca na planie


def s_answer(p, t, T):
    K.pharmacy_front(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.2, t, gaze=(-0.7, 0.0), blink_k=R.blink(t, 91, 1.8))


def s_decide(p, t, T):
    K.pharmacy_front(p, t)
    talk = 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.6, 0.0), mouth=talk, fear=0.1)


def s_breathe_h(p, t, T):
    K.pharmacy_front(p, t)
    br = B.breathing(t, 1 / 12)  # wdech 4 s, trzymanie, wydech
    K.face_cu(p, 640, 320, 1.0, "henryk", t, gaze=(0, 0), blink_k=0.5, breath=br * 2)
    p.ell(560, 560 - 10 * br, 56, 40, K.WHO["henryk"]["skin"])  # dłoń na piersi
    K.limb(p, (400, H + 60), (530, 580 - 10 * br), 60, K.WHO["henryk"]["top"], outline=4)


def s_inhale(p, t, T):
    K.pharmacy_front(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.25, t, gaze=(0, -0.2), breath=1.2 * ease(t / 0.8))
    with K.on_face(p, "narrator"):  # nadęte policzki idą za głową (rig)
        for side in (-1, 1):
            p.ell(640 + side * 76, 390, 22, 16, (238, 186, 168), w=0)


def s_exhale(p, t, T):
    K.pharmacy_front(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.15, t, gaze=(0, 0.3), blink_k=0.4, breath=1.2 * (1 - ease(t / T)))


def s_hand(p, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    shake = 8 * (1 - ease((t - 0.6) / 0.9))
    hx, hy = 640 + shake * noise(t, 93, 14), 380 + shake * noise(t, 94, 13)
    K.limb(p, (hx + 300, H + 60), (hx + 60, hy + 40), 110, K.narr_sleeve(), outline=4)
    p.ell(hx, hy, 120, 80, K.SKIN)
    for i in range(4):  # palce jako pełne kształty, wyrastają z dłoni
        K.limb(p, (hx - 80 + i * 52, hy - 40), (hx - 96 + i * 52, hy - 150 + abs(i - 1.5) * 18), 40, K.SKIN, outline=3)
    p.ell(hx, hy, 120, 80, K.SKIN)
    K.limb(p, (hx + 100, hy + 10), (hx + 170, hy - 60), 40, K.SKIN, outline=3)  # kciuk


def s_towels(p, t, T):
    p.rect(0, 0, W, H, (140, 136, 112), w=0)
    K.grille(p, 120, -40, 1160, H + 40, gap=200, bar=30)
    for k, x in enumerate((120, 320, 520, 720, 920)):
        for j, y in enumerate((180, 420)):
            col = ((200, 80, 80), (230, 226, 210), (80, 120, 170))[(k + j) % 3]
            p.rect(x - 34, y, x + 34, y + 120, col, w=3)
            for s in range(3):
                p.line([(x - 34, y + 30 + s * 30), (x + 34, y + 30 + s * 30)], w=2, color=(60, 60, 60))


def s_dark_three(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    up = [ease((t - T * d) / 0.4) for d in (0.35, 0.5, 0.42)]  # na drapanie podnoszą głowy, każde w swoim czasie
    K.sitting(p, 360, 680, 0.75, t, "zosia", gaze=(0.2, -0.9 * up[0]))
    K.sitting(p, 640, 690, 0.78, t, "narrator", gaze=(0.0, -0.9 * up[1]))
    K.sitting(p, 900, 680, 0.75, t, "henryk", gaze=(0.0, -0.3 - 0.6 * up[2]))


def s_door_shadow(p, t, T):
    K.stair_door(p, t, shadow=0.6 * math.sin(t * 2.2))


def s_henryk_dark(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0, -0.3), breath=0.2 * B.breathing(t, 0.08))


def s_eyes_wide(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    R.nurse_face(p, 640, 320, 1.0, 0.85, t, gaze=(0.5 * math.sin(t * 5), -0.6), blink_k=0.0)


def s_whisper(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    talk = 0.3 + 0.3 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.3, -0.4), mouth=talk, fear=0.5)


def s_shadow_leaves(p, t, T):
    K.stair_door(p, t, shadow=0.2 + 1.2 * ease(t / T))


def s_noblink(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    R.nurse_face(p, 640, 320, 1.0, 0.5, t, gaze=(0.0, -0.3), blink_k=0.0)
    k = (t - T * 0.45) / (T * 0.5)  # łza od niemrugania spływa po policzku
    if k > 0:
        y = 340 + 140 * min(1.0, k)
        with K.on_face(p, "narrator"):
            p.poly([(590, y - 14), (597, y), (590, y + 8), (583, y)], (190, 220, 235), w=2)


def s_ring_above(p, t, T):
    K.stair_door(p, t, glow=0.6, cam="dol")
    if t > 1.0 and int(t * 3) % 2 == 0:
        for side in (-1, 1):
            for k in range(3):
                x0 = 640 + side * (170 + k * 26)
                p.line([(x0, 70 + k * 10), (x0 + side * 18, 50 + k * 6)], w=3, color=(200, 210, 190))


FNS = [B.card("DZIEŃ 3"), writing(1, (52, 62, 92), K.WHO["zosia"]["skin"]), writing(2, (52, 62, 92), K.WHO["zosia"]["skin"]),
       writing(3, K.JACKET, K.SKIN), writing(4, K.WHO["henryk"]["top"], K.WHO["henryk"]["skin"]), s_rules_wide, s_ask, s_away,
       s_supplies, s_plan, s_answer, s_decide, s_breathe_h, s_inhale, s_exhale, s_hand, s_towels,
       s_dark_three, s_door_shadow, s_henryk_dark, s_eyes_wide, s_whisper, s_shadow_leaves, s_noblink, s_ring_above]
LOOK = [None] + [B.BASE] * 16 + [B.NIGHT] * 8
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
