"""Wspólna część skryptów dni wariantu A (render_dNN.py): ujęcia z rozpiski, kamera, światło, napisy, klatka.

Dzień definiuje FNS (funkcja ujęcia na każde ujęcie rozpiski), LOOK (barwa i światło) i CAM (własny kadr ujęcia),
a potem woła setup(...) — dostaje SCENES, DUR i frame(t) zgodne z render.py i scripts/kontrola_ujec.py.
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from render import FPS, H, SS, W, Pen, ease, framed, handheld, light_mask, subtitle

import render as _R

_nurse_face = _R.nurse_face


def _living_nurse_face(p, x, y, s, fear, t, gaze=(0.0, 0.0), blink_k=None, swallow=0.0, breath=0.0, body=None):
    """Zbliżenie narratora w dniach: samo mruga i oddycha (MASTER_BIBLE 2.6), chyba że ujęcie ustawia oczy;
    od d02_18 nosi rozpiętą kurtkę na mundurku."""
    if blink_k is None:
        blink_k = _R.blink(t, 777, 3.1)
    breath = breath + 0.6 * math.sin(2 * math.pi * 0.25 * t)
    out = _nurse_face(p, x, y, s, fear, t, gaze=gaze, blink_k=blink_k, swallow=swallow, breath=breath, body=body)
    import kit_a
    if kit_a.NARRATOR_JACKET:
        bx, by = body or (x, y)
        by -= breath * 5 * s
        for side in (-1, 1):  # poły kurtki po bokach, środek (mundurek z dekoltem) zostaje odkryty
            p.poly([(bx + side * 120 * s, by + 150 * s), (bx + side * 48 * s, by + 150 * s), (bx + side * 60 * s, by + 410 * s),
                    (bx + side * 152 * s, by + 410 * s)], kit_a.JACKET)
            p.poly([(bx + side * 50 * s, by + 150 * s), (bx + side * 34 * s, by + 152 * s), (bx + side * 60 * s, by + 230 * s)],
                   (90, 98, 110), w=2.5)  # klapa kołnierza
    return out


_R.nurse_face = _living_nurse_face

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))

DARK = ((0.84, 0.92, 1.02), (640, 360, 640, 0.5))
NIGHT = ((0.7, 0.8, 0.95), (640, 360, 560, 0.3))
WARD = ((0.92, 1.0, 0.94), None)
CELL = ((0.88, 0.98, 0.92), (640, 280, 520, 0.35))
BASE = ((0.9, 0.96, 1.0), (640, 300, 700, 0.45))
DAY = ((0.96, 1.0, 0.98), None)
DAWN = ((0.92, 0.95, 0.96), None)  # świt dnia 30: barwa bliska pierwszemu ujęciu (render.GRADE[0]), słońce rysuje ujęcie


def day_tuple(day):
    from a_dane1 import DAYS as D1
    from a_dane2 import DAYS as D2
    return next(x for x in D1 + D2 if x[0] == day)


def rows(day):
    d = day_tuple(day)
    return [shot for _, _, beats in d[2] for _, shots in beats for shot in shots]


def voice_windows(day):
    """(start, długość) kwestii w każdym ujęciu — z tempo.py, tak jak liczy je rozpiska."""
    from tempo import kwestie
    return kwestie(day_tuple(day))


def spoken(sound):
    """Napis z kwestii: lektor bez znaku, dialog i megafon z myślnikiem."""
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


def setup(day, fns, look, cam):
    import kit_a
    kit_a.DAY = day
    kit_a.MAINS = day <= 2 or day >= 14  # lampy: z sieci do wieczoru dnia 2, z agregatu od dnia 14 (księga świata)
    rs = rows(day)
    assert len(fns) == len(rs) == len(look), (len(fns), len(rs), len(look))
    scenes, t0 = [], 0.0
    for (kadr, ruch, sec, desc, sound), (vs, vl) in zip(rs, voice_windows(day)):
        scenes.append((t0, t0 + sec, ruch, spoken(sound), vs, vl))
        t0 += sec

    def camera(i, lt, T):
        ruch = scenes[i][2]
        if callable(cam.get(i)):  # własny ruch kamery ujęcia (np. odjazd do kadru z pierwszego ujęcia filmu w d30)
            return {"zoom": 1.0, "cx": 640, "cy": 360, **cam[i](lt, T)}
        c = {"zoom": 1.0, "cx": 640, "cy": 360, **cam.get(i, {})}
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
        ruch = scenes[i][2]
        amp = {"ręka": 3.0, "drg": 5.0}.get(ruch, 0.0)
        if ruch == "szarp" and lt < 0.4:
            amp = 9 * (1 - lt / 0.4)
        return handheld(t, amp, seed=200 + day * 50 + i)

    def frame(t):
        i = next((k for k, s in enumerate(scenes) if s[0] <= t < s[1]), len(scenes) - 1)
        a, b, ruch, txt, vs, vl = scenes[i]
        import kit_a
        # kurtka: zakłada w d02_18, traci w d10_16 (rzuca ją na karetkę) — księga świata, rekwizyt „kurtka”
        kit_a.DAY, kit_a.MAINS = day, day <= 2 or day >= 14  # stan dnia ustawiany w każdej klatce (kilka dni w jednym procesie)
        kit_a.NARRATOR_JACKET = (day == 2 and i >= 17) or 3 <= day <= 9 or (day == 10 and i < 15)
        # opatrunek na kolanie od d23_19, czysta koszula Henryka od d29_10 (księga świata: stany postaci)
        kit_a.NARRATOR_KNEE = day >= 24 or (day == 23 and i >= 19)  # d23_19 wpada z krwią na kolanie, opatrunek potem
        kit_a.HENRYK_SHIRT = day >= 30 or (day == 29 and i >= 9)
        lt, T = t - a, b - a
        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255))
        p = Pen(img, t, **framed(camera(i, lt, T), shake(i, lt, t)))
        fns[i](p, lt, T)
        img = img.convert("RGB").resize((W, H), Image.LANCZOS)
        arr = np.asarray(img).astype(np.float32)
        if look[i]:
            grade, mask = look[i]
            arr *= np.array(grade, dtype=np.float32)
            if mask:
                arr = light_mask(arr, *mask)
            yy, xx = np.ogrid[:H, :W]
            vig = 1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
            arr *= np.clip(vig, 0.35, 1)[..., None]
        arr += np.random.default_rng(int(t * FPS) // 3 + 13 + day).normal(0, 5, (H, W, 1))  # ziarno 8×/s, jak kreska
        if look[i] is None:  # karta: wejście i wyjście przez czerń
            arr *= min(1.0, lt / 0.4, max(0.0, (T - lt) / 0.4))
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        if txt and vs <= lt < min(T - 0.05, vs + vl + 0.35):  # napis tylko wtedy, gdy lektor mówi (MASTER_BIBLE 2.5)
            subtitle(img, wrap(txt))
        return img

    return scenes, t0, frame


def card(text):
    def fn(p, t, T):
        p.rect(0, 0, W, H, (0, 0, 0), w=0)
        p.text(640, 360, text, 54, fill=(236, 236, 230))
    return fn


def stills(module, times):
    for s in times:
        module.frame(s).save(HERE / f"{module.__name__}-klatka-{s:06.2f}s.png")


def breathing(t, rate=0.3):
    return math.sin(2 * math.pi * rate * t)
