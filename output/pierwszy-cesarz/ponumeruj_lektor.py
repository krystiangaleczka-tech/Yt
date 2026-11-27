"""Ponumerowana kopia lektora do odsłuchu: build/lektor_ponumerowany/NN_ujecie-MM_klucz_(Ty|klon).wav w kolejności filmu
i SPIS.txt (numer kwestii, ujęcie w Studio, kto czyta, długość, tekst). Pliki w lektor_en/ zostają pod kluczami ujęć,
bo po nich szuka ich dane.py i Studio.

uruchom:  JEZYK=en python3 output/pierwszy-cesarz/ponumeruj_lektor.py [katalog lektora] [katalog wyniku] [--calosc plik.m4a]
          --calosc: cały lektor w jednym pliku, kwestie po kolei z sekundą przerwy; w SPIS-ie czas startu każdej
          kwestii w tym pliku (reżyser podaje minutę z odsłuchu, np. „7:21” → numer kwestii)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
os.environ.setdefault("JEZYK", "en")
from dane import kwestia, ujecia  # noqa: E402

args = sys.argv[1:]
calosc = Path(args.pop(args.index("--calosc") + 1)) if "--calosc" in args else None
args = [a for a in args if a != "--calosc"]
src = Path(args[0]) if len(args) > 0 else HERE / "lektor_en"
out = Path(args[1]) if len(args) > 1 else HERE / "build" / "lektor_ponumerowany"
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
spis, n = ["Lektor „Pierwszy cesarz” (EN) w kolejności filmu — numer kwestii, ujęcie w Studio, kto czyta, długość, tekst"
           + (f"; [m:ss] — start kwestii w {calosc.name}" if calosc else ""), ""], 0
tmp = Path(tempfile.mkdtemp()) / "calosc.wav" if calosc else None
w, t = None, 0.0
for nr_ujecia, u in enumerate(ujecia(), 1):
    klucz, txt = u[2], kwestia(u[7])
    if not txt:
        continue
    n += 1
    meta = json.loads((src / f"{klucz}.json").read_text(encoding="utf-8"))
    kto = "Ty" if "autor" in meta.get("zrodlo", "") else "klon"
    nazwa = f"{n:02d}_ujecie-{nr_ujecia:02d}_{klucz}_{kto}.wav"
    shutil.copy2(src / f"{klucz}.wav", out / nazwa)
    czas = ""
    if calosc:
        with wave.open(str(src / f"{klucz}.wav")) as r:
            if w is None:
                w = wave.open(str(tmp), "wb")
                w.setparams(r.getparams())
                cisza = b"\0" * r.getsampwidth() * r.getnchannels() * r.getframerate()  # sekunda przerwy
            czas = f"[{int(t // 60)}:{int(t % 60):02d}]  "
            w.writeframes(r.readframes(r.getnframes()) + cisza)
            t += r.getnframes() / r.getframerate() + 1.0
    spis.append(f"{n:02d}  {czas}ujęcie {nr_ujecia:2d} (akt {u[0]})  {kto:4s}  {meta['duration']:5.2f} s  {klucz}\n    {txt}")
(out / "SPIS.txt").write_text("\n".join(spis) + "\n", encoding="utf-8")
if calosc:
    w.close()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-c:a", "aac", "-b:a", "128k", str(calosc)],
                   check=True)
    print(f"całość {int(t // 60)}:{int(t % 60):02d} → {calosc}")
print(f"{n} kwestii → {out}")
