"""Lektor ANGIELSKIEJ wersji filmu „Pierwszy cesarz” (JEZYK=en; polski lektor: lektor.py): kwestie z rozpiski czytane klonem głosu autora (Chatterbox Multilingual, ten sam
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
from dane import JEZYK, LEKTOR, SLOWNIE, kwestia, ujecia  # noqa: E402

OUT = Path(os.environ.get("LEKTOR_OUT") or LEKTOR)  # lektor/ albo lektor_en/ (JEZYK=en); LEKTOR_OUT — np. katalog testu A/B
REF = Path(os.environ.get("PROBKA") or REPO / "pilot/assets/ref_clean.wav")  # próbka głosu autora
PROMPT = Path(os.environ.get("PROMPT") or REF)  # VoxCPM2: fragment próbki do kontynuacji (krótszy = szybciej)
REF_TXT = PROMPT.with_suffix(".txt")  # dokładna transkrypcja promptu
SILNIK = os.environ.get("SILNIK", "chatterbox")  # chatterbox (Chatterbox Multilingual) albo voxcpm (VoxCPM2)
WYMOWA = [("Lü Buwei", "Lu Bułej"), ("Jing Ke", "Dżing Ke"), ("Zhao Gao", "Dżao Gao"), ("Xu Fu", "Sju Fu"), ("Li Si", "Li Sy"),
          ("Huhai", "Hu-haj"), ("Zheng", "Dżeng"), ("Zhao", "Dżao"), ("Qin", "Czin"), ("Chu", "Czu"), ("Wei", "Łej"),
          ("Yan", "Jen"), ("Qi", "Czi"), ("przed naszą erą", "przed naszą erą")]


STUDIO = os.environ.get("STUDIO", "1") != "0"  # sposób z Podręcznika → Lektor (studio()); STUDIO=0: dawne jedno podejście
ZIARNA = [42, 7, 123]  # trzy podejścia na kwestię w sposobie studyjnym; różnią się rytmem (pauzy, melodia), nie barwą
PROBY = int(os.environ.get("PROBY", "4"))  # STUDIO=0: ile podejść na kwestię, zanim zostanie najlepsze
SPRAWDZ = os.environ.get("SPRAWDZ", "1") != "0"  # Whisper sprawdza każde podejście
PROG = float(os.environ.get("PROG", "0.92"))  # zgodność tekstu z tym, co usłyszał Whisper, przy której podejście jest dobre


def _litery(txt):
    txt = re.sub(r"\[[^\]]*\]", "", txt)  # znaczniki emocji ([sigh], [dramatic] …) nie są wypowiadane
    if JEZYK == "en":
        # Whisper pisze liczby cyframi („120,000”), tekst mówiony słowami („a hundred and twenty thousand”) — bez
        # sprowadzenia obu do jednej postaci dobre podejścia odpadały (13.11.2026: rody, kopiec, koniec, upadek, chu)
        from transformers.models.whisper.english_normalizer import EnglishTextNormalizer
        txt = EnglishTextNormalizer({})(txt)
    return re.sub(r"[^a-ząćęłńóśźżü0-9]", "", txt.lower())


# AKTORSKIE=<plik.json>: {klucz: tekst mówiony ze znacznikami} — wersje kwestii z emocjami/westchnieniami dla silnika turbo
AKTORSKIE = json.loads(Path(os.environ["AKTORSKIE"]).read_text(encoding="utf-8")) if os.environ.get("AKTORSKIE") else {}


def zgodnosc(spoken, heard):
    """Podobieństwo tekstu kwestii do transkrypcji (same litery, 0..1): łapie połknięte słowa, powtórki i bełkot na końcu."""
    import difflib
    return difflib.SequenceMatcher(None, _litery(spoken), _litery(heard)).ratio()


def whisper(device):
    """Whisper large-v3 do sprawdzania nagrań: funkcja (audio, sr) → tekst."""
    import torch
    import torchaudio
    from transformers import pipeline
    pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device=device,
                    dtype=torch.float16 if device == "cuda" else torch.float32)

    def asr(audio, sr):
        x = torchaudio.functional.resample(torch.from_numpy(audio), sr, 16000).numpy()
        return pipe({"raw": x, "sampling_rate": 16000}, generate_kwargs={"language": "english" if JEZYK == "en" else "polish", "task": "transcribe"})["text"].strip()
    return asr


def mowiony(txt):
    if JEZYK == "en":
        from kwestie_en import SLOWNIE_EN, WYMOWA_EN
        for k, v in SLOWNIE_EN.items():
            txt = txt.replace(k, v)
        for k, v in WYMOWA_EN:
            txt = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", v, txt)
        return txt
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    for k, v in WYMOWA:
        txt = re.sub(rf"\b{re.escape(k)}\b", v, txt)
    return txt


def _safetensors_bez_mmap():
    """safetensors.load_file mapuje plik w pamięci; na Windows mapowanie rezerwuje pamięć (commit) na cały plik, więc przy
    zajętym RAM (np. równoległy render) kończy się „access violation”. Zamiennik czyta tensory zwykłym odczytem z pliku.
    Wywołać przed importem silnika (moduły robią `from safetensors.torch import load_file`)."""
    import json as _json
    import struct

    import safetensors.torch as st
    import torch
    if getattr(st.load_file, "_bez_mmap", False):
        return
    TYP = {"BF16": torch.bfloat16, "F16": torch.float16, "F32": torch.float32, "F64": torch.float64, "I64": torch.int64,
           "I32": torch.int32, "I16": torch.int16, "I8": torch.int8, "U8": torch.uint8, "BOOL": torch.bool}

    def load_file(filename, device="cpu"):
        out = {}
        with open(filename, "rb") as fh:
            n = struct.unpack("<Q", fh.read(8))[0]
            hdr = _json.loads(fh.read(n))
            hdr.pop("__metadata__", None)
            for k, v in hdr.items():
                a, b = v["data_offsets"]
                fh.seek(8 + n + a)
                buf = bytearray(fh.read(b - a))
                t = torch.frombuffer(buf, dtype=TYP[v["dtype"]]).reshape(v["shape"]) if buf else torch.empty(v["shape"], dtype=TYP[v["dtype"]])
                out[k] = t if str(device) == "cpu" else t.to(device)
        return out
    load_file._bez_mmap = True
    st.load_file = load_file


def _dots_wczytuj_po_kawalku():
    """dots.tts wczytuje model.safetensors (4,4 GB) w całości do RAM obok modelu w fp32 (~9 GB); na PC z zajętą pamięcią
    kończy się to „access violation” (mapowanie pliku na Windows rezerwuje pamięć na cały plik, także w safe_open).
    Tu wagi czyta się zwykłym odczytem, tensor po tensorze, więc szczyt to sam model + jeden tensor."""
    import json as _json
    import struct

    import torch
    from dots_tts.models.dots_tts.model import DotsTtsModel
    TYP = {"BF16": torch.bfloat16, "F16": torch.float16, "F32": torch.float32, "I64": torch.int64, "I32": torch.int32,
           "BOOL": torch.bool, "U8": torch.uint8}

    @classmethod
    def load(cls, module, path):
        cel = module.state_dict(keep_vars=True)
        with open(path, "rb") as fh, torch.no_grad():
            n = struct.unpack("<Q", fh.read(8))[0]
            hdr = _json.loads(fh.read(n))
            hdr.pop("__metadata__", None)

            def tensor(k):
                v = hdr[k]
                a, b = v["data_offsets"]
                fh.seek(8 + n + a)
                buf = bytearray(fh.read(b - a))
                return torch.frombuffer(buf, dtype=TYP[v["dtype"]]).reshape(v["shape"]) if buf else torch.empty(v["shape"], dtype=TYP[v["dtype"]])
            zostalo = set(cel)
            for k in hdr:
                if k not in cel:
                    raise RuntimeError(f"{path}: nieoczekiwany klucz {k}")
                cel[k].data.copy_(tensor(k))
                zostalo.discard(k)
            for nadmiarowy, kanoniczny in cls._ARTIFACT_ALIASES:
                if nadmiarowy in zostalo and kanoniczny in hdr:
                    cel[nadmiarowy].data.copy_(tensor(kanoniczny))
                    zostalo.discard(nadmiarowy)
        if zostalo:
            raise RuntimeError(f"{path}: brak kluczy {sorted(zostalo)[:5]}")
        return module
    DotsTtsModel._load_artifact_module = load

    # rdzeń (LLM + DiT, 2 mld parametrów) powstaje od razu na karcie w bf16 — i tak tam trafia (runtime: core.to(bf16)),
    # a składany w fp32 na procesorze zajmował 16+ GB RAM
    import dots_tts.models.dots_tts.model as dm
    if not getattr(dm.DotsTtsCore, "_na_karcie", False):
        rdzen = dm.DotsTtsCore

        def na_karcie(*a, **kw):
            stary = torch.get_default_dtype()
            torch.set_default_dtype(torch.bfloat16)
            try:
                with torch.device("cuda"):
                    return rdzen(*a, **kw)
            finally:
                torch.set_default_dtype(stary)
        na_karcie._na_karcie = True
        dm.DotsTtsCore = na_karcie


class silnik:
    """Klon głosu: generate(tekst, ziarno) → numpy float32 mono, sr — częstotliwość próbkowania."""

    def __init__(self, device):
        if SILNIK == "voxcpm":
            from voxcpm import VoxCPM
            self.m = VoxCPM.from_pretrained(os.environ.get("VOXCPM", "F:/claude/modele/VoxCPM2"), load_denoiser=False)
            self.sr = self.m.tts_model.sample_rate
        elif SILNIK == "dots":  # dots.tts-soar (RedNote, 2026), F:\claude\.venv-nowe
            from dots_tts.runtime import DotsTtsRuntime
            _dots_wczytuj_po_kawalku()
            self.m = DotsTtsRuntime.from_pretrained(os.environ.get("DOTS", "F:/claude/modele/dots.tts-soar"), precision="bfloat16")
            self.sr = self.m.sample_rate
        elif SILNIK == "qwen3":  # Qwen3-TTS 1.7B Base (2026), F:\claude\.venv-nowe
            import torch
            from qwen_tts import Qwen3TTSModel
            self.m = Qwen3TTSModel.from_pretrained(os.environ.get("QWEN3", "F:/claude/modele/Qwen3-TTS-1.7B-Base"),
                                                   device_map=f"{device}:0" if device == "cuda" else device,
                                                   dtype=torch.bfloat16, attn_implementation="sdpa")
            self.prompt = self.m.create_voice_clone_prompt(ref_audio=str(PROMPT), ref_text=REF_TXT.read_text(encoding="utf-8").strip(),
                                                           x_vector_only_mode=False)
            self.sr = 24000  # nadpisywane tym, co zwróci model
        elif SILNIK == "turbo":  # Chatterbox Turbo (MIT): znaczniki [sigh] [gasp] [chuckle] [whispering] [dramatic] …
            _safetensors_bez_mmap()
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            self.m = ChatterboxTurboTTS.from_local(os.environ.get("TURBO", "F:/claude/modele/chatterbox-turbo"), device)
            self.sr = self.m.sr
        else:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            self.m = ChatterboxMultilingualTTS.from_pretrained(device=device)
            self.sr = self.m.sr

    def generate(self, txt, seed):
        import numpy as np
        if SILNIK == "voxcpm":
            kw = dict(prompt_wav_path=str(PROMPT), prompt_text=REF_TXT.read_text(encoding="utf-8").strip()) if REF_TXT.exists() else {}
            wav = self.m.generate(text=txt, reference_wav_path=str(REF), cfg_value=float(os.environ.get("CFG", "2.0")),
                                  inference_timesteps=int(os.environ.get("KROKI", "10")), **kw)  # ziarno: torch.manual_seed w main
            return np.asarray(wav, np.float32).squeeze()
        if SILNIK == "dots":
            r = self.m.generate(text=txt, prompt_audio_path=str(PROMPT), prompt_text=REF_TXT.read_text(encoding="utf-8").strip(),
                                language="EN" if JEZYK == "en" else None,
                                num_steps=int(os.environ.get("KROKI", "16")), guidance_scale=float(os.environ.get("CFG", "1.2")))
            self.sr = r.get("sample_rate", self.sr)
            return r["audio"].float().cpu().numpy().squeeze().astype(np.float32)
        if SILNIK == "qwen3":
            wavs, self.sr = self.m.generate_voice_clone(text=txt, language="English" if JEZYK == "en" else "Polish",
                                                        voice_clone_prompt=self.prompt)
            return np.asarray(wavs[0], np.float32).squeeze()
        if SILNIK == "turbo":
            return self.m.generate(txt, audio_prompt_path=str(PROMPT), temperature=float(os.environ.get("TEMPERATURA", "0.8"))
                                   ).detach().cpu().numpy().squeeze().astype(np.float32)
        return self.m.generate(txt, language_id=JEZYK, audio_prompt_path=str(REF), exaggeration=0.45, cfg_weight=0.45,
                               temperature=0.7).detach().cpu().numpy().squeeze().astype(np.float32)


def enhance_python():
    for p in (os.environ.get("LEKTOR_ENHANCE"), REPO / "pilot/.venv-enhance/bin/python",
              REPO / ".venv-enhance/Scripts/python.exe"):
        if p and Path(p).exists():
            return str(p)
    return None


def studio(jobs, device):
    """Podręcznik pracowni → Lektor (docos/lektor_studio.py): próbka bez pogłosu (PROMPT, np. pilot/assets/ref_en_studio.wav),
    3 podejścia na kwestię (ZIARNA), każde suche i z odbudowanym pasmem, wybór podejścia z oddechem na każdym przecinku;
    reżyser może wskazać inne w lektor_en/podejscia/wybor.json. Podejście, w którym Whisper nie usłyszał tekstu
    (połknięte słowo, powtórka, bełkot: zgodność < PROG), odpada przy wyborze tak jak powtórzenie modelu.
    Gotowe podejścia z tym samym tekstem, silnikiem i próbką są pomijane — przerwane nagrywanie wznawia się."""
    import hashlib

    import numpy as np
    import soundfile as sf
    import torch
    enh = enhance_python()
    if not enh:
        sys.exit("Brak środowiska z resemble-enhance (pilot/.venv-enhance albo .venv-enhance, albo LEKTOR_ENHANCE).")
    pod = OUT / "podejscia"
    pod.mkdir(parents=True, exist_ok=True)
    probka = hashlib.sha256(PROMPT.read_bytes()).hexdigest()[:16]
    model = asr = None
    for n, (klucz, txt) in enumerate(jobs, 1):
        spoken = AKTORSKIE.get(klucz) or mowiony(txt)
        meta_path = pod / f"{klucz}.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        if (meta.get("spoken"), meta.get("probka"), meta.get("silnik")) != (spoken, probka, SILNIK):
            meta = {"text": txt, "spoken": spoken, "probka": probka, "silnik": SILNIK, "podejscia": {}}
        for z in ZIARNA:
            raw = pod / f"{klucz}_s{z}.raw.wav"
            if str(z) in meta["podejscia"] and raw.exists():
                info = meta["podejscia"][str(z)]
                if "whisper" in info:  # ocena liczona od nowa z zapisanej transkrypcji (poprawki porównania bez nagrywania)
                    score = max(zgodnosc(spoken, info["whisper"]), zgodnosc(txt, info["whisper"]))
                    info.update(powtorzenie=score < PROG, zgodnosc=round(score, 3))
                    meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
                continue
            if model is None:
                if SPRAWDZ:
                    asr = whisper(device)  # Whisper przed silnikiem: duże modele zostawiają mało wolnej pamięci RAM
                model = silnik(device)
            torch.manual_seed(z), random.seed(z), np.random.seed(z)
            audio = model.generate(spoken, z)
            sf.write(raw, audio, model.sr)
            info = {"powtorzenie": False}
            if asr:
                heard = asr(audio, model.sr)
                score = max(zgodnosc(spoken, heard), zgodnosc(txt, heard))  # Whisper pisze imiona i liczby po swojemu
                info = {"powtorzenie": score < PROG, "zgodnosc": round(score, 3), "whisper": heard}
            meta["podejscia"][str(z)] = info
            meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            print(f"{n}/{len(jobs)} {klucz} podejście {z}: {len(audio) / model.sr:.2f} s"
                  + (f", zgodność {info['zgodnosc']:.2f}" if asr else "") + ("  (odpada)" if info["powtorzenie"] else ""),
                  flush=True)
    del model, asr
    if device == "cuda":
        torch.cuda.empty_cache()
    # obróbka i wybór w osobnym środowisku (resemble-enhance ma inne wersje bibliotek niż Chatterbox)
    subprocess.run([enh, "-I", str(REPO / "docos/lektor_studio.py"), "podejscia", str(OUT)], check=True,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def main(only):
    import numpy as np
    import soundfile as sf
    import torch

    # karta NVIDIA (PC) — kilka sekund na kwestię; bez niej procesor (Mac z 8 GB: ok. 4 min na kwestię)
    device = os.environ.get("LEKTOR_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
    if device == "cpu":
        torch.set_num_threads(min(4, os.cpu_count() or 2))
    print(f"urządzenie: {device}", flush=True)
    orig = torch.load
    torch.load = lambda *a, **kw: orig(*a, **{**kw, "map_location": torch.device(device)})
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(u[2], kwestia(u[7])) for u in ujecia() if kwestia(u[7]) and (not only or u[2] in only)]
    if STUDIO:
        return studio(jobs, device)
    model = asr = None
    for n, (klucz, txt) in enumerate(jobs, 1):
        meta = OUT / f"{klucz}.json"
        spoken = AKTORSKIE.get(klucz) or mowiony(txt)
        if meta.exists() and (OUT / f"{klucz}.wav").exists():
            m = json.loads(meta.read_text(encoding="utf-8"))
            if m["spoken"] == spoken and m.get("silnik", SILNIK) == SILNIK:  # gotowe tym samym silnikiem i tekstem
                continue
        if model is None:
            if SPRAWDZ:
                asr = whisper(device)  # Whisper przed silnikiem: duże modele (dots, qwen3) zostawiają mało wolnej pamięci RAM
            model = silnik(device)
            import gc
            gc.collect()
        # kilka podejść (inne ziarno), każde sprawdza Whisper; zostaje to najbliższe tekstowi
        best = None
        for proba in range(PROBY if SPRAWDZ else 1):
            seed = int(os.environ.get("ZIARNO", "42")) + proba  # ZIARNO: inne ziarno przy ponownym nagraniu wybranych kwestii
            torch.manual_seed(seed), random.seed(seed), np.random.seed(seed)
            audio = model.generate(spoken, seed)
            if not SPRAWDZ:  # SPRAWDZ=0: bez Whispera (mało pamięci), jedno podejście; zgodność później osobnym przebiegiem
                best = (1.0, audio, "", seed)
                break
            heard = asr(audio, model.sr)
            score = max(zgodnosc(spoken, heard), zgodnosc(txt, heard))  # Whisper pisze imiona i liczby po swojemu
            if best is None or score > best[0]:
                best = (score, audio, heard, seed)
            if score >= PROG:
                break
            print(f"   {klucz}: podejście {proba + 1} zgodność {score:.2f} — „{heard}”", flush=True)
        score, audio, heard, seed = best
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
        meta.write_text(json.dumps({"text": txt, "spoken": spoken, "duration": round(dur, 3), "silnik": SILNIK, "seed": seed, "zgodnosc": round(score, 3), "whisper": heard}, ensure_ascii=False), encoding="utf-8")
        print(f"{n}/{len(jobs)} {klucz}: {dur:.2f} s, zgodność {score:.2f}{'' if score >= PROG else '  <-- DO ODSŁUCHU'}", flush=True)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
