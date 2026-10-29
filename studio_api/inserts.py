"""Revision-checked insert editing, AI proposals and render handoff."""
import json

from studio_core.models import Clip, Project
from studio_core.inserts import MotionInsert, find_insert, definition, signature, require_ready
from studio_core.store import Conflict
from studio_core.assistant import complete
from studio_timeline.operations import apply_operations
from studio_workers.motion import run_motion, runtime_ready


def register_inserts(app, store, jobs, connectors):
    @app.get("/api/motion/status")
    def status():
        return {"installed": runtime_ready(), "templates": ["photo", "compare", "chart", "quote", "chapter"]}

    @app.post("/api/projects/{project_id}/inserts")
    def save(project_id: str, body: dict):
        item = MotionInsert.model_validate(body["insert"])
        item.rendered_asset_id = None
        item.rendered_signature = ""
        def change(p):
            previous = next((i for i in p.inserts if i.id == item.id), None)
            if previous and signature(p, previous) == signature(p, item):
                item.rendered_asset_id = previous.rendered_asset_id
                item.rendered_signature = previous.rendered_signature
            p.inserts = [item if i.id == item.id else i for i in p.inserts] if previous else [*p.inserts, item]
        return store.mutate(project_id, int(body["expected_revision"]), change)

    @app.post("/api/projects/{project_id}/inserts/{insert_id}/delete")
    def delete(project_id: str, insert_id: str, body: dict):
        def change(p):
            find_insert(p, insert_id)
            p.inserts = [i for i in p.inserts if i.id != insert_id]
        # Existing renders and timeline clips are immutable and remain usable.
        return store.mutate(project_id, int(body["expected_revision"]), change)

    @app.post("/api/projects/{project_id}/inserts/{insert_id}/render")
    def render(project_id: str, insert_id: str, body: dict):
        p = store.get(project_id)
        if body.get("_retry_job"):
            old=jobs.get(body["_retry_job"])
            if old["project_id"]!=project_id or old["kind"]!="motion" or old["status"] not in ("FAILED","CANCELLED","INTERRUPTED"):raise ValueError("Niepoprawna migawka wstawki")
            p=Project.model_validate(json.loads((store.root/"job-inputs"/(old["id"]+".json")).read_text()))
        if p.revision != int(body["expected_revision"]):
            raise Conflict("Projekt zmienił się przed renderem")
        require_ready(p, find_insert(p, insert_id))
        if not runtime_ready():
            raise ValueError("Zainstaluj zależności aplikacji: npm --prefix apps/studio ci")
        return jobs.submit(project_id, p.revision, "motion", lambda job, progress, cancel: run_motion(store, p, insert_id, job, progress, cancel),request={"action":"motion","insert_id":insert_id,"body":{"expected_revision":p.revision}},snapshot=p.model_dump())

    @app.post("/api/projects/{project_id}/inserts/{insert_id}/to-timeline")
    def timeline(project_id: str, insert_id: str, body: dict):
        def change(p):
            item = find_insert(p, insert_id)
            if not item.rendered_asset_id or item.rendered_signature != signature(p, item):
                raise ValueError("Wyrenderuj aktualną wersję wstawki przed dodaniem do montażu")
            clip = Clip(track_id=str(body.get("track_id", "v1")), asset_id=item.rendered_asset_id,
                        title=item.title, start=body.get("start", 0), duration=item.duration)
            apply_operations(p, [{"type": "add_clip", "clip": clip.model_dump()}])
        return store.mutate(project_id, int(body["expected_revision"]), change)

    @app.post("/api/projects/{project_id}/inserts/{insert_id}/assistant/{action}")
    def assistant(project_id: str, insert_id: str, action: str, body: dict):
        p = store.get(project_id)
        item = find_insert(p, insert_id)
        command = str(body.get("command", ""))[:4000]
        allowed_images = [a.id for a in p.assets if a.kind == "image"]
        prompt = ("Adjust the following motion insert according to the user's request. Return only one JSON object, no JavaScript. "
                  "Do not invent quotes, sources or chart values. Keep data and text unless the user explicitly provides replacements. "
                  "Use only image_ids from the allowed list. Duration is in frames. Do not change id. Schema: "
                  + json.dumps(MotionInsert.model_json_schema(), ensure_ascii=False)
                  + "\nCurrent insert: " + json.dumps(definition(item), ensure_ascii=False)
                  + "\nFPS: " + str(p.sequence.fps_num / p.sequence.fps_den)
                  + "\nAllowed images: " + json.dumps(allowed_images)
                  + "\nUser request: " + command)
        if action == "prompt":
            return {"prompt": prompt,"base_revision":p.revision}
        if action not in ("generate", "import"):
            raise ValueError("Nieznana operacja asystenta wstawek")
        if action=="import" and int(body.get("base_revision",-1))!=p.revision:raise Conflict("Propozycja wstawki pochodzi z innej rewizji")
        raw = complete(connectors, prompt,store=store,project=p) if action == "generate" else str(body.get("response", ""))
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        candidate = MotionInsert.model_validate(json.loads(text))
        if candidate.id != item.id:
            raise ValueError("AI nie może zmienić identyfikatora wstawki")
        candidate.rendered_asset_id = None; candidate.rendered_signature = ""
        Project.model_validate(p.model_dump() | {"inserts": [candidate.model_dump() if i.id == item.id else i.model_dump() for i in p.inserts]})
        return {"insert": candidate, "base_revision": p.revision}

    return render
