"""Oddechy we frazie bez nagrywania od nowa: w kwestiach klonu, które klon powiedział jednym ciągiem, wstawia krótką
ciszę (0,38–0,46 s) w miejscach przecinków frazowania (kwestie_en.FRAZY_EN) — w najcichszym miejscu między słowami
w pobliżu szacowanego czasu przecinka. Słów nie rusza. Gdzie nie ma pewnej przerwy między słowami (dołek energii
co najmniej 30 ms poniżej progu), nie wstawia nic, żeby nie przeciąć słowa (reżyser 16.11: kwestia 2 — „za długo na
początku, potem przyspiesza, tam bym dał wydłużenie”).

uruchom:  pilot/.venv-enhance/bin/python -I output/pierwszy-cesarz/oddechy.py <katalog lektora> [klucz …]
Raport: <katalog>/oddechy.json (gdzie wstawiono, gdzie pominięto i dlaczego).
"""
import json
import random
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/pierwszy-cesarz/ujecia"))
from kwestie_en import EN, FRAZY_EN  # noqa: E402

CISZA_DB = -40.0     # pauza istniejąca: co najmniej 0,12 s poniżej -40 dBFS
DOLEK_DB = -47.0     # przerwa między słowami: dołek poniżej tego …
DOLEK_MIN = 0.03     # … przez co najmniej 30 ms
SZUKAJ = 0.35        # tyle sekund wokół szacowanego miejsca przecinka
ODDECH = (0.38, 0.46)
OD_PAUZY = 0.45      # nie wstawiaj bliżej istniejącej pauzy ani brzegu kwestii niż tyle


def sylaby(w):
    return max(1, len(re.findall(r"[aeiouy]+", w.lower())))


def nowe_przecinki(klucz):
    """Pozycje (ułamek sylab od początku) przecinków, które są w FRAZY_EN, a nie ma ich w zwykłym tekście."""
    stare = EN[klucz].replace(",", " , ").split()
    nowe = FRAZY_EN[klucz].replace(",", " , ").split()
    slowa = [w for w in nowe if w != ","]
    syl = np.cumsum([sylaby(w) for w in slowa])
    total = syl[-1]
    out, i, j, k = [], 0, 0, 0  # i — w nowe, j — w stare, k — słów przed przecinkiem
    while i < len(nowe):
        if nowe[i] == ",":
            if j < len(stare) and stare[j] == ",":
                j += 1
            elif k > 0:
                out.append(syl[k - 1] / total)
        else:
            k += 1
            while j < len(stare) and stare[j] == ",":
                j += 1
            j += 1
        i += 1
    return out


def dzwiek(y, sr, hop):
    return np.array([10 * np.log10(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y) - hop, hop)])


def obrob(plik, klucz, rng):
    y, sr = sf.read(plik, dtype="float32")
    hop = int(sr * 0.005)
    dt = hop / sr
    db = dzwiek(y, sr, hop)
    glos = np.where(db > CISZA_DB)[0]
    a, b = glos[0], glos[-1]
    cisza = db <= CISZA_DB
    pauzy, n = [], 0  # istniejące pauzy (początek, koniec) w ramkach
    for i in range(a, b + 2):
        if i <= b and cisza[i]:
            n += 1
        else:
            if n * dt >= 0.12:
                pauzy.append((i - n, i))
            n = 0
    # oś „samej mowy”: czas bez pauz, żeby pozycja w tekście (sylaby) przełożyła się na czas
    mowa = np.ones(b - a + 1, bool)
    for p0, p1 in pauzy:
        mowa[p0 - a:p1 - a] = False
    cum = np.cumsum(mowa)
    raport, wstaw = [], []
    for frac in nowe_przecinki(klucz):
        cel = frac * cum[-1]
        t_est = a + int(np.searchsorted(cum, cel))
        if any(abs(t_est - p0) * dt < OD_PAUZY or abs(t_est - p1) * dt < OD_PAUZY for p0, p1 in pauzy) or \
                (t_est - a) * dt < OD_PAUZY or (b - t_est) * dt < OD_PAUZY:
            raport.append({"czas": round(t_est * dt, 2), "wynik": "pominięty: blisko pauzy albo brzegu kwestii"})
            continue
        r = int(SZUKAJ / dt)
        okno = db[t_est - r:t_est + r]
        sm = np.convolve(okno, np.ones(int(DOLEK_MIN / dt)) / int(DOLEK_MIN / dt), mode="same")  # średnia z 30 ms
        k = int(np.argmin(sm))
        if sm[k] > DOLEK_DB:
            raport.append({"czas": round(t_est * dt, 2), "wynik": f"pominięty: brak przerwy między słowami (najciszej {sm[k]:.0f} dB)"})
            continue
        gdzie = t_est - r + k
        d = round(rng.uniform(*ODDECH), 2)
        wstaw.append((gdzie * hop + hop // 2, d))
        raport.append({"czas": round(gdzie * dt, 2), "wynik": f"oddech {d} s", "dolek_db": round(float(sm[k]), 1)})
    wstaw.sort()
    wstaw = [w for i, w in enumerate(wstaw) if i == 0 or (w[0] - wstaw[i - 1][0]) / sr >= 0.3]  # dwa przecinki w jednym miejscu: raz
    if wstaw:
        f = int(0.008 * sr)
        part, prev = [], 0
        for p, d in wstaw:
            seg = y[prev:p].copy()
            seg[-f:] *= np.linspace(1, 0, f)
            part += [seg, np.zeros(int(d * sr), np.float32)]
            y = np.concatenate([y[:p], y[p:p + f] * np.linspace(0, 1, f), y[p + f:]])
            prev = p
        part.append(y[prev:])
        y = np.concatenate(part)
        sf.write(plik, y, sr, subtype="PCM_16")
    return len(y) / sr, raport, len(wstaw)


def main(katalog, klucze=None):
    katalog = Path(katalog)
    wynik, razem = {}, 0
    for js in sorted(katalog.glob("*.json")):
        klucz = js.stem
        if klucz in ("oddechy",) or klucz not in FRAZY_EN or (klucze and klucz not in klucze):
            continue
        rng = random.Random(sum(map(ord, klucz)))
        dl, rap, n = obrob(katalog / f"{klucz}.wav", klucz, rng)
        meta = json.loads(js.read_text(encoding="utf-8"))
        meta["duration"] = round(dl, 3)
        meta["oddechy"] = rap
        js.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        wynik[klucz] = rap
        razem += n
        print(f"{klucz:10s} {dl:5.2f} s  wstawione {n}, pominięte {len(rap) - n}", flush=True)
    (katalog / "oddechy.json").write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"razem wstawionych oddechów: {razem}")


if __name__ == "__main__":
    main(sys.argv[1], set(sys.argv[2:]) or None)
