# DocOS / YT — zasady dla agentów

- Przed tworzeniem albo poprawianiem jakiegokolwiek ujęcia (skrypt renderu, scena Stage w Studio, obraz generowany do
  ujęcia) przeczytaj [docs/WYTYCZNE_UJEC.md](docs/WYTYCZNE_UJEC.md) i przejdź jego kontrolę (sekcja 3) przed oddaniem
  ujęć reżyserowi.
- Do autora pisz po polsku — wszystko, co czyta: odpowiedzi, podsumowania w polu „następny krok”, opisy poleceń,
  pytania i przyciski. Angielski tylko w kodzie i tam, gdzie wymaga go film (np. kwestie lektora wersji EN).
- **Render końcowy robi tylko reżyser.** „Render” w ustach reżysera to końcowe wygenerowanie filmu do wrzucenia na
  YouTube (wersja pełnej jakości, pc\renderuj*.bat) — uruchamia go on w programie, kiedy wszystko w Studio jest
  zrobione i zatwierdzone. Klipy ujęć do Studio to co innego i należą do Twojej pracy (15.11.2026: „dla mnie render
  to jest render, czyli końcowe wygenerowanie filmu”). Teatr papierowy z podglądem na żywo (`output/<film>/na_zywo.py`,
  ujęcia z `legacy.teatr`): Studio rysuje ujęcia z kodu i odświeża je samo po zapisie — klipów mp4 nie rysujesz.
  Film bez podglądu na żywo: zmiana rysunku = narysuj klipy tylko zmienionych ujęć
  (`render.py klipy 3,6,31 <katalog>`, podgląd 720p) i podmień je w Studio (`studio_pc.py --podmien`); zmiana
  długości = stary klip przedłużony stopklatką albo przycięty (`studio_pc.py --aktualizuj --stopklatka`), bez
  rysowania od nowa. Nigdy nie rysuj całego filmu, żeby poprawić kilka ujęć. Jak to robić krok po kroku: Podręcznik,
  „Jak pracujemy” → „Poprawki w Studio i render końcowy”.
- Autor jest reżyserem: ocenia grę i rytm, nie wyłapuje błędów rysunku. Zmiany robi się w Studio (ujęcia i montaż),
  bez eksportu, dopóki o niego nie poprosi.
- Nowy błąd kadru zauważony przez reżysera dopisz do tabeli „Skąd te zasady” w wytycznych i, jeśli to nowa klasa błędu,
  dodaj zasadę.
- Zasady wspólne dla wszystkich filmów są w **Podręczniku pracowni** (`docs/podrecznik/`, w aplikacji: Podręcznik
  pracowni). Przed pracą nad sekwencją, dniem albo ujęciami przeczytaj rozdziały „Jak pracujemy”, „Sekwencja, świat
  i ciągłość” i „Rytm”. Narzędzia i pliki konkretnego filmu są w jego warsztacie (Continuity Editor → Warsztat).
- Ujęcia wynikają ze stanu świata: przed rozpisaniem jednostki (dnia) przeczytaj jej wejście w księdze świata
  (Continuity Editor → Świat), po rozpisaniu dopisz, co zasiewa, zużywa i rozwiązuje, i uruchom kontrolę ciągłości
  (`POST /api/projects/{id}/continuity/check`). Zero błędów wagi 3, zanim cokolwiek zostanie narysowane albo wgrane.
- Zmiana historii idzie od góry: scenariusz i Story Bible → księga świata (decyzja w `decisions`) → rozpiska → ujęcia.
- Po każdej jednostce: recenzja (Continuity Editor → Recenzje, lista z podręcznika) i wpis w dzienniku pracy
  (`POST /api/projects/{id}/flow/log`: co, dlaczego, pliki, wynik kontroli). Zatwierdza reżyser.
- **Przed oddaniem reżyserowi** (film, sekwencja, tura poprawek) przejdź listę „Przed oddaniem reżyserowi” z Podręcznika
  (`docs/podrecznik/01_PRACA.md`) i uruchom `python3 -I scripts/kontrola_filmu.py <film> --studio --podglad` — zero błędów.
  „Jest w Studio” mów dopiero po sprawdzeniu stanu w Studio (oś, lektor, dźwięk, podgląd każdego ujęcia), nie po wyniku
  skryptu wgrywającego. Każdy film ma własne dekoracje i meble (żadnych arkuszy poprzedniego filmu), co najmniej 4 dekoracje
  na 2 minuty, a kwestie nie powtarzają zdań innych filmów (Wytyczne 1.33, reżyser 28.11.2026).
