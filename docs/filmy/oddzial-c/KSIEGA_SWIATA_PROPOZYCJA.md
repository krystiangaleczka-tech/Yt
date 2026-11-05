# Propozycja: księga świata i kontrola ciągłości (Oddział C, potem każdy film)

## Problem

Dziś łańcuch wygląda tak: scenariusz (proza) → rozpiska ujęć → rysunek. Nigdzie nie ma zapisanego **stanu świata**, więc:

- scenariusz nie wie, że telefon z podniesioną słuchawką nie zadzwoni (audyt #1), a budynek ma trzy kondygnacje (#4);
- rozpiska powstaje dzień po dniu i gubi wskazówki i zasiane rzeczy (#10, #16–#23) albo zdradza tajemnicę przed czasem (#9);
- rysunek wpisuje stan ręcznie: lampa świeci bez prądu (#6), kresek jest 7 zamiast 6 (#20), imiona się dublują (#8);
- liczby (woda, dni) wpisuję w kwestie z głowy i się nie bilansują (#14).

W [AUDYT_CIAGLOSCI_D01-10.md](AUDYT_CIAGLOSCI_D01-10.md) są 24 takie błędy w dziesięciu dniach.

## Rozwiązanie w czterech częściach

### 1. Księga świata — jedno źródło prawdy

To jeden plik danych dla filmu (`ujecia/swiat.py`), czytany przez wszystkie narzędzia:

| Dział | Co zawiera | Przykład |
|---|---|---|
| **Plan budynku** | kondygnacje, pomieszczenia, połączenia, okna i widoki | piwnica: schody → korytarz → apteka (bok) → pralnia → rozdzielnia (koniec) |
| **Postacie** | wygląd i kostium, cechy stałe, stan od dnia X, imię (unikalne) | Henryk: nie mruga, chyba że celowo; Nowak: gorączka od d6, rękawy zawsze opuszczone |
| **Rekwizyty** | kto ma, gdzie leży, od kiedy, gdzie zasiany | krótkofalówki: dyżurka C → Zosia i narrator od d2 |
| **Zasoby** | stan początkowy, zmiany przypisane do beatów, zużycie na osobę na dzień | woda: d4 +60 l; d9 −50 %; 1 l/os./dzień |
| **Zasady świata w czasie** | co działa od kiedy do kiedy | prąd z sieci do d2 18:12; obwód zamków C przecięty w nocy 1; linia wewnętrzna do d11; agregat od d14 |
| **Wątki** | zapowiedź → wskazówki → rozwiązanie, każde z numerem ujęcia | „Nowak przeciął kabel”: d5 rękawy · d5 „dla Kuby” · d7 dłoń na rękawie · d10 jego klucz · d12 żółta przywieszka · d16 wyznanie |
| **Wiedza** | kto wie co i od kiedy (widz, narrator, każda postać) | widz wie o geście Nowaka od d7, narrator od d12 |

### 2. Ujęcia z etykietami i beaty z przyczyną

Każdy beat w rozpisce dostaje pole **„bo”**, czyli odwołanie do wcześniejszego beatu albo do zasady świata, które go wywołują.
Każde ujęcie dostaje etykiety:
- `miejsce`, `obsada`,
- `rekwizyty`,
- `zasiewa`, `wskazówka`, `rozwiązuje`,
- `zmienia` (np. `woda −20 l`),
- `mówi` (wiedza, którą zdradza lektor albo kwestia).

To odpowiada wprost na Twoją zasadę: jeśli coś stało się 20 beatów wcześniej, późniejszy beat ma na to wskaźnik, a kontrola sprawdza, czy ten wskaźnik istnieje.

### 3. Kontrola świata — bramka przed rysunkiem i przed Studio

Skrypt `kontrola_swiata.py` sprawdza reguły bez AI. Reguły biorą się z [PLAN_ANIMACJA_SURVIVAL.md](../../PLAN_ANIMACJA_SURVIVAL.md) 6.2 i z audytu:

- **Zasiewy:** każde rozwiązanie ma wcześniejszy zasiew **pokazany w ujęciu**, a każdy zasiew ma rozwiązanie (albo jest jawnie otwarty).
- **Rekwizyty:** przedmiot nie jest użyty ani pokazany przed zasianiem i nie jest w dwóch miejscach naraz.
- **Zasoby:** żaden zasób nie spada poniżej zera, a liczba w kwestii albo na kartce równa się stanowi z księgi (kwestie piszę z polem `{woda_dni}`, a nie z liczbą).
- **Stan świata:** nie ma ujęcia, w którym dzwoni telefon bez linii, świeci lampa bez prądu albo działa zamek bez zasilania.
- **Ruch:** przejście tylko po połączeniach z planu budynku; postać nie jest w dwóch miejscach w tej samej chwili.
- **Imiona:** jedno imię = jedna postać.
- **Wiedza:** lektor ani postać nie mówią rzeczy, której jeszcze nie wiedzą. To chroni dramatyczną ironię, jak w #9.
- **Obsada:** postać nie pojawia się przed wejściem do historii, chyba że jako wspomnienie.

`zamien_dzien.py` i `studio_dzien.py` **odmawiają pracy**, gdy jest błąd ●●●. Audyt przestaje być jednorazowy i robi się sam przy każdej zmianie.

### 4. Rysunek czyta stan

Funkcja ujęcia dostaje `S = B.swiat(dzień, ujęcie)` i z niego bierze:
- czy lampa świeci,
- ile jest kresek na ścianie,
- kto ma kurtkę i krótkofalówkę,
- liczby na kartkach,
- układ piwnicy.

Nie wpisuję już tego ręcznie w każdym ujęciu.

## Jak wtedy powstaje sekwencja (kolejność pracy)

1. **Dzień w scenariuszu.**
2. **Wejście i wyjście dnia z księgi:** co dzień przejmuje (otwarte wątki, stan zasobów, kto gdzie jest, kto co wie) i co zmienia.
3. **Beaty z przyczyną („bo”)** i z mapą wiedzy widza i narratora.
4. **Ujęcia z etykietami**, długości z `tempo.py`, rytm z [MASTER_BIBLE.md](MASTER_BIBLE.md).
5. **`kontrola_swiata.py`** — zero błędów ●●●.
6. **Rysunek** czyta stan; arkusz klatek; Studio.

## Gdzie to jest w Studio

Aplikacja ma już miejsca na te dane, tylko ich dotąd nie wypełniałem:
- **Story Bible** — pola na postacie, chronologię i przejścia.
- **Reżyseria i napięcie** — w beatach są pola `viewerKnows` i `characterKnows` ([DIRECTOR.md](../../DIRECTOR.md)).
- **Continuity Editor** — zakładka do kontroli ciągłości.
- **Rekordy z PLAN_ANIMACJA_SURVIVAL 6.2** — postać, lokacja, przedmiot, zasada, tajemnica i scena są opisane w planie, ale jeszcze niezbudowane.

Plan:
1. Najpierw księga jako plik przy filmie (szybko, od razu dla Oddziału C).
2. Eksport do Studio: bible, beaty z wiedzą widza i postaci, notatki ciągłości.
3. Potem przeniesienie reguł kontroli do `studio_core`, żeby działały w aplikacji dla każdego filmu.

## Kolejność wdrożenia

1. **Twoje decyzje** z końca audytu (telefon, plan budynku, kabel, liczba dni, woda, pianino).
2. **Księga świata dla dni 1–30** i `kontrola_swiata.py`. Pierwsze uruchomienie musi znaleźć wszystkie 24 błędy z audytu — to test, że kontrola działa.
3. **Poprawki scenariusza** (A_DO_SWITU.md) i rozpiski dni 1–10 aż do zera błędów ●●●. Potem rysunki dni 1–10 czytające stan, ponowne wgranie do Studio.
4. **Dni 11–30** przez tę samą bramkę.
5. **Eksport do Studio** i przeniesienie reguł do aplikacji.
