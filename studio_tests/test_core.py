import copy
import json
import tempfile
import unittest
from pathlib import Path

from studio_core.models import Project, Scene, Clip, Fact, Asset, from_docos
from studio_core.store import ProjectStore, Conflict, story_hash
from studio_timeline.operations import apply_operations
from studio_core.assistant import parse_proposal
from studio_core.writer import import_response


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = ProjectStore(Path(self.temp.name))
        self.p = self.store.create(Project())

    def tearDown(self):
        self.temp.cleanup()

    def test_stale_writer_cannot_overwrite(self):
        self.store.mutate(self.p.id, self.p.revision, lambda p: setattr(p, "title", "Wersja pierwsza"))
        with self.assertRaises(Conflict):
            self.store.mutate(self.p.id, self.p.revision, lambda p: setattr(p, "title", "Nadpisanie"))
        self.assertEqual(self.store.get(self.p.id).title, "Wersja pierwsza")

    def test_history_survives_reopening_and_redo(self):
        p = self.store.mutate(self.p.id, 1, lambda p: setattr(p, "title", "Nowy tytuł"))
        reopened = ProjectStore(Path(self.temp.name))
        back = reopened.restore(p.id, p.revision, "undo")
        self.assertEqual(back.title, "Nowy dokument")
        forward = reopened.restore(p.id, back.revision, "redo")
        self.assertEqual(forward.title, "Nowy tytuł")
        self.assertGreater(forward.revision, p.revision)

    def test_fact_change_revokes_story_approval(self):
        def approve(p):
            p.story["status"] = "APPROVED"; p.story["approved_hash"] = story_hash(p)
        p = self.store.mutate(self.p.id, 1, approve)
        p = self.store.mutate(p.id, p.revision, lambda p: p.facts.append(Fact(claim="Nowe twierdzenie")))
        self.assertEqual(p.story["status"], "DRAFT")

    def test_legacy_import_preserves_unknown_fields_and_does_not_approve(self):
        raw = {"meta": {"title": "Dawny projekt", "custom": 17}, "beats": [{"id": "B01", "narration": "Hello.", "shots": [{"dur": 3, "desc": "FILE: absent.mp4", "custom": 7}]}], "experimental": {"x": 3}}
        p = from_docos(raw)
        self.assertEqual(p.legacy, raw)
        self.assertEqual(p.scenes[0].legacy["shot"]["custom"], 7)
        self.assertEqual(p.story["status"], "DRAFT")
        self.assertIsNone(p.scenes[0].asset_id)


class EditingTests(unittest.TestCase):
    def project(self):
        p = Project()
        p.sequence.clips.append(Clip(id="c1", track_id="v1", title="Kadr", duration=300))
        return p

    def test_atomic_batch_rejects_later_locked_edit(self):
        p = self.project(); p.sequence.tracks[3].locked = True
        p.sequence.clips.append(Clip(id="voice", track_id="a1", duration=300))
        before = p.model_dump()
        with self.assertRaises(ValueError):
            apply_operations(p, [{"type": "move_clip", "clip_id": "c1", "changes": {"start": 30}}, {"type": "remove_clip", "clip_id": "voice"}], "ai")
        self.assertEqual(p.model_dump(), before)

    def test_split_uses_speed_and_source_in(self):
        p = self.project(); p.sequence.clips[0].source_in = 60; p.sequence.clips[0].speed = 2
        apply_operations(p, [{"type": "split_clip", "clip_id": "c1", "frame": 100}])
        left, right = p.sequence.clips
        self.assertEqual((left.duration, right.duration, right.source_in), (100, 200, 260))

    def test_scene_timing_follows_primary_picture(self):
        p = self.project(); scene = Scene(); p.scenes.append(scene); p.sequence.clips[0].scene_id = scene.id
        apply_operations(p, [{"type": "move_clip", "clip_id": "c1", "changes": {"start": 45}}])
        self.assertEqual(p.scenes[0].start, 45)

    def test_ai_cannot_unlock_and_scope_cannot_expand(self):
        p = self.project(); p.sequence.clips[0].locked = True
        with self.assertRaises(ValueError):
            parse_proposal('{"operations":[{"type":"update_clip","clip_id":"c1","changes":{"locked":false}}]}', p, [])
        with self.assertRaises(ValueError):
            parse_proposal('{"operations":[{"type":"remove_clip","clip_id":"c1"}]}', p, ["other"])

    def test_manual_unlock_is_explicit(self):
        p = self.project(); p.sequence.clips[0].locked = True
        apply_operations(p, [{"type": "update_clip", "clip_id": "c1", "changes": {"locked": False}}])
        self.assertFalse(p.sequence.clips[0].locked)

    def test_missing_asset_cannot_be_injected(self):
        p = self.project()
        with self.assertRaises(ValueError):
            apply_operations(p, [{"type": "update_clip", "clip_id": "c1", "changes": {"asset_id": "guessed"}}])
        self.assertIsNone(p.sequence.clips[0].asset_id)

    def test_invalid_keyframes_rejected(self):
        p = self.project()
        with self.assertRaises(ValueError):
            apply_operations(p, [{"type": "update_clip", "clip_id": "c1", "changes": {"keyframes": [{"property": "opacity", "frame": 5, "value": 20}]}}])

    def test_writer_cannot_inject_unverified_fact(self):
        p = self.project(); p.story["status"] = "APPROVED"; p.facts.append(Fact(id="F1", claim="test"))
        with self.assertRaises(ValueError):
            import_response(p, "script", json.dumps([{"narration": "Claim", "fact_ids": ["F1"]}]))


if __name__ == "__main__":
    unittest.main()
