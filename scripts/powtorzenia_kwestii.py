"""Kwestie lektora filmu, które powtarzają zdania innych filmów kanału (reżyser 28.11.2026, „Imam / Diuna”: „słyszałem
zdanie »enemy as a hostage«, to już było w Pierwszym Cesarzu. Nie ma powielania scenariusza pomiędzy filmami.”).

  python3 -I scripts/powtorzenia_kwestii.py <film> [--n 3]

Porównuje kwestie z docs/filmy/<film>/ujecia/dane.py z nagranymi kwestiami innych filmów (output/*/lektor_en/*.json i
output/*/lektor/*.json) i wypisuje wspólne ciągi n słów (domyślnie 3), w których co najmniej dwa słowa nie są słowami
funkcyjnymi („the”, „of”…). Wynik czyta człowiek: zwroty ogólne („a year later”, „down the river”) mogą zostać, zdanie
o tej samej budowie i treści („handed … to the enemy as a hostage”, „It all starts in…”, „So how did…”) trzeba przepisać.
Kod wyjścia 1, gdy coś znalazł.
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = {"the", "a", "of", "and", "to", "in", "his", "was", "he", "it", "that", "on", "for", "with", "as", "at", "by", "from", "her",
        "is", "an", "this", "had", "were", "they", "their", "him", "she", "be", "or", "but", "so", "who", "not", "its"}


def slowa(t):
    return re.findall(r"[a-z']+", t.lower())


def ngramy(ws, n):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def main():
    film = sys.argv[1]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 3
    sys.path.insert(0, str(ROOT / "docs/filmy" / film / "ujecia"))
    from dane import kwestia, ujecia
    inne = []
    korzenie = {ROOT}
    try:  # w worktree nagrania innych filmów leżą w głównym katalogu repozytorium (nie idą do gita)
        import subprocess
        wspolny = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, text=True).strip()
        korzenie.add((ROOT / wspolny).resolve().parent)
    except Exception:
        pass
    pliki = sorted({str(Path(f).resolve()): f for r in korzenie for f in glob.glob(str(r / "output/*/lektor*/*.json"))}.values())
    for f in pliki:
        p = Path(f)
        if p.parts[-3] == film:
            continue
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(m, dict) and m.get("text"):
            inne.append((f"{p.parts[-3]}/{p.stem}", m["text"]))
    ile = 0
    for u in ujecia():
        t = kwestia(u[7])
        if not t:
            continue
        moje = {g for g in ngramy(slowa(t), n) if sum(w not in STOP for w in g) >= 2}
        for k, tx in inne:
            wsp = moje & ngramy(slowa(tx), n)
            if wsp:
                ile += 1
                print(f"{u[2]:16s} ~ {k}: {['  '.join(g) for g in sorted(wsp)]}\n    {t}\n    {tx}")
    print(f"\n{ile} par kwestii ze wspólnymi zwrotami ({len(inne)} kwestii innych filmów)")
    sys.exit(1 if ile else 0)


if __name__ == "__main__":
    main()
