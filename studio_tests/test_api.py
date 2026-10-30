import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from fastapi.testclient import TestClient

from studio_api.app import create_app

HEADERS = {"X-Docos-Request": "1"}


class APITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        self.p = self.client.post("/api/projects", json={"title": "Film testowy"}, headers=HEADERS).json()
        self.base = "/api/projects/" + self.p["id"]

    def tearDown(self):
        self.app.state.jobs.close(); self.client.close(); self.temp.cleanup()

    def image(self, color="blue"):
        content = io.BytesIO(); Image.new("RGB", (320, 180), color).save(content, format="PNG"); content.seek(0)
        return content

    def test_cross_site_form_mutation_rejected(self):
        self.assertEqual(self.client.post("/api/projects", json={"title": "Attack"}).status_code, 403)

    def test_shot_description_notes_and_reapplying_motion(self):
        uploaded = self.client.post(self.base + '/media', files={'file': ('blue.png', self.image(), 'image/png')}, headers=HEADERS).json()
        from studio_core.models import Scene
        scene = Scene(title='Kadr', asset_id=uploaded['asset']['id'], prompt='Prompt obrazu', description='Opis akcji', director_notes='Wolny najazd')
        project = self.app.state.store.patch(self.p['id'], uploaded['project']['revision'], {'scenes': [scene.model_dump()]})
        response = self.client.post(self.base + f'/scenes/{scene.id}/to-timeline', json={'expected_revision': project.revision, 'sync_shot': True}, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.text)
        first = response.json()
        self.assertEqual(first['scenes'][0]['description'], 'Opis akcji')
        project = self.app.state.store.patch(self.p['id'], first['revision'], {'scenes': [scene.model_dump() | {'title': 'Poprawiony kadr', 'animation': 'pan-right'}]})
        default = self.client.post(self.base + f'/scenes/{scene.id}/to-timeline', json={'expected_revision': project.revision}, headers=HEADERS)
        self.assertEqual(default.status_code, 200, default.text)
        self.assertEqual(default.json()['sequence']['clips'][0]['animation'], 'zoom-in')
        response = self.client.post(self.base + f'/scenes/{scene.id}/to-timeline', json={'expected_revision': default.json()['revision'], 'sync_shot': True}, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.text)
        saved = self.client.get(self.base).json()
        self.assertEqual(saved['scenes'][0]['prompt'], 'Prompt obrazu')
        self.assertEqual(saved['scenes'][0]['director_notes'], 'Wolny najazd')
        self.assertEqual(len(saved['sequence']['clips']), 1)
        self.assertEqual(saved['sequence']['clips'][0]['animation'], 'pan-right')
        self.assertEqual(saved['sequence']['clips'][0]['title'], 'Poprawiony kadr')

    def test_upload_and_range_file_response(self):
        result = self.client.post(self.base + "/media", files={"file": ("ocean.png", self.image(), "image/png")}, headers=HEADERS)
        self.assertEqual(result.status_code, 200, result.text)
        asset = result.json()["asset"]
        file = self.client.get(self.base + "/media/" + asset["id"], headers={"Range": "bytes=0-15"})
        self.assertEqual(file.status_code, 206)
        self.assertEqual(file.content[:4], b"\x89PNG")

    def test_json_import_cannot_reference_local_files(self):
        raw = self.p | {"assets": [{"id": "evil", "filename": "../../private", "name": "secret", "kind": "image", "mime": "image/png", "sha256": "fake"}]}
        result = self.client.post("/api/projects/import", files={"file": ("p.json", json.dumps(raw), "application/json")}, headers=HEADERS)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["assets"], [])
        self.assertNotEqual(result.json()["id"], self.p["id"])

    def test_credentials_are_not_returned_or_exported(self):
        response = self.client.patch("/api/settings", json={"pixabay_key": "private-key-value"}, headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("private-key-value", response.text)
        self.assertNotIn("private-key-value", self.client.get(self.base + "/download").text)

    def test_local_network_download_blocked(self):
        result = self.client.post(self.base + "/fetch", json={"url": "http://127.0.0.1/private"}, headers=HEADERS)
        self.assertEqual(result.status_code, 422)

    def test_scene_lock_can_be_released_without_changing_content(self):
        from studio_core.models import Scene
        scenes = [Scene(locked=True).model_dump()]
        p = self.client.patch(self.base, json={"expected_revision": 1, "changes": {"scenes": scenes}}, headers=HEADERS).json()
        scenes[0]["locked"] = False
        response = self.client.patch(self.base, json={"expected_revision": p["revision"], "changes": {"scenes": scenes}}, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.text)

    def test_empty_timeline_cannot_be_exported_as_final(self):
        response = self.client.post(self.base + "/render", json={"expected_revision": 1, "mode": "final", "quality": "full"}, headers=HEADERS)
        self.assertEqual(response.status_code, 422)

    def test_connector_search_is_normalized_and_cached(self):
        payload = {"docs": [{"key": "/works/OL1W", "title": "Ocean", "author_name": ["Author"], "first_publish_year": 2000}]}
        with patch.object(self.app.state.connectors, "json", return_value=payload) as fetch:
            first = self.client.get("/api/search", params={"provider": "openlibrary", "q": "Ocean", "kind": "book"})
            second = self.client.get("/api/search", params={"provider": "openlibrary", "q": "Ocean", "kind": "book"})
            self.assertEqual(first.status_code, 200)
            self.assertEqual(first.json()[0]["author"], "Author")
            self.assertEqual(first.json(), second.json())
            self.assertEqual(fetch.call_count, 1)

    def test_text_document_page_is_readable(self):
        result = self.client.post(self.base + "/media", files={"file": ("book.txt", b"A useful paragraph.", "text/plain")}, headers=HEADERS)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertIn("useful", result.json()["source"]["pages"][0]["text"])

    def test_complete_import_edit_render_download_flow(self):
        from studio_core.models import Scene
        result = self.client.post(self.base + "/media", files={"file": ("frame.png", self.image(), "image/png")}, headers=HEADERS).json()
        p = result["project"]
        scene = Scene(title="Ocean", narration="Ocean.", asset_id=result["asset"]["id"], duration=30)
        p = self.client.patch(self.base, json={"expected_revision": p["revision"], "changes": {"scenes": [scene.model_dump()]}}, headers=HEADERS).json()
        result = self.client.post(self.base + "/scenes/" + scene.id + "/to-timeline", json={"expected_revision": p["revision"]}, headers=HEADERS)
        self.assertEqual(result.status_code, 200, result.text)
        p = result.json()
        job = self.client.post(self.base + "/render", json={"expected_revision": p["revision"], "mode": "draft", "quality": "preview"}, headers=HEADERS).json()
        for _ in range(100):
            status = self.app.state.jobs.get(job["id"])
            if status["status"] in ("SUCCEEDED", "FAILED"):
                break
            time.sleep(.03)
        self.assertEqual(status["status"], "SUCCEEDED", status)
        movie = self.client.get(status["result"]["url"])
        self.assertEqual(movie.status_code, 200)
        self.assertIn(b"ftyp", movie.content[:40])
        self.assertGreater(len(movie.content), 1000)


if __name__ == "__main__":
    unittest.main()
