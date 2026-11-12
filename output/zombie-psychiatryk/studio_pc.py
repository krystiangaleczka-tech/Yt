"""Wgrywa gotowy film „Oddział C — Do świtu” (wersja angielska 1440p z PC) do DocOS Studio: ujęcie po ujęciu.

uruchom (Studio musi działać, ffmpeg w PATH, venv z numpy/scipy):
  python -I studio_pc.py [--port 8876] [--wideo build/en-1440] [--projekt prj_…]
- bez --projekt zakłada nowy projekt „Oddział C · Do świtu (EN 1440p, PC)”; z --projekt dokłada do istniejącego
  tylko to, czego brakuje (ujęcia o tych samych id są pomijane);
- zimne otwarcie (jednostka 0, 14 ujęć z rozpiski dnia 0) + dni 1–30: każde ujęcie to scena Studio z własnym klipem
  (720p, wycięty z renderu dnia, z zapasem 0,2 s na końcu), tytułem z opisu, kwestią EN w narracji i opisem kadru;
  ujęcia z rigiem (rig_dni.py) mają w opisie wiersz „Rig: …”, żeby reżyser wiedział, gdzie szukać nowej gry;
- ścieżka Lektor (a1): kwestie EN ujęć (radio/megafon z tym samym filtrem co w filmie);
- ścieżka Efekty (a3): „Efekty · dzień N” z efekty_dni.py (wersja studio: −8 dB pod kwestiami); zimne otwarcie: jego
  gotowy dźwięk razem z lektorem.
Bez eksportu: film ogląda się w Studio (Ujęcia / Montaż). Kopie klipów leżą w build/studio_klipy (można skasować).
"""
import argparse
import importlib
import json
import math
import mimetypes
import os
import re
import subprocess
import sys
import urllib.request
import uuid
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ["FILM_LANG"] = "en"
os.environ.setdefault("FILM_RES", "720")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
FPS_IN, FPS = 24, 30
SR = 44100
KADR = {"PO": "plan ogólny", "PP": "plan pełny", "PŚ": "plan średni", "NR": "przez ramię", "Z": "zbliżenie",
        "WZ": "wielkie zbliżenie", "D": "detal", "POV": "punkt widzenia", "TYT": "karta"}
RUCH = {"stat": "statyczna", "naj": "najazd", "odj": "odjazd", "pan": "panorama", "jaz": "jazda", "ręka": "z ręki",
        "drg": "drgania", "szarp": "szarpnięcie"}
TITLE = "Oddział C · Do świtu (EN 1440p, PC)"


class Api:
    def __init__(self, port):
        self.base = f"http://127.0.0.1:{port}/api"

    def call(self, path, body=None, method=None):
        req = urllib.request.Request(self.base + path, method=method or ("POST" if body is not None else "GET"),
                                     headers={"Content-Type": "application/json", "X-Docos-Request": "1"},
                                     data=None if body is None else json.dumps(body).encode())
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit(f"{path}: {e.code} {e.read().decode('utf-8', 'replace')[:600]}")

    def upload(self, pid, path, name):
        b = uuid.uuid4().hex
        head = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
                f"Content-Type: {mimetypes.guess_type(name)[0] or 'application/octet-stream'}\r\n\r\n").encode()
        req = urllib.request.Request(self.base + f"/projects/{pid}/media", method="POST",
                                     data=head + Path(path).read_bytes() + f"\r\n--{b}--\r\n".encode(),
                                     headers={"Content-Type": f"multipart/form-data; boundary={b}", "X-Docos-Request": "1"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)["asset"]["id"]


def title_of(desc):
    parts = [x.strip() for x in re.split(r"[:;—]", desc) if x.strip()]
    head = parts[0] if parts else desc
    if len(head) < 25 and len(parts) > 1:
        head += ": " + parts[1]
    return head if len(head) <= 70 else head[:67].rsplit(" ", 1)[0] + "…"


def wav_len(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def shots():
    """Wszystkie ujęcia filmu w kolejności: (jednostka, nr, start s, koniec s, wiersz rozpiski, napis, vs, vl)."""
    import dzien_base as B
    import en_film
    from a_dane1 import DAYS as D1
    out, t0 = [], 0.0
    vid = Path(ARGS.wideo)
    n0 = json.loads((vid / "v00.ok").read_text())["frames"]
    rows0 = [s for _, _, beats in D1[0][2] for _, sh in beats for s in sh]
    total0 = sum(r[2] for r in rows0)
    k = 0.0
    for i, r in enumerate(rows0):  # zimne otwarcie: czasy z rozpiski dnia 0, przeskalowane do długości renderu
        a, b = k * (n0 / FPS_IN) / total0, (k + r[2]) * (n0 / FPS_IN) / total0
        out.append((0, i, a, b, r, "", 0.0, 0.0))
        k += r[2]
    t0 = n0 / FPS_IN
    for d in range(1, 31):
        m = importlib.import_module(f"render_d{d:02d}")
        rows = B.rows(d)
        for i, (sc, r) in enumerate(zip(m.SCENES, rows)):
            if len(sc) == 4:
                a, b, _, txt = sc
                vs, vl = m.VWIN[i]
                vl = max(0.0, vl - 0.35) if txt else 0.0
            else:
                a, b, _, txt, vs, vl = sc
            out.append((d, i, t0 + a, t0 + b, r, txt, vs, vl))
        t0 += round(m.DUR * FPS_IN) / FPS_IN
    return out


def unit_start():
    """Początek każdej jednostki w sekundach filmu."""
    vid = Path(ARGS.wideo)
    starts, t = {}, 0.0
    starts[0] = 0.0
    t = json.loads((vid / "v00.ok").read_text())["frames"] / FPS_IN
    for d in range(1, 31):
        starts[d] = t
        m = importlib.import_module(f"render_d{d:02d}")
        t += round(m.DUR * FPS_IN) / FPS_IN
    return starts


def cut(job):
    unit, i, a_unit, dur, out = job
    if out.exists() and out.stat().st_size > 0:
        return out
    src = Path(ARGS.wideo) / f"v{unit:02d}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a_unit:.4f}", "-i", str(src), "-t", f"{dur:.4f}",
                    "-vf", "scale=1280:720:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.25", "-an",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS_IN), str(out)],
                   check=True)
    return out


def changed(unit, i):
    """Ujęcie, którego obraz zmienił się względem starego renderu: ma rig albo kurz w świetle (piwnica, apteka)."""
    if unit == 0:
        return False
    import dzien_base as B
    import rig_dni
    m = importlib.import_module(f"render_d{unit:02d}")
    return i in rig_dni.RIG.get(unit, {}) or m.LOOK[i] in (B.BASE, B.CELL)


def render_shot(job):
    """Klip 720p ujęcia narysowany od nowa kodem (rig, kurz) — bez renderu całego dnia w 1440p."""
    unit, i, dur, out = job
    if out.exists() and out.stat().st_size > 0:
        return out
    m = importlib.import_module(f"render_d{unit:02d}")
    a, b = m.SCENES[i][0], m.SCENES[i][1]
    import render as R
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.OW}x{R.OH}",
                             "-r", str(FPS_IN), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                             "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    for k in range(math.ceil((dur + 0.25) * FPS_IN)):  # zapas na końcu: ostatnia klatka ujęcia stoi
        proc.stdin.write(m.frame(min(a + k / FPS_IN, b - 1e-3)).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg {out}")
    return out


def shaped_voice(day, i, sound, tmp):
    """Kwestia z tym samym filtrem radia / megafonu co w filmie (film_en.shape)."""
    import en_film
    import film_en
    import numpy as np
    f = en_film.voice_file(day, i)
    who, how = en_film.speaker(sound)
    if how not in ("radio", "megafon"):
        return f
    v = film_en.shape(film_en.read_wav(f), how) * 0.9
    out = tmp / f"d{day:02d}_{i:02d}_{how}.wav"
    film_en.write_wav(out, v)
    return out


def main():
    import rig_dni
    api = Api(ARGS.port)
    tmp = HERE / "build" / "studio_klipy"
    tmp.mkdir(parents=True, exist_ok=True)
    if ARGS.projekt:
        pid = ARGS.projekt
    else:
        found = [p for p in api.call("/projects") if p["title"] == ARGS.tytul]
        pid = found[0]["id"] if found else api.call("/projects", {"title": ARGS.tytul, "language": "en", "production_mode": "documentary"})["id"]
    p = api.call(f"/projects/{pid}")
    have = {s["id"] for s in p["scenes"]}
    all_shots = shots()
    starts = unit_start()
    only = {int(x) for x in ARGS.dni.split(",")} if ARGS.dni else None  # próba: tylko wybrane jednostki
    todo = [s for s in all_shots if f"scene_d{s[0]:02d}_{s[1]:02d}" not in have and (only is None or s[0] in only)]
    print(f"projekt {pid}: ujęć w filmie {len(all_shots)}, do wgrania {len(todo)}", flush=True)
    # klipy ujęć: start/długość w klatkach osi (30 kl./s), plik pokrywa całe ujęcie na osi
    jobs, rjobs, meta = [], [], []
    for unit, i, a, b, r, txt, vs, vl in todo:
        f0, f1 = round(a * FPS), round(b * FPS)
        dur = (f1 - f0) / FPS + 0.05
        out = tmp / f"d{unit:02d}_{i:02d}.mp4"
        if ARGS.rysuj and changed(unit, i):  # zmieniony obraz: rysujemy samo ujęcie w 720p
            rjobs.append((unit, i, dur, out))
        else:  # obraz bez zmian: wycinek z gotowego renderu dnia
            jobs.append((unit, i, a - starts[unit], dur, out))
        meta.append((unit, i, f0, f1 - f0, r, txt, vs, vl, out))
    print(f"  do narysowania (rig, kurz): {len(rjobs)}, do wycięcia z renderu: {len(jobs)}", flush=True)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(ARGS.p) as px, ThreadPoolExecutor(ARGS.j) as ex:
        rf = [px.submit(render_shot, j) for j in rjobs]
        for n, _ in enumerate(ex.map(cut, jobs), 1):
            if n % 50 == 0:
                print(f"  wycięte: {n}/{len(jobs)}", flush=True)
        for n, f_ in enumerate(rf, 1):
            f_.result()
            if n % 25 == 0:
                print(f"  narysowane: {n}/{len(rjobs)}", flush=True)
    import en_film
    scenes, clips = [], []
    for n, (unit, i, f0, fd, r, txt, vs, vl, out) in enumerate(meta, 1):
        kadr, ruch, sec, desc, sound = r
        sid = f"scene_d{unit:02d}_{i:02d}"
        aid = api.upload(pid, out, f"d{unit:02d}_{i:02d} {title_of(desc)[:60]}.mp4")
        rig = rig_dni.RIG.get(unit, {}).get(i) if unit else None
        rig_txt = "; ".join(f"{w}: {s}" for w, s in rig.items()) if rig else ""
        description = f"({KADR.get(kadr, kadr)} · {RUCH.get(ruch, ruch)}) {desc}"
        if sound and not txt:
            description += f"\nDźwięk: {sound}"
        if rig_txt:
            description += f"\nRig (gra aktorska): {rig_txt}"
        sc = {"id": sid, "title": ("Karta · " + desc) if kadr == "TYT" else title_of(desc), "narration": txt or "",
              "description": description[:3000], "start": f0, "duration": fd, "timing": "measured", "mode": "upload",
              "animation": "static", "asset_id": aid, "role": "reconstruction",
              "legacy": {"flow_section_id": "seq_d00" if unit == 0 else f"seq_d{unit:02d}", "jednostka": unit, "ujecie": i,
                         "rig": rig_txt, "zrodlo": f"output/zombie-psychiatryk/render_d{unit:02d}.py" if unit else "render.py, render2.py"}}
        clips.append({"track_id": "v1", "asset_id": aid, "scene_id": sid, "title": sc["title"][:120], "start": f0, "duration": fd})
        if unit and en_film.voice_file(unit, i).exists() and txt:
            vf = shaped_voice(unit, i, sound or "", tmp)
            vaid = api.upload(pid, vf, f"lektor d{unit:02d}_{i:02d}.wav")
            sc["voice_asset_id"] = vaid
            clips.append({"track_id": "a1", "asset_id": vaid, "scene_id": sid, "title": f"Lektor · {txt[:80]}",
                          "start": f0 + round(vs * FPS), "duration": max(1, math.ceil(wav_len(vf) * FPS))})
        scenes.append(sc)
        if n % 50 == 0:
            print(f"  wgrane: {n}/{len(meta)}", flush=True)
    # efekty: dzień po dniu (wersja studio), zimne otwarcie z gotowym dźwiękiem
    have_titles = {c["title"] for c in p["sequence"]["clips"] if c["track_id"] == "a3"}
    fxdir = HERE / "build" / "efekty"
    for unit in range(0, 31):
        if only is not None and unit not in only:
            continue
        title = "Zimne otwarcie · dźwięk z lektorem" if unit == 0 else f"Efekty · dzień {unit}"
        if title in have_titles:
            continue
        f = (Path(ARGS.wideo) / "a00.wav") if unit == 0 else fxdir / f"e{unit:02d}_studio.wav"
        if not f.exists():
            print("brak", f)
            continue
        aid = api.upload(pid, f, f"{title}.wav")
        clips.append({"track_id": "a3", "asset_id": aid, "title": title, "start": round(starts[unit] * FPS),
                      "duration": max(1, math.ceil(wav_len(f) * FPS))})
    p = api.call(f"/projects/{pid}")
    p = api.call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": p["scenes"] + scenes}}, "PATCH")
    ops = [{"type": "add_clip", "clip": c} for c in clips]
    for k in range(0, len(ops), 200):
        p = api.call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[k:k + 200]})
    print(f"gotowe: ujęć {len(p['scenes'])}, klipów na osi {len(p['sequence']['clips'])}, materiałów {len(p['assets'])}, "
          f"rewizja {p['revision']}", flush=True)
    rigged = sum(1 for s in scenes if s["legacy"]["rig"])
    try:
        api.call(f"/projects/{pid}/flow/log", {"entry": {
            "who": "studio_pc.py", "kind": "wgranie", "summary": f"Film EN 1440p z PC wgrany ujęciami: {len(scenes)} ujęć, "
            f"z czego {rigged} z nowym rigiem (gra aktorska), efekty dźwiękowe dni 1–30 na ścieżce Efekty",
            "details": "Rig: output/zombie-psychiatryk/rig_a.py + rig_dni.py; efekty: efekty_dni.py; render: film_en.py (NVENC).",
            "files": ["output/zombie-psychiatryk/rig_a.py", "output/zombie-psychiatryk/rig_dni.py",
                      "output/zombie-psychiatryk/efekty_dni.py", "output/zombie-psychiatryk/studio_pc.py"]}})
    except SystemExit as e:
        print("dziennik:", e)
    print(pid)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8876)
    ap.add_argument("--wideo", default=str(HERE / "build" / "en-1440"))
    ap.add_argument("--projekt", default="")
    ap.add_argument("-j", type=int, default=4)
    ap.add_argument("--dni", default="", help="np. 0,5 — tylko te jednostki (próba)")
    ap.add_argument("--rysuj", action="store_true", help="ujęcia z rigiem i kurzem rysuj od nowa w 720p, resztę wytnij z --wideo")
    ap.add_argument("-p", type=int, default=6, help="procesy rysujące ujęcia")
    ap.add_argument("--tytul", default=TITLE)
    ARGS = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    main()
