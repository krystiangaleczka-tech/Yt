# Animacja rysowana kodem

Filmy w trybie „Animacja 2D” mogą mieć ujęcia rysowane programem (bez generatora obrazów). Wtedy każdy kadr powstaje
z tych samych klocków, a wygląd filmu jest powtarzalny. Konkretne pliki danego filmu są w jego warsztacie.

## Klocki

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

## Zasady rysowania

- Czasy wydarzeń liczy się od początku ujęcia (`t`), nie bezwzględnie.
- Bliżej kamery = rysowane później; otwór przycina to, co za nim (Wytyczne kadru).
- Ruch po schodach i pochylniach pokazuje się w osi ruchu (postać od przodu albo od tyłu); stopy stoją na stopniach
  policzonych z geometrii miejsca, krok to przeniesienie jednej stopy (Wytyczne kadru 1.10).
- Stan świata bierze się z księgi (lampa, kreski na ścianie, kto ma rekwizyt), nie z pamięci.
- Po narysowaniu: arkusz klatek ze środka każdego ujęcia i z każdego wydarzenia; obejrzeć, potem wgrać.
- W Studio: przegląd każdego ujęcia w zakładce Ujęcia (bez renderowania całego filmu do mp4).
