"""Księga świata, Story Bible i warsztat filmu „Bonnie and Clyde: The Outlaws Made of Paper” — źródło dla Studio.

  python3 docs/filmy/bonnie-i-clyde/ujecia/ksiega.py    — zapisuje ../swiat.json i ../warsztat.json (kopia do historii gita)

Odwołania do ujęć powstają z kluczy rozpiski (`r("parol", "parole")` → `d01_14~parole`), więc dopisanie ujęcia ich nie psuje.
Miejscem pracy jest Studio (Continuity Editor → Świat / Warsztat); wgrywa je output/bonnie-i-clyde/studio_film.py.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dane import ujecia  # noqa: E402

_REF = {u[2]: f"d{u[0]:02d}_{u[1]:02d}" for u in ujecia()}
_TXT = {u[2]: (u[6] + " " + u[7]).lower() for u in ujecia()}


def r(klucz, kotwica=""):
    """Odwołanie do ujęcia po kluczu, z kotwicą (słowem z opisu albo kwestii tego ujęcia)."""
    assert not kotwica or kotwica.lower() in _TXT[klucz], (klucz, kotwica)
    return _REF[klucz] + (f"~{kotwica}" if kotwica else "")


SWIAT = {
    "version": 1,
    "unitLabel": "Akt",
    "tempo": {"minSeconds": 80, "maxSeconds": 160, "maxVoiceShare": 0.85},
    "places": [
        {"id": "teatr", "name": "Teatr z gazet", "note": "Rama sceny oklejona pierwszymi stronami gazet z lat 30.; szyld „THE OUTLAWS "
         "MADE OF PAPER” w stylu art déco; pierwsze i ostatnie ujęcia, obietnica, puenta.", "connects": ["preria", "miasto"]},
        {"id": "west_dallas", "name": "West Dallas (lata 20.)", "note": "Namioty i szałasy pod wiaduktem nad rzeką Trinity, dymy z kominów, "
         "błoto; wóz konny Barrowów.", "connects": ["miasto"]},
        {"id": "cement_city", "name": "Cement City", "note": "Kominy cementowni, drewniane domki, szkoła z podium; dom Bonnie i Roya."},
        {"id": "wnetrza", "name": "Wnętrza", "note": "Kawiarnia w Dallas, kuchnia przyjaciółki, areszty w Waco i Kaufman (kraty), mieszkanie "
         "nad garażem w Joplin, ciemnia redakcji, biuro Hamera, chata Methvinów, dom matki Bonnie, zakład pogrzebowy. Jedna "
         "dekoracja wnętrza z wymiennymi ścianami, oknem, drzwiami i meblami."},
        {"id": "preria", "name": "Preria i drogi", "note": "Płaska preria w złocistych pasach trawy, polna droga z koleinami, słupy "
         "telegraficzne, wiatrak, płot; odmiany: Teksas, Oklahoma, granica stanów, Kansas.", "connects": ["miasto", "las"]},
        {"id": "miasto", "name": "Miasteczko", "note": "Ulica z fasadami: stacja benzynowa, sklep żelazny, kawiarnia, kiosk, drukarnia, "
         "słup z listami gończymi; odmiany: Joplin, Ruston, Commerce, Arcadia, Shreveport."},
        {"id": "eastham", "name": "Farma więzienna Eastham", "note": "Rzędy bawełny, płot z drutu, wieża strażnicza, brama; barak (teatr "
         "cieni); mgła przy odbiciu w styczniu 1934."},
        {"id": "wellington", "name": "Wellington: rozebrany most i wąwóz", "note": "Nocna droga, tablica DETOUR, most bez przęsła, wąwóz "
         "z rzeką; farma; las w Oklahomie z drzewem."},
        {"id": "las", "name": "Lasy i rzeki", "note": "Park Dexfield w Iowie (liściaste), rzeka, las sosnowy przy drodze w Luizjanie "
         "(zasadzka), krzaki."},
        {"id": "parawan", "name": "Teatr cieni", "note": "Podświetlony parawan, za którym giną ludzie: Eastham (barak), Hillsboro, Atoka, Joplin, "
         "Platte City, Sowers, Grapevine, Commerce, zasadzka. Błyski i padające sylwetki, bez krwi (D2)."},
        {"id": "mapa", "name": "Mapa pięciu stanów", "note": "Mapa z gazet na tablicy Hamera: Teksas, Oklahoma, Missouri, Luizjana, Kansas "
         "(i Iowa, Arkansas); pinezki, czerwona nić w pętlach."},
        {"id": "epilog", "name": "Epilog", "note": "Cmentarze w Dallas, jarmark z autem pod namiotem, dom Blanche (1988), ganek Hamera, kino "
         "z ekranem z gazet."},
    ],
    "characters": [
        {"id": "bonnie", "name": "Bonnie Parker", "role": "kelnerka z Dallas, poetka, wspólniczka Clyde'a",
         "look": "drobna (ok. 150 cm), jasne kręcone włosy do ramion, beret; sukienka do kolan, od " + r("wellington_bonnie", "noga")
         + " bandaż na nodze i kulenie", "costume": "w dniu zasadzki czerwona sukienka", "namedIn": ["d*"],
         "states": [{"from": r("wellington_bonnie", "noga"), "state": "poparzona noga, kuleje"},
                    {"from": r("zasadzka", "papierowy Ford"), "state": "nie żyje"}]},
        {"id": "bonnie_mala", "name": "mała Bonnie", "role": "Bonnie w szkole", "look": "dziewczynka w sukience z kokardą"},
        {"id": "clyde", "name": "Clyde Barrow", "role": "złodziej z West Dallas, kierowca", "look": "szczupły, ciemne włosy, fedora, "
         "garnitur; od " + r("palce", "siekiery") + " kuleje (obcięte palce u stopy)", "namedIn": ["d*"],
         "states": [{"from": r("palce", "siekiery"), "state": "kuleje"}, {"from": r("zasadzka", "papierowy Ford"), "state": "nie żyje"}]},
        {"id": "clyde_maly", "name": "mały Clyde", "role": "Clyde jako dziecko pod wozem", "look": "chłopiec w łatanych ogrodniczkach"},
        {"id": "buck", "name": "Buck Barrow", "role": "starszy brat Clyde'a", "look": "krępy, kaszkiet, kamizelka",
         "joins": r("buck", "Buck"), "leaves": r("dexfield", "Buck")},
        {"id": "blanche", "name": "Blanche Barrow", "role": "żona Bucka", "look": "kapelusik, płaszczyk, biały piesek na rękach",
         "joins": r("buck", "Blanche"), "leaves": r("dexfield", "Blanche"), "states": [{"from": r("platte", "Blanche"),
                                                                                       "state": "ślepa na jedno oko (od " "Platte City)"}]},
        {"id": "wd", "name": "W.D. Jones", "role": "szesnastolatek z sąsiedztwa", "look": "chudy chłopak w kaszkiecie",
         "joins": r("wd", "W.D. Jones"), "leaves": r("wd_odchodzi", "W.D.")},
        {"id": "roy", "name": "Roy Thornton", "role": "mąż Bonnie", "look": "młody, zaczesane włosy, walizka", "leaves": r("kawiarnia", "Roy")},
        {"id": "hamer", "name": "Frank Hamer", "role": "emerytowany strażnik Teksasu (Ranger), łowca", "look": "wysoki, ciężki, kapelusz "
         "Stetson, kamizelka, długi płaszcz", "namedIn": ["d05_*", "d06_*", "d07_*", "d08_*"]},
        {"id": "simmons", "name": "Lee Simmons", "role": "szef więziennictwa Teksasu", "look": "garnitur, okulary, łysina"},
        {"id": "darby", "name": "Dillard Darby", "role": "młody przedsiębiorca pogrzebowy z Ruston", "look": "czarny garnitur, muszka",
         "namedIn": ["d03_*", "d08_*"]},
        {"id": "stone", "name": "Sophia Stone", "role": "znajoma Darby'ego", "look": "kapelusz z rondem, płaszczyk"},
        {"id": "ivy", "name": "Ivy Methvin", "role": "farmer z Luizjany, ojciec Henry'ego", "look": "broda, ogrodniczki, kapelusz słomkowy",
         "namedIn": ["d07_*"]},
        {"id": "henry", "name": "Henry Methvin", "role": "młody więzień uwolniony w Eastham", "look": "chłopak w koszuli, kaszkiet",
         "namedIn": ["d07_*"]},
        {"id": "boyd", "name": "Percy Boyd", "role": "komendant policji z Commerce", "look": "mundur, czapka"},
        {"id": "murphy", "name": "H.D. Murphy", "role": "młody policjant drogowy z Grapevine", "look": "mundur, bryczesy, motocykl",
         "leaves": r("grapevine_cien", "shot")},
        {"id": "tullis", "name": "Maree Tullis", "role": "narzeczona Murphy'ego", "look": "biała suknia ślubna"},
        {"id": "matki", "name": "matki: Emma Parker i Cumie Barrow", "role": "rodziny, do których wracają", "look": "starsze kobiety "
         "w fartuchach, siwe włosy"},
        {"id": "posse", "name": "sześciu ludzi z zasadzki", "role": "Hamer, Gault, Alcorn, Hinton, Jordan, Oakley",
         "look": "kapelusze, karabiny", "namedIn": ["d07_*"]},
    ],
    "props": [
        {"id": "aparat", "name": "Aparat z kliszą", "place": "wnetrza", "seeded": r("hak_joplin_rzeczy", "aparat"),
         "uses": [r("joplin_rzeczy", "aparat"), r("ciemnia", "klisza")], "note": "Hak 1 i powrót w akcie III innymi słowami."},
        {"id": "cygaro", "name": "Pożyczone cygaro", "owner": "Bonnie", "seeded": r("zdjecie", "cygaro"),
         "uses": [r("hak_cygaro", "cigars"), r("cygaro_zlosc", "cygaro"), r("boyd_tab", "cigars")]},
        {"id": "suicide_sal", "name": "Wiersz o Suicide Sal", "owner": "Bonnie", "seeded": r("cela", "Suicide Sal"),
         "uses": [r("joplin_rzeczy", "poems")]},
        {"id": "teczka", "name": "Teczka z wycinkami", "place": "wnetrza", "seeded": r("teczka_zasiew", "teczki"),
         "uses": [r("hak_teczka", "teczkę"), r("podkreslenie", "aktach"), r("prasa_cygaro", "desk")]},
        {"id": "radiowoz_zabawka", "name": "Zabawkowy radiowóz", "owner": "Hamer", "seeded": r("hak_szuflada", "radiowóz")},
        {"id": "mapa_nic", "name": "Mapa z czerwoną nicią", "place": "mapa", "seeded": r("mapa", "mapy"),
         "uses": [r("petle", "nić"), r("prasa_cygaro", "map")]},
        {"id": "list_forda", "name": "List do Henry'ego Forda", "seeded": r("list_ford", "letter")},
        {"id": "pardon", "name": "Papier z pieczęcią PARDON", "seeded": r("methvin", "pardon")},
        {"id": "ciezarowka", "name": "Ciężarówka Ivy'ego na lewarku", "owner": "Ivy Methvin", "seeded": r("zasadzka_rano", "truck"),
         "uses": [r("zwolnienie", "ciężarówce")]},
        {"id": "wiersz", "name": "Wiersz dla matki („The Trail's End”)", "owner": "Bonnie", "seeded": r("wiersz", "poem"),
         "uses": [r("pogrzeby", "poem")], "note": "Tylko parafraza; prawa autorskie niesprawdzone."},
        {"id": "obraczka", "name": "Obrączka Roya", "owner": "Bonnie", "seeded": r("kawiarnia", "ring")},
    ],
    "resources": [],
    "rules": [
        {"id": "clyde_wolny", "name": "Clyde na wolności", "from": r("parol", "parole"), "to": r("zasadzka", "papierowy Ford")},
        {"id": "buck_zyje", "name": "Buck żyje i jest z gangiem", "from": r("buck", "Buck"), "to": r("dexfield", "Buck")},
        {"id": "wd_w_gangu", "name": "W.D. jest z gangiem", "from": r("wd", "W.D."), "to": r("wd_odchodzi", "W.D.")},
        {"id": "hamer_poluje", "name": "Hamer prowadzi pościg", "from": r("hamer", "took the job"), "to": r("dym", "rounds")},
        {"id": "powaga", "name": "ton poważny (bez żartów)", "from": r("grapevine", "Easter"), "to": r("pogrzeby", "cemeteries"),
         "note": "D2: od Grapevine do pogrzebów bez gagów; tabliczka z cygarami to ironia o Bonnie, nie o ofiarach."},
    ],
    "events": [
        {"at": r("joplin_karty", "cards"), "note": "Buck i Blanche w mieszkaniu w Joplin", "needs": ["buck_zyje"]},
        {"at": r("platte", "Buck"), "note": "Buck ranny w Platte City", "needs": ["buck_zyje"]},
        {"at": r("wellington_bonnie", "W.D."), "note": "W.D. wyciąga Bonnie z auta", "needs": ["wd_w_gangu"]},
        {"at": r("przeprawa", "W.D."), "note": "W.D. ucieka z nimi przez rzekę", "needs": ["wd_w_gangu"]},
        {"at": r("rodziny", "families"), "note": "spotkania z matkami bez W.D. i Bucka", "needsOff": ["wd_w_gangu", "buck_zyje"]},
        {"at": r("dzien1", "day one"), "note": "pierwszy dzień pościgu Hamera", "needs": ["hamer_poluje"]},
        {"at": r("grapevine", "day fifty"), "note": "Grapevine = 50. dzień pościgu", "needs": ["hamer_poluje"]},
        {"at": r("zasadzka_rano", "May 23"), "note": "zasadzka = 102. dzień", "needs": ["hamer_poluje", "clyde_wolny"]},
    ],
    "threads": [
        {"id": "cygaro", "title": "Bonnie nie paliła cygar", "setup": [r("zdjecie", "cigar")], "clues": [r("hak_cygaro", "cigars"),
         r("cygaro_zlosc", "cygaro")], "payoff": [r("boyd_tab", "cigars")]},
        {"id": "aparat", "title": "Klisza z Joplin", "setup": [r("hak_joplin_rzeczy", "camera")], "payoff": [r("joplin_rzeczy", "camera")]},
        {"id": "darby", "title": "Przedsiębiorca pogrzebowy", "setup": [r("darby_smiech", "work on her")],
         "payoff": [r("darby_zaklad", "undertaker")]},
        {"id": "wiersz", "title": "Wiersz przewidział koniec poza jednym", "setup": [r("wiersz", "side by side")],
         "clues": [r("dym", "rounds")], "payoff": [r("pogrzeby", "cemeteries")]},
        {"id": "teczka", "title": "Wycinki trafią do jednej teczki", "setup": [r("teczka_zasiew", "file")],
         "payoff": [r("hak_teczka", "file"), r("koniec", "file")]},
        {"id": "przysiega", "title": "Clyde nie wróci do Eastham", "setup": [r("przysiega", "swore")],
         "clues": [r("odbicie", "Eastham")], "payoff": [r("podkreslenie", "promise")]},
        {"id": "matki", "title": "Pętle prowadzą do matek", "setup": [r("rodziny", "families")], "clues": [r("sowers", "picnics"),
         r("petle", "mothers")], "payoff": [r("shreveport", "father's farm"), r("zasadzka_rano", "truck")]},
        {"id": "obietnica", "title": "Łowca, który nie gonił", "setup": [r("obietnica", "without ever chasing")],
         "clues": [r("poscigi", "ditch")], "payoff": [r("hak_szuflada", "stopped chasing")]},
        {"id": "methvin", "title": "Henry Methvin", "setup": [r("odbicie", "free his friends")], "payoff": [r("methvin", "Henry Methvin")]},
    ],
    "spoilers": [
        {"pattern": "Hamer", "notBefore": r("hamer", "Frank Hamer"), "why": "Łowca jest tajemnicą do aktu V (obietnica mówi „a retired Ranger”)."},
        {"pattern": "Methvin", "notBefore": r("methvin", "Ivy Methvin"), "why": "Zdrajca pojawia się dopiero w akcie VII."},
        {"pattern": "embalm", "notBefore": r("darby_zaklad", "undertaker"), "why": "Klamra Darby'ego dopiero w akcie VIII."},
    ],
    "decisions": [
        {"id": "D1", "text": "Film według szkicu D: oś A (prasa kontra prawda) z wplecionym B (pościg Hamera), opowieść wydłużona do ok. "
         "18 minut. Reżyser 19.11.2026: „Robimy A, ale wplatamy gdzieś te B, wydłużając opowieść”, potem „Tak, zatwierdzam D”.",
         "at": "2026-11-19", "by": "reżyser"},
        {"id": "D2", "text": "Ton: lekki humor jako ironia i suchy lektor; z ofiar się nie żartuje, każda ofiara ma imię, śmierć w teatrze "
         "cieni bez krwi; od Grapevine ton poważny (reżyser 18.11.2026: „lekko humorystycznie”).", "at": "2026-11-18", "by": "reżyser"},
        {"id": "D3", "text": "Film tylko po angielsku na kanał Paper Theatre; napisy w kadrze po angielsku; dla Polaków polski tytuł, opis "
         "i ewentualnie ścieżka lektora.", "at": "2026-11-18", "by": "reżyser"},
        {"id": "D4", "text": "Sceneria lat 30. w USA rysowana od nowa (preria, Ford V8, stacje, drukarnia, lasy Luizjany) — bez krajobrazu "
         "Chin i Japonii (zasada sceneria-na-film).", "at": "2026-11-19", "by": "reżyser"},
        {"id": "D5", "text": "Fakty z relacji wtórnych mają w kwestii zastrzeżenie: „reportedly”, „local historians say”, „according to local "
         "accounts”; wiersz Bonnie tylko parafrazowany; list do Forda jako niepewny.", "at": "2026-11-19", "by": "Claude"},
    ],
}

BIBLIA = {
    "characters": "Bonnie Parker — drobna, jasne kręcone włosy, beret, sukienka do kolan; od Wellington kuleje (bandaż). Clyde Barrow — "
                  "fedora, garnitur, od Eastham kuleje. Buck (kaszkiet, kamizelka), Blanche (kapelusik, biały piesek), W.D. Jones (chudy, "
                  "kaszkiet). Frank Hamer — wysoki, Stetson, długi płaszcz. Darby — czarny garnitur, muszka. Ivy Methvin — broda, "
                  "ogrodniczki. Policjanci w mundurach i czapkach, więźniowie w pasiakach, tłum w płaszczach i kapeluszach lat 30.",
    "chronology": "1909/1910 urodziny Clyde'a i Bonnie · lata 20. West Dallas · 1926 ślub Bonnie i Roya · styczeń 1930 spotkanie · marzec "
                  "1930 Waco i Ohio · 1930–32 Eastham · luty 1932 zwolnienie · kwiecień 1932 Kaufman i Hillsboro · sierpień 1932 Atoka · "
                  "grudzień 1932 W.D. · marzec 1933 Buck · 13.04.1933 Joplin · 27.04.1933 Darby · 10.06.1933 Wellington · lipiec 1933 "
                  "Platte City i Dexfield · listopad 1933 Sowers · 16.01.1934 Eastham · 10.02.1934 Hamer (dzień 1) · 1.04.1934 Grapevine "
                  "(dzień 50) · 6.04.1934 Commerce · maj 1934 wiersz · 21.05 Shreveport · 22–23.05.1934 zasadzka (dzień 102) · 1967 film · "
                  "1988 śmierć Blanche · 2026 gra wideo.",
    "narration": "Lektor po angielsku w 3. osobie, czas przeszły, suchy i ironiczny; pełne zdania z łącznikami (then, so, but, because, "
                 "while, when, until). Długość ujęcia z kwestii: oddech 0,6 s + słowa / 2,84 + pauza 1,1–2,3 s (w haku szybciej). "
                 "Ofiary mają imiona; od Grapevine bez żartów.",
    "visuals": "Teatr papierowy jak „Pierwszy cesarz” i „Syn słońca”: wycinki na planach głębi, kamera wieloplanowa (paralaksa), cienie "
               "między planami, ciepłe światło, głębia ostrości. Rama teatru oklejona gazetami z lat 30., szyld art déco. Lalki wycinane "
               "kodem (głowa, strój lat 30., ręce na zawiasie). Nic nie pojawia się znikąd: rzeczy zjeżdżają na nitkach albo wysuwają "
               "się zza rampy. Śmierć w teatrze cieni za parawanem.",
    "facts": "PBS American Experience „Bonnie & Clyde”; FBI History; 64 Parishes (zasadzka); Tyler Paper (Maree Tullis, relacja lokalna); "
             "funeralwise (Darby, relacje wtórne); relacje o komendancie Boydzie (wtórne). Do potwierdzenia przed publikacją: 5 dolarów "
             "dla porwanych, 6 dni między palcami a zwolnieniem, kanapka i skarpetki, ok. 20 tys. na pogrzebie, „co najmniej 9 "
             "stróżów prawa”.",
    "transitions": "Kurtyna między aktami z pytaniem; ściemnienie przy zmianie miejsca w akcie; zapowiedź cięta bez przejść; teatr cieni "
                   "jako osobna dekoracja (parawan).",
}

WARSZTAT = {
    "pipeline": "## Technika\n\nUjęcia są **rysowane kodem** w Pythonie (PIL + numpy) jako teatr papierowy — ten sam silnik co "
                "„Pierwszy cesarz” i „Syn słońca”.\n\n"
                "- **Silnik** (`output/pierwszy-cesarz/papier.py`, wspólny): plany głębi, kamera, cienie, głębia ostrości, światło.\n"
                "- **Papiery i wycinki wspólne** (`output/pierwszy-cesarz/zestaw.py`): faktury, darte krawędzie, chmury, nitki, wysuwanie.\n"
                "- **Zestaw filmu** (`output/bonnie-i-clyde/zestaw_bc.py`): lalki lat 30. z rękami na zawiasie, rama teatru z gazet, "
                "Ford V8, radiowóz, motocykl, ciężarówka, stacja, drukarnia, gazety, aparat, mapa, preria, miasteczko, wnętrza, "
                "więzienie, las, parawan teatru cieni.\n"
                "- **Świat** (`output/bonnie-i-clyde/scena.py`): stan sceny i scenografie.\n"
                "- **Ujęcia** (`ujecia_a.py` — akty 0–4, `ujecia_b.py` — akty 5–8): funkcja `s_<klucz>(st, w, t, T)`.\n"
                "- **Podgląd na żywo** (`na_zywo.py`): Studio rysuje ujęcia z kodu (legacy.teatr), klipów mp4 nie rysuje się.\n"
                "- **Dźwięk** (`efekty.py`, `glosy.py`, `probka_dzwieku.py`): tematy muzyczne lat 30., efekty z podsłuchu ujęć, głosy "
                "z syntetycznych głosów Kokoro + Chatterbox Turbo (bez głosu reżysera) — Podręcznik → Dźwięk.",
    "method": "## Kolejność pracy\n\n"
              "1. Rozpiska: `docs/filmy/bonnie-i-clyde/ujecia/dane.py` (z zatwierdzonego szkicu D).\n"
              "2. Księga świata: `ujecia/ksiega.py`.\n"
              "3. `python3 output/bonnie-i-clyde/studio_film.py plan` — plan, księga i warsztat do Studio + kontrola ciągłości.\n"
              "4. Rysunek: funkcja ujęcia; `python3 output/bonnie-i-clyde/render.py arkusz 12,13` — arkusz klatek.\n"
              "5. `python3 output/bonnie-i-clyde/render.py kontrola` — test „końca świata”.\n"
              "6. Podgląd na żywo w Studio (zakładka Ujęcia); `studio_film.py klatki` — zapasowe klatki na osi.\n"
              "7. Dźwięk: `python3 -I output/bonnie-i-clyde/efekty.py` (przegląd filmu, muzyka i efekty), nowy rodzaj dźwięku → "
              "`probka_dzwieku.py` i zgoda reżysera, potem `studio_film.py dzwiek`; po każdej zmianie długości ujęć: `plan`, "
              "`klatki`, dźwięk od nowa.\n"
              "8. Recenzja aktu i wpis w dzienniku. Lektor tylko za zgodą reżysera (reżyser nagrywa sam na końcu).\n"
              "9. Humor: propozycje gagów w `docs/filmy/bonnie-i-clyde/GAGI.md` (Podręcznik → Humor i gagi); reżyser wybiera "
              "skrótem, wybrane idą do rozpiski, gagi powracające do księgi świata.",
    "files": [
        {"path": "docs/filmy/bonnie-i-clyde/szkice/buduj_szkice.py", "role": "szkice A–D (D zatwierdzony)"},
        {"path": "docs/filmy/bonnie-i-clyde/ujecia/dane.py", "role": "rozpiska: akty, sceny, ujęcia, kwestie EN"},
        {"path": "docs/filmy/bonnie-i-clyde/ujecia/ksiega.py", "role": "księga świata, Story Bible i warsztat"},
        {"path": "docs/filmy/bonnie-i-clyde/GAGI.md", "role": "propozycje gagów na akty (do wyboru przez reżysera)"},
        {"path": "output/bonnie-i-clyde/zestaw_bc.py", "role": "lalki lat 30. i wycinanki filmu"},
        {"path": "output/bonnie-i-clyde/scena.py", "role": "stan świata i scenografie"},
        {"path": "output/bonnie-i-clyde/ujecia_a.py", "role": "ujęcia aktów 0–4"},
        {"path": "output/bonnie-i-clyde/ujecia_b.py", "role": "ujęcia aktów 5–8"},
        {"path": "output/bonnie-i-clyde/render.py", "role": "klatka, arkusz, kontrola, klipy"},
        {"path": "output/bonnie-i-clyde/na_zywo.py", "role": "podgląd na żywo w Studio"},
        {"path": "output/bonnie-i-clyde/studio_film.py", "role": "plan, księga, klatki i dźwięk do Studio"},
        {"path": "output/bonnie-i-clyde/efekty.py", "role": "muzyka (tematy, CUES, CISZA) i efekty (podsłuch ujęć, ZDARZENIA, głosy)"},
        {"path": "output/bonnie-i-clyde/glosy.py", "role": "głosy ludzi: referencje Kokoro, nagrania Turbo, wybór podejść"},
        {"path": "output/bonnie-i-clyde/probka_dzwieku.py", "role": "próbka do akceptacji: fragmenty filmu z miksem i sam dźwięk"},
    ],
}

if __name__ == "__main__":
    (HERE.parent / "swiat.json").write_text(json.dumps(SWIAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE.parent / "warsztat.json").write_text(json.dumps(WARSZTAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("zapisano swiat.json i warsztat.json")
