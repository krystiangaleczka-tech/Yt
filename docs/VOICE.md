# Lektor (klon głosu)

Model: **Chatterbox Multilingual** (Resemble AI, MIT). Każde nagranie zawiera niesłyszalny watermark **Perth**
(znakowanie treści AI) — nie wyłączamy go.

## Próbka głosu
- 15–30 s czystej mowy, jeden głos, cichy pokój, bez muzyki, mikrofon 15–20 cm od ust
- spokojny, „dokumentalny” ton — model kopiuje też sposób mówienia
- **model kopiuje też pogłos pokoju** — próbkę przepuszcza się przez resemble-enhance:
  `docos/lektor_studio.py probka` → `pilot/assets/ref_studio.wav`; cały sposób (3 podejścia na kwestię, suche
  z odbudowanym pasmem, wybór podejścia z oddechami) w Podręczniku pracowni → Lektor (`docs/podrecznik/07_LEKTOR.md`)
- `pilot/clone_voice.py` przygotowuje starą próbkę `ref_clean.wav` (mono 24 kHz, bez odszumiania — z pogłosem);
  Studio („Dodaj lektora”) wciąż jej używa, chyba że `DOCOS_VOICE_REF` wskazuje `ref_studio.wav`
- **próbki nie publikuj** — z niej da się sklonować Twój głos (dlatego nie ma jej w repo)

## Jak `voice_beats.py` dba o naturalność
1. **Zdanie po zdaniu** — krótsze fragmenty = stabilniejszy model.
2. **Wymowa** — liczby i skróty zamieniane na słowa (`NOAA` → „Noah”, `1997` → „nineteen ninety-seven”);
   tekst scenariusza się nie zmienia (lista `SAY`).
3. **Jedno tempo filmu** — mierzy sylaby/s każdego zdania; zdania odstające o >18% od celu (`--sps`, domyślnie 4.0)
   są generowane ponownie (do `--takes` podejść), potem drobna korekta tempa 0.85–1.2.
4. **Mikropauzy** — ~0.32 s po zdaniu, ~0.45 s po pytaniu, ~0.2 s w wyliczeniach, +0.18 s przed krótką puentą,
   lekki losowy rozrzut. Bez wstawiania oddechów.
5. **Cache** — `voice/sent/<beat>_<sha1(zdania)>.wav`: po edycji narracji generują się tylko zmienione zdania.

```bash
pilot/.venv-tts/bin/python -I docos/voice_beats.py projekt.json probka.wav projekt_dir/voice --sps 4.0 --takes 3
pilot/.venv-tts/bin/python -I docos/voice_beats.py projekt.json probka.wav projekt_dir/voice --beat B03   # jeden beat
```

## Znane ograniczenia
- Chatterbox potrafi czytać zdania w bardzo różnym tempie (zmierzone 2.2–5.4 syl./s) — stąd dogrywki.
- Na 8 GB RAM ~10× wolniej niż czas rzeczywisty.
- Kokoro (`pilot/gen_voice.py`) — szybki lektor zastępczy do podglądów (sekundy), bez klonowania.
