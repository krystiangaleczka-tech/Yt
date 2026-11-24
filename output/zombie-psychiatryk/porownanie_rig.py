"""Krótki film „przed / po” rigu: wybrane ujęcia ze starego renderu (lewa) i nowego (prawa), obok siebie, z dźwiękiem
nowej wersji. Do szybkiego obejrzenia na telefonie bez otwierania Studio.

uruchom:  python -I porownanie_rig.py [wynik.mp4] [dzien:ujecie …]
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ["FILM_LANG"] = "en"
os.environ.setdefault("FILM_RES", "720")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
OLD, NEW = HERE / "build" / "en-1440-przed-rigiem", HERE / "build" / "en-1440"
PICK = [(3, 7), (5, 15), (8, 21), (9, 7), (12, 6), (16, 9), (17, 19), (18, 13), (20, 10), (25, 13), (27, 8), (29, 12)]
FONT = "C\\:/Windows/Fonts/arialbd.ttf"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "build" / "porownanie_rig.mp4"
    pick = [tuple(int(x) for x in a.split(":")) for a in sys.argv[2:]] or PICK
    import rig_dni
    tmp = Path(tempfile.mkdtemp())
    parts = []
    for k, (d, i) in enumerate(pick):
        m = importlib.import_module(f"render_d{d:02d}")
        a, b = m.SCENES[i][0], m.SCENES[i][1]
        spec = "; ".join(f"{w}: {s}" for w, s in rig_dni.RIG.get(d, {}).get(i, {}).items())
        label = f"d{d:02d}_{i:02d}   {spec}".replace("'", "").replace(":", "\\:").replace(",", "\\,")[:110]
        seg = tmp / f"{k:02d}.mp4"
        new = NEW / f"v{d:02d}.mp4"
        new_in = (["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(new)] if (NEW / f"v{d:02d}.ok").exists() else
                  ["-t", f"{b - a:.3f}", "-i", str(HERE / "build" / "studio_klipy" / f"d{d:02d}_{i:02d}.mp4")])  # klip ze Studio
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(OLD / f"v{d:02d}.mp4"),
                        *new_in,
                        "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(NEW / f"a{d:02d}.wav"),
                        "-filter_complex",
                        "[0:v]scale=960:540,drawtext=fontfile='" + FONT + "':text='PRZED':x=20:y=20:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.6[l];"
                        "[1:v]scale=960:540,drawtext=fontfile='" + FONT + "':text='PO (rig)':x=20:y=20:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.6[r];"
                        "[l][r]hstack,pad=1920:620:0:0,drawtext=fontfile='" + FONT + "':text='" + label + "':x=20:y=560:fontsize=26:fontcolor=white[v]",
                        "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                        "-r", "24", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(seg)], check=True)
        parts.append(seg)
    (tmp / "lista.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-c", "copy",
                    "-movflags", "+faststart", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main()
