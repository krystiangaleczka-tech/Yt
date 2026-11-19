"""Głosy ludzi do efektów „Bonnie and Clyde” (wytyczne 1.14: głos człowieka z modelu mowy, nie z szumu) — BEZ głosu reżysera.

Reżyser 19.11.2026: „tak, zrób bez narracji mojej” → referencje to syntetyczne głosy Kokoro-82M (Apache-2.0, pilot/models),
nie próbka lektora. Chatterbox Turbo czyta z nich znaczniki niewerbalne ([laugh], [gasp], [groan], [sigh], [shush], [fear]…)
i krótkie okrzyki; gwar tłumu to wiele krótkich zdań różnymi głosami, ułożonych gęsto i stłumionych (efekty.gwar).

uruchom (Mac: jeden ciężki proces naraz):
  pilot/.venv/bin/python -I output/bonnie-i-clyde/glosy.py referencje          → build/glosy_ref/<głos>.wav (Kokoro)
  LEKTOR_DEVICE=cpu pilot/.venv-tts/bin/python -I output/bonnie-i-clyde/glosy.py nagraj   → build/glosy_proby/*.raw.wav
  pilot/.venv-tts/bin/python -I output/bonnie-i-clyde/glosy.py wybierz         → dzwiek_probki/<rodzaj>_1..N.wav
„wybierz” bierze podejścia automatycznie: okrzyki sprawdza Whisperem (czy padły właściwe słowa), dźwięki niewerbalne po
długości i głośności. Reżyser ocenia całość w próbce (fragment filmu + sam dźwięk), zanim głosy pójdą do Studio.
"""
import os
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = next((d for d in (HERE.parents[1], HERE.parents[4]) if (d / "pilot/models").exists()), HERE.parents[1])  # modele są w głównym checkoucie
REF = HERE / "build" / "glosy_ref"
PROBY = HERE / "build" / "glosy_proby"
CEL = HERE / "dzwiek_probki"
SR = 44100

# Głosy Kokoro (syntetyczne) w rolach: kto w filmie wydaje dźwięk.
GLOSY_KOKORO = {"bonnie": "af_bella", "kobieta": "af_sarah", "kobieta2": "af_nicole", "clyde": "am_michael", "mezczyzna": "am_adam",
                "mezczyzna2": "am_eric", "starszy": "bm_george", "gazeciarz": "am_puck", "gruby": "am_onyx", "kobieta3": "af_heart"}
TEKST_REF = ("Well, I'll tell you what happened that night. We drove down the old county road, and nobody said a word for an hour. "
             "Then the lights came up behind us, and somebody laughed.")

# rodzaj → [(głos, tekst)], każdy tekst w kilku ziarnach. Słowa (poza znacznikami) sprawdza Whisper.
NAGRANIA = {
    "smiech_b": [("bonnie", "[laugh] Ha ha ha! [laugh]"), ("bonnie", "[laugh] [laugh]")],
    "krzyk_b": [("bonnie", "[fear] Aaaah! [groan]"), ("bonnie", "[gasp] Aaah! [groan]")],
    "ugh_b": [("bonnie", "[sigh] Ugh."), ("bonnie", "Ugh! [groan]")],
    "westchnienie_b": [("bonnie", "[sigh]"), ("bonnie", "[sigh] [sigh]")],
    "brr_b": [("bonnie", "Brrr! [gasp]"), ("bonnie", "[gasp] Brrr!")],
    "au_b": [("bonnie", "[groan] Ow!"), ("bonnie", "Ow! [groan]")],
    "hej_b": [("bonnie", "[surprised] Hey!"), ("bonnie", "[angry] Hey!")],
    "shh": [("kobieta", "[shush] Shhh!"), ("kobieta", "[angry] Shhh!")],
    "hej_m": [("mezczyzna", "[angry] Hey! Hey!"), ("mezczyzna", "[surprised] Hey!")],
    "stop": [("starszy", "[angry] Stop!"), ("starszy", "[angry] Stop right there!")],
    "go": [("clyde", "[angry] Go! Go!"), ("clyde", "[angry] Come on, go!")],
    "ojnie": [("clyde", "[surprised] Oh no."), ("clyde", "[sigh] Oh no.")],
    "au_c": [("clyde", "[groan] Aaagh!"), ("clyde", "[groan] Ow!")],
    "ouch": [("clyde", "[groan] Ouch!"), ("clyde", "[gasp] Ouch!")],
    "bye": [("clyde", "[happy] Bye!"), ("clyde", "[happy] Bye now!")],
    "thats_it": [("clyde", "[sarcastic] That's it?"), ("clyde", "[surprised] That's it?")],
    "gasp_m": [("mezczyzna2", "[gasp]"), ("mezczyzna2", "[gasp] [gasp]")],
    "back_off": [("starszy", "[angry] Back off! Get back!"), ("starszy", "[angry] Back off!")],
    "extra": [("gazeciarz", "[happy] Extra! Extra!"), ("gazeciarz", "Extra! Extra! Read all about it!")],
    "smiech_m": [(g, "[laugh] [laugh]") for g in ("clyde", "mezczyzna", "mezczyzna2", "starszy", "gruby")]
                + [(g, "[laugh] Ha ha! [laugh]") for g in ("kobieta", "kobieta2", "kobieta3")],
    "wiwat": [(g, "[happy] Bravo! Bravo!") for g in ("mezczyzna", "starszy", "kobieta", "kobieta2", "gruby")]
             + [(g, "[happy] Hooray!") for g in ("clyde", "mezczyzna2", "kobieta3")],
    "gwar": [(g, t) for g, t in (("mezczyzna", "Did you see the paper this morning?"), ("kobieta", "It's them, it's really them!"),
                                  ("starszy", "Unbelievable. Just unbelievable."), ("kobieta2", "Look at that! Look at that car!"),
                                  ("mezczyzna2", "Bonnie and Clyde, can you believe it?"), ("gruby", "Move along, folks, move along."),
                                  ("kobieta3", "Oh my goodness, look at the holes."), ("clyde", "I heard they got away again."),
                                  ("mezczyzna", "Step right up, step right up!"), ("kobieta", "Who's next? Who's next?"),
                                  ("starszy", "Over here! Over here!"), ("kobieta2", "Did you hear? Did you hear?"))],
}
ZIARNA = {"gwar": [7], "smiech_m": [7], "wiwat": [7]}
DOMYSLNE_ZIARNA = [7, 42, 123]
ILE = {"gwar": 12, "smiech_m": 8, "wiwat": 8}  # ile próbek zostawić (reszta: 3)


def referencje():
    import soundfile as sf
    from kokoro_onnx import Kokoro
    REF.mkdir(parents=True, exist_ok=True)
    k = Kokoro(str(REPO / "pilot/models/kokoro-v1.0.onnx"), str(REPO / "pilot/models/voices-v1.0.bin"))
    for rola, glos in GLOSY_KOKORO.items():
        out = REF / f"{rola}.wav"
        if out.exists():
            continue
        x, sr = k.create(TEKST_REF, voice=glos, speed=1.0, lang="en-gb" if glos.startswith("b") else "en-us")
        sf.write(out, x, sr)
        print(f"{rola} ({glos}): {len(x) / sr:.1f} s", flush=True)


def _turbo(device):
    import glob
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    sciezka = os.environ.get("TURBO") or sorted(glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/models--ResembleAI--chatterbox-turbo/snapshots/*")))[-1]
    return ChatterboxTurboTTS.from_local(sciezka, device)


def nagraj():
    import random

    import soundfile as sf
    import torch
    device = os.environ.get("LEKTOR_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
    orig = torch.load
    torch.load = lambda *a, **kw: orig(*a, **{**kw, "map_location": torch.device(device)})
    PROBY.mkdir(parents=True, exist_ok=True)
    m = _turbo(device)
    for rodzaj, lista in NAGRANIA.items():
        for n, (glos, txt) in enumerate(lista):
            for z in ZIARNA.get(rodzaj, DOMYSLNE_ZIARNA):
                out = PROBY / f"{rodzaj}_t{n}_s{z}.raw.wav"
                if out.exists():
                    continue
                torch.manual_seed(z), random.seed(z), np.random.seed(z)
                wav = m.generate(txt, audio_prompt_path=str(REF / f"{glos}.wav"), temperature=0.8).detach().cpu().numpy().squeeze()
                sf.write(out, wav.astype(np.float32), m.sr)
                print(f"{out.name}: {len(wav) / m.sr:.2f} s", flush=True)


def _wczytaj(p):
    import soundfile as sf
    from scipy.signal import resample_poly
    x, sr = sf.read(str(p), dtype="float64")
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = resample_poly(x, SR // g, sr // g)
    return x


def _obwiednia(x, krok=0.01):
    h = int(SR * krok)
    return np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9) for i in range(0, max(1, len(x) - h), h)])


def wytnij(x):
    """Od pierwszego do ostatniego dźwięku powyżej −40 dB względem szczytu, z zapasem i łagodnymi brzegami."""
    e = _obwiednia(x)
    glosne = np.where(e > e.max() - 40)[0]
    if not len(glosne):
        return x
    a = max(0, int((glosne[0] * 0.01 - 0.05) * SR))
    b = min(len(x), int((glosne[-1] * 0.01 + 0.12) * SR))
    y = x[a:b].copy()
    f1, f2 = int(0.01 * SR), min(len(y) // 3, int(0.08 * SR))
    y[:f1] *= np.linspace(0, 1, f1)
    y[-f2:] *= np.linspace(1, 0, f2)
    return y / (np.abs(y).max() + 1e-9) * 0.9


def _slowa(txt):
    return set(re.findall(r"[a-z']+", re.sub(r"\[[^\]]*\]", " ", txt.lower()))) - {"aaaah", "aaah", "aaagh", "brrr", "shhh", "ha", "ugh"}


def wybierz():
    """Automatyczny wybór: okrzyki — Whisper musi usłyszeć słowa tekstu; niewerbalne — długość w rozsądnych granicach,
    bez długiej ciszy w środku. Z kilku dobrych bierze najkrótsze (najbardziej zwarte)."""
    import soundfile as sf
    try:
        from faster_whisper import WhisperModel
        asr = WhisperModel("small", device="cpu", compute_type="int8")
    except ImportError:  # brak faster-whisper w środowisku: bez sprawdzania słów (ocenia reżyser w próbce)
        asr = None
        print("UWAGA: bez faster-whisper — okrzyki wybrane bez sprawdzenia słów", flush=True)
    CEL.mkdir(exist_ok=True)
    for rodzaj, lista in NAGRANIA.items():
        dobre = []
        for n, (glos, txt) in enumerate(lista):
            for z in ZIARNA.get(rodzaj, DOMYSLNE_ZIARNA):
                p = PROBY / f"{rodzaj}_t{n}_s{z}.raw.wav"
                if not p.exists():
                    continue
                y = wytnij(_wczytaj(p))
                dl = len(y) / SR
                e = _obwiednia(y)
                dziura = np.max(np.convolve((e < e.max() - 35).astype(float), np.ones(40), "valid")) if len(e) > 40 else 0
                if not (0.25 < dl < (6.0 if rodzaj == "gwar" else 3.2)) or dziura >= 40:
                    continue
                potrzebne = _slowa(txt)
                if potrzebne and asr is not None:
                    seg, _ = asr.transcribe(str(p), language="en", beam_size=3)
                    slyszy = set(re.findall(r"[a-z']+", " ".join(s.text for s in seg).lower()))
                    if len(potrzebne & slyszy) < max(1, len(potrzebne) // 2):
                        continue
                dobre.append((n, dl, z, y))
        for f in CEL.glob(f"{rodzaj}_*.wav"):
            f.unlink()
        ile = ILE.get(rodzaj, 3)
        if rodzaj in ILE:  # tłum: po jednym podejściu z każdego tekstu (różne głosy)
            wyb = list({n: (n, dl, z, y) for n, dl, z, y in sorted(dobre, key=lambda d: d[1])}.values())[:ile]
        else:
            wyb = sorted(dobre, key=lambda d: d[1])[:ile]
        for j, (n, dl, z, y) in enumerate(wyb, 1):
            sf.write(CEL / f"{rodzaj}_{j}.wav", y, SR, subtype="PCM_16")
        print(f"{rodzaj:16s} dobrych {len(dobre):2d}, wzięte {len(wyb)}: " + ", ".join(f"t{n}s{z} {dl:.2f}s" for n, dl, z, _ in wyb), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:] or ["wybierz"]
    {"referencje": referencje, "nagraj": nagraj, "wybierz": wybierz}[a[0]]()
