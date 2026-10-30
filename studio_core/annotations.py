"""Review markup belongs to an exact local frame, separate from film content."""
from pydantic import Field, field_validator, model_validator
from .models_base import Model, uid


class AnnotationPoint(Model):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class AnnotationStroke(Model):
    points: list[AnnotationPoint] = Field(min_length=2, max_length=2000)
    color: str = Field(default="#f8d34f", pattern=r"^#[0-9a-fA-F]{6}$")
    width: float = Field(default=4, ge=1, le=16)


class FrameAnnotation(Model):
    id: str = Field(default_factory=lambda: uid("ann_"), pattern=r"^ann_[a-f0-9]{16}$")
    scene_id: str = Field(pattern=r"^(scene|stage)_[a-f0-9]{16}$")
    frame: int = Field(ge=0, strict=True)
    fps_num: int = Field(default=30, ge=1, le=240000, strict=True)
    fps_den: int = Field(default=1, ge=1, le=10000, strict=True)
    text: str = Field(min_length=1, max_length=3000)
    strokes: list[AnnotationStroke] = Field(min_length=1, max_length=20)
    created_at: str = ""
    updated_at: str = ""

    @field_validator("text")
    @classmethod
    def nonempty_text(cls, value):
        if not value.strip():
            raise ValueError("Wpisz treść uwagi do klatki")
        return value.strip()

    @model_validator(mode="after")
    def valid_rate(self):
        if not 1 <= self.fps_num / self.fps_den <= 240:
            raise ValueError("Niepoprawna liczba klatek na sekundę")
        return self
