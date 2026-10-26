# Typy ujęć, przejścia, style

Format w shot liście: `[WIZ n] (kadr / ruch) TYP: opis (X s)`

| Typ | Co robi | Parametry w opisie |
|---|---|---|
| ARCHIWUM | zdjęcie (najazd Ken Burns) lub wideo; małe skany jako „dokument na stole” | `FILE:`, `START:` (wideo), `CAPTION:` |
| DOKUMENT | jak ARCHIWUM, dla dokumentów/danych; spektrogramy rysowane proceduralnie | `FILE:` |
| WAVEFORM | żywy oscylogram z prawdziwego nagrania | `FILE: x.wav`, `START:` |
| SPEKTRO | spektrogram prawdziwego nagrania odsłaniany w czasie rzeczywistym | `FILE:`, `START:`, `SPAN:`, `MAXHZ:` |
| PRASA | plansza prasowa: dosłowny cytat + marker, „— Pismo, data” (własny layout) | `"cytat" — Pismo, data` |
| QA | rozmowa: pytanie narratora + dosłowny cytat jako odpowiedź | `Q: "…" A: "…" — źródło` |
| CYTAT | cytat maszynopisem | `"cytat" — autor, źródło` |
| LICZNIK | animowane odliczanie liczby z faktów | `"0 → 3,219 km" "podpis"` |
| HASŁO | kinetyczne słowa (auto-dopasowanie rozmiaru) | `"TEKST"` |
| LUPA | przybliżenie detalu z ramką | `FILE:`, `ZOOM: x,y,w`, `"podpis"` |
| DIAGRAM | schemat (kanał SOFAR) | — |
| SPLIT / PORÓWNANIE | porównanie dwóch obrazów | `FILES: a | b`, `"lewy — pod" "prawy — pod"`, styl |
| STOS | zdjęcia spadające na stół | `FILES: a | b | c` |
| MAPA | Pacyfik (kropki, fale), NE Pacyfik (Juan de Fuca), widok polarny | słowa kluczowe w opisie |
| OŚ_CZASU | oś czasu | `"1997 / 2001 / 2005"` |
| PODPIS | belka z imieniem na tle FILE (nie sugeruje, że osoba jest na zdjęciu) | `"IMIĘ / funkcja" FILE:` |
| TYTUŁ | napis (styl wybierany polem `style`) | `"linia 1 / linia 2"`, `over black`, `stamped` |
| AI_OBRAZ | kadr AI — zawsze z podpisem „AI reconstruction” (v5 nie używa) | `FILE:` lub `PROMPT:` |

## Przejścia (`transition`)
`cut` · `dissolve` · `dip` (przez czerń) · `slide` · `whip` (rozmycie ruchu) · `zoom` · `flash` · `burn` (przepalenie taśmy).
Domyślnie: przenikanie na granicy beatów (poza ACTION), cięcie wewnątrz beatu.

## Style napisów (`style`)
`typewriter` · `stamp` · `lower-left` · `top-right` · `center-big` · `side-bar` · `highlight` · `minimal`

## Style porównań (`style` dla PORÓWNANIE/SPLIT)
`cards` · `split` · `diagonal` · `wipe` (suwak przed/po) · `pip` (obraz w obrazie)

## Zasady (sprawdzane przez `docos.py check`)
- ujęcia 4.5–7 s (STORY), szybkie serie 1.5–3.5 s tylko w ACTION / EUREKA
- min. `min_unique_visuals` różnych materiałów, każdy max 2×
- dwie plansze tekstowe nigdy obok siebie; ten sam styl nie dwa razy z rzędu; to samo przejście nie 3× z rzędu
- max ~6% ujęć maszynopisem; max 3× ten sam typ pod rząd
