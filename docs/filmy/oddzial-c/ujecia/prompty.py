"""Prompty obrazów do ujęć wariantu A: plik do wklejenia w inne AI i ujęcia w Studio (tryb „Prompt AI”).

uruchom:  python3 docs/filmy/oddzial-c/ujecia/prompty.py <od> <do>              → ../A_PROMPTY_DNI_<od>-<do>.md
          python3 docs/filmy/oddzial-c/ujecia/prompty.py <od> <do> <projekt>    → też ujęcia tych dni w Studio
Dane: p_d*.py — SHOTS = {dzień: [(kadr, prompt albo None, uwaga produkcyjna), …]} w kolejności ujęć z a_dane*.py.
Styl, postacie i lokacje wspólne (wzięte z renderów kontrola-render*.png), więc każdy prompt jest samowystarczalny.
"""
import importlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

STYLE = ("Flat 2D cartoon horror illustration in the style of animated scary-story YouTube videos: thick wobbly hand-drawn "
         "black outlines, simple rounded shapes, flat muted colours with no gradients, cold desaturated green-grey palette, "
         "soft dark vignette at the edges, subtle film grain. Aspect ratio 16:9. No text, no captions, no watermark.")
NEGATIVE = ("photorealistic, 3D render, anime, manga, glossy, detailed shading, gradients, text, subtitles, watermark, logo, "
            "extra fingers, extra limbs, gore, blood splatter, frame border")
REF = {
    "NARRATOR": "a male hospital orderly in his thirties (simple round head, short messy dark-brown hair, light stubble drawn "
                "as small dots, small black dot eyes, thin eyebrows, pale skin, light-blue hospital scrubs with a V-neck, white sneakers)",
    "HENRYK": "Mr Henryk, a thin patient in his sixties (very pale grey-green skin, sparse grey hair at the sides of a bald head, "
              "sunken cheeks, wide round white eyes with tiny black pupils that never blink, faded grey patient gown)",
    "ZOSIA": "Zosia, a nurse in her forties (dark hair in a tight bun, round face, tired eyes, white nurse uniform under a navy "
             "cardigan, ID badge on a lanyard)",
    "PATIENTS": "infected psychiatric patients (pale green skin, grey-green hospital gowns, round white eyes with tiny black "
                "pupils, slack open mouths, slightly hunched, each one different: a bald old man, a woman with a long braid, "
                "a tall thin young man, a short heavy woman)",
    "CORRIDOR": "the long corridor of Ward C at night (one-point perspective, pale green walls with a darker green lower band, "
                "grey tiled floor, grey doors with small dark windows on both sides, fluorescent tubes on the ceiling)",
    "DUTYROOM": "the night duty room with the lights off (dark navy-blue walls, a red wall calendar, a grey double wardrobe, "
                "a brown wooden desk with a beige rotary telephone, a door with a glass window on the right, a light switch by the door)",
    "ISODOOR": "the door of isolation room 3 (grey-green metal door with a small square window covered by a diamond wire mesh, "
               "a small plaque with the number 3, a black door handle)",
    "BASEMENT": "the hospital basement (narrow concrete corridor with pipes along the ceiling, a pharmacy behind a floor-to-ceiling "
                "metal grille, shelves of medicine boxes, a cracked lamp flickering inside)",
    "IRENA": "Mrs Irena, a frail patient in her eighties (white hair in a loose bun, wrinkled kind face, pink flowered "
             "dressing gown, slippers)",
    "KUBA": "Kuba, a skinny seventeen-year-old patient (messy black hair, thin pale face, dark grey tracksuit)",
    "NOWAK": "Dr Nowak, the duty doctor in his fifties (receding grey hair, glasses, pale sweaty face, white coat over a dark "
             "sweatshirt zipped up to the chin, long sleeves)",
    "SOLDIERS": "soldiers in olive uniforms and gas masks",
    "FACADE": "the old hospital building (grey four-storey facade, rows of dark barred windows, a clock on the roof gable)",
    "YARD": "the hospital yard (patchy lawn, a gravel path, a parked white ambulance, a tall chain-link fence with an old iron "
            "gate, dark forest beyond)",
    "CONNECTOR": "a long connector corridor between hospital wings (tall windows looking onto the yard, linoleum floor)",
    "KITCHEN": "the hospital kitchen (large steel cooking pots, white tiled walls, a steel walk-in fridge door with a small window)",
    "WARD_A": "Ward A on the first floor (a day room with tables, plastic chairs and an old TV, a corridor with grey doors)",
    "STAFFROOM": "the ground-floor staff room (a worn brown sofa, a small kitchenette with a kettle and an electric hob, a "
                 "fridge, a wall telephone, a window onto the yard)",
    "ELECTRICAL": "the basement electrical room (grey metal switch cabinets, thick cables, a yellow high-voltage sign)",
    "GENERATOR": "the technical wing (a large old diesel generator, fuel drums, bare concrete walls)",
    "LODGE": "the porter's lodge at the main entrance (a desk, a wall-mounted fire-alarm control panel)",
    "ROOM8": "ward room 8 (overturned metal beds, a wooden wardrobe in the corner, a dusty window looking at the gate)",
    "DAYROOM": "the ground-floor day room (an old upright piano, worn armchairs, tall windows)",
    "ROOF": "the flat hospital roof (a rainwater tank, a roof hatch, gutters, the city on the horizon)",
    "SURGERY": "the dark third-floor surgical corridor (closed doors with small windows on both sides)",
}
LAYERS = ("Do produkcji: osobne warstwy — tło za otworem, postać jako PNG z przezroczystym tłem, ściana/drzwi z wyciętym otworem "
          "jako pierwszy plan (WYTYCZNE_UJEC 1.1 i 2). Pełny kadr z tego promptu służy tylko do testu wyglądu.")


def full(prompt):
    return prompt.format(**REF) + " " + STYLE if prompt else ""


def load_shots():
    shots = {}
    for f in sorted(HERE.glob("p_d*.py")):
        shots.update(importlib.import_module(f.stem).SHOTS)
    return shots


def rows_of(n):
    from a_dane1 import DAYS as D1
    from a_dane2 import DAYS as D2
    days = D1 + D2
    t = 0.0
    for d, _, scenes in days:
        rows = []
        for si, (stitle, place, beats) in enumerate(scenes, 1):
            for bi, (btitle, shots) in enumerate(beats, 1):
                for k, shot in enumerate(shots, 1):
                    rows.append((si, stitle, bi, btitle, k, t, shot))
                    t += shot[2]
        if d == n:
            return next(x for x in days if x[0] == n)[1], rows


def main(first, last, pid=None, port=8876):
    from buduj import KADR, RUCH, tc
    data = load_shots()
    md = [f"# Dni {first}–{last} · prompty obrazów (wariant A)", "",
          "Każdy prompt jest pełny: można go wkleić w dowolny generator obrazów bez kontekstu. Styl, postacie i lokacje są "
          "takie same we wszystkich, żeby kadry były spójne. Ruch kamery z rozpiski robi się w montażu — prompt opisuje kadr "
          "w kluczowym momencie ujęcia. Napisy (kartki, karty dni, HUD) dodaje się w Studio, nie w generatorze.", "",
          "**Negative prompt** (jeśli generator go obsługuje):", "", "```", NEGATIVE, "```", ""]
    plan = {}
    for n in range(first, last + 1):
        title, rows = rows_of(n)
        shots = data[n]
        got, want = [s[0] for s in shots], [r[6][0] for r in rows]
        assert got == want, f"dzień {n}: kolejność kadrów {got} ≠ rozpiska {want}"
        plan[n] = (title, rows, shots)
        md += [f"## Dzień {n} · {title} `{tc(rows[0][5])}–{tc(rows[-1][5] + rows[-1][6][2])}` · {len(rows)} ujęć", ""]
        current = None
        for i, ((si, stitle, bi, btitle, k, start, (kadr, ruch, sec, desc, sound)), (_, prompt, note)) in enumerate(zip(rows, shots), 1):
            if si != current:
                md += [f"### Scena {n}.{si} · {stitle}", ""]
                current = si
            md += [f"**{n}.{i:02d}** · `{tc(start)}–{tc(start + sec)}` ({kadr} · {ruch}) · beat {n}.{si}.{bi} {btitle}  ",
                   f"{desc}" + (f" — *{sound}*" if sound else ""), ""]
            md += (["```", full(prompt), "```", ""] if prompt else [f"*{note}*", ""])
            if prompt and note:
                md += [f"*{note}*", ""]
    name = "A_DZIEN01_PROMPTY.md" if first == last == 1 else f"A_PROMPTY_DNI_{first:02d}-{last:02d}.md"
    (HERE.parent / name).write_text("\n".join(md))
    print(f"{name}: {sum(len(v[1]) for v in plan.values())} ujęć")
    if pid:
        to_studio(plan, pid, port, KADR, RUCH)


def to_studio(plan, pid, port, KADR, RUCH):
    api, h = f"http://127.0.0.1:{port}/api", {"Content-Type": "application/json", "X-Docos-Request": "1"}

    def call(path, body=None, method=None):
        req = urllib.request.Request(api + path, method=method or ("POST" if body is not None else "GET"), headers=h,
                                     data=None if body is None else json.dumps(body).encode())
        with urllib.request.urlopen(req) as r:
            return json.load(r)

    names = {"wide": "Wide Shot", "medium": "Medium Shot", "close-up": "Close-Up", "extreme-close-up": "Extreme Close-Up",
             "insert": "Insert Shot", "pov": "POV Shot", "over-shoulder": "Over-the-Shoulder"}
    p = call(f"/projects/{pid}")
    flow = p["legacy"]["production_flow"]
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    cursor = max([0] + [s["start"] + s["duration"] for s in p["scenes"]])
    have = {s["legacy"].get("flow_section_id") for s in p["scenes"]}
    added = []
    for n, (title, rows, shots) in plan.items():
        if f"seq_d{n:02d}" in have:
            print(f"dzień {n} ma już ujęcia w Studio — pomijam")
            continue
        for (si, stitle, bi, btitle, k, start, (kadr, ruch, sec, desc, sound)), (_, prompt, note) in zip(rows, shots):
            oid = f"sc_d{n:02d}_{si}"
            dplan = flow["director"]["plans"][oid]
            item = next(x for x in dplan["shots"] if x["id"] == f"{oid}_b{bi}_s{k}")
            beat = next(b for b in dplan["beats"] if b["id"] == item["beatId"])
            index = [x["id"] for x in dplan["shots"]].index(item["id"]) + 1
            notes = [f"Typ: {names.get(item['typeId'], item['typeId'])}", f"Przejście: {item['transition']}",
                     sound and f"Dźwięk: {sound}", f"Beat: {beat['title']} (napięcie {beat['tensionBefore']}→{beat['tensionAfter']})",
                     f"Kadr: {KADR[kadr]} · {RUCH[ruch]}", note]
            frames = max(1, round(sec * fps))
            added.append({
                "title": f"{stitle} · {index:02d} · {item['title']}", "narration": sound[2:].strip() if sound.startswith("L:") else "",
                "description": desc, "director_notes": ". ".join(x for x in notes if x)[:3000],
                "start": cursor, "duration": frames, "timing": "estimated",
                "mode": "generate" if prompt else "search", "prompt": full(prompt) or note,
                "motion_prompt": RUCH[ruch] if ruch != "stat" else "", "search_query": item["title"], "animation": "static",
                "asset_id": None, "voice_asset_id": None, "variants": [], "fact_ids": [], "role": "illustration", "locked": False,
                "legacy": {"flow_act_id": "act_1" if n == 1 else f"act_d{n:02d}", "flow_section_id": f"seq_d{n:02d}",
                           "flow_outline_id": oid, "flow_director_shot_id": item["id"], "flow_director_beat_id": item["beatId"],
                           "flow_director_kind": item["typeId"], "image_negative_prompt": NEGATIVE}})
            cursor += frames
    if added:
        p = call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": p["scenes"] + added}}, "PATCH")
    print(f"Studio: dodano {len(added)} ujęć | ujęć razem {len(p['scenes'])} | koniec {cursor / fps:.1f} s | rewizja {p['revision']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]), int(a[1]), a[2] if len(a) > 2 else None, int(a[3]) if len(a) > 3 else 8876)
