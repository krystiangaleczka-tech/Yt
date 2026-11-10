"""Księga świata, Story Bible i warsztat filmu „Pierwszy cesarz” — źródło dla Studio.

  python3 docs/filmy/pierwszy-cesarz/ujecia/ksiega.py    — zapisuje ../swiat.json i ../warsztat.json (kopia do historii gita)

Odwołania do ujęć powstają z kluczy rozpiski (`r("mur", "mury")` → `d05_09~mury`), więc dopisanie ujęcia ich nie psuje.
Miejscem pracy jest Studio (Continuity Editor → Świat / Warsztat); wgrywa je output/pierwszy-cesarz/studio_film.py.
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
    "tempo": {"minSeconds": 45, "maxSeconds": 100, "maxVoiceShare": 0.92},
    "places": [
        {"id": "kraj", "name": "Scena „kraj”", "note": "Diorama: papier nieba, słońce i chmury na nitkach, góry, równina, miasto z bramą "
         "(Handan w akcie 1 i 3, potem stolica), most, droga przez wzgórza, dwie sosny, rampa.", "connects": ["rampa", "droga", "gora"]},
        {"id": "droga", "name": "Droga przez wzgórza", "note": "Złote pasmo przed mostem: tędy idą wojska, wozy, powóz cesarza; "
         "przy niej stoi siedem chorągwi i kanały.", "connects": ["kraj"]},
        {"id": "gora", "name": "Zielona góra i mur", "note": "Grań, zza której od aktu 5 wystaje mur z wieżami; pod nią stoi Fusu.",
         "connects": ["kraj"]},
        {"id": "rampa", "name": "Przód sceny (rampa)", "note": "Deska, zza której wysuwają się lalki: król po lewej (x = 300), stół pisarzy "
         "na środku, trójnóg z brązu po prawej.", "connects": ["kraj"]},
        {"id": "sala", "name": "Sala tronowa", "note": "Ściana z pięcioma oknami z kratą, kolumny z laki, podwyższenie tronu po lewej, "
         "kolumna na środku (zamach).", "connects": []},
        {"id": "morze", "name": "Wschodnie Morze", "note": "Cztery pasma papierowych fal, wyspa na horyzoncie, księżyc.", "connects": []},
        {"id": "teatr", "name": "Front teatru", "note": "Czerwona skrzynia ze złotą listwą i szyldem „PIERWSZY CESARZ”; pierwsze i ostatnie ujęcie.",
         "connects": ["kraj"]},
    ],
    "characters": [
        {"id": "zheng", "name": "Zheng", "aliases": ["Pierwszy Cesarz"], "role": "syn zakładnika, król Qin od 247 p.n.e., Pierwszy Cesarz od 221 p.n.e.",
         "look": "jedna wycinanka przez cały film: czarna szata ze złotymi smokami, korona z koralikami, ręka wskazująca w prawo",
         "costume": "mała lalka (205) jako chłopiec i król-chłopiec do " + r("dorosl", "duża") + ", potem duża (352)",
         "traits": "nie chodzi — obraca się na patyczku, pochyla, unosi, opada pod rampę",
         "states": [{"from": r("dorosl", "duża"), "state": "dorosły (duża lalka)"}, {"from": r("koniec", "opada"), "state": "nie żyje — lalki nie ma na scenie"}]},
        {"id": "lu", "name": "Lü Buwei", "role": "kupiec, potem kanclerz i regent", "look": "wycinanka uczonego w purpurowym obszyciu",
         "leaves": r("trucizna", "truciznę")},
        {"id": "ojciec", "name": "ojciec", "role": "książę Qin, zakładnik w Handanie (Yiren)", "look": "wycinanka uczonego w brązowym obszyciu",
         "leaves": r("ucieczka", "wywiózł")},
        {"id": "lisi", "name": "Li Si", "role": "doradca, potem kanclerz", "look": "wycinanka uczonego w zielonym obszyciu"},
        {"id": "jingke", "name": "Jing Ke", "role": "zamachowiec z Yan", "look": "wycinanka uczonego w jasnym obszyciu",
         "leaves": r("pretekst", "zginął")},
        {"id": "fusu", "name": "Fusu", "role": "najstarszy syn cesarza", "look": "wycinanka uczonego w niebieskim obszyciu",
         "leaves": r("list", "opada")},
        {"id": "zhaogao", "name": "Zhao Gao", "role": "eunuch", "look": "wycinanka uczonego w szarym obszyciu; w sali większa od wszystkich"},
        {"id": "huhai", "name": "Huhai", "role": "młodszy syn, drugi cesarz", "look": "mała lalka cesarza w niebieskim obszyciu"},
        {"id": "pisarz", "name": "pisarz", "role": "klęczy za stołem i pisze", "look": "wycinanka klęczącego pisarza z pędzlem"},
        {"id": "armia", "name": "gliniani żołnierze", "role": "armia z grobowca", "look": "wycinanki z papieru w barwie terakoty, trzy rzędy, "
         "każdy wysuwa się we własnej chwili"},
    ],
    "props": [
        {"id": "trojnog", "name": "Trójnóg z brązu", "place": "rampa", "seeded": r("posagi", "trójnogu"),
         "uses": [r("ksiegi", "trójnogu"), r("popiol", "trójnogu")], "note": "W akcie 4 przetapia broń, w akcie 6 płoną w nim księgi; chowa się o zmierzchu."},
        {"id": "zwoj", "name": "Zwój bambusowy", "place": "rampa", "seeded": r("pismo", "zwojem"), "uses": [r("ksiegi", "zwój")],
         "note": "Leży na stole pisarzy; w akcie 6 leci do ognia."},
        {"id": "mapa", "name": "Mapa siedmiu królestw", "place": "sala", "seeded": r("mapa", "mapa"), "uses": [r("mapa2", "mapa")],
         "note": "Siedem kawałków barwnego papieru; czarny papier Qin przykrywa pozostałe."},
        {"id": "mapa_yan", "name": "Zwinięta mapa ze sztyletem", "place": "sala", "seeded": r("dary", "mapa"), "uses": [r("sztylet", "sztylet")]},
        {"id": "miecz", "name": "Długi miecz króla", "owner": "Zheng", "seeded": r("kolumna", "miecz"), "uses": [r("cios", "miecz")]},
        {"id": "powoz", "name": "Powóz cesarza z czarną chorągwią", "place": "droga", "seeded": r("stela", "powóz"),
         "uses": [r("mlot", "powoz"), r("podroz", "powóz"), r("spisek", "powoz"), r("ryby", "powóz")]},
        {"id": "smoki", "name": "Dwie chorągwie ze smokiem", "place": "rampa", "seeded": r("cesarz", "smokiem"),
         "uses": [r("koniec", "smokiem"), r("upadek", "smokiem")]},
        {"id": "czarka", "name": "Czarka z brązu", "place": "rampa", "seeded": r("trucizna", "czarka"), "uses": [r("rtec", "czarka")],
         "note": "Trucizna Lü Buweia i rtęć cesarza: ta sama czarka, to samo miejsce na rampie."},
    ],
    "resources": [],
    "rules": [
        {"id": "krol_maly", "name": "Zheng jest chłopcem (mała lalka)", "from": "", "to": r("dorosl", "duża"),
         "note": "Do buntu Lao Ai na scenie stoi mała lalka."},
        {"id": "dwor", "name": "na rampie stoi stół pisarzy", "from": r("pismo", "stół"), "to": r("zmierzch", "chowają"),
         "note": "Stół zasłania środek drogi — ujęcia na drodze są przed nim albo po zmierzchu."},
        {"id": "noc", "name": "noc: księżyc zamiast słońca", "from": r("zmierzch", "księżyc"), "to": r("cisza", "słońce")},
        {"id": "cesarz_zyje", "name": "lalka cesarza stoi na scenie", "from": r("dorosl", "duża"), "to": r("koniec", "opada")},
        {"id": "czarne_stoja", "name": "na wzgórzach stoją czarne chorągwie Qin", "from": r("czarne", "czarne"), "to": r("upadek", "chorągwie")},
    ],
    "events": [
        {"at": r("regent", "mały"), "note": "kanclerz rządzi za małego króla", "needs": ["krol_maly"]},
        {"at": r("nauka", "małego"), "note": "mały król uczy się o nagrodzie i karze", "needs": ["krol_maly"]},
        {"at": r("odprawa", "król"), "note": "dorosły król odprawia kanclerza", "needsOff": ["krol_maly"]},
        {"at": r("moneta", "stołu"), "note": "moneta toczy się po stole pisarzy", "needs": ["dwor"]},
        {"at": r("miara", "stół"), "note": "waga zjeżdża na stół pisarzy", "needs": ["dwor"]},
        {"at": r("ksiegi", "stołu"), "note": "zwój leci ze stołu do ognia", "needs": ["dwor"]},
        {"at": r("drogi", "wóz"), "note": "wóz jedzie drogą przez środek sceny", "needsOff": ["dwor"]},
        {"at": r("mlot", "noc"), "note": "zamach młotem na nocnej drodze", "needs": ["noc"], "needsOff": ["dwor"]},
        {"at": r("armia", "żołnierze"), "note": "gliniana armia wstaje nocą", "needs": ["noc", "cesarz_zyje"]},
        {"at": r("spisek", "powozie"), "note": "Li Si i Zhao Gao tają śmierć cesarza", "needsOff": ["cesarz_zyje"]},
        {"at": r("powstanie", "czarne"), "note": "czarne chorągwie zaczynają padać", "needs": ["czarne_stoja"]},
        {"at": r("studnia", "dzień"), "note": "odkrycie armii w 1974 roku", "needsOff": ["noc", "czarne_stoja"]},
    ],
    "threads": [
        {"id": "handan", "title": "Chłopiec z Handanu wraca jako zdobywca", "setup": [r("handan", "Handan")], "clues": [r("sam", "bramą")],
         "payoff": [r("zhao", "Handanu")]},
        {"id": "kupiec", "title": "Kupiec, który chciał zarobić królestwo", "setup": [r("kupiec", "kupca")],
         "clues": [r("regent", "kanclerz"), r("odprawa", "kanclerza")], "payoff": [r("trucizna", "truciznę")]},
        {"id": "choragwie", "title": "Siedem chorągwi, jedna barwa", "setup": [r("choragwie", "siedem")],
         "clues": [r("mapa", "mapa"), r("han", "Han"), r("chu_yan", "Chu"), r("qi", "Qi"), r("mapa2", "czarny")], "payoff": [r("czarne", "czarne")]},
        {"id": "czarne", "title": "Czarne chorągwie padają", "setup": [r("czarne", "czarne")], "clues": [r("powstanie", "czarne")],
         "payoff": [r("upadek", "chorągwie")]},
        {"id": "zamach", "title": "Sztylet w mapie", "setup": [r("poselstwo", "zabić")], "clues": [r("dary", "mapa")],
         "payoff": [r("sztylet", "sztylet"), r("pretekst", "zginął")]},
        {"id": "miecz", "title": "Miecz za długi, żeby go wyciągnąć", "setup": [r("kolumna", "miecz")], "payoff": [r("cios", "miecz")]},
        {"id": "fusu", "title": "Syn zesłany pod mur", "setup": [r("uczeni", "Fusu")], "payoff": [r("list", "Fusu")]},
        {"id": "smierc", "title": "Jedyny wróg: śmierć", "setup": [r("zmierzch", "śmierć")],
         "clues": [r("morze", "nieśmiertelni"), r("rtec", "rtęcią"), r("meteor", "umrze"), r("armia", "śmierci")], "payoff": [r("koniec", "Umarł")]},
        {"id": "armia", "title": "Gliniana armia pod ziemią", "setup": [r("armia", "żołnierzy")], "clues": [r("cisza", "zapadają")],
         "payoff": [r("studnia", "1974")]},
        {"id": "mur", "title": "Mur na grani", "setup": [r("mur", "mury")], "clues": [r("robotnicy", "murem"), r("list", "murem")],
         "payoff": [r("qin", "mur")]},
        {"id": "teatr", "title": "To wszystko było w papierowym teatrze", "setup": [r("teatr", "teatru")], "payoff": [r("qin", "teatru")]},
        {"id": "slonce", "title": "Słońce i księżyc na nitce", "setup": [r("teatr", "słońce")], "clues": [r("zmierzch", "słońce")],
         "payoff": [r("cisza", "słońce")]},
    ],
    "spoilers": [
        {"pattern": "[Cc]esarz", "notBefore": r("cesarz", "Cesarz"), "why": "do 221 roku p.n.e. Zheng jest królem — lektor nie mówi „cesarz” przed tytułem"},
    ],
    "decisions": [
        {"id": "D1", "text": "Film ma mieć 8–12 minut; rozpiska na 8 aktów i 78 ujęć (ok. 8 min przy 2,6 słowa/s).", "at": "2026-11-10", "by": "reżyser"},
        {"id": "D2", "text": "Render pełnej jakości na końcu. Do przeglądu służą szkice 640 × 360 w zakładce Ujęcia (odtwarzanie po kolei).",
         "at": "2026-11-10", "by": "reżyser"},
        {"id": "D3", "text": "Zheng ma jedną wycinankę przez cały film: mała lalka to chłopiec, duża — dorosły. Pozostałe postacie to wycinanki "
         "uczonych z obszyciem w innej barwie (kupiec purpura, Li Si zieleń, Jing Ke jasne, Fusu niebieski, Zhao Gao szary).", "at": "2026-11-10",
         "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D4", "text": "Zdania niepewne mają zastrzeżenie w kwestii: rtęć („podobno”), rzeki z rtęci („według kronik”), Qin → Chiny "
         "(„najpewniej”). Liczby (600 tys., 700 tys., 120 tys. rodzin, 36 prowincji) za „Zapiskami historyka” Sima Qiana.", "at": "2026-11-10",
         "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D5", "text": "Akt 5: drogi, prowincje, podróże i kanał są przed stołem pisarzy, bo stół zasłania środek drogi; zamach młotem jest "
         "po zmierzchu, kiedy stół już zniknął.", "at": "2026-11-10", "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D6", "text": "Lektor wstrzymany na prośbę reżysera (nagrywanie klonem głosu trwało ok. 4 min na kwestię przy 8 GB RAM). "
         "Długości ujęć liczone z tempa zmierzonego na 3 nagranych kwestiach (2,1 słowa/s) — film 9:46.", "at": "2026-11-10", "by": "reżyser"},
        {"id": "D7", "text": "Teatr ma się „stawiać”: na początku scen dekoracja wjeżdża od nowa (niebo na nitkach, ziemia od dołu), kamera w "
         "każdym ujęciu jedzie bokiem (paralaksa), przedplan z kulis (gałąź, trzciny, kolumna), życie w tle (ptaki, wędrowcy).",
         "at": "2026-11-10", "by": "reżyser"},
    ],
}

BIBLIA = {
    "characters": "Zheng (Pierwszy Cesarz) — jedna wycinanka przez cały film: mała lalka to chłopiec z Handanu i król-chłopiec, duża to dorosły "
                  "król i cesarz. Lü Buwei — kupiec i kanclerz (purpurowe obszycie). Li Si — doradca (zielone). Jing Ke — zamachowiec (jasne). "
                  "Fusu — najstarszy syn (niebieskie). Zhao Gao — eunuch (szare, w sali większy od wszystkich). Huhai — mała lalka cesarza "
                  "w niebieskim obszyciu. Pisarz, uczeni, klęczący urzędnicy, jeździec, gliniani żołnierze.",
    "chronology": "259 p.n.e. narodziny w Handanie · 257 ucieczka ojca · ok. 250 powrót do Qin · 247 król · 238 bunt, 235 śmierć Lü Buweia · "
                  "230 Han · 228 Zhao · 227 zamach Jing Ke · 225 Wei · 223 Chu · 222 Yan · 221 Qi i tytuł cesarza · ok. 218 zamach młotem · "
                  "ok. 215 mur · 213 księgi · 212 uczeni i Fusu · 211 meteoryt · 210 śmierć · 209 powstanie · 206 koniec dynastii · 1974 odkrycie armii.",
    "narration": "Lektor w 3. osobie, czas przeszły. Kwestia to pełne zdanie z czasownikiem; w ciągach zdarzeń łączniki (więc, bo, a, żeby, "
                 "kiedy, potem). Lektor dopowiada to, czego nie widać (przyczyny, liczby, lata), obraz pokazuje zdarzenie. Długość ujęcia "
                 "z kwestii: oddech 0,6 s + ok. 2,6 słowa/s + pauza; akcja 1,4–2,6 s bez słów. Do tytułu z 221 roku lektor mówi „król”.",
    "visuals": "Teatr papierowy: wycinki na planach głębi, kamera wieloplanowa (paralaksa), cień każdego wycinka na planach za nim, ciepłe "
               "światło z lewej, głębia ostrości. Nic nie pojawia się znikąd: niebo wisi na nitkach, ziemia i lalki wysuwają się od dołu "
               "zza bliższego planu, lalki obracają się na patyczku. Noc: niebieski papier nieba i księżyc na nitce; ogień z bibuły.",
    "facts": "Źródło główne: Sima Qian, „Zapiski historyka” (Shiji), rozdz. 6 i biografie Lü Buweia, Li Si i zamachowców. Zastrzeżenia w "
             "kwestiach: pigułki z rtęcią (tradycja), rzeki z rtęci (kronika; podwyższone stężenie rtęci w kopcu potwierdzają pomiary), "
             "pochodzenie nazwy Chiny od Qin (najczęstsza hipoteza). Rejestr faktów projektu nie jest jeszcze wypełniony — do zrobienia "
             "przed publikacją.",
    "transitions": "Między ujęciami cięcie. Film zaczyna się frontem teatru i wjazdem na scenę, kończy wyjazdem i zgaszeniem lampy. "
                   "Zmiana scenografii (kraj → sala → morze) to cięcie; w sali i na morzu ta sama rampa.",
}

WARSZTAT = {
    "pipeline": "## Technika\n\nUjęcia są **rysowane kodem** w Pythonie (PIL + numpy) jako teatr papierowy.\n\n"
                "- **Wycinki**: PNG z `output/imperium-papierowe/assets` (cesarz, uczeni, miasto, most, góry, chmury, drzewa, stół, waga…) "
                "oraz wycinanki z kodu (`zestaw.py`: chorągwie królestw, mur, żołnierze, płomienie, mapa, sala, fale, dżonka, rekwizyty) "
                "z papierów pobranych z tych samych plików.\n"
                "- **Silnik** (`papier.py`): plan głębi `p` = odwrotność odległości od kamery; kamera jedzie wózkiem i ma obiektyw, więc "
                "bliskie plany rosną i przesuwają się szybciej (paralaksa); każdy wycinek rzuca miękki cień na plany za nim; głębia ostrości; "
                "światło, winieta, ziarno co 3 klatki.\n"
                "- **Świat** (`swiat.py`): stan sceny liczony z kamieni milowych rozpiski (`po(\"mur\")`), trzy scenografie (`swiat`, `sala`, "
                "`morze`), lalki (`lalka`), rekwizyty.\n"
                "- **Ujęcia** (`ujecia1.py`, `ujecia2.py`): funkcja `s_<klucz>(st, w, t, T)` — zmienia stan w czasie (wydarzenie), ustawia "
                "kamerę (`kam`), woła scenografię.\n"
                "- **Format**: 1280 × 720, 24 kl./s; szkic do przeglądu 640 × 360, 12 kl./s (`SZKIC=1`). Napis = pasek papieru w czasie kwestii.",
    "method": "## Kolejność pracy nad aktem\n\n"
              "1. Scenariusz i rozpiska: `docs/filmy/pierwszy-cesarz/ujecia/dane.py` (akt → scena → beat → ujęcie z kluczem).\n"
              "2. Księga świata: `ujecia/ksiega.py` (wątki, rekwizyty, zasady; odwołania po kluczach).\n"
              "3. `python3 output/pierwszy-cesarz/studio_film.py plan` — plan, księga i warsztat do Studio + kontrola ciągłości.\n"
              "4. Rysunek: funkcja ujęcia; `SZKIC=1 python3 render.py arkusz 12,13` — arkusz klatek; pełne klatki do kontroli rysunku.\n"
              "5. `python3 render.py kontrola` — test „końca świata” (płótno w barwie pustki).\n"
              "6. `python3 output/pierwszy-cesarz/studio_film.py klipy` — szkice do zakładki Ujęcia i na oś (przegląd: odtwarzanie po kolei).\n"
              "7. Recenzja aktu i wpis w dzienniku. **Render pełnej jakości na końcu**: `studio_film.py klipy pelne`.\n\n"
              "Na komputerze z 8 GB RAM render idzie w 3 procesach z rozwidlenia po `rozgrzej()` (wspólna pamięć wycinków).",
    "files": [
        {"path": "docs/filmy/pierwszy-cesarz/ujecia/dane.py", "role": "rozpiska: akty, sceny, beaty, ujęcia i kwestie lektora"},
        {"path": "docs/filmy/pierwszy-cesarz/ujecia/ksiega.py", "role": "księga świata, Story Bible i warsztat (źródło dla Studio)"},
        {"path": "output/pierwszy-cesarz/papier.py", "role": "silnik: plany głębi, kamera wieloplanowa, cienie, światło"},
        {"path": "output/pierwszy-cesarz/zestaw.py", "role": "wycinki, wycinanki z kodu i scena wzorcowa"},
        {"path": "output/pierwszy-cesarz/swiat.py", "role": "stan świata z kamieni milowych, lalki, trzy scenografie"},
        {"path": "output/pierwszy-cesarz/ujecia1.py", "role": "ujęcia aktów 1–4"},
        {"path": "output/pierwszy-cesarz/ujecia2.py", "role": "ujęcia aktów 5–8"},
        {"path": "output/pierwszy-cesarz/render.py", "role": "klatka, arkusz klatek, kontrola „końca świata”, klipy"},
        {"path": "output/pierwszy-cesarz/studio_film.py", "role": "plan, księga i klipy do Studio"},
        {"path": "output/imperium-papierowe/assets", "role": "wycinki PNG (jeden styl, jedno światło)"},
    ],
}

if __name__ == "__main__":
    (HERE.parent / "swiat.json").write_text(json.dumps(SWIAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE.parent / "warsztat.json").write_text(json.dumps(WARSZTAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("zapisano swiat.json i warsztat.json")
