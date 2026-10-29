# DocOS Studio 0.2 — aktualizacja i odzyskiwanie

## Kopia przed aktualizacją

Zakończ lub anuluj aktywne zadania. Dla każdego ważnego filmu pobierz w Eksportach **Pakiet ZIP**, sprawdź manifest pominiętych plików i zachowaj archiwum poza katalogiem aplikacji. ZIP przenosi projekt, media i zapisane wersje A/B. Nie przenosi prywatnych próbek głosu, kluczy, kolejki ani pełnej historii cofania.

Po zatrzymaniu serwera skopiuj cały katalog `.docos-studio` (albo własny `DOCOS_STUDIO_HOME`) do osobnego katalogu kopii. Ta kopia zawiera również `jobs.sqlite3`, pliki WAL/SHM, `job-inputs`, historię, profile i prywatną konfigurację. Traktuj ją jako prywatną; nie dodawaj do Git. Zachowaj również własne pliki wskazane zmiennymi `DOCOS_VOICE_REF` i `DOCOS_*_PYTHON`, jeśli znajdują się poza katalogiem danych.

Nie kopiuj działającej bazy SQLite pojedynczym poleceniem kopiującym tylko `jobs.sqlite3`. Zatrzymanie aplikacji i kopia całego katalogu eliminują problem niepełnej kopii WAL.

## Aktualizacja kodu

W terminalu, w katalogu repozytorium, po zapisaniu własnych zmian:

```bash
git status
git fetch origin
git pull --ff-only
python3 scripts/install_studio.py
npm start
```

Windows: `python` zamiast `python3`. Instalator nie zmienia materiałów projektu. Jeśli korzystasz z modeli i aktualizujesz ich środowiska, użyj `--with-models`; wymaga to uv i może pobrać zależności. Uruchomienie po aktualizacji: http://127.0.0.1:8876. Odśwież otwartą kartę przeglądarki, aby wczytać nowy frontend.

Schemat `docos-studio/2` odczytuje starszy `/1`. Pierwszy zapis utrwala nowy schemat i przenosi dawne wewnętrzne migawki cofania do katalogu `history`. Powrót do starego kodu wymaga przywrócenia odpowiadającej mu kopii danych, nie tylko przełączenia commita.

## Odtworzenie filmu i całego środowiska

- **Jeden film:** Projekty → import ZIP. Powstaje nowy identyfikator projektu. Sprawdź pominięcia, media, wersje A/B i kontrolę eksportu. Zatwierdzenie historii jest celowo cofnięte; zatwierdź ją po kontroli źródeł.
- **Pełne środowisko:** zatrzymaj serwer, zachowaj aktualny katalog danych jako dodatkową kopię i odtwórz cały poprzedni katalog danych. Uruchom zgodną wersję kodu.
- **Brakujące media:** wskaż folder w Narzędziach produkcji → Pliki i diagnostyka. Import/relink rozpoznaje identyczne sumy SHA-256 oraz unikalne dawne FILE/FILES. Kolizje nazw wymagają jawnego wyboru.
- **Cofnięcie jednej zmiany:** Cofnij/Ponów jest trwałe po restarcie. Historia obejmuje do 40 kroków w każdą stronę; nie zastępuje zewnętrznej kopii.
- **Powrót do montażu A/B:** wybierz zapisaną wersję, obejrzyj różnice i podgląd, a następnie przywróć. Operacja szanuje bieżące blokady i sama podlega cofaniu.

## Zadania po przerwaniu

Po ponownym uruchomieniu zadania QUEUED/RUNNING/CANCEL_REQUESTED dostają status INTERRUPTED. Nie są automatycznie wykonywane ani naliczane ponownie. Przycisk **Ponów** tworzy nowe zadanie i zachowuje poprzedni wpis.

Render, generowanie, wstawka Remotion, klatka, proxy, OCR, składanie zdań i rozpoznawanie czasów zachowują wejściową migawkę. Ponowienie wyszukiwania, pobrania lub importu folderu odczytuje zapisane żądanie; zewnętrzny serwis lub folder może już zawierać inne dane. Render nie przestawia się sam na aktualny montaż. Wyniki generowania trafiają do wariantów, a nie samowolnie na oś.

Jeśli tekst, nagranie lub źródło zmieniło się podczas zadania, kontrola rewizji/fingerprintu odrzuca nieaktualne przypisanie. Wtedy uruchom narzędzie ponownie dla aktualnej wersji. Stare zadania z wydania bez zapisanego żądania mogą wymagać ponownego uruchomienia z właściwego ekranu.

Anulowanie zatrzymuje worker i pozostawia zakończone, zaimportowane media w bibliotece. Nieudany wynik nie jest oznaczany jako poprawny film. Cache jest odtwarzalny i nie jest jedyną kopią oryginałów.

## Diagnostyka

**Narzędzia produkcji → Pliki i diagnostyka** sprawdzają FFmpeg/FFprobe, Poppler, Tesseract i import bibliotek oddzielnych środowisk. Poprawny import bibliotek nie oznacza, że pobrano wszystkie wagi. Gotowość modelu potwierdza próbne generowanie.

| Objaw | Działanie |
|---|---|
| Brak MP4 lub odczytu mediów | Zainstaluj FFmpeg wraz z FFprobe i sprawdź PATH terminala uruchamiającego Studio. |
| PDF bez podglądu/OCR | Zainstaluj Poppler, Tesseract oraz języki OCR, np. pol+eng. |
| Niekompletne środowisko | Ponów instalator z właściwym plikiem lock; nie mieszaj Pythona Studio, TTS i alignera. |
| Brak wag modelu | Pierwsze generowanie wymaga Internetu i miejsca na wagi; szczegóły błędu są w zadaniu. |
| Silny swap na Macu 8 GB | Lektor Auto wybiera CPU. Generowanie może trwać minuty; jawne MPS może wyczerpać pamięć. |
| Nieaktualny głos | Wygeneruj/wybierz wariant zgodny z tekstem, językiem, profilem i wymową; potem ponów napisy. |
| HTTP 409 | Wczytaj aktualną rewizję, przejrzyj zmiany i przygotuj nową propozycję. |
| Limit Claude lub błąd klucza | Sprawdź konto w Ustawieniach. Można nadal korzystać z ręcznie wklejanego, walidowanego JSON. |
| Timeout Remotion na macOS | Przy pierwszej instalacji wykonaj remotion:setup; jeśli pulpit jest zablokowany/niedostępny, odblokuj sesję i ponów. Na tym Macu po przywróceniu pulpitu pięć szablonów przeszło poprawnie. |
| Port 8876 zajęty | Zakończ poprzedni serwer albo uruchom `npm start -- --port 9000`. |

Serwer, frontend i modele sprawdzono na macOS z Apple Silicon 8 GB. Ścieżki Windows są obsłużone w kodzie, lecz nie przeprowadzono instalacji na osobnym komputerze Windows. To lokalna aplikacja uruchamiana instalatorem/skryptem; wydanie nie zawiera podpisanego instalatora desktopowego.

Dowody testów i ograniczenia wydania: [STUDIO_IMPLEMENTATION.md](STUDIO_IMPLEMENTATION.md).
