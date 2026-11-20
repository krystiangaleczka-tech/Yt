"""Lektor autora w wersji EN „Syna słońca”: tnie nagranie reżysera na kwestie i wkłada je do lektor_en/ zamiast klonu.

Wzór: output/pierwszy-cesarz/zloz_lektor.py (kwestie autora + klon jednym głosem). Reżyser 20.11.2026: „dałem ci jakąś
część przeze mnie wyrecytowanego tekstu do filmu, potnij to i co się nadaje weź, a co się nie nadaje wygeneruj — jak
zawsze z naszymi lektorskimi wytycznymi” (Podręcznik → Lektor).

  1. Whisper (.venv-align, faster-whisper small) daje słowa z czasami → build/autor_sun/transkrypcja.json,
     dopasowanie słów do kwestii skryptu → build/autor_sun/dopasowanie.json (klucz, start, koniec, zgodność).
  2. uruchom:  python3 output/powstanie-japonii/autor_lektor.py tnij     — kwestie z nagrania → build/autor_sun/kwestie/
               python3 output/powstanie-japonii/autor_lektor.py wstaw    — do lektor_en/ (klon zostaje jako <klucz>.klon.wav)
     Kwestie z ODPADA zostają klonem (potknięcie, złe słowo, urwana kwestia).
Cięcie: początek od pierwszego głosu (−50 dB) z zapasem 0,08 s, koniec po ostatnim głosie przed co najmniej 0,4 s ciszy
z zapasem 0,15 s — bez obcinania ciszy drugi raz (zasada 9), tylko łagodne wejście 0,04 s i wygaszenie 0,12 s.
Obróbka jak w „Pierwszym cesarzu”: niżej o 0,25 półtonu (jak próbka klonu ref_en_teatr_nizej_0.25pt.wav) i ta sama ciepła
korekcja, żeby autor i klon brzmieli jednym głosem; tempo i pauzy zostają autora. Nagranie jest czyste (szum w przerwach
−65…−71 dB, pełne pasmo 48 kHz), więc bez odszumiania (zasada 1: filtry na gotowym głosie dokładają artefaktów).
Nagrania nie idą do repo (głos autora).
"""
import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"))
os.environ["JEZYK"] = "en"
from dane import kwestia, ujecia  # noqa: E402

BUD = HERE / "build" / "autor_sun"
NAGRANIE = BUD / "sun_48k.wav"  # Sun.m4a (20.11.2026) → mono 48 kHz
KWESTIE = BUD / "kwestie"
LEKTOR = HERE / "lektor_en"
ZRODLO = "autor (nagranie Sun.m4a, 20.11.2026; niżej o 0,25 półtonu, ciepła korekcja jak w „Pierwszym cesarzu”)"
# kwestie z nagrania, które zostają klonem: zawahanie i „elder” zamiast „eldest” (hak_rana), zacięcie na „sacred”
# i za długa na 5 s (hak_koronacja), „Amaterasu set roosters” zamiast „The gods set roosters” (koguty), „from head… to
# heaven” (zejscie), nagranie urywa się w połowie kwestii (flota), początek kwestii ucięty już w nagraniu — twarde cięcie
# z cyfrowej ciszy w głos (kadzie: „Susanoo”, „turned again” zamiast „the girl”; prawnuk: „Ninigi's” słychać jako „Biggest”)
ODPADA = {"hak_rana", "hak_koronacja", "koguty", "zejscie", "flota", "kadzie", "prawnuk"}
OBNIZ = 0.25
CIEPLO = ("lowshelf=f=160:g=3,equalizer=f=3500:t=q:w=1.2:g=-2.5,highshelf=f=7000:g=-2,"
          "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1.5,loudnorm=I=-16:TP=-2")
PROG, CISZA_MIN = -50.0, 0.40


def wczytaj(p):
    with wave.open(str(p)) as w:
        sr, x = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x, sr


def poziomy(x, sr, krok=0.01):
    h = int(sr * krok)
    n = len(x) // h
    return 10 * np.log10(np.mean(x[:n * h].reshape(n, h) ** 2, axis=1) + 1e-12)


def granice(db, s0, e0, nast, krok=0.01):
    """(start, koniec) kwestii w sekundach: pierwszy głos koło s0 i ostatni głos po e0 przed ciszą ≥ CISZA_MIN."""
    i0 = max(0, int((s0 - 0.4) / krok))
    while i0 < len(db) and db[i0] < PROG:
        i0 += 1
    j, cicho, ost = int((e0 - 0.1) / krok), 0, int((e0 - 0.1) / krok)
    while j < len(db) and j * krok < nast:
        if db[j] < PROG:
            cicho += 1
            if cicho * krok >= CISZA_MIN:
                break
        else:
            cicho, ost = 0, j
        j += 1
    return max(0.0, i0 * krok - 0.08), min(nast - 0.05, (ost + 1) * krok + 0.15)


def tnij():
    dop = [r for r in json.loads((BUD / "dopasowanie.json").read_text(encoding="utf-8")) if not r.get("brak")]
    x, sr = wczytaj(NAGRANIE)
    db = poziomy(x, sr)
    KWESTIE.mkdir(exist_ok=True)
    spis = []
    for n, r in enumerate(dop):
        nast = dop[n + 1]["start"] - 0.05 if n + 1 < len(dop) else len(x) / sr
        a, b = granice(db, r["start"], r["koniec"], nast)
        y = x[int(a * sr):int(b * sr)].copy()
        with wave.open(str(KWESTIE / f"{r['klucz']}.wav"), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
        spis.append({"klucz": r["klucz"], "od": round(a, 2), "do": round(b, 2), "dlugosc": round(b - a, 2), "zgodnosc": r["wynik"],
                     "odpada": r["klucz"] in ODPADA})
        print(f"{r['klucz']:14s} {a:7.2f}–{b:7.2f}  {b - a:5.2f} s  zgodność {r['wynik']:.2f}{'  ODPADA' if r['klucz'] in ODPADA else ''}")
    (BUD / "kwestie.json").write_text(json.dumps(spis, ensure_ascii=False, indent=1), encoding="utf-8")


# Dopasowanie do osi (reżyser 20.11.2026: „dopasuj do timeline'u”, „poprzyspieszaj moje mówienie tak, żeby było dobrze”):
# kwestia autora wolniejsza niż TEMPO_MIN słowa/s jest lekko przyspieszona (atempo, wysokość głosu bez zmian), najwyżej
# o PRZYSP_MAX — przy takim przyspieszeniu głos brzmi naturalnie (Podręcznik → Lektor 8 zabrania tylko zwalniania > 3 %).
# Autor czytał średnio 2,57 słowa/s, klon 2,84; pauzy są już przycięte do zakresów (pauzy_lektora).
TEMPO_MIN, PRZYSP_MAX = 2.5, 1.08


def przyspieszenie(txt, dl):
    from dane import slownie
    slow = len(slownie(txt).split())
    return round(min(PRZYSP_MAX, max(1.0, TEMPO_MIN / (slow / max(0.5, dl - 0.25)))), 3)


def dlugosc(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True)
    return round(float(out.stdout), 3)


def wstaw():
    kopia = HERE / "build" / "lektor_en_przed_autorem_2026-11-20"
    if not kopia.exists():
        shutil.copytree(LEKTOR, kopia)
    teksty = {u[2]: kwestia(u[7]) for u in ujecia() if kwestia(u[7])}
    f, sr = 2 ** (-OBNIZ / 12), 44100
    uzyte = []
    for src in sorted(KWESTIE.glob("*.wav")):
        klucz = src.stem
        if klucz in ODPADA or klucz not in teksty:
            continue
        dst = LEKTOR / f"{klucz}.wav"
        if dst.exists() and not (LEKTOR / f"{klucz}.klon.wav").exists():
            shutil.copy2(dst, LEKTOR / f"{klucz}.klon.wav")  # zapas: kwestia klonu
        dl0 = dlugosc(src)
        tempo = przyspieszenie(teksty[klucz], dl0)
        dl0 = dl0 / tempo
        af = (f"asetrate=48000*{f:.6f},aresample={sr},atempo={1 / f:.6f},atempo={tempo}," + CIEPLO
              + f",afade=t=in:d=0.04,afade=t=out:st={max(0.0, dl0 - 0.12):.3f}:d=0.12")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-af", af, "-ar", str(sr), "-ac", "1",
                        "-c:a", "pcm_s16le", str(dst)], check=True)
        meta = {"text": teksty[klucz], "spoken": teksty[klucz], "duration": dlugosc(dst), "zrodlo": ZRODLO, "tempo": tempo,
                "klon_zapas": f"{klucz}.klon.wav" if (LEKTOR / f"{klucz}.klon.wav").exists() else None}
        (LEKTOR / f"{klucz}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        uzyte.append(klucz)
    print(f"lektor_en: głosem autora {len(uzyte)} kwestii; poprzedni lektor w {kopia}")


# ---------- drugie nagranie: kwestie od ujęcia 44 do końca, czytane w aucie (reżyser 20.11.2026, „Głos 261120_201902.m4a”) ----------
# „Niektóre kwestie poprawiałem albo podchodziłem do nich kilka razy — bierzesz ostatnie podejście; jak przerwy między
# wyrazami są za długie, skróć; przeprowadź całe nagranie przez naszą obróbkę i dopasuj do timeline'u.”
# Szum auta (−23…−25 dB w przerwach): całe nagranie przechodzi przez odszumiacz resemble-enhance (highpass 70 Hz, model
# odszumiacza, bez dyfuzji pasma — nagranie ma pełne 48 kHz) → build/autor_auto/auto_dn.wav; potem cięcie po słowach Whispera
# (ostatnie dobre podejście), pauzy w kwestii z zakresów (docos/pauzy_lektora.py: przecinek, zdanie, zawiecha bez znaku
# skrócona do 0,15–0,25 s), na końcu ten sam głos co klon (OBNIZ, CIEPLO). Tempa autora się nie rozciąga (Podręcznik → Lektor 8).
AUTO = HERE / "build" / "autor_auto"
ZRODLO_AUTO = ("autor (nagranie z auta „Głos 261120_201902.m4a”, 20.11.2026; odszumione resemble-enhance, pauzy z zakresów, "
               "niżej o 0,25 półtonu, ciepła korekcja)")
# ręczne granice (sekundy nagrania), gdzie dopasowanie nie wystarcza: (start, koniec, szukaj_wstecz)
RECZNIE = {
    "trzy_nogi": (137.00, 145.90, 0.0),   # z „Later,” (po przecinku dłuższa pauza — automat zaczynał od „it was”)
    "strzala_nieba": (205.00, 213.40, 0.0),  # do „Nigihayahi” (po „gods,” pauza — automat kończył przed imieniem)
    "smierc": (281.70, 290.52, 0.0),      # drugie podejście („at 127”), pierwsze mówiło „a hundred and seventy”
    "przebudzenie": (113.17, 122.80, 0.0),  # falstart „When… Iwarebiko” (110,4–112,3 s), potem całe zdanie od nowa
    "linia": (310.65, 319.54, 0.0),       # trzecie podejście „With him tradition says began…” (przed nim urwane „with”)
    "kronika": (323.90, 334.44, 0.0),
    "kofun": (423.10, 434.78, 0.0),       # podejście z „half a kilometre” (ostatnie mówi „half mile” — kurhan ma 486 m)
    "koronacja": (503.80, 519.00, 0.0),   # od „In 2019” — bez „However, today,” (tekst i napisy jak w skrypcie)
    "koniec": (535.64, 545.50, 0.0),      # drugie podejście („calls itself”); przed nim urwane słowo (534,2–534,7 s)
    "dzieki": (546.30, 551.62, 0.0),      # „Thank you very much … do my best”, bez „peace out”
}
WYTNIJ = {"zdrada": [(218.33, 225.30)]}  # klucz → [(od, do)] w sekundach nagrania. zdrada: „But Nigihayahi decided that the”
# z pierwszego podejścia (dalej mówił „new newcomer”) + „newcomer had the better claim…” z drugiego (zaczynało się od
# „But Nigi… But Nigihayahi decided that newcomer” — bez „the”); odcinki głosu po odszumieniu i Whisper, zmierzone 20.11


def granice_auto(db, s0, e0, wstecz, poprz, nast, krok=0.01):
    """Start: najwcześniejszy głos przed s0 (do `wstecz` s, nie przed poprz) bez ciszy ≥ 0,3 s po drodze; koniec: ostatni głos
    po e0 przed ciszą ≥ 0,35 s (nie dalej niż nast)."""
    i = int(s0 / krok)
    while i < len(db) and db[i] < PROG:   # pierwszy głos od s0
        i += 1
    j, cicho, pocz = i - 1, 0, i
    while j > 0 and j * krok > max(poprz, s0 - wstecz):
        if db[j] < PROG:
            cicho += 1
            if cicho * krok >= 0.30:
                break
        else:
            cicho, pocz = 0, j
        j -= 1
    k, cicho, ost = int((e0 - 0.15) / krok), 0, int((e0 - 0.15) / krok)
    while k < len(db) and k * krok < nast:
        if db[k] < PROG:
            cicho += 1
            if cicho * krok >= 0.35:
                break
        else:
            cicho, ost = 0, k
        k += 1
    return max(poprz, pocz * krok - 0.08), min(nast, (ost + 1) * krok + 0.15)


def tnij_auto():
    dop = {r["klucz"]: r for r in json.loads((AUTO / "dopasowanie.json").read_text(encoding="utf-8")) if not r.get("brak")}
    x, sr = wczytaj(AUTO / "auto_dn_mono.wav")
    db = poziomy(x, sr)
    kl = list(dop)
    out = AUTO / "kwestie"
    out.mkdir(exist_ok=True)
    spis, poprz = [], 0.0
    for n, k in enumerate(kl):
        r = dop[k]
        s0, e0, wstecz = RECZNIE.get(k, (r["start"], r["koniec"], 1.5))
        nk = kl[n + 1] if n + 1 < len(kl) else None
        nast = (RECZNIE[nk][0] if nk in RECZNIE else dop[nk]["start"] - 0.25) if nk else len(x) / sr
        if k in RECZNIE:
            a, b = granice_auto(db, s0, e0, 0.0, poprz, min(nast, e0 + 0.6))
        else:
            a, b = granice_auto(db, s0, e0, wstecz, poprz, nast)
        y = x[int(a * sr):int(b * sr)].copy()
        for od, do in sorted(WYTNIJ.get(k, []), reverse=True):  # wycięcie potknięcia (po pomiarze ciszy wokół)
            i0, i1 = int((od - a) * sr), int((do - a) * sr)
            f = int(0.01 * sr)
            y = np.concatenate([y[:i0 - f], y[i0 - f:i0] * np.linspace(1, 0, f), y[i1:i1 + f] * np.linspace(0, 1, f), y[i1 + f:]])
        with wave.open(str(out / f"{k}.wav"), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
        spis.append({"klucz": k, "od": round(a, 2), "do": round(b, 2), "dlugosc": round(len(y) / sr, 2)})
        print(f"{k:14s} {a:7.2f}–{b:7.2f}  {len(y) / sr:5.2f} s")
        poprz = b
    (AUTO / "kwestie.json").write_text(json.dumps(spis, ensure_ascii=False, indent=1), encoding="utf-8")


def wstaw_auto(enh_python):
    """Pauzy z zakresów (pauzy_lektora.plik w środowisku z soundfile) → ten sam głos co klon → lektor_en/."""
    teksty = {u[2]: kwestia(u[7]) for u in ujecia() if kwestia(u[7])}
    f, sr = 2 ** (-OBNIZ / 12), 44100
    pz = AUTO / "pauzy"
    pz.mkdir(exist_ok=True)
    kopia = HERE / "build" / "lektor_en_przed_autorem_auto_2026-11-20"
    if not kopia.exists():
        shutil.copytree(LEKTOR, kopia)
    uzyte = []
    for src in sorted((AUTO / "kwestie").glob("*.wav")):
        k = src.stem
        if k not in teksty:
            continue
        mowa = slownie_en(teksty[k])

        def pauzy(wej, wyj):
            subprocess.run([enh_python, "-I", "-c", (
                "import sys, json; sys.path.insert(0, %r); import pauzy_lektora as P; "
                "r = P.plik(%r, %r, %r, P.ziarno_kwestii(%r)); json.dump(r, open(%r, 'w'), ensure_ascii=False)") % (
                str(HERE.parents[1] / "docos"), str(wej), str(wyj), mowa, k, str(pz / f"{k}.json"))], check=True)

        pauzy(src, pz / f"{k}.wav")
        # przyspieszenie liczone po przycięciu pauz; nakłada się je na samą mowę PRZED ustawieniem pauz — atempo na gotowych
        # pauzach z cyfrową ciszą ucinało wybrzmienie słów (uciecia_lektora: jomon, trzy_nogi, 20.11)
        tempo = przyspieszenie(teksty[k], dlugosc(pz / f"{k}.wav"))
        if tempo > 1.0:
            szybciej = pz / f"{k}.szybciej.wav"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-af", f"atempo={tempo}", "-c:a", "pcm_s16le",
                            str(szybciej)], check=True)
            pauzy(szybciej, pz / f"{k}.wav")
        dst = LEKTOR / f"{k}.wav"
        if dst.exists() and not (LEKTOR / f"{k}.klon.wav").exists():
            shutil.copy2(dst, LEKTOR / f"{k}.klon.wav")
        dl0 = dlugosc(pz / f"{k}.wav")
        af = (f"asetrate=44100*{f:.6f},aresample={sr},atempo={1 / f:.6f}," + CIEPLO
              + f",afade=t=in:d=0.04,afade=t=out:st={max(0.0, dl0 - 0.12):.3f}:d=0.12")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(pz / f"{k}.wav"), "-af", af, "-ar", str(sr), "-ac", "1",
                        "-c:a", "pcm_s16le", str(dst)], check=True)
        meta = {"text": teksty[k], "spoken": mowa, "duration": dlugosc(dst), "zrodlo": ZRODLO_AUTO, "tempo": tempo,
                "pauzy": json.loads((pz / f"{k}.json").read_text(encoding="utf-8")),
                "klon_zapas": f"{k}.klon.wav" if (LEKTOR / f"{k}.klon.wav").exists() else None}
        (LEKTOR / f"{k}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        uzyte.append(k)
    print(f"lektor_en: z nagrania z auta {len(uzyte)} kwestii; poprzedni lektor w {kopia}")


def slownie_en(txt):
    from dane import slownie
    return slownie(txt)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "wstaw_auto":
        wstaw_auto(sys.argv[2] if len(sys.argv) > 2 else str(HERE.parents[4] / "pilot/.venv-enhance/bin/python"))
    else:
        {"tnij": tnij, "wstaw": wstaw, "tnij_auto": tnij_auto}[cmd]()
