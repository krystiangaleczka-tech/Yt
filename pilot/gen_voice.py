"""Narration with Kokoro-82M (Apache-2.0), fully local."""
from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).parent
TEXT = ("In nineteen ninety-seven, underwater microphones across the Pacific "
        "caught a sound louder than any whale on record. "
        "They called it... The Bloop.")

kokoro = Kokoro(str(ROOT / "models/kokoro-v1.0.onnx"), str(ROOT / "models/voices-v1.0.bin"))
samples, sr = kokoro.create(TEXT, voice="am_michael", speed=1.08, lang="en-us")
(ROOT / "assets").mkdir(exist_ok=True)
sf.write(ROOT / "assets/voice.wav", samples, sr)
print(f"{len(samples) / sr:.2f}s")
