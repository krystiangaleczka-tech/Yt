import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import {
  AlertTriangle, ArrowRight, Check, FolderInput, ImagePlus, ListPlus, Pause, Play, Plus, StepBack, StepForward,
  Trash2, Undo2, WandSparkles, X,
} from "lucide-react";
import { useStudio } from "./context";
import { api, mediaUrl, upload } from "./api";
import type { Asset, Project } from "./types";
import { Button, CommitText, SectionHead } from "./components";
import {
  MAX_SKETCH_VARIANTS, approvalState, clock, emptySketch, flipTimes, indexAt, isEmptySketch, newVariantId, nextShotId,
  shotsFromScenario, sketchLabel, sketchLetter, sketchesFrom, starts, totalSeconds,
  type SketchShot, type SketchSourceFile, type SketchVariant, type Sketches as SketchState,
} from "./sketchTypes";
import "./FilmFlow.css";
import "./Sketches.css";

type ImportResult = {
  project: Project;
  imported: { variantId: string; title: string; shots: number; frames: number; missing: number; path: string }[];
  warnings: string[];
};

/** Przegląd jak kartkowanie zeszytu: cały film w kilkadziesiąt sekund, kartka proporcjonalna do ujęcia. */
function Flipbook({ shots, playSeconds, projectId, assets, caption }: {
  shots: SketchShot[];
  playSeconds: number;
  projectId: string;
  assets: Map<string, Asset>;
  caption?: string;
}) {
  const times = useMemo(() => flipTimes(shots.map((x) => x.seconds), playSeconds), [shots, playSeconds]);
  const begin = useMemo(() => starts(times), [times]);
  const film = useMemo(() => starts(shots.map((x) => x.seconds)), [shots]);
  const total = playSeconds;
  const [time, setTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const clockRef = useRef(0);
  const preload = useRef<HTMLImageElement[]>([]);
  useEffect(() => {
    if (time > total) { clockRef.current = total; setTime(total); }
  }, [total, time]);
  useEffect(() => {
    if (!playing) return;
    let frame = 0, last: number | null = null;
    const tick = (now: number) => {
      clockRef.current = Math.min(total, clockRef.current + (last === null ? 0 : (now - last) / 1000));
      last = now;
      setTime(clockRef.current);
      if (clockRef.current >= total) { setPlaying(false); return; }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, total]);
  useEffect(() => {
    // Miniatury ładowane z góry, żeby kartkowanie nie czekało na sieć.
    preload.current = [...new Set(shots.map((x) => x.assetId).filter(Boolean))].flatMap((id) => {
      const asset = assets.get(id);
      if (!asset) return [];
      const image = new Image();
      image.src = mediaUrl(projectId, id, Boolean(asset.thumbnail));
      return [image];
    });
  }, [shots, assets, projectId]);
  if (!shots.length)
    return <div className="sk-flip sk-flip-empty">Wklej scenariusz albo dodaj ujęcia — przegląd pojawi się tutaj.</div>;
  const index = Math.max(0, indexAt(begin, Math.min(time, total - 1e-6)));
  const shot = shots[index];
  const asset = shot.assetId ? assets.get(shot.assetId) : undefined;
  const seek = (value: number) => { clockRef.current = Math.max(0, Math.min(total, value)); setTime(clockRef.current); };
  const step = (delta: number) => {
    // Od bieżącego czasu, nie od ostatniego renderu: kilka szybkich naciśnięć = kilka ujęć.
    const at = Math.max(0, indexAt(begin, Math.min(clockRef.current, total - 1e-6)));
    seek(begin[Math.max(0, Math.min(shots.length - 1, at + delta))] + 1e-4);
  };
  const toggle = () => {
    if (!playing && clockRef.current >= total - 1e-3) seek(0);
    setPlaying(!playing);
  };
  function keys(event: KeyboardEvent<HTMLDivElement>) {
    if ((event.target as HTMLElement).tagName === "INPUT" && event.key !== " ") return;
    if (event.key === " ") { event.preventDefault(); toggle(); }
    else if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
    else if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
  }
  return (
    <div className="sk-flip" tabIndex={0} onKeyDown={keys} aria-label="Przegląd szkicu: spacja — odtwarzaj/pauza, strzałki — poprzednie/następne ujęcie">
      <div className="sk-frame" onClick={toggle}>
        {asset ? (
          <>
            <img src={mediaUrl(projectId, asset.id, playing && Boolean(asset.thumbnail))} alt={shot.description || `Ujęcie ${shot.nr}`} />
            <span className="sk-frame-nr">#{shot.nr}{shot.key ? ` · ${shot.key}` : ""}</span>
            {shot.mark && <span className="sk-card-mark">{shot.mark}</span>}
          </>
        ) : (
          <div className="sk-card">
            <span className="sk-frame-nr">#{shot.nr}{shot.key ? ` · ${shot.key}` : ""}</span>
            {shot.mark && <span className="sk-card-mark">{shot.mark}</span>}
            {shot.kadr && <div className="sk-card-kadr">{shot.kadr}</div>}
            <div className="sk-card-desc">{shot.description || "—"}</div>
            {shot.line && <div className="sk-card-line">{shot.line}</div>}
          </div>
        )}
        {!playing && time === 0 && <span className="sk-frame-play"><Play size={34} /></span>}
      </div>
      <div className="sk-controls">
        <button type="button" onClick={() => step(-1)} aria-label="Poprzednie ujęcie" title="Poprzednie ujęcie (←)"><StepBack size={16} /></button>
        <button type="button" className="sk-play-button" onClick={toggle} aria-label={playing ? "Pauza" : "Odtwarzaj"} title="Odtwarzaj / pauza (spacja)">
          {playing ? <Pause size={18} /> : <Play size={18} />}
        </button>
        <button type="button" onClick={() => step(1)} aria-label="Następne ujęcie" title="Następne ujęcie (→)"><StepForward size={16} /></button>
        <div className="sk-scrub">
          <input type="range" min={0} max={total} step={0.01} value={time} aria-label="Przewijanie przeglądu"
            onChange={(e) => seek(Number(e.target.value))} />
          <div className="sk-marks" aria-hidden="true">
            {shots.map((x, i) => x.mark ? <span key={x.id} style={{ left: `${(begin[i] / total) * 100}%` }} title={x.mark} /> : null)}
          </div>
        </div>
        <span className="sk-time">{(Math.round(time * 10) / 10).toFixed(1).replace(".", ",")} / {total} s</span>
      </div>
      <div className="sk-now">
        <strong>Ujęcie {index + 1}/{shots.length} · {clock(film[index])} w filmie · {String(Math.round(shot.seconds * 10) / 10).replace(".", ",")} s</strong>
        {caption && <small className="muted"> · {caption}</small>}
        {asset && shot.description && <p>{shot.description}</p>}
        {asset && shot.line && <p className="sk-now-line">„{shot.line}”</p>}
      </div>
    </div>
  );
}

function SecondsInput({ value, onCommit, label = "Sekundy", min = 0.1, max = 600, step = 0.5 }: {
  value: number; onCommit: (v: number) => void; label?: string; min?: number; max?: number; step?: number;
}) {
  const [v, setV] = useState(String(value));
  const focused = useRef(false);
  useEffect(() => { if (!focused.current) setV(String(value)); }, [value]);
  return <input type="number" min={min} max={max} step={step} value={v} aria-label={label}
    onFocus={() => { focused.current = true; }}
    onChange={(e) => setV(e.target.value)}
    onBlur={() => {
      focused.current = false;
      const n = Number(v);
      if (Number.isFinite(n) && n >= min && n <= max) { if (n !== value) onCommit(n); } else setV(String(value));
    }} />;
}

function VariantCard({ variant, index, sk, project, assets, save, approve, withdraw, uploadFrame, remove }: {
  variant: SketchVariant;
  index: number;
  sk: SketchState;
  project: Project;
  assets: Map<string, Asset>;
  save: (edit: (v: SketchVariant) => void) => void;
  approve: () => void;
  withdraw: () => void;
  uploadFrame: (shotId: string, file: File) => void;
  remove: () => void;
}) {
  const [open, setOpen] = useState(false);
  const isApproved = sk.approved?.variantId === variant.id;
  const state = isApproved ? approvalState(sk) : "none";
  const auto = useMemo(() => (variant.shots.length ? [] : shotsFromScenario(variant.scenario, variant.id)),
    [variant.shots.length, variant.scenario, variant.id]);
  const shots = variant.shots.length ? variant.shots : auto;
  const empty = isEmptySketch(variant);
  const changeShot = (id: string, edit: (x: SketchShot) => void) =>
    save((v) => { const x = v.shots.find((y) => y.id === id); if (x) edit(x); });
  return (
    <section className={`flow-card sk-variant ${isApproved ? "approved" : ""}`}>
      <header className="sk-variant-head">
        <span className="sk-letter" aria-hidden="true">{sketchLetter(index)}</span>
        <div className="sk-variant-title">
          <small className="muted">{sketchLabel(index)}{variant.source?.path ? ` · z pliku ${variant.source.path}` : ""}</small>
          <CommitText value={variant.title} label={`Tytuł ${sketchLabel(index)}`} placeholder="Nazwa podejścia, np. „Dwa hooki: miecz i kruk”"
            onCommit={(value) => save((v) => { v.title = value; })} />
          <span className="sk-stats">
            {shots.length} {variant.shots.length ? "ujęć" : "kart z akapitów"} · film {clock(totalSeconds(shots))}
            {variant.shots.some((x) => x.assetId) ? ` · ${variant.shots.filter((x) => x.assetId).length} klatek` : ""}
          </span>
        </div>
        <div className="sk-variant-actions">
          {state === "current" && <span className="flow-ok"><Check size={15} /> Zatwierdzony</span>}
          {state === "stale" && <span className="flow-warning"><AlertTriangle size={15} /> Zmieniony po zatwierdzeniu</span>}
          {state !== "current" && (
            <Button primary={!sk.approved || state === "stale"} icon={Check} disabled={empty} onClick={approve}
              title={empty ? "Najpierw wklej scenariusz albo dodaj ujęcia" : undefined}>
              {state === "stale" ? "Zatwierdź ponownie" : "Zatwierdź ten szkic"}
            </Button>
          )}
          {isApproved && <Button subtle icon={Undo2} onClick={withdraw}>Cofnij zatwierdzenie</Button>}
          <button type="button" className="icon-button" aria-label={`Usuń ${sketchLabel(index)}`} disabled={isApproved}
            title={isApproved ? "Zatwierdzonego wariantu nie można usunąć" : `Usuń ${sketchLabel(index)}`} onClick={remove}>
            <Trash2 size={16} />
          </button>
        </div>
      </header>

      <div className="sk-scenario">
        {!variant.scenario.trim() || open ? (
          <>
            <CommitText multiline rows={open ? 16 : 5} value={variant.scenario} label={`Scenariusz ${sketchLabel(index)}`}
              placeholder="Wklej scenariusz tego podejścia: strukturę, hooki, kwestie lektora. Akapit = ujęcie; krótka linia „HOOK 1” albo „# Pogorszenie” to znacznik następnego ujęcia."
              onCommit={(value) => save((v) => { v.scenario = value; })} />
            {open && <button type="button" className="flow-quiet" onClick={() => setOpen(false)}>Zwiń scenariusz</button>}
          </>
        ) : (
          <div className="sk-scenario-preview">
            <p>{variant.scenario.slice(0, 420)}{variant.scenario.length > 420 ? "…" : ""}</p>
            <button type="button" className="flow-quiet" onClick={() => setOpen(true)}>Pokaż cały i edytuj</button>
          </div>
        )}
      </div>

      <Flipbook shots={shots} playSeconds={sk.playSeconds} projectId={project.id} assets={assets}
        caption={variant.shots.length ? undefined : "karty z akapitów scenariusza"} />

      <details className="sk-shots">
        <summary>Ujęcia ({variant.shots.length}) — edytuj</summary>
        <div className="flow-inline-actions">
          <button type="button" onClick={() => save((v) => {
            const nr = Math.max(0, ...v.shots.map((x) => x.nr)) + 1;
            v.shots.push({ id: nextShotId(v), nr, key: "", kadr: "", seconds: 4, description: "", line: "", mark: "", assetId: "" });
          })}><ListPlus size={14} /> Dodaj ujęcie</button>
          <button type="button" disabled={!variant.scenario.trim()} onClick={() => {
            if (variant.shots.length && !window.confirm(`Zastąpić ${variant.shots.length} ujęć rozpiską z akapitów scenariusza?`)) return;
            save((v) => { v.shots = shotsFromScenario(v.scenario, v.id); });
          }}><WandSparkles size={14} /> Rozpisz scenariusz na ujęcia</button>
        </div>
        {variant.shots.length > 0 && <div className="sk-table">
          <table>
            <thead><tr><th>Nr</th><th>Klucz</th><th>Kadr</th><th>s</th><th>Opis</th><th>Kwestia</th><th>Znacznik</th><th>Klatka</th><th /></tr></thead>
            <tbody>{variant.shots.map((x) => {
              const frame = x.assetId ? assets.get(x.assetId) : undefined;
              return <tr key={x.id}>
                <td className="sk-nr"><SecondsInput label="Numer ujęcia" min={0} max={9999} step={1} value={x.nr} onCommit={(n) => changeShot(x.id, (y) => { y.nr = Math.trunc(n); })} /></td>
                <td><CommitText value={x.key} label="Klucz" onCommit={(value) => changeShot(x.id, (y) => { y.key = value; })} /></td>
                <td><CommitText value={x.kadr} label="Kadr" placeholder="plan ogólny" onCommit={(value) => changeShot(x.id, (y) => { y.kadr = value; })} /></td>
                <td className="sk-sec"><SecondsInput value={x.seconds} onCommit={(n) => changeShot(x.id, (y) => { y.seconds = n; })} /></td>
                <td><CommitText multiline rows={2} value={x.description} label="Opis" onCommit={(value) => changeShot(x.id, (y) => { y.description = value; })} /></td>
                <td><CommitText multiline rows={2} value={x.line} label="Kwestia" onCommit={(value) => changeShot(x.id, (y) => { y.line = value; })} /></td>
                <td><CommitText value={x.mark} label="Znacznik" placeholder="HOOK 1" onCommit={(value) => changeShot(x.id, (y) => { y.mark = value; })} /></td>
                <td className="sk-frame-cell">
                  {frame ? <img src={mediaUrl(project.id, frame.id, Boolean(frame.thumbnail))} alt="" /> : x.assetId ? <small className="muted">brak pliku</small> : null}
                  <label className="flow-quiet"><ImagePlus size={13} /> Wgraj
                    <input type="file" accept="image/png,image/jpeg,image/webp" hidden onChange={(e) => {
                      const file = e.target.files?.[0];
                      e.target.value = "";
                      if (file) uploadFrame(x.id, file);
                    }} />
                  </label>
                  {x.assetId && <button type="button" className="flow-quiet" onClick={() => changeShot(x.id, (y) => { y.assetId = ""; })}>Usuń</button>}
                </td>
                <td><button type="button" className="icon-button" aria-label={`Usuń ujęcie ${x.nr}`} title="Usuń ujęcie"
                  onClick={() => save((v) => { v.shots = v.shots.filter((y) => y.id !== x.id); })}><X size={15} /></button></td>
              </tr>;
            })}</tbody>
          </table>
        </div>}
      </details>
    </section>
  );
}

export default function Sketches() {
  const s = useStudio(), p = s.project!;
  const sk = sketchesFrom(p);
  const state = approvalState(sk);
  const assets = useMemo(() => new Map(p.assets.map((a) => [a.id, a])), [p.assets]);
  const [sources, setSources] = useState<SketchSourceFile[]>([]);
  const [path, setPath] = useState("");
  const [result, setResult] = useState<ImportResult | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    api<{ sources: SketchSourceFile[] }>("/sketches/sources").then((r) => setSources(r.sources)).catch(() => setSources([]));
  }, []);
  const folders = useMemo(() => {
    const byFolder = new Map<string, { film: string; count: number }>();
    for (const x of sources) {
      const folder = x.path.split("/").slice(0, -1).join("/");
      const entry = byFolder.get(folder) || { film: x.film, count: 0 };
      entry.count += 1;
      byFolder.set(folder, entry);
    }
    return [...byFolder.entries()].filter(([, v]) => v.count > 1);
  }, [sources]);

  const put = (current: Project, next: SketchState) => api<Project>(`/projects/${current.id}/sketches`, {
    expected_revision: current.revision, sketches: { variants: next.variants, playSeconds: next.playSeconds },
  }, "PUT");
  const saveAll = (edit: (next: SketchState) => void) => s.run(() => s.mutate(async (current) => {
    const next = structuredClone(sketchesFrom(current));
    edit(next);
    return put(current, next);
  }));
  const saveVariant = (id: string) => (edit: (v: SketchVariant) => void) => saveAll((next) => {
    const v = next.variants.find((x) => x.id === id);
    if (!v) throw new Error("Ten wariant został usunięty w innym oknie");
    edit(v);
  });
  function approve(v: SketchVariant, index: number) {
    const other = sk.approved && sk.approved.variantId !== v.id ? sk.approved : null;
    if (other && !window.confirm(`Zatwierdzony jest „${other.title}”. Zatwierdzić zamiast niego ${v.title ? `„${v.title}”` : sketchLabel(index)}?`)) return;
    s.run(async () => {
      await s.mutate((current) => api<Project>(`/projects/${current.id}/sketches/approve`,
        { variant_id: v.id, expected_revision: current.revision }));
      s.notify(`Zatwierdzony szkic: ${v.title || sketchLabel(index)}. Wpis jest w dzienniku pracy.`);
    });
  }
  const withdraw = () => {
    if (!window.confirm("Cofnąć zatwierdzenie szkicu? Dalsze etapy stracą wskazany kierunek.")) return;
    s.run(() => s.mutate((current) => api<Project>(`/projects/${current.id}/sketches/withdraw`, { expected_revision: current.revision })));
  };
  const uploadFrame = (variantId: string) => (shotId: string, file: File) => s.run(() => s.mutate(async (current) => {
    const uploaded = await upload<{ asset: Asset; project: Project }>(`/projects/${current.id}/media`, file);
    const next = structuredClone(sketchesFrom(uploaded.project));
    const shot = next.variants.find((v) => v.id === variantId)?.shots.find((x) => x.id === shotId);
    if (!shot) return uploaded.project;
    shot.assetId = uploaded.asset.id;
    return put(uploaded.project, next);
  }));
  const remove = (v: SketchVariant, index: number) => {
    if (!isEmptySketch(v) && !window.confirm(`Usunąć ${sketchLabel(index)}${v.title ? ` „${v.title}”` : ""} razem z ujęciami?`)) return;
    saveAll((next) => { next.variants = next.variants.filter((x) => x.id !== v.id); });
  };
  function runImport() {
    if (!path.trim()) return;
    setBusy(true);
    s.run(async () => {
      try {
        let outcome: ImportResult | null = null;
        await s.mutate(async (current) => {
          outcome = await api<ImportResult>(`/projects/${current.id}/sketches/import`, { path: path.trim() });
          return outcome.project;
        });
        setResult(outcome);
        const done = (outcome as ImportResult | null)?.imported || [];
        s.notify(`Wczytano ${done.length === 1 ? "1 wariant" : `${done.length} warianty`}: ${done.map((x) => x.title || x.variantId).join(", ")}`);
      } finally {
        setBusy(false);
      }
    });
  }
  const approvedVariant = sk.approved ? sk.variants.find((v) => v.id === sk.approved!.variantId) : undefined;
  return (
    <div className="page-content flow-page sk-page">
      <SectionHead eyebrow="PRODUKCJA KROK PO KROKU" title="Szkice ujęć"
        description="Po tytule, przed rozpiską: kilka zupełnie różnych podejść do tej samej opowieści. Przekartkuj każde i zatwierdź jedno.">
        <span className="flow-counter">{p.channel} · {p.development.target_minutes} min</span>
      </SectionHead>
      <div className="flow-explainer">
        Każdy wariant to inny scenariusz tego samego tytułu (inne hooki, kolejność, punkt widzenia). Wklej scenariusz — przegląd pod nim od
        razu kartkuje go jak zeszyt: akapit to karta, długość kartki zależy od długości ujęcia, cały film mija w {sk.playSeconds} s. Ujęcia
        z klatkami wczytasz z plików (<code>docs/filmy/&lt;film&gt;/szkice/&lt;wariant&gt;/szkic.json</code>) albo dopiszesz ręcznie. Zatwierdzony
        szkic jest kierunkiem dla Master Story, rozpiski i AI; zatwierdzenie trafia do dziennika pracy.
      </div>
      <div className={`flow-bible-strip sk-status ${state}`}>
        <span>Zatwierdzony szkic</span>
        <strong>
          {state === "none" && "jeszcze żaden — obejrzyj przeglądy i zatwierdź jeden wariant"}
          {state === "current" && <>„{sk.approved!.title}” ✓ · {approvedVariant?.shots.length || 0} ujęć · film {clock(totalSeconds(approvedVariant?.shots || []))}</>}
          {state === "stale" && <>„{sk.approved!.title}” — zmieniony po zatwierdzeniu, zatwierdź go ponownie</>}
          {state === "missing" && <>„{sk.approved!.title}” — wariant został usunięty</>}
        </strong>
      </div>
      <div className="flow-card sk-toolbar">
        <label className="sk-play-seconds">Przegląd trwa
          <SecondsInput label="Czas przeglądu w sekundach" min={5} max={180} step={1} value={sk.playSeconds} onCommit={(n) => {
            const value = Math.max(5, Math.min(180, Math.round(n)));
            saveAll((next) => { next.playSeconds = value; });
          }} /> s
        </label>
        <div className="sk-import">
          <select value={sources.some((x) => x.path === path) || folders.some(([f]) => f === path) ? path : ""}
            onChange={(e) => setPath(e.target.value)} aria-label="Szkice w plikach">
            <option value="">{sources.length ? "Szkice w plikach…" : "Brak szkiców w docs/filmy/*/szkice/"}</option>
            {folders.map(([folder, v]) => <option key={folder} value={folder}>{v.film}: wszystkie warianty ({v.count})</option>)}
            {sources.map((x) => <option key={x.path} value={x.path} disabled={Boolean(x.error)}>
              {x.film} / {x.wariant}{x.tytul ? ` — ${x.tytul}` : ""}{x.error ? " (błąd pliku)" : ` (${x.shots} ujęć, ${x.frames} klatek)`}
            </option>)}
          </select>
          <input value={path} onChange={(e) => setPath(e.target.value)} placeholder="albo ścieżka: docs/filmy/<film>/szkice" aria-label="Katalog szkiców" />
          <Button icon={FolderInput} busy={busy} disabled={!path.trim()} onClick={runImport}>Importuj z plików</Button>
        </div>
        <Button icon={Plus} disabled={sk.variants.length >= MAX_SKETCH_VARIANTS}
          onClick={() => saveAll((next) => { next.variants.push(emptySketch(newVariantId(next))); })}>Wariant</Button>
      </div>
      {result && <div className="flow-explainer sk-import-result">
        <strong>Import:</strong> {result.imported.map((x) => `${x.title || x.variantId} — ${x.shots} ujęć, ${x.frames} klatek${x.missing ? `, brakujące klatki: ${x.missing} (zamiast nich karty)` : ""}`).join("; ")}
        {result.warnings.length > 0 && <ul>{result.warnings.slice(0, 20).map((w) => <li key={w}><AlertTriangle size={13} /> {w}</li>)}</ul>}
        <button type="button" onClick={() => setResult(null)}>Zamknij</button>
      </div>}
      {sk.variants.map((v, i) => (
        <VariantCard key={v.id} variant={v} index={i} sk={sk} project={p} assets={assets} save={saveVariant(v.id)}
          approve={() => approve(v, i)} withdraw={withdraw} uploadFrame={uploadFrame(v.id)} remove={() => remove(v, i)} />
      ))}
      <div className="flow-footer">
        <span className="muted">{state === "current" ? "Szkic zatwierdzony — rozpisz go w Master Story." : "Bez zatwierdzonego szkicu kontrola ciągłości pokaże uwagę."}</span>
        <Button primary icon={ArrowRight} onClick={() => s.setPage("master-story")}>Dalej: Master Story</Button>
      </div>
    </div>
  );
}
