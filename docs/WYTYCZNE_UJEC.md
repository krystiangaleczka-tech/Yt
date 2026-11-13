# Wytyczne ujęć — jak budować kadr, żeby reżyser nie musiał poprawiać rysunku

Obowiązuje każdego, kto tworzy albo poprawia ujęcia: Claude, inne agenty i skrypty renderu (`output/*/render*.py`),
sceny Stage w Studio i obrazy generowane do ujęć. Reżyser ocenia **grę, rytm i nastrój** — nie powinien wyłapywać
błędów rysunku. Każdy punkt poniżej wziął się z prawdziwej poprawki (sekcja „Skąd te zasady”).

## 1. Zasady kadru

### 1.1 Otwór przycina wszystko, co jest za nim
Postać lub przedmiot za szybą, okienkiem w drzwiach, oknem budynku, kratą czy lustrem jest widoczny **tylko w obrębie
otworu**. Nic nie wystaje na ramę, ścianę ani pod parapet — ani żuchwa, ani dłoń, ani krew, ani para z oddechu.
- Kolejność rysowania: tło za otworem → to, co za otworem → **ściana/drzwi wokół otworu (zasłona)** → rama → szyba/kraty/siatka.
- Zasłona to płaskie prostokąty w kolorze ściany bez drżenia kreski (`amp=0`), z zapasem na grubość kreski i na ruch
  (odskok, przekrzywienie, uderzenie) — sprawdzaj skrajne położenie, nie spoczynkowe.
- Kraty, siatka i szyba są **przed** postacią.
- W Studio: przypisz postać do obszaru lokacji („Widać przez: Okno”) — wtedy przycinanie robi aplikacja.

### 1.2 Nic nie bierze się znikąd i nie znika bez powodu
Każda postać lub rzecz wchodzi przez drzwi, zza krawędzi kadru, zza przeszkody albo z ciemności, a wychodzi tak samo.
- „Wychodzą z sal” znaczy: z konkretnych, otwartych drzwi, z progu w głąb korytarza. Nie wjeżdżają zza krawędzi kadru obok.
- Otwierają się tylko te drzwi, z których ktoś wychodzi albo które opowiadają historię. Reszta jest zamknięta.
- Pętle ruchu (np. sylwetki przechodzące za szybą) zawijają się **za zasłoną**, nigdy na widoku.
- Efekty świetlne, maski jasności i migotanie nie mogą przypadkiem wygasić ważnego elementu (oczy w ciemności muszą
  zostać wszystkie i nie mrugać razem z lampą). Elementy do zachowania wybieraj z obrazu **przed** maską i migotaniem.

### 1.3 Kamera nie pokazuje końca świata
Najazd, panorama i wstrząs nigdy nie odsłaniają pustki poza narysowanym planem (czarny pas przy krawędzi).
W skryptach renderu kamera idzie zawsze przez `framed()` z `output/zombie-psychiatryk/render.py`:
przesuwa środek kadru i w razie potrzeby minimalnie dobliża. Nowy plan rysuj z zapasem poza 1280 × 720 albo licz
na `framed()`. Kadr robi kamera (zoom wokół punktu), nie powiększanie postaci — skala postaci w lokacji jest stała.

### 1.4 Ciało jest jednym kawałkiem
Części ciała i ubrania **zachodzą na siebie** (nogi wchodzą pod koszulę/tułów, szyja pod głowę, ręka w rękaw) we
wszystkich fazach ruchu: podskok w chodzie, oddech, skłon, uniesione ręce. Sprawdzaj fazę największego rozciągnięcia,
nie pozę spoczynkową.

### 1.5 Bliżej kamery = rysowane później
Dłoń zasłania dziurkę od klucza, na której leży; słuchawka, która spadła przed aparat, jest przed nim; postać w drzwiach
jest przed ich wnętrzem, ale za framugą bliższą kamerze. Przy każdym nowym przedmiocie zadaj pytanie: co jest bliżej?
- **O kolejności decyduje linia stóp.** Kto stoi za biurkiem czy stołem, ma stopy wyżej niż nogi mebla (bliżej
  ściany) — i dopiero wtedy mebel rysuje się na nim. Stopy poniżej mebla, a blat przecinający tułów, to postać
  „przechodząca” przez mebel (`kit_a.duty_desk` / `DESK_STAND`, `kit_a.staff_table` / `TABLE_STAND`).
- **Przejście przez próg ma kolejność, która się zmienia.** Póki postać idzie wzdłuż ściany, jest przed nią i przed
  framugą; za framugę chowa się dopiero, gdy stoi na wprost otworu i robi krok w głąb. Framuga nigdy nie dzieli twarzy
  postaci w pół — ręka sięgająca z drzwi na zewnątrz jest przed framugą.

### 1.12 Co trzymane, ma dłoń i rękę
Słuchawka przy uchu, przepustka chowana do kieszeni, dłoń na czyjejś piersi — rzecz trzymana ma dłoń, a dłoń rękę,
która prowadzi do barku tej postaci (albo wychodzi spod kadru tam, gdzie ten bark jest). Nie ma słuchawek wiszących
przy uchu ani dłoni bez ręki (`kit_a.handset(..., who=)`, `kit_a.listening`).

### 1.6 Fizyka i ciągłość przedmiotów
Przedmiot ma przyczynę ruchu (drgania dzwonka zrzucają słuchawkę) i dźwięk (uderzenie o stół). Rzecz pokazana w jednym
ujęciu jest taka sama w następnym (telefon na biurku w dyżurce = telefon w zbliżeniu). Zakładaj przy tym, co widz wie:
zamknięte drzwi sprawdza się klamką, a nie tylko się o nich mówi.

### 1.7 Tłum to osobne postacie
Każdy w grupie ma własne opóźnienie, tempo i własną reakcję (jeden przystaje, drugi się spóźnia, trzeci unosi ręce
później). Ten sam ruch u wszystkich w tej samej klatce wygląda jak kopia.

### 1.8 Ujęcie ma czas na akcję
Długość ujęcia wynika z akcji i kwestii, nie odwrotnie. Gdy akcja potrzebuje czasu (najazd do okna, sprawdzenie klamki),
ujęcie się wydłuża, a wszystko za nim przesuwa się razem. Dlatego **czasy w renderze liczy się od początku sceny**
(`SCENES[i][0] + …`), nigdy jako twarde liczby bezwzględne.

### 1.9 Długość ujęcia wynika z treści, a dzień z ujęć
Nie ma siatki „tyle sekund na ujęcie” ani „tyle sekund na dzień”. Kwestia lektora albo dialog trwa tyle, ile jej
wypowiedzenie (ok. 2,5 słowa/s) plus oddech przed i po — opowiadanie i tłumaczenie to dłuższe ujęcia. Akcja tnie się
szybko (1–2 s). Detal i reakcja bez słów są krótkie, plan ogólny trwa tyle, żeby widz się zorientował, a napięcie i cisza
trzymają dłużej. Każdy rodzaj beatu ma swój rytm; dzień ma długość, jaką dają jego ujęcia, więc każdy dzień jest inny —
od 60 s (spokojny dzień) do ok. 100 s (dzień pełen akcji albo rozmów; reżyser, 6.11.2026); poza tym zakresem przebuduj
rozpiskę. Dłuższa kwestia wydłuża swoje ujęcie, a nie skraca ujęć bez słów.
W wariancie A liczy to `docs/filmy/oddzial-c/ujecia/tempo.py`; zasada jest też w Story Bible projektu (pole „Narracja”).
**Wersja językowa liczy się z własnych nagrań.** Rozpiska liczy ujęcia pod kwestie w języku oryginału; nagranie
w innym języku bywa dłuższe. Wtedy ujęcie się wydłuża (oddech przed ≥ 0,5 s, pauza po 0,6–1,2 s), a nie kwestia
przesuwa się pod cięcie — Oddział C EN: `output/zombie-psychiatryk/en_film.timing`. Kontrola: żadna kwestia nie kończy
się bliżej niż 0,5 s przed cięciem i żadna nie wychodzi za cięcie.

### 1.10 Ruch po schodach w osi ruchu, stopa na stopniu
Postacie zestawu są rysowane od przodu i od tyłu, więc schody (i każdą pochylnię) pokazuje się **w osi biegu**:
schodzący idzie na kamerę (od przodu), wchodzący się oddala (od tyłu). Schody z boku z postacią od przodu dają
przeskoki ze stopnia na stopień albo sunięcie ukosem nad stopniami.
- Stopy stoją na powierzchni policzonej z tej samej geometrii, z której narysowano miejsce. Klatka schodowa wariantu A:
  `kit_a.stair_flight` (rysunek) + `st_walker` / `st_group` (chód): krok to przeniesienie jednej stopy, kolano zgina
  się w stronę ruchu, każda postać ma własny zegar kroków (tempo, postoje, krok dostawny).
- Sprawdzaj klatkę w połowie kroku: jedna stopa na stopniu, druga w powietrzu nad krawędzią — nie w stopniu.
- Rekwizyt na schodach (puszki, rolka bandaża) też ma miejsce w tej geometrii (`st_can`, `st_proj`), żeby kolejne
  ujęcia pokazywały go w tym samym miejscu.

### 1.11 Postać w oddali to pomniejszone zbliżenie, profil to profil
Wzorem jest zbliżenie (np. zarażony z profilu w d04_22): w planie ogólnym ta sama postać ma te same proporcje
i **cieńszą kreskę w skali postaci**, a małe elementy (oczy, źrenice, uszy, usta) nie „gotują się” w kleks.
Twarz odwrócona w bok bardziej niż o pół (look ≥ 0,55) rysuje się **z profilu**: nos wystaje poza obrys głowy,
jedno oko jest w głowie (nie na jej krawędzi), ucho z tyłu, usta z przodu — nie przesunięta twarz od przodu.
W skryptach: `kit_a.scaled` (figure / figure_back / sitting / zarażeni) i `kit_a._profile_face`.

## 2. Obrazy generowane do ujęć (AI, Paper Theatre, pozy)

- Osobne warstwy: tło bez postaci, postać (PNG RGBA, przezroczyste tło), **pierwszy plan zasłaniający** (drzwi z
  okienkiem, framuga, rama okna) jako osobna warstwa z wyciętym otworem. Nigdy nie generuj postaci „wklejonej” w okno
  jednym obrazem — nie da się jej potem schować ani poruszyć.
- Postać generuj w całości (z głową, żuchwą i rękami), nawet jeśli kadr pokaże tylko część — przycina otwór, nie generator.
- W prompcie podawaj skalę i punkt widzenia zgodne z lokacją, jeden obiekt na obraz, „no frame, no window, no background”
  dla warstw postaci i rekwizytów.
- Po wygenerowaniu: sprawdź kanał alfa i niemal przezroczyste marginesy (mylą położenie; patrz
  `output/imperium-papierowe/correct_layout.py`), skalę wobec innych postaci w tej lokacji i ciągłość z poprzednim ujęciem.
- Ustaw w lokacji obszary (szyby, drzwi) i linię podłogi — bez nich recenzent kadru Studio nie sprawdzi geometrii
  ([STUDIO_ANIMATION.md](STUDIO_ANIMATION.md)).

## 3. Kontrola przed oddaniem ujęć reżyserowi

Zanim ujęcie trafi do Studio do oceny:
1. **Arkusz klatek**: początek, środek, koniec ujęcia i **każde zdarzenie** (wejście postaci, odskok, uderzenie, najazd,
   zgaśnięcie światła) — obejrzyj go, nie tylko wyrenderuj.
2. **Skrajne położenia**: przy każdym otworze obejrzyj klatkę, w której ruchoma rzecz jest najbliżej krawędzi otworu.
3. **Automatycznie**: `python3 scripts/kontrola_ujec.py output/<film>/render.py` — szuka pustych krawędzi kadru
   (koniec świata), gasnących jasnych elementów i robi arkusz klatek do obejrzenia. W ciemnych ujęciach z winietą
   „pusta krawędź” bywa fałszywa — rozstrzyga test płótna w kolorze magenta (nienarysowane miejsce świeci na różowo).
   Po poprawkach porównaj render z materiałem w Studio na **tych samych numerach klatek** i wgraj tylko zmienione ujęcia
   (`studio_dzien.py <dzień> <projekt> tylko=…`).
4. **Przejrzyj uwagi**: wszystkie uwagi reżysera w ujęciach i markery na klatkach z tego filmu muszą mieć odpowiedź w
   obrazie. Marker ma klatkę osi Studio (30 kl./s), render ma 24 kl./s — przeliczaj przez sekundy.
5. Napisz reżyserowi wprost, co sprawdzono i czego nie.

## 4. Praca w Studio

- Poprawki robi się w ujęciach (Sceny → ujęcia) i na osi montażu; **bez eksportu**, dopóki reżyser nie poprosi.
- Skrypty filmów mają tryb `update` (np. `python3 output/zombie-psychiatryk/studio_import.py update <projekt>`):
  renderuje same ujęcia, podmienia materiał i przesuwa obraz, lektora i efekty na osi.
- Kolejność zapisu: najpierw oś montażu (nowy materiał razem z nową długością), potem ujęcia — inaczej serwer odrzuci
  klip dłuższy od starego pliku. Przesunięcie klipu na osi przesuwa też jego ujęcie — ujęć dalszych dni nie zapisuje
  się potem drugi raz (podwójne przesunięcie, a przy wczesnym dniu ponad 200 operacji i odmowa serwera; 6.11.2026).
  Zmiana samych kwestii albo długości: `docs/filmy/oddzial-c/ujecia/podmien_w_miejscu.py` — bez kasowania ujęć.
- Plik ujęcia ma pokryć całą długość ujęcia na osi (zaokrąglaj liczbę klatek renderu w górę).
- Nie usuwaj uwag ani markerów reżysera — to jego notatki.

## 5. Skąd te zasady (Zombie Psychiatryk — Oddział C, 3.11.2026)

| Ujęcie | Błąd | Zasada |
|---|---|---|
| 01 Szpital nocą | sylwetka w oknie wychodziła poza obrys okna przy odskoku | 1.1 |
| 03/02 Twarz w szybie | żuchwa i krew wychodziły pod okienko drzwi izolatki | 1.1 |
| cz. 2 Pod szybą / Głowy | sylwetki widoczne na ścianie obok szyby (poprawka wcześniejsza) | 1.1, 1.2 |
| 02 Sanitariusz z latarką | nogi oderwane od tułowia w chodzie | 1.4 |
| 04/02 Skrzypnięcie | otwierały się wszystkie drzwi, a zombie wjeżdżały zza krawędzi kadru | 1.2 |
| 07/01 Klucz w zamku | dziurka od klucza narysowana na dłoni | 1.5 |
| 04 Drzwi za mną | najazd odsłaniał czarny pas za prawą krawędzią planu (znalezione w kontroli) | 1.3 |
| 03/01 Ciemne okienko, 10/01 Głowy | czarny pas u góry kadru (znalezione w kontroli) | 1.3 |
| 10/02 Tylko oczy | z czterech par oczu zostawały dwie i gasły z migotaniem (znalezione w kontroli) | 1.2 |
| 07/02 Gaśnie światło | „zamknąłem drzwi” bez gestu sprawdzenia — reżyser dodał klamkę i 1 s | 1.6, 1.8 |
| 01 Szpital nocą | za krótkie ujęcie na najazd do okna — reżyser wydłużył | 1.8 |
| 06, 08 | jednakowy tłum — reżyser dodał uniesione ręce, przystanięcie ostatniego | 1.7 |
| Wariant A, dni 1–30 (4.11) | wszystkie ujęcia ~4 s i każdy dzień po 66 s — film „jak wolny film”; potem równe 2,5 s bez względu na kwestie | 1.9 |
| Wariant A, dzień 1 (4.11) | ręka nie przy tułowiu, but jak deska, framuga znika, postacie przechodzą przez kratę, stopy obok stopni | 1.1, 1.2, 1.4, 1.5 |
| Wariant A, dzień 5/07 Kołnierz (4.11) | zbliżenie z głową wysoko: tułów urywał się w połowie kadru jak pływający prostokąt (znalezione w kontroli; `face_cu` ciągnie teraz tułów poza dolną krawędź) | 1.3, 1.4 |
| Wariant A, przegląd dni 1–30 (5.11) | rekwizyt przesunięty w ujęciu zostaje też na starym miejscu (dwie kanapy, d24); ciężarówki „odjeżdżają” w lektorze, a na obrazie stoją do końca (d18–20) | 1.2, 1.6 |
| Wariant A, przegląd dni 1–30 (5.11) | słuchawka odkładana od ucha przejeżdża przez oko (d20, d26); ręka sięga przez pół kadru, bo postacie stoją za daleko (d1/27, d28/11) | 1.4, 1.5 |
| Wariant A, przegląd dni 1–30 (5.11) | zmiana stanu postaci znika w następnym ujęciu (białe oczy Nowaka po przemianie, d17); postać zmienia pozę skokiem bez fazy pośredniej (siedzi → stoi, d13/16; „udaje sen” na stojąco, d11/22) | 1.2, 1.4 |
| Wariant A, przegląd dni 1–30 (5.11) | pod skrzydłem drzwi nic nie zasłaniało podłogi — nogi z podwórza wystawały pod drzwiami (d29); tłum za szybą w skali planu ogólnego — dwie wielkie postacie zamiast dziesiątek (d29/17) | 1.1, 1.7 |
| Wariant A, przegląd dni 1–30 (5.11) | liczba kresek na ścianie nie szła za dniem (d16–20 miały 15) — licznik w kadrze to też ciągłość (`kit_a.tally` liczy z `DAY`) | 1.6 |
| Wariant A, schody: d01, d03, d05, d06, d09, d22, d23 (5.11) | „nie podoba mi się animacja chodzenia po schodach” — schody z boku, postacie od przodu: przeskakiwały ze stopnia na stopień albo sunęły ukosem nad stopniami | 1.10 |
| Wariant A, kwestie dni 1–30 (6.11) | urwane dopowiedzenia bez czasownika („Kratę owinęliśmy ręcznikami. Nie zadzwoniła.”, „Poszli dalej. W stronę rozdzielni.”) i brak łączników w ciągach zdarzeń; dni przy 80 s ściskały ujęcia bez słów | Rytm 4, MASTER_BIBLE 2.4, D9; 1.9 (60–100 s) |
| Wariant A, rig dni 1–30 (11.11) | łza, uśmiech, nadęte policzki i słuchawka dorysowane po twarzy w stałym miejscu odklejały się od głowy, gdy głowa dostała ruch (znalezione w kontroli; rysuje się je w `kit_a.on_face`) | 1.4, 1.5 |
| Wariant A, rig dni 1–30 (12.11) | „oko dziwnie wygląda” w widokach z profilu: po skręcie głowy jedno oko lądowało na obrysie; w oddali twarze jak kleksy (gruba kreska zbliżenia i drżenie na małych oczach) — „wzoruj się na zbliżeniu” | 1.11 |

| Wariant A EN, przegląd całego filmu (13.11.2026) | „za szybko się kończą zaraz po kwestii, albo mówi i w połowie się ucina”: ujęcia liczone pod polskie kwestie, angielskie nagrania dłuższe — 124 z 287 kwestii kończyło się 0,25 s przed cięciem, 27 bez oddechu przed, d01_18 za cięciem; film dni 1–30: 36,8 → 40,3 min | 1.9 |
| Wariant A EN, przegląd (13.11.2026) | „ktoś przechodzi przez ramę drzwi, a powinien być nad nią”: dalsza framuga przecinała narratora już na korytarzu (d01_12), framuga dzieliła twarze w pół kroku, ręka Henryka szła przez wnętrze ściany (d14_12); skrzydło drzwi izolatki wystawało za ościeżnicę i znikała podłoga (d16_16) | 1.1, 1.5 |
| Wariant A EN, przegląd (13.11.2026) | stopy przed biurkiem/stołem, a blat przecinał tułów (d01_02, d02_16, d22_02, d26_01, d29_08); widok za oknem łącznika jako płaski prostokąt na oknach w perspektywie (d13_12) | 1.1, 1.5 |
| Wariant A EN, przegląd (13.11.2026) | słuchawka wisiała przy uchu bez dłoni (d20, d21, d25, d26, d28, d29 — ok. 20 ujęć); dłoń bez ręki na kieszeni (d15_08); ręka „kogoś trzeciego” spod kadru zamiast od barku Henryka (d23_08) | 1.4, 1.12 |
| Wariant A EN, przegląd (13.11.2026) | paczka z drona lądowała gdzie indziej, niż leży w następnych ujęciach (d10_01); oko i nos odwracającego się zarażonego nie szły za kołysaniem głowy (d10_14); obrót z przodu na plecy bez profilu (d30_16); „He's clear” o Zosi (d30_10) | 1.2, 1.4, 1.6 |

Otwarte: słuchawka w „Starym telefonie” nie ma kabla do aparatu, a po spadnięciu telefon dzwoni dalej (świadomie,
dla ciągłości z następnym ujęciem) — do decyzji reżysera.
