# YT — fabryka faceless dokumentów na YouTube

Lokalny, darmowy (open source) system do tworzenia filmów dokumentalnych na YouTube: od researchu i faktów,
przez scenariusz beat po beacie, lektora sklonowanym głosem, aż po montaż z prawdziwych materiałów archiwalnych.
Zbudowany i testowany na odcinku **„The Bloop”** (dźwięk z 1997 roku, który okazał się pękającym lodem).

Silnikiem piszącym scenariusze jest **Claude** (Claude Code), prowadzony przez system **DocOS** — bez kluczy API.

```
research → fakty ze źródłami → plan beatów (energia, Turn, chaos) → narracja + shot list
        → lektor (klon głosu) → materiały (NOAA/NASA/Navy/Commons) → edytor storyboardu → render
```

---

## Co jest w repo

| Folder / plik | Co to jest |
|---|---|
| [`docos/`](docos/) | **DocOS** — system scenopisarski + cały pipeline produkcji (CLI, render, edytor w przeglądarce) |
| [`pilot/`](pilot/) | pierwszy 10-sekundowy pilot (SD 1.5, Kokoro, ffmpeg) i wspólne fonty |
| [`projekty/bloop_v3/`](projekty/bloop_v3/) | projekt odcinka „The Bloop”: fakty, beaty, shot listy, rejestry licencji, opis na YT |
| [`docs/`](docs/) | dokumentacja: architektura, workflow, typy ujęć, lektor, edytor, kwestie prawne, skill dla Claude |
| `requirements-*.txt` | zależności dwóch środowisk Pythona (montaż / klon głosu) |

Czego **nie ma** w repo (celowo): próbki głosu i nagrań lektora (prywatność — z próbki da się sklonować głos),
mediów (~3 GB, odtwarzane skryptem `docos/fetch_media.py`), modeli AI, wyrenderowanych filmów i cache.

## Najważniejsze funkcje

- **Tematy i Story Lock (Documentary)** — profil kanału, prompt dziesięciu propozycji z historią tytułów,
  zatwierdzana karta pytania, dowodów i odpowiedzi filmu, przekazywana do każdego beatu. [Instrukcja](docs/EDITORIAL.md).
- **Scenariusz modułowy (DocOS)** — film to beaty z Celem, Turnem (1 emocja → 1 emocja), Typologią, Dynamiką
  wizualną (ACTION / STORY / CHILL / EUREKA / STATIC), Chaosem i kontekstem N-1/N-2. Claude pisze beat po beacie,
  więc nie „leje wody” i nie gubi wątku.
- **Zasada prawdy** — każda liczba, data, nazwisko i cytat musi być w rejestrze faktów ze źródłem
  (VERIFIED / DISPUTED / UNVERIFIED / DRAMATIZATION). Walidator łapie liczby spoza faktów.
- **Kontrola jakości** (`docos.py check`) — krzywa energii, zasada 3 beatów, czasy, różnorodność obrazu
  (min. 25 różnych materiałów, każdy max 2×, plansze tekstowe nigdy obok siebie, zmienne style i przejścia).
- **Prawdziwe materiały z licencjami** — `fetch_commons.py` szuka i pobiera z Wikimedia Commons, zapisując licencję
  i autora; nagrania NOAA (domena publiczna); plansza końcowa i opis na YT generują się z rejestrów.
- **Lektor sklonowanym głosem** — Chatterbox Multilingual (MIT), zdanie po zdaniu, jedno tempo dla całego filmu,
  dogrywki odstających zdań, naturalne mikropauzy, cache po treści zdania (zmiana tekstu = tylko to zdanie od nowa).
- **Montaż** — 20 typów ujęć (zdjęcia i wideo z najazdem, prawdziwy spektrogram/oscylogram z nagrania, plansze prasowe,
  rozmowy Q&A z prawdziwymi cytatami, liczniki, lupa, diagramy, mapy, porównania), 8 przejść, 8 stylów napisów,
  5 układów porównań, sound design (uderzenia, maszyna do pisania, przyciszanie pod lektorem, cisza przed puentą).
- **Szybkie iteracje** — render segmentami per beat z cache, równolegle: podgląd całości ~2 min,
  po zmianie jednego ujęcia ~30 s.
- **Edytor w przeglądarce** — storyboard z miniaturami, biblioteka mediów z licencjami, edycja ujęć i narracji,
  podgląd jednym kliknięciem.

## Szybki start

Wymagania: macOS / Linux, Python 3.11 + 3.12, [uv](https://github.com/astral-sh/uv), ffmpeg.

```bash
# 1. środowiska (patrz docs/SETUP.md)
uv venv -p 3.12 pilot/.venv && uv pip install -p pilot/.venv/bin/python -r requirements-render.txt
uv venv -p 3.11 pilot/.venv-tts && uv pip install -p pilot/.venv-tts/bin/python -r requirements-tts.txt

# 2. media odcinka (NOAA + Commons, wg rejestrów licencji)
python3 docos/fetch_media.py projekty/bloop_v3

# 3. edytor
pilot/.venv/bin/python -I docos/editor.py projekty/bloop_v3/bloop_v4.json --port 8766
# → http://localhost:8766
```

Lektor wymaga własnej próbki głosu (15–30 s czystej mowy) — patrz [docs/VOICE.md](docs/VOICE.md).

## Dokumentacja

### DocOS Studio — aplikacja

Lokalne studio: projekty, research i książki, przygotowanie ujęć, wielościeżkowy montaż
ręczny/AI oraz eksport MP4. Wymaga Pythona 3.11+, Node.js 22.12+ i FFmpeg.

```bash
python3 scripts/install_studio.py --run
# Otwórz http://127.0.0.1:8876
```

Instalacja, połączenia, modele, montaż i granice wydania: [docs/STUDIO.md](docs/STUDIO.md).
Dotychczasowy workflow CLI nadal działa.

### Dotychczasowy workflow i silniki

- [docs/EDITORIAL.md](docs/EDITORIAL.md) — profil kanału, propozycje tematów i Story Lock
- [docs/SETUP.md](docs/SETUP.md) — instalacja, modele, sprzęt i wydajność
- [docs/WORKFLOW.md](docs/WORKFLOW.md) — od tematu do gotowego filmu, krok po kroku (z Claude)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — jak działa DocOS, render i edytor; model danych projektu
- [docs/SHOT_TYPES.md](docs/SHOT_TYPES.md) — wszystkie typy ujęć, przejścia, style napisów i porównań
- [docs/VOICE.md](docs/VOICE.md) — klon głosu, tempo, pauzy, cache
- [docs/EDITOR.md](docs/EDITOR.md) — edytor w przeglądarce
- [docs/LEGAL.md](docs/LEGAL.md) — licencje materiałów, fakty, oznaczanie AI, głos
- [docs/skill/SKILL.md](docs/skill/SKILL.md) — skill Claude Code `dokument-scenariusz`
- [docos/README.md](docos/README.md) — DocOS CLI

## Historia odcinka „The Bloop”

| Wersja | Co się zmieniło |
|---|---|
| pilot 10 s | SD 1.5 + Kokoro + ffmpeg, potem klon głosu |
| v1–v2 | 3 min, kadry AI, plansze proceduralne — „sleep story”, za wolno, bez dowodów |
| v3 | prawdziwe materiały NOAA/Navy/ESA, Chris Fox jako bohater, plansze prasowe, sound design |
| v4 | 59 różnych ujęć, prawdziwy spektrogram/oscylogram, Q&A, diagram SOFAR, licznik, lupa |
| v5 | tempo dokumentu (5–7 s/ujęcie), ~15 prawdziwych klipów wideo, bez AI, biblioteki przejść/stylów, edytor, render z cache |

Narzędzia: Stable Diffusion 1.5, Kokoro-82M (Apache 2.0), Chatterbox Multilingual (MIT, watermark Perth),
ffmpeg, Pillow, NumPy. Fonty: Courier Prime, Montserrat (SIL OFL 1.1, licencje w `pilot/fonts/`).

## Licencja

Kod: [MIT](LICENSE). Fonty: SIL OFL 1.1. Materiały zewnętrzne (NOAA, NASA, US Navy, Wikimedia Commons) — na licencjach z rejestrów `licenses.json`, nie objęte MIT.
