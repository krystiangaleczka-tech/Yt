# Projekt: „The Bloop: The Scientist Who Said Ice, and the World That Heard a Monster”

| Plik | Co to jest |
|---|---|
| `bloop_v4.json` | **aktualny projekt (v5)** — fakty, beaty, narracja, shot listy, sekcja `render`; otwierany w edytorze |
| `bloop_v3.json` | wersja v3 (pierwszy montaż z prawdziwymi materiałami) |
| `beats/`, `beats_v4/` | odpowiedzi beatów w formacie DocOS (Narracja / Shot List / Fakty / Połączenie) dla v3 i v4 |
| `bloop_v3_description.txt` | opis filmu na YouTube ze źródłami i uznaniem autorstwa |
| `raw/*/licenses.json` | rejestry licencji materiałów (Commons); same pliki: `python3 ../../docos/fetch_media.py .` |

Lektor (`voice/`) nie jest w repo — nagraj go własną próbką głosu (`docs/VOICE.md`).

```bash
python3 ../../docos/fetch_media.py .
../../pilot/.venv/bin/python -I ../../docos/editor.py bloop_v4.json --port 8766
```
