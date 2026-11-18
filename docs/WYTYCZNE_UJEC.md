# Wytyczne ujęć — jak budować kadr, żeby reżyser nie musiał poprawiać rysunku

Obowiązuje każdego, kto tworzy albo poprawia ujęcia: Claude, inne agenty i skrypty renderu (`output/*/render*.py`),
sceny Stage w Studio i obrazy generowane do ujęć. Reżyser ocenia **grę, rytm i nastrój** — nie powinien wyłapywać
błędów rysunku. Każdy punkt poniżej wziął się z prawdziwej poprawki (sekcja 6 „Skąd te zasady”): z uwag reżysera
w ujęciach, z markerów na klatkach i z rozmów przy pracy.

**Wzorce do powielania.** Teatr papierowy: „Pierwszy cesarz” EN (projekt `prj_65a9a00a6f9d402c`, 80 ujęć, 11:18,
zatwierdzony przez reżysera 16.11.2026 po trzech turach markerów, render końcowy 17.11). Kreskówka 2D: „Oddział C”
0:00–0:53 (poprawione przez reżysera 3.11, wzorzec dla dni 2–30). Nowy film tej samej techniki zaczyna się od silnika
i sposobu pracy wzorca, nie od zera; scenerię i obsadę rysuje się nowe (Podręcznik, „Animacja rysowana kodem”).

Spis: 0 przepis na ujęcie · 1 zasady kadru · 2 obrazy generowane · 3 kontrola przed oddaniem · 4 praca w Studio
i uwagi reżysera · 5 miniaturka · 6 skąd te zasady.

## 0. Przepis na ujęcie — od wiersza rozpiski do Studio

Każde ujęcie powstaje w tej samej kolejności. Pominięty krok to zwykle marker reżysera dzień później.

1. **Wiersz rozpiski** (`docs/filmy/<film>/ujecia/dane.py`): klucz, kadr (TYT karta, PO plan ogólny, PP plan pełny,
   PŚ plan średni, Z zbliżenie, D detal), ruch kamery, **opis**, dźwięk i kwestia. Opis to scenariusz ujęcia: kto jest
   na scenie, skąd wchodzi, co robi i w jakiej kolejności, co zostaje na końcu („pada niebieska chorągiew Zhao; pod
   bramą stoi mały chłopiec, a na niego spada z góry duża lalka króla”). Opis bez czasownika („sala nocą”, „puste
   morze”) znaczy, że ujęcie nie ma wydarzenia — reżyser to wyłapie (Rytm 1).
2. **Stan świata na wejściu**: co już stoi na scenie (dekoracje i rekwizyty z poprzednich ujęć tej sceny), kto jest,
   kto co trzyma, w jakim jest stanie (żywy, chory, w koronie, oblepiony ziemią). Stan liczy kod świata z kamieni
   milowych rozpiski (`swiat.stan`, `po("mur")`), a nie pamięć wykonawcy. Pierwsza klatka ujęcia = ostatnia klatka
   poprzedniego ujęcia tej sceny minus to, co cięcie świadomie zmienia (1.2, 1.6).
3. **Obsada i rekwizyty**: kogo i co widać, zgodnie z opisem i kwestią — kogo lektor wymienia, ten jest w kadrze, nikogo
   ponad to. Nowa postać dostaje podpis (1.15); każda postać ma własną sylwetkę, strój i stałą skalę (1.6, 1.24).
4. **Oś czasu ujęcia**: wypisz zdarzenia z sekundami od początku ujęcia — wejście, zdarzenie główne, reakcja, skutek,
   wyjście — i ułóż je pod kwestią: to, o czym mówi lektor, dzieje się, kiedy o tym mówi, albo tuż po (1.11). Każde
   zdarzenie ma przyczynę, fazy i dźwięk (1.12, 1.21). Dłuższe ujęcie ma drugie wydarzenie albo ruch w tle (1.8).
   Czasy zdarzeń trzymaj w nazwanych stałych, z których korzysta i rysunek, i dźwięk (`QIN_TAB` w ujęciu =
   wpis w `efekty.ZDARZENIA`).
5. **Długość**: z kwestii (oddech przed + mowa + pauza po, Rytm 2), a gdy akcja trwa dłużej — z akcji: wzrost dekoracji,
   przemarsz wojska i upadek dostają czas po kwestii, żeby się skończyły i chwilę postały (1.8, 1.18, `dane.WYDLUZ`).
6. **Kamera i głębia**: plan wzorcowy, ruch (jazda bokiem z paralaksą, dojazd do zdarzenia, odjazd, kiedy liczy się
   potęga), kolejność planów — co gra przed czym (1.3, 1.5, 1.17). Teatr papierowy: w pionie kamera się pochyla, nie
   jedzie (`trucky=0`), a zdarzenie stoi nad paskiem napisu.
7. **Życie i znaki**: ruch w tle (chorągiew, fale, kołysanie zawieszek, mruganie), tłum z własnymi opóźnieniami (1.7);
   gagi i napisy ze słownika znaków, w języku wersji filmu (1.13, 1.20).
8. **Dźwięk**: każde zdarzenie z osi czasu ma wpis w `efekty.ZDARZENIA` w tej samej sekundzie; głos człowieka
   z nagrania (1.12, 1.14).
9. **Kontrola** (sekcja 3), potem Studio (sekcja 4). W docstringu funkcji ujęcia i w opisie z rozpiski zapisz, czego
   chciał reżyser (cytat z datą) — następna poprawka nie może tego cofnąć.

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
- Przy zmianie dekoracji wszystko, co nie należy do nowego miejsca, schodzi ze sceny w kadrze — zwija się, zapada pod
  ziemię, opada pod rampę albo odjeżdża w górę — zanim nowa dekoracja stanie; aktorzy wchodzą razem z ziemią, na której
  stoją. Kanał z wodą z jednej sceny zostawał w kolejnych dekoracjach i reżyser zaznaczył go w siedmiu ujęciach
  (15.11: „zaś ten kanał z wodą…”, „znowu wyrzuć ten kanał i wodę”), bo poprawiano go w ujęciach, a nie w stanie świata.
- Postać, która wychodzi za kadr, w następnym ujęciu wchodzi z tej samej strony (wyskok za górną krawędź → spadnięcie
  z góry do wozu, reżyser 16.11); nie „przeskakuje” na nowe miejsce przez cięcie.
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
- Ujęcie bez akcji nie istnieje: dłuższe ujęcie ma drugie wydarzenie albo wyraźny ruch w tle (reżyser 15.11: „na tym
  ujęciu niech się więcej dzieje”, „słońce wschodzi!”, „porusz turkusową chorągwią”). W czasie dodanym przez
  wydłużenie coś się dzieje — wzrost, ruch w tę i z powrotem, reakcja — a nie stopklatka.
- „Za krótko” to najczęstsza uwaga reżysera o rytmie: w „Pierwszym cesarzu” wydłużył 23 z 80 ujęć, prawie wszystkie
  z budową, wojskiem, tłumem albo podróżą (o 0,7–5 s, najczęściej o 2–3 s; `dane.WYDLUZ`). Zanim oddasz ujęcie, sprawdź na klatce końcowej,
  czy wydarzenie się skończyło i czy widz zdążył je zobaczyć w całości.
- Reżyser podaje chwile wprost („po 2 s słuchawka spada”, „zombie po 2 s podnoszą ręce”, „po 1,5 s szybkie zbliżenie
  25%”) — taka liczba to sekunda od początku ujęcia na osi czasu (0.4).

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

### 1.14 Głos człowieka z nagrania, nie z szumu
Kaszel, jęk, rzężenie, okrzyk czy westchnienie postaci to dźwięk z nagrania głosu (model mowy ze znacznikiem — Chatterbox
Turbo `[cough]`, `[groan]`, `[gasp]` — albo prawdziwe nagranie), a nie synteza szumu przez filtry. Szum z formantami
brzmi jak tłuczone naczynie, nie jak człowiek („Pierwszy cesarz”: `kaszel.py` → `dzwiek_probki/`, `efekty.cough`).
Przy podmianie zsyntezowanego dźwięku na próbkę stara synteza liczy się dalej i jest wyrzucana, żeby losowania reszty
ścieżki efektów zostały te same (1.12).

### 1.15 Widz wie, kto jest kim
- Postać, która pojawia się pierwszy raz, dostaje **podpis**: tabliczka z imieniem i rolą zjeżdża nad nią na nitce na
  ok. 2–3 s i odjeżdża w górę, kiedy postać jest już cała widoczna (`swiat.podpis(w, t, "kupiec Lü Buwei", x, y, t0)`;
  reżyser 15.11: „za 1. razem zrzuć nad nim na chwilę tabliczki, kto kim jest, jak się pierwszy raz pojawiają”).
  Podpis jest w języku wersji (1.13) i nie wisi nad kimś, o kim lektor właśnie nie mówi.
- Kwestia mówi jednoznacznie, o kim jest: „ojciec Zhenga”, a nie „ojciec” (reżyser 15.11: „mówi, że father is dead,
  ale kogo father?”).
- Jedna postać = jedna lalka przez cały film; zmiana wieku albo godności to inna wersja tej samej lalki (chłopiec →
  chłopiec w koronie → dorosły), a zmianę widać w kadrze (mała lalka chowa się, duża wysuwa się na jej miejsce).
- Skala lalek jest stała i wspólna; postać większa od innych tylko wtedy, gdy historia to mówi, i z podpisem
  (reżyser 15.11 o eunuchu: „kto to jest i czemu on jest taki ogromny?”).

### 1.16 Lalka patrzy tam, dokąd idzie
- Zwrot lalki (`flip`) to kierunek ruchu. Kiedy zawraca, najpierw się obraca (odbicie lustrzane, bokiem widać grubość
  tektury), potem rusza (reżyser 15.11: „jak idzie w lewo, to odbicie lustrzane go w lewo”).
- Gest kierunku pokazuje się obrotem: „wskazuje wschód” = lalka obraca się w lewo, a po chwili w prawo (reżyser 15.11).
- Chód przesuwa postać po ziemi; podskakiwanie w miejscu albo przesuwanie bez kroku to błąd (pilot 29.10: „potem on
  ciągle skacze w miejscu”).
- Ruch w tę i z powrotem ożywia dłuższe ujęcie: dżonki płyną zakosami, cesarz chodzi po sali (reżyser 15.11: „niech
  oni sobie pływają lewo, prawo, lewo, prawo”).

### 1.17 Potęga to liczba i przestrzeń
Wojsko, tłum, państwo, budowę i bogactwo pokazuje się ilością i rozmachem. Reżyser za każdym razem prosił o więcej
(15.11: „więcej chorągwi”, „jeszcze więcej włóczni”, „dużo dużo więcej tych wozów”, „zwiększ liczbę tych ludków”,
„pokaż więcej tych clay soldiers”, „pokazać jeszcze większy obszar i oddalić kamerę, pokazując potęgę”).
- Rzędy jeden za drugim aż po horyzont, dziesiątki postaci zamiast trzech, każda z własnym opóźnieniem (1.7); wozy na
  dwóch drogach, szybsze mijają wolniejsze; robotnicy suną po całym zboczu.
- Kamera odjeżdża, aż widać cały kraj (do ramy teatru), zamiast stać na planie średnim.
- Wspólny gest wojska idzie w rytmie: wszystkie włócznie unoszą się na 0,6 s trzy razy; po salwie strzał zaraz druga.
- Przemarsz jest szybki („szybciej niech przesuwają się”), a upadek potęgi tak samo liczny: chorągwie padają po kolei,
  płonie coraz więcej (1.23).

### 1.18 Rzecz, która wyrasta, widać od początku do końca
Teatr składa się na oczach widza (reżyser 10.11: „wcześniej te elementy na tym tle tak się stawiały”).
- Dekoracja wyrasta wtedy, kiedy kamera na nią patrzy: najpierw kamera dojeżdża, potem rzecz rośnie (stela, reżyser
  15.11: „wysuń ją w poprawnym momencie zbliżenia”) — nie poza kadrem i nie przed dojazdem.
- Przy wyrastaniu kołysze się i osiada, jakby wyrastała z ziemi („niech się kołysze, jakby wyrastała z ziemi”), a nie
  wyjeżdża sztywno (`back`, `settle` w silniku).
- Ujęcie trwa, aż wzrost się skończy, i jeszcze chwilę stoi (reżyser 15.11: „wydłuż to ujęcie i ukaż bardziej
  wyrastające mury”). W „Pierwszym cesarzu” mur, robotnicy, armia, prowincje i rody dostały po 3–5 s więcej
  (`dane.WYDLUZ`).
- To, co zbudowano, stoi w następnych ujęciach tej sceny („niech ta wieża z poprzedniego ujęcia tu będzie już do
  końca”), a znika tylko w wydarzeniu: zapada się, płonie, zwija się przy zmianie dekoracji (1.2).
- Temat ujęcia jest duży. Reżyser powiększał go za każdym razem: „zrób ją większą” (stela), „troszkę większy ten
  posąg”, „pokaż, jak wyrasta ta wyspa, i zrób większą”, „powiększ te koła”.

### 1.19 To, o czym mówi lektor, rozpoznaje się od razu
- Rzecz ma wygląd, po którym widz ją pozna bez lektora: kanał = woda między nasypami, zielone poletka wzdłuż i łódź
  z ziarnem, a nie cienka niebieska kreska (reżyser 15.11: „wyraźniej to pokaż, bo nie wiadomo, o co chodzi”); droga =
  trakt z koleinami i wóz z dużymi kołami; ujednolicenie miar = miarka, miara objętości i waga z odważnikiem, a nie
  zwoje i monety („pokaż miarkę jakąś”); podział na 36 prowincji = mapa kraju, na której układa się 36 części w
  miejscach jak naprawdę („tak jak naprawdę były”).
- Mapy, liczby, stroje i budowle są zgodne ze źródłami filmu (decyzje w księdze świata).
- Ujęcie bez słów pokazuje tylko to, co widz zrozumie sam. Jeśli obraz potrzebuje wyjaśnienia, mówi o nim lektor
  (ogień sygnałowy, reżyser 16.11: „opisz w narracji, co oznacza ten ogień sygnałowy”; Rytm 4).

### 1.20 Słownik znaków teatru papierowego
Reżyser opowiada gagami i znakami jak z komiksu. Znak znaczy w każdym filmie to samo, ma swój dźwięk w tej samej chwili
(1.12) i napis w języku wersji (1.13).

| Znak | Znaczy | Jak („Pierwszy cesarz”) |
|---|---|---|
| tabliczka z imieniem i rolą nad postacią | pierwsze pojawienie się (1.15) | `swiat.podpis`, ok. 2–3 s |
| zawieszka z rokiem albo „trzy miesiące później” | czas akcji | `Z.tag` + `Z.hang` (zjazd na nitce z kołysaniem) |
| tabliczka z okrzykiem: „AŁA!…”/„AW!…”, „O!”, „ZABIĆ KRÓLA!” | reakcja, zamiar, zaskoczenie | `podpis` z krótkim tekstem |
| tabliczka odrzucona, zjeżdża większa („KRÓL” → „PIERWSZY CESARZ”, „Qin” wylatuje, „China” na środek) | zmiana tytułu albo nazwy | `s_cesarz`, `s_qin` |
| X na oczach | śmierć | `w.oczy_x`, jedzie z głową lalki |
| czerwony X migający 2× nad postacią, z dźwiękiem | wyrok, egzekucja | `ujecia1.iks` (0,3 s widać, 0,18 s nie) |
| gwiazdki albo rzecz krążąca nad głową ok. 1 s, lalka się chwieje | zamroczenie po uderzeniu („stun”) | `Z.prop("gwiazdka")`, `s_list`, `s_lekarz` |
| biała flaga, która powiewa | kapitulacja | `Z.prop("flaga_biala")`, `s_qi` |
| zgięcie i kaszel z nagrania | choroba | `s_podroz`, 1.14 |
| kaszel, chwianie, X na oczach, opadanie pod rampę, rzężenie | konanie | `s_koniec`, `s_list` |
| spirale na oczach | oszołomienie (miniaturka) | 5.1 |

Nowy znak, który reżyser wymyśli, dopisz do tej tabeli razem z funkcją, która go rysuje.

### 1.21 Akcja ma fazy, a gag ma takt
- Atak, cios i rzut: zamach → uderzenie → skutek, każdy w swojej chwili i z dźwiękiem. Podejście może iść pchnięciami
  (80% drogi → 100% → 80% → 100%, `s_lekarz`); broń, która ma dobić, najpierw koziołkuje w powietrzu, potem spada
  (`s_pretekst`); broń pojawia się ostrzem do celu i po chwili się wbija (`s_list`). Pościg i bijatyka biorą całą scenę
  („biegaj bardziej po tym pokoju”).
- Gag ma dwa takty: najpierw widz widzi stan (mały chłopiec pod bramą), potem zmiana go zakrywa (spada na niego duży
  król, `s_zhao`). Wyskok za kadr w jednym ujęciu → spadnięcie z góry kadru w następnym (`s_sam` → `s_powrot`).
- Postacie przy wydarzeniu reagują (chłopi odskakują, urzędnicy się podnoszą), a drobny szczegół gry jest konkretny
  (marker 3.11: „płacze z jednego oka”, „ten ostatni też się zatrzymuje na chwilkę”).
- Czynność, która w rysunku wychodzi brzydko, upraszcza się do czystej: rozwijanie zwoju po stole wyglądało „ohydnie”,
  więc rozwinięta mapa zjeżdża na nitkach gotowa (reżyser 15.11: „po prostu połóż na nowo rozwinięty zwój”). Lepiej
  prosto i czysto niż ambitnie i krzywo.

### 1.22 Rzecz z części rusza się częściami, a to, co w środku, zostaje w środku
- Mechanizm ma zawiasy tam, gdzie prawdziwy: waga — podstawa stoi, belka kołysze się wokół osi, każda szala buja się
  osobno (`swiat.waga`; reżyser 15.11: „to ma stać nieruchomo”, „porusz osobno jednym odważnikiem”); ręce lalek mają
  zawias w barku i łokciu, a każda postać rusza nimi we własnej chwili (cyklopi „prężą muskuły”); pisarz kiwa głową
  nad pędzlem, a pisanie ma dźwięk.
- To, co wpada do naczynia (kulki rtęci, trucizna), znika za jego przednim brzegiem i nie wychodzi poza obrys (reżyser
  15.11: „kulki wychodzą poza wazę”) — jak przy otworze (1.1). Strumień wypływa z brzegu naczynia i kończy się
  w ustach; początek i koniec mierzy się na klatce.
- Nitka jest tylko przy tym, co teatr spuszcza z góry (zawieszka, księżyc, mapa, kielich); krople, kulki i drobiazgi
  spadają bez nitek („usuń te linie”).
- Drobne rzeczy w ruchu idą tak wolno, żeby widz zdążył je zobaczyć („te srebrne kulki niech dużo wolniej zjeżdżają”).

### 1.23 Kulminacja jest mocna
- Uderzenie, wybuch i upadek mają wyraźną siłę: mocny wstrząs kamery, duży płomień (meteoryt, reżyser 15.11: „bardziej
  zatrzęś kamerą i większy płomień meteorytu”), drżenie budowli („zrób shaking tej tomb”).
- Pożar i zniszczenie rosną do końca ujęcia („spal ją bardziej na końcu”), a nie stoją na jednym poziomie.

### 1.24 Szczegół w skali planu
- Oczy, usta i kreska twarzy w planie ogólnym są proporcjonalnie małe; duże oczy działają tylko w zbliżeniu (reżyser
  4.11: „popraw te oczy, jak są ujęcia z daleka, bo one są za duże”).
- Postać w otworze ma skalę otworu: w okienku widać ją od ramion w górę, a nie całą, małą jak mrówka, wiszącą
  w powietrzu (pilot 29.10). Postać w lokacji ma skalę sąsiadów; olbrzym tylko z powodu fabuły (1.15).

### 1.25 Każdy w kadrze gra, a każda rzecz jest tam, gdzie trzeba
- Co ma pracować, pracuje u wszystkich: każda łódź wiosłuje we własnym rytmie, nie tylko łódź bohatera (reżyser 18.11:
  „każda łódź ma wiosłować”).
- Na mocnej chwili postać reaguje gestem i okrzykiem ze słownika znaków (1.20): ścięta głowa woła „HELP!”, tonący
  „AAAA!”, brat „BROTHER!”, umierający „I can't…”, osamotniony bohater podnosi ręce, wódz „NO WAY!”, straż „STOP!” z ręką
  w górze, niedźwiedź „BOO!”. Radość widać ruchem (brat podskakuje), zamiar czynem (zamiast wskazać góry — strzela w nie).
- Rekwizyt, który postać bierze, trafia do jej dłoni; nie wisi obok ręki (miecz Ninigiego). Rzecz, o której mówi
  kwestia albo gest (słońce, na które wskazuje Itsuse), jest w kadrze cała i żyje, a nie ucięta krawędzią.
- Zwrot postaci zaczyna się od przeciwnego kierunku, żeby był widoczny (Iwarebiko najpierw patrzy w lewo, potem
  zwraca się ku słońcu). Ujęcie przejścia albo przybycia ma końcówkę „już na miejscu” (Ninigi stoi na szczycie, wojsko
  wchodzi w las) — 1.18.

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
   - **Obsada i rekwizyty**: na pierwszej, środkowej i ostatniej klatce wypisz, kogo i co widać, i porównaj z opisem
     ujęcia, kwestią i poprzednim ujęciem tej sceny — nic nie zostało z poprzedniej dekoracji, nikogo nie brakuje,
     rzecz leży tam, gdzie leżała, nowa postać ma podpis (reżyser 14.11: „sprawdź, czy na każdym ujęciu są właściwe
     osoby i rekwizyty według scenariusza”).
   - **Dźwięk**: przy opisie ujęcia przejdź listę `efekty.ZDARZENIA` — każde zdarzenie z osi czasu (0.4) ma swój
     dźwięk w tej samej sekundzie; wysuwanie lalek, opadanie płacht i gesty też.
   - **Wydarzenie się kończy**: na ostatniej klatce wzrost, przemarsz albo upadek jest skończony i stoi chwilę (1.18).
2. **Skrajne położenia**: przy każdym otworze obejrzyj klatkę, w której ruchoma rzecz jest najbliżej krawędzi otworu.
3. **Automatycznie**: `python3 scripts/kontrola_ujec.py output/<film>/render.py` — szuka pustych krawędzi kadru
   (koniec świata), gasnących jasnych elementów i robi arkusz klatek do obejrzenia. W ciemnych ujęciach z winietą
   „pusta krawędź” bywa fałszywa — rozstrzyga test płótna w kolorze magenta (nienarysowane miejsce świeci na różowo).
   Po poprawkach porównaj render z materiałem w Studio na **tych samych numerach klatek** i wgraj tylko zmienione ujęcia
   (`studio_dzien.py <dzień> <projekt> tylko=…`).
4. **Przejrzyj uwagi**: wszystkie uwagi reżysera w ujęciach i markery na klatkach z tego filmu muszą mieć odpowiedź w
   obrazie. Marker ma klatkę osi Studio (30 kl./s), render ma 24 kl./s — przeliczaj przez sekundy. Listę do pracy daje
   `python3 scripts/uwagi_rezysera.py <projekt> [--od RRRR-MM-DD] [--md plik.md]`: numer ujęcia, sekunda, klatka renderu,
   kreski w pikselach ekranu i podpowiedzi; jak czytać uwagi — 4.2. Po poprawce rzeczy wspólnej obejrzyj wszystkie
   ujęcia, w których ta rzecz stoi (1.6), nie tylko to z markerem.
5. Napisz reżyserowi wprost, co sprawdzono i czego nie — przy każdym markerze: zrobione albo pytanie.

## 4. Praca w Studio i uwagi reżysera

### 4.1 Zapis w Studio

- Poprawki robi się w ujęciach (Sceny → ujęcia) i na osi montażu; **bez eksportu**, dopóki reżyser nie poprosi.
- Skrypty filmów mają tryb `update` (np. `python3 output/zombie-psychiatryk/studio_import.py update <projekt>`):
  renderuje same ujęcia, podmienia materiał i przesuwa obraz, lektora i efekty na osi.
- Kolejność zapisu: najpierw oś montażu (nowy materiał razem z nową długością), potem ujęcia — inaczej serwer odrzuci
  klip dłuższy od starego pliku. Przesunięcie klipu na osi przesuwa też jego ujęcie — ujęć dalszych dni nie zapisuje
  się potem drugi raz (podwójne przesunięcie, a przy wczesnym dniu ponad 200 operacji i odmowa serwera; 6.11.2026).
  Zmiana samych kwestii albo długości: `docs/filmy/oddzial-c/ujecia/podmien_w_miejscu.py` — bez kasowania ujęć.
- Plik ujęcia ma pokryć całą długość ujęcia na osi (zaokrąglaj liczbę klatek renderu w górę).
- Nie usuwaj uwag ani markerów reżysera — to jego notatki.

### 4.2 Uwagi i markery reżysera — jak je czytać

Reżyser pisze krótko, w trakcie oglądania, często bez polskich znaków i z angielskimi słowami z wersji EN. Każda uwaga
to polecenie z jednym właściwym odczytaniem — poniżej, jak je odczytywaliśmy, kiedy reżyser przyjmował poprawkę.

**Gdzie są.** Uwaga w ujęciu: pole „Uwagi reżysera” (w pliku projektu `scenes[].director_notes`; w filmach z rozpiski
pierwszy wiersz bywa opisem z rozpiski — „Kadr: … Beat: …”, „Typ: …” — a uwaga reżysera to dalsze wiersze). Marker:
kreska z podpisem na klatce (`frame_annotations`: ujęcie, klatka osi 30 kl./s, tekst, kreski w ułamkach ekranu).
Wszystko naraz: `python3 scripts/uwagi_rezysera.py <projekt>` (tylko czyta plik projektu).

**Tekst.**
- Liczy się **ostatnia wersja**. Studio zapisuje uwagę w trakcie pisania, więc w historii projektu są urywki
  („wydłuż tą scenę, ale…”); późniejsza uwaga może zastąpić wcześniejszą („usuń te ujęcie” → po minucie „usuń ten
  statek i tego jednego cyklopa na środku, a tamci niech skaczą” — ujęcie zostało).
- Kilka markerów w jednym ujęciu czyta się razem, w kolejności klatek: razem opisują jedną poprawkę ujęcia.
- **Odwołania** — „to samo”, „jak poprzednio”, „jak w poprzednim ujęciu”, „zaś”, „znowu”, „i w następnych też”, „jeśli
  są kolejne ujęcia z tym, to to samo” — to ten sam błąd co w innym markerze. Poprawia się go raz, we wspólnym kodzie
  (stan świata, funkcja sceny), i sprawdza we wszystkich ujęciach z tą rzeczą (1.6). Reżyser zaznaczył kanał z wodą
  w siedmiu ujęciach, bo poprawki szły punktowo.
- **Pytanie to zgłoszenie błędu**: „czemu to zostaje na początku ujęcia??”, „kto to jest i czemu on jest taki
  ogromny?”, „czemu na ujęciu 6 są trzy postacie?”. Popraw i w podsumowaniu odpowiedz, skąd się wziął błąd. Jeśli
  stan jest zamierzony (wynika ze scenariusza), wyjaśnij to i zapytaj, zanim zmienisz.

**Kreska.**
- Obrys pokazuje rzecz, o którą chodzi; „tu”, „tutaj”, „stąd”, „postaw go tutaj” — miejsce kreski; „w tym kierunku”,
  „w kierunku, który narysowałem” — kierunek kreski od pierwszego do ostatniego punktu (sztylet, zwój); dwie kreski —
  dwa miejsca (np. skąd i dokąd).
- Kreska leży w kadrze **ekranu na tej klatce**, z ruchem kamery, a nie w kadrze wzorcowym: punkt przelicza się przez
  kamerę ujęcia w tej chwili. Przed poprawką obejrzyj klatkę markera razem z jego kreską — zwój poprawiany „na oko”
  dostał drugą uwagę o tym samym (16.11).
- Marker trzyma się klatki ujęcia z dnia, w którym go narysowano. Jeśli ujęcie potem się wydłużyło albo zmieniło, czas
  markera wskazuje miejsce w tamtej wersji — szukaj zdarzenia, a nie samej sekundy.

**Słowa reżysera** (jak je wykonywaliśmy i zostały przyjęte):

| Reżyser pisze | Znaczy |
|---|---|
| „wydłuż” (bez liczby) | obraz trwa dłużej, aż wydarzenie się skończy i chwilę postoi — w „Pierwszym cesarzu” najczęściej o 2–3 s, ujęcia widowiskowe o 3–5 s (`dane.WYDLUZ`); w dodanym czasie coś się dzieje (1.8) |
| „wydłuż o 4 s”, „do 8/9 s”, „wydłuż 3×” | liczba z uwagi: o tyle albo do tylu (całe ujęcie z pauzą po kwestii); „3×” — trzy razy dłuższy przejazd albo ujęcie |
| „usuń”, „wyrzuć”, „wyjeb” | rzecz znika z tego ujęcia i z każdego, w którym nie gra; jeśli gra później, pojawia się dopiero tam i wchodzi skądś („usuń ten zwój ze stołu, bo on będzie w następnym dopiero”) |
| „schowaj”, „skryj” | za ramą, falą, rampą albo bliższym planem (1.1, 1.5) — nie zniknięcie |
| „pojaw”, „wysuń”, „niech wyskoczy” | wejście ze słownika teatru: zza rampy, z nitki z góry, zza wzgórza, ze środka rzeczy (sztylet ze środka mapy) — nigdy mignięcie znikąd (1.2) |
| „postaw go tu”, „ustaw tutaj” | lalka stoi w miejscu kreski i jest tam cała widoczna (na wieku skrzyni, przy wozie) |
| „tabliczka …” | zawieszka z tym napisem nad postacią, w języku wersji (1.20, 1.13) |
| „stun”, „kołuje mu się nad głową” | zamroczenie ok. 1 s (1.20) |
| „X”, „Xy na oczach” | czerwony X migający 2× z dźwiękiem (wyrok) albo X na oczach (śmierć) (1.20) |
| „*cough*”, „dźwięki konania”, „z dźwiękiem” | zdarzenie dźwiękowe w tej samej chwili, głos z nagrania (1.12, 1.14) |
| „więcej”, „szybciej”, „większy” | wyraźnie, nie o jeden: rzędy i dziesiątki, temat ujęcia większy od reszty (1.17, 1.18) |
| „minimalnie”, „troszkę”, „lekko” | mała zmiana tego jednego parametru (kilka pikseli kadru wzorcowego, kilka stopni); reszta ujęcia bez zmian |
| „opisz w narracji”, „dograj narrację” | zmiana od góry: kwestia w rozpisce i w tłumaczeniu, nagranie lektora (za zgodą reżysera), długość ujęcia, dopiero potem obraz (CLAUDE.md) |
| angielskie słowa: poison, coin, clay soldiers, tomb | rzecz z filmu w wersji EN — chodzi o tę rzecz w kadrze, nie o napis |

**Kiedy nie wiadomo.** Jeśli tekst i kreska dają dwie różne poprawki, zapytaj reżysera jednym pytaniem z obiema
możliwościami, zanim narysujesz; zgadnięta poprawka wraca jako druga uwaga.

**Po wykonaniu.** Marker zostaje w Studio. Reżyser dostaje odpowiedź przy każdym markerze (zrobione albo pytanie).
Wymaganie reżysera trafia do docstringu funkcji ujęcia i do opisu w rozpisce (cytat z datą), żeby następna zmiana go
nie cofnęła. Nowy błąd — wiersz w tabeli „Skąd te zasady”; nowa klasa błędu — nowa zasada w sekcji 1.

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

## 6. Skąd te zasady

Od pilota (29.10.2026) i „Oddziału C” (3.11) do „Pierwszego cesarza” EN (16.11); wiersze w kolejności dat. Źródła:
uwagi w ujęciach i markery na klatkach w Studio (`scripts/uwagi_rezysera.py`), rozmowy z reżyserem przy pracy
i błędy znalezione w kontroli.

| Ujęcie | Błąd | Zasada |
|---|---|---|
| Pilot survival (29.10, reżyser) | postać pukająca w szybę była w oknie cała, „mała jak mrówka” i „lewituje w oknie”, zamiast być widoczna od ramion w górę; Leo w scenie 6 „tak wielki”; w scenie 5 Leo „ciągle skacze w miejscu” | 1.24, 1.16 |
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
| Oddział C, ujęcia 01–12 (3.11, uwagi w ujęciach i markery) | reżyser podawał chwile zdarzeń w sekundach ujęcia — „po 2 s ujęcia słuchawka spada na stół”, „zombie po 2 s podnoszą ręce do góry”, „po 1,5 s zbliżenie 25% szybkie” — i dopisywał drobną grę: „płacze z jednego oka”, „ten ostatni też się zatrzymuje na chwilkę” | 0.4, 1.8, 1.21 |
| Wariant A, dni 1–30 (4.11) | wszystkie ujęcia ~4 s i każdy dzień po 66 s — film „jak wolny film”; potem równe 2,5 s bez względu na kwestie | 1.9 |
| Wariant A, dzień 1 (4.11) | ręka nie przy tułowiu, but jak deska, framuga znika, postacie przechodzą przez kratę, stopy obok stopni | 1.1, 1.2, 1.4, 1.5 |
| Wariant A, dzień 5/07 Kołnierz (4.11) | zbliżenie z głową wysoko: tułów urywał się w połowie kadru jak pływający prostokąt (znalezione w kontroli; `face_cu` ciągnie teraz tułów poza dolną krawędź) | 1.3, 1.4 |
| Wariant A, dni 2–5 (4.11, reżyser) | „popraw te oczy, jak są ujęcia z daleka, bo one są za duże; jak są sceny z bliska, jest ok” — oczy w skali zbliżenia także w planach ogólnych | 1.24 |
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
| Syn słońca (17.11, przegląd według przepisu i zasad 1.15–1.24, znalezione w kontroli) | film zrobiony przed tymi zasadami: żadna postać nie miała tabliczki z imieniem; Izanami, Itsuse, Nagasunehiko i cesarz znikali bez śmierci (bez X, bez ciosu); lektor mówił o synu, którego nie było w kadrze; „flota” to jedna łódź, w Naniwie dwie lalki zamiast łodzi i wojska, w lesie Kumano same włócznie bez ludzi; śmiech bogów z syntezy szumu; pisarz kroniki schowany za stołem; cesarz z 2019 roku nieobecny na własnej koronacji; brak kurtyny między aktami; napisy tylko po polsku. Poprawione we wszystkich ujęciach z tą rzeczą (dwa rzędy wojowników w Kumano: padanie, Takakuraji, przebudzenie; syn także w ujęciu „pusto”) | 1.6, 1.11, 1.13, 1.14, 1.15, 1.17, 1.20, 1.21, Rytm 7 |
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
| Pierwszy cesarz EN (15.11, reżyser, uwagi przy 49–76) | ujęcia widowiskowe kończyły się przed końcem wydarzenia: „wydłuż to ujęcie i ukaż bardziej wyrastające mury”, „dłużej niech trwa to ujęcie”, „wydłuż scenę końcową”, „niech oni sobie pływają lewo, prawo”, „niech chodzi prawo, lewo, ale jak idzie w lewo, to odbicie lustrzane”, „wydłuż 3× … niech przesuwa się po tych twarzach” | 1.8, 1.16, 1.18 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 14, 54, 69) | wyrok i śmierć nie miały znaku: „zrób czerwony X na nim migoczący 2 razy z dźwiękiem”, „każdego rób X migający 2×”, „zrób mu Xy na oczach” | 1.20 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 24, 36, 39; rozmowa) | „tabliczka nad nim KILL THE KING!”, „niech wyciąga białą flagę i niech powiewa”, „zjeżdża tabliczka KING”, „wyrzuca tabliczkę KING i wjeżdża jeszcze większa FIRST EMPEROR”; „za 1. razem zrzuć nad nim na chwilę tabliczki, kto kim jest”; „mówi, że father is dead, ale kogo father?” | 1.15, 1.20 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 18, 19, 34–36, 38, 40, 43, 64, 78) | wojsko, państwo i budowa za skromne: „jeszcze więcej chorągwi i szybciej niech przesuwają się”, „pokazać jeszcze większy obszar … pokazując potęgę”, „jeszcze więcej włóczni”, „dużo dużo więcej tych wozów … mijając się”, „zwiększ liczbę tych ludków”, „pokaż więcej tych clay soldiers”; włócznie trzy razy w górę, druga salwa strzał | 1.17 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 40, 41, 44, 57, 64) | temat ujęcia za mały albo wyrastał nie w porę: „troszkę większy ten posąg”, „powiększ te koła”, stela „zrób ją większą i wysuń ją w poprawnym momencie zbliżenia, i niech się kołysze”, „pokaż, jak wyrasta ta wyspa, i zrób większą”; „niech ta wieża z poprzedniego ujęcia tu będzie już do końca” | 1.18 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 20, 41, 42, 48) | rzecz z kwestii była nie do poznania: kanał jako kreska („nie wiadomo, o co chodzi”), droga („bardziej pokaż tę drogę”), mapa 36 prowincji „tak jak naprawdę były”, „usuń zwoje i pieniądze ze stołu i zamiast tego pokaż miarkę” | 1.19 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 21, 23, 28, 29, 31; rozmowa przy 26) | gra bez faz i taktów: „obróć go w lewo, a po chwili w prawo”, „pokaż na chwilę małego chłopca … i zaraz skryj go, jak spadnie na niego duży”, „biegaj bardziej po tym pokoju”, „80% → 100% → 80% → 100% … i mu się kołuje nad głową, jakby miał stuna”, „stąd miecz i wbij w serce … a ten jego sztylet niech od początku kołuje w powietrzu i przy końcu go dobija”; rozwijanie zwoju „wygląda ohydnie … po prostu połóż na nowo rozwinięty zwój” | 1.16, 1.21 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 46, 48, 60) | waga kołysała się cała („to ma stać nieruchomo”, „porusz osobno jednym odważnikiem … drugim”); pisarz nie pisał („porusz jego głową w dół”, „puść dźwięk pisania”); kulki rtęci wychodziły poza wazę, wisiały na nitkach i spadały za szybko („usuń te linie”, „niech dużo wolniej zjeżdżają”) | 1.22 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 24, 33; uwagi przy 62, 75, 78) | ujęcia z jednym wydarzeniem i słaba kulminacja: „na tym ujęciu niech się więcej dzieje”, „słońce wschodzi!”, „porusz turkusową chorągwią”; „bardziej zatrzęś kamerą i większy płomień meteorytu”, „spal ją bardziej na końcu”, „zrób shaking tej tomb” | 1.8, 1.23 |
| Pierwszy cesarz EN (15.11, reżyser, markery w 21, 41, 65, 68, 70, 77, 78) | jeden błąd w siedmiu markerach: kanał z wodą zostawał po zmianie dekoracji („czemu to zostaje na początku ujęcia??”, „zaś ta woda z tym kanałem”, „znowu wyrzuć ten kanał i wodę”) — poprawiano ujęcia, a nie stan świata, i nie czytano „zaś”/„znowu” jako odwołania | 1.2, 4.2 |
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
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, markery w 7 i 8) | „zrób, że wyskakuje do góry za kadr”, „zrób, że on z góry kadru wpada do tego powozu” — chłopiec cofał się pod bramę, a w następnym ujęciu siedział już na wozie; teraz przysiada, wybija się za górną krawędź kadru i w następnym ujęciu spada z góry do wozu (podskok na skrzyni, wóz się ugina) | 1.2, 1.8 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, markery w 15) | „ten poison trochę wyżej do jego ust”, „stąd ma się wylewać” — strumień trucizny wypływał z dolnego rogu przechylonego kielicha i kończył się na brodzie; wypływa z górnego brzegu i trafia w usta. Początek i koniec strumienia mierzy się na klatce (brzeg naczynia, usta), a nie z rysunku wycinka | 1.11 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, markery w 25 i 47) | „usuń ten zwój ze stołu, bo on będzie w następnym dopiero”, „usuń ten zwój i w następnych też” — zwinięta mapa stała na stole, zanim była potrzebna, a zwój na stole pisarzy nie grał w żadnym ujęciu; zwój zniknął ze stołu pisarzy we wszystkich ujęciach tej sceny (46–48), a księgi do ognia (52) przynosi teraz uczony w dłoniach, żeby nic nie wzięło się znikąd | 1.6, 1.2 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, uwaga przy 51) | „wydłuż tę scenę do 8/9 s, ale opisz w narracji, co oznacza ten ogień sygnałowy” — ujęcie bez słów pokazywało coś, czego widz nie rozumie; dograna kwestia lektora, ogień zapala się po kolei na trzech wieżach, a kamera idzie za ostrzeżeniem | Rytm 4 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, uwaga przy 59) | „usuń ten statek i tego jednego cyklopa na środku, a tamci niech skaczą od początku sceny”, potem „zrób, że te cyklopy wskakują do wody” — puste morze nie miało wydarzenia, a żagiel powtarzał koniec poprzedniego ujęcia; teraz dwaj cyklopi podskakują i jeden po drugim skaczą łukiem do morza, znikają za grzbietem fali z pluskiem kropel (chwila plusku liczona z kadru: stopy schodzą pod grzbiet fali), ujęcie 3,4 s, żeby zostało puste morze | Rytm 1, 1.8, 1.12 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, markery w 79) | tabliczki „Qin” i „China” zjeżdżają nad góry, „Qin” wylatuje, „China” jedzie na środek — obraz do kwestii o nazwie kraju; na końcu „THANK YOU for watching / Support me and I'll do my best.” jako osobne ujęcie 80 z dużymi tabliczkami i lektorem (bez paska napisu, bo tekst jest w kadrze) | 1.13 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser, uwaga przy 69) | „tam, gdzie cesarz kona, jest dźwięk tłuczenia, a nie kaszlenia” — druga uwaga o kaszlu (pierwsza 15.11: „lepszy dźwięk kaszlenia”); kaszel z syntezy szumu przez formanty zastąpiony nagraniem kaszlu (Chatterbox Turbo, `[cough]`) we wszystkich ujęciach z kaszlem | 1.14 (nowa), 1.12 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser) | „dodaj wszędzie, gdzie jest kurtyna, dźwięk zaciągania i rozciągania kurtyny” — kurtyna między aktami miała tylko cichy szum; teraz aksamit sunie, kółka stukają o drążek w tempie ruchu, połowy spotykają się z miękkim „fump” (zasuwanie) albo kółka szarpią na starcie (rozsuwanie); reżyser zatwierdził próbkę (fragment filmu na granicy aktów + sam dźwięk) przed złożeniem filmu: „może być” | Rytm 7, 1.12 |
| Pierwszy cesarz EN (16.11 wieczorem, reżyser) | „sprawdź, czy nie trzeba dodać kilku dźwięków efektów” — przegląd ujęć z listą wydarzeń: bez dźwięku były lalki wysuwające się zza rampy (Handan, regent, spisek), opadająca płachta na powóz, świt i prężenie muskułów cyklopów; dźwięk każdego wydarzenia sprawdza się listą `efekty.ZDARZENIA` przy opisie ujęcia, a nie na słuch | 1.12, Rytm 9 |
| Miniaturka Pierwszego cesarza (16.11, reżyser) | z dwóch koncepcji wygrało zbliżenie; plan ogólny miał za drobne postacie; cesarz bez obrysu ginął na tle miasta; tabliczka „NO WAY?!” prosta i za wysoko | 5.1 |
| Miniaturka (16.11, znalezione w kontroli) | ostrze łopaty ucięte krawędzią arkusza wyglądało jak grot; grudy ziemi na żołnierzu jak dziury; szyld z tytułem EN dotykał krawędzi kadru; meteoryt nachodził na ostrze łopaty | 5.2 |
| Miniaturka (16.11, reżyser) | Fujifilm o sile 1,8 „za mocny”, 0,8 nadal za dużo → 0,5 i minimalne rozjaśnienie; spirale na oczach z białym tłem → grube czarne wprost na skórze | 5.1, 5.4 |
| Syn słońca EN, akty 3–5 (18.11, reżyser: 3 uwagi, 16 markerów) | brak reakcji na mocnych chwilach (tabliczki „help”, „hmm..”, „stop!” z ręką do góry, „no way!”, „aaa!”, „I can't..”, „aaaa”, „brother!”, „boo!”); leżąca głowa i brat bez ruchu („porusz go”, „niech skacze”); wiosłuje tylko część łodzi; miecz obok dłoni Ninigiego („miecz ma być tutaj”); słońce ucięte krawędzią; zwrot ku słońcu niewidoczny; Iwarebiko tylko wskazuje góry („strzel tu strzałą”); po stracie braci stoi bez gestu („podnosi ręce”); za krótkie końcówki zejścia Ninigiego i wejścia w las Kumano | 1.25, 1.20, 1.18 |

Otwarte: słuchawka w „Starym telefonie” nie ma kabla do aparatu, a po spadnięciu telefon dzwoni dalej (świadomie,
dla ciągłości z następnym ujęciem) — do decyzji reżysera.
