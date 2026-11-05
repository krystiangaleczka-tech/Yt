"""Kontrola ujęć skryptu renderu przed oddaniem reżyserowi (docs/WYTYCZNE_UJEC.md, sekcja 3).

uruchom:  python3 scripts/kontrola_ujec.py output/<film>/render.py [output/<film>/render2.py ...]

Moduł renderu musi mieć SCENES [(start, koniec, ...)], DUR, FPS i frame(t) → PIL.Image.
Sprawdza każdą klatkę co 2 klatki renderu:
- pusta krawędź kadru (kamera odsłania koniec świata),
- jasny element gaśnie na chwilę i wraca (maska albo migotanie zjada np. oczy),
i zapisuje arkusz klatek: początek, środek i koniec każdej sceny — do obejrzenia, nie tylko do wyrenderowania.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

EDGE, BAND, BRIGHT = 4.0, 6, 200


def load(path):
    path = Path(path).resolve()
    sys.path.insert(0, str(path.parent))  # render2 importuje render z tego samego katalogu
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(path):
    mod = load(path)
    fps = getattr(mod, "FPS", None) or getattr(sys.modules.get("render"), "FPS", 24)  # dni wariantu A biorą FPS z render.py
    problems, thumbs = [], []
    for i, (a, b, *_) in enumerate(mod.SCENES):
        ts = np.arange(a, b, 2 / fps)
        bright = []
        for t in ts:
            arr = np.asarray(mod.frame(t)).astype(np.float32).mean(axis=2)
            bright.append(int((arr > BRIGHT).sum()))
            if arr.mean() < 15 or t < 0.5 or t > mod.DUR - 0.5:
                continue  # zamierzona ciemność, przejście w ciemność i wejście/wyjście z czerni
            edges = {"góra": arr[:BAND].mean(), "dół": arr[-BAND:].mean(),
                     "lewo": arr[:, :BAND].mean(), "prawo": arr[:, -BAND:].mean()}
            empty = [k for k, v in edges.items() if v < EDGE]
            if empty:
                problems.append(f"scena {i + 1}, {t:.2f} s: pusta krawędź kadru ({', '.join(empty)})")
        for k in range(1, len(bright) - 1):
            if bright[k] == 0 and bright[k - 1] > 50 and bright[k + 1] > 50:
                problems.append(f"scena {i + 1}, {ts[k]:.2f} s: jasny element gaśnie na chwilę i wraca — sprawdź na arkuszu, czy to zamierzone (np. migająca świetlówka)")
        for t in (a + 0.05, (a + b) / 2, b - 0.05):
            im = mod.frame(t).resize((384, 216))
            ImageDraw.Draw(im).text((6, 6), f"{i + 1} · {t:.2f} s", fill=(255, 255, 0))
            thumbs.append(im)
    sheet = Image.new("RGB", (384 * 3, 216 * len(mod.SCENES)))
    for k, im in enumerate(thumbs):
        sheet.paste(im, ((k % 3) * 384, (k // 3) * 216))
    out = Path(path).with_name(f"kontrola-{Path(path).stem}.png")
    sheet.save(out)
    return problems, out


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        problems, sheet = check(p)
        bad += len(problems)
        print(f"{p}: {'OK' if not problems else str(len(problems)) + ' problemów'} · arkusz klatek: {sheet}")
        for line in problems:
            print("  -", line)
    sys.exit(1 if bad else 0)
