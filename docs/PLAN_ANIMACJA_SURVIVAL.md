# Plan: animowany survival 2D „20× lepiej” — film i rozbudowa DocOS Studio

Stan: 28.10.2026. Dokument planistyczny — nic z poniższej rozbudowy nie jest jeszcze wdrożone.
Powiązane: [STUDIO.md](STUDIO.md), [STUDIO_WORKSPACE.md](STUDIO_WORKSPACE.md), [STUDIO_RESOURCE_MODEL.md](STUDIO_RESOURCE_MODEL.md), [STUDIO_IDEAS.md](STUDIO_IDEAS.md).

## 0. W skrócie

- Cel: długie (12–15 min odcinki → 40–45 min „Full Movie”) animowane opowieści survivalowe w 2D, opowiadane w drugiej osobie, z prawdziwą wiedzą o przetrwaniu.
- „20× lepiej” nie mierzymy wyświetleniami (tych nie da się obiecać), tylko scorecardem 10 wymiarów jakości (rozdz. 3). Największe przewagi: **zero błędów ciągłości**, **postać i lokacje z jednego, wielokrotnie używanego zestawu** (nie losowe kadry AI), **prawdziwa animacja i reżyseria dźwięku**, **czytelna informacja wizualna (zapasy, mapa, dzień/godzina)**.
- Aplikacja ma dziś mocny fundament (research, fakty, lektor, napisy z czasów słów, wielościeżkowy montaż, Remotion, banki pracowni), ale jest zbudowana pod dokument. Brakuje: **Story Bible i stanu świata**, **studia postaci (rig)**, **studia lokacji**, **silnika scen „Stage”**, **storyboardu/animatiku**, **obsady głosowej**, **warstwy sound designu**, **serii i kompilacji**.
- Kolejność: decyzje i style guide → model danych + kontrola ciągłości → silnik Stage z rigiem → lokacje → animatik + głos → dźwięk → **pionowy wycinek 3–5 min** porównany z referencją → dopiero potem odcinek 1.

## 1. Na czym oparty jest plan

| Źródło | Co z niego wzięliśmy |
|---|---|
| Film referencyjny: StickFallout, *Zombie Outbreak Survival: Day 1 To Day 100 (Full Movie)*, 43:50, ok. 422 tys. wyświetleń po 10 dniach (odczyt 28.10.2026) | Pełna transkrypcja, opis, rozdziały, 60 najwyżej ocenianych komentarzy, miniatura, kilka klatek |
| Katalog kanału StickFallout | Kadencja, wyniki części i kompilacji, spadek w sezonie 2 |
| 4 rozmowy z ChatGPT | Porównanie z produkcją „na 3 promptach”, przebudowa na uniwersalne studio, analiza WhyThat i plan „20× lepiej”, ranking świeżych kanałów 2D |
| `docs/` i kod (`studio_core`, `studio_timeline`, `studio_workers`, `apps/studio`) | Stan aplikacji i luki (rozdz. 6) |
| Pamięć Claude dla tego repo | Była pusta — brak wcześniejszych ustaleń poza dokumentacją i rozmowami |

## 2. Anatomia filmu referencyjnego

### Co robią i co działa

| Element | Jak to wygląda | Wniosek dla nas |
|---|---|---|
| Rama | „Ty” jako bohater, licznik dni, godziny jako haki (6:14 rano wraca na początku i na końcu) | Zachować drugą osobę i motyw godziny; to tani, silny „loop” |
| Tajemnica | Trzy stuknięcia, głosy w radiu, „nie schodź na dół”; finał wyjaśnia wszystko ludzkimi przyczynami | Tajemnica z uczciwymi wskazówkami trzyma 44 min — komentarze chwalą konstrukcję i „nie zgadłem” |
| Wiedza | Woda (galon/osobę/dzień), sanitacja, psujące się jedzenie, wychłodzenie, nawodnienie doustne | Edutainment = wartość dla widza; u nas każda porada idzie przez bank faktów ze źródłem |
| Narracja | ok. 8 200 słów / 43:50 ≈ **188 słów/min**, jeden lektor AI czyta też kwestie postaci | Szybkie tempo jest normą gatunku; dialogi bez osobnych głosów to luka do wykorzystania |
| Obraz | Patyczak z czerwoną czapką (stały znak rozpoznawczy) na szczegółowych, ilustrowanych tłach AI; ograniczony ruch; wypalone napisy | Spójny „znak” postaci działa; reszta obrazu to nasza szansa |
| Pakowanie | 3 części po 12–16 min → kompilacja „Full Movie”; miniatura „DAY 1 vs DAY 100” w tej samej kuchni | Seria + kompilacja to sprawdzony model; miniatura „przed/po” wymaga stanów lokacji |
| Kadencja | S1: 7.10, 14.10, 15.10, kompilacja 18.10; S2 codziennie 21–25.10, kompilacja 26.10; S3 od 27.10 | Konkurencja publikuje co 1–3 dni — nasz pipeline musi być szybki, a nie tylko ładny |

Wyniki kanału (odczyt 28.10.2026): część 1 — 869 tys. (3 tyg.), część 2 — 255 tys., część finałowa — 97 tys., kompilacja S1 — 422 tys. (10 dni). Sezon 2 spada szybko: 70 → 39 → 32 → 27 tys., kompilacja S2 — 30 tys. po 2 dniach. To sygnał zmęczenia formułą — przewagą nie może być „ten sam schemat szybciej”, tylko wyraźnie lepsze wykonanie i świeży świat.

### Słabe punkty (z dowodami)

- **Odbiór „to AI”.** Najwyżej oceniany komentarz widza (304 polubienia): „I wish it was real art not ai”. Kilka innych komentarzy też nazywa film AI.
- **Błędy ciągłości.** Woda w kranie znika 2. dnia, a ok. 6:05 bohater myje ręce pod płynącym kranem — sprawdziliśmy klatkę; widzowie to wyłapali. Inny komentarz kwestionuje wygląd wizjera.
- **Dźwięk wybijający z immersji.** Śmiech ok. 19:00 wywołał falę komentarzy (część żartem, ale to moment, w którym widz przestał być „w środku” historii).
- **Obietnica tytułu.** Komentarz ze 161 polubieniami (i kolejne podobne) zauważa, że w historii o zombie prawie nie ma zombie — puenta jest celowa, ale ryzykowna.
- **Formułki.** Powracające „oto czego nikt ci nie mówi” (ChatGPT znalazł to samo u WhyThat).

## 3. Co znaczy „20× lepiej” — scorecard

Każdy wymiar oceniamy 1–5 dla referencji i naszego pilota, plus miernik obiektywny tam, gdzie się da. Pilot przechodzi dalej dopiero, gdy wygrywa w co najmniej 8 z 10 wymiarów.

| # | Wymiar | Referencja | Nasz cel | Jak mierzy aplikacja |
|---|---|---|---|---|
| 1 | Ciągłość świata | błędy zauważone przez widzów | 0 błędów po kontroli ciągłości i przeglądzie | Raport kontroli ciągłości (6.2) |
| 2 | Spójność postaci | stały znak, ale rysowane kadr po kadrze | 100% ujęć z jednego rigu | Każde ujęcie postaci odwołuje się do wersji rigu |
| 3 | Animacja | głównie pozy + lekki ruch | akcja w każdym ujęciu, zmiana pozy/kamery co ≤4 s, cykle chodu, światło | Statystyka akcji/min z danych Stage |
| 4 | Wygląd „rękodzieła” | ilustracje AI | własny style guide, plansze lokacji dopracowane ręcznie, AI najwyżej jako podmalówka | Style guide + zatwierdzenie każdej planszy |
| 5 | Informacja wizualna | w obejrzanych klatkach brak | HUD zapasów (woda L, jedzenie, bateria), plan budynku, karta dnia/godziny | HUD liczony ze stanu świata, nie wpisywany ręcznie |
| 6 | Dźwięk | efekty + muzyka, wpadki | ambienty per lokacja, foley, „za ścianą/drzwiami”, cisza jako narzędzie | Arkusz cue + kontrola szczytów |
| 7 | Historia | dobra tajemnica, formułki | cel osobisty bohatera, obsada z własnymi interesami, rejestr zapowiedzi i rozwiązań, zero formułek | Rejestr setup/payoff + detektor powtórzeń |
| 8 | Wiedza survivalowa | prawdziwe porady bez źródeł na ekranie | każda porada w banku faktów (CDC, FEMA, WHO, Czerwony Krzyż); źródła w opisie | Istniejący bank faktów |
| 9 | Głosy | jeden lektor | wyreżyserowany narrator + 3–4 rozpoznawalne głosy postaci | Obsada i reżyseria zdań (6.7) |
| 10 | Pakowanie | seria + kompilacja | seria + kompilacja + miniatury renderowane z tego samego rigu i stanów lokacji | Kompozytor miniatur (6.10) |

Wymóg produkcyjny: odcinek 12–15 min w ≤4 dni pracy na obecnym Macu (8 GB RAM), kompilacja w 1 dzień. Wyniki na YouTube to hipoteza do sprawdzenia, nie obietnica.

## 4. Koncepcja filmu (do decyzji autora)

**Format:** sezon = 3 części po 12–15 min („Day 1 → Day 30”, „Day 31 → 60”, „Day 61 → 100”) + kompilacja. Druga osoba zostaje, ale dochodzi stała obsada z własnymi głosami.

**Zasada wyboru tematu:** jedna główna lokacja z kilkoma pomieszczeniami — plansze i plan budynku robimy raz, a używamy setki razy; widz uczy się geografii miejsca, a stan miejsca (barykady, woda, światło) pokazuje upływ czasu bez słów.

Kandydaci (z rozmów z ChatGPT; to hipotezy, nie potwierdzone nisze):

- „30 dni na stacji polarnej. Ostatni samolot nie przyleci” — mróz, paliwo, światło, izolacja.
- „30 dni na promie. Każda noc odbiera kolejne pomieszczenie” — kurcząca się mapa jako naturalny HUD.
- „30 dni w schronie. Ktoś na zewnątrz zna twoje imię” — najbliżej sprawdzonego schematu tajemnicy.

Zwykła podmiana zagrożenia (zombie → blackout) odpada — taki kanał już istnieje. Postać, świat i historia muszą być w pełni własne: żadnej czerwonej czapki, żadnych motywów fabularnych StickFallout.

**Szkielet każdej historii** (ChatGPT, rozmowa 3): bohater czegoś chce → konkretne ograniczenia → konsekwencje wcześniejszych decyzji → największy kryzys i kosztowny wybór → emocjonalne domknięcie. Każda scena musi zmieniać akcję, relację, wiedzę albo atmosferę; jeśli przez kilka minut zmienia się tylko licznik dni — scenariusz wraca do poprawki.

## 5. Docelowy przebieg produkcji odcinka

| Etap | Co powstaje | Moduł aplikacji | Bramka |
|---|---|---|---|
| 1. Pomysł | brief, warianty historii, ocena | Pomysł (jest) | wybór historii |
| 2. Biblia serii | postacie, lokacje, przedmioty, zasady świata, tajemnice, oś czasu | **Story Bible (nowe)** | zatwierdzenie biblii |
| 3. Research | porady survivalowe jako fakty ze źródłami | Fakty i research (jest) | każda porada ma źródło |
| 4. Scenariusz | sceny z dniem/godziną/miejscem/obsadą/zmianami zapasów + narracja i kwestie | Scenariusz (rozbudowa) | **kontrola ciągłości = 0 błędów** |
| 5. Storyboard | kadr każdego ujęcia z rigu i planszy | **Storyboard (nowe)** | przegląd planszy kadrów |
| 6. Animatik | cały film z tymczasowym głosem (Kokoro) i szkicowym ruchem | **Animatik (nowe)** | obejrzenie całości, cięcia nudy |
| 7. Głos | narrator + obsada, reżyseria zdań | Lektor (rozbudowa) | odsłuch, dogrywki |
| 8. Animacja | sceny Stage zsynchronizowane z czasami słów | **Stage (nowe)** | kontrola akcji/min |
| 9. Dźwięk | ambienty, foley, muzyka, cisza | **Sound design (nowe)** | kontrola szczytów i LUFS |
| 10. Montaż i eksport | oś, napisy, MP4, opis ze źródłami | Montaż/Eksport (jest) | scorecard |
| 11. Seria | kompilacja, miniatury, rozdziały | **Seria (nowe)** | — |

## 6. Braki w aplikacji i co dobudować

| Moduł | Stan dziś (kod) | Co dodać | Priorytet |
|---|---|---|---|
| Profil produkcji | `Project.film_format` to tekst; Story Lock wymaga faktów VERIFIED/DISPUTED z URL dla całej historii | profil „Animowana opowieść”: fikcja nie potrzebuje źródeł, porady survivalowe tak | krytyczny |
| Story Bible i stan świata | brak | modele postaci, lokacji, przedmiotów, zasad, tajemnic, osi czasu; stan per scena | krytyczny |
| Kontrola ciągłości | `quality.py` sprawdza gotowość historii i osi czasu, nie stan świata | reguły stanu świata + przegląd AI | krytyczny |
| Studio postaci | brak; obrazy tylko z SD 1.5 (`image_worker.py`) | rig wektorowy, pozy, mimika, akcesoria, rany | krytyczny |
| Silnik scen Stage | Remotion: 5 szablonów wstawek, maks. 60 s, H.264 bez alfy | kompozycja sceny: warstwy, postacie, rekwizyty, kamera, światło, FX, HUD | krytyczny |
| Studio lokacji | jest parallax z gotowych warstw PNG | plansze warstwowe, stany, oświetlenie, punkty zaczepienia, plan budynku | wysoki |
| Storyboard i animatik | brak | kadry z danych Stage, animatik z Kokoro | wysoki |
| Obsada i reżyseria głosu | Chatterbox: jeden profil, stałe `exaggeration`/`cfg_weight` | mówca per kwestia, profile postaci, parametry per zdanie | wysoki |
| Sound design | miks = `amix` + limiter; ducking | bank SFX/ambientów z licencjami, cue sheet przy słowach, filtry per klip | wysoki |
| Napisy wypalane | SRT/VTT, ścieżka tekstowa | styl kanału renderowany w Stage | średni |
| Seria i kompilacja | banki pracowni, szablony | sezon/odcinek, kompilacja z rozdziałami, kompozytor miniatur | średni |
| Agenci i skill | skill `dokument-scenariusz`, asystent montażu | skill fabularny ze zmianami stanu świata | średni |
| Analityka | ręczny punkt odniesienia | import CSV retencji z YouTube Studio na oś | później |

### 6.1 Profil „Animowana opowieść”

- `film_format = "animated_story"` uruchamia inne etapy: Story Bible zamiast Story Lock, scenariusz scenami zamiast beatami dokumentu (beaty zostają jako plan energii).
- Fakty dotyczą tylko świata rzeczywistego (porady, liczby, zjawiska). Fikcja ma status „fikcja” w biblii i nie przechodzi przez walidator faktów.
- Projekty dokumentalne działają bez zmian; migracja `docos-studio/2` → `/3` z wartościami domyślnymi.

### 6.2 Story Bible, stan świata i kontrola ciągłości

Nowe rekordy (poziom serii w banku pracowni, migawka w odcinku — zgodnie z [STUDIO_RESOURCE_MODEL.md](STUDIO_RESOURCE_MODEL.md)):

- **Postać:** imię, rola, cel, interes, granica, głos, rig + wersja, stałe cechy, stan (rany, ubranie, ekwipunek, wiedza) od dnia X.
- **Lokacja:** pomieszczenia, plan, połączenia, odległości, stany (np. `czysta`, `zabarykadowana`, `zalana`, `ciemna`) od dnia X.
- **Przedmiot / zasób:** ilość i jednostka (woda w litrach, jedzenie w dniach, baterie w %).
- **Zasada świata:** np. „woda z sieci: brak od dnia 2, 10:42”, „prąd: brak od dnia 4”, „hałas przyciąga zagrożenie w promieniu…”.
- **Tajemnica:** zapowiedź (scena), wskazówki (sceny), rozwiązanie (scena).
- **Scena:** dzień, godzina, lokacja + stan, obsada, użyte przedmioty, czynności, zmiany zasobów (`woda -2 L`).

Reguły kontroli (deterministyczne, przed AI):

- czynność wymagająca zasobu, którego nie ma (mycie rąk pod kranem po dniu 2 → błąd, dokładnie przypadek z referencji);
- przedmiot użyty przed zdobyciem; zasób poniżej zera; rana znikająca bez leczenia;
- godzina/dzień cofające się bez oznaczenia retrospekcji; podróż szybsza niż pozwala odległość;
- tajemnica bez rozwiązania; rozwiązanie bez wcześniejszej wskazówki;
- HUD i narracja podają różne liczby (HUD liczony ze stanu, więc narracja jest sprawdzana względem niego);
- powtarzane formułki i frazy (próg powtórzeń na film).

Potem przegląd AI („dlaczego nie wybrali prostszego rozwiązania?”) jako propozycja do zatwierdzenia, nie automatyczna zmiana.

### 6.3 Studio postaci (rig)

Wybór techniczny: **wektorowy rig 2D renderowany w Remotion**, nie generowanie postaci obrazkowym AI. Powód: 100% spójności, zerowy koszt generowania, poprawka jednej pozy bez ruszania reszty, render deterministyczny.

- Szkielet: głowa, szyja, tułów, ramię/przedramię/dłoń, udo/łydka/stopa; obrót stawów i kolejność warstw.
- Widoki: przód, 3/4, profil, tył (osobne zestawy rysunków dla tych samych kości).
- Biblioteka póz (start ~25): stoi, idzie, biegnie, kuca, podgląda, nasłuchuje, niesie, pije, pisze, śpi, zaskoczenie, strach, ulga, barykaduje, siedzi, wspina się, leży ranny…
- Cykle: chód, bieg, skradanie, oddech w bezruchu, drżenie z zimna.
- Mimika: oczy, brwi, usta (zestaw ~12 emocji) + mruganie; proste „kłapanie” ust z amplitudy dla kwestii dialogowych (pełny lip-sync poza zakresem v1).
- Akcesoria i stany: plecak, latarka, opatrunek, brud/zmęczenie od dnia X — przypięte do kości dłoni/pleców.
- Znak rozpoznawczy postaci projektujemy sami (kształt sylwetki + 1 kolor akcentu).
- Edytor: podgląd pozy, suwaki stawów, zapis pozy do biblioteki, wersjonowanie rigu w banku pracowni.

### 6.4 Studio lokacji

- Plansza = warstwy (tło, środek, pierwszy plan) do paralaksy i przechodzenia postaci „za” meblami.
- Stany planszy powiązane z dniami (z biblii) — ta sama kuchnia „Day 1” i „Day 100” do miniatury i do filmu.
- Presety światła: dzień, zmierzch, noc, latarka, świeca; nakładane w Stage, nie malowane osobno.
- Punkty zaczepienia: drzwi, okno, zlew, łóżko — postać „staje przy zlewie” zamiast ręcznych współrzędnych; geografia zostaje stała między ujęciami.
- Plan budynku (wektor) do HUD-u i scen „mapy”.
- Źródło grafiki: style guide + jedna z trzech dróg (decyzja w rozdz. 9) — ręczne malowanie, lokalny model, zewnętrzne API. SD 1.5 na 8 GB daje za słabą jakość i spójność na plansze główne; można go użyć do szkiców kompozycji. Każda plansza wymaga ręcznego zatwierdzenia i trafia do banku mediów z licencją/pochodzeniem.

### 6.5 Silnik scen „Stage” (Remotion)

Nowa kompozycja obok obecnych wstawek; scena opisana JSON-em, renderowana tym samym komponentem w podglądzie i w eksporcie (jak dziś wstawki). Przykład ujęcia:

```json
{
  "shot_id": "S03_04",
  "day": 2, "time": "03:17",
  "location": {"id": "loc_mieszkanie", "state": "zabarykadowane", "light": "noc"},
  "camera": {"framing": "plan średni", "move": [{"at_word": 12, "to": {"zoom": 1.3, "x": -0.1}, "ease": "inOut", "frames": 40}]},
  "cast": [{
    "character": "chr_ty", "anchor": "drzwi_wejsciowe", "view": "3/4",
    "actions": [
      {"at_word": 3, "pose": "nasluchuje", "expression": "strach"},
      {"at_word": 15, "pose": "cofa_sie", "frames": 18}
    ]
  }],
  "props": [{"id": "klamka", "anim": "obrot", "at_word": 9, "repeat": 2}],
  "fx": [{"type": "drgania_kamery", "at_word": 21, "strength": 0.3}],
  "hud": {"woda_l": "auto", "dzien": true},
  "captions": "styl_kanalu"
}
```

- Synchronizacja z czasami słów z faster-whisper (już są w `Scene.words`), więc akcja trafia dokładnie w „trzy stuknięcia”.
- Kamera: kadr, najazd, panorama, drgania, rozmycie ostrości; przejścia z obecnej osi.
- FX: deszcz, kurz, dym, migotanie światła, stożek latarki, winieta.
- HUD liczony ze stanu świata (6.2).
- Długość: ujęcie dowolne, render w kawałkach z cache po hashu danych ujęcia (jak segmenty w `render_doc.py`) — zdejmuje limit 60 s wstawki.
- Renderowanie lokalne bez chmury; wydajność (klatki/s dla 1080p na 8 GB) mierzymy benchmarkiem w fazie 2, zanim obiecamy czasy produkcji.

### 6.6 Storyboard i animatik

- Storyboard: jedna klatka z każdego ujęcia (render pojedynczej klatki Stage) + opis i czas; widok siatki do przeglądu całego odcinka.
- Animatik: całość z szybkim głosem Kokoro i uproszczonym ruchem — oglądamy 45 min historii, zanim zainwestujemy w finalny głos i dopracowanie.

### 6.7 Obsada i reżyseria głosu

- Kwestia ma mówcę: narrator lub postać; narrator nie czyta już cudzych kwestii.
- Profil głosu per postać (prywatne próbki za zgodą, jak dziś); parametry Chatterbox (`exaggeration`, `cfg_weight`, `temperature`, tempo, pauza) **per zdanie**, z presetami: szept, napięcie, ulga, krzyk zza drzwi.
- Słownik wymowy i cache zdań — bez zmian.
- Uwaga czasowa: Chatterbox na CPU jest ok. 10× wolniejszy od czasu rzeczywistego, więc 45 min narracji to noc generowania; animatik używa Kokoro, finał generujemy raz po zamknięciu tekstu.

### 6.8 Sound design

- Bank dźwięków (CC0/własne nagrania) z tagami i licencją w banku mediów pracowni.
- Ambient przypisany do stanu lokacji (deszcz, wiatr, odległe syreny, cisza miasta) — wstawia się sam.
- Cue sheet: efekt przy słowie lub akcji Stage (stuknięcie, klamka, brzęk miski).
- Filtry per klip w miksie FFmpeg: dolnoprzepustowy („za drzwiami”), pogłos pomieszczenia, panorama zgodna z pozycją postaci, EQ; dziś miks ma tylko `amix` + limiter.
- Znaczniki ciszy przed puentą (DocOS miał `silence_before`).
- Kontrola: szczyty względem otoczenia (żeby nie było „wybijającego śmiechu”), LUFS −14.

### 6.9 Napisy wypalane

Styl kanału (krój, kolor, tło, maks. 2 linie) renderowany w Stage z istniejących czasów słów; SRT/VTT zostają do wgrania na YouTube.

### 6.10 Seria, kompilacja i miniatury

- Sezon w pracowni: biblia serii + lista odcinków (osobne projekty).
- Eksport „Full Movie”: sklejenie odcinków bez ponownego renderu, rozdziały w opisie, wspólne źródła i atrybucje.
- Kompozytor miniatur: szablon (np. „przed/po”) wypełniany rigiem w wybranej pozie i stanami lokacji — miniatura zawsze zgodna z filmem.
- Opis: źródła porad, atrybucje, informacja o użyciu AI i ustawienie YouTube „Altered or synthetic content”, gdy dotyczy.

### 6.11 Bramki jakości (przed eksportem finalnym)

1. Kontrola ciągłości: 0 błędów.
2. Każda porada survivalowa ma fakt ze źródłem.
3. Rejestr tajemnic domknięty.
4. Akcje/min i różnorodność ujęć ≥ progów profilu.
5. Dźwięk: brak szczytów ponad próg, LUFS −14.
6. Detektor formułek i powtórzeń.
7. Scorecard pilota wypełniony.

### 6.12 Agenci i skill

- Nowy skill `animacja-opowiesc` (wzorowany na `dokument-scenariusz`): pisze scenę po scenie i zwraca narrację, kwestie oraz **zmiany stanu świata** w JSON; walidator odrzuca scenę sprzeczną z biblią.
- Role jako etapy, nie osobne procesy (ChatGPT, rozmowa 3): scenarzysta, redaktor dramaturgii, kontroler ciągłości. Autor pierwszej wersji nie jest jej jedynym recenzentem.
- Propozycje AI do Stage (pozy, kamera, efekty) idą przez istniejący mechanizm propozycji z rewizją i cofaniem; AI nie uruchamia kodu.

### Czego świadomie nie robimy w v1

Blender/Grease Pencil, generowania wideo AI, pełnego lip-sync, rysowania klatka po klatce, 3D. Każde z nich podnosi koszt lub psuje spójność na 8 GB RAM, a nie jest potrzebne do pokonania referencji.

## 7. Kolejność wdrożenia i kryteria odbioru

| Faza | Zakres | Gotowe, gdy |
|---|---|---|
| 0. Decyzje | rozdz. 9, style guide, szkic postaci, wybór tematu pilota | style guide i jedna strona historii zatwierdzone |
| 1. Fundament | profil `animated_story`, migracja schematu, modele Story Bible i stanu sceny, kontrola ciągłości (reguły) | test: scena „mycie rąk pod kranem” w dniu 3 zgłasza błąd; dokumenty działają jak wcześniej |
| 2. Stage + rig | kompozycja Stage, rig z ~25 pozami, 3 cykle, mimika, kamera, HUD, render w kawałkach z cache, benchmark | 30 s sceny z akcjami przy słowach renderuje się lokalnie; zmiana jednej pozy przerenderowuje tylko to ujęcie |
| 3. Lokacje | studio lokacji, pierwsza lokacja z 4 stanami i planem | ta sama lokacja w 4 stanach w jednym ujęciu testowym |
| 4. Storyboard, animatik, głos | siatka kadrów, animatik z Kokoro, obsada i reżyseria zdań | cały scenariusz pilota oglądalny jako animatik |
| 5. Dźwięk | bank, ambienty, cue sheet, filtry per klip, kontrola szczytów | scena „za drzwiami” brzmi stłumiona; raport szczytów czysty |
| 6. Pionowy wycinek | 3–5 min w jakości finalnej | wygrana w ≥8/10 wymiarach scorecardu względem referencji, ocena autora + 2–3 widzów testowych |
| 7. Odcinek 1 | 12–15 min, publikacja | wszystkie bramki 6.11 zaliczone |
| 8. Seria | odcinki 2–3, kompilacja, miniatury, skill | kompilacja bez ponownego renderu; pierwsze dane retencji wpięte w punkt odniesienia kanału |

Fazy 1–5 to zmiany w aplikacji; 6–8 to produkcja. Część zadań z faz 2 i 3 (rig vs plansze lokacji) można robić równolegle.

## 8. Ryzyka i ograniczenia

- **Sprzęt (Mac, 8 GB RAM):** wolny Chatterbox na CPU, słaby SD 1.5, nieznana jeszcze wydajność Remotion dla długich scen — stąd benchmark w fazie 2 i animatik na Kokoro.
- **Kadencja konkurencji:** odcinki co 1–3 dni. Jakość musi wynikać z ponownego użycia zasobów (rig, lokacje, dźwięki), nie z ręcznej pracy nad każdym kadrem.
- **Zmęczenie formatem:** spadek sezonu 2 referencji; bez świeżego świata lepsze wykonanie może nie wystarczyć.
- **Polityka YouTube:** oznaczanie treści syntetycznych; zasady monetyzacji wobec masowo powielanych treści — autorski proces pomaga, ale niczego nie gwarantuje.
- **Licencja Remotion:** sprawdzić warunki przy rozwoju kanału/zespołu ([licencja](https://www.remotion.dev/docs/license)).
- **Oryginalność:** gatunek jest wspólny, ale postać, świat i fabuła muszą być własne.

## 9. Decyzje dla autora

### Stan wdrożenia (28.10.2026)

Pierwszy przyrost aplikacji jest gotowy — [instrukcja](STUDIO_ANIMATION.md): przełącznik trybu (Dokument / Animacja 2D / B-roll), bank **postaci z pozami** i bank **lokacji ze stanami** przypisane do kanału (bez przenikania między kanałami), tablica scen w stylu planu zdjęciowego („Scena 23”: lokacja + stan, postacie i pozy, akcja, kamera, narracja/dialog z mówcami, dźwięk), ocena jednym klawiszem (zatwierdź / do poprawki z obszarem i uwagą) oraz regeneracja sceny przez AI jako propozycja do przyjęcia. To realizuje część faz 1–4 z rozdz. 7, w uproszczonej formie: pozy jako gotowe obrazy (rysujesz/generujesz je sam), bez rigu kości, bez ruchu w czasie, bez głosów i bez kontroli ciągłości stanu świata.

Drugi przyrost (28.10.2026): ekran **Storyboard i animatik** — beaty nad scenami, AI rozpisujące beat na sceny z banku kanału, siatka kadrów i odtwarzacz animatiku z roboczymi głosami przeglądarki (osobny głos na postać). Ustalenia z autorem: Blender odpada (za ciężki na tego Maca, ruch 2.5D zrobi Remotion); rig na start prosty (podmiana póz + drobny ruch); model graficzny wybierzemy testem na tych samych postaciach i lokacjach; Google Flow uznany za słaby w trzymaniu spójności.

Trzeci przyrost (28.10.2026): głosy robocze Kokoro, ruch kamery i postaci, pierwszy plan, bank rekwizytów / kostiumów / nakładek, ostrzeżenia o ciągłości rekwizytów i strojów, eksport animatiku do MP4, automatyczne odświeżanie filmu przy zmianach z API.

### Czego jeszcze brakuje (przegląd z 28.10.2026, w kolejności wartości)

1. ~~**Dźwięk**~~ — zrobione 28.10.2026: bank SFX/atmosfer/muzyki z licencjami, efekty i atmosfery w scenach, muzyka na zakresy scen z przyciszaniem pod dialogiem, w animatiku i MP4. Zostaje: wyszukiwarka CC0 (np. Freesound, wymaga klucza API), stereo i finalny miks.
2. **Ciągłość stanu świata:** dzień/godzina, zasoby (woda), rany i wiedza postaci liczone automatycznie (rozdz. 6.2). Dziś ostrzeżenia obejmują tylko rekwizyty i stroje między sąsiednimi scenami.
3. **Generowanie grafik w aplikacji:** adapter API do wybranego modelu (po teście), karta postaci → pozy w tym samym stylu, stany lokacji z jednej bazy.
4. **Mimika i usta przy kwestiach:** zestaw twarzy na postać i zmiana podczas mówienia; rekwizyt „w dłoni”.
5. **Finalne głosy:** decyzja lokalny vs ElevenLabs, reżyseria kwestii, dogrywki.
6. **Animatik → Montaż:** przeniesienie scen na oś czasu, finalny render 1080p z muzyką, napisy SRT/VTT z animatiku.
7. **Seria i publikacja:** kompilacja „Full Movie”, miniatury z rigu i stanów lokacji, opis ze źródłami porad.

### Decyzje



1. ~~**Język kanału**~~ — **zdecydowano 28.10.2026: angielski.** Skutki: profil kanału i projekty z `language = "en"`; narracja, napisy, tytuły i opisy po angielsku; porady survivalowe opieramy na źródłach anglojęzycznych (CDC, FEMA, WHO, Red Cross), z jednostkami podawanymi tak, jak w źródle (np. galony i litry); głos lektora i obsady po angielsku — klon własnego głosu wymaga angielskiej próbki i odsłuchu akcentu (patrz decyzja 4); słownik wymowy w wersji angielskiej.
2. **Temat pilota:** stacja polarna, prom, schron albo własny — z zasadą „jedna główna lokacja”.
3. **Grafika lokacji:** ręcznie, lokalny model czy zewnętrzne API (koszt vs spójność vs czas).
4. **Narrator i obsada głosowa:** rekomendacja z 28.10.2026 — zewnętrzny serwis TTS zamiast lokalnego Chatterbox (na Macu 8 GB generowanie blokuje komputer). Wymaganie autora: 3–5 rozpoznawalnych głosów do scenek. Postać ma już w banku pole dostawcy i ID głosu; integracja generowania jest następnym krokiem po wyborze serwisu.
5. **Grafika postaci:** autor przygotowuje pozy sam (generuje kilka póz tej samej postaci) i wgrywa je do banku postaci kanału.

## 10. Źródła

- Film referencyjny: https://www.youtube.com/watch?v=0O2-Db4zjx0 (metadane, transkrypcja, komentarze — odczyt 28.10.2026 przez TubeAlfred)
- Katalog kanału: https://www.youtube.com/@stickfallout
- Rozmowy ChatGPT: [porównanie jakości](https://chatgpt.com/share/6ae1f20a-35ec-83ed-bc11-1b2d07525eaf), [przebudowa aplikacji](https://chatgpt.com/share/6ae1f241-6fdc-83eb-b220-217ec503f302), [pomysły na kanał](https://chatgpt.com/share/6ae1f255-309c-83ed-9040-c2f622d475a8), [kanały animacji](https://chatgpt.com/share/6ae1f265-e79c-83ed-bf18-6219ebaa4d2e)
- Kod: `studio_core/models.py`, `studio_core/inserts.py`, `studio_timeline/render.py`, `studio_workers/image_worker.py`, `studio_workers/voice_worker.py`, `apps/studio/src/motion/`
