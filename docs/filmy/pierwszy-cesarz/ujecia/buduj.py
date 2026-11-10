"""Składa czytelną rozpiskę filmu z dane.py: akt → scena → beat → ujęcie z kodami czasowymi.

uruchom:  python3 docs/filmy/pierwszy-cesarz/ujecia/buduj.py   (wynik: ../ROZPISKA.md)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dane import AKTY, ujecia  # noqa: E402

KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta / napis"}
RUCH = {"stat": "statyczna", "naj": "najazd", "odj": "odjazd", "pan": "panorama", "jaz": "jazda za postacią", "szarp": "szarpnięcie kamery"}


def tc(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


flat = iter(ujecia())
total = sum(u[5] for u in ujecia())
out = ["# Pierwszy cesarz — rozpiska (teatr papierowy)", "",
       f"**Długość:** {tc(total)} · **akty:** {len(AKTY)} · **ujęć:** {len(ujecia())}", "",
       "Kody czasowe od początku filmu. „L:” = kwestia lektora (3. osoba, czas przeszły); pozostały opis dźwięku to efekty.",
       "W nawiasie: (kadr · ruch kamery · klucz funkcji ujęcia w `output/pierwszy-cesarz`).", ""]
t = 0.0
for n, tytul, opis, sceny in AKTY:
    a0, body = t, []
    for si, (stitle, place, beaty) in enumerate(sceny, 1):
        s0, sbody = t, []
        for bi, (btitle, shots) in enumerate(beaty, 1):
            b0, bbody = t, []
            for _ in shots:
                _, nr, klucz, kadr, ruch, sec, desc, snd = next(flat)
                bbody.append(f"  - `{tc(t)}–{tc(t + sec)}` d{n:02d}_{nr:02d} ({KADR[kadr]} · {RUCH[ruch]} · `{klucz}`) {desc}"
                             + (f" — *{snd}*" if snd else ""))
                t += sec
            sbody += [f"- **Beat {n}.{si}.{bi} · {btitle}** `{tc(b0)}–{tc(t)}`"] + bbody
        body += [f"### Scena {n}.{si} · {stitle} `{tc(s0)}–{tc(t)}` · {place}"] + sbody + [""]
    out += [f"## Akt {n} · {tytul} `{tc(a0)}–{tc(t)}` ({t - a0:.1f} s)", "", opis, ""] + body
(HERE.parent / "ROZPISKA.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"ROZPISKA.md: {tc(t)}, {len(ujecia())} ujęć")
