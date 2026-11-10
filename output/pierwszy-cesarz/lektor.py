"""Lektor filmu „Pierwszy cesarz”: kwestie z rozpiski czytane klonem głosu autora (Chatterbox Multilingual, ten sam
silnik i ta sama próbka co „Dodaj lektora” w Studio: pilot/assets/ref_clean.wav). Jeden proces, model ładowany raz.

uruchom:  pilot/.venv-tts/bin/python -I output/pierwszy-cesarz/lektor.py [klucz …]
          (na PC z paczki: nagraj_lektora.bat — ten sam skrypt na karcie NVIDIA)
wynik:    output/pierwszy-cesarz/lektor/<klucz>.wav (44,1 kHz mono, cisza przycięta) + lektor/<klucz>.json (tekst)
Gotowe pliki z tym samym tekstem są pomijane, więc przerwane nagrywanie wznawia się od miejsca przerwania.
Nazwy i liczby czyta się z WYMOWA (tekst mówiony), napis zostaje w zapisie z rozpiski.
"""
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "docs/filmy/pierwszy-cesarz/ujecia"))
from dane import SLOWNIE, kwestia, ujecia  # noqa: E402

OUT = HERE / "lektor"
REF = REPO / "pilot/assets/ref_clean.wav"
WYMOWA = [("Lü Buwei", "Lu Bułej"), ("Jing Ke", "Dżing Ke"), ("Zhao Gao", "Dżao Gao"), ("Xu Fu", "Sju Fu"), ("Li Si", "Li Sy"),
          ("Huhai", "Hu-haj"), ("Zheng", "Dżeng"), ("Zhao", "Dżao"), ("Qin", "Czin"), ("Chu", "Czu"), ("Wei", "Łej"),
          ("Yan", "Jen"), ("Qi", "Czi"), ("przed naszą erą", "przed naszą erą")]


def mowiony(txt):
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    for k, v in WYMOWA:
        txt = re.sub(rf"\b{re.escape(k)}\b", v, txt)
    return txt


def main(only):
    import numpy as np
    import soundfile as sf
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    # karta NVIDIA (PC) — kilka sekund na kwestię; bez niej procesor (Mac z 8 GB: ok. 4 min na kwestię)
    device = os.environ.get("LEKTOR_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
    if device == "cpu":
        torch.set_num_threads(min(4, os.cpu_count() or 2))
    print(f"urządzenie: {device}", flush=True)
    orig = torch.load
    torch.load = lambda *a, **kw: orig(*a, **{**kw, "map_location": torch.device(device)})
    OUT.mkdir(exist_ok=True)
    jobs = [(u[2], kwestia(u[7])) for u in ujecia() if kwestia(u[7]) and (not only or u[2] in only)]
    model = None
    for n, (klucz, txt) in enumerate(jobs, 1):
        meta = OUT / f"{klucz}.json"
        spoken = mowiony(txt)
        if meta.exists() and json.loads(meta.read_text(encoding="utf-8"))["spoken"] == spoken and (OUT / f"{klucz}.wav").exists():
            continue
        if model is None:
            model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        torch.manual_seed(42), random.seed(42), np.random.seed(42)
        audio = model.generate(spoken, language_id="pl", audio_prompt_path=str(REF), exaggeration=0.45, cfg_weight=0.45,
                               temperature=0.7).detach().cpu().numpy().squeeze().astype(np.float32)
        raw = OUT / f"{klucz}.raw.wav"
        sf.write(raw, audio, model.sr)
        # cisza na brzegach precz, ta sama głośność wszystkich kwestii, 44,1 kHz
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,"
                        "acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80:makeup=1.5,loudnorm=I=-16:TP=-2",
                        "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(OUT / f"{klucz}.wav")], check=True)
        raw.unlink()
        dur = sf.info(str(OUT / f"{klucz}.wav")).duration
        meta.write_text(json.dumps({"text": txt, "spoken": spoken, "duration": round(dur, 3)}, ensure_ascii=False), encoding="utf-8")
        print(f"{n}/{len(jobs)} {klucz}: {dur:.2f} s", flush=True)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
