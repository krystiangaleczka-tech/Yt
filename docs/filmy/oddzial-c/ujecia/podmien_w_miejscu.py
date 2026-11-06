"""Podmienia dzień wariantu A w Studio W MIEJSCU — po zmianie kwestii albo długości ujęć w rozpisce (a_dane*.py).

uruchom:  python3 docs/filmy/oddzial-c/ujecia/podmien_w_miejscu.py <dzień> <id projektu> [port] [render|wgraj]
- render  — rysuje klipy dnia z nowymi długościami do output/zombie-psychiatryk/podmiana/dNN/ i robi arkusz klatek
            zmienionych ujęć (podmiana/dNN-arkusz.png); nie dotyka Studio, więc kilka dni można rysować równolegle;
- wgraj   — (Studio musi działać) plan dnia + kontrola ciągłości, wgranie klipów, oś, ujęcia, dziennik; dni po kolei;
- bez trybu: oba kroki.

W odróżnieniu od zamien_dzien.py nic nie jest kasowane:
- ujęcia dnia zostają (te same id, prompt); zmieniają się materiał, kwestia, opis, notatka „Dźwięk:”, start i długość;
- klipy za dniem (obraz, efekty, wszystkie ścieżki) przesuwają się tak, żeby zaczynały się tuż za nowym końcem dnia —
  liczone od miejsca, w którym faktycznie stoją, więc ponowne uruchomienie niczego nie przesuwa drugi raz;
- Studio przesuwa ujęcie razem z jego klipem i nie przyjmie klipu dłuższego od materiału, dlatego kolejność to:
  nowy materiał → oś (klipy dnia: materiał, start, długość) → ujęcia (te same wartości, kwestie);
- plan reżyserski dnia robi zamien_dzien.py … tylko_plan; błąd wagi 3 w kontroli dnia zatrzymuje wgranie;
- liczba i kolejność ujęć dnia w Studio muszą się zgadzać z rozpiską (gdy dzień zmienia ujęcia — zamien_dzien.py).
Efekty dnia potem: output/zombie-psychiatryk/efekty_dni.py <dzień> i efekty_dni.py wgraj <projekt> <dzień>.
"""
import importlib
import json
import math
import mimetypes
import shutil
import subprocess
import sys
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RENDER = REPO / "output/zombie-psychiatryk"
sys.path.insert(0, str(HERE))
import prompty  # noqa: E402

MODES = {a for a in sys.argv[3:] if a in ("render", "wgraj")} or {"render", "wgraj"}
ARGS = [a for a in sys.argv[1:] if a not in ("render", "wgraj")]
DAY, PID = int(ARGS[0]), ARGS[1]
PORT = ARGS[2] if len(ARGS) > 2 else "8876"
API = f"http://127.0.0.1:{PORT}/api"
H = {"Content-Type": "application/json", "X-Docos-Request": "1"}
SID = f"seq_d{DAY:02d}"
OUT = RENDER / "podmiana" / f"d{DAY:02d}"
STUDIO_FPS = 30  # oś Studio: 30 kl./s (sprawdzane przy wgraniu)


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


def spoken_line(sound):
    return sound[2:].strip() if sound.startswith("L:") else ""


def check_axis(p):
    """Każde ujęcie ma jeden klip obrazu z tym samym startem i długością; obraz filmu bez dziur i nakładek."""
    scenes = {s["id"]: s for s in p["scenes"]}
    # luźny klip bez ujęcia w zimnym otwarciu (sc_04_s2, opisany w dzienniku 5.11) nie należy do ciągu ujęć
    v1 = sorted((c for c in p["sequence"]["clips"] if c["track_id"] == "v1" and c.get("scene_id") in scenes),
                key=lambda c: c["start"])
    errors = [f"klip {c['id']} ≠ ujęcie" for c in v1
              if (c["start"], c["duration"]) != (scenes[c["scene_id"]]["start"], scenes[c["scene_id"]]["duration"])]
    errors += [f"dziura/nakładka przy {b['start']} kl." for a, b in zip(v1, v1[1:]) if a["start"] + a["duration"] != b["start"]]
    return errors


_, rows = prompty.rows_of(DAY)
frames = [max(1, round(r[6][2] * STUDIO_FPS)) for r in rows]  # długości ujęć na osi Studio


def render_day():
    """Klipy dnia z nowymi długościami + arkusz klatek ujęć z kwestią (środek napisu i ostatnia klatka)."""
    from PIL import Image, ImageDraw
    sys.path.insert(0, str(RENDER))
    mod = importlib.import_module(f"render_d{DAY:02d}")
    import render as R
    assert len(mod.SCENES) == len(rows), f"render ma {len(mod.SCENES)} ujęć, rozpiska {len(rows)}"
    for (a, b, *_), r in zip(mod.SCENES, rows):
        assert abs((b - a) - r[6][2]) < 1e-6, "render liczy inne długości niż rozpiska"
    OUT.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for n, ((a, b, *rest), fr, r) in enumerate(zip(mod.SCENES, frames, rows), 1):
        clip = OUT / f"d{DAY:02d}_{n:02d}.mp4"
        count = math.ceil(fr / STUDIO_FPS * R.FPS - 1e-9)  # klip pokrywa całe ujęcie na osi
        if not clip.exists():
            tmp = clip.with_suffix(".tmp.mp4")
            proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                     "-s", f"{R.W}x{R.H}", "-r", str(R.FPS), "-i", "-", "-c:v", "libx264", "-crf", "23",
                                     "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
            for f in range(count):
                proc.stdin.write(mod.frame(min(a + f / R.FPS, b - 1e-3)).tobytes())
            proc.stdin.close()
            if proc.wait():
                raise SystemExit(f"ffmpeg: {clip}")
            tmp.rename(clip)
        if spoken_line(r[6][4]) or "„" in r[6][4]:
            vs, vl = (rest[2], rest[3]) if len(rest) >= 4 else (0.3, (b - a) - 0.4)  # dzień 1: napis przez całe ujęcie
            for t in (a + vs + vl / 2, b - 1e-3):
                thumbs.append((f"d{DAY:02d}_{n:02d} {'napis' if t < b - 0.01 else 'koniec'}", mod.frame(t).resize((384, 216))))
        print(f"{n:02d}/{len(rows)} {count} kl.", flush=True)
    if thumbs:
        cols = 6
        sheet = Image.new("RGB", (cols * 384, math.ceil(len(thumbs) / cols) * 236), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for i, (label, im) in enumerate(thumbs):
            x, y = (i % cols) * 384, (i // cols) * 236
            sheet.paste(im, (x, y + 20))
            d.text((x + 4, y + 4), label, fill=(230, 230, 230))
        sheet.save(OUT.parent / f"d{DAY:02d}-arkusz.png")
    (OUT / "gotowe.json").write_text(json.dumps({"frames": frames}))
    print(f"dzień {DAY}: {len(rows)} klipów w {OUT}", flush=True)


def upload_day():
    done = json.loads((OUT / "gotowe.json").read_text())
    assert done["frames"] == frames, "rozpiska zmieniła się po renderze — wyrenderuj dzień jeszcze raz"
    # --- plan reżyserski dnia z rozpiski (bez osi) i kontrola ciągłości ---
    subprocess.run([sys.executable, str(HERE / "zamien_dzien.py"), str(DAY), PID, PORT, "tylko_plan"], check=True)
    report = call(f"/projects/{PID}/continuity/check", {})
    heavy = [i for i in report["issues"] if i["unit"] == DAY and i["severity"] == 3]
    if heavy:
        for i in heavy:
            print(f"  ✗ {i['ref'] or '—'} {i['rule']}: {i['message']}")
        sys.exit(f"dzień {DAY}: {len(heavy)} błędów wagi 3 — Studio bez zmian")

    # --- ujęcia dnia w Studio = rozpiska ---
    p = call(f"/projects/{PID}")
    assert p["sequence"]["fps_num"] / p["sequence"]["fps_den"] == STUDIO_FPS
    old = sorted((s for s in p["scenes"] if s["legacy"].get("flow_section_id") == SID), key=lambda s: s["start"])
    # przerwany wcześniej przebieg tego dnia zostawia jedną lukę: od starego końca dnia do nowego (dalsze klipy już
    # przesunięte) — tę jedną wolno domknąć; każda inna niespójność osi zatrzymuje pracę
    resumed = f"dziura/nakładka przy {old[0]['start'] + sum(frames)} kl."
    errors = [e for e in check_axis(p) if e != resumed]
    assert not errors, f"oś niespójna już przed podmianą — Studio bez zmian: {errors[:3]}"
    assert len(old) == len(rows), f"Studio ma {len(old)} ujęć dnia {DAY}, rozpiska {len(rows)} — użyj zamien_dzien.py"
    clip_of = {}
    for s, (si, _, bi, _, k, _, _) in zip(old, rows):
        want = f"sc_d{DAY:02d}_{si}_b{bi}_s{k}"
        assert s["legacy"].get("flow_director_shot_id") == want, f"kolejność: {s['legacy'].get('flow_director_shot_id')} ≠ {want}"
        assert not (s.get("locked") or s.get("lock_timing")), f"ujęcie {want} jest zablokowane w Studio"
        pics = [c for c in p["sequence"]["clips"] if c.get("scene_id") == s["id"] and c["track_id"] == "v1"]
        assert len(pics) == 1, f"ujęcie {want} ma {len(pics)} klipów obrazu — zmień długość w Montażu"
        clip_of[s["id"]] = pics[0]["id"]

    # --- nowy materiał ---
    assets = [upload(OUT / f"d{DAY:02d}_{n:02d}.mp4", f"d{DAY:02d}_{n:02d} {s['title'][:60]}.mp4")
              for n, s in enumerate(old, 1)]
    p = call(f"/projects/{PID}")
    ids = {s["id"] for s in old}
    start = min(s["start"] for s in p["scenes"] if s["id"] in ids)
    old_end = max(s["start"] + s["duration"] for s in p["scenes"] if s["id"] in ids)
    new_end = start + sum(frames)
    later = [c for c in p["sequence"]["clips"] if c["start"] >= old_end and c.get("scene_id") not in ids]
    delta = new_end - min(c["start"] for c in later) if later else 0  # od miejsca, w którym dalsze klipy naprawdę stoją

    def shift_later():
        nonlocal p
        if not delta:
            return
        ops = [{"type": "move_clip", "clip_id": c["id"], "changes": {"start": c["start"] + delta}}
               for c in sorted(later, key=lambda c: c["start"], reverse=delta > 0)]  # przy wydłużeniu najpierw najdalsze
        for i in range(0, len(ops), 200):  # serwer przyjmuje do 200 operacji w jednej edycji
            p = call(f"/projects/{PID}/edits", {"expected_revision": p["revision"], "operations": ops[i:i + 200]})

    # --- oś: klipy dnia (materiał, start, długość); dalsze klipy robią miejsce albo dosuwają się po skróceniu ---
    if delta > 0:
        shift_later()
    starts = [start + sum(frames[:i]) for i in range(len(frames))]
    ops = [{"type": "update_clip", "clip_id": clip_of[s["id"]], "changes": {"asset_id": aid, "start": st, "duration": fr}}
           for s, aid, st, fr in zip(old, assets, starts, frames)]
    p = call(f"/projects/{PID}/edits", {"expected_revision": p["revision"], "operations": ops[::-1] if delta > 0 else ops})
    if delta < 0:
        shift_later()

    # --- ujęcia dnia: te same wartości co klipy + kwestia, opis, notatka ---
    p = call(f"/projects/{PID}")
    cur = {s["id"]: dict(s) for s in p["scenes"] if s["id"] in ids}
    changed_text = 0
    for s, row, aid, st, fr in zip(old, rows, assets, starts, frames):
        _, _, _, desc, sound = row[6]
        new = cur[s["id"]]
        line = spoken_line(sound)
        if line != new["narration"]:
            if new["narration"]:
                before = f"Dźwięk: L: {new['narration']}"
                assert before in new["director_notes"], f"notatka ujęcia {s['id']} nie ma „{before}”"
                new["director_notes"] = new["director_notes"].replace(before, f"Dźwięk: L: {line}")
            changed_text += 1
        new.update(narration=line, description=desc, start=st, duration=fr, asset_id=aid, mode="upload", animation="static")
    scenes = [cur.get(s["id"], s) for s in p["scenes"]]
    p = call(f"/projects/{PID}", {"expected_revision": p["revision"], "changes": {"scenes": scenes}}, "PATCH")

    # --- kontrola osi i dziennik ---
    p = call(f"/projects/{PID}")
    errors = check_axis(p)
    length = sum(frames) / STUDIO_FPS
    print(f"dzień {DAY}: {len(old)} ujęć w miejscu, nowy materiał, {changed_text} nowych kwestii, {length:.1f} s, "
          f"dalsze klipy {delta:+d} kl. | oś: {'OK' if not errors else errors[:3]} | rewizja {p['revision']}", flush=True)
    call(f"/projects/{PID}/flow/log", {"entry": {
        "who": "podmien_w_miejscu.py", "unit": DAY, "kind": "poprawka",
        "summary": f"Dzień {DAY} poprawiony w miejscu: {changed_text} kwestii, {length:.1f} s, nowy materiał (bez kasowania ujęć)",
        "details": f"Dalsze klipy przesunięte o {delta / STUDIO_FPS:+.2f} s. Oś po zmianie: "
                   f"{'spójna' if not errors else '; '.join(errors[:3])}. Rysunek: output/zombie-psychiatryk/render_d{DAY:02d}.py.",
        "files": ["docs/filmy/oddzial-c/ujecia/a_dane1.py", "docs/filmy/oddzial-c/ujecia/a_dane2.py",
                  f"output/zombie-psychiatryk/render_d{DAY:02d}.py"]}})
    if errors:
        sys.exit(1)
    shutil.rmtree(OUT)  # kopie są już w mediach Studio; dysk jest ciasny


if __name__ == "__main__":
    if "render" in MODES:
        render_day()
    if "wgraj" in MODES:
        upload_day()
