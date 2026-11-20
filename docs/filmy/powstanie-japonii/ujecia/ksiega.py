"""Księga świata, Story Bible i warsztat filmu „Syn słońca — powstanie Japonii” — źródło dla Studio.

  python3 docs/filmy/powstanie-japonii/ujecia/ksiega.py    — zapisuje ../swiat.json i ../warsztat.json (kopia do historii gita)

Odwołania do ujęć powstają z kluczy rozpiski (`r("kropla", "kropli")` → `d01_07~kropli`), więc dopisanie ujęcia ich nie psuje.
Miejscem pracy jest Studio (Continuity Editor → Świat / Warsztat); wgrywa je output/powstanie-japonii/studio_film.py.
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
        {"id": "teatr", "name": "Front teatru", "note": "Skrzynia sceny w kształcie bramy torii: cynobrowe słupy, czarna belka kasagi "
         "z wygiętymi końcami, tabliczka z tytułem „SYN SŁOŃCA”; pierwsze i ostatnie ujęcie.", "connects": ["kraj", "morze"]},
        {"id": "morze", "name": "Morze pod chmurami", "note": "Cztery pasma papierowych fal, chmury na nitkach, tęczowy most niebios; "
         "z fal wysuwają się wyspy z sosnami. Ta sama dekoracja służy Morzu Wewnętrznemu i morzu przy Kii (inne wyspy, łodzie).",
         "connects": ["kraj"]},
        {"id": "yomi", "name": "Kraina zmarłych", "note": "Ciemność, jedna pochodnia, głaz na wejście z prawej.", "connects": ["morze"]},
        {"id": "niebo", "name": "Niebiańska równina", "note": "Ziemią są chmury wysuwane od dołu; poletka ryżu bogów, tkalnia, skała "
         "z jaskinią po prawej, drzewo sakaki przed nią.", "connects": ["kraj"]},
        {"id": "kraj", "name": "Kraj na scenie", "note": "Diorama: papier nieba, słońce na nitce, góry, pasma wzgórz, sosny, rzeka albo pola "
         "ryżu, rampa. Odmiany: Izumo (rzeka), Hyūga i Takachiho (Kiusiu), Kumano (las cedrów), Yamato (krąg niebieskich gór, "
         "góra Unebi, pałac Kashihara).", "connects": ["morze", "rampa"]},
        {"id": "rampa", "name": "Przód sceny (rampa)", "note": "Deska, zza której wysuwają się lalki, parawan, stół pisarza, skrzynki "
         "ze skarbami.", "connects": ["kraj"]},
        {"id": "mapa", "name": "Mapa wysp", "note": "Papierowa mapa Japonii na dwóch nitkach przed niebem; potem plansza z kurhanem.",
         "connects": ["kraj"]},
    ],
    "characters": [
        {"id": "iwarebiko", "name": "Iwarebiko", "aliases": ["Jimmu"], "role": "prawnuk Ninigiego, książę z Hyūga, od " + r("tron", "tron")
         + " pierwszy cesarz", "look": "wycinanka w stylu kofun: biała tunika z czerwonym pasem, szerokie spodnie wiązane pod kolanem, "
         "fryzura mizura, naszyjnik magatama, długi łuk", "costume": "od " + r("tron", "ganek") + " złota opaska na czole",
         "traits": "nie chodzi — jedzie na listwie z podskokiem, obraca się, pochyla, unosi łuk; ręka na zawiasie w barku",
         "states": [{"from": r("tron", "tron"), "state": "cesarz (złota opaska)"}, {"from": r("smierc", "opada"), "state": "nie żyje"}]},
        {"id": "izanagi", "name": "Izanagi", "role": "bóg, który włócznią wyłowił wyspy", "look": "biała szata, siwa mizura, włócznia"},
        {"id": "izanami", "name": "Izanami", "role": "bogini, matka wysp", "look": "czerwona szata, długie czarne włosy",
         "leaves": r("ogien", "opada")},
        {"id": "amaterasu", "name": "Amaterasu", "role": "bogini słońca", "look": "złocista szata, długie włosy, złoty krąg słońca za głową"},
        {"id": "susanoo", "name": "Susanoo", "role": "bóg burzy, brat Amaterasu", "look": "granatowa szata, rozwiane włosy, broda, miecz"},
        {"id": "uzume", "name": "Uzume", "role": "bogini tańca", "look": "pomarańczowa szata, gałązki w rękach"},
        {"id": "ninigi", "name": "Ninigi", "role": "wnuk Amaterasu", "look": "biało-złota szata, mizura", "leaves": r("prawnuk", "opada")},
        {"id": "itsuse", "name": "Itsuse", "role": "najstarszy brat Iwarebiko", "look": "niebieska szata, mizura",
         "joins": r("bracia", "Itsuse"), "leaves": r("itsuse", "zmarł")},
        {"id": "bracia2", "name": "dwaj młodsi bracia", "role": "giną w burzy przy Kii (Inahi i Mikenu)", "look": "zielona i brązowa szata",
         "joins": r("bracia", "bracia"), "leaves": r("burza", "braci")},
        {"id": "nagasune", "name": "Nagasunehiko", "role": "wódz z Yamato, „książę o długich goleniach”",
         "look": "ciemnobrązowa szata, wyższy od wszystkich, długie nogi", "leaves": r("zdrada", "opada")},
        {"id": "nigihayahi", "name": "Nigihayahi", "role": "inny potomek bogów, pan Nagasunehiko", "look": "purpurowa szata, mizura"},
        {"id": "takakuraji", "name": "Takakuraji", "role": "człowiek z Kumano, który przynosi miecz", "look": "szara tunika, przepaska"},
        {"id": "himiko", "name": "Himiko", "role": "królowa Wa w III wieku (chińskie zapiski)", "look": "biała szata, wysoka fryzura, lustra"},
        {"id": "yatagarasu", "name": "Yatagarasu", "role": "wielka wrona przewodniczka", "look": "czarny papier, trzy nogi"},
        {"id": "orochi", "name": "ośmiogłowy wąż", "role": "potwór z Izumo", "look": "osiem głów z czerwonymi oczami na szyjach z łusek",
         "leaves": r("miecz", "węża")},
    ],
    "props": [
        {"id": "wlocznia", "name": "Włócznia z klejnotami", "owner": "Izanagi", "seeded": r("most", "włócznią"),
         "uses": [r("wlocznia", "włócznię"), r("kropla", "grot")]},
        {"id": "lustro", "name": "Lustro", "place": "niebo", "seeded": r("koguty", "lustro"),
         "uses": [r("lustro", "lustrze"), r("skarby", "lustro"), r("tron", "lustro"), r("smierc", "lustro")],
         "note": "Jedno z trzech skarbów; w 2019 roku zostaje w świątyni, dlatego przy koronacji są tylko dwie skrzynki."},
        {"id": "klejnoty", "name": "Sznur klejnotów magatama", "place": "niebo", "seeded": r("koguty", "klejnotów"),
         "uses": [r("skarby", "klejnoty"), r("tron", "klejnoty"), r("smierc", "klejnoty"), r("koronacja", "klejnoty")]},
        {"id": "kusanagi", "name": "Miecz z ogona węża", "seeded": r("miecz", "ogonie"),
         "uses": [r("skarby", "miecz"), r("tron", "miecz"), r("smierc", "miecz"), r("koronacja", "miecz")]},
        {"id": "luk", "name": "Długi łuk Iwarebiko", "owner": "Iwarebiko", "seeded": r("prawnuk", "łukiem"),
         "uses": [r("pod_slonce", "łuk"), r("ptak", "łuku")]},
        {"id": "kadzie", "name": "Osiem kadzi sake", "place": "kraj", "seeded": r("kadzie", "kadzi"), "uses": [r("pije", "kadziach")]},
        {"id": "grzebien", "name": "Grzebień we włosach Susanoo", "owner": "Susanoo", "seeded": r("kadzie", "grzebień")},
        {"id": "futsu", "name": "Miecz zrzucony z nieba", "seeded": r("takakuraji", "miecz"), "uses": [r("przebudzenie", "miecz")]},
        {"id": "strzaly_nieba", "name": "Strzały z niebiańskim upierzeniem", "seeded": r("strzala_nieba", "strzale")},
        {"id": "pieczec", "name": "Złota pieczęć króla Na", "seeded": r("chlop", "pieczęć"),
         "uses": [r("pieczec", "pieczęć"), r("odcisk", "pieczęć")], "note": "Od przeglądu 18.11.2026 najpierw znalezisko chłopa (1784), potem czym była."},
        {"id": "choragiewki", "name": "Chorągiewki z czerwonym słońcem", "place": "kraj", "seeded": r("luty2", "chorągiewki")},
    ],
    "resources": [],
    "rules": [
        {"id": "izanami", "name": "Izanami żyje", "from": r("most", "Izanami"), "to": r("ogien", "opada")},
        {"id": "ciemnosc", "name": "słońce w jaskini: ciemność na niebie i ziemi", "from": r("jaskinia", "gaśnie"), "to": r("swit", "słońce"),
         "note": "Tylko pochodnie; lustro błyska dopiero w świetle ze szczeliny."},
        {"id": "itsuse", "name": "Itsuse żyje", "from": r("bracia", "Itsuse"), "to": r("itsuse", "zmarł")},
        {"id": "bracia", "name": "dwaj młodsi bracia żyją", "from": r("bracia", "bracia"), "to": r("sam", "Iwarebiko"),
         "note": "Giną w burzy (ujęcie „burza”); od następnego ujęcia ich nie ma."},
        {"id": "nagasune", "name": "Nagasunehiko żyje", "from": r("nagasune", "Nagasunehiko"), "to": r("zdrada", "opada")},
        {"id": "cesarz", "name": "Iwarebiko jest cesarzem", "from": r("tron", "tron"), "to": r("smierc", "opada")},
    ],
    "events": [
        {"at": r("wlocznia", "Izanagi"), "note": "Izanagi i Izanami mieszają morze włócznią", "needs": ["izanami"]},
        {"at": r("wyspy", "Izanami"), "note": "bogowie stoją na pierwszej wyspie", "needs": ["izanami"]},
        {"at": r("ciemno", "pochodnie"), "note": "ciemność, tylko pochodnie", "needs": ["ciemnosc"]},
        {"at": r("koguty", "koguty"), "note": "koguty pieją w ciemności", "needs": ["ciemnosc"]},
        {"at": r("uzume", "Uzume"), "note": "taniec przed jaskinią", "needs": ["ciemnosc"]},
        {"at": r("rana", "Itsuse"), "note": "strzała trafia Itsuse", "needs": ["itsuse"]},
        {"at": r("pod_slonce", "Itsuse"), "note": "ranny Itsuse wskazuje słońce", "needs": ["itsuse"]},
        {"at": r("burza", "braci"), "note": "dwaj bracia giną w burzy", "needs": ["bracia"], "needsOff": ["itsuse"]},
        {"at": r("sam", "Iwarebiko"), "note": "z braci został tylko Iwarebiko", "needsOff": ["itsuse", "bracia"]},
        {"at": r("bitwa", "Nagasunehiko"), "note": "druga bitwa z Nagasunehiko", "needs": ["nagasune"]},
        {"at": r("strzala_nieba", "Nagasunehiko"), "note": "Nagasunehiko pokazuje niebiańską strzałę", "needs": ["nagasune"]},
        {"at": r("palac", "pałac"), "note": "pałac powstaje po zwycięstwie", "needsOff": ["nagasune"]},
        {"at": r("imie", "cesarzem"), "note": "zawieszka z imieniem przed cesarzem", "needs": ["cesarz"]},
        {"at": r("linia", "cesarzy"), "note": "linia następców po śmierci", "needsOff": ["cesarz"]},
    ],
    "threads": [
        {"id": "swieto", "title": "11 lutego: urodziny państwa", "setup": [r("tron", "nowego roku")], "clues": [r("rachunek", "wróżby")],
         "payoff": [r("luty2", "lutego")]},
        {"id": "czy_zyl", "title": "Czy pierwszy cesarz żył?", "setup": [r("hak_najazd", "istniał")],
         "clues": [r("imie", "później"), r("kronika", "712"), r("rachunek", "wróżby"), r("jomon", "myśliwi"), r("haniwa", "prawdziwi")],
         "payoff": [r("koniec", "żył")]},
        {"id": "kropla", "title": "Kraj z kropli z włóczni", "setup": [r("kropla", "kropli")], "clues": [r("wyspy", "wysp")],
         "payoff": [r("koniec", "kropli")]},
        {"id": "skarby", "title": "Lustro, klejnoty i miecz", "setup": [r("koguty", "lustro"), r("lustro", "skarbów"), r("miecz", "miecz")],
         "clues": [r("skarby", "klejnoty"), r("tron", "lustro"), r("smierc", "przeszły")], "payoff": [r("koronacja", "miecz")]},
        {"id": "slonce", "title": "Potomek słońca walczy pod słońce", "setup": [r("meduza", "bogami"), r("rzeka", "przodkini")],
         "clues": [r("jaskinia", "słońce"), r("wschod", "słońce"), r("nagasune", "słońce")], "payoff": [r("pod_slonce", "słońcem")]},
        {"id": "bracia", "title": "Czterech braci wyrusza, wraca jeden", "setup": [r("hak_najazd", "braćmi"), r("bracia", "braćmi")],
         "clues": [r("rana", "Itsuse"), r("itsuse", "zmarł"), r("burza", "braci")], "payoff": [r("sam", "Iwarebiko")]},
        {"id": "nagasune", "title": "Książę o długich goleniach", "setup": [r("nagasune", "Nagasunehiko")],
         "clues": [r("rana", "strzał"), r("bitwa", "Nagasunehiko"), r("strzala_nieba", "Nagasunehiko")], "payoff": [r("zdrada", "zabił")]},
        {"id": "wrona", "title": "Wrona przewodniczka", "setup": [r("wrona", "Yatagarasu")], "payoff": [r("trzy_nogi", "trzema")]},
        {"id": "ptak", "title": "Złoty ptak na łuku", "setup": [r("zap_blysk", "ptaka")], "clues": [r("ptak", "złoty")],
         "payoff": [r("order", "ptaka")]},
        {"id": "nihon", "title": "Kraj od słońca", "setup": [r("teatr", "słońce")], "clues": [r("rzeka", "Amaterasu")],
         "payoff": [r("nihon", "słońca"), r("koniec", "słońca")]},
        {"id": "teatr", "title": "To wszystko było w papierowym teatrze", "setup": [r("teatr", "teatru")], "payoff": [r("koniec", "teatru")]},
    ],
    "spoilers": [
        {"pattern": r"\bJimmu\b", "notBefore": r("imie", "Jimmu"), "why": "imię Jimmu nadano w VIII wieku — do intronizacji bohater to Iwarebiko"},
        {"pattern": r"Nihon\b", "notBefore": r("nihon", "Nihon"), "why": "nazwa Nihon pojawia się dopiero pod koniec VII wieku"},
    ],
    "decisions": [
        {"id": "D1", "text": "Film „Syn słońca — powstanie Japonii” na wzór „Pierwszego cesarza”: mit z Kojiki i Nihon shoki (wyspy z kropli, "
         "Amaterasu, wąż, trzy skarby, wyprawa Iwarebiko na wschód, intronizacja w 660 p.n.e.), potem to, co mówi historia (kroniki "
         "spisane w 712 i 720, chińskie zapiski, Himiko, kurhany, nazwa Nihon, 1873, 2019). 9 aktów, 74 ujęcia, ok. 11 min.",
         "at": "2026-11-13", "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D2", "text": "Postacie wycinane kodem w stylu epoki kofun (tunika, spodnie wiązane pod kolanem, fryzura mizura albo długie "
         "włosy, naszyjnik magatama), bo wycinanki PNG to chińscy uczeni. Ręka na zawiasie w barku; lalki jadą na listwie z podskokiem, "
         "obracają się, pochylają i opadają pod rampę. Z PNG zostają chmury, słońce i pisarz w akcie 8 "
         "(dwór z 712 roku nosił szaty w stylu chińskim); krajobraz jest japoński (D7).", "at": "2026-11-13", "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D3", "text": "Bohater nazywa się Iwarebiko aż do intronizacji; imię Jimmu pada dopiero w ujęciu „imie” (nadał je uczony "
         "Ōmi no Mifune w VIII wieku).", "at": "2026-11-13", "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D4", "text": "Liczby i wersje za Nihon shoki (45 lat, 660 p.n.e., 76 lat panowania, 127 lat życia, burza zabiera dwóch braci, "
         "złoty ptak); Kojiki podaje 137 lat. Zastrzeżenia w kwestiach: „według kronik”, „jak mówi kronika”, „podobno”, „najpewniej” "
         "(data z cyklu 1260 lat — hipoteza Naki Michiyo).", "at": "2026-11-13", "by": "wykonawca (do zatwierdzenia)"},
        {"id": "D5", "text": "Teatr ma się „stawiać”: na początku scen dekoracja wjeżdża od nowa (niebo na nitkach, ziemia od dołu), kamera "
         "w każdym ujęciu jedzie bokiem (paralaksa), przedplan z kulis, życie w tle (ptaki, wędrowcy) — zasada z „Pierwszego cesarza” (D7).",
         "at": "2026-11-10", "by": "reżyser"},
        {"id": "D6", "text": "Film ma 8–12 minut; render pełnej jakości na końcu i robi go reżyser. Lektora nie nagrywa się bez zgody — "
         "długości ujęć z tempa klonu głosu (2,1 słowa/s), tak jak w „Pierwszym cesarzu”.", "at": "2026-11-10", "by": "reżyser"},
        {"id": "D7", "text": "Sceneria japońska, nie z „Pierwszego cesarza”: w tle Fuji nad okrągłymi, zalesionymi pagórkami z polanami "
         "i dzikimi wiśniami, na kulisach kwitnąca wiśnia, kępa bambusa i gałąź wiśni u góry kadru; Takachiho to zielony stożek, "
         "góry dookoła Yamato — błękitne pagórki. Wszystko wycięte kodem (zestaw_jp: fuji, wzgorza_jp, wisnia, bambus, galaz_wisni).",
         "at": "2026-11-13", "by": "reżyser"},
        {"id": "D8", "text": "Film idzie po angielsku na kanał Paper Theatre jako następny po „Pierwszym cesarzu” (tytuł według wzoru "
         "„<temat>, Told in Paper Theatre”); robi się go na własnej gałęzi git „powstanie-japonii”. Kwestie EN w kwestie_en.py "
         "(polska rozpiska zostaje źródłem ujęć), napisy na wycinkach przez ETYKIETY. Film EN ma 8–12 min: kwestie skrócone tak, "
         "żeby zmieściły się z pauzami i wydłużeniami (ok. 11:45 przy tempie lektora EN 2,84 słowa/s).", "at": "2026-11-17",
         "by": "reżyser"},
        {"id": "D9", "text": "Lektor EN tak jak w „Pierwszym cesarzu”: Chatterbox Multilingual po angielsku z ustawieniami TEATR "
         "(Podręcznik → Lektor, zasada 8), próbka z angielskiego nagrania autora, 3 podejścia, kontrola Whisperem, potem "
         "lektor_studio.py podejscia --teatr (3% wolniej, pauzy z zakresów) i kontrola urwanych słów (zasada 9). Polska próba "
         "wersji wielojęzycznej (14.11) odpada. Klon to wersja robocza do rytmu w Studio — reżyser nagra lektora do całego filmu "
         "sam, później (18.11: „1 wersję szybko, ja i tak będę nagrywał sam”), więc jedno podejście na kwestię (ZIARNA=42).",
         "at": "2026-11-17", "by": "reżyser"},
        {"id": "D10", "text": "Ujęcia przerabia się według Wytycznych ujęć z 17.11 (przepis na ujęcie, zasady 1.15–1.24): podpis przy "
         "pierwszym pojawieniu się każdej postaci, śmierć widać (X na oczach, konanie, opadanie), zabójstwo ma fazy ciosu, "
         "potęga liczbą (flota, wojsko w Naniwie i w bitwie, haniwa), gagi ze słownika znaków (tabliczki „HA HA!”, „AW!…”, "
         "gwiazdki przy zamroczeniu), syn przy śmierci cesarza, kurtyna z tytułem między aktami i ściemnienie przy zmianie "
         "miejsca, podziękowanie na końcu, głos człowieka (śmiech, jęk, kaszel) z nagrania, a nie z szumu.", "at": "2026-11-17",
         "by": "reżyser"},
        {"id": "D11", "text": "Film budujemy na wszystkich szkicach naraz (szkic D „Wszystko razem”: A trzy skarby, B śledztwo, "
         "C czterech braci + obecne akty; reżyser 18.11: „na nich bym zbudował cały film i A i B i C i aktualne akty”). "
         "Pierwszy krok: otwarcie jako prolog (akt 0) — 5 s zapowiedzi najlepszych akcji (skróty ujęć, render.WYCINEK), hak "
         "w środku akcji (strzała w Itsuse, burza, miecz z koronacji 2019, pytanie, czy pierwszy cesarz istniał), tytuł teatru "
         "2,5 s i obietnica filmu; w pierwszej minucie dekoracja zmienia się co najmniej 3 razy. Reszta filmu według szkicu D "
         "po jego zatwierdzeniu w Studio.", "at": "2026-11-18", "by": "reżyser"},
        {"id": "D12", "text": "Poprawki z przeglądu scenariusza (reżyser 18.11: „tak, wszystkie oprócz lektora, lektora dodam na końcu”). "
         "Film idzie według szkicu D: wypadają księżniczki kwiatów i skał, postoje w portach, pola ryżowe i żona cesarza (11:59 przy "
         "tempie lektora EN). Wprowadzenie nazywa Iwarebiko i pokazuje go z podpisem „przyszły cesarz”; meduza to pomost do mitu "
         "(„żeby zrozumieć, czemu bracia wierzyli, że pochodzą od słońca…”); Amaterasu to przodkini braci; koronacja z 2019 to „cesarz "
         "z jego rodu”. Fakty: miecz z ogona węża według tradycji ukryty w chramie, cesarz dostał zastępczy; haniwa — prawdziwi "
         "władcy Yamato, nie „pierwsi, o których wiemy”; święto 11 lutego zniesione po wojnie i przywrócone w 1966; ryż na południowym "
         "zachodzie; „inny miecz” w Kumano; 127 lat „według kroniki”. Śledztwo: chłop → pieczęć → odcisk → chińskie zapiski. Powrót "
         "do sceny z haka innymi słowami („Pamiętasz tę strzałę?”), hak przed aktem VIII („Ale czy on w ogóle istniał?”), tytuły "
         "aktów to pytania, mniej imion (bez Uzume, Takakuraji, Hyūga, Kii, Unebi), cisza muzyki przed szczytami (wąż, wrona, "
         "złoty ptak). Kwestie bez nagrania czekają na lektora reżysera.", "at": "2026-11-18", "by": "reżyser"},
        {"id": "D13", "text": "Zmiany od „Bonnie and Clyde” (reżyser 20.11: „dołóż głosy, efekty, gagi i inne rzeczy na film, patrząc "
         "na nowe zmiany od Bonnie i Clyde”). Jeden początek (Podręcznik, Rytm): zapowiedź 6 s z 10 cięciami na uderzeniach, kurtyna "
         "tytułu 2,5 s, lektor od ok. 9 s, obietnica „By the end…” wypada — hak kończy się jednym pytaniem („So where did it come "
         "from?”), a prolog przechodzi w akt I bez kurtyny (ściemnienie i zawieszka „The Age of the Gods”). Gagi według rozdziału "
         "„Humor i gagi” (GAGI.md: 16 zrobionych, 9 do wyboru; silnik humoru: legenda kontra rzeczywistość, gag powracający: "
         "królowa przed lustrem; bez gagów przy śmierci i żałobie). Głosy postaci z modelu mowy (Kokoro + Chatterbox Turbo, bez "
         "głosu reżysera) pod tabliczkami, łagodne ściszanie pod lektorem, przystanek muzyki na puencie gagu, uderzenie na każdym "
         "cięciu zapowiedzi.", "at": "2026-11-20", "by": "reżyser"},
    ],
}

BIBLIA = {
    "characters": "Iwarebiko (od intronizacji cesarz Jimmu) — biała tunika z czerwonym pasem, mizura, długi łuk; od intronizacji złota "
                  "opaska. Bracia: Itsuse (niebieski, najstarszy), dwaj młodsi (zielony, brązowy). Bogowie: Izanagi (biel, włócznia), "
                  "Izanami (czerwień), Amaterasu (złoto, krąg słońca), Susanoo (granat, rozwiane włosy), Uzume (pomarańcz). Ninigi "
                  "(biel i złoto). Wrogowie: Nagasunehiko (ciemny brąz, długie "
                  "nogi, najwyższy), Nigihayahi (purpura). Takakuraji, Himiko, pisarz z 712 roku, chłop z 1784 roku.",
    "chronology": "Era bogów (mit) · Ninigi schodzi na Takachiho · Iwarebiko ma 45 lat i wyrusza na wschód (wg Nihon shoki 667 p.n.e.) · "
                  "Kusaka, śmierć Itsuse, burza przy Kii, Kumano, Yamato · 660 p.n.e. intronizacja w Kashiharze · 585 p.n.e. śmierć "
                  "w wieku 127 lat · w rzeczywistości: koniec epoki Jōmon, ryż z kontynentu · 57 n.e. złota pieczęć króla Na · 239 "
                  "Himiko u Wei · III–VII w. kurhany · koniec VII w. nazwa Nihon i tytuł tennō · 712 Kojiki, 720 Nihon shoki · VIII w. "
                  "imię Jimmu · 1784 pieczęć wykopana · 1873 święto 11 lutego · 2019 koronacja 126. cesarza.",
    "narration": "Lektor w 3. osobie, czas przeszły. Kwestia to pełne zdanie z czasownikiem; w ciągach zdarzeń łączniki (wtedy, potem, "
                 "więc, bo, żeby, ale, kiedy). Lektor dopowiada przyczyny, liczby i źródła („według kronik”), obraz pokazuje zdarzenie. "
                 "Długość ujęcia z kwestii: oddech 0,6 s + ok. 2,1 słowa/s + pauza; akcja i żądła 1,8–3,4 s bez słów. Do intronizacji "
                 "bohater to Iwarebiko; imię Jimmu pada w ujęciu z zawieszką 神武.",
    "visuals": "Teatr papierowy jak w „Pierwszym cesarzu”: wycinki na planach głębi, kamera wieloplanowa (paralaksa), cień każdego wycinka "
               "na planach za nim, ciepłe światło z lewej, głębia ostrości. Front teatru w kształcie bramy torii. Lalki wycinane kodem "
               "w stylu kofun, z ręką na zawiasie. Nic nie pojawia się znikąd: niebo i rekwizyty wiszą na nitkach, ziemia i lalki "
                "wysuwają się od dołu zza bliższego planu. Ciemność jaskini, noc i burza to światło i barwa sceny; ogień z bibuły.",
    "facts": "Źródła mitu: Kojiki (712) i Nihon shoki (720). Chińskie zapiski: Księga Han (ponad sto państewek Wa), Księga Późniejszych Han "
             "(pieczęć z 57 roku; pieczęć z Shikanoshimy, skarb narodowy), Kronika Wei (Himiko, 239 rok, sto luster). Data 660 p.n.e. "
             "z cyklu 1260 lat liczonego wstecz od 601 roku (hipoteza Naki Michiyo). Imię Jimmu: Ōmi no Mifune, VIII w. Order Złotej "
             "Kani: 1890–1947. Kurhan Daisen: 486 m. Święto 11 lutego (Kigensetsu) od 1873, dziś Dzień Założenia Państwa. Naruhito — "
             "126. cesarz, koronacja 2019; miecz i klejnot przy ceremonii zawinięte, a miecz to zastępczy egzemplarz (Kusanagi według tradycji leży w chramie Atsuta w Nagoi; pałacowy zatonął pod Dan-no-ura w 1185 i go zastąpiono). Kigensetsu zniesione w 1948, przywrócone w 1966 jako Dzień Założenia Państwa. Uprawa ryżu na Kiusiu według części archeologów już od X–IX w. p.n.e. Rejestr faktów projektu do uzupełnienia przed publikacją.",
    "transitions": "Między ujęciami cięcie. Film zaczyna się frontem teatru i wjazdem na scenę, kończy wyjazdem i zgaszeniem lampy. Zmiana "
                   "dekoracji (morze → niebo → kraj → mapa) to cięcie, a w pierwszym ujęciu nowego miejsca dekoracja staje od nowa.",
}

WARSZTAT = {
    "pipeline": "## Technika\n\nUjęcia są **rysowane kodem** w Pythonie (PIL + numpy) jako teatr papierowy — ten sam silnik co "
                "„Pierwszy cesarz”.\n\n"
                "- **Silnik** (`output/pierwszy-cesarz/papier.py`, wspólny): plany głębi, kamera wieloplanowa (paralaksa), cienie między "
                "planami, głębia ostrości, światło, winieta, ziarno co 3 klatki.\n"
                "- **Papiery i wycinki wspólne** (`output/pierwszy-cesarz/zestaw.py`): faktury, darte krawędzie, chmury, góry, sosny, "
                "słońce, fale, zawieszki, nitki (`hang`), wysuwanie od dołu (`rise`).\n"
                "- **Zestaw filmu** (`zestaw_jp.py`): lalki w stylu kofun z ręką na zawiasie (`postac`), front teatru w kształcie torii, "
                "wyspy, most niebios, lustro, magatama, miecze, łuk, wiśnia, sakaki, wąż o ośmiu głowach, kadzie, łodzie, niedźwiedź, "
                "wrona, złoty ptak, pałac Kashihara, chaty, haniwa, kurhan, mapa wysp, pieczęć.\n"
                "- **Świat** (`scena.py`): stan sceny z kamieni milowych rozpiski, scenografie (`morze`, `niebo`, `kraj`, `mapa`), lalki.\n"
                "- **Ujęcia** (`ujecia_a.py` — akty 1–4, `ujecia_b.py` — akty 5–9): funkcja `s_<klucz>(st, w, t, T)`.\n"
                "- **Format**: 1280 × 720, 24 kl./s; szkic 640 × 360, 12 kl./s (`SZKIC=1`). Napis = pasek papieru w czasie kwestii.",
    "method": "## Kolejność pracy nad aktem\n\n"
              "1. Scenariusz i rozpiska: `docs/filmy/powstanie-japonii/ujecia/dane.py`.\n"
              "2. Księga świata: `ujecia/ksiega.py`.\n"
              "3. `python3 output/powstanie-japonii/studio_film.py plan` — plan, księga i warsztat do Studio + kontrola ciągłości.\n"
              "4. Rysunek: funkcja ujęcia; `python3 output/powstanie-japonii/render.py arkusz 12,13` — arkusz klatek.\n"
              "5. `python3 output/powstanie-japonii/render.py kontrola` — test „końca świata”.\n"
              "6. `python3 output/powstanie-japonii/studio_film.py klipy [pelne] [tylko=…]` — klipy do zakładki Ujęcia i na oś.\n"
              "7. `python3 output/powstanie-japonii/efekty.py` i `studio_film.py dzwiek` — muzyka i efekty.\n"
              "8. Recenzja aktu i wpis w dzienniku. Lektor (`lektor.py`) dopiero za zgodą reżysera.",
    "files": [
        {"path": "docs/filmy/powstanie-japonii/ujecia/dane.py", "role": "rozpiska: akty, sceny, beaty, ujęcia i kwestie lektora"},
        {"path": "docs/filmy/powstanie-japonii/ujecia/ksiega.py", "role": "księga świata, Story Bible i warsztat (źródło dla Studio)"},
        {"path": "output/pierwszy-cesarz/papier.py", "role": "silnik wspólny z „Pierwszym cesarzem”"},
        {"path": "output/pierwszy-cesarz/zestaw.py", "role": "papiery i wycinki wspólne"},
        {"path": "output/powstanie-japonii/zestaw_jp.py", "role": "lalki kofun i wycinanki tego filmu"},
        {"path": "output/powstanie-japonii/scena.py", "role": "stan świata i scenografie"},
        {"path": "output/powstanie-japonii/ujecia_a.py", "role": "ujęcia aktów 1–4"},
        {"path": "output/powstanie-japonii/ujecia_b.py", "role": "ujęcia aktów 5–9"},
        {"path": "output/powstanie-japonii/render.py", "role": "klatka, arkusz, kontrola, klipy"},
        {"path": "output/powstanie-japonii/studio_film.py", "role": "plan, księga, klipy i dźwięk do Studio"},
        {"path": "output/powstanie-japonii/efekty.py", "role": "muzyka i efekty (synteza)"},
        {"path": "output/powstanie-japonii/lektor.py", "role": "lektor — klon głosu, tylko za zgodą reżysera"},
    ],
}

if __name__ == "__main__":
    (HERE.parent / "swiat.json").write_text(json.dumps(SWIAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE.parent / "warsztat.json").write_text(json.dumps(WARSZTAT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("zapisano swiat.json i warsztat.json")
