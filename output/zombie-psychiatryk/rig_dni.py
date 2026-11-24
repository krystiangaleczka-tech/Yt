"""Gra aktorska (rig) ujęć wariantu A, które dotąd stały w miejscu: dzień → ujęcie → postać → akcja (rig_a.py).

Numer ujęcia jak w FNS dnia (0 = karta tytułowa). Akcje: mowi (usta z okna kwestii, akcent głową, gest ręki),
slucha, kiwa, kreci, odwraca, patrzy (wraca=… — wraca na wprost), w_gore, w_dol, wzrusza, nachyla, cofa,
wstrzymuje, oddycha (tempo w Hz), rozglada, wzdycha, budzi, kolysze, ciezar, gest, kaszle, przelyka;
parametry: t (start, ujemny od końca), d (czas ruchu), strona (-1 lewo / 1 prawo; domyślnie tam, gdzie ujęcie
kieruje wzrok), sila, ile, wolno, reka.
Komentarz: opis ujęcia z rozpiski | kwestia. Ujęcie bez wpisu rysuje się bez zmian.
Bez rigu zostają celowo: twarze za szybą i w okienkach (otwór przycina — WYTYCZNE 1.1), rzeczy trzymane przy
twarzy (słuchawka, kubek, ręcznik, lornetka), dłoń na ustach, ujęcia, w których bezruch pana Henryka jest treścią.
"""

RIG = {
    1: {
        9: {'narrator': ('patrzy', {"wraca": -0.6})},  # narrator patrzy na szybę, twarze za nią | L: Za szybą stał cały mój oddział.
        10: {'narrator': 'wstrzymuje'},  # narrator wstrzymuje oddech, policzki nadęte | cisza
        12: {'narrator': 'rozglada'},  # boczne drzwi dyżurki uchylają się; narrator wysuwa się plecami do ścia | L: Potem wyszedłem bokiem.
        15: {'narrator': 'wstrzymuje'},  # twarz narratora, wstrzymany oddech | 
        17: {'narrator': 'cofa'},  # narrator rozpoznaje pacjenta | L: Poznałem pana Stasia z czwórki.
        24: {'narrator': 'wzdycha'},  # narrator powtarza; jego oddech zwalnia | L: Zrobiłem to samo.
        35: {'zosia': ('patrzy', {"wraca": -0.5})},  # Zosia za kratą z nożyczkami, opuszcza je, gdy ich poznaje | L: A pod lampą stała Zosia z nożyczkami.
        38: {'zosia': ['mowi', ('slucha', {"sila": 1.3})]},  # Zosia patrzy podejrzliwie na Henryka | Zosia: „On też?”
        39: {'narrator': 'mowi'},  # narrator odpowiada | Narrator: „On mnie tu przyprowadził.”
        40: {'zosia': 'mowi'},  # Zosia szeptem | Zosia: „Ilu ich jest na górze?”
        41: {'henryk': ('patrzy', {"wraca": -0.6})},  # Henryk siada pod ścianą apteki i patrzy w drzwi | L: Pan Henryk usiadł pod ścianą i patrzył w d
    },
    2: {
        1: {'narrator': ('budzi', {"t": 0.4, "d": 1.4})},  # narrator budzi się na podłodze apteki, szare światło z okienka pod suf | L: Obudziłem się na podłodze apteki.
        2: {'henryk': ('patrzy', {"wraca": -0.5}), 'narrator': 'ciezar', 'zosia': 'ciezar'},  # apteka od środka: regały, krata, troje ludzi; Henryk pod ścianą, Zosia | L: Było nas troje.
        4: {'zosia': 'mowi'},  # Zosia liczy na palcach | Zosia: „Dwie butelki wody. Suchary. Leki.”
        5: {'henryk': ('patrzy', {"wraca": -0.6})},  # Henryk wyprostowany pod ścianą patrzy w drzwi | L: Pan Henryk nie spał, tylko patrzył w drzwi
        9: {'zosia': 'mowi'},  # Zosia | Zosia: „Dwadzieścia osiem dni. Wody mamy na d
        13: {'narrator': 'w_dol'},  # narrator patrzy na nich ze smutkiem | L: Wczoraj podawałem im kolację.
        14: {'henryk': 'kreci', 'narrator': 'ciezar'},  # Henryk kręci głową i wskazuje dalej korytarz | 
        16: {'narrator': ('patrzy', {"wraca": -0.5})},  # narrator pakuje czajnik, koc, baterie i dwie krótkofalówki do torby | L: Zabrałem czajnik, koc, baterie i dwie krót
        17: {'narrator': ('patrzy', {"wraca": -0.4})},  # narrator zdejmuje z wieszaka kurtkę i ją zakłada | 
        19: {'narrator': 'slucha', 'zosia': 'mowi'},  # w ciemnej aptece przy lampie akumulatorowej Zosi narrator zapisuje god | Zosia: „Zapisz. Osiemnasta dwanaście.”
        20: {'narrator': 'w_gore'},  # narrator patrzy w sufit | L: Wtedy nad nami coś się poruszyło.
    },
    3: {
        5: {'henryk': ('patrzy', {"wraca": -0.4}), 'narrator': 'ciezar', 'zosia': 'ciezar'},  # ściana z czterema zasadami, troje ludzi przed nią; z boku trzy kreski  | 
        6: {'zosia': 'mowi'},  # Zosia pyta | Zosia: „Skąd pan to wie?”
        7: {'henryk': 'odwraca'},  # Henryk odwraca wzrok i milczy | L: Nie odpowiedział.
        9: {'narrator': 'slucha', 'zosia': ['mowi', 'gest']},  # Zosia wskazuje na planie kuchnię | Zosia: „Kuchnia jest w zachodnim skrzydle.”
        10: {'narrator': 'mowi'},  # narrator | Narrator: „Za łącznikiem z oddziałem C.”
        11: {'zosia': 'mowi'},  # Zosia | Zosia: „W południe. Wtedy stoją najspokojniej
        13: {'narrator': 'wstrzymuje'},  # narrator wciąga powietrze i trzyma | L: Potem cztery sekundy trzymasz.
        14: {'narrator': 'wzdycha'},  # narrator wypuszcza powietrze | L: I cztery sekundy wydechu.
        20: {'narrator': 'cofa'},  # oczy narratora szeroko otwarte | 
        21: {'zosia': 'mowi'},  # Zosia szepcze | Zosia: „Dwanaście lat tu pracuję. Nigdy takie
        23: {'narrator': ('patrzy', {"wraca": -0.5})},  # narrator | L: Żadne z nas nie mrugnęło.
    },
    4: {
        8: {'narrator': ('patrzy', {"wraca": -0.4})},  # narrator ładuje konserwy do worka | 
        9: {'henryk': ('patrzy', {"wraca": -0.4})},  # Henryk napełnia kanistry z kranu: trzy po dwadzieścia litrów | woda charczy w rurach
        14: {'henryk': 'kreci'},  # Henryk kręci głową | L: Pan Henryk pokręcił głową.
        19: {'henryk': ('patrzy', {"wraca": -0.4})},  # Henryk idzie spokojnie | 
        21: {'narrator': ('wstrzymuje', {"t": 0.4})},  # trzech zarażonych mija ich w drodze do puszki, każdy w swoim tempie | L: Przeszli obok, bo szli do puszki, nie do n
        22: {'narrator': ('wstrzymuje', {"t": 0.1})},  # twarz narratora przy ścianie, zarażony przechodzi tuż przed nim | 
        26: {'zosia': 'mowi'},  # apteka: Zosia przelicza konserwy | Zosia: „Kupiliście nam tydzień.”
    },
    5: {
        4: {'narrator': 'mowi'},  # narrator szepcze przy drzwiach | Narrator: „To ja. Sanitariusz z C.”
        6: {'nowak': ('patrzy', {"wraca": -0.5})},  # kołnierz bluzy Nowaka zapięty pod szyję, długie rękawy; przy pasku pęk | L: Bluzę miał zapiętą pod szyję.
        7: {'nowak': 'slucha', 'zosia': 'mowi'},  # apteka: Zosia i Nowak | Zosia: „Jest pan ranny?”
        8: {'nowak': 'mowi'},  # Nowak | Nowak: „Nie.”
        9: {'nowak': ('patrzy', {"wraca": -0.4})},  # oczy Nowaka uciekają w bok, ku Henrykowi | 
        13: {'narrator': ('kiwa', {"ile": 1})},  # narrator rozumie | L: Dlatego tamtej nocy wszystkie drzwi stały 
        14: {'narrator': 'mowi'},  # narrator pyta | Narrator: „Czemu prąd zgasł akurat wtedy?”
        15: {'nowak': ['mowi', 'wzrusza']},  # Nowak wzrusza ramionami | Nowak: „Nie wiem.”
        16: {'nowak': 'mowi'},  # Nowak odsuwa połowę swojej porcji | Nowak: „Resztę dla Kuby.”
        17: {'zosia': ['mowi', ('slucha', {"sila": 1.3})]},  # Zosia marszczy brwi | Zosia: „Jakiego Kuby?”
        18: {'nowak': 'mowi'},  # Nowak | Nowak: „Na oddziale A ktoś jest. Chłopak i st
        20: {'zosia': 'mowi'},  # Zosia chwyta latarkę | Zosia: „Idziemy.”
        23: {'zosia': ['mowi', 'wzdycha']},  # Zosia ustępuje | Zosia: „Rano.”
        24: {'henryk': ('patrzy', {"wraca": -0.5}), 'narrator': 'slucha', 'nowak': 'slucha', 'zosia': 'slucha'},  # ciemna apteka: czworo ludzi | L: Pierwszy raz było nas czworo.
        25: {'henryk': ('patrzy', {"wraca": -0.6})},  # Henryk patrzy na rękawy Nowaka | 
    },
    6: {
        1: {'narrator': ('patrzy', {"wraca": -0.5})},  # narrator pod kratą, zgaszona latarka na kolanach | L: Tej nocy pełniłem wartę pod kratą.
        2: {'nowak': ('kolysze', {"sila": 1.4})},  # Nowak rzuca się przez sen, spocony | L: Doktor Nowak rzucał się przez sen.
        7: {'narrator': 'wstrzymuje'},  # narrator wstrzymuje oddech | 
        8: {'nowak': 'kolysze'},  # Nowak jęczy przez sen | jęk
        11: {'henryk': ('patrzy', {"wraca": -0.5}), 'nowak': 'ciezar'},  # Henryk wstaje bezgłośnie z rolką bandaża | L: Pan Henryk wstał bez jednego dźwięku.
        15: {'henryk': 'kiwa'},  # Henryk kiwa narratorowi głową | L: Wtedy pierwszy raz kiwnął mi głową.
        18: {'narrator': 'slucha', 'zosia': 'mowi'},  # Zosia odciąga narratora na bok | Zosia: „Nowak ma gorączkę.”
        19: {'narrator': 'mowi'},  # narrator zbywa | Narrator: „Wszyscy jesteśmy przeziębieni.”
        20: {'zosia': ('slucha', {"sila": 1.3})},  # Zosia patrzy, nie wierzy | L: Nie uwierzyła mi, zresztą ja sam sobie też
    },
    7: {
        2: {'nowak': 'oddycha'},  # Nowak opiera się o ścianę, ciężko oddycha | L: Po dwudziestu krokach musiał odpocząć.
        6: {'narrator': ('patrzy', {"wraca": -0.6})},  # narrator patrzy na przecięty kabel | L: Czyli ktoś otworzył tamte drzwi celowo.
        7: {'narrator': 'mowi'},  # narrator pyta | Narrator: „Kto ma klucze do rozdzielni?”
        8: {'nowak': 'mowi'},  # Nowak | Nowak: „Technik, ochrona i lekarz dyżurny.”
        10: {'nowak': 'mowi'},  # Nowak | Nowak: „Technik nie żyje. Ochroniarz uciekł.”
        11: {'zosia': ('patrzy', {"wraca": -0.6})},  # Zosia patrzy na Nowaka | 
        13: {'narrator': ('patrzy', {"wraca": -0.5}), 'nowak': 'ciezar', 'zosia': 'ciezar'},  # korytarz piwnicy w drodze powrotnej | L: W drodze powrotnej rury zaczęły stukać.
        15: {'nowak': 'slucha', 'zosia': 'mowi'},  # Zosia i Nowak zatrzymują się pod rurami | Zosia: „Słyszysz? To nie zarażeni.”
        18: {'narrator': 'wstrzymuje'},  # narrator czeka w ciszy | cisza
        21: {'narrator': ('patrzy', {"t": 0.3}), 'nowak': ('patrzy', {"t": 0.7}), 'zosia': ('patrzy', {"t": 0.5})},  # troje patrzy na Henryka | L: Wszyscy spojrzeliśmy na pana Henryka.
        22: {'henryk': 'kiwa'},  # Henryk kiwa głową | 
        23: {'zosia': ('patrzy', {"wraca": -0.5})},  # apteka wieczorem: Zosia pakuje latarki i bandaże | L: Zosia do nocy pakowała latarki i bandaże.
    },
    8: {
        4: {'kuba': ['mowi', 'kreci']},  # Kuba kręci głową na widok Henryka | Kuba: „On jest zarażony. Nie wpuszczę go.”
        5: {'narrator': 'mowi'},  # narrator przy szybie | Narrator: „On nas trzyma przy życiu.”
        7: {'irena': 'mowi', 'kuba': 'slucha'},  # Irena kładzie Kubie dłoń na ramieniu | Irena: „Kubuś, otwórz.”
        10: {'kuba': ('patrzy', {"wraca": -0.4})},  # Kuba unosi nogę od krzesła | 
        11: {'henryk': ('oddycha', {"tempo": 0.35, "sila": 1.3})},  # Henryk staje między nimi i oddycha głośno | głośny oddech
        12: {'henryk': ('patrzy', {"wraca": -0.5})},  # salowy skręca za Henrykiem w głąb korytarza | L: Salowy poszedł za nim jak pies za gwizdkie
        13: {'irena': ('patrzy', {"wraca": -0.4}), 'kuba': 'ciezar', 'zosia': 'ciezar'},  # reszta cofa się do łącznika | 
        17: {'henryk': ('patrzy', {"wraca": -0.5})},  # Henryk spokojny | L: Był spokojny, jakby robił to codziennie.
        18: {'henryk': ('patrzy', {"wraca": -0.5}), 'irena': 'slucha', 'kuba': 'slucha', 'narrator': 'slucha', 'nowak': 'slucha', 'zosia': 'slucha'},  # apteka, sześć osób | L: Wieczorem było nas sześcioro.
        19: {'irena': 'mowi', 'nowak': 'slucha'},  # Irena bierze Nowaka za rękę | Irena: „Ma pan gorączkę jak mój mąż przed śmi
        20: {'irena': ('patrzy', {"wraca": -0.4}), 'nowak': ('cofa', {"t": 0.2})},  # Nowak wyrywa rękę | 
        21: {'narrator': ('budzi', {"t": 0.1}), 'kuba': ['mowi', ('nachyla', {"t": 0.0})]},  # noc: Kuba budzi narratora | Kuba (szept): „Nowak wychodził sam.”
    },
    9: {
        1: {'narrator': 'mowi', 'nowak': 'slucha'},  # rano narrator pyta Nowaka | Narrator: „Dokąd pan chodził w nocy?”
        2: {'nowak': 'mowi'},  # Nowak | Nowak: „Do toalety.”
        3: {'zosia': ['mowi', 'gest']},  # Zosia wskazuje ścianę z zasadami | Zosia: „Zasada trzecia. Nigdy w pojedynkę.”
        4: {'kuba': 'mowi'},  # Kuba staje po stronie Nowaka | Kuba: „Zasady wymyślił wariat.”
        5: {'nowak': ('patrzy', {"wraca": -0.5})},  # Nowak milczy, chowa dłonie w rękawach | L: Nowak nic nie powiedział, tylko schował dł
        7: {'irena': ('rozglada', {"t": 0.4}), 'kuba': ('gest', {"t": 0.2}), 'narrator': ('ciezar', {"t": 0.5}), 'nowak': ('kreci', {"t": 0.6}), 'zosia': ('gest', {"t": 0.9, "reka": "l"})},  # kłótnia, wszyscy mówią naraz | L: Kłóciliśmy się za głośno.
        9: {'zosia': ('patrzy', {"wraca": -0.4})},  # Zosia gasi lampę | 
        14: {'narrator': 'wstrzymuje'},  # narrator w ciemności, nie oddycha | cisza
        17: {'zosia': ['mowi', 'gest']},  # Zosia pokazuje Kubie kartkę z liczbą dni | Zosia: „Wody mamy na półtora dnia.”
        18: {'kuba': 'cofa'},  # Kuba przerażony, nie zły | L: Pierwszy raz się bał, zamiast złościć.
        19: {'irena': 'mowi', 'kuba': 'slucha'},  # Irena obejmuje Kubę | Irena: „Nikt cię nie wini, Kubuś.”
        21: {'nowak': 'mowi'},  # Nowak | Nowak: „Nie ruszajmy prądu.”
        23: {'henryk': ('patrzy', {"wraca": -0.5}), 'irena': 'slucha', 'kuba': 'slucha', 'narrator': 'slucha', 'nowak': 'slucha', 'zosia': 'slucha'},  # ciemna apteka, wszyscy siedzą z otwartymi oczami | L: Tej nocy nikt nie spał.
    },
    10: {
        4: {'kuba': 'mowi'},  # Kuba się zgłasza | Kuba: „Ja pójdę.”
        5: {'narrator': 'mowi'},  # narrator | Narrator: „Idę z tobą.”
        6: {'zosia': 'mowi'},  # Zosia | Zosia: „Jeśli się odwrócą, wracacie. Bez pacz
        10: {'narrator': 'przelyka'},  # narrator, pot na skroni | L: Szliśmy powoli, krokiem pana Henryka.
        15: {'narrator': ('patrzy', {"wraca": -0.4})},  # narrator rzuca kurtkę na karetkę | 
        20: {'kuba': [('kolysze', {"sila": 0.7}), ('oddycha', {"tempo": 2.2, "sila": 0.8})]},  # Kuba oparty o drzwi śmieje się bez tchu | L: Kuba się śmiał, pierwszy raz, odkąd go zna
        23: {'narrator': 'w_gore'},  # narrator czyta, podnosi wzrok | L: Okno z sali 8 wychodziło prosto na bramę.
    },
    11: {
        1: {'zosia': ('patrzy', {"wraca": -0.5})},  # apteka: Zosia maluje na prześcieradle 6 ŻYWYCH · APTEKA · PIWNICA | L: Zosia napisała, ilu nas jest.
        6: {'narrator': ('patrzy', {"wraca": -0.5})},  # łazienka oddziału: narrator napełnia dwa kanistry z kranu | L: Po drodze nabrałem wody do dwóch kanistrów
        10: {'narrator': 'wzdycha'},  # narrator: ulga | L: Pierwszy raz od dziesięciu dni odetchnąłem
        11: {'henryk': ('slucha', {"sila": 1.6})},  # Henryk przekrzywia głowę, nasłuchuje | skrzyp drzwiczek szafy
        14: {'henryk': ('oddycha', {"tempo": 0.35, "sila": 1.3})},  # Henryk zasłania go i oddycha głośno, cofa się w głąb sali | głośny oddech
        15: {'narrator': ('oddycha', {"tempo": 1.8, "sila": 1.2})},  # narrator wypada na korytarz | 
        16: {'narrator': ('w_dol', {"t": 1.0})},  # narrator na korytarzu, za drzwiami cisza | L: Dopiero wtedy zrozumiałem, że pan Henryk z
        18: {'henryk': ('patrzy', {"wraca": -0.4})},  # Henryk wychodzi spokojny, zadrapanie na przedramieniu | 
        20: {'nowak': ['mowi', ('patrzy', {"wraca": -0.6})]},  # Nowak patrzy bardzo uważnie | Nowak: „Ile trwa przemiana po ugryzieniu?”
    },
    12: {
        3: {'zosia': 'mowi'},  # Zosia | Zosia: „Osiemnaście nocy bez prądu. Irena teg
        6: {'nowak': ['mowi', ('w_gore', {"t": 0.1, "d": 0.22, "sila": 1.4})]},  # Nowak gwałtownie podnosi głowę | Nowak: „Agregat może wywołać pożar.”
        7: {'zosia': ['mowi', ('patrzy', {"wraca": -0.6})]},  # Zosia patrzy na Nowaka | Zosia: „Czego pan się naprawdę boi?”
        8: {'nowak': ['mowi', 'w_dol']},  # Nowak spuszcza wzrok | Nowak: „Że zamki zamkną się też na nas.”
        10: {'kuba': 'mowi'},  # Kuba | Kuba: „Wywabimy ich. Jak z karetką.”
        12: {'kuba': ('patrzy', {"wraca": -0.4}), 'narrator': 'ciezar'},  # narrator i Kuba wkładają do worka metalowe tacki | brzęk tacek
        14: {'nowak': ('patrzy', {"wraca": -0.4})},  # Nowak nie je, ręce schowane w rękawach | 
        15: {'zosia': ('patrzy', {"t": 0.4})},  # noc: Zosia mierzy śpiącemu Nowakowi temperaturę | 
        17: {'zosia': 'mowi'},  # Zosia szepcze narratorowi | Zosia: „Nikomu ani słowa.”
        19: {'narrator': ('w_dol', {"t": 0.8})},  # narrator patrzy na śpiącego Nowaka | L: Klucz do rozdzielni nosił przecież lekarz 
    },
    13: {
        4: {'narrator': ('patrzy', {"wraca": -0.6})},  # narrator patrzy na odciski | L: Na szybie zostały setki odcisków ich dłoni
        6: {'narrator': 'mowi'},  # narrator liczy na palcach | Narrator: „Raz. Dwa. Trzy.”
        12: {'kuba': ('w_gore', {"t": 0.6}), 'narrator': ('w_gore', {"t": 0.9})},  # łącznik: za oknem, za płotem żołnierz pokazuje na niebo | L: Żołnierz za płotem pokazał na niebo, bo za
        13: {'nowak': 'mowi'},  # apteka: Nowak przy kracie, ubrany do drogi | Nowak: „Idę z wami. Tylko ja wiem, jak go uru
        14: {'zosia': ['kreci', ('wzdycha', {"t": -1.3})]},  # Zosia kręci głową, potem ustępuje | L: Zosia nie chciała go puścić, ale miał racj
        15: {'henryk': ('patrzy', {"wraca": -0.4}), 'kuba': 'ciezar', 'narrator': 'ciezar', 'nowak': 'ciezar'},  # Henryk wstaje i staje przy nich | 
        18: {'nowak': 'mowi'},  # Nowak sprawdza poziom paliwa | Nowak: „Starczy na kilkanaście dni. Na pół mo
        20: {'nowak': ('slucha', {"sila": 1.3})},  # Nowak waha się o sekundę za długo | cisza
    },
    14: {
        7: {'nowak': 'mowi'},  # Nowak krzyczy przez ryk | Nowak: „To dym z wydechu! Czujniki!”
        12: {'henryk': ('patrzy', {"wraca": -0.4}), 'narrator': 'ciezar', 'nowak': 'ciezar'},  # Henryk wciąga ich za drzwi | 
        19: {'irena': ('wzdycha', {"t": 0.6}), 'kuba': ('w_dol', {"t": 0.3}), 'zosia': ('patrzy', {"t": 0.8})},  # piwnica: wszyscy żyją, Kuba trzyma rozciętą dłoń | L: Wszyscy żyli, tylko Kuba rozciął dłoń o sz
    },
    15: {
        4: {'irena': ('oddycha', {"tempo": 0.25, "sila": 0.6})},  # Irena oddycha spokojnie | L: Włączyło się ogrzewanie, więc pani Irena p
        6: {'irena': ('patrzy', {"wraca": -0.5}), 'kuba': 'ciezar', 'zosia': 'ciezar'},  # pokój socjalny na parterze: kuchenka, kanapy, grupa wnosi rzeczy | L: Przenieśliśmy się do pokoju socjalnego.
        9: {'narrator': 'mowi', 'zosia': 'slucha'},  # narrator i Zosia na osobności przy kuchence | Narrator: „Ufasz mu?”
        10: {'zosia': 'mowi'},  # Zosia | Zosia: „Ma gorączkę od dziesięciu dni. Nie da
        12: {'zosia': 'mowi'},  # Zosia długo milczy | Zosia: „Mogła wypaść każdemu.”
        13: {'narrator': 'mowi'},  # narrator | Narrator: „On nie szedł przez portiernię.”
        16: {'nowak': ('rozglada', {"t": 0.3})},  # ciemność: Nowak wstaje, ostrożne kroki | skrzyp podłogi
        20: {'narrator': ('cofa', {"t": 0.4})},  # narrator cofa się — za nim w ciemności stoi Henryk | 
        21: {'henryk': ('patrzy', {"wraca": -0.5})},  # Henryk | L: Pan Henryk widział to samo.
    },
    16: {
        1: {'irena': ('patrzy', {"t": 0.5}), 'kuba': ('patrzy', {"t": 0.3}), 'nowak': ('w_dol', {"t": 1.0}), 'zosia': ('patrzy', {"t": 0.7})},  # pokój socjalny: narrator kładzie przepustkę na stole, wszyscy patrzą | L: Rano położyłem przepustkę na stole.
        2: {'nowak': ('w_dol', {"t": 0.8})},  # Nowak patrzy na przepustkę i wie | 
        9: {'irena': ['mowi', 'kolysze']},  # Irena płacze | Irena: „Ilu ludzi zginęło, bo pan chciał żyć?
        11: {'narrator': 'mowi'},  # narrator | Narrator: „Ile ma pan czasu?”
        13: {'kuba': ['gest', 'ciezar'], 'zosia': ('gest', {"t": 0.8, "reka": "l"})},  # Kuba wskazuje drzwi na podwórze, Zosia drzwi gabinetu | L: Kuba chciał go wyrzucić, a Zosia zamknąć.
        14: {'henryk': ('patrzy', {"wraca": -0.4})},  # Henryk wstaje i bierze Nowaka za rękę | 
        16: {'henryk': ('patrzy', {"wraca": -0.4})},  # izolatka 3: Henryk otwiera drzwi kluczem | zgrzyt klucza
        17: {'nowak': ('patrzy', {"wraca": -0.4})},  # Nowak wchodzi sam i siada na łóżku | 
        19: {'narrator': 'mowi'},  # narrator | Narrator: „Będzie pan tu siedział do końca?”
    },
    17: {
        1: {'narrator': ('w_dol', {"t": 1.2, "d": 1.2})},  # narrator i Henryk siedzą pod okienkiem izolatki | L: Cały dzień siedziałem z panem Henrykiem po
        4: {'narrator': 'mowi'},  # narrator | Narrator: „Powiem.”
        11: {'narrator': ('kiwa', {"ile": 1})},  # narrator: zrozumienie | L: Wtedy zrozumiałem, że pan Henryk nie zmien
        12: {'henryk': ('patrzy', {"wraca": -0.5})},  # Henryk | L: Uderzał w szybę, żeby mnie ostrzec.
        13: {'henryk': ('slucha', {"sila": 0.8})},  # Henryk uśmiecha się kącikami ust | 
        15: {'henryk': ('oddycha', {"tempo": 0.3})},  # Henryk pod okienkiem oddycha w jego rytmie | 
        16: {'narrator': 'mowi'},  # narrator | Narrator: „Czemu pan prawie nie mruga?”
        19: {'henryk': ('w_dol', {"d": 2.2})},  # Henryk zamyka oczy i zasypia na siedząco | L: Pan Henryk zasnął pierwszy raz od siedemna
    },
    18: {
        9: {'narrator': 'mowi'},  # narrator | Narrator: „Przepraszam.”
        10: {'henryk': ['mowi', 'kreci']},  # Henryk kręci głową | Henryk: „Wszyscy tak myśleli.”
        11: {'irena': 'mowi'},  # Irena | Irena: „Jak pan przeżył pierwszą noc?”
        13: {'henryk': ('oddycha', {"tempo": 0.22}), 'irena': ('oddycha', {"tempo": 0.22, "sila": 0.8}), 'kuba': ('oddycha', {"tempo": 0.24, "sila": 1.1}), 'narrator': ('oddycha', {"tempo": 0.21}), 'zosia': ('oddycha', {"tempo": 0.23, "sila": 0.9})},  # wszyscy z dłońmi na brzuchu uczą się oddychać przeponą | L: Uczył nas oddychać przeponą.
        14: {'kuba': ('kolysze', {"sila": 0.7})},  # Kuba najpierw się śmieje, potem oddycha cicho | 
        15: {'henryk': ('patrzy', {"wraca": -0.5})},  # świetlica wieczorem: Henryk siada przy pianinie, nie dotyka klawiszy | L: Wieczorem usiadł przy pianinie, ale nie za
        16: {'henryk': 'mowi'},  # Henryk | Henryk: „Zagram, kiedy trzeba będzie was zawo
    },
    19: {
        2: {'zosia': ('patrzy', {"wraca": -0.5})},  # sala 8: Zosia wywiesza nowe prześcieradło: 5 ŻYWYCH · PARTER | L: Wojsko nie zrzuciło nic więcej.
        3: {'kuba': 'mowi'},  # Kuba | Kuba: „Spisali nas na straty.”
        4: {'zosia': 'mowi'},  # Zosia | Zosia: „W chłodni jest jedzenie na miesiąc.”
        5: {'henryk': ('patrzy', {"wraca": -0.5}), 'narrator': 'ciezar'},  # kuchnia: narrator i Henryk wchodzą | L: Do kuchni poszliśmy we dwóch.
        7: {'henryk': ['mowi', ('patrzy', {"wraca": -0.6})]},  # Henryk patrzy długo | Henryk: „To Basia. Zawsze dawała mi dokładkę.
        8: {'narrator': ('patrzy', {"wraca": -0.4})},  # narrator otwiera drzwi chłodni | 
        10: {'henryk': ('oddycha', {"tempo": 0.35, "sila": 1.3})},  # Henryk oddycha głośno, Basia idzie za nim do magazynu | głośny oddech
        11: {'narrator': ('patrzy', {"wraca": -0.4})},  # narrator ładuje wózek jedzeniem z chłodni | 
        15: {'henryk': ('patrzy', {"wraca": -0.4})},  # Henryk zamyka magazyn, Basia nie stawia oporu | 
        16: {'irena': ('patrzy', {"wraca": -0.5})},  # Irena gotuje, para nad garnkiem | L: Zjedliśmy pierwszy ciepły posiłek od dwóch
        19: {'kuba': ('patrzy', {"wraca": -0.4}), 'zosia': 'slucha'},  # Zosia kładzie mu dłoń na ramieniu | 
    },
    20: {
        7: {'narrator': ('kiwa', {"ile": 1})},  # narrator: zrozumienie | L: To nie skończyło się na szpitalu.
        10: {'zosia': 'mowi'},  # Zosia przy słuchawce | Zosia: „A ludzie w zamkniętych salach?”
        11: {'zosia': ('cofa', {"t": 0.6})},  # Zosia słucha, blednie | Malec: „Budynek zostanie spalony.”
        14: {'zosia': 'mowi'},  # Zosia | Zosia: „Do trzydziestego się zagoi.”
        15: {'irena': 'mowi'},  # Irena spokojnie | Irena: „Ja nie przejdę. Mam gorączkę od tygod
        16: {'henryk': 'mowi', 'irena': 'slucha'},  # Henryk bierze ją za rękę | Henryk: „Jeszcze dziesięć dni. Spadnie.”
        17: {'narrator': ('patrzy', {"wraca": -0.5})},  # sala 8: narrator przy oknie, w oddali płonie miasto | L: W oddali paliło się miasto.
        18: {'narrator': ('patrzy', {"wraca": -0.5})},  # narrator | L: Myślałem o córce Nowaka.
    },
    21: {
        14: {'zosia': 'mowi'},  # Zosia | Zosia: „Obok czterdziestu trzech nikt nie prz
        15: {'henryk': ('patrzy', {"wraca": -0.4})},  # świetlica: Henryk przy pianinie dotyka klawiszy, nie naciskając | 
        16: {'narrator': 'mowi'},  # narrator | Narrator: „Pianino jest dość głośne, żeby ich
        17: {'henryk': 'mowi'},  # Henryk | Henryk: „Pianino nie. Alarm tak.”
        19: {'henryk': 'mowi'},  # Henryk | Henryk: „Można je połączyć. Alarm włącza każd
    },
    22: {
        2: {'zosia': 'mowi'},  # Zosia liczy butelki i kanistry na stole | Zosia: „Wody na siedem dni. Do trzydziestego 
        3: {'narrator': 'mowi'},  # narrator | Narrator: „Na dachu jest zbiornik na deszczów
        4: {'henryk': ('w_dol', {"sila": 0.6})},  # Henryk zostaje przy Irenie, kładzie dłoń na jej czole | L: Pani Irenie znów rosła gorączka.
        6: {'kuba': ('patrzy', {"wraca": -0.4})},  # Kuba na drabinie otwiera klapę na dach; wpada światło | 
        8: {'narrator': ('patrzy', {"wraca": -0.4})},  # zbiornik w połowie pełny; narrator zanurza kanister w zimnej wodzie | chlupot
        9: {'kuba': ['mowi', ('patrzy', {"wraca": -0.6})]},  # Kuba patrzy na miasto | Kuba: „Będzie dokąd iść, jak wyjdziemy?”
        10: {'narrator': 'mowi'},  # narrator | Narrator: „Najpierw trzeba wyjść.”
        16: {'zosia': ('patrzy', {"wraca": -0.4})},  # Zosia gotuje wodę na kuchence | 
        18: {'henryk': ('w_dol', {"sila": 0.5})},  # Henryk trzyma mokry ręcznik na czole śpiącej Ireny | 
        19: {'zosia': 'mowi'},  # noc: Zosia siada przy narratorze i chowa dłoń | Zosia: „W dniu czternastym skaleczyłam się o 
    },
    23: {
        8: {'narrator': 'slucha'},  # Henryk zatrzymuje narratora dłonią na piersi; oddychają razem | wspólny wolny oddech
        12: {'narrator': 'wstrzymuje'},  # narrator zamiera, oddycha bardzo wolno | L: Liczyłem do stu.
    },
    24: {
        2: {'kuba': ('patrzy', {"wraca": -0.4})},  # Kuba barykaduje drzwi kanapą i lodówką | szuranie mebli
        3: {'henryk': ('oddycha', {"tempo": 0.2})},  # Henryk siedzi przy drzwiach i oddycha wolno; w szparze pod drzwiami ci | 
        9: {'narrator': ['mowi', 'kreci']},  # narrator kręci głową | Narrator: „Nie.”
        12: {'henryk': ('w_dol', {"sila": 0.6})},  # Henryk w nocy zmienia Zosi okład; nie zamyka oczu | 
        13: {'zosia': ('patrzy', {"wraca": -0.5})},  # oczy Zosi: mruga często, nerwowo | L: Patrzyłem, czy mruga, i na szczęście mruga
        17: {'zosia': ['mowi', 'budzi']},  # Zosia otwiera oczy | Zosia: „Ktoś dopisał kreskę?”
    },
    25: {
        10: {'henryk': 'mowi'},  # Henryk chwyta Kubę za ramiona | Henryk: „Patrz na mnie. Cztery wdech. Cztery 
        11: {'kuba': ('oddycha', {"tempo": 0.28})},  # oddech Kuby zwalnia razem z oddechem Henryka | wspólny oddech
        13: {'kuba': ['mowi', 'kolysze']},  # Kuba płacze bezgłośnie | Kuba: „Nikt mnie nigdy tak nie uczył.”
        14: {'henryk': 'mowi'},  # Henryk | Henryk: „Mnie też nie. Dopóki nie straciłem g
        15: {'kuba': 'mowi'},  # Kuba przy pianinie | Kuba: „Nauczy mnie pan jednej melodii?”
        18: {'henryk': 'mowi'},  # Henryk | Henryk: „Kołysanka mojej żony.”
    },
    26: {
        1: {'irena': 'mowi', 'kuba': 'slucha', 'zosia': 'slucha'},  # rano przy stole Irena mówi do wszystkich, spokojnie | Irena: „Osiemdziesiąt jeden lat. Chore płuca.
        2: {'zosia': 'mowi'},  # Zosia | Zosia: „Zapalenie płuc to nie zarażenie. Leka
        3: {'irena': 'mowi'},  # Irena | Irena: „Żołnierze nie są lekarzami.”
        4: {'narrator': 'mowi'},  # narrator | Narrator: „Coś wymyślimy.”
        5: {'irena': ('slucha', {"sila": 0.8})},  # Irena uśmiecha się smutno i klepie go po dłoni | 
        13: {'zosia': ('patrzy', {"wraca": -0.4})},  # skrzydło techniczne: Zosia stuka w beczki z paliwem; tylko jedna jest  | głuche stuknięcia
        14: {'zosia': 'mowi'},  # Zosia | Zosia: „Paliwa na cztery dni. Potem zgaśnie ś
        16: {'henryk': 'mowi'},  # Henryk | Henryk: „To dobrze. Nie ma nad czym myśleć.”
        17: {'henryk': ('patrzy', {"wraca": -0.4})},  # noc: w świetlicy Henryk stroi pianino, struna po strunie | pojedyncze ciche dźwięki
    },
    27: {
        5: {'zosia': 'mowi'},  # Zosia | Zosia: „Alarm sam milknie po minucie.”
        7: {'narrator': 'mowi'},  # narrator | Narrator: „Ja. To ja wyrwałem przewody.”
        8: {'henryk': ['mowi', 'kreci']},  # Henryk kręci głową | Henryk: „Ty masz obietnicę. Dla córki doktora
        9: {'zosia': 'mowi'},  # Zosia | Zosia: „Pan też może wyjść. Nie ma pan gorącz
        12: {'zosia': ('patrzy', {"wraca": -0.4})},  # Zosia otwiera usta i zamyka je bez słowa | 
        13: {'kuba': 'mowi'},  # Kuba | Kuba: „Alarm można podpiąć pod klawisz pianin
        14: {'henryk': ['mowi', ('slucha', {"sila": 0.8})]},  # Henryk się uśmiecha | Henryk: „To zawołam ich muzyką.”
        15: {'kuba': ('patrzy', {"wraca": -0.4}), 'narrator': 'ciezar'},  # portiernia: Kuba i narrator łączą przewody centrali alarmu | 
    },
    28: {
        1: {'irena': ('patrzy', {"wraca": -0.4})},  # rano: Irena odgrzewa na kuchence wszystko, co zostało w lodówce | 
        4: {'zosia': 'mowi'},  # Zosia przy telefonie | Zosia: „Do bramy wyjdzie czworo.”
        5: {'zosia': 'mowi'},  # Zosia słucha, potem spokojnie | Zosia: „Piąta osoba zostaje z wyboru.”
        9: {'narrator': ('patrzy', {"wraca": -0.6})},  # narrator patrzy na Henryka | L: Znał ich wszystkich, bo latami patrzył na 
        12: {'irena': ('slucha', {"t": 0.4}), 'kuba': ('kolysze', {"sila": 0.6}), 'narrator': ('slucha', {"t": 0.8}), 'zosia': ('slucha', {"t": 0.2})},  # wieczór: wszyscy przy pianinie; Henryk gra bez dźwięku, Kuba nuci | nucenie
        13: {'irena': ['mowi', 'kolysze']},  # Irena płacze | Irena: „Mój mąż tak nucił, kiedy nie mógł zas
        14: {'henryk': ('wstrzymuje', {"t": 0.3, "wolno": 1.0})},  # Zosia przytula Henryka; on sztywnieje | 
    },
    29: {
        3: {'zosia': 'mowi'},  # Zosia | Zosia: „Nie doczekamy szóstej. Zamki puszczą 
        4: {'zosia': 'slucha'},  # Zosia ze słuchawką | Malec: „Ciężarówka będzie o czwartej.”
        8: {'irena': ('patrzy', {"wraca": -0.4})},  # Irena robi kanapki na drogę; nikt ich nie rusza | 
        9: {'henryk': ('patrzy', {"wraca": -0.5})},  # Henryk w czystej koszuli siedzi w świetlicy | L: Zosia znalazła mu w magazynie czystą koszu
        10: {'narrator': ('przelyka', {"t": 0.6})},  # narrator otwiera usta i nic nie mówi | 
        11: {'henryk': 'mowi'},  # Henryk | Henryk: „Oddychaj.”
        12: {'henryk': ('oddycha', {"tempo": 0.22}), 'narrator': ('oddycha', {"tempo": 0.22})},  # oddychają razem ostatni raz, w tym samym rytmie | wspólny oddech
        13: {'henryk': 'mowi'},  # Henryk | Henryk: „Nie oglądaj się, jak będziesz szedł 
        14: {'narrator': 'mowi'},  # narrator | Narrator: „Obiecuję.”
        15: {'narrator': ('rozglada', {"t": 0.3}), 'zosia': ('rozglada', {"t": 0.8})},  # 3:40: grupa przy bocznych drzwiach; Kuba trzyma Irenę pod ramię, Zosia | 
    },
    30: {
        1: {'henryk': ('patrzy', {"wraca": -0.4})},  # świetlica: Henryk uderza pierwszy akord; razem z nim wyje alarm pożaro | akord i alarm
        9: {'zosia': ('patrzy', {"wraca": -0.4})},  # brama: żołnierze mierzą temperaturę i oglądają ręce w świetle latarek | 
        10: {'zosia': ('patrzy', {"wraca": -0.6})},  # lekarz wojskowy patrzy na ranę Zosi i macha: przechodź | Lekarz: „Trzydzieści siedem i osiem. Przechod
    },
}
