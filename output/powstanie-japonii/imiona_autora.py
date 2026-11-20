"""Japońskie imiona głosem autora w kwestiach klona (reżyser 20.11.2026: „weź z moich próbek te wszystkie nazwy japońskie,
Izanami, Izanagi i tak dalej, wytnij te słowa i wrzuć w te kwestie, gdzie będzie wygenerowany głos”).

  .venv-align/bin/python -I output/powstanie-japonii/imiona_autora.py bank            — imiona z kwestii autora → build/imiona/
  .venv-align/bin/python -I output/powstanie-japonii/imiona_autora.py wstaw [klucz …] — podmiana w lektor_en/ (klon)

Kwestie autora leżą w build/lektor_en_autor_2011/ (już z obróbką „jeden głos z klonem”: niżej o 0,25 półtonu, ciepła
korekcja, głośność — autor_lektor.py), więc wycięte imię ma tę samą barwę co klon. Granice słowa: Whisper (faster-whisper
small, słowa z czasami) dopasowany do tekstu skryptu — imię leży między końcem słowa przed nim a początkiem słowa po nim;
granicę przesuwa się do najcichszego miejsca w ±0,1 s. Wklejenie z przenikaniem 12 ms, głośność imienia jak głośność
wyciętego fragmentu klona (±6 dB). Oryginał klona zostaje jako <klucz>.przed_imionami.wav, w json lista podmian.
Imienia, którego granic nie da się pewnie znaleźć (sąsiednie słowo nierozpoznane), się nie rusza — trafia do raportu.
"""
import difflib
import json
import os
import re
import shutil
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"))
os.environ["JEZYK"] = "en"
from dane import kwestia, slownie, ujecia  # noqa: E402
from kwestie_en import WYMOWA_EN  # noqa: E402

AUTOR = HERE / "build" / "lektor_en_autor_2011"
LEKTOR = HERE / "lektor_en"
BANK = HERE / "build" / "imiona"
IMIONA = {a.lower() for a, _ in WYMOWA_EN} | {"kyushu", "osaka"} - {"osaka"}
XF, OKNO = 0.012, 0.10
# imiona, przed którymi Whisper podał koniec poprzedniego słowa za wcześnie: podmiana zaczyna się od pierwszej ciszy po nim
# (wrona: „crow” w klonie kończy się 1,85 s, Whisper mówił 1,6 s — uciecia_lektora, 21.11)
OD_CISZY = {("wrona", "Yatagarasu")}

_model = None


def model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    return _model


def czytaj(p):
    with wave.open(str(p)) as w:
        sr, x = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x, sr


def zapisz(p, x, sr):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def tokeny(txt):
    return [w for w in re.findall(r"[A-Za-z0-9'\-]+", txt) if w.strip("'-")]


def norm(w):
    """Słowo do porównania: małe litery, bez interpunkcji (przecinek przy słowie psuł dopasowanie) i bez „'s”."""
    w = re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'")).strip("'")
    return w[:-2] if w.endswith("'s") else w


LICZBY = {"2019": "twenty nineteen", "660": "six hundred and sixty", "1400": "fourteen hundred", "127": "a hundred and twenty-seven",
          "712": "seven twelve", "720": "seven twenty", "1260": "twelve hundred and sixty", "1784": "seventeen eighty-four",
          "57": "fifty-seven", "1873": "eighteen seventy-three", "1966": "nineteen sixty-six", "126th": "hundred and twenty-sixth",
          "45": "forty-five", "8": "eight", "100": "a hundred"}


def rowne(a, b):
    a, b = norm(a), norm(b)
    return a == b or (len(a) > 3 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.75)


def slowa(x, sr):
    """Słowa Whispera z czasami (s)."""
    n16 = int(len(x) * 16000 / sr)
    x16 = np.interp(np.linspace(0, len(x) - 1, n16), np.arange(len(x)), x).astype(np.float32)
    segs, _ = model().transcribe(x16, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words:
            t = w.word.strip()
            if not t:
                continue
            klucz = re.sub(r"[^0-9a-z]", "", t.lower())
            if klucz in LICZBY:  # liczba zapisana cyframi → słowa z tym samym czasem (skrypt ma liczby słowami)
                out += [(z, w.start, w.end) for z in LICZBY[klucz].split()]
            else:
                out.append((t, w.start, w.end))
    return out


def dopasuj(skrypt, rozp):
    """Pary (indeks słowa skryptu, indeks słowa rozpoznanego) — najdłuższy wspólny podciąg z tolerancją."""
    n, m = len(skrypt), len(rozp)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if rowne(skrypt[i], rozp[j][0]) else max(L[i + 1][j], L[i][j + 1])
    pary, i, j = {}, 0, 0
    while i < n and j < m:
        if rowne(skrypt[i], rozp[j][0]) and L[i][j] == L[i + 1][j + 1] + 1:
            pary[i] = j
            i, j = i + 1, j + 1
        elif L[i + 1][j] >= L[i][j + 1]:
            i += 1
        else:
            j += 1
    return pary


def poziomy(x, sr, krok=0.005):
    h = int(sr * krok)
    k = len(x) // h
    return 10 * np.log10(np.mean(x[:k * h].reshape(k, h) ** 2, axis=1) + 1e-12)


def najciszej(db, t, krok=0.005):
    """Najcichsze miejsce w ±OKNO wokół t (s)."""
    a, b = max(0, int((t - OKNO) / krok)), min(len(db), int((t + OKNO) / krok) + 1)
    if a >= b:
        return t
    return (a + int(np.argmin(db[a:b]))) * krok


def glos_w(db, a, b, krok=0.005, prog=-42):
    """Zawęża [a, b] do głosu: pierwsza i ostatnia ramka powyżej progu, z zapasem 40 ms przed i 80 ms po (wybrzmienie)."""
    i0, i1 = int(a / krok), int(b / krok)
    glos = np.where(db[i0:i1] > prog)[0]
    if not len(glos):
        return a, b
    return max(a, (i0 + glos[0]) * krok - 0.04), min(b, (i0 + glos[-1] + 1) * krok + 0.08)


def mowa_granice(db, krok=0.005, prog=-45):
    glos = np.where(db > prog)[0]
    return (glos[0] * krok, (glos[-1] + 1) * krok) if len(glos) else (0.0, len(db) * krok)


def imiona_w(x, sr, txt, max_dl=1.6):
    """[(token imienia, początek, koniec)] w nagraniu kwestii; None w miejscu imienia, którego granic nie da się ustalić."""
    sk = tokeny(slownie(txt))
    rozp = slowa(x, sr)
    pary = dopasuj(sk, rozp)
    db = poziomy(x, sr)
    pocz, kon = mowa_granice(db)
    wynik = []
    for i, tok in enumerate(sk):
        if norm(tok) not in IMIONA:
            continue
        prev_ok = i == 0 or (i - 1) in pary
        nast = None if i == len(sk) - 1 else pary.get(i + 1)
        if nast is None and i < len(sk) - 1 and prev_ok:
            # następne słowo ze skryptu złożone z łącznikiem („great-grandson”) Whisper dzieli na kilka — wystarczy, że
            # rozpoznane słowo jest początkiem następnego słowa skryptu
            pierwszy = norm(sk[i + 1]).replace("-", "")
            od = pary[i - 1] + 1 if i > 0 else 0
            nast = next((j for j in range(od + 1, len(rozp)) if len(norm(rozp[j][0])) >= 3
                         and pierwszy.startswith(norm(rozp[j][0]).replace("-", ""))), None)
        next_ok = i == len(sk) - 1 or nast is not None
        if not (prev_ok and next_ok):
            wynik.append((tok, None, None, "", ""))
            continue
        a = pocz if i == 0 else najciszej(db, rozp[pary[i - 1]][2])
        b = kon if i == len(sk) - 1 else najciszej(db, rozp[nast][1])
        a, b = glos_w(db, a, b)  # sam głos imienia — przerwy (np. po przecinku) zostają tam, gdzie były
        if b - a < 0.18 or b - a > max_dl:  # klon czyta imiona sylabami z przerwami — dla klona limit większy
            wynik.append((tok, None, None, "", ""))
            continue
        wynik.append((tok, a, b, sk[i - 1] if i else "", sk[i + 1] if i + 1 < len(sk) else ""))
    return wynik


def bank():
    """Najlepsze wykonanie każdego imienia (forma z „'s” osobno) z kwestii autora."""
    BANK.mkdir(parents=True, exist_ok=True)
    kand = {}
    for u in ujecia():
        k, txt = u[2], kwestia(u[7])
        if not txt or not (AUTOR / f"{k}.wav").exists():
            continue
        x, sr = czytaj(AUTOR / f"{k}.wav")
        for tok, a, b, przed, po in imiona_w(x, sr, txt):
            if a is None:
                print(f"  (bank) {k}: „{tok}” bez pewnych granic")
                continue
            forma = tok.lower().replace("’", "'").strip("-")
            kand.setdefault(forma, []).append((b - a, k, a, b, przed, po))
    spis = {}
    for forma, lst in kand.items():
        # każde wykonanie słuchane osobno: odpada, jeśli Whisper słyszy w nim słowo funkcyjne sąsiada („to Yamato”,
        # „the Wa”) — granica zahaczyła o sąsiednie słowo; z czystych bierze się najbliższe typowej długości
        med = float(np.median([d for d, *_ in lst]))
        czyste = []
        for d, k, a_, b_, przed, po in lst:
            x, sr = czytaj(AUTOR / f"{k}.wav")
            y = x[int(a_ * sr):int(b_ * sr)]
            slysze = osobno(y, sr)
            sl = tokeny(slysze)
            # przeciek sąsiada: wycinek zaczyna się słowem stojącym przed imieniem albo kończy słowem po nim
            obce = ([sl[0]] if sl and przed and norm(sl[0]) == norm(przed) and len(sl) > 1 else []) + \
                   ([sl[-1]] if sl and po and norm(sl[-1]) == norm(po) and len(sl) > 1 else [])
            print(f"   {forma:14s} {k:14s} {d:4.2f} s | {slysze}{'  ← obce: ' + ' '.join(obce) if obce else ''}")
            if not obce:
                czyste.append((d, k, a_, b_))
        if not czyste:
            print(f"{forma:16s} — wszystkie wykonania zahaczają o sąsiednie słowo, zostaje głos klona")
            continue
        d, k, a_, b_ = min(czyste, key=lambda z: abs(z[0] - med))
        x, sr = czytaj(AUTOR / f"{k}.wav")
        zapisz(BANK / f"{forma}.wav", x[int(a_ * sr):int(b_ * sr)], sr)
        spis[forma] = {"z_kwestii": k, "od": round(a_, 3), "do": round(b_, 3), "wykonan": len(lst), "czystych": len(czyste)}
        print(f"{forma:16s} z {k:14s} {d:.2f} s ({len(czyste)}/{len(lst)} czystych)")
    (BANK / "spis.json").write_text(json.dumps(spis, ensure_ascii=False, indent=1), encoding="utf-8")


OBCE = {"to", "the", "a", "an", "in", "of", "is", "and", "on", "you", "be", "but", "dont", "oh", "that", "son", "by", "at"}


def osobno(y, sr):
    """Co słychać w samym wycinku (z ciszą dookoła)."""
    x16 = np.interp(np.linspace(0, len(y) - 1, int(len(y) * 16000 / sr)), np.arange(len(y)), y).astype(np.float32)
    x16 = np.concatenate([np.zeros(8000, np.float32), x16, np.zeros(8000, np.float32)])
    segs, _ = model().transcribe(x16, language="en", beam_size=5)
    return " ".join(z.text.strip() for z in segs)


def rms(y):
    return float(np.sqrt(np.mean(y ** 2) + 1e-12))


def wstaw(tylko=()):
    spis = json.loads((BANK / "spis.json").read_text(encoding="utf-8"))
    raport = []
    for u in ujecia():
        k, txt = u[2], kwestia(u[7])
        if not txt or (tylko and k not in tylko):
            continue
        meta_p = LEKTOR / f"{k}.json"
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        if "autor" in str(meta.get("zrodlo", "")) or meta.get("text") != txt:
            continue
        zrodlo = LEKTOR / f"{k}.przed_imionami.wav"
        if not zrodlo.exists():
            shutil.copy2(LEKTOR / f"{k}.wav", zrodlo)
        x, sr = czytaj(zrodlo)
        podm, out, last = [], [], 0
        f = int(XF * sr)
        for tok, a, b, _przed, _po in imiona_w(x, sr, txt, max_dl=3.5):
            forma = tok.lower().strip("-")
            if a is None or forma not in spis:
                raport.append(f"{k}: „{tok}” zostaje głosem klona ({'brak granic' if a is None else 'brak w banku'})")
                continue
            # początek podmiany w ciszy przed imieniem: cofnij do najbliższej ciszy (≤ 0,25 s), żeby nie uciąć końcówki
            # poprzedniego słowa, gdy Whisper podał jego koniec za wcześnie (wrona: „crow”)
            dbx = poziomy(x, sr)
            j = int(a / 0.005)
            if j < len(dbx) and dbx[max(0, j - 1)] > -45:
                k0 = j
                while k0 > 0 and (j - k0) * 0.005 < 0.25 and dbx[k0] > -50:
                    k0 -= 1
                if dbx[k0] <= -50 and (j - k0) * 0.005 < 0.25:
                    # koniec ciszy przed imieniem → pierwsza ramka głosu po niej, z zapasem
                    k1 = k0
                    while k1 < len(dbx) and dbx[k1] <= -50:
                        k1 += 1
                    a = max(0.0, k1 * 0.005 - 0.02) if k1 * 0.005 < b else a
            if (k, tok) in OD_CISZY:
                j = int(a / 0.005)
                while j < len(dbx) and dbx[j] > -58:  # aż wybrzmienie słowa przed imieniem zejdzie do ciszy
                    j += 1
                a = j * 0.005
            y, sr2 = czytaj(BANK / f"{forma}.wav")
            assert sr2 == sr
            g = float(np.clip(rms(x[int(a * sr):int(b * sr)]) / rms(y), 0.5, 2.0))
            y = y * g
            # samo imię wchodzi i wybrzmiewa łagodnie — obok może być cisza klona (uciecia_lektora: itsuse)
            n1, n2 = int(0.015 * sr), int(0.06 * sr)
            y[:n1] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n1, dtype=np.float32))
            y[-n2:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, n2, dtype=np.float32))
            ia, ib = int(a * sr), int(b * sr)
            seg = x[last:ia].copy()
            if out and len(seg) > f:  # przenikanie z poprzednim imieniem
                pass
            out.append(seg)
            out.append(y)
            last = ib
            podm.append({"imie": tok, "od": round(a, 3), "do": round(b, 3), "z_kwestii": spis[forma]["z_kwestii"],
                         "glosnosc": round(20 * np.log10(g), 1)})
        if not podm:
            continue
        out.append(x[last:])
        # sklejenie z przenikaniem XF na każdym styku
        wynik = out[0]
        for kaw in out[1:]:
            n = min(f, len(wynik), len(kaw))
            if n > 0:
                ramp = np.linspace(0, 1, n, dtype=np.float32)
                wynik = np.concatenate([wynik[:-n], wynik[-n:] * (1 - ramp) + kaw[:n] * ramp, kaw[n:]])
            else:
                wynik = np.concatenate([wynik, kaw])
        # brzegi kwestii: łagodne wejście i wybrzmienie (imię wklejone na sam początek albo koniec nie może zaczynać się
        # ani kończyć twardo — uciecia_lektora, zasada 9)
        db_k = poziomy(wynik, sr)
        if db_k[:6].max() > -50:   # imię na samym początku: 80 ms ciszy przed nim
            wynik = np.concatenate([np.zeros(int(0.08 * sr), np.float32), wynik])
        if db_k[-6:].max() > -50:  # imię na samym końcu: 250 ms ciszy po nim
            wynik = np.concatenate([wynik, np.zeros(int(0.25 * sr), np.float32)])
        n_in, n_out = int(0.02 * sr), int(0.06 * sr)
        wynik[:n_in] *= np.linspace(0, 1, n_in, dtype=np.float32)
        wynik[-n_out:] *= np.linspace(1, 0, n_out, dtype=np.float32) ** 2
        zapisz(LEKTOR / f"{k}.wav", wynik, sr)
        meta.update(duration=round(len(wynik) / sr, 3), imiona_autora=podm, przed_imionami=zrodlo.name)
        meta_p.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        print(f"{k:14s} podmienione: {', '.join(p['imie'] for p in podm)}")
    for r in raport:
        print("  " + r)


if __name__ == "__main__":
    if sys.argv[1] == "bank":
        bank()
    else:
        wstaw(set(sys.argv[2:]))
