"""Real Remotion -> immutable asset -> timeline -> FFmpeg export smoke test.

Opt in with DOCOS_TEST_REMOTION=1 after `npm ... run remotion:setup`.
Runs in CI; kept separate from the fast tests so ordinary Python-only checks
never download Chromium or require npm dependencies.
"""
import os
import tempfile
import threading
import unittest
from pathlib import Path

from PIL import Image

from studio_core.inserts import MotionInsert
from studio_core.media import import_media, probe
from studio_core.models import Project, Clip, Sequence
from studio_core.store import ProjectStore
from studio_timeline.render import render
from studio_workers.motion import run_motion


@unittest.skipUnless(os.environ.get("DOCOS_TEST_REMOTION") == "1", "Opt-in real Remotion renderer test")
class RealMotionRenderTests(unittest.TestCase):
    def test_five_templates_and_final_timeline_export(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = ProjectStore(root)
            project = store.create(Project(sequence=Sequence(width=640, height=360)))
            image_ids = []
            for color in ("#df7044", "#497db5"):
                path = root / (color[1:] + ".png")
                Image.new("RGB", (640, 360), color).save(path)
                asset, _ = import_media(store, project.id, path, path.name)
                image_ids.append(asset.id)
            for n, template in enumerate(("photo", "compare", "chart", "quote", "chapter")):
                with self.subTest(template=template):
                    item = MotionInsert(template=template, title="Próba animacji", text="Sprawdzony cytat do próby technicznej.",
                                        subtitle="Źródła i narracja", source="Materiały testowe", duration=24,
                                        image_ids=image_ids if template == "compare" else image_ids[:1] if template == "photo" else [])
                    p = store.get(project.id)
                    p = store.mutate(p.id, p.revision, lambda p: p.inserts.append(item))
                    result = run_motion(store, p, item.id, f"job_real_{n}", lambda *args: None, threading.Event())
                    self.assertTrue(result["attached"])
                    current = store.get(p.id)
                    rendered = current.inserts[-1]
                    self.assertEqual(rendered.rendered_asset_id, result["asset_id"])
                    def add(p):
                        p.sequence.clips.append(Clip(track_id="v1", asset_id=result["asset_id"], title=template, start=n*24, duration=24))
                    store.mutate(p.id, current.revision, add)
            final = root / "final.mp4"
            render(store, store.get(project.id), final, lambda *args: None, threading.Event(), preview=False)
            info = probe(final)
            self.assertAlmostEqual(float(info["format"]["duration"]), 4, delta=.1)
            self.assertGreater(final.stat().st_size, 5000)
