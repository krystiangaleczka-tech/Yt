"""2D animation production: channel-scoped cast/location banks and a reviewable scene board.

Characters and locations belong to exactly one channel. A film may only reference the bank of
its own channel, so the cast of one series never leaks into another.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps
from pydantic import Field, model_validator

from .models_base import Model, uid

ProductionMode = Literal["documentary", "animation_2d", "broll"]
CHANNEL_ID = re.compile(r"channel_[a-f0-9]{16}")
MEDIA_FILE = re.compile(r"[a-f0-9]{64}\.(png|webp|jpg)")
IMAGE_TYPES = {"PNG": ("png", "image/png"), "WEBP": ("webp", "image/webp"), "JPEG": ("jpg", "image/jpeg")}
MAX_IMAGE = 40 * 1024 * 1024
AUDIO_FILE = re.compile(r"[a-f0-9]{64}\.(wav|mp3|ogg|m4a|flac)")
AUDIO_TYPES = {"wav": "audio/wav", "mp3": "audio/mpeg", "ogg": "audio/ogg", "m4a": "audio/mp4", "flac": "audio/flac"}
MAX_AUDIO = 80 * 1024 * 1024


class CastImage(Model):
    file: str = Field(pattern=MEDIA_FILE.pattern)
    width: int = Field(ge=1, le=16384)
    height: int = Field(ge=1, le=16384)
    alpha: bool = False


class Pose(Model):
    id: str = Field(default_factory=lambda: uid("pose_"), pattern=r"^pose_[a-f0-9]{16}$")
    name: str = Field(min_length=1, max_length=80)
    view: Literal["front", "three_quarter", "side", "back"] = "front"
    image: CastImage
    tags: list[str] = Field(default_factory=list, max_length=20)
    # Outfit shown in this drawing; empty = the character's base look.
    costume_id: str = Field(default="", pattern=r"^(item_[a-f0-9]{16})?$")


class VoiceSettings(Model):
    provider: Literal["", "elevenlabs", "local"] = ""
    voice_id: str = Field(default="", max_length=200)
    notes: str = Field(default="", max_length=1000)


class Character(Model):
    id: str = Field(default_factory=lambda: uid("chr_"), pattern=r"^chr_[a-f0-9]{16}$")
    revision: int = 0
    channel_id: str = Field(pattern=CHANNEL_ID.pattern)
    name: str = Field(min_length=1, max_length=80)
    role: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=3000)
    personality: str = Field(default="", max_length=2000)
    goal: str = Field(default="", max_length=1000)
    signature: str = Field(default="", max_length=500)
    color: str = Field(default="#f2b866", pattern=r"^#[a-fA-F0-9]{6}$")
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    poses: list[Pose] = Field(default_factory=list, max_length=200)
    default_pose_id: str = ""
    archived: bool = False
    updated_at: str = ""

    @model_validator(mode="after")
    def coherent(self):
        ids = [p.id for p in self.poses]
        if len(ids) != len(set(ids)):
            raise ValueError("Powtórzone pozy postaci")
        if self.default_pose_id and self.default_pose_id not in ids:
            raise ValueError("Domyślna poza nie należy do postaci")
        return self


class Region(Model):
    """Named part of a background (window, doorway, mirror): elements assigned to it are clipped to it."""
    id: str = Field(default_factory=lambda: uid("reg_"), pattern=r"^reg_[a-f0-9]{16}$")
    name: str = Field(min_length=1, max_length=60)
    x0: float = Field(ge=0, le=1)
    y0: float = Field(ge=0, le=1)
    x1: float = Field(ge=0, le=1)
    y1: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.x1 - self.x0 < .01 or self.y1 - self.y0 < .01:
            raise ValueError("Obszar musi mieć dodatnią szerokość i wysokość")
        return self


class LocationState(Model):
    id: str = Field(default_factory=lambda: uid("lst_"), pattern=r"^lst_[a-f0-9]{16}$")
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=1000)
    time_of_day: Literal["", "day", "dusk", "night"] = ""
    image: CastImage | None = None
    # Optional transparent layer drawn in front of the characters (2.5D depth, parallax).
    foreground: CastImage | None = None
    # Where feet touch the floor (fraction of frame height); lets the reviewer spot floating characters.
    floor_y: float | None = Field(default=None, ge=0, le=1)
    regions: list[Region] = Field(default_factory=list, max_length=20)


class Location(Model):
    id: str = Field(default_factory=lambda: uid("loc_"), pattern=r"^loc_[a-f0-9]{16}$")
    revision: int = 0
    channel_id: str = Field(pattern=CHANNEL_ID.pattern)
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=3000)
    states: list[LocationState] = Field(default_factory=list, max_length=50)
    archived: bool = False
    updated_at: str = ""

    @model_validator(mode="after")
    def coherent(self):
        ids = [s.id for s in self.states]
        if len(ids) != len(set(ids)):
            raise ValueError("Powtórzone stany lokacji")
        return self


class ItemVariant(Model):
    id: str = Field(default_factory=lambda: uid("var_"), pattern=r"^var_[a-f0-9]{16}$")
    name: str = Field(min_length=1, max_length=80)
    image: CastImage


class Item(Model):
    """Reusable prop, costume or overlay (cracks, stains, light) of one channel."""
    id: str = Field(default_factory=lambda: uid("item_"), pattern=r"^item_[a-f0-9]{16}$")
    revision: int = 0
    channel_id: str = Field(pattern=CHANNEL_ID.pattern)
    category: Literal["prop", "costume", "overlay"] = "prop"
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=2000)
    character_ids: list[str] = Field(default_factory=list, max_length=20)
    variants: list[ItemVariant] = Field(default_factory=list, max_length=50)
    tags: list[str] = Field(default_factory=list, max_length=20)
    archived: bool = False
    updated_at: str = ""

    @model_validator(mode="after")
    def coherent(self):
        ids = [v.id for v in self.variants]
        if len(ids) != len(set(ids)):
            raise ValueError("Powtórzone warianty")
        if self.character_ids and self.category != "costume":
            raise ValueError("Postacie przypisuje się tylko do kostiumów")
        return self


class Sound(Model):
    """Sound effect, ambience loop or music track of one channel, with its licence."""
    id: str = Field(default_factory=lambda: uid("snd_"), pattern=r"^snd_[a-f0-9]{16}$")
    revision: int = 0
    channel_id: str = Field(pattern=CHANNEL_ID.pattern)
    kind: Literal["sfx", "ambience", "music"] = "sfx"
    name: str = Field(min_length=1, max_length=80)
    file: str = Field(pattern=AUDIO_FILE.pattern)
    duration: float = Field(default=0, ge=0, le=7200)
    volume: float = Field(default=1, ge=0, le=2)
    source_url: str = Field(default="", max_length=500)
    author: str = Field(default="", max_length=200)
    license: str = Field(default="", max_length=200)
    attribution: str = Field(default="", max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=20)
    archived: bool = False
    updated_at: str = ""


class SoundCue(Model):
    """Effect or ambience inside one scene. Ambience loops through the whole scene."""
    sound_id: str = Field(pattern=r"^snd_[a-f0-9]{16}$")
    at: float = Field(default=0, ge=0, le=1)
    volume: float = Field(default=1, ge=0, le=2)


class MusicCue(Model):
    """Music spanning a range of scenes in story order; ducked under dialogue."""
    id: str = Field(default_factory=lambda: uid("music_"), pattern=r"^music_[a-f0-9]{16}$")
    sound_id: str = Field(pattern=r"^snd_[a-f0-9]{16}$")
    from_scene_id: str = Field(pattern=r"^stage_[a-f0-9]{16}$")
    to_scene_id: str = Field(pattern=r"^stage_[a-f0-9]{16}$")
    volume: float = Field(default=.35, ge=0, le=2)
    offset: float = Field(default=0, ge=0, le=7200)


class StageProp(Model):
    item_id: str = Field(pattern=r"^item_[a-f0-9]{16}$")
    variant_id: str = ""
    x: float = Field(default=.5, ge=0, le=1)
    y: float = Field(default=.5, ge=0, le=1)
    scale: float = Field(default=.2, ge=.02, le=2)
    rotation: float = Field(default=0, ge=-180, le=180)
    layer: Literal["behind", "front"] = "behind"
    motion: Literal["none", "appear", "fade_in"] = "none"
    at: float = Field(default=.5, ge=0, le=1)  # moment of appear / fade as a fraction of the scene
    region_id: str = Field(default="", pattern=r"^(reg_[a-f0-9]{16})?$")


class StageCharacter(Model):
    character_id: str = Field(pattern=r"^chr_[a-f0-9]{16}$")
    pose_id: str = ""
    x: float = Field(default=.5, ge=0, le=1)
    y: float = Field(default=.92, ge=0, le=1.6)  # feet line; below 1 = cropped by the frame bottom
    scale: float = Field(default=.6, ge=.05, le=2)
    flip: bool = False
    motion: Literal["idle", "still", "enter_left", "enter_right", "exit_left", "exit_right"] = "idle"
    costume_id: str = Field(default="", pattern=r"^(item_[a-f0-9]{16})?$")
    region_id: str = Field(default="", pattern=r"^(reg_[a-f0-9]{16})?$")


class DialogueLine(Model):
    id: str = Field(default_factory=lambda: uid("line_"), pattern=r"^line_[a-f0-9]{16}$")
    speaker: str = Field(default="narrator", max_length=40)
    text: str = Field(default="", max_length=2000)
    direction: str = Field(default="", max_length=300)


class SceneSound(Model):
    ambience: str = Field(default="", max_length=500)
    music: str = Field(default="", max_length=500)
    sfx: list[str] = Field(default_factory=list, max_length=30)


class SceneMotion(Model):
    camera: Literal["static", "push_in", "pull_out", "pan_left", "pan_right", "shake"] = "static"
    strength: float = Field(default=.5, ge=0, le=1)
    # Framing: close-ups crop the frame (zoom around a focus point); characters keep their scale.
    zoom: float = Field(default=1, ge=1, le=4)
    focus_x: float = Field(default=.5, ge=0, le=1)
    focus_y: float = Field(default=.5, ge=0, le=1)


class Review(Model):
    status: Literal["approved", "rework"]
    note: str = Field(default="", max_length=2000)
    tags: list[str] = Field(default_factory=list, max_length=10)
    at: str = ""


REVIEW_TAGS = ("Kadr", "Postać/poza", "Tło", "Dialog", "Dźwięk", "Tempo")


class StageScene(Model):
    id: str = Field(default_factory=lambda: uid("stage_"), pattern=r"^stage_[a-f0-9]{16}$")
    number: int = Field(default=1, ge=1, le=9999)
    beat_id: str = Field(default="", pattern=r"^(beat_[a-f0-9]{16})?$")
    title: str = Field(default="Nowa scena", min_length=1, max_length=200)
    story_time: str = Field(default="", max_length=60)
    location_id: str = ""
    location_state_id: str = ""
    characters: list[StageCharacter] = Field(default_factory=list, max_length=8)
    props: list[StageProp] = Field(default_factory=list, max_length=20)
    action: str = Field(default="", max_length=3000)
    camera: str = Field(default="", max_length=300)
    dialogue: list[DialogueLine] = Field(default_factory=list, max_length=40)
    sound: SceneSound = Field(default_factory=SceneSound)
    audio: list[SoundCue] = Field(default_factory=list, max_length=20)
    motion: SceneMotion = Field(default_factory=SceneMotion)
    seconds: float = Field(default=6, ge=.5, le=600)
    status: Literal["draft", "review", "approved", "rework"] = "draft"
    reviews: list[Review] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def unique_lines(self):
        ids = [line.id for line in self.dialogue]
        if len(ids) != len(set(ids)):
            raise ValueError("Powtórzone kwestie w scenie")
        return self


CONTENT_FIELDS = ("title", "story_time", "location_id", "location_state_id", "characters", "props", "action", "camera", "motion", "dialogue", "sound", "audio", "seconds")
STAGING_RULES = """Staging rules (a reviewer checks them): feet stand on the state's floor_y unless the character is cropped by the frame bottom (y > 1) or by a region.
Anyone seen through a window, doorway or mirror gets that region_id: they are clipped to it, keep a realistic scale similar to the other characters (scale 0.5-0.7)
and usually show from the waist or chest up (their feet line far below the region's bottom edge). Never shrink a person to fit a whole body inside a window.
Close-ups and medium shots are CAMERA framing (motion.zoom with focus_x/focus_y on the subject), never a bigger character:
a character keeps the same scale as in the other scenes of the same location, standing on the floor line.
Cracks, stains and reflections on glass get the window's region_id so they never spill onto the wall."""
SCHEMA_HINT = """characters: [{"character_id","pose_id","x" 0-1,"y" feet line (0-1.6, >1 = cropped by frame bottom),"scale" (height as a fraction of the frame),"flip","region_id" (optional, clips to a state region),"motion": "idle"|"still"|"enter_left"|"enter_right"|"exit_left"|"exit_right"}];
props: [{"item_id","variant_id","x","y" centre,"scale","rotation","layer": "behind"|"front","motion": "none"|"appear"|"fade_in","at" 0-1,"region_id" (optional clip)}] — props and overlays persist between scenes until the story removes them;
audio: [{"sound_id" (sfx or ambience from the bank),"at" 0-1 moment for effects,"volume" 0-2}];
motion: {"camera": "static"|"push_in"|"pull_out"|"pan_left"|"pan_right"|"shake", "strength" 0-1, "zoom" 1-4 (framing: 1 wide, 1.6 medium, 2.2 close-up), "focus_x","focus_y" 0-1 (centre of the framing)}; dialogue: [{"speaker","text","direction"}]; sound: {"ambience","music","sfx":[]}."""
# Organisation, not content: moving a scene between beats does not reopen its review.
SCENE_FIELDS = CONTENT_FIELDS + ("beat_id",)


def read_image(content: bytes) -> tuple[bytes, CastImage, str]:
    if len(content) > MAX_IMAGE:
        raise ValueError("Obraz przekracza 40 MB")
    try:
        with Image.open(io.BytesIO(content)) as im:
            im.verify()
        with Image.open(io.BytesIO(content)) as im:
            kind = im.format
            im = ImageOps.exif_transpose(im)
            width, height = im.size
            alpha = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
    except Exception as error:
        raise ValueError("Wgraj obraz PNG, WEBP lub JPG") from error
    if kind not in IMAGE_TYPES:
        raise ValueError("Wgraj obraz PNG, WEBP lub JPG")
    suffix, mime = IMAGE_TYPES[kind]
    return content, CastImage(file=hashlib.sha256(content).hexdigest() + "." + suffix, width=width, height=height, alpha=alpha), mime


class Cast:
    """Channel-scoped banks stored beside the workspace; one folder per channel."""

    def __init__(self, store):
        self.store = store
        self.root = store.root / "workspace" / "cast"

    def channel(self, channel_id):
        if not isinstance(channel_id, str) or not CHANNEL_ID.fullmatch(channel_id):
            raise ValueError("Niepoprawny kanał")
        if not any(c["id"] == channel_id for c in self.store.channels()):
            raise ValueError("Nie ma takiego kanału")
        return self.root / channel_id

    def _rows(self, channel_id, group, model, archived):
        folder = self.channel(channel_id) / group
        rows = [model.model_validate_json(p.read_text()) for p in folder.glob("*.json")] if folder.exists() else []
        return sorted([r for r in rows if archived or not r.archived], key=lambda r: r.name.lower())

    def characters(self, channel_id, archived=False):
        return self._rows(channel_id, "characters", Character, archived)

    def locations(self, channel_id, archived=False):
        return self._rows(channel_id, "locations", Location, archived)

    def items(self, channel_id, archived=False):
        return self._rows(channel_id, "items", Item, archived)

    def sounds(self, channel_id, archived=False):
        return self._rows(channel_id, "sounds", Sound, archived)

    def bank(self, channel_id):
        return {"characters": self.characters(channel_id, True), "locations": self.locations(channel_id, True), "items": self.items(channel_id, True),
                "sounds": self.sounds(channel_id, True)}

    def _save(self, channel_id, group, model, body):
        from .store import atomic_json, now, Conflict
        folder = self.channel(channel_id)
        item = model.model_validate(body | {"channel_id": channel_id})
        images = ([p.image for p in getattr(item, "poses", [])] + [i for s in getattr(item, "states", []) for i in (s.image, s.foreground) if i]
                  + [v.image for v in getattr(item, "variants", [])])
        for image in images:
            if not (folder / "media" / image.file).is_file():
                raise ValueError("Obraz nie został wgrany do banku tego kanału")
        path = folder / group / (item.id + ".json")
        with self.store.lock:
            old = model.model_validate_json(path.read_text()) if path.exists() else None
            if old and old.channel_id != channel_id:
                raise ValueError("Wpis należy do innego kanału")
            if item.revision != (old.revision if old else 0):
                raise Conflict("Wpis zmienił się. Wczytaj aktualną wersję.")
            item.revision += 1
            item.updated_at = now()
            atomic_json(path, item.model_dump())
        return item

    def save_character(self, channel_id, body):
        costumes = {i.id for i in self.items(channel_id, True) if i.category == "costume"}
        if any(p.get("costume_id") and p["costume_id"] not in costumes for p in body.get("poses", [])):
            raise ValueError("Poza wskazuje kostium spoza banku kanału")
        return self._save(channel_id, "characters", Character, body)

    def save_location(self, channel_id, body):
        return self._save(channel_id, "locations", Location, body)

    def save_sound(self, channel_id, body):
        sound = Sound.model_validate(body | {"channel_id": channel_id})
        if not (self.channel(channel_id) / "media" / sound.file).is_file():
            raise ValueError("Plik dźwięku nie został wgrany do banku tego kanału")
        return self._save(channel_id, "sounds", Sound, body)

    def add_audio(self, channel_id, content: bytes, name: str):
        import subprocess
        import tempfile
        if len(content) > MAX_AUDIO:
            raise ValueError("Plik dźwięku przekracza 80 MB")
        suffix = Path(name or "").suffix.lower().lstrip(".")
        if suffix not in AUDIO_TYPES:
            raise ValueError("Wgraj dźwięk WAV, MP3, OGG, M4A albo FLAC")
        folder = self.channel(channel_id) / "media"
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=folder, suffix="." + suffix, delete=False) as handle:
            handle.write(content)
            temporary = Path(handle.name)
        try:
            run = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "format=duration", "-of", "csv=p=0", str(temporary)],
                                 capture_output=True, text=True, timeout=60, check=False)
            duration = float(run.stdout.strip() or 0)
            if run.returncode or duration <= 0:
                raise ValueError("Nie udało się odczytać dźwięku")
            target = folder / (hashlib.sha256(content).hexdigest() + "." + suffix)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return {"file": target.name, "duration": round(duration, 3)}

    def audio_path(self, channel_id, file):
        if not AUDIO_FILE.fullmatch(file or ""):
            raise ValueError("Niepoprawny plik dźwięku")
        path = self.channel(channel_id) / "media" / file
        if not path.is_file():
            raise FileNotFoundError(file)
        return path, AUDIO_TYPES[file.rsplit(".", 1)[1]]

    def save_item(self, channel_id, body):
        item = Item.model_validate(body | {"channel_id": channel_id})
        known = {c.id for c in self.characters(channel_id, True)}
        if not set(item.character_ids) <= known:
            raise ValueError("Kostium wskazuje postać spoza banku kanału")
        return self._save(channel_id, "items", Item, body)

    def add_image(self, channel_id, content: bytes):
        data, image, _ = read_image(content)
        folder = self.channel(channel_id) / "media"
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / image.file
        if not target.exists():
            temporary = target.with_suffix(".part")
            temporary.write_bytes(data)
            temporary.replace(target)
        return image

    def image_path(self, channel_id, file):
        if not MEDIA_FILE.fullmatch(file or ""):
            raise ValueError("Niepoprawny plik banku")
        path = self.channel(channel_id) / "media" / file
        if not path.is_file():
            raise FileNotFoundError(file)
        return path, IMAGE_TYPES[{"png": "PNG", "webp": "WEBP", "jpg": "JPEG"}[file.rsplit(".", 1)[1]]][1]


def validate_scene(scene: StageScene, characters: dict[str, Character], locations: dict[str, Location], items: dict[str, Item] | None = None):
    """Scenes may reference only the active (non-archived) bank of the film's channel."""
    items = items or {}
    if scene.location_id:
        location = locations.get(scene.location_id)
        if not location:
            raise ValueError(f"Scena {scene.number}: lokacja nie należy do banku kanału tego filmu")
        if scene.location_state_id and scene.location_state_id not in {s.id for s in location.states}:
            raise ValueError(f"Scena {scene.number}: stan nie należy do wybranej lokacji")
    elif scene.location_state_id:
        raise ValueError(f"Scena {scene.number}: wybierz lokację stanu")
    state = None
    if scene.location_id:
        location = locations[scene.location_id]
        state = next((s for s in location.states if s.id == scene.location_state_id), None) or (location.states[0] if location.states else None)
    regions = {r.id for r in (state.regions if state else [])}
    for placed in [*scene.characters, *scene.props]:
        if placed.region_id and placed.region_id not in regions:
            raise ValueError(f"Scena {scene.number}: obszar nie należy do stanu lokacji tej sceny")
    for placed in scene.characters:
        character = characters.get(placed.character_id)
        if not character:
            raise ValueError(f"Scena {scene.number}: postać nie należy do banku kanału tego filmu")
        if placed.pose_id and placed.pose_id not in {p.id for p in character.poses}:
            raise ValueError(f"Scena {scene.number}: poza nie należy do postaci {character.name}")
        if placed.costume_id:
            costume = items.get(placed.costume_id)
            if not costume or getattr(costume, "category", "") != "costume" or (costume.character_ids and character.id not in costume.character_ids):
                raise ValueError(f"Scena {scene.number}: kostium nie pasuje do postaci {character.name}")
    for cue in scene.audio:
        sound = items.get(cue.sound_id)
        if not sound or getattr(sound, "kind", "") not in ("sfx", "ambience"):
            raise ValueError(f"Scena {scene.number}: dźwięk nie należy do banku kanału albo jest muzyką (muzykę ustawiasz na zakres scen)")
    for placed in scene.props:
        item = items.get(placed.item_id)
        if not item or getattr(item, "category", "") in ("", "costume"):
            raise ValueError(f"Scena {scene.number}: rekwizyt nie należy do banku kanału tego filmu")
        if placed.variant_id and placed.variant_id not in {v.id for v in item.variants}:
            raise ValueError(f"Scena {scene.number}: wariant nie należy do rekwizytu {item.name}")
    speakers = {"narrator"} | set(characters)
    for line in scene.dialogue:
        if line.speaker not in speakers:
            raise ValueError(f"Scena {scene.number}: nieznany mówca kwestii")


def channel_bank(cast: Cast, project, *, archived=False):
    if not project.channel_id:
        raise ValueError("Przypisz film do kanału, aby korzystać z banku postaci i lokacji")
    return ({c.id: c for c in cast.characters(project.channel_id, archived)},
            {loc.id: loc for loc in cast.locations(project.channel_id, archived)},
            {i.id: i for i in [*cast.items(project.channel_id, archived), *cast.sounds(project.channel_id, archived)]})


def apply_scene_operation(project, operation: dict, characters, locations, items=None):
    """Single entry point for manual edits, reviews and accepted AI proposals."""
    kind = operation.get("type")
    scenes = project.stage_scenes
    index = {s.id: i for i, s in enumerate(scenes)}
    beats = {b.id for b in project.beats}
    if kind == "music_set":
        cue = MusicCue.model_validate(operation.get("cue", {}))
        sound = (items or {}).get(cue.sound_id)
        if not isinstance(sound, Sound) or sound.kind != "music":
            raise ValueError("Wybierz utwór muzyczny z banku kanału")
        if cue.from_scene_id not in index or cue.to_scene_id not in index:
            raise ValueError("Zakres muzyki wskazuje nieistniejącą scenę")
        project.music_cues = [c for c in project.music_cues if c.id != cue.id] + [cue]
        return cue
    if kind == "music_delete":
        project.music_cues = [c for c in project.music_cues if c.id != operation.get("cue_id")]
        return None
    if kind == "add":
        values = operation.get("scene", {})
        scene = StageScene.model_validate({k: v for k, v in values.items() if k in SCENE_FIELDS} | {"number": max((s.number for s in scenes), default=0) + 1})
        validate_scene(scene, characters, locations, items)
        if scene.beat_id and scene.beat_id not in beats:
            raise ValueError("Scena wskazuje nieistniejący beat")
        position = index.get(operation.get("after", ""), len(scenes) - 1) + 1
        scenes.insert(position, scene)
        return scene
    scene_id = operation.get("scene_id")
    if scene_id not in index:
        raise ValueError("Nie ma takiej sceny")
    scene = scenes[index[scene_id]]
    if kind == "update":
        changes = operation.get("changes", {})
        if not isinstance(changes, dict) or not set(changes) <= set(SCENE_FIELDS) | {"number"}:
            raise ValueError("Scena przyjmuje wyłącznie pola treści")
        candidate = StageScene.model_validate(scene.model_dump() | changes)
        validate_scene(candidate, characters, locations, items)
        if candidate.beat_id and candidate.beat_id not in beats:
            raise ValueError("Scena wskazuje nieistniejący beat")
        content_changed = any(getattr(candidate, k) != getattr(scene, k) for k in CONTENT_FIELDS)
        if content_changed and candidate.status in ("approved", "rework"):
            # Any change to an approved shot sends it back for the director's review.
            candidate.status = "review"
        scenes[index[scene_id]] = candidate
        return candidate
    if kind == "review":
        from .store import now
        status = operation.get("status")
        tags = [t for t in operation.get("tags", []) if t in REVIEW_TAGS]
        note = str(operation.get("note", ""))
        if status == "rework" and not (tags or note.strip()):
            raise ValueError("Napisz, co poprawić, albo wybierz obszar poprawki")
        scene.reviews.append(Review(status=status, note=note, tags=tags, at=now()))
        scene.status = status
        return scene
    if kind == "delete":
        scenes.pop(index[scene_id])
        # Music ranges cannot point at a missing scene: drop the ones anchored on it.
        project.music_cues = [c for c in project.music_cues if scene_id not in (c.from_scene_id, c.to_scene_id)]
        return None
    if kind == "move":
        target = int(operation.get("to", index[scene_id]))
        scenes.insert(max(0, min(len(scenes) - 1, target)), scenes.pop(index[scene_id]))
        for number, item in enumerate(scenes, 1):
            item.number = number
        return scene
    raise ValueError("Nieznana operacja sceny")


def regeneration_prompt(project, scene: StageScene, characters, locations, instruction: str, items=None) -> str:
    bank = bank_summary(characters, locations, items)
    neighbours = [s for s in project.stage_scenes if abs(s.number - scene.number) == 1]
    last = scene.reviews[-1] if scene.reviews else None
    feedback = "; ".join(filter(None, [", ".join(last.tags) if last else "", last.note if last else "", instruction]))
    current_issues = review_staging(scene, characters, locations, items, project.stage_scenes)
    current = scene.model_dump(include=set(CONTENT_FIELDS))
    return f"""You are the scene director of a 2D animated series. Rewrite ONE scene according to the director's feedback.
Film: {project.title}. Language of narration and dialogue: {project.language}.
Use only the character, pose, costume, item, location and state ids from the bank below. Speakers are "narrator" or a character id.
Keep the scene consistent with its neighbours (continuity of place, time, objects and injuries).

BANK: {json.dumps(bank, ensure_ascii=False)}
NEIGHBOUR SCENES: {json.dumps([s.model_dump(include={"number", "title", "story_time", "action"}) for s in neighbours], ensure_ascii=False)}
CURRENT SCENE {scene.number}: {json.dumps(current, ensure_ascii=False)}
DIRECTOR FEEDBACK: {feedback or "Make the scene clearer and more cinematic."}
STAGING REVIEWER (fix all of these): {"; ".join(current_issues) or "no issues"}

Return only JSON with keys: {", ".join(CONTENT_FIELDS)}, and "reason" (one sentence explaining the change).
{SCHEMA_HINT}
{STAGING_RULES}"""


def parse_regeneration(text: str, scene: StageScene, characters, locations, items=None, others=()) -> dict:
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        raise ValueError("Odpowiedź AI nie zawiera JSON sceny")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise ValueError("Odpowiedź AI zawiera niepoprawny JSON") from error
    reason = str(data.pop("reason", ""))[:500]
    changes = {k: v for k, v in data.items() if k in CONTENT_FIELDS}
    for line in changes.get("dialogue", []) if isinstance(changes.get("dialogue"), list) else []:
        if isinstance(line, dict):
            line.pop("id", None)
    candidate = StageScene.model_validate(scene.model_dump() | changes)
    validate_scene(candidate, characters, locations, items)
    return {"scene_id": scene.id, "changes": candidate.model_dump(include=set(CONTENT_FIELDS)), "reason": reason,
            "issues": review_staging(candidate, characters, locations, items, others)}


def bank_summary(characters, locations, items=None):
    return {
        "items": [{"id": i.id, "category": i.category, "name": i.name, "description": i.description, "for_characters": i.character_ids,
                   "variants": [{"id": v.id, "name": v.name} for v in i.variants]} for i in (items or {}).values() if isinstance(i, Item)],
        "sounds": [{"id": i.id, "kind": i.kind, "name": i.name, "seconds": i.duration} for i in (items or {}).values() if isinstance(i, Sound) and i.kind != "music"],
        "characters": [{"id": c.id, "name": c.name, "role": c.role, "description": c.description, "poses": [{"id": p.id, "name": p.name, "view": p.view} for p in c.poses]} for c in characters.values()],
        "locations": [{"id": loc.id, "name": loc.name, "description": loc.description, "states": [{"id": s.id, "name": s.name, "time_of_day": s.time_of_day, "floor_y": s.floor_y,
                                 "regions": [r.model_dump() for r in s.regions]} for s in loc.states]} for loc in locations.values()],
    }


def breakdown_prompt(project, beat, characters, locations, instruction: str, items=None) -> str:
    """Story Director: split one story beat into storyboard scenes built only from the channel bank."""
    order = [b.id for b in project.beats]
    index = order.index(beat.id)
    around = [b.model_dump(include={"title", "goal", "turn", "narration"}) for b in project.beats[max(0, index - 1):index + 2] if b.id != beat.id]
    existing = [s.model_dump(include={"number", "title", "action"}) for s in project.stage_scenes if s.beat_id == beat.id]
    return f"""You are the story director of a 2D animated series. Break ONE story beat into storyboard scenes (shots).
Film: {project.title}. Language of narration and dialogue: {project.language}.
A beat is a unit of story; a scene is a unit of picture. Use 2-8 scenes, each 3-12 seconds, varied framing, clear action.
Build scenes ONLY from the character, pose, location and state ids in the bank. Speakers are "narrator" or a character id.
Prefer reusing an existing location with a different camera over inventing new places.

BANK: {json.dumps(bank_summary(characters, locations, items), ensure_ascii=False)}
NEIGHBOUR BEATS: {json.dumps(around, ensure_ascii=False)}
BEAT: {json.dumps(beat.model_dump(include={"title", "goal", "turn", "narration"}), ensure_ascii=False)}
SCENES ALREADY IN THIS BEAT: {json.dumps(existing, ensure_ascii=False)}
DIRECTOR NOTES: {instruction or "none"}

Return only JSON: {{"reason": "one sentence", "scenes": [{{{", ".join(f'"{k}"' for k in CONTENT_FIELDS)}}}]}}.
{SCHEMA_HINT}
{STAGING_RULES}"""


def parse_breakdown(text: str, beat, characters, locations, items=None, others=()) -> dict:
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        raise ValueError("Odpowiedź AI nie zawiera JSON scen")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise ValueError("Odpowiedź AI zawiera niepoprawny JSON") from error
    rows = data.get("scenes")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise ValueError("Propozycja musi zawierać od 1 do 12 scen")
    scenes = []
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError("Niepoprawna scena w propozycji")
        values = {k: v for k, v in row.items() if k in CONTENT_FIELDS}
        for line in values.get("dialogue", []) if isinstance(values.get("dialogue"), list) else []:
            if isinstance(line, dict):
                line.pop("id", None)
        scene = StageScene.model_validate(values | {"number": number})
        validate_scene(scene, characters, locations, items)
        scenes.append(scene.model_dump(include=set(CONTENT_FIELDS)) | {"beat_id": beat.id, "issues": review_staging(scene, characters, locations, items, others)})
    return {"beat_id": beat.id, "scenes": scenes, "reason": str(data.get("reason", ""))[:500]}


# Kokoro English voices: a = American, b = British; f = female, m = male.
DRAFT_VOICES = ("am_michael", "am_adam", "am_eric", "am_liam", "am_onyx", "am_fenrir", "am_echo", "am_puck",
                "af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky", "af_nova", "af_river", "af_jessica", "af_alloy", "af_aoede", "af_kore",
                "bm_george", "bm_daniel", "bm_lewis", "bm_fable", "bf_emma", "bf_isabella", "bf_alice", "bf_lily")
DRAFT_MODEL = "kokoro-v1.0"


class DraftVoices:
    """Fast local draft voices for the animatic, cached by text, voice and speed."""

    def __init__(self, root: Path, python: Path, model_dir: Path):
        import threading
        self.folder = root / "cache" / "draft-voice"
        self.python, self.model_dir = python, model_dir
        self.lock = threading.Lock()  # one model process at a time on small machines

    def available(self):
        return self.python.is_file() and (self.model_dir / "kokoro-v1.0.onnx").is_file() and (self.model_dir / "voices-v1.0.bin").is_file()

    @staticmethod
    def key(text, voice, speed):
        return hashlib.sha256(json.dumps([DRAFT_MODEL, text, voice, round(speed, 2)]).encode()).hexdigest()[:32]

    def path(self, key):
        if not re.fullmatch(r"[a-f0-9]{32}", key or ""):
            raise ValueError("Niepoprawny plik głosu roboczego")
        return self.folder / (key + ".wav")

    def render(self, lines: list[dict]) -> dict[str, float]:
        """lines: [{"text", "voice", "speed"}] -> {key: duration}; generates only missing lines."""
        import subprocess
        if not self.available():
            raise ValueError("Brak Kokoro: ustaw DOCOS_DRAFT_TTS_PYTHON (środowisko z kokoro-onnx) i DOCOS_KOKORO_DIR z plikami modelu")
        self.folder.mkdir(parents=True, exist_ok=True)
        result, missing = {}, []
        for line in lines:
            if line["voice"] not in DRAFT_VOICES:
                raise ValueError("Nieznany głos roboczy")
            key = self.key(line["text"], line["voice"], line["speed"])
            meta = self.folder / (key + ".json")
            if meta.is_file() and self.path(key).is_file():
                result[key] = json.loads(meta.read_text())["duration"]
            elif key not in {m["key"] for m in missing}:
                missing.append(line | {"key": key, "out": str(self.path(key))})
        if missing:
            with self.lock:
                run = subprocess.run([str(self.python), "-I", str(Path(__file__).resolve().parents[1] / "studio_workers" / "draft_voice_worker.py")],
                                     input=json.dumps({"model_dir": str(self.model_dir), "lines": missing}), capture_output=True, text=True, timeout=600, check=False)
            if run.returncode:
                raise ValueError("Kokoro nie wygenerował głosu: " + (run.stderr.strip().splitlines() or ["nieznany błąd"])[-1][:300])
            durations = {Path(row["out"]).stem: row["duration"] for row in map(json.loads, run.stdout.splitlines()) if row}
            for line in missing:
                if line["key"] not in durations:
                    raise ValueError("Kokoro nie zwrócił wszystkich nagrań")
                (self.folder / (line["key"] + ".json")).write_text(json.dumps({"duration": durations[line["key"]]}))
                result[line["key"]] = durations[line["key"]]
        return result


def default_draft_voice(speaker: str, characters: dict) -> str:
    """Narrator gets a calm male voice; characters get distinct voices in bank order."""
    if speaker == "narrator":
        return "am_michael"
    pool = [v for v in DRAFT_VOICES if v != "am_michael"]
    order = sorted(characters)
    return pool[order.index(speaker) % len(pool)] if speaker in order else "am_adam"


def scene_state(scene, locations):
    location = locations.get(scene.location_id)
    if not location:
        return None
    return next((s for s in location.states if s.id == scene.location_state_id), None) or next((s for s in location.states if s.image), None)


def review_staging(scene: StageScene, characters, locations, items=None, others=()) -> list[str]:
    """Staging reviewer: geometry checks a human director would catch at a glance.

    Boxes are in frame fractions; image aspect converts height (scale) to width on a 16:9 frame.
    """
    items = items or {}
    state = scene_state(scene, locations)
    regions = {r.id: r for r in (state.regions if state else [])}
    floor = state.floor_y if state else None
    issues, people = [], []

    def overlap(box, region):
        w = max(0, min(box[2], region.x1) - max(box[0], region.x0))
        h = max(0, min(box[3], region.y1) - max(box[1], region.y0))
        area = (box[2] - box[0]) * (box[3] - box[1])
        return w * h / area if area else 0

    for placed in scene.characters:
        character = characters.get(placed.character_id)
        pose = character and (next((p for p in character.poses if p.id == placed.pose_id), None)
                              or next((p for p in character.poses if p.id == character.default_pose_id), None)
                              or (character.poses[0] if character.poses else None))
        if not pose:
            continue
        width = placed.scale * pose.image.width / pose.image.height * 9 / 16
        box = (placed.x - width / 2, placed.y - placed.scale, placed.x + width / 2, placed.y)
        people.append((character.name, placed, box))
        region = regions.get(placed.region_id)
        if region:
            if box[3] <= region.y1 + .02 and box[1] >= region.y0 - .02:
                issues.append(f"{character.name} mieści się cała w „{region.name}” — wygląda jak miniatura. "
                              f"Powiększ postać do skali innych postaci i pokaż ją od pasa w górę (dół zasłoni rama).")
            if box[1] > region.y1 or box[3] < region.y0 or box[0] > region.x1 or box[2] < region.x0:
                issues.append(f"{character.name} jest poza obszarem „{region.name}” — nie będzie widoczna.")
            continue
        if floor is not None and placed.y < floor - .04 and placed.y <= 1:
            issues.append(f"{character.name} wisi w powietrzu — stopy powyżej podłogi. Opuść postać na linię podłogi.")
        if box[1] < .01:
            issues.append(f"{character.name} jest wyższy niż kadr — zbliżenie rób kadrem kamery (zoom), nie powiększaniem postaci.")
        usual = sorted(c.scale for other in others if other.id != scene.id and other.location_id == scene.location_id
                       for c in other.characters if c.character_id == placed.character_id and not c.region_id)
        if usual:
            median = usual[len(usual) // 2]
            if placed.scale > median * 1.35 or placed.scale < median / 1.35:
                issues.append(f"{character.name} ma {placed.scale / median:.1f}× inną wielkość niż w pozostałych scenach w tej lokacji — "
                              f"zachowaj skalę postaci, a bliższy kadr ustaw kamerą (zoom).")
        for inside in regions.values():
            if overlap(box, inside) > .7:
                issues.append(f"{character.name} stoi na tle „{inside.name}”, ale nie jest do niego przypisana — "
                              f"jeśli ma być za szybą, wybierz ten obszar i powiększ postać.")
    free = [p for p in people if not p[1].region_id]
    for name, placed, _ in people:
        if placed.region_id and free:
            biggest = max(free, key=lambda p: p[1].scale)
            if placed.scale < biggest[1].scale * .75:
                issues.append(f"{name} jest dużo mniejsza niż {biggest[0]} — osoba tuż za szybą powinna mieć podobną skalę.")
    for placed in scene.props:
        item = items.get(placed.item_id)
        variant = item and (next((v for v in item.variants if v.id == placed.variant_id), None) or (item.variants[0] if item.variants else None))
        if not variant or placed.region_id:
            continue
        height = placed.scale
        width = height * variant.image.width / variant.image.height * 9 / 16
        box = (placed.x - width / 2, placed.y - height / 2, placed.x + width / 2, placed.y + height / 2)
        for region in regions.values():
            share = overlap(box, region)
            if .25 < share < .97:
                issues.append(f"„{item.name}” wychodzi poza „{region.name}” na ścianę — przypisz go do tego obszaru.")
    return issues
