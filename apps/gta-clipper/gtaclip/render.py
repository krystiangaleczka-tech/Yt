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


def spec_segments(spec: dict, src_dur: float) -> list[tuple[float, float, float]]:
    """Segments to play, in order: [(a, b, speed)] in absolute source seconds, clamped to the downloaded file."""
    lo, hi = spec["src_t0"], spec["src_t0"] + src_dur
    segs = spec.get("segments") or [{"a": spec["start"], "b": spec["end"], "speed": 1.0}]
    out = []
    for s in segs:
        a, b = max(lo, float(s["a"])), min(hi, float(s["b"]))
        sp = min(4.0, max(0.25, float(s.get("speed") or 1.0)))
        if b - a >= 0.2:
            out.append((round(a, 3), round(b, 3), sp))
    return out


def plan_pieces(src: Path, spec: dict, src_dur: float, cut_dead_air: bool, has_audio: bool,
                silence_fn=None) -> list[tuple[float, float, float]]:
    """What the Short plays, in order: [(a, b, speed)] in absolute source seconds, dead air cut inside each segment."""
    silence_fn = silence_fn or silences
    t0 = spec["src_t0"]
    pieces = []
    for a, b, sp in spec_segments(spec, src_dur):
        keep = [(0.0, b - a)]
        if cut_dead_air and has_audio and b - a > 3:
            keep = keep_segments(b - a, silence_fn(src, a - t0, b - t0))
        pieces += [(round(a + x, 3), round(a + y, 3), sp) for x, y in keep]
    return pieces


def timeline(pieces: list[tuple[float, float, float]]) -> list[list[float]]:
    """[[out_start, out_end, src_a, src_b, speed]] — where each piece lands in the finished Short."""
    tl, acc = [], 0.0
    for a, b, sp in pieces:
        d = (b - a) / sp
        tl.append([round(acc, 3), round(acc + d, 3), a, b, sp])
        acc += d
    return tl


def src_to_out(tl: list[list[float]], t: float) -> float | None:
    """Absolute source second -> second of the Short (first place it is shown), None if cut out."""
    for o0, _o1, a, b, sp in tl:
        if a <= t <= b:
            return round(o0 + (t - a) / sp, 3)
    return None


def out_to_src(tl: list[list[float]], t: float) -> float:
    """Second of the Short -> absolute source second (clamped to the ends)."""
    if not tl:
        return t
    if t <= tl[0][0]:
        return tl[0][2]
    for o0, o1, a, _b, sp in tl:
        if o0 <= t <= o1:
            return round(a + (t - o0) * sp, 3)
    return tl[-1][3]


def _atempo(speed: float) -> str:
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5")
        s /= 0.5
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


def _between(ranges, var: str = "t") -> str:
    return "+".join(f"between({var},{x:.3f},{y:.3f})" for x, y in ranges)


TEXT_Y = {"top": 420, "middle": 960, "bottom": 1500}
CAP_Y = {"top": 330, "middle": 960, "bottom": 1600}


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
    """Render one version.

    spec: start, end (absolute source seconds), hook, keywords, look, src_t0, peak, and optional edits —
    all times in absolute source seconds:
      segments  [{a, b, speed}]   what plays, in order (cut, reorder, repeat, speed up / slow down)
      zoom_at   [{t, dur, z, x, y}] zooms on a point (x, y = 0..1 of the frame)
      mute      [[a, b]], mute_all, noise (0..1: pink noise over the muted parts)
      texts     [{text, t, dur, color, size, pos}]  extra on-screen text (pos: top | middle | bottom)
    """
    s = ws.settings()
    look = {**{k: s[k] for k in ("layout", "flip", "style", "watermark", "accent", "keyword_color",
                                 "punch_zooms", "cut_dead_air", "sfx", "censor_on_screen")}, **(spec.get("look") or {})}
    src = folder / "src.mp4"
    info = media_info(src)
    t0 = spec["src_t0"]
    pieces = plan_pieces(src, spec, info["duration"], look["cut_dead_air"], info["has_audio"])
    tl = timeline(pieces)
    out_len = tl[-1][1] if tl else 0.0
    if out_len < 3:
        raise ToolError("fragment za krótki")
    lo, hi = min(p[0] for p in pieces), max(p[1] for p in pieces)

    def fmap(t_abs: float) -> float | None:
        return src_to_out(tl, t_abs)

    tr = read_json(ws.src / f"{spec['sid']}.json", {"segments": []}) if spec.get("sid") else {"segments": []}
    words = []
    for o0, _o1, a, b, sp in tl:  # per piece, so repeated pieces get their captions again
        for w in words_between(tr, a, b):
            if w["s"] < a:
                continue
            ws_, we = o0 + (w["s"] - a) / sp, o0 + (min(w["e"], b) - a) / sp
            words.append({"w": w["w"], "s": round(ws_, 3), "e": round(max(we, ws_ + 0.1), 3)})
    words.sort(key=lambda w: w["s"])

    zooms = []  # {"t": out seconds, "dur", "z", "x", "y"}
    if look["punch_zooms"] and info["has_audio"]:
        for t in punch_times(loudness_curve(src, lo - t0, hi - t0)):
            m = fmap(lo + t)
            if m is not None and m < out_len - 1:
                zooms.append({"t": round(m, 2), "dur": 0.7, "z": 1.14, "x": 0.5, "y": 0.5})
    for zq in spec.get("zoom_at") or []:
        m = fmap(float(zq["t"]))
        if m is not None and m < out_len - 0.2:
            zooms.append({"t": round(m, 2), "dur": float(zq.get("dur") or 1.5), "z": min(2.5, max(1.05, float(zq.get("z") or 1.35))),
                          "x": min(1.0, max(0.0, float(zq.get("x", 0.5)))), "y": min(1.0, max(0.0, float(zq.get("y", 0.5))))})
    zooms.sort(key=lambda z: z["t"])

    lay = analyze(src, look["layout"], start=lo - t0, dur=hi - lo)
    if lay.get("track"):
        tr_pts = [[fmap(lo + t), x] for t, x in lay["track"]]
        lay["track"] = sorted([p for p in tr_pts if p[0] is not None]) or lay["track"]
    graph, hook_y, cap_y = layout_graph(lay, look)
    if look.get("cap_pos") in CAP_Y:
        cap_y = CAP_Y[look["cap_pos"]]
        if abs(hook_y - cap_y) < 300:  # keep the hook clear of the captions
            hook_y = 960 if cap_y < 700 else 300

    texts = []
    for tx in spec.get("texts") or []:
        m = fmap(float(tx["t"]))
        if m is None or not str(tx.get("text", "")).strip():
            continue
        texts.append({"text": str(tx["text"]), "start": m, "end": min(out_len, m + float(tx.get("dur") or 2.5)),
                      "y": TEXT_Y.get(tx.get("pos"), TEXT_Y["top"]), "color": tx.get("color") or "#FFFFFF",
                      "size": int(min(200, max(50, float(tx.get("size") or 110))))})

    hook_secs = float(look.get("hook_secs") or 3.5)
    for t in texts:  # never stack an extra text on the hook or the captions
        if spec.get("hook") and t["start"] < hook_secs and abs(t["y"] - hook_y) < 300:
            t["y"] = hook_y - 300 if hook_y - 300 >= 180 else hook_y + 300
        if abs(t["y"] - cap_y) < 220:
            t["y"] = cap_y - 260 if cap_y - 260 >= 180 else cap_y + 260

    cap_args = dict(cap_y=cap_y, hook_y=hook_y, watermark=look.get("watermark", ""),
                    keyword_color=look["keyword_color"], censor_on=look["censor_on_screen"],
                    hook_secs=hook_secs, texts=texts)
    engine = look.get("caption_engine") or s.get("caption_engine", "pil")
    use_ass = engine == "ass" or (engine == "auto" and ffmpeg_has_ass())

    n = len(pieces)
    parts = [f"[0:v]fps={FPS},split={n}" + "".join(f"[s{i}]" for i in range(n)) if n > 1 else f"[0:v]fps={FPS}[s0]"]
    for i, (a, b, sp) in enumerate(pieces):
        parts.append(f"[s{i}]trim=start={a - t0:.3f}:end={b - t0:.3f},setpts=(PTS-STARTPTS)/{sp:.4f}[p{i}]")
    parts.append("".join(f"[p{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v0]")
    parts.append(graph)
    last = "[lay]"
    if zooms:
        def win(z):
            return f"between(in,{max(0, int(z['t'] * FPS) - 2)},{int((z['t'] + z['dur']) * FPS)})"
        zexpr = "+".join(f"{z['z'] - 1:.3f}*{win(z)}" for z in zooms)
        fx = "+".join(f"{z['x'] - 0.5:.3f}*{win(z)}" for z in zooms if z["x"] != 0.5) or "0"
        fy = "+".join(f"{z['y'] - 0.5:.3f}*{win(z)}" for z in zooms if z["y"] != 0.5) or "0"
        parts.append(f"{last}zoompan=z='min(2.5,1+{zexpr})':x='clip(iw*(0.5+{fx})-iw/zoom/2,0,iw-iw/zoom)':"
                     f"y='clip(ih*(0.5+{fy})-ih/zoom/2,0,ih-ih/zoom)':d=1:s=1080x1920:fps={FPS}[zm]")
        last = "[zm]"

    inputs = ["-i", "src.mp4"]
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
        for k, trk in enumerate(tracks):  # small strips (captions, hook, watermark), each overlaid in place
            ci = add_input("-f", "concat", "-safe", "0", "-i", os.path.relpath(trk["list"], folder))
            # convert each strip once to yuva420p and blend in yuv420: avoids a per-frame RGB round trip
            parts.append(f"[{ci}:v]format=yuva420p,setpts=PTS-STARTPTS[t{k}]")
            parts.append(f"{last}[t{k}]overlay={trk['x']}:{trk['y']}:eof_action=repeat:format=yuv420[o{k}]")
            last = f"[o{k}]"
        parts.append(f"{last}format=yuv420p[vout]")

    mute = [(fmap(float(a)), fmap(float(b))) for a, b in spec.get("mute") or []]
    mute = [(x, y) for x, y in mute if x is not None and y is not None and y > x]
    if spec.get("mute_all"):
        mute = [(0.0, out_len)]
    if info["has_audio"]:
        parts.append(f"[0:a]asplit={n}" + "".join(f"[as{i}]" for i in range(n)) if n > 1 else "[0:a]anull[as0]")
        for i, (a, b, sp) in enumerate(pieces):
            tempo = f",{_atempo(sp)}" if abs(sp - 1) > 1e-3 else ""
            parts.append(f"[as{i}]atrim=start={a - t0:.3f}:end={b - t0:.3f},asetpts=PTS-STARTPTS{tempo}[ap{i}]")
        parts.append("".join(f"[ap{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[acat]")
        chain = "[acat]"
        if mute:
            parts.append(f"{chain}volume=0:enable='{_between(mute)}'[amut]")
            chain = "[amut]"
        if spec.get("mute_all"):
            parts.append(f"{chain}aresample=48000[an]")
        else:
            ln = loudnorm_measure(src, lo - t0, hi - t0)
            norm = "loudnorm=I=-14:TP=-1.5:LRA=11"
            if ln:
                norm += (f":measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}"
                         f":measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true")
            parts.append(f"{chain}{norm},aresample=48000[an]")
    else:
        si = add_input("-f", "lavfi", "-t", f"{out_len:.2f}", "-i", "anullsrc=r=48000:cl=stereo")
        parts.append(f"[{si}:a]anull[an]")
    alast = "[an]"
    noise = float(spec.get("noise") or 0)
    if noise > 0 and mute:
        parts.append(f"anoisesrc=d={out_len:.3f}:c=pink:r=48000:a={min(1.0, noise) * 0.25:.3f},aformat=channel_layouts=stereo,"
                     f"volume=0:enable='not({_between(mute)})'[nz]")
        parts.append(f"{alast}[nz]amix=inputs=2:normalize=0:duration=first[anz]")
        alast = "[anz]"
    whoosh = ws.sounds / "whoosh.wav"
    if look["sfx"] and zooms and whoosh.exists():
        idx = add_input("-i", os.path.relpath(whoosh, folder))
        k_n = len(zooms)
        if k_n > 1:
            parts.append(f"[{idx}:a]asplit={k_n}" + "".join(f"[w{k}]" for k in range(k_n)))
        for k, z in enumerate(zooms):
            src_lbl = f"[w{k}]" if k_n > 1 else f"[{idx}:a]"
            parts.append(f"{src_lbl}volume=0.5,adelay={int(max(0, z['t'] - 0.15) * 1000)}:all=1[s{k}]")
        parts.append(f"{alast}" + "".join(f"[s{k}]" for k in range(k_n)) +
                     f"amix=inputs={k_n + 1}:normalize=0:duration=first[amx]")
        alast = "[amx]"
    graph_all = ";".join(p for p in parts if p)
    (folder / "graph.txt").write_text(graph_all, encoding="utf-8")
    tmp_name = out_name.replace(".mp4", ".part.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph_all, "-map", "[vout]", "-map", alast,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k",
           "-t", f"{out_len:.3f}", "-movflags", "+faststart", tmp_name]
    run(cmd, cwd=folder, timeout=3600)
    (folder / tmp_name).replace(folder / out_name)  # never leave a half-written version under its real name

    peak = spec.get("peak")
    pk = fmap(peak) if peak else None
    cover_name = out_name.replace(".mp4", "_cover.jpg")
    make_cover(ws, folder / out_name, folder / cover_name, pk if pk is not None else out_len * 0.7, spec.get("hook", ""), look["accent"])
    return {"file": out_name, "cover": cover_name, "duration": round(out_len, 2), "layout": lay["layout"],
            "cuts": len(pieces) - 1, "zooms": [z["t"] for z in zooms], "words": len(words), "face": lay.get("face"),
            "presence": lay.get("presence"), "timeline": tl}


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

    tmp = out.with_suffix(".raw.png")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0, at):.2f}", "-i", video, "-frames:v", "1", tmp])
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
    q = qcmod.check(folder / "v0.mp4", {**res, "hook": p["hook"], "score": p.get("score", 0)}, ws)
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
