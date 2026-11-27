"""Endpointy etapu „Szkice ujęć” (logika w studio_core/sketches.py)."""
from __future__ import annotations

from studio_core import sketches


def register_sketches(app, store):
    def _save(pid: str, revision, change):
        project = store.get(pid)
        flow = sketches._flow(project)
        change(flow)
        return store.save_flow(pid, int(revision if revision is not None else project.revision), flow)

    @app.get("/api/projects/{pid}/sketches")
    def read_sketches(pid: str):
        return sketches.summary(sketches._flow(store.get(pid)))

    @app.put("/api/projects/{pid}/sketches")
    def save_sketches(pid: str, body: dict):
        """Zapis edycji wariantów i czasu przeglądu. Zatwierdzenie zmienia tylko /approve i /withdraw."""
        if not isinstance(body, dict) or "expected_revision" not in body:
            raise ValueError("Wymagane pola: expected_revision i sketches")
        return _save(pid, body["expected_revision"], lambda flow: sketches.replace_editable(flow, body.get("sketches")))

    @app.post("/api/projects/{pid}/sketches/approve")
    def approve_sketch(pid: str, body: dict):
        variant_id = str(body.get("variant_id") or "")
        if not variant_id:
            raise ValueError("Wymagane pole: variant_id")
        return _save(pid, body.get("expected_revision"), lambda flow: sketches.approve(
            flow, variant_id, str(body.get("who") or ""), str(body.get("note") or "")))

    @app.post("/api/projects/{pid}/sketches/withdraw")
    def withdraw_sketch(pid: str, body: dict | None = None):
        body = body or {}
        return _save(pid, body.get("expected_revision"), lambda flow: sketches.withdraw(flow, str(body.get("who") or "")))

    @app.post("/api/projects/{pid}/sketches/import")
    def import_sketches(pid: str, body: dict):
        """Katalog wariantu (z szkic.json) albo katalog szkice/ z wariantami; tylko wewnątrz korzeni."""
        directory = sketches.resolve_inside(str(body.get("path") or ""), sketches.roots())
        revision = body.get("expected_revision")
        return sketches.import_dirs(store, pid, directory, None if revision is None else int(revision),
                                    who=str(body.get("who") or "reżyser"))

    @app.get("/api/sketches/sources")
    def sketch_sources():
        return {"sources": sketches.find_sources(sketches.roots())}
