"""Regresje CLI i kontraktu Story Lock; fikcyjne dane służą wyłącznie testom walidacji."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import docos
import editorial


def candidate_batch():
    return [
        {"title": f"How Test System {i} Works", "subject": f"Test subject {i}",
         "central_question": f"How does test system {i} work?",
         "layers": ["Origins", "Mechanism", "Consequences"], "research_leads": ["Test archive"]}
        for i in range(10)
    ]


def draft_project():
    project = docos.new_project("Test Documentary")
    editorial.attach_channel(project, editorial.new_channel("Test Channel"))
    project["facts"] = [
        {"id": f"F{i}", "claim": f"Test fixture {i}", "status": "VERIFIED", "source": "Test fixture",
         "url": f"https://example.org/fixture/{i}", "note": "Synthetic validator fixture, not research."}
        for i in range(1, 6)
    ]
    project["story_lock"].update({key: f"Test {key}" for key in editorial.STORY_FIELDS})
    project["story_lock"].update(fact_ids=[f"F{i}" for i in range(1, 6)],
                                 evidence_chain=[f"F{i}" for i in range(1, 6)])
    project["beats"] = [{"id": "B01", "facts": ["F1"], "seconds": 30, "segment": "INVESTIGATION",
                          "dynamic": "STORY", "goal": "Explain", "turn": "confusion → clarity"}]
    return project


class TopicsTests(unittest.TestCase):
    def test_prompt_carries_focus_language_and_both_title_registries(self):
        channel = editorial.new_channel("Channel")
        channel.update(focus="Oceans", language="Polski", published_titles=["Published"],
                       suggested_titles=["Suggested"])
        prompt = editorial.topics_prompt(channel)
        for expected in ("Oceans", "Polski", "Published", "Suggested", "DOCUMENTARY", "research_leads"):
            self.assertIn(expected, prompt)

    def test_saved_topics_are_excluded_without_marking_them_published(self):
        channel = editorial.new_channel("Channel")
        updated = editorial.save_topics(channel, candidate_batch())
        self.assertEqual(channel["suggested_titles"], [])
        self.assertEqual(updated["published_titles"], [])
        self.assertEqual(len(updated["topic_candidates"]), 10)
        self.assertIn(candidate_batch()[0]["title"], editorial.topics_prompt(updated))
        with self.assertRaisesRegex(ValueError, "powtórzony"):
            editorial.save_topics(updated, candidate_batch())

    def test_normalized_duplicate_of_published_title_is_rejected(self):
        channel = editorial.new_channel("Channel")
        channel["published_titles"] = ["HOW TEST SYSTEM 0 WORKS!"]
        with self.assertRaisesRegex(ValueError, "powtórzony"):
            editorial.save_topics(channel, candidate_batch())

    def test_rejects_bad_batch_without_modifying_history(self):
        changes = [lambda batch: batch.pop(),
                   lambda batch: batch[0].update(title="X" * 61),
                   lambda batch: batch[1].update(title=batch[0]["title"]),
                   lambda batch: batch[1].update(subject=batch[0]["subject"]),
                   lambda batch: batch[0].update(layers=["One", "One", "One"]),
                   lambda batch: batch[0].update(research_leads=[])]
        for change in changes:
            with self.subTest(change=change):
                channel = editorial.new_channel("Channel")
                before = copy.deepcopy(channel)
                batch = candidate_batch()
                change(batch)
                with self.assertRaises(ValueError):
                    editorial.save_topics(channel, batch)
                self.assertEqual(channel, before)

    def test_unsupported_pack_and_invalid_tempo_are_rejected(self):
        for field, value in (("pack", "WHAT_IF"), ("wpm", 0), ("wpm", True)):
            with self.subTest(field=field, value=value):
                channel = editorial.new_channel("Channel")
                channel[field] = value
                with self.assertRaises(ValueError):
                    editorial.topics_prompt(channel)


class StoryTests(unittest.TestCase):
    def test_incomplete_card_blocks_narrative_prompts(self):
        project = docos.new_project("Draft")
        editorial.attach_channel(project, editorial.new_channel("Channel"))
        with self.assertRaisesRegex(ValueError, "szkicem"):
            docos.system_prompt(project)

    def test_lock_supplies_global_promise_to_each_beat(self):
        project = draft_project()
        editorial.lock_story(project)
        self.assertEqual(project["meta"]["thesis"], project["story_lock"]["thesis"])
        self.assertEqual(project["meta"]["curiosity_gap"], project["story_lock"]["central_question"])
        self.assertEqual(editorial.story_errors(project), [])
        for prompt in (docos.system_prompt(project), docos.beat_prompt(project, 0)):
            self.assertIn(project["story_lock"]["payoff"], prompt)
            self.assertIn(project["story_lock"]["central_question"], prompt)
            self.assertIn("DOCUMENTARY", prompt)

    def test_bank_rejects_unverified_facts_missing_sources_and_unexplained_disputes(self):
        changes = [lambda p: p["facts"][0].update(status="UNVERIFIED"),
                   lambda p: p["facts"][0].update(status="DRAMATIZATION"),
                   lambda p: p["facts"][0].update(url=""),
                   lambda p: p["facts"][0].update(source=""),
                   lambda p: p["facts"][0].update(status="DISPUTED", note=""),
                   lambda p: p["story_lock"].update(evidence_chain=["F1"] * 5),
                   lambda p: p["story_lock"].update(evidence_chain=["F1", "F2", "F3", "F4", "F99"])]
        for change in changes:
            with self.subTest(change=change):
                project = draft_project()
                change(project)
                before = copy.deepcopy(project)
                with self.assertRaises(ValueError):
                    editorial.lock_story(project)
                self.assertEqual(project, before)

    def test_disputed_fact_with_note_is_allowed(self):
        project = draft_project()
        project["facts"][0].update(status="DISPUTED", note="Test view A versus test view B.")
        editorial.lock_story(project)
        self.assertEqual(editorial.story_errors(project), [])

    def test_changes_to_locked_inputs_require_explicit_unlock(self):
        changes = [lambda p: p["meta"].update(title="Other title"),
                   lambda p: p["meta"].update(thesis="Other thesis"),
                   lambda p: p["meta"].update(wpm=150),
                   lambda p: p["channel"].update(focus="Other focus"),
                   lambda p: p["story_lock"].update(payoff="Other answer"),
                   lambda p: p["facts"][0].update(claim="Other claim"),
                   lambda p: p["facts"][0].update(url="https://example.org/other")]
        for change in changes:
            with self.subTest(change=change):
                project = draft_project()
                editorial.lock_story(project)
                change(project)
                with self.assertRaisesRegex(ValueError, "Zmieniono"):
                    editorial.lock_story(project)
                self.assertTrue(any(category == "STORY_LOCK" for category, _ in docos.check(project)))
                project["story_lock"]["status"] = "DRAFT"
                project["story_lock"].pop("digest")
                editorial.lock_story(project)
                self.assertEqual(editorial.story_errors(project), [])

    def test_new_unused_fact_does_not_invalidate_lock_but_using_it_does(self):
        project = draft_project()
        editorial.lock_story(project)
        project["facts"].append({**project["facts"][0], "id": "F6"})
        self.assertEqual(editorial.story_errors(project), [])
        project["beats"][0]["facts_used"] = ["F6"]
        with self.assertRaisesRegex(ValueError, "spoza"):
            editorial.ensure_locked(project)

    def test_global_prompt_only_exposes_locked_bank(self):
        project = draft_project()
        project["facts"].append({**project["facts"][0], "id": "F6", "claim": "Unused research lead"})
        editorial.lock_story(project)
        self.assertNotIn("Unused research lead", docos.system_prompt(project))

    def test_duplicate_registry_id_is_rejected(self):
        project = draft_project()
        project["facts"].append(copy.deepcopy(project["facts"][0]))
        with self.assertRaisesRegex(ValueError, "powtórzone ID"):
            editorial.lock_story(project)

    def test_malformed_card_does_not_bypass_story_guard(self):
        for value in (None, [], "LOCKED"):
            with self.subTest(value=value):
                project = draft_project()
                project["story_lock"] = value
                with self.assertRaisesRegex(ValueError, "obiektem"):
                    docos.system_prompt(project)

    def test_story_prompt_does_not_mutate_legacy_project(self):
        project = docos.new_project("Legacy")
        before = copy.deepcopy(project)
        self.assertIn("STORY LOCK", editorial.story_prompt(project))
        self.assertEqual(project, before)
        self.assertEqual(editorial.story_errors(project), [])
        self.assertIn("Legacy", docos.system_prompt(project))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(Path(docos.__file__)), *map(str, args)],
                              capture_output=True, text=True)

    def test_channel_topics_new_lock_unlock_and_write_guards(self):
        with tempfile.TemporaryDirectory() as folder:
            channel, batch, project = [Path(folder) / name for name in ("channel.json", "topics.json", "episode.json")]
            result = self.run_cli("channel", channel, "--name", "Test Channel")
            self.assertEqual(result.returncode, 0, result.stderr)
            original_channel = channel.read_text()
            self.assertNotEqual(self.run_cli("channel", channel, "--name", "Overwrite").returncode, 0)
            self.assertEqual(channel.read_text(), original_channel)
            batch.write_text(json.dumps(candidate_batch()))
            self.assertEqual(self.run_cli("save-topics", channel, batch).returncode, 0)
            self.assertIn("How Test System 0 Works", self.run_cli("topics", channel).stdout)
            result = self.run_cli("new", project, "Test Documentary", "--channel", channel)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(project.read_text())["story_lock"]["status"], "DRAFT")
            self.assertIn("STORY LOCK", self.run_cli("story", project).stdout)
            self.assertNotEqual(self.run_cli("lock", project).returncode, 0)
            self.assertNotEqual(self.run_cli("next", project).returncode, 0)
            project.write_text(json.dumps(draft_project()))
            result = self.run_cli("lock", project)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Test central_question", self.run_cli("next", project).stdout)
            self.assertEqual(self.run_cli("unlock", project).returncode, 0)
            self.assertNotEqual(self.run_cli("next", project).returncode, 0)
            self.assertEqual(self.run_cli("lock", project).returncode, 0)
            before = project.read_text()
            response = Path(folder) / "beat.md"
            response.write_text("Narracja:\nTest narration.\n\nFakty użyte: F6\nPołączenie do N-1: Test link.")
            rejected = self.run_cli("save", project, "B01", response)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("spoza", rejected.stderr)
            self.assertEqual(project.read_text(), before)
            response.write_text(response.read_text().replace("F6", "F1"))
            accepted = self.run_cli("save", project, "B01", response)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(json.loads(project.read_text())["beats"][0]["facts_used"], ["F1"])

    @unittest.skipUnless(importlib.util.find_spec("openpyxl"), "openpyxl required for export")
    def test_plan_export_is_allowed_but_unlocked_narration_export_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "project.json"
            project = draft_project()
            path.write_text(json.dumps(project))
            output = Path(folder) / "draft"
            result = self.run_cli("export", path, "--out", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "project.xlsx").is_file())
            editorial.lock_story(project)
            project["beats"][0]["narration"] = "Test narration."
            project["story_lock"]["status"] = "DRAFT"
            path.write_text(json.dumps(project))
            protected = Path(folder) / "protected"
            result = self.run_cli("export", path, "--out", protected)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(protected.exists())

    @unittest.skipUnless(importlib.util.find_spec("openpyxl"), "openpyxl required for export")
    def test_spreadsheet_round_trip_preserves_lock_with_optional_empty_notes(self):
        with tempfile.TemporaryDirectory() as folder:
            project = draft_project()
            del project["facts"][0]["note"]
            editorial.lock_story(project)
            path = Path(folder) / "project.xlsx"
            docos.export_xlsx(project, path)
            imported = docos.import_xlsx(copy.deepcopy(project), path)
            self.assertEqual(editorial.story_errors(imported), [])


if __name__ == "__main__":
    unittest.main()
