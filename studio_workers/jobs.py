from __future__ import annotations

import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

from studio_core.models import uid
from studio_core.store import now,atomic_json


class Jobs:
    def __init__(self, root: Path):
        self.root=root
        self.path = root / "jobs.sqlite3"
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="docos")
        self.heavy_pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix="docos-model")
        self.heavy = threading.Semaphore(1)
        self.cancel_events = {}; self.tasks = {}
        with self.db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
            for job_id, data in db.execute("SELECT id,data FROM jobs").fetchall():
                job = json.loads(data)
                if job["status"] in ("QUEUED", "RUNNING", "CANCEL_REQUESTED"):
                    job.update(status="INTERRUPTED", message="Przerwano przy zamknięciu aplikacji; uruchom ponownie", updated_at=now())
                    db.execute("UPDATE jobs SET data=? WHERE id=?", (json.dumps(job), job_id))

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            with db:
                yield db
        finally:
            db.close()

    def get(self, job_id):
        with self.db() as db:
            row = db.execute("SELECT data FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise FileNotFoundError("Nie ma takiego zadania")
        return json.loads(row[0])

    def list(self, project_id=None):
        with self.db() as db:
            jobs = [json.loads(row[0]) for row in db.execute("SELECT data FROM jobs ORDER BY rowid DESC LIMIT 100")]
        return [job for job in jobs if not project_id or job["project_id"] == project_id]

    def update(self, job_id, **changes):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT data FROM jobs WHERE id=?", (job_id,)).fetchone()
            job = json.loads(row[0])
            if changes.get("status") == "CANCEL_REQUESTED" and job["status"] not in ("QUEUED", "RUNNING"):
                return
            job.update(changes, updated_at=now())
            db.execute("UPDATE jobs SET data=? WHERE id=?", (json.dumps(job), job_id))

    def submit(self, project_id, revision, kind, task, *, request=None, heavy=True,snapshot=None):
        job_id = uid("job_")
        if snapshot is not None:atomic_json(self.root/"job-inputs"/(job_id+".json"),snapshot)
        job = dict(id=job_id, project_id=project_id, revision=revision, kind=kind, status="QUEUED", progress=0,
                   message="W kolejce", result=None, request=request, created_at=now(), updated_at=now())
        with self.db() as db:
            db.execute("INSERT INTO jobs VALUES (?,?)", (job_id, json.dumps(job)))
        cancel = threading.Event(); self.cancel_events[job_id] = cancel
        self.tasks[job_id]=(task,heavy)
        def run():
            try:
                from contextlib import nullcontext
                with self.heavy if heavy else nullcontext():
                    if cancel.is_set():
                        raise InterruptedError()
                    self.update(job_id, status="RUNNING", message="Uruchamianie")
                    result = task(job_id, lambda value, message: self.update(job_id, progress=value, message=message), cancel)
                    if cancel.is_set():
                        raise InterruptedError()
                    self.update(job_id, status="SUCCEEDED", progress=1, message="Gotowe", result=result)
            except InterruptedError:
                self.update(job_id, status="CANCELLED", message="Anulowano")
            except Exception as error:
                self.update(job_id, status="FAILED", message=str(error)[-2500:])
            finally:
                self.cancel_events.pop(job_id, None)
        (self.heavy_pool if heavy else self.pool).submit(run)
        return job

    def retry(self,job_id):
        job=self.get(job_id)
        if job["status"] not in ("FAILED","CANCELLED","INTERRUPTED"):
            raise ValueError("Możesz ponowić nieudane lub przerwane zadanie")
        if job_id not in self.tasks: return None
        task,heavy=self.tasks[job_id]
        path=self.root/"job-inputs"/(job_id+".json")
        snapshot=json.loads(path.read_text()) if path.is_file() else None
        return self.submit(job["project_id"],job["revision"],job["kind"],task,request=job.get("request"),heavy=heavy,snapshot=snapshot)

    def cancel(self, job_id):
        event = self.cancel_events.get(job_id)
        if event is not None:
            self.update(job_id, status="CANCEL_REQUESTED", message="Anulowanie…")
            # Publish the request before waking the worker: otherwise CANCELLED can
            # be overwritten by the late request and remain nonterminal forever.
            event.set()
        return self.get(job_id)

    def close(self):
        for event in list(self.cancel_events.values()):
            event.set()
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.heavy_pool.shutdown(wait=False,cancel_futures=True)
