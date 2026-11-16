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

### 1.6 Fizyka i ciągłość przedmiotów
Przedmiot ma przyczynę ruchu (drgania dzwonka zrzucają słuchawkę) i dźwięk (uderzenie o stół). Rzecz pokazana w jednym
ujęciu jest taka sama w następnym (telefon na biurku w dyżurce = telefon w zbliżeniu). Zakładaj przy tym, co widz wie:
zamknięte drzwi sprawdza się klamką, a nie tylko się o nich mówi.
- Pojazd ma to, co go napędza: wóz i powóz ciągnie koń, a ktoś nim powozi.
- Postać wygląda na swój wiek i ma tylko te atrybuty, które ma w tej chwili historii: dziecko nie nosi korony, zanim
  zostało królem. Jedna lalka nie gra dziecka i dorosłego.
- Postacie różnią się sylwetką i strojem, a nie tylko kolorem obszycia: kupiec nie nosi dworskiej szaty ze smokami,
  a dwie postacie w jednym kadrze nie są tą samą wycinanką odbitą lustrzanie. Strój mówi, kim postać jest (bogaty
  kupiec, ubogi zakładnik, woźnica, posłaniec).
- Na scenie stoi tylko to, co jest w tym miejscu i czasie. Dekoracja z innej sceny (gliniana armia z grobowca) nie
  stoi przy murze ani przy powozie. Kogo lektor wymienia, ten jest w kadrze: „zginął pod kolumną” znaczy, że leży pod
  kolumną.
- Rekwizyt, który zostaje na miejscu, leży w następnych ujęciach tej sceny (rozwinięta mapa ze sztyletem leży na stole
  przez cały zamach), a w pierwszej klatce ujęcia nie ma niczego, czego ujęcie nie używa.
- Poprawka dekoracji, rekwizytu albo postaci w jednym ujęciu dotyczy **każdego ujęcia, w którym ta rzecz stoi**
  (reżyser 16.11: „jeśli są kolejne ujęcia z tym, to to samo”). Liczy się ją w stanie świata albo we wspólnej funkcji
  sceny, a nie dopisuje w jednym ujęciu; przed oddaniem obejrzyj wszystkie te ujęcia.
- To, o czym jest ujęcie (pałac, czarka z rtęcią), widać w całości: dekoracja boczna stoi po bokach i go nie zasłania,
  a rzecz na rampie czy stole jest nad jej krawędzią, nie w połowie za nią.

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

### 1.11 Rekwizyt w ręce jest w dłoni, a czynność z kwestii widać
Miecz, sztylet, czarka czy list, które postać trzyma, mają rękojeść albo brzeg **w jej dłoni** i idą za nią, kiedy się
porusza lub odwraca (ten sam punkt dłoni w każdym ujęciu tej sceny). O czym mówi lektor, to lalka robi na scenie:
„wypił truciznę” — podnosi czarkę do ust; „kopali studnię” — narzędzie uderza w ziemię i lecą grudy; „zachorował” —
kaszle; „zginął” — widać śmierć, a nie tylko zniknięcie. Postać ma stałą skalę: grozę pokazuje się gestem, cieniem
i światłem, nie powiększeniem lalki.

### 1.12 Rzecz, która się toczy, spada albo przewraca, rusza się jak prawdziwa
Ruch przedmiotu liczy się z jego fizyki, a nie z osobnych krzywych „na oko” (ujęcie 47 „Pierwszego cesarza”, moneta).
- **Toczenie bez poślizgu:** kąt obrotu wynika z przebytej drogi (droga ÷ promień), nigdy z osobnej krzywej czasu.
  Rzecz zwalnia równomiernie i nie pełznie przez ostatnią sekundę.
- **Stoi na powierzchni:** punkt styku leży na blacie albo ziemi przez cały ruch; środek jest o promień wyżej.
- **Kolejność rysowania z punktu styku:** rzecz, która toczy się dalej od kamery niż stos, kałamarz czy inny rekwizyt,
  jest rysowana ZA nim przez całą drogę — inaczej wygląda, jakby przez niego przejeżdżała. Droga omija to, co leży
  na powierzchni (księgę, po której ktoś pisze), i kończy się na wolnym miejscu, nie na krawędzi ani narożniku.
- **Skąd się bierze:** wytacza się zza przeszkody (postaci, krawędzi kadru), a w pierwszej klatce ujęcia jest schowana.
- **Upadek przyspiesza:** przewracanie i spadanie idą coraz szybciej (ok. 0,3–0,45 s), nie jednostajnie i nie w
  zwolnionym tempie; po uderzeniu krótki, gasnący dygot. Mały podskok tuż przed położeniem się (kilka pikseli kadru
  wzorcowego) daje wyraźny moment zdarzenia — rzecz kładzie się w locie i spada tam, gdzie ma leżeć.
- **Każde zdarzenie ma dźwięk w tej samej chwili:** podniesienie, uderzenie o blat, toczenie. Czasy w
  `efekty.ZDARZENIA` są te same co w funkcji ujęcia; dźwięk ciągły (toczenie) cichnie, kiedy rzecz jest w powietrzu.
- **Dźwięk poprawia się punktowo:** po zmianie jednego zdarzenia ścieżka efektów ma się różnić od poprzedniej tylko
  w tym miejscu, a muzyka wcale (porównaj próbki starego i nowego pliku). Skrócenie dźwięku ciągłego zapisuje się
  jako (długość syntezy, ile słychać), żeby nie zmienić losowań reszty filmu. Nowe, usunięte albo inne zdarzenia
  ujęcia: przy pierwszej poprawce dźwięku ujęcia jego dotychczasowa lista idzie do `efekty.W_STUDIO` (wpis zostaje na
  zawsze), a nowe zdarzenia losują z osobnego RNG tego ujęcia. Próba: `DZWIEK_DO=<katalog>` zapisuje nowy plik obok,
  porównanie próbek z plikiem w Studio ma wskazać tylko poprawione ujęcia; potem
  `studio_pc.py --efekty "<wersja>"` podmienia samą ścieżkę Efekty.
- **Miejsce spoczynku to stan świata:** rzecz leży w następnych ujęciach dokładnie tam, gdzie upadła (ten sam kod).

### 1.13 Napis w kadrze czyta widz tej wersji filmu
Każdy napis, który widz ma przeczytać — tabliczka z okrzykiem („AW!…”, „OH!”), zawieszka, napis na kamieniu, mapie
czy sztandarze, tytuł aktu — jest w języku wersji filmu. W kodzie ujęcia stoi tekst polski, a wersja angielska bierze
go przez `zestaw` z `kwestie_en.ETYKIETY`; nowy napis od razu dostaje tam tłumaczenie. Znaki chińskie zostają tylko
jako ozdoba, której nikt nie musi rozumieć (pieczęć, wzór na chorągwi) — nie jako treść, o której mówi lektor.

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
   zgaśnięcie światła) — obejrzyj go, nie tylko wyrenderuj. Czytaj klatkę razem z kwestią lektora: to, o czym mówi
   (postać, wojsko, rzecz), ma być widać w całości, a nie jako czubek zza bliższego planu.
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

## 5. Miniaturka na YouTube

Wzorzec: „Pierwszy cesarz” (16.11.2026) — `output/pierwszy-cesarz/miniatura.py` (scena) i `fujifilm.py` (wygląd zdjęcia).
Dla nowego filmu skopiuj oba skrypty do jego katalogu i podmień wycinki, scenę i napisy.

### 5.1 Układ: zbliżenie, nie plan ogólny
Miniaturkę składa ten sam silnik i te same wycinki co film (teatr papierowy: `papier.py`, `zestaw.py`) — nie osobna
grafika. Reżyser wybrał **zbliżenie**; plan ogólny całej sceny przegrał, bo w małym rozmiarze postacie są za drobne.
- **Po lewej** duża główna postać do pasa przed dekoracją filmu (cesarz przed miastem), z **grubym białym obrysem**
  (ok. 9 px w 1280 × 720). Wskazuje na wydarzenie po prawej.
- **Po prawej** najmocniejsza, najzabawniejsza scena filmu (chłopi z narzędziami w górze, gliniany żołnierz do góry
  nogami w rozkroku jak w pajacyku), postacie z jasnym kartonowym obrysem, żeby odcinały się od wzgórz.
- **W tle** jedno dramatyczne zdarzenie (meteoryt z ognistym ogonem), na ciemnym niebie, żeby ogień świecił.
- **Napisy:** szyld z tytułem u góry i krótkie tabliczki z okrzykiem przy postaciach („NO WAY?!”, „OH!”), lekko
  przekrzywione (ok. 7°). Najwyżej 3–4 napisy, każdy po 1–3 słowa, w języku wersji (1.13). Na YouTube idzie tylko
  wersja angielska.
- **Komiczny akcent na twarzy:** grube czarne spirale wprost na oczach — bez białego tła pod spodem; oko pod spiralą
  zakryte kolorem skóry z policzka, brwi zostają.
- Postacie rysowane kodem specjalnie do miniaturki są większe i dokładniejsze niż w filmie (oczy, mimika), bo stoją na
  pierwszym planie; dwie postacie to różne sylwetki i stroje, nie odbicie lustrzane (1.6).

### 5.2 Czytelność w małym rozmiarze
- Oglądaj miniaturkę zmniejszoną do **320 × 180** (lista filmów na YouTube): tytuł, główna postać, tabliczki
  i wydarzenie mają się czytać.
- Prawy dolny róg zasłania czas filmu — nie stawiaj tam niczego ważnego.
- Obejrzyj zbliżenia każdej grupy: nic się nie styka ani nie nachodzi przypadkiem (narzędzie na meteorycie, grudy
  ziemi na glinie wyglądają jak dziury, ostrze ucięte krawędzią arkusza wygląda jak grot włóczni, szyld z dłuższym
  tytułem EN dotyka krawędzi kadru).
- Test pustki w barwie magenty jak w ujęciach (1.3): kadr nie odsłania końca dekoracji.

### 5.3 Najwyższa jakość pliku
- YouTube zaleca **3840 × 2160** i przyjmuje do 50 MB przy wgrywaniu z komputera (z telefonu 2 MB). Rysuj wprost
  w 4K: `ROZMIAR=3840 python3 miniatura.py en` → `miniatura_en_4k.png` i z tego samego rysunku 1280 × 720 JPG.
- Nic nie jest powiększone z małego obrazu: wycinki rysowane kodem powstają w skali ekranu (`stack_k`), obrazy
  z plików (postać, brama) powiększa Lanczos przed sceną (`wycinek_hd`). Ostrość ustawiona na planie lalek.
- **Nie zmieniaj `zestaw.py` dla miniaturki.** Zmiana tego pliku zmienia odcisk wszystkich klipów i `render.py`
  rysowałby cały film od nowa. Kopię rysunku (np. glinianego żołnierza) trzymaj w `miniatura.py`.
- Do wgrania: PNG bez strat (`miniatura_en_4k_fuji.png`, ok. 16 MB); z telefonu: `miniatura_en_fuji.jpg`. W repo
  zostają tylko te dwa pliki (`miniatura/.gitignore`).

### 5.4 Wygląd zdjęcia z aparatu (Fujifilm)
`python3 fujifilm.py miniatura/miniatura_en_4k.png 1280` — w duchu Fujifilm Classic Negative: lekko wyblakła czerń,
chłodne cienie, ciepłe światła, przygaszona zieleń, ziarno (dokładane osobno w każdym rozmiarze), poświata wokół ognia,
winieta. Efekt ma być **delikatny**: zatwierdzona siła `MOC=0.5` (1,8 „za mocny”, 0,8 „może za dużo tego fuji”)
i rozjaśnienie półtonów `JASNOSC=0.07` (czerń i biel bez zmian). Czysty obraz zostaje obok.

### 5.5 Kolejność pracy
1. Ułóż scenę w `KADRY` (położenia w pikselach ekranu 1280 × 720) i oglądaj szybki podgląd: `JAKOSC=1` (ok. 8 s).
2. Sprawdź zbliżenia grup, rozmiar 320 × 180 i test pustki (5.2).
3. Narysuj 4K i nałóż Fujifilm (5.3, 5.4) — razem ok. 35 s. Reżyserowi oddawaj plik po efekcie.
4. Poprawki reżysera są zwykle małe („przekrzyw”, „niżej”, „grubsze”, „mniej fuji”): jedna liczba w `KADRY`,
   `OCZY_CESARZA` albo `MOC`, potem znowu krok 3.

## 6. Skąd te zasady (Zombie Psychiatryk — Oddział C, 3.11.2026)

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
| Pierwszy cesarz, teatr papierowy (10.11) | stół na przodzie sceny zasłaniał drogę, po której jechał wóz — plan bliższy kamery zabiera cały pas za sobą (znalezione na arkuszu; ujęcia na drodze przeniesione przed pojawienie się stołu) | 1.5 |
| Pierwszy cesarz (10.11) | kamera wieloplanowa opuszczona w dół „topiła” chorągwie i włócznie za bliższym pasmem wzgórz — w pionie kamera się pochyla, nie jedzie (`trucky=0` w `papier.Cam`), więc linie ziemi zostają jak w kadrze wzorcowym | 1.3 |
| Pierwszy cesarz (10.11) | pasek napisu zasłaniał wydarzenie przy dolnej krawędzi (lalka opadająca pod rampę) — kadr ustawia się tak, żeby wydarzenie było nad paskiem (znalezione w kontroli) | 1.8 |
| Pierwszy cesarz (10.11) | kawałki mapy przycięte każdy do własnego obrysu skalowały się jak cała mapa — elementy jednej układanki muszą dzielić jeden układ współrzędnych (`crop=False`) | 1.6 |
| Pierwszy cesarz (10.11, reżyser) | „od 1:00 do 1:40 mało się dzieje” — ujęcia sali stały w miejscu; za mało paralaksy i dekoracji, które się stawiają; szkic 640 × 360 oddany jako materiał do oceny | 1.8 (każde ujęcie ma wydarzenie), 3 (oceniamy pełną jakość) |
| Pierwszy cesarz (10.11) | przy zmianie dekoracji wóz i jeździec wisiały w powietrzu, zanim wysunęła się droga — aktorzy wchodzą razem z ziemią, na której stoją | 1.2 |
| Syn słońca (13.11, arkusz) | głowy węża przy kadziach, chata-pułapka, spichlerz i Himiko chowały się za bliższym pasmem wzgórz, cedrami albo parawanem — rzecz, która ma grać przed pasmem, stoi na planie bliższym niż ono (szyja węża przechodzi na bliższy plan w połowie długości) | 1.5 |
| Syn słońca (13.11, arkusz) | most niebios i wyspa Onogoro za wysoko: bogom ucinało głowy, a łódź z żaglem zasłaniała lalki na pokładzie — przy nowej dekoracji sprawdza się, czy aktorzy mieszczą się w kadrze ujęcia, a nie tylko w kadrze wzorcowym | 1.3, 1.5 |
| Syn słońca (13.11, arkusz) | Ninigi i łodzie stały, zanim wysunęła się rampa i fale (zmiana dekoracji) | 1.2 |
| Syn słońca (13.11, pełna jakość) | w lesie Kumano (las, wrona) wojsko szło za rzędami cedrów, a wojsko Nagasunehiko za bliższym pasmem wzgórz — lektor mówił o wojsku, a widać było tylko czubki włóczni; na małym arkuszu szkicu tego nie wyłapano, dopiero na klatce 1280 × 720 | 1.5, 3.1 |
| Syn słońca (13.11, dekoracja) | Japonia stała na tych samych chińskich górach, sosnach i kulisie z gałęzią co „Pierwszy cesarz” — reżyser: nie kopiować scenerii poprzedniego filmu; każdy kraj i epoka dostaje własny krajobraz (tu Fudżi, łagodne wzgórza z polanami, wiśnie, bambus) | Podręcznik 04 |
| Pierwszy cesarz EN (14.11, Studio) | cięcie padało 0,6 s po ostatnim słowie lektora, bo zaraz zaczynało się następne ujęcie — reżyser: „obcina zaraz po kwestii ujęcie […] i jest to nienaturalne”; obraz trwa jeszcze po kwestii: 1,1 s w środku beatu, 1,4 s na końcu beatu, 1,8 s na końcu sceny, 2,3 s na końcu aktu (dane.py, PAUZA_PO) | Podręcznik 03 (2) |
| Pierwszy cesarz EN (15.11, reżyser, Studio) | uwaga na klatce ujęcia 6: „ten powóz musi ciągnąć koń!” — żaden wóz w filmie nie miał konia; reżyser pytał też, czemu w ujęciu 6 są trzy postacie: chłopca grała zmniejszona lalka cesarza w koronie, więc wyglądał jak trzeci dorosły, a ojciec, zamiast wsiąść na wóz, zapadał się pod scenę | 1.6 |
| Pierwszy cesarz EN (15.11, przegląd obsady) | gliniana armia stała na scenie od budowy grobowca do świtu, także przy spisku, u Fusu pod murem i w powstaniu, i zasłaniała powóz; Jing Ke, o którym lektor mówi „zginął pod kolumną”, w ogóle nie był widoczny | 1.6 |
| Pierwszy cesarz EN (15.11, reżyser) | „widzę dwóch cesarzy patrzących na siebie, beżowy i fioletowy” — ojciec i kupiec to ta sama czarno-złota dworska wycinanka, różniła je tylko barwa obszycia; woźnica wyglądał jak jeździec-posłaniec Qin, chłopiec w Handanie nosił szatę cesarską; po zmianie strojów: „ojcu musisz zmienić posturę i twarz” — ojciec i kupiec stali tak samo ze zwojem; ojciec klęczy teraz na innej wycinance | 1.6 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 50 ujęciach) | kanał z wodą wisiał w powietrzu na początku ujęć ze zmianą dekoracji i stał na scenie do końca filmu („zaś ten kanał z wodą, nie wiem, co tu robi”); poza tym był cienką niebieską kreską („nie wiadomo, o co chodzi”) | 1.2, 1.6 |
| Pierwszy cesarz EN (15.11, reżyser) | sztylet Jing Ke i miecz króla nie w dłoni, zwój na stole w złym kierunku, waga kołysała się cała zamiast belki i szal | 1.11, 1.4 |
| Pierwszy cesarz EN (15.11, reżyser) | lektor mówi o czynności, a lalka nic nie robi: trucizna, kopanie studni, choroba i śmierć cesarza, egzekucja uczonych, podział na 36 prowincji, pisanie (pisarz schowany za stołem) | 1.11 |
| Pierwszy cesarz EN (15.11, reżyser) | eunuch Zhao Gao jako olbrzymia lalka bez podpisu („kto to jest i czemu on jest taki ogromny?”) | 1.11 |
| Pierwszy cesarz EN (15.11, reżyser) | stela wyrastała, zanim kamera do niej dojechała, i była za mała; łodzie nie chowały się za ostatnią falą, tylko stały przed nią; gałąź kulisy zasłaniała chorągwie | 1.3, 1.5, 1.8 |
| Pierwszy cesarz EN (15.11, reżyser) | 15 ujęć za krótkich na swoją akcję („wydłuż”, „wydłuż 3×”) — dane.WYDLUZ | 1.8 |
| Pierwszy cesarz EN (16.11, reżyser, ujęcie 47) | „nie może ten coin tak dziwnie animować” — moneta przejeżdżała przez stos monet i kałamarz (narysowana przed nimi, choć toczyła się za nimi), obracała się niezależnie od przebytej drogi (ślizg) i kładła się ponad sekundę w zwolnionym tempie; teraz obrót wynika z drogi, moneta wytacza się zza pisarza, jest za bliższymi rzeczami, przewraca się coraz szybciej i dygocze po upadku | 1.12, 1.5, 1.6 |
| Pierwszy cesarz EN (16.11, reżyser, ujęcie 47) | po poprawce toczenia: „ja bym ją minimalnie podniósł i w tym momencie dodał dźwięk monety, i jak jest podniesiona, to od razu spada na ten stół” — samo przewrócenie nie dawało wyraźnego momentu; moneta podskakuje z brzękiem i spada na płask (drugi brzęk) | 1.12 |
| Pierwszy cesarz EN (16.11, reżyser, ujęcie 47) | „popraw jeszcze ten zwój” — dalszy koniec zwoju wystawał poza tylną krawędź stołu, więc w detalu blatu zwój wisiał w powietrzu; leży teraz cały na blacie z cieniem tuż pod sobą, a lot do ognia zaczyna się z tego samego miejsca, rozmiaru i obrotu. W detalu sprawdza się, czy rekwizyt mieści się w obrysie powierzchni, na której leży | 1.6, 3.1 |
| Pierwszy cesarz EN (16.11, reżyser, marker w ujęciu 47) | „popraw kierunek tego zwoju wzdłuż tej krawędzi stołu” (druga uwaga o kierunku zwoju, pierwsza 15.11) — zwój leżał ukosem do wszystkich krawędzi blatu; leży teraz równolegle do tylnej krawędzi, tuż przy niej. Podłużny rekwizyt na stole kładzie się równolegle do krawędzi narysowanego blatu (kąt mierzy się na klatce, bo wycinek ma własne pochylenie), a uwagę reżysera czyta się z markera razem z obrysem, zanim się poprawi „na oko” | 1.6, 3.4 |
| Pierwszy cesarz EN (16.11, reżyser, markery w 26, 27, 29) | „usuń to z początku” — zwinięty zwój stał na stole w pierwszej klatce ujęcia ze sztyletem, choć ujęcie go nie używało; „daj tu zwój z poprzedniego ujęcia”, „zwój z poprzedniego ujęcia ma tu leżeć” — rozwinięta mapa znikała ze stołu zaraz po ujęciu, w którym zjechała; leży teraz na stole przez cały zamach (27–31, to samo miejsce, rozmiar i obrót) | 1.6, 1.2 |
| Pierwszy cesarz EN (16.11, reżyser, markery w 63, 64, 74) | „przesuń chorągiew w lewo, aby było widać cały ten budynek, a budynek wyśrodkuj pomiędzy chorągwiami”, „jeśli są kolejne ujęcia z tym, to to samo” — chorągiew ze smokiem zasłaniała pałac; chorągwie stoją teraz symetrycznie po bokach pałacu we wszystkich ujęciach z pałacem (63–75), liczone z kamery ujęcia (`swiat.smoki_przy_palacu`) | 1.6 (poprawka we wszystkich ujęciach z tą dekoracją), 1.5 |
| Pierwszy cesarz EN (16.11, reżyser, marker w 60) | „podnieś trochę ten kielich” — czarka z rtęcią była do połowy schowana za krawędzią rampy | 1.6, 1.5 |
| Pierwszy cesarz EN (16.11, reżyser, marker w 62) | „to po angielsku” — napis na meteorycie był po chińsku (始皇帝死而地分), a lektor mówi, co na nim wyryto; teraz „The Emperor will die, the land will split” (PL „Cesarz umrze, a ziemia się podzieli”) | 1.13 (nowa) |
| Pierwszy cesarz EN (16.11, reżyser, markery w 56) | „postaw go tutaj” — cesarz nie stał na wieku skrzyni drugiego powozu; stoi teraz na wieku i na nim przewraca się na płask; „tabliczka aw!...” — nad leżącym zjeżdża „AW!…” | 1.6, 1.11, 1.13 |
| Pierwszy cesarz EN (16.11, reżyser, markery w 58, 71, 77) | reżyser dopisał grę lalkom: olbrzymi „prężą muskuły” (ręce na zawiasach w barku i łokciu, każdy we własnej chwili), ryba „odskoczy do góry i wypadnie na ziemię” (spada z płachty powozu na drogę i trzepocze), nad chłopem „tabliczka o!”, a chłop „otrzep go z ziemi” (odkłada motykę, otrzepuje szmatką żołnierza, grudy odpadają, glina jaśnieje) — ujęcia miały za mało wydarzeń | 1.8, 1.11, 1.12 |
| Pierwszy cesarz EN (16.11, reżyser, markery w 72) | „niech ten list, spadając, walnie mu w głowę, i na 1 s stun”, „zabierz mu ten papier i pojaw sztylet w jego kierunku, i po chwili wbij go, i dźwięki konania” — druga uwaga o śmierci bez czynności (pierwsza 15.11, 1.11): Fusu tylko opadał za wzgórze; teraz list uderza go w głowę (gwiazdki przez sekundę), odlatuje mu z rąk, sztylet pojawia się ostrzem do niego i wbija się w pierś, Fusu kona (rzężenie, kaszel) i opada | 1.11, 1.12 |
| Pierwszy cesarz EN (16.11, kontrola przed wgraniem) | nowe zdarzenia dźwiękowe w ujęciach 26, 71, 72, 77 przesunęły wspólne losowanie szumu, więc przeliczenie zmieniało efekty w ujęciach 25–79 — plik nie trafił do Studio; teraz poprawione ujęcia losują nowe dźwięki osobno (`efekty.W_STUDIO`), a porównanie próbek z plikiem w Studio wskazało różnice tylko w 26, 71, 72 i 77, muzyka bit w bit ta sama | 1.12 |
| Miniaturka Pierwszego cesarza (16.11, reżyser) | z dwóch koncepcji wygrało zbliżenie; plan ogólny miał za drobne postacie; cesarz bez obrysu ginął na tle miasta; tabliczka „NO WAY?!” prosta i za wysoko | 5.1 |
| Miniaturka (16.11, znalezione w kontroli) | ostrze łopaty ucięte krawędzią arkusza wyglądało jak grot; grudy ziemi na żołnierzu jak dziury; szyld z tytułem EN dotykał krawędzi kadru; meteoryt nachodził na ostrze łopaty | 5.2 |
| Miniaturka (16.11, reżyser) | Fujifilm o sile 1,8 „za mocny”, 0,8 nadal za dużo → 0,5 i minimalne rozjaśnienie; spirale na oczach z białym tłem → grube czarne wprost na skórze | 5.1, 5.4 |

Otwarte: słuchawka w „Starym telefonie” nie ma kabla do aparatu, a po spadnięciu telefon dzwoni dalej (świadomie,
dla ciągłości z następnym ujęciem) — do decyzji reżysera.
