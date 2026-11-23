# Bonnie and Clyde — uwagi i markery reżysera z 23.11.2026: co zrobiono

Projekt Studio `prj_dad935cf1d7446fa`. Reżyser zostawił **91 markerów** (ujęcia 20–119, 11:44–13:27) i **13 nowych uwag
w ujęciach**. Czternasta uwaga, przy „palce” („zmień narrację…”), jest z 21.11 i była już zrobiona: kwestia mówi o siekierze
na stopie, a zwolnienie jest w ujęciu „parol”. Lista do pracy: `scripts/uwagi_rezysera.py prj_dad935cf1d7446fa --od 2026-11-22`.

Wszystko jest w kodzie ujęć: Studio rysuje je na żywo. Sekundy z markerów są na osi Studio, czyli w ujęciu z prawdziwym
nagraniem lektora. Kod przelicza je na czas akcji przez `scena.rs(klucz, s)`, a dźwięk przez `efekty.rr(s)`, więc zdarzenie
wypada dokładnie w sekundzie z markera.

## Zmiany wspólne (działają w każdym ujęciu z tą rzeczą)

- **Tabliczka z markera** wisi w miejscu kreski i już w jego sekundzie (`ujecia_a.tab_tu`; zjeżdża 0,7 s wcześniej).
- **Nakrycie głowy zdejmuje się ręką**: dłoń idzie do czubka głowy, kapelusz przechodzi do dłoni w jednej klatce, potem
  wraca na głowę albo zostaje w dłoni przy boku (`ujecia_a.kapelusz_reka`; lalka bez kapelusza i sam kapelusz z tego samego
  rysunku: `Figura.bez_kapelusza`, `Figura.kapelusz`). Użyte u Gaulta (104), Hamera w „dym” (109) i u wszystkich w ukłonach (119).
- **Słoma w ustach Gaulta** jest we wszystkich ujęciach, w których Gault się pojawia (`scena.SLOMA`).
- **Mapa w biurze Hamera wisi niżej** i po niej cały czas jeździ w poślizgu mały Ford (`_biuro`, ujęcia 80, 81 i 97).
- **Ciężarówka na lewarku** obraca się wokół tylnego koła, które stoi na ziemi, a przód wisi wyżej (`scena.ciezarowka`,
  ujęcia 105, 107 i dalsze).
- **Linia granicy stanów** to biała linia namalowana w poprzek drogi przy tablicy (`linia_granicy`, ujęcia 85 i 96).
- **Mruganie lamp i świateł auta**: `scena.mruganie` + `wnetrze(jasnosc=…)` dla żarówek, `ujecia_a.swiatla` + `miga` dla
  reflektorów i tylnych lamp Forda.
- Dźwięk: tabliczki, podpisy i błyski słychać teraz w chwili, w której są w obrazie także w ujęciach z nagranym lektorem
  (wcześniej mogły się minąć o ułamek sekundy). Tak samo liczy się cisza przed szczytem.

## Ujęcia

| Ujęcie | Marker / uwaga | Zrobione |
|---|---|---|
| 19 obietnica | „auta mają być poziomo, a za nimi taki komiksowy dym” | Fordy jadą poziomo, za nimi papierowe kłęby jak w kreskówce |
| 20 wagon | 7,93 s „dźwignij powoli słońce za kadr, bo ono też się boi” | słońce drży i powoli wjeżdża na nitce za górną krawędź; dźwięk |
| 22 poezja | 1,67 s „daj jej pióro gołębia do pisania” | w uniesionej ręce szare pióro gołębia, zeszyt w drugiej |
| 64 drzewo | 1,57 s Bonnie wiąże, chmura na środku ciał, po 1,5 s wskakuje do auta | Bonnie przy przywiązanych macha rękami w komiksowym obłoku z gwiazdkami (0,6–2,8 s); w 3,07 s skacze łukiem do tylnego okna i siedzi w aucie |
| | 2,13 s „więcej kolczatki na nich” | po obłoku 7 zwojów poziomo i 4 na krzyż, gęste kolce |
| | 2,30 s „jeszcze jedna tabliczka bye!” | druga „BYE!” w miejscu kreski |
| 65 noszenie | 1,67 s głowa w dół na barkach Clyde'a; jedna ręka zgięta na Bonnie | Clyde niesie ją przez bark: biodra na barku, głowa zwisa za plecami, nogi z przodu; przednia ręka w skrócie trzyma ją za uda |
| 66 oboz | 7,23 s „niech wjedzie tu księżyc” | księżyc zjeżdża na nitce w prawy górny róg |
| 67 rzeka | „wydłuż scenę i daj narrację, oraz Ken Burns na myjący kadr głowy i wyskakującą rybę po chwili” | nowa kwestia: „Bonnie still tried to look like a movie star, even when her only mirror was a cold river.” (klon, do odsłuchu); ujęcie dłuższe, kamera powoli najeżdża na głowę, ryba wyskakuje w pauzie po kwestii, Bonnie odskakuje, „O!” |
| 68 list_ford | „ta kartka ma latać w powietrzu 4 s i wlepić się tak jak teraz” | list frunie zygzakiem 4 s i przykleja się do maski w tym samym miejscu (plask); podpis „Clyde?” i „?” po przyklejeniu |
| 69 platte | „więcej wyjaśnień w tej scenie” | dłuższa kwestia: kiedy (lipiec 1933), gdzie (dwa domki motelu pod Platte City), opancerzone auto i to, że gang się przebił (klon, do odsłuchu); w kadrze zawieszka miejsca i czasu, podpisy „ARMORED CAR”, „Buck Barrow”, „Blanche”, błyski policji i odpowiedź gangu, na końcu Ford gangu ucieka |
| 70 dexfield | 2,60 s „uklęknij ją i zwróć w prawą stronę” | Blanche klęczy przy Bucku, zwrócona w prawo |
| | 9,13 s „tabliczka aaaa” | „AAAA!” nad nią |
| 71 przeprawa | „niech ruszają lekko rękami góra dół, jakby pływali” | każda z trzech postaci rusza rękami w swoim rytmie |
| 72 wd_odchodzi | 2,07 s „tabliczka no way!”; 4,53 s „tabliczka maminsynek po angielsku” | „NO WAY!” nad Clyde'em za kierownicą, „MAMA'S BOY!” nad Bonnie (miejsca z kresek) |
| 73 rodziny | „matki podchodzą do auta ręce w dół, a Bonnie rzuca przez dach do góry im pranie na koszyki” | matki idą od swojego auta z koszykami w opuszczonych rękach; Bonnie wyrzuca z okna 8 sztuk prania łukiem nad dachem, każda wpada do koszyka |
| 74 sowers | „zastanów się, czy dobrze jest narysowane całe to ujęcie według opisu sceny i narracji” | dodane, czego brakowało według kwestii: auto rodzin z matkami i koszyk („family picnics”), szeryf z podpisem „Dallas Sheriff Smoot Schmid” („the Dallas sheriff”), strzały z luf, dwa „OUCH!”, jeden nad Bonnie i jeden nad Clyde'em („both of them… in their legs”) |
| | 2,93 s policjant bardziej w lewo / drugi bardziej w prawo | w krzakach po obu stronach drogi (300 i 1100) |
| | 4,53 i 4,93 s „dziura w szybie” | dziury po kulach w szybach, w miejscach z kresek, jadą z autem |
| 75 odbicie | „dopiero w 4 s strzel do niego”; 2,83 s „przekręć go w tym momencie w prawo” | trzeci więzień obraca się do strażnika w 2,83 s i strzela z lufy w 4,0 s; strażnik pada po strzale; cisza przed strzałem przesunięta |
| 76 straznik | 1,47 s „niech ta czapka tak fruwa na ziemię z postrzeloną dziurą” | kapelusz spada zygzakiem jak liść i kładzie się na drodze; w rondzie dziura po kuli; podpis po upadku |
| 77 simmons | 6,23 s „to idzie do góry”; „tabliczka give him to me!” | podpis odjeżdża w górę w 6,23 s; „GIVE HIM TO ME!” przy pięści |
| 78 hamer | „od początku szeryf chodzi lewo prawo prawo lewo prawo prawo lewo dół góra i w tle latają kule…; w klatce 240 wrzuca broń do góry, obraca się i w klatce 273 łapie” | Hamer chodzi krokami L P P L P P L, przysiad i wstaje; w tle przelatują kule ze smugą jak w ujęciu 13 (z dźwiękiem); w 8,0 s podrzuca broń, dwa obroty, w 9,1 s łapie ją z prawej |
| | 3,03 s „odznaka szeryfa”; „podnieś na chwilę rękę do góry” | gwiazda strażnika Teksasu na piersi; ręka w górze 2,75–3,35 s |
| | 7,97 s „rzuca broń tu i się kręci”; 9,07 s „spada mu do ręki z tej strony”; 9,97 s „tabliczka easy.” | broń leci przez punkt z kreski i spada do ręki z prawej; „EASY.” |
| 80 hak_szuflada | 0,80 s mapa niżej, po niej cały czas driftują Bonnie i Clyde; 4,53 s „podnieś rękę i machaj, jakbyś odmawiał” | mapa niżej, po niej Ford w poślizgu z kurzem; Hamer macha uniesioną dłonią: „nie” |
| 81 hak_teczka | „mapa niżej”; 5,03 s „przesuwa boks w to miejsce”; 5,17 s „zacznij mrugać lampą”; 5,97 s „od 5 s zjeżdża na nitce kawa aż do 6,20, a po 0,5 s podnosi ją” | teczka przesuwa się do miejsca z kreski; lampa mruga od 5,17 s; kubek zjeżdża na nitce 5,0–6,2 s, po 0,5 s Hamer podnosi go do ust |
| 82 podkreslenie | 2,10 s „tutaj kredka”; 5,80 s „trzask, niech ten grafit gdzieś poleci, kredka się łamie” | ołówek grafitem na linii, trzonem w dół w prawo; w 5,8 s pęka, czubek z grafitem odlatuje łukiem, złamany ołówek podskakuje, „SNAP!” |
| 84 hamer_motel | „narysuj Bonnie na tym zdjęciu, jakby robiła pajacyka”; 4,80 s „porusz zdjęciem”; 5,80 s „puszka się przewraca”; 7,40 s „tabliczka yeah I saw” | na zdjęciu Bonnie robi pajacyka (ręce w górę i w dół); zdjęcie drga w dłoni; górna puszka przewraca się na bok; „YEAH, I SAW!” nad recepcjonistą |
| 85 dzien20 | 1,03 s „narysuj to linię białą”; 2,57 s „Bonnie ma jedną rękę w górze i macha nią”; 8,73 s „tabliczka stop!!! a następna dopiero po 1,5 s” | biała linia granicy w poprzek drogi; Bonnie macha z auta; „STOP!!!” w 8,73 s, „NOT MY STATE…” 1,5 s później |
| 86 mapa | 4,23 / 4,57 / 5,70 s „tu narysuj kropkę i połącz”, 6,27 s „tu narysuj dużą kropkę i połącz” | kropki w miejscach z kresek, każda łączy się czerwoną nicią z poprzednią; ostatnia duża (Luizjana); gag z pękającą nicią po niej |
| 88 grapevine | 10,90 s „zaświeć lampami z tyłu”; „zamrugaj lampą” | tylne lampy Forda świecą, reflektor mruga trzy razy |
| 90 tullis | 2,20 s „tak jej rozciągnij tę suknię”; 8,43 s „idzie w tym kierunku i daje kwiatka na grób”; 10,63 s „tabliczka oh lord!” | suknia ślubna w dzwon od bioder do trawy; Maree podchodzi do trumny i kładzie kwiatek przy bukiecie; „OH LORD!” |
| 91 gazety_zle | 2,07 s „na każdej gazecie duża śmiejąca się buzia Bonnie” | na każdej gazecie wielka śmiejąca się buzia Bonnie w berecie |
| 93 commerce | 5,47 s „tabliczka need help?!”; 7,63 s „lampy zamrugały” | „NEED HELP?!”; reflektor Forda w rowie mruga |
| 96 boyd_tab | 0 s „linia koloru granicy przekroczenia Kansas”; 0,97 s „tabliczka Remember I don't smoke cigars!” | biała linia granicy przy tablicy KANSAS; „REMEMBER, I DON'T SMOKE CIGARS!” nad Bonnie |
| 97 prasa_cygaro | 7,47 s „mapa niżej”; 11,07 s „lampa zaświeciła”; 12,33 s „czapka z dziurą przekręca się minimalnie w dół” | mapa niżej; lampa nie świeci, w 11,07 s mrugnie i zapala się; kapelusz na krześle z dziurą po kuli przechyla się lekko w dół |
| 98 methvin | 1,57 s „tabliczka We need to make a trap!”; 7,43 s farmer podchodzi, zabiera kartkę, wraca i po 1 s ją podnosi; 12,03 s „okay! let's try” | „WE NEED TO MAKE A TRAP!” nad Hamerem; Ivy idzie do stołu, bierze PARDON, wraca na miejsce, po 1 s unosi go pod żarówkę („HMM…”); „OKAY! LET'S TRY” |
| 99 wiersz | 2,40 s „tabliczka what's that?”; 6,77 s „tabliczka Do not forget. i Bonnie idzie w prawo za kadr” | „WHAT'S THAT?” nad matką; „DO NOT FORGET.” i Bonnie kuleje w prawo za kadr |
| 100 pozegnanie | 2,97 s „duża tabliczka z tym napisem” | duża HOME SWEET HOME w tylnej szybie, czytelna |
| 102 shreveport | 8,00 s „za szybą jego czarna sylwetka troszkę niżej, podnosi rękę z kawą”; 12,70 s „jeszcze 2× go zrób lewo prawo” | czarna sylwetka Henry'ego w oknie kawiarni (tylko w obrębie okna), podnosi kubek; po wyjściu rozgląda się jeszcze dwa razy |
| 103 noc | 1,90 s „ma słomę w ustach i na następnych ujęciach też”; 7,00 s „tabliczka yaw” | słoma w ustach Gaulta we wszystkich ujęciach z nim; „YAWN” nad Jordanem |
| 104 posse | „Manny Gault ściąga ręką kapelusz z głowy, uchyla i znowu odkłada na głowę, a rękę daje w dół przy ciele”; 11,47 s „niech podniesie broń góra dół” | Gault przy swoim podpisie zdejmuje kapelusz, uchyla go, odkłada i opuszcza rękę; Jordan dwa razy unosi i opuszcza karabin |
| 105 zasadzka_rano | 0,87 s „farmera przesuń w dół kadru”; 3,60 s „niżej to koło w ziemię” | Ivy stoi niżej; ciężarówka opiera się tylnym kołem o ziemię, przód wyżej na lewarku |
| 106 kanapka | 0 s „przesuń kanapkę w tym miejscu” | kanapka przed twarzą Bonnie, w miejscu z kreski |
| 107 zwolnienie | 0 s „podnieś wyżej przód auta i tył niżej”; 0,67 s „tabliczka hey help me!” | ciężarówka (wspólne); „HEY, HELP ME!” |
| 108 zasadzka | 2,87 s „kapelusz stąd leci do góry w tym kierunku i spada na ziemię w 4 s” | kapelusz wylatuje z okna auta, łukiem w górę i w prawo, kręci się i ląduje w 4,0 s przed maską |
| 109 dym | 0 s „więcej dziur”; „dym stąd”; 5,77 s „ręka do kapelusza, ściąga go i w dół go w ręce”; 6,70 s „6 tabliczek we got them!” | auto gęsto podziurawione; dym unosi się z prawej; Hamer zdejmuje kapelusz ręką i trzyma go przy boku; sześć „WE GOT THEM!”, po jednej nad każdym |
| 110 pamiatki | 3,67 s „latają te rzeczy Bonnie w powietrzu między ludźmi” | pukle włosów i skrawki czerwonej sukienki przelatują łukami między ludźmi |
| 111 darby_zaklad | 6,27 s „zamrugał lampą”; „undertaker podchodzi w to miejsce” | lampa mruga; Darby idzie do miejsca z kreski |
| 113 auto_jarmark | 3,60 i 4,23 s „stąd rzuć monetę” | kobieta i farmer rzucają monety ruchem ręki; monety lecą do kasetki |
| 114 blanche_po | 1,83 s „chodzi powoli lewo prawo i podlewa” | Blanche chodzi wzdłuż grządki w tę i z powrotem i podlewa |
| 116 film_hamer | „poruszaj tymi postaciami, obiektami na tym płótnie kina tak, jakby film po prostu leciał” | auto wjeżdża, para idzie do siebie, tańczy i się obraca; związany Hamer się szarpie, filmowa Bonnie krąży z aparatem i robi trzy zdjęcia; ekran lekko migocze |
| 117 gra | 7,20 s pikselowa Bonnie / Clyde wyskakuje z auta | pikselowi Bonnie i Clyde wyskakują łukami w lewo, auto zostaje puste |
| 118 koniec | 5,37 s duża teczka z napisem Bonnie & Clyde; 6,47 s „większa teczka”; 7,27 s „powoli zjeżdża karta z ich aktami”; 8,33 s „zamrugaj światłami”; 9,50 s „i te akta zjeżdżają w dół za nią do karty” | duża teczka z napisem BONNIE & CLYDE; karta „BARROW · PARKER” zjeżdża powoli; reflektory mrugają; karta chowa się za teczkę, do środka |
| 119 dzieki | „ściąga ręką kapelusz z głowy i z nim w ręku przenosi go w dół, i tak dla wszystkich, co mają coś na głowie”; 1,27 s „jej narysuj czapkę z daszkiem” | wszyscy przed ukłonem zdejmują nakrycie głowy ręką i trzymają je przy boku, a Bonnie macha beretem; czapkę z daszkiem dostał Darby (postać w czarnym garniturze w miejscu kreski) |

## Do sprawdzenia przez reżysera

- Dwie nowe kwestie, klon głosu: **„rzeka”** i **„platte”** (dłuższa, z wyjaśnieniem). Ujęcia mają długość z nowych nagrań.
- **Ujęcie 119**: kreska z 1,27 s leży na postaci w czarnym garniturze, czyli na Darbym (grabarzu), więc to on dostał czapkę
  z daszkiem. Jeśli chodziło o inną postać, wystarczy wskazać którą.
- **Ujęcie 72**: „NO WAY!” wisi nad Clyde'em (kreska bliżej kierowcy), „MAMA'S BOY!” nad Bonnie.
