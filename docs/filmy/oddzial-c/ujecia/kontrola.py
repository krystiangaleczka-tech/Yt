"""Kontrola ciągłości bez Studio: rozpiska (a_dane*.py) + kopia księgi świata (swiat.json) → ten sam raport co
„Sprawdź ciągłość” w Continuity Editor (studio_core.continuity.check).

uruchom:  python3 docs/filmy/oddzial-c/ujecia/kontrola.py [dzień …] [--wszystko]
- bez argumentów: podsumowanie wag 3 / 2 / 1 dla każdego dnia i lista błędów wagi 3;
- z numerami dni: pełna lista uwag tych dni; --wszystko: pełna lista uwag całego filmu.
Plan budowany jest tak jak w zamien_dzien.py (tytuł ujęcia z opisu, akt 1 = zimne otwarcie + dzień 1), więc wynik
odpowiada temu, co pokaże Studio po wgraniu rozpiski — pod warunkiem, że księga w Studio jest taka jak swiat.json.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
from a_dane1 import DAYS as D1  # noqa: E402
from a_dane2 import DAYS as D2  # noqa: E402
from studio_core import continuity  # noqa: E402


def title_of(desc):  # jak w zamien_dzien.py
    parts = [x.strip() for x in re.split(r"[:;—]", desc) if x.strip()]
    head = parts[0] + (": " + parts[1] if len(parts[0]) < 25 and len(parts) > 1 else "")
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


def flow_z_rozpiski(world):
    acts, sequences, outlines, plans = [], [], [], {}
    for n, title, scenes in D1 + D2:
        unit = max(1, n)  # dzień 0 (zimne otwarcie) to prolog aktu 1
        act = f"act_{unit:02d}"
        if not any(a["id"] == act for a in acts):
            acts.append({"id": act, "variants": [{"id": act + "_v", "title": title}], "selected": act + "_v"})
            sequences.append({"id": f"seq_{unit:02d}", "actId": act})
        for si, (stitle, _, beats) in enumerate(scenes, 1):
            oid = f"sc_d{n:02d}_{si}"
            outlines.append({"id": oid, "sectionId": f"seq_{unit:02d}"})
            shots = [{"id": f"{oid}_b{bi}_s{k}", "title": f"Karta · {desc}" if kadr == "TYT" else title_of(desc),
                      "description": desc, "sound": sound, "duration": sec}
                     for bi, (_, sh) in enumerate(beats, 1) for k, (kadr, _, sec, desc, sound) in enumerate(sh, 1)]
            plans[oid] = {"shots": shots}
    return {"world": world, "acts": acts, "sequences": sequences, "outlines": outlines, "director": {"plans": plans}}


def main(argv):
    world = json.loads((HERE.parent / "swiat.json").read_text(encoding="utf-8"))
    report = continuity.check(flow_z_rozpiski(world))
    issues = report["issues"]
    days = {int(a) for a in argv if a.isdigit()}
    if days or "--wszystko" in argv:
        for i in sorted(issues, key=lambda i: (i["unit"] if i["unit"] is not None else -1, -i["severity"])):
            if "--wszystko" in argv or i["unit"] in days:
                where = i["ref"] or f"dzień {i['unit']}"
                print(f"[{i['severity']}] {where} {i['rule']}: {i['message']}")
        return
    units = sorted({i["unit"] for i in issues if i["unit"] is not None})
    for u in units:
        w = [sum(1 for i in issues if i["unit"] == u and i["severity"] == s) for s in (3, 2, 1)]
        print(f"dzień {u:2d}: {w[0]} / {w[1]} / {w[2]}")
    loose = [i for i in issues if i["unit"] is None]
    total = [sum(1 for i in issues if i["severity"] == s) for s in (3, 2, 1)]
    print(f"razem (waga 3 / 2 / 1): {total[0]} / {total[1]} / {total[2]}" + (f", bez dnia: {len(loose)}" if loose else ""))
    for i in issues:
        if i["severity"] == 3:
            print(f"  ✗ {i['ref'] or '—'} {i['rule']}: {i['message']}")


if __name__ == "__main__":
    main(sys.argv[1:])
