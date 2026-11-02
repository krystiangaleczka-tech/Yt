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

Wszystkie dane w projekcie: `legacy.production_flow.director`:
- `mode`: `auto | guided | manual`
- `plans[outlineId]`: sourceSignature, patternId, mode, notes, beats[], shots[]
- `customPatterns[]`: wzorce własne dla tego projektu.

Beat: `goal, tensionBefore, tensionAfter, viewerKnows, characterKnows, soundCue, patternId`.
Shot: `beatId, typeId, title, description, duration, transition, sound`. Długości są w **sekundach**,
a istniejące sceny używają **klatek** (konwersja z FPS podczas przenoszenia).
Zatwierdzenie `approved.direction` zawiera podpis całego planu i zatwierdzonych scen.

`sceneSourceSignature` zawiera wybrany outline, sekwencję, akt, jego scenariusz,
Story Bible i Master Story. Po ich zmianie plan staje się nieaktualny. Zmiana
któregokolwiek ujęcia unieważnia zatwierdzenie reżyserii.

## Zasady bezpieczeństwa materiałów

- AI zwraca **wyłącznie propozycję**. Endpoint `POST /api/projects/{id}/flow/ai/direction/generate`
  niczego nie zapisuje. Dopiero świadoma akcja użytkownika przez PATCH zapisuje plan.
- Odpowiedź AI jest walidowana: maksymalnie 24 beaty, 90 ujęć, znane typy ujęć,
  dodatnie długości i połączenia shot → beat.
- Generowanie brakujących planów nie nadpisuje istniejących, nawet nieaktualnych.
- Przeniesienie planów do scen **pomija outline z istniejącymi ujęciami**,
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

Własne wzorce są zapisywane w aktualnym filmie. Katalog otwiera się z zakładki
**Biblioteka wzorców i ujęć** na ekranie reżyserii.

## Zakres

Obecny etap produkuje plan reżyserski i osobne ujęcia w modelu aplikacji, nie renderuje automatycznie
animacji z gotowych plików. Kontrolę jakości klatek, tworzenie assetów i audio pozostawiono
istniejącym modułom produkcyjnym.
