"""Deterministic regressions for physically assembled paper cutout entrances."""
import unittest

from PIL import Image, ImageDraw

from studio_timeline.paper_theatre import rig_image


class PaperTheatreMotionTests(unittest.TestCase):
    @staticmethod
    def sprite():
        canvas = Image.new("RGBA", (240, 180))
        ImageDraw.Draw(canvas).rectangle((100, 60, 125, 145), fill=(180, 120, 65, 255))
        return canvas

    def test_string_connects_ceiling_during_drop_and_retracts_after_settle(self):
        sprite = self.sprite()
        cue = {"string_visible": True, "swing_deg": 0, "overshoot": 0,
               "settle_duration": .22}
        mid = rig_image(sprite, "hanging_drop", cue, .30, .65)
        self.assertGreater(mid.getpixel((112, 8))[3], 0)
        self.assertGreater(mid.getbbox()[3] - mid.getbbox()[1], 40)
        end = rig_image(sprite, "hanging_drop", cue, 1.0, .65)
        self.assertEqual(end.getpixel((112, 8))[3], 0)
        self.assertGreater(end.getpixel((112, 100))[3], 0)

    def test_contour_survives_standee_rotation(self):
        sprite = self.sprite()
        plain = rig_image(sprite, "rake_lift", {"stick_visible": False}, 1, .7)
        bold = rig_image(sprite, "rake_lift", {
            "stick_visible": False, "outline_px": 12,
            "outline_color": "#362820"}, 1, .7)
        self.assertEqual(plain.getpixel((92, 100))[3], 0)
        self.assertGreater(bold.getpixel((92, 100))[3], 0)

    def test_standee_raises_from_foot_instead_of_popping_on(self):
        sprite = self.sprite()
        cue = {"stick_visible": False, "start_rotation": 82,
               "overshoot_rotation": -5, "settle_duration": .22}
        start = rig_image(sprite, "rake_lift", cue, 0, .7)
        end = rig_image(sprite, "rake_lift", cue, 1, .7)
        self.assertLess(start.getbbox()[3] - start.getbbox()[1],
                        end.getbbox()[3] - end.getbbox()[1] * .6)
        self.assertGreater(end.getpixel((112, 90))[3], 0)


if __name__ == "__main__":
    unittest.main()
