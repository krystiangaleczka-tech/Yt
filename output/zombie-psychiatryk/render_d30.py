"""Wariant A · dzień 30 „Świt” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE).

Ostatnie ujęcie wraca do kadru pierwszego ujęcia filmu (render.scene1): najpierw okno sali 8 z bliska — sylwetka
podchodzi, przekrzywia głowę i odskakuje — potem odjazd do pełnego planu, nad lasem wschodzi słońce.
"""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 30
talk = K.talk
HK = K.WHO["henryk"]
WX, WY = R.WINDOW[0] + 20, R.WINDOW[1] + 23  # środek okna sali 8 w kadrze pierwszego ujęcia


def alarm_pulse(p, t, k=1.0):
    """Czerwone błyski alarmu pożarowego na całym kadrze."""
    f = 0.5 + 0.5 * math.sin(t * 9)
    p.glow([(-20, -20), (W + 20, -20), (W + 20, H + 20), (-20, H + 20)], (255, 40, 30, int(40 * f * k)))


def s_chord(p, t, T):
    K.piano_room(p, t, wire=1.0)
    down = 1.0 if t > 0.4 else 0.0  # dłonie uderzają w klawisze
    K.figure_back(p, 640, 840, 1.05, t, "henryk", arms={"l": (-30, -26 + 14 * down), "r": (30, -26 + 14 * down)})
    if down:
        alarm_pulse(p, t)
        for k in range(4):
            a = -1.2 + k * 0.5
            p.line([(1000 + 60 * math.cos(a), 160 + 60 * math.sin(a)), (1000 + 110 * math.cos(a), 160 + 110 * math.sin(a))], w=6,
                   color=(220, 60, 50))


def s_keys(p, t, T):
    p.rect(0, 0, W, H, (70, 52, 40), w=0)
    p.rect(-20, 300, W + 20, 620, (236, 232, 216))
    for i in range(1, 16):
        p.line([(i * 85, 300), (i * 85, 620)], w=3)
    for i in (1, 2, 4, 5, 6, 8, 9, 11, 12, 13):
        p.rect(i * 85 - 22, 300, i * 85 + 22, 480, (30, 28, 26))
    p.rect(1020, 480, 1105, 620, (180, 170, 150), w=3)  # klawisz bez nakładki — nie ma go w kołysance
    note = int(t * 2.4) % 5  # kołysanka: pięć nut
    for side, base in ((-1, 380), (1, 640)):
        x = base + note * 50 * (1 if side > 0 else 0.6)
        K.limb(p, (base + side * 300, -60), (x, 420), 90, K.SHIRT, outline=4)
        p.ell(x, 440, 60, 40, HK["skin"])
        p.line([(x - 10, 470), (x - 12, 520)], w=14, color=HK["skin"])
    alarm_pulse(p, t, 0.8 if (t * 2.4) % 1 < 0.4 else 0.3)  # każdy klawisz włącza alarm na nowo


def yard_dawn(q, t, dawn=0.3, lights=1.0, crowd=True, turn=0.0, walk=0.0):
    K.yard_view(q, t, night=True, dawn=dawn, gate_lights=lights)
    if crowd:
        K.crowd(q, t, n=46, seed=29, turn=turn, area=(60, 1220, 320, 700), walk=walk, toward=(640, 300))


def s_turn(p, t, T):
    yard_dawn(p, t, dawn=0.2, turn=ease(t / (T * 0.7)) * 1.4)


def s_pour(p, t, T):
    R.corridor(p, t, [1, 1, 1, 1])
    for i in range(9):  # wlewają się korytarzem w stronę świetlicy
        k = (t / T * 0.8 + i * 0.11) % 1.0
        K.zombie_back(p, 520 + (i % 3) * 120, 900 - 520 * k, 1.3 - 1.0 * k, t + i, 200 + i, walk=t * 1.5 + i)
    alarm_pulse(p, t, 0.6)


def s_side_door(p, t, T):
    k = ease((t - 0.4) / (T * 0.6))
    K.side_door(p, t, inner=lambda q: yard_dawn(q, t, dawn=0.3, crowd=False), open_=k, lights=False)
    K.limb(p, (W + 60, H + 40), (700 - 200 * k, 490), 90, K.UNI, outline=4)
    p.ell(690 - 200 * k, 486, 40, 30, K.SKIN)


def group(p, t, k, irena_fall=0.0):
    """Czwórka od tyłu na podwórzu: Kuba trzyma Irenę pod ramię, Zosia z temblakiem, narrator z boku."""
    y = 760 - 260 * k
    s = 1.0 - 0.55 * k
    K.figure_back(p, 520 - 40 * k, y, s, t * 0.5, "kuba", walk=t * 0.5, arms={"r": (40, 90)})
    K.figure_back(p, 620 - 30 * k, y + 20 * irena_fall * s, s * (1 - 0.2 * irena_fall), t * 0.5, "irena", walk=t * 0.5)
    K.figure_back(p, 760 - 20 * k, y, s, t * 0.5, "zosia", walk=t * 0.5, arms={"l": (40, 20)})
    K.figure_back(p, 880 - 30 * k, y, s, t * 0.5, "narrator", walk=t * 0.5)


def s_walk(p, t, T):
    yard_dawn(p, t, dawn=0.35, crowd=False)
    group(p, t, 0.3 * t / T)


def s_locks(p, t, T):
    off = t > T * 0.3  # agregat gaśnie: światło, zamki
    R.corridor(p, t, [0, 0, 0, 0] if off else [1, 1, 1, 1], doors_open=0.5 * ease((t - T * 0.35) / (T * 0.5)))
    if off:
        for i in range(3):  # z sal wychodzą pozostali
            k = ease((t - T * 0.45 - i * 0.3) / 1.0)
            R.zombie(p, 260 + i * 380, 520 + 60 * k, 0.6 + 0.2 * k, t, 220 + i)


def s_trip(p, t, T):
    yard_dawn(p, t, dawn=0.45, crowd=False)
    fall = math.sin(min(1.0, t / (T * 0.8)) * math.pi)  # potyka się i wstaje
    group(p, t, 0.42, irena_fall=fall)


def s_check(p, t, T):
    yard_dawn(p, t, dawn=0.55, lights=0.6, crowd=False)
    K.figure(p, 380, 820, 1.25, t, "soldier", arms={"r": (90, -20)})
    K.figure(p, 980, 820, 1.25, t, "soldier", arms={"l": (-90, 0)})
    for x, d in ((470, 1), (890, -1)):  # latarki na dłonie
        p.glow([(x, 470), (x, 500), (x + d * 260, 600), (x + d * 260, 380)], (255, 250, 220, 70))
    K.figure(p, 680, 860, 1.15, t, "zosia", look=0.0, arms={"r": (60, -20)})
    K.sling(p, 680, 860, 1.15)


def s_doctor(p, t, T):
    yard_dawn(p, t, dawn=0.55, lights=0.6, crowd=False)
    wave = math.sin(t * 6) * 30 if t > T * 0.6 else 0  # macha: przechodź
    K.figure(p, 640, 1240, 2.6, t, "soldier", arms={"r": (80 + wave, -60)})
    p.ell(300, 620, 90, 64, K.WHO["zosia"]["skin"])  # dłoń Zosi z raną w świetle latarki
    p.line([(270, 610), (330, 630)], w=6, color=(170, 50, 50))
    K.limb(p, (-80, H + 40), (260, 640), 120, K.WHO["zosia"]["sleeve"], outline=4)
    p.glow([(160, 520), (440, 520), (440, 720), (160, 720)], (255, 250, 220, 60))


def s_sign(p, t, T):
    p.rect(0, 0, W, H, (86, 100, 70), w=0)
    K.paper(p, 600, 340, ["PRZEPUSTKA", "Irena — do ciężarówki"], w=620, h=300)
    k = ease(t / (T * 0.7))
    pts = [(420 + i * 30, 440 + 12 * math.sin(i * 1.7)) for i in range(int(10 * k) + 1)]
    if len(pts) > 1:
        p.line(pts, w=4, color=(40, 40, 120))  # podpis
    x, y = pts[-1]
    K.limb(p, (x + 400, H + 80), (x + 30, y + 50), 90, (92, 104, 72), outline=4)
    p.ell(x + 20, y + 30, 46, 34, (50, 56, 46))  # rękawica


def s_keycap(p, t, T):
    p.rect(0, 0, W, H, (60, 70, 52), w=0)  # wnętrze paki: plandeka
    K.limb(p, (-80, H + 40), (520, 470), 160, K.WHO["kuba"]["sleeve"], outline=4)
    sq = 6 * math.sin(t * 1.5)
    p.ell(640, 420, 190 - sq, 120, K.WHO["kuba"]["skin"])
    p.rect(580, 380, 700, 440, (246, 244, 236), w=3)  # nakładka klawisza
    for k in range(4):
        p.line([(700 + k * 6, 340 + k * 26), (790, 330 + k * 30)], w=24, color=K.WHO["kuba"]["skin"])


def s_silence(p, t, T):
    K.piano_room(p, t, wire=1.0)
    for i in range(8):  # tłum przy pianinie; pianino milknie
        R.zombie(p, 300 + i * 100 + 20 * math.sin(t + i), 760 + (i % 2) * 40, 1.0, t, 230 + i)
    alarm_pulse(p, t, 0.6)


def s_scream(p, t, T):
    p.rect(0, 0, W, H, (110, 104, 120), w=0)  # z drogi: szpital na wzgórzu o świcie
    p.glow([(0, 300), (W, 300), (W, 480), (0, 480)], (255, 170, 110, 50))
    p.rect(470, 340, 810, 420, (110, 106, 96))  # szpital z wieżą zegarową, jak w pierwszym ujęciu (za lasem)
    p.poly([(458, 344), (640, 312), (822, 344)], (60, 64, 68))
    p.rect(612, 296, 668, 344, (104, 100, 90))
    p.poly([(606, 300), (640, 276), (674, 300)], (60, 64, 68))
    p.ell(640, 318, 10, 10, (214, 210, 186), w=2)
    for r in range(2):
        for c in range(10):
            x0 = 484 + c * 32
            if r == 0 and c == 8:  # okno sali 8 — czerwone
                p.rect(x0, 356, x0 + 16, 374, (200, 70, 50), w=2)
            else:
                p.rect(x0, 356 + r * 30, x0 + 16, 374 + r * 30, (30, 36, 38), w=2)
    for k in range(10):  # las przed szpitalem zasłania jego podstawę
        x = k * 140 - 40
        p.poly([(x, 470), (x + 70, 380), (x + 140, 470)], (40, 52, 44))
    p.rect(-20, 460, W + 20, H + 20, (60, 70, 52))
    for i in range(7):  # ptaki zrywają się z dachu na krzyk
        k = ease((t - 0.3) / 1.2)
        bx, by = 600 + i * 20 + 200 * k * (1 + i * 0.1), 300 - 160 * k - 10 * i
        wing = 8 * math.sin(t * 20 + i)
        p.line([(bx - 12, by + wing), (bx, by), (bx + 12, by + wing)], w=3)


def s_understand(p, t, T):
    p.rect(0, 0, W, H, (60, 70, 52), w=0)
    p.glow([(0, 0), (500, 0), (500, H), (0, H)], (255, 180, 120, 40))  # świt przez plandekę
    k = ease((t - 0.4) / 1.2)
    R.nurse_face(p, 640, 330, 1.0, 0.3 + 0.3 * k, t, gaze=(-0.6 * k, 0.1))


def s_look_back(p, t, T):
    p.rect(0, 0, W, H, (40, 46, 36), w=0)  # tył ciężarówki: otwarta plandeka na drogę
    p.rect(200, 80, 1080, 640, (150, 140, 150))
    p.glow([(200, 300), (1080, 300), (1080, 640), (200, 640)], (255, 170, 110, 60))
    for k in range(10):
        x = 200 + k * 90
        p.poly([(x, 420), (x + 45, 340), (x + 90, 420)], (40, 52, 44))
    p.rect(200, 420, 1080, 640, (70, 70, 64))
    k = ease((t - 0.5) / 0.8)  # stoi twarzą do wnętrza paki; mimo obietnicy odwraca się do szpitala za plecami
    if k < 0.5:
        K.figure(p, 640, 900, 1.6, t, "narrator", look=-0.5 * k * 2, gaze=(-0.4, 0.5))
    else:
        K.figure_back(p, 640, 900, 1.6, t, "narrator")


def s_window8(p, t, T):
    K.window8_close(p, t, sil=3.0 + 3.1 * t / T, dawn=0.3)


def dawn_wide(p, t, T):
    K.window8_close(p, t, sil=None, dawn=0.3 + 0.7 * ease(t / T))  # nad lasem wschodzi słońce: jaśnieje niebo wokół budynku


def cam_window(lt, T):
    return {"zoom": 3.2, "cx": WX, "cy": WY}


def cam_out(lt, T):
    k = ease(lt / T)  # odjazd od okna do pełnego planu z pierwszego ujęcia
    return {"zoom": 3.2 - 2.2 * k, "cx": WX + (640 - WX) * k, "cy": WY + (360 - WY) * k}


FNS = [B.card("DZIEŃ 30"), s_chord, s_keys, s_turn, s_pour, s_side_door, s_walk, s_locks, s_trip, s_check, s_doctor, s_sign, s_keycap,
       s_silence, s_scream, s_understand, s_look_back, s_window8, dawn_wide]
LOOK = [None] + [B.WARD] * 2 + [B.NIGHT] + [B.WARD] + [B.NIGHT] * 4 + [B.DAWN] * 4 + [B.WARD] + [B.DAWN] * 5
CAM = {17: cam_window, 18: cam_out}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
