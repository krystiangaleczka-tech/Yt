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

## Rig postaci i efekty dźwiękowe (PC, 11.11.2026)

Ujęcia dni 1–30 w większości stały w miejscu (575 z 689 ma kamerę „stat”). 256 z nich dostało grę aktorską:

- `rig_a.py` — rig: głowa obraca się na szyi i skręca (yaw), tułów pochyla się i unosi ramiona, ręka gestykuluje,
  usta idą za prawdziwym oknem kwestii EN. Akcje: `mowi`, `slucha`, `kiwa`, `kreci`, `odwraca`, `patrzy`, `w_gore`,
  `w_dol`, `wzrusza`, `nachyla`, `cofa`, `wstrzymuje`, `oddycha`, `rozglada`, `wzdycha`, `budzi`, `kolysze`, `ciezar`,
  `gest`, `kaszle`, `przelyka`. `Pen.push/pop` w `render.py` to stos przekształceń (pusty = rysunek bez zmian).
- `rig_dni.py` — tabela: dzień → ujęcie → postać → akcja (z komentarzem: opis kadru i kwestia). Bez rigu zostały celowo
  twarze za szybą i w okienkach (WYTYCZNE 1.1), rzeczy przy twarzy (słuchawka, kubek, ręcznik, lornetka), dłoń na ustach
  i ujęcia, w których bezruch pana Henryka jest treścią. Rzeczy rysowane na twarzy po `face_cu` (łzy, uśmiech, nadęte
  policzki, słuchawka) idą przez `kit_a.on_face`, więc trzymają się głowy.
- `FILM_RIG=0` — render bez rigu (porównania); ujęcia bez wpisu w tabeli są piksel w piksel takie jak wcześniej.
- `arkusz_rig.py <png> dzien=N` — arkusz klatek ujęć z rigiem (6 chwil na ujęcie).
- Kurz w świetle piwnicy i apteki (looki BASE/CELL) — `dzien_base.dust`; `FILM_KURZ=0` wyłącza.

Efekty: `efekty_dni.py` (na PC napisany od nowa — wersja z Maca nie trafiła do repo) syntezuje tło miejsca (piwnica
z kapaniem, oddział ze świetlówkami wg stanu sieci/agregatu, noc z wiatrem, podwórze, płonące miasto od d20) i dźwięk
każdego wydarzenia z rozpiski i opisu kadru: kroki, drzwi, kraty, zamki, walenie w drzwi, huki, metal, szuranie, jęki
zarażonych, oddechy, kaszel, iskry, agregat, woda, strzały, dron, pianino, nucenie, karta dnia („dum”), narastanie przed
kolejnym dniem. Uderzenia trafiają w chwilę ruchu w kadrze (różnice klatek wideo). Alarm d14, alarm karetki d10,
alarm z kołysanką d30 płyną przez kilka ujęć: blisko w miejscu źródła, z oddali gdzie indziej.
`film_en.py dzwiek` miksuje `build/efekty/eNN.wav` z lektorem (−6 dB pod głosem); `eNN_studio.wav` (−8 dB pod
kwestiami) idzie na ścieżkę Efekty w Studio.

Render 1440p: `FILM_ENC=nvenc python -I film_en.py obraz 1 … 30 -j 6` (koder karty — rysowanie jest wtedy wąskim
gardłem, ok. 1 h; x264 slow trwał ok. 5 h). Wszystkie jednostki muszą mieć ten sam koder, bo `sklej` łączy je bez
przekodowania (zimne otwarcie przekodowane NVENC-iem z poprzedniego renderu).

Studio na PC: `python -I studio_pc.py` — zakłada projekt „Oddział C · Do świtu (EN 1440p, PC)”, każde ujęcie jako scenę
z klipem 720p, kwestie EN na ścieżce Lektor, efekty dzień po dniu na ścieżce Efekty; ujęcia z rigiem mają w opisie
„Rig (gra aktorska): …”.

### Poprawki po pierwszym przeglądzie reżysera (12.11.2026)

- **Bez bzyczenia:** tło nie ma już buczeń sieciowych (fala prostokątna 100 Hz świetlówek, 55/49/25 Hz pod spodem)
  ani przesterowanego pogłosu (ogon pogłosu był nienormalizowany, +20 dB).
- **Plan miksu:** każdy dźwięk ma poziom ze skali zdarzenia, napięcia sceny i tempa ujęcia (zasada w Podręczniku →
  Rytm 10–12, liczby w `build/efekty/eNN.json` → `ujecia[].zdarzenia[].db`). Osobne pliki: `eNN_tlo.wav`,
  `eNN_zdarzenia.wav` (+ wersje `_studio` ściszone pod kwestiami).
- **Muzyka:** `muzyka_dni.py` — syntezowana, nastrój z beatów rozpiski (pad, puls, napęd, motyw kołysanki, finał);
  `build/muzyka/mNN.wav` i frazy `cue/dNN_KK.wav`; `film_en.py dzwiek` miksuje ją pod lektorem (−8 dB pod głosem).
- **Profil i postacie w oddali:** `kit_a._profile_face` (głowa skręcona o ≥ 0,55 rysuje się z profilu, jak zarażony
  ze zbliżenia d04_22) i `kit_a.scaled` (kreska i jej drżenie w skali postaci, małe elipsy bez „gotowania się”).
- Studio: `studio_aktualizuj.py <projekt> --obraz --dzwiek` — nowy obraz ujęć i ścieżki Tło / Efekty / Muzyka.

### Przegląd całego filmu (13.11.2026)

- **Rytm kwestii EN:** ujęcia były liczone pod polskie kwestie, a `en_film.placement` wpychał dłuższe angielskie nagrania
  pod cięcie (124 z 287 kwestii kończyło się 0,25 s przed cięciem, d01_18 wychodziła za cięcie). `en_film.timing`
  wydłuża ujęcie z kwestią: oddech przed ≥ 0,5 s, pauza po 0,6–1,2 s; `separate` trzyma ¼ s różnicy z sąsiadami.
  Używają go `dzien_base.setup` i `render_d01`. Dni 1–30 EN: 36,8 → 40,3 min.
- **Kadry:** framugi (d01_12, d14_12), drzwi izolatki otwierane do środka (`kit_a.iso_door`, d16_16), biurko i stół
  z miejscem za nimi (`kit_a.duty_desk`, `kit_a.staff_table`), słuchawka w dłoni (`kit_a.handset(..., who=)`,
  `kit_a.listening`), okno łącznika w perspektywie (d13_12), ciągłość paczki (d10_01) i inne — tabela w WYTYCZNE 5.
- Kolejność po zmianie długości ujęć: `FILM_ENC=nvenc python -I film_en.py obraz 1 … 30 --res 720 -j 6` → `build/en-720`,
  skasuj `build/efekty/ruch_d*.npy`, `efekty_dni.py --wideo build/en-720`, `muzyka_dni.py`, potem
  `studio_aktualizuj.py <projekt> --czasy --dzwiek` (obraz, oś, lektor i ścieżki dźwięku na nowych miejscach).
