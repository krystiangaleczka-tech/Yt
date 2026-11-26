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


class Sources(unittest.TestCase):
    """Which parts of a stream are GTA, ongoing streams, already processed parts."""

    S = {"game_regex": r"grand theft auto|\\bgta\\b", "title_regex": r"GTA ?(6|VI)"}

    def test_twitch_chapters_without_gta_are_skipped(self):
        from gtaclip.sources import topic_plan
        # real chapters of an xQc VOD (title "🐝LIVE🐝DRAMA🐝...")
        info = {"webpage_url": "https://www.twitch.tv/videos/2939685398", "duration": 38796, "title": "🐝LIVE🐝DRAMA🐝",
                "chapters": [{"title": "Just Chatting", "start_time": 0, "end_time": 11222},
                             {"title": "ROB RUN", "start_time": 11222, "end_time": 24482},
                             {"title": "Mario Kart World", "start_time": 29901, "end_time": 31187}]}
        self.assertEqual(topic_plan(info, self.S)["verdict"], "no")

    def test_twitch_gta_chapters_become_windows(self):
        from gtaclip.sources import topic_plan
        info = {"webpage_url": "https://www.twitch.tv/videos/1", "duration": 30000, "title": "🐝LIVE🐝",
                "chapters": [{"title": "Just Chatting", "start_time": 0, "end_time": 3000},
                             {"title": "Grand Theft Auto VI", "start_time": 3000, "end_time": 9000},
                             {"title": "Just Chatting", "start_time": 9000, "end_time": 9300},   # 5 min break
                             {"title": "Grand Theft Auto VI", "start_time": 9300, "end_time": 12000},
                             {"title": "Fortnite", "start_time": 12000, "end_time": 20000},
                             {"title": "Grand Theft Auto VI", "start_time": 20000, "end_time": 20000}]}  # still running
        p = topic_plan(info, self.S)
        self.assertEqual(p["verdict"], "yes")
        self.assertEqual(p["windows"], [(3000.0, 12000.0), (20000.0, 30000.0)])

    def test_youtube_title_and_unknown(self):
        from gtaclip.sources import topic_plan
        yt = {"webpage_url": "https://www.youtube.com/watch?v=x", "duration": 7200, "categories": ["Gaming"]}
        self.assertEqual(topic_plan({**yt, "title": "GTA 6 day 3 LIVE"}, self.S)["verdict"], "yes")
        self.assertEqual(topic_plan({**yt, "title": "stream", "tags": ["gta vi"]}, self.S)["verdict"], "yes")
        self.assertEqual(topic_plan({**yt, "title": "chill stream"}, self.S)["verdict"], "unknown")

    def test_plan_windows(self):
        from gtaclip.sources import plan_windows
        h = 3600
        self.assertEqual(plan_windows(None, 10 * h, 6 * h), [(0, 6 * h), (6 * h, 10 * h)])
        self.assertEqual(plan_windows([(h, 3 * h)], 10 * h, 6 * h, done_until=2 * h), [(2 * h, 3 * h)])
        # live: stop a minute before 'now'; a tail shorter than 5 min waits for the next run
        self.assertEqual(plan_windows(None, 2 * h, 6 * h, live=True), [(0, 2 * h - 60)])
        self.assertEqual(plan_windows(None, 2 * h, 6 * h, done_until=2 * h - 200, live=True), [])


class TwitchChat(unittest.TestCase):
    """VOD chat paging (Twitch answers are faked — no network)."""

    @staticmethod
    def page(offsets, more, start_id=0):
        return [{"data": {"video": {"comments": {
            "edges": [{"cursor": f"c{start_id + i}", "node": {"id": f"m{start_id + i}", "contentOffsetSeconds": o,
                                                              "commenter": {"displayName": "u"},
                                                              "message": {"fragments": [{"text": "KEKW"}]}}}
                      for i, o in enumerate(offsets)],
            "pageInfo": {"hasNextPage": more}}}}}]

    def test_cursor_paging(self):
        from gtaclip.chat import fetch_twitch_vod_chat
        pages = iter([self.page([100, 101], True, 0), self.page([102, 150], True, 2), self.page([201, 260], False, 4)])
        with tempfile.TemporaryDirectory() as d:
            n = fetch_twitch_vod_chat("v123", 100, 200, Path(d) / "c.json", post=lambda b: next(pages), sleep=0)
            self.assertEqual(n, 4)  # 201 and 260 are outside the window

    def test_offset_fallback_when_cursor_refused(self):
        from gtaclip.chat import fetch_twitch_vod_chat
        calls = []

        def post(body):
            v = body[0]["variables"]
            calls.append(v)
            if "cursor" in v:
                return [{"errors": [{"message": "failed integrity check"}]}]
            t = v["contentOffsetSeconds"]
            return self.page([t, t + 2], True, t * 10) if t < 110 else self.page([], False)

        with tempfile.TemporaryDirectory() as d:
            n = fetch_twitch_vod_chat("123", 100, 112, Path(d) / "c.json", post=post, sleep=0)
            self.assertGreater(n, 5)
            self.assertTrue(any("cursor" in c for c in calls))

    def test_unavailable_chat_does_not_crash(self):
        from gtaclip.chat import fetch_twitch_vod_chat
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(fetch_twitch_vod_chat("1", 0, 10, Path(d) / "c.json",
                                                   post=lambda b: [{"data": {"video": None}}], sleep=0), 0)


class EditTimelineTest(unittest.TestCase):
    """Change by words: seconds of the Short <-> source seconds, cuts, speed, zooms, texts."""

    def setUp(self):
        from gtaclip.render import timeline
        # Short = source 100-110 at normal speed, then 120-130 twice as fast -> 15 s long
        self.tl = timeline([(100.0, 110.0, 1.0), (120.0, 130.0, 2.0)])
        self.spec = {"src_t0": 90.0, "start": 100.0, "end": 130.0, "hook": "H", "look": {}}

    def test_timeline_maps_both_ways(self):
        from gtaclip.render import out_to_src, src_to_out
        self.assertEqual(self.tl[-1][1], 15.0)
        self.assertEqual(out_to_src(self.tl, 4.0), 104.0)
        self.assertEqual(out_to_src(self.tl, 12.0), 124.0)
        self.assertEqual(src_to_out(self.tl, 126.0), 13.0)
        self.assertIsNone(src_to_out(self.tl, 115.0))  # cut out

    def test_plan_pieces_cuts_dead_air_inside_each_segment(self):
        from gtaclip.render import plan_pieces
        spec = {**self.spec, "segments": [{"a": 100, "b": 120, "speed": 1}, {"a": 95, "b": 99, "speed": 2}]}
        pieces = plan_pieces(Path("x"), spec, 60, True, True, silence_fn=lambda src, a, b: [(5.0, 8.0)])
        self.assertEqual(pieces[0], (100.0, 105.25, 1.0))
        self.assertEqual(pieces[1], (107.75, 120.0, 1.0))
        self.assertEqual(pieces[-1][2], 2.0)

    def test_speed_up_and_cut_from_short_seconds(self):
        from gtaclip.versions import to_spec_patch
        patch, note = to_spec_patch({"segments": [[0, 4, 1], [4, 8, 2], [12, 15, 1]]}, self.spec, self.tl, 60)
        segs = [(x["a"], x["b"], x["speed"]) for x in patch["segments"]]
        self.assertEqual(segs, [(100.0, 104.0, 1.0), (104.0, 108.0, 2.0), (124.0, 130.0, 2.0)])
        self.assertEqual((patch["start"], patch["end"]), (100.0, 130.0))
        self.assertEqual(note, "")

    def test_zoom_mute_text_and_unsupported(self):
        from gtaclip.versions import to_spec_patch
        edit = {"zooms": [{"at": 10.5, "scale": 1.5}], "mute": [[2, 12]], "noise": 0.4,
                "texts": [{"text": "a bottle of water", "at": 1, "color": "#1E90FF", "size": 150}],
                "look": {"cap_pos": "top", "bogus": 1}, "unsupported": "głos lektora — przycisk Twój głos"}
        patch, note = to_spec_patch(edit, self.spec, self.tl, 60)
        self.assertEqual(patch["zoom_at"][0]["t"], 121.0)
        self.assertEqual(patch["mute"], [[102.0, 110.0], [120.0, 124.0]])
        self.assertEqual(patch["texts"][0]["t"], 101.0)
        self.assertEqual(patch["look"], {"cap_pos": "top"})
        self.assertEqual(patch["noise"], 0.4)
        self.assertIn("Twój głos", note)

    def test_extend_and_bad_answers(self):
        from gtaclip.util import ToolError
        from gtaclip.versions import to_spec_patch
        patch, _ = to_spec_patch({"extend": {"before": 3, "after": 50}}, self.spec, self.tl, 60)
        self.assertEqual((patch["start"], patch["end"]), (97.0, 150.0))  # end clamped to the downloaded file
        with self.assertRaises(ToolError):
            to_spec_patch(["fighting", "back seat"], self.spec, self.tl, 60)

    def test_music_ranges_merge(self):
        import numpy as np
        from gtaclip.music import ranges
        r = ranges(np.array([0, 0, 0.5, 0.3, 0, 0, 0, 0.25, 0]))
        self.assertEqual(len(r), 2)
        self.assertAlmostEqual(r[0][0], 0.825, delta=0.01)

    def test_extract_json_prefers_outer_object(self):
        self.assertEqual(extract_json('{"segments": [[0, 4, 1]]}'), {"segments": [[0, 4, 1]]})
        self.assertEqual(extract_json('[{"a": {"b": 1}}]'), [{"a": {"b": 1}}])

    def test_extra_text_is_drawn(self):
        from gtaclip.capdraw import build_layer
        from gtaclip.captions import caption_events
        with tempfile.TemporaryDirectory() as d:
            ev = caption_events([], 4.0, "classic", "HOOK", [],
                                texts=[{"text": "A BOTTLE OF WATER", "start": 1.0, "end": 3.0, "y": 420,
                                        "color": "#1E90FF", "size": 150}])
            self.assertEqual([e["kind"] for e in ev], ["hook", "text"])
            tracks = build_layer(ev, 4.0, "classic", "#FFD400", Path(d) / "fonts", Path(d) / "caps")
            self.assertEqual(len(tracks), 2)
            self.assertIn("Txt", build_ass([], 4.0, "classic", "", [], texts=[{"text": "X", "start": 1, "end": 2,
                                                                                  "y": 420, "color": "#1E90FF", "size": 120}]))


if __name__ == "__main__":
    unittest.main()
