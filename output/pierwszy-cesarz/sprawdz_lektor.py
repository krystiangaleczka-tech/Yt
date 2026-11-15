"""Sprawdzenie podejść lektora Whisperem PO nagraniu (Mac z 8 GB: Whisper i klon głosu nie mieszczą się naraz).
Dla każdego podejścia w lektor_en/podejscia zapisuje transkrypcję i zgodność z tekstem; podejście poniżej progu
(połknięte słowo, powtórka, bełkot) dostaje „powtorzenie”: true i odpada przy wyborze (Podręcznik → Lektor, zasada 7).

uruchom:  JEZYK=en pilot/.venv-tts/bin/python -I output/pierwszy-cesarz/sprawdz_lektor.py
potem:    pilot/.venv-enhance/bin/python -I docos/lektor_studio.py podejscia output/pierwszy-cesarz/lektor_en --teatr
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lektor_en as L  # noqa: E402


def main():
    import soundfile as sf
    pod = L.OUT / "podejscia"
    asr = L.whisper(os.environ.get("LEKTOR_DEVICE", "cpu"))
    for meta_path in sorted(pod.glob("*.json")):
        if meta_path.name == "wybor.json":
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for z, info in meta["podejscia"].items():
            if "whisper" in info:
                continue
            audio, sr = sf.read(str(pod / f"{meta_path.stem}_s{z}.raw.wav"), dtype="float32")
            heard = asr(audio, sr)
            score = max(L.zgodnosc(meta["spoken"], heard), L.zgodnosc(meta["text"], heard))
            info.update(powtorzenie=info.get("powtorzenie", False) or score < L.PROG, zgodnosc=round(score, 3), whisper=heard)
            print(f"{meta_path.stem} s{z}: {score:.2f}" + ("  (odpada)" if score < L.PROG else ""), flush=True)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
