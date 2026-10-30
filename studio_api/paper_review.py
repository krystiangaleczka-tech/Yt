"""Explicit still review -> author approval -> timeline; never starts an MP4."""
from fastapi.responses import FileResponse
from studio_core import paper_theatre_review as review
from studio_core.store import Conflict, now


def register_paper_review(app, store, connectors):
    def selected(pid, sid, body=None):
        p = store.get(pid)
        if body is not None and p.revision != int(body['expected_revision']):
            raise Conflict('Scena zmieniła się. Wczytaj aktualny układ')
        s = next((s for s in p.scenes if s.id == sid and s.template == 'paper-theatre'), None)
        if not s:
            raise ValueError('Wybierz ujęcie Paper Theatre')
        return p, s

    @app.get('/api/projects/{pid}/paper-theatre/{sid}/review')
    def status(pid: str, sid: str):
        p, s = selected(pid, sid)
        return review.status(store, p, s)

    @app.get('/api/projects/{pid}/paper-theatre/{sid}/review/image')
    def image(pid: str, sid: str, signature: str):
        p, s = selected(pid, sid)
        if signature != review.signature(store, p, s):
            raise Conflict('Ta klatka pochodzi z poprzedniego układu')
        path, _, _ = review.frame_path(store, p, s)
        return FileResponse(path, media_type='image/png')

    @app.post('/api/projects/{pid}/paper-theatre/{sid}/review/preview')
    def preview(pid: str, sid: str, body: dict):
        p, s = selected(pid, sid, body)
        value = review.review_record(store, p, s)
        existing = s.generation.get(review.KEY, {})
        if existing.get('signature') == value['signature']:
            value = {**existing, **value}
        def save(current):
            target = next(s for s in current.scenes if s.id == sid)
            target.generation[review.KEY] = value
        return store.mutate(pid, p.revision, save)

    @app.post('/api/projects/{pid}/paper-theatre/{sid}/review/vision')
    def vision(pid: str, sid: str, body: dict):
        p, s = selected(pid, sid, body)
        current = review.status(store, p, s)
        if not current['preview']:
            raise ValueError('Najpierw przygotuj aktualne porównanie z rzeczywistą klatką')
        assessment = review.vision_review(connectors, store, p, s)
        def save(updated):
            target = next(s for s in updated.scenes if s.id == sid)
            if review.signature(store, updated, target) != assessment['signature']:
                raise Conflict('Układ zmienił się w czasie recenzji')
            target.generation[review.KEY] = {**target.generation.get(review.KEY, {}), 'assessment': assessment}
        # The connected provider may have reserved project budget in a separate revision.
        return store.mutate(pid, store.get(pid).revision, save)

    @app.post('/api/projects/{pid}/paper-theatre/{sid}/review/decision')
    def decision(pid: str, sid: str, body: dict):
        p, s = selected(pid, sid, body)
        current = review.status(store, p, s)
        if body.get('decision') not in ('approve', 'revise'):
            raise ValueError('Wybierz akceptację albo poprawki')
        notes = body.get('notes', '')
        if not isinstance(notes, str) or len(notes) > 5000:
            raise ValueError('Uwagi muszą być tekstem do 5000 znaków')
        approved = body['decision'] == 'approve'
        if approved:
            record = current['preview']
            if not record or body.get('signature') != current['signature'] or body.get('image_sha256') != record['image_sha256']:
                raise Conflict('Przed akceptacją obejrzyj aktualną klatkę')
            if not isinstance(body.get('checks'), list) or not all(isinstance(c, str) for c in body['checks']) or set(body['checks']) != review.CHECKS:
                raise ValueError('Sprawdź proporcje, położenie i styki obiektów')
            if any(i['severity'] == 'critical' for i in (current.get('assessment') or {}).get('issues', [])) and not notes.strip():
                raise ValueError('Wyjaśnij rozwiązanie krytycznych uwag scenografa przed akceptacją')
        def save(updated):
            target = next(s for s in updated.scenes if s.id == sid)
            existing = target.generation.get(review.KEY, {}) if current['current'] else {}
            target.generation[review.KEY] = {**existing, 'signature': current['signature'], 'notes': notes,
                'approval': {'approved': approved, 'at': now(), 'author': 'Autor projektu', 'checks': body.get('checks', [])}}
        return store.mutate(pid, p.revision, save)
