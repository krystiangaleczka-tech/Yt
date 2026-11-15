"""Test A/B klonów głosu: podobieństwo mówcy (WavLM x-vector, cosinus) każdego nagrania do próbki autora.

  python podobienstwo.py <próbka.wav> <katalog A> [<katalog B> …]
Wynik: średnia i minimum na katalog (im bliżej 1, tym bardziej brzmi jak autor; ~0,86+ = ten sam mówca dla WavLM-SV).
"""
import sys
from pathlib import Path


def main(ref, *dirs):
    import soundfile as sf
    import torch
    import torchaudio
    from transformers import AutoFeatureExtractor, WavLMForXVector
    fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-base-plus-sv")
    m = WavLMForXVector.from_pretrained("microsoft/wavlm-base-plus-sv").eval()

    def emb(p):
        a, sr = sf.read(p, dtype="float32")
        a = a.mean(1) if a.ndim > 1 else a
        a = torchaudio.functional.resample(torch.from_numpy(a), sr, 16000).numpy()
        with torch.no_grad():
            e = m(**fe(a, sampling_rate=16000, return_tensors="pt")).embeddings
        return torch.nn.functional.normalize(e, dim=-1)[0]

    r = emb(ref)
    for d in dirs:
        sims = {p.stem: float(emb(p) @ r) for p in sorted(Path(d).glob("*.wav"))}
        for k, v in sims.items():
            print(f"  {Path(d).name:12s} {k:12s} {v:.3f}")
        print(f"{Path(d).name}: średnio {sum(sims.values()) / len(sims):.3f}, najsłabiej {min(sims.values()):.3f}\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
