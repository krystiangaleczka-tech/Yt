"""Szkice ujęć filmu „Bonnie and Clyde: The Outlaws Made of Paper” (EN, teatr papierowy): trzy różne scenariusze.

Reżyser 18.11.2026: „dawaj 15 [minut] i pamiętaj o tym, żeby mi dać 3 możliwości na fabule ujęć według 3 różnych
scenariuszy filmu, pamiętaj o hooku itp.” — ton lekko humorystyczny (ironia, suchy lektor; z ofiar nie żartujemy, od
zabójstw policjantów ton poważnieje), długość ok. 15 min. Otwarcie według przepisu reżysera (Wytyczne 1.26): 5 s
zapowiedzi → kurtyna startu z bohaterem → najazd z wprowadzeniem → hak (z ujęciem-pomostem) → obietnica → pomost do
aktu I; drugi hak ok. 3. minuty (najpierw pogorszenie, potem promyk nadziei); kurtyny aktów z pytaniem; na końcu
podziękowanie.

Warianty:
  A · Legenda z gazety — prasa kontra prawda, chronologicznie; papier (gazety, zdjęcia) jako rama.
  B · Pościg Hamera — 102 dni emerytowanego strażnika; akta z wycinkami i licznik dni, retrospekcje.
  C · Wiersz Bonnie — historia dziewczyny, która chciała być sławna; hak: wiersz przewidział koniec poza jednym.

Długość ujęcia z kwestii: oddech 0,6 s + słowa / 2,84 słowa/s (zmierzone tempo lektora EN „Syna słońca”) + pauza po
(1,1 / 1,4 / 1,8 / 2,3 s, Rytm 2); w haku szybciej (0,4 s oddechu, 1 s pauzy). Ujęcia bez słów mają czas wpisany.
Klatek jeszcze nie ma (nie ma dekoracji lat 30.) — w Studio każde ujęcie to karta z opisem i kwestią.

Uruchomienie:  python3 -I docs/filmy/bonnie-i-clyde/szkice/buduj_szkice.py [a b c]
Wynik:         szkice/<a|b|c>/szkic.json → Studio: Szkice ujęć → „Szkice w plikach…” → „Importuj z plików”.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

TU = Path(__file__).resolve().parent
FILM = "bonnie-i-clyde"
TYTUL_FILMU = "Bonnie and Clyde: The Outlaws Made of Paper"
TEMPO_EN = 2.84
PAUZA = {"ujecie": 1.1, "beat": 1.4, "scena": 1.8, "akt": 2.3}
KADR = {"TYT": "karta / napis", "PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie",
        "D": "detal"}
DZIEKI = "Thank you for watching! If you like my videos, support me, and I'll do my best."
SLOWNIE = {"1930": "nineteen thirty", "1932": "nineteen thirty-two", "1933": "nineteen thirty-three",
           "1934": "nineteen thirty-four", "1967": "nineteen sixty-seven", "2026": "twenty twenty-six"}

# ── wspólne ujęcia: klucz → (kadr, miejsce/dekoracja, opis wydarzenia) ─────────────────────────────────────────────
W = {
    "wagon": ("PŚ", "West Dallas", "Pod wiaduktem w West Dallas rodzina Barrowów śpi pod wozem konnym; mały Clyde "
              "wyczołguje się spod koła, przeciąga się i drapie po głowie"),
    "indyki": ("PP", "West Dallas", "Nastoletni Clyde i brat Buck pchają ciężarówkę pełną gdaczących indyków; zza rogu "
               "wychodzi policjant z gwizdkiem, indyki wyfruwają; tabliczka „STOP!”"),
    "szkola": ("PŚ", "Cement City (szkoła)", "Mała Bonnie wbiega na podium po dyplom za ortografię i wiersze; klasa "
               "klaszcze, z nitki zjeżdża złota gwiazdka"),
    "slub": ("PP", "Cement City (dom)", "Piętnastoletnia Bonnie i Roy Thornton stają pod łukiem z papierowych kwiatów; "
             "z góry zjeżdża tabliczka-tatuaż: dwa serca „Bonnie” i „Roy”; podpis „Roy Thornton”"),
    "roy": ("PŚ", "Cement City (dom)", "Roy wychodzi z walizką, drzwi skrzypią i zostają otwarte; Bonnie przy oknie "
            "obraca obrączkę na palcu; zjeżdża zawieszka „1929”"),
    "kawiarnia": ("PŚ", "kawiarnia w Dallas", "Bonnie w fartuszku nalewa kawę; klient za gazetą nie podnosi wzroku; "
                  "Bonnie przewraca oczami i odstawia dzbanek z hukiem"),
    "kuchnia": ("PP", "kuchnia przyjaciółki", "W ciasnej kuchni Bonnie miesza kakao; drzwiami wchodzi Clyde w kapeluszu "
                "i uchyla go; z nitki zjeżdżają dwa serduszka; podpis „Clyde Barrow”"),
    "areszt": ("PŚ", "kuchnia przyjaciółki", "Do kuchni wchodzi policjant i zakuwa Clyde'a w kajdanki; Bonnie zostaje "
               "z łyżką w ręce; tabliczka „HEY!”"),
    "waco": ("D", "areszt w Waco", "Przy kratach Bonnie wyjmuje spod płaszcza pistolet i podaje go przez pręty; strażnik "
             "w tle ziewa i patrzy w drugą stronę"),
    "ohio": ("PP", "peron w Ohio", "Clyde w nowym kapeluszu przechadza się po peronie i gwiżdże; z obu stron wchodzą "
             "policjanci; tabliczka „OH NO”"),
    "eastham": ("PO", "Eastham", "Za bramą farmy więziennej Eastham więźniowie w pasiakach tną bawełnę, każdy w swoim "
                "rytmie; strażnik na koniu jedzie wzdłuż rzędu; słońce praży"),
    "eastham_rura": ("PŚ", "Eastham (barak, teatr cieni)", "Za parawanem w baraku cień rosłego więźnia pochyla się nad "
                     "Clyde'em; Clyde chwyta rurę, cień przeciwnika pada; muzyka cichnie"),
    "palce": ("D", "Eastham", "Na polu cień siekiery opada poza kadrem; Clyde łapie się za but i podskakuje na jednej "
              "nodze; tabliczka „AW!”, gwiazdki nad głową"),
    "parol": ("PP", "Eastham (brama)", "Brama się otwiera; Clyde wychodzi o kulach; strażnik macha za nim kartką "
              "z pieczątką „PAROLE”; Clyde patrzy na bandaż na stopie"),
    "kaufman": ("PP", "Kaufman (noc)", "Nocą Ford grzęźnie w błocie po kołpaki; Clyde i Bonnie wskakują na dwa muły, "
                "muły ani drgną; tabliczka „GO!”"),
    "cela": ("PŚ", "areszt w Kaufman", "Bonnie w celi pisze ołówkiem w zeszycie; zapisane kartki odrywają się i fruwają "
             "po celi jak ptaki"),
    "hillsboro": ("PO", "Hillsboro (teatr cieni)", "Za papierowym parawanem cienie: napad w sklepie, błysk, sylwetka "
                  "sprzedawcy opada za ladę; muzyka cichnie"),
    "stacja": ("PP", "stacja benzynowa", "Clyde wpada do budki stacji z rewolwerem; kasjer otwiera szufladę: kilka "
               "monet i guzik; tabliczka „THAT'S IT?”"),
    "matka_obietnica": ("PP", "dom matki Bonnie", "Bonnie wychodzi z aresztu prosto w objęcia matki i kiwa głową; za "
                        "płotem stoi Ford, Clyde cicho trąbi"),
    "atoka": ("PO", "Atoka (teatr cieni)", "Potańcówka pod gołym niebem w Atoce, pary wirują; dwaj stróże prawa podchodzą "
              "do auta; za parawanem błyski, jedna sylwetka pada"),
    "wd": ("PŚ", "droga w Teksasie", "Do auta wsiada chudy chłopak z nieśmiałym uśmiechem i zatrzaskuje drzwi; podpis "
           "„W.D. Jones, 16”"),
    "buck": ("PP", "więzienie Huntsville (brama)", "Z bramy wychodzi Buck Barrow z ułaskawieniem w ręku; czeka Blanche "
             "w kapelusiku, z białym pieskiem na rękach; podpisy „Buck Barrow”, „Blanche Barrow”"),
    "joplin_dom": ("PO", "Joplin", "Dwa auta zajeżdżają pod garaż z mieszkaniem na piętrze; zjeżdża zawieszka „Joplin, "
                   "Missouri, 1933”; w oknach zapalają się światła"),
    "joplin_karty": ("PŚ", "Joplin (mieszkanie)", "Buck i Blanche grają w karty, Clyde dmucha w saksofon, Bonnie pisze; "
                     "sąsiadka przykłada ucho do ściany; tabliczka „SHHH!”"),
    "joplin_walka": ("PO", "Joplin (teatr cieni)", "Za parawanem błyski z okien, dwie sylwetki policjantów padają; gang "
                     "zbiega po schodach do auta i wyjeżdża przez drzwi garażu"),
    "joplin_rzeczy": ("D", "Joplin (mieszkanie)", "Policjant chodzi po opuszczonym pokoju: walizki, karabiny, zeszyt "
                      "z wierszem; podnosi z podłogi aparat, z kasety wysuwa się klisza"),
    "ciemnia": ("PŚ", "redakcja Joplin Globe", "W czerwonym świetle ciemni klisza pływa w kuwecie; na papierze wyłania "
                "się Bonnie z rewolwerem i cygarem"),
    "zdjecie": ("PŚ", "Joplin (pozowanie)", "Ożywa klatka z kliszy: Bonnie opiera nogę o zderzak Forda, ktoś zza kadru "
                "podaje jej cygaro, ona wkłada je do ust i pozuje z rewolwerem; błyska flesz"),
    "prasa": ("PO", "drukarnia", "Wałki maszyny drukarskiej kręcą się, wylatują setki gazet ze zdjęciem Bonnie "
              "z cygarem i odlatują nad dachy miasteczek"),
    "kiosk": ("PO", "ulica (kiosk)", "Gazeciarz macha gazetą; kolejka ludzi w łatanych płaszczach kupuje; sterta gazet "
              "rośnie aż do markizy; tabliczka „EXTRA!”"),
    "darby_auto": ("PP", "Ruston", "Gang odjeżdża cudzym autem sprzed domu; z domu wybiegają młody mężczyzna "
                   "w garniturze i kobieta w kapeluszu i wskakują do drugiego auta"),
    "darby_tyl": ("PŚ", "Ruston (auto gangu)", "Darby i Stone siedzą ściśnięci na tylnym siedzeniu; Bonnie odwraca się "
                  "do nich i pyta; podpisy „Dillard Darby, undertaker”, „Sophia Stone”"),
    "darby_smiech": ("Z", "Ruston (auto gangu)", "Bonnie wybucha śmiechem i klepie się po kolanie; Darby blednie; "
                     "tabliczka „HA HA!”"),
    "darby_puszczeni": ("PP", "droga w Arkansas", "Porwani wysiadają na poboczu; Clyde wręcza im przez okno banknot; "
                        "Ford odjeżdża w kurzu, Darby zostaje z banknotem w ręce"),
    "wellington_noc": ("PO", "Wellington (noc)", "Nocna droga przez prerię, Ford pędzi z zapalonymi światłami; tablica "
                       "„DETOUR” mija się w ciemności, nikt jej nie widzi"),
    "wellington_most": ("PO", "Wellington (wąwóz)", "Ford wjeżdża na rozebrany most, leci w wąwóz, przewraca się "
                        "i bucha płomieniem; mocny wstrząs kamery, przed uderzeniem muzyka milknie (szczyt 1)"),
    "wellington_bonnie": ("PŚ", "Wellington (wąwóz)", "Clyde i W.D. wyciągają Bonnie z płonącego auta; jej noga dymi; "
                          "tabliczka „AAAA!”"),
    "farma": ("PP", "farma pod Wellington", "Rodzina farmerów nosi wiadra i opatruje Bonnie na ganku; drogą nadjeżdżają "
              "szeryf i marszałek"),
    "drzewo": ("PP", "las w Oklahomie", "Szeryf i marszałek przywiązani drutem kolczastym do drzewa; Clyde macha im "
               "z auta na pożegnanie; tabliczka „BYE!”"),
    "noszenie": ("PŚ", "motel przy drodze", "Clyde niesie Bonnie na rękach z auta do pokoju motelu; noga w bandażu; "
                 "Bonnie krzywi się przy każdym jego kroku"),
    "oboz": ("PO", "obóz przy drodze", "Wieczór przy drodze: auto z otwartymi drzwiami, pranie suszy się na drzwiach, "
             "puszka fasoli na ognisku, Bonnie pisze, Clyde czyści karabin"),
    "rzeka": ("PŚ", "rzeka", "Bonnie myje włosy w rzece; ryba wyskakuje jej spod ręki; tabliczka „BRRR!”"),
    "platte": ("PO", "Platte City (teatr cieni)", "Policja otacza dwa domki motelu, podjeżdża opancerzone auto; za "
               "parawanem błyski, sylwetka Bucka chwieje się, szyba pęka przed Blanche"),
    "dexfield": ("PO", "Dexfield Park (świt)", "Świt w lesie w Iowie: z krzaków wychodzą farmerzy i policjanci; Buck "
                 "leży przy ognisku, Blanche klęczy przy nim i nie chce odejść"),
    "przeprawa": ("PP", "rzeka w Iowie", "Clyde, Bonnie i W.D. brną przez rzekę; Clyde ciągnie Bonnie za rękę; na "
                  "brzegu za nimi błyski"),
    "wd_odchodzi": ("PŚ", "droga (noc)", "Nocą W.D. wysiada po cichu i odchodzi w ciemność; Bonnie patrzy za nim przez "
                    "szybę"),
    "rodziny": ("PO", "droga pod Dallas (noc)", "Nocą przy polnej drodze stoją dwa auta z wygaszonymi światłami; matki "
                "podają przez okna koszyki z jedzeniem, Bonnie oddaje pranie"),
    "sowers": ("PO", "Sowers (teatr cieni)", "Nocą przy drodze z krzaków wyskakują policjanci; błyski za parawanem za "
               "wcześnie, Ford z przestrzelonymi szybami odjeżdża; tabliczka „OUCH!”"),
    "odbicie": ("PO", "Eastham (mgła)", "Mgła nad polami Eastham; więźniowie wyciągają broń z rowu, strażnik pada; "
                "z mgły trąbi klakson, wyjeżdża Ford, więźniowie wskakują na stopnie"),
    "simmons": ("PŚ", "biuro więziennictwa", "Szef więziennictwa wali pięścią w biurko, aż podskakuje kałamarz; podpis "
                "„Lee Simmons, Texas prisons chief”"),
    "hamer": ("PP", "ganek w Austin", "Na ganku wysoki mężczyzna w kapeluszu wstaje powoli z bujanego fotela i sięga "
              "po karabin; podpis „Frank Hamer, retired Texas Ranger”"),
    "mapa": ("PŚ", "biuro Hamera", "Hamer przypina do mapy papierowe znaczniki: Teksas, Oklahoma, Missouri, Luizjana; "
             "łączy je czerwoną nicią"),
    "petle": ("D", "biuro Hamera", "Czerwona nić na mapie układa się w pętle wzdłuż granic stanów; każda pętla wraca do "
              "Dallas, do dwóch małych domków"),
    "grapevine": ("PO", "Grapevine (Wielkanoc)", "Wiejska droga, kwitnące drzewa, Ford stoi na poboczu; nadjeżdżają "
                  "dwaj motocykliści w mundurach i zwalniają"),
    "grapevine_cien": ("PO", "Grapevine (teatr cieni)", "Muzyka milknie; za parawanem dwa błyski, dwie sylwetki "
                       "z motocyklami padają; motocykl przewraca się z łoskotem (szczyt 2)"),
    "tullis": ("PŚ", "cmentarz w Alto", "Przy trumnie stoi młoda kobieta w białej sukni ślubnej; z góry powoli spadają "
               "płatki; podpis „Maree Tullis”"),
    "gazety_zle": ("PO", "ulica (kiosk)", "Nowe gazety z nagłówkiem o bezlitosnej Bonnie; ludzie zgniatają je "
                   "i rzucają na ziemię; kolejka przy kiosku się rozchodzi"),
    "listy_gon": ("PP", "ulica (słup)", "Na słupie wyrastają kolejne listy gończe z nagrodą; farmer z dubeltówką "
                  "przystaje, czyta i odwraca się w stronę drogi"),
    "commerce": ("PP", "Commerce", "Ford ugrzązł w rowie pod Commerce w Oklahomie; dwaj stróże prawa idą przez pole, "
                 "żeby pomóc"),
    "commerce_cien": ("PO", "Commerce (teatr cieni)", "Za parawanem błysk, starszy konstabl pada; komendant podnosi "
                      "ręce i wsiada do Forda"),
    "boyd": ("PŚ", "Commerce (auto gangu)", "Komendant na tylnym siedzeniu z rękami w górze; Bonnie odwraca się do niego "
             "z uniesionym palcem; podpis „Percy Boyd, police chief”"),
    "boyd_tab": ("Z", "droga w Kansas", "Boyd stoi przy drodze i patrzy za odjeżdżającym Fordem; zjeżdża nad nim "
                 "tabliczka „SHE DOESN'T SMOKE CIGARS!”"),
    "prasa_cygaro": ("PO", "drukarnia", "Maszyna drukarska wypluwa gazety z nagłówkiem „BONNIE: NO CIGARS!”; jedna "
                     "gazeta ląduje na biurku Hamera obok mapy"),
    "methvin": ("PŚ", "chata w Luizjanie", "Hamer siedzi przy stole naprzeciw brodatego farmera; między nimi papier "
                "z pieczęcią „PARDON”; farmer kiwa głową; podpis „Ivy Methvin”"),
    "wiersz": ("PŚ", "dom matki Bonnie", "Bonnie wręcza matce zeszyt; matka czyta przy lampie, a za oknem czeka Ford "
               "z zapalonymi światłami"),
    "pozegnanie": ("PO", "Dallas (noc)", "Ford przejeżdża powoli obok dwóch domów; w oknach dwie matki machają; Ford "
                   "znika za zakrętem"),
    "zasadzka_rano": ("PO", "droga w Luizjanie (świt)", "Świt na leśnej drodze; ciężarówka Ivy'ego stoi na lewarku jak "
                      "z przebitą oponą; w krzakach sześć kapeluszy i luf"),
    "kanapka": ("Z", "droga w Luizjanie (Ford)", "Wnętrze Forda: Bonnie w czerwonej sukience je kanapkę z papierka; "
                "Clyde prowadzi w skarpetkach i ciemnych okularach"),
    "zwolnienie": ("PP", "droga w Luizjanie", "Ford zwalnia przy ciężarówce; Ivy macha z pobocza; Clyde opuszcza szybę "
                   "i wychyla się"),
    "zasadzka": ("PO", "droga w Luizjanie (teatr cieni)", "Muzyka milknie; za parawanem dziesiątki błysków jeden po "
                 "drugim, papierowy Ford drży i powoli zjeżdża do rowu; spada kapelusz; cisza (szczyt 3)"),
    "dym": ("PŚ", "droga w Luizjanie", "Dym opada; mężczyźni wychodzą z krzaków z bronią; jeden zdejmuje kapelusz; "
            "nikt nic nie mówi"),
    "pamiatki": ("PO", "Arcadia", "Tłum otacza podziurawionego Forda; ktoś odcina nożyczkami pukiel włosów, ktoś "
                 "kawałek sukienki; szeryf odgania ludzi"),
    "darby_zaklad": ("PŚ", "zakład pogrzebowy w Arcadii", "W zakładzie pogrzebowym młody mężczyzna w fartuchu zakłada "
                     "rękawice; z nitki zjeżdża jego stary podpis „Dillard Darby, undertaker”"),
    "pogrzeby": ("PO", "dwa cmentarze w Dallas", "Dwa osobne pogrzeby na dwóch cmentarzach, między nimi droga; tłumy "
                 "przy obu; matka Bonnie odwraca się plecami do cmentarza Clyde'a"),
    "legenda": ("PO", "kino", "Gazety składają się w ekran kina; na ekranie piękna para w kapeluszach z filmu z 1967 "
                "roku; widownia wzdycha, ktoś ociera łzę"),
    "dzieki": ("PŚ", "teatr (kurtyna)", "Przed kurtyną wychodzą wszystkie lalki filmu i kłaniają się po kolei; Hamer "
               "zdejmuje kapelusz, Bonnie macha"),
    "pamietnik": ("D", "Cement City (dom)", "Bonnie pisze w pamiętniku przy oknie i ziewa; za oknem pusta ulica, "
                  "przelatuje jedna mucha; tabliczka „BORED”"),
    "hamer_motel": ("PŚ", "motel przy drodze", "Hamer pokazuje recepcjoniście zdjęcie Bonnie; recepcjonista kiwa głową "
                    "i wskazuje drogę; na ladzie stos pustych puszek po fasoli"),
    "straznik": ("PŚ", "Eastham (mgła)", "Mgła rzednie; na drodze zostaje kapelusz strażnika; z nitki zjeżdża podpis "
                 "„Major Joe Crowson”; światło przygasa"),
    "shreveport": ("PP", "Shreveport", "Przed kawiarnią w Shreveport chłopak wysiada z Forda i znika w tłumie; podpis "
                   "„Henry Methvin”; Ford czeka chwilę i odjeżdża bez niego"),
    "posse": ("PŚ", "droga w Luizjanie (noc)", "W krzakach sześciu mężczyzn; nad każdym po kolei zjeżdża podpis: Hamer, "
              "Gault, Alcorn, Hinton, Jordan, Oakley; Hinton przeciera okulary"),
    "auto_jarmark": ("PO", "jarmark", "Na jarmarku pod namiotem stoi podziurawiony Ford; kolejka ludzi płaci za wejście "
                     "i zagląda w dziury po kulach; nad namiotem kręci się karuzela"),
    "blanche_po": ("PŚ", "dom Blanche", "Starsza Blanche w okularach z jednym ciemnym szkłem podlewa kwiaty przed "
                   "domkiem; zjeżdża zawieszka „1988”"),
    "suicide_druk": ("PO", "drukarnia", "Z maszyny wychodzą gazety z wierszem Bonnie zamiast zdjęcia; wersy wiszą na "
                     "paskach papieru jak pranie"),
    "joplin_ofiary": ("PŚ", "Joplin", "Na pustym podwórku leżą dwie czapki policyjne; z nitek zjeżdżają podpisy "
                      "„Harry McGinnis”, „Wes Harryman”; światło przygasa"),
    "ksiazka": ("PŚ", "dom matki Bonnie", "Matka Bonnie kładzie na stole świeżo wydrukowaną książkę; z kartek wysuwają "
                "się paski z wersami córki i kołyszą się nad stołem"),
    "naglowki": ("PP", "ulica (kiosk)", "Na kiosku wyrastają kolejne nagłówki: „BRAINS OF THE GANG”, „CRACK SHOT”, "
                 "„CIGAR!”; Bonnie w kapeluszu z woalką czyta je z boku i marszczy nos"),
}

# Czas na akcję ponad kwestię (Wytyczne 1.8, 1.18; w „Pierwszym cesarzu” reżyser wydłużał budowę, tłum, wojsko
# i podróż o 2–3 s): dekoracja, która stawia się na początku sceny, tłum, pościg, przemarsz.
WYDLUZ = {
    "wagon": 1.5, "eastham": 2.0, "kaufman": 1.5, "hillsboro": 1.0, "stacja": 1.0, "atoka": 1.0, "buck": 1.0,
    "joplin_dom": 1.5, "joplin_walka": 1.5, "prasa": 2.0, "kiosk": 2.0, "suicide_druk": 1.0, "naglowki": 1.0,
    "darby_auto": 1.0, "wellington_noc": 1.0, "farma": 1.0, "drzewo": 1.0, "oboz": 1.5, "platte": 1.5,
    "dexfield": 1.5, "przeprawa": 1.0, "rodziny": 1.5, "sowers": 1.0, "odbicie": 2.0, "mapa": 1.5, "petle": 2.0,
    "grapevine": 1.5, "listy_gon": 1.5, "commerce": 1.0, "prasa_cygaro": 1.5, "zasadzka_rano": 1.5,
    "pamiatki": 2.5, "pogrzeby": 2.0, "auto_jarmark": 1.5, "legenda": 1.5, "posse": 1.0,
}


def slowa(line: str) -> int:
    for k, v in SLOWNIE.items():
        line = line.replace(k, v)
    return len(line.split())


def czas(line: str, pauza: str = "ujecie", hak: bool = False, dodaj: float = 0.0) -> float:
    oddech, po = (0.4, 1.0) if hak else (0.6, PAUZA[pauza])
    return round(oddech + slowa(line) / TEMPO_EN + po + dodaj, 1)


def U(klucz, kadr, miejsce, opis, kwestia="", mark="", pauza="ujecie", dodaj=0.0, sek=None, hak=False):
    """Ujęcie: opis po polsku (wydarzenie), kwestia lektora EN; bez kwestii — czas `sek`."""
    if kwestia:
        s = czas(kwestia, pauza, hak, dodaj)
    else:
        s = sek if sek is not None else 2.0
    return {"klucz": klucz, "kadr": kadr, "miejsce": miejsce, "opis": opis, "kwestia": kwestia, "mark": mark,
            "sekundy": round(s, 1), "dodaj": dodaj, "hak": hak, "pauza": pauza}


def S(klucz, kwestia="", **kw):
    """Ujęcie ze wspólnej puli W (opis i dekoracja wspólne dla wariantów)."""
    kadr, miejsce, opis = W[klucz]
    opis = kw.pop("opis", opis)
    if kwestia:
        kw["dodaj"] = kw.get("dodaj", 0.0) + WYDLUZ.get(klucz, 0.0)
    return U(klucz, kw.pop("kadr", kadr), kw.pop("miejsce", miejsce), opis, kwestia, **kw)


def Z(klucz, sek, opis, mark=""):
    """Skrót do zapowiedzi (5 s): dzieje się tam, gdzie oryginał."""
    kadr, miejsce, _ = W.get(klucz, ("PŚ", "teatr", ""))
    return U("zap_" + klucz, kadr, miejsce, f"zapowiedź (skrót ujęcia „{klucz}”): {opis}", mark=mark, sek=sek)


# ═══ WARIANT A · LEGENDA Z GAZETY ══════════════════════════════════════════════════════════════════════════════════
A_POMYSL = (
    "Prasa kontra prawda, po kolei od slumsów West Dallas do zasadzki. Scena teatru jest zbudowana z gazet: nagłówki "
    "zjeżdżają na nitkach, a potem papierowe lalki pokazują, co było naprawdę. Hak 1: żart z cygarem, który trafił na "
    "pierwsze strony. Pogorszenie: Eastham (pierwsze zabójstwo, obcięte palce), promyk nadziei i hak 2: zwolnienie "
    "sześć dni później i przysięga, że nigdy nie wróci. Humor: indyki, muły, sznur sąsiadów w Joplin, przedsiębiorca "
    "pogrzebowy, wąwóz w Wellington, wiadomość o cygarach. Od Grapevine ton poważny; finał: pamiątkarze, Darby przy "
    "ich ciałach, osobne groby, Hollywood i gra wideo sprzedają tę samą legendę.")
A = [
    Z("wellington_most", 0.9, "Ford spada z rozebranego mostu w wąwóz, bucha płomień", mark="ZAPOWIEDŹ 5 s"),
    Z("zdjecie", 0.6, "Bonnie z cygarem i rewolwerem pozuje przy Fordzie, błyska flesz"),
    Z("prasa", 0.8, "wałki drukarni kręcą się, wylatują gazety ze zdjęciem"),
    Z("boyd", 0.7, "porwany komendant z rękami w górze, Bonnie grozi mu palcem"),
    Z("hamer", 0.6, "Hamer wstaje z bujanego fotela i sięga po karabin"),
    Z("pamiatki", 1.5, "tłum przy podziurawionym Fordzie, ktoś odcina pukiel włosów; ściemnienie"),
    U("tytul", "TYT", "teatr z gazet", "Kurtyna startu rozsuwa się na teatr zbudowany z gazet: stoi Ford, Bonnie opiera "
      "nogę o zderzak z cygarem w zębach i rewolwerem, obok Clyde z karabinem; z góry zjeżdża szyld „The Outlaws Made of "
      "Paper”", mark="TYTUŁ · kurtyna startu", sek=4.6),
    U("wprowadzenie", "PŚ", "teatr z gazet", "Kamera najeżdża na Bonnie; przy jej imieniu zjeżdża podpis „Bonnie "
      "Parker”; Bonnie wyjmuje cygaro z ust i krzywi się",
      "This is Bonnie Parker, the most famous outlaw girl in America, and almost everything you think you know about "
      "her was printed in a newspaper.", mark="WPROWADZENIE"),
    U("wprowadzenie2", "PP", "teatr z gazet", "Kamera odjeżdża na Clyde'a; podpis „Clyde Barrow”; za nimi z nitek "
      "zjeżdżają nagłówki gazet jeden za drugim",
      "Together with Clyde Barrow, she spent two years robbing gas stations and corner shops, while the papers turned "
      "two broke kids from Dallas into legends.", pauza="beat"),
    S("joplin_rzeczy", "In April 1933, police raided their hideout in Joplin, Missouri, and found the one thing outlaws "
      "should never leave behind: a camera full of film.", mark="HOOK 1", hak=True),
    S("zdjecie", "On one frame, Bonnie posed with a pistol and a borrowed cigar, just for fun.", hak=True),
    U("hak_pomost", "D", "teatr z gazet", "Pomost: wielka strona gazety przewraca się przez cały kadr jak kurtyna, szelest "
      "papieru", sek=1.6),
    S("prasa", "Within days that joke was on front pages across America, and Bonnie became the cigar-smoking gun girl.",
      hak=True),
    U("hak_cygaro", "Z", "kryjówka (auto)", "Bonnie w aucie czyta gazetę ze swoim zdjęciem, wypuszcza z ust papierosa "
      "i zgniata gazetę; tabliczka „I DON'T SMOKE CIGARS!”",
      "There was just one problem: Bonnie didn't smoke cigars, and she spent the rest of her short life trying to tell "
      "everyone.", hak=True),
    U("obietnica", "PO", "teatr z gazet", "Gazety układają się w mapę pięciu stanów; po mapie sunie papierowy Ford "
      "i zostawia za sobą ślad z nagłówków",
      "By the end, you'll know how two small-time thieves became the most hunted couple in America, who finally caught "
      "them, and why their legend still sells today.", mark="OBIETNICA", pauza="beat"),
    S("wagon", "To see how a joke became a legend, we go back to West Dallas in the 1920s, a slum so poor that people "
      "called it the Devil's Back Porch.", mark="AKT I · POMOST",
      opis="Kurtyna z tytułem „Act I · Who were they before the headlines?”; rozsuwa się, z ziemi wyrastają namioty "
      "i szałasy pod wiaduktem; rodzina Barrowów śpi pod wozem konnym"),
    S("indyki", "Clyde Barrow's family had arrived with almost nothing, and as a teenager Clyde was arrested for a "
      "rented car he forgot to return, and then for a truck full of stolen turkeys."),
    S("szkola", "Bonnie Parker, meanwhile, was a star pupil who won prizes for spelling and poetry, and she dreamed of the "
      "stage."),
    S("slub", "At fifteen she married a boy named Roy Thornton and had their names tattooed in two hearts, which is a "
      "very permanent decision for a fifteen-year-old."),
    S("roy", "Roy kept disappearing and soon landed in prison, but Bonnie never divorced him and wore his ring until "
      "the very end."),
    S("kawiarnia", "So at nineteen she was a waitress with a husband in prison, waiting for something exciting to "
      "happen.", pauza="beat"),
    S("kuchnia", "In January 1930, in a friend's kitchen, she met Clyde, and from then on something exciting happened "
      "almost every week."),
    S("areszt", "Unfortunately, a few weeks later the police arrested him for a string of burglaries."),
    S("waco", "Bonnie smuggled a pistol into the Waco jail, and soon after, Clyde broke out."),
    S("ohio", "He was caught again a week later in Ohio, which tells you a lot about his talent for escapes.",
      pauza="beat"),
    S("eastham", "This time he was sent to Eastham Prison Farm, one of the harshest prisons in Texas, where men picked "
      "cotton from dawn to dark.", mark="POGORSZENIE"),
    S("eastham_rura", "There another inmate attacked him again and again, until Clyde killed him with a pipe, and it "
      "was the first life he took."),
    S("palce", "Desperate to get out of the fields, he had two of his toes cut off with an axe."),
    S("parol", "Six days later he was released on parole anyway, thanks to a petition from his mother, so the toes "
      "were a waste.", mark="HOOK 2 · promyk nadziei", pauza="beat"),
    U("przysiega", "Z", "Eastham (brama)", "Clyde o kulach odwraca się do bramy, która zamyka się za nim z hukiem; "
      "tabliczka „NEVER AGAIN”",
      "He limped for the rest of his life, and he swore he would die before going back, but how do you stay free when "
      "every policeman in Texas knows your face?", pauza="akt"),
    U("akt2", "PO", "droga w Teksasie", "Kurtyna „Act II · How do you become America's most wanted?”; rozsuwa się na "
      "drogę wśród pól; z ziemi wyrasta stacja benzynowa z jednym dystrybutorem",
      "Clyde's plan was simple: steal a fast car, rob small places with little cash and no guards, and keep driving.",
      mark="AKT II", dodaj=1.0),
    S("stacja", "Most of their robberies were gas stations and grocery stores, and many of them paid only a few "
      "dollars."),
    S("kaufman", "Their first big plan was to rob a hardware store for guns, but the car got stuck in the mud, so they "
      "tried to escape on stolen mules."),
    S("cela", "Bonnie was caught and spent two months in jail, where she wrote a long poem about an outlaw girl called "
      "Suicide Sal."),
    S("hillsboro", "While she was locked up, one of Clyde's robberies went wrong in Hillsboro, and a shopkeeper named "
      "John Bucher was shot dead.", pauza="beat"),
    S("matka_obietnica", "When the grand jury let Bonnie go, she promised her mother to stay away from Clyde, and she "
      "kept that promise for a few weeks."),
    S("atoka", "That August, at a country dance in Oklahoma, Clyde's gang shot a deputy named Eugene Moore, and now "
      "they were wanted for killing a lawman."),
    S("wd", "Soon a sixteen-year-old kid from the neighborhood, W.D. Jones, joined them, mostly because it sounded "
      "exciting."),
    S("buck", "Then in March 1933, Clyde's older brother Buck was pardoned, and he and his wife Blanche came along for "
      "what was supposed to be a short family visit."),
    S("joplin_dom", "They rented an apartment above a garage in Joplin, Missouri, where the five of them tried very hard "
      "to look like a normal family."),
    S("joplin_karty", "They played cards, drank and argued so loudly that the neighbors called the police, thinking "
      "they were bootleggers, so who was really waiting behind that door?", pauza="akt"),
    S("joplin_walka", "On April 13, 1933, two officers walked up to the garage, and the gang answered with gunfire "
      "from the windows.", mark="AKT III",
      opis="Kurtyna „Act III · How did a joke make them famous?”; rozsuwa się na garaż w Joplin; za parawanem błyski "
      "z okien, dwie sylwetki policjantów padają, gang zbiega do auta i wyjeżdża przez drzwi garażu"),
    U("joplin_ofiary", "PŚ", "Joplin", "Na pustym podwórku leżą dwie czapki policyjne; z nitek zjeżdżają podpisy "
      "„Harry McGinnis”, „Wes Harryman”; światło przygasa",
      "Detective Harry McGinnis and Constable Wes Harryman were killed, and the gang fled in such a hurry that they "
      "left almost everything behind."),
    S("joplin_rzeczy", "Remember that camera? It was lying on the floor, next to their guns, their clothes and one of "
      "Bonnie's poems."),
    S("ciemnia", "The Joplin Globe developed the film, and suddenly a country deep in the Great Depression had "
      "pictures of its new favorite villains."),
    S("kiosk", "People who had lost their jobs and farms to the banks bought every edition, because these two looked "
      "like they were having a much better time."),
    U("cygaro_zlosc", "Z", "kryjówka (auto)", "Bonnie w aucie czyta gazetę, marszczy brwi i wyrzuca cygaro przez okno; "
      "tabliczka „CIGARETTES!”",
      "Bonnie loved the attention, but she hated being called a cigar smoker, because she only ever smoked cigarettes."),
    S("darby_auto", "Two weeks later in Louisiana they stole a car, and its owner, a young man named Dillard Darby, "
      "chased them with a friend, Sophia Stone."),
    S("darby_tyl", "The gang caught them instead and took them along, and when Bonnie asked Darby what he did for a "
      "living, he said he was an undertaker."),
    S("darby_smiech", "Bonnie reportedly laughed and said that one day he might have to work on her."),
    S("darby_puszczeni", "Later they let both hostages go near Waldo, Arkansas, and even gave them five dollars to get "
      "home.", pauza="beat"),
    U("plakaty", "PO", "mapa z gazet", "Mapa z gazet: pinezki w Teksasie, Oklahomie, Missouri, Luizjanie; na mapie "
      "wyrastają ich twarze z listów gończych",
      "Now their faces were on wanted posters in five states, but what happens when America's most famous getaway "
      "driver misses a road sign?", pauza="akt", dodaj=1.0),
    S("wellington_noc", "In June 1933, near Wellington, Texas, Clyde was driving fast at night and missed the signs "
      "warning that the bridge ahead was out.", mark="AKT IV",
      opis="Kurtyna „Act IV · What does life on the run really look like?”; nocna droga przez prerię, Ford pędzi; "
      "tablica „DETOUR” mija się w ciemności"),
    S("wellington_most", sek=3.4),
    S("wellington_bonnie", "The car caught fire, and acid from the battery burned Bonnie's leg so badly that she never "
      "walked properly again."),
    S("farma", "A farm family took them in and tried to help, but somebody called the sheriff, and two lawmen arrived."),
    S("drzewo", "The gang took both lawmen hostage, drove them across the border into Oklahoma and left them tied to a "
      "tree with barbed wire."),
    S("noszenie", "For weeks afterwards Clyde carried Bonnie in his arms, because she could no longer stand on her own."),
    S("oboz", "This was the glamorous outlaw life: sleeping in stolen cars, eating cold beans from cans and washing in "
      "rivers."),
    S("rzeka", sek=2.3),
    S("platte", "In July, police surrounded them at a motel in Missouri; Buck was shot in the head, and flying glass "
      "blinded Blanche in one eye.", pauza="beat"),
    S("dexfield", "Days later, in an Iowa park, a posse of police and farmers found their camp, and Buck was captured, "
      "dying, while Blanche refused to leave him."),
    S("przeprawa", "Clyde, Bonnie and W.D. waded across a river and escaped, wounded, with almost nothing left."),
    S("wd_odchodzi", "Soon even W.D. Jones slipped away in the night and went home to his mother."),
    S("rodziny", "Bonnie and Clyde went home too, in their own way: every few weeks they met their families on dark "
      "country roads outside Dallas, bringing laundry and taking home-cooked food."),
    S("sowers", "In November, the Dallas sheriff tried to ambush one of these family picnics, and both of them escaped "
      "with bullets in their legs, so why didn't they just stop?", pauza="akt"),
    S("odbicie", "Instead, in January 1934, Clyde went back to Eastham to free his friends, while Bonnie honked the "
      "horn in the fog to guide them.", mark="AKT V",
      opis="Kurtyna „Act V · Who finally went after them?”; mgła nad polami Eastham; więźniowie wyciągają broń z rowu, "
      "strażnik pada; z mgły trąbi klakson, wyjeżdża Ford, więźniowie wskakują na stopnie"),
    S("straznik", "Five prisoners got away, but a guard named Joe Crowson was shot and later died."),
    S("simmons", "The head of the Texas prisons, Lee Simmons, took it personally, and he went looking for one "
      "particular man."),
    S("hamer", "Frank Hamer was a retired Texas Ranger who had survived dozens of gunfights, and in February 1934 he "
      "quietly took the job."),
    S("mapa", "Hamer didn't chase them, because everyone who chased them lost; instead, he studied every place they "
      "had been."),
    S("petle", "He noticed that Clyde drove in great loops along state lines, where most police could not follow, and "
      "that sooner or later they always came home to their mothers.", pauza="akt"),
    S("grapevine", "On Easter Sunday 1934, near Grapevine, Texas, two young highway patrolmen on motorcycles stopped "
      "to help what they thought was a stranded car.", mark="AKT VI",
      opis="Kurtyna „Act VI · When did America stop cheering?”; wiejska droga, kwitnące drzewa, Ford stoi na poboczu; "
      "nadjeżdżają dwaj motocykliści i zwalniają"),
    S("grapevine_cien", "They were shot before they could draw their guns.", pauza="beat", dodaj=1.2),
    S("tullis", "One of them, H.D. Murphy, was supposed to marry his sweetheart, Maree Tullis, that month, and local "
      "historians say she came to his funeral in her wedding dress.", pauza="beat"),
    S("gazety_zle", "The papers claimed Bonnie had laughed over a dying man, which was probably not true, but after "
      "Grapevine nobody was cheering for them anymore."),
    S("listy_gon", "Rewards were posted across the South, and from then on every farmer with a shotgun was watching "
      "the road for a stolen Ford."),
    S("commerce", "Five days later, near Commerce, Oklahoma, their car slid into a ditch again, and two lawmen walked "
      "over to help."),
    S("commerce_cien", "Clyde killed Constable Cal Campbell and took the police chief, Percy Boyd, as a hostage."),
    S("boyd", "They drove Boyd around for hours, and before letting him go in Kansas, Bonnie gave him one message for "
      "the newspapers."),
    S("boyd_tab", "Not that she was innocent, and not that she was sorry, only that Bonnie Parker did not smoke cigars.",
      pauza="beat"),
    S("methvin", "Meanwhile, Hamer made a deal with Ivy Methvin, whose son they had freed at Eastham: help set a trap, "
      "and your boy walks free, so how much longer could they keep driving?", pauza="akt"),
    S("wiersz", "In May 1934, Bonnie gave her mother a new poem, which said that one day she and Clyde would go down "
      "together and be buried side by side.", mark="AKT VII",
      opis="Kurtyna „Act VII · How does the story end?”; dom matki Bonnie; Bonnie wręcza matce zeszyt, matka czyta przy "
      "lampie, za oknem czeka Ford"),
    S("pozegnanie", "Then they drove on, because a car was the only home they had left.", pauza="beat"),
    S("zasadzka_rano", "On the morning of May 23, six lawmen hid beside a country road in Louisiana, next to Ivy "
      "Methvin's truck, which stood on a jack as bait."),
    S("kanapka", "Clyde was driving in his socks, and Bonnie was eating a sandwich from a café in town."),
    S("zwolnienie", sek=2.2),
    S("zasadzka", sek=4.8),
    S("dym", "The lawmen fired more than a hundred rounds in a few seconds, and it was over before Clyde could reach "
      "for a gun.", pauza="scena"),
    S("pamiatki", "Within hours thousands of people crowded into the little town of Arcadia, and souvenir hunters cut "
      "locks of Bonnie's hair and pieces of her dress."),
    S("darby_zaklad", "And according to local accounts, the undertaker Bonnie had laughed at a year earlier helped "
      "prepare her body."),
    S("pogrzeby", "Her poem got almost everything right except the last line: her mother refused to let them share a "
      "grave, so they were buried in different cemeteries.", pauza="beat"),
    S("auto_jarmark", "Even their bullet-riddled car went on tour, and people paid to look at it at fairs across the "
      "country."),
    S("blanche_po", "Blanche served six years in prison and lived quietly until 1988, the only one of the four who "
      "grew old.", pauza="beat"),
    S("legenda", "Thirty years later a Hollywood film made them young and beautiful again, and in 2026 a new video "
      "game built its heroes on the same romance."),
    U("koniec", "PŚ", "teatr z gazet", "Papierowa Bonnie z cygarem i Clyde kładą się płasko w stronę gazety; gazeta "
      "zamyka się; kurtyna zasuwa się",
      "But the real Bonnie and Clyde were two broke kids from Dallas who left at least nine dead lawmen behind them, "
      "and most of what made them legends was printed on paper.", pauza="akt"),
    S("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
]

# ═══ WARIANT B · POŚCIG HAMERA ═════════════════════════════════════════════════════════════════════════════════════
B_POMYSL = (
    "Thriller od strony łowcy: 10 lutego 1934 Teksas wynajmuje emerytowanego strażnika Franka Hamera, a ten przestaje "
    "gonić i zaczyna czytać. Ramą jest gruba teczka z wycinkami (papier!), z której wysuwają się retrospekcje, "
    "a akty liczą dni pościgu na zawieszkach: DAY 1, DAY 20, DAY 50 (Wielkanoc w Grapevine wypada dokładnie 50. dnia), "
    "DAY 102 (zasadzka). Hak 1: po dwóch latach pościgów, które kończyły się w rowie, Hamer przestaje gonić. Pogorszenie: "
    "Eastham w aktach; hak 2: Hamer podkreśla jedno zdanie — Clyde się nie podda. Humor: radiowozy w rowach, muły, "
    "indyki, list do Forda, sznur sąsiadów; od Grapevine poważnie. Finał: Hollywood w 1967 roku robi z Hamera "
    "pośmiewisko — człowiek, który złapał ich czytając papier, przegrywa z papierem.")
B = [
    U("zap_karabin", "Z", "biuro Hamera", "zapowiedź: Hamer zatrzaskuje zamek karabinu", mark="ZAPOWIEDŹ 5 s", sek=0.8),
    Z("odbicie", 0.7, "z mgły wyjeżdża Ford, więźniowie wskakują na stopnie"),
    Z("wellington_most", 0.8, "Ford spada z mostu w wąwóz, bucha płomień"),
    Z("zdjecie", 0.6, "Bonnie z cygarem pozuje, błyska flesz"),
    Z("petle", 0.7, "czerwona nić na mapie układa się w pętlę"),
    Z("zasadzka", 1.5, "dziesiątki błysków za parawanem; ściemnienie"),
    U("tytul", "TYT", "teatr (biuro Hamera)", "Kurtyna startu rozsuwa się: na scenie biurko zawalone teczkami i mapa "
      "na ścianie; przy biurku siedzi Hamer w kapeluszu; z góry zjeżdża szyld „The Outlaws Made of Paper”",
      mark="TYTUŁ · kurtyna startu", sek=4.6),
    U("wprowadzenie", "PŚ", "teatr (biuro Hamera)", "Kamera najeżdża na Hamera; przy jego imieniu zjeżdża podpis „Frank "
      "Hamer, retired Texas Ranger”; Hamer unosi wzrok znad gazety ze zdjęciem Bonnie i Clyde'a",
      "In February 1934, Texas hired a retired Ranger named Frank Hamer to find Bonnie and Clyde, the most wanted "
      "couple in America.", mark="WPROWADZENIE"),
    U("poscigi", "PO", "droga w Teksasie", "Radiowóz goni Forda po zakrętach; Ford znika za wzgórzem, radiowóz wylatuje "
      "z zakrętu i ląduje w rowie kołami do góry; tabliczka „AGAIN?!”",
      "Police in five states had been chasing them for two years, and those chases usually ended the same way, with "
      "the police car in a ditch.", pauza="beat"),
    U("hak_szuflada", "PŚ", "teatr (biuro Hamera)", "Hamer zdejmuje z biurka zabawkowy radiowóz i chowa go do "
      "szuflady; tabliczka „NO MORE CHASING”",
      "So Hamer did something nobody expected: he stopped chasing them.", mark="HOOK 1", hak=True),
    U("hak_pomost", "D", "teatr (biuro Hamera)", "Pomost: na biurko spada gruba teczka z wycinkami, podnosi się kurz",
      sek=1.6),
    U("hak_teczka", "PŚ", "teatr (biuro Hamera)", "Hamer otwiera teczkę; wycinki wyfruwają i same przypinają się do "
      "mapy; Hamer stawia kubek kawy i siada wygodnie",
      "Instead, he sat down with their file and a map, and he waited for them to make one mistake.", hak=True),
    U("obietnica", "PO", "mapa", "Kamera odjeżdża: mapa pięciu stanów; po mapie sunie papierowy Ford i ciągnie za sobą "
      "czerwoną nić",
      "By the end, you'll know what that mistake was, how a parked truck and a sandwich ended the story, and why "
      "Hollywood later turned Hamer into a joke.", mark="OBIETNICA", pauza="beat"),
    S("wagon", "To understand them, Hamer started at page one: West Dallas, a slum so poor that people called it the "
      "Devil's Back Porch.", mark="AKT I · POMOST",
      opis="Kurtyna „Act I · Who were they before the file?”; teczka otwiera się jak kurtyna na namioty i szałasy pod "
      "wiaduktem; rodzina Barrowów śpi pod wozem konnym"),
    S("indyki", "Clyde Barrow grew up there, and his police record started early, with a rented car he forgot to "
      "return and a truck full of stolen turkeys."),
    S("szkola", "Bonnie Parker's record started much better, with prizes for spelling and poetry and a dream of the "
      "stage."),
    S("slub", "At fifteen she married Roy Thornton and had their names tattooed in two hearts, which a careful man "
      "like Hamer would file under distinguishing marks."),
    S("roy", "Roy soon vanished into prison, but Bonnie never divorced him and kept wearing his ring."),
    S("kawiarnia", "By nineteen she was a waitress in Dallas with a husband in prison, and nothing in her file looked "
      "dangerous yet.", pauza="beat"),
    S("kuchnia", "In January 1930, she met Clyde in a friend's kitchen, and from that day the file got much thicker."),
    S("areszt", "A few weeks later the police arrested him for a string of burglaries."),
    S("waco", "When Clyde was jailed in Waco, Bonnie smuggled him a pistol, and soon after, he broke out."),
    S("ohio", "A week later he was caught again in Ohio, which is the kind of detail a patient man remembers.",
      pauza="beat"),
    S("eastham", "Then Clyde was sent to Eastham Prison Farm, where convicts picked cotton from dawn to dark under "
      "armed guards.", mark="POGORSZENIE"),
    S("eastham_rura", "There another inmate attacked him again and again, until Clyde killed him with a pipe, and it "
      "was the first life he took."),
    S("palce", "Desperate to get out of the fields, he had two of his toes chopped off with an axe, and six days "
      "later he was paroled anyway."),
    U("podkreslenie", "D", "biuro Hamera", "Hamer podkreśla w aktach jedno zdanie czerwonym ołówkiem, dwa razy; z nitki "
      "zjeżdża tabliczka „HE WON'T GO BACK”",
      "Hamer underlined one line twice: Clyde had sworn he would die before going back, so there would never be a "
      "surrender, only the question of where.", mark="HOOK 2 · promyk nadziei", pauza="akt"),
    U("dzien1", "PO", "droga w Teksasie", "Kurtyna „Act II · Day 1: where do you start looking for a ghost?”; zjeżdża "
      "zawieszka „DAY 1”; Hamer jedzie starym autem przez prerię z mapą na kolanach",
      "On day one, Hamer started driving, not after them, but through every town where they had already been.",
      mark="AKT II", dodaj=1.0),
    S("kaufman", "The file said their first big plan, robbing a hardware store for guns, ended with the car stuck in "
      "the mud and the two of them on stolen mules that refused to move."),
    S("cela", "Bonnie was caught and spent two months in jail, writing a long poem about an outlaw girl called Suicide "
      "Sal."),
    S("matka_obietnica", "When she got out, she promised her mother to stay away from Clyde, and the file shows how "
      "long that lasted: a few weeks."),
    S("hillsboro", "Meanwhile, one of Clyde's robberies went wrong in Hillsboro, a shopkeeper named John Bucher was "
      "shot dead, and the file stopped being funny.", pauza="beat"),
    S("stacja", "Most of their robberies were gas stations and grocery stores, and some of them paid only a few "
      "dollars."),
    S("atoka", "That August, Clyde's gang killed a deputy at a country dance in Oklahoma, and from then on every lawman "
      "in the South had a personal reason to find them."),
    S("wd", "Soon a sixteen-year-old neighbor, W.D. Jones, joined them, mostly because it sounded exciting."),
    S("buck", "Then Clyde's brother Buck, just pardoned, came along with his wife Blanche and her little white dog."),
    S("joplin_dom", "In Joplin, Missouri, the five of them rented an apartment over a garage and tried very hard to "
      "look like a normal family."),
    S("joplin_karty", "They played cards and argued so loudly that the neighbors called the police, thinking they were "
      "bootleggers.", pauza="beat"),
    S("joplin_walka", "When two officers came to check, the gang opened fire, both lawmen were killed, and the gang "
      "fled so fast that they left a camera behind."),
    S("zdjecie", "On the film was Bonnie, posing with a pistol and a borrowed cigar as a joke."),
    S("ciemnia", "The local paper, the Joplin Globe, developed the film and printed the pictures."),
    S("prasa", "Soon the photos were printed everywhere, and now Hamer could hold the most famous faces in America in "
      "his hand."),
    S("kiosk", "People who had lost everything in the Depression bought every edition, because these two seemed to be "
      "having fun."),
    S("darby_auto", "Two weeks later in Louisiana they stole a car from a young man named Dillard Darby, who chased "
      "them with a friend, Sophia Stone."),
    S("darby_tyl", "The gang caught them both and took them along, and Darby turned out to be an undertaker."),
    S("darby_smiech", "When Bonnie heard that, she reportedly laughed and said he might have to work on her someday."),
    S("darby_puszczeni", "They let him go with five dollars for the trip home, and Hamer filed it under a strange sense "
      "of humor, but if everyone knew their faces, why could nobody catch them?", pauza="akt"),
    U("dzien20", "PO", "granica stanów", "Kurtyna „Act III · Day 20: why can't anyone catch them?”; zawieszka „DAY "
      "20”; na drodze tablica „STATE LINE”; Ford przemyka przez granicę, radiowóz hamuje przed nią z piskiem",
      "By day twenty, Hamer understood their main trick: in those days, police could rarely follow a car across a "
      "state line, so Clyde simply drove into the next state.", mark="AKT III", dodaj=1.0),
    U("list_ford", "D", "biuro Hamera", "Na biurku leży list na papierze firmowym; zjeżdża podpis „Clyde?” i tabliczka "
      "ze znakiem zapytania",
      "Clyde preferred stolen Fords, and Henry Ford even received a letter thanking him for such a fine getaway car, "
      "though nobody is sure Clyde really wrote it."),
    S("wellington_noc", "But even the best driver in the South made mistakes, and one night near Wellington, Texas, he "
      "missed the signs warning that a bridge was out."),
    S("wellington_most", sek=3.4),
    S("wellington_bonnie", "The car caught fire, and battery acid burned Bonnie's leg so badly that she never walked "
      "normally again."),
    S("farma", "A farm family took them in and tried to help, until somebody called the sheriff."),
    S("drzewo", "They took the two lawmen who came to investigate and left them tied to a tree in Oklahoma, which did "
      "not make the police like them any more."),
    S("noszenie", "From then on Clyde often had to carry her, and a limping woman in a stolen Ford is easy to "
      "remember."),
    S("oboz", "They slept in stolen cars and ate from cans, because every motel clerk in the South had seen their "
      "pictures."),
    S("rzeka", sek=2.3),
    S("hamer_motel", "Everywhere Hamer went, someone remembered them: a limping girl, a young man in a hat, a new Ford "
      "and a pile of empty cans."),
    S("platte", "In July, police caught up with them twice in one week, first at a motel in Missouri and then in an "
      "Iowa park.", pauza="beat"),
    S("dexfield", "Buck was captured, dying, and Blanche, half blinded by flying glass, was arrested beside him."),
    S("przeprawa", "Bonnie and Clyde waded across a river and escaped, wounded."),
    S("wd_odchodzi", "Soon after, W.D. Jones slipped away in the night and went home, so they were hurt and alone, "
      "but who was still helping them?", pauza="akt"),
    S("rodziny", "The answer was their families: every few weeks, Bonnie and Clyde met their mothers on dark country "
      "roads outside Dallas, bringing laundry and taking home-cooked food.", mark="AKT IV",
      opis="Kurtyna „Act IV · Day 50: who is helping them?”; nocą przy polnej drodze stoją dwa auta z wygaszonymi "
      "światłami; matki podają przez okna koszyki z jedzeniem, Bonnie oddaje pranie"),
    S("sowers", "In November, the Dallas sheriff had tried to ambush one of these family picnics, but his men opened "
      "fire too early, and the couple escaped with bullets in their legs."),
    S("petle", "Hamer didn't want a shootout at a picnic, he wanted their next road, and the red thread on his map "
      "kept leading him back to their mothers.", pauza="beat"),
    S("grapevine", "Then, on day fifty, Easter Sunday, two young patrolmen stopped near Grapevine, Texas, to help what "
      "looked like a stranded car.",
      opis="Zawieszka „DAY 50 · Easter Sunday”; wiejska droga, kwitnące drzewa, Ford stoi na poboczu; nadjeżdżają "
      "dwaj motocykliści i zwalniają"),
    S("grapevine_cien", "They were shot before they could draw their guns.", pauza="beat", dodaj=1.2),
    S("tullis", "One of them, H.D. Murphy, was due to marry Maree Tullis that month, and local historians say she wore "
      "her wedding dress to his funeral.", pauza="beat"),
    S("gazety_zle", "The papers said Bonnie had laughed over a dying man, which was probably not true, but after "
      "Grapevine America stopped cheering."),
    S("listy_gon", "Rewards were posted across the South, and now every farmer with a shotgun was watching the road "
      "for a stolen Ford."),
    S("commerce", "Five days later, near Commerce, Oklahoma, their car slid into a ditch again, and two lawmen came "
      "over to help."),
    S("commerce_cien", "Clyde killed Constable Cal Campbell and took the police chief, Percy Boyd, as a hostage."),
    S("boyd", "Before letting Boyd go, Bonnie gave him one message for the newspapers."),
    S("boyd_tab", "Not that she was sorry, only that Bonnie Parker did not smoke cigars."),
    S("prasa_cygaro", "The papers printed it, and one of them landed on Hamer's desk, next to a map that was finally "
      "full, but he still needed someone to tell him the day.", pauza="akt"),
    S("odbicie", "Hamer's job had begun with a prison break: in January, Bonnie and Clyde raided Eastham to free their "
      "friends, including a young convict named Henry Methvin.", mark="AKT V",
      opis="Kurtyna „Act V · Day 90: who will betray them?”; zawieszka „January 1934”; mgła nad Eastham, więźniowie "
      "wyciągają broń z rowu, z mgły wyjeżdża Ford z trąbiącym klaksonem"),
    S("straznik", "A guard named Joe Crowson was shot during that escape and later died."),
    S("simmons", "That was why the head of the Texas prisons, Lee Simmons, had called Hamer in the first place, and "
      "promised him a free hand."),
    S("mapa", "By day ninety, the loops on Hamer's map kept passing through one quiet corner of Louisiana, where the "
      "Methvin family had a farm."),
    S("methvin", "Henry's father, Ivy Methvin, was a farmer in Louisiana, and Hamer offered him a deal: help set a "
      "trap, and your son will be pardoned."),
    S("shreveport", "On May 21, Henry got separated from Bonnie and Clyde in Shreveport, and Hamer knew exactly where "
      "he would go: home to his father's farm, where they would come looking for him."),
    S("wiersz", "Bonnie seemed to sense what was coming, and around that time she gave her mother a poem that "
      "predicted she and Clyde would die together."),
    S("pozegnanie", "Then they kept driving, because the car was the only home they had left, so where would Hamer "
      "wait for them?", pauza="akt"),
    U("noc", "PO", "droga w Luizjanie (noc)", "Kurtyna „Act VI · Day 102: what happens on a quiet road?”; zawieszka "
      "„DAY 102”; noc w lesie, sześciu mężczyzn kuli się w krzakach, nad kapeluszami krążą komary; jeden się klepie "
      "w kark",
      "On the last night, Hamer and five other lawmen hid in the bushes along a country road in Louisiana, and the "
      "mosquitoes found them first.", mark="AKT VI"),
    S("posse", "Hamer brought his old partner Manny Gault, two Dallas deputies who knew Clyde by sight, Bob Alcorn "
      "and Ted Hinton, and the local sheriff, Henderson Jordan, with his deputy, Prentiss Oakley."),
    S("zasadzka_rano", "At dawn, Ivy Methvin's truck stood by the road on a jack, as if he had a flat tyre, waiting "
      "for a car that knew him."),
    S("kanapka", "Clyde was driving in his socks, and Bonnie was eating a sandwich she had just bought in town."),
    S("zwolnienie", sek=2.2),
    S("zasadzka", sek=4.8),
    S("dym", "The lawmen fired more than a hundred rounds in a few seconds, and Clyde never reached his gun.",
      pauza="akt"),
    S("pamiatki", "Within hours thousands of people poured into the small town of Arcadia, and souvenir hunters cut "
      "pieces of Bonnie's hair and dress.", mark="AKT VII",
      opis="Kurtyna „Act VII · Who won the story?”; tłum otacza podziurawionego Forda w Arcadii; ktoś odcina nożyczkami "
      "pukiel włosów, ktoś kawałek sukienki; szeryf odgania ludzi"),
    S("darby_zaklad", "The undertaker Bonnie had once laughed at, Dillard Darby, reportedly helped prepare their "
      "bodies."),
    S("pogrzeby", "Bonnie's mother refused to let her lie next to Clyde, so the poem was wrong about one thing: they "
      "were buried in different cemeteries.", pauza="beat"),
    S("auto_jarmark", "Even their bullet-riddled car went on tour, and people paid to look at it at fairs across the "
      "country."),
    U("hamer_ganek", "PŚ", "ganek w Austin", "Hamer na ganku odkłada gazetę z nagłówkiem o zasadzce, zakłada kapelusz "
      "i odwraca się od reporterów",
      "Hamer rarely talked about that morning, and he never wrote a book about it."),
    U("film_hamer", "PO", "kino", "Gazety składają się w ekran kina: aktor grający Hamera stoi związany, a filmowa "
      "Bonnie robi sobie z nim zdjęcie; widownia się śmieje; obok ekranu prawdziwy Hamer z tabliczką „THAT'S NOT ME!”",
      "Then in 1967, a Hollywood hit showed him captured and humiliated by the gang, something that never happened, "
      "and his family sued the studio."),
    U("koniec", "PŚ", "teatr (biuro Hamera)", "Teczka Hamera zamyka się; wycinki składają się w jedną gazetę; kurtyna "
      "zasuwa się",
      "In the end, the man who caught them by reading paper lost the story to paper too, because legends sell better "
      "than files.", pauza="akt"),
    S("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
]

# ═══ WARIANT C · WIERSZ BONNIE ═════════════════════════════════════════════════════════════════════════════════════
C_POMYSL = (
    "Historia dziewczyny, która chciała być sławna. Ramą jest maleńka scena z jedną lampą i zeszyt Bonnie: kartki "
    "przewracają się jak kurtyny, a wersy jej wierszy wyjeżdżają na paskach papieru. Hak 1: kilka tygodni przed "
    "śmiercią napisała wiersz, który przewidział ich koniec — trafiła we wszystko poza jednym szczegółem (odpowiedź "
    "w akcie VII: matka nie pozwoliła na wspólny grób). Pogorszenie: Kaufman — pierwszy napad kończy się na mułach "
    "i w areszcie; hak 2 i promyk: w celi Bonnie znajduje temat swoich wierszy, własne życie. Humor: ambicje kontra "
    "błoto, fartuszek i gazety klientów, cygaro, które ją rozwścieczyło, przedsiębiorca pogrzebowy. Od Grapevine "
    "nagłówki piszą jej historię bez niej; finał: 20 tysięcy ludzi na pogrzebie — największa widownia, jaką miała.")
C = [
    U("zap_zeszyt", "D", "zeszyt Bonnie", "zapowiedź: ołówek pisze w zeszycie, kartka się przewraca",
      mark="ZAPOWIEDŹ 5 s", sek=0.8),
    Z("zdjecie", 0.6, "Bonnie z cygarem pozuje, błyska flesz"),
    Z("wellington_most", 0.8, "Ford spada z mostu w wąwóz, bucha płomień"),
    Z("boyd_tab", 0.7, "tabliczka „SHE DOESN'T SMOKE CIGARS!” nad porwanym komendantem"),
    Z("pogrzeby", 0.7, "dwa pogrzeby na dwóch cmentarzach"),
    Z("zasadzka", 1.5, "dziesiątki błysków za parawanem; ściemnienie"),
    U("tytul", "TYT", "teatr (mała scena)", "Kurtyna startu rozsuwa się na maleńką scenę z jedną lampą; stoi na niej "
      "Bonnie z zeszytem i kłania się pustej widowni; z góry zjeżdża szyld „The Outlaws Made of Paper”",
      mark="TYTUŁ · kurtyna startu", sek=4.6),
    U("wprowadzenie", "PŚ", "teatr (mała scena)", "Kamera najeżdża na Bonnie; przy imieniu zjeżdża podpis „Bonnie "
      "Parker”; Bonnie przyciska zeszyt do piersi i uśmiecha się do widowni",
      "Bonnie Parker wanted to be famous, as an actress, a singer or a poet, and in the end the whole of America knew "
      "her name.", mark="WPROWADZENIE"),
    U("wprowadzenie2", "PP", "teatr (mała scena)", "Obok Bonnie wysuwa się Clyde z karabinem, podpis „Clyde Barrow”; "
      "pusta widownia nagle zapełnia się policjantami w czapkach",
      "She just didn't plan to get famous robbing gas stations with Clyde Barrow, with half the police in the South "
      "trying to catch her.", pauza="beat"),
    U("hak_wiersz", "D", "zeszyt Bonnie", "Ołówek kończy ostatnią zwrotkę wiersza i podpisuje „Bonnie”; litery "
      "na moment świecą",
      "A few weeks before she died, Bonnie wrote a poem predicting exactly how she and Clyde would end.",
      mark="HOOK 1", hak=True),
    U("hak_pomost", "D", "zeszyt Bonnie", "Pomost: kartka zeszytu przewraca się przez cały kadr jak kurtyna", sek=1.6),
    U("hak_droga", "PO", "droga w Luizjanie (teatr cieni)", "Za parawanem papierowy Ford zwalnia na leśnej drodze, "
      "z krzaków wysuwają się lufy; obraz staje, światło gaśnie",
      "She got almost everything right, the road, the guns and the two of them together, except for one detail.",
      hak=True),
    U("obietnica", "PŚ", "teatr (mała scena)", "Bonnie zamyka zeszyt i patrzy w kamerę; z nitki zjeżdża wielki znak "
      "zapytania i kołysze się nad nią",
      "By the end, you'll know what she got wrong, and how a girl who wrote poems in a Dallas café became the most "
      "photographed outlaw in America.", mark="OBIETNICA", pauza="beat"),
    U("cement_city", "PO", "Cement City", "Kurtyna „Act I · What did Bonnie Parker dream about?”; z ziemi wyrastają "
      "dymiące kominy cementowni i drewniane domki; mała Bonnie z mamą wysiadają z wozu z tobołkami",
      "Her story starts in Cement City, a dusty factory town outside Dallas, where her widowed mother moved the family "
      "when Bonnie was four.", mark="AKT I · POMOST", dodaj=1.0),
    S("szkola", "Bonnie was tiny, loud and clever, she won prizes for spelling and poetry, and she dreamed of standing "
      "on a real stage."),
    S("slub", "At fifteen she married Roy Thornton and had their names tattooed in two hearts, because she never did "
      "anything halfway."),
    S("roy", "Roy soon disappeared into prison, yet Bonnie never divorced him and wore his ring for the rest of her "
      "life."),
    S("pamietnik", "While he was gone, she kept a diary, and most of its pages complained that nothing exciting ever "
      "happened to her."),
    S("kawiarnia", "So at nineteen she was a waitress in Dallas, pouring coffee for customers who never looked up from "
      "their newspapers.", pauza="beat"),
    S("kuchnia", "Then, in January 1930, in a friend's kitchen, she met a charming young man named Clyde Barrow."),
    S("areszt", "A few weeks later the police arrested him for a string of burglaries, and Bonnie suddenly had a "
      "dramatic role to play."),
    S("waco", "She smuggled a pistol into the Waco jail, and soon after, Clyde broke out."),
    S("ohio", "He was caught again a week later in Ohio, which tells you a lot about his talent for escapes."),
    S("eastham", "He was sent to Eastham, the most feared prison farm in Texas, where men picked cotton from dawn to "
      "dark."),
    S("eastham_rura", "There Clyde killed a man for the first time, an inmate who had attacked him again and again."),
    S("palce", "To escape the cotton fields, he had two toes cut off with an axe, and six days later he was paroled "
      "anyway."),
    U("brama_c", "PP", "Eastham (brama)", "Clyde wychodzi o kulach przez bramę; po drugiej stronie drogi czeka Bonnie "
      "w kapeluszu; robi krok w jego stronę, potem drugi",
      "When he limped out of Eastham in 1932, he swore he would never go back, and Bonnie had to decide which side of "
      "the law she was on.", pauza="akt"),
    S("kaufman", "She didn't have to decide for long: her first robbery with Clyde ended with their car stuck in the "
      "mud and the two of them on stolen mules that refused to move.", mark="AKT II · POGORSZENIE",
      opis="Kurtyna „Act II · Can a poet rob a store?”; nocą Ford grzęźnie w błocie po kołpaki; Clyde i Bonnie "
      "wskakują na dwa muły, muły ani drgną; tabliczka „GO!”"),
    U("kaufman_zlapana", "PP", "Kaufman (pole)", "Policjanci z latarkami otaczają Bonnie siedzącą na mule; muł spokojnie "
      "je trawę; w tle Clyde ucieka przez pole",
      "Clyde ran off to find another car, and Bonnie was caught and locked in the Kaufman jail."),
    S("cela", "But behind bars she finally found her subject, and she filled a notebook with a long poem about an "
      "outlaw girl called Suicide Sal.", mark="HOOK 2 · promyk nadziei", pauza="beat"),
    U("paski", "PO", "teatr (mała scena)", "Wersy wiersza wyjeżdżają na papierowych paskach jak napisy w kinie; Bonnie "
      "recytuje do pustej widowni, w pierwszym rzędzie siada jeden strażnik",
      "It was full of gangsters, betrayal and big feelings, and for the first time Bonnie was writing about a world "
      "she was about to live in."),
    S("matka_obietnica", "When the grand jury let her go, she promised her mother she was done with Clyde, and that "
      "promise lasted a few weeks."),
    S("hillsboro", "Meanwhile, during one of Clyde's robberies in Hillsboro, a shopkeeper named John Bucher was shot "
      "dead, and the poem was turning into real life.", pauza="beat"),
    S("stacja", "Their robberies were small, gas stations and grocery stores that often paid only a few dollars, and "
      "every one of them made the two of them more wanted."),
    S("atoka", "That August, Clyde's gang killed a deputy at a country dance in Oklahoma, and now they were wanted for "
      "killing a lawman.", pauza="beat"),
    S("wd", "A sixteen-year-old neighbor, W.D. Jones, joined them, mostly because it sounded exciting."),
    S("buck", "Then Clyde's brother Buck, just pardoned, came along with his wife Blanche, who brought her little white "
      "dog."),
    S("joplin_dom", "In Joplin, Missouri, the five of them rented an apartment over a garage and tried to live like a "
      "normal family."),
    S("joplin_karty", "For them, a normal family life mostly meant cards, whiskey and loud arguments, but what would "
      "Bonnie leave behind when the police came?", pauza="akt"),
    S("joplin_walka", "In April 1933 the police came, two officers were killed, and the gang fled, leaving almost "
      "everything behind.", mark="AKT III",
      opis="Kurtyna „Act III · How do you become a star?”; za parawanem błyski z okien garażu w Joplin, dwie sylwetki "
      "policjantów padają, gang zbiega do auta i wyjeżdża"),
    S("joplin_ofiary", "The two men killed that day were Detective Harry McGinnis and Constable Wes Harryman."),
    S("joplin_rzeczy", "Among the things the gang left were Bonnie's poem and a camera full of film."),
    S("zdjecie", "On one frame, Bonnie had posed with a pistol and a borrowed cigar, playing a gangster for the "
      "camera."),
    S("ciemnia", "The Joplin Globe developed the film in its darkroom, and Bonnie's joke slowly appeared on the "
      "paper."),
    S("prasa", "Newspapers printed the pictures across the country, and the waitress from Dallas finally had the "
      "audience she always wanted."),
    S("suicide_druk", "The papers even printed her poem about Suicide Sal, so Bonnie became a published poet in the "
      "worst possible way."),
    S("kiosk", "People hit hard by the Depression bought every edition, because these two looked like they were "
      "having more fun than anyone else."),
    S("naglowki", "Reporters printed anything that sold, calling her the brains of the gang, a crack shot and a "
      "cigar-smoking gun girl."),
    U("cygaro_zlosc", "Z", "kryjówka (auto)", "Bonnie w aucie czyta gazetę ze swoim zdjęciem, marszczy brwi i wyrzuca "
      "cygaro przez okno; tabliczka „CIGARETTES!”",
      "Bonnie loved being famous, but she hated being called the cigar-smoking gun girl, because she only smoked "
      "cigarettes.", pauza="beat"),
    S("darby_auto", "Two weeks later in Louisiana they stole a car, and its owner, a young man named Dillard Darby, "
      "chased them with a friend, Sophia Stone."),
    S("darby_tyl", "The gang caught them both and took them along for a long, nervous ride."),
    S("darby_smiech", "When Bonnie asked what he did for a living and he said he was an undertaker, she reportedly "
      "laughed and said he might have to work on her one day."),
    S("darby_puszczeni", "They let him go with five dollars to get home, and he probably hoped never to see her again, "
      "but fame was fun, so what would it cost?", pauza="akt"),
    S("wellington_noc", "In June 1933, near Wellington, Texas, Clyde drove into the night too fast to notice that the "
      "bridge ahead was gone.", mark="AKT IV",
      opis="Kurtyna „Act IV · What does fame cost?”; nocna droga przez prerię, Ford pędzi; tablica „DETOUR” mija się "
      "w ciemności"),
    S("wellington_most", sek=3.4),
    S("wellington_bonnie", "The car burned, and battery acid seared Bonnie's leg so badly that she would never walk "
      "properly again."),
    S("farma", "A farm family took them in and tried to help, but somebody called the sheriff, and two lawmen "
      "arrived."),
    S("drzewo", "The gang took both lawmen hostage and left them tied to a tree in Oklahoma, which was rude, but at "
      "least nobody died that night."),
    S("noszenie", "For the rest of her life she limped, and when the pain was bad, Clyde carried her."),
    S("oboz", "Fame meant sleeping in stolen cars, eating cold beans and washing her hair in rivers, while her photo "
      "hung in every post office."),
    S("rzeka", sek=2.3),
    S("platte", "In July police surrounded them at a motel; Buck was shot in the head, and flying glass blinded "
      "Blanche in one eye.", pauza="beat"),
    S("dexfield", "Days later in Iowa, Buck was captured, dying, and Blanche stayed with him, even though it meant "
      "prison."),
    S("przeprawa", "Bonnie and Clyde escaped across a river, wounded."),
    S("wd_odchodzi", "Soon W.D. Jones slipped away too, and now there was nobody left but the two of them, so why "
      "didn't she go home?", pauza="akt"),
    S("rodziny", "She did go home, every few weeks, to meet her mother on dark country roads outside Dallas, even "
      "though every visit could be a trap.", mark="AKT V",
      opis="Kurtyna „Act V · Who writes the headlines?”; nocą przy polnej drodze dwa auta z wygaszonymi światłami; "
      "matka Bonnie podaje przez okno koszyk, Bonnie ściska jej rękę"),
    S("sowers", "In November the sheriff tried exactly that, and both of them escaped with bullets in their legs."),
    S("odbicie", "In January 1934, Bonnie honked the horn through the fog at Eastham to guide five escaped convicts to "
      "the car."),
    S("straznik", "Behind them, a guard named Joe Crowson lay dying."),
    S("hamer", "That raid made Texas hire a retired Ranger named Frank Hamer, a man who didn't care about headlines at "
      "all."),
    S("mapa", "Hamer didn't chase them; he studied every place they had been, and he noticed that they always came "
      "home to their families."),
    S("grapevine", "On Easter Sunday, near Grapevine, Texas, two young highway patrolmen stopped to help what looked "
      "like a stranded car."),
    S("grapevine_cien", "They were shot before they could draw their guns.", pauza="beat", dodaj=1.2),
    S("tullis", "One of them, H.D. Murphy, was supposed to marry Maree Tullis that month, and local historians say she "
      "came to his funeral in her wedding dress.", pauza="beat"),
    S("gazety_zle", "The papers wrote that Bonnie laughed over a dying patrolman, which was probably false, but now "
      "the headlines were writing her story without her."),
    S("listy_gon", "Rewards were posted across the South, and every farmer with a shotgun was watching the road."),
    S("commerce", "Five days later, near Commerce, Oklahoma, their car slid into a ditch, and two lawmen walked over "
      "to help."),
    S("commerce_cien", "Clyde killed Constable Cal Campbell, and the gang took the police chief, Percy Boyd, as a "
      "hostage."),
    S("boyd", "They drove him around for hours, and Bonnie kept talking to him about the newspapers."),
    S("boyd_tab", "Before letting him go, Bonnie asked him to tell the newspapers just one thing: she did not smoke "
      "cigars."),
    S("prasa_cygaro", "The papers printed it everywhere, and it was the last headline she ever corrected, so how would "
      "she write the ending?", pauza="akt",
      opis="Maszyna drukarska wypluwa gazety z nagłówkiem „BONNIE: NO CIGARS!”; jedna gazeta ląduje w aucie na "
      "kolanach Bonnie, ona uśmiecha się pierwszy raz od dawna"),
    S("wiersz", "In May 1934, Bonnie gave her mother a new poem, which said that one day they would go down together "
      "and be buried side by side.", mark="AKT VI",
      opis="Kurtyna „Act VI · How does her poem end?”; dom matki Bonnie; Bonnie wręcza matce zeszyt, matka czyta przy "
      "lampie, za oknem czeka Ford"),
    S("methvin", "By then Frank Hamer had made a deal with Ivy Methvin, the father of a young convict they had freed, "
      "to help set a trap on a Louisiana road."),
    S("pozegnanie", "Bonnie and Clyde saw their families one last time, and then they drove east.", pauza="beat"),
    S("shreveport", "On May 21, Henry Methvin got separated from them in Shreveport, and everyone knew he would head "
      "for his father's farm, so Bonnie and Clyde would come looking for him there."),
    S("posse", "Six lawmen were waiting for them: Hamer and his old partner Manny Gault, two Dallas deputies who knew "
      "Clyde by sight, and the local sheriff with his deputy."),
    S("zasadzka_rano", "On the morning of May 23, Ivy's truck stood by the road on a jack, while those six men waited "
      "in the bushes."),
    S("kanapka", "Bonnie was eating a sandwich, and Clyde was driving in his socks."),
    S("zwolnienie", sek=2.2),
    S("zasadzka", sek=4.8),
    S("dym", "The lawmen fired more than a hundred rounds in a few seconds, and just as the poem said, they went down "
      "together.", pauza="akt"),
    S("pamiatki", "Thousands of people crowded into the little town of Arcadia, and souvenir hunters cut locks of her "
      "hair and pieces of her dress.", mark="AKT VII",
      opis="Kurtyna „Act VII · What did she get wrong?”; tłum otacza podziurawionego Forda w Arcadii; ktoś odcina "
      "nożyczkami pukiel włosów, ktoś kawałek sukienki"),
    S("darby_zaklad", "The undertaker she had laughed at a year before, Dillard Darby, reportedly helped prepare her "
      "body."),
    S("pogrzeby", "And here is what the poem got wrong: Bonnie's mother refused to let them share a grave, so they "
      "were buried in two different cemeteries.", mark="ODPOWIEDŹ NA HOOK 1", pauza="beat"),
    U("tlum", "PO", "cmentarz w Dallas", "Na pogrzeb Bonnie schodzi się ogromny tłum, z nieba spadają kwiaty; "
      "kamera odjeżdża, aż widać cały cmentarz pełen ludzi",
      "About twenty thousand people came to her funeral, the biggest audience she ever had.", dodaj=1.0),
    S("auto_jarmark", "Even the bullet-riddled car went on tour, and people paid to look at it at fairs across the "
      "country."),
    S("blanche_po", "Blanche served six years in prison and lived quietly until 1988, the only one of the four who "
      "grew old.", pauza="beat"),
    S("ksiazka", "That same year, Bonnie's mother published a book about her daughter with her poems inside, so "
      "Bonnie finally became an author."),
    S("legenda", "Thirty years later a Hollywood movie gave her the glamour she always wanted, and her story still "
      "sells today."),
    U("koniec", "PŚ", "teatr (mała scena)", "Bonnie na małej scenie kłania się; lampa gaśnie; zeszyt zamyka się sam; "
      "kurtyna zasuwa się",
      "But the real Bonnie Parker was a waitress who wanted to be a poet, and the only stage she ever got was a "
      "stolen Ford.", pauza="akt"),
    S("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
]

def A_(*klucze):
    """Kopie ujęć wariantu A po kluczu (ostatnie wystąpienie — np. „joplin_rzeczy” z aktu III, nie z haka)."""
    ostatnie = {it["klucz"]: it for it in A}
    return [copy.deepcopy(ostatnie[k]) for k in klucze]


# ═══ WARIANT D · A + POŚCIG HAMERA ═════════════════════════════════════════════════════════════════════════════════
D_POMYSL = (
    "Reżyser 19.11.2026: „Robimy A, ale wplatamy gdzieś te B, wydłużając opowieść”. Oś to A (prasa kontra prawda, "
    "po kolei, teatr z gazet). Wątek B wchodzi zasiewem w akcie III (wycinki z kiosku same wpadają do teczki na "
    "pustym biurku łowcy), a od aktu V pościg Hamera prowadzi film: pościgi kończące się w rowie, Hamer przestaje "
    "gonić i otwiera tę teczkę, podkreśla przysięgę z bramy Eastham (powrót do haka 2 innymi słowami), zawieszki "
    "DAY 1 → DAY 20 → DAY 50 (Grapevine) → DAY 102 (zasadzka), sztuczka z granicą stanów, list do Forda, Shreveport, "
    "noc w krzakach i nazwiska sześciu ludzi z zasadzki. Nowy akt VIII: kto ma legendę — pamiątkarze, Darby, osobne "
    "groby, auto na jarmarkach, Blanche, Hamer milczy, Hollywood robi z niego pośmiewisko, gra wideo. Puenta łączy oba: "
    "gazety zrobiły z nich legendę, a cierpliwy człowiek czytający ich akta ich zatrzymał.")
D = [
    Z("wellington_most", 0.9, "Ford spada z rozebranego mostu w wąwóz, bucha płomień", mark="ZAPOWIEDŹ 5 s"),
    Z("zdjecie", 0.6, "Bonnie z cygarem i rewolwerem pozuje przy Fordzie, błyska flesz"),
    Z("prasa", 0.7, "wałki drukarni kręcą się, wylatują gazety ze zdjęciem"),
    Z("boyd", 0.6, "porwany komendant z rękami w górze, Bonnie grozi mu palcem"),
    Z("petle", 0.6, "czerwona nić na mapie Hamera układa się w pętlę"),
    Z("hamer", 0.6, "Hamer wstaje z bujanego fotela i sięga po karabin"),
    Z("pamiatki", 1.3, "tłum przy podziurawionym Fordzie, ktoś odcina pukiel włosów; ściemnienie"),
    U("tytul", "TYT", "teatr z gazet", "Kurtyna startu rozsuwa się na teatr zbudowany z gazet: stoi Ford, Bonnie opiera "
      "nogę o zderzak z cygarem w zębach i rewolwerem, obok Clyde z karabinem; z góry zjeżdża szyld „The Outlaws Made of "
      "Paper”", mark="TYTUŁ · kurtyna startu", sek=4.6),
    U("wprowadzenie", "PŚ", "teatr z gazet", "Kamera najeżdża na Bonnie; przy jej imieniu zjeżdża podpis „Bonnie "
      "Parker”; Bonnie wyjmuje cygaro z ust i krzywi się",
      "This is Bonnie Parker, the most famous outlaw girl in America, and almost everything you think you know about "
      "her was printed in a newspaper.", mark="WPROWADZENIE"),
    U("wprowadzenie2", "PP", "teatr z gazet", "Kamera odjeżdża na Clyde'a; podpis „Clyde Barrow”; za nimi z nitek "
      "zjeżdżają nagłówki gazet jeden za drugim",
      "Together with Clyde Barrow, she spent two years robbing gas stations and corner shops, while the papers turned "
      "two broke kids from Dallas into legends.", pauza="beat"),
    S("joplin_rzeczy", "In April 1933, police raided their hideout in Joplin, Missouri, and found the one thing outlaws "
      "should never leave behind: a camera full of film.", mark="HOOK 1", hak=True),
    S("zdjecie", "On one frame, Bonnie posed with a pistol and a borrowed cigar, just for fun.", hak=True),
    U("hak_pomost", "D", "teatr z gazet", "Pomost: wielka strona gazety przewraca się przez cały kadr jak kurtyna, szelest "
      "papieru", sek=1.6),
    S("prasa", "Within days that joke was on front pages across America, and Bonnie became the cigar-smoking gun girl.",
      hak=True),
    U("hak_cygaro", "Z", "kryjówka (auto)", "Bonnie w aucie czyta gazetę ze swoim zdjęciem, wypuszcza z ust papierosa "
      "i zgniata gazetę; tabliczka „I DON'T SMOKE CIGARS!”",
      "There was just one problem: Bonnie didn't smoke cigars, and she spent the rest of her short life trying to tell "
      "everyone.", hak=True),
    U("obietnica", "PO", "teatr z gazet", "Gazety układają się w mapę pięciu stanów; po mapie sunie papierowy Ford, a za "
      "nim, w pewnej odległości, sunie drugi, z kapeluszem Hamera w oknie",
      "By the end, you'll know how two small-time thieves became the most hunted couple in America, how a retired "
      "Ranger caught them without ever chasing them, and why their legend still sells today.", mark="OBIETNICA",
      pauza="beat"),
    *A_("wagon", "indyki", "szkola", "slub", "roy", "kawiarnia", "kuchnia", "areszt", "waco", "ohio", "eastham",
        "eastham_rura", "palce", "parol", "przysiega",
        "akt2", "stacja", "kaufman", "cela", "hillsboro", "matka_obietnica", "atoka", "wd", "buck", "joplin_dom",
        "joplin_karty",
        "joplin_walka", "joplin_ofiary", "joplin_rzeczy", "ciemnia", "kiosk", "cygaro_zlosc", "darby_auto",
        "darby_tyl", "darby_smiech", "darby_puszczeni"),
    U("teczka_zasiew", "D", "biuro Hamera (zapowiedź)", "Wycinki z gazet odfruwają z kiosku i jeden po drugim wpadają "
      "do grubej teczki na pustym biurku; krzesło przy biurku jest puste, na oparciu wisi kapelusz",
      "None of them knew yet that every one of these clippings would end up in a single file, on the desk of the man "
      "who would finally catch them."),
    U("plakaty", "PO", "mapa z gazet", "Mapa z gazet: pinezki w Teksasie, Oklahomie, Missouri, Luizjanie; na mapie "
      "wyrastają ich twarze z listów gończych",
      "For now, their faces were on wanted posters in five states, but what happens when America's most famous "
      "getaway driver misses a road sign?", pauza="akt", dodaj=1.0),
    *A_("wellington_noc", "wellington_most", "wellington_bonnie", "farma",
                                              "drzewo", "noszenie", "oboz", "rzeka"),
    U("list_ford", "D", "obóz przy drodze", "Na masce Forda leży list na papierze firmowym; zjeżdża podpis „Clyde?” "
      "i tabliczka ze znakiem zapytania",
      "Clyde preferred stolen Fords, and Henry Ford even received a letter thanking him for such a fine getaway car, "
      "though nobody is sure Clyde really wrote it."),
    *A_("platte", "dexfield", "przeprawa", "wd_odchodzi", "rodziny", "sowers",
                                              "odbicie", "straznik", "simmons", "hamer"),
    U("poscigi", "PO", "droga w Teksasie", "Radiowóz goni Forda po zakrętach; Ford znika za wzgórzem, radiowóz wylatuje "
      "z zakrętu i ląduje w rowie kołami do góry; tabliczka „AGAIN?!”",
      "Police in five states had been chasing Bonnie and Clyde for two years, and those chases usually ended the same "
      "way, with the police car in a ditch.", mark="HOOK 3 · pościg Hamera"),
    U("hak_szuflada", "PŚ", "biuro Hamera", "Hamer zdejmuje z biurka zabawkowy radiowóz i chowa go do szuflady; "
      "tabliczka „NO MORE CHASING”",
      "So Hamer did something nobody expected: he stopped chasing them."),
    U("hak_teczka", "PŚ", "biuro Hamera", "Hamer otwiera grubą teczkę z aktu III; wycinki wyfruwają i same przypinają "
      "się do mapy; Hamer stawia kubek kawy i siada wygodnie",
      "Instead, he sat down with that file of newspaper clippings and a map, and he waited for them to make one "
      "mistake."),
    U("podkreslenie", "D", "biuro Hamera", "Hamer podkreśla w aktach jedno zdanie czerwonym ołówkiem, dwa razy; z nitki "
      "zjeżdża tabliczka „HE WON'T GO BACK”",
      "He underlined one line twice, the promise Clyde had made at the gate of Eastham, which meant there would never "
      "be a surrender, only the question of where.", pauza="beat"),
    U("dzien1", "PO", "droga w Teksasie", "Zjeżdża zawieszka „DAY 1”; Hamer jedzie starym autem przez prerię z mapą na "
      "kolanach",
      "On day one, Hamer started driving, not after them, but through every town where they had already been.",
      dodaj=1.0),
    S("hamer_motel", "Everywhere he went, someone remembered them: a limping girl, a young man in a hat, a new Ford "
      "and a pile of empty cans."),
    U("dzien20", "PO", "granica stanów", "Zawieszka „DAY 20”; na drodze tablica „STATE LINE”; Ford przemyka przez "
      "granicę, radiowóz hamuje przed nią z piskiem",
      "By day twenty, he understood their main trick: in those days, police could rarely follow a car across a state "
      "line, so Clyde simply drove into the next state.", dodaj=1.0),
    S("mapa", "So Hamer stopped marking where they had been and started marking where they kept coming back to."),
    S("petle", "The loops always ran along state lines, and sooner or later every one of them led home to their "
      "mothers, so how long would Hamer have to wait?", pauza="akt"),
    S("grapevine", "On day fifty of Hamer's hunt, Easter Sunday 1934, two young highway patrolmen stopped near "
      "Grapevine, Texas, to help what they thought was a stranded car.", mark="AKT VI",
      opis="Kurtyna „Act VI · When did America stop cheering?”; zawieszka „DAY 50 · Easter Sunday”; wiejska droga, "
      "kwitnące drzewa, Ford stoi na poboczu; nadjeżdżają dwaj motocykliści i zwalniają"),
    *A_("grapevine_cien", "tullis", "gazety_zle", "listy_gon", "commerce",
                                              "commerce_cien", "boyd", "boyd_tab"),
    S("prasa_cygaro", "The papers printed that too, and one of them landed on Hamer's desk, next to a map that was "
      "finally full, but he still needed someone to tell him the day.", pauza="akt"),
    S("methvin", "Hamer found that someone in Ivy Methvin, the father of Henry Methvin, a young convict they had freed at Eastham: "
      "help set a trap, and your son will be pardoned.", mark="AKT VII",
      opis="Kurtyna „Act VII · How do you set a trap for a ghost?”; chata w Luizjanie; Hamer siedzi przy stole "
      "naprzeciw brodatego farmera, między nimi papier z pieczęcią „PARDON”; farmer kiwa głową; podpis „Ivy Methvin”"),
    S("wiersz", "Around that time, Bonnie gave her mother a new poem, which said that one day she and Clyde would go "
      "down together and be buried side by side."),
    *A_("pozegnanie"),
    S("shreveport", "On May 21, Henry Methvin got separated from Bonnie and Clyde in Shreveport, and Hamer knew where "
      "he would go: home to his father's farm, where they would come looking for him."),
    U("noc", "PO", "droga w Luizjanie (noc)", "Zawieszka „DAY 101”; noc w lesie, sześciu mężczyzn kuli się w krzakach; "
      "nad kapeluszami krążą komary, jeden mężczyzna bezgłośnie klepie się w kark",
      "On the night of May 22, Hamer and five other lawmen hid in the bushes along a country road in Louisiana, and they waited "
      "there until dawn, swatting mosquitoes in silence."),
    S("posse", "Hamer had brought his old partner Manny Gault, two Dallas deputies who knew Clyde by sight, Bob Alcorn "
      "and Ted Hinton, and the local sheriff, Henderson Jordan, with his deputy, Prentiss Oakley."),
    S("zasadzka_rano", "On the morning of day one hundred and two, May 23, Ivy Methvin's truck stood by the road on a "
      "jack as bait.",
      opis="Zawieszka „DAY 102”; świt na leśnej drodze; ciężarówka Ivy'ego stoi na lewarku jak z przebitą oponą; "
      "w krzakach sześć kapeluszy i luf"),
    *A_("kanapka", "zwolnienie", "zasadzka"),
    S("dym", "The lawmen fired more than a hundred rounds in a few seconds, and it was over before Clyde could reach "
      "for a gun.", pauza="akt"),
    S("pamiatki", "Within hours thousands of people crowded into the little town of Arcadia, and souvenir hunters cut "
      "locks of Bonnie's hair and pieces of her dress.", mark="AKT VIII",
      opis="Kurtyna „Act VIII · Who owns the legend?”; tłum otacza podziurawionego Forda w Arcadii; ktoś odcina "
      "nożyczkami pukiel włosów, ktoś kawałek sukienki; szeryf odgania ludzi"),
    *A_("darby_zaklad", "pogrzeby", "auto_jarmark", "blanche_po"),
    U("hamer_ganek", "PŚ", "ganek w Austin", "Hamer na ganku odkłada gazetę z nagłówkiem o zasadzce, zakłada kapelusz "
      "i odwraca się od reporterów",
      "Hamer rarely talked about that morning, and he never wrote a book about it."),
    U("film_hamer", "PO", "kino", "Gazety składają się w ekran kina: piękna para z filmu z 1967 roku, potem aktor grający "
      "Hamera stoi związany, a filmowa Bonnie robi sobie z nim zdjęcie; widownia się śmieje; obok ekranu prawdziwy "
      "Hamer z tabliczką „THAT'S NOT ME!”",
      "Thirty years later, a Hollywood hit made Bonnie and Clyde young and beautiful, and showed Hamer captured and "
      "humiliated by the gang, something that never happened, so his family sued the studio.", dodaj=1.5),
    U("gra", "PO", "kino", "Ekran z gazet migocze: zamiast filmu pojawia się kolorowa, pikselowa para uciekinierów "
      "w aucie z gry wideo; widzowie w pierwszym rzędzie trzymają pady",
      "And in 2026, a new video game built its heroes on the same old romance."),
    U("koniec", "PŚ", "teatr z gazet", "Papierowa Bonnie z cygarem i Clyde kładą się płasko w stronę gazety; obok "
      "zamyka się teczka Hamera; kurtyna zasuwa się",
      "The real Bonnie and Clyde were two broke kids from Dallas who left at least nine dead lawmen behind them; "
      "newspapers made them legends, and a patient man reading their file brought them down.", pauza="akt"),
    S("dzieki", DZIEKI, mark="PODZIĘKOWANIE", pauza="akt"),
]

WARIANTY = {
    "a": ("A · Legenda z gazety — prasa kontra prawda", A_POMYSL, A),
    "b": ("B · Pościg Hamera — 102 dni i teczka z wycinkami", B_POMYSL, B),
    "c": ("C · Wiersz Bonnie — dziewczyna, która chciała być sławna", C_POMYSL, C),
    "d": ("D · A z pościgiem Hamera — legenda z gazety i teczka łowcy", D_POMYSL, D),
}

TON = (
    "Humor to ironia i suchy lektor: śmiejemy się z legendy, niezdarności i próżności (indyki, muły, wąwóz, cygaro), "
    "nigdy z ofiar. Każda śmierć policjanta czy sprzedawcy ma imię i ciszę; od Grapevine (Wielkanoc 1934) ton zostaje "
    "poważny do końca. Śmierć pokazuje teatr cieni za parawanem — błyski i padające sylwetki, bez krwi. Trzy szczyty "
    "z ciszą muzyki: Wellington, Grapevine, zasadzka.")

FAKTY = (
    "Sprawdzone 18.11 w sieci (do potwierdzenia w gazetach z 1934 przed rozpiską): wiadomość Bonnie przez komendanta "
    "Boyda, że nie pali cygar (relacje wtórne); Maree Tullis w sukni ślubnej na pogrzebie H.D. Murphy'ego (jeden "
    "artykuł lokalny, Tyler Paper) — w kwestii „local historians say”; śmiech Bonnie z zawodu Darby'ego i to, że "
    "Darby pomagał przy balsamowaniu (relacje wtórne) — w kwestii „reportedly”. List Clyde'a do Forda: autentyczność "
    "sporna — kwestia to mówi. Wiersz Bonnie („The Trail's End”) tylko parafrazujemy; status praw autorskich "
    "niesprawdzony. Do sprawdzenia przed rozpiską: 5 dolarów dla porwanych (jedno źródło), 6 dni między obcięciem palców a zwolnieniem, kanapka i skarpetki "
    "w dniu zasadzki, liczba ok. 20 tys. na pogrzebie Bonnie, „co najmniej 9 zabitych stróżów prawa”, wiek i sytuacja "
    "Cala Campbella, dni pościgu Hamera (10.02 → 23.05.1934 = 102 dni; Grapevine 1.04 = dzień 50).")

ZRODLA = (
    "PBS American Experience „Bonnie & Clyde”; FBI History „Bonnie and Clyde”; 64 Parishes „Capture of Bonnie and "
    "Clyde”; Tyler Paper (Maree Tullis); funeralwise.com (Dillard Darby); homebrewedmojo.blogspot.com (Percy Boyd).")


def zegar(t: float) -> str:
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


def buduj(w: str) -> dict:
    tytul, pomysl, items = WARIANTY[w]
    # sąsiednie ujęcia różnią się co najmniej o ¼ s (Rytm 2): późniejsze dostaje 0,3 s dłuższą pauzę po kwestii
    for _ in range(5):
        for poprz, it in zip(items, items[1:]):
            if it["sekundy"] > 1.5 and abs(it["sekundy"] - poprz["sekundy"]) < 0.25 - 1e-9:
                it["sekundy"] = round(it["sekundy"] + 0.3, 1)
    czasy, t = [], 0.0
    for it in items:
        czasy.append(t)
        t += it["sekundy"]
    dlugosc = t
    # pierwsza minuta: zmiany dekoracji (inne miejsce niż w poprzednim ujęciu)
    zmiany, poprz = [], None
    for c, it in zip(czasy, items):
        if c >= 60:
            break
        miejsce = it["miejsce"].split(" (")[0] if it["klucz"].startswith("zap_") else it["miejsce"]
        if poprz is not None and miejsce != poprz:
            zmiany.append(f"{zegar(c)} {it['miejsce']}")
        poprz = miejsce
    znaczniki = [f"{zegar(c)}  {it['mark']}" for c, it in zip(czasy, items) if it["mark"]]
    akty = [m.group(1) for it in items if it["opis"].startswith("Kurtyna")
            for m in [re.search(r"„(Act [^”]+)”", it["opis"])] if m]
    kwestie = [it["kwestia"] for it in items if it["kwestia"]]
    hak2 = next(c for c, it in zip(czasy, items) if "HOOK 2" in it["mark"])
    scen = "\n".join([
        tytul, "", "PODEJŚCIE", pomysl, "", "TON", TON, "",
        f"DŁUGOŚĆ: {zegar(dlugosc)} · {len(items)} ujęć · {len(kwestie)} kwestii EN, "
        f"{sum(slowa(k) for k in kwestie)} słów (tempo {TEMPO_EN} słowa/s)",
        f"HOOK 2 w {zegar(hak2)}", "",
        f"PIERWSZA MINUTA: dekoracja zmienia się {len(zmiany)} razy ({'; '.join(zmiany)})", "",
        "ZNACZNIKI", *znaczniki, "",
        "AKTY (tytuł na kurtynie)", *[f"- {a}" for a in akty], "",
        "FAKTY", FAKTY, "", "ŹRÓDŁA", ZRODLA, "",
        "KLATKI: jeszcze ich nie ma — dekoracje lat 30. (prerie, Ford V8, stacje, drukarnia, teatr cieni) powstaną po "
        "zatwierdzeniu szkicu; w przeglądzie każde ujęcie to karta z opisem i kwestią.",
    ])
    # ujęcie z prologu (hak), którego rysunek wraca w akcie, dostaje klucz „hak_…” (jak w „Synu słońca”)
    akt1 = next(n for n, it in enumerate(items) if it["mark"].startswith("AKT I"))
    pozniej = {it["klucz"] for it in items[akt1:]}
    klucze = [("hak_" + it["klucz"]) if n < akt1 and it["klucz"] in pozniej else it["klucz"]
              for n, it in enumerate(items)]
    assert len(set(klucze)) == len(klucze), [k for k in klucze if klucze.count(k) > 1]
    ujecia = [{"nr": n, "klucz": klucze[n - 1], "sekundy": it["sekundy"], "opis": it["opis"], "kwestia": it["kwestia"],
               "kadr": KADR.get(it["kadr"], it["kadr"]), "znacznik": it["mark"]}
              for n, it in enumerate(items, 1)]
    return {"film": FILM, "wariant": w.upper(), "tytul": tytul, "scenariusz": scen, "ujecia": ujecia,
            "_dlugosc": dlugosc, "_hak2": hak2, "_zmiany": len(zmiany)}


def main(argv: list[str]) -> None:
    for w in (argv or list(WARIANTY)):
        d = buduj(w)
        meta = {k: d.pop(k) for k in ("_dlugosc", "_hak2", "_zmiany")}
        out = TU / w / "szkic.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{d['tytul']}: {zegar(meta['_dlugosc'])}, {len(d['ujecia'])} ujęć, hook 2 w {zegar(meta['_hak2'])}, "
              f"zmiany dekoracji w 1. minucie: {meta['_zmiany']} → {out.relative_to(TU.parents[3])}")


if __name__ == "__main__":
    main(sys.argv[1:])
