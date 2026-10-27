"""Input fingerprints shared by the editor, workers and final-export checks."""
from __future__ import annotations

from collections import defaultdict, deque
import hashlib
import json
import re
import os
from pathlib import Path
from functools import lru_cache

from .models import Project, Scene, VoiceSentence


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def voice_config(project: Project, scene: Scene) -> dict:
    profile = {**project.voice_profile, **scene.voice_profile}
    defaults = {"model": "chatterbox-multilingual", "exaggeration": .5, "cfg_weight": .4, "temperature": .7, "pause": .25, "seed": 42}
    result = {key: profile.get(key,value) for key,value in defaults.items()}
    if profile.get("device","auto")!="auto": result["device"]=profile["device"]
    result["reference_sha256"] = profile.get("reference_sha256", "")
    if not result["reference_sha256"]:
        reference = Path(os.environ.get("DOCOS_VOICE_REF", Path(__file__).resolve().parents[1]/"pilot/assets/ref_clean.wav"))
        if reference.is_file():
            stat = reference.stat()
            result["reference_sha256"] = reference_digest(str(reference), stat.st_mtime_ns, stat.st_size)
    return result


@lru_cache(maxsize=32)
def reference_digest(path, modified, size):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spoken(project: Project, text: str) -> str:
    for word, replacement in sorted(project.pronunciation.items(), key=lambda item: -len(item[0])):
        text = re.sub(r"(?<!\w)" + re.escape(word) + r"(?!\w)", lambda _: replacement, text)
    return text


def sentence_hash(project: Project, scene: Scene, text: str) -> str:
    return fingerprint({"text": spoken(project, text), "language": project.language, "voice": voice_config(project, scene)})


def voice_hash(project: Project, scene: Scene) -> str:
    return sentence_hash(project, scene, scene.narration)


def image_config(scene):
    config={key:scene.generation.get(key,value) for key,value in {"seed":42,"width":768,"height":448,"steps":25}.items()}
    if any(isinstance(v,bool) or not isinstance(v,int) for v in config.values()):raise ValueError("Parametry obrazu wymagają liczb całkowitych")
    if not 0<=config["seed"]<2**31 or not 1<=config["steps"]<=75 or any(not 256<=config[k]<=1024 or config[k]%8 for k in ("width","height")):raise ValueError("Obraz: rozmiar 256–1024 co 8 px, kroki 1–75, ziarno 0–2147483647")
    return config


def image_prompt(project,scene):return scene.prompt+(". "+str(project.channel_profile["visual_style"]) if project.channel_profile.get("visual_style") else "")


def image_hash(project,scene):return fingerprint({"model":"stable-diffusion-v1-5","prompt":image_prompt(project,scene),"config":image_config(scene)})


def voice_state(project: Project, scene: Scene) -> str:
    if not scene.narration.strip():
        return "empty"
    if not scene.voice_asset_id:
        return "missing"
    return "current" if scene.voice_input_hash == voice_hash(project, scene) else "stale"


def evidence_hash(project,scene):
    facts=[f.model_dump() for f in project.facts if f.id in scene.fact_ids]
    ids={f["source_id"] for f in facts if f.get("source_id")}
    return fingerprint({"title":project.title,"story":{k:v for k,v in project.story.items() if k!="status" and not k.startswith("approved_")},"facts":facts,"sources":[s.model_dump() for s in project.sources if s.id in ids]})


def reconcile(before: Project, project: Project) -> None:
    old = {scene.id: scene for scene in before.scenes}
    assets = {a.id: a for a in project.assets}
    for scene in project.scenes:
        previous = old.get(scene.id)
        if previous is None or previous.narration!=scene.narration or previous.fact_ids!=scene.fact_ids:
            scene.script_input_hash=evidence_hash(project,scene)
        elif not scene.script_input_hash:
            scene.script_input_hash=evidence_hash(before,previous)
        if scene.voice_asset_id and (previous is None or previous.voice_asset_id != scene.voice_asset_id):
            asset = assets.get(scene.voice_asset_id)
            scene.voice_input_hash = str(asset.provenance.get("voice_hash") or voice_hash(project, scene)) if asset else ""
        if previous and (voice_hash(before, previous) != voice_hash(project, scene) or previous.voice_asset_id != scene.voice_asset_id):
            scene.words = []
            scene.alignment_hash = ""
        buckets = defaultdict(deque)
        for sentence in scene.sentences:
            buckets[sentence.text].append(sentence)
        sentences = []
        for text in re.split(r"(?<=[.!?])\s+|\n+", scene.narration.strip()):
            text = text.strip()
            if text:
                sentence = buckets[text].popleft() if buckets[text] else VoiceSentence(text=text)
                sentence.spoken_text = spoken(project, text)
                sentences.append(sentence)
        scene.sentences = sentences
