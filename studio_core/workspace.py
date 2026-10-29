"""Explicit reuse of versioned bank resources; films retain independent snapshots."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import shutil

from .models import Project, Fact, Source, Asset, uid
from .development import Development, FilmIdea, StoryOption, ChannelBaseline, Chapter
from .workspace_models import Category, Resource, ResourceLink, Preset, FilmTemplate
from .store import atomic_json, now, Conflict
from .voices import Voices


class Workspace:
    def __init__(self, store):
        self.store = store
        self.root = store.root / "workspace"
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, group, identity):
        prefix = "cat" if group == "categories" else "res"
        if not re.fullmatch(prefix + r"_[a-f0-9]{16}", identity):
            raise ValueError("Niepoprawny identyfikator pracowni")
        return self.root / group / (identity + ".json")

    def categories(self, archived=False):
        rows = [Category.model_validate_json(p.read_text()) for p in (self.root / "categories").glob("cat_*.json")]
        return [c for c in rows if archived or not c.archived]

    def category(self, identity):
        return Category.model_validate_json(self.path("categories", identity).read_text())

    def save_category(self, body):
        item = Category.model_validate(body)
        if item.channel_id and not any(c["id"] == item.channel_id for c in self.store.channels()):
            raise ValueError("Nie ma takiego kanału")
        with self.store.lock:
            path = self.path("categories", item.id)
            old = self.category(item.id) if path.exists() else None
            if item.revision != (old.revision if old else 0):
                raise Conflict("Kategoria zmieniła się. Wczytaj aktualną wersję.")
            item.revision += 1
            atomic_json(path, item.model_dump())
        return item

    def defaults(self):
        path = self.root / "defaults.json"
        return json.loads(path.read_text()) if path.exists() else {"revision": 0, "preset": {}}

    def save_defaults(self, body):
        preset = Preset.model_validate(body.get("preset", {}))
        with self.store.lock:
            previous = self.defaults()
            if body.get("revision") != previous["revision"]:
                raise Conflict("Ustawienia pracowni zmieniły się")
            value = {"revision": previous["revision"] + 1, "preset": preset.model_dump(exclude_none=True)}
            atomic_json(self.root / "defaults.json", value)
            return value

    def get(self, identity, revision=None):
        path = self.path("resources", identity)
        if revision is not None:
            if not isinstance(revision, int) or revision < 1:
                raise ValueError("Niepoprawna wersja zasobu")
            path = self.root / "versions" / identity / f"r{revision:08}.json"
        return Resource.model_validate_json(path.read_text())

    def resources(self, *, archived=False):
        values = [Resource.model_validate_json(p.read_text()) for p in (self.root / "resources").glob("res_*.json")]
        return sorted([v for v in values if archived or not v.archived], key=lambda v: v.updated_at, reverse=True)

    @staticmethod
    def summary(item):
        return item.model_dump(exclude={"payload"}) | {"facts": len(item.payload.get("facts", [])), "sources": len(item.payload.get("sources", [])), "assets": len(item.payload.get("assets", []))}

    def usages(self):
        result = {}
        for row in self.store.list(include_archived=True):
            p = self.store.get(row["id"])
            for link in p.resource_links:
                result.setdefault(link.resource_id, []).append({"project_id": p.id, "title": p.title, "published": p.published, "archived": p.archived, "revision": link.revision})
        return result

    def media_path(self, asset):
        if not re.fullmatch(r"[a-f0-9]{64}", asset.sha256):
            raise ValueError("Niepoprawna suma materiału")
        from .bundles import SAFE_FILE
        if not SAFE_FILE.fullmatch(asset.filename):
            raise ValueError("Niepoprawna nazwa pliku w banku")
        return self.root / "media" / (asset.sha256 + Path(asset.filename).suffix)

    def validate_payload(self, item):
        payload = item.payload
        if item.kind in ("fact", "source", "media"):
            if not set(payload) <= {"facts", "sources", "assets"}:
                raise ValueError("Zasób zawiera pola spoza banku wiedzy/mediów")
            p = Project(development={}, **payload)
            if item.kind == "fact" and len(p.facts) != 1:
                raise ValueError("Wpis faktu wymaga dokładnie jednego twierdzenia")
            if item.kind != "fact" and p.facts:
                raise ValueError("Fakty dodawaj jako osobne wpisy banku")
            if item.kind == "source" and len(p.sources) != 1:
                raise ValueError("Wpis źródła wymaga jednego źródła")
            if item.kind == "media" and (len(p.assets) != 1 or p.sources):
                raise ValueError("Wpis medium wymaga jednego materiału")
            for a in p.assets:
                if a.private:
                    raise ValueError("Prywatnych plików nie publikujemy w banku. Głosy wybieraj przez profile lektora.")
                path = self.media_path(a)
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != a.sha256:
                    raise ValueError("Brak zgodnego pliku w banku; udostępnij go z filmu lub wgraj do banku")
            return {k: [v.model_dump() for v in getattr(p, k)] for k in ("facts", "sources", "assets")}
        if item.kind == "idea":
            idea = FilmIdea.model_validate(payload)
            if idea.stories:
                raise ValueError("Poczekalnia przechowuje temat. Historie i ich oceny należą do filmu.")
            return idea.model_dump()
        if item.kind == "template":
            return FilmTemplate.model_validate(payload).model_dump()
        if item.kind == "baseline":
            return ChannelBaseline.model_validate(payload).model_dump()
        if set(payload) != {"text"} or not isinstance(payload["text"], str) or len(payload["text"]) > 20000:
            raise ValueError("Notatka wymaga tekstu do 20 000 znaków")
        return payload

    def save(self, body):
        item = Resource.model_validate(body)
        if item.channel_id and not any(c["id"] == item.channel_id for c in self.store.channels()):
            raise ValueError("Nie ma takiego kanału")
        for cid in item.category_ids:
            category = self.category(cid)
            if category.archived:
                raise ValueError("Kategoria jest zarchiwizowana")
        item.payload = self.validate_payload(item)
        if len(json.dumps(item.model_dump(), ensure_ascii=False).encode()) > 8 * 1024 * 1024:
            raise ValueError("Wpis banku przekracza 8 MB")
        with self.store.lock:
            path = self.path("resources", item.id)
            old = self.get(item.id) if path.exists() else None
            if item.revision != (old.revision if old else 0):
                raise Conflict("Wpis banku zmienił się. Wczytaj aktualną wersję.")
            if old and item.kind != old.kind:
                raise ValueError("Nie zmieniaj rodzaju istniejącego zasobu")
            if old and item.kind == "fact":
                before, after = old.payload["facts"][0], item.payload["facts"][0]
                if any(before.get(k) != after.get(k) for k in ("claim", "source", "url", "page", "quote", "source_id")) or old.payload["sources"] != item.payload["sources"]:
                    after["status"] = "UNVERIFIED"
                    after["checked_at"] = ""
            item.revision += 1
            item.created_at = old.created_at if old else now()
            item.updated_at = now()
            atomic_json(self.root / "versions" / item.id / f"r{item.revision:08}.json", item.model_dump())
            atomic_json(path, item.model_dump())
        return item

    def publish(self, pid, body):
        p = self.store.get(pid)
        if p.revision != int(body["expected_revision"]):
            raise Conflict("Film zmienił się przed udostępnieniem zasobu")
        kind, identity = body["kind"], body["item_id"]
        payload = {}
        if kind in ("fact", "source", "media"):
            facts = [f for f in p.facts if f.id == identity] if kind == "fact" else []
            sources = [s for s in p.sources if s.id == (facts[0].source_id if facts else identity)] if kind != "media" else []
            aids = {identity} if kind == "media" else {a for s in sources for a in (s.asset_id, s.original_asset_id) if a}
            assets = [a for a in p.assets if a.id in aids]
            if (kind == "fact" and not facts) or (kind == "source" and not sources) or (kind == "media" and not assets):
                raise ValueError("Nie ma wybranego elementu filmu")
            for a in assets:
                if a.private:
                    raise ValueError("Prywatny plik nie może trafić do banku")
                source = self.store.folder(pid) / "media" / a.filename
                if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != a.sha256:
                    raise ValueError("Brak zgodnego oryginału materiału")
                target = self.media_path(a)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copyfile(source, target)
                if a.thumbnail:
                    thumb = source.parent / a.thumbnail
                    if thumb.is_file():
                        shutil.copyfile(thumb, target.with_suffix(".thumb.jpg"))
            payload = {"facts": [f.model_dump() for f in facts], "sources": [s.model_dump() for s in sources], "assets": [a.model_dump() for a in assets]}
        elif kind == "idea":
            idea = next((i for i in p.development.ideas if i.id == identity), None)
            if not idea:
                raise ValueError("Nie ma takiego pomysłu")
            payload = idea.model_dump() | {"stories": []}
        elif kind == "template":
            story = next((s for i in p.development.ideas for s in i.stories if s.id == identity), None)
            if not story:
                raise ValueError("Nie ma takiego planu")
            chapters = []
            for ci, c in enumerate(story.chapters):
                chapters.append(Chapter(title=f"Rozdział {ci+1}", sections=[{"title": f"Część {si+1}", "seconds": s.seconds, "energy": s.energy} for si, s in enumerate(c.sections)]).model_dump())
            payload = {"preset": {"target_minutes": p.development.target_minutes}, "chapters": chapters}
        elif kind == "baseline":
            payload = p.development.baseline.model_dump()
        else:
            raise ValueError("Nieobsługiwane udostępnienie")
        metadata = {k: body[k] for k in ("title", "scope", "channel_id", "category_ids", "tags", "context") if k in body}
        metadata.setdefault("title", (facts[0].claim[:200] if kind == "fact" else sources[0].title[:200] if kind == "source" else assets[0].name[:200] if kind == "media" else "Zasób z filmu"))
        return self.save(metadata | {"kind": kind, "payload": payload, "origin_project_id": pid, "origin_item_id": identity})

    def effective(self, channel_id="", category_id="", template_id=""):
        defaults = self.defaults()
        values = dict(defaults["preset"])
        snapshots = {"workspace": copy.deepcopy(defaults)}
        channel = next((c for c in self.store.channels() if c["id"] == channel_id), None)
        if channel_id and not channel:
            raise ValueError("Wybierz istniejący kanał")
        if channel:
            snapshots["channel"] = channel
            values.update({k: v for k, v in channel.items() if k in Preset.model_fields})
        if category_id:
            category = self.category(category_id)
            if category.archived or category.channel_id and category.channel_id != channel_id:
                raise ValueError("Kategoria nie pasuje do wybranego kanału")
            snapshots["category"] = category.model_dump()
            values.update(category.defaults.model_dump(exclude_none=True))
        if template_id:
            resource = self.get(template_id)
            if resource.archived or resource.kind != "template":
                raise ValueError("Wybierz aktywny szablon")
            template = FilmTemplate.model_validate(resource.payload)
            values.update(template.preset.model_dump(exclude_none=True))
            snapshots["template"] = resource.model_dump()
        return Preset.model_validate(values), snapshots

    @staticmethod
    def apply_preset(p, preset):
        values = preset.model_dump(exclude_none=True)
        for key in ("audience", "viewer_promise", "references", "constraints", "target_minutes"):
            if key in values:
                setattr(p.development, key, values[key])
        for key in ("narrative_style", "visual_style", "font", "color"):
            if key in values:
                p.channel_profile[key] = values[key]
        for key in ("width", "height", "fps_num", "fps_den", "ducking", "ducking_gain"):
            if key in values:
                setattr(p.sequence, key, values[key])
        if "language" in values:
            p.language = values["language"]
        if "pronunciation" in values:
            p.pronunciation = copy.deepcopy(values["pronunciation"])
        if values.get("voice_id"):
            p.voice_profile = {"id": values["voice_id"]}

    def new_project(self, body):
        allowed = {"title", "language", "channel_id", "category_id", "template_id", "film_format", "production_mode"}
        if not set(body) <= allowed:
            raise ValueError("Nowy film przyjmuje wyłącznie nazwę i wybrane ustawienia. Treść dobierz później z banku.")
        preset, snapshots = self.effective(body.get("channel_id", ""), body.get("category_id", ""), body.get("template_id", ""))
        p = Project(title=str(body.get("title") or "Nowy film").strip() or "Nowy film", development=Development(), channel_id=body.get("channel_id", ""), category_id=body.get("category_id", ""), film_format=str(body.get("film_format", ""))[:100], workspace_snapshot=snapshots)
        if "channel" in snapshots:
            p.channel = snapshots["channel"]["name"]
            p.channel_profile = copy.deepcopy(snapshots["channel"])
        p.category_profile = snapshots.get("category", {})
        self.apply_preset(p, preset)
        if preset.voice_id:
            Voices(self.store.root).get(preset.voice_id)
        if body.get("language"):
            p.language = str(body["language"])
        p.production_mode = body.get("production_mode") or snapshots.get("channel", {}).get("production_mode", "documentary")
        if p.production_mode not in ("documentary", "animation_2d", "broll"):
            raise ValueError("Nieznany tryb produkcji")
        if p.production_mode == "animation_2d" and not p.channel_id:
            raise ValueError("Film animowany wymaga kanału: postacie i lokacje należą do banku kanału")
        if body.get("template_id"):
            template = snapshots["template"]
            self.apply_template_structure(p, template["payload"])
            p.resource_links.append(ResourceLink(resource_id=template["id"], revision=template["revision"], kind="template", title=template["title"], imported_at=now()))
        return self.store.create(p)

    @staticmethod
    def apply_template_structure(p, payload):
        template = FilmTemplate.model_validate(payload)
        if not template.chapters:
            return
        chapters = copy.deepcopy(template.chapters)
        for c in chapters:
            c.id = uid("chapter_")
            for s in c.sections:
                s.id = uid("section_")
        p.development.ideas.append(FilmIdea(title=p.title, stories=[StoryOption(title="Plan do wypełnienia ze szablonu", chapters=chapters)]))

    @staticmethod
    def source_fingerprint(source):
        return hashlib.sha256(json.dumps(source.model_dump(include={"title", "provider", "url", "author", "edition", "identifier", "text", "pages"}), sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def import_resource(self, pid, rid, body):
        resource = self.get(rid, body.get("resource_revision"))
        latest = self.get(rid)
        if latest.archived:
            raise ValueError("Wpis banku jest zarchiwizowany")
        def apply(p):
            previous = next((v for v in p.resource_links if v.resource_id == rid), None)
            if previous and previous.revision == resource.revision:
                return
            if previous and not body.get("update"):
                raise ValueError("Film ma inną wersję tego zasobu. Porównaj i jawnie przyjmij aktualizację.")
            mapping = dict(previous.local_ids) if previous else {}
            payload = resource.payload
            if resource.kind in ("fact", "source", "media"):
                for raw in payload.get("assets", []):
                    asset = Asset.model_validate(raw)
                    existing = next((a for a in p.assets if a.sha256 == asset.sha256 and a.kind == asset.kind), None)
                    if existing:
                        mapping[asset.id] = existing.id
                        continue
                    source = self.media_path(asset)
                    if not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest() != asset.sha256:
                        raise ValueError("Plik banku jest niedostępny lub zmieniony")
                    target = self.store.folder(pid) / "media" / asset.filename
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != asset.sha256:
                        raise ValueError("Kolizja plików projektu")
                    shutil.copyfile(source, target)
                    if asset.thumbnail and source.with_suffix(".thumb.jpg").is_file():
                        shutil.copyfile(source.with_suffix(".thumb.jpg"), target.parent / asset.thumbnail)
                    asset.id = "asset_" + hashlib.sha256((rid + raw["id"] + asset.sha256).encode()).hexdigest()[:20]
                    asset.provenance = {**asset.provenance, "bank_resource_id": rid, "bank_revision": resource.revision}
                    mapping[raw["id"]] = asset.id
                    p.assets.append(asset)
                for raw in payload.get("sources", []):
                    source = Source.model_validate(raw)
                    original_id = source.id
                    signature = self.source_fingerprint(source)
                    same = next((s for s in p.sources if self.source_fingerprint(s) == signature), None)
                    source.id = same.id if same else mapping.get(original_id, uid("src_"))
                    source.asset_id = mapping.get(source.asset_id) if source.asset_id else None
                    source.original_asset_id = mapping.get(source.original_asset_id) if source.original_asset_id else None
                    source.metadata = {**source.metadata, "bank_resource_id": rid, "bank_revision": resource.revision}
                    mapping[original_id] = source.id
                    if not same:
                        p.sources = [s for s in p.sources if s.id != source.id] + [source]
                for raw in payload.get("facts", []):
                    fact = Fact.model_validate(raw)
                    original_id = fact.id
                    fact.id = mapping.get(original_id, uid("fact_"))
                    fact.source_id = mapping.get(fact.source_id) if fact.source_id else None
                    fact.provenance = {**fact.provenance, "bank_resource_id": rid, "bank_revision": resource.revision, "bank_status": raw["status"], "bank_checked_at": raw.get("checked_at", ""), "review_required": True}
                    fact.status = "UNVERIFIED"
                    fact.checked_at = ""
                    mapping[original_id] = fact.id
                    p.facts = [f for f in p.facts if f.id != fact.id] + [fact]
            elif resource.kind == "note":
                local_id = mapping.get("note", uid("src_"))
                source = Source(id=local_id, title=resource.title, provider="note", text=payload["text"], metadata={"kind": "research_note", "bank_resource_id": rid, "bank_revision": resource.revision})
                p.sources = [s for s in p.sources if s.id != local_id] + [source]
                mapping["note"] = local_id
            elif resource.kind == "idea":
                idea = FilmIdea.model_validate(payload)
                original_id = idea.id
                idea.id = mapping.get(original_id, uid("idea_"))
                p.development.ideas = [i for i in p.development.ideas if i.id != idea.id] + [idea]
                mapping[original_id] = idea.id
            elif resource.kind == "baseline":
                p.development.baseline = ChannelBaseline.model_validate(payload)
            elif resource.kind == "template":
                if not body.get("apply_settings") and not body.get("apply_structure"):
                    raise ValueError("Wybierz zakres zastosowania szablonu")
                template = FilmTemplate.model_validate(payload)
                if body.get("apply_settings"):
                    if p.scenes or p.sequence.clips:
                        raise ValueError("Ustawienia istniejącego montażu edytuj w filmie. Ten profil zastosuj do nowego projektu.")
                    self.apply_preset(p, template.preset)
                if body.get("apply_structure"):
                    self.apply_template_structure(p, payload)
            link = ResourceLink(resource_id=rid, revision=resource.revision, kind=resource.kind, title=resource.title, local_ids=mapping, imported_at=now())
            p.resource_links = [v for v in p.resource_links if v.resource_id != rid] + [link]
        return self.store.mutate(pid, int(body["expected_revision"]), apply)

    def links(self, pid):
        p = self.store.get(pid)
        result = []
        for link in p.resource_links:
            try:
                current = self.get(link.resource_id)
                result.append(link.model_dump() | {"latest_revision": current.revision, "archived": current.archived, "update_available": current.revision > link.revision})
            except FileNotFoundError:
                result.append(link.model_dump() | {"missing": True, "update_available": False})
        return result
