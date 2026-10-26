from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import Field, model_validator
from .models_base import Model, uid
from .inserts import MotionInsert


class Fact(Model):
    id: str = Field(default_factory=lambda: uid("fact_"))
    claim: str = ""
    source: str = ""
    url: str = ""
    page: str = ""
    status: Literal["UNVERIFIED", "VERIFIED", "DISPUTED"] = "UNVERIFIED"
    note: str = ""


class Source(Model):
    id: str = Field(default_factory=lambda: uid("src_"))
    title: str
    provider: str = "custom"
    url: str = ""
    author: str = ""
    edition: str = ""
    identifier: str = ""
    text: str = ""
    pages: list[dict[str, Any]] = Field(default_factory=list)
    asset_id: str | None = None
    accessed_at: str = ""


class Asset(Model):
    id: str
    name: str
    kind: Literal["image", "video", "audio", "document"]
    filename: str
    mime: str
    sha256: str
    duration: float = 0
    width: int = 0
    height: int = 0
    thumbnail: str = ""
    source_url: str = ""
    author: str = ""
    license: str = ""
    license_url: str = ""
    attribution: str = ""
    prompt: str = ""
    provenance: dict[str, Any] = Field(default_factory=dict)


class Scene(Model):
    id: str = Field(default_factory=lambda: uid("scene_"))
    title: str = "Nowe ujęcie"
    narration: str = ""
    start: int = Field(default=0, ge=0)
    duration: int = Field(default=180, ge=1)
    timing: Literal["estimated", "measured"] = "estimated"
    mode: Literal["generate", "search", "upload", "library"] = "search"
    prompt: str = ""
    motion_prompt: str = ""
    search_query: str = ""
    animation: Literal["static", "zoom-in", "zoom-out", "pan-left", "pan-right"] = "zoom-in"
    asset_id: str | None = None
    voice_asset_id: str | None = None
    variants: list[str] = Field(default_factory=list)
    fact_ids: list[str] = Field(default_factory=list)
    role: Literal["literal", "illustration", "reconstruction"] = "illustration"
    locked: bool = False
    legacy: dict[str, Any] = Field(default_factory=dict)


class Track(Model):
    id: str
    name: str
    kind: Literal["video", "text", "audio"]
    role: Literal["picture", "overlay", "titles", "narration", "music", "effects"]
    locked: bool = False
    muted: bool = False


class Keyframe(Model):
    property: Literal["x", "y", "scale", "rotation", "opacity", "volume"]
    frame: int = Field(ge=0)
    value: float = Field(ge=-10000, le=10000)


class Clip(Model):
    id: str = Field(default_factory=lambda: uid("clip_"))
    track_id: str
    asset_id: str | None = None
    scene_id: str | None = None
    title: str = "Klip"
    text: str = ""
    start: int = Field(default=0, ge=0)
    duration: int = Field(default=180, ge=1)
    source_in: int = Field(default=0, ge=0)
    speed: float = Field(default=1, ge=.25, le=4)
    x: float = Field(default=0, ge=-2, le=2)
    y: float = Field(default=0, ge=-2, le=2)
    scale: float = Field(default=1, ge=.05, le=5)
    rotation: float = Field(default=0, ge=-360, le=360)
    opacity: float = Field(default=1, ge=0, le=1)
    volume: float = Field(default=1, ge=0, le=4)
    animation: Literal["static", "zoom-in", "zoom-out", "pan-left", "pan-right"] = "static"
    fade_in: int = Field(default=0, ge=0)
    fade_out: int = Field(default=0, ge=0)
    locked: bool = False
    keyframes: list[Keyframe] = Field(default_factory=list)


class Sequence(Model):
    fps_num: int = Field(default=30, ge=1, le=120)
    fps_den: int = Field(default=1, ge=1, le=1001)
    width: int = Field(default=1280, ge=144, le=3840, multiple_of=2)
    height: int = Field(default=720, ge=144, le=3840, multiple_of=2)
    tracks: list[Track] = Field(default_factory=lambda: [
        Track(id="v1", name="Obraz", kind="video", role="picture"),
        Track(id="v2", name="Nakładki", kind="video", role="overlay"),
        Track(id="t1", name="Napisy", kind="text", role="titles"),
        Track(id="a1", name="Lektor", kind="audio", role="narration"),
        Track(id="a2", name="Muzyka", kind="audio", role="music"),
        Track(id="a3", name="Efekty", kind="audio", role="effects"),
    ])
    clips: list[Clip] = Field(default_factory=list)


class Project(Model):
    schema_version: Literal["docos-studio/1"] = "docos-studio/1"
    id: str = Field(default_factory=lambda: uid("prj_"), pattern=r"^prj_[a-f0-9]{16}$")
    revision: int = Field(default=0, ge=0)
    title: str = Field(default="Nowy dokument", min_length=1, max_length=200)
    language: str = "pl"
    channel: str = "Mój kanał"
    niche: str = "Documentary"
    updated_at: str = ""
    demo: bool = False
    topics: list[dict[str, Any]] = Field(default_factory=list)
    topic_history: list[str] = Field(default_factory=list)
    facts: list[Fact] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    story: dict[str, str] = Field(default_factory=lambda: {
        "central_question": "", "hook": "", "signature_line": "", "payoff": "",
        "thesis": "", "complication": "", "counterpoint": "", "stakes_for_viewer": "",
        "open_question": "", "sting": "", "status": "DRAFT", "approved_hash": "",
    })
    scenes: list[Scene] = Field(default_factory=list)
    inserts: list[MotionInsert] = Field(default_factory=list, max_length=200)
    assets: list[Asset] = Field(default_factory=list)
    sequence: Sequence = Field(default_factory=Sequence)
    legacy: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def coherent(self):
        for name in ("facts", "sources", "scenes", "assets", "inserts"):
            ids = [x.id for x in getattr(self, name)]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Powtórzone identyfikatory: {name}")
        track_ids = [t.id for t in self.sequence.tracks]
        clip_ids = [c.id for c in self.sequence.clips]
        if len(set(track_ids)) != len(track_ids) or len(set(clip_ids)) != len(clip_ids):
            raise ValueError("Powtórzone identyfikatory na osi czasu")
        assets = {a.id: a for a in self.assets}
        for insert in self.inserts:
            if any(i not in assets or assets[i].kind != "image" for i in insert.image_ids):
                raise ValueError("Wstawka wymaga zdjęć z biblioteki projektu")
            if insert.rendered_asset_id and (insert.rendered_asset_id not in assets or assets[insert.rendered_asset_id].kind != "video"):
                raise ValueError("Wstawka wymaga istniejącego renderu wideo")
        facts = {f.id for f in self.facts}
        for scene in self.scenes:
            if not set(scene.fact_ids) <= facts:
                raise ValueError("Ujęcie odwołuje się do nieistniejącego faktu")
            if any(a and a not in assets for a in [scene.asset_id, scene.voice_asset_id, *scene.variants]):
                raise ValueError("Ujęcie odwołuje się do nieistniejącego materiału")
        tracks = {t.id: t for t in self.sequence.tracks}
        fps = self.sequence.fps_num / self.sequence.fps_den
        if fps < 1:
            raise ValueError("FPS musi wynosić co najmniej jeden")
        for clip in self.sequence.clips:
            if clip.track_id not in tracks:
                raise ValueError("Klip wymaga istniejącej ścieżki")
            if clip.asset_id and clip.asset_id not in assets:
                raise ValueError("Klip wymaga istniejącego materiału")
            if clip.start + clip.duration > fps * 21600:
                raise ValueError("Maksymalna długość sekwencji to sześć godzin")
            for k in clip.keyframes:
                bounds = {"x": (-2, 2), "y": (-2, 2), "scale": (.05, 5), "rotation": (-360, 360), "opacity": (0, 1), "volume": (0, 4)}
                if not bounds[k.property][0] <= k.value <= bounds[k.property][1] or k.frame > clip.duration:
                    raise ValueError("Keyframe poza zakresem klipu lub parametru")
            if clip.asset_id:
                a = assets[clip.asset_id]
                kind = tracks[clip.track_id].kind
                if kind == "audio" and a.kind not in ("audio", "video"):
                    raise ValueError("Na ścieżce audio umieść dźwięk")
                if kind == "video" and a.kind not in ("image", "video"):
                    raise ValueError("Na ścieżce obrazu umieść zdjęcie lub film")
                if a.duration and (clip.source_in + clip.duration * clip.speed) / fps > a.duration + 1 / fps:
                    raise ValueError("Zakres klipu przekracza długość materiału źródłowego")
        return self


def fps(project: Project) -> float:
    return project.sequence.fps_num / project.sequence.fps_den


def duration(project: Project) -> int:
    return max((c.start + c.duration for c in project.sequence.clips), default=0)


def from_docos(data: dict) -> Project:
    if data.get("schema_version") == "docos-studio/1":
        return Project.model_validate({k: v for k, v in data.items() if not k.startswith("_")})
    if not isinstance(data.get("beats"), list) or not isinstance(data.get("meta"), dict):
        raise ValueError("Oczekiwano projektu DocOS lub DocOS Studio")
    meta = data["meta"]
    p = Project(title=meta.get("title") or "Import DocOS", language=meta.get("language", "en"), legacy=data)
    for item in data.get("facts", []):
        status = item.get("status", "UNVERIFIED")
        p.facts.append(Fact(id=str(item.get("id") or uid("fact_")), claim=str(item.get("claim") or item.get("text") or ""),
                            source=str(item.get("source", "")), url=str(item.get("url", "")), note=str(item.get("note", "")),
                            status=status if status in ("VERIFIED", "DISPUTED") else "UNVERIFIED"))
    lock = data.get("story_lock", {})
    for k in p.story:
        if k in lock and isinstance(lock[k], str) and k not in ("status", "approved_hash"):
            p.story[k] = lock[k]
    # An imported approval is never silently granted to the new editing model.
    start = 0
    for beat in data["beats"]:
        narration = beat.get("narration", "")
        if not isinstance(narration, str):
            narration = str(narration)
        shots = beat.get("shots") or [{}]
        for index, shot in enumerate(shots):
            seconds = max(1, float(shot.get("dur") or 6))
            scene = Scene(title=str(shot.get("desc") or beat.get("name") or beat.get("id") or "Ujęcie")[:100],
                          narration=narration if index == 0 else "", start=start, duration=math.ceil(seconds * 30),
                          prompt=str(shot.get("prompt") or ""), search_query=str(shot.get("desc") or ""),
                          legacy={"beat_id": beat.get("id"), "shot": shot, "beat_narration": narration})
            p.scenes.append(scene)
            start += scene.duration
    return Project.model_validate(p.model_dump())
