import { createContext, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { api } from "./api";
import type { Project, ProjectSummary, Job, Health, Operation } from "./types";
import type { ProductionMode } from "./animationTypes";

export type Page =
  | "projects"
  | "idea"
  | "facts"
  | "story"
  | "script"
  | "generation"
  | "motion"
  | "editing"
  | "export"
  | "sources"
  | "library"
  | "jobs"
  | "production"
  | "paper-theatre"
  | "bank"
  | "bank-media"
  | "templates"
  | "workspace-settings"
  | "idea-pool"
  | "cast"
  | "locations"
  | "scenes"
  | "storyboard"
  | "props"
  | "sounds";
type Context = {
  project: Project | null;
  projects: ProjectSummary[];
  jobs: Job[];
  health: Health | null;
  page: Page;
  setPage: (p: Page) => void;
  loading: boolean;
  saving: boolean;
  saveError: boolean;
  notice: { text: string; error: boolean } | null;
  notify: (s: string, error?: boolean) => void;
  load: (id: string) => Promise<void>;
  accept: (p: Project) => void;
  reload: () => Promise<void>;
  reloadList: () => Promise<void>;
  patch: (
    changes: Partial<Project> | ((p: Project) => Partial<Project>),
  ) => Promise<Project>;
  edit: (
    operations: Operation[],
    origin?: string,
    revision?: number,
  ) => Promise<Project>;
  mutate: (fn: (p: Project) => Promise<Project>) => Promise<Project>;
  run: (task: () => Promise<unknown>) => void;
  targetInsert: string | null;
  setTargetInsert: (id: string | null) => void;
  targetScene: string | null;
  setTargetScene: (id: string | null) => void;
  settingsOpen: boolean;
  setSettingsOpen: (b: boolean) => void;
  searchInitial: string;
  setSearchInitial: (s: string) => void;
  mode: ProductionMode;
  setMode: (m: ProductionMode) => void;
  close: () => void;
};
const StudioContext = createContext<Context | null>(null);
export const useStudio = () => {
  const value = useContext(StudioContext);
  if (!value) throw new Error("Brak kontekstu Studio");
  return value;
};

export function StudioProvider({ children }: { children: ReactNode }) {
  const [project, setProject] = useState<Project | null>(null),
    [projects, setProjects] = useState<ProjectSummary[]>([]),
    [jobs, setJobs] = useState<Job[]>([]),
    [health, setHealth] = useState<Health | null>(null),
    [page, setPage] = useState<Page>("generation"),
    [loading, setLoading] = useState(true),
    [saving, setSaving] = useState(false),
    [saveError, setSaveError] = useState(false),
    [notice, setNotice] = useState<Context["notice"]>(null),
    [targetInsert, setTargetInsert] = useState<string | null>(null),
    [targetScene, setTargetScene] = useState<string | null>(null),
    [settingsOpen, setSettingsOpen] = useState(false),
    [searchInitial, setSearchInitial] = useState(""),
    [mode, setModeState] = useState<ProductionMode>(
      (localStorage.getItem("docos-mode") as ProductionMode) || "documentary",
    );
  function close() {
    ref.current = null;
    setProject(null);
    localStorage.removeItem("docos:last-project");
  }
  function setMode(next: ProductionMode) {
    setModeState(next);
    localStorage.setItem("docos-mode", next);
  }
  const ref = useRef<Project | null>(null),
    queue = useRef<Promise<unknown>>(Promise.resolve()),
    noticeTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  function notify(text: string, error = false) {
    setNotice({ text, error });
    clearTimeout(noticeTimer.current);
    noticeTimer.current = setTimeout(
      () => setNotice(null),
      error ? 12000 : 5000,
    );
  }
  function accept(p: Project) {
    if (
      ref.current &&
      (ref.current.id !== p.id || ref.current.revision > p.revision)
    )
      return;
    if (ref.current?.id !== p.id && p.production_mode) setMode(p.production_mode);
    ref.current = p;
    setProject(p);
    localStorage.setItem("docos:last-project", p.id);
  }
  async function reloadList() {
    setProjects(await api<ProjectSummary[]>("/projects"));
  }
  async function load(id: string) {
    await queue.current;
    setLoading(true);
    try {
      const p = await api<Project>("/projects/" + id);
      ref.current = null;
      accept(p);
      const remembered = localStorage.getItem("docos:page:" + id);
      const pages: Page[] = [
        "idea",
        "facts",
        "story",
        "script",
        "generation",
        "motion",
        "editing",
        "export",
        "sources",
        "library",
        "jobs",
        "production",
        "paper-theatre",
        "bank",
        "bank-media",
        "templates",
        "workspace-settings",
        "idea-pool",
        "cast",
        "locations",
        "scenes",
        "storyboard",
        "props",
        "sounds",
      ];
      setPage(
        pages.includes(remembered as Page)
          ? (remembered as Page)
          : p.production_mode === "animation_2d"
            ? "scenes"
            : "generation",
      );
    } finally {
      setLoading(false);
    }
  }
  async function reload() {
    await queue.current;
    const pid = ref.current?.id;
    if (pid) accept(await api<Project>("/projects/" + pid));
    setHealth(await api<Health>("/health"));
    await reloadList();
  }
  // Claude and other windows edit the same film through the API: pick up newer revisions.
  useEffect(() => {
    const timer = setInterval(() => {
      const current = ref.current;
      if (!current || document.hidden) return;
      queue.current = queue.current.then(async () => {
        try {
          const list = await api<ProjectSummary[]>("/projects");
          const row = list.find((x) => x.id === current.id);
          if (row && ref.current?.id === current.id && row.revision > ref.current.revision) {
            accept(await api<Project>("/projects/" + current.id));
            notify("Film zaktualizowany — wczytano najnowsze zmiany");
          }
          setProjects(list);
        } catch {
          /* offline: the next tick retries */
        }
      });
    }, 4000);
    return () => clearInterval(timer);
  }, []);
  function mutate(fn: (p: Project) => Promise<Project>): Promise<Project> {
    const task = queue.current.then(async () => {
      if (!ref.current) throw new Error("Wybierz projekt");
      setSaving(true);
      try {
        const next = await fn(ref.current);
        accept(next);
        setSaveError(false);
        return next;
      } catch (error) {
        setSaveError(true);
        if ((error as { status?: number }).status === 409 && ref.current)
          accept(await api<Project>("/projects/" + ref.current.id));
        throw error;
      } finally {
        setSaving(false);
      }
    });
    queue.current = task.catch(() => undefined);
    return task;
  }
  const patch = (
    changes: Partial<Project> | ((p: Project) => Partial<Project>),
  ) =>
    mutate((p) =>
      api<Project>(
        "/projects/" + p.id,
        {
          expected_revision: p.revision,
          changes: typeof changes === "function" ? changes(p) : changes,
        },
        "PATCH",
      ),
    );
  const edit = (
    operations: Operation[],
    origin = "manual",
    revision?: number,
  ) =>
    mutate((p) =>
      api<Project>("/projects/" + p.id + "/edits", {
        expected_revision: revision ?? p.revision,
        operations,
        origin,
      }),
    );
  function run(task: () => Promise<unknown>) {
    task().catch((e) =>
      notify(e instanceof Error ? e.message : String(e), true),
    );
  }
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const [list, status] = await Promise.all([
          api<ProjectSummary[]>("/projects"),
          api<Health>("/health"),
        ]);
        if (!active) return;
        setProjects(list);
        setHealth(status);
        const requested = new URLSearchParams(window.location.search);
        const last = localStorage.getItem("docos:last-project");
        const chosen =
          list.find((x) => x.id === requested.get("project"))?.id ||
          list.find((x) => x.id === last)?.id ||
          list.find((x) => (x.production_mode || "documentary") === mode)?.id;
        if (chosen) {
          const p = await api<Project>("/projects/" + chosen);
          if (active) accept(p);
          const remembered =
            requested.get("page") || localStorage.getItem("docos:page:" + p.id);
          if (active && remembered) setPage(remembered as Page);
        } else setPage((requested.get("page") as Page) || "projects");
      } catch (error) {
        if (active)
          notify(
            error instanceof Error
              ? error.message
              : "Nie można połączyć ze studiem",
            true,
          );
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    if (project) {
      localStorage.setItem("docos:page:" + project.id, page);
      window.history.replaceState(
        null,
        "",
        `?project=${encodeURIComponent(project.id)}&page=${encodeURIComponent(page)}`,
      );
    } else if (!loading)
      window.history.replaceState(null, "", `?page=${encodeURIComponent(page)}`);
  }, [page, project?.id, loading]);
  useEffect(() => {
    let previous: string | null = null;
    const events = new EventSource("/api/events");
    events.addEventListener("jobs", (event) => {
      const next = JSON.parse((event as MessageEvent).data) as Job[];
      setJobs(next);
      const completed = next
        .filter((j) => j.status === "SUCCEEDED")
        .map((j) => j.id)
        .join(",");
      if (previous !== null && completed !== previous) run(reload);
      previous = completed;
    });
    const timer = setInterval(() => {
      if (events.readyState === EventSource.CLOSED)
        run(async () => setJobs(await api<Job[]>("/jobs")));
    }, 5000);
    return () => {
      events.close();
      clearInterval(timer);
    };
  }, []);
  return (
    <StudioContext.Provider
      value={{
        mode,
        setMode,
        close,
        project,
        projects,
        jobs,
        health,
        page,
        setPage,
        loading,
        saving,
        saveError,
        notice,
        notify,
        load,
        accept,
        reload,
        reloadList,
        patch,
        edit,
        mutate,
        run,
        targetInsert,
        setTargetInsert,
        targetScene,
        setTargetScene,
        settingsOpen,
        setSettingsOpen,
        searchInitial,
        setSearchInitial,
      }}
    >
      {children}
    </StudioContext.Provider>
  );
}
