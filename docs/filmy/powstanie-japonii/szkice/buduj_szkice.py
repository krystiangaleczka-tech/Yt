"""Szkice ujęć filmu „Son of the Sun” (EN): trzy różne podejścia do tej samej historii, do porównania w Studio.

Reżyser 18.11.2026: hak na start, drugi hak po ok. 3 minutach (najpierw pogorszenie, potem promyk nadziei), na końcu
„Thank you! If you like my videos, support me, and I'll do my best.”; trzy całe szkice ujęć do przekartkowania w Studio
(etap „Szkice ujęć”), z których zatwierdzony staje się podstawą dalszej pracy.

Źródła: rozpiska (ujecia/dane.py, JEZYK=en — długości ujęć z nagranego lektora EN), kwestie EN (ujecia/kwestie_en.py)
i nieruchome klatki EN z projektu Studio (output/powstanie-japonii/studio_en.json → media projektu). Ujęcie z rozpiski
bierze swoją klatkę; gdy wariant zmienia kwestię, wpalony stary napis zostaje przykryty nowym. Nowe ujęcie bez klatki
dostaje w Studio kartę (opis + kwestia) — to jest do narysowania.

Uruchomienie (z katalogu repo albo worktree):
    JEZYK=en .venv-studio/bin/python docs/filmy/powstanie-japonii/szkice/buduj_szkice.py
Wynik: szkice/<a|b|c>/szkic.json + klatki/ (klatki są w .gitignore — powstają z Studio). Import do Studio:
Szkice ujęć → „Szkice w plikach…” → „powstanie-japonii: wszystkie warianty” → „Importuj z plików”.
"""
from __future__ import annotations

import json
import os
import re
import sys
import textwrap
from pathlib import Path

os.environ["JEZYK"] = "en"
TU = Path(__file__).resolve().parent
UJECIA = TU.parent / "ujecia"
sys.path.insert(0, str(UJECIA))
import dane  # noqa: E402
from kwestie_en import EN, SLOWNIE_EN  # noqa: E402

WORKTREE = TU.parents[3]
STUDIO_EN = WORKTREE / "output/powstanie-japonii/studio_en.json"
PROJEKT_EN = "prj_6e17b06bab8649db"
STUDIO_HOME = Path(os.environ.get("DOCOS_STUDIO_HOME", Path.home() / "Documents/YT/.docos-studio"))
TEMPO_EN = 2.84
KADR = {"TYT": "karta / napis", "PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal"}
PAUZA = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}

# Ujęcia rozpiski: klucz → (ref, kadr, sekundy EN, opis PL, kwestia EN)
ROZPISKA = {}
for akt, k, klucz, kadr, _ruch, sec, opis, dzwiek in dane.ujecia():
    ROZPISKA[klucz] = (f"d{akt:02d}_{k:02d}", KADR.get(kadr, kadr), sec, opis, EN.get(klucz, "") if dzwiek.startswith("L:") else "")


def slowa(line: str) -> int:
    for k, v in SLOWNIE_EN.items():
        line = line.replace(k, v)
    return sum(2 if re.search(r"\d", w) else 1 for w in line.split())


def czas(line: str, pauza="ujecie", hak=False, dodaj=0.0) -> float:
    """Oddech + mowa (tempo lektora EN) + pauza po kwestii (Rytm 2); w haku szybciej: 0,4 s oddechu i 1 s pauzy."""
    if not line:
        return 2.0
    oddech, po = (0.4, 1.0) if hak else (0.6, PAUZA[pauza])
    return round(oddech + slowa(line) / TEMPO_EN + po + dodaj, 1)


KEEP = object()


def R(klucz, line=KEEP, sec=None, mark="", pauza="ujecie", hak=False, uwaga=""):
    """Ujęcie z rozpiski (istniejące): ta sama klatka; kwestia i długość mogą się zmienić."""
    return {"typ": "R", "klucz": klucz, "line": line, "sec": sec, "mark": mark, "pauza": pauza, "hak": hak, "uwaga": uwaga}


def N(klucz, opis, line, kadr="plan średni", klatka=None, sec=None, mark="", pauza="ujecie", hak=False):
    """Nowe ujęcie (do narysowania). klatka = klucz ujęcia, którego obraz pokazać poglądowo; None = karta."""
    return {"typ": "N", "klucz": klucz, "opis": opis, "line": line, "kadr": kadr, "klatka": klatka, "sec": sec,
            "mark": mark, "pauza": pauza, "hak": hak}


def AKT(numer, pytanie):
    """Kurtyna między aktami z tytułem-pytaniem (zasuwa się w pauzie końca aktu — nie wydłuża filmu)."""
    return {"typ": "AKT", "mark": f"AKT {numer}", "pytanie": pytanie}


DZIEKI = "Thank you for watching! If you like my videos, support me, and I'll do my best."

# ----------------------------------------------------------------------------------------------- wariant A
A = {
    "wariant": "a",
    "tytul": "A · Trzy skarby — miecz, którego nikt nie widział",
    "podejscie": (
        "Zimny start od tajemnicy: w 2019 roku nowy cesarz dostaje miecz, którego nikt nie widział. Trzy skarby (lustro, "
        "klejnoty, miecz) są nicią całego filmu: mit pokazuje, skąd się wzięły, wyprawa Iwarebiko — komu przypadły, "
        "a historia na końcu — co z tego jest prawdą. Kolejność jak w obecnym filmie, więc to najtańszy wariant: prawie "
        "wszystkie ujęcia już są, nowe są tylko kwestie haka, obietnicy, drugiego haka i podziękowania."),
    "pogorszenie": "Starcy z Izumo: wąż pożarł siedem córek i idzie po ostatnią.",
    "hak2": "Susanoo znajduje miecz w ogonie węża — ten sam, który według tradycji dostał cesarz w 2019 roku "
            "(odpowiedź na hak 1) — a Ninigi dostaje trzy skarby, choć człowiek, który zbuduje z nimi kraj, "
            "jeszcze się nie urodził (pytanie na dalej).",
    "ujecia": [
        R("koronacja", "In 2019, Japan's new emperor was handed a sword that no one alive has ever seen.", hak=True, mark="HOOK 1"),
        R("orochi", "Legend says it was pulled from the tail of an eight-headed serpent.", hak=True),
        R("linia", "It has passed through a hundred and twenty-six emperors, so who was the first of them, and did he "
                   "even exist?", hak=True, pauza="beat"),
        R("teatr", sec=2.5, mark="TYTUŁ", uwaga="Otwarcie teatru skrócone z 6,5 s do 2,5 s, dopiero po haku."),
        R("luty", "By the end, you'll know why Japan's birthday was probably made up, and why its football team wears a "
                  "three-legged crow.", mark="OBIETNICA", pauza="akt"),
        AKT("I", "Act I · How do you make a country from a single drop?"),
        R("most", "In the beginning, the young earth drifted without shape, until two gods, Izanagi and Izanami, came "
                  "down to give it one.", uwaga="Meduza wypada; jej zdanie wchodzi do kwestii mostu."),
        R("wlocznia"), R("kropla"), R("wyspy"),
        AKT("II", "Act II · Why did the sun hide in a cave?"),
        R("ogien"),
        R("rzeka", "Grieving, Izanagi washed in a river, and from his eyes and nose were born Amaterasu, the sun goddess, "
                   "the moon god, and Susanoo, god of storms.", pauza="beat", uwaga="Kraina zmarłych (yomi) wypada."),
        R("susanoo"), R("jaskinia"), R("ciemno"), R("koguty"), R("uzume"), R("lustro"), R("swit"),
        AKT("III", "Act III · What was hiding in the serpent's tail?"),
        R("wygnanie"), R("starcy", mark="POGORSZENIE"), R("kadzie"), R("orochi"), R("pije"),
        R("miecz", "When the drunken heads fell asleep, Susanoo cut the serpent apart and found a sword in its tail, the "
                   "sword that, according to tradition, is still handed to every new emperor.",
          mark="HOOK 2 · promyk nadziei", pauza="beat", uwaga="Odpowiedź na hak 1: miecz z koronacji 2019."),
        R("skarby", "Amaterasu gave the mirror, the jewels and the sword to her grandson Ninigi, but the man who would "
                    "build a country with them had not yet been born.", uwaga="Pytanie na dalej (drugi hak)."),
        R("zejscie", pauza="akt", uwaga="Księżniczki kwiatów i skał (siostry, płatki) wypadają."),
        AKT("IV", "Act IV · Why would a prince sail east at forty-five?"),
        R("prawnuk"), R("wschod"), R("bracia"), R("flota"), R("naniwa", uwaga="Postoje w portach wypadają."),
        R("nagasune"), R("strzaly"), R("rana"), R("pod_slonce"),
        AKT("V", "Act V · Who sent the crow?"),
        R("itsuse"), R("burza"), R("sam"), R("las"), R("niedzwiedz"), R("takakuraji"), R("przebudzenie"), R("wrona"),
        R("trzy_nogi", mark="ODPOWIEDŹ 1"),
        AKT("VI", "Act VI · How do you win a battle in a hailstorm?"),
        R("yamato", uwaga="Pułapka w chacie wypada."), R("bitwa"), R("ptak"), R("blysk"), R("order"),
        R("strzala_nieba"), R("zdrada"),
        AKT("VII", "Act VII · Who sat on the first throne?"),
        R("palac"), R("tron"), R("imie"), R("smierc", uwaga="Żona i pola ryżowe wypadają."), R("pusto"), R("linia"),
        AKT("VIII", "Act VIII · Was any of it true?"),
        R("kronika"), R("rachunek", mark="ODPOWIEDŹ 2"), R("jomon"), R("wa"), R("pieczec"), R("odcisk"), R("chlop"),
        R("himiko"),
        AKT("IX", "Act IX · Why 'the origin of the sun'?"),
        R("kofun"), R("haniwa"), R("tancerz"), R("nihon"), R("luty2"), R("koronacja"), R("koniec"),
        R("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
    ],
}

# ----------------------------------------------------------------------------------------------- wariant B
B = {
    "wariant": "b",
    "tytul": "B · Śledztwo — czy Jimmu w ogóle istniał?",
    "podejscie": (
        "Film jako śledztwo. Start od sprzeczności: Japonia świętuje urodziny cesarza, który mógł nie istnieć, a datę "
        "wyliczono z wróżby. Najpierw kto i po co spisał historię (712), potem jej treść w skrócie („kronika twierdzi…”), "
        "potem dowody, które ją podważają (pogorszenie: data z wróżby, myśliwi zamiast pałaców, imię nadane po 1400 "
        "latach), aż złota pieczęć wykopana przez chłopa pokazuje, że prawdziwi królowie jednak byli (hak 2). Druga "
        "połowa to legenda wyprawy jako opowieść, której dwór potrzebował, a koniec — kurhany, Nihon, 1873 i 2019. "
        "Najmocniej przestawia kolejność, mit jest najkrótszy."),
    "pogorszenie": "Data 660 p.n.e. z chińskiej wróżby, na wyspach tylko myśliwi, imię Jimmu nadane 1400 lat później — "
                   "wygląda, że nie ma tu nic prawdziwego.",
    "hak2": "W 1784 roku motyka chłopa uderza w złoto: pieczęć z roku 57 dowodzi, że na wyspach byli prawdziwi królowie.",
    "ujecia": [
        R("luty", "Every eleventh of February, Japan celebrates the day its first emperor took the throne.", hak=True,
          mark="HOOK 1"),
        R("rachunek", "But that date was only fixed thirteen centuries later.", hak=True),
        R("jomon", "In that year, the islands were home only to hunters and fishermen.", hak=True),
        R("cien", "So why does Japan celebrate a man who may never have lived?", hak=True, pauza="beat"),
        R("teatr", sec=2.5, mark="TYTUŁ"),
        N("obietnica", "Karta śledztwa: na nitkach zjeżdżają po kolei cztery zawieszki — zwój kroniki, liczba „1260”, "
                       "złota pieczęć i trójnoga wrona — i kołyszą się obok siebie.",
          "Let's follow four clues: a court chronicle, a Chinese prophecy, a farmer's golden find and a three-legged crow.",
          kadr="plan średni", mark="OBIETNICA", pauza="akt"),
        AKT("I", "Act I · Who wrote the story, and why?"),
        R("kronika", "The story of the first emperor was written down only in 712 and 720, in chronicles the court "
                     "ordered to prove its right to rule."),
        R("most", "The chronicles begin with two gods, Izanagi and Izanami, standing on a floating bridge above a "
                  "shapeless sea."),
        R("kropla", "They stirred the sea with a jewelled spear, and from one drop of salt grew the first island, and "
                    "then all of Japan."),
        R("wyspy", "", sec=3.0, uwaga="Bez kwestii: wyspy wysuwają się spomiędzy fal."),
        R("jaskinia", "Izanagi's daughter Amaterasu, the sun goddess, once hid in a cave, and the whole world went dark."),
        R("uzume"),
        R("lustro", "Curious, Amaterasu peeked out at her own radiance in a mirror, and that mirror became one of the "
                    "three sacred treasures of Japan's emperors."),
        R("orochi", "Her brother Susanoo killed an eight-headed serpent that had eaten seven girls,"
                    " and in its tail he found a sword, the second treasure.", uwaga="Kadzie i picie sake wypadają."),
        R("skarby"),
        R("zejscie", pauza="akt"),
        AKT("II", "Act II · Does the date add up?"),
        R("tron", "The chronicle says that Ninigi's great-grandson, Prince Iwarebiko, took the throne on the first day "
                  "of 660 BC."),
        R("rachunek"),
        R("jomon", mark="POGORSZENIE"),
        R("imie", "Even the name Jimmu was given to him by scholars fourteen hundred years later, so it looked as if "
                  "nothing here was real.", pauza="beat"),
        R("chlop", "Then, in 1784, a farmer repairing a ditch struck something golden with his hoe.",
          mark="HOOK 2 · promyk nadziei"),
        R("pieczec", "It was a seal the emperor of China had sent to a king of the Wa in the year 57: proof that real "
                     "kings ruled the islands long before the chronicles."),
        R("odcisk"), R("wa"), R("himiko", pauza="akt"),
        AKT("III", "Act III · Who was the prince the chronicle needed?"),
        R("prawnuk"), R("wschod"), R("bracia"), R("flota"), R("naniwa"), R("nagasune"), R("strzaly"), R("rana"),
        R("pod_slonce", pauza="akt"),
        AKT("IV", "Act IV · Who sent the crow?"),
        R("itsuse"), R("burza"), R("sam"), R("las"), R("niedzwiedz"), R("takakuraji"), R("przebudzenie"), R("wrona"),
        R("trzy_nogi", mark="ODPOWIEDŹ 1"),
        AKT("V", "Act V · How did a newcomer win Yamato?"),
        R("yamato"), R("pulapka"), R("bitwa"), R("ptak"), R("blysk"), R("strzala_nieba"), R("zdrada"),
        R("palac", "Below Mount Unebi, at Kashihara, Iwarebiko built a palace whose pillars, the chronicle says, were "
                   "driven into the bedrock, and there he became the first emperor."),
        R("smierc"), R("linia", pauza="akt"),
        AKT("VI", "Act VI · So did he exist?"),
        R("kofun"), R("haniwa"), R("tancerz"), R("nihon"), R("luty2", mark="ODPOWIEDŹ 2"), R("koronacja"), R("koniec"),
        R("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
    ],
}

# ----------------------------------------------------------------------------------------------- wariant C
C = {
    "wariant": "c",
    "tytul": "C · Czterech braci — od klęski do tronu",
    "podejscie": (
        "Start w środku akcji, od najgorszej chwili: strzała trafia najstarszego brata, burza zabiera dwóch kolejnych, "
        "zostaje jeden. Potem film cofa się i krótko opowiada legendę rodu (słońce, lustro, miecz) jako to, w co wierzył "
        "książę, i wraca na wyprawę: klęska pod słońcem (pogorszenie, tak jak w haku), zaczarowany las i ratunek — miecz "
        "z nieba i trójnoga wrona (hak 2). Dalej Yamato, tron i na koniec zwrot historyczny: kronika, wróżba, pieczęć, "
        "kurhany, 2019. Najbardziej opowieść o bohaterze; mit najkrótszy, film najkrótszy."),
    "pogorszenie": "Klęska pod Kusaką: strzała w Itsuse, Itsuse umiera, burza zabiera dwóch braci, Iwarebiko zostaje sam, "
                   "a w lesie Kumano cała armia pada zaczarowana.",
    "hak2": "Takakuraji przynosi miecz zrzucony z nieba, wojsko się budzi i przylatuje wrona Yatagarasu.",
    "ujecia": [
        R("strzaly", mark="HOOK 1", uwaga="Bez kwestii: chmara strzał spod słońca."),
        R("rana", "An arrow struck Prince Itsuse, the eldest of four brothers fighting their way east.", hak=True),
        R("burza", "Soon Itsuse was dead, and a storm swallowed two more of the brothers.", hak=True),
        R("sam", "The last one left would become Japan's first emperor, if he ever existed at all.", hak=True,
          pauza="beat"),
        R("teatr", sec=2.5, mark="TYTUŁ"),
        N("obietnica", "Wrona Yatagarasu przelatuje nad górami (kadr z ujęcia „wrona”), a obok zjeżdża zawieszka "
                       "„11 February” i kołysze się.",
          "By the end, you'll know who sent him a three-legged crow, and why Japan celebrates a birthday that was "
          "probably made up.", kadr="plan ogólny", klatka="wrona", mark="OBIETNICA", pauza="akt"),
        AKT("I", "Act I · Why did a prince believe he came from the sun?"),
        R("prawnuk", "His name was Iwarebiko, and he grew up on Kyushu, in the land of Hyuga, as a descendant of the sun "
                     "goddess herself."),
        R("kropla", "His family's legend began with two gods, who stirred the sea with a jewelled spear until a single "
                    "drop of salt became the first island of Japan.", uwaga="Meduza i most wypadają."),
        R("rzeka", "Later, the god Izanagi washed in a river, and from his left eye was born Amaterasu, the sun goddess."),
        R("jaskinia"),
        R("lustro", "The gods lured her out with a mirror, and light returned to the world."),
        R("orochi", "Her storm-god brother, Susanoo, killed an eight-headed serpent and found a sword in its tail."),
        R("skarby", "Amaterasu gave the mirror, the jewels and the sword to her grandson Ninigi, who carried them "
                    "down from heaven to Kyushu.", pauza="akt", uwaga="Zejście Ninigiego wchodzi do tej kwestii."),
        AKT("II", "Act II · Why were they losing?"),
        R("wschod", "Iwarebiko was Ninigi's great-grandson, and at forty-five he heard of a beautiful land in the east, "
                    "surrounded by blue mountains."),
        R("bracia"), R("naniwa", uwaga="Rejs i postoje wypadają: łodzie od razu przybijają w Naniwie."),
        R("nagasune"), R("strzaly"), R("rana"), R("pod_slonce"),
        R("itsuse", mark="POGORSZENIE"), R("burza"), R("sam", pauza="akt"),
        AKT("III", "Act III · Who sent the crow?"),
        R("las"), R("niedzwiedz"), R("takakuraji", mark="HOOK 2 · promyk nadziei"), R("przebudzenie"), R("wrona"),
        R("trzy_nogi", mark="ODPOWIEDŹ 1", pauza="akt"),
        AKT("IV", "Act IV · How do you take a valley where every hill has a chief?"),
        R("yamato"), R("pulapka"), R("bitwa"), R("ptak"), R("blysk"), R("strzala_nieba"), R("zdrada", pauza="akt"),
        AKT("V", "Act V · Did the first emperor really live to 127?"),
        R("palac"), R("tron"), R("imie"), R("smierc"), R("linia", pauza="akt"),
        AKT("VI", "Act VI · So did he exist?"),
        R("kronika"), R("rachunek", mark="ODPOWIEDŹ 2"), R("jomon"), R("pieczec"), R("chlop"), R("kofun"), R("haniwa"),
        R("nihon"), R("luty2"), R("koronacja"), R("koniec"),
        R("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
    ],
}


def ujecia_wariantu(w):
    out, pytanie, akt_mark = [], "", ""
    for e in w["ujecia"]:
        if e["typ"] == "AKT":
            pytanie, akt_mark = e["pytanie"], e["mark"]
            continue
        if e["typ"] == "R":
            ref, kadr, sec0, opis, line0 = ROZPISKA[e["klucz"]]
            line = line0 if e["line"] is KEEP else e["line"]
            zmiana = line != line0
            sec = e["sec"] if e["sec"] is not None else (
                sec0 if not zmiana else czas(line, e["pauza"], e["hak"], 0.0 if e["hak"] else dane.WYDLUZ.get(e["klucz"], 0.0)))
            if e["hak"] and not zmiana:
                sec = min(sec, czas(line, hak=True))
            rodzaj = ("z rozpiski, bez kwestii" if zmiana and not line else "z rozpiski, nowa kwestia" if zmiana
                      else "z rozpiski" if e["sec"] is None else "z rozpiski, skrócone")
            if e["hak"]:
                e = {**e, "uwaga": " ".join(x for x in ("W haku: szybkie cięcie, tylko kulminacja ujęcia.", e["uwaga"]) if x)}
            item = {"klucz": e["klucz"], "ref": ref, "kadr": kadr, "sekundy": sec, "opis": opis, "kwestia": line,
                    "klatka_ref": ref, "napis": zmiana, "rodzaj": rodzaj, "uwaga": e["uwaga"], "mark": e["mark"]}
        else:
            sec = e["sec"] if e["sec"] is not None else czas(e["line"], e["pauza"], e["hak"])
            item = {"klucz": e["klucz"], "ref": "", "kadr": e["kadr"], "sekundy": sec, "opis": e["opis"],
                    "kwestia": e["line"], "klatka_ref": ROZPISKA[e["klatka"]][0] if e["klatka"] else "",
                    "napis": bool(e["klatka"]), "rodzaj": "nowe ujęcie, do narysowania", "uwaga": "", "mark": e["mark"]}
        if pytanie:
            item["opis"] = f"Kurtyna z tytułem aktu: „{pytanie}”. Potem: " + item["opis"]
            item["mark"] = " · ".join(x for x in (akt_mark, item["mark"]) if x)
            pytanie = ""
        if item["uwaga"]:
            item["opis"] += f" — Uwaga: {item['uwaga']}"
        out.append(item)
    return out


def zegar(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


def klatka(ref, line, napis, cel, assets, klipy, media):
    from PIL import Image, ImageDraw, ImageFont
    asset = assets.get(klipy[ref]["asset"]) if ref in klipy else None
    if not asset or not (media / asset["filename"]).is_file():
        return False
    im = Image.open(media / asset["filename"]).convert("RGB").resize((640, 360))
    if napis:  # wpalony napis starej kwestii przykryty nową kwestią wariantu (Rytm 5: napis = kwestia)
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle((0, 282, 640, 360), fill=(18, 14, 10, 255))
        if line:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 13)
            rows = textwrap.wrap(line, 78)[:3]
            h = 17 * len(rows) + 10
            top = 352 - h
            w = max(d.textlength(r, font=font) for r in rows) + 24
            d.rectangle(((640 - w) / 2, top, (640 + w) / 2, top + h), fill=(240, 231, 209, 255))
            for i, r in enumerate(rows):
                d.text((320, top + 6 + 17 * i), r, font=font, fill=(40, 30, 22), anchor="mt")
    cel.parent.mkdir(parents=True, exist_ok=True)
    im.save(cel, "JPEG", quality=85)
    return True


def scenariusz(w, items):
    t, czasy = 0.0, []
    for i in items:
        czasy.append(t)
        t += i["sekundy"]
    znaczniki = [f"{zegar(czasy[n])}  {i['mark']}" for n, i in enumerate(items) if i["mark"]]
    nowe = [i for i in items if i["rodzaj"] != "z rozpiski"]
    pominiete = [k for k in ROZPISKA if k not in {i["klucz"] for i in items}]
    lines = [w["tytul"], "", "PODEJŚCIE", w["podejscie"], "",
             f"DŁUGOŚĆ: {zegar(t)} · {len(items)} ujęć (obecny film EN: 12:20,4 · 79 ujęć)", "",
             "ZNACZNIKI", *znaczniki, "",
             "POGORSZENIE → HAK 2", f"Pogorszenie: {w['pogorszenie']}", f"Hak 2: {w['hak2']}", "",
             "AKTY (tytuł na kurtynie)",
             *[f"{e['mark']}: {e['pytanie']}" for e in w["ujecia"] if e["typ"] == "AKT"], "",
             f"CO TRZEBA ZROBIĆ: nowe ujęcia do narysowania: {sum(i['rodzaj'] == 'nowe ujęcie, do narysowania' for i in items)}, "
             f"nowe kwestie do nagrania: {sum('nowa kwestia' in i['rodzaj'] for i in items)}, "
             f"skrócone ujęcia: {sum(i['rodzaj'] == 'z rozpiski, skrócone' for i in items)}; reszta ujęć bez zmian.",
             f"WYPADA Z FILMU ({len(pominiete)}): " + ", ".join(pominiete), "",
             "NOWE I ZMIENIONE KWESTIE EN"]
    for n, i in enumerate(nowe):
        if i["kwestia"]:
            lines.append(f"{zegar(czasy[items.index(i)])} [{i['klucz']}] „{i['kwestia']}”")
    return "\n".join(lines), t, czasy


def main():
    klipy = json.loads(STUDIO_EN.read_text(encoding="utf-8"))["klipy"]
    folder = STUDIO_HOME / "projects" / PROJEKT_EN
    project = json.loads((folder / "project.json").read_text(encoding="utf-8"))
    assets = {a["id"]: a for a in project["assets"]}
    media = folder / "media"
    for w in (A, B, C):
        items = ujecia_wariantu(w)
        tekst, total, czasy = scenariusz(w, items)
        cel = TU / w["wariant"]
        ujecia = []
        for n, i in enumerate(items, 1):
            plik = ""
            if i["klatka_ref"]:
                nazwa = f"klatki/{n:03d}_{i['klucz']}.jpg"
                if klatka(i["klatka_ref"], i["kwestia"], i["napis"], cel / nazwa, assets, klipy, media):
                    plik = nazwa
            ujecia.append({"nr": n, "klucz": i["klucz"], "kadr": i["kadr"], "sekundy": i["sekundy"],
                           "opis": f"[{i['rodzaj']}] " + i["opis"], "kwestia": i["kwestia"], "znacznik": i["mark"],
                           "klatka": plik})
        (cel / "szkic.json").write_text(json.dumps({
            "film": "powstanie-japonii", "wariant": w["wariant"], "tytul": w["tytul"], "scenariusz": tekst,
            "ujecia": ujecia}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        hak2 = next(czasy[n] for n, i in enumerate(items) if i["mark"].startswith("HOOK 2") or " HOOK 2" in i["mark"])
        gorzej = next(czasy[n] for n, i in enumerate(items) if "POGORSZENIE" in i["mark"])
        hak1 = sum(i["sekundy"] for i in items[:next(n for n, i in enumerate(items) if "TYTUŁ" in i["mark"])])
        print(f"{w['tytul']}: {zegar(total)}, {len(items)} ujęć, hak 1 {hak1:.1f} s, pogorszenie {zegar(gorzej)}, "
              f"hak 2 {zegar(hak2)}, klatek {sum(1 for u in ujecia if u['klatka'])}")


if __name__ == "__main__":
    main()
