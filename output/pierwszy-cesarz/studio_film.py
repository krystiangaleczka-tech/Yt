"""Studio: plan filmu „Pierwszy cesarz”, księga świata i klipy ujęć — bez eksportu filmu.

  python3 studio_film.py plan                    — zakłada projekt (za pierwszym razem), wgrywa plan (akty, sceny, beaty, ujęcia),
                                                   Story Bible, księgę świata i warsztat; układa ujęcia; kontrola ciągłości
  python3 studio_film.py klipy [tylko=3,6,10]    — szkice 640 × 360 (12 kl./s) do zakładki Ujęcia i na oś montażu
  python3 studio_film.py klipy pelne [tylko=…]   — to samo w pełnej jakości (1280 × 720, 24 kl./s) — na końcu pracy
  python3 studio_film.py klipy katalog=<folder> [tylko=…] — wgrywa klipy wyrenderowane gdzie indziej (paczka na PC), bez renderu
  python3 studio_film.py dzwiek [lektor]         — muzyka i efekty (dzwiek/*.wav); z „lektor” także kwestie z lektor/*.wav
Studio musi działać (port 8876). Identyfikator projektu i wgrane klipy pamięta studio.json obok skryptu.
Ujęcia Studio są dopasowywane po `legacy.flow_director_shot_id`, więc uwagi i markery reżysera zostają przy ujęciach.
"""
import json
import math
import mimetypes
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "docs/filmy/pierwszy-cesarz/ujecia"))
import ksiega  # noqa: E402
from dane import AKTY, kwestia, ujecia  # noqa: E402

API = f"http://127.0.0.1:{os.environ.get('DOCOS_API_PORT', '8876')}/api"
HEAD = {"Content-Type": "application/json", "X-Docos-Request": "1"}
STATE = HERE / "studio.json"
TITLE = "Pierwszy cesarz — teatr papierowy"
KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "Z": "zbliżenie", "D": "detal", "TYT": "karta / napis"}
RUCH = {"stat": "statyczna", "naj": "najazd", "odj": "odjazd", "pan": "panorama", "jaz": "jazda za postacią", "szarp": "szarpnięcie kamery"}
TYPE = {"PO": "wide", "PP": "wide", "PŚ": "medium", "Z": "close-up", "D": "insert", "TYT": "insert"}
NAPIECIE = {1: 3, 2: 4, 3: 8, 4: 6, 5: 4, 6: 6, 7: 7, 8: 8}  # krzywa filmu: napięcie aktu 0–10


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"), headers=HEAD,
                                 data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Studio odrzuciło {method or 'POST'} {path}: {e.code} {e.read().decode()[:600]}")


def upload(pid, path, name):
    b = uuid.uuid4().hex
    head = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(name)[0] or 'video/mp4'}\r\n\r\n").encode()
    req = urllib.request.Request(API + f"/projects/{pid}/media", method="POST", data=head + path.read_bytes() + f"\r\n--{b}--\r\n".encode(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["asset"]["id"]


def state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"pid": "", "klipy": {}}


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n")


def tc(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def node(nid, title, description):
    return {"id": nid, "variants": [{"id": nid + "_v1", "title": title, "description": description}], "selected": nid + "_v1"}


def tytul(opis):
    head = opis.split(";")[0].split(":")[-1].strip() if len(opis.split(":")[0]) < 22 else opis.split(";")[0].split(":")[0].strip()
    head = head[0].upper() + head[1:]
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


def rozpiska():
    """Lista ujęć z miejscem w planie: akt, scena, beat, numer w beacie + dane ujęcia z dane.ujecia()."""
    flat, out = iter(ujecia()), []
    for n, _, _, sceny in AKTY:
        for si, (stitle, place, beaty) in enumerate(sceny, 1):
            for bi, (btitle, shots) in enumerate(beaty, 1):
                for k in range(1, len(shots) + 1):
                    _, nr, klucz, kadr, ruch, sec, opis, snd = next(flat)
                    out.append(dict(akt=n, nr=nr, scena=si, stitle=stitle, place=place, beat=bi, btitle=btitle, k=k, klucz=klucz, kadr=kadr,
                                    ruch=ruch, sec=sec, opis=opis, snd=snd, ref=f"d{n:02d}_{nr:02d}",
                                    oid=f"sc_d{n:02d}_{si}", bid=f"sc_d{n:02d}_{si}_b{bi}", sid=f"sc_d{n:02d}_{si}_b{bi}_s{k}"))
    return out


def plan():
    st = state()
    if not st["pid"]:
        p = call("/projects", {"title": TITLE, "language": "pl", "channel_id": "channel_f066137b388e4ed8", "production_mode": "animation_2d",
                               "film_format": "teatr papierowy, lektor w 3. osobie"})
        st["pid"] = p["id"]
        save_state(st)
        print("nowy projekt:", p["id"])
    pid = st["pid"]
    p = call(f"/projects/{pid}")
    rows = rozpiska()
    old = p["legacy"].get("production_flow") or {}
    flow = {"version": 1, "factual": True, "sourceIdeaId": old.get("sourceIdeaId", ""), "approved": old.get("approved", {}),
            "reviews": old.get("reviews", []), "log": old.get("log", []), "unitReviews": old.get("unitReviews", {}),
            "bible": ksiega.BIBLIA, "world": ksiega.SWIAT, "book": ksiega.WARSZTAT,
            "master": node("master", "Pierwszy cesarz", " ".join(a[2] for a in AKTY)),
            "acts": [], "sequences": [], "outlines": [], "scripts": {}, "director": {"mode": "manual", "plans": {}, "customPatterns": []}}
    t = 0.0
    for n, atitle, aopis, sceny in AKTY:
        act, seq = f"act_{n:02d}", f"seq_d{n:02d}"
        mine = [r for r in rows if r["akt"] == n]
        flow["acts"].append(node(act, f"Akt {n} · {atitle}", aopis))
        flow["sequences"].append({**node(seq, f"Akt {n} · {atitle}", " → ".join(s[0] for s in sceny) + "."), "actId": act,
                                  "seconds": round(sum(r["sec"] for r in mine), 1)})
        flow["scripts"][act] = "\n\n".join(kwestia(r["snd"]) for r in mine if kwestia(r["snd"]))
        for si, (stitle, place, beaty) in enumerate(sceny, 1):
            oid = f"sc_d{n:02d}_{si}"
            srows = [r for r in mine if r["scena"] == si]
            s0, nap = t, NAPIECIE[n]
            beats, shots = [], []
            for bi, (btitle, _) in enumerate(beaty, 1):
                brows = [r for r in srows if r["beat"] == bi]
                beats.append({"id": f"{oid}_b{bi}", "title": btitle, "goal": "; ".join(r["opis"] for r in brows)[:3900],
                              "tensionBefore": max(0, nap - 1), "tensionAfter": min(10, nap + (1 if bi == len(beaty) else 0)),
                              "viewerKnows": " ".join(kwestia(r["snd"]) for r in brows)[:1900], "characterKnows": "",
                              "soundCue": "; ".join(r["snd"] for r in brows if r["snd"] and not r["snd"].startswith("L:"))[:990],
                              "patternId": "exposition" if any(r["kadr"] == "TYT" for r in brows) else
                              ("chase" if any(r["ruch"] == "szarp" for r in brows) else "slow-burn")})
                for r in brows:
                    shots.append({"id": r["sid"], "beatId": r["bid"], "typeId": TYPE[r["kadr"]], "title": tytul(r["opis"]),
                                  "description": f"[{tc(t)}–{tc(t + r['sec'])}] ({KADR[r['kadr']]} · {RUCH[r['ruch']]}) {r['opis']}",
                                  "duration": r["sec"], "transition": "dip" if r["kadr"] == "TYT" else "cut", "sound": r["snd"]})
                    r["t0"], r["title"] = t, tytul(r["opis"])
                    t += r["sec"]
            flow["outlines"].append({**node(oid, stitle, f"{place}. Beaty: " + ", ".join(b[0] for b in beaty) + "."), "sectionId": seq,
                                     "seconds": round(t - s0, 1)})
            flow["director"]["plans"][oid] = {"outlineId": oid, "sourceSignature": "", "patternId": beats[0]["patternId"], "mode": "manual",
                                              "notes": f"Akt {n} · scena {si} · {tc(s0)}–{tc(t)} filmu. Rozpiska: "
                                                       "docs/filmy/pierwszy-cesarz/ujecia/dane.py", "beats": beats, "shots": shots}
    signed = subprocess.run(["node", "--experimental-strip-types", str(REPO / "output/zombie-psychiatryk/studio_signatures.mjs"),
                             str(REPO / "apps/studio/src/flowTypes.ts")], input=json.dumps(flow), capture_output=True, text=True, check=True).stdout
    p = call(f"/projects/{pid}/flow", {"expected_revision": p["revision"], "flow": json.loads(signed)}, "PUT")

    # ujęcia: istniejące zostają (uwagi, markery, materiał), zmienia się opis, kwestia i miejsce na osi
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    old = {s["id"]: s["duration"] for s in p["scenes"]}  # przed zmianami: dalej słowniki ujęć są zmieniane w miejscu
    by_shot = {s["legacy"].get("flow_director_shot_id"): s for s in p["scenes"]}
    scenes, cursor = [], 0
    for n, r in enumerate(rows, 1):
        frames = max(1, round(r["sec"] * fps))
        s = by_shot.get(r["sid"]) or {"mode": "search", "asset_id": None, "voice_asset_id": None, "variants": [], "fact_ids": [],
                                      "role": "illustration", "locked": False, "animation": "static", "timing": "estimated"}
        s.update(title=f"{r['stitle']} · {r['nr']:02d} · {r['title']}", narration=kwestia(r["snd"]), description=r["opis"],
                 director_notes=f"Kadr: {KADR[r['kadr']]} · {RUCH[r['ruch']]}. Beat: {r['btitle']}. Dźwięk: {r['snd']}"[:3000],
                 start=cursor, duration=frames, prompt=f"Rysowane kodem: output/pierwszy-cesarz, funkcja s_{r['klucz']} ({r['ref']}).",
                 motion_prompt=RUCH[r["ruch"]] if r["ruch"] != "stat" else "", search_query=r["title"],
                 legacy={**s.get("legacy", {}), "flow_act_id": f"act_{r['akt']:02d}", "flow_section_id": f"seq_d{r['akt']:02d}",
                         "flow_outline_id": r["oid"], "flow_director_shot_id": r["sid"], "flow_director_beat_id": r["bid"],
                         "flow_director_kind": TYPE[r["kadr"]], "klucz": r["klucz"]})
        scenes.append(s)
        cursor += frames
    # ujęcie zmieniło długość: stary materiał już nie pasuje — klip schodzi z osi, ujęcie czeka na nowy render
    # (najpierw oś, potem ujęcia, bo serwer odrzuca ujęcie dłuższe od swojego materiału)
    changed = {s["id"] for s in scenes if s.get("id") in old and old[s["id"]] != s["duration"]}
    gone = [{"type": "remove_clip", "clip_id": c["id"]} for c in p["sequence"]["clips"] if c.get("scene_id") in changed]
    for i in range(0, len(gone), 200):
        p = call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": gone[i:i + 200]})
    for s in scenes:
        if s.get("id") in changed:
            s.update(asset_id=None, mode="search")
    p = call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
    # klipy, które już są na osi, idą za swoimi ujęciami
    on_axis = {c.get("scene_id"): c for c in p["sequence"]["clips"] if c["track_id"] == "v1"}
    ops = [{"type": "move_clip", "clip_id": on_axis[s["id"]]["id"], "changes": {"start": s["start"]}} for s in p["scenes"]
           if s["id"] in on_axis and on_axis[s["id"]]["start"] != s["start"]]
    for i in range(0, len(ops), 200):
        p = call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})
    rep = call(f"/projects/{pid}/continuity/check", {})
    tot = rep["totals"]
    for i in rep["issues"]:
        if i["severity"] >= 2:
            print(f"  [{i['severity']}] {i.get('ref') or ('akt ' + str(i.get('unit')))} {i['rule']}: {i['message']}")
    call(f"/projects/{pid}/flow/log", {"entry": {
        "who": "studio_film.py", "kind": "tworzenie", "summary": f"Plan filmu wgrany z rozpiski: {len(AKTY)} aktów, {len(rows)} ujęć, {tc(t)}",
        "details": f"Kontrola ciągłości (waga 3 / 2 / 1): {tot.get('3', 0)} / {tot.get('2', 0)} / {tot.get('1', 0)}.",
        "files": ["docs/filmy/pierwszy-cesarz/ujecia/dane.py", "docs/filmy/pierwszy-cesarz/ujecia/ksiega.py"]}})
    print(f"projekt {pid} | {len(AKTY)} aktów, {len(rows)} ujęć, {tc(t)} | kontrola {tot.get('3', 0)}/{tot.get('2', 0)}/{tot.get('1', 0)}")
    return tot


def klipy(args):
    st = state()
    pid = st["pid"]
    pelne = "pelne" in args
    only = sorted({int(x) for a in args if a.startswith("tylko=") for x in a[6:].split(",")})
    rows = rozpiska()
    gotowe = next((Path(x[8:]) for x in args if x.startswith("katalog=")), None)  # klipy wyrenderowane gdzie indziej (PC)
    if gotowe:
        tmp, pelne = gotowe, True
    else:
        tmp = Path(tempfile.mkdtemp(prefix="cesarz-klipy-"))
        env = {**os.environ, "SZKIC": "0" if pelne else "1"}
        cmd = [sys.executable, str(HERE / "render.py"), "klipy"] + ([",".join(map(str, only))] if only else []) + [str(tmp)]
        subprocess.run(cmd, env=env, check=True)
    p = call(f"/projects/{pid}")
    by_shot = {s["legacy"].get("flow_director_shot_id"): s for s in p["scenes"]}
    done = []
    for n, r in enumerate(rows, 1):
        clip = tmp / f"{r['ref']}.mp4"
        if not clip.exists():
            continue
        if only and n not in only:
            continue
        asset = upload(pid, clip, f"{r['ref']} {r['klucz']}{'' if pelne else ' szkic'}.mp4")
        if not gotowe:
            clip.unlink()  # kopia jest już w mediach Studio; dysk jest ciasny
        st["klipy"][r["ref"]] = {"asset": asset, "tryb": "pelne" if pelne else "szkic"}
        by_shot[r["sid"]].update(asset_id=asset, mode="upload", animation="static")
        done.append(r["sid"])
    save_state(st)
    p = call(f"/projects/{pid}")  # wgrane materiały podbiły rewizję
    scenes = [{**s, **({"asset_id": by_shot[k]["asset_id"], "mode": "upload", "animation": "static"} if (k := s["legacy"].get(
        "flow_director_shot_id")) in done else {})} for s in p["scenes"]]
    p = call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
    on_axis = {c.get("scene_id"): c for c in p["sequence"]["clips"] if c["track_id"] == "v1"}
    mine = [s for s in p["scenes"] if s["legacy"].get("flow_director_shot_id") in done]
    ops = [{"type": "update_clip", "clip_id": on_axis[s["id"]]["id"], "changes": {"asset_id": s["asset_id"]}} for s in mine if s["id"] in on_axis]
    for i in range(0, len(ops), 200):
        p = call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})
    for s in mine:
        if s["id"] not in on_axis:
            p = call(f"/projects/{pid}/scenes/{s['id']}/to-timeline", {"expected_revision": p["revision"]})
    have = sum(bool(s["asset_id"]) for s in p["scenes"])
    call(f"/projects/{pid}/flow/log", {"entry": {
        "who": "studio_film.py", "kind": "wgranie",
        "summary": f"Ujęcia wgrane ({'pełna jakość' if pelne else 'szkic 640 × 360'}): {len(done)}" + (f" (tylko {only})" if only else ""),
        "details": f"Z materiałem {have}/{len(p['scenes'])} ujęć; klipów na osi {len(p['sequence']['clips'])}; rewizja {p['revision']}.",
        "files": ["output/pierwszy-cesarz/render.py", "output/pierwszy-cesarz/ujecia1.py", "output/pierwszy-cesarz/ujecia2.py"]}})
    print(f"wgrano {len(done)} ujęć | z materiałem {have}/{len(p['scenes'])} | klipów na osi {len(p['sequence']['clips'])} | rewizja {p['revision']}")


def dzwiek(lektor=False):
    """Lektor (ścieżka Lektor, klip na kwestię, od oddechu w ujęciu), muzyka i efekty (po jednym klipie na cały film)."""
    st = state()
    pid = st["pid"]
    p = call(f"/projects/{pid}")
    fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
    by_shot = {s["legacy"].get("flow_director_shot_id"): s for s in p["scenes"]}
    ops = [{"type": "remove_clip", "clip_id": c["id"]} for c in p["sequence"]["clips"]
           if c["track_id"] in (("a1", "a2", "a3") if lektor else ("a2", "a3"))]
    total = 0
    for r in rozpiska():
        sc = by_shot[r["sid"]]
        total = max(total, sc["start"] + sc["duration"])
        wav = HERE / "lektor" / f"{r['klucz']}.wav"
        if not lektor or not kwestia(r["snd"]) or not wav.exists():
            continue
        meta = json.loads(wav.with_suffix(".json").read_text())
        if meta["text"] != kwestia(r["snd"]):
            continue
        cached = st.setdefault("lektor", {}).get(r["klucz"])
        if not cached or cached["sha"] != _sha(wav):
            cached = {"asset": upload(pid, wav, f"lektor {r['ref']} {r['klucz']}.wav"), "sha": _sha(wav)}
            st["lektor"][r["klucz"]] = cached
            save_state(st)
        start = sc["start"] + round(0.6 * fps)
        ops.append({"type": "add_clip", "clip": {"track_id": "a1", "asset_id": cached["asset"], "scene_id": sc["id"],
                                                 "title": f"Lektor · {kwestia(r['snd'])[:80]}", "start": start,
                                                 "duration": max(1, math.ceil(meta["duration"] * fps))}})
    for track, name, vol in (("a2", "muzyka", 0.8), ("a3", "efekty", 1.0)):
        wav = HERE / "dzwiek" / f"{name}.wav"
        aid = upload(pid, wav, f"{name} — cały film.wav")
        with wave.open(str(wav)) as w:
            frames = min(total, math.floor(w.getnframes() / w.getframerate() * fps))
        ops.append({"type": "add_clip", "clip": {"track_id": track, "asset_id": aid, "title": f"{name.capitalize()} · cały film",
                                                 "start": 0, "duration": frames, "volume": vol}})
    p = call(f"/projects/{pid}")  # wgrane pliki podbiły rewizję
    for i in range(0, len(ops), 200):
        p = call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})
    n1 = sum(c["track_id"] == "a1" for c in p["sequence"]["clips"])
    call(f"/projects/{pid}/flow/log", {"entry": {
        "who": "studio_film.py", "kind": "wgranie", "summary": f"Dźwięk wgrany: muzyka i efekty na cały film" + (f", lektor {n1} kwestii" if lektor else " (lektor jeszcze nie nagrany)"),
        "details": "Lektor: klon głosu autora (Chatterbox, próbka bez pogłosu pilot/assets/ref_studio.wav, 3 podejścia na kwestię, "
                   "suche i z odbudowanym pasmem — Podręcznik → Lektor), output/pierwszy-cesarz/lektor.py. "
                   "Muzyka i efekty: synteza w numpy, output/pierwszy-cesarz/efekty.py (pod kwestiami ściszone).",
        "files": ["output/pierwszy-cesarz/lektor.py", "output/pierwszy-cesarz/efekty.py"]}})
    print(f"lektor: {n1} klipów | muzyka i efekty: po 1 klipie | rewizja {p['revision']}")


def _sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


if __name__ == "__main__":
    if sys.argv[1:2] == ["plan"]:
        plan()
    elif sys.argv[1:2] == ["dzwiek"]:
        dzwiek(lektor="lektor" in sys.argv[2:])
    elif sys.argv[1:2] == ["klipy"]:
        klipy(sys.argv[2:])
    else:
        sys.exit(__doc__)
