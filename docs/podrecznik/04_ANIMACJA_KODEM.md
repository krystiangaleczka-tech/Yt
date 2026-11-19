# Animacja rysowana kodem

Filmy w trybie „Animacja 2D” mogą mieć ujęcia rysowane programem (bez generatora obrazów). Wtedy każdy kadr powstaje
z tych samych klocków, a wygląd filmu jest powtarzalny. Konkretne pliki danego filmu są w jego warsztacie.

Są dwie techniki. Każda ma film-wzorzec, który reżyser zatwierdził; nowy film tej techniki zaczyna się od kopii jego
silnika i sposobu pracy (Wytyczne ujęć, wstęp i sekcja 0).

## Kreskówka 2D (wzorzec: „Oddział C”, 0:00–0:53)

| Klocek | Co robi |
|---|---|
| **Pióro** (`Pen` w `render.py` filmu) | rysuje linie, wielokąty, elipsy i tekst z drżeniem kreski, które „gotuje się” 8 razy na sekundę; rysuje w podwójnej rozdzielczości (SS=2) i zmniejsza |
| **Kamera** (`framed`, `handheld`) | kadr robi kamera (zoom wokół punktu), nie powiększanie postaci; lekkie pływanie z ręki, wstrząsy; nigdy nie pokazuje końca świata |
| **Wygląd** (`LOOK`) | barwa, maska światła, winieta, ziarno (zmiana co 3 klatki) |
| **Zestaw postaci** (`kit_*.py`) | postacie od przodu i od tyłu, siedzące, zbliżenia twarzy; mruganie i oddech wbudowane; kostiumy z księgi świata |
| **Zestaw miejsc** | tła lokacji zgodne z planem budynku z księgi świata |
| **Baza jednostki** (`dzien_base.py`) | z rozpiski robi listę ujęć z długościami i oknami kwestii; składa klatkę: kamera, wygląd, napis w czasie kwestii |
| **Plik jednostki** (`render_dNN.py`) | jedna funkcja na ujęcie: `s_nazwa(p, t, T)` rysuje stan w chwili `t` z długości `T` |
| **Wgrywanie** (`studio_dzien.py`) | renderuje każde ujęcie do klipu, wgrywa do Ujęć i na oś montażu |

## Teatr papierowy (wzorzec: „Pierwszy cesarz” EN, 16.11.2026)

Pliki w `output/pierwszy-cesarz/`, rozpiska i księga w `docs/filmy/pierwszy-cesarz/ujecia/`; szczegóły w warsztacie filmu.

| Klocek | Co robi |
|---|---|
| **Silnik** (`papier.py`) | plany głębi `p` (odwrotność odległości od kamery); kamera `Cam` jedzie wózkiem i ma obiektyw, więc bliskie plany rosną i przesuwają się szybciej (paralaksa); w pionie kamera się pochyla, nie jedzie (`trucky=0`); miękki cień każdego wycinka na planach za nim; głębia ostrości, światło, winieta, ziarno |
| **Wycinki** (`zestaw.py`) | wycinki PNG i wycinanki rysowane kodem na papierze filmu; `lalka` (lalka na patyczku), `prop` (rekwizyt i znak: X, gwiazdka, biała flaga), `tag` (zawieszka z napisem), `hang` (rzecz na nitce: zjazd z przestrzeleniem i gasnącym kołysaniem); plany `P` (`P.lalki`, `P.rekwizyty`…) |
| **Świat** (`swiat.py`) | stan sceny z kamieni milowych rozpiski (`stan(i)`, `po("mur")`); scenografie (`swiat`, `sala`, `morze`); `lalka(…, k, sink, flip, lean)` — wysuwanie zza rampy, opadanie pod nią, obrót, przechył; `podpis` — tabliczka z imieniem; rzeczy wspólne dla wielu ujęć (`powoz`, `waga`, `smoki_przy_palacu`), żeby poprawka szła do wszystkich naraz |
| **Ujęcia** (`ujecia1.py`, `ujecia2.py`) | `s_<klucz>(st, w, t, T)` zmienia stan w czasie (wydarzenia od `t = 0` ujęcia), ustawia kamerę (`kam`), woła scenografię; docstring opisuje ujęcie i cytuje uwagi reżysera z datą |
| **Dźwięk** (`efekty.py`) | `ZDARZENIA` — dźwięk każdego zdarzenia ujęcia w tej samej sekundzie co w rysunku; `W_STUDIO` — ujęcia już w Studio losują nowe dźwięki osobno (Wytyczne 1.12) |
| **Podgląd na żywo** (`na_zywo.py`) | Studio rysuje ujęcia z kodu i odświeża je po zapisie (rozdział „Jak pracujemy”) |
| **Render** (`render.py`) | arkusz klatek, kontrola „końca świata”, klipy ujęć; render końcowy uruchamia tylko reżyser |

**Gramatyka teatru** — te same ruchy w każdym filmie, żeby widz czytał je bez myślenia:

- **Wejścia**: lalka wysuwa się zza rampy (z odbiciem i osiadaniem); rzecz zjeżdża z góry na nitce (z przestrzeleniem
  i kołysaniem); dekoracja wyrasta zza wzgórz albo z ziemi i się kołysze; wojsko wyłania się rzędami zza grani; fale
  wysuwają się od dołu; broń i rekwizyt pojawiają się ze środka innej rzeczy albo zza postaci.
- **Wyjścia**: lalka opada pod rampę; rzecz odjeżdża w górę na nitce albo wylatuje; dekoracja zapada się pod ziemię,
  zwija się albo płonie; statek chowa się za ostatnią falą; postać wyskakuje za kadr i wpada do następnego ujęcia z tej
  samej strony.
- **Zmiany**: między aktami kurtyna z tytułem, przy zmianie miejsca ściemnienie (rozdział „Rytm” 7); nowa dekoracja
  buduje się na oczach widza na początku sceny, a stara schodzi w kadrze.
- **Kamera** w każdym ujęciu jedzie (bokiem z paralaksą, dojazd do zdarzenia, odjazd na potęgę); przedplan (kulisy)
  i tło żyją.
- **Lalka** obraca się w stronę ruchu (bokiem widać grubość tektury), pochyla się, podskakuje w jeździe; ręce mają
  zawiasy w barku i łokciu; znaki i gagi bierze ze słownika (Wytyczne 1.20).
- **Potęga** to liczba: rzędy, dziesiątki postaci, kamera odjeżdża (Wytyczne 1.17).

**Nowy film teatru papierowego**: skopiuj `papier.py`, `render.py`, `na_zywo.py` i szkielet `efekty.py`; wytnij nową
scenerię kraju i epoki oraz nową obsadę (`zestaw.py`); rozpisz `dane.py` i `ksiega.py`; opisz pliki w warsztacie filmu.


### Lekcje z „Bonnie and Clyde” (19.11.2026, Ameryka lat 30.)

Pliki w `output/bonnie-i-clyde/`: `zestaw_bc.py` (lalki lat 30. na tej samej geometrii arkusza co japońskie, Ford V8,
radiowóz, motocykl, ciężarówka, fasady, wnętrza, rekwizyty, teatr oklejony gazetami), `scena.py` (scenografie
i pomocnicze), `ujecia_a.py` / `ujecia_b.py`. Zasady, które dopisał silnik:

| Zasada | Jak |
|---|---|
| Aktorzy i auta wchodzą dopiero, gdy dekoracja się zbuduje | `scena.BUDOWA` ustawia render przed ujęciem, `wejscie()` opóźnia lalki i auta; bez tego stały na pustym płótnie |
| Pasażer auta nie ma nóg pod karoserią | `lalka(…, siedzi=True)` — korpus ucięty tuż pod biodrami; miejsce w oknie z `J.FORD_GLOWY` albo własne `(x, y)`, czwarty element `-1` = twarzą do tyłu |
| Sylwetka teatru cieni jest całkiem czarna | `cien(…)` z `alpha=1`; przy przezroczystości ręce rysowały na tułowiu „X” |
| Auto dachuje wokół własnego środka | `auto_srodek(st, t, cx, cy, h, rot)` — `auto()` obraca się wokół linii kół i przy 180° znikało pod sceną |
| Pod ścianą wnętrza stały pas podłogi | `scena.spod()` — podczas budowy podłoga wjeżdża od dołu i przez chwilę prześwitywało płótno (kontrola końca świata) |
| Wysokość z odbicia może być zerowa | `h=max(1.0, …*back(k))` — `back` daje 0 w jednej klatce i klatka się wywraca (wyłapał to przegląd dźwięku) |
| Rzecz na ziemi i leżąca postać są nad rampą | rekwizyt ok. `y ≤ 690` albo plan przed rampą; leżąca lalka `lift` ok. 70; rzeka w przeprawie z górą ok. 590 |
| Kamera nisko przy akcji przy ziemi | zbliżenia na ziemię `y` 480–520; inaczej akcja chowa się pod napisami |
| Nic nie zasłania twarzy w oknie i nikt przypadkiem nie celuje w partnera | gazeta obok głowy, nie na niej; karabin czyszczony leży na kolanach |
| Skrót w zapowiedzi bez zdradzających podpisów | `render.WYCINEK` od chwili akcji, ale po zjechaniu podpisu („Frank Hamer” jest tajemnicą do aktu V) |
| Przejście bez kurtyny | `render.BEZ_KURTYNY = {1}` — prolog przechodzi w akt I ściemnieniem (Rytm, „jeden początek”) |

**Przegląd po akcie.** Arkusz po 6 ujęć z miniaturami 400 px (`R.arkusz(zakres, plik, cols=3, tw=400)`), potem pełne
klatki tylko tam, gdzie coś nie gra; poprawki od razu dla całej klasy błędu (w silniku), nie w jednym ujęciu.

## Zasady rysowania

- Czasy wydarzeń liczy się od początku ujęcia (`t`), nie bezwzględnie.
- Bliżej kamery = rysowane później; otwór przycina to, co za nim (Wytyczne ujęć).
- Ruch po schodach i pochylniach pokazuje się w osi ruchu (postać od przodu albo od tyłu); stopy stoją na stopniach
  policzonych z geometrii miejsca, krok to przeniesienie jednej stopy (Wytyczne ujęć 1.10).
- Stan świata bierze się z księgi (lampa, kreski na ścianie, kto ma rekwizyt), nie z pamięci.
- Każdy film ma scenerię swojego kraju i epoki. Silnik, papiery i sposób pracy są wspólne, ale krajobrazu poprzedniego
  filmu (góry, drzewa, kulisy) nie przenosi się do nowego — reżyser zobaczył Japonię na chińskich górach z „Pierwszego
  cesarza” (13.11). Dla Japonii: Fuji, okrągłe pagórki z polanami, wiśnie, bambus.
- Każde ujęcie powstaje według przepisu z Wytycznych ujęć (sekcja 0): wiersz rozpiski → stan świata → obsada → oś czasu
  zdarzeń pod kwestią → długość → kamera → życie i znaki → dźwięk → kontrola.
- Po narysowaniu: arkusz klatek ze środka każdego ujęcia i z każdego wydarzenia; obejrzeć, potem wgrać.
- W Studio: przegląd każdego ujęcia w zakładce Ujęcia (bez renderowania całego filmu do mp4).
