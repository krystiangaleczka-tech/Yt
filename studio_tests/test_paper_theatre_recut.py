"""Paper Theatre re-cut: prompts, settings, job wiring, accept/revert and worker rules."""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from studio_api.app import create_app
from studio_core import paper_theatre_recut as recut

HEADERS = {"X-Docos-Request": "1"}
HAS_CV2 = importlib.util.find_spec("cv2") is not None
REPO = Path(__file__).resolve().parents[1]


def rgba(size, box, color, shape="rect"):
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    (draw.ellipse if shape == "disc" else draw.rectangle)(box, fill=(*color, 255))
    return image


class RecutPromptTests(unittest.TestCase):
    def test_auto_prompt_uses_opaque_bounds_and_deepest_point(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "x.png"
            rgba((200, 100), (40, 20, 119, 69), (200, 10, 10)).save(path)
            p = recut.auto_prompt(path, "props")
            self.assertEqual(p["box"], [40, 20, 120, 70])
            x, y = p["pos"][0]
            self.assertTrue(55 <= x <= 105 and 35 <= y <= 55, p)
            self.assertTrue(p["auto"])
            rgba((200, 200), (40, 40, 159, 159), (200, 60, 30), "disc").save(path)
            self.assertEqual(recut.auto_prompt(path, "sky")["hull"], "circle")
            self.assertEqual(recut.auto_prompt(path, "props")["hull"], "auto")

    def test_settings_are_bounded_and_scene_scoped(self):
        class Scene:
            asset_ids = ["asset_a", "asset_b"]
        ok = recut.normalize_settings({
            "prompts": {"asset_a": {"box": [-20, 5, 500, 60], "pos": [[10, 10]], "neg": []}},
            "depth": {"asset_b": 9.5},
            "extra_objects": [{"key": "extra_1", "name": "Bambus", "group": "props",
                               "prompt": {"box": [1, 1, 30, 30], "pos": [[5, 5]]}}],
            "options": {"leftover": "merge", "smear_strokes": [{"points": [[1, 1], [9, 9]], "width": 12}]},
        }, Scene, 320, 180)
        self.assertEqual(ok["prompts"]["asset_a"]["box"], [0, 5, 320, 60])
        self.assertEqual(ok["options"]["leftover"], "merge")
        self.assertTrue(ok["options"]["fix_seams"] and ok["options"]["complete_scenery"])
        bad = [
            {"prompts": {"asset_x": {"box": [0, 0, 9, 9], "pos": [[1, 1]]}}},
            {"prompts": {"asset_a": {"box": [0, 0, 9, 9], "pos": []}}},
            {"prompts": {"asset_a": {"box": [0, 0, 1, 1], "pos": [[0, 0]]}}},
            {"prompts": {"asset_a": {"box": [0, 0, 9, 9], "pos": [[1, 1]] * 13}}},
            {"extra_objects": [{"key": "extra_1", "name": "Drugi", "group": "hero",
                                "prompt": {"box": [1, 1, 9, 9], "pos": [[2, 2]]}}]},
            {"options": {"leftover": "blur"}},
            {"options": {"smear_strokes": [{"points": [[1, 1]], "width": 500}]}},
        ]
        for case in bad:
            with self.assertRaises(ValueError, msg=str(case)):
                recut.normalize_settings(case, Scene, 320, 180)


class RecutApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        self.project = self.client.post("/api/projects", json={"title": "Rozcięcie"}, headers=HEADERS).json()
        self.base = "/api/projects/" + self.project["id"]
        self.bg = self.upload("tlo", Image.new("RGB", (320, 180), (190, 166, 133)))
        self.sun = self.upload("slonce", rgba((320, 180), (200, 20, 260, 80), (210, 70, 40), "disc"))
        self.wall = self.upload("mur", rgba((320, 180), (40, 90, 280, 150), (150, 140, 120)))
        self.hero = self.upload("cesarz", rgba((320, 180), (120, 60, 170, 170), (30, 30, 30)))
        rev = self.client.get(self.base).json()["revision"]
        shot = self.client.post(self.base + "/paper-theatre/scenes", json={"expected_revision": rev}, headers=HEADERS).json()
        self.sid = shot["scenes"][-1]["id"]
        rev = shot["revision"]
        r = self.client.post(f"{self.base}/paper-theatre/{self.sid}/commit", json={
            "expected_revision": rev, "background_id": self.bg,
            "layers": [{"asset_id": self.sun, "group": "sky"}, {"asset_id": self.wall, "group": "foundations"},
                       {"asset_id": self.hero, "group": "hero"}]}, headers=HEADERS)
        self.assertEqual(r.status_code, 200, r.text)
        self.recut = f"{self.base}/paper-theatre/{self.sid}/recut"

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def upload(self, name, image):
        b = io.BytesIO(); image.save(b, format="PNG")
        r = self.client.post(self.base + "/media", files={"file": (name + ".png", b.getvalue(), "image/png")}, headers=HEADERS)
        self.assertEqual(r.status_code, 200, r.text)
        return r.json()["asset"]["id"]

    def rev(self):
        return self.client.get(self.base).json()["revision"]

    def test_runtime_is_local_and_free(self):
        rt = self.client.get("/api/paper-theatre/recut/runtime").json()
        self.assertTrue(rt["local"])
        self.assertFalse(rt["paid"])
        self.assertIn("mobile_sam.pt", rt["models"])

    def test_state_settings_job_accept_and_revert(self):
        st = self.client.get(self.recut).json()
        self.assertEqual([o["asset_id"] for o in st["objects"]], [self.sun, self.wall, self.hero])
        self.assertEqual(st["objects"][0]["prompt"]["hull"], "circle")
        self.assertEqual(st["objects"][2]["group"], "hero")
        r = self.client.post(self.recut + "/settings", json={"expected_revision": self.rev(), "settings": {
            "prompts": {self.hero: {"box": [118, 58, 172, 172], "pos": [[140, 80], [145, 150]], "neg": []}},
            "depth": {self.wall: 0.5}, "options": {"leftover": "layers"}}}, headers=HEADERS)
        self.assertEqual(r.status_code, 200, r.text)
        st = self.client.get(self.recut).json()
        self.assertFalse(st["objects"][2]["prompt"].get("auto"))
        self.assertEqual(st["objects"][1]["depth"], 0.5)
        old = self.app.state.store.get(self.project["id"]).scenes[-1]
        old_cues = [dict(c) for c in old.parameters["layer_cues"]]
        captured = {}

        def fake_worker(python, worker, job_dir, progress, cancel):
            data = json.loads((job_dir / "input.json").read_text())
            captured.update(data)
            out = Path(data["output_dir"]); out.mkdir(parents=True)
            for layer in data["layers"]:
                shutil.copy(layer["path"], out / f"{layer['key']}.png")
            Image.new("RGB", (320, 180), (191, 167, 134)).save(out / "background.png")
            rgba((320, 180), (0, 0, 319, 30), (230, 220, 200)).save(out / "leftover_01.png")
            Image.new("RGB", (60, 40), "white").save(out / "review.jpg")
            (out / "report.json").write_text(json.dumps({
                "layers": {}, "leftovers": [{"key": "leftover_01", "area": 9600, "bbox": [0, 0, 319, 30]}],
                "warnings": [], "final_mean_abs_diff": 0.0, "final_px_over_20": 0, "unowned_px": 0, "seconds": 1}))

        with tempfile.TemporaryDirectory() as fake_env, patch("studio_api.paper_recut.run_worker", fake_worker):
            python = Path(fake_env) / "python"; python.write_text(""); python.chmod(0o755)
            with patch.dict(os.environ, {"DOCOS_IMAGE_PYTHON": str(python)}):
                job = self.client.post(self.recut + "/run", json={"expected_revision": self.rev()}, headers=HEADERS)
                self.assertEqual(job.status_code, 200, job.text)
                for _ in range(200):
                    state = self.app.state.jobs.get(job.json()["id"])
                    if state["status"] in ("SUCCEEDED", "FAILED"):
                        break
                    time.sleep(.05)
        self.assertEqual(state["status"], "SUCCEEDED", state["message"])
        hero_in = next(x for x in captured["layers"] if x["key"] == self.hero)
        self.assertEqual(hero_in["prompt"]["parts"], [[[140, 80]], [[145, 150]]], "characters: one part per point")
        self.assertEqual(captured["options"]["leftover"], "layers")
        # Nothing changes in the scene before explicit acceptance.
        scene = self.app.state.store.get(self.project["id"]).scenes[-1]
        self.assertEqual(scene.asset_ids, [self.sun, self.wall, self.hero])
        r = self.client.post(self.recut + "/accept", json={"expected_revision": self.rev()}, headers=HEADERS)
        self.assertEqual(r.status_code, 200, r.text)
        scene = next(s for s in r.json()["scenes"] if s["id"] == self.sid)
        self.assertEqual(len(scene["asset_ids"]), 4)
        self.assertNotEqual(scene["asset_id"], self.bg)
        cues = scene["parameters"]["layer_cues"]
        self.assertEqual(cues[:3], old_cues, "existing timing and order stay untouched")
        self.assertEqual(cues[3]["z_index"], -100)
        self.assertEqual(cues[3]["layer"], 4)
        self.assertLess(cues[3]["start"], min(c["start"] for c in old_cues))
        again = self.client.post(self.recut + "/accept", json={"expected_revision": self.rev()}, headers=HEADERS)
        self.assertEqual(again.status_code, 422)
        r = self.client.post(self.recut + "/revert", json={"expected_revision": self.rev()}, headers=HEADERS)
        self.assertEqual(r.status_code, 200, r.text)
        scene = next(s for s in r.json()["scenes"] if s["id"] == self.sid)
        self.assertEqual(scene["asset_ids"], [self.sun, self.wall, self.hero])
        self.assertEqual(scene["asset_id"], self.bg)
        self.assertEqual(scene["parameters"]["layer_cues"], old_cues)

    def test_run_requires_image_environment(self):
        with patch.dict(os.environ, {"DOCOS_IMAGE_PYTHON": "/nonexistent/python"}):
            r = self.client.post(self.recut + "/run", json={"expected_revision": self.rev()}, headers=HEADERS)
        self.assertEqual(r.status_code, 422)
        self.assertIn("install_studio.py --with-models", r.json()["detail"])


@unittest.skipUnless(HAS_CV2, "worker logic runs in the image-model environment (OpenCV)")
class RecutWorkerRulesTests(unittest.TestCase):
    """Synthetic scene, fake models: the production rules hold end to end."""

    def test_paper_start_holes_under_characters_and_exact_final_frame(self):
        sys.path.insert(0, str(REPO / "studio_workers"))
        import cutout_worker as worker
        size = (240, 140)
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            bg = Image.new("RGB", size, (190, 166, 133)); bg.save(d / "bg.png")
            layers = {
                "sun": (rgba(size, (150, 10, 200, 60), (210, 70, 40), "disc"), "sky", [175, 35]),
                "cloud": (rgba(size, (130, 40, 230, 70), (240, 235, 225)), "sky", [200, 60]),
                "wall": (rgba(size, (20, 70, 220, 120), (150, 140, 120)), "foundations", [40, 95]),
                "hero": (rgba(size, (90, 50, 130, 135), (25, 25, 25)), "hero", [110, 100]),
            }
            entries, alphas = [], {}
            for i, (key, (im, group, pt)) in enumerate(layers.items()):
                im.save(d / f"{key}.png")
                a = np.array(im)[..., 3] > 0
                ys, xs = np.nonzero(a)
                box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
                alphas[tuple(box)] = a
                entries.append({"key": key, "name": key, "group": group, "order": i, "depth": float(i),
                                "path": str(d / f"{key}.png"),
                                "prompt": {"box": box, "pos": [pt], "neg": [],
                                           "hull": "circle" if key == "sun" else "auto"}})
            (d / "job").mkdir()
            (d / "job" / "input.json").write_text(json.dumps({
                "width": size[0], "height": size[1], "background": str(d / "bg.png"), "layers": entries,
                "extra_objects": [], "models_dir": str(d / "models"), "output_dir": str(d / "job" / "out"),
                "options": {"leftover": "layers", "fix_seams": False, "complete_scenery": True}}))

            class FakeSeg:
                def __init__(self, *_): pass
                def __call__(self, img, box, pos=(), neg=(), **_):
                    return alphas[tuple(box)].astype(np.float32)

            class FakeLama:
                def __init__(self, *_): pass
                def crop(self, img, mask, margin=48):
                    out = img.copy(); out[mask] = (255, 0, 255); return out
                __call__ = crop

            with patch.object(worker, "ensure_model", lambda folder, key: folder / key), \
                    patch.object(worker, "progress", lambda *_: None), \
                    patch.object(worker, "Segmenter", FakeSeg), patch.object(worker, "Lama", FakeLama):
                worker.run(d / "job")
            out = d / "job" / "out"
            report = json.loads((out / "report.json").read_text())
            self.assertEqual(report["final_px_over_20"], 0, "final frame equals the source")
            backdrop = np.array(Image.open(out / "background.png").convert("RGB")).astype(int)
            self.assertLess(np.abs(backdrop - [190, 166, 133]).mean(), 12, "backdrop is plain paper")
            wall = np.array(Image.open(out / "wall.png"))
            hero_px = np.array(layers["hero"][0])[..., 3] > 0
            inner = hero_px.copy(); inner[:, :93] = False; inner[:, 128:] = False
            self.assertTrue((wall[..., 3][inner & (np.array(layers["wall"][0])[..., 3] > 0)] == 0).all(),
                            "no invented wall under the character: an empty hole")
            sun = np.array(Image.open(out / "sun.png"))
            self.assertEqual(sun[50, 175, 3], 255, "sun disc completed behind the later cloud")
            self.assertTrue(report["leftovers"] == [] or all(x["area"] > 0 for x in report["leftovers"]))
            self.assertTrue((out / "review.jpg").is_file())


if __name__ == "__main__":
    unittest.main()
