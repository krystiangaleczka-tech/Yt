"""Księga świata, Story Bible i warsztat filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune”.

  python3 -I docs/filmy/szamil-diuna/ujecia/ksiega.py    — zapisuje ../swiat.json i ../warsztat.json (kopia do historii gita)

Odwołania do ujęć powstają z kluczy rozpiski (`r("zakladnik", "hostage")` → `d01_08~hostage`), więc dopisanie ujęcia ich nie
psuje. Miejscem pracy jest Studio (Continuity Editor → Świat / Warsztat); wgrywa je output/szamil-diuna/studio_film.py.
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
    # film krótki (ok. 5:30): akty 45–90 s; prolog to jednostka 0 wewnątrz aktu 1 (world.prologue ustawia studio_film.py)
    "tempo": {"minSeconds": 40, "maxSeconds": 95, "maxVoiceShare": 0.85},
    "places": [
        {"id": "teatr", "name": "Teatr papierowy", "note": "Rama z ciemnego rzeźbionego drewna z ornamentem kaukaskim; z lewej wydma "
         "(Arrakis), z prawej góry (Kaukaz) — dwie połowy sceny, które wracają w puencie.", "connects": ["gory", "pustynia"]},
        {"id": "gory", "name": "Góry Dagestanu", "note": "Ośnieżone granie, wąwozy, kamienne auły przyklejone do zboczy, mgła z bibuły; "
         "odmiany: Gimry, Achulgo (skała z twierdzą nad zakolem rzeki), Wedeno (stolica w lesie), Gunib (płaskowyż w urwiskach).",
         "connects": ["rzeka", "gruzja"]},
        {"id": "rzeka", "name": "Rzeki", "note": "Rzeka pod Achulgo nocą (ucieczka, tratwa) i rzeka Miczik w marcu 1855 (bród, wymiana)."},
        {"id": "gruzja", "name": "Cinandali (Gruzja)", "note": "Dwór z drewnianym balkonem, winnice, kamienny mur."},
        {"id": "petersburg", "name": "Petersburg", "note": "Złote iglice, śnieżna droga, sala balowa z kolumnami i żyrandolem, pałac cara."},
        {"id": "pustynia", "name": "Pustynia", "note": "Wydma (hak i puenta), droga pielgrzymki do Medyny, słowa nad wydmą."},
        {"id": "pracownia", "name": "Pracownie pisarzy", "note": "Biurko Lesley Blanch (Londyn, 1960) i stół Franka Herberta (1965)."},
    ],
    "characters": [
        {"id": "szamil", "name": "Imam Shamil", "aliases": ["Shamil"], "role": "trzeci imam Dagestanu (1834–1859), przywódca oporu",
         "look": "orli profil, broda (czarna → siwa od " + r("kapitulacja", "starszy") + "), biały turban na papasze, czarna czerkieska, "
         "kindżał u pasa", "namedIn": ["d*"],
         "states": [{"from": r("kapitulacja", "starszy"), "state": "62 lata, siwa broda, bez broni"}]},
        {"id": "dzamaluddin", "name": "Jamal al-Din", "role": "pierworodny syn Szamila, zakładnik", "look": "jako chłopiec: mała "
         "lalka w papasze; od " + r("kadet", "oficer") + " wysoki młody oficer z wąsikiem w rosyjskim mundurze; od "
         + r("mundur", "czerkieskę") + " w czarnej czerkiesce", "namedIn": ["d01_*", "d02_*"],
         "joins": r("zakladnik", "Jamal al-Din"), "leaves": r("swieca", "gaśnie"),
         "states": [{"from": r("chlopiec", "chłopiec"), "state": "zakładnik u Rosjan"},
                    {"from": r("kadet", "oficer"), "state": "dorosły oficer carskiej armii"},
                    {"from": r("przeprawa_syn", "uniform"), "state": "z powrotem u ojca"},
                    {"from": r("swieca", "gaśnie"), "state": "nie żyje (1858)"}]},
        {"id": "ghazi", "name": "Ghazi Muhammad", "role": "syn Szamila, dowódca najazdu na Cinandali", "look": "młody jeździec w czerni"},
        {"id": "anna", "name": "Princess Anna Chavchavadze", "role": "żona księcia Dawida Czawczawadze, wnuczka ostatniego króla Gruzji",
         "look": "biały czepiec, ciemna suknia"},
        {"id": "warwara", "name": "Princess Varvara Orbeliani", "role": "siostra Anny, wdowa", "look": "biały czepiec, szara suknia"},
        {"id": "bariatinski", "name": "Prince Baryatinsky", "role": "namiestnik Kaukazu, przyjmuje kapitulację",
         "look": "mundur generalski, siedzi na kamieniu pod brzozą"},
        {"id": "car", "name": "Tsar Alexander II", "role": "car Rosji (od 1855)", "look": "mundur, bokobrody"},
        {"id": "muridzi", "name": "muridzi", "role": "wojownicy Szamila", "look": "czarne czerkieski, papachy, szable"},
        {"id": "blanch", "name": "Lesley Blanch", "role": "pisarka, autorka „The Sabres of Paradise” (1960)", "look": "kobieta w "
         "kapeluszu przy maszynie do pisania"},
        {"id": "herbert", "name": "Frank Herbert", "role": "autor „Diuny” (1965)", "look": "mężczyzna z brodą i w okularach przy maszynie"},
    ],
    "props": [
        {"id": "karty", "name": "Dwie karty ze zdaniem o ostrzu", "place": "teatr", "seeded": r("cytat_diuna", "Killing"),
         "uses": [r("cytat_1960", "point"), r("ramka", "lupy"), r("ksiazka", "karty")]},
        {"id": "kindzal", "name": "Kindżał", "owner": "Shamil", "seeded": r("kindzal", "kindżał"),
         "uses": [r("slowo_kindjal", "kindżał"), r("ojciec", "kindżału"), r("ojciec_brzeg", "kindżału"), r("kindjal", "kindżał")]},
        {"id": "biala_flaga", "name": "Biała flaga", "seeded": r("zakladnik", "biała flaga"),
         "uses": [r("flaga", "biała flaga"), r("biala_flaga", "białą flagę")]},
        {"id": "ksiazka_blanch", "name": "„The Sabres of Paradise”", "place": "pracownia", "seeded": r("ksiazka", "SABRES"),
         "uses": [r("blanch", "Sabres")]},
        {"id": "srebro", "name": "40 000 rubli", "seeded": r("cena", "40,000"), "uses": [r("monety", "rublami")]},
        {"id": "mundur", "name": "Rosyjski mundur Dżamaluddina", "owner": "Jamal al-Din", "seeded": r("kadet", "oficer"),
         "uses": [r("przeprawa_syn", "uniform"), r("mundur", "epolety"), r("biala_flaga", "mundurze")]},
    ],
    "resources": [],
    "rules": [
        {"id": "wojna", "name": "Wojna Szamila trwa", "from": r("imam", "imam"), "to": r("kapitulacja", "surrendered"),
         "note": "Od wyboru na imama (1834) do kapitulacji w Gunibie (6.09.1859; 25.08 st. st.) — 25 lat z tytułu."},
        {"id": "syn_u_rosjan", "name": "Syn u Rosjan", "from": r("chlopiec", "chłopiec"), "to": r("przeprawa_syn", "crossed"),
         "note": "Od Achulgo (1839) do wymiany na rzece Miczik (marzec 1855)."},
    ],
    "events": [
        {"at": r("rzeka", "Michik"), "needs": ["syn_u_rosjan"], "note": "Wymiana ma sens tylko, gdy syn jest jeszcze u Rosjan."},
    ],
    "threads": [
        {"id": "zdanie", "title": "Dwa zdania o ostrzu", "setup": [r("cytat_diuna", "Killing")],
         "clues": [r("cytat_1960", "sentence"), r("ksiazka", "book")], "payoff": [r("blanch", "Sabres")],
         "note": "Hak: zdanie z Diuny i z książki z 1960; rozwiązanie: kim była autorka i skąd Herbert wziął słowa."},
        {"id": "syn", "title": "Syn zakładnik", "setup": [r("zakladnik", "hostage")],
         "clues": [r("petersburg", "officer"), r("koniec_aktu1", "back"), r("cena", "son")], "payoff": [r("przeprawa_syn", "crossed")],
         "note": "Pytanie z końca aktu I („no way to get him back”) — odpowiedź w akcie II."},
        {"id": "pytanie", "title": "Jak wojna w górach trafiła na pustynną planetę", "setup": [r("pytanie", "desert planet")],
         "clues": [r("blanch", "Sabres")], "payoff": [r("herbert", "Dune")]},
        {"id": "siridar", "title": "Siridar — słowo Szamila na carskiego namiestnika", "setup": [r("kapitulacja", "siridar")],
         "payoff": [r("tytuly", "siridar")], "note": "Szkic D: przy kapitulacji pada słowo, w akcie IV wraca jako puenta listy."},
        {"id": "slowa_kurtyny", "title": "Słowo z Diuny na początku każdego aktu", "setup": [r("slowo_kindjal", "KINDJAL")],
         "clues": [r("koniec_aktu1", "KANLY"), r("samotny", "SIRIDAR"), r("medyna", "SIETCH")],
         "payoff": [r("kanly", "Kanly"), r("sietch", "Sietch")],
         "note": "Szkic D: słowa na kurtynach wracają w akcie IV z wyjaśnieniem. Przypisanie słowa do aktu jest nasze — lektor "
                 "nie twierdzi, że słowo pochodzi z tego wydarzenia (D4)."},
        {"id": "flaga", "title": "Biała flaga", "setup": [r("zakladnik", "biała flaga")], "clues": [r("flaga", "biała flaga")],
         "payoff": [r("biala_flaga", "white flag")], "note": "Flaga przy oddaniu syna wraca przy kapitulacji i w puencie."},
    ],
    "spoilers": [
        {"pattern": "Gunib", "notBefore": r("gunib", "Gunib"), "why": "Koniec wojny dopiero w akcie III (zapowiedź pokazuje tylko flagę)."},
        {"pattern": "surrender", "notBefore": r("kapitulacja", "surrendered"), "why": "Kapitulacja to kulminacja aktu III."},
        {"pattern": "Herbert", "notBefore": r("herbert", "Herbert"), "why": "Nazwisko autora Diuny pada przy jego wejściu w akcie IV."},
    ],
    "decisions": [
        {"id": "D1", "at": "2026-11-27", "by": "reżyser", "text": "Tytuł główny: „The Imam Who Fought Russia for 25 Years — and "
         "Ended Up in Dune” (wariant 3 z rozmowy; reżyser: „tytuł ten z rosją 25 years czyli 3 jako główny pierwszy”); "
         "zapasowe do testu A/B: „The Real Holy War Hidden Inside Dune”, „Dune Borrowed Its Words From a Real War”."},
        {"id": "D2", "at": "2026-11-27", "by": "reżyser", "text": "Film krótki (test formatu 4–5 min) z gęstym montażem: ok. 70 ujęć, "
         "zbliżenia, detale i Ken Burns na prawdziwych obrazach XIX w. — zawsze z wydarzeniem w środku (Rytm 1)."},
        {"id": "D3", "at": "2026-11-27", "by": "wykonawca", "text": "Ton czysto historyczny: Szamil jest symbolem dla Czeczenów "
         "i Dagestańczyków, w tle islam i Rosja — bez polityki współczesnej, bez ocen."},
        {"id": "D4", "at": "2026-11-27", "by": "wykonawca", "text": "Udokumentowane są słowa i zdania (esej Collinsa, LARB 2017), nie "
         "cała fabuła. Film nie mówi „Paul to Szamil” ani „Herbert ukradł”; zastrzeżenie pada w akcie IV."},
        {"id": "D5", "at": "2026-11-27", "by": "wykonawca", "text": "Prawa autorskie: żadnych postaci, kadrów ani okładek z filmów "
         "Villeneuve'a i z wydań książek; cytaty z powieści krótkie, na naszych kartach z maszynopisem. Ken Burns tylko po plikach "
         "oznaczonych jako domena publiczna (Horschelt 1863, fotografia Szamila 1859)."},
        {"id": "D6", "at": "2026-11-28", "by": "reżyser", "text": "Kalendarz gregoriański w całym filmie (fact-check ChatGPT "
         "przekazany przez reżysera 28.11): kapitulacja 6.09.1859 (25.08 st. st.) → „That September”; wymiana 22.03.1855 "
         "(10.03 st. st.) → „March 1855”; najazd lipiec 1854 → „summer of 1854”. Wiek syna przy Achulgo: 6 (NPLG), ok. 7 "
         "(Central Asian Survey), 8 (Blanch), 12 (Wikipedia) → „still a boy”, lalka małego dziecka; niewola księżnych 8–9 "
         "miesięcy → „for months”."},
        {"id": "D8", "at": "2026-11-28", "by": "reżyser", "text": "Zatwierdzony szkic D „Dwa zdania, trop słów i rzeka” zamiast A "
         "(reżyser: „Zatwierdzam”, po porównaniu A z podejściami „Trop słów” i „Syn między dwoma światami”): słowo z Diuny na "
         "początku każdego aktu (KINDJAL, KANLY, SIRIDAR, SIETCH), „siridar” przy kapitulacji jako zasiew puenty aktu IV, "
         "wymiana na rzece jako emocjonalny szczyt (zbliżenia, „almost sixteen years”, cisza przed uściskiem). 76 ujęć, 5:55."},
        {"id": "D7", "at": "2026-11-28", "by": "reżyser", "text": "Poprawki z fact-checku 28.11: (1) karta z Diuny dopiero po "
         "sprawdzeniu w wydaniu — źródła cytują „tip” albo „point”, mówi Duncan Idaho albo Gurney Halleck; lektor nie nazywa "
         "nauczyciela; (2) zapowiedź mówi o historii wojny, nie że Diuna wzięła słowa „od imama”; (3) wymiana na rzece to nie "
         "„dwie księżne za syna”: z księżnymi były dzieci i służba, Szamil żądał więcej, stanęło na synu, 40 000 rubli "
         "w srebrze i wymianie jeńców; (4) obrazy do Ken Burnsa tylko z plików Commons oznaczonych jako domena publiczna "
         "(Horschelt 1863, Denier 1859); ilustracja wymiany z Met (nr 423472) tylko jako wzór rysunku."},
    ],
}

BIBLIA = {
    "characters": "Imam Szamil (ur. 1797 w Gimry, Awar; imam 1834–1859) — orli profil, broda czarna, w akcie III siwa; biały turban na "
                  "papasze, czarna czerkieska, kindżał. Dżamaluddin — chłopiec w papasze (1839), potem wysoki oficer w rosyjskim "
                  "mundurze, po wymianie w czerkiesce; umiera 1858. Ghazi Muhammad — syn Szamila, dowódca najazdu. Księżne Anna "
                  "Czawczawadze i Warwara Orbeliani (białe czepce) z dziećmi. Książę Bariatinski (mundur generalski), car "
                  "Aleksander II. Muridzi w czarnych czerkieskach. Lesley Blanch (pisarka), Frank Herbert (broda, okulary). Jedna "
                  "postać = jedna lalka; zmiana wieku = wymiana lalki w kadrze (Wytyczne 1.15).",
    "chronology": "1797 urodziny Szamila · 1834 imam · 1839 Achulgo: syn zakładnikiem, ucieczka nocą · lata 40. syn w Petersburgu · "
                  "lato 1854 najazd na Cinandali · do marca 1855 księżne w Wedeno · 22.03.1855 (10.03 st. st.) wymiana na rzece Miczik (syn, 40 000 "
                  "rubli w srebrze, wymiana jeńców) · 1858 śmierć syna · 6.09.1859 (25.08 st. st.) kapitulacja w Gunibie przed Bariatinskim · wygnanie "
                  "w Kałudze · 1871 śmierć w Medynie · 1960 „The Sabres of Paradise” · 1965 „Diuna” · grudzień 2026 trzecia "
                  "„Diuna” w kinach (ekranizacja „Mesjasza Diuny”).",
    "narration": "Lektor po angielsku, 3. osoba, czas przeszły, spokojny i poważny; pełne zdania z łącznikami (then, but, so, when). "
                 "Długość ujęcia z kwestią: oddech 0,6 s (w haku 0,4) + słowa / 2,84 + pauza 1,1–2,3 s; ujęcia bez słów 1,4–3,7 s. "
                 "Lektor od pierwszej sekundy na zapowiedzi; hak to dwa zdania; jedno pytanie prowadzi w retrospekcję; bez "
                 "kurtyny przed aktem I. Nie mówimy „Paul to Szamil” ani „Herbert ukradł”.",
    "visuals": "Teatr papierowy jak „Pierwszy cesarz”, „Syn słońca” i „Bonnie and Clyde”: wycinki na planach głębi, kamera wieloplanowa, "
               "nitki, kurtyna z pytaniem między aktami. Scena podzielona: wydma (Arrakis) z lewej, góry Kaukazu z prawej. Paleta: "
               "piaskowe ochry i złoto pustyni kontra granat, biel śniegu i czerń czerkiesek; zieleń islamu tylko na chorągwiach "
               "imamatu. Nowa sceneria, nic z poprzednich filmów (góry kaukaskie, auły, winnice, sala balowa). Ken Burns po "
               "prawdziwych obrazach XIX w. zawsze z papierowym wydarzeniem w środku. Rysuj pod telefon: duże lalki, mało drobnego "
               "tekstu.",
    "facts": "Daty według kalendarza gregoriańskiego (D6). Will Collins, „The Secret History of Dune”, Los Angeles Review of Books, 16.09.2017 (słowa: chakobsa, kanly, kindjal, sietch, "
             "tabr, padishah, siridar; zdania o ostrzu i o mądrości z gór/pustyni). Wikipedia: Imam Shamil, Siege of Akhoulgo, "
             "Battle of Ghunib, Russian conquest of Chechnya and Dagestan, Chavchavadze (wymiana 10.03.1855, 40 000 rubli). "
             "Gruzińska Biblioteka Narodowa (nplg.gov.ge) — Cinandali i niewola księżnych. Kara Kennedy, „Frank Herbert's Dune: A "
             "Critical Companion” (Palgrave, 2022) — do sprawdzenia w indeksie, czy pisze o Blanch. Rozbieżności: wiek syna (6–12), "
             "dzień najazdu (2/4 lipca 1854). Do sprawdzenia przed nagraniem: oba cytaty w samych książkach z numerem strony "
             "(w Diunie „tip” czy „point”, Duncan Idaho czy Gurney). Obrazy: Commons Horschelt 1863 i Denier 1859 (domena "
             "publiczna). Szamil nie jest udowodnionym pierwowzorem Paula; Herbert nie potwierdził inspiracji Szamilem wprost.",
    "transitions": "Zapowiedź bez przejść; kurtyna startu; prolog → akt I przez zapadającą się wydmę i zawieszkę „Dagestan, 1834” "
                   "(bez kurtyny); kurtyny z pytaniem przed aktami II–IV; ściemnienie przy zmianie miejsca w akcie; nitki ze słowami "
                   "przechodzą z gór nad wydmę (akt IV); słowo z Diuny otwiera każdy akt (KINDJAL na początku aktu I, KANLY / "
                   "SIRIDAR / SIETCH na kurtynach nad pytaniem — szkic D); biała flaga łączy zakładnika, kapitulację i puentę.",
}

WARSZTAT = {
    "pipeline": "## Technika\n\nUjęcia będą **rysowane kodem** w Pythonie jako teatr papierowy — silnik „Pierwszego cesarza” "
                "(`output/pierwszy-cesarz/papier.py`, `zestaw.py`) i sposób pracy „Bonnie and Clyde” (podgląd na żywo, "
                "`uklad.py` przy rekwizytach w dłoniach).\n\n"
                "- **Zestaw filmu** (do zrobienia, `output/szamil-diuna/zestaw_kz.py`): lalki kaukaskie (czerkieski, papachy, "
                "kindżały), rosyjskie mundury, księżne, sala balowa, góry i auły, winnice, rzeka, wydma, karty z maszynopisem, "
                "słowa na nitkach.\n"
                "- **Świat** (`scena.py`), **ujęcia** (`ujecia_a.py` — akty 0–2, `ujecia_b.py` — akty 3–4), **podgląd na żywo** "
                "(`na_zywo.py`), **dźwięk** (`efekty.py`).\n"
                "- **Ken Burns**: pliki domeny publicznej z Wikimedia Commons (Horschelt 1863, fotografia 1859) w "
                "`output/szamil-diuna/obrazy/` z zapisaną licencją.",
    "method": "## Kolejność pracy\n\n"
              "1. Szkice A/B/C: `python3 -I docs/filmy/szamil-diuna/szkice/buduj_szkice.py` → import w Studio (etap Szkice ujęć).\n"
              "2. Rozpiska: `docs/filmy/szamil-diuna/ujecia/dane.py` (z zatwierdzonego szkicu).\n"
              "3. Księga świata: `ujecia/ksiega.py`.\n"
              "4. `python3 -I output/szamil-diuna/studio_film.py plan` — plan, księga i warsztat do Studio + kontrola ciągłości.\n"
              "5. Rysunek po aktach, arkusz klatek, kontrola (Wytyczne 3), podgląd na żywo.\n"
              "6. Dźwięk (próbka do akceptacji), lektor (klon, jedno podejście na kwestię), recenzja aktu i dziennik.",
    "files": [
        {"path": "docs/filmy/szamil-diuna/szkice/buduj_szkice.py", "role": "szkice A–C"},
        {"path": "docs/filmy/szamil-diuna/ujecia/dane.py", "role": "rozpiska: akty, sceny, ujęcia, kwestie EN"},
        {"path": "docs/filmy/szamil-diuna/ujecia/ksiega.py", "role": "księga świata, Story Bible i warsztat"},
        {"path": "output/szamil-diuna/studio_film.py", "role": "plan, księga i rozwój filmu do Studio"},
    ],
}

if __name__ == "__main__":
    (HERE.parent / "swiat.json").write_text(json.dumps(SWIAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE.parent / "warsztat.json").write_text(json.dumps(WARSZTAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("zapisano swiat.json i warsztat.json")
