# 2026-10-26 — tematy i Story Lock dla Documentary

## Zmiana

Przed pisaniem beatów można teraz przygotować profil kanału, wygenerować dziesięć propozycji
z promptu dla Claude oraz zatwierdzić pytanie, dowody i odpowiedź całego filmu w Story Lock.

- Dodano `docos/editorial.py` oraz polecenia `channel`, `topics`, `save-topics`, `story`, `lock`, `unlock`.
- `new --channel` kopiuje ustawienia kanału i tworzy kartę `DRAFT`.
- Historia proponowanych i opublikowanych tytułów zapobiega powtórzeniom w kolejnych listach.
- Każdy prompt beatu dostaje pakiet Documentary i zatwierdzoną kartę całego filmu.
- Bank wymaga źródeł i statusów VERIFIED/DISPUTED; spory wymagają notatki o stanowiskach.
- Zmiany karty, ustawień narracji lub faktów wymagają ponownego zatwierdzenia.
- Zapis beatu odrzuca ID faktów spoza banku przed modyfikacją projektu.
- Eksport szkicu pozostaje dostępny; eksport niezatwierdzonej narracji jest blokowany.
- Dodano instrukcję `docs/EDITORIAL.md` i uzupełniono istniejący skill oraz opisy workflow.

## Walidacja

- `python3 -m unittest discover -s docos/tests -v` — 18 testów, w tym ścieżki CLI,
  duplikaty tytułów, źródła, zmiany zatwierdzonej karty, odrzucanie zapisu i eksport/import arkusza.
- Porównanie z wersją bazową dla `projekty/bloop_v3/bloop_v4.json`: identyczny prompt globalny,
  wszystkie 12 promptów beatów, lista kontroli, scenariusz, plan renderu i wartości wszystkich siedmiu arkuszy.
- Dotychczasowy projekt The Bloop: zero uwag kontrolnych przed i po zmianie.
- `git diff --check` — bez błędów białych znaków.
- Sprawdzono metadane istniejącego skilla i odnośnik do nowej instrukcji.

## Zakres

Generowanie tematów i tekstu nadal wykonuje Claude; polecenia przygotowują prompty i zapisują dane.
Nie dodano kluczy API ani połączeń do płatnych modeli. Walidacja źródła i URL nie zastępuje researchu
i oceny prawdziwości twierdzenia. Nie zmieniono istniejącego odcinka, renderera ani lektora.
Starsze projekty bez Story Lock zachowują dotychczasowe zachowanie.
