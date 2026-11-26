# GTA Clipper (macOS)

Robi pionowe Shorty (1080×1920) z długich filmów i streamów GTA 6: znajduje nowe źródła, wybiera najlepsze
momenty, montuje (kamerka streamera na górze, gra na dole, napisy słowo po słowie, hook, okładka, opis z hashtagami),
sam sprawdza jakość, a Ty przeglądasz wszystko w aplikacji w przeglądarce. Działa tylko na Twoim Macu i nic nie
publikuje bez Ciebie.

Wymagania: macOS 14 (Sonoma) lub nowszy, Mac z procesorem Apple (M1–M4), Homebrew, ok. 5 GB wolnego miejsca.

## Instalacja (raz)

1. W Terminalu:
   ```
   brew install python@3.12 ffmpeg deno
   ```
   `deno` jest potrzebne yt-dlp do pobierania z YouTube.
2. Dwuklik `start_clipper.command` w tym folderze. Za pierwszym razem robi własne środowisko `.venv`, instaluje
   yt-dlp, faster-whisper (transkrypcja na Macu), OpenCV (twarze), streamlink (Twitch na żywo), czcionki napisów
   i model mowy (ok. 1 GB, kilka minut). Potem otwiera aplikację: http://localhost:8765
3. Skill dla Claude Code (opcjonalnie): `.venv/bin/python clipper.py install-skill`, potem restart Claude Code.

## Użycie

- **Aplikacja**: dwuklik `start_clipper.command`. Kreator na start: język filmów, streamerzy, które AI wybiera momenty.
- **Claude Code ze skillem**: „Zrób 10 Shortsów GTA 6 z najnowszych filmów, najpierw pokaż wybór”.
- **Terminal**: `.venv/bin/python clipper.py make --count 10` (wszystkie polecenia: `.venv/bin/python clipper.py -h`).

Folder roboczy: `~/gta-shorts` (zmiana: `--workspace` albo zmienna `CLIPPER_WORKSPACE`).

## Jak to działa

| Krok | Co robi |
|---|---|
| Znajdź | Wyszukiwanie YouTube + Twoi streamerzy (YouTube, Twitch, Kick) + `channels.txt`. Pobiera **tylko dźwięk**, czat (gdy jest) i dane „najczęściej odtwarzane”. Transkrypcja z czasem każdego słowa. |
| Sygnały | Dla każdej sekundy: głos podskoczył (`LOUD`), czat przyspieszył (`CHAT`), widzowie przewijali tu (`REPLAYED`), słowa o pościgu/wypadku/bójce/akrobacji/reakcji (`MOMENT`) → `HEAT` 0–100. Z tego ~30 kandydatów. |
| Wybór | **Free**: bez AI. **Smart**: AI czyta tylko kandydatów. **Deep**: AI czyta całe transkrypcje. AI = Claude Code, Codex, Gemini, Kimi, OpenCode, Ollama albo własne polecenie. |
| Montaż | Pobiera tylko wybrane sekundy (+8 s zapasu do poprawek). Szuka twarzy: kamerka streamera → na górze, gra na dole (albo bańka); twarz na cały ekran → kadr idzie za twarzą; brak kamerki → cały kadr na rozmyciu. Wycina ciszę, do 3 zbliżeń na największych reakcjach, napisy (13 stylów), hook przez pierwsze 3,5 s, normalizacja głośności, okładka, `post.txt`. Napisy rysuje kod (Pillow), a ffmpeg tylko je nakłada — nie trzeba ffmpeg z libass. Wypalanie przez libass: `"caption_engine": "ass"` w `settings.json`. |
| Kontrola | PASS / WARN / FAIL: format, długość, dźwięk, czarny lub zamrożony obraz, brak napisów lub kamerki, ocena AI, **muzyka w tle** (najczęstszy powód blokad Content ID — model YAMNet rozpoznaje ją także pod gadaniem). |
| Przegląd | A = zatwierdź, X = odrzuć, strzałki. Zmiana słowami („zakończ 2 s wcześniej”), inny wygląd, Twój głos (nagrany w przeglądarce, z Dyktafonu albo z iPhone’a przez AirDrop) — zawsze jako nowa wersja obok oryginału. |
| Plan | Przeciągnij na dzień albo „Rozłóż automatycznie” (co 90 min od 10:00, bez nocy). |
| Codziennie | Autopilot przez launchd (zadanie użytkownika w `~/Library/LaunchAgents`). Jeśli Mac o tej porze śpi, przebieg rusza po obudzeniu. Najpierw podgląd. Log: `~/gta-shorts/logs/autopilot.log`. |
| Na żywo | Twitch: nagrywa stream (ostatnie 10 min), czyta publiczny czat bez logowania. Gdy liczba różnych piszących w 10 s skacze ×3 ponad normę, tnie od 25 s przed do 10 s po i robi z tego Shorta. |

## Ograniczenia (uczciwie)

- Na żywo tylko Twitch. Kick i YouTube Live: Shorty z nagrania po streamie.
- Czat z powtórek: YouTube tak. Nagrania z Twitcha — nie (yt-dlp nie pobiera ich czatu), więc tam wybór opiera się
  na głośności, słowach i AI. Czat Twitcha na żywo działa.
- Wykrywanie muzyki może przepuścić cichy podkład bez wokalu pod głośnym gadaniem.
- Wykrywanie kamerki to przybliżenie z położenia twarzy. Nietypowe nakładki mogą dać zły kadr → QC daje WARN,
  a w szczegółach Shorta zmienisz układ.
- Transkrypcja idzie na procesorze (faster-whisper nie używa GPU Maca) i przy długich streamach to najdłuższy krok.
  Na słabszym Macu ustaw model „base”.
- Polecenia AI innych niż Claude Code (Codex, Gemini, Kimi, OpenCode) są szablonami — sprawdź je w Ustawieniach.
- Klipuj tylko streamerów, którzy na to pozwalają.

## Testy

```
.venv/bin/python -m unittest discover -s tests -v
```
