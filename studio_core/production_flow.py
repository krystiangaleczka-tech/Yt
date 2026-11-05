"""Validated storage contract for the guided film flow (``legacy.production_flow``).

The flow is written by the Studio UI (Master Story, acts, sequences, scene plan,
director plans and approvals). It lives in ``Project.legacy`` for backward
compatibility, so the general project PATCH deliberately cannot touch it; this
module is the only write path and validates shape and size first.

The validated payload is stored exactly as sent (no re-ordering or default
filling) so client-side approval signatures stay stable across a reload.
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_FLOW_BYTES = 8 * 1024 * 1024


class _FlowModel(BaseModel):
    # Unknown keys are tolerated so an older/newer client never loses work.
    model_config = ConfigDict(extra="allow", allow_inf_nan=False)


class FlowVariant(_FlowModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(default="", max_length=1000)
    description: str = Field(default="", max_length=120_000)


class FlowNode(_FlowModel):
    id: str = Field(min_length=1, max_length=120)
    variants: list[FlowVariant] = Field(default_factory=list, max_length=50)
    selected: str | None = Field(default=None, max_length=120)


class FlowSection(FlowNode):
    actId: str = Field(default="", max_length=120)
    seconds: float = Field(default=60, ge=0, le=36_000)


class FlowOutline(FlowNode):
    sectionId: str = Field(default="", max_length=120)
    seconds: float = Field(default=60, ge=0, le=36_000)


class FlowReview(_FlowModel):
    id: str = Field(default="", max_length=120)
    agent: str = Field(default="", max_length=200)
    verdict: str = Field(default="", max_length=10_000)
    issues: list[str] = Field(default_factory=list, max_length=100)
    suggestions: list[str] = Field(default_factory=list, max_length=100)


class DirectorBeat(_FlowModel):
    id: str = Field(min_length=1, max_length=160)
    title: str = Field(default="", max_length=300)
    goal: str = Field(default="", max_length=4000)
    tensionBefore: int = Field(default=0, ge=0, le=10)
    tensionAfter: int = Field(default=0, ge=0, le=10)
    viewerKnows: str = Field(default="", max_length=2000)
    characterKnows: str = Field(default="", max_length=2000)
    soundCue: str = Field(default="", max_length=1000)
    patternId: str = Field(default="", max_length=160)


class DirectorShot(_FlowModel):
    id: str = Field(min_length=1, max_length=160)
    beatId: str = Field(default="", max_length=160)
    typeId: str = Field(default="medium", min_length=1, max_length=60)
    title: str = Field(default="", max_length=300)
    description: str = Field(default="", max_length=3000)
    duration: float = Field(default=2, ge=0.1, le=120)
    transition: str = Field(default="cut", max_length=30)
    sound: str = Field(default="", max_length=1000)


class SceneDirection(_FlowModel):
    outlineId: str = Field(min_length=1, max_length=120)
    sourceSignature: str = Field(default="", max_length=2_000_000)
    patternId: str = Field(default="", max_length=160)
    mode: Literal["auto", "guided", "manual"] = "auto"
    notes: str = Field(default="", max_length=5000)
    beats: list[DirectorBeat] = Field(default_factory=list, max_length=60)
    shots: list[DirectorShot] = Field(default_factory=list, max_length=240)


class DirectorPattern(_FlowModel):
    id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=120)
    purpose: str = Field(default="", max_length=1000)
    cue: str = Field(default="", max_length=1000)
    rhythm: str = Field(default="", max_length=1000)
    shots: list[str] = Field(default_factory=list, min_length=1, max_length=40)
    tension: list[int] = Field(default_factory=lambda: [3, 6], min_length=2, max_length=16)

    @field_validator("tension")
    @classmethod
    def _tension_scale(cls, value: list[int]) -> list[int]:
        if any(v < 0 or v > 10 for v in value):
            raise ValueError("Napięcie wzorca musi mieścić się w skali 0–10")
        return value


class DirectorState(_FlowModel):
    mode: Literal["auto", "guided", "manual"] = "auto"
    plans: dict[str, SceneDirection] = Field(default_factory=dict)
    customPatterns: list[DirectorPattern] = Field(default_factory=list, max_length=200)

    @model_validator(mode="after")
    def _plans_keyed_by_outline(self):
        if len(self.plans) > 2000:
            raise ValueError("Za dużo planów reżyserskich")
        for key, plan in self.plans.items():
            if plan.outlineId != key:
                raise ValueError("Plan reżyserski jest przypisany do innej sceny niż jego klucz")
        return self


class WorldBook(_FlowModel):
    """Księga świata (studio_core/continuity.py). Listy mają limity, treść jest swobodna."""
    version: int = Field(default=1, ge=1, le=99)
    unitLabel: str = Field(default="Dzień", max_length=40)
    places: list[dict] = Field(default_factory=list, max_length=500)
    characters: list[dict] = Field(default_factory=list, max_length=500)
    props: list[dict] = Field(default_factory=list, max_length=1000)
    resources: list[dict] = Field(default_factory=list, max_length=100)
    rules: list[dict] = Field(default_factory=list, max_length=500)
    events: list[dict] = Field(default_factory=list, max_length=2000)
    threads: list[dict] = Field(default_factory=list, max_length=500)
    spoilers: list[dict] = Field(default_factory=list, max_length=500)
    decisions: list[dict] = Field(default_factory=list, max_length=500)


class ProductionBook(_FlowModel):
    """Warsztat filmu: jak powstają ujęcia i sekwencje tego projektu."""
    pipeline: str = Field(default="", max_length=200_000)
    method: str = Field(default="", max_length=200_000)
    files: list[dict] = Field(default_factory=list, max_length=200)


class UnitReview(_FlowModel):
    status: Literal["robocza", "do poprawy", "zatwierdzona"] = "robocza"
    signature: str = Field(default="", max_length=200)
    checks: dict[str, str] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=20_000)
    reviewer: str = Field(default="", max_length=200)
    at: str = Field(default="", max_length=40)


class LogEntry(_FlowModel):
    id: str = Field(default="", max_length=120)
    at: str = Field(default="", max_length=40)
    who: str = Field(default="", max_length=200)
    unit: int | None = Field(default=None, ge=0, le=999)
    kind: str = Field(default="praca", max_length=40)
    summary: str = Field(min_length=1, max_length=2000)
    details: str = Field(default="", max_length=20_000)
    files: list[str] = Field(default_factory=list, max_length=100)


class ProductionFlow(_FlowModel):
    version: int = Field(default=1, ge=1, le=99)
    factual: bool = False
    sourceIdeaId: str = Field(default="", max_length=200)
    bible: dict[str, str] = Field(default_factory=dict)
    master: FlowNode = Field(default_factory=lambda: FlowNode(id="master"))
    acts: list[FlowNode] = Field(default_factory=list, max_length=30)
    sequences: list[FlowSection] = Field(default_factory=list, max_length=400)
    outlines: list[FlowOutline] = Field(default_factory=list, max_length=2000)
    scripts: dict[str, str] = Field(default_factory=dict)
    approved: dict[str, str] = Field(default_factory=dict)
    reviews: list[FlowReview] = Field(default_factory=list, max_length=40)
    director: DirectorState = Field(default_factory=DirectorState)
    world: WorldBook = Field(default_factory=WorldBook)
    book: ProductionBook = Field(default_factory=ProductionBook)
    unitReviews: dict[str, UnitReview] = Field(default_factory=dict)
    log: list[LogEntry] = Field(default_factory=list, max_length=5000)

    @model_validator(mode="after")
    def _unique_ids(self):
        for name, items in (("akt", self.acts), ("sekwencja", self.sequences), ("scena", self.outlines)):
            ids = [item.id for item in items]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Powtórzony identyfikator: {name}")
        if any(len(v) > 400_000 for v in self.scripts.values()):
            raise ValueError("Scenariusz aktu jest zbyt długi")
        if any(len(v) > 200_000 for v in self.bible.values()):
            raise ValueError("Pole Story Bible jest zbyt długie")
        return self


def validated_flow(flow: object) -> dict:
    """Return the flow unchanged after validating it; raise ValueError otherwise."""
    if not isinstance(flow, dict):
        raise ValueError("Plan filmu musi być obiektem")
    size = len(json.dumps(flow, ensure_ascii=False).encode("utf-8"))
    if size > MAX_FLOW_BYTES:
        raise ValueError("Plan filmu jest zbyt duży do zapisania")
    ProductionFlow.model_validate(flow)
    return flow
