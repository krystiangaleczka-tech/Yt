"""Kontrola całego filmu przed oddaniem reżyserowi — jedno polecenie zamiast pamiętania listy (reżyser 28.11.2026: „musisz
zapisać gdzieś to, co zrobiliśmy, aby zawsze tworzenie filmu było w ten sposób, z przestrzeganiem wytycznych”).

  python3 -I scripts/kontrola_filmu.py <film> [--studio] [--podglad]

Sprawdza (Podręcznik → Jak pracujemy, „Nowy film krok po kroku”; Wytyczne 1.9, 1.26, 1.32, 1.33):
  1. rytm rozpiski (dane.kontrola_rytmu: samotne krótkie ujęcia, trzy równe długości, kwestia bez wydarzeń) i tempo początku
     (dane.AKCJA: pierwsza akcja najpóźniej 0:30, co najmniej 3 ujęcia akcji przed 3:00, najwyżej 75 s bez akcji),
  2. lektor: każda kwestia ma nagranie z tym samym tekstem (dane.nagranie),
  3. kwestie bez zdań z innych filmów (scripts/powtorzenia_kwestii.py — do przejrzenia, nie zawsze błąd),
  4. scenografia: co najmniej 4 dekoracje w każdych 2 minutach (output/<film>/kontrola_scenografii.py),
  5. wycinki innego filmu: tapeta, okno, deski, drzwi i meble zestawu „Bonnie and Clyde” w dekoracjach ujęć,
  z --studio (Studio musi działać, port 8876):
  6. oś: liczba ujęć, długość osi = rozpiska, klatka v1 przy każdym ujęciu, lektor (a1) przy każdej kwestii, muzyka (a2)
     i efekty (a3) tak długie jak oś,
  7. kontrola ciągłości: zero błędów wagi 3 i 2,
  8. podgląd na żywo: działa bez błędu; z --podglad każde ujęcie zwraca obraz (Studio nie pokaże ujęcia, które się wywraca
     — 28.11 sześć ujęć z nowymi meblami zwracało błąd, a plan i skrypty mówiły „wgrane”).
Na końcu wypisuje kontrole, których ten skrypt nie robi sam (wszystkie klatki układu, koniec świata, arkusze, odsłuch).
Kod wyjścia 1, gdy coś jest błędem (powtórzenia kwestii tylko ostrzegają).
"""
import ast
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "http://127.0.0.1:8876/api"
# Arkusze zestawu „Bonnie and Clyde” (zestaw_bc.py), z którego wyszły zestawy następnych filmów: w dekoracji nowego filmu
# są błędem (Wytyczne 1.33 — reżyser 28.11: „wziąłeś biuro z Bonnie i Clyde, ma być zupełnie inne”).
OBCE_ARKUSZE = {"sciana", "okno", "podloga", "drzwi", "fasada", "chodnik", "latarnia", "tablica", "gazeta"}
OBCE_MEBLE = {"stol", "stol_obrus", "krzeslo", "kuchenka", "biurko", "lada", "lozko", "szafka", "kanapa", "fotel_bujany"}
OBCE_DEKORACJE = {"wnetrze", "teatr_gazet", "preria", "miasto", "eastham", "west_dallas", "drukarnia", "kino", "cmentarz", "mapa_scena"}

bledy, ostrzezenia = [], []


def wynik(ok, nazwa, opis, ostrzezenie=False):
    znak = "OK " if ok else ("UWAGA" if ostrzezenie else "BŁĄD")
    print(f"[{znak}] {nazwa}: {opis}")
    if not ok:
        (ostrzezenia if ostrzezenie else bledy).append(nazwa)


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method="POST" if body is not None else "GET",
                                 headers={"Content-Type": "application/json", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def dekoracje_i_obce(out):
    """Funkcje scen osiągalne z ujęć (graf wywołań scena.py) i wywołania obcych arkuszy, mebli i dekoracji w nich."""
    scena_src = (out / "scena.py").read_text(encoding="utf-8")
    scena = {n.name: n for n in ast.parse(scena_src).body if isinstance(n, ast.FunctionDef)}

    def wywolania(fn):
        for c in ast.walk(fn):
            if isinstance(c, ast.Call):
                f = c.func
                nazwa = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                przez_J = isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "J"
                yield nazwa, przez_J, c

    ujecia = []
    for plik in sorted(out.glob("ujecia_*.py")):
        ujecia += [n for n in ast.parse(plik.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)]
    lokalne = {n.name: n for n in ujecia}
    obce = []
    for uj in [n for n in ujecia if n.name.startswith("s_")]:
        do_przejscia, widziane = [uj], set()
        while do_przejscia:
            fn = do_przejscia.pop()
            if fn.name in widziane:
                continue
            widziane.add(fn.name)
            for nazwa, przez_J, c in wywolania(fn):
                if przez_J and nazwa in OBCE_ARKUSZE:
                    obce.append(f"{uj.name[2:]}: J.{nazwa}() w {fn.name}")
                if nazwa in OBCE_DEKORACJE:
                    obce.append(f"{uj.name[2:]}: dekoracja {nazwa}()")
                if nazwa == "mebel" and len(c.args) >= 2 and isinstance(c.args[1], ast.Constant) and c.args[1].value in OBCE_MEBLE:
                    obce.append(f"{uj.name[2:]}: mebel „{c.args[1].value}” w {fn.name}")
                if przez_J and nazwa == "mebel" and c.args and isinstance(c.args[0], ast.Constant) and c.args[0].value in OBCE_MEBLE:
                    obce.append(f"{uj.name[2:]}: J.mebel(„{c.args[0].value}”) w {fn.name}")
                if nazwa in scena and nazwa not in widziane:
                    do_przejscia.append(scena[nazwa])
                elif nazwa in lokalne and nazwa not in widziane and not nazwa.startswith("s_"):
                    do_przejscia.append(lokalne[nazwa])
    return sorted(set(obce))


def main():
    film = sys.argv[1]
    studio = "--studio" in sys.argv
    podglad = "--podglad" in sys.argv
    docs, out = ROOT / "docs/filmy" / film / "ujecia", ROOT / "output" / film
    sys.path.insert(0, str(docs))
    sys.path.insert(0, str(out))
    import dane
    rows = dane.ujecia()
    kw = [r for r in rows if dane.kwestia(r[7])]
    total = sum(r[5] for r in rows)
    print(f"film {film}: {len(rows)} ujęć, {int(total // 60)}:{total % 60:04.1f}, kwestii {len(kw)}\n")

    # 1. rytm
    if hasattr(dane, "kontrola_rytmu"):
        uw = dane.kontrola_rytmu(rows)
        wynik(not uw, "rytm", "bez uwag" if not uw else "; ".join(uw[:5]))
    # 1b. tempo początku (Podręcznik → Metoda filmu, 3: początek w akcji)
    if hasattr(dane, "AKCJA"):
        t, starty = 0.0, []
        for r in rows:
            if r[2] in dane.AKCJA:
                starty.append((t, r[2]))
            t += r[5]
        przed3 = [x for x in starty if x[0] < 180]
        luki = [b[0] - a[0] for a, b in zip([(0.0, "")] + przed3, przed3 + [(180.0, "")])]
        ok = bool(starty) and starty[0][0] <= 30 and len(przed3) >= 3 and max(luki) <= 75
        wynik(ok, "tempo początku", (f"pierwsza akcja {starty[0][1]} w {starty[0][0]:.0f} s, przed 3:00 {len(przed3)} ujęć akcji, "
                                     f"najdłużej bez akcji {max(luki):.0f} s") if starty else "brak ujęć akcji w dane.AKCJA")
    else:
        wynik(False, "tempo początku", "rozpiska nie ma dane.AKCJA (ujęcia akcji) — Podręcznik → Metoda filmu, 3", ostrzezenie=True)
    # 2. nagrania lektora
    if hasattr(dane, "nagranie"):
        brak = [r[2] for r in kw if dane.nagranie(r[7]) is None]
        wynik(not brak, "lektor", f"{len(kw)} kwestii nagranych" if not brak else f"bez nagrania: {', '.join(brak)}")
    # 3. powtórzenia z innych filmów
    p = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/powtorzenia_kwestii.py"), film], capture_output=True, text=True)
    ile = re.search(r"(\d+) par kwestii", p.stdout)
    pary = int(ile.group(1)) if ile else -1
    wynik(pary == 0, "powtórzenia", "żadna kwestia nie powtarza zwrotów innych filmów" if pary == 0 else
          f"{pary} par ze wspólnymi zwrotami — przejrzyj: python3 -I scripts/powtorzenia_kwestii.py {film}", ostrzezenie=True)
    # 4. scenografia
    ks = out / "kontrola_scenografii.py"
    if ks.exists():
        p = subprocess.run([sys.executable, "-I", str(ks)], capture_output=True, text=True, cwd=out)
        linia = [x for x in p.stdout.splitlines() if x.startswith("różnych dekoracji")]
        wynik(p.returncode == 0, "scenografia", linia[0] if linia else p.stdout[-300:])
    else:
        wynik(False, "scenografia", f"brak {ks.relative_to(ROOT)} (wzór: output/szamil-diuna/kontrola_scenografii.py)", ostrzezenie=True)
    # 5. obce wycinki
    obce = dekoracje_i_obce(out)
    wynik(not obce, "wycinki innego filmu", "dekoracje i meble tylko z zestawu filmu" if not obce else "; ".join(obce[:8]) +
          (f" … (+{len(obce) - 8})" if len(obce) > 8 else ""))

    if studio:
        stan = next((json.loads((out / n).read_text()) for n in ("studio.json", "studio_en.json") if (out / n).exists()), None)
        pid = stan["pid"]
        p = call(f"/projects/{pid}")
        fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
        koniec = max(s["start"] + s["duration"] for s in p["scenes"]) / fps
        clips = p["sequence"]["clips"]
        n = {tr: sum(c["track_id"] == tr for c in clips) for tr in ("v1", "a1", "a2", "a3")}
        dl = {tr: max([c["duration"] / fps for c in clips if c["track_id"] == tr] or [0]) for tr in ("a2", "a3")}
        wynik(len(p["scenes"]) == len(rows) and abs(koniec - total) < 0.25, "Studio: ujęcia",
              f"{len(p['scenes'])} ujęć, oś {koniec:.1f} s (rozpiska {total:.1f} s)")
        wynik(n["v1"] >= len(rows), "Studio: klatki v1", f"{n['v1']} klipów na {len(rows)} ujęć")
        wynik(n["a1"] == len(kw), "Studio: lektor", f"{n['a1']} klipów na {len(kw)} kwestii")
        for tr, nazwa in (("a2", "muzyka"), ("a3", "efekty")):
            wynik(n[tr] >= 1 and abs(dl[tr] - koniec) < 0.5, f"Studio: {nazwa}",
                  f"{dl[tr]:.1f} s przy osi {koniec:.1f} s" if n[tr] else "brak klipu (dźwięk po zatwierdzeniu próbki)", ostrzezenie=not n[tr])
        rep = call(f"/projects/{pid}/continuity/check", {})
        tot = rep["totals"]
        wynik(not tot.get("3") and not tot.get("2"), "Studio: ciągłość", f"waga 3/2/1: {tot.get('3', 0)}/{tot.get('2', 0)}/{tot.get('1', 0)}")
        try:
            st = call(f"/projects/{pid}/teatr/stan")
            wynik(st.get("dostepny") and not st.get("blad"), "podgląd na żywo", f"wersja {st.get('wersja')}, policzonych {st.get('gotowe')}/{st.get('ujec')}"
                  + (f", błąd: {st['blad'][-200:]}" if st.get("blad") else ""))
            if podglad:
                zle = []
                for s in sorted(p["scenes"], key=lambda s: s["start"]):
                    odn = s["legacy"].get("teatr", {}).get("odn")
                    if not odn:
                        continue
                    try:
                        urllib.request.urlopen(urllib.request.Request(f"{API}/projects/{pid}/teatr/ujecie/{odn}",
                                                                      headers={"X-Docos-Request": "1"}), timeout=300).read()
                    except Exception as e:
                        zle.append(f"{odn} {s['legacy'].get('klucz')} ({e})")
                wynik(not zle, "podgląd: każde ujęcie", "wszystkie ujęcia się rysują" if not zle else "; ".join(zle[:6]))
        except Exception as e:
            wynik(False, "podgląd na żywo", f"niedostępny ({e})", ostrzezenie=True)

    print("\nKontrole poza tym skryptem (Wytyczne 3; Podręcznik → Jak pracujemy):")
    print(f"  - układ sceny we WSZYSTKICH klatkach: python3 -I output/{film}/kontrola_ukladu.py (3 procesy: --czesc i/3)")
    print(f"  - koniec świata: cd output/{film} && PROCESY=3 python3 -I render.py kontrola")
    print("  - arkusze klatek zmienionych ujęć obejrzane (obsada, rekwizyty, pary cięć n−1 → n → n+1)")
    print(f"  - lektor: docos/uciecia_lektora.py output/{film}/lektor_en + odsłuch Whisperem; nowy rodzaj dźwięku → próbka do reżysera")
    print(f"\nbłędów: {len(bledy)}{' (' + ', '.join(bledy) + ')' if bledy else ''}; ostrzeżeń: {len(ostrzezenia)}")
    sys.exit(1 if bledy else 0)


if __name__ == "__main__":
    main()
