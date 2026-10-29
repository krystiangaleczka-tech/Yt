# DocOS Studio — 26 października 2026

## Zmiana

Dodano lokalną aplikację produkcji dokumentów: React/TypeScript/Vite + FastAPI i rzeczywisty
wielościeżkowy compositor FFmpeg. Gałąź bazuje na generatorze tematów i Story Lock z PR #1;
dotychczasowe CLI i renderery pozostają dostępne.

- Projekty, polski interfejs, zapis rewizji, historia cofania/ponawiania i przykład z lokalnymi ilustracjami.
- Centrum źródeł: Commons, Pixabay, opcjonalny Pexels, Open Library, Google Books, Crossref i własne API JSON.
- Import mediów, stron, PDF/EPUB/TXT/MD, numery stron i rozdziałów, pochodzenie, autor i warunki użycia.
- Pomysł, bank faktów, karta historii, scenariusz oraz propozycje AI przez API, Claude CLI lub przenoszenie promptów.
- Generowanie ujęć: prompt obrazu, zapytanie, upload/schowek, biblioteka, ruch, czas i narracja.
- Osobne procesy obrazów i wielojęzycznego głosu, warianty bez cichej podmiany i pomiar długości nagrania.
- Montaż: warstwy obrazu, tekstu i audio, przesuwanie/przycinanie/podział, duplikowanie, zamykanie luki,
  blokady, wyciszenia, transformacje, prędkość, fades i liniowe keyframes.
- Asystent montażu: walidowane operacje, zakres zaznaczenia, podgląd propozycji i przyjęcie jako jednej zmiany.
- Eksport roboczy/publikacyjny, kontrola braków, ten sam graf dla dokładnego podglądu i MP4, JSON i ZIP z mediami.
- Kolejka SQLite, zdarzenia postępu, anulowanie i oznaczanie przerwanych zadań po restarcie.
- Instrukcja `docs/STUDIO.md`, skrypt instalacji i uruchomienia, przypięte zależności i workflow CI.

## Weryfikacja

Przeprowadzona w Linux x86_64:

- `npm run build`: poprawny TypeScript i build produkcyjny.
- `npm run test:frontend`: **5/5** testów czasu, interpolacji i odwracalnego podglądu propozycji.
- `.venv-studio/bin/python -m unittest discover -s studio_tests -v`: **33/33**.
- `python -m unittest discover -s docos/tests -v`: **18/18**, łącznie z eksportem/importem XLSX.
- Rzeczywiste FFmpeg: sekwencja zdjęć, nakładka, napis, keyframes, dźwięk AAC, kontrola klatek i długości MP4.
- Pełny test API: upload → ujęcie → montaż → zadanie renderu → pobranie MP4.
- PDF i EPUB z lokalizacją tekstu; pakiet ZIP z weryfikacją sum; odmowa nadpisania przy starej rewizji;
  blokady i zakres AI; brak kluczy w eksporcie; anulowanie i trwały stan kolejki.
- Poprawiono wyścig anulowania: spóźniony CANCEL_REQUESTED nie może nadpisać terminalnego statusu zadania.
- `git diff --check`: bez błędów.

## Zakres sprawdzenia

Podgląd Sites nie uruchomił serwera Python z powodu braku jego zależności w środowisku podglądu.
Pełna kontrola w przeglądarce, wygląd na telefonie i gesty wymagają sprawdzenia na docelowym komputerze.
Nie instalowano ani nie uruchamiano dużych modeli ML, GPU lub rzeczywistych kont dostawców stocków/AI.
Testy adapterów korzystają z kontrolowanych odpowiedzi. Nie deklarujemy pomiarów wydajności długich filmów.

Nie jest to realizacja wszystkich sześćdziesięciu zadań planu ani pełna zgodność funkcji z CapCut.
Granice i dalsze rozszerzenia są wymienione w `docs/STUDIO.md`; główne moduły są połączone z rzeczywistym API i eksportem.
