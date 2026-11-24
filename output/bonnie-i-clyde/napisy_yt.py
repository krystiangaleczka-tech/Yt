"""Napisy do YouTube (SRT, angielskie i polskie) do „Bonnie and Clyde” (EN) — z czasów prawdziwego lektora w filmie.
Wzór: output/powstanie-japonii/napisy_yt.py (gałąź powstanie-japonii).

  python3 output/bonnie-i-clyde/napisy_yt.py   → output/bonnie-i-clyde/napisy_yt/Bonnie_and_Clyde_en.srt i _pl.srt

Kwestia zaczyna się w filmie tam, gdzie zloz.py kładzie nagranie (start ujęcia + oddech z dane.okno_kwestii, w haku krótszy),
a jej napis trwa od pierwszego do ostatniego dźwięku nagrania lektor_en/<klucz>.wav (+0,4 s, nie dłużej niż do następnego
napisu). Długie kwestie dzielą się na napisy po najwyżej dwa wiersze po 42 znaki (zalecenie YouTube); granice między nimi
trafiają w pauzy lektora, a gdy pauzy nie ma w pobliżu — w miejsce wynikające z liczby znaków.

Film jest tylko po angielsku (rozpiska ma kwestie EN), więc polskie napisy to tłumaczenie kwestii w NAPISY_PL — każda
kwestia musi tam być (skrypt odmawia, gdy brakuje). Reżyser 24.11.2026: „pamiętaj o napisach en i pl, też je zrób”.
"""
import json
import os
import re
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
UJ = HERE.parents[1] / "docs/filmy/bonnie-i-clyde/ujecia"
sys.path.insert(0, str(UJ))
OUT = HERE / "napisy_yt"
LEKTOR = HERE / "lektor_en"
NAZWA = "Bonnie_and_Clyde"
WIERSZ, NAPIS = 42, 84  # znaków w wierszu, w całym napisie (dwa wiersze)
PO_GLOSIE = {"en": 0.4, "pl": 1.2}  # napis zostaje chwilę po ostatnim słowie (polski jest dłuższy: czyta się go dłużej)

NAPISY_PL = {
    "wprowadzenie": "To Bonnie Parker, najsłynniejsza dziewczyna wyjęta spod prawa w Ameryce, a prawie wszystko, co o niej wiesz, wydrukowała gazeta.",
    "wprowadzenie2": "Razem z Clyde'em Barrowem przez dwa lata napadała na stacje benzynowe i sklepiki, a gazety zrobiły z dwójki biednych dzieciaków z Dallas legendy.",
    "hak_joplin_rzeczy": "W kwietniu 1933 roku policja wpadła do ich kryjówki w Joplin w Missouri i znalazła coś, czego przestępcy nigdy nie powinni zostawiać: aparat pełen kliszy.",
    "zdjecie": "Na jednym zdjęciu Bonnie pozowała z pistoletem i pożyczonym cygarem, tak dla zabawy.",
    "prasa": "W kilka dni ten żart trafił na pierwsze strony gazet w całej Ameryce, a Bonnie stała się dziewczyną z cygarem i spluwą.",
    "hak_cygaro": "Był tylko jeden problem: Bonnie nie paliła cygar i przez resztę swojego krótkiego życia próbowała to wszystkim wytłumaczyć.",
    "obietnica": "Jak więc żart zmienia dwójkę biednych dzieciaków w najbardziej ściganą parę w Ameryce i jak jeden cierpliwy człowiek łapie ich, w ogóle ich nie ścigając?",
    "wagon": "Wszystko zaczyna się w West Dallas w latach dwudziestych, w slumsach tak biednych, że nazywano je Diabelskim Gankiem; tam dorastał Clyde Barrow, prawie bez niczego.",
    "indyki": "Jako nastolatek został aresztowany za ciężarówkę pełną kradzionych indyków.",
    "poezja": "W tym samym czasie, kilka kilometrów dalej, w Cement City, Bonnie Parker pisała wiersze i marzyła o scenie.",
    "slub": "Ale mając piętnaście lat, wyszła za chłopaka o imieniu Roy Thornton i wytatuowała sobie ich imiona w dwóch sercach. Bardzo trwała decyzja.",
    "kawiarnia": "Roy szybko trafił do więzienia, więc w wieku dziewiętnastu lat była kelnerką, wciąż nosiła jego obrączkę i czekała, aż wydarzy się coś ekscytującego.",
    "kuchnia": "W styczniu 1930 roku poznała Clyde'a w kuchni przyjaciółki i wreszcie wydarzyło się coś ekscytującego: kilka tygodni później go aresztowano.",
    "waco_przed": "Bonnie przemyciła pistolet do więzienia w Waco.",
    "waco": "Clyde uciekł, a tydzień później znów go złapano, w Ohio.",
    "eastham": "Tym razem trafił do Eastham, jednej z najcięższych farm więziennych w Teksasie.",
    "eastham_rura": "Tam inny więzień napadał go raz za razem, aż Clyde zabił go rurą. To było pierwsze życie, które odebrał.",
    "palce": "Żeby nie pracować w polu, Clyde pozwolił, żeby siekiera spadła mu na stopę.",
    "parol": "Sześć dni później i tak wyszedł warunkowo.",
    "przysiega": "Przysiągł, że raczej zginie, niż wróci, ale jak zostać na wolności, kiedy każdy policjant w Teksasie zna twoją twarz?",
    "po_bramie": "Bonnie czekała pod bramą z włączonym silnikiem, a tym razem mieli plan: nie zatrzymywać się.",
    "akt2": "Plan Clyde'a był prosty: ukraść szybkie auto, napadać na małe miejsca z niewielką gotówką i bez ochrony, i jechać dalej.",
    "stacja": "Większość ich napadów to stacje benzynowe i sklepy spożywcze, a wiele dawało tylko kilka dolarów.",
    "kaufman": "Ich pierwszym dużym planem był napad na sklep żelazny po broń, ale auto ugrzęzło w błocie, więc próbowali uciec na kradzionych mułach.",
    "cela": "Bonnie złapano i spędziła dwa miesiące w areszcie, gdzie napisała długi wiersz o dziewczynie wyjętej spod prawa, Suicide Sal.",
    "hillsboro": "Kiedy siedziała zamknięta, jeden z napadów Clyde'a w Hillsboro poszedł źle i zastrzelono sklepikarza Johna Buchera.",
    "matka_obietnica": "Kiedy ława przysięgłych puściła Bonnie, obiecała matce, że będzie się trzymać z dala od Clyde'a, i dotrzymała obietnicy przez kilka tygodni.",
    "atoka": "Tego sierpnia, na wiejskiej potańcówce w Oklahomie, gang Clyde'a zastrzelił zastępcę szeryfa Eugene'a Moore'a i teraz szukano ich za zabicie stróża prawa.",
    "wd": "Wkrótce dołączył do nich szesnastoletni chłopak z sąsiedztwa, W.D. Jones, głównie dlatego, że brzmiało to ekscytująco.",
    "buck": "W marcu 1933 roku starszy brat Clyde'a, Buck, został ułaskawiony i razem z żoną Blanche przyjechał na coś, co miało być krótką wizytą rodzinną.",
    "joplin_dom": "Wynajęli mieszkanie nad garażem w Joplin w Missouri, gdzie we piątkę bardzo starali się wyglądać na zwykłą rodzinę.",
    "joplin_karty": "Grali w karty, pili i kłócili się tak głośno, że sąsiedzi wezwali policję, myśląc, że to przemytnicy alkoholu. Kto naprawdę czekał za tymi drzwiami?",
    "joplin_walka": "13 kwietnia 1933 roku dwóch funkcjonariuszy podeszło do garażu, a gang odpowiedział ogniem z okien.",
    "joplin_ofiary": "Detektyw Harry McGinnis i konstabl Wes Harryman zginęli, a gang uciekł w takim pośpiechu, że zostawił prawie wszystko.",
    "joplin_rzeczy": "Pamiętasz ten aparat? Leżał na podłodze obok ich broni, ubrań i jednego z wierszy Bonnie.",
    "ciemnia": "Joplin Globe wywołał kliszę i nagle kraj pogrążony w Wielkim Kryzysie miał zdjęcia swoich nowych ulubionych złoczyńców.",
    "kiosk": "Ludzie, którzy stracili pracę i farmy na rzecz banków, kupowali każde wydanie, bo tym dwojgu najwyraźniej żyło się dużo lepiej.",
    "cygaro_zlosc": "Bonnie lubiła rozgłos, ale nie znosiła, kiedy nazywano ją palaczką cygar, bo paliła wyłącznie papierosy.",
    "darby_auto": "Dwa tygodnie później w Luizjanie ukradli auto, a jego właściciel, młody Dillard Darby, ruszył za nimi w pościg z przyjaciółką, Sophią Stone.",
    "darby_tyl": "To gang złapał ich i zabrał ze sobą, a kiedy Bonnie zapytała Darby'ego, czym się zajmuje, odpowiedział, że jest przedsiębiorcą pogrzebowym.",
    "darby_smiech": "Podobno Bonnie się roześmiała i powiedziała, że pewnego dnia może będzie musiał zająć się nią.",
    "darby_puszczeni": "Później wypuścili oboje zakładników pod Waldo w Arkansas i nawet dali im pięć dolarów na powrót do domu.",
    "teczka_zasiew": "Nikt z nich jeszcze nie wiedział, że każdy z tych wycinków trafi do jednej teczki, na biurko człowieka, który w końcu ich złapie.",
    "plakaty": "Na razie ich twarze wisiały na listach gończych w pięciu stanach. Co się dzieje, kiedy najsłynniejszy kierowca ucieczek w Ameryce przegapi znak drogowy?",
    "wellington_noc": "W czerwcu 1933 roku pod Wellington w Teksasie Clyde jechał nocą szybko i przegapił znaki, że most przed nim jest rozebrany.",
    "wellington_bonnie": "Auto zapaliło się od wyciekającej benzyny i tak poparzyło nogę Bonnie, że już nigdy nie chodziła normalnie.",
    "farma": "Rodzina farmerów przyjęła ich i próbowała pomóc, ale ktoś zadzwonił po szeryfa i przyjechało dwóch stróżów prawa.",
    "drzewo": "Gang wziął obu jako zakładników, przewiózł ich przez granicę do Oklahomy i zostawił przywiązanych drutem kolczastym do drzewa.",
    "noszenie": "Przez kolejne tygodnie Clyde nosił Bonnie na rękach, bo nie mogła już sama ustać.",
    "oboz": "Tak wyglądało wspaniałe życie wyjętych spod prawa: spanie w kradzionych autach, zimna fasola z puszki i mycie się w rzekach.",
    "rzeka": "Bonnie wciąż starała się wyglądać jak gwiazda filmowa, nawet kiedy jej jedynym lustrem była zimna rzeka.",
    "list_ford": "Clyde wolał kradzione Fordy, a sam Henry Ford dostał nawet list z podziękowaniem za tak świetne auto do ucieczek, choć nikt nie wie na pewno, czy napisał go Clyde.",
    "platte": "W lipcu 1933 roku policja otoczyła ich dwa domki motelowe pod Platte City w Missouri i przywiozła nawet opancerzone auto; gang przebił się ogniem, ale Buck dostał w głowę, a odłamki szkła oślepiły Blanche na jedno oko.",
    "dexfield": "Kilka dni później, w parku w Iowie, obława policjantów i farmerów znalazła ich obóz; umierającego Bucka złapano, a Blanche nie chciała go zostawić.",
    "przeprawa": "Clyde, Bonnie i W.D. przeszli w bród rzekę i uciekli, ranni, prawie bez niczego.",
    "wd_odchodzi": "Wkrótce nawet W.D. Jones wymknął się nocą i wrócił do matki.",
    "rodziny": "Bonnie i Clyde też wracali do domu, na swój sposób: co kilka tygodni spotykali rodziny na ciemnych polnych drogach pod Dallas, przywozili pranie i zabierali domowe jedzenie.",
    "sowers": "W listopadzie szeryf z Dallas urządził zasadzkę na jeden z tych rodzinnych pikników i oboje uciekli z kulami w nogach. Dlaczego po prostu nie przestali?",
    "odbicie": "Zamiast tego w styczniu 1934 roku Clyde wrócił do Eastham uwolnić przyjaciół, a Bonnie trąbiła we mgle, żeby ich prowadzić.",
    "straznik": "Uciekło pięciu więźniów, ale strażnik Joe Crowson został postrzelony i później zmarł.",
    "simmons": "Szef teksańskich więzień, Lee Simmons, wziął to do siebie i zaczął szukać jednego konkretnego człowieka.",
    "hamer": "Frank Hamer był emerytowanym Strażnikiem Teksasu, który przeżył dziesiątki strzelanin, a w lutym 1934 roku po cichu przyjął to zlecenie.",
    "poscigi": "Policja pięciu stanów ścigała Bonnie i Clyde'a od dwóch lat, a te pościgi zwykle kończyły się tak samo: radiowozem w rowie.",
    "hak_szuflada": "Hamer zrobił więc coś, czego nikt się nie spodziewał: przestał ich ścigać.",
    "hak_teczka": "Zamiast tego usiadł z tą teczką wycinków z gazet i mapą i czekał, aż popełnią jeden błąd.",
    "podkreslenie": "Dwa razy podkreślił jedno zdanie, które gazety podobno przytoczyły za Clyde'em po Eastham: nigdy tam nie wróci. To znaczyło, że nigdy się nie podda, a pytanie brzmi tylko: gdzie.",
    "dzien1": "Pierwszego dnia Hamer ruszył w drogę, nie za nimi, ale przez każde miasto, w którym już byli.",
    "hamer_motel": "Wszędzie, gdzie dotarł, ktoś ich pamiętał: kulejącą dziewczynę, młodego mężczyznę w kapeluszu, nowego Forda i stos pustych puszek.",
    "dzien20": "Do dwudziestego dnia zrozumiał ich główny trik: w tamtych czasach policja rzadko mogła ścigać auto przez granicę stanu, więc Clyde po prostu wjeżdżał do następnego stanu.",
    "mapa": "Hamer przestał więc zaznaczać, gdzie byli, i zaczął zaznaczać, dokąd ciągle wracali.",
    "petle": "Pętle zawsze biegły wzdłuż granic stanów i prędzej czy później każda prowadziła do domu, do ich matek. Jak długo Hamer będzie musiał czekać?",
    "grapevine": "Pięćdziesiątego dnia polowania Hamera, w Niedzielę Wielkanocną 1934 roku, dwóch młodych policjantów drogówki zatrzymało się pod Grapevine w Teksasie, żeby pomóc autu, które wzięli za zepsute.",
    "grapevine_cien": "Zastrzelono ich, zanim zdążyli wyciągnąć broń.",
    "tullis": "Jeden z nich, H.D. Murphy, miał w tym miesiącu poślubić swoją ukochaną, Maree Tullis, a miejscowi historycy mówią, że przyszła na jego pogrzeb w sukni ślubnej.",
    "gazety_zle": "Gazety pisały, że Bonnie śmiała się nad umierającym, co raczej nie było prawdą, ale po Grapevine nikt już im nie kibicował.",
    "listy_gon": "Na całym Południu wyznaczono nagrody i odtąd każdy farmer ze strzelbą wypatrywał na drodze kradzionego Forda.",
    "commerce": "Pięć dni później, pod Commerce w Oklahomie, ich auto znów zsunęło się do rowu, a dwóch stróżów prawa podeszło pomóc.",
    "commerce_cien": "Clyde zabił konstabla Cala Campbella i wziął komendanta policji, Percy'ego Boyda, jako zakładnika.",
    "boyd": "Godzinami wozili Boyda, a zanim wypuścili go w Kansas, Bonnie dała mu jedną wiadomość dla gazet.",
    "boyd_tab": "Nie to, że jest niewinna, i nie to, że żałuje, tylko to, że Bonnie Parker nie pali cygar.",
    "prasa_cygaro": "Gazety wydrukowały i to, a jedna z nich trafiła na biurko Hamera, obok mapy, która w końcu była pełna, ale wciąż potrzebował kogoś, kto poda mu dzień.",
    "methvin": "Hamer znalazł tego kogoś w Ivym Methvinie, ojcu Henry'ego Methvina, młodego więźnia, którego uwolnili w Eastham: pomóż zastawić pułapkę, a twój syn zostanie ułaskawiony.",
    "wiersz": "Mniej więcej wtedy Bonnie dała matce nowy wiersz, w którym pisała, że pewnego dnia zginą z Clyde'em razem i zostaną pochowani obok siebie.",
    "pozegnanie": "Potem pojechali dalej, bo auto było jedynym domem, jaki im został.",
    "henry_wsiada": "Na drodze pod Shreveport zabrali jednego z więźniów z Eastham, chłopaka o imieniu Henry Methvin.",
    "shreveport": "21 maja Henry Methvin rozdzielił się z Bonnie i Clyde'em w Shreveport, a Hamer wiedział, dokąd pójdzie: do domu, na farmę ojca, gdzie będą go szukać.",
    "noc": "W nocy z 22 maja Hamer i pięciu innych stróżów prawa ukryli się w krzakach przy polnej drodze w Luizjanie i czekali tam do świtu, w ciszy odganiając komary.",
    "posse": "Hamer wziął swojego dawnego partnera Manny'ego Gaulta, dwóch zastępców szeryfa z Dallas, którzy znali Clyde'a z widzenia, Boba Alcorna i Teda Hintona, oraz miejscowego szeryfa Hendersona Jordana z zastępcą, Prentissem Oakleyem.",
    "zasadzka_rano": "Rano sto drugiego dnia, 23 maja, ciężarówka Ivy'ego Methvina stała przy drodze na lewarku jako przynęta.",
    "kanapka": "Clyde prowadził w samych skarpetkach, a Bonnie jadła kanapkę z kawiarni w miasteczku.",
    "dym": "Stróże prawa oddali ponad sto strzałów w kilka sekund i było po wszystkim, zanim Clyde zdążył sięgnąć po broń.",
    "pamiatki": "W ciągu kilku godzin tysiące ludzi zjechały do miasteczka Arcadia, a łowcy pamiątek obcinali kosmyki włosów Bonnie i kawałki jej sukienki.",
    "darby_zaklad": "A według miejscowych relacji przedsiębiorca pogrzebowy, z którego Bonnie śmiała się rok wcześniej, pomagał przygotować jej ciało.",
    "pogrzeby": "Jej wiersz trafił prawie we wszystko poza ostatnim wersem: matka nie zgodziła się na wspólny grób, więc pochowano ich na różnych cmentarzach.",
    "auto_jarmark": "Nawet ich podziurawione kulami auto ruszyło w trasę, a ludzie płacili, żeby obejrzeć je na jarmarkach w całym kraju.",
    "blanche_po": "Blanche odsiedziała sześć lat w więzieniu i żyła spokojnie do 1988 roku, jako jedyna z tej czwórki dożyła starości.",
    "hamer_ganek": "Hamer rzadko mówił o tamtym poranku i nigdy nie napisał o nim książki.",
    "film_hamer": "Trzydzieści lat później hollywoodzki przebój pokazał Bonnie i Clyde'a jako młodych i pięknych, a Hamera jako schwytanego i upokorzonego przez gang, czego nigdy nie było, więc jego rodzina pozwała wytwórnię.",
    "gra": "A w 2026 roku nowa gra wideo zbudowała swoich bohaterów na tym samym starym romansie.",
    "koniec": "Prawdziwi Bonnie i Clyde byli dwójką biednych dzieciaków z Dallas, po których zostało co najmniej dziewięciu zabitych stróżów prawa; gazety zrobiły z nich legendy, a cierpliwy człowiek, czytający ich teczkę, ich powstrzymał.",
    "dzieki": "Dziękuję za obejrzenie! Jeśli lubisz moje filmy, wesprzyj mnie, a ja postaram się jak najlepiej.",
}


def czytaj_wav(p):
    with wave.open(str(p)) as f:
        sr, n, ch, sw = f.getframerate(), f.getnframes(), f.getnchannels(), f.getsampwidth()
        a = np.frombuffer(f.readframes(n), {2: np.int16, 4: np.int32}[sw]).astype(np.float32)
    return a.reshape(-1, ch).mean(axis=1), sr


def glos(p):
    """(pierwszy dźwięk, ostatni dźwięk, [środki pauz]) w sekundach nagrania — ramki 20 ms, cisza 35 dB pod szczytem."""
    a, sr = czytaj_wav(p)
    hop = int(sr * 0.02)
    n = len(a) // hop
    rms = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms / rms.max())
    gl = db > -35
    idx = np.flatnonzero(gl)
    t0, t1 = idx[0] * 0.02, (idx[-1] + 1) * 0.02
    pauzy, bieg = [], None
    for i in range(idx[0], idx[-1] + 1):
        if not gl[i] and bieg is None:
            bieg = i
        elif gl[i] and bieg is not None:
            if (i - bieg) * 0.02 >= 0.14:
                pauzy.append((bieg + i) / 2 * 0.02)
            bieg = None
    return t0, t1, pauzy


def zdania(txt):
    """Zdania (po kropce, pytajniku, wykrzykniku); zdanie krótsze niż 30 znaków dołącza do poprzedniego."""
    out = []
    for z in re.split(r"(?<=[.?!])(?<!p\.n\.e\.)(?<!\d\.)(?<![A-Z]\.[A-Z]\.)\s+", txt.strip()):  # „W.D. Jones”, „H.D. Murphy”  # „660 roku p.n.e.”, „126. cesarz” to nie koniec zdania
        if out and (len(z) < 30 or len(out[-1]) < 30) and len(out[-1]) + 1 + len(z) <= NAPIS:
            out[-1] += " " + z
        else:
            out.append(z)
    return out


def rowno(zd):
    return rowno_n(zd, -(-len(zd) // NAPIS))


def rowno_n(zd, n):
    """Zdanie na najmniej napisów po najwyżej NAPIS znaków, możliwie równych; cięcie najchętniej po przecinku,
    dwukropku albo średniku, a nigdy przed jednym-dwoma ostatnimi słowami."""
    slowa = zd.split()
    if n == 1 and miesci(zd):
        return [zd]
    cel = len(zd) / n
    m = len(slowa)
    dl = lambda i, j: len(" ".join(slowa[i:j]))
    best = {(0, 0): (0.0, [])}  # (słów zużytych, napisów) → (koszt, granice)
    for k in range(n):
        for (i, kk), (koszt, gr) in list(best.items()):
            if kk != k:
                continue
            for j in range(i + 1, m + 1):
                L = dl(i, j)
                if L > NAPIS:
                    break
                if not miesci(" ".join(slowa[i:j])):
                    continue
                ostatni = k == n - 1
                if ostatni != (j == m):
                    continue
                kara = ((L - cel) / 10) ** 2
                if not ostatni:
                    kara += koszt_ciecia(slowa[j - 1], slowa[j]) * 3
                    kara += 40 if m - j <= 2 else 0
                c = (koszt + kara, gr + [j])
                if (j, k + 1) not in best or c[0] < best[(j, k + 1)][0]:
                    best[(j, k + 1)] = c
    if (m, n) not in best:  # nie da się na n napisów po dwa wiersze: o jeden więcej
        return rowno_n(zd, n + 1)
    _, gr = best[(m, n)]
    return [" ".join(slowa[a:b]) for a, b in zip([0] + gr[:-1], gr)]


def podziel(txt):
    """Napisy po najwyżej NAPIS znaków: zdanie po zdaniu, długie zdanie na równe kawałki (rowno)."""
    return [c for zd in zdania(txt) for c in rowno(zd)]


# słowa, przed którymi dobrze zaczyna się nowy wiersz (spójniki, zaimki względne), i takie, po których nie wolno
# łamać (przedimki, przyimki, spójniki na końcu wiersza)
PRZED = set("and but so which who whose when where while because that as until though or nor "
            "i a ale bo więc który która które którego której którzy kiedy gdzie aż żeby że czyli choć gdy".split())
NIE_PO = set("the a an of to in on at by for from with into his her its their and so that "
             "w we z ze i a na do o od po za u przy dla przez pod nad bez jak jego jej się".split())


def koszt_ciecia(przed, po):
    """Kara za złamanie wiersza albo napisu między słowami przed | po (0 — po przecinku, kropce, dwukropku)."""
    if re.fullmatch(r"(?:[A-Z]\.)+,?", przed) and not przed.endswith(","):  # „W.D. | Jones”, „H.D. | Murphy” — inicjały z nazwiskiem
        return 12
    if re.fullmatch(r"\d+\.?", przed) or przed.lower() in ("hundred", "thousand"):  # „127 | lat”, „126. | cesarz”
        return 12
    if przed[-1] in ",.;:?!":
        return 0
    if przed.lower() in NIE_PO:
        return 12
    return 2 if po.lower().strip("„'") in PRZED else 5


def _ciecia(txt):
    """Spacje, po których oba wiersze mają najwyżej WIERSZ znaków."""
    return [m.start() for m in re.finditer(" ", txt) if m.start() <= WIERSZ and len(txt) - m.start() - 1 <= WIERSZ]


def miesci(txt):
    return len(txt) <= WIERSZ or bool(_ciecia(txt))


def wiersze(txt):
    """Dwa wiersze po najwyżej WIERSZ znaków, możliwie równe; najchętniej po przecinku."""
    if len(txt) <= WIERSZ:
        return txt
    i = min(_ciecia(txt), key=lambda s: abs(s - len(txt) / 2) / 3 + 2 * koszt_ciecia(txt[:s].split()[-1], txt[s + 1:].split()[0]))
    return txt[:i] + "\n" + txt[i + 1:]


def tc(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def kwestie(jezyk):
    """[(start w filmie, koniec, tekst, klucz)] — jeden wpis na kwestię lektora."""
    os.environ["JEZYK"] = "en"
    import dane
    out, t = [], 0.0
    for u in dane.ujecia():
        klucz, sec, snd = u[2], u[5], u[7]
        en = dane.kwestia(snd)
        if en:
            meta = json.loads((LEKTOR / f"{klucz}.json").read_text(encoding="utf-8"))
            assert meta["text"] == en, f"{klucz}: nagranie z innym tekstem"
            start = t + dane.okno_kwestii(snd, klucz in dane.HAK)[0]
            g0, g1, pauzy = glos(LEKTOR / f"{klucz}.wav")
            if jezyk == "pl" and klucz not in NAPISY_PL:
                raise SystemExit(f"brak polskiego napisu dla kwestii „{klucz}” (NAPISY_PL)")
            txt = en if jezyk == "en" else NAPISY_PL[klucz]
            out.append((start + g0, start + g1, txt, [start + p for p in pauzy]))
        t += sec
    return out


def srt(jezyk):
    wpisy = []
    for a, b, txt, pauzy in kwestie(jezyk):
        czesci = podziel(txt)
        dl = sum(len(c) for c in czesci)
        granice, acc = [a], 0
        for c in czesci[:-1]:
            acc += len(c)
            cel = a + (b - a) * acc / dl
            blisko = [p for p in pauzy if abs(p - cel) < 0.9 and p > granice[-1] + 0.6]
            granice.append(min(blisko, key=lambda p: abs(p - cel)) if blisko else cel)
        granice.append(b)
        for n, c in enumerate(czesci):
            wpisy.append([granice[n], granice[n + 1], c])
    for n, w in enumerate(wpisy):  # chwila po ostatnim słowie, ale bez nachodzenia na następny napis
        nast = wpisy[n + 1][0] if n + 1 < len(wpisy) else w[1] + 2
        if n + 1 == len(wpisy) or wpisy[n + 1][0] - w[1] > 0.3:
            w[1] = min(w[1] + PO_GLOSIE[jezyk], nast - 0.05)
        else:
            w[1] = nast - 0.02 if nast - w[1] < 0.5 else w[1]
    return "".join(f"{n + 1}\n{tc(a)} --> {tc(b)}\n{wiersze(txt)}\n\n" for n, (a, b, txt) in enumerate(wpisy)), wpisy


def main():
    OUT.mkdir(exist_ok=True)
    for jez in ("en", "pl"):
        tekst, wpisy = srt(jez)
        p = OUT / f"{NAZWA}_{jez}.srt"
        p.write_text(tekst, encoding="utf-8")
        dlugie = [w[2] for w in wpisy if len(w[2]) > NAPIS]
        krotkie = [w for w in wpisy if w[1] - w[0] < 1.0]
        print(f"{p.name}: {len(wpisy)} napisów, ostatni do {tc(wpisy[-1][1])}; za długie: {len(dlugie)}, krótsze niż 1 s: "
              f"{len(krotkie)}")


if __name__ == "__main__":
    main()
