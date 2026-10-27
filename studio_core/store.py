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
from .freshness import reconcile, fingerprint
from .locking import FileLock


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
    payload = {"story": {k: v for k, v in p.story.items() if k != "status" and not k.startswith("approved_")},
               "facts": [f.model_dump() for f in p.facts], "sources": [s.model_dump() for s in p.sources], "title": p.title}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Conflict(ValueError):
    pass


class ProjectStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = FileLock(self.root / ".project-service.lock")

    def folder(self, project_id: str) -> Path:
        if not re.fullmatch(r"prj_[a-f0-9]{16}", project_id):
            raise ValueError("Niepoprawny identyfikator projektu")
        return self.root / "projects" / project_id

    def read_document(self, project_id: str) -> dict:
        return json.loads((self.folder(project_id) / "project.json").read_text(encoding="utf-8"))

    def get(self, project_id: str) -> Project:
        doc = self.read_document(project_id)
        return Project.model_validate({k: v for k, v in doc.items() if not k.startswith("_")})

    def snapshot(self,project_id,value):
        if isinstance(value,str):
            if not re.fullmatch(r"hist_[a-f0-9]{32}",value):raise ValueError("Niepoprawny wpis historii")
            return value
        reference="hist_"+hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:32]
        path=self.folder(project_id)/"history"/(reference+".json")
        if not path.exists():atomic_json(path,value)
        return reference

    def history_value(self,project_id,value):
        if isinstance(value,dict):return copy.deepcopy(value)
        reference=self.snapshot(project_id,value)
        return json.loads((self.folder(project_id)/"history"/(reference+".json")).read_text())

    def prune_history(self,project_id,history):
        keep={reference for values in history.values() for reference in values if isinstance(reference,str)}
        for path in (self.folder(project_id)/"history").glob("hist_*.json"):
            if path.stem not in keep:path.unlink(missing_ok=True)

    def list(self, *, include_archived=False) -> list[dict]:
        result = []
        for path in (self.root / "projects").glob("prj_*/project.json"):
            try:
                p = self.get(path.parent.name)
                if p.archived and not include_archived:
                    continue
                result.append({"id": p.id, "title": p.title, "revision": p.revision, "updated_at": p.updated_at,
                               "scenes": len(p.scenes), "assets": len(p.assets), "demo": p.demo,
                               "duration": max((c.start + c.duration for c in p.sequence.clips), default=0),
                               "fps": p.sequence.fps_num / p.sequence.fps_den, "archived": p.archived, "channel": p.channel,
                               "next_step": next_step(p)})
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
            original = current.model_copy(deep=True)
            change(current)
            old_facts={f.id:f for f in original.facts}
            old_sources={s.id:s for s in original.sources}
            for fact in current.facts:
                old=old_facts.get(fact.id)
                source=next((s for s in current.sources if s.id==fact.source_id),None)
                evidence_changed=old and any(getattr(old,k)!=getattr(fact,k) for k in ("claim","source","url","page","quote","source_id"))
                source_changed=source and source.id in old_sources and source!=old_sources[source.id]
                if old and (evidence_changed or source_changed): fact.status="UNVERIFIED";fact.checked_at=""
                elif fact.status=="VERIFIED" and (not old or old.status!="VERIFIED"): fact.checked_at=now()
            validate_scene_locks(original, current)
            reconcile(original, current)
            if story_hash(current) != previous_story:
                current.story["status"] = "DRAFT"
                current.story["approved_hash"] = ""
            current = Project.model_validate(current.model_dump())
            current.id = project_id
            current.revision = revision + 1
            current.updated_at = now()
            undo = (document.get("_undo", []) + [before])[-40:] if history else document.get("_undo", [])
            pointers={"_undo":[self.snapshot(project_id,value) for value in undo],"_redo":[]}
            atomic_json(self.folder(project_id) / "project.json", current.model_dump() | pointers)
            self.prune_history(project_id,pointers)
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
            restored = self.history_value(project_id,stack[-1])
            # Never lose newly imported or generated immutable assets when undoing an edit.
            known = {a["id"] for a in restored["assets"]}
            restored["assets"] += [a for a in current["assets"] if a["id"] not in known]
            p = Project.model_validate(restored)
            p.revision = revision + 1
            p.updated_at = now()
            history = {key:[self.snapshot(project_id,value) for value in stack[:-1]],other:[self.snapshot(project_id,value) for value in (doc.get(other, []) + [current])[-40:]]}
            atomic_json(self.folder(project_id) / "project.json", p.model_dump() | history)
            self.prune_history(project_id,history)
            return p

    def history(self, project_id: str) -> dict:
        doc = self.read_document(project_id)
        return {"undo": len(doc.get("_undo", [])), "redo": len(doc.get("_redo", []))}


def next_step(project: Project) -> str:
    if not project.facts:
        return "Dodaj źródła i fakty"
    if project.story.get("status") != "APPROVED":
        return "Zatwierdź kartę historii"
    if not project.scenes:
        return "Przygotuj scenariusz"
    missing = sum(not s.asset_id and s.template == "media" for s in project.scenes)
    if missing:
        return f"Wybierz materiał do {missing} ujęć"
    from .freshness import voice_state
    missing = sum(voice_state(project, s) in ("missing", "stale") for s in project.scenes)
    return f"Przygotuj lub odśwież {missing} nagrań" if missing else "Sprawdź montaż i eksportuj film"


def validate_scene_locks(before: Project, after: Project) -> None:
    from .freshness import voice_hash
    scenes = {s.id: s for s in after.scenes}
    for old in before.scenes:
        new = scenes.get(old.id)
        if new and old.narration.strip() and (old.locked or old.lock_narration) and voice_hash(before,old)!=voice_hash(after,new):
            raise ValueError("Profil, język lub wymowa zmieniłyby zablokowaną narrację")
        if new == old:
            continue
        if old.locked:
            if new != old.model_copy(update={"locked": False}):
                raise ValueError("Odblokuj ujęcie przed zmianą jego treści")
            continue
        for flag, fields in {
            "lock_narration": ("narration", "voice_asset_id", "voice_profile", "sentences", "words", "alignment_hash"),
            "lock_timing": ("start", "duration"),
            "lock_media": ("asset_id", "asset_ids", "template", "parameters", "prompt", "animation", "motion_prompt"),
        }.items():
            if getattr(old, flag) and (new is None or any(getattr(old, field) != getattr(new, field) for field in fields)):
                raise ValueError("Najpierw zwolnij odpowiednią blokadę ujęcia")
