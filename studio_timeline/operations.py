from __future__ import annotations

import copy
from typing import Any

from studio_core.models import Clip, Project, Track, uid,fps


def apply_operations(project: Project, operations: list[dict[str, Any]], origin: str = "manual") -> None:
    if not operations or len(operations) > 200:
        raise ValueError("Wymagane od jednej do dwustu operacji")
    # Work on a detached copy: an invalid later operation cannot partially apply a batch.
    draft = project.model_copy(deep=True)
    tracks = {t.id: t for t in draft.sequence.tracks}
    for op in operations:
        kind = op.get("type")
        if kind in ("group_clips", "ungroup_clips"):
            ids = set(op.get("clip_ids", []))
            members = [c for c in draft.sequence.clips if c.id in ids]
            if not ids or len(members) != len(ids):
                raise ValueError("Wybierz istniejące klipy do grupowania")
            group = uid("group_") if kind == "group_clips" else ""
            for member in members:
                ensure_unlocked(draft, member, {"group_id": group})
                member.group_id = group
            continue
        if kind == "set_sequence":
            if origin != "manual" or not set(op.get("changes", {})) <= {"width", "height", "fps_num", "fps_den", "ducking", "ducking_gain"}:
                raise ValueError("Tylko użytkownik zmienia rozmiar sekwencji")
            old_rate=fps(draft)
            draft.sequence = type(draft.sequence).model_validate(draft.sequence.model_dump() | op["changes"])
            factor=fps(draft)/old_rate
            if factor!=1:
                for clip in draft.sequence.clips:
                    ensure_unlocked(draft,clip,{"start":clip.start,"duration":clip.duration,"source_in":clip.source_in})
                    end=round((clip.start+clip.duration)*factor);clip.start=round(clip.start*factor);clip.duration=max(1,end-clip.start);clip.source_in=round(clip.source_in*factor)
                    clip.fade_in=round(clip.fade_in*factor);clip.fade_out=round(clip.fade_out*factor);clip.transition_duration=min(clip.duration,round(clip.transition_duration*factor))
                    points={}
                    for key in clip.keyframes:
                        key.frame=min(clip.duration,round(key.frame*factor));points[key.property,key.frame]=key
                    clip.keyframes=list(points.values())
                for scene in draft.scenes:
                    end=round((scene.start+scene.duration)*factor);scene.start=round(scene.start*factor);scene.duration=max(1,end-scene.start)
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
            if not set(changes) <= {"name", "locked", "muted", "solo"}:
                raise ValueError("Nieobsługiwane pola ścieżki")
            updated = Track.model_validate(track.model_dump() | changes)
            draft.sequence.tracks = [updated if t.id == track.id else t for t in draft.sequence.tracks]
            continue
        if kind == "add_clip":
            new = Clip.model_validate(op["clip"])
            if new.track_id not in tracks or tracks[new.track_id].locked:
                raise ValueError("Nie można dodać klipu na zablokowaną lub nieistniejącą ścieżkę")
            scene = next((s for s in draft.scenes if s.id == new.scene_id), None)
            if scene and (scene.locked or scene.lock_timing or scene.lock_media):
                raise ValueError("Ujęcie jest zablokowane; odblokuj je przed dodaniem klipu")
            draft.sequence.clips.append(new)
            continue
        if not clip:
            raise ValueError("Nie ma takiego klipu")
        changes = op.get("changes", {})
        unlock_only = origin == "manual" and kind == "update_clip" and changes == {"locked": False}
        if (clip.locked or tracks[clip.track_id].locked) and not unlock_only:
            raise ValueError(f"Klip {clip.title} lub jego ścieżka jest zablokowana")
        if not unlock_only:
            ensure_unlocked(draft, clip, changes, destructive=kind in ("remove_clip", "ripple_remove", "split_clip"))
        if origin == "ai" and "locked" in changes:
            raise ValueError("AI nie zmienia blokad użytkownika")
        if kind == "ripple_remove":
            end = clip.start + clip.duration
            for later in draft.sequence.clips:
                if later.id != clip.id and later.track_id == clip.track_id and later.start >= end:
                    if later.locked:
                        raise ValueError("Dalszy klip jest zablokowany; nie można zamknąć luki")
                    ensure_unlocked(draft, later, {"start": later.start - clip.duration})
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
            if kind == "move_clip" and clip.group_id and op.get("move_group",True):
                delta=replacement.start-clip.start
                for member in draft.sequence.clips:
                    if member.id!=clip.id and member.group_id==clip.group_id:
                        ensure_unlocked(draft,member,{"start":member.start+delta})
                        member.start+=delta
            draft.sequence.clips = [replacement if c.id == clip.id else c for c in draft.sequence.clips]
        elif kind == "split_clip":
            at = op.get("frame")
            if not isinstance(at, int) or not clip.start < at < clip.start + clip.duration:
                raise ValueError("Podział musi wypadać wewnątrz klipu")
            offset = at - clip.start
            right = clip.model_copy(deep=True)
            right.id = uid("clip_")
            right.start = at
            right.duration = clip.duration - offset
            right.source_in += round(offset * clip.speed)
            right.fade_in = 0
            left_keys, right_keys = [], []
            for prop in {k.property for k in clip.keyframes}:
                value = value_at(clip, prop, offset)
                Key = type(next(k for k in clip.keyframes if k.property == prop))
                left_keys.extend(k for k in clip.keyframes if k.property == prop and k.frame < offset)
                left_keys.append(Key(property=prop, frame=offset, value=value))
                right_keys.append(Key(property=prop, frame=0, value=value))
                right_keys.extend(k.model_copy(update={"frame": k.frame-offset}) for k in clip.keyframes if k.property == prop and k.frame > offset)
            clip.keyframes, right.keyframes = left_keys, right_keys
            clip.duration = offset
            clip.fade_out = 0
            clip.fade_in = min(clip.fade_in, clip.duration)
            clip.transition_duration = min(clip.transition_duration, clip.duration)
            right.transition = "cut"; right.transition_duration = 0
            right.fade_out = min(right.fade_out, right.duration)
            draft.sequence.clips.append(right)
        else:
            raise ValueError(f"Nieobsługiwana operacja: {kind}")
    # One scene can have multiple clips; primary picture defines its displayed timing.
    tracks = {t.id: t for t in draft.sequence.tracks}
    for scene in draft.scenes:
        clips = [c for c in draft.sequence.clips if c.scene_id == scene.id and tracks.get(c.track_id) and tracks[c.track_id].role == "picture"]
        if clips:
            scene.start = min(c.start for c in clips)
            scene.duration = max(c.start + c.duration for c in clips) - scene.start
    validated = Project.model_validate(draft.model_dump())
    project.sequence = validated.sequence
    project.scenes = validated.scenes


def ensure_unlocked(project: Project, clip: Clip, changes: dict, destructive=False) -> None:
    track = next(t for t in project.sequence.tracks if t.id == clip.track_id)
    scene = next((s for s in project.scenes if s.id == clip.scene_id), None)
    if clip.locked or track.locked or scene and scene.locked:
        raise ValueError("Klip, ścieżka lub powiązane ujęcie jest zablokowane")
    if scene:
        timing = {"start", "duration", "speed", "source_in", "track_id"}
        media = {"asset_id", "asset_ids", "template", "parameters", "text", "animation", "keyframes", "crop"}
        if scene.lock_timing and (destructive or timing & changes.keys()):
            raise ValueError("Czas ujęcia jest zablokowany")
        if scene.lock_media and (destructive or media & changes.keys()):
            raise ValueError("Materiał ujęcia jest zablokowany")
        if scene.lock_narration and track.role == "narration" and (destructive or changes):
            raise ValueError("Narracja ujęcia jest zablokowana")


def value_at(clip: Clip, prop: str, frame: int) -> float:
    points = sorted([k for k in clip.keyframes if k.property == prop], key=lambda k: k.frame)
    previous_frame, previous_value = 0, getattr(clip, prop)
    for point in points:
        if point.frame >= frame:
            if point.frame == previous_frame:
                return point.value
            return previous_value + (point.value-previous_value) * (frame-previous_frame) / (point.frame-previous_frame)
        previous_frame, previous_value = point.frame, point.value
    return previous_value
