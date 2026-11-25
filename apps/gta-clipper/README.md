# GTA Clipper

Robi pionowe Shorty (1080×1920) z długich filmów i streamów GTA 6: znajduje nowe źródła, wybiera najlepsze
momenty, montuje (kamerka streamera na górze, gra na dole, napisy słowo po słowie, hook, okładka, opis z hashtagami),
sam sprawdza jakość, a Ty przeglądasz wszystko w aplikacji w przeglądarce. Działa tylko na Twoim PC i nic nie
publikuje bez Ciebie.

## Instalacja (raz)

1. Python 3.10–3.12 i ffmpeg (Windows: `winget install Gyan.FFmpeg`, potem nowy terminal).
2. W tym folderze:
   ```
   python clipper.py setup
   ```
   Instaluje yt-dlp, faster-whisper (transkrypcja na PC), OpenCV (twarze), streamlink (Twitch na żywo),
   czcionki napisów i model mowy. Pierwszy raz pobiera ok. 1 GB.
3. Skill dla Claude Code (opcjonalnie): `python clipper.py install-skill`, potem restart Claude Code.

## Użycie

- **Aplikacja**: `python clipper.py app` albo dwuklik `start_clipper.bat` → http://localhost:8765
  Kreator na start: język filmów, streamerzy, które AI wybiera momenty.
- **Claude Code ze skillem**: „Zrób 10 Shortsów GTA 6 z najnowszych filmów, najpierw pokaż wybór”.
- **Wiersz poleceń**: `python clipper.py make --count 10` (wszystkie polecenia: `python clipper.py -h`).

Folder roboczy: `~/gta-shorts` (zmiana: `--workspace` albo zmienna `CLIPPER_WORKSPACE`).

## Jak to działa

| Krok | Co robi |
|---|---|
| Znajdź | Wyszukiwanie YouTube + Twoi streamerzy (YouTube, Twitch, Kick) + `channels.txt`. Pobiera **tylko dźwięk**, czat (gdy jest) i dane „najczęściej odtwarzane”. Transkrypcja z czasem każdego słowa. |
| Sygnały | Dla każdej sekundy: głos podskoczył (`LOUD`), czat przyspieszył (`CHAT`), widzowie przewijali tu (`REPLAYED`), słowa o pościgu/wypadku/bójce/akrobacji/reakcji (`MOMENT`) → `HEAT` 0–100. Z tego ~30 kandydatów. |
| Wybór | **Free**: bez AI. **Smart**: AI czyta tylko kandydatów. **Deep**: AI czyta całe transkrypcje. AI = Claude Code, Codex, Gemini, Kimi, OpenCode, Ollama albo własne polecenie. |
| Montaż | Pobiera tylko wybrane sekundy (+8 s zapasu do poprawek). Szuka twarzy: kamerka streamera → na górze, gra na dole (albo bańka); twarz na cały ekran → kadr idzie za twarzą; brak kamerki → cały kadr na rozmyciu. Wycina ciszę, do 3 zbliżeń na największych reakcjach, napisy (13 stylów), hook przez pierwsze 3,5 s, normalizacja głośności, okładka, `post.txt`. |
| Kontrola | PASS / WARN / FAIL: format, długość, dźwięk, czarny lub zamrożony obraz, brak napisów lub kamerki, ocena AI. |
| Przegląd | A = zatwierdź, X = odrzuć, strzałki. Zmiana słowami („zakończ 2 s wcześniej”), inny wygląd, Twój głos — zawsze jako nowa wersja obok oryginału. |
| Plan | Przeciągnij na dzień albo „Rozłóż automatycznie” (co 90 min od 10:00, bez nocy). |
| Codziennie | Autopilot przez Harmonogram zadań Windows / launchd / crontab. Najpierw podgląd. |
| Na żywo | Twitch: nagrywa stream (ostatnie 10 min), czyta publiczny czat bez logowania. Gdy liczba różnych piszących w 10 s skacze ×3 ponad normę, tnie od 25 s przed do 10 s po i robi z tego Shorta. |

## Ograniczenia (uczciwie)

- Na żywo tylko Twitch. Kick i YouTube Live: Shorty z nagrania po streamie.
- Czat z powtórek: YouTube tak. Twitch VOD — tylko jeśli yt-dlp go pobierze; inaczej wybór opiera się na
  głośności, słowach i AI.
- Wykrywanie kamerki to przybliżenie z położenia twarzy. Nietypowe nakładki mogą dać zły kadr → QC daje WARN,
  a w szczegółach Shorta zmienisz układ.
- Polecenia AI innych niż Claude Code (Codex, Gemini, Kimi, OpenCode) są szablonami — sprawdź je w Ustawieniach.
- Klipuj tylko streamerów, którzy na to pozwalają.

## Testy

```
python -m unittest discover -s tests -v
```
