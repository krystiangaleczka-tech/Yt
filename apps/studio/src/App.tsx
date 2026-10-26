import { lazy, Suspense, useState } from "react";
import {
  Aperture,
  FolderOpen,
  Plus,
  Compass,
  BookOpen,
  GitBranch,
  FileText,
  Clapperboard,
  SlidersHorizontal,
  ArrowUpRight,
  Library,
  Layers3,
  Settings2,
  PanelLeftClose,
  PanelLeftOpen,
  Check,
  LoaderCircle,
  Film,
  Search,
  ArrowRight,
  Upload,
  Menu,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { StudioProvider, useStudio } from "./context";
import type { Page } from "./context";
import { api, upload } from "./api";
import type { Project } from "./types";
import { Button, Modal, Field, SectionHead, Empty } from "./components";
import Generation from "./Generation";
import Sources from "./Sources";
import Timeline from "./Timeline";
import { Idea, Facts, Story, Script } from "./Editorial";
import { Exports, JobList } from "./Exports";
import Settings from "./Settings";
import LibraryView from "./Library";

const MotionEditor = lazy(() => import("./MotionEditor"));

const steps: { id: Page; label: string; icon: LucideIcon }[] = [
  { id: "idea", label: "Pomysł", icon: Compass },
  { id: "facts", label: "Fakty i research", icon: BookOpen },
  { id: "story", label: "Historia", icon: GitBranch },
  { id: "script", label: "Scenariusz", icon: FileText },
  { id: "generation", label: "Generowanie", icon: Clapperboard },
  { id: "editing", label: "Montaż", icon: SlidersHorizontal },
  { id: "export", label: "Eksport", icon: ArrowUpRight },
];
function Shell() {
  const s = useStudio();
  const [collapsed, setCollapsed] = useState(false),
    [mobileNav, setMobileNav] = useState(false),
    [newOpen, setNewOpen] = useState(false),
    [title, setTitle] = useState(""),
    [language, setLanguage] = useState("pl");
  const step = steps.find((x) => x.id === s.page);
  const running = s.jobs.filter((j) =>
    ["RUNNING", "QUEUED", "CANCEL_REQUESTED"].includes(j.status),
  ).length;
  const navigate = (page: Page) => {
    s.setPage(page);
    setMobileNav(false);
  };
  async function create() {
    const p = await api<Project>("/projects", { title, language });
    await s.load(p.id);
    await s.reloadList();
    s.setPage("idea");
    setNewOpen(false);
    setTitle("");
    s.notify("Utworzono nowy film");
  }
  const content =
    s.page === "projects" ? (
      <Projects onNew={() => setNewOpen(true)} />
    ) : !s.project ? (
      <Empty
        title="Utwórz pierwszy film"
        action={
          <Button primary icon={Plus} onClick={() => setNewOpen(true)}>
            Nowy film
          </Button>
        }
      />
    ) : s.page === "generation" ? (
      <Generation />
    ) : s.page === "motion" ? (
      <Suspense
        fallback={<div className="page-content">Ładowanie wstawek…</div>}
      >
        <MotionEditor />
      </Suspense>
    ) : s.page === "editing" ? (
      <Timeline />
    ) : s.page === "sources" ? (
      <Sources />
    ) : s.page === "library" ? (
      <LibraryView />
    ) : s.page === "facts" ? (
      <Facts />
    ) : s.page === "story" ? (
      <Story />
    ) : s.page === "script" ? (
      <Script />
    ) : s.page === "idea" ? (
      <Idea />
    ) : s.page === "jobs" ? (
      <div className="page-content">
        <SectionHead
          title="Zadania"
          description="Generowanie i renderowanie w tle"
        />
        <JobList all />
      </div>
    ) : (
      <Exports />
    );
  return (
    <div
      className={`studio ${collapsed ? "sidebar-collapsed" : ""} ${mobileNav ? "mobile-nav-open" : ""}`}
    >
      {mobileNav && (
        <button
          className="nav-scrim"
          aria-label="Zamknij nawigację"
          onClick={() => setMobileNav(false)}
        />
      )}
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("projects");
          }}
        >
          <span className="brand-mark">
            <Aperture size={21} />
          </span>
          <span className="brand-name">
            DocOS<span>Studio</span>
          </span>
        </a>
        <Button
          icon={Plus}
          className="new-project"
          onClick={() => setNewOpen(true)}
        >
          Nowy film
        </Button>
        <button
          className={`nav-item ${s.page === "projects" ? "active" : ""}`}
          onClick={() => navigate("projects")}
          title="Projekty"
        >
          <FolderOpen size={18} />
          <span>Projekty</span>
        </button>
        <div className="nav-label">TWÓJ FILM</div>
        <nav aria-label="Etapy produkcji">
          {steps.map((item, index) => (
            <button
              key={item.id}
              className={`nav-item ${s.page === item.id ? "active" : ""}`}
              aria-current={s.page === item.id ? "page" : undefined}
              onClick={() => navigate(item.id)}
              title={item.label}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
              {!collapsed && (
                <small>{String(index + 1).padStart(2, "0")}</small>
              )}
            </button>
          ))}
        </nav>
        <button
          className={`nav-item ${s.page === "motion" ? "active" : ""}`}
          onClick={() => navigate("motion")}
          title="Wstawki animowane"
        >
          <Film size={18} />
          <span>Wstawki animowane</span>
        </button>
        <div className="nav-label resources-label">ZASOBY</div>
        <button
          className={`nav-item ${s.page === "sources" ? "active" : ""}`}
          onClick={() => navigate("sources")}
          title="Centrum źródeł"
        >
          <Search size={18} />
          <span>Centrum źródeł</span>
        </button>
        <button
          className={`nav-item ${s.page === "library" ? "active" : ""}`}
          onClick={() => navigate("library")}
          title="Biblioteka mediów"
        >
          <Library size={18} />
          <span>Biblioteka</span>
          {!collapsed && <small>{s.project?.assets.length || 0}</small>}
        </button>
        <button
          className={`nav-item ${s.page === "jobs" ? "active" : ""}`}
          onClick={() => navigate("jobs")}
          title="Zadania"
        >
          <Layers3 size={18} />
          <span>Zadania</span>
          {running > 0 && <span className="running-count">{running}</span>}
        </button>
        <div className="sidebar-bottom">
          <button
            className="nav-item"
            onClick={() => s.setSettingsOpen(true)}
            title="Ustawienia"
          >
            <Settings2 size={18} />
            <span>Ustawienia</span>
          </button>
          <div className="workspace-profile">
            <span className="avatar">
              <Film size={15} />
            </span>
            <div>
              <strong>Moje studio</strong>
              <span>Przestrzeń lokalna</span>
            </div>
            <button
              className="icon-button collapse-button"
              onClick={() => setCollapsed(!collapsed)}
              aria-label={collapsed ? "Rozwiń panel" : "Zwiń panel"}
            >
              {collapsed ? (
                <PanelLeftOpen size={16} />
              ) : (
                <PanelLeftClose size={16} />
              )}
            </button>
          </div>
        </div>
      </aside>
      <div className="app-area">
        <header className="app-header">
          <button
            className="icon-button mobile-menu"
            onClick={() => setMobileNav(!mobileNav)}
            aria-label="Otwórz nawigację"
          >
            <Menu size={20} />
          </button>
          <div className="breadcrumbs">
            <FolderOpen size={15} />
            <select
              aria-label="Otwarty projekt"
              value={s.project?.id || ""}
              onChange={(e) => s.run(() => s.load(e.target.value))}
            >
              {s.projects.length === 0 && (
                <option value="">Moje projekty</option>
              )}
              {s.projects.map((p) => (
                <option value={p.id} key={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
            <span>/</span>
            <strong>
              {step?.label ||
                {
                  sources: "Centrum źródeł",
                  projects: "Projekty",
                  library: "Biblioteka",
                  jobs: "Zadania",
                  motion: "Wstawki animowane",
                }[s.page as "sources"]}
            </strong>
          </div>
          <div className="header-right">
            <span className="save-state" aria-live="polite">
              {s.saving ? (
                <>
                  <LoaderCircle size={13} className="spin" />
                  Zapisywanie
                </>
              ) : (
                <>
                  <Check size={13} />
                  Zapisano
                </>
              )}
            </span>
            {s.project?.demo && (
              <span className="badge quiet">Projekt demo</span>
            )}
            <Button
              icon={ArrowUpRight}
              primary
              onClick={() => navigate("export")}
            >
              Eksportuj
            </Button>
          </div>
        </header>
        <main
          className={`main-content page-${s.page}`}
          key={s.project?.id || "none"}
        >
          {s.loading ? (
            <div className="loading">
              <LoaderCircle className="spin" size={28} />
              <span>Otwieram studio…</span>
            </div>
          ) : (
            content
          )}
        </main>
      </div>
      {s.notice && (
        <div
          className={`toast ${s.notice.error ? "error" : ""}`}
          role={s.notice.error ? "alert" : "status"}
        >
          {s.notice.error ? (
            <span className="error-dot" />
          ) : (
            <Check size={17} />
          )}
          <span>{s.notice.text}</span>
        </div>
      )}
      <Modal
        open={newOpen}
        onClose={() => setNewOpen(false)}
        title="Zacznij nową historię"
        description="Od pierwszego pytania do gotowego filmu."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            s.run(create);
          }}
        >
          <Field label="Tytuł roboczy">
            <input
              autoFocus
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="O czym będzie Twój film?"
              maxLength={200}
            />
          </Field>
          <Field label="Język narracji">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="pl">Polski</option>
              <option value="en">English</option>
            </select>
          </Field>
          <Button primary type="submit" icon={ArrowRight}>
            Utwórz projekt
          </Button>
        </form>
      </Modal>
      <Settings />
    </div>
  );
}
function Projects({ onNew }: { onNew: () => void }) {
  const s = useStudio();
  return (
    <div className="page-content">
      <SectionHead
        eyebrow="TWOJA PRACOWNIA"
        title="Każdy film zaczyna się od pytania."
        description="Wróć do swojej historii lub zacznij następną."
      >
        <label className="button">
          <Upload size={16} />
          Importuj projekt
          <input
            type="file"
            accept=".json,.zip"
            className="visually-hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file)
                s.run(async () => {
                  const p = await upload<Project>(
                    file.name.toLowerCase().endsWith(".zip")
                      ? "/projects/import-bundle"
                      : "/projects/import",
                    file,
                  );
                  await s.load(p.id);
                  await s.reloadList();
                  s.setPage("script");
                  s.notify(
                    file.name.toLowerCase().endsWith(".zip")
                      ? "Wczytano projekt z mediami"
                      : "Wczytano treść projektu. Media dodaj do biblioteki.",
                  );
                });
            }}
          />
        </label>
        <Button primary icon={Plus} onClick={onNew}>
          Nowy film
        </Button>
      </SectionHead>
      <div className="project-grid">
        {s.projects.map((p) => (
          <button
            className="project-card"
            key={p.id}
            onClick={() =>
              s.run(async () => {
                await s.load(p.id);
                s.setPage("generation");
              })
            }
          >
            <div className="project-cover">
              <Film size={42} />
              <span>{p.demo ? "PRZYKŁADOWA PRODUKCJA" : "TWÓJ DOKUMENT"}</span>
            </div>
            <div className="project-card-body">
              <h3>{p.title}</h3>
              <p>
                {p.scenes} ujęć <span>·</span> {p.assets} materiałów
              </p>
              <div className="project-meta">
                <span>
                  {new Date(p.updated_at).toLocaleDateString("pl-PL")}
                </span>
                <ArrowUpRight size={17} />
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
export default function App() {
  return (
    <StudioProvider>
      <Shell />
    </StudioProvider>
  );
}
