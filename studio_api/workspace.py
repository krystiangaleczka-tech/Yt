"""Workspace banks are available without an open film; imports are explicit."""
from pathlib import Path
import tempfile

from fastapi import UploadFile
from fastapi.responses import FileResponse

from studio_core.models import Project
from studio_core.workspace_models import Category
from studio_core.service import ProjectService
from studio_core.media import import_media, MAX_UPLOAD
from studio_core.store import Conflict


def register_workspace(app, workspace):
    store = workspace.store

    @app.get('/api/workspace')
    def overview():
        uses = workspace.usages()
        return {'categories': workspace.categories(), 'resources': [workspace.summary(r) | {'uses': uses.get(r.id, [])} for r in workspace.resources()], 'defaults': workspace.defaults(), 'channels': store.channels()}

    @app.get('/api/workspace/preview')
    def preview(channel_id: str = '', category_id: str = '', template_id: str = ''):
        preset, snapshots = workspace.effective(channel_id, category_id, template_id)
        return {'preset': preset.model_dump(exclude_none=True), 'chapters': len(snapshots.get('template', {}).get('payload', {}).get('chapters', [])), 'facts': 0, 'sources': 0, 'assets': 0}

    @app.post('/api/workspace/defaults')
    def defaults(body: dict):
        return workspace.save_defaults(body)

    @app.get('/api/workspace/categories')
    def categories(include_archived: bool = False):
        return workspace.categories(include_archived)

    @app.post('/api/workspace/categories')
    def save_category(body: dict):
        return workspace.save_category(body)

    @app.get('/api/workspace/resources')
    def resources(include_archived: bool = False):
        uses = workspace.usages()
        return [workspace.summary(r) | {'uses': uses.get(r.id, [])} for r in workspace.resources(archived=include_archived)]

    @app.get('/api/workspace/resources/{rid}/uses')
    def uses(rid: str):
        workspace.get(rid)
        return workspace.usages().get(rid, [])

    @app.get('/api/workspace/resources/{rid}')
    def resource(rid: str, revision: int | None = None):
        return workspace.get(rid, revision)

    @app.post('/api/workspace/resources')
    def save_resource(body: dict):
        return workspace.save(body)

    @app.get('/api/workspace/resources/{rid}/media/{aid}')
    def resource_media(rid: str, aid: str):
        r = workspace.get(rid)
        from studio_core.models import Asset
        asset = next((Asset.model_validate(a) for a in r.payload.get('assets', []) if a['id'] == aid), None)
        if not asset:
            raise FileNotFoundError()
        return FileResponse(workspace.media_path(asset), media_type=asset.mime, filename=asset.name)

    @app.post('/api/workspace/media')
    async def add_media(file: UploadFile):
        content = await file.read(MAX_UPLOAD + 1)
        if len(content) > MAX_UPLOAD:
            raise ValueError('Plik przekracza 300 MB')
        with tempfile.TemporaryDirectory(dir=workspace.root) as folder:
            staging = ProjectService(Path(folder) / 'staging')
            p = staging.create(Project(development={}))
            original = Path(folder) / 'input'
            original.write_bytes(content)
            asset, source = import_media(staging, p.id, original, file.filename or 'plik')
            from studio_core.workspace import Workspace
            temporary_workspace = Workspace(staging)
            # Publish into the real bank, while reading this isolated staging film.
            temporary_workspace.root = workspace.root
            return temporary_workspace.publish(p.id, {'expected_revision': staging.get(p.id).revision, 'kind': 'source' if source else 'media', 'item_id': source.id if source else asset.id, 'title': source.title if source else asset.name})

    @app.get('/api/projects/{pid}/workspace/links')
    def links(pid: str):
        return workspace.links(pid)

    @app.post('/api/projects/{pid}/workspace/publish')
    def publish(pid: str, body: dict):
        return workspace.publish(pid, body)

    @app.post('/api/projects/{pid}/workspace/import/{rid}')
    def use_resource(pid: str, rid: str, body: dict):
        return workspace.import_resource(pid, rid, body)

    @app.post('/api/projects/{pid}/workspace/context')
    def context(pid: str, body: dict):
        channel = next((c for c in store.channels() if c['id'] == body.get('channel_id')), None)
        if body.get('channel_id') and not channel:
            raise ValueError('Nie ma takiego kanału')
        category = workspace.category(body['category_id']) if body.get('category_id') else None
        if category and (category.archived or category.channel_id and category.channel_id != body.get('channel_id')):
            raise ValueError('Kategoria nie pasuje do kanału')
        def change(p):
            p.channel_id = body.get('channel_id', '')
            p.channel = channel['name'] if channel else 'Mój kanał'
            p.category_id = category.id if category else ''
            p.category_profile = category.model_dump() if category else {}
            p.film_format = str(body.get('film_format', ''))[:100]
        return store.mutate(pid, int(body['expected_revision']), change)
