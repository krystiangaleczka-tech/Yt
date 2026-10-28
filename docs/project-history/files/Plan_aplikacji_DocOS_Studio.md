# DocOS Studio — plan aplikacji do tworzenia filmów

Data: 26 października 2026. Wersja planu: **2 — źródła, generowanie filmu i osobny montaż wielościeżkowy**.
Status: propozycja produktu i plan wdrożenia, bez zmian w aplikacji.

## 1. Decyzja produktowa

Zbudować lokalne studio produkcji narracyjnych filmów dokumentalnych: od pomysłu, przez źródła i scenariusz,
do głosu, obrazu i gotowego pliku. Nazwa robocza: **DocOS Studio**.

Interfejs działa w przeglądarce, a przetwarzanie mediów i głosu wykonuje lokalny silnik Python.
Pierwszym sprawdzanym środowiskiem powinien być macOS Apple Silicon, ponieważ pod niego napisano i opisano
obecny pipeline. Architektura ma umożliwić osobno testowane wydanie Windows z NVIDIA.
Docelowy system użytkownika trzeba potwierdzić przed wyborem pierwszego instalatora.

Użytkownik pracuje na treści i podglądzie filmu. Zamiast wpisywać `FILE:`, `START:` czy `ZOOM:` wybiera
materiał, przeciąga zakres klipu i zaznacza kadr myszą. Pola techniczne pozostają w widoku zaawansowanym.

Przewaga produktu: **jedno miejsce łączące narrację, dowody, materiały i montaż**. Każdy element obrazu
lub głosu ma przypisaną wersję treści, źródła i stan gotowości.

Trzy odrębne obszary produkcyjne: **Źródła**, **Generowanie filmu**, **Montaż**.
Źródła dostarczają informacji i materiałów. Generowanie przygotowuje konkretne ujęcia wraz z narracją
i czasem. Montaż pozwala użytkownikowi lub AI układać je w film na wspólnej osi czasu.

## 2. Zakres przeglądu repozytorium

Przejrzano wszystkie 64 pliki z `main`: 61 tekstowych oraz trzy binarne fonty, których strukturę,
nazwy, wersje i informacje licencyjne odczytano z tabel TTF. Uwzględniono też wszystkie dziesięć zmienionych
lub dodanych plików PR #1. Łącznie objęto przeglądem 74 wersje plików; drzewo PR zawiera 68 plików.

- `main`: commit `c27da6c1f9400ad8494f84784139d07456ef16ee`.
- PR #1: commit `2964df4bc9935329dab537c382ffed2599e667fd`, nadal otwarty w chwili przeglądu.
- PR dodaje tematy, profil Documentary i Story Lock; plan traktuje je jako zależność do scalenia albo
  przeniesienia do przyszłej gałęzi aplikacji, a nie funkcje już obecne na `main`.
- Odcinek wskazany przez dokumentację jako bieżący to `projekty/bloop_v3/bloop_v4.json`:
  **12 beatów, 53 ujęcia, 22 pozycje rejestru faktów, 546 słów narracji**.
- Rejestry mediów mają 33 pozycje w `raw/commons/licenses.json` i 15 w `raw/video/licenses.json`.
  Są to pozycje rejestrów, nie liczba unikalnych materiałów wykorzystanych w filmie.
- Kontrola obecnego projektu zwraca zero uwag. Starszy projekt v3 zwraca 14 uwag, a przykład w `docos/examples` sześć.
  To wyniki istniejących reguł, nie potwierdzenie prawdziwości faktów ani jakości gotowego filmu.

Pobrano i przeanalizowano kod, dane projektów, 24 pliki beatów, dokumentację, zależności i licencje.
Nie odtwarzano kilku gigabajtów mediów ani nie uruchamiano modeli TTS/SD i pełnego renderu.
Dlatego wydajność nowej aplikacji pozostaje celem do pomiaru, a nie wynikiem tego przeglądu.

## 3. Co wykorzystujemy, a co wymaga przebudowy

| Obszar | Istniejący fundament | Plan |
|---|---|---|
| Scenariusz | `docos.py`: struktura, prompty, fakty, kontrola, eksport | Wydzielić funkcje domenowe i udostępnić przez wspólną warstwę usług |
| Tematy i historia | `editorial.py` z PR #1 | Dodać formularze, historię zmian i ekran zatwierdzania |
| Montaż | `render_doc.py`, część narzędzi `render_film.py` | Zachować szablony; dodać model osi czasu i compositor dla nakładających się warstw |
| Głos | `voice_beats.py`: zdania, dogrywki, tempo | Dodać profile głosu, poprawny cache i sterowanie z interfejsu |
| Media | `fetch_commons.py`, rejestry licencji | Zbudować katalog, import, pobieranie, powiązania i naprawianie ścieżek |
| Źródła zewnętrzne | Commons i źródła faktów zapisane w projektach | Wspólny interfejs integracji zdjęć, stocków, książek, informacji i źródeł własnych |
| Generowanie ujęć | `make_assets.py`, plan renderu i istniejące animacje | Osobny dział z promptem/zleceniem wyszukania, wklejeniem medium, narracją i czasem ujęcia |
| Edytor | `editor.py` + `editor.html` | Wykorzystać zachowania i API jako materiał do migracji; zbudować nową warstwę aplikacji i interfejs |
| Projekty | JSON i eksport/import XLSX | Zachować przenośny format, dodać wersjonowanie i bezpieczne zapisy |
| Pilot | Skrypty demonstracyjne | Zachować jako przykłady i materiał do testów, nie jako warstwę produkcyjną aplikacji |

### Ustalenia techniczne wpływające na plan

| Ustalenie z kodu | Skutek dla projektu aplikacji |
|---|---|
| Edytor otwiera jeden plik projektu przekazany przy uruchomieniu | Potrzebne zarządzanie kanałami i wieloma odcinkami |
| `App.save()` zapisuje cały dokument i pojedynczy backup, bez numeru rewizji | Zapis atomowy, kontrola konfliktów, autosave i historia wersji |
| `App.save()` i bezpośredni renderer nie egzekwują całego nowego kontraktu Story Lock | Reguły zatwierdzania muszą działać we wspólnej usłudze dla GUI, CLI i zadań |
| Stan zadania istnieje jako pojedynczy słownik w pamięci procesu | Trwała kolejka, identyfikatory zadań, odtwarzanie stanu po restarcie |
| `start_voice()` przekazuje `--lang en` i ma ścieżki typowe dla macOS | Język z projektu, profile środowisk i wykrywanie możliwości sprzętu |
| Skrypty TTS i SD wybierają MPS lub CPU; nie mają gałęzi CUDA | Obsługę NVIDIA trzeba zaimplementować i przetestować, mimo szerszej deklaracji w dokumentacji |
| Cache zdania uwzględnia treść i beat, ale nie profil głosu, język ani ustawienia modelu | Klucz cache musi opisywać wszystkie wejścia mające wpływ na dźwięk |
| `seg_key()` nie obejmuje rozszerzenia `.mp4` w zbieraniu użytych plików | Zastąpić wyszukiwanie rozszerzeń jawną listą powiązanych assetów |
| Klucz napisów końcowych opiera się m.in. na liczbie dodatkowych linii, nie ich pełnej treści | Zmiana autora lub licencji musi unieważniać odpowiedni wynik renderu |
| Część podprocesów ignoruje kod zakończenia lub nie sprawdza pliku wynikowego | Sukces zadania wymaga poprawnego kodu wyjścia i walidacji artefaktu |
| Media są indeksowane po samej nazwie pliku | Stałe identyfikatory assetów i wykrywanie kolizji nazw |
| Opis ujęcia łączy tekst z parametrami sterującymi | Typowane parametry ujęcia i adapter zgodności ze starymi opisami |
| Mapy i diagram SOFAR zawierają konkretne dane oraz angielskie napisy | Katalog parametryzowanych szablonów i lokalizowane etykiety |
| Obraz jest renderowany w stałym układzie 1920×1080, a wideo ma wymuszone odbarwienie | Konfiguracja kadru i wyglądu; pionowy film wymaga pracy nad kompozycją |
| Podgląd jest skalowany do 360p po obliczeniu klatek w pełnym rozmiarze | Osobny, rzeczywiście lekki tryb podglądu do zmierzenia na sprzęcie |
| W bieżącym projekcie `raw` zawiera wcześniejsze shot listy wszystkich 12 beatów | Pole `raw` zachować jako historię pochodzenia; bieżące `shots` są nadrzędne |
| Diagramy i podpisy mogą zawierać informacje spoza faktów przypisanych do narracji beatu | Powiązania źródeł muszą obejmować również twierdzenia na ekranie |

## 4. Organizacja aplikacji

Nawigacja globalna: **Projekty**, **Źródła**, **Biblioteka**, **Zadania**.
Źródła służą do podłączania dostawców i repozytoriów treści, a Biblioteka przechowuje już wybrane,
pozyskane lub wygenerowane materiały. Wybór kanału i ustawienia są dostępne w belce aplikacji.
Otwarty odcinek ma siedem etapów:

**Pomysł → Fakty → Historia → Scenariusz → Generowanie → Montaż → Eksport**.

Przejścia między etapami są dostępne przez cały czas. Aplikacja informuje, co jest gotowe do produkcji,
a co pozostaje szkicem. Braki nie blokują przeglądania i planowania; blokady dotyczą operacji wymagających
zatwierdzonej treści lub kompletnych plików.

| Etap | Główny widok | Najważniejsza czynność |
|---|---|---|
| Pomysł | Karty tematów, profil kanału, lista użytych tytułów | Wybrać temat lub wpisać własny |
| Fakty | Lista twierdzeń z panelem źródła i miejscami użycia | Sprawdzić i oznaczyć fakty do historii |
| Historia | Czytelna karta pytania, hooka, komplikacji i odpowiedzi | Zatwierdzić wersję Story Lock |
| Scenariusz | Rozdziały i beaty oraz edytor narracji | Napisać lub poprawić fragment z zachowaniem źródeł |
| Generowanie | Plan ujęć z promptami, wyszukiwaniem, materiałami i narracją | Pozyskać lub wygenerować obraz dla określonego czasu |
| Montaż | Wielościeżkowa oś czasu, podgląd, efekty i asystent AI | Ręcznie lub poleceniami AI zmontować gotowy film |
| Eksport | Lista braków i ustawienia pliku wynikowego | Przygotować zatwierdzoną wersję filmu |

### Widok projektów

Karta odcinka pokazuje tytuł, miniaturę, kanał, datę ostatniej zmiany i konkretny następny krok,
np. „Wybierz materiał do trzech ujęć”. Status wynika z istniejących danych, a nie z arbitralnego procentu jakości.
Można utworzyć odcinek, otworzyć istniejący JSON, skopiować projekt lub wrócić do ostatnio edytowanego miejsca.

### Centrum źródeł — zdjęcia, książki, stocki i informacje

Każde połączenie ma własne ustawienia, stan dostępności, rodzaje obsługiwanych treści i sposób dodawania
wyników do projektu. Można szukać w wybranym źródle albo w kilku podłączonych naraz.
Wyniki są pogrupowane jako zdjęcia, filmy, książki, dokumenty, informacje i własne materiały.

| Rodzaj | Proponowane połączenia | Wynik |
|---|---|---|
| Zdjęcia i archiwalia | Wikimedia Commons, wybrane archiwa, własne zbiory i dostawcy stocków | Podgląd, rozmiar, autor, pochodzenie, opis i warunki użycia |
| Filmy stockowe | Pixabay; Pexels przy dostępnym kluczu; inni dostawcy przez adaptery | Podgląd klipu, czas, rozdzielczość, orientacja, warianty i przypisanie do sceny |
| Książki i publikacje | Google Books, Open Library, własne PDF/EPUB i biblioteki cyfrowe | Konkretne wydanie, autor, rok, ISBN, okładka i dostępne fragmenty lub pełny tekst |
| Informacje i badania | Strony, artykuły, raporty instytucji, RSS, DOI/Crossref | Dostępna treść, metadane, cytowany fragment i odnośnik do oryginału |
| Custom źródła | Folder, ręcznie dodany plik/link, własne API/JSON lub adapter | Materiały i informacje w tym samym katalogu i formacie wyników |
| Generatory | Lokalny generator obrazu oraz opcjonalne zewnętrzne adaptery | Obrazy/wideo zgodne z możliwościami podłączonego silnika |

Integracje są modułowe: pojedynczy dostawca nie warunkuje działania całego studia. Commons i import własny
korzystają z istniejącego procesu. Dokumentacja Pixabay opisuje API obrazów i filmów; trzeba obsłużyć klucz,
limity, cache odpowiedzi i zasady pobierania [S8]. Pexels ma API zdjęć i filmów, lecz 26 października 2026
jego oficjalna strona informuje o wstrzymaniu wydawania nowych kluczy. Automatyczna integracja Pexels
jest więc warunkowa; pozostaje możliwość ręcznego importu [S9].

Karta wyniku pokazuje odpowiednie akcje: „Podejrzyj”, „Dodaj jako źródło”, „Użyj w ujęciu”, „Pobierz”
albo „Otwórz u dostawcy”. Widać autora, miejsce/czas wykonania, licencję, ewentualny koszt, rozmiar
i wcześniejsze użycia. Podłączenie nie oznacza automatycznie dostępności pełnego tekstu czy pobierania.

W książkach rozróżniamy rekord katalogowy, podgląd i plik z treścią. Google Books podaje dostępność treści,
a Open Library rozróżnia dzieło i wydania [S10, S11]. Cytat zapisuje konkretne wydanie i stronę lub lokalizację EPUB.
Skan może przejść OCR, ale autor nadal widzi oryginalną stronę. Ilustracja z książki ma osobno przypisane
pochodzenie i informację o prawach do obrazu.

Źródło może być dowodem, materiałem do pokazania lub pełnić obie role. Znaleziony opis książki albo DOI
nie jest przeczytanym pełnym tekstem. Crossref dostarcza metadane publikacji; pełna treść jest osobnym zasobem [S12].
Ogólne wyszukiwanie internetu działa przez wybranego dostawcę wyszukiwania. Ręczny link i własny dokument
pozwalają pracować także bez takiego połączenia.

„Dodaj źródło” pozwala wskazać folder/link albo skonfigurować połączenie. Zaawansowane ustawienia własnego API
opisują mapowanie wyników, paginację i uwierzytelnianie. Poświadczenia pozostają poza eksportem projektu
i promptami AI. Połączenie można przetestować bez pobierania całej biblioteki.

### Fakty i źródła dowodowe

Po zaznaczeniu twierdzenia widać źródło, URL, datę sprawdzenia, notatkę, ewentualny spór oraz powiązane beaty
i ujęcia. Statusy po polsku: „Sprawdzony”, „Sporny”, „Do sprawdzenia”, „Rekonstrukcja”. Ostatni status opisuje
charakter produkcji, nie dowód faktograficzny.

Nowy materiał z internetu trafia jako kandydat do sprawdzenia. Oznaczenie „Sprawdzony” wymaga decyzji autora
i wskazania źródła. Dopasowanie wypowiedzi do dowodu oraz audyt cytatów mają pokazywać uzasadnienie,
nie etykietę sugerującą nieomylność AI.

### Historia

Story Lock jest kartą redakcyjną z pytaniem filmu, obietnicą tytułu, hookiem, tezą, komplikacją, payoffem,
powracającym szczegółem i bankiem dowodów. Sekcje można składać; podstawowa karta pokazuje najpierw pięć
najważniejszych odpowiedzi. Zatwierdzenie zapisuje wersję oraz autora decyzji.

Zmiana istotnego założenia otwiera nową rewizję. Aplikacja pokazuje różnice i elementy wymagające ponownego
sprawdzenia. Praca nad wariantem nie kasuje zatwierdzonej wersji filmu.

### Scenariusz

Lewy panel pokazuje rozdziały i krótkie fragmenty historii. Środek służy do pisania narracji; panel boczny
pokazuje przypisane fakty, cel fragmentu i jego miejsce w historii. Dostępny jest też widok całego tekstu.

Polecenia AI są kontekstowe: „Napisz fragment”, „Skróć”, „Wyjaśnij prościej”, „Wzmocnij początek”,
„Zaproponuj zakończenie”. Każda propozycja jest porównywana z obecną treścią przed przyjęciem.
Istniejące pojęcia energia, Turn, typologia i chaos trafiają do szczegółów, z prostymi objaśnieniami.

### Generowanie filmu — osobny dział przygotowania ujęć

Każda karta ujęcia jest powiązana ze sceną, fragmentem narracji i zakresem czasu filmu. Tryby przygotowania:
**Generuj**, **Znajdź w internecie/źródłach**, **Wklej lub prześlij**, **Weź z biblioteki**.
Zmiana sposobu nie usuwa wcześniejszych wariantów.

Na dużym ekranie **po lewej znajduje się panel przygotowania ujęcia**: prompt dla zdjęcia/wideo lub opis
materiału do znalezienia, źródła, referencje i pole wklejania. Pośrodku jest duży podgląd i warianty wyników.
Właściwości obejmują metodę ujęcia/animacji i czas. Poniżej znajduje się plan wszystkich ujęć z narracją.

| Pole karty / planu | Zachowanie |
|---|---|
| Timestamp początku i końca | Zakres w filmie i czas trwania: plan przed nagraniem, potem możliwość dopasowania do głosu |
| Narracja dla timestampu | Dokładny fragment tekstu i odsłuch; możliwość dzielenia lub łączenia jednostek narracji |
| Prompt generowania | Edytowalny opis obrazu/wideo; osobno referencje, model i szczegóły po rozwinięciu |
| Materiał do pozyskania | Fraza wyszukania/opis zlecenia, rodzaj treści, preferowane źródła, miejsce i epoka |
| Obrazek/film do wklejenia | Ctrl/Cmd+V dla obsługiwanego schowka, przeciągnięcie pliku, import i wklejenie URL |
| Wybrany obraz lub film | Podgląd, źródło, autor, wariant i zakres materiału źródłowego; możliwość zamiany |
| Metoda ujęcia/animacji | Najazd, oddalenie, panoramowanie, statyczny kadr, lupa, parallax, plansza lub keyframes |
| Stan | Do znalezienia, w kolejce, gotowy wariant, wybrany, zablokowany, nieaktualny albo błąd |

Wklejenie URL może prowadzić do pliku albo strony źródłowej; aplikacja pokazuje, jaki import obsługuje.
Film można przesłać jako plik lub przez wspierane połączenie. Nie zakładamy, że każdy system ma w schowku
binarny plik wideo.

Opis poszukiwanego kadru zostaje przy ujęciu z internetu. Prompt i parametry zostają przy ujęciu generowanym.
Prompt obrazu, prompt ruchu i zapytanie wyszukiwarki są osobnymi polami. Generowanie wideo AI pojawia się
po podłączeniu odpowiedniego silnika; obecny generator obrazów SD nie jest automatycznie generatorem wideo.

Podstawowy katalog sposobów prezentacji:

Przykłady:

- Zdjęcie: wybór pliku, punkt skupienia, początek i koniec najazdu, podpis.
- Klip: zaznaczenie początku i końca, podgląd odcinka, dopasowanie do narracji.
- Lupa: narysowanie prostokąta na zdjęciu, regulacja czasu zbliżenia.
- Cytat/prasa: tekst, autor, publikacja, data i powiązany fakt.
- Licznik: wartość, jednostka, podpis i źródło liczby.
- Spektrogram: nagranie, zakres czasu, częstotliwości i podpis pochodzenia.
- Mapa: wybrany obszar, punkty i trasy z danych geograficznych, etykiety i źródło.

Presety ruchu mają podgląd, intensywność i punkty początku/końca. Parallax wymaga przygotowania warstw lub maski.
Dla sceny można wykonać warianty i wybrać najlepszy. Kolejka przygotowuje wskazane ujęcie, scenę lub zestaw braków,
respektując ograniczenia dostawców. „Dodaj do montażu” umieszcza wybrane wersje na osi czasu z zachowaniem ID,
promptu i pochodzenia. Ponowna generacja tworzy propozycję zamiany, nie nadpisuje ręcznej edycji.

### Montaż — osobna zakładka w stylu pracy CapCut

Biblioteka plików znajduje się po lewej, duży odtwarzacz pośrodku, inspektor po prawej, a wielościeżkowa
oś czasu na dole. Obok można wysunąć panel asystenta AI. Interfejs ma własną identyfikację wizualną.

| Obszar | Funkcje |
|---|---|
| Obraz | Wiele ścieżek zdjęć/filmów, nakładki, skala, położenie, obrót, przezroczystość i kadrowanie |
| Tekst i grafiki | Napisy, tytuły, podpisy, cytaty, mapy i diagramy jako edytowalne elementy |
| Audio | Ścieżki lektora, muzyki, efektów i nagrań źródłowych; fale, wyciszenie i solo |
| Edycja klipów | Przeciąganie, podział, przycinanie, usuwanie, ripple, przyciąganie, luki, grupowanie i blokady |
| Animacja | Presety i keyframes położenia, skali, obrotu, przezroczystości i głośności |
| Przejścia i tempo | Katalog przejść, długość przejścia, zmiana prędkości i dopasowanie do narracji |
| Kontrola | Cofanie/ponawianie, wersje montażu, podgląd zakresu i porównanie wariantów |

Jedna scena może mieć wiele klipów i warstw. Przesunięcie klipu aktualizuje zakres pokazywany w Generowaniu.
Przy konflikcie z zablokowaną narracją można przesunąć obraz, dopasować tempo albo zmienić plan.

**Użytkownik i AI korzystają z tych samych operacji edycji.** Przykładowe polecenia:

- „Zrób dynamiczniejsze pierwsze dwadzieścia sekund. Zachowaj narrację”.
- „Od trzydziestej piątej do pięćdziesiątej sekundy zastąp plansze filmami archiwalnymi”.
- „Przy słowie lód przejdź na górę lodową, a pod nagraniem źródłowym wycisz muzykę”.
- „Zostaw zaznaczone ujęcie i jego długość. Popraw pozostałe przebitki w tej scenie”.

Tryb propozycji pokazuje podgląd i różnice przed przyjęciem zmian. Tryb automatyczny stosuje odwracalne
zmiany w wcześniej wybranym zakresie i respektuje blokady. Seria zmian jest jedną operacją w historii:
można ją cofnąć i kontynuować ręcznie. Zmiana narracji lub założeń historii wymaga właściwej rewizji treści.

Podgląd ma trzy poziomy: natychmiastowa kompozycja orientacyjna, dokładna klatka z renderera i wyrenderowany
podgląd wybranego fragmentu. Interfejs wyraźnie rozróżnia podgląd orientacyjny od wyniku finalnego silnika.

### Lektor i dźwięk

W Generowaniu sekcja Lektor pokazuje tekst podzielony na zdania, odsłuch, wersje nagrań i słownik wymowy.
Można poprawić jedno zdanie, odsłuchać warianty i wybrać najlepszy. Ustawienia modelu są dostępne po rozwinięciu.

Zmiana profilu głosu, języka lub modelu oznacza nagrania jako wymagające aktualizacji. Zmiana jednego zdania
nie uruchamia automatycznie całego filmu. Profile przechowują odnośnik do lokalnej próbki; same próbki nie trafiają
do zwykłego eksportu projektu.

W Montażu dźwięk ma czytelne ścieżki lektora, podkładu oraz efektów/nagrań archiwalnych. Suwaki kontrolują głośność,
przyciszenie pod lektorem i wyciszenia. Parametry obecnych `cues`, `lead`, `tail` i `silence_before` otrzymują
formularze oraz uchwyty na osi czasu.

### Dodatkowe propozycje

- **Plan przebitek z narracji:** propozycje, czego szukać dla kolejnych zdań, oraz mapa pokrycia obrazu.
- **Blokady twórcze:** „zachowaj głos”, „zachowaj czas”, „zachowaj wybrany obraz”, „nie generuj ponownie”.
- **Styl kanału:** referencje, kolory, fonty, rodzaj ruchu i reguły montażu wspólne dla odcinków.
- **Dosłownie / ilustracyjnie / rekonstrukcja:** określenie roli kadru i czytelne oznaczenia.
- **Lista braków:** sceny czekające na źródło, obraz, film, głos lub wybór wariantu.
- **Wersje A/B:** porównanie dwóch montaży otwarcia z tych samych materiałów.
- **Budżet produkcji:** szacunek czasu i kosztu generacji, ponowne użycie materiałów i limit automatycznego działania.
- **Ścieżka pochodzenia:** od klipu do promptu, materiału źródłowego, faktu lub konkretnej strony książki.

## 5. Wygląd i zasady intuicyjności

Kierunek: spokojne studio montażowe z dużym podglądem obrazu, czytelnym tekstem i oszczędnym akcentem koloru.
Domyślny motyw grafitowy; opcjonalny jasny. Tło grafitowe, nieco jaśniejsze panele, subtelne separatory,
bursztynowy akcent akcji i osobne kolory semantyczne komunikatów.

Proponowane tokeny ciemnego motywu: tło `#101318`, panel `#181D25`, separator `#2B3442`,
tekst `#EDF1F7`, tekst pomocniczy `#AAB4C4`, akcent `#F2B866` z ciemnym tekstem przycisku.
Finalne pary kolorów wymagają pomiaru kontrastu.

- Systemowy krój sans serif i tekst podstawowy 14–16 px. Courier Prime dla identyfikatorów i oznaczeń czasu.
- Regularny rytm odstępów 4/8 px, umiarkowanie zaokrąglone narożniki, widoczny fokus klawiatury.
- Jedna dominująca czynność w aktualnym kontekście; etykiety opisują rezultat: „Wygeneruj podgląd fragmentu”.
- Ustawienia szczegółowe pojawiają się po zaznaczeniu elementu lub rozwinięciu „Zaawansowane”.
- Autosave z jednoznacznym stanem: zapisywanie, zapisano, konflikt albo błąd.
- Cofanie i ponawianie działa na zmianach treści, ujęć i dźwięku. Operacje generowania tworzą wersje wyników.
- Błędy są przy właściwym polu i prowadzą do elementu wymagającego poprawy.
- Status jest opisany tekstem i ikoną; kolor jest dodatkową informacją.
- Przeciąganie ma odpowiednik klawiaturowy i przyciski przesuwania.
- Na mniejszych ekranach inspektor wysuwa się jako panel, a podgląd może zostać powiększony.
- Telefon służy najpierw do przeglądania, odsłuchu i zatwierdzania; precyzyjny montaż pozostaje zadaniem interfejsu komputerowego.

## 6. Model pracy i aktualność wyników

Każdy artefakt ma wersję wejścia oraz status: brak, w kolejce, aktualny, nieaktualny albo błąd.
Aplikacja pokazuje przyczynę, np. „Nagranie powstało dla poprzedniej wersji zdania”.

| Zmiana | Co wymaga aktualizacji |
|---|---|
| Literówka w jednym zdaniu | To zdanie; następnie czas i miks odpowiedniego beatu |
| Inny głos lub język | Powiązane nagrania dla tego profilu i dalsze zależne wyniki |
| Inny obraz ujęcia | Miniatura i segment wykorzystujący obraz; ewentualnie następny segment korzystający z jego tła |
| Ten sam plik MP4 podmieniony na inną treść | Wszystkie wyniki zależne od jego identyfikatora i skrótu zawartości |
| Zmiana źródła lub faktu | Ocena aktualności Story Lock i powiązanych twierdzeń narracji/obrazu |
| Zmiana autora/licencji materiału | Napisy końcowe i opis filmu |
| Skrócenie głosu | Układ czasowy zależnych ujęć, miks i potrzebne segmenty |
| Przesunięcie klipu w Montażu | Timestampy powiązanego ujęcia w Generowaniu oraz zależne zakresy renderu |
| Nowy wariant wygenerowanego obrazu | Propozycja zastąpienia klipu z zachowaniem jego czasu i animacji, o ile użytkownik tak wybierze |
| Inne wydanie książki lub aktualizacja dokumentu | Ponowna ocena powiązanych cytatów i stron; bez cichej zamiany dowodu |

Rozróżniamy unieważnienie zatwierdzenia, potrzebę ponownej oceny treści i potrzebę ponownego przeliczenia.
Zmiana faktu nie oznacza, że AI może samodzielnie przepisać zatwierdzony scenariusz.

Zadania uruchamiają się z niezmiennej migawki. Jeśli projekt zmieni się podczas renderu, gotowy plik pozostaje
wynikiem wcześniejszej rewizji i jest tak oznaczony. Nie udaje aktualnego podglądu.
Użyte media są identyfikowane skrótem zawartości i zachowywane jako niezmienne wersje. Sama kopia JSON
nie wystarczy, jeśli wskazany plik zostanie podmieniony w trakcie obliczeń.

## 7. Proponowana architektura

| Warstwa | Wybór | Uzasadnienie |
|---|---|---|
| Interfejs | React + TypeScript + Vite | Osobne Źródła, Generowanie i Montaż; wspólny model zaznaczenia oraz zmian |
| Komponenty | Radix Primitives + własne tokeny i CSS Modules | Spójny wygląd oraz fundament obsługi klawiatury i fokusu |
| API | Python + FastAPI + Pydantic | Wspólny kontrakt danych i bezpośrednie wykorzystanie obecnych silników |
| Zdarzenia | SSE z identyfikatorem zdarzenia | Postęp zadań i odtwarzanie komunikatów po ponownym połączeniu |
| Dane projektu | Wersjonowany JSON | Czytelność, zgodność z dotychczasowym procesem i przenoszenie projektów |
| Katalog i zadania | Lokalny SQLite | Katalog projektów, indeksy i trwały stan kolejki |
| Przetwarzanie | Osobne procesy robocze Pythona i FFmpeg | Responsywny interfejs, kontrola zasobów, odseparowane środowiska modeli |
| Kompozycja filmu | Timeline/RenderGraph oraz adapter renderera | Wiele jednoczesnych warstw, keyframes, przejścia i spójność podglądu z eksportem |
| Opakowanie desktopowe później | Tauri z procesem pomocniczym | Możliwość uruchamiania tego samego studia z ikony |

To rekomendacja architektoniczna wynikająca z repozytorium, nie istniejący stos projektu.
Wersje zależności należy przypiąć po krótkim teście uruchomienia na docelowym komputerze.
Vite udostępnia szablon React/TypeScript; Radix opisuje mechanizmy dostępności swoich komponentów [S1, S2].
Ciężkie generowanie i render trafiają do procesów roboczych; dokumentacja FastAPI rozróżnia takie zadania
od prostych operacji wykonywanych przez `BackgroundTasks` [S3].

### Przepływ wewnętrzny

GUI i CLI wywołują ten sam `ProjectService`. Usługa sprawdza rewizję i reguły redakcyjne,
zapisuje zmianę lub tworzy zadanie. Worker otrzymuje migawkę, uruchamia adapter silnika,
publikuje postęp i rejestruje wynik. UI odbiera zdarzenia i pokazuje aktualność wyniku.

Proponowane moduły w repo:

| Katalog | Odpowiedzialność |
|---|---|
| `apps/studio/` | Interfejs React |
| `studio_api/` | Endpointy, walidacja żądań, zdarzenia |
| `studio_core/` | Projekty, rewizje, źródła, Story Lock, ujęcia, reguły |
| `studio_workers/` | Kolejka, adaptery renderu, głosu i pobierania |
| `studio_connectors/` | Integracje źródeł, normalizacja wyników, limity i dostępność treści |
| `studio_timeline/` | Model montażu, operacje edycji, plan kompozycji i walidacja zmian AI |
| `docos/` | Zachowany CLI i istniejące silniki stopniowo korzystające z nowych usług |
| `tests/fixtures/` | Kopie referencyjnych danych i małe media testowe |

### Źródła prawdy i zgodność

- `project.json` pozostaje źródłem prawdy dla treści odcinka: metadanych, faktów, historii, narracji i ujęć.
- Manifest assetów przechowuje metadane materiałów, ich pochodzenie i licencje. Projekt odwołuje się do stałych ID.
- SQLite przechowuje trwały stan zadań i katalog. Indeks treści projektu i assetów można odbudować z plików.
- Baza nie staje się drugą niezależnie edytowaną kopią scenariusza.
- Kanał ma wersjonowany profil, a odcinek zachowuje jego migawkę.

Nowy format dodaje `schema_version`, `project_id`, `revision`, stałe `shot_id` oraz typowane parametry.
Projekt zawiera plan scen i ujęć oraz odrębną sekwencję montażową. Wygenerowane medium jest assetem,
a każde jego wystąpienie na osi czasu ma własny `clip_id`. Powtórzenie zdjęcia nie duplikuje jego źródła.
Identyfikatory `B01`/`F1` mogą pozostać czytelnymi oznaczeniami w istniejących projektach.
Stary opis jest zachowany jako `legacy_desc`; adapter tworzy wejście dla obecnego renderera.
Nieznane pola importu przechowujemy, zamiast je usuwać. Eksport do starszej wersji zgłasza funkcje,
których starszy format nie potrafi zapisać.
Starszemu odcinkowi nie dopisujemy automatycznie zatwierdzonego Story Lock. Migracja może zaproponować kartę,
ale wymaga jej sprawdzenia. Dawne wpisy DRAMATIZATION zachowujemy jako oznaczenia produkcyjne,
a nie dodajemy ich do banku dowodów narracji.

### Kontrakt źródeł i planu produkcji

| Obiekt | Odpowiedzialność |
|---|---|
| SourceConnection | Dostawca/folder/API, zakres możliwości, połączenie i referencja do poświadczeń |
| SourceDocument | Autor, wydanie, URL/DOI/ISBN, fragment, lokalizacja strony i stan sprawdzenia |
| MediaAsset | Niezmienna wersja medium, plik, format, autor, pochodzenie i warunki wykorzystania |
| ScenePlan / ShotPlan | Narracja, planowany czas, prompt obrazu/ruchu, zapytanie wyszukania, wybrany wariant i animacja |
| GenerationRequest | Model/dostawca, pełne wejście, referencje, parametry, koszt i wyniki jako wersje assetów |
| Sequence / Track / Clip | Montaż: warstwy, pozycje, długości, źródłowe in/out, prędkość, grupy i blokady |
| Keyframe | Wartość parametru w określonym czasie i sposób interpolacji |
| EditBatch | Zestaw ręcznych lub AI operacji na konkretnej rewizji z możliwością cofnięcia |

Adapter podaje możliwości źródła: wyszukanie, podgląd, pobranie, odczyt tekstu, pobranie okładki,
generowanie obrazu lub wideo. UI pokazuje akcje, które są obsługiwane. Wynik katalogowy, fragment tekstu
i faktycznie pobrany plik mają odrębne stany, choć mogą być powiązane jednym rekordem pochodzenia.

Zapytania zewnętrzne przechodzą przez backend. Własny adapter ma jawnie skonfigurowane hosty i mapowanie danych;
linki z wyników nie stają się uprawnieniem do wysyłania poświadczeń innemu hostowi.
Treści do analizy można ograniczyć do zaznaczonego fragmentu zamiast wysyłać całą książkę do modelu.

### Rzeczywisty silnik montażu

Obecny renderer skaluje ujęcia kolejno w ramach beatów. Nakładki, równoległe ścieżki i niezależne klipy
wymagają dodatkowego modelu kompozycji. RenderGraph opisuje kolejność warstw, transformacje, tekst,
przejścia i miks. Adapter wykorzystuje FFmpeg oraz obecne szablony Python; test prototypowy sprawdza
wierność i wydajność na kilku warstwach przed podjęciem dalszych decyzji implementacyjnych.
Dokumentacja filtrów FFmpeg stanowi punkt wyjścia do kompozycji; dostępne funkcje trzeba sprawdzić
również w wersji zainstalowanej na docelowym komputerze [S13].

Czas montażu jest wyrażony w całkowitych klatkach przy zapisanym racjonalnym FPS; audio ma osobną dokładność
próbek. Zakres pliku źródłowego jest niezależny od miejsca klipu w filmie. Planowane timestampy sprzed TTS
są oznaczone jako szacowane. Po przygotowaniu głosu można dopasować sceny do zmierzonych segmentów audio.
Polecenia odwołujące się do konkretnego słowa wymagają rzeczywistego dopasowania tekstu do nagrania;
przy dostępności tylko czasów zdań UI wskazuje ograniczoną dokładność.

Podgląd orientacyjny może korzystać z uproszczeń, ale dokładny podgląd i eksport używają tego samego grafu.
Cache obejmuje wejściowe media, klipy, animacje, sąsiednie przejścia, fonty i wynikowe zakresy kompozycji.
Nakładka obejmująca kilka scen unieważnia wszystkie odpowiednie zakresy, nie tylko jeden beat.

Ręczna edycja i AI wywołują wspólny zestaw operacji: dodaj, podziel, przytnij, przesuń, zamień medium,
ustaw przejście/keyframe, zmień głośność. Operacje są walidowane na rewizji bazowej, uwzględniają blokady
i zapisują jeden odwracalny EditBatch. Asystent nie edytuje przypadkowo innych scen, gdy polecenie dotyczy zaznaczenia.

### Zapis i edycja zewnętrzna

Zapis do pliku tymczasowego i atomowa podmiana; każda mutacja wymaga `expected_revision`.
Wykrycie równoległej edycji przez GUI, CLI lub zewnętrzny edytor powoduje pokazanie różnic.
Historia zatwierdzeń i kopie wersji są odrębne od cache, który można bezpiecznie odbudować.

SQLite z WAL pozostaje na lokalnym dysku. Ten tryb wymaga procesów na tym samym hoście i dopuszcza jednego
zapisującego naraz; kolejka ma krótki czas transakcji i serializowane mutacje [S4].
Kopia zapasowa działającej bazy korzysta z właściwego mechanizmu backupu, nie z kopiowania samego pliku `.db`.

### Zasoby i zadania

Stany zadania: `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCEL_REQUESTED`, `CANCELLED`, `INTERRUPTED`.
Zapisywane są: wejściowa rewizja, postęp, heartbeat, próby, kod zakończenia, log i pliki wynikowe.

Po restarcie zadanie można wznowić od gotowych zdań/segmentów, jeśli ich cache jest zgodny.
Nie zakładamy wznawiania dokładnie w środku obliczanej klatki. Anulowanie kończy procesy potomne i usuwa
niedokończone pliki tymczasowe; zachowuje już sprawdzone segmenty.

Na komputerze z 8 GB RAM domyślnie działa jedno ciężkie zadanie modelowe. Render dostaje liczbę workerów
wynikającą z pomiaru i dostępnej pamięci. Pobieranie i lekkie indeksowanie mogą działać osobno.
Środowiska TTS i renderu nadal są oddzielone. Start aplikacji nie ładuje wszystkich modeli.

## 8. Integracja z Claude i automatyzacja

Pierwsza ścieżka działa z obecnym sposobem pracy: aplikacja przygotowuje prompt, użytkownik korzysta
z własnego Claude Code, a odpowiedź trafia do widoku propozycji. Import może przyjąć strukturę JSON
lub stary format `Narracja / Shot List / Fakty użyte`.

Opcjonalny adapter wywołuje lokalne, oficjalne CLI w trybie programowym. Dokumentacja opisuje `claude -p`
i formaty wyników; dokładny kontrakt, autoryzację, limity i zachowanie błędów trzeba sprawdzić w teście
integracyjnym na używanej wersji [S5]. Aplikacja nie kopiuje tokenów logowania ani nie udaje przeglądarki.
Jeśli aplikacja będzie dystrybuowana innym użytkownikom, adapter musi respektować aktualne warunki
uruchamiania Claude Code w produktach i indywidualne uwierzytelnianie użytkownika [S6].

Tryby użytkownika:

| Tryb | Zachowanie |
|---|---|
| Prowadzony | Aplikacja proponuje kolejny krok i pokazuje propozycje do akceptacji |
| Samodzielny | Użytkownik pisze i montuje, a AI uruchamia dla zaznaczonych fragmentów lub zakresów osi czasu |
| Automatyczny | Wykonuje wcześniej wybrany zestaw kroków z zapisanymi regułami zatwierdzania |

Wynik AI jest propozycją powiązaną z rewizją wejścia. Błędny JSON, brakujące źródło lub fakt spoza banku
nie nadpisuje projektu. Rozróżniamy poprawność formatu, poprawność źródła i redakcyjną ocenę treści.
Zakres automatyzacji jest widoczny przed startem, a generowanie można anulować.
W montażu zakres określa zaznaczenie, scena, przedział czasu lub cały film. Blokady narracji, źródła,
medium i czasu są danymi projektu egzekwowanymi przez usługę edycji, a nie jedynie wskazówką w prompcie.

Lokalny render i TTS nie wymagają hostingu aplikacji. Użycie zewnętrznego modelu pozostaje zależne
od konta i warunków wybranego dostawcy; plan nie zakłada nieograniczonego darmowego generowania.

## 9. Kontrola jakości i gotowości do eksportu

Reguły dzielimy na blokady produkcyjne, ostrzeżenia i sugestie redakcyjne.

| Poziom | Przykłady | Zachowanie |
|---|---|---|
| Blokada | Brak pliku, niepoprawny parametr, wynik dla niezatwierdzonej treści, niewyjaśnione pochodzenie użytego materiału | Finalny eksport wymaga rozwiązania problemu lub właściwej decyzji opisanej w projekcie |
| Ostrzeżenie | Niski rozmiar zdjęcia, wielokrotne użycie klipu, zbyt krótka plansza, nieaktualny odsłuch | Kliknięcie prowadzi do elementu; podgląd roboczy może powstać z widocznym oznaczeniem braków |
| Sugestia | Monotonia typów ujęć, długie zdania, słaby powrót do pytania filmu | Autor decyduje; sugestia nie blokuje montażu |

Ocena źródeł obejmuje narrację i tekst na ekranie. Rekonstrukcje i materiały ilustracyjne mają osobne oznaczenia.
Wszystkie atrybucje pochodzą z faktycznie wykorzystanych materiałów, w tym klipów wideo i nagrań audio.
Wybór licencji nie wynika automatycznie z nazwy katalogu ani nazwy instytucji.

Podgląd i eksport wymagają sprawdzenia pliku przez `ffprobe`: istnienia ścieżek audio/wideo,
czasu trwania i możliwości odczytu. Przed eksportem widać rewizję projektu i datę wygenerowania lektora.

## 10. Backlog wdrożenia — 60 zadań

Każde zadanie ma odrębny wynik do przeglądu. Podział jest propozycją, a nie deklaracją wykonania.
Zachowano identyfikatory APP-001–036 z pierwszego planu. Zakres rozszerzają APP-037–060.

| ID | Zadanie | Kryterium odbioru |
|---|---|---|
| APP-001 | Referencyjne projekty i testy zgodności, ustalenie podstawy PR #1 | Import aktualnego Bloop zachowuje 12 beatów, 53 ujęcia i 22 pozycje faktów; starsze formaty mają opisany wynik kontroli |
| APP-002 | Wersjonowany schemat i adapter typowanych ujęć | Round-trip zachowuje znane i nieznane dane; formularze nie wymagają ręcznych znaczników w opisie |
| APP-003 | Wspólny ProjectService i bezpieczne mutacje | GUI i CLI egzekwują te same reguły; konflikt rewizji nie nadpisuje zmian |
| APP-004 | Trwała kolejka i nadzór procesów | Po restarcie widoczny stan zadania; błąd procesu nie zostaje opisany jako sukces |
| APP-005 | System wizualny i komponenty | Spójne motywy, stany pól, focus, puste widoki i komunikaty; akceptacja ekranów referencyjnych |
| APP-006 | Powłoka aplikacji, Źródła i siedem etapów | Generowanie i Montaż są osobne; przejścia zachowują wybór, a układ działa przy 1440, 1024, 768 i 390 px |
| APP-007 | Kanały i projekty | Można utworzyć, otworzyć, zduplikować i zarchiwizować odcinek oraz wybrać kanał |
| APP-008 | Autosave, historia i cofanie | Odświeżenie nie gubi zapisanego szkicu; cofanie przywraca treść i kolejność ujęć |
| APP-009 | Pomysły i historia tytułów | Dziesięć propozycji można zapisać i wybrać; tytuły historyczne są wykluczane |
| APP-010 | Fakty i źródła | Widać dowód, stan weryfikacji i każde miejsce użycia; import nie oznacza faktów automatycznie jako sprawdzonych |
| APP-011 | Ekran Story Lock | Zatwierdzenie zapisuje wersję; zmiana istotnych danych pokazuje różnice i zależności |
| APP-012 | Ręczny przepływ z Claude i import propozycji | Prompt i wynik przechodzą walidację; błędna odpowiedź nie zmienia projektu |
| APP-013 | Plan rozdziałów i beatów | Przestawianie fragmentów zachowuje ID i powiązania; widoczna krzywa tempa z objaśnieniem |
| APP-014 | Edytor narracji z przypisaniem faktów | Edycja fragmentu i całego tekstu pozostaje spójna; źródła są dostępne przy twierdzeniach |
| APP-015 | Generowanie i poprawki pojedynczego beatu | Propozycja zawiera wersję wejścia; akceptacja nie nadpisuje nowszego tekstu |
| APP-016 | Porównywanie wersji i zależności | Zmiana zdania/faktu pokazuje wymagające ponownej oceny materiały, głos i wyniki |
| APP-017 | Katalog assetów, import i ponowne powiązanie | Dwa pliki o tej samej nazwie nie mylą się; przeniesiony projekt można naprawić przez wskazanie folderu |
| APP-018 | Wyszukiwanie i pobieranie z Commons | Pobranie zapisuje pochodzenie, autora i licencję; błędy i ponowienia są widoczne w zadaniach |
| APP-019 | Formularze i katalog obecnych typów ujęć | Każdy typ ma właściwe kontrolki oraz zgodne wejście renderera; brak parametru wskazany przy polu |
| APP-020 | Dopasowanie materiałów do ujęć | Sugestie pokazują uzasadnienie, pochodzenie i użycia; wybór należy do autora |
| APP-021 | Storyboard w Generowaniu | Dodawanie, duplikowanie, usuwanie i zmiana kolejności działa myszą/klawiaturą i zachowuje powiązania montażu |
| APP-022 | Podstawy interakcji osi czasu | Przycinanie i czas ujęcia działają z blokadami; przygotowane podstawy wielościeżkowego montażu |
| APP-023 | Podgląd i dokładna klatka | Generowanie i Montaż wybierają to samo ujęcie; UI odróżnia wynik starszej rewizji |
| APP-024 | Uogólnienie szablonów i wyglądu | Nowy temat nie wymaga edycji kodu map/diagramów; dane, podpisy i grading są parametrami |
| APP-025 | Profile głosu i przygotowanie próbki | Można dodać próbkę lub własne nagrania, odsłuchać je i wybrać profil bez publikowania próbki |
| APP-026 | Adapter TTS i cache konfiguracji | Język i profil są respektowane; zmiana ustawień unieważnia właściwe nagrania |
| APP-027 | Edycja wymowy i dogrywki zdań | Zmienione zdanie można wygenerować i porównać bez utraty wybranych wcześniejszych wersji |
| APP-028 | Mikser i nagrania archiwalne | Podkład, efekty i lektor mają osobne ustawienia; odsłuch odpowiada finalnemu planowi miksu |
| APP-029 | Render na migawkach i poprawny cache | Zmiana MP4 lub atrybucji odświeża właściwe segmenty; anulowanie i błąd nie tworzą gotowego artefaktu |
| APP-030 | Kreator eksportu i kontrola braków | Eksportuje działający MP4 oraz obecne formaty JSON/MD/TXT/XLSX z oznaczoną rewizją |
| APP-031 | Dopasowanie tekstu do audio i napisy SRT/VTT | Czasy zdań/słów mają zmierzone dopasowanie; można poprawić segmentację, dokładność i brzmienie tekstu |
| APP-032 | Przenośna paczka projektu | Po przeniesieniu można odtworzyć projekt i media; manifest opisuje świadomie pominięte duże lub prywatne pliki |
| APP-033 | Testy E2E, dostępności i wydajności | Główny proces przechodzi na danych referencyjnych; pomiary wykonane na opisanym sprzęcie |
| APP-034 | Launcher i diagnostyka środowiska | Aplikację uruchamia się jednym wejściem; brak FFmpeg/modelu ma konkretną instrukcję naprawy |
| APP-035 | Opcjonalny automatyczny adapter Claude Code | Sprawdzony sposób autoryzacji i błędów; ograniczony zakres zadań; zweryfikowane warunki dystrybucji |
| APP-036 | Przygotowanie wydania i odtwarzania danych | Kopię projektu da się przywrócić; instrukcja obejmuje aktualizację i odzyskiwanie po przerwaniu zadania |
| APP-037 | Rejestr połączeń i interfejs adapterów źródeł | Można dodać/testować źródło; możliwości i brak dostępu są jawne; poświadczenia nie trafiają do projektu |
| APP-038 | Wyszukiwanie w wielu źródłach | Wyniki są normalizowane, filtrowane i przypisywane do scen; ograniczenia dostawców i anulowanie są respektowane |
| APP-039 | Adaptery stockowych zdjęć i wideo | Pixabay oraz warunkowy Pexels mają podgląd, import wariantu i pochodzenie; brak klucza nie blokuje importu własnego |
| APP-040 | Katalogi książek i konkretne wydania | Google Books/Open Library rozróżniają metadane, podgląd i pełną treść; cytat wskazuje wydanie |
| APP-041 | Własne PDF/EPUB i skany | Odczyt/OCR zachowuje numerację i oryginał; można wskazać cytat lub ilustrację z lokalizacją |
| APP-042 | Artykuły, raporty, RSS i DOI | Informacja ma zapisany fragment, datę i oryginał; metadane nie są podawane jako przeczytany pełny tekst |
| APP-043 | Custom źródła | Folder, link i konfigurowalny adapter API współpracują z tym samym katalogiem bez zmian UI dla każdego dostawcy |
| APP-044 | Osobny dział Generowanie filmu | Lewy panel ma prompt/zlecenie wyszukania; karta zawiera medium, metodę animacji, timestamp i narrację |
| APP-045 | Wklejanie i przesyłanie mediów | Schowek, plik, drag-and-drop i obsługiwany URL rozpoznają rodzaj materiału; pochodzenie da się uzupełnić |
| APP-046 | Generowanie obrazów i wariantów | Prompt i parametry są zapisane; można wygenerować/porównać wariant bez kasowania wybranego klipu |
| APP-047 | Presety ruchu i animacji | Najazd, pan, lupa i inne wspierane metody mają podgląd oraz edytowalne parametry; parallax ma jawne wymagania |
| APP-048 | Synchronizacja Generowania z Montażem | Przyjęte medium trafia na oś; zmiana czasu aktualizuje plan, a regeneracja nie nadpisuje ręcznych poprawek |
| APP-049 | Kanoniczny model sekwencji i ścieżek | Scena, asset i wystąpienie klipu mają odrębne ID; czas klipów, warstwy i blokady zachowują się po zapisie |
| APP-050 | Edytor wielościeżkowy | Działa split, trim, move, ripple, snap, grupowanie, overlay i niezależne audio z cofaniem |
| APP-051 | Compositor i eksport montażu | Równoległe warstwy, tekst, animacje i przejścia dają ten sam wynik w dokładnym podglądzie i eksporcie |
| APP-052 | Podgląd proxy i zakresy renderu | Można płynnie przeglądać proxy i przeliczyć zaznaczony zakres; wynik ma rewizję i stan aktualności |
| APP-053 | Wspólne operacje montażowe dla UI i AI | Każda zmiana ma bazową rewizję, walidację i undo; zestaw operacji przyjmuje się atomowo |
| APP-054 | Asystent montażu w języku naturalnym | Polecenie działa na wybranym zakresie, respektuje blokady i daje podgląd różnic lub odwracalny automatyczny wynik |
| APP-055 | Wersje A/B i przejmowanie edycji | Można porównać dwa montaże oraz ręcznie kontynuować po AI bez utraty ujęć i poprzedniej wersji |
| APP-056 | Cache zależności warstw i klipów | Zmiana nakładki, prędkości, animacji lub dźwięku unieważnia wszystkie właściwe zakresy |
| APP-057 | Gotowość ujęć i budżet produkcji | Widać braki, wybrane warianty, szacowane koszty/czas i limity automatyzacji |
| APP-058 | Plan przebitek i spójność kanału | Z narracji powstają propozycje kadrów/zapytań; referencje i blokady stylu są zachowane przy wariantach |
| APP-059 | Testy kontraktów źródeł i edycji | Fixtures obejmują brak dostępu, podgląd książki, kolizje edycji, keyframes, timebase i anulowanie; testy nie wymagają płatnych wywołań |
| APP-060 | Pełny proces produkcji i dokumentacja | Test od źródła książkowego/stocku przez przygotowanie ujęcia i montaż ręczny/AI do eksportu oraz ponownego otwarcia projektu |

### Kolejność dostarczania

**Wersja A — Generowanie i Montaż dla istniejących projektów.** APP-001–008, 017, 019, 021–023, 029, 030,
037, 038, 043–045, 047–052, 056. To 27 zadań: osobny plan ujęć, własne źródła/import oraz rzeczywista
wielościeżkowa edycja z podglądem i eksportem. Korzysta z dostarczonych nagrań głosu.

**Wersja B — źródła i cały nowy film, także z montażem AI.** APP-009–016, 018, 020, 024–028, 039–042, 046,
053–055, 057, 058. To kolejne 25 zadań: książki, stocki, informacje, scenariusz, lektor, generowanie obrazów
i sterowanie montażem. AI korzysta z importowanych propozycji; automatyczny adapter CLI dochodzi w wersji C.

**Wersja C — dopracowane wydanie 1.0.** APP-031–036, 059, 060. To ostatnie osiem zadań: dokładne dopasowanie
tekstu do audio, napisy, przenoszenie projektów, opcjonalne automatyczne połączenie Claude i pełna walidacja wydania.

W każdej wersji wygląd i ergonomia mają być dopracowane. Równolegle z fundamentem należy zatwierdzić
cztery ekrany: Źródła, Scenariusz, Generowanie i Montaż. Projekt interakcji powstaje razem z fundamentem backendu.

Zależności krytyczne: schemat i ProjectService przed mutacjami UI; kolejka przed TTS/renderem;
asset ID przed ostatecznym cache; Story Lock przed generowaniem zatwierdzanej narracji;
rzeczywiste czasy audio przed dokładnymi napisami i timingiem filmu.
Dodatkowo: model sekwencji przed wielościeżkową edycją, compositor przed obietnicą finalnego wyniku warstw,
a wspólne operacje montażowe i blokady przed automatycznym stosowaniem poleceń AI.

## 11. Kryteria odbioru całego produktu

1. Nowy użytkownik otwiera projekt i rozumie następny krok bez znajomości parametrów JSON.
2. Istniejący Bloop zachowuje zawartość po imporcie; rozbieżności historycznych pól są jawne.
3. Utworzenie nowego filmu, zebranie źródeł, napisanie scenariusza i przypisanie mediów nie wymaga edytora kodu.
4. Da się poprawić jedno zdanie lektora i jedno ujęcie, a następnie przeliczyć tylko zależne wyniki.
5. Zmiana ustawień głosu, klipu MP4 i licencji ma sprawdzony skutek dla cache.
6. Aplikacja przeżywa odświeżenie strony, restart i błąd procesu bez gubienia zatwierdzonych danych.
7. Render jest powiązany z jedną rewizją i przechodzi kontrolę pliku wynikowego.
8. Źródła, ilustracje, rekonstrukcje i atrybucje pozostają dostępne w projekcie oraz eksporcie.
9. UI ma obsługę klawiatury, czytelne etykiety i mierzalny kontrast; przeciąganie nie jest jedyną drogą edycji.
10. Referencyjny test obejmuje materiały 4K/1080p, małe zdjęcie, brakujące media, błąd pobrania, dwie równoległe edycje
    i anulowanie generowania. Ciężkie testy modeli są oddzielone od szybkich testów logiki.
11. Połączenia zdjęć, stocków, książek, informacji i źródeł własnych mają jawne możliwości i zapisane pochodzenie.
12. Ujęcie w Generowaniu zawiera prompt lub zlecenie wyszukania, medium do wklejenia/importu, metodę ruchu,
    timestamp i odpowiedni fragment narracji; może zostać przekazane do Montażu i z niego ponownie otwarte.
13. W osobnym Montażu można ręcznie przyciąć, rozdzielić i nałożyć klipy oraz zrobić to samo przez propozycję AI.
14. AI respektuje zablokowane narracje, media i czasy. Zestaw zmian da się cofnąć i kontynuować ręcznie.
15. Podgląd i finalny eksport poprawnie składają wiele ścieżek obrazu, tekst i niezależny dźwięk.

Budżety wydajności są celami do potwierdzenia: reakcja na lokalną edycję poniżej 100 ms w typowym projekcie,
otwarcie indeksowanego projektu bez pełnego skanowania całej biblioteki, oraz podgląd fragmentu bez renderowania
niezmienionej reszty filmu. Dokładne czasy generowania zależą od sprzętu i zostaną zapisane w benchmarkach.

## 12. Kolejne rozszerzenia po pierwszym wydaniu

- Opakowanie Tauri i natywne okno wyboru katalogów; Tauri dokumentuje procesy pomocnicze dla narzędzi Python [S7].
- Pionowe kompozycje Shorts z osobnymi układami i bezpiecznymi marginesami napisów.
- Dodatkowe pakiety History i Geography oraz osobno opisany tryb fikcyjnych What-If.
- Wiele wersji językowych odcinka z osobnymi głosami i timingiem, współdzielących bazę źródeł.
- Zdalny worker lub serwer renderujący, jeśli lokalna maszyna okaże się wąskim gardłem.
- Wspólna praca wielu osób i osobne role po wprowadzeniu kont oraz synchronizacji.
- Integracja publikowania na YouTube jako odrębna funkcja z osobnym poświadczeniem i zatwierdzeniem publikacji.

## 13. Źródła i odnośniki

Repozytorium i przeglądane wersje:

- [Yt — main](https://github.com/krystiangaleczka-tech/Yt/tree/c27da6c1f9400ad8494f84784139d07456ef16ee).
- [PR #1 — tematy i Story Lock](https://github.com/krystiangaleczka-tech/Yt/pull/1).
- [Obecny edytor](https://github.com/krystiangaleczka-tech/Yt/blob/c27da6c1f9400ad8494f84784139d07456ef16ee/docos/editor.py).
- [Renderer i cache](https://github.com/krystiangaleczka-tech/Yt/blob/c27da6c1f9400ad8494f84784139d07456ef16ee/docos/render_doc.py).
- [Lektor](https://github.com/krystiangaleczka-tech/Yt/blob/c27da6c1f9400ad8494f84784139d07456ef16ee/docos/voice_beats.py).

Dokumentacja techniczna sprawdzona na potrzeby rekomendacji:

- S1: [Vite — Getting Started](https://vite.dev/guide/).
- S2: [Radix Primitives — Accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility).
- S3: [FastAPI — Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).
- S4: [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html).
- S5: [Claude Code — Run programmatically](https://code.claude.com/docs/en/headless).
- S6: [Claude Code — Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance).
- S7: [Tauri — Embedding External Binaries](https://v2.tauri.app/develop/sidecar/).
- S8: [Pixabay — API Documentation](https://pixabay.com/api/docs/).
- S9: [Pexels — API i stan wydawania kluczy](https://www.pexels.com/api/), [dokumentacja zdjęć i filmów](https://www.pexels.com/api/documentation/).
- S10: [Google Books — Volume i accessInfo](https://developers.google.com/books/docs/v1/reference/volumes).
- S11: [Open Library — API](https://openlibrary.org/developers/api), [dzieła i wydania](https://openlibrary.org/dev/docs/api/books).
- S12: [Crossref — REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [dostęp do pełnych tekstów](https://www.crossref.org/documentation/retrieve-metadata/text-and-data-mining/).
- S13: [FFmpeg — dokumentacja filtrów](https://ffmpeg.org/ffmpeg-filters.html).

### Historia planu

- Wersja 1: przegląd wszystkich plików repozytorium i plan 36 zadań.
- Wersja 2: osobne Źródła, Generowanie i Montaż; integracje zdjęć, stocków, książek, informacji i custom źródeł;
  karta ujęcia z promptem, medium, animacją, timestampem i narracją; wielościeżkowa edycja ręczna/AI;
  wspólne operacje montażowe, synchronizacja i rozszerzenie backlogu do 60 zadań.

## Załącznik: kompletność przeglądu

Poniższy wykaz obejmuje wszystkie pliki `main` oraz dodatkowe wersje z PR #1.
Fonty oceniono jako dane binarne; kod i pozostałe pliki jako tekst lub struktury JSON.
### Pliki main — 64

| Plik | Wersja (skrót SHA) | Rola w przeglądzie |
|---|---|---|
| `.gitignore` | `6952f58` | Wykluczenia prywatnych nagrań, modeli, cache i ciężkich mediów; podstawa pakowania projektu. |
| `LICENSE` | `7057b6b` | Licencja kodu; zachować przy dystrybucji. |
| `README.md` | `f1daa41` | Zakres produktu, uruchamianie i historia wersji. |
| `docos/README.md` | `174108b` | Kontrakt CLI i przepływ produkcji. |
| `docos/docos.py` | `01671e2` | Model projektu, prompty, parser, reguły i eksport/import. |
| `docos/editor.html` | `c5654a0` | Aktualny interfejs; zachowania do odtworzenia i rozbudowy. |
| `docos/editor.py` | `7069a55` | Serwer edytora, zapis, miniatury, biblioteka i uruchamianie zadań. |
| `docos/examples/bloop.json` | `68b9d81` | Starszy przykład; dane do testów zgodności i komunikatów. |
| `docos/fetch_commons.py` | `97106ff` | Wyszukiwanie/pobieranie i metadane licencji. |
| `docos/fetch_media.py` | `a3259f4` | Odtwarzanie mediów, lista NOAA i fragmenty właściwe Bloop. |
| `docos/make_assets.py` | `b6d1803` | Opcjonalne kadry AI; wydzielenie adaptera zadania. |
| `docos/migrate_sent_cache.py` | `b99eef6` | Jednorazowa migracja dawnego cache zdań. |
| `docos/render_doc.py` | `8b44319` | Główny renderer, dźwięk, przejścia i cache. |
| `docos/render_film.py` | `2fe7cf0` | Wspólne narzędzia i starszy renderer ze specjalizacjami Bloop. |
| `docos/voice_beats.py` | `ceb5a30` | TTS per zdanie, wymowa, tempo i cache. |
| `docs/ARCHITECTURE.md` | `11d69ed` | Model danych i połączenia silników. |
| `docs/EDITOR.md` | `d4f2604` | Zachowania i endpointy obecnego edytora. |
| `docs/LEGAL.md` | `72aefa9` | Obecne zasady pochodzenia materiałów i oznaczeń; nie zastępują oceny konkretnego assetu. |
| `docs/SETUP.md` | `9e59a71` | Środowiska i historyczne pomiary wydajności. |
| `docs/SHOT_TYPES.md` | `fde698b` | Katalog ujęć i parametrów. |
| `docs/VOICE.md` | `b83fb93` | Próbki głosu i zasady generowania. |
| `docs/WORKFLOW.md` | `48b3722` | Proces tworzenia odcinka. |
| `docs/skill/SKILL.md` | `fe11fa3` | Instrukcje scenopisarskie dla Claude. |
| `pilot/clone_voice.py` | `ba56665` | Demonstracyjne przygotowanie próbki i klonowanie. |
| `pilot/compose.py` | `86d5301` | Stały pilot dziesięciosekundowy; przykłady efektów, nie rdzeń studia. |
| `pilot/fonts/CourierPrime-Bold.ttf` | `d27ce71` | Binarny TTF: Courier Prime Bold 3.018, 415 glifów. |
| `pilot/fonts/CourierPrime-Regular.ttf` | `2a0f8bd` | Binarny TTF: Courier Prime Regular 3.018, 415 glifów. |
| `pilot/fonts/Montserrat.ttf` | `c97aca1` | Binarny font zmienny Montserrat 9.000, 2747 glifów. |
| `pilot/fonts/OFL-courierprime.txt` | `7cdc333` | Warunki dołączenia Courier Prime. |
| `pilot/fonts/OFL-montserrat.txt` | `fe576a2` | Warunki dołączenia Montserrat. |
| `pilot/gen_images.py` | `67d2221` | Demonstracyjne prompty SD i zależność MPS. |
| `pilot/gen_voice.py` | `a235ab5` | Demonstracyjny szybki lektor Kokoro. |
| `projekty/bloop_v3/README.md` | `86e5d28` | Wskazanie bieżącego projektu i historycznych wariantów. |
| `projekty/bloop_v3/beats/B01.md` | `2539a20` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B02.md` | `f71b220` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B03.md` | `f499ded` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B04.md` | `efec0c4` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B05.md` | `aed6306` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B06.md` | `00a370d` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B07.md` | `3337f2e` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B08.md` | `b349d7f` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B09.md` | `4a2c692` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B10.md` | `3dee034` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B11.md` | `7f64bcc` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats/B12.md` | `3935b44` | Odpowiedź beatu v3: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B01.md` | `e67a495` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B02.md` | `4600fde` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B03.md` | `646f28a` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B04.md` | `82162a1` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B05.md` | `285454a` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B06.md` | `d82f3f2` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B07.md` | `8e7c893` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B08.md` | `2c167c5` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B09.md` | `514bd31` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B10.md` | `8b00d5f` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B11.md` | `106e37d` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/beats_v4/B12.md` | `baacf78` | Historyczna odpowiedź beatu v4: narracja, ujęcia, fakty i połączenie. |
| `projekty/bloop_v3/bloop_v3.json` | `fcf8ffe` | Starszy projekt: 12 beatów, 69 ujęć, 21 faktów. |
| `projekty/bloop_v3/bloop_v3_description.txt` | `b3e0e1d` | Opis, źródła i atrybucje; przykład eksportu. |
| `projekty/bloop_v3/bloop_v4.json` | `920a88b` | Bieżący projekt: 12 beatów, 53 ujęcia, 22 fakty; sekcja render. |
| `projekty/bloop_v3/raw/commons/licenses.json` | `0ae7130` | 33 pozycje metadanych i licencji. |
| `projekty/bloop_v3/raw/video/licenses.json` | `7a710b7` | 15 pozycji metadanych i licencji wideo. |
| `requirements-render.txt` | `295f399` | Zależności montażu i opcjonalnych narzędzi. |
| `requirements-tts.txt` | `2189fda` | Oddzielne zależności TTS. |

### Wersje dodane lub zmienione w PR #1 — 10

| Plik | Zmiana | Wersja (skrót SHA) | Rola |
|---|---|---|---|
| `README.md` | zmieniony | `e038a58` | Zakres produktu, uruchamianie i historia wersji. |
| `docos/README.md` | zmieniony | `8ae5072` | Kontrakt CLI i przepływ produkcji. |
| `docos/docos.py` | zmieniony | `582f197` | Model projektu, prompty, parser, reguły i eksport/import. |
| `docos/editorial.py` | nowy | `bab5f53` | Nowy profil Documentary, tematy i kontrakt Story Lock. |
| `docos/tests/test_editorial.py` | nowy | `a3005d4` | Nowe testy redakcji i interfejsu CLI. |
| `docs/ARCHITECTURE.md` | zmieniony | `c00366e` | Model danych i połączenia silników. |
| `docs/EDITORIAL.md` | nowy | `c009f92` | Nowa instrukcja tematów i zatwierdzania historii. |
| `docs/WORKFLOW.md` | zmieniony | `111c821` | Proces tworzenia odcinka. |
| `docs/changes/2026-10-26-topics-story-lock.md` | nowy | `75f62d8` | Log zmian i walidacji PR #1. |
| `docs/skill/SKILL.md` | zmieniony | `9831768` | Instrukcje scenopisarskie dla Claude. |


