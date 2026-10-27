from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import Field, model_validator
from .models_base import Model, uid
from .inserts import MotionInsert
from .development import Development, migrate_ideas
from .workspace_models import ResourceLink


class Fact(Model):
    id: str = Field(default_factory=lambda: uid("fact_"))
    claim: str = ""
    source: str = ""
    url: str = ""
    page: str = ""
    status: Literal["UNVERIFIED", "VERIFIED", "DISPUTED", "DRAMATIZATION"] = "UNVERIFIED"
    note: str = ""
    source_id: str | None = None
    quote: str = ""
    checked_at: str = ""
    provenance: dict[str, Any] = Field(default_factory=dict)


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
    metadata: dict[str, Any] = Field(default_factory=dict)
    original_asset_id: str | None = None

    @model_validator(mode="after")
    def readable_pages(self):
        if len(self.pages)>2000: raise ValueError("Maksymalnie dwa tysiące stron źródła")
        for page in self.pages:
            if not isinstance(page.get("page"),(str,int)) or not isinstance(page.get("text"),str): raise ValueError("Strona wymaga lokalizacji page i tekstu text")
            page["page"]=str(page["page"])
        return self


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
    private: bool = False

    @model_validator(mode="after")
    def local_names(self):
        for value in (self.filename,self.thumbnail):
            if value and ("/" in value or "\\" in value or value in (".","..")):
                raise ValueError("Materiał wymaga lokalnej nazwy pliku bez ścieżki")
        return self


class VoiceSentence(Model):
    id: str = Field(default_factory=lambda: uid("sent_"))
    text: str
    spoken_text: str = ""
    asset_id: str | None = None
    variants: list[str] = Field(default_factory=list)
    input_hash: str = ""
    duration: float = Field(default=0, ge=0)


class Beat(Model):
    id: str = Field(default_factory=lambda: uid("beat_"))
    title: str = "Nowy fragment"
    planning_ref: str = ""
    planning_chapter_id: str = ""
    planning_seconds: int = Field(default=0, ge=0, le=3600)
    planning_question: str = ""
    retention_plan: str = ""
    evidence_needed: str = ""
    chapter: str = "Historia"
    goal: str = ""
    narration: str = ""
    turn: str = ""
    energy: int = Field(default=5, ge=1, le=10)
    dynamics: str = "STORY"
    typology: str = "EVIDENCE"
    chaos: str = "NONE"
    fact_ids: list[str] = Field(default_factory=list)


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
    beat_id: str | None = None
    lock_narration: bool = False
    lock_timing: bool = False
    lock_media: bool = False
    voice_input_hash: str = ""
    voice_profile: dict[str, Any] = Field(default_factory=dict)
    sentences: list[VoiceSentence] = Field(default_factory=list)
    words: list[dict[str, Any]] = Field(default_factory=list)
    alignment_hash: str = ""
    template: str = "media"
    parameters: dict[str, Any] = Field(default_factory=dict)
    asset_ids: list[str] = Field(default_factory=list)
    generation: dict[str, Any] = Field(default_factory=dict)
    script_input_hash: str = ""


class Track(Model):
    id: str
    name: str
    kind: Literal["video", "text", "audio"]
    role: Literal["picture", "overlay", "titles", "narration", "music", "effects"]
    locked: bool = False
    muted: bool = False
    solo: bool = False


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
    group_id: str = ""
    template: str = "media"
    parameters: dict[str, Any] = Field(default_factory=dict)
    asset_ids: list[str] = Field(default_factory=list)
    fact_ids: list[str] = Field(default_factory=list)
    transition: Literal["cut", "dissolve", "fade-black", "wipe-left", "wipe-right", "slide-left", "slide-right", "zoom"] = "cut"
    transition_duration: int = Field(default=0, ge=0)
    crop: dict[str, float] = Field(default_factory=dict)


class Sequence(Model):
    fps_num: int = Field(default=30, ge=1, le=120000)
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
    ducking: bool = False
    ducking_gain: float = Field(default=.25, ge=0, le=1)


class Project(Model):
    schema_version: Literal["docos-studio/2"] = "docos-studio/2"
    id: str = Field(default_factory=lambda: uid("prj_"), pattern=r"^prj_[a-f0-9]{16}$")
    revision: int = Field(default=0, ge=0)
    title: str = Field(default="Nowy dokument", min_length=1, max_length=200)
    language: str = "pl"
    channel: str = "Mój kanał"
    niche: str = "Documentary"
    updated_at: str = ""
    demo: bool = False
    topics: list[dict[str, Any]] = Field(default_factory=list)
    development: Development = Field(default_factory=Development)
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
    channel_id: str = ""
    channel_profile: dict[str, Any] = Field(default_factory=dict)
    category_id: str = ""
    category_profile: dict[str, Any] = Field(default_factory=dict)
    film_format: str = ""
    workspace_snapshot: dict[str, Any] = Field(default_factory=dict)
    resource_links: list[ResourceLink] = Field(default_factory=list)
    archived: bool = False
    published: bool = False
    beats: list[Beat] = Field(default_factory=list)
    voice_profile: dict[str, Any] = Field(default_factory=dict)
    pronunciation: dict[str, str] = Field(default_factory=dict)
    budget: dict[str, float] = Field(default_factory=lambda: {"max_cost": 0, "max_jobs": 20, "max_seconds": 3600})
    accepted_warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def migrate_version_one(cls,value):
        if isinstance(value,dict):
            value=migrate_ideas(value)
            if value.get("schema_version")=="docos-studio/1":return {**value,"schema_version":"docos-studio/2"}
        return value

    @model_validator(mode="after")
    def coherent(self):
        from .templates import validate_parameters
        for key,value in self.budget.items():
            if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
                raise ValueError("Limity budżetu muszą być nieujemnymi liczbami")
        if not 1<=self.budget.get("max_jobs",20)<=100 or not 1<=self.budget.get("max_seconds",3600)<=21600:
            raise ValueError("Limit zadań: 1–100; limit czasu: 1–21600 sekund")
        for name in ("facts", "sources", "scenes", "assets", "beats", "inserts"):
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
        if any(not set(section.fact_ids)<=facts for idea in self.development.ideas for story in idea.stories for chapter in story.chapters for section in chapter.sections):
            raise ValueError("Plan rozdziałów wskazuje nieistniejący fakt")
        beats = {b.id for b in self.beats}
        sources={s.id for s in self.sources}
        if any(not set(b.fact_ids)<=facts for b in self.beats): raise ValueError("Fragment odwołuje się do nieistniejącego faktu")
        if any(f.source_id and f.source_id not in sources for f in self.facts): raise ValueError("Fakt odwołuje się do nieistniejącego źródła")
        if any(a and a not in assets for s in self.sources for a in (s.asset_id,s.original_asset_id)): raise ValueError("Dokument odwołuje się do nieistniejącego pliku")
        for scene in self.scenes:
            validate_parameters(scene.template, scene.parameters)
            from .freshness import image_config
            image_config(scene)
            if not set(scene.fact_ids) <= facts:
                raise ValueError("Ujęcie odwołuje się do nieistniejącego faktu")
            if scene.beat_id and scene.beat_id not in beats:
                raise ValueError("Ujęcie odwołuje się do nieistniejącego fragmentu")
            if any(a and a not in assets for a in [scene.asset_id, scene.voice_asset_id, *scene.variants, *scene.asset_ids]):
                raise ValueError("Ujęcie odwołuje się do nieistniejącego materiału")
            for sentence in scene.sentences:
                if any(a and a not in assets for a in [sentence.asset_id, *sentence.variants]):
                    raise ValueError("Zdanie odwołuje się do nieistniejącego nagrania")
            if scene.voice_asset_id and assets[scene.voice_asset_id].kind!="audio": raise ValueError("Lektor wymaga nagrania audio")
            if scene.words:
                if not scene.voice_asset_id: raise ValueError("Znaczniki wymagają powiązanego nagrania")
                from .audio import validate_words
                validate_words(scene.words,assets[scene.voice_asset_id].duration)
        tracks = {t.id: t for t in self.sequence.tracks}
        fps = self.sequence.fps_num / self.sequence.fps_den
        if not 1<=fps<=120:
            raise ValueError("FPS musi mieścić się w zakresie 1–120")
        for clip in self.sequence.clips:
            validate_parameters(clip.template, clip.parameters)
            if clip.scene_id and clip.scene_id not in {s.id for s in self.scenes}: raise ValueError("Klip wskazuje nieistniejące ujęcie")
            if clip.crop:
                if set(clip.crop)!={"x","y","width","height"} or any(not math.isfinite(v) for v in clip.crop.values()):
                    raise ValueError("Kadrowanie wymaga x/y/width/height")
                x,y,w,h=(clip.crop[k] for k in ("x","y","width","height"))
                if min(x,y)<0 or min(w,h)<=0 or x+w>1 or y+h>1:
                    raise ValueError("Kadrowanie musi mieścić się w obrazie")
            if clip.track_id not in tracks:
                raise ValueError("Klip wymaga istniejącej ścieżki")
            if clip.asset_id and clip.asset_id not in assets:
                raise ValueError("Klip wymaga istniejącego materiału")
            if any(a not in assets for a in clip.asset_ids) or not set(clip.fact_ids) <= facts:
                raise ValueError("Klip wskazuje nieistniejący materiał lub fakt")
            if clip.transition_duration > clip.duration:
                raise ValueError("Przejście nie może być dłuższe od klipu")
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
                if kind == "video" and a.kind not in ("image", "video") and clip.template not in ("waveform", "spectrogram"):
                    raise ValueError("Na ścieżce obrazu umieść zdjęcie lub film")
                if a.duration and (clip.source_in + clip.duration * clip.speed) / fps > a.duration + 1 / fps:
                    raise ValueError("Zakres klipu przekracza długość materiału źródłowego")
        return self


def fps(project: Project) -> float:
    return project.sequence.fps_num / project.sequence.fps_den


def duration(project: Project) -> int:
    return max((c.start + c.duration for c in project.sequence.clips), default=0)


def from_docos(data: dict) -> Project:
    if data.get("schema_version") in ("docos-studio/1","docos-studio/2"):
        return Project.model_validate({k: v for k, v in data.items() if not k.startswith("_")})
    if not isinstance(data.get("beats"), list) or not isinstance(data.get("meta"), dict):
        raise ValueError("Oczekiwano projektu DocOS lub DocOS Studio")
    meta = data["meta"]
    p = Project(title=meta.get("title") or "Import DocOS", language=meta.get("language", "en"), legacy=data)
    for item in data.get("facts", []):
        status = item.get("status", "UNVERIFIED")
        p.facts.append(Fact(id=str(item.get("id") or uid("fact_")), claim=str(item.get("claim") or item.get("text") or ""),
                            source=str(item.get("source", "")), url=str(item.get("url", "")), note=str(item.get("note", "")),
                            status=status if status in ("VERIFIED", "DISPUTED", "DRAMATIZATION") else "UNVERIFIED"))
    lock = data.get("story_lock", {})
    for k in p.story:
        if k in lock and isinstance(lock[k], str) and k not in ("status", "approved_hash"):
            p.story[k] = lock[k]
    # An imported approval is never silently granted to the new editing model.
    start = 0
    for beat in data["beats"]:
        from .templates import legacy_parameters
        bank = {f.id for f in p.facts}
        beat_model = Beat(id=str(beat.get("id") or uid("beat_")), title=str(beat.get("scene_desc") or beat.get("name") or beat.get("id") or "Fragment"), chapter=str(beat.get("chapter") or "Historia"), goal=str(beat.get("goal", "")), turn=str(beat.get("turn", "")), dynamics=str(beat.get("dynamic", "STORY")), typology=str(beat.get("typology", "EVIDENCE")), chaos=str(beat.get("chaos", "NONE")), fact_ids=[str(f) for f in beat.get("facts_used", beat.get("facts", [])) if str(f) in bank], narration=str(beat.get("narration", "")))
        from docos.docos import DYNAMICS
        beat_model.energy = int(DYNAMICS.get(beat_model.dynamics, (5,))[0])
        p.beats.append(beat_model)
        narration = beat.get("narration", "")
        if not isinstance(narration, str):
            narration = str(narration)
        shots = beat.get("shots") or [{}]
        for index, shot in enumerate(shots):
            template, parameters = legacy_parameters(shot)
            if shot.get("asset")=="AI_OBRAZ" and not parameters.get("pending_files"):
                parameters["pending_files"]=[f"{beat_model.id}_wiz{int(shot.get('n',index+1)):02d}.png"]
            seconds = max(1, float(shot.get("dur") or 6))
            scene = Scene(title=str(shot.get("desc") or beat.get("name") or beat.get("id") or "Ujęcie")[:100],
                          narration=narration if index == 0 else "", start=start, duration=math.ceil(seconds * 30),
                          prompt=str(shot.get("prompt") or ""), search_query=str(shot.get("desc") or ""),
                          beat_id=beat_model.id, fact_ids=beat_model.fact_ids, template=template, parameters=parameters,
                          legacy={"beat_id": beat.get("id"), "shot": shot, "beat_narration": narration})
            p.scenes.append(scene)
            start += scene.duration
    return Project.model_validate(p.model_dump())


def import_content(data: dict) -> Project:
    """Import textual project data without granting filesystem access or approval."""
    import copy
    import re
    data=copy.deepcopy(data)
    if data.get("schema_version") in ("docos-studio/1","docos-studio/2"):
        # Metadata may preserve edit decisions, but every file is resolved under
        # the NEW project directory. Invalid/untrusted path records are dropped.
        data["assets"]=[a for a in data.get("assets",[]) if re.fullmatch(r"asset_[a-f0-9]{20}",str(a.get("id",""))) and re.fullmatch(r"[a-f0-9]{64}",str(a.get("sha256",""))) and str(a.get("filename","")) not in ("",".","..") and "/" not in str(a.get("filename","")) and "\\" not in str(a.get("filename",""))]
        known={a["id"] for a in data["assets"]}
        for item in data.get("inserts",[]):
            item["image_ids"]=[];item["rendered_asset_id"]=None;item["rendered_signature"]=""
        for asset in data["assets"]: asset["thumbnail"]=""
        for scene in data.get("scenes",[]):
            for key in ("asset_id","voice_asset_id"): scene[key]=scene.get(key) if scene.get(key) in known else None
            if not scene.get("voice_asset_id"):scene["words"]=[];scene["alignment_hash"]=""
            for key in ("variants","asset_ids"): scene[key]=[a for a in scene.get(key,[]) if a in known]
            for sentence in scene.get("sentences",[]):
                sentence["asset_id"]=sentence.get("asset_id") if sentence.get("asset_id") in known else None
                sentence["variants"]=[a for a in sentence.get("variants",[]) if a in known]
        for source in data.get("sources",[]):
            for key in ("asset_id","original_asset_id"): source[key]=source.get(key) if source.get(key) in known else None
        for clip in data.get("sequence",{}).get("clips",[]):
            clip["asset_id"]=clip.get("asset_id") if clip.get("asset_id") in known else None
            clip["asset_ids"]=[a for a in clip.get("asset_ids",[]) if a in known]
    project=from_docos(data);project.id=uid("prj_");project.revision=0
    if data.get("schema_version") not in ("docos-studio/1","docos-studio/2"):
        project.sequence.clips=[Clip(track_id="v1",scene_id=s.id,asset_id=s.asset_id,title=s.title,start=s.start,duration=s.duration,template=s.template,parameters=s.parameters,asset_ids=s.asset_ids,fact_ids=s.fact_ids,animation=s.animation) for s in project.scenes]
    project.story["status"]="DRAFT";project.story["approved_hash"]=""
    return project
