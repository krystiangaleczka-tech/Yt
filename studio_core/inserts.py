"""Editable, bounded motion templates. User/AI input is data, never executable code."""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field, model_validator

from .models_base import Model, uid


class ChartItem(Model):
    label: str = Field(min_length=1, max_length=24)
    value: float = Field(ge=0, le=1e12)


class MotionInsert(Model):
    id: str = Field(default_factory=lambda: uid("insert_"), pattern=r"^insert_[a-f0-9]{16}$")
    template: Literal["photo", "compare", "chart", "quote", "chapter"] = "chapter"
    title: str = Field(default="Nowa wstawka", min_length=1, max_length=90)
    subtitle: str = Field(default="", max_length=180)
    text: str = Field(default="", max_length=240)
    source: str = Field(default="", max_length=160)
    image_ids: list[str] = Field(default_factory=list, max_length=2)
    labels: list[str] = Field(default_factory=lambda: ["Wcześniej", "Dziś"], min_length=2, max_length=2)
    data: list[ChartItem] = Field(default_factory=lambda: [ChartItem(label="A", value=30), ChartItem(label="B", value=70)], min_length=1, max_length=8)
    unit: str = Field(default="", max_length=16)
    duration: int = Field(default=180, ge=15, le=7200)
    accent: str = Field(default="#e8b86d", pattern=r"^#[a-fA-F0-9]{6}$")
    background: str = Field(default="#101722", pattern=r"^#[a-fA-F0-9]{6}$")
    zoom: float = Field(default=1.12, ge=1, le=1.5)
    pan: float = Field(default=0, ge=-15, le=15)
    rotation: float = Field(default=0, ge=-10, le=10)
    brightness: float = Field(default=1, ge=.5, le=1.5)
    saturation: float = Field(default=1, ge=0, le=2)
    blur: float = Field(default=0, ge=0, le=12)
    rendered_asset_id: str | None = None
    rendered_signature: str = ""

    @model_validator(mode="after")
    def bounded_labels(self):
        if any(len(s) > 40 for s in self.labels):
            raise ValueError("Podpis zdjęcia: maksymalnie czterdzieści znaków")
        return self


def definition(insert: MotionInsert) -> dict:
    return insert.model_dump(exclude={"rendered_asset_id", "rendered_signature"})


def signature(project, insert: MotionInsert) -> str:
    assets = {a.id: a.sha256 for a in project.assets}
    payload = {"insert": definition(insert), "width": project.sequence.width,
               "height": project.sequence.height, "fps_num": project.sequence.fps_num,
               "fps_den": project.sequence.fps_den,
               "media": [assets.get(i) for i in insert.image_ids], "renderer": "docos-motion/1"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def require_ready(project, insert: MotionInsert):
    count = {"photo": 1, "compare": 2}.get(insert.template, 0)
    if len(insert.image_ids) < count:
        raise ValueError(f"Ten szablon wymaga zdjęć: {count}")
    if insert.template == "quote" and not insert.text.strip():
        raise ValueError("Wpisz treść cytatu")
    if insert.duration / (project.sequence.fps_num / project.sequence.fps_den) > 60:
        raise ValueError("Wstawka może trwać najwyżej sześćdziesiąt sekund")


def find_insert(project, insert_id):
    item = next((i for i in project.inserts if i.id == insert_id), None)
    if item is None:
        raise ValueError("Nie znaleziono wstawki")
    return item
