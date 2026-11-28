"""Rozpiska filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (teatr papierowy, EN, ok. 5 min):
akt → scena → beat → ujęcie.

Reżyser 27.11.2026: tytuł z Rosją i 25 latami jako główny („wpisz tytuł ten z rosją 25 years czyli 3 jako główny
pierwszy”), film krótki 4–5 min do testu formatu, „chcę więcej ujęć, ew. zbliżeń, kenburnsów” → ok. 70 ujęć.
Kąt (rozmowa 27.11): esej Willa Collinsa „The Secret History of Dune” (LARB, 16.09.2017) — Herbert wziął słowa i zdania
z „The Sabres of Paradise” Lesley Blanch (1960) o imamie Szamilu; film opowiada historię Szamila i na końcu pokazuje słowa.
Wzór układu danych: docs/filmy/bonnie-i-clyde/ujecia/dane.py (te same zasady rytmu i ta sama krotka ujęcia).

ujęcie: (klucz, kadr, ruch, sekundy, opis wydarzenia, dźwięk)
- klucz — nazwa przyszłej funkcji ujęcia w output/szamil-diuna (`s_<klucz>`); brak funkcji = ujęcie do narysowania;
- kadr: TYT karta, PO plan ogólny, PP plan pełny, PŚ plan średni, Z zbliżenie, D detal;
  ruch: stat, naj (najazd), odj (odjazd), pan (panorama), jaz (jazda za postacią), szarp (szarpnięcie), kb (Ken Burns
  po prawdziwym obrazie XIX w. — zawsze z wydarzeniem w środku, Rytm 1);
- sekundy — None: długość z kwestii (oddech + słowa / TEMPO_EN + pauza po kwestii według granicy); liczba: ujęcie bez słów;
- dźwięk zaczynający się od „L:” to kwestia lektora po angielsku.
Źródło od 28.11.2026: zatwierdzony szkic D „Dwa zdania, trop słów i rzeka” (reżyser: „Zatwierdzam”) — A + słowo z Diuny
na początku każdego aktu, „siridar” przy kapitulacji, wolniejsza wymiana na rzece (szkice/buduj_szkice.py, wariant_d).
Ton: poważny, historyczny, bez polityki dnia dzisiejszego (księga świata D3); Szamil nie jest Paulem (D4).
"""

N = None
AKTY = [
 (0, "Prologue",
  "Zapowiedź 6 s z lektorem od pierwszej sekundy (o czym jest film), krótka kurtyna startu z pytaniem, wprowadzenie Szamila, "
  "hak: dwa niemal identyczne zdania — z Diuny (1965) i z książki o prawdziwej wojnie (1960) — i jedno pytanie, które prowadzi "
  "w retrospekcję (Podręcznik → Rytm, „Początek filmu”). Bez kurtyny przed aktem I.",
  [("Zapowiedź", "Skróty najmocniejszych ujęć", [
     ("Zapowiedź — skróty", [
      ("zap_akhulgo", "PO", "szarp", 0.7, "zapowiedź (skrót ujęcia „armaty”): armaty pod skałą Achulgo dają ognia, dym z bibuły",
       "L: Dune borrowed its words from the story of a real holy war, and of the imam who led it."),
      ("zap_tratwa", "PŚ", "szarp", 0.4, "zapowiedź (skrót ujęcia „tratwa”): nocą po rzece płynie tratwa ze słomianymi kukłami",
       "plusk, uderzenie"),
      ("zap_najazd", "PO", "szarp", 0.7, "zapowiedź (skrót ujęcia „jezdzcy”): jeźdźcy w czerni przeskakują mur winnicy",
       "tętent, uderzenie"),
      ("zap_rzeka", "PO", "szarp", 0.4, "zapowiedź (skrót ujęcia „brzegi”): dwa szeregi jeźdźców na brzegach rzeki", "rzeka, uderzenie"),
      ("zap_mundur", "PŚ", "szarp", 0.7, "zapowiedź (skrót ujęcia „mundur”): młody oficer zrywa epolety z munduru",
       "szelest, uderzenie"),
      ("zap_gunib", "PO", "szarp", 0.4, "zapowiedź (skrót ujęcia „flaga”): nad górską wioską wznosi się biała flaga",
       "wiatr, uderzenie"),
      ("zap_slowa", "D", "szarp", 0.7, "zapowiedź (skrót ujęcia „kanly”): z góry na nitkach zjeżdża słowo KANLY", "uderzenie"),
      ("zap_wydma", "PO", "szarp", 2.2, "zapowiedź: wydma z piasku zapada się w scenę, w jej miejscu wyrasta szczyt; ściemnienie",
       "piasek, gong; ściemnienie"),
     ]),
   ]),
   ("Kurtyna i hak", "Teatr papierowy, rama z rzeźbionego drewna", [
     ("Kurtyna startu i wprowadzenie", [
      ("tytul", "TYT", "naj", 3.7, "Kurtyna startu rozsuwa się na teatr: z lewej wydma z piasku, z prawej ośnieżone góry; na "
       "grani stoi lalka w czarnej czersce, plecami do widza; z góry zjeżdża szyld „The Imam Who Fought Russia for 25 Years”",
       "L: Almost no Dune fan knows his name."),
      ("przedstawienie", "PŚ", "naj", N, "Kamera najeżdża na lalkę na grani; lalka odwraca się do widza (orli profil, siwiejąca "
       "broda, biały turban na papasze); przy imieniu zjeżdża podpis „Imam Shamil”",
       "L: This is Imam Shamil, the man the Russian Empire hunted for twenty-five years."),
     ]),
     ("Dwa zdania", [
      ("cytat_diuna", "Z", "stat", N, "Na nitce zjeżdża biała karta z maszynopisem — zdanie o zabijaniu sztychem bez artyzmu "
       "z „Diuny” i podpis „Dune, 1965”; karta kołysze się i staje. TEKST KARTY DO SPRAWDZENIA W WYDANIU: źródła cytują "
       "„Killing with the tip/point lacks artistry”, mówi Duncan Idaho albo Gurney Halleck (fact-check 28.11)",
       "L: In Dune, a duke's son learns this rule with a blade in his hand."),
      ("kindzal", "D", "szarp", 1.4, "Papierowy kindżał spada ostrzem w dół i wbija się w deskę sceny obok karty; drży",
       "stuknięcie, metaliczne drżenie"),
      ("cytat_1960", "Z", "naj", N, "Obok zjeżdża pożółkła karta „To kill with the point lacked artistry.” z podpisem "
       "„1960”; kamera dojeżdża do obu kart",
       "L: Five years earlier, almost the same sentence was printed in a history book."),
      ("ramka", "D", "stat", 2.2, "Ramka lupy przesuwa się po obu zdaniach; słowa, które się powtarzają („kill… lacks artistry”), "
       "podświetlają się po kolei na złoto (wybór słów po sprawdzeniu brzmienia w wydaniu)", "szelest, dwa dzwonki"),
      ("ksiazka", "PŚ", "odj", N, "Karty odjeżdżają w górę; z dołu wysuwa się plansza-okładka „THE SABRES OF PARADISE · 1960” "
       "z rysunkiem gór i szabli; za nią cień lalki Szamila",
       "L: That book was about Shamil, and about a real holy war in the mountains of the Caucasus."),
     ]),
     ("Pytanie", [
      ("pytanie", "PO", "naj", N, "Wydma z lewej zapada się pod scenę, sypie się piasek; w jej miejscu wyrastają ośnieżone "
       "góry z mgłą z bibuły, kołyszą się i osiadają; ściemnienie i zawieszka „Dagestan, 1834”",
       "L: So how did a war in the mountains end up on a desert planet?"),
     ]),
   ]),
  ]),
 (1, "The Imam",
  "Szamil zostaje imamem (1834), muridzi przysięgają walkę na śmierć, carska armia wchodzi w doliny. Oblężenie Achulgo (1839): "
  "Szamil oddaje syna Dżamaluddina jako zakładnika, twierdza pada, imam ucieka nocą, a tratwa z kukłami odciąga pościg. Syn "
  "jedzie na północ, do Petersburga. Akt kończy się pytaniem bez odpowiedzi: jak odzyskać syna.",
  [("Góry i imam", "Góry Dagestanu: granie, wąwozy, kamienne wioski (auły) przyklejone do zboczy", [
     ("Nowy imam", [
      ("slowo_kindjal", "D", "stat", 1.8, "Nad górami na nitce zjeżdża słowo KINDJAL, obraca się i zmienia w kindżał, który "
       "wsuwa się za pas lalki Szamila na grani (słowo z Diuny otwiera akt I)", "szelest, szczęk"),
      ("imam", "PO", "jaz", N, "Na grani pojawiają się jeźdźcy w czerni, każdy z własnym opóźnieniem; na czele Szamil; zawieszka "
       "„Dagestan, 1834” odjeżdża w górę", "L: In 1834, the fighters of Dagestan chose a new imam: Shamil, a scholar from the "
       "mountain village of Gimry."),
      ("twarz", "Z", "naj", 1.8, "Zbliżenie: Szamil unosi wzrok, mruga raz; wiatr szarpie frędzlem turbanu", "wiatr"),
      ("muridzi", "PŚ", "stat", N, "Muridzi w czarnych czerkieskach jeden po drugim unoszą szable (fale, jeden spóźniony); nad "
       "nimi tabliczka „TO THE DEATH!”", "L: His warriors, the murids, swore to fight the Russian Empire to the death."),
      ("choragiew", "D", "stat", 1.6, "Czarna chorągiew rozwija się na wietrze nad aułem", "łopot płótna"),
     ]),
     ("Carska armia", [
      ("armia", "PO", "odj", N, "Kamera odjeżdża: z północy w doliny wchodzą rzędy piechoty w białych czapkach aż po horyzont, "
       "działa na wozach; mała lalka Szamila patrzy z grani", "L: From the north, the Tsar's armies pushed deeper into the "
       "mountains, valley by valley."),
     ]),
   ]),
   ("Achulgo", "Skała z twierdzą nad zakolem rzeki; obóz rosyjski w dolinie", [
     ("Oblężenie", [
      ("akhulgo", "PO", "naj", N, "Kamera dojeżdża do skały: na szczycie wyrasta twierdza z kamieni, kołysze się i osiada; "
       "u stóp rozstawiają się namioty; zawieszka „Akhulgo, 1839”",
       "L: In 1839, they trapped Shamil on the rock fortress of Akhulgo."),
      ("armaty", "PO", "szarp", 1.5, "Armaty dają ognia po kolei; dym z bibuły; kamienie odpryskują od murów; wstrząs kamery",
       "trzy wystrzały, kamienie"),
      ("szturm", "PP", "jaz", 1.8, "Drabiny przystawione do skały; żołnierze wspinają się, pierwszy spada, reszta się cofa",
       "okrzyki, upadek"),
     ]),
     ("Zakładnik", [
      ("zakladnik", "PŚ", "stat", N, "Na murze unosi się biała flaga; Szamil kładzie dłoń na ramieniu chłopca; przy imieniu "
       "zjeżdża podpis „Jamal al-Din, Shamil's son”", "L: To buy time, Shamil handed the Russians a hostage: his own son, "
       "Jamal al-Din, still a boy."),
      ("chlopiec", "PP", "jaz", 2.0, "Mały chłopiec idzie ścieżką między bagnetami w dół, do obozu; w połowie drogi ogląda się "
       "za siebie", "kroki, szczęk bagnetów"),
      ("ojciec", "Z", "stat", 1.6, "Zbliżenie: Szamil odwraca twarz, zaciska dłoń na rękojeści kindżału", "cisza, wiatr"),
     ]),
   ]),
   ("Ucieczka i syn", "Noc nad rzeką pod Achulgo; potem śnieżna droga na północ", [
     ("Ucieczka nocą", [
      ("ucieczka", "PO", "stat", N, "Noc, księżyc na nitce; twierdza płonie; maleńkie postacie spuszczają się na linach po skale "
       "do jaskini nad rzeką", "L: The fortress fell anyway. But Shamil escaped by night, down the cliff and along the river."),
      ("tratwa", "PŚ", "jaz", 2.4, "Gag: po rzece płynie tratwa ze słomianymi kukłami w papachach; żołnierze z latarniami "
       "biegną brzegiem za nią, „THERE!”; w tle w drugą stronę przemyka cień prawdziwych uciekinierów",
       "plusk, okrzyk „There!”"),
     ]),
     ("Syn na północ", [
      ("petersburg", "PO", "jaz", N, "Kryta kibitka jedzie śnieżną drogą na północ; w okienku twarz chłopca; na horyzoncie "
       "wyrastają złote iglice; zawieszka „St Petersburg”", "L: His son went the other way: north, to St Petersburg, to be "
       "raised as a Russian officer."),
      ("koniec_aktu1", "PŚ", "naj", N, "Szamil sam na grani, wiatr; ryje kreskę na kamieniu, za nią następne kreski (lata) — "
       "kurtyna zasuwa się w pauzie, na niej mała tabliczka „Act II · KANLY”, pod nią pytanie „How do you buy back a son?” (słowo "
       "KANLY zjeżdża na nitce na kurtynę)",
       "L: For fifteen years, Shamil had no way to get him back."),
     ]),
   ]),
  ]),
 (2, "The Son and the Princesses",
  "Dżamaluddin dorasta w Petersburgu jako oficer cara. Latem 1854 syn Szamila Ghazi Muhammad napada na Cinandali w Gruzji "
  "i porywa księżne Annę Czawczawadze i Warwarę Orbeliani z dziećmi; miesiące niewoli w Wedeno, cena: 40 000 rubli i syn. "
  "W marcu 1855 wymiana na rzece Miczik. Syn wraca w rosyjskim mundurze, w górach jest obcy, umiera w 1858.",
  [("Petersburg", "Sala balowa i plac apelowy w Petersburgu: kolumny, żyrandol, mundury", [
     ("Kadet", [
      ("kadet", "PŚ", "stat", N, "Mała lalka chłopca w mundurze kadeta chowa się w dół, na jej miejsce wysuwa się wysoki młody "
       "oficer z wąsikiem (ta sama twarz); podpis „Jamal al-Din” zjeżdża na chwilę", "L: In St Petersburg the boy grew up as a "
       "cadet, then as an officer in the Tsar's army."),
      ("bal", "PP", "pan", 2.2, "Oficer kłania się na balu, pary wirują za nim, żyrandol migocze", "walc, szmer sali"),
     ]),
   ]),
   ("Najazd na Cinandali", "Gruzińska posiadłość: dwór z drewnianym balkonem, winnice, mur; potem auł Wedeno", [
     ("Najazd", [
      ("kalendarz", "D", "stat", 1.8, "Kartki zdzieranego kalendarza lecą jedna po drugiej: 1840… 1848… 1854", "szelest kartek"),
      ("tsinandali", "PO", "naj", N, "Kamera dojeżdża do dworu wśród winnic; zawieszka „Tsinandali, Georgia, 1854”; na grzbiecie "
       "za murem wyrastają jeźdźcy; podpis „Ghazi Muhammad, Shamil's son”", "L: Then, in the summer of 1854, Shamil's son "
       "Ghazi Muhammad raided Tsinandali, a princely estate in Georgia."),
      ("jezdzcy", "PO", "szarp", 1.5, "Jeźdźcy przeskakują mur winnicy, liście winorośli fruwają", "tętent, okrzyki"),
      ("ksiezne", "PŚ", "jaz", N, "Dwie księżne w białych czepcach na koniach jeźdźców, dzieci przed nimi, za nimi guwernantka i służba; podpisy „Princess Anna "
       "Chavchavadze” i „Princess Varvara Orbeliani” zjeżdżają po kolei, za kwestią", "L: His riders carried off two "
       "princesses, Anna Chavchavadze and Varvara Orbeliani, with their children and household."),
      ("perly", "D", "stat", 1.4, "Sznur pereł pęka, perły toczą się po pyle i zostają", "stuk pereł"),
     ]),
     ("Cena", [
      ("vedeno", "PO", "naj", N, "Auł Wedeno w górach; księżne w kamiennym domu, za oknem straż; zawieszka „Vedeno”",
       "L: For months, they were held in Vedeno, Shamil's mountain capital."),
      ("cena", "PŚ", "stat", N, "Szamil przy niskim stoliku pisze list; pierwsza liczba na kartce jest ogromna, przekreśla ją "
       "i pisze „40,000”, obok rysunek chłopca i rządek jeńców",
       "L: Shamil first asked for far more. He settled for his son, forty thousand silver roubles, and an exchange of prisoners."),
      ("monety", "D", "stat", 1.7, "Na szalę spadają worki ze srebrnymi rublami, szala opada", "brzęk monet"),
     ]),
   ]),
   ("Wymiana na rzece", "Rzeka Miczik: kamieniste brzegi, płytki bród, las na zboczach", [
     ("Dwa brzegi", [
      ("rzeka", "PO", "naj", N, "Kamera dojeżdża do rzeki; z lewej i prawej ustawiają się dwa oddziały; zawieszka "
       "„River Michik, March 1855” (wzór do rysunku: ilustracja wymiany z 1855 w zbiorach Met, nr 423472)", "L: In March 1855, both sides met at the river Michik."),
      ("brzegi", "PO", "stat", 2.0, "Dwa szeregi jeźdźców na brzegach, chorągwie — czarna imamatu i biała flaga rozmów; konie "
       "przestępują z nogi na nogę", "rzeka, parskanie koni"),
      ("przeprawa_ksiezne", "PP", "jaz", 2.6, "Wóz z księżnymi, dziećmi i służbą przejeżdża bród w stronę Rosjan, za nim wozy z workami "
       "srebra jadą w drugą stronę, a jeńcy przechodzą pieszo; dziecko macha", "woda, koła"),
     ]),
     ("Syn wraca", [
      ("przeprawa_syn", "PP", "jaz", N, "Młody oficer w rosyjskim mundurze przejeżdża bród w drugą stronę, ku górom",
       "L: Jamal al-Din crossed the other way, still wearing his Russian uniform."),
      ("syn_brzeg", "Z", "naj", 2.4, "Zbliżenie: młody oficer zatrzymuje konia na środku brodu i patrzy na góry, z których "
       "wyjechał jako dziecko; waha się", "rzeka"),
      ("mundur", "PŚ", "stat", 2.0, "Na brzegu zrywa epolety, ktoś podaje mu czarną czerkieskę, zakłada ją", "szelest, stuk"),
      ("ojciec_brzeg", "Z", "naj", N, "Zbliżenie: Szamil na drugim brzegu; dłoń puszcza rękojeść kindżału",
       "L: Father and son had not seen each other for almost sixteen years."),
      ("uscisk", "Z", "naj", 3.6, "Muzyka milknie, zostaje szum rzeki; Szamil obejmuje syna, kamera bardzo wolno dojeżdża; na "
       "końcu uścisku wraca motyw ojca (emocjonalny szczyt filmu, Wytyczne 1.23)", "cisza, rzeka, motyw"),
     ]),
   ]),
   ("Obcy w górach", "Kamienny dom w aule, zima", [
     ("Obcy", [
      ("obcy", "PŚ", "stat", N, "Syn w czerkiesce siedzi w kamiennej izbie nad rosyjską książką; za oknem śnieg i góry; "
       "w myślach (obłok) zjeżdża miniaturka Petersburga", "L: But the mountains were no longer his home. He had grown up in "
       "the Tsar's capital, and he missed it."),
      ("choroba", "PŚ", "stat", N, "Syn kaszle w łóżku, przy nim świeca; Szamil siada obok",
       "L: Three years later, in 1858, he fell ill and died."),
      ("swieca", "D", "stat", 2.0, "Płomień świecy drży i gaśnie; smużka dymu", "zdmuchnięcie, cisza"),
      ("samotny", "PO", "odj", 3.0, "Szamil sam na grani w deszczu z bibuły; kamera odjeżdża — kurtyna zasuwa się, na niej "
       "mała tabliczka „Act III · SIRIDAR”, pod nią pytanie „How does a 25-year war end?”", "deszcz, kurtyna"),
     ]),
   ]),
  ]),
 (3, "Gunib",
  "1859: wojna przegrana, Szamil osaczony w Gunibie — ok. 400 obrońców wobec 16 000 żołnierzy. 6 września 1859 (25 sierpnia st. st.) "
  "62-letni imam schodzi i poddaje się księciu Bariatinskiemu (obraz Horschelta). Car przyjmuje go z honorami, wygnanie "
  "w Kałudze, pielgrzymka, śmierć w Medynie w 1871.",
  [("Ostatnia góra", "Gunib: wioska na płaskowyżu otoczonym urwiskami", [
     ("Osaczony", [
      ("gunib", "PO", "naj", N, "Kamera dojeżdża do płaskowyżu z wioską; mgła; zawieszka „Gunib, 1859”",
       "L: By 1859, the war was lost, and Shamil was cornered in the mountain village of Gunib."),
      ("liczby", "PO", "odj", N, "Kamera odjeżdża: garstka obrońców na górze, a dookoła rzędy wojska aż po horyzont; tabliczki "
       "„400” nad garstką i „16,000” nad wojskiem", "L: He had about four hundred fighters left. Around them stood sixteen "
       "thousand Russian soldiers."),
      ("wspinaczka", "PP", "jaz", 1.8, "O świcie żołnierze wspinają się po urwisku, jeden za drugim", "kamienie, oddechy"),
      ("flaga", "D", "stat", 2.1, "Nad Gunibem wznosi się biała flaga i powiewa", "łopot, cisza"),
     ]),
   ]),
   ("Kapitulacja", "Polana pod brzozami pod Gunibem; potem pałac i dom w Kałudze", [
     ("Kapitulacja", [
      ("kapitulacja", "PP", "stat", N, "Szamil, starszy, z siwą brodą, schodzi ścieżką do księcia siedzącego na kamieniu pod "
       "brzozą; przy nazwisku podpis „Prince Baryatinsky”, a na „siridar” nad księciem zjeżdża tabliczka SIRIDAR (zasiew "
       "puenty z aktu IV)", "L: That September, the sixty-two-year-old imam came down and surrendered to Prince "
       "Baryatinsky, the Tsar's viceroy. Shamil's word for such a man was siridar."),
      ("obraz_horschelt", "PO", "kb", 3.0, "Ken Burns po obrazie Theodora Horschelta „Kapitulacja Szamila” (1863; Commons: Horschelt._Surrender_of_Shamil._1863.jpg, domena publiczna): ramka "
       "przesuwa się od księcia do Szamila, a w obraz wsuwa się papierowa dłoń z białą flagą", "szelest, smyczki"),
      ("car", "PŚ", "stat", N, "Szamil staje przed carem Aleksandrem II w sali z kolumnami; car podaje mu rękę; podpis „Tsar "
       "Alexander II”", "L: The Tsar received him with honours, then sent him into a comfortable exile in Kaluga."),
      ("zdjecie_1859", "D", "kb", 2.4, "Ken Burns po portrecie Szamila z 1859 (Andriej Denier, Commons: Shamil_by_Denier.jpg, domena publiczna); obok zapala się świeca i oświetla twarz",
       "zapałka, płomień"),
     ]),
     ("Pielgrzymka", [
      ("medyna", "PO", "jaz", N, "Karawana na pustyni pod księżycem; Szamil na wielbłądzie; zawieszka „Medina, 1871”; kurtyna "
       "zasuwa się, na niej mała tabliczka „Act IV · SIETCH”, pod nią pytanie „What did Dune take?”", "L: Years later he was allowed to go on pilgrimage, and he died in "
       "Medina in 1871."),
     ]),
   ]),
  ]),
 (4, "The Words",
  "1960: Lesley Blanch opisuje wojnę Szamila w „The Sabres of Paradise”; 1965: „Diuna” Franka Herberta. Słowa na nitkach: "
  "kanly, kindjal, chakobsa, sietch i tabr, padishah i siridar; przysłowie z gór → z pustyni. Zastrzeżenie: Herbert czerpał "
  "z wielu źródeł, Paul to nie Szamil. Puenta: następna Diuna opowiada, co dzieje się po wygranej świętej wojnie — wojna "
  "Szamila skończyła się białą flagą.",
  [("Książka", "Pracownia pisarki w Londynie; potem stół Herberta", [
     ("Blanch i Herbert", [
      ("blanch", "PŚ", "stat", N, "Pisarka przy maszynie do pisania; kartki wylatują i składają się w książkę z szablami na "
       "okładce; podpis „Lesley Blanch”; zawieszka „1960”", "L: A century later, the writer Lesley Blanch told his story in a "
       "book: The Sabres of Paradise."),
      ("herbert", "PŚ", "naj", N, "Mężczyzna z brodą przy maszynie; z kartki zamiast tuszu sypie się piasek i usypuje wydmę; "
       "podpis „Frank Herbert”; zawieszka „1965”", "L: Five years later came Frank Herbert's Dune, and some of her words "
       "were in it."),
     ]),
   ]),
   ("Słowa", "Scena z wydmą po lewej i górami po prawej; słowa zjeżdżają na nitkach z gór na pustynię", [
     ("Słowa", [
      ("kanly", "D", "stat", N, "Słowo KANLY zjeżdża nad góry, przesuwa się na nitce nad wydmę; pod nim dwa skrzyżowane kindżały",
       "L: Kanly, the blood feud of the mountain clans, became a feud between great houses."),
      ("kindjal", "D", "stat", N, "Słowo KINDJAL; kindżał z gór przechodzi z dłoni murida do dłoni w rękawicy z herbem",
       "L: The kindjal, the dagger no mountain man went without, became a weapon of dukes."),
      ("chakobsa", "D", "stat", N, "Słowo CHAKOBSA; myśliwy szepcze do drugiego, z ust wylatują litery i odlatują nad wydmę",
       "L: Chakobsa, a hunters' language of the Caucasus, became a language of Dune."),
      ("sietch", "D", "stat", N, "Słowa SIETCH i TABR zjeżdżają osobno i sklejają się w tabliczkę „SIETCH TABR” nad jaskinią "
       "w skale pustyni", "L: Sietch and tabr, Cossack words for a camp, became Paul's home: Sietch Tabr."),
      ("tytuly", "PŚ", "stat", N, "Nad lalką cara zjeżdża tabliczka PADISHAH, nad księciem Bariatinskim (ta sama lalka co przy "
       "kapitulacji) SIRIDAR; potem obie przesuwają się nad wydmę", "L: Even padishah, Shamil's word for the Tsar, and "
       "siridar, his word for the man who took his surrender, ended up in Herbert's empire."),
      ("szamil_patrzy", "Z", "stat", 1.6, "Zbliżenie: lalka Szamila z boku sceny odprowadza wzrokiem słowa, które odpływają na "
       "nitkach nad wydmę", "szelest nitek"),
     ]),
     ("Przysłowie i zastrzeżenie", [
      ("przyslowie", "Z", "stat", N, "Dwie karty obok siebie: „…wisdom from the hills.” i „…wisdom from the desert.”; słowo "
       "„hills” odpada i spada, na jego miejsce zjeżdża „desert”", "L: And a mountain proverb, wisdom comes from the hills, "
       "became wisdom from the desert."),
      ("zastrzezenie", "PO", "odj", N, "Kamera odjeżdża: na scenie leżą stosy innych książek i map pustyni; lalka Szamila stoi "
       "z boku, nie na środku", "L: Herbert drew on many sources, and Paul is not Shamil. But these words came from his war."),
     ]),
   ]),
   ("Puenta", "Cała scena: wydma i góry obok siebie", [
     ("Dwie wojny", [
      ("dwie_wojny", "PO", "naj", N, "Wydma i góry obok siebie; nad wydmą unosi się złote słońce, nad górami szare chmury",
       "L: The next Dune film is about what happens after a holy war is won."),
      ("biala_flaga", "PŚ", "naj", N, "Szamil na grani podnosi białą flagę; obok cień syna w mundurze, który się rozwiewa",
       "L: Shamil's war ended on a mountain, with a white flag, and a son he could not keep."),
      ("dzieki", "TYT", "stat", N, "Kurtyna zasuwa się; na niej szyld „Paper Theatre”", "L: Thanks for watching Paper Theatre."),
     ]),
   ]),
  ]),
]

HAK = ["tytul", "przedstawienie", "cytat_diuna", "cytat_1960", "ksiazka", "pytanie"]  # w haku szybciej
JEZYK = "en"
TEMPO_EN = 2.84  # angielski klon (TEATR): „Pierwszy cesarz” EN, 1233 słowa w 434 s nagrań (17.11.2026)
SLOWNIE = {"1834": "eighteen thirty-four", "1839": "eighteen thirty-nine", "1854": "eighteen fifty-four",
           "1855": "eighteen fifty-five", "1858": "eighteen fifty-eight", "1859": "eighteen fifty-nine",
           "1871": "eighteen seventy-one"}
WYDLUZ = {"armia": 1.5, "akhulgo": 1.5, "liczby": 1.5, "pytanie": 1.2, "imam": 0.8}  # wojsko, budowa, przemiana dekoracji
PAUZA_PO = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}
HAK_PAUZA = 1.0


def kwestia(dzwiek):
    return dzwiek[2:].strip() if dzwiek.startswith("L:") else ""


def slownie(txt):
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    return txt


def okno_kwestii(dzwiek, hak=False):
    """(start, długość) kwestii w ujęciu: oddech, potem mowa według tempa lektora (nagrań jeszcze nie ma)."""
    txt = kwestia(dzwiek)
    if not txt:
        return (0.0, 0.0)
    return (0.4 if hak else 0.6, len(slownie(txt).split()) / TEMPO_EN)


def ujecia(akt=None):
    """Płaska lista ujęć: (akt, nr w akcie, klucz, kadr, ruch, sekundy, opis, dźwięk). Sąsiednie ujęcia różnią się co
    najmniej o ¼ s (Podręcznik, „Rytm” 2)."""
    out, prev = [], None
    for n, _, _, sceny in AKTY:
        k = 0
        for si, (_, _, beaty) in enumerate(sceny):
            for bi, (_, shots) in enumerate(beaty):
                for ui, (klucz, kadr, ruch, sec, opis, dzwiek) in enumerate(shots):
                    k += 1
                    if sec is None:
                        hak = klucz in HAK
                        granica = ("ujecie" if ui < len(shots) - 1 else "beat" if bi < len(beaty) - 1
                                   else "scena" if si < len(sceny) - 1 else "akt")
                        start, mowa = okno_kwestii(dzwiek, hak)
                        sec = round(start + mowa + (HAK_PAUZA if hak else PAUZA_PO[granica]) + WYDLUZ.get(klucz, 0.0), 1)
                        if prev is not None and abs(sec - prev) < 0.25:
                            sec = round(prev + 0.3, 1)
                    prev = sec
                    if akt is None or akt == n:
                        out.append((n, k, klucz, kadr, ruch, sec, opis, dzwiek))
    return out


if __name__ == "__main__":
    rows = ujecia()
    total = sum(r[5] for r in rows)
    mowa = sum(okno_kwestii(r[7])[1] for r in rows)
    for n, t, *_ in AKTY:
        a = [r for r in rows if r[0] == n]
        print(f"akt {n} {t:28s} {len(a):3d} ujęć {sum(r[5] for r in a):6.1f} s")
    print(f"razem {len(rows)} ujęć, {int(total // 60)}:{total % 60:04.1f}, lektor {mowa:.0f} s ({mowa / total:.0%}), "
          f"bez słów {sum(1 for r in rows if not kwestia(r[7]))} ujęć, słów {sum(len(slownie(kwestia(r[7])).split()) for r in rows)}")
BEZ_NAGRAN = [False]  # zgodność z render.py („Bonnie and Clyde”): długości z tempa lektora, nagrań jeszcze nie ma
