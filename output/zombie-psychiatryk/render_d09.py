"""Wariant A · dzień 9 „Rachunek” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import random
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 9
NW = K.WHO["nowak"]
RULES = [("DŹWIĘK", 70, 0), ("ODDECH", 70, 6), ("PARAMI", 70, -4), ("NIE OTWIERAJ PO ZMROKU", 44, 10)]
TOWEL = (226, 222, 210)


def talk(t, T, a=0.3, b=0.4):
    return 0.5 + 0.5 * math.sin(t * 9) if a < t < T - b else 0.0


def s_ask(p, t, T):
    K.pharmacy_inside(p, t)
    turn = ease((t - T * 0.7) / 0.4)  # Nowak odwraca wzrok, zanim narrator skończy
    K.figure(p, 480, 760, 1.05, t, "narrator", look=0.5, mouth=talk(t, T * 0.75))
    K.figure(p, 800, 760, 1.05, t, "nowak", look=-0.5 + 0.9 * turn, gaze=(-0.6 + 1.2 * turn, 0.3))


def s_toilet(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(0.7, 0.4), mouth=talk(t, T), fear=0.35)


def s_rule_three(p, t, T):
    K.wall_text(p, RULES, 1.0)
    up = ease((t - 0.2) / 0.5)  # Zosia podnosi rękę do trzeciej zasady
    K.figure(p, 300, 900, 1.0, t, "zosia", look=0.5, mouth=talk(t, T, 0.5), arms={"r": (40 + 120 * up, 95 - 330 * up)})


def s_kuba_angry(p, t, T):
    K.pharmacy_front(p, t)
    lean = 14 * ease((t - 0.2) / 0.4)  # Kuba wychyla się do przodu
    K.face_cu(p, 640, 330 + lean, 1.0 + lean / 400, "kuba", t, gaze=(-0.5, 0.0), mouth=talk(t, T), fear=0.15)


def s_sleeves(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 280, 1.0, "nowak", t, gaze=(0.0, 1.0), fear=0.4)
    k = ease((t - 0.5) / (T * 0.5))
    for side in (-1, 1):  # dłonie znikają w rękawach
        x = 640 + side * 120
        K.limb(p, (x + side * 160, H + 60), (x, 560), 110, NW["top"], outline=4)
        if k < 0.95:
            p.ell(x - side * 10 * k, 540 + 20 * k, 46 * (1 - k * 0.8), 34 * (1 - k * 0.8), NW["skin"])
        p.ell(x, 560, 56, 40, NW["top"], w=4)


def s_tap_word(p, t, T):
    p.rect(0, 0, W, H, (142, 140, 128), w=0)
    p.text(640, 330, "PARAMI", 150, fill=(28, 26, 26))
    taps = [0.6, 1.0, 1.4]
    lift = min(1.0, min(abs(t - h) for h in taps) / 0.15)  # trzy stuknięcia palcem
    x, y = 820, 380 - 40 * lift
    K.limb(p, (x + 380, H + 100), (x + 30, y + 70), 100, K.WHO["henryk"]["top"], outline=4)
    p.ell(x + 30, y + 60, 50, 40, K.WHO["henryk"]["skin"])
    p.line([(x + 10, y + 40), (x - 20, y - 10)], w=18, color=K.WHO["henryk"]["skin"])
    p.line([(x + 10, y + 40), (x - 20, y - 10)], w=2.5)


def s_argue(p, t, T):
    K.pharmacy_inside(p, t)
    for i, (who, x) in enumerate((("zosia", 260), ("narrator", 470), ("kuba", 680), ("nowak", 890), ("irena", 1090))):
        speaking = math.sin(t * (2.2 + i * 0.7) + i) > 0.1  # wszyscy mówią naraz, każdy w swoim rytmie
        g = 30 * math.sin(t * (3 + i)) if speaking else 0
        K.figure(p, x, 760, 0.95, t, who, look=0.4 if i < 2 else -0.4, mouth=0.6 if speaking else 0.0,
                 arms={"r": (40 + g, 40)} if who in ("zosia", "kuba") else None)


FIRST = dict(a=14, b=9, step=0.36, seed=90, jitter=0.15)  # pierwszy z trzech: zrywa nitkę i staje na 9. stopniu


def first_feet(t, t0=None):
    w = FIRST
    moves = K.st_moves(w["a"], w["b"])
    k = K.st_clock(t, len(moves), w["step"], t0=FIRST_T0 if t0 is None else t0, jitter=w["jitter"], seed=w["seed"])
    return K.st_pose(moves, k, w["a"])


def snap_time(t0):
    """Chwila, w której bosa stopa schodząca na 9. stopień zahacza o nitkę."""
    t = t0
    while t < t0 + 5.0:
        if any(z < K.CAN_Z + 0.2 and y < K.CAN_Y + 0.05 for y, z in first_feet(t, t0)[0].values()):
            return t
        t += 0.01
    return t0


TB = 0.12  # huk zaraz po cięciu (rozpiska: „puszki na schodach spadają — huk”, szarpnięcie kamery)
FIRST_T0 = TB - snap_time(0.0)


def s_cans_fall(p, t, T):
    """Detal: bosa stopa zarażonego wchodzi w nitkę, nitka pęka, puszki spadają na stopień i skaczą w dół na kamerę."""
    K.stair_flight(p, t, cam="gora", dark=0.35)
    feet, swing = first_feet(t)
    K.st_person(p, t, feet, swing, -0.1, None, zombie=True, seed=90, tilt=0.1)
    if t < TB:
        K.can_trap(p, t)
        return
    K.can_trap(p, t, broken=True)
    for i, x in enumerate(K.CAN_X):
        r = random.Random(40 + i)
        u = t - TB - 0.035 * i - r.uniform(0, 0.05)
        Y, Z = K.CAN_Y - 0.12, K.CAN_Z
        if u > 0:
            if u < 0.14:  # spada na stopień
                Y -= (K.CAN_Y - 0.12 - (K.CAN_TREAD * K.ST_R + 0.05)) * (u / 0.14) ** 2
            else:  # i skacze po stopniach w dół, każde odbicie niższe
                u -= 0.14
                hop = 0.19 + 0.04 * r.random()
                n = int(u / hop)
                h = u / hop - n
                L = K.CAN_TREAD - n
                Y = (L - h) * K.ST_R + 0.05 + 0.12 * 0.75 ** n * math.sin(math.pi * h)
                Z = (L - 0.5 - h) * K.ST_D
            x += 0.08 * r.uniform(-1, 1) * min(1.0, u * 3)
        K.st_can(p, x, Y, Z, rot=max(0.0, u) * r.uniform(-14, 14))


def battery_lamp(p, x, y, on):
    p.rect(x - 18, y - 40, x + 18, y + 6, (90, 92, 96), w=3)
    p.rect(x - 13, y - 34, x + 13, y - 16, (250, 236, 170) if on else (80, 80, 76), w=2)
    if on:
        p.glow([(x - 50, y - 50), (x + 50, y - 50), (x + 260, 720), (x - 260, 720)], (255, 240, 170, 50))


def s_lamp_off(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    on = t < T * 0.45  # Zosia gasi lampę akumulatorową
    K.figure(p, 160, 600, 0.8, t, "zosia", look=0.6, gaze=(0.6, 1.0), arms={"r": (70, 40)})
    p.rect(-20, 430, 270, 600, (60, 46, 34))
    battery_lamp(p, 230, 430, on)


def lying(p, x, y, s, t, who, lift=0.0):
    c = K.WHO[who]
    p.poly([(x - 120 * s, y - 30 * s), (x + 60 * s, y - 34 * s), (x + 60 * s, y), (x - 120 * s, y)], c["top"])
    p.ell(x + 100 * s, y - 30 * s - 20 * lift * s, 40 * s, 34 * s, c["skin"])


def s_lie_down(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    for i, (who, x) in enumerate((("zosia", 250), ("narrator", 470), ("irena", 690), ("kuba", 900), ("nowak", 1100))):
        lift = ease((t - T * 0.5) / 0.3) * (1 - ease((t - T * 0.75) / 0.3)) if who == "kuba" else 0.0  # Kuba unosi głowę
        lying(p, x, 650, 1.0, t, who, lift)
    p.rect(-20, 560, W + 20, 610, (60, 52, 44))  # dolna półka regału zasłania leżących


FALLEN = ((-0.55, 3, 1.57), (0.1, 2, 1.2), (0.62, 0, 1.57), (-0.15, 5, 0.3), (0.45, 1, 1.9))  # puszki po upadku


def s_three_down(p, t, T):
    """Zeszło trzech, każdy innym krokiem: pierwszy równo i szybko, drugi krokiem dostawnym z zatrzymaniami,
    trzeci nierówno, zrywami. Na stopniach leżą puszki, przy ścianach zwisają końce nitki."""
    K.stair_flight(p, t, dark=0.6)
    K.can_trap(p, t, broken=True)
    for x, L, rot in FALLEN:
        y, z = K.st_level(L)
        K.st_can(p, x, y + 0.035, z, rot=rot)
    K.st_group(p, t, [dict(a=9, b=1, step=0.38, t0=0.3, x=-0.1, zombie=True, seed=90, jitter=0.15, tilt=0.1),  # ten od nitki
                      dict(a=13, b=4, step=0.3, hold=0.25, t0=0.35, kind="dost", lead="r", x=0.5, zombie=True,
                           seed=91, jitter=0.5, tilt=-0.15),
                      dict(a=14, b=5, step=0.26, t0=0.9, x=-0.55, zombie=True, seed=92, jitter=0.7, tilt=0.25)])


def s_teeth(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    chatter = 4 * math.sin(t * 60)
    K.face_cu(p, 640, 330 + chatter * 0.3, 1.0, "irena", t, gaze=(0.3, -0.5), fear=0.7)
    K.limb(p, (-80, 700), (560, 430), 110, K.narr_sleeve(), outline=4)  # dłoń narratora na jej ustach
    p.ell(640, 420 + chatter, 96, 52, K.SKIN)


def s_towel_grille(p, t, T):
    p.rect(0, 0, W, H, (20, 22, 24), w=0)
    for x in range(120, W, 180):
        p.rect(x - 14, -20, x + 14, H + 20, (50, 52, 54))
        for y in range(40, H, 70):
            p.poly([(x - 30, y), (x + 30, y + 14), (x + 30, y + 46), (x - 30, y + 32)], TOWEL, w=2)
    k = ease(t / (T * 0.8))  # palce zarażonego suną po ręczniku
    fx = 200 + 600 * k
    p.ell(fx, 360, 70, 44, K.ZSKIN)
    for i in range(4):
        p.ell(fx + 50 + i * 4, 330 + i * 22, 28, 10, K.ZSKIN, w=2)


def s_hold_breath(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    R.nurse_face(p, 640, 320, 1.0, 0.6, t, gaze=(0.9 - 1.6 * ease(t / T), -0.2), blink_k=0.0, breath=1.4)


def s_away(p, t, T):
    K.cellar(p, t, flick=0.6)
    k = t / T
    for i, (dl, s0) in enumerate(((0.0, 0.8), (0.35, 0.75), (0.7, 0.85))):
        f = max(0.0, k - dl * 0.4)
        K.zombie_back(p, 600 + 40 * i, 700 - 220 * f, s0 * (1 - 0.5 * f), t + i, 93 + i, walk=t * 0.5)


def s_canister(p, t, T):
    p.rect(0, 0, W, H, (96, 94, 86), w=0)
    k = ease(t / T)  # kałuża rośnie
    p.ell(560, 560, 200 + 260 * k, 60 + 70 * k, (70, 90, 110), w=0)
    p.ell(560, 560, 200 + 260 * k, 60 + 70 * k, None, w=2, color=(140, 170, 190))
    p.poly([(380, 420), (740, 400), (760, 520), (400, 540)], (200, 210, 230), w=4)  # kanister na boku
    p.rect(740, 430, 790, 480, (60, 110, 160), w=3)
    if int(t * 6) % 2 == 0:
        p.ell(790, 500 + 30 * ((t * 3) % 1), 6, 8, (140, 170, 190), w=0)  # kapie z szyjki


def s_paper(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.6, 0.2), mouth=talk(t, T, 0.8))
    up = ease((t - 0.1) / 0.5)
    K.paper(p, 980, 720 - 260 * up, ["woda:", "1,5 dnia"], w=300, h=220, rot=-0.1)


def s_kuba_scared(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - 0.3) / 0.8)
    K.face_cu(p, 640, 330, 1.0, "kuba", t, gaze=(0.0, 0.5 + 0.3 * k), fear=0.2 + 0.6 * k)


def s_hug(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 760, 360, 0.9, "kuba", t, gaze=(-0.4, 0.6), fear=0.6)
    K.face_cu(p, 330, 340, 0.85, "irena", t, gaze=(0.9, 0.2), mouth=talk(t, T, 0.6, 0.4))
    k = ease((t - 0.2) / 0.6)  # ręka Ireny obejmuje Kubę
    K.limb(p, (420, 700), (560 + 300 * k, 560 - 20 * k), 70, K.WHO["irena"]["sleeve"], outline=4)
    p.ell(580 + 300 * k, 556 - 20 * k, 40, 30, K.WHO["irena"]["skin"])


def s_banging(p, t, T):
    hit = (t % 1.15) < 0.12  # miarowe uderzanie zza drzwi rozdzielni
    K.cellar(p, t, flick=0.5, door_open=0.02 if hit else 0.0)
    if hit:
        for k in range(3):
            p.line([(560 - k * 20, 300 + k * 30), (520 - k * 20, 290 + k * 30)], w=3, color=(200, 200, 190))


def s_no_power(p, t, T):
    p.rect(0, 0, W, H, (40, 42, 44), w=0)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(-0.4, 0.3), mouth=talk(t, T), fear=0.5)


def s_two_blinks(p, t, T):
    p.rect(0, 0, W, H, (40, 42, 44), w=0)
    bk = 0.0
    for h in (T * 0.45, T * 0.62):  # dwa szybkie mrugnięcia — ostrzeżenie
        d = t - h
        if 0 <= d < 0.18:
            bk = max(bk, 1 - abs(d - 0.09) / 0.09)
    K.face_cu(p, 640, 470, 2.4, "henryk", t, gaze=(-0.5, 0.0), blink_k=bk)


def s_nobody_sleeps(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    flinch = 6 if (t % 1.15) < 0.12 else 0  # każde uderzenie z rozdzielni słychać aż tutaj
    for who, x in (("zosia", 200), ("narrator", 390), ("henryk", 570), ("nowak", 750), ("irena", 930), ("kuba", 1100)):
        K.sitting(p, x, 690 - (flinch if who in ("kuba", "irena") else 0), 0.62, t, who, eyes=1.0)


FNS = [B.card("DZIEŃ 9"), s_ask, s_toilet, s_rule_three, s_kuba_angry, s_sleeves, s_tap_word, s_argue,
       s_cans_fall, s_lamp_off, s_lie_down, s_three_down, s_teeth, s_towel_grille, s_hold_breath, s_away,
       s_canister, s_paper, s_kuba_scared, s_hug, s_banging, s_no_power, s_two_blinks, s_nobody_sleeps]
LOOK = [None] + [B.BASE] * 7 + [B.BASE, B.BASE] + [B.DARK] * 6 + [B.BASE] * 4 + [B.NIGHT] * 4
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
