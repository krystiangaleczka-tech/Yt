"""Głosy ludzi i postaci do efektów „Syna słońca” EN (wytyczne 1.14: głos człowieka z modelu mowy, nie z szumu) — BEZ głosu
reżysera. Wzór: „Bonnie and Clyde” glosy.py i Podręcznik, rozdział „Dźwięk” (19.11.2026): referencje to syntetyczne głosy
Kokoro-82M (Apache-2.0, pilot/models), Chatterbox Turbo czyta z nich znaczniki niewerbalne ([laugh], [groan], [gasp], [sigh],
[fear], [angry], [surprised], [happy]) i krótkie okrzyki z tabliczek (HELP!, NO WAY!, BROTHER!…).

Reżyser 20.11.2026: „dołóż głosy, efekty, gagi i inne rzeczy na film, patrząc na nowe zmiany od Bonnie i Clyde”.

uruchom (Mac: jeden ciężki proces naraz):
  pilot/.venv/bin/python -I output/powstanie-japonii/glosy.py referencje          → build/glosy_ref/<rola>.wav (Kokoro)
  LEKTOR_DEVICE=cpu pilot/.venv-tts/bin/python -I output/powstanie-japonii/glosy.py nagraj   → build/glosy_proby/*.raw.wav
  .venv-align/bin/python -I output/powstanie-japonii/glosy.py slowa              → build/glosy_proby/slowa.json (Whisper)
  pilot/.venv-tts/bin/python -I output/powstanie-japonii/glosy.py wybierz         → dzwiek_probki/<rodzaj>_1..N.wav
Whisper (faster-whisper) jest tylko w .venv-align, a soundfile tylko w .venv-tts — dlatego słowa liczy osobny krok „slowa”
(sam Whisper, czyta pliki przez av), a „wybierz” bierze je z slowa.json.
„wybierz” bierze podejścia automatycznie (długość, głośność, bez dziury w środku; z faster-whisper — także słowa okrzyków).
Kolejne użycia rodzaju w filmie biorą kolejne próbki (efekty.glos). Pliki .wav nie idą do repo.
"""
import os
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = next((d for d in (HERE.parents[1], HERE.parents[4]) if (d / "pilot/models").exists()), HERE.parents[1])  # modele w głównym katalogu
REF = HERE / "build" / "glosy_ref"
PROBY = HERE / "build" / "glosy_proby"
CEL = HERE / "dzwiek_probki"
SR = 44100

# Role (kto w filmie wydaje głos) → syntetyczny głos Kokoro.
GLOSY_KOKORO = {"iwarebiko": "am_michael", "itsuse": "am_adam", "brat2": "am_eric", "brat3": "am_liam", "nagasune": "am_onyx",
                "wojownik": "am_puck", "glowa": "am_fenrir", "niedzwiedz": "am_santa", "chlop": "am_echo", "zdrajca": "bm_daniel",
                "bog": "bm_george", "bog2": "bm_lewis", "bogini": "af_bella", "bogini2": "af_kore", "bogini3": "af_nova",
                "starka": "bf_emma", "starzec": "bm_fable", "izanami": "af_sarah"}
TEKST_REF = ("Listen to me. Long ago, beyond the sea, there was a land of green hills, and every morning the sun rose over it "
             "like a red paper lantern. Nobody said a word for a while, and then somebody laughed.")

# rodzaj → [(rola, tekst)]; każdy tekst w kilku ziarnach. Słowa (poza znacznikami) sprawdza Whisper, jeśli jest.
NAGRANIA = {
    "smiech": [(g, "[laugh] Ha ha ha! [laugh]") for g in ("bog", "bog2", "bogini", "bogini2", "bogini3")]
              + [(g, "[laugh] [laugh]") for g in ("bog", "bogini2")],
    "jek": [("itsuse", "[groan]"), ("izanami", "[gasp] [groan]"), ("nagasune", "[groan]")],
    "au": [("itsuse", "[groan] Ow!"), ("itsuse", "Ow! [groan]")],
    "aaa": [("itsuse", "[groan] Aaaah!"), ("itsuse", "[fear] Aaah! [groan]")],
    "nie_moge": [("itsuse", "[sigh] I can't..."), ("itsuse", "[groan] I can't...")],
    "pomocy": [("glowa", "[fear] Help!"), ("glowa", "[fear] Help! Help!")],
    "hmm": [("iwarebiko", "Hmm..."), ("iwarebiko", "[sigh] Hmm...")],
    "stop": [("wojownik", "[angry] Stop!"), ("wojownik", "[angry] Stop right there!")],
    "nie_ma_mowy": [("nagasune", "[angry] No way!"), ("nagasune", "[angry] No way! Never!")],
    "aaaa": [("brat2", "[fear] Aaaaah!"), ("brat2", "[gasp] Aaaah!")],
    "bracie": [("brat3", "[fear] Brother!"), ("brat3", "[fear] Brother! Help!")],
    "bu": [("niedzwiedz", "[happy] Boo!"), ("niedzwiedz", "Boo!")],
    "oh": [("chlop", "[surprised] Oh!"), ("chlop", "[surprised] Oh! What's this?")],
    "pulapka": [("zdrajca", "[fear] A trap!"), ("zdrajca", "[fear] It's a trap!")],
    "placz": [("starka", "[sigh] [sigh]"), ("starzec", "[sigh]")],
    "gasp": [(g, "[gasp]") for g in ("bog", "bogini", "wojownik")],
    "hura": [(g, "[happy] Hooray!") for g in ("wojownik", "brat2", "brat3", "iwarebiko")],
    # gagi 20.11.2026 (GAGI.md) — głos pod tabliczką
    "uff": [("bog", "[sigh] Phew..."), ("bog", "Phew! [sigh]")],
    "tada": [("bog2", "[happy] Ta-da!"), ("wojownik", "[happy] Ta-da!")],
    "wow": [("bogini", "[surprised] Wow!"), ("bogini2", "[happy] Wow!")],
    "au_s": [("bog", "[groan] Ow!"), ("bog", "Ow! [groan]")],
    "hik": [("glowa", "Hic!"), ("glowa", "[laugh] Hic!")],
    "ej": [("itsuse", "[surprised] Hey!"), ("itsuse", "[angry] Hey!")],
    "moje": [("nagasune", "[angry] Mine!"), ("wojownik", "[angry] Mine!"), ("zdrajca", "[angry] Mine!")],
    "taka_sama": [("nagasune", "[surprised] Same arrow?!"), ("nagasune", "[angry] The same arrow?!")],
    "starsze": [("zdrajca", "Make it older!"), ("zdrajca", "[whisper] Make it older!")],
    "zloto": [("chlop", "[surprised] Real gold?"), ("chlop", "Real gold?!")],
    "ups": [("wojownik", "[surprised] Oops!"), ("chlop", "Oops!")],
}
ZIARNA = {}  # Mac 8 GB i ok. 40 s na podejście: jedno ziarno na tekst (dwa teksty = dwa warianty okrzyku)
DOMYSLNE_ZIARNA = [7]
ILE = {"smiech": 7, "hura": 6, "gasp": 3}  # ile próbek zostawić (reszta: 3)


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
    return set(re.findall(r"[a-z']+", re.sub(r"\[[^\]]*\]", " ", txt.lower()))) - {"aaaah", "aaah", "aaaaah", "ha", "hmm", "ow"}


def slowa():
    """Transkrypcja wszystkich podejść (sam faster-whisper) do slowa.json — „wybierz” sprawdza z niej słowa okrzyków."""
    import json
    from faster_whisper import WhisperModel
    asr = WhisperModel("small", device="cpu", compute_type="int8")
    out = {}
    for p in sorted(PROBY.glob("*.raw.wav")):
        seg, _ = asr.transcribe(str(p), language="en", beam_size=3)
        out[p.name] = " ".join(x.text for x in seg).strip()
        print(f"{p.name:28s} {out[p.name]}", flush=True)
    (PROBY / "slowa.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def wybierz():
    """Automatyczny wybór: okrzyki — Whisper musi usłyszeć słowa tekstu (jeśli jest); niewerbalne — długość w rozsądnych
    granicach, bez długiej ciszy w środku. Z kilku dobrych bierze najkrótsze (najbardziej zwarte)."""
    import json

    import soundfile as sf
    zapis = PROBY / "slowa.json"
    slyszane = json.loads(zapis.read_text(encoding="utf-8")) if zapis.exists() else None
    if slyszane is None:  # bez kroku „slowa”: bez sprawdzania słów (ocenia reżyser w próbce)
        print("UWAGA: brak slowa.json (krok „slowa”) — okrzyki wybrane bez sprawdzenia słów", flush=True)
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
                if not (0.25 < dl < 3.2) or dziura >= 40:
                    continue
                potrzebne = _slowa(txt)
                if potrzebne and slyszane is not None:
                    slyszy = set(re.findall(r"[a-z']+", slyszane.get(p.name, "").lower()))
                    if len(potrzebne & slyszy) < max(1, len(potrzebne) // 2):
                        continue
                dobre.append((n, dl, z, y))
        for f in CEL.glob(f"{rodzaj}_*.wav"):
            f.unlink()
        ile = ILE.get(rodzaj, 3)
        if rodzaj in ILE:  # kilka głosów: po jednym podejściu z każdego tekstu
            wyb = list({n: (n, dl, z, y) for n, dl, z, y in sorted(dobre, key=lambda d: d[1])}.values())[:ile]
        else:
            wyb = sorted(dobre, key=lambda d: d[1])[:ile]
        for j, (n, dl, z, y) in enumerate(wyb, 1):
            sf.write(CEL / f"{rodzaj}_{j}.wav", y, SR, subtype="PCM_16")
        print(f"{rodzaj:12s} dobrych {len(dobre):2d}, wzięte {len(wyb)}: " + ", ".join(f"t{n}s{z} {dl:.2f}s" for n, dl, z, _ in wyb), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:] or ["wybierz"]
    {"referencje": referencje, "nagraj": nagraj, "slowa": slowa, "wybierz": wybierz}[a[0]]()
