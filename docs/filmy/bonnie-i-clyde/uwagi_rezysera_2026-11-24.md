# Bonnie and Clyde — uwagi, markery i czat reżysera z 24.11.2026: co zrobiono

Projekt Studio `prj_dad935cf1d7446fa`. Reżyser zostawił **21 markerów** (15:33–16:11) i dopisał uwagi w ujęciach 23, 116, 117,
118 i 119. W czacie dodał: spody aut w kilku ujęciach nadal znikają; 118 i 119 stoją, „nikt się nie rusza”; w ujęciach 20–23
dodać efekty i zmienić muzykę; ujęcie 20 jest nudne — w połowie słońce na księżyc, noc, gwiazdy; w ujęciu 21 z nocy na słońce.
Lista do pracy: `scripts/uwagi_rezysera.py prj_dad935cf1d7446fa --od 2026-11-24`.

**Uwagi z godziną 16:01 w ujęciach 19, 32, 67, 68, 69, 71, 73, 74, 75, 78, 84 i 104 są stare** (z 21.11 i 23.11, zrobione —
`uwagi_rezysera_2026-11-23.md`). Studio zapisało pole uwag w całości i podbiło im datę. Nowe są tylko dopisane linie.

Wszystko jest w kodzie ujęć (Studio rysuje je na żywo). Długości ujęć się nie zmieniły (film nadal 18:19,0, 119 ujęć);
muzyka i efekty przeliczone na cały film i wgrane od nowa.

## Zmiany wspólne

- **Spód auta** (czat, marker 96): wariant Forda „w kurzu” (`zestaw_bc.ford(kurz=True)`) rysował kurz `ImageDraw` z kolorem
  półprzezroczystym, który podmieniał piksele razem z alfą — dół karoserii robił się przezroczysty i spod niej wystawały nogi
  pasażerów. Teraz kurz to warstwa nałożona na wierzch, tylko na blachę. Poprawka działa w każdym ujęciu z kurzem (6 ujęć).
  Nowa zasada: Wytyczne 1.29.
- **Noc w trakcie ujęcia** (`scena.niebo` z `w.zmierzch`, `scena.gwiazdy`, `west_dallas(chmury_k=)`): papier nocy kładzie się
  na papier dnia, chmury unoszą się na nitkach i odsłaniają księżyc i gwiazdy; gwiazdy z papieru zjeżdżają po kolei i migoczą.
- **Oczy „< <”** (`zestaw_bc`, `oczy="mniejszosc"`, lalka `detektyw_oo`).
- **Nowe wycinki**: nuta (`J.nuta`), odbitka z czarną Bonnie (`J.odbitka_bonnie`), suknia ślubna z jednego kawałka
  (`rek("suknia_cala")`).
- **Muzyka**: nowe tematy w `efekty.py` — kołysanka z pozytywki (`kolysanka`), walczyk salonowy (`walc`), marsz weselny na
  organach (`slub`, melodia chóru weselnego z „Lohengrina” Wagnera, domena publiczna). Nowe dźwięki: świerszcze od zmroku,
  „ta-da”, strzał 8-bit (`pew`), deszcz.

## Lista: ujęcie, marker albo uwaga, co zrobiono

| Ujęcie | Marker / uwaga | Zrobione |
|---|---|---|
| 14 hak_joplin_rzeczy | 7,07 s „zrób mu z kulek oczu na chwilę znaki mniejszości, jakby patrzał na te zdjęcia, że woo < <” | przez 1,3 s od tej sekundy oczy policjanta to dwa „<”, usta „o” |
| 20 wagon | czat: „zbyt nudne; w połowie zmienić słońce na księżyc, ściemnić na noc, dodać gwiazdy” | słońce drży i ucieka (marker 23.11), od 8,5 s zapada noc: chmury wjeżdżają w górę, zjeżdża księżyc i gwiazdy na nitkach; tabliczka „DEVIL'S BACK PORCH” na kwestię; pranie kołysze się między szałasami; śpiąca rodzina jest teraz widoczna pod wozem (leżała schowana za rampą) z „Z” nad głowami; ćma z pudełka leci do księżyca i krąży wokół niego |
| 21 indyki | czat: „z ciemności i księżyca zmienić na słońce” | ujęcie zaczyna się nocą z 20, księżyc i gwiazdy odjeżdżają w górę, zjeżdża słońce, robi się dzień; indyki gulgoczą o świcie |
| 20–23 | czat: „dodać efekty i muzykę zmienić” | 20 kołysanka (pozytywka), świerszcze od zmroku, księżyc na nitce, dzwonki gwiazd, trzepot ćmy; 21 ragtime, świerszcze i gulgot o świcie; 22 walczyk, kartka, „ta-da” przy ukłonie Bonnie; 23 marsz weselny, dzwony, serce; od 24 wraca blues |
| 23 slub | „muzyka weddingowa” | marsz weselny na organach (temat `slub`) |
| 44 buck | 5,70 s „miauu! (i dźwięk dodaj)” | piesek Blanche podskakuje jej w rękach i miauczy: tabliczka „MEOW!” nad nim, dźwięk kota |
| 46 joplin_karty | 0,00 s „bierze do buzi i gra, a nad nim nuty” | Clyde podnosi saksofon ustnikiem do ust, dłoń na korpusie (ręka w skrócie), z czary lecą nuty; po „SHHH!” chwilę milknie |
| 48 joplin_ofiary | 0,00 s „spada czapka”, „spada druga czapka” | obie czapki spadają z góry po liniach z markerów, koziołkują i lądują; dźwięk |
| 49 joplin_rzeczy | 5,70 s „tu te same oczy z tamtej sceny co na początku filmu” | jak w ujęciu 14: oczy „< <” od tej sekundy |
| 50 ciemnia | 8,97 s „u góry różne odbitki Bonnie, czarne” | na sznurku pod sufitem siedem odbitek, na każdej czarna Bonnie w innej pozie |
| 53 darby_auto | 3,83 s „dźwięk trąbienia” | klakson w tej sekundzie |
| 54 darby_tyl | 0,60 s „błoto spod kół wylatuje z buksowania” | spod tylnego koła łukiem w tył leci błoto; dźwięk błota |
| 59 wellington_noc | 5,17 s „mrugają światła i po chwili się psują” | reflektory mrugają, iskra i gasną na dobre — dlatego nikt nie widzi tablicy DETOUR; kliknięcia i „pff” |
| 61 wellington_bonnie | 0,00 s „przybliż go do nich dwóch” | Clyde stoi tuż przy Bonnie i W.D., jego dłoń trzyma Bonnie pod ramię |
| 86 mapa | 6,87 s „linia ma być prowadzona z jednej kropki, a nie z dwóch” | pęknięta nić zsuwa się z dużej kropki i zwisa tylko z górnej; po supełku biegnie znowu od tej jednej kropki |
| 88 grapevine | 7,17 s „zrób, że mają gwizdki i dźwięk gwizdka” | obaj motocykliści mają gwizdki w ustach i dmuchają dwa razy (podmuch przy gwizdku); dźwięk gwizdka |
| 90 tullis | 1,80 s „napraw suknię, ma być w jednej całości”; 8,47 s „tu połóż tego kwiatka” | suknia z jednego kawałka od ramion do trawy; kwiatek ląduje na wieku trumny w punkcie z kreski, dłoń Maree tam sięga |
| 96 boyd_tab | 2,27 s „napraw spód auta, bo zniknął” | spód auta wrócił (zmiana wspólna, wyżej) |
| 102 shreveport | 8,13 s „tu go postaw i za tymi białymi kreskami” | sylwetka Henry'ego w lewej części okna, za białymi szczeblami; stoi w oknie fasady, a nie w miejscu ekranu |
| 106 kanapka | 0,00 s „przesuń kanapkę minimalnie w lewo, do ust” | lewy koniec kanapki przy ustach Bonnie |
| 107 zwolnienie | 0,67 s „dźwięk hamowania” | pisk hamulców |
| 109 dym | 3,77 s „dłużej dym” | dym z papierowych kłębów unosi się znad auta przez całe ujęcie i rzednie dopiero pod koniec |
| 112 pogrzeby | 6,43 s „zaczyna padać deszcz, ale jest słonecznie nadal” | od tej sekundy pada deszcz przez całą scenę, słońce zostaje; dźwięk deszczu |
| 116 film_hamer | „od 10 s daj jeszcze jedno jakieś ujęcie na płótno” | od 10 s trzecia scena filmu: kronika, wirująca gazeta „HAMERS SUE STUDIO” (na „so his family sued the studio”) |
| 117 gra | „na końcu wyskakują i strzelają oboje kulami pikselowymi, i troszkę skróć tę jazdę auta” | jazda 2,8 s zamiast 4,6 s, rów i wyskok wcześniej (5,4 s); od 6,2 s plecami do siebie strzelają pikselowymi kulami w obie strony, przy lufie błysk; dźwięk 8-bit |
| 118 koniec | „napraw to ściąganie w dół na linkach, to co napisałem w markerach”; czat: „statyczne, nikt się nie rusza” | teczka w rozmiarze z obrysu markera; karta zjeżdża powoli, a o 9,5 s schodzi na linkach za teczkę i zostaje w niej (wcześniej znikała w jednej klatce); do tego: z pustej kieszeni Clyde'a wylatuje ćma (klamra z West Dallas), na „nine dead lawmen” zjeżdża dziewięć czapek, na „brought them down” pieczątka CASE CLOSED, kurtyna zasuwa się, kiedy kończy się kwestia |
| 119 dzieki | „napraw to ujęcie, bo nic się nie dzieje”; czat: „nikt się nie rusza” | lalki wchodzą z obu stron, kłaniają się falą (każdy zdejmuje nakrycie głowy ręką i trzyma je przy boku), z widowni lecą kwiaty i lądują im pod nogami, na „support me” nad każdym serce, Bonnie macha beretem; potem gag z kurtyną |

## Sprawdzone

- Każdy marker obejrzany na klatce z jego sekundy przed i po poprawce (arkusze i zbliżenia).
- `render.py kontrola` (pusta krawędź kadru) dla wszystkich poprawionych ujęć.
- Kontrola ciągłości: 0 błędów wagi 3; zostaje ostrzeżenie wagi 2 o długości aktu IV (170 s, wydłużony na prośbę reżysera 23.11).

## O podglądzie 118 i 119

Podgląd na żywo liczy oba ujęcia poprawnie (ruch był w kodzie także przed poprawką). Jeśli Studio pokaże je nieruchome,
to znaczy, że podgląd jeszcze ich nie przeliczył i gra zapasowa klatka z osi — po chwili odświeża się sam.
