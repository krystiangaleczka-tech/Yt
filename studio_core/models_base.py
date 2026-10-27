"""Shared base for project and motion models without circular imports."""
import uuid
from pydantic import BaseModel, ConfigDict


def uid(prefix: str = "") -> str:
    return prefix + uuid.uuid4().hex[:16]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
