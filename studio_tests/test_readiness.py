"""Gotowość filmu (GET /api/projects/{id}/gotowosc): lektor, muzyka, efekty, zgoda na próbkę, recenzje, ciągłość."""
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.app import create_app
from studio_core import readiness
from studio_core.models import Asset, Clip, Project, Scene, Sequence

H = {"X-Docos-Request": "1"}
FPS = 30
# Trzy ujęcia: 0–2 s z kwestią, 2–4 s bez kwestii, 4–7 s z kwestią. Film trwa 7 s (210 klatek).
SHOTS = [("Zapowiedź", 0, 60, "Some words came from a real war."), ("Kurtyna", 60, 60, ""),
         ("Skok", 120, 90, "He jumped from the cliff.")]


def audio(aid, seconds):
    return Asset(id=aid, name=aid, kind="audio", filename=f"{aid}.wav", mime="audio/wav", sha256="0" * 64, duration=seconds)


def flow_one_act():
    shot = {"id": "s1", "beatId": "b", "typeId": "medium", "title": "skok", "description": "skok z urwiska", "duration": 2.0,
            "transition": "cut", "sound": ""}
    return {"acts": [{"id": "a1", "variants": [{"id": "v1", "title": "Akt 1 · Skok"}], "selected": "v1"}],
            "sequences": [{"id": "q1", "actId": "a1", "variants": [], "selected": None}],
            "outlines": [{"id": "o1", "sectionId": "q1", "variants": [], "selected": None}],
            "scripts": {}, "director": {"mode": "auto", "plans": {"o1": {"outlineId": "o1", "beats": [], "shots": [shot]}}},
            "world": {}, "log": [],
            "book": {"files": [{"path": "output/test-film/studio_film.py", "role": "plan, klatki i dźwięk"}]}}


def film(narrated=(), music=None, effects=None, log=None, voice_at=None):
    """narrated: numery ujęć z klipem lektora; music/effects: (od, do) w klatkach albo None."""
    scenes = [Scene(id=f"scene_{n}", title=t, narration=text, start=start, duration=dur)
              for n, (t, start, dur, text) in enumerate(SHOTS, start=1)]
    assets = [audio("asset_music", 60), audio("asset_fx", 60)] + [audio(f"asset_l{n}", 2) for n in narrated]
    clips = [Clip(id=f"clip_v{n}", track_id="v1", scene_id=s.id, title=s.title, start=s.start, duration=s.duration,
                  template="title", text=s.title) for n, s in enumerate(scenes, start=1)]
    for n in narrated:
        s = scenes[n - 1]
        start = (voice_at or {}).get(n, s.start + 6)
        clips.append(Clip(id=f"clip_l{n}", track_id="a1", asset_id=f"asset_l{n}", scene_id=s.id, title="Lektor", start=start, duration=45))
    for track, span, aid in (("a2", music, "asset_music"), ("a3", effects, "asset_fx")):
        if span:
            clips.append(Clip(id=f"clip_{track}", track_id=track, asset_id=aid, title=track, start=span[0], duration=span[1] - span[0]))
    flow = flow_one_act()
    flow["log"] = log or []
    return Project(title="Test gotowości", production_mode="animation_2d", scenes=scenes, assets=assets,
                   sequence=Sequence(fps_num=FPS, clips=clips), legacy={"production_flow": flow})


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.tmp.name), seed_demo=False)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.app.state.jobs.close()
        self.tmp.cleanup()

    def make(self, **kw):
        return self.app.state.store.create(film(**kw)).id

    def state(self, pid):
        r = self.client.get(f"/api/projects/{pid}/gotowosc")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        return data, {i["key"]: i for i in data["items"]}

    def test_project_without_narration_or_sound(self):
        data, items = self.state(self.make())
        self.assertFalse(data["ready"])
        self.assertEqual(data["film"]["seconds"], 7.0)
        self.assertEqual(items["lektor"]["state"], "brak")
        self.assertEqual([s["nr"] for s in items["lektor"]["shots"]], [1, 3])
        self.assertIn("0 z 2", items["lektor"]["summary"])
        self.assertEqual(items["lektor"]["command"], "python3 -I output/test-film/studio_film.py lektor")
        self.assertEqual(items["muzyka"]["state"], "brak")
        self.assertEqual(items["efekty"]["state"], "brak")
        self.assertEqual(items["probka"]["state"], "brak")
        self.assertEqual(items["recenzje"]["state"], "brak")
        self.assertEqual(items["render"]["state"], "informacja")
        for title in ("Lektor", "Muzyka", "Efekty", "Próbka dźwięku zatwierdzona", "Recenzje aktów"):
            self.assertIn(title, data["blocking"])
        self.assertEqual(list(items), ["ciaglosc", "recenzje", "lektor", "probka", "muzyka", "efekty", "render"])

    def test_partial_narration_lists_missing_lines(self):
        _, items = self.state(self.make(narrated=(1,)))
        self.assertEqual(items["lektor"]["state"], "brak")
        self.assertIn("1 z 2", items["lektor"]["summary"])
        self.assertEqual([(s["nr"], s["sceneId"]) for s in items["lektor"]["shots"]], [(3, "scene_3")])

    def test_full_narration_is_ready(self):
        _, items = self.state(self.make(narrated=(1, 3)))
        self.assertEqual(items["lektor"]["state"], "gotowe")
        self.assertEqual(items["lektor"]["shots"], [])

    def test_narration_outside_its_shot_needs_recount(self):
        # Kwestia ujęcia 3 zaczyna się w 1 s — ujęcia zmieniły długość, a lektor nie poszedł za nimi.
        _, items = self.state(self.make(narrated=(1, 3), voice_at={3: 30}))
        self.assertEqual(items["lektor"]["state"], "do przeliczenia")
        self.assertEqual([s["nr"] for s in items["lektor"]["shots"]], [3])

    def test_sound_shorter_than_timeline_needs_recount(self):
        _, items = self.state(self.make(narrated=(1, 3), music=(0, 150), effects=(0, 210)))
        self.assertEqual(items["muzyka"]["state"], "do przeliczenia")
        self.assertIn("dźwięk do przeliczenia", items["muzyka"]["summary"])
        self.assertEqual(items["muzyka"]["coverage"], {"start": 0.0, "end": 5.0, "film": 7.0, "clips": 1})
        self.assertEqual(items["efekty"]["state"], "gotowe")

    def test_sound_within_half_second_and_longer_than_film(self):
        _, items = self.state(self.make(music=(0, 199), effects=(0, 240)))
        self.assertEqual(items["muzyka"]["state"], "gotowe")  # 6,63 s przy 7 s: w tolerancji 0,5 s
        self.assertEqual(items["efekty"]["state"], "do przeliczenia")
        self.assertIn("dłużej niż film", items["efekty"]["summary"])

    def test_sound_sample_decision_is_logged_with_quote(self):
        pid = self.make(music=(0, 210), effects=(0, 210))
        _, items = self.state(pid)
        self.assertIn("Dźwięk jest już wgrany", items["probka"]["summary"])
        r = self.client.post(f"/api/projects/{pid}/gotowosc/probka", headers=H, json={"decision": "zatwierdzona"})
        self.assertEqual(r.status_code, 422)  # bez cytatu reżysera nie ma zgody
        r = self.client.post(f"/api/projects/{pid}/gotowosc/probka", headers=H,
                             json={"decision": "do poprawy", "quote": "muzyka za głośna pod lektorem"})
        self.assertEqual(r.status_code, 200, r.text)
        _, items = self.state(pid)
        self.assertEqual(items["probka"]["state"], "brak")
        self.assertIn("za głośna", items["probka"]["summary"])
        r = self.client.post(f"/api/projects/{pid}/gotowosc/probka", headers=H,
                             json={"decision": "zatwierdzona", "quote": "„Zatwierdzam, wgraj”", "sample": "build/probka"})
        self.assertEqual(r.status_code, 200, r.text)
        log = r.json()["legacy"]["production_flow"]["log"]
        self.assertEqual([e["kind"] for e in log], ["próbka dźwięku", "próbka dźwięku"])
        self.assertEqual(log[-1]["decision"], "zatwierdzona")
        self.assertEqual(log[-1]["summary"], "Próbka dźwięku zatwierdzona: „Zatwierdzam, wgraj”")
        _, items = self.state(pid)
        self.assertEqual(items["probka"]["state"], "gotowe")
        self.assertIn("„Zatwierdzam, wgraj”", items["probka"]["summary"])

    def test_approval_written_in_upload_details_counts(self):
        log = [{"id": "e1", "at": "2026-11-24T17:55:00+01:00", "who": "studio_film.py", "kind": "wgranie",
                "summary": "Dźwięk wgrany: muzyka na cały film, efekty na cały film",
                "details": "Muzyka i efekty: synteza w numpy. Próbkę zatwierdził reżyser 19.11.2026 („Zatwierdzam, wgraj”)."}]
        _, items = self.state(self.make(log=log))
        self.assertEqual(items["probka"]["state"], "gotowe")
        self.assertEqual(items["probka"]["decision"]["quote"], "Zatwierdzam, wgraj")
        self.assertEqual(items["probka"]["decision"]["at"], "2026-11-19")

    def test_everything_ready(self):
        pid = self.make(narrated=(1, 3), music=(0, 210), effects=(0, 210))
        self.client.post(f"/api/projects/{pid}/gotowosc/probka", headers=H, json={"decision": "zatwierdzona", "quote": "Zatwierdzam"})
        _, items = self.state(pid)
        self.assertEqual(items["recenzje"]["state"], "brak")
        self.assertEqual(items["recenzje"]["units"][0]["review"], "brak")
        r = self.client.post(f"/api/projects/{pid}/flow/review/a1", headers=H, json={"status": "zatwierdzona", "reviewer": "reżyser"})
        self.assertEqual(r.status_code, 200, r.text)
        data, items = self.state(pid)
        self.assertEqual(items["recenzje"]["state"], "gotowe")
        self.assertEqual(items["ciaglosc"]["totals"]["3"], 0)
        self.assertTrue(data["ready"], data["blocking"])
        self.assertEqual(data["blocking"], [])
        self.assertIn("czeka na render końcowy reżysera", items["render"]["summary"])

    def test_commands_follow_film_script(self):
        script = Path(self.tmp.name) / "repo" / "output" / "test-film" / "studio_film.py"
        script.parent.mkdir(parents=True)
        script.write_text("def plan():\n    pass\n\n\ndef dzwiek(lektor=False):\n    pass\n", encoding="utf-8")
        data = readiness.readiness(film(), Path(self.tmp.name) / "repo")
        items = {i["key"]: i for i in data["items"]}
        self.assertEqual(items["lektor"]["command"], "python3 -I output/test-film/studio_film.py dzwiek lektor")
        self.assertNotIn("nie ma jeszcze polecenia", items["muzyka"]["todo"])
        script.write_text("def lektor():\n    pass\n", encoding="utf-8")
        items = {i["key"]: i for i in readiness.readiness(film(), Path(self.tmp.name) / "repo")["items"]}
        self.assertEqual(items["lektor"]["command"], "python3 -I output/test-film/studio_film.py lektor")
        self.assertIn("nie ma jeszcze polecenia „dzwiek”", items["muzyka"]["todo"])

    def test_continuity_errors_block(self):
        project = film()
        project.legacy["production_flow"]["world"] = {"threads": [{"title": "klucz", "payoff": ["d01_01"]}]}
        pid = self.app.state.store.create(project).id
        _, items = self.state(pid)
        self.assertEqual(items["ciaglosc"]["state"], "brak")
        self.assertGreater(items["ciaglosc"]["totals"]["3"], 0)
        self.assertTrue(items["ciaglosc"]["issues"])
        report = self.client.post(f"/api/projects/{pid}/continuity/check", headers=H).json()
        self.assertEqual(report["totals"]["3"], items["ciaglosc"]["totals"]["3"])


if __name__ == "__main__":
    unittest.main()
