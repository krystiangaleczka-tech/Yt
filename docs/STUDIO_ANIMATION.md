# Tryb Animacja 2D — postacie, lokacje i tablica scen

Stan wdrożenia: 28.10.2026. Plan całości: [PLAN_ANIMACJA_SURVIVAL.md](PLAN_ANIMACJA_SURVIVAL.md).

## Tryb produkcji

Przełącznik w lewym górnym rogu wybiera tryb: **Dokument**, **Animacja 2D** albo **B-roll**. Tryb zmienia nawigację, listę projektów i domyślne ustawienie nowego filmu. Film należy do jednego trybu; przełączenie na inny tryb zamyka otwarty film innego trybu, a kolejny start aplikacji otwiera film zgodny z wybranym trybem.

- **Animacja 2D:** Pomysł → Research → Scenariusz → **Sceny** → Montaż → Eksport, a w Pracowni **Postacie** i **Lokacje**.
- **Dokument** i **B-roll** zachowują dotychczasowy przebieg. B-roll nie ma jeszcze osobnych narzędzi.

Kanał ma własny tryb produkcji (Pracownia → Kanały i kategorie → profil kanału). Nowy film dziedziczy go, chyba że wybierzesz inny w oknie **Nowy film**. Film animowany wymaga kanału.

## Bank postaci i lokacji należy do kanału

Postacie i lokacje są zapisywane osobno dla każdego kanału (`<DOCOS_STUDIO_HOME>/workspace/cast/<kanał>/`). Inny kanał ich nie widzi i nie może ich użyć. Serwer odrzuca scenę, która wskazuje postać, pozę, lokację albo stan spoza banku kanału danego filmu. Zmiana kanału filmu, który ma już sceny, jest zablokowana, bo rozerwałaby te powiązania.

Film korzysta z bieżącej wersji wpisu w banku — poprawiona poza od razu pojawia się w scenach wszystkich odcinków tego kanału. To świadoma różnica wobec banku wiedzy, gdzie film zachowuje migawkę: tu celem jest stały wygląd obsady w całej serii.

### Postacie

Każda postać ma imię, rolę, znak rozpoznawczy, kolor akcentu, wygląd, charakter, cel i ustawienia głosu (dostawca, ID głosu, sposób gry). **Pozy** wgrywasz jako obrazy — najlepiej PNG z przezroczystym tłem; obraz bez przezroczystości jest oznaczony ostrzeżeniem. Pozę można nazwać, przypisać do widoku (przód, 3/4, profil, tył) i ustawić jako domyślną. Wiele plików można przeciągnąć naraz.

### Lokacje

Lokacja ma opis układu (gdzie drzwi, okno, zlew) i **stany**: to samo miejsce w różnych chwilach historii, np. „Dzień 1” i „Dzień 30 — barykada”, z własnym tłem i porą dnia.

Zapis wpisu wymaga zgodnej rewizji. Gdy ktoś (albo inne okno) zmienił wpis wcześniej, aplikacja odrzuci zapis zamiast nadpisać zmiany. Archiwizacja ukrywa wpis z wyboru w nowych scenach.

## Tablica scen

Ekran **Sceny** pokazuje listę scen ze statusem, kadr sceny i inspektor.

- **Kadr** składa tło wybranego stanu lokacji z pozami postaci. Postać przesuwasz, przeciągając ją na kadrze; wielkość, pozę i odbicie zmieniasz w inspektorze. Pierwsza kwestia pojawia się jako napis.
- **Scena** opisuje czas w historii, lokację i stan, postacie, akcję, kamerę, narrację i dialog (mówca: narrator albo postać z banku, z uwagą „jak mówi”) oraz dźwięk: atmosferę, muzykę i efekty.
- **Statusy:** Szkic → Do oceny → Zatwierdzona albo Do poprawki. Każda zmiana treści zatwierdzonej lub odesłanej sceny wraca do statusu „Do oceny”. Historia ocen zostaje przy scenie.

### Szybka ocena

| Klawisz | Działanie |
|---|---|
| ↑ ↓ lub J K | poprzednia / następna scena |
| A | zatwierdź i przejdź do następnej |
| R | przejdź do uwag; Ctrl/Cmd+Enter odsyła do poprawki |
| G | regeneruj z AI |

„Do poprawki” wymaga zaznaczenia obszaru (Kadr, Postać/poza, Tło, Dialog, Dźwięk, Tempo) albo napisania uwagi.

### Regeneracja z AI

**Regeneruj z AI** wysyła scenę, sąsiednie sceny, bank kanału i Twoje uwagi do połączonego modelu (Ustawienia) albo do Claude CLI. Wynik to **propozycja** pokazana jako porównanie przed/po; scena zmienia się dopiero po **Przyjmij propozycję**, a potem czeka na ocenę. Propozycja z postacią, pozą albo lokacją spoza banku jest odrzucana. Gdy model nie jest dostępny, aplikacja daje prompt do skopiowania i pole na odpowiedź JSON.

Wszystkie operacje na scenach podlegają kontroli rewizji i trwałemu Cofnij/Ponów.

## Czego jeszcze nie ma

Kadr jest podglądem składu sceny, a nie renderem: brak ruchu postaci, kamery i światła w czasie, brak generowania głosu postaci, brak dźwięków z banku i brak przenoszenia scen na oś Montażu. Te elementy są kolejnymi etapami planu.

## Weryfikacja

`studio_tests/test_animation.py`: dziedziczenie trybu z kanału, wymóg kanału, przezroczystość i izolacja obrazów, konflikt rewizji, izolacja banku między kanałami, przebieg ocen i powrót do „Do oceny” po zmianie, kolejność, cofanie, blokada zmiany kanału oraz walidacja propozycji AI.
