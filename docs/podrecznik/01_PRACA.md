# Jak pracujemy: od scenariusza do ujęcia

Zasady wspólne dla każdego filmu w DocOS Studio. Każdy film ma dodatkowo **warsztat** (zakładka Continuity Editor →
Warsztat): konkretne narzędzia, pliki i polecenia tego projektu.

## Role

- **Reżyser (autor)** decyduje o historii, grze i rytmie; zatwierdza etapy i recenzje jednostek. Nie poprawia
  rysunku — błędy kadru wyłapuje kontrola i wykonawca.
- **Wykonawca** (człowiek albo Claude) rozpisuje, rysuje, wgrywa i prowadzi dziennik.
- **Recenzent** sprawdza jednostkę po jej zrobieniu (rozdział „Recenzja jednostki”). Może nim być reżyser, drugi
  wykonawca albo agent — ważne, żeby nie oceniał tylko własnej pracy bez listy kontrolnej.

## Jednostka filmu

Film dzieli się na **jednostki** — akty w aplikacji. W serialu dzień po dniu jednostką jest dzień (np. „Dzień 7”).
Każda jednostka przechodzi ten sam cykl:

1. **Wejście** — co jednostka dziedziczy: otwarte wątki, stan zasobów, kto gdzie jest i kto co wie (księga świata).
2. **Scenariusz jednostki** — w etapie Akty / Scenariusz; zgodny z Master Story i Story Bible.
3. **Beaty z przyczyną** — każdy beat ma odpowiedź na pytanie „bo co?” (wcześniejszy beat albo zasada świata).
4. **Ujęcia** — rozpiska: kadr, ruch, opis wydarzenia w ujęciu, kwestia; długości z zasad rytmu.
5. **Księga świata** — dopisz, co jednostka zasiewa, wyjaśnia, zużywa i zmienia.
6. **Kontrola** — przycisk „Sprawdź ciągłość”; zero błędów wagi 3, zanim cokolwiek zostanie narysowane.
7. **Wykonanie ujęć** — rysunek / generowanie; arkusz klatek; wgranie do Ujęć i na oś montażu.
8. **Recenzja jednostki** — lista kontrolna; status „zatwierdzona” albo „do poprawy” z uwagami.
9. **Dziennik** — krótki wpis: co zrobiono, dlaczego, jakie pliki, wynik kontroli.

## Etapy w aplikacji

Story Bible → Projekt → Pomysł i tytuł → **Szkice ujęć** → Master Story → Akty → Sekwencje → Scenariusz → Plan scen →
Reżyseria i napięcie → Sceny / Canvas → Ujęcia → Montaż → **Continuity Editor** (świat, kontrola, recenzje, dziennik,
warsztat) → **Gotowość filmu** → Eksport.

**Gotowość filmu** pokazuje, których kroków z „Nowy film krok po kroku” (7–13) filmowi jeszcze brakuje do oddania:
lektor na ścieżce a1 (brakujące kwestie z numerami ujęć), muzyka a2 i efekty a3 na całą oś (dźwięk krótszy albo dłuższy od
filmu = „do przeliczenia”), zgoda reżysera na próbkę dźwięku, recenzje jednostek, kontrola ciągłości i render końcowy
(tylko informacja — robi go reżyser). Stan liczy się sam z projektu (`GET /api/projects/{id}/gotowosc`); ręcznie zapisuje
się tylko decyzję reżysera o próbce — z cytatem, jako wpis „próbka dźwięku” w dzienniku
(`POST /api/projects/{id}/gotowosc/probka {"decision": "zatwierdzona" | "do poprawy", "quote", "sample"}`). Zanim film
trafi do reżysera, wszystkie wiersze poza „informacja” mają być „gotowe”.

Zmiana na wcześniejszym etapie unieważnia zatwierdzenia późniejszych (podpisy). Zmiana ujęć unieważnia recenzję
jednostki i oznacza jednostki z nią powiązane (rozdział „Dziennik pracy i zmiany w locie”).

## Szkice ujęć (po tytule, przed rozpiską)

Do jednego tytułu można podejść na wiele sposobów. Zanim powstanie cały film, reżyser porównuje **kilka zupełnie różnych
podejść** (domyślnie trzy warianty A, B, C; można dodać do 12) i zatwierdza jedno. Szkic jest dla całego filmu, więc
nie jest jednostką (tabela „Jednostka filmu” go nie dotyczy).

- **Wariant** = tytuł podejścia, wklejony scenariusz (struktura, hooki, kwestie) i lista ujęć: numer, klucz, kadr,
  długość w sekundach, opis, kwestia lektora, znacznik (np. „HOOK 1”, „pogorszenie”, „promyk nadziei”), opcjonalnie
  klatka.
- **Wypełnianie ręcznie** — wklej scenariusz: przegląd od razu kartkuje go z akapitów (akapit = karta; krótka linia
  „HOOK 1”, „# Pogorszenie” albo zakończona dwukropkiem to znacznik następnego ujęcia; tekst w cudzysłowie to kwestia).
  „Rozpisz scenariusz na ujęcia” zamienia akapity na edytowalne ujęcia; klatki wgrywa się przy ujęciu.
- **Wypełnianie z plików** — katalog `docs/filmy/<film>/szkice/<wariant>/` z plikiem `szkic.json` i klatkami obok:
  `{"film", "wariant", "tytul", "scenariusz", "ujecia": [{"nr", "klucz", "sekundy", "opis", "kwestia", "klatka":
  "klatki/001.png", "kadr", "znacznik"}]}` (`kadr` i `znacznik` opcjonalne). W Studio: „Szkice w plikach…” → wybór
  katalogu → „Importuj z plików” (jeden wariant albo cały katalog `szkice/`). Bez Studio:
  `python -m studio_core.cli szkice <id_projektu> <katalog>` albo `POST /api/projects/{id}/sketches/import {"path"}`.
  Klatki: PNG/JPG/WEBP wewnątrz katalogu wariantu, zalecane 1280×720; brakująca albo uszkodzona klatka daje
  ostrzeżenie i kartę, nie błąd. Ponowny import tego samego filmu i wariantu podmienia ten sam wariant.
- **Przegląd jak zeszyt** — pod każdym wariantem odtwarzacz: cały film mija w ustawionym czasie (domyślnie 25 s,
  5–180 s), kartka trwa proporcjonalnie do długości ujęcia, z minimum, żeby żadne nie znikło. Ujęcie bez klatki to
  czarno-biała karta (kadr, opis, kwestia). Spacja — odtwarzaj/pauza, strzałki — poprzednie/następne ujęcie; żółte
  kreski na pasku to znaczniki.
- **Zatwierdzenie** — „Zatwierdź ten szkic” zapisuje migawkę wariantu i wpis w dzienniku pracy (rodzaj „szkic”).
  Dalsze etapy się do niego odwołują: pasek „Szkic ujęć” na etapach od Master Story, przycisk „Przejmij zatwierdzony
  szkic” w Master Story, a AI dostaje go jako kierunek reżysera (struktura, hooki, kolejność).
- **Zmiana po zatwierdzeniu** — wariant oznaczony „Zmieniony po zatwierdzeniu”; kontrola ciągłości pokazuje uwagę
  wagi 2 (reguła „szkic”), aż reżyser zatwierdzi go ponownie. Wypełnione szkice bez zatwierdzenia = uwaga wagi 1.

## Podgląd na żywo (teatr papierowy)

Od 15.11.2026 ujęcia teatru papierowego („Pierwszy cesarz”) Studio rysuje **na żywo z kodu**, bez klipów mp4:

- Python (`output/<film>/na_zywo.py`) liczy tylko ruch ujęcia — kto gdzie stoi, jak duży, jak rozmyty, gdzie kamera
  i światło — ok. 1 ms na klatkę. Karta graficzna w przeglądarce rysuje z tego klatkę tymi samymi wzorami co
  `render.py` (ok. 4 ms zamiast ok. 450 ms). Różnica z renderem: średnio ok. 5/255 na kanał, głównie inne ziarno.
- Studio uruchamia ten serwer samo, kiedy ujęcia projektu mają w `legacy.teatr` film, język i kod ujęcia
  (`{"film": "pierwszy-cesarz", "jezyk": "en", "odn": "d01_06"}`; log: `.docos-studio/logs/teatr-<film>-<język>.log`).
- **Po zapisaniu kodu** ujęć albo świata obraz w „Ujęciach” i „Montażu” odświeża się sam po ok. 1 s; po zmianie
  zestawu wycinków po kilku sekundach. Błąd w kodzie pokazuje się na podglądzie, a widać ostatnią dobrą wersję.
- Znaczek „NA ŻYWO · kod vN” w rogu podglądu; przycisk „klip mp4” wraca do klipów (przełącznik wspólny dla Ujęć
  i Montażu), „na żywo” — z powrotem. Klipy mp4 zostają na osi jako zapas.
- Render końcowy dalej robi `render.py` z tego samego kodu (reżyser, `pc\renderuj*.bat`).
- Ręcznie, jedno ujęcie z porównaniem z Pythonem (klawisz P): `JEZYK=en python3 -I output/pierwszy-cesarz/na_zywo.py 6`
  → http://127.0.0.1:8899.

Czego jeszcze nie ma: napis na podglądzie jest rysowany czcionką przeglądarki (minimalnie inny niż w renderze),
nitki bez wygładzania krawędzi; inne filmy potrzebują własnego `na_zywo.py` (ten sam wzór).

## Poprawki w Studio i render końcowy

Trzy różne rzeczy, których nie wolno mylić:

1. **Render końcowy** — wygenerowanie gotowego filmu do wrzucenia na YouTube (pełna jakość, `pc\renderuj*.bat`).
   Dla reżysera „render” znaczy właśnie to. Uruchamia go **wyłącznie reżyser**, w programie, kiedy wszystko
   w Studio jest zrobione i zatwierdzone.
2. **Klipy ujęć do Studio** — komputer rysuje z kodu klatki jednego ujęcia i zapisuje krótki klip mp4 (podgląd
   1280 × 720, szybkie kodowanie `veryfast`). Tak nowy rysunek trafia do Studio. Trwa to ok. 13 s pracy na
   sekundę ujęcia (30 ujęć, ok. 4 min filmu — kilkanaście minut). To zwykła praca wykonawcy, nie render końcowy.
3. **Aktualizacja w Studio** — skrypt wgrywa klipy do istniejącego projektu, podmienia obraz ujęć, ustawia
   długości, przesuwa kwestie lektora, podmienia muzykę i efekty. Uwagi reżysera przy ujęciach zostają.

Zasady:

- **Zmiana rysunku albo nowe ujęcie w filmie z podglądem na żywo:** wystarczy zapisać kod — Studio pokaże zmianę
  samo. Klipów mp4 do Studio nie rysujesz. Wyjątek: zmiana napisów na wycinkach (`ETYKIETY`) — podgląd trzyma
  wycinki w pamięci, więc zatrzymaj go (`pkill -f output/<film>/na_zywo.py`); Studio uruchamia go sam, a przez kilka
  sekund rozgrzewania ujęcia odpowiadają błędem 500 (stan: `/api/projects/<id>/teatr/stan`, pole `gotowe`).
- **Wycięte, dodane albo przestawione ujęcia:** `studio_film.py plan` dopasowuje ujęcia Studio po kluczu rozpiski
  (`legacy.klucz`), nie po miejscu w akcie, więc uwagi i markery reżysera zostają przy swoim ujęciu (wcześniej po wycięciu
  ujęcia przechodziły na sąsiada). Po planie z nową numeracją: `klatki` dla wszystkich ujęć (zapas na osi idzie po
  odnośniku `dAA_NN`), `efekty.py`, `dzwiek lektor` (zostają tylko nagrania, których tekst się nie zmienił), szkic
  przebudowany (`buduj_szkice.py d`) i zaimportowany od nowa (`POST /api/projects/<id>/sketches/import` z katalogiem
  wariantu).
- **Zmiana rysunku w filmie bez podglądu na żywo:** narysuj klipy tylko zmienionych ujęć i podmień je w Studio — oś,
  lektor, muzyka i uwagi zostają. Nigdy nie rysuj całego filmu, żeby poprawić kilka ujęć.
- **Zmiana długości ujęć** (rytm, pauza po kwestii, nowe nagranie lektora): długości liczy rozpiska filmu, muzykę
  i efekty przelicza się od nowa (to synteza, kilka minut), a obraz to istniejące klipy — dłuższe ujęcie dostaje
  stopklatkę na końcu, krótsze jest przycięte. Rysowanie od nowa nie jest tu potrzebne. Efekt dźwiękowy pod sam
  koniec ujęcia może się minąć ze stopklatką o ułamek sekundy; wyrówna to render końcowy.
- **Render końcowy** liczy tylko ujęcia, które zmieniły się od poprzedniego renderu do tego samego katalogu (odcisk
  klipu: kod ujęcia, stan świata, długość, napis, jakość). Koduje dokładnie (`PRESET=slow`).
- **Gotowy plik na YouTube** składa `zloz.py` z klipów renderu końcowego: obraz, lektor, muzyka i efekty zmiksowane
  jak montaż w Studio (głośności ścieżek z osi, suma bez normalizacji, ogranicznik 0,95). Eksport MP4 w Studio tego
  nie zastępuje — projekt ma rozdzielczość i klipy podglądu. Klipy do złożenia filmu renderuje się z `FILM=1`:
  ujęcie kończy się na klatce najbliższej końcowi z rozpiski, więc film trwa tyle co oś w Studio. Klipy do Studio
  (bez `FILM=1`) są zaokrąglone w górę, żeby pokryły miejsce ujęcia na osi; złożone jeden po drugim byłyby dłuższe
  od osi (16.11.2026, „Pierwszy cesarz” EN: o 1,3 s, muzyka i efekty obok obrazu) — `zloz.py` takich nie składa.
  Nagrania lektora, muzyka i efekty nie idą na GitHuba: przed renderem na innym komputerze trzeba je tam skopiować,
  a `zloz.py --sprawdz` sprawdza, czy są z tej samej wersji co rozpiska.
- 15.11.2026 wykonawca pomylił klipy ujęć z renderem końcowym i zamiast nowych klipów dał do Studio same obrazy
  z klatkami — reżyser: „dla mnie render to jest render, czyli końcowe wygenerowanie filmu do wrzucenia na
  YouTube”. Podgląd z obrazów (`studio_pc.py --podglad`) to tylko awaryjna szybka ilustracja, nie zamiast klipów.

Przykład — „Pierwszy cesarz” (EN), ujęcia dłuższe o pauzę po kwestii (14.11.2026):

```
JEZYK=en python3 output/pierwszy-cesarz/efekty.py
JEZYK=en python3 -I output/pierwszy-cesarz/studio_pc.py --projekt prj_65a9a00a6f9d402c --aktualizuj --stopklatka --klipy build/klipy_en
```

Przykład — nowy rysunek 30 ujęć (15.11.2026; co się zmieniło: `output/pierwszy-cesarz/poprawki/2026-11-15.json`):

```
cd output/pierwszy-cesarz
JEZYK=en PROCESY=3 python3 render.py klipy 3,6,31 ../../build/klipy_en_nowe
cd ../..
JEZYK=en python3 -I output/pierwszy-cesarz/studio_pc.py --projekt prj_65a9a00a6f9d402c --podmien 3,6,31 --klipy build/klipy_en_nowe --zmiany output/pierwszy-cesarz/poprawki/2026-11-15.json
```

Render końcowy (reżyser, na PC): `output\pierwszy-cesarz\pc\renderuj_en.bat`.

## Nowy film krok po kroku (wzór: „Bonnie and Clyde”, 18–19.11.2026)

Cały film od tematu do Studio w półtora dnia. Kolejność, która się sprawdziła:

1. **Temat i kąt.** Najpierw trendy i konkurencja na YouTube (TubeAlfred: zapytania, kanały, wyniki filmów; narzędzia
   „batch” liczą 1 kredyt na element — partię dobieraj do salda). Dla wybranego tematu kilka różnych kątów opowieści
   z dowodami popytu, potem tytuł (szukaj na YouTube, zanim go zaproponujesz).
2. **Szkice ujęć.** Trzy różne scenariusze z hakami (`docs/filmy/<film>/szkice/buduj_szkice.py`, wspólna pula ujęć),
   import do Studio (etap „Szkice ujęć”). Reżyser wybiera albo łączy („robimy A, ale wplatamy B” → szkic D) i zatwierdza.
3. **Własna gałąź i worktree.** `git worktree add .claude/worktrees/<film> -b <film>`; w głównym katalogu dowiązania
   symboliczne `docs/filmy/<film>` i `output/<film>` do worktree, bo Studio działa z głównego katalogu. Commit po każdym
   etapie na gałęzi filmu.
4. **Spójność scenariusza** przed rozpiską: fakty i daty, kto kiedy się pojawia, co jest tajemnicą do którego aktu
   (np. łowca do aktu V), czy kwestie nie zdradzają zakończenia.
5. **Rozpiska i księga.** `dane.py` raz wygenerowany ze szkicu, potem jedyne źródło; `ksiega.py` (świat, postaci,
   rekwizyty, wątki, spoilery; `namedIn` to lista wzorców `["d05_*"]`); `buduj.py` → `ROZPISKA.md`;
   `studio_film.py plan` → kontrola ciągłości bez błędów wagi 3 i 2.
6. **Rysunek po aktach.** Zestaw kraju i epoki (lalki, dekoracje, pojazdy, rekwizyty), `scena.py` (scenografie
   i pomocnicze), ujęcia `ujecia_a.py` / `ujecia_b.py`. Po każdym akcie arkusz klatek (rozdział „Animacja kodem”),
   poprawki, commit.
7. **Kontrole.** `render.py kontrola` (koniec świata) i przegląd dźwięku (`efekty.py` liczy każdą klatkę co 0,08 s —
   wyłapuje też klatki, które się wywracają). Dopiero potem Studio.
8. **Studio.** `studio_film.py plan`, potem `klatki` (po jednej klatce na ujęcie na oś v1 jako zapas; obraz rysuje
   podgląd na żywo — sprawdź `/api/projects/<id>/teatr/stan`). Studio uruchamia `npm run dev` (konfiguracja „studio”,
   API na porcie 8876).
9. **Dźwięk** według rozdziału „Dźwięk”: próbka do akceptacji, dopiero potem `studio_film.py dzwiek`.
10. **Dziennik** po każdym etapie (co, dlaczego, pliki, wynik kontroli), a w nim cytat zgody reżysera.
11. **Lektor** to klon głosu autora we wszystkich kwestiach (reżyser 23.11 przy „Bonnie and Clyde”: „zrób głos mój
    lektorski w całym filmie tak jak w poprzednich”), jedno podejście na kwestię i kontrola Whisperem (rozdział „Lektor”).
    Po nagraniu ujęcia mają długość z prawdziwych kwestii, a akcja przekłada się sama (`render.czas_akcji`, rozdział
    „Animacja kodem”). Po każdej zmianie długości ujęć: `plan`, `klatki` i ponownie dźwięk (muzyka i efekty idą jednym
    klipem na cały film).
12. **Tury poprawek reżysera.** Reżyser ogląda film w Studio (podgląd na żywo; na telefonie — szybki podgląd całego filmu
    640 × 360, 12 kl./s, z pełnym dźwiękiem, w czterech częściach po 4–6 min i do 15 MB, 23.11) i zostawia markery oraz uwagi.
    Każda tura: lista z `scripts/uwagi_rezysera.py`, porównanie z raportem poprzedniej tury, poprawki w kodzie, dźwięk od
    nowa, raport `docs/filmy/<film>/uwagi_rezysera_<data>.md` i lekcje w Wytycznych (sekcja 4.2 i tabela „Skąd te zasady”).
    „Bonnie and Clyde” miał cztery tury (19, 21, 23 i 24.11): 30, 28, 91 i 20 markerów.
13. **Render końcowy** należy do reżysera (albo idzie na jego wyraźną prośbę): `FILM=1 ROZDZIELCZOSC=1440 PROCESY=3
    render.py klipy …`, potem `zloz.py` (rozdział niżej, „Poprawki w Studio i render końcowy”).
14. **Publikacja i Shortsy** — rozdział „Publikacja: miniaturka, tytuł, napisy i Shortsy”.
