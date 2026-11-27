# Recenzja jednostki (dnia)

Po każdej jednostce recenzent przechodzi listę i zapisuje wynik w Continuity Editor → Recenzje. Recenzja ma podpis
treści: każda późniejsza zmiana ujęć, scenariusza jednostki albo powiązanych wpisów księgi ją unieważnia.

| Punkt | Pytanie |
|---|---|
| **Scenariusz** | Czy ujęcia opowiadają to, co mówi scenariusz jednostki i Master Story? Czy nic ważnego nie wypadło (wskazówki!)? |
| **Chronologia** | Czy pora dnia, kolejność i czas trwania zdarzeń się zgadzają z poprzednimi jednostkami? |
| **Beaty** | Czy każdy beat ma przyczynę i skutek; czy napięcie rośnie do kulminacji? |
| **Tempo** | Czy długości wynikają z treści (rozdział „Rytm”), jednostka mieści się w zakresie, sąsiednie ujęcia się różnią? |
| **Narracja** | Czy lektor dopowiada, a nie opisuje; czy nie zdradza niczego przed czasem; czy jest cisza tam, gdzie trzeba? |
| **Ciągłość** | Czy automatyczna kontrola nie ma błędów wagi 3; czy księga świata opisuje, co jednostka zmienia? |
| **Pary cięć** | Czy każde ujęcie n wynika z n−1 i prowadzi do n+1 (miejsce, pora dnia, kto gdzie jest i co trzyma)? Gdzie wynikanie się rwie, jest pomost (Wytyczne 3.1, „Pary cięć”)? |
| **Kadr** | Czy każde ujęcie przeszło Wytyczne ujęć (otwory, ciało, głębia, koniec świata) i ma wydarzenie, które kończy się na oczach widza? Czy są w nim właściwe postacie i rekwizyty według rozpiski, nic nie zostało z poprzedniej dekoracji, a nowa postać ma podpis? Czy każde zdarzenie ma dźwięk w tej samej chwili (`efekty.ZDARZENIA`)? Czy każda uwaga i każdy marker reżysera ma odpowiedź w obrazie (`scripts/uwagi_rezysera.py`), a poprawka rzeczy wspólnej objęła wszystkie ujęcia z tą rzeczą? |

Statusy: **robocza** → **do poprawy** (z uwagami) → **zatwierdzona**. Gdy zatwierdzona jednostka jest powiązana
wątkiem, rekwizytem albo zasadą z jednostką zmienioną później, aplikacja pokazuje „do sprawdzenia po zmianie w dniu N”.

## Przegląd scenariusza (przed rysunkiem i po każdej dużej zmianie historii)

Reżyser 18.11.2026 („Syn słońca”): „przejrzyj całą historię scenariusza i zobacz, czy jest spójna, prawdziwa z faktami,
poukładana, czy ma sens, czy widzowi się będzie podobać, czy film będzie oglądany, gdzie mogą być błędy i utraty watch
time'u — musisz odpowiedzieć na to wszystko”. Odpowiedź ma stałą formę, z kodami czasu wersji, którą się ocenia:

1. **Fakty** — tabela „gdzie (kod czasu, ujęcie) · problem · poprawka” dla błędów, które widz wytknie w komentarzach;
   potem drobniejsze; na końcu lista tego, co sprawdzone i prawdziwe (żeby było widać zakres).
2. **Spójność** — czy wprowadzenie pokazuje tego, o kim mówi; czy jest pomost między hakiem a retrospekcją; jak długo
   bohater znika z opowieści; powtórki z haka w ciele filmu (te same ujęcia i słowa); imiona na minutę.
3. **Sens** — czy pytanie z haka wraca i czy obietnice są spłacone (z kodami czasu).
4. **Czy się spodoba i czy będzie oglądany** — mocne i słabe strony; bez wymyślonych liczb utrzymania.
5. **Mapa utraty widzów** — tabela „czas · co · ryzyko (niskie / średnie / wysokie) · lek”: martwe chwile, skoki bez
   pomostu, zakończenia, które brzmią jak koniec filmu, ciągi dat i liczb.
6. **Kolejność poprawek** — numerowana lista; reżyser odpowiada skrótem („tak, wszystkie oprócz 6”). Zatwierdzone
   poprawki idą od góry: księga świata (decyzja w `decisions`) → rozpiska → ujęcia → szkic.
