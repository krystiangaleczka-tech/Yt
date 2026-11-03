"""Paper Theatre re-cut endpoints: prompts, local model job, accept/revert."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from studio_core.store import Conflict
from studio_core import paper_theatre_recut as recut

PROGRESS = re.compile(r"^PROGRESS ([0-9.]+) (.*)$")


def run_worker(python: str, worker: Path, job_dir: Path, progress, cancel) -> None:
    """Run the image-environment worker; forward its PROGRESS lines; honour cancel."""
    log = job_dir / "worker.log"
    with log.open("w+") as stream:
        process = subprocess.Popen([python, "-I", str(worker), str(job_dir)], stdout=stream, stderr=subprocess.STDOUT)
        seen = 0
        while process.poll() is None:
            if cancel.wait(.5):
                process.terminate()
                try:
                    process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise InterruptedError()
            text = log.read_text(errors="replace")
            end = text.rfind("\n") + 1
            for line in text[seen:end].splitlines():
                match = PROGRESS.match(line.strip())
                if match:
                    progress(min(.9, float(match.group(1)) * .9), match.group(2))
            seen = max(seen, end)
        if process.returncode:
            raise ValueError("Worker wycinania: " + log.read_text(errors="replace")[-1500:])


def register_recut(app, store, jobs, repo: Path):
    worker = repo / "studio_workers" / "cutout_worker.py"

    def scene(pid, sid, revision=None):
        project = store.get(pid)
        if revision is not None and int(revision) != project.revision:
            raise Conflict("Projekt zmienił się od otwarcia panelu rozcinania")
        return project, recut.scene_of(project, sid)

    @app.get("/api/paper-theatre/recut/runtime")
    def recut_runtime():
        return recut.runtime(repo)

    @app.get("/api/projects/{pid}/paper-theatre/{sid}/recut")
    def recut_state(pid: str, sid: str):
        project, shot = scene(pid, sid)
        return recut.state(store, project, shot)

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/recut/settings")
    def recut_settings(pid: str, sid: str, body: dict):
        project, shot = scene(pid, sid, body.get("expected_revision"))
        w, h = recut.frame_size(store, project, shot)
        settings = recut.normalize_settings(body.get("settings"), shot, w, h)

        def save(p):
            target = next(s for s in p.scenes if s.id == sid)
            data = dict(target.generation.get(recut.KEY, {}))
            data["settings"] = settings
            target.generation = {**target.generation, recut.KEY: data}
        return store.mutate(pid, int(body["expected_revision"]), save)

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/recut/run")
    def recut_run(pid: str, sid: str, body: dict):
        project, shot = scene(pid, sid, body.get("expected_revision"))
        rt = recut.runtime(repo)
        if not rt["python_ready"]:
            raise ValueError("Brak środowiska modeli obrazu. Uruchom: python scripts/install_studio.py --with-models "
                             "albo ustaw DOCOS_IMAGE_PYTHON.")
        active = [x for x in jobs.list(pid) if x["status"] in ("QUEUED", "RUNNING", "CANCEL_REQUESTED")]
        if len(active) >= project.budget.get("max_jobs", 20):
            raise ValueError("Osiągnięto limit zadań tego projektu")
        base_revision = project.revision

        def run(job_id, progress, cancel):
            job_dir = store.folder(pid) / "jobs" / job_id
            current = store.get(pid)
            recut.write_job_input(store, current, recut.scene_of(current, sid), job_dir, rt["models_dir"])
            progress(.01, "Przygotowanie wycinków")
            run_worker(rt["python"], worker, job_dir, progress, cancel)
            progress(.92, "Zapis nowych wycinków do biblioteki")
            result = recut.import_outputs(store, pid, sid, job_dir / "out", job_id=job_id, base_revision=base_revision)
            return {"scene_id": sid, "layers": len(result["map"]), "leftovers": len(result["leftovers"]),
                    "extra": len(result["extra"]), "warnings": result["report"].get("warnings", [])}
        return jobs.submit(pid, base_revision, "image", run,
                           request={"action": "paper-theatre-recut", "scene_id": sid,
                                    "body": {"expected_revision": base_revision}},
                           snapshot=project.model_dump())

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/recut/accept")
    def recut_accept(pid: str, sid: str, body: dict):
        return store.mutate(pid, int(body["expected_revision"]), lambda p: recut.accept(p, sid))

    @app.post("/api/projects/{pid}/paper-theatre/{sid}/recut/revert")
    def recut_revert(pid: str, sid: str, body: dict):
        return store.mutate(pid, int(body["expected_revision"]), lambda p: recut.revert(p, sid))
