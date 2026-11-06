"""Miara kwestii: czy lektor i postacie mówią zdaniami, czy urywkami (MASTER_BIBLE.md 2.4a, podręcznik „Rytm” 4a).

uruchom:  python3 docs/filmy/oddzial-c/ujecia/styl_kwestii.py [dzień …] [--lista]
- tabela: średnio słów w zdaniu i odsetek zdań do 3 słów — lektor i dialog osobno, dzień po dniu, wzorzec = zimne otwarcie;
- „posiekane”: kwestia z kilku zdań, w której któreś ma do 3 słów („Nożyce leżały obok. Z warsztatu.”);
- „echo”: kwestia lektora, której słowa w większości powtarzają opis kadru (lektor opisuje obraz zamiast dopowiadać);
- --lista (albo numery dni): wypisuje posiekane kwestie i echa z odwołaniem dNN_KK.
To miara, nie wyrok: krótka replika („Nie.”, „Teraz.”) albo puenta sceny mogą zostać — byle nie były regułą.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a_dane1 import DAYS as D1  # noqa: E402
from a_dane2 import DAYS as D2  # noqa: E402

PROG = {"lektor_srednio": 5.0, "lektor_krotkie": 0.25, "dialog_srednio": 4.5, "dialog_krotkie": 0.30, "posiekane": 1,
        "probka": 6}  # progi średniej liczymy, gdy dzień ma co najmniej tyle zdań (kilka krótkich replik to nie reguła)
QUOTE = re.compile(r"„([^”]+)”")


def text_of(sound):
    if sound.startswith("L:"):
        return "L", sound[2:].strip()
    m = QUOTE.search(sound)
    return ("D", m.group(1)) if m else (None, "")


def sentences(text):
    return [s for s in (x.strip(" ,;:—-") for x in re.split(r"(?<=[.!?…])\s+", text.strip())) if s]


def words(s):
    return re.findall(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", s)


def stem(w):
    return w.lower()[:5]


def echo(text, desc):
    """Udział treściwych słów kwestii, które są też w opisie kadru."""
    mine = {stem(w) for w in words(text) if len(w) >= 4}
    seen = {stem(w) for w in words(desc) if len(w) >= 4}
    return len(mine & seen) / len(mine) if mine else 0.0


def shots(day):
    out, k = [], 0
    for _, _, beats in day[2]:
        for _, sh in beats:
            for kadr, _, _, desc, sound in sh:
                k += 1
                out.append((f"d{day[0]:02d}_{k:02d}", desc, sound))
    return out


def stats(day):
    res = {"L": [], "D": [], "posiekane": [], "echo": []}
    for ref, desc, sound in shots(day):
        who, text = text_of(sound)
        if not who:
            continue
        ss = sentences(text)
        res[who] += [len(words(s)) for s in ss]
        if len(ss) > 1 and any(len(words(s)) <= 3 for s in ss):
            res["posiekane"].append((ref, sound))
        if who == "L" and echo(text, desc) >= 0.6:
            res["echo"].append((ref, sound))
    return res


def fmt(ws):
    if not ws:
        return "    —        "
    return f"{sum(ws) / len(ws):4.1f}  {sum(w <= 3 for w in ws) / len(ws):4.0%}   "


def main(argv):
    pick = {int(a) for a in argv if a.isdigit()}
    show = "--lista" in argv or bool(pick)
    print("dzień  lektor: słów/zd. ≤3 sł.  dialog: słów/zd. ≤3 sł.  posiekane  echo")
    total = {"L": [], "D": [], "posiekane": [], "echo": []}
    for day in D1 + D2:
        if pick and day[0] not in pick:
            continue
        r = stats(day)
        if day[0]:
            for k in total:
                total[k] += r[k]
        bad = []
        if len(r["L"]) >= PROG["probka"] and (sum(r["L"]) / len(r["L"]) < PROG["lektor_srednio"]
                       or sum(w <= 3 for w in r["L"]) / len(r["L"]) > PROG["lektor_krotkie"]):
            bad.append("lektor")
        if len(r["D"]) >= PROG["probka"] and (sum(r["D"]) / len(r["D"]) < PROG["dialog_srednio"]
                       or sum(w <= 3 for w in r["D"]) / len(r["D"]) > PROG["dialog_krotkie"]):
            bad.append("dialog")
        if len(r["posiekane"]) > PROG["posiekane"]:
            bad.append("posiekane")
        label = "wzorzec" if day[0] == 0 else f"{day[0]:5d}"
        print(f"{label:7s}       {fmt(r['L'])}          {fmt(r['D'])}   {len(r['posiekane']):5d}  {len(r['echo']):4d}"
              + (f"   ← {', '.join(bad)}" if bad and day[0] else ""))
        if show and day[0]:
            for ref, s in r["posiekane"]:
                print(f"        posiekane {ref}: {s}")
            for ref, s in r["echo"]:
                print(f"        echo      {ref}: {s}")
    if not pick:
        print(f"dni 1–30      {fmt(total['L'])}          {fmt(total['D'])}   {len(total['posiekane']):5d}  {len(total['echo']):4d}")
    print(f"progi: lektor ≥ {PROG['lektor_srednio']} słowa/zdanie i ≤ {PROG['lektor_krotkie']:.0%} zdań do 3 słów; "
          f"dialog ≥ {PROG['dialog_srednio']} i ≤ {PROG['dialog_krotkie']:.0%}; posiekane ≤ {PROG['posiekane']} na dzień")


if __name__ == "__main__":
    main(sys.argv[1:])
