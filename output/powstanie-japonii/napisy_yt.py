"""Napisy do YouTube (SRT, angielskie i polskie) do wersji EN „Son of the Sun” — z czasów prawdziwego lektora w filmie.

  python3 output/powstanie-japonii/napisy_yt.py   → output/powstanie-japonii/napisy_yt/Son_of_the_Sun_en.srt i _pl.srt

Kwestia zaczyna się w filmie tam, gdzie zloz.py kładzie nagranie (start ujęcia + oddech z dane.okno_kwestii), a jej
napis trwa od pierwszego do ostatniego dźwięku nagrania lektor_en/<klucz>.wav (+0,4 s, nie dłużej niż do następnego
napisu). Długie kwestie dzielą się na napisy po najwyżej dwa wiersze po 42 znaki (zalecenie YouTube); granice między
nimi trafiają w pauzy lektora (cisza w nagraniu), a gdy pauzy nie ma w pobliżu — w miejsce wynikające z liczby znaków.

Polskie napisy to polskie kwestie z rozpiski (dane.py), które były źródłem angielskich; NAPISY_PL podmienia te, które
po polsku czytał lektor z liczbami słownie albo którym w napisie brakowałoby podmiotu. Reżyser 21.11.2026: „daj napisy
en i pl do youtube”.
"""
import json
import os
import re
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
UJ = HERE.parents[1] / "docs/filmy/powstanie-japonii/ujecia"
sys.path.insert(0, str(UJ))
OUT = HERE / "napisy_yt"
LEKTOR = HERE / "lektor_en"
WIERSZ, NAPIS = 42, 84  # znaków w wierszu, w całym napisie (dwa wiersze)
PO_GLOSIE = {"en": 0.4, "pl": 1.2}  # napis zostaje chwilę po ostatnim słowie (polski jest dłuższy: czyta się go dłużej)

NAPISY_PL = {
    "wschod": "Kiedy miał 45 lat, usłyszał, że na wschodzie leży piękna kraina otoczona niebieskimi górami.",
    "bitwa": "Iwarebiko jeszcze raz walczył z Nagasunehiko, ale bitwa długo nie mogła się rozstrzygnąć, a niebo pociemniało "
             "i spadł grad.",
    "palac": "W Kashiharze, u stóp zielonej góry, Iwarebiko kazał zbudować pałac, którego słupy, jak pisze kronika, wbito "
             "w samą skałę.",
    "tron": "Pierwszego dnia nowego roku, w 660 roku p.n.e., wstąpił tam na tron jako pierwszy cesarz Japonii.",
    "imie": "Imię Jimmu, czyli „boska waleczność”, nadali mu uczeni dopiero 1400 lat później.",
    "smierc": "Według kroniki zmarł, mając 127 lat, a trzy skarby przeszły na jego syna.",
    "rachunek": "Datę 660 roku p.n.e. najpewniej wyliczono z chińskiej wróżby, według której co 1260 lat przychodzi "
                "wielka przemiana.",
    "jomon": "Tymczasem w 660 roku p.n.e. na wyspach żyli myśliwi i rybacy, a ryż dopiero zaczynano uprawiać "
             "na południowym zachodzie.",
    "luty2": "Dopiero w 1873 roku rząd w Tokio przeliczył datę z kroniki na nasz kalendarz i ogłosił 11 lutego świętem, "
             "które po wojnie zniesiono, a w 1966 roku przywrócono.",
    "koronacja": "W 2019 roku na tron wstąpił 126. cesarz i przyniesiono mu klejnoty oraz zastępczy miecz z ogona węża, "
                 "wciąż owinięte płótnem, którego nikt nie odwija.",
}


def czytaj_wav(p):
    with wave.open(str(p)) as f:
        sr, n, ch, sw = f.getframerate(), f.getnframes(), f.getnchannels(), f.getsampwidth()
        a = np.frombuffer(f.readframes(n), {2: np.int16, 4: np.int32}[sw]).astype(np.float32)
    return a.reshape(-1, ch).mean(axis=1), sr


def glos(p):
    """(pierwszy dźwięk, ostatni dźwięk, [środki pauz]) w sekundach nagrania — ramki 20 ms, cisza 35 dB pod szczytem."""
    a, sr = czytaj_wav(p)
    hop = int(sr * 0.02)
    n = len(a) // hop
    rms = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms / rms.max())
    gl = db > -35
    idx = np.flatnonzero(gl)
    t0, t1 = idx[0] * 0.02, (idx[-1] + 1) * 0.02
    pauzy, bieg = [], None
    for i in range(idx[0], idx[-1] + 1):
        if not gl[i] and bieg is None:
            bieg = i
        elif gl[i] and bieg is not None:
            if (i - bieg) * 0.02 >= 0.14:
                pauzy.append((bieg + i) / 2 * 0.02)
            bieg = None
    return t0, t1, pauzy


def zdania(txt):
    """Zdania (po kropce, pytajniku, wykrzykniku); zdanie krótsze niż 30 znaków dołącza do poprzedniego."""
    out = []
    for z in re.split(r"(?<=[.?!])(?<!p\.n\.e\.)(?<!\d\.)\s+", txt.strip()):  # „660 roku p.n.e.”, „126. cesarz” to nie koniec zdania
        if out and (len(z) < 30 or len(out[-1]) < 30) and len(out[-1]) + 1 + len(z) <= NAPIS:
            out[-1] += " " + z
        else:
            out.append(z)
    return out


def rowno(zd):
    return rowno_n(zd, -(-len(zd) // NAPIS))


def rowno_n(zd, n):
    """Zdanie na najmniej napisów po najwyżej NAPIS znaków, możliwie równych; cięcie najchętniej po przecinku,
    dwukropku albo średniku, a nigdy przed jednym-dwoma ostatnimi słowami."""
    slowa = zd.split()
    if n == 1 and miesci(zd):
        return [zd]
    cel = len(zd) / n
    m = len(slowa)
    dl = lambda i, j: len(" ".join(slowa[i:j]))
    best = {(0, 0): (0.0, [])}  # (słów zużytych, napisów) → (koszt, granice)
    for k in range(n):
        for (i, kk), (koszt, gr) in list(best.items()):
            if kk != k:
                continue
            for j in range(i + 1, m + 1):
                L = dl(i, j)
                if L > NAPIS:
                    break
                if not miesci(" ".join(slowa[i:j])):
                    continue
                ostatni = k == n - 1
                if ostatni != (j == m):
                    continue
                kara = ((L - cel) / 10) ** 2
                if not ostatni:
                    kara += koszt_ciecia(slowa[j - 1], slowa[j]) * 3
                    kara += 40 if m - j <= 2 else 0
                c = (koszt + kara, gr + [j])
                if (j, k + 1) not in best or c[0] < best[(j, k + 1)][0]:
                    best[(j, k + 1)] = c
    if (m, n) not in best:  # nie da się na n napisów po dwa wiersze: o jeden więcej
        return rowno_n(zd, n + 1)
    _, gr = best[(m, n)]
    return [" ".join(slowa[a:b]) for a, b in zip([0] + gr[:-1], gr)]


def podziel(txt):
    """Napisy po najwyżej NAPIS znaków: zdanie po zdaniu, długie zdanie na równe kawałki (rowno)."""
    return [c for zd in zdania(txt) for c in rowno(zd)]


# słowa, przed którymi dobrze zaczyna się nowy wiersz (spójniki, zaimki względne), i takie, po których nie wolno
# łamać (przedimki, przyimki, spójniki na końcu wiersza)
PRZED = set("and but so which who whose when where while because that as until though or nor "
            "i a ale bo więc który która które którego której którzy kiedy gdzie aż żeby że czyli choć gdy".split())
NIE_PO = set("the a an of to in on at by for from with into his her its their and so that "
             "w we z ze i a na do o od po za u przy dla przez pod nad bez jak jego jej się".split())


def koszt_ciecia(przed, po):
    """Kara za złamanie wiersza albo napisu między słowami przed | po (0 — po przecinku, kropce, dwukropku)."""
    if re.fullmatch(r"\d+\.?", przed) or przed.lower() in ("hundred", "thousand"):  # „127 | lat”, „126. | cesarz”
        return 12
    if przed[-1] in ",.;:?!":
        return 0
    if przed.lower() in NIE_PO:
        return 12
    return 2 if po.lower().strip("„'") in PRZED else 5


def _ciecia(txt):
    """Spacje, po których oba wiersze mają najwyżej WIERSZ znaków."""
    return [m.start() for m in re.finditer(" ", txt) if m.start() <= WIERSZ and len(txt) - m.start() - 1 <= WIERSZ]


def miesci(txt):
    return len(txt) <= WIERSZ or bool(_ciecia(txt))


def wiersze(txt):
    """Dwa wiersze po najwyżej WIERSZ znaków, możliwie równe; najchętniej po przecinku."""
    if len(txt) <= WIERSZ:
        return txt
    i = min(_ciecia(txt), key=lambda s: abs(s - len(txt) / 2) / 3 + 2 * koszt_ciecia(txt[:s].split()[-1], txt[s + 1:].split()[0]))
    return txt[:i] + "\n" + txt[i + 1:]


def tc(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def kwestie(jezyk):
    """[(start w filmie, koniec, tekst, klucz)] — jeden wpis na kwestię lektora."""
    os.environ["JEZYK"] = "en"
    import dane
    out, t = [], 0.0
    for u in dane.ujecia():
        klucz, sec, snd = u[2], u[5], u[7]
        en = dane.kwestia(snd)
        if en:
            meta = json.loads((LEKTOR / f"{klucz}.json").read_text(encoding="utf-8"))
            assert meta["text"] == en, f"{klucz}: nagranie z innym tekstem"
            start = t + dane.okno_kwestii(snd)[0]
            g0, g1, pauzy = glos(LEKTOR / f"{klucz}.wav")
            txt = en if jezyk == "en" else NAPISY_PL.get(klucz, snd[2:].strip())
            out.append((start + g0, start + g1, txt, [start + p for p in pauzy]))
        t += sec
    return out


def srt(jezyk):
    wpisy = []
    for a, b, txt, pauzy in kwestie(jezyk):
        czesci = podziel(txt)
        dl = sum(len(c) for c in czesci)
        granice, acc = [a], 0
        for c in czesci[:-1]:
            acc += len(c)
            cel = a + (b - a) * acc / dl
            blisko = [p for p in pauzy if abs(p - cel) < 0.9 and p > granice[-1] + 0.6]
            granice.append(min(blisko, key=lambda p: abs(p - cel)) if blisko else cel)
        granice.append(b)
        for n, c in enumerate(czesci):
            wpisy.append([granice[n], granice[n + 1], c])
    for n, w in enumerate(wpisy):  # chwila po ostatnim słowie, ale bez nachodzenia na następny napis
        nast = wpisy[n + 1][0] if n + 1 < len(wpisy) else w[1] + 2
        if n + 1 == len(wpisy) or wpisy[n + 1][0] - w[1] > 0.3:
            w[1] = min(w[1] + PO_GLOSIE[jezyk], nast - 0.05)
        else:
            w[1] = nast - 0.02 if nast - w[1] < 0.5 else w[1]
    return "".join(f"{n + 1}\n{tc(a)} --> {tc(b)}\n{wiersze(txt)}\n\n" for n, (a, b, txt) in enumerate(wpisy)), wpisy


def main():
    OUT.mkdir(exist_ok=True)
    for jez in ("en", "pl"):
        tekst, wpisy = srt(jez)
        p = OUT / f"Son_of_the_Sun_{jez}.srt"
        p.write_text(tekst, encoding="utf-8")
        dlugie = [w[2] for w in wpisy if len(w[2]) > NAPIS]
        krotkie = [w for w in wpisy if w[1] - w[0] < 1.0]
        print(f"{p.name}: {len(wpisy)} napisów, ostatni do {tc(wpisy[-1][1])}; za długie: {len(dlugie)}, krótsze niż 1 s: "
              f"{len(krotkie)}")


if __name__ == "__main__":
    main()
