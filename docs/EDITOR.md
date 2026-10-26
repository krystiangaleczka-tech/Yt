# Edytor w przeglądarce

```bash
pilot/.venv/bin/python -I docos/editor.py projekty/bloop_v3/bloop_v4.json --port 8766
# → http://localhost:8766
```

## Układ
- **Lewa kolumna** — beaty: kolor dynamiki, start, długość (z prawdziwego lektora), scena.
- **Środek** — wybrany beat: dynamika, chaos, akcja, **narracja** (+ „Nagraj głos beatu” — tylko zmienione zdania),
  **karty ujęć**: miniatura renderowana z prawdziwego silnika, typ, przejście, styl, czas, kadr, opis;
  ↑ ↓ (kolejność), ⧉ (duplikuj), ✕ (usuń), „+ Dodaj ujęcie”.
- **Prawa kolumna** — odtwarzacz podglądu (skacze do początku wybranego beatu), log renderu,
  **biblioteka mediów** z wyszukiwarką, typem, licencją i licznikiem użyć.
  Klik = ustaw `FILE:` w zaznaczonym ujęciu · Shift+klik = dodaj do `FILES:` (porównania, stos).
- **Pasek uwag** — wynik `docos.py check` na bieżąco; klik przenosi do beatu.

## Skróty
`Cmd/Ctrl+S` — zapis. Zapis robi kopię `*.bak.json`.

## Przyciski
- **Podgląd (szybki)** — 640×360, 12 kl/s; renderuje tylko zmienione beaty (~30 s po zmianie, ~2 min od zera).
- **Render finalny** — 1080p, 25 kl/s (~15–20 min).

## API (dla automatyzacji)
`GET /api/state` · `POST /api/save {project}` · `POST /api/render {quality}` · `POST /api/voice {beat}` ·
`GET /api/job` · `GET /thumb?beat=B03&n=2` · `GET /mthumb/<plik>` · `GET /out/<plik>.mp4` (z obsługą Range)
