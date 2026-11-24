# Bonnie and Clyde — materiały do publikacji na YouTube (wersja EN)

Stan na 24.11.2026. Film: **18:19** (1099,0 s), 119 ujęć, 101 kwestii lektora (klon głosu autora). Ustawienia kanału
i domyślne ustawienia przesyłania są wspólne z „Pierwszym cesarzem”: `output/pierwszy-cesarz/publikacja/PUBLIKACJA.md`
(gałąź film/pierwszy-cesarz).

## Pliki

| Co | Plik |
|---|---|
| Film | `output/bonnie-i-clyde/build/Bonnie_and_Clyde_1440p_YouTube.mp4` (2560 × 1440, 24 kl./s; poza repo) |
| Miniaturka | `output/bonnie-i-clyde/miniatura/miniatura_C_en_4k_fuji.png` (3840 × 2160, ok. 15 MB). Zapas z telefonu: `miniatura_C_en_fuji.jpg` |
| Miniaturka D (24.11 wieczorem) | `output/bonnie-i-clyde/miniatura/miniatura_D_en_4k_fuji.png` — łowcy w krzakach, podziurawiony Ford zapadnięty tyłem w rowie, na dachu Bonnie (biała suknia ślubna, czerwony beret) strzela w lewo, Clyde w prawo, w tle Teksas i pociski, „THE REAL ENDING”. Pasuje do tytułu 2 (GTA 6) |
| Opis z rozdziałami | `opis_en.txt` — wklej w całości (stała część „How this video was made” już w nim jest) |
| Napisy | `output/bonnie-i-clyde/napisy_yt/Bonnie_and_Clyde_en.srt` (angielskie) i `_pl.srt` (polskie) |

Jak powstał film: `FILM=1 ROZDZIELCZOSC=1440 PROCESY=3 python3 render.py klipy build/klipy_1440p` (CRF 21, ok. 16 Mbit/s;
przy CRF 18 ziarno papieru dawało 40 Mbit/s), potem `python3 zloz.py build/klipy_1440p build/Bonnie_and_Clyde_1440p_YouTube.mp4`
(lektor w oknach kwestii, Muzyka 0,8, Efekty 1,0 — jak montaż w Studio). Napisy: `python3 napisy_yt.py`. Miniaturka:
`ROZMIAR=3840 WARIANT=C python3 miniatura.py` i `MOC=0.5 JASNOSC=0.07 python3 ../pierwszy-cesarz/fujifilm.py
miniatura/miniatura_C_en_4k.png 1280`.

## Tytuł i test A/B tytułów

Reżyser 24.11.2026: „trzy tytuły według obowiązujących trendów na YouTube, co się klika na dzień 24.11.2026; na pewno jeden
tytuł musi być coś z GTA 6”, a do tego „tylko jedna miniatura, ta z C”. Jedna miniaturka, więc test idzie na samych
tytułach (Studio → Tytuł → Testy A/B). Wpisuj od pary 1: pierwsza wersja zostaje, gdy test nie wyłoni zwycięzcy.

| | Tytuł | Co sprawdza |
|---|---|---|
| 1 | `The ENTIRE Bonnie and Clyde Story in 18 Minutes` | format „The ENTIRE … in N Minutes” (wybrany przy „Synu słońca”); pasuje do miniaturki („THE WHOLE STORY”, „18 MIN”); na YouTube nie ma filmu o tym brzmieniu |
| 2 | `Before GTA 6: The REAL Bonnie and Clyde Ending, Told in Paper Theatre` | ruch z GTA 6 (premiera 19–20.11.2026, rekordowe 3,79 mld USD pierwszego dnia według Take-Two; Rockstar sam nazwał grę historią „w typie Bonnie i Clyde'a”) — wyszukiwanie „gta 6 bonnie and clyde” to dziś filmy „Bonnie and Clyde Ending” z gry: 366 tys. i 51 tys. w 1–4 dni, „wszystkie zakończenia GTA 6” 816 tys. i 1,5 mln |
| 3 | `One Joke Photo Made Bonnie & Clyde America's Most Hunted Couple` | hak filmu (zdjęcie dla żartu z cygarem) i „mit kontra prawda”, który teraz rośnie: „Bonnie and Clyde Were WAY Worse Than the Movie Showed” (History in Moments) 717 tys. w 2 tygodnie; wątek zdjęcia ma na YouTube tylko maleńkie filmy (4 i 259 wyświetleń) |

Sprawdzone w wyszukiwarce YouTube 24.11.2026 wieczorem (sortowanie po dacie przesłania). 18.11 tytuły z GTA nie miały
wyświetleń, bo gra jeszcze nie wyszła — po premierze to się odwróciło. W miniaturce nie ma grafik z GTA 6 (znak towarowy).

## Rozdziały

Są w opisie: początki aktów na tej samej siatce co render końcowy, zaokrąglone w dół do sekundy — 0:00, 1:19, 3:34, 5:34,
7:39, 10:29, 12:48, 14:35, 16:31. W Studio wyłącz rozdziały automatyczne.

## Hasztagi i tagi

Hasztagi na końcu opisu: `#BonnieAndClyde #TrueCrime #GTA6` (pierwsze trzy YouTube pokazuje nad tytułem; gra jest w filmie,
w akcie VIII).

Tagi tego filmu (tagi ogólne kanału dochodzą same z domyślnych ustawień przesyłania):

```
Bonnie and Clyde, Bonnie Parker, Clyde Barrow, Frank Hamer, Bonnie and Clyde true story, Bonnie and Clyde ambush, Bonnie and Clyde ending, GTA 6 Bonnie and Clyde, Barrow Gang, Great Depression, 1930s outlaws, public enemy, true crime, American history, Texas Rangers, Gibsland Louisiana, Joplin photos, Blanche Barrow, The Highwaymen, paper theatre
```

## Przypięty komentarz

Dopisz go zaraz po publikacji i przypnij. Ma fakt, którego nie ma w filmie, i pytanie do widzów:

```
The real death car still exists: the bullet-riddled 1934 Ford is on display at a casino in Primm, Nevada, on the road between Los Angeles and Las Vegas.

So who made the legend: the outlaws, the newspapers, or the man who finally caught them?
```

## Ustawienia w Studio

1. **Szczegóły:** tytuł (para 1), opis z `opis_en.txt`, miniaturka C, playlista z historią Ameryki (nowa — dotychczasowa
   „Ancient Asia” nie pasuje).
2. **Odbiorcy:** „Nie, to nie jest film dla dzieci” (strzelaniny, śmierć policjantów i bohaterów, pokazane w teatrze cieni
   i śladami). Bez ograniczenia wiekowego.
3. **Pokaż więcej:** płatna promocja: nie; treści zmienione lub syntetyczne: nie (klon własnego głosu YouTube wymienia wśród
   rzeczy, których nie trzeba oznaczać; i tak piszemy o nim w opisie); tagi z sekcji wyżej; język filmu angielski;
   certyfikat napisów „nigdy nie były emitowane w telewizji w USA”; kategoria **Edukacja**; licencja standardowa;
   komentarze włączone, moderacja podstawowa.
4. **Elementy filmu:**
   - **Napisy:** `Bonnie_and_Clyde_en.srt` jako angielskie, `Bonnie_and_Clyde_pl.srt` jako polskie. W filmie nie ma
     wypalonych napisów (reżyser 24.11), więc te pliki są jedynymi napisami.
   - **Ekran końcowy:** ostatnie ujęcie to podziękowanie i ukłony (18:09–18:19). Ustaw ekran końcowy od 18:09: przycisk
     subskrypcji i film „Son of the Sun” albo o pierwszym cesarzu Chin. Elementy nie mogą zasłaniać lalek w ukłonie.
5. **Widoczność:** najpierw Niepubliczny — obejrzyj na YouTube, czy jest 1440p (YouTube liczy wyższe jakości po kilkunastu
   minutach od wgrania), czy działają rozdziały i napisy. Potem Zaplanuj (np. czwartek albo piątek o 20:00 czasu polskiego,
   14:00 w Nowym Jorku) — póki GTA 6 jest świeże, lepiej szybciej niż później.
