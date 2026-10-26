# Tematy i Story Lock — pakiet Documentary

Etap redakcyjny przed beatami DocOS: profil kanału → propozycje tematów → research → Story Lock
→ plan beatów → narracja i shot list → audyt → lektor i montaż.
Piszącym silnikiem nadal jest Claude Code. Polecenia `topics` i `story` drukują prompty;
nie wywołują modelu ani wyszukiwarki i nie wymagają kluczy API.

## Profil i dziesięć propozycji

Z katalogu repozytorium, w istniejącym folderze docelowym:

```bash
python3 docos/docos.py channel kanal.json --name "Mój kanał"
# Ustaw w kanal.json: focus, language, narrator, wpm i published_titles.
python3 docos/docos.py topics kanal.json
```

Przekaż wydrukowany prompt Claude. Odpowiedź zapisz jako `tematy.json`: tablicę dziesięciu obiektów
z polami `title`, `subject`, `central_question`, `layers` (co najmniej trzy różne warstwy)
i `research_leads` (źródła lub instytucje do sprawdzenia).

```bash
python3 docos/docos.py save-topics kanal.json tematy.json
python3 docos/docos.py topics kanal.json
```

Zapis sprawdza kompletność, limit 60 znaków tytułu i powtórzenia. Następny prompt wyklucza
`published_titles` oraz całe `suggested_titles`. `topic_candidates` przechowuje ostatnią dziesiątkę.
Po publikacji dopisz tytuł do `published_titles`. Historia dotyczy jednego pliku profilu; nie łączy się
automatycznie między różnymi kopiami. Podobieństwo znaczeniowe i spełnienie obietnicy ocenia autor,
CLI wykrywa powtórzenia po pominięciu wielkości liter, interpunkcji i nadmiarowych odstępów.

Pomysł nie jest zweryfikowanym faktem. Sprawdź przesłankę tytułu przed jego wyborem.
Pakiet Documentary podaje cztery konstrukcje tytułów, głos narratora i łuk argumentacji.
Nie narzuca liczby pytań, wielokropków ani jednej długości filmu. Budżet wynika z `target_minutes` i `wpm`.

## Projekt i karta historii

```bash
python3 docos/docos.py new odcinek.json "Wybrany tytuł" --channel kanal.json
python3 docos/docos.py story odcinek.json
```

Nowy projekt dostaje kopię ustawień kanału i `story_lock` w stanie `DRAFT`.
Zmiany zewnętrznego profilu nie zmieniają wcześniejszych odcinków.
Wykonaj research w sieci i uzupełnij `facts`: `id`, `claim`, `status`, `source`, `url`, `note`.
Następnie uzupełnij kartę w `odcinek.json`:

| Pole | Znaczenie |
|---|---|
| `central_question` | Jedno pytanie całego filmu |
| `hook` | Konkretny sposób otwarcia |
| `signature_line` | Oryginalne zdanie wracające w finale |
| `payoff` | Odpowiedź lub końcowy wniosek |
| `recurring_detail` | Szczegół wprowadzony wcześniej i domknięty na końcu, albo `none` |
| `thesis` | Odpowiedź w jednym zdaniu |
| `key_players` | Potwierdzone osoby i organizacje, albo `none` |
| `complication` | Co sprawia, że prosta odpowiedź jest niepełna |
| `counterpoint` | Najsilniejszy uzasadniony kontrargument, albo `none` |
| `stakes_for_viewer` | Dlaczego temat dotyczy widza |
| `open_question` | Co pozostaje nieznane, albo `none` |
| `check_section` | `IN` lub `OUT`; osobna sekcja kontrargumentu, bez wymuszania sporów |
| `sting` | Powiązany następny temat albo `none` |
| `fact_ids` | Lista ID całego banku faktów dopuszczonych do narracji |
| `evidence_chain` | Od pięciu do ośmiu różnych ID z banku, w kolejności argumentacji |

Pola opisowe są tekstem, `fact_ids` i `evidence_chain` są tablicami ID, np. `['F1', 'F2']`
(w JSON stosuj podwójne cudzysłowy). Dodatkowe fakty mogą pozostać w `facts` na etapie researchu,
ale beaty mogą używać wyłącznie banku karty. Bank akceptuje `VERIFIED` i `DISPUTED`, z twierdzeniem,
źródłem i URL http(s). Dla `DISPUTED` opisz spór i stanowiska w `note`.
Samo wpisanie `VERIFIED` ani przejście walidatora nie potwierdza prawdziwości twierdzenia.

```bash
python3 docos/docos.py lock odcinek.json
python3 docos/docos.py check odcinek.json
python3 docos/docos.py system odcinek.json
python3 docos/docos.py next odcinek.json
```

`lock` zatwierdza kartę i synchronizuje `meta.thesis` oraz `meta.curiosity_gap` z kartą.
Zatwierdzona karta i pakiet trafiają do promptu globalnego oraz każdego beatu.
Autor nadal planuje i pisze beaty zwykłym workflow DocOS. `save` odrzuca użyte ID spoza banku przed zapisem.
Plik kontrolny jest sumą danych, a nie dowodem sprawdzenia stron internetowych.

W trybie prowadzonym pokaż kartę użytkownikowi przed zatwierdzeniem. Jeśli użytkownik zlecił
całość automatycznie, sprawdź źródła i zatwierdź kartę bez obowiązkowego zatrzymywania po każdym etapie.

## Zmiany i starsze odcinki

Zmiana tytułu, karty, ustawień narracji, kopii profilu lub faktów z banku unieważnia zatwierdzenie.
Polecenia `system`, `prompt`, `next`, `save` oraz eksport zawierający narrację blokują dalszy przepływ
do czasu ponownego zatwierdzenia. Eksport szkicu bez narracji pozostaje dostępny do planowania w arkuszu.
Komórki promptów takiego szkicu pokazują informację o konieczności zatwierdzenia karty.

```bash
python3 docos/docos.py unlock odcinek.json
# Popraw kartę, źródła, plan i ewentualnie wcześniejsze beaty.
python3 docos/docos.py lock odcinek.json
```

Ponowne `lock` nie przerabia napisanej narracji. Autor musi sprawdzić ją względem zmienionej karty.
Cały audyt obejmuje obietnicę tytułu, odpowiedź na pytanie, powtórzenia, źródła i domknięcie szczegółu.

Starsze projekty bez `story_lock` działają jak wcześniej. `story` pokaże kartę, którą można dodać do JSON
bez migracji pozostałych danych. `new` bez `--channel` zachowuje dotychczasowy format.
Narracja i shot list pozostają osobne; liczby mogą zostać zapisane cyframi do kontroli faktów,
a wymowę przygotowuje warstwa lektora. Render i generowanie głosu pozostają dotychczasowe.

Testy bez modeli i zależności renderera:

```bash
python3 -m unittest discover -s docos/tests -v
```
