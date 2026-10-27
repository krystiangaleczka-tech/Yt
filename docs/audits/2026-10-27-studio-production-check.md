# DocOS Studio 0.2 — rzeczywista próba produkcyjna

Data: 27.10.2026. Komputer: macOS 26.3.1, Apple Silicon, 8 GB RAM. Prywatne próbki, nagrania, media i klucze nie są częścią repozytorium.

## Materiał i przebieg

- Źródło: Jules Verne, *Twenty Thousand Leagues under the Sea*, [Project Gutenberg #164](https://www.gutenberg.org/ebooks/164), pobrany oryginał EPUB. Zachowano oryginalny plik, rozdziały i cytat potwierdzający autorstwo.
- Dodatkowe metadane: rzeczywiste wyszukiwanie Open Library i wybór konkretnego wydania.
- Obraz stockowy: rzeczywiste wyszukanie i pobranie Wikimedia Commons, z pochodzeniem i atrybucją.
- Obraz generowany: lokalny SD 1.5, 512×288, 12 kroków, seed 73; zachowany jako wariant. Film używa wybranego obrazu Commons.
- Lektor: lokalny Chatterbox, dwa polskie zdania. Po nieudanej próbie MPS z nadmiernym swapem wybrano CPU; aktualna domyślna konfiguracja Auto robi to na Macach do 12 GB.
- Czasy słów: rzeczywisty faster-whisper tiny na CPU. 10 słów z pomiarami. Pisownię poprawiono według wejściowej narracji, bez zmieniania czasów. Nie oceniano niezależnie jakości głosu odsłuchem.
- Montaż: jawnie wklejony i zwalidowany JSON ustawił zbliżenie. To kontrolowany przypadek propozycji, nie odpowiedź modelu tekstowego. Utworzono tekst na osi i dwie wersje A/B.
- Eksport: MP4 oraz MD/TXT/opis/atrybucje/XLSX/SRT/VTT; następnie ZIP z mediami i A/B, zaimportowany do nowego projektu i porównany.

Narracja próby: „Jules Verne opisywał podmorskie podróże. Sprawdzamy źródło, nagranie i obraz.” Nie przedstawia obrazu hydrofonu jako dowodu treści książki.

## Wynik

Projekt QA: `prj_25ffda25cda44dd8` w `/tmp/docos-studio-full-e2e`.
Pierwszy render: `job_bd41e1d73ee343ec`; render po przeglądzie pisowni: `job_b1b94a1fb7d949ab`.

Film: H.264, 640×360, 30 fps, audio AAC, **10,266 s**. Kontrola gotowości końcowej referencji: brak uwag. ZIP zawiera dwie wersje; po imporcie zachowano słowa i mierzone czasy. Zatwierdzenie historii nowego importu jest celowo cofnięte.

Lokalne dowody:

- `/tmp/docos-studio-full-e2e/e2e-report.json`
- `/tmp/docos-studio-full-e2e/final-review.json`
- `/tmp/docos-studio-full-e2e/qa-reviewed-project.zip`
- `/tmp/docos-studio-full-e2e/projects/prj_25ffda25cda44dd8/exports/job_b1b94a1fb7d949ab.mp4`
- `/tmp/docos-live-e2e.log`

Etap lokalnego głosu po wznowieniu: około 202 s; wznowiony proces zakończył się po około 224 s. Ten czas nie obejmuje wcześniejszego pobierania wag/źródeł i tworzenia obrazu. CPU działa poprawnie, ale nie jest szybkim generowaniem w czasie rzeczywistym.

Próba deterministyczna bez sieci/modeli również przeszła: `/tmp/docos-studio-fixture-e2e/e2e-report.json`. Skrypt powtórzenia: `scripts/verify_studio_e2e.py`; wariant rzeczywisty wymaga `--live` i skonfigurowanych lokalnych modeli.

## Granice potwierdzenia

Claude CLI ma limit konta do 28.10.2026 10:00 Europe/Warsaw. Pełnej odpowiedzi modelu tekstowego nie uzyskano. Pixabay/Pexels nie mają rzeczywistych kluczy użytkownika; ich kontrakty testowano kontrolowanymi odpowiedziami. Wyniki fixture nie zastępują tych brakujących prób live.

67 testów Studio, 18 testów DocOS i 7 testów frontendu przechodziło przed scaleniem późniejszych zdalnych zmian Remotion. Aktualny zbiorczy wynik po scaleniu należy sprawdzić w [macierzy wdrożenia](../STUDIO_IMPLEMENTATION.md).

Benchmark 500 ujęć/500 klipów i 40 trwałych kroków cofania: [surowy raport](../benchmarks/2026-10-27-studio-mac8gb.json). Zmiana historii z powtarzanych pełnych dokumentów na odrębne migawki obniżyła p95 zapisu z 2015,34 do 247,36 ms; plik główny z 41,76 MB do 1,02 MB. Pomiar obejmuje dysk, blokady i fsync, nie opóźnienie interakcji przeglądarki.
