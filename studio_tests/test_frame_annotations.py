import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.app import create_app
from studio_core.animation import StageScene
from studio_core.models import Scene

H = {'X-Docos-Request': '1'}


class FrameAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        store = self.app.state.store
        channel = store.save_channel({'name': 'Film', 'production_mode': 'animation_2d'})
        project = self.client.post('/api/projects', json={'title': 'Sceny', 'channel_id': channel['id']}, headers=H).json()
        self.media = Scene(title='Papier', duration=90, locked=True)
        self.stage = StageScene(title='Aktor', seconds=4, status='approved')
        project = store.patch(project['id'], project['revision'], {'scenes': [self.media.model_dump()]})
        project = store.mutate(project.id, project.revision, lambda p: p.stage_scenes.append(self.stage))
        self.pid = project.id
        self.base = f'/api/projects/{self.pid}'

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def current(self):
        return self.client.get(self.base).json()

    def payload(self, **changes):
        return {'scene_id': self.media.id, 'frame': 42, 'text': 'Przesuń chmurę w lewo.',
                'strokes': [{'points': [{'x': .2, 'y': .3}, {'x': .4, 'y': .6}]}]} | changes

    def create(self, **changes):
        return self.client.post(self.base + '/frame-annotations', json={
            'expected_revision': self.current()['revision'], **self.payload(**changes)}, headers=H)

    def test_exact_frame_and_normalized_marker_persist_for_both_kinds_of_shots(self):
        before = self.current()
        response = self.create()
        self.assertEqual(response.status_code, 200, response.text)
        response = self.create(scene_id=self.stage.id, frame=9, text='Popraw pozę.')
        self.assertEqual(response.status_code, 200, response.text)
        saved = self.current()
        self.assertEqual([(n['scene_id'], n['frame']) for n in saved['frame_annotations']], [(self.media.id, 42), (self.stage.id, 9)])
        self.assertEqual(saved['frame_annotations'][0]['strokes'][0]['points'][1], {'x': .4, 'y': .6})
        self.assertTrue(saved['frame_annotations'][0]['created_at'])
        self.assertEqual(saved['scenes'], before['scenes'])
        self.assertEqual(saved['stage_scenes'], before['stage_scenes'])
        self.assertEqual(saved['sequence'], before['sequence'])
        self.assertEqual(saved['stage_scenes'][0]['status'], 'approved')
        self.assertTrue(saved['scenes'][0]['locked'])

    def test_invalid_frame_geometry_and_empty_comment_are_rejected_atomically(self):
        for changes in [
            {'frame': -1}, {'frame': 90}, {'frame': 2.2}, {'text': '   '},
            {'scene_id': 'scene_' + 'f' * 16}, {'fps_num': 0}, {'fps_num': 300},
            {'strokes': []}, {'strokes': [{'points': [{'x': -.1, 'y': .5}, {'x': .5, 'y': .5}]}]},
        ]:
            with self.subTest(changes=changes):
                response = self.create(**changes)
                self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.current()['frame_annotations'], [])

    def test_retry_edit_delete_and_revision_conflicts(self):
        annotation_id = 'ann_' + 'a' * 16
        stale = self.current()['revision']
        first = self.create(id=annotation_id)
        self.assertEqual(first.status_code, 200, first.text)
        retry = self.create(id=annotation_id)
        self.assertEqual(retry.status_code, 200, retry.text)
        self.assertEqual(len(retry.json()['frame_annotations']), 1)
        conflict = self.client.patch(self.base + '/frame-annotations/' + annotation_id,
                                     json={'expected_revision': stale, 'changes': {'text': 'Zmienione'}}, headers=H)
        self.assertEqual(conflict.status_code, 409)
        edited = self.client.patch(self.base + '/frame-annotations/' + annotation_id,
                                  json={'expected_revision': self.current()['revision'], 'changes': {'text': 'Przesuń o 10 px.'}}, headers=H)
        self.assertEqual(edited.status_code, 200, edited.text)
        note = edited.json()['frame_annotations'][0]
        self.assertEqual((note['frame'], note['text']), (42, 'Przesuń o 10 px.'))
        forbidden = self.client.patch(self.base + '/frame-annotations/' + annotation_id,
                                     json={'expected_revision': self.current()['revision'], 'changes': {'frame': 10}}, headers=H)
        self.assertEqual(forbidden.status_code, 422)
        deleted = self.client.request('DELETE', self.base + '/frame-annotations/' + annotation_id,
                                      json={'expected_revision': self.current()['revision']}, headers=H)
        self.assertEqual(deleted.status_code, 200, deleted.text)
        self.assertEqual(self.current()['frame_annotations'], [])

    def test_annotations_keep_their_original_fractional_time_base(self):
        response = self.create(frame=59, fps_num=30000, fps_den=1001)
        self.assertEqual(response.status_code, 200, response.text)
        note = response.json()['frame_annotations'][0]
        self.assertEqual((note['frame'], note['fps_num'], note['fps_den']), (59, 30000, 1001))
        self.app.state.store.mutate(self.pid, self.current()['revision'], lambda p: setattr(p.sequence, 'fps_num', 25))
        self.assertEqual(self.current()['frame_annotations'][0], note)

    def test_annotations_survive_project_bundle_and_are_scoped_to_project(self):
        created = self.create()
        self.assertEqual(created.status_code, 200, created.text)
        note = created.json()['frame_annotations'][0]
        other = self.client.post('/api/projects', json={'title': 'Inny film'}, headers=H).json()
        response = self.client.request('DELETE', f"/api/projects/{other['id']}/frame-annotations/{note['id']}",
                                       json={'expected_revision': other['revision']}, headers=H)
        self.assertEqual(response.status_code, 422)
        archive = self.client.get(self.base + '/bundle')
        self.assertEqual(archive.status_code, 200, archive.text)
        restored = self.client.post('/api/projects/import-bundle', files={'file': ('film.zip', archive.content, 'application/zip')}, headers=H)
        self.assertEqual(restored.status_code, 200, restored.text)
        self.assertEqual(restored.json()['frame_annotations'], [note])
