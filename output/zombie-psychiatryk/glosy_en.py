"""Głosy wersji angielskiej (US) całego wariantu A: zimne otwarcie + dni 1–30, każda postać własnym klonem.

uruchom: C:\\Users\\igorf\\.zombie-tts\\venv\\Scripts\\python -I glosy_en.py \\
            --glos narrator="F:/claude/glosy/Głos*.m4a" --glos malec="F:/claude/glosy/*WA0001.m4a,F:/claude/glosy/*WA0002.m4a" \\
            --glos nowak="F:/claude/glosy/*WA0003.m4a,F:/claude/glosy/*WA0004.m4a" [--dni 0 1 2] [--takes 3] [--refs 2]
Postać bez --glos zostaje bez głosu (w filmie sam napis) — dograć: ten sam skrypt z jej próbką, gotowe pliki są pomijane.

Wynik: voice/en/l*.wav, p2_l*.wav (otwarcie, render.py/render2.py) i voice/en/dni/dNN_II.wav (dzień, ujęcie).
Na każdą kwestię: refs okien referencji × takes podejść; Whisper large-v3 (czy padł ten tekst), WavLM (podobieństwo do
próbki postaci), długość (musi się zmieścić w ujęciu; najwyżej ×1,15 szybciej). Raport: voice/en/dni/raport.json.
"""
import argparse
import glob
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
import en_film  # noqa: E402
from kwestie_en import tts_text  # noqa: E402

# zimne otwarcie: (plik, tekst, maks. długość) — jak PARTS_EN w voice_clone.py
OPENING = [
    ("l1", "At the asylum on Forest Road, someone was always screaming.", 3.6),
    ("l2", "But that night, all of Ward C went silent.", 2.8),
    ("l3", "Mr. Henry stood at the isolation window. He didn't blink.", 3.8),
    ("l4", "That's when I realized the doors behind me were open.", 3.6),
    ("l5", "All of them.", 1.3),
    ("p2_l1", "I ran for the nurses' station at the end of the hall.", 3.2),
    ("p2_l2", "I locked the door and turned off the light.", 3.0),
    ("p2_l3", "Through the glass, I watched them shuffle past.", 3.3),
    ("p2_l4", "Then the phone rang.", 2.0),
    ("p2_l5", "And every head turned at once.", 2.9),
]
FX = ("silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "highpass=f=70,agate=threshold=0.02:ratio=3:release=120,"
      "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
      "equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=4200:t=q:w=1.2:g=2,"
      "loudnorm=I=-16:TP=-2")
MAX_TEMPO = 1.15
MAX_CER = 0.08

ap = argparse.ArgumentParser()
ap.add_argument("--glos", action="append", default=[], help="postać=wzorzec[,wzorzec] próbek (glob)")
ap.add_argument("--dni", type=int, nargs="+", default=list(range(0, 31)))
ap.add_argument("--takes", type=int, default=3)
ap.add_argument("--refs", type=int, default=2)
ap.add_argument("--nadpisz", action="store_true", help="generuj także te, które już są")
args = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")
dev = "cuda"
OUT = HERE / "voice" / "en" / "dni"
OUT.mkdir(parents=True, exist_ok=True)
tmp = Path(tempfile.mkdtemp())

# ---------- lista kwestii ----------
from a_dane1 import DAYS as D1  # noqa: E402
from a_dane2 import DAYS as D2  # noqa: E402
from tempo import kwestie  # noqa: E402

jobs = []  # (postać, sposób, plik wyjściowy, tekst do TTS, maks. długość)
voices = {g.split("=", 1)[0].strip().lower(): g.split("=", 1)[1] for g in args.glos}
for d in D1 + D2:
    day = d[0]
    if day not in args.dni:
        continue
    if day == 0:
        if "narrator" in voices:
            jobs += [("narrator", "", HERE / "voice" / "en" / f"{n}.wav", t, lim) for n, t, lim in OPENING]
        continue
    rows = [s for _, _, beats in d[2] for _, shots in beats for s in shots]
    wins = kwestie(d) if day != 1 else [(0.5, 0)] * len(rows)
    for i, (row, (vs, vl)) in enumerate(zip(rows, wins)):
        who, how = en_film.speaker(row[4])
        if who in voices:
            T = row[2]
            jobs.append((who, how, en_film.voice_file(day, i), tts_text(en_film.EN[f"{day}.{i}"]), T - 0.4))
todo = [j for j in jobs if args.nadpisz or not j[2].exists()]
print(f"kwestii z głosem: {len(jobs)}, do zrobienia: {len(todo)}; postacie: {sorted(voices)}", flush=True)
if not todo:
    raise SystemExit

# ---------- próbki: czyszczenie, okna referencji ----------
refs, clean_all = {}, {}
for who, pats in voices.items():
    files = sorted({f for p in pats.split(",") for f in glob.glob(p.strip())})
    assert files, f"brak próbek dla {who}: {pats}"
    wavs = []
    for k, f in enumerate(files):
        c = tmp / f"{who}_{k}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-af",
                        "highpass=f=70,afftdn=nf=-30,silenceremove=start_periods=1:start_threshold=-45dB:"
                        "stop_periods=-1:stop_duration=0.3:stop_threshold=-45dB,loudnorm=I=-18:TP=-2",
                        "-ac", "1", "-ar", "24000", str(c)], check=True)
        wavs.append(librosa.load(c, sr=24000)[0])
    allw = np.concatenate(wavs)
    clean_all[who] = allw
    total = len(allw) / 24000
    starts = list(np.linspace(5, total - 15, args.refs)) if total > 25 else [0.0]
    refs[who] = []
    for k, s in enumerate(starts):
        p = tmp / f"{who}_ref{k}.wav"
        sf.write(p, allw[int(s * 24000):int((s + 10) * 24000)], 24000)
        refs[who].append(p)
    print(f"{who}: {len(files)} pliki, {total:.0f}s mowy po czyszczeniu, okna od {[round(s) for s in starts]}", flush=True)

_load = torch.load
torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": torch.device(dev)})
from chatterbox.tts import ChatterboxTTS  # noqa: E402
from transformers import AutoFeatureExtractor, WavLMForXVector, pipeline  # noqa: E402

model = ChatterboxTTS.from_pretrained(device=dev)
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device=dev, dtype=torch.float16)
sv_fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-base-plus-sv")
sv = WavLMForXVector.from_pretrained("microsoft/wavlm-base-plus-sv").to(dev).eval()


def xvec(wav16):
    inp = sv_fe(wav16, sampling_rate=16000, return_tensors="pt").to(dev)
    with torch.inference_mode():
        e = sv(**inp).embeddings[0]
    return torch.nn.functional.normalize(e, dim=-1).cpu().numpy()


def norm(s):
    s = unicodedata.normalize("NFC", s.lower())
    s = re.sub(r"\b(zosha|zosia)\b", "zosia", s)
    return re.sub(r"[^\w ]+", "", re.sub(r"[-\s]+", " ", s)).strip()


def cer(ref, hyp):
    a, b = norm(ref), norm(hyp)
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[len(b)] / max(1, len(a))


target = {}
for who, allw in clean_all.items():
    w16 = librosa.resample(allw, orig_sr=24000, target_sr=16000)
    ch = [w16[i:i + 64000] for i in range(0, max(1, len(w16) - 32000), 64000)]
    v = np.mean([xvec(c) for c in ch if len(c) > 16000], axis=0)
    target[who] = v / np.linalg.norm(v)

rep_path = OUT / "raport.json"
report = json.loads(rep_path.read_text(encoding="utf-8")) if rep_path.exists() else {}
cond = None
for n, (who, how, out, text, limit) in enumerate(sorted(todo, key=lambda j: j[0]), 1):
    takes = []
    for r, ref in enumerate(refs[who]):
        if cond != (who, r):
            model.prepare_conditionals(str(ref), exaggeration=0.5)
            cond = (who, r)
        for k in range(args.takes):
            torch.manual_seed(1000 + 37 * r + k)
            wav = model.generate(text, exaggeration=0.5, cfg_weight=0.4, temperature=0.7)
            raw = tmp / f"x_{r}_{k}.wav"
            sf.write(raw, wav.squeeze(0).cpu().numpy(), model.sr)
            fx = tmp / f"x_{r}_{k}_fx.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", FX, "-ar", "44100", "-ac", "1",
                            str(fx)], check=True)
            y16, _ = librosa.load(raw, sr=16000)
            heard = asr({"raw": y16, "sampling_rate": 16000},
                        generate_kwargs={"language": "english", "task": "transcribe"})["text"].strip()
            takes.append(dict(ref=r, take=k, dur=round(sf.info(fx).duration, 3), cer=round(cer(text, heard), 3),
                              sim=round(float(xvec(y16) @ target[who]), 4), heard=heard, fx=str(fx)))

    def score(t):
        return (t["cer"] <= MAX_CER, t["dur"] <= limit * MAX_TEMPO, t["sim"] - t["cer"])

    best = max(takes, key=score)
    tempo = min(MAX_TEMPO, max(1.0, best["dur"] / limit))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", best["fx"], "-af", f"atempo={tempo:.3f}",
                    "-ar", "44100", "-ac", "1", str(out)], check=True)
    flag = "" if best["cer"] <= MAX_CER and best["dur"] <= limit * MAX_TEMPO else "  <-- SPRAWDZIĆ"
    print(f"[{n}/{len(todo)}] {who:8s} {out.name}: {best['dur'] / tempo:.2f}s/{limit:.2f}s CER={best['cer']:.2f} "
          f"sim={best['sim']:.3f} „{best['heard']}”{flag}", flush=True)
    report[out.name] = dict(who=who, how=how, text=text, limit=round(limit, 2), tempo=round(tempo, 3),
                            chosen={k: v for k, v in best.items() if k != "fx"},
                            takes=[{k: v for k, v in t.items() if k != "fx"} for t in takes])
    if n % 10 == 0 or n == len(todo):
        rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
