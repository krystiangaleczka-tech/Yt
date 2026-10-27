"""Private voice references are stored outside projects and portable bundles."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from .models import uid
from .store import atomic_json, now
from .media import probe

DEFAULT_CONFIG = {"model": "chatterbox-multilingual", "device":"auto", "exaggeration": .5, "cfg_weight": .4, "temperature": .7, "pause": .25, "seed": 42}


class Voices:
    def __init__(self, root):
        self.root = root/"voice-profiles"
        self.root.mkdir(parents=True,exist_ok=True)

    def folder(self, voice_id):
        if not re.fullmatch(r"voice_[a-f0-9]{16}",voice_id):
            raise ValueError("Niepoprawny profil głosu")
        return self.root/voice_id

    def list(self):
        return [json.loads(path.read_text()) for path in self.root.glob("voice_*/profile.json")]

    def get(self, voice_id):
        return json.loads((self.folder(voice_id)/"profile.json").read_text())

    def create(self, name, reference, settings=None):
        info=probe(reference)
        duration=float(info["format"]["duration"])
        if not 3<=duration<=120:
            raise ValueError("Próbka głosu musi mieć od 3 do 120 sekund")
        voice_id=uid("voice_"); folder=self.folder(voice_id); folder.mkdir(parents=True)
        path=folder/"reference.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(reference),"-ac","1","-ar","24000","-af","highpass=f=70,lowpass=f=11000,loudnorm=I=-20:TP=-2:LRA=7",str(path)],check=True,capture_output=True)
        path.chmod(0o600)
        config={**DEFAULT_CONFIG,**(settings or {})}
        self.validate(config)
        value={"id":voice_id,"name":str(name).strip()[:100] or "Mój głos","reference_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"duration":float(probe(path)["format"]["duration"]),"created_at":now(),**config}
        atomic_json(folder/"profile.json",value); (folder/"profile.json").chmod(0o600)
        return value

    def update(self, voice_id, changes):
        value=self.get(voice_id)
        if not set(changes)<={"name",*DEFAULT_CONFIG}:
            raise ValueError("Nieznane parametry profilu")
        value.update(changes); self.validate(value)
        atomic_json(self.folder(voice_id)/"profile.json",value)
        return value

    @staticmethod
    def validate(config):
        if config.get("model")!="chatterbox-multilingual": raise ValueError("Nieobsługiwany model głosu")
        if config.get("device","auto") not in ("auto","cpu","mps","cuda"): raise ValueError("Nieobsługiwane urządzenie głosu")
        for name,low,high in (("exaggeration",0,2),("cfg_weight",0,1),("temperature",.05,2),("pause",0,2),("seed",0,2**31-1)):
            if not isinstance(config.get(name),(float,int)) or not low<=config[name]<=high:
                raise ValueError("Parametr głosu poza zakresem: "+name)

    def reference(self, profile):
        if profile.get("id"):
            return self.folder(profile["id"])/"reference.wav"
        return Path(os.environ.get("DOCOS_VOICE_REF",Path(__file__).resolve().parents[1]/"pilot/assets/ref_clean.wav"))


def alignment_hash(project, scene):
    from .freshness import fingerprint, voice_hash
    asset=next((a for a in project.assets if a.id==scene.voice_asset_id),None)
    return fingerprint({"voice":voice_hash(project,scene),"audio":asset.sha256 if asset else ""})
