# DocOS / YT — zasady dla agentów

- Przed tworzeniem albo poprawianiem jakiegokolwiek ujęcia (skrypt renderu, scena Stage w Studio, obraz generowany do
  ujęcia) przeczytaj [docs/WYTYCZNE_UJEC.md](docs/WYTYCZNE_UJEC.md) i przejdź jego kontrolę (sekcja 3) przed oddaniem
  ujęć reżyserowi.
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
