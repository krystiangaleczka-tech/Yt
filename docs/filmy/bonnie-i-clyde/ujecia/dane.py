"""Rozpiska filmu „Bonnie and Clyde: The Outlaws Made of Paper” (teatr papierowy, EN, ok. 17–18 minut): akt → scena → beat → ujęcie.

Źródło: zatwierdzony szkic ujęć D (reżyser 19.11.2026: „Robimy A, ale wplatamy gdzieś te B, wydłużając opowieść”; „Tak,
zatwierdzam D”), docs/filmy/bonnie-i-clyde/szkice/buduj_szkice.py — rozpiskę wygenerowano z niego raz, od teraz to ten plik
jest źródłem (zmiana historii: scenariusz i Story Bible → księga świata → ta rozpiska → ujęcia).
Wzór: „Syn słońca” (docs/filmy/powstanie-japonii/ujecia/dane.py) — ten sam układ danych i te same zasady.

ujęcie: (klucz, kadr, ruch, sekundy, opis wydarzenia, dźwięk)
- klucz — nazwa funkcji ujęcia w output/bonnie-i-clyde (`s_<klucz>`); brak funkcji = ujęcie do narysowania;
- kadr i ruch — skróty jak w pozostałych filmach (buduj.py);
- sekundy — None: długość liczy się z kwestii (oddech + słowa / TEMPO_EN + pauza po kwestii według granicy + WYDLUZ);
  liczba: ujęcie bez słów;
- dźwięk zaczynający się od „L:” to kwestia lektora po angielsku (film jest tylko w wersji EN, księga świata D3).
Ton: ironia i suchy lektor; z ofiar się nie żartuje, od Grapevine (akt VI) ton jest poważny (księga świata D2).
"""
import json
from pathlib import Path

N = None
AKTY = [(0,
  'Prologue',
  'Sześć sekund najmocniejszych akcji (10 cięć po 0,6 s) i ściemnienie; krótka kurtyna startu na teatr z gazet, Bonnie z cygarem '
  'przy Fordzie. Wprowadzenie, hak 1 (klisza z Joplin, cygaro na pierwszych stronach, a Bonnie nie paliła cygar) i obietnica jako '
  'jedno pytanie prowadzące w retrospekcję (jeden początek filmu, Podręcznik → Rytm, 19.11.2026).',
  [('Zapowiedź — skróty najmocniejszych ujęć',
    'Zapowiedź — skróty najmocniejszych ujęć',
    [('Zapowiedź — skróty najmocniejszych ujęć',
      [('zap_wellington_most',
        'PO',
        'szarp',
        0.4,
        'zapowiedź (skrót ujęcia „wellington_most”): Ford spada z rozebranego mostu w wąwóz i uderza o dno',
        'zgrzyt, uderzenie'),
       ('zap_zdjecie',
        'PŚ',
        'szarp',
        0.7,
        'zapowiedź (skrót ujęcia „zdjecie”): Bonnie z cygarem i rewolwerem pozuje przy Fordzie, błyska flesz',
        'flesz'),
       ('zap_prasa',
        'PO',
        'szarp',
        0.4,
        'zapowiedź (skrót ujęcia „prasa”): wałki drukarni kręcą się, wylatują gazety ze zdjęciem',
        'maszyna drukarska'),
       ('zap_kiosk',
        'PO',
        'szarp',
        0.7,
        'zapowiedź (skrót ujęcia „kiosk”): gazeciarz macha gazetą, kolejka ludzi, „EXTRA!”',
        'gwar, „Extra!”'),
       ('zap_kaufman',
        'PO',
        'szarp',
        0.4,
        'zapowiedź (skrót ujęcia „kaufman”): Clyde i Bonnie w nocy wskakują na muły obok Forda w błocie',
        'silnik w błocie, skok'),
       ('zap_poscigi',
        'PO',
        'szarp',
        0.7,
        'zapowiedź (skrót ujęcia „poscigi”): radiowóz wylatuje z zakrętu i koziołkuje w powietrzu',
        'pisk opon, syrena'),
       ('zap_boyd',
        'PŚ',
        'szarp',
        0.4,
        'zapowiedź (skrót ujęcia „boyd”): porwany komendant z rękami w górze, Bonnie grozi mu palcem',
        'silnik'),
       ('zap_sowers',
        'PO',
        'szarp',
        0.7,
        'zapowiedź (skrót ujęcia „sowers”): nocą z krzaków błyskają strzały, Ford z przestrzelonymi szybami',
        'strzały, szkło'),
       ('zap_hamer',
        'PP',
        'szarp',
        0.4,
        'zapowiedź (skrót z ganku): łowca na ganku sięga po karabin',
        'zamek karabinu'),
       ('zap_zasadzka',
        'PO',
        'szarp',
        1.2,
        'zapowiedź (skrót ujęcia „zasadzka”): teatr cieni: dziesiątki błysków wokół papierowego Forda; ściemnienie',
        'seria strzałów; ściemnienie')])]),
   ('Teatr z gazet i hak',
    'Teatr z gazet i hak',
    [('Teatr z gazet i hak',
      [('tytul',
        'TYT',
        'naj',
        2.4,
        'Kurtyna startu rozsuwa się na teatr zbudowany z gazet: stoi Ford, Bonnie opiera nogę o zderzak z cygarem w zębach i '
        'rewolwerem, obok Clyde z karabinem; z góry zjeżdża szyld „The Outlaws Made of Paper”',
        'kurtyna, fanfara z płyty gramofonowej, szelest gazet'),
       ('wprowadzenie',
        'PŚ',
        'naj',
        None,
        'Kamera najeżdża na Bonnie; przy jej imieniu zjeżdża podpis „Bonnie Parker”; Bonnie cały czas trzyma rewolwer w jednej ręce, drugą wyjmuje cygaro z ust, krzywi się („UGH!”) i ciska je za siebie (markery reżysera 21.11)',
        'L: This is Bonnie Parker, the most famous outlaw girl in America, and almost everything you think you know about her '
        'was printed in a newspaper.'),
       ('wprowadzenie2',
        'PP',
        'odj',
        None,
        "Kamera odjeżdża na Clyde'a; podpis „Clyde Barrow”; za nimi z nitek zjeżdżają nagłówki gazet jeden za drugim. Gag (markery "
        "reżysera 19.11 i 21.11): Bonnie strzela z końca lufy, kula odbija się od brzegów kadru jak w grze i wbija się w bak Forda; "
        "paliwo leci ciurkiem na ziemię i powoli zalewa scenę do kolan; „…”",
        'L: Together with Clyde Barrow, she spent two years robbing gas stations and corner shops, while the papers turned two '
        'broke kids from Dallas into legends.'),
       ('hak_joplin_rzeczy',
        'D',
        'stat',
        None,
        'Policjant chodzi po opuszczonym pokoju: walizki, karabiny, zeszyt z wierszem; podnosi z podłogi aparat wysoko, do oczu, '
        'a z dołu aparatu wysuwa się w dół klisza z mikro, czarnymi pozami Bonnie w klatkach; policjant lekko macha aparatem, otwiera '
        'usta, tabliczka „OOO…” (markery reżysera 21.11)',
        'L: In April 1933, police raided their hideout in Joplin, Missouri, and found the one thing outlaws should never leave '
        'behind: a camera full of film.'),
       ('zdjecie',
        'PŚ',
        'naj',
        None,
        'Ożywa klatka z kliszy: przy Fordzie stoi chłopak z cygarem; Bonnie podchodzi, chłopak wkłada jej cygaro do ust; Bonnie '
        'wraca, kręci rewolwerem i wsuwa go za pasek, pozuje; chłopak wyciąga z kieszeni stary aparat z wielką lampą błyskową '
        'i robi jej zdjęcie — błyska flesz (markery reżysera 21.11)',
        'L: On one frame, Bonnie posed with a pistol and a borrowed cigar, just for fun.'),
       ('hak_pomost',
        'D',
        'stat',
        1.6,
        'Pomost: wielka strona gazety przewraca się przez cały kadr jak kurtyna, szelest papieru',
        'szelest przewracanej strony'),
       ('prasa',
        'PO',
        'jaz',
        None,
        'Wałki maszyny drukarskiej kręcą się, wylatują setki gazet ze zdjęciem Bonnie z cygarem i odlatują nad dachy miasteczek; '
        'pod koniec maszyna zaczyna lekko podskakiwać (marker reżysera 21.11)',
        'L: Within days that joke was on front pages across America, and Bonnie became the cigar-smoking gun girl.'),
       ('hak_cygaro',
        'Z',
        'stat',
        None,
        "Bonnie przy aucie czyta gazetę ze swoim zdjęciem; cygaro wypada jej z ust; gazeta znika, a w dłoni jest zgnieciona "
        "kulka, którą Bonnie wyrzuca za kadr — tam miauczy trafiony kot (marker reżysera 21.11); tabliczka „I DON'T SMOKE "
        "CIGARS!”; Bonnie podskakuje z przerażenia",
        "L: There was just one problem: Bonnie didn't smoke cigars, and she spent the rest of her short life trying to tell "
        'everyone.')])]),
   ('Obietnica — teatr z gazet',
    'Obietnica — teatr z gazet',
    [('Obietnica — teatr z gazet',
      [('obietnica',
        'PO',
        'odj',
        None,
        'Gazety układają się w mapę pięciu stanów; po mapie driftują z dymem spod kół dwa papierowe Fordy, każdy inną trasą '
        '(markery reżysera 21.11): szary Bonnie i Clyde\'a i czarny z kapeluszem w oknie (łowca bez nazwiska); łowca dojeżdża '
        'na miejsce pierwszy i czeka',
        'L: So how does a joke turn two broke kids into the most hunted couple in America, and how does one patient man catch '
        'them without ever chasing them?')])])]),
 (1,
  'Who were they before the headlines?',
  'West Dallas lat 20., Clyde i Bonnie przed nagłówkami — krótko (Podręcznik → Rytm, 19.11.2026: tło bohatera z napięciem, '
  'akcja w niemych, szybkich ujęciach): indyki, ślub z Royem, kawiarnia, spotkanie w kuchni i areszt, Waco i Ohio. Pogorszenie: '
  'Eastham — pierwsze zabójstwo, obcięte palce i zwolnienie; hak 2: przysięga.',
  [('West Dallas',
    'West Dallas',
    [('West Dallas',
      [('wagon',
        'PŚ',
        'naj',
        None,
        'Ściemnienie (bez kurtyny — jeden początek filmu); z ziemi wyrastają namioty i szałasy pod wiaduktem, zjeżdża zawieszka '
        '„West Dallas, 1920s”; rodzina Barrowów śpi pod wozem konnym',
        'L: It all starts in West Dallas in the 1920s, in a slum so poor that people called it the '
        "Devil's Back Porch, where Clyde Barrow grew up with almost nothing."),
       ('indyki',
        'PP',
        'stat',
        None,
        'Nastoletni Clyde i brat Buck siedzą na pace ciężarówki między gdaczącymi indykami; zza rogu wychodzi policjant '
        'z gwizdkiem, „STOP!”; chłopcy zeskakują i podnoszą ręce, indyki wyfruwają',
        'L: As a teenager, he got arrested for a truck full of stolen turkeys.')])]),
   ('Cement City',
    'Cement City',
    [('Cement City',
      # Pomost z historii Clyde'a do historii Bonnie (reżyser 19.11: „dlaczego z ujęcia o indykach robi się nagle ślub? to nie
      # ma sensu … pomiędzy te dwa daj jedno przechodzące do tego weddingu, o ile ma to pokrycie w scenariuszu”). Pokrycie:
      # Bonnie dorastała w Cement City, kilka mil od West Dallas, pisała wiersze i marzyła o scenie (księga: miejsce cement_city,
      # „szkoła z podium”); ślub w 1926. Ujęcie szkoły wypadło przy skracaniu aktu I i z nim zniknęło „tymczasem”.
      [('poezja',
        'PŚ',
        'stat',
        None,
        'Cement City: drewniane domki, w tle kominy cementowni; zawieszka „Cement City, 1926”; piętnastoletnia Bonnie na '
        'szkolnym podium recytuje z zeszytu, wolną rękę wznosi jak aktorka; z góry kadru spada indyk, który odleciał z czapki policjanta, '
        'i siada przed podium jako jedyna widownia',
        'L: Meanwhile, a few miles away in Cement City, Bonnie Parker wrote poems and dreamed of the stage.'),
       ('slub',
        'PP',
        'stat',
        None,
        'Piętnastoletnia Bonnie i Roy Thornton stają pod łukiem z papierowych kwiatów; pod kwiatami zjeżdża wstęga „Happy '
        'Ever After” po łuku; podpis „Roy Thornton”; nad łukiem tabliczka-tatuaż: dwa serca „Bonnie” i „Roy”',
        'L: But at fifteen she married a boy named Roy Thornton and had their names tattooed in two hearts, a very permanent '
        'decision.')])]),
   ('Kawiarnia w Dallas',
    'kawiarnia w Dallas',
    [('Kawiarnia w Dallas',
      [('kawiarnia',
        'PŚ',
        'naj',
        None,
        'Bonnie w fartuszku trzyma dzbanek za ucho i nalewa kawę do filiżanki na ladzie, ruszając dzbankiem w górę i w dół; klient '
        'trzyma gazetę przed sobą w dłoni (nie na głowie) i nie podnosi wzroku; na palcu Bonnie błyska obrączka od Roya; Bonnie '
        'odstawia dzbanek z hukiem (markery reżysera 21.11)',
        'L: Roy soon landed in prison, so at nineteen she was a waitress still wearing his ring, waiting for something '
        'exciting to happen.')])]),
   ('Kuchnia przyjaciółki',
    'kuchnia przyjaciółki',
    [('Kuchnia przyjaciółki',
      [('kuchnia',
        'PP',
        'stat',
        None,
        'W ciasnej kuchni Bonnie miesza kakao (łyżka w garnku), na ścianie wisi patelnia; drzwiami wchodzi Clyde w kapeluszu '
        'i uchyla go; z nitek zjeżdżają serca, jedno nad Bonnie, drugie nad Clyde\'em; na „arrested” serca odjeżdżają, nad Clyde\'em '
        'zjeżdżają kajdanki (markery reżysera 21.11)',
        "L: In January 1930 she met Clyde in a friend's kitchen, and something exciting finally happened: a few weeks later he "
        'was arrested.'),
       ('areszt',
        'PŚ',
        'naj',
        5.6,
        "Nieme: do kuchni wpada policjant i zakuwa Clyde'a w kajdanki; Bonnie z patelnią w dłoni (marker reżysera 21.11) woła "
        "„HEY!”, biegnie za nimi, drzwi trzaskają jej przed nosem",
        'kajdanki, okrzyk Bonnie')])]),
   ('Areszt w Waco',
    'areszt w Waco',
    [('Areszt w Waco',
      [('waco_przed',
        'PŚ',
        'naj',
        None,
        'Ujęcie pośrednie: ulica w Waco przed aresztem „COUNTY JAIL”, zawieszka „Waco, Texas, 1930”; Bonnie w płaszczu idzie '
        'z patelnią z kuchni, zarzuca ją na plecy, bierze zza paska rewolwer, rozgląda się, chowa go pod płaszcz i z niewinną '
        'miną wchodzi do środka (markery reżysera 21.11)',
        'L: Bonnie smuggled a pistol into the Waco jail.'),
       ('waco',
        'D',
        'stat',
        None,
        'W areszcie Bonnie (w płaszczu, z patelnią na plecach) podaje Clyde\'owi przez kraty pistolet spod płaszcza; strażnik ziewa i zasypia; Clyde otwiera drzwi '
        'celi i wychodzi z kadru; Bonnie odchodzi; strażnik budzi się przed pustą celą, „?!”',
        'L: Clyde broke out, and a week later he was caught again in Ohio.')])]),
   ('Peron w Ohio',
    'peron w Ohio',
    [('Peron w Ohio',
      [('ohio',
        'PP',
        'stat',
        6.4,
        'Nieme: zawieszka „One week later”; Clyde przechadza się po peronie w Middletown (Ohio) i gwiżdże; z obu stron wchodzą '
        'policjanci, „OH NO”; policjant wskazuje więźniarkę z kratami, „BACK TO TEXAS!”, i prowadzą go do niej',
        'gwizdana melodyjka, kroki, „Oh no”')])]),
   ('Eastham',
    'Eastham',
    [('Eastham',
      [('eastham',
        'PO',
        'odj',
        None,
        'Za bramą farmy więziennej Eastham więźniowie w pasiakach okopują bawełnę motykami, każdy w swoim rytmie; strażnik '
        'siedzi na koniu i jedzie wzdłuż rzędu; słońce praży',
        'L: This time he was sent to Eastham, one of the harshest prison farms in Texas.'),
       ('eastham_rura',
        'PŚ',
        'stat',
        None,
        "Za parawanem w baraku cień rosłego więźnia pochyla się nad Clyde'em; Clyde chwyta rurę, cień przeciwnika pada; muzyka "
        'cichnie',
        'L: There another inmate attacked him again and again, until Clyde killed him with a pipe, and it was the first life he '
        'took.'),
       ('palce',
        'D',
        'stat',
        # reżyser 21.11: przyciął ujęcie w Studio do 7,0 s i napisał „zmień narrację, bo opis sceny jest kompletnie inny” —
        # kwestia mówi to, co widać (siekiera spada na stopę); zwolnienie przeszło do ujęcia „parol”, gdzie je widać
        7.0,
        'Na polu Clyde podnosi ręce; z góry spada siekiera na jego stopę i wbija się w ziemię; Clyde łapie się za but '
        'i podskakuje na jednej nodze; tabliczka „AW!”, gwiazdki nad głową',
        'L: To get out of the fields, Clyde let an axe fall on his own foot.'),
       ('parol',
        'PP',
        'stat',
        # 23.11: nagranie kwestii trwa 2,6 s — 4,2 s daje 1 s pauzy po kwestii przed cięciem (Rytm 3)
        4.2,
        'Szybkie: brama się otwiera; Clyde wychodzi o kulach; strażnik macha za nim kartką z pieczątką „PAROLE” (kwestia z „palce”, '
        'reżyser 21.11)',
        'L: Six days later: paroled anyway.'),
       ('przysiega',
        'Z',
        'stat',
        None,
        'Brama zamyka się za Clyde\'em z hukiem; Clyde o kulach odwraca się do niej, tabliczka „NEVER AGAIN”; potem idzie '
        'powoli o kulach od lewej do prawej przez kadr',
        # reżyser 19.11: „skróć ten kadr do 10 s” — kuleje widać na obrazie, więc kwestia bez „He limped for the rest of his life”
        'L: He swore he would die before going back, but how do you stay free when every policeman in Texas knows your '
        'face?'),
       ('po_bramie',
        'PŚ',
        'naj',
        None,
        'Przed zamkniętą bramą Eastham stoi Ford z Bonnie za kierownicą; Clyde o kulach dokuśtykuje do auta, wrzuca kule na tylne '
        'siedzenie i wskakuje do środka — siedzi w tylnym oknie (marker reżysera 21.11: „clyde w aucie”)',
        'L: Bonnie was waiting outside the gate with the engine running, and this time they had a plan: keep moving.')])])]),
 (2,
  "How do you become America's most wanted?",
  "Plan Clyde'a, drobne napady, muły w Kaufman, wiersz o Suicide Sal, pierwsze ofiary, W.D. Jones, Buck i Blanche, mieszkanie "
  'nad garażem w Joplin.',
  [('Droga w Teksasie',
    'droga w Teksasie',
    [('Droga w Teksasie',
      [('akt2',
        'PO',
        'jaz',
        None,
        "Kurtyna „Act II · How do you become America's most wanted?”; rozsuwa się na drogę wśród pól; z ziemi wyrasta stacja "
        'benzynowa z jednym dystrybutorem; Clyde za kierownicą kuleje, kule leżą na tylnym siedzeniu',
        "L: Clyde's plan was simple: steal a fast car, rob small places with little cash and no guards, and keep driving.")])]),
   ('Stacja benzynowa',
    'stacja benzynowa',
    [('Stacja benzynowa',
      [('stacja',
        'PP',
        'stat',
        None,
        "Clyde wchodzi kulejąc do budki stacji z rewolwerem; kasjer otwiera szufladę: kilka monet i guzik; tabliczka „THAT'S IT?”",
        'L: Most of their robberies were gas stations and grocery stores, and many of them paid only a few dollars.')])]),
   ('Kaufman',
    'Kaufman',
    [('Kaufman',
      [('kaufman',
        'PP',
        'stat',
        None,
        'Nocą Ford grzęźnie w błocie po kołpaki; Clyde i Bonnie wskakują na dwa muły, muły ani drgną; tabliczka „GO!”',
        'L: Their first big plan was to rob a hardware store for guns, but the car got stuck in the mud, so they tried to escape '
        'on stolen mules.')])]),
   ('Areszt w Kaufman',
    'areszt w Kaufman',
    [('Areszt w Kaufman',
      [('cela',
        'PŚ',
        'naj',
        None,
        'Bonnie w celi pisze ołówkiem w zeszycie; zapisane kartki odrywają się i fruwają po celi jak ptaki',
        'L: Bonnie was caught and spent two months in jail, where she wrote a long poem about an outlaw girl called Suicide '
        'Sal.')])]),
   ('Hillsboro',
    'Hillsboro',
    [('Hillsboro',
      [('hillsboro',
        'PO',
        'stat',
        None,
        'Za papierowym parawanem cienie: napad w sklepie, błysk, sylwetka sprzedawcy opada za ladę; muzyka cichnie',
        "L: While she was locked up, one of Clyde's robberies went wrong in Hillsboro, and a shopkeeper named John Bucher was "
        'shot dead.')])]),
   ('Dom matki Bonnie',
    'dom matki Bonnie',
    [('Dom matki Bonnie',
      [('matka_obietnica',
        'PP',
        'stat',
        None,
        'Bonnie wychodzi z aresztu prosto w objęcia matki i kiwa głową; za płotem stoi Ford, Clyde cicho trąbi',
        'L: When the grand jury let Bonnie go, she promised her mother to stay away from Clyde, and she kept that promise for a '
        'few weeks.')])]),
   ('Atoka',
    'Atoka',
    [('Atoka',
      [('atoka',
        'PO',
        'stat',
        None,
        'Potańcówka pod gołym niebem w Atoce, pary wirują; dwaj stróże prawa podchodzą do auta; za parawanem błyski, jedna '
        'sylwetka pada',
        "L: That August, at a country dance in Oklahoma, Clyde's gang shot a deputy named Eugene Moore, and now they were wanted "
        'for killing a lawman.')])]),
   ('Droga w Teksasie',
    'droga w Teksasie',
    [('Droga w Teksasie',
      [('wd',
        'PŚ',
        'naj',
        None,
        'Do auta wsiada chudy chłopak z nieśmiałym uśmiechem i zatrzaskuje drzwi; podpis „W.D. Jones, 16”',
        'L: Soon a sixteen-year-old kid from the neighborhood, W.D. Jones, joined them, mostly because it sounded exciting.')])]),
   ('Więzienie Huntsville',
    'więzienie Huntsville',
    [('Więzienie Huntsville',
      [('buck',
        'PP',
        'stat',
        None,
        'Z bramy wychodzi Buck Barrow z ułaskawieniem w ręku; czeka Blanche w kapelusiku, z białym pieskiem na rękach; podpisy '
        '„Buck Barrow”, „Blanche Barrow”',
        "L: Then in March 1933, Clyde's older brother Buck was pardoned, and he and his wife Blanche came along for what was "
        'supposed to be a short family visit.')])]),
   ('Joplin',
    'Joplin',
    [('Joplin',
      [('joplin_dom',
        'PO',
        'jaz',
        None,
        'Dwa auta zajeżdżają pod garaż z mieszkaniem na piętrze; zjeżdża zawieszka „Joplin, Missouri, 1933”; w oknach zapalają '
        'się światła',
        'L: They rented an apartment above a garage in Joplin, Missouri, where the five of them tried very hard to look like a '
        'normal family.'),
       ('joplin_karty',
        'PŚ',
        'naj',
        None,
        'Buck i Blanche grają w karty, Clyde dmucha w saksofon, Bonnie pisze; sąsiadka przykłada ucho do ściany; tabliczka '
        '„SHHH!”',
        'L: They played cards, drank and argued so loudly that the neighbors called the police, thinking they were bootleggers, '
        'so who was really waiting behind that door?')])])]),
 (3,
  'How did a joke make them famous?',
  'Strzelanina w Joplin, klisza w ciemni redakcji, gazety sprzedają legendę, Bonnie i cygaro, porwany przedsiębiorca pogrzebowy '
  'Darby; zasiew teczki łowcy.',
  [('Joplin',
    'Joplin',
    [('Joplin',
      [('joplin_walka',
        'PO',
        'stat',
        None,
        'Kurtyna „Act III · How did a joke make them famous?”; rozsuwa się na garaż w Joplin; za parawanem błyski z okien, dwie '
        'sylwetki policjantów padają, gang zbiega do auta i wyjeżdża przez drzwi garażu',
        'L: On April 13, 1933, two officers walked up to the garage, and the gang answered with gunfire from the windows.'),
       ('joplin_ofiary',
        'PŚ',
        'naj',
        None,
        'Na pustym podwórku leżą dwie czapki policyjne; z nitek zjeżdżają podpisy „Harry McGinnis”, „Wes Harryman”; światło '
        'przygasa',
        'L: Detective Harry McGinnis and Constable Wes Harryman were killed, and the gang fled in such a hurry that they left '
        'almost everything behind.'),
       ('joplin_rzeczy',
        'D',
        'stat',
        None,
        'Policjant chodzi po opuszczonym pokoju: walizki, karabiny, zeszyt z wierszem; podnosi z podłogi aparat wysoko, do oczu, '
        'a z dołu aparatu wysuwa się w dół klisza z mikro, czarnymi pozami Bonnie w klatkach; policjant lekko macha aparatem, otwiera '
        'usta, tabliczka „OOO…” (markery reżysera 21.11)',
        "L: Remember that camera? It was lying on the floor, next to their guns, their clothes and one of Bonnie's poems.")])]),
   ('Redakcja Joplin Globe',
    'redakcja Joplin Globe',
    [('Redakcja Joplin Globe',
      [('ciemnia',
        'PŚ',
        'naj',
        None,
        'W czerwonym świetle ciemni klisza pływa w kuwecie; na papierze wyłania się Bonnie z rewolwerem i cygarem',
        'L: The Joplin Globe developed the film, and suddenly a country deep in the Great Depression had pictures of its new '
        'favorite villains.')])]),
   ('Ulica',
    'ulica',
    [('Ulica',
      [('kiosk',
        'PO',
        'odj',
        None,
        'Gazeciarz macha gazetą; kolejka ludzi w łatanych płaszczach kupuje; sterta gazet rośnie aż do markizy; tabliczka '
        '„EXTRA!”',
        'L: People who had lost their jobs and farms to the banks bought every edition, because these two looked like they were '
        'having a much better time.')])]),
   ('Kryjówka',
    'kryjówka',
    [('Kryjówka',
      [('cygaro_zlosc',
        'Z',
        'stat',
        None,
        'Bonnie w aucie czyta gazetę, marszczy brwi i wyrzuca cygaro przez okno; tabliczka „CIGARETTES!”',
        'L: Bonnie loved the attention, but she hated being called a cigar smoker, because she only ever smoked cigarettes.')])]),
   ('Ruston',
    'Ruston',
    [('Ruston',
      [('darby_auto',
        'PP',
        'stat',
        None,
        'Gang odjeżdża cudzym autem sprzed domu; z domu wybiegają młody mężczyzna w garniturze i kobieta w kapeluszu i wskakują '
        'do drugiego auta; przy krawężniku stoi bordowy samochód, w którym czekają Buck i Blanche',
        'L: Two weeks later in Louisiana they stole a car, and its owner, a young man named Dillard Darby, chased them with a '
        'friend, Sophia Stone.'),
       ('darby_tyl',
        'PŚ',
        'naj',
        None,
        'Darby i Stone siedzą ściśnięci na tylnym siedzeniu; Bonnie odwraca się do nich i pyta; podpisy „Dillard Darby, '
        'undertaker”, „Sophia Stone”',
        'L: The gang caught them instead and took them along, and when Bonnie asked Darby what he did for a living, he said he '
        'was an undertaker.'),
       ('darby_smiech',
        'Z',
        'stat',
        None,
        'Bonnie wybucha śmiechem i klepie się po kolanie; Darby blednie; tabliczka „HA HA!”',
        'L: Bonnie reportedly laughed and said that one day he might have to work on her.')])]),
   ('Droga w Arkansas',
    'droga w Arkansas',
    [('Droga w Arkansas',
      [('darby_puszczeni',
        'PP',
        'stat',
        None,
        'Porwani wysiadają na poboczu; Clyde wręcza im przez okno banknot; Ford odjeżdża w kurzu, Darby zostaje z banknotem w '
        'ręce',
        'L: Later they let both hostages go near Waldo, Arkansas, and even gave them five dollars to get home.')])]),
   ('Biuro Hamera',
    'biuro Hamera',
    [('Biuro Hamera',
      [('teczka_zasiew',
        'D',
        'stat',
        None,
        'Wycinki z gazet odfruwają z kiosku i jeden po drugim wpadają do grubej teczki na pustym biurku; krzesło przy biurku '
        'jest puste, na oparciu wisi kapelusz',
        'L: None of them knew yet that every one of these clippings would end up in a single file, on the desk of the man who '
        'would finally catch them.')])]),
   ('Mapa z gazet',
    'mapa z gazet',
    [('Mapa z gazet',
      [('plakaty',
        'PO',
        'odj',
        None,
        'Mapa z gazet: pinezki w Teksasie, Oklahomie, Missouri, Luizjanie; na mapie wyrastają ich twarze z listów gończych',
        "L: For now, their faces were on wanted posters in five states, but what happens when America's most famous getaway "
        'driver misses a road sign?')])])]),
 (4,
  'What does life on the run really look like?',
  'Most w Wellington, poparzona noga Bonnie, szeryf przywiązany do drzewa, życie w samochodzie, list do Forda, Platte City i '
  'Dexfield (śmierć Bucka), odejście W.D., spotkania z matkami, zasadzka w Sowers.',
  [('Wellington',
    'Wellington',
    [('Wellington',
      [('wellington_noc',
        'PO',
        'odj',
        None,
        'Kurtyna „Act IV · What does life on the run really look like?”; nocna droga przez prerię, Ford pędzi; tablica „DETOUR” '
        'mija się w ciemności',
        'L: In June 1933, near Wellington, Texas, Clyde was driving fast at night and missed the signs warning that the bridge '
        'ahead was out.'),
       ('wellington_most',
        'PO',
        'szarp',
        3.4,
        'Ford wjeżdża na rozebrany most, leci w wąwóz, przewraca się; z dziury po kuli w baku cieknie benzyna na rozgrzany wydech i bucha ogień; mocny wstrząs kamery, przed uderzeniem '
        'muzyka milknie (szczyt 1)',
        'pisk opon, łamanie desek, uderzenie o dno, buchający ogień, cisza muzyki (szczyt 1)'),
       ('wellington_bonnie',
        'PŚ',
        'naj',
        None,
        'Clyde i W.D. wyciągają Bonnie z płonącego auta; jej noga dymi; tabliczka „AAAA!”',
        "L: The car caught fire from the leaking gas, and it scorched Bonnie's leg so badly that she never walked properly "
        'again.')])]),
   ('Farma pod Wellington',
    'farma pod Wellington',
    [('Farma pod Wellington',
      [('farma_auto',
        'PŚ',
        'naj',
        4.5,
        'Na podwórku farmy Clyde kuleje do szarego Forda farmera i wsiada za kierownicę; farmer z żoną patrzą z ganku',
        ''),
       ('farma',
        'PP',
        'stat',
        None,
        'Rodzina farmerów nosi wiadra i opatruje Bonnie na ganku; drogą nadjeżdżają szeryf i marszałek',
        'L: A farm family took them in and tried to help, but somebody called the sheriff, and two lawmen arrived.')])]),
   ('Las w Oklahomie',
    'las w Oklahomie',
    [('Las w Oklahomie',
      [('drzewo',
        'PP',
        'stat',
        None,
        'Szeryf i marszałek przywiązani drutem kolczastym do drzewa; Clyde macha im z szarego Forda farmera na pożegnanie; tabliczka „BYE!”',
        'L: The gang took both lawmen hostage, drove them across the border into Oklahoma and left them tied to a tree with '
        'barbed wire.')])]),
   ('Motel przy drodze',
    'motel przy drodze',
    [('Motel przy drodze',
      [('noszenie',
        'PŚ',
        'naj',
        None,
        'Clyde niesie Bonnie na rękach z auta do pokoju motelu; noga w bandażu; Bonnie krzywi się przy każdym jego kroku',
        'L: For weeks afterwards Clyde carried Bonnie in his arms, because she could no longer stand on her own.')])]),
   ('Obóz przy drodze',
    'obóz przy drodze',
    [('Obóz przy drodze',
      [('oboz',
        'PO',
        'jaz',
        None,
        'Wieczór przy drodze: auto z otwartymi drzwiami, pranie suszy się na drzwiach, puszka fasoli na ognisku, Bonnie pisze, '
        'Clyde czyści karabin; obok drugiego auta bordo siedzą Buck i Blanche',
        'L: This was the glamorous outlaw life: sleeping in stolen cars, eating cold beans from cans and washing in rivers.')])]),
   ('Rzeka',
    'rzeka',
    [('Rzeka',
      [('rzeka',
        'PŚ',
        'naj',
        # reżyser 23.11: „wydłuż scenę i daj narrację, oraz Ken Burns na myjący kadr głowy i wyskakującą rybę po chwili”
        None,
        'Bonnie myje włosy w rzece; kamera powoli najeżdża na jej głowę (Ken Burns); po chwili ryba wyskakuje jej spod ręki; '
        'tabliczka „BRRR!”',
        'L: Bonnie still tried to look like a movie star, even when her only mirror was a cold river.')])]),
   ('Obóz przy drodze',
    'obóz przy drodze',
    [('Obóz przy drodze',
      [('list_ford',
        'D',
        'stat',
        None,
        'Na masce Forda leży list na papierze firmowym; zjeżdża podpis „Clyde?” i tabliczka ze znakiem zapytania',
        'L: Clyde preferred stolen Fords, and Henry Ford even received a letter thanking him for such a fine getaway car, though '
        'nobody is sure Clyde really wrote it.')])]),
   ('Platte City',
    'Platte City',
    [('Platte City',
      [('platte',
        'PO',
        'stat',
        None,
        # reżyser 23.11: „więcej wyjaśnień w tej scenie” — kwestia mówi kiedy, gdzie, co przywiozła policja i jak się wyrwali;
        # w kadrze zawieszka miejsca i czasu, podpisy „ARMORED CAR”, „Buck Barrow”, „Blanche”, na końcu Ford gangu ucieka
        'Platte City, lipiec 1933, teatr cieni: policja otacza dwa domki motelu, podjeżdża opancerzone auto z podpisem; błyski, '
        'gang odpowiada ogniem; sylwetka Bucka chwieje się (podpis), szyba pęka przed Blanche (podpis); Ford gangu wyrywa się '
        'spod domków i ucieka',
        'L: In July 1933, police surrounded their two motel cabins near Platte City, Missouri, and even brought an armored car; '
        'the gang shot their way out, but Buck was hit in the head, and flying glass blinded Blanche in one eye.')])]),
   ('Dexfield Park',
    'Dexfield Park',
    [('Dexfield Park',
      [('dexfield',
        'PO',
        'jaz',
        None,
        'Świt w lesie w Iowie: z krzaków wychodzą farmerzy i policjanci; Buck leży przy ognisku, Blanche klęczy przy nim i nie '
        'chce odejść',
        'L: Days later, in an Iowa park, a posse of police and farmers found their camp, and Buck was captured, dying, while '
        'Blanche refused to leave him.')])]),
   ('Rzeka w Iowie',
    'rzeka w Iowie',
    [('Rzeka w Iowie',
      [('przeprawa',
        'PP',
        'stat',
        None,
        'Clyde, Bonnie i W.D. brną przez rzekę; Clyde ciągnie Bonnie za rękę; na brzegu za nimi błyski',
        'L: Clyde, Bonnie and W.D. waded across a river and escaped, wounded, with almost nothing left.')])]),
   ('Droga',
    'droga',
    [('Droga',
      [('wd_odchodzi',
        'PŚ',
        'naj',
        None,
        'Nocą W.D. wysiada po cichu i odchodzi w ciemność; Bonnie patrzy za nim przez szybę',
        'L: Soon even W.D. Jones slipped away in the night and went home to his mother.')])]),
   ('Droga pod Dallas',
    'droga pod Dallas',
    [('Droga pod Dallas',
      [('rodziny',
        'PO',
        'jaz',
        None,
        'Nocą przy polnej drodze stoją dwa auta z wygaszonymi światłami; matki podają przez okna koszyki z jedzeniem, Bonnie '
        'oddaje pranie',
        'L: Bonnie and Clyde went home too, in their own way: every few weeks they met their families on dark country roads '
        'outside Dallas, bringing laundry and taking home-cooked food.')])]),
   ('Sowers',
    'Sowers',
    [('Sowers',
      [('sowers',
        'PO',
        'stat',
        None,
        'Nocą przy drodze z krzaków wyskakują policjanci; błyski za parawanem za wcześnie, Ford z przestrzelonymi szybami '
        'odjeżdża; tabliczka „OUCH!”',
        'L: In November, the Dallas sheriff tried to ambush one of these family picnics, and both of them escaped with bullets '
        "in their legs, so why didn't they just stop?")])])]),
 (5,
  'Who finally went after them?',
  'Odbicie więźniów z Eastham, Simmons wynajmuje Hamera; Hamer przestaje gonić, otwiera teczkę, DAY 1, DAY 20, granica stanów, '
  'pętle prowadzą do matek.',
  [('Eastham',
    'Eastham',
    [('Eastham',
      [('odbicie',
        'PO',
        'jaz',
        None,
        'Kurtyna „Act V · Who finally went after them?”; mgła nad polami Eastham; więźniowie wyciągają broń z rowu, strażnik '
        'pada; z mgły trąbi klakson, wyjeżdża Ford, więźniowie wskakują na stopnie',
        'L: Instead, in January 1934, Clyde went back to Eastham to free his friends, while Bonnie honked the horn in the fog to '
        'guide them.'),
       ('straznik',
        'PŚ',
        'naj',
        None,
        'Mgła rzednie; na drodze zostaje kapelusz strażnika; z nitki zjeżdża podpis „Major Joe Crowson”; światło przygasa',
        'L: Five prisoners got away, but a guard named Joe Crowson was shot and later died.')])]),
   ('Biuro więziennictwa',
    'biuro więziennictwa',
    [('Biuro więziennictwa',
      [('simmons',
        'PŚ',
        'naj',
        None,
        'Szef więziennictwa wali pięścią w biurko, aż podskakuje kałamarz; podpis „Lee Simmons, Texas prisons chief”',
        'L: The head of the Texas prisons, Lee Simmons, took it personally, and he went looking for one particular man.')])]),
   ('Ganek w Austin',
    'ganek w Austin',
    [('Ganek w Austin',
      [('hamer',
        'PP',
        'stat',
        None,
        'Na ganku wysoki mężczyzna w kapeluszu wstaje powoli z bujanego fotela i sięga po karabin; podpis „Frank Hamer, retired '
        'Texas Ranger”',
        'L: Frank Hamer was a retired Texas Ranger who had survived dozens of gunfights, and in February 1934 he quietly took '
        'the job.')])]),
   ('Droga w Teksasie',
    'droga w Teksasie',
    [('Droga w Teksasie',
      [('poscigi',
        'PO',
        'odj',
        None,
        'Radiowóz goni Forda po zakrętach; Ford znika za wzgórzem, radiowóz wylatuje z zakrętu i ląduje w rowie kołami do góry; '
        'tabliczka „AGAIN?!”',
        'L: Police in five states had been chasing Bonnie and Clyde for two years, and those chases usually ended the same way, '
        'with the police car in a ditch.')])]),
   ('Biuro Hamera',
    'biuro Hamera',
    [('Biuro Hamera',
      [('hak_szuflada',
        'PŚ',
        'naj',
        None,
        'Hamer zdejmuje z biurka zabawkowy radiowóz i chowa go do szuflady; tabliczka „NO MORE CHASING”',
        'L: So Hamer did something nobody expected: he stopped chasing them.'),
       ('hak_teczka',
        'PŚ',
        'naj',
        None,
        'Hamer otwiera grubą teczkę z aktu III; wycinki wyfruwają i same przypinają się do mapy; Hamer stawia kubek kawy i siada '
        'wygodnie',
        'L: Instead, he sat down with that file of newspaper clippings and a map, and he waited for them to make one mistake.'),
       ('podkreslenie',
        'D',
        'stat',
        None,
        "Hamer podkreśla w aktach jedno zdanie czerwonym ołówkiem, dwa razy; z nitki zjeżdża tabliczka „HE WON'T GO BACK”",
        'L: He underlined one line twice, a line the papers reportedly quoted from Clyde after Eastham: he would never go back, which meant there would never be a '
        'surrender, only the question of where.')])]),
   ('Droga w Teksasie',
    'droga w Teksasie',
    [('Droga w Teksasie',
      [('dzien1',
        'PO',
        'odj',
        None,
        'Zjeżdża zawieszka „DAY 1”; Hamer jedzie starym autem przez prerię z mapą na kolanach',
        'L: On day one, Hamer started driving, not after them, but through every town where they had already been.')])]),
   ('Motel przy drodze',
    'motel przy drodze',
    [('Motel przy drodze',
      [('hamer_motel',
        'PŚ',
        'naj',
        None,
        'Hamer pokazuje recepcjoniście zdjęcie Bonnie; recepcjonista kiwa głową i wskazuje drogę; na ladzie stos pustych puszek '
        'po fasoli',
        'L: Everywhere he went, someone remembered them: a limping girl, a young man in a hat, a new Ford and a pile of empty '
        'cans.')])]),
   ('Granica stanów',
    'granica stanów',
    [('Granica stanów',
      [('dzien20',
        'PO',
        'jaz',
        None,
        'Zawieszka „DAY 20”; na drodze tablica „STATE LINE”; Ford przemyka przez granicę, radiowóz hamuje przed nią z piskiem',
        'L: By day twenty, he understood their main trick: in those days, police could rarely follow a car across a state line, '
        'so Clyde simply drove into the next state.')])]),
   ('Biuro Hamera',
    'biuro Hamera',
    [('Biuro Hamera',
      [('mapa',
        'PŚ',
        'naj',
        None,
        'Hamer przypina do mapy papierowe znaczniki: Teksas, Oklahoma, Missouri, Luizjana; łączy je czerwoną nicią',
        'L: So Hamer stopped marking where they had been and started marking where they kept coming back to.'),
       ('petle',
        'D',
        'stat',
        None,
        'Czerwona nić na mapie układa się w pętle wzdłuż granic stanów; każda pętla wraca do Dallas, do dwóch małych domków',
        'L: The loops always ran along state lines, and sooner or later every one of them led home to their mothers, so how long '
        'would Hamer have to wait?')])])]),
 (6,
  'When did America stop cheering?',
  'DAY 50: Grapevine (poważnie od tej chwili), Maree Tullis, gazety odwracają się, nagrody, Commerce, komendant Boyd i wiadomość '
  'o cygarach; gazeta na biurku Hamera.',
  [('Grapevine',
    'Grapevine',
    [('Grapevine',
      [('grapevine',
        'PO',
        'jaz',
        None,
        'Kurtyna „Act VI · When did America stop cheering?”; zawieszka „DAY 50 · Easter Sunday”; wiejska droga, kwitnące drzewa, '
        'Ford stoi na poboczu; nadjeżdżają dwaj motocykliści i zwalniają',
        "L: On day fifty of Hamer's hunt, Easter Sunday 1934, two young highway patrolmen stopped near Grapevine, Texas, to help "
        'what they thought was a stranded car.'),
       ('grapevine_cien',
        'PO',
        'stat',
        None,
        'Muzyka milknie; za parawanem dwa błyski, dwie sylwetki z motocyklami padają; motocykl przewraca się z łoskotem (szczyt '
        '2)',
        'L: They were shot before they could draw their guns.')])]),
   ('Cmentarz w Alto',
    'cmentarz w Alto',
    [('Cmentarz w Alto',
      [('tullis',
        'PŚ',
        'naj',
        None,
        'Przy trumnie stoi młoda kobieta w białej sukni ślubnej; z góry powoli spadają płatki; podpis „Maree Tullis”',
        'L: One of them, H.D. Murphy, was supposed to marry his sweetheart, Maree Tullis, that month, and local historians say '
        'she came to his funeral in her wedding dress.')])]),
   ('Ulica',
    'ulica',
    [('Ulica',
      [('gazety_zle',
        'PO',
        'odj',
        None,
        'Nowe gazety z nagłówkiem o bezlitosnej Bonnie; ludzie zgniatają je i rzucają na ziemię; kolejka przy kiosku się '
        'rozchodzi',
        'L: The papers claimed Bonnie had laughed over a dying man, which was probably not true, but after Grapevine nobody was '
        'cheering for them anymore.'),
       ('listy_gon',
        'PP',
        'stat',
        None,
        'Na słupie wyrastają kolejne listy gończe z nagrodą; farmer z dubeltówką przystaje, czyta i odwraca się w stronę drogi',
        'L: Rewards were posted across the South, and from then on every farmer with a shotgun was watching the road for a '
        'stolen Ford.')])]),
   ('Commerce',
    'Commerce',
    [('Commerce',
      [('commerce',
        'PP',
        'stat',
        None,
        'Ford ugrzązł w rowie pod Commerce w Oklahomie; dwaj stróże prawa idą przez pole, żeby pomóc',
        'L: Five days later, near Commerce, Oklahoma, their car slid into a ditch again, and two lawmen walked over to help.'),
       ('commerce_cien',
        'PO',
        'stat',
        None,
        'Za parawanem błysk, starszy konstabl pada; komendant podnosi ręce i wsiada do Forda',
        'L: Clyde killed Constable Cal Campbell and took the police chief, Percy Boyd, as a hostage.'),
       ('boyd',
        'PŚ',
        'naj',
        None,
        'Komendant na tylnym siedzeniu z rękami w górze; Bonnie odwraca się do niego z uniesionym palcem; podpis „Percy Boyd, '
        'police chief”',
        'L: They drove Boyd around for hours, and before letting him go in Kansas, Bonnie gave him one message for the '
        'newspapers.')])]),
   ('Droga w Kansas',
    'droga w Kansas',
    [('Droga w Kansas',
      [('boyd_tab',
        'Z',
        'stat',
        None,
        "Boyd stoi przy drodze i patrzy za odjeżdżającym Fordem; zjeżdża nad nim tabliczka „SHE DOESN'T SMOKE CIGARS!”",
        'L: Not that she was innocent, and not that she was sorry, only that Bonnie Parker did not smoke cigars.')])]),
   ('Drukarnia',
    'drukarnia',
    [('Drukarnia',
      [('prasa_cygaro',
        'PO',
        'jaz',
        None,
        'Maszyna drukarska wypluwa gazety z nagłówkiem „BONNIE: NO CIGARS!”; jedna gazeta ląduje na biurku Hamera obok mapy',
        "L: The papers printed that too, and one of them landed on Hamer's desk, next to a map that was finally full, but he "
        'still needed someone to tell him the day.')])])]),
 (7,
  'How do you set a trap for a ghost?',
  'Układ z Ivym Methvinem, wiersz dla matki, ostatnie pożegnanie, Shreveport, noc w krzakach, sześciu ludzi, DAY 102: ciężarówka '
  'na lewarku, kanapka, zasadzka.',
  [('Chata w Luizjanie',
    'chata w Luizjanie',
    [('Chata w Luizjanie',
      [('methvin',
        'PŚ',
        'naj',
        None,
        'Kurtyna „Act VII · How do you set a trap for a ghost?”; chata w Luizjanie; Hamer siedzi przy stole naprzeciw brodatego '
        'farmera, między nimi papier z pieczęcią „PARDON”; farmer kiwa głową; podpis „Ivy Methvin”',
        'L: Hamer found that someone in Ivy Methvin, the father of Henry Methvin, a young convict they had freed at Eastham: '
        'help set a trap, and your son will be pardoned.')])]),
   ('Dom matki Bonnie',
    'dom matki Bonnie',
    [('Dom matki Bonnie',
      [('wiersz',
        'PŚ',
        'naj',
        None,
        'Bonnie kuleje do matki i wręcza jej zeszyt; matka czyta przy lampie, a za oknem czeka Ford z zapalonymi światłami',
        'L: Around that time, Bonnie gave her mother a new poem, which said that one day she and Clyde would go down together '
        'and be buried side by side.')])]),
   ('Dallas',
    'Dallas',
    [('Dallas',
      [('pozegnanie',
        'PO',
        'jaz',
        None,
        'Ford przejeżdża powoli obok dwóch domów; w oknach dwie matki machają; Ford znika za zakrętem',
        'L: Then they drove on, because a car was the only home they had left.')])]),
   ('Shreveport',
    'Shreveport',
    [('Shreveport',
      [('henry_wsiada',
        'PŚ',
        'naj',
        None,
        'Na poboczu drogi pod Shreveport chłopak w kaszkiecie, jeden z więźniów z Eastham, macha do Forda; Ford zwalnia i zabiera go na tylne siedzenie; podpis „Henry Methvin”',
        'L: On the road outside Shreveport, they picked up one of the Eastham prisoners, a boy named Henry Methvin.'),
       ('shreveport',
        'PP',
        'odj',
        None,
        'Przed kawiarnią w Shreveport chłopak wysiada z Forda i znika w tłumie; podpis „Henry Methvin”; Ford czeka chwilę i '
        'odjeżdża bez niego',
        'L: On May 21, Henry Methvin got separated from Bonnie and Clyde in Shreveport, and Hamer knew where he would go: home '
        "to his father's farm, where they would come looking for him.")])]),
   ('Droga w Luizjanie',
    'droga w Luizjanie',
    [('Droga w Luizjanie',
      [('noc',
        'PO',
        'jaz',
        None,
        'Zawieszka „DAY 101”; noc w lesie, sześciu mężczyzn kuli się w krzakach; nad kapeluszami krążą komary, jeden mężczyzna '
        'bezgłośnie klepie się w kark',
        'L: On the night of May 22, Hamer and five other lawmen hid in the bushes along a country road in Louisiana, and they '
        'waited there until dawn, swatting mosquitoes in silence.'),
       ('posse',
        'PŚ',
        'naj',
        None,
        'W krzakach sześciu mężczyzn; nad każdym po kolei zjeżdża podpis: Hamer, Gault, Alcorn, Hinton, Jordan, Oakley; Hinton '
        'przeciera okulary',
        'L: Hamer had brought his old partner Manny Gault, two Dallas deputies who knew Clyde by sight, Bob Alcorn and Ted '
        'Hinton, and the local sheriff, Henderson Jordan, with his deputy, Prentiss Oakley.'),
       ('zasadzka_rano',
        'PO',
        'jaz',
        None,
        "Zawieszka „DAY 102”; świt na leśnej drodze; ciężarówka Ivy'ego stoi na lewarku jak z przebitą oponą; w krzakach sześć "
        'kapeluszy i luf',
        "L: On the morning of day one hundred and two, May 23, Ivy Methvin's truck stood by the road on a jack as bait."),
       ('kanapka',
        'Z',
        'stat',
        None,
        'Wnętrze Forda: Bonnie w czerwonej sukience je kanapkę z papierka; Clyde prowadzi w skarpetkach i ciemnych okularach',
        'L: Clyde was driving in his socks, and Bonnie was eating a sandwich from a café in town.'),
       ('zwolnienie',
        'PP',
        'stat',
        2.2,
        'Ford zwalnia przy ciężarówce; Ivy macha z pobocza; Clyde opuszcza szybę i wychyla się',
        'warkot silnika zwalnia, chrzęst żwiru'),
       ('zasadzka',
        'PO',
        'stat',
        4.8,
        'Muzyka milknie; za parawanem dziesiątki błysków jeden po drugim, papierowy Ford drży i powoli zjeżdża do rowu; spada '
        'kapelusz; cisza (szczyt 3)',
        'cisza muzyki, seria strzałów za parawanem, szkło, potem cisza (szczyt 3)'),
       ('dym',
        'PŚ',
        'naj',
        None,
        'Dym opada; mężczyźni wychodzą z krzaków z bronią; jeden zdejmuje kapelusz; nikt nic nie mówi',
        'L: The lawmen fired more than a hundred rounds in a few seconds, and it was over before Clyde could reach for a '
        'gun.')])])]),
 (8,
  'Who owns the legend?',
  'Kto ma legendę: pamiątkarze w Arcadii, Darby przy ciele, osobne groby, auto na jarmarkach, Blanche, milczenie Hamera, '
  'Hollywood 1967, gra 2026, puenta i podziękowanie.',
  [('Arcadia',
    'Arcadia',
    [('Arcadia',
      [('pamiatki',
        'PO',
        'odj',
        None,
        'Kurtyna „Act VIII · Who owns the legend?”; tłum otacza podziurawionego Forda w Arcadii; ktoś odcina nożyczkami pukiel '
        'włosów, ktoś kawałek sukienki; szeryf odgania ludzi',
        "L: Within hours thousands of people crowded into the little town of Arcadia, and souvenir hunters cut locks of Bonnie's "
        'hair and pieces of her dress.')])]),
   ('Zakład pogrzebowy w Arcadii',
    'zakład pogrzebowy w Arcadii',
    [('Zakład pogrzebowy w Arcadii',
      [('darby_zaklad',
        'PŚ',
        'naj',
        None,
        'W zakładzie pogrzebowym młody mężczyzna w fartuchu zakłada rękawice; z nitki zjeżdża jego stary podpis „Dillard Darby, '
        'undertaker”',
        'L: And according to local accounts, the undertaker Bonnie had laughed at a year earlier helped prepare her body.')])]),
   ('Dwa cmentarze w Dallas',
    'dwa cmentarze w Dallas',
    [('Dwa cmentarze w Dallas',
      [('pogrzeby',
        'PO',
        'odj',
        None,
        'Dwa osobne pogrzeby na dwóch cmentarzach, między nimi droga; tłumy przy obu; matka Bonnie odwraca się plecami do '
        "cmentarza Clyde'a",
        'L: Her poem got almost everything right except the last line: her mother refused to let them share a grave, so they '
        'were buried in different cemeteries.')])]),
   ('Jarmark',
    'jarmark',
    [('Jarmark',
      [('auto_jarmark',
        'PO',
        'odj',
        None,
        'Na jarmarku pod namiotem stoi podziurawiony Ford; kolejka ludzi płaci za wejście i zagląda w dziury po kulach; nad '
        'namiotem kręci się karuzela',
        'L: Even their bullet-riddled car went on tour, and people paid to look at it at fairs across the country.')])]),
   ('Dom Blanche',
    'dom Blanche',
    [('Dom Blanche',
      [('blanche_po',
        'PŚ',
        'naj',
        None,
        'Starsza Blanche w okularach z jednym ciemnym szkłem podlewa kwiaty przed domkiem; zjeżdża zawieszka „1988”',
        'L: Blanche served six years in prison and lived quietly until 1988, the only one of the four who grew old.')])]),
   ('Ganek w Austin',
    'ganek w Austin',
    [('Ganek w Austin',
      [('hamer_ganek',
        'PŚ',
        'naj',
        None,
        'Hamer na ganku odkłada gazetę z nagłówkiem o zasadzce, zakłada kapelusz i odwraca się od reporterów',
        'L: Hamer rarely talked about that morning, and he never wrote a book about it.')])]),
   ('Kino',
    'kino',
    [('Kino',
      [('film_hamer',
        'PO',
        'jaz',
        None,
        'Gazety składają się w ekran kina: piękna para z filmu z 1967 roku, potem aktor grający Hamera stoi związany, a filmowa '
        "Bonnie robi sobie z nim zdjęcie; widownia się śmieje; obok ekranu prawdziwy Hamer z tabliczką „THAT'S NOT ME!”",
        'L: Thirty years later, a Hollywood hit made Bonnie and Clyde young and beautiful, and showed Hamer captured and '
        'humiliated by the gang, something that never happened, so his family sued the studio.'),
       ('gra',
        'PO',
        'jaz',
        None,
        'Ekran z gazet migocze: zamiast filmu pojawia się kolorowa, pikselowa para uciekinierów w aucie z gry wideo; widzowie w '
        'pierwszym rzędzie trzymają pady',
        'L: And in 2026, a new video game built its heroes on the same old romance.')])]),
   ('Teatr z gazet',
    'teatr z gazet',
    [('Teatr z gazet',
      [('koniec',
        'PŚ',
        'naj',
        None,
        'Papierowa Bonnie z cygarem i Clyde kładą się płasko w stronę gazety; obok zamyka się teczka Hamera; kurtyna zasuwa się',
        'L: The real Bonnie and Clyde were two broke kids from Dallas who left at least nine dead lawmen behind them; newspapers '
        'made them legends, and a patient man reading their file brought them down.')])]),
   ('Teatr',
    'teatr',
    [('Teatr',
      [('dzieki',
        'PŚ',
        'naj',
        None,
        'Przed kurtyną wychodzą wszystkie lalki filmu i kłaniają się po kolei; Hamer zdejmuje kapelusz, Bonnie macha',
        "L: Thank you for watching! If you like my videos, support me, and I'll do my best.")])])])]

WYDLUZ = {'akt2': 1.0, 'rzeka': 1.6,
 'atoka': 1.0,
 'auto_jarmark': 1.5,
 'buck': 1.0,
 'commerce': 1.0,
 'darby_auto': 1.0,
 'dexfield': 1.5,
 'drzewo': 1.0,
 'dzien1': 1.0,
 'dzien20': 1.0,
 'eastham': 2.0,
 'farma': 1.0,
 'film_hamer': 1.5,
 'grapevine': 1.5,
 'grapevine_cien': 1.2,
 'hillsboro': 1.0,
 'joplin_dom': 1.5,
 'joplin_walka': 1.5,
 'kaufman': 1.5,
 'kiosk': 2.0,
 'listy_gon': 1.5,
 'mapa': 1.5,
 'oboz': 1.5,
 'odbicie': 2.0,
 'pamiatki': 2.5,
 'petle': 2.0,
 'plakaty': 1.0,
 'platte': 2.6,
 'pogrzeby': 2.0,
 'posse': 1.0,
 'prasa': 2.0,
 'prasa_cygaro': 1.5,
 'przeprawa': 1.0,
 'rodziny': 1.5,
 'sowers': 1.0,
 'stacja': 1.0,
 'wagon': 1.5,
 'wellington_noc': 1.0,
 'zasadzka_rano': 1.5}

HAK = ['hak_cygaro', 'joplin_rzeczy', 'prasa', 'zdjecie']

JEZYK = "en"  # film tylko po angielsku (kanał Paper Theatre)
TEMPO_EN = 2.84  # angielski klon (TEATR): „Pierwszy cesarz” EN, 1233 słowa w 434 s nagrań (17.11.2026)
SLOWNIE = {"1920s": "nineteen twenties", "1930": "nineteen thirty", "1932": "nineteen thirty-two", "1933": "nineteen thirty-three",
           "1934": "nineteen thirty-four", "1967": "nineteen sixty-seven", "1988": "nineteen eighty-eight",
           "2026": "twenty twenty-six", "May 21": "May twenty-first", "May 22": "May twenty-second", "May 23": "May twenty-third",
           "April 13": "April thirteenth"}
LEKTOR = Path(__file__).resolve().parents[4] / "output/bonnie-i-clyde/lektor_en"
ETYKIETY = {}  # napisy w kadrze są już po angielsku (wytyczne 1.13)


def kwestia(dzwiek):
    return dzwiek[2:].strip() if dzwiek.startswith("L:") else ""


BEZ_NAGRAN = [False]  # True: długości z tempa lektora (TEMPO_EN), jak przy układaniu akcji ujęć — zob. ujecia_szkicu()


def nagranie(dzwiek):
    """Długość nagranej kwestii (lektor_en/<klucz>.json) albo None, gdy jeszcze jej nie ma albo tekst się zmienił."""
    txt = kwestia(dzwiek)
    for f in LEKTOR.glob("*.json") if txt and LEKTOR.exists() and not BEZ_NAGRAN[0] else ():
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("text") == txt:
            return meta["duration"]
    return None


def slownie(txt):
    for k, v in SLOWNIE.items():
        txt = txt.replace(k, v)
    return txt


def okno_kwestii(dzwiek, hak=False):
    """(start, długość) kwestii w ujęciu: oddech (w haku krótszy), potem nagranie lektora — a zanim powstanie, tempo lektora."""
    txt = kwestia(dzwiek)
    if not txt:
        return (0.0, 0.0)
    real = nagranie(dzwiek)
    return (0.4 if hak else 0.6, real if real else len(slownie(txt).split()) / TEMPO_EN)


# Pauza po kwestii, zanim padnie cięcie (Podręcznik, „Rytm” 2 i 3; reżyser 14.11.2026 przy „Pierwszym cesarzu”).
PAUZA_PO = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}
HAK_PAUZA = 1.0  # w haku szybciej (szkic D)


# Gagi (reżyser 19.11.2026: „tak, gagi robimy wszystkie” — 30 propozycji z docs/filmy/bonnie-i-clyde/GAGI.md; zasady:
# Podręcznik → Humor i gagi). Gag dopisuje się do opisu ujęcia; GAG_CZAS to sekundy, o które gag wydłuża ujęcie.
GAGI = {
    "zdjecie": "Bonnie kręci rewolwerem na palcu i wsuwa go za pasek jak rewolwerowiec, a cygaro bierze od chłopaka "
               "(marker reżysera 19.11)",
    "wprowadzenie2": "Bonnie strzela, kula odbija się od brzegów kadru jak w grze i trafia w bak Forda; paliwo cieknie pod "
                     "auto (marker reżysera 19.11)",
    "hak_cygaro": "na „didn't smoke cigars” cygaro w ustach Bonnie smętnie opada jak zwiędły kwiat (puzon w dół)",
    "indyki": "po „stolen turkeys” indyk ląduje na czapce policjanta, policjant stoi godnie dalej, a potem indyk z niej odlatuje za kadr",
    "slub": "na „a very permanent decision” pęka prawa nitka wstęgi HAPPY EVER AFTER, wstęga zwisa krzywo; Roy zerka w górę "
            "(W3: nitka teatru)",
    "kawiarnia": "na „something exciting” przez kawiarnię toczy się kula stepowego zielska; Bonnie odprowadza ją wzrokiem",
    "kuchnia": "na „he was arrested” serduszka odjeżdżają w górę, na tej samej nitce zjeżdżają kajdanki",
    "akt2": "na „keep driving” auto odjeżdża bez Bonnie, wraca tyłem, Bonnie wsiada z miną „serio?”",
    "stacja": "na „only a few dollars” z otwartej kasy wylatuje ćma; sprzedawca rozkłada ręce (W1: pusta kasa)",
    "wd": "po „sounded exciting” W.D. wskakuje do auta przez okno, nogi machają w powietrzu",
    "joplin_dom": "na „normal family” w oknach pięć uśmiechów jak na zdjęciu rodzinnym; z okna wysuwa się lufa, Bonnie ją wpycha",
    "ciemnia": "kiedy na odbitce pojawia się Bonnie z cygarem, wywołującemu wypada papieros z ust, „O!”",
    "kiosk": "mężczyzna w kolejce wywraca puste kieszenie, wylatuje ćma; i tak kupuje gazetę za ostatnią monetę (W1)",
    "darby_auto": "skradziony Ford gaśnie: kaszel, kaszel; Darby prawie dobiega, auto rusza z piskiem tuż przed jego ręką",
    "darby_tyl": "na „undertaker” Darby wyjmuje miarkę i mierzy Bonnie od głowy do pasa; Bonnie patrzy na miarkę (czarny humor, "
                 "zasiew klamry z ujęcia darby_zaklad)",
    "darby_puszczeni": "na „five dollars” wiatr porywa banknot z ręki Darby'ego, Darby goni go jak przedtem auto",
    "oboz": "na „glamorous” złote iskry i blask jak w Hollywood; na „cold beans” iskry gasną, a łyżka stoi w zimnej fasoli na "
            "baczność",
    "list_ford": "na „fine getaway car” Ford mruga reflektorem i nieśmiało trąbi",
    "wd_odchodzi": "W.D. wymyka się na palcach jak w kreskówce; z prawej krawędzi ręka matki wyciąga go za ucho",
    "rodziny": "na „bringing laundry” Bonnie podaje matce stos prania wyższy od auta, matka oddaje maleńki talerzyk z ciastem",
    "dzien1": "Hamer jedzie tak wolno, że wyprzedza go starsza pani z laską; Hamer uchyla kapelusza",
    "hamer_motel": "na „a pile of empty cans” Hamer dotyka jednej puszki, cała piramida się rozsypuje; Hamer nawet nie mrugnie",
    "dzien20": "szeryf przy STATE LINE: przelatuje ptak, plask na kapeluszu; szeryf zastyga i powoli patrzy w górę, „…”",
    "mapa": "Hamer naciąga czerwoną nić po mapie, nić pęka, on bez patrzenia zawiązuje supeł (W3)",
    "listy_gon": "farmer z wiatrówką na widok pojazdu robi musztrę jak na paradzie w takt werbla — a to wóz z sianem i koniem",
    "prasa_cygaro": "drukarz czyta świeży nagłówek BONNIE: NO CIGARS! i zapala sobie cygaro",
    "noc": "na „swatting mosquitoes” szeryfowie po kolei klepią komary, jeden klepie sąsiada w policzek; obaj zastygają, „SHHH!”",
    "kanapka": "liść sałaty z kanapki Bonnie spada na okulary Clyde'a; Clyde go nie zdejmuje i prowadzi dalej",
    "auto_jarmark": "kasetka „10¢ A LOOK” pęka od monet, które sypią się na trawę (W1: puenta)",
    "gra": "pikselowe auto podskakuje i ląduje w pikselowym rowie; zjeżdża „AGAIN?!” (W2: puenta)",
    "dzieki": "kurtyna zacina się w połowie, Bonnie i Clyde szarpią ją razem, spada im na głowy; zza kulis wychyla się "
              "maszynista i macha (W3: puenta)",
    # druga seria (reżyser 19.11: „więcej gagów”)
    "wagon": "na „almost nothing” mały Clyde otwiera blaszane pudełko na obiad, wylatuje z niego ćma (W1: zasiew)",
    "poezja": "z góry kadru spada indyk, który odleciał z czapki policjanta, i siada przed podium jako jedyna widownia; na „stage” "
              "Bonnie się kłania, indyk gulgocze (pomost obrazem między historią Clyde'a i Bonnie)",
    "prasa": "po „gun girl” jedna gazeta wraca z wiatrem i przykleja się drukarzowi do twarzy, „MMPH!”, odkleja ją",
    "cela": "wiersz nie wychodzi: stos zgniecionych kartek przy pryczy rośnie aż do kolan Bonnie",
    "matka_obietnica": "na „for a few weeks” zawieszka WEEK 1 → 2 → 3, klakson, Bonnie biegnie do Forda; matka zostaje z "
                       "otwartymi ramionami",
    "buck": "po „family visit” piesek Blanche wyskakuje z jej rąk i obszczekuje Bucka, „YAP!”, Buck odskakuje",
    "joplin_karty": "Buckowi wypada z rękawa as i ląduje na stole; Blanche pochyla się do niego, „!”",
    "plakaty": "ostatni list gończy zjeżdża do góry nogami i po chwili przekręca się z „boing”",
    "farma": "na „somebody called the sheriff” farmerka upuszcza wiadro i macha na radiowóz, „OVER HERE!”",
    "drzewo": "przywiązanemu szeryfowi siada na kapeluszu ptak i zostaje; szeryf: „…”",
    "simmons": "po trzecim uderzeniu w biurko pęka prawa nitka szyldu TEXAS PRISON SYSTEM, szyld zwisa krzywo (W3)",
    "hamer": "kiedy Hamer odchodzi, pusty fotel buja się dalej sam, coraz mocniej; Hamer ogląda się na niego",
    "podkreslenie": "przy drugim podkreśleniu łamie się grafit, ołówek podskakuje, czubek odlatuje, „SNAP!”",
    "methvin": "po „pardoned” Ivy podnosi papier PARDON pod żarówkę i sprawdza go jak banknot, „HMM…”",
    "pozegnanie": "na „the only home” w tylnej szybie Forda kołysze się tabliczka HOME SWEET HOME",
    "shreveport": "Henry wchodzi do kawiarni, a kiedy wychodzi z dwiema kanapkami, Forda już nie ma; rozgląda się, „...?”",
    "posse": "ostatni podpis spada za nisko i stuka młodego Oakleya w kapelusz; Oakley się kuli, „OUCH!”",
}
GAG_CZAS = {"zdjecie": 1.0, "kuchnia": 0.8, "wd": 0.5, "darby_auto": 1.0, "darby_tyl": 0.8, "darby_puszczeni": 1.0,
            "wd_odchodzi": 1.0, "hamer_motel": 0.5, "listy_gon": 1.0, "noc": 1.0, "gra": 0.8, "dzieki": 1.8,
            "methvin": 0.8, "shreveport": 0.8, "poezja": 0.6,
            "waco": 1.6, "waco_przed": 3.2}


def ujecia(akt=None):
    """Płaska lista ujęć: (akt, nr w akcie, klucz, kadr, ruch, sekundy, opis, dźwięk). Długość ujęcia z kwestią liczy się
    z kwestii: oddech + nagranie (albo tempo) + pauza po (PAUZA_PO według granicy; w haku HAK_PAUZA) + WYDLUZ; sąsiednie
    ujęcia różnią się co najmniej o ¼ s (Podręcznik, „Rytm” 2)."""
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
                    sec = round(sec + GAG_CZAS.get(klucz, 0.0), 1)
                    if klucz in GAGI:
                        opis = f"{opis}. Gag: {GAGI[klucz]}"
                    for _ in range(3):
                        if prev is not None and abs(sec - prev) < 0.25:
                            sec = round(sec + 0.3, 1)
                    prev = sec
                    out.append((n, k, klucz, kadr, ruch, sec, opis, dzwiek))
    return [u for u in out if akt is None or u[0] == akt]


def ujecia_szkicu():
    """Ujęcia z długościami z tempa lektora (słowa / TEMPO_EN), bez nagrań. Akcję ujęć (sekundy w ujecia_a/b.py,
    efekty.ZDARZENIA, GAG_PUENTA) układano w tym rytmie, zanim powstał lektor; render.czas_akcji() przekłada ją na
    prawdziwe nagranie (23.11.2026: po nagraniu klonu ujęcia skróciły się nawet o 2,4 s i gagi wypadały za cięciem)."""
    BEZ_NAGRAN[0] = True
    try:
        return ujecia()
    finally:
        BEZ_NAGRAN[0] = False


if __name__ == "__main__":
    t = 0.0
    for n, tytul, _, _ in AKTY:
        us = ujecia(n)
        d = sum(u[5] for u in us)
        mowa = sum(okno_kwestii(u[7])[1] for u in us)
        print(f"Akt {n} · {tytul}: {len(us)} ujęć, {d:.1f} s, lektor {mowa / d:.0%}")
        t += d
    print(f"film: {int(t // 60)} min {t % 60:.0f} s ({t:.1f} s), {len(ujecia())} ujęć")
