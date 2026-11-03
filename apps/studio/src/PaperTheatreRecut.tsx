import { useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { ChevronLeft, ChevronRight, RotateCcw, Scissors, Undo2 } from "lucide-react";
import { api, mediaUrl } from "./api";
import { useStudio } from "./context";
import { Button, Field, NumberField } from "./components";
import type { Project, Scene } from "./types";
import {
  addPoint, normalizeBox, readyToRun, removeNearest, setBox, settingsPayload, toImage,
} from "./recutPrompt";
import type { Point, Prompt, RecutObject, RecutOptions, Stroke } from "./recutPrompt";

type Report = {
  warnings: string[];
  final_mean_abs_diff: number;
  final_px_over_20: number;
  unowned_px: number;
  seconds: number;
  leftovers: { key: string; area: number }[];
  layers: Record<string, { visible: number; extended: number; empty: boolean }>;
};
type Result = {
  job_id: string;
  map: Record<string, string>;
  background: string;
  extra: { key: string; name: string; asset_id: string }[];
  leftovers: { key: string; area: number; asset_id: string }[];
  review_asset_id: string;
  report: Report;
};
type RecutState = {
  width: number;
  height: number;
  objects: RecutObject[];
  extra_objects: RecutObject[];
  options: RecutOptions;
  result: Result | null;
  applied: boolean;
};
type Runtime = { python_ready: boolean; models: Record<string, boolean>; models_dir: string };
type Tool = "pos" | "neg" | "box" | "erase" | "smear";

const GROUP_LABEL: Record<string, string> = {
  sky: "niebo", landscape: "krajobraz", foundations: "architektura", vegetation: "roślinność",
  props: "rekwizyt", characters: "postać", hero: "bohater",
};

/** Re-cut the scene's cutouts along real contours with local MobileSAM + LaMa. */
export default function PaperTheatreRecut({ scene }: { scene: Scene }) {
  const studio = useStudio();
  const project = studio.project!;
  const [runtime, setRuntime] = useState<Runtime | null>(null);
  const [data, setData] = useState<RecutState | null>(null);
  const [objects, setObjects] = useState<RecutObject[]>([]);
  const [extras, setExtras] = useState<RecutObject[]>([]);
  const [options, setOptions] = useState<RecutOptions | null>(null);
  const [edited, setEdited] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState("");
  const [tool, setTool] = useState<Tool>("pos");
  const [strokeWidth, setStrokeWidth] = useState(20);
  const [drag, setDrag] = useState<Point[] | null>(null);
  const [jobId, setJobId] = useState("");
  const [dirty, setDirty] = useState(false);
  const [newName, setNewName] = useState("");
  const [newGroup, setNewGroup] = useState("props");
  const svgRef = useRef<SVGSVGElement>(null);

  const load = async () => {
    const [rt, st] = await Promise.all([
      api<Runtime>("/paper-theatre/recut/runtime"),
      api<RecutState>(`/projects/${project.id}/paper-theatre/${scene.id}/recut`),
    ]);
    setRuntime(rt);
    setData(st);
    setObjects(st.objects);
    setExtras(st.extra_objects || []);
    setOptions(st.options);
    setEdited(new Set(st.objects.filter((o) => !o.prompt.auto).map((o) => o.key)));
    setSelected((current) => current || st.objects[0]?.key || "");
    setDirty(false);
  };

  useEffect(() => { studio.run(load); }, [scene.id]);

  useEffect(() => {
    if (!jobId) return;
    const job = studio.jobs.find((item) => item.id === jobId);
    if (job?.status === "SUCCEEDED") {
      setJobId("");
      studio.run(async () => {
        await studio.reload();
        await load();
        studio.notify("Nowe wycinki są w bibliotece. Sprawdź arkusz kontroli i zastosuj je.");
      });
    } else if (job?.status === "FAILED" || job?.status === "CANCELLED") {
      setJobId("");
      studio.notify(job.message || "Rozcinanie zostało przerwane", true);
    }
  }, [jobId, studio.jobs]);

  const all = useMemo(() => [...objects, ...extras], [objects, extras]);
  const current = all.find((o) => o.key === selected);
  const index = objects.findIndex((o) => o.key === selected);
  const job = studio.jobs.find((item) => item.id === jobId);
  const width = data?.width || 1280, height = data?.height || 720;
  const poster = `/api/projects/${project.id}/scenes/${scene.id}/poster?revision=${project.revision}&frame=${Math.max(0, scene.duration - 1)}`;

  const updatePrompt = (key: string, change: (p: Prompt) => Prompt) => {
    const apply = (list: RecutObject[]) => list.map((o) => o.key === key ? { ...o, prompt: change(o.prompt) } : o);
    setObjects(apply);
    setExtras(apply);
    setEdited((s) => new Set(s).add(key));
    setDirty(true);
  };
  const updateObject = (key: string, patch: Partial<RecutObject>) => {
    const apply = (list: RecutObject[]) => list.map((o) => o.key === key ? { ...o, ...patch } : o);
    setObjects(apply);
    setExtras(apply);
    setDirty(true);
  };
  const updateOptions = (patch: Partial<RecutOptions>) => {
    setOptions((o) => o ? { ...o, ...patch } : o);
    setDirty(true);
  };

  const point = (event: ReactPointerEvent) => {
    const rect = svgRef.current!.getBoundingClientRect();
    return toImage(event.clientX, event.clientY, rect, width, height);
  };
  const down = (event: ReactPointerEvent<SVGSVGElement>) => {
    if (!current && tool !== "smear") return;
    const p = point(event);
    if (tool === "box" || tool === "smear") {
      event.currentTarget.setPointerCapture(event.pointerId);
      setDrag([p]);
    } else if (tool === "erase") {
      updatePrompt(current!.key, (pr) => removeNearest(pr, p));
    } else {
      updatePrompt(current!.key, (pr) => addPoint(pr, p, tool === "pos" && !event.shiftKey));
    }
  };
  const move = (event: ReactPointerEvent<SVGSVGElement>) => {
    if (!drag) return;
    const p = point(event);
    setDrag(tool === "box" ? [drag[0], p] : [...drag, p]);
  };
  const up = () => {
    if (!drag) return;
    if (tool === "box" && current && drag.length > 1) {
      updatePrompt(current.key, (pr) => setBox(pr, normalizeBox(drag[0], drag[drag.length - 1])));
    } else if (tool === "smear" && options) {
      const pts = drag.filter((_, i) => i % 3 === 0 || i === drag.length - 1).slice(0, 64);
      updateOptions({ smear_strokes: [...options.smear_strokes, { points: pts, width: strokeWidth } as Stroke].slice(-60) });
    }
    setDrag(null);
  };

  const save = async () => {
    const p = await studio.mutate((p) => api<Project>(`/projects/${p.id}/paper-theatre/${scene.id}/recut/settings`, {
      expected_revision: p.revision, settings: settingsPayload(objects, edited, extras, options!),
    }));
    setDirty(false);
    return p;
  };
  const run = () => studio.run(async () => {
    const problem = readyToRun(extras);
    if (problem) throw new Error(problem);
    const p = await save();
    const started = await api<{ id: string }>(`/projects/${p.id}/paper-theatre/${scene.id}/recut/run`, {
      expected_revision: p.revision,
    });
    setJobId(started.id);
    studio.notify("Rozcinanie działa lokalnie w tle. Przy ~120 wycinkach zajmuje kilka minut.");
  });
  const accept = () => studio.run(async () => {
    await studio.mutate((p) => api<Project>(`/projects/${p.id}/paper-theatre/${scene.id}/recut/accept`, { expected_revision: p.revision }));
    await load();
    studio.notify("Ujęcie używa nowych wycinków. Start z samego papieru; poprzednie zostały zachowane.");
  });
  const revert = () => studio.run(async () => {
    await studio.mutate((p) => api<Project>(`/projects/${p.id}/paper-theatre/${scene.id}/recut/revert`, { expected_revision: p.revision }));
    await load();
    studio.notify("Przywrócono poprzednie wycinki i plan wejść.");
  });
  const addExtra = () => {
    const name = newName.trim();
    if (!name) return;
    const key = "extra_" + Date.now().toString(36);
    const box: [number, number, number, number] = [Math.round(width * .4), Math.round(height * .4), Math.round(width * .6), Math.round(height * .6)];
    setExtras((list) => [...list, { key, name, group: newGroup, depth: objects.length + list.length, prompt: { box, pos: [], neg: [], hull: "auto" } }]);
    setSelected(key);
    setTool("box");
    setNewName("");
    setDirty(true);
  };

  if (!data || !options) return <section className="surface tool-panel"><h2>Ponowne rozcięcie</h2><p className="muted">Wczytywanie…</p></section>;

  const report = data.result?.report;
  const pr = current?.prompt;
  return (
    <section className="surface" style={{ padding: 12, marginTop: 12 }}>
      <h2>Rozetnij ponownie · czyste wycinki na papierze</h2>
      <p className="small muted">
        Każdy obiekt jest wycinany po prawdziwym konturze (MobileSAM, lokalnie i bezpłatnie). Film startuje z samego papieru;
        pod postaciami nic nie jest rozmywane ani dorysowywane — do ich wejścia widać papier. Dorysowane są tylko części
        scenografii zasłonięte przez inną scenografię (LaMa). Nazwy, kolejność i czasy wejść zostają bez zmian.
      </p>
      {runtime && !runtime.python_ready && (
        <p role="alert">Brak środowiska modeli obrazu. Zainstaluj: <code>python scripts/install_studio.py --with-models</code>.</p>
      )}
      {runtime?.python_ready && Object.values(runtime.models).some((v) => !v) && (
        <p className="small muted">Przy pierwszym uruchomieniu modele (ok. 245 MB) zostaną pobrane do {runtime.models_dir}.</p>
      )}
      <div className="production-grid">
        <div>
          <div className="button-row" role="toolbar" aria-label="Narzędzia konturu">
            <Button primary={tool === "pos"} onClick={() => setTool("pos")}>+ Punkt obiektu</Button>
            <Button primary={tool === "neg"} onClick={() => setTool("neg")}>− Punkt tła</Button>
            <Button primary={tool === "box"} onClick={() => setTool("box")}>Ramka</Button>
            <Button primary={tool === "erase"} onClick={() => setTool("erase")}>Usuń punkt</Button>
            <Button primary={tool === "smear"} onClick={() => setTool("smear")}>Smuga do usunięcia</Button>
          </div>
          <div style={{ position: "relative", width: "100%", aspectRatio: `${width} / ${height}` }}>
            <img src={poster} alt="Ostatnia klatka ujęcia — tu zaznaczasz kontury" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
            <svg ref={svgRef} viewBox={`0 0 ${width} ${height}`} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", cursor: "crosshair", touchAction: "none" }}
              onPointerDown={down} onPointerMove={move} onPointerUp={up} onPointerCancel={() => setDrag(null)}
              aria-label="Kliknij obiekt: punkt dodatni; Shift lub narzędzie „−” dodaje punkt tła; przeciągnij, by narysować ramkę">
              {options.smear_strokes.map((s, i) => (
                <polyline key={"s" + i} points={s.points.map((p) => p.join(",")).join(" ")} fill="none" stroke="rgba(220,40,40,.45)" strokeWidth={s.width} strokeLinecap="round" />
              ))}
              {pr && <>
                <rect x={pr.box[0]} y={pr.box[1]} width={pr.box[2] - pr.box[0]} height={pr.box[3] - pr.box[1]} fill="none" stroke="#ffd34d" strokeWidth={2} strokeDasharray="6 4" />
                {pr.extra?.map((e, i) => <rect key={"e" + i} x={e.box[0]} y={e.box[1]} width={e.box[2] - e.box[0]} height={e.box[3] - e.box[1]} fill="none" stroke="#ffd34d" strokeWidth={1} strokeDasharray="2 3" />)}
                {pr.poly && <polygon points={pr.poly.map((p) => p.join(",")).join(" ")} fill="rgba(255,211,77,.15)" stroke="#ffd34d" />}
                {[...pr.pos, ...(pr.parts?.flat() || []), ...(pr.extra?.flatMap((e) => e.pos) || [])].map((p, i) => (
                  <circle key={"p" + i} cx={p[0]} cy={p[1]} r={6} fill="#23c55e" stroke="#fff" strokeWidth={2} />
                ))}
                {pr.neg.map((p, i) => <circle key={"n" + i} cx={p[0]} cy={p[1]} r={6} fill="#ef4444" stroke="#fff" strokeWidth={2} />)}
              </>}
              {drag && tool === "box" && drag.length > 1 && (() => {
                const b = normalizeBox(drag[0], drag[drag.length - 1]);
                return <rect x={b[0]} y={b[1]} width={b[2] - b[0]} height={b[3] - b[1]} fill="rgba(255,211,77,.12)" stroke="#ffd34d" />;
              })()}
              {drag && tool === "smear" && <polyline points={drag.map((p) => p.join(",")).join(" ")} fill="none" stroke="rgba(220,40,40,.45)" strokeWidth={strokeWidth} strokeLinecap="round" />}
            </svg>
          </div>
          <p className="small muted">Zielony = należy do obiektu, czerwony = nie należy. Postaciom zaznacz osobno głowę, tułów, rękaw i dłoń — każdy punkt liczy się jako osobna część.</p>
          {tool === "smear" && <div className="button-row">
            <NumberField label="Szerokość smugi (px)" value={strokeWidth} min={2} max={80} step={1} onCommit={setStrokeWidth} />
            <Button onClick={() => updateOptions({ smear_strokes: [] })} disabled={!options.smear_strokes.length}>Wyczyść smugi ({options.smear_strokes.length})</Button>
          </div>}
        </div>
        <div>
          <Field label="Obiekt">
            <select value={selected} onChange={(e) => setSelected(e.target.value)}>
              {objects.map((o) => (
                <option key={o.key} value={o.key}>
                  {(report?.layers[o.key]?.empty ? "⚠ " : edited.has(o.key) ? "✎ " : "") + o.name} · {GROUP_LABEL[o.group] || o.group}
                </option>
              ))}
              {extras.map((o) => <option key={o.key} value={o.key}>➕ {o.name} · {GROUP_LABEL[o.group] || o.group}</option>)}
            </select>
          </Field>
          <div className="button-row">
            <Button icon={ChevronLeft} disabled={index <= 0} onClick={() => setSelected(objects[index - 1].key)}>Poprzedni</Button>
            <Button icon={ChevronRight} disabled={index < 0 || index >= objects.length - 1} onClick={() => setSelected(objects[index + 1].key)}>Następny</Button>
          </div>
          {current && <>
            <NumberField label="Przesłanianie (większe = bliżej widza)" value={current.depth} min={-1000} max={1000} step={.1}
              onCommit={(v) => updateObject(current.key, { depth: v })} />
            <Field label="Dopełnienie zasłoniętych części (tylko scenografia)">
              <select value={current.prompt.hull || "auto"} onChange={(e) => updatePrompt(current.key, (p) => ({ ...p, hull: e.target.value as Prompt["hull"] }))}>
                <option value="auto">automatyczne</option>
                <option value="circle">pełne koło (słońce, księżyc)</option>
                <option value="none">bez dopełniania</option>
              </select>
            </Field>
            <div className="button-row">
              <Button icon={RotateCcw} disabled={!current.auto_prompt}
                onClick={() => {
                  updatePrompt(current.key, () => ({ ...current.auto_prompt!, auto: true }));
                  setEdited((s) => { const n = new Set(s); n.delete(current.key); return n; });
                }}>Automatyczny kontur</Button>
              {current.key.startsWith("extra_") && <Button onClick={() => { setExtras((l) => l.filter((o) => o.key !== current.key)); setSelected(objects[0]?.key || ""); setDirty(true); }}>Usuń nowy obiekt</Button>}
            </div>
          </>}
          <h3>Obiekt, którego nie ma w planie</h3>
          <p className="small muted">Np. wiązka bambusa przed bohaterem. Dostanie własny wycinek i wejście na końcu swojej grupy.</p>
          <div className="two-fields">
            <Field label="Nazwa"><input value={newName} onChange={(e) => setNewName(e.target.value)} /></Field>
            <Field label="Grupa">
              <select value={newGroup} onChange={(e) => setNewGroup(e.target.value)}>
                {Object.entries(GROUP_LABEL).filter(([k]) => k !== "hero").map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </Field>
          </div>
          <Button onClick={addExtra} disabled={!newName.trim()}>Dodaj obiekt i narysuj ramkę</Button>
          <h3>Reszta sceny</h3>
          <Field label="Piksele, które nie należą do żadnego obiektu (niebo, rzeka, ściany)">
            <select value={options.leftover} onChange={(e) => updateOptions({ leftover: e.target.value as RecutOptions["leftover"] })}>
              <option value="layers">osobne wycinki scenografii, wchodzą jako pierwsze</option>
              <option value="merge">dołącz do najbliższych wycinków scenografii</option>
              <option value="paper">zostaw papier (raport pokaże braki)</option>
            </select>
          </Field>
          <label className="checkbox small"><input type="checkbox" checked={options.fix_seams} onChange={(e) => updateOptions({ fix_seams: e.target.checked })} /> Usuń szwy po starych wielokątach</label>
          <label className="checkbox small"><input type="checkbox" checked={options.complete_scenery} onChange={(e) => updateOptions({ complete_scenery: e.target.checked })} /> Dorysuj zasłoniętą scenografię (nigdy pod postaciami)</label>
          <div className="button-row">
            <Button onClick={() => studio.run(save)} disabled={!dirty}>Zapisz ustawienia</Button>
            <Button icon={Scissors} primary busy={!!jobId} disabled={!runtime?.python_ready} onClick={run}>Rozetnij ponownie</Button>
          </div>
          {job && <p aria-live="polite" className="small">{Math.round(job.progress * 100)}% · {job.message}</p>}
        </div>
      </div>
      {data.result && report && (
        <section aria-live="polite" style={{ marginTop: 12 }}>
          <h3>Wynik {data.applied ? "· zastosowany" : "· czeka na akceptację"}</h3>
          <p className="small">
            {Object.keys(data.result.map).length} wycinków · {data.result.leftovers.length} wycinków reszty sceny · {data.result.extra.length} nowych obiektów ·
            ostatnia klatka vs źródło: średnia różnica {report.final_mean_abs_diff}, pikseli &gt;20: {report.final_px_over_20} · {report.seconds} s
          </p>
          {report.warnings.map((w, i) => <p className="small muted" key={i}>⚠ {w}</p>)}
          <details>
            <summary>Arkusz kontroli: każdy obiekt z zielonym konturem</summary>
            <img alt="Arkusz kontroli: każdy obiekt z zielonym konturem" style={{ width: "100%" }} src={mediaUrl(project.id, data.result.review_asset_id)} />
          </details>
          <div className="button-row">
            {!data.applied && <Button primary onClick={accept}>Zastosuj nowe wycinki</Button>}
            {data.applied && <Button icon={Undo2} onClick={revert}>Przywróć poprzednie wycinki</Button>}
          </div>
        </section>
      )}
    </section>
  );
}
