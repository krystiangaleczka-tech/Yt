"""Film ideas, alternative stories and transparent channel-relative scenarios."""
from __future__ import annotations

import hashlib
import json
import math
from statistics import median, stdev, NormalDist
from typing import Literal

from pydantic import Field, model_validator
from .models_base import Model, uid


class EditorialScore(Model):
    hook: int = Field(default=50, ge=0, le=100)
    audience_fit: int = Field(default=50, ge=0, le=100)
    originality: int = Field(default=50, ge=0, le=100)
    visuals: int = Field(default=50, ge=0, le=100)
    retention: int = Field(default=50, ge=0, le=100)
    evergreen: int = Field(default=50, ge=0, le=100)


class Assumptions(Model):
    reach_low: float = Field(default=.5, ge=.05, le=100)
    reach_base: float = Field(default=1, ge=.05, le=100)
    reach_high: float = Field(default=2, ge=.05, le=100)
    ctr_delta: float = Field(default=0, ge=-20, le=20)
    retention_delta: float = Field(default=0, ge=-50, le=50)
    reason: str = Field(default="Neutralny scenariusz roboczy; dostosuj po analizie tematu i opakowania.", max_length=3000)

    @model_validator(mode="after")
    def ordered(self):
        if not self.reach_low <= self.reach_base <= self.reach_high:
            raise ValueError("Scenariusze zasięgu muszą rosnąć: ostrożny ≤ bazowy ≤ optymistyczny")
        return self


class Subchapter(Model):
    id: str = Field(default_factory=lambda: uid("section_"), pattern=r"^section_[a-f0-9]{16}$")
    title: str = Field(default="Nowy podrozdział", min_length=1, max_length=200)
    purpose: str = Field(default="", max_length=3000)
    question: str = Field(default="", max_length=1000)
    turn: str = Field(default="", max_length=1000)
    retention_plan: str = Field(default="", max_length=2000)
    evidence_needed: str = Field(default="", max_length=2000)
    seconds: int = Field(default=60, ge=5, le=3600)
    energy: int = Field(default=5, ge=1, le=10)
    fact_ids: list[str] = Field(default_factory=list, max_length=100)


class Chapter(Model):
    id: str = Field(default_factory=lambda: uid("chapter_"), pattern=r"^chapter_[a-f0-9]{16}$")
    title: str = Field(default="Nowy rozdział", min_length=1, max_length=200)
    purpose: str = Field(default="", max_length=2000)
    sections: list[Subchapter] = Field(default_factory=list, max_length=30)


class StoryOption(Model):
    id: str = Field(default_factory=lambda: uid("outline_"), pattern=r"^outline_[a-f0-9]{16}$")
    title: str = Field(default="Nowy wariant historii", min_length=1, max_length=200)
    origin: Literal["manual", "ai", "legacy"] = "manual"
    synopsis: str = Field(default="", max_length=6000)
    central_question: str = Field(default="", max_length=1500)
    hook: str = Field(default="", max_length=2000)
    stakes: str = Field(default="", max_length=2000)
    payoff: str = Field(default="", max_length=2000)
    title_pitch: str = Field(default="", max_length=300)
    thumbnail: str = Field(default="", max_length=2000)
    evergreen_reason: str = Field(default="", max_length=2000)
    rationale: str = Field(default="", max_length=3000)
    risks: list[str] = Field(default_factory=list, max_length=20)
    evidence_gaps: list[str] = Field(default_factory=list, max_length=20)
    scores: EditorialScore = Field(default_factory=EditorialScore)
    assumptions: Assumptions = Field(default_factory=Assumptions)
    chapters: list[Chapter] = Field(default_factory=list, max_length=30)
    applied_hash: str = ""


class FilmIdea(Model):
    id: str = Field(default_factory=lambda: uid("idea_"), pattern=r"^idea_[a-f0-9]{16}$")
    title: str = Field(default="Nowy pomysł", min_length=1, max_length=200)
    question: str = Field(default="", max_length=1500)
    angle: str = Field(default="", max_length=3000)
    notes: str = Field(default="", max_length=4000)
    origin: Literal["manual", "ai", "legacy"] = "manual"
    stories: list[StoryOption] = Field(default_factory=list, max_length=20)


class ChannelBaseline(Model):
    typical_views_30d: int | None = Field(default=None, ge=0, le=10**12)
    views_30d: list[int] = Field(default_factory=list, max_length=200)
    ctr: float | None = Field(default=None, ge=0, le=100)
    retention: float | None = Field(default=None, ge=0, le=100)
    comparable_minutes: float | None = Field(default=None, gt=0, le=360)
    success_multiple: float = Field(default=1.5, ge=1, le=100)
    viral_multiple: float = Field(default=5, ge=1, le=1000)
    evidence: str = Field(default="", max_length=4000)

    @model_validator(mode="after")
    def sensible(self):
        if any(v < 0 or v > 10**12 for v in self.views_30d): raise ValueError("Wyświetlenia muszą być nieujemne")
        if self.viral_multiple <= self.success_multiple: raise ValueError("Próg wiralu musi przewyższać próg sukcesu")
        return self


class Development(Model):
    topic_area: str = Field(default="", max_length=2000)
    audience: str = Field(default="", max_length=2000)
    viewer_promise: str = Field(default="", max_length=2000)
    references: str = Field(default="", max_length=2000)
    constraints: str = Field(default="", max_length=3000)
    target_minutes: int = Field(default=15, ge=1, le=360)
    baseline: ChannelBaseline = Field(default_factory=ChannelBaseline)
    ideas: list[FilmIdea] = Field(default_factory=list, max_length=100)
    selected_idea_id: str | None = None
    selected_story_id: str | None = None
    selected_story_hash: str = ""

    @model_validator(mode="after")
    def coherent(self):
        ids=[]
        for idea in self.ideas:
            ids.append(idea.id)
            for story in idea.stories:
                ids.append(story.id)
                for chapter in story.chapters:
                    ids.append(chapter.id); ids.extend(s.id for s in chapter.sections)
        if len(ids)!=len(set(ids)): raise ValueError("Powtórzone identyfikatory planu filmu")
        selected=next((i for i in self.ideas if i.id==self.selected_idea_id),None)
        if self.selected_idea_id and not selected: raise ValueError("Nie ma wybranego pomysłu")
        if self.selected_story_id and (not selected or not any(s.id==self.selected_story_id for s in selected.stories)):
            raise ValueError("Wariant historii musi należeć do wybranego pomysłu")
        return self


def migrate_ideas(data):
    """Keep old topic cards accessible without choosing a new production direction."""
    if "development" in data: return data
    ideas=[]
    for index,item in enumerate(data.get("topics",[])):
        title=str(item.get("title", ""))[:200]
        if not title.strip(): continue
        identity=hashlib.sha256(f"{index}:{title}".encode()).hexdigest()[:16]
        ideas.append({"id":"idea_"+identity,"title":title,"question":str(item.get("central_question", ""))[:1500],"angle":str(item.get("subject", ""))[:3000],"origin":"legacy"})
    title=str(data.get("title", ""))[:200]
    if not ideas and title and title!="Nowy dokument":
        identity=hashlib.sha256(title.encode()).hexdigest()[:16]
        ideas.append({"id":"idea_"+identity,"title":title,"question":str(data.get("story",{}).get("central_question", ""))[:1500],"origin":"legacy"})
    selected=next((i["id"] for i in ideas if i["title"]==title),None)
    return {**data,"development":{"ideas":ideas,"selected_idea_id":selected}}


def structure_hash(story):
    return hashlib.sha256(json.dumps([c.model_dump() for c in story.chapters],sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def direction_hash(story,idea=None):
    values=story.model_dump(include={"title","synopsis","central_question","hook","stakes","payoff","title_pitch"})
    if idea:values["film"]={"title":idea.title,"question":idea.question}
    return hashlib.sha256(json.dumps(values,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def forecast(baseline: ChannelBaseline, story: StoryOption):
    samples=baseline.views_30d
    reference=float(baseline.typical_views_30d) if baseline.typical_views_30d is not None else median(samples) if samples else None
    a=story.assumptions
    views=None if not reference else {"low":round(reference*a.reach_low),"base":round(reference*a.reach_base),"high":round(reference*a.reach_high)}
    def interval(value,delta,spread):
        if value is None:return None
        center=max(0,min(100,value+delta))
        return {"low":round(max(0,center-spread),1),"base":round(center,1),"high":round(min(100,center+spread),1)}
    probabilities=None
    if len(samples)>=10 and reference and reference>0:
        logs=[math.log1p(v) for v in samples]
        distribution=NormalDist(math.log1p(reference*a.reach_base),max(.6,stdev(logs)))
        probabilities={name:round((1-distribution.cdf(math.log1p(reference*multiple)))*100,1) for name,multiple in (("success",baseline.success_multiple),("viral",baseline.viral_multiple))}
    return {"views_30d":views,"ctr":interval(baseline.ctr,a.ctr_delta,2),"retention":interval(baseline.retention,a.retention_delta,10),
            "probabilities":probabilities,"reference_views":reference,"sample_size":len(samples),"editorial_score":round((story.scores.hook+story.scores.audience_fit+story.scores.originality+story.scores.visuals+story.scores.retention)/5),
            "evergreen":story.scores.evergreen,"confidence":"scenario_only","method":"docos-scenario/1",
            "note":"Scenariusze oparte na wpisanych założeniach. Prawdopodobieństwa są symulacją rozkładu logarytmicznego, bez kalibracji skuteczności; nie są prognozą YouTube. CTR nie obejmuje wszystkich źródeł wyświetleń."}
