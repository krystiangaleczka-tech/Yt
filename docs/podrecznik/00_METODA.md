# Metoda filmu: od pomysłu do publikacji

Reżyser 28.11.2026, przy czwartym filmie teatru papierowego: „Ty powinieneś mieć wszystko zapisane, jak masz robić — że my
wchodzimy, jest jakiś film, tworzymy jakiś pomysł, studiujemy go, czy jest sens, i jedziemy z tematem”. Ten rozdział jest
przepisem na cały film. Wykonawca prowadzi film według niego sam i przychodzi do reżysera z gotowym, sprawdzonym etapem
— reżyser ocenia grę, rytm i nastrój, wybiera i zatwierdza, ale nie powinien mówić, co jest następnym krokiem. Szczegóły
każdego kroku są w rozdziałach podręcznika i w Wytycznych ujęć (`docs/WYTYCZNE_UJEC.md`); tu jest kolejność i to, co
z nich wynika dla każdego filmu.

## 1. Pomysł i badanie: czy jest sens

1. **Temat z popytem, nie z sympatii.** Trendy i konkurencja na YouTube (TubeAlfred: zapytania, kanały, wyniki filmów —
   narzędzia „batch” liczą 1 kredyt na element; partia nie większa niż saldo). Szukaj tematów, które już mają widzów (filmy
   innych kanałów z dużą liczbą wyświetleń w stosunku do subskrypcji) i nowego wejścia (premiera filmu, rocznica, trend
   formatu jak „The ENTIRE … in N Minutes”).
2. **Trzy kąty opowieści** z dowodami popytu: o czym jest film w jednym zdaniu, kto jest bohaterem, jaki jest zwrot, co widz
   wie na końcu, czego nie wiedział. Kąt musi mieć **akcję na początku** (rozdział 3) — temat bez sceny akcji na start
   wymaga innego kąta.
3. **Tytuł**: przed propozycją sprawdź na YouTube, czy taki już jest; tytuł obiecuje to, co pokazuje pierwsza minuta.
4. **Decyzja reżysera**: idziemy albo nie. Do tego czasu nic nie jest rysowane.

## 2. Szkice ujęć (trzy scenariusze)

Trzy różne scenariusze z hakami jako „Szkice ujęć” w Studio (`docs/filmy/<film>/szkice/`, import
`/api/projects/{id}/sketches/import`). Każdy szkic ma od razu:
- **mapę tempa** (rozdział 3) — gdzie jest pierwsza akcja, gdzie zwroty, gdzie zwolnienie;
- **plan scenografii** (rozdział 4) — lista miejsc i trzy podejścia do każdego rodzaju scenerii;
- **mapę gagów** — coś śmiesznego co ok. 20–25 s poza fragmentami powagi (Podręcznik → Humor i gagi);
- **długość z historii** (8–12 min; dłużej tylko, gdy reżyser zatwierdzi w szkicu).

Reżyser wybiera albo łączy szkice i zatwierdza w Studio. Potem własna gałąź i worktree filmu (Jak pracujemy, krok 3).

## 3. Tempo filmu: początek w akcji

**Dane.** „Pierwszy cesarz”: 50 % widzów zostało do 15 s, 35 % do 30 s, 21 % do 60 s, a kto przetrwał ok. 4 minut, zostawał
do końca. „Bonnie and Clyde”: kto kliknął, oglądał średnio 8:34, ale wejść było mało. Reżyser 28.11: „w każdym naszym filmie
dopiero po 2–3 minutach zaczyna się jakaś akcja i on jest angażujący”. W „Imamie / Diunie” (szkic E) pierwsza akcja była
w 1:14, przed nią same objaśnienia. Wniosek: **pierwsza minuta decyduje, a nasze filmy oddawały ją na wstęp**.

**Mapa tempa każdego filmu** (sekundy orientacyjne):

| Odcinek | Co się dzieje |
|---|---|
| 0:00–0:06 | Zapowiedź: ok. 10 skrótów najmocniejszych akcji, lektor od 1 s jednym zdaniem o stawce (Wytyczne 1.26). |
| 0:06–0:10 | Kurtyna startu z jednym krótkim zdaniem-pytaniem. |
| 0:10–0:50 | **Otwarcie w akcji**: najmocniejsza prawdziwa scena historii jako akcja — konflikt na scenie, zwrot, cliffhanger (Imam: oblężenie wieży, skok nad bagnetami, ucieczka z raną). Bohater działa, zanim usłyszymy, kim jest. Żadnych map, portretów ani streszczeń. |
| 0:50–1:40 | Po co ten film: obietnica (temat, most do tego, co widz zna), kim jest bohater (krótko, w ruchu, nawiązując do otwarcia), hak emocjonalny, jedno pytanie prowadzące dalej. |
| 1:40–3:00 | Dalej szybko: akcja albo zwrot co 15–25 s, co najmniej **3 sceny akcji w pierwszych 3 minutach**; tło (dzieciństwo, polityka, geografia) tylko jako zdanie w ujęciu, w którym coś się dzieje. |
| po ok. 2:30–3:00 | Wolno lekko zwolnić (emocja, oddech, gag), potem budować do kulminacji; co 45–60 s nowe pytanie albo zwrot; kurtyny aktów od aktu II. |

„Akcja” to konflikt na scenie: walka, pościg, ucieczka, zagrożenie, zasadzka, wybuch, gag z ruchem — nie przedstawienie
postaci, mapa ani wyjaśnienie. Rozpiska oznacza ujęcia akcji w `dane.AKCJA`, a `scripts/kontrola_filmu.py` sprawdza:
pierwsza akcja nie później niż 0:30, co najmniej 3 ujęcia akcji przed 3:00, w pierwszych 3 minutach nie więcej niż 75 s bez
akcji. Szczegóły rytmu ujęć: Rytm (kwestia + 2–4 wydarzenia, długość z treści).

## 4. Scenografia: trzy podejścia do każdej scenerii

- Co najmniej 4 różne dekoracje w każdych 2 minutach (Wytyczne 1.33, `kontrola_scenografii.py` filmu).
- **Każdy rodzaj scenerii ma w filmie trzy podejścia** (reżyser 28.11: „jak jest jedna dana sceneria, dajmy góry, albo rzeka,
  albo woda, albo las, to robimy trzy różne podejścia do tego, żeby widz się nie nudził”): inne ułożenie (góry: pasma
  w poprzek, dolina w głąb, jeden wielki szczyt), inna pora i światło (rzeka: zmierzch, dzień, noc), inna kompozycja (plan
  ogólny, zbliżenie miejsca, wnętrze). Każdy powrót tej scenerii w innym rozdziale bierze inne podejście.
- Upływ czasu na niebie: słońce i księżyc na nitkach jadą po kolei w jedną stronę, scena ciemnieje i jaśnieje
  (`scena.cykl_dni`) — nigdy dwa ciała naraz i nigdy pod spodem słońce dekoracji (Wytyczne 1.6).
- Każdy film rysuje swoje dekoracje, meble, podłogi i kulisy; z poprzedniego filmu bierze się tylko silnik (Wytyczne 1.33).
  Plan miejsc powstaje w szkicu, zanim cokolwiek zostanie narysowane.

## 5. Rozpiska, księga świata, rysunek

Kolejność z Podręcznika → Jak pracujemy (kroki 4–6) i Sekwencja, świat i ciągłość: spójność scenariusza i kwestie bez zdań
z innych filmów (`scripts/powtorzenia_kwestii.py`), rozpiska `dane.py` (jedyne źródło), księga `ksiega.py`, kontrola
ciągłości bez błędów wagi 3 i 2, potem rysunek po aktach na najnowszym silniku (`uklad.py`) z arkuszem klatek po każdym akcie.

## 6. Lektor i dźwięk

Lektor: klon głosu autora, przepis teatru papierowego, jedno podejście na kwestię, wymowa nazw, Whisper i kontrola ucięć
(Podręcznik → Lektor). Dźwięk: tematy w brzmieniu kraju i epoki, efekty z podsłuchu ujęć, cisza przed szczytami; nowy rodzaj
dźwięku idzie najpierw jako próbka do reżysera, a jego zgodę zapisuje się w Studio (etap „Gotowość filmu”).

## 7. Kontrole i Studio

Lista „Przed oddaniem reżyserowi” (Jak pracujemy) i `python3 -I scripts/kontrola_filmu.py <film> --studio --podglad` — zero
błędów; potem układ sceny we wszystkich klatkach i koniec świata. W Studio etap **Gotowość filmu** pokazuje, czego jeszcze
brakuje (lektor, zgoda na próbkę, muzyka, efekty, recenzje aktów, ciągłość). „Jest w Studio” mówi się dopiero po sprawdzeniu
Studio, nie po wyniku skryptu.

## 8. Tury poprawek, render, publikacja, wyniki

- Każda tura markerów: lista z `scripts/uwagi_rezysera.py`, poprawki, raport tury, lekcje w Wytycznych (tabela „Skąd te
  zasady”) i — jeśli się da — nowa kontrola w `kontrola_filmu.py`. Uwaga reżysera, która raz padła, obowiązuje we wszystkich
  następnych filmach.
- Render końcowy robi reżyser. Publikacja i Shortsy: Podręcznik → Publikacja.
- Wyniki po 7 i 28 dniach, po źródłach ruchu: utrzymanie w 15 s, 30 s, 60 s, 3 min — wnioski dopisuje się tutaj (rozdział 3)
  i do Rytmu, żeby następny film zaczynał od nich.
