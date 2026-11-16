"""Ponumerowana kopia lektora do odsłuchu: build/lektor_ponumerowany/NN_ujecie-MM_klucz_(Ty|klon).wav w kolejności filmu
i SPIS.txt (numer kwestii, ujęcie w Studio, kto czyta, długość, tekst). Pliki w lektor_en/ zostają pod kluczami ujęć,
bo po nich szuka ich dane.py i Studio.

uruchom:  JEZYK=en python3 output/pierwszy-cesarz/ponumeruj_lektor.py
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
os.environ.setdefault("JEZYK", "en")
from dane import kwestia, ujecia  # noqa: E402

src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "lektor_en"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "build" / "lektor_ponumerowany"
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
spis, n = ["Lektor „Pierwszy cesarz” (EN) w kolejności filmu — numer kwestii, ujęcie w Studio, kto czyta, długość, tekst", ""], 0
for nr_ujecia, u in enumerate(ujecia(), 1):
    klucz, txt = u[2], kwestia(u[7])
    if not txt:
        continue
    n += 1
    meta = json.loads((src / f"{klucz}.json").read_text(encoding="utf-8"))
    kto = "Ty" if "autor" in meta.get("zrodlo", "") else "klon"
    nazwa = f"{n:02d}_ujecie-{nr_ujecia:02d}_{klucz}_{kto}.wav"
    shutil.copy2(src / f"{klucz}.wav", out / nazwa)
    spis.append(f"{n:02d}  ujęcie {nr_ujecia:2d} (akt {u[0]})  {kto:4s}  {meta['duration']:5.2f} s  {klucz}\n    {txt}")
(out / "SPIS.txt").write_text("\n".join(spis) + "\n", encoding="utf-8")
print(f"{n} kwestii → {out}")
