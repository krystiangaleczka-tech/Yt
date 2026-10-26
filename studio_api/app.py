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

from studio_core.models import Project, Scene, Clip, Source, Fact, from_docos, uid, fps, duration
from studio_core.store import ProjectStore, Conflict, atomic_json, now, story_hash
from studio_core.media import import_media, asset_path, PlainText, MAX_UPLOAD
from studio_core.demo import create_demo
from studio_core.assistant import editing_prompt, parse_proposal, generate_proposal
from studio_core.assistant import complete
from studio_core import writer
from studio_core.bundles import export_bundle, import_bundle, MAX_BUNDLE
from studio_connectors.sources import Connectors, get_bytes
from studio_timeline.operations import apply_operations
from studio_timeline.render import render
from studio_workers.jobs import Jobs
from studio_api.inserts import register_inserts

REPO = Path(__file__).resolve().parents[1]


def create_app(root: Path | None = None, *, seed_demo=True) -> FastAPI:
    root = root or Path(os.environ.get("DOCOS_STUDIO_HOME", REPO / ".docos-studio"))
    store = ProjectStore(root)
    connectors = Connectors(root)
    jobs = Jobs(root)
    if seed_demo and not store.list():
        create_demo(store)

    @asynccontextmanager
    async def lifespan(app):
        yield
        jobs.close()

    app = FastAPI(title="DocOS Studio", version="0.1.0", lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])
    app.state.store = store; app.state.jobs = jobs; app.state.connectors = connectors
    register_inserts(app, store, jobs, connectors)

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
        return {"ok": True, "version": "0.1.0", "ffmpeg": bool(shutil.which("ffmpeg")), "ffprobe": bool(shutil.which("ffprobe")),
                "ai": bool(connectors.config().get("ai_base_url") or shutil.which("claude")),
                "image": image_python().is_file(), "voice": voice_python().is_file() and voice_ref().is_file()}

    def image_python():
        return Path(os.environ.get("DOCOS_IMAGE_PYTHON", REPO / "pilot" / ".venv" / "bin" / "python"))

    def voice_python():
        return Path(os.environ.get("DOCOS_TTS_PYTHON", REPO / "pilot" / ".venv-tts" / "bin" / "python"))

    def voice_ref():
        return Path(os.environ.get("DOCOS_VOICE_REF", REPO / "pilot" / "assets" / "ref_clean.wav"))

    @app.get("/api/projects")
    def list_projects():
        return store.list()

    @app.post("/api/projects")
    def new_project(body: dict):
        title = str(body.get("title") or "Nowy dokument").strip()
        return store.create(Project(title=title, language=str(body.get("language") or "pl")))

    @app.get("/api/projects/{project_id}")
    def get_project(project_id: str):
        return store.get(project_id)

    @app.patch("/api/projects/{project_id}")
    def patch_project(project_id: str, body: dict):
        changes = body.get("changes", {})
        allowed = {"title", "language", "channel", "niche", "facts", "sources", "story", "scenes"}
        if not set(changes) <= allowed:
            raise ValueError("Oś czasu i materiały mają osobne operacje")
        def change(p):
            candidate = Project.model_validate(p.model_dump() | changes)
            if any(s.locked and next((x for x in candidate.scenes if x.id == s.id), None) not in (s, s.model_copy(update={"locked": False})) for s in p.scenes):
                raise ValueError("Odblokuj ujęcie przed zmianą jego treści")
            if "story" in changes:
                candidate.story["status"] = "DRAFT"; candidate.story["approved_hash"] = ""
            for key in changes:
                setattr(p, key, getattr(candidate, key))
        return store.mutate(project_id, int(body["expected_revision"]), change)

    @app.post("/api/projects/{project_id}/story/approve")
    def approve_story(project_id: str, body: dict):
        def approve(p):
            if any(not p.story.get(k, "").strip() for k in ("central_question", "hook", "payoff", "thesis")):
                raise ValueError("Uzupełnij pytanie, hook, tezę i odpowiedź")
            if not p.demo and not any(f.status == "VERIFIED" and f.source and f.url for f in p.facts):
                raise ValueError("Dodaj co najmniej jeden sprawdzony fakt ze źródłem i adresem")
            p.story["status"] = "APPROVED"; p.story["approved_hash"] = story_hash(p)
        return store.mutate(project_id, int(body["expected_revision"]), approve)

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
            if not scene.asset_id:
                raise ValueError("Najpierw wybierz materiał do ujęcia")
            clips = [c for c in p.sequence.clips if c.scene_id == scene_id and c.track_id == "v1"]
            existing = clips[0] if clips else None
            if existing:
                ops = [{"type": "update_clip", "clip_id": c.id, "changes": {"asset_id": scene.asset_id, "animation": scene.animation,
                        **({"start": scene.start, "duration": scene.duration} if len(clips) == 1 else {})}} for c in clips]
            else:
                ops = [{"type": "add_clip", "clip": Clip(track_id="v1", scene_id=scene.id, asset_id=scene.asset_id, title=scene.title,
                                                             start=scene.start, duration=scene.duration, animation=scene.animation).model_dump()}]
            apply_operations(p, ops)
        return store.mutate(project_id, int(body["expected_revision"]), add)

    @app.post("/api/projects/import")
    async def import_project(file: UploadFile):
        data = await file.read(8 * 1024 * 1024 + 1)
        if len(data) > 8 * 1024 * 1024:
            raise ValueError("Projekt przekracza osiem megabajtów")
        raw = json.loads(data)
        p = from_docos(raw)
        # JSON imports cannot grant file access or inherit trusted approval.
        p.id = uid("prj_"); p.assets = []; p.sequence.clips = []
        for scene in p.scenes:
            scene.asset_id = None; scene.voice_asset_id = None; scene.variants = []
        for item in p.inserts:
            item.image_ids = []; item.rendered_asset_id = None; item.rendered_signature = ""
        p.story["status"] = "DRAFT"; p.story["approved_hash"] = ""
        return store.create(p)

    @app.get("/api/projects/{project_id}/download")
    def download_project(project_id: str):
        p = store.get(project_id)
        return Response(json.dumps(p.model_dump(), ensure_ascii=False, indent=2), media_type="application/json",
                        headers={"Content-Disposition": 'attachment; filename="project.json"'})

    @app.get("/api/projects/{project_id}/bundle")
    def bundle(project_id: str):
        return FileResponse(export_bundle(store, store.get(project_id)), media_type="application/zip", filename="docos-project.zip")

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
        return FileResponse(path)

    @app.get("/api/connectors")
    def list_connectors():
        return connectors.catalog()

    @app.get("/api/settings")
    def get_settings():
        c = connectors.config()
        return {"pixabay_configured": bool(c.get("pixabay_key")), "pexels_configured": bool(c.get("pexels_key")), "ai_configured": bool(c.get("ai_key")),
                "ai_base_url": c.get("ai_base_url", ""), "ai_model": c.get("ai_model", ""), "custom": c.get("custom", [])}

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
                        identifier=str(result.get("identifier", "")), text=str(result.get("description", "")), accessed_at=now())
        return store.mutate(project_id, int(body["expected_revision"]), lambda p: p.sources.append(source))

    @app.post("/api/projects/{project_id}/fetch")
    def fetch_medium(project_id: str, body: dict):
        result = body.get("result", {})
        url = str(result.get("download_url") or body.get("url") or "")
        content, content_type, final_url = get_bytes(url, limit=MAX_UPLOAD)
        suffix = Path(urlparse(final_url).path).suffix.lower()
        if not suffix or suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mov", ".wav", ".mp3", ".pdf", ".epub", ".txt", ".md", ".ogv"}:
            suffix = {"image/jpeg": ".jpg", "image/png": ".png", "video/mp4": ".mp4", "application/pdf": ".pdf"}.get(content_type.split(";")[0], "")
        if not suffix:
            if "html" in content_type:
                text = PlainText.extract(content.decode("utf-8", "replace"))[:200000]
                source = Source(title=str(body.get("title") or result.get("title") or urlparse(final_url).hostname), provider="url", url=final_url,
                                text=text, accessed_at=now())
                p = store.get(project_id)
                updated = store.mutate(project_id, p.revision, lambda p: p.sources.append(source))
                return {"project": updated, "source": source, "asset": None}
            raise ValueError("Ten adres nie prowadzi do obsługiwanego materiału")
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content); tmp.flush()
            asset, source = import_media(store, project_id, Path(tmp.name), str(result.get("title") or "internet")[:100].replace("/", "_") + suffix,
                                         {"source_url": result.get("url") or final_url, "author": result.get("author", ""), "license": result.get("license", ""), "license_url": result.get("license_url", "")})
        return {"asset": asset, "source": source, "project": store.get(project_id)}

    @app.post("/api/projects/{project_id}/assistant/prompt")
    def assistant_prompt(project_id: str, body: dict):
        return {"prompt": editing_prompt(store.get(project_id), str(body.get("command", "")), body.get("selection", []))}

    @app.post("/api/projects/{project_id}/writer/{kind}/{action}")
    def writing(project_id: str, kind: str, action: str, body: dict):
        p = store.get(project_id)
        if action == "prompt":
            return {"prompt": writer.prompt(p, kind)}
        if action == "generate":
            return {"response": complete(connectors, writer.prompt(p, kind))}
        if action == "import":
            return store.mutate(project_id, int(body["expected_revision"]), lambda p: writer.import_response(p, kind, str(body["response"])))
        raise ValueError("Nieznana operacja scenopisarska")

    @app.post("/api/projects/{project_id}/assistant/propose")
    def assistant_propose(project_id: str, body: dict):
        p = store.get(project_id)
        if body.get("response"):
            return parse_proposal(body["response"], p, body.get("selection", []))
        return generate_proposal(connectors, p, str(body.get("command", "")), body.get("selection", []))

    @app.get("/api/projects/{project_id}/check")
    def check(project_id: str):
        p = store.get(project_id)
        issues = []
        if p.story.get("status") != "APPROVED" or p.story.get("approved_hash") != story_hash(p):
            issues.append({"type": "story", "severity": "warning", "message": "Historia czeka na zatwierdzenie"})
        if not p.sequence.clips:
            issues.append({"type": "timeline", "severity": "error", "message": "Oś czasu jest pusta"})
        for scene in p.scenes:
            if not scene.asset_id:
                issues.append({"type": "media", "severity": "warning", "scene_id": scene.id, "message": f"{scene.title}: brak wybranego obrazu"})
            if scene.narration and not scene.voice_asset_id:
                issues.append({"type": "voice", "severity": "warning", "scene_id": scene.id, "message": f"{scene.title}: brak nagrania narracji"})
        for clip in p.sequence.clips:
            if clip.asset_id and not asset_path(store, project_id, clip.asset_id).is_file():
                issues.append({"type": "file", "severity": "error", "message": f"Brakuje pliku klipu {clip.title}"})
        for a in p.assets:
            if a.source_url and not a.license and a.kind in ("image", "video"):
                issues.append({"type": "license", "severity": "warning", "message": f"Sprawdź warunki użycia: {a.name}"})
        return {"issues": issues, "duration": duration(p), "fps": fps(p)}

    @app.post("/api/projects/{project_id}/render")
    def start_render(project_id: str, body: dict):
        p = store.get(project_id)
        if p.revision != int(body["expected_revision"]):
            raise Conflict("Projekt zmienił się przed renderem")
        preview = body.get("quality", "preview") == "preview"
        final = body.get("mode") == "final"
        if final and check(project_id)["issues"]:
            raise ValueError("Rozwiąż uwagi kontroli albo wybierz eksport roboczy")
        def task(job_id, progress, cancel):
            output = store.folder(project_id) / "exports" / (job_id + ".mp4")
            output.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(output.with_suffix(".json"), p.model_dump())
            render(store, p, output, progress, cancel, preview=preview)
            return {"url": f"/api/jobs/{job_id}/output", "filename": output.name, "revision": p.revision, "mode": "final" if final else "draft"}
        return jobs.submit(project_id, p.revision, "preview" if preview else "render", task)

    @app.post("/api/projects/{project_id}/generate/{scene_id}/{kind}")
    def generate(project_id: str, scene_id: str, kind: str, body: dict):
        p = store.get(project_id)
        scene = next((s for s in p.scenes if s.id == scene_id), None)
        if not scene or scene.locked:
            raise ValueError("Ujęcie nie istnieje lub jest zablokowane")
        if kind == "image" and not image_python().is_file():
            raise ValueError("Skonfiguruj środowisko obrazów: DOCOS_IMAGE_PYTHON; instrukcja w docs/STUDIO.md")
        if kind == "voice" and (not voice_python().is_file() or not voice_ref().is_file()):
            raise ValueError("Skonfiguruj DOCOS_TTS_PYTHON i DOCOS_VOICE_REF albo wgraj własne nagranie")
        if kind not in ("image", "voice"):
            raise ValueError("Nieobsługiwany typ generowania")
        if kind == "image" and not scene.prompt.strip() or kind == "voice" and not scene.narration.strip():
            raise ValueError("Uzupełnij prompt lub narrację")
        def task(job_id, progress, cancel):
            work = store.folder(project_id) / "jobs" / job_id; work.mkdir(parents=True, exist_ok=True)
            if kind == "image":
                output = work / "image.png"
                cmd = [str(image_python()), "-I", str(REPO / "studio_workers" / "image_worker.py"), str(output), "--prompt", scene.prompt]
            else:
                snapshot = work / "voice-input.json"
                atomic_json(snapshot, {"narration": scene.narration, "language": p.language})
                output = work / "voice" / "B01.wav"
                lang = {"Polish": "pl", "English": "en"}.get(p.language, p.language)
                cmd = [str(voice_python()), "-I", str(REPO / "studio_workers" / "voice_worker.py"), str(snapshot), str(voice_ref()), str(output), "--language", lang]
            log = work / "worker.log"
            with log.open("w+") as stream:
                process = subprocess.Popen(cmd, stdout=stream, stderr=stream)
                while process.poll() is None:
                    if cancel.wait(.25):
                        process.terminate()
                        try: process.wait(timeout=4)
                        except subprocess.TimeoutExpired: process.kill(); process.wait()
                        raise InterruptedError()
                if process.returncode or not output.is_file():
                    stream.seek(0)
                    raise ValueError("Generator: " + stream.read()[-1800:])
            progress(.9, "Zapisywanie wariantu")
            asset, _ = import_media(store, project_id, output, output.name,
                                    {"prompt": scene.prompt if kind == "image" else scene.narration,
                                     "provenance": {"job_id": job_id, "input_revision": p.revision, "kind": kind, "language": p.language}})
            current = store.get(project_id)
            def attach(project):
                found = next((s for s in project.scenes if s.id == scene_id), None)
                if found and not found.locked and asset.id not in found.variants:
                    found.variants.append(asset.id)
                # Selection and timeline replacement stay explicit, even for the first variant.
            store.mutate(project_id, current.revision, attach)
            return {"asset_id": asset.id, "revision": p.revision}
        return jobs.submit(project_id, p.revision, kind, task)

    @app.get("/api/jobs")
    def list_jobs(project_id: str | None = None):
        return jobs.list(project_id)

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel_job(job_id: str):
        return jobs.cancel(job_id)

    @app.get("/api/jobs/{job_id}/output")
    def job_output(job_id: str):
        job = jobs.get(job_id)
        if job["status"] != "SUCCEEDED" or job["kind"] not in ("render", "preview"):
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

    dist = REPO / "apps" / "studio" / "dist"
    if dist.exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="studio")
    return app


def httpx_error_types():
    import httpx
    return (httpx.HTTPError, OSError)
