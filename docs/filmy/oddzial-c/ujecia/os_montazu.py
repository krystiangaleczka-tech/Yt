"""Układa ścieżkę obrazu (v1) na osi montażu jeden klip za drugim, w kolejności filmu, i wyrównuje start ujęć.

Kolejność: akty → sekwencje z planu filmu; w sekwencji ujęcia wg `flow_director_shot_id` (scena, beat, ujęcie),
a ujęcia bez planu reżyserskiego (zimne otwarcie) wg obecnej pozycji. Klipy dźwięku nie są ruszane (leżą tylko
pod zimnym otwarciem, które się nie przesuwa). Wywołuje to zamien_dzien.py po każdej podmianie dnia, bo podmiana
liczy pozycje z zapisów ujęć, a te mogą się rozjechać z osią.

  python3 docs/filmy/oddzial-c/ujecia/os_montazu.py <projekt> [port]
"""
import json
import re
import sys
import urllib.request

H = {"Content-Type": "application/json", "X-Docos-Request": "1"}


def _call(api, path, body=None, method=None):
    req = urllib.request.Request(api + path, method=method or ("POST" if body is not None else "GET"), headers=H,
                                 data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def uloz(pid, port=8876):
    api = f"http://127.0.0.1:{port}/api"
    p = _call(api, f"/projects/{pid}")
    flow = p["legacy"]["production_flow"]
    order = {}
    for act in flow["acts"]:
        for sec in (s for s in flow["sequences"] if s["actId"] == act["id"]):
            order[sec["id"]] = len(order)
    scenes = {s["id"]: s for s in p["scenes"]}
    v1 = [c for c in p["sequence"]["clips"] if c["track_id"] == "v1"]

    def key(c):
        s = scenes.get(c.get("scene_id"), {})
        leg = s.get("legacy", {})
        nums = tuple(int(x) for x in re.findall(r"\d+", leg.get("flow_director_shot_id", "")))
        return (order.get(leg.get("flow_section_id"), 10 ** 6), nums[1:] if nums else (), c["start"])

    cursor, ops, starts = 0, [], {}
    for c in sorted(v1, key=key):
        if c["start"] != cursor:
            ops.append({"type": "move_clip", "clip_id": c["id"], "changes": {"start": cursor}})
        starts[c.get("scene_id")] = (cursor, c["duration"])
        cursor += c["duration"]
    for i in range(0, len(ops), 200):  # serwer przyjmuje do 200 operacji w jednej edycji
        p = _call(api, f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})
    fixed = 0
    new_scenes = []
    for s in p["scenes"]:
        if s["id"] in starts and (s["start"], s["duration"]) != starts[s["id"]]:
            s = {**s, "start": starts[s["id"]][0], "duration": starts[s["id"]][1]}
            fixed += 1
        new_scenes.append(s)
    if fixed:
        p = _call(api, f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": new_scenes}}, "PATCH")
    return len(ops), fixed, cursor


if __name__ == "__main__":
    moved, fixed, end = uloz(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8876)
    print(f"oś: przesunięto {moved} klipów, wyrównano {fixed} ujęć, koniec obrazu {end / 30:.1f} s")
