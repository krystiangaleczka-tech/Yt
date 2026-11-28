"""Próbka dźwięku do akceptacji reżysera (Podręcznik → Dźwięk: nowy rodzaj dźwięku idzie najpierw jako próbka): fragmenty
filmu z obrazem i pełnym miksem — lektor, muzyka i efekty — oraz same tematy i same nowe efekty.

  python3 -I probka_dzwieku.py      → build/probka_dzwiek.mp4 (fragmenty z FRAGMENTY, 720p, 24 kl./s, plansza przed każdym)
                                       build/probka_muzyka.wav (tematy po kolei), build/probka_efekty.wav (nowe efekty)
Najpierw lektor (lektor_en/) i efekty.py (dzwiek_en/muzyka.wav, efekty.wav). Klatki liczą się w kilku procesach (PROCESY,
domyślnie 3); każdy pisze swój kawałek mp4, potem ffmpeg skleja kawałki i podkłada dźwięk. Wzór: „Bonnie and Clyde”.
"""
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "build"
# (pierwsze ujęcie, ostatnie ujęcie) — przegląd brzmień: zapowiedź i Diuna → góry i motyw Szamila; skok w ciszy i lezginka;
# pieczątka imperium i bałałajka; Dargo, koza, zasadzka w ciszy; rzeka i uścisk z motywem; Kaługa, Blanch, Herbert
FRAGMENTY = [("zap_skok", "przedstawienie"), ("skok", "imam"), ("raport", "syn_na_polnoc"), ("dargo", "zasadzka"),
             ("syn_wraca", "uscisk"), ("kaluga", "herbert")]
MIKS = {"lektor": 1.0, "muzyka": 0.8, "efekty": 1.0}  # jak głośności ścieżek w Studio


def czytaj(path):
    with wave.open(str(path)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        return (x.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else x), w.getframerate()


def zapisz(path, x, sr):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def lektor_filmu(sr, n):
    """Ścieżka lektora na cały film: każda kwestia od oddechu w swoim ujęciu (jak studio_film.py lektor)."""
    import render as R
    from dane import HAK, LEKTOR, kwestia, okno_kwestii, ujecia
    x = np.zeros(n)
    for i, u in enumerate(ujecia()):
        wav = LEKTOR / f"{u[2]}.wav"
        if not kwestia(u[7]) or not wav.exists() or json.loads(wav.with_suffix(".json").read_text()).get("text") != kwestia(u[7]):
            continue
        y, s = czytaj(wav)
        if s != sr:
            y = np.interp(np.arange(int(len(y) * sr / s)) * s / sr, np.arange(len(y)), y)
        j = int((R.SCENES[i][0] + okno_kwestii(u[7], u[2] in HAK)[0]) * sr)
        x[j:j + len(y)] += y[:max(0, n - j)]
    return x


def _kawalek(arg):
    import render as R
    a, b, path = arg[:3]
    fps = R.FPS
    n = int(round((b - a) * fps))
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}", "-r", str(fps),
                          "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)
    for f in range(n):
        p.stdin.write(np.asarray(R.frame(a + f / fps).convert("RGB")).tobytes())
    p.stdin.close()
    p.wait()
    return path


KARTA = 1.2  # s: plansza przed każdym fragmentem


def _karta(path, txt, fps):
    import render as R
    import zestaw_kz as Z
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (R.W, R.H), (12, 10, 10))
    d = ImageDraw.Draw(im)
    for i, (linia, rozm) in enumerate(txt):
        f = ImageFont.truetype(Z.FONT_PL, rozm, index=Z.PL_IDX)
        d.text((R.W / 2, R.H / 2 - 30 + 60 * i), linia, font=f, fill=(236, 220, 180), anchor="mm")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}", "-r", str(fps),
                          "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)
    for _ in range(int(round(KARTA * fps))):
        p.stdin.write(np.asarray(im).tobytes())
    p.stdin.close()
    p.wait()


def film(fragmenty=FRAGMENTY, nazwa="probka_dzwiek"):
    import multiprocessing as mp
    import render as R
    OUT.mkdir(exist_ok=True)
    idx = {k: i for i, k in enumerate(R.KOL)}
    zakresy = [(R.SCENES[idx[a]][0], R.SCENES[idx[b]][1]) for a, b in fragmenty]
    kaw = []
    for z, (a, b) in enumerate(zakresy):
        krok = (b - a) / max(1, round((b - a) / 6.0))
        t = a
        while t < b - 1e-6:
            kaw.append((t, min(b, t + krok), OUT / f"_kaw_{z:02d}_{len(kaw):03d}.mp4", z))
            t += krok
    with mp.get_context("fork").Pool(int(os.environ.get("PROCESY", "3"))) as pool:
        for i, _ in enumerate(pool.imap(_kawalek, kaw)):
            print(f"\r{i + 1}/{len(kaw)}", end="", flush=True)
    print()
    karty = []
    for z, (a, b) in enumerate(fragmenty):
        i = idx[a]
        t0 = R.SCENES[i][0]
        kp = OUT / f"_karta_{z:02d}.mp4"
        _karta(kp, [(f"Fragment {z + 1} / {len(fragmenty)}", 44),
                    (f"akt {R.GRANICE[i]['akt']} · ujęcie {i + 1} „{a}”" + (f" … „{b}”" if b != a else "") + f" · {int(t0 // 60)}:{t0 % 60:04.1f} w filmie", 30)],
               R.FPS)
        karty.append(kp)
    lista = OUT / "_lista.txt"
    lista.write_text("".join(f"file '{karty[z].name}'\n" + "".join(f"file '{k[2].name}'\n" for k in kaw if k[3] == z)
                             for z in range(len(zakresy))))
    obraz = OUT / "_obraz.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(obraz)], check=True)
    mus, sr = czytaj(HERE / "dzwiek_en/muzyka.wav")
    fx, _ = czytaj(HERE / "dzwiek_en/efekty.wav")
    lek = lektor_filmu(sr, len(mus))
    m = mus * MIKS["muzyka"] + fx * MIKS["efekty"] + lek * MIKS["lektor"]
    fps = R.FPS
    czesci = []
    for z, (a, b) in enumerate(zakresy):
        nkl = sum(int(round((k[1] - k[0]) * fps)) for k in kaw if k[3] == z)
        x = m[int(a * sr):int(a * sr) + int(nkl / fps * sr)].copy()
        r = int(0.15 * sr)
        x[:r] *= np.linspace(0, 1, r)
        x[-r:] *= np.linspace(1, 0, r)
        czesci += [np.zeros(int(round(KARTA * fps)) * sr // fps), x]
    dzw = OUT / "_dzwiek.wav"
    zapisz(dzw, np.concatenate(czesci) * 0.95, sr)
    wynik = OUT / f"{nazwa}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(obraz), "-i", str(dzw), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(wynik)], check=True)
    for p in [k[2] for k in kaw] + karty + [lista, obraz, dzw]:
        p.unlink()
    print(wynik)


def sam_dzwiek():
    import efekty as E
    sr = E.SR
    cisza = np.zeros(int(0.7 * sr))
    tematy = [("gory", {"motyw": True}), ("gory", {"zurna": True, "doli": True}), ("lezginka", {}), ("imperium", {"fanfara": True}),
              ("lament", {"motyw": "syn"}), ("rosja", {}), ("rosja", {"zywo": True}), ("pustynia", {"zurna": True}), ("walc", {})]
    czesci = []
    for c, (st, o) in enumerate(tematy):
        fn, g = E.STYLE[st]
        P = E.Pasmo(10.0)
        fn(P, 10.0, np.random.default_rng(200 + c), o)
        x = E._wyrownaj(P.x[:int(10.0 * sr)], E.MUZYKA_DB + g)
        x[-int(0.8 * sr):] *= np.linspace(1, 0, int(0.8 * sr))
        czesci += [x, cisza]
    zapisz(OUT / "probka_muzyka.wav", np.tanh(np.concatenate(czesci) * 2.4) * 0.9, sr)
    efekty = ["armata", "strzal", "strzal_cien", "koza", "kot", "gulp", "bek", "szabla_wyj", "szable", "krysztal", "kamien", "gory_rosna",
              "dum", "stempel", "kopyto", "brr", "pytanie", "wahwah_k", "slide_down"]
    czesci = []
    for k in efekty:
        czesci += [E.KROTKIE[k](), cisza]
    for k, d in (("piasek", 2.5), ("maszyna", 3.0), ("flaga", 3.0), ("kola", 3.0), ("lina", 3.0), ("dzwoneczki", 3.0)):
        czesci += [E.DLUGIE[k](d), cisza]
    zapisz(OUT / "probka_efekty.wav", np.tanh(np.concatenate(czesci) * 1.2) * 0.9, sr)
    print(OUT / "probka_muzyka.wav", OUT / "probka_efekty.wav")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    sam_dzwiek()
    if sys.argv[1:2] != ["bez_filmu"]:
        film()
