"""Składa rozpiskę ujęć wariantu z danych (dzień → scena → beat → ujęcie) i liczy kody czasowe.

uruchom:  python3 docs/filmy/oddzial-c/ujecia/buduj.py a
dane:     a_dane1.py, a_dane2.py (lista DAYS), wynik: ../A_DO_SWITU_UJECIA.md
ujęcie:   (kadr, ruch, sekundy, opis, dźwięk); dźwięk zaczynający się od „L:” to kwestia lektora
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = {"a": "A_DO_SWITU_UJECIA.md"}
TITLE = {"a": "A. Do świtu — 30 nocy na Leśnej · sceny, beaty, ujęcia"}

KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "NR": "zza ramienia", "Z": "zbliżenie",
        "WZ": "wielkie zbliżenie", "D": "detal", "POV": "oczami bohatera", "TYT": "karta / napis"}
RUCH = {"stat": "statyczna", "naj": "najazd", "odj": "odjazd", "pan": "panorama", "jaz": "jazda za postacią",
        "ręka": "z ręki", "drg": "drgania", "szarp": "szarpnięcie kamery"}

def tc(t):
    m, s = divmod(round(t, 1), 60)
    return f"{int(m)}:{s:04.1f}" if s % 1 else f"{int(m)}:{int(s):02d}"


def main(key):
    days = []
    for part in (1, 2):
        days += importlib.import_module(f"{key}_dane{part}").DAYS


    lines = [f"# {TITLE[key]}", "",
             "Kody czasowe liczone od początku filmu (0:00), z długości ujęć. Zimne otwarcie (dzień 0) to gotowe ujęcia "
             "z `output/zombie-psychiatryk/` z prawdziwymi czasami renderu. W nawiasie: (kadr · ruch kamery).", "",
             "| Kadr | | Ruch | |", "|---|---|---|---|"]
    for (k, kv), (r, rv) in zip(KADR.items(), list(RUCH.items()) + [("", "")] * 9):
        lines.append(f"| {k} | {kv} | {r} | {rv} |")
    lines += ["", "„L:” = kwestia lektora (narrator, 1. osoba, czas przeszły). Pozostały opis dźwięku to efekty i ambient.", ""]

    t, total_shots, report = 0.0, 0, []
    for n, title, scenes in days:
        start = t
        body = []
        for si, (stitle, place, beats) in enumerate(scenes, 1):
            s0 = t
            sbody = []
            for bi, (btitle, shots) in enumerate(beats, 1):
                b0 = t
                bbody = []
                for kadr, ruch, sec, desc, sound in shots:
                    assert kadr in KADR and ruch in RUCH, (n, kadr, ruch)
                    snd = f" — *{sound}*" if sound else ""
                    bbody.append(f"  - `{tc(t)}–{tc(t + sec)}` ({kadr} · {ruch}) {desc}{snd}")
                    t += sec
                    total_shots += 1
                sbody.append(f"- **Beat {n}.{si}.{bi} · {btitle}** `{tc(b0)}–{tc(t)}`")
                sbody += bbody
            body.append(f"### Scena {n}.{si} · {stitle} `{tc(s0)}–{tc(t)}` · {place}")
            body += sbody + [""]
        head = "Zimne otwarcie" if n == 0 else f"Dzień {n}"
        lines += [f"## {head} · {title} `{tc(start)}–{tc(t)}` ({t - start:.1f} s)", ""] + body
        report.append((n, t - start))

    lines.insert(2, f"**Długość:** {tc(t)} · **dni:** {len(days) - 1} · **ujęć:** {total_shots}\n")
    (HERE.parent / OUT[key]).write_text("\n".join(lines) + "\n")
    print(f"{OUT[key]}: {tc(t)}, {total_shots} ujęć")
    for n, d in report:
        print(f"  dzień {n:2d}: {d:5.1f} s")


if __name__ == "__main__":
    main(sys.argv[1])
