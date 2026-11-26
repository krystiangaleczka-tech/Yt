---
name: gta-clipper
description: Robi pionowe Shorty (9:16) z długich filmów i streamów GTA 6 — szuka nowych źródeł, wybiera najlepsze momenty, montuje (kamerka streamera na górze, gra na dole, napisy słowo po słowie, hook), sprawdza jakość i otwiera aplikację do przeglądu. Użyj, gdy użytkownik prosi o Shorty / klipy / rolki z GTA 6, ze streamu, z linku YouTube/Twitch/Kick albo z pliku, o polowanie na żywo na Twitchu, o dodanie głosu do Shorta albo o otwarcie aplikacji Clipper.
---

# GTA Clipper

Silnik i aplikacja leżą w `{{APP_DIR}}`. Wszystkie polecenia uruchamiaj tak:

```
"{{PYTHON}}" "{{APP_DIR}}/clipper.py" <polecenie>
```

Folder roboczy (Shorty, transkrypcje, ustawienia): domyślnie `~/gta-shorts`.
Do autora pisz po polsku. Nigdy niczego nie publikuj sam — tylko na wyraźną prośbę i tylko zatwierdzone Shorty.

## Pierwsze uruchomienie

Program działa na macOS. Jeśli `"{{PYTHON}}" "{{APP_DIR}}/clipper.py" doctor` pokazuje braki: uruchom `setup`
(instaluje yt-dlp, faster-whisper, OpenCV, streamlink, czcionki, model mowy — kilka minut, tylko raz).
Brak ffmpeg albo deno: `brew install ffmpeg deno`. ffmpeg bez libass nie przeszkadza — napisy rysuje kod (Pillow).

## Przepis: „Zrób N Shortsów GTA 6 z najnowszych filmów”

1. **Znajdź**: `find --count 5` (albo `find --url <link> [<link>…]`, albo plik z dysku jako link).
   U streamerów z listy gra jest sprawdzana z rozdziałów Twitcha / kategorii Kicka / opisu YouTube, więc tytuł nie musi
   mówić „GTA”; z długiego streamu brane są tylko fragmenty z GTA. Trwający stream: brane jest to, co już było.
   Pobiera tylko dźwięk, robi transkrypcję na tym PC. Stream dłuższy niż ~6 h: `--window 1:00:00-2:00:00`.
2. **Wybierz** — Ty jesteś AI, więc nie wołaj drugiego AI:
   `pick --mode agent --count N` → przeczytaj `~/gta-shorts/AGENT_TASK.md` (zasady + ~30 kandydatów z tagami
   `[LOUD +12dB] [CHAT x4 KEKW] [REPLAYED x5] [MOMENT chase] [HEAT 87]`). Zapisz listę JSON do
   `~/gta-shorts/picks_raw.json` i uruchom `pick --from-raw`. Trzymaj się zasad z pliku:
   - premisa przed szczytem; samo krzyczenie bez premisy = 0 pkt,
   - ocena 0–100 = czy obcy o 1 w nocy dogląda do końca; test obcego (2 z 3 „tak”),
   - maks. 2 Shorty z jednego źródła, puenta w ostatnich 40%, koniec NA puencie (nigdy na logo/sponsorze),
   - hook: maks. 6 słów, WIELKIMI, imię streamera pierwsze; tytuł ≤ 70 znaków; 3–5 hashtagów; 1–3 słowa kluczowe.
3. **Pokaż tabelę** wyboru (moment, hook, dlaczego) i **czekaj** na „wygląda dobrze, zrób je”. Na prośbę o podgląd:
   `peek` (4 klatki na moment w `~/gta-shorts/peek/`), obejrzyj je i popraw złe okna.
4. **Zmontuj**: `render` (pobiera tylko wybrane sekundy, 3 naraz; słaby PC: zmienna `CLIPPER_WORKERS=1`).
5. **Kontrola**: wynik `PASS / WARN / FAIL` jest w logu i w `meta.json`. FAIL → jedna próba poprawki
   (`change <id> "..."` albo `clip <źródło> <start> <koniec> --hook "..."`), potem odpuść.
6. **Oddaj**: podsumuj (ile PASS/WARN/FAIL, gdzie są pliki, `overview_*.jpg`) i zaproponuj
   `app` — przegląd w przeglądarce (A = zatwierdź, X = odrzuć, strzałki).

Zamiast kroków 1–4 bez pytania o wybór: `make --count N [--mode free|smart|deep] [--url …]`.

## Inne prośby

| Prośba | Polecenie |
|---|---|
| „otwórz aplikację Clipper” | `app` (strona http://localhost:8765, działa tylko na tym PC) |
| „skończ Shorta 3 dwie sekundy wcześniej” | `change <id> "zakończ 2 s wcześniej"` — oryginał zostaje, powstaje v1 |
| „styl beast, kamerka pod grą, znak wodny @kanał” | `look <id> --style beast --flip --watermark "@kanał"` |
| „wstaw mój głos po puencie w Shorcie 1” | `voice <id> [plik] --at payoff` (bez pliku: najnowsze nagranie z Dyktafonu, Pobranych — np. AirDrop z iPhone’a — albo Biurka) |
| „poluj na żywo na xqc” | `live xqc` (Twitch; tnie, gdy czat wybucha; `--ratio 2 --min 40` dla głośnego czatu) |
| „zapisz ostatnie 10 minut streamu” | `live buffer <kanał>` |
| „rozplanuj zatwierdzone” | `schedule --every 90 --first 10:00` (`--preview` = tylko podgląd) |
| „rób to codziennie o 9” | `autopilot preview`, a po zgodzie autora `autopilot on` (launchd; godzina w Ustawieniach/`settings.json`) |
| „daj opisy do wklejenia” | `posttext` |

`<id>` to nazwa folderu w `~/gta-shorts/shorts/` (np. `20261125-0930_01_xqc`); „Short 1” = folder z `_01_`
z najnowszej partii.

## Publikacja przez MCP (tylko na prośbę)

Zatwierdzone Shorty: `shorts/<id>/meta.json` ma `"status": "approved"`, plik = `versions[current].file`,
opis w `post.txt`, termin w `scheduled_at` (unix). Po publikacji ustaw `"published": true`.

## Zasady

- Klipuj tylko streamerów, którzy na to pozwalają (`streamers.json`, pole `rules`: `no` = nie ruszaj).
- Napisy pokazują słowa streamera; obelgi są wykropkowane tylko na ekranie, dźwięk zostaje.
- Nie rób całego przebiegu od nowa, żeby poprawić jeden Short — od tego są wersje.
