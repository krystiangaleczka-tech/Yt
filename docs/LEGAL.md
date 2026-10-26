# Kwestie prawne i uczciwość

## Materiały
- **Domena publiczna**: utwory rządu USA — NOAA (nagrania, spektrogramy, zdjęcia), NASA, US Navy, CIA.
- **Wikimedia Commons**: tylko PD, CC0, CC BY, CC BY-SA (`fetch_commons.py` odrzuca inne). CC BY / BY-SA wymagają
  podania autora i licencji — robi to plansza końcowa i opis filmu (z rejestrów `licenses.json`).
- **Prasa**: artykuły są chronione prawem autorskim — nie publikujemy skanów ani pełnych tekstów.
  Plansze PRASA/QA/CYTAT pokazują **krótkie, dosłowne cytaty** z podaniem źródła i daty, we własnym layoucie
  (komentarz/omówienie), nie podróbkę strony gazety.
- **Materiały ilustracyjne** (inne miejsce/czas niż opisywane) mają podpis „illustrative”.

## Fakty
Każda liczba, data, nazwisko i cytat w narracji musi być w rejestrze `facts` ze źródłem.
DISPUTED — tylko z zastrzeżeniem; UNVERIFIED — nie stwierdzamy; DRAMATIZATION — rekonstrukcja oznaczona na ekranie.
Nie generujemy fałszywych wywiadów ani twarzy prawdziwych osób.

## AI
- kadry AI zawsze z podpisem „AI reconstruction” (v5 ich nie używa),
- lektor to klon głosu autora — informacja w napisach końcowych i opisie,
- YouTube wymaga oznaczenia realistycznych treści syntetycznych (ustawienie „Altered or synthetic content”).

## Głos
Klonuj tylko własny głos albo za wyraźną zgodą osoby. Próbki głosu nie publikuj.
Watermark Perth (Chatterbox) zostaje w nagraniach.

## Licencje narzędzi
SD 1.5 — CreativeML OpenRAIL-M · Kokoro-82M — Apache 2.0 · Chatterbox — MIT ·
Courier Prime, Montserrat — SIL OFL 1.1 (`pilot/fonts/OFL-*.txt`).
Kod w tym repo nie ma jeszcze wybranej licencji (domyślnie: wszelkie prawa zastrzeżone).
