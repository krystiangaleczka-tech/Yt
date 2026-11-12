"""Wariant A · dzień 1 „Telefon” — 31 ujęć rysowanych kodem, w stylu render.py / render2.py.

Czasy i kolejność ujęć z docs/filmy/oddzial-c/ujecia/a_dane1.py (dzień 1), napisy z kwestii lektora i dialogów.
uruchom:  python3 render_d01.py            → dzien01.mp4 (bez dźwięku, do podglądu)
          python3 render_d01.py 12.5 40    → klatki kontrolne w podanych sekundach (od początku dnia)
kontrola: python3 ../../scripts/kontrola_ujec.py render_d01.py
"""
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import render as _R0
from PIL import Image

import kit_a as K
import render as R
import render2 as R2
from render import FPS, H, INK, SS, W, Pen, ease, framed, handheld, light_mask, noise, subtitle

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
from a_dane1 import DAYS  # noqa: E402

DAY = 1
ROWS = [shot for _, _, beats in next(d for d in DAYS if d[0] == DAY)[2] for _, shots in beats for shot in shots]


def spoken(sound):
    """Napis z kwestii: lektor bez znaku, dialog z myślnikiem."""
    if sound.startswith("L:"):
        return sound[2:].strip()
    m = re.search(r"„([^”]+)”", sound)
    return "— " + m.group(1) if m else ""


def wrap(txt, n=40):
    out, line = [], ""
    for w in txt.split():
        if len(line) + len(w) + 1 > n and line:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return "\n".join(out + [line])


# ---------- ujęcia (p, t — czas od początku ujęcia, T — długość) ----------

def s01_card(p, t, T):
    p.rect(0, 0, W, H, (0, 0, 0), w=0)
    p.text(640, 330, "ODDZIAŁ C", 64, fill=(236, 236, 230))
    p.text(640, 410, "DO ŚWITU", 34, fill=(200, 200, 194))


def s02_phone(p, t, T):
    K.phone_detail(p, t, ring=int(t * 3) % 2 == 0)


def s03_grab(p, t, T):
    K.duty_room(p, dark=True)
    s, y = 0.85, 640
    x = 1000 - 300 * ease(t / 1.1)
    sh = (x - 50 * s, y - 268 * s)  # lewy bark
    rest, phone, ear = (-14, 95), ((585 - sh[0]) / s, (408 - sh[1]) / s), (6, -66)
    grab, up = ease((t - 0.6) / 0.6), ease((t - 1.5) / 0.7)
    held = t > 1.2
    hand = tuple(r + (ph - r) * grab for r, ph in zip(rest, phone)) if not held else \
        tuple(ph + (e - ph) * up for ph, e in zip(phone, ear))
    # stoi za biurkiem: najpierw on, potem całe biurko i telefon przed nim
    K.figure(p, x, y, s, t, "narrator", walk=t if t < 1.1 else None, look=-0.4 + 0.3 * up, arms={"l": hand}, mouth=0.5)
    if held:  # słuchawka w dłoni, przy uchu stoi pionowo
        hx, hy = sh[0] + hand[0] * s, sh[1] + hand[1] * s
        ang = 1.4 * up
        K.limb(p, (hx - 34 * math.cos(ang), hy - 34 * math.sin(ang)), (hx + 34 * math.cos(ang), hy + 34 * math.sin(ang)),
               14, (196, 186, 152), outline=2.5)
        p.ell(hx, hy, 11 * s, 11 * s, K.SKIN)
    p.rect(470, 420, 790, 450, (110, 84, 60))
    p.rect(490, 450, 520, 560, (96, 72, 52))
    p.rect(740, 450, 770, 560, (96, 72, 52))
    K.desk_phone(p, handset=False)
    if not held:  # słuchawka leży na blacie przed aparatem, jak po upadku
        p.poly([(560, 414), (626, 410), (628, 418), (562, 422)], (196, 186, 152), w=2.5)

def handset_cu(p, x, y):
    """Słuchawka przy uchu i ustach narratora w zbliżeniu (z prawej strony twarzy)."""
    K.limb(p, (x + 150, y - 10), (x + 70, y + 120), 46, (196, 186, 152), outline=4)
    p.ell(x + 150, y - 6, 44, 34, (196, 186, 152), rot=0.9)
    p.ell(x + 66, y + 124, 40, 30, (196, 186, 152), rot=0.9)
    K.limb(p, (x + 230, y + 420), (x + 176, y + 60), 70, K.UNI, outline=4)
    p.ell(x + 176, y + 40, 40, 46, K.SKIN)


def s04_listen(p, t, T):
    p.rect(0, 0, W, H, (40, 50, 62), w=0)
    p.rect(980, 120, 1200, 300, (110, 140, 118), w=5)  # szyba drzwi, za nią jasny korytarz
    gx = min(1.0, 0.4 + ease(t / 1.2))
    K.narrator_cu(p, 600, 330, 1.0, 0.7, t, gaze=(gx, -0.1), blink_k=0.0, breath=math.sin(t * 5) * 0.4)
    handset_cu(p, 600, 330)


def s05_mouth(p, t, T):
    p.rect(0, 0, W, H, (40, 50, 62), w=0)
    K.narrator_cu(p, 600, 330, 1.0, 0.25, t, gaze=(1.0, 0.0), breath=0.0)
    for side in (-1, 1):  # policzki nadęte od wstrzymanego oddechu
        p.ell(600 + side * 76, 400, 22, 16, (238, 186, 168), w=0)
    handset_cu(p, 600, 330)


def s06_look(p, t, T):
    p.rect(0, 0, W, H, (40, 50, 62), w=0)
    K.narrator_cu(p, 640, 280, 1.0, 0.5, t, gaze=(0.1, 1.0), blink_k=R.blink(t, 21, 1.6), breath=math.sin(t * 3) * 0.5)
    # słuchawka trzymana oburącz przed piersią, ponad napisami
    for side in (-1, 1):
        K.limb(p, (640 + side * 170, H + 40), (640 + side * 95, 545), 60, K.UNI, outline=4)
    p.poly([(560, 520), (720, 510), (722, 532), (562, 542)], (196, 186, 152), w=3)
    p.ell(560, 530, 30, 26, (196, 186, 152))
    p.ell(722, 520, 30, 26, (196, 186, 152))
    for side in (-1, 1):
        p.ell(640 + side * 95, 545, 34, 28, K.SKIN)

def s07_lay(p, t, T):
    k = ease(t / 1.6)
    pos = (640 - 60 - 60 * k, 460 - 60 + 138 * k, -0.1 - 0.22 * k)
    withdraw = ease((t - 1.8) / 0.8)
    hand = None if withdraw >= 1 else (pos[0] + 30 + 300 * withdraw, pos[1] - 20 - 500 * withdraw)
    K.phone_detail(p, t, ring=False, handset=pos, hand=hand)


TURN8 = (0.6, 1.4, 0.9, 2.1)  # każdy odwraca głowę ku telefonowi kiedy indziej


def s08_pov(p, t, T, turn=True):
    p.rect(0, 0, W, H, (40, 50, 60), w=0)
    p.rect(330, 60, 950, 760, (56, 66, 72))
    p.rect(420, 120, 860, 420, (172, 190, 160), w=0)
    sil = (24, 28, 30)
    for i, (x, sc) in enumerate(((480, 0.9), (590, 1.0), (700, 0.85), (805, 1.05))):
        s = 0.9 * sc
        y = 460 + 3 * math.sin(t * 2.2 + i)
        x += 4 * math.sin(t * 1.3 + i * 2)
        p.poly([(x - 44 * s, y - 180 * s), (x + 44 * s, y - 180 * s), (x + 50 * s, y + 40), (x - 50 * s, y + 40)], sil, w=3)
        k = ease((t - TURN8[i]) / 0.6) if turn else 0.0
        hx = x - 8 * s * k
        p.ell(hx, y - 222 * s, 36 * s, 42 * s, sil, w=3)
        p.ell(hx + (18 - 44 * k) * s, y - 228 * s, 4 * s, 5 * s, (200, 204, 190), w=0)  # oko: z profilu ku telefonowi (w lewo)
    for x0, y0, x1, y1 in ((-50, -50, 330, H + 50), (950, -50, W + 50, H + 50)):
        p.rect(x0, y0, x1, y1, (40, 50, 60), w=0)
    for x0, y0, x1, y1 in ((330, 120, 420, 420), (860, 120, 950, 420), (330, 60, 950, 120), (330, 420, 950, H + 50)):
        p.rect(x0, y0, x1, y1, (56, 66, 72), w=0)
    p.rect(330, -50, 950, 60, (40, 50, 60), w=0)
    for xx in (330, 950):
        p.line([(xx, 60), (xx, H + 20)], w=4)
    p.line([(330, 60), (950, 60)], w=4)
    p.rect(420, 120, 860, 420, None, w=7)


def s09_key(p, t, T):
    K.keyhole(p, t, T, plate=(120, 130, 120), wall=(52, 62, 70))


def side_door(p, t, op):
    """Boczne drzwi dyżurki na lewej ścianie korytarza, blisko kamery; op 0..1 — uchylenie."""
    p.poly([(90, 140), (300, 210), (300, 640), (90, 720)], (40, 46, 44))
    xo = 90 + 210 * (1 - op)
    p.poly([(90, 140), (xo, 210 - 40 * op), (xo, 640 + 50 * op), (90, 720)], (124, 138, 122))
    p.line([(90, 140), (300, 210), (300, 640), (90, 720)], w=4)


def s10_slip(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1], vp=(820, 320), doors_open=0.9)
    op = 0.65 * ease(t / 1.0)
    out = ease((t - 0.8) / 2.4)
    # otwór drzwi na lewej ścianie: ciemne wnętrze, framuga, skrzydło otwiera się do środka
    p.poly([(90, 150), (300, 214), (300, 640), (90, 712)], (24, 28, 28))
    xo = 90 + 210 * (1 - op)
    p.poly([(90, 150), (xo, 214 - 40 * op), (xo, 640 + 46 * op), (90, 712)], (124, 138, 122))
    if out > 0:  # wysuwa się z otworu bokiem, plecami do ściany
        K.figure(p, 190 + 170 * out, 760, 1.05, t, "narrator", look=1.0, mouth=0.0, arms={"l": (-20, 70), "r": (10, 90)})
    p.line([(90, 150), (300, 214)], w=5)
    p.poly([(282, 208), (300, 214), (300, 640), (282, 646)], (150, 166, 140))  # dalsza framuga
    p.poly([(60, 130), (100, 146), (100, 760), (60, 760)], (150, 166, 140))  # bliższa framuga, przed nim

CROWD11 = [(-70, 0.0, 0.34), (-20, 0.4, 0.38), (40, 0.2, 0.36), (95, 0.7, 0.33), (5, 0.9, 0.4)]


def s11_along(p, t, T):
    R.corridor(p, t, [1, 1, 1 if math.sin(t * 29) > -0.4 else 0, 1], doors_open=0.9)
    p.rect(610, 290, 670, 330, (182, 200, 168), w=3)  # szyba dyżurki na końcu korytarza świeci
    for i, (dx, ph, s) in enumerate(CROWD11):
        R.zombie(p, 640 + dx, 412 + 6 * i, s, t + ph, 30 + i, tilt=0.1 * math.sin(i))
    k = t / T
    K.figure(p, 150 + 220 * k, 740 - 40 * k, 1.0 - 0.12 * k, t * 0.6, "narrator", walk=t * 0.6, look=1.0,
             arms={"l": (-24, 60), "r": (14, 90)}, mouth=0.0)


def s12_profile(p, t, T):
    p.rect(0, 0, W, H, (128, 142, 120), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    K.zombie_profile(p, 640, 300, 1.0, t)


def s13_hold(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    gx = 0.8 * noise(t, 31, 1.4)
    K.narrator_cu(p, 640, 320, 1.0, 0.28, t, gaze=(gx, 0.0), blink_k=0.0, breath=0.0)
    with K.on_face(p, "narrator"):  # nadęte policzki idą za głową (rig)
        for side in (-1, 1):
            p.ell(640 + side * 76, 390, 22, 16, (238, 186, 168), w=0)


def iso_end_door(p):
    """Zamknięte drzwi izolatki 3 na końcu korytarza: okienko z siatką i tabliczka."""
    p.rect(610, 290, 670, 410, (124, 138, 122), w=3)
    p.rect(625, 302, 655, 326, (20, 24, 24), w=2)
    for i in range(4):
        p.line([(625 + i * 8, 302), (633 + i * 8, 326)], w=1, color=(80, 90, 84), amp=0.3)
    p.rect(628, 336, 652, 346, (196, 196, 180), w=1.5)


def s14_end(p, t, T):
    R.corridor(p, t, [1, 0, 1, 1], doors_open=0.9)
    iso_end_door(p)


def henryk_window(p, k):
    """Kadr okienka izolatki z render.scene3 długo po uderzeniu (k — sekundy od uderzenia)."""
    R.scene3(p, R.SLAM_T - R.SCENES[2][0] + k, 5.6)


def s15_window(p, t, T):
    henryk_window(p, 5 + t)


def s16_fog(p, t, T):
    henryk_window(p, 3.3 + t)


def s17_hand(p, t, T):
    henryk_window(p, 9 + t)
    # dłoń w okienku: wdech (unosi się), trzymanie, wydech (opada) — tylko w obrębie okienka
    ph = (t % 4.0) / 4.0
    lift = ease(ph / 0.33) * (1 - ease((ph - 0.66) / 0.33))
    hx, hy = 576, 300 - 90 * lift  # lewa strona okienka, przed twarzą — z dala od krwi na szybie
    skin = (200, 208, 188)
    p.ell(hx, hy, 36, 30, skin, w=4)
    for i in range(4):
        p.line([(hx - 24 + i * 15, hy - 18), (hx - 22 + i * 15, hy - 44)], w=8, color=skin)
        p.line([(hx - 24 + i * 15, hy - 18), (hx - 22 + i * 15, hy - 44)], w=2)
    p.rect(470, 341, 810, 400, (112, 126, 112), w=0, amp=0)  # nadgarstek nie wychodzi pod okienko
    K.mesh(p)
    p.rect(470, 120, 810, 360, None, w=8)
    p.rect(560, 400, 720, 450, (196, 196, 180), w=3)
    p.text(640, 425, "IZOLATKA 3", 22)


def s18_breathe(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    br = math.sin(2 * math.pi * 0.25 * t)
    K.narrator_cu(p, 640, 320, 1.0, 0.1, t, gaze=(0.0, 0.3), blink_k=0.45, breath=br * 1.4)


def s19_isokey(p, t, T):
    K.keyhole(p, t, T, plate=(96, 108, 98), wall=(112, 126, 112), ring=True)


def s20_out(p, t, T):
    p.rect(0, 0, W, H, (112, 126, 112), w=0)
    p.rect(0, 470, W, H, (92, 104, 92), w=0)
    p.rect(330, 80, 650, 640, (16, 20, 20))  # otwarte drzwi izolatki, w środku ciemno
    p.rect(290, 60, 330, 660, (124, 138, 122))  # framuga zostaje na miejscu przez całe ujęcie
    p.rect(650, 60, 690, 660, (124, 138, 122))
    p.rect(290, 40, 690, 80, (124, 138, 122))
    p.rect(470, 50, 520, 70, (196, 196, 180), w=2)
    step = ease(t / 1.6)
    reach = ease((t - 1.9) / 0.7)
    s = 0.95 + 0.08 * step
    hx, hy = 490 + 150 * step, 650 + 40 * step  # wychodzi aż do narratora: ręka sięga rękawa bez rozciągania
    NX = 830
    K.figure(p, NX, 700, 1.0, t, "narrator", look=-0.8, arms={"l": (-30, 80)}, mouth=0.3)
    sleeve = (NX - 50 - 30 + 10, 700 - 268 + 70)  # rękaw narratora nad łokciem
    sh = (hx + 50 * s, hy - 268 * s)
    target = ((sleeve[0] - sh[0]) / s, (sleeve[1] - sh[1]) / s)
    arm = (20 + (target[0] - 20) * reach, 90 + (target[1] - 90) * reach)
    # wychodzi z izolatki ku kamerze — jest przed framugą
    K.figure(p, hx, hy, s, t, "henryk", walk=t if t < 1.6 else None, look=0.4, arms={"r": arm})

def s21_lead(p, t, T, k0=0.0, k1=1.0):
    R.corridor(p, t, [1, 1, 0 if math.sin(t * 23) > 0.6 else 1, 1], doors_open=0.9)
    crowd = [(-330, 0.62, 0.0), (300, 0.6, 0.5), (-150, 0.5, 0.2), (180, 0.45, 0.8), (-40, 0.38, 0.35), (120, 0.36, 0.6)]
    k = k0 + (k1 - k0) * t / T
    walkers = [(560 - 40 * k, 560 + 90 * k, 0.62 + 0.18 * k, "henryk"), (680 - 40 * k, 545 + 90 * k, 0.6 + 0.18 * k, "narrator")]
    items = [(420 + 260 * s, ("z", 640 + dx, 420 + 260 * s, s, ph)) for dx, s, ph in crowd]
    items += [(y, ("f", x, y, s, who)) for x, y, s, who in walkers]
    for _, it in sorted(items, key=lambda v: v[0]):
        if it[0] == "z":
            _, x, y, s, ph = it
            R.zombie(p, x, y, s, t + ph, 50 + int(ph * 10), tilt=0.12 * math.sin(ph * 7))
        else:
            _, x, y, s, who = it
            K.figure(p, x, y, s, t * 0.5, who, walk=t * 0.5, look=0.0, arms={"r": (30, 70)} if who == "henryk" else None)


def s22_shoe(p, t, T):
    p.rect(0, 0, W, H, (92, 104, 92), w=0)
    for i in range(-2, 8):
        p.line([(i * 220, 0), (i * 220 - 160, H)], w=3, color=(60, 70, 62))
    for j in range(1, 5):
        p.line([(0, j * 170), (W, j * 170 - 40)], w=3, color=(60, 70, 62))
    p.ell(640, 600, 300, 70, (120, 138, 128), w=0)  # mokra plama
    p.glow([(420, 580), (860, 560), (840, 620), (440, 640)], (220, 235, 225, 50))
    down = ease(t / 0.8)
    y = 320 + 210 * down  # podeszwa ląduje na kafelku
    # but z boku: podeszwa, cholewka, nosek, sznurówki; nad nim kostka i nogawka
    p.poly([(400, y + 60), (860, y + 60), (900, y + 40), (890, y + 80), (400, y + 82)], (196, 196, 190), w=4)
    p.poly([(410, y + 60), (420, y - 40), (560, y - 70), (640, y - 50), (760, y - 10), (870, y + 10), (880, y + 60)],
           (240, 240, 236), w=4)
    p.poly([(780, y - 6), (870, y + 12), (882, y + 58), (790, y + 58)], (226, 226, 220), w=3)
    for k in range(4):
        p.line([(580 + k * 42, y - 52 + k * 10), (604 + k * 42, y - 30 + k * 10)], w=4)
    K.limb(p, (500, y - 50), (470, -80), 150, (226, 192, 166), outline=4)
    K.limb(p, (480, y - 120), (440, -80), 190, K.TROUSERS, outline=4)
    if t > 0.85:  # pisk podeszwy na mokrym kafelku
        for side in (-1, 1):
            for k in range(3):
                p.line([(650 + side * (290 + k * 26), y + 70 - k * 14), (650 + side * (310 + k * 26), y + 46 - k * 16)], w=4)

def s23_freeze(p, t, T):
    R.corridor(p, t, [1, 1, 1, 0], doors_open=0.9)
    frz = min(t, 0.5)  # zastyga w pół kroku
    R.zombie(p, 640, 850, 2.4, frz, 61, tilt=0.3 * (1 - ease((t - 0.6) / 1.4)))


def s24_cover(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    K.narrator_cu(p, 640, 320, 1.0, 0.85, t, gaze=(0.0, 0.0), blink_k=0.0, breath=0.0)
    skin = (184, 194, 170)
    hx, hy = 620 + 4 * noise(t, 33, 3), 404
    K.limb(p, (hx - 380, H + 60), (hx - 60, hy + 30), 80, (150, 154, 148), outline=4)
    p.ell(hx, hy, 96, 54, skin, w=4)
    for i in range(4):
        p.line([(hx - 30 + i * 30, hy - 30), (hx - 10 + i * 34, hy + 34)], w=2.5)


def s25_back(p, t, T):
    R.corridor(p, t, [1, 1, 1, 0], doors_open=0.9)
    p.rect(610, 290, 670, 330, (182, 200, 168), w=3)
    k = ease(t / T)
    K.zombie_back(p, 640 + 30 * k, 760 - 180 * k, 1.1 - 0.4 * k, t, 61, walk=t * 0.7)


def s26_stairs(p, t, T):
    """Schodzą z podestu na kamerę: Henryk przy ścianie, z dłonią na poręczy, wolniej; narrator dwa stopnie za nim."""
    K.stair_flight(p, t, dark=0.1)
    K.st_group(p, t, [dict(who="henryk", a=11, b=3, step=0.47, x=-0.74, rail=True),
                      dict(who="narrator", a=14, b=5, step=0.42, t0=0.1, lead="r", x=-0.2, look=0.15)])

def flick_at(t):
    return 0.7 if math.sin(t * 23) * math.sin(t * 5.1) > 0.55 else 1.0


def s27_basement(p, t, T):
    K.basement(p, t, flick_at(t))


def s28_zosia(p, t, T):
    fl = flick_at(t)
    K.pharmacy_front(p, t, fl)
    low = ease((t - 1.6) / 1.2)
    K.figure(p, 640, 905, 1.8, t, "zosia", look=-0.1, arms={"r": (40 - 20 * low, -150 + 220 * low)}, eyes=1.0, mouth=0.2)
    hx, hy = 640 + 50 * 1.8 + (40 - 20 * low) * 1.8, 905 - 268 * 1.8 + (-150 + 220 * low) * 1.8
    for a in (0.6, -0.6):  # nożyczki w dłoni
        p.line([(hx, hy), (hx + 60 * math.sin(a), hy - 60 * math.cos(a))], w=6, color=(170, 172, 176))
    K.grille(p, -20, -20, W + 20, H + 20)


def s29_padlock(p, t, T):
    p.rect(0, 0, W, H, (140, 136, 112), w=0)
    K.grille(p, 100, -40, 1180, H + 40, gap=180, bar=26)
    open_ = ease((t - 1.6) / 0.6)
    p.line([(280, 300), (420, 360), (560, 340), (700, 380), (840, 350), (980, 400)], w=14, color=(120, 120, 116))
    p.rect(560, 380, 720, 560, (186, 160, 80), w=4)
    p.ell(640, 380 - 50 * open_, 70, 70, None, w=14)
    p.ell(640, 470, 12, 18, (60, 50, 30), w=2)
    for side in (-1, 1):
        hx = 640 + side * 190
        K.limb(p, (hx + side * 200, H + 80), (hx, 520), 110, (52, 62, 92), outline=4)
        p.ell(hx - side * 20, 500, 80, 60, (234, 204, 182))


def s30_whisper(p, t, T):
    fl = flick_at(t)
    K.pharmacy_front(p, t, fl)
    mouth = 0.5 + 0.5 * math.sin(t * 9) if 0.3 < t < 3.4 else 0.0
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.2, -0.8), mouth=mouth, fear=0.4)
    K.grille(p, 220, -40, 1060, H + 40, gap=210, bar=22)


def s31_noanswer(p, t, T):
    K.basement(p, t, 0.85)
    K.figure(p, 300, 760, 0.7, t, "henryk", look=-0.6, gaze=(-0.6, -1.0), eyes=1.0)
    K.narrator_cu(p, 790, 330, 1.0, 0.38, t, gaze=(-0.2, 0.9), blink_k=R.blink(t, 41, 2.6), breath=math.sin(t * 2) * 0.6)


def s_pov_still(p, t, T):
    s08_pov(p, t, T, turn=False)


def s_stare(p, t, T):
    p.rect(0, 0, W, H, (40, 50, 62), w=0)
    p.rect(1000, 110, 1240, 300, (110, 140, 118), w=5)
    K.narrator_cu(p, 560, 330, 1.0, 0.75, t, gaze=(1.0, -0.2), blink_k=0.0, breath=math.sin(t * 4) * 0.3)


def s_hold_dark(p, t, T):
    p.rect(0, 0, W, H, (40, 50, 62), w=0)
    K.narrator_cu(p, 640, 320, 1.0, 0.28, t, gaze=(0.6 * noise(t, 35, 1.5), 0.0), breath=0.0)
    with K.on_face(p, "narrator"):  # nadęte policzki idą za głową (rig)
        for side in (-1, 1):
            p.ell(640 + side * 76, 390, 22, 16, (238, 186, 168), w=0)


def s_profile2(p, t, T):
    p.rect(0, 0, W, H, (128, 142, 120), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    K.zombie_profile(p, 680, 300, 1.0, t + 2.0, seed=8)
    # pan Staś: siwy wianuszek włosów z tyłu głowy, siwy zarost na brodzie, koszula w paski
    arc = [(680 + 132 * math.cos(a), 300 + 152 * math.sin(a)) for a in [math.radians(d) for d in range(-50, 70, 10)]]
    p.line(arc, w=14, color=(214, 216, 208))
    for i in range(14):
        x0 = 568 + i * 9
        p.line([(x0, 392 + (i % 3) * 5), (x0 + 2, 398 + (i % 3) * 5)], w=3, color=(222, 224, 214))
    for k in range(5):
        p.line([(540 + k * 60, 470), (520 + k * 60, 720)], w=6, color=(130, 150, 170))

def s_recognise(p, t, T):
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(0, 430, W, H, (104, 124, 100), w=0)
    K.narrator_cu(p, 640, 320, 1.0, 0.45, t, gaze=(-0.9, 0.1), blink_k=R.blink(t, 37, 1.4), swallow=max(0.0, 1 - abs(t - 1.4) / 0.2))


def s_beep(p, t, T):
    K.phone_detail(p, t, ring=False)
    if int(t * 4) % 2 == 0:  # sygnał linii ze słuchawki
        for k in range(3):
            p.line([(380 - k * 26, 560 - k * 10), (356 - k * 26, 540 - k * 14)], w=4)


def s_heyes(p, t, T):
    henryk_window(p, 6 + t)


def s_lead2(p, t, T):
    s21_lead(p, t, T, k0=0.55, k1=1.0)


def s_enter(p, t, T):
    fl = flick_at(t)
    p.rect(0, 0, W, H, (54, 58, 62), w=0)  # za kratą ciemny korytarz piwnicy
    p.rect(-20, 560, W + 20, H + 20, tuple(int(c * fl) for c in (96, 94, 86)))
    k = ease(t / 1.2)  # najpierw skrzydło kraty odsuwa się do końca, za prawe skrzydło
    walkers = [(who, x0 + (x1 - x0) * ease((t - dl) / (T - dl)), ease((t - dl) / (T - dl)))
               for who, x0, x1, dl in (("henryk", 600, 520, 1.0), ("narrator", 700, 720, 1.35))]

    def walker(who, x, kk):
        K.figure(p, x, 560 + 150 * kk, 0.55 + 0.35 * kk, t * 0.5, who, walk=t * 0.5 if kk > 0 else None)

    for who, x, kk in walkers:  # jeszcze za kratą — krata jest przed nimi
        if kk < 0.12:
            walker(who, x, kk)
    K.grille(p, 120, 60, 520, 560, gap=64, bar=10)
    gx = 800 + 280 * k
    K.grille(p, gx - 280, 60, gx - 30, 560, gap=64, bar=10, col=(70, 74, 76))
    K.grille(p, 800, 60, 1160, 560, gap=64, bar=10)
    K.figure(p, 1100, 760, 0.95, t, "zosia", look=-0.8, arms={"l": (-60, 40)})
    for who, x, kk in walkers:  # przeszli przez otwartą kratę ku kamerze — są już przed nią
        if kk >= 0.12:
            walker(who, x, kk)
    for x0 in (0, 1180):  # regały apteki po bokach, bliżej kamery
        p.rect(x0, -20, x0 + 100, H + 20, (120, 100, 74))

def s_suspect(p, t, T):
    K.pharmacy_front(p, t, flick_at(t))
    talk = 0.5 + 0.5 * math.sin(t * 10) if 0.4 < t < 1.3 else 0.0
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-1.0, 0.0), mouth=talk, fear=0.2)


def s_answer(p, t, T):
    K.pharmacy_front(p, t, flick_at(t))
    K.narrator_cu(p, 640, 320, 1.0, 0.35 if 0.3 < t < 1.8 else 0.2, t, gaze=(0.8, 0.0), blink_k=R.blink(t, 39, 1.8))


def s_sit(p, t, T):
    fl = flick_at(t)
    K.pharmacy_front(p, t, fl)
    s, x, y = 1.3, 640, 700
    c = K.WHO["henryk"]
    K.figure(p, x, y, s, t, "henryk", look=0.0, eyes=1.0, legs=False, arms={"l": (70, 120), "r": (-70, 120)})
    hip = y - 112 * s
    for side in (-1, 1):  # podkulone kolana przed tułowiem, stopy na podłodze, dłonie na kolanach
        knee = (x + side * 70 * s, hip - 70 * s)
        K.limb(p, (x + side * 26 * s, hip), knee, 48 * s, c["top"])
        K.limb(p, knee, (x + side * 78 * s, y - 14), 40 * s, c["skin"])
        p.ell(x + side * 86 * s, y - 8, 30 * s, 13 * s, c["shoes"], w=3)
        p.ell(knee[0] - side * 6, knee[1] - 4, 14 * s, 14 * s, c["skin"])
    p.line([(0, y), (W, y)], w=3)

FNS = [s01_card, s02_phone, s03_grab, s04_listen, s_pov_still, s05_mouth, s06_look, s07_lay, s08_pov, s_stare, s_hold_dark,
       s09_key, s10_slip, s11_along, s12_profile, s13_hold, s_profile2, s_recognise, s_beep, s14_end, s15_window, s16_fog,
       s_heyes, s17_hand, s18_breathe, s19_isokey, s20_out, s21_lead, s22_shoe, s23_freeze, s24_cover, s25_back, s_lead2,
       s26_stairs, s27_basement, s28_zosia, s29_padlock, s_enter, s_suspect, s_answer, s30_whisper, s_sit, s31_noanswer]
assert len(FNS) == len(ROWS), (len(FNS), len(ROWS))

# kamera dla detali i zbliżeń, które potrzebują własnego środka (reszta wynika z ruchu w rozpisce)
CAM = {5: dict(cx=640, cy=420, zoom=2.4), 21: dict(cx=650, cy=330, zoom=2.0), 22: dict(cx=652, cy=258, zoom=2.6),
       15: dict(cy=330)}
# (mnożnik barwy, maska światła (cx, cy, r, ambient) albo None)
DARK = ((0.84, 0.92, 1.02), (640, 360, 640, 0.5))
WARD = ((0.92, 1.0, 0.94), None)
CELL = ((0.88, 0.98, 0.92), (640, 280, 520, 0.35))
BASE = ((0.9, 0.96, 1.0), (640, 300, 700, 0.45))
LOOK = [None] + [DARK] * 11 + [WARD] * 6 + [DARK, WARD] + [CELL] * 4 + [WARD, CELL] + [WARD] * 7 + [BASE] * 10

SCENES, t0, VWIN = [], 0.0, []
for k, (kadr, ruch, sec, desc, sound) in enumerate(ROWS):
    txt, win = spoken(sound), (0.3, sec - 0.4)  # dzień 1 po polsku: napis przez całe ujęcie
    if R.LANG == "en":  # angielski: napis tylko w czasie kwestii (en_film.py)
        import en_film
        txt = en_film.text(DAY, k, sound)
        if txt:
            vs, vl = en_film.placement(DAY, k, sound, sec, 0.5, min(sec - 0.8, len(txt.split()) / 2.7))
            win = (vs, vl + 0.35)
    SCENES.append((t0, t0 + sec, ruch, txt))
    VWIN.append(win)
    t0 += sec
DUR = t0
# gra aktorska ujęć z rigiem (rig_dni.py; FILM_RIG=0 — bez) i kurz w świetle apteki — jak w dniach z dzien_base
import os as _os  # noqa: E402
import rig_a  # noqa: E402
import rig_dni  # noqa: E402
RIG = rig_dni.RIG.get(DAY, {}) if _os.environ.get("FILM_RIG", "1") != "0" else {}


def camera(i, lt, T):
    ruch = SCENES[i][2]
    c = {"zoom": 1.0, "cx": 640, "cy": 360, **CAM.get(i, {})}
    k = ease(lt / T)
    if ruch == "naj":
        c["zoom"] *= 1 + 0.14 * k
    elif ruch == "odj":
        c["zoom"] *= 1.14 - 0.14 * k
    elif ruch == "pan":
        c["cx"] += 160 * (k - 0.5)
        c["zoom"] *= 1.15
    elif ruch == "jaz":
        c["cx"] += 70 * (lt / T - 0.5)
        c["zoom"] *= 1.06 + 0.04 * lt / T
    else:
        c["zoom"] *= 1.0 + 0.02 * lt / T
    return c


def shake(i, lt, t):
    ruch = SCENES[i][2]
    amp = {"ręka": 3.0, "drg": 5.0}.get(ruch, 0.0)
    if ruch == "szarp" and lt < 0.4:
        amp = 9 * (1 - lt / 0.4)
    return handheld(t, amp, seed=200 + i)


def frame(t):
    i = next((k for k, s in enumerate(SCENES) if s[0] <= t < s[1]), len(SCENES) - 1)
    a, b, ruch, txt = SCENES[i]
    lt, T = t - a, b - a
    rig_a.set_shot(DAY, i, lt, T, VWIN[i][0], max(0.0, VWIN[i][1] - 0.35) if (txt and R.LANG == "en") else 0.0, RIG.get(i))
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255))
    p = Pen(img, t, **framed(camera(i, lt, T), shake(i, lt, t)))
    FNS[i](p, lt, T)
    if LOOK[i] in (BASE, CELL):
        import dzien_base
        if dzien_base.KURZ:
            dzien_base.dust(p, DAY, i, lt, t)
    img = img.convert("RGB").resize((_R0.OW, _R0.OH), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    if LOOK[i]:
        grade, mask = LOOK[i]
        arr *= np.array(grade, dtype=np.float32)
        if mask:
            arr = light_mask(arr, *mask)
        yy, xx = _R0.grid()
        vig = 1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
        arr *= np.clip(vig, 0.35, 1)[..., None]
    arr += np.random.default_rng(int(t * FPS) // 3 + 13).normal(0, 5, (_R0.OH, _R0.OW, 1))  # ziarno 8×/s, jak kreska
    if i == 0:  # karta: wejście i wyjście przez czerń
        arr *= min(1.0, lt / 0.5, max(0.0, (T - lt) / 0.5))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    if txt and VWIN[i][0] <= lt < min(T - 0.1, VWIN[i][0] + VWIN[i][1]):
        subtitle(img, wrap(txt))
    return img


def main(stills=None):
    if stills:
        for s in stills:
            frame(s).save(HERE / f"d01-klatka-{s:06.2f}s.png")
        return
    out = HERE / "dzien01.mp4"
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", str(out)],
                            stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        proc.stdin.write(frame(k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(out)


if __name__ == "__main__":
    main([float(a) for a in sys.argv[1:]] or None)
