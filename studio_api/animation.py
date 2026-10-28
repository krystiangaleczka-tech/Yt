"""2D animation endpoints: channel-scoped cast/location banks and the scene review board."""
from fastapi import UploadFile
from fastapi.responses import FileResponse

from studio_core.animation import (Cast, MAX_IMAGE, apply_scene_operation, channel_bank, parse_regeneration,
                                   regeneration_prompt)
from studio_core.assistant import complete


def register_animation(app, store, connectors):
    cast = Cast(store)
    app.state.cast = cast

    @app.get('/api/channels/{cid}/cast')
    def bank(cid: str):
        return cast.bank(cid)

    @app.post('/api/channels/{cid}/characters')
    def save_character(cid: str, body: dict):
        return cast.save_character(cid, body)

    @app.post('/api/channels/{cid}/locations')
    def save_location(cid: str, body: dict):
        return cast.save_location(cid, body)

    @app.post('/api/channels/{cid}/cast-media')
    async def add_image(cid: str, file: UploadFile):
        cast.channel(cid)
        content = await file.read(MAX_IMAGE + 1)
        return cast.add_image(cid, content)

    @app.get('/api/channels/{cid}/cast-media/{name}')
    def image(cid: str, name: str):
        path, mime = cast.image_path(cid, name)
        return FileResponse(path, media_type=mime, headers={'Cache-Control': 'private, max-age=31536000, immutable'})

    def scene_of(project, sid):
        scene = next((s for s in project.stage_scenes if s.id == sid), None)
        if not scene:
            raise ValueError('Nie ma takiej sceny')
        return scene

    @app.post('/api/projects/{pid}/stage-scenes')
    def scene_operation(pid: str, body: dict):
        project = store.get(pid)
        characters, locations = channel_bank(cast, project)
        def change(p):
            for operation in body.get('operations', []):
                apply_scene_operation(p, operation, characters, locations)
        return store.mutate(pid, int(body['expected_revision']), change)

    @app.post('/api/projects/{pid}/stage-scenes/{sid}/prompt')
    def prompt(pid: str, sid: str, body: dict):
        project = store.get(pid)
        characters, locations = channel_bank(cast, project)
        return {'prompt': regeneration_prompt(project, scene_of(project, sid), characters, locations, str(body.get('instruction', ''))[:2000]),
                'base_revision': project.revision}

    @app.post('/api/projects/{pid}/stage-scenes/{sid}/regenerate')
    def regenerate(pid: str, sid: str, body: dict):
        project = store.get(pid)
        characters, locations = channel_bank(cast, project)
        scene = scene_of(project, sid)
        text = body.get('response')
        if not text:
            text = complete(connectors, regeneration_prompt(project, scene, characters, locations, str(body.get('instruction', ''))[:2000]), store=store, project=project)
        return parse_regeneration(str(text), scene, characters, locations) | {'base_revision': project.revision}
