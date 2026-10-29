"""Contract tests for the standalone Paper Theatre production category."""
import io
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from studio_api.app import create_app
from studio_core.paper_theatre import plan, GROUP_INDEX
from studio_timeline.paper_theatre import rig_image

HEADERS = {"X-Docos-Request": "1"}


class PaperTheatreCategoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        self.project = self.client.post("/api/projects", json={"title": "Wycinki"}, headers=HEADERS).json()
        self.base = "/api/projects/" + self.project["id"]
        self.background = self.png("tlo", background=True)
        self.cloud = self.png("chmura")
        self.fortress = self.png("forteca")
        self.tree = self.png("drzewo")
        self.character = self.png("urzednik")
        self.hero = self.png("cesarz")

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def png(self, name, *, background=False, size=(320, 180)):
        image = Image.new("RGB" if background else "RGBA", size, "#e6d7b7" if background else (0,0,0,0))
        if not background:
            ImageDraw.Draw(image).rectangle((25, 30, 64, 91), fill="#36513b")
        binary = io.BytesIO()
        image.save(binary, format="PNG")
        response = self.client.post(self.base+"/media", files={
            "file": (name+".png", binary.getvalue(), "image/png")
        }, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["asset"]["id"]

    def layers(self):
        # Intentionally unsorted: the planner must not trust input order.
        return [
            {"asset_id": self.character, "group": "characters"},
            {"asset_id": self.hero, "group": "hero"},
            {"asset_id": self.tree, "group": "vegetation"},
            {"asset_id": self.fortress, "group": "foundations"},
            {"asset_id": self.cloud, "group": "sky"},
        ]

    def payload(self):
        current=self.client.get(self.base).json()
        return {"expected_revision": current["revision"],
                "background_id": self.background, "layers": self.layers()}

    def test_sequential_group_plan_and_hero_final_outline(self):
        p=self.app.state.store.get(self.project["id"])
        scheduled=plan(self.app.state.store,p,self.background,self.layers())
        self.assertEqual(scheduled["asset_ids"],[
            self.cloud,self.fortress,self.tree,self.character,self.hero
        ])
        self.assertEqual([c["group"] for c in scheduled["layer_cues"]],
                         ["sky","foundations","vegetation","characters","hero"])
        cues=scheduled["layer_cues"]
        self.assertTrue(all(b["start"] >= a["start"] + a["duration"]
                            for a,b in zip(cues,cues[1:])))
        self.assertEqual(cues[-1]["rig"],"rake_lift")
        self.assertEqual(cues[0]["rig"],"hanging_drop")
        self.assertEqual(cues[1]["rig"],"bottom_rise")
        self.assertEqual(cues[-1]["outline_px"],8)
        self.assertFalse(scheduled["quality"]["reference_match_confirmed"])

    def test_create_preview_commit_and_timeline_are_independent(self):
        current=self.client.get(self.base).json()
        response=self.client.post(self.base+"/paper-theatre/scenes",
                json={"expected_revision":current["revision"]},headers=HEADERS)
        self.assertEqual(response.status_code,200,response.text)
        p=response.json()
        scene=p["scenes"][-1]
        self.assertEqual(scene["template"],"paper-theatre")
        payload=self.payload()
        preview=self.client.post(self.base+"/paper-theatre/"+scene["id"]+"/preview",
                                  json=payload,headers=HEADERS)
        self.assertEqual(preview.status_code,200,preview.text)
        self.assertEqual(self.client.get(self.base).json()["revision"],payload["expected_revision"])
        commit=self.client.post(self.base+"/paper-theatre/"+scene["id"]+"/commit",
                                 json=payload,headers=HEADERS)
        self.assertEqual(commit.status_code,200,commit.text)
        updated=commit.json()
        chosen=updated["scenes"][-1]
        self.assertEqual(chosen["asset_id"],self.background)
        self.assertEqual(chosen["asset_ids"][-1],self.hero)
        self.assertGreater(chosen["duration"],0)
        self.assertFalse(updated["sequence"]["clips"])
        timeline=self.client.post(self.base+"/scenes/"+scene["id"]+"/to-timeline",
                                  json={"expected_revision":updated["revision"]},headers=HEADERS)
        self.assertEqual(timeline.status_code,200,timeline.text)
        clip=timeline.json()["sequence"]["clips"][0]
        self.assertEqual(clip["template"],"paper-theatre")
        self.assertEqual(clip["asset_ids"][-1],self.hero)
        self.assertEqual(clip["parameters"]["layer_cues"][-1]["group"],"hero")

    def test_no_fake_flattened_layer_allowed(self):
        flattened=self.png("spłaszczony",background=True)
        p=self.app.state.store.get(self.project["id"])
        with self.assertRaisesRegex(ValueError,"przezroczysto"):
            plan(self.app.state.store,p,self.background,
                 [{"asset_id":flattened,"group":"hero"}])

    def test_reject_repeat_hero_and_character_without_final_hero(self):
        p=self.app.state.store.get(self.project["id"])
        with self.assertRaisesRegex(ValueError,"jedna"):
            plan(self.app.state.store,p,self.background,
                 [{"asset_id":self.hero,"group":"hero"},
                  {"asset_id":self.character,"group":"hero"}])
        with self.assertRaisesRegex(ValueError,"najważniejszą postać"):
            plan(self.app.state.store,p,self.background,
                 [{"asset_id":self.character,"group":"characters"}])

    def test_reject_mixed_size_and_duplicate(self):
        mismatched=self.png("inny rozmiar",size=(400,220))
        p=self.app.state.store.get(self.project["id"])
        with self.assertRaisesRegex(ValueError,"rozmiar"):
            plan(self.app.state.store,p,self.background,
                 [{"asset_id":mismatched,"group":"hero"}])
        with self.assertRaisesRegex(ValueError,"powtórzonych"):
            plan(self.app.state.store,p,self.background,
                 [{"asset_id":self.hero,"group":"hero"},
                  {"asset_id":self.hero,"group":"hero"}])

    def test_hero_outline_changes_silhouette_not_rectangle(self):
        sprite=Image.new("RGBA",(128,72),(0,0,0,0))
        ImageDraw.Draw(sprite).rectangle((42,23,58,49),fill="#303030")
        no_outline=rig_image(sprite,"static",{"rig":"static"},0,.2)
        outlined=rig_image(sprite,"static",{"outline_px":5,
                            "outline_color":"#e7c26d"},0,.2)
        self.assertEqual(no_outline.getpixel((39,35))[3],0)
        self.assertGreater(outlined.getpixel((39,35))[3],0)
        self.assertEqual(outlined.getpixel((1,1))[3],0)


if __name__=="__main__":
    unittest.main()
