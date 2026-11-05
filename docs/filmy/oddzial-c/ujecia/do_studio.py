"""Dopisuje wariant A (30 dni) do projektu Studio „Zombie Psychiatryk — Oddział C”, nie ruszając zimnego otwarcia.

uruchom (Studio musi działać):  python3 docs/filmy/oddzial-c/ujecia/do_studio.py <id projektu> [port]
- akt act_1 dostaje wybrany wariant „Dzień 1” (stary zostaje w wariantach), sekwencje części 2 przechodzą do act_1,
  akt act_2 znika (limit Studio to 30 aktów), dni 2–30 to akty act_d02…act_d30;
- każdy dzień: jedna sekwencja, sceny z rozpiski, plan reżyserski z beatami i ujęciami (czasy z a_dane*.py);
- istniejące sceny i plany zostają; podpisy planów przelicza kod Studio (flowTypes.ts), zatwierdzenia zostają reżyserowi.
"""
import copy
import json
import re
import subprocess
import tempfile
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
from a_dane1 import DAYS as D1  # noqa: E402
from a_dane2 import DAYS as D2  # noqa: E402
from buduj import KADR, RUCH, tc  # noqa: E402

PID = sys.argv[1]
API = f"http://127.0.0.1:{sys.argv[2] if len(sys.argv) > 2 else 8876}/api"
DAYS = [d for d in D1 + D2 if d[0] > 0]
COLD_OPEN = sum(s[2] for _, _, beats in D1[0][2] for _, shots in beats for s in shots)
# napięcie dnia (0–10): krzywa całego filmu
ARC = {1: 7, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 5, 8: 7, 9: 7, 10: 7, 11: 8, 12: 5, 13: 7, 14: 10, 15: 4, 16: 7, 17: 8,
       18: 3, 19: 5, 20: 6, 21: 7, 22: 6, 23: 8, 24: 7, 25: 7, 26: 5, 27: 6, 28: 4, 29: 8, 30: 10}
TYPE = {"PO": "wide", "PP": "wide", "PŚ": "medium", "NR": "over-shoulder", "Z": "close-up", "WZ": "extreme-close-up",
        "D": "insert", "POV": "pov", "TYT": "insert"}


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"),
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def node(nid, title, description):
    return {"id": nid, "variants": [{"id": nid + "_v1", "title": title, "description": description}], "selected": nid + "_v1"}


def day_texts():
    """Dzień → 20 zdań z A_DO_SWITU.md (opis aktu)."""
    out = {}
    for block in (HERE.parent / "A_DO_SWITU.md").read_text().split("\n## ")[1:]:
        n = int(re.match(r"Dzień (\d+)", block).group(1))
        out[n] = " ".join(re.sub(r"^\d+\. ", "", l) for l in block.splitlines() if re.match(r"^\d+\. ", l))
    return out


def pattern(shots):
    moves = [s[1] for s in shots]
    if {"szarp", "drg"} & set(moves) or moves.count("jaz") >= 2:
        return "chase"
    if any(s[0] == "TYT" for s in shots):
        return "exposition"
    if any(s[0] == "POV" for s in shots):
        return "anticipation"
    if sum(s[0] == "D" for s in shots) >= 2:
        return "investigation"
    if sum(":" in s[4] and not s[4].startswith("L:") for s in shots) >= 2:
        return "emotional"
    return "slow-burn"


def title_of(desc):
    parts = [x.strip() for x in re.split(r"[:;—]", desc) if x.strip()]
    head = parts[0]
    if len(head) < 25 and len(parts) > 1:  # „przez szybę: głowy…” — sam początek nic nie mówi
        head += ": " + parts[1]
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


texts = day_texts()
p = call(f"/projects/{PID}")
backup = Path(tempfile.gettempdir()) / f"oddzial-c-flow-przed-wariantem-A-rev{p['revision']}.json"
backup.write_text(json.dumps(p, ensure_ascii=False))
flow = copy.deepcopy(p["legacy"]["production_flow"])
if any(a["id"] == "act_d02" for a in flow["acts"]):
    raise SystemExit("Wariant A jest już w projekcie — nic nie zmieniam.")

flow["master"]["variants"].append({"id": "master_a36", "title": "Oddział C · Do świtu (36 min, 30 dni)", "description": (
    "Noc na oddziale C (gotowe zimne otwarcie): pacjenci przemieniają się, a telefon zdradza sanitariusza. Dzwoni Zosia z apteki "
    "w piwnicy: zarażeni idą na dźwięk, nie na światło. Sanitariusz wyprowadza z izolatki pana Henryka, który nie jest "
    "zarażony — oddycha tak wolno, że go nie słyszą. Od rana wojsko trzyma szpital w kordonie: kwarantanna 30 dni, potem "
    "ewakuacja zdrowych. Grupa w piwnicy (Zosia, Henryk, dr Nowak, pani Irena, Kuba) uczy się zasad: dźwięk, oddech, parami, "
    "nie otwieraj po zmroku. Zamki puściły, bo ktoś przeciął zasilanie — to Nowak, który ukrywa ugryzienie i chciał uciec. "
    "Agregat zamyka zarażonych w salach, ale alarm pożarowy ściąga wszystkich. Nowak przemienia się w izolatce 3, a Henryk "
    "odzyskuje głos i opowiada, że w noc wybuchu walił w szybę, żeby ostrzec. Wojsko wycofuje się, miasto płonie, kończy się "
    "woda i paliwo. Dnia 30 o świcie Henryk gra na pianinie podłączonym do alarmu i ściąga cały szpital do siebie, a reszta "
    "przechodzi podwórzem do ciężarówki. W oknie sali 8 sylwetka przekrzywia głowę jak w pierwszym ujęciu filmu. "
    "„Pan Henryk dalej nie mrugał. Pilnował ich do rana.”")})
flow["master"]["selected"] = "master_a36"

act1 = next(a for a in flow["acts"] if a["id"] == "act_1")
act1["variants"].append({"id": "act_1_a36", "title": f"Dzień 1 · {DAYS[0][1]}", "description": texts[1]})
act1["selected"] = "act_1_a36"
flow["acts"] = [act1] + [node(f"act_d{n:02d}", f"Dzień {n} · {title}", texts[n]) for n, title, _ in DAYS[1:]]
for seq in flow["sequences"]:
    if seq["actId"] == "act_2":
        seq["actId"] = "act_1"
assert len(flow["acts"]) == 30

scripts = {"act_1": flow["scripts"].get("act_1", "") + "\n\n" + flow["scripts"].get("act_2", "")}
t = COLD_OPEN
for n, title, scenes in DAYS:
    act = "act_1" if n == 1 else f"act_d{n:02d}"
    sid = f"seq_d{n:02d}"
    day_start, lines = t, []
    for si, (stitle, place, beats) in enumerate(scenes, 1):
        oid = f"sc_d{n:02d}_{si}"
        s0, plan_beats, plan_shots = t, [], []
        for bi, (btitle, shots) in enumerate(beats, 1):
            bid, pat = f"{oid}_b{bi}", pattern(shots)
            voice = [s[4][2:].strip() for s in shots if s[4].startswith("L:")]
            arc = ARC[n]
            plan_beats.append({
                "id": bid, "title": btitle, "goal": "; ".join(s[3] for s in shots)[:3900],
                "tensionBefore": max(0, arc - 2 if bi == 1 else arc - 1),
                "tensionAfter": min(10, arc + (1 if pat == "chase" else 0)),
                "viewerKnows": " ".join(voice)[:1900], "characterKnows": "",
                "soundCue": "; ".join(s[4] for s in shots if s[4] and not s[4].startswith("L:"))[:990],
                "patternId": pat})
            for k, (kadr, ruch, sec, desc, sound) in enumerate(shots, 1):
                plan_shots.append({
                    "id": f"{bid}_s{k}", "beatId": bid, "typeId": TYPE[kadr],
                    "title": f"Karta · {desc}" if kadr == "TYT" else title_of(desc),
                    "description": f"[{tc(t)}–{tc(t + sec)}] ({KADR[kadr]} · {RUCH[ruch]}) {desc}",
                    "duration": sec, "transition": "dip" if kadr == "TYT" else "cut", "sound": sound})
                if sound and ":" in sound:
                    lines.append(sound[2:].strip() if sound.startswith("L:") else sound)
                t += sec
        flow["outlines"].append({**node(oid, stitle, f"{place}. Beaty: " + ", ".join(b[0] for b in beats) + "."),
                                 "sectionId": sid, "seconds": round(t - s0, 1)})
        flow["director"]["plans"][oid] = {
            "outlineId": oid, "sourceSignature": "", "patternId": plan_beats[0]["patternId"], "mode": "manual",
            "notes": f"Wariant A · dzień {n} · scena {si} · {tc(s0)}–{tc(t)} filmu. Rozpiska: docs/filmy/oddzial-c/A_DO_SWITU_UJECIA.md",
            "beats": plan_beats, "shots": plan_shots}
    flow["sequences"].append({**node(sid, f"Dzień {n} · {title}", " → ".join(s[0] for s in scenes) + "."),
                              "actId": act, "seconds": round(t - day_start, 1)})
    scripts[act] = (scripts.get(act, "") + "\n\n" if act in scripts else "") + "\n\n".join(lines)
flow["scripts"] = scripts

b = flow["bible"]
b["characters"] += ("\n\nWariant A (30 dni): Zosia — pielęgniarka z apteki w piwnicy, przywódczyni; dr Nowak — lekarz dyżurny, "
                    "ukrywa ugryzienie, przeciął zasilanie, przemienia się w izolatce 3 (dzień 17); pani Irena — 81 lat, "
                    "oddział A, chore płuca; Kuba — 17 lat, oddział A, po próbie samobójczej; por. Malec — dowódca kordonu "
                    "(głos w telefonie); Basia — zarażona kucharka w chłodni. Pan Henryk Wilk — były nauczyciel muzyki, "
                    "nie zarażony, odzyskuje głos w dniu 18, zostaje w szpitalu w dniu 30.")
b["chronology"] += ("\n\nWariant A: noc 1 = zimne otwarcie + dzień 1; dni 2–30 = kwarantanna wojska. Kluczowe: dzień 7 przecięty "
                    "kabel, 14 agregat i alarm, 16 wyznanie Nowaka, 18 Henryk mówi, 20 telefon z kordonu, 27 plan z pianinem, "
                    "30 świt i ewakuacja.")
b["transitions"] += ("\n\nKażdy dzień zaczyna się 2-sekundową kartą „DZIEŃ N” (przejście przez czerń). Dzień 30 kończy się tym "
                     "samym kadrem co pierwsze ujęcie filmu (okno sali 8).")

signed = subprocess.run(["node", "--experimental-strip-types", str(REPO / "output/zombie-psychiatryk/studio_signatures.mjs"),
                         str(REPO / "apps/studio/src/flowTypes.ts")],
                        input=json.dumps(flow), capture_output=True, text=True, check=True).stdout
p = call(f"/projects/{PID}/flow", {"expected_revision": p["revision"], "flow": json.loads(signed)}, "PUT")

# ujęcia części 2 należały do act_2 — teraz to dzień 1 (act_1)
scenes = p["scenes"]
for s in scenes:
    if s["legacy"].get("flow_act_id") == "act_2":
        s["legacy"]["flow_act_id"] = "act_1"
p = call(f"/projects/{PID}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
fl = p["legacy"]["production_flow"]
print(f"kopia: {backup}")
print(f"rewizja {p['revision']} | akty {len(fl['acts'])} | sekwencje {len(fl['sequences'])} | sceny {len(fl['outlines'])} | "
      f"plany {len(fl['director']['plans'])} | ujęcia w planach {sum(len(x['shots']) for x in fl['director']['plans'].values())} | "
      f"film {tc(t)}")
