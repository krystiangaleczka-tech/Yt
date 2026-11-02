import { useEffect, useMemo, useState } from "react";
import { ArrowDown, ArrowRight, ArrowUp, BookOpen, Check, Copy, Plus, RefreshCw, Sparkles, Trash2 } from "lucide-react";
import { useStudio } from "./context";
import { Button, SectionHead } from "./components";
import { api } from "./api";
import { makeScene } from "./Generation";
import { chosen, flowFrom, isApproved, isReady, sceneSourceSignature, stageSignature } from "./flowTypes";
import type { FlowData } from "./flowTypes";
import {
  buildAutoPlan, directorPatterns, parseDirectorAI, patternById, shotKinds, clampTension,
} from "./directorTypes";
import type { DirectorBeat, DirectorShot, DirectorMode, SceneDirection } from "./directorTypes";
import "./Director.css";

function key() { return crypto.randomUUID(); }
function seconds(n: number) { return n.toFixed(1).replace(".", ",") + " s"; }
function TensionChart({ beats }: { beats: DirectorBeat[] }) {
  const values = beats.length ? [beats[0].tensionBefore, ...beats.map(b => b.tensionAfter)] : [0, 0];
  const points = values.map((v, i) => (30 + i * 540 / (values.length - 1)) + "," + (140 - v * 12)).join(" ");
  return <div className="director-chart" role="img" aria-label={"Mapa napięcia: " + values.join(", ") + " w skali 0–10"}>
    <svg viewBox="0 0 600 174" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
      {[0, 5, 10].map(v => <g key={v}><line x1="30" x2="570" y1={140-v*12} y2={140-v*12} stroke="currentColor" opacity=".12"/><text x="8" y={144-v*12} fill="currentColor" fontSize="11">{v}</text></g>)}
      <polyline fill="none" stroke="#80a9f8" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" points={points} />
      {values.map((v,i) => <g key={i}><circle cx={30+i*540/(values.length-1)} cy={140-v*12} r="5" fill="#80a9f8"/><text x={30+i*540/(values.length-1)} y="164" fontSize="10" textAnchor="middle" fill="currentColor">{i===0?"Start":"Beat "+i}</text></g>)}
    </svg>
    <span className="director-muted">Skala 0–10 jest oceną dramaturgiczną, nie obiektywnym pomiarem emocji.</span>
  </div>;
}
function MontageBars({ shots, onChoose, active }: {
  shots: DirectorShot[]; onChoose: (id: string) => void; active: string | null;
}) {
  const max = Math.max(1, ...shots.map(s => s.duration));
  let cursor = 0;
  return <div className="director-bars" aria-label="Plan montażowy">
    {shots.map((shot, i) => {
      const start = cursor; cursor += shot.duration;
      return <button type="button" className={"director-bar-row " + (active === shot.id ? "active" : "")}
        key={shot.id} onClick={() => onChoose(shot.id)} title={"Edytuj ujęcie " + (i+1)}>
        <span className="director-time">{seconds(start)}–{seconds(cursor)}</span>
        <span className="director-bar" style={{ width: Math.max(8, shot.duration / max * 100) + "%", background: i % 3 === 0 ? "#6185cc" : i % 3 === 1 ? "#b78d55" : "#b56565" }} />
        <span className="director-bar-name">{String(i+1).padStart(2, "0")}. {shot.title} <small>{seconds(shot.duration)}</small></span>
      </button>;
    })}
  </div>;
}
export default function Director() {
  const s = useStudio();
  const p = s.project!;
  const flow = flowFrom(p);
  const [sceneId, setSceneId] = useState("");
  const [view, setView] = useState<"plan" | "library">("plan");
  const [selectedShot, setSelectedShot] = useState<string | null>(null);
  const [patternId, setPatternId] = useState("");
  const [guidance, setGuidance] = useState("");
  const [filter, setFilter] = useState("");
  const [newPattern, setNewPattern] = useState("");
  const [busy, setBusy] = useState(false);
  const outline = flow.outlines.find(x => x.id === sceneId) || flow.outlines[0];
  const plan = outline ? flow.director.plans[outline.id] : undefined;
  const stale = Boolean(plan && plan.sourceSignature !== sceneSourceSignature(flow, outline.id));
  const options = useMemo(() => [...directorPatterns, ...flow.director.customPatterns], [flow.director.customPatterns]);
  useEffect(() => { setSelectedShot(null); setPatternId(""); setGuidance(""); }, [outline?.id]);
  const selected = plan?.shots.find(x => x.id === selectedShot);
  const totalDuration = plan?.shots.reduce((sum, shot) => sum + shot.duration, 0) || 0;
  const selectedPattern = patternById(plan?.patternId || patternId || "anticipation", flow.director.customPatterns);
  function save(edit: (flow: FlowData) => void) {
    s.run(() => s.patch(current => {
      const next = structuredClone(flowFrom(current));
      edit(next);
      return { legacy: { ...current.legacy, production_flow: next } };
    }));
  }
  function savePlan(edit: (plan: SceneDirection) => void) {
    if (!outline || !plan) return;
    save(f => { const target = f.director.plans[outline.id]; if (target) edit(target); });
  }
  function prepare(all: boolean) {
    if (!outline) { s.notify("Najpierw dodaj sceny w planie scen.", true); return; }
    save(f => {
      const targets = all ? f.outlines : f.outlines.filter(row => row.id === outline.id);
      for (const target of targets) {
        // Bulk planning never overwrites any existing manual edits, even stale ones.
        if (all && f.director.plans[target.id]) continue;
        const previous = f.director.plans[target.id];
        const preferred = all ? "" : patternId;
        f.director.plans[target.id] = buildAutoPlan(f, target, f.director.mode, preferred, all ? "" : guidance);
        if (previous) f.director.plans[target.id].notes = guidance || previous.notes;
      }
    });
    s.notify(all ? "Przygotowano plany brakujących scen." : "Zapisano nowy plan sceny.");
  }
  async function generateAI() {
    if (!outline) return;
    setBusy(true);
    try {
      const response = await api<{response: string; base_revision: number}>(
        "/projects/" + p.id + "/flow/ai/direction/generate",
        { target_id: outline.id, instruction: guidance + "\nPreferowany wzorzec: " + (patternId || selectedPattern.id) });
      const targetId = outline.id;
      await s.patch(current => {
        if (current.revision !== response.base_revision) throw new Error("Projekt zmienił się podczas generowania. Ponów próbę.");
        const next = structuredClone(flowFrom(current));
        const target = next.outlines.find(x => x.id === targetId);
        if (!target) throw new Error("Scena została usunięta.");
        next.director.plans[targetId] = parseDirectorAI(response.response, next, target, next.director.mode);
        return { legacy: { ...current.legacy, production_flow: next } };
      });
      s.notify("Plan AI zapisany. Sprawdź beaty i ujęcia przed zatwierdzeniem.");
    } catch (error) { s.notify(error instanceof Error ? error.message : String(error), true); }
    finally { setBusy(false); }
  }
  function applyShotList() {
    if (!isApproved(flow, "direction")) { s.notify("Najpierw zatwierdź aktualny plan reżyserii.", true); return; }
    s.run(async () => {
      await s.patch(current => {
        const f = flowFrom(current);
        if (!isApproved(f, "direction")) throw new Error("Reżyseria wymaga ponownego zatwierdzenia.");
        const registered = new Set(current.scenes.map(shot => String(shot.legacy.flow_outline_id || "")));
        const prepared = f.outlines.filter(row => !registered.has(row.id));
        if (!prepared.length) throw new Error("Sceny mają już ujęcia. Nie duplikuję ani nie nadpisuję Twojego montażu.");
        const fps = current.sequence.fps_num / current.sequence.fps_den;
        let cursor = Math.max(0, ...current.scenes.map(shot => shot.start + shot.duration));
        const produced = prepared.flatMap(row => {
          const direction = f.director.plans[row.id];
          const parent = f.sequences.find(item => item.id === row.sectionId);
          return direction.shots.map((item, index) => {
            const shot = makeScene(cursor);
            const frameDuration = Math.max(1, Math.round(item.duration * fps));
            shot.title = (chosen(row)?.title || "Scena") + " · " + String(index + 1).padStart(2, "0") + " · " + item.title;
            shot.prompt = item.description;
            shot.director_notes = "Typ: " + item.typeId + ". Przejście: " + item.transition + ". Dźwięk: " + item.sound;
            shot.duration = frameDuration;
            shot.legacy = { ...shot.legacy, flow_act_id: parent?.actId || "", flow_section_id: row.sectionId,
              flow_outline_id: row.id, flow_director_shot_id: item.id, flow_director_beat_id: item.beatId,
              flow_director_kind: item.typeId };
            cursor += frameDuration;
            return shot;
          });
        });
        return { scenes: [...current.scenes, ...produced] };
      });
      s.notify("Ujęcia dodane do scen, bez nadpisywania istniejących.");
      s.setPage("scenes");
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
    const selectedBase = patternById(patternId || "anticipation", flow.director.customPatterns);
    save(f => f.director.customPatterns.push({
      ...selectedBase, id: "custom-" + key(), name: newPattern.trim().slice(0, 100),
      purpose: "Własny wzorzec do edycji podczas planowania scen.", cue: "Wybierz ręcznie.", rhythm: selectedBase.rhythm,
    }));
    setNewPattern("");
    s.notify("Wzorzec dodany do biblioteki projektu.");
  }
  return <div className="page-content flow-page director-page">
    <SectionHead eyebrow="ETAP REŻYSERII" title="Beaty, napięcie i plan montażowy"
      description="Na podstawie zatwierdzonych scen przygotuj rytm, ujęcia i wykres napięcia. Dopiero potem wygeneruj kadry.">
      <span className="flow-counter">{flow.outlines.length} scen · {Object.keys(flow.director.plans).length} planów</span>
    </SectionHead>
    <div className="director-topbar">
      <div className="flow-tabs" role="group" aria-label="Zakładki reżyserii">
        <button className={view === "plan" ? "active" : ""} onClick={() => setView("plan")}>Planowanie scen</button>
        <button className={view === "library" ? "active" : ""} onClick={() => setView("library")}><BookOpen size={14}/> Biblioteka wzorców i ujęć</button>
      </div>
      <label>Tryb pracy
        <select value={flow.director.mode} onChange={e => save(f => { f.director.mode = e.target.value as DirectorMode; })}>
          <option value="auto">Automatyczny</option><option value="guided">Z wytycznymi</option><option value="manual">Ręczny</option>
        </select>
      </label>
    </div>
    {view === "library" ? <>
      <section className="flow-card director-library-controls">
        <h3>Biblioteka reżyserii i montażu</h3>
        <p>Wzorce pomagają budować emocje, ale nie są sztywnymi regułami. Domyślne wzorce są wspólne dla wszystkich projektów, własne zapisują się w aktualnym filmie.</p>
        <input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Szukaj: suspense, POV, telefon, pościg..." aria-label="Szukaj w bibliotece"/>
        <div className="director-library-create"><input value={newPattern} onChange={e => setNewPattern(e.target.value)} placeholder="Nazwa własnego wzorca" aria-label="Nazwa nowego wzorca" />
          <Button icon={Plus} disabled={!newPattern.trim()} onClick={addPattern}>Dodaj wzorzec</Button></div>
      </section>
      <div className="director-library-grid">
        {options.filter(item => (item.name + item.purpose + item.cue).toLowerCase().includes(filter.toLowerCase())).map(item =>
          <section className="flow-card" key={item.id}><h3>{item.name}</h3>
            <p>{item.purpose}</p><p className="director-muted">{item.cue}</p>
            <small>Rytm: {item.rhythm}</small>
            <div className="director-chipline">{item.shots.map((id,i) => <span key={i}>{shotKinds.find(x => x.id === id)?.name || id}</span>)}</div>
            <div className="flow-actions"><Button onClick={() => { setView("plan"); setPatternId(item.id); }}>Użyj w scenie</Button>
              {item.id.startsWith("custom-") && <Button icon={Trash2} onClick={() => save(f => {
                f.director.customPatterns = f.director.customPatterns.filter(x => x.id !== item.id);
              })}>Usuń własny</Button>}</div>
          </section>)}
      </div>
      <h3>Rodzaje ujęć</h3>
      <div className="director-library-grid">{shotKinds.filter(item => (item.name + item.usage).toLowerCase().includes(filter.toLowerCase())).map(item =>
        <section key={item.id} className="flow-card"><h3>{item.name}</h3><p className="director-muted">{item.usage}</p></section>)}</div>
    </> : <>
      <div className="director-toolbar flow-card">
        <label>Scena do reżyserowania
          <select value={outline?.id || ""} onChange={e => setSceneId(e.target.value)}>
            {flow.outlines.map((item,i) => <option value={item.id} key={item.id}>{i+1}. {chosen(item)?.title || "Scena bez tytułu"} · {item.seconds} s</option>)}
          </select>
        </label>
        <div className="director-status">
          {isApproved(flow, "outlines") ? <span className="flow-ok"><Check size={14}/> Plan scen zatwierdzony</span> :
            <span className="flow-warning">Najpierw zatwierdź Plan scen</span>}
          {stale && <span className="flow-warning">Opis sceny zmieniony. Plan wymaga ponownej generacji.</span>}
        </div>
        <div className="flow-actions">
          <Button icon={Sparkles} disabled={!outline} onClick={() => prepare(false)}>{plan ? "Przelicz bieżącą scenę" : "Zaplanuj scenę"}</Button>
          <Button icon={Copy} disabled={!flow.outlines.length} onClick={() => prepare(true)}>Zaplanuj brakujące sceny</Button>
        </div>
        <div className="director-guidance">
          <label>Wzorzec reżyserski
            <select value={patternId || plan?.patternId || ""} onChange={e => setPatternId(e.target.value)}>
              <option value="">Dobierz automatycznie</option>
              {options.map(item => <option value={item.id} key={item.id}>{item.name}</option>)}
            </select>
          </label>
          <label>Wytyczne (opcjonalnie)
            <textarea rows={2} placeholder="Np. od telefonu do okna; coraz krótsze cięcia, a na końcu nieruchome ujęcie..." value={guidance} onChange={e => setGuidance(e.target.value)} />
          </label>
        </div>
        <div className="flow-actions"><Button icon={Sparkles} busy={busy} disabled={!outline || busy} onClick={() => s.run(generateAI)}>Wygeneruj bardziej filmowo przez AI</Button>
          <span className="director-muted">Automatyczny plan działa także bez podłączonego modelu AI.</span></div>
      </div>
      {!outline ? <div className="flow-empty"><p>Brak scen. Wróć do Planu scen, dodaj sceny i wróć tutaj.</p>
        <Button icon={ArrowRight} onClick={() => s.setPage("scene-plan")}>Otwórz plan scen</Button></div> :
      !plan ? <div className="flow-empty">Wybierz „Zaplanuj scenę” lub „Zaplanuj brakujące sceny”. System wyznaczy beaty, wykres napięcia i cięcia.</div> :
      <div className="director-grid">
        <section className="flow-card">
          <div className="flow-card-head"><h3>Mapa napięcia · {chosen(outline)?.title}</h3><span className="director-muted">{plan.beats.length} beatów</span></div>
          <p className="director-muted">Zamierzony efekt: {selectedPattern.purpose}. {selectedPattern.rhythm}</p>
          <TensionChart beats={plan.beats} />
          <div className="director-beats">
            {plan.beats.map((beat,i) => <details key={beat.id} open={i===0 ? true : undefined}>
              <summary><strong>Beat {String(i+1).padStart(2, "0")} · {beat.title}</strong><span>{beat.tensionBefore} → {beat.tensionAfter}/10</span></summary>
              <label>Nazwa beatu<input defaultValue={beat.title} key={beat.id+":title"} onBlur={e => { if (e.target.value !== beat.title) updateBeat(beat.id, {title:e.target.value}); }}/></label>
              <label>Cel dramaturgiczny<textarea rows={2} defaultValue={beat.goal} key={beat.id+":goal"} onBlur={e => { if (e.target.value !== beat.goal) updateBeat(beat.id, {goal:e.target.value}); }}/></label>
              <div className="director-tension-inputs">
                <label>Przed: {beat.tensionBefore}<input type="range" min="0" max="10" value={beat.tensionBefore} onChange={e => updateBeat(beat.id, {tensionBefore:clampTension(Number(e.target.value))})}/></label>
                <label>Po: {beat.tensionAfter}<input type="range" min="0" max="10" value={beat.tensionAfter} onChange={e => updateBeat(beat.id, {tensionAfter:clampTension(Number(e.target.value))})}/></label>
              </div>
              <label>Co wie widz<input defaultValue={beat.viewerKnows} key={beat.id+":view"} onBlur={e => updateBeat(beat.id, {viewerKnows:e.target.value})}/></label>
              <label>Co wie bohater<input defaultValue={beat.characterKnows} key={beat.id+":character"} onBlur={e => updateBeat(beat.id, {characterKnows:e.target.value})}/></label>
              <label>Sygnał dźwiękowy<input defaultValue={beat.soundCue} key={beat.id+":sound"} onBlur={e => updateBeat(beat.id, {soundCue:e.target.value})}/></label>
            </details>)}
          </div>
        </section>
        <section className="flow-card">
          <div className="flow-card-head"><h3>Plan montażowy</h3><span className="director-muted">{seconds(totalDuration)} / plan {seconds(outline.seconds)}</span></div>
          <p className="director-muted">Wybierz pasek, żeby edytować konkretne ujęcie. Długość paska odpowiada czasowi trwania.</p>
          <MontageBars shots={plan.shots} active={selectedShot} onChoose={setSelectedShot} />
          {selected && <div className="director-shot-editor" key={selected.id}>
            <div className="flow-card-head"><h3>Edytor ujęcia</h3><div className="flow-actions">
              <button title="Przesuń wyżej" onClick={() => moveShot(selected.id,-1)}><ArrowUp size={14}/></button>
              <button title="Przesuń niżej" onClick={() => moveShot(selected.id,1)}><ArrowDown size={14}/></button>
              <button title="Usuń ujęcie" onClick={() => { savePlan(x => { if (x.shots.length > 1) x.shots = x.shots.filter(z => z.id !== selected.id); }); setSelectedShot(null); }}><Trash2 size={14}/></button>
            </div></div>
            <label>Typ ujęcia<select value={selected.typeId} onChange={e => updateShot(selected.id, {typeId:e.target.value, title:shotKinds.find(x => x.id === e.target.value)?.name || selected.title})}>
              {shotKinds.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></label>
            <label>Beat<select value={selected.beatId} onChange={e => updateShot(selected.id, {beatId:e.target.value})}>
              {plan.beats.map(b => <option value={b.id} key={b.id}>{b.title}</option>)}</select></label>
            <label>Opis obrazu<textarea rows={3} defaultValue={selected.description} onBlur={e => updateShot(selected.id, {description:e.target.value})}/></label>
            <div className="director-shot-fields">
              <label>Czas w sekundach<input type="number" min="0.1" max="120" step="0.1" defaultValue={selected.duration} onBlur={e => updateShot(selected.id, {duration:Math.min(120,Math.max(.1,Number(e.target.value)||1))})}/></label>
              <label>Przejście<select value={selected.transition} onChange={e => updateShot(selected.id, {transition:e.target.value})}>
                {["cut","smash-cut","match-cut","dissolve","dip","whip","flash"].map(t => <option key={t} value={t}>{t}</option>)}</select></label>
            </div>
            <label>Dźwięk<input defaultValue={selected.sound} onBlur={e => updateShot(selected.id, {sound:e.target.value})}/></label>
          </div>}
          <div className="flow-actions">
            <Button icon={Plus} onClick={() => savePlan(x => { const shot:DirectorShot = {
              id:key(), beatId:x.beats[0]?.id || "", typeId:"medium", title:"Medium Shot",
              description:chosen(outline)?.description || "", duration:2, transition:"cut", sound:"" };
              x.shots.push(shot); })}>Dodaj ujęcie</Button>
            <Button icon={RefreshCw} onClick={() => { setSelectedShot(null); prepare(false); }}>Zaproponuj inny montaż</Button>
          </div>
        </section>
      </div>}
      <div className="flow-footer">
        <div>{isApproved(flow, "direction") ? <span className="flow-ok"><Check size={16}/> Reżyseria zatwierdzona</span> :
          !isApproved(flow, "outlines") ? <span className="flow-warning">Najpierw zatwierdź plan scen</span> :
          <span className="director-muted">{Object.keys(flow.director.plans).length} z {flow.outlines.length} scen przygotowanych; każda zmiana planu unieważnia zatwierdzenie.</span>}</div>
        <div className="flow-actions">
          <Button disabled={!isReady(flow,"direction") || isApproved(flow,"direction")} icon={Check} onClick={() => save(f => { f.approved.direction = stageSignature(f,"direction"); })}>Zatwierdź reżyserię</Button>
          <Button disabled={!isApproved(flow,"direction")} primary onClick={applyShotList}>Utwórz ujęcia z planu <ArrowRight size={15}/></Button>
          <Button onClick={() => s.setPage("scenes")}>Przejdź do scen</Button>
        </div>
      </div>
    </>}
  </div>;
}
