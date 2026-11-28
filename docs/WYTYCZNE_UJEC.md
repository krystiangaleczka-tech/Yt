# Wytyczne ujęć — jak budować kadr, żeby reżyser nie musiał poprawiać rysunku

Obowiązuje każdego, kto tworzy albo poprawia ujęcia: Claude, inne agenty i skrypty renderu (`output/*/render*.py`),
sceny Stage w Studio i obrazy generowane do ujęć. Reżyser ocenia **grę, rytm i nastrój** — nie powinien wyłapywać
błędów rysunku. Każdy punkt poniżej wziął się z prawdziwej poprawki (sekcja 6 „Skąd te zasady”): z uwag reżysera
w ujęciach, z markerów na klatkach i z rozmów przy pracy.

**Wzorce do powielania.** Teatr papierowy: „Pierwszy cesarz” EN (projekt `prj_65a9a00a6f9d402c`, 80 ujęć, 11:18,
zatwierdzony przez reżysera 16.11.2026 po trzech turach markerów, render końcowy 17.11) i „Bonnie and Clyde” EN (projekt
`prj_dad935cf1d7446fa`, 119 ujęć, 18:19, gagi, klon lektora i podgląd na żywo; cztery tury markerów 19–24.11, 169 markerów
i 17 uwag, opublikowany 25.11 — raporty tur w `docs/filmy/bonnie-i-clyde/uwagi_rezysera_<data>.md`). Kreskówka 2D: „Oddział C”
0:00–0:53 (poprawione przez reżysera 3.11, wzorzec dla dni 2–30). Nowy film tej samej techniki zaczyna się od silnika
i sposobu pracy wzorca, nie od zera; scenerię i obsadę rysuje się nowe (Podręcznik, „Animacja rysowana kodem”). Silnik bierze się **najnowszy**, także
z gałęzi roboczej, na której jeszcze trwa praca (28.11: `uklad.py` z ujęcia „kawiarnia” był tylko na gałęzi
`claude/bonnie-i-clyde-kawiarnia`, a film o Szamilu powstał najpierw bez niego; reżyser: „miałeś się zastosować do wszystkich
wytycznych od najnowszych po najstarsze obowiązujące”) — przed pierwszym ujęciem sprawdź `git worktree list` i gałęzie
wzorca, weź najnowszy silnik i przejdź wytyczne od najnowszych (1.32) do najstarszych.

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
   kto co trzyma, w jakim jest stanie (żywy, chory, w koronie, oblepiony ziemią), jaka jest pora dnia (1.6). Stan liczy kod świata z kamieni
   milowych rozpiski (`swiat.stan`, `po("mur")`), a nie pamięć wykonawcy. Pierwsza klatka ujęcia = ostatnia klatka
   poprzedniego ujęcia tej sceny minus to, co cięcie świadomie zmienia (1.2, 1.6).
3. **Obsada i rekwizyty**: kogo i co widać, zgodnie z opisem i kwestią — kogo lektor wymienia, ten jest w kadrze, nikogo
   ponad to. Nowa postać dostaje podpis (1.15); każda postać ma własną sylwetkę, strój i stałą skalę (1.6, 1.24).
   Przy meblach i rzeczach w dłoniach: kto stoi za czym i do czego jest przyczepiona każda rzecz (dłoń, blat, naczynie,
   głowa) — rzut sceny z góry (1.32).
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
- Rzecz, która jest skutkiem zdarzenia w tym ujęciu, pojawia się w kadrze w chwili zdarzenia: czapki zabitych spadają
  z góry i dopiero potem leżą, kapelusz wylatuje z okna auta i ląduje — nie leży od pierwszej klatki (markery 24.11 w ujęciu
  48 „Bonnie and Clyde”: „spada czapka”, „spada druga czapka”).
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

### 1.6 Fizyka i ciągłość przedmiotów
Przedmiot ma przyczynę ruchu (drgania dzwonka zrzucają słuchawkę) i dźwięk (uderzenie o stół). Rzecz pokazana w jednym
ujęciu jest taka sama w następnym (telefon na biurku w dyżurce = telefon w zbliżeniu). Zakładaj przy tym, co widz wie:
zamknięte drzwi sprawdza się klamką, a nie tylko się o nich mówi.
- Pojazd ma to, co go napędza: wóz i powóz ciągnie koń, a ktoś nim powozi.
- Postać wygląda na swój wiek i ma tylko te atrybuty, które ma w tej chwili historii: dziecko nie nosi korony, zanim
  zostało królem. Jedna lalka nie gra dziecka i dorosłego.
- Znak, który z daleka czyta się jako symbol (krzyż, półksiężyc, gwiazda), nie wchodzi do kadru przypadkiem — zwłaszcza
  w historii wojny religijnej: pionowy karabin na tle czerwonej opaski białej czapki z daleka był czerwonym krzyżem nad
  głową rosyjskiego żołnierza (film o Szamilu, 28.11; karabin trzymany za plecami, własny arkusz `rek_kz("karabin")`).
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
- **Pora dnia to stan świata.** Ujęcie zaczyna się w porze, w której skończyło się poprzednie ujęcie tej sceny, a noc
  zapada albo mija na oczach widza: chmury unoszą się na nitkach, zjeżdża księżyc i po kolei gwiazdy; rano księżyc
  i gwiazdy odjeżdżają w górę i zjeżdża słońce („Bonnie and Clyde”: `scena.niebo` z `w.zmierzch`, `scena.gwiazdy`). Reżyser
  24.11 o ujęciach 20–21: „w połowie ujęcia 20 zmieniłbym słońce na księżyc, ściemnił na noc i dodał gwiazdy, i pamiętaj:
  w ujęciu 21 musisz z ciemności i księżyca zmienić na słońce”. Kwestia albo opis z nocą („Nocą W.D. wysiada…”) ma w kadrze
  księżyc albo gwiazdy (marker 23.11 w ujęciu 66: „niech wjedzie tu księżyc”), a tło dźwięku idzie za porą (noc — świerszcze).

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
- **Bez martwych sekund.** Ujęcie nie zaczyna się kilkoma sekundami ciemności ani pustej sceny, a długie martwe ujęcie
  nie stoi obok ujęć za krótkich na swoją akcję. Reżyser 19.11 („Bonnie and Clyde”, Eastham): „czemu jest przez 5 s ciemna
  scena, a poprzednie 2 były turbo krótkie? wytnij to i wydłuż tamte poprzednie po 2 s” — czas z martwego fragmentu dostają
  sąsiednie ujęcia, którym go brakowało.

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

**Rytm filmu: ujęcie = kwestia + wydarzenia, bez samotnych wstawek** (reżyser 28.11, „Imam / Diuna” wersja D: „są trzy
ujęcia jakieś długie, nagle jest jedno, które ma pół sekundy. Znowu są dwa ujęcia długie, a jeszcze nic się na nich nie
dzieje… każde ujęcie powinno być… zależne od tego, co jest w scenariuszu i co jest w narracji”). W D połowa ujęć była bez
słów (detale 1,4–2,4 s), a ujęcia z kwestią trwały 6–10 s, w których lalka tylko stała — rytm skakał „długie, długie,
krótkie” i nic się nie działo. Wzór to „Syn słońca” i „Bonnie and Clyde”: kwestia w 80–85 % ujęć, mediana ok. 10 s.
- Ujęcie z kwestią ma w opisie rozpiski **2–4 wydarzenia z sekundami** i każde stoi na słowie lektora: w kodzie
  `sl("klucz", "słowo")` (chwila słowa z tempa kwestii), gag w pauzie po kwestii `po_kw("klucz")` (output/szamil-diuna/ujecia_a.py).
- Detal, który w D był osobną wstawką (kindżał wbity w deskę, perły, świeca), jest wydarzeniem wewnątrz ujęcia z kwestią.
  Ujęcie bez słów to zapowiedź, kurtyna albo emocjonalne trzymanie (uścisk); krótkie ujęcia akcji idą seriami, nigdy
  pojedynczo między długimi.
- Długość filmu wynika z historii („nie róbmy stricte 4–5-minutowego filmu”), nie z formatu.
- Kontrola przed rysunkiem: `dane.kontrola_rytmu()` (docs/filmy/szamil-diuna/ujecia/dane.py) wyłapuje samotne krótkie
  ujęcie (< 3 s) między dwoma długimi (> 6 s), trzy ujęcia z rzędu o długościach w przedziale 0,6 s i kwestię bez
  dwóch wydarzeń w opisie — zero uwag, zanim cokolwiek zostanie narysowane.

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
porusza lub odwraca (ten sam punkt dłoni w każdym ujęciu tej sceny). Kwestia mówi o tym, co widać w tym ujęciu; to, co pokazuje następne ujęcie, mówi się w następnym (reżyser 21.11 o ujęciu
„palce”: „zmień narrację, bo opis sceny jest kompletnie inny” — kwestia o obciętych palcach i zwolnieniu leżała na obrazie
siekiery spadającej na stopę). O czym mówi lektor, to lalka robi na scenie:
„wypił truciznę” — podnosi czarkę do ust; „kopali studnię” — narzędzie uderza w ziemię i lecą grudy; „zachorował” —
kaszle; „zginął” — widać śmierć, a nie tylko zniknięcie. Postać ma stałą skalę: grozę pokazuje się gestem, cieniem
i światłem, nie powiększeniem lalki.

W historii o prawdziwych ofiarach („Bonnie and Clyde”) śmierć pokazuje teatr cieni za parawanem albo ślad: czapka, która
spada i zostaje na drodze, kapelusz z dziurą po kuli, dziewięć czapek na „nine dead lawmen”. Bez X na oczach, bez jęków
zabitych i bez gagu (Podręcznik → Humor, „Granica”; Dźwięk, „Głosy ludzi”).

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
- **Dygot na krawędzi dna:** rzecz postawiona z hukiem (dzbanek walnięty o ladę) kołysze się wokół tego narożnika dna,
  który dotyka blatu, a druga krawędź unosi się — nie obraca się wokół środka dna, bo wtedy narożnik wchodzi w blat
  („kawiarnia” 27.11: kontrola „stoi na blacie” pokazała dno 3 px pod blatem). Rzecz obok na tym samym blacie (filiżanka)
  podskakuje razem z uderzeniem.
- **Toczenie z podskokami** (kula stepowego zielska): w locie kula leci po paraboli i dalej się obraca (kąt nadal z drogi),
  a w każdej chwili styku dno leży na posadzce. Kontrola: dno = posadzka − wysokość podskoku w każdej klatce, w której
  posadzka jest w kadrze.
- **Lekka rzecz frunie:** kapelusz, kartka, list, pióro i gazeta opadają zygzakiem jak liść, kołyszą się i kładą na płask,
  a nie spadają jak kamień. Reżyser 23.11 („Bonnie and Clyde”): „niech ta czapka tak fruwa na ziemię z postrzeloną dziurą”,
  „ta kartka ma latać w powietrzu 4 s i wlepić się tak jak teraz”, kapelusz z okna auta „leci do góry w tym kierunku i spada
  na ziemię w 4 s” — czas z uwagi to czas od wylotu do położenia się, a miejsce lądowania to miejsce, w którym rzecz potem leży.
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
Tabliczka z markera „po angielsku” to okrzyk, jaki powiedziałby widz tej wersji, a nie przekład słowo w słowo
(„tabliczka maminsynek po angielsku” → „MAMA'S BOY!”, 23.11).

**Napisów lektora nie wypala się w obrazie** (reżyser 24.11, „Bonnie and Clyde”: „usuń te napisy, bo odpaliłem Studio
i nadal są w ujęciach”). Ujęcia, podgląd na żywo i render końcowy rysują się bez paska napisów (`render.py`; `NAPISY=1`
włącza go z powrotem), a napisy EN i PL idą na YouTube jako pliki `.srt` (`napisy_yt.py`). Cały kadr, także dół pod dawnym
paskiem, jest narysowany i sprawdzony na klatce. Ważna akcja dalej stoi nad dolnym pasem kadru, bo tam YouTube kładzie
napisy i pasek odtwarzania. Napisy, które są częścią obrazu (tabliczki, szyldy, zawieszki, nagłówki gazet), zostają.

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
- Kamera i podpis pokazują tego, o kim jest kwestia, w chwili, gdy lektor go nazywa. Wprowadzenie „to historia
  pierwszego cesarza” z najazdem na brata, który za chwilę ginie, myli widza (reżyser 18.11, „Syn słońca”) — najazd
  obejmuje bohatera, podpis „Iwarebiko, the future emperor” zjeżdża przy jego imieniu, drugi podpis („Itsuse, eldest
  brother”) dopiero przy „trzech braciach”. Kilka podpisów w jednym ujęciu idzie po kolei, za kwestią.
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
- Scena w teatrze cieni (sylwetki za parawanem) sama nic nie wyjaśnia: kwestia mówi kiedy, gdzie, kto i co się stało, a w kadrze
  wiszą zawieszka miejsca i czasu i podpisy na słowo („ARMORED CAR”, „Buck Barrow”, „Blanche”); wydarzenie kończy się skutkiem
  (gang ucieka). Reżyser 23.11 o Platte City: „więcej wyjaśnień w tej scenie”. Kwestia mówi też o tym, co widać: „family picnics”
  wymaga auta rodzin i koszyka w kadrze, „the Dallas sheriff” — szeryfa z podpisem, „both of them… in their legs” — dwóch „OUCH!”
  (Sowers: „zastanów się, czy dobrze jest narysowane całe to ujęcie według opisu sceny i narracji”).

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
| oczy „< <” na chwilę, usta „o” | zachwyt, „wow” na widok czegoś | „Bonnie and Clyde”: `zestaw_bc` `oczy="mniejszosc"` (24.11; ten sam znak przy tym samym widoku w ujęciach 14 i 49) |
| nuty wylatujące z instrumentu | muzyka grana w kadrze | `J.nuta` (24.11, saksofon Clyde'a przy ustach) |
| „Z” nad głowami | sen | ujęcie 20 „wagon” (śpiąca rodzina pod wozem) |
| komiksowy obłok z gwiazdkami nad czynnością | czynność, której nie rysujemy w szczegółach (wiązanie drutem, szamotanina); po obłoku widać jej skutek | ujęcie 64 „drzewo” (23.11: „ukryj środek ich ciała z drutami w takiej chmurze jak w bajkach”) |
| księżyc albo słońce na nitce, gwiazdy zjeżdżające po kolei | pora dnia; zmierzch i świt w kadrze (1.6) | `scena.niebo` + `w.zmierzch`, `scena.gwiazdy` (24.11) |
| komiksowy dym albo kurz za autem jadącym poziomo, poślizg bokiem | pęd, ucieczka — także auto na mapie (1.27) | ujęcie 19 „obietnica”, mapa w biurze Hamera (21.11, 23.11) |
| dziury po kulach w szybie i karoserii, jadą razem z autem | ostrzał | ujęcia 74 „sowers”, 109 „dym” |
| czapka albo kapelusz z dziurą po kuli, spada i zostaje | śmierć stróża prawa bez pokazywania ciała (1.11) | ujęcia 48, 76, 97, 118 |

Znak wisi nad postacią, której dotyczy: serce nad każdym z zakochanych, kajdanki nad tym, kogo aresztują — nie pośrodku
między nimi (markery 21.11: „nad nią serce”, „nad nim serce”, „nad nim kajdanki”).

**Tabliczka z markera** („tabliczka no way!”, „tabliczka yeah I saw”) wisi w miejscu kreski i już w sekundzie markera, a nie
dopiero od niej zjeżdża (`ujecia_a.tab_tu`: punkt ekranu → kadr wzorcowy, zjazd 0,7 s wcześniej). „Następna dopiero po 1,5 s”
to odstęp między chwilami, w których tabliczki już wiszą. Kilka takich samych okrzyków nad grupą (sześć „WE GOT THEM!”) wisi
na przemian wyżej i niżej, po jednej nad każdym.

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
- Strumień z naczynia do naczynia (kawa z dzbanka do filiżanki): dzióbek stoi **nad otworem** drugiego naczynia, strumień
  zaczyna się na końcu dzióbka, spada w dół i kończy się kilka pikseli pod brzegiem, schowany za przednią ścianką
  (plan strumienia tuż za filiżanką); na początku rośnie od dzióbka w dół, na końcu odrywa się od dzióbka; w naczyniu
  pojawia się tafla napoju. W `uklad.py`: `u.trafia` (koniec strumienia między brzegami otworu) + `u.w_naczyniu` (nic spod
  brzegu) + `u.dotyka` strumienia i dzióbka w tym samym punkcie (wzór: `ujecie_kawiarnia.strumien`).
- Nitka jest tylko przy tym, co teatr spuszcza z góry (zawieszka, księżyc, mapa, kielich); krople, kulki i drobiazgi
  spadają bez nitek („usuń te linie”).
- Drobne rzeczy w ruchu idą tak wolno, żeby widz zdążył je zobaczyć („te srebrne kulki niech dużo wolniej zjeżdżają”).
- To samo dotyczy teczki, kieszeni i szuflady: rzecz chowana do środka zjeżdża za przednią ściankę i zostaje w środku,
  a nie znika w jednej klatce (24.11, ujęcie 118 „Bonnie and Clyde”: „napraw to ściąganie w dół na linkach” — karta z aktami
  schodzi na linkach za teczkę).
- Nitka idzie z punktu, na którym wisi: pęknięta nić na mapie zwisa z jednej pinezki, a po supełku biegnie dalej od tej
  samej (24.11, ujęcie 86: „linia ma być prowadzona z jednej kropki, a nie z dwóch”).

### 1.23 Kulminacja jest mocna
- Uderzenie, wybuch i upadek mają wyraźną siłę: mocny wstrząs kamery, duży płomień (meteoryt, reżyser 15.11: „bardziej
  zatrzęś kamerą i większy płomień meteorytu”), drżenie budowli („zrób shaking tej tomb”).
- Pożar i zniszczenie rosną do końca ujęcia („spal ją bardziej na końcu”), a nie stoją na jednym poziomie.
- Przed szczytem muzyka milknie, zostają same efekty (syk głów węża, grad), na szczycie pada uderzenie (bęben, gong),
  a muzyka wraca głośniej i opada przez ok. 3 s (`efekty.CISZA`; przegląd 18.11: „za mało ciszy i muzyki przy
  szczytach”). Cisza jest krótka i rzadka: dwa–trzy szczyty na film.

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
- Film na ekranie kina i zdjęcie w dłoni też grają: postacie na płótnie chodzą, tańczą, pozują, auto wjeżdża, obraz migocze
  jak z projektora (reżyser 23.11: „poruszaj tymi postaciami… tak, jakby film po prostu leciał”); Bonnie na zdjęciu „robi
  pajacyka” (`zestaw_bc.zdjecie_pajacyk`). Światło żyje: lampa mruga albo zapala się na wydarzenie (`scena.mruganie`,
  `wnetrze(jasnosc=…)`), auto daje znak światłami (`ujecia_a.swiatla`, `miga`).
- Rzecz, która w życiu nie stoi, nie stoi w kadrze: auto z pracującym silnikiem drży i szarpie się, „jakby minimalnie
  chciało jechać, ale jest na ręcznym” (marker 19.11); dym po strzelaninie unosi się przez całe ujęcie i rzednie dopiero
  pod koniec (24.11: „dłużej dym”); błoto pryska łukiem spod buksującego koła (24.11). Światło, które gaśnie albo się psuje,
  robi to na wydarzenie i ma skutek (Wellington 24.11: reflektory mrugają i gasną, więc nikt nie widzi tablicy DETOUR).
- Gest po czynności dopowiada postać: po strzale ręka z rewolwerem idzie do ust i dmucha w dym z lufy (marker 19.11),
  strażnik na „STOP!” podnosi rękę, Hamer odmawia uniesioną dłonią, którą macha (23.11). Kto długo stoi w kadrze, ma swój
  ruch w tę i z powrotem (Blanche chodzi wzdłuż grządki i podlewa, Henry za szybą rozgląda się „jeszcze 2× lewo prawo”).
- Zwrot postaci zaczyna się od przeciwnego kierunku, żeby był widoczny (Iwarebiko najpierw patrzy w lewo, potem
  zwraca się ku słońcu). Ujęcie przejścia albo przybycia ma końcówkę „już na miejscu” (Ninigi stoi na szczycie, wojsko
  wchodzi w las) — 1.18.

### 1.26 Otwarcie, skróty i kurtyny
- **Zapowiedź (6 s)** składa się z ok. 10 skrótów najmocniejszych ujęć filmu (`render.WYCINEK`: oryginał od jego
  najlepszej chwili, ze stanem świata z jego miejsca w filmie), cięte parami 0,4 / 0,7 s (sąsiednie różne co najmniej
  o ¼ s), bez przejść, z uderzeniem na każdym cięciu; kończy się ściemnieniem (reżyser 18.11: „mini spoiler 5 s, co
  będzie w filmie (najlepsze akcje)”; 19.11: „najlepiej zrób go 6 s i szybko zmieniaj ujęcia”). Skrót bierze chwilę akcji,
  ale nie podpis, który zdradza tajemnicę późniejszego aktu.
- **Lektor od pierwszej sekundy** (20.11, „Syn słońca”, reżyser: „mogę gadać nawet od 1 s filmu”): już na zapowiedzi
  jedno zdanie o tym, o czym jest film — bohaterowie i stawka („Japan began with gods, monsters, and four brothers who
  set out to rule it.”); kwestia stoi na pierwszym skrócie i biegnie przez całą zapowiedź (napis przechodzi na następne
  skróty). W kurtynie startu krótkie zdanie, które stawia pytanie („Only one of them survived.”). Liczby: Podręcznik →
  Rytm, „Początek filmu”.
- **Jedna scena najwyżej dwa razy**: zapowiedź nie bierze scen, które są w haku — scena z haka gra w haku i w ciele
  filmu, scena z zapowiedzi w zapowiedzi i w ciele filmu (reżyser 20.11, „Syn słońca”: „czemu pokazujemy scenę z morza
  w zapowiedzi, zaraz w 15 znowu i potem w filmie? czemu nie tylko 2 razy?”). Przy każdej zmianie haka sprawdź listę
  `render.WYCINEK`: żadne źródło skrótu `zap_*` nie może być źródłem skrótu `hak_*`.
- **Kurtyna startu** trwa krótko (ok. 2,5 s; z kwestią lektora tyle, żeby po niej została co najmniej 1 s obrazu — „Syn słońca”: 3,0 s, kwestia od 0,2 s) i rozsuwa się na tytuł teatru, a na scenie stoi już bohater haka
  (`KURTYNA_START`); następne ujęcie najeżdża na niego i lektor mówi, kim jest — **wprowadzenie przed akcją** (reżyser
  18.11: „z dupy jest wprowadzenie: strzelają, potem 3 giną, a nie ma info, co się dowiemy”). Akcja haka pokazuje każde
  zdarzenie raz (strzała trafia raz, następne ujęcie zaczyna się od skutku), a postać, której imię padnie dopiero w ciele
  filmu, jest w haku bez imienia i bez podpisu („the eldest brother”).
- **Hak** nie skacze z miejsca na miejsce bez pomostu: między dwoma ujęciami haka z różnych dekoracji stoi ujęcie
  przejściowe (teatr cieni za parawanem między strzałą a burzą; reżyser 18.11: „po 1 ujęciu nie może być od razu ta
  woda, tylko coś pomiędzy”). Po obietnicy, przed pierwszym aktem, ujęcie-pomost mówi, po co cofamy się w czasie
  („To see why these brothers believed they came from the sun, we go back to the beginning…”).
- **Jeden początek** (reżyser 19.11, „Bonnie and Clyde”: „a potem w tym filmie dowiecie się blablabla… i kurtyna
  i znowu od nowa tak jakby? tak ma być?” — nie): obietnica to jedno pytanie, które prowadzi prosto w retrospekcję
  („So how does a joke turn two broke kids into…?” → „It all starts in West Dallas…”), a nie lista „By the end, you'll
  know…”. Między prologiem a aktem I nie ma kurtyny ani tabliczki aktu (`render.BEZ_KURTYNY`), tylko ściemnienie
  i zawieszka miejsca i czasu; kurtyny z pytaniami od aktu II. Liczby i powód: Podręcznik → Rytm, „Początek filmu”.
- W pierwszej minucie dekoracja zmienia się co najmniej 3 razy (licznik w `buduj_szkice.zmiany_scenerii`).
- **Powrót do sceny z haka** w ciele filmu ma inne słowa niż hak („Remember that arrow?”), a nie powtórkę kwestii.
- **Kurtyna aktu** pokazuje tytuł-pytanie w dwóch rzędach: mała tabliczka „Act N”, pod nią pytanie, na które akt
  odpowiada (`render.kurtyna`); żadna tabliczka nie jest szersza od kadru. Akt przed zwrotem fabuły kończy się
  pytaniem w kwestii, a nie zdaniem, które brzmi jak koniec filmu („But did he ever really exist?”).

### 1.27 Teatr, który się buduje, i to, co przed rampą
- Lalki i auta wchodzą dopiero, kiedy dekoracja się zbuduje (`scena.wejscie`); na pustym płótnie nikt nie stoi.
  To samo dotyczy rzeczy: rekwizyt, zawieszka i nitka postawione wprost w ujęciu pojawiają się po zbudowaniu dekoracji
  (`render.po_budowie`), a światło za oknem zapala się, gdy stoi ściana — teczka nie wisi nad pustym płótnem przed biurkiem.
  Wyjątek: rzecz w dłoni albo na głowie lalki wchodzi **razem z lalką**, pełna od pierwszej klatki — nie prześwituje
  w dłoni wysuwającej się lalki (w `uklad.py`: `u.w_dloni` albo `u.rzecz(..., z_lalka=True)`; „kawiarnia” 27.11: dzbanek
  i gazeta przez 0,3 s prześwitywały w dłoniach, bo `po_budowie` przyciemniał je jak rekwizyty postawione na scenie).
- Pasażer auta jest widoczny w oknie od pasa w górę; nogi nie wystają spod karoserii (`siedzi=True`). Rzecz w oknie
  (gazeta) stoi obok głowy, nie na niej.
- Rzecz leżąca na ziemi, leżąca postać i woda, w której ktoś brodzi, są nad rampą — inaczej rampa i napisy je chowają
  (czapki zabitych, trumna, rzeka, ranny Buck).
- Broń w ręce celuje tam, gdzie ma celować: kto czyści karabin, trzyma go na kolanach, a nie w stronę partnera.
- Sylwetka w teatrze cieni jest jednolicie czarna; prześwitujące ręce rysują na tułowiu „X”.
- Auto, które dachuje, obraca się wokół swojego środka i ląduje widoczne; płomień wychodzi z auta, nie zasłania go.
- Akcja przy ziemi w zbliżeniu: kamera niżej, żeby nie chowała się pod napisem. Rzecz, o której mówi kwestia (teczka
  Hamera, kanapka Bonnie), stoi nad pasem napisów i przed karoserią, nie za nią; reakcja („HA HA HA!”) wisi nad głową, nie
  na twarzy i nie pod napisem.
- **Żaden napis nie jest lustrzany**: przewracana strona gazety pokazuje drugą stronę (inną gazetę), lecące gazety obracają
  się bez odbicia, napis na drzwiach auta jadącego w lewo rysuje się odbity w arkuszu (`ford(lustro=True)`), żeby po odbiciu
  auta czytał się normalnie.
- **Napis mieści się na swojej tablicy**: tablica jest szersza od napisu; napis z odstępami liter liczy środek sam
  (`glyphs(spacing=…)` stawia litery od punktu startu). Napis na pasiastym płótnie ma własny szyld, inaczej ginie na jasnym pasie.
- **Nazwa, którą mówi lektor, jest do przeczytania**: tabliczka miejsca (nazwy cmentarzy) wisi nad głowami, nie za postaciami
  przy krawędzi kadru; nowa tabliczka nie zasłania dekoracji, o której jest ujęcie (serca nad łukiem z kwiatów, nie na nim).
- **Rzecz w dłoni ma kierunek, jaki ma w życiu**, a nie przedłuża ręki jak patyk (reżyser 19.11: „musisz poprawić ich
  umiejscowienie w rękach”): karabin w gotowości albo na warcie stoi pionowo przy boku, lufą w górę (`KARABIN_PION`;
  sąsiedzi z karabinami pod kątem tworzyli X); gazeta jest w dłoni przed postacią, obok głowy — nie na głowie i nie
  w tułowiu (marker 21.11: „gazeta za ręką, a nie w nim i na głowie”) — dłoń leży na bliższym brzegu kartki; łyżka miesza w garnku (garnek przed łyżką); laska sięga ziemi; miarka zwisa z dłoni wzdłuż mierzonego;
  kapelusz uniesiony w dłoni w oknie auta (pasażer może trzymać rzecz). Każdą trzymaną rzecz sprawdza się na arkuszu
  zbliżeń dłoni (wycinek 240 px wokół dłoni w kilku chwilach ujęcia).
- **Postać niesiona wisi przez bark niosącego**: biodra na barku, głowa i ręce zwisają za plecami, nogi z przodu, a przednia
  ręka niosącego (w skrócie) trzyma ją za uda (marker 23.11 w ujęciu 65: „Bonnie połóż tak, głową w dół na barkach Clyde'a”,
  „jedną rękę pozginaj w ten sposób na Bonnie”; wcześniej leżała na wyciągniętych rękach i wisiała za plecami). Stojący
  trzyma karabin w dłoniach (`KARABIN()`), a nie „na kolanach” w powietrzu.
- **Wycinek na mapie gra jak w teatrze**: auto jadące po mapie stoi poziomo, jak lalka na scenie (nie obraca się wzdłuż drogi
  jak w widoku z góry), na zakrętach ślizga się bokiem, a za nim kłębi się komiksowy dym albo kurz; druga trasa to ten sam
  gag po innej drodze (marker 21.11 w ujęciu 19: „autka mają driftować po mapie z dymem”, „tak samo jak tamto, tylko inna
  trasa”; uwaga 23.11: „auta mają być poziomo, a za nimi taki komiksowy dym”). Mapa wisi tak nisko, że widać ją całą nad dolnym
  pasem kadru (23.11 w ujęciach 80, 81, 97: „mapa niżej”).
- **Zmiana bohatera albo miejsca ma łącznik**: kiedy opowieść przechodzi od jednej postaci do drugiej (Clyde → Bonnie)
  albo do innego miasta, pierwsza kwestia nowej sceny mówi, gdzie i kiedy jesteśmy („Meanwhile, a few miles away in Cement
  City…”), zjeżdża zawieszka miejsca, a obraz łączy oba ujęcia (indyk, który uciekł w West Dallas, spada w Cement City).
  Z indyków od razu w ślub było „bez sensu” (reżyser 19.11). Kontrola: wypisz wszystkie granice scen z końcem i początkiem
  kwestii i sprawdź, czy każda ma łącznik czasu, miejsca albo osoby.
- **To samo miejsce nie buduje się od zera**: kiedy następna scena dzieje się w tym samym miejscu (pole pod Waldo po
  śmiechu Darby'ego, rzeka zaraz po Dexfield, ta sama nocna droga, Kansas po jeździe z Boydem), jest zwykłe cięcie bez
  gaśnięcia i bez pustego płótna (`render.CIAGLOSC`); budowa od zera mówi widzowi „nowa historia”.
- **Próbka z fragmentów ma plansze**: przed każdym fragmentem plansza z numerem, aktem, ujęciem i minutą filmu
  (`probka_dzwieku._karta`) — zlepek bez plansz wygląda jak jeden film, w którym historie nachodzą na siebie.
- **Podpis i puenta na słowo**: podpis zjeżdża, kiedy lektor nazywa postać i postać jest widać (W.D. stoi przy aucie, wsiada
  potem); puenta kwestii („undertaker”) nie stoi w podpisie wcześniej niż w kwestii.

### 1.28 Biomechanika lalki i rekwizytu
Reżyser 19.11 („umiejscowienie tych rekwizytów w rękach, albo na stole, przy stole itp. jest tragiczne… ogarnij biomechanikę”).
Lalka teatru papierowego ma ciało sztywne i dwie ręce, każda to jeden odcinek od barku do dłoni (zawias tylko w barku). Z tego
wynikają zasady — liczone, nie zgadywane (`scena.bark`, `scena.dlon`, `scena.siegnij`, `scena.stan_przy`).
W silniku `uklad.py` (1.32) ręka ma **łokieć**: ramię i przedramię na spince, zasięg = ramię + przedramię, kąty liczy
odwrotna kinematyka (`u.lalka(..., przod=cel)`); `siegnij` zastępuje kontrola „dłoń sięga celu”, a `stan_przy` —
ustawienie postaci z punktu chwytu (wzór: `ujecie_kawiarnia.stan_bonnie_x`: ucho dzbanka w 80% zasięgu ręki). Zasady
niżej obowiązują w obu silnikach:

**Zasięg i kolejność.** Najpierw ustala się punkt, którego dotyka dłoń (ucho dzbanka nad filiżanką, brzeg gazety przy twarzy,
dłoń partnera, blat), potem kąt ręki z tego punktu: `kat, dosiega = siegnij(lalka, x, punkt)`. Jeśli dłoń nie dosięga
(odległość od barku większa niż ręka), lalka **podchodzi** (`stan_przy`) albo rzecz leży bliżej — rzecz nigdy nie przyskakuje
do dłoni, a dłoń nie wisi w powietrzu obok rzeczy.

**Narzędzie ustawia się od końca, który pracuje.** Rzecz z dwoma ważnymi punktami (dzbanek: ucho i dzióbek; konewka, łyżka
z czerpakiem, pióro, nóż) liczy się od tego, co robi: najpierw dzióbek nad otworem filiżanki (z filiżanki, która stoi na
blacie), z niego i z przechyłu — ucho, z ucha — cel dłoni, z celu dłoni — miejsce postaci. Przechylając dzbanek, obraca się
go wokół dzióbka (dzióbek stoi nad filiżanką, dłoń z uchem się przesuwa), a nie wokół dłoni. Odwrotna kolejność (postać →
dłoń → dzbanek) daje strumień obok filiżanki.

**Chwyt za uchwyt.** Każdy rekwizyt ma punkt chwytu w arkuszu (kotwica `trzyma`): dzbanek — ucho, rewolwer — kolba (0.3, 0.75),
karabin — szyjka kolby (0.3, 0.55), kula — rączka (0.5, 0.45), laska — gałka, gazeta — bliższy brzeg, miarka — kasetka.
Dłoń leży na punkcie chwytu; rzecz płaska (gazeta, list, zdjęcie) leży **za dłonią** (szósty element `trzyma` z = 0.02).

**Kierunek rzeczy nie idzie za ręką**, tylko za tym, do czego służy (`za_ręką = False`): rewolwer lufą przed siebie, poziomo
(marker 19.11: „w tę stronę ma być skierowany rewolwer, i w następnych ujęciach też”); karabin noszony przy nodze lufą w dół
(`KARABIN`), karabin do strzału poziomo, ręka ok. 90° (`CEL`), karabin na warcie pionowo lufą w górę (`KARABIN_PION`);
dzbanek pionowo, przy nalewaniu przechylony o ok. 45° dzióbkiem nad naczynie; laska i kula pionowo do ziemi; łyżka w garnku.

**Rzecz na stole stoi na blacie**: dolna krawędź rzeczy = górna krawędź mebla (`STOPY − wysokość mebla`), plan rzeczy tuż
przed meblem. Postać przy stole stoi tak blisko, że dłoń sięga blatu; siedząca — `sink`, a mebel ją zasłania od pasa w dół.

**Rzecz zmienia się w jednej klatce, bez przemiany**: gazeta → zgnieciona kulka, cygaro w dłoni → cygaro w ustach,
rewolwer w dłoni → za paskiem. W klatce N rzecz A znika, w klatce N+1 w tym samym miejscu jest rzecz B (marker 19.11: „ma
zniknąć w tej klatce… i tu w rękach pojawić się w następnej klatce; nie robisz tych przemian pomiędzy tymi dwoma rodzajami
obiektu”). Nigdy nie skaluje się jednej rzeczy w drugą.

**Rzecz przechodzi z ręki do ręki dłonią w dłoń**: dający wyciąga rękę (dłoń w punkcie P), biorący sięga tą samą chwilą do P
(`siegnij`), rzecz przeskakuje między dłońmi w jednej klatce. Nie ma rąk bez właściciela — jeśli coś podaje ktoś, to ten ktoś
stoi w kadrze (marker 19.11: „skąd ta ręka? tu ma stać gościu”).

**Jedna ręka — jedna rzecz.** Co ręka trzyma, zostaje w niej, dopóki historia tego nie odkłada; druga czynność idzie drugą ręką
(marker 21.11: „w tej ręce cały czas trzyma pistolet”, „w drugiej ręce bierze z buzi papieros”). Dłoń przy ustach, piersi czy
kieszeni jest bliżej barku niż długość ręki, więc ręka zgina się ku kamerze — w rysunku jest krótsza (`scena.do_punktu` → `rece`
i `skrot`), a tylna ręka, która sięga przez pierś, idzie przed tułów (`tyl_przed`). Rzecz wkładana komuś do ust idzie z dłoni
dającego prosto do ust (dający stoi tak blisko, że dosięga — `stan_przy`), podmiana w jednej klatce.

**Strój do czynności.** Jeśli opis albo kwestia mówi „chowa pod płaszcz”, lalka ma płaszcz (`bonnie_plaszcz`), a rzecz znika
pod połą przy dłoni na piersi — nie przy biodrze sukienki (marker 21.11: „skryj go pod płaszcz”).

**Strzał widać**: strzela się, kiedy kamera pokazuje strzelca; błysk na końcu lufy, lufa w kierunku lotu kuli, potem dymek
(marker 21.11: „teraz strzel z końcówki rewolweru” — wcześniej strzał padał poza kadrem, kula brała się znikąd).

**Postać na pojeździe**: siedzi (`siedzi=True`, biodra na siedzisku, pace, grzbiecie konia), nie stoi obok; zsiada łukiem
(skok) na ziemię, a wsiada łukiem do okna i dalej siedzi w nim widoczna — nie znika w przenikaniu (marker 21.11: „clyde
w aucie”). Z auta, które ugrzęzło, wyskakuje się łukiem „przez dach” (marker 19.11, Kaufman). Jeździec na koniu: biodra na
grzbiecie, nogi zakrywa koń.

**Nakrycie głowy zdejmuje ręka**: dłoń idzie do czubka głowy (ręka w skrócie), kapelusz przechodzi z głowy do dłoni w jednej
klatce (lalka bez kapelusza + sam kapelusz z tego samego rysunku), potem uchylony wraca na głowę albo zostaje w dłoni przy boku
(`ujecia_a.kapelusz_reka`; reżyser 23.11: Gault „ściąga ręką kapelusz z głowy i uchyla, i znowu odkłada na głowę, a rękę daje
w dół przy ciele”; ukłony: „i tak dla wszystkich, co mają coś na głowie”). Nie podmienia się lalki na „bez kapelusza” z kapeluszem
przyklejonym do ręki. Cecha postaci (słoma w ustach Gaulta) jest w lalce, więc idzie za nią do każdego ujęcia (`scena.SLOMA`).

**Rzecz rzucona i upuszczona leci z dłoni** po łuku przez punkt z kreski markera i ląduje tam, gdzie leży potem (moneta z ręki
kobiety do kasetki, broń Hamera w górę i do ręki z drugiej strony, kapelusz z okna auta na ziemię, pranie z okna przez dach do
koszyka); ręka rzucającego robi zamach.

**Kontakt dwóch postaci** (pocałunek, uścisk): podchodzą, aż głowy albo dłonie się zetkną, i nie wchodzą jedna w drugą;
wyższa się pochyla (`lean`), niższa unosi (`lift`); potem wracają na swoje miejsca. Postacie, które są razem, stoją razem:
Clyde przy Bonnie i W.D. trzyma ją pod ramię, a nie stoi metr dalej (marker 24.11: „przybliż go do nich dwóch”).

**Kontrola**: arkusz zbliżeń dłoni (wycinek 240 px wokół każdej dłoni z rzeczą w kilku chwilach ujęcia) i arkusz stołów
(rzeczy na blacie, postacie przy meblach) przed oddaniem ujęć.

### 1.29 Wycinek jest cały w każdym wariancie, a kostium jest jednym kawałkiem

- **Nakładka kładzie się na wierzch.** Kurz, błoto, cień czy plama na wycinku to osobna warstwa nałożona na niego
  (`alpha_composite`, tylko tam, gdzie wycinek ma papier). `ImageDraw` z półprzezroczystym kolorem na obrazie RGBA nie
  miesza kolorów, tylko podmienia piksel razem z alfą — dół karoserii „auta w kurzu” robił się przezroczysty i spod niego
  wystawały nogi pasażerów, w każdym ujęciu z `kurz=True` (reżyser 24.11: „w kilku nadal nie ma spodów aut”).
- **Wariant sprawdza się jak nowy wycinek.** Każdy przełącznik wycinka (kurz, dziury, napis, noc) zmienia arkusz: obejrzyj
  go raz obok wersji podstawowej, zanim pojedzie do ujęć.
- **Punkt chwytu leży na papierze.** Rekwizyt, który ktoś trzyma, nalewa albo stawia, ma w arkuszu punkty: chwyt, koniec
  roboczy (dzióbek, lufa), dno. Zanim pojedzie do ujęć, obejrzyj arkusz raz w powiększeniu z tymi punktami zaznaczonymi:
  ucho jest przyklejone do korpusu, dzióbek wychodzi z korpusu, dno to dolna krawędź papieru. `zestaw_bc.REKWIZYTY["dzbanek"]`
  ma ucho 17 px obok korpusu (wisi w powietrzu), więc dłoń na uchu nie trzymała dzbanka — „kawiarnia” 27.11 rysuje własny
  dzbanek (`ujecie_kawiarnia.dzbanek_ark`); inne ujęcia ze starym dzbankiem trzeba przejrzeć (1.6).
- **Mebel nie ma szpar.** Mebel jest sklejony z kawałków o poszarpanych brzegach i między nimi zostają szparki 1–3 px, przez
  które prześwituje to, co za nim — przez ladę prześwitywała Bonnie („kawiarnia” 27.11, kontrola „od pasa w dół za ladą”).
  `u.mebel` w `uklad.py` kładzie za każdym meblem jego plecy (obrys z zalepionymi szparkami, ciemniejsza barwa mebla);
  mebel rysowany poza silnikiem (`scena.wnetrze`) trzeba sprawdzić tak samo, kiedy ktoś za nim stoi.
- **Kostium z jednego kawałka.** Strój, który zakłada się na lalkę (suknia ślubna, płaszcz), to jeden wycinek od linii
  ramion do dołu, przed tułowiem i za przednią ręką, z pochyleniem lalki — nie dzwon doklejony od pasa do sukienki z arkusza
  lalki (reżyser 24.11: „suknia ma być w jednej całości, a nie w dwóch częściach”).

### 1.30 Postać w oddali to pomniejszone zbliżenie, profil to profil
Wzorem jest zbliżenie (np. zarażony z profilu w d04_22): w planie ogólnym ta sama postać ma te same proporcje
i **cieńszą kreskę w skali postaci**, a małe elementy (oczy, źrenice, uszy, usta) nie „gotują się” w kleks.
Twarz odwrócona w bok bardziej niż o pół (look ≥ 0,55) rysuje się **z profilu**: nos wystaje poza obrys głowy,
jedno oko jest w głowie (nie na jej krawędzi), ucho z tyłu, usta z przodu — nie przesunięta twarz od przodu.
W skryptach: `kit_a.scaled` (figure / figure_back / sitting / zarażeni) i `kit_a._profile_face`.

### 1.31 Co trzymane, ma dłoń i rękę
Słuchawka przy uchu, przepustka chowana do kieszeni, dłoń na czyjejś piersi — rzecz trzymana ma dłoń, a dłoń rękę,
która prowadzi do barku tej postaci (albo wychodzi spod kadru tam, gdzie ten bark jest). Nie ma słuchawek wiszących
przy uchu ani dłoni bez ręki (`kit_a.handset(..., who=)`, `kit_a.listening`).

### 1.32 Układ sceny liczy silnik: kto za czym stoi i do czego jest przyczepiona każda rzecz
Reżyser 27.11 („Bonnie and Clyde”, ujęcie 25 „kuchnia”): „model AI nie do końca wie, kto trzyma co w ręku, kto jest za czym”.
Przy ręcznym `x`, `y`, `p` i `z` każdego wycinka te decyzje zostawały wyobraźni wykonawcy i wracały jako markery: stół stał za
aktorami jak ława, Clyde wjeżdżał zza krawędzi kadru obok zamkniętych drzwi, choć słychać było drzwi, a kapelusz „uchylał”
pustą dłonią nad głową. Dlatego:
- **Najpierw rzut z góry.** Przed rysunkiem ujęcia z meblami, drzwiami i rzeczami w dłoniach zapisz rzędy sceny (za ścianą,
  przy ścianie, aktorzy, przód przed aktorami) i kto stoi w którym; kto jest za ladą, a kto przed nią, i dlaczego. Plan głębi
  i kolejność rysowania wynikają z rzędu, nie z liczby wpisanej przy wycinku.
- **Bliższy rząd nie stoi przed akcją ujęcia.** Kto stoi bliżej widza, stoi z boku tego, o czym jest ujęcie, a nie przed
  tym — i to samo dotyczy rzeczy w jego dłoniach. „Kawiarnia” (27.11): Bonnie za ladą (obsługa stoi za ladą, lada zasłania
  ją od pasa jak kuchenka w „kuchni”), klient przed ladą, ale przy jej końcu — gdyby stał przed środkiem lady, zasłoniłby
  filiżankę i nalewanie; jego gazeta zasłaniała filiżankę jeszcze, póki wisiała za nisko (kontrola „filiżanka: widać ≥ 95%”
  pokazała 82%). Na to, o czym jest ujęcie, zawsze stawiaj kontrolę `u.widac(…, 0.95)`.
- **Każda rzecz jest do czegoś przyczepiona**: do dłoni (za punkt chwytu), do blatu, do wnętrza naczynia albo do głowy.
  Położenie liczy się w każdej klatce z tego, do czego jest przyczepiona (garnek jedzie razem z wyrastającą kuchenką).
  Przepięcie, np. z głowy do dłoni, dzieje się w tej klatce, w której dłoń dotyka chwytu (1.28).
- **Gest do głowy, ust i ucha robi ręka z łokciem**: dłoń idzie do punktu, a kąty barku i łokcia liczy silnik (odwrotna
  kinematyka dwóch odcinków). Sztywna ręka z jednym zawiasem nie sięga własnej głowy: od barku do kapelusza jest ok. 0,75
  długości ręki.
- **Wejście przez drzwi to przejście z rzędu do rzędu**: drzwi się otwierają, postać przechodzi przez otwór, drzwi się
  domykają. Dźwięk drzwi oznacza, że drzwi się ruszają (1.2).
- **Kontrola każdej klatki na buforze identyfikatorów** (każdy wycinek ma właściciela): ile widać każdej rzeczy, czy dłoń
  dotyka chwytu, czy dno stoi na blacie, czy nic nie wychodzi spod brzegu naczynia ani poza otwór drzwi, czy dłoń sięga
  celu. Obok klatki rzut sceny z góry z rzędami, przyczepieniami i kamerą.
- **Kontrola nie przechodzi na pusto.** Kontrola, której w danej klatce nie da się sprawdzić — rzeczy jeszcze nie ma
  (wyłania się przy budowie dekoracji), punkt albo dno jest poza kadrem (przy zbliżeniu 1,15 posadzka jest pod dolną
  krawędzią, kula za prawym brzegiem) — nie daje „OK”, tylko trafia do pominiętych z powodem (`st.uklad.pominiete`).
  Raport (`uklad.zlicz` + `uklad.raport_md`) pokazuje przy każdej kontroli: z błędem / sprawdzonych / pominiętych,
  a kontrola sprawdzona w **zero** klatek jest błędem — zapisana, a nigdy niesprawdzona niczego nie dowodzi
  („kawiarnia” 27.11: „filiżanka stoi na blacie” przechodziła, kiedy filiżanki jeszcze nie było). Kontrolę zapisuj bez
  warunku „dokładnie w tej chwili” i sprawdź, czy każda kontrola z opisu ujęcia ma swój wiersz w raporcie — kontrola styku
  zielska z posadzką czekała na podskok równy dokładnie zeru, nie trafiła w żadną klatkę i w raporcie nie było jej wcale.
- **Nowa kontrola dostaje dowód.** Kiedy dopisujesz nowy rodzaj kontroli albo nową kontrolę rzeczy w dłoni, raz celowo
  zepsuj to, co sprawdza (dzbanek przesunięty o 20 px od dłoni), pokaż, że kontrola to łapie, i cofnij — wzór:
  `python3 ujecie_kawiarnia.py dowod <katalog>`.

Silnik: `output/bonnie-i-clyde/uklad.py` (nakładka na `papier.Stage` i `scena.lalka`; `Uklad(st, t)`, `u.mebel`, `u.na`,
`u.lalka`, `u.rzecz`, `u.w_dloni`, `u.trafia`, `kontrola(st)`, `zlicz`, `raport_md`, `rzut(st, …)`), wzory:
`ujecie_kuchnia.py` (ujęcie 25, zatwierdzone przez reżysera 27.11: 17 kontroli, 0 błędów) i `ujecie_kawiarnia.py` (ujęcie 24:
strumień do filiżanki, odstawianie z hukiem, gazeta w obu dłoniach, toczenie z podskokami; 24 kontrole na każdej z 250 klatek,
0 błędów; czeka na reżysera). Na 27.11 silnik jest na gałęziach `bonnie-i-clyde-kuchnia-uklad` (kuchnia) i
`claude/bonnie-i-clyde-kawiarnia` (kawiarnia + usprawnienia silnika z tej sekcji), jeszcze nie scalonych z gałęzią filmu.
Ujęcia z meblami, drzwiami i rzeczami w dłoniach budujemy odtąd na tym silniku.

### 1.33 Scenografia zmienia się z opowieścią, a każdy film ma własną
Reżyser 28.11.2026 po 2 minutach szkicu E „Imama / Diuny”: „jest za mało różnych ujęć… przez 2 minuty tylko dwie
scenografie, bądź jedna, a powinno ich być co najmniej, nie wiem, raczej 4 przez 2 minuty… od 40 s jest cały czas to
samo, że są te góry… Jeśli mamy pokazywać znowu daną scenerię, to musimy ją pokazać w inny sposób… potem za jakiś czas
w inny sposób w danym podrozdziale czy rozdziale, bo musi być różnica ujęć”; „wziąłeś biuro z Bonnie i Clyde. Ma być
zupełnie inne”.
- **Co najmniej 4 różne dekoracje w każdych 2 minutach** (wzór po poprawce: najmniej 9, średnio 11,5). Licznik:
  `output/szamil-diuna/kontrola_scenografii.py` (okno 120 s co 10 s, najdłuższy ciąg tej samej dekoracji) — zero okien
  poniżej minimum, zanim ujęcia pójdą do Studio.
- **To samo miejsce jeszcze raz = inaczej pokazane**: plan ogólny, potem zbliżenie miejsca (wioska → wieża z bliska →
  wąwóz), inna pora dnia i światło w kolejnych ujęciach jednej sceny (wymiana na rzece: dzień → złota godzina → zachód,
  `scena.MICZIK_SWIATLO`), inna pogoda albo pora roku, inny pokój tego samego domu (izba Szamila, pokój syna, sypialnia
  nocą). Siedem ujęć oblężenia Achulgo stało na jednej dekoracji; po poprawce: skała z twierdzą, bateria na szańcach,
  brama, obóz, skała z jaskiniami z bliska, rzeka nocą.
- **Motyw krajobrazu nie jest tłem każdej dekoracji.** Pasma gór stoją w planach ogólnych gór; las, dwór, równina,
  wąwóz i miasto mają własne tło (gęsty las bez gór, łagodne wzgórza, ściany skał, niebo pory dnia). W szkicu E te same
  arkusze gór stały za lasem, Gruzją, rzeką i nawet za Kaługą na rosyjskiej równinie.
- **Każdy film rysuje swoje dekoracje i meble.** Z poprzedniego filmu bierze się silnik i sposób pracy, nie wycinki:
  tapeta, okno, podłoga z desek, biurko, stół, łóżko i szafka „Bonnie and Clyde” złożyły gabinet cara i reżyser je
  rozpoznał. Wnętrze ma epokę i miejsce (Pałac Zimowy: płyciny, złocone pilastry, karmazynowe zasłony, dwugłowy orzeł,
  parkiet, malachitowy blat), meble są w zestawie filmu (`MEBLE["biurko_palac"]`…). Przed oddaniem przejrzyj, z jakich
  arkuszy złożona jest każda dekoracja (pamięć: także kulisy i podłoga pod ścianą).
- Technicznie: duży arkusz z dziesiątkami kawałków liczy się raz i leży na dysku (`zestaw_kz.stack_d`, `build/wycinki`),
  a drobiazgi (grzbiety książek, kamienie, klepki) rysuje się wprost na arkuszu — regały z 480 kawałkami papieru liczyły
  się 2 minuty i blokowały podgląd na żywo.

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
   - **Pary cięć**: dla każdego ujęcia n sprawdź n−1 → n → n+1 — czy n wynika z tego, co stało się w n−1 (miejsce, pora
     dnia, kto gdzie jest, kto co trzyma, co leży), i czy n+1 to kontynuuje. Gdzie wynikanie się rwie, wolno dodać krótkie
     ujęcie-pomost (reżyser 21.11, „Bonnie and Clyde”: „zobacz każde ujęcie n i sprawdź, czy n+1 i n−1 jest spójne w miarę
     z poprzedzającymi wydarzeniami… możesz dodać sceny jakieś pomiędzy łączące te dwa ujęcia — możesz, nie musisz”; 19.11:
     „raz Bonnie jest w kawiarni, nagle jest w więzieniu… musi być jakieś ujęcie pomiędzy” → pomosty „poezja” i „waco_przed”).
     Przy tym przeglądzie liczy się każda drobna uwaga reżysera (21.11: „najbardziej dla mnie są ważne te drobne uwagi!”).
2. **Skrajne położenia**: przy każdym otworze obejrzyj klatkę, w której ruchoma rzecz jest najbliżej krawędzi otworu.
3. **Automatycznie**: `python3 scripts/kontrola_ujec.py output/<film>/render.py` — szuka pustych krawędzi kadru
   (koniec świata), gasnących jasnych elementów i robi arkusz klatek do obejrzenia. W ciemnych ujęciach z winietą
   „pusta krawędź” bywa fałszywa — rozstrzyga test płótna w kolorze magenta (nienarysowane miejsce świeci na różowo).
   Po poprawkach porównaj render z materiałem w Studio na **tych samych numerach klatek** i wgraj tylko zmienione ujęcia
   (`studio_dzien.py <dzień> <projekt> tylko=…`).
   - **Ujęcie na silniku `uklad.py`** (1.32): `python3 ujecie_<klucz>.py kontrola <katalog>` — raport ze **wszystkich**
     klatek ujęcia (nie co drugiej: przy 24 kl./s pełny przebieg 10-sekundowego ujęcia to ok. minuty), 0 błędów, żadnej
     kontroli sprawdzonej w zero klatek, a pominięte tylko z powodem, który wynika z osi czasu (budowa dekoracji, punkt
     poza kadrem). Obejrzyj arkusz kontroli (klatka + rzut z góry w chwilach zdarzeń) i arkusz zbliżeń dłoni. Przy nowej
     kontroli — dowód celowym błędem (1.32). Po zmianie silnika uruchom kontrolę także ujęć już zatwierdzonych na nim
     (`ujecie_kuchnia.py kontrola`).
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
- Nie usuwaj uwag ani markerów reżysera — to jego notatki. Narzędzie wgrywające plan zostawia w polu uwag wiersze reżysera i zmienia tylko wiersz
  z rozpiski (21.11 `studio_film.py plan` nadpisywał uwagę „zmień narrację…”); przycięcie ujęcia w Studio przenosi się do rozpiski
  jako długość ujęcia, żeby następne wgranie go nie cofnęło.
- Po zmianie liczby albo długości ujęć przelicz dźwięk (muzyka i efekty na cały film) i wgraj go od nowa razem z planem —
  21.11 w Studio grały ścieżki o długości 1086,9 s przy filmie 1106,4 s: od pierwszego nowego ujęcia dźwięk się rozjeżdżał,
  a ostatnie 20 s było ciche.

### 4.2 Uwagi i markery reżysera — jak je czytać

Reżyser pisze krótko, w trakcie oglądania, często bez polskich znaków i z angielskimi słowami z wersji EN. Każda uwaga
to polecenie z jednym właściwym odczytaniem — poniżej, jak je odczytywaliśmy, kiedy reżyser przyjmował poprawkę.

**Data uwagi.** Studio zapisuje pole „Uwagi reżysera” w całości, więc po edycji jednej uwagi stare uwagi w innych ujęciach
mogą dostać nową datę (24.11 jedenaście uwag z 23.11 miało godzinę 16:01). Przed pracą porównaj tekst uwagi z raportem
poprzedniej rundy (`docs/filmy/<film>/uwagi_rezysera_<data>.md`): zrobione nie wraca do pracy, nowe są dopisane linie.

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
  dwa miejsca (np. skąd i dokąd). „Stąd rzuć monetę”, „kapelusz stąd leci do góry w tym kierunku” — początek kreski to dłoń,
  z której rzecz wylatuje, kreska to tor (1.28). Obrys rzeczy to też jej wielkość („większa teczka” — teczka w rozmiarze
  obrysu, 23.11).
- Kreska na postaci wskazuje tę postać: poprawka jest dla niej, a odpowiedź ją nazywa (23.11, ujęcie 119 „Bonnie and Clyde”:
  „jej narysuj czapkę z daszkiem” — kreska leżała na postaci w czarnym garniturze, czyli na Darbym, więc czapkę dostał on,
  z pytaniem w raporcie, czy o niego chodziło).
- Kreska leży w kadrze **ekranu na tej klatce**, z ruchem kamery, a nie w kadrze wzorcowym: punkt przelicza się przez
  kamerę ujęcia w tej chwili. Przed poprawką obejrzyj klatkę markera razem z jego kreską — zwój poprawiany „na oko”
  dostał drugą uwagę o tym samym (16.11).
- **Sekunda markera jest na osi Studio**, a od nagrania lektora ujęcie ma długość z prawdziwej kwestii, nie z tempa szacunkowego
  (akcja ujęć jest przełożona przez `render.czas_akcji`). Chwilę z uwagi albo markera zapisuje się w stałej w sekundach osi
  i przelicza przy rysowaniu `scena.rs(klucz, s)`, a w dźwięku `efekty.rr(s)` — inaczej zdarzenie mija się z markerem
  (23.11: ujęcia skróciły się nawet o 2,4 s). Każdy marker ogląda się na klatce z jego sekundy z narysowaną kreską i tekstem,
  a poprawkę sprawdza na tej samej klatce.
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
| „w klatce 240 … w klatce 273” | klatka osi Studio (30 kl./s): 240 = 8,0 s, 273 = 9,1 s od początku ujęcia; przelicz przez `scena.rs` (Kreska) |
| „od 5 s zjeżdża … aż do 6,20, a po 0,5 s podnosi” | sekundy osi Studio od początku ujęcia: początek, koniec i odstęp zdarzenia (0.4, 1.8) |
| „chodzi lewo prawo prawo lewo prawo prawo lewo dół góra” | kroki i obroty dokładnie w tej kolejności, „dół góra” — przysiad i wstanie (Hamer na ganku, 23.11) |
| „drift”, „driftować” | auto w poślizgu bokiem, z kurzem albo komiksowym dymem; na mapie stoi poziomo (1.27) |
| „Ken Burns” | powolny najazd kamery na szczegół, o którym jest kwestia (23.11, rzeka: „Ken Burns na myjący kadr głowy”) |
| „mrugaj lampą”, „zaświeć lampami z tyłu”, „lampa zaświeciła” | żarówka albo reflektor mruga kilka razy w tej chwili albo zapala się na dobre (`scena.mruganie`, `ujecia_a.swiatla` / `miga`, 1.25) |
| „…i dźwięk dodaj”, „dźwięk trąbienia”, „dźwięk hamowania” | zdarzenie dźwiękowe w tej sekundzie; jeśli w kadrze nie ma przyczyny (gwizdek, klakson), dorysuj ją (1.12) |
| „więcej wyjaśnień”, „zastanów się, czy dobrze jest narysowane całe ujęcie według opisu sceny i narracji” | przegląd ujęcia słowo po słowie kwestii: kiedy, gdzie, kto, co i jaki skutek — w kwestii i w kadrze (1.19) |
| „napraw to, co napisałem w markerach” | uwaga w ujęciu odsyła do markerów tego ujęcia — wykonaj je razem, w kolejności klatek |
| „muzyka weddingowa”, „zmień muzykę” | temat muzyki z treści sceny (Podręcznik → Dźwięk, „Muzyka”) |
| „nic się nie dzieje”, „nikt się nie rusza” | ujęcie bez wydarzenia (1.8, Rytm 1) — albo podgląd na żywo jeszcze go nie przeliczył i gra zapasowa klatka; sprawdź jedno i drugie, zanim odpowiesz |

**Kiedy nie wiadomo.** Jeśli tekst i kreska dają dwie różne poprawki, zapytaj reżysera jednym pytaniem z obiema
możliwościami, zanim narysujesz; zgadnięta poprawka wraca jako druga uwaga. Jeśli poprawka przeczy faktom filmu, napisz, co
mówią źródła, i zaproponuj obraz zgodny z nimi (19.11, Ohio: reżyser zaproponował tam Bonnie, a w Ohio złapano Clyde'a —
po wyjaśnieniu został Clyde).

**Po wykonaniu.** Marker zostaje w Studio. Reżyser dostaje odpowiedź przy każdym markerze (zrobione albo pytanie),
a każda tura ma raport `docs/filmy/<film>/uwagi_rezysera_<data>.md`: zmiany wspólne, tabela „ujęcie · marker albo uwaga ·
zrobione”, co sprawdzono i co zostaje do decyzji reżysera (reżyser 23.11: „opisz te błędy, moje uwagi i poprawki do pliku”).
Raport poprzedniej tury jest też miarą przy następnej (Data uwagi).
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

### 5.6 Lekcje z „Bonnie and Clyde” (24–25.11.2026)
Skrypt: `output/bonnie-i-clyde/miniatura.py` (warianty C, D, E, G; `postac_k` / `duza` rysują lalki filmu w skali ekranu,
`twarz` dokłada minę, `zaslona` przyciemnia albo barwi samo tło — `J.glow` w zwykłym trybie prawie nie kryje).
- **Plan ogólny w beżach się nie klika.** C i D (cała scena, ciepłe beże) dały po 18 h CTR 2,1 % przy 3,2 % „Syna słońca”:
  w 320 × 180 twarze nie mają miny. Następne warianty to **zbliżenie dwóch twarzy z wyraźną miną na ciemnym albo barwnym
  tle** (E: zasadzka, Bonnie i Clyde do pasa z krzykiem; G: ciemnia w czerwonym świetle, Bonnie mruga z cygarem — ciemnię
  wybrał reżyser). Zasada 5.1 (zbliżenie) obowiązuje także wtedy, gdy kusi plakat z całej akcji.
- **Plakat z akcji (D) — poprawki reżysera**, gdy już jest: rekwizyty z ujęcia filmu w jego skali („krzaki są za duże —
  weź te krzaki z tego ujęcia… dużo mniejsze”), aktorzy pierwszego planu nisko, żeby było widać temat „w całej okazałości”;
  bohaterowie w rozkroku i „dużo większy napis”; auto niżej, tak żeby schować tylne koła; postacie z dołu wynurzone o ok.
  10 % i z kapeluszami w uniesionych dłoniach pod ok. 45°; rzecz w dłoni z białym obrysem, żeby odcinała się od pola
  („czapki weź jakoś bardziej odznacz, może biała obwódka”); grubsze litery napisu; w tle rozmyte drobiazgi epoki (kaktusy).
- **Bez cudzych znaków towarowych.** GTA 6 może być w tytule, ale w miniaturce nie ma grafik z gry.
- **Test A/B miniaturek** (Studio YouTube → Test & Compare): najwyżej 3 warianty — nowy wariant zastępuje stary, nie
  dochodzi; każdy tytuł idzie w parze z miniaturką, która pokazuje to, co tytuł obiecuje. Przy ok. 120 wyświetleniach
  miniatury na wariant test nie wyłoni zwycięzcy; wyniki czyta się po 7 i 28 dniach (Podręcznik → Publikacja).

## 6. Skąd te zasady

Od pilota (29.10.2026) i „Oddziału C” (3.11) przez „Pierwszego cesarza” EN (16.11) i „Syna słońca” EN (18.11) do „Bonnie and
Clyde” EN (19–27.11); wiersze w kolejności dat. Źródła:
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
| Wariant A, rig dni 1–30 (11.11) | łza, uśmiech, nadęte policzki i słuchawka dorysowane po twarzy w stałym miejscu odklejały się od głowy, gdy głowa dostała ruch (znalezione w kontroli; rysuje się je w `kit_a.on_face`) | 1.4, 1.5 |
| Wariant A, rig dni 1–30 (12.11) | „oko dziwnie wygląda” w widokach z profilu: po skręcie głowy jedno oko lądowało na obrysie; w oddali twarze jak kleksy (gruba kreska zbliżenia i drżenie na małych oczach) — „wzoruj się na zbliżeniu” | 1.30 |
| Wariant A EN, przegląd całego filmu (13.11.2026) | „za szybko się kończą zaraz po kwestii, albo mówi i w połowie się ucina”: ujęcia liczone pod polskie kwestie, angielskie nagrania dłuższe — 124 z 287 kwestii kończyło się 0,25 s przed cięciem, 27 bez oddechu przed, d01_18 za cięciem; film dni 1–30: 36,8 → 40,3 min | 1.9 |
| Wariant A EN, przegląd (13.11.2026) | „ktoś przechodzi przez ramę drzwi, a powinien być nad nią”: dalsza framuga przecinała narratora już na korytarzu (d01_12), framuga dzieliła twarze w pół kroku, ręka Henryka szła przez wnętrze ściany (d14_12); skrzydło drzwi izolatki wystawało za ościeżnicę i znikała podłoga (d16_16) | 1.1, 1.5 |
| Wariant A EN, przegląd (13.11.2026) | stopy przed biurkiem/stołem, a blat przecinał tułów (d01_02, d02_16, d22_02, d26_01, d29_08); widok za oknem łącznika jako płaski prostokąt na oknach w perspektywie (d13_12) | 1.1, 1.5 |
| Wariant A EN, przegląd (13.11.2026) | słuchawka wisiała przy uchu bez dłoni (d20, d21, d25, d26, d28, d29 — ok. 20 ujęć); dłoń bez ręki na kieszeni (d15_08); ręka „kogoś trzeciego” spod kadru zamiast od barku Henryka (d23_08) | 1.4, 1.31 |
| Wariant A EN, przegląd (13.11.2026) | paczka z drona lądowała gdzie indziej, niż leży w następnych ujęciach (d10_01); oko i nos odwracającego się zarażonego nie szły za kołysaniem głowy (d10_14); obrót z przodu na plecy bez profilu (d30_16); „He's clear” o Zosi (d30_10) | 1.2, 1.4, 1.6 |
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
| Syn słońca EN, otwarcie (18.11, reżyser) | po zapowiedzi brak ściemnienia i kurtyny startu; hak zaczynał się od akcji bez słowa, o czym jest film („z dupy jest wprowadzenie”); po strzale od razu woda bez ujęcia pomiędzy; najazd z kwestią o pierwszym cesarzu pokazywał brata, który ginie (przegląd scenariusza); kurtyny aktów bez pytań | 1.26, 1.15 |
| Syn słońca EN, przegląd scenariusza (18.11, wykonawca, zatwierdzone przez reżysera) | hak i ciało filmu powtarzały te same zdania; śmierć cesarza brzmiała jak koniec filmu; brak pomostu z haka do mitu; brak ciszy przed szczytami | 1.26, 1.23 |
| Syn słońca EN, akty 3–5 (18.11, reżyser: 3 uwagi, 16 markerów) | brak reakcji na mocnych chwilach (tabliczki „help”, „hmm..”, „stop!” z ręką do góry, „no way!”, „aaa!”, „I can't..”, „aaaa”, „brother!”, „boo!”); leżąca głowa i brat bez ruchu („porusz go”, „niech skacze”); wiosłuje tylko część łodzi; miecz obok dłoni Ninigiego („miecz ma być tutaj”); słońce ucięte krawędzią; zwrot ku słońcu niewidoczny; Iwarebiko tylko wskazuje góry („strzel tu strzałą”); po stracie braci stoi bez gestu („podnosi ręce”); za krótkie końcówki zejścia Ninigiego i wejścia w las Kumano | 1.25, 1.20, 1.18 |
| Syn słońca EN, ujęcia 58–85 (19.11, kontrola na prośbę reżysera) | bitwa: lektor mówi o walce Iwarebiko z Nagasunehiko, a widać same czubki włóczni za pasmem wzgórz, bez ludzi i bez obu wodzów; błysk złotego ptaka prawie niewidoczny; po przestawieniu śledztwa mapa wysp wisiała już w tle pieczęci, a w następnym ujęciu zjeżdżała drugi raz; „restored in 1966” bez śladu w obrazie | 1.5, 1.17, 1.19, 1.2, 1.23 |
| Syn słońca EN, akty 3–9 (20.11, reżyser: 7 uwag, 35 markerów) | stojące głowy węża (mają się ruszać i gryźć); miecz „wyrastał” z ziemi zamiast z ogona — ma wyjechać od dołu przez ogon; rzeczy bez reakcji i bez życia: wymachiwanie mieczem, sztylet wodza, piorun w łódź, bariera przed piorunem, wiewiórka, niedźwiedź staje i straszy, miecz rzucony i złapany, piłka i wrona, pułapka spada na głowę zamiast „znikania”, strzały-ciężary; brak ciągłości: żołnierze z bitwy znikali przy złotym ptaku, płonące strzały nie płonęły dalej, zwój znikał ze stołu, pęknięty filar bez naprawy w następnych ujęciach; napisy: „lived 127 years!”, „nowadays, in 2019” | 1.2, 1.6, 1.21, 1.25 |

| Bonnie and Clyde, arkusze aktów II–VIII (19.11, kontrola wykonawcy) | lalki i auta stały na płótnie, zanim wyrosła dekoracja; nogi pasażerów pod Fordem; sylwetki tancerzy z „X” na tułowiu; Ford w błocie zasłonięty pasem błota, a muły bez jeźdźców; cela zakryta gęstymi kratami; czapki zabitych, trumny i rzeka schowane za rampą; gazeta na twarzy Bonnie; Clyde „czyścił” karabin wycelowany w Bonnie; Ford z mostu znikał pod sceną po obrocie i za płomieniami; wycinki do teczki leciały poza kadrem | 1.27, 1.2, 1.1 |
| Bonnie and Clyde, kontrola końca świata i przegląd dźwięku (19.11) | przy budowie wnętrza pod ścianą świeciło puste płótno (14 ujęć); wyrastające domki i pinezki miały w jednej klatce wysokość 0 i klatka się wywracała | 1.3, Animacja kodem |
| Bonnie and Clyde, otwarcie (19.11, reżyser) | „jest 5 s spoiler, najlepiej zrób go 6 s i szybko zmieniaj ujęcia… a potem w tym filmie dowiecie się blablabla… i kurtyna i znowu od nowa tak jakby?” — trzy starty: długa kurtyna tytułu, lista obietnic, kurtyna aktu I z powrotem w czasie; w zapowiedzi podpis zdradzał łowcę | 1.26 |
| Pierwszy cesarz EN, wyniki po 1 dniu 20 h (19.11, reżyser) | po 30 s ogląda 35 %, średnio 1:29 z 11:19: pusta rama z tytułem na starcie, chronologia „Long ago…” bez haka, pięć nazw w 40 s, kurtyna aktu w 1:18 | 1.26, Rytm |
| Bonnie and Clyde, ślub (19.11, marker reżysera) | „znika to i po łuku napis pod tymi kwiatkami Happy Ever After” — tabliczka z sercami zjeżdżała na górę łuku z kwiatów i go zasłaniała; pod łukiem brakowało napisu | 1.27 |
| Bonnie and Clyde, 21 markerów (19.11, reżyser) | broń w złą stronę w prologu; ręka zza kadru podaje cygaro; klisza wysuwa się w bok zamiast w dół; gazeta płynnie zmienia się w kulkę; chłopcy obok ciężarówki zamiast na pace; Bonnie nie trzyma dzbanka i nie leje do filiżanki; gazeta obok rąk; ciemne 5 s na początku Eastham po turbo krótkich ujęciach; Bonnie „nagle w więzieniu” (brak ujęcia pośredniego przed aresztem w Waco i niejasna ucieczka); siekiera nie spada z góry; przysięga za długa i bez ruchu | 1.27, 1.28 |
| Bonnie and Clyde, akt I (19.11, reżyser) | „dlaczego z ujęcia 21 o jakichś indykach robi się nagle w 22 ślub? to nie ma sensu” — przy skracaniu aktu I wypadło ujęcie szkoły, które było pomostem od Clyde'a do Bonnie; kwestia ślubu zaczynała się bez „tymczasem” | 1.27, Rytm |
| Bonnie and Clyde, gagi (19.11, reżyser) | „więcej gagów i musisz poprawić ich umiejscowienie w rękach szczególnie” — karabiny łowców w X, gazety obok twarzy, łyżka obok garnka, laska w górę, miarka w powietrzu, kieszenie jako kwadraty, ręka maszynisty jak patyk, kapelusz nad maską | 1.27 |
| Bonnie and Clyde, próbka głosów (19.11, reżyser) | „wygląda to jakby dwie historie nachodziły na siebie… na 2:48 jak kurtyna wjeżdża, pojawiają się dwie różne tabliczki po sobie” — próbka była zlepkiem fragmentów z różnych aktów bez plansz (kurtyna aktu III, zaraz potem akt VIII); w filmie cztery sceny w tym samym miejscu budowały się od pustego płótna | 1.27 |
| Bonnie and Clyde, recenzja 114 ujęć (19.11, kontrola wykonawcy na prośbę reżysera) | lustrzane „EXTRA!” na przewracanej stronie i „SHERIFF” na aucie jadącym w lewo; „THE OUTLAWS MADE OF PAPER” i „BONNIE AND CLYDE” wystawały poza tablice; w zapowiedzi na 0,1 s mignął podpis Hamera; teczka, kapelusz, karabin, puszka i list wisiały nad pustym płótnem w czasie budowy; Bonnie „niesiona” wisiała za plecami Clyde'a; karabin „na kolanach” stojącego Clyde'a; podpis Buchera poza kadrem, W.D. podpisany już w aucie, „undertaker” w podpisie 8 s przed puentą; kanapka za karoserią, teczka i „HA HA HA!” pod napisem; nazwy cmentarzy za żałobnikami; „SEE THE DEATH CAR” biały na białym pasie | 1.27 |
| Syn słońca EN, zapowiedź i hak (20.11, reżyser) | burza i wąż były w zapowiedzi, zaraz potem w haku (ujęcia 15 i 17) i jeszcze raz w ciele filmu — „czemu nie tylko 2 razy?” | 1.26 |
| Bonnie and Clyde, 28 markerów i uwaga (21.11, reżyser) | rewolwer znikał z dłoni, kiedy ta sama ręka wyjmowała cygaro z ust; strzał padał poza kadrem; chłopak dawał cygaro Bonnie do ręki zamiast do ust; gazeta klienta na głowie i w tułowiu; łyżka obok garnka; serca pośrodku zamiast nad każdym z zakochanych; „pod płaszcz” bez płaszcza; Clyde znikał przy wsiadaniu do auta; kwestia „palce” mówiła o czym innym niż obraz; plan nadpisał uwagę reżysera, a dźwięk nie poszedł za nowymi ujęciami | 1.11, 1.20, 1.27, 1.28, 4.1 |
| Bonnie and Clyde, 91 markerów i 13 uwag (23.11, reżyser) | tabliczki zjeżdżały dopiero w sekundzie markera i nie tam, gdzie kreska; kapelusze były wklejone w głowę (zdjęcie = podmiana lalki); scena za parawanem w Platte City i Sowers nie mówiła kiedy, gdzie i kto; ekran kina i zdjęcie stały nieruchomo; rzeczy rzucane brały się znikąd; słońce, lampy i światła aut nie grały; Gault bez cechy, po której się go rozpozna | 1.19, 1.20, 1.25, 1.28, 4.2 |
| Bonnie and Clyde, 21 markerów, uwagi i czat (24.11, reżyser) | spód auta znikał w każdym ujęciu z kurzem (półprzezroczysty kolor podmieniał alfę wycinka); suknia Maree z dwóch części; ujęcia 20, 118 i 119 statyczne, „nic się nie dzieje”, a śpiąca rodzina z opisu ujęcia 20 leżała schowana za rampą; czapki leżały od pierwszej klatki zamiast spaść; saksofon przy ręce, nie przy ustach; nić na mapie zwisała z dwóch kropek; brakowało dźwięków przy miauczeniu, trąbieniu, gwizdkach i hamowaniu | 1.8, 1.12, 1.25, 1.28, 1.29, 4.2 |
| Bonnie and Clyde, przegląd wszystkich markerów i uwag filmu (27.11: 169 markerów z 19–24.11, 17 uwag, czat) — markery w ujęciach 36–43 (19.11) | reżyser rozpisał gag przed stacją jako ciąg z chwilami („Bonnie wysiada… on po 1 s odjeżdża… Bonnie biegnie, wyciąga Clyde'a z auta, a auto z kurzem samo odjeżdża… u góry tabliczki let's rob it”, „możesz wydłużyć tę scenę”); z rabunku stacji „zamień na 1 banknot”; z ugrzęźniętego Forda mieli „wyskoczyć (przez dach jakby)”, a policja „iść na nich za kadr powoli”; po strzale Clyde bez gestu („rękę podnosi do góry i dmucha w dym z rewolweru”); „nie widać tabliczki” w Atoce; auto na postoju martwe („ruszaj tym autem, jakby minimalnie chciało jechać, ale jest na ręcznym”); Eastham zaczynał się 5 s ciemności po dwóch „turbo krótkich” ujęciach | 1.8, 1.25, 1.27, 1.28 |
| Bonnie and Clyde, czat (19.11 i 21.11, reżyser) | „raz Bonnie jest w kawiarni, nagle jest w więzieniu… musi być jakieś ujęcie pomiędzy”; „zobacz każde ujęcie n i sprawdź, czy n+1 i n−1 jest spójne… możesz dodać sceny pomiędzy”; Ohio: propozycja Bonnie wbrew faktom (złapano tam Clyde'a), wyjaśniona przed zmianą | 3.1 (pary cięć), 4.2 |
| Bonnie and Clyde, markery 23.11 (czego nie objął wiersz z 23.11) | Bonnie niesiona na wyciągniętych rękach, a miała wisieć przez bark głową w dół; wiązanie drutem rysowane wprost, a miało zniknąć w obłoku „jak w bajkach”; kapelusz z dziurą spadał jak kamień („niech fruwa”), kartka miała latać 4 s; auta na mapie obracały się wzdłuż drogi i nie driftowały; mapa za nisko w kadrze; chwile w klatkach osi Studio („w klatce 240… 273”) i kroki „lewo prawo prawo lewo”; „tabliczka maminsynek po angielsku”; kreska na postaci w czarnym garniturze (czapka z daszkiem) | 1.12, 1.13, 1.20, 1.27, 4.2 |
| Bonnie and Clyde, 24.11 (czego nie objął wiersz z 24.11) | noc i dzień zmieniały się przez cięcie albo wcale (ujęcia 20–21: „słońce na księżyc… z ciemności i księżyca zmienić na słońce”); karta z aktami znikała z teczki w jednej klatce; dym po zasadzce rzedł za szybko („dłużej dym”); reżyser dopisał znaki: oczy „< <”, nuty nad saksofonem, gwiazdy; napisy lektora wypalone w obrazie („usuń te napisy”) | 1.2, 1.6, 1.13, 1.20, 1.22, 1.25 |
| Miniaturki Bonnie and Clyde (24–25.11, reżyser i wyniki po 18 h) | plan ogólny w beżach (C, D) — CTR 2,1 % przy 3,2 % „Syna słońca”, w 320 px nie widać min; w plakacie D krzaki za duże, auto za wysoko, czapki w dłoniach ginęły na polu; Test & Compare przyjmuje najwyżej 3 warianty | 5.6 |
| Bonnie and Clyde, ujęcie 25 „kuchnia” (27.11, reżyser) | „model AI nie do końca wie, kto trzyma co w ręku, kto jest za czym” — Clyde wjeżdżał zza krawędzi kadru obok zamkniętych drzwi (dźwięk drzwi był, drzwi się nie otwierały), „uchylał” kapelusz pustą dłonią nad głową (sztywna ręka z jednym zawiasem nie sięga własnej głowy), stół stał za aktorami jak ława | 1.1, 1.2, 1.32 (nowa; silnik `uklad.py`) |
| Bonnie and Clyde, ujęcie 24 „kawiarnia” (27.11, kontrola silnika `uklad.py` — nie marker reżysera) | kontrola „stoi na blacie” przechodziła, kiedy filiżanki jeszcze nie było, a kontrola styku zielska nie trafiła w żadną klatkę; przy krawędzi kadru kontrola mierzyła brzeg kadru zamiast dna; dzbanek z zestawu ma ucho 17 px obok korpusu; przez szparki w ladzie prześwitywała Bonnie; gazeta klienta zasłaniała filiżankę (82%); dzbanek kołysany wokół środka dna wchodził 3 px w blat; dzbanek i gazeta prześwitywały w dłoniach wysuwających się lalek | 1.12, 1.22, 1.27, 1.28, 1.29, 1.32, 3.3 |
| Imam / Diuna, cały film (28.11, reżyser) | Nowy film zaczęty od zestawu „Bonnie and Clyde” sprzed ujęcia „kawiarnia”: 76 ujęć bez `uklad.py` — rzeczy w dłoniach, siedzenie i kto za czym ustawione na oko, sprawdzone tylko arkuszami po 4 klatki; reżyser: „miałeś się zastosować do wszystkich wytycznych od najnowszych po najstarsze obowiązujące” | Wstęp: najnowszy silnik także z gałęzi roboczej, wytyczne od 1.32 w dół przed pierwszym ujęciem; 1.32 i 3.3 w każdym ujęciu z rzeczą w dłoni, siedzeniem albo otworem |
| Imam / Diuna, pierwsza minuta wersji D (28.11, reżyser) | Ujęcia z kwestią 6–10 s, w których lalka tylko stoi, przeplatane samotnymi wstawkami 0,4–2,4 s bez słów; ciągle te same szare góry; otwarcie z dwóch kart z cytatem („nic nie wiadomo, o co chodzi”); jeden gag w całym filmie; film przycięty do 4–5 min — „przebuduj to… ludzie mają to oglądać” | 1.9 „Rytm filmu”: ujęcie = kwestia + 2–4 wydarzenia na słowach, bez samotnych wstawek, długość z historii, `kontrola_rytmu()`; Humor: silnik humoru i lista gagów przed rozpiską; Rytm „Początek filmu”: otwarcie od tego, co widz zna |
| Imam / Diuna (28.11, kontrola `uklad.py` i przegląd z wytycznymi — nie marker) | Burta wozu, okno kibitki, grzbiet wielbłąda i blat stolika liczone z nieprzyciętego arkusza (wycinek jest przycięty do papieru) — wóz zasłaniał księżne w całości; jeździec wysuwał się osobno od konia (biodro 18–99 px od siodła w pierwszych 0,3–0,9 s); karabin z czerwoną opaską czapki z daleka jak krzyż; kibitka, wozy i armaty jechały bez koni i woźnic; w jednym kadrze ta sama lalka murida i oficera po kilka razy; podpisy zjeżdżały do 1,3 s przed imieniem | 1.28/1.32: punkt arkusza w kadrze tylko przez arkusz `Ark` (`uklad_kz.pkt`), jeździec wjeżdża razem z koniem; 1.6: znak czytany z daleka jako symbol nie wchodzi do kadru, pojazd ma konia i woźnicę, grupa z różnych lalek; 1.27: podpis na słowo, liczony z tempa kwestii |

| Imam / Diuna, 2 minuty szkicu E (28.11, reżyser) | Od 0:40 do 4:00 prawie każde ujęcie na tym samym paśmie gór (7 ujęć Achulgo i 4 w Gimry na jednej dekoracji), góry także za lasem, dworem i Kaługą; gabinet cara złożony z tapety, okna, podłogi i biurka „Bonnie and Clyde” | 1.33 |
| Imam / Diuna, lektor (28.11, reżyser) | Kwestia haka powtarzała zdanie z „Pierwszego cesarza” („handed … to the enemy as a hostage”), a „It all starts in…” i „So how did…” stały już w „Synu słońca” i „Bonnie and Clyde” | Podręcznik → Jak pracujemy, krok 4 (`scripts/powtorzenia_kwestii.py`) |

Otwarte: słuchawka w „Starym telefonie” nie ma kabla do aparatu, a po spadnięciu telefon dzwoni dalej (świadomie,
dla ciągłości z następnym ujęciem) — do decyzji reżysera.
