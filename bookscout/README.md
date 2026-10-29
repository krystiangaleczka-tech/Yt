# Book Scout

Szuka w katalogach bibliotek książek, których nie ma w pełni w sieci, ocenia je przez Claude
(subskrypcja, bez API) i porównuje z YouTube. Wynik to ranking tematów na filmy z prognozą wyświetleń,
zarobku, kosztu, trudności i ROI. Wybrane tematy trafiają do DocOS (`tematy.json`).

```
losowanie (Open Library / Biblioteka Narodowa) → dostępność cyfrowa (OL, Internet Archive, HathiTrust, Google Books)
→ ocena Claude (kopiuj–wklej albo plik dla Claude Code) → rynek (Wikipedia + YouTube) → scoring → ★ → DocOS
```

## Uruchomienie

```bash
.venv-studio/bin/python -m bookscout          # http://127.0.0.1:8890
```

Wymaga tylko środowiska Studio (`fastapi`, `uvicorn`, `httpx`). Dane trzyma w `bookscout/data/` (poza gitem).

Opcjonalnie skopiuj `bookscout/.env.example` do `bookscout/.env` i wpisz `GOOGLE_API_KEY`
(YouTube Data API v3 + Books API). Bez klucza popyt liczony jest z Wikipedii, a YouTube sprawdzisz przez Claude Code.

## Przepływ

1. **Losuj**: wybierz kategorię albo „Losowo” i źródło.
   - **Open Library (EN)**: książki anglojęzyczne. Domyślnie tylko te bez e-booka.
   - **Biblioteka Narodowa (PL→EN)**: polskie książki, które nie są przekładami (arbitraż językowy dla kanału EN).
2. **Ocena Claude**:
   - *Kopiuj–wklej*: „Przygotuj prompt” → wklej w claude.ai → wklej odpowiedź JSON → „Importuj oceny”.
   - *Claude Code*: „Zapisz paczkę do pliku” → w Claude Code: `oceń paczkę Book Scout <id>` → „Importuj z plików”.
     Claude zapisuje odpowiedź jako `bookscout/data/batches/<id>.response.json`.
3. **Ranking**: „Analizuj rynek” pobiera odsłony Wikipedii i (z kluczem) 25 wyników YouTube na temat.
   Bez klucza: „Analiza YouTube przez Claude Code”, czyli plik, który Claude Code uzupełnia narzędziem
   TubeAlfred (1 kredyt na temat).
4. Oznacz najlepsze tematy ★ i kliknij „Eksport ★ do DocOS”. Przy dokładnie 10 tematach plik przechodzi wprost
   przez `docos.py save-topics`. Pojedynczy temat otwórz przez `docos.py new`.

## Wskaźniki

| Wskaźnik | Skąd |
|---|---|
| Ciekawość 0–100, trudność 1–10, materiały wizualne, godziny researchu | ocena Claude |
| Popyt 0–100 | odsłony artykułu Wikipedii (12 mies.) i mediana wyświetleń filmów na temat |
| Konkurencja 0–100 | trafne filmy long-form, filmy >100 tys. wyświetleń, w tym z ostatnich 24 mies. |
| **Ratio** popyt / konkurencja | >1,5 = luka na rynku |
| Ratio wyświetlenia / subskrypcje | czy temat „ciągnie” także na małych kanałach |
| Wyjątkowość | ciekawość × brak wersji cyfrowej (+15% bez angielskiego wydania) |
| Wyświetlenia (12 mies.) | mediana podobnych filmów × wielkość Twojego kanału, przedział ×0,4–×2,5 |
| Zarobek, koszt, ROI | wyświetlenia × RPM; godziny × stawka + koszty stałe (Ustawienia) |
| Wynik | 25% ciekawość, 20% popyt, 15% wolne pole, 15% wyjątkowość, 15% ROI, 10% łatwość |

Prognozy są orientacyjne (±50–100%) i służą do porównywania tematów między sobą.
Wątki z oceny Claude to hipotezy do sprawdzenia w książce, a nie fakty (zasada prawdy DocOS).

## Testy

```bash
.venv-studio/bin/python -m unittest bookscout.tests.test_bookscout -v
```
