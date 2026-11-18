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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # kwestie_en.py obok

N = None
AKTY = [
    # Akt 0 · zapowiedź i hak (szkic D „Wszystko razem”, reżyser 18.11.2026: „na początku musi być taki mini spoiler 5 s, co będzie
    # w filmie (najlepsze akcje)”; „w pierwszej minucie musi się dużo zmieniać, sceneria co najmniej 3 razy”). Ujęcia zap_* i hak_*
    # to skróty innych ujęć filmu: render.WYCINEK rysuje oryginał od jego najlepszej chwili. Sąsiednie skróty różnią się ≥ ¼ s.
    (0, "Zapowiedź i hak", "Pięć sekund najmocniejszych akcji filmu i ściemnienie; kurtyna startu rozsuwa się na teatr, na polanie "
        "stoi czterech braci, kamera najeżdża na najstarszego, a lektor mówi, o czym jest film. Potem hak: strzała trafia Itsuse, "
        "w teatrze cieni Itsuse pada, burza zabiera dwóch braci, w 2019 roku cesarz dostaje miecz, którego nikt nie widział — "
        "i obietnica filmu.", [
        ("Zapowiedź", "skróty najmocniejszych ujęć filmu, cięte bez przejść; na końcu ściemnienie", [
            ("Zapowiedź", [
                ("zap_jaskinia", "PO", "stat", 0.8, "zapowiedź (skrót ujęcia „jaskinia” od 5,0 s): słońce odjeżdża w górę, scena gaśnie",
                 "muzyka: jeden mocny akord na całą zapowiedź"),
                ("zap_orochi", "PO", "naj", 0.5, "zapowiedź (skrót ujęcia „orochi” od 6,0 s): osiem głów węża stoi nad górami",
                 "syk, uderzenie bębna"),
                ("zap_miecz", "PŚ", "szarp", 0.9, "zapowiedź (skrót ujęcia „miecz” od 0,6 s): Susanoo tnie mieczem, szyje opadają",
                 "świst miecza, cios"),
                ("zap_strzaly", "PP", "szarp", 0.6, "zapowiedź (skrót ujęcia „strzaly” od 0,3 s): chmara strzał spod słońca",
                 "świst strzał"),
                ("zap_burza", "PO", "szarp", 0.9, "zapowiedź (skrót ujęcia „burza” od 2,6 s): łódź przechyla się za falę, błyska",
                 "grzmot, fale"),
                ("zap_wrona", "PO", "jaz", 0.55, "zapowiedź (skrót ujęcia „wrona” od 5,5 s): wrona przelatuje nad górami",
                 "krakanie, łopot skrzydeł"),
                ("zap_blysk", "PP", "szarp", 0.85, "zapowiedź (skrót ujęcia „blysk” od 0,1 s): błysk złotego ptaka, włócznie się cofają",
                 "grzmot, potem cisza"),
            ]),
        ]),
        ("Teatr i bracia", "front teatru i kraj na scenie, potem teatr cieni za parawanem", [
            ("Tytuł", [
                ("teatr", "TYT", "naj", 4.5, "kurtyna startu rozsuwa się na front teatru w kształcie bramy torii z szyldem „SYN "
                 "SŁOŃCA”: światło już się pali, czerwone słońce dojeżdża na nitce, od dołu wysuwa się kraj, a na polanie po kolei "
                 "wysuwają się czterej bracia (pierwszy Itsuse); kamera wjeżdża do środka sceny (render.WYCINEK, KURTYNA_START)",
                 "kurtyna, gong, szelest papieru"),
            ]),
            ("Wprowadzenie", [
                # przegląd 18.11.2026: lektor mówi o pierwszym cesarzu, więc kamera i podpis pokazują Iwarebiko, nie tylko
                # Itsuse (inaczej widz bierze Itsuse za przyszłego cesarza, a po 15 s Itsuse ginie); kwestia krótsza (ok. 9 s)
                ("hak_najazd", "PO", "naj", N, "kamera najeżdża z całej sceny na Itsuse i Iwarebiko stojących na polanie, dwaj młodsi "
                 "bracia zostają za kadrem; nad Iwarebiko zjeżdża podpis „Iwarebiko, przyszły cesarz”, potem nad Itsuse „Itsuse, "
                 "najstarszy brat”", "L: Kroniki mówią, że książę Iwarebiko razem z trzema braćmi wywalczył sobie drogę na wschód "
                 "i został pierwszym cesarzem Japonii, o ile w ogóle istniał."),
            ]),
            ("Hak", [
                ("hak_rana", "Z", "stat", N, "hak (skrót ujęcia „rana” od początku): strzała trafia Itsuse w ramię, lalka się zatacza",
                 "L: Ale strzała trafiła najstarszego brata, księcia Itsuse."),
                ("hak_cien", "PŚ", "stat", 4.6, "teatr cieni: na podświetlonym parawanie cień Itsuse; z prawej wysuwa się cień łucznika, "
                 "napina łuk i strzela, strzała trafia Itsuse w ramię, Itsuse zatacza się i opada (śmierć)",
                 "L: Itsuse zmarł od tej rany, daleko od domu."),
                ("hak_burza", "PO", "szarp", N, "hak (skrót ujęcia „burza” od 0,8 s): dwie łodzie z braćmi przechylają się i znikają za "
                 "falą, zostaje łódź Iwarebiko", "L: Burza zabrała dwóch kolejnych i został tylko Iwarebiko."),
                ("hak_koronacja", "PO", "naj", N, "hak (skrót ujęcia „koronacja” od 1,0 s): tron pod baldachimem, cesarz w szacie "
                 "koronacyjnej, przed nim wyrastają skrzynki owinięte płótnem, zjeżdża zawieszka „126”",
                 "L: W 2019 roku sto dwudziesty szósty cesarz z jego rodu dostał miecz, którego nikt z żyjących nie widział."),
            ]),
        ]),
        ("Obietnica", "kraj na scenie, chorągiewki na wzgórzach", [
            ("Obietnica", [
                # reżyser 18.11.2026: „ujęcie 14 skracamy o 4 s” (12,4 → 8,4 s) — obietnica bez wrony
                ("luty", "PO", "naj", 8.4, "na wzgórzach wyskakują po kolei białe chorągiewki z czerwonym słońcem, a nad scenę zjeżdża na nitce "
                 "zawieszka „11 lutego”", "L: Pod koniec filmu będziesz wiedzieć, skąd wziął się ten miecz i czemu urodziny Japonii "
                 "są zmyślone."),
            ]),
        ]),
    ]),
    (1, "Kropla z włóczni", "Kroniki zaczynają od bogów Izanagi i Izanami, którzy włócznią wyłowili z morza pierwszą wyspę, a potem "
        "urodzili osiem wielkich wysp.", [
        ("Pływający most", "scena: morze pod chmurami", [
            ("Początek", [
                # pomost z haka do mitu (przegląd 18.11.2026: po obietnicy film skakał w „na początku…” bez słowa, po co)
                ("meduza", "PO", "naj", N, "zmiana dekoracji: na scenie tylko pasma papierowych fal pod chmurami, a między falami dryfuje "
                 "półprzezroczysta papierowa meduza", "L: Żeby zrozumieć, czemu ci bracia wierzyli, że pochodzą od słońca, wróćmy do "
                 "początku, kiedy młoda ziemia dryfowała po wodzie jak meduza."),
                ("most", "PP", "naj", N, "z chmur zjeżdża na nitkach tęczowy łuk mostu; po nim zsuwają się dwie lalki bogów: Izanagi w białej "
                 "szacie z włócznią i Izanami w czerwonej; nad bogami, kiedy staną, tabliczki „Izanami” i „Izanagi”", "L: Wtedy na pływający most niebios zeszło dwoje bogów, Izanagi i Izanami, którzy "
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
                 "a Izanagi wyciąga do niej rękę; bogini drży w ogniu, dostaje X na oczach (śmierć) i dopiero wtedy opada", "L: Ostatnim dzieckiem bogini był bóg ognia, który poparzył ją tak mocno, że umarła i odeszła "
                 "do krainy zmarłych."),
                ("yomi", "PP", "stat", N, "ciemność: Izanagi z pochodnią schodzi w głąb; z mroku wyłania się sina lalka Izanami, Izanagi cofa się, "
                 "a z boku wtacza się głaz i zamyka przejście", "L: Izanagi zszedł za nią w ciemność, ale kiedy zobaczył, jak bardzo się "
                 "zmieniła, uciekł i zatoczył głaz na wejście."),
            ]),
            ("Troje dzieci", [
                ("rzeka", "PŚ", "naj", N, "Izanagi pochyla się nad rzeką; z wody wynurzają się po kolei trzy krążki: złote słońce, srebrny księżyc "
                 "i ciemna chmura, a za nimi lalki trojga bogów; przy każdym z troje bogów tabliczka z imieniem i rolą", "L: Potem obmył się w rzece, a z jego lewego oka narodziła się Amaterasu, "
                 "bogini słońca i przodkini czterech braci, z prawego bóg księżyca, a z nosa Susanoo, bóg burzy."),
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
                # mniej imion (przegląd 18.11.2026): Uzume bez imienia, w kadrze tabliczka z rolą
                ("uzume", "PP", "stat", N, "na odwróconej kadzi tańczy bogini Uzume, tupie i wymachuje gałązkami; rząd bogów kołysze się "
                 "ze śmiechu, każdy w swoim rytmie; nad nią tabliczka „bogini tańca”, nad bogami tabliczki „HA HA!”; scena jaśniejsza niż reszta nocy", "L: Wtedy jedna z bogiń zatańczyła na odwróconej kadzi tak zuchwale, że wszyscy bogowie "
                 "wybuchnęli śmiechem."),
                # nić trzech skarbów (szkic A): lustro to pierwszy skarb cesarzy
                ("lustro", "Z", "stat", N, "głaz uchyla się, ze szczeliny pada światło; Amaterasu wychyla się, lustro na drzewie rozbłyskuje, "
                 "a zza skały wysuwa się siłacz i odsuwa głaz; nad siłaczem tabliczka „najsilniejszy z bogów”", "L: Zaciekawiona Amaterasu wyjrzała i zobaczyła w lustrze własny blask, "
                 "a to lustro stało się pierwszym z trzech świętych skarbów cesarzy Japonii."),
                ("swit", "PO", "odj", 3.2, "słońce wraca na nitce, scena jaśnieje, a przed jaskinią zjeżdża gruby sznur z białymi paskami papieru",
                 "gong, pianie kogutów"),
            ]),
        ]),
    ]),
    (3, "Miecz w ogonie węża", "Wygnany Susanoo zabija w Izumo ośmiogłowego węża i znajduje w jego ogonie miecz. Amaterasu daje wnukowi "
        "Ninigiemu lustro, klejnoty i miecz, a Ninigi schodzi z nimi na Kiusiu.", [
        ("Izumo", "scena: kraina Izumo, rzeka między górami", [
            ("Wygnanie", [
                ("wygnanie", "PP", "jaz", N, "lalka Susanoo zjeżdża na nitce z chmur nad górami i ląduje nad rzeką; rzeką spływają dwie pałeczki",
                 "L: Susanoo wygnano z nieba na ziemię, do krainy Izumo, gdzie rzeką spływały czyjeś pałeczki do jedzenia."),
                ("starcy", "PŚ", "stat", N, "w górze rzeki dwoje starców i dziewczyna; starcy kiwają się w płaczu, a za wzgórzem przesuwa się "
                 "cień ogromnego węża; tabliczki „starcy z Izumo” i „ostatnia córka”", "L: W górze rzeki płakała para starców, bo ośmiogłowy wąż pożarł już siedem ich córek i miał przyjść "
                 "po ostatnią."),
            ]),
            ("Sake", [
                ("kadzie", "PŚ", "stat", N, "dziewczyna kurczy się w grzebień, który wskakuje Susanoo we włosy; zza rampy wysuwa się rząd "
                 "ośmiu kadzi", "L: Susanoo zamienił dziewczynę w grzebień, wpiął go sobie we włosy i postawił osiem kadzi mocnego sake."),
                ("orochi", "PO", "naj", N, "zza gór wychylają się po kolei osiem głów na długich szyjach, z czerwonymi oczami",
                 "L: Wąż miał osiem głów i osiem ogonów, a był tak długi, że rozciągał się na osiem dolin i osiem wzgórz."),
                ("pije", "PP", "stat", 3.4, "głowy zanurzają się w kadziach, piją, kiwają się i jedna po drugiej opadają na wzgórza",
                 "chlupot, chrapanie"),
                # drugi hak (szkic A) i fakt (przegląd 18.11.2026): miecz z ogona węża według tradycji leży w chramie Atsuta,
                # cesarz w 2019 roku dostał jego zastępczy egzemplarz (ujęcie „koronacja”)
                ("miecz", "PŚ", "szarp", N, "Susanoo tnie mieczem: szyje opadają, z ogona wysuwa się błyszczący miecz i wznosi się nad scenę",
                 "L: Kiedy pijane głowy zasnęły, Susanoo porąbał węża i w jego ogonie znalazł miecz, który według tradycji do dziś "
                 "leży ukryty w chramie i którego nikt z żyjących nie widział."),
            ]),
        ]),
        # księżniczki kwiatów i skał (siostry, płatki) wypadają ze szkicem D (reżyser 18.11.2026 przywrócił tylko krainę zmarłych)
        ("Wnuk", "scena: niebo na chmurach, potem szczyt Takachiho na Kiusiu", [
            ("Trzy skarby", [
                ("skarby", "PŚ", "naj", N, "na chmurach Amaterasu i jej wnuk Ninigi; zjeżdżają na nitkach lustro, sznur klejnotów i miecz, "
                 "a Ninigi unosi ręce; nad Ninigim tabliczka „Ninigi, wnuk Amaterasu”", "L: Amaterasu dała lustro, klejnoty i miecz "
                 "swojemu wnukowi Ninigiemu, ale człowiek, który zbuduje z nimi kraj, jeszcze się nie urodził."),
                ("zejscie", "PO", "jaz", N, "Ninigi zjeżdża na chmurze przez kolejne warstwy chmur aż na szczyt góry; kamera jedzie z nim w dół",
                 "L: Ninigi zszedł z nieba przez osiem warstw chmur na szczyt góry Takachiho na wyspie Kiusiu."),
            ]),
        ]),
    ]),
    (4, "Na wschód", "Prawnuk Ninigiego, książę Iwarebiko, w wieku 45 lat wyrusza z braćmi z Kiusiu na wschód. Po latach rejsu po Morzu "
        "Wewnętrznym ląduje w Naniwie, ale wódz Nagasunehiko odpiera go, a strzała rani najstarszego brata Itsuse.", [
        ("Hyūga", "scena: Kiusiu, wybrzeże Hyūga", [
            ("Prawnuk", [
                ("prawnuk", "PŚ", "naj", N, "lalka Ninigiego opada pod rampę, a na jej miejscu wysuwa się młodszy książę z łukiem; z góry zjeżdża "
                 "zawieszka „Kiusiu”; tabliczka „książę Iwarebiko”", "L: Prawnuk Ninigiego, książę Iwarebiko, dorastał na Kiusiu, daleko od reszty wysp."),
                ("wschod", "PO", "naj", N, "Iwarebiko wskazuje na wschód: po prawej stronie sceny wysuwają się błękitne góry, a nad nimi wschodzi "
                 "słońce; Iwarebiko najpierw patrzy na zachód, obraca się i dopiero wtedy wskazuje", "L: Kiedy miał czterdzieści pięć lat, usłyszał, że na wschodzie leży piękna kraina otoczona niebieskimi górami."),
                ("bracia", "PŚ", "stat", N, "obok Iwarebiko wysuwają się trzej bracia, najstarszy Itsuse w niebieskiej szacie; wszyscy obracają "
                 "się na wschód; nad Itsuse tabliczka „Itsuse, najstarszy brat”", "L: Uznał, że stamtąd najlepiej będzie rządzić całym krajem, więc razem z braćmi i wojskiem wyruszył "
                 "na wschód."),
            ]),
        ]),
        ("Morze Wewnętrzne", "scena: morze między wyspami", [
            ("Rejs", [
                ("flota", "PO", "jaz", N, "łodzie z wiosłami i żaglami z maty płyną na wschód między wyspami; kamera płynie z nimi; kilkanaście łodzi na trzech pasmach fal, szybsze mijają wolniejsze",
                 "L: Płynęli wzdłuż wybrzeży Morza Wewnętrznego, a według kroniki zatrzymywali się po drodze na całe lata."),
                # postoje w portach wypadają (przegląd 18.11.2026: cięcie do 12 min, „całe lata” mówi już kwestia floty)
            ]),
        ]),
        ("Kusaka", "scena: zatoka Naniwa i góry od wschodu", [
            ("Wróg", [
                ("naniwa", "PP", "naj", N, "łodzie przybijają do brzegu zatoki; wojsko z białymi proporcami wysuwa się na brzeg, przed nim "
                 "wznoszą się góry; sześć łodzi w zatoce na przodzie sceny, cztery rzędy włóczni i wojownicy ruszają ku górom", "L: W końcu dopłynęli do zatoki Naniwa, tam gdzie dziś leży Osaka, i ruszyli przez góry do krainy Yamato."),
                ("nagasune", "PŚ", "stat", N, "zza grani wyrasta wielka lalka wodza na długich nogach, za nią las włóczni z ciemnymi proporcami; "
                 "słońce świeci zza jego pleców; tabliczka „wódz Nagasunehiko”, cztery rzędy włóczni unoszą się trzy razy w rytmie", "L: Drogę zastąpił im miejscowy wódz Nagasunehiko, czyli „książę o długich goleniach”, "
                 "ze swoim wojskiem."),
            ]),
            ("Strzała", [
                ("strzaly", "PP", "szarp", 2.2, "z gór, spod wschodzącego słońca, nadlatuje chmara strzał i wbija się w brzeg", "świst strzał"),
                # powrót do sceny z haka innymi słowami (przegląd 18.11.2026: nie powtarzać kwestii haka)
                ("rana", "Z", "stat", N, "strzała trafia Itsuse w ramię; lalka zatacza się i przyciska rękę; nad Itsuse tabliczka „AŁA!…”",
                 "L: Pamiętasz tę strzałę? Trafiła najstarszego brata, Itsuse, i wtedy Iwarebiko zrozumiał, dlaczego przegrywają."),
                ("pod_slonce", "PŚ", "stat", N, "ranny Itsuse wskazuje słońce nad górami; Iwarebiko odwraca się ku słońcu i opuszcza łuk",
                 "L: Jako potomkowie bogini słońca walczyli twarzą do słońca, więc postanowili obejść góry i uderzyć ze słońcem za plecami."),
            ]),
        ]),
    ]),
    (5, "Wrona z gór Kumano", "Itsuse umiera od rany, a burza zabiera dwóch kolejnych braci. W lasach Kumano armia pada zaczarowana, aż "
        "Takakuraji przynosi miecz z nieba; wielka wrona Yatagarasu prowadzi wojsko przez góry do Yamato.", [
        ("Półwysep Kii", "scena: morze przy półwyspie Kii", [
            ("Straty", [
                ("itsuse", "PŚ", "stat", N, "na łodzi ranny Itsuse przechyla się i powoli opada pod rampę; Iwarebiko pochyla się nad nim; Itsuse dostaje X na oczach (śmierć), zanim opadnie",
                 "L: Itsuse już nie wyzdrowiał i zmarł na łodzi, kiedy płynęli na południe."),
                ("burza", "PO", "szarp", N, "burza: fale rosną, łodzie podskakują, dwie z nich przechylają się i znikają za falą",
                 "L: Potem burza zatopiła dwie łodzie, a morze zabrało jeszcze dwóch braci."),
                # przegląd 18.11.2026: hak powiedział już „został tylko Iwarebiko” — tu nowe zdanie, które ciągnie dalej
                ("sam", "Z", "stat", N, "zbliżenie: Iwarebiko sam na łodzi, za nim puste morze i ciemne chmury",
                 "L: Iwarebiko stracił wszystkich trzech braci, a najtrudniejsze było jeszcze przed nim."),
            ]),
        ]),
        ("Kumano", "scena: góry i lasy Kumano", [
            ("Niedźwiedź", [
                ("las", "PO", "stat", 5.5, "zmiana dekoracji: wyrastają cedry Kumano, między nimi snuje się mgła, a wojsko z białymi "
                 "proporcami wchodzi w las; wojownicy z włóczniami idą w las na przodzie", "ptaki, wiatr w koronach drzew"),
                ("niedzwiedz", "PP", "stat", N, "las Kumano: spomiędzy cedrów wychodzi czarny niedźwiedź i znika, a wojownicy przewracają się "
                 "po kolei, każdy w swojej chwili; dwa rzędy wojowników, nad padającymi krążą przez chwilę gwiazdki (zamroczenie)", "L: W lasach Kumano z gęstwiny wyszedł wielki niedźwiedź i zniknął, a cała armia nagle "
                 "padła jak zaczarowana."),
                # przegląd 18.11.2026: „inny miecz”, żeby widz nie wziął go za miecz z ogona węża; bez imienia Takakuraji
                ("takakuraji", "PŚ", "stat", N, "z nieba zjeżdża na nitce przez dach spichlerza miecz; miejscowy człowiek (Takakuraji) chwyta go "
                 "i niesie do leżącego Iwarebiko; tabliczka „miejscowy człowiek”", "L: Wtedy miejscowy człowiek przyniósł mu inny miecz, który "
                 "bóg piorunów zrzucił z nieba przez dach jego spichlerza."),
                ("przebudzenie", "PP", "stat", N, "Iwarebiko podnosi się z mieczem, a za nim wstają wojownicy, jeden po drugim; cienie lasu "
                 "cofają się", "L: Kiedy Iwarebiko wziął miecz do ręki, złe moce lasu padły same, a jego wojownicy obudzili się jeden "
                 "po drugim."),
            ]),
            ("Przewodnik", [
                ("wrona", "PO", "jaz", N, "nad górami przelatuje wielka czarna wrona, a pod nią wojsko z białymi proporcami idzie przełęczą; "
                 "kamera leci z nią; tabliczka „Yatagarasu” leci z wroną; trzy kolumny wojska", "L: Z nieba przysłano mu też wielką wronę Yatagarasu, która przeprowadziła wojsko przez dzikie góry "
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
                 "znika pod nią; brat ostrzega tabliczką „PUŁAPKA!”, nad chatą po upadku belki miga dwa razy czerwony X", "L: Jeden z nich zbudował dla gościa dom z ukrytą pułapką, ale własny brat go wydał i wódz zginął w swojej "
                 "pułapce."),
            ]),
        ]),
        ("Bitwa", "scena: wzgórza Yamato, burza z gradem", [
            ("Grad", [
                ("bitwa", "PO", "jaz", N, "dwa lasy włóczni ścierają się na wzgórzach, białe i ciemne proporce; niebo ciemnieje i sypie się "
                 "papierowy grad; po trzy rzędy włóczni z każdej strony pchają się w tę i z powrotem, mocny wstrząs przy starciu, grad gęstnieje do końca", "L: Z Nagasunehiko walczył jeszcze raz, ale bitwa długo nie mogła się rozstrzygnąć, a niebo pociemniało "
                 "i spadł grad."),
                ("ptak", "PŚ", "naj", N, "z chmur zlatuje złoty ptak i siada na czubku łuku Iwarebiko; ptak rozbłyskuje",
                 "L: Wtedy na czubku jego łuku usiadł złoty ptak, który świecił jak błyskawica."),
                ("blysk", "PP", "szarp", 2.2, "błysk: ciemne włócznie chwieją się i cofają za wzgórze", "grzmot, krzyki"),
                ("order", "D", "stat", N, "detal: na nitce zjeżdża złoty order z ptakiem i kołysze się, aż stanie",
                 "L: Na pamiątkę tego ptaka Japonia przez pół wieku odznaczała żołnierzy Orderem Złotej Kani."),
            ]),
            ("Nigihayahi", [
                ("strzala_nieba", "PŚ", "stat", N, "Nagasunehiko i Iwarebiko unoszą po strzale z niebiańskim upierzeniem; za wodzem wysuwa się "
                 "lalka Nigihayahiego; tabliczka „Nigihayahi”", "L: Nagasunehiko wciąż nie chciał się poddać, bo służył innemu potomkowi bogów, Nigihayahiemu."),
                ("zdrada", "PŚ", "stat", N, "Nigihayahi unosi miecz, lalka Nagasunehiko opada pod rampę, a Nigihayahi kłania się Iwarebiko; zabójstwo w fazach: zamach, cios ze wstrząsem, X na oczach i migający X, wódz opada, jego proporzec pada, Nigihayahi przechodzi do Iwarebiko i się kłania",
                 "L: Ale Nigihayahi uznał, że przybysz ma lepsze prawo do władzy, zabił upartego wodza i przeszedł na jego stronę."),
            ]),
        ]),
    ]),
    (7, "Pierwszy cesarz", "Pod górą Unebi Iwarebiko buduje pałac Kashihara i w 660 roku p.n.e. wstępuje na tron jako pierwszy cesarz; "
        "imię Jimmu dostaje dopiero od uczonych z VIII wieku. Panuje 76 lat, umiera w wieku 127 lat, a skarby przechodzą na syna.", [
        ("Kashihara", "scena: kotlina Yamato, góra Unebi", [
            ("Pałac", [
                ("palac", "PO", "naj", N, "u stóp zielonej góry Unebi wysuwają się słupy, potem podłoga, dach z trzciny i skrzyżowane belki "
                 "na szczycie pałacu", "L: W Kashiharze, u stóp zielonej góry, kazał zbudować pałac, którego słupy, jak pisze "
                 "kronika, wbito w samą skałę."),
                ("tron", "PŚ", "naj", N, "Iwarebiko wysuwa się na ganek pałacu; zjeżdżają za nim lustro, klejnoty i miecz, a obok zawieszka "
                 "„660 p.n.e.”", "L: Pierwszego dnia nowego roku, w 660 roku przed naszą erą, wstąpił tam na tron jako pierwszy cesarz "
                 "Japonii."),
                ("imie", "Z", "stat", N, "zbliżenie: przed cesarzem zjeżdża zawieszka ze znakami 神武; pod znakami podpis „Jimmu — boska waleczność”",
                 "L: Imię Jimmu, czyli „boska waleczność”, nadali mu uczeni dopiero tysiąc czterysta lat później."),
                # żona cesarza wypada (przegląd 18.11.2026: cięcie do 12 min; wątek bez dalszego ciągu)
            ]),
        ]),
        # pola ryżowe (76 lat panowania) wypadają ze szkicem D; 127 lat „według kroniki” (Kojiki podaje 137)
        ("Panowanie", "scena: kotlina Yamato z polami ryżu", [
            ("Długie życie", [
                ("smierc", "PŚ", "stat", N, "zawieszka „127 lat”; lalka cesarza przechyla się i opada pod rampę, a lustro, klejnoty i miecz "
                 "zostają nad pustym miejscem; cesarz dostaje X na oczach i opada, pod skarbami wysuwa się jego syn z tabliczką „syn cesarza”", "L: Według kroniki zmarł, mając sto dwadzieścia siedem lat, a trzy skarby przeszły na jego syna."),
                ("pusto", "D", "stat", 2.6, "detal: pusty ganek pałacu; lustro kołysze się na nitce i łapie ostatni promień słońca; pod skarbami stoi już syn", "wiatr"),
                # hak przed aktem VIII (przegląd 18.11.2026): śmierć cesarza i „linia trwa do dziś” brzmiały jak koniec filmu
                ("linia", "PO", "odj", N, "wzdłuż wzgórz wysuwa się długi szereg małych lalek cesarzy, coraz mniejszych w głębi; trzy rzędy cesarzy w różnych strojach aż po horyzont",
                 "L: Od niego, według tradycji, zaczęła się linia cesarzy, która nie przerwała się do dziś. Ale czy on w ogóle istniał?"),
            ]),
        ]),
    ]),
    (8, "Kronika i ziemia", "Historię spisano dopiero w 712 i 720 roku na zamówienie dworu, a datę 660 p.n.e. wyliczono z chińskiej "
        "wróżby; wtedy na wyspach żyli myśliwi i rybacy. Chińskie zapiski mówią o ponad stu państewkach Wa, złotej pieczęci z 57 roku "
        "i królowej Himiko.", [
        ("Kronika", "przód sceny: stół pisarza, potem wyspy w epoce myśliwych", [
            ("712", [
                ("kronika", "PŚ", "stat", N, "zza rampy wysuwa się stół, za nim pisarz w dworskiej szacie; zwój rozwija się i pokrywa znakami, "
                 "a z góry zjeżdża zawieszka „712”; pisarz przed stołem, cały widoczny, z tabliczką „pisarz dworu”", "L: Całą tę historię spisano jednak dopiero w 712 i 720 roku, w kronikach zamówionych "
                 "przez dwór, który chciał pokazać, skąd ma prawo do władzy."),
                ("rachunek", "D", "stat", N, "detal: na nitkach zjeżdżają po kolei zawieszki „601”, „− 1260 lat” i „660 p.n.e.”",
                 "L: Datę 660 roku najpewniej wyliczono z chińskiej wróżby, według której co tysiąc dwieście sześćdziesiąt lat przychodzi "
                 "wielka przemiana."),
                ("jomon", "PO", "naj", N, "zmiana dekoracji: wzgórza bez pałacu i pól; wyrastają stożkowe chaty z trzciny i gliniane garnki, "
                 "a między nimi przechodzą myśliwi z włóczniami", "L: Tymczasem w 660 roku przed naszą erą na wyspach żyli myśliwi i rybacy, "
                 "a ryż dopiero zaczynano uprawiać na południowym zachodzie."),
            ]),
        ]),
        # kolejność śledztwa ze szkicu B: najpierw znalezisko chłopa (promyk nadziei po „nic tu nie jest prawdą”), potem czym było,
        # a chińskie zapiski z tamtych czasów na końcu (przegląd 18.11.2026: „pierwsze pewne wiadomości” po pieczęci to krok wstecz)
        ("Chińskie zapiski", "scena: mapa wysp na nitkach", [
            ("Wa", [
                ("chlop", "PŚ", "stat", N, "chłop kopie motyką rów na polu; spod ziemi wysuwa się złota pieczęć, a z góry zjeżdża zawieszka „1784”; motyka uderza w ziemię, lecą grudy; nad chłopem tabliczka „O!”",
                 "L: Ale w 1784 roku chłop, który naprawiał rów na polu, uderzył motyką w coś złotego."),
                ("pieczec", "D", "naj", N, "detal: złota pieczęć z wężem na uchwycie zjeżdża na nitce i obraca się; zawieszka „57”",
                 "L: Była to pieczęć, którą cesarz Chin w 57 roku posłał jednemu z królów Wa: dowód, że na wyspach rządzili "
                 "prawdziwi królowie na długo przed kronikami."),
                ("odcisk", "D", "stat", 2.4, "pieczęć opada na papier i unosi się, a na papierze zostaje czerwony odcisk pięciu znaków",
                 "stuk pieczęci"),
                ("wa", "PO", "stat", N, "na nitkach zjeżdża papierowa mapa wysp; na niej wyskakują dziesiątki maleńkich chorągiewek",
                 "L: Chińskie zapiski z tamtych czasów opisują kraj ludzi Wa jako ponad sto małych państewek."),
            ]),
            ("Himiko", [
                ("himiko", "PŚ", "naj", N, "za parawanem wysuwa się lalka królowej Himiko; na nitkach zjeżdżają do niej rzędy błyszczących luster; tabliczka „królowa Himiko”",
                 "L: W trzecim wieku rządziła tam królowa Himiko, która podobno trzymała wodzów w posłuszeństwie czarami i dostała od Chin sto "
                 "brązowych luster."),
            ]),
        ]),
    ]),
    (9, "Źródło słońca", "Królowie z Yamato chowają się w kurhanach w kształcie dziurki od klucza; pod koniec VII wieku kraj dostaje nazwę "
        "Nihon. W 1873 roku rząd ogłasza 11 lutego świętem (po wojnie zniesionym, od 1966 znów obchodzonym), a w 2019 roku 126. cesarz dostaje przy koronacji klejnoty i zastępczy miecz.", [
        ("Kurhany", "scena: równina z kurhanem", [
            ("Królowie", [
                ("kofun", "PO", "naj", N, "na nitkach zjeżdża plansza z kurhanem w kształcie dziurki od klucza, otoczonym fosą; zawieszka „486 m”",
                 "L: Potem władcy z Yamato zaczęli się chować w ogromnych kurhanach w kształcie dziurki od klucza, a największy ma prawie pół "
                 "kilometra długości."),
                ("haniwa", "PP", "jaz", N, "przed kurhanem wysuwają się rzędy glinianych figurek: wojownicy, konie, domki i tancerze, każda "
                 "we własnej chwili; trzy rzędy figurek, najdalszy aż po krawędź kurhanu", "L: Na ich zboczach stawiano tysiące glinianych figurek haniwa, a w środku leżeli prawdziwi władcy "
                 "Yamato, choć nikt nie wie na pewno, kim byli."),
                ("tancerz", "Z", "stat", 2.6, "zbliżenie: gliniany tancerz haniwa z uniesioną ręką; przez jego puste oczy prześwieca słońce",
                 "wiatr, stuk gliny"),
            ]),
        ]),
        ("Nihon", "cała scena, potem front teatru", [
            ("Nazwa", [
                ("nihon", "PŚ", "stat", N, "zawieszka 倭 zjeżdża, obraca się na nitce i odjeżdża, a na jej miejsce zjeżdża 日本; za nią wschodzi "
                 "czerwone słońce; pod znakami podpisy „Wa” i „Nihon — źródło słońca”", "L: Pod koniec siódmego wieku dwór nazwał kraj Nihon, czyli „źródło słońca”, bo patrząc z Chin, słońce "
                 "wschodziło właśnie tam."),
                ("luty2", "PŚ", "stat", N, "kartka kalendarza „11 lutego” zjeżdża na nitce obok zawieszki „1873”; na wzgórzach znów wyskakują "
                 "chorągiewki ze słońcem", "L: Dopiero w 1873 roku rząd w Tokio przeliczył datę z kroniki na nasz kalendarz i ogłosił jedenasty "
                 "lutego świętem, które po wojnie zniesiono, a w 1966 roku przywrócono."),
                ("koronacja", "PO", "naj", N, "przód sceny: na stojakach stają dwie skrzynki owinięte białym płótnem, a za nimi wyrasta tron pod "
                 "ośmiokątnym baldachimem; zawieszka „126”; na tronie staje cesarz w szacie koronacyjnej", "L: W 2019 roku na tron wstąpił sto dwudziesty szósty cesarz "
                 "i przyniesiono mu klejnoty oraz zastępczy miecz z ogona węża, wciąż owinięte płótnem, którego nikt nie odwija."),
            ]),
            ("Słońce", [
                ("koniec", "PO", "odj", N, "kamera wycofuje się z teatru: nad wyspami świeci czerwone słońce, światło w skrzyni gaśnie i zostaje "
                 "szyld z tytułem", "L: Nikt nie wie, czy Jimmu naprawdę żył, ale kraj, który zaczął się od kropli z włóczni, do dziś nazywa "
                 "siebie źródłem słońca."),
                # podziękowanie jak w „Pierwszym cesarzu” (reżyser 16.11.2026); tekst jest w kadrze, więc bez paska napisu
                ("dzieki", "TYT", "stat", N, "ciemna scena pod szyldem: na nitkach zjeżdżają duże papierowe tabliczki z "
                 "podziękowaniem dla widzów, potem film schodzi w czerń", "L: Dziękuję za obejrzenie! Jeśli lubisz moje filmy, "
                 "wesprzyj mnie, a dam z siebie wszystko."),
            ]),
        ]),
    ]),
]

# liczby w kwestiach czytane słowami — do liczenia czasu kwestii i do lektora (zamiana całych fraz, bo forma zależy od zdania)
SLOWNIE = {"w 660 roku": "w sześćset sześćdziesiątym roku", "Datę 660 roku": "Datę sześćset sześćdziesiątego roku",
           "w 712 i 720 roku": "w siedemset dwunastym i siedemset dwudziestym roku", "W 57 roku": "W pięćdziesiątym siódmym roku",
           "w 57 roku": "w pięćdziesiątym siódmym roku",
           "W 1784 roku": "W tysiąc siedemset osiemdziesiątym czwartym roku", "w 1784 roku": "w tysiąc siedemset osiemdziesiątym czwartym roku",
           "w 1873 roku": "w tysiąc osiemset siedemdziesiątym trzecim roku", "w 1966 roku": "w tysiąc dziewięćset sześćdziesiątym szóstym roku",
           "W 2019 roku": "W dwa tysiące dziewiętnastym roku"}


# JEZYK=en: angielska wersja filmu na kanał Paper Theatre (reżyser 17.11.2026, księga D8): kwestie z kwestie_en.py,
# lektor w lektor_en/. Polska rozpiska zostaje źródłem ujęć i ich kolejności.
JEZYK = __import__("os").environ.get("JEZYK", "pl")


def kwestia(dzwiek):
    txt = dzwiek[2:].strip() if dzwiek.startswith("L:") else ""
    return _PL2EN[txt] if txt and JEZYK == "en" else txt


def _pl2en():
    from kwestie_en import EN
    out = {}
    for _, _, _, sceny in AKTY:
        for _, _, beaty in sceny:
            for _, shots in beaty:
                for klucz, *_r, dzwiek in shots:
                    if dzwiek.startswith("L:"):
                        out[dzwiek[2:].strip()] = EN[klucz]
    return out


_PL2EN = _pl2en() if JEZYK == "en" else {}

TEMPO = 2.1  # słowa na sekundę: tempo klonu głosu autora zmierzone przy „Pierwszym cesarzu” (10.11.2026)
TEMPO_EN = 2.84  # angielski klon (TEATR, 3% wolniej, pauzy): „Pierwszy cesarz” EN, 1233 słowa w 434 s nagrań (17.11.2026)
LEKTOR = Path(__file__).resolve().parents[4] / ("output/powstanie-japonii/lektor" + ("_en" if JEZYK == "en" else ""))


def nagranie(dzwiek):
    """Długość nagranej kwestii (lektor/<klucz>.json) albo None, gdy jeszcze jej nie ma albo tekst się zmienił."""
    txt = kwestia(dzwiek)
    for f in LEKTOR.glob("*.json") if txt and LEKTOR.exists() else ():
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("text") == txt:
            return meta["duration"]
    return None


def slownie(txt):
    if JEZYK == "en":
        from kwestie_en import SLOWNIE_EN
        for k, v in SLOWNIE_EN.items():
            txt = txt.replace(k, v)
        return txt
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
    return (0.6, len(slownie(txt).split()) / (TEMPO_EN if JEZYK == "en" else TEMPO))


# Pauza po kwestii, zanim padnie cięcie (podręcznik, „Rytm” 2 i 3). Reżyser 14.11.2026 (przy „Pierwszym cesarzu”): przy
# 0,6 s „obcina zaraz po kwestii ujęcie, bo następuje następne, i jest to nienaturalne” — obraz trwa jeszcze chwilę po
# ostatnim słowie, a im większa granica (beat → scena → akt), tym dłużej, bo koniec sceny to długie trzymanie.
PAUZA_PO = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}

# Ujęcia z kwestią wydłużone o tyle sekund po kwestii, bo wydarzenie ma się skończyć na oczach widza i chwilę postać
# (wytyczne 1.8, 1.17, 1.18: we wzorcu reżyser wydłużał budowę, wojsko, tłum i podróż o 2–5 s). Przegląd 17.11.2026.
WYDLUZ = {"wyspy": 2.0, "orochi": 2.0, "miecz": 1.5, "flota": 2.5, "naniwa": 2.0, "nagasune": 1.5, "itsuse": 1.5,
          "niedzwiedz": 1.5, "przebudzenie": 1.5, "wrona": 1.5, "bitwa": 2.5, "zdrada": 1.5, "palac": 2.5, "smierc": 1.5,
          "linia": 2.0, "haniwa": 2.5, "koronacja": 1.5, "uzume": 1.0, "rana": 1.0, "pulapka": 1.0, "dzieki": 0.7,
          # reżyser 18.11.2026: „wydłuż niektóre za krótkie ujęcia” — Ninigi stoi już na szczycie (zejście)
          "zejscie": 2.0}


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
                        sec = round(sec + WYDLUZ.get(klucz, 0.0), 1)
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
