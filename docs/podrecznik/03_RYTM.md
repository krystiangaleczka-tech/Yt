# Rytm i tempo ujęć

Wzorzec do porównań wybiera reżyser dla każdego filmu (np. gotowe, poprawione otwarcie) i zapisuje go w warsztacie
filmu. Zasady poniżej są wspólne.

1. **Ujęcie = wydarzenie.** W każdym ujęciu coś się zmienia w określonej chwili: ktoś staje, odwraca głowę, gaśnie
   światło, coś spada. Cięcie pada po wydarzeniu. Statyczna ilustracja zdania z lekkim zoomem to błąd.
2. **Długość z treści, nigdy z siatki.** Otwarcie sceny 4–7 s; akcja 1–1,8 s; reakcja bez słów 1,2–2 s; detal
   1,5–2,5 s; napięcie i cisza 2,5–6 s; ujęcie z kwestią: oddech przed (0,5–1,2 s) + kwestia (~2,6 słowa/s) + pauza
   po: co najmniej 1 s, zanim padnie cięcie — dłużej na końcu beatu (~1,4 s), sceny (~1,8 s) i aktu (~2,3 s); cięcie
   zaraz po ostatnim słowie (0,6 s) reżyser odbiera jako nienaturalne. Sąsiednie ujęcia różnią się co najmniej o ¼ s.
   Teatr papierowy jest spokojniejszy niż kreskówka: we wzorcu („Pierwszy cesarz” EN, 80 ujęć, 11:18) ujęcie z kwestią
   trwa 5,3–15,5 s (mediana 9 s), bez słów 1,4–7,8 s; ujęcia z budową, wojskiem, tłumem i podróżą dostały od reżysera
   2–5 s ponad kwestię, bo wydarzenie ma się skończyć na oczach widza (Wytyczne ujęć 1.8, 1.18).
3. **Rytm sceny:** szeroko i długo na otwarcie → coraz krótsze ujęcia do kulminacji → długie trzymanie albo krótkie
   żądło na koniec. Jednostka trwa tyle, ile wynika z treści, w zakresie ustalonym dla filmu (np. 60–100 s); dzień z dużą ilością mowy po prostu trwa dłużej.
4. **Lektor dopowiada, obraz pokazuje.** Kwestia nie opisuje tego, co widać. Cisza zostaje w co trzecim–czwartym
   ujęciu (reakcje, detale, żądła).
   **Kwestia to pełne zdanie** z czasownikiem, bez urwanych dopowiedzeń („Kratę owinęliśmy ręcznikami, żeby nie
   zadzwoniła.”, nie „…ręcznikami. Nie zadzwoniła.”). W sekwencjach zdarzeń kwestie łączą łączniki: wtedy, potem,
   następnie, wówczas, później, wcześniej, natomiast, bo, żeby, aby, więc, ale — nie w każdej kwestii; krótkie zdanie
   zostaje tam, gdzie jest żądłem.
5. **Napis = kwestia**: pojawia się z głosem, znika chwilę po nim.
6. **Życie w kadrze:** mruganie w nieregularnych odstępach (nigdy wszyscy naraz), oddech, błądzący wzrok; kamera lekko
   pływa; tło żyje (wiatr, migotanie). Cechy postaci mają pierwszeństwo (np. postać, która nie mruga).
7. **Światło jako dramaturgia** — zgaszenie, ciemność, wyjście w czerń są wydarzeniem w ujęciu. Między zwykłymi
   ujęciami jest cięcie. Teatr papierowy (reżyser, 15.11.2026): **kurtyna między aktami** — zasuwa się w pauzie na
   końcu aktu, na niej tytuł następnego aktu, rozsuwa się na początku nowego (dekoracja buduje się za nią);
   **ściemnienie światła przy zmianie miejsca** w akcie (ok. 0,35 s gaśnie i 0,35 s się zapala). Przejścia nachodzą
   na pauzę po kwestii, więc film nie robi się od nich dłuższy. Kurtyna ma swój dźwięk (reżyser, 16.11.2026): przy zasuwaniu
   aksamit sunie, kółka stukają o drążek, połowy spotykają się z miękkim „fump”, a klapki teatralne stukają przy tytule;
   przy rozsuwaniu kółka szarpią na starcie (`efekty.kurtyna_nowa` „Pierwszego cesarza”). Bez przesuwania całego kadru z boku czy z góry —
   dekoracja i tak wjeżdża, a slajd wygląda jak program do prezentacji. Kod: `render.przejscie` filmu.
8. **Tłum to osobne postacie** (opóźnienia, tempo, jeden spóźniony).
9. **Dźwięk:** ciągłe tło pod całością, osobny dźwięk każdego wydarzenia, lektor.
10. **Głośność dźwięku wynika ze sceny, nie z biblioteki.** Każdy dźwięk ma poziom z trzech rzeczy:
    - **skala zdarzenia** — małe (krok, papier, klamka, oddech), średnie (drzwi, zamek, jęk, woda, metal),
      duże (huk, strzał, alarm, regał, agregat);
    - **napięcie sceny** (0–10, z krzywej filmu, ruchu kamery i słów akcji, wygładzone w scenie) — im wyższe,
      tym głośniej i gęściej; rozmowa obniża efekty, „cisza” w rozpisce zostawia ledwie słyszalne tło i serce;
    - **tempo ujęcia** — krótkie ujęcia w akcji o włos głośniej, długie i spokojne ciszej.
    Tło miejsca (pomieszczenie, wiatr, kapanie) jest zawsze cicho pod spodem; **żadnych stałych buczeń sieciowych**
    (50/100 Hz) — świetlówka czy agregat brzmią tylko wtedy, gdy są wydarzeniem w scenie. Pod kwestią efekty
    schodzą o ok. 6 dB, muzyka o 8 dB.
11. **Muzyka niesie nastrój beatu, nie ilustruje zdania.** Nastrój z napięcia i treści: brak (cisza, karta,
    muzyka grana w kadrze), cicha plama, niepokój, puls, napęd (akcja), motyw (wspomnienie, czułość), finał.
    Sąsiednie beaty o tym samym nastroju to jedna fraza. Motyw, który pojawi się w kadrze (piosenka, melodia
    postaci), wcześniej wraca w muzyce jako zasiew.
12. **Plan miksu jest zapisany w projekcie:** opis ujęcia ma wiersz „Dźwięk (plan miksu)” (napięcie, tempo, tło,
    zdarzenia ze skalą i dB, muzyka), a klipy na ścieżkach Tło / Efekty / Muzyka mają poziom w tytule. Reżyser
    poprawia go gałką głośności klipu w Montażu — wtedy plan i oś mówią to samo.

## Początek filmu i utrzymanie uwagi — lekcja z wyników „Pierwszego cesarza” (19.11.2026)

**Liczby po 1 dniu 20 h.** 287 wyświetleń, 137 unikalnych widzów, 6,3 h oglądania. Średnio 1:24–1:29 z 11:19 (13 %), po
30 s ogląda tylko 35 %, spadek trwa do ok. 3:45, potem równo 8–10 % do końca. Aż 206 z 287 wyświetleń przyszło z reklamy
YouTube (zimny widz), miniatura: 392 wyświetlenia, CTR 5,4 %. Reakcje: +11 subskrypcji (8 % widzów), 15 polubień, 0 łapek w
dół, 6 udostępnień, 4 komentarze. Telefon 56 %, tablet 17 %, komputer i TV po 14 %; napisy angielskie włącza 26 %; USA 49 %,
Polska 12 %; kobiety 58 %.

**Co działa.** Kto przetrwa ok. 4 minuty, zostaje do końca i reaguje (8 % subskrybuje, zero łapek w dół, udostępnienia) — teatr
i opowieść się bronią. Miniatura klika się przyzwoicie.

**Co zawiodło (wersja opublikowana).**
1. Martwy start: ok. 3 s pustej ramy z tytułem i 3 s krajobrazu, zanim padło pierwsze słowo.
2. Brak haka i pytania: „Long ago, this land was divided…” — tło chronologiczne od narodzin, widz nie wie, po co ogląda.
3. Za dużo nazw na starcie: siedem królestw, Zheng, Handan, Qin, Lü Buwei w 40 s.
4. Jedna dekoracja przez pierwszą minutę, a w 1:18 kurtyna z tytułem aktu — „koniec rozdziału” w chwili, gdy widz decyduje.
5. 72 % ruchu z reklamy zaniża utrzymanie; bez rozbicia na źródła ruchu wykres miesza zimnego widza z prawdziwym.

**Zasady od „Bonnie and Clyde”** (uzupełniają przepis na otwarcie z 18.11):
1. Pierwsza klatka już w ruchu i na temat. Zapowiedź 6 s: ok. 10 cięć po 0,6 s na uderzeniach muzyki, na końcu ściemnienie.
2. Kurtyna tytułu krótko (ok. 2,5 s; z kwestią tyle, żeby po niej została ≥1 s obrazu). **Lektor mówi od pierwszej sekundy**, już na zapowiedzi: jedno zdanie o tym, o czym
   jest film (bohaterowie i stawka), a w kurtynie krótkie zdanie, które stawia pytanie („Syn słońca”: „Japan began with gods,
   monsters, and four brothers who set out to rule it.” → „Only one of them survived.”). Krzywa „Cesarza” odczytana ze
   zrzutu: ok. 72 % w 6 s, kiedy padło pierwsze słowo, 62 % w 9 s, 50 % w 15 s, 35 % w 30 s, 21 % w 60 s — każda sekunda
   ciszy na starcie kosztuje kilka procent widzów (20.11.2026, reżyser: „mogę gadać nawet od 1 s filmu”; wcześniej było
   „najpóźniej ok. 9 s”).
3. **Jeden początek.** Po zapowiedzi i tytule opowieść już się toczy: hak (tajemnica) w pierwszych 15–30 s, a obietnica to jedno
   pytanie, które prowadzi prosto w retrospekcję („It all starts…”) — bez listy „By the end, you'll know…”.
4. Między prologiem a aktem I **bez kurtyny i tabliczki aktu** (wygląda jak drugi start filmu); zamiast niej ściemnienie i
   zawieszka miejsca i czasu („West Dallas, 1920s”). Kurtyny z tytułami aktów od aktu II.
5. Tło bohatera krótko i z napięciem; nowa nazwa najwyżej co ok. 20 s i zawsze z podpisem; co 45–60 s nowe pytanie albo zwrot.
6. Podpisy i tabliczki czytelne na telefonie. Napisy lektora tylko jako osobne pliki EN i PL — od 24.11 nie wypala się ich
   w obrazie (Wytyczne 1.13).
7. Wyniki czytać po źródłach ruchu; reklamę puszczać, gdy ruch organiczny trzyma po 30 s co najmniej ok. 60 %.

**Wyniki „Bonnie and Clyde” (opublikowany 25.11.2026 o 0:47, 18:20, bez reklamy).** Po 18 h: 291 wyświetleń miniatury,
CTR 2,1 %, 9 wyświetleń; po ok. 36 h: 366 wyświetleń miniatury, CTR 1,9 %, 24 wyświetlenia, z czego tylko 7 z kliknięć
w miniaturę i ok. 5 osób (reszta to powtórne odtworzenia), średnio 8:34 (7:31 u tych, którzy kliknęli miniaturę), 2
udostępnienia, 6 polubień. Reżyser: „film 18 min, myślałem, że im dłuższy, tym się będzie lepiej oglądał, a tu nagle dupa”.
Wnioski:
1. **Długość nie przyciąga widzów** — najpierw decyduje miniaturka (CTR), potem pierwsze 30 s. Kto kliknął, oglądał
   długo, więc historia i teatr się bronią; brakowało wejść (Wytyczne 5.6). Docelowa długość zostaje 8–12 min (reżyser
   10.11); dłuższy film tylko wtedy, gdy historia tego wymaga i reżyser zatwierdzi to w szkicu („Bonnie and Clyde”: szkic D
   = A + pościg Hamera, 17:40 → 18:19).
2. **Shortsy od razu po filmie.** Shortsy kanału miały po 34–184 wyświetleń, czyli tyle co długie filmy — film bez Shortsów
   traci drugie wejście (Podręcznik → Publikacja).
3. Liczby z pierwszych dni czyta się po źródłach ruchu i po unikalnych widzach; ocena po 7 i 28 dniach.

**Jak skrócić akt tła (Bonnie and Clyde, akt I: 149 → 119 s, 19.11.2026).** Ujęcie, którego treść da się dopowiedzieć
w sąsiedniej kwestii, wypada („szkoła” → „Bonnie Parker wrote poems…” w kwestii ślubu; więzienie Roya i obrączka →
kawiarnia). Akcja, o której mówi lektor, idzie w krótkich niemych gagach 3,5–4,5 s z tabliczką (areszt „HEY!”, peron
„OH NO”, brama „PAROLE”). Kwestie zwięzłe, z ironią na końcu („something exciting finally happened: … he was
arrested”). Ostatnie ujęcie aktu zostawia pytanie.

**Szybkie cięcia a zasada ¼ s.** Sąsiednie ujęcia różnią się co najmniej o 0,25 s, więc równe cięcia 0,6 s rozpiska
sama wydłuża. Zapowiedź tnie się parami 0,4 / 0,7 s (różnica bez błędów zaokrągleń), a ostatnie ujęcie z wyciemnieniem
jest dłuższe.

### Ujęcie = kwestia + wydarzenia (lekcja z „Imama / Diuny”, 28.11.2026)

Wersja D filmu o Szamilu (76 ujęć, 5:55) miała połowę ujęć bez słów — detale 1,4–2,4 s — a ujęcia z kwestią po 6–10 s,
w których lalka tylko stała. Reżyser po minucie: „trzy ujęcia jakieś długie, nagle jedno, które ma pół sekundy… dwa długie,
a jeszcze nic się na nich nie dzieje”, „cały początek… nic nie wiadomo, o co chodzi”, „brakuje gagów”. Film przebudowano
od rozpiski (szkic E: 70 ujęć, 9:55, kwestia w 61, 22 gagi). Zasady:
1. **Każde ujęcie z kwestią ma 2–4 wydarzenia na słowach lektora** (w opisie rozpiski z sekundami, w kodzie `sl()`), gag stoi
   w pauzie po kwestii. Detal nie jest osobnym ujęciem, tylko wydarzeniem w ujęciu z kwestią.
2. **Krótkie ujęcia nie stoją samotnie** między długimi — bez słów zostaje zapowiedź, kurtyna i emocjonalne trzymanie.
   Cisza mieszka w pauzie po kwestii i w gagu.
3. **Długość z historii**, nie z formatu (4–5 min było za krótko na tę historię; wyszło prawie 10 min).
4. **Otwarcie od tego, co widz zna** (pustynia Diuny i jej słowa), potem zwrot („te słowa są z gór Kaukazu”), kim jest bohater,
   hak i jedno pytanie. Karta z cytatem jako hak była dla zimnego widza niezrozumiała.
5. **Każda scena ma swoje miejsce** — w D prawie wszystko działo się na tych samych szarych górach; w E są pustynia, Gimry
   z wieżą, gabinet z mapą, bukowy las, Dargo, Kaługa, pracownie pisarzy.
6. Przed rysunkiem `kontrola_rytmu()` z rozpiski filmu: zero uwag.

### Skracanie a pomosty (lekcja z 19.11.2026)

Przy skracaniu aktu nie wycina się ujęcia, które przenosi opowieść do innej postaci albo miejsca, choćby było „tylko tłem”.
W „Bonnie and Clyde” wypadło ujęcie szkoły Bonnie i po indykach Clyde'a od razu zaczynał się ślub Bonnie; reżyser: „to nie
ma sensu”. Pomost wrócił jako krótkie ujęcie z łącznikiem w kwestii („Meanwhile, a few miles away…”), zawieszką miejsca
i rzeczą, która przechodzi z ujęcia do ujęcia. Po każdym skróceniu wypisz granice scen (koniec i początek kwestii) i sprawdź
łączniki (Wytyczne 1.27).

