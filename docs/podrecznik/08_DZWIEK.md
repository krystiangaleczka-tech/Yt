# Dźwięk: muzyka, efekty i głosy

Dźwięk filmu teatru papierowego bez lektora: ścieżka **Muzyka** (a2) i ścieżka **Efekty** (a3), każda jednym klipem
na cały film. Lektor to osobna ścieżka: klon głosu autora (rozdział „Lektor”). Wzór: „Bonnie and Clyde” (19.11.2026) — `output/bonnie-i-clyde/`
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

7. **Tempo z montażu** (reżyser 20.11: „powinno liczyć tempo cięć”): w obrębie tematu tempo idzie za długością ujęć —
   60 / długość bieżącego ujęcia, wygładzone gaussem (σ 5 s), względem mediany filmu, mnożnik ×0,85…×1,2 (wykładnik 0,5).
   Nuty nie zmieniają wysokości: temat układa się w „czasie muzycznym”, a mapa czasu (`Pasmo.mapa`) rozciąga go albo ściska
   na osi filmu. W obrębie ujęcia tempo stoi — liczenie cięć w okienku kołysało tempem od cięcia do cięcia.
8. **Zmiana tematu na cięciu**: stary temat kończy się na cięciu (0,12 s wyciszenia), nowy wchodzi na nim mocną częścią
   taktu z akcentem stopy (`CIECIE_WYJSCIE`, `CIECIE_WEJSCIE`) — bez półsekundowego przenikania, które rozmywało zmianę.
9. **Przystanek na gagu**: na puencie gagu (`GAG_PUENTA`, sekunda od początku ujęcia) muzyka cichnie o 9 dB na 0,6 s
   i wraca w 0,5 s, żeby dźwięk gagu wybrzmiał. Ściszanie, przystanki i cisza przed szczytem liczą się jako obwiednia
   w 100 Hz i dopiero potem rozciągają na próbki (pętla w 100 Hz trwa ułamek sekundy, na 44,1 kHz — minuty). Bez muzycznego podkreślania każdego ruchu — przy kilkudziesięciu gagach
   muzyka by się jąkała.
10. **Temat z treści sceny, nie z aktu.** Scena, która ma swój nastrój, dostaje swój temat, nawet jeśli trwa jedno ujęcie:
    ślub — marsz weselny na organach (chór weselny z „Lohengrina” Wagnera, domena publiczna), noc i sen — kołysanka
    z pozytywki, wieczór z poezją — walczyk salonowy; od następnej sceny wraca temat aktu. Reżyser 24.11 („Bonnie and Clyde”):
    „muzyka weddingowa”, „od ujęcia 20 do 23 musisz dodać jakieś efekty i muzykę zmienić” — cały akt I grał blues i ragtime,
    także pod ślubem i nocą w obozie. Nowy temat to nowy rodzaj dźwięku: próbka przed wgraniem (Akceptacja).

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
6. **Każda czynność, która w życiu brzmi, brzmi i tu** — także ta, której podsłuch nie widzi: klakson, pisk hamulców,
   buksowanie w błocie, gwizdek, zwierzę pod swoją tabliczką („MEOW!”), deszcz, świerszcze od zmroku. Reżyser 24.11 dopisywał
   je markerami („dźwięk trąbienia”, „dźwięk hamowania”, „zrób, że mają gwizdki i dźwięk gwizdka”, „miauu! (i dźwięk
   dodaj)”). Przy przeglądzie ujęcia wypisz czasowniki z opisu, kwestii i markerów i sprawdź, czy każdy ma wpis w `ZDARZENIA`
   w tej samej sekundzie; jeśli dźwięk nie ma przyczyny w kadrze (gwizdek), dorysuj ją.
7. **Błysk stoi w jednym miejscu.** Skan rozpoznaje błysk (strzał, flesz) po położeniu, więc położenie błysku zaokrągla się
   i trzyma przez cały błysk — błysk przy drżącej dłoni dał 159 dźwięków flesza w jednym ujęciu (23.11).
8. **Chwile z markerów w dźwięku** zapisuje się w sekundach osi Studio i przelicza `efekty.rr(s)` (Wytyczne 4.2, „Kreska”) —
   po nagraniu lektora ujęcia mają długość z prawdziwych kwestii, więc sekunda z tempa szacunkowego mija się z obrazem.

## Głosy ludzi

1. Tylko z modelu mowy albo nagrania, nigdy z szumu (Wytyczne 1.14).
2. **Bez głosu reżysera**, chyba że sam o to poprosi (19.11.2026: „zrób bez narracji mojej”). Referencje to syntetyczne
   głosy Kokoro-82M (`pilot/models`, role: Bonnie, Clyde, sąsiadka, szeryf, gazeciarz, tłum), a Chatterbox Turbo czyta
   z nich znaczniki niewerbalne (`[laugh]`, `[gasp]`, `[groan]`, `[sigh]`, `[shush]`, `[fear]`, `[angry]`, `[happy]`)
   i krótkie okrzyki.
3. `glosy.py referencje` (Kokoro) → `nagraj` (Turbo, po kilka ziaren) → `wybierz` (przycięcie ciszy; z faster-whisper
   sprawdza słowa okrzyków). Pliki w `dzwiek_probki/` (poza gitem). Na Macu jedno podejście Turbo trwa ok. 40 s (cpu),
   więc wystarczy **jedno ziarno na tekst i dwa teksty na rodzaj** (dwa warianty okrzyku) — 75 podejść to ok. 50 min.
   faster-whisper jest tylko w `.venv-align`, a soundfile tylko w `pilot/.venv-tts`: słowa liczy osobny krok
   `.venv-align/bin/python -I output/<film>/glosy.py slowa` (zapisuje `build/glosy_proby/slowa.json`), a `wybierz`
   bierze je z tego pliku („Syn słońca”). Okrzyk z westchnieniem ma dziurę ciszy w środku i automat go odrzuca —
   takie podejście przyjmuje się ręcznie po odsłuchu.
4. Głos postaci idzie pod tabliczkę (`TAB_GLOS`, wyjątki dla ujęcia w `TAB_GLOS_UJ`); przy porażce najpierw głos,
   potem puzon. W „Synu słońca” głosy i dźwięki gagów stoją w `efekty.GLOSY_UJ` pod kluczem **ujęcia źródłowego**
   (sekunda = zjazd tabliczki + ok. 0,3 s): skróty w zapowiedzi i haku (`render.WYCINEK`) biorą z niego to, co wypada
   w ich fragmencie, bez osobnych wpisów. Tłum to wiele krótkich zdań różnymi głosami, gęsto, stłumionych i z pogłosem (słychać ludzi, nie słowa);
   śmiech widowni i wiwaty — kilka głosów naraz.
5. Zabici w teatrze cieni nie jęczą — prawdziwe ofiary pokazujemy z szacunkiem.

## Akceptacja i wgranie

1. **Nowy rodzaj dźwięku → próbka przed filmem**: `probka_dzwieku.py` robi fragmenty filmu z obrazem i pełnym miksem
   oraz sam dźwięk (tematy po kolei, nowe efekty, głosy). Wysłać reżyserowi, wgrać dopiero po zgodzie.
2. Do czasu zgody na głosy: `BEZ_GLOSOW=1 python3 -I efekty.py` (reszta dźwięku już zatwierdzona).
3. `studio_film.py dzwiek` — muzyka na a2 (głośność 0,8), efekty na a3 (1,0); wpis w dzienniku z cytatem zgody
   (Studio → Gotowość filmu → „Zgoda reżysera na próbkę”: wpis „próbka dźwięku”, który aplikacja rozpoznaje).
4. Po każdej zmianie długości ujęć (nowy początek, skrócony akt) przelicz dźwięk i wgraj ponownie — inaczej rozjedzie
   się z obrazem. To samo po każdej turze poprawek rysunku, nawet gdy długości się nie zmieniły: nowe zdarzenia, tabliczki
   i błyski mają nowe dźwięki (24.11: same `efekty.py` + `studio_film.py dzwiek`).

## Kontrola

- Głośność na ujęcie (RMS): najgłośniej mają być zapowiedź i szczyty, nic nie przesterowane; przed lektorem muzyka
  ok. −24 dB, efekty ok. −26 dB.
- Brak próbki głosu to cisza z ostrzeżeniem, nie szum.
- Przegląd dźwięku liczy każdą klatkę co 0,08 s — klatka, która się wywraca, wychodzi tu wcześniej niż w Studio.
