"""Production tools exposed through the same project service as the CLI."""
from __future__ import annotations

import io
import math
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from fastapi import UploadFile
from fastapi.responses import FileResponse, Response
from PIL import Image

from studio_core.models import Fact, Clip, Project, uid, fps
from studio_core.media import asset_path, import_media, pdf_page, read_document, probe
from studio_core.templates import TEMPLATES
from studio_core.exports import publication, captions, workbook, read_workbook, attribution
from studio_core.freshness import voice_hash, voice_state, sentence_hash
from studio_core.voices import Voices, alignment_hash
from studio_core.store import Conflict, atomic_json, now
from studio_timeline.operations import apply_operations
from studio_timeline.render import render


def register(app, store, jobs, connectors, repo, callbacks):
    voices=Voices(store.root)

    def job_project(pid,body,kind):
        if not body.get("_retry_job"): return store.get(pid)
        old=jobs.get(body["_retry_job"])
        if old["project_id"]!=pid or old["kind"]!=kind or old["status"] not in ("FAILED","CANCELLED","INTERRUPTED"):
            raise ValueError("Niepoprawna migawka ponawianego zadania")
        return Project.model_validate(json.loads((store.root/"job-inputs"/(old["id"]+".json")).read_text()))

    def job_request(action,body,**identifiers):
        return {"action":action,"body":{k:v for k,v in body.items() if k!="_retry_job"},**identifiers}

    @app.get("/api/paper-theatre/groups")
    def theatre_groups():
        from studio_core.paper_theatre import GROUPS
        return [{"id": ident, "name": name, "rig": rig} for ident, name, rig in GROUPS]

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/reference/prompt")
    def theatre_reference_prompt(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre_reference import draft_prompt
        project = store.get(pid)
        if int(body["expected_revision"]) != project.revision:
            raise Conflict("Scena zmieniła się od przygotowania promptu")
        scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
        if not scene:
            raise ValueError("Wybierz scenę Paper Theatre")
        return {"prompt": draft_prompt(scene, body.get("brief", ""), body.get("style", "")),
                "source_scene_id": scene.id, "base_revision": project.revision,
                "width": 512, "height": 288}

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/reference/generate")
    def theatre_reference_generate(pid: str, sid: str, body: dict):
        """Render a cheap 16:9 draft with the configured local image worker."""
        from studio_core.paper_theatre_reference import draft_prompt
        project = store.get(pid)
        if int(body["expected_revision"]) != project.revision:
            raise Conflict("Scena zmieniła się przed generowaniem draftu")
        scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
        if not scene or scene.locked or scene.lock_media:
            raise ValueError("Ujęcie Paper Theatre nie istnieje lub jest zablokowane")
        python = Path(os.environ.get("DOCOS_IMAGE_PYTHON",
                       repo / "pilot" / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")))
        if not python.is_file():
            raise ValueError("Ustaw DOCOS_IMAGE_PYTHON, aby wygenerować draft lokalnym modelem, albo wgraj obraz ręcznie")
        prompt = draft_prompt(scene, body.get("brief", ""), body.get("style", ""))
        active = [x for x in jobs.list(pid) if x["status"] in ("QUEUED", "RUNNING", "CANCEL_REQUESTED")]
        if len(active) >= project.budget.get("max_jobs", 20):
            raise ValueError("Osiągnięto limit zadań tego projektu")

        def run(job_id, progress, cancel):
            directory = store.folder(pid) / "jobs" / job_id
            directory.mkdir(parents=True, exist_ok=True)
            image = directory / "paper-theatre-draft.png"
            log = directory / "worker.log"
            cmd = [str(python), "-I", str(repo / "studio_workers" / "image_worker.py"), str(image),
                   "--prompt", prompt, "--width", "512", "--height", "288",
                   "--steps", "18", "--seed", "42"]
            progress(.05, "Tworzenie miniatury kompozycji")
            with log.open("w+") as stream:
                process = subprocess.Popen(cmd, stdout=stream, stderr=stream)
                while process.poll() is None:
                    if cancel.wait(.25):
                        process.terminate()
                        try:
                            process.wait(timeout=4)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                        raise InterruptedError()
                if process.returncode or not image.is_file():
                    stream.seek(0)
                    raise ValueError("Generator draftu: " + stream.read()[-1200:])
            progress(.85, "Zapis obrazu referencyjnego")
            asset, _ = import_media(store, pid, image, "paper-theatre-reference-" + sid + ".png",
                {"prompt": prompt, "provenance": {
                    "kind": "paper-theatre-reference", "scene_id": sid,
                    "source_revision": project.revision, "draft": True,
                    "width": 512, "height": 288}})
            current = store.get(pid)
            def attach(p):
                target = next((x for x in p.scenes if x.id == sid), None)
                if target is not None and not target.locked and not target.lock_media:
                    target.generation = {**target.generation,
                        "paper_theatre_reference": {"asset_id": asset.id, "prompt": prompt,
                            "source_revision": project.revision, "approved": False}}
            store.mutate(pid, current.revision, attach)
            return {"asset_id": asset.id, "scene_id": sid, "draft": True}
        return jobs.submit(pid, project.revision, "image", run,
            request={"action": "paper-theatre-draft", "scene_id": sid,
                     "body": {"expected_revision": project.revision}},
            snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/reference/analyze")
    def theatre_reference_analyze(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre_reference import propose_objects_from_reference
        project = store.get(pid)
        if int(body["expected_revision"]) != project.revision:
            raise Conflict("Plan odnosi się do poprzedniej rewizji")
        scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
        if not scene:
            raise ValueError("Wybierz ujęcie Paper Theatre")
        ref_id = body.get("reference_asset_id", "")
        if not isinstance(ref_id, str):
            raise ValueError("Niepoprawny obraz referencyjny")
        manifest = propose_objects_from_reference(connectors, store, project, scene,
            ref_id, body.get("brief", ""), body.get("style", ""),
            body.get("reference_notes", ""))
        return {"manifest": manifest, "base_revision": project.revision}

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/cutouts/generate")
    def theatre_generate_reference_cutout(pid: str, sid: str, body: dict):
        """One explicitly requested alpha cutout; always an unselected library variant."""
        from studio_core.paper_theatre_asset_first import normalize_manifest, image_prompts
        from studio_core.paper_theatre_cutouts import MODELS, generate_cutout_png, reserve_cutout_cost, check_reference
        project = store.get(pid)
        if project.revision != int(body["expected_revision"]):
            raise Conflict("Scena zmieniła się od zatwierdzenia kompozycji")
        scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
        if scene is None or scene.locked or scene.lock_media:
            raise ValueError("Nie ma edytowalnego ujęcia Paper Theatre")
        manifest = normalize_manifest(body.get("manifest", {}))
        if manifest["mode"] != "reference-guided" or not manifest["reference_approved"]:
            raise ValueError("Najpierw zaakceptuj referencję i plan osobnych obiektów")
        reference_id = manifest["reference_asset_id"]
        if not reference_id or reference_id in [o["asset_id"] for o in manifest["objects"]]:
            raise ValueError("Referencja nie może być użyta jako gotowy wycinek")
        object_id = body.get("object_id")
        item = next((o for o in image_prompts(manifest) if o["id"] == object_id), None)
        if item is None:
            raise ValueError("Wybierz istniejący obiekt ze spisu sceny")
        if item["asset_id"]:
            raise ValueError("Ten obiekt ma już przypisany PNG; odłącz go przed nową generacją")
        reference = next((a for a in project.assets if a.id == reference_id and a.kind == "image"), None)
        if reference is None:
            raise ValueError("Obraz referencyjny nie jest plikiem tego projektu")
        path = asset_path(store, pid, reference_id, project=project)
        check_reference(path)  # Reject bad formats before accepting a job.
        settings = connectors.config()
        key = settings.get("paper_image_key", "")
        model = settings.get("paper_image_model", "gpt-image-2.5-sunburst")
        estimate = settings.get("paper_image_request_cost", 0)
        if not key or model not in MODELS:
            raise ValueError("Skonfiguruj własny klucz i model generatora PNG w Połączeniach")
        if not isinstance(estimate, (int, float)) or estimate <= 0:
            raise ValueError("Ustaw dodatni szacowany koszt obrazu w Połączeniach")
        active = [j for j in jobs.list(pid) if j["status"] in ("QUEUED", "RUNNING", "CANCEL_REQUESTED")]
        if len(active) >= project.budget.get("max_jobs", 20):
            raise ValueError("Osiągnięto limit zadań projektu")
        prompt = item["prompt"] + (
            " The attached scene is for STYLE and PROPORTION REFERENCE ONLY. "
            "Do not reconstruct the complete scene or cut pixels from the reference. "
            "Generate ONLY this one isolated object on a completely transparent background."
        )

        def run(job_id, progress, cancel):
            if cancel.is_set():
                raise InterruptedError()
            reserve_cutout_cost(store, project, estimate)
            progress(.12, "Wysłano zatwierdzoną referencję do modelu obrazów")
            raw = generate_cutout_png(path, prompt, key=key, model=model)
            if cancel.is_set():
                raise InterruptedError()
            directory = store.folder(pid) / "jobs" / job_id
            directory.mkdir(parents=True, exist_ok=True)
            png = directory / (object_id + ".png")
            png.write_bytes(raw)
            progress(.82, "Weryfikacja PNG i zapis w bibliotece")
            asset, _ = import_media(
                store, pid, png, object_id + ".png",
                {"prompt": prompt, "provenance": {
                    "kind": "paper-theatre-cutout", "source_revision": project.revision,
                    "scene_id": sid, "object_id": object_id, "reference_asset_id": reference_id,
                    "model": model, "job_id": job_id, "user_acceptance_required": True,
                }},
            )
            return {"asset_id": asset.id, "object_id": object_id,
                    "revision": project.revision, "requires_acceptance": True}

        return jobs.submit(pid, project.revision, "image", run, heavy=False,
            request={"action": "paper-theatre-cutout", "scene_id": sid, "object_id": object_id,
                     "reference_id": reference_id},
            snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/asset-first/propose")
    def theatre_asset_first_propose(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre_asset_first import drafting_prompt, normalize_manifest
        from studio_core.assistant import complete
        project = store.get(pid)
        if project.revision != int(body["expected_revision"]):
            raise Conflict("Projekt zmienił się od czasu przygotowania planu")
        scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
        if scene is None: raise ValueError("Wybierz ujęcie Paper Theatre")
        prompt = drafting_prompt(body.get("brief", ""), body.get("style", ""))
        action = body.get("action", "prompt")
        if action == "prompt":
            return {"prompt": prompt, "base_revision": project.revision}
        if action != "generate":
            raise ValueError("Nieznane działanie planera Asset-first")
        output = complete(connectors, prompt, store=store, project=project)
        clean = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", output.strip())
        try:
            value = normalize_manifest(json.loads(clean))
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            raise ValueError("AI zwróciło niepoprawny plan obiektów: " + str(error)) from error
        return {"manifest": value, "base_revision": project.revision}

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/asset-first/prompts")
    def theatre_asset_first_prompts(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre_asset_first import normalize_manifest, image_prompts
        project = store.get(pid)
        if project.revision != int(body["expected_revision"]):
            raise Conflict("Projekt zmienił się od czasu przygotowania promptów")
        if not any(x.id == sid and x.template == "paper-theatre" for x in project.scenes):
            raise ValueError("Wybierz ujęcie Paper Theatre")
        manifest = normalize_manifest(body.get("manifest", {}))
        return {"manifest": manifest, "prompts": image_prompts(manifest)}

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/asset-first/save")
    def theatre_asset_first_save(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre_asset_first import normalize_manifest
        manifest = normalize_manifest(body.get("manifest", {}))
        def save(project):
            scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
            if scene is None or scene.locked or scene.lock_media:
                raise ValueError("Nie ma edytowalnego ujęcia Paper Theatre")
            assigned = [o["asset_id"] for o in manifest["objects"] if o["asset_id"]]
            if any(a not in {asset.id for asset in project.assets} for a in assigned):
                raise ValueError("Plan zawiera nieznany identyfikator pliku")
            scene.generation = {**scene.generation, "paper_theatre_asset_first": manifest}
        return store.mutate(pid, int(body["expected_revision"]), save)

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/asset-first/assemble")
    def theatre_asset_first_assemble(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre_asset_first import normalize_manifest, assemble_manifest
        manifest = normalize_manifest(body.get("manifest", {}))
        def assemble(project):
            scene = next((x for x in project.scenes if x.id == sid and x.template == "paper-theatre"), None)
            if scene is None or scene.locked or scene.lock_media:
                raise ValueError("Nie ma edytowalnego ujęcia Paper Theatre")
            p = assemble_manifest(store, project, body.get("background_id", ""), manifest,
                                  gap=body.get("gap", .12),
                                  group_gap=body.get("group_gap", .22),
                                  hero_outline_px=body.get("hero_outline_px", 8))
            required = math.ceil(p["total_seconds"] * fps(project))
            if scene.duration < required:
                if scene.lock_timing or any(c.scene_id == sid for c in project.sequence.clips):
                    raise ValueError("Wydłuż istniejące ujęcie w Montażu; plan Asset-first się nie mieści")
                scene.duration = required
            scene.asset_id = p["background_id"]
            scene.asset_ids = p["asset_ids"]
            scene.animation = "static"
            # No hidden motion from a legacy preset: the manifest owns composition.
            scene.parameters = {"depth": 0, "layer_cues": p["layer_cues"]}
            scene.generation = {**scene.generation,
                "paper_theatre_asset_first": manifest,
                "paper_theatre_report": {
                    "cutouts": p["cutouts"], "warnings": p["warnings"],
                    "hero_last": p["hero_last"], "reference_match_confirmed": False,
                    "mode": "asset-first"}}
        return store.mutate(pid, int(body["expected_revision"]), assemble)

    @app.post("/api/projects/{pid}/paper-theatre/scenes")
    def theatre_new_scene(pid: str, body: dict):
        from studio_core.models import Scene
        def create(project):
            start=max((scene.start + scene.duration for scene in project.scenes), default=0)
            scene=Scene(title="Paper Theatre 2.5D", start=start, duration=round(20*fps(project)),
                        animation="static", template="paper-theatre",
                        parameters={"depth": .015, "layer_cues": []})
            project.scenes.append(scene)
        return store.mutate(pid, int(body["expected_revision"]), create)

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/preview")
    def theatre_preview(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre import plan
        project=store.get(pid)
        if int(body["expected_revision"]) != project.revision:
            raise Conflict("Plan pochodzi z poprzedniej rewizji filmu")
        scene=next((s for s in project.scenes if s.id == sid), None)
        if scene is None: raise ValueError("Nie ma takiego ujęcia")
        return plan(store,project,body.get("background_id",""),body.get("layers",[]),
                    gap=body.get("gap",.12),group_gap=body.get("group_gap",.22),
                    hero_outline_px=body.get("hero_outline_px",8))

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/commit")
    def theatre_commit(pid: str, sid: str, body: dict):
        from studio_core.paper_theatre import plan
        def change(project):
            scene=next((s for s in project.scenes if s.id == sid), None)
            if scene is None: raise ValueError("Nie ma takiego ujęcia")
            if scene.locked or scene.lock_media:
                raise ValueError("Odblokuj media tego ujęcia przed zmianą scenografii")
            assembled=plan(store,project,body.get("background_id",""),body.get("layers",[]),
                           gap=body.get("gap",.12),group_gap=body.get("group_gap",.22),
                           hero_outline_px=body.get("hero_outline_px",8))
            required=math.ceil(assembled["total_seconds"]*fps(project))
            if scene.duration < required:
                if scene.lock_timing or any(c.scene_id==sid for c in project.sequence.clips):
                    raise ValueError("Ujęcie jest za krótkie. Dostosuj długość w montażu i ponów.")
                scene.duration=required
            scene.template="paper-theatre"
            scene.animation="static"
            scene.asset_id=assembled["background_id"]
            scene.asset_ids=assembled["asset_ids"]
            scene.parameters={"depth":.015,"layer_cues":assembled["layer_cues"]}
            scene.generation={**scene.generation,"paper_theatre_report":{
                "cutouts": assembled["cutouts"], "warnings": assembled["warnings"],
                "hero_last": assembled["hero_last"], "reference_match_confirmed": False}}
        return store.mutate(pid,int(body["expected_revision"]),change)

    @app.get("/api/templates")
    def templates(): return TEMPLATES

    @app.get("/api/font")
    def film_font(name: str="montserrat"):
        from studio_timeline.templates import FONTS,FONT
        return FileResponse(FONTS.get(name,FONT),media_type="font/ttf")

    @app.get("/api/projects/{pid}/clips/{cid}/poster")
    def clip_poster(pid: str, cid: str, revision: int, frame: int=0):
        from studio_timeline.posters import poster
        project=store.get(pid)
        if project.revision!=revision: raise Conflict("Podgląd dotyczy poprzedniej rewizji")
        clip=next((c for c in project.sequence.clips if c.id==cid),None)
        if not clip: raise FileNotFoundError()
        return FileResponse(poster(store,project,clip,frame),media_type="image/png")

    @app.get("/api/projects/{pid}/scenes/{sid}/poster")
    def scene_poster(pid: str, sid: str, revision: int, frame: int=0):
        from studio_timeline.posters import poster
        project=store.get(pid)
        if project.revision!=revision: raise Conflict("Podgląd dotyczy poprzedniej rewizji")
        scene=next((s for s in project.scenes if s.id==sid),None)
        if not scene: raise FileNotFoundError()
        clip=Clip(track_id="v1",scene_id=sid,asset_id=scene.asset_id,asset_ids=scene.asset_ids,template=scene.template,parameters=scene.parameters,duration=scene.duration)
        return FileResponse(poster(store,project,clip,frame),media_type="image/png")

    @app.get("/api/channels")
    def channels(): return store.channels()

    @app.post("/api/channels")
    def save_channel(body: dict): return store.save_channel(body)

    @app.post("/api/projects/{pid}/duplicate")
    def duplicate(pid: str, body: dict): return store.duplicate(pid,str(body.get("title", "")))

    @app.post("/api/projects/{pid}/scenes/{sid}/operation")
    def scene_operation(pid: str, sid: str, body: dict):
        return store.scene_operation(pid,int(body["expected_revision"]),body["operation"],sid,body.get("target"))

    @app.get("/api/projects/{pid}/versions")
    def versions(pid: str): return store.versions(pid)

    @app.post("/api/projects/{pid}/versions")
    def save_version(pid: str, body: dict): return store.save_version(pid,body.get("name","Wariant"))

    @app.get("/api/projects/{pid}/versions/{vid}")
    def version(pid: str, vid: str): return store.version(pid,vid)

    @app.post("/api/projects/{pid}/versions/{vid}/restore")
    def restore_version(pid: str, vid: str, body: dict): return store.restore_version(pid,int(body["expected_revision"]),vid)

    @app.post("/api/projects/{pid}/versions/{vid}/preview")
    def version_preview(pid: str, vid: str, body: dict):
        project=Project.model_validate(store.version(pid,vid)["project"])
        def task(job_id,progress,cancel):
            output=store.folder(pid)/"exports"/(job_id+".mp4"); output.parent.mkdir(exist_ok=True)
            atomic_json(output.with_suffix(".json"),project.model_dump())
            render(store,project,output,progress,cancel,preview=True)
            return {"url":f"/api/jobs/{job_id}/output","revision":project.revision,"variant_id":vid}
        return jobs.submit(pid,project.revision,"preview",task,request=job_request("version_preview",body,version_id=vid),snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/relink")
    def relink(pid: str, body: dict): return store.relink(pid,int(body["expected_revision"]))

    @app.get("/api/projects/{pid}/production")
    def production(pid: str):
        project=store.get(pid)
        from studio_core.budget import spending
        return {"voice":{s.id:voice_state(project,s) for s in project.scenes},"fact_uses":{f.id:[{"scene_id":s.id,"title":s.title} for s in project.scenes if f.id in s.fact_ids] for f in project.facts},
                "spending":spending(store,pid),
                "budget":project.budget,"jobs":len(jobs.list(pid)),"local_cost":0,"estimated_voice_seconds":sum(len(s.narration.split())/2.5 for s in project.scenes if voice_state(project,s) in ("missing","stale")),
                "energy":[{"id":b.id,"title":b.title,"energy":b.energy,"turn":b.turn} for b in project.beats],"attribution":attribution(project)}

    @app.get("/api/projects/{pid}/story/diff")
    def story_diff(pid: str):
        project=store.get(pid)
        approvals=sorted((store.folder(pid)/"approvals").glob("*.json"),key=lambda p:p.stat().st_mtime_ns)
        old=json.loads(approvals[-1].read_text()) if approvals else None
        changes=[]
        if old:
            for name in ("title","story","facts","sources"):
                if old.get(name)!=project.model_dump().get(name): changes.append({"field":name,"before":old.get(name),"after":project.model_dump().get(name)})
        return {"approved_revision":old.get("revision") if old else None,"changes":changes,"dependent_scenes":[s.id for s in project.scenes if s.narration]}

    @app.get("/api/projects/{pid}/export/{format}")
    def export(pid: str, format: str):
        project=store.get(pid)
        if format=="xlsx": content=workbook(project); mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; extension="xlsx"
        elif format in ("srt","vtt"): content=captions(project,format); mime="text/vtt" if format=="vtt" else "text/plain"; extension=format
        elif format in ("md","txt","description","credits"): content=publication(project,format); mime="text/markdown" if format=="md" else "text/plain"; extension="md" if format=="md" else "txt"
        else: raise ValueError("Nieobsługiwany format eksportu")
        return Response(content,media_type=mime,headers={"Content-Disposition":f'attachment; filename="docos-r{project.revision}-{format}.{extension}"',"X-Docos-Revision":str(project.revision)})

    @app.get("/api/jobs/{job_id}/export/{format}")
    def job_publication(job_id: str, format: str):
        job=jobs.get(job_id)
        if job["status"]!="SUCCEEDED" or job["kind"] not in ("render","preview"): raise FileNotFoundError()
        project=Project.model_validate(json.loads((store.folder(job["project_id"])/"exports"/(job_id+".json")).read_text()))
        if format=="json": content=json.dumps(project.model_dump(),ensure_ascii=False,indent=2)
        elif format in ("srt","vtt"): content=captions(project,format)
        elif format in ("description","credits","md","txt"): content=publication(project,format)
        else: raise ValueError("Nieobsługiwany format migawki renderu")
        return Response(content,media_type="application/json" if format=="json" else "text/plain",headers={"X-Docos-Revision":str(project.revision)})

    @app.post("/api/projects/{pid}/workbook")
    async def import_workbook(pid: str, file: UploadFile):
        content=await file.read(8*1024*1024+1)
        if len(content)>8*1024*1024: raise ValueError("Arkusz jest za duży")
        imported=read_workbook(content)
        if imported.id!=pid: raise ValueError("Arkusz pochodzi z innego projektu")
        def update(project):
            for key in ("title","language","channel","facts","sources","assets","story","beats","scenes","sequence"):
                setattr(project,key,getattr(imported,key))
        return store.mutate(pid,imported.revision,update)

    @app.patch("/api/projects/{pid}/assets/{aid}")
    def asset_metadata(pid: str, aid: str, body: dict):
        changes=body.get("changes",{})
        if not set(changes)<={"author","license","license_url","attribution","source_url","name"}: raise ValueError("Nieobsługiwane metadane")
        def update(project):
            asset=next((a for a in project.assets if a.id==aid),None)
            if not asset: raise FileNotFoundError()
            for key,value in changes.items(): setattr(asset,key,str(value))
        return store.mutate(pid,int(body["expected_revision"]),update)

    @app.post("/api/projects/{pid}/sources/{source_id}/quote")
    def cite(pid: str, source_id: str, body: dict):
        def add(project):
            source=next((s for s in project.sources if s.id==source_id),None)
            if not source: raise FileNotFoundError()
            page=str(body.get("page","1")); quote=str(body.get("quote","")); claim=str(body.get("claim") or quote)
            if source.pages and page not in {str(p["page"]) for p in source.pages}: raise ValueError("Nie ma takiej strony w dokumencie")
            page_text=next((p["text"] for p in source.pages if str(p["page"])==page),source.text)
            if quote and " ".join(quote.split()) not in " ".join(page_text.split()):
                raise ValueError("Cytatu nie znaleziono na wskazanej stronie. Sprawdź tekst i lokalizację.")
            if not claim.strip(): raise ValueError("Podaj twierdzenie lub zaznacz cytat")
            project.facts.append(Fact(claim=claim,source=source.title+(" — "+source.edition if source.edition else ""),url=source.url,source_id=source.id,page=page,quote=quote))
        return store.mutate(pid,int(body["expected_revision"]),add)

    def source_file(pid, source_id):
        source=next((s for s in store.get(pid).sources if s.id==source_id),None)
        if not source or not source.asset_id: raise FileNotFoundError()
        return source,asset_path(store,pid,source.asset_id)

    @app.get("/api/projects/{pid}/sources/{source_id}/page/{page}/image")
    def page_image(pid: str, source_id: str, page: int):
        source,path=source_file(pid,source_id)
        if path.suffix.lower()!=".pdf": raise ValueError("Podgląd strony graficznej jest dostępny dla PDF")
        return FileResponse(pdf_page(path,page),media_type="image/png")

    @app.post("/api/projects/{pid}/sources/{source_id}/ocr")
    def ocr(pid: str, source_id: str, body: dict):
        project=job_project(pid,body,"ocr")
        source=next(s for s in project.sources if s.id==source_id)
        path=asset_path(store,pid,source.asset_id,project=project)
        def task(job_id,progress,cancel):
            from studio_core.media import recognize
            pages=[]
            for index,page in enumerate(source.pages):
                if cancel.is_set(): raise InterruptedError()
                if body.get("pages") and str(page["page"]) not in [str(x) for x in body["pages"]]:
                    pages.append(page); continue
                if path.suffix.lower()!=".pdf": raise ValueError("OCR wymaga oryginalnego PDF")
                text=recognize(pdf_page(path,int(page["page"]),cancel),cancel)
                pages.append({**page,"text":text[:16000],"method":"ocr","needs_ocr":False})
                progress((index+1)/max(1,len(source.pages)),"OCR strony "+str(page["page"]))
            current=store.get(pid)
            def attach(p):
                found=next((s for s in p.sources if s.id==source_id),None)
                if not found or found.pages!=source.pages or found.asset_id!=source.asset_id: raise Conflict("Źródło zmieniło się podczas OCR; uruchom aktualny odczyt")
                found.pages=pages; found.text="\n\n".join(page["text"] for page in pages)[:500000]
            store.mutate(pid,current.revision,attach)
            return {"source_id":source_id,"revision":project.revision}
        return jobs.submit(pid,project.revision,"ocr",task,request=job_request("ocr",body,source_id=source_id),snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/sources/{source_id}/illustration")
    def illustration(pid: str, source_id: str, body: dict):
        source,path=source_file(pid,source_id); page=str(body.get("page","1"))
        if path.suffix==".epub":
            from studio_core.media import epub_images
            images=epub_images(path); index=int(body.get("image_index",0))
            if not 0<=index<len(images): raise ValueError("Nie ma takiej ilustracji")
            item=images[index]
            if item["chapters"] and page not in item["chapters"]: raise ValueError("Wybierz rozdział zawierający tę ilustrację")
            image=Image.open(io.BytesIO(item["bytes"]))
        else:image=Image.open(pdf_page(path,int(page)))
        crop=body.get("crop",{"x":0,"y":0,"width":1,"height":1})
        x,y,w,h=(float(crop[k]) for k in ("x","y","width","height"))
        if min(x,y)<0 or min(w,h)<=0 or x+w>1.001 or y+h>1.001: raise ValueError("Niepoprawny prostokąt ilustracji")
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            image.crop((round(x*image.width),round(y*image.height),round((x+w)*image.width),round((y+h)*image.height))).save(tmp.name)
            asset,_=import_media(store,pid,Path(tmp.name),f"strona-{page}.png",{"source_url":source.url,"author":source.author,"license":str(body.get("license","")),"provenance":{"source_id":source.id,"page":page,"crop":crop,"kind":"document-extract"}})
        return {"asset":asset,"project":store.get(pid)}

    @app.get("/api/projects/{pid}/sources/{source_id}/images")
    def book_images(pid: str, source_id: str):
        from studio_core.media import epub_images
        _,path=source_file(pid,source_id)
        if path.suffix!=".epub": raise ValueError("Lista ilustracji jest dostępna dla EPUB")
        return [{"index":i,"name":item["name"],"chapters":item["chapters"]} for i,item in enumerate(epub_images(path))]

    @app.get("/api/projects/{pid}/sources/{source_id}/image/{index}")
    def epub_image(pid: str, source_id: str, index: int):
        from studio_core.media import epub_images
        _,path=source_file(pid,source_id)
        if path.suffix!=".epub": raise ValueError("Wybierz książkę EPUB")
        images=epub_images(path)
        if not 0<=index<len(images): raise FileNotFoundError()
        output=io.BytesIO();Image.open(io.BytesIO(images[index]["bytes"])).convert("RGB").save(output,"PNG")
        return Response(output.getvalue(),media_type="image/png")

    @app.get("/api/voices")
    def list_voices(): return voices.list()

    @app.post("/api/voices")
    async def create_voice(file: UploadFile, name: str="Mój głos"):
        content=await file.read(30*1024*1024+1)
        if len(content)>30*1024*1024: raise ValueError("Próbka jest za duża")
        with tempfile.NamedTemporaryFile(suffix=Path(file.filename or ".wav").suffix) as tmp:
            tmp.write(content); tmp.flush()
            return voices.create(name,Path(tmp.name))

    @app.patch("/api/voices/{voice_id}")
    def update_voice(voice_id: str, body: dict): return voices.update(voice_id,body)

    @app.get("/api/voices/{voice_id}/sample")
    def voice_sample(voice_id: str): return FileResponse(voices.folder(voice_id)/"reference.wav",media_type="audio/wav")

    @app.post("/api/projects/{pid}/voices/select")
    def select_voice(pid: str, body: dict):
        profile=voices.get(body["voice_id"]) if body.get("voice_id") else {}
        return store.patch(pid,int(body["expected_revision"]),{"voice_profile":profile})

    @app.get("/api/projects/{pid}/assets/{aid}/waveform")
    def audio_waveform(pid: str, aid: str, bins: int=240):
        from studio_core.audio import waveform
        path=asset_path(store,pid,aid)
        cache=path.with_suffix(f".wave-{max(16,min(2000,bins))}.json")
        if not cache.exists(): atomic_json(cache,waveform(path,bins))
        return json.loads(cache.read_text())

    @app.post("/api/projects/{pid}/scenes/{sid}/sentences/{sentence_id}/select")
    def select_sentence(pid: str, sid: str, sentence_id: str, body: dict):
        def select(project):
            scene=next(s for s in project.scenes if s.id==sid)
            sentence=next(s for s in scene.sentences if s.id==sentence_id)
            asset=next(a for a in project.assets if a.id==body["asset_id"])
            if asset.id not in sentence.variants or asset.provenance.get("voice_hash")!=sentence_hash(project,scene,sentence.text):
                raise ValueError("Ten wariant zdania pochodzi z innego tekstu lub profilu")
            sentence.asset_id=asset.id; sentence.duration=asset.duration; sentence.input_hash=asset.provenance["voice_hash"]
        return store.mutate(pid,int(body["expected_revision"]),select)

    @app.post("/api/projects/{pid}/scenes/{sid}/voice/select")
    def select_scene_voice(pid: str, sid: str, body: dict):
        def select(project):
            scene=next(s for s in project.scenes if s.id==sid)
            if scene.locked or scene.lock_narration: raise ValueError("Narracja ujęcia jest zablokowana")
            asset=next(a for a in project.assets if a.id==body["asset_id"])
            if asset.kind!="audio": raise ValueError("Wybierz nagranie audio")
            length=max(1,int(asset.duration*fps(project)))
            scene.voice_asset_id=asset.id;scene.timing="measured"
            # Preserve manually edited picture timing; replacing narration is explicit.
            linked=[c for c in project.sequence.clips if c.scene_id==sid and next(t for t in project.sequence.tracks if t.id==c.track_id).role=="narration"]
            ops=[{"type":"remove_clip","clip_id":c.id} for c in linked]
            ops.append({"type":"add_clip","clip":Clip(track_id="a1",asset_id=asset.id,scene_id=sid,start=scene.start,duration=length,title="Lektor · "+scene.title).model_dump()})
            apply_operations(project,ops)
            scene=next(s for s in project.scenes if s.id==sid)
            if not any(c.scene_id==sid and next(t for t in project.sequence.tracks if t.id==c.track_id).role=="picture" for c in project.sequence.clips) and not scene.lock_timing:
                scene.duration=length
        return store.mutate(pid,int(body["expected_revision"]),select)

    @app.post("/api/projects/{pid}/scenes/{sid}/assemble")
    def assemble_voice(pid: str, sid: str, body: dict):
        from studio_core.audio import assemble
        project=job_project(pid,body,"assemble")
        if project.revision!=int(body["expected_revision"]): raise Conflict("Projekt zmienił się przed złożeniem głosu")
        scene=next(s for s in project.scenes if s.id==sid)
        if scene.locked or scene.lock_narration: raise ValueError("Lektor jest zablokowany")
        def task(job_id,progress,cancel):
            work=store.folder(pid)/"jobs"/job_id; work.mkdir(parents=True)
            output=work/"assembled.wav"
            words=assemble(store,project,scene,output,cancel)
            asset,_=import_media(store,pid,output,scene.title+"-lektor.wav",{"provenance":{"kind":"voice","voice_hash":voice_hash(project,scene),"input_revision":project.revision,"sentences":words}})
            current=store.get(pid)
            def attach(p):
                found=next(s for s in p.scenes if s.id==sid)
                if found.locked or found.lock_narration: return
                if asset.id not in found.variants: found.variants.append(asset.id)
            store.mutate(pid,current.revision,attach)
            return {"asset_id":asset.id,"revision":project.revision}
        return jobs.submit(pid,project.revision,"assemble",task,request=job_request("assemble",body,scene_id=sid),snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/scenes/{sid}/alignment")
    def align_voice(pid: str, sid: str, body: dict):
        from studio_core.audio import run_process,validate_words
        project=job_project(pid,body,"alignment"); scene=next(s for s in project.scenes if s.id==sid)
        if project.revision!=int(body["expected_revision"]): raise Conflict("Projekt zmienił się przed dopasowaniem")
        if scene.locked or scene.lock_narration: raise ValueError("Lektor jest zablokowany")
        if voice_state(project,scene)!="current": raise ValueError("Najpierw wybierz aktualne nagranie")
        asset=next(a for a in project.assets if a.id==scene.voice_asset_id)
        expected_hash=alignment_hash(project,scene)
        def save(words):
            validate_words(words,asset.duration)
            current=store.get(pid)
            def attach(p):
                found=next(s for s in p.scenes if s.id==sid)
                if alignment_hash(p,found)!=expected_hash: raise Conflict("Nagranie zmieniło się podczas dopasowania")
                found.words=words; found.alignment_hash=expected_hash
            return store.mutate(pid,current.revision,attach)
        if body.get("method")=="sentences":
            words=asset.provenance.get("sentences")
            if not words: raise ValueError("Wybrane audio nie ma pomiarów zdań. Złóż zdania lub użyj rozpoznawania.")
            return save(words)
        if "words" in body: return save(body["words"])
        python=Path(os.environ.get("DOCOS_ALIGN_PYTHON",repo/".venv-align"/("Scripts/python.exe" if os.name=="nt" else "bin/python")))
        if not python.is_file(): raise ValueError("Zainstaluj lokalne dopasowanie: uv venv --python 3.12 .venv-align; uv pip install --python .venv-align/bin/python -r requirements-align.txt")
        model=str(body.get("model","small"))
        if model not in ("tiny","base","small","medium"): raise ValueError("Wybierz model tiny/base/small/medium")
        def task(job_id,progress,cancel):
            work=store.folder(pid)/"jobs"/job_id; work.mkdir(parents=True)
            output=work/"words.json"
            run_process([str(python),"-I",str(repo/"studio_workers/align_worker.py"),str(asset_path(store,pid,asset.id,project=project)),str(output),"--language",project.language,"--model",model],cancel)
            result=json.loads(output.read_text()); updated=save(result["words"])
            return {"revision":updated.revision,"words":len(result["words"]),"method":result["method"]}
        return jobs.submit(pid,project.revision,"alignment",task,request=job_request("alignment",body,scene_id=sid),snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/frame")
    def exact_frame(pid: str, body: dict):
        project=job_project(pid,body,"frame")
        if project.revision!=int(body["expected_revision"]): raise Conflict("Podgląd pochodzi z innej rewizji")
        if body.get("operations") and not body.get("_retry_job"):
            from studio_core.assistant import parse_proposal,scope_selection
            proposal=parse_proposal(json.dumps({"operations":body["operations"]}),project,scope_selection(project,body));apply_operations(project,proposal["operations"],"ai")
        frame=int(body.get("frame",0))
        from studio_core.models import duration
        if not 0<=frame<duration(project): raise ValueError("Klatka poza sekwencją")
        def task(job_id,progress,cancel):
            from studio_core.audio import run_process
            folder=store.folder(pid)/"exports"; folder.mkdir(exist_ok=True)
            video=folder/(job_id+".mp4"); output=folder/(job_id+".png")
            render(store,project,video,progress,cancel,preview=True,start_frame=frame,end_frame=frame+1)
            run_process(["ffmpeg","-v","error","-y","-i",str(video),"-frames:v","1",str(output)],cancel)
            return {"url":f"/api/jobs/{job_id}/frame","frame":frame,"revision":project.revision}
        return jobs.submit(pid,project.revision,"frame",task,request=job_request("frame",body),snapshot=project.model_dump())

    @app.get("/api/jobs/{job_id}/frame")
    def frame_output(job_id: str):
        job=jobs.get(job_id)
        if job["status"]!="SUCCEEDED" or job["kind"]!="frame": raise FileNotFoundError()
        return FileResponse(store.folder(job["project_id"])/"exports"/(job_id+".png"),media_type="image/png")

    @app.post("/api/projects/{pid}/assets/{aid}/proxy")
    def proxy(pid: str, aid: str, body: dict):
        from studio_core.audio import run_process
        project=job_project(pid,body,"proxy"); asset=next(a for a in project.assets if a.id==aid)
        if asset.kind!="video": raise ValueError("Proxy jest przeznaczone dla filmu")
        def task(job_id,progress,cancel):
            folder=store.root/"cache/proxy"; folder.mkdir(parents=True,exist_ok=True)
            output=folder/(asset.sha256+"-v2.mp4")
            if not output.exists():
                temporary=output.with_suffix(".part.mp4")
                run_process(["ffmpeg","-v","error","-y","-i",str(asset_path(store,pid,aid,project=project)),"-vf","scale=960:540:force_original_aspect_ratio=decrease:force_divisible_by=2","-c:v","libx264","-preset","veryfast","-crf","25","-c:a","aac","-movflags","+faststart",str(temporary)],cancel)
                probe(temporary); os.replace(temporary,output)
            return {"url":f"/api/projects/{pid}/assets/{aid}/proxy","revision":project.revision,"asset_id":aid}
        return jobs.submit(pid,project.revision,"proxy",task,request=job_request("proxy",body,asset_id=aid),snapshot=project.model_dump())

    @app.get("/api/projects/{pid}/assets/{aid}/proxy")
    def proxy_file(pid: str, aid: str):
        asset=next(a for a in store.get(pid).assets if a.id==aid)
        path=store.root/"cache/proxy"/(asset.sha256+"-v2.mp4")
        if not path.is_file(): raise FileNotFoundError()
        return FileResponse(path,media_type="video/mp4")

    @app.get("/api/projects/{pid}/assets/{aid}/proxy-status")
    def proxy_status(pid: str, aid: str):
        asset=next(a for a in store.get(pid).assets if a.id==aid)
        return {"ready":(store.root/"cache/proxy"/(asset.sha256+"-v2.mp4")).is_file(),"url":f"/api/projects/{pid}/assets/{aid}/proxy"}

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str): return jobs.get(job_id)

    @app.post("/api/jobs/{job_id}/retry")
    def retry_job(job_id: str):
        result=jobs.retry(job_id)
        if result: return result
        old=jobs.get(job_id); request=old.get("request") or {}; pid=old["project_id"]
        if request.get("action")=="render":
            path=store.root/"job-inputs"/(old["id"]+".json")
            if not path.exists():return callbacks["render"](pid,request["body"])
            project=Project.model_validate(json.loads(path.read_text()));preview=old["kind"]=="preview";body=request["body"]
            def task(new_id,progress,cancel):
                output=store.folder(pid)/"exports"/(new_id+".mp4");output.parent.mkdir(exist_ok=True)
                atomic_json(output.with_suffix(".json"),project.model_dump())
                render(store,project,output,progress,cancel,preview=preview,start_frame=int(body.get("start_frame",0)),end_frame=body.get("end_frame"))
                return {"url":f"/api/jobs/{new_id}/output","revision":project.revision,"mode":body.get("mode","draft")}
            return jobs.submit(pid,project.revision,old["kind"],task,request=request,snapshot=project.model_dump())
        if request.get("action")=="generate": return callbacks["generate"](pid,request["scene_id"],request["kind"],{**request["body"],"_retry_job":old["id"]})
        if request.get("action")=="motion": return callbacks["motion"](pid,request["insert_id"],{**request["body"],"_retry_job":old["id"]})
        if request.get("action")=="fetch": return queued_fetch(pid,request["body"])
        if request.get("action")=="search": return multisearch(pid,request["body"])
        body={**request.get("body",{}),"_retry_job":old["id"]}
        if request.get("action")=="frame": return exact_frame(pid,body)
        if request.get("action")=="proxy": return proxy(pid,request["asset_id"],body)
        if request.get("action")=="ocr": return ocr(pid,request["source_id"],body)
        if request.get("action")=="assemble": return assemble_voice(pid,request["scene_id"],body)
        if request.get("action")=="alignment": return align_voice(pid,request["scene_id"],body)
        if request.get("action")=="version_preview": return version_preview(pid,request["version_id"],body)
        if request.get("action")=="folder": return import_folder(pid,request["body"])
        raise ValueError("Otwórz narzędzie i ponów operację dla aktualnej rewizji projektu")

    @app.post("/api/projects/{pid}/fetch-queued")
    def queued_fetch(pid: str, body: dict):
        project=store.get(pid)
        def task(job_id,progress,cancel):
            progress(.1,"Pobieranie materiału")
            if cancel.is_set(): raise InterruptedError()
            response=callbacks["fetch"](pid,body)
            # Imported bytes remain in the library if a cancellation arrives after download.
            asset=response.get("asset"); asset_id=asset.id if asset else None
            if not cancel.is_set() and body.get("scene_id") and asset_id:
                current=store.get(pid)
                def attach(p):
                    scene=next((s for s in p.scenes if s.id==body["scene_id"]),None)
                    if scene and not scene.locked and not scene.lock_media:
                        if asset_id not in scene.variants: scene.variants.append(asset_id)
                store.mutate(pid,current.revision,attach)
            return {"asset_id":asset_id,"revision":project.revision}
        return jobs.submit(pid,project.revision,"fetch",task,request={"action":"fetch","body":body},heavy=False)

    @app.post("/api/projects/{pid}/search")
    def multisearch(pid: str, body: dict):
        from concurrent.futures import ThreadPoolExecutor,as_completed
        project=store.get(pid); query=str(body.get("query","")); kind=str(body.get("kind","image")); page=int(body.get("page",1))
        providers=body.get("providers") or [c["id"] for c in connectors.catalog() if c["configured"] and kind in c["kinds"]]
        if not isinstance(providers,list) or len(providers)>12: raise ValueError("Wybierz do dwunastu dostawców")
        def task(job_id,progress,cancel):
            results=[]; errors={}
            with ThreadPoolExecutor(max_workers=4) as pool:
                requests={pool.submit(connectors.search,provider,query,kind,page):provider for provider in providers}
                for future in as_completed(requests):
                    if cancel.is_set():
                        for pending in requests: pending.cancel()
                        raise InterruptedError()
                    provider=requests[future]
                    try: results.extend(future.result())
                    except Exception: errors[provider]="Źródło nie odpowiedziało. Sprawdź połączenie, limit lub klucz API."
                    progress((len(errors)+len({x['provider'] for x in results}))/max(1,len(providers)),"Wyniki: "+provider)
            orientation=body.get("orientation"); license_query=str(body.get("license","")).casefold()
            if orientation: results=[x for x in results if not x.get("width") or ((x.get("width",0)>=x.get("height",0))==(orientation=="landscape"))]
            if license_query: results=[x for x in results if license_query in x.get("license","").casefold()]
            return {"results":results,"errors":errors,"revision":project.revision}
        return jobs.submit(pid,project.revision,"search",task,request={"action":"search","body":body},heavy=False)

    @app.get("/api/books/editions")
    def editions(work: str, page: int=1): return connectors.editions(work,page)

    @app.post("/api/feed")
    def rss(body: dict): return connectors.feed(str(body.get("url","")))

    @app.post("/api/connectors/{provider}/test")
    def connector_test(provider: str):
        catalog=next((c for c in connectors.catalog() if c["id"]==provider),None)
        if not catalog: raise ValueError("Nieznane połączenie")
        try:
            results=connectors.search(provider,"ocean",catalog["kinds"][0])
            return {"ok":True,"message":f"Połączenie działa: {len(results)} wyników","capabilities":catalog["capabilities"]}
        except Exception:
            return {"ok":False,"message":"Błąd połączenia. Sprawdź klucz, adres API i limit dostawcy.","capabilities":catalog["capabilities"]}

    @app.post("/api/projects/{pid}/beats/{bid}/writer/{action}")
    def fragment_writer(pid: str, bid: str, action: str, body: dict):
        from studio_core.assistant import complete
        project=store.get(pid); beat=next(b for b in project.beats if b.id==bid)
        prompt="Popraw wyłącznie wskazany fragment dokumentu. Zwróć JSON {narration,title,goal,turn,fact_ids}. Narracja bez instrukcji obrazu. Nie dodawaj faktów bez źródeł. Zachowaj ciągłość historii.\n"+json.dumps({"story":project.story,"fragments":[b.model_dump() for b in project.beats],"target":beat.model_dump(),"facts":[f.model_dump() for f in project.facts],"channel":project.channel_profile,"instruction":str(body.get("instruction",""))},ensure_ascii=False)
        if action=="prompt": return {"prompt":prompt,"base_revision":project.revision}
        if action=="generate": return {"response":complete(connectors,prompt,store=store,project=project),"base_revision":project.revision}
        if action!="import": raise ValueError("Nieznana operacja")
        if int(body.get("base_revision",-1))!=project.revision: raise Conflict("Fragment zmienił się od przygotowania propozycji")
        response=str(body.get("response","")); response=re.sub(r"^```(?:json)?\s*|\s*```$","",response.strip())
        data=json.loads(response)
        if not isinstance(data,dict) or not set(data)<={"narration","title","goal","turn","fact_ids"}: raise ValueError("Niepoprawna propozycja fragmentu")
        def change(p):
            found=next(b for b in p.beats if b.id==bid)
            known={f.id:f for f in p.facts}
            if any(fid not in known or known[fid].status=="UNVERIFIED" for fid in data.get("fact_ids",found.fact_ids)):raise ValueError("Fragment wskazuje nieznany lub niesprawdzony fakt")
            for key,value in data.items(): setattr(found,key,value)
            scenes=[s for s in p.scenes if s.beat_id==bid]
            if scenes and "narration" in data:
                if any(s.locked or s.lock_narration for s in scenes): raise ValueError("Narracja fragmentu jest zablokowana")
                if sum(bool(s.narration) for s in scenes)>1: raise ValueError("Fragment ma narrację rozdzieloną na ujęcia. Zapisz poprawkę w polu fragmentu i ręcznie rozdziel tekst.")
                scenes[0].narration=found.narration
                scenes[0].fact_ids=found.fact_ids
        return store.mutate(pid,project.revision,change)

    @app.post("/api/projects/{pid}/scenes/{sid}/suggestions")
    def shot_suggestions(pid: str, sid: str, body: dict):
        project=store.get(pid); scene=next(s for s in project.scenes if s.id==sid)
        words=set(re.findall(r"\w{4,}",(scene.narration+" "+scene.search_query+" "+scene.title).casefold()))
        candidates=[]
        for asset in project.assets:
            if asset.kind not in ("image","video"): continue
            matches=words&set(re.findall(r"\w{4,}",(asset.name+" "+asset.prompt+" "+asset.attribution).casefold()))
            if matches:
                candidates.append({"asset_id":asset.id,"score":len(matches),"reason":"Wspólne słowa: "+", ".join(sorted(matches)),"uses":[s.title for s in project.scenes if s.asset_id==asset.id or asset.id in s.asset_ids],"source":asset.source_url})
        return {"assets":sorted(candidates,key=lambda x:-x["score"]),"search_query":scene.search_query or " ".join(sorted(words)[:8]),"style":project.channel_profile,"fact_ids":scene.fact_ids,"revision":project.revision}

    @app.get("/api/diagnostics")
    def diagnose():
        from studio_core.diagnostics import diagnostics
        return diagnostics(repo)

    @app.post("/api/ai/test")
    def test_ai():
        from studio_core.assistant import complete
        try: return {"ok":True,"message":complete(connectors,'Return only the text: DocOS connection OK')[:500]}
        except Exception as error: return {"ok":False,"message":str(error)[:1000]}

    @app.post("/api/projects/{pid}/captions-to-timeline")
    def captions_to_timeline(pid: str, body: dict):
        from studio_core.exports import caption_segments
        def add(project):
            segments=caption_segments(project)
            ops=[{"type":"remove_clip","clip_id":c.id} for c in project.sequence.clips if c.parameters.get("measured_caption")]
            for item in segments:
                start=round(item["start"]*fps(project));duration=max(1,round(item["end"]*fps(project))-start)
                ops.append({"type":"add_clip","clip":Clip(track_id="t1",text=item["text"],title="Napisy",start=start,duration=duration,y=.32,scale=.8,parameters={"measured_caption":True}).model_dump()})
            for first in range(0,len(ops),200): apply_operations(project,ops[first:first+200])
        return store.mutate(pid,int(body["expected_revision"]),add)

    @app.post("/api/projects/{pid}/scenes/{sid}/review-evidence")
    def review_evidence(pid: str, sid: str, body: dict):
        from studio_core.freshness import evidence_hash
        def review(project):
            scene=next(s for s in project.scenes if s.id==sid)
            scene.script_input_hash=evidence_hash(project,scene)
        return store.mutate(pid,int(body["expected_revision"]),review)

    @app.post("/api/projects/{pid}/planner/{action}")
    def shot_planner(pid: str, action: str, body: dict):
        from studio_core.assistant import complete
        project=store.get(pid);beat=next(b for b in project.beats if b.id==body["beat_id"])
        prompt='Zaplanuj przebitki do fragmentu dokumentu na podstawie narracji, dowodów i stylu kanału. Nie wymyślaj faktów ani nazw plików. Zwróć tablicę JSON [{"title":"", "seconds":6,"template":"media","parameters":{},"prompt":"opis obrazu","search_query":"archiwum","fact_ids":[],"reason":"dlaczego to ujęcie wspiera narrację"}]. Nie powtarzaj całej narracji w każdym kadrze.\n'+json.dumps({"fragment":beat.model_dump(),"facts":[f.model_dump() for f in project.facts if f.id in beat.fact_ids],"channel":project.channel_profile,"templates":[t["id"] for t in TEMPLATES],"existing":[s.model_dump() for s in project.scenes if s.beat_id==beat.id],"instruction":body.get("instruction","")},ensure_ascii=False)
        if action=="prompt": return {"prompt":prompt,"base_revision":project.revision}
        if action=="generate": return {"response":complete(connectors,prompt,store=store,project=project),"base_revision":project.revision}
        if action!="import": raise ValueError("Nieznana operacja planera")
        if int(body.get("base_revision",-1))!=project.revision: raise Conflict("Plan dotyczy poprzedniej rewizji")
        response=re.sub(r"^```(?:json)?\s*|\s*```$","",str(body.get("response","")).strip());data=json.loads(response)
        if not isinstance(data,list) or not 1<=len(data)<=100: raise ValueError("Plan wymaga 1–100 ujęć")
        def append(p):
            from studio_core.models import Scene
            first=max((s.start+s.duration for s in p.scenes),default=0)
            has_narration=any(s.narration for s in p.scenes if s.beat_id==beat.id)
            for index,item in enumerate(data):
                if not set(item.get("fact_ids",[]))<=set(beat.fact_ids): raise ValueError("Plan wskazuje fakt spoza fragmentu")
                duration=max(1,round(float(item.get("seconds",6))*fps(p)))
                scene=Scene(title=str(item.get("title","Przebitka")),start=first,duration=duration,beat_id=beat.id,template=item.get("template","media"),parameters=item.get("parameters",{}),prompt=item.get("prompt",""),search_query=item.get("search_query",""),fact_ids=item.get("fact_ids",[]),narration=beat.narration if not has_narration and index==0 else "",generation={"planning_reason":str(item.get("reason","")),"input_revision":project.revision})
                p.scenes.append(scene);first+=duration
        return store.mutate(pid,project.revision,append)

    @app.post("/api/projects/{pid}/folder")
    def import_folder(pid: str, body: dict):
        from studio_core.media import IMAGE_EXT,VIDEO_EXT,AUDIO_EXT,DOC_EXT,MAX_UPLOAD
        folder=Path(str(body.get("path",""))).expanduser().resolve()
        if not folder.is_dir(): raise ValueError("Folder nie istnieje")
        project=store.get(pid)
        def task(job_id,progress,cancel):
            files=sorted(p for p in folder.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in IMAGE_EXT|VIDEO_EXT|AUDIO_EXT|DOC_EXT)[:1000]
            licenses={}
            from studio_core.media import PlainText
            for registry in folder.rglob("licenses.json"):
                if registry.is_symlink() or registry.stat().st_size>2*1024*1024: continue
                try:
                    for record in json.loads(registry.read_text()):
                        if isinstance(record,dict) and record.get("file"):
                            licenses[str(registry.parent/Path(record["file"]).name)]=record
                except (ValueError,TypeError): continue
            imported=[]; errors=[]
            for i,path in enumerate(files):
                if cancel.is_set(): raise InterruptedError()
                if path.stat().st_size>MAX_UPLOAD: errors.append({"name":path.name,"error":"Przekroczono 300 MB"}); continue
                try:
                    license=licenses.get(str(path),{})
                    metadata={"provenance":{"provider":"folder","relative_path":str(path.relative_to(folder))},"source_url":str(license.get("page") or license.get("url", "")),"author":PlainText.extract(str(license.get("artist", ""))),"license":str(license.get("license", "")),"license_url":str(license.get("license_url", "")),"attribution":PlainText.extract(str(license.get("credit", "")))}
                    asset,_=import_media(store,pid,path,path.name,metadata)
                    imported.append(asset.id)
                except Exception: errors.append({"name":path.name,"error":"Nie udało się odczytać pliku"})
                progress((i+1)/max(1,len(files)),path.name)
            current=store.get(pid)
            if body.get("relink",True): store.relink(pid,current.revision)
            if body.get("watch"):
                atomic_json(store.folder(pid)/"watched-folder.json",{"path":str(folder),"enabled":True,"last_scan":now()})
            return {"asset_ids":list(dict.fromkeys(imported)),"errors":errors,"revision":project.revision}
        return jobs.submit(pid,project.revision,"folder",task,heavy=False,request=job_request("folder",body))

    @app.get("/api/projects/{pid}/folder")
    def folder_status(pid: str):
        path=store.folder(pid)/"watched-folder.json"
        return json.loads(path.read_text()) if path.exists() else {"enabled":False}

    @app.delete("/api/projects/{pid}/folder")
    def unwatch_folder(pid: str):
        (store.folder(pid)/"watched-folder.json").unlink(missing_ok=True)
        return {"enabled":False}

    # Watch only folders explicitly selected in Studio; no paths enter a portable project.
    import threading
    stop=threading.Event()
    original_close=jobs.close
    def close(): stop.set(); original_close()
    jobs.close=close
    def watch():
        while not stop.wait(15):
            for path in (store.root/"projects").glob("prj_*/watched-folder.json"):
                try:
                    value=json.loads(path.read_text()); pid=path.parent.name
                    if value.get("enabled") and not any(j["kind"]=="folder" and j["status"] in ("RUNNING","QUEUED") for j in jobs.list(pid)):
                        folder=Path(value["path"])
                        stamp=max((p.stat().st_mtime_ns for p in folder.rglob("*") if p.is_file() and not p.is_symlink()),default=0)
                        if value.get("stamp")!=stamp:
                            value["stamp"]=stamp; atomic_json(path,value)
                            import_folder(pid,{"path":str(folder),"watch":False})
                except (OSError,ValueError): continue
    threading.Thread(target=watch,daemon=True,name="docos-folder-watch").start()

