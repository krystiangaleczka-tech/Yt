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

    def test_entrance_parameters_reject_out_of_range_values(self):
        for field, value in (("assembly_interval", -1), ("assembly_duration", 100),
                             ("assembly_start", -1), ("assembly_drop", .5)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_parameters("parallax", {field: value})


if __name__ == "__main__":
    unittest.main()
