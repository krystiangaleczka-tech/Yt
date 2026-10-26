# DocOS Studio

Lokalna aplikacja do tworzenia narracyjnych dokumentów. React + TypeScript, FastAPI i kompozytor FFmpeg.
Interfejs i dane projektu są lokalne. Research oraz polecenia do połączonego modelu korzystają z usług zewnętrznych.

## Uruchomienie

Wymagania: Python 3.11+ (zalecany 3.12), Node.js 22.12+ i `ffmpeg` oraz `ffprobe` w PATH.
Kod i renderer sprawdzono w Linux x86_64. macOS/Windows i GPU wymagają testu na docelowym komputerze.

```bash
python3 scripts/install_studio.py --run
# Windows: python scripts/install_studio.py --run
```

Otwórz **http://127.0.0.1:8876**. Instalator nie pobiera modeli TTS ani Stable Diffusion.
Pierwszy start tworzy edytowalny przykład „Głos oceanu” z czterema lokalnymi ilustracjami.
To przykład interfejsu, nie materiał badawczy. Nagranie lektora trzeba dodać lub wygenerować.

Kolejny start: `.venv-studio/bin/python -m studio_api`.
Windows: `.venv-studio\Scripts\python -m studio_api`.
Serwer nasłuchuje wyłącznie na `127.0.0.1`; inny port: `--port 9000`.
`DOCOS_STUDIO_HOME` zmienia katalog danych; domyślnie `.docos-studio/` w repozytorium.

## Przepływ pracy

1. **Pomysł**: własny tytuł lub dziesięć propozycji AI. Historia tytułów w projekcie wyklucza powtórzenia.
2. **Fakty**: twierdzenia, publikacja, URL, strona/sekcja, notatka i ręcznie ustalany status weryfikacji.
3. **Historia**: pytanie, hook, teza, komplikacja, kontrargument i finał; zatwierdzenie przed scenariuszem AI.
4. **Scenariusz**: narracja ujęć, audyt długości, orientacyjny czas i czysty tekst lektora.
5. **Generowanie**: prompt lub wyszukanie, import/wklejenie, materiał, ruch, czas i narracja danego ujęcia.
6. **Montaż**: wielościeżkowa sekwencja; ręczne zmiany i propozycje AI we wspólnym modelu.
7. **Eksport**: lista braków, dokładny podgląd, MP4, JSON lub ZIP z mediami.

Pola tekstowe zapisują się po opuszczeniu pola. Oś czasu zapisuje się po zakończeniu gestu lub zmianie parametru.
Każdy zapis wymaga aktualnej rewizji. Konflikt nie nadpisuje nowszych danych; zachowaj własną niezapisaną treść
i odśwież projekt. Zmiana tytułu, karty lub faktów cofa zatwierdzenie historii.

## Źródła

| Połączenie | Dostępne działanie |
|---|---|
| Wikimedia Commons | Zdjęcia i filmy, podgląd, pobranie, autor i metadane licencji |
| Pixabay | Zdjęcia i stockowe filmy po wpisaniu klucza API |
| Pexels | Opcjonalne zdjęcia i filmy z posiadanym dostępem API |
| Open Library | Katalog książek, autorzy, wydania, ISBN i link do źródła |
| Google Books | Katalog, identyfikatory i dostępne podglądy |
| Crossref | Publikacje, DOI, metadane i link do oryginału |
| Własne | Publiczne API JSON, URL stron, PDF, EPUB, TXT i MD |

Wyniki są buforowane przez dobę. Katalog książek nie daje automatycznie pełnego tekstu ani praw do okładki.
PDF zachowuje numery stron, EPUB ścieżki rozdziałów. Skany bez tekstu wymagają obejrzenia oryginału; OCR jest poza wydaniem.
Pliki można wybierać wielokrotnie; aplikacja nie obserwuje automatycznie folderów na dysku.

Własny adapter przyjmuje publiczny URL z `{query}`, ścieżkę do tablicy, np. `data.results`,
i mapowanie `{"title":"name","url":"source","download_url":"file","thumbnail":"preview"}`.
Własne API w tej wersji nie otrzymują dodatkowych nagłówków autoryzacyjnych.

Klucze w Ustawieniach zapisują się osobno w `connections.json` (na Unix prawa `0600`),
nie trafiają do eksportów projektu ani gita. Odczyt ustawień nie zwraca kluczy.
Można też używać `DOCOS_PIXABAY_KEY`, `DOCOS_PEXELS_KEY`, `DOCOS_AI_KEY`, `DOCOS_AI_BASE_URL`, `DOCOS_AI_MODEL`.
Zmienne środowiskowe mają pierwszeństwo przed ustawieniami aplikacji.

## Generowanie i lektor

Wybierz Prompt AI, Z internetu, Własny plik lub Biblioteka. Obraz można wkleić przez Ctrl+V/Cmd+V,
gdy przeglądarka udostępnia plik. Wideo można wgrać lub pobrać z bezpośredniego URL; schowek filmów zależy od systemu.
Link do strony jest importowany jako źródło tekstowe. Limity: materiał 300 MB, projekt JSON 8 MB, ZIP 2 GB.

Presety: kadr statyczny, przybliżenie, oddalenie i panoramy. Notatka o ruchu pozostaje wskazówką w planie,
nie jest programem animacji. Generowanie wideo z promptu wymaga dalszego adaptera; ten model tworzy obrazy.
Dokładną animację ustawia się keyframes w Montażu.

```bash
export DOCOS_IMAGE_PYTHON="$PWD/pilot/.venv/bin/python"
export DOCOS_TTS_PYTHON="$PWD/pilot/.venv-tts/bin/python"
export DOCOS_VOICE_REF="$PWD/pilot/assets/ref_clean.wav"
.venv-studio/bin/python -m studio_api
```

Środowisko obrazów: torch i diffusers. TTS: chatterbox-tts, torch, numpy i soundfile; patrz istniejące
`requirements-render.txt` i `requirements-tts.txt`. Windows może wskazywać `Scripts/python.exe`.
Workery wybierają CUDA, MPS albo CPU. Pierwsze wywołanie może pobierać modele i wymagać autoryzacji dostawcy.
API nie ładuje modeli przy starcie. Jedno ciężkie zadanie działa naraz.
Generowanie zapisuje wariant z promptem, językiem i rewizją wejścia; wyboru dokonuje użytkownik.
Po wybraniu nagrania lektora czas ujęcia jest zmierzony. Zastosowanie w montażu jest jawne.
Odsłuch tekstu w przeglądarce nie tworzy pliku audio do eksportu.

## Montaż

- Obraz, nakładki, tekst, lektor, muzyka i efekty na osobnych ścieżkach.
- Przesuwanie, przycinanie, podział, duplikowanie, usuwanie i zamykanie luki na wybranej ścieżce.
- Przyciąganie do kursora i krawędzi; strzałki przesuwają o klatkę, Shift+strzałka o sekundę.
- Początek na osi i początek w pliku są niezależne. Czas jest liczbą całkowitych klatek.
- Pozycja, skala, obrót, krycie, prędkość, głośność, wejścia/wyjścia i liniowe keyframes.
- Blokady ścieżek i klipów, wyciszenia, cofanie/ponawianie ostatnich czterdziestu zmian także po restarcie.

Asystent korzysta z API zgodnego z Chat Completions lub zalogowanego `claude` CLI, uruchamianego bez narzędzi.
Można też skopiować prompt, wkleić JSON z własnego AI, sprawdzić propozycję, pokazać ją na osi i zastosować.
Seria jest jedną zmianą w historii. Propozycja jest związana z rewizją i zaznaczeniem oraz respektuje blokady.
Bez timestampów słów asystent nie powinien zgadywać cięcia przy słowie — podaj konkretny zakres czasu.

Canvas to podgląd roboczy. Dokładny podgląd i eksport korzystają z tego samego grafu FFmpeg.
Font, synchronizacja, dekodowanie i miks przeglądarki mogą się różnić; oceniaj dokładny render przed publikacją.
Audio filmu nie jest automatycznie mieszane ze ścieżką obrazu. API obsługuje wideo na ścieżce audio;
interfejs biblioteki dodaje filmy jako obraz. Przy podziale klipu z keyframes usuń wcześniej punkty.
Przesunięcia po usunięciu dotyczą wyłącznie wybranej ścieżki i respektują dalsze blokady.
Katalog przejść, grupy, waveformy, ducking i wyrównanie słów pozostają rozszerzeniami.

## Dane i przenoszenie

JSON jest źródłem prawdy, SQLite przechowuje kolejkę. Zapis jest atomowy z historią.
Media identyfikuje hash treści i pochodzenia. Zadania używają migawki wejścia; późniejsza edycja jej nie zmienia.
Restart oznacza niedokończone zadania jako INTERRUPTED; można zlecić je ponownie.

ZIP przenosi manifest i media, sprawdza sumy kontrolne, rozmiary i nazwy plików.
Sam JSON przenosi treść, a import czyści niedostępne odwołania do mediów i cofa zatwierdzenie historii.
Stary DocOS pozostaje w `legacy`, również z nieznanymi polami. Nowy renderer nie emuluje automatycznie
wszystkich starych szablonów, np. map i spektrogramów. Dawne CLI i renderer nadal są dostępne.

## Development

```bash
npm run dev
# Po instalacji zależności; Vite localhost:3000, API 127.0.0.1:8876
npm run build
.venv-studio/bin/python -m unittest discover -s studio_tests -v
python3 -m unittest discover -s docos/tests -v
```

`DOCOS_API_PORT` wybiera port API w development; `PORT` lub `--port` port frontendu.
Testy renderu potrzebują FFmpeg. Testy adapterów używają kontrolowanych odpowiedzi, nie realnych kluczy.

## Zakres wydania

Działający fundament lokalnego studia; nie obejmuje jeszcze wszystkich sześćdziesięciu zadań planu.
Do dalszej pracy: kontrola UI i dostępności na docelowym komputerze, testy długich projektów,
instalator desktopowy, stare szablony, OCR, wyrównanie słów, wspólne profile kanałów,
wersje A/B oraz cache modeli i zakresów renderu. Konta źródeł i modele konfiguruje użytkownik.
