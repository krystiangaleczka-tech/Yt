# Audyt ciągłości — Oddział C, wariant A, dni 1–10 (4.11.2026)

**Co porównano:**
- Story Bible w Studio (projekt `prj_f2503a77f5fa44bc`).
- Scenariusz [A_DO_SWITU.md](A_DO_SWITU.md) z dniami 1–30. Późniejsze dni sprawdzono pod kątem tego, co muszą zasiać dni 1–10.
- Rozpiska ujęć [ujecia/a_dane1.py](ujecia/a_dane1.py).
- Rysunki `output/zombie-psychiatryk/render_d01–d07.py` i zimne otwarcie (`render.py`, `render2.py`).

**Gdzie leży błąd:**
- **S** — w scenariuszu,
- **R** — w rozpisce ujęć (moja przeróbka),
- **K** — w rysunku.

**Waga:**
- **●●●** — psuje logikę historii,
- **●●** — widz może wyłapać,
- **●** — drobne.

Wynik: **24 błędy**. W tym 7 psuje logikę historii, a 8 to zasiane elementy, których brakuje na ekranie.
Część poprawek to decyzje reżysera; zebrane są na końcu.

## 1. Świat: prąd, telefon, budynek

| # | Waga | Gdzie | Błąd | Propozycja |
|---|---|---|---|---|
| 1 | ●●● | S d3/20, d4/1 · R d3/25, d4/2 | Telefon w dyżurce C dzwoni nad ranem w dniu 3 i w dniu 4, a jego słuchawka od nocy 1 leży na biurku i piszczy (d1/8, d2/16). Telefon z podniesioną słuchawką nie może zadzwonić. | Dzwoni **inny** aparat, np. w pokoju lekarskim obok dyżurki. Dzwoni kordon, który obdzwania numery szpitala. To od razu zasiewa telefon z kordonu z dnia 20. |
| 2 | ●●● | S d11/6 vs d20/1 | W dniu 11 słuchawka „już nie piszczy, bo padła linia”, a w dniu 20 przez telefon dzwoni por. Malec. | Pada tylko linia wewnętrzna, a miejska działa w portierni. Albo Malec mówi przez krótkofalówkę wojskową zrzuconą w paczce w dniu 10 (patrz #14). |
| 3 | ●●● | S d5/13, d7/5 vs zimne otwarcie | Przecięty „gruby kabel zasilania oddziału C” zwolnił zamki w nocy 1. Tymczasem w zimnym otwarciu na oddziale C palą się świetlówki, a narrator gasi światło w dyżurce, więc oddział miał prąd. | W dniu 7 przecięty jest **kabel obwodu zamków** (rozdzielnica zamków), a nie zasilanie całego oddziału. Sieć gaśnie dopiero w dniu 2 (d2/17). |
| 4 | ●●● | S d11/1, d23/6 · zimne otwarcie | Budynek z pierwszego ujęcia ma parter i dwa rzędy okien, a okno sali 8 jest w środkowym rzędzie, czyli na 1. piętrze. Scenariusz daje salę 8 na 2. piętro, oddział A na 1. piętro „nad kuchnią”, a chirurgię na 3. piętro. | Jeden plan budynku jako źródło: oddział C na 1. piętrze (skrzydło główne), oddział A na 1. piętrze (skrzydło zachodnie, nad kuchnią), chirurgia w wieży. Dzień 11 i dzień 23 dostosować do tego planu. |
| 5 | ●●● | S d1/35, d7/2, d9/11–13 · K `kit_a.basement` | Apteka jest „na końcu korytarza piwnicy” (d1), a rozdzielnia też „w końcu korytarza” (d7). W dniu 9 zarażeni mijają kratę apteki i idą dalej do rozdzielni, więc apteka nie może być ślepym końcem. Rysunek pokazuje aptekę zawsze na końcu. | Plan piwnicy: schody → korytarz → **apteka z boku** → dalej pralnia i na końcu rozdzielnia. Na tym planie zbudować `basement()` i `basement_door()`. |
| 6 | ●● | K d3–d10 (`pharmacy_front`, `pharmacy_inside`) | Od wieczoru dnia 2 nie ma prądu, a na rysunkach w aptece w dzień świeci lampa pod sufitem. | Lampa sufitowa zgaszona od dnia 2. Światło pada z okienka w dzień, a w nocy z latarek i z **lampy akumulatorowej** Zosi (tę „gasi” w d9/8). Lampę trzeba pokazać wcześniej, np. w d2/20. |
| 7 | ●● | S d2/5, d6/19 · bible | Megafon w dniu 2 ogłasza 30 dni kwarantanny, w dniu 6 „zostały 24 dni”, a ewakuacja jest w dniu 30. Liczone od dnia 2 zostałoby 26 dni. | Megafon w dniu 2: „kwarantanna do odwołania, minimum 28 dni”. Albo liczyć od nocy 1 i zostawić 24. |

## 2. Postacie i ich wiedza

| # | Waga | Gdzie | Błąd | Propozycja |
|---|---|---|---|---|
| 8 | ●●● | R d6/7 · K d6 `s_badge` | **Mój błąd:** pielęgniarkę ze schodów nazwałem „Basią z nocnej zmiany” („B. KOWAL”). W bible i w dniu 19 Basia to kucharka z chłodni, którą Henryk nazywa po imieniu. | Pielęgniarka dostaje inne imię (np. „Ewa”). Imion postaci drugiego planu pilnuje lista w księdze świata. |
| 9 | ●●● | R d7/12 | **Mój błąd:** lektor mówi „Został lekarz dyżurny. Stał przed nami.”. Scenariusz celowo trzyma ironię: narrator **nie** zauważa gestu Nowaka, widz tak (d7/11). Narrator domyśla się dopiero w dniu 12 (klucz z żółtą przywieszką), a wyznanie jest w dniu 16. | Zdanie usunąć. Zosia patrzy na Nowaka bez słów, a lektor milczy. |
| 10 | ●●● | R d5 (brak S d5/16–17) | Wypadła wskazówka: Nowak oddaje połowę porcji „Kubie, którego jeszcze nie znają”. Ona zdradza, że Nowak wychodził po nocy na oddział A, i jest zapowiedzią d8/20 („Nowak wychodził sam”). | Dodać w dniu 5 beat z dwoma ujęciami: Nowak odsuwa miskę, mówi „Dla Kuby”, a Zosia pyta „Jakiego Kuby?”. |
| 11 | ●● | S d9/20 vs d8/9 · S d17 | W dniu 9 Henryk „po raz pierwszy od dnia 1 mruga”, choć mrugnął w dniu 8. W dniu 17 narrator pyta, „dlaczego Henryk nigdy nie mruga”. | Zasada: Henryk **mruga tylko celowo, jako znak** (d8 dowód, d9 ostrzeżenie). Dzień 9: „drugi raz w życiu widziałem, jak mruga”. Dzień 17: „prawie nigdy”. W rysunkach to już działa: Henryk nie mruga sam z siebie, więc mrugnięcia w d8 i d9 trzeba narysować jawnie. |
| 12 | ● | S d8/7 · K `kit_a` | Kuba jest „w dresie”, a na rysunku ma zieloną bluzę i dżinsy. | Kostium Kuby: szary dres. Wpis w księdze świata (kostiumy). |
| 13 | ● | R d6/18 vs S d6/13 | Kredowe trasy rysuje narrator (S), a w rozpisce Zosia. | Zostawić narratora, bo w dniu 15 to on przenosi kreski i trasy. |

## 3. Zasoby (woda, jedzenie)

| # | Waga | Gdzie | Błąd | Propozycja |
|---|---|---|---|---|
| 14 | ●●● | S d4/19, d9/14–15, d10 · R d9/18, d10/22 | Liczby się nie bilansują. W dniu 4 jest woda na 4 dni dla 3 osób, więc bez dolewki kończy się w dniu 8. Tymczasem od dnia 5 są 4 osoby, od dnia 8 sześć, a w dniu 9, po wylaniu połowy, „zostają trzy dni”. 12 butelek po 1,5 l w dniu 10 to 18 l dla 6 osób, czyli ok. 3 dni przy 1 l/os./dzień, a nie „tydzień”. | Księga zasobów liczy stan na każdy dzień (litry, porcje, liczba osób, zużycie). Liczby w kwestiach i na kartkach **brać z niej**, a nie wpisywać ręcznie. Do decyzji, ile wody przynoszą z kuchni w dniu 4 (np. 3 kanistry po 20 l). |
| 15 | ● | S d2/14 | Czajnik elektryczny zabrany rano w dniu 2, a wieczorem gaśnie prąd. Brak puenty. | Puenta w dniu 14 (agregat): pierwsza herbata od dwóch tygodni. Albo czajnik usunąć. |

## 4. Zasiane i niezasiane (Czechow)

Elementy, które późniejsze dni wykorzystują, a których w dniach 1–10 nie widać:

| # | Waga | Element | Gdzie jest potrzebny | Gdzie go zasiać |
|---|---|---|---|---|
| 16 | ●●● | **Krótkofalówki** | d13, d14 i d29 (finałowe „teraz”). W scenariuszu pojawiają się w d2/16, w rozpisce wypadły. | d2: w dyżurce obok baterii leżą dwie krótkofalówki. Ujęcie detalu i kwestia Zosi w d2. |
| 17 | ●●● | **Pianino** w świetlicy parteru, Henryk jako nauczyciel muzyki | d18, d21, d25–d30 (plan z pianinem w d27) | d4 (łącznik) albo d8: mijają świetlicę, Henryk zwalnia przy pianinie i przesuwa palcem po zamkniętej klapie. Bez słowa. |
| 18 | ●● | **Karetka** na podwórzu | d10/14–15 | Pokazać ją w widokach podwórza w d2/7 (ciężarówki) i d4/5 (żołnierze z lornetkami). |
| 19 | ●● | **Kurtka** narratora | d10/14 | Narrator nosi kurtkę na mundurku od dnia 2 (zimna piwnica), widać ją w kilku ujęciach. Albo w d10 zabiera z dyżurki kurtkę kierowcy. |
| 20 | ●● | **Kreski na ścianie** | d6/20 („Henryk zrobił już sześć”), d24 („dwudziesta czwarta”) | W d3–d5 w tle ściany widać rosnące kreski Henryka (3, 4, 5). W d6 jest razem **6** kresek: 5 Henryka i 1 narratora. Na moim rysunku d6 jest ich 7 — błąd. |
| 21 | ●● | **Klucze Nowaka** (pęk dyżurnego z żółtą przywieszką) | d10/9, d12/20 | Pęk widoczny przy pasku Nowaka od dnia 5, przywieszka mała i nieczytelna. W d12 zbliżenie na nią. |
| 22 | ● | **Lampa akumulatorowa** | d9/8 („Zosia gasi lampę”) | Patrz #6. |
| 23 | ● | **Notes** narratora | d7/13, później d16, d26, d28 | Pokazać notes w kieszeni od dnia 2, np. przy notowaniu godziny zgaśnięcia prądu (d2/20). Wtedy notuje narrator, a nie Zosia. |

## 5. Bible w Studio

| # | Waga | Błąd | Propozycja |
|---|---|---|---|
| 24 | ●● | W bible stoi i „Pan Henryk — pierwszy widoczny »zmieniony«”, i „nie zarażony”. Pole „Lektor prowadzi opowieść prawie w każdym ujęciu” przeczy zasadzie z zimnego otwarcia (lektor w 10 z 14 ujęć, po oddechu). | Henryk: „nie zarażony; wygląda na zmienionego, bo nie mruga i prawie nie oddycha”. Lektor: zgodnie z MASTER_BIBLE 2.4. |

## Decyzje dla reżysera

1. **Telefon w dniach 3–4** (#1, #2): drugi aparat w pokoju lekarskim, przez który dzwoni kordon. Czy zostać przy jednym telefonie i zmienić scenę?
2. **Plan budynku** (#4, #5): oddział C i A na 1. piętrze w dwóch skrzydłach, chirurgia w wieży, apteka z boku korytarza piwnicy, rozdzielnia na końcu. Czy wolisz inaczej?
3. **Przecięty kabel** (#3): kabel obwodu zamków oddziału C?
4. **Liczba dni kwarantanny** (#7): „minimum 28 dni” czy liczenie od nocy 1?
5. **Woda** (#14): ile przynoszą z kuchni w dniu 4? Z tego wyliczę resztę.
6. **Pianino** (#17): zasiać w dniu 4 czy w dniu 8?

## Stan po poprawkach (4.11.2026, wieczór)

Reżyser przyjął sześć decyzji (D1–D6, zapisane w księdze świata → `decisions`). Poprawiono scenariusz
(A_DO_SWITU.md), rozpiskę dni 2–10, prompty i rysunki. Księga świata jest w Studio (Continuity Editor → Świat),
a jej kopia w [swiat.json](swiat.json). Automatyczna kontrola znajduje wszystkie błędy z tego audytu na danych
sprzed poprawek; po poprawkach **dni 0–10 mają zero błędów wagi 3**.

| # | Co poprawiono |
|---|---|
| 1, 2 | Dni 3–4 dzwoni telefon w pokoju lekarskim (numer miejski; kordon obdzwania szpital). Dzień 20: Malec przez linię portierni. |
| 3 | Dzień 7: kabel **obwodu zamków** oddziału C; lektor „Ktoś otworzył tamte drzwi. Celowo.” |
| 4 | Sala 8 na 1. piętrze; chirurgia w wieży (d11, d23); pianino w świetlicy parteru także w d27 i d30. |
| 5 | Plan piwnicy w księdze świata (apteka z boku, rozdzielnia na końcu). Rysunek korytarza piwnicy jeszcze do przerobienia. |
| 6 | Lampy z sieci gasną od dnia 3 (`kit_a.MAINS`); lampa akumulatorowa Zosi zasiana w d2. |
| 7 | Megafon: „Kwarantanna. Minimum dwadzieścia osiem dni.” |
| 8 | Pielęgniarka ze schodów to Ewa („E. KOWAL”). |
| 9 | Usunięte „Został lekarz dyżurny. Stał przed nami.” |
| 10 | Dzień 5: „Resztę dla Kuby.” — „Jakiego Kuby?” (dwa nowe ujęcia). |
| 11 | Scenariusz d9 i d17: Henryk mruga tylko celowo. |
| 14 | Woda z bilansu: d2 „na dwa”, d3 „na jeden dzień”, d4 „na dwa tygodnie”, d9 „na półtora dnia”, d10 „na trzy dni”. |
| 16–23 | Zasiane: krótkofalówki i kurtka (d2), karetka (d2), notes i lampa (d2), pianino (d4), klucze Nowaka (d5), kreski Henryka (d3: trzy, d6: sześć). |

**Nowe, znalezione przez kontrolę:**

- **#25 (●●●, scenariusz d11–d22):** między dniem 10 a 22 nikt nie przynosi wody, więc bilans kończy się w dniu 12, a w dniu 22 „starczy na cztery dni”. Do decyzji przy przebudowie dni 11+: wyprawy po wodę do kranów (działają do dnia 22) albo kolejny zrzut.
- **#26 (●●):** dzień 1 trwa 126,5 s, a dzień 30 132 s — poza zakresem 55–80 s (dzień 1 czeka na zapowiedziane poprawki).
- **#27:** czajnik z dnia 2 nadal bez puenty (propozycja: pierwsza herbata przy agregacie w dniu 14).

**Obraz (5.11.2026):** dni 2–10 przerysowane i wgrane do Studio (nowe tempo, poprawki, nowe ujęcia; dni 8–10
narysowane od zera). Piwnica wg planu budynku (`kit_a.cellar`), Kuba w szarym dresie, narrator w kurtce od d02_18 do
d10_16, lampy z sieci zgaszone od dnia 3. Oś montażu ułożona od nowa (0 dziur i nakładek; obraz 0:00–14:25,5).
Każdy dzień ma roboczą recenzję agenta — zatwierdzenie należy do reżysera. Dzień 1 czeka na zapowiedziane poprawki.
