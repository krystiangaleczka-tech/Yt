"""Multilingual Studio TTS; no English-specific text rewriting or tempo guessing."""
import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("reference")
    parser.add_argument("output")
    parser.add_argument("--language", default="pl")
    args = parser.parse_args()
    import numpy as np
    import soundfile as sf
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    # Chatterbox checkpoints are loaded on the selected device, including MPS hosts.
    original_load = torch.load
    torch.load = lambda *a, **kw: original_load(*a, **{**kw, "map_location": torch.device(device)})
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    narration = data["narration"]
    parts = []
    for text in re.split(r"(?<=[.!?])\s+", narration.strip()):
        if not text:
            continue
        audio = model.generate(text, language_id=args.language, audio_prompt_path=args.reference,
                               exaggeration=.5, cfg_weight=.4, temperature=.7).detach().cpu().numpy().squeeze()
        parts.extend([audio.astype(np.float32), np.zeros(round(model.sr*.25), dtype=np.float32)])
    if not parts:
        raise ValueError("Brak tekstu do nagrania")
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, np.concatenate(parts[:-1]), model.sr)


if __name__ == "__main__":
    main()
