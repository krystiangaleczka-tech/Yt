import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
import {
  Check,
  ChevronDown,
  ChevronUp,
  Clipboard,
  FlipHorizontal,
  LayoutGrid,
  MapPinned,
  Music2,
  Play,
  Plus,
  RotateCcw,
  Sparkles,
  Trash2,
  UserPlus,
  Volume2,
  X,
} from "lucide-react";
import { useStudio } from "./context";
import { ReworkBatch } from "./ReworkBatch";
import { api } from "./api";
import { Button, CommitText, Empty, Field, IconButton, NumberField } from "./components";
import {
  actorMotionLabels,
  cameraLabels,
  castAudio,
  propMotionLabels,
  castImage,
  reviewTags,
  statusLabels,
} from "./animationTypes";
import type {
  ActorMotion,
  CameraMove,
  CastBank,
  Character,
  DialogueLine,
  StageCharacter,
  StageProp,
  StageScene,
  SoundCue,
} from "./animationTypes";
import type { Project } from "./types";

export type Proposal = {
  scene_id: string;
  changes: Partial<StageScene>;
  reason: string;
  base_revision: number;
};
type Filter = "all" | "open" | "rework" | "approved";
const filters: { id: Filter; label: string }[] = [
  { id: "all", label: "Wszystkie" },
  { id: "open", label: "Do oceny" },
  { id: "rework", label: "Do poprawki" },
  { id: "approved", label: "Zatwierdzone" },
];
const typing = (target: EventTarget | null) =>
  target instanceof HTMLElement &&
  (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName) ||
    target.isContentEditable);

export default function SceneBoard() {
  const s = useStudio();
  const p = s.project!;
  const [bank, setBank] = useState<CastBank>({ characters: [], locations: [] }),
    [selected, setSelected] = useState(
      localStorage.getItem("docos:stage:" + p.id) || "",
    ),
    [filter, setFilter] = useState<Filter>("all"),
    [tags, setTags] = useState<string[]>([]),
    [note, setNote] = useState(""),
    [proposal, setProposal] = useState<Proposal | null>(null),
    [manual, setManual] = useState<{ prompt: string; response: string; error: string } | null>(null),
    [busy, setBusy] = useState(false);
  const noteRef = useRef<HTMLTextAreaElement>(null);
  const [previewRun, setPreviewRun] = useState(0);
  const previewTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => {
    if (p.channel_id)
      s.run(async () => setBank(await api<CastBank>(`/channels/${p.channel_id}/cast`)));
  }, [p.channel_id]);
  const scenes = p.stage_scenes || [];
  const visible = scenes.filter((x) =>
    filter === "all"
      ? true
      : filter === "open"
        ? x.status === "review" || x.status === "draft"
        : x.status === filter,
  );
  const scene = scenes.find((x) => x.id === selected) || visible[0] || scenes[0];
  useEffect(() => {
    if (scene) localStorage.setItem("docos:stage:" + p.id, scene.id);
    setTags([]);
    setNote("");
    setProposal(null);
    setManual(null);
  }, [scene?.id]);
  const characters = useMemo(
    () => Object.fromEntries(bank.characters.map((c) => [c.id, c])),
    [bank],
  );
  const approved = scenes.filter((x) => x.status === "approved").length;

  function send(operations: Record<string, unknown>[]) {
    return s.mutate((current) =>
      api<Project>(`/projects/${current.id}/stage-scenes`, {
        expected_revision: current.revision,
        operations,
      }),
    );
  }
  const update = (changes: Partial<StageScene>) =>
    scene && s.run(() => send([{ type: "update", scene_id: scene.id, changes }]));
  function next(delta: number) {
    const list = visible.length ? visible : scenes;
    const index = list.findIndex((x) => x.id === scene?.id);
    const target = list[Math.max(0, Math.min(list.length - 1, index + delta))];
    if (target) setSelected(target.id);
  }
  function review(status: "approved" | "rework") {
    if (!scene) return;
    if (status === "rework" && !tags.length && !note.trim()) {
      noteRef.current?.focus();
      s.notify("Zaznacz obszar albo napisz, co poprawić");
      return;
    }
    s.run(async () => {
      await send([{ type: "review", scene_id: scene.id, status, tags, note }]);
      // The review is stored in the scene history (and fed to regeneration), so the bar starts clean.
      setTags([]);
      setNote("");
      if (status === "approved") next(1);
    });
  }
  function instruction() {
    return [tags.join(", "), note].filter(Boolean).join(" — ");
  }
  function regenerate(response?: string) {
    if (!scene) return;
    s.run(async () => {
      setBusy(true);
      try {
        setProposal(
          await api<Proposal>(
            `/projects/${p.id}/stage-scenes/${scene.id}/regenerate`,
            { instruction: instruction(), ...(response ? { response } : {}) },
          ),
        );
        setManual(null);
      } catch (error) {
        const { prompt } = await api<{ prompt: string }>(
          `/projects/${p.id}/stage-scenes/${scene.id}/prompt`,
          { instruction: instruction() },
        );
        setManual({ prompt, response: response || "", error: String((error as Error).message || error) });
        throw error;
      } finally {
        setBusy(false);
      }
    });
  }
  useEffect(() => {
    function key(e: KeyboardEvent) {
      if (typing(e.target) || e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key.toLowerCase();
      if (k === "arrowdown" || k === "j") next(1);
      else if (k === "arrowup" || k === "k") next(-1);
      else if (k === "a") review("approved");
      else if (k === "r") {
        e.preventDefault();
        noteRef.current?.focus();
      } else if (k === "g") regenerate();
      else return;
      e.preventDefault();
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  });

  if (p.production_mode !== "animation_2d")
    return (
      <Empty
        icon={LayoutGrid}
        title="Sceny są częścią trybu Animacja 2D"
        children="Ten film jest w innym trybie. Utwórz film animowany albo przełącz tryb w lewym górnym rogu."
      />
    );
  if (!p.channel_id)
    return (
      <Empty
        icon={LayoutGrid}
        title="Przypisz film do kanału"
        children="Sceny korzystają z postaci i lokacji banku kanału. Ustaw kanał w Narzędziach produkcji → Kontekst i zasoby filmu."
      />
    );
  return (
    <div className="scene-board">
      <aside className="scene-list">
        <div className="scene-list-head">
          <div>
            <strong>Sceny</strong>
            <span className="muted small">
              {approved}/{scenes.length} zatwierdzonych
            </span>
          </div>
          <Button
            icon={Plus}
            primary
            onClick={() =>
              s.run(async () => {
                const before = new Set(scenes.map((x) => x.id));
                const result = await send([
                  {
                    type: "add",
                    after: scene?.id,
                    scene: scene
                      ? {
                          location_id: scene.location_id,
                          location_state_id: scene.location_state_id,
                          story_time: scene.story_time,
                        }
                      : {},
                  },
                ]);
                const added = result.stage_scenes.find((x) => !before.has(x.id));
                if (added) setSelected(added.id);
              })
            }
          >
            Scena
          </Button>
        </div>
        <ReworkBatch bank={bank} compact />
        <div className="scene-progress" aria-hidden>
          <span style={{ width: `${scenes.length ? (approved / scenes.length) * 100 : 0}%` }} />
        </div>
        <div className="scene-filters" role="tablist">
          {filters.map((f) => (
            <button
              key={f.id}
              role="tab"
              aria-selected={filter === f.id}
              className={filter === f.id ? "active" : ""}
              onClick={() => setFilter(f.id)}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="scene-items">
          {visible.map((x) => (
            <button
              key={x.id}
              className={`scene-item ${x.id === scene?.id ? "active" : ""}`}
              onClick={() => setSelected(x.id)}
            >
              <span className={`status-dot ${x.status}`} title={statusLabels[x.status]} />
              <span className="scene-no">{String(x.number).padStart(2, "0")}</span>
              <span className="scene-item-text">
                <strong>{x.title}</strong>
                <span className="muted small">{x.action || "—"}</span>
              </span>
            </button>
          ))}
          {visible.length === 0 && (
            <p className="muted small">Brak scen w tym widoku.</p>
          )}
        </div>
        <p className="muted small scene-keys">
          ↑↓ / J K — scena · A — zatwierdź · R — poprawka · G — regeneruj
        </p>
      </aside>
      {!scene ? (
        <Empty
          icon={LayoutGrid}
          title="Pierwsza scena"
          children="Dodaj scenę, wybierz lokację i postacie z banku kanału. Każdą scenę zatwierdzasz albo odsyłasz do poprawki."
        />
      ) : (
        <>
          <section className="scene-main">
            <div className="scene-title-row">
              <span className="scene-number">SCENA {String(scene.number).padStart(2, "0")}</span>
              <span className={`badge status-${scene.status}`}>{statusLabels[scene.status]}</span>
              {scene.story_time && <span className="muted small">{scene.story_time}</span>}
              <span className="muted small">{scene.seconds} s</span>
            </div>
            <h2 className="scene-heading">{scene.title}</h2>
            {continuity(scene, scenes[scenes.findIndex((x) => x.id === scene.id) - 1], bank).map((w) => (
              <p key={w} className="continuity-warning small">Ciągłość: {w}</p>
            ))}
            <Stage
              key={scene.id + previewRun}
              scene={scene}
              bank={bank}
              channelId={p.channel_id}
              animate={previewRun > 0}
              onPlace={previewRun ? undefined : (placed) => update({ characters: placed })}
              onPlaceProps={previewRun ? undefined : (props) => update({ props })}
            />
            <div className="scene-preview-row">
              <Button
                icon={Play}
                subtle
                onClick={() => {
                  setPreviewRun((n) => n + 1);
                  clearTimeout(previewTimer.current);
                  previewTimer.current = setTimeout(() => setPreviewRun(0), scene.seconds * 1000 + 400);
                }}
              >
                Podgląd ruchu ({scene.seconds} s)
              </Button>
            </div>
            <div className="scene-facts">
              {scene.action && <p>{scene.action}</p>}
              {scene.camera && (
                <p className="muted small">Kamera: {scene.camera}</p>
              )}
              {scene.dialogue.length > 0 && (
                <ul className="scene-dialogue">
                  {scene.dialogue.map((line, i) => (
                    <li key={line.id || i}>
                      <strong>
                        {line.speaker === "narrator"
                          ? "Narrator"
                          : characters[line.speaker]?.name || "?"}
                      </strong>
                      {line.direction && <em> ({line.direction})</em>}: {line.text}
                    </li>
                  ))}
                </ul>
              )}
              <div className="scene-sound">
                {(scene.audio || []).map((cue, i) => {
                  const sound = bank.sounds?.find((x) => x.id === cue.sound_id);
                  return sound ? (
                    <span key={"cue" + i} className="sound-chip linked">
                      <Volume2 size={13} /> {sound.name}
                      {sound.kind === "sfx" ? ` @${Math.round(cue.at * 100)}%` : " (pętla)"}
                    </span>
                  ) : null;
                })}
                {scene.sound.ambience && (
                  <span className="sound-chip"><Volume2 size={13} /> {scene.sound.ambience}</span>
                )}
                {scene.sound.music && (
                  <span className="sound-chip"><Music2 size={13} /> {scene.sound.music}</span>
                )}
                {scene.sound.sfx.map((x) => (
                  <span key={x} className="sound-chip">SFX: {x}</span>
                ))}
              </div>
            </div>
            <div className="review-bar">
              <div className="review-tags" aria-label="Co poprawić">
                {reviewTags.map((t) => (
                  <button
                    key={t}
                    className={tags.includes(t) ? "active" : ""}
                    aria-pressed={tags.includes(t)}
                    onClick={() =>
                      setTags(tags.includes(t) ? tags.filter((x) => x !== t) : [...tags, t])
                    }
                  >
                    {t}
                  </button>
                ))}
              </div>
              <textarea
                ref={noteRef}
                rows={2}
                value={note}
                placeholder="Uwagi reżysera — co zmienić (Esc wraca do skrótów)"
                onChange={(e) => setNote(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Escape") (e.target as HTMLElement).blur();
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) review("rework");
                }}
              />
              <div className="review-actions">
                <Button primary icon={Check} onClick={() => review("approved")}>
                  Zatwierdź <kbd>A</kbd>
                </Button>
                <Button icon={RotateCcw} onClick={() => review("rework")}>
                  Do poprawki <kbd>R</kbd>
                </Button>
                <Button icon={Sparkles} busy={busy} onClick={() => regenerate()}>
                  Regeneruj z AI <kbd>G</kbd>
                </Button>
              </div>
            </div>
            {proposal && (
              <ProposalCard
                scene={scene}
                proposal={proposal}
                characters={characters}
                bank={bank}
                accept={() =>
                  s.run(async () => {
                    await send([{ type: "update", scene_id: scene.id, changes: proposal.changes }]);
                    setProposal(null);
                    s.notify("Przyjęto propozycję. Scena czeka na ocenę.");
                  })
                }
                reject={() => setProposal(null)}
              />
            )}
            {manual && (
              <div className="proposal-card">
                <div className="proposal-head">
                  <strong>AI nie dało poprawnej propozycji</strong>
                  <IconButton icon={X} label="Zamknij" onClick={() => setManual(null)} />
                </div>
          <p className="small manual-error">{manual.error}</p>
          <p className="muted small">
            Spróbuj ponownie albo skopiuj prompt do własnego modelu i wklej odpowiedź JSON — aplikacja sprawdzi, czy używa tylko postaci i lokacji z banku.
          </p>
                <Button
                  icon={Clipboard}
                  onClick={() =>
                    s.run(async () => {
                      await navigator.clipboard.writeText(manual.prompt);
                      s.notify("Skopiowano prompt");
                    })
                  }
                >
                  Kopiuj prompt
                </Button>
                <textarea
                  rows={5}
                  value={manual.response}
                  placeholder='{"title": "...", "action": "...", ...}'
                  onChange={(e) => setManual({ ...manual, response: e.target.value })}
                />
                <Button
                  primary
                  disabled={!manual.response.trim()}
                  onClick={() => regenerate(manual.response)}
                >
                  Sprawdź odpowiedź
                </Button>
              </div>
            )}
            {scene.reviews.length > 0 && (
              <details className="review-history">
                <summary>Historia ocen ({scene.reviews.length})</summary>
                <ul>
                  {[...scene.reviews].reverse().map((r, i) => (
                    <li key={i}>
                      <span className={`status-dot ${r.status}`} />
                      {statusLabels[r.status]}
                      {r.tags.length > 0 && ` · ${r.tags.join(", ")}`}
                      {r.note && ` — ${r.note}`}
                      <span className="muted small">
                        {" "}
                        {r.at && new Date(r.at).toLocaleString("pl-PL")}
                      </span>
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </section>
          <SceneInspector
            key={scene.id}
            scene={scene}
            sceneBefore={scenes[scenes.findIndex((x) => x.id === scene.id) - 1]}
            bank={bank}
            beats={p.beats}
            update={update}
            remove={() =>
              s.run(async () => {
                if (!confirm(`Usunąć scenę ${scene.number}?`)) return;
                await send([{ type: "delete", scene_id: scene.id }]);
                next(1);
              })
            }
            move={(delta) =>
              s.run(() =>
                send([
                  {
                    type: "move",
                    scene_id: scene.id,
                    to: scenes.findIndex((x) => x.id === scene.id) + delta,
                  },
                ]),
              )
            }
          />
        </>
      )}
    </div>
  );
}

export function Stage({
  scene,
  bank,
  channelId,
  onPlace,
  onPlaceProps,
  lineIndex = 0,
  compact = false,
  animate = false,
}: {
  scene: StageScene;
  bank: CastBank;
  channelId: string;
  onPlace?: (placed: StageCharacter[]) => void;
  onPlaceProps?: (props: StageProp[]) => void;
  lineIndex?: number;
  compact?: boolean;
  /** Play camera and character motion over the scene's duration (animatic / preview). */
  animate?: boolean;
}) {
  const frame = useRef<HTMLDivElement>(null);
  const [drag, setDrag] = useState<{
    kind: "actor" | "prop";
    index: number;
    x: number;
    y: number;
    dx: number;
    dy: number;
  } | null>(null);
  const location = bank.locations.find((l) => l.id === scene.location_id);
  const state =
    location?.states.find((st) => st.id === scene.location_state_id) ||
    location?.states.find((st) => st.image);
  const line = compact ? undefined : scene.dialogue[lineIndex];
  const camera = scene.motion?.camera || "static";
  const motionStyle = {
    "--dur": `${scene.seconds}s`,
    "--s": scene.motion?.strength ?? 0.5,
  } as CSSProperties;
  const speaker =
    line && line.speaker !== "narrator"
      ? bank.characters.find((c) => c.id === line.speaker)?.name
      : "";
  function renderProps(layer: StageProp["layer"]) {
    return (scene.props || []).map((placed, index) => {
      if (placed.layer !== layer) return null;
      const item = bank.items?.find((i) => i.id === placed.item_id);
      const variant =
        item?.variants.find((v) => v.id === placed.variant_id) || item?.variants[0];
      if (!variant) return null;
      const at = drag?.kind === "prop" && drag.index === index ? drag : placed;
      return (
        <span
          key={"prop" + index}
          className={`stage-prop layer-${layer} prop-${placed.motion}`}
          style={
            {
              left: `${at.x * 100}%`,
              top: `${at.y * 100}%`,
              height: `${placed.scale * 100}%`,
              "--at": placed.at,
              "--rot": `${placed.rotation}deg`,
            } as CSSProperties
          }
          onPointerDown={(e) => {
            if (!onPlaceProps) return;
            e.currentTarget.setPointerCapture(e.pointerId);
            const p = position(e);
            setDrag({ kind: "prop", index, x: placed.x, y: placed.y, dx: p.x - placed.x, dy: p.y - placed.y });
          }}
        >
          <img src={castImage(channelId, variant.image.file)} alt={item?.name} draggable={false} />
        </span>
      );
    });
  }
  function position(e: ReactPointerEvent) {
    const r = frame.current!.getBoundingClientRect();
    return {
      x: Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)),
      y: Math.min(1, Math.max(0, (e.clientY - r.top) / r.height)),
    };
  }
  return (
    <div
      ref={frame}
      className={`stage-frame ${state?.time_of_day === "night" ? "night" : ""} ${compact ? "compact" : ""} ${animate ? "animate" : ""}`}
      style={motionStyle}
      onPointerMove={(e) => {
        if (!drag) return;
        const at = position(e);
        setDrag({
          ...drag,
          x: Math.min(1, Math.max(0, at.x - drag.dx)),
          y: Math.min(1, Math.max(0, at.y - drag.dy)),
        });
      }}
      onPointerUp={() => {
        if (!drag) return;
        const moved = { x: Math.round(drag.x * 1000) / 1000, y: Math.round(drag.y * 1000) / 1000 };
        if (drag.kind === "actor" && onPlace)
          onPlace(scene.characters.map((c, i) => (i === drag.index ? { ...c, ...moved } : c)));
        if (drag.kind === "prop" && onPlaceProps)
          onPlaceProps((scene.props || []).map((c, i) => (i === drag.index ? { ...c, ...moved } : c)));
        setDrag(null);
      }}
    >
      <div className={`stage-world cam-${camera}`}>
      {state?.image ? (
        <img className="stage-bg" src={castImage(channelId, state.image.file)} alt="" />
      ) : (
        <div className="stage-empty">
          <MapPinned size={28} />
          <span>{location ? `${location.name} — brak tła stanu` : "Wybierz lokację"}</span>
        </div>
      )}
      {renderProps("behind")}
      {scene.characters.map((placed, index) => {
        const character = bank.characters.find((c) => c.id === placed.character_id);
        const pose =
          character?.poses.find((x) => x.id === placed.pose_id) ||
          character?.poses.find((x) => x.id === character.default_pose_id) ||
          character?.poses[0];
        const at = drag?.kind === "actor" && drag.index === index ? drag : placed;
        return pose ? (
          <span
            key={index}
            className={`stage-actor motion-${placed.motion || "idle"}`}
            style={{
              left: `${at.x * 100}%`,
              top: `${at.y * 100}%`,
              height: `${placed.scale * 100}%`,
            }}
            onPointerDown={(e) => {
              if (!onPlace) return;
              e.currentTarget.setPointerCapture(e.pointerId);
              // Keep the grab point under the cursor instead of snapping the feet to it.
              const at = position(e);
              setDrag({ kind: "actor", index, x: placed.x, y: placed.y, dx: at.x - placed.x, dy: at.y - placed.y });
            }}
          >
            <img
              src={castImage(channelId, pose.image.file)}
              alt={`${character?.name} — ${pose.name}`}
              draggable={false}
              style={{ transform: `scaleX(${placed.flip ? -1 : 1})` }}
            />
          </span>
        ) : (
          <span
            key={index}
            className="stage-missing"
            style={{ left: `${placed.x * 100}%`, top: `${placed.y * 100}%` }}
          >
            {character?.name || "?"}: brak pozy
          </span>
        );
      })}
      {renderProps("front")}
      {state?.foreground && (
        <img className="stage-fg" src={castImage(channelId, state.foreground.file)} alt="" />
      )}
      </div>
      {line?.text && (
        <div className="stage-caption">
          {speaker && <strong>{speaker}: </strong>}
          {line.text}
        </div>
      )}
    </div>
  );
}

export function ProposalCard({
  scene,
  proposal,
  characters,
  bank,
  accept,
  reject,
}: {
  scene: StageScene;
  proposal: Proposal;
  characters: Record<string, Character>;
  bank: CastBank;
  accept: () => void;
  reject: () => void;
}) {
  const after = { ...scene, ...proposal.changes } as StageScene;
  const where = (x: StageScene) => {
    const l = bank.locations.find((loc) => loc.id === x.location_id);
    return [l?.name, l?.states.find((st) => st.id === x.location_state_id)?.name]
      .filter(Boolean)
      .join(" · ");
  };
  const cast = (x: StageScene) =>
    x.characters
      .map((c) => {
        const ch = characters[c.character_id];
        return `${ch?.name || "?"} (${ch?.poses.find((p) => p.id === c.pose_id)?.name || "poza domyślna"})`;
      })
      .join(", ");
  const talk = (x: StageScene) =>
    x.dialogue
      .map((d: DialogueLine) => `${d.speaker === "narrator" ? "Narrator" : characters[d.speaker]?.name || "?"}: ${d.text}`)
      .join("\n");
  const sound = (x: StageScene) =>
    [x.sound.ambience, x.sound.music, ...x.sound.sfx].filter(Boolean).join(" · ");
  const rows: [string, string, string][] = [
    ["Tytuł", scene.title, after.title],
    ["Miejsce", where(scene), where(after)],
    ["Postacie", cast(scene), cast(after)],
    ["Akcja", scene.action, after.action],
    ["Kamera", scene.camera, after.camera],
    ["Dialog", talk(scene), talk(after)],
    ["Dźwięk", sound(scene), sound(after)],
  ];
  return (
    <div className="proposal-card">
      <div className="proposal-head">
        <strong>Propozycja AI</strong>
        {proposal.reason && <span className="muted small">{proposal.reason}</span>}
      </div>
      <table className="proposal-diff">
        <tbody>
          {rows
            .filter(([, a, b]) => a !== b)
            .map(([k, a, b]) => (
              <tr key={k}>
                <th>{k}</th>
                <td className="before">{a || "—"}</td>
                <td className="after">{b || "—"}</td>
              </tr>
            ))}
        </tbody>
      </table>
      <div className="button-row">
        <Button primary icon={Check} onClick={accept}>
          Przyjmij propozycję
        </Button>
        <Button icon={X} onClick={reject}>
          Odrzuć
        </Button>
      </div>
    </div>
  );
}

function SceneInspector({
  scene,
  sceneBefore,
  bank,
  beats,
  update,
  remove,
  move,
}: {
  scene: StageScene;
  sceneBefore?: StageScene;
  bank: CastBank;
  beats: Project["beats"];
  update: (changes: Partial<StageScene>) => void;
  remove: () => void;
  move: (delta: number) => void;
}) {
  const location = bank.locations.find((l) => l.id === scene.location_id);
  const active = bank.characters.filter((c) => !c.archived);
  const costumesFor = (characterId: string) =>
    (bank.items || []).filter(
      (i) =>
        i.category === "costume" &&
        !i.archived &&
        (!i.character_ids.length || i.character_ids.includes(characterId)),
    );
  const sceneSounds = (bank.sounds || []).filter((x) => x.kind !== "music" && !x.archived);
  const cues = scene.audio || [];
  const setCue = (index: number, patch: Partial<SoundCue>) =>
    update({ audio: cues.map((x, i) => (i === index ? { ...x, ...patch } : x)) });
  const placeable = (bank.items || []).filter((i) => i.category !== "costume" && !i.archived && i.variants.length);
  const props = scene.props || [];
  const setProp = (index: number, patch: Partial<StageProp>) =>
    update({ props: props.map((x, i) => (i === index ? { ...x, ...patch } : x)) });
  const setPlaced = (index: number, patch: Partial<StageCharacter>) =>
    update({
      characters: scene.characters.map((c, i) => (i === index ? { ...c, ...patch } : c)),
    });
  const setLine = (index: number, patch: Partial<DialogueLine>) =>
    update({
      dialogue: scene.dialogue.map((d, i) => (i === index ? { ...d, ...patch } : d)),
    });
  return (
    <aside className="scene-inspector">
      <div className="inspector-row">
        <IconButton icon={ChevronUp} label="Przesuń wyżej" onClick={() => move(-1)} />
        <IconButton icon={ChevronDown} label="Przesuń niżej" onClick={() => move(1)} />
        <IconButton icon={Trash2} label="Usuń scenę" onClick={remove} />
      </div>
      <Field label="Beat historii">
        <select
          value={scene.beat_id}
          onChange={(e) => update({ beat_id: e.target.value })}
        >
          <option value="">Bez beatu</option>
          {beats.map((b, i) => (
            <option key={b.id} value={b.id}>
              B{String(i + 1).padStart(2, "0")} · {b.title}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Tytuł sceny">
        <CommitText value={scene.title} onCommit={(title) => update({ title: title || "Scena" })} />
      </Field>
      <div className="two-fields">
        <Field label="Czas w historii">
          <CommitText
            value={scene.story_time}
            placeholder="Dzień 3, 06:14"
            onCommit={(story_time) => update({ story_time })}
          />
        </Field>
        <NumberField
          label="Długość (s)"
          value={scene.seconds}
          min={0.5}
          max={600}
          step={0.5}
          onCommit={(seconds) => update({ seconds })}
        />
      </div>
      <div className="two-fields">
        <Field label="Lokacja">
          <select
            value={scene.location_id}
            onChange={(e) =>
              update({
                location_id: e.target.value,
                location_state_id:
                  bank.locations.find((l) => l.id === e.target.value)?.states[0]?.id || "",
              })
            }
          >
            <option value="">—</option>
            {bank.locations
              .filter((l) => !l.archived || l.id === scene.location_id)
              .map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
          </select>
        </Field>
        <Field label="Stan">
          <select
            value={scene.location_state_id}
            disabled={!location}
            onChange={(e) => update({ location_state_id: e.target.value })}
          >
            <option value="">—</option>
            {location?.states.map((st) => (
              <option key={st.id} value={st.id}>
                {st.name}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <div className="inspector-section">
        <strong>Postacie w kadrze</strong>
        {scene.characters.map((placed, index) => {
          const character = bank.characters.find((c) => c.id === placed.character_id);
          return (
            <div key={index} className="placed-row">
              <select
                aria-label="Postać"
                value={placed.character_id}
                onChange={(e) => setPlaced(index, { character_id: e.target.value, pose_id: "" })}
              >
                {active.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <select
                aria-label="Poza"
                value={placed.pose_id}
                onChange={(e) => setPlaced(index, { pose_id: e.target.value })}
              >
                <option value="">Domyślna</option>
                {character?.poses
                  .filter((pose) => !placed.costume_id || pose.costume_id === placed.costume_id)
                  .map((pose) => (
                  <option key={pose.id} value={pose.id}>
                    {pose.name}
                  </option>
                ))}
              </select>
              {costumesFor(placed.character_id).length > 0 && (
                <select
                  aria-label="Kostium"
                  className="placed-motion"
                  value={placed.costume_id || ""}
                  onChange={(e) => setPlaced(index, { costume_id: e.target.value, pose_id: "" })}
                >
                  <option value="">Strój bazowy</option>
                  {costumesFor(placed.character_id).map((x) => (
                    <option key={x.id} value={x.id}>
                      {x.name}
                    </option>
                  ))}
                </select>
              )}
              <select
                aria-label="Ruch postaci"
                className="placed-motion"
                value={placed.motion || "idle"}
                onChange={(e) => setPlaced(index, { motion: e.target.value as ActorMotion })}
              >
                {Object.entries(actorMotionLabels).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
              <input
                type="range"
                aria-label="Wielkość"
                min={0.1}
                max={1.2}
                step={0.05}
                defaultValue={placed.scale}
                onPointerUp={(e) => setPlaced(index, { scale: Number(e.currentTarget.value) })}
                onKeyUp={(e) => setPlaced(index, { scale: Number(e.currentTarget.value) })}
              />
              <IconButton
                icon={FlipHorizontal}
                label="Odbij w poziomie"
                onClick={() => setPlaced(index, { flip: !placed.flip })}
              />
              <IconButton
                icon={X}
                label="Usuń z kadru"
                onClick={() =>
                  update({ characters: scene.characters.filter((_, i) => i !== index) })
                }
              />
            </div>
          );
        })}
        <Button
          icon={UserPlus}
          subtle
          disabled={!active.length || scene.characters.length >= 8}
          onClick={() =>
            update({
              characters: [
                ...scene.characters,
                {
                  character_id: active[0].id,
                  pose_id: "",
                  x: 0.3 + 0.2 * (scene.characters.length % 3),
                  y: 0.92,
                  scale: 0.6,
                  flip: false,
                },
              ],
            })
          }
        >
          {active.length ? "Dodaj postać" : "Bank postaci kanału jest pusty"}
        </Button>
        <span className="muted small">Przeciągnij postać na podglądzie, aby ją ustawić.</span>
      </div>
      <div className="inspector-section">
        <strong>Rekwizyty i nakładki</strong>
        {props.map((placed, index) => {
          const item = bank.items?.find((i) => i.id === placed.item_id);
          return (
            <div key={index} className="prop-row">
              <select
                aria-label="Rekwizyt"
                value={placed.item_id}
                onChange={(e) => setProp(index, { item_id: e.target.value, variant_id: "" })}
              >
                {placeable.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.name}
                  </option>
                ))}
              </select>
              <select
                aria-label="Wariant"
                value={placed.variant_id}
                onChange={(e) => setProp(index, { variant_id: e.target.value })}
              >
                <option value="">Pierwszy wariant</option>
                {item?.variants.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </select>
              <IconButton
                icon={X}
                label="Usuń z kadru"
                onClick={() => update({ props: props.filter((_, i) => i !== index) })}
              />
              <select
                aria-label="Warstwa"
                value={placed.layer}
                onChange={(e) => setProp(index, { layer: e.target.value as StageProp["layer"] })}
              >
                <option value="behind">Za postaciami</option>
                <option value="front">Przed postaciami</option>
              </select>
              <select
                aria-label="Pojawienie"
                value={placed.motion}
                onChange={(e) => setProp(index, { motion: e.target.value as StageProp["motion"] })}
              >
                {Object.entries(propMotionLabels).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
              <input
                type="range"
                aria-label="Wielkość rekwizytu"
                min={0.03}
                max={1}
                step={0.01}
                defaultValue={placed.scale}
                onPointerUp={(e) => setProp(index, { scale: Number(e.currentTarget.value) })}
                onKeyUp={(e) => setProp(index, { scale: Number(e.currentTarget.value) })}
              />
              {placed.motion !== "none" && (
                <label className="small muted prop-at">
                  moment: {Math.round(placed.at * 100)}% sceny
                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    defaultValue={placed.at}
                    onPointerUp={(e) => setProp(index, { at: Number(e.currentTarget.value) })}
                    onKeyUp={(e) => setProp(index, { at: Number(e.currentTarget.value) })}
                  />
                </label>
              )}
            </div>
          );
        })}
        <Button
          icon={Plus}
          subtle
          disabled={!placeable.length || props.length >= 20}
          onClick={() =>
            update({
              props: [
                ...props,
                {
                  item_id: placeable[0].id,
                  variant_id: "",
                  x: 0.5,
                  y: 0.5,
                  scale: 0.2,
                  rotation: 0,
                  layer: "behind",
                  motion: "none",
                  at: 0.5,
                },
              ],
            })
          }
        >
          {placeable.length ? "Dodaj rekwizyt" : "Bank rekwizytów kanału jest pusty"}
        </Button>
        {sceneBefore && (sceneBefore.props || []).length > 0 && (
          <Button
            subtle
            onClick={() =>
              update({
                props: [
                  ...props,
                  ...(sceneBefore.props || [])
                    .filter((x) => !props.some((y) => y.item_id === x.item_id))
                    .map((x) => ({ ...x, motion: "none" as const })),
                ],
              })
            }
          >
            Przenieś rekwizyty z poprzedniej sceny
          </Button>
        )}
      </div>
      <Field label="Akcja — co widzimy">
        <CommitText
          multiline
          rows={3}
          value={scene.action}
          placeholder="Stoi w kuchni, patrzy na butelkę wody i się waha."
          onCommit={(action) => update({ action })}
        />
      </Field>
      <Field label="Kamera — opis kadru">
        <CommitText
          value={scene.camera}
          placeholder="plan średni, powolny najazd"
          onCommit={(camera) => update({ camera })}
        />
      </Field>
      <div className="two-fields">
        <Field label="Ruch kamery">
          <select
            value={scene.motion?.camera || "static"}
            onChange={(e) =>
              update({
                motion: {
                  strength: scene.motion?.strength ?? 0.5,
                  camera: e.target.value as CameraMove,
                },
              })
            }
          >
            {Object.entries(cameraLabels).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Siła ruchu">
          <input
            type="range"
            min={0.1}
            max={1}
            step={0.1}
            defaultValue={scene.motion?.strength ?? 0.5}
            onPointerUp={(e) =>
              update({
                motion: {
                  camera: scene.motion?.camera || "static",
                  strength: Number(e.currentTarget.value),
                },
              })
            }
          />
        </Field>
      </div>
      <div className="inspector-section">
        <strong>Narracja i dialog</strong>
        {scene.dialogue.map((line, index) => (
          <div key={line.id || index} className="line-row">
            <div className="line-top">
              <select
                aria-label="Mówca"
                value={line.speaker}
                onChange={(e) => setLine(index, { speaker: e.target.value })}
              >
                <option value="narrator">Narrator</option>
                {bank.characters.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <CommitText
                value={line.direction}
                placeholder="jak mówi (szept, zmęczony…)"
                onCommit={(direction) => setLine(index, { direction })}
              />
              <IconButton
                icon={X}
                label="Usuń kwestię"
                onClick={() => update({ dialogue: scene.dialogue.filter((_, i) => i !== index) })}
              />
            </div>
            <CommitText
              multiline
              rows={2}
              value={line.text}
              onCommit={(text) => setLine(index, { text })}
            />
          </div>
        ))}
        <Button
          icon={Plus}
          subtle
          onClick={() =>
            update({
              dialogue: [...scene.dialogue, { speaker: "narrator", text: "", direction: "" }],
            })
          }
        >
          Dodaj kwestię
        </Button>
      </div>
      <div className="inspector-section">
        <strong>Dźwięk</strong>
        {cues.map((cue, index) => {
          const sound = sceneSounds.find((x) => x.id === cue.sound_id);
          return (
            <div key={index} className="cue-row">
              <select
                aria-label="Dźwięk"
                value={cue.sound_id}
                onChange={(e) => {
                  const next = sceneSounds.find((x) => x.id === e.target.value);
                  setCue(index, {
                    sound_id: e.target.value,
                    ...(next && next.kind !== sound?.kind ? { volume: next.kind === "ambience" ? 0.15 : 1 } : {}),
                  });
                }}
              >
                {sceneSounds.map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.kind === "ambience" ? "Atmosfera: " : "Efekt: "}
                    {x.name}
                  </option>
                ))}
              </select>
              <IconButton
                icon={Play}
                label="Odsłuchaj"
                onClick={() => sound && void new Audio(castAudio(sound.channel_id, sound.file)).play()}
              />
              <IconButton icon={X} label="Usuń dźwięk" onClick={() => update({ audio: cues.filter((_, i) => i !== index) })} />
              {sound?.kind === "sfx" && (
                <label className="small muted cue-wide">
                  moment: {Math.round(cue.at * 100)}% sceny
                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    defaultValue={cue.at}
                    onPointerUp={(e) => setCue(index, { at: Number(e.currentTarget.value) })}
                    onKeyUp={(e) => setCue(index, { at: Number(e.currentTarget.value) })}
                  />
                </label>
              )}
              <label className="small muted cue-wide">
                głośność: {Math.round(cue.volume * 100)}%
                <input
                  type="range"
                  min={0}
                  max={2}
                  step={0.05}
                  defaultValue={cue.volume}
                  onPointerUp={(e) => setCue(index, { volume: Number(e.currentTarget.value) })}
                  onKeyUp={(e) => setCue(index, { volume: Number(e.currentTarget.value) })}
                />
              </label>
            </div>
          );
        })}
        <Button
          icon={Plus}
          subtle
          disabled={!sceneSounds.length || cues.length >= 20}
          onClick={() =>
            update({
              // Ambience sits far under the voices; the director turned the first ones down to ~5%.
              audio: [...cues, { sound_id: sceneSounds[0].id, at: 0, volume: sceneSounds[0].kind === "ambience" ? 0.15 : 1 }],
            })
          }
        >
          {sceneSounds.length ? "Dodaj efekt lub atmosferę" : "Bank dźwięków kanału jest pusty"}
        </Button>
        <span className="muted small">Notatki dźwiękowe (dla AI i dźwiękowca):</span>
        <Field label="Atmosfera">
          <CommitText
            value={scene.sound.ambience}
            placeholder="cisza mieszkania, odległe syreny"
            onCommit={(ambience) => update({ sound: { ...scene.sound, ambience } })}
          />
        </Field>
        <Field label="Muzyka">
          <CommitText
            value={scene.sound.music}
            placeholder="napięcie, niskie smyczki"
            onCommit={(music) => update({ sound: { ...scene.sound, music } })}
          />
        </Field>
        <Field label="Efekty (po przecinku)">
          <CommitText
            value={scene.sound.sfx.join(", ")}
            placeholder="kapanie, trzy stuknięcia"
            onCommit={(v) =>
              update({
                sound: {
                  ...scene.sound,
                  sfx: v.split(",").map((x) => x.trim()).filter(Boolean),
                },
              })
            }
          />
        </Field>
      </div>
    </aside>
  );
}

/** Warnings when something visible disappears or changes between consecutive scenes in one place. */
function continuity(scene: StageScene, before: StageScene | undefined, bank: CastBank) {
  if (!before || before.location_id !== scene.location_id || !scene.location_id) return [];
  const name = (id: string) =>
    bank.items?.find((i) => i.id === id)?.name ||
    bank.characters.find((c) => c.id === id)?.name ||
    "?";
  const warnings: string[] = [];
  for (const prop of before.props || [])
    if (!(scene.props || []).some((x) => x.item_id === prop.item_id))
      warnings.push(`w poprzedniej scenie był „${name(prop.item_id)}” — czy ma zniknąć?`);
  for (const actor of scene.characters) {
    const earlier = before.characters.find((c) => c.character_id === actor.character_id);
    if (earlier && (earlier.costume_id || "") !== (actor.costume_id || ""))
      warnings.push(`${name(actor.character_id)} zmienia strój względem poprzedniej sceny.`);
  }
  return warnings;
}
