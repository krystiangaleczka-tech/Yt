import { Fragment, useEffect, useMemo, useState, type ReactNode } from "react";
import { AlertTriangle, BookOpen, Check, ClipboardList, Globe2, History, RefreshCw, Save, Wrench } from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import { Button } from "./components";
import Markdown from "./Markdown";
import type { Project } from "./types";
import "./Continuity.css";

type Issue = { severity: 1 | 2 | 3; rule: string; message: string; ref: string; unit: number | null; hint: string };
type UnitRow = {
  unit: number; actId: string; title: string; shots: number; seconds: number; voiceShare: number; equalNeighbours: number;
  signature: string; review: string; linked: number[]; issues: Record<string, number>; impactedBy?: number[];
};
type Report = { units: UnitRow[]; issues: Issue[]; totals: Record<string, number> };
type Review = { status: string; checks: Record<string, string>; notes: string; reviewer: string; at: string; signature: string };
type LogEntry = { id: string; at: string; who: string; unit: number | null; kind: string; summary: string; details: string; files: string[] };
type Book = { pipeline?: string; method?: string; files?: { path: string; role: string }[] };
type Tab = "check" | "reviews" | "world" | "book" | "log" | "ai";

const CHECKS: [string, string, string][] = [
  ["scenario", "Scenariusz", "Ujęcia opowiadają to, co scenariusz jednostki i Master Story; nic ważnego nie wypadło."],
  ["chronology", "Chronologia", "Pora dnia, kolejność i czas zgadzają się z poprzednimi jednostkami."],
  ["beats", "Beaty", "Każdy beat ma przyczynę i skutek; napięcie rośnie do kulminacji."],
  ["tempo", "Tempo", "Długości z treści, jednostka w zakresie, sąsiednie ujęcia się różnią."],
  ["narration", "Narracja", "Lektor dopowiada, nie opisuje; nie zdradza niczego przed czasem; jest cisza."],
  ["continuity", "Ciągłość", "Zero błędów wagi 3; księga świata opisuje, co jednostka zmienia."],
  ["frames", "Kadr", "Każde ujęcie przeszło Wytyczne kadru i ma wydarzenie."],
];
const WEIGHT: Record<number, string> = { 3: "psuje logikę", 2: "widz wyłapie", 1: "drobne" };
const WORLD_GROUPS: [string, string][] = [
  ["places", "Miejsca"], ["characters", "Postacie"], ["props", "Rekwizyty"], ["resources", "Zasoby"], ["rules", "Zasady świata"],
  ["events", "Zdarzenia"], ["threads", "Wątki"], ["spoilers", "Spoilery"], ["decisions", "Decyzje"],
];

const flowOf = (p: Project) => (p.legacy?.production_flow || {}) as Record<string, unknown>;
const unitName = (label: string, n: number | null | undefined) => n === null || n === undefined ? "całość" : n === 0 ? "Prolog" : `${label} ${n}`;
const when = (iso: string) => iso ? new Date(iso).toLocaleString("pl-PL", { dateStyle: "short", timeStyle: "short" }) : "";

export default function ContinuityEditor({ aiReviews }: { aiReviews: ReactNode }) {
  const s = useStudio();
  const p = s.project!;
  const flow = flowOf(p);
  const world = (flow.world || {}) as Record<string, unknown>;
  const label = String(world.unitLabel || "Dzień");
  const [tab, setTab] = useState<Tab>("check");
  const [report, setReport] = useState<Report | null>(null);
  const [checking, setChecking] = useState(false);
  async function runCheck() {
    setChecking(true);
    try { setReport(await api<Report>(`/projects/${p.id}/continuity/check`, {})); }
    catch (e) { s.notify(String((e as Error).message), true); }
    finally { setChecking(false); }
  }
  useEffect(() => { void runCheck(); }, [p.id, p.revision]);
  const tabs: [Tab, string, typeof Check][] = [
    ["check", "Kontrola", AlertTriangle], ["reviews", "Recenzje jednostek", ClipboardList], ["world", "Księga świata", Globe2],
    ["book", "Warsztat filmu", Wrench], ["log", "Dziennik", History], ["ai", "Recenzenci AI", BookOpen],
  ];
  return <div className="cont">
    <div className="cont-tabs" role="tablist">
      {tabs.map(([id, name, Icon]) => <button key={id} role="tab" aria-selected={tab === id} className={tab === id ? "active" : ""}
        onClick={() => setTab(id)}><Icon size={15} />{name}{id === "check" && report && report.totals["3"] ? <span className="cont-badge w3">{report.totals["3"]}</span> : null}</button>)}
      <span className="cont-spacer" />
      <Button icon={RefreshCw} disabled={checking} onClick={runCheck}>{checking ? "Sprawdzam…" : "Sprawdź ciągłość"}</Button>
    </div>
    {tab === "check" && <CheckTab report={report} label={label} />}
    {tab === "reviews" && <ReviewsTab report={report} label={label} reviews={(flow.unitReviews || {}) as Record<string, Review>} />}
    {tab === "world" && <WorldTab world={world} />}
    {tab === "book" && <BookTab book={(flow.book || {}) as Book} />}
    {tab === "log" && <LogTab log={(flow.log || []) as LogEntry[]} label={label} />}
    {tab === "ai" && aiReviews}
  </div>;
}

function CheckTab({ report, label }: { report: Report | null; label: string }) {
  if (!report) return <div className="flow-empty">Sprawdzam plan filmu…</div>;
  const groups = new Map<string, Issue[]>();
  for (const i of report.issues) {
    const k = unitName(label, i.unit);
    groups.set(k, [...(groups.get(k) || []), i]);
  }
  return <>
    <div className="flow-explainer">Kontrola zestawia księgę świata z planem ujęć (Reżyseria i napięcie) bez udziału AI i niczego nie zmienia.
      Waga 3 psuje logikę historii — przed wykonaniem ujęć jednostki musi jej być zero.</div>
    <div className="cont-totals">{[3, 2, 1].map(w => <span key={w} className={`cont-badge w${w}`}>{report.totals[String(w)] || 0} · {WEIGHT[w]}</span>)}</div>
    {!report.issues.length ? <div className="flow-empty"><Check size={16} /> Brak uwag.</div> :
      [...groups.entries()].map(([unit, items]) => <section key={unit} className="flow-card cont-group">
        <h3>{unit}</h3>
        <ul className="cont-issues">{items.map((i, k) => <li key={k} className={`w${i.severity}`}>
          <span className={`cont-badge w${i.severity}`}>{i.severity}</span>
          <span className="cont-rule">{i.rule}</span>
          <code className={i.ref ? "" : "cont-noref"}>{i.ref.split("~")[0] || "—"}</code>
          <span>{i.message}</span>
          {i.hint && <small className="muted">{i.hint}</small>}
        </li>)}</ul>
      </section>)}
  </>;
}

function ReviewsTab({ report, label, reviews }: { report: Report | null; label: string; reviews: Record<string, Review> }) {
  const s = useStudio();
  const p = s.project!;
  const [open, setOpen] = useState<string | null>(null);
  const [draft, setDraft] = useState<{ checks: Record<string, string>; notes: string; reviewer: string }>({ checks: {}, notes: "", reviewer: "reżyser" });
  useEffect(() => {
    const r = open ? reviews[open] : undefined;
    setDraft({ checks: { ...(r?.checks || {}) }, notes: r?.notes || "", reviewer: r?.reviewer || "reżyser" });
  }, [open]);
  if (!report) return <div className="flow-empty">Sprawdzam plan filmu…</div>;
  function save(actId: string, status: string) {
    s.run(() => s.mutate(async () => api<Project>(`/projects/${p.id}/flow/review/${actId}`, { status, ...draft })));
  }
  const form = (actId: string) => (
<section className="flow-card cont-review">
      <h3>Recenzja: {unitName(label, report.units.find(u => u.actId === actId)?.unit)}</h3>
      {CHECKS.map(([key, name, hint]) => <div className="cont-check" key={key}>
        <div><strong>{name}</strong><small className="muted">{hint}</small></div>
        <div className="cont-seg">{[["ok", "Dobrze"], ["fix", "Do poprawy"], ["", "—"]].map(([v, t]) =>
          <button key={v} className={(draft.checks[key] || "") === v ? "active" : ""}
            onClick={() => setDraft(d => ({ ...d, checks: { ...d.checks, [key]: v } }))}>{t}</button>)}</div>
      </div>)}
      <label className="cont-field">Uwagi<textarea rows={4} value={draft.notes} onChange={e => setDraft(d => ({ ...d, notes: e.target.value }))} /></label>
      <label className="cont-field">Recenzent<input value={draft.reviewer} onChange={e => setDraft(d => ({ ...d, reviewer: e.target.value }))} /></label>
      <div className="flow-actions">
        <Button primary icon={Check} onClick={() => save(actId, "zatwierdzona")}>Zatwierdź jednostkę</Button>
        <Button icon={AlertTriangle} onClick={() => save(actId, "do poprawy")}>Do poprawy</Button>
        <Button onClick={() => save(actId, "robocza")}>Zapisz roboczo</Button>
      </div>
    </section>
  );
  const statusClass = (r: string) => r === "zatwierdzona" ? "ok" : r === "nieaktualna" || r === "do poprawy" ? "warn" : "idle";
  return <>
    <div className="flow-explainer">Po każdej jednostce recenzent przechodzi listę kontrolną. Recenzja ma podpis treści — zmiana ujęć, scenariusza
      jednostki albo powiązanych wpisów księgi ją unieważnia, a jednostki powiązane wątkiem dostają oznaczenie „do sprawdzenia”.</div>
    <div className="cont-table"><table>
      <thead><tr><th>Jednostka</th><th>Ujęcia</th><th>Czas</th><th>Lektor</th><th>Uwagi 3/2/1</th><th>Recenzja</th><th /></tr></thead>
      <tbody>{report.units.filter(u => u.actId).map(u => <Fragment key={u.actId}><tr className={open === u.actId ? "open" : ""}>
        <td><strong>{unitName(label, u.unit)}</strong> <span className="muted">{u.title.replace(/^Dzień \d+ · /, "")}</span>
          {u.impactedBy?.length ? <div className="cont-impact"><AlertTriangle size={13} /> do sprawdzenia po zmianie: {u.impactedBy.map(n => unitName(label, n)).join(", ")}</div> : null}</td>
        <td>{u.shots}</td><td>{u.seconds.toFixed(1)} s</td><td>{Math.round(u.voiceShare * 100)}%</td>
        <td>{[3, 2, 1].map(w => <span key={w} className={`cont-badge w${w} ${u.issues[String(w)] ? "" : "zero"}`}>{u.issues[String(w)] || 0}</span>)}</td>
        <td><span className={`cont-status ${statusClass(u.review)}`}>{u.review}</span></td>
        <td><Button onClick={() => setOpen(open === u.actId ? null : u.actId)}>{open === u.actId ? "Zamknij" : "Recenzuj"}</Button></td>
      </tr>{open === u.actId && <tr className="open"><td colSpan={7}>{form(u.actId)}</td></tr>}</Fragment>)}</tbody>
    </table></div>

  </>;
}

function WorldTab({ world }: { world: Record<string, unknown> }) {
  const s = useStudio();
  const p = s.project!;
  const initial = useMemo(() => JSON.stringify(world, null, 2), [p.revision]);
  const [text, setText] = useState(initial);
  const [error, setError] = useState("");
  useEffect(() => setText(initial), [initial]);
  function save() {
    let parsed: unknown;
    try { parsed = JSON.parse(text); } catch (e) { setError("To nie jest poprawny JSON: " + (e as Error).message); return; }
    setError("");
    s.run(() => s.mutate(async (current) => api<Project>(`/projects/${p.id}/flow/world`, { expected_revision: current.revision, world: parsed }, "PUT")));
  }
  const threads = (world.threads || []) as { title?: string; setup?: string[]; clues?: string[]; payoff?: string[]; open?: boolean }[];
  return <>
    <div className="flow-explainer">Wspólny stan świata filmu: plan budynku, postacie, rekwizyty, zasoby, zasady w czasie i wątki (zasiew → wskazówki →
      rozwiązanie). Odwołania do ujęć: <code>dNN_KK</code>. Opis pól: Podręcznik pracowni → „Sekwencja, świat i ciągłość”.</div>
    <div className="cont-totals">{WORLD_GROUPS.map(([k, t]) => <span key={k} className="cont-badge idle">{t}: {Array.isArray(world[k]) ? (world[k] as unknown[]).length : 0}</span>)}</div>
    {threads.length > 0 && <section className="flow-card"><h3>Wątki</h3><div className="cont-table"><table>
      <thead><tr><th>Wątek</th><th>Zasiew</th><th>Wskazówki</th><th>Rozwiązanie</th></tr></thead>
      <tbody>{threads.map((t, k) => <tr key={k}><td>{t.title}</td><td>{(t.setup || []).join(", ")}</td><td>{(t.clues || []).join(", ")}</td>
        <td>{(t.payoff || []).join(", ") || (t.open ? "otwarty" : "—")}</td></tr>)}</tbody>
    </table></div></section>}
    <section className="flow-card">
      <h3>Edycja księgi (JSON)</h3>
      <textarea className="cont-json" spellCheck={false} value={text} onChange={e => setText(e.target.value)} />
      {error && <p className="flow-warning">{error}</p>}
      <div className="flow-actions"><Button primary icon={Save} disabled={text === initial} onClick={save}>Zapisz księgę</Button>
        <Button disabled={text === initial} onClick={() => setText(initial)}>Cofnij zmiany</Button></div>
    </section>
  </>;
}

function BookTab({ book }: { book: Book }) {
  const s = useStudio();
  const p = s.project!;
  const [edit, setEdit] = useState(false);
  const [pipeline, setPipeline] = useState(book.pipeline || "");
  const [method, setMethod] = useState(book.method || "");
  const [files, setFiles] = useState((book.files || []).map(f => `${f.path} — ${f.role}`).join("\n"));
  useEffect(() => { setPipeline(book.pipeline || ""); setMethod(book.method || ""); setFiles((book.files || []).map(f => `${f.path} — ${f.role}`).join("\n")); }, [p.revision]);
  function save() {
    const list = files.split("\n").map(l => l.trim()).filter(Boolean).map(l => { const [path, ...rest] = l.split(" — "); return { path: path.trim(), role: rest.join(" — ").trim() }; });
    s.run(async () => {
      await s.mutate(async (current) => api<Project>(`/projects/${p.id}/flow/book`, { expected_revision: current.revision, book: { pipeline, method, files: list } }, "PUT"));
      setEdit(false);
    });
  }
  return <>
    <div className="flow-explainer">Warsztat tego filmu: czym i jak powstają ujęcia oraz sekwencje, jakie pliki i polecenia. Ma wystarczyć, żeby ktoś inny
      przejął pracę. Zasady wspólne dla wszystkich filmów są w Podręczniku pracowni.</div>
    <div className="flow-actions">{edit ? <><Button primary icon={Save} onClick={save}>Zapisz warsztat</Button><Button onClick={() => setEdit(false)}>Anuluj</Button></>
      : <Button icon={Wrench} onClick={() => setEdit(true)}>Edytuj</Button>}</div>
    {edit ? <div className="cont-book-edit">
      <label className="cont-field">Jak powstają ujęcia (Markdown)<textarea rows={16} value={pipeline} onChange={e => setPipeline(e.target.value)} /></label>
      <label className="cont-field">Jak powstają sekwencje i dni (Markdown)<textarea rows={16} value={method} onChange={e => setMethod(e.target.value)} /></label>
      <label className="cont-field">Pliki (jedna linia: ścieżka — rola)<textarea rows={10} value={files} onChange={e => setFiles(e.target.value)} /></label>
    </div> : <div className="flow-grid cont-book">
      <section className="flow-card"><h3>Jak powstają ujęcia</h3>{book.pipeline ? <Markdown text={book.pipeline} /> : <p className="muted">Brak opisu.</p>}</section>
      <section className="flow-card"><h3>Jak powstają sekwencje i dni</h3>{book.method ? <Markdown text={book.method} /> : <p className="muted">Brak opisu.</p>}</section>
      <section className="flow-card"><h3>Pliki</h3>{book.files?.length ? <div className="cont-table"><table><tbody>
        {book.files.map(f => <tr key={f.path}><td><code>{f.path}</code></td><td>{f.role}</td></tr>)}</tbody></table></div> : <p className="muted">Brak listy.</p>}</section>
    </div>}
  </>;
}

function LogTab({ log, label }: { log: LogEntry[]; label: string }) {
  const s = useStudio();
  const p = s.project!;
  const [entry, setEntry] = useState({ summary: "", details: "", kind: "praca", unit: "", who: "reżyser" });
  function add() {
    if (!entry.summary.trim()) return;
    s.run(async () => {
      await s.mutate(async () => api<Project>(`/projects/${p.id}/flow/log`, { entry: { ...entry, unit: entry.unit === "" ? null : Number(entry.unit) } }));
      setEntry(e => ({ ...e, summary: "", details: "" }));
    });
  }
  return <>
    <div className="flow-explainer">Krótki wpis po każdej pracy nad jednostką i po każdej decyzji: co, dlaczego, jakie pliki, wynik kontroli. Narzędzia filmu
      dopisują się same. Wpisów się nie kasuje.</div>
    <section className="flow-card cont-log-form">
      <div className="cont-row">
        <select value={entry.kind} onChange={e => setEntry({ ...entry, kind: e.target.value })}>
          {["praca", "tworzenie", "poprawka", "decyzja", "audyt", "wgranie", "recenzja"].map(k => <option key={k}>{k}</option>)}</select>
        <input placeholder={`${label} (numer)`} value={entry.unit} onChange={e => setEntry({ ...entry, unit: e.target.value.replace(/\D/g, "") })} />
        <input placeholder="Kto" value={entry.who} onChange={e => setEntry({ ...entry, who: e.target.value })} />
      </div>
      <input placeholder="Co zrobiono (jedno zdanie)" value={entry.summary} onChange={e => setEntry({ ...entry, summary: e.target.value })} />
      <textarea rows={3} placeholder="Szczegóły: dlaczego, pliki, wynik kontroli" value={entry.details} onChange={e => setEntry({ ...entry, details: e.target.value })} />
      <div className="flow-actions"><Button primary disabled={!entry.summary.trim()} onClick={add}>Dopisz do dziennika</Button></div>
    </section>
    {!log.length ? <div className="flow-empty">Dziennik jest pusty.</div> : <ol className="cont-log">{[...log].reverse().map(e => <li key={e.id}>
      <div className="cont-log-head"><span className="cont-badge idle">{e.kind}</span><strong>{e.summary}</strong>
        <span className="muted">{unitName(label, e.unit)} · {e.who} · {when(e.at)}</span></div>
      {e.details && <p>{e.details}</p>}
      {e.files?.length ? <small className="muted">{e.files.join(" · ")}</small> : null}
    </li>)}</ol>}
  </>;
}
