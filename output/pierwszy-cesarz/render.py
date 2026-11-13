"""Pierwszy cesarz — teatr papierowy rysowany kodem (1280 × 720, 24 kl./s).

Rozpiska: docs/filmy/pierwszy-cesarz/ujecia/dane.py (akt → scena → beat → ujęcie, z kluczem ujęcia).
Ujęcia: ujecia1.py (akty 1–4) i ujecia2.py (akty 5–8), funkcja `s_<klucz>(st, w, t, T)` na ujęcie.
Świat (stan sceny, lalki, scenografie): swiat.py. Silnik (plany głębi, kamera, cienie, światło): papier.py.

  python3 render.py arkusz [1,2,3] [plik]   — arkusz klatek ujęć (numery od 1) do obejrzenia
  python3 render.py klatka 12.5 [plik]      — jedna klatka filmu (czas w sekundach)
  python3 render.py kontrola [1,2,3]        — test „końca świata” (płótno w barwie pustki), równolegle
  python3 render.py klipy [1,2,3] <katalog> — klip mp4 na ujęcie
  SZKIC=1 …                                 — szkic 640 × 360, 12 kl./s (przegląd w Studio); bez tego pełna jakość
  NAPISY=0 …                                — bez napisów (czyste ujęcia pod lektora i napisy ze Studio)
Moduł ma SCENES, DUR, FPS i frame(t) — tak jak pozostałe filmy (scripts/kontrola_ujec.py, wgrywanie do Studio).
"""
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))

import papier  # noqa: E402
import swiat  # noqa: E402
import ujecia1  # noqa: E402
import ujecia2  # noqa: E402
import zestaw as Z  # noqa: E402
from dane import kwestia, okno_kwestii, ujecia  # noqa: E402
from papier import FPS, H, W, Stage  # noqa: E402

NAPISY = os.environ.get("NAPISY", "1") != "0"
SZKIC = os.environ.get("SZKIC", "0") == "1"  # szkic do przeglądu w Studio: 640 × 360, 12 kl./s
if SZKIC:
    papier.Q, FPS = 0.5, 12
elif os.environ.get("ROZDZIELCZOSC"):  # wysokość klatki, np. ROZDZIELCZOSC=1440 → 2560 × 1440 (ta sama geometria, Q = 2)
    papier.Q = int(os.environ["ROZDZIELCZOSC"]) / H
CRF = os.environ.get("CRF", "23" if papier.Q <= 1 else "18")  # większa klatka: mniej kompresji, żeby papier nie poszedł w kostkę

UJ = ujecia()
KOL = swiat.KOL
FNS = [getattr(ujecia1, "s_" + k, None) or getattr(ujecia2, "s_" + k, None) for k in KOL]  # None = ujęcie do narysowania
ODN = [f"d{a:02d}_{k:02d}" for a, k, *_ in UJ]
# ujęcia, w których dekoracja staje od nowa (pierwsze ujęcie sceny albo zmiana miejsca): elementy wjeżdżają po kolei
BUDUJ = {"handan", "regent", "machina", "wymarsz", "dary", "ksiaze", "czarne", "drogi", "mur", "armia", "podroz", "spisek", "huhai",
         "powstanie", "studnia", "trucizna"}

# (start, koniec, ruch, napis, start kwestii, długość kwestii) — jak w pozostałych filmach
SCENES, _t = [], 0.0
for _akt, _k, _klucz, _kadr, _ruch, _sec, _opis, _snd in UJ:
    SCENES.append((_t, _t + _sec, _ruch, kwestia(_snd), *okno_kwestii(_snd)))
    _t += _sec
DUR = _t


def wrap(txt, n=60):
    out, line = [], ""
    for word in txt.split():
        if len(line) + len(word) + 1 > n and line:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    return out + [line]


def subtitle(img, txt):
    """Napis jako pasek papieru u dołu kadru — tylko wtedy, gdy lektor mówi."""
    q = papier.Q
    w, h = img.size
    f = ImageFont.truetype(Z.FONT_PL, round(28 * q), index=Z.PL_IDX)
    lines = wrap(txt)
    d = ImageDraw.Draw(img, "RGBA")
    lh = 36 * q
    wd = max(d.textlength(ln, font=f) for ln in lines) + 40 * q
    y1 = h - 20 * q
    y0 = y1 - lh * len(lines) - 14 * q
    d.rounded_rectangle([w / 2 - wd / 2 + 3 * q, y0 + 4 * q, w / 2 + wd / 2 + 3 * q, y1 + 4 * q], 4 * q, fill=(20, 12, 8, 90))
    d.rounded_rectangle([w / 2 - wd / 2, y0, w / 2 + wd / 2, y1], 4 * q, fill=(238, 224, 192, 238))
    for n, ln in enumerate(lines):
        d.text((w / 2, y0 + 8 * q + lh * n + lh / 2 - 2 * q), ln, font=f, fill=(44, 28, 22, 255), anchor="mm")


def frame(t, void=None):
    i = next((k for k, s in enumerate(SCENES) if s[0] <= t < s[1]), len(SCENES) - 1)
    a, b, ruch, txt, vs, vl = SCENES[i]
    lt, T = t - a, b - a
    st = Stage(t, seed=i)
    st.void = void
    if FNS[i] is None:  # ujęcie jeszcze nie narysowane: pusta scena z kartką
        st.put(Z.sky(), W / 2, H / 2, 0.14, w=1760, anchor=(0.5, 0.5), shadow=None)
        st.put(Z.tag(f"{ODN[i]} · do narysowania"), W / 2, H / 2, 0.8, h=60, anchor=(0.5, 0.5))
    else:
        w = swiat.stan(i)
        if KOL[i] in BUDUJ:
            w.build = lt
        st.T = T
        FNS[i](st, w, lt, T)
    if void:  # kontrola „końca świata”: surowe płótno, nienarysowane miejsca zostają w barwie pustki
        return st.render(post=False)
    st.dim *= min(1.0, t / 0.5, max(0.0, (DUR - 0.1 - t) / 1.0))  # film wchodzi z czerni i w nią wychodzi
    img = st.render()
    if NAPISY and txt and vs <= lt < min(T - 0.05, vs + vl + 0.35):
        subtitle(img, txt)
    return img


def arkusz(only=None, out=None, cols=4, tw=320):
    """Arkusz klatek: kilka chwil każdego ujęcia (początek, środek, koniec)."""
    rows = [i for i in range(len(SCENES)) if not only or i + 1 in only]
    th = tw * 9 // 16
    sheet = Image.new("RGB", (tw * cols, th * len(rows)))
    for r, i in enumerate(rows):
        a, b = SCENES[i][:2]
        for c in range(cols):
            f = 0.03 + 0.94 * c / (cols - 1)
            t = a + (b - a) * f
            im = frame(t).resize((tw, th), Image.LANCZOS)
            ImageDraw.Draw(im).text((5, 3), f"{i + 1} {ODN[i]} {KOL[i]} · {t - a:.1f} s", fill=(255, 255, 0))
            sheet.paste(im, (c * tw, r * th))
    out = out or HERE / "arkusz.png"
    sheet.save(out)
    return out


def _pustka(i):
    """Ile pikseli pustki (nienarysowanego płótna) ma najgorsza klatka ujęcia i; sprawdzana co 4. klatka."""
    from papier import VOID
    a, b = SCENES[i][:2]
    worst, when = 0, a
    for f in range(0, int((b - a) * FPS), 4):
        arr = np.asarray(frame(a + f / FPS, void=VOID)).astype(np.int16)
        n = int(((arr[..., 0] > 250) & (arr[..., 1] < 6) & (arr[..., 2] > 250)).sum())
        if n > worst:
            worst, when = n, a + f / FPS
    return i, worst, when


def _klip(arg):
    """Renderuje jedno ujęcie do pliku mp4 (klatki zaokrąglone w górę, żeby klip pokrył ujęcie na osi)."""
    import subprocess
    i, out = arg
    a, b = SCENES[i][:2]
    n = math.ceil((b - a) * FPS - 1e-9)
    ow, oh = int(round(W * papier.Q)), int(round(H * papier.Q))
    part = out.with_name(out.stem + ".part.mp4")  # plik niedokończony nie wygląda na gotowy po przerwaniu
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", CRF, "-preset", "slow", "-threads", os.environ.get("X264_WATKI", "4"), "-pix_fmt", "yuv420p", str(part)],
                            stdin=subprocess.PIPE)
    for f in range(n):
        proc.stdin.write(frame(min(a + f / FPS, b - 1e-3)).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit(f"ffmpeg: {out}")
    os.replace(part, out)
    return i, n


def rozgrzej(ktore=None):
    """Buduje wycinki w procesie głównym, zanim powstaną procesy robocze — po rozwidleniu dzielą one tę samą pamięć.
    Bez tego każdy proces ładował własny komplet wycinków i komputer z 8 GB RAM wchodził w pamięć wymiany (10.11.2026)."""
    for i, (a, b, *_) in enumerate(SCENES):
        if FNS[i] is None or (ktore and i not in ktore):
            continue
        for f in (0.5, 0.93):
            FNS[i](Stage(a, seed=i), swiat.stan(i), (b - a) * f, b - a)  # samo ułożenie sceny tworzy wycinki
    for v in range(6):
        Z.soldier(v)
    for n in range(10):
        Z.flame(n)


PROCESY = int(os.environ.get("PROCESY", "1"))  # 8 GB RAM i inne otwarte programy: kilka procesów naraz tylko się dławi


def rownolegle(fn, args, procs=None):
    """Jeden proces po kolei (domyślnie) albo kilka z rozwidlenia (PROCESY=3 na maszynie z wolną pamięcią)."""
    procs = procs or PROCESY
    if procs <= 1:
        for a in args:
            yield fn(a)
        return
    import multiprocessing as mp
    # macOS/Linux: rozwidlenie (wspólna pamięć wycinków); Windows nie ma fork — każdy proces wczytuje wycinki sam
    ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
    with ctx.Pool(procs, maxtasksperchild=6) as pool:
        yield from pool.imap_unordered(fn, args)


def klipy(out, only=None, procs=None):
    """Klipy ujęć (numery od 1) do katalogu out; zwraca {indeks: (plik, klatki)}."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    idx = [i for i in range(len(SCENES)) if FNS[i] is not None and (not only or i + 1 in only)]
    if (procs or PROCESY) > 1 and sys.platform != "win32":
        rozgrzej(set(idx))
    idx = [i for i in idx if not (out / f"{ODN[i]}.mp4").exists() or os.environ.get("NADPISZ") == "1"]  # wznowienie: gotowe zostają
    done = {}
    for i, n in rownolegle(_klip, [(i, out / f"{ODN[i]}.mp4") for i in idx], procs):
        done[i] = (out / f"{ODN[i]}.mp4", n)
        print(f"{ODN[i]} {KOL[i]}: {n} klatek", flush=True)
    return done


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "arkusz"
    only = {int(x) for x in sys.argv[2].split(",")} if len(sys.argv) > 2 and sys.argv[2][0].isdigit() else None
    if cmd == "klatka":
        frame(float(sys.argv[2])).save(sys.argv[3] if len(sys.argv) > 3 else str(HERE / "klatka.png"))
    elif cmd == "kontrola":
        idx = [i for i in range(len(SCENES)) if FNS[i] is not None and (not only or i + 1 in only)]
        if PROCESY > 1:
            rozgrzej(set(idx))
        bad = 0
        for i, n, when in sorted(rownolegle(_pustka, idx)):
            bad += n > 0
            print(f"{ODN[i]} {KOL[i]}: {'OK' if n == 0 else f'PUSTKA {n} px w {when - SCENES[i][0]:.2f} s'}")
        sys.exit(1 if bad else 0)
    elif cmd == "klipy":
        klipy(sys.argv[-1], only)
    else:
        print(arkusz(only, sys.argv[3] if len(sys.argv) > 3 else None))
