"""Reusable settings and versioned resources, independent of a film's content."""
from typing import Literal
from pydantic import Field, model_validator
from .models_base import Model, uid
from .development import Chapter


class Preset(Model):
    language: str | None = None
    audience: str | None = Field(default=None, max_length=2000)
    viewer_promise: str | None = Field(default=None, max_length=2000)
    references: str | None = Field(default=None, max_length=2000)
    constraints: str | None = Field(default=None, max_length=3000)
    target_minutes: int | None = Field(default=None, ge=1, le=360)
    narrative_style: str | None = Field(default=None, max_length=4000)
    visual_style: str | None = Field(default=None, max_length=4000)
    font: Literal["montserrat", "courier", "courier-bold"] | None = None
    color: str | None = Field(default=None, pattern=r"^#[a-fA-F0-9]{6}$")
    voice_id: str | None = Field(default=None, pattern=r"^voice_[a-f0-9]{16}$")
    pronunciation: dict[str, str] | None = None
    width: int | None = Field(default=None, ge=144, le=3840, multiple_of=2)
    height: int | None = Field(default=None, ge=144, le=3840, multiple_of=2)
    fps_num: int | None = Field(default=None, ge=1, le=120000)
    fps_den: int | None = Field(default=None, ge=1, le=1001)
    ducking: bool | None = None
    ducking_gain: float | None = Field(default=None, ge=0, le=1)


class Category(Model):
    id: str = Field(default_factory=lambda: uid("cat_"), pattern=r"^cat_[a-f0-9]{16}$")
    revision: int = 0
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=3000)
    channel_id: str = ""
    defaults: Preset = Field(default_factory=Preset)
    archived: bool = False


class Resource(Model):
    id: str = Field(default_factory=lambda: uid("res_"), pattern=r"^res_[a-f0-9]{16}$")
    revision: int = 0
    title: str = Field(min_length=1, max_length=200)
    kind: Literal["fact", "source", "note", "media", "idea", "template", "baseline"]
    scope: Literal["workspace", "channel", "category"] = "workspace"
    channel_id: str = ""
    category_ids: list[str] = Field(default_factory=list, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=30)
    context: str = Field(default="", max_length=4000)
    payload: dict = Field(default_factory=dict)
    origin_project_id: str = ""
    origin_item_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    archived: bool = False

    @model_validator(mode="after")
    def scope_has_target(self):
        if self.scope == "channel" and not self.channel_id:
            raise ValueError("Wybierz kanał zasobu")
        if self.scope == "category" and not self.category_ids:
            raise ValueError("Wybierz przynajmniej jedną kategorię zasobu")
        return self


class ResourceLink(Model):
    resource_id: str
    revision: int
    kind: str
    title: str
    local_ids: dict[str, str] = Field(default_factory=dict)
    imported_at: str = ""


class FilmTemplate(Model):
    preset: Preset = Field(default_factory=Preset)
    chapters: list[Chapter] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def no_evidence(self):
        if any(s.fact_ids for c in self.chapters for s in c.sections):
            raise ValueError("Szablon może zawierać strukturę, ale nie fakty konkretnego filmu")
        return self
