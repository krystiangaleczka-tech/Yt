"""Pierwszy cesarz — teatr papierowy rysowany kodem (1280 × 720, 24 kl./s).

Rozpiska: docs/filmy/pierwszy-cesarz/ujecia/dane.py (akt → scena → beat → ujęcie, z kluczem ujęcia).
Ujęcia: ujecia1.py (akty 1–4) i ujecia2.py (akty 5–8), funkcja `s_<klucz>(st, w, t, T)` na ujęcie.
Świat (stan sceny, lalki, scenografie): swiat.py. Silnik (plany głębi, kamera, cienie, światło): papier.py.

  python3 render.py arkusz [1,2,3] [plik]   — arkusz klatek ujęć (numery od 1) do obejrzenia
  python3 render.py klatka 12.5 [plik]      — jedna klatka filmu (czas w sekundach)
  python3 render.py kontrola [1,2,3]        — test „końca świata” (płótno w barwie pustki), równolegle
  python3 render.py klipy [1,2,3] <katalog> — klip mp4 na ujęcie; renderuje tylko ujęcia, których odcisk (kod ujęcia,
                                              stan świata, długość, napis, jakość…) zmienił się od ostatniego renderu
  python3 render.py przyjmij <katalog>      — klipy sprzed odcisków: przyjmij jako aktualne (gdy liczba klatek się zgadza)
  PRESET=slow …                             — kodowanie x264 do renderu końcowego (domyślnie veryfast: przegląd w Studio)
  WARSTWY=1 …                               — warstwy stałe (na próbę: to, co w ujęciu stoi, rysowane raz)
  NADPISZ=1 …                               — wszystkie wybrane ujęcia od nowa
  SZKIC=1 …                                 — szkic 640 × 360, 12 kl./s (przegląd w Studio); bez tego pełna jakość
  NAPISY=0 …                                — bez napisów (czyste ujęcia pod lektora i napisy ze Studio)
Moduł ma SCENES, DUR, FPS i frame(t) — tak jak pozostałe filmy (scripts/kontrola_ujec.py, wgrywanie do Studio).
"""
import hashlib
import inspect
import json
import math
import os
import sys
import zlib
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
# x264: do oglądania w Studio wystarczy veryfast (obraz prawie ten sam, kodowanie kilka razy szybsze);
# render końcowy (pc/renderuj*.bat) ustawia PRESET=slow
PRESET = os.environ.get("PRESET", "veryfast")
# warstwy stałe (papier.Warstwy) — przyspieszenie w trakcie sprawdzania: domyślnie wyłączone, dopóki porównanie
# z pełnym renderem nie wykaże, że obraz jest ten sam; WARSTWY=1 włącza je na próbę
WARSTWY = os.environ.get("WARSTWY", "0") == "1"

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


def ziarno(i):
    """Ziarno ujęcia z jego klucza, nie z miejsca w filmie: wstawienie albo wydłużenie innego ujęcia go nie zmienia."""
    return zlib.crc32(KOL[i].encode()) % 1000003


def uloz(t, void=None):
    """Klatka w chwili t filmu, ułożona (wycinki, kamera, światło), jeszcze nie narysowana: (Stage, napis albo None).
    Wszystko zależy tylko od czasu w ujęciu — klip ujęcia jest ten sam bez względu na to, gdzie ujęcie stoi w filmie
    (poza wejściem z czerni w pierwszym i wyjściem w czerń w ostatnim)."""
    i = next((k for k, s in enumerate(SCENES) if s[0] <= t < s[1]), len(SCENES) - 1)
    a, b, ruch, txt, vs, vl = SCENES[i]
    lt, T = t - a, b - a
    st = Stage(lt, seed=ziarno(i))
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
    if not void:
        st.dim *= min(1.0, t / 0.5, max(0.0, (DUR - 0.1 - t) / 1.0))  # film wchodzi z czerni i w nią wychodzi
    return st, (txt if NAPISY and txt and vs <= lt < min(T - 0.05, vs + vl + 0.35) else None)


def frame(t, void=None):
    st, napis = uloz(t, void)
    if void:  # kontrola „końca świata”: surowe płótno, nienarysowane miejsca zostają w barwie pustki
        return st.render(post=False)
    img = st.render()
    if napis:
        subtitle(img, napis)
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
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", CRF, "-preset", PRESET, "-threads", os.environ.get("X264_WATKI", "4"), "-pix_fmt", "yuv420p", str(part)],
                            stdin=subprocess.PIPE)
    klatki = [uloz(min(a + f / FPS, b - 1e-3)) for f in range(n)]  # najpierw całe ujęcie ułożone: plan warstw stałych
    plan = papier.Warstwy([st for st, _ in klatki]) if WARSTWY else None
    for f, (st, napis) in enumerate(klatki):
        img = plan.render(f) if plan else st.render()
        if napis:
            subtitle(img, napis)
        proc.stdin.write(img.tobytes())
        klatki[f] = None  # ułożona klatka już niepotrzebna
    proc.stdin.close()
    if proc.wait():
        raise SystemExit(f"ffmpeg: {out}")
    os.replace(part, out)
    zapisz_odcisk(out, i, n)
    return i, n


# ---- odcisk klipu: renderuje się tylko to, co się zmieniło ----
# Wersja wyglądu silnika (papier.py i rysowanie w render.py). Zmień ją, gdy zmienia się to, JAK klatka wygląda
# (światło, cienie, ziarno…) — wtedy wszystkie klipy liczą się od nowa. Przyspieszenia, które obrazu nie zmieniają
# (np. warstwy stałe), jej nie ruszają.
SILNIK = "2026-11-14 warstwy, ziarno z ujęcia"
MODULY_UJEC = {"ujecia1", "ujecia2"}
PROSTE = (int, float, str, bool, tuple, list, dict, set, frozenset, type(None))


def _zrodlo(fn, out):
    """Kod funkcji ujęcia razem z funkcjami i stałymi modułów ujęć, których używa (rekurencyjnie)."""
    if ("fn", fn.__module__, fn.__qualname__) in out:
        return
    out[("fn", fn.__module__, fn.__qualname__)] = inspect.getsource(fn)

    def names(code):
        yield from code.co_names
        for c in code.co_consts:
            if hasattr(c, "co_names"):
                yield from names(c)
    for nm in sorted(set(names(fn.__code__))):
        v = fn.__globals__.get(nm)
        if inspect.isfunction(v) and v.__module__ in MODULY_UJEC:
            _zrodlo(v, out)
        elif v is not None and isinstance(v, PROSTE):  # stała modułu (atrybuty i wbudowane: nie ma ich w globals)
            out[("stala", fn.__module__, nm)] = repr(v)


def _plik(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


_WSPOLNE = None


def odcisk(i):
    """Wszystko, od czego zależy obraz klipu ujęcia i: kod ujęcia (i funkcji, których używa), stan świata, długość,
    napis, jakość, kodek, język, wycinki (zestaw.py), świat (swiat.py), wersja silnika. Inny odcisk = klip od nowa."""
    global _WSPOLNE
    if _WSPOLNE is None:
        _WSPOLNE = [SILNIK, _plik(HERE / "zestaw.py"), _plik(HERE / "swiat.py"), os.environ.get("JEZYK", "pl")]
    a, b, ruch, txt, vs, vl = SCENES[i]
    zr = {}
    _zrodlo(FNS[i], zr)
    dane = [_WSPOLNE, KOL[i], KOL[i] in BUDUJ, sorted((repr(k), v) for k, v in zr.items()), repr(swiat.stan(i)),
            round(b - a, 6), math.ceil((b - a) * FPS - 1e-9), papier.Q, FPS, NAPISY, CRF, PRESET,
            txt if NAPISY else "", round(vs, 6), round(vl, 6), i == 0, i == len(SCENES) - 1]
    return hashlib.sha256(json.dumps(dane, ensure_ascii=False, default=str).encode()).hexdigest()[:20]


def _plik_odcisku(out):
    return Path(out).with_suffix(".odcisk.json")


def zapisz_odcisk(out, i, n):
    _plik_odcisku(out).write_text(json.dumps({"ujecie": ODN[i], "klucz": KOL[i], "klatki": n, "odcisk": odcisk(i)},
                                             ensure_ascii=False) + "\n", encoding="utf-8")


def aktualny(out, i):
    """Klip istnieje i powstał z tych samych danych, co teraz."""
    j = _plik_odcisku(out)
    if not Path(out).exists() or not j.exists():
        return False
    try:
        return json.loads(j.read_text(encoding="utf-8")).get("odcisk") == odcisk(i)
    except ValueError:
        return False


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
    # tylko to, co się zmieniło: klip z tym samym odciskiem zostaje (także po przerwanym renderze)
    stare = len(idx)
    idx = [i for i in idx if os.environ.get("NADPISZ") == "1" or not aktualny(out / f"{ODN[i]}.mp4", i)]
    print(f"klipy: do renderu {len(idx)} z {stare} (reszta bez zmian), PRESET={PRESET}, warstwy stałe: {'tak' if WARSTWY else 'nie'}",
          flush=True)
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
    elif cmd == "przyjmij":
        # klipy wyrenderowane przed odciskami: przyjmij je jako zgodne z obecnymi danymi (tylko gdy liczba klatek się zgadza)
        import subprocess
        out = Path(sys.argv[-1])
        for i in range(len(SCENES)):
            clip = out / f"{ODN[i]}.mp4"
            if FNS[i] is None or not clip.exists() or (only and i + 1 not in only) or _plik_odcisku(clip).exists():
                continue
            n = math.ceil((SCENES[i][1] - SCENES[i][0]) * FPS - 1e-9)
            got = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                                      "stream=nb_read_packets", "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout or 0)
            print(f"{ODN[i]} {KOL[i]}: {'przyjęty' if got == n else f'NIE — {got} klatek, ujęcie ma {n}'}")
            if got == n:
                zapisz_odcisk(clip, i, n)
    else:
        print(arkusz(only, sys.argv[3] if len(sys.argv) > 3 else None))
