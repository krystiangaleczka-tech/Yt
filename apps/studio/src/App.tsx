import { lazy, Suspense, useEffect, useState } from "react";
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
  Upload,
  Menu,
  Users,
  MapPinned,
  LayoutGrid,
  PersonStanding,
  Video,
  Backpack,
  AudioLines,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { StudioProvider, useStudio } from "./context";
import type { Page } from "./context";
import { api, upload } from "./api";
import type { Project, ProjectSummary } from "./types";
import { Button, SectionHead, Empty } from "./components";
import Generation from "./Generation";
import Sources from "./Sources";
import Timeline from "./Timeline";
import { Idea, Facts, Story, Script } from "./Editorial";
import { Exports, JobList } from "./Exports";
import Settings from "./Settings";
import LibraryView from "./Library";
import Production from "./Production";
import PaperTheatre from "./PaperTheatre";
import { NewFilmModal } from "./Workspace";
import { flowFrom, isApproved } from "./flowTypes";
import type { FlowPage } from "./FilmFlow";
import { workspacePages, workspaceTitles } from "./workspaceTypes";
import { modeLabels } from "./animationTypes";
import type { ProductionMode } from "./animationTypes";

const MotionEditor = lazy(() => import("./MotionEditor"));
const FilmFlow = lazy(() => import("./FilmFlow"));
const WorkspaceView = lazy(() => import("./WorkspacePage"));
const CastBankView = lazy(() => import("./CastBank"));
const Scenes = lazy(() => import("./Scenes"));
const ShotEditor = lazy(() => import("./ShotEditor"));
const Storyboard = lazy(() => import("./Storyboard"));

const steps: { id: Page; label: string; icon: LucideIcon }[] = [
  { id: "bible", label: "Story Bible", icon: BookOpen },
  { id: "projects", label: "Projekt", icon: FolderOpen },
  { id: "idea", label: "Pomysł i tytuł", icon: Compass },
  { id: "master-story", label: "Master Story", icon: GitBranch },
  { id: "acts", label: "Akty", icon: Layers3 },
  { id: "sequences", label: "Sekwencje", icon: FileText },
  { id: "script-flow", label: "Scenariusz", icon: FileText },
  { id: "scene-plan", label: "Plan scen", icon: Clapperboard },
  { id: "scenes", label: "Sceny / Canvas", icon: LayoutGrid },
  { id: "generation", label: "Ujęcia", icon: Film },
  { id: "editing", label: "Montaż", icon: SlidersHorizontal },
  { id: "continuity", label: "Continuity Editor", icon: Check },
  { id: "export", label: "Eksport", icon: ArrowUpRight },
];
const modes: { id: ProductionMode; icon: LucideIcon }[] = [
  { id: "documentary", icon: FileText },
  { id: "animation_2d", icon: PersonStanding },
  { id: "broll", icon: Video },
];
function Shell() {
  const s = useStudio();
  const [collapsed, setCollapsed] = useState(false),
    [mobileNav, setMobileNav] = useState(false),
    [newOpen, setNewOpen] = useState(false);
  const modeSteps = steps;
  const filmFlow = s.project ? flowFrom(s.project) : null;
  const step = modeSteps.find((x) => x.id === (s.page === "shot-editor" ? "scenes" : s.page));
  function switchMode(next: ProductionMode) {
    if (next === s.mode) return;
    s.setMode(next);
    if (s.project && s.project.production_mode !== next) {
      // A film belongs to one mode; leave it so the next start opens the chosen mode.
      s.close();
      s.setPage("projects");
    }
    setMobileNav(false);
  }
  const [dirty, setDirty] = useState(false);
  useEffect(() => {
    const changed = (e: Event) => setDirty(Boolean((e as CustomEvent).detail));
    window.addEventListener("docos:dirty", changed);
    return () => window.removeEventListener("docos:dirty", changed);
  }, []);
  const [theme, setTheme] = useState(
    localStorage.getItem("docos-theme") || "dark",
  );
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("docos-theme", theme);
  }, [theme]);
  const running = s.jobs.filter((j) =>
    ["RUNNING", "QUEUED", "CANCEL_REQUESTED"].includes(j.status),
  ).length;
  const navigate = (page: Page) => {
    s.setPage(page);
    setMobileNav(false);
  };
  async function openCreated(p: Project) {
    await s.load(p.id);
    await s.reloadList();
    s.setPage("idea");
    s.notify("Utworzono osobny film");
  }
  const globalPage = (workspacePages as readonly string[]).includes(s.page);
  const content =
    s.page === "projects" ? (
      <Projects onNew={() => setNewOpen(true)} />
    ) : s.page === "cast" || s.page === "locations" || s.page === "props" || s.page === "sounds" ? (
      <Suspense fallback={<div className="page-content">Ładowanie banku…</div>}>
        <CastBankView section={s.page} />
      </Suspense>
    ) : globalPage ? (
      <Suspense
        fallback={<div className="page-content">Ładowanie pracowni…</div>}
      >
        <WorkspaceView section={s.page} />
      </Suspense>
    ) : !s.project ? (
      <Empty
        title="Utwórz pierwszy film"
        action={
          <Button primary icon={Plus} onClick={() => setNewOpen(true)}>
            Nowy film
          </Button>
        }
      />
    ) : (["bible", "master-story", "acts", "sequences", "script-flow", "scene-plan", "continuity"] as string[]).includes(s.page) ? (
      <Suspense fallback={<div className="page-content">Otwieram etap produkcji…</div>}>
        <FilmFlow page={s.page as FlowPage} />
      </Suspense>
    ) : s.page === "scenes" ? (
      <Suspense fallback={<div className="page-content">Ładowanie scen…</div>}>
        <Scenes key={s.project.id} />
      </Suspense>
    ) : s.page === "shot-editor" ? (
      <Suspense fallback={<div className="page-content">Ładowanie edytora ujęcia…</div>}>
        <ShotEditor />
      </Suspense>
    ) : s.page === "storyboard" ? (
      <Suspense fallback={<div className="page-content">Ładowanie storyboardu…</div>}>
        <Storyboard />
      </Suspense>
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
    ) : s.page === "production" ? (
      <Production />
    ) : s.page === "paper-theatre" ? (
      <div className="page-content production-page">
        <SectionHead eyebrow="ANIMACJA PAPIEROWA"
          title="Paper Theatre 2.5D"
          description="Oddzielne warstwy PNG, wejścia grupami i podnoszone figurki. Najważniejsza postać wchodzi ostatnia." />
        <PaperTheatre />
      </div>
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
        <div className="mode-switch" role="radiogroup" aria-label="Tryb produkcji">
          {modes.map((m) => (
            <button
              key={m.id}
              role="radio"
              aria-checked={s.mode === m.id}
              className={s.mode === m.id ? "active" : ""}
              title={`Tryb: ${modeLabels[m.id]}`}
              onClick={() => switchMode(m.id)}
            >
              <m.icon size={15} />
              <span>{modeLabels[m.id]}</span>
            </button>
          ))}
        </div>
        <Button
          icon={Plus}
          className="new-project"
          onClick={() => setNewOpen(true)}
        >
          Nowy film
        </Button>
        <div className="nav-label">PRODUKCJA FILMU</div>
        <nav aria-label="Etapy produkcji">
          {modeSteps.map((item, index) => (
            <button
              key={item.id}
              className={`nav-item ${s.page === item.id || (s.page === "shot-editor" && item.id === "scenes") ? "active" : ""}`}
              aria-current={s.page === item.id || (s.page === "shot-editor" && item.id === "scenes") ? "page" : undefined}
              onClick={() => navigate(item.id)}
              title={item.label}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
              {!collapsed && (
                <small>{item.id === "bible" ? "00" : String(index).padStart(2, "0")}{filmFlow && (item.id === "master-story" ? isApproved(filmFlow, "master") : item.id === "acts" ? isApproved(filmFlow, "acts") : item.id === "sequences" ? isApproved(filmFlow, "sequences") : item.id === "scene-plan" ? isApproved(filmFlow, "outlines") : false) ? " ✓" : ""}</small>
              )}
            </button>
          ))}
        </nav>
        <details className="flow-advanced">
          <summary>Narzędzia zaawansowane</summary>
          {s.mode === "animation_2d" && ([
            ["cast", "Postacie", Users],
            ["locations", "Lokacje", MapPinned],
            ["props", "Rekwizyty", Backpack],
            ["sounds", "Dźwięki", AudioLines],
          ] as const).map(([id, label, Icon]) => (
            <button key={id} className={`nav-item ${s.page === id ? "active" : ""}`} onClick={() => navigate(id)}>
              <Icon size={18} /><span>{label}</span>
            </button>
          ))}
          {workspacePages.map(page => (
            <button key={page} className={`nav-item ${s.page === page ? "active" : ""}`} onClick={() => navigate(page)}>
              <Library size={18} /><span>{workspaceTitles[page]}</span>
            </button>
          ))}
          {([
            ["facts", "Research", BookOpen],
            ["story", "Karta historii", GitBranch],
            ["script", "Klasyczny scenariusz", FileText],
            ["storyboard", "Storyboard", Clapperboard],
            ["motion", "Wstawki animowane", Film],
            ["paper-theatre", "Paper Theatre 2.5D", Layers3],
            ["sources", "Centrum źródeł", Search],
            ["library", "Materiały filmu", Library],
            ["jobs", "Zadania", Layers3],
          ] as const).map(([id, label, Icon]) => (
            <button key={id} className={`nav-item ${s.page === id ? "active" : ""}`} onClick={() => navigate(id)}>
              <Icon size={18} /><span>{label}</span>
            </button>
          ))}
        </details>
        <div className="sidebar-bottom">
          <button
            className={`nav-item ${s.page === "production" ? "active" : ""}`}
            title="Narzędzia produkcji"
            onClick={() => navigate("production")}
          >
            <SlidersHorizontal size={18} />
            <span>Narzędzia produkcji</span>
          </button>
          <button
            className="nav-item"
            title="Zmień motyw"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Aperture size={18} />
            <span>{theme === "dark" ? "Jasny motyw" : "Ciemny motyw"}</span>
          </button>
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
              {s.project && !s.projects.some((p) => p.id === s.project?.id) && (
                <option value={s.project.id}>
                  {s.project.title} · archiwum
                </option>
              )}
              {s.projects.map((p) => (
                <option value={p.id} key={p.id}>
                  {p.id === s.project?.id ? s.project.title : p.title}
                </option>
              ))}
            </select>
            <span>/</span>
            <strong>
              {step?.label ||
                {
                  ...workspaceTitles,
                  sources: "Centrum źródeł",
                  projects: "Projekty",
                  library: "Biblioteka",
                  jobs: "Zadania",
                  production: "Narzędzia produkcji",
                  motion: "Wstawki animowane",
                  cast: "Postacie",
                  locations: "Lokacje",
                  props: "Rekwizyty i kostiumy",
                  sounds: "Dźwięki i muzyka",
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
                  {s.saveError
                    ? "Błąd zapisu"
                    : dirty
                      ? "Oczekuje zapisu"
                      : "Zapisano"}
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
        {s.project && modeSteps.some(item => item.id === s.page) && (
          <div className="flow-progress-bar">
            <button disabled={modeSteps[0].id === s.page} onClick={() => navigate(modeSteps[Math.max(0, modeSteps.findIndex(x => x.id === s.page) - 1)].id)}>← Wstecz</button>
            <span>{modeSteps.findIndex(x => x.id === s.page)} / {modeSteps.length - 1} · {step?.label}</span>
            <button disabled={modeSteps[modeSteps.length - 1].id === s.page} onClick={() => navigate(modeSteps[Math.min(modeSteps.length - 1, modeSteps.findIndex(x => x.id === s.page) + 1)].id)}>Dalej →</button>
          </div>
        )}
        <main
          className={`main-content page-${s.page}`}
          key={`${s.project?.id || "none"}:${s.page}`}
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
      <NewFilmModal
        open={newOpen}
        close={() => setNewOpen(false)}
        onCreated={openCreated}
      />
      <Settings />
    </div>
  );
}
function Projects({ onNew }: { onNew: () => void }) {
  const s = useStudio();
  const [archived, setArchived] = useState(false),
    [projectList, setProjectList] = useState<ProjectSummary[]>(s.projects);
  useEffect(() => {
    if (archived)
      s.run(async () =>
        setProjectList(
          await api<ProjectSummary[]>("/projects?include_archived=true"),
        ),
      );
    else setProjectList(s.projects);
  }, [archived, s.projects]);
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
        {projectList.filter((p) => (p.production_mode || "documentary") === s.mode).length === 0 && (
          <p className="muted">
            Brak filmów w trybie {modeLabels[s.mode]}. Utwórz nowy film albo zmień tryb w lewym górnym rogu.
          </p>
        )}
        {projectList.filter((p) => (p.production_mode || "documentary") === s.mode).map((p) => (
          <button
            className="project-card"
            key={p.id}
            onClick={() =>
              s.run(async () => {
                await s.load(p.id);
              })
            }
          >
            <div className="project-cover">
              <Film size={42} />
              <span>
                {p.demo
                  ? "PRZYKŁADOWA PRODUKCJA"
                  : modeLabels[p.production_mode || "documentary"].toUpperCase()}
              </span>
            </div>
            <div className="project-card-body">
              <h3>{p.title}</h3>
              <p>
                {p.production_mode === "animation_2d"
                  ? `${p.stage_scenes || 0} scen`
                  : `${p.scenes} ujęć`}{" "}
                <span>·</span> {p.assets} materiałów
              </p>
              <p className="small muted">
                {p.archived ? "Archiwum · " : ""}
                {p.next_step}
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
      <label className="checkbox">
        <input
          type="checkbox"
          checked={archived}
          onChange={(e) => setArchived(e.target.checked)}
        />
        Pokaż archiwalne projekty
      </label>
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
