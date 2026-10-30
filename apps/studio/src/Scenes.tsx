import { useEffect, useRef, useState } from "react";
import {
  ArrowUpRight,
  Clapperboard,
  Clock3,
  Film,
  Layers3,
  Plus,
  Search,
  Upload,
} from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import {
  AssetThumb,
  Button,
  CommitText,
  Empty,
  Field,
  Modal,
  SectionHead,
} from "./components";
import { makeScene } from "./Generation";
import { Stage } from "./SceneBoard";
import { ReworkBatch } from "./ReworkBatch";
import { statusLabels } from "./animationTypes";
import type { CastBank, StageScene } from "./animationTypes";
import type { Project, Scene } from "./types";
import { fps } from "./timing";
import {
  paperLayerIds,
  readSceneImport,
  shotEntries,
  shotSeconds,
} from "./sceneWorkspace";
import type { ShotEntry } from "./sceneWorkspace";

export default function Scenes() {
  const s = useStudio(),
    p = s.project!;
  const [bank, setBank] = useState<CastBank>({ characters: [], locations: [] });
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [kind, setKind] = useState(
    p.production_mode === "animation_2d" ? "stage" : "media",
  );
  const [imported, setImported] = useState<ReturnType<
    typeof readSceneImport
  > | null>(null);
  const [importing, setImporting] = useState(false);
  const file = useRef<HTMLInputElement>(null);
  useEffect(() => {
    let alive = true;
    setBank({ characters: [], locations: [] });
    if (p.channel_id)
      s.run(async () => {
        const value = await api<CastBank>(`/channels/${p.channel_id}/cast`);
        if (alive) setBank(value);
      });
    return () => {
      alive = false;
    };
  }, [p.channel_id]);
  const entries = shotEntries(p),
    rate = fps(p);
  const visible = entries.filter((entry) => {
    const text =
      entry.kind === "stage"
        ? entry.scene.action
        : entry.scene.description || entry.scene.narration;
    return (
      `${entry.scene.title} ${text}`
        .toLocaleLowerCase("pl")
        .includes(query.toLocaleLowerCase("pl")) &&
      (filter === "all" ||
        (entry.kind === "stage" && entry.scene.status === filter) ||
        (entry.kind === "media" && filter === "media"))
    );
  });
  const total = entries.reduce(
    (sum, entry) => sum + shotSeconds(entry, rate),
    0,
  );
  function open(entry: ShotEntry) {
    s.setTargetScene(entry.scene.id);
    s.setPage("shot-editor");
  }
  function update(entry: ShotEntry, changes: Partial<StageScene & Scene>) {
    s.run(() =>
      entry.kind === "stage"
        ? s.mutate((current) =>
            api<Project>(`/projects/${current.id}/stage-scenes`, {
              expected_revision: current.revision,
              operations: [
                { type: "update", scene_id: entry.scene.id, changes },
              ],
            }),
          )
        : s.patch((current) => ({
            scenes: current.scenes.map((scene) =>
              scene.id === entry.scene.id ? { ...scene, ...changes } : scene,
            ),
          })),
    );
  }
  async function create() {
    let id: string;
    if (kind === "stage") {
      const before = new Set(p.stage_scenes.map((scene) => scene.id));
      const result = await s.mutate((current) =>
        api<Project>(`/projects/${current.id}/stage-scenes`, {
          expected_revision: current.revision,
          operations: [{ type: "add", scene: {} }],
        }),
      );
      id = result.stage_scenes.find((scene) => !before.has(scene.id))!.id;
    } else if (kind === "paper") {
      const result = await s.mutate((current) =>
        api<Project>(`/projects/${current.id}/paper-theatre/scenes`, {
          expected_revision: current.revision,
        }),
      );
      id = result.scenes[result.scenes.length - 1].id;
    } else {
      const scene = makeScene(
        Math.max(0, ...p.scenes.map((item) => item.start + item.duration)),
      );
      await s.patch((current) => ({ scenes: [...current.scenes, scene] }));
      id = scene.id;
    }
    s.setTargetScene(id);
    s.setPage("shot-editor");
  }
  async function readFile(value: File) {
    if (value.size > 8 * 1024 * 1024) throw new Error("Plik przekracza 8 MB.");
    setImported(readSceneImport(JSON.parse(await value.text())));
  }
  async function importScenes() {
    if (!imported) return;
    setImporting(true);
    try {
      if (imported.kind === "stage") {
        if (p.production_mode !== "animation_2d" || !p.channel_id)
          throw new Error(
            "Sceny z bankiem postaci wymagają filmu Animacja 2D przypisanego do kanału.",
          );
        await s.mutate((current) =>
          api<Project>(`/projects/${current.id}/stage-scenes`, {
            expected_revision: current.revision,
            operations: imported.scenes.map((scene) => ({
              type: "add",
              scene,
            })),
          }),
        );
      } else {
        await s.patch((current) => {
          let cursor = Math.max(
            0,
            ...current.scenes.map((scene) => scene.start + scene.duration),
          );
          const scenes = imported.scenes.map((scene) => {
            const fresh = makeScene(cursor);
            const next = { ...fresh, ...scene, id: fresh.id } as Scene;
            if (
              typeof next.start === "number" &&
              typeof next.duration === "number"
            )
              cursor = Math.max(cursor, next.start + next.duration);
            return next;
          });
          return { scenes: [...current.scenes, ...scenes] };
        });
      }
      s.notify(`Zaimportowano ${imported.scenes.length} ujęć.`);
      setImported(null);
    } finally {
      setImporting(false);
    }
  }
  return (
    <div className="page-content scenes-overview">
      <SectionHead
        eyebrow="PLAN ODCINKA"
        title="Sceny"
        description="Wszystkie ujęcia odcinka. Kliknij miniaturę lub wiersz, żeby otworzyć edytor ujęcia."
      />
      <div className="scenes-overview-toolbar">
        <label className="scene-search">
          <Search size={16} />
          <input
            aria-label="Szukaj scen"
            placeholder="Szukaj sceny…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <span className="muted small">
          {entries.length} ujęć · {total.toFixed(1)} s
        </span>
        <Button icon={Upload} onClick={() => file.current?.click()}>
          Importuj sceny
        </Button>
        <input
          hidden
          type="file"
          ref={file}
          accept=".json,application/json"
          onChange={(e) => {
            const value = e.target.files?.[0];
            e.target.value = "";
            if (value) s.run(() => readFile(value));
          }}
        />
        <select
          aria-label="Rodzaj nowego ujęcia"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          {p.production_mode === "animation_2d" && p.channel_id && (
            <option value="stage">Animacja 2D</option>
          )}
          <option value="media">Zdjęcie / wideo</option>
          <option value="paper">Paper Theatre 2.5D</option>
        </select>
        <Button icon={Plus} primary onClick={() => s.run(create)}>
          Dodaj ujęcie
        </Button>
      </div>
      <div className="scene-filters" role="group" aria-label="Filtr scen">
        {[
          ["all", "Wszystkie"],
          ["draft", "Szkice"],
          ["review", "Do oceny"],
          ["rework", "Do poprawki"],
          ["approved", "Zatwierdzone"],
          ["media", "Zdjęcia, wideo i Paper Theatre"],
        ].map(([id, label]) => (
          <button
            key={id}
            aria-pressed={filter === id}
            className={filter === id ? "active" : ""}
            onClick={() => setFilter(id)}
          >
            {label}
          </button>
        ))}
      </div>
      {p.production_mode === "animation_2d" &&
        p.channel_id &&
        p.stage_scenes.length > 0 && (
          <details className="scene-review-tools">
            <summary>Ocena scen i poprawki AI</summary>
            <ReworkBatch bank={bank} compact />
          </details>
        )}
      {visible.length > 0 ? (
        <>
          <div className="scene-sheet-columns" aria-hidden="true">
            <span>UJĘCIE</span>
            <span>PODGLĄD</span>
            <span>OPIS SCENY</span>
            <span>DIALOG / NARRACJA</span>
            <span>METRYKA I UWAGI</span>
          </div>
          <div className="scene-sheet-list">
            {visible.map((entry) => {
              const shot = entry.scene,
                stage = entry.kind === "stage" ? entry.scene : null;
              const media = entry.kind === "media" ? entry.scene : null;
              const index = entries.findIndex(
                (item) => item.scene.id === shot.id,
              );
              const beat = p.beats.find((item) => item.id === shot.beat_id);
              const location =
                stage &&
                bank.locations.find((item) => item.id === stage.location_id);
              const asset =
                media && p.assets.find((item) => item.id === media.asset_id);
              const isPaper = media?.template === "paper-theatre";
              return (
                <article
                  key={shot.id}
                  className="scene-sheet-row surface"
                  onClick={(event) => {
                    if (
                      !(event.target as HTMLElement).closest(
                        "button,input,textarea,select,label,a",
                      )
                    )
                      open(entry);
                  }}
                >
                  <div className="scene-sheet-number">
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <span className="small muted">
                      {stage ? "2D" : isPaper ? "2.5D" : "FILM"}
                    </span>
                  </div>
                  <button
                    className="scene-sheet-preview"
                    aria-label={`Edytuj ujęcie: ${shot.title}`}
                    onClick={() => open(entry)}
                  >
                    {stage ? (
                      <Stage
                        scene={stage}
                        bank={bank}
                        channelId={p.channel_id}
                        compact
                      />
                    ) : asset ? (
                      <AssetThumb asset={asset} project={p} />
                    ) : (
                      <div className="shot-placeholder">
                        {isPaper ? <Layers3 size={28} /> : <Film size={28} />}
                        <span>Dodaj obraz</span>
                      </div>
                    )}
                    <span className="shot-open-label">
                      Edytuj ujęcie <ArrowUpRight size={13} />
                    </span>
                  </button>
                  <div className="scene-sheet-description">
                    <CommitText
                      label={`Tytuł ujęcia ${index + 1}`}
                      value={shot.title}
                      disabled={media?.locked}
                      onCommit={(title) =>
                        update(entry, { title: title || "Ujęcie" })
                      }
                    />
                    <CommitText
                      label={`Opis sceny ${index + 1}`}
                      multiline
                      rows={3}
                      disabled={media?.locked}
                      value={stage?.action || media?.description || ""}
                      placeholder="Co dzieje się w tej scenie?"
                      onCommit={(text) =>
                        update(
                          entry,
                          stage ? { action: text } : { description: text },
                        )
                      }
                    />
                    {stage && (
                      <span className={`badge status-${stage.status}`}>
                        {statusLabels[stage.status]}
                      </span>
                    )}
                    {isPaper && (
                      <span className="badge quiet">
                        Paper Theatre 2.5D · {paperLayerIds(media!).length}{" "}
                        warstw
                      </span>
                    )}
                  </div>
                  <div className="scene-sheet-dialogue">
                    <span className="shot-field-heading">
                      {stage ? "Dialog sceny" : "Narracja"}
                    </span>
                    {stage ? (
                      stage.dialogue.length ? (
                        stage.dialogue.map((line, i) => (
                          <p key={line.id || i}>
                            <strong>
                              {line.speaker === "narrator"
                                ? "Narrator"
                                : bank.characters.find(
                                    (item) => item.id === line.speaker,
                                  )?.name || line.speaker}
                            </strong>
                            {line.direction && <em> ({line.direction})</em>}
                            <br />
                            {line.text}
                          </p>
                        ))
                      ) : (
                        <p className="muted small">
                          Dodaj kwestie w edytorze ujęcia.
                        </p>
                      )
                    ) : (
                      <CommitText
                        label={`Narracja ujęcia ${index + 1}`}
                        multiline
                        rows={4}
                        value={media!.narration}
                        disabled={media!.locked || media!.lock_narration}
                        placeholder="Tekst lektora…"
                        onCommit={(narration) => update(entry, { narration })}
                      />
                    )}
                    {stage && (
                      <Button subtle onClick={() => open(entry)}>
                        Edytuj dialog
                      </Button>
                    )}
                  </div>
                  <div className="scene-sheet-meta">
                    <span className="shot-field-heading">Metryka</span>
                    <span className="small">
                      <Clock3 size={13} /> {shotSeconds(entry, rate).toFixed(1)}{" "}
                      s{stage?.story_time ? ` · ${stage.story_time}` : ""}
                    </span>
                    {location && (
                      <span className="small muted">{location.name}</span>
                    )}
                    {beat && <span className="small muted">{beat.title}</span>}
                    <Field label="Uwagi reżysera">
                      <CommitText
                        label={`Uwagi reżysera ${index + 1}`}
                        multiline
                        rows={2}
                        disabled={media?.locked}
                        value={shot.director_notes || ""}
                        placeholder="Wskazówki do tego ujęcia…"
                        onCommit={(director_notes) =>
                          update(entry, { director_notes })
                        }
                      />
                    </Field>
                  </div>
                </article>
              );
            })}
          </div>
        </>
      ) : (
        <Empty
          icon={Clapperboard}
          title={
            entries.length ? "Brak pasujących scen" : "Zaplanuj pierwszą scenę"
          }
        >
          {entries.length
            ? "Zmień filtr lub wyszukiwaną frazę."
            : "Dodaj ujęcie albo zaimportuj gotowe sceny. Z tej listy przejdziesz do edycji każdego ujęcia."}
        </Empty>
      )}
      <Modal
        open={!!imported}
        onClose={() => setImported(null)}
        title="Importuj sceny"
        description="Ujęcia zostaną dodane do tego filmu z nowymi identyfikatorami. Zasoby muszą istnieć w filmie lub banku kanału."
      >
        <p>
          {imported?.scenes.length} ujęć ·{" "}
          {imported?.kind === "stage"
            ? "Animacja 2D"
            : "Zdjęcia, wideo i kompozycje"}
        </p>
        <ol>
          {imported?.scenes.slice(0, 10).map((scene, i) => (
            <li key={i}>{String(scene.title || "Ujęcie " + (i + 1))}</li>
          ))}
        </ol>
        <Button primary busy={importing} onClick={() => s.run(importScenes)}>
          Dodaj ujęcia do filmu
        </Button>
      </Modal>
    </div>
  );
}
