"""Pierwszy cesarz — gotowy film z dźwiękiem, bez Studio (na PC po renderze klipów).

1. Muzyka i efekty (efekty.py) liczone od nowa z prawdziwych długości lektora → dzwiek/muzyka.wav, dzwiek/efekty.wav.
2. Ścieżka lektora: każda kwestia w swoim ujęciu po oddechu 0,6 s (jak ścieżka Lektor w Studio).
3. Miks: lektor 1,0 + muzyka 0,8 + efekty 1,0 (głośności jak w Studio) → dzwiek/miks.wav.
4. Klipy ujęć po kolei, każdy przycięty do długości ujęcia na osi (dźwięk nie rozjeżdża się z obrazem), + miks
   → pierwszy-cesarz.mp4 (1280 × 720, 24 kl./s, AAC 192 kb/s).

uruchom:  python output/pierwszy-cesarz/montaz.py [katalog_klipów] [plik_wyjściowy]
          (domyślnie: klipy w repozytorium / paczce i pierwszy-cesarz.mp4 obok nich)
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "docs/filmy/pierwszy-cesarz/ujecia"))

import efekty  # noqa: E402
import render as R  # noqa: E402
from dane import kwestia, okno_kwestii, ujecia  # noqa: E402

SR = efekty.SR


def czytaj(path):
    with wave.open(str(path)) as w:
        if w.getframerate() != SR or w.getsampwidth() != 2:
            raise SystemExit(f"{path}: oczekiwano 44,1 kHz 16 bit")
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(axis=1)


def lektor(n):
    out, t0, brak = np.zeros(n, np.float32), 0.0, []
    for _, _, klucz, _, _, sec, _, snd in ujecia():
        if kwestia(snd):
            wav = HERE / "lektor" / f"{klucz}.wav"
            if not wav.exists():
                brak.append(klucz)
            else:
                x = czytaj(wav)
                i = int(round((t0 + okno_kwestii(snd)[0]) * SR))
                out[i:i + len(x)] += x[:max(0, n - i)]
        t0 += sec
    if brak:
        raise SystemExit(f"Brak nagrań lektora: {', '.join(brak)}. Najpierw nagraj_lektora.bat.")
    return out


def main(klipy, wynik):
    klipy = Path(klipy)
    pliki = [klipy / f"{o}.mp4" for o in R.ODN]
    brak = [p.name for p in pliki if not p.exists()]
    if brak:
        raise SystemExit(f"Brak {len(brak)} klipów w {klipy} (np. {brak[0]}). Najpierw renderuj.bat.")

    print("1/4 muzyka i efekty (kilka minut)…", flush=True)
    efekty.main()
    n = int(round(R.DUR * SR))
    print("2/4 lektor…", flush=True)
    mow = lektor(n)
    print("3/4 miks…", flush=True)
    mix = mow.copy()
    for name, vol in (("muzyka", 0.8), ("efekty", 1.0)):
        x = czytaj(efekty.OUT / f"{name}.wav")[:n]
        mix[:len(x)] += x * vol
    peak = float(np.abs(mix).max())
    if peak > 0.95:
        mix *= 0.95 / peak
    with wave.open(str(efekty.OUT / "miks.wav"), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    print("4/4 film…", flush=True)
    lista = efekty.OUT / "klipy.txt"
    with open(lista, "w", encoding="utf-8") as f:
        for p, (a, b, *_) in zip(pliki, R.SCENES):
            f.write(f"file '{p.resolve().as_posix()}'\noutpoint {b - a:.4f}\n")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-stats", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-i", str(efekty.OUT / "miks.wav"), "-map", "0:v", "-map", "1:a", "-r", str(R.FPS),
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", str(wynik)], check=True)
    print(f"Gotowe: {wynik} ({R.DUR / 60:.1f} min)")


if __name__ == "__main__":
    k = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "klipy"
    main(k, Path(sys.argv[2]) if len(sys.argv) > 2 else k.parent / "pierwszy-cesarz.mp4")
