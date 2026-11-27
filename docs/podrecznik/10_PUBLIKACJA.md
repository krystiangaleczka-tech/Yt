# Publikacja: miniaturka, tytuł, napisy i Shortsy

Co się dzieje z filmem po renderze końcowym. Render i decyzję o publikacji ma reżyser; wykonawca przygotowuje plik,
napisy, opis, miniaturki, tytuły do testu i Shortsy, a wszystko zapisuje w `output/<film>/publikacja/PUBLIKACJA.md`.
Wzory: „Pierwszy cesarz” (`output/pierwszy-cesarz/publikacja/PUBLIKACJA.md`: ustawienia kanału i przesyłania wspólne
dla wszystkich filmów) i „Bonnie and Clyde” (24–26.11.2026, gałąź `bonnie-i-clyde`).

## Kolejność

1. **Plik na YouTube**: klipy renderu końcowego z `FILM=1` (1440p, CRF 21 — przy CRF 18 ziarno papieru dawało 40 Mbit/s),
   potem `zloz.py` (lektor, muzyka 0,8, efekty 1,0 jak w Studio; −16 LUFS). Dane pliku do `PUBLIKACJA.md`.
2. **Napisy** EN i PL jako pliki `.srt` (`napisy_yt.py`). W obrazie nie ma wypalonych napisów (Wytyczne 1.13), więc te pliki
   są jedynymi napisami — wgrywa się oba.
3. **Opis z rozdziałami**: rozdziały to początki aktów na siatce renderu końcowego, zaokrąglone w dół do sekundy, pierwszy
   0:00; w Studio YouTube wyłącz rozdziały automatyczne. Stała część „How this video was made” (wszystko rysowane kodem,
   lektor to klon głosu autora). Trzy hasztagi na końcu (YouTube pokazuje je nad tytułem).
4. **Miniaturki i tytuły** do testu A/B (Wytyczne 5 i niżej).
5. **Przypięty komentarz**: fakt, którego nie ma w filmie, i pytanie do widzów.
6. **Ustawienia**: nie dla dzieci, bez ograniczenia wiekowego (śmierć pokazana w teatrze cieni i śladami), kategoria
   Edukacja, ekran końcowy na ostatnim ujęciu (podziękowanie) tak, żeby nie zasłaniał lalek. Najpierw Niepubliczny:
   sprawdź 1440p (YouTube liczy wyższe jakości po kilkunastu minutach), rozdziały i napisy; potem Zaplanuj.
7. **Shortsy** z renderu końcowego, jeden dziennie od publikacji (niżej).
8. **Wyniki** po 7 i 28 dniach (niżej).

## Tytuł

- Przed propozycją tytułu szukaj na YouTube dokładnego brzmienia (sortowanie po dacie, ostatni miesiąc) — reżyser pyta
  „jesteś pewny?”, a wyszukiwarka nieraz odwracała pierwszy wybór.
- **Most z gorącego tematu działa tylko po stronie, której szukają ludzie.** Po premierze GTA 6 (19–20.11.2026) gracze
  szukali zakończenia gry, więc tytuł zaczyna się od „GTA 6's Ending…”, a nie od „the real story behind” (takie tytuły miały
  3–6 wyświetleń). „Before GTA 6” odpada, kiedy gra już wyszła — brzmi, jakby film powstał przed premierą. Gra może być w tytule
  i hasztagu, ale nie w grafice miniaturki (znak towarowy).
- Jedna zmiana na test: rozpoznawalna część tytułu zostaje (wzór ciekawości, „Told in Paper Theatre”), zmienia się jedno.

## Test A/B (Test & Compare)

- Najwyżej 3 warianty. Nowa miniaturka zastępuje wariant, nie dochodzi — test trzeba zatrzymać i założyć nowy.
- Para tytuł + miniaturka: każdy tytuł z miniaturką, która pokazuje to, co obiecuje („GTA 6's Ending vs What Really Happened
  to Bonnie and Clyde” + plakat z zasadzki; „One Joke Photo Made Bonnie & Clyde America's Most Hunted Couple” + ciemnia ze
  zdjęciem z cygarem).
- Wpisuj od pary 1 — pierwsza zostaje, gdy test nie wyłoni zwycięzcy. Przy ok. 120 wyświetleniach miniatury na wariant
  zwycięzcy nie będzie; nie oceniaj wariantów po jednym dniu.

## Shortsy

Shortsy tnie się z renderu końcowego skryptem `shorts.py` filmu (wzory: `output/pierwszy-cesarz/shorts.py`,
`output/powstanie-japonii/shorts.py`, `output/bonnie-i-clyde/shorts.py`), a nie składa w Studio: silnik teatru rysuje kadr
16:9, a render ma zatwierdzony obraz i miks. Kolejne Shortsy to wpisy w `SHORTS` (od/do ujęcia, środek wycinka, zaczepka).

- **Najwyżej 60 s.** Shorts z całego filmu też (reżyser 24.11: „skróć do minuty, przecież to na YT”).
- **Pętla bez szwu**: zaczyna się od zasuniętej kurtyny, która się rozsuwa, i kończy jej zasunięciem (reżyser 20.11: „niech
  film się zaczyna, że jest kurtyna i rozjeżdża, żeby był taki infinite”).
- **Ciąg akcji, przyczyna przed skutkiem, bez scen rozmowy** (reżyser 23.11 o wężu w „Synu słońca”: najpierw Susanoo niszczy
  pola ryżowe, potem zejście na linkach i od razu kadzie z sake — rozmowę ze starcami wyciąć). Shorts z całego filmu ma „ręce
  i nogi” (24.11): każde zdanie wynika z poprzedniego, zaimki mają poprzednika.
- **Tylko pełne zdania lektora**, cięcie tylko w pauzie nagrania ≥ 0,3 s. Lektor nie wchodzi przed ok. 0,9 s Shortsa — szelest
  rozsuwanej kurtyny (0,1–0,95 s) zagłusza pierwsze słowo (Whisper usłyszał „The missing five states” zamiast „Police in
  five states”).
- **Nie kończ na kurtynie aktu z filmu**: tabliczka następnego aktu zjeżdża, zanim kurtyna się domknie — koniec najpóźniej
  1,5 s przed nią i własna kurtyna Shortsa.
- **Kadr**: pionowy wycinek z kadru 16:9; „Bonnie and Clyde” nie ma wypalonych napisów, więc wycinek ma pełną wysokość
  (1883 × 1440) — lalki stoją na samym dole sceny. U góry zaczepka (2 wiersze, „THE REAL ENDING / OF BONNIE & CLYDE”), pod
  pasem obrazu własne duże napisy cięte na oddechach lektora (`podzial`, gdy automat tnie źle). Kadr sprawdza arkusz klatek
  co 0,5 s (`--proba`), bo szeroka scena gubi postacie przy brzegach.
- **Kontrola**: każdy Shorts przez Whispera (`.venv-align`, model small, `HF_HUB_OFFLINE=1`); głośność jak w filmie. Plik
  ponad 30 MB nie dojdzie na telefon — obok lżejsza kopia `*_lekki.mp4` (ok. 3,2 Mb/s).
- **Publikacja**: w Studio YouTube → Shorts → Powiązany film = długi film; tytuł i opis w `PUBLIKACJA.md` (pierwsze zdanie
  opisu to fakt z Shortsa, dalej „The whole story in N minutes, told in paper theatre: see the related video.”); jeden dziennie,
  najpierw ten, który łapie gorący temat.

## Wyniki

- Czytaj po źródłach ruchu (reklama a ruch organiczny) i po unikalnych widzach: „Bonnie and Clyde” miał po 36 h
  24 wyświetlenia, ale ok. 5 osób.
- Oceniaj po 7 i 28 dniach; wnioski o długości i otwarciu — Podręcznik → Rytm („Początek filmu”, „Wyniki „Bonnie and Clyde””).
- Reklama dopiero wtedy, gdy ruch organiczny trzyma po 30 s co najmniej ok. 60 % (Rytm).
