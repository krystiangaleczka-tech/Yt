# Projekt: AI Film Studio, czyli własne studio dokumentalne sterowane przez Multi-Agent AI

To jest dokładnie kierunek, w którym rozwijałbym naszą aplikację do produkcji filmów na YouTube.

**Nie zatrudniasz 15 specjalistów. Budujesz 15 wyspecjalizowanych agentów AI, z których każdy ma własny skill, narzędzia, obowiązki i standard jakości.** Ty jesteś producentem wykonawczym, który zatwierdza najważniejsze decyzje.

Ale jest jeden warunek: nie mogą to być zwykłe chatboty udające pracowników. Muszą faktycznie wykonywać operacje na plikach, programach, scenach i osi czasu.

## 1. Struktura Twojego wirtualnego studia

```text
                   TY: EXECUTIVE PRODUCER
     (tematy, kierunek artystyczny, budżet, akceptacja)
                            |
                            v
                  AGENT 00: STUDIO DIRECTOR
    (orkiestracja, delegowanie, zależności, harmonogram)
                            |
           +----------------+----------------+
           |                |                |
           v                v                v
    PREPRODUKCJA       VISUAL STUDIO    POSTPRODUKCJA
    Agenci 01–04       Agenci 05–08     Agenci 09–11
           |                |                |
           +----------------+----------------+
                            |
                            v
                 KONTROLA I PUBLIKACJA
                     Agenci 12–14
```

- **01–04: Preprodukcja** – research, fakty, scenariusz, storyboard.
- **05–08: Visual Studio** – archiwa, parallax 2.5D, mapy 3D, motion design.
- **09–11: Postprodukcja** – narracja, dźwięk, montaż.
- **12–14: Kontrola i publikacja** – QA, miniatury, analityka YouTube.

To daje **15 agentów AI łącznie z głównym dyrektorem**, podzielonych na cztery działy. Każdy dział może pracować równolegle, ale wszyscy korzystają z jednej bazy projektu i wspólnej biblioteki materiałów.

Najważniejsze: Studio Director nie powinien sam tworzyć wszystkiego. Rozdziela zadania, egzekwuje wyniki i odsyła niedopracowane ujęcia do poprawy. W przeciwnym razie otrzymasz piętnaście modeli generujących piętnaście wersji tego samego chaosu.

## 2. Dokładny podział agentów i ich skilli

| Agent AI | Skill | Zadanie i rezultat |
|---|---|---|
| **00. Studio Director** | `studio-orchestrator` | Rozdziela pracę, zarządza agentami i akceptacjami |
| **01. Creative Director** | `creative-strategy` | Ustala styl kanału, tematy, ton i zasady wizualne |
| **02. Military Researcher** | `military-research` | Szuka książek, relacji, dokumentów i źródeł historycznych |
| **03. Military Fact Checker** | `historical-verification` | Sprawdza daty, uzbrojenie, jednostki i sprzeczne relacje |
| **04. Screenwriter** | `documentary-storytelling` | Pisze scenariusz, narrację, storyboard i listę ujęć |
| **05. Archive Specialist** | `archive-asset-research` | Zdobywa zdjęcia, filmy, mapy, dokumenty i licencje |
| **06. Parallax Artist** | `photo-compositing-2.5d` | Wycinanie warstw, animacje zdjęć, kamery 2.5D |
| **07. Terrain 3D Artist** | `military-map-animation` | Tworzy topografię, mapy 3D, trasy i animacje terenu |
| **08. Motion Designer** | `cinematic-motion-design` | Animuje infografiki, dokumenty, napisy, efekty |
| **09. Voice Director** | `narration-director` | Przygotowuje i synchronizuje nagrania lektorskie |
| **10. Sound Designer** | `cinematic-sound-design` | Muzyka, efekty, atmosfera, miksowanie |
| **11. Film Editor** | `timeline-video-editing` | Składa ujęcia i dźwięk na osi czasu, montuje film |
| **12. Quality Controller** | `documentary-quality-control` | Weryfikuje jakość, źródła, licencje i zgodność scen |
| **13. Thumbnail Designer** | `youtube-packaging` | Projektuje miniatury i tytuły |
| **14. YouTube Analyst** | `youtube-performance-analysis` | Analizuje CTR, retencję i wyniki opublikowanych filmów |

Najważniejsze są agenci 04, 06, 07 i 11. To ich współpraca zamienia ciekawą historię w rzeczywisty film, zamiast kolejnego pokazu slajdów z dramatyczną muzyką.

## 3. Jak agenci mają korzystać z programów?

Nie budowałbym własnego silnika animacji 3D ani całego programu montażowego od zera. W naszej aplikacji stworzyłbym warstwę zarządzającą istniejącymi silnikami.

### Blender + Python

Agent 07 generuje tereny 3D, steruje kamerą, oświetleniem i eksportuje ujęcia. Blender obsługuje uruchamianie skryptów i renderowanie bez interfejsu graficznego.

### Remotion + React / TypeScript

Agent 06 i 08 mogą generować programowo kompozycje, parallax, napisy i infografiki. Remotion pozwala renderować filmy za pomocą kodu, lokalnie lub na serwerze.

### Adobe After Effects

Przydatny do złożonych efektów i dopracowanych szablonów. Agent może automatyzować renderowanie przez `aerender`, ale tworzenie dowolnych efektów od podstaw jest trudniejsze niż w podejściu opartym na kodzie.

### DaVinci Resolve + FFmpeg

Agent 11 wykonuje automatyczny montaż, synchronizację i eksport. Resolve zostawiłbym również do profesjonalnego wykończenia oraz ręcznych poprawek.

**Kluczowa decyzja:** Remotion i Blender powinny być silnikami wykonawczymi, a nasza aplikacja centralnym miejscem zarządzania całym filmem. Nie trzeba zmuszać każdego agenta, by używał jednego programu.

## 4. Jak wygląda rzeczywista współpraca agentów?

Załóżmy, że zlecasz:

> Przygotuj 18-minutowy dokument o historycznej operacji Navy SEALs. Styl premium dark documentary. Wykorzystaj rzeczywiste materiały archiwalne, mapy 3D, parallax 2.5D i kinowy montaż. Nie wymyślaj faktów ani materiałów źródłowych.

### Przepływ produkcji

1. **Research i weryfikacja** – lista źródeł, faktów, niepewności.
2. **Scenariusz i storyboard** – narracja, opis ujęć i znaczniki czasowe.
3. **Równoległa produkcja wizualna** – zdjęcia, parallax, animowane mapy, infografiki.
4. **Produkcja audio** – lektor, muzyka, efekty, synchronizacja.
5. **Montaż** – kompletna edytowalna oś czasu.
6. **Kontrola jakości** – poprawki, weryfikacja, finalny render.
7. **Publikacja i analiza** – miniatura, tytuł, pomiar rezultatów.

Agent montażysta nie dostaje polecenia „zrób coś fajnego”. Dostaje gotową listę ujęć z narracją, plikami, długością animacji i wskazówkami reżyserskimi.

### Przykładowe ujęcie zapisane w aplikacji

**SCENA 023** | **01:36 – 01:48**

**Przelot nad górami Afganistanu**

- **Obraz:** Mroczna mapa topograficzna 3D, powolny ruch kamery, zaznaczenie historycznie potwierdzonej lokalizacji.
- **Agent:** 07. Terrain 3D Artist.
- **Narracja:** Fragment zatwierdzonego scenariusza przypisany do ujęcia.
- **Wynik:** `scene_023.mov` + projekt Blender + metadane źródeł.
- **Kontrola:** Wymaga sprawdzenia zgodności mapy z udokumentowaną lokalizacją.

Dzięki takiemu podejściu, gdy stwierdzisz „zmień mapę między 1:36 a 1:48”, Studio Director uruchomi agenta 07, a następnie agenta 11. Nie będzie regenerować całego filmu.

## 5. Co musi zawierać każdy skill?

Sam plik `SKILL.md` z opisem roli nie wystarczy.

Każdy specjalista potrzebuje pięciu elementów: instrukcji, dostępu do narzędzi, ustrukturyzowanych danych wejściowych, konkretnego rezultatu i automatycznych testów jakości.

Przykładowa struktura:

```text
ai-film-studio/
  agents/
    00-studio-director/
    01-creative-director/
    02-military-researcher/
    03-fact-checker/
    04-screenwriter/
    05-archive-specialist/
    06-parallax-artist/
    07-terrain-3d-artist/
    08-motion-designer/
    09-voice-director/
    10-sound-designer/
    11-film-editor/
    12-quality-controller/
    13-thumbnail-designer/
    14-youtube-analyst/

  skills/
    .../SKILL.md

  tools/
    blender/
    remotion/
    after-effects/
    video-editing/
    asset-search/

  projects/
  shared-library/
  render-queue/
```

Skill powinien również zawierać przykłady dobrego i złego rezultatu. Agent od map nie może sobie wymyślać przebiegu operacji, a agent od archiwów nie może uznawać dowolnego zdjęcia z Google za materiał z prawem do publikacji.

## 6. Co dokładamy do naszej aplikacji?

W praktyce potrzebujemy pięciu zintegrowanych obszarów.

### Agent Command Center

Status wszystkich agentów, zadania, błędy, kolejki, historia decyzji i akceptacje.

### Research & Asset Library

Książki, notatki, archiwa, filmy, zdjęcia, licencje, fragmenty źródeł i wyszukiwanie semantyczne.

### Scene Builder

Scenariusz, prompt lub materiał źródłowy, rodzaj animacji, agent wykonujący, timestamp, narracja i podgląd.

### AI Timeline Editor

Edytor podobny funkcjonalnie do CapCut: ścieżki obrazu i audio, podgląd, ręczne poprawki, montaż sterowany językiem naturalnym.

### Render & Quality Control

Renderowanie ujęć równolegle, podgląd wersji, porównywanie zmian i zatwierdzanie publikacji.

Technicznie zastosowałbym TypeScript do aplikacji i orkiestracji, Python do automatyzacji grafiki 3D, bazę PostgreSQL do stanu projektów, magazyn plików S3-compatible oraz kolejkę zadań dla renderowania. Agenci powinni pracować na wersjonowanych plikach projektu, a nie przesyłać sobie rezultaty wyłącznie w rozmowach.

## 7. Jedna rzecz, której nie powinniśmy automatyzować bez kontroli

Produkcja dokumentów wojskowych to nie tylko animacja. To również wiarygodność.

YouTube wyraźnie rozróżnia autorskie, przetworzone dokumenty od powtarzalnych produkcji masowych i wymaga odpowiednich oznaczeń dla realistycznych treści zmienionych lub wygenerowanych przez AI.

Dlatego zostawiłbym Tobie trzy obowiązkowe zatwierdzenia: scenariusza i ustaleń historycznych, kierunku wizualnego po pierwszych ujęciach oraz gotowego filmu. Osobno należy weryfikować licencje archiwaliów. I nie zakładajmy z góry retencji 55–70%, bo sam motion design jej nie gwarantuje. System YouTube ocenia również satysfakcję i zachowania widzów.

## Moja rekomendacja

Nie uruchamiałbym piętnastu agentów od razu w pełnej produkcji. Najpierw zbudowałbym działający przepływ z sześciu: **Director → Researcher → Screenwriter → Visual Artist → Film Editor → Quality Controller**.

Następnie rozdzieliłbym Visual Artist na osobnych specjalistów od parallax, map i motion designu, dołożył audio oraz pozostałe role. To pozwoli sprawdzić, czy system faktycznie produkuje kompletne sceny i edytowalne filmy, a nie tylko imponującą liczbę raportów.

**Docelowo budujemy nie generator filmów AI, lecz autonomiczne studio dokumentalne z kontrolą człowieka.** Agenci są pracownikami, skille ich specjalizacjami, a nasza aplikacja miejscem, w którym powstaje i jest montowany każdy odcinek.
