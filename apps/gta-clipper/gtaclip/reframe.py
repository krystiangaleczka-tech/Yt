"""Where is the streamer? Face tracking that decides the 9:16 layout.

  facecrop  the face fills the screen (IRL, podcast) -> 9:16 crop that follows the face
  stack     a webcam overlay is found -> cam on top, game below (flip = cam below)
  bubble    full-frame game with a round cam bubble
  full      no cam visible -> whole frame over a blurred copy of itself
"""
from __future__ import annotations

import subprocess
import threading
from pathlib import Path

import numpy as np

from .util import media_info


_LOCK = threading.Lock()


def _cascades():
    # cv2 must not be imported by several render threads at once; cascades are not thread-safe
    with _LOCK:
        import cv2

        base = Path(cv2.data.haarcascades)
        return (cv2.CascadeClassifier(str(base / "haarcascade_frontalface_default.xml")),
                cv2.CascadeClassifier(str(base / "haarcascade_profileface.xml")))


def sample_frames(video: Path, fps: float = 2.0, width: int = 640, start: float = 0, dur: float | None = None):
    info = media_info(video)
    W, H = info["width"], info["height"]
    h = int(round(H * width / W / 2) * 2)
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.2f}"]
    if dur:
        cmd += ["-t", f"{dur:.2f}"]
    cmd += ["-i", str(video), "-vf", f"fps={fps},scale={width}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (width * h * 3)
    frames = np.frombuffer(raw[: n * width * h * 3], np.uint8).reshape(n, h, width, 3)
    return frames, W, H, width / W


def detect_faces(frames) -> list[list[tuple[int, int, int, int]]]:
    front, prof = _cascades()
    import cv2

    out = []
    for f in frames:
        g = cv2.equalizeHist(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
        fs = list(front.detectMultiScale(g, 1.12, 6, minSize=(22, 22)))
        if not fs:
            fs = list(prof.detectMultiScale(g, 1.12, 6, minSize=(22, 22)))
            if not fs:  # profile facing the other way
                fl = prof.detectMultiScale(cv2.flip(g, 1), 1.12, 6, minSize=(22, 22))
                fs = [(g.shape[1] - x - w, y, w, h) for x, y, w, h in fl]
        out.append([tuple(int(v) for v in b) for b in fs])
    return out


def analyze(video: Path, layout: str = "auto", start: float = 0, dur: float | None = None) -> dict:
    frames, W, H, sc = sample_frames(video, start=start, dur=dur)
    dets = detect_faces(frames)
    n = max(1, len(frames))
    fw = frames.shape[2] if len(frames) else 640
    fh = frames.shape[1] if len(frames) else 360
    # cluster face centres on a coarse grid
    clusters: dict[tuple[int, int], list] = {}
    cell = fw * 0.09
    for i, faces in enumerate(dets):
        for (x, y, w, h) in faces:
            key = (int((x + w / 2) // cell), int((y + h / 2) // cell))
            clusters.setdefault(key, []).append((i, x, y, w, h))
    # merge neighbours
    best_hits: list = []
    for key, hits in clusters.items():
        merged = [h for k2, hs in clusters.items() if abs(k2[0] - key[0]) <= 1 and abs(k2[1] - key[1]) <= 1 for h in hs]
        frames_hit = {h[0] for h in merged}
        if len(frames_hit) > len({h[0] for h in best_hits}):
            best_hits = merged
    res = {"width": W, "height": H, "layout": "full", "cam": None, "face": None, "track": [], "presence": 0.0}
    if best_hits:
        presence = len({h[0] for h in best_hits}) / n
        arr = np.array([h[1:] for h in best_hits], dtype=float)
        x, y, w, h = np.median(arr, axis=0)
        cx_std = float(np.std(arr[:, 0] + arr[:, 2] / 2)) / fw
        area = (w * h) / (fw * fh)
        res["presence"] = round(presence, 2)
        face = [x / sc, y / sc, w / sc, h / sc]
        res["face"] = [round(v) for v in face]
        if presence >= 0.45 and area >= 0.045:
            res["layout"] = "facecrop"
            res["track"] = _track(dets, sc, n, fps=2.0, W=W)
        elif presence >= 0.3 and cx_std < 0.05:
            res["cam"] = cam_box(face, W, H)
            res["layout"] = "stack"
    if layout != "auto":
        if layout in ("stack", "bubble") and not res["cam"]:
            if res["face"]:
                res["cam"] = cam_box(res["face"], W, H)
            else:
                res["layout"] = "full"
                return res
        if layout == "facecrop" and not res["track"]:
            res["track"] = _track(dets, sc, n, 2.0, W) if res["face"] else []
            if not res["track"]:
                res["layout"] = "full"
                return res
        res["layout"] = layout
    return res


def cam_box(face, W: int, H: int) -> list[int]:
    """Estimate the webcam overlay rectangle from the face box."""
    x, y, w, h = face
    bw, bh = w * 3.4, h * 3.0
    cx, cy = x + w / 2, y + h / 2
    bx, by = cx - bw / 2, cy - bh * 0.45
    # snap to frame edges when close (overlays sit in corners)
    snap = 0.07
    if bx < W * snap:
        bx = 0
    if bx + bw > W * (1 - snap):
        bx = W - bw
    if by < H * snap:
        by = 0
    if by + bh > H * (1 - snap):
        by = H - bh
    bx, by = max(0, bx), max(0, by)
    bw, bh = min(bw, W - bx), min(bh, H - by)
    return [int(bx) // 2 * 2, int(by) // 2 * 2, int(bw) // 2 * 2, int(bh) // 2 * 2]


def _track(dets, sc, n, fps, W):
    pts = []
    for i, faces in enumerate(dets):
        if faces:
            x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
            pts.append((i / fps, (x + w / 2) / sc))
    if not pts:
        return []
    t = np.array([p[0] for p in pts])
    c = np.array([p[1] for p in pts])
    tt = np.arange(0, n / fps, 0.5)
    cc = np.interp(tt, t, c)
    k = 5
    cc = np.convolve(np.pad(cc, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    return [[round(float(a), 2), round(float(b))] for a, b in zip(tt, cc)]


def game_crop(W: int, H: int, out_w: int, out_h: int, cam=None) -> list[int]:
    """Crop of the game area with aspect out_w:out_h, moved away from the cam overlay."""
    ch = H
    cw = int(ch * out_w / out_h)
    if cw > W:
        cw = W
        ch = int(cw * out_h / out_w)
    x = (W - cw) // 2
    if cam:
        cx0, cx1 = cam[0], cam[0] + cam[2]
        if cx1 <= W / 2 and x < cx1:          # cam on the left
            x = min(W - cw, max(x, cx1))
        elif cx0 >= W / 2 and x + cw > cx0:   # cam on the right
            x = max(0, min(x, cx0 - cw))
    y = (H - ch) // 2
    return [cw // 2 * 2, ch // 2 * 2, int(x), int(y)]


def track_expr(track, crop_w: int, W: int) -> str:
    """ffmpeg expression for crop x following the face (piecewise linear)."""
    if not track:
        return str((W - crop_w) // 2)
    xs = [(t, min(max(cx - crop_w / 2, 0), W - crop_w)) for t, cx in track]
    # thin out to keep the expression short
    step = max(1, len(xs) // 40)
    xs = xs[::step] + ([xs[-1]] if xs[-1] not in xs[::step] else [])
    expr = f"{xs[-1][1]:.0f}"
    for (t0, x0), (t1, x1) in reversed(list(zip(xs, xs[1:]))):
        d = max(t1 - t0, 0.01)
        expr = f"if(lt(t,{t1:.2f}),{x0:.0f}+({x1 - x0:.0f})*(t-{t0:.2f})/{d:.2f},{expr})"
    return f"if(lt(t,{xs[0][0]:.2f}),{xs[0][1]:.0f},{expr})"
