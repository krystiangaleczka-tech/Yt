import { useEffect, useState } from "react";
import { BookOpen, Save, Pencil } from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import { Button, SectionHead } from "./components";
import Markdown from "./Markdown";
import "./Continuity.css";

type Chapter = { key: string; title: string; path: string; text: string };

/** Podręcznik pracowni: zasady wspólne dla wszystkich filmów (pliki Markdown w docs/, edytowalne tutaj). */
export default function Handbook() {
  const s = useStudio();
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [active, setActive] = useState("praca");
  const [draft, setDraft] = useState<string | null>(null);
  useEffect(() => { api<{ chapters: Chapter[] }>("/handbook").then(r => setChapters(r.chapters)).catch(e => s.notify(String(e.message), true)); }, []);
  const chapter = chapters.find(c => c.key === active) || chapters[0];
  async function save() {
    if (!chapter || draft === null) return;
    try {
      const saved = await api<Chapter>(`/handbook/${chapter.key}`, { text: draft }, "PUT");
      setChapters(list => list.map(c => c.key === saved.key ? saved : c));
      setDraft(null);
      s.notify("Zapisano rozdział podręcznika");
    } catch (e) { s.notify(String((e as Error).message), true); }
  }
  return <div className="page-content">
    <SectionHead title="Podręcznik pracowni" description="Zasady wspólne dla każdego filmu: jak pracujemy, jak budować sekwencje i świat, rytm, kadr, animacja kodem, recenzje i dziennik." />
    <div className="handbook">
      <nav className="handbook-nav">{chapters.map(c => <button key={c.key} className={c.key === chapter?.key ? "active" : ""}
        onClick={() => { setActive(c.key); setDraft(null); }}><BookOpen size={15} /><span>{c.title}</span></button>)}</nav>
      {chapter && <article className="flow-card handbook-body">
        <div className="handbook-head"><small className="muted">{chapter.path}</small>
          {draft === null ? <Button icon={Pencil} onClick={() => setDraft(chapter.text)}>Edytuj</Button>
            : <span className="flow-actions"><Button primary icon={Save} onClick={save}>Zapisz</Button><Button onClick={() => setDraft(null)}>Anuluj</Button></span>}</div>
        {draft === null ? (chapter.text ? <Markdown text={chapter.text} /> : <p className="muted">Rozdział jest pusty.</p>)
          : <textarea className="cont-json" value={draft} onChange={e => setDraft(e.target.value)} />}
      </article>}
    </div>
  </div>;
}
