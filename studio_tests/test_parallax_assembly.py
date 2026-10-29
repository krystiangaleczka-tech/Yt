"""Regressions for staged paper-cut 2.5D assembly and legacy parallax rendering."""
import unittest

from PIL import Image, ImageDraw

from studio_core.models import Clip
from studio_core.templates import validate_parameters
from studio_timeline.templates import paint


class Frames:
    def __init__(self):
        background = Image.new("RGBA", (100, 60), "#e8e1d4")
        cloud = Image.new("RGBA", (100, 60), (0, 0, 0, 0))
        mountain = Image.new("RGBA", (100, 60), (0, 0, 0, 0))
        figure = Image.new("RGBA", (100, 60), (0, 0, 0, 0))
        ImageDraw.Draw(cloud).rectangle((5, 5, 25, 18), fill="#729adb")
        ImageDraw.Draw(mountain).rectangle((40, 35, 65, 55), fill="#a27f6b")
        ImageDraw.Draw(figure).rectangle((75, 12, 92, 32), fill="#40583c")
        self.images = [background, cloud, mountain, figure]

    def frame(self, index, frame):
        return self.images[index]


class ParallaxAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.media = Frames()
        self.clip = Clip(track_id="v1", template="parallax", duration=50)
        self.background = (232, 225, 212)

    def frame(self, seconds, **options):
        params = validate_parameters("parallax", {"depth": 0, **options})
        return paint(self.clip, params, self.media, round(seconds * 10), 100, 60, 10)

    def colors(self, frame):
        return (frame.getpixel((15, 10)), frame.getpixel((50, 45)), frame.getpixel((80, 20)))

    def test_old_parallax_still_shows_every_layer_immediately(self):
        self.assertEqual(self.colors(self.frame(0)), ((114, 154, 219), (162, 127, 107), (64, 88, 60)))

    def test_layers_arrive_one_by_one_in_selected_order(self):
        settings = dict(assembly_start=.1, assembly_interval=.9, assembly_duration=.2, assembly_drop=.08)
        self.assertEqual(self.colors(self.frame(0, **settings)), (self.background,) * 3)
        self.assertEqual(self.colors(self.frame(.6, **settings)),
                         ((114, 154, 219), self.background, self.background))
        self.assertEqual(self.colors(self.frame(1.5, **settings)),
                         ((114, 154, 219), (162, 127, 107), self.background))
        self.assertEqual(self.colors(self.frame(2.6, **settings)),
                         ((114, 154, 219), (162, 127, 107), (64, 88, 60)))

    def test_individual_layer_cue_overrides_default_schedule(self):
        opts = dict(assembly_start=.1, assembly_interval=.9, assembly_duration=.2,
                    layer_cues=[{"layer": 3, "start": .2, "duration": .2}])
        self.assertEqual(self.colors(self.frame(.6, **opts)),
                         ((114, 154, 219), self.background, (64, 88, 60)))

    def test_invalid_cues_are_rejected_before_render(self):
        bad = [
            [{"layer": 1, "start": -1}],
            [{"layer": 1}, {"layer": 1}],
            [{"layer": True}],
            [{"layer": 1, "start": float("nan")}],
            [{"layer": 1, "drop": 2}],
            [{"layer": 1, "script": "oops"}],
        ]
        for cues in bad:
            with self.subTest(cues=cues), self.assertRaises(ValueError):
                validate_parameters("parallax", {"layer_cues": cues})

    def test_hanging_cloud_enters_from_above_with_a_fine_string(self):
        cue = {"layer": 1, "rig": "hanging_drop", "start": .1, "duration": .3,
               "settle_duration": .1, "overshoot": 0, "swing_deg": 0,
               "string_visible": True, "string_length": .3}
        opts = {"layer_cues": [cue]}
        self.assertEqual(self.frame(0, **opts).getpixel((15, 10)), self.background)
        # The sprite begins outside the canvas, not faded over its destination.
        self.assertEqual(self.frame(.1, **opts).getpixel((15, 10)), self.background)
        landed = self.frame(.6, **opts)
        self.assertEqual(landed.getpixel((15, 10)), (114, 154, 219))
        self.assertNotEqual(landed.getpixel((16, 1)), self.background)  # midpoint of inclusive rectangle rounds to x=16

    def test_rake_lift_unfolds_from_cutout_lower_pivot(self):
        cue = {"layer": 3, "rig": "rake_lift", "start": .1,
               "duration": .3, "start_rotation": 88, "overshoot_rotation": -5,
               "settle_duration": .1, "pivot_y": 1, "pivot_x": .5,
               "stick_visible": True, "stick_length": .15}
        opts = {"layer_cues": [cue]}
        self.assertEqual(self.frame(0, **opts).getpixel((80, 20)), self.background)
        flat = self.frame(.1, **opts)
        self.assertEqual(flat.getpixel((80, 20)), self.background)
        upright = self.frame(.6, **opts)
        self.assertEqual(upright.getpixel((80, 20)), (64, 88, 60))

    def test_bottom_rise_starts_below_and_lands(self):
        opts = {"layer_cues": [{"layer": 2, "rig": "bottom_rise",
                                "start": .1, "duration": .3, "overshoot": .02,
                                "settle_duration": .1}]}
        self.assertEqual(self.frame(.1, **opts).getpixel((50, 45)), self.background)
        self.assertEqual(self.frame(.6, **opts).getpixel((50, 45)), (162, 127, 107))

    def test_mechanical_rig_does_not_fade_unrelated_static_layer(self):
        opts = {"layer_cues": [{"layer": 1, "rig": "hanging_drop",
                                "start": .5, "duration": .3}]}
        self.assertEqual(self.frame(0, **opts).getpixel((80, 20)), (64, 88, 60))
        self.assertEqual(self.frame(0, **opts).getpixel((15, 10)), self.background)

    def test_static_cutout_becomes_visible_on_cue(self):
        opts = {"layer_cues": [{"layer": 2, "rig": "static", "start": .5}]}
        self.assertEqual(self.frame(.3, **opts).getpixel((50, 45)), self.background)
        self.assertEqual(self.frame(.5, **opts).getpixel((50, 45)), (162, 127, 107))

    def test_trimmed_segment_keeps_original_rig_time(self):
        opts = {"layer_cues": [{"layer": 1, "rig": "hanging_drop",
                                "start": .5, "duration": .3, "overshoot": 0,
                                "swing_deg": 0}]}
        self.clip.parameters = {"_frame_offset": 12, "_original_duration": 50}
        self.assertEqual(self.frame(0, **opts).getpixel((15, 10)), (114, 154, 219))

    def test_rig_validation_rejects_wrong_types_and_nonfinite_values(self):
        for bad in (
            {"rig": "injection"},
            {"rig": 2},
            {"string_visible": "false"},
            {"stick_visible": 1},
            {"pivot_x": -1},
            {"start_rotation": 120},
            {"swing_deg": float("nan")},
            {"settle_duration": -1},
            {"overshoot_rotation": float("inf")},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_parameters("parallax", {"layer_cues": [{"layer": 1, **bad}]})

    def test_entrance_parameters_reject_out_of_range_values(self):
        for field, value in (("assembly_interval", -1), ("assembly_duration", 100),
                             ("assembly_start", -1), ("assembly_drop", .5)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_parameters("parallax", {field: value})


if __name__ == "__main__":
    unittest.main()
