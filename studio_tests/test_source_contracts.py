import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from studio_connectors.sources import Connectors


class ProviderContracts(unittest.TestCase):
    def test_optional_stock_variants_and_book_preview_without_paid_requests(self):
        cases=[("pixabay","video",{"hits":[{"id":1,"tags":"ocean","pageURL":"https://pixabay.com/videos/id-1/","user":"Author","duration":3,"videos":{"small":{"url":"https://cdn.example.org/a.mp4","width":640,"height":360},"large":{"url":"https://cdn.example.org/b.mp4","width":1920,"height":1080}}}]},"Pixabay Content License"),
               ("pexels","video",{"videos":[{"id":2,"url":"https://pexels.com/video/2/","user":{"name":"Camera author"},"width":1920,"height":1080,"duration":4,"video_files":[{"file_type":"video/mp4","quality":"hd","link":"https://cdn.example.org/c.mp4","width":1280,"height":720}]}]},"Pexels License"),
               ("googlebooks","book",{"items":[{"id":"book","volumeInfo":{"title":"Ocean","authors":["Book author"],"publishedDate":"2001","publisher":"Press","previewLink":"https://books.google.com/preview","infoLink":"https://books.google.com/book"},"accessInfo":{"viewability":"PARTIAL","publicDomain":False}}]},None)]
        with tempfile.TemporaryDirectory() as directory:
            connectors=Connectors(Path(directory))
            with patch.object(connectors,"config",return_value={"pixabay_key":"fixture-only","pexels_key":"fixture-only"}):
                for provider,kind,payload,license in cases:
                    with self.subTest(provider=provider),patch.object(connectors,"json",return_value=payload):
                        result=connectors.search(provider,"ocean",kind)[0]
                        self.assertEqual(result["provider"],provider);self.assertTrue(result["author"])
                        if license:self.assertEqual(result["license"],license);self.assertTrue(result["variants"])
                        else:self.assertEqual(result["access"],"preview");self.assertNotIn("download_url",result)

    def test_malformed_feed_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory,patch("studio_connectors.sources.get_bytes",return_value=(b"not xml","text/html","https://example.org/feed")):
            with self.assertRaisesRegex(ValueError,"RSS/Atom"):Connectors(Path(directory)).feed("https://example.org/feed")


if __name__=="__main__":unittest.main()
