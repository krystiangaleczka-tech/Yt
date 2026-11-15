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
2. **Każda kwestia w trzech podejściach** (ziarna 42, 7, 123). Podejścia różnią się rytmem — gdzie lektor bierze
   oddech, jak prowadzi melodię — a nie barwą.
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
   `aktorskie_en.json` filmu, ten sam sposób (próbka bez pogłosu, 3 podejścia, sucho, wybór z oddechami), próbka
   z angielskiego nagrania autora (`ref_en_studio.wav`). Każde podejście sprawdza Whisper: podejście, w którym nie
   usłyszał tekstu (zgodność < 0,92 — połknięte słowo, powtórka), odpada przy wyborze jak powtórzenie modelu.
8. **Teatr papierowy: zawsze ten sam przepis** („w ten sposób chcę mieć zawsze robiony lektor dla paper theatre”,
   14.11.2026). Nagrywa się z ustawieniami `TEATR` z `docos/lektor_studio.py` (Chatterbox Multilingual:
   exaggeration 1,0, cfg_weight 0,3, temperature 0,7 — mocna ekspresja), dalej trzy podejścia i wybór jak wyżej,
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
   - Mocna ekspresja częściej się powtarza — dlatego zawsze trzy podejścia; podejście z powtórzeniem odpada.
   - Pauzę mierzy się jako ciszę między słowami, nie odstęp między plikami: plik kwestii bywa z ciszą na końcu.
   - Wersja angielska (Turbo) jeszcze bez tego przepisu: Turbo nie ma tych ustawień, a zakresy pauz są pod polski.

## Jak

```bash
# raz na próbkę głosu (środowisko z resemble-enhance: pilot/.venv-enhance, na PC .venv-enhance)
pilot/.venv-enhance/bin/python -I docos/lektor_studio.py probka nagranie.m4a pilot/assets/ref_studio.wav
# kwestie filmu: podejścia, obróbka i wybór (lektor.py sam wywołuje lektor_studio.py podejscia)
pilot/.venv-tts/bin/python -I output/<film>/lektor.py [klucz …]
# po zmianie wybor.json (teatr papierowy: z --teatr, jak lektor.py)
pilot/.venv-enhance/bin/python -I docos/lektor_studio.py podejscia output/<film>/lektor --teatr
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
