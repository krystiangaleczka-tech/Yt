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
    # szkic E (28.11): akty 60–115 s z tempa rozpiski; z prawdziwym lektorem (D12) 64–125 s — górna granica 130 s;
    # prolog to jednostka 0 wewnątrz aktu 1 (world.prologue ustawia studio_film.py)
    "tempo": {"minSeconds": 55, "maxSeconds": 130, "maxVoiceShare": 0.85},
    "places": [
        {"id": "teatr", "name": "Teatr papierowy", "note": "Rama z ciemnego rzeźbionego drewna; prolog i puenta: wydma (Arrakis) "
         "i góry Kaukazu obok siebie; maszynista za kulisami (laska z hakiem).", "connects": ["gory", "pustynia"]},
        {"id": "gory", "name": "Góry Dagestanu i Czeczenii", "note": "Gimry (wąwóz z wieżą), auł na grani, Achulgo (skała z twierdzą "
         "nad rzeką), bukowe lasy Czeczenii, Dargo (spalone), Wedeno, Gunib (płaskowyż w urwiskach).", "connects": ["rzeka", "gruzja"]},
        {"id": "rzeka", "name": "Rzeki", "note": "Rzeka pod Achulgo nocą (tratwa) i rzeka Miczik w marcu 1855 (bród, wymiana)."},
        {"id": "gruzja", "name": "Cinandali (Gruzja)", "note": "Dwór z balkonem, winnice, kamienny mur."},
        {"id": "petersburg", "name": "Petersburg", "note": "Gabinet z mapą i biurkiem z pieczątką, sala balowa, sala tronowa, iglice."},
        {"id": "kaluga", "name": "Kaługa", "note": "Dom z kolumienkami i płotem, za płotem gapie."},
        {"id": "pustynia", "name": "Pustynia", "note": "Arrakis z robakiem (prolog, puenta), droga pielgrzymki do Medyny."},
        {"id": "pracownia", "name": "Pracownie pisarzy", "note": "Biurko Lesley Blanch (Londyn, 1960) i stół Franka Herberta (1965)."},
    ],
    "characters": [
        {"id": "szamil", "name": "Imam Shamil", "aliases": ["Shamil"], "role": "trzeci imam Dagestanu (1834–1859), przywódca oporu",
         "look": "orli profil, broda (czarna → siwa od " + r("gunib", "siwą brodą") + "), biały turban na papasze, czarna czerkieska, "
         "kindżał u pasa", "namedIn": ["d*"],
         "states": [{"from": r("rana", "ręka przy piersi"), "state": "ranny bagnetem (1832)"},
                    {"from": r("imam", "zdrowy"), "state": "imam"},
                    {"from": r("gunib", "siwą brodą"), "state": "62 lata, siwa broda"},
                    {"from": r("kapitulacja", "surrendered"), "state": "w niewoli honorowej"}]},
        {"id": "ghazi_imam", "name": "Ghazi Muhammad", "role": "pierwszy imam Dagestanu, nauczyciel Szamila, ginie w Gimry 1832",
         "look": "szara czerkieska, papacha", "namedIn": ["d01_*"], "joins": r("gimry", "Ghazi Muhammad"),
         "leaves": r("wieza", "was killed")},
        {"id": "dzamaluddin", "name": "Jamal al-Din", "role": "pierworodny syn Szamila, zakładnik", "look": "jako chłopiec: mała "
         "lalka w papasze; od " + r("kadet", "oficer") + " wysoki oficer z wąsikiem w rosyjskim mundurze; od "
         + r("mundur", "czerkieskę") + " w czarnej czerkiesce", "namedIn": ["d02_*", "d04_*"],
         "joins": r("amanat", "Jamal al-Din"), "leaves": r("smierc", "died"),
         "states": [{"from": r("chlopiec", "boy"), "state": "zakładnik u Rosjan"},
                    {"from": r("kadet", "oficer"), "state": "dorosły oficer carskiej armii"},
                    {"from": r("syn_wraca", "uniform"), "state": "wraca do ojca"},
                    {"from": r("smierc", "died"), "state": "nie żyje (1858)"}]},
        {"id": "syn_drugi", "name": "Shamil's second son", "role": "syn Szamila, dowódca najazdu na Cinandali (imię jak pierwszy imam — "
         "lektor go nie nazywa, żeby nie mylić z Ghazim Muhammadem z aktu I)", "look": "młody jeździec w czerni"},
        {"id": "nikolaj", "name": "Tsar Nicholas I", "role": "car do 1855", "look": "mundur, łysiejący, bokobrody",
         "namedIn": ["d01_*"]},
        {"id": "woroncow", "name": "Count Vorontsov", "role": "namiestnik i dowódca wyprawy na Dargo 1845",
         "look": "mundur generalski, kapelusz z ogromnym pióropuszem", "namedIn": ["d03_*"]},
        {"id": "urzednik", "name": "urzędnik z pieczątką", "role": "Petersburg: stempluje raporty z gór (gag powracający)",
         "look": "czarny frak, okulary; w 1859 siwy"},
        {"id": "tolstoj", "name": "Leo Tolstoy", "role": "młody ochotnik w armii rosyjskiej na Kaukazie (1851–1854), pisarz",
         "look": "czapka kadeta, zeszyt", "namedIn": ["d03_*"]},
        {"id": "anna", "name": "Princess Anna Chavchavadze", "role": "żona księcia Dawida Czawczawadze, wnuczka ostatniego króla Gruzji",
         "look": "biały czepiec, ciemnoczerwona suknia"},
        {"id": "warwara", "name": "Princess Varvara Orbeliani", "role": "siostra Anny, wdowa", "look": "biały czepiec, szara suknia"},
        {"id": "guwernantka", "name": "French governess", "role": "Anna Drancy, guwernantka dzieci; jej książka ukazała się w 1857",
         "look": "czarna suknia, kok"},
        {"id": "bariatinski", "name": "Prince Baryatinsky", "role": "namiestnik Kaukazu, przyjmuje kapitulację",
         "look": "mundur generalski, siedzi na kamieniu pod brzozą"},
        {"id": "car", "name": "Tsar Alexander II", "role": "car Rosji (od 1855)", "look": "mundur, bokobrody"},
        {"id": "muridzi", "name": "muridzi", "role": "wojownicy Szamila", "look": "czarne czerkieski, papachy, szable"},
        {"id": "koza", "name": "koza", "role": "gag powracający", "look": "biało-szara koza z bródką"},
        {"id": "fremen", "name": "fremeni", "role": "lalki z Diuny w prologu i w akcie VI (bez twarzy z filmów, D5)",
         "look": "piaskowe płaszcze z kapturami"},
        {"id": "blanch", "name": "Lesley Blanch", "role": "pisarka, autorka „The Sabres of Paradise” (1960)", "look": "kobieta w "
         "kapeluszu przy maszynie do pisania"},
        {"id": "herbert", "name": "Frank Herbert", "role": "autor „Diuny” (1965)", "look": "mężczyzna z brodą i w okularach przy maszynie"},
    ],
    "props": [
        {"id": "kindzal", "name": "Kindżał", "owner": "Shamil", "seeded": r("arrakis", "kindjal"),
         "uses": [r("przedstawienie", "kindżału"), r("chlopiec", "kindżału"), r("kreski", "kindżałem"), r("uscisk", "kindżału"),
                  r("slowa1", "kindjal"), r("zdanie", "kindżał")]},
        {"id": "pieczatka", "name": "Pieczątka urzędnika", "place": "petersburg", "seeded": r("raport", "pieczątka"),
         "uses": [r("zwyciestwo", "pieczątka"), r("stempel", "pieczątka")]},
        {"id": "biala_flaga", "name": "Biała flaga", "seeded": r("amanat", "biała flaga"),
         "uses": [r("rzeka", "biała flaga"), r("szturm_gunib", "biała flaga"), r("biala_flaga", "białą flagę")]},
        {"id": "srebro", "name": "40 000 rubli", "seeded": r("cena", "40,000"), "uses": [r("rzeka", "srebra"), r("przeprawa", "silver")]},
        {"id": "mundur", "name": "Rosyjski mundur Dżamaluddina", "owner": "Jamal al-Din", "seeded": r("kadet", "oficer"),
         "uses": [r("syn_wraca", "uniform"), r("mundur", "epolety"), r("biala_flaga", "mundurze")]},
        {"id": "suchary", "name": "Worki z sucharami", "seeded": r("zwyciestwo", "suchar"), "uses": [r("suchary", "SUKHARI"),
                                                                                                  r("zasadzka", "sucharami")]},
        {"id": "ksiazka_blanch", "name": "„The Sabres of Paradise”", "place": "pracownia", "seeded": r("blanch", "Sabres"),
         "uses": [r("zdanie", "1960")]},
    ],
    "resources": [],
    "rules": [
        {"id": "wojna", "name": "Wojna Szamila trwa", "from": r("imam", "imam"), "to": r("kapitulacja", "surrendered"),
         "note": "Od wyboru na imama (1834) do kapitulacji w Gunibie (6.09.1859; 25.08 st. st.) — 25 lat z tytułu."},
        {"id": "syn_u_rosjan", "name": "Syn u Rosjan", "from": r("chlopiec", "boy"), "to": r("syn_wraca", "uniform"),
         "note": "Od Achulgo (1839) do wymiany na rzece Miczik (marzec 1855)."},
        {"id": "ksiezne_w_niewoli", "name": "Księżne w niewoli", "from": r("ksiezne", "princesses"), "to": r("przeprawa", "princesses"),
         "note": "Od najazdu na Cinandali (lipiec 1854) do wymiany (marzec 1855) — osiem miesięcy."},
    ],
    "events": [
        {"at": r("rzeka", "Michik"), "needs": ["syn_u_rosjan", "ksiezne_w_niewoli"],
         "note": "Wymiana ma sens tylko, gdy syn jest jeszcze u Rosjan, a księżne u Szamila."},
    ],
    "threads": [
        {"id": "syn", "title": "Syn zakładnik", "setup": [r("hak_syn", "hostage")],
         "clues": [r("amanat", "hostage"), r("syn_na_polnoc", "officer"), r("kreski", "son back"), r("cena", "his son")],
         "payoff": [r("syn_wraca", "uniform")], "note": "Hak w prologu (syn oddany, wraca w mundurze) — rozwiązanie w akcie IV."},
        {"id": "pytanie", "title": "Jak wojna w śniegu trafiła na pustynną planetę", "setup": [r("pytanie", "desert planet")],
         "clues": [r("medyna", "desert")], "payoff": [r("herbert", "Dune"), r("slowa1", "Kanly")]},
        {"id": "kanly", "title": "Kanly — wendeta z gór", "setup": [r("arrakis", "kanly")], "clues": [r("kanly_1834", "kanly")],
         "payoff": [r("slowa1", "Kanly")], "note": "Słowo pada w Diunie (prolog), wraca przy śmierci drugiego imama, odlatuje na pustynię w akcie VI."},
        {"id": "padyszach", "title": "Padyszach — słowo Szamila na cara", "setup": [r("cena", "padishah")],
         "payoff": [r("slowa3", "padishah")]},
        {"id": "siridar", "title": "Siridar — słowo Szamila na carskiego namiestnika", "setup": [r("kapitulacja", "siridar")],
         "payoff": [r("slowa3", "siridar")]},
        {"id": "pieczatka", "title": "Pieczątka imperium (gag w trzech podejściach)", "setup": [r("raport", "FINISHED")],
         "clues": [r("zwyciestwo", "VICTORY")], "payoff": [r("stempel", "CAPTURED")],
         "note": "Zasiew: raport o końcu Szamila i kamień przez okno; powtórka: zwycięstwo w pustym Dargo; zwrot: tym razem prawda, bez żartu."},
        {"id": "koza", "title": "Koza (gag w trzech podejściach)", "setup": [r("rana", "koza")], "clues": [r("dargo", "koza")],
         "payoff": [r("kaluga", "koza")]},
        {"id": "robak", "title": "Robak z Diuny na złej scenie", "setup": [r("arrakis", "robak")], "clues": [r("herbert", "robak")],
         "payoff": [r("dzieki", "robak")]},
        {"id": "ksiazki", "title": "Ta wojna trafia do książek", "setup": [r("tolstoj", "stories")], "clues": [r("wedeno", "book")],
         "payoff": [r("blanch", "book")], "note": "Tołstoj (akt III), guwernantka (1857, akt IV), Blanch (1960) — a potem Herbert."},
        {"id": "flaga", "title": "Biała flaga", "setup": [r("amanat", "biała flaga")], "clues": [r("szturm_gunib", "biała flaga")],
         "payoff": [r("biala_flaga", "white flag")]},
    ],
    "spoilers": [
        {"pattern": "Gunib", "notBefore": r("gunib", "Gunib"), "why": "Koniec wojny dopiero w akcie V (zapowiedź pokazuje tylko urwisko)."},
        {"pattern": "surrender", "notBefore": r("kapitulacja", "surrendered"), "why": "Kapitulacja to kulminacja aktu V."},
        {"pattern": "Herbert", "notBefore": r("herbert", "Herbert"), "why": "Nazwisko autora Diuny pada przy jego wejściu w akcie VI."},
        {"pattern": "Jamal", "notBefore": r("amanat", "Jamal al-Din"), "why": "W haku syn jest bez imienia (Wytyczne 1.26)."},
    ],
    "decisions": [
        {"id": "D1", "at": "2026-11-27", "by": "reżyser", "text": "Tytuł główny: „The Imam Who Fought Russia for 25 Years — and "
         "Ended Up in Dune” (wariant 3 z rozmowy; reżyser: „tytuł ten z rosją 25 years czyli 3 jako główny pierwszy”); "
         "zapasowe do testu A/B: „The Real Holy War Hidden Inside Dune”, „Dune Borrowed Its Words From a Real War”."},
        {"id": "D3", "at": "2026-11-27", "by": "wykonawca", "text": "Ton czysto historyczny: Szamil jest symbolem dla Czeczenów "
         "i Dagestańczyków, w tle islam i Rosja — bez polityki współczesnej, bez ocen."},
        {"id": "D4", "at": "2026-11-27", "by": "wykonawca", "text": "Udokumentowane są słowa i zdania (esej Collinsa, LARB 2017), nie "
         "cała fabuła. Film nie mówi „Paul to Szamil” ani „Herbert ukradł”; zastrzeżenie pada w akcie VI."},
        {"id": "D5", "at": "2026-11-27", "by": "wykonawca", "text": "Prawa autorskie: żadnych postaci, kadrów ani okładek z filmów "
         "Villeneuve'a i z wydań książek; robak i fremeni to nasze wycinanki z papieru; cytaty z powieści krótkie, na naszych kartach."},
        {"id": "D6", "at": "2026-11-28", "by": "reżyser", "text": "Kalendarz gregoriański w całym filmie (fact-check 28.11): "
         "kapitulacja 6.09.1859 (25.08 st. st.); wymiana 22.03.1855 (10.03 st. st.) → „March 1855”; najazd lipiec 1854 → „summer "
         "of 1854”. Wiek syna przy Achulgo 6–12 według źródeł → „still a boy”, lalka małego dziecka."},
        {"id": "D7", "at": "2026-11-28", "by": "reżyser", "text": "Karta z Diuny dopiero po sprawdzeniu w wydaniu — źródła cytują "
         "„tip” albo „point”, mówi Duncan Idaho albo Gurney Halleck; lektor mówi „a swordmaster”. Wymiana: syn + 40 000 rubli "
         "w srebrze + wymiana jeńców, z księżnymi dzieci i guwernantka."},
        {"id": "D9", "at": "2026-11-28", "by": "reżyser", "text": "Przebudowa całego filmu (szkic E) zamiast poprawek D. Reżyser po "
         "pierwszej minucie D: „są trzy ujęcia jakieś długie, nagle jest jedno, które ma pół sekundy… dwa ujęcia długie, a jeszcze "
         "nic się na nich nie dzieje”, „każde ujęcie powinno być… zależne od tego, co jest w scenariuszu i w narracji”, „nie róbmy "
         "stricte 4–5-minutowego filmu”, „cały początek… nic nie wiadomo, o co chodzi”, „brakuje gagów”, „przebuduj to”. Szkic E: "
         "70 ujęć, 9:45, kwestia w 61 ujęciach i 2–4 wydarzenia pod słowa w każdym; otwarcie od Diuny, którą widz zna; Gimry 1832 "
         "(skok — legenda), Dargo 1845 i „Biscuit Expedition”, Tołstoj, Kaługa; słowa z Diuny zasiane w historii; 22 gagi (GAGI.md). "
         "Silnik, lalki i dekoracje z D zostają."},
        {"id": "D12", "at": "2026-11-28", "by": "wykonawca", "text": "Lektor nagrany klonem (reżyser 28.11: „nagraj lektora”): "
         "61 kwestii, przepis TEATR, ziarno 42, 12 kwestii poprawionych ziarnem 123 albo 7 po kontroli Whisperem i ucięć. Klon czyta "
         "2,64 słowa/s zamiast 2,84 z rozpiski, więc film urósł z 9:58 do 10:34, a akt IV (syn i księżne) do 124 s — długość "
         "z historii i z nagrań (reżyser: „nie róbmy stricte 4–5-minutowego filmu”), stąd górna granica tempa 130 s. Akcja "
         "przechodzi na nagrania sama (render.czas_akcji), wydarzenia zostają na swoich słowach."},
        {"id": "D11", "at": "2026-11-28", "by": "wykonawca", "text": "Cisza w szkicu E mieszka w ujęciach (pauza po kwestii, gag, "
         "emocjonalne trzymanie uścisku), a nie w osobnych wstawkach 1,4–2,4 s bez słów — reżyser 28.11 o wersji D: „trzy ujęcia "
         "długie, nagle jedno pół sekundy”. Uwaga kontroli „lektor w 100% ujęć” (waga 1) jest świadoma; wzór „Syn słońca” "
         "i „Bonnie and Clyde” (kwestia w 80–85% ujęć, mediana ok. 10 s)."},
        {"id": "D10", "at": "2026-11-28", "by": "wykonawca", "text": "Fakty szkicu E: skok w Gimry 1832 to opowieść (Baddeley) — lektor "
         "mówi „the story goes”; drugi imam Hamzat-bek zabity w wendecie 1834; Dargo spalone przez Szamila przed wejściem Rosjan, "
         "straty wyprawy według źródeł różne → bez liczby; Tołstoj w Czeczenii 1851–1854, w czerwcu 1853 pod Groznym prawie pojmany "
         "(z Sado); Szamil żądał miliona rubli (NPLG), stanęło na 40 000; guwernantka Anna Drancy wydała wspomnienia w 1857."},
    ],
}

BIBLIA = {
    "characters": "Imam Szamil (ur. 1797 w Gimry, Awar; imam 1834–1859) — orli profil, broda czarna, od Gunibu siwa; biały turban na "
                  "papasze, czarna czerkieska, kindżał; cecha: spokój, nigdy go nie ma tam, gdzie celują. Ghazi Muhammad — pierwszy imam, "
                  "przyjaciel Szamila z dzieciństwa, ginie w Gimry. Dżamaluddin — chłopiec w papasze (1839), kadet, oficer z wąsikiem, po "
                  "wymianie w czerkiesce; umiera 1858. Drugi syn Szamila (bez imienia w lektorze) prowadzi najazd. Księżne Anna "
                  "Czawczawadze i Warwara Orbeliani (białe czepce) z dziećmi i francuską guwernantką. Car Mikołaj I (biały mundur), "
                  "car Aleksander II, hrabia Woroncow (pióropusz — gag), książę Bariatinski, urzędnik z pieczątką (gag powracający), "
                  "Lew Tołstoj (czapka kadeta, zeszyt), koza (gag powracający). Lesley Blanch, Frank Herbert. Fremeni i robak — nasze "
                  "wycinanki (D5). Jedna postać = jedna lalka; zmiana wieku = wymiana lalki w kadrze (Wytyczne 1.15).",
    "chronology": "1797 urodziny Szamila · 1832 Gimry: śmierć Ghaziego Muhammada, skok Szamila (legenda) · 1834 drugi imam ginie "
                  "w wendecie, Szamil imamem · 1839 Achulgo (80 dni): syn zakładnikiem, ucieczka nocą · 1840 powstanie Czeczenii · "
                  "1845 Dargo i „sucharowa ekspedycja” · 1851–1854 Tołstoj na Kaukazie (czerwiec 1853 prawie pojmany) · lato 1854 "
                  "najazd na Cinandali · do marca 1855 księżne w Wedeno · 22.03.1855 (10.03 st. st.) wymiana na rzece Miczik · 1857 "
                  "wspomnienia guwernantki · 1858 śmierć syna · 6.09.1859 (25.08 st. st.) kapitulacja w Gunibie · Kaługa · 1871 śmierć "
                  "w Medynie · 1960 „The Sabres of Paradise” · 1965 „Diuna” · grudzień 2026 trzecia „Diuna” w kinach.",
    "narration": "Lektor po angielsku, 3. osoba, czas przeszły, spokojny, z lekką ironią wobec imperium (nigdy wobec ofiar); pełne "
                 "zdania z łącznikami. Szkic E (28.11): każde ujęcie z kwestią ma 2–4 wydarzenia na słowach lektora; długość ujęcia: "
                 "oddech 0,6 s (w haku 0,4) + słowa / 2,84 + pauza 1,1–2,3 s + czas na wydarzenie albo gag (WYDLUZ); bez samotnych "
                 "wstawek bez słów (Wytyczne 1.9 „Rytm filmu”). Lektor od pierwszej sekundy; otwarcie od Diuny, którą widz zna; jedno "
                 "pytanie prowadzi do Gimry 1832; bez kurtyny przed aktem I. Nie mówimy „Paul to Szamil” ani „Herbert ukradł”; skok "
                 "w Gimry to „the story goes”. Silnik humoru: papiery imperium kontra góry (pieczątka FINISHED → VICTORY → CAPTURED, "
                 "trzecia bez żartu), Szamila nigdy nie ma tam, gdzie celują, koza w trzech podejściach, teatr świadomy siebie (robak "
                 "z Diuny na złej scenie, laska maszynisty). Granica: bez gagów przy śmierci, zakładniku, zasadzce, śmierci syna "
                 "i kapitulacji. Lista: GAGI.md.",
    "visuals": "Teatr papierowy jak „Syn słońca” i „Bonnie and Clyde”: wycinki na planach głębi, kamera wieloplanowa, nitki, "
               "kurtyna z pytaniem między aktami. Każda scena ma swoje miejsce: Arrakis (wydmy, dwa słońca, robak), Gimry z wieżą, "
               "plac aułu, gabinet w Petersburgu z mapą i biurkiem, Achulgo, bukowy las Czeczenii, Dargo w ogniu, Cinandali, Wedeno, "
               "rzeka Miczik, Gunib, sala tronowa, Kaługa z płotem, pustynia Medyny, pracownie pisarzy, teatr cieni przy śmierci. "
               "Paleta: piaskowe ochry pustyni kontra granat i biel śniegu i czerń czerkiesek. Rysuj pod telefon: duże lalki, mało "
               "drobnego tekstu.",
    "facts": "Daty według kalendarza gregoriańskiego (D6). Will Collins, „The Secret History of Dune”, LARB, 16.09.2017 (słowa: chakobsa, "
             "kanly, kindjal, sietch, tabr, padishah, siridar; zdania o ostrzu i o mądrości z gór/pustyni). Wikipedia: Imam Shamil, "
             "Battle of Gimry, Siege of Akhoulgo, Battle of Dargo (1845), Battle of Ghunib, The Prisoner of the Caucasus (Tołstoj 1853), "
             "Chavchavadze. Gruzińska Biblioteka Narodowa (nplg.gov.ge) — Cinandali, żądanie miliona rubli, zgoda cara. Szczegóły "
             "i rozbieżności: decyzje D6, D7, D10. Szamil nie jest udowodnionym pierwowzorem Paula; Herbert nie potwierdził inspiracji "
             "Szamilem wprost.",
    "transitions": "Zapowiedź bez przejść; kurtyna startu na pustynię; wydmy zapadają się w góry (zwrot); prolog → akt I przez kalendarz "
                   "lecący wstecz i zawieszkę „Gimry, Dagestan, 1832” (bez kurtyny); kurtyny z pytaniem przed aktami II–VI; "
                   "ściemnienie przy zmianie miejsca w akcie; w akcie VI słowa zasiane w historii lecą na nitkach z gór nad wydmę; "
                   "biała flaga łączy zakładnika, Gunib i puentę.",
}

WARSZTAT = {
    "pipeline": "## Technika\n\nUjęcia będą **rysowane kodem** w Pythonie jako teatr papierowy — silnik „Pierwszego cesarza” "
                "(`output/pierwszy-cesarz/papier.py`, `zestaw.py`) i sposób pracy „Bonnie and Clyde” (podgląd na żywo, "
                "`uklad.py` przy rekwizytach w dłoniach).\n\n"
                "- **Zestaw filmu** (do zrobienia, `output/szamil-diuna/zestaw_kz.py`): lalki kaukaskie (czerkieski, papachy, "
                "kindżały), rosyjskie mundury, księżne, sala balowa, góry i auły, winnice, rzeka, wydma, karty z maszynopisem, "
                "słowa na nitkach.\n"
                "- **Świat** (`scena.py`), **ujęcia** (`ujecia_a.py` — prolog i akty I–II, `ujecia_b.py` — akty III–VI; wydarzenia "
                "na słowach lektora `sl()`, gagi `po_kw()`), **podgląd na żywo** "
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
        {"path": "docs/filmy/szamil-diuna/ujecia/dane.py", "role": "rozpiska szkicu E: akty, sceny, ujęcia, kwestie EN; kontrola_rytmu()"},
        {"path": "docs/filmy/szamil-diuna/ujecia/buduj.py", "role": "ROZPISKA.md — czytelny scenariusz dla reżysera"},
        {"path": "docs/filmy/szamil-diuna/GAGI.md", "role": "22 gagi szkicu E, silnik humoru, granica tonu"},
        {"path": "docs/filmy/szamil-diuna/szkice/szkic_e.py", "role": "szkic E (przebudowa 28.11) do etapu Szkice ujęć"},
        {"path": "docs/filmy/szamil-diuna/ujecia/ksiega.py", "role": "księga świata, Story Bible i warsztat"},
        {"path": "output/szamil-diuna/studio_film.py", "role": "plan, księga i rozwój filmu do Studio"},
    ],
}

if __name__ == "__main__":
    (HERE.parent / "swiat.json").write_text(json.dumps(SWIAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE.parent / "warsztat.json").write_text(json.dumps(WARSZTAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("zapisano swiat.json i warsztat.json")
