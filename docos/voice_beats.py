"""Lektor per beat sklonowanym głosem (Chatterbox Multilingual, MIT; zostawia watermark Perth).

    ../pilot/.venv-tts/bin/python -I voice_beats.py PROJECT.json REF.wav OUT_DIR [--lang en] [--beat B03] [--sps 4.0]

Każde zdanie generowane jest osobno, przycinane z ciszy i sprowadzane do jednego tempa całego filmu
(sylaby/s, korekta 0.88–1.15), potem sklejane z naturalnymi mikropauzami. Bez wstawiania oddechów.
"""
import argparse
import hashlib
import json
import random
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

# wymowa: liczby i skróty słowami (tekst scenariusza zostaje bez zmian)
SAY = [
    (r"\bNOAA\b", "Noah"),
    (r"\b1997\b", "nineteen ninety-seven"),
    (r"\b2001\b", "two thousand one"),
    (r"\b2005\b", "two thousand five"),
    (r"\b2008\b", "two thousand eight"),
    (r"\b5,000 km\b", "five thousand kilometres"),
    (r"\b16 times\b", "sixteen times"),
    (r"\bA53a\b", "A fifty-three A"),
    (r"\b1960s\b", "nineteen-sixties"),
    (r"\b1991\b", "nineteen ninety-one"),
    (r"\bJune 22, 1993\b", "June twenty-second, nineteen ninety-three"),
    (r"\b2002\b", "two thousand two"),
    (r"\bSOSUS\b", "Sosus"),
    (r"\bCNN\b", "C. N. N."),
]


def speakable(text: str) -> str:
    for pat, rep in SAY:
        text = re.sub(pat, rep, text)
    return text


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def syllables(text: str) -> int:
    return max(1, sum(len(re.findall(r"[aeiouy]+", w.lower())) or 1 for w in re.findall(r"[A-Za-z']+", text)))


def pause_after(sent: str, nxt: str | None) -> float:
    """Mikropauzy jak w mowie: krótko w wyliczeniach, dłużej po pytaniu i przed puentą."""
    if nxt is None:
        return 0.0
    words = len(sent.split())
    p = 0.32
    if sent.endswith("?"):
        p = 0.45
    elif words <= 3 and len(nxt.split()) <= 3:  # "Train. Whistle. Slowdown."
        p = 0.2
    elif sent.endswith(":") or nxt.startswith(("“", '"')):
        p = 0.25
    if len(nxt.split()) <= 6 and words > 6:  # krótka puenta po dłuższym zdaniu
        p += 0.18
    return p + random.uniform(-0.05, 0.06)


def trim(x: np.ndarray, sr: int, thr: float = 0.012, pad: float = 0.03) -> np.ndarray:
    idx = np.where(np.abs(x) > thr)[0]
    if idx.size == 0:
        return x
    a, b = max(idx[0] - int(pad * sr), 0), min(idx[-1] + int(pad * sr), x.size)
    return x[a:b]


def atempo(x: np.ndarray, sr: int, f: float) -> np.ndarray:
    if abs(f - 1) < 0.01:
        return x
    with tempfile.TemporaryDirectory() as d:
        i, o = Path(d) / "i.wav", Path(d) / "o.wav"
        sf.write(i, x, sr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(i), "-af", f"atempo={f:.4f}", str(o)], check=True)
        y, _ = sf.read(o, dtype="float32")
    return y


ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("ref")
ap.add_argument("out")
ap.add_argument("--lang", default="en")
ap.add_argument("--beat", default="")
ap.add_argument("--sps", type=float, default=4.0, help="docelowe tempo w sylabach/s dla całego filmu")
ap.add_argument("--exaggeration", type=float, default=0.5)
ap.add_argument("--cfg", type=float, default=0.4)
ap.add_argument("--temperature", type=float, default=0.7)
ap.add_argument("--takes", type=int, default=3, help="ile podejść na zdanie poza tolerancją")
ap.add_argument("--reroll", action="store_true", help="ignoruj zapisane zdania")
a = ap.parse_args()
random.seed(7)

prj = json.loads(Path(a.project).read_text(encoding="utf-8"))
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)

device = "mps" if torch.backends.mps.is_available() else "cpu"
_load = torch.load
torch.load = lambda *x, **k: _load(*x, **{**k, "map_location": torch.device(device)})
from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # noqa: E402

model = ChatterboxMultilingualTTS.from_pretrained(device=device)
sr = model.sr

for b in prj["beats"]:
    if a.beat and b["id"] != a.beat or not b.get("narration"):
        continue
    sents = sentences(b["narration"])
    parts, log = [], []
    cache = out / "sent"
    cache.mkdir(exist_ok=True)
    for i, s in enumerate(sents):
        text = speakable(s)
        syl = syllables(text)
        cf = cache / f"{b['id']}_{hashlib.sha1(text.encode()).hexdigest()[:10]}.wav"
        if cf.exists() and not a.reroll:
            wav, _ = sf.read(cf, dtype="float32")
            rate = syl / (wav.size / sr)
        else:
            best = None
            for take in range(a.takes):
                w = model.generate(text, language_id=a.lang, audio_prompt_path=a.ref, exaggeration=a.exaggeration,
                                   cfg_weight=a.cfg, temperature=a.temperature).cpu().numpy().squeeze()
                w = trim(w.astype(np.float32), sr)
                r = syl / (w.size / sr)
                if best is None or abs(np.log(r / a.sps)) < abs(np.log(best[1] / a.sps)):
                    best = (w, r)
                if syl <= 3 or abs(np.log(r / a.sps)) < np.log(1.18):  # wystarczająco blisko celu
                    break
            wav, rate = best
            sf.write(cf, wav, sr)
        f = 1.0 if syl <= 3 else float(np.clip(a.sps / rate, 0.85, 1.2))  # krótkich słów nie mierzymy
        wav = atempo(wav, sr, f)
        fade = int(0.008 * sr)
        wav[:fade] *= np.linspace(0, 1, fade)
        wav[-fade:] *= np.linspace(1, 0, fade)
        parts += [wav, np.zeros(int(pause_after(s, sents[i + 1] if i + 1 < len(sents) else None) * sr), np.float32)]
        log.append(f"{rate:.1f}->x{f:.2f}")
    full = np.concatenate(parts)
    sf.write(out / f"{b['id']}.wav", full, sr)
    words = len(b["narration"].split())
    print(f"{b['id']}: {full.size / sr:.1f}s, {words / (full.size / sr) * 60:.0f} wpm | {' '.join(log)}", flush=True)
