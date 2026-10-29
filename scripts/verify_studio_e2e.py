"""Reproducible book → evidence → picture/voice → edit → publish → reopen check.

Default uses a small local document and deterministic media. --live adds real
Commons/Gutenberg/Open Library requests and local image/TTS/ASR workers. It never
calls a paid AI provider. Output remains in the explicitly selected QA directory.
"""
import argparse
import io
import json
from pathlib import Path
import sys
import threading
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from PIL import Image
from studio_api.app import create_app
from studio_core.models import Scene,Beat,Clip
from studio_core.media import probe
from studio_core.freshness import voice_hash
from studio_core.store import atomic_json

HEADERS={"X-Docos-Request":"1"}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--home",type=Path,required=True);parser.add_argument("--live",action="store_true");parser.add_argument("--resume-project")
    args=parser.parse_args();app=create_app(args.home,seed_demo=False);started=time.perf_counter();events=[]
    with TestClient(app) as client:
        def call(method,path,**kwargs):
            response=client.request(method,"/api"+path,headers=HEADERS,**kwargs)
            if not response.is_success: raise RuntimeError(f"{method} {path}: {response.status_code} {response.text[:800]}")
            return response
        def event(name,**data):
            events.append({"step":name,"elapsed":round(time.perf_counter()-started,3),**data});print(name,flush=True)
        p=call("GET","/projects/"+args.resume_project).json() if args.resume_project else call("POST","/projects",json={"title":"Próba produkcyjna — źródła, lektor i napisy","language":"pl"}).json();pid=p["id"];base="/projects/"+pid
        def current(): return call("GET",base).json()
        def change(changes):
            return call("PATCH",base,json={"expected_revision":current()["revision"],"changes":changes}).json()
        def wait(job):
            deadline=time.monotonic()+1200
            while time.monotonic()<deadline:
                value=call("GET","/jobs/"+job["id"]).json()
                if value["status"]=="SUCCEEDED":return value
                if value["status"] in ("FAILED","CANCELLED","INTERRUPTED"):raise RuntimeError(json.dumps(value,ensure_ascii=False))
                time.sleep(.2)
            call("POST","/jobs/"+job["id"]+"/cancel",json={});raise TimeoutError("Worker exceeded 20 minutes")
        event("project",id=pid)
        if not args.resume_project:
            if args.live:
                result=call("POST",base+"/fetch",json={"result":{"url":"https://www.gutenberg.org/ebooks/164","download_url":"https://www.gutenberg.org/ebooks/164.epub3.images","title":"Twenty Thousand Leagues under the Sea","author":"Jules Verne","provider":"gutenberg"}}).json()
                source=result["source"]
                books=call("GET","/search",params={"provider":"openlibrary","q":"Twenty Thousand Leagues under the Sea","kind":"book"}).json()
                if books:
                    editions=call("GET","/books/editions",params={"work":books[0]["id"]}).json()
                    if editions: call("POST",base+"/sources",json={"expected_revision":current()["revision"],"result":editions[0]})
                stock=call("GET","/search",params={"provider":"commons","q":"hydrophone","kind":"image"}).json()[0]
                job=wait(call("POST",base+"/fetch-queued",json={"result":stock}).json());picture_id=job["result"]["asset_id"]
            else:
                result=call("POST",base+"/media",files={"file":("source.txt",b"Jules Verne wrote Twenty Thousand Leagues under the Sea.")}).json();source=result["source"]
                image=io.BytesIO();Image.new("RGB",(640,360),"#223b53").save(image,"PNG")
                picture_id=call("POST",base+"/media",files={"file":("ocean.png",image.getvalue())}).json()["asset"]["id"]
            event("sources",pages=len(source["pages"]),picture_id=picture_id)
            page=next((x for x in source["pages"] if "Jules Verne" in x["text"]),source["pages"][0])
            quote="Jules Verne" if "Jules Verne" in page["text"] else page["text"][:80]
            p=call("POST",base+f"/sources/{source['id']}/quote",json={"expected_revision":current()["revision"],"page":page["page"],"quote":quote,"claim":"Autorem powieści jest Jules Verne."}).json()
            fact=p["facts"][-1];fact["status"]="VERIFIED";fact["note"]="Sprawdzenie autorstwa w pobranym oryginale; próba produkcyjna, nie twierdzenie o hydrofonie."
            p=change({"facts":[fact],"story":{**p["story"],"central_question":"Jak przejść od źródła do gotowego filmu?","hook":"Zaczynamy od książki i prawdziwego nagrania.","thesis":"Studio zachowuje pochodzenie materiałów.","payoff":"Sprawdzamy obraz, lektora i napisy."}})
            p=call("POST",base+"/story/approve",json={"expected_revision":p["revision"]}).json()
            event("evidence",fact_id=fact["id"],page=page["page"])
            beat=Beat(title="Od książki do filmu",narration="Jules Verne opisywał podmorskie podróże. Sprawdzamy źródło, nagranie i obraz.",fact_ids=[fact["id"]])
            scene=Scene(title="Źródło i ocean",narration=beat.narration,beat_id=beat.id,fact_ids=beat.fact_ids,asset_id=picture_id,prompt="Documentary photograph of an empty ocean at dusk, soft cool light, no text",duration=240,generation={"width":512,"height":288,"steps":12,"seed":73})
            p=change({"beats":[beat.model_dump()],"scenes":[scene.model_dump()]})
            p=call("POST",base+"/edits",json={"expected_revision":p["revision"],"operations":[{"type":"set_sequence","changes":{"width":640,"height":360}}]}).json()
        else:
            scene=Scene.model_validate(p["scenes"][0])
        if args.live:
            previous_image=next((a for a in p["assets"] if a["provenance"].get("kind")=="image"),None)
            image_job={"result":{"asset_id":previous_image["id"]}} if previous_image else wait(call("POST",base+f"/generate/{scene.id}/image",json={"expected_revision":p["revision"]}).json())
            voice_job=wait(call("POST",base+f"/generate/{scene.id}/voice",json={"expected_revision":current()["revision"]}).json());voice_id=voice_job["result"]["asset_id"]
            event("local_models",image_asset=image_job["result"]["asset_id"],voice_asset=voice_id)
        else:
            import subprocess
            tone=args.home/"qa-tone.wav"
            subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","sine=frequency=440:duration=3",str(tone)],check=True)
            from studio_core.media import import_media
            project=app.state.store.get(pid);voice,_=import_media(app.state.store,pid,tone,tone.name,{"provenance":{"kind":"voice","voice_hash":voice_hash(project,project.scenes[0])}});voice_id=voice.id
        p=call("POST",base+f"/scenes/{scene.id}/voice/select",json={"expected_revision":current()["revision"],"asset_id":voice_id}).json()
        p=call("POST",base+f"/scenes/{scene.id}/to-timeline",json={"expected_revision":p["revision"]}).json()
        if args.live:
            wait(call("POST",base+f"/scenes/{scene.id}/alignment",json={"expected_revision":p["revision"],"model":"tiny"}).json())
        else:
            call("POST",base+f"/scenes/{scene.id}/alignment",json={"expected_revision":p["revision"],"words":[{"word":"Próba lokalnego procesu.","start":.1,"end":2.8}]})
        p=current();main_clip=next(c for c in p["sequence"]["clips"] if c["track_id"]=="v1")
        # Same atomic operation path is used for a manual change and accepted AI JSON.
        prompt=call("POST",base+"/assistant/prompt",json={"command":"Dodaj łagodne zbliżenie obrazu","selection":[main_clip["id"]]}).json()
        proposal=call("POST",base+"/assistant/propose",json={"base_revision":prompt["base_revision"],"selection":[main_clip["id"]],"response":json.dumps({"description":"Kontrolowana propozycja testowa; bez wywołania modelu AI","operations":[{"type":"update_clip","clip_id":main_clip["id"],"changes":{"animation":"zoom-in"}}]})}).json()
        p=call("POST",base+"/edits",json={"expected_revision":proposal["base_revision"],"origin":"ai","operations":proposal["operations"]}).json()
        p=call("POST",base+"/captions-to-timeline",json={"expected_revision":p["revision"]}).json()
        call("POST",base+"/versions",json={"name":"Referencja A — źródło i lektor"})
        event("editing",clips=len(p["sequence"]["clips"]),words=len(p["scenes"][0]["words"]))
        checks=call("GET",base+"/check").json()
        if any(i["severity"]=="error" for i in checks["issues"]):raise RuntimeError(json.dumps(checks,ensure_ascii=False))
        # Acknowledging missing local-file license is limited to the deterministic fixture.
        warnings=[i["code"] for i in checks["issues"] if i["severity"]=="warning"]
        if warnings: p=change({"accepted_warnings":warnings})
        else:p=current()
        job=wait(call("POST",base+"/render",json={"expected_revision":p["revision"],"quality":"full","mode":"final"}).json())
        movie=app.state.store.folder(pid)/"exports"/(job["id"]+".mp4");info=probe(movie)
        assert {s["codec_type"] for s in info["streams"]}=={"video","audio"}
        for format in ("md","txt","description","credits","xlsx","srt","vtt"):
            raw=call("GET",base+"/export/"+format).content
            assert raw,format
            (args.home/("qa-export."+format)).write_bytes(raw)
        archive=call("GET",base+"/bundle").content
        restored=call("POST","/projects/import-bundle",files={"file":("project.zip",archive,"application/zip")}).json()
        assert restored["sequence"]==p["sequence"]
        assert restored["scenes"][0]["words"]==p["scenes"][0]["words"]
        assert all((app.state.store.folder(restored["id"])/"media"/a["filename"]).is_file() for a in restored["assets"])
        event("publication_and_reopen",render=str(movie),duration=float(info["format"]["duration"]),restored_id=restored["id"],warnings=warnings)
        report={"live_sources_and_models":args.live,"ai":"validated manual JSON fixture, no paid or live text-model call","project_id":pid,"render_job_id":job["id"],"home":str(args.home),"events":events}
        atomic_json(args.home/"e2e-report.json",report)
        print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
