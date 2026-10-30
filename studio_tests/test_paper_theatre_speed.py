"""The fast Paper Theatre compositor must keep the reference renderer's pixels.

composite_rig() replaces image.alpha_composite(rig_image(...)) inside paint().
rig_image() stays the reference. The only accepted difference: once a hanging
cutout has practically stopped swinging (|angle| < 0.001°), bicubic sampling
lands exactly on pixel centres and the last floating-point bit decides the
rounding, so a few pixels may differ by at most 2/255.
"""
import math
import random
import unittest
from types import SimpleNamespace

import numpy as np
from PIL import Image, ImageDraw

import studio_timeline.templates as templates
from studio_timeline.paper_theatre import composite_rig, rig_image, rig_motion


def blob_layer(rng, size, near_edge=False):
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    w, h = size
    x = rng.randint(-60, 60) if near_edge else rng.randint(w // 5, 4 * w // 5)
    y = rng.randint(-40, h // 3) if near_edge else rng.randint(h // 5, 4 * h // 5)
    for _ in range(4):
        rx, ry = rng.randint(8, w // 6), rng.randint(8, h // 4)
        ox, oy = rng.randint(-20, 20), rng.randint(-20, 20)
        draw.ellipse((x + ox - rx, y + oy - ry, x + ox + rx, y + oy + ry),
                     fill=(rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255),
                           rng.choice((255, 255, 200, 120))))
    return image


def diff(a, b):
    return np.abs(np.asarray(a, dtype=int) - np.asarray(b, dtype=int)).max(axis=2)


def reference(image, source, rig, cue, elapsed, duration, offset=(0, 0), memo=None, size=None):
    layer = source() if callable(source) else source
    image.alpha_composite(rig_image(layer, rig, cue, elapsed, duration), offset)


class FastCompositorParity(unittest.TestCase):
    RIGS = (
        ("static", {}),
        ("static", {"outline_px": 16, "outline_color": "#362820"}),
        ("bottom_rise", {"overshoot": .018}),
        ("bottom_rise", {"outline_px": 6}),
        ("hanging_drop", {"string_visible": True, "swing_deg": 3.2, "swing_decay": 1.1,
                          "overshoot": .025, "settle_duration": .22}),
        ("hanging_drop", {"string_visible": True, "string_length": .2, "swing_deg": 0}),
        ("rake_lift", {"stick_visible": True, "stick_length": .1, "start_rotation": 82,
                       "overshoot_rotation": -5, "settle_duration": .22}),
        ("rake_lift", {"stick_visible": False, "outline_px": 12, "start_rotation": 88,
                       "pivot_x": .3, "pivot_y": .9}),
    )

    def test_every_rig_matches_reference_bit_for_bit(self):
        rng = random.Random(20261030)
        for rig, cue in self.RIGS:
            for trial in range(18):
                size = rng.choice(((320, 180), (640, 360), (480, 270)))
                source = blob_layer(rng, size, near_edge=trial % 3 == 0)
                elapsed = rng.uniform(-.2, 2.2)
                duration = rng.uniform(.3, .9)
                if rig == "hanging_drop" and cue["swing_deg"]:
                    angle = cue["swing_deg"] * math.sin(elapsed * 8) * math.exp(-cue["swing_decay"] * elapsed)
                    if 0 < abs(angle) < 1e-3:
                        continue  # covered by the tolerance test below
                offset = (rng.randint(-25, 25), 0)
                backdrop = Image.new("RGBA", size, (190, 166, 133, 255))
                expected, actual = backdrop.copy(), backdrop.copy()
                reference(expected, source, rig, cue, elapsed, duration, offset)
                composite_rig(actual, source, rig, cue, elapsed, duration, offset)
                with self.subTest(rig=rig, cue=cue, trial=trial, elapsed=elapsed):
                    self.assertEqual(int(diff(expected, actual).max()), 0)

    def test_settled_swing_differs_by_rounding_noise_only(self):
        rng = random.Random(7)
        cue = {"string_visible": True, "swing_deg": 3.2, "swing_decay": 1.1,
               "overshoot": .025, "settle_duration": .22}
        source = blob_layer(rng, (1280, 720))
        backdrop = Image.new("RGBA", source.size, (190, 166, 133, 255))
        for elapsed in (12.0, 20.25, 28.5):
            expected, actual = backdrop.copy(), backdrop.copy()
            reference(expected, source, "hanging_drop", cue, elapsed, .6)
            composite_rig(actual, source, "hanging_drop", cue, elapsed, .6)
            delta = diff(expected, actual)
            self.assertLessEqual(int(delta.max()), 2)
            self.assertLess((delta > 0).sum(), source.width * source.height * .0005)

    def test_memo_reuse_is_identical_to_fresh_work(self):
        rng = random.Random(3)
        source = blob_layer(rng, (480, 270))
        cue = {"stick_visible": True, "outline_px": 8}
        memo = {}
        for frame in range(0, 60, 3):
            elapsed = frame / 30
            backdrop = Image.new("RGBA", source.size, (190, 166, 133, 255))
            fresh, cached = backdrop.copy(), backdrop.copy()
            composite_rig(fresh, source, "rake_lift", cue, elapsed, .7)
            composite_rig(cached, lambda: source, "rake_lift", cue, elapsed, .7, memo=memo)
            self.assertEqual(int(diff(fresh, cached).max()), 0)

    def test_rig_motion_rounds_like_python(self):
        motion = rig_motion("hanging_drop", {"string_visible": True}, .25, .6, (10, 20, 50, 61), 1280, 720)
        self.assertIsInstance(motion["dy_px"], int)
        self.assertEqual(motion["dy_px"], round(motion["dy"]))
        with self.assertRaises(ValueError):
            rig_motion("teleport", {}, .1, .5, (0, 0, 1, 1), 10, 10)


class PaintParity(unittest.TestCase):
    def scene(self):
        rng = random.Random(42)
        w, h = 480, 270
        layers, cues = [], []
        groups = [("sky", "hanging_drop"), ("sky", "hanging_drop"), ("landscape", "hanging_drop"),
                  ("foundations", "bottom_rise"), ("props", "static"),
                  ("characters", "rake_lift"), ("hero", "rake_lift")]
        for index, (group, rig) in enumerate(groups, start=1):
            source = Image.new("RGBA", (rng.randint(120, 300), rng.randint(120, 320)))
            draw = ImageDraw.Draw(source)
            draw.ellipse((4, 4, source.width - 4, source.height - 4),
                         fill=(rng.randint(40, 220), rng.randint(40, 220), 120, 255))
            layers.append(source)
            cue = {"layer": index, "group": group, "rig": rig, "start": .2 + index * .25,
                   "duration": .6, "settle_duration": .22, "depth": 1 + index * .3,
                   "layout_x": rng.uniform(.15, .85), "layout_y": rng.uniform(.4, .95),
                   "layout_width": rng.uniform(.1, .3), "z_index": rng.randint(0, 70)}
            if rig == "hanging_drop":
                cue.update(string_visible=True, swing_deg=3.2, swing_decay=1.1, overshoot=.025)
            if rig == "rake_lift":
                cue.update(pivot_x=.5, pivot_y=1, stick_visible=True, stick_length=.1,
                           outline_px=12 if group == "hero" else 8, outline_color="#362820")
            cues.append(cue)
        background = Image.new("RGBA", (w, h), (190, 166, 133, 255))
        media = SimpleNamespace(images=[background] + layers, streams=[None] * (len(layers) + 1))
        media.frame = lambda i, n: media.images[i] if i < len(media.images) else None
        clip = SimpleNamespace(template="paper-theatre", parameters={}, duration=150, speed=1)
        params = {"depth": .015, "layer_cues": cues, "caption": ""}
        return clip, params, media, w, h

    def test_paint_frames_match_reference_compositor(self):
        clip, params, media, w, h = self.scene()
        fast = [np.asarray(templates.paint(clip, params, media, n, w, h, 30)) for n in range(0, 150, 7)]
        original = templates.composite_rig
        templates.composite_rig = reference
        try:
            slow = [np.asarray(templates.paint(clip, params, media, n, w, h, 30)) for n in range(0, 150, 7)]
        finally:
            templates.composite_rig = original
        for n, (a, b) in zip(range(0, 150, 7), zip(slow, fast)):
            delta = np.abs(a.astype(int) - b.astype(int)).max(axis=2)
            with self.subTest(frame=n):
                # Up to 5 s: every swing is still above 0.001°, so bit-exact.
                self.assertEqual(int(delta.max()), 0)

    def test_render_cache_key_follows_paper_rigs(self):
        import hashlib
        only_templates = hashlib.sha256(templates.Path(templates.__file__).read_bytes()).hexdigest()
        self.assertNotEqual(templates.renderer_hash(), only_templates)


if __name__ == "__main__":
    unittest.main()
