import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from studio_api.app import create_app
from studio_core.models import Project, Beat, Fact
from studio_core.development import ChannelBaseline, StoryOption, FilmIdea, Chapter, Subchapter, forecast
from studio_core.bundles import export_bundle, import_bundle
from studio_core.exports import workbook, read_workbook

H={"X-Docos-Request":"1"}


class DevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.app=create_app(Path(self.temp.name),seed_demo=False);self.store=self.app.state.store;self.client=TestClient(self.app)
        self.story=StoryOption(title="Śledztwo",synopsis="Od pytania do sprawdzonej odpowiedzi",hook="Co naprawdę słychać?",central_question="Skąd pochodzi sygnał?",payoff="Pokazujemy wynik analizy",chapters=[Chapter(title="Pytanie",sections=[Subchapter(title="Ślad",seconds=90,retention_plan="Najpierw dźwięk, potem kontekst",evidence_needed="Oryginalne nagranie")]),Chapter(title="Odpowiedź",sections=[Subchapter(title="Weryfikacja",seconds=120)])])
        self.idea=FilmIdea(title="Tajemnica sygnału",question="Skąd pochodzi dźwięk?",stories=[self.story]);self.p=self.store.create(Project(title="Nowy dokument",development={"ideas":[self.idea.model_dump()]}));self.base="/api/projects/"+self.p.id
    def tearDown(self):self.app.state.jobs.close();self.client.close();self.temp.cleanup()
    def post(self,path,body=None):return self.client.post(self.base+path,json=body or {},headers=H)
    def current(self):return self.store.get(self.p.id)
    def select(self):
        r=self.post("/development/select",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":self.story.id});self.assertEqual(r.status_code,200,r.text);return r.json()

    def test_legacy_topics_get_stable_cards_and_keep_original_fields(self):
        raw=Project(title="Film").model_dump();raw.pop("development");raw["topics"]=[{"title":"Film","central_question":"Pytanie?","subject":"Nauka","custom":"keep"}]
        first=Project.model_validate(raw);second=Project.model_validate(raw)
        self.assertEqual(first.development.ideas[0].id,second.development.ideas[0].id);self.assertEqual(first.topics[0]["custom"],"keep")
        self.assertEqual(first.development.selected_idea_id,first.development.ideas[0].id)

    def test_select_keeps_alternatives_and_requires_story_reapproval(self):
        before=self.current();p=self.select()
        self.assertEqual(p["title"],self.idea.title);self.assertEqual(p["story"]["hook"],self.story.hook);self.assertEqual(p["story"]["status"],"DRAFT")
        self.assertEqual(len(p["development"]["ideas"][0]["stories"]),1)
        restored=self.store.restore(self.p.id,p["revision"],"undo");self.assertEqual(restored.title,before.title);self.assertEqual(restored.development.selected_story_id,None)

    def test_chapter_handoff_preserves_existing_script_order_and_is_idempotent(self):
        p=self.current();p=self.store.patch(p.id,p.revision,{"beats":[Beat(title="Ręczny tekst",narration="Zachowaj").model_dump()]});self.select()
        for _ in range(2):
            p=self.current();r=self.post("/development/to-script",{"expected_revision":p.revision,"idea_id":self.idea.id,"story_id":self.story.id});self.assertEqual(r.status_code,200,r.text)
        p=self.current();self.assertEqual([b.title for b in p.beats],["Ręczny tekst","Ślad","Weryfikacja"])
        self.assertEqual(p.beats[0].narration,"Zachowaj");self.assertEqual(p.beats[1].planning_seconds,90);self.assertTrue(p.beats[1].retention_plan)
        self.assertEqual([b.chapter for b in p.beats[1:]],["Pytanie","Odpowiedź"])
        self.assertEqual([b.planning_chapter_id for b in p.beats[1:]],[c.id for c in self.story.chapters])

    def test_edited_selected_story_must_be_applied_before_script_handoff(self):
        self.select();p=self.current();dev=p.development.model_dump();dev["ideas"][0]["stories"][0]["hook"]="Inne otwarcie";self.store.patch(p.id,p.revision,{"development":dev})
        f=self.client.get(self.base+"/development/forecasts").json();self.assertFalse(f[self.story.id]["selected_current"])
        r=self.post("/development/to-script",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":self.story.id});self.assertEqual(r.status_code,422)

    def test_publication_title_is_applied_and_later_edits_require_reselection(self):
        p=self.current();dev=p.development.model_dump();dev["ideas"][0]["stories"][0]["title_pitch"]="Co naprawdę kryje ten sygnał?";self.store.patch(p.id,p.revision,{"development":dev})
        self.assertEqual(self.select()["title"],"Co naprawdę kryje ten sygnał?")
        p=self.current();dev=p.development.model_dump();dev["ideas"][0]["stories"][0]["title_pitch"]="Nowa obietnica";self.store.patch(p.id,p.revision,{"development":dev})
        self.assertFalse(self.client.get(self.base+"/development/forecasts").json()[self.story.id]["selected_current"])
        self.assertEqual(self.current().title,"Co naprawdę kryje ten sygnał?")

    def test_invalid_selection_duplicate_ids_and_unknown_evidence_are_rejected(self):
        r=self.post("/development/select",{"expected_revision":1,"idea_id":self.idea.id,"story_id":"outline_"+"0"*16});self.assertEqual(r.status_code,422)
        raw=self.current().model_dump();raw["development"]["ideas"].append(self.idea.model_dump())
        with self.assertRaises(ValueError):Project.model_validate(raw)
        raw=self.current().model_dump();raw["development"]["ideas"][0]["stories"][0]["chapters"][0]["sections"][0]["fact_ids"]=["invented"]
        with self.assertRaises(ValueError):Project.model_validate(raw)

    def test_another_outline_replaces_only_an_empty_plan(self):
        self.select();self.post("/development/to-script",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":self.story.id})
        p=self.current();other=StoryOption(title="Inna konstrukcja",chapters=[Chapter(title="Nowy plan",sections=[Subchapter(title="Nowy początek")])]);dev=p.development.model_dump();dev["ideas"][0]["stories"].append(other.model_dump());self.store.patch(p.id,p.revision,{"development":dev})
        def choose_other():return self.post("/development/select",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":other.id})
        choose_other();r=self.post("/development/to-script",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":other.id});self.assertEqual(r.status_code,200,r.text)
        self.assertEqual([b.title for b in self.current().beats],["Nowy początek"])
        p=self.current();self.store.mutate(p.id,p.revision,lambda p:setattr(p.beats[0],"narration","Ręcznie napisany tekst"))
        self.select();r=self.post("/development/to-script",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":self.story.id});self.assertEqual(r.status_code,422,r.text)
        self.assertEqual(self.current().beats[0].narration,"Ręcznie napisany tekst")

    def test_ai_import_appends_fresh_variants_and_rejects_old_revision(self):
        path="/development/ai/stories/";body={"idea_id":self.idea.id};prompt=self.post(path+"prompt",body).json()
        response=json.dumps([self.story.model_dump()])
        r=self.post(path+"import",body|{"base_revision":prompt["base_revision"],"response":response});self.assertEqual(r.status_code,200,r.text)
        stories=r.json()["development"]["ideas"][0]["stories"];self.assertEqual(len(stories),2);self.assertNotEqual(stories[0]["id"],stories[1]["id"])
        self.assertNotEqual(stories[0]["chapters"][0]["sections"][0]["id"],stories[1]["chapters"][0]["sections"][0]["id"])
        self.assertEqual(self.post(path+"import",body|{"base_revision":prompt["base_revision"],"response":response}).status_code,409)

    def test_ai_review_cannot_invent_absolute_analytics_and_uses_budget_context(self):
        body={"idea_id":self.idea.id,"story_id":self.story.id};path="/development/ai/review/"
        bad=self.post(path+"import",body|{"base_revision":1,"response":json.dumps({"views_30d":1000000})});self.assertEqual(bad.status_code,422)
        with patch("studio_api.development.complete",return_value='{"rationale":"Hipoteza"}') as model:
            r=self.post(path+"generate",body);self.assertEqual(r.status_code,200)
            self.assertIs(model.call_args.kwargs["store"],self.store);self.assertEqual(model.call_args.kwargs["project"].id,self.p.id)
        self.assertEqual(self.current().development.ideas[0].stories[0].rationale,"")

    def test_partial_ai_review_preserves_manual_scores_and_reach_assumptions(self):
        p=self.current();dev=p.development.model_dump();variant=dev["ideas"][0]["stories"][0];variant["scores"]["originality"]=82;variant["assumptions"]["reach_high"]=3;self.store.patch(p.id,p.revision,{"development":dev})
        r=self.post("/development/ai/review/import",{"idea_id":self.idea.id,"story_id":self.story.id,"base_revision":self.current().revision,"response":json.dumps({"scores":{"hook":75},"assumptions":{"ctr_delta":1}})})
        self.assertEqual(r.status_code,200,r.text);variant=self.current().development.ideas[0].stories[0]
        self.assertEqual(variant.scores.hook,75);self.assertEqual(variant.scores.originality,82);self.assertEqual(variant.assumptions.reach_high,3);self.assertEqual(variant.assumptions.ctr_delta,1)

    def test_planned_sections_flow_into_an_approved_script_and_workbook(self):
        self.select();r=self.post("/development/to-script",{"expected_revision":self.current().revision,"idea_id":self.idea.id,"story_id":self.story.id});self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(self.post("/writer/script/prompt").status_code,422)
        p=self.current();fact=Fact(claim="Kontrolowane twierdzenie testowe",source="Źródło testowe",url="https://example.org/record",status="VERIFIED");p=self.store.patch(p.id,p.revision,{"facts":[fact.model_dump()]})
        r=self.post("/story/approve",{"expected_revision":p.revision});self.assertEqual(r.status_code,200,r.text)
        prompt=self.post("/writer/script/prompt").json();beats=self.current().beats
        self.assertTrue(all(beat.id in prompt["prompt"] for beat in beats))
        response=[{"title":beat.title,"narration":"Kontrolowane twierdzenie testowe", "seconds":6,"fact_ids":[fact.id],"beat_id":beat.id} for beat in beats]
        r=self.post("/writer/script/import",{"base_revision":prompt["base_revision"],"response":json.dumps(response)});self.assertEqual(r.status_code,200,r.text)
        p=self.current();self.assertEqual([scene.beat_id for scene in p.scenes],[beat.id for beat in beats]);self.assertTrue(all(scene.fact_ids==[fact.id] for scene in p.scenes))
        restored=read_workbook(workbook(p));self.assertEqual(restored.development,p.development);self.assertEqual(restored.beats,p.beats)

    def test_bundle_and_saved_version_keep_full_development_tree(self):
        self.select();p=self.current();version=self.store.save_version(p.id,"Plan")
        restored=import_bundle(self.store,export_bundle(self.store,p));self.assertEqual(restored.development,p.development)
        dev=p.development.model_dump();dev["topic_area"]="Changed";p=self.store.patch(p.id,p.revision,{"development":dev})
        p=self.store.restore_version(p.id,p.revision,version["id"]);self.assertEqual(p.development.topic_area,"")


class ForecastTests(unittest.TestCase):
    def test_missing_or_zero_baseline_never_fabricates_views_or_probability(self):
        for baseline in (ChannelBaseline(),ChannelBaseline(typical_views_30d=0)):
            result=forecast(baseline,StoryOption());self.assertIsNone(result["views_30d"]);self.assertIsNone(result["probabilities"]);self.assertIsNone(result["ctr"])

    def test_bands_are_explicit_scenarios_and_probabilities_need_ten_outcomes(self):
        baseline=ChannelBaseline(views_30d=[1000,2000,3000],ctr=5,retention=40)
        result=forecast(baseline,StoryOption());self.assertEqual(result["views_30d"],{"low":1000,"base":2000,"high":4000});self.assertIsNone(result["probabilities"])
        self.assertEqual(result["ctr"],{"low":3,"base":5,"high":7});self.assertEqual(result["retention"]["base"],40)

    def test_conditional_probabilities_are_ordered_and_respond_to_assumptions(self):
        baseline=ChannelBaseline(views_30d=[500,700,800,900,1000,1000,1100,1300,1500,2000])
        neutral=forecast(baseline,StoryOption());better=forecast(baseline,StoryOption(assumptions={"reach_low":1,"reach_base":2,"reach_high":3}))
        self.assertLess(neutral["probabilities"]["viral"],neutral["probabilities"]["success"])
        self.assertGreater(better["probabilities"]["success"],neutral["probabilities"]["success"])
        self.assertEqual(neutral["confidence"],"scenario_only")
        with self.assertRaises(ValueError):ChannelBaseline(success_multiple=5,viral_multiple=2)
        with self.assertRaises(ValueError):StoryOption(assumptions={"reach_low":3,"reach_base":1})


if __name__=="__main__":unittest.main()
