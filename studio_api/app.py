from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, UploadFile, Request, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, ValidationError

from studio_core.models import Project, Scene, Clip, Source, Fact, from_docos, import_content, uid, fps, duration
from studio_core.store import ProjectStore, Conflict, atomic_json, now, story_hash
from studio_core.service import ProjectService
from studio_core.quality import check_project
from studio_core.freshness import voice_hash, voice_state, voice_config, sentence_hash, spoken,image_hash,image_prompt,image_config
from studio_core.voices import Voices
from studio_core.media import import_media, asset_path, PlainText, MAX_UPLOAD
from studio_core.demo import create_demo
from studio_core.assistant import editing_prompt, parse_proposal, generate_proposal
from studio_core.assistant import complete
from studio_core.assistant import scope_selection,enforce_range
from studio_core import writer
from studio_core.bundles import export_bundle, import_bundle, MAX_BUNDLE
from studio_connectors.sources import Connectors, get_bytes
from studio_timeline.operations import apply_operations
from studio_timeline.render import render
from studio_workers.jobs import Jobs
from studio_api.inserts import register_inserts
from studio_core.workspace import Workspace
from studio_api.workspace import register_workspace
from studio_api.animation import register_animation

REPO = Path(__file__).resolve().parents[1]


def create_app(root: Path | None = None, *, seed_demo=True) -> FastAPI:
    root = root or Path(os.environ.get("DOCOS_STUDIO_HOME", REPO / ".docos-studio"))
    store = ProjectService(root)
    connectors = Connectors(root)
    voices = Voices(root)
    jobs = Jobs(root)
    if seed_demo and not store.list():
        create_demo(store)

    @asynccontextmanager
    async def lifespan(app):
        yield
        jobs.close()

    app = FastAPI(title="DocOS Studio", version="0.2.0", lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])
    app.state.store = store; app.state.jobs = jobs; app.state.connectors = connectors
    workspace = Workspace(store)
    app.state.workspace = workspace
    from studio_api.paper_review import register_paper_review
    register_paper_review(app, store, connectors)
    register_workspace(app, workspace)
    register_animation(app, store, connectors, jobs)
    motion_render=register_inserts(app, store, jobs, connectors)

    @app.middleware("http")
    async def local_mutations(request: Request, call_next):
        if request.url.path.startswith("/api/") and request.method not in ("GET", "HEAD", "OPTIONS"):
            if request.headers.get("x-docos-request") != "1":
                return JSONResponse({"detail": "Brak nagłówka żądania Studio"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(Conflict)
    async def conflict(request, error):
        return JSONResponse({"detail": str(error)}, status_code=409)

    @app.exception_handler(FileNotFoundError)
    async def not_found(request, error):
        return JSONResponse({"detail": "Nie znaleziono projektu lub pliku"}, status_code=404)

    @app.exception_handler(ValueError)
    async def bad_request(request, error):
        return JSONResponse({"detail": str(error)[:2500]}, status_code=422)

    @app.exception_handler(subprocess.CalledProcessError)
    async def process_error(request, error):
        return JSONResponse({"detail": "Nie udało się odczytać medium. Sprawdź format i dostępność FFmpeg."}, status_code=422)

    @app.get("/api/health")
    def health():
        return {"ok": True, "version": "0.2.0", "ffmpeg": bool(shutil.which("ffmpeg")), "ffprobe": bool(shutil.which("ffprobe")),
                "ai": bool(connectors.config().get("ai_base_url") or shutil.which("claude")),
                "image": image_python().is_file(), "voice": voice_python().is_file() and (voice_ref().is_file() or bool(voices.list()))}

    def image_python():
        return Path(os.environ.get("DOCOS_IMAGE_PYTHON", REPO / "pilot" / ".venv" / ("Scripts/python.exe" if os.name=="nt" else "bin/python")))

    def voice_python():
        return Path(os.environ.get("DOCOS_TTS_PYTHON", REPO / "pilot" / ".venv-tts" / ("Scripts/python.exe" if os.name=="nt" else "bin/python")))

    def voice_ref():
        return Path(os.environ.get("DOCOS_VOICE_REF", REPO / "pilot" / "assets" / "ref_clean.wav"))

    @app.get("/api/projects")
    def list_projects(include_archived: bool = False):
        return store.list(include_archived=include_archived)

    @app.post("/api/projects")
    def new_project(body: dict):
        return workspace.new_project(body)

    @app.get("/api/projects/{project_id}")
    def get_project(project_id: str):
        return store.get(project_id)

    @app.patch("/api/projects/{project_id}")
    def patch_project(project_id: str, body: dict):
        return store.patch(project_id, int(body["expected_revision"]), body.get("changes", {}))

    @app.post("/api/projects/{project_id}/story/approve")
    def approve_story(project_id: str, body: dict):
        def approve(p):
            if any(not p.story.get(k, "").strip() for k in ("central_question", "hook", "payoff", "thesis")):
                raise ValueError("Uzupełnij pytanie, hook, tezę i odpowiedź")
            if not p.demo and not any(f.status == "VERIFIED" and f.source and (f.url or f.source_id) for f in p.facts):
                raise ValueError("Dodaj co najmniej jeden sprawdzony fakt ze źródłem i adresem")
            p.story["approved_at"] = now(); p.story["approved_by"] = "Autor projektu"
            p.story["status"] = "APPROVED"; p.story["approved_hash"] = story_hash(p)
        approved = store.mutate(project_id, int(body["expected_revision"]), approve)
        atomic_json(store.folder(project_id)/"approvals"/(f"r{approved.revision:08}.json"),approved.model_dump())
        return approved

    @app.get("/api/projects/{project_id}/history")
    def history(project_id: str):
        return store.history(project_id)

    @app.post("/api/projects/{project_id}/history/{direction}")
    def restore(project_id: str, direction: str, body: dict):
        if direction not in ("undo", "redo"):
            raise ValueError("Nieznana operacja historii")
        return store.restore(project_id, int(body["expected_revision"]), direction)

    @app.post("/api/projects/{project_id}/edits")
    def edit(project_id: str, body: dict):
        origin = body.get("origin", "manual")
        if origin not in ("manual", "ai"):
            raise ValueError("Nieznane źródło operacji")
        return store.mutate(project_id, int(body["expected_revision"]), lambda p: apply_operations(p, body["operations"], origin))

    @app.post("/api/projects/{project_id}/scenes/{scene_id}/to-timeline")
    def scene_to_timeline(project_id: str, scene_id: str, body: dict):
        def add(p):
            scene = next(s for s in p.scenes if s.id == scene_id)
            if scene.template == "paper-theatre":
                from studio_core.paper_theatre_review import require_approved
                require_approved(store, p, scene)
            if not scene.asset_id and scene.template == "media":
                raise ValueError("Najpierw wybierz materiał do ujęcia")
            clips = [c for c in p.sequence.clips if c.scene_id == scene_id and c.track_id == "v1"]
            existing = clips[0] if clips else None
            if existing:
                ops = [{"type": "update_clip", "clip_id": c.id, "changes": {"asset_id": scene.asset_id, "template": scene.template, "parameters": scene.parameters, "asset_ids": scene.asset_ids, "fact_ids": scene.fact_ids,
                        **({"title": scene.title, "animation": scene.animation} if body.get("sync_shot") else {}),
                        **({"start": scene.start, "duration": scene.duration} if len(clips) == 1 and body.get("sync_timing") else {})}} for c in clips]
            else:
                ops = [{"type": "add_clip", "clip": Clip(track_id="v1", scene_id=scene.id, asset_id=scene.asset_id, title=scene.title,
                                                             start=scene.start, duration=scene.duration, animation=scene.animation, template=scene.template, parameters=scene.parameters, asset_ids=scene.asset_ids, fact_ids=scene.fact_ids).model_dump()}]
            apply_operations(p, ops)
        return store.mutate(project_id, int(body["expected_revision"]), add)

    @app.post("/api/projects/import")
    async def import_project(file: UploadFile):
        data = await file.read(8 * 1024 * 1024 + 1)
        if len(data) > 8 * 1024 * 1024:
            raise ValueError("Projekt przekracza osiem megabajtów")
        raw = json.loads(data)
        p = import_content(raw)
        return store.create(p)

    @app.get("/api/projects/{project_id}/download")
    def download_project(project_id: str):
        p = store.get(project_id)
        return Response(json.dumps(p.model_dump(), ensure_ascii=False, indent=2), media_type="application/json",
                        headers={"Content-Disposition": 'attachment; filename="project.json"'})

    @app.get("/api/projects/{project_id}/bundle")
    def bundle(project_id: str, max_asset_mb: int=300):
        if not 1<=max_asset_mb<=2048: raise ValueError("Limit pliku od 1 do 2048 MB")
        return FileResponse(export_bundle(store, store.get(project_id),max_asset_mb=max_asset_mb), media_type="application/zip", filename="docos-project.zip")

    @app.post("/api/projects/import-bundle")
    async def upload_bundle(file: UploadFile):
        with tempfile.NamedTemporaryFile(suffix=".zip") as temporary:
            length = 0
            while chunk := await file.read(1024 * 1024):
                length += len(chunk)
                if length > MAX_BUNDLE:
                    raise ValueError("Pakiet przekracza dwa gigabajty")
                temporary.write(chunk)
            temporary.flush()
            return import_bundle(store, Path(temporary.name))

    @app.post("/api/projects/{project_id}/media")
    async def upload(project_id: str, file: UploadFile):
        store.get(project_id)
        with tempfile.NamedTemporaryFile() as tmp:
            total = 0
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_UPLOAD:
                    raise ValueError("Maksymalny rozmiar materiału to 300 MB")
                tmp.write(chunk)
            tmp.flush()
            asset, source = import_media(store, project_id, Path(tmp.name), file.filename or "file")
        return {"asset": asset, "source": source, "project": store.get(project_id)}

    @app.get("/api/projects/{project_id}/media/{asset_id}")
    def media(project_id: str, asset_id: str, thumbnail: bool = False):
        path = asset_path(store, project_id, asset_id, thumbnail)
        return FileResponse(path,filename=path.name) if path.suffix in (".html",".xml") else FileResponse(path)

    @app.get("/api/connectors")
    def list_connectors():
        return connectors.catalog()

    @app.get("/api/settings")
    def get_settings():
        c = connectors.config()
        return {"pixabay_configured": bool(c.get("pixabay_key")), "pexels_configured": bool(c.get("pexels_key")), "ai_configured": bool(c.get("ai_key")),
                "ai_request_cost":c.get("ai_request_cost",0),
                "ai_base_url": c.get("ai_base_url", ""), "ai_model": c.get("ai_model", ""),
                 "paper_image_configured": bool(c.get("paper_image_key")),
                 "paper_image_model": c.get("paper_image_model", "gpt-image-2.5-sunburst"),
                 "paper_image_request_cost": c.get("paper_image_request_cost", 0),
                 "custom": [{k:v for k,v in x.items() if k!="headers"}|{"authenticated":bool(x.get("headers"))} for x in c.get("custom", [])]}

    @app.patch("/api/settings")
    def settings(body: dict):
        connectors.save(body)
        return get_settings()

    @app.get("/api/search")
    def search(provider: str, q: str, kind: str = "image", page: int = 1):
        try:
            return connectors.search(provider, q, kind, page)
        except (httpx_error_types()) as error:
            return JSONResponse({"detail": "Źródło nie odpowiedziało poprawnie. Sprawdź połączenie lub klucz API."}, status_code=502)

    @app.post("/api/projects/{project_id}/sources")
    def add_source(project_id: str, body: dict):
        result = body.get("result", {})
        source = Source(title=str(result.get("title") or "Źródło"), provider=str(result.get("provider", "custom")),
                        url=str(result.get("url", "")), author=str(result.get("author", "")), edition=str(result.get("edition", "")),
                        identifier=str(result.get("identifier", "")), text=str(result.get("description", "")), accessed_at=now(),metadata={k:result[k] for k in ("preview_url","access","language","published_at","pages") if k in result})
        return store.mutate(project_id, int(body["expected_revision"]), lambda p: p.sources.append(source))

    @app.post("/api/projects/{project_id}/fetch")
    def fetch_medium(project_id: str, body: dict):
        result = body.get("result", {})
        url = str(result.get("download_url") or body.get("url") or "")
        provider=next((x for x in connectors.config().get("custom",[]) if x["id"]==result.get("provider")),None)
        headers=provider.get("headers") if provider and urlparse(provider["url"]).netloc==urlparse(url).netloc else None
        content, content_type, final_url = get_bytes(url, limit=MAX_UPLOAD,headers=headers)
        suffix = Path(urlparse(final_url).path).suffix.lower()
        if not suffix or suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mov", ".wav", ".mp3", ".pdf", ".epub", ".txt", ".md", ".ogv"}:
            suffix = {"image/jpeg": ".jpg", "image/png": ".png", "video/mp4": ".mp4", "application/pdf": ".pdf"}.get(content_type.split(";")[0], "")
        if not suffix:
            if "html" in content_type:
                suffix=".html"
            elif "xml" in content_type:
                suffix=".xml"
            else:
                raise ValueError("Ten adres nie prowadzi do obsługiwanego materiału")
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content); tmp.flush()
            from studio_core.media import HTMLMetadata
            html_meta=HTMLMetadata.extract(content.decode("utf-8","replace")) if suffix==".html" else {}
            asset, source = import_media(store, project_id, Path(tmp.name), str(result.get("title") or "internet")[:100].replace("/", "_") + suffix,
                                         {"source_url": result.get("url") or final_url, "author": result.get("author", ""), "license": result.get("license", ""), "license_url": result.get("license_url", ""),"provenance":{"provider":result.get("provider","url"),"download_url":final_url,"retrieved_at":now(),"variant":result.get("selected_variant","")}})
        if source:
            current=store.get(project_id)
            def metadata(p):
                nonlocal source
                source=next(s for s in p.sources if s.asset_id==asset.id)
                source.provider=str(result.get("provider","url"));source.title=str(result.get("title") or html_meta.get("title") or source.title)
                source.author=str(result.get("author") or html_meta.get("author") or source.author);source.edition=str(result.get("edition",""));source.identifier=str(result.get("identifier",""))
                source.metadata={**source.metadata,**html_meta,**{k:result[k] for k in ("published_at","preview_url","access") if k in result}}
            store.mutate(project_id,current.revision,metadata)
        return {"asset": asset, "source": source, "project": store.get(project_id)}

    @app.post("/api/projects/{project_id}/assistant/prompt")
    def assistant_prompt(project_id: str, body: dict):
        p=store.get(project_id)
        return {"prompt": editing_prompt(p, str(body.get("command", "")), scope_selection(p,body))+"\nDODATKOWE OGRANICZENIA: "+json.dumps(body.get("constraints",{}),ensure_ascii=False),"base_revision":p.revision}

    @app.post("/api/projects/{project_id}/writer/{kind}/{action}")
    def writing(project_id: str, kind: str, action: str, body: dict):
        p = store.get(project_id)
        p.topic_history = store.channel_titles(p)
        if action == "prompt":
            return {"prompt": writer.prompt(p, kind), "base_revision": p.revision}
        if action == "generate":
            return {"response": complete(connectors, writer.prompt(p, kind),store=store,project=p), "base_revision": p.revision}
        if action == "import":
            if int(body.get("base_revision", -1)) != p.revision:
                raise Conflict("Propozycja AI pochodzi z innej rewizji. Wygeneruj aktualny prompt przed przyjęciem.")
            return store.mutate(project_id, int(body["base_revision"]), lambda p: writer.import_response(p, kind, str(body["response"])))
        raise ValueError("Nieznana operacja scenopisarska")

    @app.post("/api/projects/{project_id}/assistant/propose")
    def assistant_propose(project_id: str, body: dict):
        p = store.get(project_id)
        selection=scope_selection(p,body)
        if body.get("response"):
            if int(body.get("base_revision",-1))!=p.revision: raise Conflict("Propozycja montażu pochodzi z innej rewizji")
            return enforce_range(p,parse_proposal(body["response"], p, selection),body)
        proposal=parse_proposal(complete(connectors,editing_prompt(p,str(body.get("command","")),selection)+"\nOGRANICZENIA: "+json.dumps(body.get("constraints",{}),ensure_ascii=False),store=store,project=p),p,selection)
        return enforce_range(p,proposal,body)

    @app.get("/api/projects/{project_id}/check")
    def check(project_id: str):
        return check_project(store, store.get(project_id))

    @app.post("/api/projects/{project_id}/render")
    def start_render(project_id: str, body: dict):
        p = store.get(project_id)
        if p.revision != int(body["expected_revision"]):
            raise Conflict("Projekt zmienił się przed renderem")
        if body.get("operations"):
            proposal=parse_proposal(json.dumps({"description":"Podgląd propozycji","operations":body["operations"]}),p,scope_selection(p,body))
            apply_operations(p,proposal["operations"],"ai")
        from studio_core.paper_theatre_review import require_export_approval
        require_export_approval(store, p)
        preview = body.get("quality", "preview") == "preview"
        final = body.get("mode") == "final"
        if final and body.get("operations"): raise ValueError("Najpierw przyjmij propozycję przed eksportem publikacyjnym")
        if final and check(project_id)["blocking"]:
            raise ValueError("Rozwiąż uwagi kontroli albo wybierz eksport roboczy")
        p.voice_profile={**p.voice_profile,"reference_sha256":voice_config(p,Scene())["reference_sha256"]}
        def task(job_id, progress, cancel):
            output = store.folder(project_id) / "exports" / (job_id + ".mp4")
            output.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(output.with_suffix(".json"), p.model_dump())
            render(store, p, output, progress, cancel, preview=preview, start_frame=int(body.get("start_frame",0)), end_frame=body.get("end_frame"))
            return {"url": f"/api/jobs/{job_id}/output", "filename": output.name, "revision": p.revision, "mode": "final" if final else "draft"}
        return jobs.submit(project_id, p.revision, "preview" if preview else "render", task,request={"action":"render","body":body},snapshot=p.model_dump())

    @app.post("/api/projects/{project_id}/generate/{scene_id}/{kind}")
    def generate(project_id: str, scene_id: str, kind: str, body: dict):
        p = store.get(project_id)
        if body.get("_retry_job"):
            previous=jobs.get(body["_retry_job"])
            if previous["project_id"]!=project_id or previous["kind"]!=kind or previous["status"] not in ("FAILED","CANCELLED","INTERRUPTED"):raise ValueError("Niepoprawna migawka ponawianego zadania")
            p=Project.model_validate(json.loads((root/"job-inputs"/(previous["id"]+".json")).read_text()))
        if "expected_revision" in body and int(body["expected_revision"])!=p.revision: raise Conflict("Projekt zmienił się przed generowaniem")
        active=[j for j in jobs.list(project_id) if j["status"] in ("QUEUED","RUNNING","CANCEL_REQUESTED")]
        if len(active)>=p.budget.get("max_jobs",20): raise ValueError("Osiągnięto limit zadań automatyzacji projektu")
        scene = next((s for s in p.scenes if s.id == scene_id), None)
        if not scene or scene.locked:
            raise ValueError("Ujęcie nie istnieje lub jest zablokowane")
        if kind == "voice" and scene.lock_narration or kind == "image" and scene.lock_media:
            raise ValueError("Ten element ujęcia jest zablokowany")
        profile = voice_config(p, scene)
        reference = voices.reference({**p.voice_profile, **scene.voice_profile})
        if kind == "voice" and not scene.sentences:
            p = store.mutate(project_id,p.revision,lambda project: None)
            scene = next(s for s in p.scenes if s.id == scene_id)
        if kind=="voice":p.voice_profile={**p.voice_profile,"reference_sha256":voice_config(p,Scene())["reference_sha256"]}
        if kind == "image" and not image_python().is_file():
            raise ValueError("Skonfiguruj środowisko obrazów: DOCOS_IMAGE_PYTHON; instrukcja w docs/STUDIO.md")
        if kind == "voice" and (not voice_python().is_file() or not reference.is_file()):
            raise ValueError("Skonfiguruj DOCOS_TTS_PYTHON i DOCOS_VOICE_REF albo wgraj własne nagranie")
        if kind not in ("image", "voice"):
            raise ValueError("Nieobsługiwany typ generowania")
        if kind == "image" and not scene.prompt.strip() or kind == "voice" and not scene.narration.strip():
            raise ValueError("Uzupełnij prompt lub narrację")
        if (len(scene.narration.split())/2.5 if kind=="voice" else scene.duration/fps(p))>p.budget.get("max_seconds",3600):
            raise ValueError("Materiał przekracza limit czasu automatyzacji projektu")
        def task(job_id, progress, cancel):
            work = store.folder(project_id) / "jobs" / job_id; work.mkdir(parents=True, exist_ok=True)
            if kind=="voice" and hashlib.sha256(reference.read_bytes()).hexdigest()!=profile["reference_sha256"]:raise ValueError("Próbka głosu zmieniła się od zlecenia. Wybierz aktualny profil i ponów generowanie.")
            if kind == "image":
                output = work / "image.png"
                config = image_config(scene)
                cmd = [str(image_python()), "-I", str(REPO / "studio_workers" / "image_worker.py"), str(output), "--prompt", image_prompt(p,scene),
                       "--seed",str(int(config["seed"])),"--width",str(int(config["width"])),"--height",str(int(config["height"])),"--steps",str(int(config["steps"]))]
            else:
                snapshot = work / "voice-input.json"
                sentences = [sentence for sentence in scene.sentences if not body.get("sentence_id") or sentence.id == body["sentence_id"]]
                if not sentences:
                    raise ValueError("Nie ma takiego zdania")
                atomic_json(snapshot, {"narration": scene.narration, "language": p.language, "config": profile,
                                      "sentences": [sentence.model_dump() | {"spoken_text":spoken(p,sentence.text),"input_hash":sentence_hash(p,scene,sentence.text)} for sentence in sentences],
                                      "cache_dir":str(root/"cache/voice")})
                output = work / "voice" / "B01.wav"
                lang = {"Polish": "pl", "English": "en"}.get(p.language, p.language)
                cmd = [str(voice_python()), "-I", str(REPO / "studio_workers" / "voice_worker.py"), str(snapshot), str(reference), str(output), "--language", lang]
            log = work / "worker.log"
            with log.open("w+") as stream:
                process = subprocess.Popen(cmd, stdout=stream, stderr=stream)
                previous_progress=""
                while process.poll() is None:
                    with log.open() as observed:
                        tail=observed.read()[-64000:]
                    parts=re.findall(r"(?:STEP|SENTENCE) (\d+)/(\d+)",tail)
                    if parts and str(parts[-1])!=previous_progress:
                        done,total=map(int,parts[-1]);progress(.05+.8*done/max(1,total),f"{'Krok obrazu' if kind=='image' else 'Zdanie'} {done}/{total}");previous_progress=str(parts[-1])
                    if cancel.wait(.25):
                        process.terminate()
                        try: process.wait(timeout=4)
                        except subprocess.TimeoutExpired: process.kill(); process.wait()
                        raise InterruptedError()
                if process.returncode or not output.is_file():
                    stream.seek(0)
                    raise ValueError("Generator: " + stream.read()[-1800:])
            progress(.9, "Zapisywanie wariantu")
            if kind=="voice" and hashlib.sha256(reference.read_bytes()).hexdigest()!=profile["reference_sha256"]:raise ValueError("Próbka głosu zmieniła się podczas generowania; wynik nie został przypisany")
            runtime=json.loads(output.with_suffix(".json").read_text()) if output.with_suffix(".json").exists() else {}
            measured=[]
            if kind=="voice" and not body.get("sentence_id"):
                manifest=json.loads(output.with_suffix(".json").read_text())
                measured=[{"word":item["text"],"start":item["start"],"end":item["end"],"method":"measured-sentence"} for item in manifest["sentences"]]
            asset, _ = import_media(store, project_id, output, output.name,
                                    {"prompt": scene.prompt if kind == "image" else scene.narration,
                                     "provenance": {"job_id": job_id, "input_revision": p.revision, "kind": kind, "language": p.language,"execution_device":runtime.get("device","unknown"),"model":runtime.get("model","unknown"), "config":profile if kind == "voice" else config, **({"voice_hash": sentence_hash(p,scene,sentences[0].text) if body.get("sentence_id") else voice_hash(p, scene),"sentences":measured} if kind == "voice" else {"image_hash":image_hash(p,scene),"effective_prompt":image_prompt(p,scene)})}})
            sentence_assets = []
            if kind == "voice":
                manifest = json.loads(output.with_suffix(".json").read_text())
                for item in manifest["sentences"]:
                    a,_ = import_media(store,project_id,Path(item["filename"]),"sentence.wav",{"prompt":item["text"],"provenance":{"kind":"voice_sentence","voice_hash":item["input_hash"],"config":profile}})
                    sentence_assets.append((item,a))
            current = store.get(project_id)
            def attach(project):
                found = next((s for s in project.scenes if s.id == scene_id), None)
                if found and not found.locked and not (found.lock_narration if kind == "voice" else found.lock_media):
                    if not body.get("sentence_id") and asset.id not in found.variants:
                        found.variants.append(asset.id)
                    for item,a in sentence_assets:
                        sentence = next((s for s in found.sentences if s.id == item["id"]),None)
                        if sentence and a.id not in sentence.variants:
                            sentence.variants.append(a.id)
                        if sentence and not sentence.asset_id and sentence_hash(project,found,sentence.text) == item["input_hash"]:
                            sentence.asset_id=a.id; sentence.input_hash=item["input_hash"]; sentence.duration=item["duration"]
                # Selection and timeline replacement stay explicit, even for the first variant.
            store.mutate(project_id, current.revision, attach)
            return {"asset_id": asset.id, "revision": p.revision}
        return jobs.submit(project_id, p.revision, kind, task,request={"action":"generate","scene_id":scene_id,"kind":kind,"body":{**{k:v for k,v in body.items() if k!="_retry_job"},"expected_revision":p.revision}},snapshot=p.model_dump())

    @app.get("/api/jobs")
    def list_jobs(project_id: str | None = None):
        return jobs.list(project_id)

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel_job(job_id: str):
        return jobs.cancel(job_id)

    @app.get("/api/jobs/{job_id}/output")
    def job_output(job_id: str):
        job = jobs.get(job_id)
        if job["status"] != "SUCCEEDED" or job["kind"] not in ("render", "preview", "animatic"):
            raise FileNotFoundError()
        return FileResponse(store.folder(job["project_id"]) / "exports" / (job_id + ".mp4"), media_type="video/mp4")

    @app.get("/api/events")
    async def events(request: Request):
        import asyncio
        async def stream():
            previous = ""
            while not await request.is_disconnected():
                payload = json.dumps(jobs.list(), ensure_ascii=False)
                if payload != previous:
                    yield "event: jobs\ndata: " + payload + "\n\n"
                    previous = payload
                else:
                    yield ": heartbeat\n\n"
                await asyncio.sleep(1)
        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    from .production import register
    from .development import register_development
    register_development(app,store,connectors)
    register(app,store,jobs,connectors,REPO,{"render":start_render,"generate":generate,"writer":writing,"fetch":fetch_medium,"motion":motion_render})
    dist = REPO / "apps" / "studio" / "dist"
    if dist.exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="studio")
    return app


def httpx_error_types():
    import httpx
    return (httpx.HTTPError, OSError)
