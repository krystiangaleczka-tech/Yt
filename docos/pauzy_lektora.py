"""Pauzy lektora jak u człowieka — za każdym razem trochę inne (reżyser, 14.11.2026: „człowiek mówi różnie”).
Część przepisu na lektora teatru papierowego (Podręcznik pracowni → Lektor, zasada 8).

Każda pauza ma zakres od–do zależny od znaku, długości zdania i słowa przed nią; program losuje długość z zakresu
(ziarno losowania, więc wynik da się powtórzyć albo przelosować) i pilnuje, żeby dwie kolejne pauzy tego samego
rodzaju nie były prawie równe. Zakresy wzięte z bajki czytanej przez aktorkę (Pinokio, Audiobajki: mediana pauzy
0,58 s, 3/4 krótszych niż 0,8 s, prawie nigdy ponad 1,2 s) i z uwag reżysera:
  - po „całą” (zdanie 13 słów) 1,33 s za długo, po „zakładnik” (zdanie 21 słów) 0,85 s za krótko
    → pauza po zdaniu rośnie z jego długością,
  - przecinek po słowie zakończonym samogłoską — dłużej niż zwykle,
  - co drugie zdanie minimalnie dłużej,
  - po nazwie własnej oddech, nazwa zostaje w uchu (Podręcznik → Lektor, „Handan”).

Pauza = cisza między końcem jednego słowa a początkiem następnego. W nagraniu kwestii pauzy znajduje się w ciszy
(poniżej -40 dBFS) i przypisuje znakom przestankowym wg pozycji w tekście mówionym; z każdej starej pauzy zostaje
naturalne wybrzmienie (BRZEG) z obu stron, środek dostaje nową długość. Głos się nie zmienia.

Dwa użycia:
  - film: pauzy w środku jednej kwestii (lektor_studio.py podejscia --teatr woła plik()); pauzę po kwestii ustala
    montaż ujęć, nie ten program,
  - ciągły tekst (próba, bajka): kwestie sklejone w podanej kolejności, z pauzą po zdaniu między nimi:
      python -I docos/pauzy_lektora.py <katalog lektora> <wynik.wav> klucz [klucz …] [--ziarno N]
    Katalog lektora: <klucz>.wav + <klucz>.json z polem "spoken" (układ docos/lektor_studio.py). Obok wyniku
    <wynik>.json z listą pauz (gdzie, reguła, zakres, wylosowane, było).
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

# ── zakresy pauz (sekundy, od–do) ─────────────────────────────────────────────────────────────────────────────
PO_ZDANIU = [            # (zdanie ma najwyżej tyle słów, od, do)
    (8, 0.60, 0.80),     # krótkie
    (16, 0.70, 0.90),    # średnie
    (10 ** 6, 0.85, 1.05),  # długie
]
CO_DRUGIE_ZDANIE = 0.10  # co drugie zdanie minimalnie dłużej
PYTANIE = 0.10           # po „?” i „!”
MAKS_ZDANIE = 1.20       # dłuższej pauzy aktorka w bajce prawie nie robi

PRZECINEK = (0.30, 0.50)
PO_SAMOGLOSCE = 0.15     # przecinek po słowie zakończonym samogłoską
PO_NAZWIE = 0.10         # słowo przed znakiem to nazwa własna (wielka litera nie na początku zdania)
DLUGIE_SLOWO = 0.05      # słowo przed znakiem ma 4 sylaby i więcej
KROTKIE_SLOWO = -0.05    # słowo przed znakiem ma 1 sylabę
SREDNIK = (0.45, 0.65)   # ; i :
MYSLNIK = (0.40, 0.60)   # — i –
WIELOKROPEK = (0.80, 1.10)
BEZ_ZNAKU = (0.15, 0.25)  # lektor zrobił w środku frazy pauzę > BEZ_ZNAKU_PROG bez znaku w tekście → skrócić
BEZ_ZNAKU_PROG = 0.30

ROZNICA_MIN = 0.06       # dwie kolejne pauzy tego samego rodzaju różnią się co najmniej o tyle
BRZEG = 0.03             # tyle wybrzmienia zostaje z każdej strony starej pauzy
CISZA_DB, KANDYDAT_MIN = -40.0, 0.12   # pauza w nagraniu: co najmniej 0,12 s poniżej -40 dBFS
TOLERANCJA = 1.0         # pauza dalej niż tyle sekund od miejsca znaku (wg pozycji w tekście) nie jest jego pauzą

SAMOGLOSKI = "aąeęioóuy"


def sylaby(slowo):
    return max(1, len(re.findall(f"[{SAMOGLOSKI}]+", slowo.lower())))


def _db(y, sr):
    hop = int(sr * 0.01)
    return np.array([10 * np.log10(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y) - hop, hop)]), hop


def pauzy_w_nagraniu(y, sr):
    """→ (pauzy [(start, koniec) w próbkach], początek mowy, koniec mowy)."""
    db, hop = _db(y, sr)
    glos = np.where(db > CISZA_DB)[0]
    a, b = glos[0], glos[-1]
    out, n, st = [], 0, 0
    for i in range(a, b + 2):
        if i <= b and db[i] <= CISZA_DB:
            st, n = (i if n == 0 else st), n + 1
        else:
            if n * 0.01 >= KANDYDAT_MIN:
                out.append((st * hop, (st + n) * hop))
            n = 0
    return out, a * hop, (b + 1) * hop


def czysty(spoken):
    """Tekst mówiony bez znaczników aktorskich ([chuckle] itp.), żeby pozycje znaków odpowiadały mowie."""
    return re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", "", spoken)).strip()


def znaki(spoken):
    """Znaki w środku kwestii: (pozycja w tekście, znak, słowo przed, czy to nazwa własna, liczba słów zdania)."""
    zdania = [(m.start(), m.end(), len(re.findall(r"\w+", m.group()))) for m in re.finditer(r"[^.!?…]+[.!?…]*", spoken)]
    out = []
    for m in re.finditer(r"(\.\.\.|…|[,;:.!?—–])(?=\s*\w)", spoken):
        slowo = re.findall(r"\w+", spoken[:m.start()])[-1]
        zd = next((z for z in zdania if z[0] <= m.start() < z[1]), zdania[-1])
        poczatek_zdania = len(re.findall(r"\w+", spoken[zd[0]:m.start()])) == 1
        out.append((m.start(), m.group(1), slowo, slowo[0].isupper() and not poczatek_zdania, zd[2]))
    return out


class Losowanie:
    def __init__(self, ziarno):
        self.r = random.Random(ziarno)
        self.ostatnie = {}

    def __call__(self, rodzaj, od, do):
        x = self.r.uniform(od, do)
        for _ in range(30):
            if abs(x - self.ostatnie.get(rodzaj, -9)) >= ROZNICA_MIN or do - od < 2 * ROZNICA_MIN:
                break
            x = self.r.uniform(od, do)
        self.ostatnie[rodzaj] = x
        return round(x, 3)


def zakres_zdania(slow, nr_zdania, znak):
    od, do = next((o, d) for maks, o, d in PO_ZDANIU if slow <= maks)
    dod, regula = 0.0, [f"zdanie {slow} słów"]
    if nr_zdania % 2 == 0:
        dod += CO_DRUGIE_ZDANIE
        regula.append("co drugie zdanie")
    if znak in "?!":
        dod += PYTANIE
        regula.append(f"po „{znak}”")
    return min(od + dod, MAKS_ZDANIE), min(do + dod, MAKS_ZDANIE), regula


def zakres_znaku(znak, slowo, nazwa):
    if znak in ("...", "…"):
        return (*WIELOKROPEK, ["wielokropek"])
    if znak in ";:":
        od, do = SREDNIK
        regula = ["średnik/dwukropek"]
    elif znak in "—–":
        od, do = MYSLNIK
        regula = ["myślnik"]
    else:
        od, do = PRZECINEK
        regula = ["przecinek"]
    dod = 0.0
    if znak == "," and slowo[-1].lower() in SAMOGLOSKI:
        dod += PO_SAMOGLOSCE
        regula.append("po samogłosce")
    if nazwa:
        dod += PO_NAZWIE
        regula.append("po nazwie")
    syl = sylaby(slowo)
    if syl >= 4:
        dod += DLUGIE_SLOWO
        regula.append(f"długie słowo ({syl} syl.)")
    elif syl == 1:
        dod += KROTKIE_SLOWO
        regula.append("krótkie słowo (1 syl.)")
    return od + dod, do + dod, regula


def przypisz(zn, kandydaci, a, b, sr, dl_tekstu):
    """Znak → pauza w nagraniu (indeks) wg pozycji w tekście, po kolei; dłuższa pauza wygrywa z bliższą krótką."""
    wynik, od = [], 0
    for poz, *_ in zn:
        t = a + (b - a) * poz / dl_tekstu
        best, koszt = None, None
        for i in range(od, len(kandydaci)):
            s, e = kandydaci[i]
            odl = abs((s + e) / 2 - t) / sr
            if odl > TOLERANCJA:
                continue
            k = odl - 0.6 * (e - s) / sr
            if koszt is None or k < koszt:
                best, koszt = i, k
        wynik.append(best)
        if best is not None:
            od = best + 1
    return wynik


def ustaw_pauze(y, s, e, cel, sr):
    """Pauza y[s:e] → długość cel: wybrzmienie z brzegów zostaje, środek to cisza."""
    br = int(BRZEG * sr)
    if e - s <= 2 * br:
        br = (e - s) // 2
    srodek = max(0, int(cel * sr) - 2 * br)
    return np.concatenate([y[s:s + br], np.zeros(srodek, dtype=np.float32), y[e - br:e]])


def kwestia(y, sr, spoken, los, nr_zdania=0, klucz=""):
    """Pauzy w środku jednej kwestii.
    → (nagranie od mowy do mowy z wybrzmieniem na brzegach, wybrzmienie z przodu, z tyłu [próbki], raport, nr_zdania)."""
    spoken = czysty(spoken)
    kand, a, b = pauzy_w_nagraniu(y, sr)
    zn = znaki(spoken)
    przyp = przypisz(zn, kand, a, b, sr, len(spoken))
    zmiany, raport = {}, []   # indeks kandydata → cel
    for (poz, znak, slowo, nazwa, slow), ip in zip(zn, przyp):
        if znak in ".!?":
            nr_zdania += 1
            od, do, regula = zakres_zdania(slow, nr_zdania, znak)
            rodzaj = "zdanie"
        else:
            od, do, regula = zakres_znaku(znak, slowo, nazwa)
            rodzaj = "znak"
        cel = los(rodzaj, od, do)
        bylo = None if ip is None else round((kand[ip][1] - kand[ip][0]) / sr, 2)
        raport.append({"kwestia": klucz, "gdzie": f"{slowo}{znak}", "regula": ", ".join(regula),
                       "od": round(od, 2), "do": round(do, 2), "wylosowane": cel, "bylo": bylo})
        if ip is None:
            raport[-1]["uwaga"] = "brak pauzy w nagraniu — zostaje bez pauzy"
        else:
            zmiany[ip] = cel
    for i, (s, e) in enumerate(kand):   # długie pauzy bez znaku w tekście
        if i not in zmiany and (e - s) / sr > BEZ_ZNAKU_PROG:
            cel = los("bez_znaku", *BEZ_ZNAKU)
            zmiany[i] = cel
            raport.append({"kwestia": klucz, "gdzie": f"{s / sr:.2f} s (bez znaku w tekście)", "regula": "bez znaku",
                           "od": BEZ_ZNAKU[0], "do": BEZ_ZNAKU[1], "wylosowane": cel, "bylo": round((e - s) / sr, 2)})
    br = int(BRZEG * sr)
    pocz, kon = max(0, a - br), min(len(y), b + br)
    out, last = [], pocz
    for i in sorted(zmiany):
        s, e = kand[i]
        out += [y[last:s], ustaw_pauze(y, s, e, zmiany[i], sr)]
        last = e
    out.append(y[last:kon])
    return np.concatenate(out), a - pocz, kon - b, raport, nr_zdania


def ziarno_kwestii(klucz):
    """Stałe ziarno z klucza kwestii: to samo nagranie dostaje przy każdym przebiegu te same pauzy."""
    return int(hashlib.sha256(klucz.encode("utf-8")).hexdigest()[:8], 16)


def plik(src, dst, spoken, ziarno):
    """Film: pauzy w środku jednej kwestii, src → dst (brzegi: tylko wybrzmienie, bez ciszy). → raport."""
    y, sr = sf.read(str(src), dtype="float32")
    nagr, _, _, raport, _ = kwestia(y, sr, spoken, Losowanie(ziarno), klucz=Path(dst).stem)
    sf.write(str(dst), nagr, sr, subtype="PCM_16")
    return raport


def wypisz(raport):
    for p in raport:
        bylo = f"{p['bylo']:.2f}" if p["bylo"] is not None else "  — "
        print(f"{p['gdzie']:<34} {bylo} → {p['wylosowane']:.2f} s   [{p['od']:.2f}–{p['do']:.2f}] {p['regula']}"
              + (f"  ({p['uwaga']})" if p.get("uwaga") else ""))


def uloz(katalog, dst, klucze, ziarno=1):
    """Ciągły tekst: kwestie sklejone w podanej kolejności, między nimi pauza po zdaniu."""
    katalog, dst = Path(katalog), Path(dst)
    los, raport, sr, czesci, nr_zdania = Losowanie(ziarno), [], None, [], 0
    for nk, k in enumerate(klucze):
        y, s_ = sf.read(str(katalog / f"{k}.wav"), dtype="float32")
        sr = sr or s_
        assert s_ == sr, f"{k}: {s_} Hz zamiast {sr} Hz"
        spoken = czysty(json.loads((katalog / f"{k}.json").read_text(encoding="utf-8"))["spoken"])
        nagr, przod, tyl, r, nr_zdania = kwestia(y, sr, spoken, los, nr_zdania, k)
        raport += r
        pauza = 0
        if nk < len(klucze) - 1:   # koniec kwestii = koniec zdania
            nr_zdania += 1
            slow = len(re.findall(r"\w+", re.findall(r"[^.!?…]+[.!?…]*", spoken)[-1]))
            znak = (re.findall(r"[.!?…]", spoken) or ["."])[-1]
            od, do, regula = zakres_zdania(slow, nr_zdania, znak)
            cel = los("zdanie", od, do)
            ostatnie_slowo = re.findall(r"\w+", spoken)[-1]
            raport.append({"kwestia": k, "gdzie": f"{ostatnie_slowo}{znak} (koniec kwestii)",
                           "regula": ", ".join(regula), "od": round(od, 2), "do": round(do, 2), "wylosowane": cel,
                           "bylo": None})
            pauza = int(cel * sr)
        czesci.append((nagr, przod, tyl, pauza))
    # między kwestiami: cisza tyle, żeby razem z wybrzmieniem na końcu i przed początkiem następnej dała pauzę
    sklejone = []
    for i, (nagr, _, tyl, pauza) in enumerate(czesci):
        sklejone.append(nagr)
        if i < len(czesci) - 1:
            sklejone.append(np.zeros(max(0, pauza - tyl - czesci[i + 1][1]), dtype=np.float32))
    cisza = np.zeros(int(0.3 * sr), dtype=np.float32)
    wynik = np.concatenate([cisza] + sklejone + [cisza])
    sf.write(str(dst), wynik, sr, subtype="PCM_16")
    dst.with_suffix(".json").write_text(json.dumps({"ziarno": ziarno, "klucze": klucze, "pauzy": raport},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    wypisz(raport)
    print(f"{dst}: {len(wynik) / sr:.1f} s, ziarno {ziarno}")


if __name__ == "__main__":
    args = sys.argv[1:]
    ziarno = 1
    if "--ziarno" in args:
        i = args.index("--ziarno")
        ziarno = int(args[i + 1])
        del args[i:i + 2]
    if len(args) < 3:
        sys.exit(__doc__)
    uloz(args[0], args[1], args[2:], ziarno)
