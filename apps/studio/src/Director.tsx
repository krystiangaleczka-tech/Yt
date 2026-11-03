import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDown, ArrowRight, ArrowUp, BookOpen, Check, Copy, Plus, RefreshCw, Sparkles, Trash2, Undo2, X,
} from "lucide-react";
import { useStudio } from "./context";
import { Button, SectionHead } from "./components";
import { api } from "./api";
import { makeScene } from "./Generation";
import { chosen, flowFrom, isApproved, isReady, orderedOutlines, sceneSourceSignature, stageSignature } from "./flowTypes";
import type { FlowData, FlowOutline } from "./flowTypes";
import { saveFlow } from "./flowSave";
import {
  buildAutoPlan, directorLimits, directorPatterns, parseDirectorAI, patternById, shotKinds, clampTension, transitions,
} from "./directorTypes";
import type { DirectorBeat, DirectorShot, DirectorMode, DirectorPattern, SceneDirection } from "./directorTypes";
import type { Project } from "./types";
import "./Director.css";

const beatColors = ["#6185cc", "#b78d55", "#b56565", "#5f9e86", "#8a6fc0", "#c07a3f"];
function key() { return crypto.randomUUID(); }
function seconds(n: number) { return (Number(n) || 0).toFixed(1).replace(".", ",") + " s"; }
function beatColor(plan: SceneDirection, beatId: string) {
  const index = plan.beats.findIndex(b => b.id === beatId);
  return beatColors[(index < 0 ? 0 : index) % beatColors.length];
}
type PlanStatus = "missing" | "stale" | "ready";
function planStatus(flow: FlowData, outline: FlowOutline): PlanStatus {
  const plan = flow.director.plans[outline.id];
  if (!plan) return "missing";
  return plan.sourceSignature === sceneSourceSignature(flow, outline.id) ? "ready" : "stale";
}
const statusMark: Record<PlanStatus, string> = { missing: "○", stale: "⚠", ready: "✓" };

function TensionChart({ beats }: { beats: DirectorBeat[] }) {
  const values = beats.length ? [beats[0].tensionBefore, ...beats.map(b => b.tensionAfter)] : [0, 0];
  const x = (i: number) => 30 + i * 540 / (values.length - 1);
  const y = (v: number) => 140 - v * 12;
  const points = values.map((v, i) => x(i) + "," + y(v)).join(" ");
  const label = (i: number) => i === 0 ? "Start" : (values.length > 7 ? "B" : "Beat ") + String(i).padStart(2, "0");
  return <div className="director-chart" role="img" aria-label={"Mapa napięcia: " + values.join(", ") + " w skali 0–10"}>
    <svg viewBox="0 0 600 174" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
      {[0, 5, 10].map(v => <g key={v}><line x1="30" x2="570" y1={y(v)} y2={y(v)} stroke="currentColor" opacity=".12"/><text x="8" y={y(v) + 4} fill="currentColor" fontSize="11">{v}</text></g>)}
      <polygon points={`${x(0)},${y(0)} ${points} ${x(values.length - 1)},${y(0)}`} fill="#80a9f8" opacity=".12" />
      <polyline fill="none" stroke="#80a9f8" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" points={points} />
      {values.map((v, i) => <g key={i}><circle cx={x(i)} cy={y(v)} r="5" fill="#80a9f8"/>
        <text x={x(i)} y={y(v) - 10} fontSize="10" textAnchor="middle" fill="currentColor">{v}</text>
        <text x={x(i)} y="164" fontSize="10" textAnchor="middle" fill="currentColor">{label(i)}</text></g>)}
    </svg>
    <span className="director-muted">Skala 0–10 jest oceną dramaturgiczną, nie obiektywnym pomiarem emocji.</span>
  </div>;
}

function MontageBars({ plan, onChoose, active }: {
  plan: SceneDirection; onChoose: (id: string) => void; active: string | null;
}) {
  const max = Math.max(1, ...plan.shots.map(s => s.duration));
  let cursor = 0;
  return <>
    <div className="director-legend">{plan.beats.map((beat, i) =>
      <span key={beat.id}><i style={{ background: beatColor(plan, beat.id) }} />Beat {String(i + 1).padStart(2, "0")} · {beat.title}</span>)}</div>
    <div className="director-bars" aria-label="Plan montażowy">
      {plan.shots.map((shot, i) => {
        const start = cursor; cursor += shot.duration;
        return <button type="button" className={"director-bar-row " + (active === shot.id ? "active" : "")}
          key={shot.id} onClick={() => onChoose(shot.id)} title={"Edytuj ujęcie " + (i + 1)}>
          <span className="director-time">{seconds(start)}–{seconds(cursor)}</span>
          <span className="director-bar" style={{ width: Math.max(8, shot.duration / max * 100) + "%", background: beatColor(plan, shot.beatId) }} />
          <span className="director-bar-name">{String(i + 1).padStart(2, "0")}. {shot.title} <small>{seconds(shot.duration)} · {shot.transition}</small></span>
        </button>;
      })}
    </div>
  </>;
}

/** Local value while dragging; saves once the slider settles instead of on every step. */
function TensionSlider({ label, value, onCommit }: { label: string; value: number; onCommit: (n: number) => void }) {
  const [draft, setDraft] = useState(value);
  const pending = useRef<(() => void) | null>(null), timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => setDraft(value), [value]);
  // Flush a pending change when the beat or scene is switched before the delay ends.
  useEffect(() => () => { clearTimeout(timer.current); pending.current?.(); }, []);
  function change(next: number) {
    setDraft(next);
    clearTimeout(timer.current);
    pending.current = next === value ? null : () => { pending.current = null; onCommit(clampTension(next)); };
    timer.current = setTimeout(() => pending.current?.(), 450);
  }
  return <label>{label}: {draft}
    <input type="range" min="0" max="10" value={draft} onChange={e => change(Number(e.target.value))} />
  </label>;
}

function PatternEditor({ pattern, onSave, onDelete }: {
  pattern: DirectorPattern; onSave: (p: DirectorPattern) => void; onDelete: () => void;
}) {
  const s = useStudio();
  const [draft, setDraft] = useState(pattern);
  const [tension, setTension] = useState(pattern.tension.join(", "));
  const source = JSON.stringify(pattern);
  useEffect(() => { setDraft(pattern); setTension(pattern.tension.join(", ")); }, [source]);
  function save() {
    const values = tension.split(/[,\s;]+/).filter(Boolean).map(Number);
    if (values.length < 2 || values.length > 16 || values.some(v => !Number.isFinite(v) || v < 0 || v > 10)) {
      s.notify("Krzywa napięcia: od 2 do 16 liczb 0–10, np. 2, 4, 7, 9.", true); return;
    }
    if (!draft.name.trim() || !draft.shots.length) { s.notify("Wzorzec wymaga nazwy i co najmniej jednego ujęcia.", true); return; }
    onSave({ ...draft, name: draft.name.trim(), tension: values.map(clampTension) });
  }
  return <div className="director-pattern-editor">
    <label>Nazwa<input value={draft.name} maxLength={120} onChange={e => setDraft({ ...draft, name: e.target.value })} /></label>
    <label>Cel<textarea rows={2} value={draft.purpose} maxLength={1000} onChange={e => setDraft({ ...draft, purpose: e.target.value })} /></label>
    <label>Kiedy użyć<input value={draft.cue} maxLength={1000} onChange={e => setDraft({ ...draft, cue: e.target.value })} /></label>
    <label>Rytm montażu<input value={draft.rhythm} maxLength={1000} onChange={e => setDraft({ ...draft, rhythm: e.target.value })} /></label>
    <label>Krzywa napięcia (0–10)<input value={tension} onChange={e => setTension(e.target.value)} placeholder="2, 4, 7, 9" /></label>
    <div>
      <small>Sekwencja ujęć</small>
      <div className="director-chipline">{draft.shots.map((id, i) => <span key={i}>{shotKinds.find(x => x.id === id)?.name || id}
        <button type="button" aria-label="Usuń ujęcie z wzorca" onClick={() => setDraft({ ...draft, shots: draft.shots.filter((_, j) => j !== i) })}><X size={10} /></button></span>)}</div>
      <select value="" aria-label="Dodaj ujęcie do wzorca" onChange={e => { if (e.target.value && draft.shots.length < 40) setDraft({ ...draft, shots: [...draft.shots, e.target.value] }); }}>
        <option value="">+ Dodaj ujęcie…</option>
        {shotKinds.map(k => <option key={k.id} value={k.id}>{k.name}</option>)}
      </select>
    </div>
    <div className="flow-actions">
      <Button icon={Check} onClick={save}>Zapisz wzorzec</Button>
      <Button icon={Trash2} onClick={onDelete}>Usuń własny</Button>
    </div>
  </div>;
}

export default function Director() {
  const s = useStudio();
  const p = s.project!;
  const flow = flowFrom(p);
  const outlines = orderedOutlines(flow);
  const [sceneId, setSceneId] = useState("");
  const [view, setView] = useState<"plan" | "library">("plan");
  const [selectedShot, setSelectedShot] = useState<string | null>(null);
  const [patternId, setPatternId] = useState("");
  const [guidance, setGuidance] = useState("");
  const [filter, setFilter] = useState("");
  const [newPattern, setNewPattern] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const outline = outlines.find(x => x.id === sceneId) || outlines[0];
  const plan = outline ? flow.director.plans[outline.id] : undefined;
  const stale = Boolean(outline && plan && planStatus(flow, outline) === "stale");
  const options = useMemo(() => [...directorPatterns, ...flow.director.customPatterns], [flow.director.customPatterns]);
  useEffect(() => { setSelectedShot(null); setPatternId(""); setGuidance(""); }, [outline?.id]);
  const selected = plan?.shots.find(x => x.id === selectedShot);
  const totalDuration = plan?.shots.reduce((sum, shot) => sum + shot.duration, 0) || 0;
  const selectedPattern = patternById(patternId || plan?.patternId || "anticipation", flow.director.customPatterns);
  const statuses = outlines.map(row => planStatus(flow, row));
  const counts = { ready: statuses.filter(x => x === "ready").length, stale: statuses.filter(x => x === "stale").length,
    missing: statuses.filter(x => x === "missing").length };
  const aiAvailable = Boolean(s.health?.ai);

  /** Every change goes through the validated flow endpoint; the notice appears only after the server accepted it. */
  function commit(edit: (flow: FlowData, project: Project) => void, message?: string) {
    s.run(async () => {
      await saveFlow(s.mutate, edit);
      if (message) s.notify(message);
    });
  }
  function savePlan(edit: (plan: SceneDirection) => void, message?: string) {
    if (!outline) return;
    const id = outline.id;
    commit(f => {
      const target = f.director.plans[id];
      if (!target) throw new Error("Plan tej sceny nie istnieje. Najpierw go przygotuj.");
      edit(target);
    }, message);
  }
  function prepare(all: boolean) {
    if (!outline) { s.notify("Najpierw dodaj sceny w planie scen.", true); return; }
    if (all) {
      if (!counts.missing) {
        s.notify(counts.stale ? "Wszystkie sceny mają plany. Nieaktualne (⚠) przejrzyj i przelicz pojedynczo albo oznacz jako aktualne." :
          "Wszystkie sceny mają już plany reżyserii.");
        return;
      }
      commit(f => {
        // Bulk planning never overwrites any existing plan, even a stale one with manual edits.
        for (const target of f.outlines)
          if (!f.director.plans[target.id]) f.director.plans[target.id] = buildAutoPlan(f, target, f.director.mode);
      }, `Przygotowano plany dla ${counts.missing} ${counts.missing === 1 ? "sceny" : "scen"}. Sprawdź wykresy i paski montażowe.`);
      return;
    }
    if (plan && !confirm("Zastąpić obecny plan tej sceny nowym? Ręczne zmiany beatów i ujęć tej sceny zostaną zastąpione.\nMożesz to cofnąć przyciskiem „Cofnij ostatnią zmianę”.")) return;
    const id = outline.id, preferred = patternId, notes = guidance;
    commit(f => {
      const target = f.outlines.find(row => row.id === id);
      if (!target) throw new Error("Scena została usunięta z planu scen.");
      const previous = f.director.plans[id];
      f.director.plans[id] = buildAutoPlan(f, target, f.director.mode, preferred, notes);
      if (previous && !notes) f.director.plans[id].notes = previous.notes;
    }, plan ? "Zapisano nowy plan sceny." : "Plan sceny gotowy.");
  }
  function keepStalePlan() {
    if (!outline) return;
    const id = outline.id;
    commit(f => {
      const target = f.director.plans[id];
      if (target) target.sourceSignature = sceneSourceSignature(f, id);
    }, "Plan zachowany i oznaczony jako zgodny z aktualnym opisem sceny.");
  }
  function keepAllStalePlans() {
    if (!confirm(`Zachować ${counts.stale} nieaktualnych planów bez zmian i oznaczyć je jako zgodne z obecną historią?\nUżyj tego, gdy zmiana (np. w Story Bible) nie wpływa na rytm scen.`)) return;
    commit(f => {
      for (const row of f.outlines) {
        const target = f.director.plans[row.id];
        if (target) target.sourceSignature = sceneSourceSignature(f, row.id);
      }
    }, "Wszystkie plany oznaczone jako aktualne. Przejrzyj je i zatwierdź reżyserię.");
  }
  async function generateAI() {
    if (!outline) return;
    if (plan && !confirm("AI przygotuje nowy plan i zastąpi obecny plan tej sceny. Kontynuować?\nMożesz to cofnąć przyciskiem „Cofnij ostatnią zmianę”.")) return;
    const targetId = outline.id, signature = sceneSourceSignature(flow, targetId);
    setBusy(true);
    try {
      const response = await api<{ response: string; base_revision: number }>(
        "/projects/" + p.id + "/flow/ai/direction/generate",
        { target_id: targetId, instruction: guidance + "\nPreferowany wzorzec: " + (patternId || selectedPattern.id) });
      // Validate first: a malformed answer never touches the project.
      const proposal = parseDirectorAI(response.response, flow, outline, flow.director.mode);
      await saveFlow(s.mutate, f => {
        if (!f.outlines.some(x => x.id === targetId)) throw new Error("Scena została usunięta podczas generowania.");
        // Unrelated edits elsewhere are fine; only a changed scene source invalidates the answer.
        if (sceneSourceSignature(f, targetId) !== signature)
          throw new Error("Opis sceny zmienił się podczas generowania. Wygeneruj ponownie.");
        f.director.plans[targetId] = { ...proposal, mode: f.director.mode, sourceSignature: signature };
      });
      s.notify("Plan AI zapisany. Sprawdź beaty i ujęcia przed zatwierdzeniem.");
    } catch (error) { s.notify(error instanceof Error ? error.message : String(error), true); }
    finally { setBusy(false); }
  }
  function applyShotList() {
    if (!isApproved(flow, "direction")) { s.notify("Najpierw zatwierdź aktualny plan reżyserii.", true); return; }
    s.run(async () => {
      let added = 0;
      let skipped: string[] = [];
      await s.patch(current => {
        const f = flowFrom(current);
        if (!isApproved(f, "direction")) throw new Error("Reżyseria wymaga ponownego zatwierdzenia.");
        const withShots = new Set(current.scenes.map(shot => String(shot.legacy.flow_outline_id || "")));
        // Paragraphs imported directly from the script cover the whole act; never stack director shots on top.
        const scriptActs = new Set(current.scenes.filter(shot => shot.legacy.flow_act_id && !shot.legacy.flow_outline_id)
          .map(shot => String(shot.legacy.flow_act_id)));
        const actOf = (row: FlowOutline) => f.sequences.find(item => item.id === row.sectionId)?.actId || "";
        const ordered = orderedOutlines(f);
        const prepared = ordered.filter(row => !withShots.has(row.id) && !scriptActs.has(actOf(row)));
        skipped = ordered.filter(row => !prepared.includes(row)).map(row => chosen(row)?.title || "Scena");
        if (!prepared.length) throw new Error("Wszystkie sceny mają już ujęcia. Nie duplikuję ani nie nadpisuję Twojego montażu.");
        const fps = current.sequence.fps_num / current.sequence.fps_den;
        let cursor = Math.max(0, ...current.scenes.map(shot => shot.start + shot.duration));
        const produced = prepared.flatMap(row => {
          const direction = f.director.plans[row.id];
          return direction.shots.map((item, index) => {
            const shot = makeScene(cursor);
            const frameDuration = Math.max(1, Math.round(item.duration * fps));
            const beat = direction.beats.find(b => b.id === item.beatId);
            shot.title = (chosen(row)?.title || "Scena") + " · " + String(index + 1).padStart(2, "0") + " · " + item.title;
            shot.prompt = item.description;
            shot.search_query = item.title;
            shot.director_notes = ["Typ: " + (shotKinds.find(k => k.id === item.typeId)?.name || item.typeId),
              "Przejście: " + item.transition, item.sound && "Dźwięk: " + item.sound,
              beat && "Beat: " + beat.title + " (napięcie " + beat.tensionBefore + "→" + beat.tensionAfter + ")",
              beat?.goal && "Cel: " + beat.goal].filter(Boolean).join(". ").slice(0, 3000);
            shot.duration = frameDuration;
            shot.legacy = { ...shot.legacy, flow_act_id: actOf(row), flow_section_id: row.sectionId,
              flow_outline_id: row.id, flow_director_shot_id: item.id, flow_director_beat_id: item.beatId,
              flow_director_kind: item.typeId };
            cursor += frameDuration;
            return shot;
          });
        });
        added = produced.length;
        return { scenes: [...current.scenes, ...produced] };
      });
      s.notify(`Dodano ${added} ujęć do scen.` + (skipped.length ?
        ` Pominięto ${skipped.length} ${skipped.length === 1 ? "scenę" : "scen"} z istniejącymi ujęciami: ${skipped.slice(0, 4).join(", ")}${skipped.length > 4 ? "…" : ""}.` : ""));
      s.setPage("scenes");
    });
  }
  function undo() {
    s.run(async () => {
      await s.mutate(current => api<Project>(`/projects/${current.id}/history/undo`, { expected_revision: current.revision }));
      s.notify("Cofnięto ostatnią zmianę projektu.");
    });
  }
  function updateBeat(id: string, patch: Partial<DirectorBeat>) {
    savePlan(x => { x.beats = x.beats.map(b => b.id === id ? { ...b, ...patch } : b); });
  }
  function updateShot(id: string, patch: Partial<DirectorShot>) {
    savePlan(x => { x.shots = x.shots.map(b => b.id === id ? { ...b, ...patch } : b); });
  }
  function moveShot(id: string, direction: number) {
    savePlan(x => {
      const index = x.shots.findIndex(z => z.id === id), next = index + direction;
      if (index >= 0 && next >= 0 && next < x.shots.length) [x.shots[index], x.shots[next]] = [x.shots[next], x.shots[index]];
    });
  }
  function addPattern() {
    if (!newPattern.trim()) return;
    const base = patternById(patternId || "anticipation", flow.director.customPatterns);
    const id = "custom-" + key();
    commit(f => { f.director.customPatterns.push({
      ...base, id, name: newPattern.trim().slice(0, 100),
      purpose: "Własny wzorzec (na bazie: " + base.name + ").", cue: base.cue, rhythm: base.rhythm,
    }); }, "Wzorzec dodany do biblioteki projektu. Możesz go teraz edytować.");
    setNewPattern("");
    setEditing(id);
  }
  const text = (value: string, limit: number, save: (v: string) => void) => ({
    defaultValue: value, maxLength: limit,
    onBlur: (e: { target: { value: string } }) => { if (e.target.value !== value) save(e.target.value); },
  });
  return <div className="page-content flow-page director-page">
    <SectionHead eyebrow="ETAP REŻYSERII" title="Beaty, napięcie i plan montażowy"
      description="Na podstawie zatwierdzonych scen przygotuj rytm, ujęcia i wykres napięcia. Dopiero potem wygeneruj kadry.">
      <span className="flow-counter">{outlines.length} scen · {counts.ready} gotowych{counts.stale ? ` · ${counts.stale} nieaktualnych` : ""}</span>
    </SectionHead>
    <div className="director-topbar">
      <div className="flow-tabs" role="group" aria-label="Zakładki reżyserii">
        <button className={view === "plan" ? "active" : ""} onClick={() => setView("plan")}>Planowanie scen</button>
        <button className={view === "library" ? "active" : ""} onClick={() => setView("library")}><BookOpen size={14}/> Biblioteka wzorców i ujęć</button>
      </div>
      <div className="director-topbar-actions">
        <label>Tryb pracy
          <select value={flow.director.mode} onChange={e => { const mode = e.target.value as DirectorMode; commit(f => { f.director.mode = mode; }); }}>
            <option value="auto">Automatyczny</option><option value="guided">Z wytycznymi</option><option value="manual">Ręczny</option>
          </select>
        </label>
        <Button icon={Undo2} disabled={s.saving} onClick={undo}>Cofnij ostatnią zmianę</Button>
      </div>
    </div>
    {view === "library" ? <>
      <section className="flow-card director-library-controls">
        <h3>Biblioteka reżyserii i montażu</h3>
        <p>Wzorce pomagają budować emocje, ale nie są sztywnymi regułami. Wbudowane wzorce i rodzaje ujęć są dostępne w każdym projekcie; własne zapisują się w aktualnym filmie.</p>
        <input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Szukaj: suspense, POV, telefon, pościg..." aria-label="Szukaj w bibliotece"/>
        <div className="director-library-create"><input value={newPattern} maxLength={100} onChange={e => setNewPattern(e.target.value)} placeholder="Nazwa własnego wzorca" aria-label="Nazwa nowego wzorca" />
          <Button icon={Plus} disabled={!newPattern.trim()} onClick={addPattern}>Dodaj wzorzec</Button></div>
        <p className="director-muted">Nowy wzorzec startuje jako kopia wzorca wybranego w planowaniu sceny (domyślnie Anticipation / Payoff).</p>
      </section>
      <div className="director-library-grid">
        {options.filter(item => (item.name + item.purpose + item.cue + item.shots.join(" ")).toLowerCase().includes(filter.toLowerCase())).map(item =>
          <section className="flow-card" key={item.id}>
            {editing === item.id && item.id.startsWith("custom-") ?
              <PatternEditor pattern={item}
                onSave={next => { commit(f => { f.director.customPatterns = f.director.customPatterns.map(x => x.id === item.id ? next : x); }, "Wzorzec zapisany."); setEditing(null); }}
                onDelete={() => { if (confirm("Usunąć własny wzorzec „" + item.name + "”? Istniejące plany scen pozostaną bez zmian."))
                  commit(f => { f.director.customPatterns = f.director.customPatterns.filter(x => x.id !== item.id); }, "Wzorzec usunięty."); }} /> : <>
              <h3>{item.name}{item.id.startsWith("custom-") && <small className="director-badge">własny</small>}</h3>
              <p>{item.purpose}</p><p className="director-muted">{item.cue}</p>
              <small>Rytm: {item.rhythm}</small>
              <div className="director-chipline">{item.shots.map((id, i) => <span key={i}>{shotKinds.find(x => x.id === id)?.name || id}</span>)}</div>
              <small className="director-muted">Napięcie: {item.tension.join(" → ")}</small>
              <div className="flow-actions"><Button onClick={() => { setView("plan"); setPatternId(item.id); }}>Użyj w scenie</Button>
                {item.id.startsWith("custom-") && <Button onClick={() => setEditing(item.id)}>Edytuj</Button>}</div>
            </>}
          </section>)}
      </div>
      <h3>Rodzaje ujęć</h3>
      <div className="director-library-grid">{shotKinds.filter(item => (item.name + item.usage).toLowerCase().includes(filter.toLowerCase())).map(item =>
        <section key={item.id} className="flow-card"><h3>{item.name}</h3><p className="director-muted">{item.usage}</p></section>)}</div>
    </> : <>
      <div className="director-toolbar flow-card">
        <label>Scena do reżyserowania
          <select value={outline?.id || ""} onChange={e => setSceneId(e.target.value)}>
            {outlines.map((item, i) => <option value={item.id} key={item.id}>{statusMark[statuses[i]]} {i + 1}. {chosen(item)?.title || "Scena bez tytułu"} · {item.seconds} s</option>)}
          </select>
        </label>
        <div className="director-status">
          {isApproved(flow, "outlines") ? <span className="flow-ok"><Check size={14}/> Plan scen zatwierdzony</span> :
            <span className="flow-warning">Najpierw zatwierdź Plan scen</span>}
          <span className="director-muted">✓ gotowe · ⚠ nieaktualne · ○ bez planu</span>
          {counts.stale > 1 && <Button icon={Check} onClick={keepAllStalePlans}>Zachowaj wszystkie nieaktualne plany ({counts.stale})</Button>}
        </div>
        {stale && <div className="director-stale">
          <span className="flow-warning">Scena, scenariusz aktu, Story Bible lub Master Story zmieniły się od przygotowania tego planu.</span>
          <div className="flow-actions">
            <Button icon={Check} onClick={keepStalePlan}>Plan nadal pasuje — oznacz jako aktualny</Button>
            <Button icon={RefreshCw} onClick={() => prepare(false)}>Przelicz plan od nowa</Button>
          </div>
        </div>}
        <div className="flow-actions">
          <Button icon={Sparkles} disabled={!outline} onClick={() => prepare(false)}>{plan ? "Przelicz bieżącą scenę" : "Zaplanuj scenę"}</Button>
          <Button icon={Copy} disabled={!outlines.length} onClick={() => prepare(true)}>Zaplanuj brakujące sceny{counts.missing ? ` (${counts.missing})` : ""}</Button>
        </div>
        <div className="director-guidance">
          <label>Wzorzec reżyserski
            <select value={patternId || plan?.patternId || ""} onChange={e => setPatternId(e.target.value)}>
              <option value="">Dobierz automatycznie</option>
              {options.map(item => <option value={item.id} key={item.id}>{item.name}</option>)}
            </select>
          </label>
          <label>Wytyczne (opcjonalnie)
            <textarea rows={2} maxLength={directorLimits.notes} placeholder="Np. od telefonu do okna; coraz krótsze cięcia, a na końcu nieruchome ujęcie..." value={guidance} onChange={e => setGuidance(e.target.value)} />
          </label>
        </div>
        <div className="flow-actions"><Button icon={Sparkles} busy={busy} disabled={!outline || busy || !aiAvailable} onClick={() => s.run(generateAI)}>Wygeneruj bardziej filmowo przez AI</Button>
          <span className="director-muted">{aiAvailable ? "Automatyczny plan działa także bez modelu AI." :
            "Model AI nie jest podłączony (Ustawienia → Połączenia). Plan automatyczny działa bez niego."}</span></div>
      </div>
      {!outline ? <div className="flow-empty"><p>Brak scen. Wróć do Planu scen, dodaj sceny i wróć tutaj.</p>
        <Button icon={ArrowRight} onClick={() => s.setPage("scene-plan")}>Otwórz plan scen</Button></div> :
      !plan ? <div className="flow-empty">Wybierz „Zaplanuj scenę” lub „Zaplanuj brakujące sceny”. System wyznaczy beaty, wykres napięcia i cięcia.</div> :
      <div className="director-grid">
        <section className="flow-card">
          <div className="flow-card-head"><h3>Mapa napięcia · {chosen(outline)?.title}</h3><span className="director-muted">{plan.beats.length} beatów</span></div>
          <p className="director-muted">Wzorzec: {patternById(plan.patternId, flow.director.customPatterns).name}. {patternById(plan.patternId, flow.director.customPatterns).purpose} {patternById(plan.patternId, flow.director.customPatterns).rhythm}</p>
          <TensionChart beats={plan.beats} />
          <div className="director-beats">
            {plan.beats.map((beat, i) => <details key={beat.id} open={i === 0 ? true : undefined}>
              <summary><strong><i className="director-dot" style={{ background: beatColor(plan, beat.id) }} />Beat {String(i + 1).padStart(2, "0")} · {beat.title}</strong><span>{beat.tensionBefore} → {beat.tensionAfter}/10</span></summary>
              <label>Nazwa beatu<input key={beat.id + ":title:" + beat.title} {...text(beat.title, directorLimits.title, v => updateBeat(beat.id, { title: v }))} /></label>
              <label>Cel dramaturgiczny<textarea rows={2} key={beat.id + ":goal:" + beat.goal} {...text(beat.goal, directorLimits.goal, v => updateBeat(beat.id, { goal: v }))} /></label>
              <div className="director-tension-inputs">
                <TensionSlider label="Przed" value={beat.tensionBefore} onCommit={n => updateBeat(beat.id, { tensionBefore: n })} />
                <TensionSlider label="Po" value={beat.tensionAfter} onCommit={n => updateBeat(beat.id, { tensionAfter: n })} />
              </div>
              <label>Co wie widz<input key={beat.id + ":view:" + beat.viewerKnows} {...text(beat.viewerKnows, directorLimits.knows, v => updateBeat(beat.id, { viewerKnows: v }))} /></label>
              <label>Co wie bohater<input key={beat.id + ":character:" + beat.characterKnows} {...text(beat.characterKnows, directorLimits.knows, v => updateBeat(beat.id, { characterKnows: v }))} /></label>
              <label>Sygnał dźwiękowy<input key={beat.id + ":sound:" + beat.soundCue} {...text(beat.soundCue, directorLimits.sound, v => updateBeat(beat.id, { soundCue: v }))} /></label>
            </details>)}
          </div>
        </section>
        <section className="flow-card">
          <div className="flow-card-head"><h3>Plan montażowy</h3>
            <span className={"director-muted" + (Math.abs(totalDuration - outline.seconds) > Math.max(2, outline.seconds * .15) ? " director-warn" : "")}>{seconds(totalDuration)} / plan {seconds(outline.seconds)}</span></div>
          <p className="director-muted">Wybierz pasek, żeby edytować konkretne ujęcie. Długość paska odpowiada czasowi trwania, kolor — beatowi.</p>
          <MontageBars plan={plan} active={selectedShot} onChoose={setSelectedShot} />
          {selected && <div className="director-shot-editor" key={selected.id}>
            <div className="flow-card-head"><h3>Edytor ujęcia</h3><div className="flow-actions">
              <button title="Przesuń wyżej" onClick={() => moveShot(selected.id, -1)}><ArrowUp size={14}/></button>
              <button title="Przesuń niżej" onClick={() => moveShot(selected.id, 1)}><ArrowDown size={14}/></button>
              <button title="Usuń ujęcie" disabled={plan.shots.length <= 1} onClick={() => {
                savePlan(x => { if (x.shots.length > 1) x.shots = x.shots.filter(z => z.id !== selected.id); }); setSelectedShot(null); }}><Trash2 size={14}/></button>
            </div></div>
            <label>Typ ujęcia<select value={selected.typeId} onChange={e => updateShot(selected.id, { typeId: e.target.value, title: shotKinds.find(x => x.id === e.target.value)?.name || selected.title })}>
              {shotKinds.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></label>
            <label>Beat<select value={selected.beatId} onChange={e => updateShot(selected.id, { beatId: e.target.value })}>
              {plan.beats.map((b, i) => <option value={b.id} key={b.id}>Beat {String(i + 1).padStart(2, "0")} · {b.title}</option>)}</select></label>
            <label>Tytuł ujęcia<input key={selected.id + ":" + selected.title} {...text(selected.title, directorLimits.title, v => updateShot(selected.id, { title: v }))} /></label>
            <label>Opis obrazu<textarea rows={3} key={selected.id + ":desc:" + selected.description} {...text(selected.description, directorLimits.description, v => updateShot(selected.id, { description: v }))} /></label>
            <div className="director-shot-fields">
              <label>Czas w sekundach<input key={selected.id + ":dur:" + selected.duration} type="number" min="0.1" max="120" step="0.1" defaultValue={selected.duration} onBlur={e => {
                const value = Math.round(Math.min(120, Math.max(.1, Number(e.target.value) || 1)) * 10) / 10;
                e.target.value = String(value);
                if (value !== selected.duration) updateShot(selected.id, { duration: value }); }}/></label>
              <label>Przejście<select value={selected.transition} onChange={e => updateShot(selected.id, { transition: e.target.value })}>
                {[...new Set([...transitions, selected.transition])].map(t => <option key={t} value={t}>{t}</option>)}</select></label>
            </div>
            <label>Dźwięk<input key={selected.id + ":sound:" + selected.sound} {...text(selected.sound, directorLimits.sound, v => updateShot(selected.id, { sound: v }))} /></label>
          </div>}
          <div className="flow-actions">
            <Button icon={Plus} disabled={plan.shots.length >= directorLimits.shots} onClick={() => {
              const shot: DirectorShot = {
                id: key(), beatId: plan.shots.find(x => x.id === selectedShot)?.beatId || plan.beats[plan.beats.length - 1]?.id || "",
                typeId: "medium", title: "Medium Shot",
                description: (chosen(outline)?.description || "").slice(0, directorLimits.description), duration: 2, transition: "cut", sound: "" };
              savePlan(x => { x.shots.push(shot); });
              setSelectedShot(shot.id);
            }}>Dodaj ujęcie</Button>
            <Button icon={RefreshCw} onClick={() => { setSelectedShot(null); prepare(false); }}>Zaproponuj inny montaż</Button>
          </div>
        </section>
      </div>}
      <div className="flow-footer">
        <div>{isApproved(flow, "direction") ? <span className="flow-ok"><Check size={16}/> Reżyseria zatwierdzona</span> :
          !isApproved(flow, "outlines") ? <span className="flow-warning">Najpierw zatwierdź plan scen</span> :
          <span className="director-muted">{counts.ready} z {outlines.length} scen gotowych{counts.missing ? `, ${counts.missing} bez planu` : ""}{counts.stale ? `, ${counts.stale} nieaktualnych (⚠)` : ""}. Każda zmiana planu wymaga ponownego zatwierdzenia.</span>}</div>
        <div className="flow-actions">
          <Button disabled={!isReady(flow, "direction") || isApproved(flow, "direction")} icon={Check}
            onClick={() => commit(f => { f.approved.direction = stageSignature(f, "direction"); }, "Reżyseria zatwierdzona. Teraz utwórz ujęcia z planu.")}>Zatwierdź reżyserię</Button>
          <Button disabled={!isApproved(flow, "direction")} primary onClick={applyShotList}>Utwórz ujęcia z planu <ArrowRight size={15}/></Button>
          <Button onClick={() => s.setPage("scenes")}>Przejdź do scen</Button>
        </div>
      </div>
    </>}
  </div>;
}
