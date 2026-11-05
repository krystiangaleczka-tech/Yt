"""Wariant A · dzień 8 „Oddział A” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 8
GOWN = (150, 170, 190)  # salowy w niebieskim fartuchu
WALL_A = (150, 160, 140)


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def glass(p, x0=0, y0=0, x1=W, y1=H):
    """Odbicia na szybie przed twarzą (rysowane na końcu)."""
    for k in range(3):
        p.line([(x0 + 120 + k * 60, y0 + 40), (x0 + 40 + k * 60, y0 + 200)], w=3, color=(220, 230, 230), amp=0.4)


def s_connector(p, t, T):
    K.connector(p, t)
    k = t / T
    for who, dx, ph in (("zosia", -90, 0.0), ("narrator", 30, 0.3), ("henryk", 150, 0.1)):
        s = 0.5 + 0.35 * k
        K.figure(p, 760 + dx * s - 120 * k, 470 + 230 * k, s, t * 0.6 + ph, who, walk=t * 0.6 + ph)


def s_chain_door(p, t, T):
    tug = 6 * math.sin(t * 40) if T * 0.55 < t < T * 0.55 + 0.35 else 0  # ktoś od środka szarpie łańcuch
    K.ward_a_door(p, t, chain=1.0 + tug / 20, inner=lambda q: K.barricade_behind(q, t))


def s_pov_barricade(p, t, T):
    def inner(q):
        q.rect(0, 0, W, H, (150, 156, 136), w=0)
        q.rect(-20, 420, W + 20, H + 20, (110, 116, 100))
        for k, x in enumerate((380, 520, 700, 860)):
            q.poly([(x - 80, 360 - (k % 2) * 30), (x + 70, 350 - (k % 2) * 30), (x + 80, 380 - (k % 2) * 30), (x - 70, 390 - (k % 2) * 30)],
                   (150, 120, 90))
        K.figure(q, 520, 560, 0.62, t, "irena", look=0.2, arms={"l": (20, 40), "r": (-20, 40)})
        up = ease((t - T * 0.4) / 0.4)  # Kuba podnosi nogę od krzesła
        h = K.figure(q, 760, 560, 0.62, t, "kuba", look=-0.3, arms={"r": (40, 95 - 150 * up)})
        K.chair_leg(q, h["r"], up=0.5 + 0.5 * up)
        for x in (360, 600, 820):
            q.rect(x - 110, 420, x + 110, 520, (150, 120, 90))
    K.ward_a_door(p, t, chain=1.0, inner=inner)


def face_through_glass(p, t, who, **kw):
    p.rect(0, 0, W, H, (150, 156, 136), w=0)
    K.face_cu(p, 640, 340, 1.0, who, t, **kw)
    glass(p)


def s_kuba_no(p, t, T):
    p.rect(0, 0, W, H, (150, 156, 136), w=0)
    shake = 22 * math.sin(t * 7) * (1 - ease((t - T * 0.8) / 0.3))  # kręci głową
    K.face_cu(p, 640 + shake, 340, 1.0, "kuba", t, gaze=(-0.2, 0.0), mouth=talk(t, T), fear=0.3)
    glass(p)


def s_narrator_glass(p, t, T):
    p.rect(0, 0, W, H, WALL_A, w=0)
    R.nurse_face(p, 640, 320, 1.0, 0.4 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.0, 0.0))
    p.rect(0, 0, 160, H, (124, 138, 122), w=0, amp=0)  # framuga szyby
    p.line([(160, 0), (160, H)], w=6)


def s_henryk_blink(p, t, T):
    p.rect(0, 0, W, H, WALL_A, w=0)
    a = T * 0.35
    bk = math.sin(min(1.0, max(0.0, (t - a) / 1.4)) * math.pi)  # jedno mrugnięcie, bardzo powolne (znak, nie odruch)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(0.0, 0.0), blink_k=bk)
    glass(p)


def s_irena_hand(p, t, T):
    p.rect(0, 0, W, H, (150, 156, 136), w=0)
    K.face_cu(p, 470, 340, 0.9, "irena", t, gaze=(0.8, 0.2), mouth=talk(t, T, 0.6, 0.4))
    K.face_cu(p, 1060, 380, 0.9, "kuba", t, gaze=(-0.8, 0.0))
    k = ease((t - 0.2) / 0.5)  # dłoń Ireny ląduje na ramieniu Kuby
    hx, hy = 760 + 120 * k, 640 - 20 * k
    K.limb(p, (560, H + 60), (hx - 30, hy + 10), 70, K.WHO["irena"]["sleeve"], outline=4)
    p.ell(hx, hy, 44, 30, K.WHO["irena"]["skin"])
    glass(p)


def s_chain_falls(p, t, T):
    p.rect(0, 0, W, H, (124, 138, 122), w=0)
    p.rect(-20, 520, W + 20, H + 20, (92, 104, 92))
    p.line([(-20, 520), (W + 20, 520)], w=4)
    for k in range(10):  # ogniwa spadają po kolei i odbijają się od podłogi
        f = max(0.0, t - k * 0.04)
        y = min(500.0, 160 + 900 * f * f)
        bounce = 18 * abs(math.sin(f * 14)) * math.exp(-f * 5) if y >= 500 else 0
        p.ell(520 + k * 26 + 30 * f, y - bounce, 14, 8, None, w=5, color=(90, 92, 96), rot=k * 0.7)


def s_orderly(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1], doors_open=0.0)
    vx, vy = 640, 330
    p.rect(vx - 30, vy - 40, vx + 30, vy + 80, (20, 22, 22))  # otwarte drzwi toalety na końcu
    k = ease((t - 0.4) / (T * 0.8))
    s = 0.33 + 0.25 * k
    R.zombie(p, vx + 10 * k, vy + 80 + 120 * k, s, t, 80, gown=GOWN, tilt=0.15)
    if k < 0.05:  # dopóki stoi w progu, framuga zasłania jego boki
        p.rect(vx - 60, vy - 40, vx - 30, vy + 80, (130, 144, 122), w=0, amp=0)
        p.rect(vx + 30, vy - 40, vx + 60, vy + 80, (130, 144, 122), w=0, amp=0)


def s_kuba_leg(p, t, T):
    p.rect(0, 0, W, H, (150, 160, 140), w=0)
    K.face_cu(p, 640, 360, 1.0, "kuba", t, gaze=(0.6, 0.0), fear=0.6)
    up = ease(t / 0.5)  # noga od krzesła wędruje w górę przed twarz
    x, y = 860, 760 - 260 * up
    p.poly([(x - 18, y + 40), (x + 18, y + 40), (x + 30, y - 260), (x - 4, y - 266)], (150, 110, 70), w=4)
    p.ell(x, y + 30, 50, 36, K.WHO["kuba"]["skin"])


def breath_puffs(p, x, y, t, rate=1.2):
    ph = (t * rate) % 1.0
    if ph < 0.5:
        for k in range(3):
            r = 10 + k * 14 + 30 * ph
            p.ell(x + 30 + k * 20 + 40 * ph, y - 10 - k * 6, r, r * 0.6, None, w=2, color=(230, 236, 236))


def s_henryk_between(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    R.zombie(p, 800, 540, 0.62, t, 80, gown=GOWN, tilt=0.15 + 0.15 * ease((t - T * 0.4) / 0.5))  # salowy przekrzywia głowę
    step = ease(t / 0.6)
    K.figure_back(p, 560 + 60 * step, 760, 1.05, t, "henryk", walk=t * 0.5 if step < 1 else None)
    breath_puffs(p, 620, 760 - 336 * 1.05, t)  # głośny, celowy oddech


def s_lead_away(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1], doors_open={(2, 1): 0.9})
    k = t / T  # Henryk prowadzi oddechem w głąb, salowy idzie za nim
    K.figure_back(p, 640 + 40 * k, 640 - 150 * k, 0.7 - 0.3 * k, t, "henryk", walk=t * 0.4)
    K.zombie_back(p, 600 + 30 * k, 720 - 130 * k, 0.9 - 0.35 * k, t, 81, gown=GOWN, walk=t * 0.4)


def s_retreat(p, t, T):
    K.connector(p, t)
    k = t / T  # Zosia, Irena i Kuba cofają się do łącznika, oglądając się za siebie
    for who, dx, lag in (("zosia", -150, 0.0), ("irena", 0, 0.15), ("kuba", 150, 0.05)):
        f = max(0.0, k - lag)
        s = 0.55 + 0.35 * f
        K.figure(p, 760 + dx * s - 100 * f, 480 + 220 * f, s, t * 0.5, who, walk=t * 0.5, look=0.7, gaze=(1.0, 0.0))


def s_back_for_him(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    k = t / T
    K.figure_back(p, 640, 800 - 200 * k, 1.1 - 0.4 * k, t * 0.7, "narrator", walk=t * 0.7)


def s_hold_door(p, t, T):
    K.bathroom(p, t)
    hits = [0.3, 0.9, 1.3]
    j = 10 if any(0 <= t - h < 0.12 for h in hits) else 0  # uderzenia od środka kabiny
    p.rect(700 + j, 140, 960 + j, 600, (150, 170, 176))
    p.rect(900 + j, 360, 916 + j, 400, (110, 110, 110), w=2)
    K.figure(p, 830 + j * 0.6, 760, 1.05, t, "henryk", look=-0.3, lean=-0.2, arms={"l": (-30, 80), "r": (30, 80)})
    if j:
        for k in range(4):
            a = k * 1.4
            p.line([(830 + 180 * math.cos(a), 300 + 140 * math.sin(a)), (830 + 220 * math.cos(a), 300 + 170 * math.sin(a))], w=4)


def s_mop(p, t, T):
    p.rect(0, 0, W, H, (150, 170, 176), w=0)
    p.rect(560, 300, 720, 340, (110, 110, 110), w=3)  # klamka
    k = ease((t - 0.2) / 0.7)  # trzonek mopa wsuwa się pod klamkę
    x = -200 + 900 * k
    p.poly([(x - 700, 352), (x, 330), (x, 346), (x - 700, 372)], (190, 160, 110), w=3)
    K.limb(p, (x - 620, H + 60), (x - 520, 380), 90, K.narr_sleeve(), outline=4)
    p.ell(x - 510, 370, 50, 36, K.SKIN)


def s_calm(p, t, T):
    K.bathroom(p, t)
    br = math.sin(t * 2 * math.pi / 4.0)  # wolny oddech pana Henryka
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.3, 0.1), breath=br * 2)
    if br < -0.6:
        for k in range(3):
            p.ell(780 + k * 30, 470 - k * 10, 14 + k * 10, 8 + k * 6, None, w=2, color=(230, 236, 236))


def s_six(p, t, T):
    K.pharmacy_inside(p, t, dark=0.45)
    cough = 6 * math.sin(t * 30) if T * 0.5 < t < T * 0.5 + 0.5 else 0  # Irena kaszle
    for who, x, y in (("zosia", 200, 690), ("narrator", 390, 700), ("henryk", 570, 690), ("nowak", 750, 700),
                      ("irena", 930 + cough, 690), ("kuba", 1100, 700)):
        K.sitting(p, x, y, 0.62, t, who, gaze=(-0.6, 0.0) if who == "henryk" else None)


def s_irena_nowak(p, t, T):
    K.pharmacy_inside(p, t, dark=0.45)
    k = ease((t - 0.2) / 0.6)  # Irena bierze go za rękę
    K.figure(p, 520, 760, 1.0, t, "irena", look=0.5, mouth=talk(t, T, 0.6, 0.4), arms={"r": (40 + 90 * k, 95 + 10 * k)})
    K.figure(p, 790, 760, 1.0, t, "nowak", look=-0.4, arms={"l": (-30 - 40 * k, 100)})


def s_pull_away(p, t, T):
    p.rect(0, 0, W, H, (80, 84, 80), w=0)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(-0.6, 0.3), fear=0.5)
    k = ease((t - 0.3) / 0.25)  # wyrywa rękę z dłoni Ireny
    K.limb(p, (900, H + 60), (760 - 300 * (1 - k), 640 + 60 * k), 90, K.WHO["nowak"]["sleeve"], outline=4)
    if k < 0.6:
        p.ell(520, 640, 52, 36, K.WHO["irena"]["skin"])


def s_kuba_wakes(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    eyes = ease((t - 0.6) / 0.4)
    R.nurse_face(p, 900, 380, 0.85, 0.2 + 0.4 * eyes, t, gaze=(-0.8, 0.0), blink_k=1 - eyes)
    K.face_cu(p, 380, 360, 0.85, "kuba", t, gaze=(1.0, 0.1), mouth=talk(t, T, 0.8, 0.3) * 0.6, fear=0.4)


def s_grille_dark(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    R.nurse_face(p, 760, 330, 1.0, 0.4, t, gaze=(-1.0, 0.0))
    K.grille(p, -40, -20, 380, H + 20, gap=70, bar=12, col=(40, 44, 46))  # zamknięta krata, przed nim


FNS = [B.card("DZIEŃ 8"), s_connector, s_chain_door, s_pov_barricade, s_kuba_no, s_narrator_glass, s_henryk_blink,
       s_irena_hand, s_chain_falls, s_orderly, s_kuba_leg, s_henryk_between, s_lead_away, s_retreat, s_back_for_him,
       s_hold_door, s_mop, s_calm, s_six, s_irena_nowak, s_pull_away, s_kuba_wakes, s_grille_dark]
LOOK = [None] + [B.DAY] * 17 + [B.BASE] * 3 + [B.NIGHT] * 2
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
