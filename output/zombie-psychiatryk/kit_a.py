"""Wspólny zestaw do ujęć wariantu A (30 dni): postacie, twarze, tła i rekwizyty w stylu render.py / render2.py.

Wszystko rysuje się w układzie 1280×720 przez Pen z render.py (kreska „gotuje się” 8 razy na sekundę).
Zasady kadru: docs/WYTYCZNE_UJEC.md — otwory przycinają to, co za nimi; kraty i szyby są przed postacią;
bliżej kamery rysuje się później; tłum to osobne postacie z własnym tempem.
"""
import math
import random
from contextlib import contextmanager

import render as R
import render2 as R2
import rig_a as rig
from render import INK, W, H, ease, noise, blink

SKIN, HAIR, UNI, TROUSERS = R2.SKIN, R2.HAIR, R2.UNI, R2.TROUSERS
ZSKIN = (139, 156, 128)
WHITE = (244, 244, 240)
NO_BLINK = {"henryk", "soldier"}
JACKET = (58, 66, 78)
NARRATOR_JACKET = False  # narrator nosi kurtkę od d02_18 (księga świata: rekwizyt „kurtka”); ustawia dzien_base
DAY = 0  # bieżący dzień (ustawia dzien_base.setup)
HENRYK_SHIRT = False  # czysta koszula z magazynu: od d29_10 (księga świata)
NARRATOR_KNEE = False  # opatrunek na kolanie: od d23_19
SHIRT = (236, 236, 228)
MAINS = True  # prąd z sieci; dzien_base wyłącza go od dnia 3 (księga świata: prąd z sieci do d02_19)  # pan Henryk nie mruga (to jego znak od zimnego otwarcia); żołnierz ma maskę

WHO = {
    "narrator": dict(skin=SKIN, top=UNI, sleeve=UNI, bottom=TROUSERS, shoes=(240, 240, 236), neck=WHITE, hair="orderly",
                     eye=10, pupil=3.5),
    "henryk": dict(skin=(186, 194, 170), top=(150, 154, 148), sleeve=(150, 154, 148), bottom=(186, 194, 170),
                   shoes=(120, 116, 108), neck=(186, 194, 170), hair="henryk", eye=12, pupil=2.5),
    "zosia": dict(skin=(234, 204, 182), top=(52, 62, 92), sleeve=(52, 62, 92), bottom=(236, 236, 230),
                  shoes=(240, 240, 236), neck=WHITE, hair="bun", eye=10, pupil=3.5, badge=True),
    "nowak": dict(skin=(230, 206, 188), top=(236, 236, 232), sleeve=(236, 236, 232), bottom=(70, 74, 84),
                  shoes=(40, 40, 40), neck=(40, 44, 56), hair="nowak", eye=9, pupil=3.0),
    "irena": dict(skin=(232, 208, 194), top=(170, 128, 146), sleeve=(170, 128, 146), bottom=(170, 128, 146),
                  shoes=(200, 170, 180), neck=(232, 208, 194), hair="irena", eye=9, pupil=3.0),
    "kuba": dict(skin=(228, 196, 170), top=(132, 136, 140), sleeve=(132, 136, 140), bottom=(118, 122, 126),
                 shoes=(232, 232, 228), neck=(84, 104, 78), hair="kuba", eye=10, pupil=3.5),
    "soldier": dict(skin=(150, 150, 140), top=(92, 104, 72), sleeve=(92, 104, 72), bottom=(84, 96, 66),
                    shoes=(36, 36, 34), neck=(92, 104, 72), hair="mask", eye=0, pupil=0),
}


def _costume(who):
    """Strój postaci w bieżącym ujęciu: kurtka narratora (d02_18–d10_16), czysta koszula Henryka (od d29_10)."""
    c = WHO[who]
    if who == "narrator" and NARRATOR_JACKET:
        c = {**c, "top": JACKET, "sleeve": JACKET}
    if who == "henryk" and HENRYK_SHIRT:
        c = {**c, "top": SHIRT, "sleeve": SHIRT}
    return c


def limb(p, a, b, w, col, outline=3):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    p.poly([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], col, w=outline)


def _hair_back(p, c, hx, hy, s):
    if c["hair"] == "bun":
        p.ell(hx, hy - 58 * s, 22 * s, 18 * s, (52, 40, 36))


def _hair_front(p, c, hx, hy, s):
    st = c["hair"]
    if st == "orderly":
        p.poly([(hx - 47 * s, hy), (hx - 44 * s, hy - 36 * s), (hx - 10 * s, hy - 56 * s), (hx + 30 * s, hy - 52 * s),
                (hx + 48 * s, hy - 24 * s), (hx + 46 * s, hy - 2 * s), (hx + 20 * s, hy - 24 * s), (hx - 24 * s, hy - 20 * s)], HAIR)
        for i in range(5):  # zarost
            a = math.pi * (0.25 + 0.5 * i / 4)
            p.line([(hx + math.cos(a) * 36 * s, hy + 18 * s + math.sin(a) * 30 * s),
                    (hx + math.cos(a) * 38 * s, hy + 20 * s + math.sin(a) * 31 * s)], w=2, color=(120, 100, 88))
    elif st == "henryk":
        for side in (-1, 1):
            p.ell(hx + side * 42 * s, hy - 4 * s, 9 * s, 18 * s, (176, 176, 170), w=2.5)
        p.line([(hx - 18 * s, hy - 30 * s), (hx + 16 * s, hy - 31 * s)], w=2, color=(120, 128, 112))
    elif st == "nowak":
        for side in (-1, 1):
            p.ell(hx + side * 40 * s, hy - 14 * s, 10 * s, 20 * s, (170, 170, 166), w=2.5)
        p.line([(hx - 20 * s, hy - 44 * s), (hx + 18 * s, hy - 46 * s)], w=2, color=(150, 150, 146))
    elif st == "mask":
        p.poly([(hx - 50 * s, hy - 6 * s), (hx - 46 * s, hy - 46 * s), (hx, hy - 62 * s), (hx + 46 * s, hy - 46 * s),
                (hx + 50 * s, hy - 6 * s)], (78, 90, 60))
        p.ell(hx, hy + 14 * s, 38 * s, 34 * s, (120, 124, 118))
        for side in (-1, 1):
            p.ell(hx + side * 17 * s, hy + 6 * s, 11 * s, 11 * s, (30, 34, 36), w=3)
        p.ell(hx, hy + 40 * s, 14 * s, 12 * s, (70, 72, 70), w=3)
    elif st == "irena":  # siwe loki
        for k in range(7):
            a = math.pi * (1.05 + 0.9 * k / 6)
            p.ell(hx + math.cos(a) * 40 * s, hy - 8 * s + math.sin(a) * 44 * s, 15 * s, 13 * s, (206, 204, 200), w=2.5)
    elif st == "kuba":  # rozczochrane ciemne włosy
        p.poly([(hx - 48 * s, hy - 4 * s), (hx - 50 * s, hy - 40 * s), (hx - 30 * s, hy - 52 * s), (hx - 20 * s, hy - 64 * s),
                (hx, hy - 54 * s), (hx + 18 * s, hy - 66 * s), (hx + 30 * s, hy - 52 * s), (hx + 50 * s, hy - 40 * s),
                (hx + 48 * s, hy - 4 * s), (hx + 26 * s, hy - 30 * s), (hx - 4 * s, hy - 26 * s), (hx - 30 * s, hy - 32 * s)],
               (46, 36, 30))
    elif st == "bun":
        p.poly([(hx - 48 * s, hy - 2 * s), (hx - 42 * s, hy - 38 * s), (hx, hy - 56 * s), (hx + 42 * s, hy - 38 * s),
                (hx + 48 * s, hy - 2 * s), (hx + 30 * s, hy - 30 * s), (hx, hy - 38 * s), (hx - 30 * s, hy - 30 * s)], (52, 40, 36))


def figure(p, x, y, s, t, who, walk=None, look=0.0, arms=None, eyes=None, mouth=0.0, lean=0.0, gaze=None, legs=True):
    """Postać od przodu, stopy w (x, y); s=1 to ok. 390 px wzrostu. walk — zegar chodu (None: stoi);
    look -1..1 — twarz w bok; arms {'l'|'r': (dx, dy)} — dłoń względem barku w jednostkach s;
    eyes 0..1 — otwarcie oczu; mouth 0..1; gaze — (gx, gy) źrenic, domyślnie tam, gdzie twarz."""
    c = _costume(who)
    seed = sum(map(ord, who)) * 13
    P = rig.pose(who, hint=look if abs(look) > 0.2 else (gaze[0] if gaze else None))  # rig ujęcia (rig_a)
    if P["active"]:
        if P["mouth"] is not None:
            mouth = P["mouth"]
        look = max(-1.0, min(1.0, look + P["yaw"]))
        if gaze is not None or P["gx"] or P["gy"]:
            g0 = gaze if gaze is not None else (look, 0.0)
            gaze = (max(-1.0, min(1.0, g0[0] + P["gx"])), max(-1.0, min(1.0, g0[1] + P["gy"])))
        lean = lean + P["bx"] * 2.3
    shu = P["shrug"] * 14 * s
    if eyes is None:  # samo mruganie, każda postać we własnym rytmie; pan Henryk nie mruga nigdy (MASTER_BIBLE 2.6)
        eyes = 1.0 if who in NO_BLINK else 1 - R.blink(t, seed, 2.6 + (seed % 7) * 0.25)
    ph = (walk or 0.0) * 6
    if walk is not None:
        y -= abs(math.sin(ph)) * 5 * s
    if legs:
        for side, sgn in ((-1, 1), (1, -1)):
            lift = max(0, math.sin(ph) * sgn) * 16 * s if walk is not None else 0
            lx = x + side * 18 * s
            p.poly([(lx - 16 * s, y - 120 * s), (lx + 16 * s, y - 120 * s), (lx + 14 * s, y - 14 * s - lift),
                    (lx - 14 * s, y - 14 * s - lift)], c["bottom"])
            p.ell(lx, y - 8 * s - lift, 18 * s, 10 * s, c["shoes"], w=3)
            if who == "narrator" and NARRATOR_KNEE and side < 0:  # opatrunek na rozciętym kolanie (d23)
                p.rect(lx - 15 * s, y - 78 * s, lx + 15 * s, y - 58 * s, WHITE, w=2)
    tx = x + lean * 20 * s
    p.poly([(tx - 54 * s, y - 280 * s - shu * 0.7), (tx + 54 * s, y - 280 * s - shu * 0.7), (x + 56 * s, y - 112 * s),
            (x - 56 * s, y - 112 * s)], c["top"])
    if who == "zosia":
        p.poly([(tx - 22 * s, y - 280 * s), (tx, y - 212 * s), (tx + 22 * s, y - 280 * s)], WHITE, w=3)
        p.line([(tx - 14 * s, y - 276 * s), (tx + 18 * s, y - 214 * s)], w=2, color=(170, 40, 40))
        p.rect(tx + 12 * s, y - 214 * s, tx + 34 * s, y - 186 * s, WHITE, w=2)
    else:
        if who == "narrator" and NARRATOR_JACKET:  # rozpięta kurtka: spod niej widać mundurek
            p.poly([(tx - 18 * s, y - 280 * s), (tx + 18 * s, y - 280 * s), (x + 16 * s, y - 112 * s), (x - 16 * s, y - 112 * s)], UNI, w=2.5)
        p.poly([(tx - 22 * s, y - 280 * s), (tx, y - 252 * s), (tx + 22 * s, y - 280 * s)], c["neck"], w=3)
    arms = arms or {}
    hands = {}
    for side in (-1, 1):
        key = "l" if side < 0 else "r"
        sh = (tx + side * 50 * s, y - 268 * s - shu)
        dx, dy = arms.get(key, (side * 14, 95 + (math.sin(ph) * side * 8 if walk is not None else 0)))
        if P["gesture"] > 0 and key == P["hand"] and key not in arms:  # gest przy mówieniu: dłoń przed tułowiem
            g = ease(P["gesture"])
            dx, dy = dx + (side * 38 + P["gdx"] - dx) * g, dy + (44 + P["gdy"] - dy) * g
        hand = (sh[0] + dx * s, sh[1] + dy * s)
        limb(p, sh, hand, 24 * s, c["sleeve"])
        p.ell(hand[0], hand[1], 13 * s, 13 * s, c["skin"])
        hands[key] = hand
    hx, hy = tx + look * 6 * s + P["hx"] * 46 * s, y - 336 * s + P["hy"] * 46 * s - shu * 0.5
    p.poly([(hx - 14 * s, hy + 40 * s), (hx + 14 * s, hy + 40 * s), (tx + 14 * s, y - 274 * s), (tx - 14 * s, y - 274 * s)],
           c["skin"], w=3)
    p.push(pivot=(hx, hy + 40 * s), rot=P["rot"])  # głowa obraca się na szyi
    _hair_back(p, c, hx, hy, s)
    p.ell(hx, hy, 46 * s, 52 * s, c["skin"])
    _hair_front(p, c, hx, hy, s)
    fx = hx + look * 22 * s
    er = c["eye"] * 0.6  # oko w planie ogólnym: mniejsze, kreska cieńsza (z daleka oczy były za duże)
    ew = max(1.5, min(3.0, 3.0 * s))
    gx, gy = gaze if gaze is not None else (look, 0.0)
    if c["hair"] == "mask":
        p.pop()
        return hands
    for side in (-1, 1):
        if (look > 0.6 and side < 0) or (look < -0.6 and side > 0):
            continue  # dalsze oko schowane
        ex, ey = fx + side * 18 * s, hy + 6 * s
        if eyes < 0.25:
            p.line([(ex - er * s, ey), (ex + er * s, ey)], w=ew)
        else:
            p.ell(ex, ey, er * s, (er + 0.6) * s * eyes, (246, 246, 240), w=ew)
            pr = max(1.2, c["pupil"] * 0.8 * s)
            p.ell(ex + gx * 2.5 * s, ey + gy * 2.5 * s * eyes, pr, pr, INK, w=0)
    if who == "nowak":  # okulary
        for side in (-1, 1):
            p.ell(fx + side * 18 * s, hy + 6 * s, 11 * s, 10 * s, None, w=ew * 0.85)
        p.line([(fx - 7 * s, hy + 5 * s), (fx + 7 * s, hy + 5 * s)], w=ew * 0.85)
    if mouth > 0.15:
        p.ell(fx, hy + 30 * s, 7 * s, (4 + 8 * mouth) * s, (70, 30, 30), w=3)
    else:
        p.line([(fx - 9 * s, hy + 30 * s), (fx + 9 * s, hy + 30 * s)], w=3)
    p.pop()
    return hands


def face_cu(p, x, y, s, who, t, gaze=(0.0, 0.0), blink_k=None, mouth=0.0, fear=0.0, breath=0.0, white=False):
    """Zbliżenie twarzy (Zosia, Henryk) w skali nurse_face z render.py: środek głowy w (x, y).
    Rig (rig_a.pose): tułów pochyla się i unosi ramiona, głowa obraca się wokół szyi, twarz skręca w bok (yaw),
    usta idą za prawdziwym oknem kwestii — tylko w ujęciach z wpisem w RIG dnia."""
    c = _costume(who)
    skin = c["skin"]
    seed = sum(map(ord, who)) * 17
    P = rig.pose(who, hint=gaze[0])
    rr = 120 * s
    if blink_k is None:  # samo mruganie, chyba że ujęcie ustawia oczy; pan Henryk nie mruga nigdy
        blink_k = 0.0 if who in NO_BLINK else R.blink(t, seed, 2.8 + (seed % 5) * 0.3)
    if P["mouth"] is not None:
        mouth = P["mouth"]
    gaze = (max(-1.0, min(1.0, gaze[0] + P["gx"])), max(-1.0, min(1.0, gaze[1] + P["gy"])))
    breath = (breath + 0.6 * math.sin(2 * math.pi * 0.27 * t + seed)) * P["breath"] + P["breath_add"]
    if P["lean"]:
        p.push(pivot=(x, 760), sx=1 + P["lean"])
    bx, sh = P["bx"] * rr, P["shrug"] * 34 * s
    by = y - breath * 5 * s + P["by"] * rr
    bot = max(by + 400 * s, 760)  # tułów zawsze wychodzi poza dolną krawędź kadru
    sp = 120 * s + 30 * s * (bot - by - 150 * s) / (250 * s)
    p.poly([(x + bx - 120 * s, by + 150 * s - sh), (x + bx + 120 * s, by + 150 * s - sh), (x + sp, bot), (x - sp, bot)], c["top"])
    hdx, hdy = bx + P["hx"] * rr, P["by"] * rr + P["hy"] * rr
    p.poly([(x + hdx - 30 * s, y + hdy + 90 * s), (x + hdx + 30 * s, y + hdy + 90 * s), (x + bx + 34 * s, by + 160 * s),
            (x + bx - 34 * s, by + 160 * s)], skin)
    cx_, cy_ = x + bx, by - sh * 0.6  # kołnierz idzie z tułowiem
    if who == "zosia":
        p.poly([(cx_ - 40 * s, cy_ + 150 * s), (cx_, cy_ + 230 * s), (cx_ + 40 * s, cy_ + 150 * s)], WHITE, w=3)
    elif who == "nowak":  # bluza zapięta pod szyję pod fartuchem
        p.poly([(cx_ - 44 * s, cy_ + 120 * s), (cx_ + 44 * s, cy_ + 120 * s), (cx_ + 50 * s, cy_ + 260 * s), (cx_ - 50 * s, cy_ + 260 * s)],
               (40, 44, 56), w=3)
        p.line([(cx_, cy_ + 124 * s), (cx_, cy_ + 260 * s)], w=3, color=(150, 150, 150))
    else:
        p.poly([(cx_ - 40 * s, cy_ + 150 * s), (cx_, cy_ + 200 * s), (cx_ + 40 * s, cy_ + 150 * s)], c["top"], w=3)
    p.push(pivot=(x, y + 110 * s), rot=P["rot"], dx=hdx, dy=hdy)  # głowa na szyi
    yaw = P["yaw"]
    HEAD[who] = (x, P["lean"], (x, y + 110 * s), P["rot"], hdx, hdy, yaw * 30 * s)
    fx = x + yaw * 30 * s  # twarz skręca, czaszka zostaje
    hx_ = x + yaw * 8 * s
    if who == "zosia":
        p.ell(hx_, y - 150 * s, 52 * s, 40 * s, (52, 40, 36))
    for side in (-1, 1):
        hide = max(0.0, side * yaw)
        p.ell(x + side * 122 * s - yaw * 14 * s, y + 14 * s, 18 * s * (1 - 0.5 * hide), 30 * s, skin)
    p.ell(x, y + 6 * s, 120 * s, 132 * s, skin, n=34)
    if who == "zosia":
        p.poly([(hx_ - 126 * s, y - 6 * s), (hx_ - 116 * s, y - 96 * s), (hx_ - 40 * s, y - 140 * s), (hx_ + 40 * s, y - 140 * s),
                (hx_ + 116 * s, y - 96 * s), (hx_ + 126 * s, y - 6 * s), (hx_ + 80 * s, y - 80 * s), (hx_, y - 96 * s),
                (hx_ - 80 * s, y - 80 * s)], (52, 40, 36))
    elif who == "nowak":
        for side in (-1, 1):
            p.ell(hx_ + side * 108 * s, y - 30 * s, 24 * s, 50 * s, (170, 170, 166), w=3)
        p.line([(hx_ - 60 * s, y - 100 * s), (hx_ + 56 * s, y - 104 * s)], w=2.5, color=(150, 150, 146))
    elif who == "irena":
        for k in range(9):
            a = math.pi * (1.0 + k / 8)
            p.ell(hx_ + math.cos(a) * 108 * s, y - 20 * s + math.sin(a) * 118 * s, 36 * s, 32 * s, (206, 204, 200), w=3)
    elif who == "kuba":
        p.poly([(hx_ - 126 * s, y - 4 * s), (hx_ - 128 * s, y - 90 * s), (hx_ - 80 * s, y - 130 * s), (hx_ - 50 * s, y - 160 * s),
                (hx_, y - 136 * s), (hx_ + 46 * s, y - 166 * s), (hx_ + 80 * s, y - 132 * s), (hx_ + 128 * s, y - 90 * s),
                (hx_ + 126 * s, y - 4 * s), (hx_ + 70 * s, y - 76 * s), (hx_ - 10 * s, y - 70 * s), (hx_ - 76 * s, y - 84 * s)],
               (46, 36, 30))
    elif who == "henryk":
        for side in (-1, 1):
            p.ell(hx_ + side * 112 * s, y - 20 * s, 22 * s, 44 * s, (176, 176, 170), w=3)
        for k in range(3):
            p.line([(hx_ - 50 * s, y - 70 * s - k * 16 * s), (hx_ + 48 * s, y - 72 * s - k * 16 * s)], w=2, color=(120, 128, 112))
    big = 1.25 if who == "henryk" else 1.0
    open_ = (0.55 + 0.45 * ease(fear)) * (1 - blink_k)
    for side in (-1, 1):
        ex, ey = fx + side * 46 * s, y + 6 * s
        r = (14 + 8 * ease(fear)) * big
        rx = r * (1 - 0.3 * max(0.0, side * yaw))  # dalsze oko w skręcie węższe
        ry = (r + 3) * open_
        if ry < 3:
            p.line([(ex - rx * s, ey), (ex + rx * s, ey)], w=4)
        else:
            p.ell(ex, ey, rx * s, ry * s, (246, 246, 240), w=3.5)
            pr = min(5.5 if who != "henryk" else 3.5, ry * 0.7)
            if white:  # po przemianie: bielmo zamiast źrenicy (Nowak od d17_08)
                p.ell(ex, ey, pr * 0.9 * s, pr * 0.9 * s, (204, 208, 198), w=0)
            else:
                p.ell(ex + gaze[0] * (rx - 6) * s, ey + gaze[1] * ry * 0.35 * s, pr * s, pr * s, INK, w=0)
        p.line([(ex - 22 * s, ey - (18 + 14 * fear) * s), (ex + 20 * s, ey - (18 + 14 * fear) * s + side * 4 * s)], w=4)
    if who == "nowak":
        for side in (-1, 1):
            p.ell(fx + side * 46 * s, y + 6 * s, 34 * s * (1 - 0.3 * max(0.0, side * yaw)), 28 * s, None, w=4)
        p.line([(fx - 12 * s, y + 2 * s), (fx + 12 * s, y + 2 * s)], w=4)
        for dx, dy in ((96, -10), (104, 20)):  # pot przy skroni
            p.poly([(x + dx * s, y + (dy - 12) * s), (x + (dx + 7) * s, y + dy * s), (x + dx * s, y + (dy + 8) * s),
                    (x + (dx - 7) * s, y + dy * s)], (190, 220, 235), w=2)
    p.line([(fx - 4 * s, y + 30 * s), (fx - 10 * s, y + 52 * s), (fx + 2 * s, y + 54 * s)], w=3)
    if mouth > 0.15:
        p.ell(fx, y + 84 * s, (8 + 4 * mouth) * s, (4 + 12 * mouth) * s, (70, 30, 30), w=3.5)
    else:
        p.line([(fx - 18 * s, y + 82 * s), (fx + 18 * s, y + 82 * s)], w=4)
    if who == "henryk":
        for side in (-1, 1):
            p.line([(fx + side * 70 * s, y + 40 * s), (fx + side * 60 * s, y + 80 * s)], w=2.5, color=(140, 150, 128))
    p.pop()
    if P["lean"]:
        p.pop()


HEAD = {}  # ostatni układ głowy zbliżenia: postać → (x, lean, pivot, rot, dx, dy, przesunięcie twarzy)


@contextmanager
def on_face(p, who, face=True):
    """Rysuj w układzie głowy zbliżenia, które przed chwilą narysowało face_cu / nurse_face (łza, uśmiech,
    nadęte policzki, słuchawka przy uchu) — z rigiem przyklejone do twarzy, bez rigu bez zmian.
    face=True: rzecz leży na twarzy (idzie też za skrętem twarzy), False: przy uchu / na czaszce."""
    x, lean, pivot, rot, dx, dy, fs = HEAD.get(who, (640, 0.0, (640, 440), 0.0, 0.0, 0.0, 0.0))
    n = 0
    if lean:
        p.push(pivot=(x, 760), sx=1 + lean)
        n += 1
    if rot or dx or dy or (face and fs):
        p.push(pivot=pivot, rot=rot, dx=dx + (fs if face else 0.0), dy=dy)
        n += 1
    try:
        yield
    finally:
        for _ in range(n):
            p.pop()


def narrator_cu(p, x, y, s, fear, t, gaze=(0.0, 0.0), blink_k=0.0, swallow=0.0, breath=0.0, body=None):
    """Zbliżenie narratora (render.nurse_face) z rigiem rig_a; bez wpisu w RIG rysunek jak w nurse_face
    (plus poły kurtki, gdy narrator ją nosi). Usta: w akcji „mowi” idą za oknem kwestii, inaczej otwiera je strach."""
    P = rig.pose("narrator", hint=gaze[0])
    rr = 120 * s
    skin = (232, 200, 174)
    gaze = (max(-1.0, min(1.0, gaze[0] + P["gx"])), max(-1.0, min(1.0, gaze[1] + P["gy"])))
    swallow = max(swallow, P["swallow"])
    breath = breath * P["breath"] + P["breath_add"]
    if P["lean"]:
        p.push(pivot=(x, 760), sx=1 + P["lean"])
    bx, by = body or (x, y)
    bx += P["bx"] * rr
    by += P["by"] * rr - breath * 5 * s
    sh = P["shrug"] * 34 * s
    hdx, hdy = P["bx"] * rr + P["hx"] * rr, P["by"] * rr + P["hy"] * rr
    p.poly([(bx - 120 * s, by + 150 * s - sh), (bx + 120 * s, by + 150 * s - sh), (bx + 150 * s, by + 400 * s + breath * 5 * s),
            (bx - 150 * s, by + 400 * s + breath * 5 * s)], (150, 180, 190))
    p.poly([(x + hdx - 30 * s, y + hdy + 90 * s), (x + hdx + 30 * s, y + hdy + 90 * s), (bx + 34 * s, by + 160 * s),
            (bx - 34 * s, by + 160 * s)], skin)
    if swallow > 0:
        p.line([(x + hdx - 8 * s, y + hdy + 140 * s - swallow * 22 * s), (x + hdx + 8 * s, y + hdy + 138 * s - swallow * 22 * s)], w=3)
    p.poly([(bx - 40 * s, by + 150 * s - sh * 0.6), (bx, by + 200 * s - sh * 0.6), (bx + 40 * s, by + 150 * s - sh * 0.6)],
           (244, 244, 240), w=3)
    _narrator_jacket(p, bx, by, s, sh)
    p.push(pivot=(x, y + 110 * s), rot=P["rot"], dx=hdx, dy=hdy)
    yaw = P["yaw"]
    HEAD["narrator"] = (x, P["lean"], (x, y + 110 * s), P["rot"], hdx, hdy, yaw * 30 * s)
    fx, hx_ = x + yaw * 30 * s, x + yaw * 8 * s
    hair = (58, 46, 38)
    for side in (-1, 1):
        hide = max(0.0, side * yaw)
        p.ell(x + side * 122 * s - yaw * 14 * s, y + 14 * s, 18 * s * (1 - 0.5 * hide), 30 * s, skin)
    p.ell(x, y + 6 * s, 120 * s, 132 * s, skin, n=34)
    p.poly([(hx_ - 126 * s, y - 10 * s), (hx_ - 120 * s, y - 100 * s), (hx_ - 60 * s, y - 150 * s), (hx_ + 40 * s, y - 156 * s),
            (hx_ + 112 * s, y - 120 * s), (hx_ + 126 * s, y - 20 * s), (hx_ + 100 * s, y - 70 * s), (hx_ + 20 * s, y - 92 * s),
            (hx_ - 70 * s, y - 80 * s)], hair)
    for i in range(9):  # zarost
        a = math.pi * (0.15 + 0.7 * i / 8)
        p.line([(fx + math.cos(a) * 92 * s, y + 40 * s + math.sin(a) * 80 * s),
                (fx + math.cos(a) * 96 * s, y + 44 * s + math.sin(a) * 82 * s)], w=3, color=(120, 100, 88))
    open_ = (0.4 + 0.6 * ease(fear)) * (1 - blink_k)
    for side in (-1, 1):
        ex, ey = fx + side * 46 * s, y + 6 * s
        r = 14 + 8 * ease(fear)
        rx = r * (1 - 0.3 * max(0.0, side * yaw))
        ry = (r + 3) * open_
        if ry < 3:
            p.line([(ex - rx * s, ey), (ex + rx * s, ey)], w=4)
        else:
            p.ell(ex, ey, rx * s, ry * s, (246, 246, 240), w=3.5)
            pr = min(5.5, ry * 0.7)
            p.ell(ex + gaze[0] * (rx - 6) * s, ey + gaze[1] * ry * 0.35 * s, pr * s, pr * s, INK, w=0)
            if open_ < 0.75:  # ciężka powieka
                p.line([(ex - rx * s, ey - ry * 0.4 * s), (ex, ey - ry * s - 3 * s), (ex + rx * s, ey - ry * 0.4 * s)], w=4)
        bl = 16 + 18 * ease(fear)
        p.line([(ex - 22 * s, ey - bl * s - side * 4 * s * fear), (ex + 20 * s, ey - bl * s + side * 6 * s * fear)], w=4)
    p.line([(fx - 4 * s, y + 30 * s), (fx - 10 * s, y + 52 * s), (fx + 2 * s, y + 54 * s)], w=3)
    m = P["mouth"]
    if m is not None:
        if m > 0.15:
            p.ell(fx, y + 84 * s, (8 + 4 * m) * s, (4 + 12 * m) * s, (70, 30, 30), w=3.5)
        else:
            p.line([(fx - 18 * s, y + 82 * s), (fx + 18 * s, y + 82 * s)], w=4)
    elif fear < 0.3:
        p.line([(fx - 18 * s, y + 82 * s), (fx + 18 * s, y + 82 * s)], w=4)
    else:
        p.ell(fx, y + 84 * s, (8 + 6 * fear) * s, (8 + 12 * fear) * s, (70, 30, 30), w=3.5)
    if fear >= 0.3:
        dy = (t * 40) % 40
        p.poly([(x + 104 * s, y - 40 * s + dy), (x + 112 * s, y - 20 * s + dy), (x + 104 * s, y - 12 * s + dy), (x + 96 * s, y - 20 * s + dy)],
               (190, 220, 235), w=2.5)
    p.pop()
    if P["lean"]:
        p.pop()


def _narrator_jacket(p, bx, by, s, sh=0.0):
    """Poły rozpiętej kurtki narratora po bokach (d02_18–d10_16); środek z mundurkiem zostaje odkryty."""
    if not NARRATOR_JACKET:
        return
    for side in (-1, 1):
        p.poly([(bx + side * 120 * s, by + 150 * s - sh), (bx + side * 48 * s, by + 150 * s - sh * 0.6), (bx + side * 60 * s, by + 410 * s),
                (bx + side * 152 * s, by + 410 * s)], JACKET)
        p.poly([(bx + side * 50 * s, by + 150 * s - sh * 0.6), (bx + side * 34 * s, by + 152 * s - sh * 0.6), (bx + side * 60 * s, by + 230 * s)],
               (90, 98, 110), w=2.5)  # klapa kołnierza


def zombie_profile(p, x, y, s, t, seed=3):
    """Pacjent w profilu, zwrócony w lewo: białe, suche oko bez mrugania, otwarte usta, ledwie widoczny oddech."""
    gown = (162, 172, 164)
    sway = 4 * noise(t, seed, 0.6) * s
    p.poly([(x - 170 * s, y + 160 * s), (x + 230 * s, y + 160 * s), (x + 260 * s, y + 420 * s), (x - 200 * s, y + 420 * s)], gown)
    p.poly([(x - 30 * s, y + 90 * s), (x + 50 * s, y + 90 * s), (x + 60 * s, y + 175 * s), (x - 40 * s, y + 175 * s)], ZSKIN)
    hx = x + sway
    p.ell(hx, y, 130 * s, 150 * s, ZSKIN, n=34)
    p.ell(hx + 70 * s, y + 4 * s, 22 * s, 34 * s, ZSKIN)
    p.poly([(hx - 128 * s, y - 10 * s), (hx - 156 * s, y + 30 * s), (hx - 124 * s, y + 40 * s)], ZSKIN)
    jaw = 6 * math.sin(t * 2 * math.pi * 0.3) * s
    p.ell(hx - 92 * s, y + 92 * s + jaw / 2, 18 * s, (16 * s + jaw), (40, 22, 22), w=3)
    p.ell(hx - 66 * s, y - 34 * s, 26 * s, 24 * s, (236, 238, 226), w=3)
    p.ell(hx - 80 * s, y - 34 * s, 4 * s, 4 * s, INK, w=0)
    for k in range(4):
        p.line([(hx - 40 * s + k * 40 * s, y - 140 * s), (hx - 20 * s + k * 42 * s, y - 120 * s)], w=2.5)


def zombie_back(p, x, y, s, t, seed, gown=(150, 160, 152), walk=None, legs=True):
    """Pacjent od tyłu (odchodzi w głąb). walk — zegar kroków albo None; legs=False — nogi rysuje kto inny (schody)."""
    ph = (walk if walk is not None else t * 0.4) * 5
    sway = math.sin(t * 3.1 + seed) * 5 * s
    step = math.sin(ph) * 8 * s if walk is not None else 0
    if legs:
        p.poly([(x - 22 * s, y - 70 * s), (x - 6 * s, y - 70 * s), (x - 8 * s, y + step), (x - 26 * s, y + step)], ZSKIN)
        p.poly([(x + 6 * s, y - 70 * s), (x + 22 * s, y - 70 * s), (x + 26 * s, y - step), (x + 8 * s, y - step)], ZSKIN)
    hx = x + sway
    p.poly([(hx - 44 * s, y - 192 * s), (hx + 44 * s, y - 192 * s), (x + 50 * s, y - 62 * s), (x - 50 * s, y - 62 * s)], gown)
    p.line([(hx, y - 190 * s), (x + 2 * s, y - 64 * s)], w=2.5)
    for side in (-1, 1):
        limb(p, (hx + side * 42 * s, y - 182 * s), (hx + side * 54 * s, y - 112 * s), 20 * s, gown)
        p.ell(hx + side * 54 * s, y - 108 * s, 12 * s, 12 * s, ZSKIN)
    p.ell(hx, y - 228 * s, 36 * s, 42 * s, ZSKIN)
    for k in range(3):
        p.line([(hx - 24 * s + k * 18 * s, y - 262 * s), (hx - 20 * s + k * 18 * s, y - 236 * s)], w=2.5)


# ---------- tła ----------

def duty_room(p, dark=True, glow=1.0):
    """Dyżurka z render2.room + drzwi z szybą (korytarz za nią świeci), biurko z telefonem."""
    R2.room(p, dark)
    p.rect(800, 120, 1060, 560, (104, 116, 104) if not dark else (70, 82, 84))
    p.rect(850, 170, 1010, 300, tuple(int(c * (0.6 + 0.4 * glow)) for c in (172, 190, 160)), w=5)
    p.rect(1030, 346, 1046, 392, (150, 150, 140), w=2.5)
    p.rect(470, 420, 790, 450, (110, 84, 60))
    p.rect(490, 450, 520, 560, (96, 72, 52))
    p.rect(740, 450, 770, 560, (96, 72, 52))


def desk_phone(p, handset=True):
    """Telefon na biurku dyżurki w skali planu ogólnego (jak w render2.scene2)."""
    p.poly([(600, 420), (680, 420), (672, 392), (608, 392)], (206, 196, 168), w=3)
    p.ell(640, 405, 12, 9, (172, 160, 128), w=2)
    if handset:
        p.poly([(596, 392), (684, 392), (680, 382), (600, 382)], (196, 186, 152), w=2.5)


def phone_detail(p, t, ring, handset="desk", hand=None):
    """Detal telefonu z tarczą (render2.scene4) w stanie po upadku słuchawki.
    handset: 'desk' — leży przed aparatem; (cx, cy, ang) — gdzie jest; hand — (x, y) dłoni trzymającej słuchawkę."""
    r = random.Random(int(t * R.FPS))
    j = 6 if ring else 0
    p.rect(0, 0, W, H, (44, 54, 62), w=0)
    p.rect(-20, 480, W + 20, H + 20, (92, 70, 52))
    p.line([(0, 480), (W, 480)], w=5)
    bx, by = 640 + r.uniform(-j, j), 460 + r.uniform(-j, j)
    p.poly([(bx - 220, by + 40), (bx + 220, by + 40), (bx + 170, by - 120), (bx - 170, by - 120)], (196, 184, 150))
    p.ell(bx, by - 30, 92, 80, (172, 160, 128))
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.3
        p.ell(bx + math.cos(a) * 60, by - 30 + math.sin(a) * 52, 12, 11, (60, 56, 50), w=2)
    p.ell(bx, by - 30, 24, 22, (220, 210, 180), w=3)
    for side in (-1, 1):
        p.poly([(bx + side * 140, by - 118), (bx + side * 160, by - 118), (bx + side * 156, by - 150), (bx + side * 144, by - 150)],
               (172, 160, 128), w=3)
    cx, cy, ang = (640 - 120, 460 + 78, -0.32) if handset == "desk" else handset

    def hs(px, py):
        return (cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang))

    p.line([(bx + 220, by + 20), (bx + 300, by + 80), (bx + 420, by + 60), (bx + 560, by + 140)], w=6)
    p.line([(bx - 200, by + 30), (cx - 150, cy + 60), (cx - 230, cy + 30)], w=5)  # kabel słuchawki
    p.poly([hs(-230, 22), hs(230, 22), hs(200, -22), hs(-200, -22)], (186, 174, 140))
    p.ell(*hs(-220, 18), 46, 34, (186, 174, 140), rot=ang)
    p.ell(*hs(220, 18), 46, 34, (186, 174, 140), rot=ang)
    if ring:
        ry = by - 150
        for side in (-1, 1):
            for k in range(3):
                x0 = bx + side * (290 + k * 30)
                p.line([(x0, ry - 60 + k * 10), (x0 + side * 24, ry - 90 + k * 6)], w=5)
        p.ell(bx + 150, by - 70, 12, 12, (220, 40, 40), w=3)
    if hand:  # rękaw z góry kadru i dłoń na słuchawce — bliżej kamery, więc rysowana na końcu
        hx, hy = hand
        limb(p, (hx + 260, -40), (hx + 40, hy - 10), 90, UNI, outline=4)
        p.ell(hx, hy, 70, 52, SKIN)
        for i in range(4):
            p.line([(hx - 40 + i * 24, hy - 10), (hx - 46 + i * 24, hy + 40)], w=3)


def keyhole(p, t, T, plate=(170, 160, 120), wall=(112, 126, 112), ring=False):
    """Detal zamka: klucz obraca się powoli, dłoń przed dziurką (render2.scene2). ring — pęk kluczy."""
    p.rect(0, 0, W, H, wall, w=0)
    p.rect(520, 140, 760, 600, plate)
    p.ell(640, 300, 46, 46, (60, 56, 48))
    p.ell(640, 480, 18, 30, (60, 56, 48))
    ang = ease(t / (T * 0.85)) * math.pi / 2 + 0.03 * noise(t, 62, 8)
    ca, sa = math.cos(ang), math.sin(ang)
    tx, ty = 3 * noise(t, 61, 7), 3 * noise(t, 63, 6)

    def rot(px, py):
        return (640 + tx + px * ca - py * sa, 300 + ty + px * sa + py * ca)

    p.poly([rot(-8, -10), rot(8, -10), rot(8, 120), rot(-8, 120)], (196, 176, 96))
    p.ell(*rot(0, 160), 46, 40, (196, 176, 96), rot=ang)
    p.ell(*rot(0, 160), 14, 12, wall, rot=ang)
    if ring:
        rx, ry = rot(0, 200)
        swing = 10 * math.sin(t * 3.4)
        p.ell(rx, ry + 30, 46, 38, None, w=5)
        for k, dx in enumerate((-30, 24)):
            kx, ky = rx + dx + swing * (k + 1) * 0.6, ry + 90
            p.poly([(kx - 6, ky - 20), (kx + 6, ky - 20), (kx + 6, ky + 50), (kx - 6, ky + 50)], (176, 176, 168), w=2.5)
            p.ell(kx, ky - 26, 16, 14, (176, 176, 168), w=2.5)
    hx, hy = rot(0, 170)
    p.ell(hx + 40, hy + 50, 90, 70, SKIN)
    for i in range(4):
        p.line([(hx - 30 + i * 22, hy + 10), (hx - 10 + i * 22, hy - 40)], w=22, color=SKIN)
        p.line([(hx - 30 + i * 22, hy + 10), (hx - 10 + i * 22, hy - 40)], w=2.5)
    limb(p, (hx + 120, hy + 90), (hx + 360, H + 80), 110, UNI, outline=4)


# ---------- klatka schodowa w osi biegu (5.11.2026: zamiast widoku z boku) ----------
# Schody z boku nie pasowały do postaci rysowanych od przodu: postacie przeskakiwały ze stopnia na stopień albo sunęły
# ukosem nad stopniami. Teraz kamera stoi u stóp biegu i patrzy w górę na podest (ten sam kadr, co „drzwi na szczycie
# schodów”). Schodzący idą na kamerę (figure, R.zombie — od przodu), wchodzący się oddalają (figure_back, zombie_back).
# Wszystko liczy się w metrach i rzutuje perspektywą, więc stopa stoi dokładnie na stopniu, a postać maleje
# z odległością. Krok = przeniesienie jednej stopy (st_moves); każda postać ma własny zegar kroków (st_clock).
ST_N, ST_R, ST_D, ST_W, ST_LAND = 12, 0.14, 0.26, 2.2, 1.4  # stopni do podestu, wysokość, głębokość, szerokość, podest
ST_TOP = ST_N * ST_R
ST_BACK = (ST_N - 1) * ST_D + ST_LAND  # ściana podestu (drzwi albo okno)
ST_PX = 1.75 / 388  # metry na piksel postaci w skali s=1 (figure: od podeszwy do czubka głowy ok. 388 px)
ST_ZS = 1.3  # zarażony (R.zombie, zombie_back) ma 270 px wzrostu — w tej samej odległości rysujemy go ×1,3
ST_RAIL = 0.8  # poręcz na lewej ścianie, nad linią krawędzi stopni
ST_CAMS = {
    "dol": {"e": (0.1, 1.7, -1.9), "f": 720, "c": (640, 270)},  # z piwnicy u stóp biegu (oczy stojącego), w górę na podest
    "drzwi": {"e": (0.0, 2.0, 1.9), "f": 700, "c": (640, 240)},  # z górnych stopni na dół drzwi i szparę (detal)
    "srodek": {"e": (0.05, 2.0, 0.2), "f": 700, "c": (640, 340)},  # z dolnych stopni na podest (plan średni)
    "gora": {"e": (0.05, 1.5, 0.9), "f": 700, "c": (640, 330)},  # nad górnymi stopniami (puszki na nitce, detal)
}
ST_WALL, ST_LAMP, ST_STEP, ST_RISE = (112, 124, 110), (72, 96, 84), (130, 132, 124), (100, 104, 98)
ST_CEIL, ST_FLOOR, ST_DOOR = (84, 92, 86), (82, 84, 80), (60, 66, 64)
_ST = {"cam": ST_CAMS["dol"], "dark": 0.0}


def st_proj(X, Y, Z, cam=None):
    """Punkt klatki (metry: X w prawo, Y w górę, Z w głąb biegu; Z=0 — pierwsze czoło stopnia) na kadr 1280×720."""
    cam = cam or _ST["cam"]
    (ex, ey, ez), f, (cx, cy) = cam["e"], cam["f"], cam["c"]
    d = max(0.08, Z - ez)
    return cx + f * (X - ex) / d, cy - f * (Y - ey) / d


def st_scale(Z, cam=None):
    """Skala figure() dla postaci stojącej na głębokości Z."""
    cam = cam or _ST["cam"]
    return cam["f"] * ST_PX / max(0.08, Z - cam["e"][2])


def st_nose(Z):
    """Wysokość linii krawędzi stopni (po niej biegnie poręcz): posadzka piwnicy → bieg → podest."""
    return min(ST_TOP, max(0.0, ST_R * (Z / ST_D + 1)))


def st_level(L):
    """(Y, Z) miejsca na stopę na poziomie L: ≤0 posadzka przed biegiem, 1..N-1 środek stopnia, ≥N podest."""
    def at(i):
        if i <= 0:
            return 0.0, -0.4 + 0.5 * i
        if i >= ST_N:
            return ST_TOP, min(ST_BACK - 0.25, (ST_N - 1) * ST_D + 0.35 + 0.45 * (i - ST_N))
        return i * ST_R, (i - 0.5) * ST_D
    i = math.floor(L)
    (y0, z0), (y1, z1) = at(i), at(i + 1)
    return y0 + (y1 - y0) * (L - i), z0 + (z1 - z0) * (L - i)


def _st_col(col, Z):
    """Dalej = ciemniej (bieg ginie w mroku), noc przyciemnia całość."""
    d = Z - _ST["cam"]["e"][2]
    k = (1 - 0.42 * min(1.0, max(0.0, (d - 1.5) / 5.5))) * (1 - 0.55 * _ST["dark"])
    return tuple(int(c * k) for c in col)


def _st_riser(p, i):
    """Czoło stopnia i (1..N; N — krawędź podestu)."""
    hw, z = ST_W / 2, (i - 1) * ST_D
    if z < _ST["cam"]["e"][2] + 0.3:
        return
    P = st_proj
    p.poly([P(-hw, (i - 1) * ST_R, z), P(hw, (i - 1) * ST_R, z), P(hw, i * ST_R, z), P(-hw, i * ST_R, z)],
           _st_col(ST_RISE, z), w=3)


def stair_flight(p, t, cam="dol", dark=0.0, top="drzwi", gap=1.0, shadow=0.0, glow=0.0, sky=(64, 74, 92), sign=True):
    """Bieg schodów z piwnicy na podest w osi kamery. top: „drzwi” (drzwi parteru ze szparą światła; shadow -1..1 —
    cień w szparze) albo „okno” (okno półpiętra na piętrach, kolor nieba sky). glow — poświata z góry."""
    cam = ST_CAMS[cam] if isinstance(cam, str) else cam
    _ST.update(cam=cam, dark=dark)
    P = st_proj
    ey, zn = cam["e"][1], cam["e"][2] + 0.3
    hw = ST_W / 2
    zl = (ST_N - 1) * ST_D  # krawędź podestu
    zs = [z for z in (zn, -ST_D, zl, ST_BACK) if z >= zn]
    p.rect(-400, -400, W + 400, H + 400, _st_col(ST_CEIL, 3.0), w=0)  # sufit i spód wyższego biegu
    # ściana podestu
    p.poly([P(-hw, ST_TOP - 0.1, ST_BACK), P(hw, ST_TOP - 0.1, ST_BACK), P(hw, ST_TOP + 2.5, ST_BACK),
            P(-hw, ST_TOP + 2.5, ST_BACK)], _st_col(ST_WALL, ST_BACK), w=3)
    p.poly([P(-hw, ST_TOP - 0.1, ST_BACK), P(hw, ST_TOP - 0.1, ST_BACK), P(hw, ST_TOP + 1.05, ST_BACK),
            P(-hw, ST_TOP + 1.05, ST_BACK)], _st_col(ST_LAMP, ST_BACK), w=2)  # lamperia
    if top == "drzwi":
        d0, d1 = P(-0.45, ST_TOP, ST_BACK), P(0.45, ST_TOP + 1.95, ST_BACK)
        p.rect(d0[0], d1[1], d1[0], d0[1], _st_col(ST_DOOR, ST_BACK), w=3)
        hx, hy = P(0.33, ST_TOP + 1.0, ST_BACK)
        p.line([(hx, hy), (hx - 14, hy)], w=4)  # klamka
        if gap:  # szpara światła pod drzwiami (MASTER: na górze zawsze szpara światła)
            g0, g1 = P(-0.44, ST_TOP, ST_BACK), P(0.44, ST_TOP + 0.045, ST_BACK)
            p.rect(g0[0], g1[1], g1[0], g0[1], tuple(int(c * (0.55 + 0.45 * gap)) for c in (214, 222, 188)), w=0)
            p.glow([g0, (g1[0], g0[1]), P(0.7, ST_TOP, ST_BACK - 0.9), P(-0.7, ST_TOP, ST_BACK - 0.9)],
                   (200, 210, 170, int(34 * gap)))
            if shadow and abs(shadow) < 1.25:  # cień przechodzi w szparze i kładzie się smugą na podeście
                xa, xb = max(-0.44, 0.44 * shadow - 0.1), min(0.44, 0.44 * shadow + 0.1)
                if xb > xa:
                    a, b = P(xa, ST_TOP, ST_BACK), P(xb, ST_TOP + 0.045, ST_BACK)
                    p.rect(a[0], b[1], b[0], a[1], (20, 22, 22), w=0)
                    p.glow([a, P(xb, ST_TOP, ST_BACK), P(xb * 1.6, ST_TOP, ST_BACK - 0.9), P(xa * 1.6, ST_TOP, ST_BACK - 0.9)],
                           (0, 0, 0, 70))
        if sign:  # zielony znak wyjścia awaryjnego nad drzwiami
            s0, s1 = P(-0.2, ST_TOP + 2.01, ST_BACK), P(0.2, ST_TOP + 2.16, ST_BACK)
            p.rect(s0[0], s1[1], s1[0], s0[1], (120, 200, 140) if dark < 0.8 else (90, 150, 104), w=2.5)
            p.glow([(s0[0] - 30, s1[1] - 20), (s1[0] + 30, s1[1] - 20), (s1[0] + 90, s0[1] + 120), (s0[0] - 90, s0[1] + 120)],
                   (120, 220, 150, 34))
    else:  # okno półpiętra
        w0, w1 = P(-0.5, ST_TOP + 0.95, ST_BACK), P(0.5, ST_TOP + 2.15, ST_BACK)
        sky = tuple(int(c * (1 - 0.3 * dark)) for c in sky)
        p.rect(w0[0], w1[1], w1[0], w0[1], sky, w=4)
        mx, my = (w0[0] + w1[0]) / 2, (w0[1] + w1[1]) / 2
        p.line([(mx, w1[1]), (mx, w0[1])], w=4)
        p.line([(w0[0], my), (w1[0], my)], w=4)
        p.glow([w0, (w1[0], w0[1]), P(0.75, ST_TOP, ST_BACK - 1.6), P(-0.75, ST_TOP, ST_BACK - 1.6)], (*sky, 46))
    if glow:
        p.glow([P(-hw, ST_TOP + 2.5, ST_BACK), P(hw, ST_TOP + 2.5, ST_BACK), P(hw, ST_TOP, ST_BACK - 2.5),
                P(-hw, ST_TOP, ST_BACK - 2.5)], (140, 230, 160, int(40 * glow)))
    # ściany boczne z lamperią (olejna farba do 1 m nad stopniami)
    for X in (-hw, hw):
        p.poly([P(X, st_nose(z) + 2.5, z) for z in zs] + [P(X, -0.3, z) for z in reversed(zs)], _st_col(ST_WALL, 2.0), w=0)
        p.poly([P(X, st_nose(z) + 1.25, z) for z in zs] + [P(X, -0.3, z) for z in reversed(zs)], _st_col(ST_LAMP, 2.0), w=0)
        p.line([P(X, st_nose(z) + 1.25, z) for z in zs], w=2.5)
        p.line([P(X, st_nose(z) + 2.5, z) for z in zs], w=3)  # styk ściany z sufitem
        p.line([P(X, -0.3, ST_BACK), P(X, ST_TOP + 2.5, ST_BACK)], w=3)  # narożnik podestu
    if top == "okno":  # na półpiętrze bieg skręca w prawo, w górę: stąd schodzą z wyższych pięter
        za, zb = zl + 0.2, ST_BACK - 0.05
        p.poly([P(hw, ST_TOP - 0.3, za), P(hw, ST_TOP - 0.3, zb), P(hw, ST_TOP + 2.4, zb), P(hw, ST_TOP + 2.4, za)],
               _st_col((44, 50, 48), ST_BACK), w=3)
        for j in range(1, 6):  # pierwsze stopnie wyższego biegu w przejściu
            y = ST_TOP + j * ST_R
            p.line([P(hw, y, za + 0.02), P(hw, y, zb - 0.02)], w=2.5, color=_st_col((96, 100, 94), ST_BACK))
    for X, z, y, pts in ((hw, 1.3, 1.75, ((0, 0), (0.18, -0.1), (0.3, -0.06), (0.5, -0.2))),  # pęknięcie tynku
                         (-hw, 0.4, 1.7, ((0, 0), (0.12, 0.08), (0.2, 0.02), (0.36, 0.14))),
                         (hw, 2.4, 1.3, ((0, 0), (0.1, -0.12), (0.24, -0.1)))):
        if z > zn + 0.2:
            p.line([P(X, st_nose(z) + y + dy, z + dz) for dz, dy in pts], w=2, color=(52, 58, 54))
    # podest i stopnie od najdalszego; stopnie powyżej oka widać tylko od czoła
    if ST_TOP < ey:
        p.poly([P(-hw, ST_TOP, max(zl, zn)), P(hw, ST_TOP, max(zl, zn)), P(hw, ST_TOP, ST_BACK), P(-hw, ST_TOP, ST_BACK)],
               _st_col(ST_STEP, ST_BACK), w=3)
    for i in range(ST_N, 0, -1):
        z0, z1 = (i - 1) * ST_D, i * ST_D
        if i < ST_N and i * ST_R < ey and z1 > zn:
            p.poly([P(-hw, i * ST_R, max(z0, zn)), P(hw, i * ST_R, max(z0, zn)), P(hw, i * ST_R, z1), P(-hw, i * ST_R, z1)],
                   _st_col(ST_STEP, z1), w=3)
        _st_riser(p, i)
    if zn < 0:  # posadzka piwnicy u stóp biegu
        p.poly([P(-hw - 2, 0, zn), P(hw + 2, 0, zn), P(hw, 0, 0), P(-hw, 0, 0)], _st_col(ST_FLOOR, 0.0), w=0)
        p.line([P(-hw, 0, 0), P(hw, 0, 0)], w=3)
    # poręcz na lewej ścianie (zawsze nad stopniami — stopnie jej nie zasłaniają)
    xr = -hw + 0.07
    rail = [P(xr, st_nose(z) + ST_RAIL, z) for z in zs[:-1] + [ST_BACK - 0.1]]
    p.line(rail, w=7)
    p.line(rail, w=3, color=(118, 96, 70))
    z = math.ceil((zn + 0.3) / 0.9) * 0.9
    while z < ST_BACK - 0.2:  # wsporniki
        y = st_nose(z) + ST_RAIL
        p.line([P(xr, y, z), P(xr, y - 0.07, z), P(-hw, y - 0.07, z)], w=3)
        z += 0.9


def st_moves(a, b, kind="alt", lead="l"):
    """Kroki z poziomu a na b (na starcie obie stopy na a): lista (stopa, skąd, dokąd).
    alt — stopy na zmianę, każda mija drugą (zwykły chód); dost — krok dostawny: prowadząca stopa schodzi,
    druga do niej dostawia (ostrożnie, z ciężarem, zarażony bez równowagi)."""
    d = 1 if b > a else -1
    other = "r" if lead == "l" else "l"
    if kind == "dost":
        return [m for L in range(a, b, d) for m in ((lead, L, L + d), (other, L, L + d))]
    feet, out, f = {"l": a, "r": a}, [], lead
    while feet["l"] != b or feet["r"] != b:
        o = "r" if f == "l" else "l"
        to = min(feet[o] + d, b) if d > 0 else max(feet[o] + d, b)
        out.append((f, feet[f], to))
        feet[f], f = to, o
    return out


def st_clock(t, n, step, hold=0.0, t0=0.0, jitter=0.0, seed=0):
    """Ile z n kroków zrobiono w chwili t (ułamek — krok w toku): krok trwa `step` s, po nim postój `hold` s;
    jitter 0..1 — nierówne tempo (zarażeni: każdy krok inny)."""
    r = random.Random(seed)
    t -= t0
    for i in range(n):
        m = step * (1 + jitter * r.uniform(-1, 1))
        h = hold * (1 + jitter * r.uniform(-1, 1))
        if t < m:
            return i + max(0.0, t) / m
        if t < m + h:
            return i + 1.0
        t -= m + h
    return float(n)


def st_pose(moves, k, a):
    """Stopy po k krokach z poziomu a: ({'l': (Y, Z), 'r': (Y, Z)}, (stopa w powietrzu, faza) albo None)."""
    lv = {"l": a, "r": a}
    n = int(k)
    for f, _, L1 in moves[:n]:
        lv[f] = L1
    feet = {f: st_level(L) for f, L in lv.items()}
    fr = k - n
    if n >= len(moves) or fr <= 0:
        return feet, None
    f, L0, L1 = moves[n]
    (y0, z0), (y1, z1) = st_level(L0), st_level(L1)
    e = fr * fr * (3 - 2 * fr)
    if y1 < y0:  # w dół: stopa najpierw wysuwa się nad krawędź, potem opada na niższy stopień
        zf, yf = 1 - (1 - e) ** 2, e * e
    elif y1 > y0:  # w górę: najpierw się unosi, potem wchodzi na stopień
        zf, yf = e * e, 1 - (1 - e) ** 2
    else:
        zf = yf = e
    feet[f] = (y0 + (y1 - y0) * yf + 0.07 * math.sin(math.pi * fr), z0 + (z1 - z0) * zf)
    return feet, (f, fr)


def _leg(p, a, k, b, w0, w1, col):
    """Noga jednym konturem: biodro a → kolano k → kostka b (bez szwu w kolanie)."""
    def n(u, v, w):
        dx, dy = v[0] - u[0], v[1] - u[1]
        L = math.hypot(dx, dy) or 1.0
        return -dy / L * w / 2, dx / L * w / 2
    n0, n2 = n(a, k, w0), n(k, b, w1)
    nk = ((n0[0] + n2[0]) / 2, (n0[1] + n2[1]) / 2)
    p.poly([(a[0] + n0[0], a[1] + n0[1]), (k[0] + nk[0], k[1] + nk[1]), (b[0] + n2[0], b[1] + n2[1]),
            (b[0] - n2[0], b[1] - n2[1]), (k[0] - nk[0], k[1] - nk[1]), (a[0] - n0[0], a[1] - n0[1])], col, w=3)


def st_person(p, t, feet, swing, x, who, back=False, zombie=False, gown=(168, 178, 172), seed=0, tilt=0.0, rail=False,
              arms=None, lean=0.0, kneel=None, drop=1.0, blood=0.0, **kw):
    """Postać na schodach: stopy z st_pose (metry), x — odległość od osi biegu. Nogi liczone w przestrzeni
    (kolano zgina się w stronę ruchu), tułów z figure / figure_back / R.zombie / zombie_back bez nóg.
    Stopa na stopniu powyżej oka chowa się za jego krawędzią (czoło stopnia rysujemy ponownie).
    rail — dłoń na poręczy (lewa ściana); kneel — stopa ('l'/'r'), która klęka (kolano na stopniu), drop 0..1 —
    jak daleko już opadła, blood 0..1 — rozcięte kolano. Zwraca dłonie (figure, figure_back) albo {'x', 'y', 's'} tułowia zarażonego."""
    ey = _ST["cam"]["e"][1]
    leg = (70 * ST_ZS if zombie else 120) * ST_PX
    zh = sum(z for _, z in feet.values()) / 2
    yh = min(y + math.sqrt(max(0.0, (leg * 0.97) ** 2 - (z - zh) ** 2)) for y, z in feet.values())
    if kneel:
        yh += (feet[kneel][0] + leg * 0.5 - yh) * drop
    s = st_scale(zh)
    sb = s * ST_ZS if zombie else s
    hx, hy = st_proj(x, yh, zh)
    ybody = hy + (70 if zombie else 120) * sb
    fwd = 1 if back else -1
    om = (14 * ST_ZS if zombie else 18) * ST_PX
    c = None if zombie else _costume(who)
    col = ZSKIN if zombie else c["bottom"]
    for f in sorted(feet, key=lambda f: -feet[f][1]):  # dalsza stopa pierwsza
        side = -1 if f == "l" else 1
        X = x + side * om
        fy, fz = feet[f]
        if f == kneel:  # kolano opada na stopień, łydka za nim (od przodu jej nie widać)
            fy, fz = fy + 0.02 * drop, fz - 0.1 * fwd * drop
        vy, vz = fy - yh, fz - zh
        d = math.hypot(vy, vz) or 1e-6
        if f == kneel or d >= leg * 0.995:
            ky, kz = yh + vy / 2, zh + vz / 2
        else:
            hk = math.sqrt((leg / 2) ** 2 - (d / 2) ** 2)
            ny, nz = -vz / d, vy / d
            if nz * fwd < 0:
                ny, nz = -ny, -nz
            ky, kz = yh + vy / 2 + ny * hk, zh + vz / 2 + nz * hk
        a, kp, b = st_proj(X, yh, zh), st_proj(X, ky, kz), st_proj(X, fy, fz)
        sf = st_scale(fz) * (ST_ZS if zombie else 1)
        if zombie:
            _leg(p, a, kp, b, 16 * sb, 17 * sf, col)
            p.ell(b[0], b[1] - 4 * sf, 12 * sf, 6 * sf, ZSKIN, w=2.5)
        elif f == kneel:
            _leg(p, a, kp, b, 32 * s, 30 * sf, col)
            p.ell(b[0], b[1] - 6 * sf, 17 * sf, 12 * sf, col, w=3)  # kolano na krawędzi stopnia
            if blood:
                p.ell(b[0] + 2 * sf, b[1] - 6 * sf, 11 * sf * blood, 8 * sf * blood, (170, 36, 36), w=0)
        else:
            ux, uy, vx, vy = a[0] - kp[0], a[1] - kp[1], b[0] - kp[0], b[1] - kp[1]
            fold = (ux * vx + uy * vy) / ((math.hypot(ux, uy) * math.hypot(vx, vy)) or 1.0)
            shoe = lambda: p.ell(b[0], b[1] - 8 * sf, 18 * sf, (9 if back else 10) * sf, c["shoes"], w=3)
            if fold > -0.35:  # mocno zgięta noga: udo i łydka osobno, bliższa część rysowana później
                sk = st_scale(kz)
                parts = [((zh + kz) / 2, lambda: limb(p, a, kp, 32 * s, col)),
                         ((kz + fz) / 2, lambda: (shoe(), limb(p, kp, b, 28 * sf, col)))]
                for _, draw in sorted(parts, key=lambda q: -q[0]):
                    draw()
                p.ell(kp[0], kp[1], 15 * sk, 13 * sk, col, w=3)  # kolano
            else:
                _leg(p, a, kp, b, 32 * s, 28 * sf, col)
                shoe()
        if who == "narrator" and NARRATOR_KNEE and side < 0 and f != kneel:
            p.rect(kp[0] - 15 * s, kp[1] - 10 * s, kp[0] + 15 * s, kp[1] + 10 * s, WHITE, w=2)
        j = max(1, min(ST_N, int(fz // ST_D) + 1))
        if fz > (j - 1) * ST_D and j * ST_R > ey:
            _st_riser(p, j)  # krawędź stopnia zasłania podeszwę
    if arms is None and not zombie:
        sw = math.sin(math.pi * swing[1]) if swing else 0.0
        arms = {k: (sd * 14, 95 + (8 * sw if swing and swing[0] != k else -4 * sw)) for k, sd in (("l", -1), ("r", 1))}
    if rail and not zombie:
        zr = zh + 0.14 * fwd
        rx, ry = st_proj(-ST_W / 2 + 0.07, st_nose(zr) + ST_RAIL, zr)
        sx, sy = hx + lean * 20 * s - 50 * s, ybody - 268 * s
        arms = {**arms, "l": ((rx - sx) / s, (ry - sy) / s)}
    if zombie:
        if back:
            zombie_back(p, hx, ybody, sb, t, seed, gown=gown, legs=False)
        else:
            R.zombie(p, hx, ybody, sb, t, seed, gown=gown, tilt=tilt, legs=False, **kw)
        return {"x": hx, "y": ybody, "s": sb}
    if back:
        hands = figure_back(p, hx, ybody, s, t, who, arms=arms, legs=False)
    else:
        hands = figure(p, hx, ybody, s, t, who, arms=arms, lean=lean, legs=False, **kw)
    return {**hands, "s": s}


def st_walker(p, t, who, a, b, step, x=0.0, t0=0.0, kind="alt", lead="l", hold=0.0, jitter=0.0, seed=0, **kw):
    """Postać idąca po schodach z poziomu a na b: w dół od przodu, w górę od tyłu. Zwraca dłonie (figure)."""
    moves = st_moves(a, b, kind, lead)
    k = st_clock(t, len(moves), step, hold, t0, jitter, seed)
    feet, swing = st_pose(moves, k, a)
    return st_person(p, t, feet, swing, x, who, back=b > a, seed=seed, **kw)


def st_group(p, t, walkers):
    """Kilka postaci na schodach naraz (dict-y z argumentami st_walker: who, a, b, step, x, t0, kind, lead, hold,
    jitter, seed i reszta dla st_person). Każda ma własny zegar; rysujemy od najdalszej. Zwraca wyniki w kolejności."""
    poses = []
    for i, w in enumerate(walkers):
        w = dict(w)
        a, b = w.pop("a"), w.pop("b")
        moves = st_moves(a, b, w.pop("kind", "alt"), w.pop("lead", "l"))
        k = st_clock(t, len(moves), w.pop("step"), w.pop("hold", 0.0), w.pop("t0", 0.0), w.pop("jitter", 0.0),
                     w.get("seed", 0))
        feet, swing = st_pose(moves, k, a)
        poses.append((sum(z for _, z in feet.values()), i, feet, swing, b > a, w))
    out = [None] * len(walkers)
    for _, i, feet, swing, back, w in sorted(poses, key=lambda q: -q[0]):
        out[i] = st_person(p, t, feet, swing, w.pop("x", 0.0), w.pop("who", None), back=back, **w)
    return out


def st_can(p, X, Y, Z, rot=0.0, col=(180, 186, 190)):
    """Puszka po konserwie (7 × 10 cm), środek w (X, Y, Z); rot — obrót w kadrze (spada, toczy się)."""
    cx, cy = st_proj(X, Y, Z)
    f = _ST["cam"]["f"] / max(0.08, Z - _ST["cam"]["e"][2])
    w, h, c, sn = 0.035 * f, 0.05 * f, math.cos(rot), math.sin(rot)
    q = lambda dx, dy: (cx + dx * c - dy * sn, cy + dx * sn + dy * c)
    p.poly([q(-w, -h), q(w, -h), q(w, h), q(-w, h)], _st_col(col, Z), w=3)
    p.line([q(-w, -h * 0.2), q(w, -h * 0.2)], w=1.5)
    p.ell(*q(0, -h), w, w * 0.32, _st_col((206, 210, 212), Z), w=2.5, rot=rot)


CAN_TREAD, CAN_X = 9, (-0.78, -0.4, -0.02, 0.38, 0.76)  # pułapka z d06: nitka nad 9. stopniem, pięć puszek
CAN_Y, CAN_Z = CAN_TREAD * ST_R + 0.2, (CAN_TREAD - 1) * ST_D + 0.06


def can_trap(p, t, broken=False):
    """Nitka od ściany do ściany na wysokości kostki nad stopniem CAN_TREAD; puszki wiszą tuż nad stopniem.
    broken — po zerwaniu zostają tylko końce nitki zwisające przy ścianach (puszki rysuje ujęcie)."""
    P, hw = st_proj, ST_W / 2
    if broken:
        for X, d in ((-hw, 1), (hw, -1)):
            p.line([P(X, CAN_Y, CAN_Z), P(X + d * 0.12, CAN_Y - 0.1, CAN_Z), P(X + d * 0.16, CAN_Y - 0.18, CAN_Z)],
                   w=2, color=(240, 240, 230), amp=0.4)
        return
    p.line([P(-hw, CAN_Y, CAN_Z), P(0, CAN_Y - 0.03, CAN_Z), P(hw, CAN_Y, CAN_Z)], w=2, color=(240, 240, 230), amp=0.4)
    for i, x in enumerate(CAN_X):
        sw = 0.012 * math.sin(t * 2 + i)
        p.line([P(x, CAN_Y - 0.03 * (1 - abs(x) / hw), CAN_Z), P(x + sw, CAN_Y - 0.07, CAN_Z)], w=1.5, color=(240, 240, 230))
        st_can(p, x + sw, CAN_Y - 0.12, CAN_Z, rot=sw * 4)


def stairwell(p, t, **kw):
    """Klatka schodowa główna z piwnicy na parter (zgodność ze starymi wywołaniami)."""
    stair_flight(p, t, **kw)


def basement(p, t, flick=1.0, vp=(640, 340)):
    """Korytarz piwnicy w perspektywie: beton, rury pod sufitem, na końcu krata apteki z pękniętą lampą."""
    vx, vy = vp
    bx0, by0, bx1, by1 = vx - 150, vy - 100, vx + 150, vy + 100
    p.rect(0, 0, W, H, (70, 76, 80), w=0)
    p.poly([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], (58, 62, 66))
    p.poly([(0, H), (W, H), (bx1, by1), (bx0, by1)], (78, 80, 78))
    p.poly([(0, 0), (bx0, by0), (bx0, by1), (0, H)], (88, 94, 96))
    p.poly([(W, 0), (bx1, by0), (bx1, by1), (W, H)], (84, 90, 92))
    for k, (ox, oy) in enumerate(((-40, 18), (0, 34), (60, 22))):
        p.line([(vx + ox * 5.5, -10 + oy), (vx + ox, by0 + oy * 0.4)], w=10 - 2 * k, color=(110, 104, 96))
        p.line([(vx + ox * 5.5, -10 + oy), (vx + ox, by0 + oy * 0.4)], w=2)
    lit = tuple(int(c * flick) for c in (178, 170, 132))
    p.rect(bx0, by0, bx1, by1, lit)
    for i in range(4):  # półki apteki
        p.line([(bx0 + 20, by0 + 40 + i * 40), (bx1 - 20, by0 + 40 + i * 40)], w=3, color=(100, 90, 70))
        for k in range(8):
            p.rect(bx0 + 28 + k * 32, by0 + 22 + i * 40, bx0 + 50 + k * 32, by0 + 40 + i * 40,
                   ((150, 120, 110), (120, 140, 150), (190, 186, 170))[(k + i) % 3], w=1.5)
    p.ell(vx, by0 + 14, 20, 10, (236, 230, 190) if flick > 0.9 and MAINS else (150, 146, 120), w=2)
    p.line([(vx - 8, by0 + 8), (vx + 2, by0 + 16), (vx - 4, by0 + 22)], w=1.5)
    for i in range(11):
        xx = bx0 + 6 + i * 29
        p.line([(xx, by0), (xx, by1)], w=4, color=(50, 52, 54))
    p.line([(bx0, vy), (bx1, vy)], w=4, color=(50, 52, 54))
    p.rect(bx0, by0, bx1, by1, None, w=6)


def pharmacy_front(p, t, flick=1.0):
    """Apteka od frontu (za kratą): regały z pudełkami, pęknięta lampa pod sufitem."""
    p.rect(0, 0, W, H, tuple(int(c * flick) for c in (150, 146, 120)), w=0)
    p.rect(-20, 600, W + 20, H + 20, (96, 94, 86))
    p.line([(0, 600), (W, 600)], w=4)
    for i in range(4):
        y0 = 140 + i * 110
        p.rect(80, y0 + 90, 1200, y0 + 104, (120, 100, 74))
        for k in range(18):
            x0 = 96 + k * 60
            p.rect(x0, y0 + 30 + (k * 7) % 20, x0 + 44, y0 + 90, ((170, 130, 116), (120, 146, 160), (200, 196, 176), (150, 170, 130))[(k + i) % 4], w=2)
    p.line([(640, -10), (640, 70)], w=3)
    p.ell(640, 90, 60, 26, (240, 232, 190) if flick > 0.9 and MAINS else (160, 154, 126), w=3)
    p.line([(610, 80), (634, 94), (622, 104)], w=2)


def grille(p, x0, y0, x1, y1, gap=64, bar=10, col=(60, 64, 66)):
    """Krata apteki — zawsze przed postacią (rysować na końcu)."""
    x = x0
    while x <= x1:
        p.line([(x, y0), (x, y1)], w=bar, color=col)
        p.line([(x, y0), (x, y1)], w=2)
        x += gap
    for yy in (y0 + 10, (y0 + y1) / 2, y1 - 10):
        p.line([(x0, yy), (x1, yy)], w=bar, color=col)
        p.line([(x0, yy), (x1, yy)], w=2)


def clip_seg(a, b, x0, y0, x1, y1):
    """Odcinek przycięty do prostokąta (Liang–Barsky) albo None."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for pp, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if pp == 0:
            if q < 0:
                return None
            continue
        r = q / pp
        if pp < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 > t1:
            return None
    return (a[0] + dx * t0, a[1] + dy * t0), (a[0] + dx * t1, a[1] + dy * t1)


def mesh(p, x0=500, y0=140, x1=780, y1=340):
    """Siatka w okienku izolatki (jak w render.scene3), przycięta do okienka — rysować po tym, co za nią."""
    for i in range(-6, 12):
        for a, b in (((500 + i * 40, 140), (500 + i * 40 + 200, 340)), ((500 + i * 40 + 200, 140), (500 + i * 40, 340))):
            seg = clip_seg(a, b, x0, y0, x1, y1)
            if seg:
                p.line(list(seg), w=1.5, color=(80, 90, 84), amp=0.6)
    p.rect(498, 138, 782, 342, None, w=6)


# ---------- dni 2–5 ----------

def pharmacy_inside(p, t, flick=1.0, dark=0.0):
    """Apteka od środka: regały, lada z lewej, krata z prawej, wysokie okienko pod sufitem."""
    def c(col):
        k = flick * (1 - 0.75 * dark)
        return tuple(int(v * k) for v in col)
    p.rect(0, 0, W, H, c((150, 146, 120)), w=0)
    p.rect(-20, 560, W + 20, H + 20, c((96, 94, 86)))
    p.line([(0, 560), (W, 560)], w=4)
    for i in range(3):
        y0 = 200 + i * 110
        p.rect(300, y0 + 80, 880, y0 + 92, c((120, 100, 74)))
        for k in range(9):
            x0 = 312 + k * 62
            p.rect(x0, y0 + 26 + (k * 7) % 18, x0 + 46, y0 + 80, c(((170, 130, 116), (120, 146, 160), (200, 196, 176))[(k + i) % 3]), w=2)
    p.rect(90, 60, 250, 140, c((200, 210, 200)) if dark < 0.5 else c((40, 46, 56)), w=4)  # okienko pod sufitem
    for k in range(1, 4):
        p.line([(90 + k * 40, 60), (90 + k * 40, 140)], w=3)
    p.rect(-20, 430, 270, 600, c((128, 98, 70)))  # lada
    p.line([(-20, 430), (270, 430)], w=4)
    grille(p, 940, 60, W + 40, 600, gap=60, bar=10, col=c((60, 64, 66)))
    p.ell(640, 70, 50, 20, (240, 232, 190) if flick > 0.9 and dark < 0.5 and MAINS else c((150, 146, 120)), w=3)


def truck_side(p, x, col=(86, 100, 70)):
    """Ciężarówka wojska z boku w planie przez okienko (yard_trucks): x — środek paki."""
    p.rect(x - 130, 330, x + 60, 460, col)
    p.rect(x + 60, 370, x + 150, 460, tuple(int(c * 0.9) for c in col))
    p.rect(x + 80, 380, x + 130, 410, (170, 186, 180), w=3)
    for wx in (x - 90, x + 20, x + 110):
        p.ell(wx, 462, 26, 26, (36, 36, 34))


def yard_trucks(p, t, soldiers=True, wire=0.0, trucks=None, moving=()):
    """Widok przez okienko piwnicy: płot z siatki, brama, ciężarówki wojska, las. wire 0..1 — rozwinięte zasieki.
    trucks — stojące ciężarówki (domyślnie trzy; od nocy dnia 18 została jedna z trzech — księga świata);
    moving — x ciężarówek w ruchu (rysowane jak stojące)."""
    if trucks is None:
        trucks = (180, 640, 1000) if DAY <= 18 else (180,)
    p.rect(0, 0, W, H, (150, 160, 158), w=0)
    p.poly([(0, 300), (W, 280), (W, H), (0, H)], (98, 110, 88))
    for k in range(9):  # las
        x = k * 160 - 40
        p.poly([(x, 300), (x + 80, 150), (x + 160, 300)], (52, 70, 60))
    for x in tuple(trucks) + tuple(moving):  # ciężarówki
        truck_side(p, x)
    if soldiers:
        for k, x in enumerate((340, 470, 820)):
            figure(p, x + 6 * math.sin(t + k), 560, 0.42, t, "soldier", arms={"r": (30, 40)})
    for x in range(0, W + 1, 36):  # siatka płotu przed nimi
        p.line([(x, 470), (x + 36, 600)], w=1.5, color=(70, 76, 72), amp=0.4)
        p.line([(x + 36, 470), (x, 600)], w=1.5, color=(70, 76, 72), amp=0.4)
    for x in (0, 320, 640, 960, 1280):
        p.line([(x, 450), (x, 610)], w=6, color=(60, 62, 60))
    p.line([(0, 470), (W, 470)], w=4, color=(60, 62, 60))
    if wire > 0:
        n = int(14 * wire)
        for k in range(n):
            p.ell(40 + k * 90, 600, 46, 26, None, w=3)


def basement_window(p, inner):
    """Okienko piwnicy z kratą: inner(p) rysuje widok, ściana zasłania wszystko poza otworem."""
    inner(p)
    wall = (96, 100, 96)
    for x0, y0, x1, y1 in ((-50, -50, 200, H + 50), (1080, -50, W + 50, H + 50), (200, -50, 1080, 140), (200, 580, 1080, H + 50)):
        p.rect(x0, y0, x1, y1, wall, w=0, amp=0)
    for k in range(1, 6):
        p.line([(200 + k * 147, 140), (200 + k * 147, 580)], w=12, color=(56, 58, 58))
    p.rect(200, 140, 1080, 580, None, w=8)


def wall_line(i, txt, size, ry):
    """Lewy początek i wysokość i-tej linii zasad na ścianie (napis rośnie od lewej, jak przy pisaniu)."""
    from PIL import ImageFont
    f = ImageFont.truetype(R.FONT_B, size)
    return 640 - f.getlength(txt) / 2 + (i % 2) * 18 - 9, 110 + i * 100 + ry, f


def wall_text(p, lines, k=1.0):
    """Betonowa ściana z odręcznymi zasadami; ostatnia linia odsłaniana w miarę pisania (k 0..1).
    Zwraca (x, y) końca pisanej linii — tam jest marker."""
    from PIL import ImageFont
    p.rect(0, 0, W, H, (142, 140, 128), w=0)
    for i in range(7):
        p.line([(120 + i * 170, 40 + (i * 37) % 60), (150 + i * 170, 90 + (i * 53) % 70)], w=2, color=(110, 108, 98))
    end = (640, 360)
    lines = [(R.tr(txt), size, ry) for txt, size, ry in lines]  # wersja językowa filmu
    for i, (txt, size, ry) in enumerate(lines):
        show = txt if i < len(lines) - 1 else txt[:max(0, int(round(len(txt) * k)))]
        x0, y, f = wall_line(i, txt, size, ry)
        if show:
            fz = ImageFont.truetype(R.FONT_B, int(size * p.zoom * R.SS))
            p.d.text(p.tp((x0, y)), show, font=fz, fill=(28, 26, 26), anchor="lm")
        end = (x0 + f.getlength(show), y)
    return end


def connector(p, t, vp=(820, 330)):
    """Łącznik: długi korytarz, po lewej wysokie okna na podwórze z płotem."""
    vx, vy = vp
    bx0, by0, bx1, by1 = vx - 90, vy - 70, vx + 90, vy + 70
    p.rect(0, 0, W, H, (150, 160, 150), w=0)
    p.poly([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], (170, 176, 166))
    p.poly([(0, H), (W, H), (bx1, by1), (bx0, by1)], (110, 112, 104))
    p.poly([(W, 0), (bx1, by0), (bx1, by1), (W, H)], (150, 166, 150))
    p.poly([(0, 0), (bx0, by0), (bx0, by1), (0, H)], (130, 146, 132))
    p.rect(bx0, by0, bx1, by1, (60, 66, 62))
    for k, f in enumerate((0.0, 0.3, 0.55, 0.75)):  # okna na lewej ścianie
        f2 = f + 0.18

        def at(ff, yy):
            top, bot = by0 * ff, H + (by1 - H) * ff
            return (bx0 * ff, top + (bot - top) * yy)
        a, b, c2, d = at(f, 0.15), at(f2, 0.15), at(f2, 0.7), at(f, 0.7)
        p.poly([a, b, c2, d], (196, 206, 200))
        p.line([(a[0] + (b[0] - a[0]) * 0.1, a[1] + (d[1] - a[1]) * 0.55), (b[0], b[1] + (c2[1] - b[1]) * 0.55)], w=2,
               color=(80, 90, 84))  # płot za oknem
        p.poly([a, b, c2, d], None, w=4)
    for i in range(1, 7):
        f = (i / 7) ** 1.8
        yy = by1 + (H - by1) * f
        p.line([(bx0 * (1 - f), yy), (bx1 + (W - bx1) * f, yy)], w=2, color=(84, 88, 80))


def kitchen(p, t):
    """Kuchnia szpitalna: kafelki, kotły na kuchni, drzwi chłodni z okienkiem po prawej."""
    p.rect(0, 0, W, H, (196, 204, 198), w=0)
    for x in range(0, W, 60):
        p.line([(x, 0), (x, 470)], w=1.5, color=(160, 168, 162), amp=0.4)
    for y in range(0, 470, 60):
        p.line([(0, y), (W, y)], w=1.5, color=(160, 168, 162), amp=0.4)
    p.rect(-20, 470, W + 20, H + 20, (120, 124, 118))
    p.rect(60, 380, 760, 560, (150, 156, 158))
    for k, x in enumerate((170, 400, 630)):
        p.rect(x - 90, 250, x + 90, 380, (176, 182, 186))
        p.ell(x, 250, 90, 22, (120, 126, 128))
    p.rect(880, 160, 1160, 600, (176, 184, 188))  # drzwi chłodni
    p.rect(970, 230, 1070, 320, (40, 54, 70), w=5)
    p.rect(1120, 360, 1140, 440, (90, 90, 90))


def fridge_window(p, t, k=0.0):
    """Zbliżenie okienka chłodni: oszroniona kucharka wodzi głową za latarką — tylko w obrębie okienka."""
    p.rect(0, 0, W, H, (34, 46, 62), w=0)
    gx = 640 + 40 * math.sin(t * 1.2)
    skin = (170, 190, 186)
    p.ell(gx, 330, 120, 140, skin, w=5)
    p.poly([(gx - 110, 220), (gx + 110, 220), (gx + 80, 150), (gx - 80, 150)], (236, 236, 232))  # czepek kucharski
    for side in (-1, 1):
        p.line([(gx + side * 30, 270), (gx + side * 70, 262)], w=8, color=(240, 246, 250))  # oszronione brwi
        p.ell(gx + side * 48, 300, 26, 28, (238, 240, 228), w=4)
    p.ell(gx, 400, 26, 34, (36, 18, 18), w=4)
    for i in range(30):  # szron na szybie
        r = random.Random(i)
        p.ell(r.uniform(420, 860), r.uniform(150, 520), r.uniform(2, 6), r.uniform(2, 6), (220, 232, 240), w=0)
    door = (176, 184, 188)
    for x0, y0, x1, y1 in ((-50, -50, 420, H + 50), (860, -50, W + 50, H + 50), (420, -50, 860, 140), (420, 540, 860, H + 50)):
        p.rect(x0, y0, x1, y1, door, w=0, amp=0)
    p.rect(420, 140, 860, 540, None, w=10)


def treatment_door(p, t, op=0.0, who=None):
    """Drzwi gabinetu zabiegowego na podeście; op — uchylenie, w szparze kozetka albo ktoś."""
    p.rect(0, 0, W, H, (112, 126, 112), w=0)
    p.rect(0, 560, W, H, (92, 104, 92), w=0)
    p.rect(420, 80, 860, 620, (30, 34, 34))
    if op < 0.1:
        p.rect(470, 380, 560, 420, (200, 196, 180), w=2)  # róg kozetki w szparze
    if who:
        who(p)
    gap = 40 + 300 * op
    p.rect(420 + gap, 80, 860, 620, (124, 138, 122))
    p.rect(800, 350, 830, 380, (150, 150, 140), w=2)
    p.rect(400, 60, 440, 640, (150, 166, 140))
    p.rect(840, 60, 880, 640, (150, 166, 140))
    p.rect(400, 40, 880, 80, (150, 166, 140))


def ceiling_crack(p, t):
    p.rect(0, 0, W, H, (70, 74, 78), w=0)
    pts = [(200, 360), (380, 330), (470, 380), (640, 350), (760, 400), (980, 370), (1100, 410)]
    p.line(pts, w=5)
    for i in range(24):
        r = random.Random(i)
        x = r.uniform(300, 1000)
        y = 380 + ((t * r.uniform(120, 260) + r.uniform(0, 400)) % 360)
        p.ell(x, y, 3, 3, (170, 170, 160), w=0)


def stair_door(p, t, shadow=0.0, glow=0.0, cam="drzwi", dark=0.55):
    """Ciemne schody w górę do zamkniętych drzwi parteru — ta sama klatka co stair_flight; w szparze pod drzwiami
    światło i cień (shadow -1..1 — gdzie). cam: „drzwi” (detal z połowy biegu) albo „dol” (z piwnicy)."""
    stair_flight(p, t, cam=cam, dark=dark, shadow=shadow, glow=glow)


def sitting(p, x, y, s, t, who, look=0.0, gaze=None, eyes=None, mouth=0.0, arms=None):
    """Postać siedząca na podłodze z podkulonymi kolanami; (x, y) — miejsce na podłodze."""
    c = WHO[who]
    hands = figure(p, x, y, s, t, who, look=look, gaze=gaze, eyes=eyes, mouth=mouth, legs=False,
                   arms=arms or {"l": (70, 120), "r": (-70, 120)})
    hip = y - 112 * s
    for side in (-1, 1):
        knee = (x + side * 70 * s, hip - 70 * s)
        limb(p, (x + side * 26 * s, hip), knee, 48 * s, c["bottom"] if who != "henryk" else c["top"])
        limb(p, knee, (x + side * 78 * s, y - 14 * s), 40 * s, c["bottom"] if who != "henryk" else c["skin"])
        p.ell(x + side * 86 * s, y - 8 * s, 30 * s, 13 * s, c["shoes"], w=3)
        if not arms:
            p.ell(knee[0] - side * 6 * s, knee[1] - 4 * s, 14 * s, 14 * s, c["skin"])
    return hands


def paper(p, x, y, lines, w=420, h=300, rot=0.0, hand=False):
    """Kartka z odręcznym tekstem na blacie (tekst rysujemy sami — to nie generator)."""
    p.poly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2 + rot * 40), (x + w / 2, y + h / 2 + rot * 40), (x - w / 2, y + h / 2)],
           (236, 232, 214), w=3)
    for i, ln in enumerate(lines):
        p.text(x, y - h / 2 + 50 + i * 54, ln, 30, fill=(40, 40, 70))
    if hand:
        limb(p, (x + w / 2 + 160, y + h / 2 + 200), (x + w / 2 - 30, y + h / 2 - 40), 70, (52, 62, 92), outline=4)
        p.ell(x + w / 2 - 40, y + h / 2 - 50, 40, 30, WHO["zosia"]["skin"])
        p.line([(x + w / 2 - 70, y + h / 2 - 60), (x + w / 2 - 120, y + h / 2 - 110)], w=6, color=(60, 60, 140))


# ---------- dni 6–10: nowe miejsca ----------

def ward_a_door(p, t, chain=1.0, inner=None):
    """Podwójne drzwi oddziału A z szybami; inner(p) — to, co za szybą (ściana i skrzydła drzwi zasłaniają resztę);
    chain 0..1 — łańcuch przełożony przez klamki od środka (0: zdjęty)."""
    p.rect(0, 0, W, H, (40, 46, 44), w=0)
    if inner:
        inner(p)
    wall, door = (150, 166, 140), (124, 138, 122)
    for x0, y0, x1, y1 in ((-50, -50, 300, H + 50), (980, -50, W + 50, H + 50), (300, -50, 980, 70)):
        p.rect(x0, y0, x1, y1, wall, w=0, amp=0)
    p.rect(-50, 600, W + 50, H + 50, (92, 104, 92), w=0, amp=0)
    for x0 in (300, 640):  # skrzydła drzwi z wyciętą szybą
        x1 = x0 + 340
        for a, b, c, d in ((x0, 70, x1, 150), (x0, 400, x1, 600), (x0, 150, x0 + 50, 400), (x1 - 50, 150, x1, 400)):
            p.rect(a, b, c, d, door, w=0, amp=0)
        p.rect(x0 + 50, 150, x1 - 50, 400, None, w=5)
        p.rect(x0, 70, x1, 600, None, w=5)
    for x in (610, 670):
        p.rect(x - 8, 440, x + 8, 500, (150, 150, 140), w=3)  # klamki
    if chain > 0:
        for k in range(9):
            cx = 560 + k * 20
            p.ell(cx, 470 + 14 * math.sin(k / 8 * math.pi) * chain, 12, 7, None, w=4, color=(90, 92, 96))
    p.rect(300, 70, 980, 600, None, w=8)


def barricade_behind(p, t, who=()):
    """Widok przez szybę oddziału A: korytarz, barykada ze stolików, ludzie za nią (who: [(kto, x, look)])."""
    p.rect(0, 0, W, H, (150, 156, 136), w=0)
    p.rect(-20, 420, W + 20, H + 20, (110, 116, 100))
    for k, x in enumerate((380, 520, 700, 860)):
        p.poly([(x - 80, 360 - (k % 2) * 30), (x + 70, 350 - (k % 2) * 30), (x + 80, 380 - (k % 2) * 30), (x - 70, 390 - (k % 2) * 30)],
               (150, 120, 90))
        p.line([(x - 60, 390), (x - 60, 470)], w=6)
        p.line([(x + 60, 380), (x + 60, 470)], w=6)
    for w_, x, lk in who:
        figure(p, x, 560, 0.62, t, w_, look=lk, arms={"r": (40, -60)} if w_ == "kuba" else None)
    for k, x in enumerate((360, 600, 820)):  # stoliki z przodu barykady zasłaniają nogi
        p.rect(x - 110, 420, x + 110, 520, (150, 120, 90))


def chair_leg(p, hand, up=1.0):
    x, y = hand
    p.poly([(x - 8, y + 10), (x + 8, y + 10), (x + 14, y - 120 * up), (x - 2, y - 124 * up)], (150, 110, 70), w=3)


def bathroom(p, t):
    """Łazienka oddziału: kafelki, rząd kabin, jedna zamknięta."""
    p.rect(0, 0, W, H, (196, 210, 210), w=0)
    for x in range(0, W, 64):
        p.line([(x, 0), (x, 560)], w=1.5, color=(150, 166, 166), amp=0.4)
    for y in range(0, 560, 64):
        p.line([(0, y), (W, y)], w=1.5, color=(150, 166, 166), amp=0.4)
    p.rect(-20, 560, W + 20, H + 20, (120, 130, 130))
    for k, x in enumerate((140, 420, 700, 980)):
        p.rect(x, 140, x + 260, 600, (150, 170, 176))
        p.rect(x + 200, 360, x + 216, 400, (110, 110, 110), w=2)
    p.line([(0, 560), (W, 560)], w=4)


def switch_room(p, t, spark=0.0):
    """Rozdzielnia: otwarta szafa z bezpiecznikami i grubymi kablami; spark — błysk iskry."""
    p.rect(0, 0, W, H, (84, 90, 88), w=0)
    p.rect(-20, 600, W + 20, H + 20, (70, 72, 70))
    p.rect(380, 80, 900, 620, (130, 136, 130))
    p.rect(410, 110, 870, 590, (60, 64, 64))
    for r in range(4):
        for c in range(6):
            p.rect(440 + c * 70, 140 + r * 80, 480 + c * 70, 190 + r * 80, (180, 180, 170), w=2)
    for k in range(4):
        p.line([(470 + k * 110, 590), (470 + k * 110 + 20, 740)], w=16, color=(30, 30, 30))
    p.rect(900, 80, 1080, 620, (130, 136, 130))  # otwarte skrzydło
    p.poly([(1000, 200), (1040, 260), (1000, 260), (1020, 320)], (230, 200, 40), w=3)  # znak napięcia
    if spark > 0:
        for k in range(6):
            a = k * 1.1 + t * 20
            p.line([(640, 560), (640 + 50 * spark * math.cos(a), 560 + 50 * spark * math.sin(a))], w=4, color=(250, 240, 160))


def yard(p, t, amb_light=0.0, fence=True):
    """Podwórze szpitala od strony bocznych drzwi: trawnik, ścieżka, karetka po prawej, płot i las w głębi."""
    p.rect(0, 0, W, H, (176, 196, 206), w=0)
    for k in range(10):
        x = k * 140 - 40
        p.poly([(x, 290), (x + 70, 170), (x + 140, 290)], (60, 84, 66))
    p.rect(-20, 280, W + 20, H + 20, (118, 150, 96))
    p.poly([(560, H + 20), (720, H + 20), (660, 290), (620, 290)], (176, 170, 150))
    if fence:
        for x in range(0, W + 1, 30):
            p.line([(x, 250), (x + 30, 300)], w=1.5, color=(80, 86, 82), amp=0.4)
            p.line([(x + 30, 250), (x, 300)], w=1.5, color=(80, 86, 82), amp=0.4)
        p.line([(0, 250), (W, 250)], w=3, color=(70, 72, 70))
    ambulance(p, 1040, 470, 1.0, amp=amb_light)


def ambulance(p, x, y, s, amp=0.0):
    """Karetka z boku, (x, y) — środek dołu nadwozia; amp>0 — mruga światło na dachu."""
    p.rect(x - 170 * s, y - 150 * s, x + 90 * s, y, (236, 236, 228))
    p.poly([(x + 90 * s, y - 110 * s), (x + 150 * s, y - 110 * s), (x + 170 * s, y - 50 * s), (x + 170 * s, y), (x + 90 * s, y)],
           (236, 236, 228))
    p.rect(x + 100 * s, y - 100 * s, x + 145 * s, y - 60 * s, (150, 180, 200), w=3)
    p.rect(x - 170 * s, y - 80 * s, x + 170 * s, y - 64 * s, (200, 60, 50), w=0)
    p.rect(x - 60 * s, y - 130 * s, x - 20 * s, y - 90 * s, (200, 60, 50), w=0)
    p.rect(x - 70 * s, y - 120 * s, x - 10 * s, y - 100 * s, (200, 60, 50), w=0)
    for wx in (x - 110 * s, x + 110 * s):
        p.ell(wx, y + 4 * s, 26 * s, 26 * s, (36, 36, 34))
    on = amp > 0 and int(amp * 6) % 2 == 0
    p.rect(x - 40 * s, y - 170 * s, x + 10 * s, y - 150 * s, (90, 140, 240) if on else (90, 110, 150))
    if on:
        p.glow([(x - 120 * s, y - 240 * s), (x + 90 * s, y - 240 * s), (x + 60 * s, y - 140 * s), (x - 90 * s, y - 140 * s)],
               (120, 170, 255, 70))


def drone(p, x, y, s, t):
    p.rect(x - 40 * s, y - 14 * s, x + 40 * s, y + 14 * s, (60, 62, 66))
    for side in (-1, 1):
        p.line([(x + side * 30 * s, y - 10 * s), (x + side * 80 * s, y - 30 * s)], w=5 * s)
        sp = 34 * s * abs(math.sin(t * 40 + side))
        p.line([(x + side * 80 * s - sp, y - 36 * s), (x + side * 80 * s + sp, y - 36 * s)], w=4 * s, color=(120, 120, 120))


def parcel(p, x, y, s=1.0):
    p.rect(x - 60 * s, y - 50 * s, x + 60 * s, y, (176, 150, 100))
    p.line([(x, y - 50 * s), (x, y)], w=6 * s, color=(220, 220, 210))
    p.line([(x - 60 * s, y - 25 * s), (x + 60 * s, y - 25 * s)], w=6 * s, color=(220, 220, 210))


def bandage(p, x, y, r=40, rot=0.0):
    p.ell(x, y, r, r, (240, 238, 228), w=3)
    p.ell(x, y, r * 0.35, r * 0.35, (200, 196, 186), w=2)
    p.line([(x + r * math.cos(rot), y + r * math.sin(rot)), (x + r * 1.8 * math.cos(rot + 0.4), y + r * 1.8 * math.sin(rot + 0.4))],
           w=r * 0.5, color=(240, 238, 228))


HAIR_BACK = {"orderly": HAIR, "bun": (52, 40, 36), "nowak": (170, 170, 166), "henryk": None, "kuba": (46, 36, 30),
             "irena": (206, 204, 200), "mask": (78, 90, 60)}


def figure_back(p, x, y, s, t, who, walk=None, arms=None, legs=True):
    """Postać od tyłu (odchodzi w głąb), stopy w (x, y), skala jak figure(). arms jak w figure();
    legs=False — nogi rysuje kto inny (schody: st_person). Zwraca dłonie."""
    c = _costume(who)
    P = rig.pose(who)
    shu = P["shrug"] * 14 * s
    ph = (walk or 0.0) * 6
    if walk is not None:
        y -= abs(math.sin(ph)) * 5 * s
    for side, sgn in ((-1, 1), (1, -1)) if legs else ():
        lift = max(0, math.sin(ph) * sgn) * 16 * s if walk is not None else 0
        lx = x + side * 18 * s
        p.poly([(lx - 16 * s, y - 120 * s), (lx + 16 * s, y - 120 * s), (lx + 14 * s, y - 14 * s - lift),
                (lx - 14 * s, y - 14 * s - lift)], c["bottom"])
        p.ell(lx, y - 8 * s - lift, 18 * s, 9 * s, c["shoes"], w=3)
    p.poly([(x - 54 * s, y - 280 * s - shu * 0.7), (x + 54 * s, y - 280 * s - shu * 0.7), (x + 56 * s, y - 112 * s),
            (x - 56 * s, y - 112 * s)], c["top"])
    arms = arms or {}
    hands = {}
    for side in (-1, 1):
        key = "l" if side < 0 else "r"
        sh = (x + side * 50 * s, y - 268 * s - shu)
        dx, dy = arms.get(key, (side * 14, 95 + (math.sin(ph) * -side * 8 if walk is not None else 0)))
        hand = (sh[0] + dx * s, sh[1] + dy * s)
        limb(p, sh, hand, 24 * s, c["sleeve"])
        p.ell(hand[0], hand[1], 13 * s, 13 * s, c["skin"])
        hands[key] = hand
    hx, hy = x + (P["hx"] - P["yaw"] * 0.15) * 46 * s, y - 336 * s + P["hy"] * 46 * s - shu * 0.5
    p.poly([(hx - 14 * s, hy + 40 * s), (hx + 14 * s, hy + 40 * s), (x + 14 * s, y - 274 * s), (x - 14 * s, y - 274 * s)], c["skin"], w=3)
    p.push(pivot=(hx, hy + 40 * s), rot=P["rot"])
    p.ell(hx, hy, 46 * s, 52 * s, c["skin"])
    hc = HAIR_BACK.get(c["hair"])
    if c["hair"] in ("henryk", "nowak"):  # łysina z siwymi bokami; u Nowaka siwy wianek z tyłu głowy
        grey = (176, 176, 170) if c["hair"] == "henryk" else (170, 170, 166)
        if c["hair"] == "nowak":
            p.poly([(hx - 46 * s, hy), (hx - 40 * s, hy + 26 * s), (hx, hy + 38 * s), (hx + 40 * s, hy + 26 * s), (hx + 46 * s, hy),
                    (hx, hy + 14 * s)], grey)
        for side in (-1, 1):
            p.ell(hx + side * 40 * s, hy, 10 * s, 20 * s, grey, w=2.5)
    elif c["hair"] == "irena":
        for k in range(8):
            a = math.pi * (1.0 + k / 7)
            p.ell(hx + math.cos(a) * 34 * s, hy - 4 * s + math.sin(a) * 40 * s, 15 * s, 13 * s, hc, w=2.5)
    elif hc:
        p.ell(hx, hy - 8 * s, 46 * s, 44 * s, hc)
        if c["hair"] == "bun":
            p.ell(hx, hy - 52 * s, 20 * s, 16 * s, hc)
    p.pop()
    if who == "nowak":  # fartuch: biały, z rozcięciem na plecach
        p.line([(x, y - 200 * s), (x, y - 112 * s)], w=2.5)
    return hands


def basement_door(p, t, vp=(640, 340), sign=True, open_=0.0):
    """Koniec korytarza piwnicy zamiast apteki: drzwi rozdzielni ze znakiem napięcia."""
    basement(p, t, vp=vp)
    vx, vy = vp
    p.rect(vx - 150, vy - 100, vx + 150, vy + 100, (70, 76, 80))
    p.rect(vx - 70, vy - 90, vx + 70, vy + 100, (20, 22, 24))
    p.rect(vx - 70 + 140 * open_, vy - 90, vx + 70, vy + 100, (110, 116, 112))
    if sign and open_ < 0.6:
        p.poly([(vx + 10, vy - 60), (vx + 40, vy - 10), (vx - 20, vy - 10)], (230, 200, 40), w=3)


def cellar(p, t, flick=1.0, vp=(640, 340), door_open=0.0, pharmacy=True):
    """Korytarz piwnicy wg planu budynku (księga świata, decyzja D2): apteka za kratą z BOKU (lewa ściana),
    dalej pralnia, na końcu drzwi rozdzielni z żółtym znakiem. Rury pod sufitem."""
    vx, vy = vp
    bx0, by0, bx1, by1 = vx - 150, vy - 100, vx + 150, vy + 100
    p.rect(0, 0, W, H, (70, 76, 80), w=0)
    p.poly([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], (58, 62, 66))
    p.poly([(0, H), (W, H), (bx1, by1), (bx0, by1)], (78, 80, 78))
    p.poly([(0, 0), (bx0, by0), (bx0, by1), (0, H)], (88, 94, 96))
    p.poly([(W, 0), (bx1, by0), (bx1, by1), (W, H)], (84, 90, 92))
    for k, (ox, oy) in enumerate(((-40, 18), (0, 34), (60, 22))):  # rury pod sufitem
        p.line([(vx + ox * 5.5, -10 + oy), (vx + ox, by0 + oy * 0.4)], w=10 - 2 * k, color=(110, 104, 96))
        p.line([(vx + ox * 5.5, -10 + oy), (vx + ox, by0 + oy * 0.4)], w=2)

    def at(f, yy, side=-1):  # punkt na bocznej ścianie: f — głębokość 0 (kamera) … 1 (koniec), yy — 0 sufit … 1 podłoga
        edge, bx = (0, bx0) if side < 0 else (W, bx1)
        top, bot = by0 * f, H + (by1 - H) * f
        return edge + (bx - edge) * f, top + (bot - top) * yy

    # koniec korytarza: drzwi rozdzielni
    p.rect(bx0, by0, bx1, by1, (64, 70, 74))
    p.rect(vx - 70, vy - 90, vx + 70, by1, (20, 22, 24))
    p.rect(vx - 70 + 140 * door_open, vy - 90, vx + 70, by1, (110, 116, 112))
    if door_open < 0.6:
        p.poly([(vx + 10, vy - 60), (vx + 40, vy - 10), (vx - 20, vy - 10)], (230, 200, 40), w=3)
    # drzwi pralni na prawej ścianie, głębiej
    a, b, c, d = at(0.62, 0.3, 1), at(0.74, 0.3, 1), at(0.74, 0.95, 1), at(0.62, 0.95, 1)
    p.poly([a, b, c, d], (60, 64, 66))
    if pharmacy:  # apteka za kratą na lewej ścianie
        f0, f1 = 0.30, 0.55
        a, b, c, d = at(f0, 0.18), at(f1, 0.18), at(f1, 0.96), at(f0, 0.96)
        lit = tuple(int(v * flick * (1 if MAINS else 0.55)) for v in (178, 170, 132))
        p.poly([a, b, c, d], lit)
        for i in range(1, 4):  # półki w głębi apteki
            y0, y1 = a[1] + (d[1] - a[1]) * i / 4, b[1] + (c[1] - b[1]) * i / 4
            p.line([(a[0] + 6, y0), (b[0] - 4, y1)], w=3, color=(100, 90, 70))
        for i in range(9):  # pręty kraty
            f = f0 + (f1 - f0) * i / 8
            top, bot = at(f, 0.18), at(f, 0.96)
            p.line([top, bot], w=5 - 2 * f, color=(50, 52, 54))
        p.poly([a, b, c, d], None, w=4)
    for i in range(1, 7):  # płyty podłogi
        f = (i / 7) ** 1.8
        yy = by1 + (H - by1) * f
        p.line([(bx0 * (1 - f), yy), (bx1 + (W - bx1) * f, yy)], w=2, color=(60, 62, 60))


def narr_sleeve():
    """Kolor rękawa narratora w zbliżeniach dłoni: kurtka od d02_18 do d10_16, poza tym mundurek."""
    return JACKET if NARRATOR_JACKET else UNI


# ---------- dni 11–20: nowe miejsca ----------

def ward_room(p, t, wardrobe=0.0, window=True, sheet=0.0, inner=None, sheet_lines=("6 ŻYWYCH", "APTEKA", "PIWNICA")):
    """Sala 8 oddziału C: przewrócone łóżka, okno na bramę (lewa część), szafa w prawym kącie.
    wardrobe 0..1 — uchylenie drzwiczek szafy; sheet 0..1 — prześcieradło na szybie; inner(q) — widok za oknem."""
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(-20, 540, W + 20, H + 20, (104, 124, 100))
    p.line([(-20, 540), (W + 20, 540)], w=4)
    if window:
        if inner:
            inner(p)
        else:
            p.rect(160, 110, 560, 420, (190, 200, 196))
            p.poly([(160, 330), (560, 320), (560, 420), (160, 420)], (98, 110, 88))
        for x0, y0, x1, y1 in ((-50, -50, 160, H + 50), (560, -50, W + 50, H + 50), (160, -50, 560, 110), (160, 420, 560, H + 50)):
            p.rect(x0, y0, x1, y1, (150, 166, 140), w=0, amp=0)
        p.rect(-20, 540, 700, H + 20, (104, 124, 100), w=0, amp=0)
        p.line([(-20, 540), (700, 540)], w=4)
        p.line([(360, 110), (360, 420)], w=8, color=(90, 96, 90))
        for i in range(10):  # kurz na szybie
            r = random.Random(i)
            p.ell(r.uniform(180, 540), r.uniform(130, 400), r.uniform(10, 30), r.uniform(4, 9), (170, 178, 170), w=0)
        p.rect(160, 110, 560, 420, None, w=8)
        if sheet > 0:
            h = 300 * sheet
            p.poly([(180, 120), (540, 116), (536, 120 + h), (184, 124 + h)], (238, 236, 228), w=3)
            if sheet > 0.8:
                for k, txt in enumerate(sheet_lines):
                    p.text(360, 170 + k * 70, txt, 40, fill=(30, 30, 30))
    for k, (x, rot) in enumerate(((640, 0.25), (860, -0.18))):  # przewrócone łóżka
        p.poly([(x - 120, 600 + 20 * rot), (x + 140, 590 - 30 * rot), (x + 150, 640), (x - 110, 650)], (176, 182, 176), w=3)
        p.line([(x - 110, 650), (x - 130, 690)], w=6)
        p.line([(x + 140, 640), (x + 160, 690)], w=6)
    p.rect(1010, 140, 1220, 560, (124, 108, 86))  # szafa
    gap = 100 * wardrobe
    p.rect(1010, 140, 1115, 560, (20, 22, 22) if wardrobe > 0.02 else (124, 108, 86))
    p.rect(1010 + gap, 140, 1115 + gap * 0.2, 560, (134, 118, 96))
    p.line([(1115, 140), (1115, 560)], w=3)
    p.rect(1095 + gap * 0.2, 330, 1105 + gap * 0.2, 370, (90, 90, 80), w=2)


def iso_door(p, t, inner=None, open_=0.0, wall=(150, 166, 140)):
    """Drzwi izolatki 3 z okienkiem (siatka). inner(q) rysuje to, co za okienkiem; ściana i drzwi przycinają resztę."""
    p.rect(0, 0, W, H, wall, w=0)
    p.rect(-20, 600, W + 20, H + 20, (104, 124, 100))
    p.rect(420, 60, 860, 640, (30, 34, 34))
    if inner:
        inner(p)
    door = (124, 138, 122)
    if open_ < 0.05:
        for x0, y0, x1, y1 in ((420, 60, 860, 160), (420, 330, 860, 640), (420, 160, 540, 330), (740, 160, 860, 330)):
            p.rect(x0, y0, x1, y1, door, w=0, amp=0)
        for x0, y0, x1, y1 in ((-50, -50, 420, H + 50), (860, -50, W + 50, H + 50), (420, -50, 860, 60)):
            p.rect(x0, y0, x1, y1, wall, w=0, amp=0)
        p.rect(-20, 600, 420, H + 20, (104, 124, 100), w=0, amp=0)
        p.rect(860, 600, W + 20, H + 20, (104, 124, 100), w=0, amp=0)
        for k in range(1, 5):  # siatka w okienku — przed tym, co za nim
            p.line([(540 + k * 40, 160), (540 + k * 40, 330)], w=2, color=(60, 64, 60), amp=0.4)
            p.line([(540, 160 + k * 34), (740, 160 + k * 34)], w=2, color=(60, 64, 60), amp=0.4)
        p.rect(540, 160, 740, 330, None, w=5)
        p.rect(800, 380, 830, 420, (150, 150, 140), w=2)
        p.text(640, 110, "3", 40, fill=(40, 40, 40))
    else:
        p.rect(420 + 400 * open_, 60, 860 + 40 * open_, 640, door)
        for x0, y0, x1, y1 in ((-50, -50, 420, H + 50), (900, -50, W + 50, H + 50), (420, -50, 900, 60)):
            p.rect(x0, y0, x1, y1, wall, w=0, amp=0)
    p.rect(400, 40, 880, 660, None, w=8)


def tech_room(p, t, tarp=1.0, running=0.0, lights=False):
    """Skrzydło techniczne: agregat (pod plandeką, tarp 0..1), beczki z paliwem, rura wydechowa, przełącznik."""
    base = (150, 156, 150) if lights else (70, 74, 76)
    p.rect(0, 0, W, H, base, w=0)
    p.rect(-20, 560, W + 20, H + 20, tuple(int(c * 0.8) for c in base))
    j = 3 * math.sin(t * 50) * running
    p.rect(380 + j, 300, 860 + j, 560, (90, 110, 70))  # agregat
    p.rect(420 + j, 340, 560 + j, 420, (60, 66, 60), w=3)
    p.rect(840, 120, 870, 300, (100, 100, 96))  # rura wydechowa
    if running:
        for k in range(4):
            y = 120 - ((t * 120 + k * 40) % 160)
            p.ell(855 + 10 * math.sin(t * 3 + k), y, 26 + k * 6, 16 + k * 4, (120, 120, 116), w=2)
    if tarp > 0:
        p.poly([(360, 300 - 10 * tarp), (880, 290), (900, 570), (350, 575)], (110, 120, 96), w=4)
        for k in range(5):
            p.line([(400 + k * 100, 310), (420 + k * 100, 560)], w=2, color=(90, 98, 80))
    for k, x in enumerate((960, 1060, 1160)):
        p.rect(x - 40, 400, x + 40, 560, (150, 60, 40))
        p.ell(x, 400, 40, 12, (170, 80, 60), w=3)
    p.rect(160, 280, 260, 400, (130, 130, 126))  # skrzynka z przełącznikiem
    p.rect(195, 300, 225, 380, (40, 40, 40), w=2)


def porter_lodge(p, t, wires=1.0, lights=True):
    """Portiernia: centrala alarmu na ścianie (wires 1 — przewody na miejscu, 0 — wyrwane), okienko na bramę, biurko."""
    p.rect(0, 0, W, H, (170, 176, 166) if lights else (90, 94, 90), w=0)
    p.rect(-20, 560, W + 20, H + 20, (120, 122, 112))
    p.rect(120, 140, 460, 400, (196, 206, 210), w=6)  # okienko portierni
    p.line([(290, 140), (290, 400)], w=5)
    p.rect(-20, 430, 620, 520, (120, 96, 70))  # biurko
    p.rect(760, 120, 1100, 460, (200, 60, 50))  # centrala alarmu
    p.rect(800, 160, 1060, 260, (240, 230, 220), w=3)
    for k in range(6):
        p.ell(830 + k * 42, 210, 12, 12, (250, 80, 60) if int(t * 4) % 2 == 0 and wires > 0.5 else (90, 40, 40), w=2)
    for k in range(5):  # wiązka przewodów
        sag = 40 * (1 - wires)
        p.line([(820 + k * 50, 460), (820 + k * 50 + 20 * (1 - wires), 560 + sag)], w=6, color=((200, 60, 60), (60, 60, 200), (220, 220, 220), (60, 160, 60), (40, 40, 40))[k])


def tally(p, n, note=None):
    """Kreski kredą nad kanapą: piątkami (cztery i skośna), dwa rzędy po trzy piątki; od d24 nuta Henryka przy 24."""
    chalk = (236, 236, 226)
    for m in range(n):
        g, k = divmod(m, 5)
        row, col = divmod(g, 3)
        x0, y0 = 520 + col * 70 - row * 10, 120 + row * 80
        if k < 4:
            p.line([(x0 + k * 12, y0), (x0 + 2 + k * 12, y0 + 60)], w=4, color=chalk)
        else:
            p.line([(x0 - 8, y0 + 40), (x0 + 46, y0 + 20)], w=4, color=chalk)
    if note if note is not None else DAY >= 24 and n >= 24:
        x, y = 600, 300  # pod dwudziestą czwartą kreską
        p.ell(x, y, 12, 9, chalk, w=3)
        p.line([(x + 11, y), (x + 11, y - 46)], w=4, color=chalk)
        p.line([(x + 11, y - 46), (x + 26, y - 34)], w=4, color=chalk)


def staff_room(p, t, lights=True, night=False, marks=None, couch=True):
    """Pokój socjalny na parterze: kanapy, kuchenka z czajnikiem, okno, telefon na ścianie, kreski kredą."""
    wall = (200, 196, 176) if lights and not night else (70, 72, 74)
    p.rect(0, 0, W, H, wall, w=0)
    p.rect(-20, 560, W + 20, H + 20, tuple(int(c * 0.7) for c in wall))
    p.rect(80, 120, 380, 380, (150, 170, 190) if not night else (30, 36, 50), w=6)  # okno
    p.line([(230, 120), (230, 380)], w=5)
    p.rect(860, 360, 1200, 470, (210, 210, 206))  # blat z kuchenką
    p.rect(880, 330, 980, 360, (60, 60, 60), w=2)
    p.ell(1100, 330, 34, 26, (220, 220, 216), w=3)  # czajnik z dyżurki
    p.rect(760, 180, 810, 260, (230, 228, 220), w=3)  # telefon na ścianie
    p.rect(768, 196, 802, 214, (60, 60, 60), w=2)
    if couch:  # kanapa (w dniu 24 przesunięta pod drzwi jako barykada)
        p.poly([(420, 560), (760, 560), (780, 470), (400, 470)], (120, 90, 110))
        p.rect(400, 440, 780, 480, (110, 80, 100))
    tally(p, marks if marks is not None else max(15, DAY))  # od dnia 15 (przeprowadzka) kreska co dzień


def chute(p, t, open_=0.0):
    """Drzwiczki zsypu w ścianie korytarza C (obok dyżurki)."""
    p.rect(0, 0, W, H, (150, 166, 140), w=0)
    p.rect(-20, 560, W + 20, H + 20, (104, 124, 100))
    p.rect(470, 200, 810, 480, (20, 22, 22))
    p.poly([(470, 200), (810, 200), (810 - 60 * open_, 480 - 300 * open_), (470 + 60 * open_, 480 - 300 * open_)], (160, 164, 166), w=4)
    p.text(640, 160, "ZSYP — PRALNIA", 26)


def thermometer(p, t, value=39.0, rise=1.0):
    p.rect(0, 0, W, H, (128, 98, 70), w=0)
    p.poly([(200, 330), (1080, 300), (1090, 380), (210, 410)], (236, 236, 232), w=4)
    p.ell(220, 370, 40, 40, (200, 60, 50), w=3)
    k = rise * (value - 34) / 8
    p.line([(240, 368), (240 + 820 * k, 340 - 26 * k)], w=12, color=(200, 60, 50))
    for i in range(9):
        x = 300 + i * 92
        p.line([(x, 316 - 3 * i), (x, 338 - 3 * i)], w=3)
        p.text(x, 296 - 3 * i, str(34 + i), 22)


def sheet_on_pane(p, k=1.0, lines=("5 ŻYWYCH", "PARTER", "POKÓJ SOCJ.")):
    """Prześcieradło na prawej szybie okna sali 8 (od dnia 19); k 0..1 — rozwijanie z góry."""
    h = 304 * k
    p.poly([(366, 120), (540, 116), (536, 120 + h), (370, 124 + h)], (238, 236, 228), w=3)
    if k > 0.8:
        for i, txt in enumerate(lines):
            p.text(453, 190 + i * 64, txt, 24, fill=(30, 30, 30))


# ---------- dni 21–30: nowe miejsca ----------

def talk(t, T, a=0.3, b=0.4, speed=9):
    """Ruch ust w kwestii: od a do T-b."""
    return 0.5 + 0.5 * math.sin(t * speed) if a < t < T - b else 0.0


def irena_lying(p, t, x=640, y=520, fever=0.6, eyes=0.0):
    """Irena na kanapie pokoju socjalnego: szlafrok, siwe loki, oczy zamknięte, oddech płytki."""
    c = WHO["irena"]
    br = 4 * math.sin(t * 2.4)
    p.ell(x - 200, y + 20, 70, 30, (236, 236, 230), w=3)  # poduszka
    p.poly([(x - 140, y - 10 - br), (x + 240, y - 10 - br), (x + 250, y + 40), (x - 150, y + 40)], (200, 196, 180))  # koc
    p.ell(x - 190, y + 6, 46, 40, c["skin"])
    for k in range(6):
        a = math.pi * (0.6 + 0.8 * k / 5)
        p.ell(x - 190 + math.cos(a) * 40, y + math.sin(a) * 40, 14, 12, (206, 204, 200), w=2.5)
    for side in (-1, 1):
        if eyes > 0.3:
            p.ell(x - 190 + side * 16, y + 6, 6, 5 * eyes, (246, 246, 240), w=2)
        else:
            p.line([(x - 190 + side * 16 - 7, y + 6), (x - 190 + side * 16 + 7, y + 6)], w=3)
    if fever:
        p.ell(x - 190, y + 26, 20 * fever, 6 * fever, (230, 150, 140), w=0)  # rumieńce gorączki


def handset(p, x, y, s=1.0):
    """Słuchawka telefonu na ścianie przy uchu (zbliżenie)."""
    p.poly([(x - 30 * s, y - 120 * s), (x + 10 * s, y - 130 * s), (x + 40 * s, y + 120 * s), (x, y + 130 * s)], (230, 228, 220), w=3)


def listening(p, t, T, fear=0.3, gaze=(-0.4, 0.2), speaking=False, who="narrator", night=False):
    """Zbliżenie przy telefonie na ścianie pokoju socjalnego: słuchawka przy uchu, kabel do aparatu, głos w słuchawce."""
    staff_room(p, t, night=night)
    if who == "narrator":
        R.nurse_face(p, 640, 330, 1.0, (0.4 if speaking and 0.3 < t < T - 0.4 else fear), t, gaze=gaze)
    else:
        mouth = 0.5 + 0.5 * math.sin(t * 9) if speaking and 0.3 < t < T - 0.4 else 0.0
        face_cu(p, 640, 330, 1.0, who, t, gaze=gaze, mouth=mouth, fear=fear)
    P = rig.pose(who)  # słuchawka przy uchu idzie za głową, jeśli ujęcie ma rig
    hdx, hdy = (P["bx"] + P["hx"]) * 120, (P["by"] + P["hy"]) * 120
    p.push(pivot=(640, 440), rot=P["rot"], dx=hdx, dy=hdy)
    handset(p, 500 - P["yaw"] * 14, 360)  # ucho przesuwa się razem ze skrętem twarzy (face_cu: -yaw·14)
    end = p.local((510, 490))
    p.pop()
    p.line([end, (420, 620), (300, 700)], w=4, color=(60, 60, 60))
    if not speaking and int(t * 6) % 3 == 0:  # głos w słuchawce
        for k in range(2):
            p.line([(450 - k * 20, 300 - k * 14), (430 - k * 20, 290 - k * 14)], w=3)


def piano_room(p, t, lights=True, wire=0.0, lid=True):
    """Świetlica parteru: pianino pod ścianą, krzesła, okno; wire 0..1 — kabel od alarmu wzdłuż podłogi do pianina (d27)."""
    wall = (150, 154, 150) if lights else (60, 62, 66)
    p.rect(0, 0, W, H, wall, w=0)
    p.rect(-20, 560, W + 20, H + 20, tuple(int(c * 0.72) for c in wall))
    p.rect(80, 120, 300, 360, (60, 70, 86) if lights else (24, 28, 40), w=6)  # okno na podwórze
    p.line([(190, 120), (190, 360)], w=5)
    p.rect(420, 260, 860, 560, (70, 52, 40))  # pianino
    p.rect(420, 260, 860, 290, (84, 64, 50))
    if lid:
        p.rect(450, 400, 830, 430, (230, 226, 210))
        for i in range(1, 19):
            p.line([(450 + i * 21, 400), (450 + i * 21, 430)], w=1.5)
    else:
        p.rect(450, 400, 830, 430, (84, 64, 50))
    for x in (960, 1100):  # krzesła
        p.rect(x, 420, x + 90, 440, (120, 100, 80), w=3)
        p.line([(x + 6, 440), (x + 6, 560)], w=5)
        p.line([(x + 84, 440), (x + 84, 560)], w=5)
        p.rect(x, 330, x + 14, 430, (120, 100, 80), w=3)
    if wire > 0:  # kabel spod podłogi, przy listwie, do spodu klawiatury
        k = ease(wire)
        pts = [(W + 20, 600), (1000, 600), (880, 590), (860, 520), (840, 440)]
        n = max(2, int(len(pts) * k + 0.999))
        p.line(pts[:n], w=5, color=(200, 60, 60))


def city_far(q, t, fire=1.0, dark=0.0, y=330):
    """Miasto za lasem nocą: bloki na horyzoncie, łuna nad płonącymi dzielnicami; dark 0..1 — gasną światła."""
    q.rect(0, 0, W, H, (24, 26, 40), w=0)
    rng = random.Random(7)
    for i in range(26):
        x = i * 52 - 10
        h = rng.uniform(30, 110)
        q.rect(x, y - h, x + 44, y + 10, (34, 36, 50), w=2)
        for k in range(int(h // 22)):
            if rng.random() > 0.35 + 0.6 * dark:
                q.rect(x + 10, y - h + 10 + k * 22, x + 18, y - h + 18 + k * 22, (230, 210, 140), w=0)
    for i, cx in enumerate((260, 700, 1040)):  # trzy płonące dzielnice
        for k in range(6):
            f = 0.5 + 0.5 * math.sin(t * 3 + i * 2 + k)
            q.ell(cx + k * 22 - 55, y - 10, 16, (10 + 18 * f) * fire, (230, int(120 + 40 * f), 50), w=0)
        q.glow([(cx - 160, y - 160), (cx + 160, y - 160), (cx + 160, y + 10), (cx - 160, y + 10)], (255, 140, 60, int(45 * fire)))
    q.poly([(0, y + 10), (W, y), (W, H), (0, H)], (20, 26, 22))


def roof(p, t, dusk=0.0, fire=1.0, dark=0.0, tank=0.5, hatch=1.0):
    """Dach oddziału C: papa, zbiornik na deszczówkę po prawej, klapa z drabiny, w tle las i miasto.
    dusk 0..1 — od dnia do zachodu (niebo różowieje, potem granatowieje)."""
    sky = tuple(int(a + (b - a) * dusk) for a, b in zip((170, 186, 196), (90, 70, 96)))
    p.rect(0, 0, W, H, sky, w=0)
    for i in range(14):  # miasto na horyzoncie
        x = 40 + i * 90
        h = 30 + (i * 37) % 70
        p.rect(x, 300 - h, x + 60, 310, (120, 120, 130) if dusk < 0.5 else (50, 50, 66), w=2)
    for i, cx in enumerate((300, 720, 1010)):  # dym nad trzema dzielnicami
        for k in range(4):
            yy = 280 - ((t * 20 + k * 50) % 200)
            p.ell(cx + 20 * math.sin(t + k), yy, 30 + k * 10, 18 + k * 6, (70, 66, 64), w=0)
        if fire:
            p.glow([(cx - 80, 230), (cx + 80, 230), (cx + 80, 310), (cx - 80, 310)], (255, 140, 60, int((20 + 40 * dusk) * fire)))
            for k in range(4):  # płomienie u podstawy dymu
                f = 0.5 + 0.5 * math.sin(t * 4 + i + k)
                p.ell(cx - 30 + k * 20, 296, 9, (8 + 10 * f) * fire, (240, int(130 + 50 * f), 50), w=0)
    for k in range(10):  # las
        x = k * 140 - 40
        p.poly([(x, 380), (x + 70, 300), (x + 140, 380)], (52, 70, 60) if dusk < 0.6 else (30, 40, 36))
    p.poly([(-20, 400), (W + 20, 380), (W + 20, H + 20), (-20, H + 20)], (90, 90, 92))  # papa
    for k in range(6):
        p.line([(0, 430 + k * 50), (W, 410 + k * 52)], w=1.5, color=(70, 70, 72))
    p.line([(-20, 400), (W + 20, 380)], w=5)  # krawędź dachu (rynna)
    p.rect(860, 230, 1160, 470, (150, 156, 160))  # zbiornik
    p.ell(1010, 230, 150, 24, (130, 136, 140), w=4)
    p.line([(860, 470 - 240 * tank), (1160, 470 - 240 * tank)], w=2, color=(90, 110, 120))
    p.rect(180, 520, 380, 600, (70, 70, 70))  # klapa
    if hatch > 0:
        p.poly([(180, 520), (380, 520), (380 - 30 * hatch, 520 - 150 * hatch), (180 + 30 * hatch, 520 - 150 * hatch)], (110, 110, 108), w=4)


def crowd(p, t, n=40, seed=5, turn=0.0, area=(80, 1200, 330, 700), walk=0.0, toward=None, smax=0.93):
    """Tłum zarażonych na podwórzu widziany od strony budynku: każdy z własnym tempem i miejscem; dalej = mniejszy.
    turn 0..1 — odwracają się od bramy (plecy) ku budynkowi (twarz), każdy z innym opóźnieniem;
    walk — przesunięcie w stronę toward (x, y) dla wszystkich (0..1)."""
    rng = random.Random(seed)
    x0, x1, y0, y1 = area
    people = []
    for i in range(n):
        y = y0 + (y1 - y0) * rng.random() ** 0.8
        people.append((y, rng.uniform(x0, x1), rng.uniform(0, 0.6), rng.randint(1, 999)))
    for y, x, delay, sd in sorted(people):
        s = 0.18 + (smax - 0.18) * (y - y0) / max(1, (y1 - y0))  # smax — największa skala (najbliżej kamery)
        if toward and walk:
            x += (toward[0] - x) * walk * 0.5
            y += (toward[1] - y) * walk * 0.15
        if turn > delay + 0.25 * (sd % 3) / 2:
            R.zombie(p, x, y, s, t + sd, sd, tilt=0.06 * ((sd % 5) - 2))
        else:
            zombie_back(p, x, y, s, t + sd, sd, walk=(t + sd) if walk else None)


def yard_view(p, t, night=False, gate_lights=0.0, dawn=0.0, beyond=None, hole=False, truck_=True):
    """Podwórze od strony budynku: trawnik, ścieżka do bramy, płot z zasiekami, ciężarówka za bramą, las.
    beyond(q) — to, co za płotem (rysowane przed siatką); hole — dziura w płocie od strony lasu (lewa część)."""
    sky = (176, 196, 206) if not night else tuple(int(a + (b - a) * dawn) for a, b in zip((22, 26, 36), (120, 110, 120)))
    p.rect(0, 0, W, H, sky, w=0)
    for k in range(10):
        x = k * 140 - 40
        p.poly([(x, 290), (x + 70, 170), (x + 140, 290)], (60, 84, 66) if not night else (20, 30, 26))
    grass = (118, 150, 96) if not night else (40, 52, 40)
    p.rect(-20, 280, W + 20, H + 20, grass)
    p.poly([(560, H + 20), (720, H + 20), (660, 290), (620, 290)], (176, 170, 150) if not night else (70, 70, 64))
    if truck_:  # ciężarówka wojska na drodze za bramą: paka z plandeką, kabina, koła na ziemi
        col = (86, 100, 70) if not night else (40, 46, 36)
        p.rect(576, 236, 676, 280, col)
        p.poly([(576, 236), (676, 236), (670, 228), (582, 228)], col, w=2)
        p.rect(676, 250, 708, 280, tuple(int(c * 0.9) for c in col))
        p.rect(682, 254, 702, 264, (150, 170, 176) if not night else (60, 66, 70), w=2)
        for wx in (594, 640, 694):
            p.ell(wx, 282, 8, 8, (36, 36, 34))
    if beyond:
        beyond(p)
    for x in range(0, W + 1, 30):
        if hole and 90 <= x <= 180:
            continue
        p.line([(x, 250), (x + 30, 300)], w=1.5, color=(80, 86, 82), amp=0.4)
        p.line([(x + 30, 250), (x, 300)], w=1.5, color=(80, 86, 82), amp=0.4)
    p.line([(0, 250), (W, 250)], w=3, color=(70, 72, 70))
    for k in range(14):  # zasieki
        p.ell(40 + k * 90, 300, 40, 18, None, w=2)
    p.rect(600, 230, 680, 300, None, w=4)  # brama
    if gate_lights > 0:
        for x in (690, 704):  # reflektory ciężarówki za bramą
            p.ell(x, 272, 6, 5, (255, 250, 220), w=0)
        p.glow([(560, 240), (760, 240), (900, 420), (380, 420)], (255, 250, 220, int(70 * gate_lights)))


def truck(p, x, y, s=1.0, lights=0.0, color=(86, 100, 70)):
    """Ciężarówka wojskowa z plandeką, z boku, przodem w lewo; lights — reflektory."""
    p.rect(x - 60 * s, y - 170 * s, x + 260 * s, y - 30 * s, color)  # paka z plandeką
    p.poly([(x - 60 * s, y - 170 * s), (x + 260 * s, y - 170 * s), (x + 250 * s, y - 190 * s), (x - 50 * s, y - 190 * s)], color, w=3)
    p.rect(x - 170 * s, y - 130 * s, x - 60 * s, y - 30 * s, tuple(int(c * 0.9) for c in color))  # kabina
    p.rect(x - 150 * s, y - 115 * s, x - 90 * s, y - 80 * s, (150, 170, 176), w=3)
    for wx in (x - 120 * s, x + 60 * s, x + 200 * s):
        p.ell(wx, y - 24 * s, 28 * s, 28 * s, (36, 36, 34))
    if lights > 0:
        p.ell(x - 168 * s, y - 60 * s, 10 * s, 8 * s, (255, 250, 220), w=0)
        p.glow([(x - 170 * s, y - 80 * s), (x - 170 * s, y - 40 * s), (x - 600 * s, y + 20 * s), (x - 600 * s, y - 140 * s)],
               (255, 250, 220, int(80 * lights)))


def side_door(p, t, inner=None, open_=0.0, lights=True):
    """Boczne drzwi parteru z szybą; inner(q) — podwórze za szybą (albo za otwartym skrzydłem)."""
    wall = (150, 154, 146) if lights else (50, 54, 56)
    p.rect(0, 0, W, H, wall, w=0)
    p.rect(-20, 600, W + 20, H + 20, tuple(int(c * 0.7) for c in wall))
    p.rect(440, 60, 840, 640, (30, 34, 36))
    if inner:
        inner(p)
    for x0, y0, x1, y1 in ((-50, -50, 440, H + 50), (840, -50, W + 50, H + 50), (440, -50, 840, 60)):
        p.rect(x0, y0, x1, y1, wall, w=0, amp=0)
    p.rect(-50, 600, 440, H + 50, tuple(int(c * 0.7) for c in wall), w=0, amp=0)
    p.rect(840, 600, W + 50, H + 50, tuple(int(c * 0.7) for c in wall), w=0, amp=0)
    p.rect(430, 640, 850, H + 50, tuple(int(c * 0.7) for c in wall), w=0, amp=0)  # podłoga pod progiem zasłania podwórze
    door = (110, 120, 116)
    if open_ < 0.05:
        for a, b, c, d in ((440, 60, 840, 140), (440, 380, 840, 640), (440, 140, 520, 380), (760, 140, 840, 380)):
            p.rect(a, b, c, d, door, w=0, amp=0)
        p.rect(520, 140, 760, 380, None, w=5)
        p.rect(500, 470, 780, 500, (170, 170, 160), w=3)  # pozioma klamka antypaniczna
    else:
        p.poly([(440, 60), (440 + 400 * (1 - open_), 60 - 30 * open_), (440 + 400 * (1 - open_), 640 + 30 * open_), (440, 640)], door)
    p.rect(440, 60, 840, 640, None, w=8)


def sling(p, x, y, s=1.0):
    """Temblak Zosi na figurze (x, y — stopy, skala jak figure): biały trójkąt przez pierś, ręka zgięta."""
    p.poly([(x - 40 * s, y - 270 * s), (x + 50 * s, y - 200 * s), (x - 30 * s, y - 180 * s)], WHITE, w=3)


def window8_close(p, t, sil=None, dawn=0.0):
    """Okno sali 8 z bliska, od strony bramy, w rysunku pierwszego ujęcia (render.scene1, okno (8, 1)).
    sil — czas sylwetki w skali scene1 (3.0–6.1: podchodzi, przekrzywia głowę, odskakuje); None — pusto."""
    R.scene1(p, sil if sil is not None else 9.0, 7.0)
    if dawn:
        dawn_sky(p, dawn)


def dawn_sky(p, k):
    """Świt w kadrze pierwszego ujęcia: ciepłe światło narasta ku horyzontowi (gładko, pasami po 12 px) — pada też na fasadę."""
    for i in range(46):
        y = i * 12
        a = (i / 45) ** 1.6 * 70 * k
        p.glow([(-20, y), (W + 20, y), (W + 20, y + 12), (-20, y + 12)], (255, 176, 120, int(a)))