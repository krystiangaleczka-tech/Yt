from __future__ import annotations

import copy
from typing import Any

from studio_core.models import Clip, Project, Track, uid


def apply_operations(project: Project, operations: list[dict[str, Any]], origin: str = "manual") -> None:
    if not operations or len(operations) > 200:
        raise ValueError("Wymagane od jednej do dwustu operacji")
    # Work on a detached copy: an invalid later operation cannot partially apply a batch.
    draft = project.model_copy(deep=True)
    for op in operations:
        kind = op.get("type")
        if kind == "set_sequence":
            if origin != "manual" or not set(op.get("changes", {})) <= {"width", "height"}:
                raise ValueError("Tylko użytkownik zmienia rozmiar sekwencji")
            draft.sequence = type(draft.sequence).model_validate(draft.sequence.model_dump() | op["changes"])
            continue
        tracks = {t.id: t for t in draft.sequence.tracks}
        clip = next((c for c in draft.sequence.clips if c.id == op.get("clip_id")), None)
        if kind == "add_track":
            draft.sequence.tracks.append(Track.model_validate(op["track"]))
            continue
        if kind == "update_track":
            track = tracks.get(op.get("track_id"))
            if not track:
                raise ValueError("Nie ma takiej ścieżki")
            changes = op.get("changes", {})
            if origin == "ai" and (track.locked or "locked" in changes):
                raise ValueError("AI nie może zmieniać ani odblokowywać zablokowanych ścieżek")
            if not set(changes) <= {"name", "locked", "muted"}:
                raise ValueError("Nieobsługiwane pola ścieżki")
            updated = Track.model_validate(track.model_dump() | changes)
            draft.sequence.tracks = [updated if t.id == track.id else t for t in draft.sequence.tracks]
            continue
        if kind == "add_clip":
            new = Clip.model_validate(op["clip"])
            if new.track_id not in tracks or tracks[new.track_id].locked:
                raise ValueError("Nie można dodać klipu na zablokowaną lub nieistniejącą ścieżkę")
            draft.sequence.clips.append(new)
            continue
        if not clip:
            raise ValueError("Nie ma takiego klipu")
        changes = op.get("changes", {})
        unlock_only = origin == "manual" and kind == "update_clip" and changes == {"locked": False}
        if (clip.locked or tracks[clip.track_id].locked) and not unlock_only:
            raise ValueError(f"Klip {clip.title} lub jego ścieżka jest zablokowana")
        if origin == "ai" and "locked" in changes:
            raise ValueError("AI nie zmienia blokad użytkownika")
        if kind == "ripple_remove":
            end = clip.start + clip.duration
            for later in draft.sequence.clips:
                if later.id != clip.id and later.track_id == clip.track_id and later.start >= end:
                    if later.locked:
                        raise ValueError("Dalszy klip jest zablokowany; nie można zamknąć luki")
                    later.start -= clip.duration
            draft.sequence.clips.remove(clip)
        elif kind == "remove_clip":
            draft.sequence.clips.remove(clip)
        elif kind in ("update_clip", "move_clip", "trim_clip"):
            allowed = set(Clip.model_fields) - {"id", "scene_id"}
            if not set(changes) <= allowed:
                raise ValueError("Nieobsługiwane pola klipu")
            if changes.get("track_id", clip.track_id) not in tracks or tracks[changes.get("track_id", clip.track_id)].locked:
                raise ValueError("Docelowa ścieżka jest zablokowana lub nie istnieje")
            replacement = Clip.model_validate(clip.model_dump() | changes)
            draft.sequence.clips = [replacement if c.id == clip.id else c for c in draft.sequence.clips]
        elif kind == "split_clip":
            at = op.get("frame")
            if not isinstance(at, int) or not clip.start < at < clip.start + clip.duration:
                raise ValueError("Podział musi wypadać wewnątrz klipu")
            if clip.keyframes:
                raise ValueError("Przed podziałem usuń keyframes albo podziel klip bez animacji punktowej")
            offset = at - clip.start
            right = clip.model_copy(deep=True)
            right.id = uid("clip_")
            right.start = at
            right.duration = clip.duration - offset
            right.source_in += round(offset * clip.speed)
            right.fade_in = 0
            clip.duration = offset
            clip.fade_out = 0
            draft.sequence.clips.append(right)
        else:
            raise ValueError(f"Nieobsługiwana operacja: {kind}")
    # One scene can have multiple clips; primary picture defines its displayed timing.
    for scene in draft.scenes:
        clips = [c for c in draft.sequence.clips if c.scene_id == scene.id and tracks.get(c.track_id) and tracks[c.track_id].role == "picture"]
        if clips:
            scene.start = min(c.start for c in clips)
            scene.duration = max(c.start + c.duration for c in clips) - scene.start
    validated = Project.model_validate(draft.model_dump())
    project.sequence = validated.sequence
    project.scenes = validated.scenes
