"""Szkice ujęć A, B, C filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (etap Studio „Szkice ujęć”).

  python3 -I docs/filmy/szamil-diuna/szkice/buduj_szkice.py [a b c]   — zapisuje <wariant>/szkic.json do importu w Studio

Wspólna pula ujęć to rozpiska (../ujecia/dane.py); warianty różnią się hakiem i kolejnością, reszta ujęć jest ta sama:
- A · Dwa zdania — hak: zdanie z Diuny i niemal to samo zdanie z książki z 1960; chronologia; słowa na końcu (rozmowa 27.11).
- B · Wymiana na rzece — hak: imam odzyskuje syna za porwane księżne, srebro i jeńców (1855); zdania o ostrzu przechodzą do aktu IV.
- C · Słowa najpierw — hak: słowa, które zna każdy fan Diuny (kanly, kindjal, sietch, padishah), nie zostały wymyślone;
  na końcu dwa zdania jako dowód.
- D · A + trop słów + rzeka (28.11, wybór reżysera „1” po porównaniu A z podejściami „Trop słów” i „Syn między dwoma
  światami”): słowo z Diuny na początku każdego aktu, „siridar” przy kapitulacji, wolniejsza wymiana na rzece.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ujecia"))
from dane import PAUZA_PO, TEMPO_EN, kwestia, okno_kwestii, slownie, ujecia  # noqa: E402

KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta"}
POOL = {u[2]: u for u in ujecia()}
ZAP = [k for k in POOL if k.startswith("zap_")]
ZNACZNIK = {"tytul": "KURTYNA STARTU", "pytanie": "HOOK 1 · pytanie", "koniec_aktu1": "HOOK 2 · pytanie aktu",
            "tsinandali": "pogorszenie", "przeprawa_syn": "promyk nadziei", "swieca": "cios", "kapitulacja": "KULMINACJA",
            "przyslowie": "dowód", "biala_flaga": "PUENTA", "slowo_kindjal": "słowo z Diuny", "uscisk": "SZCZYT EMOCJI"}


def ujecie(klucz, kadr, sek, opis, kw=""):
    """Nowe ujęcie haka (skrót istniejącego ujęcia z innym słowem lektora)."""
    if sek is None:
        sek = round(0.4 + len(slownie(kw).split()) / TEMPO_EN + 1.0, 1)
    return (None, None, klucz, kadr, "naj", sek, opis, "L: " + kw if kw else "")


def akt(n):
    return [k for k in POOL if POOL[k][0] == n]


def linia(klucz, kadr, ruch, opis, kw, pauza="ujecie"):
    """Nowe ujęcie z kwestią spoza haka: oddech + tempo lektora + pauza po kwestii (zasady z dane.py)."""
    start, mowa = okno_kwestii("L: " + kw)
    return (None, None, klucz, kadr, ruch, round(start + mowa + PAUZA_PO[pauza], 1), opis, "L: " + kw)


def wariant_d(rows):
    """A + słowa z Diuny na początku aktów (podejście „Trop słów”) + wolniejsza wymiana na rzece (podejście „Syn”)."""
    zmiana = {
        "koniec_aktu1": dict(opis=("„Act II · How do you buy back a son?”", "mała tabliczka „Act II · KANLY”, pod nią pytanie "
                                   "„How do you buy back a son?” (słowo KANLY zjeżdża na nitce na kurtynę)")),
        "samotny": dict(opis=("„Act III · How does a 25-year war end?”", "mała tabliczka „Act III · SIRIDAR”, pod nią pytanie "
                              "„How does a 25-year war end?”")),
        "medyna": dict(opis=("„Act IV · What did Dune take?”", "mała tabliczka „Act IV · SIETCH”, pod nią pytanie "
                             "„What did Dune take?”")),
        "kapitulacja": dict(kw="That September, the sixty-two-year-old imam came down and surrendered to Prince Baryatinsky, "
                               "the Tsar's viceroy. Shamil's word for such a man was siridar.",
                            opis=("podpis „Prince Baryatinsky”", "podpis „Prince Baryatinsky”, a na „siridar” nad księciem "
                                  "zjeżdża tabliczka SIRIDAR (zasiew puenty z aktu IV)")),
        "tytuly": dict(kw="Even padishah, Shamil's word for the Tsar, and siridar, his word for the man who took his "
                          "surrender, ended up in Herbert's empire.",
                       opis=("nad gubernatorem SIRIDAR", "nad księciem Bariatinskim (ta sama lalka co przy kapitulacji) "
                             "SIRIDAR")),
        "uscisk": dict(sek=3.6, opis=("Szamil obejmuje syna; muzyka — motyw ojca", "Muzyka milknie, zostaje szum rzeki; Szamil "
                                      "obejmuje syna, kamera bardzo wolno dojeżdża; na końcu uścisku wraca motyw ojca "
                                      "(emocjonalny szczyt filmu, Wytyczne 1.23)")),
    }
    wstaw = {
        "pytanie": [("slowo_kindjal", "D", "stat", 1.8, "Nad górami na nitce zjeżdża słowo KINDJAL, obraca się i zmienia w "
                     "kindżał, który wsuwa się za pas lalki Szamila na grani (słowo z Diuny otwiera akt I)", "szelest, szczęk")],
        "przeprawa_syn": [("syn_brzeg", "Z", "naj", 2.4, "Zbliżenie: młody oficer zatrzymuje konia na środku brodu i patrzy na "
                           "góry, z których wyjechał jako dziecko; waha się", "rzeka")],
        "mundur": [linia("ojciec_brzeg", "Z", "naj", "Zbliżenie: Szamil na drugim brzegu; dłoń puszcza rękojeść kindżału",
                         "Father and son had not seen each other for almost sixteen years.")],
    }
    out = []
    for row in rows:
        _, _, klucz, kadr, ruch, sek, opis, dz = row
        z = zmiana.get(klucz, {})
        if "opis" in z:
            assert z["opis"][0] in opis, (klucz, z["opis"][0])
            opis = opis.replace(*z["opis"])
        if "kw" in z:
            start, mowa = okno_kwestii("L: " + z["kw"])
            sek, dz = round(sek - sum(okno_kwestii(dz)) + start + mowa, 1), "L: " + z["kw"]
        sek = z.get("sek", sek)
        out.append((None, None, klucz, kadr, ruch, sek, opis, dz))
        out += [w if len(w) == 8 else (None, None, *w) for w in wstaw.get(klucz, [])]
    for i in range(1, len(out)):  # sąsiednie ujęcia różnią się co najmniej o ¼ s (Rytm 2)
        if abs(out[i][5] - out[i - 1][5]) < 0.25:
            out[i] = (*out[i][:5], round(out[i - 1][5] + 0.3, 1), *out[i][6:])
    return out


def warianty():
    pro = akt(0)
    a1, a2, a3, a4 = akt(1), akt(2), akt(3), akt(4)
    zdania = ["cytat_diuna", "kindzal", "cytat_1960", "ramka", "ksiazka"]
    A = [POOL[k] for k in pro + a1 + a2 + a3 + a4]
    hak_b = [ujecie("hak_rzeka", "PO", None, "skrót ujęcia „rzeka”: dwa oddziały na brzegach zamarzającej rzeki, wóz z księżnymi "
                    "jedzie w jedną stronę, młody oficer w drugą", "In 1855, on a river in the Caucasus, an imam got his son back. "
                    "The price was two kidnapped princesses, silver and prisoners."),
             ujecie("hak_mundur", "PŚ", None, "skrót ujęcia „mundur”: syn wychodzi z wody w rosyjskim mundurze",
                    "The son came back wearing the uniform of his father's enemy."),
             ujecie("hak_pytanie", "PO", None, "wydma zapada się w scenę, wyrastają góry; zawieszka „Dagestan, 1834”",
                    "A century later, their war ended up inside Dune. So how did it get there?")]
    B = ([POOL[k] for k in ZAP + ["tytul", "przedstawienie"]] + hak_b + [POOL[k] for k in a1 + a2 + a3]
         + [POOL[k] for k in a4[:2] + zdania[:4] + a4[2:]])
    hak_c = [ujecie("hak_slowa", "D", None, "na nitkach zjeżdżają po kolei słowa KANLY, KINDJAL, SIETCH, PADISHAH",
                    "Kanly. Kindjal. Sietch. Padishah. Every Dune fan knows these words."),
             ujecie("hak_gory", "PO", None, "słowa odjeżdżają nad góry Kaukazu; z grani patrzy lalka Szamila",
                    "But Frank Herbert did not invent them. They come from a real war in the Caucasus."),
             ujecie("hak_pytanie", "PO", None, "wydma zapada się w scenę, wyrastają góry; zawieszka „Dagestan, 1834”",
                    "So whose war was it?")]
    slowa = ["kanly", "kindjal", "chakobsa", "sietch", "tytuly"]
    C = ([POOL[k] for k in ZAP + ["tytul", "przedstawienie"]] + hak_c + [POOL[k] for k in a1 + a2 + a3]
         + [POOL[k] for k in ["blanch", "herbert"] + slowa[2:3] + slowa[4:] + zdania[:4] + a4[-5:]])
    return {
        "d": ("D · Dwa zdania, trop słów i rzeka", "Wariant A z trzema zmianami z porównania podejść (28.11, reżyser: „1”): "
              "(1) z podejścia „Trop słów” — każdy akt otwiera słowo z Diuny: KINDJAL zjeżdża nad góry na początku aktu I, "
              "KANLY, SIRIDAR i SIETCH stoją na kurtynach aktów II–IV nad pytaniem, więc Diuna jest w filmie co ok. minutę, a nie "
              "tylko na początku i na końcu; (2) „siridar” przy kapitulacji: Szamil poddaje się carskiemu namiestnikowi, a jego "
              "słowo na ten urząd trafiło do Diuny — w akcie IV wraca jako puenta listy słów; (3) z podejścia „Syn między dwoma "
              "światami” — wymiana na rzece jest emocjonalnym szczytem: zbliżenia syna i ojca na dwóch brzegach, „almost sixteen "
              "years”, muzyka milknie przed uściskiem, długie trzymanie.", wariant_d(A)),
        "a": ("A · Dwa zdania", "Hak: zdanie z Diuny (1965) i niemal to samo zdanie z książki z 1960. Pytanie: jak wojna w górach "
              "trafiła na pustynną planetę? Chronologia: imam i Achulgo → syn i księżne → Gunib → słowa. Kąt z rozmowy 27.11.", A),
        "b": ("B · Wymiana na rzece", "Hak: w 1855 imam odzyskuje syna za porwane księżne, srebro i jeńców, a syn wraca w mundurze wroga. "
              "Emocja na start, Diuna jako tajemnica do aktu IV; zdania o ostrzu jako dowód na końcu.", B),
        "c": ("C · Słowa najpierw", "Hak: kanly, kindjal, sietch, padishah — słowa, które zna każdy fan Diuny, a których Herbert "
              "nie wymyślił. Najmocniejszy haczyk dla fanów Diuny; historia Szamila jako odpowiedź; na końcu dwa zdania.", C),
    }


def zapisz(w, tytul, opis, rows):
    out, t = [], 0.0
    for nr, row in enumerate(rows, 1):
        _, _, klucz, kadr, ruch, sek, op, dz = row
        out.append({"nr": nr, "klucz": klucz, "sekundy": sek, "opis": op, "kwestia": kwestia(dz),
                    "kadr": KADR[kadr], **({"znacznik": ZNACZNIK[klucz]} if klucz in ZNACZNIK else {})})
        t += sek
    scen = opis + "\n\n" + "\n\n".join(f"{x['opis']}\n\"{x['kwestia']}\"" if x["kwestia"] else x["opis"] for x in out)
    d = HERE / w
    d.mkdir(exist_ok=True)
    (d / "szkic.json").write_text(json.dumps({"film": "szamil-diuna", "wariant": w.upper(), "tytul": tytul, "scenariusz": scen,
                                              "ujecia": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{tytul}: {len(out)} ujęć, {int(t // 60)}:{t % 60:04.1f}")


if __name__ == "__main__":
    # 28.11.2026 reżyser zatwierdził D i rozpiska (dane.py) jest już wariantem D — od tej chwili ona jest źródłem, a pliki
    # a/b/c/d/szkic.json to zamrożone migawki porównania. Ponowne zbudowanie A–D z nowej rozpiski dałoby inne warianty.
    if "slowo_kindjal" in POOL and os.environ.get("NADPISZ_SZKICE") != "1":
        raise SystemExit("Rozpiska jest już wariantem D (zatwierdzony 28.11). Szkice a–d są zamrożone; NADPISZ_SZKICE=1, jeśli "
                         "naprawdę chcesz je przebudować.")
    wyb = sys.argv[1:] or ["a", "b", "c", "d"]
    for w, (tytul, opis, rows) in warianty().items():
        if w in wyb:
            zapisz(w, tytul, opis, rows)
