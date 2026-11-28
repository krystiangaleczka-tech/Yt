"""„The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (kopia output/bonnie-i-clyde/zloz.py; reżyser 28.11.2026:
„rób render tylko 1080p z tym rozwiązaniem 1440p, żeby odblokować lepszą jakość 1080p”).
Składa cały film do wrzucenia na YouTube: klipy ujęć (render.py klipy) jeden po drugim, lektor w swoich oknach
kwestii, muzyka i efekty — zmiksowane tak samo jak montaż w Studio (ścieżka Muzyka 80 %, Efekty 100 %, Lektor 100 %,
suma bez normalizacji i ogranicznik 0,95 jak w eksporcie Studio, studio_timeline/render.py).

Kwestie stoją na początku klipu + start okna (oddech 0,6 s), z czasem liczonym z prawdziwej liczby klatek klipów.
Muzyka i efekty (efekty.py) są liczone w sekundach rozpiski, więc klipy muszą być z FILM=1 (render.py: klatki na
wspólnej siatce czasu filmu, film trwa tyle co oś w Studio). Klipy zaokrąglone w górę (klipy do Studio) dają film
o ponad sekundę dłuższy od osi — wtedy zloz.py odmawia, zamiast złożyć film z dźwiękiem obok obrazu.

  FILM=1 ROZDZIELCZOSC=1440 PROCESY=3 python3 render.py klipy build/klipy_1440p   — klipy (CRF 21, ok. 3 h na Macu)
  python zloz.py <katalog z klipami> <plik wyjściowy.mp4>   — film z pełnym dźwiękiem
  python zloz.py --sprawdz                                    — przed renderem: czy lektor, muzyka i efekty są na
                                                               miejscu i z tej samej wersji co rozpiska
  JEZYK=en …                                                  — wersja angielska (lektor_en/, dzwiek_en/)
  BEZ_MUZYKI=1 …                                              — sam obraz i lektor (podgląd)
"""
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/szamil-diuna/ujecia"))
from dane import HAK, JEZYK, LEKTOR, kwestia, okno_kwestii, ujecia  # noqa: E402

FPS = 24
DZWIEK = HERE / ("dzwiek_en" if JEZYK == "en" else "dzwiek")  # muzyka.wav i efekty.wav z efekty.py
# głośność ścieżek jak w montażu w Studio (projekt prj_738d7663d85e4b2d: Muzyka 0,8, Efekty i Lektor 1,0 — studio_film.dzwiek)
MUZYKA, EFEKTY = 0.8, 1.0


def klatki(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def dlugosc_wav(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def sprawdz(muzyka=True):
    """Lista problemów z dźwiękiem (pusta = można renderować i składać). Nagrania .wav nie idą na GitHuba, więc na PC
    mogą zostać stare: nagranie musi mieć długość z lektor*/<klucz>.json, z którego rozpiska liczy długości ujęć."""
    bledy, UJ = [], ujecia()
    for _akt, _k, klucz, *rest in UJ:
        txt = kwestia(rest[-1])
        if not txt:
            continue
        wav, meta = LEKTOR / f"{klucz}.wav", LEKTOR / f"{klucz}.json"
        if not wav.exists() or not meta.exists():
            bledy.append(f"brak nagrania lektora: {wav if not wav.exists() else meta}")
            continue
        m = json.loads(meta.read_text(encoding="utf-8"))
        if m.get("text") != txt:
            bledy.append(f"{meta.name}: tekst kwestii inny niż w rozpisce")
        elif abs(dlugosc_wav(wav) - m["duration"]) > 0.02:
            bledy.append(f"{wav.name}: nagranie ma {dlugosc_wav(wav):.2f} s, a rozpiska liczy {m['duration']:.2f} s"
                         " — to stare nagranie, skopiuj lektora z Maca")
    if muzyka:
        dur = sum(u[5] for u in UJ)
        for nazwa in ("muzyka.wav", "efekty.wav"):
            p = DZWIEK / nazwa
            if not p.exists():
                bledy.append(f"brak {p} — skopiuj dźwięk z Maca")
            elif abs(dlugosc_wav(p) - dur) > 0.05:
                bledy.append(f"{p}: {dlugosc_wav(p):.1f} s, a film ma {dur:.1f} s — dźwięk z innej wersji filmu")
    return bledy


def main(klipy, wynik):
    klipy, wynik = Path(klipy).resolve(), Path(wynik).resolve()  # lista concat: ffmpeg czyta ścieżki względem katalogu listy
    muzyka = os.environ.get("BEZ_MUZYKI") != "1"
    bledy = sprawdz(muzyka)
    if bledy:
        raise SystemExit("\n".join(bledy))
    UJ = ujecia()
    lista, glosy, t = [], [], 0.0
    for akt, k, klucz, *_rest in UJ:
        clip = klipy / f"d{akt:02d}_{k:02d}.mp4"
        if not clip.exists():
            raise SystemExit(f"brak klipu: {clip}")
        snd = _rest[-1]
        if kwestia(snd):
            glosy.append((LEKTOR / f"{klucz}.wav", t + okno_kwestii(snd, klucz in HAK)[0]))  # w haku krótszy oddech (jak w Studio)
        lista.append(clip)
        t += klatki(clip) / FPS
    dur = sum(u[5] for u in UJ)
    if muzyka and abs(t - dur) > 1 / FPS:
        raise SystemExit(f"klipy trwają razem {t:.2f} s, a oś filmu {dur:.2f} s — muzyka i efekty rozjechałyby się"
                         " z obrazem. Klipy do filmu renderuj z FILM=1.")
    concat = wynik.with_suffix(".lista.txt")
    concat.write_text("".join(f"file '{c.as_posix()}'\n" for c in lista), encoding="utf-8")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat)]
    for wav, _ in glosy:
        cmd += ["-i", str(wav)]
    fil = "".join(f"[{n + 1}:a]adelay={round(s * 1000)}:all=1[a{n}];" for n, (_, s) in enumerate(glosy))
    sciezki = [f"[a{n}]" for n in range(len(glosy))]
    if muzyka:
        for nazwa, glosnosc in (("muzyka.wav", MUZYKA), ("efekty.wav", EFEKTY)):
            cmd += ["-i", str(DZWIEK / nazwa)]
            fil += f"[{len(sciezki) + 1}:a]volume={glosnosc}[{nazwa[:2]}];"
            sciezki.append(f"[{nazwa[:2]}]")
    # jak eksport Studio: suma ścieżek bez normalizacji, ogranicznik 0,95, cisza do końca obrazu
    fil += "".join(sciezki) + f"amix=inputs={len(sciezki)}:normalize=0:duration=longest,alimiter=limit=0.95,apad[g]"
    cmd += ["-filter_complex", fil, "-map", "0:v", "-map", "[g]", "-c:v", "copy", "-c:a", "aac", "-b:a", "384k",
            "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", str(wynik)]
    subprocess.run(cmd, check=True)
    concat.unlink()
    print(f"{wynik}: {t:.1f} s, {len(lista)} ujęć, {len(glosy)} kwestii" + (", muzyka i efekty" if muzyka else ", bez muzyki"))


if __name__ == "__main__":
    if sys.argv[1:] == ["--sprawdz"]:
        problemy = sprawdz(os.environ.get("BEZ_MUZYKI") != "1")
        print("\n".join(problemy) or f"Dźwięk gotowy: lektor ({LEKTOR.name}), muzyka i efekty ({DZWIEK.name}).")
        sys.exit(1 if problemy else 0)
    main(sys.argv[1], sys.argv[2])
