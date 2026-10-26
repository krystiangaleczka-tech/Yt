"""Clone the user's voice with Chatterbox Multilingual (MIT) and write assets/voice.wav.

usage: .venv-tts/bin/python clone_voice.py my_voice.m4a [en|pl]
"""
import subprocess
import sys
from pathlib import Path

import torch
import torchaudio as ta

ROOT = Path(__file__).parent
TEXT = {
    "en": ("In nineteen ninety-seven, underwater microphones across the Pacific "
           "caught a sound louder than any whale on record. "
           "They called it... The Bloop."),
    "pl": ("W dziewięćdziesiątym siódmym hydrofony na Pacyfiku "
           "nagrały dźwięk głośniejszy niż każdy wieloryb. "
           "Nazwano go... Bloop."),
}

src = Path(sys.argv[1])
lang = sys.argv[2] if len(sys.argv) > 2 else "en"

# clean reference: mono 24 kHz, trimmed silence, loudness-normalised, max 30 s
ref = ROOT / "assets/ref_clean.wav"
ref.parent.mkdir(exist_ok=True)
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
    "-af", "highpass=f=70,silenceremove=start_periods=1:start_threshold=-45dB:"
           "stop_periods=-1:stop_duration=0.6:stop_threshold=-45dB,loudnorm=I=-18:TP=-2",
    "-ac", "1", "-ar", "24000", "-t", "30", str(ref),
], check=True)

device = "mps" if torch.backends.mps.is_available() else "cpu"
_load = torch.load
torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": torch.device(device)})

from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # noqa: E402

model = ChatterboxMultilingualTTS.from_pretrained(device=device)
wav = model.generate(TEXT[lang], language_id=lang, audio_prompt_path=str(ref),
                     exaggeration=0.45, cfg_weight=0.4, temperature=0.7)
out = ROOT / f"assets/voice_clone_{lang}.wav"
ta.save(str(out), wav.cpu(), model.sr)
print(f"wrote {out} ({wav.shape[-1] / model.sr:.2f}s)")
