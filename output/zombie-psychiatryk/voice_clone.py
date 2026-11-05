"""Lektor klonem głosu (Chatterbox Multilingual na CUDA) → voice/l1..l5.wav i voice/p2_l1..l5.wav.

uruchom: C:\\Users\\igorf\\.zombie-tts\\venv\\Scripts\\python -I voice_clone.py probka.m4a [--takes 8] [--refs 3] [--parts 1 2]
        [--lang en]   → voice/en/, angielski model Chatterbox
Najlepiej podać próbkę po studio_clean.py (bez pogłosu pokoju) — Chatterbox kopiuje akustykę referencji.

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
PARTS_EN = {
    1: [
        ("l1", "At the asylum on Forest Road, someone was always screaming.", 3.4),
        ("l2", "But that night, all of Ward C went silent.", 2.6),
        ("l3", "Mr. Henry stood at the isolation window. He didn't blink.", 3.6),
        ("l4", "That's when I realized the doors behind me were open.", 3.4),
        ("l5", "All of them.", 1.2),
    ],
    2: [
        ("p2_l1", "I ran for the nurses' station at the end of the hall.", 3.0),
        ("p2_l2", "I locked the door and turned off the light.", 2.8),
        ("p2_l3", "Through the glass, I watched them shuffle past.", 3.0),
        ("p2_l4", "Then the phone rang.", 2.0),
        ("p2_l5", "And every head turned at once.", 2.8),
    ],
}
# sucho, bez pogłosu: przycięta cisza, odszumienie, bramka na szum między słowami
FX = ("silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "highpass=f=70,agate=threshold=0.02:ratio=3:release=120,"
      # „studio”: równa głośność i bliskość mikrofonu — kompresja, mniej buczenia, więcej czytelności
      "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
      "equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=4200:t=q:w=1.2:g=2,"
      "loudnorm=I=-16:TP=-2")
MAX_TEMPO = 1.15   # tyle można przyspieszyć bez słyszalnego „chipmunka”
MAX_CER = 0.08     # powyżej tego Whisper słyszy inne słowa

ap = argparse.ArgumentParser()
ap.add_argument("sample")
ap.add_argument("--takes", type=int, default=8, help="podejść na każde okno referencji")
ap.add_argument("--refs", type=int, default=3, help="ile 10-sekundowych okien próbki wypróbować")
ap.add_argument("--parts", type=int, nargs="+", default=[1, 2])
ap.add_argument("--lang", choices=["pl", "en"], default="pl")
ap.add_argument("--lines", nargs="+", help="tylko te zdania, np. p2_l4 p2_l5 (dogrywka po przerwanym biegu)")
ap.add_argument("--no-sv", action="store_true", help="bez sędziego podobieństwa WavLM (mało RAM/dysku)")
args = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")  # konsola Windows (cp1250) nie ma „→”
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
# sędziowie (Whisper, WavLM) na CPU poza CUDA — na MPS nie wszystkie operacje działają, a RAM jest ciasny
judge = device if device == "cuda" else "cpu"
if args.lang == "en":
    PARTS = PARTS_EN
OUT = HERE / "voice" if args.lang == "pl" else HERE / "voice" / args.lang

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
from chatterbox.tts import ChatterboxTTS  # noqa: E402
from transformers import AutoFeatureExtractor, WavLMForXVector, pipeline  # noqa: E402

# angielski model (~3 GB) tylko na CUDA; na Macu wielojęzyczny, już pobrany, też mówi po angielsku
english_model = args.lang == "en" and device == "cuda"
model = (ChatterboxTTS if english_model else ChatterboxMultilingualTTS).from_pretrained(device=device)
asr_model = "openai/whisper-large-v3" if judge == "cuda" else "openai/whisper-base"
asr = pipeline("automatic-speech-recognition", model=asr_model, device=judge,
               dtype=torch.float16 if device == "cuda" else torch.float32)
if not args.no_sv:
    sv_fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-base-plus-sv")
    sv = WavLMForXVector.from_pretrained("microsoft/wavlm-base-plus-sv").to(judge).eval()


def xvec(wav16):
    inp = sv_fe(wav16, sampling_rate=16000, return_tensors="pt").to(judge)
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
if not args.no_sv:
    target = np.mean([xvec(c) for c in chunks if len(c) > 16000], axis=0)
    target /= np.linalg.norm(target)

OUT.mkdir(parents=True, exist_ok=True)
report = {}
for name, text, limit in [ln for part in args.parts for ln in PARTS[part] if not args.lines or ln[0] in args.lines]:
    takes = []
    for r, ref in enumerate(refs):
        model.prepare_conditionals(str(ref), exaggeration=0.55)
        for k in range(args.takes):
            torch.manual_seed(1000 + 37 * r + k)
            lang_kw = {} if english_model else {"language_id": args.lang}
            wav = model.generate(text, exaggeration=0.55, cfg_weight=0.35, temperature=0.7, **lang_kw)
            raw = tmp / f"{name}_{r}_{k}.wav"
            sf.write(raw, wav.squeeze(0).cpu().numpy(), model.sr)
            fx = tmp / f"{name}_{r}_{k}_fx.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", FX,
                            "-ar", "44100", "-ac", "1", str(fx)], check=True)
            y16, _ = librosa.load(raw, sr=16000)
            heard = asr({"raw": y16, "sampling_rate": 16000},
                        generate_kwargs={"language": {"pl": "polish", "en": "english"}[args.lang],
                                         "task": "transcribe"})["text"]
            t = dict(ref=r, take=k, dur=round(sf.info(fx).duration, 3), cer=round(cer(text, heard), 3),
                     sim=0.0 if args.no_sv else round(float(xvec(y16) @ target), 4), heard=heard.strip(), fx=str(fx))
            takes.append(t)
            print(f"{name} ref{r} take{k}: {t['dur']:.2f}s (okno {limit}s) CER={t['cer']:.2f} "
                  f"podobieństwo={t['sim']:.3f}  „{t['heard']}”", flush=True)

    def score(t):
        return (t["cer"] <= MAX_CER, t["dur"] <= limit * MAX_TEMPO, t["sim"] - t["cer"])

    best = max(takes, key=score)
    tempo = min(MAX_TEMPO, max(1.0, best["dur"] / limit))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", best["fx"], "-af", f"atempo={tempo:.3f}",
                    "-ar", "44100", "-ac", "1", str(OUT / f"{name}.wav")], check=True)
    print(f"→ {name}.wav: ref{best['ref']} take{best['take']} {best['dur'] / tempo:.2f}s "
          f"CER={best['cer']:.2f} podobieństwo={best['sim']:.3f}", flush=True)
    report[name] = dict(text=text, limit=limit, chosen=best, takes=takes)

(OUT / ("raport.json" if not args.lines else f"raport-{'-'.join(args.lines)}.json")).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
