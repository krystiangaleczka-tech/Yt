"""Różnorodność scenografii filmu (reżyser 28.11.2026: „za mało różnych ujęć… przez 2 minuty tylko dwie scenografie, bądź
jedna, a powinno ich być co najmniej 4… jeśli to mają być góry, to pokazujemy je w jeden sposób, potem w inny”).

  python3 -I kontrola_scenografii.py [--okno 120] [--min 4]

Z kodu ujęć (ujecia_a.py, ujecia_b.py) odczytuje, którą dekorację stawia każde ujęcie (funkcja sceny z wariantem: pora
dnia, pokój, światło), i liczy w każdym oknie 2 minut (co 10 s), ile różnych dekoracji widać; podaje też najdłuższy ciąg
tej samej dekoracji. Kod wyjścia 1, gdy jakieś okno ma mniej niż --min dekoracji.
"""
import ast
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/szamil-diuna/ujecia"))
from dane import ujecia  # noqa: E402

WARIANTY = ("pora", "noc", "mrok", "swiatlo")


def dekoracje_ujec():
    src = (HERE / "scena.py").read_text(encoding="utf-8")
    sety = set(re.findall(r"^def ([a-z_0-9]+)\(st, t, w", src, re.M)) | {"pracownia", "plaskowyz", "polana", "parawan"}
    sety -= {"slonce", "chmury", "koniec", "zawieszki", "rampa", "kulisy", "pas", "wzgorza", "klif", "ziemia", "niebo_pory", "gory_pasmo"}
    out = {}
    for f in ("ujecia_a.py", "ujecia_b.py"):
        for n in ast.parse((HERE / f).read_text(encoding="utf-8")).body:
            if not isinstance(n, ast.FunctionDef):
                continue
            calls = []
            for c in ast.walk(n):
                if isinstance(c, ast.Call):
                    nm = c.func.id if isinstance(c.func, ast.Name) else getattr(c.func, "attr", "")
                    if nm in sety:
                        war = {k.arg: ast.unparse(k.value) for k in c.keywords if k.arg in WARIANTY}
                        if nm == "izba_kz" and len(c.args) > 3:
                            war["pokój"] = ast.unparse(c.args[3])
                        calls.append(nm + (str(war) if war else ""))
            out[n.name] = list(dict.fromkeys(calls))
    return out


def main():
    okno = float(sys.argv[sys.argv.index("--okno") + 1]) if "--okno" in sys.argv else 120.0
    minimum = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 4
    fn = dekoracje_ujec()
    rows, t = [], 0.0
    for u in ujecia():
        k = u[2]
        s = fn.get("s_" + k, [])
        if s and s[0] == "pracownia":
            s = [f"pracownia_sc[{k}]"]
        rows.append((t, t + u[5], k, s[0] if s else ("(zapowiedź)" if k.startswith("zap_") else "?")))
        t += u[5]
    okna = []
    for start in range(0, int(t - okno) + 1, 10):
        w = {m for a, b, k, m in rows if b > start and a < start + okno and not k.startswith("zap_")}
        okna.append((len(w), start))
    best, prev, a0 = (0.0, ""), None, 0.0
    for a, b, k, m in rows:
        if m != prev:
            a0, prev = a, m
        if b - a0 > best[0]:
            best = (round(b - a0, 1), f"{m} od {int(a0 // 60)}:{a0 % 60:04.1f}")
    for a, b, k, m in rows:
        print(f"{int(a // 60)}:{a % 60:04.1f} {k:15s} {m}")
    zle = [f"{s // 60}:{s % 60:02d} ({n})" for n, s in okna if n < minimum]
    print(f"\nróżnych dekoracji w filmie: {len({m for *_, m in rows})}; w oknie {okno:.0f} s najmniej {min(okna)[0]}, średnio "
          f"{sum(n for n, _ in okna) / len(okna):.1f}; najdłużej jedna dekoracja: {best[0]} s ({best[1]})")
    print("okna poniżej minimum:", zle or "brak")
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
