"""Lektor filmu „Pierwszy cesarz”: kwestie z rozpiski czytane klonem głosu autora (Chatterbox Multilingual), sposobem
z Podręcznika pracowni → Lektor (docos/lektor_studio.py): próbka bez pogłosu, kilka podejść na kwestię, suche
i z odbudowanym pasmem, wybór podejścia z oddechami na przecinkach. Jeden proces, model ładowany raz.

uruchom:  pilot/.venv-tts/bin/python -I output/pierwszy-cesarz/lektor.py [klucz …]
          (na PC z paczki: nagraj_lektora.bat — ten sam skrypt na karcie NVIDIA)
próbka:   pilot/assets/ref_studio.wav (bez pogłosu: docos/lektor_studio.py probka); nie ma jej w repo
wynik:    lektor/podejscia/<klucz>_s<ziarno>.raw.wav — surowe podejścia, potem docos/lektor_studio.py (środowisko
          z resemble-enhance: LEKTOR_ENHANCE albo pilot/.venv-enhance / .venv-enhance) robi z nich suche nagrania
          i kładzie wybrane jako lektor/<klucz>.wav + lektor/<klucz>.json
Gotowe podejścia z tym samym tekstem i tą samą próbką są pomijane, więc przerwane nagrywanie wznawia się od miejsca
przerwania. Nazwy i liczby czyta się z WYMOWA (tekst mówiony), napis zostaje w zapisie z rozpiski.
"""
import hashlib
import json
import logging
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
POD = OUT / "podejscia"
REF = REPO / "pilot/assets/ref_studio.wav"
ZIARNA = [42, 7, 123]   # trzy podejścia na kwestię; różnią się rytmem (pauzy, melodia), nie barwą
WYMOWA = [("Lü Buwei", "Lu Bułej"), ("Jing Ke", "Dżing Ke"), ("Zhao Gao", "Dżao Gao"), ("Xu Fu", "Sju Fu"), ("Li Si", "Li Sy"),
          ("Huhai", "Hu-haj"), ("Zheng", "Dżeng"), ("Zhao", "Dżao"), ("Qin", "Czin"), ("Chu", "Czu"), ("Wei", "Łej"),
          ("Yan", "Jen"), ("Qi", "Czi"), ("przed naszą erą", "przed naszą erą")]


def mowiony(txt):
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    for k, v in WYMOWA:
        txt = re.sub(rf"\b{re.escape(k)}\b", v, txt)
    return txt


class Powtorzenia(logging.Handler):
    """Chatterbox ostrzega, gdy ucina kwestię, bo się powtarza — takie podejście odpada przy wyborze."""
    def __init__(self):
        super().__init__(logging.WARNING)
        self.bylo = False

    def emit(self, record):
        msg = record.getMessage()
        if "token_repetition=True" in msg or "alignment_repetition=tensor(True" in msg or "repetition of token" in msg:
            self.bylo = True


def enhance_python():
    for p in (os.environ.get("LEKTOR_ENHANCE"), REPO / "pilot/.venv-enhance/bin/python",
              REPO / ".venv-enhance/Scripts/python.exe"):
        if p and Path(p).exists():
            return str(p)
    return None


def main(only):
    if not REF.exists():
        sys.exit(f"Brak próbki bez pogłosu: {REF}\nZrób ją: <python z resemble-enhance> -I docos/lektor_studio.py probka "
                 f"<nagranie głosu> pilot/assets/ref_studio.wav (albo skopiuj gotową, nie ma jej w repo).")
    enh = enhance_python()
    if not enh:
        sys.exit("Brak środowiska z resemble-enhance (pilot/.venv-enhance albo .venv-enhance, albo LEKTOR_ENHANCE).")
    import numpy as np
    import soundfile as sf
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    # karta NVIDIA (PC) — kilka sekund na podejście; Mac: MPS ok. 1–2 min na podejście, procesor kilka razy wolniej
    device = os.environ.get("LEKTOR_DEVICE") or ("cuda" if torch.cuda.is_available() else
                                                 "mps" if torch.backends.mps.is_available() else "cpu")
    if device == "cpu":
        torch.set_num_threads(min(4, os.cpu_count() or 2))
    print(f"urządzenie: {device}", flush=True)
    orig = torch.load
    torch.load = lambda *a, **kw: orig(*a, **{**kw, "map_location": torch.device(device)})
    POD.mkdir(parents=True, exist_ok=True)
    probka = hashlib.sha256(REF.read_bytes()).hexdigest()[:16]
    straz = Powtorzenia()
    logging.getLogger("chatterbox").addHandler(straz)
    jobs = [(u[2], kwestia(u[7])) for u in ujecia() if kwestia(u[7]) and (not only or u[2] in only)]
    model = None
    for n, (klucz, txt) in enumerate(jobs, 1):
        meta_path = POD / f"{klucz}.json"
        spoken = mowiony(txt)
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        if meta.get("spoken") != spoken or meta.get("probka") != probka:
            meta = {"text": txt, "spoken": spoken, "probka": probka, "podejscia": {}}
        for z in ZIARNA:
            raw = POD / f"{klucz}_s{z}.raw.wav"
            if str(z) in meta["podejscia"] and raw.exists():
                continue
            if model is None:
                model = ChatterboxMultilingualTTS.from_pretrained(device=device)
            torch.manual_seed(z), random.seed(z), np.random.seed(z)
            straz.bylo = False
            audio = model.generate(spoken, language_id="pl", audio_prompt_path=str(REF), exaggeration=0.45,
                                   cfg_weight=0.45, temperature=0.7).detach().cpu().numpy().squeeze().astype(np.float32)
            sf.write(raw, audio, model.sr)
            meta["podejscia"][str(z)] = {"powtorzenie": straz.bylo}
            meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            print(f"{n}/{len(jobs)} {klucz} podejście {z}: {len(audio) / model.sr:.2f} s"
                  + (" (powtórzenie)" if straz.bylo else ""), flush=True)
    del model
    if device == "mps":
        torch.mps.empty_cache()
    # obróbka i wybór w osobnym środowisku (resemble-enhance ma inne wersje bibliotek niż Chatterbox)
    subprocess.run([enh, "-I", str(REPO / "docos/lektor_studio.py"), "podejscia", str(OUT)], check=True)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
