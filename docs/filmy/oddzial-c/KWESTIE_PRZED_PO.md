# Oddział C · wariant A — kwestie dni 1–30 przed i po (6.11.2026)

Uwaga reżysera: *„za dużo bardzo krótkich zdań, często brzmią jak bez okoliczników”*. Zasada: podręcznik „Rytm” 4a,
MASTER_BIBLE.md 2.4a. Historia się nie zmienia — zmienia się tylko to, jak lektor i postacie ją mówią.

Jak czytać: **Przed** → **Po**. „cisza” znaczy, że lektor tylko nazywał to, co widać — ujęcie zostaje bez słów
(albo z samym efektem). Finał d30_19 i zimne otwarcie bez zmian. Zmienionych kwestii: 210.

Pełne zdanie nie musi być dłuższe: tam, gdzie dzień miał zapas czasu (dni 11–30), zdania dostały okoliczność;
w ciasnych dniach 1–10 urywki zlały się w jedno zdanie, a kwestie powtarzające obraz zamieniły się w ciszę. Każdy dzień
mieści się w 55–80 s. Dni 2 i 5 nadal lekko ściskają ujęcia bez słów (o 3 i 2 s, przed zmianą o 5 i 2,5 s). Film jest
dłuższy o ok. 2 min 20 s.

| | lektor: słów w zdaniu | lektor: zdań do 3 słów | dialog: słów w zdaniu | dialog: zdań do 3 słów | posiekane kwestie | film |
|---|---|---|---|---|---|---|
| zimne otwarcie (wzorzec) | 5,1 | 27 % | — | — | 1 | — |
| dni 1–30 przed | 4,2 | 39 % | 3,5 | 55 % | 131 | 36:24 |
| dni 1–30 po | 6,9 | 4 % | 5,9 | 16 % | 2 | 38:42 |

## Co dalej w Studio (projekt `prj_f2503a77f5fa44bc`, Studio uruchomione)

Zmiana jest w rozpisce i w kopiach księgi w repozytorium; Studio jeszcze jej nie ma. Kontrola bez Studio
(`ujecia/kontrola.py`): **0 / 1 / 2** (waga 3 / 2 / 1; przed zmianą 0 / 1 / 3) — jedyna uwaga wagi 2 to długość dnia 1
(akt z zimnym otwarciem, była już wcześniej).

```bash
python3 docs/filmy/oddzial-c/ujecia/laduj_swiat.py wczytaj prj_f2503a77f5fa44bc      # notatki zasobów + warsztat
for d in $(seq 1 30); do python3 docs/filmy/oddzial-c/ujecia/zamien_dzien.py $d prj_f2503a77f5fa44bc tylko_plan; done
```

Po `tylko_plan` nowe kwestie widać w planie każdego dnia (oś bez zmian) — można je ocenić przed rysowaniem. Gdy reżyser
zatwierdzi brzmienie: dla każdego dnia `zamien_dzien.py <dzień> <projekt>` i `output/zombie-psychiatryk/studio_dzien.py
<dzień> <projekt>` (nowe czasy ujęć i okna napisów; rysunki się nie zmieniły). Skrypty same dopisują wpisy do dziennika.
Recenzje dni zostaną unieważnione (zmienił się podpis treści) — to zamierzone.

## Dzień 1 · Telefon — 126.5 s → 133.5 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d01_04 | twarz narratora ze słuchawką, oczy na szybie | Zosia (szept): „Tu Zosia. Apteka w piwnicy.” | Zosia (szept): „Tu Zosia, z apteki w piwnicy.” |
| d01_06 | usta narratora przy słuchawce, wstrzymany oddech | Zosia: „Idą na dźwięk. Światło ich nie obchodzi.” | Zosia: „Idą na dźwięk, a światło ich nie obchodzi.” |
| d01_08 | dłoń kładzie słuchawkę na blacie przed aparatem | L: Położyłem ją na biurku. Niech gra. | L: Położyłem ją na biurku, niech gra. |
| d01_09 | przez szybę: głowy pacjentów jedna po drugiej, z opóźnieniami, kierują | L: I wtedy się odwrócili. Do telefonu, nie do mnie. | L: I wtedy odwrócili się do telefonu, nie do mnie. |
| d01_12 | klucz w bocznych drzwiach obraca się milimetr po milimetrze, dłoń zasł | L: Zamek otwierałem trzy sekundy. | L: Zamek otwierałem przez trzy długie sekundy. |
| d01_13 | boczne drzwi dyżurki uchylają się; narrator wysuwa się plecami do ścia | L: Wyszedłem bokiem. | — *cisza* — |
| d01_20 | koniec korytarza: wszystkie drzwi otwarte poza jednymi — izolatka 3 | L: Zamknięte były tylko jedne drzwi. | L: Zamknięte zostały tylko jedne drzwi, izolatki trzy. |
| d01_21 | okienko izolatki z siatką: pan Henryk patrzy bez mrugnięcia, przycięty | L: Izolatka trzy. | — *cisza* — |
| d01_22 | para z oddechu Henryka na szybie pojawia się i znika | L: Pan Henryk oddychał. Raz na bardzo długo. | L: Pan Henryk oddychał raz na bardzo długo. |
| d01_23 | oczy Henryka w okienku patrzą prosto na narratora | L: Patrzył na mnie. Nie mrugał. | L: Patrzył na mnie i nie mrugał. |
| d01_24 | dłoń Henryka w okienku pokazuje: wdech, trzymanie, wolny wydech | L: Pokazał mi dłonią: wdech, czekaj, wydech. | L: Dłonią pokazał mi, jak oddychać, żeby nie usłyszeli. |
| d01_25 | narrator powtarza; jego oddech zwalnia | L: Zrobiłem to samo. | L: Zrobiłem to samo i serce zwolniło. |
| d01_26 | klucz z pęku w zamku izolatki, dłoń przed dziurką | L: Otworzyłem izolatkę. | — *cisza* — |
| d01_27 | Henryk wychodzi przez drzwi izolatki i bierze narratora za rękaw | L: Wziął mnie za rękaw. | — *cisza* — |
| d01_28 | Henryk prowadzi narratora środkiem grupy pacjentów, obaj oddychają tym | L: I poprowadził mnie środkiem. | L: Wziął mnie za rękaw i poprowadził środkiem. |
| d01_32 | pacjent odwraca się i wraca w stronę dyżurki | L: Odwrócił się z powrotem. | L: Po chwili odwrócił się z powrotem. |
| d01_36 | Zosia za kratą z nożyczkami, opuszcza je, gdy ich poznaje | L: I stała Zosia. Z nożyczkami. | L: Stała tam Zosia i ściskała nożyczki. |
| d01_39 | Zosia patrzy podejrzliwie na Henryka | Zosia: „On też?” | Zosia: „On też jest chory?” |

## Dzień 2 · Kordon — 80.0 s → 79.7 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d02_04 | kartka Zosi: 2 butelki wody, suchary, leki | L: Zosia liczyła, co mamy. | — *cisza* — |
| d02_05 | Zosia liczy na palcach | Zosia: „Dwie butelki wody. Suchary. Leki.” | Zosia: „Mamy dwie butelki wody, suchary i leki.” |
| d02_06 | Henryk wyprostowany pod ścianą patrzy w drzwi | L: Pan Henryk nie spał. Patrzył w drzwi. | L: Pan Henryk pilnował drzwi, jakby miał dyżur. |
| d02_08 | żołnierze w maskach rozwijają zasieki przy bramie | Megafon: „Kwarantanna. Minimum dwadzieścia osiem dni.” | Megafon: „Kwarantanna na minimum dwadzieścia osiem dni.” |
| d02_10 | Zosia | Zosia: „Dwadzieścia osiem dni. Wody mamy na dwa.” | Zosia: „Dwadzieścia osiem dni, a wody mamy na dwa.” |
| d02_12 | przez otwarte drzwi sali: zarażeni twarzami do ściany, każdy kołysze s | L: Stali w salach twarzami do ścian. | — *cisza* — |
| d02_16 | słuchawka wciąż leży na biurku dyżurki, w dzień | L: Słuchawka wciąż leżała na biurku. | cichy pisk słuchawki |
| d02_17 | narrator pakuje czajnik, koc, baterie i dwie krótkofalówki do torby | L: Zabrałem czajnik, koc, baterie. I dwie krótkofalówki. | L: Zabrałem czajnik, koc, baterie i dwie krótkofalówki. |
| d02_20 | w ciemnej aptece przy lampie akumulatorowej Zosi narrator zapisuje god | Zosia: „Zapisz. Osiemnasta dwanaście.” | Zosia: „Zapisz godzinę: osiemnasta dwanaście.” |
| d02_21 | narrator patrzy w sufit | L: Nad nami coś się poruszyło. | — *cisza* — |

## Dzień 3 · Zasady — 79.0 s → 78.8 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d03_03 | pod spodem: ODDECH | L: Potem drugie. | — *cisza* — |
| d03_04 | narrator dopisuje: PARAMI | L: Ja dopisałem trzecie. | — *cisza* — |
| d03_05 | krzywym pismem Henryk dopisuje: NIE OTWIERAJ PO ZMROKU | L: Czwarte napisał pan Henryk. | L: Czwarte słowo napisał pan Henryk. |
| d03_08 | Henryk odwraca wzrok i milczy | L: Nie odpowiedział. | — *cisza* — |
| d03_09 | kartka zapasów: woda 2 dni, jedzenie 3 dni | L: Wody na jeden dzień. Jedzenia na trzy. | L: Wody zostało na jeden dzień, jedzenia na trzy. |
| d03_11 | narrator | Narrator: „Za łącznikiem z oddziałem C.” | Narrator: „Trzeba iść łącznikiem za oddziałem C.” |
| d03_12 | Zosia | Zosia: „W południe. Wtedy stoją najspokojniej.” | Zosia: „W południe, bo wtedy stoją najspokojniej.” |
| d03_13 | Henryk z dłonią na piersi uczy oddechu | L: Pan Henryk uczył nas oddychać. Cztery sekundy wdech. | L: Pan Henryk uczył nas oddychać na cztery. |
| d03_14 | narrator wciąga powietrze i trzyma | L: Cztery trzymasz. | — *cisza* — |
| d03_15 | narrator wypuszcza powietrze | L: Cztery wydech. | — *cisza* — |
| d03_16 | dłoń narratora przestaje drżeć | L: Ręce przestały mi drżeć. | — *cisza* — |
| d03_17 | ręczniki owinięte wokół prętów kraty | L: Owinęliśmy kratę ręcznikami. | L: Kratę owinęliśmy ręcznikami, żeby nie dzwoniła. |
| d03_22 | Zosia szepcze | Zosia: „Dwanaście lat tu pracuję. Nigdy takiej ciszy.” | Zosia: „Dwanaście lat tu pracuję, a takiej ciszy nie znam.” |
| d03_25 | ciemna klatka schodowa; z góry słaby dzwonek drugiego telefonu, w poko | L: A nad ranem zadzwonił drugi telefon. Ten w pokoju lekarskim. | L: A nad ranem zadzwonił drugi telefon, w pokoju lekarskim. |

## Dzień 4 · Kuchnia — 77.3 s → 77.2 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d04_03 | ostatni z nich znika w drzwiach pokoju lekarskiego | L: To wystarczyło. | L: Dwa dzwonki wystarczyły, żeby korytarz opustoszał. |
| d04_07 | żołnierz w masce unosi rękę | L: Żołnierz nas widział. Nic nie zrobił. | L: Żołnierz nas widział, ale nic nie zrobił. |
| d04_13 | okienko chłodni: oszroniona kucharka wodzi głową za latarką, przycięta | L: W chłodni była kucharka. Zamknęła się tam tamtej nocy. | L: W chłodni była kucharka, która zamknęła się tam tamtej nocy. |
| d04_15 | Henryk kręci głową | L: Pan Henryk pokręcił głową. | — *cisza* — |
| d04_19 | narrator biegnie z workiem | L: Zacząłem biec. | — *cisza* — |
| d04_22 | trzech zarażonych mija ich w drodze do puszki, każdy w swoim tempie | L: Przeszli obok. Do puszki, nie do nas. | L: Przeszli obok, do puszki, nie do nas. |
| d04_29 | narrator podnosi głowę | L: Wieczorem z góry ktoś zakaszlał. Jak żywy człowiek. | L: Wieczorem z góry ktoś zakaszlał, jak żywy człowiek. |

## Dzień 5 · Dr Nowak — 79.5 s → 79.5 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d05_05 | narrator szepcze przy drzwiach | Narrator: „To ja. Sanitariusz z C.” | Narrator: „To ja, sanitariusz z C.” |
| d05_06 | drzwi się uchylają: dr Nowak, blady, spocony | L: To był doktor Nowak. Lekarz dyżurny. | L: To był doktor Nowak, lekarz dyżurny. |
| d05_13 | długopis wskazuje rozdzielnię | Nowak: „Zamki są elektromagnetyczne. Bez prądu puszczają.” | Nowak: „Zamki są elektromagnetyczne, bez prądu puszczają.” |
| d05_19 | Nowak | Nowak: „Na oddziale A ktoś jest. Chłopak i starsza kobieta.” | Nowak: „Na oddziale A jest chłopak i starsza kobieta.” |
| d05_24 | Zosia ustępuje | Zosia: „Rano.” | Zosia: „Pójdziemy rano.” |
| d05_27 | Nowak chowa dłonie w rękawach | L: Doktor Nowak schował dłonie w rękawach. | — *cisza* — |

## Dzień 6 · Noc patrolu — 75.8 s → 79.5 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d06_07 | identyfikator na jej fartuchu | L: Znałem ją. Ewa z nocnej zmiany. | L: To była Ewa z nocnej zmiany. |
| d06_11 | dłoń narratora na ustach Nowaka | L: Zasłoniłem mu usta. Czoło miał gorące. | L: Zasłoniłem mu usta, a czoło miał gorące. |
| d06_15 | pielęgniarka odwraca się i wspina za dźwiękiem | L: Poszła za dźwiękiem. W górę. | L: Poszła za dźwiękiem w górę. |
| d06_19 | Zosia odciąga narratora na bok | Zosia: „Nowak ma gorączkę.” | Zosia: „Doktor Nowak ma gorączkę od wczoraj.” |
| d06_20 | narrator zbywa | Narrator: „Wszyscy jesteśmy przeziębieni.” | Narrator: „W tej piwnicy wszyscy jesteśmy przeziębieni.” |
| d06_21 | Zosia patrzy, nie wierzy | L: Nie uwierzyła mi. Ja sam sobie też nie. | L: Nie uwierzyła mi, a ja sam sobie też nie. |

## Dzień 7 · Przecięty przewód — 75.0 s → 78.2 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d07_05 | gruby kabel zamków oddziału C przecięty równo | L: Kabel zamków oddziału C ktoś przeciął. Równo. | L: Ktoś równo przeciął kabel zamków oddziału C. |
| d07_06 | nożyce do metalu z oznaczeniem warsztatu | L: Nożyce leżały obok. Z warsztatu. | L: Obok leżały nożyce z warsztatu. |
| d07_07 | narrator patrzy na przecięty kabel | L: Ktoś otworzył tamte drzwi. Celowo. | L: Ktoś celowo otworzył tamte drzwi. |
| d07_11 | Nowak | Nowak: „Technik nie żyje. Ochroniarz uciekł.” | Nowak: „Technik nie żyje, a ochroniarz uciekł pierwszej nocy.” |
| d07_17 | narrator przykłada ucho do rury | L: Przyłożyłem ucho. Ktoś płakał. | L: Przyłożyłem ucho i usłyszałem płacz. |
| d07_20 | rura: odpowiedź | L: Odpowiedziały dwa stuknięcia. Ktoś żył. | L: Odpowiedziały dwa stuknięcia, więc ktoś żył. |
| d07_22 | troje patrzy na Henryka | L: Wszyscy spojrzeliśmy na pana Henryka. | L: Wszyscy spojrzeliśmy na pana Henryka, jakby to on tu dowodził. |

## Dzień 8 · Oddział A — 72.7 s → 77.8 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d08_03 | drzwi oddziału A: łańcuch przez klamki od środka | L: Drzwi spięto łańcuchem. Od środka. | L: Łańcuch był założony od środka, więc ktoś się tam zamknął. |
| d08_05 | Kuba kręci głową na widok Henryka | Kuba: „On jest zarażony. Nie wpuszczę go.” | Kuba: „On jest zarażony, nie wpuszczę go.” |
| d08_07 | Henryk przez szybę mruga raz, bardzo powoli | L: Pan Henryk mrugnął. Raz, bardzo powoli. | L: Pan Henryk mrugnął raz, bardzo powoli. |
| d08_08 | Irena kładzie Kubie dłoń na ramieniu | Irena: „Kubuś, otwórz.” | Irena: „Kubuś, otwórz im, przecież to ludzie.” |
| d08_13 | salowy skręca za Henrykiem w głąb korytarza | L: Salowy poszedł za nim. Jak pies za gwizdkiem. | L: Salowy poszedł za nim jak pies za gwizdkiem. |
| d08_18 | Henryk spokojny | L: Był spokojny. Jakby robił to codziennie. | L: Był spokojny, jakby robił to codziennie. |
| d08_22 | noc: Kuba budzi narratora | Kuba (szept): „Nowak wychodził sam.” | Kuba (szept): „Nowak wychodził w nocy sam.” |
| d08_23 | narrator patrzy na kratę w ciemności | L: Spojrzałem na kratę. Była zamknięta. | L: Krata była zamknięta, więc musiał mieć własny klucz. |

## Dzień 9 · Rachunek — 74.7 s → 77.7 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d09_03 | Nowak | Nowak: „Do toalety.” | Nowak: „Do toalety, a dokąd miałbym chodzić?” |
| d09_04 | Zosia wskazuje ścianę z zasadami | Zosia: „Zasada trzecia. Nigdy w pojedynkę.” | Zosia: „Mieliśmy nie chodzić w pojedynkę.” |
| d09_05 | Kuba staje po stronie Nowaka | Kuba: „Zasady wymyślił wariat.” | Kuba: „Te zasady wymyślił wariat z izolatki.” |
| d09_06 | Nowak milczy, chowa dłonie w rękawach | L: Nowak nic nie powiedział. Schował dłonie w rękawach. | L: Nowak nic nie powiedział. |
| d09_07 | palec Henryka stuka w słowo PARAMI | L: Pan Henryk zastukał palcem w jedno słowo. | — *cisza* — |
| d09_11 | wszyscy leżą za regałami | L: Położyliśmy się za regałami. Wszyscy sześcioro. | L: Położyliśmy się za regałami, wszyscy sześcioro. |
| d09_12 | trzech zarażonych schodzi, każdy innym krokiem | L: Zeszło trzech. Każdy innym krokiem. | L: Zeszło ich trzech, chociaż hałas trwał tylko sekundę. |
| d09_14 | palce zarażonego na kracie owiniętej ręcznikiem | L: Kratę owinęliśmy ręcznikami. Nie zadzwoniła. | L: Krata owinięta ręcznikami nie zadzwoniła. |
| d09_16 | zarażeni odchodzą korytarzem do rozdzielni | L: Poszli dalej. W stronę rozdzielni. | L: Poszli dalej, w stronę rozdzielni. |
| d09_17 | przewrócony kanister, kałuża | L: Kuba potrącił kanister. Połowa wody wsiąkła w beton. | L: Kuba potrącił kanister i połowa wody wsiąkła w beton. |
| d09_22 | Nowak | Nowak: „Nie ruszajmy prądu.” | Nowak: „Lepiej nie ruszajmy prądu, póki tam stoją.” |
| d09_23 | Henryk mruga dwa razy szybko | L: Pan Henryk mrugnął dwa razy. Szybko. | L: Pan Henryk szybko mrugnął dwa razy, jakby się nie zgadzał. |

## Dzień 10 · Paczka — 74.2 s → 76.0 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d10_02 | nad podwórzem dron zrzuca paczkę na trawnik | megafon: „Woda i racje. Zrzut na trawniku.” | megafon: „Zrzucamy wodę i racje na trawnik.” |
| d10_05 | Kuba się zgłasza | Kuba: „Ja pójdę.” | Kuba: „Ja po nią pójdę.” |
| d10_06 | narrator | Narrator: „Idę z tobą.” | Narrator: „Idę z tobą, bo nikt nie chodzi sam.” |
| d10_07 | Zosia | Zosia: „Jeśli się odwrócą, wracacie. Bez paczki.” | Zosia: „Jeśli się odwrócą, wracacie bez paczki.” |
| d10_08 | Henryk owija im buty bandażem | L: Pan Henryk owinął nam buty bandażem. | — *cisza* — |
| d10_11 | narrator, pot na skroni | L: Szliśmy krokiem pana Henryka. Powoli. | L: Szliśmy powoli, krokiem pana Henryka. |
| d10_13 | żołnierze za płotem celują | L: Żołnierze za płotem celowali. Nie strzelali. | L: Żołnierze za płotem celowali, ale nie strzelali. |
| d10_21 | Kuba oparty o drzwi śmieje się bez tchu | L: Kuba się śmiał. Pierwszy raz, odkąd go znałem. | L: Kuba śmiał się pierwszy raz, odkąd go znałem. |
| d10_22 | w aptece: dwanaście butelek wody | L: Dwanaście butelek wody. Na trzy dni. | L: Dwanaście butelek wody starczy na trzy dni. |

## Dzień 11 · Okno — 67.2 s → 77.3 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d11_06 | dyżurka: słuchawka na biurku, cisza | L: Słuchawka już nie piszczała. Padła linia. | L: Słuchawka już nie piszczała, bo w nocy padła linia. |
| d11_07 | łazienka oddziału: narrator napełnia dwa kanistry z kranu | L: Po drodze nabrałem wody. Dwa kanistry. | L: Po drodze nabrałem z kranu dwa kanistry wody. |
| d11_09 | narrator rozkłada prześcieradło na szybie i przytrzymuje je dłońmi | L: Rozłożyłem prześcieradło na szybie. | L: Rozłożyłem prześcieradło na szybie i czekałem, aż ktoś przy bramie spojrzy. |
| d11_14 | narrator odskakuje od okna | L: Odskoczyłem. Jak sylwetka z pierwszej nocy. | L: Odskoczyłem od okna tak samo jak sylwetka z pierwszej nocy. |
| d11_20 | Zosia ogląda zadrapanie pod lampą | Zosia: „Paznokieć. Nie zęby.” | Zosia: „To ślad po paznokciu, nie po zębach.” |
| d11_22 | Nowak odwraca się do ściany i udaje, że śpi | L: Nikt nie wiedział. Nowak udał, że śpi. | L: Nikt z nas nie wiedział, a Nowak od razu udał, że śpi. |

## Dzień 12 · Plan agregatu — 69.3 s → 79.0 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d12_02 | okienko pod sufitem, szare światło | megafon: „Widzieliśmy sygnał. Zostało osiemnaście dni.” | megafon: „Widzieliśmy wasz sygnał w oknie, zostało osiemnaście dni.” |
| d12_04 | Zosia | Zosia: „Osiemnaście nocy bez prądu. Irena tego nie przetrzyma.” | Zosia: „Osiemnastu nocy bez prądu pani Irena nie przetrzyma.” |
| d12_05 | plan budynku: palec narratora na agregacie | Narrator: „Agregat da prąd. Prąd zamknie zamki.” | Narrator: „Jeśli uruchomimy agregat, prąd z powrotem zamknie zamki.” |
| d12_11 | Kuba | Kuba: „Wywabimy ich. Jak z karetką.” | Kuba: „Wywabimy ich hałasem, tak jak wtedy z karetką.” |
| d12_12 | palec Henryka na planie: stary zsyp z oddziału C do pralni | L: Pan Henryk pokazał stary zsyp na pranie. | L: Pan Henryk pokazał na planie stary zsyp na pranie. |
| d12_17 | termometr: trzydzieści dziewięć | L: Trzydzieści dziewięć stopni. | L: Miał trzydzieści dziewięć stopni, a nawet się nie obudził. |
| d12_18 | Zosia szepcze narratorowi | Zosia: „Nikomu ani słowa.” | Zosia: „Nikomu ani słowa, dopóki nie będziemy pewni.” |
| d12_20 | narrator patrzy na śpiącego Nowaka | L: Klucz do rozdzielni. Lekarz dyżurny. | L: To był klucz do rozdzielni, a miał go lekarz dyżurny. |

## Dzień 13 · Zsyp — 65.2 s → 79.0 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d13_03 | drzwiczki zsypu w ścianie obok dyżurki | L: Zsyp był obok dyżurki. Tam, gdzie to się zaczęło. | L: Zsyp był obok dyżurki, tam, gdzie to wszystko się zaczęło. |
| d13_05 | narrator patrzy na odciski | L: Na szybie zostały ich dłonie. Setki. | L: Na szybie zostały setki odcisków ich dłoni z tamtej nocy. |
| d13_07 | narrator liczy na palcach | Narrator: „Raz. Dwa. Trzy.” | Narrator: „Puszczam na trzy, a ty od razu zamykasz klapę.” |
| d13_12 | krótkofalówka w dłoni narratora | Zosia (radio): „Korytarz wolny.” | Zosia (radio): „Korytarz przy rozdzielni jest wolny.” |
| d13_13 | łącznik: za oknem, za płotem żołnierz pokazuje na niebo | L: Żołnierz za płotem pokazał na niebo. Zaraz zmrok. | L: Żołnierz za płotem pokazał na niebo, żeby nas ostrzec przed zmrokiem. |
| d13_14 | apteka: Nowak przy kracie, ubrany do drogi | Nowak: „Idę z wami. Tylko ja wiem, jak go uruchomić.” | Nowak: „Idę z wami, bo tylko ja wiem, jak go uruchomić.” |
| d13_15 | Zosia kręci głową, potem ustępuje | L: Zosia nie chciała go puścić. Ale miał rację. | L: Zosia nie chciała go puścić, ale wiedziała, że ma rację. |
| d13_17 | piwnica o zmroku: czterech idzie korytarzem obok rozdzielni | L: Poszliśmy we czterech. | L: Poszliśmy we czterech, chociaż Nowak ledwo trzymał się na nogach. |
| d13_18 | skrzydło techniczne: agregat pod plandeką, beczki z paliwem | L: Agregat stał pod plandeką. | L: Agregat stał pod plandeką, jakby nikt go od lat nie ruszał. |
| d13_19 | Nowak sprawdza poziom paliwa | Nowak: „Starczy na kilkanaście dni. Na pół mocy.” | Nowak: „Paliwa starczy na kilkanaście dni, jeśli puścimy pół mocy.” |

## Dzień 14 · Prąd — 57.3 s → 57.5 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d14_08 | Nowak krzyczy przez ryk | Nowak: „To dym z wydechu! Czujniki!” | Nowak: „To dym z wydechu, czujniki go złapały!” |
| d14_15 | narrator biegnie sam korytarzem parteru | L: Pobiegłem sam. Nie było czasu na pary. | L: Pobiegłem sam, bo nie było czasu szukać pary. |
| d14_19 | na podłodze portierni zakurzona przepustka Nowaka | L: W portierni leżała przepustka. Doktor Nowak. | L: Na podłodze portierni leżała przepustka doktora Nowaka. |
| d14_20 | piwnica: wszyscy żyją, Kuba trzyma rozciętą dłoń | L: Wszyscy żyli. Kuba rozciął dłoń o szkło. | L: Wszyscy przeżyli, tylko Kuba rozciął dłoń o szkło. |
| d14_21 | jasny, pusty korytarz | L: Szpital był jasny. I prawie pusty. | L: Szpital znowu był jasny, a korytarze prawie puste. |

## Dzień 15 · Cisza po alarmie — 68.0 s → 74.2 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d15_05 | Irena oddycha spokojnie | L: Pani Irena przestała kaszleć. Włączyło się ogrzewanie. | L: Pani Irena przestała kaszleć, bo z prądem wróciło ogrzewanie. |
| d15_06 | okienko | megafon: „Widzimy światła. Zostało piętnaście dni.” | megafon: „Widzimy u was światła, zostało piętnaście dni.” |
| d15_07 | pokój socjalny na parterze: kuchenka, kanapy, grupa wnosi rzeczy | L: Przenieśliśmy się do pokoju socjalnego. | L: Z piwnicy przenieśliśmy się do pokoju socjalnego na parterze. |
| d15_08 | ciepła woda z kranu, para | L: Pierwszy raz od dwóch tygodni ciepła woda. | L: Pierwszy raz od dwóch tygodni z kranu leciała ciepła woda. |
| d15_11 | Zosia | Zosia: „Ma gorączkę od dziesięciu dni. Nie daje się zbadać.” | Zosia: „Od dziesięciu dni ma gorączkę i nie daje się zbadać.” |
| d15_16 | noc: kreski kredą na ścianie pokoju socjalnego | L: Przenieśliśmy kreski kredą. Piętnaście. | L: Na nowej ścianie przerysowaliśmy kredą wszystkie piętnaście kresek. |

## Dzień 16 · Konfrontacja — 68.2 s → 73.0 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d16_02 | pokój socjalny: narrator kładzie przepustkę na stole, wszyscy patrzą | L: Rano położyłem przepustkę na stole. | L: Rano położyłem przepustkę na stole, przy wszystkich. |
| d16_05 | Nowak | Nowak: „Ugryzł mnie pacjent z C. Zanim puściły zamki.” | Nowak: „Ugryzł mnie pacjent z C, jeszcze zanim puściły zamki.” |
| d16_11 | Nowak | Nowak: „Wszyscy. Ja też. Tylko trochę później.” | Nowak: „Zginą wszyscy, ja też, tylko trochę później.” |
| d16_13 | Nowak | Nowak: „Prawie nic.” | Nowak: „Został mi może dzień, może dwa.” |
| d16_14 | Kuba wskazuje drzwi na podwórze, Zosia drzwi gabinetu | L: Kuba chciał go wyrzucić. Zosia zamknąć. | L: Kuba chciał go wyrzucić na podwórze, a Zosia zamknąć w gabinecie. |

## Dzień 17 · Noc przemiany — 60.5 s → 64.5 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d17_03 | Nowak w okienku | Nowak: „Mam córkę. W mieście, za kordonem.” | Nowak: „Mam córkę, mieszka w mieście, za kordonem.” |
| d17_07 | notes narratora: godziny i objawy | L: Zapisywałem godziny. Zosia prosiła o notatki. | L: Zapisywałem godziny, bo Zosia prosiła o dokładne notatki. |
| d17_09 | notes: gorączka, cisza, brak mrugania, kołysanie | L: Gorączka. Cisza. Brak mrugania. Kołysanie. | L: Pan Henryk też nie mrugał, ale żadnego innego objawu nie miał. |
| d17_12 | narrator: zrozumienie | L: Wtedy zrozumiałem. Pan Henryk nie zmienił się tamtej nocy. | L: Wtedy zrozumiałem, że pan Henryk wcale nie zmienił się tamtej nocy. |
| d17_20 | Henryk zamyka oczy i zasypia na siedząco | L: Pan Henryk zasnął. Pierwszy raz od siedemnastu dni. | L: Pan Henryk zasnął wtedy pierwszy raz od siedemnastu dni. |

## Dzień 18 · Henryk mówi — 64.8 s → 76.8 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d18_02 | pokój socjalny: Henryk budzi się na kanapie | L: Obudził się na kanapie w pokoju socjalnym. | L: Obudził się dopiero po południu, na kanapie w pokoju socjalnym. |
| d18_04 | Henryk pije powoli | L: Pił bardzo powoli. Jakby nie pamiętał smaku. | L: Pił bardzo powoli, jakby nie pamiętał smaku herbaty. |
| d18_06 | Henryk | Henryk: „Uczyłem muzyki.” | Henryk: „Całe życie uczyłem dzieci muzyki.” |
| d18_07 | Henryk | Henryk: „Po śmierci żony przestałem mówić. I spać.” | Henryk: „Po śmierci żony przestałem mówić i prawie nie spałem.” |
| d18_09 | Henryk | Henryk: „Chciałem krzyczeć. Nie umiałem.” | Henryk: „Chciałem krzyczeć, ale nie umiałem wydobyć głosu.” |
| d18_10 | narrator | Narrator: „Przepraszam.” | Narrator: „Przepraszam, że brałem pana za jednego z nich.” |
| d18_13 | Henryk | Henryk: „Muzyka to oddech. Cisza to też dźwięk.” | Henryk: „Muzyka to oddech, a cisza to też dźwięk.” |
| d18_14 | wszyscy z dłońmi na brzuchu uczą się oddychać przeponą | L: Uczył nas oddychać przeponą. | L: Przez całe popołudnie uczył nas oddychać przeponą. |
| d18_16 | świetlica wieczorem: Henryk siada przy pianinie, nie dotyka klawiszy | L: Wieczorem usiadł przy pianinie. Nie zagrał. | L: Wieczorem usiadł przy pianinie, ale nie zagrał ani jednej nuty. |
| d18_20 | przez okno: połowa ciężarówek odjeżdża spod bramy | L: W nocy megafon milczał. Połowa ciężarówek odjechała. | L: W nocy megafon milczał, a połowa ciężarówek odjechała spod bramy. |

## Dzień 19 · Głód — 62.3 s → 67.2 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d19_03 | sala 8: Zosia wywiesza nowe prześcieradło: 5 ŻYWYCH · PARTER | L: Wojsko nie zrzuciło nic więcej. | L: Od dnia paczki wojsko nie zrzuciło nam nic więcej. |
| d19_08 | Henryk patrzy długo | Henryk: „To Basia. Zawsze dawała mi dokładkę.” | Henryk: „To Basia, zawsze dawała mi dokładkę.” |
| d19_10 | Basia wychodzi wolno | L: Wyszła wolno. Jakby była zmęczona. | L: Wyszła wolno, jakby wracała z bardzo długiej zmiany. |
| d19_15 | narrator smaruje koło masłem | L: Posmarowałem koło masłem. | L: Posmarowałem koło masłem, żeby przestało piszczeć. |
| d19_17 | Irena gotuje, para nad garnkiem | L: Pierwszy ciepły posiłek od dwóch tygodni. | L: Tego wieczoru zjedliśmy pierwszy ciepły posiłek od tamtej nocy. |

## Dzień 20 · Głos z bramy — 68.2 s → 78.7 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d20_02 | narrator ze słuchawką przy uchu | Malec: „Porucznik Malec. Kordon.” | Malec: „Mówi porucznik Malec, dowódca kordonu.” |
| d20_05 | narrator | Narrator: „Pięcioro. Doktor Nowak się zmienił.” | Narrator: „Jest nas pięcioro, bo doktor Nowak się zmienił.” |
| d20_07 | narrator słucha | Malec: „W mieście to trwa krócej. Tam gryzą wiele razy.” | Malec: „W mieście to trwa krócej, bo tam gryzą wiele razy.” |
| d20_09 | narrator słucha | Malec: „Ewakuacja dnia trzydziestego. O świcie, przy bramie.” | Malec: „Ewakuacja będzie trzydziestego, o świcie, przy bramie.” |
| d20_10 | narrator | Malec: „Wychodzą zdrowi. Gorączka albo rana zostaje.” | Malec: „Wychodzą tylko zdrowi, a kto ma gorączkę albo ranę, zostaje.” |
| d20_16 | Irena spokojnie | Irena: „Ja nie przejdę. Mam gorączkę od tygodnia.” | Irena: „Ja nie przejdę, bo od tygodnia mam gorączkę.” |
| d20_17 | Henryk bierze ją za rękę | Henryk: „Jeszcze dziesięć dni. Spadnie.” | Henryk: „Do trzydziestego jest jeszcze dziesięć dni, gorączka zdąży spaść.” |
| d20_18 | sala 8: narrator przy oknie, w oddali płonie miasto | L: W oddali paliło się miasto. | L: Za lasem płonęło miasto, w którym mieszkała córka Nowaka. |
| d20_19 | narrator | L: Myślałem o córce Nowaka. | L: Nie wiedziałem, czy zdążę przekazać córce, co mówił jej ojciec. |

## Dzień 21 · Rój — 74.7 s → 78.8 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d21_03 | zamek szafy: zwykły haczyk, wygięty | L: Szafy nie trzymał prąd. Tylko haczyk. | L: Szafy nie trzymał prąd, tylko zwykły haczyk. |
| d21_12 | narrator słucha | Malec: „Ewakuacja aktualna. Jeśli dojdziecie do drogi.” | Malec: „Ewakuacja jest aktualna, jeśli dojdziecie do drogi.” |
| d21_15 | Zosia | Zosia: „Obok czterdziestu trzech nikt nie przejdzie. Choćby oddychał najciszej.” | Zosia: „Obok czterdziestu trzech nikt nie przejdzie, choćby oddychał najciszej.” |
| d21_18 | Henryk | Henryk: „Pianino nie. Alarm tak.” | Henryk: „Pianino jest za ciche, ale alarm ich zawoła.” |
| d21_19 | portiernia: wyrwane w dniu 14 przewody zwisają z centrali alarmu | Narrator: „Wyrwałem przewody.” | Narrator: „Przecież sam wyrwałem z niego przewody.” |
| d21_20 | Henryk | Henryk: „Można je połączyć. Alarm włącza każdy przycisk w budynku.” | Henryk: „Można je połączyć, a alarm włącza każdy przycisk w budynku.” |

## Dzień 22 · Woda — 69.3 s → 72.3 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d22_03 | Zosia liczy butelki i kanistry na stole | Zosia: „Wody na siedem dni. Do trzydziestego jest osiem.” | Zosia: „Wody mamy na siedem dni, a do trzydziestego jest osiem.” |
| d22_15 | dach o zachodzie: dwie postacie leżą bez ruchu przy zbiorniku | L: Czekaliśmy, aż o nas zapomną. Słońce zdążyło zajść. | L: Czekaliśmy, aż o nas zapomną, i w tym czasie zaszło słońce. |
| d22_21 | dłoń Zosi pod lampą: rana ropieje | Zosia: „Nic nie mówiłam. Ropieje.” | Zosia: „Nic nie mówiłam, a teraz rana ropieje.” |

## Dzień 23 · Zosia — 57.7 s → 60.3 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d23_03 | Zosia | Zosia: „To zakażenie bakteryjne. Nie ugryzienie.” | Zosia: „To zwykłe zakażenie bakteryjne, a nie ugryzienie.” |
| d23_04 | Zosia | Zosia: „Ale żołnierze zobaczą ranę i gorączkę. Nie będą dociekać.” | Zosia: „Ale żołnierze zobaczą ranę i gorączkę, więc nie będą dociekać.” |
| d23_06 | Zosia | Zosia: „Chirurgia. Wieża, najwyższe piętro. Zamknięta szafa.” | Zosia: „Antybiotyk jest na chirurgii, w wieży, w zamkniętej szafie.” |
| d23_08 | Kuba zostaje przy chorych; narrator w drzwiach z latarką | L: Kuba musiał zostać z chorymi. Poszedłem sam. | L: Kuba musiał zostać z chorymi, więc poszedłem sam. |
| d23_10 | ciemny korytarz chirurgii; z obu stron dłonie suną po szybach drzwi | L: Agregat ciągnął tylko połowę obwodów. Wieża była ciemna. | L: Agregat ciągnął tylko połowę obwodów, więc wieża była ciemna. |

## Dzień 24 · Gorączka — 56.7 s → 57.7 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d24_14 | oczy Zosi: mruga często, nerwowo | L: Patrzyłem, czy mruga. Mrugała. | L: Całą noc patrzyłem, czy mruga, a ona mrugała. |

## Dzień 25 · Kuba — 64.8 s → 71.3 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d25_02 | narrator ze słuchawką | Malec: „Zostało pięć dni. Podwórze jest pełne.” | Malec: „Zostało pięć dni, a podwórze jest pełne.” |
| d25_03 | narrator słucha | Malec: „Wyjdźcie dachem. Zjedźcie po linie na tył.” | Malec: „Wyjdźcie dachem i zjedźcie po linie na tył budynku.” |
| d25_04 | narrator | Narrator: „Pani Irena nie zjedzie po linie. Zosia ledwo chodzi.” | Narrator: „Pani Irena nie zjedzie po linie, a Zosia ledwo chodzi.” |
| d25_11 | Henryk chwyta Kubę za ramiona | Henryk: „Patrz na mnie. Cztery wdech. Cztery trzymaj. Cztery wydech.” | Henryk: „Patrz na mnie: na cztery wdech, na cztery trzymasz, na cztery wydech.” |
| d25_15 | Henryk | Henryk: „Mnie też nie. Dopóki nie straciłem głosu.” | Henryk: „Mnie też nikt nie uczył, dopóki nie straciłem głosu.” |
| d25_18 | palce Kuby grają w powietrzu pięć nut | L: Pięć nut. Powtarzał je, aż zapamiętał. | L: Pięć nut powtarzał w powietrzu tak długo, aż je zapamiętał. |
| d25_19 | Henryk | Henryk: „Kołysanka mojej żony.” | Henryk: „To kołysanka, którą śpiewała moja żona.” |
| d25_20 | noc: Irena budzi narratora | Irena: „Trzydziestego zostanę tutaj. I tak nie przejdę badania.” | Irena: „Trzydziestego zostanę tutaj, bo i tak nie przejdę badania.” |

## Dzień 26 · Miasto gaśnie — 70.7 s → 73.5 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d26_02 | rano przy stole Irena mówi do wszystkich, spokojnie | Irena: „Osiemdziesiąt jeden lat. Chore płuca. Nikogo za bramą.” | Irena: „Mam osiemdziesiąt jeden lat, chore płuca i nikogo za bramą.” |
| d26_03 | Zosia | Zosia: „Zapalenie płuc to nie zarażenie. Lekarz wojskowy to zobaczy.” | Zosia: „Zapalenie płuc to nie zarażenie, lekarz wojskowy to zobaczy.” |
| d26_10 | narrator ze słuchawką | Malec: „Część kordonu poszła do miasta. Zostaje pluton i jedna ciężarówka.” | Malec: „Część kordonu poszła do miasta, zostaje pluton i jedna ciężarówka.” |
| d26_12 | narrator słucha | Malec: „Do punktu za rzeką. Biorą tylko zdrowych.” | Malec: „Do punktu za rzeką, gdzie biorą tylko zdrowych.” |
| d26_15 | Zosia | Zosia: „Paliwa na cztery dni. Potem zgaśnie światło i puszczą zamki.” | Zosia: „Paliwa starczy na cztery dni, potem zgaśnie światło i puszczą zamki.” |
| d26_17 | Henryk | Henryk: „To dobrze. Nie ma nad czym myśleć.” | Henryk: „To dobrze, przynajmniej nie ma nad czym myśleć.” |

## Dzień 27 · Plan — 71.8 s → 78.0 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d27_04 | Henryk | Henryk: „Połączymy alarm. Ściągnie ich do środka, za dźwiękiem.” | Henryk: „Połączymy alarm, a on ściągnie ich za dźwiękiem do środka.” |
| d27_05 | palec Henryka na planie: od bocznych drzwi do bramy | Henryk: „Wy wyjdziecie bokiem.” | Henryk: „A wy w tym czasie wyjdziecie bokiem.” |
| d27_08 | narrator | Narrator: „Ja. To ja wyrwałem przewody.” | Narrator: „Ja zostanę, bo to ja wyrwałem przewody.” |
| d27_09 | Henryk kręci głową | Henryk: „Ty masz obietnicę. Dla córki doktora.” | Henryk: „Ty obiecałeś coś doktorowi i musisz dojść do jego córki.” |
| d27_10 | Zosia | Zosia: „Pan też może wyjść. Nie ma pan gorączki ani rany.” | Zosia: „Pan też może wyjść, bo nie ma pan gorączki ani rany.” |
| d27_20 | narrator przy oknie | L: Plan zadziała. I pan Henryk naprawdę zostanie. | L: Wiedziałem już, że plan zadziała i że pan Henryk naprawdę zostanie. |

## Dzień 28 · Pożegnanie — 67.7 s → 72.2 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d28_04 | Henryk | Henryk: „Od dawna nie.” | Henryk: „Od dawna już się nie boję.” |
| d28_08 | Henryk przy drzwiach sali | Henryk: „Pani Jadzia.” | Henryk: „To pani Jadzia, zawsze pierwsza wstawała.” |
| d28_09 | Henryk przy następnych drzwiach | Henryk: „Pan Staś. Lubił krzyżówki.” | Henryk: „A to pan Staś, który lubił krzyżówki.” |
| d28_10 | narrator patrzy na Henryka | L: Znał ich wszystkich. Latami patrzył na nich przez okienko. | L: Znał ich wszystkich, bo latami patrzył na nich przez okienko. |

## Dzień 29 · Ostatnia noc — 64.8 s → 66.2 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d29_04 | Zosia | Zosia: „Nie doczekamy szóstej. Zamki puszczą wcześniej.” | Zosia: „Nie doczekamy szóstej, bo zamki puszczą wcześniej.” |
| d29_06 | plecak: narrator pakuje notes i przepustkę Nowaka | L: Notatki z izolatki i przepustka. Dla jego córki. | L: Spakowałem notatki z izolatki i przepustkę Nowaka dla jego córki. |

## Dzień 30 · Świt — 71.3 s → 73.3 s

| ujęcie | kadr | przed | po |
|---|---|---|---|
| d30_07 | grupa idzie wolno przez podwórze | L: Szliśmy wolno. Bieg jest głośniejszy niż oddech. | L: Szliśmy wolno, bo bieg jest głośniejszy niż oddech. |
| d30_11 | lekarz wojskowy patrzy na ranę Zosi i macha: przechodź | Lekarz: „Trzydzieści siedem i osiem. Przechodzi.” | Lekarz: „Trzydzieści siedem i osiem, może przejść.” |
| d30_16 | narrator rozumie | L: To krzyczał pan Henryk. Odzyskał głos. | L: To krzyczał pan Henryk, który w końcu odzyskał głos. |

