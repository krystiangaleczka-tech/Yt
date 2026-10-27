# Plan APP-001–060 — wdrożenie Studio 0.2

Stan: 27.10.2026, gałąź `codex/docos-studio-20261026`. Podstawa: plan v2 z [rozmowy Projects/Yt](https://chatgpt.com/g/g-p-6adf28f1a0448191bc6f743c798b95df-yt/c/6adf293e-3f38-83ed-be04-ce446ec13b4d). [Audyt z 26.10](audits/2026-10-26-studio-review.md) opisuje historyczny stan pierwszej wersji.

Wszystkie 60 pozycji mają implementację w kodzie i interfejsie. Nie oznacza to 60 osobnych testów z rzeczywistymi usługami ani pełnej certyfikacji dostępności. Ograniczenia weryfikacji pozostają jawne: limit konta Claude, brak kluczy stockowych, brak komputera Windows i ograniczony zakres ręcznego audytu dostępności.

## Wyniki

| Kontrola | Wynik |
|---|---|
| Backend Studio | **83 potwierdzone testy**: 82 szybkie (15,922 s; osobny render pominięty) + 1 rzeczywisty test pięciu szablonów Remotion i końcowego eksportu (17,483 s). |
| Stare DocOS | **18/18**, 1,276 s; również XLSX, bez pominiętych testów. |
| Frontend | **7/7**: czas, keyframes, propozycje, podział animacji i kontrast palet. |
| Build | TypeScript i Vite przechodzą; frontend 0.2.0. |
| Import Bloop v4 | 12 fragmentów, 53 ujęcia, 22 fakty, 139 aktywnych powiązań; oryginał zachowany. |
| Katalog ujęć | Test renderuje wszystkie 20 typów do jednego filmu, z rzeczywistym obrazem/audio. |
| Rzeczywisty E2E | EPUB Gutenberg, wydanie Open Library, obraz Commons, lokalne SD 1.5, Chatterbox i faster-whisper; H.264/AAC 640×360, **10,266 s**, eksporty i ponowny import ZIP. |
| Napisy referencji | 10 słów; pisownia poprawiona względem narracji, zmierzone czasy zachowane. Drugi eksport i ZIP z 2 wersjami A/B; kontrola bez uwag. Nie wykonano niezależnej oceny jakości głosu odsłuchem. |
| 500 ujęć/500 klipów/40 kroków cofania | Odczyt p95 **27,73 ms**, zapis p95 **247,36 ms** na Macu 8 GB. Pomiar serwisu i dysku, bez przeglądarki i modeli. |
| UI | Safari: wybrane nowe ekrany przy **390/768/1024/1440×900**. Sprawdzono produkcję, lektora, A/B, czytnik EPUB, pola napisów i widoczny focus, mobilny montaż oraz edytor wstawek w obu motywach. Utworzono, zapisano i wyrenderowano wstawkę z UI. Przywrócono ciemny motyw. To nie jest pełna certyfikacja WCAG ani test każdej kombinacji ekran/szerokość. |

[Pomiar wydajności](benchmarks/2026-10-27-studio-mac8gb.json) · [Raport produkcyjny](audits/2026-10-27-studio-production-check.md) · [Uruchamianie i polecenia testów](STUDIO.md) · [Aktualizacja i odzyskiwanie](STUDIO_RELEASE.md).

## Macierz realizacji

„Test” potwierdza wskazane zachowanie, nie każdą kombinację ustawień. „Kontrakt” oznacza kontrolowane odpowiedzi dostawcy bez płatnego żądania. Nazwy modułów wskazują główne miejsca implementacji.

| ID | Zaimplementowany rezultat | Dowód / granica weryfikacji |
|---|---|---|
| APP-001 | Migracja Bloop: fragmenty, szablony, narracja, fakty, aktywne powiązania i legacy; relink FILE/FILES. | Test rzeczywistego Bloop v4; models/templates/service. Oryginalne media wymagają plików lokalnych. |
| APP-002 | Schemat docos-studio/2, migracja /1, typowane modele i walidacja 20 szablonów. | Test migracji i render katalogu; studio_core/models.py i templates.py. |
| APP-003 | Wspólny ProjectService dla GUI/CLI, blokada między procesami, atomowa kontrola rewizji. | service/locking/cli; testy konfliktów i trwałości. |
| APP-004 | Kolejka SQLite, postęp/anulowanie/INTERRUPTED, żądania i migawki ponowień; oddzielne kolejki sieci/modeli. | Test restartu i ponowienia klatki starej rewizji; test researchu podczas zajętego modelu. |
| APP-005 | Grafitowy i jasny motyw, focus, etykiety, klawiatura, stany zapisu i błędów. | Pomiar palet: tekst ≥4,5:1, focus ≥3:1. Ograniczenie audytu UI opisane wyżej. |
| APP-006 | Siedem etapów, połączone Źródła/Generowanie/Montaż, wspólne ujęcie i zapamiętany ekran. | App/context i responsywne CSS; ręczny przegląd wybranych ekranów 390/768/1024/1440 px oraz reset przewijania po zmianie strony. |
| APP-007 | Projekty/kanały: tworzenie, import, duplikacja, archiwum i migawka profilu odcinka. | service, Projekty, Production → Kanał. |
| APP-008 | Autosave tekstu po 900 ms/blur, kolejka CAS, błędy i trwałe Cofnij/Ponów do 40 kroków. | Test starej historii i cofania po restarcie; store/context/components. |
| APP-009 | 10 propozycji tematów i historia tytułów całego kanału, także archiwum. | writer i service.channel_titles; generowanie zależy od konta AI. |
| APP-010 | Statusy faktów, cytat/lokalizacja, data kontroli i mapa użyć. | Test zmiany dowodu i cofnięcia weryfikacji; models/quality i redakcja. |
| APP-011 | Zatwierdzenie historii zależne od treści/dowodów, migawka i różnice od zatwierdzenia. | store, /story/diff, Editorial; testy unieważnienia zatwierdzeń. |
| APP-012 | Prompt, JSON i dawny Narracja/Shot List z wejściową rewizją. | writer/API; test odrzucenia poprzedniej rewizji. |
| APP-013 | Rozdziały/fragmenty, cel, narracja, zwrot, energia, dynamika, typologia i krzywa energii. | Beat i Production → Fragmenty. Krzywa jest planem redakcyjnym. |
| APP-014 | Pełna narracja i fragmenty/ujęcia z faktami; fingerprint dowodów i uwagi o aktualności. | writer/freshness, Editorial/Production; test zmienionego dowodu. |
| APP-015 | AI jednego fragmentu i planer z wejściową rewizją oraz sprawdzonymi faktami. | Walidacja JSON, rewizji, blokad i dowodów; model live ograniczony limitem konta. |
| APP-016 | Aktualność tekstu, języka, wymowy, profilu, obrazu i dowodów; porównanie wersji. | freshness/service; testy starego głosu i zmiany dowodów. |
| APP-017 | Identyfikacja mediów sumą, pochodzenie, duplikaty, biblioteka i relink. | Test naruszonego oryginału i historycznych mediów A/B; media/service/Library. |
| APP-018 | Commons: warianty/prawa, kolejka pobierania, błędy i ponowienia. | Rzeczywisty obraz Commons w E2E i eksport użytych atrybucji. |
| APP-019 | 20 formularzy ujęć, parametry, miniatury i render. | Test wszystkich typów oraz aktualności miniatur; templates/Production. |
| APP-020 | Sugestie i planer z uzasadnieniem, wyszukanie dla ujęcia, użycia, jawny wybór wariantu. | Generation/Library i zapisane planning_reason. |
| APP-021 | Storyboard: dodanie, duplikacja, usuwanie i kolejność myszą/przyciskami klawiatury. | scene_operation, Generation/Production; atomowe mutacje i blokady. |
| APP-022 | Czas i powiązane klipy; blokady całości, narracji, czasu i mediów. | Test blokady sceny wobec ręcznej edycji/AI; store/operations. |
| APP-023 | Roboczy podgląd, dokładna klatka i zakres, wspólne zaznaczenie i rewizja wyniku. | Preview/Timeline/API; test prawdziwej klatki i migawki po restarcie. |
| APP-024 | Mapy z bounds/punktami/trasami, diagramy i Natural Earth offline. | Render mapy/diagramu w katalogu. Dawne szkice geograficzne oznaczone jako przybliżone. |
| APP-025 | Prywatne profile, próbka 3–120 s, mono 24 kHz i normalizacja. | voices i Production → Lektor; próbki pominięte w ZIP. |
| APP-026 | Chatterbox, język/konfiguracja, fingerprint i cache zdań. | Rzeczywisty polski WAV w E2E; na Macu 8 GB CPU, czas liczony w minutach. |
| APP-027 | Wymowa, zdania/warianty, dogrywka zdania i składanie z pomiarami. | voice_worker/audio i panel Lektor; cache z rzeczywistych wejść/próbki. |
| APP-028 | Narracja/muzyka/SFX, waveform, solo/mute, poziomy, fades, keyframes i ducking. | Timeline/render/audio; rzeczywisty miks AAC i test aktywnych ścieżek napisów. |
| APP-029 | Migawki, cache zakresów, anulowanie i walidacja strumieni/długości filmu. | Test selektywnego cache, naruszonego oryginału i E2E. |
| APP-030 | MP4/JSON/MD/TXT/XLSX/opis/atrybucje oraz eksport konkretnej migawki renderu. | Test bezstratnej edycji XLSX i kompletny E2E eksportów. |
| APP-031 | Zmierzone słowa/zdania, edytor pisowni/czasu, split/merge, SRT/VTT i tekst na osi. | Rzeczywiste ASR; test trim/speed i starego głosu; Captions/align_worker/exports. |
| APP-032 | ZIP: manifest sum, media i A/B; jawne pominięcia prywatnych/dużych/brakujących plików. | Test prywatności, sum i historycznych mediów; rzeczywisty ZIP/reopen. |
| APP-033 | Powtarzalny E2E, pomiary kontrastu i wydajności, regresje API/renderu. | verify_studio_e2e/benchmark_studio, testy i ręczny przegląd nowych ekranów. Zakres kontroli UI opisany powyżej; bez pełnej certyfikacji WCAG. |
| APP-034 | Instalator/start, osobne locki modeli i diagnostyka narzędzi/importów. | install_studio/studio-start/diagnostics; rzeczywiste środowiska działają na tym Macu. |
| APP-035 | Claude CLI bez narzędzi albo zgodne API, test połączenia i błędy konta. | Testy auth/limitu, ręczny JSON. Live: usage_limit_reached do 28.10.2026 10:00. |
| APP-036 | Kopia, aktualizacja, rollback i odzyskiwanie projektów/zadań. | STUDIO_RELEASE.md; ZIP/reopen, trwała historia i ponowienie po restarcie w testach. |
| APP-037 | Rejestr możliwości źródeł, test połączenia, prywatne klucze i diagnostyka. | Connectors/Settings; test nagłówków i origin przekierowań. |
| APP-038 | Równoległe źródła, filtry, postęp, częściowe błędy i anulowanie. | Test wyniku mimo awarii dostawcy i niezależności kolejki; /search/Sources. |
| APP-039 | Opcjonalne Pixabay/Pexels: klucze, warianty, prawa i pobrania. | Kontrakty bez płatnych żądań; rzeczywiste klucze użytkownika nie były dostępne. |
| APP-040 | Wydanie/ISBN Open Library; katalog/podgląd/pełny tekst Google Books; czytnik i cytaty. | Żywe wydanie Open Library oraz kontrakt poziomów dostępu; bez obchodzenia praw wydawcy. |
| APP-041 | PDF/EPUB: oryginały, strony/rozdziały, OCR, skany i ilustracje. | Rzeczywisty OCR skanu PDF, pochodzenie ilustracji EPUB i żywy EPUB w E2E. |
| APP-042 | HTML/raport/DOI/RSS/Atom, metadane/daty/oryginały i cytaty. | Kontrakt błędnego feedu i test cytatu odrzucający zmyślony tekst; media/Connectors/SourceReader. |
| APP-043 | Import/obserwowanie folderu z licencjami; własne API z nagłówkami i paginacją. | /folder, watcher, kontrakt prywatnych nagłówków/strony. Folder jest ustawieniem lokalnym. |
| APP-044 | Generowanie: prompt, szukanie, medium, ruch, czas i narracja. | Generation/Production, wspólny zapis i rzeczywiste generowanie lokalne. |
| APP-045 | Plik, drag/drop, schowek obrazu/pliku i URL z pochodzeniem. | Komponent importu i API mediów; uprawnienia schowka zależą od przeglądarki. |
| APP-046 | SD 1.5: seed/rozmiar/steps/prompt/styl i warianty z parametrami. | Rzeczywisty PNG w E2E; wynik nie zastępuje sam wybranego medium. |
| APP-047 | Pan/zoom/keyframes, crop, lupa, maska prostokątna i parallax PNG. | Render wszystkich typów; parallax wymaga przygotowanych przezroczystych warstw. |
| APP-048 | Jawne przypisanie medium/głosu i aktualizacja powiązań bez niszczenia ręcznych cięć/ruchu. | to-timeline, voice/select i service.patch; operacje atomowe i blokady. |
| APP-049 | Osobne ID, całkowite klatki, niezależne source_in i wymierny fps. | Test ułamkowego fps i rzeczywistego czasu renderu; models/operations. |
| APP-050 | Wielościeżkowy trim/split/ripple/grupy/snap i podział interpolowanych keyframes. | Testy grupy i ciągłości animacji; frontend także sprawdza propozycję split. |
| APP-051 | Obraz/tekst/warstwy/maski/ruch/przejścia w jednym dokładnym kompozytorze. | Test przenikania i zakresu; render/templates. Canvas pozostaje podglądem roboczym. |
| APP-052 | Proxy z proporcjami, dokładna klatka i IN/OUT, etykieta rewizji. | API/Timeline; test klatki po restarcie. |
| APP-053 | Ręczna edycja i AI: wspólne atomowe operacje, blokady i cofanie. | E2E przyjętego JSON i regresje blokad; ProjectService/operations. |
| APP-054 | AI: całość/zaznaczenie/ujęcie/czas, ograniczenia, różnice i podgląd. | Walidacja rewizji/zakresu/blokad; assistant/Timeline. Live zależy od limitu konta. |
| APP-055 | A/B: zapis, różnice, podgląd, przywrócenie i historyczne media. | Test ZIP z medium nieobecnym w bieżącej wersji; service/Production. |
| APP-056 | Cache zakresów zależny od źródeł/klipów/warstw/ustawień/fontów/kodu. | Test zmiany jednego zakresu i wykrycia zmiany oryginału mimo cache. |
| APP-057 | Gotowość, stare/brakujące dane, jawne uwagi, szacunki i limity kosztu/zadań/czasu. | Test blokady przed API; quality/budget/Exports. Koszt jest rezerwacją szacunku. |
| APP-058 | Profil stylu/font/kolor/referencje i planer przebitek z faktami/uzasadnieniem. | Kanały, planner i provenance; obrazy uwzględniają styl w promptach/hashach. |
| APP-059 | Regresje dostawców, książek, rewizji, blokad, czasu, animacji, cache, anulowania i portabilności. | 83 Studio (w tym rzeczywisty Remotion) + 18 DocOS + 7 frontend; bez płatnych usług. |
| APP-060 | Książka/stock → dowód → lokalne media/głos/ASR → montaż → eksporty → ZIP/reopen. | Rzeczywisty E2E. Operacje AI z jawnego JSON; limit uniemożliwił odpowiedź modelu tekstowego. |

## Ograniczenia rzeczywistego sprawdzenia

- Claude było zalogowane, lecz zwracało limit do 28.10.2026 10:00 Europe/Warsaw. Fixture nie jest opisywane jako odpowiedź działającego modelu.
- Pixabay/Pexels sprawdzono kontraktami; bez kluczy nie ma potwierdzenia działania konta użytkownika.
- MPS przy 8 GB powodował silny swap. Auto wybiera CPU. Około 202 s to wznowiony etap głosu; 224 s dotyczy wznowionego E2E z istniejącym obrazem i źródłami, bez pierwszej instalacji/pobierania wag.
- Nie przeprowadzono pełnego audytu WCAG, każdej kombinacji ekran/szerokość, instalacji Windows ani każdej kombinacji szablonów/warstw/kodeków. Pomiar palet nie zastępuje audytu całego UI.
- Próbki głosu, nagrania i klucze nie są commitowane. Media i ZIP pozostają w lokalnym katalogu QA lub danych aplikacji.

## Scalenie aktualnej gałęzi

Zachowano zdalne commity Remotion bb931f9 i 3b429f5. Nowy moduł korzysta z budżetu AI i wejściowych rewizji; ponowienia mają migawkę, a atrybucje filmu uwzględniają zdjęcia wewnątrz wyrenderowanych wstawek. Dodano regresje tych połączeń. W pierwszej próbie bez dostępnego okna/sesji pulpitu macOS renderer zgłaszał timeout. Po udostępnieniu pulpitu ta sama domyślna konfiguracja przeszła wszystkie pięć szablonów i eksport końcowy; dodano wskazówkę diagnostyczną dla tego błędu. Nie zmieniano zablokowanej sesji ani zabezpieczeń komputera.
