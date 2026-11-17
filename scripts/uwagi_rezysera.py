"""Uwagi reżysera i markery na klatkach z projektu Studio — lista do pracy nad poprawkami
(docs/WYTYCZNE_UJEC.md, 4.2 „Uwagi i markery reżysera — jak je czytać”).

uruchom:  python3 scripts/uwagi_rezysera.py <projekt> [--od RRRR-MM-DD] [--fps 24] [--md plik.md]

<projekt> — id projektu (prj_…) albo ścieżka do project.json. Skrypt tylko czyta plik projektu
z .docos-studio/projects — niczego nie zmienia w Studio.

Dla każdego ujęcia z uwagą albo markerem wypisuje:
- numer ujęcia na osi, tytuł i czas na osi Studio,
- uwagę reżysera z pola ujęcia (bez opisu z rozpiski: wierszy „Kadr:”, „Typ:”, „Beat:”…) i kiedy ostatnio ją zmieniono,
- każdy marker: sekundę w ujęciu, klatkę osi (30 kl./s) i klatkę renderu (--fps), tekst i kreski w pikselach ekranu
  (początek → koniec, obrys) — kreska jest w kadrze ekranu na tej klatce, z ruchem kamery, nie w kadrze wzorcowym,
- podpowiedzi, o czym pamiętać przy wykonaniu (odwołanie do poprzedniej uwagi, dźwięk, długość, pytanie).
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO = re.compile(r"^(Kadr|Typ|Beat|Dźwięk|Cel|Przejście):")

# podpowiedzi: (słowa w tekście bez polskich znaków, przypomnienie z wytycznych)
PODPOWIEDZI = [
    (("to samo", "jak poprzednio", "jak w poprzednim", "z poprzedniego", "zas ", "znowu", "w nastepnych",
      "kolejne ujecia", "jesli sa kolejne"),
     "odwołanie do innej uwagi albo ujęcia — poprawka raz we wspólnym kodzie i we wszystkich ujęciach z tą rzeczą (1.6)"),
    (("dzwiek", "cough", "konani", "brzek", "plusk", "z dzwiekiem"),
     "dźwięk — zdarzenie w efekty.ZDARZENIA w tej samej sekundzie, głos z nagrania (1.12, 1.14)"),
    (("wydluz", "dluzej", "skroc", "krocej"),
     "długość — zmiana w rozpisce (WYDLUZ), w dodanym czasie coś się dzieje (1.8, 1.18)"),
    (("narracj", "lektor", "opisz"),
     "zmiana od góry — kwestia w rozpisce i tłumaczeniu, nagranie lektora za zgodą reżysera (4.2)"),
    (("tabliczk",), "znak ze słownika (1.20), napis w języku wersji (1.13)"),
    (("usun", "wyrzuc", "wyjeb"),
     "usunięcie — z tego ujęcia i z każdego, w którym rzecz nie gra; jeśli gra później, tam wchodzi skądś (1.2, 1.6)"),
    (("schowaj", "skryj"), "schowanie — za ramą, falą, rampą albo bliższym planem, nie zniknięcie (1.1, 1.5)"),
]


def bez_ogonkow(s):
    s = unicodedata.normalize("NFKD", s.lower().replace("ł", "l"))
    return "".join(c for c in s if not unicodedata.combining(c))


def podpowiedzi(tekst):
    t = bez_ogonkow(tekst) + " "
    out = [p for slowa, p in PODPOWIEDZI if any(s in t for s in slowa)]
    if "?" in tekst:
        out.append("pytanie = zgłoszenie błędu: popraw i w podsumowaniu odpowiedz, skąd się wziął (4.2)")
    return out


def plik_projektu(arg):
    p = Path(arg)
    if p.suffix == ".json":
        return p
    return ROOT / ".docos-studio" / "projects" / arg / "project.json"


def uwaga(scena):
    lines = [l.strip() for l in (scena.get("director_notes") or "").split("\n")]
    return "\n".join(l for l in lines if l and not AUTO.match(l))


def kiedy_zmieniona(path, sceny):
    """Najwcześniejsza wersja projektu z historii, w której uwaga ujęcia ma już dzisiejszy tekst."""
    teraz = {s["id"]: uwaga(s) for s in sceny}
    out = {}
    hist = path.parent / "history"
    wersje = []
    for f in sorted(hist.glob("*.json")) if hist.is_dir() else []:
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        wersje.append((j.get("updated_at") or "", j))
    for at, j in sorted(wersje, key=lambda x: x[0]):
        for s in j.get("scenes", []):
            sid = s.get("id")
            if sid in teraz and teraz[sid] and sid not in out and uwaga(s) == teraz[sid]:
                out[sid] = at
    return out


def czas(sek):
    m, s = divmod(sek, 60)
    return f"{int(m)}:{s:04.1f}"


def kreski(strokes, w, h):
    out = []
    for st in strokes or []:
        pts = [(p["x"] * w, p["y"] * h) for p in st.get("points", [])]
        if not pts:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        out.append(f"kreska ({x0:.0f}, {y0:.0f}) → ({x1:.0f}, {y1:.0f}), obrys x {min(xs):.0f}–{max(xs):.0f}, "
                   f"y {min(ys):.0f}–{max(ys):.0f}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("projekt")
    ap.add_argument("--od", default="", help="tylko markery i uwagi zmienione od tej daty (RRRR-MM-DD)")
    ap.add_argument("--fps", type=float, default=24.0, help="klatki na sekundę renderu filmu (teatr papierowy: 24)")
    ap.add_argument("--md", default="", help="zapisz listę do pliku Markdown zamiast wypisywać")
    a = ap.parse_args()

    path = plik_projektu(a.projekt)
    if not path.exists():
        sys.exit(f"Nie ma pliku projektu: {path}")
    j = json.loads(path.read_text(encoding="utf-8"))
    seq = j.get("sequence") or {}
    fps_osi = (seq.get("fps_num") or 30) / (seq.get("fps_den") or 1)
    w, h = seq.get("width") or 1280, seq.get("height") or 720
    sceny = j.get("scenes", [])
    zmiany = kiedy_zmieniona(path, sceny)
    markery = {}
    for m in j.get("frame_annotations") or []:
        if a.od and (m.get("updated_at") or m.get("created_at") or "")[:10] < a.od:
            continue
        markery.setdefault(m.get("scene_id"), []).append(m)

    out = [f"# Uwagi reżysera — {j.get('title', path.parent.name)}", "",
           f"Projekt `{path.parent.name}`, oś {fps_osi:g} kl./s, render {a.fps:g} kl./s, ekran {w} × {h}."]
    n_uwag = n_mark = 0
    for nr, s in enumerate(sceny, 1):
        u = uwaga(s)
        if u and a.od and zmiany.get(s["id"], "9999")[:10] < a.od:
            u = ""
        ms = sorted(markery.get(s["id"], []), key=lambda m: m.get("frame") or 0)
        if not u and not ms:
            continue
        start = float(s.get("start") or 0) / fps_osi
        dl = float(s.get("duration") or 0) / fps_osi
        out += ["", f"## {nr}. {s.get('title') or s['id']}  ·  oś {czas(start)}, {dl:.1f} s  ·  `{s['id']}`"]
        opis = (s.get("description") or "").strip().split("\n")[0]
        if opis:
            out.append(f"_Opis ujęcia:_ {opis}")
        if u:
            n_uwag += 1
            kiedy = zmiany.get(s["id"], "")
            out.append(f"- **Uwaga w ujęciu**{f' ({kiedy[:16].replace(chr(84), chr(32))})' if kiedy else ''}: {u}")
            out += [f"  - ↳ {p}" for p in podpowiedzi(u)]
        for m in ms:
            n_mark += 1
            f = m.get("frame") or 0
            fm = (m.get("fps_num") or 30) / (m.get("fps_den") or 1)
            sek = f / fm
            kiedy = (m.get("updated_at") or m.get("created_at") or "")[:16].replace("T", " ")
            out.append(f"- **Marker** {sek:.2f} s w ujęciu (klatka osi {f}, klatka renderu {round(sek * a.fps)}, "
                       f"oś {czas(start + sek)}; {kiedy}): {m.get('text', '').strip()}")
            out += [f"  - {k}" for k in kreski(m.get("strokes"), w, h)]
            out += [f"  - ↳ {p}" for p in podpowiedzi(m.get("text", ""))]
    out += ["", f"Razem: {n_uwag} uwag w ujęciach, {n_mark} markerów."]
    txt = "\n".join(out) + "\n"
    if a.md:
        Path(a.md).write_text(txt, encoding="utf-8")
        print(f"Zapisano {a.md}: {n_uwag} uwag, {n_mark} markerów.")
    else:
        sys.stdout.write(txt)


if __name__ == "__main__":
    main()
