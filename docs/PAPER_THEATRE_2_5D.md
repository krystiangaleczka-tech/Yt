# Paper Theatre 2.5D · standard produkcji DocOS Studio

**Status:** niezależna od gatunku technika ujęcia w kategorii Narzędzia produkcji → Paper Theatre 2.5D. Pierwsza implementacja kreatora, planowania sekwencji, walidacji osobnych PNG, renderowania mechanik, podglądu klatki i przekazania do Montażu. Nie mylić z automatycznym rozcinaniem jednolitej grafiki na sto profesjonalnych warstw.


## Zastosowanie: niezależny styl realizacji ujęcia

**Paper Theatre 2.5D nie jest typem filmu ani gatunkiem dokumentalnym.**
To jedna z technik animowania scen, szczególnie przydatna w opowieściach
historycznych, biografiach, legendach, narracjach opartych na faktach oraz
innych historiach. Film lub odcinek może mieszać Paper Theatre, klasyczną
animację 2D, archiwalia, B-roll, mapy i wstawki Remotion. Wybranie Paper
Theatre dla jednego ujęcia **nie** zmienia profilu filmu ani zasad weryfikacji
faktów. Każda rzeczywista data, liczba i cytat nadal wymagają źródła
w istniejącym systemie redakcyjnym, niezależnie od sposobu wizualizacji.

### Aktualizacja 30.10.2026: edycja pozycji i walidacja

- Wgranie paczki PNG o nazwach identycznych z ID obiektów przypisuje je
  automatycznie, bez nadpisywania wcześniej wybranych materiałów.
- Podstawowy edytor maski alpha pozwala usuwać piksele pędzlem,
  przywracać wyłącznie piksele z oryginału, cofać pociągnięcia i
  eksportować nowy PNG bez niszczenia źródła.
- Obiekty w kreatorze można przeciągać na mapie kompozycji; klawiatura:
  strzałki co 0,01, Shift + strzałki co 0,05 znormalizowanego kadru.
- Każdy obiekt ma własny pivot X/Y (0–1) i mechanikę wejścia (opcjonalnie
  zamiast domyślnej grupy). Te wartości trafiają przez manifest, walidację,
  plan i cue do istniejącego renderera MP4.
- Kontrola wycinków wskazuje wieloczęściowe maski alpha, obiekty wychodzące
  poza kadr i mocne nakładanie prostokątów sylwetek. To **ostrzeżenia**,
  nie precyzyjna detekcja kolizji klatka po klatce, i nie powód, żeby
  odrzucać poprawną, zamierzoną okluzję.
- Schematyczny podgląd React nie zastępuje dokładnej klatki z renderera.
  Automatyczne image-to-image, gwarantowane generowanie alpha PNG, precyzyjny
  edytor wektorowych masek, rekonstrukcja ukrytych pikseli i akceptacja jakości
  wizualnej nadal wymagają dalszych wdrożeń i rzeczywistych testów.

## Workflow domyślny: Reference-to-layers (aktualizacja 29.10.2026)

**Najnowsza decyzja:** po ustaleniu scenariusza i beatów tworzymy najpierw **mały draftowy obraz całej sceny** (np. 512 × 288), który pokazuje kompozycję, proporcje i wspólny styl. Dopiero gdy jest zaakceptowany, z jego pomocą tworzymy **Scene Object Manifest** i oddzielne przezroczyste PNG dla każdego obiektu. Obraz draftowy jest wyłącznie referencją i nigdy nie stanowi spłaszczonego tła lub materiału do nieprecyzyjnego wycinania. **Reference-to-layers jest teraz domyślną opcją**. **Asset-first** bez obrazu poglądowego pozostaje pełnoprawną alternatywą.

### Etapy

1. **Scenariusz → mały draft:** opis sceny/narracja i spójna stylistyka służą do wygenerowania poglądowego obrazu kompozycji. Aplikacja potrafi przygotować prompt, wygenerować PNG 512 × 288 przez istniejący lokalny image worker (po konfiguracji DOCOS_IMAGE_PYTHON) albo przyjąć własny PNG/JPEG. Przed przejściem dalej użytkownik wybiera referencję, może opisać jej najważniejsze cechy i **jawnie akceptuje kompozycję**.
2. **Reference → lista obiektów:** model wizualny podłączony przez zgodny endpoint chat/completions z obsługą obrazów może, po wyraźnym kliknięciu użytkownika, przeanalizować draft i zwrócić listę obiektów oraz pozycje. Bez takiego modelu listę można przygotować ręcznie albo w innym narzędziu; nie udajemy, że model tekstowy widzi obraz.
3. **Scene Object Manifest:** każdy element jest niezależnym rekordem z `id`, `name`, `description`, `group`, `x`, `y`, `width`, `z`, `asset_id` (na początku pustym) i opcjonalnym `duration`. Grupy ustalają wejścia, **Z ustala przesłanianie**. `x` to środek poziomy, `y` to dolny punkt wycinka, `width` to część szerokości kadru.
4. **Jedna linia artystyczna:** globalny `style` zasila wszystkie per-obiektowe prompty. Nie wolno dopuścić do postaci w innym oświetleniu, odcieniu papieru lub technice kreski niż reszta dioramy.
5. **Generowanie pojedynczych zasobów:** osobny prompt dla każdej chmury, budynku, drzewa, monety i postaci. Generator musi zwrócić rzeczywisty **RGBA PNG** z przezroczystym tłem i jednym obiektem. Aplikacja przygotowuje i eksportuje prompty oraz wczytuje i wiąże gotowe PNG. **Nie deklarujemy automatycznego generowania alpha PNG**: obecny lokalny image worker nie zapewnia wiarygodnych wycinków, ten etap wymaga jeszcze integracji odpowiedniego modelu lub zewnętrznego generatora.
6. **Scene Layout Planner:** render umieszcza obraz na podstawie współrzędnych i szerokości ze spisu; wycina przezroczyste marginesy, nie rozciąga obiektu i nie wymaga płótna wielkości całego filmu. Niezależne `z_index` odpowiada za to, co jest przed czym.
7. **Staging i rigging:** `sky = hanging_drop`, `landscape/foundations = bottom_rise`, `vegetation/props/characters/hero = rake_lift`. Każdy ma osobny czas. Hero tylko jeden, na końcu, z mocnym obrysem.
8. **Podgląd, poprawki i montaż:** najpierw plan i statyczna mapa kompozycji, następnie rzeczywiste klatki renderera, a dopiero potem eksport MP4.

### Co jest wdrożone teraz

- Domyślny panel **Reference-to-layers**, z osobnym wyborem **Asset-first** i zachowanym zaawansowanym edytorem już przygotowanych PNG.
- Prompt i generowanie niewielkiego draftu przez skonfigurowany lokalny model obrazu; możliwość ręcznego wgrania JPEG/PNG, obejrzenia i zatwierdzenia.
- Opcjonalne rozpoznawanie obiektów bezpośrednio z obrazu przez podłączony **model vision**; wysyłanie obrazu odbywa się wyłącznie po kliknięciu użytkownika.
- Edycja listy obiektów, ich grup, opisów, współrzędnych X/Y, szerokości i głębi Z.
- Zapis manifestu w `Scene.generation.paper_theatre_asset_first`; wersjonowanie razem z projektem bez nowego formatu pliku.
- API przygotowywania promptów per obiekt, importowania własnej listy JSON i propozycji AI przez skonfigurowany model tekstowy (brak modelu oznacza brak propozycji, a nie wymyślone wyniki).
- Wczytanie obrazów i przypisanie ich do obiektów, walidacja przeźroczystości i unikalności, składanie ujęcia i przekazanie do osi czasu. Draft referencyjny jest zapisany jako osobny asset projektu, nie może zostać użyty jako finalne tło ani wycinek.
- Podgląd orientacyjnej sceny i rzeczywistego kompozytora; rozdzielenie kolejności wejść od przesłaniania przez Z.

### Pozostały zakres, którego nie wolno uznać za ukończony

- Bezpośrednia generacja jakościowych przezroczystych PNG z modelu obrazu, zamiast jedynie promptów i ręcznego importu.
- [ ] Referencyjna zgodność wygenerowanych osobno PNG z draftem nie jest jeszcze automatycznie oceniana; prompty niosą opis stylu i notatki, ale lokalny image worker nie używa wejścia obrazowego do sterowania generowaniem przez obraz. W razie potrzeby przekazuj draft do generatora obsługującego image-to-image/reference conditioning.
- Weryfikacja jednolitości stylu między osobno wygenerowanymi obrazami; automatyczne wykrywanie wielu obiektów na jednej warstwie, kolizji i brakujących pikseli.
- Przeciąganie, pivoty oraz podstawowy pędzel alpha są wdrożone; **profesjonalny edytor konturów/masek**, zaawansowane wypełnianie i dokładny **wielowarstwowy podgląd na żywo** nadal wymagają implementacji.
- Pełna ewaluacja benchmarku na materiale referencyjnym i zatwierdzony end-to-end eksport MP4.

### Zasada jakości

Asset-first usuwa problem prób odtwarzania zakrytych fragmentów z gotowego obrazu, ale **nie gwarantuje automatycznie jakości 100%**. Największe ryzyka przesuwają się na spójność stylu, proporcje i kompozycję. Zachowujemy ocenę 50% poprzedniego demo jako punkt wyjścia.

## Dlaczego ta kategoria jest osobna

Referencja: papierowa diorama składana przed widzem, jak teatrzyk / scenografia na patyczkach i cieniutkich nitkach. Wersja demonstracyjna chińskiego imperium została oceniona przez właściciela projektu jako **około 50% zamierzonego efektu**, nie jako finalny benchmark jakości. W pierwszych podejściach kilka dużych fragmentów obrazu było przemieszczanych lub niewyraźnie maskowanych, zamiast poprawnego montażu wielu indywidualnych wycinków. **Nie używać tych rezultatów jako dowodu spełnienia jakości 1:1.**

Kluczowa różnica: jeden obiekt = jeden wyodrębniony, przezroczysty PNG + indywidualny cue i własny rytm. Małe chmury, pojedyncze detale, monety, sztandary, drzewa, rzeźby oraz każda postać nie mogą zostać ukryte w jednej szerokiej teksturze „grupy”. Grupa wyznacza tylko **kolejność animowania**, nie spłaszcza obiektów do wspólnego obrazu.

## Niezmienne zasady inscenizacji

1. **Tło bazowe**: czysta scenografia bez postaci, chmur i rekwizytów, nie spłaszczony gotowy obraz z widocznymi elementami, które później mają „wchodzić”. W razie brakujących tyłów obiektów potrzebne są retusz i rekonstrukcja tła.
2. **Niebo**: słońce, księżyc i **każda pojedyncza chmura** są zawieszane z góry na bardzo cienkiej, opcjonalnie widocznej nici. Wchodzą po kolei; delikatne osadzenie i kołysanie, brak zwykłego fade-in.
3. **Krajobraz**: osobne pasma i pojedyncze góry mogą wysuwać się od dołu lub zza dalszej scenografii.
4. **Ciężkie fundamenty**: mury, bramy, miasta, mosty i podstawy budowli wsuwają się od dołu, z wyczuwalnym ciężarem. Najpierw struktura, później drobne nakładki.
5. **Roślinność**: każde drzewo i krzak z własnym dolnym pivotem, podnoszony jak papierowy wycinek na patyczku, z niewielkim overshoot.
6. **Rekwizyty i posągi**: oddzielne wycinki, podnoszone podobnie do teatrzyku; jeśli dany rekwizyt jest zawieszony, zmienić cue na hanging_drop ręcznie w zaawansowanym edytorze.
7. **Postacie drugoplanowe**: **każda osobno**, jedna za drugą, nigdy szeroka grupa wycięta razem.
8. **Najważniejsza postać**: wchodzi **ostatnia**, samodzielnym ruchem podnoszenia; ma **najsilniejszy obrys** postaci, wyznaczony z alpha, a nie prostokąt wokół pliku. W jednej scenie może być tylko jeden taki punkt kulminacyjny.
9. **Ruch grup**: grupy układają się sekwencyjnie, bez kolizji wejść. W obrębie grupy również osobny start każdego PNG.
10. **Po złożeniu**: kompozycja zostaje na ekranie, bez dziur, nadmiernego pulsowania czy nagłego przeskoku do gotowego spłaszczonego obrazu.

## Zasady zasobów

- Do kreatora wgraj **osobny PNG z alpha dla każdego najmniejszego elementu**.
- W starszym ręcznym edytorze PNG muszą mieć **identyczne wymiary płótna**; w nowym Asset-first i Reference-to-layers obiekty mogą mieć własne wymiary i są ustawiane przez X/Y/szerokość. Wszystkie wycinki muszą zawierać prawdziwą przezroczystość.
- Każdy plik wycinka powinien zawierać **dokładnie jeden obiekt**. Automatyczny raport wskazuje podejrzanie wielkie obszary, ale nie potrafi jeszcze wykryć połączonych obiektów w jednej masce.
- Wcześniejszy materiał źródłowy to **pojedynczy spłaszczony PNG**, więc ukryte tekstury pod postaciami i drzewami **nie istnieją**. Bez nowych danych/silniejszej segmentacji i inpaintingu nie da się zagwarantować identycznych rekonstrukcji.
- Zakaz udawania, że pocięcie prostokątów lub rozmazany fragment tła jest gotową segmentacją 1:1.

## Dostępny workflow w aplikacji

W **Narzędziach produkcji → Paper Theatre 2.5D**:
1. Utwórz osobne ujęcie lub wybierz już utworzone.
2. Importuj PNG, wybierz osobne czyste tło i dodawaj poszczególne wycinki.
3. Każdemu nadaj rolę z siedmiu grup, ustal kolejność i indywidualny czas wejścia.
4. Zaznacz jedną najważniejszą postać jako `hero`. Jeśli są inne postacie, hero jest wymagany.
5. Ustaw odstęp między elementami, przerwy pomiędzy grupami i szerokość obrysu bohatera.
6. Użyj **Sprawdź plan i PNG**. Walidowane są typ pliku, kanał alpha, identyczna rozdzielczość, unikalność mediów, ułożenie grup i czas harmonogramu.
7. Użyj **Zapisz Paper Theatre**, podejrzyj klatki, a następnie **Zastosuj w montażu**. Render używa istniejącego kompozytora i FFmpeg.

Zmiany przechowywane są w istniejącym projekcie jako `Scene(template="paper-theatre")` i jej `parameters.layer_cues`; kopie, snapshoty i eksporty projektu zachowują definicje animacji. Starsze szablony `parallax` nie zmieniają sposobu działania.

## Kryteria akceptacyjne wersji profesjonalnej

- [x] Wyodrębniona kategoria, nie tylko preset parallaxu.
- [x] Indywidualne przezroczyste PNG z walidacją rozdzielczości, alfa i unikalności.
- [x] Oddzielne grupy w ustalonej kolejności; żadna grupa nie wyprzedza poprzedniej.
- [x] Hanging drop / bottom rise / rake lift i dokładne klatki.
- [x] Postacie osobno, wyróżniony bohater na końcu, obrys śledzący alpha.
- [x] Panel kreatora, zapisywanie, montaż i podstawowe testy regresji.
- [ ] Jakościowy, dokładny pipeline automatycznej segmentacji i rekonstrukcji zasłoniętych elementów.
- [ ] Edytor konturu i punktów zakotwiczenia **dla każdego obiektu** z podglądem na scenie, nie tylko parametry schematów.
- [ ] Kontrola overlapów i brakujących pikseli podczas całego przebiegu renderowania.
- [ ] Ocena gotowego MP4 klatka po klatce na tle filmu referencyjnego, osobna akceptacja kierunku estetycznego.
- [ ] Referencyjne E2E z wieloma dziesiątkami prawidłowych, niezależnych assetów i pełnym filmem.

### Nie dopowiadać sukcesu

Stan wdrożenia nowej kategorii ≠ 100% jakości wizualnej. Ocena 50% dotyczy dotychczasowego demo. Nowy format jest narzędziem do dalszej poprawy, a nie dowodem finalnego efektu. Nie deklarować zgodności 1:1 bez kompletnego zestawu assetów i oceny rzeczywistego eksportu.
