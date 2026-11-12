"""Lektor „jak z wyciszonego studia” — sposób wspólny dla wszystkich filmów (Podręcznik pracowni → Lektor).

Chatterbox kopiuje akustykę próbki: pogłos pokoju w próbce = pogłos w lektorze. Filtry na gotowym nagraniu tego nie
naprawiają (12.11.2026: odszumianie pogłosu i EQ na gotowej kwestii brzmiały gorzej, z dziwnymi dźwiękami). Dlatego:

1. probka     — resemble-enhance zdejmuje z próbki szum i pogłos (pełne pasmo, cisza między słowami)
                → pilot/assets/ref_studio.wav; z niej nagrywa się każdą kwestię
2. podejscia  — każda kwestia w kilku podejściach (ziarna losowania, nagrywa je lektor.py filmu); każde podejście
                suche (bramka, kompresja, EQ) i z pasmem powyżej ~8 kHz odbudowanym przez resemble-enhance
3. wybór      — podejście z oddechem na każdym przecinku i kropce w środku kwestii, a z równych to spokojniejsze
                (dłuższe pauzy); bez podejść, w których model się powtórzył. Reżyser może wskazać inne ziarno
                w <lektor>/podejscia/wybor.json, np. {"handan": 7}

Układ katalogu lektora filmu:
  <lektor>/podejscia/<klucz>.json            tekst, próbka (sha) i podejścia z flagą powtórzenia — pisze lektor.py
  <lektor>/podejscia/<klucz>_s<ziarno>.raw.wav   surowe z Chatterboxa (24 kHz)
  <lektor>/podejscia/<klucz>_s<ziarno>.wav       po obróbce (44,1 kHz)
  <lektor>/<klucz>.wav + <klucz>.json        wybrane podejście — to czytają render, montaż i Studio

uruchom w środowisku z resemble-enhance (Mac: pilot/.venv-enhance, PC: .venv-enhance — zakłada je nagraj_lektora.bat):
  python -I docos/lektor_studio.py probka <nagranie.m4a> pilot/assets/ref_studio.wav [sekundy, domyślnie 16]
  python -I docos/lektor_studio.py podejscia <katalog lektora filmu>
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

# sucho: cisza na brzegach precz, bramka na szum między słowami, kompresja, mniej buczenia, więcej czytelności
FX = ("silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
      "highpass=f=70,agate=threshold=0.02:ratio=3:release=120,"
      "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
      "equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=4200:t=q:w=1.2:g=2,"
      "loudnorm=I=-16:TP=-2")
# po odbudowie pasma: lekka kompresja, „powietrze” w górze, ta sama głośność, cisza bez szumu rekonstrukcji
POST = ("acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80:makeup=1.5,"
        "equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=1.5,"
        "highshelf=f=9000:g=2,loudnorm=I=-16:TP=-2,"
        "agate=threshold=0.012:ratio=4:attack=3:release=150")
PAUZA_DB, PAUZA_MIN = -40.0, 0.15   # pauza = co najmniej 0,15 s ciszy poniżej -40 dBFS w środku kwestii


def _ffmpeg(src, dst, af=None, sr=44100):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src)] + (["-af", af] if af else [])
    subprocess.run(cmd + ["-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)


def _enhance(src, dst, lambd):
    """resemble-enhance w kawałkach po 8 s (całość naraz nie mieści się w 8 GB RAM); lambd = siła odszumiania."""
    import torch
    import torchaudio
    from huggingface_hub import snapshot_download
    from resemble_enhance.enhancer.inference import enhance

    run_dir = Path(snapshot_download("ResembleAI/resemble-enhance", allow_patterns=["enhancer_stage2/*"])) / "enhancer_stage2"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    wav, sr = torchaudio.load(str(src))
    mono, parts = wav.mean(0), []
    for i in range(0, len(mono), 8 * sr):
        out, out_sr = enhance(mono[i:i + 8 * sr], sr, device, nfe=32, solver="midpoint", lambd=lambd, tau=0.5,
                              run_dir=run_dir)
        parts.append(out.cpu())
    torchaudio.save(str(dst), torch.cat(parts).unsqueeze(0), out_sr)


def probka(src, dst, sekundy=16.0):
    tmp = Path(tempfile.mkdtemp()) / "in.wav"
    _ffmpeg(src, tmp, f"highpass=f=70,silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:"
                      f"stop_duration=0.4:stop_threshold=-45dB,atrim=0:{sekundy}")
    _enhance(tmp, dst, lambd=0.9)
    print(f"próbka bez pogłosu → {dst}")


def obrob(raw, dst):
    tmp = Path(tempfile.mkdtemp())
    _ffmpeg(raw, tmp / "fx.wav", FX)
    _enhance(tmp / "fx.wav", tmp / "e.wav", lambd=0.1)   # próbka już czysta: chodzi o pasmo, nie o odszumianie
    _ffmpeg(tmp / "e.wav", dst, POST)


def pauzy(path):
    """Pauzy w środku kwestii (s), bez ciszy na brzegach."""
    y, sr = sf.read(str(path), dtype="float32")
    hop = int(sr * 0.01)
    db = np.array([10 * np.log10(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y) - hop, hop)])
    glos = np.where(db > PAUZA_DB)[0]
    if not len(glos):
        return []
    cisza = db[glos[0]:glos[-1] + 1] <= PAUZA_DB
    out, n = [], 0
    for c in np.append(cisza, False):
        if c:
            n += 1
        else:
            if n * 0.01 >= PAUZA_MIN:
                out.append(round(n * 0.01, 2))
            n = 0
    return out


def wybierz(spoken, takes):
    """takes: {ziarno: (ścieżka, powtórzenie)} → ziarno. Oddech na każdym znaku przestankowym w środku kwestii,
    z równych spokojniejsze; bez powtórzeń i bez podejść o długości odstającej o >25% od mediany (zacięcia)."""
    przerwy = len(re.findall(r"[,;:.!?—–](?=\s*\w)", spoken))
    dl = {z: sf.info(str(p)).duration for z, (p, _) in takes.items()}
    med = float(np.median(list(dl.values())))
    ok = [z for z, (_, powt) in takes.items() if not powt and abs(dl[z] - med) <= 0.25 * med] or list(takes)

    def ocena(z):
        p = pauzy(takes[z][0])
        return -abs(len(p) - przerwy), sum(p)
    return max(ok, key=ocena)


def podejscia(lektor):
    lektor = Path(lektor)
    pod = lektor / "podejscia"
    wybor = json.loads((pod / "wybor.json").read_text(encoding="utf-8")) if (pod / "wybor.json").exists() else {}
    for meta_path in sorted(pod.glob("*.json")):
        if meta_path.name == "wybor.json":
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        klucz = meta_path.stem
        takes = {}
        for z, info in meta["podejscia"].items():
            raw, gotowe = pod / f"{klucz}_s{z}.raw.wav", pod / f"{klucz}_s{z}.wav"
            if not raw.exists():
                continue
            if not gotowe.exists() or gotowe.stat().st_mtime < raw.stat().st_mtime:
                obrob(raw, gotowe)
                print(f"obróbka {gotowe.name}", flush=True)
            takes[z] = (gotowe, info.get("powtorzenie", False))
        if not takes:
            continue
        rez = str(wybor[klucz]) if str(wybor.get(klucz, "")) in takes else None
        z = rez or wybierz(meta["spoken"], takes)
        dst, dst_meta = lektor / f"{klucz}.wav", lektor / f"{klucz}.json"
        nowe = {"text": meta["text"], "spoken": meta["spoken"], "duration": round(sf.info(str(takes[z][0])).duration, 3),
                "podejscie": int(z), "wybral": "reżyser" if rez else "automat", "probka": meta["probka"]}
        if dst_meta.exists() and json.loads(dst_meta.read_text(encoding="utf-8")) == nowe and dst.exists():
            continue
        shutil.copy2(takes[z][0], dst)
        dst_meta.write_text(json.dumps(nowe, ensure_ascii=False), encoding="utf-8")
        print(f"{klucz}: podejście {z} ({nowe['wybral']}), {nowe['duration']:.2f} s", flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "probka":
        probka(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 16.0)
    elif len(sys.argv) == 3 and sys.argv[1] == "podejscia":
        podejscia(sys.argv[2])
    else:
        sys.exit(__doc__)
