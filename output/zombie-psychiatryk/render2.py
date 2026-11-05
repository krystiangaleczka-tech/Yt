"""Część 2 (15 s): dyżurka. Używa kreski, postaci i korytarza z render.py.

Uruchom: python3 render2.py   (wynik: zombie-psychiatryk-2.mp4)
"""
import math
import random
import subprocess
import wave

import numpy as np
from PIL import Image

from render import (FPS, H, HERE, INK, SS, SUFFIX, VOICE_DIR, W, Pen, localize, blink, breath_snd, corridor, creak, ease, framed, handheld,
                    light_mask, noise, subtitle, voice_len, zombie)

DUR = 26.0
# (start, koniec, plik lektora, start lektora, napis) — z pauzami przed i po kwestiach
SCENES = [
    (0.0, 4.4, "p2_l1.wav", 0.50, "Pobiegłem do dyżurki\nna końcu korytarza."),
    (4.4, 11.0, "p2_l2.wav", 6.50, "Zamknąłem drzwi\ni zgasiłem światło."),
    (11.0, 17.0, "p2_l3.wav", 11.80, "Przez szybę widziałem,\njak przechodzą obok."),
    (17.0, 20.6, "p2_l4.wav", 18.60, "Wtedy zadzwonił telefon."),
    (20.6, 26.0, "p2_l5.wav", 21.10, "I wszyscy naraz\nodwrócili głowy."),
]
SCENES = localize(SCENES)
STUMBLE = 2.75         # w scenie 1: potknięcie w biegu
HANDLE = (2.7, 3.95)   # w scenie 2: sprawdza klamkę, czy drzwi na pewno zamknięte
SWITCH_T = 4.4 + 5.1   # pstryk — gaśnie światło
PEEK = (3.0, 4.6)      # w scenie 3: jeden z nich staje przy szybie
LAST_STOP = (5.25, 5.8)  # w scenie 3: ostatni też przystaje na chwilę
TEAR = 3.4             # w scenie 3: łza z jednego oka
RING_T = 17.0 + 0.9    # pierwszy dzwonek, po chwili ciszy
DROP = 2.0             # w scenie 4: od drgań słuchawka spada na stół
TURN_T = 20.6 + 1.3    # głowy odwracają się do szyby
RING_END = TURN_T + 0.9
DARK = 3.9             # w scenie 5: gaśnie wszystko poza oczami
VOICE_LEN = [voice_len(fn) for _, _, fn, _, _ in SCENES]
# (start marszu, skala) — w scenie 3 drugi dochodzi do środka szyby dokładnie na PEEK
WALKERS3 = [(0.0, 0.9), (PEEK[0] - 260 / 150, 1.0), (2.4, 0.85), (3.5, 1.05)]
# w scenie 5 wszyscy są w szybie, kiedy dzwoni; odwracają się nierówno — jeden spóźniony
WALKERS5 = [(1.3 - (x - 380) / 150, sc) for x, sc in ((470, 0.9), (585, 1.0), (690, 0.85), (800, 1.05))]
TURN_DELAY = (0.0, 0.35, 0.12, 0.75)

SKIN = (226, 192, 166)
HAIR = (58, 46, 38)
UNI = (150, 180, 190)
TROUSERS = (118, 148, 160)


def orderly_run(p, x, y, s, t, look=0.0):
    """Sanitariusz biegnie w stronę kamery. look 0..1 — ogląda się przez ramię."""
    ph = t * 11
    bob = abs(math.sin(ph)) * 10 * s
    y -= bob
    for side, sgn in ((-1, 1), (1, -1)):
        lift = max(0, math.sin(ph) * sgn) * 40 * s
        lx = x + side * 18 * s
        p.poly([(lx - 16 * s, y - 120 * s), (lx + 16 * s, y - 120 * s), (lx + 14 * s, y - 14 * s - lift),
                (lx - 14 * s, y - 14 * s - lift)], TROUSERS)
        p.ell(lx, y - 8 * s - lift, 18 * s, 10 * s, (240, 240, 236), w=3)
    p.poly([(x - 54 * s, y - 280 * s), (x + 54 * s, y - 280 * s), (x + 56 * s, y - 112 * s), (x - 56 * s, y - 112 * s)], UNI)
    p.poly([(x - 22 * s, y - 280 * s), (x, y - 252 * s), (x + 22 * s, y - 280 * s)], (244, 244, 240), w=3)
    for side, sgn in ((-1, 1), (1, -1)):
        sw = math.sin(ph) * sgn * 38 * s
        sx = x + side * 54 * s
        p.poly([(sx - 12 * s, y - 274 * s), (sx + 12 * s, y - 274 * s), (sx + side * 12 * s + 10 * s, y - 180 * s + sw),
                (sx + side * 12 * s - 10 * s, y - 180 * s + sw)], UNI)
        p.ell(sx + side * 12 * s, y - 172 * s + sw, 13 * s, 13 * s, SKIN)
    p.ell(x, y - 336 * s, 46 * s, 52 * s, SKIN)
    p.poly([(x - 47 * s, y - 336 * s), (x - 44 * s, y - 372 * s), (x - 10 * s, y - 392 * s), (x + 30 * s, y - 388 * s),
            (x + 48 * s, y - 360 * s), (x + 46 * s, y - 338 * s), (x + 20 * s, y - 360 * s), (x - 24 * s, y - 356 * s)], HAIR)
    fx = x + look * 26 * s  # twarz obraca się w bok
    for side in (-1, 1):
        if look > 0.6 and side < 0:
            continue  # dalsze oko schowane za nosem
        p.ell(fx + side * 18 * s, y - 330 * s, 10 * s, 11 * s, (246, 246, 240), w=3)
        p.ell(fx + side * 18 * s + look * 6 * s, y - 328 * s, 3.5 * s, 3.5 * s, INK, w=0)
        p.line([(fx + side * 8 * s, y - 348 * s), (fx + side * 28 * s, y - 352 * s + side * 2 * s)], w=3)
    p.ell(fx, y - 302 * s, 9 * s, 12 * s, (70, 30, 30), w=3)


def scene1(p, t, T):
    fl = [1, 1 if math.sin(t * 27) > -0.3 else 0, 1, 0 if t > 1.5 else 1]
    corridor(p, t, fl, doors_open=0.9)
    for i, dx in enumerate((-70, 40, 110)):
        zombie(p, 640 + dx, 420 + 15 * t, 0.42 + 0.06 * t, t, i * 1.3, arms=ease((t - 2.0 - 0.12 * i) / 0.4))
    k = ease(t / T)
    look = ease((t - 1.5) / 0.25) * (1 - ease((t - 2.2) / 0.25))
    st = max(0.0, 1 - abs(t - STUMBLE) / 0.2)  # potknięcie: zapada się i odbija w bok
    orderly_run(p, 640 + 30 * math.sin(t * 2) + 24 * st, 560 + 160 * k + 46 * st, 0.8 + 0.7 * k, t, look=look)


def room(p, dark):
    wall = (78, 96, 104) if not dark else (46, 58, 70)
    p.rect(0, 0, W, H, wall, w=0)
    p.poly([(0, 560), (W, 560), (W, H), (0, H)], (70, 76, 70))
    p.line([(0, 560), (W, 560)], w=4)
    # kalendarz i szafka
    p.rect(120, 150, 260, 320, (214, 210, 196), w=3)
    p.rect(120, 150, 260, 190, (160, 60, 52), w=3)
    for r in range(4):
        for c in range(5):
            p.rect(134 + c * 25, 204 + r * 27, 152 + c * 25, 222 + r * 27, None, w=1.5)
    p.rect(300, 260, 470, 560, (120, 118, 104))
    p.line([(385, 260), (385, 560)], w=3)
    p.ell(372, 410, 5, 5, INK, w=0)
    p.ell(398, 410, 5, 5, INK, w=0)


def scene2(p, t, T):
    sw = SWITCH_T - SCENES[1][0]
    if t < 2.6:
        # zbliżenie: ręka drży, klucz za pierwszym razem się zacina i odskakuje, za drugim przekręca
        p.rect(0, 0, W, H, (112, 126, 112), w=0)
        p.rect(520, 140, 760, 600, (170, 160, 120))
        p.ell(640, 300, 46, 46, (60, 56, 48))
        p.ell(640, 480, 18, 30, (60, 56, 48))  # dziurka pod dłonią — dłoń ją zasłania
        ang = 0.35 * ease((t - 0.4) / 0.2) * (1 - ease((t - 0.75) / 0.12)) + ease((t - 1.35) / 0.5) * math.pi / 2
        ang += 0.03 * noise(t, 62, 8)
        ca, sa = math.cos(ang), math.sin(ang)
        tx, ty = 3 * noise(t, 61, 7), 3 * noise(t, 63, 6)

        def rot(px, py):
            return (640 + tx + px * ca - py * sa, 300 + ty + px * sa + py * ca)

        p.poly([rot(-8, -10), rot(8, -10), rot(8, 120), rot(-8, 120)], (196, 176, 96))
        p.ell(*rot(0, 160), 46, 40, (196, 176, 96), rot=ang)
        p.ell(*rot(0, 160), 14, 12, (112, 126, 112), rot=ang)
        # dłoń
        hx, hy = rot(0, 170)
        p.ell(hx + 40, hy + 50, 90, 70, SKIN)
        for i in range(4):
            p.line([(hx - 30 + i * 22, hy + 10), (hx - 10 + i * 22, hy - 40)], w=22, color=SKIN)
            p.line([(hx - 30 + i * 22, hy + 10), (hx - 10 + i * 22, hy - 40)], w=2.5)
        return
    room(p, dark=t >= sw)
    # sprawdza klamkę: dłoń na klamce, dwa razy w dół — drzwi tylko drgną, są zamknięte
    a, b = HANDLE
    grip = ease((t - a) / 0.25) * (1 - ease((t - b + 0.25) / 0.25))
    press = abs(math.sin(math.pi * (t - a - 0.25) / 0.35)) if a + 0.25 < t < a + 0.95 else 0.0
    rattle = 2 * press * noise(t, 66, 30)
    # drzwi z szybą po prawej
    p.rect(800 + rattle, 120, 1060 + rattle, 560, (104, 116, 104))
    p.rect(850 + rattle, 170, 1010 + rattle, 300, (180, 196, 170) if t < sw else (110, 140, 118), w=5)
    # biurko z telefonem
    p.rect(470, 420, 790, 450, (110, 84, 60))
    p.rect(490, 450, 520, 560, (96, 72, 52))
    p.rect(740, 450, 770, 560, (96, 72, 52))
    p.poly([(600, 420), (680, 420), (672, 392), (608, 392)], (206, 196, 168), w=3)
    # sanitariusz przy włączniku: dyszy po biegu, po zgaszeniu odwraca głowę do szyby i nasłuchuje
    x = 1120
    p.rect(1090, 290, 1130, 340, (220, 216, 200), w=3)
    on = t < sw
    p.rect(1104, 300 if on else 316, 1116, 314 if on else 330, (90, 90, 84), w=2)
    pant = math.sin(2 * math.pi * 0.9 * t) * (1 - 0.6 * ease((t - sw - 0.8) / 0.6))
    dy = -4 * pant
    turn = ease((t - sw - 0.5) / 0.4)
    p.poly([(x - 210, 560), (x - 120, 560), (x - 110, 330 + dy), (x - 220, 330 + dy)], UNI)
    hx = x - 165 - 8 * turn + 2 * noise(t, 64, 0.8)
    p.ell(hx, 280 + dy, 44, 50, SKIN)
    p.poly([(hx - 44, 282 + dy), (hx - 35, 240 + dy), (hx + 15, 226 + dy), (hx + 43, 250 + dy), (hx + 41, 280 + dy),
            (hx + 5, 262 + dy)], HAIR)
    if blink(t, 65, 2.2) < 0.5 or t > sw:
        p.ell(hx + 33 - 60 * turn, 282 + dy, 6, 6, INK, w=0)
    # klamka na drzwiach, dźwignia w stronę zawiasu
    droop = 16 * press
    p.rect(1030 + rattle, 346, 1046 + rattle, 392, (150, 150, 140), w=2.5)
    p.poly([(1038 + rattle, 356), (1038 + rattle, 368), (996 + rattle, 372 + droop), (996 + rattle, 362 + droop)], (170, 170, 160), w=2.5)
    reach = ease((t - sw + 0.6) / 0.5) * (1 - 0.7 * ease((t - sw - 0.3) / 0.5))
    hx2 = x - 60 + 40 * reach + (1010 - (x - 60)) * grip
    hy2 = 320 - 10 * reach + (367 + droop - 320) * grip
    p.line([(x - 120, 350 + dy), (hx2, hy2)], w=22, color=UNI)
    p.line([(x - 120, 350 + dy), (hx2, hy2)], w=3)
    p.ell(hx2, hy2, 14, 14, SKIN)


def walker_x(t, start, stop=None):
    """Pozycja sylwetki za szybą; stop=(a, b) — stoi w miejscu od a do b."""
    if stop:
        a, b = stop
        t = t if t < a else (a if t < b else t - (b - a))
    return 380 + ((t - start) * 150) % 700


def window_view(p, t, T, turn, walkers, stops=None):
    """Szyba w drzwiach dyżurki od środka: korytarz jasny, pokój ciemny. stops — {nr sylwetki: (od, do)} postoju;
    sylwetka 1 przy postoju powoli przekręca głowę. Zwraca pozycje sylwetek."""
    stops = stops or {}
    p.rect(0, 0, W, H, (40, 50, 60), w=0)
    p.rect(330, 60, 950, 760, (56, 66, 72))
    p.rect(420, 120, 860, 420, (172, 190, 160), w=0)
    xs = []
    for i, (start, sc) in enumerate(walkers):
        # zatrzymują się w chwili dzwonka; w scenie 3 niektórzy przystają na chwilę
        stop = stops.get(i)
        x = walker_x(t - turn if turn is not None else t, start, stop)
        xs.append(x)
        # chód: lekkie bujanie, nie sunięcie
        y = 460 - abs(math.sin((t - start) * 4.4)) * 6 * (turn is None) * (not (stop and stop[0] <= t < stop[1]))
        s = 0.9 * sc
        sil = (24, 28, 30)
        p.poly([(x - 44 * s, y - 180 * s), (x + 44 * s, y - 180 * s), (x + 50 * s, y + 40), (x - 50 * s, y + 40)], sil, w=3)
        # ten, który przystaje, powoli przekręca głowę w stronę szyby — ale nie do końca
        peek = 0.0
        if stop and i == 1:
            peek = ease((t - stop[0] - 0.3) / 0.6) * (1 - ease((t - stop[1] + 0.3) / 0.3))
        hx = x + (0 if turn is not None else 8 * s * (1 - peek))
        p.ell(hx, y - 222 * s, 36 * s, 42 * s, sil, w=3)
        if turn is not None:
            k = ease((turn - TURN_DELAY[i]) / 0.35)
            if k > 0:
                for side in (-1, 1):
                    p.ell(hx + side * 13 * s, y - 228 * s, 7 * s * k, 8 * s * k, (246, 248, 236), w=0)
        else:
            p.ell(hx + 22 * s * (1 - peek) + 10 * s * peek, y - 228 * s, 4 * s, 5 * s, (200, 204, 190), w=0)
    # wszystko poza szybą zasłaniają z powrotem ściana i drzwi
    for x0, y0, x1, y1 in ((-50, -50, 330, H + 50), (950, -50, W + 50, H + 50)):
        p.rect(x0, y0, x1, y1, (40, 50, 60), w=0)
    for x0, y0, x1, y1 in ((330, 120, 420, 420), (860, 120, 950, 420), (330, 60, 950, 120), (330, 420, 950, H + 50)):
        p.rect(x0, y0, x1, y1, (56, 66, 72), w=0)
    p.rect(330, -50, 950, 60, (40, 50, 60), w=0)
    p.line([(330, 60), (330, H + 20)], w=4)
    p.line([(950, 60), (950, H + 20)], w=4)
    p.line([(330, 60), (950, 60)], w=4)
    for i in range(1, 4):
        p.line([(420, 120 + i * 75), (860, 120 + i * 75)], w=1.5, color=(70, 80, 70), amp=0.5)
    p.rect(420, 120, 860, 420, None, w=7)
    return xs


def scene3(p, t, T):
    xs = window_view(p, t, T, None, WALKERS3, stops={1: PEEK, 0: LAST_STOP})
    # sanitariusz skulony pod szybą: oddycha, mruga, wodzi wzrokiem za nimi;
    # kiedy jeden przystaje — wstrzymuje oddech i nie mruga, potem wypuszcza powietrze
    held = ease((t - PEEK[0] - 0.1) / 0.3) * (1 - ease((t - PEEK[1]) / 0.3))
    exhale = max(0.0, 1 - abs(t - PEEK[1] - 0.4) / 0.4)
    br = math.sin(2 * math.pi * 0.55 * t) * (1 - held) - 6 * exhale / 4
    x, y = 300, 720
    dy = -4 * br
    p.poly([(x - 150, y), (x + 150, y), (x + 120, y - 190 + dy), (x - 110, y - 210 + dy)], (52, 64, 70))
    hx, hy = x + 10 + 2 * noise(t, 71, 0.7), y - 260 + dy
    p.ell(hx, hy, 74, 80, (130, 110, 96))
    p.poly([(hx - 76, hy - 2), (hx - 70, hy - 60), (hx - 10, hy - 84), (hx + 50, hy - 70), (hx + 74, hy - 10), (hx + 20, hy - 36)],
           (34, 28, 24))
    # wzrok: za tym, który jest najbliżej środka szyby
    target = min(xs, key=lambda v: abs(v - 640))
    look = max(-1.0, min(1.0, (target - 640) / 260)) + 0.08 * noise(t, 72, 5)
    bk = blink(t, 73, 2.0) * (1 - held)
    wide = 2 * held
    for side in (-1, 1):
        ex, ey = hx + 20 + side * 24, hy + 2
        if bk > 0.5:
            p.line([(ex - 11, ey), (ex + 11, ey)], w=3)
        else:
            p.ell(ex, ey, 11 + wide, 12 + wide, (226, 228, 216), w=3)
            p.ell(ex + 5 * look, ey - 4, 4, 4, INK, w=0)
    p.line([(hx + 8, hy + 38), (hx + 32, hy + 38)], w=3)
    # ręka zakrywająca usta drży
    p.ell(hx + 26 + 1.5 * noise(t, 74, 9), hy + 46 + 1.5 * noise(t, 75, 9), 34, 22, (130, 110, 96))
    # płacze z jednego oka: łza zbiera się w kąciku i spływa po policzku
    if t > TEAR:
        ex, ey = hx + 44, hy + 14
        drop = 34 * ease((t - TEAR - 0.4) / 1.8)
        if drop > 2:
            p.line([(ex, ey), (ex + 2, ey + drop)], w=2.5, color=(150, 175, 190), amp=0.4)
        r = 2 + 2 * ease((t - TEAR) / 0.4)
        p.ell(ex + 2, ey + drop, r, r * 1.3, (200, 226, 240), w=1.5)


def scene4(p, t, T):
    r0 = RING_T - SCENES[3][0]
    ring = t > r0 and (int((t - r0) * 3) % 2 == 0)
    j = 6 if ring else 0
    r = random.Random(int(t * FPS))
    p.rect(0, 0, W, H, (44, 54, 62), w=0)
    p.rect(-20, 480, W + 20, H + 20, (92, 70, 52))
    p.line([(0, 480), (W, 480)], w=5)
    # stary telefon
    bx, by = 640 + r.uniform(-j, j), 460 + r.uniform(-j, j)
    p.poly([(bx - 220, by + 40), (bx + 220, by + 40), (bx + 170, by - 120), (bx - 170, by - 120)], (196, 184, 150))
    p.ell(bx, by - 30, 92, 80, (172, 160, 128))
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.3
        p.ell(bx + math.cos(a) * 60, by - 30 + math.sin(a) * 52, 12, 11, (60, 56, 50), w=2)
    p.ell(bx, by - 30, 24, 22, (220, 210, 180), w=3)
    # widełki — widać je, kiedy słuchawka spadnie
    for side in (-1, 1):
        p.poly([(bx + side * 140, by - 118), (bx + side * 160, by - 118), (bx + side * 156, by - 150), (bx + side * 144, by - 150)],
               (172, 160, 128), w=3)
    # od drgań słuchawka zsuwa się z widełek i spada na stół, odbija się raz
    lift = 18 if ring and t < DROP else 0
    k = ease((t - DROP) / 0.12) * 0.15 + 0.85 * min(1.0, max(0.0, (t - DROP - 0.06) / 0.26)) ** 2
    bounce = 14 * max(0.0, math.sin(math.pi * (t - DROP - 0.32) / 0.16)) if DROP + 0.32 < t < DROP + 0.48 else 0.0
    cx = bx - 120 * k
    cy = (by - 172 - lift + r.uniform(-j, j)) * (1 - k) + (by + 78 - bounce) * k
    ang = -0.32 * k + 0.06 * bounce / 14

    def hs(px, py):
        return (cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang))

    p.poly([hs(-230, 22), hs(230, 22), hs(200, -22), hs(-200, -22)], (186, 174, 140))
    p.ell(*hs(-220, 18), 46, 34, (186, 174, 140), rot=ang)
    p.ell(*hs(220, 18), 46, 34, (186, 174, 140), rot=ang)
    ry = by - 150 - lift
    p.line([(bx + 220, by + 20), (bx + 300, by + 80), (bx + 420, by + 60), (bx + 560, by + 140)], w=6)
    if ring:
        for side in (-1, 1):
            for k in range(3):
                x0 = bx + side * (290 + k * 30)
                p.line([(x0, ry - 60 + k * 10), (x0 + side * 24, ry - 90 + k * 6)], w=5)
        p.ell(bx + 150, by - 70, 12, 12, (220, 40, 40), w=3)


def scene5(p, t, T):
    t0 = TURN_T - SCENES[4][0]
    window_view(p, t, T, t - t0 if t >= t0 else None, WALKERS5)


SCENE_FN = [scene1, scene2, scene3, scene4, scene5]
CAMERAS = [
    lambda t, T: dict(zoom=1.0),
    lambda t, T: dict(zoom=1.0 + 0.04 * t / T),
    lambda t, T: dict(zoom=1.0 + 0.08 * ease(t / T), cx=600, cy=380),
    lambda t, T: dict(zoom=1.05 + 0.1 * ease(t / T), cy=380),
    lambda t, T: dict(zoom=1.0 + 0.35 * ease((t - 1.6) / 2.2), cx=640, cy=290),
]
GRADE = [(0.9, 0.98, 0.92), (0.95, 0.98, 0.96), (0.86, 0.94, 0.98), (0.95, 0.96, 0.94), (0.86, 0.94, 0.98)]


def shake_at(t):
    amp = 0.0
    if STUMBLE - 0.1 <= t < STUMBLE + 0.25:
        amp = 6
    if RING_T <= t < SCENES[4][0]:
        amp = 3
    d = SCENES[4][0] + DARK
    if d <= t < d + 0.6:
        amp = 7
    return handheld(t, amp, seed=99)


def frame(t):
    for i, (a, b, _, vs, txt) in enumerate(SCENES):
        if a <= t < b or i == len(SCENES) - 1:
            break
    lt, T = t - a, b - a
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255))
    p = Pen(img, t, **framed(CAMERAS[i](lt, T), shake_at(t)))
    SCENE_FN[i](p, lt, T)
    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32) * np.array(GRADE[i], dtype=np.float32)
    raw = arr  # przed maską światła i migotaniem — z tego szukamy oczu, żeby żadne nie gasło przypadkiem
    if i == 1 and t >= SWITCH_T:
        arr = light_mask(arr, 930, 235, 420, 0.32) * np.array((0.8, 0.9, 1.05), dtype=np.float32)
    if i in (2, 4):
        flick = 1.0 if math.sin(t * 23) * math.sin(t * 5.1) > -0.5 else 0.8
        arr = light_mask(arr, 640, 270, 560, 0.35) * flick
    if i == 3:
        arr = light_mask(arr, 640, 420, 520, 0.4)
    if i == 4:
        dark = ease((lt - DARK) / 0.3)
        eyes = (raw.mean(axis=2, keepdims=True) > 200).astype(np.float32)
        arr = arr * (1 - dark) + raw * 0.85 * eyes * dark
    yy, xx = np.ogrid[:H, :W]
    vig = 1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
    arr *= np.clip(vig, 0.35, 1)[..., None]
    arr += np.random.default_rng(int(t * FPS) + 7).normal(0, 5, (H, W, 1))
    arr *= min(1.0, t / 0.25, max(0.0, (DUR - 0.1 - t) / 0.3))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    if vs - 0.05 <= t < min(b - 0.05, vs + VOICE_LEN[i] + 0.8) and t < DUR - 0.2:
        subtitle(img, txt)
    return img


def audio(path):
    sr = 44100
    n = int(DUR * sr)
    ts = np.arange(n) / sr
    rng = np.random.default_rng(11)
    out = np.zeros(n)
    out += 0.06 * np.sin(2 * np.pi * 49 * ts) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * ts))
    out += 0.035 * np.sin(2 * np.pi * 73.4 * ts + np.sin(ts * 1.3))

    def hit(t0, length, decay, amp, freq=None):
        i0 = int(t0 * sr)
        L = min(int(length * sr), n - i0)
        e = np.exp(-np.arange(L) / (decay * sr))
        sig = rng.normal(0, 1, L) * 0.6
        if freq:
            sig = sig + np.sin(2 * np.pi * freq * np.arange(L) / sr)
        out[i0:i0 + L] += amp * sig * e

    S = [sc[0] for sc in SCENES]
    # bieg: kroki nierówne, potknięcie, ciężki oddech, jęki za plecami
    for k in np.arange(0.1, S[1] - 0.1, 0.29):
        if abs(k - STUMBLE) > 0.12:
            hit(k + rng.uniform(-0.025, 0.025), 0.07, 0.012, rng.uniform(0.24, 0.34))
    hit(STUMBLE, 0.15, 0.03, 0.5, 70)
    for k in np.arange(0.3, S[1] - 0.2, 0.58):
        breath_snd(out, sr, rng, k, 0.28, 0.04, inhale=bool(int(k / 0.58) % 2))
    m = ts < S[1]
    out += 0.03 * sum(np.sin(2 * np.pi * f * ts + 2 * np.sin(ts * (0.9 + j))) for j, f in enumerate((105, 128))) * m
    # trzask drzwi, klucz się zacina, drugi raz przekręca, pstryk
    hit(S[1] + 0.05, 0.6, 0.08, 0.7, 50)
    hit(S[1] + 0.55, 0.06, 0.008, 0.2)
    hit(S[1] + 0.85, 0.08, 0.01, 0.25)
    hit(S[1] + 1.55, 0.1, 0.01, 0.35)
    hit(S[1] + 1.8, 0.1, 0.01, 0.35)
    for k in (0.42, 0.77):  # klamka w dół dwa razy, drzwi drgają w zamku
        hit(S[1] + HANDLE[0] + k, 0.12, 0.02, 0.3, 140)
    hit(SWITCH_T, 0.05, 0.004, 0.5)
    for k in np.arange(S[1] + 0.2, S[2] - 0.2, 0.62):  # dyszenie, po zgaszeniu cichnie
        quiet = 1.0 if k < SWITCH_T + 0.8 else 0.5
        breath_snd(out, sr, rng, k, 0.32, 0.05 * quiet, inhale=bool(int((k - S[1]) / 0.62) % 2))
    # szuranie za drzwiami; przy szybie: wstrzymany oddech, potem wydech
    sh = np.convolve(rng.normal(0, 1, n), np.ones(60) / 60, mode="same")
    peek = (ts > S[2] + PEEK[0]) & (ts < S[2] + PEEK[1])
    out += 0.5 * sh * ((ts > S[2]) & (ts < S[3])) * (0.5 + 0.5 * np.sin(ts * 7.0) ** 2) * np.where(peek, 0.25, 1.0)
    for k in np.arange(S[2] + 0.3, S[3] - 0.3, 1 / 0.55):
        if not (S[2] + PEEK[0] - 0.3 < k < S[2] + PEEK[1] + 0.2):
            breath_snd(out, sr, rng, k, 0.8, 0.03)
    breath_snd(out, sr, rng, S[2] + PEEK[1] + 0.1, 0.8, 0.07, inhale=False)
    # chwila zupełnej ciszy, potem dzwonek: 2 tony z drganiem, rytm 1/3 s; urywa się, gdy już patrzą
    out[int(S[3] * sr):int(RING_T * sr)] *= 0.25
    ring = (np.sin(2 * np.pi * 1180 * ts) + np.sin(2 * np.pi * 1420 * ts)) * (np.sin(2 * np.pi * 20 * ts) > 0)
    gate = (ts > RING_T) & (ts < RING_END) & ((((ts - RING_T) * 3).astype(int) % 2) == 0)
    out += 0.07 * ring * gate
    hit(S[3] + DROP + 0.32, 0.35, 0.05, 0.6, 160)  # słuchawka uderza o stół
    hit(S[3] + DROP + 0.48, 0.2, 0.03, 0.3, 190)
    d = S[4] + DARK
    out[int(RING_END * sr):int(d * sr)] *= 0.3
    hit(d, 1.0, 0.25, 0.6, 38)
    hit(d + 0.9, 0.4, 0.15, 0.8, 36)
    out[int((DUR - 0.2) * sr):] *= 0.0
    for _, _, fn, vs, _ in SCENES:
        with wave.open(str(VOICE_DIR / fn)) as w:
            v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        i0 = int(vs * sr)
        v = v[: n - i0]
        out[i0:i0 + len(v)] += 0.95 * v
    out = np.tanh(out * 1.1) * 0.85
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


def main(stills=None):
    if stills:
        for t in stills:
            frame(t).save(HERE / f"cz2-klatka{SUFFIX}-{t:05.2f}s.png")
        return
    wav = HERE / f"audio2{SUFFIX}.wav"
    audio(wav)
    out = HERE / f"zombie-psychiatryk-2{SUFFIX}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        proc.stdin.write(frame(k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(out)


if __name__ == "__main__":
    import sys
    main([float(a) for a in sys.argv[1:]] or None)
