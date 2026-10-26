"""Odtwarza media projektu (nie trzymamy ich w repo) na podstawie rejestrów licencji.

    python3 fetch_media.py ../projekty/bloop_v3

- pliki z Wikimedia Commons: z `raw/*/licenses.json` (tytuł pliku, licencja, autor)
- nagrania i spektrogramy NOAA PMEL (domena publiczna): lista poniżej
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
NOAA = {
    "noaa": [
        "https://www.pmel.noaa.gov/acoustics/sounds/bloop.wav",
        "https://www.pmel.noaa.gov/acoustics/sounds/A53JD33Calving_3x.wav",
        "https://www.pmel.noaa.gov/acoustics/sounds/HarmonicTremor2006_215_09_20UsedOnBloopWebsite.wav",
        "https://www.pmel.noaa.gov/acoustics/spectrograms/bloop.jpg",
        "https://www.pmel.noaa.gov/acoustics/spectrograms/icequake-JD33CalvingHF1.png",
        "https://www.pmel.noaa.gov/acoustics/spectrograms/IcebergHarmonicTremor_HighFreq.png",
    ]
}
# fragmenty przycinane po pobraniu: plik -> (oryginał, start, długość)
TRIMS = {"v_sub_interior_crew_1080.mp4": ("v_sub_interior_crew.webm", 140, 170)}


def main():
    root = Path(sys.argv[1]).resolve()
    raw = root / "raw"
    for folder, urls in NOAA.items():
        out = raw / folder
        out.mkdir(parents=True, exist_ok=True)
        for u in urls:
            dst = out / u.rsplit("/", 1)[1]
            if not dst.exists():
                print("NOAA", dst.name)
                urllib.request.urlretrieve(u, dst)
    for ledger in sorted(raw.glob("*/licenses.json")):
        for x in json.loads(ledger.read_text()):
            name = x["file"]
            if (ledger.parent / name).exists():
                continue
            src_name = TRIMS.get(name, (name,))[0]
            stem = Path(src_name).stem
            print("Commons", x["title"])
            subprocess.run([sys.executable, str(HERE / "fetch_commons.py"), "get", x["title"], str(ledger.parent),
                            "--name", stem], check=False)
            if name in TRIMS:
                orig, ss, t = TRIMS[name]
                p = ledger.parent / orig
                if p.exists():
                    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(ss), "-t", str(t), "-i", str(p),
                                    "-vf", "scale=1920:-2", "-c:v", "libx264", "-crf", "23", "-an", str(ledger.parent / name)])
                    p.unlink()
    print("gotowe")


if __name__ == "__main__":
    main()
