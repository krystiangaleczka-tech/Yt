---
name: dokument-scenariusz
description: Pisanie scenariuszy i scenopisów (narracja + shot list) do faceless dokumentów YouTube systemem DocOS — beat po beacie, z rejestrem faktów, krzywą energii, chaosem i eksportem do arkusza/renderu. Użyj, gdy użytkownik chce stworzyć, zaplanować, dopisać albo sprawdzić scenariusz filmu dokumentalnego / wyjaśniającego na YouTube.
---

# DocOS — scenariusz dokumentu YouTube

Narzędzie: `/Users/krystiangaleczka/Documents/YT/docos/docos.py` (uruchamiaj `uv run -q <ścieżka>/docos.py ...`).
Projekt = jeden plik JSON (źródło prawdy). Arkusz .xlsx to widok do planowania (edytowalny, wczytywany przez `import`).
Ty (Claude) jesteś silnikiem piszącym — nie potrzeba żadnego API.

## Zasady nadrzędne
- **Dokument, nie fikcja.** Każda liczba, data, nazwisko i cytat musi być w rejestrze faktów z źródłem. Statusy: VERIFIED / DISPUTED (tylko z zastrzeżeniem) / UNVERIFIED (nie stwierdzaj) / DRAMATIZATION (rekonstrukcja, oznacz w shot liście).
- Fakty weryfikuj w sieci (WebSearch/WebFetch) przed wpisaniem jako VERIFIED; podawaj URL. Gdy czegoś nie da się potwierdzić — DISPUTED/UNVERIFIED, nie zmyślaj.
- 1 beat = 1 emocja wejściowa → 1 wyjściowa (Turn z jedną strzałką).
- Pisz tylko bieżący beat. Kontekst to wyłącznie N-1/N-2 z promptu — nie przepisuj poprzednich beatów.
- Shot list produkcyjny (Wide, ECU, Macro, POV, Match Cut, Ken Burns), nie literacki. Bohater pod presją działa, nie czeka.

## Workflow
0. **Etap redakcyjny Documentary** przy nowym kanale/odcinku: przeczytaj `docs/EDITORIAL.md` w repozytorium YT.
   Wczytaj profil lub utwórz go przez `channel`; wygeneruj dziesięć propozycji z promptu `topics`, zapisz je przez `save-topics`.
   Jeśli temat już podano, pomiń propozycje. Użyj `new ... --channel <profil.json>`, wykonaj research,
   uzupełnij kartę z `story`, zatwierdź przez `lock` i dopiero pisz beaty. Polecenia nie wywołują API modeli.
   W trybie prowadzonym pokaż kartę do zatwierdzenia; przy zleceniu automatycznym sprawdź ją i kontynuuj.
   Po zmianie założeń użyj `unlock` i ponownie `lock`. Starsze projekty bez karty działają jak wcześniej.
1. **Start**, jeśli projektu jeszcze nie utworzono: `docos.py new <projekt>.json "Tytuł"` w folderze odcinka (domyślnie `~/Documents/YT/projekty/<slug>/`).
2. **Research → fakty**: uzupełnij `facts` (F1, F2…) z źródłami. Bez faktów nie planuj beatów.
3. **Struktura**: uzupełnij `meta` (logline, teza, curiosity gap, narrator, język narracji, target_minutes, visual_style, master_outline), `chapters` (segment + default_dynamic), `subchapters`, potem `beats` (akcja, cel, turn, typologia, dynamika, chaos, fakty, sekundy).
   - Segmenty: COLD_OPEN (energia 8–10), CONTEXT, INVESTIGATION (4–7, Looped Arc: RISING_ACTION → CONFLICT → COMEBACK → EVIDENCE → PAYOFF → TRANSITION), TWIST (7–9), RESOLUTION, OUTRO.
   - Dynamika: ACTION(10) / EUREKA(8) / STORY(5) / STATIC(3) / CHILL(2). Puste pole = dziedziczy z rozdziału, potem z segmentu.
   - Chaos: NONE / MICRO / MINI / MACRO — w dokumencie zwrot musi wynikać z faktu z rejestru.
   - Beat ≈ 15–45 s. Suma ≈ target_minutes.
4. **Kontrola planu**: `docos.py check` i `status`. Napraw: >3 ACTION pod rząd, >2 CHILL/STATIC pod rząd, średnia energii segmentu poza zakresem, wielostopniowe Turny, 4× ta sama polaryzacja.
5. **Pętla pisania** (dla każdego beatu):
   - `docos.py next <projekt>.json` → przeczytaj prompt (pierwszy raz przeczytaj też `docos.py system`).
   - Napisz odpowiedź DOKŁADNIE w formacie (Narracja / Shot List z `[WIZ n] (kadr) TYP: opis (X s)` / Fakty użyte / Połączenie do N-1) do pliku tymczasowego w scratchpadzie.
   - `docos.py save <projekt>.json <BEAT> <plik>` → popraw beat, jeśli wypisze ostrzeżenia (szczególnie [FAKTY]).
   - Dla długich filmów pisz partiami (np. 5 beatów), pokazując użytkownikowi postęp; nie pisz kilku beatów w jednym kroku.
6. **Finał**: `docos.py check`, potem `docos.py export <projekt>.json` → `.xlsx` (heatmapa, krzywa energii, kontrola), `_script.md` (scenariusz + źródła do opisu), `_narration.txt` (dla lektora), `_render_plan.json`.
7. **Materiały** (opcjonalnie): `~/Documents/YT/pilot/.venv/bin/python -I ~/Documents/YT/docos/make_assets.py <render_plan.json> [--beat B01] [--limit N]` → kadry AI_OBRAZ lokalnie (SD 1.5, ~1 min/kadr na M3, uruchamiaj w tle) + `assets_todo.md` (archiwum/dokumenty/plansze do zdobycia).
   Lektor: `_narration.txt` → klon głosu użytkownika `~/Documents/YT/pilot/clone_voice.py` (Chatterbox, MIT, zostawia watermark Perth — nie wyłączaj go).

## Produkcja filmu (v5)
- Materiały: tylko prawdziwe (NOAA/NASA/US Navy = domena publiczna, Wikimedia Commons z licencją) — `fetch_commons.py search|get` zapisuje licencje do `licenses.json`. AI tylko wyjątkowo i z podpisem "AI reconstruction".
- Tempo dokumentu: ujęcia 4.5–7 s; szybkie serie tylko w hooku/kulminacji. Min. 25 różnych materiałów, każdy max 2×, plansze tekstowe nigdy obok siebie, zmienne style napisów i przejścia (`docos.py check` to pilnuje).
- Typy ujęć: ARCHIWUM (zdjęcie/wideo + START:), DOKUMENT, PRASA, QA, CYTAT, LICZNIK, HASŁO, LUPA (ZOOM:), WAVEFORM/SPEKTRO (prawdziwe audio), DIAGRAM, SPLIT/PORÓWNANIE (FILES: a | b), STOS, MAPA, OŚ_CZASU, PODPIS, TYTUŁ.
- Pola ujęcia: `transition` (cut, dissolve, dip, slide, whip, zoom, flash, burn), `style` napisu (typewriter, stamp, lower-left, top-right, center-big, side-bar, highlight, minimal) lub porównania (cards, split, diagonal, wipe, pip).
- Sekcja `render` w projekcie: media, voice, lead/tail, cues (prawdziwe nagrania), credits, silence_before.
- Lektor: `voice_beats.py` (zdanie po zdaniu, jedno tempo, mikropauzy, cache po treści zdania).
- Render: `render_doc.py PROJEKT.json --out film.mp4 --quality preview|final` (segmenty per beat z cache, równolegle).
- **Edytor w przeglądarce**: `~/Documents/YT/pilot/.venv/bin/python -I ~/Documents/YT/docos/editor.py PROJEKT.json --port 8766` → http://localhost:8766 (storyboard z miniaturami, biblioteka mediów, podgląd ~30 s po zmianie).

## Edycja w arkuszu
Użytkownik może planować w Excel/Sheets: `export` → edycja zakładek Ustawienia/Rozdziały/Fakty/Beaty → `docos.py import <projekt>.json <plik.xlsx>`. Import nie nadpisuje napisanych narracji.

## Przykład
`~/Documents/YT/docos/examples/bloop.json` — 3-minutowy dokument o „The Bloop” (B01 napisany).
