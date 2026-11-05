"""Wariant A · dzień 20 „Głos z bramy” — ujęcia rysowane kodem; czasy z rozpiski (tempo.py, MASTER_BIBLE)."""
import math
import sys

import dzien_base as B
import kit_a as K
import render as R
from render import H, W, ease

DAY = 20


def talk(t, T, a=0.3, b=0.4, speed=9):
    return 0.5 + 0.5 * math.sin(t * speed) if a < t < T - b else 0.0


def handset(p, x, y, s=1.0):
    p.poly([(x - 30 * s, y - 120 * s), (x + 10 * s, y - 130 * s), (x + 40 * s, y + 120 * s), (x, y + 130 * s)], (230, 228, 220), w=3)


def listening(p, t, T, fear=0.3, gaze=(-0.4, 0.2), speaking=False):
    """Narrator przy telefonie na ścianie: słuchawka przy uchu, kabel do aparatu."""
    K.staff_room(p, t)
    R.nurse_face(p, 640, 330, 1.0, (0.4 if speaking and 0.3 < t < T - 0.4 else fear), t, gaze=gaze)
    handset(p, 500, 360)
    p.line([(510, 490), (420, 620), (300, 700)], w=4, color=(60, 60, 60))
    if not speaking and int(t * 6) % 3 == 0:  # głos w słuchawce
        for k in range(2):
            p.line([(450 - k * 20, 300 - k * 14), (430 - k * 20, 290 - k * 14)], w=3)


def s_malec(p, t, T):
    listening(p, t, T, fear=0.45, gaze=(-0.6, 0.0))


def s_field_phone(p, t, T):
    K.yard_trucks(p, t, soldiers=False, wire=1.0)
    p.rect(560, 380, 720, 470, (86, 100, 70), w=3)  # polowy telefon przy bramie
    k = ease(t / (T * 0.7))
    p.line([(640, 470), (640 + 200 * k, 520 + 40 * k), (640 + 500 * k, 560)], w=5, color=(30, 30, 30))  # kabel wpinany w linię portierni
    K.figure(p, 460, 600, 0.55, t, "soldier", arms={"r": (60, 40)})


def s_how_many(p, t, T):
    listening(p, t, T, fear=0.35, gaze=(0.3, 0.3))


def s_five(p, t, T):
    listening(p, t, T, gaze=(0.0, 0.6), speaking=True)


def s_read_notes(p, t, T):
    p.rect(0, 0, W, H, (190, 186, 170), w=0)
    K.paper(p, 600, 340, ["14:20 — mówi do siebie", "16:05 — pojedyncze słowa", "19:40 — przestaje mrugać",
                          "23:10 — kołysanie"], w=600, h=360)
    k = ease(t / T)  # palec przesuwa się po kolejnych linijkach
    K.limb(p, (1200, 760), (860, 230 + 200 * k), 80, K.narr_sleeve(), outline=4)
    p.ell(850, 226 + 200 * k, 40, 30, K.SKIN)


def s_city_faster(p, t, T):
    listening(p, t, T, fear=0.5, gaze=(-0.2, -0.2))


def s_understands(p, t, T):
    K.staff_room(p, t)
    k = ease((t - 0.3) / 0.8)
    R.nurse_face(p, 640, 330, 1.0, 0.4 + 0.3 * k, t, gaze=(0.0, 0.8 * k))
    handset(p, 500 - 40 * k, 360 + 170 * k)  # słuchawka opada od ucha w dół, obok twarzy


def s_day30(p, t, T):
    listening(p, t, T, fear=0.4, gaze=(0.5, 0.0))


def s_healthy(p, t, T):
    listening(p, t, T, fear=0.55, gaze=(0.0, 0.3))


def s_zosia_asks(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(-0.4, 0.0), mouth=talk(t, T), fear=0.3)
    p.poly([(470, 240), (510, 230), (540, 480), (500, 490)], (230, 228, 220), w=3)


def s_zosia_pale(p, t, T):
    K.staff_room(p, t)
    k = ease((t - 0.4) / 0.8)  # blednie: oczy szeroko, oddech staje
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.0, 0.0), fear=0.3 + 0.6 * k, blink_k=0.0)
    p.poly([(470, 240), (510, 230), (540, 480), (500, 490)], (230, 228, 220), w=3)


def s_hang_up(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    p.rect(480, 140, 800, 560, (230, 228, 220), w=5)
    p.rect(520, 190, 760, 260, (60, 60, 60), w=3)
    k = ease(t / 0.5)  # słuchawka wraca na widełki — potem cisza
    p.poly([(520, 300 - 120 * (1 - k)), (760, 300 - 120 * (1 - k)), (760, 340 - 120 * (1 - k)), (520, 340 - 120 * (1 - k))],
           (230, 228, 220), w=3)


def s_stitches(p, t, T):
    p.rect(0, 0, W, H, (200, 196, 176), w=0)
    K.limb(p, (W + 80, H + 80), (700, 460), 160, K.WHO["kuba"]["sleeve"], outline=4)
    turn = ease(t / 0.6)  # obraca dłoń wnętrzem do siebie
    p.ell(620, 420, 150, 110 * (0.6 + 0.4 * turn), K.WHO["kuba"]["skin"])
    for i in range(6):
        x = 540 + i * 30
        p.line([(x, 390), (x + 12, 430)], w=3, color=(30, 30, 60))
    p.line([(530, 410), (720, 410)], w=3, color=(170, 60, 60))


def s_heal(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 640, 330, 1.0, "zosia", t, gaze=(0.5, 0.3), mouth=talk(t, T), fear=0.15)


def s_irena(p, t, T):
    K.staff_room(p, t)
    cough = 6 * math.sin(t * 30) if T * 0.75 < t < T * 0.75 + 0.4 else 0
    K.face_cu(p, 640, 330 + cough * 0.3, 1.0, "irena", t, gaze=(0.0, 0.2), mouth=talk(t, T * 0.75), fear=0.0)


def s_henryk_hand(p, t, T):
    K.staff_room(p, t)
    K.face_cu(p, 760, 330, 0.95, "henryk", t, gaze=(-0.6, 0.2), mouth=talk(t, T, 0.6, 0.4, 6) * 0.8)
    k = ease((t - 0.2) / 0.5)  # bierze Irenę za rękę
    K.limb(p, (900, H + 60), (560 - 40 * k, 640), 80, K.WHO["henryk"]["top"], outline=4)
    p.ell(520 - 40 * k, 640, 46, 32, K.WHO["henryk"]["skin"])
    K.limb(p, (-60, H + 40), (480 - 40 * k, 650), 70, K.WHO["irena"]["sleeve"], outline=4)
    p.ell(470 - 40 * k, 650, 40, 28, K.WHO["irena"]["skin"])


def city(q, t, fire=1.0):
    q.rect(0, 0, W, H, (24, 26, 40), w=0)
    q.poly([(0, 330), (W, 320), (W, H), (0, H)], (20, 26, 22))
    for i in range(14):  # łuna nad miastem
        x = 120 + i * 34
        f = 0.5 + 0.5 * math.sin(t * 3 + i)
        q.ell(x, 320, 16, 10 + 14 * f * fire, (230, int(120 + 40 * f), 50), w=0)
    q.glow([(80, 200), (640, 200), (640, 340), (80, 340)], (255, 140, 60, int(50 * fire)))


def s_city(p, t, T):
    K.ward_room(p, t, sheet=0.0, inner=lambda q: city(q, t))
    K.sheet_on_pane(p)  # prześcieradło z dnia 19 na prawej szybie
    K.figure_back(p, 260, 800, 1.1, t, "narrator")


def s_daughter(p, t, T):
    p.rect(0, 0, W, H, (24, 26, 40), w=0)
    flick = 0.5 + 0.5 * math.sin(t * 3)
    p.glow([(0, 0), (500, 0), (500, H), (0, H)], (255, 140, 60, int(30 + 20 * flick)))  # łuna na twarzy
    R.nurse_face(p, 700, 330, 1.0, 0.3, t, gaze=(-0.9, -0.1))


def s_wardrobe(p, t, T):
    k = ease((t - T * 0.45) / (T * 0.3))  # za jego plecami szafa uchyla się na centymetr
    K.ward_room(p, t, sheet=0.0, wardrobe=0.06 * k, inner=lambda q: city(q, t, 0.6))
    K.sheet_on_pane(p)
    K.figure_back(p, 260, 800, 1.1, t, "narrator")


FNS = [B.card("DZIEŃ 20"), s_malec, s_field_phone, s_how_many, s_five, s_read_notes, s_city_faster, s_understands,
       s_day30, s_healthy, s_zosia_asks, s_zosia_pale, s_hang_up, s_stitches, s_heal, s_irena, s_henryk_hand, s_city,
       s_daughter, s_wardrobe]
LOOK = [None] + [B.WARD] + [B.DAY] + [B.WARD] * 14 + [B.NIGHT] * 3
CAM = {}
SCENES, DUR, frame = B.setup(DAY, FNS, LOOK, CAM)

if __name__ == "__main__":
    B.stills(sys.modules[__name__], [float(a) for a in sys.argv[1:]])
