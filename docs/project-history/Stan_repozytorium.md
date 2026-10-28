# Stan repozytorium przy archiwizacji

Sprawdzenie: **28 października 2026**. Repozytorium: [krystiangaleczka-tech/Yt](https://github.com/krystiangaleczka-tech/Yt). Widoczność: publiczna. Domyślna gałąź: `main`.

## Kod zapisany przed dodaniem archiwum

| Gałąź | Odczytany HEAD | Zakres |
|---|---|---|
| `main` | `c27da6c1f9400ad8494f84784139d07456ef16ee` | Bazowy DocOS i projekt Bloop |
| `codex/documentary-topics-story-lock-20261026` | `2964df4bc9935329dab537c382ffed2599e667fd` | Generator Documentary i Story Lock |
| `codex/docos-studio-20261026` | `378913567116f0a0ae86d34df33f060b58f2f420` | DocOS Studio, Remotion, produkcja i montaż |

- [PR #1](https://github.com/krystiangaleczka-tech/Yt/pull/1): otwarty, bez draftu, baza `main`.
- [PR #2](https://github.com/krystiangaleczka-tech/Yt/pull/2): otwarty draft, baza `codex/documentary-topics-story-lock-20261026`.

PR-y nie były scalone podczas sprawdzania. Kod Studio nie jest przez to automatycznie obecny na `main`. Ta archiwizacja dodaje dokumentację do `main`; nie scala PR-ów i nie zmienia ich kodu.

## Najważniejsze miejsca kodu Studio

Poniższe linki wskazują odczytany, stały commit Studio:

- [Interfejs](https://github.com/krystiangaleczka-tech/Yt/tree/378913567116f0a0ae86d34df33f060b58f2f420/apps/studio/src)
- [API](https://github.com/krystiangaleczka-tech/Yt/tree/378913567116f0a0ae86d34df33f060b58f2f420/studio_api)
- [Silnik](https://github.com/krystiangaleczka-tech/Yt/tree/378913567116f0a0ae86d34df33f060b58f2f420/studio_core)
- [Oś czasu i render](https://github.com/krystiangaleczka-tech/Yt/tree/378913567116f0a0ae86d34df33f060b58f2f420/studio_timeline)
- [Workery](https://github.com/krystiangaleczka-tech/Yt/tree/378913567116f0a0ae86d34df33f060b58f2f420/studio_workers)
- [Konektory źródeł](https://github.com/krystiangaleczka-tech/Yt/tree/378913567116f0a0ae86d34df33f060b58f2f420/studio_connectors)
- [Instrukcja Studio](https://github.com/krystiangaleczka-tech/Yt/blob/378913567116f0a0ae86d34df33f060b58f2f420/docs/STUDIO.md)
- [Macierz implementacji](https://github.com/krystiangaleczka-tech/Yt/blob/378913567116f0a0ae86d34df33f060b58f2f420/docs/STUDIO_IMPLEMENTATION.md)
- [Aktualizacja i odtwarzanie](https://github.com/krystiangaleczka-tech/Yt/blob/378913567116f0a0ae86d34df33f060b58f2f420/docs/STUDIO_RELEASE.md)

W pierwotnym logu uruchamiano Studio na właściwej gałęzi poleceniem `python3 scripts/install_studio.py --run`, pod `http://127.0.0.1:8876`. Szczegóły instalacji należy odczytać z instrukcji dla używanego commita.

## Późniejszy audyt produkcyjny

Źródło: [zapis próby z 27 października](https://github.com/krystiangaleczka-tech/Yt/blob/378913567116f0a0ae86d34df33f060b58f2f420/docs/audits/2026-10-27-studio-production-check.md).

Zapis opisuje rzeczywistą próbę na macOS 26.3.1, Apple Silicon, 8 GB RAM: EPUB Jules’a Verne’a, Open Library, Wikimedia Commons, lokalny obraz, głos Chatterbox na CPU, czasy słów faster-whisper oraz montaż i eksport. Raportowany wynik: H.264/AAC, 640×360, 30 fps, **10,266 s**; eksporty tekstowe, napisy, XLSX, pakiet ZIP i ponowny import A/B.

Ten audyt raportuje 83 testy Studio, 18 DocOS i 7 frontend oraz wybrane ekrany UI przy szerokościach 390/768/1024/1440 px. Dokumentacja opisuje benchmark 500 ujęć/500 klipów z 40 krokami historii: p95 zapisu 2015,34 → 247,36 ms, dokument główny 41,76 → 1,02 MB. Są to wyniki zapisanego audytu, nie testy wykonane ponownie podczas archiwizacji.

**Zapisane ograniczenia:** brak niezależnego odsłuchu głosu; brak uzyskanej pełnej odpowiedzi modelu tekstowego w tej próbie; Pixabay/Pexels sprawdzane kontraktowo, bez rzeczywistych kluczy; brak osobnej instalacji Windows; brak pełnej certyfikacji dostępności. Ręcznie wklejony JSON w próbie nie dowodzi działania end-to-end modelu tekstowego.

## Czego nie odzyskano jako plików do tego archiwum

Nie pobrano pełnych eksportów czatów ani prywatnych danych działającej aplikacji: oryginałów mediów, prywatnych nagrań, kluczy i lokalnych artefaktów testowych wskazywanych w dokumentacji jako `/tmp/...`. Dostęp do repozytorium i tekstowego audytu nie oznacza dostępu do tych plików. Nie odtworzono ich z opisów.

## Weryfikacja archiwum

Pięć plików źródłowych zachowano bez zmian treści; ich rozmiary i SHA-256 zapisano w [manifeście](manifest.json). Podsumowania rozróżniają wymagania, pomysły i historyczne wyniki. Zmiany archiwum obejmują nowe pliki w `docs/project-history/`.

