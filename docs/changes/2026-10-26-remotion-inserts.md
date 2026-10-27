# Wstawki Remotion w DocOS Studio

Data: 26 października 2026.

## Zmiana

Do istniejącego studia dodano osobny dział **Wstawki animowane**, dostępny również
z generowania ujęć i montażu. Pięć oryginalnych szablonów obejmuje animowane zdjęcie,
porównanie zdjęć, wykres słupkowy, cytat oraz planszę rozdziału. Podgląd Remotion Player
i renderer Node korzystają z tego samego komponentu i deterministycznego czasu klatkowego.

Formularz udostępnia tekst, źródło, własne dane, zdjęcia z biblioteki, czas, kolory i modulację
zdjęć: zoom, przesunięcie, obrót, jasność, nasycenie, rozmycie. Definicje są zapisywane w projekcie,
objęte historią undo/redo i przenoszone przez istniejący pakiet ZIP. Sam JSON nie przenosi
uprawnień dostępu do plików — odnośniki multimedialne są czyszczone podczas importu.

AI proponuje wyłącznie zwalidowane parametry szablonu, przez połączony model albo ręczny import JSON.
Przed zapisaniem użytkownik ogląda propozycję. Brak uruchamiania dowolnego kodu z modelu.

Render działa jako anulowalne zadanie w istniejącej kolejce. MP4 zostaje zweryfikowany przez ffprobe
i zapisany jako niezmienny materiał z definicją oraz sygnaturą źródłową. Zmieniona w trakcie renderu
wstawka nie otrzymuje starego wyniku jako bieżącej wersji. Sygnatura uwzględnia także rozdzielczość,
FPS i źródłowe zdjęcia. Dodanie do osi czasu jest jawne i respektuje blokady ścieżek. Dotychczasowe
klipy nie są samodzielnie podmieniane. Eksport całego filmu nadal wykorzystuje FFmpeg.

Naprawiono też odświeżenie projektu po ukończeniu pierwszego zadania: porównanie strumienia SSE
zachowuje pusty zbiór ukończonych zadań bez wartości zastępczej powodującej nadmiarowe odświeżenia.

## Zależności i uruchomienie

`remotion`, `@remotion/player`, `@remotion/bundler`, `@remotion/renderer`: przypięte `4.0.539`.
Instalacja i konfiguracja: [STUDIO.md](../STUDIO.md#wstawki-remotion).
Dla renderowania potrzebny Chrome Headless Shell (`npm --prefix apps/studio run remotion:setup`),
albo własny zgodny plik przeglądarki przez `DOCOS_REMOTION_BROWSER`.
Moduł nie rejestruje konta, nie kupuje subskrypcji i nie wysyła renderów do chmury.

## Weryfikacja lokalna

- Build produkcyjny React/TypeScript: poprawny; edytor Remotion ładowany oddzielnie.
- Osobne zbudowanie kompozycji bundlerem Remotion: poprawne.
- 49 testów Studio: poprawne, w tym 13 nowych testów modułu wstawek.
- 18 dotychczasowych testów DocOS: poprawne.
- 5 testów frontendowej osi czasu: poprawne.
- Test rzeczywistego renderera jest opt-in; standardowy przebieg lokalny go pomija.
- `git diff --check`: poprawny.

Ograniczenia środowiska lokalnego: podgląd Sites kończy się na brakującym `uvicorn`
w izolowanym środowisku podglądu. Próba rzeczywistego renderu Remotion po poprawnym bundlowaniu
zatrzymała się w bibliotece na `uv_interface_addresses` (odczyt interfejsów sieciowych zablokowany
w środowisku wykonawczym). Nie obchodzono tych ograniczeń. Pełna weryfikacja interfejsu
w przeglądarce i lokalnego MP4 z Remotion pozostaje niewykonana.

Lista zadań pozwala też otwierać i pobierać MP4 wstawki; błąd ostatniego renderu jest widoczny
w edytorze. Usunięta definicja nie pozostawia aktywnego przycisku edycji źródła na klipie.

Workflow CI wykorzystuje istniejące FFmpeg/ffprobe na runnerze i instaluje je tylko w razie braku.
Został rozszerzony o przygotowanie renderera i prawdziwy test pięciu szablonów:
render Remotion → rejestracja materiału → oś czasu → eksport FFmpeg. Wynik CI należy sprawdzić
na opublikowanym commicie; sam opis testu nie stanowi potwierdzenia jego powodzenia.

## Zakres pierwszej wersji

Wstawki do sześćdziesięciu sekund, pełne tło, H.264 bez alpha i bez własnego audio.
Wykresy: od jednego do ośmiu nieujemnych słupków. Brak riggingu, ożywiania twarzy, generowania
nowych kadrów, wieloetapowej infografiki i animowanej mapy. Prawdziwość danych i cytatów oraz
prawa do źródeł pozostają przedmiotem weryfikacji redakcyjnej. Font systemowy może różnić się
pomiędzy komputerami.
