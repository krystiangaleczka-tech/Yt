# Paper Theatre 2.5D · standard produkcji DocOS Studio

**Status:** niezależna od gatunku technika ujęcia w kategorii Narzędzia produkcji → Paper Theatre 2.5D. Pierwsza implementacja kreatora, planowania sekwencji, walidacji osobnych PNG, renderowania mechanik, podglądu klatki i przekazania do Montażu. Nie mylić z automatycznym rozcinaniem jednolitej grafiki na sto profesjonalnych warstw.


### Podgląd na żywo i szybszy eksport, 30.10.2026

Iteracja nie wymaga już renderu MP4. Wąskim gardłem nie był wybór biblioteki
(Three.js / PixiJS / Remotion), tylko renderer Pythona, który w każdej klatce
liczył od nowa rzeczy stałe: obrys postaci (`MaxFilter`, ~1 s na postać na
klatkę), obrót i rozmycie cienia na pełnym płótnie dla każdej warstwy.

- **Podgląd na żywo** (prawa kolumna panelu, nad mapą kompozycji): Canvas 2D,
  odtwarzanie, przewijanie, klatka po klatce. Pokazuje **bieżące, niezapisane
  zmiany** (harmonogram z planera przez `POST /paper-theatre/{sid}/preview`,
  który niczego nie zapisuje; przeciągnięte pozycje nakładane są od razu) albo
  **zapisane ujęcie** z przełącznikiem „dokładna klatka z renderera MP4”.
- **Jedna logika ruchu, dwa języki:** `rig_motion()` w
  `studio_timeline/paper_theatre.py` i `apps/studio/src/paperTheatreMotion.ts`
  liczą te same liczby (pozycje, kąty, czasy). Oba testy porównują je z
  `apps/studio/tests/fixtures/paper-theatre-motion.json` (1430 przypadków).
  Po zmianie rigu: popraw obie strony i uruchom
  `python3 scripts/paper_theatre_motion_fixture.py`.
- **Granica podglądu:** geometria i czas są identyczne z eksportem, piksele
  nie — przeglądarka inaczej skaluje i rozmywa cień. Dokładną klatkę zawsze
  daje renderer.
- **Eksport ~10× szybszy przy tych samych pikselach:** `composite_rig()` liczy
  stałe rzeczy raz na render i pracuje na obszarze wycinka zamiast całego kadru.
  `rig_image()` zostaje wzorcem; `studio_tests/test_paper_theatre_speed.py`
  porównuje oba co do bitu. Jedyny wyjątek: wycinek na nitce, którego wahnięcie
  zanikło poniżej 0,001°, może mieć pojedyncze piksele różne o 1–2/255
  (zaokrąglenie ostatniego bitu przy próbkowaniu bicubic), poniżej szumu H.264.
- Klucze cache szablonów i miniatur obejmują teraz także `paper_theatre.py`,
  więc zmiana rigu nie zostawi starego MP4 w cache.

**Następne kroki (niezrobione):** podgląd na żywo ujęć Paper Theatre w
głównym podglądzie Montażu; polecenia AI zmieniające cue (JSON patch zamiast
nowej sceny); opcjonalny eksport szkicu z przeglądarki (WebCodecs). Three.js
ma sens dopiero przy prawdziwym ruchu kamery w 3D — obecne rigi są płaskie.


### Korekta ruchu wycinanek, 30.10.2026

Na podstawie audytu 15-sekundowego przykładu (16025.mp4) stwierdzono fragmentaryczne odsłanianie krajobrazu między 0–6 s, pustą sylwetkę między 7–12 s i niewystarczająco czytelne wejście bohaterów między 10–13 s. Sam MP4 jest **spłaszczonym wynikiem**, nie zestawem źródłowych PNG alpha; nie da się z niego wiarygodnie odtworzyć zasłoniętych fragmentów każdej wycinanki.

- W domyślnym presetcie wszystkie elementy scenografii jadą **w całości** na widocznej nitce od sufitu. Nitka pozostaje przymocowana do górnej krawędzi obiektu i znika po zakończeniu osadzania, pozostawiając punkcik mocowania. Nie używa się animowanego ujawniania fragmentów.
- Postacie nadal korzystają z `rake_lift`, ale wejście jest wolniejsze, z wyraźniejszym pochyleniem i wychyleniem końcowym. Dolna kotwica pozostaje w miejscu.
- Każda postać otrzymuje gruby ciemnobrązowy kontur (domyślnie 12 px), bohater główny 16 px. Poszerzony kontur jest uwzględniany przy obracaniu, by nie obcinać go na granicy sprite'a.
- Każde wejście wymaga **osobnego, kompletnego PNG alpha** z ukrytymi pod okluzją częściami. Dotychczasowe ostrzeżenia o rozłącznych fragmentach alpha nadal obowiązują: należy je sprawdzić i wymienić wadliwe zasoby, a nie maskować ich animacją.
- Zmiany obejmują przyszłe rendery i ponowny render scen na podstawie indywidualnych warstw. Nie rekonstruują automatycznie już wyeksportowanego, spłaszczonego MP4.

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

## Opcjonalne generowanie oddzielnych PNG przez API (30.10.2026)

Studio obsługuje teraz bezpośrednie, **ręcznie inicjowane** generowanie
pojedynczego PNG alpha w trybie Reference-to-layers przez OpenAI Images Edit API.

1. W **Połączeniach** ustaw osobny klucz obrazowy, obsługiwany model
   (GPT Image 2.5 Sunburst lub Flare) i konserwatywny, dodatni szacunkowy koszt
   pojedynczej próby. Ustaw także dodatni limit API projektu. Klucze pozostają
   poza eksportami i repo; można użyć zmiennych `DOCOS_PAPER_IMAGE_KEY`,
   `DOCOS_PAPER_IMAGE_MODEL`, `DOCOS_PAPER_IMAGE_REQUEST_COST`.
2. Utwórz/zaimportuj i **jawnie zaakceptuj** draft. Utwórz listę osobnych
   obiektów, sprawdź identyfikatory i kliknij **Wygeneruj pojedynczy PNG alpha
   z referencji** przy konkretnym obiekcie.
3. Aplikacja wysyła zatwierdzony obraz jako referencję stylu, żąda
   `background=transparent` i `output_format=png`, weryfikuje format
   oraz rzeczywiste niepuste alpha, a wynik dodaje do biblioteki.
4. Wynik pozostaje **nieprzypisanym wariantem**: obejrzyj go, oceń styl i
   ręcznie powiąż z obiektem; wygenerowanie nie zmienia automatycznie
   montażu ani zatwierdzonych grafik.
5. Jeśli obiektów jest dużo, po akceptacji referencji możesz uruchomić
   **serię maksymalnie 12 brakujących wycinków** w jednym zadaniu. UI
   pokaże łączny szacowany koszt przed wysyłką i poprosi o potwierdzenie.
   Każda warstwa jest generowana osobno i rezerwowana osobno; anulowanie
   nie usuwa już zapisanych wariantów. Częściowe niepowodzenia są raportowane,
   a gotowe pliki pozostają w bibliotece bez automatycznego przypisania.
6. Wcześniej wygenerowany wariant nie jest naliczany ponownie przypadkowo:
   wybierz go z biblioteki, a dodatkowy wariant zlecaj tylko świadomie,
   osobnym przyciskiem z potwierdzeniem kosztu.
7. Jeżeli dostawca zwróci obraz bez alpha, zadanie kończy się błędem;
   nie wycinamy fałszywego tła. Ręczny import PNG działa bez klucza.

Szacunek kosztu jest **rezerwowany przed żądaniem**, również w przypadku
nieudanej próby, ponieważ dostawca może ją rozliczyć. Połączone konto API
i płatne generowanie **nie były testowane w trybie live**. Integracja ma
testy kontraktowe, ale spójność estetyczna nie jest gwarantowana. Nie
traktujemy jej jako automatycznej akceptacji wszystkich warstw ani
ukończenia benchmarku 1:1.

## Workflow domyślny: Reference-to-layers (aktualizacja 29.10.2026)

**Najnowsza decyzja:** po ustaleniu scenariusza i beatów tworzymy najpierw **mały draftowy obraz całej sceny** (np. 512 × 288), który pokazuje kompozycję, proporcje i wspólny styl. Dopiero gdy jest zaakceptowany, z jego pomocą tworzymy **Scene Object Manifest** i oddzielne przezroczyste PNG dla każdego obiektu. Obraz draftowy jest wyłącznie referencją i nigdy nie stanowi spłaszczonego tła lub materiału do nieprecyzyjnego wycinania. **Reference-to-layers jest teraz domyślną opcją**. **Asset-first** bez obrazu poglądowego pozostaje pełnoprawną alternatywą.

### Etapy

1. **Scenariusz → mały draft:** opis sceny/narracja i spójna stylistyka służą do wygenerowania poglądowego obrazu kompozycji. Aplikacja potrafi przygotować prompt, wygenerować PNG 512 × 288 przez istniejący lokalny image worker (po konfiguracji DOCOS_IMAGE_PYTHON) albo przyjąć własny PNG/JPEG. Przed przejściem dalej użytkownik wybiera referencję, może opisać jej najważniejsze cechy i **jawnie akceptuje kompozycję**.
2. **Reference → lista obiektów:** model wizualny podłączony przez zgodny endpoint chat/completions z obsługą obrazów może, po wyraźnym kliknięciu użytkownika, przeanalizować draft i zwrócić listę obiektów oraz pozycje. Bez takiego modelu listę można przygotować ręcznie albo w innym narzędziu; nie udajemy, że model tekstowy widzi obraz.
3. **Scene Object Manifest:** każdy element jest niezależnym rekordem z `id`, `name`, `description`, `group`, `x`, `y`, `width`, `z`, `asset_id` (na początku pustym) i opcjonalnym `duration`. Grupy ustalają wejścia, **Z ustala przesłanianie**. `x` to środek poziomy, `y` to dolny punkt wycinka, `width` to część szerokości kadru.
4. **Jedna linia artystyczna:** globalny `style` zasila wszystkie per-obiektowe prompty. Nie wolno dopuścić do postaci w innym oświetleniu, odcieniu papieru lub technice kreski niż reszta dioramy.
5. **Generowanie pojedynczych zasobów:** osobny prompt dla każdej chmury, budynku, drzewa, monety i postaci. Generator musi zwrócić rzeczywisty **RGBA PNG** z przezroczystym tłem i jednym obiektem. Aplikacja przygotowuje i eksportuje prompty oraz wczytuje i wiąże gotowe PNG. **Lokalny image worker nadal nie zapewnia generacji alpha PNG.** Osobny opcjonalny adapter zewnętrznego API jest dostępny po konfiguracji własnego klucza i wymaga weryfikacji rzeczywistego wyniku przez autora.
6. **Scene Layout Planner:** render umieszcza obraz na podstawie współrzędnych i szerokości ze spisu; wycina przezroczyste marginesy, nie rozciąga obiektu i nie wymaga płótna wielkości całego filmu. Niezależne `z_index` odpowiada za to, co jest przed czym.
7. **Staging i rigging:** `sky/landscape/foundations/vegetation/props = hanging_drop` (pełny obiekt zjeżdża na nitce od górnej krawędzi, kołysze się, zatrzymuje i zostaje przypięty); `characters/hero = rake_lift` (kartonowa figurka składa się wokół dolnego punktu podparcia i staje pionowo). `bottom_rise` pozostaje opcjonalnym ruchem wybranym ręcznie. Każdy obiekt ma osobny czas. Hero wchodzi ostatni, a wszystkie postacie mają wyraźny ciemny obrys; hero jeszcze grubszy.
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

- Bezpośredni opcjonalny adapter API transparent PNG jest zaimplementowany. **Wciąż otwarte:** test z prawdziwym kontem, spójność stylu, pełne automatyczne zatwierdzanie kompozycji, jakościowa zgodność wszystkich obiektów i niezawodność na docelowym sprzęcie. Batch (do 12) jest wdrożony jako oddzielne zadanie z kontrolą kosztu.
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

## Scenograf: najpierw porównanie, potem decyzja autora (30.10.2026)

Paper Theatre pozostaje warsztatem scenografii. Montaż składa kompletne ujęcie:
po zatwierdzeniu rozmieszczenia można dodać głos, dymki/plansze, nakładki,
dźwięk i ruch klipów. Z inspektora klipu Paper Theatre można wrócić bezpośrednio
do scenografii przez **Scenograf · układ i porównanie z referencją**.

1. Ustal referencję i przygotuj osobne wycinki. Zgoda na wzór kompozycji nie jest
   zgodą na wynik złożenia PNG.
2. Ustaw obiekty istniejącym edytorem przeciągania, masek, skali, pivotów i Z.
   Edytor przycina PNG do rzeczywistego obrysu alfa, tak jak renderer.
3. **Złóż układ i pokaż porównanie** przygotowuje pojedynczą klatkę właściwego
   kompozytora, po zakończeniu wejść. Nie tworzy MP4. **Porównaj zapisany układ**
   ocenia aktualne warstwy i nie składa starego manifestu na nowo, co ma znaczenie
   po przyjęciu wycinków z „Rozetnij ponownie”.
4. W Scenografie porównaj obrazy obok siebie albo nakładką z regulacją widoczności.
   Opcjonalny przycisk **Scenograf AI** wysyła oba obrazy do połączonego modelu
   obsługującego obrazy lub Claude CLI. Wynik zawiera konkretne rozbieżności
   i zalecane poprawki. Brak dostawcy lub jego błąd jest pokazywany jako błąd,
   nigdy jako udana ocena. Uwagi modelu wymagają weryfikacji człowieka.
5. Autor sprawdza proporcje, położenie/przesłanianie i styki (np. pióra z księgą),
   odsyła układ do poprawy albo jawnie akceptuje pokazany wynik. Akceptacja
   krytycznych uwag wymaga opisania świadomego odstępstwa. Model nie akceptuje
   pracy za autora. Nie ma deklarowanego wyniku „95% podobieństwa”.
6. Dopiero potem przekaż scenę do Montażu i oceniaj kompletne ujęcie z ruchem,
   dialogami i nakładkami przed eksportem.

Akceptacja jest związana z treścią plików, referencją, układem, cue, rozmiarem
kadru, stylem oraz wersją kompozytora. Po ich zmianie potrzebne są nowe porównanie
oraz decyzja. Niezwiązana zmiana tytułu projektu nie unieważnia oceny obrazu.
Ręcznie pocięte klipy mogą zachować własne cięcia; warstwy na osi muszą odpowiadać
zatwierdzonej scenografii. Akceptacja układu nie jest oceną historycznej prawdziwości
ani automatycznym zatwierdzeniem późniejszych nakładek, dialogów i ruchu kamery.

Ochrona API obejmuje przekazanie scenografii do montażu i eksport MP4 (również
roboczy). Pojedyncze klatki kontrolne pozostają dostępne. Dotyczy nowych scen,
rekonstrukcji `reference-guided` i scen świadomie włączonych do recenzji. Starsze,
ręcznie przygotowane warstwy bez tego workflow zachowują poprzednie działanie;
wyciszone ścieżki nie blokują renderu pozostałej części filmu. Nie nadpisuje się
starych eksportów ani nie oznacza ich jako zaakceptowanych.
