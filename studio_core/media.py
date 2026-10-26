from __future__ import annotations

import hashlib
import io
import json
import mimetypes
import os
import shutil
import subprocess
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageOps

from .models import Asset, Source
from .store import ProjectStore, now

MAX_UPLOAD = 300 * 1024 * 1024
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".mkv", ".ogv"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac"}
DOC_EXT = {".pdf", ".epub", ".txt", ".md"}


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in ("p", "div", "br", "h1", "h2", "li") and not self.skip:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    @classmethod
    def extract(cls, value: str) -> str:
        p = cls(); p.feed(value)
        return "\n".join(" ".join(line.split()) for line in "".join(p.parts).splitlines() if line.strip())


def probe(path: Path) -> dict:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                            capture_output=True, text=True, timeout=30, check=True)
    return json.loads(result.stdout)


def read_document(path: Path) -> list[dict]:
    if path.suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        return [{"page": str(i + 1), "text": (page.extract_text() or "")[:16000]} for i, page in enumerate(reader.pages[:200])]
    if path.suffix == ".epub":
        from ebooklib import epub, ITEM_DOCUMENT
        with zipfile.ZipFile(path) as z:
            if sum(f.file_size for f in z.infolist()) > 100 * 1024 * 1024:
                raise ValueError("Zbyt duża rozpakowana książka EPUB")
        book = epub.read_epub(str(path), options={"ignore_ncx": True})
        return [{"page": item.get_name(), "text": PlainText.extract(item.get_content().decode("utf-8", "replace"))[:16000]}
                for item in list(book.get_items_of_type(ITEM_DOCUMENT))[:200]]
    return [{"page": "1", "text": path.read_text(encoding="utf-8", errors="replace")[:500000]}]


def import_media(store: ProjectStore, project_id: str, path: Path, name: str, metadata: dict | None = None) -> tuple[Asset, Source | None]:
    metadata = metadata or {}
    suffix = Path(name).suffix.lower()
    if suffix not in IMAGE_EXT | VIDEO_EXT | AUDIO_EXT | DOC_EXT:
        raise ValueError("Obsługiwane są zdjęcia, filmy, audio, PDF, EPUB, TXT i MD")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    provenance_key = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
    asset_id = "asset_" + hashlib.sha256((digest + provenance_key).encode()).hexdigest()[:20]
    folder = store.folder(project_id) / "media"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / (asset_id + suffix)
    temporary = destination.with_suffix(suffix + ".part")
    with path.open("rb") as source_stream, temporary.open("wb") as target_stream:
        shutil.copyfileobj(source_stream, target_stream)
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    asset = Asset(id=asset_id, name=Path(name).name, kind="image", filename=destination.name, mime=mime, sha256=digest,
                  **{k: metadata[k] for k in ("source_url", "author", "license", "license_url", "attribution", "prompt", "provenance") if k in metadata})
    source = None
    try:
        if suffix in IMAGE_EXT:
            with Image.open(temporary) as im:
                im.verify()
            with Image.open(temporary) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                asset.width, asset.height = im.size
                im.thumbnail((640, 360))
                asset.thumbnail = asset_id + ".thumb.jpg"
                im.save(folder / asset.thumbnail, quality=85)
        elif suffix in DOC_EXT:
            asset.kind = "document"
            # Readers use the real extension, never a client-controlled filesystem path.
            os.replace(temporary, destination)
            pages = read_document(destination)
            source = Source(title=asset.name, provider="upload", asset_id=asset_id,
                            text="\n\n".join(p["text"] for p in pages)[:500000], pages=pages, accessed_at=now())
        else:
            info = probe(temporary)
            streams = info.get("streams", [])
            video = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
            if suffix in VIDEO_EXT and not video or suffix in AUDIO_EXT and not audio:
                raise ValueError("Plik nie zawiera oczekiwanej ścieżki multimedialnej")
            asset.kind = "video" if suffix in VIDEO_EXT else "audio"
            asset.duration = float(info.get("format", {}).get("duration") or 0)
            if not 0 < asset.duration < 86400:
                raise ValueError("Nie można odczytać poprawnej długości materiału")
            if video:
                asset.width, asset.height = video.get("width", 0), video.get("height", 0)
                asset.thumbnail = asset_id + ".thumb.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(temporary), "-frames:v", "1", "-vf", "scale=640:-2",
                                str(folder / asset.thumbnail)], check=True, capture_output=True, timeout=30)
        if temporary.exists():
            os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    with store.lock:
        current = store.get(project_id)
        def add(p):
            if not any(a.id == asset.id for a in p.assets):
                p.assets.append(asset)
            if source and not any(s.asset_id == asset.id for s in p.sources):
                p.sources.append(source)
        store.mutate(project_id, current.revision, add)
    return asset, source


def asset_path(store: ProjectStore, project_id: str, asset_id: str, thumbnail=False) -> Path:
    p = store.get(project_id)
    asset = next((a for a in p.assets if a.id == asset_id), None)
    if asset is None:
        raise FileNotFoundError("Nie ma takiego materiału")
    name = asset.thumbnail if thumbnail else asset.filename
    if not name or Path(name).name != name:
        raise FileNotFoundError("Nie ma pliku materiału")
    return store.folder(project_id) / "media" / name
