# Audyt DocOS Studio i poprawa interfejsu — 26.10.2026

Sprawdzana podstawa: `c0fa554`, branch `codex/docos-studio-20261026`.
Porównanie z rozmową „Ocena repozytorium filmowego” i planem v2 z 60 zadaniami, odczytanymi w zalogowanym Safari:
https://chatgpt.com/g/g-p-6adf28f1a0448191bc6f743c798b95df-yt/c/6adf293e-3f38-83ed-be04-ce446ec13b4d

**Wniosek: aplikacja ma działający fundament i główne ekrany z zamówienia, ale nie realizuje całego zaakceptowanego planu. Nie jest jeszcze gotowym, kompletnym studiem produkcyjnym.**

Źródła, Generowanie i Montaż są osobnymi, połączonymi obszarami. Dostępne są rzeczywiste operacje edycji, zapis i render MP4. Istnieją jednak błędy aktualności danych i blokad, a część zaawansowanych funkcji pozostaje niewykonana. Dokumentacja wdrożenia sama zaznacza ten ograniczony zakres w `docs/STUDIO.md` i logu zmian.

## Potwierdzone problemy

### 1. Zmiana narracji pozostawia stare nagranie jako aktualne — wysoki priorytet

W izolowanym projekcie przypisano nagranie, zatwierdzono historię i zmieniono całą narrację ujęcia. Kontrola `/check` przed zmianą i po zmianie zwróciła `issues: []`. Pole `voice_asset_id` nadal wskazywało stary dźwięk, a historia zachowała `APPROVED`. Warunek finalnego eksportu opiera się na tej kontroli, więc nie wykryje rozbieżności tekstu i głosu.

Przyczyna: kontrola w `studio_api/app.py:308` sprawdza obecność nagrania, bez porównania treści wejściowej. Brakuje statusu nieaktualnego nagrania po zmianie narracji/języka/profilu. Wynik: film może zawierać poprzednią wersję wypowiedzi bez ostrzeżenia.

### 2. Propozycje redakcyjne AI nie zachowują rewizji wejściowej — wysoki priorytet

Symulowano zmianę tytułu podczas generowania karty historii. Generowanie wystartowało dla rewizji 16, projekt zmieniono do 17, a odpowiedź dla poprzedniego tytułu została przyjęta z HTTP 200. Zastąpiła pole hook aktualnej karty.

Przyczyna: `/writer/.../generate` zwraca samą odpowiedź, bez rewizji. `WriterTools` przy przyjęciu przesyła bieżącą rewizję zamiast rewizji promptu (`apps/studio/src/Editorial.tsx:74`). Mechanizm montażowego asystenta AI ma osobne `base_revision` i jest pod tym względem lepiej zabezpieczony.

### 3. Blokada ujęcia w Generowaniu nie chroni odpowiadających klipów przed AI — średni priorytet

Zablokowano ujęcie (`scene.locked=true`), a następnie wysłano operację przesunięcia jego klipu jako AI. Operacja zwróciła HTTP 200, zmieniła początek ujęcia z 0 na 30 klatek i pozostawiła oznaczenie blokady.

`studio_timeline/operations.py:48` respektuje blokady klipu i ścieżki, lecz nie sprawdza blokady powiązanej sceny. Osobne blokady klipów/ścieżek są testowane i działają. UI powinno jednoznacznie pokazywać zakres blokad; plan wymagał ich wspólnego egzekwowania.

### 4. Import Bloop zachowuje dane historyczne, ale nie odtwarza aktywnych powiązań i szablonów — średni priorytet

Import rzeczywistego `bloop_v4.json`: 12 beatów, 53 ujęcia i 22 fakty. Powstaje 53 scen, zachowano 22 fakty i kompletny oryginał w `legacy`, ale suma aktywnych `scene.fact_ids` wynosi zero. Beat jest spłaszczany do ujęć; jego narracja trafia tylko do pierwszego z nich. Dotychczasowe mapy, spektrogramy i inne szablony nie są odtwarzane przez nowy compositor. Sam JSON nie przenosi plików ani gotowej osi czasu.

To oznacza konieczność ręcznego ponownego przygotowania produkcji istniejącego filmu. Zachowanie surowego oryginału chroni treść historyczną, lecz nie spełnia pełnego kryterium zgodności produkcyjnej APP-001/019/024.

## Sprawdzenie działania na tym komputerze

| Obszar | Wynik i ograniczenie |
|---|---|
| Uruchomienie | FastAPI i zbudowany frontend działają na `127.0.0.1:8876`. |
| Build | `npm run build` przechodzi po zmianach UI. |
| Testy Studio | 36/36 po dodaniu 3 regresji obsługi błędów Claude; pierwotny zestaw 33/33. |
| Testy frontendu | 5/5. |
| Stare testy DocOS | 16 przechodzi, 2 pominięte z powodu braku `openpyxl` w użytym środowisku `pilot/.venv`. Nie jest to pełne powtórzenie deklarowanych 18/18 eksportów XLSX. |
| Edycja w Safari | Zmiana początku klipu z 8 na 9 sekund zapisana; Cofnij przywrócił 8 sekund. Odtwarzanie podglądu Canvas pokazuje ilustracje. |
| Rzeczywisty podgląd MP4 | Uruchomiony przyciskiem w UI. Zadanie zakończone sukcesem. FFprobe: H.264, 640×360, 30 fps, 32,000 s. Demo nie ma nagrań audio; osobny test sprawdza rzeczywisty miks AAC, obraz, tekst i keyframes. |
| Commons | Rzeczywiste zapytanie `hydrophone`: 18 wyników z metadanymi. |
| Open Library | Rzeczywiste zapytanie `ocean`: 18 wyników katalogowych. Nie jest to dostęp do pełnego tekstu książek. |
| Pixabay/Pexels | Kod adapterów obecny; nie przeprowadzono wywołań na rzeczywistych kluczach użytkownika. |
| Lektor lokalny | Worker Chatterbox wygenerował polskie zdanie: WAV PCM 16-bit, 24 kHz, 3,4 s. Nie oceniano jakości głosu odsłuchem. |
| Generator obrazu | Środowisko importuje torch/diffusers, ale test bez sieci zakończył się brakiem kompletu plików dla domyślnego ładowania SD 1.5. Nie pobierano dużych wag. Generowanie obrazu online nie zostało potwierdzone. Samo `health.image=true` oznacza istnienie interpretera, nie gotowość modelu. |
| Asystent AI | Claude CLI jest zalogowane. Rzeczywisty test zwrócił 429 `usage_limit_reached`: tygodniowy limit konta, odnowienie 28.10 o 10:00 Europe/Warsaw. Test pełnej propozycji AI z działającym modelem pozostaje niepotwierdzony do odnowienia limitu. Ręczny import operacji i ich walidację obejmują testy. |
| Przenoszenie i konflikty | Testy ZIP, sum kontrolnych, undo/redo po restarcie, starych rewizji, anulowania i trwałej kolejki przechodzą. |

## Zmiany wykonane podczas tego audytu

Na prośbę użytkownika przebudowano wygląd w wybranym kierunku: ciemne, profesjonalne, zwarte studio.

- Neutralne grafity, subtelny lawendowy akcent, mniejsze nagłówki i systemowa typografia bez zależności od Google Fonts.
- Węższa nawigacja, krótsze etykiety, prostsze nazwy ekranów i mniej dekoracyjnych odstępów.
- Na desktopie Generowanie mieści podgląd, narrację i zwarty storyboard w obszarze aplikacji; boczne panele przewijają się niezależnie.
- Montaż ma podgląd i stale dostępną oś czasu, bardziej zwarte ścieżki oraz rzeczywiste miniatury w klipach.
- Dostosowanie układu do węższych ekranów, stan aktywnej strony dla technologii asystujących i mniejszy pusty inspektor mobilny.
- Poprawiono obsługę błędu Claude CLI: limit AI ma własny komunikat. Wcześniej błąd zakończenia procesu był myląco wyświetlany jako problem medium/FFmpeg. Dodano 3 testy regresji.

Przeprowadzono kontrolę wizualną Safari na desktopie oraz w trybie responsywnym przy 1440×900, 1024×900 i 390×900. Sprawdzono też mobilne menu i przejście do Generowania. Nie jest to kompletny audyt dostępności ani test wszystkich gestów i przeglądarek.

## Mapa 60 zadań planu

„Działa” oznacza potwierdzony wskazany zakres; „Częściowo” oznacza brak części kryterium; „Brak” oznacza niewykonaną funkcję. Ta tabela porównuje kryteria z kodem i wykonanymi kontrolami, nie przypisuje procentu ukończenia ani nie udaje 60 osobnych testów E2E.

| ID | Ocena | Stan względem kryterium |
|---|---|---|
| APP-001 | Częściowo | Zachowane 53 ujęcia i 22 fakty Bloop oraz oryginał, ale brak aktywnych powiązań i odtworzenia produkcji. |
| APP-002 | Częściowo | Typowany, wersjonowany schemat; brak formularzy dawnych szablonów. |
| APP-003 | Częściowo | Atomowe mutacje i rewizje w Studio; stare CLI nie korzysta ze wspólnej usługi Studio. |
| APP-004 | Działa | Trwała kolejka, błędy i stan INTERRUPTED po restarcie potwierdzone testami. |
| APP-005 | Częściowo | System UI przebudowany i obejrzany; brak pełnego pomiaru dostępności i jasnego motywu. |
| APP-006 | Częściowo | Osobne źródła i siedem etapów, kontrola kilku szerokości; wybór sceny nie jest stale synchronizowany we wszystkich kierunkach. |
| APP-007 | Częściowo | Tworzenie/otwieranie/import; brak zarządzania archiwizacją, duplikacją i osobnym katalogiem kanałów. |
| APP-008 | Działa | Zapis po opuszczeniu pola, trwała historia i undo/redo; tekst w aktywnym polu przed opuszczeniem nie jest jeszcze zapisany. |
| APP-009 | Częściowo | Generator/import 10 tematów i pamięć w projekcie; brak wspólnej historii całego kanału między odcinkami. |
| APP-010 | Częściowo | Fakty, statusy i źródła istnieją; niekompletna mapa użyć i migracja powiązań. |
| APP-011 | Częściowo | Karta i zatwierdzenie działają; brak widoku różnic i pełnych zależności. |
| APP-012 | Częściowo | Prompt i JSON z walidacją; niezaimplementowany dawny format odpowiedzi i powiązanie z rewizją wejścia. |
| APP-013 | Brak | Brak pełnego modelu edytowanych rozdziałów/beatów i krzywej tempa w Studio. |
| APP-014 | Częściowo | Narracja ujęć i zbiorczy tekst; niekompletne powiązanie redakcji z dowodami. |
| APP-015 | Częściowo | AI dodaje szkic ujęć; brak bezpiecznej poprawki pojedynczego beatu z rewizją promptu. |
| APP-016 | Brak | Brak pełnego porównania wersji i unieważniania głosu/mediów po zmianie tekstu. |
| APP-017 | Częściowo | Assety identyfikowane treścią i pochodzeniem; brak naprawy powiązań przez wskazanie folderu. |
| APP-018 | Częściowo | Commons wyszukuje; import zapisuje metadane, ale pobrania nie są pełną kolejką zadań z ponowieniami. |
| APP-019 | Brak | Brak katalogu i formularzy wszystkich dotychczasowych typów ujęć. |
| APP-020 | Częściowo | Ręczny wybór materiału i wyszukiwanie z ujęcia; brak rozbudowanych sugestii z uzasadnieniem i mapą użyć. |
| APP-021 | Częściowo | Storyboard dodaje i wybiera ujęcia; brak pełnego duplikowania/usuwania/przestawiania kart. |
| APP-022 | Działa | Czas, trim, przesuwanie i blokady klipów/ścieżek; zakres blokady sceny wymaga naprawy. |
| APP-023 | Częściowo | Canvas i pełny dokładny podgląd; brak osobnej dokładnej klatki i kompletnej synchronizacji zaznaczenia. |
| APP-024 | Brak | Dawne mapy/diagramy nie zostały uogólnione w nowym silniku. |
| APP-025 | Częściowo | Własne nagrania i próbka przez konfigurację środowiska; brak edytora profili i przygotowania próbki w UI. |
| APP-026 | Częściowo | TTS respektuje język i generuje WAV; brak cache konfiguracji oraz poprawnego stanu aktualności. |
| APP-027 | Brak | Brak słownika wymowy i zarządzania dogrywkami/cache pojedynczych zdań. Worker dzieli tekst, lecz skleja całe ujęcie. |
| APP-028 | Częściowo | Osobne audio, głośność, fades i keyframes; brak duckingu i waveformów. |
| APP-029 | Częściowo | Migawki renderu i anulowanie; brak segmentowego cache i pełnej kontroli oczekiwanych strumieni/czasu. |
| APP-030 | Częściowo | MP4/JSON/ZIP i TXT narracji; brak pełnego nowego kreatora MD/XLSX oraz opisu/atrybucji. |
| APP-031 | Brak | Brak zmierzonego dopasowania słów/zdań i napisów SRT/VTT. Ścieżka tekstowa nie zastępuje tej funkcji. |
| APP-032 | Działa | ZIP z mediami, manifestem i weryfikacją sum kontrolnych. |
| APP-033 | Częściowo | Testy API i renderu plus ręczne UI; brak pełnej automatyzacji E2E, audytu dostępności i benchmarków. |
| APP-034 | Częściowo | Instalator i start działają; diagnostyka modeli wykrywa głównie ścieżki, nie gotowość generatora. |
| APP-035 | Częściowo | Adapter Claude obecny i konto zalogowane; test modelu blokuje realny limit konta. Poprawiono komunikat błędu. |
| APP-036 | Częściowo | Historia i ZIP pomagają odzyskiwać dane; brak kompletnego przetestowanego procesu wydania/aktualizacji. |
| APP-037 | Częściowo | Rejestr adapterów i prywatna konfiguracja; brak pełnego testowania połączeń i diagnostyki możliwości. |
| APP-038 | Częściowo | Normalizacja i wyszukiwanie jednego dostawcy; brak równoległego zbiorczego wyszukiwania oraz anulowania zapytań. |
| APP-039 | Niepotwierdzone | Adaptery Pixabay/Pexels obecne; nie testowano rzeczywistych kluczy, wariantów i pobrań. |
| APP-040 | Częściowo | Katalogi książek i podstawowe metadane; brak pełnego wyboru konkretnego wydania i całego procesu cytowania. |
| APP-041 | Częściowo | Odczyt tekstowych PDF/EPUB z lokalizacjami przechodzi testy; brak OCR i wyboru ilustracji/skanu. |
| APP-042 | Częściowo | URL/HTML i Crossref; brak RSS i kompletnej obsługi raportów. |
| APP-043 | Częściowo | Pliki, linki i publiczne JSON API; brak obserwowanych folderów, uwierzytelniania i paginacji custom API. |
| APP-044 | Działa | Osobne Generowanie z promptem/szukaniem, materiałem, ruchem, początkiem, długością i narracją. |
| APP-045 | Częściowo | Plik, URL, schowek i drag/drop obecne; schowka z filmem nie potwierdzono na wszystkich systemach. |
| APP-046 | Niepotwierdzone | Worker i warianty istnieją; domyślnego obrazu nie wygenerowano z niekompletnego cache offline. |
| APP-047 | Częściowo | Pięć presetów i keyframes; brak lupy, masek/parallax oraz pełnego katalogu. |
| APP-048 | Częściowo | Przekazanie medium na oś i aktualizacja czasu od klipu działają; blokady sceny są niespójne. |
| APP-049 | Działa | Oddzielne ID scen, assetów i klipów, całkowite klatki i niezależne source_in. |
| APP-050 | Częściowo | Split/trim/move/ripple/snap, warstwy i undo; brak grupowania, ograniczenia podziału klipu z keyframes. |
| APP-051 | Częściowo | Rzeczywiste warstwy/tekst/audio/keyframes z tego samego renderera; brak katalogu przejść. |
| APP-052 | Częściowo | Canvas i render całego podglądu; brak proxy oraz renderowania wybranego zakresu. |
| APP-053 | Działa | Wspólne atomowe operacje, rewizje i cofanie dla ręcznej edycji i montażowego AI. |
| APP-054 | Częściowo | Polecenia i walidacja propozycji, zaznaczenie/całość; realny model blokuje limit, blokada sceny wymaga poprawy. |
| APP-055 | Brak | Brak porównywania alternatywnych montaży A/B. |
| APP-056 | Brak | Brak cache renderowanych zakresów zależnych od warstw/klipów. |
| APP-057 | Częściowo | Lista braków i warianty; brak budżetu, limitów kosztu i wiarygodnego stanu aktualności. |
| APP-058 | Brak | Brak wspólnego profilu stylu kanału i pełnego planera przebitek. |
| APP-059 | Częściowo | Dobre testy operacji, timebase, ZIP i kolejek; niepełna macierz kontraktów dostawców i zależności modeli. |
| APP-060 | Częściowo | Przechodzi mały proces API upload→ujęcie→montaż→MP4; brak referencyjnego pełnego procesu książka/stock→AI/TTS→eksport i odtworzenie. |

## Kolejność dalszych napraw

1. Zapisać hash tekstu/języka/profilu przy nagraniu i egzekwować status aktualności w kontroli oraz eksporcie.
2. Powiązać propozycje scenopisarskie z rewizją promptu i odrzucać nieaktualne wyniki.
3. Ujednolicić blokady Generowania i Montażu oraz odtworzyć powiązania faktów przy migracji.
4. Dokończyć profile głosu, dogrywki zdań, przejścia, szablony i napisy; dopiero potem pełny test referencyjnego filmu.
5. Dodać cache zakresów/proxy i pomiary długich projektów na docelowym sprzęcie.

Zmiany UI i obsługi błędu są lokalne. Pozostałe wskazane problemy funkcjonalne pozostają otwarte; audyt nie deklaruje ich naprawy.
