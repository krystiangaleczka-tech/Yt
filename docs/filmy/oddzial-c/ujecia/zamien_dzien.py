"""Podmienia jeden dzień wariantu A w Studio po zmianie rozpiski (a_dane*.py) i promptów (p_d*.py).

uruchom (Studio musi działać):  python3 docs/filmy/oddzial-c/ujecia/zamien_dzien.py <dzień> <id projektu> [port] [tylko_plan] [wymus]
- tylko_plan: aktualizuje plan filmu (akt, sceny, plany reżyserskie), oś montażu zostaje bez zmian;
- przed zmianą osi uruchamia kontrolę ciągłości; błędy wagi 3 w tym dniu zatrzymują pracę (chyba że „wymus”);
- każda podmiana dopisuje wpis do dziennika pracy filmu.
- plany reżyserskie scen sc_dNN_* (beaty, ujęcia, czasy) i sekundy scen/sekwencji z rozpiski; podpisy liczy kod Studio;
- stare ujęcia dnia i ich klipy na osi znikają, nowe wchodzą od tego samego miejsca (tryb „Prompt AI” z promptem);
- jeśli dzień zmienił długość, późniejsze ujęcia i klipy przesuwają się o różnicę;
- zimne otwarcie i inne dni zostają. Potem: output/zombie-psychiatryk/studio_dzien.py <dzień> <projekt> — materiał.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import prompty  # noqa: E402
from buduj import KADR, RUCH, tc  # noqa: E402

FLAGS = {a for a in sys.argv[1:] if a in ("tylko_plan", "wymus")}
ARGS = [a for a in sys.argv[1:] if a not in FLAGS]
DAY, PID = int(ARGS[0]), ARGS[1]
API = f"http://127.0.0.1:{ARGS[2] if len(ARGS) > 2 else 8876}/api"
H = {"Content-Type": "application/json", "X-Docos-Request": "1"}
TYPE = {"PO": "wide", "PP": "wide", "PŚ": "medium", "NR": "over-shoulder", "Z": "close-up", "WZ": "extreme-close-up",
        "D": "insert", "POV": "pov", "TYT": "insert"}
NAMES = {"wide": "Wide Shot", "medium": "Medium Shot", "close-up": "Close-Up", "extreme-close-up": "Extreme Close-Up",
         "insert": "Insert Shot", "pov": "POV Shot", "over-shoulder": "Over-the-Shoulder"}
ARC = {1: 7, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 5, 8: 7, 9: 7, 10: 7, 11: 8, 12: 5, 13: 7, 14: 10, 15: 4, 16: 7, 17: 8,
       18: 3, 19: 5, 20: 6, 21: 7, 22: 6, 23: 8, 24: 7, 25: 7, 26: 5, 27: 6, 28: 4, 29: 8, 30: 10}


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"), headers=H,
                                 data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)


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
    head = parts[0] + (": " + parts[1] if len(parts[0]) < 25 and len(parts) > 1 else "")
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


title, rows = prompty.rows_of(DAY)
shots_p = prompty.load_shots()[DAY]
assert [s[0] for s in shots_p] == [r[6][0] for r in rows], "prompty nie zgadzają się z rozpiską"
p = call(f"/projects/{PID}")
flow = p["legacy"]["production_flow"]
fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
sid, act = f"seq_d{DAY:02d}", "act_1" if DAY == 1 else f"act_d{DAY:02d}"

# --- plan: sceny, beaty, ujęcia ---
from a_dane1 import DAYS as D1  # noqa: E402
from a_dane2 import DAYS as D2  # noqa: E402
scenes_data = next(d for d in D1 + D2 if d[0] == DAY)[2]
t = rows[0][5]
lines, outlines = [], []
for si, (stitle, place, beats) in enumerate(scenes_data, 1):
    oid = f"sc_d{DAY:02d}_{si}"
    s0, pbeats, pshots = t, [], []
    for bi, (btitle, shots) in enumerate(beats, 1):
        bid, pat = f"{oid}_b{bi}", pattern(shots)
        arc = ARC[DAY]
        pbeats.append({"id": bid, "title": btitle, "goal": "; ".join(s[3] for s in shots)[:3900],
                       "tensionBefore": max(0, arc - 2 if bi == 1 else arc - 1), "tensionAfter": min(10, arc + (pat == "chase")),
                       "viewerKnows": " ".join(s[4][2:].strip() for s in shots if s[4].startswith("L:"))[:1900],
                       "characterKnows": "", "soundCue": "; ".join(s[4] for s in shots if s[4] and not s[4].startswith("L:"))[:990],
                       "patternId": pat})
        for k, (kadr, ruch, sec, desc, sound) in enumerate(shots, 1):
            pshots.append({"id": f"{bid}_s{k}", "beatId": bid, "typeId": TYPE[kadr],
                           "title": f"Karta · {desc}" if kadr == "TYT" else title_of(desc),
                           "description": f"[{tc(t)}–{tc(t + sec)}] ({KADR[kadr]} · {RUCH[ruch]}) {desc}",
                           "duration": sec, "transition": "dip" if kadr == "TYT" else "cut", "sound": sound})
            if ":" in sound:
                lines.append(sound[2:].strip() if sound.startswith("L:") else sound)
            t += sec
    desc = f"{place}. Beaty: " + ", ".join(b[0] for b in beats) + "."
    outline = next((o for o in flow["outlines"] if o["id"] == oid), None)
    if outline is None:  # nowa scena dnia — za ostatnią sceną tego dnia
        outline = {"id": oid, "variants": [{"id": oid + "_v1", "title": stitle, "description": desc}],
                   "selected": oid + "_v1", "sectionId": sid, "seconds": 0}
        last = max(i for i, o in enumerate(flow["outlines"]) if o["sectionId"] == sid)
        flow["outlines"].insert(last + 1, outline)
    v = next(x for x in outline["variants"] if x["id"] == outline["selected"])
    v.update(title=stitle, description=desc)
    outline["seconds"] = round(t - s0, 1)
    plan = flow["director"]["plans"].setdefault(oid, {"outlineId": oid, "sourceSignature": "", "mode": "manual"})
    plan.update(patternId=pbeats[0]["patternId"], beats=pbeats, shots=pshots,
                notes=f"Wariant A · dzień {DAY} · scena {si} · {tc(s0)}–{tc(t)} filmu.")
gone = [o["id"] for o in flow["outlines"] if o["sectionId"] == f"seq_d{DAY:02d}" and int(o["id"].rsplit("_", 1)[1]) > len(scenes_data)]
flow["outlines"] = [o for o in flow["outlines"] if o["id"] not in gone]
for oid in gone:
    flow["director"]["plans"].pop(oid, None)
new_len = t - rows[0][5]
seq = next(s for s in flow["sequences"] if s["id"] == sid)
seq["seconds"] = round(new_len, 1)
if DAY == 1:  # akt 1 = zimne otwarcie (części 1 i 2) + dzień 1; skrypt otwarcia zostaje
    head = flow["scripts"]["act_1"].split("\n\n")
    flow["scripts"]["act_1"] = "\n\n".join(head[:10] + lines)
else:
    flow["scripts"][act] = "\n\n".join(lines)
signed = subprocess.run(["node", "--experimental-strip-types", str(REPO / "output/zombie-psychiatryk/studio_signatures.mjs"),
                         str(REPO / "apps/studio/src/flowTypes.ts")], input=json.dumps(flow), capture_output=True, text=True,
                        check=True).stdout
p = call(f"/projects/{PID}/flow", {"expected_revision": p["revision"], "flow": json.loads(signed)}, "PUT")

report = call(f"/projects/{PID}/continuity/check", {})
mine = [i for i in report["issues"] if i["unit"] == DAY]
w = {k: sum(1 for i in mine if i["severity"] == k) for k in (3, 2, 1)}
for i in mine:
    if i["severity"] == 3:
        print(f"  ✗ {i['ref'] or '—'} {i['rule']}: {i['message']}")


def log(summary, details=""):
    call(f"/projects/{PID}/flow/log", {"entry": {"who": "zamien_dzien.py", "unit": DAY, "kind": "tworzenie", "summary": summary,
                                                 "details": details, "files": [f"docs/filmy/oddzial-c/ujecia/a_dane*.py"]}})


if "tylko_plan" in FLAGS:
    log(f"Plan dnia {DAY} zaktualizowany z rozpiski ({len(rows)} ujęć, {t - rows[0][5]:.1f} s); oś bez zmian",
        f"Kontrola dnia: {w[3]} / {w[2]} / {w[1]} (waga 3 / 2 / 1).")
    print(f"dzień {DAY}: plan zaktualizowany (oś bez zmian) | kontrola {w[3]}/{w[2]}/{w[1]}")
    sys.exit(0)
if w[3] and "wymus" not in FLAGS:
    sys.exit(f"dzień {DAY}: {w[3]} błędów wagi 3 w kontroli ciągłości — popraw albo uruchom z „wymus” (zostanie zapisane w dzienniku)")
p = call(f"/projects/{PID}")

# --- oś: usuń klipy starych ujęć dnia, przesuń późniejsze ---
old = sorted((s for s in p["scenes"] if s["legacy"].get("flow_section_id") == sid), key=lambda s: s["start"])
start = old[0]["start"]
old_end = max(s["start"] + s["duration"] for s in old)
old_ids = {s["id"] for s in old}
frames = [max(1, round(r[6][2] * fps)) for r in rows]
delta = start + sum(frames) - old_end
ops = [{"type": "remove_clip", "clip_id": c["id"]} for c in p["sequence"]["clips"] if c.get("scene_id") in old_ids]
if delta:
    ops += [{"type": "move_clip", "clip_id": c["id"], "changes": {"start": c["start"] + delta}} for c in p["sequence"]["clips"]
            if c.get("scene_id") not in old_ids and c["start"] >= old_end]
for i in range(0, len(ops), 200):  # serwer przyjmuje do 200 operacji w jednej edycji
    p = call(f"/projects/{PID}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})

# --- ujęcia: nowe w miejsce starych ---
flow = p["legacy"]["production_flow"]
new, cursor = [], start
for ((si, stitle, bi, btitle, k, _, (kadr, ruch, sec, desc, sound)), (_, prompt, note)), fr in zip(zip(rows, shots_p), frames):
    oid = f"sc_d{DAY:02d}_{si}"
    plan = flow["director"]["plans"][oid]
    item = next(x for x in plan["shots"] if x["id"] == f"{oid}_b{bi}_s{k}")
    beat = next(b for b in plan["beats"] if b["id"] == item["beatId"])
    index = [x["id"] for x in plan["shots"]].index(item["id"]) + 1
    notes = [f"Typ: {NAMES.get(item['typeId'], item['typeId'])}", f"Przejście: {item['transition']}", sound and f"Dźwięk: {sound}",
             f"Beat: {beat['title']} (napięcie {beat['tensionBefore']}→{beat['tensionAfter']})", f"Kadr: {KADR[kadr]} · {RUCH[ruch]}", note]
    new.append({"title": f"{stitle} · {index:02d} · {item['title']}",
                "narration": sound[2:].strip() if sound.startswith("L:") else "", "description": desc,
                "director_notes": ". ".join(x for x in notes if x)[:3000], "start": cursor, "duration": fr, "timing": "estimated",
                "mode": "generate" if prompt else "search", "prompt": prompty.full(prompt) or note,
                "motion_prompt": RUCH[ruch] if ruch != "stat" else "", "search_query": item["title"], "animation": "static",
                "asset_id": None, "voice_asset_id": None, "variants": [], "fact_ids": [], "role": "illustration", "locked": False,
                "legacy": {"flow_act_id": act, "flow_section_id": sid, "flow_outline_id": oid, "flow_director_shot_id": item["id"],
                           "flow_director_beat_id": item["beatId"], "flow_director_kind": item["typeId"],
                           "image_negative_prompt": prompty.NEGATIVE}})
    cursor += fr
scenes = []
for s in p["scenes"]:
    if s["id"] in old_ids:
        if s["id"] == old[0]["id"]:
            scenes += new
        continue
    if delta and s["start"] >= old_end:
        s["start"] += delta
    scenes.append(s)
p = call(f"/projects/{PID}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
import os_montazu  # noqa: E402  — pozycje z zapisów ujęć mogą się rozjechać z osią: układamy obraz od nowa
moved, _, _ = os_montazu.uloz(PID, int(API.rsplit(":", 1)[1].split("/")[0]))
p = call(f"/projects/{PID}")
mine = [s for s in p["scenes"] if s["legacy"].get("flow_section_id") == sid]
print(f"dzień {DAY}: {len(old)} → {len(mine)} ujęć | {tc(new_len)} | przesunięcie dalszych: {delta} kl. | rewizja {p['revision']}")
log(f"Dzień {DAY} podmieniony w Studio: {len(rows)} ujęć, {t - rows[0][5]:.1f} s", f"Kontrola dnia: {w[3]} / {w[2]} / {w[1]}"
    + (" — WYMUSZONO mimo błędów wagi 3" if w[3] else ""))
