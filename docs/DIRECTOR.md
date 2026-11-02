# Reżyseria AI: beaty, napięcie i plan montażowy

## Miejsce w procesie

W **DocOS Studio** etap `Reżyseria i napięcie` znajduje się pomiędzy **Planem scen** a **Scenami / Canvas**.
Rozdziela literacki opis wydarzenia od sposobu jego przedstawienia. Zachowuje dotychczasowy
edytor scen, generator ujęć, timeline i montaż.

1. Zatwierdź Master Story, akty, sekwencje, scenariusz oraz plan scen.
2. Otwórz **Reżyseria i napięcie**; wybierz scenę i tryb (automatyczny, z wytycznymi, ręczny).
3. Użyj **Zaplanuj scenę** lub **Zaplanuj brakujące sceny**. Plan powstaje lokalnie z opisu, bez wymagania zewnętrznego LLM.
4. Alternatywnie wybierz wzorzec z biblioteki i uruchom **Wygeneruj bardziej filmowo przez AI**.
5. Dostosuj mapę napięcia 0–10, cel i wiedzę postaci/widza w każdym beacie; dostosuj ujęcia i długości pasków montażowych.
6. **Zatwierdź reżyserię**, a potem **Utwórz ujęcia z planu**. Ujęcia są tworzone w istniejącym modelu scen, a nie w osobnym fikcyjnym timeline.

## Model danych

Wszystkie dane w projekcie: `legacy.production_flow.director`. Cały plan filmu (Story Bible, Master Story,
akty, sekwencje, plan scen i reżyseria) zapisuje się wyłącznie przez `PUT /api/projects/{id}/flow`
(`expected_revision` + `flow`). Endpoint waliduje kształt i limity (`studio_core/production_flow.py`),
zmienia tylko `legacy.production_flow`, zwraca 409 przy nieaktualnej rewizji i trafia do historii Cofnij.
Ogólny `PATCH /api/projects/{id}` celowo nie przyjmuje `legacy`.

- `mode`: `auto | guided | manual`
- `plans[outlineId]`: sourceSignature, patternId, mode, notes, beats[], shots[]
- `customPatterns[]`: wzorce własne dla tego projektu.

Beat: `goal, tensionBefore, tensionAfter, viewerKnows, characterKnows, soundCue, patternId`.
Shot: `beatId, typeId, title, description, duration, transition, sound`. Długości są w **sekundach**,
a istniejące sceny używają **klatek** (konwersja z FPS podczas przenoszenia).
Zatwierdzenie `approved.direction` zawiera podpis całego planu i zatwierdzonych scen.
Podpisy to krótkie skróty (`v2:…`) liczone z JSON o posortowanych kluczach, więc nie kopiują
całej historii do `project.json` i nie zależą od kolejności pól po zapisie.

`sceneSourceSignature` zawiera wybrany outline, sekwencję, akt, jego scenariusz,
Story Bible i Master Story. Po ich zmianie plan staje się nieaktualny (⚠ na liście scen).
Możesz go przeliczyć albo — jeśli zmiana nie wpływa na rytm — kliknąć **Plan nadal pasuje —
oznacz jako aktualny** (lub zbiorczo **Zachowaj wszystkie nieaktualne plany**). Zmiana
któregokolwiek ujęcia unieważnia zatwierdzenie reżyserii.

## Zasady bezpieczeństwa materiałów

- AI zwraca **wyłącznie propozycję**. Endpoint `POST /api/projects/{id}/flow/ai/direction/generate`
  niczego nie zapisuje. Odpowiedź jest najpierw walidowana, a zapis przez endpoint flow odbywa się
  tylko, gdy opis sceny nie zmienił się w trakcie generowania. Zastąpienie istniejącego planu
  (AI lub „Przelicz”) wymaga potwierdzenia; **Cofnij ostatnią zmianę** przywraca poprzednią wersję.
- AI dostaje opis wybranej sceny, kontekst historii, plany sąsiednich scen i własne wzorce projektu,
  a nie shot listy całego filmu.
- Odpowiedź AI jest walidowana: maksymalnie 24 beaty, 90 ujęć, znane typy ujęć,
  dodatnie długości i połączenia shot → beat.
- Generowanie brakujących planów nie nadpisuje istniejących, nawet nieaktualnych.
- Przeniesienie planów do scen idzie w kolejności filmu (akt → sekwencja → scena) i
  **pomija outline z istniejącymi ujęciami** oraz akty zaimportowane bezpośrednio ze scenariusza,
  zachowując ręczne korekty, narzędzia i materiały. Jeśli wszystkie outline mają ujęcia,
  operacja jest zatrzymywana, a nie tworzy duplikatów.
- Zmiana opisów scen, beatów i planów nie usuwa już wygenerowanych kadrów.
  Po transferze do scen edytuj je w zwykłym edytorze.
- Biblioteka wzorców jest katalogiem propozycji, a nie automatyczną prawdą montażową.
  Szybki montaż naprzemienny jest jedną z metod; długi nieruchomy kadr może działać lepiej.

## Biblioteka

`apps/studio/src/directorTypes.ts` zawiera katalog typów ujęć i montażowych wzorców:
Rapid Intercutting, Shot/Reverse Shot, Slow Burn, Jumpscare, False Relief,
Delayed Reveal, Investigation, Chase, Parallel Action, Aftermath, Emotional Pause,
Visual Exposition, Evidence Montage, Anticipation/Payoff.

Własne wzorce są zapisywane w aktualnym filmie i można je edytować (nazwa, cel, kiedy użyć,
rytm, sekwencja ujęć, krzywa napięcia). Katalog otwiera się z zakładki
**Biblioteka wzorców i ujęć** na ekranie reżyserii. Wbudowane wzorce i 16 rodzajów ujęć są
dostępne w każdym projekcie.

## Zakres

Obecny etap produkuje plan reżyserski i osobne ujęcia w modelu aplikacji, nie renderuje automatycznie
animacji z gotowych plików. Kontrolę jakości klatek, tworzenie assetów i audio pozostawiono
istniejącym modułom produkcyjnym.
