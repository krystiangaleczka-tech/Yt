# Płynne odtwarzanie lektora w Montażu

Problem: roboczy podgląd synchronizował audio z zegarem animacji. Przy różnicy większej niż 150 ms ponownie ustawiał `currentTime`; przy każdym rysowaniu przypisywał również tempo i głośność. Opóźnione uruchomienie/buforowanie mogło powodować kolejne przewinięcia, a obietnice `play()` nie były koordynowane.

Zmiana:

- Podczas odtwarzania obraz korzysta z zegara aktywnego nagrania, z pierwszeństwem lektora; podczas buforowania czeka na audio.
- Nagranie przewija się przy rozpoczęciu/wznowieniu, ręcznym przewinięciu albo zmianie źródła/tempa. Nie jest przewijane w celu doganiania kolejnych klatek obrazu.
- Tempo i głośność są przypisywane po zmianie wartości. Jedno oczekujące `play()` jest współdzielone; późna odpowiedź i szybkie Pause/Play nie wznawiają zatrzymanego dźwięku ani nie zgłaszają starego błędu jako bieżącego.
- Błędy odtwarzania są widoczne. Podwójne kliknięcie ścieżki zatrzymuje transport przed zmianą pozycji.

Build TypeScript/Vite i **14 testów frontendu** przechodzą. Siedem nowych regresji obejmuje opóźniony zegar, brak kolejnych seeków, pause/scrub/resume, oczekujące i odrzucone play, szybkie ponowienie, buforowanie, source_in/speed oraz mute/solo.

Backend i renderer publikacyjny nie były zmieniane. W referencji WAV i audio istniejącego MP4 porównano lokalnie: po wyrównaniu przesunięcia 2,625 ms korelacja próbek wynosi 0,948 (AAC jest stratny). To kontrola sygnału, nie niezależna ocena odsłuchowa.
