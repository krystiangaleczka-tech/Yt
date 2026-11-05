"""Wgrywa ujęcia jednego dnia wariantu A (render_dNN.py) do ujęć Studio i na oś montażu, bez eksportu filmu.

uruchom (Studio musi działać):  python3 studio_dzien.py <dzień> <id projektu> [port] [tylko=3,6,10]
- ujęcia Studio dnia to te z legacy.flow_section_id == seq_dNN, w kolejności osi; ich liczba musi się zgadzać z renderem;
- każdy klip pokrywa całą długość ujęcia na osi (klatki renderu zaokrąglone w górę);
- ujęcie przechodzi z „Prompt AI” na „upload”; prompt zostaje w ujęciu.
"""
import importlib
import json
import math
import mimetypes
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAY, PID = int(sys.argv[1]), sys.argv[2]
ARGS = [a for a in sys.argv[3:] if not a.startswith("tylko=")]
ONLY = {int(x) for a in sys.argv[3:] if a.startswith("tylko=") for x in a[6:].split(",")}
API = f"http://127.0.0.1:{ARGS[0] if ARGS else 8876}/api"
H = {"Content-Type": "application/json", "X-Docos-Request": "1"}
mod = importlib.import_module(f"render_d{DAY:02d}")
import render as R  # noqa: E402


def call(path, body=None, method=None):
    req = urllib.request.Request(API + path, method=method or ("POST" if body is not None else "GET"), headers=H,
                                 data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def upload(path, name):
    b = uuid.uuid4().hex
    head = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(name)[0] or 'video/mp4'}\r\n\r\n").encode()
    req = urllib.request.Request(API + f"/projects/{PID}/media", method="POST",
                                 data=head + path.read_bytes() + f"\r\n--{b}--\r\n".encode(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}", "X-Docos-Request": "1"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["asset"]["id"]


p = call(f"/projects/{PID}")
fps = p["sequence"]["fps_num"] / p["sequence"]["fps_den"]
shots = sorted((s for s in p["scenes"] if s["legacy"].get("flow_section_id") == f"seq_d{DAY:02d}"), key=lambda s: s["start"])
assert len(shots) == len(mod.SCENES), f"Studio ma {len(shots)} ujęć dnia {DAY}, render {len(mod.SCENES)}"
tmp = Path(tempfile.mkdtemp())
for n, (scene, (a, b, *_)) in enumerate(zip(shots, mod.SCENES), 1):
    if ONLY and n not in ONLY:
        continue
    clip = tmp / f"d{DAY:02d}_{n:02d}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{R.W}x{R.H}", "-r", str(R.FPS), "-i", "-", "-c:v", "libx264", "-crf", "23",
                             "-pix_fmt", "yuv420p", str(clip)], stdin=subprocess.PIPE)
    count = math.ceil(scene["duration"] / fps * R.FPS - 1e-9)
    for f in range(count):
        proc.stdin.write(mod.frame(min(a + f / R.FPS, b - 1e-3)).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit(f"ffmpeg: {clip}")
    scene["asset_id"] = upload(clip, f"d{DAY:02d}_{n:02d} {scene['title'][:60]}.mp4")
    scene["mode"], scene["animation"] = "upload", "static"
    print(f"{n:02d}/{len(shots)} {scene['title'][:70]}", flush=True)
shutil.rmtree(tmp)  # kopie są już w mediach Studio; dysk jest ciasny
p = call(f"/projects/{PID}")  # wgrane materiały podbiły rewizję
shots = [s for n, s in enumerate(shots, 1) if not ONLY or n in ONLY]
by_id = {s["id"]: s for s in shots}
scenes = [by_id.get(s["id"], s) for s in p["scenes"]]
p = call(f"/projects/{PID}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")
on_axis = {c.get("scene_id"): c for c in p["sequence"]["clips"] if c["track_id"] == "v1"}
ops = [{"type": "update_clip", "clip_id": on_axis[s["id"]]["id"], "changes": {"asset_id": s["asset_id"]}}
       for s in shots if s["id"] in on_axis]  # poprawione ujęcie: nowy materiał także na osi
if ops:
    p = call(f"/projects/{PID}/edits", {"expected_revision": p["revision"], "operations": ops})
for s in shots:
    if s["id"] not in on_axis:
        p = call(f"/projects/{PID}/scenes/{s['id']}/to-timeline", {"expected_revision": p["revision"]})
mine = [s for s in p["scenes"] if s["id"] in by_id]
print(f"dzień {DAY}: z materiałem {sum(bool(s['asset_id']) for s in mine)}/{len(mine)} | klipów na osi {len(p['sequence']['clips'])} "
      f"| rewizja {p['revision']}")
call(f"/projects/{PID}/flow/log", {"entry": {
    "who": "studio_dzien.py", "unit": DAY, "kind": "wgranie",
    "summary": f"Materiał dnia {DAY} wgrany: {sum(bool(s['asset_id']) for s in mine)}/{len(mine)} ujęć"
               + (f" (tylko {sorted(ONLY)})" if ONLY else ""),
    "details": f"Rysunek: output/zombie-psychiatryk/render_d{DAY:02d}.py; rewizja {p['revision']}.",
    "files": [f"output/zombie-psychiatryk/render_d{DAY:02d}.py"]}})
