"""Workspace layout and settings.

A workspace is one folder that holds everything the clipper makes:

    <workspace>/
        settings.json      app + pipeline settings
        streamers.json     who we clip, platform, clip rules, live watch flag
        src/               audio, transcripts, metadata and signals per source video
        candidates.json    best windows found by signals (input for the AI)
        candidates.md      the same, readable for an AI / human
        picks.json         chosen moments (output of pick)
        shorts/<id>/       one folder per Short: meta.json, v0.mp4, v1.mp4..., cover.jpg
        live/              live hunt buffer and cuts
        logs/              job logs
        fonts/, sounds/    copied at setup
"""
from __future__ import annotations

import json
import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
DEFAULT_WORKSPACE = Path(os.environ.get("CLIPPER_WORKSPACE", Path.home() / "gta-shorts"))

DEFAULT_SETTINGS: dict = {
    "setup_done": False,
    "ui_language": "pl",
    # Spoken language of sources we accept and of captions / hooks we write.
    "language": "en",
    "query": "GTA 6",
    "title_regex": r"GTA ?(6|VI)",
    # game name as Twitch / Kick report it (chapters, category) — decides which parts of a stream are GTA
    "game_regex": r"grand theft auto|\bgta\b",
    # words that give GTA away in speech, for YouTube streams whose title / description say nothing
    "topic_words": ["gta", "grand theft auto", "vice city", "leonida", "los santos", "rockstar"],
    "topic_min_hits": 1,
    "max_source_hours": 6,
    "within_hours": 72,
    # AI that picks moments: claude | codex | gemini | kimi | opencode | ollama | custom | none
    "ai": "claude",
    "ai_commands": {
        "claude": "claude -p --model claude-opus-5-5 --effort medium",   # Opus picks moments and writes hooks clearly better than Sonnet
        "codex": "codex exec -",
        "gemini": "gemini -p {prompt_text}",
        "kimi": "kimi --print -c {prompt_text}",
        "opencode": "opencode run {prompt_text}",
        "ollama": "ollama run llama3.1",
        "custom": "",
    },
    # free = no AI, smart = AI reads the best 30 windows, deep = AI reads whole transcripts
    "pick_mode": "smart",
    "shorts_per_run": 10,
    "max_per_source": 2,
    "candidates": 30,
    "skip_music": True,          # drop moments with background music before the AI sees them (Content ID)
    "min_len": 15,
    "max_len": 59,
    # Look
    "layout": "auto",            # auto | stack | bubble | full | facecrop
    "flip": False,               # cam below the game
    "style": "classic",
    "watermark": "",
    "accent": "#FFD400",
    "keyword_color": "#2BE36B",
    "punch_zooms": True,
    "cut_dead_air": True,
    "sfx": False,
    "censor_on_screen": True,
    "caption_engine": "pil",     # pil = drawn in code (default) | ass = burned by ffmpeg/libass | auto
    "workers": 3,
    "whisper_model": "small",
    "whisper_device": "auto",
    # Posting plan
    "post_every_min": 90,
    "post_first_at": "10:00",
    "autopilot": {"enabled": False, "time": "09:00", "count": 10, "days": [0, 1, 2, 3, 4, 5, 6]},
    "live": {"ratio": 3.0, "min_per_min": 30, "before": 25, "after": 10, "keep_minutes": 10, "mode": "smart"},
    "updates": {"auto_check": True, "last_check": 0, "available": False},
    "repo_issue_url": "https://github.com/krystiangaleczka-tech/Yt/issues/new",
}


class Workspace:
    def __init__(self, root: str | os.PathLike | None = None):
        self.root = Path(root or DEFAULT_WORKSPACE).expanduser().resolve()

    # folders -------------------------------------------------------------
    @property
    def src(self) -> Path: return self.root / "src"
    @property
    def shorts(self) -> Path: return self.root / "shorts"
    @property
    def live(self) -> Path: return self.root / "live"
    @property
    def logs(self) -> Path: return self.root / "logs"
    @property
    def fonts(self) -> Path: return self.root / "fonts"
    @property
    def sounds(self) -> Path: return self.root / "sounds"
    @property
    def peek(self) -> Path: return self.root / "peek"

    def ensure(self) -> "Workspace":
        for p in (self.root, self.src, self.shorts, self.live, self.logs, self.fonts, self.sounds, self.peek):
            p.mkdir(parents=True, exist_ok=True)
        return self

    # json files ------------------------------------------------------------
    def path(self, name: str) -> Path:
        return self.root / name

    def read_json(self, name: str, default):
        return read_json(self.path(name), default)

    def write_json(self, name: str, data) -> None:
        write_json(self.path(name), data)

    # settings --------------------------------------------------------------
    def settings(self) -> dict:
        s = json.loads(json.dumps(DEFAULT_SETTINGS))
        _deep_update(s, self.read_json("settings.json", {}))
        # env knobs override (handy for weak PCs / quick tests)
        if os.environ.get("CLIPPER_WORKERS"):
            s["workers"] = int(os.environ["CLIPPER_WORKERS"])
        if os.environ.get("CLIPPER_LAYOUT"):
            s["layout"] = os.environ["CLIPPER_LAYOUT"]
        if os.environ.get("CLIPPER_STYLE"):
            s["style"] = os.environ["CLIPPER_STYLE"]
        if os.environ.get("PICK_MODE"):
            s["pick_mode"] = os.environ["PICK_MODE"]
        return s

    def save_settings(self, patch: dict) -> dict:
        cur = self.read_json("settings.json", {})
        _deep_update(cur, patch)
        self.write_json("settings.json", cur)
        return self.settings()

    def streamers(self) -> list[dict]:
        return self.read_json("streamers.json", [])

    def save_streamers(self, items: list[dict]) -> None:
        self.write_json("streamers.json", items)


def _deep_update(dst: dict, src: dict) -> None:
    for k, v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


def read_json(path: Path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
