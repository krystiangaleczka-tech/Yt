"""The same project operations are used by FastAPI and the Studio CLI."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
from pathlib import Path

from .models import Project, Scene, Beat, Clip, uid
from .store import ProjectStore, atomic_json, now, story_hash
from .freshness import fingerprint, voice_state
from studio_timeline.operations import apply_operations


class ProjectService(ProjectStore):
    def patch(self, project_id, revision, changes):
        allowed = {"title", "language", "channel", "niche", "facts", "sources", "story", "scenes", "beats", "voice_profile", "pronunciation", "channel_id", "channel_profile", "budget", "archived", "published", "accepted_warnings", "development"}
        if not isinstance(changes, dict) or not set(changes) <= allowed:
            raise ValueError("Oś czasu i materiały mają osobne operacje")
        def update(project):
            candidate = Project.model_validate(project.model_dump() | changes)
            originals={s.id:s for s in project.scenes}
            for scene in candidate.scenes:
                old=originals.get(scene.id)
                if old and not scene.script_input_hash and scene.narration==old.narration and scene.fact_ids==old.fact_ids:
                    scene.script_input_hash=old.script_input_hash
            if "story" in changes:
                candidate.story["status"] = "DRAFT"; candidate.story["approved_hash"] = ""
            for key in changes:
                setattr(project, key, getattr(candidate, key))
            if "scenes" in changes:
                ops=[]
                tracks={t.id:t for t in project.sequence.tracks}
                for scene in project.scenes:
                    old=originals.get(scene.id)
                    if not old: continue
                    linked=[c for c in project.sequence.clips if c.scene_id==scene.id]
                    pictures=[c for c in linked if tracks[c.track_id].role=="picture"]
                    if old.duration!=scene.duration and len(pictures)>1:
                        raise ValueError("Ujęcie ma kilka ręcznie pociętych klipów. Zmień długość w Montażu, aby zachować cięcia.")
                    for clip in linked:
                        values={}
                        if old.start!=scene.start: values["start"]=clip.start+scene.start-old.start
                        if old.duration!=scene.duration and clip in pictures: values["duration"]=scene.duration
                        if values: ops.append({"type":"update_clip","clip_id":clip.id,"changes":values})
                if ops: apply_operations(project,ops)
        return self.mutate(project_id, revision, update)

    def edit(self, project_id, revision, operations, origin="manual"):
        return self.mutate(project_id, revision, lambda project: apply_operations(project, operations, origin))

    def duplicate(self, project_id, title=""):
        with self.lock:
            project = self.get(project_id)
            project.id = uid("prj_"); project.title = title or project.title + " — kopia"
            project.demo = False; project.archived = False; project.published = False
            project.story["status"] = "DRAFT"; project.story["approved_hash"] = ""
            original = self.folder(project_id) / "media"
            if original.exists():
                shutil.copytree(original, self.folder(project.id) / "media")
            return self.create(project)

    def scene_operation(self, project_id, revision, operation, scene_id, target=None):
        def update(project):
            index = next((i for i, s in enumerate(project.scenes) if s.id == scene_id), -1)
            if index < 0:
                raise ValueError("Nie ma takiego ujęcia")
            scene = project.scenes[index]
            linked = [c for c in project.sequence.clips if c.scene_id == scene_id]
            tracks = {t.id: t for t in project.sequence.tracks}
            if scene.locked or any(c.locked or tracks[c.track_id].locked for c in linked):
                raise ValueError("Odblokuj ujęcie i jego klipy przed zmianą")
            if operation == "duplicate":
                other = scene.model_copy(deep=True); other.id = uid("scene_"); other.title += " — kopia"
                other.start = max((s.start+s.duration for s in project.scenes), default=0)
                project.scenes.append(other)
                for clip in linked:
                    new = clip.model_copy(deep=True); new.id = uid("clip_"); new.scene_id = other.id
                    new.start += other.start-scene.start; new.group_id = ""
                    project.sequence.clips.append(new)
            elif operation == "remove":
                if scene.lock_media or scene.lock_timing or scene.lock_narration:
                    raise ValueError("Zwolnij blokady ujęcia przed usunięciem")
                project.scenes.pop(index)
                project.sequence.clips = [c for c in project.sequence.clips if c.scene_id != scene_id]
            elif operation == "move":
                destination = max(0, min(len(project.scenes)-1, int(target)))
                project.scenes.insert(destination, project.scenes.pop(index))
                frame = 0
                for s in project.scenes:
                    offset = frame-s.start
                    if offset and (s.locked or s.lock_timing):
                        raise ValueError("Zmiana kolejności przesunęłaby zablokowane ujęcie")
                    for clip in project.sequence.clips:
                        if clip.scene_id == s.id:
                            if offset and (clip.locked or tracks[clip.track_id].locked):
                                raise ValueError("Zmiana kolejności przesunęłaby zablokowany klip")
                            if offset and s.lock_narration and tracks[clip.track_id].role=="narration": raise ValueError("Zmiana kolejności przesunęłaby zablokowaną narrację")
                            clip.start += offset
                    s.start = frame; frame += s.duration
            else:
                raise ValueError("Nieznana operacja storyboardu")
        return self.mutate(project_id, revision, update)

    def save_version(self, project_id, name):
        project = self.get(project_id)
        version_id = uid("version_")
        atomic_json(self.folder(project_id) / "versions" / (version_id+".json"), {"id": version_id, "name": str(name)[:100] or "Wariant", "created_at": now(), "project": project.model_dump()})
        return {"id": version_id, "name": str(name), "revision": project.revision}

    def versions(self, project_id):
        result = []
        for file in (self.folder(project_id) / "versions").glob("version_*.json"):
            value = json.loads(file.read_text()); p = value.pop("project")
            result.append(value | {"revision": p["revision"], "clips": len(p["sequence"]["clips"])})
        return sorted(result, key=lambda v: v["created_at"], reverse=True)

    def version(self, project_id, version_id):
        if not re.fullmatch(r"version_[a-f0-9]{16}", version_id):
            raise ValueError("Niepoprawny wariant")
        return json.loads((self.folder(project_id) / "versions" / (version_id+".json")).read_text())

    def restore_version(self, project_id, revision, version_id):
        variant = Project.model_validate(self.version(project_id, version_id)["project"])
        def restore(project):
            assets = {a.id: a for a in project.assets}
            assets.update({a.id: a for a in variant.assets})
            for key in ("sequence", "scenes", "beats", "facts", "sources", "story", "title", "language", "voice_profile", "pronunciation", "development", "resource_links", "workspace_snapshot", "category_id", "category_profile", "film_format", "channel_id", "channel_profile", "channel"):
                setattr(project, key, copy.deepcopy(getattr(variant, key)))
            project.assets = list(assets.values())
        return self.mutate(project_id, revision, restore)

    def channels(self):
        return [json.loads(file.read_text()) for file in sorted((self.root / "channels").glob("channel_*.json"))]

    def save_channel(self, values):
        channel_id = str(values.get("id") or uid("channel_"))
        if not re.fullmatch(r"channel_[a-f0-9]{16}", channel_id):
            raise ValueError("Niepoprawny kanał")
        from .workspace_models import Preset
        allowed = {"id", "name", "motion", "rules", "revision"} | set(Preset.model_fields)
        if not set(values) <= allowed or not str(values.get("name", "")).strip():
            raise ValueError("Podaj nazwę i poprawne ustawienia kanału")
        settings = Preset.model_validate({k: v for k, v in values.items() if k in Preset.model_fields}).model_dump(exclude_none=True)
        values = {k: v for k, v in values.items() if k not in Preset.model_fields} | settings
        path = self.root / "channels" / (channel_id+".json")
        with self.lock:
            previous = json.loads(path.read_text()) if path.exists() else {}
            if previous and values.get("revision") != previous["revision"]:
                from .store import Conflict
                raise Conflict("Profil kanału zmienił się")
            result = values | {"id": channel_id, "revision": previous.get("revision", 0)+1}
            atomic_json(path, result)
        return result

    def channel_titles(self, project):
        titles = []
        for item in self.list(include_archived=True):
            p = self.get(item["id"])
            if (p.channel_id == project.channel_id or not p.channel_id and p.channel == project.channel) if project.channel_id else (p.channel == project.channel):
                titles.extend(p.topic_history)
                titles.extend(i.title for i in p.development.ideas)
                if p.published or p.id != project.id:
                    titles.append(p.title)
        return list(dict.fromkeys(titles))

    def relink(self, project_id, revision):
        def update(project):
            media=self.folder(project_id)/"media"
            for missing in project.assets:
                if not (media/missing.filename).is_file():
                    candidate=next((a for a in project.assets if a.sha256==missing.sha256 and (media/a.filename).is_file()),None)
                    if candidate:
                        source=media/candidate.filename
                        with source.open("rb") as stream:
                            if hashlib.file_digest(stream,"sha256").hexdigest()!=missing.sha256: raise ValueError("Plik do odzyskania nie zgadza się z sumą kontrolną")
                        shutil.copyfile(source,media/missing.filename)
            by_name = {}
            for asset in project.assets:
                by_name.setdefault(asset.name, []).append(asset)
            for scene in project.scenes:
                pending = scene.parameters.get("pending_files", [])
                matches = []
                for name in pending:
                    candidates = by_name.get(Path(name).name, [])
                    if len(candidates) > 1:
                        raise ValueError("Kolizja nazw: " + name + ". Wybierz właściwy materiał ręcznie.")
                    if candidates:
                        matches.append(candidates[0].id)
                if matches:
                    scene.asset_id = matches[0]; scene.asset_ids = matches
                    for clip in project.sequence.clips:
                        if clip.scene_id == scene.id and next(t for t in project.sequence.tracks if t.id == clip.track_id).kind == "video":
                            clip.asset_id = matches[0]; clip.asset_ids = matches
        return self.mutate(project_id, revision, update)
