import io
import json
import subprocess
import sys
import time
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient
from PIL import Image

from studio_api.app import create_app
from studio_core.models import Project

H = {'X-Docos-Request': '1'}


def png(color=(200, 40, 40, 255), size=(40, 80)):
    data = io.BytesIO()
    Image.new('RGBA', size, color).save(data, 'PNG')
    return data.getvalue()


class AnimationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        self.store = self.app.state.store
        self.channel = self.store.save_channel({'name': 'Survival', 'language': 'en', 'production_mode': 'animation_2d'})
        self.other = self.store.save_channel({'name': 'Dokumenty', 'language': 'pl'})

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def ok(self, response):
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def image(self, channel_id, content=None):
        return self.ok(self.client.post(f'/api/channels/{channel_id}/cast-media', files={'file': ('pose.png', content or png(), 'image/png')}, headers=H))

    def character(self, channel_id, name='Mara'):
        pose = {'name': 'Stoi', 'view': 'front', 'image': self.image(channel_id)}
        return self.ok(self.client.post(f'/api/channels/{channel_id}/characters', json={'name': name, 'role': 'Pielęgniarka', 'poses': [pose]}, headers=H))

    def location(self, channel_id):
        state = {'name': 'Dzień 1', 'time_of_day': 'day', 'image': self.image(channel_id, png((30, 60, 90, 255), (160, 90)))}
        return self.ok(self.client.post(f'/api/channels/{channel_id}/locations', json={'name': 'Kuchnia', 'states': [state]}, headers=H))

    def film(self, channel_id=None, **body):
        return self.ok(self.client.post('/api/projects', json={'title': 'Day 1', 'channel_id': channel_id or self.channel['id']} | body, headers=H))

    def scenes(self, project, *operations):
        return self.ok(self.client.post(f"/api/projects/{project['id']}/stage-scenes", json={'expected_revision': project['revision'], 'operations': list(operations)}, headers=H))

    def test_mode_is_inherited_from_channel_and_animation_requires_channel(self):
        film = self.film()
        self.assertEqual(film['production_mode'], 'animation_2d')
        self.assertEqual(self.film(self.other['id'])['production_mode'], 'documentary')
        response = self.client.post('/api/projects', json={'title': 'Bez kanału', 'production_mode': 'animation_2d'}, headers=H)
        self.assertEqual(response.status_code, 422)
        listed = self.ok(self.client.get('/api/projects'))
        self.assertIn('production_mode', listed[0])
        self.assertEqual(Project(development={}).production_mode, 'documentary')

    def test_pose_image_keeps_transparency_and_is_scoped_to_channel(self):
        image = self.image(self.channel['id'])
        self.assertTrue(image['alpha'])
        self.assertEqual(self.client.get(f"/api/channels/{self.channel['id']}/cast-media/{image['file']}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/channels/{self.other['id']}/cast-media/{image['file']}").status_code, 404)
        response = self.client.post(f"/api/channels/{self.other['id']}/characters", json={'name': 'Obcy', 'poses': [{'name': 'Stoi', 'image': image}]}, headers=H)
        self.assertEqual(response.status_code, 422)
        bad = self.client.post(f"/api/channels/{self.channel['id']}/cast-media", files={'file': ('x.png', b'not an image', 'image/png')}, headers=H)
        self.assertEqual(bad.status_code, 422)

    def test_bank_revisions_conflict_and_channel_isolation(self):
        mara = self.character(self.channel['id'])
        self.assertEqual(mara['revision'], 1)
        stale = self.client.post(f"/api/channels/{self.channel['id']}/characters", json=mara | {'revision': 0, 'name': 'Inna'}, headers=H)
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(len(self.ok(self.client.get(f"/api/channels/{self.channel['id']}/cast"))['characters']), 1)
        self.assertEqual(self.ok(self.client.get(f"/api/channels/{self.other['id']}/cast"))['characters'], [])
        moved = self.client.post(f"/api/channels/{self.other['id']}/characters", json=mara, headers=H)
        self.assertEqual(moved.status_code, 422)

    def test_scene_board_review_flow(self):
        mara, kitchen = self.character(self.channel['id']), self.location(self.channel['id'])
        film = self.film()
        placed = {'character_id': mara['id'], 'pose_id': mara['poses'][0]['id'], 'x': .4}
        film = self.scenes(film, {'type': 'add', 'scene': {'title': 'Woda', 'location_id': kitchen['id'], 'location_state_id': kitchen['states'][0]['id'],
                                                          'characters': [placed], 'action': 'Patrzy na wodę.',
                                                          'dialogue': [{'speaker': mara['id'], 'text': 'Do we drink it?'}],
                                                          'sound': {'ambience': 'quiet flat', 'sfx': ['drip']}}})
        scene = film['stage_scenes'][0]
        self.assertEqual((scene['number'], scene['status']), (1, 'draft'))
        rework = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [{'type': 'review', 'scene_id': scene['id'], 'status': 'rework'}]}, headers=H)
        self.assertEqual(rework.status_code, 422)
        film = self.scenes(film, {'type': 'review', 'scene_id': scene['id'], 'status': 'approved'})
        self.assertEqual(film['stage_scenes'][0]['status'], 'approved')
        film = self.scenes(film, {'type': 'update', 'scene_id': scene['id'], 'changes': {'camera': 'close-up'}})
        self.assertEqual(film['stage_scenes'][0]['status'], 'review')
        film = self.scenes(film, {'type': 'review', 'scene_id': scene['id'], 'status': 'rework', 'tags': ['Tło', 'nieznany'], 'note': 'ciemniej'})
        self.assertEqual(film['stage_scenes'][0]['reviews'][-1]['tags'], ['Tło'])
        film = self.scenes(film, {'type': 'add', 'scene': {'title': 'Druga'}}, {'type': 'move', 'scene_id': scene['id'], 'to': 1})
        self.assertEqual([s['title'] for s in film['stage_scenes']], ['Druga', 'Woda'])
        self.assertEqual([s['number'] for s in film['stage_scenes']], [1, 2])
        undo = self.ok(self.client.post(f"/api/projects/{film['id']}/history/undo", json={'expected_revision': film['revision']}, headers=H))
        self.assertEqual(len(undo['stage_scenes']), 1)

    def test_scenes_reject_cast_of_another_channel(self):
        stranger = self.character(self.other['id'], 'Obcy')
        film = self.film()
        response = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [{'type': 'add', 'scene': {'characters': [{'character_id': stranger['id']}]}}]}, headers=H)
        self.assertEqual(response.status_code, 422)
        self.assertIn('banku kanału', response.json()['detail'])
        film = self.scenes(film, {'type': 'add', 'scene': {'title': 'Pusta'}})
        moved = self.client.post(f"/api/projects/{film['id']}/workspace/context", json={'expected_revision': film['revision'], 'channel_id': self.other['id']}, headers=H)
        self.assertEqual(moved.status_code, 422)

    def test_regeneration_is_a_validated_proposal(self):
        mara, kitchen = self.character(self.channel['id']), self.location(self.channel['id'])
        film = self.scenes(self.film(), {'type': 'add', 'scene': {'title': 'Woda', 'location_id': kitchen['id']}})
        scene = film['stage_scenes'][0]
        prompt = self.ok(self.client.post(f"/api/projects/{film['id']}/stage-scenes/{scene['id']}/prompt", json={'instruction': 'more tension'}, headers=H))
        self.assertIn(mara['poses'][0]['id'], prompt['prompt'])
        answer = {'title': 'Woda w półmroku', 'characters': [{'character_id': mara['id'], 'pose_id': mara['poses'][0]['id'], 'x': .3}],
                  'dialogue': [{'speaker': 'narrator', 'text': 'You count the bottles again.'}], 'reason': 'Więcej napięcia'}
        with mock.patch('studio_api.animation.complete', return_value='```json\n' + json.dumps(answer) + '\n```'):
            proposal = self.ok(self.client.post(f"/api/projects/{film['id']}/stage-scenes/{scene['id']}/regenerate", json={'instruction': 'more tension'}, headers=H))
        self.assertEqual(proposal['changes']['title'], 'Woda w półmroku')
        self.assertEqual(self.store.get(film['id']).stage_scenes[0].title, 'Woda')
        invented = json.dumps(answer | {'characters': [{'character_id': 'chr_0000000000000000'}]})
        response = self.client.post(f"/api/projects/{film['id']}/stage-scenes/{scene['id']}/regenerate", json={'response': invented}, headers=H)
        self.assertEqual(response.status_code, 422)
        film = self.scenes(film, {'type': 'update', 'scene_id': scene['id'], 'changes': proposal['changes']})
        self.assertEqual(film['stage_scenes'][0]['dialogue'][0]['speaker'], 'narrator')


    def test_beats_group_scenes_and_story_director_proposes_scenes(self):
        mara, kitchen = self.character(self.channel['id']), self.location(self.channel['id'])
        film = self.film()
        beat = {'id': 'beat_' + 'a' * 16, 'title': 'Woda się kończy', 'goal': 'Pokazać pierwszy deficyt', 'narration': 'The tap coughs and dies.'}
        film = self.store.patch(film['id'], film['revision'], {'beats': [beat]}).model_dump()
        missing = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [{'type': 'add', 'scene': {'beat_id': 'beat_' + 'b' * 16}}]}, headers=H)
        self.assertEqual(missing.status_code, 422)
        film = self.scenes(film, {'type': 'add', 'scene': {'title': 'Kran', 'beat_id': beat['id']}})
        scene = film['stage_scenes'][0]
        film = self.scenes(film, {'type': 'review', 'scene_id': scene['id'], 'status': 'approved'},
                           {'type': 'update', 'scene_id': scene['id'], 'changes': {'beat_id': ''}})
        self.assertEqual(film['stage_scenes'][0]['status'], 'approved')
        prompt = self.ok(self.client.post(f"/api/projects/{film['id']}/beats/{beat['id']}/breakdown/prompt", json={}, headers=H))
        self.assertIn(kitchen['states'][0]['id'], prompt['prompt'])
        answer = {'reason': 'Dwa ujęcia', 'scenes': [
            {'title': 'Kran kaszle', 'location_id': kitchen['id'], 'location_state_id': kitchen['states'][0]['id'], 'seconds': 4},
            {'title': 'Mara patrzy', 'characters': [{'character_id': mara['id'], 'pose_id': mara['poses'][0]['id']}],
             'dialogue': [{'speaker': mara['id'], 'text': "That's it."}]}]}
        with mock.patch('studio_api.animation.complete', return_value=json.dumps(answer)):
            proposal = self.ok(self.client.post(f"/api/projects/{film['id']}/beats/{beat['id']}/breakdown", json={}, headers=H))
        self.assertEqual([s['beat_id'] for s in proposal['scenes']], [beat['id']] * 2)
        self.assertEqual(len(self.store.get(film['id']).stage_scenes), 1)
        bad = self.client.post(f"/api/projects/{film['id']}/beats/{beat['id']}/breakdown", json={'response': json.dumps({'scenes': [{'location_id': 'loc_' + '0' * 16}]})}, headers=H)
        self.assertEqual(bad.status_code, 422)
        film = self.scenes(film, *[{'type': 'add', 'scene': s} for s in proposal['scenes']])
        self.assertEqual([s['title'] for s in film['stage_scenes']], ['Kran', 'Kran kaszle', 'Mara patrzy'])


    def test_draft_voices_are_cached_per_line_and_use_distinct_defaults(self):
        mara = self.character(self.channel['id'])
        drafts = self.app.state.draft_voices
        models = Path(self.temp.name) / 'kokoro'
        models.mkdir()
        for name in ('kokoro-v1.0.onnx', 'voices-v1.0.bin'):
            (models / name).write_bytes(b'x')
        drafts.python, drafts.model_dir = Path(sys.executable), models
        calls = []

        def fake_run(command, input, **kwargs):
            job = json.loads(input)
            calls.append(job['lines'])
            out = []
            for line in job['lines']:
                Path(line['out']).write_bytes(b'RIFF')
                out.append(json.dumps({'out': line['out'], 'duration': 1.5}))
            return mock.Mock(returncode=0, stdout='\n'.join(out), stderr='')

        film = self.scenes(self.film(), {'type': 'add', 'scene': {'title': 'Rozmowa', 'dialogue': [
            {'speaker': 'narrator', 'text': 'Day two.'}, {'speaker': mara['id'], 'text': 'Water?'}, {'speaker': 'narrator', 'text': ' '}]}})
        scene = film['stage_scenes'][0]
        url = f"/api/projects/{film['id']}/stage-scenes/{scene['id']}/draft-voice"
        with mock.patch('subprocess.run', side_effect=fake_run):
            first = self.ok(self.client.post(url, json={}, headers=H))
            again = self.ok(self.client.post(url, json={}, headers=H))
        self.assertEqual(len(first), 2)
        self.assertNotEqual(first[0]['voice'], first[1]['voice'])
        self.assertEqual(first, again)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.client.get(first[0]['url']).status_code, 200)
        bad = self.client.post(url, json={'voices': {'narrator': 'zz_unknown'}}, headers=H)
        self.assertEqual(bad.status_code, 422)
        self.assertTrue(self.ok(self.client.get('/api/draft-voices'))['available'])


    def test_items_bank_costumes_and_scene_props(self):
        cid = self.channel['id']
        mara, kitchen = self.character(cid), self.location(cid)
        crack = self.ok(self.client.post(f'/api/channels/{cid}/items', json={'name': 'Pęknięta szyba', 'category': 'overlay',
                                                                            'variants': [{'name': 'małe', 'image': self.image(cid)}]}, headers=H))
        jacket = self.ok(self.client.post(f'/api/channels/{cid}/items', json={'name': 'Kurtka', 'category': 'costume', 'character_ids': [mara['id']]}, headers=H))
        self.assertEqual(len(self.ok(self.client.get(f'/api/channels/{cid}/cast'))['items']), 2)
        wrong = self.client.post(f'/api/channels/{cid}/items', json={'name': 'Kurtka', 'category': 'costume', 'character_ids': ['chr_' + '0' * 16]}, headers=H)
        self.assertEqual(wrong.status_code, 422)
        pose = mara['poses'][0] | {'costume_id': jacket['id']}
        mara = self.ok(self.client.post(f'/api/channels/{cid}/characters', json=mara | {'poses': [pose]}, headers=H))
        film = self.film()
        stranger = self.client.post(f"/api/channels/{self.other['id']}/items", json={'name': 'Obcy', 'variants': []}, headers=H).json()
        bad = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [
            {'type': 'add', 'scene': {'props': [{'item_id': stranger['id']}]}}]}, headers=H)
        self.assertEqual(bad.status_code, 422)
        film = self.scenes(film, {'type': 'add', 'scene': {'location_id': kitchen['id'], 'characters': [{'character_id': mara['id'], 'costume_id': jacket['id']}],
                                                            'props': [{'item_id': crack['id'], 'motion': 'appear', 'at': .3, 'layer': 'behind'}], 'seconds': 1.2,
                                                            'motion': {'camera': 'push_in', 'strength': .6}, 'dialogue': [{'speaker': mara['id'], 'text': 'Water?'}]}})
        self.assertEqual(film['stage_scenes'][0]['props'][0]['item_id'], crack['id'])
        costume_on_prop = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [
            {'type': 'update', 'scene_id': film['stage_scenes'][0]['id'], 'changes': {'props': [{'item_id': jacket['id']}]}}]}, headers=H)
        self.assertEqual(costume_on_prop.status_code, 422)
        self.app.state.draft_voices.model_dir = Path(self.temp.name) / 'missing'
        job = self.ok(self.client.post(f"/api/projects/{film['id']}/animatic/render", json={'expected_revision': film['revision']}, headers=H))
        for _ in range(200):
            state = self.ok(self.client.get('/api/jobs/' + job['id']))
            if state['status'] in ('SUCCEEDED', 'FAILED'):
                break
            time.sleep(.05)
        self.assertEqual(state['status'], 'SUCCEEDED', state['message'])
        self.assertFalse(state['result']['voiced'])
        video = self.client.get(state['result']['url'])
        self.assertEqual(video.status_code, 200)
        path = Path(self.temp.name) / 'a.mp4'
        path.write_bytes(video.content)
        probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width:format=duration', '-of', 'json', str(path)], capture_output=True, text=True).stdout)
        self.assertEqual({s['codec_type'] for s in probe['streams']}, {'video', 'audio'})
        self.assertAlmostEqual(float(probe['format']['duration']), 1.5, delta=.3)


    def test_sound_bank_scene_cues_music_ranges_and_mix(self):
        cid = self.channel['id']

        def tone(hz, seconds=1.0):
            import numpy as np
            import wave as wav
            data = io.BytesIO()
            t = np.arange(int(22050 * seconds)) / 22050
            with wav.open(data, 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
                w.writeframes((np.sin(2 * np.pi * hz * t) * 12000).astype('<i2').tobytes())
            return data.getvalue()

        def sound(name, kind, hz):
            uploaded = self.ok(self.client.post(f'/api/channels/{cid}/cast-audio', files={'file': (name + '.wav', tone(hz), 'audio/wav')}, headers=H))
            self.assertAlmostEqual(uploaded['duration'], 1.0, delta=.05)
            return self.ok(self.client.post(f'/api/channels/{cid}/sounds', json={'name': name, 'kind': kind, 'license': 'CC0'} | uploaded, headers=H))

        knock, room, theme = sound('knock', 'sfx', 600), sound('room', 'ambience', 120), sound('theme', 'music', 330)
        bad = self.client.post(f'/api/channels/{cid}/cast-audio', files={'file': ('x.txt', b'nope', 'text/plain')}, headers=H)
        self.assertEqual(bad.status_code, 422)
        self.assertEqual(self.client.get(f"/api/channels/{self.other['id']}/cast-audio/{knock['file']}").status_code, 404)
        film = self.film()
        music_in_scene = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [
            {'type': 'add', 'scene': {'audio': [{'sound_id': theme['id']}]}}]}, headers=H)
        self.assertEqual(music_in_scene.status_code, 422)
        film = self.scenes(film, {'type': 'add', 'scene': {'title': 'A', 'seconds': 1, 'audio': [{'sound_id': room['id']}, {'sound_id': knock['id'], 'at': .2}]}},
                           {'type': 'add', 'scene': {'title': 'B', 'seconds': 1}})
        first, second = (s['id'] for s in film['stage_scenes'])
        wrong = self.client.post(f"/api/projects/{film['id']}/stage-scenes", json={'expected_revision': film['revision'], 'operations': [
            {'type': 'music_set', 'cue': {'sound_id': knock['id'], 'from_scene_id': first, 'to_scene_id': second}}]}, headers=H)
        self.assertEqual(wrong.status_code, 422)
        film = self.scenes(film, {'type': 'music_set', 'cue': {'sound_id': theme['id'], 'from_scene_id': first, 'to_scene_id': second}})
        self.assertEqual(len(film['music_cues']), 1)
        self.app.state.draft_voices.model_dir = Path(self.temp.name) / 'missing'
        job = self.ok(self.client.post(f"/api/projects/{film['id']}/animatic/render", json={'expected_revision': film['revision']}, headers=H))
        for _ in range(300):
            state = self.ok(self.client.get('/api/jobs/' + job['id']))
            if state['status'] in ('SUCCEEDED', 'FAILED'):
                break
            time.sleep(.05)
        self.assertEqual(state['status'], 'SUCCEEDED', state['message'])
        path = Path(self.temp.name) / 'mix.mp4'
        path.write_bytes(self.client.get(state['result']['url']).content)
        volume = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
        self.assertNotIn('mean_volume: -91', volume)
        film = self.scenes(film, {'type': 'delete', 'scene_id': second})
        self.assertEqual(film['music_cues'], [])


    def test_rework_batch_returns_proposals_without_touching_scenes(self):
        mara = self.character(self.channel['id'])
        film = self.scenes(self.film(), {'type': 'add', 'scene': {'title': 'Jeden'}}, {'type': 'add', 'scene': {'title': 'Dwa'}},
                           {'type': 'add', 'scene': {'title': 'Trzy'}})
        one, two, three = (s['id'] for s in film['stage_scenes'])
        none = self.client.post(f"/api/projects/{film['id']}/stage-scenes/rework-batch", json={}, headers=H)
        self.assertEqual(none.status_code, 422)
        film = self.scenes(film, {'type': 'review', 'scene_id': one, 'status': 'rework', 'note': 'ciemniej'},
                           {'type': 'review', 'scene_id': two, 'status': 'rework', 'note': 'Mara ma pukać'},
                           {'type': 'review', 'scene_id': three, 'status': 'approved'})
        answers = iter([json.dumps({'title': 'Jeden po poprawce', 'reason': 'ciemniej'}),
                        json.dumps({'characters': [{'character_id': 'chr_' + '0' * 16}]})])
        with mock.patch('studio_api.animation.complete', side_effect=lambda *a, **k: next(answers)):
            job = self.ok(self.client.post(f"/api/projects/{film['id']}/stage-scenes/rework-batch", json={}, headers=H))
            for _ in range(200):
                state = self.ok(self.client.get('/api/jobs/' + job['id']))
                if state['status'] in ('SUCCEEDED', 'FAILED'):
                    break
                time.sleep(.02)
        self.assertEqual(state['status'], 'SUCCEEDED', state['message'])
        result = state['result']
        self.assertEqual([p['scene_id'] for p in result['proposals']], [one])
        self.assertEqual(result['proposals'][0]['before']['title'], 'Jeden')
        self.assertEqual([e['scene_id'] for e in result['errors']], [two])
        self.assertEqual([s['title'] for s in self.store.get(film['id']).model_dump()['stage_scenes']], ['Jeden', 'Dwa', 'Trzy'])
        self.assertTrue(mara)


if __name__ == '__main__':
    unittest.main()
