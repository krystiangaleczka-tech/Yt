import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  Download,
  Check,
  AlertCircle,
  Film,
  Clock3,
  Play,
  X,
  LoaderCircle,
  FileJson,
  FileText,
  ChevronRight,
  RotateCcw,
} from "lucide-react";
import { useStudio } from "./context";
import { api, saveText } from "./api";
import { Button, Empty, Field, Modal, SectionHead } from "./components";
import type { Issue, Job } from "./types";
import { fps, time, totalFrames } from "./timing";

const states: Record<string, string> = {
  QUEUED: "W kolejce",
  RUNNING: "W toku",
  SUCCEEDED: "Gotowe",
  FAILED: "Błąd",
  CANCELLED: "Anulowano",
  CANCEL_REQUESTED: "Anulowanie",
  INTERRUPTED: "Przerwano",
};
const kinds: Record<string, string> = {
  render: "Eksport filmu",
  preview: "Dokładny podgląd",
  image: "Generowanie obrazu",
  voice: "Generowanie lektora",
};
export function JobList({ all = false }: { all?: boolean }) {
  const s = useStudio();
  const [preview, setPreview] = useState<Job | null>(null);
  const jobs = s.jobs.filter((j) => all || j.project_id === s.project?.id);
  if (!jobs.length)
    return (
      <Empty icon={Film} title="Tu pojawią się Twoje zadania">
        Generowanie i eksport działają w tle. Możesz dalej pracować nad filmem.
      </Empty>
    );
  return (
    <>
      <div className="jobs-list">
        {jobs.map((job) => (
          <article
            className={`job-card surface ${job.status.toLowerCase()}`}
            key={job.id}
          >
            <div className="job-icon">
              {job.status === "RUNNING" || job.status === "QUEUED" ? (
                <LoaderCircle className="spin" size={21} />
              ) : job.status === "SUCCEEDED" ? (
                <Check size={21} />
              ) : (
                <Film size={21} />
              )}
            </div>
            <div className="job-description">
              <div className="inline-heading">
                <h3>{kinds[job.kind] || job.kind}</h3>
                <span
                  className={
                    "badge " +
                    (job.status === "SUCCEEDED"
                      ? "success"
                      : job.status === "FAILED"
                        ? "warning"
                        : "quiet")
                  }
                >
                  {states[job.status] || job.status}
                </span>
              </div>
              <p>{job.message}</p>
              <span className="small muted">
                Rewizja {job.revision} ·{" "}
                {new Date(job.created_at).toLocaleString("pl-PL")}
              </span>
              {["RUNNING", "QUEUED", "CANCEL_REQUESTED"].includes(
                job.status,
              ) && (
                <div
                  className="job-progress"
                  role="progressbar"
                  aria-label="Postęp zadania"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(job.progress * 100)}
                >
                  <div
                    style={{ width: Math.max(3, job.progress * 100) + "%" }}
                  />
                </div>
              )}
            </div>
            <div className="job-actions">
              {job.result?.url && job.status === "SUCCEEDED" && (
                <>
                  <Button icon={Play} onClick={() => setPreview(job)}>
                    Otwórz
                  </Button>
                  <a
                    href={job.result.url}
                    download={(s.project?.title || "film") + ".mp4"}
                    className="icon-button"
                    aria-label="Pobierz MP4"
                  >
                    <Download size={17} />
                  </a>
                </>
              )}
              {["RUNNING", "QUEUED"].includes(job.status) && (
                <Button
                  subtle
                  icon={X}
                  onClick={() =>
                    s.run(async () => {
                      await api("/jobs/" + job.id + "/cancel", {});
                      s.notify("Zlecono anulowanie");
                    })
                  }
                >
                  Anuluj
                </Button>
              )}
            </div>
          </article>
        ))}
      </div>
      <Modal
        open={!!preview}
        onClose={() => setPreview(null)}
        title={preview?.kind === "preview" ? "Dokładny podgląd" : "Gotowy film"}
        description={"Wynik dla rewizji " + preview?.revision}
        wide
      >
        {preview?.result?.url && (
          <video
            className="full-preview"
            controls
            autoPlay
            src={preview.result.url}
          />
        )}
      </Modal>
    </>
  );
}

export function Exports() {
  const s = useStudio(),
    p = s.project!;
  const [issues, setIssues] = useState<Issue[]>([]),
    [checked, setChecked] = useState(false),
    [quality, setQuality] = useState("full"),
    [mode, setMode] = useState("draft"),
    [busy, setBusy] = useState(false);
  async function check() {
    const result = await api<{ issues: Issue[] }>(
      "/projects/" + p.id + "/check",
    );
    setIssues(result.issues);
    setChecked(true);
  }
  useEffect(() => {
    s.run(check);
  }, [p.revision]);
  async function render() {
    setBusy(true);
    try {
      await api<Job>("/projects/" + p.id + "/render", {
        expected_revision: p.revision,
        quality: quality === "preview" ? "preview" : "full",
        mode,
      });
      s.notify("Rozpoczęto przygotowanie filmu");
    } finally {
      setBusy(false);
    }
  }
  const hasRunning = s.jobs.some(
    (j) =>
      j.project_id === p.id &&
      ["RUNNING", "QUEUED"].includes(j.status) &&
      ["render", "preview"].includes(j.kind),
  );
  return (
    <div className="page-content export-page">
      <SectionHead
        eyebrow="07 / GOTOWY FILM"
        title="Twoja historia jest blisko finału."
        description="Sprawdź materiały i przygotuj plik do obejrzenia lub publikacji."
      >
        <a
          className="button"
          href={"/api/projects/" + p.id + "/download"}
          download="project.json"
        >
          <FileJson size={16} />
          Projekt JSON
        </a>
        <a
          className="button"
          href={"/api/projects/" + p.id + "/bundle"}
          download="docos-project.zip"
        >
          <Download size={16} />
          Projekt z mediami
        </a>
      </SectionHead>
      <div className="export-grid">
        <section className="surface export-settings">
          <div className="export-symbol">
            <ArrowUpRight size={30} />
          </div>
          <h2>Eksport MP4</h2>
          <p className="muted small">H.264 · audio AAC, jeśli jest na osi</p>
          <Field label="Format obrazu">
            <select
              value={p.sequence.width + "x" + p.sequence.height}
              onChange={(e) => {
                const [w, h] = e.target.value.split("x").map(Number);
                s.run(() =>
                  s.edit([
                    { type: "set_sequence", changes: { width: w, height: h } },
                  ]),
                );
              }}
            >
              <option value="1280x720">Poziomy · 1280 × 720</option>
              <option value="1920x1080">Poziomy · 1920 × 1080</option>
              <option value="1080x1920">Pionowy · 1080 × 1920</option>
              {!["1280x720", "1920x1080", "1080x1920"].includes(
                p.sequence.width + "x" + p.sequence.height,
              ) && (
                <option value={p.sequence.width + "x" + p.sequence.height}>
                  Własny · {p.sequence.width} × {p.sequence.height}
                </option>
              )}
            </select>
          </Field>
          <Field label="Jakość">
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
            >
              <option value="full">Pełny rozmiar sekwencji</option>
              <option value="preview">
                Lekki podgląd · szerokość do 640 px
              </option>
            </select>
          </Field>
          <Field label="Wersja">
            <select value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="draft">Robocza · dopuszcza uwagi</option>
              <option value="final">
                Publikacyjna · wymaga pełnej kontroli
              </option>
            </select>
          </Field>
          <div className="export-summary">
            <span>
              <Clock3 size={15} />
              {time(totalFrames(p), fps(p))}
            </span>
            <span>{p.sequence.clips.length} klipów</span>
            <span>{fps(p)} fps</span>
          </div>
          <Button
            primary
            className="full-width"
            icon={ArrowUpRight}
            busy={busy}
            disabled={
              !p.sequence.clips.length ||
              hasRunning ||
              (mode === "final" && issues.length > 0)
            }
            onClick={() => s.run(render)}
          >
            {hasRunning ? "Film jest w kolejce" : "Przygotuj film"}
          </Button>
          <p className="small muted">
            Render zachowuje migawkę projektu. Późniejsze poprawki nie zmienią
            trwającego zadania.
          </p>
        </section>
        <section className="surface export-checks">
          <div className="panel-heading">
            <h2>Przed eksportem</h2>
            <Button subtle icon={RotateCcw} onClick={() => s.run(check)}>
              Sprawdź
            </Button>
          </div>
          {checked && !issues.length ? (
            <div className="all-clear">
              <Check size={29} />
              <h3>Kontrola projektu bez uwag</h3>
              <p>Sprawdź jeszcze film i poprawność źródeł przed publikacją.</p>
            </div>
          ) : (
            <div className="check-list">
              {issues.map((issue, index) => (
                <button
                  key={index}
                  className={"check-item " + issue.severity}
                  onClick={() => {
                    if (issue.scene_id) s.setTargetScene(issue.scene_id);
                    s.setPage(
                      issue.type === "story"
                        ? "story"
                        : ["media", "voice", "file"].includes(issue.type)
                          ? "generation"
                          : "library",
                    );
                  }}
                >
                  <AlertCircle size={17} />
                  <span>{issue.message}</span>
                  <ChevronRight size={16} />
                </button>
              ))}
            </div>
          )}
          <div className="export-note">
            <FileText size={18} />
            <p>
              Eksport roboczy może nie zawierać nagrania lektora. Brakujące
              elementy pozostają widoczne na liście.
            </p>
          </div>
        </section>
      </div>
      <div className="inline-heading section-divider">
        <h2>Przygotowane pliki i zadania</h2>
        <div className="player-spacer" />
        <Button
          subtle
          icon={Download}
          onClick={() =>
            saveText(
              "narracja.txt",
              p.scenes
                .map((sc) => sc.narration)
                .filter(Boolean)
                .join(" "),
            )
          }
        >
          Narracja TXT
        </Button>
      </div>
      <JobList />
    </div>
  );
}
