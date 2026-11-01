"""Lektor klonem głosu (Chatterbox Multilingual na CUDA) → voice/l1..l5.wav i voice/p2_l1..l5.wav.

uruchom: C:\\Users\\igorf\\.zombie-tts\\venv\\Scripts\\python -I voice_clone.py probka.m4a [--takes 8] [--refs 3] [--parts 1 2]

Na każde zdanie: kilka 10-sekundowych okien z próbki jako referencja × kilka podejść.
Każde podejście ocenia niezależny sędzia:
  - Whisper large-v3 — czy powiedział dokładnie ten tekst (błąd znaków, CER),
  - WavLM speaker-verification — jak bardzo brzmi jak próbka (cosinus x-vectorów),
  - długość — czy mieści się w oknie ujęcia z render.py / render2.py.
Wygrywa najbardziej podobne do próbki spośród poprawnie wypowiedzianych i mieszczących się.
Raport wszystkich podejść → voice/raport.json.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch

HERE = Path(__file__).parent
# (plik, tekst, maks. długość w s — okno ujęcia w render.py / render2.py)
PARTS = {}
PARTS[1] = [
    ("l1", "W szpitalu przy Leśnej zawsze ktoś krzyczał.", 2.7),
    ("l2", "Ale tej nocy cały oddział C ucichł.", 2.5),
    ("l3", "W okienku izolatki stał pan Henryk. Nie mrugał.", 3.4),
    ("l4", "Wtedy zrozumiałem, że drzwi za mną są otwarte.", 3.3),
    ("l5", "Wszystkie.", 1.0),
]
PARTS[2] = [
    ("p2_l1", "Pobiegłem do dyżurki na końcu korytarza.", 2.6),
    ("p2_l2", "Zamknąłem drzwi i zgasiłem światło.", 2.6),
    ("p2_l3", "Przez szybę widziałem, jak przechodzą obok.", 3.3),
    ("p2_l4", "Wtedy zadzwonił telefon.", 2.0),
    ("p2_l5", "I wszyscy naraz odwrócili głowy.", 2.8),
]
# sucho, bez pogłosu: przycięta cisza, odszumienie, bramka na szum między słowami
FX = ("silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "highpass=f=70,lowpass=f=11000,afftdn=nf=-28:tn=1,agate=threshold=0.02:ratio=3:release=120,"
      "loudnorm=I=-16:TP=-2")
MAX_TEMPO = 1.15   # tyle można przyspieszyć bez słyszalnego „chipmunka”
MAX_CER = 0.08     # powyżej tego Whisper słyszy inne słowa

ap = argparse.ArgumentParser()
ap.add_argument("sample")
ap.add_argument("--takes", type=int, default=8, help="podejść na każde okno referencji")
ap.add_argument("--refs", type=int, default=3, help="ile 10-sekundowych okien próbki wypróbować")
ap.add_argument("--parts", type=int, nargs="+", default=[1, 2])
args = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")  # konsola Windows (cp1250) nie ma „→”
device = "cuda" if torch.cuda.is_available() else "cpu"

tmp = Path(tempfile.mkdtemp())
# próbka bez szumu tła i z przyciętymi pauzami — w 10 s referencji jest wtedy sama mowa
clean = tmp / "clean.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", args.sample, "-af",
                "highpass=f=70,afftdn=nf=-30,silenceremove=start_periods=1:start_threshold=-45dB:"
                "stop_periods=-1:stop_duration=0.3:stop_threshold=-45dB,loudnorm=I=-18:TP=-2",
                "-ac", "1", "-ar", "24000", str(clean)], check=True)
clean_wav, _ = librosa.load(clean, sr=24000)
total = len(clean_wav) / 24000
starts = [0.0] if total <= 10.5 else list(np.linspace(0, total - 10, args.refs))
refs = []
for k, s in enumerate(starts):
    p = tmp / f"ref{k}.wav"
    sf.write(p, clean_wav[int(s * 24000):int((s + 10) * 24000)], 24000)
    refs.append(p)
print(f"próbka po oczyszczeniu: {total:.1f}s, okna referencji od: {[round(s, 1) for s in starts]}", flush=True)

_load = torch.load
torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": torch.device(device)})
from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # noqa: E402
from transformers import AutoFeatureExtractor, WavLMForXVector, pipeline  # noqa: E402

model = ChatterboxMultilingualTTS.from_pretrained(device=device)
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device=device,
               dtype=torch.float16 if device == "cuda" else torch.float32)
sv_fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-base-plus-sv")
sv = WavLMForXVector.from_pretrained("microsoft/wavlm-base-plus-sv").to(device).eval()


def xvec(wav16):
    inp = sv_fe(wav16, sampling_rate=16000, return_tensors="pt").to(device)
    with torch.inference_mode():
        e = sv(**inp).embeddings[0]
    return torch.nn.functional.normalize(e, dim=-1).cpu().numpy()


def norm(s):
    s = unicodedata.normalize("NFC", s.lower())
    return re.sub(r"[^\w ]+", "", re.sub(r"\s+", " ", s)).strip()


def cer(ref, hyp):
    a, b = norm(ref), norm(hyp)
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[len(b)] / max(1, len(a))


# głos docelowy = średnia z kilku kawałków całej próbki
clean16 = librosa.resample(clean_wav, orig_sr=24000, target_sr=16000)
chunks = [clean16[i:i + 16000 * 4] for i in range(0, max(1, len(clean16) - 16000 * 2), 16000 * 4)]
target = np.mean([xvec(c) for c in chunks if len(c) > 16000], axis=0)
target /= np.linalg.norm(target)

(HERE / "voice").mkdir(exist_ok=True)
report = {}
for name, text, limit in [ln for part in args.parts for ln in PARTS[part]]:
    takes = []
    for r, ref in enumerate(refs):
        model.prepare_conditionals(str(ref), exaggeration=0.55)
        for k in range(args.takes):
            torch.manual_seed(1000 + 37 * r + k)
            wav = model.generate(text, language_id="pl", exaggeration=0.55, cfg_weight=0.35, temperature=0.7)
            raw = tmp / f"{name}_{r}_{k}.wav"
            sf.write(raw, wav.squeeze(0).cpu().numpy(), model.sr)
            fx = tmp / f"{name}_{r}_{k}_fx.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", FX,
                            "-ar", "44100", "-ac", "1", str(fx)], check=True)
            y16, _ = librosa.load(raw, sr=16000)
            heard = asr({"raw": y16, "sampling_rate": 16000},
                        generate_kwargs={"language": "polish", "task": "transcribe"})["text"]
            t = dict(ref=r, take=k, dur=round(sf.info(fx).duration, 3), cer=round(cer(text, heard), 3),
                     sim=round(float(xvec(y16) @ target), 4), heard=heard.strip(), fx=str(fx))
            takes.append(t)
            print(f"{name} ref{r} take{k}: {t['dur']:.2f}s (okno {limit}s) CER={t['cer']:.2f} "
                  f"podobieństwo={t['sim']:.3f}  „{t['heard']}”", flush=True)

    def score(t):
        return (t["cer"] <= MAX_CER, t["dur"] <= limit * MAX_TEMPO, t["sim"] - t["cer"])

    best = max(takes, key=score)
    tempo = min(MAX_TEMPO, max(1.0, best["dur"] / limit))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", best["fx"], "-af", f"atempo={tempo:.3f}",
                    "-ar", "44100", "-ac", "1", str(HERE / "voice" / f"{name}.wav")], check=True)
    print(f"→ {name}.wav: ref{best['ref']} take{best['take']} {best['dur'] / tempo:.2f}s "
          f"CER={best['cer']:.2f} podobieństwo={best['sim']:.3f}", flush=True)
    report[name] = dict(text=text, limit=limit, chosen=best, takes=takes)

(HERE / "voice" / "raport.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
