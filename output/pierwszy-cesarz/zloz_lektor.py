"""Składa lektora EN: kwestie klonu (katalog z lektor_studio.py podejscia --teatr) + kwestie przeczytane przez autora.

Kwestie autora (output/pierwszy-cesarz/build/autor_10/<klucz>.wav, pocięte z oczyszczonego nagrania) dostają to samo
obniżenie i ciepłą korekcję co próbka klonu (OBNIZ półtonu), żeby brzmiały jednym głosem; tempo i pauzy zostają autora.
Obecny lektor_en/ idzie do kopii, potem lektor_en/ = klon + autor; dane.py liczy długości ujęć z lektor_en/*.json.

uruchom:  python3 output/pierwszy-cesarz/zloz_lektor.py <katalog klonu> [--bez-autora] [--klon handan,pretekst] [--cel <katalog>]
"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
import os  # noqa: E402
os.environ["JEZYK"] = "en"
from dane import kwestia, ujecia  # noqa: E402

OBNIZ = 0.25  # półtonu — jak próbka klonu pilot/assets/ref_en_teatr_nizej_0.25pt.wav
CIEPLO = ("lowshelf=f=160:g=3,equalizer=f=3500:t=q:w=1.2:g=-2.5,highshelf=f=7000:g=-2,"
          "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1.5,loudnorm=I=-16:TP=-2")


def dlugosc(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True)
    return round(float(out.stdout), 3)


def main(klon, z_autorem=True, cel=None, klon_zamiast=()):
    """cel — katalog wyniku (domyślnie lektor_en/, który czyta Studio); klon_zamiast — kwestie autora, w których
    zostaje klon (reżyser 16.11: kwestie 2 i 6 — klon)."""
    klon = Path(klon)
    na_studio = cel is None
    cel = Path(cel) if cel else HERE / "lektor_en"
    kopia = HERE / "build" / "lektor_en_przed_zlozeniem"
    if not na_studio and cel.exists():
        shutil.rmtree(cel)
    if na_studio and cel.exists():
        if kopia.exists():
            shutil.rmtree(kopia)
        shutil.copytree(cel, kopia)
        shutil.rmtree(cel)
    shutil.copytree(klon, cel)  # klon: <klucz>.wav + .json + podejscia/
    autor = HERE / "build" / "autor_10"
    f = 2 ** (-OBNIZ / 12)
    uzyte = []
    for u in ujecia():
        klucz, txt = u[2], kwestia(u[7])
        src = autor / f"{klucz}.wav"
        if not (z_autorem and txt and src.exists()) or klucz in klon_zamiast:
            continue
        dst = cel / f"{klucz}.wav"
        shutil.copy2(dst, cel / f"{klucz}.klon.wav")  # zapas: kwestia klonu
        sr = 44100
        # bez obcinania ciszy (cięło wybrzmienie słów — reżyser 16.11): kwestia jest już pocięta z zapasem, brzegi wchodzą
        # i wygasają łagodnie
        af = (f"asetrate={sr}*{f:.6f},aresample={sr},atempo={1 / f:.6f}," + CIEPLO + ",afade=t=in:d=0.04")
        dl0 = dlugosc(src) * f / f  # długość się nie zmienia (asetrate + atempo)
        af += f",afade=t=out:st={max(0.0, dl0 - 0.12):.3f}:d=0.12"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-af", af, "-ar", str(sr), "-ac", "1",
                        "-c:a", "pcm_s16le", str(dst)], check=True)
        meta = json.loads((cel / f"{klucz}.json").read_text(encoding="utf-8"))
        meta.update(duration=dlugosc(dst), zrodlo="autor (nagranie 15.11.2026, oczyszczone, niżej o 0,25 półtonu)",
                    klon_zapas=f"{klucz}.klon.wav")
        (cel / f"{klucz}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        uzyte.append(klucz)
    n = len(list(cel.glob("*.json")))
    print(f"lektor_en: {n} kwestii, w tym głosem autora: {', '.join(uzyte) or 'żadna'}; poprzedni lektor w {kopia}")


if __name__ == "__main__":
    a = sys.argv[1:]
    cel = a[a.index("--cel") + 1] if "--cel" in a else None
    kl = a[a.index("--klon") + 1].split(",") if "--klon" in a else ()
    main(a[0], "--bez-autora" not in a, cel, kl)
