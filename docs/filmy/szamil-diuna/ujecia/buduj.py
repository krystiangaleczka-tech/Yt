"""ROZPISKA.md z dane.py: czytelny scenariusz filmu dla reżysera (akt, scena, ujęcie, czas, kwestia, co się dzieje).

  python3 -I docs/filmy/szamil-diuna/ujecia/buduj.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dane import AKTY, kontrola_rytmu, kwestia, ujecia  # noqa: E402

KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta"}


def mmss(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


def main():
    rows = ujecia()
    by = {r[2]: r for r in rows}
    total = sum(r[5] for r in rows)
    out = ["# The Imam Who Fought Russia for 25 Years — and Ended Up in Dune · rozpiska (szkic E, 28.11.2026)", "",
           f"{len(rows)} ujęć, **{mmss(total)}**, kwestia lektora w {sum(1 for r in rows if kwestia(r[7]))} ujęciach. "
           f"Kontrola rytmu: {len(kontrola_rytmu(rows))} uwag. Źródło: `ujecia/dane.py`.", ""]
    t = 0.0
    for n, tytul, opis, sceny in AKTY:
        a = [r for r in rows if r[0] == n]
        out += [f"## Akt {n} · {tytul} ({sum(r[5] for r in a):.0f} s)", "", opis, ""]
        for sc, plan, beaty in sceny:
            out += [f"### {sc}", f"*{plan}*", ""]
            for _, shots in beaty:
                for x in shots:
                    r = by[x[0]]
                    kw = kwestia(r[7])
                    out.append(f"**{r[1]}. `{r[2]}`** · {mmss(t)} · {r[5]} s · {KADR[r[3]]}")
                    if kw:
                        out.append(f"> {kw}")
                    out += [r[6] + ("" if kw else f" — *dźwięk: {r[7]}*"), ""]
                    t += r[5]
    (HERE.parent / "ROZPISKA.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("zapisano ROZPISKA.md")


if __name__ == "__main__":
    main()
