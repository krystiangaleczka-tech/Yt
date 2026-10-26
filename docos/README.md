# DocOS — system scenopisarski dla dokumentów YouTube

Przeróbka koncepcji „AI Scriptwriting OS” (arkusz + złota formuła) pod faceless dokumenty.
Działa lokalnie, bez kluczy API. Silnikiem piszącym jest Claude (skill `dokument-scenariusz`).

## Tematy i Story Lock

Pakiet Documentary dodaje profil kanału, dziesięć propozycji z pamięcią tytułów i zatwierdzaną kartę historii.
`topics` i `story` przygotowują prompty dla Claude; walidacja i zapis działają lokalnie.
Pełny przebieg i pola karty: [docs/EDITORIAL.md](../docs/EDITORIAL.md).

```bash
python3 docos.py channel kanal.json --name "Mój kanał"
python3 docos.py topics kanal.json
# Claude zapisuje tablicę propozycji w tematy.json.
python3 docos.py save-topics kanal.json tematy.json
python3 docos.py new odcinek.json "Wybrany tytuł" --channel kanal.json
python3 docos.py story odcinek.json
# Research i uzupełnienie facts oraz story_lock w projekcie.
python3 docos.py lock odcinek.json
python3 docos.py next odcinek.json
```

## Szybki start
```bash
uv run -q docos.py new projekty/moj_odcinek.json "Tytuł odcinka"
uv run -q docos.py export projekty/moj_odcinek.json   # arkusz do planowania
uv run -q docos.py import projekty/moj_odcinek.json projekty/moj_odcinek/moj_odcinek.xlsx
uv run -q docos.py check  projekty/moj_odcinek.json
uv run -q docos.py next   projekty/moj_odcinek.json   # prompt dla następnego beatu
uv run -q docos.py save   projekty/moj_odcinek.json B03 wynik.md
uv run -q docos.py status projekty/moj_odcinek.json
```
W Claude Code wystarczy napisać np. „napisz scenariusz dokumentu o …” — skill poprowadzi cały proces.

## Co jest w systemie (z dziennika koncepcji → wersja dokumentalna)
| Koncepcja | W DocOS |
|---|---|
| Ustawienia globalne / System Prompt | `meta` + `docos.py system` |
| Rozdział / Podrozdział / Scena / Beat | `chapters`, `subchapters`, pola beatu |
| Cel vs Turn (1 emocja → 1 emocja) | `goal`, `turn` + walidacja |
| Typologia, Looped Arc | `typology` (INTRODUCTION … OPEN_QUESTION) |
| Dynamika Wizualna (ACTION/STORY/CHILL/EUREKA/STATIC) | `dynamic`, liczba i długość ujęć liczone z czasu beatu |
| Kontekst N-1 / N-2 („zszywacz”) | automatycznie z „Połączenie do N-1” poprzednich beatów |
| Chaos (NONE/MICRO/MINI/MACRO) | zwrot śledztwa — musi wynikać z faktu |
| Krzywa energii, zasada 3 beatów, segment jako master fader | `check` + wykres i heatmapa w xlsx |
| **Nowe:** rejestr faktów ze źródłami | `facts` + wykrywanie liczb spoza faktów |
| **Nowe:** typy materiału w shot liście | ARCHIWUM, AI_OBRAZ (z promptem), DOKUMENT, TYTUŁ, PORÓWNANIE, MAPA, OŚ_CZASU, CYTAT |
| **Nowe:** most do produkcji | `_render_plan.json` → `make_assets.py` (kadry AI) + `assets_todo.md` |

## Pliki
- `docos.py` — CLI (Python 3.10+, openpyxl instalowany automatycznie przez `uv run`)
- `make_assets.py` — kadry AI z planu renderu (uruchamiaj pythonem z `../pilot/.venv`)
- `examples/bloop.json` — przykładowy projekt

## Produkcja wideo (v5)
| Narzędzie | Do czego |
|---|---|
| `fetch_commons.py` | wyszukiwanie/pobieranie zdjęć i wideo z Commons + rejestr licencji |
| `voice_beats.py` | lektor sklonowanym głosem, zdanie po zdaniu, stałe tempo, mikropauzy, cache |
| `render_doc.py` | montaż z projektu: segmenty per beat w cache, równolegle; `--quality preview` (~2 min całość, ~30 s po zmianie) lub `final` |
| `editor.py` + `editor.html` | edytor storyboardu w przeglądarce: ujęcia, przejścia, style, narracja, biblioteka mediów, podgląd |

```bash
~/Documents/YT/pilot/.venv/bin/python -I editor.py ../projekty/bloop_v3/bloop_v4.json --port 8766
```
