# Warsztat pomysłów i kierunku filmu

W **Pomysł** powstaje brief, kolekcja tematów i osobna kolekcja historii dla każdego tematu. Otwarcie kafelka jest nawigacją; wybór filmu do produkcji jest osobną, jawną operacją.

## Od briefu do scenariusza

1. Wpisz obszar poszukiwań, widza, obietnicę, docelowy czas, referencje i ograniczenia. Dodaj własny pomysł lub poproś AI o propozycje.
2. Otwórz kafelek tematu. Możesz poprawić jego tytuł, pytanie, punkt widzenia i notatki. Przygotuj kilka wariantów historii, ręcznie albo z AI.
3. W każdym wariancie opisz zarys, pytanie, pierwsze 30 sekund, stawkę i finał. Perspektywa wydawcy dodaje tytuł publikacji, miniaturę, evergreen, ryzyka spalenia tematu i luki w dowodach.
4. Porównaj warianty w tabeli. Otwórz **Potencjał i metryki**, sprawdź uzasadnienie i edytuj założenia. Samo wygenerowanie oceny nie wybiera kierunku filmu.
5. Wybierz historię przyciskiem **Wybierz tę historię**. Tytuł publikacji (jeśli jest wpisany; inaczej tytuł tematu) i robocza karta Historii przyjmą jej kierunek; źródła, narracja i montaż pozostają w projekcie. Historia wymaga researchu i ponownego zatwierdzenia.
6. W **Rozdziały i podrozdziały** dodaj lub wygeneruj strukturę. Edytuj kolejność, cel, pytanie, zwrot, retencję, czas, energię i potrzebne dowody. Możesz przypisać fakty z banku.
7. **Przenieś plan do scenariusza** tworzy fragment dla każdego podrozdziału, zachowując kolejność i identyfikatory rozdziałów. W Scenariuszu widać hierarchię i można otworzyć redakcję fragmentów. Prompt całego scenariusza również uwzględnia ten plan.

Poprzedni pusty plan może zostać zastąpiony nowym. Jeśli ma już narrację lub ujęcia, aplikacja zatrzyma zmianę: przygotuj kopię projektu i przejrzyj wcześniejszą wersję. Ponowne przekazanie tego samego planu nie tworzy duplikatów. Zmianę rozwiniętego planu można przygotować w kopii wariantu; nie nadpisuje to istniejącego scenariusza automatycznie.

Przyciski Cofnij/Ponów obejmują również brief, kafelki, oceny, strukturę i wybór kierunku. Warianty oraz dane punktu odniesienia są zapisywane z projektem i trafiają do jego ZIP/XLSX/JSON. Dotychczasowe propozycje tematów są dostępne jako migrowane kafelki.

## Co oznaczają metryki

Wyniki mają służyć porównaniu hipotez redakcyjnych. Nie są gwarancją wyniku ani modelem prognozującym rekomendacje YouTube.

**Ocena redakcyjna 0–100** jest średnią pięciu subiektywnych ocen: otwarcia, dopasowania do widza, oryginalności, potencjału wizualnego i utrzymania uwagi. Evergreen ma osobną ocenę 0–100 i uzasadnienie. Wartość 50 to neutralny punkt startowy, nie wynik pomiaru. AI może zaproponować oceny, ale muszą być sprawdzone przez redaktora.

**Punkt odniesienia kanału** wpisujesz sam: wyświetlenia porównywalnych filmów po pierwszych 30 dniach, CTR, średni obejrzany procent filmu i porównywaną długość. Nie ma automatycznego połączenia z YouTube Analytics. Pole źródła danych powinno zawierać okres, zakres i powód uznania filmów za porównywalne. Liczby wyświetleń wklejaj po jednej na wiersz. Gdy nie wpiszesz typowego wyniku ręcznie, aplikacja użyje mediany listy.

**Wyświetlenia 30 dni**: typowy wynik × trzy jawne mnożniki z wariantu. Domyślnie są to 0,5× / 1× / 2×. To neutralne scenariusze robocze, które można zmienić wraz z uzasadnieniem. Bez dodatniego punktu odniesienia liczba wyświetleń pozostaje nieokreślona.

**CTR i retencja**: punkt odniesienia plus wpisana zmiana w punktach procentowych. Prezentowane pasma to ±2 pp dla CTR i ±10 pp dla retencji, z ograniczeniem do 0–100%. Są scenariuszami, nie przedziałami ufności. Zmiana CTR nie przelicza automatycznie całkowitych wyświetleń. CTR dotyczy tylko zarejestrowanych impresji, więc nie obejmuje wszystkich źródeł wyświetleń ([YouTube: CTR](https://support.google.com/youtube/answer/7628154)). Retencja tutaj oznacza średni obejrzany procent filmu; utrzymanie widza po pierwszych 30 sekundach jest inną miarą ([YouTube: retencja](https://support.google.com/youtube/answer/9314415)).

**Szansa sukcesu / wiralu** pojawia się dopiero dla co najmniej 10 porównywalnych wyników. Próg sukcesu to domyślnie ≥1,5× typowego wyniku, a wiralu ≥5×; oba są edytowalne i odnoszą się do pierwszych 30 dni. Symulacja korzysta z rozkładu logarytmicznego: środek `log(1 + typowy_wynik × mnożnik_bazowy)`, odchylenie `max(0,6; odchylenie log(1 + wyniki))`, następnie pole ogona powyżej progu. To eksperymentalna symulacja warunkowa, bez walidacji predykcyjnej i bez kalibracji na przyszłych premierach. Interfejs zawsze oznacza jej pewność jako niską. Wprowadzanie optymistycznych mnożników zwiększa wynik symulacji; nie dostarcza nowego dowodu, że film osiągnie taki zasięg.

## AI i zachowanie pracy

AI dodaje pomysły i warianty do kolekcji; plan rozdziałów zastępuje dopiero po przyjęciu propozycji. Zawsze można skopiować prompt i wkleić JSON z własnego narzędzia. Model nie może wpisać bezpośrednio „miliona wyświetleń” ani „90% szans” jako danych Analytics: import oceny przyjmuje wyłącznie rubrykę, hipotezy i uzasadnienie. Nieznane fakty i nieaktualne rewizje są odrzucane. Wywołania połączonego modelu używają istniejących limitów budżetu.

Wybór historii zapisuje migawkę kierunku. Późniejsza zmiana zarysu, otwarcia lub tematu jest sygnalizowana i wymaga ponownego jawnego wyboru przed przekazaniem nowego planu. Kafelek można rozwijać bez wpływu na film w produkcji. Zmiana oceny lub założeń nie przepisuje karty Historii.

## Weryfikacja

Regresje backendu: migracja i stabilne ID, osobne warianty, rewizje AI, budżet, wybór i cofanie, kompletne przeniesienie hierarchii, idempotencja, ochrona rozwiniętego scenariusza, brak wymyślonych prognoz, granice modelu scenariuszy, ZIP i wersje. Testy frontendu sprawdzają izolację kopii wariantów i zachowanie dowodów. Rzeczywiste wywołanie modelu tekstowego nadal zależy od dostępności konta; kontrolowane odpowiedzi testowe nie są opisane jako odpowiedź live.

Kontrola z 27.10.2026: pełny zestaw Studio — 97 zaliczonych testów i 1 pominięty opcjonalny test rzeczywistego renderowania Remotion; frontend — 16 zaliczonych testów; kompilacja TypeScript/Vite poprawna. W Safari sprawdzono ręczne tworzenie kafelka, zapis po odświeżeniu, Cofnij/Ponów, nawigację między tematami i historiami, przeliczanie CTR, jawny wybór kierunku, przekazanie trzech rozdziałów i czterech podrozdziałów do Scenariusza oraz podgląd i import kontrolowanej odpowiedzi redakcyjnej. Układ sprawdzono na komputerze i przy szerokości 390 px. Lokalne dane demonstracyjne są oznaczone jako przykład, nie wyniki kanału użytkownika.
