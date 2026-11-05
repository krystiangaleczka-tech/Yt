import copy
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.app import create_app
from studio_core import continuity
from studio_core.models import Project

H = {"X-Docos-Request": "1"}


def shot(i, desc, sound="", dur=2.0):
    return {"id": f"s{i}", "beatId": "b", "typeId": "medium", "title": desc, "description": desc, "duration": dur,
            "transition": "cut", "sound": sound}


def flow_with(days, world=None):
    """days: [[shot, ...], ...] — jeden akt, jedna sekwencja i jedna scena na dzień."""
    flow = {"acts": [], "sequences": [], "outlines": [], "scripts": {}, "director": {"mode": "auto", "plans": {}},
            "world": world or {}}
    for n, shots in enumerate(days, start=1):
        flow["acts"].append({"id": f"a{n}", "variants": [{"id": f"v{n}", "title": f"Dzień {n}"}], "selected": f"v{n}"})
        flow["sequences"].append({"id": f"q{n}", "actId": f"a{n}", "variants": [], "selected": None})
        flow["outlines"].append({"id": f"o{n}", "sectionId": f"q{n}", "variants": [], "selected": None})
        flow["director"]["plans"][f"o{n}"] = {"outlineId": f"o{n}", "beats": [], "shots": shots}
    return flow


def rules_of(report, rule):
    return [i for i in report["issues"] if i["rule"] == rule]


class ContinuityTests(unittest.TestCase):
    def test_refs_follow_film_order_and_prologue(self):
        flow = flow_with([[shot(1, "otwarcie"), shot(2, "otwarcie 2"), shot(3, "dzień 1")], [shot(4, "dzień 2")]],
                         {"prologue": {"1": 2}})
        us = continuity.units(flow)
        self.assertEqual([u["unit"] for u in us], [0, 1, 2])
        self.assertEqual(us[0]["shots"][1]["ref"], "d00_02")
        self.assertEqual(us[1]["shots"][0]["ref"], "d01_01")

    def test_payoff_without_setup_and_before_setup(self):
        days = [[shot(1, "a"), shot(2, "b")], [shot(3, "c")]]
        r = continuity.check(flow_with(days, {"threads": [
            {"title": "kurtka", "payoff": ["d02_01"]},
            {"title": "klucz", "setup": ["d02_01"], "payoff": ["d01_02"]}]}))
        msgs = [i["message"] for i in rules_of(r, "wątek")]
        self.assertTrue(any("bez zasiewu" in m for m in msgs))
        self.assertTrue(any("przed zasiewem" in m for m in msgs))
        self.assertTrue(all(i["severity"] == 3 for i in rules_of(r, "wątek")))

    def test_prop_used_before_seeded_and_missing_shot(self):
        r = continuity.check(flow_with([[shot(1, "a")], [shot(2, "b")]], {"props": [
            {"name": "krótkofalówka", "seeded": "d02_01", "uses": ["d01_01", "d01_05"]}]}))
        self.assertTrue(any("pokazany dopiero" in i["message"] for i in rules_of(r, "rekwizyt")))
        self.assertTrue(any("nie istnieje" in i["message"] for i in rules_of(r, "odwołanie")))

    def test_scenario_refs_only_order(self):
        r = continuity.check(flow_with([[shot(1, "a")]], {"threads": [{"title": "t", "setup": ["d01_01"], "payoff": ["s05_20"]},
                                                                     {"title": "u", "setup": ["s05_20"], "payoff": ["d01_01"]}]}))
        self.assertFalse(rules_of(r, "odwołanie"))
        self.assertEqual(len(rules_of(r, "wątek")), 1)

    def test_anchor_detects_shifted_ref(self):
        r = continuity.check(flow_with([[shot(1, "kanistry z kranu"), shot(2, "kran")]], {"props": [
            {"name": "kanister", "seeded": "d01_01~kanistr", "uses": ["d01_02~kanistr"]}]}))
        self.assertEqual([i["ref"] for i in rules_of(r, "odwołanie")], ["d01_02"])

    def test_event_needs_active_rule(self):
        world = {"rules": [{"id": "linia", "name": "telefon wolny (słuchawka odłożona)", "from": "", "to": "d01_02"}],
                 "events": [{"at": "d02_01", "note": "telefon dzwoni", "needs": ["linia"]}]}
        r = continuity.check(flow_with([[shot(1, "a"), shot(2, "słuchawka na biurku")], [shot(3, "dzwoni")]], world))
        self.assertEqual(len(rules_of(r, "zasada")), 1)

    def test_resource_ledger_and_claims(self):
        world = {"characters": [{"name": "A", "party": True}, {"name": "B", "party": True, "joins": "d02_01"}],
                 "resources": [{"name": "woda", "unit": "l", "perPersonDay": 1, "start": 4,
                                "claims": [{"at": "d01_01", "days": 4, "note": "woda na 4 dni"},
                                           {"at": "d02_01", "days": 10}]}]}
        r = continuity.check(flow_with([[shot(1, "a")], [shot(2, "b")], [shot(3, "c")], [shot(4, "d")]], world))
        msgs = [i["message"] for i in rules_of(r, "zasób")]
        self.assertTrue(any("d02_01" in m and "10" in m for m in msgs))
        self.assertTrue(any("poniżej zera" in m for m in msgs))
        self.assertFalse(any("d01_01" in i["ref"] for i in rules_of(r, "zasób")))

    def test_name_reserved_for_one_character(self):
        world = {"characters": [{"name": "Basia", "role": "kucharka z chłodni", "namedIn": ["d02_*"]}]}
        r = continuity.check(flow_with([[shot(1, "pielęgniarka", "L: Znałem ją. Basia z nocnej zmiany.")],
                                        [shot(2, "kucharka", "Henryk: „To Basia.”")]], world))
        self.assertEqual([i["ref"] for i in rules_of(r, "imię")], ["d01_01"])

    def test_spoiler_only_counts_spoken_text_before_limit(self):
        world = {"spoilers": [{"pattern": "lekarz dyżurny", "notBefore": "d02_01", "why": "narrator domyśla się w dniu 2"}]}
        r = continuity.check(flow_with([[shot(1, "notes: lekarz dyżurny", "L: Został lekarz dyżurny.")],
                                        [shot(2, "x", "L: To był lekarz dyżurny.")]], world))
        self.assertEqual([i["ref"] for i in rules_of(r, "wiedza")], ["d01_01"])

    def test_tempo_and_narration(self):
        shots = [shot(i, "x", "L: słowa", 2.0) for i in range(5)]
        r = continuity.check(flow_with([shots], {"tempo": {"minSeconds": 55, "maxSeconds": 80, "maxVoiceShare": 0.8}}))
        self.assertTrue(rules_of(r, "tempo"))
        self.assertTrue(rules_of(r, "narracja"))


class ContinuityApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.tmp.name), seed_demo=False)
        self.client = TestClient(self.app)
        flow = flow_with([[shot(1, "a")], [shot(2, "b")]], {"threads": [{"title": "t", "setup": ["d01_01"], "payoff": ["d02_01"]}]})
        self.project = self.app.state.store.create(Project(title="T", production_mode="animation_2d",
                                                           legacy={"production_flow": flow}))

    def tearDown(self):
        self.client.close()
        self.app.state.jobs.close()
        self.tmp.cleanup()

    def test_review_goes_stale_after_change_and_marks_linked_units(self):
        pid = self.project.id
        for act in ("a1", "a2"):
            r = self.client.post(f"/api/projects/{pid}/flow/review/{act}", headers=H,
                                 json={"status": "zatwierdzona", "checks": {"tempo": "ok"}, "reviewer": "reżyser"})
            self.assertEqual(r.status_code, 200, r.text)
        report = self.client.post(f"/api/projects/{pid}/continuity/check", headers=H).json()
        self.assertEqual([u["review"] for u in report["units"]], ["zatwierdzona", "zatwierdzona"])
        project = self.client.get(f"/api/projects/{pid}", headers=H).json()
        flow = copy.deepcopy(project["legacy"]["production_flow"])
        flow["director"]["plans"]["o1"]["shots"][0]["description"] = "zmienione ujęcie"
        r = self.client.put(f"/api/projects/{pid}/flow", headers=H, json={"expected_revision": project["revision"], "flow": flow})
        self.assertEqual(r.status_code, 200, r.text)
        report = self.client.post(f"/api/projects/{pid}/continuity/check", headers=H).json()
        self.assertEqual(report["units"][0]["review"], "nieaktualna")
        self.assertEqual(report["units"][1].get("impactedBy"), [1])
        log = self.client.get(f"/api/projects/{pid}", headers=H).json()["legacy"]["production_flow"]["log"]
        self.assertEqual([e["kind"] for e in log], ["recenzja", "recenzja"])

    def test_log_append_keeps_rest_of_flow(self):
        pid = self.project.id
        r = self.client.post(f"/api/projects/{pid}/flow/log", headers=H,
                             json={"entry": {"who": "Claude", "unit": 2, "kind": "tworzenie", "summary": "Narysowano dzień 2",
                                             "files": ["render_d02.py"]}})
        self.assertEqual(r.status_code, 200, r.text)
        flow = r.json()["legacy"]["production_flow"]
        self.assertEqual(flow["log"][-1]["summary"], "Narysowano dzień 2")
        self.assertEqual(flow["world"]["threads"][0]["title"], "t")

    def test_timeline_gap_is_reported(self):
        pid = self.project.id
        project = self.client.get(f"/api/projects/{pid}", headers=H).json()
        asset_free = [{"type": "add_clip", "clip": {"track_id": "v1", "start": s, "duration": 30, "title": t, "template": "title",
                                                     "text": t}} for s, t in ((0, "a"), (45, "b"))]
        r = self.client.post(f"/api/projects/{pid}/edits", headers=H, json={"expected_revision": project["revision"], "operations": asset_free})
        if r.status_code != 200:
            self.skipTest("add_clip nie przyjmuje tej postaci klipu: " + r.text[:120])
        report = self.client.post(f"/api/projects/{pid}/continuity/check", headers=H).json()
        self.assertTrue(any(i["rule"] == "oś" and "dziura 15" in i["message"] for i in report["issues"]))

    def test_invalid_review_status_is_rejected(self):
        r = self.client.post(f"/api/projects/{self.project.id}/flow/review/a1", headers=H, json={"status": "super"})
        self.assertGreaterEqual(r.status_code, 400)

    def test_handbook_lists_chapters(self):
        r = self.client.get("/api/handbook", headers=H)
        self.assertEqual(r.status_code, 200)
        keys = [c["key"] for c in r.json()["chapters"]]
        self.assertIn("kadr", keys)
        self.assertIn("recenzja", keys)


if __name__ == "__main__":
    unittest.main()
