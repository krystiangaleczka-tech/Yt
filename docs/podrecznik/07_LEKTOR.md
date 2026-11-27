# Lektor: głos jak z wyciszonego studia

Lektor to klon głosu autora (Chatterbox Multilingual; wersja angielska z emocjami: Chatterbox Turbo). Ma brzmieć sucho i blisko, jak nagrany w wyciszonym studiu:
bez pogłosu pokoju, bez zamulenia, bez dziwnych dźwięków w nazwach. Narzędzie wspólne dla filmów:
`docos/lektor_studio.py`; skrypt lektora filmu (np. `output/pierwszy-cesarz/lektor.py`) tylko nagrywa podejścia.
Lektor teatru papierowego zawsze według przepisu z zasady 8.

## Zasady

1. **Pogłos usuwa się z próbki, nie z nagrania.** Chatterbox kopiuje akustykę próbki — pogłos w próbce to pogłos
   w każdej kwestii. Próbkę przepuszcza się raz przez resemble-enhance (`lektor_studio.py probka`) i z niej nagrywa
   wszystko: `pilot/assets/ref_studio.wav`. Surowe nagranie z telefonu nigdy nie jest próbką. Filtrów odszumiania
   pogłosu ani EQ na gotowych kwestiach się nie używa — brzmią gorzej i dokładają artefaktów.
2. **Jedno podejście na kwestię** (ziarno 42, `ZIARNA=42`; reżyser 18.11 i 20.11.2026: „rób jedno podejście, no bo po co
   będziesz robić na każde ujęcie 3 podejścia? To będzie trwało wieczność, a my to mamy zrobić w miarę szybko”). Innym ziarnem
   (123, potem 7) nagrywa się od nowa tylko kwestie, w których kontrola (Whisper, `docos/uciecia_lektora.py`) albo odsłuch
   znajdzie błąd. Trzy podejścia z wyborem (ziarna 42, 7, 123 — różnią się rytmem: gdzie lektor bierze oddech, jak prowadzi
   melodię, a nie barwą) tylko wtedy, gdy reżyser o nie poprosi; wtedy wybiera się według zasady 4. Wzór: „Bonnie and
   Clyde” 23.11 — 100 kwestii jednym podejściem (ok. 2,5 h na procesorze Maca), 12 nagranych od nowa ziarnem 123.
3. **Każde podejście suche i z pełnym pasmem.** Bramka na szum między słowami, kompresja, lekka korekcja, potem
   resemble-enhance odbudowuje pasmo powyżej ~8 kHz, którego Chatterbox sam nie generuje. Długość kwestii się nie
   zmienia, więc ujęcia pasują dalej.
4. **Wybór podejścia: oddech na każdym przecinku.** Wygrywa podejście z pauzą na każdym przecinku i kropce w środku
   kwestii; z równych — spokojniejsze (dłuższe pauzy). Odpadają podejścia, w których model się powtórzył albo które
   są o ponad ¼ dłuższe lub krótsze od pozostałych (zacięcie). Wzorzec: „W jednym z nich, w mieście Handan, urodził
   się chłopiec…” — z oddechem po „Handan”, nazwa zostaje w uchu.
5. **Reżyser ma ostatnie słowo.** Słucha kwestii; gdy chce inne podejście, wpisuje je w `lektor/podejscia/wybor.json`
   (np. `{"handan": 7}`) i uruchamia `lektor_studio.py podejscia` jeszcze raz. Pozostałe podejścia zostają
   w `lektor/podejscia/` do odsłuchu.
6. **Próbki nie publikuje się** — z niej da się sklonować głos. `pilot/assets/` i pliki `.wav` nie trafiają do repo;
   na drugi komputer próbkę przenosi się osobno.
7. **Emocje w tekście = Chatterbox Turbo, po angielsku.** Śmiech, westchnienie, szept, dramatyczny ton
   (`[chuckle] [sigh] [whispering] [dramatic] [gasp]`, pauza `...`) czyta tylko Turbo, a Turbo mówi wyłącznie po
   angielsku — Multilingual (polski) znaczniki pomija. Wersja angielska: tekst mówiony ze znacznikami w
   `aktorskie_en.json` filmu, ten sam sposób (próbka bez pogłosu, podejścia według zasady 2, sucho), próbka
   z angielskiego nagrania autora (`ref_en_studio.wav`). Każde podejście sprawdza Whisper: podejście, w którym nie
   usłyszał tekstu (zgodność < 0,92 — połknięte słowo, powtórka), odpada przy wyborze jak powtórzenie modelu.
8. **Teatr papierowy: zawsze ten sam przepis** („w ten sposób chcę mieć zawsze robiony lektor dla paper theatre”,
   14.11.2026). Nagrywa się z ustawieniami `TEATR` z `docos/lektor_studio.py` (Chatterbox Multilingual:
   exaggeration 1,0, cfg_weight 0,3, temperature 0,7 — mocna ekspresja), dalej podejście według zasady 2,
   a wybrane podejście kończy `lektor_studio.py podejscia --teatr`:
   - **mowa wolniej o 3 %** (atempo 0,97 — wysokość głosu bez zmian),
   - **pauzy w środku kwestii losowane z zakresów** (`docos/pauzy_lektora.py`), bo człowiek nie mówi z jedną pauzą:

     | Pauza | Od–do (s) |
     |---|---|
     | po zdaniu do 8 słów / 9–16 słów / 17 i więcej | 0,60–0,80 / 0,70–0,90 / 0,85–1,05 |
     | co drugie zdanie, po „?” i „!” | +0,10 (razem najwyżej 1,20) |
     | przecinek | 0,30–0,50 |
     | przecinek po słowie zakończonym samogłoską | +0,15 |
     | po nazwie własnej (nazwa zostaje w uchu) | +0,10 |
     | po słowie 4+ sylab / jednosylabowym | +0,05 / −0,05 |
     | średnik, dwukropek / myślnik / wielokropek | 0,45–0,65 / 0,40–0,60 / 0,80–1,10 |
     | pauza bez znaku w tekście dłuższa niż 0,3 s | skrócona do 0,15–0,25 |

     Dwie kolejne pauzy tego samego rodzaju różnią się co najmniej o 0,06 s. Ziarno losowania bierze się z klucza
     kwestii, więc ponowny przebieg daje te same pauzy. Zakresy pochodzą z bajki czytanej przez aktorkę (mediana
     pauzy 0,58 s, prawie nigdy ponad 1,2 s) i z uwag reżysera; zmienia się je w jednym miejscu, na górze
     `pauzy_lektora.py`.
   - Pauzę po kwestii ustala montaż ujęć (Rytm), nie lektor. Dłuższe pauzy w kwestii wydłużają ją, więc ujęcie
     poprawia się w Studio stopklatką.
   - Mocna ekspresja częściej się powtarza — podejście z powtórzeniem (Whisper, odsłuch) nagrywa się od nowa innym
     ziarnem (zasady 2 i 11).
   - Pauzę mierzy się jako ciszę między słowami, nie odstęp między plikami: plik kwestii bywa z ciszą na końcu.
   - Wersja angielska (Turbo) jeszcze bez tego przepisu: Turbo nie ma tych ustawień, a zakresy pauz są pod polski.
   - Mowy nie zwalnia się bardziej niż o te 3 %: rozciągnięta mowa (atempo 0,81) brzmi jak autotune, samogłoski
     falują. Film czytany wolniej dostaje dłuższe pauzy (`PAUZY_SKALA`, np. 1,3) i przecinki frazowania w tekście
     mówionym przed nagraniem, a nie rozciąganie.
9. **Kwestia nie może się urywać.** Każde słowo wygasa samo, także ostatnie w kwestii („dziwne przycięcia w środku
   słowa albo przy końcu słowa”, 16.11.2026). Przed odsłuchem i przed Studio: `docos/uciecia_lektora.py <katalog
   lektora>` — zero uwag.
   - Ciszę obcina się tylko na brzegach, dopiero poniżej −55 dB i z zapasem 0,12 s (`lektor_studio.py`). W pauzach
     zostaje 0,12 s wybrzmienia wygaszanego do zera i 0,06 s nabiegu przed słowem (`pauzy_lektora.py`). Kwestii
     pociętych z nagrania autora nie przycina się drugi raz po ciszy — tylko łagodne wejście i wygaszenie.
   - Chatterbox czasem urywa ostatnie słowo (podejście kończy się głosem, nie ciszą), a resemble-enhance rzadko
     wycina ciche wybrzmienie jak szum. Takiej kwestii nie łata się obróbką: nagrywa się ją innym ziarnem i wybrane
     podejście wpisuje w `wybor.json`.
   - Ciszy (oddechów) nie wstawia się w gotowe nagranie klona po fakcie — automat brał za przerwę miejsce w środku
     słowa.
10. **Nazwy czyta się tak, jak się je wymawia.** Klon czyta pisownię, więc nazwy, które wymawia się inaczej, dostają zapis
    fonetyczny w tekście mówionym (`WYMOWA` w skrypcie lektora filmu; „Bonnie and Clyde”: Hamer → Haymer, Eastham → Eastum,
    Waco → Wayco). Napisy, tabliczki i rozpiska zostają w pisowni oryginalnej. Liczby czyta się słowami (`dane.SLOWNIE`).
11. **Kwestia nagrana od nowa wygrywa automatycznie, nie „ręką reżysera”.** Nowe ziarno: `BEZ_OBROBKI=1` i same klucze,
    potem złe podejście przenieś do `podejscia/odrzucone/` i usuń z `podejscia/<klucz>.json`, żeby automat wybrał nowe —
    wpis w `wybor.json` oznaczyłby je jako wybór reżysera. Nowe albo zmienione kwestie po uwadze reżysera („daj narrację”,
    „więcej wyjaśnień”) nagrywa się klonem od razu i oddaje „do odsłuchu” w raporcie tury; długość ujęcia idzie z nagrania
    (`render.czas_akcji`, Animacja kodem).

## Jak

```bash
# raz na próbkę głosu (środowisko z resemble-enhance: pilot/.venv-enhance, na PC .venv-enhance)
pilot/.venv-enhance/bin/python -I docos/lektor_studio.py probka nagranie.m4a pilot/assets/ref_studio.wav
# kwestie filmu: podejścia, obróbka i wybór (lektor.py sam wywołuje lektor_studio.py podejscia)
pilot/.venv-tts/bin/python -I output/<film>/lektor.py [klucz …]
# po zmianie wybor.json (teatr papierowy: z --teatr, jak lektor.py)
pilot/.venv-enhance/bin/python -I docos/lektor_studio.py podejscia output/<film>/lektor --teatr
# kontrola urwanych słów (zasada 9) — przed odsłuchem i przed Studio
pilot/.venv-enhance/bin/python -I docos/uciecia_lektora.py output/<film>/lektor
# kwestie do nagrania od nowa innym ziarnem (na Macu bez Whispera: SPRAWDZ=0, LEKTOR_DEVICE=mps), potem wybor.json
ZIARNA=7 BEZ_OBROBKI=1 TEATR=1 pilot/.venv-tts/bin/python -I output/<film>/lektor.py klucz1 klucz2
# próba ciągłego tekstu (kwestie sklejone z pauzami po zdaniach), inne ziarno = inne pauzy
pilot/.venv-enhance/bin/python -I docos/pauzy_lektora.py output/<film>/lektor proba.wav klucz1 klucz2 … --ziarno 1
```

Wersja angielska z emocjami (Turbo) — na PC dwuklik `output/pierwszy-cesarz/pc/zrob_film_en.bat`, albo:

```bash
JEZYK=en SILNIK=turbo AKTORSKIE=output/<film>/aktorskie_en.json PROMPT=pilot/assets/ref_en_studio.wav \
  python -I output/<film>/lektor_en.py [klucz …]     # → lektor_en/podejscia, wybór w lektor_en/
```

Nagrywanie idzie na PC z kartą NVIDIA (kilka sekund na podejście; RTX 4070, Turbo z Whisperem: 67 kwestii × 3
podejścia ok. 8 min, obróbka wszystkich ok. 4 min). Na Macu z 8 GB RAM: ok. 1–2 min na podejście przez MPS —
i tylko przy wolnej pamięci (zamknięty emulator Androida, inne ciężkie programy); przy pełnym swapie model staje.
Na Macu zawsze po kwestii: cały 20-sekundowy fragment w jednym nagraniu urósł do 9,5 GB i stanął (14.11.2026).

resemble-enhance na Windows: `deepspeed` (potrzebny tylko do treningu) nie instaluje się z pip, a plik ustawień
modelu ma ścieżki uniksowe — `lektor_studio.py` obchodzi oba sam (`_resemble_na_windows`).

## Skąd te zasady

| Data | Co usłyszał reżyser | Przyczyna | Zasada |
|---|---|---|---|
| 12.11.2026 | Głos zamulony | Próbka z wiadomości głosowej (16 kHz, 28 kb/s) ucięta na 9 kHz, Chatterbox nad ~11 kHz nic | 1, 3 |
| 12.11.2026 | Pogłos, „nie jak w studiu” | Pogłos pokoju w próbce skopiowany do lektora | 1 |
| 12.11.2026 | Dziwny dźwięk na „Handan” po filtrach | Odszumianie pogłosu na gotowej kwestii (artefakty) | 1 |
| 12.11.2026 | Wybór s7 zamiast s42 | s7 ma oddech po „Handan” i po „Dżeng”, spokojniej | 2, 4 |
| 13.11.2026 | „Musi się śmiać, robić pauzy, emocje — tekst ma być po angielsku” | Multilingual nie czyta znaczników | 7 |
| 14.11.2026 | Między wersjami „nie wiem, który lepszy”; wybór: mocna ekspresja (C), spowolniona o 3 % | Ustawienia mało zmieniają melodię (trzyma się próbki), słychać tempo i akcent | 8 |
| 14.11.2026 | Po „całą” za długa przerwa, po „zakładnik” za krótka; przecinek po samogłosce i co drugie zdanie dłużej; pauzy mają być różne jak u człowieka | Ukryta cisza na końcu pliku kwestii; pauza nie zależała od długości zdania | 8 |
| 16.11.2026 | Wydłużone „Handan” u klona „jak autotune”, u autora naturalnie | Rozciąganie gotowej mowy o 19 % (atempo 0,81) rozmazuje samogłoski | 8 |
| 16.11.2026 | „Dziwne przycięcia w środku słowa albo przy końcu słowa” (EN, 7:21, 7:40, 7:47, 8:03 odsłuchu) | Wstawiane po fakcie oddechy cięły słowa; pauzy ucinały wybrzmienie (0,03 s i cyfrowe zero); obróbka obcinała ciszę na −42 dB, a loudnorm podnosił cięcie o ok. 20 dB; składanie kwestii autora obcinało ciszę drugi raz (−50 dB); Chatterbox urwał ostatnie słowo w 5 z 67 kwestii, resemble-enhance wyciął wybrzmienie w 1 | 9 |
| 18.11 i 20.11.2026 | „Rób jedno podejście… po co 3 podejścia na każde ujęcie? To będzie trwało wieczność” | Trzy podejścia na kwestię to trzy razy dłuższe nagrywanie (na Macu ok. 1–2 min na podejście) | 2 |
| 20.11.2026 („Syn słońca”) | Własne nagranie autora z jazdy autem „nie podoba mi się” → „klonujemy, jak przy pierwszym cesarzu” | Nagranie w ruchu ma zawiechy i nierówne tempo; klon z oczyszczonej próbki brzmi równo | 8 |
| 23.11.2026 („Bonnie and Clyde”) | „Zrób głos mój lektorski w całym filmie tak jak w poprzednich” — 100 kwestii klonem; klon czytał „Hamer” jak „hammer”, a 12 podejść miało urwane albo połknięte słowa | Klon czyta pisownię; Chatterbox czasem urywa koniec | 10, 11, 2 |
