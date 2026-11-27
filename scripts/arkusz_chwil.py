"""Arkusz klatek z wybranych chwil ujęć teatru papierowego — do kontroli gagów, markerów reżysera i poprawek.

Uruchom z katalogu filmu (tam, gdzie leży render.py):
  cd output/<film>
  JEZYK=en python3 <YT>/scripts/arkusz_chwil.py arkusz.jpg klucz:0.1,0.5,-0.4 inny:2.53s,9.8s   (<YT> = główny katalog;
  katalog filmu bywa dowiązaniem do worktree, więc ścieżka względna ../../scripts trafia nie tam)
  BOX='{"miecz:2.53s": [[170, 392, 311, 645]]}' JEZYK=en python3 <YT>/scripts/arkusz_chwil.py markery.jpg miecz:2.53s

Chwila: ułamek długości ujęcia (0.5), sekundy od początku ujęcia („2.53s”, tak jak marker w Studio) albo sekundy od
końca (liczba ujemna, „-0.4”). BOX (JSON) rysuje różowe ramki w pikselach ekranu 1280 × 720 — obrys markera reżysera
ze `scripts/uwagi_rezysera.py`, żeby było widać, czego dotyczy. Miniatury 640 × 360, po 3 w rzędzie, z podpisem
„odnośnik klucz sekunda/długość”. Wzór: „Syn słońca” EN, markery i gagi 18–20.11.2026.
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
args = sys.argv[1:]
sys.argv = ["x"]  # render.py czyta własne argumenty przy imporcie
import render as R  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

if len(args) < 2:
    sys.exit(__doc__)
out, specs = args[0], args[1:]
box = json.loads(os.environ.get("BOX", "{}"))
tiles = []
for spec in specs:
    k, fr = spec.split(":")
    i = R.KOL.index(k)
    a, b = R.SCENES[i][:2]
    for f in fr.split(","):
        t = a + float(f[:-1]) if f.endswith("s") else (b + float(f) if float(f) < 0 else a + (b - a) * float(f))
        im = R.frame(t).convert("RGB").resize((640, 360))
        d = ImageDraw.Draw(im)
        for x0, y0, x1, y1 in box.get(f"{k}:{f}", []):
            d.rectangle((x0 / 2, y0 / 2, x1 / 2, y1 / 2), outline=(255, 0, 255), width=2)
        d.text((8, 8), f"{R.ODN[i]} {k} {t - a:.1f}/{b - a:.1f}s", fill=(255, 255, 0))
        tiles.append(im)
cols = 3
sheet = Image.new("RGB", (640 * cols, 360 * ((len(tiles) + cols - 1) // cols)))
for n, im in enumerate(tiles):
    sheet.paste(im, ((n % cols) * 640, (n // cols) * 360))
sheet.save(out, quality=85)
print(out, len(tiles))
