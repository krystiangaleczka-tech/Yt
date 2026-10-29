import io
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from studio_api.app import create_app
from studio_core.models import Project, Clip, Asset
from studio_core.inserts import MotionInsert, definition, signature
from studio_core.bundles import export_bundle, import_bundle
from studio_workers.motion import run_motion

H = {"X-Docos-Request": "1"}


class MotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        self.store = self.app.state.store
        self.p = self.store.create(Project(title="Motion test"))
        self.base = "/api/projects/" + self.p.id

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def save(self, item, revision=None):
        revision = self.store.get(self.p.id).revision if revision is None else revision
        return self.client.post(self.base + "/inserts", json={"expected_revision": revision, "insert": item.model_dump()}, headers=H)

    def image(self):
        f = io.BytesIO(); Image.new("RGB", (320, 180), "red").save(f, format="PNG")
        return self.client.post(self.base + "/media", files={"file": ("photo.png", f.getvalue(), "image/png")}, headers=H).json()["asset"]["id"]

    def rendered(self, item):
        asset = Asset(id="asset_" + "a" * 20, name="render.mp4", filename="asset_" + "a" * 20 + ".mp4", kind="video", mime="video/mp4", sha256="fake", duration=6)
        def change(p):
            p.assets.append(asset)
            target = p.inserts[0]
            target.rendered_asset_id = asset.id
            target.rendered_signature = signature(p, target)
        self.store.mutate(self.p.id, self.store.get(self.p.id).revision, change)
        return asset

    def test_old_projects_default_to_empty_inserts(self):
        raw = self.p.model_dump(); del raw["inserts"]
        self.assertEqual(Project.model_validate(raw).inserts, [])

    def test_save_revision_conflicts_and_undo(self):
        item = MotionInsert(title="Chapter")
        result = self.save(item)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(self.save(item, revision=1).status_code, 409)
        p = self.store.restore(self.p.id, result.json()["revision"], "undo")
        self.assertEqual(p.inserts, [])

    def test_no_remote_images_or_nonimage_assets(self):
        item = MotionInsert(template="photo", image_ids=["https://example.com/x.png"])
        self.assertEqual(self.save(item).status_code, 422)
        image_id = self.image(); item.image_ids = [image_id]
        self.assertEqual(self.save(item).status_code, 200)
        with self.assertRaises(ValueError):
            MotionInsert(accent="red; background: url(http://evil)")
        with self.assertRaises(ValueError):
            MotionInsert(data=[{"label": "bad", "value": float("nan")}])

    def test_changed_definition_invalidates_render(self):
        item = MotionInsert(); self.save(item); self.rendered(item)
        unchanged = self.save(item).json()["inserts"][0]
        self.assertIsNotNone(unchanged["rendered_asset_id"])
        item.title = "Changed"
        changed = self.save(item).json()["inserts"][0]
        self.assertIsNone(changed["rendered_asset_id"])
        self.assertEqual(len(self.store.get(self.p.id).assets), 1)

    def test_render_signature_includes_resolution_and_fps(self):
        item = MotionInsert(); self.save(item); self.rendered(item)
        current = self.store.get(self.p.id)
        self.store.mutate(self.p.id, current.revision, lambda p: setattr(p.sequence, "width", 1920))
        r = self.client.post(self.base + f"/inserts/{item.id}/to-timeline", json={"expected_revision": self.store.get(self.p.id).revision}, headers=H)
        self.assertEqual(r.status_code, 422, r.text)
        self.assertEqual(self.store.get(self.p.id).sequence.clips, [])

    def test_timeline_handoff_is_explicit_and_keeps_old_clips(self):
        item = MotionInsert(); self.save(item); a = self.rendered(item)
        p = self.store.get(self.p.id)
        response = self.client.post(self.base + f"/inserts/{item.id}/to-timeline", json={"expected_revision": p.revision, "start": 90}, headers=H)
        self.assertEqual(response.status_code, 200, response.text)
        clip = response.json()["sequence"]["clips"][0]
        self.assertEqual((clip["asset_id"], clip["start"], clip["duration"]), (a.id, 90, 180))
        item.title = "New version"; self.save(item)
        self.assertEqual(self.store.get(self.p.id).sequence.clips[0].asset_id, a.id)

    def test_locked_track_rejects_handoff(self):
        item = MotionInsert(); self.save(item); self.rendered(item)
        p = self.store.get(self.p.id)
        self.store.mutate(p.id, p.revision, lambda p: setattr(p.sequence.tracks[0], "locked", True))
        r = self.client.post(self.base + f"/inserts/{item.id}/to-timeline", json={"expected_revision": self.store.get(p.id).revision}, headers=H)
        self.assertEqual(r.status_code, 422)

    def test_missing_photos_and_duration_limit_stop_before_queue(self):
        item = MotionInsert(template="compare")
        self.save(item)
        r = self.client.post(self.base + f"/inserts/{item.id}/render", json={"expected_revision": self.store.get(self.p.id).revision}, headers=H)
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self.app.state.jobs.list(), [])
        item.template = "chapter"; item.duration = 1801; self.save(item)
        r = self.client.post(self.base + f"/inserts/{item.id}/render", json={"expected_revision": self.store.get(self.p.id).revision}, headers=H)
        self.assertEqual(r.status_code, 422)

    def test_ai_proposal_is_validated_but_never_saved(self):
        item = MotionInsert(title="Original"); self.save(item)
        changed = item.model_copy(update={"zoom": 1.3, "title": "Proposed"})
        base = self.base + f"/inserts/{item.id}/assistant/"
        revision=self.store.get(self.p.id).revision
        response = self.client.post(base + "import", json={"base_revision":revision,"response": json.dumps(changed.model_dump())}, headers=H)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["insert"]["title"], "Proposed")
        self.assertEqual(self.store.get(self.p.id).inserts[0].title, "Original")
        changed.image_ids = ["not-in-project"]
        self.assertEqual(self.client.post(base + "import", json={"base_revision":revision,"response": json.dumps(changed.model_dump())}, headers=H).status_code, 422)
        changed.image_ids = []; changed.id = MotionInsert().id
        self.assertEqual(self.client.post(base + "import", json={"base_revision":revision,"response": json.dumps(changed.model_dump())}, headers=H).status_code, 422)
        prompt = self.client.post(base + "prompt", json={"command": "Zoom"}, headers=H).json()["prompt"]
        self.assertIn("Do not invent", prompt)

    def test_motion_proposal_from_old_prompt_is_rejected(self):
        item=MotionInsert();self.save(item)
        path=self.base+f"/inserts/{item.id}/assistant/"
        prompt=self.client.post(path+"prompt",json={},headers=H).json()
        self.store.mutate(self.p.id,prompt["base_revision"],lambda p:setattr(p,"title","Changed"))
        result=self.client.post(path+"import",json={"base_revision":prompt["base_revision"],"response":json.dumps(item.model_dump())},headers=H)
        self.assertEqual(result.status_code,409,result.text)

    def test_insert_credits_include_source_photo_without_duplicate_generated_license_warning(self):
        from studio_core.exports import attribution
        from studio_core.quality import check_project
        item=MotionInsert(template="photo",image_ids=[self.image()]);self.save(item);asset=self.rendered(item)
        p=self.store.get(self.p.id)
        def change(p):
            p.assets[-1].provenance={"kind":"remotion","definition":definition(item)}
            p.sequence.clips.append(Clip(track_id="v1",asset_id=asset.id,duration=30))
        p=self.store.mutate(p.id,p.revision,change)
        self.assertIn(item.image_ids[0],{a["id"] for a in attribution(p)})
        warnings={i["code"] for i in check_project(self.store,p)["issues"]}
        self.assertIn("license:"+item.image_ids[0],warnings)
        self.assertNotIn("license:"+asset.id,warnings)

    def test_json_import_clears_media_references(self):
        item = MotionInsert(template="photo", image_ids=[self.image()]); self.save(item)
        raw = self.store.get(self.p.id).model_dump()
        result = self.client.post("/api/projects/import", files={"file": ("p.json", json.dumps(raw), "application/json")}, headers=H)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()["inserts"][0]["image_ids"], [])

    def test_bundle_roundtrip_preserves_editable_parameters(self):
        item = MotionInsert(template="photo", image_ids=[self.image()], zoom=1.3, saturation=.5)
        self.save(item)
        original = self.store.get(self.p.id)
        result = import_bundle(self.store, export_bundle(self.store, original))
        self.assertNotEqual(result.id, original.id)
        self.assertEqual(definition(result.inserts[0]), definition(item))
        self.assertTrue((self.store.folder(result.id) / "media" / result.assets[0].filename).is_file())

    def test_delete_keeps_rendered_clips(self):
        item = MotionInsert(); self.save(item); self.rendered(item)
        p = self.store.get(self.p.id)
        result = self.client.post(self.base + f"/inserts/{item.id}/delete", json={"expected_revision": p.revision}, headers=H)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["inserts"], [])
        self.assertEqual(len(result.json()["assets"]), 1)

    def test_worker_registers_snapshot_but_does_not_attach_a_stale_render(self):
        # Test worker bookkeeping with a real valid video, replacing only Node execution.
        item = MotionInsert(duration=15); self.save(item)
        p = self.store.get(self.p.id)
        fixture = Path(self.temp.name) / "fixture.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=blue:s=1280x720:r=30:d=0.5", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(fixture)], check=True)
        actual_popen = subprocess.Popen
        def fake_node(cmd, **kwargs):
            if Path(cmd[0]).name != "node":
                return actual_popen(cmd, **kwargs)
            shutil.copyfile(fixture, cmd[-1])
            current = self.store.get(p.id)
            self.store.mutate(p.id, current.revision, lambda p: setattr(p.inserts[0], "title", "Edited while rendering"))
            class Done:
                returncode = 0
                def poll(self): return 0
            return Done()
        with patch("studio_workers.motion.runtime_ready", return_value=True), patch("studio_workers.motion.subprocess.Popen", side_effect=fake_node):
            result = run_motion(self.store, p, item.id, "job_test", lambda *args: None, threading.Event())
        self.assertFalse(result["attached"])
        current = self.store.get(p.id)
        self.assertIsNone(current.inserts[0].rendered_asset_id)
        self.assertEqual(current.assets[-1].provenance["definition"]["title"], item.title)
        self.assertFalse((self.store.folder(p.id) / "jobs/job_test/public").exists())


if __name__ == "__main__":
    unittest.main()
