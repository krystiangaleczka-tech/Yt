# DocOS Studio 0.2

Lokalne studio dokumentalne: research → fakty → historia → scenariusz → ujęcia i głos → montaż → publikacja. Interfejs, pliki i modele działają lokalnie; research i połączony model tekstowy korzystają z wybranych usług.

## Instalacja i start

Studio wymaga **Python 3.12+**, Node.js 22.12+ oraz FFmpeg/FFprobe w PATH. Sprawdzone środowisko: macOS 26.3.1, Apple Silicon, 8 GB RAM, Python Studio 3.13.5. Głos ma oddzielnego Pythona 3.11, obrazy i znaczniki słów — 3.12.

```bash
python3 scripts/install_studio.py --run
# Kolejne uruchomienia:
npm start
# Inny port:
npm start -- --port 9000
```

Windows: użyj `python` zamiast `python3`. Domyślne ścieżki interpreterów uwzględniają `Scripts/python.exe`; tego wydania nie przetestowano na Windows. Otwórz http://127.0.0.1:8876. Serwer nasłuchuje wyłącznie lokalnie. `DOCOS_STUDIO_HOME` wybiera katalog danych; domyślnie `.docos-studio/`.

Podstawowy instalator przygotowuje Studio i frontend. Opcjonalne środowiska modeli instalujesz przez [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
python3 scripts/install_studio.py --with-models --run
# Samo rozpoznawanie czasów słów:
python3 scripts/install_studio.py --with-alignment
```

Wagi modeli pobierają się przy pierwszym użyciu. Pliki lock dla serwera, obrazów, głosu i alignera zapisują sprawdzone wersje. Próbkę lektora wgraj w **Narzędzia produkcji → Lektor**. Bez modeli działają pliki własne, redakcja, montaż i eksport.

## Praca nad filmem

1. **Pomysł** — tytuł własny albo 10 propozycji; historia tematów jest wspólna dla kanału, również między odcinkami i w archiwum.
2. **Fakty i research** — twierdzenie, źródło, strona/rozdział, cytat, status i użycia. Zmiana twierdzenia lub źródła cofa jego weryfikację.
3. **Historia** — pytanie, hook, teza i finał; zatwierdzenie wymaga sprawdzonego źródła. Widok różnic pokazuje zmiany od poprzedniego zatwierdzenia.
4. **Scenariusz** — narracje ujęć i pełny tekst. W Narzędziach edytujesz rozdziały/fragmenty, ich cele, zwroty i energię 1–10. Krzywa energii jest planem redakcyjnym.
5. **Generowanie** — obraz z promptu, wyszukanie, biblioteka, plik, schowek lub URL. Wygenerowany wynik staje się wariantem; sam nie zastępuje ręcznego wyboru.
6. **Montaż** — wielościeżkowa oś z klatkami, source_in, trim, split, ripple, grupami, keyframes, przejściami i audio.
7. **Eksport** — kontrola gotowości, podgląd lub MP4, materiały publikacyjne i pakiet projektu.

Tekst zapisuje się po 900 ms bezczynności albo po opuszczeniu pola. Liczby po opuszczeniu pola, gesty po zakończeniu. Nagłówek pokazuje oczekiwanie, zapisywanie lub błąd. Konflikt rewizji chroni nowsze zmiany i wczytuje aktualny stan. Trwałe Cofnij/Ponów obejmuje 40 kroków w każdą stronę; nie usuwa plików z biblioteki.

Zaznaczenie ujęcia jest wspólne dla scenariusza, generowania, montażu i narzędzi. Kolejny start pamięta ostatni projekt i ekran. Projekty można duplikować, archiwizować i otwierać z archiwum.

## Ujęcia i styl

**Narzędzia produkcji → Ujęcia** zawierają 20 formularzy: media, dokument, tytuł, cytat, prasa, podpis osoby, licznik, oś wydarzeń, mapa, diagram, waveform, spektrogram, lupa, split, porównanie, stos, QA, hasło, karty i parallax.

Mapy mają edytowalne bounds, punkty i trasy; podkład Natural Earth działa offline. Diagramy przyjmują węzły i połączenia. Oscylogram i spektrogram wymagają rzeczywistego audio. Parallax wymaga tła i wyciętych warstw PNG z przezroczystością. Nie jest automatycznym wycinaniem obiektów.

Profil kanału zapisuje styl narracji i obrazów, referencje, kolor oraz krój napisów. Wbudowane kroje to Montserrat i Courier Prime z dołączonymi licencjami OFL. Projekt zachowuje migawkę profilu; późniejsza zmiana kanału nie przepisuje wcześniejszych odcinków.

Blokady obejmują całe ujęcie lub osobno narrację, czas i media. Są egzekwowane również dla powiązanych klipów i AI. Przekazanie do montażu jawnie zmienia medium/parametry; generowanie wariantu nie rusza ręcznych cięć i ruchu. Zmiana długości ręcznie pociętego ujęcia wymaga pracy na osi.

## Źródła i książki

| Dostawca | Zakres |
|---|---|
| Wikimedia Commons | Zdjęcia/filmy, warianty, autor, licencja, kolejka pobierania |
| Pixabay, Pexels | Opcjonalny stock po podaniu własnego klucza |
| Open Library | Wyszukiwanie dzieł i wybór konkretnego wydania/ISBN |
| Google Books | Metadane i oznaczenie: katalog, podgląd albo dostępny pełny tekst |
| Crossref | Publikacje/DOI i metadane |
| Własne źródła | PDF, EPUB, HTML, raporty, RSS/Atom, folder i API JSON |

Możesz szukać równolegle w połączonych źródłach, filtrować typ/orientację/licencję i anulować zadanie. Awaria jednego dostawcy nie ukrywa pozostałych wyników. Katalog ani podgląd książki nie oznaczają automatycznie dostępnego pliku lub praw do ilustracji.

Czytnik zachowuje strony PDF i rozdziały EPUB, oryginał oraz datę pobrania. Zaznaczony cytat można dodać do banku z lokalizacją. PDF ma podgląd skanu, OCR i prostokąt wyodrębnienia ilustracji; EPUB listę ilustracji z rozdziałem. OCR wymaga Popplera i Tesseract, najlepiej z językami pol+eng. Wynik OCR/ASR wymaga sprawdzenia.

Własne API obsługują publiczny URL z `{query}` i `{page}`, ścieżkę wyników, mapowanie pól i prywatny nagłówek autoryzacji. Nagłówki nie przechodzą na inny origin przy przekierowaniu. Klucze są w oddzielnym `connections.json` (0600 na Unix), nigdy w eksportach projektu. Test połączenia jest w Ustawieniach.

**Pliki i diagnostyka** importują wskazany folder i opcjonalnie obserwują zmiany. Rejestry `licenses.json` zachowują podpisy. Relink dopasowuje FILE/FILES z DocOS do unikalnych nazw; przy kolizji wybierz materiał ręcznie. Brakujący plik pakietu można odzyskać z identycznej sumy SHA-256.

## Głos i napisy

Profile przygotowują prywatną próbkę 3–120 s do mono 24 kHz i wyrównują głośność. Próbki nie trafiają do ZIP. Parametry, język i słownik wymowy uczestniczą w fingerprintach. Zmiana tych danych oznacza nagranie jako nieaktualne i blokuje finalny eksport do czasu poprawki.

Zdania mają własne warianty i cache; można dograć jedno zdanie i złożyć wybrane nagrania. Wybór całego lektora jest atomową, jawną operacją na ścieżce narracji. Muzyka i efekty mają osobne ścieżki; dostępne są solo, mute, poziom, fades, keyframes i ducking.

Na Macu z pamięcią do 12 GB tryb Auto wybiera CPU dla Chatterbox. MPS na sprawdzonym Macu 8 GB powodował intensywny swap; CPU wygenerował próbę poprawnie, ale generowanie może trwać minuty. Możesz jawnie wybrać urządzenie w profilu lub ustawić `DOCOS_TTS_DEVICE`.

Napisy powstają z rozpoznanych czasów słów (faster-whisper) albo ze zmierzonych długości zdań. Ich granice nie są zgadywane proporcjonalnie do tekstu. Edytor pozwala poprawić pisownię, czas, łączenie i podział po odsłuchu. Mała pewność rozpoznania daje uwagę do sprawdzenia. SRT/VTT uwzględniają trim, speed i położenie nagrania na osi; mogą również trafić na ścieżkę tekstową.

## Podgląd, AI i eksport

Canvas jest roboczym podglądem: używa ograniczonego okna mediów i proxy, a klatki szablonów pochodzą z renderera. **Dokładna klatka** i **Dokładny podgląd** korzystają z tego samego kompozytora co finalny film. IN/OUT wybierają zakres. Wynik ma własną rewizję; późniejsza edycja nie zmienia trwającego zadania. Cache zależy od zakresu, warstw, plików, fontów i ustawień.

Claude CLI działa z pustym zestawem narzędzi; alternatywą jest API zgodne z Chat Completions. Model proponuje JSON. Możesz też skopiować prompt i wkleić JSON lub dawny format Narracja/Shot List. Przyjęcie wymaga zgodnej rewizji. Asystent montażu ma zakres: zaznaczenie, ujęcie, czas albo całość; propozycję można obejrzeć i cofnąć jako jedną serię. Wersje A/B zapisują, porównują, podglądają i przywracają montaż.

Planer przebitek korzysta z narracji fragmentu, banku faktów i profilu kanału, zachowując uzasadnienie. API ma zachowawczy budżet: wpisujesz szacowany koszt wywołania i limit projektu. Studio blokuje przekroczenie; rzeczywisty rachunek pozostaje u dostawcy. Lokalne modele i render nie naliczają opłat API.

Eksporty: MP4 H.264/AAC, JSON, MD, TXT, XLSX, SRT, VTT, opis filmu i użyte atrybucje. XLSX ma edytowalne tabele oraz ukryty manifest bez utraty danych; import odrzuca stare rewizje i formuły. Opis i JSON konkretnego renderu można pobrać z jego migawki, niezależnie od bieżących zmian.

Pakiet ZIP zawiera projekt, warianty A/B, media i manifest sum. Prywatne, brakujące lub zbyt duże pliki są jawnie wymienione jako pominięte. Limit pakietu: 2 GB/2000 plików; pojedynczego przesyłanego medium: 300 MB; JSON/XLSX: 8 MB. JSON zachowuje układ i metadane, lecz nie przenosi plików. Import do nowego projektu nie daje dostępu do starych ścieżek i nie przenosi zatwierdzenia historii.

## Dane, aktualizacja i weryfikacja

Schemat `docos-studio/2` automatycznie odczytuje /1. Stary DocOS/Bloop zachowuje pełne `legacy`, fragmenty, źródłowe opisy i powiązania faktów. Przybliżone mapy/diagramy starego renderera stają się edytowalnymi danymi; nowy wygląd nie jest kopią piksel w piksel.

Instrukcja kopii, aktualizacji i odzyskiwania: [STUDIO_RELEASE.md](STUDIO_RELEASE.md).
Kryteria APP-001–060 i dowody: [STUDIO_IMPLEMENTATION.md](STUDIO_IMPLEMENTATION.md).

```bash
npm run build
.venv-studio/bin/python -m unittest discover -s studio_tests -v
.venv-studio/bin/python -m unittest discover -s docos/tests -v
npm run test:frontend
.venv-studio/bin/python scripts/verify_studio_e2e.py --home /tmp/docos-qa
# Rzeczywiste źródła oraz lokalne modele; bez płatnego modelu tekstowego:
.venv-studio/bin/python scripts/verify_studio_e2e.py --home /tmp/docos-live-qa --live
.venv-studio/bin/python scripts/benchmark_studio.py --output /tmp/docos-benchmark.json
```

CLI Studio korzysta z tego samego serwisu, blokady między procesami i rewizji:

```bash
.venv-studio/bin/python -m studio_core.cli list
.venv-studio/bin/python -m studio_core.cli check PROJECT_ID
.venv-studio/bin/python -m studio_core.cli edit PROJECT_ID operations.json --revision 12
.venv-studio/bin/python -m studio_core.cli backup PROJECT_ID
```

Zewnętrzne konta pozostają zależnością użytkownika. Podczas wdrożenia Claude zwracał limit konta do 28.10.2026; rzeczywistego modelu tekstowego i kluczy Pixabay/Pexels nie zastępowano udawanymi wywołaniami. Kontrakty tych integracji są testowane kontrolowanymi odpowiedziami.

## Wstawki Remotion

W panelu bocznym otwórz **Wstawki animowane** lub kliknij **Dodaj wstawkę** w generowaniu filmu albo montażu.
Moduł zawiera pięć oryginalnych szablonów: animowane zdjęcie, porównanie dwóch zdjęć, wykres słupkowy,
cytat ze źródłem i planszę rozdziału. Wstawki nie wymagają generowania obrazów przez AI.

1. Wybierz szablon. Dla zdjęć najpierw dodaj materiały do biblioteki filmu.
2. Uzupełnij treść, źródło, czas i kolory. Dla zdjęć ustaw przybliżenie, przesunięcie,
   obrót, jasność, nasycenie i rozmycie. W wykresie wpisz własne, sprawdzone dane (do ośmiu słupków).
3. Obejrzyj animację w odtwarzaczu. Zapisz i kliknij **Renderuj klip**.
4. Po ukończeniu zadania wybierz początek na osi czasu i **Dodaj do montażu**.
   Zwykły montaż, miks audio i eksport całego filmu nadal obsługuje FFmpeg.

Podgląd i render używają tego samego komponentu React i animacji liczonych z numeru klatki.
Wyrenderowany MP4 jest osobnym, niezmiennym materiałem. Edycja wstawki nie podmienia samodzielnie
istniejących klipów: wyrenderuj nową wersję i dodaj ją jawnie. Przycisk **Edytuj źródło wstawki**
w inspektorze klipu wraca do edytowalnej definicji. Definicje, źródłowe zdjęcia i rendery są zachowywane
w pakiecie ZIP. Import samego JSON usuwa odniesienia do plików.

### Instalacja silnika renderującego

Wymagany jest Node.js co najmniej 22.12 oraz zależności aplikacji. Pakiety Remotion mają jedną
przypiętą wersję: `4.0.539`. Po aktualizacji aplikacji uruchom:

```bash
npm --prefix apps/studio ci
npm --prefix apps/studio run build
npm --prefix apps/studio run remotion:setup
```

Ostatnia komenda przygotowuje Chrome Headless Shell używany przez renderer; wymaga internetu
przy pierwszym pobraniu i odpowiednich bibliotek systemowych Chromium. Sam podgląd Player działa
w przeglądarce użytkownika. Można wskazać własny zgodny plik wykonywalny przez
`DOCOS_REMOTION_BROWSER` (również dla komendy setup). Renderowanie pozostaje lokalne, bez chmury Remotion.
Pełny instalator `python3 scripts/install_studio.py --run` instaluje podstawowe zależności;
przygotowanie przeglądarki jest osobnym, opcjonalnym krokiem potrzebnym tylko dla wstawek.

**Zmień z AI** przygotowuje propozycję parametrów istniejącej wstawki przez skonfigurowany model
lub prompt do skopiowania i import odpowiedzi JSON. Propozycja trafia do podglądu i wymaga zapisu.
AI nie uruchamia kodu React/JavaScript i może użyć wyłącznie identyfikatorów zdjęć z danego projektu.
Nie ma automatycznej weryfikacji prawdziwości cytatów ani danych liczbowych — sprawdź je ze źródłem.

Czas pojedynczej wstawki: maksymalnie sześćdziesiąt sekund. Szablony są pełnoklatkowe, renderowane
jako H.264 bez przezroczystości i bez ścieżki dźwiękowej; lektor i muzyka są dodawane w montażu.
Nie jest to rigging postaci, rekonstrukcja głębi ani generowanie ruchu twarzy. Animacja zdjęcia
zmienia kompozycję i filtry istniejących pikseli. Dla uzyskania identycznego kroju pisma na różnych
komputerach należy używać tego samego zestawu fontów systemowych.

Remotion podlega własnej licencji: [warunki](https://www.remotion.dev/docs/license)
i [cennik](https://www.remotion.dev/docs/license/pricing). Przed użyciem w większej organizacji lub
udostępnieniem usługi sprawdź uprawnienia licencyjne. Instalacja nie kupuje subskrypcji.

Test integracyjny wszystkich pięciu szablonów oraz eksportu z FFmpeg:

```bash
DOCOS_TEST_REMOTION=1 .venv-studio/bin/python -m unittest studio_tests.test_motion_render -v
```

Wymaga przygotowanego renderera i przeglądarki. CI wykonuje go z Node 22 i Pythonem 3.12.
