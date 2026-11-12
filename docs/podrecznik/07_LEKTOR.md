# Lektor: głos jak z wyciszonego studia

Lektor to klon głosu autora (Chatterbox Multilingual). Ma brzmieć sucho i blisko, jak nagrany w wyciszonym studiu:
bez pogłosu pokoju, bez zamulenia, bez dziwnych dźwięków w nazwach. Narzędzie wspólne dla filmów:
`docos/lektor_studio.py`; skrypt lektora filmu (np. `output/pierwszy-cesarz/lektor.py`) tylko nagrywa podejścia.

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

## Jak

```bash
# raz na próbkę głosu (środowisko z resemble-enhance: pilot/.venv-enhance, na PC .venv-enhance)
pilot/.venv-enhance/bin/python -I docos/lektor_studio.py probka nagranie.m4a pilot/assets/ref_studio.wav
# kwestie filmu: podejścia, obróbka i wybór (lektor.py sam wywołuje lektor_studio.py podejscia)
pilot/.venv-tts/bin/python -I output/<film>/lektor.py [klucz …]
# po zmianie wybor.json
pilot/.venv-enhance/bin/python -I docos/lektor_studio.py podejscia output/<film>/lektor
```

Nagrywanie idzie na PC z kartą NVIDIA (kilka sekund na podejście). Na Macu z 8 GB RAM: ok. 1–2 min na podejście
przez MPS — i tylko przy wolnej pamięci (zamknięty emulator Androida, inne ciężkie programy); przy pełnym swapie
model staje.

## Skąd te zasady

| Data | Co usłyszał reżyser | Przyczyna | Zasada |
|---|---|---|---|
| 12.11.2026 | Głos zamulony | Próbka z wiadomości głosowej (16 kHz, 28 kb/s) ucięta na 9 kHz, Chatterbox nad ~11 kHz nic | 1, 3 |
| 12.11.2026 | Pogłos, „nie jak w studiu” | Pogłos pokoju w próbce skopiowany do lektora | 1 |
| 12.11.2026 | Dziwny dźwięk na „Handan” po filtrach | Odszumianie pogłosu na gotowej kwestii (artefakty) | 1 |
| 12.11.2026 | Wybór s7 zamiast s42 | s7 ma oddech po „Handan” i po „Dżeng”, spokojniej | 2, 4 |
