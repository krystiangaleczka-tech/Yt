"""Fast tests of the logic that needs no network, video or speech model."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gtaclip.ai import extract_json  # noqa: E402
from gtaclip.captions import build_ass, censor  # noqa: E402
from gtaclip.chat import SpikeDetector, counts  # noqa: E402
from gtaclip.config import Workspace  # noqa: E402
from gtaclip.pick import normalize  # noqa: E402
from gtaclip.reframe import cam_box, game_crop  # noqa: E402
from gtaclip.render import keep_segments, mapper  # noqa: E402
from gtaclip.versions import simple_parse  # noqa: E402


def _ts(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


class Captions(unittest.TestCase):
    def test_no_overlap_between_phrases(self):
        w = [{"w": t, "s": s, "e": e} for t, s, e in
             [("of", 0, .5), ("look", .4, .8), ("at", .8, 1), ("how", 1, 1.3), ("much", 1.3, 1.6), ("nd", 1.62, 2)]]
        ev = [ln for ln in build_ass(w, 3, "classic").splitlines() if ln.startswith("Dialogue: 0")]
        iv = [(_ts(ln.split(",")[1]), _ts(ln.split(",")[2])) for ln in ev]
        for a, b in zip(iv, iv[1:]):
            self.assertLessEqual(a[1], b[0] + 1e-6)

    def test_hook_and_keyword_colour(self):
        ass = build_ass([{"w": "secret", "s": 0, "e": .5}], 2, "classic", "SPEED FOUND KFC", ["secret"],
                        keyword_color="#2BE36B")
        self.assertIn("SPEED FOUND KFC", ass)
        self.assertIn("&H006BE32B", ass)

    def test_censor_on_screen(self):
        self.assertEqual(censor("faggot"), "f*****")
        self.assertEqual(censor("crazy"), "crazy")


class Chat(unittest.TestCase):
    def test_filters(self):
        self.assertFalse(counts("Nightbot", "hi"))
        self.assertFalse(counts("x", "!points"))
        self.assertFalse(counts("x", "go to https://a.b"))
        self.assertTrue(counts("x", "KEKW"))

    def test_spike_after_explosion_only(self):
        d = SpikeDetector(ratio=3, min_per_min=30)
        t0, spikes = 1_000_000.0, []
        for sec in range(420):
            n = 3 if sec < 400 else 25
            for k in range(n):
                d.add(t0 + sec + k / (n + 1), f"u{(sec * 7 + k) % (40 if sec < 400 else 400)}", "hey")
            if d.check(t0 + sec + .99):
                spikes.append(sec)
        self.assertEqual(len(spikes), 1)
        self.assertGreaterEqual(spikes[0], 400)


class Cutting(unittest.TestCase):
    def test_keep_segments_and_map(self):
        keep = keep_segments(20, [(5, 8), (0.2, 0.9), (19.5, 20)])
        self.assertEqual(keep, [(0.0, 5.25), (7.75, 20)])
        f = mapper(keep)
        self.assertAlmostEqual(f(10), 5.25 + 2.25)
        self.assertIsNone(f(6))


class Layout(unittest.TestCase):
    def test_cam_box_snaps_to_corner(self):
        x, y, w, h = cam_box([60, 40, 100, 100], 1920, 1080)
        self.assertEqual((x, y), (0, 0))

    def test_game_crop_avoids_left_cam(self):
        gw, gh, gx, gy = game_crop(1920, 1080, 1080, 1280, cam=[0, 0, 400, 300])
        self.assertGreaterEqual(gx, 400)
        self.assertLessEqual(gx + gw, 1920)


class Words(unittest.TestCase):
    def test_simple_requests(self):
        spec = {"start": 100.0, "end": 130.0}
        self.assertEqual(simple_parse("zakończ 2 sekundy wcześniej", spec), {"end": 128.0})
        self.assertEqual(simple_parse("end it 2 seconds earlier", spec), {"end": 128.0})
        self.assertEqual(simple_parse("zacznij 3 s wcześniej", spec), {"start": 97.0})
        self.assertEqual(simple_parse("styl beast", spec), {"look": {"style": "beast"}})

    def test_extract_json_from_chatty_answer(self):
        self.assertEqual(extract_json('Sure!\n```json\n[{"a": 1}]\n```'), [{"a": 1}])
        self.assertEqual(extract_json('ok {"keep": true} bye'), {"keep": True})


class Picks(unittest.TestCase):
    def test_normalize_limits_and_hook(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Workspace(d).ensure()
            ws.write_json("src/s1.meta.json", {"url": "u", "name": "xQc", "title": "t"})
            cands = [{"cid": i, "sid": "s1", "start": i * 100.0, "end": i * 100 + 30.0, "peak": i * 100 + 20.0,
                      "tags": [], "transcript": ""} for i in range(1, 5)]
            raw = [{"cid": i, "hook": "xqc finds a very secret place in gta six", "score": 90} for i in range(1, 5)]
            picks = normalize(ws, raw, cands, 10)
            self.assertEqual(len(picks), 2)  # max 2 per source by default
            self.assertEqual(picks[0]["hook"], "XQC FINDS A VERY SECRET PLACE")


class CaptionsInCode(unittest.TestCase):
    """The Pillow fallback (ffmpeg without libass) covers the whole Short with exact durations."""

    def test_layer_timeline(self):
        from gtaclip.capdraw import build_layer
        from gtaclip.captions import caption_events

        w = [{"w": t, "s": s, "e": e} for t, s, e in [("yo", 0.5, 0.9), ("the", 1.0, 1.2), ("cops", 1.2, 1.8)]]
        with tempfile.TemporaryDirectory() as d:
            ev = caption_events(w, 4.0, "classic", "SPEED FOUND KFC", ["cops"], watermark="@me")
            tracks = build_layer(ev, 4.0, "classic", "#FFD400", Path(d) / "fonts", Path(d) / "caps")
            self.assertEqual(len(tracks), 3)  # captions, hook, watermark
            for tr in tracks:
                lines = tr["list"].read_text().splitlines()
                total = sum(float(x.split()[1]) for x in lines if x.startswith("duration"))
                self.assertAlmostEqual(total, 4.0, places=2)
                self.assertTrue(lines[-1].startswith("file "))  # last image repeated for the concat demuxer
                self.assertLess(tr["h"], 400)  # a strip, not the whole 1920 px frame


class Music(unittest.TestCase):
    """Warning rule for music under the stream (scores come from YAMNet, one per ~0.49 s)."""

    def test_rule(self):
        import numpy as np
        from gtaclip.music import summarize

        self.assertFalse(summarize(np.zeros(60))["warn"])                       # talking only
        self.assertFalse(summarize(np.r_[np.zeros(56), [0.15] * 4])["warn"])    # ~2 s of a faint hint
        self.assertTrue(summarize(np.r_[np.zeros(55), [0.5] * 5])["warn"])      # ~2.4 s of clear music
        self.assertTrue(summarize(np.r_[np.zeros(50), [0.12] * 10])["warn"])    # ~4.9 s of quieter music
        self.assertEqual(summarize(np.zeros(0))["seconds"], 0.0)


if __name__ == "__main__":
    unittest.main()
