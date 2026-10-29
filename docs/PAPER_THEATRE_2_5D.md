# Paper Theatre 2.5D · standard produkcji DocOS Studio

**Status:** odrębna kategoria Narzędzia produkcji → Paper Theatre 2.5D. Pierwsza implementacja kreatora, planowania sekwencji, walidacji osobnych PNG, renderowania mechanik, podglądu klatki i przekazania do Montażu. Nie mylić z automatycznym rozcinaniem jednolitej grafiki na sto profesjonalnych warstw.

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
- Tło i wszystkie PNG muszą mieć **identyczne wymiary płótna**, żeby utrzymać precyzyjne współrzędne. Wycinek ma przezroczyste otoczenie.
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
