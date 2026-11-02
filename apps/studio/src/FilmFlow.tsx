import { useEffect, useState } from "react";
import { ArrowDown, ArrowRight, ArrowUp, Check, Copy, Plus, Sparkles, Trash2, AlertTriangle } from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import { makeScene } from "./Generation";
import { blankIdea } from "./developmentTypes";
import type { Project } from "./types";
import type { Page } from "./context";
import { Button, SectionHead } from "./components";
import {
  bibleFields, chosen, flowFrom, isApproved, isReady, newNode, newVariant, stageSignature,
  type FlowData, type FlowNode, type FlowReview, type FlowStage,
} from "./flowTypes";
import "./FilmFlow.css";

export type FlowPage = "bible" | "project-setup" | "idea-flow" | "master-story" | "acts" | "sequences" | "scene-plan" | "script-flow" | "continuity";
const nextPage: Record<FlowPage, string> = {
  bible: "project-setup", "project-setup": "idea-flow", "idea-flow": "master-story", "master-story": "acts", acts: "sequences",
  sequences: "script-flow", "script-flow": "scene-plan",
  "scene-plan": "director", continuity: "export",
};
type AIKind = "ideas" | "master" | "act" | "sequences" | "outlines" | "script" | "review";
type AIRequest = { kind: AIKind; targetId?: string };
const stageForPage: Partial<Record<FlowPage, FlowStage>> = {
  "master-story": "master", acts: "acts", sequences: "sequences", "scene-plan": "outlines",
};
function cleanJson(text: string): unknown {
  return JSON.parse(text.trim().replace(/^\x60\x60\x60(?:json)?\s*/, "").replace(/\s*\x60\x60\x60$/, ""));
}
function optionsFrom(data: unknown, max = 8) {
  if (!Array.isArray(data) || !data.length || data.length > max)
    throw new Error("AI powinno zwrócić tablicę od 1 do " + max + " wariantów.");
  return data.map((x) => {
    if (!x || typeof x !== "object") throw new Error("Niepoprawny wariant.");
    const row = x as Record<string, unknown>;
    const title = String(row.title || "").trim().slice(0, 200);
    const description = String(row.description || row.synopsis || "").trim().slice(0, 6000);
    if (!title || !description) throw new Error("Każdy wariant wymaga tytułu i opisu.");
    return { title, description, seconds: Math.max(5, Math.min(3600, Number(row.seconds) || 120)) };
  });
}
function updateNode(node: FlowNode, variantId: string, patch: { title?: string; description?: string }) {
  node.variants = node.variants.map(v => v.id === variantId ? { ...v, ...patch } : v);
}
function VariantEditor({
  node, label, change, add, remove,
}: {
  node: FlowNode; label: string;
  change: (fn: (node: FlowNode) => void) => void;
  add: () => void; remove?: () => void;
}) {
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  useEffect(() => setDrafts({}), [node.id]);
  const active = chosen(node);
  return (
    <section className="flow-card">
      <div className="flow-card-head">
        <h3>{label}</h3>
        {remove && <button className="flow-quiet" onClick={remove} aria-label={"Usuń " + label}><Trash2 size={15} /></button>}
      </div>
      <div className="flow-tabs" role="group" aria-label={"Warianty " + label}>
        {node.variants.map((variant, index) => (
          <button key={variant.id} className={node.selected === variant.id ? "active" : ""}
            onClick={() => change(n => { n.selected = variant.id; })}>
            Wersja {index + 1}{node.selected === variant.id ? " ✓" : ""}
          </button>
        ))}
        <button onClick={add}><Plus size={13} /> Wariant</button>
      </div>
      {!active ? <p>Dodaj pierwszy wariant.</p> : (
        <div className="flow-fields" key={active.id}>
          <label>Nazwa wariantu
            <input defaultValue={active.title} key={active.id + ":title"}
              onBlur={e => { if (e.target.value !== active.title) change(n => updateNode(n, active.id, { title: e.target.value })); }} />
          </label>
          <label>Co się wydarzy i dlaczego widz będzie oglądał dalej?
            <textarea key={active.id + ":description"} rows={5}
              value={drafts[active.id] ?? active.description}
              onChange={e => setDrafts(v => ({ ...v, [active.id]: e.target.value }))}
              onBlur={() => { const v = drafts[active.id]; if (v !== undefined && v !== active.description) change(n => updateNode(n, active.id, { description: v })); }}
              placeholder="Opisz własnymi słowami, wklej tekst albo wygeneruj kilka propozycji…" />
          </label>
          <div className="flow-inline-actions">
            <button onClick={() => change(n => { const copy = newVariant((active.title || "Wariant") + " (kopia)", drafts[active.id] ?? active.description); n.variants.push(copy); n.selected = copy.id; })}>
              <Copy size={14} /> Kopiuj wariant do edycji
            </button>
            {node.variants.length > 1 && <button onClick={() => change(n => { n.variants = n.variants.filter(x => x.id !== active.id); n.selected = n.variants[0]?.id || null; })}>Usuń ten wariant</button>}
          </div>
        </div>
      )}
    </section>
  );
}
export default function FilmFlow({ page }: { page: FlowPage }) {
  const s = useStudio(), p = s.project!, flow = flowFrom(p);
  const [activeAct, setActiveAct] = useState<string>(""), [activeSection, setActiveSection] = useState<string>("");
  const [ai, setAI] = useState<AIRequest | null>(null);
  const [instruction, setInstruction] = useState(""), [answer, setAnswer] = useState(""), [prompt, setPrompt] = useState("");
  const [responseRevision, setResponseRevision] = useState<number | null>(null), [busy, setBusy] = useState(false);
  const [scriptDraft, setScriptDraft] = useState("");
  const [ownIdea, setOwnIdea] = useState("");
  const act = flow.acts.find(a => a.id === activeAct) || flow.acts[0];
  const sections = flow.sequences.filter(x => x.actId === act?.id);
  const section = flow.sequences.find(x => x.id === activeSection) || sections[0];
  const script = act ? (flow.scripts[act.id] || "") : "";
  useEffect(() => setScriptDraft(script), [p.id, act?.id, script]);
  const saved = (edit: (data: FlowData) => void) => s.run(async () => {
    await s.patch(current => {
      const value = structuredClone(flowFrom(current));
      edit(value);
      return { legacy: { ...current.legacy, production_flow: value } };
    });
  });
  const changeNode = (collection: "acts" | "sequences" | "outlines", id: string, edit: (n: FlowNode) => void) =>
    saved(f => { const n = f[collection].find(x => x.id === id); if (n) edit(n); });
  const title = ({
    bible: "Story Bible", "project-setup": "Twój film", "idea-flow": "Pomysł na odcinek", "master-story": "Master Story", acts: "Akty filmu",
    sequences: "Sekwencje i podrozdziały", "script-flow": "Scenariusz aktu po akcie",
    "scene-plan": "Plan scen", continuity: "Continuity Editor",
  } as Record<FlowPage, string>)[page];
  const subtitle = ({
    bible: "Centralna pamięć filmu. Korzystają z niej agenci AI we wszystkich następnych etapach.",
    "project-setup": "Jeden projekt, jeden film. Na początek tylko tytuł, kanał i krótki opis.",
    "idea-flow": "Napisz własny pomysł, wklej opis albo wygeneruj kilka propozycji i wybierz jedną.",
    "master-story": "Najpierw cała 36-minutowa historia, dopiero potem małe fragmenty.",
    acts: "Przygotuj warianty otwarcia, rozwinięcia i finału. Wybierz po jednej wersji.",
    sequences: "Każdy akt dzielimy na rozdziały i podrozdziały, bez utraty całości fabuły.",
    "script-flow": "AI pisze wybrany akt, znając zakończenie, poprzednie części i Story Bible.",
    "scene-plan": "Krótki zarys każdej sceny; po zatwierdzeniu przejdź do istniejącego edytora scen.",
    continuity: "Reżyser, redaktor, krytyk i trzech widzów oceniają ten sam pełny film.",
  } as Record<FlowPage, string>)[page];
  function openAI(kind: AIKind, targetId?: string) { setAI({ kind, targetId }); setAnswer(""); setPrompt(""); setInstruction(""); setResponseRevision(null); }
  async function request(action: "prompt" | "generate") {
    if (!ai) return;
    setBusy(true);
    try {
      const response = await api<{ response?: string; prompt?: string; base_revision: number }>(
        `/projects/${p.id}/flow/ai/${ai.kind}/${action}`, { target_id: ai.targetId, instruction });
      setResponseRevision(response.base_revision);
      if (response.response) setAnswer(response.response);
      if (response.prompt) setPrompt(response.prompt);
    } finally { setBusy(false); }
  }
  function importAI() {
    if (!ai) return;
    if (responseRevision !== p.revision) { s.notify("Projekt zmienił się. Pobierz aktualną odpowiedź AI.", true); return; }
    try {
      if (ai.kind === "ideas") {
        const rows = optionsFrom(cleanJson(answer), 8);
        s.run(async () => { await s.patch(current => ({ development: { ...current.development,
          ideas: [...current.development.ideas, ...rows.map(row => ({ ...blankIdea(), title: row.title, question: row.description.slice(0, 1500), origin: "ai" as const }))] } })); });
      } else if (ai.kind === "script") {
        const text = answer.trim();
        if (!text) throw new Error("Scenariusz jest pusty.");
        saved(f => { f.scripts[ai.targetId || ""] = text.slice(0, 30000); });
      } else if (ai.kind === "review") {
        const data = cleanJson(answer) as { reviews?: unknown[] };
        if (!data || !Array.isArray(data.reviews) || !data.reviews.length || data.reviews.length > 8) throw new Error("Oczekiwano tablicy reviews.");
        const reviews: FlowReview[] = data.reviews.map(item => {
          const x = item as Record<string, unknown>;
          return { id: crypto.randomUUID(), agent: String(x.agent || "Recenzent").slice(0, 80),
            verdict: String(x.verdict || "").slice(0, 3000),
            issues: Array.isArray(x.issues) ? x.issues.map(String).slice(0, 20) : [],
            suggestions: Array.isArray(x.suggestions) ? x.suggestions.map(String).slice(0, 20) : [] };
        });
        saved(f => { f.reviews = reviews; });
      } else {
        const parsed = optionsFrom(cleanJson(answer), ai.kind === "master" ? 5 : 12);
        saved(f => {
          if (ai.kind === "master") {
            for (const item of parsed) f.master.variants.push(newVariant(item.title, item.description));
            if (!f.master.selected) f.master.selected = f.master.variants[0].id;
          }
          if (ai.kind === "act") {
            const node = f.acts.find(x => x.id === ai.targetId);
            if (node) for (const item of parsed) node.variants.push(newVariant(item.title, item.description));
          }
          if (ai.kind === "sequences") {
            for (const item of parsed) f.sequences.push({ ...newNode(item.title), actId: ai.targetId || "", seconds: item.seconds,
              variants: [newVariant(item.title, item.description)], selected: null });
            for (const node of f.sequences.filter(x => x.actId === ai.targetId && !x.selected)) node.selected = node.variants[0].id;
          }
          if (ai.kind === "outlines") {
            for (const item of parsed) f.outlines.push({ ...newNode(item.title), sectionId: ai.targetId || "", seconds: item.seconds,
              variants: [newVariant(item.title, item.description)], selected: null });
            for (const node of f.outlines.filter(x => x.sectionId === ai.targetId && !x.selected)) node.selected = node.variants[0].id;
          }
        });
      }
      setAI(null);
      s.notify("Propozycje zapisane. Wybierz i zatwierdź odpowiednią wersję.");
    } catch (error) { s.notify(error instanceof Error ? error.message : String(error), true); }
  }
  function approve(stage: FlowStage) {
    if (!isReady(flow, stage)) { s.notify("Uzupełnij wybrane warianty i zatwierdź poprzedni etap.", true); return; }
    saved(f => { f.approved[stage] = stageSignature(f, stage); });
  }
  function move(collection: "acts" | "sequences" | "outlines", id: string, dir: number) {
    saved(f => { const rows = f[collection]; const i = rows.findIndex(x => x.id === id), j = i + dir;
      if (i >= 0 && j >= 0 && j < rows.length) [rows[i], rows[j]] = [rows[j], rows[i]]; });
  }
  function importScript() {
    if (!act || !script.trim()) return;
    const paragraphs = script.trim().split(/\n\s*\n/).map(x => x.trim()).filter(Boolean);
    s.run(async () => {
      await s.patch(current => {
        if (current.scenes.some(x => x.legacy.flow_act_id === act.id))
          throw new Error("Ten akt ma już ujęcia. Edytuj je zamiast tworzyć duplikaty.");
        let cursor = Math.max(0, ...current.scenes.map(x => x.start + x.duration));
        const fps = current.sequence.fps_num / current.sequence.fps_den;
        const shots = paragraphs.map((text, index) => {
          const shot = makeScene(cursor);
          shot.title = `${chosen(act)?.title || "Akt"} · ${index + 1}`;
          shot.narration = text;
          shot.duration = Math.max(60, Math.round((text.split(/\s+/).length / 2.5) * fps));
          shot.legacy = { ...shot.legacy, flow_act_id: act.id };
          cursor += shot.duration;
          return shot;
        });
        return { scenes: [...current.scenes, ...shots] };
      });
      s.notify("Scenariusz tego aktu przeniesiono do ujęć.");
    });
  }
  function applyOutlines() {
    if (!act || !isApproved(flow, "outlines")) {
      s.notify("Najpierw zatwierdź aktualny plan scen.", true);
      return;
    }
    const plan = flow.sequences.filter(x => x.actId === act.id).flatMap(sequence =>
      flow.outlines.filter(x => x.sectionId === sequence.id).map(outline => ({
        outline, sequence, selected: chosen(outline),
      })));
    if (!plan.length || plan.some(x => !x.selected?.description.trim())) {
      s.notify("Wszystkie sceny aktu muszą mieć wybraną wersję.", true);
      return;
    }
    s.run(async () => {
      await s.patch(current => {
        const existing = current.scenes.filter(shot => shot.legacy.flow_act_id === act.id);
        if (existing.length && existing.length !== plan.length)
          throw new Error(`Scenariusz ma ${existing.length} akapitów, plan ma ${plan.length} scen. Dopasuj ich liczbę przed synchronizacją, aby nie stracić narracji.`);
        if (existing.some(shot => shot.locked))
          throw new Error("Odblokuj ujęcia tego aktu przed synchronizacją.");
        const fps = current.sequence.fps_num / current.sequence.fps_den;
        let cursor = Math.max(0, ...current.scenes.map(x => x.start + x.duration));
        if (!existing.length) {
          const shots = plan.map(({ outline, sequence, selected }) => {
            const shot = makeScene(cursor);
            shot.title = selected!.title;
            shot.prompt = selected!.description;
            shot.search_query = selected!.title;
            shot.duration = Math.max(1, Math.round(outline.seconds * fps));
            shot.legacy = { ...shot.legacy, flow_act_id: act.id, flow_section_id: sequence.id, flow_outline_id: outline.id };
            cursor += shot.duration;
            return shot;
          });
          return { scenes: [...current.scenes, ...shots] };
        }
        const ids = existing.map(shot => shot.id);
        const byId = new Map(ids.map((id, i) => [id, plan[i]]));
        return { scenes: current.scenes.map(shot => {
          const item = byId.get(shot.id);
          if (!item) return shot;
          if (shot.legacy.flow_outline_id && shot.legacy.flow_outline_id !== item.outline.id)
            throw new Error("Kolejność planu zmieniła się po synchronizacji ujęć. Zaktualizuj ręcznie istniejące sceny.");
          return {
            ...shot,
            title: shot.title.startsWith((chosen(act)?.title || "Akt") + " ·") ? item.selected!.title : shot.title,
            prompt: shot.prompt || item.selected!.description,
            search_query: shot.search_query || item.selected!.title,
            legacy: { ...shot.legacy, flow_section_id: item.sequence.id, flow_outline_id: item.outline.id },
          };
        }) };
      });
      s.notify("Plan scen przypisany do ujęć. Narracja i materiały zostały zachowane.");
    });
  }
  const stage = stageForPage[page];
  return (
    <div className="page-content flow-page">
      <SectionHead eyebrow="PRODUKCJA KROK PO KROKU" title={title} description={subtitle}>
        <span className="flow-counter">{p.channel} · {p.development.target_minutes} min</span>
      </SectionHead>
      {page !== "bible" && <div className="flow-bible-strip">
        <span>0 · Story Bible</span>
        <strong>{bibleFields.filter(x => flow.bible[x.key].trim()).length}/6 uzupełnionych obszarów</strong>
        <button onClick={() => s.setPage("bible")}>Otwórz pamięć filmu <ArrowRight size={14} /></button>
      </div>}
      {page === "bible" && <>
        <div className="flow-explainer">Pamięć jest zapisywana w tym projekcie. AI otrzymuje ją przy generowaniu nowych wariantów i recenzji. Nie trzeba jej uzupełniać w całości przed rozpoczęciem.</div>
        <label className="flow-toggle"><input type="checkbox" checked={flow.factual}
          onChange={e => saved(f => { f.factual = e.target.checked; })} />
          Film faktograficzny: wymagaj weryfikacji twierdzeń i źródeł</label>
        <div className="flow-grid">{bibleFields.map(entry => <section key={entry.key} className="flow-card">
          <h3>{entry.title}</h3><p className="muted small">{entry.hint}</p>
          <textarea rows={6} key={entry.key + p.revision} defaultValue={flow.bible[entry.key]}
            onBlur={e => { if (e.target.value !== flow.bible[entry.key]) saved(f => { f.bible[entry.key] = e.target.value; }); }} />
        </section>)}</div>
        <div className="flow-actions"><Button primary icon={ArrowRight} onClick={() => s.setPage("project-setup")}>Dalej: projekt</Button></div>
      </>}
      {page === "project-setup" && <>
        <section className="flow-card">
          <h3>Podstawowe informacje</h3>
          <div className="flow-grid">
            <label>Tytuł roboczy filmu
              <input defaultValue={p.title} key={p.id + ":title"}
                onBlur={e => { const value = e.target.value.trim(); if (value && value !== p.title) s.run(() => s.patch({ title: value })); }} />
            </label>
            <label>Kanał
              <input value={p.channel} readOnly title="Kanał wybrano przy tworzeniu filmu" />
            </label>
            <label>Długość docelowa (minuty)
              <input type="number" min={1} max={360} defaultValue={p.development.target_minutes}
                onBlur={e => { const minutes = Math.max(1, Math.min(360, Number(e.target.value) || 15)); if (minutes !== p.development.target_minutes) s.run(() => s.patch(current => ({ development: { ...current.development, target_minutes: minutes } }))); }} />
            </label>
            <label>Odbiorcy filmu
              <textarea rows={2} defaultValue={p.development.audience}
                onBlur={e => { if (e.target.value !== p.development.audience) s.run(() => s.patch(current => ({ development: { ...current.development, audience: e.target.value } }))); }} />
            </label>
          </div>
          <p className="muted small">Projekt ma już swój kanał i styl produkcji. Możesz wrócić do tych ustawień później.</p>
          <div className="flow-actions">
            <Button onClick={() => s.setPage("projects")}>Wszystkie projekty</Button>
            <Button primary icon={ArrowRight} onClick={() => s.setPage("idea-flow")}>Dalej: pomysł</Button>
          </div>
        </section>
      </>}
      {page === "idea-flow" && <>
        <section className="flow-card">
          <h3>O czym opowiesz?</h3>
          <label>Temat / zarys filmu
            <textarea rows={4} defaultValue={p.development.topic_area}
              placeholder="Np. Dlaczego cesarz Qin zjednoczył Chiny?"
              onBlur={e => { if (e.target.value !== p.development.topic_area) s.run(() => s.patch(current => ({ development: { ...current.development, topic_area: e.target.value } }))); }} />
          </label>
          <div className="flow-actions"><Button icon={Sparkles} onClick={() => openAI("ideas")}>Wygeneruj 3–5 pomysłów</Button></div>
        </section>
        <section className="flow-card"><h3>Dodaj własny pomysł</h3>
          <div className="flow-inline-actions">
            <input value={ownIdea} onChange={e => setOwnIdea(e.target.value)} placeholder="Krótki tytuł lub pomysł…" />
            <Button icon={Plus} disabled={!ownIdea.trim()} onClick={() => {
              const value = ownIdea.trim(); setOwnIdea("");
              s.run(() => s.patch(current => ({ development: { ...current.development,
                ideas: [...current.development.ideas, { ...blankIdea(), title: value }] } })));
            }}>Dodaj</Button>
          </div>
        </section>
        <div className="flow-grid">
          {p.development.ideas.map((idea, index) => <section key={idea.id} className="flow-card">
            <small>WARIANT {index + 1}{idea.origin === "ai" ? " · AI" : ""}</small>
            <h3>{idea.title}</h3>
            <p>{idea.question || idea.angle || "Własny pomysł, do rozwinięcia w Master Story."}</p>
            <Button primary={p.development.selected_idea_id === idea.id}
              onClick={() => s.run(() => s.mutate(current => api<Project>(
                `/projects/${current.id}/development/select`,
                { expected_revision: current.revision, idea_id: idea.id })))}>
              {p.development.selected_idea_id === idea.id ? "Wybrany pomysł ✓" : "Wybierz pomysł"}
            </Button>
          </section>)}
        </div>
        <div className="flow-actions">
          <Button onClick={() => s.setPage("idea")}>Zaawansowane porównanie pomysłów</Button>
          <Button primary disabled={!p.development.selected_idea_id} icon={ArrowRight}
            onClick={() => s.setPage("master-story")}>Dalej: Master Story</Button>
        </div>
      </>}
      {page === "master-story" && <>
        {p.development.selected_story_id && <div className="flow-explainer">
          W aplikacji istnieje wybrany wariant historii. Możesz go zaimportować do Master Story bez usuwania źródła.
          <button onClick={() => saved(f => {
            const story = p.development.ideas.flatMap(x => x.stories).find(x => x.id === p.development.selected_story_id);
            if (story) { const v = newVariant(story.title, story.synopsis); f.master.variants.push(v); f.master.selected = v.id; }
          })}>Przejmij wybraną historię</button>
        </div>}
        <VariantEditor node={flow.master} label="Fabuła całego filmu"
          change={fn => saved(f => fn(f.master))}
          add={() => saved(f => { const v = newVariant("Nowa wersja Master Story"); f.master.variants.push(v); f.master.selected = v.id; })} />
        <div className="flow-actions"><Button icon={Sparkles} onClick={() => openAI("master")}>Wygeneruj 3–5 fabuł</Button></div>
      </>}
      {page === "acts" && <>
        <div className="flow-explainer">Dla 36 minut zacznij od około 12 minut na akt. To podział roboczy, nie sztywna reguła dramaturgii.</div>
        {flow.acts.map((node, i) => <div key={node.id}>
          <VariantEditor node={node} label={`Akt ${i + 1}`}
            change={fn => changeNode("acts", node.id, fn)}
            add={() => changeNode("acts", node.id, n => { const v = newVariant("Wariant aktu"); n.variants.push(v); n.selected = v.id; })}
            remove={flow.acts.length > 1 ? () => saved(f => { f.acts = f.acts.filter(x => x.id !== node.id); }) : undefined} />
          <div className="flow-inline-actions">
            <button onClick={() => openAI("act", node.id)}><Sparkles size={14} /> Wygeneruj 3 wersje aktu</button>
            <button disabled={i === 0} onClick={() => move("acts", node.id, -1)}><ArrowUp size={14} /> W górę</button>
            <button disabled={i === flow.acts.length - 1} onClick={() => move("acts", node.id, 1)}><ArrowDown size={14} /> W dół</button>
          </div>
        </div>)}
        <Button icon={Plus} onClick={() => saved(f => { f.acts.push(newNode("Nowy akt")); })}>Dodaj akt</Button>
      </>}
      {page === "sequences" && <>
        <div className="flow-select-bar"><label>Akt <select value={act?.id || ""} onChange={e => setActiveAct(e.target.value)}>
          {flow.acts.map((x, i) => <option value={x.id} key={x.id}>{i + 1}. {chosen(x)?.title || "Akt"}</option>)}
        </select></label><span>{sections.reduce((sum, x) => sum + x.seconds, 0) / 60} min zaplanowane</span></div>
        {sections.map((node, i) => <div key={node.id}>
          <VariantEditor node={node} label={`Sekwencja ${i + 1} · ${node.seconds} s`}
            change={fn => changeNode("sequences", node.id, fn)}
            add={() => changeNode("sequences", node.id, n => { const v = newVariant("Alternatywny przebieg"); n.variants.push(v); n.selected = v.id; })}
            remove={() => saved(f => { f.sequences = f.sequences.filter(x => x.id !== node.id); })} />
          <label className="flow-seconds">Czas (sekundy) <input type="number" min={5} max={3600} defaultValue={node.seconds}
            onBlur={e => saved(f => { const n = f.sequences.find(x => x.id === node.id); if (n) n.seconds = Math.max(5, Math.min(3600, Number(e.target.value) || 60)); })} /></label>
          <div className="flow-inline-actions"><button disabled={i === 0} onClick={() => move("sequences", node.id, -1)}>↑ W górę</button>
            <button disabled={i === sections.length - 1} onClick={() => move("sequences", node.id, 1)}>↓ W dół</button></div>
        </div>)}
        <div className="flow-actions">
          <Button icon={Plus} onClick={() => saved(f => { if (act) f.sequences.push({ ...newNode("Nowa sekwencja"), actId: act.id, seconds: 180 }); })}>Dodaj sekwencję</Button>
          <Button icon={Sparkles} onClick={() => openAI("sequences", act?.id)}>Wygeneruj sekwencje aktu</Button>
        </div>
      </>}
      {page === "script-flow" && <>
        <div className="flow-select-bar"><label>Scenariusz aktu <select value={act?.id || ""} onChange={e => setActiveAct(e.target.value)}>
          {flow.acts.map((x, i) => <option key={x.id} value={x.id}>Akt {i + 1}: {chosen(x)?.title || "Bez tytułu"}</option>)}
        </select></label><span>{script.trim().split(/\s+/).filter(Boolean).length} słów</span></div>
        <section className="flow-card"><h3>Tekst lektora · {chosen(act)?.title}</h3>
          <p className="muted small">Jeden akt na raz, ze znajomością całej historii. Oddziel akapity pustą linią. Każdy akapit po przeniesieniu stanie się ujęciem.</p>
          <textarea rows={18} value={scriptDraft} onChange={e => setScriptDraft(e.target.value)}
            placeholder="Wklej scenariusz, napisz samodzielnie lub skorzystaj z AI…" />
          <div className="flow-actions">
            <Button onClick={() => saved(f => { if (act) f.scripts[act.id] = scriptDraft; })}>Zapisz scenariusz</Button>
            <Button icon={Sparkles} onClick={() => openAI("script", act?.id)}>AI: napisz ten akt</Button>
            <Button disabled={!script.trim() || p.scenes.some(x => x.legacy.flow_act_id === act?.id)} onClick={importScript}>
              Bezpośredni import do ujęć (pomija reżyserię)
            </Button>
          </div>
          {p.scenes.some(x => x.legacy.flow_act_id === act?.id) && <p className="flow-warning">Ten akt ma już ujęcia. Ponowny import nie nadpisze Twojej pracy.</p>}
        </section>
      </>}
      {page === "scene-plan" && <>
        <div className="flow-select-bar"><label>Sekwencja <select value={section?.id || ""} onChange={e => { setActiveSection(e.target.value); setActiveAct(flow.sequences.find(x => x.id === e.target.value)?.actId || ""); }}>
          {flow.sequences.map((x, i) => <option key={x.id} value={x.id}>{i + 1}. {chosen(x)?.title || "Sekwencja"}</option>)}
        </select></label></div>
        {flow.outlines.filter(x => x.sectionId === section?.id).map((node, i) => <div key={node.id}>
          <VariantEditor node={node} label={`Scena ${i + 1}`}
            change={fn => changeNode("outlines", node.id, fn)}
            add={() => changeNode("outlines", node.id, n => { const v = newVariant("Inna wersja sceny"); n.variants.push(v); n.selected = v.id; })}
            remove={() => saved(f => { f.outlines = f.outlines.filter(x => x.id !== node.id); })} />
          <div className="flow-inline-actions"><button disabled={i === 0} onClick={() => move("outlines", node.id, -1)}>↑</button>
            <button onClick={() => move("outlines", node.id, 1)}>↓</button></div>
        </div>)}
        <div className="flow-actions">
          <Button icon={Plus} disabled={!section} onClick={() => saved(f => { if (section) f.outlines.push({ ...newNode("Nowa scena"), sectionId: section.id, seconds: 60 }); })}>Dodaj scenę</Button>
          <Button icon={Sparkles} disabled={!section} onClick={() => openAI("outlines", section?.id)}>AI: wersje scen</Button>
          <Button primary icon={ArrowRight} onClick={() => s.setPage("director")}>Dalej: reżyseria i mapa napięcia</Button>
          <Button icon={Check} disabled={!isApproved(flow, "outlines")} onClick={applyOutlines}>Bezpośrednio do ujęć (pomija reżyserię)</Button>
          <Button onClick={() => s.setPage("scenes")}>Otwórz istniejący edytor scen</Button>
        </div>
      </>}
      {page === "continuity" && <>
        <div className="flow-explainer">Ocena działa na całym projekcie: Master Story, planie, tekstach wszystkich aktów, ujęciach i faktach. Agenci proponują poprawki, ale nie nadpisują automatycznie Twoich scen.</div>
        <div className="flow-actions"><Button primary icon={Sparkles} onClick={() => openAI("review")}>Uruchom zespół recenzentów</Button></div>
        {flow.reviews.length ? <div className="flow-grid">{flow.reviews.map(r => <section className="flow-card" key={r.id}>
          <h3>{r.agent}</h3><p>{r.verdict}</p>
          <strong>Problemy</strong><ul>{r.issues.map((v, i) => <li key={i}>{v}</li>)}</ul>
          <strong>Proponowane poprawki</strong><ul>{r.suggestions.map((v, i) => <li key={i}>{v}</li>)}</ul>
        </section>)}</div> : <div className="flow-empty">Brak zapisanej recenzji. Możesz ją uruchomić po przygotowaniu filmu.</div>}
      </>}
      {stage && <div className="flow-footer">
        <div>{isApproved(flow, stage) ? <span className="flow-ok"><Check size={16} /> Etap zatwierdzony</span> :
          flow.approved[stage] ? <span className="flow-warning"><AlertTriangle size={16} /> Zmiany wymagają ponownego zatwierdzenia</span> :
            <span className="muted">Etap jest roboczy. Możesz wrócić do niego później.</span>}</div>
        <div className="flow-actions">
          <Button disabled={!isReady(flow, stage) || isApproved(flow, stage)} icon={Check} onClick={() => approve(stage)}>Zatwierdź etap</Button>
          <Button primary icon={ArrowRight} onClick={() => s.setPage(nextPage[page] as Page)}>Dalej</Button>
        </div>
      </div>}
      {(page === "script-flow" || page === "continuity") && <div className="flow-footer"><Button primary icon={ArrowRight} onClick={() => s.setPage(nextPage[page] as Page)}>Dalej</Button></div>}
      {ai && <div className="flow-modal-backdrop" role="presentation" onMouseDown={e => { if (e.target === e.currentTarget) setAI(null); }}>
        <section className="flow-modal" role="dialog" aria-modal="true" aria-label="Generowanie AI">
          <div className="flow-card-head"><h2>AI · {ai.kind}</h2><button onClick={() => setAI(null)} aria-label="Zamknij">×</button></div>
          <p className="muted small">AI dostaje zatwierdzoną fabułę, Story Bible, strukturę oraz cel następnego aktu. Wybór propozycji należy do Ciebie.</p>
          <label>Własne wskazówki <textarea rows={3} value={instruction} onChange={e => setInstruction(e.target.value)} /></label>
          <div className="flow-actions"><Button icon={Sparkles} busy={busy} onClick={() => s.run(() => request("generate"))}>Generuj</Button>
            <Button icon={Copy} busy={busy} onClick={() => s.run(() => request("prompt"))}>Przygotuj prompt</Button></div>
          {prompt && <label>Prompt do zewnętrznego AI<textarea readOnly rows={6} value={prompt} /></label>}
          <label>Odpowiedź AI (możesz także wkleić odpowiedź innego modelu)
            <textarea rows={12} value={answer} onChange={e => setAnswer(e.target.value)} /></label>
          {responseRevision !== null && responseRevision !== p.revision && <p className="flow-warning">Projekt się zmienił. Wygeneruj ponownie.</p>}
          <div className="flow-actions"><Button primary disabled={!answer.trim() || responseRevision !== p.revision} onClick={importAI}>Dodaj propozycje do projektu</Button>
            <Button onClick={() => setAI(null)}>Anuluj</Button></div>
        </section>
      </div>}
    </div>
  );
}
