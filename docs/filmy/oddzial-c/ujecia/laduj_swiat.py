"""Księga świata i warsztat Oddziału C: repozytorium ⇄ Studio.

  python3 docs/filmy/oddzial-c/ujecia/laduj_swiat.py wczytaj <projekt> [port]  — swiat.json + warsztat.json → Studio
  python3 docs/filmy/oddzial-c/ujecia/laduj_swiat.py eksport <projekt> [port]  — Studio → swiat.json + warsztat.json

Miejscem pracy jest Studio (Continuity Editor → Świat / Warsztat); pliki w repozytorium to kopia do historii gita.
"""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
MODE, PID = sys.argv[1], sys.argv[2]
API = f"http://127.0.0.1:{sys.argv[3] if len(sys.argv) > 3 else 8876}/api"
H = {"Content-Type": "application/json", "X-Docos-Request": "1"}


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"), headers=H,
                                 data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)


if MODE == "wczytaj":
    world = json.loads((FILM / "swiat.json").read_text(encoding="utf-8"))
    book = json.loads((FILM / "warsztat.json").read_text(encoding="utf-8"))
    p = call(f"/projects/{PID}")
    p = call(f"/projects/{PID}/flow/world", {"expected_revision": p["revision"], "world": world}, "PUT")
    p = call(f"/projects/{PID}/flow/book", {"expected_revision": p["revision"], "book": book}, "PUT")
    r = call(f"/projects/{PID}/continuity/check", {})
    t = r["totals"]
    call(f"/projects/{PID}/flow/log", {"entry": {"who": "laduj_swiat.py", "kind": "praca", "summary": "Wczytano księgę świata i warsztat z repozytorium",
                                                 "details": f"Kontrola całego filmu: {t['3']} / {t['2']} / {t['1']} (waga 3 / 2 / 1).",
                                                 "files": ["docs/filmy/oddzial-c/swiat.json", "docs/filmy/oddzial-c/warsztat.json"]}})
    print(f"wczytano | kontrola {t['3']}/{t['2']}/{t['1']}")
elif MODE == "eksport":
    flow = call(f"/projects/{PID}")["legacy"]["production_flow"]
    (FILM / "swiat.json").write_text(json.dumps(flow.get("world", {}), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FILM / "warsztat.json").write_text(json.dumps(flow.get("book", {}), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wyeksportowano swiat.json i warsztat.json")
else:
    sys.exit("tryb: wczytaj | eksport")
