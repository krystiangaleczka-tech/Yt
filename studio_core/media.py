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
DOC_EXT = {".pdf", ".epub", ".txt", ".md", ".html", ".xml"}


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


class HTMLMetadata(HTMLParser):
    def __init__(self):super().__init__();self.values={};self.in_title=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="title":self.in_title=True
        if tag=="meta":
            key=attrs.get("property",attrs.get("name",""));value=attrs.get("content","")
            mapping={"og:title":"title","author":"author","article:author":"author","article:published_time":"published_at","date":"published_at","citation_publication_date":"published_at"}
            if key in mapping and value:self.values[mapping[key]]=value[:500]
    def handle_endtag(self,tag):
        if tag=="title":self.in_title=False
    def handle_data(self,text):
        if self.in_title and "title" not in self.values:self.values["title"]=text.strip()[:500]
    @classmethod
    def extract(cls,text):
        parser=cls();parser.feed(text);return parser.values


def probe(path: Path) -> dict:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                            capture_output=True, text=True, timeout=30, check=True)
    return json.loads(result.stdout)


def read_document(path: Path, *, ocr=False) -> list[dict]:
    if path.suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        result = []
        for i,page in enumerate(reader.pages[:2000]):
            text = page.extract_text() or ""
            method = "text"
            if not text.strip() and ocr:
                image = pdf_page(path, i+1)
                text = recognize(image); method = "ocr"
            result.append({"page":str(i+1),"text":text[:16000],"method":method,"needs_ocr":not text.strip()})
        return result
    if path.suffix == ".epub":
        from ebooklib import epub, ITEM_DOCUMENT
        with zipfile.ZipFile(path) as z:
            if sum(f.file_size for f in z.infolist()) > 100 * 1024 * 1024:
                raise ValueError("Zbyt duża rozpakowana książka EPUB")
        book = epub.read_epub(str(path), options={"ignore_ncx": True})
        return [{"page": item.get_name(), "text": PlainText.extract(item.get_content().decode("utf-8", "replace"))[:16000]}
                for item in list(book.get_items_of_type(ITEM_DOCUMENT))[:2000]]
    text=path.read_text(encoding="utf-8", errors="replace")[:500000]
    if path.suffix in (".html",".xml"): text=PlainText.extract(text)
    return [{"page": "1", "text": text}]


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
            source = Source(title=asset.name, provider="upload", asset_id=asset_id, original_asset_id=asset_id,url=asset.source_url,author=asset.author,
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


def asset_path(store: ProjectStore, project_id: str, asset_id: str, thumbnail=False, *,project=None) -> Path:
    p = project if project is not None else store.get(project_id)
    if p.id!=project_id:raise ValueError("Migawka pochodzi z innego projektu")
    asset = next((a for a in p.assets if a.id == asset_id), None)
    if asset is None:
        raise FileNotFoundError("Nie ma takiego materiału")
    name = asset.thumbnail if thumbnail else asset.filename
    if not name or Path(name).name != name:
        raise FileNotFoundError("Nie ma pliku materiału")
    return store.folder(project_id) / "media" / name


def pdf_page(path, page, cancel=None):
    if not shutil.which("pdftoppm"):
        raise ValueError("Podgląd PDF wymaga Popplera. macOS: brew install poppler; Linux: apt install poppler-utils")
    if int(page)<1 or int(page)>2000:
        raise ValueError("Niepoprawny numer strony")
    output=path.parent/(path.stem+f".page-{int(page)}")
    target=output.with_suffix(output.suffix+".png")
    if not target.is_file():
        from .locking import FileLock
        with FileLock(path.parent/(output.name+".lock")):
            if not target.is_file():
                temporary=output.with_name(output.name+".part")
                command=["pdftoppm","-f",str(int(page)),"-l",str(int(page)),"-singlefile","-scale-to","1600","-png",str(path),str(temporary)]
                generated=Path(str(temporary)+".png")
                try:
                    if cancel is None: subprocess.run(command,check=True,capture_output=True,timeout=60)
                    else:
                        from .audio import run_process
                        run_process(command,cancel)
                    with Image.open(generated) as image: image.verify()
                    generated.replace(target)
                finally:generated.unlink(missing_ok=True)
    return target


def recognize(path,cancel=None):
    if not shutil.which("tesseract"):
        raise ValueError("OCR wymaga Tesseract. macOS: brew install tesseract tesseract-lang; Linux: apt install tesseract-ocr tesseract-ocr-pol")
    languages=subprocess.run(["tesseract","--list-langs"],capture_output=True,text=True,check=True).stdout
    language="pol+eng" if "pol" in languages.splitlines() else "eng"
    if cancel is None: return subprocess.run(["tesseract",str(path),"stdout","-l",language],capture_output=True,text=True,check=True,timeout=90).stdout
    from .audio import run_process
    with tempfile.TemporaryDirectory() as folder:
        output=Path(folder)/"ocr"
        run_process(["tesseract",str(path),str(output),"-l",language],cancel)
        return output.with_suffix(".txt").read_text()


def epub_images(path):
    from ebooklib import epub,ITEM_IMAGE,ITEM_DOCUMENT
    book=epub.read_epub(str(path),options={"ignore_ncx":True})
    chapters=[(i.get_name(),i.get_content().decode("utf-8","replace")) for i in book.get_items_of_type(ITEM_DOCUMENT)]
    results=[]
    for item in list(book.get_items_of_type(ITEM_IMAGE))[:500]:
        try:
            with Image.open(io.BytesIO(item.get_content())) as image: image.verify()
        except (OSError,ValueError): continue
        results.append({"name":item.get_name(),"bytes":item.get_content(),"chapters":[name for name,text in chapters if Path(item.get_name()).name in text]})
    return results
