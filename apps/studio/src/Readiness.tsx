import { useEffect, useState } from "react";
import { BookOpen, Check, CircleAlert, CircleCheck, CircleDashed, Copy, Info, RefreshCw, TimerReset, TriangleAlert } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import { Button, SectionHead } from "./components";
import type { Project } from "./types";
import "./FilmFlow.css";
import "./Continuity.css";
import "./Readiness.css";

type State = "gotowe" | "brak" | "do przeliczenia" | "uwagi" | "informacja" | "nie dotyczy";
type Shot = { nr: number; sceneId: string; title: string; narration: string };
type Decision = { decision: "zatwierdzona" | "do poprawy"; quote: string; at: string; who: string; source: "wpis" | "opis" };
type Item = {
  key: string; title: string; state: State; summary: string; todo: string; command: string; chapter: string; track?: string;
  shots?: Shot[]; units?: { unit: number; actId: string; title: string; review: string }[];
  totals?: Record<string, number>; issues?: { severity: number; rule: string; ref: string; message: string }[];
  coverage?: { start: number; end: number; film: number; clips: number } | null; decision?: Decision | null;
};
type Readiness = { ready: boolean; blocking: string[]; items: Item[]; script: string; film: { seconds: number; shots: number; revision: number } };

const LOOK: Record<State, { icon: LucideIcon; label: string }> = {
  gotowe: { icon: CircleCheck, label: "gotowe" },
  brak: { icon: CircleAlert, label: "brak" },
  "do przeliczenia": { icon: TimerReset, label: "do przeliczenia" },
  uwagi: { icon: TriangleAlert, label: "uwagi" },
  informacja: { icon: Info, label: "informacja" },
  "nie dotyczy": { icon: CircleDashed, label: "nie dotyczy" },
};
const CHAPTERS: Record<string, string> = {
  lektor: "Lektor", dzwiek: "Dźwięk", recenzja: "Recenzja jednostki", sekwencja: "Sekwencja, świat i ciągłość", praca: "Jak pracujemy",
};
const REVIEW_CLASS: Record<string, string> = { zatwierdzona: "ok", nieaktualna: "warn", "do poprawy": "warn" };
const tc = (seconds: number) => `${Math.floor(seconds / 60)}:${(seconds % 60).toFixed(1).padStart(4, "0").replace(".", ",")}`;

/** Gotowość filmu: kroki po Ujęciach i Montażu (lektor, dźwięk, zgoda na próbkę, recenzje, ciągłość), liczone z projektu. */
export default function ReadinessView() {
  const s = useStudio();
  const p = s.project!;
  const [data, setData] = useState<Readiness | null>(null);
  const [busy, setBusy] = useState(false);
  async function refresh() {
    setBusy(true);
    try { setData(await api<Readiness>(`/projects/${p.id}/gotowosc`)); }
    catch (e) { s.notify(String((e as Error).message), true); }
    finally { setBusy(false); }
  }
  useEffect(() => { void refresh(); }, [p.id, p.revision]);
  function openChapter(key: string) {
    sessionStorage.setItem("docos:handbook-chapter", key);
    s.setPage("handbook");
  }
  return <div className="page-content flow-page">
    <SectionHead eyebrow="PRZED RENDEREM KOŃCOWYM" title="Gotowość filmu"
      description="Czego filmowi brakuje do oddania: lektor, zgoda na próbkę dźwięku, muzyka, efekty, recenzje i ciągłość. Stan liczy się sam z projektu — nic się tu nie odhacza ręcznie, poza zgodą reżysera na próbkę.">
      <Button icon={RefreshCw} disabled={busy} onClick={refresh}>{busy ? "Sprawdzam…" : "Sprawdź jeszcze raz"}</Button>
    </SectionHead>
    {!data ? <div className="flow-empty">Sprawdzam film…</div> : <>
      <section className={`flow-card rd-head ${data.ready ? "ready" : "todo"}`}>
        {data.ready ? <CircleCheck size={26} /> : <CircleAlert size={26} />}
        <div>
          <h3>{data.ready ? "Film gotowy do renderu końcowego" : `Do oddania brakuje: ${data.blocking.join(", ")}`}</h3>
          <p className="muted">{tc(data.film.seconds)} · {data.film.shots} ujęć{data.script ? <> · skrypt filmu <code>{data.script}</code></> : null}</p>
        </div>
      </section>
      <ol className="rd-list">{data.items.map(item => <Row key={item.key} item={item} onChapter={openChapter} />)}</ol>
    </>}
  </div>;
}

function Row({ item, onChapter }: { item: Item; onChapter: (key: string) => void }) {
  const s = useStudio();
  const look = LOOK[item.state] || LOOK.informacja;
  const Icon = look.icon;
  const [open, setOpen] = useState(false);
  const shots = item.shots || [];
  async function copy(text: string) {
    try { await navigator.clipboard.writeText(text); s.notify("Skopiowano polecenie"); }
    catch { s.notify("Nie udało się skopiować — zaznacz polecenie ręcznie", true); }
  }
  function goShot(id: string) {
    s.setTargetScene(id);
    s.setPage("generation");
  }
  return <li className={`flow-card rd-row rd-${item.state.replace(/ /g, "-")}`}>
    <div className="rd-state"><Icon size={18} /><span>{look.label}</span></div>
    <div className="rd-body">
      <div className="rd-title"><h3>{item.title}</h3>{item.track && <span className="cont-badge idle">ścieżka {item.track}</span>}</div>
      <p>{item.summary}</p>
      {item.coverage && <Coverage c={item.coverage} />}
      {item.units && item.units.length > 0 && <div className="rd-chips">{item.units.map(u =>
        <span key={u.actId} className={`cont-status ${REVIEW_CLASS[u.review] || "idle"}`} title={u.title}>{u.title || `jednostka ${u.unit}`}: {u.review}</span>)}</div>}
      {item.issues && item.issues.length > 0 && item.state !== "gotowe" && <ul className="cont-issues rd-issues">{item.issues.map((i, k) =>
        <li key={k}><span className={`cont-badge w${i.severity}`}>{i.severity}</span><span className="cont-rule">{i.rule}</span>
          <code className={i.ref ? "" : "cont-noref"}>{i.ref || "—"}</code><span>{i.message}</span></li>)}</ul>}
      {shots.length > 0 && <div className="rd-shots">
        <button className="rd-more" onClick={() => setOpen(!open)}>{open ? "Zwiń listę ujęć" : `Pokaż ujęcia (${shots.length})`}</button>
        {open && <ul>{shots.map(x => <li key={x.sceneId}>
          <button className="rd-shot" onClick={() => goShot(x.sceneId)} title="Otwórz ujęcie w zakładce Ujęcia"
            aria-label={`Ujęcie ${x.nr}: ${x.title} — otwórz w zakładce Ujęcia`}>{x.nr} · {x.title}</button>
          {x.narration && <span className="muted"> — „{x.narration}”</span>}</li>)}</ul>}
      </div>}
      {item.key === "probka" && <SampleForm item={item} />}
      {(item.todo || item.command) && <div className="rd-todo">
        {item.todo && <p><strong>{item.state === "informacja" ? "Kto: " : "Co zrobić: "}</strong>{item.todo}</p>}
        {item.command && <div className="rd-command"><code>{item.command}</code>
          <button onClick={() => copy(item.command)} aria-label="Kopiuj polecenie" title="Kopiuj polecenie"><Copy size={14} /></button></div>}
      </div>}
      <div className="rd-links">
        <button onClick={() => onChapter(item.chapter)}><BookOpen size={13} /> Podręcznik: {CHAPTERS[item.chapter] || item.chapter}</button>
        {(item.key === "recenzje" || item.key === "ciaglosc") && <button onClick={() => s.setPage("continuity")}>Otwórz Continuity Editor</button>}
        {(item.key === "muzyka" || item.key === "efekty" || item.key === "lektor") && <button onClick={() => s.setPage("editing")}>Otwórz Montaż</button>}
      </div>
    </div>
  </li>;
}

function Coverage({ c }: { c: { start: number; end: number; film: number } }) {
  const span = Math.max(c.film, c.end, 0.001);
  const left = (100 * c.start) / span, width = (100 * (Math.min(c.end, span) - c.start)) / span, film = (100 * c.film) / span;
  return <div className="rd-cover" aria-label={`Dźwięk od ${tc(c.start)} do ${tc(c.end)}, film ${tc(c.film)}`}>
    <div className="rd-cover-bar">
      <div className="rd-cover-film" style={{ width: `${film}%` }} />
      <div className="rd-cover-sound" style={{ left: `${left}%`, width: `${Math.max(0, width)}%` }} />
    </div>
    <span className="rd-cover-label">dźwięk {tc(c.start)}–{tc(c.end)} · film {tc(c.film)}</span>
  </div>;
}

function SampleForm({ item }: { item: Item }) {
  const s = useStudio();
  const p = s.project!;
  const [open, setOpen] = useState(false);
  const [quote, setQuote] = useState("");
  const [sample, setSample] = useState("");
  const [who, setWho] = useState("reżyser");
  function save(decision: "zatwierdzona" | "do poprawy") {
    s.run(async () => {
      await s.mutate(async (current: Project) => api<Project>(`/projects/${p.id}/gotowosc/probka`,
        { decision, quote, sample, who, expected_revision: current.revision }));
      setQuote(""); setSample(""); setOpen(false);
      s.notify(decision === "zatwierdzona" ? "Zgoda na próbkę zapisana w dzienniku" : "Uwagi do próbki zapisane w dzienniku");
    });
  }
  if (!open) return <div className="flow-actions"><Button icon={Check} primary={item.state !== "gotowe"} onClick={() => setOpen(true)}>
    {item.state === "gotowe" ? "Zapisz nową decyzję o próbce" : "Zgoda reżysera na próbkę"}</Button></div>;
  return <div className="rd-sample">
    <label className="cont-field">Słowa reżysera (cytat z rozmowy)
      <textarea rows={2} value={quote} placeholder="np. Zatwierdzam, wgraj" onChange={e => setQuote(e.target.value)} /></label>
    <div className="rd-sample-row">
      <label className="cont-field">Próbka (plik albo katalog)<input value={sample} placeholder="np. build/probka_dzwieku" onChange={e => setSample(e.target.value)} /></label>
      <label className="cont-field">Kto<input value={who} onChange={e => setWho(e.target.value)} /></label>
    </div>
    <div className="flow-actions">
      <Button primary icon={Check} disabled={!quote.trim()} onClick={() => save("zatwierdzona")}>Próbka zatwierdzona</Button>
      <Button icon={TriangleAlert} disabled={!quote.trim()} onClick={() => save("do poprawy")}>Próbka do poprawy</Button>
      <Button onClick={() => setOpen(false)}>Anuluj</Button>
    </div>
    <small className="muted">Decyzja trafia do dziennika pracy jako wpis „próbka dźwięku” z cytatem. Wpisów się nie kasuje — nowa decyzja zastępuje poprzednią.</small>
  </div>;
}
