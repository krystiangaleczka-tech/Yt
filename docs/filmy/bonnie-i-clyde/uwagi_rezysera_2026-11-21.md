# Uwagi reżysera z 21.11.2026 — błędy, uwagi i poprawki

Projekt Studio `prj_dad935cf1d7446fa` (EN, podgląd na żywo), rewizja 1194, markery z 22:37–22:57. Odczytane z Studio
(`frame_annotations` i `director_notes`), zanim następne wgranie planu mogło nadpisać pole uwag w ujęciu. Kreski w pikselach
ekranu 1280 × 720 (początek → koniec), sekunda = czas w ujęciu. Wykonane 21–22.11.2026; zasady, które z tego wyszły, są
w docs/WYTYCZNE_UJEC.md (1.11, 1.20, 1.27, 1.28, 4.1 i tabela „Skąd te zasady”).

Każde ujęcie: **Błąd** — co było w kadrze, **Uwaga** — co napisał reżyser (cytat), **Poprawka** — co zrobiono i gdzie.

## 12. wprowadzenie (d00_12)
- **Błąd:** ta sama, przednia ręka wyjmowała cygaro z ust — rewolwer znikał z dłoni na 4,6–7,2 s, cygaro wisiało w dłoni
  daleko od ust (ręka sztywna, nie sięgała), a z ust znikało dopiero na 5,2 s, więc przez chwilę były dwa cygara.
- **Uwaga:** 4,10 s „w tej ręce cały czas trzyma pistolet”; 4,10 s „w drugiej ręce bierze z buzi papieros”; 7,33 s „i go
  rzuca do tyłu” (kreska: łuk ręki w górę i za siebie).
- **Poprawka:** rewolwer w przedniej dłoni przez całe ujęcie; tylna ręka idzie przed tułów, zgina się ku kamerze (skrót)
  i dłoń trafia w środek cygara przy ustach (4,1–4,6 s), cygaro przechodzi z ust do dłoni w jednej klatce; Bonnie patrzy na
  nie, „UGH!”; zamach i rzut za siebie na 7,33 s, cygaro koziołkuje w lewo, spada za rampę, unosi się dymek. „Papieros”
  odczytany jako cygaro z ujęcia (na nim stoi cała historia — „borrowed cigar”). Silnik: `lalka(skrot=…, tyl_przed=…)`,
  `scena.do_punktu`. Dźwięk: pyknięcie cygara, świst rzutu, upadek i syk.

## 13. wprowadzenie2 (d00_13)
- **Błąd:** Bonnie strzelała na 0,15 s, kiedy kamera była jeszcze na Clydzie — strzału nie było widać, kula brała się znikąd;
  trafienie w bak było za Bonnie, pod pasem napisu, a kałuża ledwo widoczna.
- **Uwaga:** 1,27 s „teraz strzel z końcówki rewolweru”; 5,37 s „tu się wbija kula” (punkt na aucie); 5,63 s „zaczyna lecieć
  ciurkiem paliwo i zalewa ziemię powoli aż do kolan” (kreska od auta w lewo na ziemię).
- **Poprawka:** Bonnie celuje i strzela na 1,27 s — błysk na końcu lufy, rewolwer uniesiony w kierunku strzału (ok. 34°),
  dymek z lufy, potem ręka opada, a rewolwer wisi lufą w dół (nie zasłania dziury). Tor kuli liczony na ekranie: odbicia
  lustrzane od brzegów kadru jak w grze (5 odbić), koniec dokładnie w punkcie markera na 5,37 s, tam dziura w karoserii
  z iskrą. Od 5,63 s strumień paliwa z dziury, poziomo w lewo i łukiem na ziemię (za Bonnie wychodzi z jej lewej strony,
  jak na kresce), krople; od 5,95 s paliwo zalewa scenę jak fale w teatrze — rząd za autem zakrywa deski, rząd przed lalkami
  rośnie do kolan; kamera po trafieniu schodzi niżej, żeby zalew był nad pasem napisu; „…” nad Bonnie na 9,0 s. Dźwięk:
  odciągnięcie kurka, strzał, 5 rykoszetów, uderzenie w blachę, lanie, woda. Opis ujęcia w rozpisce znów mówi o gagu.

## 14. hak_joplin_rzeczy (d00_14; ten sam rysunek co 49. joplin_rzeczy)
- **Błąd:** klatki kliszy były puste (brązowe prostokąty); policjant stał bez reakcji.
- **Uwaga:** 6,60 s „na tych klatkach z filmu są pozy czarne Bonnie, różne mikro”; 7,80 s „macha tym lekko”; 7,80 s
  „otwiera buzię i tabliczkę ooo..”.
- **Poprawka:** nowa klisza (`zestaw_bc.klisza_pozy`) — w każdej klatce mikro, czarna sylwetka Bonnie w innej pozie
  (z rewolwerem, machająca, ręce na biodrach, ręce w górze), stojąca prosto, kiedy klisza wisi pionowo; od 7,6 s policjant
  lekko macha aparatem, klisza buja się za ręką z opóźnieniem; na 7,8 s otwarte usta (lalka `detektyw_o`, podmiana w jednej
  klatce) i tabliczka „OOO…” z westchnieniem. W krótszym ujęciu 49 to samo o 6,0 s, żeby tabliczka zdążyła.

## 15. zdjecie (d00_15)
- **Błąd:** Bonnie brała cygaro od chłopaka do ręki i dopiero potem do ust; flesz błyskał znikąd — chłopak nie miał aparatu.
- **Uwaga:** 2,03 s „chłopak daje jej papierosa do buzi”; 5,67 s „chłopak wyciąga z kieszeni aparat stary, ten z lampą taką
  dużą, i robi jej zdjęcie”.
- **Poprawka:** Bonnie staje tak blisko, że wyciągnięta dłoń chłopaka sięga jej ust; cygaro przechodzi z jego dłoni do jej
  ust w jednej klatce na 2,03 s. Nowy rekwizyt `aparat_lampa` (stary aparat prasowy z wielką czaszą lampy): dłoń do kieszeni
  (4,9 s), aparat wychodzi z kieszeni (5,3–5,67 s), do oka, flesz z czaszy na 6,35 s, migawka. Skrót w zapowiedzi
  (`zap_zdjecie`) pokazuje teraz flesz.

## 17. prasa (d00_17)
- **Błąd:** maszyna stała sztywno do końca ujęcia.
- **Uwaga:** 7,17 s „zaczyna podskakiwać lekko maszyna” (obrys całej maszyny).
- **Poprawka:** od 7,17 s maszyna z wałkami podskakuje o kilka pikseli co 0,31 s (`drukarnia(podskok=…)`), każdy podskok
  ze stukiem.

## 18. hak_cygaro (d00_18)
- **Błąd:** zgnieciona kulka wylatywała za kadr bez skutku.
- **Uwaga:** 5,70 s „dźwięk kota, bo dostał tym papierem” (kreska przy prawym brzegu, gdzie wylatuje kulka).
- **Poprawka:** na 5,72 s za kadrem miauczy trafiony kot (nowy dźwięk `efekty.kot`), a Bonnie podskakuje ze strachu na 6,1 s
  — podskok ma teraz przyczynę. Nowy rodzaj dźwięku: do odsłuchu przez reżysera.

## 19. obietnica (d00_19)
- **Błąd:** dwa Fordy sunęły po mapie sztywno, tą samą trasą, jeden za drugim.
- **Uwaga:** 4,27 s „autka mają driftować po mapie z dymem” (kreska: trasa czarnego Forda łowcy); 4,27 s „tak samo jak tamto,
  tylko inna trasa” (kreska: trasa szarego Forda Bonnie i Clyde'a).
- **Poprawka:** każdy Ford jedzie trasą ze swojej kreski (przeliczoną z ekranu na mapę), na zakrętach wychodzi w poślizg
  (tył na zewnątrz), spod kół idzie dym, przy największych poślizgach pisk opon. Końce tras podniesione nad pas napisu;
  łowca dojeżdża pierwszy i czeka („catch them without ever chasing them”), oba auta stają prosto.

## 24. kawiarnia (d01_05)
- **Błąd:** klient miał gazetę na twarzy i głowie, ręka szła przez kartkę; strumień kawy kończył się nad filiżanką.
- **Uwaga:** 1,57 s „tego gościa cofnij w prawo minimalnie, tak żeby gazetę trzymał w ręku, gazeta za ręką, a nie w nim i na
  głowie”; „tu wlewasz kawę”; „wlewając ruszasz tym dzbankiem góra dół”.
- **Poprawka:** klient 64 px w prawo, gazeta przed nim obok głowy, obie dłonie na jej bliższym brzegu (kartka za dłonią).
  Ta sama zmiana we wspólnej funkcji `czyta_gazete`, więc tak samo czyta drukarz (97) i Hamer (115). Strumień kawy kończy się
  w filiżance, za jej przednią ścianką; dzbanek dwa razy w górę i w dół przy nalewaniu (dłuższe nalewanie, huk przesunięty
  na 3,6 s, „SIGH…” na 3,2 s); obrączka idzie za dłonią.

## 25. kuchnia (d01_06)
- **Błąd:** dłoń z łyżką była obok garnka; serca wisiały razem pośrodku, kajdanki też pośrodku.
- **Uwaga:** 1,50 s „tu ma być łyżka i koniec ręki Bonnie, więc ją cofnij w prawo minimalnie”; 5,17 s „nad nią serce”,
  „nad nim serce”; 9,23 s „nad nim kajdanki”.
- **Poprawka:** Bonnie stoi tak, że dłoń i łyżka są nad środkiem garnka (`stan_przy`); jedno serce nad Bonnie, drugie nad
  Clyde'em; na „arrested” serca odjeżdżają, a nad Clyde'em zjeżdżają kajdanki. Na ścianie wisi patelnia (zapowiedź ujęcia 26).

## 26. areszt (d01_07)
- **Błąd:** Bonnie goniła policjanta z łyżką.
- **Uwaga:** 0,00 s „daj jej patelnię!” (kreska od dłoni w górę).
- **Poprawka:** nowy rekwizyt `patelnia`; Bonnie trzyma ją uniesioną jak do ciosu (`PATELNIA(-80)`), stoi tam, gdzie
  mieszała w poprzednim ujęciu.

## 27. waco_przed (d01_08) i 28. waco (d01_09)
- **Błąd:** Bonnie szła z rewolwerem w ręce, „chowała go pod płaszcz”, choć płaszcza nie miała (sukienka), rewolwer znikał
  przy biodrze.
- **Uwaga:** 1,70 s „daj jej patelnię zamiast rewolweru”; 2,33 s „włóż patelnię na plecy”; 2,97 s „weź stąd rewolwer do ręki”
  (kreska przy pasku); 3,97 s „skryj go pod płaszcz”.
- **Poprawka:** nowa lalka `bonnie_plaszcz` (płaszcz w Waco). Bonnie idzie z patelnią, zarzuca ją przez ramię na plecy
  (2,33 s, `patelnia_na_plecach`), bierze zza paska rewolwer (2,97 s), rozgląda się („…”), dłoń na piersi — rewolwer znika pod
  połą płaszcza (3,97 s), poprawia beret, „♪”, wchodzi. W ujęciu 28 Bonnie jest w tym samym płaszczu, z patelnią na plecach,
  i wyjmuje pistolet spod płaszcza prosto do krat.

## 32. palce (d01_13) — uwaga w ujęciu i zmiana w Studio
- **Błąd:** kwestia („he had two toes cut off with an axe, and six days later he was paroled anyway”) mówiła o czymś innym niż
  obraz (siekiera spada na stopę) i o zwolnieniu, które widać dopiero w następnym ujęciu; była za długa na 7 s.
- **Uwaga:** reżyser przyciął ujęcie w Studio z 10,2 s do 7,0 s, wykasował „two toes” z kwestii i napisał „zmień narrację, bo
  opis sceny jest kompletnie inny”.
- **Poprawka:** kwestia mówi to, co widać: „To get out of the fields, Clyde let an axe fall on his own foot.”; długość 7,0 s
  zapisana w rozpisce (następne wgranie jej nie cofnie). Zwolnienie przeszło do ujęcia 33 „parol”, gdzie strażnik macha kartką
  PAROLE: „Six days later: paroled anyway.” (ujęcie było nieme, długość bez zmian — 4,0 s).

## 35. po_bramie (d01_16)
- **Błąd:** Clyde przy wsiadaniu do auta znikał w przenikaniu (rzecz znika bez powodu).
- **Uwaga:** 4,07 s „clyde w aucie” (obrys tylnego okna).
- **Poprawka:** Clyde wrzuca kulę na tylne siedzenie, wskakuje łukiem do auta i od 3,9 s siedzi w tylnym oknie. Kula leży
  w aucie za karoserią — widać ją tylko przez szybę (tak samo w ujęciu 36 akt2, gdzie wcześniej przebijała drzwi).

## Błędy procesu (znalezione przy sprawdzaniu)
- **Dźwięk nie poszedł za obrazem:** muzyka i efekty w Studio miały 1086,9 s przy filmie 1106,4 s (po nowych ujęciach-mostach
  z 21.11 dźwięku nie przeliczono) — od pierwszego nowego ujęcia dźwięk się rozjeżdżał, ostatnie 20 s było ciche.
  Poprawka: efekty.py przeliczony (1106,4 s), wgrany `studio_film.py dzwiek`; zasada w wytycznych 4.1.
- **Wgranie planu kasowało uwagi reżysera:** `studio_film.py plan` wpisywał w pole uwag tylko wiersz z rozpiski — uwaga
  „zmień narrację…” zginęłaby przy pierwszym wgraniu. Poprawka: narzędzie zostawia wiersze reżysera (uwaga jest w Studio).
- **Ten sam błąd w kilku ujęciach:** gazeta na głowie była we wspólnej funkcji czytania — poprawiona raz, dla 24, 97 i 115.

## Kontrola (21–22.11)
Arkusze klatek z kreskami markerów i paski klatek każdego zmienionego ujęcia obejrzane; test końca świata OK na 15 ujęciach;
kontrola ciągłości w Studio 0/0/7 (zero błędów wagi 3); dźwięki zmierzone w chwilach zdarzeń (kot +20 dB, strzał, kula
w baku, flesz, piski opon). Wpis w dzienniku pracy Studio.

## Lista markerów (dane z Studio)

| Ujęcie | s | Kreska (ekran) | Tekst |
|---|---|---|---|
| 12 wprowadzenie | 4,10 | (782,343)→(763,335) | w tej ręce cały czas trzyma pistolet |
| 12 wprowadzenie | 4,10 | (616,403)→(602,397) | w drugiej ręce bierze z buzi papieros |
| 12 wprowadzenie | 7,33 | (631,385)→(605,389) | i go rzuca do tyłu |
| 13 wprowadzenie2 | 1,27 | (111,397)→(103,384) | teraz strzel z końcówki rewolweru |
| 13 wprowadzenie2 | 5,37 | (552,524)→(558,530) | tu się wbija kula |
| 13 wprowadzenie2 | 5,63 | (428,541)→(326,560) | zaczyna lecieć ciurkiem paliwo i zalewa ziemię powoli aż do kolan |
| 14 hak_joplin_rzeczy | 6,60 | (496,278)→(499,286) | na tych klatkach z filmu są pozy czarne Bonnie, różne mikro |
| 14 hak_joplin_rzeczy | 7,80 | (491,283)→(503,274) | macha tym lekko |
| 14 hak_joplin_rzeczy | 7,80 | (654,284)→(653,296) | otwiera buzię i tabliczkę ooo.. |
| 15 zdjecie | 2,03 | (840,339)→(834,338) | chłopak daje jej papierosa do buzi |
| 15 zdjecie | 5,67 | (1033,472)→(1029,481) | chłopak wyciąga z kieszeni aparat stary, ten z lampą taką dużą, i robi jej zdjęcie |
| 17 prasa | 7,17 | (257,286)→(298,284) | zaczyna podskakiwać lekko maszyna |
| 18 hak_cygaro | 5,70 | (1266,371)→(1249,378) | dźwięk kota, bo dostał tym papierem |
| 19 obietnica | 4,27 | (591,409)→(793,563) | autka mają driftować po mapie z dymem |
| 19 obietnica | 4,27 | (675,332)→(803,588) | tak samo jak tamto, tylko inna trasa |
| 24 kawiarnia | 1,57 | (901,337)→(871,337) | tego gościa cofnij w prawo minimalnie… gazeta za ręką, a nie w nim i na głowie |
| 24 kawiarnia | 1,57 | (693,480)→(699,528) | tu wlewasz kawę |
| 24 kawiarnia | 1,57 | (664,415)→(656,401) | wlewając ruszasz tym dzbankiem góra dół |
| 25 kuchnia | 1,50 | (416,435)→(416,454) | tu ma być łyżka i koniec ręki Bonnie, więc ją cofnij w prawo minimalnie |
| 25 kuchnia | 5,17 | (483,164)→(483,309) | nad nią serce |
| 25 kuchnia | 5,17 | (929,166)→(932,296) | nad nim serce |
| 25 kuchnia | 9,23 | (927,171)→(925,297) | nad nim kajdanki |
| 26 areszt | 0,00 | (538,500)→(543,432) | daj jej patelnię! |
| 27 waco_przed | 1,70 | (420,467)→(435,425) | daj jej patelnię zamiast rewolweru |
| 27 waco_przed | 2,33 | (499,424)→(492,480) | włóż patelnię na plecy |
| 27 waco_przed | 2,97 | (509,515)→(506,503) | weź stąd rewolwer do ręki |
| 27 waco_przed | 3,97 | (525,515)→(525,514) | skryj go pod płaszcz |
| 35 po_bramie | 4,07 | (1026,506)→(1036,504) | clyde w aucie |
| 32 palce | — | uwaga w ujęciu | zmień narrację, bo opis sceny jest kompletnie inny (i przycięcie do 7,0 s) |

Razem: 1 uwaga w ujęciu, 28 markerów — wszystkie wykonane. Do odsłuchu: miauknięcie kota (18) i nowa kwestia w „parol” (33).
