import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.app import create_app
from studio_core.models import Scene

H = {'X-Docos-Request': '1'}


class TeatrTests(unittest.TestCase):
    """Podgląd na żywo: projekt bez ujęć z legacy.teatr nie uruchamia żadnego serwera; złe nazwy są odrzucane."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        store = self.app.state.store
        channel = store.save_channel({'name': 'Film', 'production_mode': 'animation_2d'})
        project = self.client.post('/api/projects', json={'title': 'Teatr', 'channel_id': channel['id']}, headers=H).json()
        project = store.patch(project['id'], project['revision'], {'scenes': [Scene(title='Papier', duration=90).model_dump()]})
        self.pid = project.id

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def test_project_without_live_scenes_has_no_theatre(self):
        self.assertEqual(self.client.get(f'/api/projects/{self.pid}/teatr/stan').json(), {'dostepny': False})
        self.assertEqual(self.client.get(f'/api/projects/{self.pid}/teatr/ujecie/d01_01').status_code, 404)

    def test_bad_names_are_rejected(self):
        self.assertEqual(self.client.get(f'/api/projects/{self.pid}/teatr/ujecie/..%2Fx').status_code, 404)
        self.assertEqual(self.client.get(f'/api/projects/{self.pid}/teatr/ujecie/d1_1').status_code, 400)
        self.assertEqual(self.client.get(f'/api/projects/{self.pid}/teatr/wycinki/zly.png').status_code, 400)

    def test_unknown_film_is_reported_not_crashed(self):
        store = self.app.state.store
        project = store.get(self.pid)
        scene = project.scenes[0].model_dump()
        scene['legacy'] = {'teatr': {'film': 'nie-ma-takiego-filmu', 'jezyk': 'en', 'odn': 'd01_01'}}
        store.patch(self.pid, project.revision, {'scenes': [scene]})
        response = self.client.get(f'/api/projects/{self.pid}/teatr/stan')
        self.assertGreaterEqual(response.status_code, 400)
        self.assertIn('podglądu na żywo', response.text)
