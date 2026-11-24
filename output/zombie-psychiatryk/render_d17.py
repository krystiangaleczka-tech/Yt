"""Wariant A · dzień 17 „Noc przemiany” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 17
NW = K.WHO["nowak"]
WALL = (150, 166, 140)


def talk(t, T, a=0.3, b=0.4, speed=9):
    return 0.5 + 0.5 * math.sin(t * speed) if a < t < T - b else 0.0


def window_cu(p, t, inner, mesh=True):
    """Zbliżenie okienka izolatki: to, co za szybą, przycięte przez drzwi; siatka przed twarzą."""
    p.rect(0, 0, W, H, (30, 34, 34), w=0)
    inner(p)
    door = (124, 138, 122)
    for x0, y0, x1, y1 in ((-50, -50, 300, H + 50), (980, -50, W + 50, H + 50), (300, -50, 980, 90), (300, 630, 980, H + 50)):
        p.rect(x0, y0, x1, y1, door, w=0, amp=0)
    if mesh:
        for k in range(1, 6):
            p.line([(300 + k * 113, 90), (300 + k * 113, 630)], w=3, color=(60, 64, 60), amp=0.4)
            p.line([(300, 90 + k * 90), (980, 90 + k * 90)], w=3, color=(60, 64, 60), amp=0.4)
    p.rect(300, 90, 980, 630, None, w=8)


def nowak_in(p, t, **kw):
    window_cu(p, t, lambda q: K.face_cu(q, 640, 380, 1.0, "nowak", t, **kw))


def s_two(p, t, T):
    K.iso_door(p, t, inner=lambda q: K.face_cu(q, 640, 260, 0.45, "nowak", t, gaze=(0.0, 0.5), fear=0.5))
    K.sitting(p, 980, 700, 0.9, t, "henryk", gaze=(-0.3, -0.5))
    K.sitting(p, 230, 700, 0.9, t, "narrator", gaze=(0.6, -0.3 + 0.1 * math.sin(t)))


def s_daughter(p, t, T):
    nowak_in(p, t, gaze=(0.3, 0.2), mouth=talk(t, T), fear=0.5)


def s_tell_her(p, t, T):
    nowak_in(p, t, gaze=(0.0, 0.0), mouth=talk(t, T), fear=0.6)


def s_promise(p, t, T):
    p.rect(0, 0, W, H, WALL, w=0)
    k = ease((t - 0.3) / 0.4)
    R.nurse_face(p, 640, 320 + 8 * k, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(-0.6, -0.3), body=(640, 320))


def s_words(p, t, T):
    slow = 9 - 6 * ease(t / T)  # słowa coraz wolniej
    nowak_in(p, t, gaze=(0.3 * math.sin(t), 0.4), mouth=talk(t, T, speed=slow), fear=0.7)


def notes(p, lines, t, T):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    n = min(len(lines), int(t / (T * 0.8) * len(lines)) + 1)
    K.paper(p, 600, 340, lines[:n], w=560, h=330)
    x = 600 + 180
    K.limb(p, (x + 380, H + 80), (x + 30, 480), 80, K.narr_sleeve(), outline=4)
    p.ell(x + 20, 470, 40, 30, K.SKIN)
    p.line([(x, 450), (x - 30, 420)], w=6, color=(40, 40, 120))


def s_notes(p, t, T):
    notes(p, ["14:20 — mówi do siebie", "16:05 — pojedyncze słowa", "19:40 — ?"], t, T)


def s_white_eyes(p, t, T):
    k = ease(t / T)  # oczy bieleją od brzegów; przestaje mrugać
    window_cu(p, t, lambda q: K.face_cu(q, 640, 380, 1.4, "nowak", t, gaze=(0.0, 0.0), blink_k=0.0, fear=0.5), mesh=False)
    for side in (-1, 1):  # źrenica znika pod bielmem, od brzegów do środka
        ex, ey = 640 + side * 46 * 1.4, 380 + 6 * 1.4
        p.ell(ex, ey, 8.5 * k, 8.5 * k, (236, 238, 226), w=0)


def s_notes2(p, t, T):
    notes(p, ["gorączka", "cisza", "brak mrugania", "kołysanie"], t, T)


def s_dark_window(p, t, T):
    window_cu(p, t, lambda q: q.rect(300, 90, 980, 630, (14, 16, 16), w=0))


def s_slam(p, t, T):
    k = ease(t / 0.18)  # twarz uderza w szybę — jak Henryk w pierwszą noc
    window_cu(p, t, lambda q: (q.rect(300, 90, 980, 630, (14, 16, 16), w=0),
                               K.face_cu(q, 640, 380, 0.6 + 0.6 * k, "nowak", t, gaze=(0.0, 0.0), blink_k=0.0, fear=0.9, white=True)))
    if 0.15 < t < 0.35:
        p.line([(520, 200), (600, 300), (560, 380)], w=3, color=(230, 230, 230))


def s_realize(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    k = ease((t - 0.3) / 0.8)
    R.nurse_face(p, 640, 320, 1.0, 0.3 + 0.4 * k, t, gaze=(0.8 * k, 0.0))


def s_warned(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.6, 0.0))


def s_smile(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    K.face_cu(p, 640, 330, 1.0, "henryk", t, gaze=(-0.5, 0.0))
    k = ease((t - 0.4) / 0.6)  # kąciki ust idą w górę
    with K.on_face(p, "henryk"):
        for side in (-1, 1):
            p.line([(640 + side * 18, 412), (640 + side * (24 + 6 * k), 412 - 8 * k)], w=4)


def s_breath_fog(p, t, T):
    def inner(q):
        q.rect(300, 90, 980, 630, (20, 22, 24), w=0)
        K.face_cu(q, 640, 400, 1.2, "nowak", t, gaze=(0.0, 0.0), blink_k=0.0, fear=0.4, white=True)
    window_cu(p, t, inner, mesh=False)
    period = 1.2 + 1.2 * t / T  # para coraz rzadziej
    ph = (t % period) / period
    if ph < 0.4:
        a = 1 - ph / 0.4
        p.ell(640, 520, 160 * a + 40, 70 * a + 20, (210, 220, 220), w=0)


def s_same_rhythm(p, t, T):
    K.iso_door(p, t, inner=lambda q: K.face_cu(q, 640, 260, 0.45, "nowak", t, gaze=(0.0, 0.0), blink_k=0.0, fear=0.4, white=True))
    br = math.sin(t * 2 * math.pi / 4.0)  # ten sam powolny rytm co Nowak za szybą
    K.sitting(p, 980, 700 - 4 * br, 0.95, t, "henryk", gaze=(-0.2, -0.6))


def s_why(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    R.nurse_face(p, 640, 320, 1.0, 0.35 if 0.3 < t < T - 0.4 else 0.25, t, gaze=(0.7, 0.2))


def s_patrze(p, t, T):
    p.rect(0, 0, W, H, (190, 200, 196), w=0)  # zaparowana szyba
    for i in range(40):
        p.ell(100 + (i * 157) % 1080, 80 + (i * 97) % 560, 30, 20, (205, 214, 210), w=0)
    word = R.tr("PATRZĘ")  # wersja językowa: słowo pisane litera po literze
    n = min(len(word), int(t / (T * 0.8) * len(word)) + 1)
    p.text(600, 360, word[:n], 150, fill=(120, 130, 128))
    off = 260 * ease((t - T * 0.82) / (T * 0.15))  # słowo skończone: dłoń odsuwa się, widać całe „PATRZĘ” z ogonkiem
    x = 330 + n * 95 + off
    y0 = off * 0.9
    K.limb(p, (x + 300, H + 100 + y0), (x + 20, 420 + y0), 90, K.WHO["henryk"]["top"], outline=4)
    p.ell(x + 10, 410 + y0, 44, 32, K.WHO["henryk"]["skin"])
    p.line([(x, 390 + y0), (x - 20, 350 + y0)], w=14, color=K.WHO["henryk"]["skin"])


def s_turns_wall(p, t, T):
    k = ease((t - 0.3) / (T * 0.6))  # odchodzi od okienka i staje twarzą do ściany
    def inner(q):
        q.rect(300, 90, 980, 630, (120, 130, 126), w=0)
        if k < 0.5:
            K.face_cu(q, 640, 380 + 200 * k, 1.0 - 0.8 * k, "nowak", t, gaze=(0.0, 0.0), blink_k=0.0, white=True)
        else:
            K.zombie_back(q, 640, 640, 1.4, t, 170, gown=(226, 226, 220))
    window_cu(p, t, inner)


def s_sleeps(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    k = ease((t - 0.3) / 0.8)  # dopiero teraz zamyka oczy
    K.face_cu(p, 640, 330 + 10 * k, 1.0, "henryk", t, gaze=(0.0, 0.3), blink_k=k, breath=math.sin(t * 1.2))


FNS = [B.card("DZIEŃ 17"), s_two, s_daughter, s_tell_her, s_promise, s_words, s_notes, s_white_eyes, s_notes2, s_dark_window,
       s_slam, s_realize, s_warned, s_smile, s_breath_fog, s_same_rhythm, s_why, s_patrze, s_turns_wall, s_sleeps]
LOOK = [None] + [B.WARD] * 8 + [B.NIGHT] * 9 + [B.WARD] * 2
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
