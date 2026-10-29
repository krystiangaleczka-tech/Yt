"""Draft animatic voices with Kokoro-82M (Apache-2.0). Runs in the model environment, never in the API.

Input (stdin): {"model_dir": "...", "lines": [{"text", "voice", "speed", "out"}]}
Writes one WAV per line and prints its duration in seconds as JSON lines.
"""
import json
import sys
from pathlib import Path


def main():
    job = json.load(sys.stdin)
    import soundfile as sf
    from kokoro_onnx import Kokoro
    folder = Path(job["model_dir"])
    kokoro = Kokoro(str(folder / "kokoro-v1.0.onnx"), str(folder / "voices-v1.0.bin"))
    for line in job["lines"]:
        # British voices start with "b"; everything else is spoken as American English.
        lang = "en-gb" if line["voice"].startswith("b") else "en-us"
        samples, rate = kokoro.create(line["text"], voice=line["voice"], speed=float(line["speed"]), lang=lang)
        out = Path(line["out"])
        temporary = out.with_suffix(".part.wav")
        sf.write(temporary, samples, rate)
        temporary.replace(out)
        print(json.dumps({"out": str(out), "duration": round(len(samples) / rate, 3)}), flush=True)


if __name__ == "__main__":
    main()
