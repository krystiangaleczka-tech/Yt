# Przekazanie pracy: etap „Szkice ujęć” w DocOS Studio

Plik dla następnego agenta (inne konto Claude). Przeczytaj go w całości, potem `CLAUDE.md` w repo.
**Usuń ten plik w ostatnim commicie**, kiedy funkcja będzie gotowa.

## 1. Zadanie (od sesji nadrzędnej, słowa reżysera)

Dodać do DocOS Studio nową kategorię (etap) **„Szkice ujęć”**. Po zatwierdzeniu tytułu filmu reżyser porównuje
w niej kilka zupełnie różnych podejść do opowieści i wybiera jedno, zanim powstanie cały film.

Reżyser: „stwórz w programie nową kategorię szkic ujęć… 3 takie szkice ujęć całe i dla każdego wklejony inny
scenariusz, bo do jednego tytułu możemy podejść na milion sposobów… pod spodem dla każdej historii mini, szybki
przegląd wszystkich ujęć… jeśli film ma 12 minut, to przeglądanie trwa przyspieszone 20 czy 30 sekund, jak
w zeszycie, na każdej kartce osobny szkic… szkic, który ja zatwierdzę, na jego podstawie tworzymy dalszą część filmu”.

Co ma działać:
1. **Warianty** — domyślnie 3 (można dodać kolejne). Każdy: tytuł, wklejony scenariusz (długi tekst: struktura,
   hooki, kwestie), lista ujęć: numer, opis, kwestia lektora, długość w s, opcjonalnie obraz klatki.
2. **Przegląd jak kartkowanie zeszytu** — pod każdym wariantem odtwarzacz klatek po kolei. Cały film w ok. 20–30 s
   (do ustawienia), czas klatki proporcjonalny do długości ujęcia, z rozsądnym minimum. Pauza, przewijanie,
   numer/opis bieżącego ujęcia.
3. **Ujęcie bez obrazu dostaje kartę** — najszybsza możliwa, czarno-biała: kadr, krótki opis, kwestia. Przegląd
   działa od razu po wklejeniu scenariusza, zanim cokolwiek narysowano.
4. **Zatwierdzenie** — przycisk „Zatwierdź” wybiera jeden wariant; zapis w projekcie i w dzienniku pracy
   (`POST /api/projects/{id}/flow/log` albo ten sam mechanizm), reszta produkcji (rozpiska, ujęcia) ma się do niego
   odwoływać.
5. **Import z plików** — katalog `docs/filmy/<film>/szkice/<wariant>/` z `szkic.json` =
   `{"film","wariant","tytul","scenariusz","ujecia":[{"nr","klucz","sekundy","opis","kwestia","klatka":"klatki/001.png"}]}`
   i klatkami PNG obok. Polecenie albo endpoint wczytuje katalog do projektu, łącznie z wgraniem klatek jako mediów.
   Puste `klatka` → karta. (Inny wątek wypełni to dla filmu o Japonii, gałąź `powstanie-japonii`.)

Gotowe, gdy: kategoria działa w przeglądarce, 3 warianty dają się wypełnić ręcznie i z importu, przegląd gra
w 20–30 s, zatwierdzenie się zapisuje, są testy jak w reszcie `studio_api`. Dopisać w Podręczniku
(`docs/podrecznik/01_PRACA.md`), gdzie w cyklu stoją „Szkice ujęć”: po tytule, przed rozpiską i ujęciami.
Reżyserowi napisać po polsku, jak tego użyć. **Commit na własnej gałęzi; bez push i bez merge**, dopóki reżyser
nie poprosi.

## 2. Ograniczenia

- Pracuj TYLKO w worktree `/Users/krystiangaleczka/Documents/YT/.claude/worktrees/szkice-ujec`,
  gałąź `studio/szkice-ujec` (od `main` 7ebb2bc). Nie zmieniaj gałęzi w głównym checkoucie
  (`film/pierwszy-cesarz`) — z niego chodzi Studio reżysera (API port 8876) i pracują tam inne sesje.
- Dowiązania `node_modules` i `apps/studio/node_modules` (symlinki do głównego checkoutu) **nie commitować** —
  dodawaj pliki do gita po nazwie, nigdy `git add -A`.
- Mac 8 GB RAM, ok. 11 GB wolnego dysku: jeden ciężki proces naraz (np. `npm run build` albo serwer, nie oba
  z czymś jeszcze). Długie polecenia w tle.
- Wszystko, co czyta autor, po polsku (UI, komunikaty, podsumowania, przyciski). Kod po angielsku.
- Python: `/Users/krystiangaleczka/Documents/YT/.venv-studio/bin/python` (3.13).

## 3. Stan na moment przekazania

Zrobione (commit WIP na gałęzi):
- `studio_core/production_flow.py`: modele `SketchShot`, `SketchVariant`, `SketchApproval`, `Sketches` i pole
  `ProductionFlow.sketches`. Sprawdzone: `validated_flow({...sketches...})` przechodzi.

Do zrobienia: wszystko poniżej z sekcji 5.

## 4. Co już rozpoznano w kodzie (żeby nie czytać od nowa)

Backend:
- `studio_api/flow.py` — wzorzec endpointów planu filmu: `_flow(project)` (deepcopy `legacy.production_flow`),
  `_save(pid, revision, change)` → `store.save_flow(...)`, `_now()`; `add_log` dopisuje wpis
  `{id, at, who, unit, kind, summary, details, files}` i przycina `del log[:-5000]`; `continuity_check` dokleja
  `timeline_issues` i liczy `totals` (trzeba przeliczać per waga, nie tylko „2”). `flow_prompt()` buduje kontekst AI
  (`context = {...}`) — tu dodać `approved_sketch`.
- `studio_core/production_flow.py` — walidacja; payload zapisywany dokładnie tak, jak przyszedł (`extra="allow"`).
- `studio_core/service.py:save_flow` — zapis tylko `legacy.production_flow` przez `self.mutate(...)`.
- `studio_core/store.py:mutate(pid, revision, change)` — blokada plikowa (między procesami), sprawdza rewizję
  (`Conflict` → 409), historia cofania 40 kroków.
- `studio_core/media.py:import_media` — **robi osobną mutację na każdy plik** (zapchałoby historię cofania przy
  70 klatkach). Dla klatek szkicu napisać własne „przygotuj asset bez mutacji” + jedna mutacja na cały import.
  Wzór id: `"asset_" + sha256(digest_źródła + json(provenance, sort_keys))[:20]`; miniatura
  `<id>.thumb.jpg` 640×360 (PIL `thumbnail`, quality 85); pliki w `store.folder(pid)/"media"`.
  **`Asset.sha256` musi być skrótem pliku zapisanego na dysku** (`studio_core/bundles.py` to sprawdza).
  `Asset` (studio_core/models.py): id, name, kind="image", filename, mime, sha256, width, height, thumbnail,
  provenance. Media serwuje `GET /api/projects/{pid}/media/{asset_id}?thumbnail=true`.
- `studio_api/app.py:create_app` — rejestracja modułów (`register_flow(app, store, connectors)` itd.); middleware
  wymaga nagłówka `X-Docos-Request: 1` dla zapisów; `ValueError` → 422, `Conflict` → 409. `REPO` = korzeń repo.
  `dist` frontendu serwowany z `apps/studio/dist`, jeśli istnieje.
- `studio_core/cli.py` — CLI `python -m studio_core.cli` na `ProjectService(--home)`; dodać polecenie importu.
- `studio_core/handbook.py` — rozdziały podręcznika z plików; `01_PRACA.md` ma sekcję „Etapy w aplikacji”.
- Testy: `studio_tests/test_flow.py` (unittest + `TestClient(create_app(Path(tmp), seed_demo=False))`,
  nagłówek `H = {"X-Docos-Request": "1"}`, `tearDown`: `client.close(); app.state.jobs.close(); tmp.cleanup()`).
  Uruchamianie: `.venv-studio/bin/python -m unittest studio_tests.test_<x> -v`.

Frontend (`apps/studio/src`):
- `App.tsx` — tablica `steps` (etapy w pasku bocznym, numer = indeks; ✓ przy zatwierdzonych), routing: lista stron
  idących do `<FilmFlow page=…>` (`["bible","project-setup","idea-flow",…,"continuity"]`).
- `context.tsx` — typ `Page` (dodać `"sketches"`) i lista `pages` przy wczytaniu projektu (dodać).
- `FilmFlow.tsx` — `FlowPage`, `nextPage` (idea-flow → teraz sketches → master-story), tytuły/podtytuły stron,
  pasek „Story Bible” (`flow-bible-strip`) — obok dodać pasek „Szkic ujęć: … ✓ / niezatwierdzony” na stronach po
  szkicach; na stronie Master Story jest wzór przycisku „Przejmij wybraną historię” — dodać analogiczny
  „Przejmij zatwierdzony szkic” (nowy wariant master z tytułem i scenariuszem szkicu). Przycisk na idea-flow
  „Dalej: Master Story” → „Dalej: szkice ujęć”.
- `flowTypes.ts` — `flowFrom()` rozpakowuje `...value`, więc nieznane klucze (np. `sketches`) przeżywają zapis
  całego planu przez `saveFlow`; `stableJson()` do porównań.
- `Continuity.tsx` + `Continuity.css` — wzorzec kategorii z zakładkami (`cont-tabs`), `flow-card`,
  `flow-explainer`, `flow-empty`; zapis przez `s.run(() => s.mutate(async () => api<Project>(url, body)))`.
- `api.ts` — `api(path, body, method)`, `upload(path, file)`, `mediaUrl(pid, assetId, thumbnail)`.
- Testy frontu: `apps/studio/tests/*.test.mjs`, `node --experimental-strip-types --test`, importują `../src/*.ts`.

## 5. Projekt rozwiązania (ustalony, do wykonania)

### Dane — `legacy.production_flow.sketches`
```
{ version: 1, playSeconds: 25,
  variants: [{ id, title, scenario, source: {film, wariant, path, importedAt, frames, missing},
               shots: [{ id, nr, key, kadr, seconds, description, line, mark, assetId }] }],
  approved: { variantId, title, at, who, note, signature, snapshot } | null }
```
- Brak `sketches` → 3 domyślne puste warianty o stałych id `szkic_a`, `szkic_b`, `szkic_c` (to samo w Pythonie
  i TS), etykiety „Wariant A/B/C” z indeksu. Maks. 12 wariantów.
- `content(variant)` = `{title, scenario, shots:[{nr,key,kadr,seconds,description,line,mark,assetId}]}` (bez id).
  Zatwierdzenie zapisuje `snapshot = content(variant)` + `signature` (sha256 JSON sort_keys, seconds jako
  `round(float,3)`). Stan zatwierdzenia: `none` / `current` (content == snapshot) / `stale` / `missing`
  (wariant usunięty). Klient liczy to sam: `stableJson(content(v)) === stableJson(snapshot)`.
- `mark` (opcjonalny znacznik struktury: „HOOK 1”, „HOOK 2”, „pogorszenie”, „promyk nadziei”) — kreski na pasku
  przewijania; `kadr` (opcjonalnie „plan ogólny”, „zbliżenie”) — na karcie.

### Nowy moduł `studio_core/sketches.py` (logika) + `studio_api/sketches.py` (endpointy)
- `normalize(state)`, `content(v)`, `signature(v)`, `approval_state(sk)`, `summary(flow)`,
  `issues(flow)`, `approved_brief(flow)` (dla AI), `import_dirs(store, pid, directory, roots|None, revision|None)`,
  `find_sources(roots)`.
- Endpointy (rejestracja w `create_app`, np. `register_sketches(app, store, roots)`):
  - `GET  /api/projects/{pid}/sketches` → `{sketches, state, variants:[{id,label,title,shots,seconds,frames,signature}]}`
  - `PUT  /api/projects/{pid}/sketches` `{expected_revision, sketches}` → zapisuje `variants` i `playSeconds`;
    **`approved` zawsze bierze z zapisanego stanu** (zatwierdza tylko endpoint approve).
  - `POST /api/projects/{pid}/sketches/approve` `{variant_id, who?, note?, expected_revision?}` → snapshot + wpis
    w dzienniku `kind:"szkic"`, `summary:"Zatwierdzony szkic ujęć: <tytuł>"`, details: liczba ujęć, długość,
    źródło. Pusty wariant → ValueError.
  - `POST /api/projects/{pid}/sketches/withdraw` → `approved = null` + wpis w dzienniku.
  - `POST /api/projects/{pid}/sketches/import` `{path}` → katalog wariantu albo katalog `szkice/` z podkatalogami
    (import wszystkich, jedna mutacja, wpis w dzienniku). Ścieżka względna = od korzenia repo; dozwolone tylko
    wewnątrz korzeni (`REPO` + zmienna `DOCOS_SKETCH_ROOTS`, separator `os.pathsep`) po `resolve()`
    (`docs/filmy/powstanie-japonii` w głównym checkoucie to symlink do worktree — i tak jest wewnątrz REPO).
  - `GET  /api/sketches/sources` → lista `docs/filmy/*/szkice/*/szkic.json` w korzeniach
    (`{path, film, wariant, tytul, shots, frames}`) — lista do wyboru w UI, reżyser nie wpisuje ścieżek.
- Import: `szkic.json` ≤ 2 MB, walidacja pydantic (klucze polskie, `extra` dozwolone; `nr` int albo tekst z cyframi,
  brak → kolejny; opcjonalne `kadr`, `znacznik`). Klatka: ścieżka musi leżeć w katalogu wariantu, rozszerzenie
  png/jpg/jpeg/webp, ≤ 40 MB; brak pliku albo uszkodzony obraz → **ostrzeżenie w wyniku + karta**, nie błąd.
  Klatki zapisywane jako JPEG q90, maks. 1920×1080 (oszczędność dysku), miniatura 640×360; id assetu z sha256
  źródła + provenance `{"kind":"sketch-frame", film, wariant, nr, file}` → ponowny import nie duplikuje plików;
  `sha256` assetu = skrót zapisanego JPEG, `provenance.source_sha256` = skrót PNG. Jedna `store.mutate`: dodaj
  nowe assety, wstaw wariant, wpis w dzienniku, `validated_flow`. Przy `revision=None` — ponów do 3 razy przy
  `Conflict`.
  Umiejscowienie wariantu: (1) istniejący z tym samym `source.film`+`source.wariant` → podmiana treści, id zostaje
  (zatwierdzenie samo zrobi się „stale”, jeśli treść inna); (2) pierwszy pusty wariant; (3) dopisz na końcu
  (id `szkic_<slug>`, unikalne). Id ujęć `<id_wariantu>-<nnn>`.
- CLI: `python -m studio_core.cli szkice <project_id> <katalog>` (bez ograniczenia korzeni — CLI jest zaufane).
- Kontrola ciągłości (`continuity_check` w flow.py): `issues(flow)` — są wypełnione warianty, brak zatwierdzenia →
  waga 1; zatwierdzony zmieniony (`stale`) albo usunięty (`missing`) → waga 2; reguła `"szkic"`. Przeliczyć totals.
- AI: w `flow_prompt` `context["approved_sketch"] = approved_brief(flow)` (tytuł, scenariusz ≤ 20000 znaków, ujęcia
  ≤ 400: nr, sekundy, kadr, opis/kwestia ≤ 400 znaków, znacznik; `stale`) i zdanie w poleceniu: zatwierdzony szkic
  to kierunek reżysera — trzymaj się jego struktury, hooków i kolejności.

### Frontend
- `sketchTypes.ts` (czyste funkcje, z testem `tests/sketches.test.mjs`): typy, `sketchesFrom(project)` (3 domyślne),
  `content`, `approvalState`, `flipTimes(shots, total, min=0.15)` — czasy proporcjonalne do `seconds`, minimum
  wodnym wyrównaniem (ujęcia poniżej minimum dostają minimum, reszta skalowana, aż suma = total; jeśli
  n·min > total, każde dostaje total/n), `shotsFromScenario(text)` — akapity (pusta linia) → ujęcia; krótki
  jednowierszowy akapit (≤ 60 znaków, `#…`, wersaliki albo kończy się „:”) to `mark` następnego ujęcia; tekst
  w „…” / "…" → `line`; sekundy = max(3, round(słowa/2.5)+1).
- `Sketches.tsx` + `Sketches.css`, strona `"sketches"` w `steps` między „Pomysł i tytuł” a „Master Story”
  (ikona np. `BookCopy`/`Images` z lucide-react), routing w App.tsx (lazy jak Director).
  - Nagłówek `SectionHead` (eyebrow „PRODUKCJA KROK PO KROKU”), objaśnienie, pole „Przegląd trwa [25] s” (5–180),
    „Importuj z plików” (select z `/api/sketches/sources` + pole ścieżki + przycisk), „+ Wariant”.
  - Każdy wariant to karta jedna pod drugą: nagłówek (litera, tytuł edytowalny, liczba ujęć, długość filmu mm:ss,
    stan: „Zatwierdzony ✓” / „Zmieniony po zatwierdzeniu” / przycisk **„Zatwierdź ten szkic”**, usuń wariant —
    nie zatwierdzonego), scenariusz (textarea, zwinięty podgląd z „Pokaż cały”), **pod spodem odtwarzacz**,
    niżej `<details>` „Ujęcia (N) — edytuj”: tabela Nr | Klucz | Kadr | s | Opis | Kwestia | Znacznik | Klatka
    (miniatura, „Wgraj” przez `upload('/projects/'+id+'/media', file)` → `assetId`, „Usuń”) | ×; „Dodaj ujęcie”;
    „Rozpisz scenariusz na ujęcia” (`shotsFromScenario`, z potwierdzeniem, gdy są ujęcia).
    Bez ujęć odtwarzacz kartkuje karty z akapitów scenariusza automatycznie (podpis „karty z akapitów”).
  - Zapis edycji: `PUT /sketches` na `onBlur` (jak reszta FilmFlow), przez `s.mutate`.
  - Odtwarzacz (komponent `Flipbook`): kadr 16:9, `requestAnimationFrame`, stan czasu przeglądu; Play/Pauza,
    poprzednie/następne ujęcie, suwak (z kreskami `mark`), klawisze spacja/←/→ gdy ma fokus; pod kadrem
    „Ujęcie 12/74 · 3:05 w filmie · 6 s” + opis + kwestia. Podczas grania miniatury (`?thumbnail=true`),
    na pauzie pełny obraz; wstępne ładowanie miniatur (`new Image()`).
  - Karta bez obrazu: czarne tło, biały tekst, CSS (zero generowania): numer i klucz w rogu, kadr wersalikami,
    opis dużym, kwestia kursywą na dole jak napis; znacznik `mark` jako etykieta.
- Odwołania dalej: pasek „Szkic ujęć” na stronach FilmFlow po szkicach i w `Director.tsx` (pod `SectionHead`,
  linia ~320), ✓ w pasku bocznym przy „Szkice ujęć”, „Przejmij zatwierdzony szkic” w Master Story.

### Testy (`studio_tests/test_sketches.py`)
Walidacja (duplikaty id, limity); domyślne 3 warianty w GET; PUT nie nadpisuje `approved`; approve zapisuje
snapshot i wpis w dzienniku; edycja po zatwierdzeniu → `stale` i problem wagi 2 w `/continuity/check`; import
katalogu z 2 klatkami PNG (PIL tworzy obrazki w tmp) + 1 bez klatki + 1 z brakującym plikiem (ostrzeżenie):
assety dodane, `assetId` ustawione, jedna rewizja, ponowny import nie dubluje assetów i podmienia ten sam wariant;
import katalogu `szkice/` z dwoma wariantami wypełnia puste `szkic_a`, `szkic_b`; ścieżka poza korzeniami → 422;
ścieżka klatki `../` → ostrzeżenie/odmowa; `/api/sketches/sources`; `flow_prompt` zawiera zatwierdzony szkic;
CLI. Korzeń testowy przez `patch.dict(os.environ, {"DOCOS_SKETCH_ROOTS": tmp})` przed `create_app`.
Na koniec cały zestaw: `.venv-studio/bin/python -m unittest discover -s studio_tests` (w tle, długie)
i `npm --prefix apps/studio test`, `npm --prefix apps/studio run build` (tsc + vite; jeden ciężki proces naraz).

### Sprawdzenie w przeglądarce (na kopii danych, nie na danych reżysera)
- Zbuduj front w worktree (`npm --prefix apps/studio run build`), uruchom API z worktree na porcie 8879
  z `DOCOS_STUDIO_HOME=<scratchpad>/studio-szkice` (API serwuje `dist`). Konfiguracja w
  `<worktree>/.claude/launch.json` (katalog `.claude/` jest w .gitignore), np.:
  `{"name":"studio-szkice","runtimeExecutable":"/usr/bin/env","runtimeArgs":["DOCOS_STUDIO_HOME=<scratch>",
  "/Users/krystiangaleczka/Documents/YT/.venv-studio/bin/python","-m","studio_api","--port","8879"],
  "cwd":"<worktree>","port":8879}` → `preview_start {name:"studio-szkice"}`.
- Testowy katalog szkiców: w worktree np. `docs/filmy/test-szkice/szkice/a|b|c/` (NIE commitować) albo przez
  `DOCOS_SKETCH_ROOTS`. Sprawdź: 3 warianty ręcznie, import, przegląd 25 s (zmierz), pauza/suwak, karty,
  zatwierdzenie (dziennik w Continuity Editor → Dziennik), zrzut ekranu jako dowód. Zatrzymaj serwer po teście.

### Na koniec
1. Podręcznik `docs/podrecznik/01_PRACA.md`: w „Etapy w aplikacji” wstawić „Szkice ujęć” po „Pomysł i tytuł”,
   przed „Master Story”, i krótką sekcję „Szkice ujęć (po tytule, przed rozpiską)”: po co, jak wypełnić
   (ręcznie / import z `docs/filmy/<film>/szkice/<wariant>/szkic.json`, format jak wyżej + opcjonalne `kadr`,
   `znacznik`), przegląd 20–30 s, zatwierdzenie → dziennik, dalsze etapy (rozpiska, Master Story, AI) odwołują
   się do zatwierdzonego szkicu; zmiana po zatwierdzeniu = ostrzeżenie w kontroli ciągłości.
   W tabeli „Jednostka filmu” nic nie zmieniać (szkic jest dla całego filmu, przed jednostkami).
2. Usunąć ten plik, commit na `studio/szkice-ujec` (kończyć wiadomość linią
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`), bez push i merge.
3. Notatka dla wątku filmu o Japonii (folder notatek sesji, jeśli dostępny:
   `~/Library/Application Support/Claude/side-session-notes/local_c0ed4a26-f9e3-4a03-bc63-983f67f06b0e/`):
   endpoint importu, polecenie CLI, opcjonalne pola `kadr` i `znacznik`, zalecany rozmiar klatek 1280×720.
4. Reżyserowi po polsku: gdzie jest etap, jak wypełnić ręcznie i z plików, jak oglądać przegląd, jak zatwierdzić,
   że zmiana trafi do jego Studio dopiero po merge gałęzi (na jego prośbę).
