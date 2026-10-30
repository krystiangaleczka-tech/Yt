"""The browser preview and the MP4 renderer share one set of motion vectors."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SharedMotionFixture(unittest.TestCase):
    def test_fixture_matches_python_renderer(self):
        spec = importlib.util.spec_from_file_location(
            "paper_theatre_motion_fixture", ROOT / "scripts/paper_theatre_motion_fixture.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # A rig change in studio_timeline/paper_theatre.py must be mirrored in
        # apps/studio/src/paperTheatreMotion.ts and the fixture regenerated.
        self.assertEqual(module.main.__module__, "paper_theatre_motion_fixture")
        import sys
        argv = sys.argv
        sys.argv = ["fixture", "--check"]
        try:
            self.assertEqual(module.main(), 0, "Uruchom: python3 scripts/paper_theatre_motion_fixture.py")
        finally:
            sys.argv = argv


if __name__ == "__main__":
    unittest.main()
