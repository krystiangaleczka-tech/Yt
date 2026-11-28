"""Szkic E „Przebudowa” (28.11.2026) — cały film z rozpiski szkicu E do etapu Studio „Szkice ujęć”, z klatką na każde ujęcie.

  python3 -I docs/filmy/szamil-diuna/szkice/szkic_e.py           — zapisuje e/szkic.json i e/klatki/NNN.png
  python3 -I docs/filmy/szamil-diuna/szkice/szkic_e.py import    — to samo + import wariantu E do projektu Studio

Reżyser 28.11 po pierwszej minucie wersji D: „przebuduj to… przecież to ma być zajebiste”. Szkice A–D zostają zamrożone
(buduj_szkice.py); E powstaje z rozpiski (ujecia/dane.py), która od przebudowy jest źródłem. Zatwierdza reżyser w Studio.
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
OUT = Path(__file__).resolve().parents[4] / "output/szamil-diuna" if (Path(__file__).resolve().parents[4] / "output/szamil-diuna").exists() \
    else Path("/Users/krystiangaleczka/Documents/YT/output/szamil-diuna")
sys.path.insert(0, str(FILM / "ujecia"))
from dane import AKTY, kwestia, ujecia  # noqa: E402

KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta"}
ZNACZNIK = {"zap_skok": "ZAPOWIEDŹ", "tytul": "KURTYNA STARTU", "arrakis": "Diuna, którą widz zna", "zamiana": "ZWROT: słowa są z gór",
            "przedstawienie": "kim jest Szamil", "hak_syn": "HOOK 1", "pytanie": "PYTANIE → retrospekcja", "skok": "akcja (legenda)",
            "kanly_1834": "słowo z Diuny: kanly", "marsz": "HOOK 2 · kurtyna", "amanat": "cios", "raport": "gag: pieczątka 1",
            "kreski": "kurtyna", "dargo": "gag: koza 2", "zwyciestwo": "gag: pieczątka 2", "zasadzka": "powaga",
            "tolstoj": "kurtyna", "cena": "słowo z Diuny: padishah", "syn_wraca": "promyk nadziei", "uscisk": "SZCZYT EMOCJI",
            "smierc": "cios · kurtyna", "kapitulacja": "KULMINACJA · siridar", "stempel": "zwrot gagu: pieczątka 3",
            "kaluga": "gag: koza 3", "medyna": "kurtyna", "slowa1": "ROZWIĄZANIE: słowa", "zdanie": "dowód", "biala_flaga": "PUENTA"}
API = f"http://127.0.0.1:{os.environ.get('DOCOS_API_PORT', '8876')}/api"


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", "X-Docos-Request": "1"}, method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main():
    rows = ujecia()
    d = HERE / "e"
    (d / "klatki").mkdir(parents=True, exist_ok=True)
    kod = ("import sys; sys.argv=['x']; sys.path.insert(0, %r); import render as R\n"
           "for n in range(len(R.SCENES)):\n    a, b = R.SCENES[n][:2]\n    R.frame(a + (b - a) * 0.6).save(%r %% (n + 1))\n") % (
        str(OUT), str(d / "klatki" / "%03d.png"))
    subprocess.run([sys.executable, "-c", kod], env={**os.environ, "SZKIC": "1"}, check=True, cwd=str(OUT))
    out, t = [], 0.0
    for nr, (akt, _, klucz, kadr, ruch, sek, opis, dz) in enumerate(rows, 1):
        out.append({"nr": nr, "klucz": klucz, "sekundy": sek, "opis": opis, "kwestia": kwestia(dz), "kadr": KADR[kadr],
                    "klatka": f"klatki/{nr:03d}.png", **({"znacznik": ZNACZNIK[klucz]} if klucz in ZNACZNIK else {})})
        t += sek
    opis = ("Przebudowa całego filmu (reżyser 28.11: „przebuduj to”). Każde ujęcie ma kwestię lektora i 2–4 wydarzenia na jej "
            "słowach; otwarcie od Diuny, którą widz zna; Gimry 1832, Achulgo 1839, Dargo 1845 i Tołstoj, syn i księżne, Gunib "
            "i Kaługa, słowa. 22 gagi (docs/filmy/szamil-diuna/GAGI.md). Długość z historii: "
            f"{int(t // 60)}:{t % 60:04.1f}.\n\n" + "\n\n".join(f"Akt {n} · {tyt}: {o}" for n, tyt, o, _ in AKTY))
    scen = opis + "\n\n" + "\n\n".join(f"{x['opis']}\n\"{x['kwestia']}\"" if x["kwestia"] else x["opis"] for x in out)
    (d / "szkic.json").write_text(json.dumps({"film": "szamil-diuna", "wariant": "E", "tytul": "E · Przebudowa: słowa z gór na pustyni",
                                              "scenariusz": scen, "ujecia": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"szkic E: {len(out)} ujęć, {int(t // 60)}:{t % 60:04.1f}")
    if "import" in sys.argv[1:]:
        pid = json.loads((OUT / "studio.json").read_text())["pid"]
        p = call(f"/projects/{pid}")
        r = call(f"/projects/{pid}/sketches/import", {"path": str(d), "expected_revision": p["revision"], "who": "Claude"})
        print("import:", json.dumps(r, ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
