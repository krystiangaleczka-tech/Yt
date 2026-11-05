# Sekwencja, świat i ciągłość

Ujęcie nie bierze się z niczego. Wynika z **wcześniejszych wydarzeń** i **stanu świata**, a jego skutki muszą być
widoczne później. Dlatego każdy film ma **księgę świata** (Continuity Editor → Świat), a aplikacja sprawdza ją
z planem ujęć bez udziału AI.

## Odwołania do ujęć

`dNN_KK` — jednostka NN (akt w kolejności filmu, od 1) i ujęcie KK w niej (od 1, z kartą tytułową włącznie).
Prolog (np. gotowe zimne otwarcie wewnątrz pierwszego aktu) to jednostka 0: `prologue: {"1": 14}`.
Można odwoływać się do jednostek, których plan jeszcze nie powstał — wtedy liczy się kolejność.

## Działy księgi

| Dział | Pola | Po co |
|---|---|---|
| `places` | id, name, floor, wing, connects, note | jeden plan budynku dla scenariusza i rysunku |
| `characters` | name, aliases, role, look, costume, traits, party, joins, leaves, namedIn | kostiumy, kto jest w grupie (do zasobów), imiona jednoznaczne |
| `props` | name, owner, place, seeded, uses | rekwizyt pokazany zanim zostanie użyty |
| `resources` | name, unit, perPersonDay, start, changes (delta albo share), claims | bilans wody, jedzenia, baterii; liczby w kwestiach |
| `rules` | id, name, from, to, note | co działa w jakim przedziale (prąd, linia telefoniczna, zamki) |
| `events` | at, needs, needsOff, note | zdarzenie wymaga zasady (telefon dzwoni → linia wolna) |
| `threads` | title, setup, clues, payoff, open | zasiew → wskazówki → rozwiązanie |
| `spoilers` | pattern, notBefore, why | czego lektor i postacie nie mogą powiedzieć przed danym ujęciem |
| `decisions` | id, text, at, by | decyzje reżysera, które zmieniły świat |
| `tempo` | minSeconds, maxSeconds, maxVoiceShare | zakres długości jednostki, udział lektora |

## Co sprawdza kontrola

Waga 3 psuje logikę, 2 widz wyłapie, 1 drobne.

- wątek: rozwiązanie bez zasiewu, rozwiązanie przed zasiewem (3); wskazówka poza wątkiem (2); zasiew bez rozwiązania (1);
- rekwizyt użyty przed pokazaniem albo nigdy niepokazany (3);
- zdarzenie sprzeczne z zasadą świata w tej chwili (3);
- zasób poniżej zera, liczba w kwestii niezgodna z bilansem (3);
- imię użyte dla innej postaci albo przed czasem (3);
- kwestia zdradzająca coś przed czasem (3);
- odwołanie do nieistniejącego ujęcia (2);
- jednostka poza zakresem długości (2), seria ujęć tej samej długości, za dużo lektora (1), scena bez planu (1).

## Kolejność pracy nad sekwencją

1. Przeczytaj wejście jednostki z księgi (otwarte wątki, zasoby, kto gdzie jest, kto co wie).
2. Rozpisz beaty z przyczyną; zapisz, co jednostka zmienia w świecie.
3. Rozpisz ujęcia; każde ma wydarzenie (rozdział „Rytm”).
4. Uzupełnij księgę (zasiewy, użycia, zmiany zasobów, zdarzenia).
5. Uruchom kontrolę i popraw do zera błędów wagi 3.
6. Dopiero teraz wykonuj ujęcia.

Narzędzia wgrywające ujęcia do Studio odmawiają pracy nad jednostką, która ma błędy wagi 3 (chyba że reżyser
świadomie wymusi i zostanie to zapisane w dzienniku).
