"""Aktualizuje projekt Studio „Oddział C · Do świtu (EN 1440p, PC)”: nowy obraz ujęć dni i dźwięk z planem miksu.

uruchom (Studio musi działać; najpierw efekty_dni.py i muzyka_dni.py):
  python -I studio_aktualizuj.py <id projektu> [--obraz] [--dzwiek] [-p 6] [--dni 3,5]
--obraz   rysuje od nowa ujęcia dni (720p) i podmienia materiał scen i klipów na osi (długości bez zmian);
--czasy   nowe długości ujęć (en_film.timing) po renderze dni (film_en.py obraz --res 720 → build/en-720):
          obraz ujęć z tego renderu, klipy Obrazu i Lektora przesunięte na nowe miejsca (razem z --dzwiek);
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
    if ARGS.czasy:
        p = czasy(api, pid, only, starts)
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


def _cut(job):
    """Klip 720p ujęcia wycięty z renderu dnia (--wideo-dni), z zapasem na końcu jak studio_pc.cut."""
    src, a_unit, dur, out = job
    if out.exists() and out.stat().st_size > 0:
        return out
    import subprocess
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a_unit:.4f}", "-i", str(src), "-t", f"{dur:.4f}",
                    "-vf", "scale=1280:720:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.25", "-an",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", "24", str(out)],
                   check=True)
    return out


def czasy(api, pid, only, starts):
    """Nowe długości ujęć (en_film.timing: kwestia EN z oddechem przed i pauzą po) w Studio: obraz ujęć wycięty
    z nowego renderu dni, klipy Obrazu przesunięte i z nową długością (ujęcia idą za nimi), kwestie na ścieżce Lektor
    przesunięte do nowego startu kwestii, napis ujęcia z kwestie_en. Zimne otwarcie bez zmian."""
    from concurrent.futures import ThreadPoolExecutor
    wideo = Path(ARGS.wideo_dni)
    out_dir = HERE / "build" / "studio_klipy_v3"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [s for s in SP.shots() if s[0] in only]
    jobs, meta = [], []
    for unit, i, a, b, r, txt, vs, vl in rows:
        f0, f1 = round(a * FPS), round(b * FPS)
        out = out_dir / f"d{unit:02d}_{i:02d}.mp4"
        jobs.append((wideo / f"v{unit:02d}.mp4", a - starts[unit], (f1 - f0) / FPS + 0.05, out))
        meta.append((unit, i, f0, f1 - f0, txt, vs, out))
    print(f"czasy: wycinam {len(jobs)} ujęć z {wideo}…", flush=True)
    with ThreadPoolExecutor(ARGS.p) as ex:
        for n, _ in enumerate(ex.map(_cut, jobs), 1):
            if n % 100 == 0:
                print(f"  wycięte {n}/{len(jobs)}", flush=True)
    p = api.call(f"/projects/{pid}")
    scenes = {s["id"]: s for s in p["scenes"]}
    clips = {(c["track_id"], c.get("scene_id")): c for c in p["sequence"]["clips"] if c.get("scene_id")}
    ops, new_asset, narr = [], {}, {}
    for n, (unit, i, f0, fd, txt, vs, out) in enumerate(meta, 1):
        sid = f"scene_d{unit:02d}_{i:02d}"
        aid = api.upload(pid, out, f"d{unit:02d}_{i:02d} v3 {scenes[sid]['title'][:50]}.mp4")
        new_asset[sid], narr[sid] = aid, txt or ""
        ops.append({"type": "update_clip", "clip_id": clips[("v1", sid)]["id"],
                    "changes": {"asset_id": aid, "start": f0, "duration": fd}})
        if ("a1", sid) in clips:
            ops.append({"type": "update_clip", "clip_id": clips[("a1", sid)]["id"], "changes": {"start": f0 + round(vs * FPS)}})
        if n % 100 == 0:
            print(f"  wgrane {n}/{len(meta)}", flush=True)
    p = api.call(f"/projects/{pid}")
    for k in range(0, len(ops), 200):  # najpierw oś montażu (nowy materiał razem z nową długością), potem ujęcia
        p = api.call(f"/projects/{pid}/edits", {"expected_revision": p["revision"], "operations": ops[k:k + 200]})
    sc = []
    for s in p["scenes"]:
        if s["id"] in new_asset:
            s = {**s, "asset_id": new_asset[s["id"]], "narration": narr[s["id"]]}
            if s.get("sentences") and narr[s["id"]]:
                s["sentences"] = [{**s["sentences"][0], "text": narr[s["id"]], "spoken_text": narr[s["id"]]}] + s["sentences"][1:]
        sc.append(s)
    p = api.call(f"/projects/{pid}", {"expected_revision": p["revision"], "changes": {"scenes": sc}}, "PATCH")
    total = max(c["start"] + c["duration"] for c in p["sequence"]["clips"] if c["track_id"] == "v1")
    print(f"czasy: przesunięto {len(ops)} klipów; film trwa {total / FPS / 60:.2f} min", flush=True)
    try:
        api.call(f"/projects/{pid}/flow/log", {"entry": {
            "who": "studio_aktualizuj.py", "kind": "rytm",
            "summary": "Długości ujęć z nagrań EN: oddech przed kwestią ≥ 0,5 s, pauza po 0,6–1,2 s; obraz z nowego renderu dni",
            "details": "Przegląd 13.11.2026 (reżyser: ujęcia kończą się zaraz po kwestii albo ucinają ją w połowie): "
                       "124 z 287 kwestii kończyło się 0,25 s przed cięciem, 27 zaczynało bez oddechu, d01_18 wychodziła "
                       "za cięcie. en_film.timing wydłuża ujęcie z kwestią, ujęć bez słów nie skraca. W tym samym renderze "
                       "poprawki kadrów z przeglądu (framugi d01_12, d14_12; biurko d01_02, d02_16; stół d22_02, d26_01, "
                       "d29_08; słuchawka w dłoni; drzwi izolatki d16_16; okno łącznika d13_12; d10_01, d10_14, d15_08, "
                       "d23_08, d30_16; napis d30_10).",
            "files": ["output/zombie-psychiatryk/en_film.py", "output/zombie-psychiatryk/dzien_base.py",
                      "output/zombie-psychiatryk/render_d01.py", "output/zombie-psychiatryk/kit_a.py"]}})
    except SystemExit as e:
        print("dziennik:", e)
    return p


def _unit_of(title):
    m = re.search(r"(?:dzień |· d)(\d+)", title)
    return int(m.group(1)) if m else -1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("projekt")
    ap.add_argument("--port", type=int, default=8876)
    ap.add_argument("--obraz", action="store_true")
    ap.add_argument("--dzwiek", action="store_true")
    ap.add_argument("--czasy", action="store_true", help="nowe długości ujęć: obraz z --wideo-dni, oś i lektor przesunięte")
    ap.add_argument("--wideo-dni", default=str(HERE / "build" / "en-720"), help="render dni (film_en.py obraz --res 720)")
    ap.add_argument("--dni", default="")
    ap.add_argument("-p", type=int, default=6)
    ARGS = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    main()
