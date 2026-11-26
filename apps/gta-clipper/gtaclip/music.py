"""Is there music in this clip? (Music under a stream = the most common Content ID claim, from the label.)

YAMNet (Google, Apache 2.0, AudioSet classes) runs on ~1 s windows every ~0.5 s via LiteRT.
It tells music apart from speech, engines, gunshots etc., and still hears music under talking.
"""
from __future__ import annotations

import subprocess
import threading
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

MODEL_URL = ("https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/"
             "audio_classification/android/lite-model_yamnet_classification_tflite_1.tflite")
MODEL_NAME = "yamnet.tflite"
SR = 16000
WIN = 15600   # 0.975 s, what the model expects
HOP = 7800    # ~0.49 s
# AudioSet classes: 24-32 singing / rapping / humming, 132 "Music", 133-276 instruments and genres
MUSIC_IDX = list(range(24, 33)) + list(range(132, 277))
# Warn when: >= 2 s with a clear music score (>= 0.2) or >= 4 s with a weaker one (>= 0.1).
# Calibrated on CC music (hip hop, pop with vocals, jazz) mixed under speech at -6..-24 dB and on 9.5 min
# of narration + game sound: every song with vocals is caught down to -24 dB, an instrumental beat down to
# -12 dB, and there were no false warnings. A quiet beat (-18 dB and below) under loud talking can slip through.
STRONG, WEAK = 0.2, 0.1
STRONG_SECONDS, WEAK_SECONDS = 2.0, 4.0

_local = threading.local()


def model_path(ws) -> Path:
    return Path(ws.root) / "models" / MODEL_NAME


def download_model(ws) -> Path | None:
    p = model_path(ws)
    if p.exists() and p.stat().st_size > 1_000_000:
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(MODEL_URL, p)
        return p
    except Exception:
        return None


def available(ws) -> bool:
    import importlib.util

    if importlib.util.find_spec("ai_edge_litert") is None:
        return False
    return model_path(ws).exists()


def _interpreter(path: Path):
    """One interpreter per thread (renders run in parallel)."""
    cache = getattr(_local, "it", None)
    if cache and cache[0] == str(path):
        return cache[1]
    from ai_edge_litert.interpreter import Interpreter

    it = Interpreter(model_path=str(path))
    it.allocate_tensors()
    _local.it = (str(path), it)
    return it


def labels(path: Path) -> list[str]:
    return zipfile.ZipFile(path).read("yamnet_label_list.txt").decode().splitlines()


def scores(path: Path, media: Path, start: float = 0, dur: float | None = None) -> np.ndarray:
    """Music score (0-1) for every ~0.49 s of the media."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + \
          ["-i", str(media), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
    if len(a) < SR // 2:
        return np.zeros(0)
    it = _interpreter(path)
    inp, out = it.get_input_details()[0]["index"], it.get_output_details()[0]["index"]
    res = []
    for i in range(0, max(1, len(a) - WIN + 1), HOP):
        fr = a[i:i + WIN]
        if len(fr) < WIN:
            fr = np.pad(fr, (0, WIN - len(fr)))
        it.set_tensor(inp, np.ascontiguousarray(fr, dtype=np.float32))
        it.invoke()
        res.append(float(it.get_tensor(out)[0][MUSIC_IDX].max()))
    return np.array(res)


def summarize(s: np.ndarray) -> dict:
    """Turn per-window scores into {'seconds', 'strong_seconds', 'peak', 'warn'}."""
    step = HOP / SR
    weak = float((s >= WEAK).sum()) * step if len(s) else 0.0
    strong = float((s >= STRONG).sum()) * step if len(s) else 0.0
    return {"seconds": round(weak, 1), "strong_seconds": round(strong, 1),
            "peak": round(float(s.max()), 2) if len(s) else 0.0,
            "warn": strong >= STRONG_SECONDS or weak >= WEAK_SECONDS}


def music_report(ws, media: Path) -> dict | None:
    """Music summary of a clip, or None when the detector is not installed."""
    if not available(ws):
        return None
    return summarize(scores(model_path(ws), media))
