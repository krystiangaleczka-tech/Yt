# Zasoby pracowni, kategorie, szablony i pojedynczy film

Status: propozycja architektury produktu, 27.10.2026. Dokument opisuje planowane zachowanie; nie jest raportem wdrożenia.

## Główna zasada

**Nowy film tworzy osobny, pusty projekt.** Research, pomysły, historia i scenariusz powstają najpierw w tym filmie. Autor może świadomie dobrać istniejące zasoby z banku albo udostępnić wybrane elementy filmu do dalszego wykorzystania.

Treść odcinka, zasób banku i szablon mają różne zadania. Umieszczenie materiału w kategorii porządkuje jego dostępność; samo w sobie nie dodaje go do żadnego filmu.

## Dwa niezależne oznaczenia zasobu

1. **Zakres:** pracownia → kanał → kategoria → film. Ustawienia filmu mogą nadpisywać wybrane wartości domyślne; nie zmieniają ich u źródła.
2. **Sposób wykorzystania:** materiał lub wiedza do dobrania, profil ustawień, szablon do wypełnienia albo indywidualna treść filmu.

Kanał określa markę, widza i język. Kategoria określa obszar tematyczny, np. Nauka, Historia, Kryminalne. Format określa konstrukcję, np. śledztwo, biografia, wyjaśnienie. Film o nauce może korzystać z szablonu śledztwa; kategoria nie narzuca konkretnej historii.

Zasób istnieje w banku raz i może mieć wiele kategorii oraz tagów. Kolekcje są filtrami, nie kopiami plików. Zasób przypisany do innej kategorii nadal można wyszukać i świadomie wykorzystać; kategorie porządkują propozycje.

## Co i jak wykorzystujemy ponownie

| Element | Gdzie przechowujemy wzorzec lub oryginał | Co trafia do nowego filmu |
|---|---|---|
| Klucze usług, lokalne modele, ustawienia aplikacji | Pracownia, ustawienia prywatne | Film korzysta z konfiguracji; nie dostaje kopii sekretów |
| Tożsamość kanału, widz, język, fonty, kolory, zasady redakcyjne | Profil kanału | Migawka wybranego profilu i jej wersja; wartości można zmienić w filmie |
| Zalecenia tematyczne, słownik, polecane źródła i kryteria oceny | Kategoria | Wybrane ustawienia domyślne i sugestie; bez automatycznego importu treści |
| Profil głosu i słownik wymowy | Prywatne profile pracowni/kanału, ewentualne uzupełnienia kategorii | Wybrany profil oraz migawka ustawień; nagrania dla tego scenariusza powstają osobno |
| Dokumenty, książki, publikacje i ich metadane | Bank źródeł | Świadomie wybrane źródła wraz z wydaniem, cytatami, lokalizacją i pochodzeniem |
| Fakty i wyniki researchu | Najpierw film; wybrane wpisy można dodać do banku wiedzy | Wybrane fakty razem z potrzebnymi źródłami; przegląd zastosowania w nowym kontekście |
| Notatki badawcze | Film; po świadomym udostępnieniu bank | Wybrane notatki, oddzielone od potwierdzonych twierdzeń |
| Zdjęcia, nagrania, muzyka, SFX, logo, intro/outro | Najpierw film lub jawny import do banku mediów | Tylko wskazane pliki z metadanymi i warunkami użycia; bez dawnego montażu |
| Szablony historii, rozdziałów, miniaturek i tytułów | Biblioteka szablonów, tagowana kategorią i formatem | Struktura, pola do wypełnienia i wskazówki; bez konkretnej fabuły i twierdzeń z poprzedniego filmu |
| Szablony wstawek, napisów, ruchu, miksu i eksportu | Biblioteka szablonów/profili | Wybrane komponenty i parametry; konkretne podpisy, dane i pliki dobiera autor |
| Luźny temat na przyszłość | Pomysły w filmie; opcjonalnie poczekalnia pomysłów kanału | Jeden świadomie wybrany temat z informacją o wcześniejszych użyciach |
| Brief, warianty historii, rozdziały, scenariusz i ujęcia konkretnego filmu | Film | Powstają od nowa; zapisanie schematu jako szablonu usuwa szczegóły tego filmu |
| Tytuł publikacji, miniatura, hook, payoff i opis | Film | Własne propozycje; szablon może dostarczyć układ i pytania pomocnicze |
| Oceny redakcyjne, prognozy, założenia, ryzyka i luki w dowodach | Film | Nowa ocena jego konkretnego kierunku; szablon przenosi kryteria, nie wynik |
| Rzeczywiste wyniki opublikowanych filmów | Wyniki danego filmu oraz indeks analityczny kanału | Wybrana, datowana grupa porównawcza; bez przenoszenia starych prognoz jako wyników |
| Wygenerowany lektor, znaczniki słów, napisy, cięcia i finalny render | Film | Pozostają związane z konkretną narracją i montażem; fragment można jawnie zachować jako materiał do ponownego użycia |
| Zatwierdzenia, zaakceptowane uwagi, historia zmian, zadania i zużyty budżet | Film | Nowy film rozpoczyna własny cykl pracy; profil może ustawić nowe limity, ale nie przenosi zużycia |

## Przepływ „Nowy film”

1. Kliknięcie **Nowy film** otwiera krótki formularz: nazwa robocza, kanał, opcjonalna kategoria, język. Nazwa może pozostać robocza, dopóki nie wybierzemy tematu.
2. Opcjonalnie wybieramy szablon lub zostawiamy pusty projekt. Formularz pokazuje, jakie ustawienia zostaną zastosowane. Żadne fakty, źródła, media ani narracje z poprzedniego filmu nie są zaznaczone domyślnie.
3. Powstaje szkic i otwiera się **Pomysł**. Brief oraz kafelki dotyczą tego nowego filmu. W tym miejscu można również dobrać temat z poczekalni.
4. W **Fakty i research** dodajemy własny research albo używamy **Dodaj z banku**. Wybór faktu pokazuje powiązane źródła; przyjęcie przenosi cały potrzebny zestaw zależności.
5. W **Materiały filmu** można użyć **Dodaj z banku mediów**. Dodanie do projektu i umieszczenie na osi czasu pozostają oddzielnymi czynnościami.

Nie potrzeba obowiązkowego kreatora importu przed rozpoczęciem pracy. Bank jest dostępny również później, kiedy wiadomo już, czego film potrzebuje.

Operacja **Kopia robocza filmu** służy rozwijaniu alternatyw istniejącego filmu i pozostaje oddzielona od tworzenia nowego odcinka. Może zachować treść i montaż, ale musi mieć nowe ID, własną historię pracy i ponowne zatwierdzenie. Nie jest szablonem startowym nowego filmu.

## Trzy jawne działania

- **Dodaj do filmu z banku** — wybieramy istniejącą wiedzę lub materiał. Powstaje projektowa wersja z odnośnikiem do konkretnej wersji wpisu w banku.
- **Zastosuj szablon** — wypełniamy strukturę lub stosujemy ustawienia. Przed zmianą istniejącej pracy widać różnice i zakres zastosowania.
- **Dodaj do banku / Zapisz jako szablon** — autor wskazuje, co ma być dostępne ponownie. Edycja filmu nigdy sama nie publikuje zmian w banku.

Promocja elementu do banku powinna pytać o nazwę, zakres i kategorię. Jeżeli wiedza zależy od daty, miejsca, wersji urządzenia lub przyjętej definicji, ten kontekst jest częścią wpisu.

## Niezależność projektu i aktualność dowodów

Film zachowuje migawkę użytej wersji zasobu oraz jej pochodzenie. Aktualizacja lub wycofanie wpisu w banku nie przepisuje wcześniejszych filmów. Aplikacja może pokazać: **Dostępna nowsza wersja — porównaj**.

Weryfikacja faktu w banku i akceptacja jego użycia w filmie są osobnymi informacjami. Import zachowuje autora weryfikacji, datę, źródło, cytat i kontekst, a użycie w nowym filmie czeka na przegląd. Potwierdzenie źródła nie oznacza automatycznie, że każde sformułowanie narracji jest poprawne. Zmiana dowodów w filmie zachowuje istniejący mechanizm ponownego zatwierdzania Historii.

Powtórne dodanie tej samej wersji wpisu nie tworzy drugiego identycznego faktu. Wpisy z dwóch filmów mogą być kandydatami do scalenia w banku, ale podobna treść nie wystarcza do automatycznego uznania ich za ten sam fakt.

Udostępnione dokumenty i media powinny być przechowywane niezależnie od folderu filmu, z którego pochodzą. Zarchiwizowanie lub późniejsze usunięcie tamtego filmu nie może zepsuć innego projektu. Projektowy ZIP nadal zawiera potrzebną treść, wersje źródeł i dozwolone pliki, zgodnie z obecnymi zasadami eksportu prywatnych materiałów.

## Metryki: dane wspólne, decyzja dla filmu

Wspólny zbiór porównawczy przechowuje rzeczywiste wyniki filmów wraz z okresem pomiaru, długością, językiem, kategorią i formatem. Pozwala wybrać porównywalne filmy; nie miesza domyślnie Shorts z długim dokumentem ani wszystkich kategorii w jedną średnią.

Film zapisuje migawkę wybranych danych odniesienia i swoich założeń. Ocena wariantu i jego prognoza pozostają indywidualne. Dodanie nowych wyników do kanału nie zmienia historycznej oceny decyzji bez jawnego przeliczenia. Niepotwierdzone prognozy nigdy nie trafiają do zbioru rzeczywistych wyników.

Historia tematów i publikacji działa przekrojowo: przy nowym pomyśle pokazujemy podobne tematy, przygotowywane filmy i poprzednie publikacje. Jest kontekstem decyzji redakcyjnej, a nie treścią kopiowaną do scenariusza.

## Nawigacja

**Pracownia**, dostępna bez otwartego filmu:

- Filmy i przycisk Nowy film.
- Bank wiedzy: źródła, fakty, notatki i kolekcje researchu.
- Bank mediów.
- Szablony i profile.
- Kanały i kategorie, w tym zbiór porównawczy oraz historia tematów.
- Poczekalnia pomysłów.

**Otwarty film**, z jego nazwą stale widoczną:

- Pomysł → Fakty i research → Historia → Scenariusz → Generowanie → Montaż → Eksport.
- Materiały filmu, zadania, wersje i ustawienia tego filmu.

Wyszukiwarka źródeł może pracować w obu kontekstach. Wynik ma jawny cel: **Dodaj do tego filmu** albo **Zapisz w banku**. AI domyślnie korzysta z wiedzy dodanej do filmu; szersze przeszukiwanie banku jest wybieraną operacją, a znalezione propozycje czekają na przyjęcie.

## Dopasowanie do obecnego kodu

- `Project` zawiera obecnie fakty, źródła, media, warsztat pomysłów i dane odniesienia. Biblioteka w UI filtruje `project.assets`, więc jest biblioteką danego filmu.
- `ProjectService.channels()` i `save_channel()` zapisują wspólne profile. `project.channel_profile` jest migawką, co pasuje do proponowanego modelu.
- `channel_titles()` już zbiera historię tematów między projektami kanału.
- Profile głosu istnieją poza pojedynczym projektem; ich prywatny charakter trzeba zachować przy dalszym wykorzystaniu.
- `POST /api/projects` tworzy świeży `Project`; obecnie przyjmuje tylko tytuł i język. To właściwy punkt rozbudowy o świadomy wybór profilu, kategorii i szablonu.
- Obecna duplikacja kopiuje cały film. Powinna pozostać osobnym działaniem opisanym jako kopia robocza.
- Brakuje modelu kategorii, banku źródeł/faktów/mediów, projektowego przeglądu zaimportowanego faktu i trwałych powiązań wersji banku z projektem.

Docelowo potrzebujemy osobnych rekordów kategorii, wersjonowanych wpisów banku i wersjonowanych szablonów. Projekt zachowuje lokalne ID oraz pochodzenie: identyfikator wpisu, numer wersji i datę dodania. Pliki można deduplikować po sumie kontrolnej; metadane źródła i kontekst użycia pozostają rozdzielone.

## Kolejność wdrażania

1. Wprowadzić kanały/kategorie i rozdzielenie nawigacji pracowni od otwartego filmu. Rozbudować Nowy film, zachowując pustą treść jako domyślne zachowanie.
2. Wdrożyć bank źródeł i faktów, jawne udostępnianie z filmu oraz import zestawu fakt–źródło–plik z przeglądem zastosowania.
3. Wdrożyć bank mediów i powiązania wersji tak, żeby projekty nie zależały od folderów innych filmów.
4. Dodać szablony struktury i profile ustawień z listą dozwolonych pól. Szablon nie może zawierać narracji, ocen, zatwierdzeń, zadań ani przypadkowych zależności poprzedniego filmu.
5. Przenieść wspólne dane porównawcze i poczekalnię pomysłów do kanałów/kategorii; zachować migawki użyte w istniejących filmach.

Migracja zachowuje wszystkie obecne dane w ich filmach. Nie publikuje automatycznie dotychczasowych źródeł, mediów ani faktów do banku. Autor może później udostępnić wybrane wpisy.

## Kryteria odbioru przyszłego wdrożenia

- Nowy film zawiera wyłącznie świadomie wybrane ustawienia/szablon; nie dziedziczy faktów, scenariusza ani montażu otwartego wcześniej projektu.
- Bez importu z banku można przejść cały proces produkcji.
- Import faktu przenosi jego zależności i pochodzenie, wykrywa ponowne dodanie oraz wymaga przeglądu użycia w filmie.
- Zmiana wpisu w banku, kategorii lub szablonie nie zmienia gotowych ani rozpoczętych filmów bez jawnej operacji autora.
- Zmiana materiału w filmie nie zmienia banku ani innych filmów.
- Szablon zawiera strukturę i parametry, a nie konkretny tekst i wyniki poprzedniej produkcji.
- Cofanie i konflikt rewizji obejmują import do filmu. Eksport i ponowny import zachowują wszystkie wykorzystane wersje oraz zależności.
- Film pozostaje otwieralny po zarchiwizowaniu źródłowego projektu; wycofanie wpisu w banku nie usuwa użytej migawki.
- Zbiór wyników rzeczywistych nie zawiera ocen ani prognoz modelu.
