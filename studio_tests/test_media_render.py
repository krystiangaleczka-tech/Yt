import io
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from studio_core.models import Project, Clip, Keyframe
from studio_core.store import ProjectStore
from studio_core.media import import_media, probe
from studio_core.bundles import import_bundle, export_bundle
from studio_timeline.render import render


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = ProjectStore(self.root)
        self.p = self.store.create(Project())

    def tearDown(self):
        self.temp.cleanup()

    def image(self, color, metadata=None):
        path = self.root / (color + ".png")
        Image.new("RGB", (320, 180), color).save(path)
        return import_media(self.store, self.p.id, path, path.name, metadata)[0]

    def test_same_bytes_different_provenance_are_distinct_assets(self):
        a = self.image("red", {"source_url": "https://example.org/a"})
        b = self.image("red", {"source_url": "https://example.org/b"})
        self.assertEqual(a.sha256, b.sha256)
        self.assertNotEqual(a.id, b.id)
        self.assertEqual(len(self.store.get(self.p.id).assets), 2)

    def test_pdf_retains_page_and_extracts_text(self):
        from pypdf import PdfWriter
        from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
        writer = PdfWriter(); page = writer.add_blank_page(width=320, height=180)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
        stream = DecodedStreamObject(); stream.set_data(b"BT /F1 12 Tf 10 100 Td (Source paragraph.) Tj ET")
        page[NameObject("/Contents")] = stream
        path = self.root / "source.pdf"
        with path.open("wb") as target: writer.write(target)
        _, source = import_media(self.store, self.p.id, path, path.name)
        self.assertEqual(source.pages[0]["page"], "1")
        self.assertIn("Source paragraph", source.pages[0]["text"])

    def test_epub_retains_chapter(self):
        from ebooklib import epub
        book = epub.EpubBook(); book.set_identifier("example"); book.set_title("Example"); book.set_language("en")
        chapter = epub.EpubHtml(title="Ocean", file_name="ocean.xhtml", lang="en")
        chapter.content = "<h1>Ocean</h1><p>A source paragraph.</p>"
        book.add_item(chapter)
        book.toc = (epub.Link("ocean.xhtml", "Ocean", "chapter"),)
        book.add_item(epub.EpubNcx()); book.add_item(epub.EpubNav())
        book.spine = ["nav", chapter]
        path = self.root / "source.epub"; epub.write_epub(str(path), book)
        _, source = import_media(self.store, self.p.id, path, path.name)
        self.assertEqual(source.pages[0]["page"], "ocean.xhtml")
        self.assertIn("source paragraph", source.text)

    def test_bundle_round_trip_keeps_timeline_and_verifies_assets(self):
        a = self.image("red")
        p = self.store.get(self.p.id)
        p = self.store.mutate(p.id, p.revision, lambda p: p.sequence.clips.append(Clip(track_id="v1", asset_id=a.id, duration=30)))
        bundle = export_bundle(self.store, p)
        restored = import_bundle(self.store, bundle)
        self.assertNotEqual(restored.id, p.id)
        self.assertEqual(restored.sequence.clips, p.sequence.clips)
        self.assertEqual(restored.assets, p.assets)
        self.assertTrue((self.store.folder(restored.id) / "media" / a.filename).exists())

    def test_tampered_bundle_is_rejected(self):
        a = self.image("red")
        p = self.store.get(self.p.id)
        path = self.root / "tampered.zip"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("project.json", json.dumps(p.model_dump()))
            z.writestr("media/" + a.filename, b"different bytes")
        with self.assertRaisesRegex(ValueError, "kontrolna"):
            import_bundle(self.store, path)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
    def test_real_multilayer_video_audio_text_and_keyframes(self):
        red, blue, green = self.image("red"), self.image("blue"), self.image("green")
        audio = self.root / "sound.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", str(audio)], check=True)
        sound, _ = import_media(self.store, self.p.id, audio, audio.name)
        p = self.store.get(self.p.id); p.sequence.width = 320; p.sequence.height = 180
        p.sequence.clips = [
            Clip(track_id="v1", asset_id=red.id, duration=30),
            Clip(track_id="v1", asset_id=blue.id, start=30, duration=30),
            Clip(track_id="v2", asset_id=green.id, start=15, duration=30, scale=.5, opacity=.7,
                 keyframes=[Keyframe(property="x", frame=0, value=-.05), Keyframe(property="x", frame=30, value=.05)]),
            Clip(track_id="t1", text="Głos oceanu", start=5, duration=20, scale=.5, y=.3),
            Clip(track_id="a2", asset_id=sound.id, duration=60, volume=.2, fade_out=10),
        ]
        output = self.root / "film.mp4"
        render(self.store, p, output, lambda value, message: None, threading.Event())
        info = probe(output)
        self.assertEqual({s["codec_type"] for s in info["streams"]}, {"audio", "video"})
        self.assertAlmostEqual(float(info["format"]["duration"]), 2, places=1)
        for moment, channel in ((.2, 0), (1.8, 2)):
            png = self.root / (str(moment) + ".png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(moment), "-i", str(output), "-frames:v", "1", str(png)], check=True)
            with Image.open(png) as image:
                self.assertGreater(image.getpixel((20, 20))[channel], 150)


if __name__ == "__main__":
    unittest.main()
