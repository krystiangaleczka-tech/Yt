# Dźwięk: muzyka, efekty i głosy

Dźwięk filmu teatru papierowego bez lektora: ścieżka **Muzyka** (a2) i ścieżka **Efekty** (a3), każda jednym klipem
na cały film. Lektora nagrywa reżyser (rozdział „Lektor”). Wzór: „Bonnie and Clyde” (19.11.2026) — `output/bonnie-i-clyde/`
`efekty.py`, `glosy.py`, `probka_dzwieku.py`; reżyser chciał, żeby dźwięk był „engaging”, i zatwierdził próbkę.

## Muzyka

1. **Tematy, nie jedno tło.** Każdy film ma kilka tematów w brzmieniu swojego kraju i epoki (lata 30. w Ameryce:
   ragtime na fortepianie stride z banjo, kontrabasem i miotełkami; blues z harmonijką; folk na banjo; temat łowcy —
   pizzicato w d-moll, tykanie zegara, trzy nuty fortepianu; napięcie — bicie serca i burdon; pieśń przy pracy; walc
   kataryniarski; bluegrass; 8-bit). Synteza w numpy (`_piano`, `_banjo`, `_bas`, `_dech`…), nuty w pamięci podręcznej.
2. **Temat zmienia się z akcją**: lista `CUES` — od którego ujęcia gra który temat (z opcjami: tempo, tonacja,
   fanfara, rosnące tempo w napięciu). Przejścia łagodne (0,5 s).
3. **Postać ma motyw**, który wraca: temat łowcy słychać pierwszy raz przy teczce w akcie III, zanim widz wie, czyja
   to teczka.
4. **Cisza przed szczytem** (`CISZA`: od, do, czy muzyka wraca głośniej): most w Wellington, Grapevine, zasadzka —
   zostają same efekty. Dwa–trzy szczyty na film.
5. **Pod kwestią lektora** muzyka ciszej o 8 dB, efekty o 5 dB (okna kwestii z `dane.okno_kwestii`) — **łagodnie**
   (`efekty.sciszanie`): w dół w 0,3 s, zaczyna 0,25 s przed kwestią, w górę w 0,9 s, a przerwy między zdaniami krótsze niż
   3 s zostają ściszone. Twardy przeskok na brzegach kwestii (190 razy w filmie, połowa przerw krótsza niż 3 s) słychać jako
   muzykę, która „raz gra ciszej, raz głośniej” — zwłaszcza zanim jest lektor, bo wtedy ściszenie nie ma powodu (reżyser
   19.11, „Bonnie and Clyde”).
6. **Tematy wyrównane**: każdy temat ma tę samą głośność (`MUZYKA_DB`, RMS bez brzegów), a różnica stylu jest zamierzona
   i mała (`STYLE`: mrok −1,5 dB, napięcie +0,5 dB, opcja „cicho” −2,5 dB). Bez tego ragtime grał o 6–7 dB głośniej od folku
   i mroku. Miara po zmianie: rozrzut tematów (10.–90. centyl) 9,1 → 4,3 dB; zostają tylko celowe zmiany — cisza przed
   szczytem i powrót muzyki w dłuższej pauzie lektora.

## Efekty

1. **Z rysunku, nie z pamięci.** `efekty.skan()` przegląda cały film (`render.uloz` co 0,08 s) z podsłuchem funkcji
   ujęć: auta → silnik z prędkości na ekranie (wolno cicho i nisko, szybko głośno i wyżej), radiowóz z napisem SHERIFF
   z syreną, pisk opon przy gwałtownym hamowaniu; lalki w ruchu → drewniane kroki lalek po deskach; błysk → strzał
   (za parawanem stłumiony) albo flesz (biały błysk); tabliczki i podpisy, zawieszki („DAY 1” → pieczątka), rzeczy na
   nitkach. Zmiana rysunku zmienia dźwięk sama.
2. **Tabliczka brzmi jak jej napis** (`TAB_DZWIEK`): porażka „AGAIN?!”, „THAT'S IT?” → puzon wah-wah; „BEEP” →
   klakson; „SCREECH!” → pisk; „AW!”, „OUCH!” → sprężyna; „NEVER AGAIN”, „HOME” → akcent fortepianu i kotła.
3. **Wydarzenia ręczne** (`ZDARZENIA`): to, czego podsłuch nie widzi (muł, indyki, kasa, maszyna drukarska, dzwony,
   oklaski), w sekundzie z rysunku. Długie dźwięki mają czas trwania zamiast głośności.
4. **Tło miejsca** według dekoracji ujęcia (preria — wiatr i ptaki; las — ptaki, o świcie chór; noc — świerszcze;
   ulica, pokój, pole w upale z cykadami, drukarnia, kino z projektorem), zmiana dekoracji — papier i drewno, kurtyny
   z dźwiękiem z „Pierwszego cesarza”.
5. **Zapowiedź** ma uderzenie na każdym cięciu (jak zwiastun).

## Głosy ludzi

1. Tylko z modelu mowy albo nagrania, nigdy z szumu (Wytyczne 1.14).
2. **Bez głosu reżysera**, chyba że sam o to poprosi (19.11.2026: „zrób bez narracji mojej”). Referencje to syntetyczne
   głosy Kokoro-82M (`pilot/models`, role: Bonnie, Clyde, sąsiadka, szeryf, gazeciarz, tłum), a Chatterbox Turbo czyta
   z nich znaczniki niewerbalne (`[laugh]`, `[gasp]`, `[groan]`, `[sigh]`, `[shush]`, `[fear]`, `[angry]`, `[happy]`)
   i krótkie okrzyki.
3. `glosy.py referencje` (Kokoro) → `nagraj` (Turbo, po kilka ziaren) → `wybierz` (przycięcie ciszy; z faster-whisper
   sprawdza słowa okrzyków). Pliki w `dzwiek_probki/` (poza gitem).
4. Głos postaci idzie pod tabliczkę (`TAB_GLOS`, wyjątki dla ujęcia w `TAB_GLOS_UJ`); przy porażce najpierw głos,
   potem puzon. Tłum to wiele krótkich zdań różnymi głosami, gęsto, stłumionych i z pogłosem (słychać ludzi, nie słowa);
   śmiech widowni i wiwaty — kilka głosów naraz.
5. Zabici w teatrze cieni nie jęczą — prawdziwe ofiary pokazujemy z szacunkiem.

## Akceptacja i wgranie

1. **Nowy rodzaj dźwięku → próbka przed filmem**: `probka_dzwieku.py` robi fragmenty filmu z obrazem i pełnym miksem
   oraz sam dźwięk (tematy po kolei, nowe efekty, głosy). Wysłać reżyserowi, wgrać dopiero po zgodzie.
2. Do czasu zgody na głosy: `BEZ_GLOSOW=1 python3 -I efekty.py` (reszta dźwięku już zatwierdzona).
3. `studio_film.py dzwiek` — muzyka na a2 (głośność 0,8), efekty na a3 (1,0); wpis w dzienniku z cytatem zgody.
4. Po każdej zmianie długości ujęć (nowy początek, skrócony akt) przelicz dźwięk i wgraj ponownie — inaczej rozjedzie
   się z obrazem.

## Kontrola

- Głośność na ujęcie (RMS): najgłośniej mają być zapowiedź i szczyty, nic nie przesterowane; przed lektorem muzyka
  ok. −24 dB, efekty ok. −26 dB.
- Brak próbki głosu to cisza z ostrzeżeniem, nie szum.
- Przegląd dźwięku liczy każdą klatkę co 0,08 s — klatka, która się wywraca, wychodzi tu wcześniej niż w Studio.
