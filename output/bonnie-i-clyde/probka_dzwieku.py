"""Próbka dźwięku do akceptacji reżysera: fragmenty filmu z obrazem i pełnym miksem (muzyka + efekty) oraz sam dźwięk.

  python3 -I probka_dzwieku.py                     → build/probka_dzwiek.mp4 (fragmenty z FRAGMENTY, 720p, 24 kl./s)
                                                      build/probka_muzyka.wav (tematy po kolei), build/probka_efekty.wav (nowe efekty)
Najpierw efekty.py (dzwiek_en/muzyka.wav, efekty.wav). Klatki liczą się w kilku procesach (PROCESY, domyślnie 4); każdy pisze
swój kawałek mp4, potem ffmpeg skleja kawałki i podkłada dźwięk. Lektora nie ma (nagrywa go reżyser) — napisy są w obrazie.
"""
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "build"
# (pierwsze ujęcie, ostatnie ujęcie) — przegląd brzmień: otwarcie, ucieczka z żartem, łowca i pościg, zasadzka
FRAGMENTY = [("zap_wellington_most", "wprowadzenie2"), ("akt2", "kaufman"), ("hamer", "hak_teczka"), ("zasadzka_rano", "dym")]
# próbka głosów (glosy.py): gwar i „EXTRA!”, śmiech Bonnie, krzyk przy Wellington, pamiątkarze, śmiech widowni, wiwaty
FRAGMENTY_GLOSY = [("zap_wellington_most", "wagon"), ("kiosk", "darby_smiech"), ("wellington_most", "wellington_bonnie"), ("joplin_karty", "joplin_karty"), ("pamiatki", "pamiatki"),
                   ("film_hamer", "film_hamer"), ("dzieki", "dzieki")]
# próbka gagów (reżyser 19.11: „gagi robimy wszystkie”): całe ujęcia z gagami, z trzema nowymi dźwiękami (kaszel silnika,
# werbel do musztry, zapałka) — do akceptacji przed wgraniem
FRAGMENTY_GAGI = [(k, k) for k in ("zdjecie", "slub", "kawiarnia", "stacja", "darby_auto", "oboz", "dzien20", "listy_gon", "prasa_cygaro",
                                   "noc", "gra", "dzieki")]
MIKS = {"muzyka": 0.8, "efekty": 1.0}  # jak głośności ścieżek w Studio (studio_film.dzwiek)


def czytaj(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768, w.getframerate()


def zapisz(path, x, sr):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


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


KARTA = 1.2  # s: plansza przed każdym fragmentem próbki


def _karta(path, txt, fps):
    """Czarna plansza z opisem fragmentu (reżyser 19.11: zlepek fragmentów bez plansz wyglądał jak jeden film, w którym
    „dwie historie nachodzą na siebie”, a kurtyny dwóch różnych aktów stały obok siebie)."""
    import render as R
    import zestaw_bc as Z
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
    procs = int(os.environ.get("PROCESY", "4"))
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        for i, p in enumerate(pool.imap(_kawalek, kaw)):
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
    zrodlo = Path(os.environ.get("DZWIEK_Z", HERE / "dzwiek_en"))
    mus, sr = czytaj(zrodlo / "muzyka.wav")
    fx, _ = czytaj(zrodlo / "efekty.wav")
    m = mus * MIKS["muzyka"] + fx * MIKS["efekty"]
    fps = R.FPS
    czesci = []
    for z, (a, b) in enumerate(zakresy):
        nkl = sum(int(round((k[1] - k[0]) * fps)) for k in kaw if k[3] == z)
        x = m[int(a * sr):int(a * sr) + int(nkl / fps * sr)]
        r = int(0.15 * sr)
        x = x.copy()
        x[:r] *= np.linspace(0, 1, r)
        x[-r:] *= np.linspace(1, 0, r)
        czesci.append(np.zeros(int(round(KARTA * fps)) * sr // fps))  # cisza pod planszą
        czesci.append(x)
    dzw = OUT / "_dzwiek.wav"
    zapisz(dzw, np.concatenate(czesci) * 0.95, sr)
    wynik = OUT / f"{nazwa}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(obraz), "-i", str(dzw), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(wynik)], check=True)
    for k in kaw:
        k[2].unlink()
    for k in karty:
        k.unlink()
    for p in (lista, obraz, dzw):
        p.unlink()
    print(wynik)


def sam_dzwiek():
    import efekty as E
    sr = E.SR
    cisza = np.zeros(int(0.7 * sr))
    tematy = [("rag", {"fanfara": True}), ("folk", {}), ("blues", {}), ("lowca", {}), ("napiecie", {"bpm": (60, 90)}), ("mrok", {}),
              ("praca", {}), ("jarmark", {}), ("folk", {"bpm": 176, "szybko": True}), ("chip", {})]
    czesci = []
    for c, (st, o) in enumerate(tematy):
        fn, g = E.STYLE[st]
        P = E.Pasmo(9.0)
        fn(P, 9.0, np.random.default_rng(200 + c), o)
        x = P.x[:int(9.0 * sr)] * g
        x[-int(0.8 * sr):] *= np.linspace(1, 0, int(0.8 * sr))
        czesci += [x, cisza]
    zapisz(OUT / "probka_muzyka.wav", np.tanh(np.concatenate(czesci) * 1.2) * 0.9, sr)
    efekty = ["klakson", "beep2", "pisk", "krach", "strzal", "strzal_cien", "flesz", "wahwah", "smiech_p", "boing", "osiol", "indyk",
              "gwizdek", "kasa", "stempel", "tab", "podpis", "zawieszka", "sting", "sting_l", "brama_hit", "kajdanki", "zamek", "dzwon"]
    czesci = []
    for k in efekty:
        czesci += [E.KROTKIE[k](), cisza]
    for k, d in (("prasa", 3.0), ("oklaski", 3.0), ("komary", 2.5), ("gwizdanie", 4.0), ("dzwony", 4.0)):
        czesci += [E.DLUGIE[k](d), cisza]
    zapisz(OUT / "probka_efekty.wav", np.tanh(np.concatenate(czesci) * 1.2) * 0.9, sr)
    print(OUT / "probka_muzyka.wav", OUT / "probka_efekty.wav")


def same_glosy():
    import efekty as E
    sr = E.SR
    cisza = np.zeros(int(0.6 * sr))
    czesci = []
    for rodzaj in ("smiech_b", "krzyk_b", "ugh_b", "westchnienie_b", "brr_b", "au_b", "hej_b", "shh", "hej_m", "stop", "go", "ojnie", "au_c",
                   "ouch", "bye", "thats_it", "gasp_m", "back_off", "extra"):
        czesci += [E.glos(rodzaj, 0.8), cisza]
    czesci += [E.smiech_tlum() * 1.3, cisza, E.gwar(6.0) * 2.5, cisza, E.wiwat_tlum(5.0) * 2.0]
    zapisz(OUT / "probka_glosy.wav", np.tanh(np.concatenate(czesci) * 1.2) * 0.9, sr)
    print(OUT / "probka_glosy.wav")


def same_nowe():
    """Same nowe dźwięki gagów, po kolei z ciszą: kaszel silnika ×2, werbel ×3, zapałka ×2."""
    import efekty as E
    sr = E.SR
    cisza = np.zeros(int(0.7 * sr))
    czesci = []
    for rodzaj, ile in (("kaszel_silnika", 2), ("werbel_fx", 3), ("zapalka", 2)):
        for _ in range(ile):
            czesci += [E.KROTKIE[rodzaj](), cisza]
        czesci.append(cisza)
    zapisz(OUT / "probka_nowe_dzwieki.wav", np.concatenate(czesci) * 0.9, sr)
    print(OUT / "probka_nowe_dzwieki.wav")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    if sys.argv[1:2] == ["gagi"]:
        same_nowe()
        film(FRAGMENTY_GAGI, "probka_gagi")
    elif sys.argv[1:2] == ["glosy"]:
        same_glosy()
        film(FRAGMENTY_GLOSY, "probka_glosy")
    else:
        sam_dzwiek()
        film()
