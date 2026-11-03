import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from studio_api.app import create_app
from studio_api.flow import flow_prompt
from studio_core.models import Project


H = {"X-Docos-Request": "1"}


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.tmp.name), seed_demo=False)
        self.store = self.app.state.store
        self.client = TestClient(self.app)
        self.project = self.store.create(Project(
            title="Zombie w szpitalu", production_mode="animation_2d",
            legacy={"production_flow": {
                "factual": False,
                "bible": {"chronology": "Noc, kolejność wydarzeń jest ważna"},
                "master": {"variants": [{"id": "v1", "title": "Zombie",
                                        "description": "Zombie biega po szpitalu."}], "selected": "v1"},
                "acts": [{"id": "a1", "variants": [{"id": "v2", "title": "Początek",
                         "description": "Zombie budzi się."}], "selected": "v2"}],
                "sequences": [], "outlines": [], "scripts": {}
            }}
        ))

    def tearDown(self):
        self.client.close()
        self.app.state.jobs.close()
        self.tmp.cleanup()

    def test_prompt_provides_story_bible_and_future_story_context(self):
        p = flow_prompt(self.project, "script", "a1")
        self.assertIn("Noc, kolejność wydarzeń", p)
        self.assertIn("Zombie biega po szpitalu.", p)
        self.assertIn("TYLKO TEKST NARRACJI WYBRANEGO AKTU", p)

    def test_review_includes_distinct_six_roles(self):
        p = flow_prompt(self.project, "review")
        for role in ("Reżyser", "Redaktor scenariusza", "Krytyk", "Widz A", "Widz B", "Widz C"):
            self.assertIn(role, p)

    def test_fact_mode_refuses_unsourced_factual_script(self):
        project = self.project.model_copy(deep=True)
        project.legacy["production_flow"]["factual"] = True
        with self.assertRaises(ValueError):
            flow_prompt(project, "script", "a1")

    def test_generating_draft_never_changes_project(self):
        before = self.store.get(self.project.id)
        with patch("studio_api.flow.complete", return_value='[{"title":"Wariant","description":"Długi opis"}]'):
            r = self.client.post(f"/api/projects/{before.id}/flow/ai/master/generate", json={}, headers=H)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIn("Wariant", r.json()["response"])
        self.assertEqual(self.store.get(before.id).revision, before.revision)

    def test_director_prompt_knows_selected_scene_and_does_not_mutate(self):
        project = self.project.model_copy(deep=True)
        project.legacy["production_flow"]["outlines"] = [{
            "id": "o1", "sectionId": "s1", "seconds": 12,
            "variants": [{"id": "v3", "title": "Telefon", "description": "Telefon dzwoni, zombie patrzą w okno."}],
            "selected": "v3",
        }]
        prompt = flow_prompt(project, "direction", "o1", "Cisza przed zaskoczeniem")
        self.assertIn("Telefon dzwoni, zombie patrzą w okno", prompt)
        self.assertIn("shot", prompt.lower())
        self.assertIn("Cisza przed zaskoczeniem", prompt)
        with self.assertRaises(ValueError):
            flow_prompt(project, "direction", "wrong")

    def test_invalid_target_is_rejected(self):
        r = self.client.post(f"/api/projects/{self.project.id}/flow/ai/act/prompt",
                             json={"target_id": "nonexistent"}, headers=H)
        self.assertEqual(r.status_code, 422)


def director_flow(outline_id="o1", **plan_overrides):
    beat = {"id": "b1", "title": "Dzwonek", "goal": "Ujawnienie", "tensionBefore": 3, "tensionAfter": 8,
            "viewerKnows": "", "characterKnows": "", "soundCue": "telefon", "patternId": "rapid-intercut"}
    shot = {"id": "s1", "beatId": "b1", "typeId": "insert", "title": "Telefon", "description": "Telefon wibruje",
            "duration": 1.5, "transition": "cut", "sound": ""}
    plan = {"outlineId": outline_id, "sourceSignature": "v2:abc-def-1", "patternId": "rapid-intercut", "mode": "auto",
            "notes": "", "beats": [beat], "shots": [shot]}
    plan.update(plan_overrides)
    return {
        "version": 1, "factual": False, "sourceIdeaId": "",
        "bible": {"characters": "Lekarz", "chronology": "", "narration": "", "visuals": "", "facts": "", "transitions": ""},
        "master": {"id": "master", "variants": [{"id": "v1", "title": "Zombie", "description": "Pełna historia."}], "selected": "v1"},
        "acts": [{"id": "a1", "variants": [{"id": "v2", "title": "Początek", "description": "Zombie budzi się."}], "selected": "v2"}],
        "sequences": [{"id": "q1", "actId": "a1", "seconds": 120, "variants": [], "selected": None}],
        "outlines": [{"id": "o1", "sectionId": "q1", "seconds": 12,
                      "variants": [{"id": "v3", "title": "Telefon", "description": "Telefon dzwoni."}], "selected": "v3"}],
        "scripts": {"a1": "Nagle odezwał się telefon."},
        "approved": {"master": "v2:x-y-1", "direction": "v2:q-r-2"},
        "reviews": [],
        "director": {"mode": "guided", "plans": {outline_id: plan},
                     "customPatterns": [{"id": "custom-1", "name": "Mój wzorzec", "purpose": "", "cue": "", "rhythm": "",
                                         "shots": ["pov", "reaction"], "tension": [2, 9]}]},
    }


class FlowPersistenceTests(unittest.TestCase):
    """Regression: the UI used to PATCH `legacy`, which the API always refused, so nothing was saved."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.tmp.name), seed_demo=False)
        self.store = self.app.state.store
        self.client = TestClient(self.app)
        self.project = self.store.create(Project(title="Szpital", production_mode="animation_2d",
                                                 legacy={"docos_meta": {"keep": True}}))

    def tearDown(self):
        self.client.close()
        self.app.state.jobs.close()
        self.tmp.cleanup()

    def put(self, flow, revision=None):
        return self.client.put(f"/api/projects/{self.project.id}/flow", headers=H, json={
            "expected_revision": self.project.revision if revision is None else revision, "flow": flow})

    def test_generic_patch_still_refuses_legacy(self):
        r = self.client.patch(f"/api/projects/{self.project.id}", headers=H, json={
            "expected_revision": self.project.revision, "changes": {"legacy": {"production_flow": {}}}})
        self.assertEqual(r.status_code, 422)

    def test_flow_and_director_survive_save_and_reload_exactly(self):
        flow = director_flow()
        r = self.put(flow)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["revision"], self.project.revision + 1)
        reloaded = self.client.get(f"/api/projects/{self.project.id}").json()
        saved = reloaded["legacy"]["production_flow"]
        # Byte-identical (including key order) so client-side approval signatures stay valid after reload.
        self.assertEqual(json.dumps(saved, ensure_ascii=False), json.dumps(flow, ensure_ascii=False))
        self.assertEqual(saved["director"]["plans"]["o1"]["shots"][0]["duration"], 1.5)
        self.assertEqual(saved["approved"]["direction"], "v2:q-r-2")
        self.assertEqual(reloaded["legacy"]["docos_meta"], {"keep": True}, "other legacy keys must stay untouched")

    def test_stale_revision_is_rejected_with_conflict(self):
        self.assertEqual(self.put(director_flow()).status_code, 200)
        r = self.put(director_flow(notes="druga zmiana"))
        self.assertEqual(r.status_code, 409)

    def test_save_can_be_undone(self):
        self.assertEqual(self.put(director_flow()).status_code, 200)
        current = self.store.get(self.project.id)
        r = self.client.post(f"/api/projects/{self.project.id}/history/undo", headers=H,
                             json={"expected_revision": current.revision})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertNotIn("production_flow", r.json()["legacy"])

    def test_invalid_flow_is_rejected_and_nothing_changes(self):
        bad_tension = director_flow()
        bad_tension["director"]["plans"]["o1"]["beats"][0]["tensionAfter"] = 11
        bad_duration = director_flow()
        bad_duration["director"]["plans"]["o1"]["shots"][0]["duration"] = 0
        wrong_key = director_flow()
        wrong_key["director"]["plans"]["o1"]["outlineId"] = "other"
        duplicate = director_flow()
        duplicate["outlines"].append(dict(duplicate["outlines"][0]))
        for flow in (bad_tension, bad_duration, wrong_key, duplicate, ["not", "an", "object"]):
            r = self.put(flow)
            self.assertEqual(r.status_code, 422, r.text)
        self.assertEqual(self.store.get(self.project.id).revision, self.project.revision)

    def test_minimal_and_older_flows_are_accepted(self):
        r = self.put({"factual": False, "acts": [], "futureField": {"x": 1}})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["legacy"]["production_flow"]["futureField"], {"x": 1})

    def test_director_prompt_uses_neighbouring_plans_and_custom_patterns(self):
        flow = director_flow()
        flow["outlines"].append({"id": "o2", "sectionId": "q1", "seconds": 20,
                                 "variants": [{"id": "v4", "title": "Okno", "description": "Zombie za szybą."}],
                                 "selected": "v4"})
        flow["outlines"].append({"id": "o3", "sectionId": "q1", "seconds": 20,
                                 "variants": [{"id": "v5", "title": "Daleko", "description": "Inna scena."}],
                                 "selected": "v5"})
        flow["director"]["plans"]["o3"] = director_flow("o3")["director"]["plans"]["o3"]
        self.assertEqual(self.put(flow).status_code, 200)
        prompt = flow_prompt(self.store.get(self.project.id), "direction", "o2")
        context = json.loads(prompt.split("KONTEKST:\n", 1)[1])
        self.assertEqual(sorted(context["director_plans"]), ["o1", "o3"])
        self.assertEqual(context["custom_patterns"][0]["name"], "Mój wzorzec")
        far = flow_prompt(self.store.get(self.project.id), "direction", "o1")
        self.assertEqual(sorted(json.loads(far.split("KONTEKST:\n", 1)[1])["director_plans"]), [])
