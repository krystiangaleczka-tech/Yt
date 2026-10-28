"""2D animation endpoints: channel-scoped cast/location banks and the scene review board."""
import os
from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import FileResponse

from studio_core.animation import (Cast, DRAFT_VOICES, DraftVoices, MAX_IMAGE, apply_scene_operation, breakdown_prompt,
                                   channel_bank, default_draft_voice, parse_breakdown, parse_regeneration, regeneration_prompt)
from studio_core.assistant import complete
from studio_core.animatic import Images, render_animatic
from studio_core.store import Conflict, atomic_json


REPO = Path(__file__).resolve().parents[1]


def register_animation(app, store, connectors, jobs):
    cast = Cast(store)
    app.state.cast = cast
    python = os.environ.get("DOCOS_DRAFT_TTS_PYTHON") or os.environ.get("DOCOS_IMAGE_PYTHON") or REPO / "pilot" / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    drafts = DraftVoices(store.root, Path(python), Path(os.environ.get("DOCOS_KOKORO_DIR", REPO / "pilot" / "models")))
    app.state.draft_voices = drafts

    @app.get('/api/draft-voices')
    def draft_voices():
        return {'available': drafts.available(), 'voices': list(DRAFT_VOICES)}

    @app.get('/api/draft-voices/{key}.wav')
    def draft_voice_file(key: str):
        path = drafts.path(key)
        if not path.is_file():
            raise FileNotFoundError(key)
        return FileResponse(path, media_type='audio/wav', headers={'Cache-Control': 'private, max-age=31536000, immutable'})

    @app.get('/api/channels/{cid}/cast')
    def bank(cid: str):
        return cast.bank(cid)

    @app.post('/api/channels/{cid}/characters')
    def save_character(cid: str, body: dict):
        return cast.save_character(cid, body)

    @app.post('/api/channels/{cid}/locations')
    def save_location(cid: str, body: dict):
        return cast.save_location(cid, body)

    @app.post('/api/channels/{cid}/items')
    def save_item(cid: str, body: dict):
        return cast.save_item(cid, body)

    @app.post('/api/channels/{cid}/sounds')
    def save_sound(cid: str, body: dict):
        return cast.save_sound(cid, body)

    @app.post('/api/channels/{cid}/cast-audio')
    async def add_audio(cid: str, file: UploadFile):
        cast.channel(cid)
        return cast.add_audio(cid, await file.read(80 * 1024 * 1024 + 1), file.filename or '')

    @app.get('/api/channels/{cid}/cast-audio/{name}')
    def audio(cid: str, name: str):
        path, mime = cast.audio_path(cid, name)
        return FileResponse(path, media_type=mime, headers={'Cache-Control': 'private, max-age=31536000, immutable'})

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
        characters, locations, items = channel_bank(cast, project)
        def change(p):
            for operation in body.get('operations', []):
                apply_scene_operation(p, operation, characters, locations, items)
        return store.mutate(pid, int(body['expected_revision']), change)

    @app.post('/api/projects/{pid}/stage-scenes/{sid}/prompt')
    def prompt(pid: str, sid: str, body: dict):
        project = store.get(pid)
        characters, locations, items = channel_bank(cast, project)
        return {'prompt': regeneration_prompt(project, scene_of(project, sid), characters, locations, str(body.get('instruction', ''))[:2000], items),
                'base_revision': project.revision}

    @app.post('/api/projects/{pid}/stage-scenes/{sid}/regenerate')
    def regenerate(pid: str, sid: str, body: dict):
        project = store.get(pid)
        characters, locations, items = channel_bank(cast, project)
        scene = scene_of(project, sid)
        text = body.get('response')
        if not text:
            text = complete(connectors, regeneration_prompt(project, scene, characters, locations, str(body.get('instruction', ''))[:2000], items), store=store, project=project)
        return parse_regeneration(str(text), scene, characters, locations, items) | {'base_revision': project.revision}

    def beat_of(project, bid):
        beat = next((b for b in project.beats if b.id == bid), None)
        if not beat:
            raise ValueError('Nie ma takiego beatu')
        return beat

    @app.post('/api/projects/{pid}/beats/{bid}/breakdown/prompt')
    def breakdown_text(pid: str, bid: str, body: dict):
        project = store.get(pid)
        characters, locations, items = channel_bank(cast, project)
        return {'prompt': breakdown_prompt(project, beat_of(project, bid), characters, locations, str(body.get('instruction', ''))[:2000], items)}

    @app.post('/api/projects/{pid}/beats/{bid}/breakdown')
    def breakdown(pid: str, bid: str, body: dict):
        project = store.get(pid)
        characters, locations, items = channel_bank(cast, project)
        beat = beat_of(project, bid)
        text = body.get('response')
        if not text:
            text = complete(connectors, breakdown_prompt(project, beat, characters, locations, str(body.get('instruction', ''))[:2000], items), store=store, project=project)
        return parse_breakdown(str(text), beat, characters, locations, items) | {'base_revision': project.revision}

    @app.post('/api/projects/{pid}/stage-scenes/{sid}/draft-voice')
    def draft_voice(pid: str, sid: str, body: dict):
        project = store.get(pid)
        characters, _, _ = channel_bank(cast, project, archived=True)
        scene = scene_of(project, sid)
        chosen = body.get('voices') or {}
        speed = min(1.5, max(0.6, float(body.get('speed', 1))))
        lines = [{'id': line.id, 'text': line.text.strip(), 'voice': chosen.get(line.speaker) or default_draft_voice(line.speaker, characters), 'speed': speed}
                 for line in scene.dialogue if line.text.strip()]
        durations = drafts.render([{k: v for k, v in line.items() if k != 'id'} for line in lines])
        result = []
        for line in lines:
            key = drafts.key(line['text'], line['voice'], speed)
            result.append({'line_id': line['id'], 'voice': line['voice'], 'url': f'/api/draft-voices/{key}.wav', 'duration': durations[key]})
        return result

    def scene_voices(project, scene, characters, chosen, speed):
        lines = [{'id': line.id, 'text': line.text.strip(), 'voice': chosen.get(line.speaker) or default_draft_voice(line.speaker, characters), 'speed': speed}
                 for line in scene.dialogue if line.text.strip()]
        durations = drafts.render([{k: v for k, v in line.items() if k != 'id'} for line in lines])
        return {line['id']: {'duration': durations[drafts.key(line['text'], line['voice'], speed)],
                             'path': drafts.path(drafts.key(line['text'], line['voice'], speed))} for line in lines}

    @app.post('/api/projects/{pid}/animatic/render')
    def render_animatic_job(pid: str, body: dict):
        project = store.get(pid)
        if project.revision != int(body.get('expected_revision', project.revision)):
            raise Conflict('Projekt zmienił się przed renderem animatiku')
        bank = channel_bank(cast, project, archived=True)
        if not project.stage_scenes:
            raise ValueError('Animatik nie ma scen')
        chosen = body.get('voices') or {}
        speed = min(1.5, max(0.6, float(body.get('speed', 1))))
        voiced = bool(body.get('voice', True)) and drafts.available()
        height = 1080 if body.get('quality') == 'final' else 720
        size = (height * 16 // 9, height)
        speakers = {c.id: c.name for c in bank[0].values()}

        def task(job_id, progress, cancel):
            output = store.folder(pid) / 'exports' / (job_id + '.mp4')
            output.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(output.with_suffix('.json'), project.model_dump())
            progress(0.01, 'Przygotowanie głosów' if voiced else 'Składanie klatek')
            drafts_for = (lambda scene: scene_voices(project, scene, bank[0], chosen, speed)) if voiced else (lambda scene: {})
            result = render_animatic(project, bank, Images(cast, project.channel_id), drafts_for, output, progress, cancel, size=size, speakers=speakers)
            return result | {'url': f'/api/jobs/{job_id}/output', 'filename': output.name, 'revision': project.revision, 'voiced': voiced}

        return jobs.submit(pid, project.revision, 'animatic', task, request={'action': 'animatic', 'body': body}, snapshot=project.model_dump())
