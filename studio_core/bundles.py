"""Portable project packages. Only manifest-listed media are read or written."""
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from .models import Project, uid
from .store import ProjectStore

MAX_BUNDLE = 2 * 1024 * 1024 * 1024
SAFE_FILE = re.compile(r"asset_[a-f0-9]{20}\.(?:png|jpe?g|gif|webp|mp4|webm|mov|mkv|ogv|wav|mp3|m4a|ogg|flac|aac|pdf|epub|txt|md)$")


def export_bundle(store: ProjectStore, project: Project) -> Path:
    folder = store.folder(project.id) / "exports"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"project-r{project.revision}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("project.json", json.dumps(project.model_dump(), ensure_ascii=False, indent=2))
        for asset in project.assets:
            if not SAFE_FILE.fullmatch(asset.filename):
                raise ValueError("Niepoprawna ścieżka materiału w projekcie")
            path = store.folder(project.id) / "media" / asset.filename
            if not path.is_file():
                raise ValueError("Brak materiału do spakowania: " + asset.name)
            archive.write(path, "media/" + asset.filename)
            if asset.thumbnail and re.fullmatch(r"asset_[a-f0-9]{20}\.thumb\.jpg", asset.thumbnail):
                thumb = path.parent / asset.thumbnail
                if thumb.is_file():
                    archive.write(thumb, "media/" + asset.thumbnail)
    return output


def import_bundle(store: ProjectStore, path: Path) -> Project:
    with zipfile.ZipFile(path) as archive:
        if len(archive.infolist()) > 2000 or sum(i.file_size for i in archive.infolist()) > MAX_BUNDLE:
            raise ValueError("Pakiet przekracza limit dwóch gigabajtów lub dwóch tysięcy plików")
        if archive.getinfo("project.json").file_size > 8 * 1024 * 1024:
            raise ValueError("Manifest projektu jest zbyt duży")
        data = json.loads(archive.read("project.json"))
        project = Project.model_validate({k: v for k, v in data.items() if not k.startswith("_")})
        project.id = uid("prj_"); project.revision = 0; project.demo = False
        project.story["status"] = "DRAFT"; project.story["approved_hash"] = ""
        with tempfile.TemporaryDirectory(dir=store.root) as temporary:
            staging = Path(temporary)
            for asset in project.assets:
                if not SAFE_FILE.fullmatch(asset.filename):
                    raise ValueError("Niepoprawna nazwa pliku w pakiecie")
                with archive.open("media/" + asset.filename) as source, (staging / asset.filename).open("wb") as target:
                    shutil.copyfileobj(source, target)
                with (staging / asset.filename).open("rb") as source:
                    if hashlib.file_digest(source, "sha256").hexdigest() != asset.sha256:
                        raise ValueError("Suma kontrolna materiału nie zgadza się z projektem")
                if asset.thumbnail:
                    if not re.fullmatch(r"asset_[a-f0-9]{20}\.thumb\.jpg", asset.thumbnail):
                        raise ValueError("Niepoprawna miniatura w pakiecie")
                    name = "media/" + asset.thumbnail
                    if name in archive.namelist():
                        with archive.open(name) as source, (staging / asset.thumbnail).open("wb") as target:
                            shutil.copyfileobj(source, target)
                    else:
                        asset.thumbnail = ""
            folder = store.folder(project.id) / "media"
            folder.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(staging, folder)
            return store.create(project)
