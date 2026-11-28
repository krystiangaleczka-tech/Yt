"""Gotowość filmu: czego brakuje do oddania (lektor, dźwięk, zgoda na próbkę, recenzje, ciągłość)."""
from __future__ import annotations

import copy
from pathlib import Path

from studio_core import readiness


def register_readiness(app, store, repo: Path):
    @app.get("/api/projects/{pid}/gotowosc")
    def film_readiness(pid: str):
        """Liczy stan z danych projektu; niczego nie zmienia."""
        return readiness.readiness(store.get(pid), repo)

    @app.post("/api/projects/{pid}/gotowosc/probka")
    def sound_sample(pid: str, body: dict):
        """Decyzja reżysera o próbce dźwięku z cytatem — wpis „próbka dźwięku” w dzienniku pracy."""
        entry = readiness.sample_entry(body if isinstance(body, dict) else {})
        project = store.get(pid)
        flow = project.legacy.get("production_flow")
        flow = copy.deepcopy(flow) if isinstance(flow, dict) else {}
        log = flow.setdefault("log", [])
        log.append(entry)
        del log[:-5000]
        revision = body.get("expected_revision")
        return store.save_flow(pid, int(revision if revision is not None else project.revision), flow)
