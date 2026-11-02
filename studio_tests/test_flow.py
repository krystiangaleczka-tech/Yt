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
