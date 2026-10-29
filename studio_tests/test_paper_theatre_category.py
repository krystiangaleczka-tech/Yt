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
        # Uploads are content-addressed: distinct cutouts need distinct pixels.
        variant = sum((i + 1) * ord(char) for i, char in enumerate(name))
        color = (80 + variant % 130, 60 + (variant // 7) % 140, 70 + (variant // 11) % 130)
        image = Image.new("RGB" if background else "RGBA", size, color if background else (0, 0, 0, 0))
        if not background:
            start = 15 + variant % 30
            ImageDraw.Draw(image).rectangle((start, 30, start + 38, 91), fill=(*color, 255))
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

    def asset_manifest(self, *, small=None):
        return {
            "brief": "Chińskie cesarstwo składane jak papierowy teatr.",
            "style": "Ciepły papier ryżowy, tusz, czerwone złoto.",
            "objects": [
                {"id": "emperor", "name": "Cesarz", "group": "hero",
                 "description": "Cesarz w szatach", "asset_id": self.hero,
                 "x": .3, "y": .9, "width": .22, "z": 70},
                {"id": "cloud", "name": "Chmura", "group": "sky",
                 "description": "Pojedyncza chmura", "asset_id": self.cloud,
                 "x": .7, "y": .2, "width": .16, "z": -10},
                {"id": "wall", "name": "Mur", "group": "foundations",
                 "description": "Mur z kamieni", "asset_id": small or self.fortress,
                 "x": .53, "y": .72, "width": .5, "z": 30},
            ],
        }

    def test_asset_first_manifest_prompts_and_assembly(self):
        from studio_core.paper_theatre_asset_first import normalize_manifest, image_prompts
        obj = self.asset_manifest()
        normalized = normalize_manifest(obj)
        self.assertEqual([e["id"] for e in normalized["objects"]], ["cloud", "wall", "emperor"])
        prompts = image_prompts(normalized)
        self.assertEqual(len(prompts), 3)
        self.assertTrue(all("ONE SINGLE ISOLATED" in e["prompt"] and "RGBA PNG" in e["prompt"] for e in prompts))
        current = self.client.get(self.base).json()
        created = self.client.post(self.base+"/paper-theatre/scenes",
                                   json={"expected_revision":current["revision"]}, headers=HEADERS)
        self.assertEqual(created.status_code,200,created.text)
        shot = created.json()["scenes"][-1]["id"]
        rev = created.json()["revision"]
        route = self.base + "/paper-theatre/" + shot + "/asset-first/"
        prompt = self.client.post(route+"propose",json={"expected_revision":rev,
                                  "brief":"Chińskie imperium","style":"Papier ryżowy","action":"prompt"},
                                  headers=HEADERS)
        self.assertEqual(prompt.status_code,200,prompt.text)
        self.assertIn("objects",prompt.json()["prompt"])
        proposals = self.client.post(route+"prompts",
            json={"expected_revision":rev,"manifest":obj},headers=HEADERS)
        self.assertEqual(proposals.status_code,200,proposals.text)
        self.assertEqual(len(proposals.json()["prompts"]),3)
        saved = self.client.post(route+"save",
            json={"expected_revision":rev,"manifest":obj},headers=HEADERS)
        self.assertEqual(saved.status_code,200,saved.text)
        prepared = saved.json()["scenes"][-1]
        self.assertEqual(prepared["generation"]["paper_theatre_asset_first"]["objects"][0]["id"], "cloud")
        self.assertFalse(prepared["asset_ids"])
        assembled = self.client.post(route+"assemble",json={
            "expected_revision":saved.json()["revision"], "background_id":self.background,
            "manifest":obj},headers=HEADERS)
        self.assertEqual(assembled.status_code,200,assembled.text)
        shot = assembled.json()["scenes"][-1]
        self.assertEqual(shot["asset_ids"],[self.cloud,self.fortress,self.hero])
        cues=shot["parameters"]["layer_cues"]
        self.assertEqual(cues[0]["layout_x"], .7)
        self.assertEqual(cues[1]["layout_width"], .5)
        self.assertEqual(cues[2]["z_index"], 70)
        self.assertEqual(cues[-1]["group"],"hero")

    def test_asset_first_small_pngs_and_validation(self):
        from studio_core.paper_theatre_asset_first import normalize_manifest, assemble_manifest
        small = self.png("malutka-wieża", size=(48,90))
        manifest = self.asset_manifest(small=small)
        p = self.app.state.store.get(self.project["id"])
        result = assemble_manifest(self.app.state.store,p,self.background,manifest)
        self.assertEqual(result["cutouts"],3)
        self.assertEqual(result["layer_cues"][1]["layout_width"], .5)
        bad=self.asset_manifest()
        bad["objects"][0]["x"] = float("nan")
        with self.assertRaisesRegex(ValueError,"Pozycja"):
            normalize_manifest(bad)
        bad=self.asset_manifest()
        bad["objects"][0]["z"] = 1.3
        with self.assertRaisesRegex(ValueError,"całkowitej"):
            normalize_manifest(bad)
        bad=self.asset_manifest()
        bad["objects"][0]["asset_id"] = ""
        with self.assertRaisesRegex(ValueError,"Brak wygenerowanych"):
            assemble_manifest(self.app.state.store,p,self.background,bad)

    def test_asset_first_render_uses_layout_and_z_not_cue_order(self):
        from studio_timeline.templates import paint
        from studio_core.models import Clip
        class Frames:
            def __init__(self):
                self.images=[
                    Image.new("RGBA",(100,60),"#e6d7b7"),
                    Image.new("RGBA",(20,20),"#ff0000"),
                    Image.new("RGBA",(20,20),"#0000ff")]
            def frame(self,i,n):
                return self.images[i]
        clip=Clip(track_id="v1", template="paper-theatre", duration=60)
        settings={"depth":0,"layer_cues":[
            {"layer":1,"rig":"static","start":0,"layout_x":.5,"layout_y":.8,
             "layout_width":.2,"z_index":70},
            {"layer":2,"rig":"static","start":0,"layout_x":.5,"layout_y":.8,
             "layout_width":.2,"z_index":30},
        ]}
        image=paint(clip,settings,Frames(),30,100,60,10)
        # Higher Z red is painted above lower Z blue even though red is first.
        self.assertEqual(image.getpixel((50,40))[:3],(255,0,0))
        self.assertEqual(image.getpixel((10,40))[:3],(230,215,183))

    def test_reference_guided_draft_from_scene_and_approved_inventory(self):
        from studio_core.paper_theatre_reference import draft_prompt
        from studio_core.paper_theatre_asset_first import normalize_manifest, image_prompts, assemble_manifest
        current = self.client.get(self.base).json()
        response = self.client.post(self.base + "/paper-theatre/scenes",
            json={"expected_revision": current["revision"]}, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.text)
        shot = response.json()["scenes"][-1]
        path = self.base + "/paper-theatre/" + shot["id"] + "/reference/"
        reference = self.png("draft-reference", background=True)
        prompt = self.client.post(path + "prompt", json={
            "expected_revision": self.client.get(self.base).json()["revision"],
            "brief": "Cesarz wydaje rozkaz", "style": "Papier ryżowy",
        }, headers=HEADERS)
        self.assertEqual(prompt.status_code, 200, prompt.text)
        self.assertIn("Cesarz wydaje rozkaz", prompt.json()["prompt"])
        self.assertIn("512", str(prompt.json()["width"]))
        self.assertIn("ONLY a small preview", prompt.json()["prompt"])
        manifest = self.asset_manifest()
        manifest.update(mode="reference-guided", reference_asset_id=reference,
                        reference_notes="Cesarz po lewej, obłoki wysoko",
                        reference_approved=False)
        project = self.app.state.store.get(self.project["id"])
        with self.assertRaisesRegex(ValueError, "zaakceptuj"):
            assemble_manifest(self.app.state.store, project, self.background, manifest)
        manifest["reference_approved"] = True
        data = normalize_manifest(manifest)
        self.assertEqual(data["reference_asset_id"], reference)
        self.assertEqual(data["mode"], "reference-guided")
        prompts = image_prompts(data)
        self.assertTrue(all(p["reference_asset_id"] == reference for p in prompts))
        self.assertIn("Cesarz po lewej", prompts[-1]["prompt"])
        self.assertEqual(assemble_manifest(self.app.state.store, project,
            self.background, manifest)["cutouts"], 3)
        with self.assertRaisesRegex(ValueError, "nie może być tłem"):
            assemble_manifest(self.app.state.store, project, reference, manifest)
        self.assertFalse(any(c["asset_id"] == reference for c in data["objects"]))

    def test_vision_reference_route_uses_connected_analysis_not_pixel_cutting(self):
        from unittest.mock import patch
        current = self.client.get(self.base).json()
        response = self.client.post(self.base + "/paper-theatre/scenes",
            json={"expected_revision": current["revision"]}, headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        sid = response.json()["scenes"][-1]["id"]
        image = self.png("visual draft", background=True)
        with patch("studio_core.paper_theatre_reference.propose_objects_from_reference") as vision:
            vision.return_value = self.asset_manifest()
            result = self.client.post(
                self.base + "/paper-theatre/" + sid + "/reference/analyze",
                json={"expected_revision": self.client.get(self.base).json()["revision"],
                      "reference_asset_id": image,
                      "brief": "Chińska scena", "style": "Papier", "reference_notes": "Most z prawej"},
                headers=HEADERS)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(len(result.json()["manifest"]["objects"]), 3)
        vision.assert_called_once()
        self.assertEqual(vision.call_args.args[4], image)

    def test_hero_outline_changes_silhouette_not_rectangle(self):
        sprite=Image.new("RGBA",(128,72),(0,0,0,0))
        ImageDraw.Draw(sprite).rectangle((42,23,58,49),fill="#303030")
        no_outline=rig_image(sprite,"static",{"rig":"static"},0,.2)
        outlined=rig_image(sprite,"static",{"outline_px":5,
                            "outline_color":"#e7c26d"},0,.2)
        self.assertEqual(no_outline.getpixel((39,35))[3],0)
        self.assertGreater(outlined.getpixel((39,35))[3],0)
        self.assertEqual(outlined.getpixel((1,1))[3],0)


    def test_technique_is_not_documentary_only(self):
        from studio_core.paper_theatre_reference import draft_prompt
        from studio_core.paper_theatre_asset_first import DEFAULT_BRIEF, DEFAULT_STYLE
        from types import SimpleNamespace
        scene = SimpleNamespace(title="Legenda", narration="Opowieść o dawnej królowej.",
                                prompt="")
        prompt = draft_prompt(scene, "Bitwa w epoce brązu", DEFAULT_STYLE)
        self.assertIn("story shot", prompt)
        self.assertNotIn("documentary shot", prompt)
        self.assertNotIn("documentary", DEFAULT_STYLE.lower())
        self.assertNotIn("dokument", DEFAULT_BRIEF.lower())

    def test_per_object_pivot_and_entrance_rig_round_trip(self):
        from studio_core.paper_theatre_asset_first import normalize_manifest, assemble_manifest
        manifest = self.asset_manifest()
        manifest["objects"][1].update(pivot_x=.17, pivot_y=.91, rig="hanging_drop")
        normalized = normalize_manifest(manifest)
        self.assertEqual(normalized["objects"][1]["pivot_x"], .17)
        self.assertEqual(normalized["objects"][1]["rig"], "hanging_drop")
        project = self.app.state.store.get(self.project["id"])
        data = assemble_manifest(self.app.state.store, project, self.background, normalized)
        cue = data["layer_cues"][1]
        self.assertEqual(cue["rig"], "hanging_drop")
        self.assertEqual(cue["pivot_x"], .17)
        self.assertEqual(cue["pivot_y"], .91)
        for key, invalid in (("pivot_x", -1), ("pivot_y", True),
                             ("rig", "unknown_motion")):
            broken = self.asset_manifest()
            broken["objects"][1][key] = invalid
            with self.assertRaises(ValueError):
                normalize_manifest(broken)

    def test_geometry_and_alpha_diagnostics_are_advisory(self):
        from studio_core.paper_theatre_quality import alpha_diagnostics, layout_warnings
        sprite = Image.new("RGBA", (120, 60), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        draw.rectangle((10, 10, 30, 40), fill=(20, 30, 40, 255))
        draw.rectangle((85, 10, 105, 40), fill=(20, 30, 40, 255))
        self.assertEqual(alpha_diagnostics(sprite)["regions"], 2)
        entries = [
            {"name": "Drzewo", "bounds": (0, 0, 100, 100),
             "layout": {"layout_x": .5, "layout_y": .7, "layout_width": .4}},
            {"name": "Mur", "bounds": (0, 0, 100, 100),
             "layout": {"layout_x": .5, "layout_y": .7, "layout_width": .4}},
            {"name": "Obłok", "bounds": (0, 0, 100, 100),
             "layout": {"layout_x": .99, "layout_y": .2, "layout_width": .4}},
        ]
        warnings = layout_warnings(entries, (320, 180))
        self.assertTrue(any("nakładanie" in w for w in warnings))
        self.assertTrue(any("poza kadr" in w for w in warnings))
        self.assertEqual(layout_warnings([{"name": "Dym", "layout": {}}], (320,180)), [])


if __name__=="__main__":
    unittest.main()
