# Architektura

```
projekt.json ──► docos.py (plan, prompty, check, export)
     │                │
     │                └─► render_plan (ujęcia z czasem)
     │
     ├─► voice_beats.py ──► voice/B01.wav … (+ voice/sent/<beat>_<sha1>.wav cache zdań)
     │
     └─► render_doc.py
            plan_film()      oś czasu: beat = lead + lektor + tail; ujęcia skalowane (szybkie cięcia < 2 s nie są rozciągane)
            render_segment() worker: jeden beat → wideo bez dźwięku (cache: .render_cache/<jakość>/<beat>_<hash>.mp4)
            mix_audio()      lektor + podkład + efekty + prawdziwe nagrania (cues), przyciszanie pod lektorem
            render_film()    równoległy render brakujących segmentów → concat → mux audio → loudnorm -14 LUFS
                 ▲
editor.py (HTTP, stdlib) ── editor.html (storyboard) ── /api/state, /api/save, /api/render, /api/voice, /thumb
```

## Model danych projektu (`*.json`)
- Opcjonalne `channel` i `story_lock` — kopia profilu Documentary oraz zatwierdzana karta historii z bankiem ID faktów.
  `editorial.py` obsługuje prompty tematów, historię tytułów i kontrolę zmian karty; szczegóły w [EDITORIAL.md](EDITORIAL.md).
- `meta` — tytuł, logline, teza, curiosity gap, narrator, relacja z widzem, słownik, zakazy, język, target_minutes, wpm,
  visual_style, master_outline, min_unique_visuals
- `chapters[]` — `id, title, description, segment, default_dynamic`; `subchapters[]`
- `facts[]` — `id, claim, status (VERIFIED|DISPUTED|UNVERIFIED|DRAMATIZATION), source, url, note`
- `beats[]` — `id, segment, scene_no, scene_desc, chapter, subchapter, action, goal, turn, typology, dynamic, chaos,
  facts[], seconds` + po napisaniu: `narration, shots[], facts_used[], link (Połączenie do N-1), raw`
- `shots[]` — `n, framing, asset, desc, prompt, dur` + opcjonalnie `transition, style`
  - w `desc`: tekst w "cudzysłowach", `FILE: plik`, `FILES: a | b`, `START: s`, `ZOOM: x,y,w`, `SPAN: s`, `MAXHZ: hz`, `CAPTION: "…"`
- `render` — konfiguracja montażu (media, voice, lead/tail, cues, credits, credit_lines, silence_before)

## Klucz cache segmentu
SHA1 z: wersji renderera, jakości, ujęć beatu (z czasami, przejściami, indeksem użycia pliku), ostatniego ujęcia
poprzedniego beatu (przejście/tło tytułu), dat modyfikacji użytych plików, flag pierwszy/ostatni beat.
Zmiana jednego beatu → render tylko jego (i ewentualnie następnego). Zmiana długości lektora zmienia tylko ten beat.

## Pliki
| Plik | Rola |
|---|---|
| `docos/docos.py` | DocOS CLI: new, system, prompt, next, save, check, status, export, import |
| `docos/render_doc.py` | montaż v5: typy ujęć, przejścia, style, porównania, audio, segmenty, cache |
| `docos/render_film.py` | wspólne narzędzia (fonty, spektrogram, mapy, tytuły, Ken Burns) + renderer v2 |
| `docos/editor.py`, `editor.html` | edytor w przeglądarce |
| `docos/voice_beats.py` | lektor (Chatterbox) |
| `docos/fetch_commons.py`, `fetch_media.py` | materiały z licencjami / odtworzenie mediów |
| `docos/make_assets.py` | kadry AI (SD 1.5) z planu — opcjonalnie |
| `pilot/*` | pilot 10 s: `gen_images.py`, `gen_voice.py` (Kokoro), `clone_voice.py`, `compose.py` |
