# A. Bunkier K-9 — *Sealed Under the Front: 100 Days in Bunker K-9*

## Streszczenie (36 min)

Pierwszego dnia wojny chowasz się z 60 cywilami w schronie K-9 pod starym szpitalem. Ostrzał z północy i z południa zawala wyjście, wentylacja staje — od teraz powietrze daje tylko ręczna korba filtrów. Trzeciego dnia odkrywasz, że drzwi awaryjne zostały **zaspawane od środka**. Z zamkniętego poziomu B3 coś puka. Ludzie zaczynają chorować: szara skorupa na skórze, a potem wstają jako **Wydrążeni** — nie widzą, idą za oddechem. Komendant Brandt kłamie, inżynier Oskar uczy cię oddychać powoli, mała Mila rysuje „szarych ludzi” i zauważa, że w zimnie śpią.

W części 2 prawda wychodzi na jaw: pod schronem było laboratorium (Projekt SZARY), a „front” wokół bunkra to w rzeczywistości **kordon kwarantanny** — obie armie strzelają w każdą dziurę, która się otworzy. Próba przekopania się kończy katastrofą, Oskar ginie, otwierając szyb powietrzny z B3. Radio ujawnia, że dnia 60 bunkier ma zostać „wysterylizowany”. Ty wynegocjowujesz 40 dni: sami oczyścicie bunkier.

W części 3 przerzucacie diesel z generatora do B3. Brandt zostaje, żeby podpalić gniazdo. Bunkier płonie od dołu, generator gaśnie i przez ostatnie 20 dni żyjecie w całkowitej ciemności, codziennie nadając „K-9 clean”. Dnia 100 ktoś tnie drzwi palnikiem. Za nimi stoją w kombinezonach żołnierze **obu** armii — razem.

**Bohater:** Ty, praktykant konserwatora (znak: żółte nauszniki na szyi, prezent od Oskara).
**Pozostali:** Oskar (stary inżynier, mentor, ginie w cz. 2), Lena (pielęgniarka), kpt. Brandt (komendant, ukrywa protokół), Mila (8 lat, zgubiła matkę), Rafał (lider „kopaczy”, zarażony w cz. 2), Teodor (pierwszy zarażony).
**Zasady świata:** Wydrążeni idą za oddechem (CO₂), w zimnie zwalniają i zasypiają, ogień zabija bakterię. Zarażenie: skorupa w 2–4 dni.
**Tajemnica:** zaspawane drzwi (cz. 1) → klucz Brandta i teczka protokołu (cz. 1/2) → kordon zamiast frontu (cz. 2) → „sterylizacja” i rozejm przy K-9 (cz. 3).

## Assety

- **Lokacje (stany):** ulica nad schronem (dzień 1 / ruiny dnia 100) · hala schronu (pełna / pusta, barykady / ciemność) · pokój filtrów z korbą (działa / zepsuta / cienie w kratce) · korytarz z drzwiami awaryjnymi (spaw świeży / zardzewiały / cięty palnikiem) · szyb windy towarowej · poziom B3 (laboratorium / gniazdo / spalone) · biuro Brandta.
- **Pierwszy plan:** kratka wentylacyjna, framuga stalowych drzwi, łóżka piętrowe, rury.
- **Postacie:** Ty (~30 póz, w tym „wstrzymany oddech”, maska, zmęczony/brudny), Oskar, Lena, Brandt, Mila, Rafał (+ wersja zarażona), Wydrążeni (3 typy: stoi, idzie, śpi).
- **Rekwizyty:** nauszniki, latarka, korba, kanister diesla (pełny/pusty), klucz Brandta, teczka K-9, radio, rysunki Mili, maski, racje, licznik dni na ścianie, świeczka.
- **HUD:** dzień, O₂ %, woda L, racje, diesel L.

---

## ROZDZIAŁ 1 — „Zamknięci” (Day 1–30, 0:00–12:00)

### 1.1 Wejście · 0:00–3:00 · Day 1

- **B01** `0:00` Hook: dzień 100 jako zapowiedź — stoisz przy drzwiach, oddychasz bardzo wolno, za tobą cień.
  - S1 `PO·stat` ciemny korytarz, tylko latarka · S2 `Z·naj` twoja twarz, para z ust znika · S3 `D·stat` HUD O₂ 16% · S4 czerń → tytuł.
- **B02** `0:30` Dzień 1, miasto: syreny, ludzie biegną do piwnicy szpitala. W tłumie łapiesz za rękę zgubioną Milę.
  - S1 `PO·pan` ulica w dymie (PT: warstwy budynków) · S2 `PŚ·stat` biegniesz z torbą narzędzi · S3 `Z·stat` ręka Mili w twojej.
- **B03** `1:00` Schron K-9: 60 osób, Brandt liczy głowy i ogłasza zasady (racje, cisza).
  - S1 `PO·odj` hala pełna ludzi · S2 `PŚ·stat` Brandt z listą · S3 `D·stat` lista „60”.
- **B04** `1:30` Ostrzał z obu stron. Oskar rozpoznaje po dźwięku: „to Północ… a to Południe”.
  - S1 `PO·drg 0,4` kurz z sufitu · S2 `Z·stat` Oskar nasłuchuje · S3 `D·drg 0,2` bujająca się lampa.
- **B05** `2:00` Bezpośrednie trafienie — główne wyjście się zawala.
  - S1 `PO·drg 1,0` błysk, pył · S2 czarna klatka 0,5 s · S3 `PŚ·stat` latarki w pyle.
- **B06** `2:30` Cisza. Wentylacja staje. Oskar: „Nie wpada już powietrze”. `[porada]` objawy nadmiaru CO₂ (ból głowy, senność).
  - S1 `D·stat` wiatrak w kratce się zatrzymuje · S2 `Z·naj` Oskar patrzy w górę · S3 `D·stat` HUD O₂ 21% zaczyna spadać.

### 1.2 Powietrze · 3:00–6:00 · Day 2–7

- **B07** `3:00` Z Oskarem w pokoju filtrów: ręczna korba agregatu filtrowentylacyjnego. Od teraz powietrze = mięśnie.
  - S1 `PO·stat` pokój filtrów · S2 `D·stat` korba · S3 `Z·stat` pot na twoim czole.
- **B08** `3:30` Grafik zmian po 4 h przy korbie; montaż dni 3–5.
  - S1 `D·stat` kreski na ścianie · S2 `PŚ·stat` kolejne osoby kręcą (podmiana póz) · S3 `D·stat` HUD dzień 5.
- **B09** `4:00` Dzień 3: oglądasz drzwi awaryjne. Świeży spaw — **od środka**.
  - S1 `PŚ·naj` ty przy drzwiach · S2 `D·stat` błyszczące krople spawu · S3 `Z·stat` twoja twarz.
- **B10** `4:30` Mówisz Brandtowi. „To wybuch je zespolił”. Kłamie.
  - S1 `PŚ·stat` ty · S2 `PŚ·stat` Brandt · S3 `D·stat` jego dłoń zasłania klucz przy pasku.
- **B11** `5:00` Dzień 6: woda z rur ma metaliczny smak, Lena każe gotować. `[porada]` przegotowanie wody.
  - S1 `PŚ·stat` Lena przy kuchence · S2 `D·stat` garnek · S3 `D·stat` HUD woda 340 L.
- **B12** `5:30` Dzień 7, noc: z zamkniętego poziomu B3 coś puka. Trzy razy.
  - S1 `PO·stat` śpiąca hala · S2 `D·naj` kratka w podłodze · S3 `Z·stat` otwierasz oczy.

### 1.3 Poziom B3 · 6:00–9:00 · Day 8–18

- **B13** `6:00` Dzień 8: Teodor kaszle, na nadgarstku szara skorupa. Lena go izoluje.
  - S1 `PŚ·stat` prycza za zasłoną · S2 `D·stat` skorupa · S3 `Z·stat` Lena w masce.
- **B14** `6:30` Dzień 10: Oskar odkrywa, że dolny kanał korby zasysa powietrze z B3. Stary znak: „K-9 / PROJEKT SZARY”.
  - S1 `PO·pan` kanały pod sufitem · S2 `D·stat` znak ostrzegawczy · S3 `Z·stat` Oskar milknie.
- **B15** `7:00` Dzień 12: Teodor umiera. Brandt każe zwieźć ciało windą na B3. Jedziesz z nim.
  - S1 `PO·stat` szyb windy · S2 `PŚ·odj` winda zjeżdża · S3 `Z·stat` latarka na kraty B3.
- **B16** `7:30` Noc: ciała w windzie nie ma. Ślady wleczenia.
  - S1 `D·stat` smuga na podłodze · S2 `Z·stat` Mila patrzy z pryczy.
- **B17** `8:00` Dzień 15: pierwszy Wydrążony — Teodor stoi w korytarzu. Wstrzymujesz oddech; odwraca się. Odkrycie zasady: idą za oddechem.
  - S1 `PO·stat` korytarz · S2 `Z·naj` Teodor ze skorupą · S3 `D·stat` para z twoich ust znika · S4 `Z·stat` Teodor odchodzi.
- **B18** `8:30` Dzień 18: mówisz wszystkim. Brandt zakuwa kraty B3 łańcuchem. Panika.
  - S1 `PO·drg 0,2` tłum · S2 `D·stat` łańcuch i kłódka · S3 `Z·stat` ty — decyzja: dowiesz się więcej.

### 1.4 Oddech · 9:00–12:00 · Day 19–30

- **B19** `9:00` Oskar uczy „dyscypliny oddechu”: wolno, nosem, mało ruchu. `[porada]` mniejszy wysiłek = mniejsze zużycie tlenu.
  - S1 `PŚ·stat` Oskar pokazuje · S2 `PO·stat` ludzie oddychają razem · S3 `D·stat` HUD O₂ 19%.
- **B20** `9:30` Dzień 23: przy korbie oddycha się najmocniej — Wydrążeni ciągną do pokoju filtrów. Jest ich już trzech.
  - S1 `PO·stat` pokój filtrów · S2 `D·naj` cienie za kratką · S3 `Z·stat` kręcący przestaje kręcić.
- **B21** `10:00` Dzień 26: podsłuchujesz Brandta przy radiu: „K-9 holding”.
  - S1 `PŚ·stat` przez szparę w drzwiach · S2 `D·stat` gałka radia · S3 `Z·stat` ty.
- **B22** `10:30` Dzień 28: Wydrążeni wdzierają się do dolnej hali. Tracicie drugą korbę i jedną osobę.
  - S1 `PO·drg 0,6` atak (PT: postacie wstają zza łóżek) · S2 `PŚ·pan` ucieczka po schodach · S3 `D·stat` HUD: 1 korba.
- **B23** `11:00` Dzień 30: zabierasz śpiącemu Brandtowi klucz.
  - S1 `PŚ·stat` śpiący Brandt · S2 `D·naj` klucz na pasku · S3 `Z·stat` jego powieki drgają.
- **B24** `11:30` Cliffhanger: w szufladzie teczka „K-9 — protokół kwarantanny. Zamknąć od wewnątrz. Dzień 1”. `[K]` zapowiedź części 2.
  - S1 `D·stat` teczka · S2 `Z·naj` twoja twarz · S3 czerń + „Part 2”.

## ROZDZIAŁ 2 — „Kordon” (Day 31–60, 12:00–24:00)

### 2.1 Prawda Brandta · 12:00–15:00 · Day 31–36

- **B25** `12:00` `[K]` Przypomnienie części 1 w 30 s (montaż kluczowych kadrów).
  - S1–S4 `D/Z·stat` spaw, Teodor, łańcuch, teczka.
- **B26** `12:30` Z Oskarem konfrontujecie Brandta. Przyznaje: rozkaz, spaw, laboratorium pod szpitalem, wyciek po trafieniu. Ale „ratunek przyjdzie dnia 60”.
  - S1 `PŚ·stat` trzy postacie · S2 `Z·stat` Brandt · S3 `Z·stat` Oskar.
- **B27** `13:00` Schron się dzieli: część chce się przekopać przez gruz, Brandt zabrania. Głosowanie.
  - S1 `PO·stat` dwie grupy · S2 `D·stat` ręce w górze · S3 `Z·stat` ty — nie głosujesz.
- **B28** `13:30` Dzień 33: „kopacze” Rafała zaczynają kopać główne wyjście.
  - S1 `PO·stat` rumowisko · S2 `PŚ·stat` Rafał z łomem · S3 `D·stat` HUD racje.
- **B29** `14:00` Dzień 35: Mila pokazuje rysunki „szarych ludzi” — śpią, kiedy jest zimno.
  - S1 `PŚ·stat` Mila z kartkami · S2 `D·pan` rysunki · S3 `Z·stat` ty rozumiesz.
- **B30** `14:30` Dzień 36: Oskar sprawdza — przy zimnych rurach z B2 Wydrążeni zwalniają. Pierwsza broń: zimno.
  - S1 `PO·stat` korytarz z rurami · S2 `Z·stat` Wydrążony zastyga · S3 `Z·stat` Oskar kiwa głową.

### 2.2 Kopanie · 15:00–18:00 · Day 37–45

- **B31** `15:00` Montaż kopania, racje maleją. `[porada]` racjonowanie kalorii przy wysiłku.
  - S1 `PO·stat` kopiący (podmiana póz) · S2 `D·stat` HUD racje ↓ · S3 `D·stat` kreski na ścianie.
- **B32** `15:30` Dzień 40: szczelina, światło dnia, wpada powietrze. Radość.
  - S1 `PO·naj` snop światła · S2 `Z·stat` twarze w świetle · S3 `D·stat` HUD O₂ ↑.
- **B33** `16:00` Natychmiast ostrzał — w szczelinę strzelają obie armie. To nie front, to kordon. Rafał ranny.
  - S1 `PO·drg 1,0` wybuchy · S2 `PŚ·stat` Rafał pada · S3 `Z·stat` Brandt: „Mówiłem”.
- **B34** `16:30` Dzień 42: gruz się osuwa, kopacze odcięci. Ciężki oddech rannych ściąga Wydrążonych.
  - S1 `PO·drg 0,5` zasyp · S2 `D·naj` para oddechu w ciemności · S3 `PO·stat` cienie nadchodzą.
- **B35** `17:00` Ratunek w ciemności: przechodzisz obok Wydrążonych na wstrzymanym oddechu, niesiesz Rafała.
  - S1 `POV·stat` latarka · S2 `PŚ·pan` mijasz ich · S3 `D·stat` HUD licznik wstrzymania oddechu · S4 `Z·stat` wydech za drzwiami.
- **B36** `17:30` Dzień 45: Rafał ma skorupę na nodze. Sam prosi, by zejść na B3.
  - S1 `D·stat` skorupa · S2 `PŚ·stat` Rafał i Lena · S3 `PO·odj` Rafał odchodzi w ciemność.

### 2.3 Oskar · 18:00–21:00 · Day 46–54

- **B37** `18:00` Dzień 47: krytyczny poziom powietrza, ból głowy, ostatnia korba trzeszczy. `[porada]` świeczka jako wskaźnik tlenu — zawodny i niebezpieczny.
  - S1 `PO·stat` senne twarze · S2 `D·stat` gasnąca świeczka · S3 `D·stat` HUD O₂ 17%.
- **B38** `18:30` Dzień 49: plan Oskara — laboratorium B3 ma własny szyb powietrzny na powierzchnię. Droga prowadzi przez gniazdo.
  - S1 `D·stat` plan bunkra · S2 `PŚ·stat` Oskar rysuje trasę · S3 `Z·stat` ty.
- **B39** `19:00` Dzień 50: przygotowania — maski, zimne okłady, mapa. Mila daje ci swój rysunek-mapę.
  - S1 `D·pan` sprzęt · S2 `PŚ·stat` Mila podaje kartkę · S3 `Z·stat` Oskar zakłada ci nauszniki.
- **B40** `19:30` Dzień 52: zejście na B3. Laboratorium, próbki, dziennik: SZARY miał pomagać żołnierzom przetrwać brak tlenu.
  - S1 `PO·pan` laboratorium · S2 `D·stat` próbki · S3 `D·stat` dziennik.
- **B41** `20:00` Gniazdo: dziesiątki śpiących Wydrążonych w zimnie. Oskar kaszle.
  - S1 `PO·naj` gniazdo · S2 `Z·stat` Oskar zakrywa usta · S3 `D·stat` jedna głowa się unosi.
- **B42** `20:30` Oskar trzyma drzwi, ty otwierasz zawór szybu. Powietrze rusza na górę. Oskar zostaje.
  - S1 `PŚ·drg 0,4` Oskar przy drzwiach · S2 `D·stat` zawór · S3 `Z·stat` ostatnie spojrzenie · S4 `PO·stat` drzwi się zamykają.

### 2.4 Wiadomość · 21:00–24:00 · Day 55–60

- **B43** `21:00` Dzień 55: żałoba. Bunkier znów oddycha. Brandt pierwszy raz cię słucha.
  - S1 `PO·stat` hala, wiatrak w kratce się kręci · S2 `D·stat` nauszniki Oskara · S3 `PŚ·stat` Brandt siada obok.
- **B44** `21:30` Dzień 57: radio z zewnątrz: „K-9, sterilization on day 60”.
  - S1 `D·stat` radio · S2 `Z·stat` Brandt blednie · S3 `Z·stat` ty.
- **B45** `22:00` Dzień 58: Brandt pokazuje pełny protokół — jeśli kwarantanna zawiedzie, bunkier się spala. Ratunku nigdy nie planowano.
  - S1 `D·stat` strona protokołu · S2 `PŚ·stat` Brandt mówi · S3 `PO·stat` cisza w hali.
- **B46** `22:30` Dzień 59: część ludzi chce szturmować wyjście. Uspokajasz ich: trzeba udowodnić, że bunkier jest czysty.
  - S1 `PO·drg 0,3` tłum · S2 `PŚ·stat` ty na skrzyni · S3 `Z·stat` Lena kiwa głową.
- **B47** `23:00` Dzień 60: nadajesz: „Sami spalimy B3. Dajcie nam 40 dni”. Cisza… „Day 100. Then we come in.”
  - S1 `Z·stat` ty przy mikrofonie · S2 `D·stat` szum · S3 `D·stat` HUD dzień 60 → 100.
- **B48** `23:30` Cliffhanger: ciepłe powietrze z szybu ogrzewa B3 — Wydrążeni się budzą. `[K]` zapowiedź części 3.
  - S1 `PO·naj` gniazdo, ruch · S2 `D·stat` termometr ↑ · S3 czerń + „Part 3”.

## ROZDZIAŁ 3 — „Ogień” (Day 61–100, 24:00–36:00)

### 3.1 Oblężenie od dołu · 24:00–27:00 · Day 61–70

- **B49** `24:00` `[K]` Przypomnienie części 2 w 30 s.
  - S1–S4 `D/Z·stat` szczelina, Oskar, radio, gniazdo.
- **B50** `24:30` Dzień 62: barykada na schodach, korytarz-pułapka przy zimnych rurach.
  - S1 `PO·stat` barykada · S2 `PŚ·stat` noszenie łóżek · S3 `D·stat` rury.
- **B51** `25:00` Dzień 64: co noc napierają. Śpicie na zmiany, oddychacie wolno. `[porada]` warty i sen zmianowy.
  - S1 `PO·stat` noc · S2 `D·drg 0,3` barykada drga · S3 `Z·stat` wartownik.
- **B52** `25:30` Dzień 66: Lena — w notatkach z B3: bakterię zabija tylko wysoka temperatura.
  - S1 `D·stat` notatki · S2 `PŚ·stat` Lena i ty · S3 `Z·stat` spojrzenie na generator.
- **B53** `26:00` Dzień 68: plan — diesel z generatora do B3 i podpalić. Koszt: koniec prądu, 30 dni w ciemności.
  - S1 `PO·stat` generator · S2 `D·stat` HUD diesel 400 L · S3 `PO·stat` głosowanie, wszyscy „za”.
- **B54** `26:30` Dzień 70: Brandt chce prowadzić. Ty: „Tylko ja znam drogę”.
  - S1 `PŚ·stat` dwie postacie · S2 `Z·stat` Brandt ustępuje · S3 `D·stat` mapa Mili.

### 3.2 Diesel · 27:00–30:00 · Day 71–80

- **B55** `27:00` Dzień 72: znoszenie kanistrów windą i schodami.
  - S1 `PO·stat` szyb windy · S2 `PŚ·stat` kanistry (podmiana póz) · S3 `D·stat` HUD diesel ↓ na górze / ↑ na dole.
- **B56** `27:30` Dzień 74: Mila zniknęła — zeszła szybem, żeby donieść ci mapę.
  - S1 `PO·stat` pusta prycza · S2 `D·stat` otwarty szyb · S3 `Z·stat` ty.
- **B57** `28:00` Dzień 75: Mila śpi zwinięta między Wydrążonymi. Wynosisz ją na wstrzymanym oddechu. Najmocniejsza scena napięcia.
  - S1 `PO·stat` gniazdo · S2 `PŚ·naj` podnosisz Milę · S3 `D·stat` licznik oddechu · S4 `Z·stat` Mila zakrywa ci usta dłonią.
- **B58** `28:30` Dzień 77: rozlewanie diesla po B3. Wydrążony Rafał stoi tuż obok i… waha się.
  - S1 `PO·pan` rozlewanie · S2 `Z·stat` Rafał · S3 `Z·stat` ty — nie oddychasz.
- **B59** `29:00` Dzień 79: zdalny zapłon nie działa. Brandt zostaje, żeby podpalić. Spowiedź Brandta.
  - S1 `PŚ·stat` Brandt i ty · S2 `D·stat` zapalniczka · S3 `Z·stat` Brandt: „Idź”.
- **B60** `29:30` Dzień 80: ogień. B3 płonie. Generator gaśnie — czerń.
  - S1 `PO·drg 0,8` ogień (PT: płomienie z wycinanek) · S2 `D·stat` gasnąca żarówka · S3 czerń 2 s.

### 3.3 Ciemność · 30:00–33:00 · Day 81–95

- **B61** `30:00` Dzień 82: życie po ciemku. Kreski dni liczysz palcami.
  - S1 `D·stat` dłoń na kreskach (tylko latarka na dynamo) · S2 `PO·stat` ledwo widoczna hala · S3 `D·stat` HUD dzień 82.
- **B62** `30:30` Dzień 85: przez wypalony szyb wpada zimne, czyste powietrze.
  - S1 `PO·naj` szyb, smuga światła · S2 `Z·stat` oddychasz pełną piersią · S3 `D·stat` HUD O₂ 21%.
- **B63** `31:00` Dzień 88: na górze ktoś kaszle. Ktoś ukrywa skorupę. Paranoja.
  - S1 `PO·stat` ludzie odsuwają się od siebie · S2 `Z·stat` przyjaciel Rafała chowa rękę · S3 `Z·stat` Lena.
- **B64** `31:30` Dzień 90: Lena bada wszystkich. Wynik dodatni ma przyjaciel Rafała — sam schodzi do spalonego B3.
  - S1 `D·stat` latarka na nadgarstkach · S2 `PŚ·stat` on wstaje · S3 `PO·odj` odchodzi.
- **B65** `32:00` Dzień 93: ostatnie racje. `[porada]` jak długo człowiek wytrzyma bez jedzenia vs bez wody.
  - S1 `D·stat` ostatnia puszka · S2 `PŚ·stat` dzielicie na 40 · S3 `D·stat` HUD racje 0.
- **B66** `32:30` Dzień 95: codziennie nadajesz „K-9 clean”. Tylko szum.
  - S1 `Z·stat` ty przy radiu · S2 `D·stat` kreska 95 · S3 `PO·stat` śpiący ludzie.

### 3.4 Dzień 100 · 33:00–36:00 · Day 96–100

- **B67** `33:00` Dzień 98: przy zaspawanych drzwiach syk palnika.
  - S1 `PŚ·stat` drzwi · S2 `D·naj` iskry przez spaw · S3 `Z·stat` ty.
- **B68** `33:30` Dzień 99: sterylizacja czy ratunek? Wszyscy przy drzwiach. Mila trzyma cię za rękę.
  - S1 `PO·stat` grupa · S2 `D·stat` dłonie · S3 `Z·stat` Lena.
- **B69** `34:00` Dzień 100: drzwi padają. Żołnierze Północy i Południa w kombinezonach — razem.
  - S1 `PO·drg 0,3` drzwi padają, światło · S2 `PŚ·stat` dwie naszywki obok siebie · S3 `Z·stat` ty mrużysz oczy.
- **B70** `34:30` Dekontaminacja, ruiny miasta, pierwszy oddech pod niebem.
  - S1 `PO·odj` ulica dnia 100 · S2 `Z·stat` twarz w słońcu · S3 `PŚ·stat` Mila biegnie.
- **B71** `35:00` Domknięcie: wieszasz nauszniki Oskara na tabliczce K-9, Mila przypina rysunek.
  - S1 `D·stat` nauszniki · S2 `D·stat` rysunek · S3 `PO·odj` bunkier znika w kadrze.
- **B72** `35:30` Outro: ściana ze 100 kreskami, napisy, zapowiedź kolejnej serii.
  - S1 `PO·pan` ściana kresek · S2 `D·stat` kreska 100 · S3 karta końcowa.
