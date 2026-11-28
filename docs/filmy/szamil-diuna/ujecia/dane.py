"""Rozpiska filmu „The Imam Who Fought Russia for 25 Years — and Ended Up in Dune” (teatr papierowy, EN): akt → scena →
beat → ujęcie.

**Przebudowa 28.11.2026 (szkic E).** Reżyser po obejrzeniu pierwszej minuty wersji D (76 ujęć, 5:55): „są trzy ujęcia jakieś
długie, nagle jest jedno, które ma pół sekundy… dwa ujęcia długie, a jeszcze nic się na nich nie dzieje… każde ujęcie powinno
być innej długości, zależne od tego, co jest w scenariuszu i w narracji”, „nie róbmy stricte 4–5-minutowego filmu”, „cały
początek… nic nie wiadomo, o co chodzi”, „brakuje gagów”. Diagnoza (scratchpad rytm.py, 28.11): w D 34 z 76 ujęć było bez
słów (1,4–2,4 s), 10 krótkich wstawek stało samotnie między długimi ujęciami z kwestią, w których lalka tylko stała; mediana
5,4 s. „Syn słońca” (najlepsze utrzymanie widzów) i „Bonnie and Clyde”: kwestia w 80–85 % ujęć, mediana ok. 10 s, w każdym
ujęciu 2–4 wydarzenia pod słowa lektora. Szkic E bierze ten wzór:
- **ujęcie = kwestia + wydarzenia**: 1–3 zdania lektora (13–27 słów) i w opisie sekundy wydarzeń, które dzieją się wtedy,
  kiedy lektor o nich mówi, albo tuż po (Wytyczne 0.4, 1.11);
- **bez samotnych wstawek**: ujęcie bez słów to zapowiedź, kurtyna albo emocjonalne trzymanie (uścisk); `kontrola_rytmu()`
  wyłapuje krótkie ujęcie między dwoma długimi, serie ujęć tej samej długości i ujęcia z kwestią bez wydarzeń w opisie;
- **otwarcie, które się rozumie**: Diuna, którą widz zna (pustynia, sietch, kanly, kindżał) → te słowa są z prawdziwej wojny
  w górach → kim był Szamil → hak (syn oddany wrogowi wraca w rosyjskim mundurze) → jedno pytanie → Gimry 1832;
- **słowa z Diuny zasiane w historii** (kanly przy wendecie 1834, padyszach w liście do cara, siridar przy kapitulacji),
  a w ostatnim akcie odlatują na nitkach na pustynię — widz je rozpoznaje;
- **silnik humoru**: papiery imperium kontra góry (pieczątka „FINISHED” / „VICTORY!” / „CAPTURED” — trzecie podejście już
  bez żartu), Szamil, którego nigdy nie ma tam, gdzie celują, koza (zasiew w Gimry, Dargo, puenta w Kałudze), teatr
  świadomy siebie (robak z Diuny na złej scenie); granica tonu: bez gagów przy śmierci, zakładniku i zasadzce (Humor).
- **długość z historii** (ok. 9:40), nie z formatu.

ujęcie: (klucz, kadr, ruch, sekundy, opis wydarzenia, dźwięk)
- klucz — nazwa funkcji ujęcia w output/szamil-diuna (`s_<klucz>`);
- kadr: TYT karta, PO plan ogólny, PP plan pełny, PŚ plan średni, Z zbliżenie, D detal;
  ruch: stat, naj (najazd), odj (odjazd), pan (panorama), jaz (jazda za postacią), szarp (szarpnięcie);
- sekundy — None: długość z kwestii (oddech + słowa / TEMPO_EN + pauza po kwestii według granicy + WYDLUZ); liczba:
  ujęcie bez słów albo długość ustawiona ręką;
- dźwięk zaczynający się od „L:” to kwestia lektora po angielsku.
Ton: historyczny, bez polityki dnia dzisiejszego (księga D3); Szamil nie jest Paulem (D4).
"""
import json
from pathlib import Path


N = None
AKTY = [
 (0, "Prologue",
  "Początek w akcji (reżyser 28.11: „w każdym filmie dopiero po 2–3 minutach zaczyna się akcja… początek ma angażować”): "
  "zapowiedź 6 s z lektorem i krótka kurtyna startu; zaraz po niej akt I zaczyna się walką w Gimry 1832 (bez kurtyny przed "
  "aktem I).",
  [("Zapowiedź", "Skróty najmocniejszych ujęć filmu", [
     ("Zapowiedź — skróty", [
      ("zap_skok", "PP", "szarp", 0.7, "skrót ujęcia „tolstoj”: jeźdźcy w czerni wypadają zza wzgórza (skok jest w otwarciu)",
       "L: Some of Dune's words came from a real holy war, fought in the snow against an empire."),
      ("zap_armaty", "PO", "szarp", 0.4, "skrót ujęcia „armaty”: armaty pod Achulgo dają ognia", "huk, uderzenie"),
      ("zap_tratwa", "PŚ", "szarp", 0.7, "skrót ujęcia „tratwa”: tratwa ze słomianymi kukłami nocą", "plusk, uderzenie"),
      ("zap_dargo", "PO", "szarp", 0.4, "skrót ujęcia „dargo”: płonąca stolica Szamila", "ogień, uderzenie"),
      ("zap_najazd", "PO", "szarp", 0.7, "skrót ujęcia „tsinandali”: jeźdźcy przeskakują mur winnicy", "tętent, uderzenie"),
      ("zap_rzeka", "PO", "szarp", 0.4, "skrót ujęcia „przeprawa”: wóz z księżnymi w brodzie", "woda, uderzenie"),
      ("zap_gunib", "PP", "szarp", 0.7, "skrót ujęcia „szturm_gunib”: żołnierze na linach na urwisku", "kamienie, uderzenie"),
      ("zap_slowa", "D", "szarp", 0.4, "skrót ujęcia „slowa1”: słowo KANLY leci na nitce z gór nad wydmę", "uderzenie"),
      ("zap_wydma", "PO", "szarp", 1.6, "skrót ujęcia „herbert”: z maszyny do pisania sypie się piasek, wyrasta wydma; ściemnienie",
       "piasek, gong; ściemnienie"),
     ]),
   ]),
   ("Kurtyna", "Kurtyna startu rozsuwa się na pustynię Diuny (teatr świadomy siebie)", [
     ("Kurtyna startu", [
      ("tytul", "TYT", "naj", 4.4, "Kurtyna startu rozsuwa się na pustynię: wydmy, dwa słońca, na grzbiecie wydmy mała lalka w "
       "ciemnym płaszczu pustyni (fremen); 0,5 s z góry zjeżdża szyld „The Imam Who Fought Russia for 25 Years”; 2,6 s piasek "
       "na grzbiecie drga (coś jest pod spodem)", "L: Almost no Dune fan knows his name."),
     ]),
   ]),
  ]),
 (1, "The New Imam",
  "Otwarcie w akcji bez kurtyny (reżyser 28.11): Gimry 1832 — oblężenie wieży, śmierć Ghaziego, skok Szamila nad bagnetami "
  "(legenda), ucieczka z raną; most do Diuny (te słowa wiek później trafiły do powieści) i zwrot (są z gór Kaukazu); kim jest "
  "człowiek ze skoku; hak (syn oddany wrogowi wraca w rosyjskim mundurze) i jedno pytanie, które prowadzi do 1834. Potem 1834: "
  "drugi imam ginie w wendecie (kanly), Szamil zostaje imamem; car Mikołaj I chce gór „dolina po dolinie”; wojsko wchodzi, "
  "muridzi uderzają i znikają. (Sceny otwarcia były w prologu; akt I miał wtedy 43 s, poniżej 55 s z księgi — 28.11.)",
  [("Gimry", "Wąwóz z górską wioską: kamienne domy tarasami, kamienna wieża przy ścieżce, potok", [
     ("Wieża", [
      ("gimry", "PO", "naj", N, "0,6 s wioska w wąwozie buduje się po kurtynie, zjeżdża zawieszka „Gimry, Dagestan, 1832”; "
       "2,6 s przy imieniu na płaskim dachu staje Ghazi Muhammad, podpis „Ghazi Muhammad, the first imam”; 5,8 s obok niego "
       "Szamil (rówieśnik i przyjaciel Ghaziego z dzieciństwa w Gimry), podpis „Shamil”; 7 s za granią wysuwają się po kolei białe czapki rosyjskich żołnierzy; 8,4 s Szamil "
       "wskazuje je ręką, Ghazi odwraca głowę",
       "L: In 1832, Russian soldiers came to Gimry for Ghazi Muhammad, the first imam of Dagestan, and for his childhood friend, Shamil."),
      ("wieza", "PP", "stat", N, "Kamienna wieża; 0,6 s Ghazi i Szamil w oknach wieży, dookoła wysuwa się szereg żołnierzy; "
       "2–4 s błyski i dymki wystrzałów z obu stron; 4,6 s na „was killed” Ghazi znika z okna, a jego papacha spada z okna "
       "i zostaje na ziemi (ślad śmierci, bez gagu, Wytyczne 1.11); 7 s pod drzwiami wieży żołnierze stają w szereg z bagnetami "
       "w górę; Szamil w drzwiach na podwyższonym progu",
       "L: The two men were trapped in a stone tower with a handful of fighters. Ghazi Muhammad was killed, and soldiers with bayonets waited at the door."),
      ("skok", "PP", "szarp", N, "0,6 s Szamil na progu wieży nad szeregiem bagnetów, unosi szablę; 2,2 s na „jumped” skacze "
       "łukiem nad głowami żołnierzy (muzyka milknie, bęben), 3,4 s ląduje za ich plecami; 4–6 s żołnierze obracają się "
       "jeden po drugim w złą stronę, nad każdym „?!”; 6,8 s Szamil biegnie w wąwóz, trzyma się za bok; gag: ostatni żołnierz "
       "wciąż celuje w puste drzwi",
       "L: Then, the story goes, Shamil jumped. He leapt clean over the soldiers' heads and landed behind them."),
      ("rana", "PŚ", "jaz", N, "Wąwóz o zmierzchu; 0,6 s Szamil biegnie, zatacza się, ręka przy piersi; 3,4 s żołnierze strzelają "
       "w pusty wąwóz, dymki; 5 s Szamil chowa się w szałasie pasterza; 7 s z ciemności wychodzi koza, obwąchuje go i liże "
       "po brodzie, Szamil kładzie palec na ustach („SHH!”) — zasiew kozy",
       "L: He escaped into the gorge with a bayonet wound through his chest, and hid in the mountains until he could fight again."),
     ]),
   ]),
   ("Diuna i zwrot", "Teatr papierowy w ramie z rzeźbionego drewna: najpierw cała scena to pustynia, potem góry Kaukazu", [
     ("Diuna, którą widz zna", [
      ("arrakis", "PO", "pan", N, "Most z Gimry do Diuny („that war turned up in a novel”). Pustynia: 0,6 s za wydmą wynurza się papierowy robak z Diuny (pierścienie, okrągła paszcza) "
       "i zanurza się z powrotem; 2,6 s na „kindjal” fremen wyciąga kindżał, nad nim KINDJAL; 4,6 s na „great houses” po bokach "
       "zjeżdżają dwie chorągwie rodów (zielona i niebieska, bez herbów z filmów), między nimi KANLY; 6,8 s na „sietches” w skale "
       "otwiera się jaskinia, nad nią SIETCH; 9 s gag: robak wynurza się pod kartą KANLY, połyka ją i beka chmurką piasku; fremeni "
       "patrzą na siebie. W Diunie kanly to wendeta wielkich rodów, nie fremenów (sprawdzenie faktów 28.11)",
       "L: A century later, that war turned up in a novel. In Dune, fighters carry a dagger called a kindjal, great houses swear blood feuds called kanly, and desert people live in caves called sietches."),
      ("zamiana", "PO", "naj", N, "0,6 s na „weren't made up” wydmy zapadają się pod scenę, sypie się piasek; 2,5 s wyrastają "
       "ośnieżone góry Kaukazu, kołyszą się i osiadają; 4,5 s z góry zaczyna padać papierowy śnieg; 6 s zza grani wysuwają się "
       "kamienne domy aułu; 8,8 s gag: fremen, który został na scenie, trzęsie się z zimna, tabliczka „BRRR!”, a zza kulis "
       "wysuwa się laska maszynisty z hakiem i ściąga go za kołnierz ze sceny",
       "L: But those words weren't made up for another planet. They come from the Caucasus mountains, and from a war that lasted twenty-five years."),
     ]),
     ("Szamil", [
      ("przedstawienie", "PŚ", "naj", N, "Kamera najeżdża na lalkę na grani (plecami do widza); 0,8 s Szamil odwraca się: orli "
       "profil, czarna broda, biały turban na papasze; 1,8 s przy imieniu zjeżdża podpis „Imam Shamil”; 3,5 s za nim wysuwają się "
       "jeden po drugim muridzi w czarnych czerkieskach; 6,2 s na „most wanted” nad Szamilem spada tabliczka „WANTED BY THE TSAR”, "
       "a Szamil spokojnie odsuwa ją pochwą kindżału",
       "L: The man who made that jump became Imam Shamil, a scholar from the mountains and the most wanted man in the Russian Empire."),
     ]),
   ]),
   ("Hak", "Rzeka w górach: dwa brzegi i bród (ta sama rzeka wróci w akcie IV)", [
     ("Syn", [
      ("hak_syn", "PO", "jaz", N, "Rzeka w górach: z lewej brzeg z rosyjskimi żołnierzami, z prawej jeźdźcy w czerni; 0,6 s Szamil "
       "na prawym brzegu prowadzi za rękę małego chłopca w papasze, chłopiec idzie sam w lewo (przy „hostage” chłopiec chowa się "
       "za szeregiem Rosjan); 4,6 s na „Sixteen years later” kartki kalendarza przelatują nad rzeką; 6 s z lewego brzegu w bród "
       "wjeżdża młody mężczyzna w rosyjskim mundurze, na koniu; 9,2 s staje na środku brodu i patrzy na Szamila — bez imienia "
       "i bez podpisu (imię pada w akcie I)",
       "L: To buy time in a siege, he gave up his own little boy as a hostage. Sixteen years later, that boy rode home through a river in a Russian officer's uniform."),
      ("pytanie", "PO", "naj", N, "Rzeka zamiera; 0,6 s na „desert planet” połowa gór zapada się w piasek, a nad nią na moment "
       "wyrasta wydma i znów się chowa; 4,5 s na „Follow” kartki kalendarza lecą wstecz: 1855… 1850… 1845… 1839… 1834, ostatnia "
       "uderza maszynistę w kulisach („OUCH!”); na „jump” zawieszka „Dagestan, 1834”; ściemnienie",
       "L: So what is a war fought in the snow doing on a desert planet? Follow the man from the tower, two years after his famous jump."),
     ]),
   ]),
   ("Nowy imam", "Meczet w aule (teatr cieni), potem plac w aule na grani", [
     ("Kanly", [
      ("kanly_1834", "PO", "stat", N, "Teatr cieni: za podświetlonym parawanem sylwetka meczetu z kopułą; zawieszka „1834”; 2 s "
       "dwie sylwetki z kindżałami podchodzą do trzeciej; 4 s trzecia sylwetka (drugi imam) opada za parawan — bez gagu; "
       "6,4 s na „kanly” nad parawanem zjeżdża na nitce duże słowo KANLY i kołysze się",
       "L: Two years on, the second imam was killed in a blood feud. In the mountains, such a feud carried a special name: kanly."),
     ]),
   ]),
   ("Imam", "Plac w aule na grani", [
     ("Przysięga", [
      ("imam", "PO", "naj", N, "Plac w aule; 0,6 s Szamil (zdrowy) wchodzi na kamień; 1,5–4 s muridzi wysuwają się po kolei "
       "zza rampy, każdy z własnym opóźnieniem; 4,5 s na „imam” wszyscy unoszą szable falą; 6,6 s nad nimi zjeżdża tabliczka "
       "„TO THE DEATH!”; 8,6 s gag: ostatni murid unosi szablę spóźniony, odwrotnie, sprawdza i poprawia",
       "L: So in 1834, the fighters made Shamil their imam, and his murids swore to fight the Russian Empire to the death."),
     ]),
   ]),
   ("Imperium", "Gabinet w Petersburgu: wielka mapa Kaukazu na stole; potem dolina z kolumną wojska", [
     ("Mapa i marsz", [
     ]),
   ]),
   ("Petersburg", "Gabinet w Petersburgu: wielka mapa Kaukazu na stole", [
     ("Mapa", [
      ("mapa", "PŚ", "stat", N, "Gabinet: car Mikołaj I przy stole z wielką papierową mapą gór; podpis „Tsar Nicholas I”; 2 s "
       "generał wsuwa kijem rzędy cynowych żołnierzyków w doliny; 4,2 s na „valley by valley” papierowa góra na mapie "
       "podnosi się z łoskotem i żołnierzyki zjeżdżają z niej jak z sanek; 6,4 s generał łapie ostatniego; car marszczy brwi",
       "L: In St Petersburg, Tsar Nicholas the First wanted these mountains conquered, valley by valley, whatever it cost."),
     ]),
   ]),
   ("Dolina", "Dolina z kolumną wojska, lasy i skały", [
     ("Marsz", [
      ("marsz", "PO", "jaz", N, "Dolina: kolumna piechoty w białych czapkach, armata na wozie z koniem i woźnicą, chorągiew; "
       "2 s na „struck” zza skał wyskakują muridzi, dymki strzałów, i chowają się z powrotem; 4,5 s na „vanished” w lesie nikogo; "
       "6,5 s gag: murid wysuwa się za plecami ostatniego żołnierza i stuka go w ramię, żołnierz się odwraca — pusto; kurtyna",
       "L: His armies marched in. Shamil's men struck from the forests and the cliffs, and then simply vanished."),
     ]),
   ]),
  ]),
 (2, "The Hostage",
  "Achulgo 1839: 80 dni oblężenia, Szamil oddaje syna Dżamaluddina jako zakładnika, twierdza pada, Szamil ucieka nocą (tratwa "
  "z kukłami odciąga pościg). Petersburg ogłasza koniec Szamila (pieczątka 1), a rok później powstaje Czeczenia. Syn jedzie do "
  "Petersburga.",
  [("Achulgo", "Skała z twierdzą nad zakolem rzeki; obóz rosyjski w dolinie", [
     ("Oblężenie", [
      ("akhulgo", "PO", "naj", N, "0,6 s na skale wyrasta twierdza z kamieni, kołysze się i osiada; zawieszka „Akhulgo, 1839”; "
       "3 s u stóp wyrastają namioty; 5 s koń wciąga armatę na pozycję, woźnica na koźle; 8 s na „eighty days” nad obozem "
       "przesuwa się księżyc i słońce dwa razy (dni mijają)",
       "L: In 1839, the Russians trapped Shamil, his family and his fighters on the rock fortress of Akhulgo, and the siege lasted eighty days."),
      ("armaty", "PO", "szarp", N, "0,6 s armaty dają ognia po kolei, dym z bibuły, kamienie odpryskują od murów, wstrząs "
       "kamery; 3,5 s na „attack after attack” drabina przy skale, żołnierze się wspinają; 5,4 s gag: obrońca odpycha drabinę, która "
       "z wolna przechyla się do tyłu z żołnierzem uczepionym na górze, „WHOA!”, i znika za skałą — bez upadku na oczach",
       "L: Cannons pounded the walls day after day, and attack after attack up the cliff was thrown back."),
     ]),
     ("Zakładnik", [
      ("amanat", "PŚ", "stat", N, "Brama twierdzy; 0,6 s nad murem unosi się biała flaga rozmów; 2,5 s Szamil wychodzi z małym "
       "chłopcem w papasze, dłoń na jego ramieniu; 5,6 s przy imieniu zjeżdża podpis „Jamal al-Din, Shamil's son”; 7,4 s dłoń "
       "Szamila zostaje jeszcze chwilę i powoli puszcza; bez gagu",
       "L: To win time for talks, Shamil did something unthinkable. He gave the Russians an amanat, a hostage of honour: his eldest son, Jamal al-Din, still a boy."),
      ("chlopiec", "PP", "jaz", N, "Rosyjski oficer prowadzi chłopca ścieżką w dół przed szeregiem bagnetów do obozu; 3 s w połowie "
       "drogi chłopiec ogląda się za siebie; na górze Szamil zaciska dłoń na rękojeści kindżału; 6 s chłopiec znika między namiotami",
       "L: The boy was led down to the enemy camp. The talks failed anyway."),
      ("upadek", "PO", "stat", N, "0,6 s nad twierdzą unosi się dym, mury płoną; 2,5 s na murze staje rosyjska chorągiew; "
       "4 s żołnierze z latarniami schodzą do jaskiń w skale i zaglądają w każdą; bez gagu",
       "L: In August, the fortress fell. The Russians searched the ruins and the caves for Shamil's body."),
     ]),
   ]),
   ("Ucieczka", "Noc nad rzeką pod Achulgo; potem gabinet w Petersburgu i śnieżna droga na północ", [
     ("Tratwa", [
      ("tratwa", "PŚ", "jaz", N, "Noc, księżyc, płonąca twierdza w tle; 0,6 s po rzece płynie tratwa ze słomianymi kukłami "
       "w papachach; 3 s żołnierze z latarniami biegną brzegiem za tratwą, „THERE!”, strzelają, dymki; 6 s w tle w przeciwną "
       "stronę po skale przemyka cień Szamila z rodziną; 9,4 s gag: kukle odpada głowa i spada do wody, żołnierz z latarnią "
       "zastyga, tabliczka „…”",
       "L: But Shamil had slipped out by night. While soldiers chased a raft of straw dummies down the river, he climbed away along the cliff."),
     ]),
   ]),
   ("Gabinet", "Gabinet w Petersburgu: biurko urzędnika, okno", [
     ("Raport", [
      ("raport", "PŚ", "stat", N, "Gabinet w Petersburgu; 0,6 s urzędnik kładzie na biurku raport; 1,4 s wielka pieczątka "
       "uderza: „SHAMIL: FINISHED” (zasiew gagu pieczątki); urzędnik zadowolony; 4,4 s na „Within a year” za oknem przesuwa się "
       "kalendarz 1840; 5,6 s przez okno wpada kamień z kartką „CHECHNYA RISES”, pieczątka spada z biurka, „OOPS”",
       "L: St Petersburg stamped the case closed: Shamil was finished. Within a year, most of Chechnya rose up behind him."),
     ]),
     ("Syn na północ", [
     ]),
   ]),
   ("Droga na północ", "Śnieżna droga, złote iglice na horyzoncie", [
     ("Kibitka", [
      ("syn_na_polnoc", "PO", "jaz", N, "Kryta kibitka (koń i woźnica) jedzie śnieżną drogą na północ, w okienku twarz chłopca; "
       "2 s pada śnieg; 4 s na „St Petersburg” na horyzoncie wyrastają złote iglice; 6 s kibitka mija szlaban z biało-czarną "
       "budką i wartownikiem, który salutuje",
       "L: His son was taken north to St Petersburg, where the Tsar had him raised as a Russian officer."),
     ]),
   ]),
   ("Grań", "Grań nad aułem, wiatr", [
     ("Lata", [
      ("kreski", "PŚ", "naj", N, "Szamil sam na grani, wiatr szarpie frędzlem turbanu; 1,4 s ryje kindżałem kreskę na kamieniu, "
       "potem następne kreski (lata); 5,2 s podnosi wzrok na północ; kurtyna zasuwa się w pauzie, na niej „Act 2” i pytanie "
       "„Can you win by burning your own capital?”",
       "L: Shamil kept fighting, year after year. But he had no way to get his son back."),
     ]),
   ]),
  ]),
 (3, "The Biscuit Expedition",
  "Dargo 1845: nowy dowódca hrabia Woroncow ma zdobyć stolicę Szamila. Marsz przez lasy, Dargo puste i spalone przez samego "
  "Szamila (koza), raport o zwycięstwie (pieczątka 2), brak jedzenia, kolumna po suchary i zasadzka w lesie (powaga, teatr "
  "cieni) — „Sucharna ekspedycja”. Lata 50.: wśród Rosjan młody Lew Tołstoj, prawie pojmany.",
  [("Rozkaz", "Sala w pałacu w Tyflisie: mapa, okno; potem bukowy las Czeczenii", [
     ("Woroncow", [
      ("vorontsov", "PŚ", "stat", N, "0,6 s hrabia Woroncow w kapeluszu z ogromnym pióropuszem bierze z rąk posłańca rozkaz cara; "
       "podpis „Count Vorontsov”; 3,5 s na mapie zjeżdża strzałka do „DARGO”; 6 s gag: Woroncow się kłania, pióropusz zahacza "
       "o żyrandol, żyrandol się kołysze, Woroncow prostuje się dumnie",
       "L: In 1845, the Tsar sent a new commander, Count Vorontsov, with one simple order: take Dargo, Shamil's capital."),
     ]),
   ]),
   ("Las", "Bukowy las Czeczenii", [
     ("Marsz przez las", [
      ("pochod", "PO", "jaz", N, "Bukowy las: kolumna wojska, wozy z workami, armata; 2,4 s zza buków wychylają się muridzi, "
       "dymki strzałów, chowają się; 5,4 s gag: żołnierz puka w pień, z dziupli wysuwa się murid, puka go w czapkę i znika; "
       "żołnierz patrzy na kolegów, tabliczka „?!”",
       "L: His army marched for weeks through mountain passes and thick forests, and Shamil's men fired at it from behind every tree."),
     ]),
   ]),
   ("Dargo", "Spalona wioska w lesie, dym; potem namiot Woroncowa", [
     ("Pusta stolica", [
      ("dargo", "PO", "naj", N, "0,6 s kolumna wchodzi do Dargo: domy płoną, dym; 3 s żołnierze zaglądają do domów — puste; "
       "5,4 s na „set his own capital on fire” płomienie rosną; 7,6 s gag: z dymu wychodzi koza, jedyna mieszkanka, staje przed "
       "Woroncowem i beczy „MEH”",
       "L: When the soldiers finally reached Dargo, it was empty. Shamil had set his own capital on fire and left."),
     ]),
   ]),
   ("Namiot", "Namiot Woroncowa pod Dargo", [
     ("Raport", [
      ("zwyciestwo", "PŚ", "stat", N, "Namiot; 0,6 s Woroncow pisze raport, 1,8 s pieczątka uderza: „DARGO TAKEN! VICTORY!” "
       "(powtórka gagu pieczątki); 4 s na „nothing left to eat” adiutant przynosi pusty worek i odwraca go do góry dnem — "
       "wypada jeden suchar; Woroncow patrzy na suchar",
       "L: Vorontsov reported a great victory. Then he noticed that his army had nothing left to eat."),
     ]),
     ("Suchary", [
      ("suchary", "PO", "jaz", N, "Bukowy las, droga; 0,6 s kolumna z wozami wraca po zaopatrzenie, na wozach worki z napisem "
       "„SUKHARI” (suchary); 4 s las gęstnieje, robi się ciemniej; 6,5 s na „waiting” w koronach buków pojawiają się oczy "
       "i lufy; bez gagu",
       "L: So a column went back through the forest to fetch supplies, mostly sacks of dry biscuits. Shamil's men were waiting in the trees."),
     ]),
   ]),
   ("Zasadzka", "Teatr cieni: droga w lesie", [
     ("Zasadzka", [
      ("zasadzka", "PO", "stat", N, "Teatr cieni: drzewa padają w poprzek drogi, wozy stają; 2,4 s błyski strzałów, sylwetki "
       "padają za parawan; 5 s cisza, worek z sucharami leży na drodze; 6,8 s na „Biscuit Expedition” zjeżdża tabliczka "
       "„THE BISCUIT EXPEDITION” — bez dźwięku gagu (powaga)",
       "L: Felled trees blocked the road, and the column was cut to pieces. The Russians remember it as the Biscuit Expedition."),
     ]),
   ]),
   ("Tołstoj", "Droga między fortami w Czeczenii, lata 50.", [
     ("Pisarz w wojsku", [
      ("tolstoj", "PP", "jaz", N, "0,6 s młody ochotnik w czapce kadeta jedzie konno i pisze w zeszycie; 3 s przy nazwisku podpis "
       "„Leo Tolstoy, 24”; 5,6 s na „almost captured” zza wzgórza wypadają jeźdźcy w czerni; Tołstoj i jego czeczeński przyjaciel "
       "(Sado) galopują w prawo; 8,5 s gag: z zeszytu wylatują kartki i lecą za nim jak ogon; 10 s jedna kartka przykleja się "
       "do twarzy goniącego; kurtyna",
       "L: The war dragged on. In the 1850s, one young Russian volunteer here was Leo Tolstoy. He was almost captured, and later wrote stories about this war."),
     ]),
   ]),
  ]),
 (4, "The Son and the Princesses",
  "Dżamaluddin dorasta w Petersburgu jako oficer cara. Latem 1854 drugi syn Szamila najeżdża Cinandali w Gruzji i porywa księżne "
  "Annę Czawczawadze i Warwarę Orbeliani z dziećmi i guwernantką; osiem miesięcy w Wedeno. Szamil pisze do cara („padyszach”): "
  "syn i milion rubli, stanęło na 40 000. Marzec 1855: wymiana na rzece Miczik. Syn wraca w mundurze, przebiera się, uścisk. "
  "W górach jest obcy, umiera w 1858.",
  [("Petersburg", "Sala balowa w Petersburgu: kolumny, żyrandol, pary", [
     ("Oficer cara", [
      ("kadet", "PŚ", "stat", N, "0,6 s mała lalka chłopca w mundurze kadeta salutuje; 2 s chowa się w dół, a na jej miejsce "
       "wysuwa się wyższy kadet, 3,5 s potem wysoki oficer z wąsikiem (ta sama twarz); 4 s przy imieniu podpis „Jamal al-Din”; "
       "6 s za nim pary wirują w walcu, żyrandol migocze; 8,4 s oficer kłania się damie i rusza do tańca",
       "L: Meanwhile, in St Petersburg, Jamal al-Din grew up as a cadet, then an officer in the Tsar's own army. The mountains became a childhood memory."),
     ]),
   ]),
   ("Cinandali", "Gruzińska posiadłość: dwór z balkonem, winnice, kamienny mur; potem Wedeno", [
     ("Najazd", [
      ("tsinandali", "PO", "naj", N, "0,6 s dwór wśród winnic, zawieszka „Tsinandali, Georgia, 1854”; 2,6 s na grzbiecie za murem "
       "wyrastają jeźdźcy w czerni, podpis „Shamil's second son”; 5,2 s jeźdźcy przeskakują mur winnicy, liście winorośli "
       "fruwają; 7,4 s na balkonie dwie damy w białych czepcach odskakują, „!!”",
       "L: Then, in the summer of 1854, Shamil's second son raided Tsinandali, a princely estate in Georgia."),
     ]),
   ]),
   ("Porwanie", "Górska droga, jeźdźcy z księżnymi", [
     ("Porwanie", [
      ("ksiezne", "PŚ", "jaz", N, "Jeźdźcy jadą w góry; 0,6 s na koniach przed jeźdźcami księżne w białych czepcach, przy "
       "imionach podpisy „Princess Anna Chavchavadze” i „Princess Varvara Orbeliani”; 4,5 s za nimi na koniach dzieci; "
       "6,4 s na „governess” guwernantka w czarnej sukni na ostatnim koniu trzyma kapelusz",
       "L: His riders carried off two princesses, Anna Chavchavadze and Varvara Orbeliani, with their children and their French governess."),
     ]),
   ]),
   ("Wedeno", "Auł Wedeno: kamienny dom z oknem", [
     ("Niewola", [
      ("wedeno", "PO", "naj", N, "Wedeno w górach: kamienny dom, w oknie księżne, przed domem wartownik; zawieszka „Vedeno”; "
       "2,5 s na „eight months” nad domem przesuwają się księżyc i słońce, śnieg pada i topnieje; 5,5 s na „governess” "
       "w oknie guwernantka pisze w zeszycie i zerka na wartownika",
       "L: For eight months they were held in Shamil's mountain capital, Vedeno. Their governess later turned those months into a book."),
     ]),
     ("Cena", [
     ]),
   ]),
   ("Izba Szamila", "Izba: niski stolik, list", [
     ("List", [
      ("cena", "PŚ", "stat", N, "Izba: Szamil przy niskim stoliku pisze list z żądaniami gęsim piórem; 2,4 s na „padishah” nad "
       "listem zjeżdża tabliczka PADISHAH; 4,4 s na „his son” obok rysunek chłopca; 5,6 s na „a million” liczba „1,000,000”; "
       "7,6 s na „forty thousand” cyfry odpadają po kolei i spadają na podłogę z brzękiem, zjeżdża „40,000”; Szamil gładzi brodę. "
       "Rokowania szły przez pośredników, a zgodę na powrót syna dał car (NPLG) — lektor nie mówi, że Szamil pisał do cara",
       "L: Shamil's demands went all the way to the Tsar, whom he called the padishah: his son, and a million roubles. He settled for forty thousand, and a prisoner exchange."),
     ]),
   ]),
   ("Wymiana na rzece", "Rzeka Miczik: kamieniste brzegi, płytki bród, góry w marcu", [
     ("Dwa brzegi", [
      ("rzeka", "PO", "naj", N, "0,6 s na brzegach ustawiają się dwa oddziały: z lewej Rosjanie, z prawej jeźdźcy w czerni; "
       "zawieszka „River Michik, March 1855”; 3 s chorągwie: czarna imamatu i biała flaga rozmów; 5,4 s konie przestępują "
       "z nogi na nogę; z lewej wjeżdża wóz z workami srebra",
       "L: In March 1855, both sides met at the river Michik to make the exchange."),
      ("przeprawa", "PP", "jaz", N, "0,6 s wóz z księżnymi, dziećmi i guwernantką przejeżdża bród w lewo, do Rosjan; 2,6 s "
       "na „The silver” wóz z workami srebra jedzie w prawo; 4,6 s dziecko na wozie macha; 6 s koń przy wozie strząsa wodę "
       "z grzywy",
       "L: The princesses and their children crossed one way. The silver went the other."),
     ]),
     ("Syn wraca", [
      ("syn_wraca", "PO", "jaz", N, "0,6 s z lewego brzegu wjeżdża w bród młody oficer w rosyjskim mundurze na koniu; 3 s przy "
       "imieniu podpis „Jamal al-Din”; 5,6 s zatrzymuje konia na środku rzeki i patrzy na góry; 7,6 s rusza dalej w prawo",
       "L: And from the Russian side rode Jamal al-Din, a grown man now, still in his Russian officer's uniform."),
      ("mundur", "PŚ", "stat", N, "Prawy brzeg; 0,6 s młody oficer zsiada z konia; 2,5 s zdejmuje epolety; 4,5 s murid podaje "
       "mu złożoną czarną czerkieskę; 6 s oficer chowa się na moment za koniem i wychodzi w czerkiesce (lalka w czerkiesce)",
       "L: Before he could meet his father, he had to take off the uniform and put on mountain clothes."),
      ("uscisk", "Z", "naj", 6.2, "Muzyka milknie, zostaje szum rzeki; 0,8 s Szamil podchodzi, dłoń puszcza rękojeść kindżału; "
       "2,2 s obejmuje syna, kamera bardzo wolno dojeżdża; 4,6 s na końcu uścisku wraca motyw ojca (emocjonalny szczyt filmu, "
       "Wytyczne 1.23)", "cisza, rzeka, motyw"),
     ]),
   ]),
   ("Obcy w górach", "Kamienna izba w aule, zima", [
     ("Obcy", [
      ("obcy", "PŚ", "stat", N, "Izba: syn w czerkiesce siedzi nad rosyjską książką, za oknem śnieg; 2,2 s nad nim obłok "
       "z miniaturą Petersburga: iglice, wirujące pary; 5 s Szamil w drzwiach patrzy na syna; 7 s obłok pęka i znika",
       "L: But Jamal al-Din had become a stranger in the mountains. He missed his books and the life of the capital."),
      ("smierc", "PŚ", "stat", N, "Syn leży w łóżku pod kołdrą, oparty o poduszkę, przy nim świeca; Szamil stoi przy łóżku, dłoń "
       "na kołdrze; 0,6 s syn kaszle; 3,4 s na „died” syn osuwa się na poduszkę, płomień świecy drży i gaśnie, smużka dymu; bez gagu; kurtyna w pauzie, na niej „Act 5” i pytanie „How does a 25-year war end?”",
       "L: Three years after coming home, in 1858, he fell ill and died."),
     ]),
   ]),
  ]),
 (5, "Gunib",
  "1859: wojna przegrana, 62-letni Szamil na górze Gunib, ok. 400 obrońców wobec 16 000 żołnierzy, szturm po urwiskach o świcie. "
  "Kapitulacja przed księciem Bariatinskim („siridar”), pieczątka 3 — tym razem prawdziwa i bez żartu. Car Aleksander II przyjmuje "
  "go z honorami, dom w Kałudze, tłumy gapiów; pielgrzymka i śmierć w Medynie 1871.",
  [("Ostatnia góra", "Gunib: wioska na płaskowyżu otoczonym urwiskami", [
     ("Osaczony", [
      ("gunib", "PO", "naj", N, "0,6 s płaskowyż z wioską wyrasta z mgły, zawieszka „Gunib, 1859”; 3,5 s na „Shamil, now "
       "sixty-two” na krawędzi staje Szamil z siwą brodą; 5,5 s wiatr szarpie czarną chorągiew; 7 s kamień obsuwa się "
       "z urwiska",
       "L: By 1859, the war was lost. Shamil, now sixty-two, made his last stand on the mountain of Gunib."),
      ("liczby", "PO", "odj", N, "Kamera odjeżdża: garstka obrońców na górze; 0,6 s tabliczka „400” nad garstką; 3 s dookoła "
       "góry wysuwają się rzędy wojska aż po horyzont, każdy rząd z opóźnieniem; 4,6 s tabliczka „16,000” nad wojskiem",
       "L: He had about four hundred fighters left. Around the mountain stood sixteen thousand Russian soldiers."),
      ("szturm_gunib", "PP", "jaz", N, "Świt; 0,6 s żołnierze wspinają się po urwisku na linach, jeden za drugim; 3 s pierwszy "
       "dosięga krawędzi; 5 s na górze unosi się biała flaga i powiewa; cisza",
       "L: At dawn, the soldiers climbed cliffs that everyone believed could not be climbed."),
     ]),
   ]),
   ("Kapitulacja", "Polana pod brzozami pod Gunibem; potem gabinet w Petersburgu, sala tronowa i dom w Kałudze", [
     ("Siridar", [
      ("kapitulacja", "PP", "jaz", N, "0,6 s Szamil, siwy, schodzi ścieżką do księcia siedzącego na kamieniu pod brzozą, za nim "
       "kilku muridów; 3 s przy nazwisku podpis „Prince Baryatinsky”; 5 s Szamil staje przed księciem; 6,4 s na „siridar” nad "
       "księciem zjeżdża tabliczka SIRIDAR (zasiew puenty aktu VI); bez gagu",
       "L: Shamil came down and surrendered to Prince Baryatinsky, the Tsar's viceroy. Shamil's word for such a man was siridar."),
     ]),
   ]),
   ("Gabinet", "Gabinet w Petersburgu, ten sam co w 1839", [
     ("Pieczątka", [
      ("stempel", "D", "stat", N, "Gabinet w Petersburgu, ten sam urzędnik co w 1839, siwy; 0,6 s kładzie raport; 1,6 s pieczątka "
       "opada powoli: „SHAMIL: CAPTURED” — trzecie podejście gagu bez żartu: bez brzdęku, urzędnik tylko patrzy; 3,6 s za oknem "
       "biją dzwony",
       "L: This time, the report from the mountains was true."),
     ]),
   ]),
   ("Sala tronowa", "Sala z kolumnami", [
     ("Car", [
      ("car", "PŚ", "stat", N, "Sala z kolumnami; 0,6 s Szamil staje przed carem Aleksandrem II, podpis „Tsar Alexander II”; "
       "3 s car podaje mu rękę; 5,4 s na „Kaluga” obok zjeżdża domek z kolumienkami, zawieszka „Kaluga”",
       "L: The new Tsar, Alexander the Second, received his old enemy with honours, and gave him a house in the town of Kaluga."),
     ]),
   ]),
   ("Kaługa", "Dom z kolumienkami i płot", [
     ("Gapie", [
      ("kaluga", "PO", "stat", N, "Dom w Kałudze z płotem; 0,6 s Szamil na ganku; 2,5 s zza płotu wychylają się głowy gapiów, "
       "jedna po drugiej: damy z lornetkami, dzieci, żołnierz; 5 s na „just to look at him” Szamil uprzejmie macha, gapie "
       "chowają się i wysuwają; 7,8 s gag: na końcu zza płotu wychyla się koza; Szamil i koza patrzą na siebie",
       "L: The man Russia had hunted for twenty-five years became its most famous guest. Crowds came just to look at him."),
     ]),
     ("Pielgrzymka", [
      ("medyna", "PO", "jaz", N, "Pustynia pod księżycem; 0,6 s karawana, Szamil na wielbłądzie; 4 s zawieszka „Medina, 1871”; "
       "6,8 s na „in the desert” karawana staje, Szamil schodzi z wielbłąda i patrzy na wydmy; kurtyna w pauzie, na niej "
       "„Act 6” i pytanie „How did his war get into Dune?”",
       "L: At the end of his life he was allowed to go on pilgrimage, and in 1871 he died in Medina, in the desert."),
     ]),
   ]),
  ]),
 (6, "The Words",
  "1960: Lesley Blanch, „The Sabres of Paradise”; 1965: „Diuna” Franka Herberta. Słowa zasiane w historii (kanly, kindżał, "
  "padyszach, siridar) i nowe (chakobsa, sietch, tabr) lecą na nitkach z gór nad wydmę; zdanie o ostrzu i przysłowie z gór. "
  "Zastrzeżenie: Herbert czerpał z wielu źródeł, Paul to nie Szamil. Puenta: następna Diuna jest o tym, co po wygranej świętej "
  "wojnie — wojna Szamila skończyła się białą flagą i synem, którego nie zatrzymał.",
  [("Książka", "Pracownia pisarki w Londynie; potem stół Herberta", [
     ("Blanch i Herbert", [
      ("blanch", "PŚ", "stat", N, "0,6 s pisarka w kapeluszu przy maszynie do pisania, zawieszka „London, 1960”; 2 s podpis "
       "„Lesley Blanch”; 4 s dzwonek maszyny, kartki wylatują jak ptaki i składają się w książkę z szablami na okładce; "
       "7,6 s gag: ostatnia kartka ląduje na kocie, który miauczy i ucieka",
       "L: Almost a century later, in 1960, the writer Lesley Blanch told Shamil's story in a book called The Sabres of Paradise."),
     ]),
   ]),
   ("Stół Herberta", "Pracownia Herberta, 1965", [
     ("Diuna", [
      ("herbert", "PŚ", "naj", N, "0,6 s mężczyzna z brodą przy maszynie, zawieszka „1965”, podpis „Frank Herbert”; 3 s z maszyny "
       "zamiast kartek sypie się piasek, usypuje wydmę, zasypuje mu buty; 5,4 s z wydmy wynurza się mały robak, rozgląda się; "
       "7,4 s gag: Herbert wytrząsa piasek z buta",
       "L: Five years later, Frank Herbert published Dune, and some words from her book were in it."),
     ]),
   ]),
   ("Słowa", "Scena podzielona: z lewej wydma, z prawej góry; słowa przelatują na nitkach z gór nad wydmę", [
     ("Słowa na nitkach", [
      ("slowa1", "PO", "pan", N, "0,6 s nad górami wisi KANLY (to samo co w 1834), 1,4 s przelatuje na nitce nad wydmę, gdzie "
       "dwaj fremeni zwracają się do siebie; 4,5 s na „kindjal” murid z gór podaje kindżał, który przechodzi nad sceną "
       "do dłoni w rękawicy z herbem po stronie pustyni",
       "L: Kanly, the mountain blood feud, became a feud between great houses. The kindjal, the mountain dagger, became a weapon of dukes."),
      ("slowa2", "PO", "pan", N, "0,6 s na „Chakobsa” dwaj myśliwi w górach szepczą, z ust wylatują litery i lecą nad wydmę, "
       "gdzie składają się w CHAKOBSA; 5 s na „Sietch and tabr” słowa SIETCH i TABR zjeżdżają osobno i sklejają się "
       "w tabliczkę „SIETCH TABR” nad jaskinią w skale pustyni; 8 s z jaskini wygląda robak, tabliczka się chwieje",
       "L: Chakobsa, a hunters' language of the Caucasus, became a language of Dune. Sietch and tabr, old words for a camp, became Paul's home, Sietch Tabr."),
      ("slowa3", "PŚ", "stat", N, "0,6 s na „padishah” nad lalką cara (ta sama co w 1855) zjeżdża PADISHAH; 3,2 s na „siridar” nad "
       "księciem Bariatinskim (ta sama lalka co pod Gunibem) SIRIDAR; 6 s obie tabliczki odjeżdżają na nitkach nad wydmę; "
       "car i książę patrzą za nimi i poprawiają mundury",
       "L: Even padishah, Shamil's word for the Tsar, and siridar, his word for the prince who took his surrender, ended up in Herbert's empire."),
     ]),
     ("Zdanie i przysłowie", [
      ("zdanie", "Z", "stat", N, "Dwie karty na nitkach: z lewej pożółkła „To kill with the point lacked artistry.” (1960), "
       "z prawej biała z maszynopisem z Diuny (1965, TEKST DO SPRAWDZENIA W WYDANIU, księga D7); 3 s ramka lupy przesuwa się "
       "po obu zdaniach, wspólne słowa podświetlają się na złoto; 7 s kindżał spada ostrzem w dół i wbija się w deskę między "
       "kartami",
       "L: He even borrowed a line. Blanch wrote that to kill with the point lacked artistry, and in Dune, a swordmaster teaches the same rule."),
      ("przyslowie", "Z", "stat", N, "Karta „…wisdom from the hills.”; 2 s na „became” słowo „hills” odkleja się z jednej nitki "
       "i spada; 3,5 s na jego miejsce zjeżdża „desert”; 5 s z dołu sypie się trochę piasku",
       "L: And a mountain proverb about wisdom from the hills became wisdom from the desert."),
      ("zastrzezenie", "PO", "odj", N, "Kamera odjeżdża: na scenie stosy innych książek i map pustyni; 2,8 s na „Paul is not "
       "Shamil” lalka Szamila stoi z boku i kręci głową; 5 s na „his war” Szamil kładzie dłoń na stosie książek",
       "L: Herbert drew on many sources, and Paul is not Shamil. But these words came from Shamil's war."),
     ]),
   ]),
   ("Puenta", "Cała scena: wydma i góry obok siebie", [
     ("Dwie wojny", [
      ("dwie_wojny", "PO", "naj", N, "Wydma i góry obok siebie; 0,6 s nad wydmą wschodzi złote słońce, fremeni unoszą ręce; "
       "3,5 s nad górami zbierają się szare chmury i pada śnieg",
       "L: The next Dune film is about what happens after a holy war is won."),
      ("biala_flaga", "PŚ", "naj", N, "0,6 s Szamil na grani podnosi białą flagę; 3,5 s obok niego cień syna w mundurze, który "
       "rozwiewa się jak dym; 6 s Szamil opuszcza flagę i patrzy na wydmę",
       "L: Shamil's real war ended on a mountain, with a white flag, and a son he could not keep."),
      ("dzieki", "TYT", "stat", N, "0,3 s kurtyna zasuwa się; 0,9 s na niej zjeżdża szyld „Paper Theatre”; 1,6 s spod kurtyny wychyla się mały "
       "robak i chowa się z powrotem", "L: Thanks for watching Paper Theatre."),
     ]),
   ]),
  ]),
]

# Ujęcia akcji (konflikt na scenie: walka, pościg, ucieczka, zasadzka) — mapa tempa (Podręcznik → Metoda filmu, 3; reżyser 28.11:
# „dopiero po 2–3 minutach zaczyna się akcja”): pierwsza najpóźniej 0:30, trzy przed 3:00 (scripts/kontrola_filmu.py)
AKCJA = ["wieza", "skok", "rana", "kanly_1834", "marsz", "armaty", "upadek", "tratwa", "pochod", "dargo", "zasadzka", "tolstoj",
         "tsinandali", "szturm_gunib"]
HAK = ["przedstawienie", "hak_syn", "pytanie"]  # w haku oddech 0,4 s i pauza 1,0 s
JEZYK = "en"
TEMPO_EN = 2.84  # angielski klon (TEATR): „Pierwszy cesarz” EN, 1233 słowa w 434 s nagrań (17.11.2026)
SLOWNIE = {"1832": "eighteen thirty-two", "1834": "eighteen thirty-four", "1839": "eighteen thirty-nine",
           "1845": "eighteen forty-five", "1850s": "eighteen fifties", "1854": "eighteen fifty-four",
           "1855": "eighteen fifty-five", "1858": "eighteen fifty-eight", "1859": "eighteen fifty-nine",
           "1871": "eighteen seventy-one", "1960": "nineteen sixty", "1965": "nineteen sixty-five"}
# czas po kwestii na wydarzenie, które ma się skończyć na oczach widza (Wytyczne 1.8, 1.18) albo na gag (Humor: gag
# wydłuża ujęcie o 0,5–1,5 s)
WYDLUZ = {"arrakis": 0.9, "zamiana": 0.7, "hak_syn": 0.8, "pytanie": 0.6, "skok": 1.6, "kanly_1834": 0.0, "imam": 1.6,
          "mapa": 1.8, "marsz": 1.0, "akhulgo": 1.2, "armaty": 1.6, "chlopiec": 1.6, "upadek": 1.0, "tratwa": 0.8,
          "raport": 1.0, "syn_na_polnoc": 1.0, "kreski": 1.6, "vorontsov": 0.2, "pochod": 1.0, "dargo": 1.2,
          "zwyciestwo": 1.0, "zasadzka": 0.8, "tolstoj": 0.6, "kadet": 0.8, "tsinandali": 1.4, "ksiezne": 0.2,
          "wedeno": 0.8, "cena": 1.0, "rzeka": 2.6, "przeprawa": 2.0, "syn_wraca": 2.2, "mundur": 0.6, "obcy": 0.6,
          "smierc": 1.5, "gunib": 0.6, "liczby": 2.8, "szturm_gunib": 1.6, "kapitulacja": 1.6, "stempel": 1.4,
          "kaluga": 1.0, "blanch": 0.8, "herbert": 1.4, "slowa1": 0.6, "slowa3": 0.0, "zdanie": 1.6, "przyslowie": 0.8,
          "dwie_wojny": 0.8, "biala_flaga": 1.0}
PAUZA_PO = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}
HAK_PAUZA = 1.0


def kwestia(dzwiek):
    return dzwiek[2:].strip() if dzwiek.startswith("L:") else ""


def slownie(txt):
    for k, v in sorted(SLOWNIE.items(), key=lambda kv: -len(kv[0])):
        txt = txt.replace(k, v)
    return txt


LEKTOR = Path(__file__).resolve().parents[4] / "output/szamil-diuna/lektor_en"  # klon głosu autora (lektor_en.py), poza repo
BEZ_NAGRAN = [False]  # True: długości z tempa lektora (TEMPO_EN), w którym ułożono akcję ujęć (render.czas_akcji)


def nagranie(dzwiek):
    """Długość nagranej kwestii (lektor_en/<klucz>.json) albo None, gdy jeszcze jej nie ma albo tekst się zmienił."""
    txt = kwestia(dzwiek)
    for f in LEKTOR.glob("*.json") if txt and LEKTOR.exists() and not BEZ_NAGRAN[0] else ():
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("text") == txt and "duration" in meta:
            return meta["duration"]
    return None


# Oddech przed kwestią inny niż zwykły (0,6 s; w haku 0,4 s): kwestia zapowiedzi trwa 6 s nagrania i wychodzi poza
# zapowiedź (6,0 s), więc zaczyna się wcześniej, a kwestia przy kurtynie startu później — między zdaniami zostaje pauza
# (nagranie 28.11: przy 0,6 s jedno zdanie kończyło się dokładnie tam, gdzie zaczynało się drugie)
ODDECH = {"zap_skok": 0.3, "tytul": 1.1}


def okno_tempa(dzwiek, hak=False):
    """(start, długość) kwestii według tempa lektora — rytm, w którym ułożono akcję (ujecia_a.sl, po_kw)."""
    txt = kwestia(dzwiek)
    if not txt:
        return (0.0, 0.0)
    if not KLUCZ_KWESTII:
        KLUCZ_KWESTII.update({kwestia(x[5]): x[0] for _n, _t, _o, sc in AKTY for _s, _p, bt in sc for _b, sh in bt for x in sh})
    return (ODDECH.get(KLUCZ_KWESTII.get(txt), 0.4 if hak else 0.6), len(slownie(txt).split()) / TEMPO_EN)


KLUCZ_KWESTII = {}


def okno_kwestii(dzwiek, hak=False):
    """(start, długość) kwestii w ujęciu: oddech, potem nagranie lektora — a zanim powstanie, tempo lektora."""
    start, dl = okno_tempa(dzwiek, hak)
    real = nagranie(dzwiek) if dl else None
    return (start, real if real else dl)


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


def kontrola_rytmu(rows=None):
    """Lista uwag o rytmie (reżyser 28.11.2026: „trzy ujęcia długie, nagle jedno pół sekundy… dwa długie, na których nic się
    nie dzieje”): (1) samotne krótkie ujęcie (< 3 s) między dwoma długimi (> 6 s) poza zapowiedzią; (2) trzy ujęcia z rzędu
    o długościach w przedziale 0,6 s (siatka zamiast treści); (3) ujęcie z kwestią, którego opis nie ma co najmniej dwóch
    chwil wydarzeń w sekundach („2,5 s …”) — lalka stoi, a lektor mówi (Rytm 1)."""
    import re
    rows = rows or ujecia()
    uw = []
    for i, r in enumerate(rows):
        if r[2].startswith("zap_"):
            continue
        if 0 < i < len(rows) - 1 and r[5] < 3.0 and rows[i - 1][5] > 6.0 and rows[i + 1][5] > 6.0:
            uw.append(f"{r[2]}: samotne krótkie ujęcie {r[5]} s między {rows[i - 1][5]} a {rows[i + 1][5]} s")
        if i >= 2 and not rows[i - 2][2].startswith("zap_") and max(x[5] for x in rows[i - 2:i + 1]) - min(x[5] for x in rows[i - 2:i + 1]) < 0.6:
            uw.append(f"{r[2]}: trzy ujęcia z rzędu tej samej długości ({', '.join(str(x[5]) for x in rows[i - 2:i + 1])})")
        if kwestia(r[7]) and len(re.findall(r"\d+(?:,\d+)? s\b", r[6])) < 2:
            uw.append(f"{r[2]}: kwestia bez co najmniej dwóch wydarzeń w opisie")
    return uw


if __name__ == "__main__":
    rows = ujecia()
    total = sum(r[5] for r in rows)
    mowa = sum(okno_kwestii(r[7])[1] for r in rows)
    for n, t, *_ in AKTY:
        a = [r for r in rows if r[0] == n]
        print(f"akt {n} {t:28s} {len(a):3d} ujęć {sum(r[5] for r in a):6.1f} s")
    print(f"razem {len(rows)} ujęć, {int(total // 60)}:{total % 60:04.1f}, lektor {mowa:.0f} s ({mowa / total:.0%}), "
          f"bez słów {sum(1 for r in rows if not kwestia(r[7]))} ujęć, słów {sum(len(slownie(kwestia(r[7])).split()) for r in rows)}")
    uw = kontrola_rytmu(rows)
    print(f"kontrola rytmu: {len(uw)} uwag")
    for u in uw:
        print("  -", u)
