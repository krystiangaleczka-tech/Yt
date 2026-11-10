"""Rozpiska filmu „Pierwszy cesarz” (teatr papierowy, ok. 9 minut): akt → scena → beat → ujęcie.

ujęcie: (klucz, kadr, ruch, sekundy, opis wydarzenia, dźwięk)
- klucz — nazwa funkcji ujęcia w output/pierwszy-cesarz/render.py (`s_<klucz>`); brak funkcji = ujęcie do narysowania;
- kadr i ruch — skróty jak w pozostałych filmach (docs/filmy/oddzial-c/ujecia/buduj.py);
- sekundy — None: długość liczy się z kwestii (oddech 0,6 s + ok. 2,6 słowa/s + pauza 0,6 s); liczba: ujęcie bez słów;
- dźwięk zaczynający się od „L:” to kwestia lektora (pełne zdanie; liczby czytane słowami są w SLOWNIE).
"""
import json
from functools import lru_cache
from pathlib import Path

N = None
AKTY = [
    (1, "Zakładnik", "Chłopiec z rodziny wroga rodzi się w oblężonym Handanie; kupiec Lü Buwei wywozi jego ojca do Qin, a "
        "dziewięcioletni Zheng wraca do kraju, którego nie zna, i w wieku trzynastu lat zostaje królem.", [
        ("Teatr się otwiera", "scena teatru papierowego", [
            ("Otwarcie", [
                ("teatr", "TYT", "naj", 6.5, "front teatru z tytułem na gzymsie: w ciemnej skrzyni zapala się światło, słońce zjeżdża na nitce, "
                 "od dołu wysuwają się góry, równina i miasto; kamera wjeżdża do środka sceny", "gong, szelest papieru, skrzyp bloczków"),
            ]),
            ("Siedem chorągwi", [
                ("choragwie", "PO", "naj", N, "na wzgórzach wyskakuje po kolei siedem chorągwi, każda w barwie i ze znakiem swojego królestwa; "
                 "ostatnia, czarna chorągiew Qin staje z lewej", "L: Dawno temu tę ziemię dzieliło siedem królestw, a każde chciało mieć ją całą."),
            ]),
        ]),
        ("Handan", "scena: brama miasta Handan pod niebieską chorągwią Zhao", [
            ("Syn zakładnika", [
                ("handan", "PP", "naj", N, "kamera podjeżdża pod bramę miasta; przy niebieskiej chorągwi Zhao wysuwa się lalka ojca-zakładnika, "
                 "a obok niej mała lalka chłopca", "L: W jednym z nich, w mieście Handan, urodził się chłopiec imieniem Zheng, syn księcia z Qin "
                 "oddanego wrogom jako zakładnik."),
                ("oblezenie", "PŚ", "stat", N, "za wzgórzem przesuwa się las włóczni z czarnymi proporcami Qin; ojciec i chłopiec cofają się pod bramę, "
                 "niebieska chorągiew drży", "L: Qin właśnie oblegało to miasto, więc sąsiedzi mieli powód, żeby nienawidzić chłopca z rodziny wroga."),
            ]),
            ("Kupiec", [
                ("kupiec", "PŚ", "naj", N, "obok ojca wysuwa się lalka kupca w purpurowym obszyciu, za nim wtacza się wóz ze skrzynią, a na rampie "
                 "rośnie stos monet", "L: Ojca wypatrzył jednak bogaty kupiec Lü Buwei, który uznał, że książę na wygnaniu to towar, na którym "
                 "można zarobić królestwo."),
                ("ucieczka", "PP", "jaz", N, "noc: wóz z ojcem i kupcem odjeżdża na zachód obok włóczni straży; mały chłopiec zostaje pod bramą sam",
                 "L: Kupiec przekupił straże i wywiózł księcia do Qin, a chłopiec został w Handanie wśród wrogów."),
                ("sam", "Z", "stat", 2.4, "zbliżenie małej lalki pod wielką bramą: za nią przechodzą włócznie straży, lalka cofa się pod mur",
                 "kroki straży, wiatr"),
            ]),
        ]),
        ("Powrót", "droga na zachód i przód sceny", [
            ("Do Qin", [
                ("powrot", "PP", "jaz", N, "dzień: wóz z małą lalką jedzie przez wzgórza na zachód, kamera idzie z nim aż do czarnej chorągwi Qin",
                 "L: Miał dziewięć lat, kiedy pozwolono mu wreszcie wyjechać do kraju, którego nigdy nie widział."),
                ("krol13", "PŚ", "naj", N, "przód sceny: mała lalka Zhenga wysuwa się zza rampy, a z góry zjeżdża na nitce zawieszka „247 p.n.e.”; "
                 "lalka unosi się i prostuje", "L: Trzy lata później jego ojciec już nie żył i trzynastoletni Zheng został królem Qin."),
            ]),
        ]),
    ]),
    (2, "Król chłopiec", "Za małego króla rządzi kanclerz Lü Buwei. Dorosły Zheng tłumi bunt, odprawia kanclerza i bierze za doradcę "
        "Li Si, który radzi podbić sąsiadów; Qin jest na to gotowe.", [
        ("Regent", "sala tronowa", [
            ("Kanclerz", [
                ("regent", "PO", "stat", N, "sala tronowa: mały król stoi na podwyższeniu, obok wysuwa się dwa razy większa lalka kanclerza; "
                 "klęczący urzędnicy kłaniają się kanclerzowi, a mały król znika w jego cieniu", "L: Rządził za niego kupiec, teraz kanclerz Lü Buwei, "
                 "a chłopiec na tronie uczył się patrzeć i milczeć."),
                ("nauka", "Z", "naj", N, "zbliżenie małego króla; za nim zjeżdżają na nitkach dwie zawieszki: „nagroda” i „kara”",
                 "L: Uczył się też tego, co głosili jego nauczyciele: że ludzie słuchają tylko nagrody i kary."),
            ]),
            ("Bunt", [
                ("dorosl", "PŚ", "stat", N, "mała lalka króla chowa się pod rampę, a na jej miejscu wysuwa się duża; w oknach sali czerwienieje "
                 "łuna i przesuwają się włócznie", "L: Kiedy dorósł, na dworze wybuchł bunt, bo kochanek jego matki chciał posadzić na tronie "
                 "własnych synów."),
                ("bunt", "PP", "szarp", 1.8, "okna sali: włócznie buntowników i straży zderzają się, łuna migocze", "szczęk broni, krzyki"),
                ("odprawa", "PŚ", "stat", N, "król pochyla się z wyciągniętą ręką; lalka kanclerza odwraca się i odjeżdża ku wyjściu, a urzędnicy "
                 "kłaniają się teraz królowi", "L: Zheng stłumił bunt w kilka dni, a kanclerza, który wprowadził spiskowca na dwór, "
                 "odprawił z urzędu."),
                ("trucizna", "D", "stat", N, "kanclerz stoi sam na skraju sceny, przed nim czarka z brązu; lalka powoli opada pod rampę, czarka zostaje",
                 "L: Lü Buwei wypił truciznę, zanim dotarł na wygnanie."),
            ]),
            ("Doradca", [
                ("lisi", "PŚ", "naj", N, "obok króla wysuwa się lalka Li Si w zielonym obszyciu i kłania się; urzędnicy klęczą twarzą do króla",
                 "L: Od tej pory król nie miał nad sobą nikogo, a najbliżej niego stanął nowy doradca, Li Si."),
                ("mapa", "PP", "naj", N, "na nitkach zjeżdża do sali mapa z siedmiu kawałków barwnego papieru; Li Si pochyla się ku niej, a czarny "
                 "kawałek Qin wysuwa się na sąsiada", "L: Li Si powtarzał mu, że sześć królestw trzeba połknąć teraz, póki są skłócone i słabe."),
            ]),
        ]),
        ("Machina Qin", "scena: kraj Qin, wzgórza i równina", [
            ("Wojsko", [
                ("machina", "PO", "naj", N, "za wzgórzami wyrastają rząd za rzędem lasy włóczni z czarnymi proporcami",
                 "L: Qin było gotowe, bo od stu lat każdy chłop był tu żołnierzem, a awans dostawało się za głowy zabitych wrogów."),
                ("kusze", "PP", "stat", N, "zza wzgórza wylatuje chmara papierowych strzał, zatacza łuk przez niebo i wbija się w zbocze góry",
                 "L: Jego kusznicy strzelali z broni składanej z jednakowych części, które pasowały do każdej kuszy."),
            ]),
            ("Kanał", [
                ("kanal", "PP", "pan", N, "po równinie rozwija się niebieska wstęga kanału, a wzdłuż niej wyskakują zielone poletka",
                 "L: Pomógł mu nawet wróg: inżynier przysłany po to, żeby zrujnować Qin wielką budową, wykopał kanał, który wykarmił jego armię."),
            ]),
        ]),
    ]),
    (3, "Wojna i zamach", "W 230 roku p.n.e. Qin rusza na wschód: pada Han, potem Zhao. Książę Yan wysyła zamachowca Jing Ke ze sztyletem "
        "ukrytym w mapie; król ucieka dookoła kolumny i zabija go własnym mieczem.", [
        ("Pierwsze podboje", "scena: droga przez wzgórza na wschód", [
            ("Wymarsz", [
                ("wymarsz", "PP", "jaz", N, "król wskazuje wschód; za wzgórzem rusza las włóczni z czarnymi proporcami, jeździec na przedzie; "
                 "kamera jedzie z wojskiem", "L: W 230 roku przed naszą erą wojsko Qin ruszyło na wschód i zaczęło od najsłabszego sąsiada."),
                ("han", "PŚ", "stat", 1.5, "jeździec mija zieloną chorągiew Han: chorągiew przechyla się i pada", "tętent, trzask drzewca"),
                ("zhao", "PP", "naj", N, "pada niebieska chorągiew Zhao; pod bramą Handanu, tam gdzie stał kiedyś mały chłopiec, staje duża lalka króla",
                 "L: Dwa lata później padło Zhao, a król wrócił do Handanu i policzył się z tymi, którzy dręczyli jego rodzinę."),
            ]),
            ("Poselstwo", [
                ("poselstwo", "PP", "jaz", N, "spod turkusowej chorągwi Yan rusza na zachód wóz ze skrzynią; chorągiew kołysze się za nim",
                 "L: Sąsiedzi wiedzieli już, co ich czeka, więc książę Yan wysłał do Qin człowieka, który miał zabić króla."),
            ]),
        ]),
        ("Zamach", "sala tronowa", [
            ("Podarunki", [
                ("dary", "PŚ", "stat", N, "sala: po prawej wysuwa się niski stół, a za nim lalka Jing Ke w jasnym obszyciu; na stole stają "
                 "szkatuła i zwinięta mapa, król stoi po lewej", "L: Jing Ke przyniósł dwa podarunki: głowę zbiegłego generała i mapę ziem, które Yan "
                 "rzekomo oddawało."),
                ("sztylet", "D", "stat", N, "detal: zwój rozwija się po blacie i na samym końcu odsłania sztylet",
                 "L: W zwiniętej mapie był ukryty sztylet."),
                ("atak", "PŚ", "szarp", 1.4, "Jing Ke rzuca się ze sztyletem przez salę, król odskakuje w tył", "krzyk, tupot"),
            ]),
            ("Kolumna", [
                ("kolumna", "PP", "stat", N, "król ucieka dookoła kolumny: znika za nią i wychodzi z drugiej strony, zamachowiec krok za nim",
                 "L: Król uciekał dookoła kolumny, bo miecz miał tak długi, że nie mógł go wyciągnąć z pochwy."),
                ("lekarz", "PŚ", "stat", N, "klęczący dworzanin unosi się i ciska torbą z lekami: torba leci łukiem i trafia zamachowca, "
                 "który się zatacza", "L: Dworzanom nie wolno było wnosić broni, więc lekarz rzucił w zamachowca torbą z lekami."),
                ("cios", "Z", "szarp", 1.7, "nad ramieniem króla wysuwa się miecz i zatacza łuk; lalka Jing Ke przechyla się i osuwa pod kolumnę",
                 "świst miecza, upadek"),
                ("pretekst", "PŚ", "odj", N, "Jing Ke leży pod kolumną, sztylet tkwi wbity w nią; król stoi nieruchomo, urzędnicy podnoszą się po kolei",
                 "L: Jing Ke zginął pod kolumną, a król dostał pretekst, którego potrzebował do wojny z Yan."),
            ]),
        ]),
    ]),
    (4, "Koniec sześciu królestw", "Padają Wei, Chu, Yan i Qi. W 221 roku p.n.e. cały kraj ma jednego władcę, który nazywa się "
        "Pierwszym Cesarzem i przetapia broń pokonanych na posągi.", [
        ("Cztery królestwa", "scena: wzgórza i miasto", [
            ("Wei i Chu", [
                ("ksiaze", "PP", "stat", N, "jeździec w czarnym przywozi pod turkusową chorągiew Yan zwój z pieczęcią; chorągiew pochyla się nisko, "
                 "ale włócznie Qin nie zatrzymują się", "L: Książę, który wysłał zamachowca, zginął z rozkazu własnego ojca, ale Yan to nie uratowało."),
                ("wei", "PO", "naj", N, "miasto pod żółtą chorągwią Wei: od rzeki podnoszą się arkusze niebieskiego papieru, zalewają mury, "
                 "a chorągiew przewraca się w wodę", "L: Stolica Wei miała mury nie do zdobycia, więc generał skierował na nią rzekę i po trzech "
                 "miesiącach mury same zmiękły."),
                ("chu", "PP", "jaz", N, "przed czerwoną chorągwią Chu przesuwają się cztery rzędy włóczni, jeden za drugim, aż zasłaniają wzgórza",
                 "L: Na wielkie Chu król posłał sześćset tysięcy ludzi, czyli prawie wszystko, co miał."),
                ("chu_yan", "PŚ", "pan", 2.5, "czerwona chorągiew Chu chwieje się dłużej niż inne i pada, turkusowa Yan zaraz po niej", "bęben, trzask"),
            ]),
            ("Qi", [
                ("qi", "PP", "stat", N, "jeździec staje przed ostatnią, fioletową chorągwią Qi; z góry zjeżdża zawieszka „221 p.n.e.”, "
                 "a chorągiew sama kładzie się na ziemi", "L: Ostatnie królestwo poddało się bez walki w 221 roku przed naszą erą."),
                ("mapa2", "D", "stat", N, "mapa na nitkach: czarny papier Qin nasuwa się po kolei na sześć barwnych kawałków, aż cała jest czarna",
                 "L: W dziewięć lat czarna barwa Qin przykryła całą mapę."),
            ]),
        ]),
        ("Jeden władca", "cała scena, potem lewy brzeg", [
            ("Czarne chorągwie", [
                ("czarne", "PO", "odj", N, "w miejscach sześciu powalonych chorągwi wstają po kolei czarne chorągwie Qin",
                 "L: Wtedy po raz pierwszy cały kraj miał jednego władcę."),
            ]),
            ("Pierwszy Cesarz", [
                ("cesarz", "Z", "naj", N, "zbliżenie lalki Zhenga: za jego plecami zjeżdżają na nitkach dwie chorągwie ze smokiem, "
                 "a lalka prostuje się i unosi", "L: Tytuł króla wydał mu się za mały, więc ułożył sobie nowy: Pierwszy Cesarz."),
                ("posagi", "PP", "naj", N, "włócznie pokonanych opadają do trójnogu z brązu, z którego bije łuna; za nim wysuwa się olbrzymi posąg, "
                 "wyższy niż mury miasta", "L: Broń pokonanych kazał przetopić na dwanaście olbrzymich posągów z brązu."),
            ]),
        ]),
    ]),
    (5, "Jeden kraj", "Cesarz łączy kraj drogami i kanałami, dzieli go na prowincje, objeżdża go i każe ryć swoją chwałę w kamieniu; "
        "ujednolica pismo, monetę i miary, a mury północy łączy w jeden.", [
        ("Porządek", "scena: droga przez wzgórza, wzgórza całego kraju", [
            ("Drogi i prowincje", [
                ("drogi", "PP", "jaz", N, "cesarz wskazuje drogę, a po niej toczy się wóz ze skrzynią, podskakuje na koleinach i mija czarne chorągwie",
                 "L: Połączył kraj drogami, po których wozy jeździły na osiach jednej szerokości."),
                ("prowincje", "PO", "stat", N, "na wzgórzach całego kraju wysuwają się po kolei małe lalki urzędników z deszczułkami, każda przy "
                 "czarnej chorągwi", "L: Kraj podzielił na trzydzieści sześć prowincji i posłał do nich urzędników, których mógł w każdej chwili "
                 "odwołać."),
                ("rody", "PP", "jaz", N, "trzy wozy ze skrzyniami, każdy dalej i mniejszy, ciągną jeden za drugim ku bramie stolicy",
                 "L: Dawnym rodom kazał porzucić zamki, więc sto dwadzieścia tysięcy rodzin przeniosło się do stolicy, pod jego oko."),
            ]),
            ("Podróże i kanał", [
                ("stela", "PP", "naj", N, "powóz z czarną chorągwią staje pod górą; kamera unosi się na jej szczyt, gdzie wysuwa się kamienna stela "
                 "ze znakami", "L: Jeździł po kraju i na świętych górach kazał ryć w kamieniu, że przyniósł światu pokój."),
                ("kanal2", "PP", "pan", N, "wzdłuż drogi rozwija się druga niebieska wstęga kanału i wpływają na nią dwie papierowe łodzie",
                 "L: Na południu jego inżynierowie połączyli kanałem dwie rzeki, żeby armia mogła popłynąć jeszcze dalej."),
            ]),
        ]),
        ("Jedna miara wszystkiego", "przód sceny: stół pisarzy", [
            ("Pismo", [
                ("pismo", "PŚ", "stat", N, "zza rampy wysuwa się stół ze zwojem bambusowym, potem klęczący pisarz; księga z deszczułek wsuwa się "
                 "pod jego pędzel i pisarz zaczyna pisać", "L: Kazał też wszystkim pisać tymi samymi znakami, żeby jego rozkaz rozumiano "
                 "w każdej prowincji."),
            ]),
            ("Moneta i miara", [
                ("moneta", "D", "stat", N, "detal stołu: moneta z kwadratową dziurką toczy się po blacie i kładzie przy stosie monet",
                 "L: Wszędzie płacono odtąd tą samą monetą."),
                ("miara", "D", "stat", N, "na stół zjeżdża na nitce waga, a zaraz po niej brązowy odważnik; waga kołysze się, aż stanie",
                 "L: Odważniki i miary też miały być wszędzie jednakowe."),
            ]),
        ]),
        ("Mur", "góry na północy", [
            ("Mur", [
                ("mur", "PO", "pan", N, "zza grani gór wysuwają się kolejne odcinki muru i wieże strażnicze, od zachodu ku miastu; kamera idzie za murem",
                 "L: Na północy kazał połączyć stare mury w jeden, żeby zatrzymać jeźdźców ze stepu."),
                ("robotnicy", "PP", "pan", N, "po grani pod murem suną sylwetki ludzi z koszami na nosidłach; jeden po drugim przystają i znikają za granią",
                 "L: Budowały go setki tysięcy żołnierzy, skazańców i chłopów, a wielu zostało pod murem na zawsze."),
                ("ognie", "Z", "stat", 2.6, "na wieży strażniczej zapala się ogień sygnałowy, a po chwili odpowiada mu ogień na następnej wieży",
                 "trzask ognia, wiatr"),
            ]),
        ]),
    ]),
    (6, "Ogień i strach", "Cesarz pali księgi, karze uczonych i zsyła syna na północ. Uchodzi z zamachu i boi się już tylko śmierci: "
        "śle statki po eliksir i łyka rtęć.", [
        ("Ogień", "przód sceny: stół pisarzy i trójnóg", [
            ("Księgi", [
                ("ksiegi", "PŚ", "stat", N, "uczony z deszczułką wysuwa się obok stołu; cesarz pochyla się z wyciągniętą ręką, zwój bambusowy leci ze stołu "
                 "do trójnogu, płomienie z bibuły skaczą w górę, a scena czerwienieje", "L: Kiedy uczeni zaczęli chwalić dawne czasy, kazał spalić "
                 "ich księgi."),
                ("popiol", "D", "stat", 2.2, "detal trójnogu: zwój czernieje i zapada się, płomienie przygasają", "trzask ognia, cisza"),
                ("uczeni", "PŚ", "stat", N, "obok uczonego wysuwają się dwaj następni, po czym wszyscy trzej po kolei opadają pod rampę; czwarta lalka, "
                 "w niebieskim obszyciu — książę Fusu — kłania się cesarzowi, odwraca i odjeżdża ze sceny", "L: Rok później kazał stracić kilkuset "
                 "uczonych, a własnego syna Fusu, który się za nimi ujął, zesłał na północ pod mur."),
            ]),
        ]),
        ("Strach", "przód sceny o zmierzchu, droga nocą", [
            ("Zmierzch", [
                ("zmierzch", "PP", "odj", N, "słońce zjeżdża na nitce za góry, scena sinieje; stół z pisarzem i trójnóg chowają się pod rampę, "
                 "cesarz zostaje sam, a nad górami staje papierowy księżyc", "L: Został mu już tylko jeden wróg, którego nie umiał pokonać, "
                 "czyli własna śmierć."),
                ("mlot", "PP", "szarp", N, "noc: drogą jadą dwa powozy; zza wzgórza leci żelazny młot i miażdży pierwszy z nich, drugi staje w miejscu",
                 "L: Podczas jednej z podróży żelazny młot zmiażdżył powóz jadący tuż obok jego powozu."),
            ]),
        ]),
        ("Eliksir", "morze, potem przód sceny", [
            ("Morze", [
                ("morze", "PO", "naj", N, "morze: cztery pasma papierowych fal wysuwają się od dołu i kołyszą w przeciwne strony, na horyzoncie "
                 "wyrasta wyspa z górą", "L: Słał więc statki na Wschodnie Morze, bo słyszał, że na tamtejszych wyspach mieszkają nieśmiertelni."),
                ("xufu", "PP", "jaz", N, "trzy papierowe dżonki płyną po falach ku wyspie, maleją i znikają za horyzontem",
                 "L: Mag Xu Fu popłynął tam z tysiącami chłopców i dziewcząt i nigdy nie wrócił."),
                ("puste", "PO", "stat", 2.6, "puste morze pod księżycem; ostatni żagiel znika za falą", "fale, cisza"),
                ("rtec", "D", "stat", N, "przy cesarzu wysuwa się czarka z brązu; na nitkach zjeżdżają do niej jedna po drugiej srebrne kulki, "
                 "a lalka cesarza pochyla się nad czarką", "L: Podobno łykał też pigułki z rtęcią, które miały przedłużać życie, a najpewniej "
                 "je skracały."),
            ]),
        ]),
    ]),
    (7, "Gliniana armia", "Cesarz ukrywa się w pałacach, czyta wróżbę na meteorycie, buduje pałac i grobowiec z glinianą armią. "
        "W 210 roku p.n.e. umiera w podróży.", [
        ("Znaki", "sala nocą, potem wzgórza", [
            ("Ukryty", [
                ("przejscia", "PP", "pan", N, "sala nocą: lalka cesarza przesuwa się za kolumnami, znika za jedną i wychodzi zza następnej; "
                 "lampy gasną za nim po kolei", "L: Cesarz krył się teraz w pałacach połączonych zakrytymi przejściami, żeby nikt nie wiedział, "
                 "gdzie śpi."),
                ("meteor", "PO", "stat", N, "noc: z nieba spada kamień z ognistym ogonem i ląduje na wzgórzu; przy nim zjeżdża zawieszka ze znakami",
                 "L: Kiedy spadł meteoryt, ktoś wyrył na nim, że Pierwszy Cesarz umrze, a jego ziemia zostanie podzielona."),
            ]),
            ("Budowy", [
                ("palac", "PP", "naj", N, "za wzgórzami rośnie piętro po piętrze olbrzymi pałac, wyższy od góry",
                 "L: Zaczął też budować pałac tak wielki, że w jednej jego sali miało się zmieścić dziesięć tysięcy ludzi."),
                ("kopiec", "PO", "pan", N, "po prawej wyrasta kopiec grobowca, a po jego zboczu suną sylwetki ludzi z koszami",
                 "L: A od pierwszego roku panowania siedemset tysięcy ludzi kopało mu grobowiec pod górą Li."),
            ]),
        ]),
        ("Armia", "cała scena nocą", [
            ("Żołnierze z gliny", [
                ("armia", "PO", "jaz", N, "zza wzgórz i zza rampy wysuwają się rząd po rzędzie gliniani żołnierze, każdy we własnej chwili",
                 "L: Kazał ulepić z gliny tysiące żołnierzy naturalnej wielkości, żeby strzegli go także po śmierci."),
                ("twarze", "Z", "pan", 2.6, "kamera przesuwa się po twarzach pierwszego rzędu; ostatni żołnierz dojeżdża na miejsce spóźniony",
                 "cisza, jeden stuk"),
                ("rzeki", "PP", "jaz", N, "między rzędami żołnierzy suną srebrne wstęgi rzek z rtęci",
                 "L: Według kronik w grobowcu płynęły rzeki z rtęci, a kusze miały same strzelać do każdego, kto wejdzie."),
            ]),
        ]),
        ("Ostatnia podróż", "droga nocą, potem przód sceny", [
            ("Choroba", [
                ("podroz", "PP", "jaz", N, "noc: powóz cesarza z czarną chorągwią toczy się drogą na wschód, coraz wolniej, i staje",
                 "L: W 210 roku przed naszą erą wyruszył w kolejną podróż po kraju i w drodze zachorował."),
                ("koniec", "PŚ", "stat", N, "z góry zjeżdża zawieszka „210 p.n.e.”; lalka cesarza przechyla się i powoli opada pod rampę, "
                 "chorągwie ze smokiem zostają nad pustym miejscem", "L: Umarł latem, daleko od stolicy, mając czterdzieści dziewięć lat."),
            ]),
        ]),
    ]),
    (8, "Upadek", "Li Si i eunuch Zhao Gao tają śmierć cesarza, fałszują list do Fusu i sadzają na tronie Huhaia. Po roku wybucha "
        "powstanie, po piętnastu latach nie ma dynastii. Glinianą armię odkrywają chłopi w 1974 roku.", [
        ("Spisek", "droga nocą, mur na północy, sala tronowa", [
            ("Powóz", [
                ("spisek", "PŚ", "stat", N, "przy powozie wysuwają się dwie lalki: Li Si w zielonym i eunuch Zhao Gao w szarym; pochylają się ku sobie, "
                 "a na powóz opada czarna zasłona", "L: Kanclerz Li Si i eunuch Zhao Gao zataili jego śmierć, bo chcieli sami wybrać następcę."),
                ("ryby", "PP", "jaz", N, "powóz jedzie dalej, a za nim wóz z górą ryb; kamera jedzie z nimi",
                 "L: Powóz jechał dalej jak gdyby nigdy nic, a żeby upał nie zdradził prawdy, obok postawiono wozy z solonymi rybami."),
            ]),
            ("List", [
                ("list", "PŚ", "stat", N, "pod murem na północy: do lalki Fusu zjeżdża na nitce zwój; Fusu pochyla się nad nim i opada za wzgórze",
                 "L: Najstarszy syn dostał sfałszowany list, w którym ojciec kazał mu odebrać sobie życie, i posłuchał."),
                ("huhai", "PŚ", "naj", N, "sala: na podwyższeniu mała lalka w koronie, za nią wyrasta wielka szara lalka eunucha i zasłania lampę",
                 "L: Tron dostał młodszy syn Huhai, który słuchał eunucha we wszystkim."),
            ]),
        ]),
        ("Powstanie", "cała scena", [
            ("Kraj wstaje", [
                ("powstanie", "PO", "naj", N, "zza wzgórz całego kraju wyrastają włócznie z czerwonymi szmatami; czarne chorągwie zaczynają padać "
                 "jedna po drugiej", "L: Już rok później chłopi pędzeni do służby na granicy wzniecili powstanie i poszedł za nimi cały kraj."),
                ("upadek", "PO", "odj", N, "padają ostatnie czarne chorągwie, zrywają się nitki chorągwi ze smokiem, a miasto staje w czerwonej łunie",
                 "L: Dynastia, która miała trwać dziesięć tysięcy pokoleń, upadła po piętnastu latach."),
                ("cisza", "PO", "stat", 3.6, "świt: gliniani żołnierze zapadają się pod ziemię, księżyc odjeżdża w górę, a słońce wraca na nitce; "
                 "na scenie zostaje mur na grani i ani jednej chorągwi", "wiatr"),
            ]),
        ]),
        ("Po dwóch tysiącach lat", "wzgórza w dzień, potem front teatru", [
            ("Studnia", [
                ("studnia", "PŚ", "stat", N, "dzień: sylwetka chłopa kopie motyką na wzgórzu; spod ziemi wysuwa się gliniana głowa, potem cały "
                 "żołnierz, a z góry zjeżdża zawieszka „1974”", "L: Glinianą armię znaleźli dopiero w 1974 roku chłopi, którzy kopali studnię."),
                ("grobowiec", "PO", "naj", N, "kopiec grobowca w słońcu, nietknięty; na jego szczycie stoi sosna",
                 "L: Samego grobowca nikt do dziś nie otworzył."),
            ]),
            ("Qin", [
                ("qin", "PO", "odj", N, "kamera wycofuje się z teatru: mur na górach i gliniana armia, potem światło w skrzyni gaśnie "
                 "i zostaje sam szyld z tytułem", "L: Zostało po nim słowo, którym do dziś nazywamy ten kraj, bo Chiny to najpewniej dawne Qin."),
            ]),
        ]),
    ]),
]

# liczby w kwestiach czytane słowami — do liczenia czasu kwestii
SLOWNIE = {"230": "dwieście trzydziestym", "221": "dwieście dwudziestym pierwszym", "210": "dwieście dziesiątym",
           "1974": "tysiąc dziewięćset siedemdziesiątym czwartym"}


def kwestia(dzwiek):
    return dzwiek[2:].strip() if dzwiek.startswith("L:") else ""


TEMPO = 2.1  # słowa na sekundę: klon głosu autora czyta wolniej niż przyjęte wcześniej 2,6
LEKTOR = Path(__file__).resolve().parents[4] / "output/pierwszy-cesarz/lektor"


def nagranie(dzwiek):
    """Długość nagranej kwestii (lektor/<klucz>.json) albo None, gdy jeszcze jej nie ma albo tekst się zmienił."""
    txt = kwestia(dzwiek)
    for f in LEKTOR.glob("*.json") if txt and LEKTOR.exists() else ():
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("text") == txt:
            return meta["duration"]
    return None


def okno_kwestii(dzwiek):
    """(start, długość) kwestii w ujęciu: oddech 0,6 s, potem nagranie lektora — a zanim powstanie, tempo lektora
    zmierzone na pierwszych nagraniach klonu głosu (ok. 2,1 słowa na sekundę, 10.11.2026)."""
    txt = kwestia(dzwiek)
    if not txt:
        return (0.0, 0.0)
    real = nagranie(dzwiek)
    if real:
        return (0.6, real)
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    return (0.6, len(txt.split()) / TEMPO)


def ujecia(akt=None):
    """Płaska lista ujęć: (akt, nr w akcie, klucz, kadr, ruch, sekundy, opis, dźwięk). Długość ujęcia z kwestią liczy się
    z kwestii; sąsiednie ujęcia różnią się co najmniej o ¼ s (podręcznik, „Rytm” 2)."""
    out, prev = [], None
    for n, _, _, sceny in AKTY:
        k = 0
        for _, _, beaty in sceny:
            for _, shots in beaty:
                for klucz, kadr, ruch, sec, opis, dzwiek in shots:
                    k += 1
                    if sec is None:
                        sec = round(0.6 + okno_kwestii(dzwiek)[1] + 0.6, 1)
                        if okno_kwestii(dzwiek)[1] > 6.5:  # długie zdanie: dłuższy oddech po nim
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
