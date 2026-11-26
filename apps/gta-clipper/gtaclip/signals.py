"""Find the hot seconds in hours of stream — without any AI.

Signals per second:
  LOUD      voice jumps above the stream's own running level (dB over rolling median)
  CHAT      distinct chatters in 10 s vs. the usual rate (x times)
  REPLAYED  YouTube "most replayed" heat map (x times the median)
  MOMENT    words that name a GTA moment: chase, crash, fight, stunt, reaction, funny
  HEAT      all of the above combined, 0-100

Candidate windows are built around HEAT peaks and snapped to sentence boundaries,
so every window starts with a premise and ends after the payoff.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import numpy as np

from .chat import load_replay, top_tokens
from .config import Workspace, write_json
from .transcribe import text_between
from .util import hms, log

MOMENTS = {
    "chase": r"\b(cops?|police|chase|chasing|wanted|stars?|run+|helicopter|swat)\b",
    "crash": r"\b(crash(ed|ing)?|wreck(ed)?|flip(ped)?|explod\w*|blew up|boom)\b",
    "fight": r"\b(fight|punch(ed)?|shot|shoot(ing)?|kill(ed)?|dead|died|gun)\b",
    "stunt": r"\b(jump(ed)?|stunt|parachute|flying|plane|land(ed)?|insane)\b",
    "reaction": r"\b(no way|oh my god|what the|bro what|are you serious|yo+|wait+|look at)\b",
    "funny": r"\b(haha+|lol|lmao|funny|laugh\w*|bruh)\b|\[laugh",
}
HYPE = re.compile(r"!|\b(yo+|bro+|what+|no+|wow|holy|crazy|insane|let'?s go+)\b", re.I)


def loudness_per_second(audio: Path) -> np.ndarray:
    """RMS level in dBFS for every second (streamed, low memory)."""
    sr = 8000
    cmd = ["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out = []
    while True:
        raw = p.stdout.read(sr * 2 * 60)
        if not raw:
            break
        a = np.frombuffer(raw[: len(raw) // 2 * 2], np.int16).astype(np.float32) / 32768.0
        n = len(a) // sr
        if n:
            blk = a[: n * sr].reshape(n, sr)
            out.extend((20 * np.log10(np.sqrt((blk ** 2).mean(axis=1)) + 1e-6)).tolist())
    p.wait()
    return np.array(out, dtype=np.float32)


def rolling_median(x: np.ndarray, win: int) -> np.ndarray:
    if len(x) == 0:
        return x
    pad = win // 2
    xp = np.pad(x, (pad, pad), mode="edge")
    step = max(1, win // 10)
    idx = np.arange(0, len(x), step)
    med = np.array([np.median(xp[i:i + win]) for i in idx])
    return np.interp(np.arange(len(x)), idx, med)


def compute(ws: Workspace, meta: dict, tr: dict) -> dict:
    sid = meta["sid"]
    audio = next((p for p in ws.src.glob(f"{sid}.*") if p.suffix in (".m4a", ".opus", ".webm", ".mp3", ".wav")), None)
    off = float(tr.get("offset", 0) or 0)
    loud = loudness_per_second(audio) if audio else np.zeros(int(tr.get("end", 0)))
    n = len(loud)
    t0 = off
    base = rolling_median(loud, 61)
    loud_up = np.clip(loud - base, 0, 30)

    # chat
    chat = load_replay(ws.src, sid)
    chat_x = np.zeros(n)
    chat_per_s = np.zeros(n)
    chat_by_sec: dict[int, list] = {}
    if chat:
        for t, a, txt in chat:
            i = int(t - t0)
            if 0 <= i < n:
                chat_per_s[i] += 1
                chat_by_sec.setdefault(i, []).append((t, a, txt))
        w10 = np.convolve(chat_per_s, np.ones(10), mode="same")
        cb = rolling_median(w10, 301)
        chat_x = w10 / np.maximum(cb, 1.0)

    # YouTube most replayed
    rep = np.zeros(n)
    hm = meta.get("heatmap") or []
    if hm:
        vals = np.array([h.get("value", 0) for h in hm])
        med = float(np.median(vals)) or 0.01
        for h in hm:
            a, b = int(h["start_time"] - t0), int(h["end_time"] - t0)
            rep[max(0, a):max(0, min(n, b))] = h.get("value", 0) / med

    # words
    mom = np.zeros(n)
    hype = np.zeros(n)
    labels: dict[int, set] = {}
    for seg in tr.get("segments", []):
        i = int(seg["start"] - t0)
        if not 0 <= i < n:
            continue
        txt = seg["text"].lower()
        for lab, rx in MOMENTS.items():
            if re.search(rx, txt):
                mom[i:i + 4] += 1
                labels.setdefault(i, set()).add(lab)
        hype[i:i + 3] += len(HYPE.findall(seg["text"]))

    def z(x):
        if not len(x) or x.max() <= 0:
            return np.zeros_like(x, dtype=float)
        return np.clip(x / (np.percentile(x, 99.5) + 1e-6), 0, 1.5)

    heat = (0.38 * z(loud_up) + 0.27 * z(np.maximum(chat_x - 1, 0)) + 0.17 * z(np.maximum(rep - 1, 0))
            + 0.10 * z(mom) + 0.08 * z(hype))
    heat = np.convolve(heat, np.ones(5) / 5, mode="same")
    heat = np.clip(heat / (heat.max() + 1e-6) * 100, 0, 100) if len(heat) else heat
    sig = {"sid": sid, "offset": t0, "loud": loud.round(1).tolist(), "loud_up": loud_up.round(1).tolist(),
           "chat_x": np.round(chat_x, 2).tolist(), "chat_per_s": chat_per_s.astype(int).tolist(),
           "replayed": np.round(rep, 2).tolist(), "heat": np.round(heat, 1).tolist(),
           "labels": {str(k): sorted(v) for k, v in labels.items()}, "has_chat": bool(chat)}
    write_json(ws.src / f"{sid}.signals.json", sig)
    sig["_chat_by_sec"] = chat_by_sec
    return sig


def _snap(tr: dict, start: float, end: float, peak: float, min_len: float, max_len: float) -> tuple[float, float]:
    segs = tr.get("segments", [])
    # earliest sentence start that still gives a premise, latest sentence end that keeps the payoff
    starts = [s["start"] for s in segs if start - 4 <= s["start"] <= peak - 4]
    ends = [s["end"] for s in segs if peak + 2 <= s["end"] <= end + 4]
    s0 = min(starts) if starts else start
    e0 = max(ends) if ends else end
    if e0 - s0 < min_len:
        e0 = s0 + min_len
    if e0 - s0 > max_len:
        s0 = max(s0, e0 - max_len)
    return round(s0, 2), round(e0 + 0.4, 2)


def candidates(ws: Workspace, sources: list[tuple[dict, dict]], n: int = 30) -> list[dict]:
    s = ws.settings()
    min_len, max_len = s["min_len"], s["max_len"]
    from . import music
    check_music = s.get("skip_music", True) and music.available(ws)
    out, skipped = [], 0
    for meta, tr in sources:
        sig = compute(ws, meta, tr)
        audio = next((p for p in ws.src.glob(f"{meta['sid']}.*") if p.suffix in (".m4a", ".opus", ".webm", ".mp3", ".wav")), None)
        heat = np.array(sig["heat"])
        if not len(heat):
            continue
        t0 = sig["offset"]
        order = np.argsort(-heat)
        taken: list[int] = []
        per_src = 0
        for i in order:
            if heat[i] < 25 or per_src >= max(6, n // max(1, len(sources))):
                break
            if any(abs(i - j) < 40 for j in taken):
                continue
            peak = t0 + i
            st, en = _snap(tr, peak - 22, peak + 12, peak, min_len, max_len)
            if check_music and audio:  # background music = Content ID claims: let the moment go
                rep = music.summarize(music.scores(music.model_path(ws), audio, start=max(0.0, st - t0), dur=en - st))
                if rep["warn"]:
                    skipped += 1
                    taken.append(int(i))  # keep the spacing so its neighbours are not re-tested
                    continue
            taken.append(int(i))
            a, b = int(st - t0), int(en - t0)
            win = slice(max(0, a), max(a + 1, b))
            tags = []
            lu = max(sig["loud_up"][win] or [0])
            if lu >= 6:
                tags.append(f"[LOUD +{lu:.0f}dB]")
            cx = max(sig["chat_x"][win] or [0])
            if cx >= 2:
                msgs = [m for k in range(win.start, win.stop) for m in sig["_chat_by_sec"].get(k, [])]
                tok = top_tokens(msgs, 1)
                tags.append(f"[CHAT x{cx:.0f}{' ' + tok[0] if tok else ''}]")
            rp = max(sig["replayed"][win] or [0])
            if rp >= 1.5:
                tags.append(f"[REPLAYED x{rp:.0f}]")
            labs = sorted({l for k in range(win.start, win.stop) for l in sig["labels"].get(str(k), [])})
            if labs:
                tags.append(f"[MOMENT {' '.join(labs[:2])}]")
            tags.append(f"[HEAT {heat[i]:.0f}]")
            out.append({
                "sid": meta["sid"], "url": meta["url"], "title": meta.get("title", ""), "name": meta.get("name", ""),
                "platform": meta.get("platform"), "start": st, "end": en, "peak": round(peak, 1),
                "heat": round(float(heat[i]), 1), "tags": tags, "labels": labs,
                "transcript": text_between(tr, st, en),
            })
            per_src += 1
    out.sort(key=lambda c: -c["heat"])
    out = out[:n]
    for k, c in enumerate(out, 1):
        c["cid"] = k
    write_json(ws.path("candidates.json"), out)
    write_candidates_md(ws, out)
    log(f"{len(out)} kandydatów → {ws.path('candidates.md')}" + (f" (pominąłem {skipped} z muzyką w tle)" if skipped else ""))
    return out


def write_candidates_md(ws: Workspace, cands: list[dict]) -> None:
    lines = ["# Candidates (best windows by loudness, chat, replays and words)", ""]
    for c in cands:
        lines.append(f"## #{c['cid']} {c['name']} — {c['title'][:80]}")
        lines.append(f"source {c['sid']} | {hms(c['start'])}–{hms(c['end'])} | peak {hms(c['peak'])} | {' '.join(c['tags'])}")
        lines.append(c["transcript"] or "(no speech)")
        lines.append("")
    ws.path("candidates.md").write_text("\n".join(lines), encoding="utf-8")
