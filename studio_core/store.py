from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .models import Project


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix("." + uuid.uuid4().hex + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def story_hash(p: Project) -> str:
    payload = {"story": {k: v for k, v in p.story.items() if k not in ("status", "approved_hash")},
               "facts": [f.model_dump() for f in p.facts], "title": p.title}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Conflict(ValueError):
    pass


class ProjectStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()

    def folder(self, project_id: str) -> Path:
        if not re.fullmatch(r"prj_[a-f0-9]{16}", project_id):
            raise ValueError("Niepoprawny identyfikator projektu")
        return self.root / "projects" / project_id

    def read_document(self, project_id: str) -> dict:
        return json.loads((self.folder(project_id) / "project.json").read_text(encoding="utf-8"))

    def get(self, project_id: str) -> Project:
        doc = self.read_document(project_id)
        return Project.model_validate({k: v for k, v in doc.items() if not k.startswith("_")})

    def list(self) -> list[dict]:
        result = []
        for path in (self.root / "projects").glob("prj_*/project.json"):
            try:
                p = self.get(path.parent.name)
                result.append({"id": p.id, "title": p.title, "revision": p.revision, "updated_at": p.updated_at,
                               "scenes": len(p.scenes), "assets": len(p.assets), "demo": p.demo,
                               "duration": max((c.start + c.duration for c in p.sequence.clips), default=0),
                               "fps": p.sequence.fps_num / p.sequence.fps_den})
            except (ValueError, OSError):
                continue
        return sorted(result, key=lambda x: x["updated_at"], reverse=True)

    def create(self, project: Project) -> Project:
        with self.lock:
            if (self.folder(project.id) / "project.json").exists():
                raise Conflict("Projekt już istnieje")
            project.revision = 1
            project.updated_at = now()
            atomic_json(self.folder(project.id) / "project.json", project.model_dump() | {"_undo": [], "_redo": []})
            return project

    def mutate(self, project_id: str, revision: int, change: Callable[[Project], None], *, history=True) -> Project:
        with self.lock:
            document = self.read_document(project_id)
            before = {k: v for k, v in document.items() if not k.startswith("_")}
            current = Project.model_validate(before)
            if current.revision != revision:
                raise Conflict(f"Projekt zmienił się w innym oknie. Wczytaj rewizję {current.revision}.")
            previous_story = story_hash(current)
            change(current)
            if story_hash(current) != previous_story:
                current.story["status"] = "DRAFT"
                current.story["approved_hash"] = ""
            current = Project.model_validate(current.model_dump())
            current.id = project_id
            current.revision = revision + 1
            current.updated_at = now()
            undo = (document.get("_undo", []) + [before])[-40:] if history else document.get("_undo", [])
            atomic_json(self.folder(project_id) / "project.json", current.model_dump() | {"_undo": undo, "_redo": []})
            return current

    def restore(self, project_id: str, revision: int, direction: str) -> Project:
        with self.lock:
            doc = self.read_document(project_id)
            if doc["revision"] != revision:
                raise Conflict("Projekt zmienił się. Wczytaj aktualną wersję.")
            key, other = ("_undo", "_redo") if direction == "undo" else ("_redo", "_undo")
            stack = doc.get(key, [])
            if not stack:
                raise ValueError("Brak zmian do cofnięcia" if direction == "undo" else "Brak zmian do ponowienia")
            current = {k: v for k, v in doc.items() if not k.startswith("_")}
            restored = copy.deepcopy(stack[-1])
            # Never lose newly imported or generated immutable assets when undoing an edit.
            known = {a["id"] for a in restored["assets"]}
            restored["assets"] += [a for a in current["assets"] if a["id"] not in known]
            p = Project.model_validate(restored)
            p.revision = revision + 1
            p.updated_at = now()
            history = {key: stack[:-1], other: (doc.get(other, []) + [current])[-40:]}
            atomic_json(self.folder(project_id) / "project.json", p.model_dump() | history)
            return p

    def history(self, project_id: str) -> dict:
        doc = self.read_document(project_id)
        return {"undo": len(doc.get("_undo", [])), "redo": len(doc.get("_redo", []))}
