"""Wariant A · dzień 23 „Zosia” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 23
talk = K.talk
ZS = K.WHO["zosia"]
DARK_HALL = ((0.8, 0.88, 1.0), (640, 380, 520, 0.18))  # wieża bez prądu: tylko krąg latarki


def forearm(p, streak=1.0):
    K.limb(p, (-80, 620), (900, 360), 190, ZS["skin"], outline=4)
    p.ell(960, 340, 130, 100, ZS["skin"])  # dłoń
    p.line([(990, 300), (1050, 380)], w=8, color=(170, 50, 50))  # rana
    p.ell(1020, 340, 70, 50, None, w=3, color=(210, 90, 80))
    if streak:  # czerwona smuga w górę przedramienia
        pts = [(980, 350), (820, 400), (640, 450), (440, 500), (240, 540)]
        n = max(2, int(len(pts) * streak + 0.999))
        p.line(pts[:n], w=16, color=(210, 80, 80))
    K.limb(p, (-80, 760), (180, 560), 220, ZS["sleeve"], outline=4)  # rękaw mundurka


def s_streak(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    forearm(p, streak=ease(t / (T * 0.8)))


def zosia_talk(p, t, T, gaze, fear=0.3):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=gaze, mouth=talk(t, T), fear=fear)


def s_not_bite(p, t, T):
    zosia_talk(p, t, T, (0.0, 0.5), 0.25)


def s_soldiers(p, t, T):
    zosia_talk(p, t, T, (-0.5, 0.0), 0.4)


def s_shelf(p, t, T):
    p.rect(0, 0, W, H, (60, 58, 50), w=0)  # półka apteki w piwnicy, latarka
    for y in (200, 420, 640):
        p.rect(-20, y, W + 20, y + 24, (128, 98, 70))
    for i in range(9):  # puste miejsca po pudełkach: jaśniejsze ślady w kurzu
        p.rect(80 + i * 130, 120, 170 + i * 130, 200, (84, 80, 70), w=2)
    p.rect(560, 330, 700, 420, (236, 236, 232), w=3)  # samotny paracetamol
    p.text(630, 375, "PARACETAMOL", 16)
    p.glow([(380, 80), (900, 80), (980, 600), (300, 600)], (255, 240, 200, 40))


def s_where(p, t, T):
    zosia_talk(p, t, T, (0.3, -0.4), 0.3)


def s_key(p, t, T):
    p.rect(0, 0, W, H, (190, 186, 170), w=0)
    K.limb(p, (W + 80, H + 40), (760, 470), 150, K.narr_sleeve(), outline=4)
    p.ell(640, 440, 190, 120, K.SKIN)  # otwarta dłoń narratora
    k = ease(t / (T * 0.5))
    kx, ky = 640, 200 + 230 * k  # klucz spada w dłoń
    p.ell(kx - 60, ky, 26, 26, (200, 180, 90), w=4)
    p.line([(kx - 34, ky), (kx + 60, ky)], w=8, color=(200, 180, 90))
    p.line([(kx + 40, ky), (kx + 40, ky + 20)], w=6, color=(200, 180, 90))
    if k > 0.6:
        K.paper(p, 420, 480, ["CHIRURGIA", "SZAFA 2"], w=260, h=180)
        p.rect(500, 540, 520, 590, (230, 230, 240), w=2)  # narysowana fiolka
    K.limb(p, (-80, -60), (420, 230 + 100 * k), 110, ZS["sleeve"], outline=4)  # ręka Zosi
    p.ell(450, 250 + 100 * k, 50, 36, ZS["skin"])


def s_alone(p, t, T):
    K.staff_room(p, t, night=True)
    K.irena_lying(p, t, x=700, fever=0.8)
    K.sitting(p, 230, 720, 0.85, t, "kuba", gaze=(0.6, 0.0))
    K.figure(p, 1040, 780, 1.0, t, "narrator", look=-0.6, arms={"r": (40, 60)})
    p.glow([(1100, 520), (1100, 560), (1280, 700), (1280, 400)], (255, 240, 200, 60))  # latarka w dłoni


def s_breathe(p, t, T):
    K.staff_room(p, t, night=True)
    br = math.sin(t * 2 * math.pi / 4.0)  # oddychają w jednym rytmie
    R.nurse_face(p, 420, 360, 0.8, 0.5 - 0.3 * ease(t / T), t, gaze=(0.6, 0.0), breath=br * 2)
    K.face_cu(p, 900, 340, 0.8, "henryk", t, gaze=(-0.6, 0.0), breath=br * 2)
    K.limb(p, (980, H + 40), (520, 560 + 6 * br), 70, K.WHO["henryk"]["top"], outline=4)  # dłoń na piersi narratora
    p.ell(510, 556 + 6 * br, 46, 34, K.WHO["henryk"]["skin"])


def hand_in_window(q, x, y, s, t, seed):
    dx = 20 * math.sin(t * 0.8 + seed) * s
    q.ell(x + dx, y, 16 * s, 22 * s, K.ZSKIN, w=2)
    for k in range(4):
        q.line([(x + dx - 9 * s + k * 6 * s, y - 16 * s), (x + dx - 9 * s + k * 6 * s, y - 34 * s)], w=3 * s, color=K.ZSKIN)


def s_hall(p, t, T):
    R.corridor(p, t, 0.0)
    for k, f in enumerate((0.28, 0.55, 0.78)):  # dłonie suną po szybkach drzwi sal (geometria z render.corridor)
        ff = f + 0.04
        top, bot = 250 * ff, H + (410 - H) * ff
        y = top + (bot - top) * 0.38 + 16 * (1 - f)
        for side, x in ((-1, 520 * ff), (1, W + (760 - W) * ff)):
            hand_in_window(p, x, y, 1.6 * (1 - f) + 0.3, t, k * 2 + side)


def s_ajar(p, t, T):
    """Drzwi sali chirurgii (bez numeru izolatki): uszkodzony zamek puszcza, skrzydło uchyla się na zawiasach w lewo."""
    wall, door = (70, 78, 74), (110, 120, 116)
    p.rect(0, 0, W, H, wall, w=0)
    p.rect(-20, 600, W + 20, H + 20, (50, 56, 54))
    p.rect(440, 70, 840, 620, (6, 6, 8))  # wnętrze sali: ciemność
    k = 0.18 * ease((t - 0.4) / (T * 0.6))
    x0 = 440 + 400 * k  # lewa krawędź skrzydła odsuwa się od framugi
    p.poly([(x0, 70 - 20 * k), (840, 70), (840, 620), (x0, 620 + 20 * k)], door)
    wx0 = x0 + (840 - x0) * 0.3
    p.rect(wx0, 150, wx0 + (840 - x0) * 0.4, 300, (30, 34, 34), w=4)  # okienko w skrzydle
    p.rect(x0 + 16, 340, x0 + 36, 400, (150, 150, 140), w=2)  # klamka z wyłamanym zamkiem
    p.line([(x0 + 26, 400), (x0 + 30, 418)], w=3)
    p.rect(430, 60, 850, 630, None, w=8)  # framuga
    if k > 0.05:
        for i in range(3):  # skrzyp
            p.line([(380 - i * 26, 300 + i * 18), (350 - i * 26, 296 + i * 18)], w=3, color=(150, 150, 150))


def slit(p, t, eye_x, eye_r, shade=1.0):
    p.rect(0, 0, W, H, (70, 78, 74), w=0)
    p.rect(560, -20, 720, H + 20, (6, 6, 8))  # szczelina drzwi
    if eye_r > 2:
        p.ell(eye_x, 330, eye_r * 1.6, eye_r, tuple(int(c * shade) for c in (236, 238, 226)), w=3)
        p.ell(eye_x, 330, eye_r * 0.25, eye_r * 0.25, tuple(int(c * shade) for c in (200, 204, 196)), w=0)  # bielmo
    p.rect(400, -20, 560, H + 20, (110, 120, 116), w=4)  # skrzydło drzwi
    p.rect(720, -20, 900, H + 20, (70, 78, 74), w=0, amp=0)


def s_eye(p, t, T):
    slit(p, t, 640, 50)


def s_freeze(p, t, T):
    p.rect(0, 0, W, H, (40, 44, 46), w=0)
    br = math.sin(t * 2 * math.pi / 5.0)  # oddech bardzo wolny
    R.nurse_face(p, 640, 330, 1.0, 0.75, t, gaze=(0.8, 0.0), blink_k=0.0, breath=br * 2)


def s_eye_back(p, t, T):
    k = ease(t / T)
    slit(p, t, 640, 50 * (1 - 0.7 * k), shade=1 - 0.8 * k)


def s_cabinet(p, t, T):
    p.rect(0, 0, W, H, (150, 160, 158), w=0)
    p.rect(320, 60, 960, 640, (220, 226, 226), w=5)  # szafa z szybą
    for y in (220, 380, 540):
        p.line([(320, y), (960, y)], w=4)
    for i in range(8):
        p.rect(370 + i * 70, 290, 400 + i * 70, 375, (230, 230, 240), w=2)
    k = ease(t / T)
    gone = int(3 * k)
    for i in range(3 - gone):  # antybiotyk i dwie fiolki morfiny znikają z półki
        p.rect(380 + i * 80, 460, 420 + i * 80, 535, (240, 220, 200) if i else (200, 230, 210), w=2)
    K.limb(p, (W + 80, H + 60), (520, 480), 90, K.narr_sleeve(), outline=4)
    p.ell(500, 480, 46, 34, K.SKIN)


def s_torch(p, t, T):
    p.rect(0, 0, W, H, (20, 22, 24), w=0)
    p.rect(-20, 420, W + 20, H + 20, (40, 42, 44))
    x = 300 + 500 * ease(t / T)
    a = t * 9
    p.rect(x - 70, 470, x + 70, 520, (60, 60, 64), w=3)
    p.glow([(x, 495), (x + 600 * math.cos(a), 495 + 200 * math.sin(a)), (x + 600 * math.cos(a + 0.4), 495 + 200 * math.sin(a + 0.4))],
           (255, 240, 200, 80))  # snop latarki wiruje po ścianach


def s_three(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 28), w=0)
    p.rect(-20, 560, W + 20, H + 20, (36, 38, 40))
    k = ease(t / 0.3)
    p.rect(440, 80, 840, 600, (8, 8, 10))
    p.poly([(440, 80), (440 - 200 * k, 40), (440 - 200 * k, 640), (440, 600)], (110, 120, 116), w=4)  # drzwi na oścież
    for i, x in enumerate((540, 640, 740)):
        R.zombie(p, x + 20 * math.sin(t + i), 620 + 30 * ease((t - i * 0.2) / T), 1.0 + 0.15 * i, t, 120 + i)


def s_stairs(p, t, T):
    """Zbiega po ciemku z fiolkami w dłoni, ręką po poręczy; w ciemności chybia stopnia i pada na kolano
    (stąd krew na kolanie w następnym ujęciu)."""
    K.stair_flight(p, t, top="okno", sky=(46, 44, 62), dark=0.65)
    x, a = -0.72, 10  # wbiega w kadr z wyższych stopni; pada blisko kamery (plan średni)
    moves = K.st_moves(a, 0)
    tf = T * 0.62
    k = K.st_clock(min(t, tf), len(moves), 0.17)
    feet, swing = K.st_pose(moves, k, a)
    if t < tf or int(k) >= len(moves):
        h = K.st_person(p, t, feet, swing, x, "narrator", rail=True, look=0.2, eyes=1.0, arms={"r": (36, 70)})
    else:  # stopa w powietrzu nie trafia w stopień: kolano uderza w stopień, na który leciała
        f, _, L1 = moves[int(k)]
        feet = {**feet, f: K.st_level(L1)}
        u = ease((t - tf) / 0.16)
        h = K.st_person(p, t, feet, None, x, "narrator", kneel=f, drop=u, blood=ease((t - tf - 0.12) / 0.2),
                        rail=True, eyes=1.0, mouth=0.5 * u, gaze=(0.3 * u, 0.9 * u),  # łapie poręcz, patrzy na kolano
                        arms={"r": (36 - 70 * u, 70 - 40 * u)})  # fiolki przyciska do piersi
    s = h["s"]
    hx, hy = h["r"]
    for i in range(3):  # fiolki w zaciśniętej dłoni
        p.rect(hx - 10 * s + i * 8 * s, hy - 26 * s, hx - 5 * s + i * 8 * s, hy - 6 * s, (240, 220, 200), w=1.5)


def s_burst(p, t, T):
    K.staff_room(p, t, night=True)
    K.irena_lying(p, t, x=700, fever=0.8)
    k = ease(t / 0.4)
    x = 1200 - 300 * k
    K.figure(p, x, 780, 1.05, t * 1.5, "narrator", walk=t * 1.5, look=-0.5, arms={"r": (60, -40), "l": (-40, 120)}, eyes=1.0)
    p.rect(x - 34, 680, x - 4, 700, (180, 40, 40), w=0)  # krew na kolanie
    for i in range(3):
        p.rect(x + 100 + i * 14, 430, x + 108 + i * 14, 470, (240, 220, 200), w=2)  # fiolki w dłoni
    K.sitting(p, 230, 720, 0.85, t, "kuba", gaze=(0.8, 0.0))


def s_door(p, t, T):
    p.rect(0, 0, W, H, (70, 72, 74), w=0)  # drzwi pokoju socjalnego od środka
    p.rect(-20, 600, W + 20, H + 20, (50, 52, 54))
    p.rect(440, 80, 840, 590, (110, 100, 90))
    p.rect(780, 330, 810, 350, (170, 170, 160), w=2)
    p.rect(440, 590, 840, 604, (200, 200, 170), w=0)  # światło z korytarza w szparze pod drzwiami
    for i in range(3):  # cienie stóp przesuwają się w szparze
        x = 480 + ((t * (40 + 15 * i) + i * 130) % 320)
        p.rect(x, 590, x + 34, 604, (20, 20, 22), w=0)
    if int(t * 3) % 2 == 0:  # szuranie
        for i in range(3):
            p.line([(880 + i * 26, 560 - i * 14), (910 + i * 26, 552 - i * 14)], w=3, color=(150, 150, 150))


FNS = [B.card("DZIEŃ 23"), s_streak, s_not_bite, s_soldiers, s_shelf, s_where, s_key, s_alone, s_breathe, s_hall, s_ajar, s_eye,
       s_freeze, s_eye_back, s_cabinet, s_torch, s_three, s_stairs, s_burst, s_door]
LOOK = [None] + [B.WARD] * 3 + [B.BASE] + [B.WARD] * 2 + [B.NIGHT] * 2 + [DARK_HALL] * 6 + [B.NIGHT] * 2 + [B.DARK] + [B.NIGHT] * 2
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
