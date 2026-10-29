import { useEffect, useMemo, useState } from "react";
import { Check, SkipForward, Sparkles, X } from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import { Button } from "./components";
import { ProposalCard } from "./SceneBoard";
import type { Proposal } from "./SceneBoard";
import type { CastBank, StageScene } from "./animationTypes";
import type { Project } from "./types";

type BatchProposal = Proposal & { number: number; title: string; before: Partial<StageScene> };
type BatchResult = {
  proposals: BatchProposal[];
  errors: { scene_id: string; number: number; message: string }[];
  revision: number;
};
const CONTENT = ["title", "story_time", "location_id", "location_state_id", "characters", "props", "action",
  "camera", "motion", "dialogue", "sound", "audio", "seconds"] as const;
const content = (scene: Partial<StageScene>) =>
  JSON.stringify(CONTENT.map((k) => scene[k as keyof StageScene] ?? null));

/** One click: AI drafts fixes for every scene sent back for rework; the director accepts them one by one. */
export function ReworkBatch({ bank, compact = false }: { bank: CastBank; compact?: boolean }) {
  const s = useStudio();
  const p = s.project!;
  const job = s.jobs
    .filter((j) => j.project_id === p.id && j.kind === "rework")
    .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0];
  const result = job?.status === "SUCCEEDED" ? (job.result as unknown as BatchResult) : null;
  const key = job ? "docos:rework-done:" + job.id : "";
  const [handled, setHandled] = useState<string[]>([]);
  useEffect(() => {
    try {
      setHandled(key ? JSON.parse(localStorage.getItem(key) || "[]") : []);
    } catch {
      setHandled([]);
    }
  }, [key]);
  const queue = useMemo(
    () => (result?.proposals || []).filter((x) => !handled.includes(x.scene_id)),
    [result, handled],
  );
  const current = queue[0];
  const scene = current && p.stage_scenes.find((x) => x.id === current.scene_id);
  const stale = !!(current && scene && content(scene) !== content(current.before));
  const characters = useMemo(() => Object.fromEntries(bank.characters.map((c) => [c.id, c])), [bank]);
  const open = p.stage_scenes.filter((x) => x.status === "rework").length;
  const running = job && ["QUEUED", "RUNNING"].includes(job.status);

  function done(id: string) {
    const next = [...handled, id];
    setHandled(next);
    localStorage.setItem(key, JSON.stringify(next));
  }
  function accept() {
    if (!current || !scene) return;
    if (stale && !confirm(`Scena ${current.number} zmieniła się od przygotowania propozycji. Nadpisać ją propozycją?`)) return;
    s.run(async () => {
      await s.mutate((latest) =>
        api<Project>(`/projects/${latest.id}/stage-scenes`, {
          expected_revision: latest.revision,
          operations: [{ type: "update", scene_id: current.scene_id, changes: current.changes }],
        }),
      );
      done(current.scene_id);
    });
  }
  useEffect(() => {
    if (!current) return;
    function keys(e: KeyboardEvent) {
      const t = e.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName) || e.metaKey || e.ctrlKey) return;
      if (e.key === "Enter") accept();
      else if (e.key.toLowerCase() === "x") done(current!.scene_id);
      else return;
      e.preventDefault();
      e.stopPropagation();
    }
    window.addEventListener("keydown", keys, true);
    return () => window.removeEventListener("keydown", keys, true);
  });

  return (
    <div className={`rework-batch ${compact ? "compact" : ""}`}>
      <Button
        icon={Sparkles}
        busy={!!running}
        disabled={!open || !!running}
        title={open ? "AI przygotuje poprawki wszystkich scen ze statusem „Do poprawki” według Twoich uwag" : "Brak scen do poprawki"}
        onClick={() =>
          s.run(async () => {
            await api(`/projects/${p.id}/stage-scenes/rework-batch`, {});
            s.notify(`AI poprawia ${open} scen — propozycje pojawią się tutaj`);
          })
        }
      >
        {running
          ? `Poprawiam… ${job?.message || ""}`
          : `Popraw sceny do poprawki${open ? ` (${open})` : ""}`}
      </Button>
      {job?.status === "FAILED" && <p className="manual-error small">Zbiorcza poprawka nie powiodła się: {job.message}</p>}
      {result && result.errors.length > 0 && queue.length === 0 && (
        <p className="manual-error small">
          Bez propozycji: {result.errors.map((e) => `scena ${e.number} (${e.message})`).join("; ")}
        </p>
      )}
      {current && scene && (
        <div className="batch-review">
          <div className="proposal-head">
            <strong>
              Scena {current.number}: {current.title} — propozycja {result!.proposals.length - queue.length + 1}/{result!.proposals.length}
            </strong>
            <span className="muted small">Enter — przyjmij · X — pomiń</span>
          </div>
          {scene.reviews.length > 0 && (
            <p className="small muted">Twoja uwaga: {[...scene.reviews].reverse()[0].tags.join(", ")} {[...scene.reviews].reverse()[0].note}</p>
          )}
          {stale && <p className="manual-error small">Ta scena zmieniła się od przygotowania propozycji.</p>}
          <ProposalCard
            scene={scene}
            proposal={current}
            characters={characters}
            bank={bank}
            accept={accept}
            reject={() => done(current.scene_id)}
          />
          <div className="button-row">
            <Button primary icon={Check} onClick={accept}>
              Przyjmij <kbd>Enter</kbd>
            </Button>
            <Button icon={SkipForward} onClick={() => done(current.scene_id)}>
              Pomiń <kbd>X</kbd>
            </Button>
            <Button icon={X} subtle onClick={() => result!.proposals.forEach((x) => done(x.scene_id))}>
              Zamknij wszystkie
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
