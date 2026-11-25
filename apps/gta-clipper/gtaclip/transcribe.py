"""Local speech-to-text with word timings (faster-whisper).

Audio is decoded by ffmpeg in 10-minute chunks, so 6-hour streams do not need
gigabytes of RAM. Nothing leaves the PC.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from .config import write_json
from .util import hms, log, media_info

SR = 16000
CHUNK = 600  # seconds

_MODEL = None
_MODEL_KEY = None


def _model(name: str = "small", device: str = "auto"):
    global _MODEL, _MODEL_KEY
    from faster_whisper import WhisperModel  # heavy import, only when needed

    key = (name, device)
    if _MODEL is not None and _MODEL_KEY == key:
        return _MODEL
    tries = [("cuda", "float16"), ("cpu", "int8")] if device == "auto" else [(device, "int8" if device == "cpu" else "float16")]
    last = None
    for dev, ct in tries:
        try:
            _MODEL = WhisperModel(name, device=dev, compute_type=ct)
            _MODEL_KEY = key
            return _MODEL
        except Exception as e:  # no CUDA etc.
            last = e
    raise RuntimeError(f"Nie udało się wczytać modelu Whisper: {last}")


def _decode(path: Path, start: float, dur: float):
    import numpy as np

    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(path),
           "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def transcribe(audio: Path, out_base: Path, language: str | None = None, model: str = "small",
               device: str = "auto", start: float = 0.0, end: float | None = None) -> dict:
    """Write <out_base>.json (segments + words) and <out_base>.txt; return the json dict.

    Times are absolute in the source (start offset added)."""
    audio = Path(audio)
    total = media_info(audio)["duration"]
    end = min(end or total, total)
    m = _model(model, device)
    segments, detected = [], None
    t = start
    while t < end - 0.5:
        dur = min(CHUNK, end - t)
        pcm = _decode(audio, t, dur)
        if len(pcm) < SR // 2:
            break
        segs, info = m.transcribe(pcm, language=language, vad_filter=True, word_timestamps=True,
                                  condition_on_previous_text=False)
        detected = detected or info.language
        for s in segs:
            words = [{"w": w.word.strip(), "s": round(w.start + t, 2), "e": round(w.end + t, 2),
                      "p": round(w.probability, 2)} for w in (s.words or []) if w.word.strip()]
            segments.append({"start": round(s.start + t, 2), "end": round(s.end + t, 2),
                             "text": s.text.strip(), "words": words})
        log(f"  transkrypcja {hms(t + dur)} / {hms(end)}")
        t += dur
    data = {"language": detected or language, "start": start, "end": end, "segments": segments}
    write_json(Path(str(out_base) + ".json"), data)
    with open(str(out_base) + ".txt", "w", encoding="utf-8") as f:
        for s in segments:
            f.write(f"[{hms(s['start'])}] {s['text']}\n")
    return data


def detect_language(audio: Path, model: str = "small", device: str = "auto", at: float = 60.0) -> str | None:
    """Quick language check on 30 s of audio."""
    m = _model(model, device)
    total = media_info(audio)["duration"]
    at = min(at, max(0.0, total - 30))
    pcm = _decode(Path(audio), at, 30)
    if len(pcm) < SR:
        return None
    _, info = m.transcribe(pcm, vad_filter=True)
    return info.language


def words_between(tr: dict, start: float, end: float) -> list[dict]:
    out = []
    for s in tr.get("segments", []):
        if s["end"] < start or s["start"] > end:
            continue
        for w in s.get("words", []):
            if w["s"] >= start - 0.05 and w["e"] <= end + 0.3:
                out.append(dict(w))
    return out


def text_between(tr: dict, start: float, end: float, stamps: bool = True) -> str:
    lines = []
    for s in tr.get("segments", []):
        if s["end"] < start or s["start"] > end:
            continue
        lines.append(f"[{hms(s['start'])}] {s['text']}" if stamps else s["text"])
    return "\n".join(lines) if stamps else " ".join(lines)
