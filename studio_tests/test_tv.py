import io
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from fastapi.testclient import TestClient

from studio_api.app import create_app
from studio_core.models import Scene

HEADERS = {"X-Docos-Request": "1"}


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class TVStreamTests(unittest.TestCase):
    """Strumień HLS na telewizor: playlisty, odcinki i to, że FFmpeg odtwarza całość o długości z osi."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.app = create_app(self.root / "home", seed_demo=False)
        self.client = TestClient(self.app)
        self.p = self.client.post("/api/projects", json={"title": "TV"}, headers=HEADERS).json()
        self.base = "/api/projects/" + self.p["id"]

    def tearDown(self):
        self.app.state.jobs.close(); self.client.close(); self.temp.cleanup()

    def upload(self, name, content, mime):
        result = self.client.post(self.base + "/media", files={"file": (name, content, mime)}, headers=HEADERS)
        self.assertEqual(result.status_code, 200, result.text)
        return result.json()["asset"]

    def build(self):
        clip = self.root / "shot.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=1280x720:r=30:d=2",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)], check=True)
        video = self.upload("shot.mp4", clip.read_bytes(), "video/mp4")
        png = io.BytesIO(); Image.new("RGB", (320, 180), "blue").save(png, format="PNG")
        image = self.upload("blue.png", png.getvalue(), "image/png")
        scenes = [Scene(title="Klip", asset_id=video["id"], mode="upload", animation="static", start=0, duration=60),
                  Scene(title="Obraz", asset_id=image["id"], animation="zoom-in", start=60, duration=45),
                  Scene(title="Pusty", start=105, duration=30)]
        project = self.app.state.store.get(self.p["id"])
        project = self.app.state.store.patch(self.p["id"], project.revision, {"scenes": [s.model_dump() for s in scenes]})
        for scene in scenes[:2]:
            r = self.client.post(self.base + f"/scenes/{scene.id}/to-timeline",
                                 json={"expected_revision": project.revision, "sync_timing": True}, headers=HEADERS)
            self.assertEqual(r.status_code, 200, r.text)
            project = self.app.state.store.get(self.p["id"])
        return scenes

    def fetch_stream(self, name, playlist_url):
        """Pobiera playlistę i jej odcinki do katalogu, z odnośnikami do plików, jak zrobiłby telewizor."""
        response = self.client.get(playlist_url)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("mpegurl", response.headers["content-type"])
        folder = self.root / name; folder.mkdir()
        lines, index = [], 0
        for line in response.text.splitlines():
            if line and not line.startswith("#"):
                segment = self.client.get(playlist_url.rsplit("/", 1)[0] + "/" + line)
                self.assertEqual(segment.status_code, 200, segment.text)
                self.assertEqual(segment.headers["content-type"], "video/mp2t")
                (folder / f"{index}.ts").write_bytes(segment.content)
                line = f"{index}.ts"; index += 1
            lines.append(line)
        (folder / "index.m3u8").write_text("\n".join(lines) + "\n")
        return response.text, folder

    def decoded_seconds(self, playlist: Path) -> float:
        result = subprocess.run(["ffmpeg", "-v", "error", "-i", str(playlist), "-map", "0:v:0", "-f", "null", "-",
                                 "-progress", "pipe:1"], capture_output=True, text=True, check=True)
        self.assertEqual(result.stderr.strip(), "")
        frames = [int(x) for x in re.findall(r"^frame=(\d+)", result.stdout, re.M)]
        return frames[-1] / 30

    def test_address_endpoint(self):
        result = self.client.get("/api/tv/address")
        self.assertEqual(result.status_code, 200)
        address = result.json()["address"]
        self.assertTrue(address is None or re.fullmatch(r"\d+\.\d+\.\d+\.\d+", address))

    def test_probe_stream_for_the_airplay_picker(self):
        text, folder = self.fetch_stream("probe", "/api/tv/probe.m3u8")
        self.assertEqual(text.count("#EXTINF"), 1)
        streams = {s["codec_type"]: s for s in probe(folder / "0.ts")["streams"]}
        self.assertEqual(set(streams), {"video", "audio"})
        self.assertAlmostEqual(self.decoded_seconds(folder / "index.m3u8"), 1, delta=0.1)

    def test_shots_stream_plays_every_shot_for_its_length(self):
        scenes = self.build()
        text, folder = self.fetch_stream("shots", self.base + "/tv/shots.m3u8?start=0")
        self.assertEqual(text.count("#EXTINF"), 3)
        self.assertEqual(text.count("#EXT-X-DISCONTINUITY"), 2)
        self.assertIn("#EXT-X-ENDLIST", text)
        # Gotowy klip H.264 idzie bez kodowania: odcinek ma te same parametry co plik.
        first = probe(folder / "0.ts")["streams"][0]
        self.assertEqual((first["codec_name"], first["width"], first["height"]), ("h264", 1280, 720))
        for index, scene in enumerate(scenes):
            seconds = float(probe(folder / f"{index}.ts")["format"]["duration"])
            self.assertAlmostEqual(seconds, scene.duration / 30, delta=0.1, msg=scene.title)
        self.assertAlmostEqual(self.decoded_seconds(folder / "index.m3u8"), 135 / 30, delta=0.1)
        later, _ = self.fetch_stream("later", self.base + "/tv/shots.m3u8?start=2")
        self.assertEqual(later.count("#EXTINF"), 1)

    def test_montage_stream_follows_the_timeline_from_the_playhead(self):
        self.build()
        text, folder = self.fetch_stream("montage", self.base + "/tv/montage.m3u8?start=15")
        self.assertNotIn("#EXT-X-DISCONTINUITY", text)
        lengths = [float(x) for x in re.findall(r"#EXTINF:([\d.]+),", text)]
        self.assertAlmostEqual(sum(lengths), (105 - 15) / 30, delta=0.01)
        self.assertLessEqual(max(lengths), 6)
        # Znaczniki czasu ciągną się od pozycji kursora, odcinek po odcinku (muxer MPEG-TS dodaje wszystkim
        # to samo stałe przesunięcie, zwykle 1,4 s).
        starts = [float(probe(folder / f"{i}.ts")["format"]["start_time"]) for i in range(len(lengths))]
        self.assertGreaterEqual(starts[0], 15 / 30 - 0.05)
        self.assertLess(starts[0], 15 / 30 + 2)
        for previous, length, start in zip(starts, lengths, starts[1:]):
            self.assertAlmostEqual(start, previous + length, delta=0.2)
        self.assertAlmostEqual(self.decoded_seconds(folder / "index.m3u8"), (105 - 15) / 30, delta=0.15)

    def test_segment_outside_timeline_is_rejected(self):
        self.build()
        self.assertEqual(self.client.get(self.base + "/tv/montage/90-500.ts").status_code, 422)
        self.assertEqual(self.client.get(self.base + "/tv/shot/scene_missing.ts").status_code, 404)


if __name__ == "__main__":
    unittest.main()
