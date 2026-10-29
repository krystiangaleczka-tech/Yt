import io
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from studio_api.app import create_app
from studio_core.models import Project, Scene, Beat, Fact, Clip, Keyframe, from_docos,import_content,fps
from studio_core.service import ProjectService
from studio_core.freshness import voice_hash,voice_state,sentence_hash
from studio_core.media import import_media,probe
from studio_core.exports import workbook,read_workbook,captions
from studio_core.voices import alignment_hash
from studio_core.templates import TEMPLATES,validate_parameters
from studio_core.bundles import export_bundle,import_bundle
from studio_timeline.operations import apply_operations
from studio_timeline.render import render,render_full
from studio_connectors.sources import Connectors

HEADERS={"X-Docos-Request":"1"}
REPO=Path(__file__).resolve().parents[1]


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.store=ProjectService(self.root); self.p=self.store.create(Project())
    def tearDown(self): self.temp.cleanup()
    def image(self,name="red",rgba=False):
        path=self.root/(name+".png"); Image.new("RGBA" if rgba else "RGB",(240,144),(255,0,0,128) if rgba else name).save(path)
        return import_media(self.store,self.p.id,path,path.name,{"license":"CC0"})[0]
    def audio(self,metadata=None):
        path=self.root/"tone.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","sine=frequency=440:duration=3",str(path)],check=True)
        return import_media(self.store,self.p.id,path,path.name,metadata)[0]
    def project(self): return self.store.get(self.p.id)

    def test_real_bloop_preserves_beats_templates_facts_and_unknown_fields(self):
        raw=json.loads((REPO/"projekty/bloop_v3/bloop_v4.json").read_text()); raw["future_setting"]={"keep":True}
        p=from_docos(raw)
        self.assertEqual((len(p.beats),len(p.scenes),len(p.facts)),(12,53,22))
        self.assertEqual(sum(len(s.fact_ids) for s in p.scenes),139)
        self.assertTrue(all(s.beat_id for s in p.scenes)); self.assertTrue(p.legacy["future_setting"]["keep"])
        self.assertIn("spectrogram",{s.template for s in p.scenes})

    def test_text_language_profile_and_pronunciation_invalidate_voice(self):
        p=self.store.patch(self.p.id,1,{"scenes":[Scene(narration="NOAA bada ocean.").model_dump()]})
        scene=p.scenes[0]; voice=self.audio({"provenance":{"voice_hash":voice_hash(p,scene),"kind":"voice"}})
        p=self.project(); p=self.store.patch(p.id,p.revision,{"scenes":[scene.model_dump()|{"voice_asset_id":voice.id}]})
        self.assertEqual(voice_state(p,p.scenes[0]),"current")
        for change in ({"language":"en"},{"voice_profile":{"temperature":.9}},{"pronunciation":{"NOAA":"Noa"}},{"scenes":[p.scenes[0].model_dump()|{"narration":"Inna narracja."}]}):
            draft=p.model_copy(deep=True)
            for k,v in change.items(): setattr(draft,k,v if k!="scenes" else [Scene.model_validate(x) for x in v])
            self.assertEqual(voice_state(draft,draft.scenes[0]),"stale")

    def test_scene_lock_protects_timeline_against_manual_and_ai(self):
        scene=Scene(locked=True); p=Project(scenes=[scene]); clip=Clip(track_id="v1",scene_id=scene.id,template="title",parameters={"text":"Test"});p.sequence.clips=[clip]
        for origin in ("manual","ai"):
            with self.assertRaisesRegex(ValueError,"zablokowane"):
                apply_operations(p,[{"type":"move_clip","clip_id":clip.id,"changes":{"start":30}}],origin)
            self.assertEqual(p.sequence.clips[0].start,0)

    def test_group_move_is_atomic_and_blocked_member_prevents_all_changes(self):
        clips=[Clip(track_id="t1",duration=30,text="A"),Clip(track_id="t1",start=40,duration=30,text="B")];p=Project();p.sequence.clips=clips
        apply_operations(p,[{"type":"group_clips","clip_ids":[c.id for c in clips]}])
        apply_operations(p,[{"type":"move_clip","clip_id":clips[0].id,"changes":{"start":15}}])
        self.assertEqual([c.start for c in p.sequence.clips],[15,55])
        p.sequence.clips[1].locked=True; before=p.model_dump()
        with self.assertRaises(ValueError): apply_operations(p,[{"type":"move_clip","clip_id":clips[0].id,"changes":{"start":20}}])
        self.assertEqual(p.model_dump(),before)

    def test_split_keeps_interpolated_keyframes_and_source_time(self):
        p=Project();clip=Clip(track_id="t1",duration=60,text="A",source_in=4,speed=1.5,keyframes=[Keyframe(property="x",frame=0,value=-1),Keyframe(property="x",frame=60,value=1)])
        p.sequence.clips=[clip]; apply_operations(p,[{"type":"split_clip","clip_id":clip.id,"frame":30}])
        left,right=p.sequence.clips
        self.assertEqual((left.keyframes[-1].value,right.keyframes[0].value),(0,0));self.assertEqual(right.source_in,49)

    def test_xlsx_edits_round_trip_without_losing_assets_or_timing(self):
        from openpyxl import load_workbook
        asset=self.image();p=self.project();p.facts=[Fact(claim="=2+2",source="Dowód")];p.scenes=[Scene(title="Original",asset_id=asset.id,duration=40)];p.sequence.clips=[Clip(track_id="v1",asset_id=asset.id,duration=40)]
        raw=workbook(p); restored=read_workbook(raw)
        self.assertEqual(restored.model_dump(),p.model_dump())
        book=load_workbook(io.BytesIO(raw));self.assertEqual(book["Fakty"]["B2"].data_type,"s")
        book["Ujęcia"]["B2"]="Edited";target=io.BytesIO();book.save(target)
        restored=read_workbook(target.getvalue());self.assertEqual(restored.scenes[0].title,"Edited");self.assertEqual(restored.assets,p.assets)

    def test_subtitles_follow_trim_speed_and_reject_stale_voice(self):
        scene=Scene(narration="Hello ocean.");p=self.project();p.scenes=[scene]
        asset=self.audio({"provenance":{"voice_hash":voice_hash(p,scene),"kind":"voice"}});p.assets=self.project().assets
        scene.voice_asset_id=asset.id;scene.voice_input_hash=voice_hash(p,scene);scene.words=[{"word":"Hello","start":.2,"end":.7},{"word":"ocean.","start":1,"end":1.5}];scene.alignment_hash=alignment_hash(p,scene)
        p.sequence.clips=[Clip(track_id="a1",asset_id=asset.id,scene_id=scene.id,start=30,source_in=15,duration=30,speed=2)]
        result=captions(p,"srt");self.assertIn("00:00:01,000 --> 00:00:01,500",result);self.assertIn("Hello ocean.",result)
        p.language="en"
        with self.assertRaisesRegex(ValueError,"odśwież"): captions(p,"srt")

    def test_private_media_is_omitted_with_explicit_bundle_manifest(self):
        asset=self.image();p=self.project();p.assets[0].private=True
        path=export_bundle(self.store,p)
        import zipfile
        with zipfile.ZipFile(path) as archive:
            manifest=json.loads(archive.read("manifest.json"));self.assertEqual(manifest["omitted"][0]["reason"],"private");self.assertNotIn("media/"+asset.filename,archive.namelist())
        restored=import_bundle(self.store,path);self.assertFalse((self.store.folder(restored.id)/"media"/asset.filename).exists())

    def test_all_templates_render_real_media_into_one_movie(self):
        red=self.image();blue=self.image("blue");cutout=self.image("cutout",True);audio=self.audio()
        p=self.project();p.sequence.width=240;p.sequence.height=144
        values={"text":"Ocean evidence","question":"Why?","answer":"Measured data.","author":"Author","events":[{"date":"1997","text":"Recording"}],"points":[{"lon":10,"lat":20,"label":"Sensor"}],"routes":[[0,0],[10,20]],"nodes":[{"id":"a","text":"A","x":.3,"y":.5},{"id":"b","text":"B","x":.7,"y":.5}],"edges":[["a","b"]],"items":["Evidence","Question"]}
        for index,template in enumerate(TEMPLATES):
            name=template["id"];params={f["key"]:values.get(f["key"],f["default"]) for f in template["fields"]}
            asset=audio.id if name in ("waveform","spectrogram") else red.id
            layers=[red.id,cutout.id] if name in ("parallax","paper-theatre") else [red.id,blue.id]
            p.sequence.clips.append(Clip(track_id="v1",start=index*3,duration=3,template=name,parameters=params,asset_id=asset,asset_ids=layers if name in ("split","comparison","stack","parallax","paper-theatre") else []))
        output=self.root/"catalog.mp4";render(self.store,p,output,lambda *_:None,threading.Event())
        self.assertAlmostEqual(float(probe(output)["format"]["duration"]),len(TEMPLATES)*3/fps(p),places=1)
        self.assertIn("paper-theatre",{template["id"] for template in TEMPLATES})

    def test_range_cache_reuses_only_unchanged_ranges(self):
        p=self.project();p.sequence.width=240;p.sequence.height=144;p.sequence.clips=[Clip(track_id="v1",duration=150,template="title",parameters={"text":"First"}),Clip(track_id="v1",start=150,duration=30,template="title",parameters={"text":"Second"})]
        output=self.root/"range.mp4";render(self.store,p,output,lambda *_:None,threading.Event())
        p.sequence.clips[1].parameters["text"]="Changed";render(self.store,p,output,lambda *_:None,threading.Event())
        stats=json.loads(output.with_suffix(".cache.json").read_text());self.assertEqual(stats["reused"],1)

    def test_json_keeps_edit_decisions_without_granting_old_file_access(self):
        asset=self.image();p=self.project();p.scenes=[Scene(asset_id=asset.id)];p.sequence.clips=[Clip(track_id="v1",scene_id=p.scenes[0].id,asset_id=asset.id,start=7,duration=60,source_in=0)]
        imported=import_content(p.model_dump());restored=self.store.create(imported)
        self.assertEqual(restored.sequence,p.sequence);self.assertEqual(restored.assets[0].model_dump(exclude={"thumbnail"}),p.assets[0].model_dump(exclude={"thumbnail"}));self.assertEqual(restored.assets[0].thumbnail,"")
        self.assertFalse((self.store.folder(restored.id)/"media"/asset.filename).exists())

    def test_version_one_migrates_without_discarding_editable_content(self):
        raw=self.p.model_dump();raw["schema_version"]="docos-studio/1";raw["legacy"]={"future_field":"preserved"}
        migrated=Project.model_validate(raw)
        self.assertEqual(migrated.schema_version,"docos-studio/2");self.assertEqual(migrated.legacy,raw["legacy"])

    def test_old_inline_undo_upgrades_to_durable_snapshot_references(self):
        from studio_core.store import atomic_json
        doc=self.store.read_document(self.p.id);old=self.p.model_dump();old["title"]="Stary tytuł";doc["_undo"]=[old];atomic_json(self.store.folder(self.p.id)/"project.json",doc)
        p=self.store.patch(self.p.id,1,{"title":"Nowy tytuł"});doc=self.store.read_document(p.id)
        self.assertTrue(all(isinstance(value,str) for value in doc["_undo"]))
        reopened=ProjectService(self.root);p=reopened.restore(p.id,p.revision,"undo");p=reopened.restore(p.id,p.revision,"undo")
        self.assertEqual(p.title,"Stary tytuł");self.assertEqual(reopened.history(p.id)["redo"],2)

    def test_bundle_keeps_ab_version_and_its_original_media(self):
        a=self.image();b=self.image("blue");p=self.project();p.sequence.width=240;p.sequence.height=144
        p=self.store.edit(p.id,p.revision,[{"type":"add_clip","clip":Clip(track_id="v1",asset_id=a.id,duration=3).model_dump()}]);version=self.store.save_version(p.id,"A")
        def change(project):project.assets=[b];project.sequence.clips=[Clip(track_id="v1",asset_id=b.id,duration=3)]
        p=self.store.mutate(p.id,p.revision,change)
        snapshot=Project.model_validate(self.store.version(p.id,version["id"])["project"])
        render(self.store,snapshot,self.root/"version.mp4",lambda *_:None,threading.Event())
        restored=import_bundle(self.store,export_bundle(self.store,p));saved=self.store.version(restored.id,version["id"])
        self.assertEqual(saved["project"]["id"],restored.id);self.assertEqual(saved["project"]["story"]["status"],"DRAFT")
        self.assertTrue((self.store.folder(restored.id)/"media"/a.filename).is_file())

    def test_evidence_edit_revokes_verification_and_marks_narration_for_review(self):
        from studio_core.freshness import evidence_hash
        fact=Fact(claim="Original evidence",status="VERIFIED",source="Book")
        scene=Scene(narration="Original evidence",fact_ids=[fact.id])
        p=self.store.patch(self.p.id,1,{"facts":[fact.model_dump()],"scenes":[scene.model_dump()]})
        original_hash=p.scenes[0].script_input_hash
        p=self.store.patch(p.id,p.revision,{"facts":[p.facts[0].model_dump()|{"claim":"Revised evidence"}]})
        self.assertEqual(p.facts[0].status,"UNVERIFIED");self.assertEqual(p.scenes[0].script_input_hash,original_hash)
        self.assertNotEqual(original_hash,evidence_hash(p,p.scenes[0]))

    def test_fractional_fps_preserves_seconds_and_renders_its_timebase(self):
        p=self.project();p.sequence.width=240;p.sequence.height=144;p.scenes=[Scene(start=30,duration=60)];p.sequence.clips=[Clip(track_id="t1",scene_id=p.scenes[0].id,start=30,duration=60,text="Timing",keyframes=[Keyframe(property="opacity",frame=60,value=1)])]
        apply_operations(p,[{"type":"set_sequence","changes":{"fps_num":30000,"fps_den":1001}}])
        self.assertAlmostEqual(p.sequence.clips[0].start/(30000/1001),1,delta=.034)
        movie=self.root/"ntsc.mp4";render(self.store,p,movie,lambda *_:None,threading.Event())
        video=next(s for s in probe(movie)["streams"] if s["codec_type"]=="video")
        n,d=map(int,video["avg_frame_rate"].split("/"));self.assertAlmostEqual(n/d,30000/1001,places=4)

    def test_transitions_render_and_preserve_previous_picture_during_dissolve(self):
        red=self.image();blue=self.image("blue");p=self.project();p.sequence.width=240;p.sequence.height=144
        transitions=["cut","dissolve","fade-black","wipe-left","wipe-right","slide-left","slide-right","zoom"]
        p.sequence.clips=[Clip(track_id="v1",asset_id=red.id if i%2==0 else blue.id,start=i*15,duration=15,transition=t,transition_duration=9 if t!="cut" else 0) for i,t in enumerate(transitions)]
        movie=self.root/"transitions.mp4";render(self.store,p,movie,lambda *_:None,threading.Event())
        raw=subprocess.run(["ffmpeg","-v","error","-ss","0.65","-i",str(movie),"-frames:v","1","-f","image2pipe","-vcodec","png","pipe:1"],capture_output=True,check=True).stdout
        with Image.open(io.BytesIO(raw)) as image:
            r,g,b=image.getpixel((120,72));self.assertGreater(r,40);self.assertGreater(b,40)

    def test_tampered_original_cannot_be_hidden_by_a_cached_render(self):
        asset=self.image();p=self.project();p.sequence.width=240;p.sequence.height=144;p.sequence.clips=[Clip(track_id="v1",asset_id=asset.id,duration=3)]
        movie=self.root/"tamper.mp4";render(self.store,p,movie,lambda *_:None,threading.Event())
        Image.new("RGB",(240,144),"blue").save(self.store.folder(p.id)/"media"/asset.filename)
        with self.assertRaisesRegex(ValueError,"zmienił treść"):render(self.store,p,movie,lambda *_:None,threading.Event())


class ProductionAPITests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.app=create_app(Path(self.temp.name),seed_demo=False);self.client=TestClient(self.app)
        self.p=self.client.post("/api/projects",json={"title":"Test"},headers=HEADERS).json();self.base="/api/projects/"+self.p["id"]
    def tearDown(self): self.app.state.jobs.close();self.client.close();self.temp.cleanup()
    def test_writer_rejects_previous_input_revision(self):
        prompt=self.client.post(self.base+"/writer/topics/prompt",json={},headers=HEADERS).json()
        self.client.patch(self.base,json={"expected_revision":1,"changes":{"title":"Changed"}},headers=HEADERS)
        response=self.client.post(self.base+"/writer/topics/import",json={"base_revision":prompt["base_revision"],"response":"[]"},headers=HEADERS)
        self.assertEqual(response.status_code,409)
    def test_quotes_retain_source_and_page_and_reject_invented_text(self):
        source=self.client.post(self.base+"/media",files={"file":("source.txt",b"Ocean evidence from a real document.")},headers=HEADERS).json()["source"]
        p=self.app.state.store.get(self.p["id"])
        bad=self.client.post(self.base+f"/sources/{source['id']}/quote",json={"expected_revision":p.revision,"quote":"Invented quote","page":"1"},headers=HEADERS);self.assertEqual(bad.status_code,422)
        good=self.client.post(self.base+f"/sources/{source['id']}/quote",json={"expected_revision":p.revision,"quote":"Ocean evidence","page":"1"},headers=HEADERS)
        self.assertEqual(good.status_code,200,good.text);self.assertEqual(good.json()["facts"][0]["source_id"],source["id"])
    def test_concrete_book_edition_and_access_level_contract(self):
        payload={"entries":[{"key":"/books/OL1M","title":"Ocean","publish_date":"1997","publishers":["NOAA"],"isbn_13":["123"]}]}
        with patch.object(self.app.state.connectors,"json",return_value=payload):
            result=self.client.get("/api/books/editions",params={"work":"/works/OL1W"})
        self.assertEqual(result.status_code,200);self.assertEqual(result.json()[0]["access"],"catalog");self.assertIn("NOAA",result.json()[0]["edition"])
    def test_custom_auth_is_private_and_page_substitution_reaches_provider(self):
        with patch("studio_connectors.sources.public_url",side_effect=lambda x:x):
            self.app.state.connectors.save({"custom":[{"id":"custom_test","name":"Archive","url":"https://example.org?q={query}&p={page}","kind":"image","headers":{"Authorization":"Bearer secret-value"},"results_path":"items","mapping":{"title":"title","url":"url"}}]})
        self.assertNotIn("secret-value",self.client.get("/api/settings").text)
        with patch.object(self.app.state.connectors,"json",return_value={"items":[{"title":"Ocean","url":"https://example.org/a"}]}) as fetch:
            self.app.state.connectors.search("custom_test","ocean","image",2)
            self.assertIn("p=2",fetch.call_args.args[0]);self.assertEqual(fetch.call_args.kwargs["headers"]["Authorization"],"Bearer secret-value")
    def test_multisearch_keeps_success_when_another_source_fails(self):
        def search(provider,*_):
            if provider=="broken": raise ValueError("upstream")
            return [{"id":"a","provider":provider,"title":"Ocean"}]
        with patch.object(self.app.state.connectors,"search",side_effect=search):
            response=self.client.post(self.base+"/search",json={"query":"ocean","providers":["commons","broken"]},headers=HEADERS).json()
            for _ in range(100):
                job=self.app.state.jobs.get(response["id"])
                if job["status"] in ("SUCCEEDED","FAILED"):break
                time.sleep(.01)
        self.assertEqual(job["status"],"SUCCEEDED");self.assertEqual(len(job["result"]["results"]),1);self.assertIn("broken",job["result"]["errors"])

    def test_template_poster_is_real_and_rejects_a_stale_revision(self):
        scene=Scene(template="counter",parameters={"from":0,"to":1997,"unit":"rok"})
        p=self.client.patch(self.base,json={"expected_revision":1,"changes":{"scenes":[scene.model_dump()]}},headers=HEADERS).json()
        path=self.base+f"/scenes/{scene.id}/poster"
        result=self.client.get(path,params={"revision":p["revision"],"frame":60})
        self.assertEqual(result.status_code,200,result.text[:100] if result.status_code!=200 else "")
        self.assertTrue(result.content.startswith(b"\x89PNG"))
        self.assertEqual(self.client.get(path,params={"revision":1}).status_code,409)

    def test_frame_retry_after_restart_uses_original_snapshot(self):
        scene=Scene(template="counter",parameters={"from":0,"to":1997})
        store=self.app.state.store
        p=store.patch(self.p["id"],1,{"scenes":[scene.model_dump()]})
        p=store.edit(p.id,p.revision,[{"type":"set_sequence","changes":{"width":320,"height":180}},{"type":"add_clip","clip":Clip(track_id="v1",scene_id=scene.id,template="counter",parameters=scene.parameters,duration=30).model_dump()}])
        with patch("studio_api.production.render",side_effect=ValueError("controlled interruption")):
            job=self.client.post(self.base+"/frame",json={"expected_revision":p.revision,"frame":5},headers=HEADERS).json()
            deadline=time.monotonic()+3
            while self.app.state.jobs.get(job["id"])["status"] not in ("FAILED","SUCCEEDED") and time.monotonic()<deadline:time.sleep(.01)
        self.assertEqual(self.app.state.jobs.get(job["id"])["status"],"FAILED")
        store.patch(p.id,p.revision,{"title":"New revision"})
        self.app.state.jobs.close();self.client.close()
        self.app=create_app(Path(self.temp.name),seed_demo=False);self.client=TestClient(self.app)
        response=self.client.post("/api/jobs/"+job["id"]+"/retry",json={},headers=HEADERS)
        self.assertEqual(response.status_code,200,response.text);retry=response.json()
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            state=self.app.state.jobs.get(retry["id"])
            if state["status"] in ("FAILED","SUCCEEDED"):break
            time.sleep(.02)
        self.assertEqual(state["status"],"SUCCEEDED",state)
        self.assertEqual(state["result"]["revision"],p.revision)
        self.assertTrue(self.client.get(state["result"]["url"]).content.startswith(b"\x89PNG"))

    def test_network_queue_is_independent_of_blocked_local_model(self):
        jobs=self.app.state.jobs;started=threading.Event();release=threading.Event();network=threading.Event()
        def heavy(*args):started.set();release.wait(3);return {}
        local_job=jobs.submit(self.p["id"],1,"voice",heavy,snapshot=self.p)
        try:
            self.assertTrue(started.wait(1))
            research_job=jobs.submit(self.p["id"],1,"search",lambda *_:network.set() or {},heavy=False)
            self.assertTrue(network.wait(1),"Research must not wait for a local model")
        finally:
            release.set()
            deadline=time.monotonic()+3
            while jobs.get(local_job["id"])["status"] not in ("SUCCEEDED","FAILED","CANCELLED") and time.monotonic()<deadline:time.sleep(.01)
            if network.is_set():
                while jobs.get(research_job["id"])["status"] not in ("SUCCEEDED","FAILED","CANCELLED") and time.monotonic()<deadline:time.sleep(.01)

    def test_api_budget_blocks_before_an_external_request(self):
        from studio_core.budget import reserve,spending
        store=self.app.state.store;project=store.patch(self.p["id"],1,{"budget":{"max_cost":.1,"max_jobs":2,"max_seconds":60}})
        with patch.object(self.app.state.connectors,"config",return_value={"ai_base_url":"https://example.org","ai_request_cost":.08}):
            reserve(store,project,self.app.state.connectors)
            with self.assertRaisesRegex(ValueError,"budżet"):reserve(store,project,self.app.state.connectors)
        self.assertAlmostEqual(spending(store,project.id)["estimated_cost"],.08)

    def test_scanned_pdf_ocr_preserves_original_and_extracts_illustration(self):
        from PIL import ImageDraw,ImageFont
        image=Image.new("RGB",(1000,500),"white");draw=ImageDraw.Draw(image);draw.text((50,180),"Source evidence 1997",font=ImageFont.truetype(str(REPO/"pilot/fonts/Montserrat.ttf"),48),fill="black")
        output=io.BytesIO();image.save(output,"PDF")
        source=self.client.post(self.base+"/media",files={"file":("scan.pdf",output.getvalue())},headers=HEADERS).json()["source"]
        job=self.client.post(self.base+f"/sources/{source['id']}/ocr",json={"pages":["1"]},headers=HEADERS).json()
        for _ in range(300):
            state=self.app.state.jobs.get(job["id"])
            if state["status"] in ("SUCCEEDED","FAILED"):break
            time.sleep(.02)
        self.assertEqual(state["status"],"SUCCEEDED",state)
        p=self.client.get(self.base).json();document=next(s for s in p["sources"] if s["id"]==source["id"])
        self.assertIn("1997",document["pages"][0]["text"]);self.assertEqual(document["original_asset_id"],source["asset_id"])
        crop=self.client.post(self.base+f"/sources/{source['id']}/illustration",json={"page":1,"crop":{"x":0,"y":0,"width":1,"height":1}},headers=HEADERS)
        self.assertEqual(crop.status_code,200,crop.text);self.assertEqual(crop.json()["asset"]["provenance"]["page"],"1")

    def test_epub_illustration_keeps_chapter_provenance(self):
        from ebooklib import epub
        book=epub.EpubBook();book.set_identifier("qa");book.set_title("Book");book.set_language("en")
        image=io.BytesIO();Image.new("RGB",(80,50),"red").save(image,"PNG")
        book.add_item(epub.EpubItem(uid="photo",file_name="images/ocean.png",media_type="image/png",content=image.getvalue()))
        chapter=epub.EpubHtml(title="Ocean",file_name="chapter.xhtml",lang="en");chapter.content='<h1>Ocean</h1><img src="images/ocean.png"/>';book.add_item(chapter);book.spine=[chapter];book.add_item(epub.EpubNcx());book.add_item(epub.EpubNav())
        with tempfile.NamedTemporaryFile(suffix=".epub") as file:
            epub.write_epub(file.name,book);content=Path(file.name).read_bytes()
        source=self.client.post(self.base+"/media",files={"file":("book.epub",content)},headers=HEADERS).json()["source"]
        images=self.client.get(self.base+f"/sources/{source['id']}/images").json();self.assertIn("chapter.xhtml",images[0]["chapters"])
        result=self.client.post(self.base+f"/sources/{source['id']}/illustration",json={"page":"chapter.xhtml","image_index":0},headers=HEADERS)
        self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()["asset"]["provenance"]["page"],"chapter.xhtml")


if __name__=="__main__":unittest.main()
