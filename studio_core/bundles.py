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
SAFE_FILE = re.compile(r"asset_[a-f0-9]{20}\.(?:png|jpe?g|gif|webp|mp4|webm|mov|mkv|ogv|wav|mp3|m4a|ogg|flac|aac|pdf|epub|txt|md|html|xml)$")


def export_bundle(store: ProjectStore, project: Project, *, max_asset_mb=300) -> Path:
    project=project.model_copy(deep=True);versions=[];assets={a.id:a for a in project.assets}
    for path in sorted((store.folder(project.id)/"versions").glob("version_*.json")):
        if not re.fullmatch(r"version_[a-f0-9]{16}\.json",path.name):continue
        value=json.loads(path.read_text());variant=Project.model_validate(value["project"])
        versions.append((path.name,value));assets.update({a.id:a for a in variant.assets if a.id not in assets})
    project.assets=list(assets.values())
    folder = store.folder(project.id) / "exports"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"project-r{project.revision}-{uid()}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("project.json", json.dumps(project.model_dump(), ensure_ascii=False, indent=2))
        if archive.getinfo("project.json").file_size>8*1024*1024:raise ValueError("Projekt przekracza 8 MB. Ogranicz liczbę materiałów lub długość dołączonych źródeł.")
        manifest={"schema":"docos-bundle/2","revision":project.revision,"project_sha256":hashlib.sha256(archive.read("project.json")).hexdigest(),"files":[],"versions":[],"omitted":[]}
        for name,value in versions:
            raw=json.dumps(value,ensure_ascii=False,indent=2).encode()
            if len(raw)>8*1024*1024:raise ValueError("Wariant przekracza 8 MB")
            archive.writestr("versions/"+name,raw);manifest["versions"].append({"path":"versions/"+name,"sha256":hashlib.sha256(raw).hexdigest()})
        for asset in project.assets:
            if not SAFE_FILE.fullmatch(asset.filename):
                raise ValueError("Niepoprawna ścieżka materiału w projekcie")
            path = store.folder(project.id) / "media" / asset.filename
            total=sum(item.file_size for item in archive.infolist())
            reason="private" if asset.private else "missing" if not path.is_file() else "large" if path.stat().st_size>max_asset_mb*1024*1024 else "bundle-limit" if total+path.stat().st_size>MAX_BUNDLE-8*1024*1024 or len(archive.filelist)>1900 else ""
            if reason:
                manifest["omitted"].append({"asset_id":asset.id,"filename":asset.filename,"reason":reason,"sha256":asset.sha256})
                continue
            if not path.is_file():
                raise ValueError("Brak materiału do spakowania: " + asset.name)
            if hashlib.sha256(path.read_bytes()).hexdigest()!=asset.sha256: raise ValueError("Suma kontrolna materiału nie zgadza się z projektem")
            archive.write(path, "media/" + asset.filename)
            manifest["files"].append({"path":"media/"+asset.filename,"sha256":asset.sha256,"size":path.stat().st_size})
            if asset.thumbnail and re.fullmatch(r"asset_[a-f0-9]{20}\.thumb\.jpg", asset.thumbnail):
                thumb = path.parent / asset.thumbnail
                if thumb.is_file():
                    archive.write(thumb, "media/" + asset.thumbnail)
        archive.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
        archive.writestr("README.txt","DocOS Studio backup r"+str(project.revision)+"\nImportuj ZIP w ekranie Projekty. Lista omitted w manifest.json opisuje pliki do ponownego dołączenia. Prywatne próbki głosu i klucze połączeń nie są przenoszone.\n")
        if sum(item.file_size for item in archive.infolist())>MAX_BUNDLE or len(archive.infolist())>2000:raise ValueError("Pakiet przekracza limit. Ogranicz liczbę wariantów lub wielkość materiałów.")
    return output


def import_bundle(store: ProjectStore, path: Path) -> Project:
    with zipfile.ZipFile(path) as archive:
        if len(archive.infolist()) > 2000 or sum(i.file_size for i in archive.infolist()) > MAX_BUNDLE:
            raise ValueError("Pakiet przekracza limit dwóch gigabajtów lub dwóch tysięcy plików")
        if archive.getinfo("project.json").file_size > 8 * 1024 * 1024:
            raise ValueError("Manifest projektu jest zbyt duży")
        data = json.loads(archive.read("project.json"))
        manifest=json.loads(archive.read("manifest.json")) if "manifest.json" in archive.namelist() else {}
        if manifest and hashlib.sha256(archive.read("project.json")).hexdigest()!=manifest.get("project_sha256"):
            raise ValueError("Suma kontrolna projektu w pakiecie jest niepoprawna")
        omitted={x["filename"] for x in manifest.get("omitted",[])}
        project = Project.model_validate({k: v for k, v in data.items() if not k.startswith("_")})
        project.id = uid("prj_"); project.revision = 0; project.demo = False
        project.story["status"] = "DRAFT"; project.story["approved_hash"] = ""
        versions=[]
        for item in manifest.get("versions",[]):
            name=item["path"]
            if not re.fullmatch(r"versions/version_[a-f0-9]{16}\.json",name) or archive.getinfo(name).file_size>8*1024*1024:raise ValueError("Niepoprawny wariant w pakiecie")
            raw=archive.read(name)
            if hashlib.sha256(raw).hexdigest()!=item["sha256"]:raise ValueError("Suma kontrolna wariantu jest niepoprawna")
            value=json.loads(raw);variant=Project.model_validate(value["project"])
            if value.get("id")!=Path(name).stem:raise ValueError("Identyfikator wariantu nie zgadza się z plikiem")
            if not {a.id for a in variant.assets}<={a.id for a in project.assets}:raise ValueError("Wariant wskazuje materiał spoza manifestu")
            variant.id=project.id;variant.story["status"]="DRAFT";variant.story["approved_hash"]=""
            versions.append((Path(name).name,{**value,"project":variant.model_dump()}))
        with tempfile.TemporaryDirectory(dir=store.root) as temporary:
            staging = Path(temporary)
            for asset in project.assets:
                if not SAFE_FILE.fullmatch(asset.filename):
                    raise ValueError("Niepoprawna nazwa pliku w pakiecie")
                if asset.filename in omitted:
                    asset.thumbnail=""
                    continue
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
            for name,value in versions:
                from .store import atomic_json
                atomic_json(folder.parent/"versions"/name,value)
            return store.create(project)
