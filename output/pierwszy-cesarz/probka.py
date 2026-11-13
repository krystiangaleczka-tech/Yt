"""Przygotowanie próbki głosu do klonowania: czyszczenie + transkrypcja Whisperem.

  python probka.py <nagranie (wav/mp3/m4a)> <wyjście.wav> [en|pl]

Robi: <wyjście>.wav (mono 24 kHz, bez szumu niskich, bez ciszy na brzegach, ta sama głośność) + <wyjście>.txt (transkrypcja)
oraz <wyjście>_prompt.wav/.txt — pierwsze pełne zdania do ok. 15 s (VoxCPM2 kontynuuje nagranie z promptu; krótszy = szybciej).
"""
import subprocess
import sys
from pathlib import Path


def main(src, out, lang="en"):
    import soundfile as sf
    import torch
    from transformers import pipeline
    out = Path(out)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af",
                    "highpass=f=70,afftdn=nf=-30,"
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.2,areverse,loudnorm=I=-18:TP=-2",
                    "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(out)], check=True)
    audio, sr = sf.read(out, dtype="float32")
    pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device="cuda", dtype=torch.float16)
    import torchaudio
    x = torchaudio.functional.resample(torch.from_numpy(audio), sr, 16000).numpy()
    r = pipe({"raw": x, "sampling_rate": 16000}, return_timestamps=True,
             generate_kwargs={"language": "english" if lang == "en" else "polish", "task": "transcribe"})
    out.with_suffix(".txt").write_text(r["text"].strip(), encoding="utf-8")
    print(f"{out}: {len(audio) / sr:.1f} s\n{r['text'].strip()}")
    # prompt: kolejne fragmenty do ok. 15 s, ucięte na końcu zdania
    txt, end = [], 0.0
    for ch in r["chunks"]:
        a, b = ch["timestamp"]
        if b is None or (b > 16 and txt):
            break
        txt.append(ch["text"].strip())
        end = b
        if b > 9 and ch["text"].strip().endswith((".", "!", "?")):
            break
    pr = out.with_name(out.stem + "_prompt.wav")
    sf.write(pr, audio[:int(min(len(audio), (end + 0.25) * sr))], sr)
    pr.with_suffix(".txt").write_text(" ".join(txt), encoding="utf-8")
    print(f"{pr}: {end:.1f} s — {' '.join(txt)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
