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
