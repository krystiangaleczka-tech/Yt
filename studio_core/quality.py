from collections import Counter

from .freshness import voice_state,evidence_hash,image_hash
from .models import fps, duration
from .store import story_hash
from .templates import MEDIA_TEMPLATES, validate_parameters


def check_project(store, project):
    issues = []
    def add(code, message, severity="warning", scene_id=None):
        issues.append({"code": code, "type": code.split(":")[0], "severity": severity, "message": message,
                       "scene_id": scene_id, "accepted": code in project.accepted_warnings})
    if project.story.get("status") != "APPROVED" or project.story.get("approved_hash") != story_hash(project):
        add("story", "Historia czeka na zatwierdzenie")
    if not project.sequence.clips:
        add("timeline", "Oś czasu jest pusta", "error")
    assets = {a.id: a for a in project.assets}
    tracks = {t.id: t for t in project.sequence.tracks}
    used = {c.asset_id for c in project.sequence.clips if c.asset_id}
    used |= {a for c in project.sequence.clips for a in c.asset_ids}
    for scene in project.scenes:
        if not scene.asset_id and scene.template in MEDIA_TEMPLATES:
            add("media:"+scene.id, scene.title+": brak wybranego materiału", scene_id=scene.id)
        state = voice_state(project, scene)
        if scene.narration and scene.script_input_hash and scene.script_input_hash!=evidence_hash(project,scene):
            add("script_dependency:"+scene.id,scene.title+": sprawdź narrację po zmianie historii lub dowodów",scene_id=scene.id)
        if state == "missing":
            add("voice:"+scene.id, scene.title+": brak nagrania narracji", scene_id=scene.id)
        elif state == "stale":
            add("stale_voice:"+scene.id, scene.title+": nagranie jest nieaktualne po zmianie tekstu, języka lub głosu", "error", scene.id)
        elif state == "current":
            matches = [c for c in project.sequence.clips if c.scene_id == scene.id and tracks[c.track_id].role == "narration" and c.asset_id == scene.voice_asset_id and not tracks[c.track_id].muted]
            if not matches:
                add("voice_timeline:"+scene.id, scene.title+": zastosuj wybrane nagranie w montażu", "error", scene.id)
        if any(w.get("probability",1)<.6 and not w.get("reviewed") for w in scene.words):
            add("captions_review:"+scene.id,scene.title+": sprawdź słowa rozpoznane z małą pewnością",scene_id=scene.id)
        if scene.template in {"quote", "press", "counter", "qa", "diagram", "map", "timeline"} and not scene.fact_ids and not project.demo:
            add("screen_fact:"+scene.id, scene.title+": wskaż źródła twierdzeń pokazywanych na ekranie", scene_id=scene.id)
        params = validate_parameters(scene.template, scene.parameters)
        chosen=assets.get(scene.asset_id)
        if chosen and chosen.provenance.get("image_hash") and chosen.provenance["image_hash"]!=image_hash(project,scene):add("stale_image:"+scene.id,scene.title+": obraz pochodzi z poprzedniego promptu, stylu lub ustawień",scene_id=scene.id)
        if scene.template in {"title", "quote", "press", "slogan"} and not params.get("text", "").strip():
            add("template:"+scene.id, scene.title+": uzupełnij treść planszy", "error", scene.id)
        if scene.template == "parallax" and len(scene.asset_ids) < 2:
            add("layers:"+scene.id, scene.title+": parallax wymaga tła i wyciętej warstwy PNG", "error", scene.id)
        for fact_id in scene.fact_ids:
            fact = next(f for f in project.facts if f.id == fact_id)
            if fact.status == "UNVERIFIED":
                add("fact:"+fact.id, "Wykorzystany fakt wymaga sprawdzenia: "+fact.claim[:100], scene_id=scene.id)
            elif fact.status == "DISPUTED" and not fact.note.strip():
                add("dispute:"+fact.id, "Wyjaśnij spór przy fakcie: "+fact.claim[:100], "error", scene.id)
    for asset_id in used:
        asset = assets.get(asset_id)
        if not asset:
            add("asset:"+str(asset_id), "Nieznany materiał na osi czasu", "error")
            continue
        if not (store.folder(project.id)/"media"/asset.filename).is_file():
            add("file:"+asset.id, "Brak pliku: "+asset.name, "error")
        if asset.kind in ("image", "video", "audio") and not asset.license and asset.provenance.get("kind") not in ("voice","voice_sentence","image"):
            add("license:"+asset.id, "Uzupełnij warunki użycia materiału: "+asset.name)
        if asset.kind == "image" and asset.width < project.sequence.width // 2:
            add("resolution:"+asset.id, "Mała rozdzielczość obrazu: "+asset.name)
    count = Counter(c.asset_id for c in project.sequence.clips if c.asset_id and tracks[c.track_id].kind == "video")
    for asset_id, uses in count.items():
        if uses > 2:
            add("repetition:"+asset_id, f"Materiał użyty {uses} razy: "+assets[asset_id].name, "suggestion")
    return {"issues": issues, "duration": duration(project), "fps": fps(project), "voice": {s.id: voice_state(project, s) for s in project.scenes},
            "blocking": [i for i in issues if i["severity"] == "error" or i["severity"] == "warning" and not i["accepted"]]}
