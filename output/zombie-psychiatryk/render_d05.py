"""Wariant A · dzień 5 „Dr Nowak” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease, noise

DAY = 5
NW = K.WHO["nowak"]


def talk(t, T):
    return 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < T - 0.4 else 0.0



def nowak_with_keys(q, t):
    K.figure(q, 560, 640, 1.05, t, "nowak", look=0.1, arms={"l": (-10, 60)})
    bx, by = 560 + 40, 640 - 118  # pęk kluczy dyżurnego przy pasku (zasiew: dni 10 i 12)
    q.ell(bx, by, 10, 10, None, w=2.5, color=(150, 150, 140))
    for i, (dx, dy) in enumerate(((-6, 22), (2, 26), (9, 20))):
        q.line([(bx, by + 6), (bx + dx, by + dy)], w=3, color=(170, 170, 160))
    q.rect(bx + 6, by + 18, bx + 14, by + 26, (220, 190, 40), w=1.5)  # żółta przywieszka


def s_portion(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(0.3, 0.8), mouth=talk(t, T), fear=0.3)
    k = ease((t - 0.2) / 0.7)  # odsuwa miskę z połową porcji
    p.ell(560 + 160 * k, 640, 110, 34, (220, 220, 214), w=4)
    p.ell(560 + 160 * k, 632, 80, 18, (170, 130, 90))
    K.limb(p, (300, H + 60), (500 + 160 * k, 650), 70, NW["top"], outline=4)


def s_frown(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - 0.2) / 0.5)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.6, 0.0), mouth=talk(t, T) * 0.8, fear=0.15 + 0.2 * k)

def s_stairs(p, t, T):
    """Wchodzi przy poręczy w górę, plecami do nas; latarkę przed sobą zasłania dłonią — na stopniach przed nim
    tylko czerwonawa poświata spod palców."""
    K.stair_flight(p, t, dark=0.5)
    x, a = -0.72, 1
    moves = K.st_moves(a, 9)
    feet, swing = K.st_pose(moves, K.st_clock(t, len(moves), 0.5, t0=0.25), a)
    yc, zc = min(y for y, _ in feet.values()), sum(z for _, z in feet.values()) / 2
    P = K.st_proj
    p.glow([P(x - 0.3, yc + 0.1, zc + 0.3), P(x + 0.5, yc + 0.1, zc + 0.3), P(x + 0.9, yc + 0.7, zc + 2.4),
            P(x - 0.4, yc + 0.7, zc + 2.4)], (255, 130, 96, 44))
    K.st_person(p, t, feet, swing, x, "narrator", back=True, rail=True, arms={"r": (6, 64)})

def s_barricade(p, t, T):
    j = 4 * math.sin(t * 60) if T * 0.55 < t < T * 0.55 + 0.3 else 0  # ktoś w środku przesuwa szafkę
    K.treatment_door(p, t, op=0.0)
    if j:
        p.line([(470, 560), (520, 560)], w=3)
        p.rect(462 + j, 380, 470 + j, 620, (30, 34, 34), w=0)


def s_gap(p, t, T):
    p.rect(0, 0, W, H, (124, 138, 122), w=0)
    p.rect(560, -20, 700, H + 20, (16, 18, 18))
    k = ease((t - 0.5) / 0.4)  # oko pojawia się w szparze dopiero po chwili
    blink = R.blink(t, 101, 1.4)
    if k > 0.05 and blink < 0.5:
        x = 690 - 60 * k
        p.ell(x, 330, 26, 16, (230, 230, 220), w=2)
        p.ell(x + 2, 330, 7, 7, R.INK, w=0)
        p.ell(x, 330, 34, 22, None, w=2.5)  # oprawka okularów


def s_whisper_door(p, t, T):
    p.rect(0, 0, W, H, (112, 126, 112), w=0)
    p.rect(980, -20, W + 20, H + 20, (124, 138, 122))
    R.nurse_face(p, 600, 330, 1.0, 0.35 if 0.3 < t < T - 0.3 else 0.2, t, gaze=(1.0, 0.0))


def s_open(p, t, T):
    op = ease(t / (T * 0.7))
    K.treatment_door(p, t, op=op, who=lambda q: nowak_with_keys(q, t))


def s_collar(p, t, T):
    p.rect(0, 0, W, H, (112, 126, 112), w=0)
    K.face_cu(p, 640, 20, 1.3, "nowak", t, gaze=(0.2, 0.0), fear=0.4)


def s_question(p, t, T):
    K.pharmacy_inside(p, t)
    K.figure(p, 420, 760, 1.05, t, "zosia", look=0.6, mouth=talk(t, T))
    K.figure(p, 860, 760, 1.05, t, "nowak", look=-0.5, arms={"l": (20, 100), "r": (-20, 100)})


def s_no(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(-0.5, 0.0), mouth=talk(t, T * 0.6), fear=0.3)


def s_slide(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(ease(t / T) * 1.0, 0.2), fear=0.4)


def s_stare(p, t, T):
    K.pharmacy_front(p, t)
    k = ease(t / T)  # Henryk powoli przesuwa wzrok za Nowakiem, nie mruga
    K.face_cu(p, 640 - 8 * k, 330, 1.0, "henryk", t, gaze=(-0.4 - 0.5 * k, 0.1 * k))


def plan_paper(p, n=4):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    p.poly([(200, 120), (1080, 100), (1100, 620), (180, 640)], (236, 232, 214), w=4)
    for (x0, y0, x1, y1, txt) in ((260, 180, 520, 320, "APTEKA"), (560, 160, 820, 300, "AGREGAT"),
                                  (300, 380, 600, 560, "ROZDZIELNIA"), (680, 380, 1000, 560, "ODDZIAŁ C"))[:n]:
        p.rect(x0, y0, x1, y1, None, w=3, color=(40, 40, 90))
        p.text((x0 + x1) / 2, (y0 + y1) / 2, txt, 24, fill=(40, 40, 90))


def s_plan(p, t, T):
    n = 1 + min(3, int(t / (T * 0.75) * 4))  # Nowak dorysowuje kolejne pomieszczenia
    plan_paper(p, n)


def s_point(p, t, T):
    plan_paper(p)
    k = ease(t / (T * 0.6))
    px, py = 700 - 250 * k, 300 + 170 * k
    K.limb(p, (px + 420, H + 80), (px + 60, py + 60), 100, NW["top"], outline=4)
    p.ell(px + 50, py + 50, 54, 40, NW["skin"])
    p.line([(px, py), (px + 60, py + 50)], w=10, color=(30, 30, 90))


def s_understand(p, t, T):
    K.pharmacy_front(p, t)
    k = ease((t - T * 0.45) / 0.5)  # zrozumienie: oczy się otwierają, wzrok wraca w górę
    R.nurse_face(p, 640, 320, 1.0, 0.3 + 0.35 * k, t, gaze=(0.0, 0.4 - 0.5 * k))


def s_ask(p, t, T):
    K.pharmacy_front(p, t)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.2, t, gaze=(0.8, 0.0))


def s_shrug(p, t, T):
    K.pharmacy_front(p, t)
    up = math.sin(min(1.0, t / 1.2) * math.pi)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(0.0, 0.8), mouth=talk(t, T * 0.5), breath=up * 3)


def s_speak(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "nowak", t, gaze=(-0.3, 0.2), mouth=talk(t, T), fear=0.3)


def s_pipes(p, t, T):
    p.rect(0, 0, W, H, (58, 62, 66), w=0)
    knock = (t % 1.1) < 0.18  # rury drżą od stukania
    for k, (y, wd) in enumerate(((180, 60), (320, 46), (440, 70))):
        dy = 3 * math.sin(t * 70 + k) if knock else 0
        p.rect(-20, y + dy, W + 20, y + wd + dy, (110 + k * 6, 104, 96))
        for x in range(80, W, 260):
            p.rect(x, y - 10 + dy, x + 30, y + wd + 10 + dy, (90, 90, 88))
    if knock:
        p.ell(500, 210, 4, 4, (170, 170, 160), w=0)


def s_grab(p, t, T):
    K.pharmacy_inside(p, t)
    k = ease(t / (T * 0.6))
    K.figure(p, 420, 760, 1.05, t, "zosia", look=-0.5, arms={"l": (-80 - 60 * k, 40 + 20 * k)})
    p.rect(-20, 430, 270, 600, (128, 98, 70))
    p.line([(-20, 430), (270, 430)], w=4)
    p.rect(180 + 40 * (1 - k), 400, 250 + 40 * (1 - k), 430, (60, 60, 60), w=2)  # latarka na ladzie


def s_block(p, t, T):
    p.rect(0, 0, W, H, (54, 58, 62), w=0)
    p.rect(-20, 600, W + 20, H + 20, (96, 94, 86))
    K.grille(p, 60, 40, 500, 620, gap=64, bar=12)
    K.grille(p, 780, 40, 1220, 620, gap=64, bar=12)
    k = ease(t / 0.6)  # rozkłada ręce w przejściu
    K.figure(p, 640, 760, 1.15, t, "henryk", look=0.0, arms={"l": (-14 - 106 * k, 95 - 75 * k), "r": (14 + 106 * k, 95 - 75 * k)})


def s_window_dark(p, t, T):
    p.rect(0, 0, W, H, (96, 100, 96), w=0)
    k = ease(t / T)  # niebo za okienkiem gaśnie
    p.rect(300, 180, 980, 520, tuple(int(a + (b - a) * k) for a, b in zip((120, 130, 150), (20, 24, 32))), w=8)
    for k2 in range(1, 5):
        p.line([(300 + k2 * 136, 180), (300 + k2 * 136, 520)], w=14, color=(56, 58, 58))


def s_givein(p, t, T):
    K.pharmacy_front(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.6, 0.5), mouth=talk(t, T * 0.5), fear=0.2, blink_k=0.3)


def s_four(p, t, T):
    K.pharmacy_inside(p, t, dark=1.0)
    nod = ease((t - T * 0.5) / 0.8)  # narrator przysypia, Nowak chowa ręce, Henryk patrzy
    for who, x in (("zosia", 260), ("narrator", 520), ("henryk", 780), ("nowak", 1040)):
        g = {"henryk": (0.6 * nod, -0.2), "narrator": (0.0, 0.8 * nod)}.get(who)
        K.sitting(p, x, 690, 0.7, t, who, gaze=g, eyes=1 - nod * 0.8 if who == "narrator" else None)


def s_sleeves(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    k = ease((t - 0.4) / 0.7)  # wzrok schodzi na rękawy
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.6, -0.1 + 1.1 * k))


def s_hide(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 30), w=0)
    K.face_cu(p, 640, 280, 1.0, "nowak", t, gaze=(0.0, 1.0), fear=0.5)
    k = ease(t / (T * 0.7))
    for side in (-1, 1):  # dłonie chowają się w rękawach fartucha
        x = 640 + side * 120
        K.limb(p, (x + side * 160, H + 60), (x, 560), 110, NW["top"], outline=4)
        if k < 0.95:
            p.ell(x - side * 10 * k, 540 + 20 * k, 46 * (1 - k * 0.8), 34 * (1 - k * 0.8), NW["skin"])
        p.ell(x, 560, 56, 40, NW["top"], w=4)  # mankiet przed dłonią


FNS = [B.card("DZIEŃ 5"), s_stairs, s_barricade, s_gap, s_whisper_door, s_open, s_collar,
       s_question, s_no, s_slide, s_stare, s_plan, s_point, s_understand, s_ask, s_shrug,
       s_portion, s_frown, s_speak, s_pipes, s_grab, s_block, s_window_dark, s_givein, s_four, s_sleeves, s_hide]
LOOK = [None] + [B.WARD] * 6 + [B.BASE] * 17 + [B.NIGHT] * 3
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
