"""Wariant A · dzień 14 „Prąd” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import random
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 14


def talk(t, T, a=0.2, b=0.3):
    return 0.5 + 0.5 * math.sin(t * 11) if a < t < T - b else 0.0


def s_lever(p, t, T):
    p.rect(0, 0, W, H, (130, 130, 126), w=0)
    p.rect(420, 120, 860, 620, (100, 100, 96), w=4)
    p.rect(580, 220, 700, 520, (40, 40, 40), w=4)
    a = ease(t / 0.4) * math.pi / 2  # dźwignia w dół
    cx, cy = 640, 300
    p.line([(cx, cy), (cx + 110 * math.cos(-math.pi / 2 + a), cy + 110 * math.sin(-math.pi / 2 + a) + 120)], w=26, color=(200, 60, 50))
    K.limb(p, (1300, 760), (cx + 100 * math.cos(-math.pi / 2 + a) + 60, cy + 120 + 100 * math.sin(-math.pi / 2 + a)), 140, K.narr_sleeve(), outline=4)
    if t > 0.4:
        p.rect(800, 160, 830, 190, (120, 240, 120), w=2)  # kontrolka


def s_roar(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=t > 0.5)


def s_lights_on(p, t, T):
    on = [1 if t > d else 0 for d in (0.3, 0.6, 0.9, 1.2)]  # świetlówki zapalają się jedna po drugiej
    R.corridor(p, t, on, doors_open=0.0)


def s_lock(p, t, T):
    p.rect(0, 0, W, H, (124, 138, 122), w=0)
    p.rect(300, 200, 980, 520, (150, 150, 140), w=4)  # rygiel elektromagnetyczny
    k = ease(t / 0.15)
    p.rect(560 + 260 * (1 - k), 300, 760 + 260 * (1 - k), 420, (90, 94, 96), w=4)
    if 0.1 < t < 0.4:
        for i in range(5):
            a = i * 1.2
            p.line([(760 + 80 * math.cos(a), 360 + 80 * math.sin(a)), (760 + 140 * math.cos(a), 360 + 140 * math.sin(a))], w=4)


def s_banging(p, t, T):
    p.rect(0, 0, W, H, (124, 138, 122), w=0)
    p.rect(300, 60, 980, 720, (110, 124, 108))
    p.rect(520, 160, 760, 360, (40, 46, 44), w=5)  # okienko w drzwiach sali
    for i in range(4):  # dłonie walą w szybę, każda w swoim rytmie
        hit = (t * (2.2 + i * 0.4) + i * 0.3) % 1.0 < 0.3
        x, y = 560 + i * 55, 220 + (i % 2) * 70
        p.ell(x, y + (6 if hit else 0), 26, 32, K.ZSKIN, w=2)
    for x0, y0, x1, y1 in ((300, 60, 980, 160), (300, 360, 980, 720), (300, 160, 520, 360), (760, 160, 980, 360)):
        p.rect(x0, y0, x1, y1, (110, 124, 108), w=0, amp=0)
    p.rect(520, 160, 760, 360, None, w=5)


def s_alarm(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    on = int(t * 5) % 2 == 0
    p.rect(580, 60, 700, 120, (200, 60, 50), w=3)  # głośnik / sygnalizator
    if on:
        p.glow([(500, 40), (780, 40), (900, 360), (380, 360)], (255, 80, 60, 50))
        for k in range(3):
            p.ell(640, 140, 80 + 50 * k, 30 + 20 * k, None, w=3, color=(240, 200, 200))


def s_nowak_shouts(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    K.face_cu(p, 640, 340, 1.0, "nowak", t, gaze=(-0.4, 0.0), mouth=0.6 + 0.4 * talk(t, T), fear=0.8)


def s_run_in(p, t, T):
    K.cellar(p, t, flick=1.0)
    k = t / T  # trzech biegnie z pralni prosto na kamerę
    for i, dl in enumerate((0.0, 0.15, 0.3)):
        f = max(0.0, k - dl)
        R.zombie(p, 560 + 80 * i, 440 + 300 * f, 0.35 + 0.6 * f, t * 2 + i, 160 + i, tilt=0.1 * (i - 1))


def s_henryk_door(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    k = t / T  # zarażeni mijają go w głębi — idą na agregat (dalej od kamery = rysowani wcześniej)
    for i in range(3):
        f = max(0.0, k - i * 0.15)
        R.zombie(p, 120 + 560 * f, 640 - 30 * i, 0.7, t * 2 + i, 160 + i)
    K.figure_back(p, 300, 780, 1.1, t, "henryk", arms={"l": (-80, 30), "r": (80, 30)})


def s_barrel(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    k = t / T
    x = 1000 - 700 * k  # beczka toczy się z hukiem
    p.ell(x, 520, 60, 60, (150, 60, 40), rot=k * 12)
    p.line([(x - 50 * math.cos(k * 12), 520 - 50 * math.sin(k * 12)), (x + 50 * math.cos(k * 12), 520 + 50 * math.sin(k * 12))], w=4)
    K.figure(p, 1120, 780, 1.0, t, "kuba", look=-0.6, arms={"r": (-120 * (1 - k), 40)})


def s_shelf(p, t, T):
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    a = ease(t / 0.5) * 1.2  # regał przewraca się w poprzek przejścia
    bx, by = 640, 600
    pts = [(bx - 40, by), (bx + 40, by)]
    top = (bx + 300 * math.sin(a), by - 300 * math.cos(a))
    p.poly([(bx - 40, by), (bx + 40, by), (top[0] + 40, top[1]), (top[0] - 40, top[1])], (150, 110, 70), w=4)
    K.figure(p, 380, 780, 1.0, t, "narrator", look=0.6, lean=0.4, arms={"r": (120, -20)})
    K.figure(p, 520, 780, 1.0, t, "nowak", look=0.6, lean=0.4, arms={"r": (120, -10)})
    if 0.45 < t < 0.6:
        for k in range(6):
            p.line([(top[0] + 60 * math.cos(k), top[1] + 40 * math.sin(k)), (top[0] + 110 * math.cos(k), top[1] + 70 * math.sin(k))], w=4)


def s_pull(p, t, T):
    """Henryk w drzwiach na lewej ścianie wciąga ich do środka: otwór drzwi (ciemno), w nim Henryk, ściana z framugą
    wokół otworu. Narrator i Nowak idą wzdłuż ściany — przed nią — aż narrator stanie na wprost otworu; dopiero wtedy
    cofa się w drzwi i chowa za framugę. Ręka Henryka wychodzi z drzwi przed framugą: ponagla, potem chwyta rękaw
    narratora (przegląd 13.11.2026: framuga przecinała ich w pół kroku, ręka szła przez twarz Nowaka)."""
    K.tech_room(p, t, tarp=0.0, running=1.0, lights=True)
    k = ease(t / (T * 0.78))
    step = ease((t - T * 0.72) / (T * 0.28))  # na wprost otworu: krok w głąb drzwi
    wall = (120, 124, 120)
    x0, x1 = 40, 250  # otwór drzwi w ścianie po lewej
    p.rect(-20, 0, x0, H, wall)
    p.rect(x0, 0, x1, 130, wall)
    p.rect(x0, 130, x1, H + 20, (40, 42, 44))  # w drzwiach ciemno
    hs, hx_, hy_ = 0.97, 92, 752
    K.figure(p, hx_, hy_, hs, t, "henryk", look=0.7, arms={"r": (10, 40)})  # ręka sięgająca — na końcu, przed framugą
    nx, ny, ns = 150 + 410 * (1 - k), 780 - 26 * step, 1.0 - 0.06 * step
    wx = nx + 190  # Nowak tuż za nim, wciąż w sali
    walk_n = t * 1.5 if k < 1 else None
    if step > 0:  # narrator w drzwiach: za framugą
        K.figure(p, nx, ny, ns, t * 1.5, "narrator", walk=walk_n, look=-0.7)
    p.rect(x1, 0, x1 + 26, H + 20, wall)  # framuga po stronie sali
    p.line([(x1 + 26, 0), (x1 + 26, H + 20)], w=4)
    p.rect(x0 - 6, 124, x1 + 26, 136, wall)
    K.figure(p, wx, 780, 1.0, t * 1.5 + 0.3, "nowak", walk=t * 1.5 + 0.3 if k < 1 else None, look=-0.7)
    if step <= 0:  # narrator jeszcze w sali, przed ścianą
        K.figure(p, nx, ny, ns, t * 1.5, "narrator", walk=walk_n, look=-0.7)
    c = K.WHO["henryk"]
    sh = (hx_ + 50 * hs, hy_ - 268 * hs)  # prawy bark Henryka
    sleeve = (nx - 44 * ns, ny - 268 * ns + 60 * ns)  # rękaw narratora nad łokciem (bliżej drzwi)
    grab = ((sleeve[0] - sh[0]) / hs, (sleeve[1] - sh[1]) / hs)
    wave = (80, 10 + 30 * math.sin(t * 9))  # najpierw ponagla ręką, chwyta, gdy narrator jest blisko
    g = max(0.0, min(1.0, (330 - nx) / 120))
    reach = (wave[0] + (grab[0] - wave[0]) * g, wave[1] + (grab[1] - wave[1]) * g)
    hand = (sh[0] + reach[0] * hs, sh[1] + reach[1] * hs)
    K.limb(p, sh, hand, 24 * hs, c["sleeve"])
    p.ell(hand[0], hand[1], 13 * hs, 13 * hs, c["skin"])


def s_radio(p, t, T):
    p.rect(0, 0, W, H, (150, 156, 150), w=0)
    K.limb(p, (W + 100, H + 100), (700, 470), 140, K.narr_sleeve(), outline=4)
    p.ell(660, 450, 80, 60, K.SKIN)
    p.rect(590, 230, 690, 470, (40, 42, 46), w=4)
    p.line([(670, 230), (670, 120)], w=10)
    p.rect(610, 260, 670, 300, (120, 220, 120) if int(t * 6) % 2 == 0 else (60, 90, 60), w=2)
    if int(t * 5) % 2 == 0:  # w tle wciąż wyje alarm
        p.glow([(0, 0), (W, 0), (W, 160), (0, 160)], (255, 80, 60, 30))


def s_run_alone(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    k = t / T
    K.figure_back(p, 640, 820 - 260 * k, 1.1 - 0.5 * k, t * 1.8, "narrator", walk=t * 1.8)
    if int(t * 5) % 2 == 0:
        p.glow([(0, 0), (W, 0), (W, 160), (0, 160)], (255, 80, 60, 30))


def s_ground_floor(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    for i in range(14):  # każda plama na podłodze w ostrym świetle
        r = random.Random(i)
        x, y = r.uniform(200, 1080), r.uniform(480, 700)
        p.ell(x, y, r.uniform(10, 40), r.uniform(5, 14), (80, 90, 80), w=0)
    k = ease(t / T)
    for i in range(3):  # krwawe ślady stóp prowadzą do portierni
        p.ell(500 + i * 80 + 60 * k, 640 - i * 40, 20, 10, (120, 50, 40), w=0)


def s_wires(p, t, T):
    rip = ease((t - 0.3) / 0.25)
    K.porter_lodge(p, t, wires=1 - rip)
    K.limb(p, (1300, 760), (900, 520 + 60 * rip), 130, K.narr_sleeve(), outline=4)
    p.ell(880, 510 + 60 * rip, 70, 50, K.SKIN)
    if t < 0.3 + 0.25 and int(t * 5) % 2 == 0:
        p.glow([(0, 0), (W, 0), (W, 160), (0, 160)], (255, 80, 60, 30))


def s_silence(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    for side, x in ((-1, 220), (1, 1060)):  # tylko walenie w drzwi zamkniętych sal
        if (t * 1.7 + (side > 0) * 0.4) % 1.0 < 0.2:
            for k in range(3):
                p.line([(x, 380 + k * 40), (x - side * 40, 370 + k * 40)], w=3)


def s_pass(p, t, T):
    p.rect(0, 0, W, H, (120, 122, 112), w=0)
    for i in range(30):  # kurz na podłodze portierni
        r = random.Random(i)
        p.ell(r.uniform(0, W), r.uniform(0, H), 3, 2, (150, 150, 140), w=0)
    p.poly([(420, 260), (860, 240), (880, 520), (440, 540)], (236, 232, 214), w=4)
    p.rect(470, 300, 590, 440, (190, 200, 210), w=2)
    p.text(720, 330, "dr J. NOWAK", 30)
    p.text(720, 390, "lekarz", 22)
    k = ease((t - 0.3) / 0.6)  # dłoń zdmuchuje / ściera kurz
    for i in range(10):
        r = random.Random(100 + i)
        p.ell(r.uniform(460, 840) + 200 * k, r.uniform(280, 500), 3, 2, (190, 190, 180), w=0)
    K.limb(p, (1300, 800), (900 - 100 * k, 520), 120, K.narr_sleeve(), outline=4)


def s_alive(p, t, T):
    K.pharmacy_inside(p, t)
    k = ease((t - 0.2) / 0.6)  # Kuba podnosi rozciętą dłoń
    h = K.figure(p, 640, 760, 1.05, t, "kuba", look=0.0, gaze=(0.3, -0.4), arms={"r": (40, 95 - 150 * k)})
    p.line([(h["r"][0] - 10, h["r"][1] - 6), (h["r"][0] + 12, h["r"][1] + 8)], w=4, color=(170, 40, 40))
    K.figure(p, 380, 760, 1.0, t, "zosia", look=0.6)
    K.figure(p, 900, 760, 1.0, t, "irena", look=-0.6)


def s_bright(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1], doors_open=0.0)
    for k, y in enumerate((424, 470, 560)):  # odbicia świetlówek w podłodze — stałe; najazd robi kamera
        p.ell(640, y, 14 + 22 * k, 3 + 3 * k, (214, 222, 200), w=0)


FNS = [B.card("DZIEŃ 14"), s_lever, s_roar, s_lights_on, s_lock, s_banging, s_alarm, s_nowak_shouts, s_run_in,
       s_henryk_door, s_barrel, s_shelf, s_pull, s_radio, s_run_alone, s_ground_floor, s_wires, s_silence, s_pass,
       s_alive, s_bright]
LOOK = [None] + [B.BASE] * 20
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
