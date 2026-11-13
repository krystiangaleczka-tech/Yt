"""Składa podgląd całego filmu: klipy ujęć (render.py klipy) jeden po drugim + lektor w swoich oknach kwestii.
Bez muzyki i efektów — te dokłada Studio na Macu. Kwestie stawia na początku klipu + start okna (oddech 0,6 s),
licząc czas z prawdziwej liczby klatek klipów, więc głos nie rozjeżdża się z obrazem.

  python zloz.py <katalog z klipami> <plik wyjściowy.mp4>
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
from dane import LEKTOR, kwestia, okno_kwestii, ujecia  # noqa: E402

FPS = 24


def klatki(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def main(klipy, wynik):
    klipy, wynik = Path(klipy), Path(wynik)
    UJ = ujecia()
    lista, glosy, t = [], [], 0.0
    for akt, k, klucz, *_rest in UJ:
        clip = klipy / f"d{akt:02d}_{k:02d}.mp4"
        if not clip.exists():
            raise SystemExit(f"brak klipu: {clip}")
        snd = _rest[-1]
        if kwestia(snd):
            wav = LEKTOR / f"{klucz}.wav"  # lektor/ albo lektor_en/ (JEZYK=en)
            if not wav.exists():
                raise SystemExit(f"brak nagrania: {wav}")
            glosy.append((wav, t + okno_kwestii(snd)[0]))
        lista.append(clip)
        t += klatki(clip) / FPS
    concat = wynik.with_suffix(".lista.txt")
    concat.write_text("".join(f"file '{c.as_posix()}'\n" for c in lista), encoding="utf-8")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat)]
    for wav, _ in glosy:
        cmd += ["-i", str(wav)]
    fil = "".join(f"[{n + 1}:a]adelay={round(s * 1000)}:all=1[a{n}];" for n, (_, s) in enumerate(glosy))
    fil += "".join(f"[a{n}]" for n in range(len(glosy))) + f"amix=inputs={len(glosy)}:normalize=0,apad[g]"
    cmd += ["-filter_complex", fil, "-map", "0:v", "-map", "[g]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-shortest", "-movflags", "+faststart", str(wynik)]
    subprocess.run(cmd, check=True)
    concat.unlink()
    print(f"{wynik}: {t:.1f} s, {len(lista)} ujęć, {len(glosy)} kwestii")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
