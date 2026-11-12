"""Aktualizuje projekt Studio „Oddział C · Do świtu (EN 1440p, PC)”: nowy obraz ujęć dni i dźwięk z planem miksu.

uruchom (Studio musi działać; najpierw efekty_dni.py i muzyka_dni.py):
  python -I studio_aktualizuj.py <id projektu> [--obraz] [--dzwiek] [-p 6] [--dni 3,5]
--obraz   rysuje od nowa ujęcia dni (720p) i podmienia materiał scen i klipów na osi (długości bez zmian);
--dzwiek  usuwa stare „Efekty · dzień N”, zakłada ścieżkę a4 „Tło” i kładzie:
            a4 Tło      — klip na scenę rozpiski (tło miejsca, poziom z planu miksu w tytule),
            a3 Efekty   — klip na ujęcie ze zdarzeniami (każde zdarzenie: skala i dB w tytule),
            a2 Muzyka   — klip na frazę muzyki (nastrój, napięcie, dB w tytule);
          opis ujęcia dostaje wiersz „Dźwięk (plan miksu): …”, a legacy.miks — liczby. Głośność klipu (volume)
          zostaje 1 — poziom jest w pliku; reżyser poprawia ją w Montażu gałką klipu.
"""
import argparse
import importlib
import json
import math
import os
import re
import sys
import wave
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
os.environ["FILM_LANG"] = "en"
os.environ.setdefault("FILM_RES", "720")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "docs/filmy/oddzial-c/ujecia"))
import studio_pc as SP  # noqa: E402

FPS, SR = 30, 44100
KLIPY = HERE / "build" / "studio_klipy_v2"
KAWALKI = HERE / "build" / "studio_dzwiek"


def read_wav(p):
    with wave.open(str(p)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768


def write_wav(p, x):
    with wave.open(str(p), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def piece(x, t_day, f0, f1):
    """Kawałek dźwięku dnia dokładnie na klatkach osi [f0, f1) — sąsiednie kawałki stykają się bez przerwy."""
    i0, i1 = int(round((f0 / FPS - t_day) * SR)), int(round((f1 / FPS - t_day) * SR))
    y = x[max(0, i0):max(0, i1)]
    return np.pad(y, (0, max(0, (i1 - i0) - len(y))))


def main():
    api = SP.Api(ARGS.port)
    SP.ARGS = argparse.Namespace(wideo=str(HERE / "build" / "en-1440-przed-rigiem"))
    pid = ARGS.projekt
    only = {int(x) for x in ARGS.dni.split(",")} if ARGS.dni else set(range(1, 31))
    starts = SP.unit_start()
    p = api.call(f"/projects/{pid}")
    scenes = {s["id"]: s for s in p["scenes"]}
    if ARGS.obraz:
        KLIPY.mkdir(parents=True, exist_ok=True)
        jobs = []
        for s in p["scenes"]:
            u, i = s["legacy"].get("jednostka"), s["legacy"].get("ujecie")
            if u in only:
                jobs.append((u, i, s["duration"] / FPS + 0.05, KLIPY / f"d{u:02d}_{i:02d}.mp4"))
        print(f"rysuję {len(jobs)} ujęć w 720p…", flush=True)
        with ProcessPoolExecutor(ARGS.p) as ex:
            for n, _ in enumerate(ex.map(SP.render_shot, jobs, chunksize=4), 1):
                if n % 50 == 0:
                    print(f"  narysowane {n}/{len(jobs)}", flush=True)
        new_asset = {}
        for n, (u, i, _, out) in enumerate(jobs, 1):
            sid = f"scene_d{u:02d}_{i:02d}"
            new_asset[sid] = api.upload(pid, out, f"d{u:02d}_{i:02d} v2 {scenes[sid]['title'][:50]}.mp4")
            if n % 100 == 0:
                print(f"  wgrane {n}/{len(jobs)}", flush=True)
        p = api.call(f"/projects/{pid}")
        ops = [{"type": "update_clip", "clip_id": c["id"], "changes": {"asset_id": new_asset[c["scene_id"]]}}
               for c in p["sequence"]["clips"] if c["track_id"] == "v1" and c.get("scene_id") in new_asset]
        for k in range(0, len(ops), 200):  # najpierw oś montażu, potem ujęcia (WYTYCZNE 4)
            p = api.call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[k:k + 200]})
        sc = [{**s, "asset_id": new_asset.get(s["id"], s["asset_id"])} for s in p["scenes"]]
        p = api.call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": sc}}, "PATCH")
        print(f"obraz: podmieniono {len(ops)} klipów", flush=True)
    if ARGS.dzwiek:
        KAWALKI.mkdir(parents=True, exist_ok=True)
        p = api.call(f"/projects/{pid}")
        ops = [{"type": "remove_clip", "clip_id": c["id"]} for c in p["sequence"]["clips"]
               if (c["track_id"] == "a3" and c["title"].startswith("Efekty · ") and _unit_of(c["title"]) in only)
               or (c["track_id"] in ("a2", "a4") and _unit_of(c["title"]) in only)]
        if not any(t["id"] == "a4" for t in p["sequence"]["tracks"]):
            ops.insert(0, {"type": "add_track", "track": {"id": "a4", "name": "Tło", "kind": "audio", "role": "effects"}})
        for k in range(0, len(ops), 200):
            p = api.call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[k:k + 200]})
        clips, desc_lines, miks_of = [], {}, {}
        import dzien_base as B
        for day in sorted(only):
            t_day = starts[day]
            m = importlib.import_module(f"render_d{day:02d}")
            rows = B.rows(day)
            E = json.loads((HERE / "build" / "efekty" / f"e{day:02d}.json").read_text(encoding="utf-8"))
            M = json.loads((HERE / "build" / "muzyka" / f"m{day:02d}.json").read_text(encoding="utf-8"))
            tlo = read_wav(HERE / "build" / "efekty" / f"e{day:02d}_tlo_studio.wav")
            zd = read_wav(HERE / "build" / "efekty" / f"e{day:02d}_zdarzenia_studio.wav")
            fr = [(round((t_day + sc[0]) * FPS), round((t_day + sc[1]) * FPS)) for sc in m.SCENES]
            shots = E["ujecia"]
            import efekty_dni as EF
            # a4 Tło: scena rozpiski
            for stitle, idx in EF.scenes_of(day):
                f0, f1 = fr[idx[0]][0], fr[idx[-1]][1]
                places = sorted({shots[i]["miejsce"] for i in idx})
                dbs = [shots[i]["tlo_db"] for i in idx]
                f = KAWALKI / f"tlo_d{day:02d}_{idx[0]:02d}.wav"
                write_wav(f, piece(tlo, t_day, f0, f1))
                clips.append(("a4", f, f0, f1 - f0, f"Tło · d{day:02d} · {stitle} · {'/'.join(places)} · {min(dbs):.0f}…{max(dbs):.0f} dB"))
            # a3 Efekty: od ujęcia ze zdarzeniami do następnego ujęcia ze zdarzeniami (ogony nie giną)
            starts_ev = [i for i, e in enumerate(shots) if e["zdarzenia"]] + [len(shots)]
            for a, b in zip(starts_ev, starts_ev[1:]):
                e = shots[a]
                f0, f1 = fr[a][0], fr[b - 1][1]
                names = ", ".join(f"{z['dzwiek']} ({z['skala']} {z['db']:.0f} dB)" for z in e["zdarzenia"])[:150]
                f = KAWALKI / f"ef_d{day:02d}_{a:02d}.wav"
                write_wav(f, piece(zd, t_day, f0, f1))
                clips.append(("a3", f, f0, f1 - f0, f"Efekty · d{day:02d}_{a:02d} · napięcie {e['napiecie']:.0f} · {e['tempo']} · {names}"))
            # a2 Muzyka: frazy
            for c in M["sceny"]:
                if c["nastroj"] == "brak" or "plik" not in c:
                    continue
                f = HERE / "build" / "muzyka" / "cue" / c["plik"]
                f0 = round((t_day + c["start"]) * FPS)
                dur = max(1, math.ceil(len(read_wav(f)) / SR * FPS) - 1)
                clips.append(("a2", f, f0, dur, f"Muzyka · d{day:02d} · {c['scena'][:60]} · {c['nastroj']} · napięcie {c['napiecie']:.0f} · {c['db']:.0f} dB"))
            mus = {}
            for c in M["sceny"]:
                for i in range(c["ujecia"][0], c["ujecia"][1] + 1) if c["ujecia"] else []:
                    mus[i] = c["nastroj"] + (f" {c['db']:.0f} dB" if "db" in c else "")
            for i, e in enumerate(shots):
                zz = "; ".join(f"{z['dzwiek']} {z['skala']} {z['db']:.0f} dB" for z in e["zdarzenia"]) or "—"
                desc_lines[f"scene_d{day:02d}_{i:02d}"] = (f"Dźwięk (plan miksu): napięcie {e['napiecie']:.1f}/10 · tempo {e['tempo']} · "
                                                           f"tło {e['miejsce']} {e['tlo_db']:.0f} dB · zdarzenia: {zz} · "
                                                           f"muzyka: {mus.get(i, 'brak')}")
                miks_of[f"scene_d{day:02d}_{i:02d}"] = {**e, "muzyka": mus.get(i, "brak")}
        print(f"dźwięk: {len(clips)} klipów do wgrania", flush=True)
        adds = []
        for n, (track, f, f0, dur, title) in enumerate(clips, 1):
            aid = api.upload(pid, f, f"{title[:80]}.wav")
            adds.append({"type": "add_clip", "clip": {"track_id": track, "asset_id": aid, "title": title[:200], "start": f0, "duration": dur}})
            if n % 100 == 0:
                print(f"  wgrane {n}/{len(clips)}", flush=True)
        p = api.call(f"/projects/{pid}")
        for k in range(0, len(adds), 200):
            p = api.call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": adds[k:k + 200]})
        sc = []
        for s in p["scenes"]:
            if s["id"] in desc_lines:
                d = re.sub(r"\nDźwięk \(plan miksu\):.*$", "", s["description"], flags=re.S)
                d = (d + "\n" + desc_lines[s["id"]])[:3000]
                s = {**s, "description": d, "legacy": {**s["legacy"], "miks": miks_of[s["id"]]}}
            sc.append(s)
        p = api.call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": sc}}, "PATCH")
        print(f"dźwięk: klipów na osi {len(p['sequence']['clips'])}", flush=True)
        try:
            api.call(f"/projects/{pid}/flow/log", {"entry": {
                "who": "studio_aktualizuj.py", "kind": "dźwięk",
                "summary": "Plan miksu: tło na scenę (a4), efekty na ujęcie (a3), muzyka na frazę (a2); bez buczeń sieciowych",
                "details": "dB = skala (małe −34 / średnie −27 / duże −19) + 0,8 × (napięcie − 5) + tempo (szybkie +1,5 / wolne −1); "
                           "tło wg miejsca + 0,5 × (napięcie − 5); pod kwestiami efekty −6 dB, muzyka −8 dB, tło −4 dB. "
                           "Liczby w legacy.miks ujęć i w tytułach klipów.",
                "files": ["output/zombie-psychiatryk/efekty_dni.py", "output/zombie-psychiatryk/muzyka_dni.py"]}})
        except SystemExit as e:
            print("dziennik:", e)


def _unit_of(title):
    m = re.search(r"(?:dzień |· d)(\d+)", title)
    return int(m.group(1)) if m else -1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("projekt")
    ap.add_argument("--port", type=int, default=8876)
    ap.add_argument("--obraz", action="store_true")
    ap.add_argument("--dzwiek", action="store_true")
    ap.add_argument("--dni", default="")
    ap.add_argument("-p", type=int, default=6)
    ARGS = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    main()
