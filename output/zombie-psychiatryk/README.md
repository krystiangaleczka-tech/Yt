# Oddział C — 25,5 s + 25 s, animowany horror

Ujęcia mają pauzy przed i po kwestiach, a postacie mikroruchy: mruganie w nieregularnych odstępach, oddech,
błądzący wzrok, zawahania, potknięcia (`noise()`, `blink()` w `render.py`). Kamera lekko pływa „z ręki”.

Płaska animacja 2D z odręczną kreską w konwencji animowanych strasznych historii. Historia i postacie są własne.

| Plik | Co robi |
|---|---|
| `render.py` | część 1 → `zombie-psychiatryk.mp4` |
| `render2.py` | część 2 (dyżurka) → `zombie-psychiatryk-2.mp4`; korzysta z rysunków z `render.py` |
| `voice_clone.py` | lektor klonem głosu (Chatterbox) → `voice/l*.wav` i `voice/p2_l*.wav` |
| `voice/*.wav` | gotowy lektor (sklonowany głos autora) — w repo celowo, wymuszone mimo `.gitignore` |
| `zombie-psychiatryk-calosc-lekki.mp4` | obie części sklejone, lekka kopia (3 MB) |
| `probka.m4a` | próbka głosu autora — **nie ma jej w repo**; położyć obok skryptów przed `voice_clone.py` |

## Na innym komputerze (Windows/Linux/Mac)

Potrzebne: Python 3.11, ffmpeg w PATH.

```bash
pip install pillow numpy
python render.py          # część 1, ok. 1 min
python render2.py         # część 2
```

Klonowanie głosu (najszybciej z kartą NVIDIA):

```bash
python -m venv .venv-tts
.venv-tts/Scripts/pip install chatterbox-tts        # Windows; na Linux/Mac: .venv-tts/bin/pip
.venv-tts/Scripts/python -I voice_clone.py probka.m4a --takes 3
python render.py && python render2.py
```

### Ten PC (RTX 4070)

Środowisko jest w `C:\Users\igorf\.zombie-tts\venv` (Python 3.11, torch 2.6 + CUDA 12.4, chatterbox-tts, `setuptools<81` dla znaku wodnego perth). ffmpeg z winget.

```bash
C:\Users\igorf\.zombie-tts\venv\Scripts\python -I voice_clone.py probka.m4a --takes 3 --refs 1 --parts 2   # ok. 1 min
C:\Users\igorf\.zombie-tts\venv\Scripts\python -I voice_clone.py probka.m4a --takes 8 --refs 3             # najlepsza jakość, ok. 20 min
C:\Users\igorf\.zombie-tts\venv\Scripts\python render.py
C:\Users\igorf\.zombie-tts\venv\Scripts\python render2.py
ffmpeg -i zombie-psychiatryk.mp4 -i zombie-psychiatryk-2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -c:a aac -b:a 192k zombie-psychiatryk-calosc.mp4
```

Lektor jest suchy (bez pogłosu), odszumiony i z bramką na szum między słowami — filtr `FX` w `voice_clone.py`.

`render2.py` bez `-I` — importuje `render.py` z tego samego katalogu.

`voice_clone.py` z każdego zdania generuje `refs × takes` wersji, każdą sprawdza Whisper large-v3 (czy padł dokładnie ten tekst) i WavLM speaker-verification (podobieństwo do próbki), i bierze najbardziej podobną poprawną wersję mieszczącą się w ujęciu. Wszystkie oceny → `voice/raport.json`.

## Stan

- Część 1: gotowa, lektor z `probka.m4a` (8 podejść × 3 okna, podobieństwo 0,90–0,98).
- Część 2: gotowa, lektor z `probka.m4a` (3 podejścia × 1 okno, podobieństwo 0,91–0,97).

## Wersja angielska, lektor „studyjny”

Echo w lektorze pochodziło z pogłosu pokoju w `probka.m4a` — Chatterbox kopiuje akustykę referencji.
`studio_clean.py` (resemble-enhance, venv `pilot/.venv-enhance`) zdejmuje pogłos i szum → `probka-studio.wav`.

```bash
python -I voice_clone.py probka-studio.wav --lang en --takes 8 --refs 3     # → voice/en/
FILM_LANG=en python render.py && FILM_LANG=en python render2.py            # → *-en.mp4
```

Chatterbox prawie nie generuje pasma powyżej ~8 kHz — stąd „zamulony” głos. `studio_lines.py` odbudowuje
je resemble-enhance w gotowych zdaniach (oryginały → `voice-raw/`), długość zdań bez zmian:

```bash
../../pilot/.venv-enhance/bin/python studio_lines.py voice voice/en
```

Windows (cmd): `set FILM_LANG=en` przed renderem. Na Macu bez CUDA: `--refs 1 --takes 3 --no-sv`
(wielojęzyczny model zamiast angielskiego, bez sędziego WavLM) — wymaga kilku GB wolnego dysku na swap.

## Rozbiór w DocOS Studio

`studio_import.py` wpisuje gotowy film do projektu Studio: pomysł, Story Bible, Master Story, 2 akty, 5 sekwencji,
scenariusz, 10 scen i reżyserię (beaty, napięcie, 14 ujęć z czasami z renderów), a potem wideo każdego ujęcia,
lektora, efekty bez lektora (`audio()` z ciszą zamiast nagrań) i oś montażu. Notatki z produkcji → Continuity Editor.

```bash
python3 studio_import.py flow  <id projektu>   # potem w Studio: zatwierdź etapy, „Utwórz ujęcia z planu”
python3 studio_import.py media <id projektu>
```

`studio_signatures.mjs` liczy podpisy planów kodem Studio (`flowTypes.ts`), żeby plany nie były „nieaktualne”.
