"""Arkusz klatek ujęć z rigiem (WYTYCZNE_UJEC 3.1): wiersz = ujęcie, kolumny = chwile ujęcia (początek → koniec).

uruchom:  python -I arkusz_rig.py <wynik.png> 5:15 12:6 18:13 …   (dzień:ujęcie; bez listy — wszystkie ujęcia z RIG dnia)
          python -I arkusz_rig.py <wynik.png> dzien=7                (cały dzień z RIG)
Kolumny: 6 chwil od 5% do 95% długości ujęcia, napis: akcje rigu. FILM_RIG=0 — te same klatki bez rigu.
"""
import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("FILM_LANG", "en")
os.environ.setdefault("FILM_RES", "720")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import rig_dni  # noqa: E402

out = Path(sys.argv[1])
args = sys.argv[2:]
shots = []
for a in args:
    if a.startswith("dzien="):
        d = int(a[6:])
        shots += [(d, i) for i in sorted(rig_dni.RIG.get(d, {}))]
    else:
        d, i = a.split(":")
        shots.append((int(d), int(i)))
TW, TH, COLS = 384, 216, (0.05, 0.25, 0.45, 0.65, 0.8, 0.95)
sheet = Image.new("RGB", (TW * len(COLS) + 300, TH * len(shots)), (20, 20, 20))
dr = ImageDraw.Draw(sheet)
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
for r, (d, i) in enumerate(shots):
    m = importlib.import_module(f"render_d{d:02d}")
    a, b = m.SCENES[i][0], m.SCENES[i][1]
    for c, f in enumerate(COLS):
        img = m.frame(a + (b - a) * f).resize((TW, TH))
        sheet.paste(img, (300 + c * TW, r * TH))
    spec = rig_dni.RIG.get(d, {}).get(i, {})
    txt = f"d{d:02d}_{i:02d}  {b - a:.1f}s\n" + "\n".join(f"{w}: {s}" for w, s in spec.items())
    dr.multiline_text((8, r * TH + 8), txt[:400], font=font, fill=(230, 230, 220))
sheet.save(out)
print(out, len(shots), "ujęć")
