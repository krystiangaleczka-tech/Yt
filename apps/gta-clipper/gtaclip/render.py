"""Render picks into finished 1080x1920 Shorts.

For each pick: download only that moment (+8 s padding for later re-cuts), find the
streamer's face, choose the layout, cut dead air, add up to 3 punch zooms on the
loudest reactions, burn word-by-word captions + hook + watermark, normalise loudness
(two-pass), then save a cover image and the post text.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from . import qc as qcmod
from .capdraw import build_layer
from .captions import build_ass, caption_events
from .config import Workspace, read_json, write_json
from .reframe import analyze, game_crop, track_expr
from .setup import ffmpeg_has_ass
from .sources import fetch_section
from .transcribe import words_between
from .util import ToolError, log, media_info, run, slug

PAD = 8.0
FPS = 30


# ------------------------------------------------------------ analysis helpers
def silences(src: Path, a: float, b: float, noise: str = "-32dB", d: float = 0.9) -> list[tuple[float, float]]:
    p = run(["ffmpeg", "-v", "info", "-hide_banner", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", src,
             "-vn", "-af", f"silencedetect=n={noise}:d={d}", "-f", "null", "-"], check=False)
    out, cur = [], None
    for line in p.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            cur = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and cur is not None:
            out.append((max(0.0, cur), float(m.group(1))))
            cur = None
    if cur is not None:
        out.append((cur, b - a))
    return out


def keep_segments(length: float, sil: list[tuple[float, float]], margin: float = 0.25) -> list[tuple[float, float]]:
    keep, t = [], 0.0
    for s0, s1 in sil:
        if s0 < 1.0 or s1 > length - 1.0:   # never cut the very start or end
            continue
        a, b = s0 + margin, s1 - margin
        if b - a < 0.4:
            continue
        if a > t:
            keep.append((t, a))
        t = b
    keep.append((t, length))
    return [(round(a, 3), round(b, 3)) for a, b in keep if b - a > 0.05]


def mapper(keep: list[tuple[float, float]]):
    def f(t: float) -> float | None:
        acc = 0.0
        for a, b in keep:
            if t < a:
                return None
            if t <= b:
                return acc + (t - a)
            acc += b - a
        return None
    return f


def loudness_curve(src: Path, a: float, b: float, step: float = 0.1) -> np.ndarray:
    sr = 8000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(src), "-vn",
                          "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw[: len(raw) // 2 * 2], np.int16).astype(np.float32) / 32768
    n = int(len(x) / (sr * step))
    if n == 0:
        return np.zeros(0)
    blk = x[: n * int(sr * step)].reshape(n, -1)
    return 20 * np.log10(np.sqrt((blk ** 2).mean(axis=1)) + 1e-6)


def punch_times(curve: np.ndarray, step: float = 0.1, n: int = 3) -> list[float]:
    if len(curve) < 30:
        return []
    med = float(np.median(curve))
    order = np.argsort(-curve)
    out: list[float] = []
    for i in order:
        t = i * step
        if curve[i] < med + 10 or len(out) >= n:
            break
        if t < 1.5 or any(abs(t - o) < 4 for o in out):
            continue
        out.append(round(t, 2))
    return sorted(out)


def loudnorm_measure(src: Path, a: float, b: float) -> dict | None:
    p = run(["ffmpeg", "-hide_banner", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", src, "-vn",
             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], check=False)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        float(d["input_i"])
        return d
    except (ValueError, KeyError):
        return None


# --------------------------------------------------------------- layout graph
def layout_graph(lay: dict, look: dict) -> tuple[str, int, int]:
    """Returns (filter chain from [v0] to [lay], hook_y, cap_y)."""
    W, H = lay["width"], lay["height"]
    kind = lay["layout"]
    if H > W:  # already vertical
        return ("[v0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[lay]", 300, 1380)
    if kind == "stack" and lay.get("cam"):
        cx, cy, cw, ch = lay["cam"]
        cam_h = int(min(860, max(560, round(1080 * ch / cw / 2) * 2)))
        target = 1080 / cam_h
        if cw / ch > target:   # cam too wide -> trim width around face
            nw = int(ch * target) // 2 * 2
            fx = (lay["face"][0] + lay["face"][2] / 2) if lay.get("face") else cx + cw / 2
            cx = int(min(max(fx - nw / 2, cx), cx + cw - nw)) // 2 * 2
            cw = nw
        else:
            nh = int(cw / target) // 2 * 2
            cy = int(cy + (ch - nh) / 2) // 2 * 2
            ch = nh
        game_h = 1920 - cam_h
        gw, gh, gx, gy = game_crop(W, H, 1080, game_h, lay["cam"])
        top, bottom = ("[game]", "[cam]") if look.get("flip") else ("[cam]", "[game]")
        seam = game_h if look.get("flip") else cam_h
        g = (f"[v0]split=2[c][g];[c]crop={cw}:{ch}:{cx}:{cy},scale=1080:{cam_h},setsar=1[cam];"
             f"[g]crop={gw}:{gh}:{gx}:{gy},scale=1080:{game_h},setsar=1[game];"
             f"{top}{bottom}vstack=inputs=2,drawbox=x=0:y={seam - 4}:w=1080:h=8:color=black@1:t=fill[lay]")
        if look.get("flip"):
            return g, 170, int(game_h * 0.62)
        return g, cam_h + 130, cam_h + int(game_h * 0.56)
    if kind == "bubble" and lay.get("cam"):
        gw, gh, gx, gy = game_crop(W, H, 1080, 1920, lay["cam"])
        fx, fy, fw, fh = lay.get("face") or lay["cam"]
        side = int(min(H, W, max(fw, fh) * 2.3)) // 2 * 2
        sx = int(min(max(fx + fw / 2 - side / 2, 0), W - side))
        sy = int(min(max(fy + fh / 2 - side / 2, 0), H - side))
        b = 420
        ring = "if(gt(hypot(X-W/2,Y-H/2),W/2-12),255,{c}(X,Y))"
        g = (f"[v0]split=2[c][g];[g]crop={gw}:{gh}:{gx}:{gy},scale=1080:1920,setsar=1[bg];"
             f"[c]crop={side}:{side}:{sx}:{sy},scale={b}:{b},format=rgba,"
             f"geq=r='{ring.format(c='r')}':g='{ring.format(c='g')}':b='{ring.format(c='b')}':"
             f"a='if(lt(hypot(X-W/2,Y-H/2),W/2-1),255,0)'[bub];"
             f"[bg][bub]overlay=x=(W-w)/2:y=H-h-230[lay]")
        return g, 260, 1080
    if kind == "facecrop" and lay.get("track"):
        cw = int(H * 9 / 16) // 2 * 2
        x = track_expr(lay["track"], cw, W)
        return f"[v0]crop={cw}:{H}:'{x}':0,scale=1080:1920,setsar=1[lay]", 300, 1380
    g = ("[v0]split=2[a][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
         "gblur=sigma=28,eq=brightness=-0.12[bg];[a]scale=1080:-2,setsar=1[fg];"
         "[bg][fg]overlay=(W-w)/2:(H-h)/2[lay]")
    fg_h = int(1080 * H / W)
    return g, (1920 - fg_h) // 2 - 150, (1920 + fg_h) // 2 + 170


# ------------------------------------------------------------------ produce
def produce(ws: Workspace, folder: Path, spec: dict, out_name: str) -> dict:
    """Render one version. spec: start, end (absolute source seconds), hook, keywords, look, src_t0, peak."""
    s = ws.settings()
    look = {**{k: s[k] for k in ("layout", "flip", "style", "watermark", "accent", "keyword_color",
                                 "punch_zooms", "cut_dead_air", "sfx", "censor_on_screen")}, **(spec.get("look") or {})}
    src = folder / "src.mp4"
    info = media_info(src)
    t0 = spec["src_t0"]
    a = max(0.0, spec["start"] - t0)
    b = min(info["duration"], spec["end"] - t0)
    length = b - a
    if length < 3:
        raise ToolError("fragment za krótki")

    keep = [(0.0, length)]
    if look["cut_dead_air"] and info["has_audio"]:
        keep = keep_segments(length, silences(src, a, b))
    fmap = mapper(keep)
    out_len = sum(y - x for x, y in keep)

    tr = read_json(ws.src / f"{spec['sid']}.json", {"segments": []}) if spec.get("sid") else {"segments": []}
    words = []
    for w in words_between(tr, spec["start"], spec["end"]):
        ms, me = fmap(w["s"] - spec["start"]), fmap(min(w["e"], spec["end"]) - spec["start"])
        if ms is None:
            continue
        words.append({"w": w["w"], "s": ms, "e": me if me is not None else ms + 0.3})

    zooms = []
    if look["punch_zooms"] and info["has_audio"]:
        for t in punch_times(loudness_curve(src, a, b)):
            m = fmap(t)
            if m is not None and m < out_len - 1:
                zooms.append(round(m, 2))

    lay = analyze(src, look["layout"], start=a, dur=length)
    if lay.get("track"):
        lay["track"] = [[fmap(t) if fmap(t) is not None else t, x] for t, x in lay["track"]]
    graph, hook_y, cap_y = layout_graph(lay, look)

    cap_args = dict(cap_y=cap_y, hook_y=hook_y, watermark=look.get("watermark", ""),
                    keyword_color=look["keyword_color"], censor_on=look["censor_on_screen"])
    engine = look.get("caption_engine") or s.get("caption_engine", "auto")
    use_ass = engine == "ass" or (engine == "auto" and ffmpeg_has_ass())

    sel_v = sel_a = ""
    if len(keep) > 1:
        expr = "+".join(f"between(t,{x:.3f},{y:.3f})" for x, y in keep)
        sel_v = f"select='{expr}',setpts=N/FRAME_RATE/TB,"
        sel_a = f"aselect='{expr}',asetpts=N/SR/TB,"
    parts = [f"[0:v]fps={FPS},{sel_v}setpts=PTS-STARTPTS[v0]", graph]
    last = "[lay]"
    if zooms:
        z = "+".join(f"between(in,{int(t * FPS) - 2},{int((t + 0.7) * FPS)})" for t in zooms)
        parts.append(f"{last}zoompan=z='1+0.14*({z})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS}[zm]")
        last = "[zm]"

    inputs = ["-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", "src.mp4"]
    n_in = 1

    def add_input(*args) -> int:
        nonlocal n_in
        inputs.extend(args)
        n_in += 1
        return n_in - 1

    if use_ass:  # ffmpeg draws the text (libass)
        ass = build_ass(words, out_len, look["style"], spec.get("hook", ""), spec.get("keywords", []),
                        accent=look["accent"], **cap_args)
        (folder / "subs.ass").write_text(ass, encoding="utf-8")
        fonts_rel = os.path.relpath(ws.fonts, folder).replace("\\", "/")
        parts.append(f"{last}ass=subs.ass:fontsdir='{fonts_rel}',format=yuv420p[vout]")
    else:  # no libass: our code draws the captions, ffmpeg only overlays the images
        events = caption_events(words, out_len, look["style"], spec.get("hook", ""), spec.get("keywords", []), **cap_args)
        tracks = build_layer(events, out_len, look["style"], look["accent"], ws.fonts, folder / "caps")
        for k, tr in enumerate(tracks):  # small strips (captions, hook, watermark), each overlaid in place
            ci = add_input("-f", "concat", "-safe", "0", "-i", os.path.relpath(tr["list"], folder))
            # convert each strip once to yuva420p and blend in yuv420: avoids a per-frame RGB round trip
            parts.append(f"[{ci}:v]format=yuva420p,setpts=PTS-STARTPTS[t{k}]")
            parts.append(f"{last}[t{k}]overlay={tr['x']}:{tr['y']}:eof_action=repeat:format=yuv420[o{k}]")
            last = f"[o{k}]"
        parts.append(f"{last}format=yuv420p[vout]")
    if info["has_audio"]:
        ln = loudnorm_measure(src, a, b)
        norm = "loudnorm=I=-14:TP=-1.5:LRA=11"
        if ln:
            norm += (f":measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}"
                     f":measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true")
        parts.append(f"[0:a]{sel_a}asetpts=PTS-STARTPTS,{norm},aresample=48000[an]")
    else:
        si = add_input("-f", "lavfi", "-t", f"{out_len:.2f}", "-i", "anullsrc=r=48000:cl=stereo")
        parts.append(f"[{si}:a]anull[an]")
    alast = "[an]"
    whoosh = ws.sounds / "whoosh.wav"
    if look["sfx"] and zooms and whoosh.exists():
        idx = add_input("-i", os.path.relpath(whoosh, folder))
        n = len(zooms)
        if n > 1:
            parts.append(f"[{idx}:a]asplit={n}" + "".join(f"[w{k}]" for k in range(n)))
        for k, t in enumerate(zooms):
            src_lbl = f"[w{k}]" if n > 1 else f"[{idx}:a]"
            parts.append(f"{src_lbl}volume=0.5,adelay={int(max(0, t - 0.15) * 1000)}:all=1[s{k}]")
        parts.append(f"{alast}" + "".join(f"[s{k}]" for k in range(len(zooms))) +
                     f"amix=inputs={len(zooms) + 1}:normalize=0:duration=first[amx]")
        alast = "[amx]"
    graph_all = ";".join(p for p in parts if p)
    (folder / "graph.txt").write_text(graph_all, encoding="utf-8")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph_all, "-map", "[vout]", "-map", alast,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k",
           "-t", f"{out_len:.3f}", "-movflags", "+faststart", out_name]
    run(cmd, cwd=folder, timeout=3600)

    peak = spec.get("peak")
    pk = fmap(peak - spec["start"]) if peak else None
    cover_name = out_name.replace(".mp4", "_cover.jpg")
    make_cover(ws, folder / out_name, folder / cover_name, pk if pk is not None else out_len * 0.7, spec.get("hook", ""), look["accent"])
    return {"file": out_name, "cover": cover_name, "duration": round(out_len, 2), "layout": lay["layout"],
            "cuts": len(keep) - 1, "zooms": zooms, "words": len(words), "face": lay.get("face"),
            "presence": lay.get("presence")}


def _font(ws: Workspace, size: int):
    from PIL import ImageFont

    for p in (ws.fonts / "Poppins-Black.ttf", ws.fonts / "Anton-Regular.ttf"):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_cover(ws: Workspace, video: Path, out: Path, at: float, hook: str, accent: str) -> None:
    from PIL import Image, ImageDraw

    tmp = out.with_suffix(".raw.jpg")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0, at):.2f}", "-i", video, "-frames:v", "1", "-q:v", "3", tmp])
    im = Image.open(tmp).convert("RGB")
    if hook:
        d = ImageDraw.Draw(im)
        words = hook.upper().split()
        size = 96
        while True:  # wrap by real text width, shrink if one word is too wide
            font = _font(ws, size)
            lines, cur = [], ""
            for w in words:
                t = f"{cur} {w}".strip()
                if cur and d.textlength(t, font=font) > 940:
                    lines.append(cur)
                    cur = w
                else:
                    cur = t
            lines.append(cur)
            if size <= 48 or max(d.textlength(ln, font=font) for ln in lines) <= 940:
                break
            size -= 8
        y = 1920 * 0.60
        for ln in lines:
            bb = d.textbbox((0, 0), ln, font=font)
            w, h = bb[2] - bb[0], bb[3] - bb[1]
            x = (1080 - w) / 2
            d.rectangle([x - 28, y - 18, x + w + 28, y + h + 34], fill=accent)
            d.text((x, y - bb[1] + 4), ln, font=font, fill="#111111")
            y += h + 64
    im.save(out, quality=90)
    tmp.unlink(missing_ok=True)


def post_text(p: dict) -> str:
    return f"{p.get('title', '')}\n\n{' '.join(p.get('hashtags', []))}\n\n{p.get('credit', '')}\n"


# ------------------------------------------------------------------ batch
def new_short_id(p: dict, idx: int, batch: str) -> str:
    return f"{batch}_{idx:02d}_{slug(p.get('name') or 'short', 16)}"


def render_pick(ws: Workspace, p: dict, idx: int, batch: str, extra: dict | None = None) -> dict:
    sid = p["sid"]
    meta = read_json(ws.src / f"{sid}.meta.json", {})
    short_id = new_short_id(p, idx, batch)
    folder = ws.shorts / short_id
    folder.mkdir(parents=True, exist_ok=True)
    t0 = max(0.0, p["start"] - PAD)
    log(f"  [{idx:02d}] pobieram {p['hook']} ({p['end'] - p['start']:.0f} s)")
    if extra and extra.get("src_file"):
        Path(extra["src_file"]).replace(folder / "src.mp4")
        t0 = extra["src_t0"]
    else:
        fetch_section(meta or {"url": p["url"]}, t0, p["end"] + PAD, folder / "src.mp4")
    spec = {"sid": sid, "start": p["start"], "end": p["end"], "hook": p["hook"], "keywords": p.get("keywords", []),
            "peak": p.get("peak"), "src_t0": t0, "look": {}}
    log(f"  [{idx:02d}] montuję")
    res = produce(ws, folder, spec, "v0.mp4")
    (folder / "post.txt").write_text(post_text(p), encoding="utf-8")
    q = qcmod.check(folder / "v0.mp4", {**res, "hook": p["hook"], "score": p.get("score", 0)})
    res["qc"] = q
    sm = {"id": short_id, "batch": batch, "created": int(time.time()), "status": "new", "source": extra.get("source", "vod") if extra else "vod",
          "pick": p, "spec": spec, "versions": [{"v": 0, "note": "oryginał", "created": int(time.time()), **res}],
          "current": 0, "scheduled_at": None, "published": False}
    write_json(folder / "meta.json", sm)
    log(f"  [{idx:02d}] {q['status']} {short_id} {'; '.join(q['notes'])}")
    return sm


def render_batch(ws: Workspace, picks: list[dict], workers: int | None = None) -> list[dict]:
    s = ws.settings()
    batch = time.strftime("%Y%m%d-%H%M")
    workers = workers or s["workers"]
    results = []

    def job(ip):
        i, p = ip
        try:
            return render_pick(ws, p, i, batch)
        except Exception as e:  # keep the rest going
            log(f"  [{i:02d}] błąd: {e}")
            return None

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        for r in ex.map(job, list(enumerate(picks, 1))):
            if r:
                results.append(r)
    overview(ws, results, ws.shorts / f"overview_{batch}.jpg")
    c = {k: sum(1 for r in results if r["versions"][0]["qc"]["status"] == k) for k in ("PASS", "WARN", "FAIL")}
    log(f"\n{len(results)} Shortsów gotowych w {ws.shorts}: {c['PASS']} PASS, {c['WARN']} WARN, {c['FAIL']} FAIL")
    return results


def overview(ws: Workspace, shorts: list[dict], out: Path) -> None:
    from PIL import Image, ImageDraw

    if not shorts:
        return
    tw, th, cols = 216, 384, 5
    rows = (len(shorts) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 12) + 12, rows * (th + 12) + 12), "#101014")
    d = ImageDraw.Draw(sheet)
    colors = {"PASS": "#2BD46B", "WARN": "#F5B400", "FAIL": "#FF4D4D"}
    for k, sm in enumerate(shorts):
        v = sm["versions"][-1]
        cov = ws.shorts / sm["id"] / v["cover"]
        x, y = 12 + (k % cols) * (tw + 12), 12 + (k // cols) * (th + 12)
        if cov.exists():
            sheet.paste(Image.open(cov).resize((tw, th)), (x, y))
        st = v["qc"]["status"]
        d.rectangle([x + 6, y + 6, x + 70, y + 30], fill=colors[st])
        d.text((x + 12, y + 10), st, fill="#000000")
    sheet.save(out, quality=88)
