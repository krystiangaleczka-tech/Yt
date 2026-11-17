"""Rozpiska filmu „Syn słońca — powstanie Japonii” (teatr papierowy, ok. 11 minut): akt → scena → beat → ujęcie.

Wzór: „Pierwszy cesarz” (docs/filmy/pierwszy-cesarz/ujecia/dane.py) — ten sam układ danych i te same zasady.

ujęcie: (klucz, kadr, ruch, sekundy, opis wydarzenia, dźwięk)
- klucz — nazwa funkcji ujęcia w output/powstanie-japonii (`s_<klucz>`); brak funkcji = ujęcie do narysowania;
- kadr i ruch — skróty jak w pozostałych filmach (buduj.py);
- sekundy — None: długość liczy się z kwestii (oddech 0,6 s + nagranie albo ok. 2,1 słowa/s + pauza 0,6 s);
  liczba: ujęcie bez słów;
- dźwięk zaczynający się od „L:” to kwestia lektora (pełne zdanie; liczby czytane słowami są w SLOWNIE).
Bohater nazywa się Iwarebiko aż do intronizacji; imię Jimmu pada dopiero w ujęciu `imie` (księga świata, D3).
"""
import json
from pathlib import Path

N = None
AKTY = [
    (1, "Kropla z włóczni", "Japonia świętuje urodziny państwa 11 lutego, choć nikt nie wie, czy jej pierwszy cesarz żył. Kroniki "
        "zaczynają od bogów Izanagi i Izanami, którzy włócznią wyłowili z morza pierwszą wyspę, a potem urodzili osiem wielkich wysp.", [
        ("Teatr się otwiera", "front teatru i kraj na scenie", [
            ("Otwarcie", [
                ("teatr", "TYT", "naj", 6.5, "front teatru w kształcie bramy torii z szyldem „SYN SŁOŃCA”: w ciemnej skrzyni zapala się światło, "
                 "czerwone słońce zjeżdża na nitce, od dołu wysuwają się góry, wzgórza i pola ryżowe; kamera wjeżdża do środka sceny",
                 "gong, szelest papieru, skrzyp bloczków"),
            ]),
            ("Święto", [
                ("luty", "PO", "naj", N, "na wzgórzach wyskakują po kolei białe chorągiewki z czerwonym słońcem, a nad scenę zjeżdża na nitce "
                 "zawieszka „11 lutego”", "L: Co roku jedenastego lutego Japonia świętuje urodziny swojego państwa, bo tego dnia na tron miał "
                 "wstąpić jej pierwszy cesarz."),
                ("cien", "PŚ", "stat", N, "przód sceny: zza rampy wysuwa się papierowy parawan podświetlony od tyłu; na nim wyrasta cień władcy "
                 "z łukiem, a nad nim przelatuje cień ptaka", "L: Według kronik był prapraprawnukiem bogini słońca, a historycy do dziś się "
                 "spierają, czy ten człowiek w ogóle żył."),
            ]),
        ]),
        ("Pływający most", "scena: morze pod chmurami", [
            ("Początek", [
                ("meduza", "PO", "naj", N, "zmiana dekoracji: na scenie tylko pasma papierowych fal pod chmurami, a między falami dryfuje "
                 "półprzezroczysta papierowa meduza", "L: Kroniki zaczynają od czasów, kiedy młoda ziemia dryfowała po wodzie jak meduza "
                 "i nie miała jeszcze kształtu."),
                ("most", "PP", "naj", N, "z chmur zjeżdża na nitkach tęczowy łuk mostu; po nim zsuwają się dwie lalki bogów: Izanagi w białej "
                 "szacie z włócznią i Izanami w czerwonej", "L: Wtedy na pływający most niebios zeszło dwoje bogów, Izanagi i Izanami, którzy "
                 "dostali rozkaz, żeby nadać jej kształt."),
            ]),
            ("Wyspy", [
                ("wlocznia", "PŚ", "stat", N, "Izanagi pochyla się z mostu i zanurza w falach długą włócznię z klejnotami; wokół drzewca fale "
                 "zataczają kręgi", "L: Zanurzyli w morzu włócznię wysadzaną klejnotami i mieszali nią tak długo, aż słona woda zaczęła gęstnieć."),
                ("kropla", "D", "stat", N, "detal: grot włóczni unosi się nad falę, skapuje z niego biała kropla, a tam, gdzie spadła, wyrasta "
                 "mała wysepka", "L: Kiedy ją unieśli, z ostrza skapnęła sól i z tej kropli urosła pierwsza wyspa."),
                ("wyspy", "PO", "odj", N, "spomiędzy fal wysuwają się po kolei wyspy z sosnami, od lewej do prawej, a Izanami i Izanagi stoją "
                 "na pierwszej", "L: Bóg i bogini zamieszkali na niej razem, a potem urodziło im się osiem wielkich wysp, czyli Japonia."),
            ]),
        ]),
    ]),
    (2, "Słońce w jaskini", "Izanami umiera, rodząc boga ognia; z oczyszczenia Izanagiego rodzą się Amaterasu, bóg księżyca i Susanoo. "
        "Susanoo pustoszy niebo, Amaterasu zamyka się w jaskini, a bogowie wywabiają ją lustrem, kogutami i tańcem.", [
        ("Ogień i ciemność", "scena: wyspy, potem kraina zmarłych", [
            ("Bóg ognia", [
                ("ogien", "PŚ", "stat", N, "na wyspie przy Izanami wybuchają płomienie z bibuły; bogini przechyla się i powoli opada pod rampę, "
                 "a Izanagi wyciąga do niej rękę", "L: Ostatnim dzieckiem bogini był bóg ognia, który poparzył ją tak mocno, że umarła i odeszła "
                 "do krainy zmarłych."),
                ("yomi", "PP", "stat", N, "ciemność: Izanagi z pochodnią schodzi w głąb; z mroku wyłania się sina lalka Izanami, Izanagi cofa się, "
                 "a z boku wtacza się głaz i zamyka przejście", "L: Izanagi zszedł za nią w ciemność, ale kiedy zobaczył, jak bardzo się "
                 "zmieniła, uciekł i zatoczył głaz na wejście."),
            ]),
            ("Troje dzieci", [
                ("rzeka", "PŚ", "naj", N, "Izanagi pochyla się nad rzeką; z wody wynurzają się po kolei trzy krążki: złote słońce, srebrny księżyc "
                 "i ciemna chmura, a za nimi lalki trojga bogów", "L: Potem obmył się w rzece, a z jego lewego oka narodziła się Amaterasu, "
                 "bogini słońca, z prawego bóg księżyca, a z nosa Susanoo, bóg burzy."),
            ]),
        ]),
        ("Jaskinia", "scena: niebiańska równina na chmurach, skała z jaskinią", [
            ("Burza", [
                ("susanoo", "PP", "szarp", N, "niebiańska równina: Susanoo przelatuje przez scenę w wirze wiatru, poletka ryżu odrywają się "
                 "i fruwają, dach tkalni pęka i spada", "L: Susanoo szalał po niebie, niszczył pola ryżowe siostry, a w końcu rozbił dach "
                 "komnaty, w której tkała."),
                ("jaskinia", "PO", "stat", N, "Amaterasu wchodzi do skalnej jaskini, głaz zasuwa się na wejście, słońce odjeżdża na nitce "
                 "w górę i cała scena gaśnie", "L: Obrażona Amaterasu zamknęła się w skalnej jaskini, a na niebie i na ziemi zapadła ciemność."),
                ("ciemno", "PO", "stat", 2.8, "ciemność: zapalają się po kolei pochodnie, w ich świetle widać zarysy bogów",
                 "wiatr, trzask pochodni"),
            ]),
            ("Lustro", [
                ("koguty", "PŚ", "naj", N, "przed jaskinią wyrasta drzewo sakaki; na nitkach zjeżdżają na nie lustro i sznur zielonych klejnotów, "
                 "a na grzędzie stają koguty i pieją", "L: Bogowie postawili przed jaskinią koguty, żeby piały jak o świcie, a na drzewie "
                 "zawiesili lustro i sznur klejnotów."),
                ("uzume", "PP", "stat", N, "na odwróconej kadzi tańczy bogini Uzume, tupie i wymachuje gałązkami; rząd bogów kołysze się "
                 "ze śmiechu, każdy w swoim rytmie", "L: Bogini Uzume zatańczyła na odwróconej kadzi tak zuchwale, że wszyscy bogowie "
                 "wybuchnęli śmiechem."),
                ("lustro", "Z", "stat", N, "głaz uchyla się, ze szczeliny pada światło; Amaterasu wychyla się, lustro na drzewie rozbłyskuje, "
                 "a zza skały wysuwa się siłacz i odsuwa głaz", "L: Zaciekawiona Amaterasu wyjrzała i zobaczyła w lustrze własny blask, "
                 "a wtedy najsilniejszy z bogów wyciągnął ją na zewnątrz."),
                ("swit", "PO", "odj", 3.2, "słońce wraca na nitce, scena jaśnieje, a przed jaskinią zjeżdża gruby sznur z białymi paskami papieru",
                 "gong, pianie kogutów"),
            ]),
        ]),
    ]),
    (3, "Miecz w ogonie węża", "Wygnany Susanoo zabija w Izumo ośmiogłowego węża i znajduje w jego ogonie miecz. Amaterasu daje wnukowi "
        "Ninigiemu lustro, klejnoty i miecz; Ninigi schodzi na Kiusiu i wybiera księżniczkę kwiatów zamiast księżniczki skał.", [
        ("Izumo", "scena: kraina Izumo, rzeka między górami", [
            ("Wygnanie", [
                ("wygnanie", "PP", "jaz", N, "lalka Susanoo zjeżdża na nitce z chmur nad górami i ląduje nad rzeką; rzeką spływają dwie pałeczki",
                 "L: Susanoo wygnano z nieba na ziemię, do krainy Izumo, gdzie rzeką spływały czyjeś pałeczki do jedzenia."),
                ("starcy", "PŚ", "stat", N, "w górze rzeki dwoje starców i dziewczyna; starcy kiwają się w płaczu, a za wzgórzem przesuwa się "
                 "cień ogromnego węża", "L: W górze rzeki płakała para starców, bo ośmiogłowy wąż pożarł już siedem ich córek i miał przyjść "
                 "po ostatnią."),
            ]),
            ("Sake", [
                ("kadzie", "PŚ", "stat", N, "dziewczyna kurczy się w grzebień, który wskakuje Susanoo we włosy; zza rampy wysuwa się rząd "
                 "ośmiu kadzi", "L: Susanoo zamienił dziewczynę w grzebień, wpiął go sobie we włosy i postawił osiem kadzi mocnego sake."),
                ("orochi", "PO", "naj", N, "zza gór wychylają się po kolei osiem głów na długich szyjach, z czerwonymi oczami",
                 "L: Wąż miał osiem głów i osiem ogonów, a był tak długi, że rozciągał się na osiem dolin i osiem wzgórz."),
                ("pije", "PP", "stat", 3.4, "głowy zanurzają się w kadziach, piją, kiwają się i jedna po drugiej opadają na wzgórza",
                 "chlupot, chrapanie"),
                ("miecz", "PŚ", "szarp", N, "Susanoo tnie mieczem: szyje opadają, z ogona wysuwa się błyszczący miecz i wznosi się nad scenę",
                 "L: Kiedy pijane głowy zasnęły, Susanoo porąbał węża, a w jego ogonie znalazł miecz, który oddał siostrze na przeprosiny."),
            ]),
        ]),
        ("Wnuk", "scena: niebo na chmurach, potem szczyt Takachiho na Kiusiu", [
            ("Trzy skarby", [
                ("skarby", "PŚ", "naj", N, "na chmurach Amaterasu i jej wnuk Ninigi; zjeżdżają na nitkach lustro, sznur klejnotów i miecz, "
                 "a Ninigi unosi ręce", "L: Amaterasu postanowiła, że ziemią będzie rządził jej wnuk Ninigi, i dała mu trzy skarby: lustro, "
                 "klejnoty i miecz z ogona węża."),
                ("zejscie", "PO", "jaz", N, "Ninigi zjeżdża na chmurze przez kolejne warstwy chmur aż na szczyt góry; kamera jedzie z nim w dół",
                 "L: Ninigi zszedł z nieba przez osiem warstw chmur na szczyt góry Takachiho na wyspie Kiusiu."),
            ]),
            ("Kwiat i skała", [
                ("siostry", "PŚ", "stat", N, "pod kwitnącą wiśnią stoi księżniczka w różowym, obok przy głazie jej szara siostra; Ninigi odwraca "
                 "się ku wiśni, a szara lalka opada pod rampę", "L: Tamtejszy bóg gór ofiarował mu dwie córki, ale Ninigi wybrał piękną "
                 "księżniczkę kwiatów, a brzydką księżniczkę skał odesłał do ojca."),
                ("platki", "D", "stat", N, "detal: z wiśni sypią się płatki i opadają na rampę, a kwiaty na gałęziach gasną jeden po drugim",
                 "L: Dlatego, jak mówi kronika, życie cesarzy jest krótkie jak życie kwiatów, a nie trwałe jak skała."),
            ]),
        ]),
    ]),
    (4, "Na wschód", "Prawnuk Ninigiego, książę Iwarebiko, w wieku 45 lat wyrusza z braćmi z Kiusiu na wschód. Po latach rejsu po Morzu "
        "Wewnętrznym ląduje w Naniwie, ale wódz Nagasunehiko odpiera go, a strzała rani najstarszego brata Itsuse.", [
        ("Hyūga", "scena: Kiusiu, wybrzeże Hyūga", [
            ("Prawnuk", [
                ("prawnuk", "PŚ", "naj", N, "lalka Ninigiego opada pod rampę, a na jej miejscu wysuwa się młodszy książę z łukiem; z góry zjeżdża "
                 "zawieszka „Hyūga”", "L: Prawnuk Ninigiego, książę Iwarebiko, dorastał na Kiusiu, w krainie Hyūga, daleko od reszty wysp."),
                ("wschod", "PO", "naj", N, "Iwarebiko wskazuje na wschód: po prawej stronie sceny wysuwają się błękitne góry, a nad nimi wschodzi "
                 "słońce", "L: Kiedy miał czterdzieści pięć lat, usłyszał, że na wschodzie leży piękna kraina otoczona niebieskimi górami."),
                ("bracia", "PŚ", "stat", N, "obok Iwarebiko wysuwają się trzej bracia, najstarszy Itsuse w niebieskiej szacie; wszyscy obracają "
                 "się na wschód", "L: Uznał, że stamtąd najlepiej będzie rządzić całym krajem, więc razem z braćmi i wojskiem wyruszył "
                 "na wschód."),
            ]),
        ]),
        ("Morze Wewnętrzne", "scena: morze między wyspami", [
            ("Rejs", [
                ("flota", "PO", "jaz", N, "łodzie z wiosłami i żaglami z maty płyną na wschód między wyspami; kamera płynie z nimi",
                 "L: Płynęli wzdłuż wybrzeży Morza Wewnętrznego, a według kroniki zatrzymywali się po drodze na całe lata."),
                ("postoje", "PP", "stat", N, "przy brzegu stoją łodzie; na poletku ryż wyrasta, żółknie i zostaje ścięty, a na brzegu rośnie "
                 "szkielet nowej łodzi", "L: W każdym porcie budowali okręty, siali ryż i zbierali zapasy na wojnę, która czekała ich na końcu "
                 "drogi."),
            ]),
        ]),
        ("Kusaka", "scena: zatoka Naniwa i góry od wschodu", [
            ("Wróg", [
                ("naniwa", "PP", "naj", N, "łodzie przybijają do brzegu zatoki; wojsko z białymi proporcami wysuwa się na brzeg, przed nim "
                 "wznoszą się góry", "L: W końcu dopłynęli do zatoki Naniwa, tam gdzie dziś leży Osaka, i ruszyli przez góry do krainy Yamato."),
                ("nagasune", "PŚ", "stat", N, "zza grani wyrasta wielka lalka wodza na długich nogach, za nią las włóczni z ciemnymi proporcami; "
                 "słońce świeci zza jego pleców", "L: Drogę zastąpił im miejscowy wódz Nagasunehiko, czyli „książę o długich goleniach”, "
                 "ze swoim wojskiem."),
            ]),
            ("Strzała", [
                ("strzaly", "PP", "szarp", 1.8, "z gór, spod wschodzącego słońca, nadlatuje chmara strzał i wbija się w brzeg", "świst strzał"),
                ("rana", "Z", "stat", N, "strzała trafia Itsuse w ramię; lalka zatacza się i przyciska rękę",
                 "L: Jedna ze strzał trafiła najstarszego brata, Itsuse, i wtedy zrozumiał, dlaczego przegrywają."),
                ("pod_slonce", "PŚ", "stat", N, "ranny Itsuse wskazuje słońce nad górami; Iwarebiko odwraca się ku słońcu i opuszcza łuk",
                 "L: Jako potomkowie bogini słońca walczyli twarzą do słońca, więc postanowili obejść góry i uderzyć ze słońcem za plecami."),
            ]),
        ]),
    ]),
    (5, "Wrona z gór Kumano", "Itsuse umiera od rany, a burza zabiera dwóch kolejnych braci. W lasach Kumano armia pada zaczarowana, aż "
        "Takakuraji przynosi miecz z nieba; wielka wrona Yatagarasu prowadzi wojsko przez góry do Yamato.", [
        ("Półwysep Kii", "scena: morze przy półwyspie Kii", [
            ("Straty", [
                ("itsuse", "PŚ", "stat", N, "na łodzi ranny Itsuse przechyla się i powoli opada pod rampę; Iwarebiko pochyla się nad nim",
                 "L: Kiedy płynęli na południe, dookoła półwyspu Kii, Itsuse zmarł od rany."),
                ("burza", "PO", "szarp", N, "burza: fale rosną, łodzie podskakują, dwie z nich przechylają się i znikają za falą",
                 "L: Potem burza zatopiła dwie łodzie, a morze zabrało jeszcze dwóch braci."),
                ("sam", "Z", "stat", N, "zbliżenie: Iwarebiko sam na łodzi, za nim puste morze i ciemne chmury",
                 "L: Z czterech braci został tylko Iwarebiko."),
            ]),
        ]),
        ("Kumano", "scena: góry i lasy Kumano", [
            ("Niedźwiedź", [
                ("las", "PO", "stat", 3.0, "zmiana dekoracji: wyrastają cedry Kumano, między nimi snuje się mgła, a wojsko z białymi "
                 "proporcami wchodzi w las", "ptaki, wiatr w koronach drzew"),
                ("niedzwiedz", "PP", "stat", N, "las Kumano: spomiędzy cedrów wychodzi czarny niedźwiedź i znika, a wojownicy przewracają się "
                 "po kolei, każdy w swojej chwili", "L: W lasach Kumano z gęstwiny wyszedł wielki niedźwiedź i zniknął, a cała armia nagle "
                 "padła jak zaczarowana."),
                ("takakuraji", "PŚ", "stat", N, "z nieba zjeżdża na nitce przez dach spichlerza miecz; miejscowy człowiek Takakuraji chwyta go "
                 "i niesie do leżącego Iwarebiko", "L: Wtedy miejscowy człowiek, Takakuraji, przyniósł mu miecz, który bóg piorunów zrzucił "
                 "z nieba przez dach jego spichlerza."),
                ("przebudzenie", "PP", "stat", N, "Iwarebiko podnosi się z mieczem, a za nim wstają wojownicy, jeden po drugim; cienie lasu "
                 "cofają się", "L: Kiedy Iwarebiko wziął miecz do ręki, złe moce lasu padły same, a jego wojownicy obudzili się jeden "
                 "po drugim."),
            ]),
            ("Przewodnik", [
                ("wrona", "PO", "jaz", N, "nad górami przelatuje wielka czarna wrona, a pod nią wojsko z białymi proporcami idzie przełęczą; "
                 "kamera leci z nią", "L: Z nieba przysłano mu też wielką wronę Yatagarasu, która przeprowadziła wojsko przez dzikie góry "
                 "aż do Yamato."),
                ("trzy_nogi", "Z", "stat", N, "zbliżenie: wrona siada na gałęzi i składa skrzydła — ma trzy nogi",
                 "L: Później malowano ją z trzema nogami i do dziś nosi ją na koszulkach japońska reprezentacja w piłce nożnej."),
            ]),
        ]),
    ]),
    (6, "Złoty ptak", "W Yamato każde wzgórze ma swojego wodza; jeden zastawia na Iwarebiko pułapkę i sam w niej ginie. W drugiej bitwie "
        "z Nagasunehiko na łuku Iwarebiko siada złoty ptak i oślepia wrogów, a Nigihayahi zabija upartego wodza i przechodzi na stronę "
        "przybysza.", [
        ("Yamato", "scena: kotlina Yamato w kręgu gór", [
            ("Wodzowie", [
                ("yamato", "PO", "naj", N, "kotlina Yamato: w kręgu niebieskich gór wyrastają trzy wzgórza, a na każdym staje proporzec innego "
                 "wodza", "L: W Yamato każde wzgórze miało własnego wodza, a żaden z nich nie zamierzał oddać ziemi przybyszowi z Kiusiu."),
                ("pulapka", "PŚ", "stat", N, "wódz zaprasza do chaty; jego brat ostrzega Iwarebiko; z dachu chaty spada belka pułapki, a wódz "
                 "znika pod nią", "L: Jeden z nich zbudował dla gościa dom z ukrytą pułapką, ale własny brat go wydał i wódz zginął w swojej "
                 "pułapce."),
            ]),
        ]),
        ("Bitwa", "scena: wzgórza Yamato, burza z gradem", [
            ("Grad", [
                ("bitwa", "PO", "jaz", N, "dwa lasy włóczni ścierają się na wzgórzach, białe i ciemne proporce; niebo ciemnieje i sypie się "
                 "papierowy grad", "L: Z Nagasunehiko walczył jeszcze raz, ale bitwa długo nie mogła się rozstrzygnąć, a niebo pociemniało "
                 "i spadł grad."),
                ("ptak", "PŚ", "naj", N, "z chmur zlatuje złoty ptak i siada na czubku łuku Iwarebiko; ptak rozbłyskuje",
                 "L: Wtedy na czubku jego łuku usiadł złoty ptak, który świecił jak błyskawica."),
                ("blysk", "PP", "szarp", 2.0, "błysk: ciemne włócznie chwieją się i cofają za wzgórze", "grzmot, krzyki"),
                ("order", "D", "stat", N, "detal: na nitce zjeżdża złoty order z ptakiem i kołysze się, aż stanie",
                 "L: Na pamiątkę tego ptaka Japonia przez pół wieku odznaczała żołnierzy Orderem Złotej Kani."),
            ]),
            ("Nigihayahi", [
                ("strzala_nieba", "PŚ", "stat", N, "Nagasunehiko i Iwarebiko unoszą po strzale z niebiańskim upierzeniem; za wodzem wysuwa się "
                 "lalka Nigihayahiego", "L: Nagasunehiko wciąż nie chciał się poddać, bo służył innemu potomkowi bogów, Nigihayahiemu."),
                ("zdrada", "PŚ", "stat", N, "Nigihayahi unosi miecz, lalka Nagasunehiko opada pod rampę, a Nigihayahi kłania się Iwarebiko",
                 "L: Ale Nigihayahi uznał, że przybysz ma lepsze prawo do władzy, zabił upartego wodza i przeszedł na jego stronę."),
            ]),
        ]),
    ]),
    (7, "Pierwszy cesarz", "Pod górą Unebi Iwarebiko buduje pałac Kashihara i w 660 roku p.n.e. wstępuje na tron jako pierwszy cesarz; "
        "imię Jimmu dostaje dopiero od uczonych z VIII wieku. Panuje 76 lat, umiera w wieku 127 lat, a skarby przechodzą na syna.", [
        ("Kashihara", "scena: kotlina Yamato, góra Unebi", [
            ("Pałac", [
                ("palac", "PO", "naj", N, "u stóp zielonej góry Unebi wysuwają się słupy, potem podłoga, dach z trzciny i skrzyżowane belki "
                 "na szczycie pałacu", "L: Pod górą Unebi, w miejscu zwanym Kashihara, kazał zbudować pałac, którego słupy, jak pisze "
                 "kronika, wbito w samą skałę."),
                ("tron", "PŚ", "naj", N, "Iwarebiko wysuwa się na ganek pałacu; zjeżdżają za nim lustro, klejnoty i miecz, a obok zawieszka "
                 "„660 p.n.e.”", "L: Pierwszego dnia nowego roku, w 660 roku przed naszą erą, wstąpił tam na tron jako pierwszy cesarz "
                 "Japonii."),
                ("imie", "Z", "stat", N, "zbliżenie: przed cesarzem zjeżdża zawieszka ze znakami 神武",
                 "L: Imię Jimmu, czyli „boska waleczność”, nadali mu uczeni dopiero tysiąc czterysta lat później."),
                ("zona", "PŚ", "stat", N, "obok cesarza wysuwa się lalka księżniczki w zielonym; oboje kłaniają się sobie",
                 "L: Za żonę wziął córkę miejscowego boga, żeby nowa władza połączyła się ze starą ziemią."),
            ]),
        ]),
        ("Panowanie", "scena: kotlina Yamato z polami ryżu", [
            ("Długie życie", [
                ("pola", "PO", "pan", N, "pola ryżowe zielenieją, złocą się i znów zielenieją; słońce i księżyc mijają się na nitkach",
                 "L: Według kroniki panował siedemdziesiąt sześć lat, a jego dwór rósł razem z polami ryżu w kotlinie."),
                ("smierc", "PŚ", "stat", N, "zawieszka „127 lat”; lalka cesarza przechyla się i opada pod rampę, a lustro, klejnoty i miecz "
                 "zostają nad pustym miejscem", "L: Zmarł, mając sto dwadzieścia siedem lat, a lustro, klejnoty i miecz przeszły na jego syna."),
                ("pusto", "D", "stat", 2.6, "detal: pusty ganek pałacu; lustro kołysze się na nitce i łapie ostatni promień słońca", "wiatr"),
                ("linia", "PO", "odj", N, "wzdłuż wzgórz wysuwa się długi szereg małych lalek cesarzy, coraz mniejszych w głębi",
                 "L: Od niego miała się zacząć linia cesarzy, która według tradycji nie przerwała się aż do dziś."),
            ]),
        ]),
    ]),
    (8, "Kronika i ziemia", "Historię spisano dopiero w 712 i 720 roku na zamówienie dworu, a datę 660 p.n.e. wyliczono z chińskiej "
        "wróżby; wtedy na wyspach żyli myśliwi i rybacy. Chińskie zapiski mówią o ponad stu państewkach Wa, złotej pieczęci z 57 roku "
        "i królowej Himiko.", [
        ("Kronika", "przód sceny: stół pisarza, potem wyspy w epoce myśliwych", [
            ("712", [
                ("kronika", "PŚ", "stat", N, "zza rampy wysuwa się stół, za nim pisarz w dworskiej szacie; zwój rozwija się i pokrywa znakami, "
                 "a z góry zjeżdża zawieszka „712”", "L: Całą tę historię spisano jednak dopiero w 712 i 720 roku, w kronikach zamówionych "
                 "przez dwór, który chciał pokazać, skąd ma prawo do władzy."),
                ("rachunek", "D", "stat", N, "detal: na nitkach zjeżdżają po kolei zawieszki „601”, „− 1260 lat” i „660 p.n.e.”",
                 "L: Datę 660 roku najpewniej wyliczono z chińskiej wróżby, według której co tysiąc dwieście sześćdziesiąt lat przychodzi "
                 "wielka przemiana."),
                ("jomon", "PO", "naj", N, "zmiana dekoracji: wzgórza bez pałacu i pól; wyrastają stożkowe chaty z trzciny i gliniane garnki, "
                 "a między nimi przechodzą myśliwi z włóczniami", "L: Tymczasem w 660 roku przed naszą erą na wyspach żyli myśliwi i rybacy, "
                 "a ryż dopiero docierał na nie z kontynentu."),
            ]),
        ]),
        ("Chińskie zapiski", "scena: mapa wysp na nitkach", [
            ("Wa", [
                ("wa", "PO", "stat", N, "na nitkach zjeżdża papierowa mapa wysp; na niej wyskakują dziesiątki maleńkich chorągiewek",
                 "L: Pierwsze pewne wiadomości o wyspach zostawili Chińczycy, według których kraj ludzi Wa dzielił się na ponad sto państewek."),
                ("pieczec", "D", "naj", N, "detal: złota pieczęć z wężem na uchwycie zjeżdża na nitce i obraca się; zawieszka „57”",
                 "L: W 57 roku cesarz Chin podarował jednemu z ich królów złotą pieczęć z wężem na uchwycie."),
                ("odcisk", "D", "stat", 2.4, "pieczęć opada na papier i unosi się, a na papierze zostaje czerwony odcisk pięciu znaków",
                 "stuk pieczęci"),
                ("chlop", "PŚ", "stat", N, "chłop kopie motyką rów na polu; spod ziemi wysuwa się złota pieczęć, a z góry zjeżdża zawieszka „1784”",
                 "L: W 1784 roku wykopał ją chłop, który naprawiał rów na polu, i dziś jest skarbem narodowym Japonii."),
            ]),
            ("Himiko", [
                ("himiko", "PŚ", "naj", N, "za parawanem wysuwa się lalka królowej Himiko; na nitkach zjeżdżają do niej rzędy błyszczących luster",
                 "L: W trzecim wieku rządziła tam królowa Himiko, która podobno trzymała wodzów w posłuszeństwie czarami i dostała od Chin sto "
                 "brązowych luster."),
            ]),
        ]),
    ]),
    (9, "Źródło słońca", "Królowie z Yamato chowają się w kurhanach w kształcie dziurki od klucza; pod koniec VII wieku kraj dostaje nazwę "
        "Nihon. W 1873 roku rząd ogłasza 11 lutego świętem, a w 2019 roku 126. cesarz dostaje przy koronacji miecz i klejnoty.", [
        ("Kurhany", "scena: równina z kurhanem", [
            ("Królowie", [
                ("kofun", "PO", "naj", N, "na nitkach zjeżdża plansza z kurhanem w kształcie dziurki od klucza, otoczonym fosą; zawieszka „486 m”",
                 "L: Potem władcy z Yamato zaczęli się chować w ogromnych kurhanach w kształcie dziurki od klucza, a największy ma prawie pół "
                 "kilometra długości."),
                ("haniwa", "PP", "jaz", N, "przed kurhanem wysuwają się rzędy glinianych figurek: wojownicy, konie, domki i tancerze, każda "
                 "we własnej chwili", "L: Na ich zboczach stawiano tysiące glinianych figurek haniwa, a w środku leżeli pierwsi królowie, "
                 "o których wiemy, że naprawdę żyli."),
                ("tancerz", "Z", "stat", 2.6, "zbliżenie: gliniany tancerz haniwa z uniesioną ręką; przez jego puste oczy prześwieca słońce",
                 "wiatr, stuk gliny"),
            ]),
        ]),
        ("Nihon", "cała scena, potem front teatru", [
            ("Nazwa", [
                ("nihon", "PŚ", "stat", N, "zawieszka 倭 zjeżdża, obraca się na nitce i odjeżdża, a na jej miejsce zjeżdża 日本; za nią wschodzi "
                 "czerwone słońce", "L: Pod koniec siódmego wieku dwór nazwał kraj Nihon, czyli „źródło słońca”, bo patrząc z Chin, słońce "
                 "wschodziło właśnie tam."),
                ("luty2", "PŚ", "stat", N, "kartka kalendarza „11 lutego” zjeżdża na nitce obok zawieszki „1873”; na wzgórzach znów wyskakują "
                 "chorągiewki ze słońcem", "L: Dopiero w 1873 roku rząd w Tokio przeliczył datę z kroniki na nasz kalendarz i ogłosił jedenasty "
                 "lutego świętem."),
                ("koronacja", "PO", "naj", N, "przód sceny: na stojakach stają dwie skrzynki owinięte białym płótnem, a za nimi wyrasta tron pod "
                 "ośmiokątnym baldachimem; zawieszka „126”", "L: W 2019 roku na tron wstąpił sto dwudziesty szósty cesarz i przy koronacji "
                 "znów przyniesiono mu miecz i klejnoty, choć nikt nie odwija ich z płótna."),
            ]),
            ("Słońce", [
                ("koniec", "PO", "odj", N, "kamera wycofuje się z teatru: nad wyspami świeci czerwone słońce, światło w skrzyni gaśnie i zostaje "
                 "szyld z tytułem", "L: Nikt nie wie, czy Jimmu naprawdę żył, ale kraj, który zaczął się od kropli z włóczni, do dziś nazywa "
                 "siebie źródłem słońca."),
            ]),
        ]),
    ]),
]

# liczby w kwestiach czytane słowami — do liczenia czasu kwestii i do lektora (zamiana całych fraz, bo forma zależy od zdania)
SLOWNIE = {"w 660 roku": "w sześćset sześćdziesiątym roku", "Datę 660 roku": "Datę sześćset sześćdziesiątego roku",
           "w 712 i 720 roku": "w siedemset dwunastym i siedemset dwudziestym roku", "W 57 roku": "W pięćdziesiątym siódmym roku",
           "W 1784 roku": "W tysiąc siedemset osiemdziesiątym czwartym roku",
           "w 1873 roku": "w tysiąc osiemset siedemdziesiątym trzecim roku", "W 2019 roku": "W dwa tysiące dziewiętnastym roku"}


def kwestia(dzwiek):
    return dzwiek[2:].strip() if dzwiek.startswith("L:") else ""


TEMPO = 2.1  # słowa na sekundę: tempo klonu głosu autora zmierzone przy „Pierwszym cesarzu” (10.11.2026)
LEKTOR = Path(__file__).resolve().parents[4] / "output/powstanie-japonii/lektor"


def nagranie(dzwiek):
    """Długość nagranej kwestii (lektor/<klucz>.json) albo None, gdy jeszcze jej nie ma albo tekst się zmienił."""
    txt = kwestia(dzwiek)
    for f in LEKTOR.glob("*.json") if txt and LEKTOR.exists() else ():
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("text") == txt:
            return meta["duration"]
    return None


def slownie(txt):
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    return txt


def okno_kwestii(dzwiek):
    """(start, długość) kwestii w ujęciu: oddech 0,6 s, potem nagranie lektora — a zanim powstanie, tempo lektora."""
    txt = kwestia(dzwiek)
    if not txt:
        return (0.0, 0.0)
    real = nagranie(dzwiek)
    if real:
        return (0.6, real)
    return (0.6, len(slownie(txt).split()) / TEMPO)


# Pauza po kwestii, zanim padnie cięcie (podręcznik, „Rytm” 2 i 3). Reżyser 14.11.2026 (przy „Pierwszym cesarzu”): przy
# 0,6 s „obcina zaraz po kwestii ujęcie, bo następuje następne, i jest to nienaturalne” — obraz trwa jeszcze chwilę po
# ostatnim słowie, a im większa granica (beat → scena → akt), tym dłużej, bo koniec sceny to długie trzymanie.
PAUZA_PO = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}


def ujecia(akt=None):
    """Płaska lista ujęć: (akt, nr w akcie, klucz, kadr, ruch, sekundy, opis, dźwięk). Długość ujęcia z kwestią liczy się
    z kwestii: oddech przed + nagranie + pauza po (PAUZA_PO wg granicy, na której ujęcie stoi); sąsiednie ujęcia
    różnią się co najmniej o ¼ s (podręcznik, „Rytm” 2)."""
    out, prev = [], None
    for n, _, _, sceny in AKTY:
        k = 0
        for si, (_, _, beaty) in enumerate(sceny):
            for bi, (_, shots) in enumerate(beaty):
                for ui, (klucz, kadr, ruch, sec, opis, dzwiek) in enumerate(shots):
                    k += 1
                    if sec is None:
                        granica = ("ujecie" if ui < len(shots) - 1 else "beat" if bi < len(beaty) - 1
                                   else "scena" if si < len(sceny) - 1 else "akt")
                        start, mowa = okno_kwestii(dzwiek)
                        sec = round(start + mowa + PAUZA_PO[granica], 1)
                        if mowa > 6.5:  # długie zdanie: dłuższy oddech po nim
                            sec = round(sec + 0.3, 1)
                    if prev is not None and abs(sec - prev) < 0.25:
                        sec = round(sec + 0.3, 1)
                    prev = sec
                    out.append((n, k, klucz, kadr, ruch, sec, opis, dzwiek))
    return [u for u in out if akt is None or u[0] == akt]


if __name__ == "__main__":
    t = 0.0
    for n, tytul, _, _ in AKTY:
        us = ujecia(n)
        d = sum(u[5] for u in us)
        mowa = sum(okno_kwestii(u[7])[1] for u in us)
        print(f"Akt {n} · {tytul}: {len(us)} ujęć, {d:.1f} s, lektor {mowa / d:.0%}")
        t += d
    print(f"film: {int(t // 60)} min {t % 60:.0f} s ({t:.1f} s), {len(ujecia())} ujęć")
