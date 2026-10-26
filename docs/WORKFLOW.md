# Workflow: od tematu do filmu

Najprościej w Claude Code: *„napisz scenariusz dokumentu o …”* — skill `dokument-scenariusz` prowadzi przez wszystkie kroki.
Poniżej to samo ręcznie.

## 0. Tematy i Story Lock (Documentary)

Przy nowym kanale lub odcinku skorzystaj z [etapu redakcyjnego](EDITORIAL.md):
`channel` → `topics` → `save-topics` → `new --channel` → research → `story` → `lock`.
Claude generuje propozycje z promptu, a DocOS pamięta ich tytuły i przekazuje zatwierdzoną kartę do każdego beatu.
Starsze projekty bez karty zachowują dotychczasowy przebieg.

## 1. Projekt i research
```bash
cd docos
uv run -q docos.py new ../projekty/moj_odcinek/odcinek.json "Tytuł"
```
Uzupełnij `meta` (logline, teza, curiosity gap, narrator, język, target_minutes, wpm, min_unique_visuals),
a przede wszystkim **`facts`** — każde twierdzenie ze źródłem i statusem. Bez faktów nie planuj beatów.

## 2. Struktura
`chapters` (segment + domyślna dynamika) i `beats` (akcja, cel, turn, typologia, dynamika, chaos, fakty, sekundy).
Segmenty: COLD_OPEN, CONTEXT, INVESTIGATION (Looped Arc), TWIST, RESOLUTION, OUTRO.
```bash
uv run -q docos.py check odcinek.json     # energia, turny, czasy
uv run -q docos.py status odcinek.json
```

## 3. Pisanie beat po beacie (Claude)
```bash
uv run -q docos.py system odcinek.json    # raz: globalne DNA odcinka
uv run -q docos.py next odcinek.json      # prompt dla kolejnego beatu (z N-1/N-2)
uv run -q docos.py save odcinek.json B03 wynik.md
```
Format odpowiedzi: `Narracja:` / `Shot List:` (`[WIZ n] (kadr) TYP: opis (X s)`) / `Fakty użyte:` / `Połączenie do N-1:`.
`save` od razu ostrzega o liczbach spoza faktów, złej długości i różnorodności.

## 4. Materiały
```bash
python3 fetch_commons.py search "humpback whale" --video
python3 fetch_commons.py get "File:....webm" ../projekty/moj_odcinek/raw/video --name v_humpback
```
Każde pobranie trafia do `licenses.json`. Nagrania NOAA/NASA/Navy — domena publiczna.
Klipy 4K pobierają się jako pochodna 1080p (jeśli Commons ją ma).

## 5. Sekcja `render` w projekcie
```json
"render": {
  "media": ["raw"], "voice": "voice",
  "lead": {"B01": 3.0}, "tail": {"B11": 6.5},
  "cues": ["B01:start:bloop.wav:1.0:10", "B11:end:A53JD33Calving_3x.wav:1.0:6.5"],
  "credits": ["raw/commons/licenses.json", "raw/video/licenses.json"],
  "credit_lines": ["Audio: NOAA PMEL (public domain)", "..."],
  "silence_before": "B11"
}
```

## 6. Lektor
```bash
../pilot/.venv-tts/bin/python -I voice_beats.py odcinek.json moja_probka.wav ../projekty/moj_odcinek/voice --sps 4.0
```

## 7. Edycja i podgląd
```bash
../pilot/.venv/bin/python -I editor.py ../projekty/moj_odcinek/odcinek.json --port 8766
```
lub bez edytora: `render_doc.py odcinek.json --out podglad.mp4 --quality preview`.

## 8. Finał
`--quality final` (1080p, 25 fps) + opis z sekcją źródeł (patrz `projekty/bloop_v3/bloop_v3_description.txt`).
