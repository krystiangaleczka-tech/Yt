import { useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Scissors,
  Trash2,
  Copy,
  Undo2,
  Redo2,
  Plus,
  Type,
  Sparkles,
  Volume2,
  VolumeX,
  LockKeyhole,
  Unlock,
  Magnet,
  ZoomIn,
  ZoomOut,
  Check,
  Image as ImageIcon,
  Music2,
  Film,
  Maximize2,
  X,
  ListMinus,
} from "lucide-react";
import { useStudio } from "./context";
import { api, id, mediaUrl } from "./api";
import {
  AssetThumb,
  Button,
  CommitText,
  Field,
  IconButton,
  NumberField,
  Modal,
} from "./components";
import type {
  Clip,
  Project,
  Proposal,
  Track,
  Keyframe,
  Job,
  Operation,
} from "./types";
import { fps, time, totalFrames, newClip, proposalPreview } from "./timing";
import { animations } from "./Generation";
import Preview from "./Preview";

type Drag = {
  id: string;
  edge: "move" | "left" | "right";
  x: number;
  original: Clip;
  changed: Clip;
};
export default function Timeline() {
  const s = useStudio(),
    p = s.project!;
  const [frame, setFrame] = useState(0),
    [playing, setPlaying] = useState(false),
    [selected, setSelected] = useState<string | null>(null),
    [zoom, setZoom] = useState(42),
    [snap, setSnap] = useState(true),
    [drag, setDrag] = useState<Drag | null>(null),
    [assistant, setAssistant] = useState(false),
    [library, setLibrary] = useState(true),
    [history, setHistory] = useState({ undo: 0, redo: 0 }),
    [large, setLarge] = useState(false),
    [proposed, setProposed] = useState<Proposal | null>(null);
  const dragRef = useRef<Drag | null>(null),
    rulerRef = useRef<HTMLDivElement>(null);
  const rate = fps(p),
    total = totalFrames(p),
    active = p.sequence.clips.find((c) => c.id === selected),
    activeTrack = p.sequence.tracks.find((t) => t.id === active?.track_id),
    locked = !!(active?.locked || activeTrack?.locked);
  const renderProject = useMemo(
    () =>
      drag
        ? {
            ...p,
            sequence: {
              ...p.sequence,
              clips: p.sequence.clips.map((c) =>
                c.id === drag.id ? drag.changed : c,
              ),
            },
          }
        : proposed
          ? proposalPreview(p, proposed.operations)
          : p,
    [p, drag, proposed],
  );
  useEffect(() => {
    s.run(async () => setHistory(await api("/projects/" + p.id + "/history")));
  }, [p.revision]);
  useEffect(() => {
    if (frame > total) setFrame(total);
  }, [total]);
  useEffect(() => setProposed(null), [p.revision]);
  function change(changes: Partial<Clip>) {
    if (!active) return;
    s.run(() =>
      s.edit([
        {
          type: "update_clip",
          clip_id: active.id,
          changes: changes as Record<string, unknown>,
        },
      ]),
    );
  }
  async function undo(direction: "undo" | "redo") {
    await s.mutate((current) =>
      api<Project>("/projects/" + current.id + "/history/" + direction, {
        expected_revision: current.revision,
      }),
    );
  }
  async function addAsset(assetId: string) {
    const a = p.assets.find((a) => a.id === assetId)!;
    const track = a.kind === "audio" ? "a2" : "v1";
    const c = newClip(
      track,
      a.id,
      frame,
      a.duration ? Math.floor(a.duration * rate) : 180,
    );
    c.title = a.name;
    await s.edit([{ type: "add_clip", clip: c }]);
    setSelected(c.id);
  }
  async function text() {
    const c = newClip("t1", null, frame, Math.round(rate * 4));
    c.title = "Nowy napis";
    c.text = "Twoja historia";
    await s.edit([{ type: "add_clip", clip: c }]);
    setSelected(c.id);
  }
  async function duplicate() {
    if (!active) return;
    const c = {
      ...active,
      id: id("clip_"),
      start: active.start + active.duration,
    };
    await s.edit([{ type: "add_clip", clip: c }]);
    setSelected(c.id);
  }
  async function split() {
    if (active)
      await s.edit([{ type: "split_clip", clip_id: active.id, frame }]);
  }
  async function preview() {
    await api<Job>("/projects/" + p.id + "/render", {
      expected_revision: p.revision,
      quality: "preview",
      mode: "draft",
    });
    s.notify("Dokładny podgląd jest w kolejce. Otworzysz go w Zadaniach.");
  }
  function startDrag(
    event: PointerEvent<HTMLElement>,
    clip: Clip,
    edge: Drag["edge"],
  ) {
    event.stopPropagation();
    if (event.button !== 0) return;
    setSelected(clip.id);
    setPlaying(false);
    if (
      clip.locked ||
      p.sequence.tracks.find((t) => t.id === clip.track_id)?.locked
    )
      return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    const d = {
      id: clip.id,
      edge,
      x: event.clientX,
      original: clip,
      changed: clip,
    };
    dragRef.current = d;
    setDrag(d);
  }
  function moveDrag(event: PointerEvent<HTMLElement>) {
    const d = dragRef.current;
    if (!d) return;
    const delta = Math.round(((event.clientX - d.x) / zoom) * rate),
      c = { ...d.original };
    let next = Math.max(0, d.original.start + delta);
    if (snap) {
      const edges = [
        0,
        frame,
        ...p.sequence.clips
          .filter((x) => x.id !== c.id)
          .flatMap((x) => [x.start, x.start + x.duration]),
      ];
      for (const edge of edges) {
        if (Math.abs(next - edge) < (rate / zoom) * 7) {
          next = edge;
          break;
        }
        if (
          d.edge === "move" &&
          Math.abs(next + c.duration - edge) < (rate / zoom) * 7
        ) {
          next = Math.max(0, edge - c.duration);
          break;
        }
      }
    }
    if (d.edge === "move") c.start = next;
    else if (d.edge === "left") {
      const shift = Math.min(
        c.duration - 1,
        Math.max(-c.source_in / c.speed, next - c.start),
      );
      c.start += Math.round(shift);
      c.duration -= Math.round(shift);
      c.source_in += Math.round(shift * c.speed);
    } else c.duration = Math.max(1, c.duration + delta);
    const asset = p.assets.find((a) => a.id === c.asset_id);
    if (asset?.duration && d.edge === "right")
      c.duration = Math.max(
        1,
        Math.min(
          c.duration,
          Math.floor((asset.duration * rate - c.source_in) / c.speed),
        ),
      );
    dragRef.current = { ...d, changed: c };
    setDrag(dragRef.current);
  }
  function endDrag() {
    const d = dragRef.current;
    if (!d) return;
    dragRef.current = null;
    setDrag(null);
    if (JSON.stringify(d.original) !== JSON.stringify(d.changed))
      s.run(() =>
        s.edit([
          {
            type: d.edge === "move" ? "move_clip" : "trim_clip",
            clip_id: d.id,
            changes: {
              start: d.changed.start,
              duration: d.changed.duration,
              source_in: d.changed.source_in,
            },
          },
        ]),
      );
  }
  const width = Math.max(650, (total / rate) * zoom + 150),
    step = zoom >= 60 ? 1 : zoom >= 25 ? 5 : 10;
  const ticks = Array.from(
    { length: Math.floor(width / zoom / step) + 1 },
    (_, i) => i * step,
  );
  function trackChange(track: Track, changes: Partial<Track>) {
    s.run(() =>
      s.edit([{ type: "update_track", track_id: track.id, changes }]),
    );
  }
  return (
    <div className="editing-page">
      <div className="editor-topbar">
        <div className="editor-heading">
          <h1>Montaż</h1>
          <span className="badge quiet">Sekwencja główna</span>
        </div>
        <div className="editor-top-actions">
          <Button subtle icon={ImageIcon} onClick={() => setLibrary(!library)}>
            Materiały
          </Button>
          <Button
            icon={Sparkles}
            className={assistant ? "selected-button" : ""}
            onClick={() => {
              setAssistant(!assistant);
              setProposed(null);
            }}
          >
            Asystent AI
          </Button>
          <Button primary icon={Play} onClick={() => s.run(preview)}>
            Dokładny podgląd
          </Button>
        </div>
      </div>
      <div
        className={`editing-upper ${library ? "with-library" : ""} ${assistant ? "with-assistant" : ""}`}
      >
        {library && (
          <section className="editor-media surface">
            <div className="panel-heading">
              <h2>Materiały</h2>
              <span className="badge quiet">{p.assets.length}</span>
            </div>
            <div className="editor-media-grid">
              {p.assets
                .filter((a) => a.kind !== "document")
                .map((a) => (
                  <button
                    key={a.id}
                    onClick={() => s.run(() => addAsset(a.id))}
                    title={"Dodaj do osi: " + a.name}
                  >
                    <AssetThumb asset={a} project={p} />
                    <span>{a.name}</span>
                    <Plus className="asset-add" size={15} />
                  </button>
                ))}
            </div>
            <Button subtle icon={Plus} onClick={() => s.setPage("library")}>
              Dodaj materiały
            </Button>
          </section>
        )}
        <section className="editor-player surface">
          <div className="preview-heading">
            <span>PODGLĄD ROBOCZY</span>
            <span>
              {p.sequence.width} × {p.sequence.height} ·{" "}
              {rate.toFixed(rate % 1 ? 2 : 0)} fps
            </span>
          </div>
          <div className="canvas-wrapper">
            <Preview
              project={renderProject}
              frame={frame}
              playing={playing}
              onFrame={setFrame}
              onEnded={() => setPlaying(false)}
            />
          </div>
          <div className="editor-seek">
            <input
              type="range"
              aria-label="Pozycja podglądu"
              min={0}
              max={Math.max(1, total - 1)}
              value={frame}
              onChange={(e) => {
                setPlaying(false);
                setFrame(Number(e.target.value));
              }}
            />
          </div>
          <div className="player-toolbar">
            <IconButton
              icon={SkipBack}
              label="Początek filmu"
              onClick={() => {
                setPlaying(false);
                setFrame(0);
              }}
            />
            <IconButton
              icon={playing ? Pause : Play}
              label={playing ? "Zatrzymaj" : "Odtwórz film"}
              onClick={() => {
                if (total) setPlaying(!playing);
              }}
            />
            <IconButton
              icon={SkipForward}
              label="Koniec filmu"
              onClick={() => {
                setPlaying(false);
                setFrame(Math.max(0, total - 1));
              }}
            />
            <span className="timecode">
              {time(frame, rate, true)} <span>/ {time(total, rate, true)}</span>
            </span>
            <div className="player-spacer" />
            <IconButton
              icon={Maximize2}
              label="Powiększ podgląd"
              onClick={() => {
                setPlaying(false);
                setLarge(true);
              }}
            />
          </div>
        </section>
        {assistant ? (
          <Assistant
            selected={selected ? [selected] : []}
            onClose={() => {
              setAssistant(false);
              setProposed(null);
            }}
            onPreview={setProposed}
          />
        ) : (
          <section className="clip-inspector surface">
            <div className="panel-heading">
              <h2>Inspektor</h2>
              {active && (
                <IconButton
                  icon={active.locked ? LockKeyhole : Unlock}
                  label={active.locked ? "Odblokuj klip" : "Zablokuj klip"}
                  onClick={() => change({ locked: !active.locked })}
                />
              )}
            </div>
            {active ? (
              <>
                <Field label="Nazwa klipu">
                  <CommitText
                    value={active.title}
                    onCommit={(v) => change({ title: v })}
                    disabled={locked}
                  />
                </Field>
                {activeTrack?.kind === "text" && (
                  <Field label="Tekst na ekranie">
                    <CommitText
                      multiline
                      rows={3}
                      value={active.text}
                      onCommit={(v) => change({ text: v })}
                      disabled={locked}
                    />
                  </Field>
                )}
                <div className="two-fields">
                  <NumberField
                    label="Początek (s)"
                    value={active.start / rate}
                    onCommit={(v) => change({ start: Math.round(v * rate) })}
                    disabled={locked}
                  />
                  <NumberField
                    label="Długość (s)"
                    value={active.duration / rate}
                    min={1 / rate}
                    onCommit={(v) => change({ duration: Math.round(v * rate) })}
                    disabled={locked}
                  />
                </div>
                <NumberField
                  label="W materiale od (s)"
                  value={active.source_in / rate}
                  onCommit={(v) => change({ source_in: Math.round(v * rate) })}
                  disabled={locked}
                />
                {activeTrack?.kind === "audio" ? (
                  <>
                    <NumberField
                      label="Głośność"
                      value={active.volume}
                      max={4}
                      onCommit={(v) => change({ volume: v })}
                      disabled={locked}
                    />
                    <NumberField
                      label="Prędkość"
                      value={active.speed}
                      min={0.25}
                      max={4}
                      onCommit={(v) => change({ speed: v })}
                      disabled={locked}
                    />
                  </>
                ) : (
                  <>
                    <div className="panel-divider" />
                    <div className="inspector-label">TRANSFORMACJA</div>
                    <div className="two-fields">
                      <NumberField
                        label="Pozycja X"
                        value={active.x}
                        min={-2}
                        max={2}
                        step={0.01}
                        onCommit={(v) => change({ x: v })}
                        disabled={locked}
                      />
                      <NumberField
                        label="Pozycja Y"
                        value={active.y}
                        min={-2}
                        max={2}
                        step={0.01}
                        onCommit={(v) => change({ y: v })}
                        disabled={locked}
                      />
                      <NumberField
                        label="Skala"
                        value={active.scale}
                        min={0.05}
                        max={5}
                        step={0.05}
                        onCommit={(v) => change({ scale: v })}
                        disabled={locked}
                      />
                      <NumberField
                        label="Obrót (°)"
                        value={active.rotation}
                        min={-360}
                        max={360}
                        step={1}
                        onCommit={(v) => change({ rotation: v })}
                        disabled={locked}
                      />
                    </div>
                    <NumberField
                      label="Krycie"
                      value={active.opacity}
                      max={1}
                      step={0.05}
                      onCommit={(v) => change({ opacity: v })}
                      disabled={locked}
                    />
                    <Field label="Ruch">
                      <select
                        value={active.animation}
                        disabled={locked}
                        onChange={(e) =>
                          change({
                            animation: e.target.value as Clip["animation"],
                          })
                        }
                      >
                        {animations.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.name}
                          </option>
                        ))}
                      </select>
                    </Field>
                    {p.assets.find((a) => a.id === active.asset_id)?.kind ===
                      "video" && (
                      <NumberField
                        label="Prędkość"
                        value={active.speed}
                        min={0.25}
                        max={4}
                        onCommit={(v) => change({ speed: v })}
                        disabled={locked}
                      />
                    )}
                  </>
                )}
                <div className="two-fields">
                  <NumberField
                    label="Wejście (s)"
                    value={active.fade_in / rate}
                    max={active.duration / rate}
                    onCommit={(v) => change({ fade_in: Math.round(v * rate) })}
                    disabled={locked}
                  />
                  <NumberField
                    label="Wyjście (s)"
                    value={active.fade_out / rate}
                    max={active.duration / rate}
                    onCommit={(v) => change({ fade_out: Math.round(v * rate) })}
                    disabled={locked}
                  />
                </div>
                <Keyframes
                  clip={active}
                  frame={frame}
                  disabled={locked}
                  onChange={(keyframes) => change({ keyframes })}
                />
              </>
            ) : (
              <div className="inspector-empty">
                <SlidersIcon />
                <h3>Wybierz klip</h3>
                <p>Zmienisz tu czas, ruch, obraz i dźwięk.</p>
              </div>
            )}
          </section>
        )}
      </div>
      <section className="timeline-panel surface">
        <div className="timeline-toolbar">
          <div className="timeline-tool-group">
            <IconButton
              icon={Undo2}
              label="Cofnij"
              disabled={!history.undo || s.saving}
              onClick={() => s.run(() => undo("undo"))}
            />
            <IconButton
              icon={Redo2}
              label="Ponów"
              disabled={!history.redo || s.saving}
              onClick={() => s.run(() => undo("redo"))}
            />
            <span className="tool-separator" />
            <IconButton
              icon={Scissors}
              label="Podziel klip w pozycji kursora"
              disabled={
                !active ||
                locked ||
                frame <= active.start ||
                frame >= active.start + active.duration
              }
              onClick={() => s.run(split)}
            />
            <IconButton
              icon={Copy}
              label="Duplikuj klip"
              disabled={!active || locked}
              onClick={() => s.run(duplicate)}
            />
            <IconButton
              icon={Trash2}
              label="Usuń klip"
              disabled={!active || locked}
              onClick={() =>
                s.run(() =>
                  s.edit([{ type: "remove_clip", clip_id: active!.id }]),
                )
              }
            />
            <IconButton
              icon={ListMinus}
              label="Usuń klip i zamknij lukę na ścieżce"
              disabled={!active || locked}
              onClick={() =>
                s.run(() =>
                  s.edit([{ type: "ripple_remove", clip_id: active!.id }]),
                )
              }
            />
            <span className="tool-separator" />
            <Button subtle icon={Type} onClick={() => s.run(text)}>
              Napis
            </Button>
          </div>
          <div className="timeline-tool-group">
            <button
              className={`icon-button ${snap ? "toggled" : ""}`}
              aria-label="Przyciąganie"
              aria-pressed={snap}
              onClick={() => setSnap(!snap)}
            >
              <Magnet size={17} />
            </button>
            <IconButton
              icon={ZoomOut}
              label="Oddal oś"
              onClick={() => setZoom(Math.max(10, zoom - 10))}
            />
            <input
              className="timeline-zoom"
              type="range"
              aria-label="Powiększenie osi czasu"
              min={10}
              max={140}
              value={zoom}
              onChange={(e) => setZoom(Number(e.target.value))}
            />
            <IconButton
              icon={ZoomIn}
              label="Przybliż oś"
              onClick={() => setZoom(Math.min(140, zoom + 10))}
            />
            <span className="small muted">{time(total, rate)}</span>
          </div>
        </div>
        <div className="timeline-scroll">
          <div className="timeline-content" style={{ width: width + 146 }}>
            <div className="time-ruler-row">
              <div className="track-title-spacer">ŚCIEŻKI</div>
              <div
                className="time-ruler"
                ref={rulerRef}
                style={{ width }}
                onPointerDown={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setFrame(
                    Math.max(
                      0,
                      Math.min(
                        total - 1,
                        Math.round(((e.clientX - rect.left) / zoom) * rate),
                      ),
                    ),
                  );
                  setPlaying(false);
                }}
              >
                {ticks.map((t) => (
                  <span
                    className="ruler-tick"
                    style={{ left: t * zoom }}
                    key={t}
                  >
                    {time(t * rate, rate)}
                  </span>
                ))}
              </div>
            </div>
            {p.sequence.tracks.map((track) => (
              <div
                className={`timeline-track ${track.kind} ${track.locked ? "locked-track" : ""}`}
                key={track.id}
              >
                <div className="track-title">
                  <span>{track.name}</span>
                  <div>
                    <IconButton
                      icon={track.locked ? LockKeyhole : Unlock}
                      label={
                        track.locked
                          ? "Odblokuj " + track.name
                          : "Zablokuj " + track.name
                      }
                      onClick={() =>
                        trackChange(track, { locked: !track.locked })
                      }
                    />
                    <IconButton
                      icon={track.muted ? VolumeX : Volume2}
                      label={
                        track.muted
                          ? "Włącz " + track.name
                          : "Wycisz " + track.name
                      }
                      onClick={() =>
                        trackChange(track, { muted: !track.muted })
                      }
                    />
                  </div>
                </div>
                <div
                  className={`track-lane ${track.muted ? "muted-track" : ""}`}
                  style={{ width }}
                  onDoubleClick={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    setFrame(
                      Math.max(
                        0,
                        Math.round(((e.clientX - rect.left) / zoom) * rate),
                      ),
                    );
                  }}
                >
                  {renderProject.sequence.clips
                    .filter((c) => c.track_id === track.id)
                    .map((c) => (
                      <div
                        key={c.id}
                        className={`timeline-clip ${selected === c.id ? "selected" : ""} ${track.role} ${c.locked ? "locked-clip" : ""}`}
                        style={{
                          left: (c.start / rate) * zoom,
                          width: Math.max(4, (c.duration / rate) * zoom),
                        }}
                        onPointerDown={(e) => startDrag(e, c, "move")}
                        onPointerMove={moveDrag}
                        onPointerUp={endDrag}
                        onPointerCancel={endDrag}
                        onKeyDown={(e) => {
                          if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
                            e.preventDefault();
                            s.run(() =>
                              s.edit([
                                {
                                  type: "move_clip",
                                  clip_id: c.id,
                                  changes: {
                                    start: Math.max(
                                      0,
                                      c.start +
                                        (e.key === "ArrowRight" ? 1 : -1) *
                                          (e.shiftKey ? Math.round(rate) : 1),
                                    ),
                                  },
                                },
                              ]),
                            );
                          }
                          if (e.key === "Enter") setSelected(c.id);
                        }}
                        role="button"
                        tabIndex={0}
                        aria-label={c.title + " od " + time(c.start, rate)}
                      >
                        {track.kind === "video" && c.asset_id && (
                          <img
                            className="clip-thumbnail"
                            src={mediaUrl(p.id, c.asset_id, true)}
                            alt=""
                            draggable={false}
                            loading="lazy"
                          />
                        )}
                        <span
                          className="clip-trim left"
                          onPointerDown={(e) => startDrag(e, c, "left")}
                          role="button"
                          aria-label="Przytnij początek"
                        />
                        <span className="clip-title">
                          {track.kind === "audio" ? (
                            <Music2 size={12} />
                          ) : track.kind === "text" ? (
                            <Type size={12} />
                          ) : (
                            <Film size={12} />
                          )}
                          <span>{c.title}</span>
                          {c.locked && <LockKeyhole size={11} />}
                        </span>
                        <span
                          className="clip-trim right"
                          onPointerDown={(e) => startDrag(e, c, "right")}
                          role="button"
                          aria-label="Przytnij koniec"
                        />
                      </div>
                    ))}
                </div>
              </div>
            ))}
            <div
              className="playhead"
              style={{ left: 146 + (frame / rate) * zoom }}
            >
              <div />
            </div>
          </div>
        </div>
        <div className="timeline-bottom">
          <span>
            {proposed
              ? "Podgląd propozycji AI · zmiany czekają na przyjęcie"
              : "Przeciągnij klip lub jego krawędź · strzałki przesuwają o klatkę"}
          </span>
          <span>
            {p.sequence.clips.length} klipów · rewizja {p.revision}
          </span>
        </div>
      </section>
      <Modal
        open={large}
        onClose={() => setLarge(false)}
        title="Podgląd kompozycji"
        wide
      >
        <Preview
          project={p}
          frame={frame}
          playing={false}
          onFrame={setFrame}
          onEnded={() => {}}
        />
      </Modal>
    </div>
  );
}
function SlidersIcon() {
  return <Film size={27} />;
}
function Keyframes({
  clip,
  frame,
  disabled,
  onChange,
}: {
  clip: Clip;
  frame: number;
  disabled: boolean;
  onChange: (k: Keyframe[]) => void;
}) {
  const [prop, setProp] = useState<Keyframe["property"]>("scale");
  const at = Math.max(0, Math.min(clip.duration, frame - clip.start));
  function add() {
    const existing = clip.keyframes.filter(
      (k) => !(k.property === prop && k.frame === at),
    );
    onChange([...existing, { property: prop, frame: at, value: clip[prop] }]);
  }
  return (
    <details className="advanced">
      <summary>
        Punkty animacji{" "}
        <span className="badge quiet">{clip.keyframes.length}</span>
      </summary>
      <div className="keyframe-add">
        <select
          aria-label="Parametr punktu animacji"
          value={prop}
          onChange={(e) => setProp(e.target.value as Keyframe["property"])}
        >
          <option value="scale">Skala</option>
          <option value="x">Pozycja X</option>
          <option value="y">Pozycja Y</option>
          <option value="rotation">Obrót</option>
          <option value="opacity">Krycie</option>
          <option value="volume">Głośność</option>
        </select>
        <IconButton
          icon={Plus}
          label="Dodaj punkt w pozycji kursora"
          disabled={disabled}
          onClick={add}
        />
      </div>
      <p className="small muted">Klatka lokalna: {at}</p>
      {clip.keyframes.map((k, i) => (
        <div className="keyframe-row" key={i}>
          <span>
            {k.property}
            <small>f {k.frame}</small>
          </span>
          <input
            type="number"
            aria-label={"Wartość " + k.property + " w klatce " + k.frame}
            defaultValue={k.value}
            step="0.05"
            disabled={disabled}
            onBlur={(e) => {
              const value = Number(e.target.value);
              if (Number.isFinite(value))
                onChange(
                  clip.keyframes.map((x, n) => (n === i ? { ...x, value } : x)),
                );
            }}
          />
          <IconButton
            icon={X}
            label="Usuń punkt"
            disabled={disabled}
            onClick={() => onChange(clip.keyframes.filter((_, n) => n !== i))}
          />
        </div>
      ))}
    </details>
  );
}

function Assistant({
  selected,
  onClose,
  onPreview,
}: {
  selected: string[];
  onClose: () => void;
  onPreview: (p: Proposal | null) => void;
}) {
  const s = useStudio(),
    p = s.project!;
  const [command, setCommand] = useState(""),
    [scope, setScope] = useState("selection"),
    [response, setResponse] = useState(""),
    [proposal, setProposal] = useState<Proposal | null>(null),
    [busy, setBusy] = useState(false),
    [prompt, setPrompt] = useState("");
  const selection = scope === "selection" ? selected : [];
  async function copy() {
    const result = await api<{ prompt: string }>(
      "/projects/" + p.id + "/assistant/prompt",
      { command, selection },
    );
    setPrompt(result.prompt);
    try {
      await navigator.clipboard.writeText(result.prompt);
      s.notify("Prompt montażu skopiowany");
    } catch {
      s.notify("Skopiuj prompt z pola poniżej");
    }
  }
  async function propose(manual = false) {
    setBusy(true);
    try {
      const result = await api<Proposal>(
        "/projects/" + p.id + "/assistant/propose",
        { command, selection, ...(manual ? { response } : {}) },
      );
      setProposal(result);
    } finally {
      setBusy(false);
    }
  }
  async function accept() {
    if (!proposal) return;
    await s.edit(proposal.operations, "ai", proposal.base_revision);
    setProposal(null);
    s.notify("Przyjęto montaż AI. Możesz cofnąć całą serię zmian.");
  }
  return (
    <section className="assistant-panel surface">
      <div className="panel-heading">
        <h2>
          <Sparkles size={16} />
          Asystent montażu
        </h2>
        <IconButton icon={X} label="Zamknij asystenta" onClick={onClose} />
      </div>
      <div className="ai-intro">
        <span className="ai-orb">
          <Sparkles size={23} />
        </span>
        <strong>Ty nadajesz kierunek.</strong>
        <p>Opisz zmianę. Sprawdzisz ją przed zastosowaniem.</p>
      </div>
      <Field label="Co zmienić?">
        <textarea
          rows={4}
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Skróć otwarcie. Zachowaj lektora i dodaj delikatne najazdy."
        />
      </Field>
      <Field label="Zakres">
        <select value={scope} onChange={(e) => setScope(e.target.value)}>
          <option value="selection">
            Zaznaczony klip {selected.length ? "" : "· brak"}
          </option>
          <option value="all">Cały film</option>
        </select>
      </Field>
      <Button
        primary
        icon={Sparkles}
        busy={busy}
        disabled={
          !command.trim() || (scope === "selection" && !selected.length)
        }
        onClick={() => s.run(() => propose())}
      >
        Zaproponuj zmiany
      </Button>
      <div className="lock-hint">
        <LockKeyhole size={13} />
        <span>AI respektuje blokady ścieżek i klipów.</span>
      </div>
      <details className="advanced">
        <summary>Użyj własnego AI</summary>
        <Button subtle icon={Copy} onClick={() => s.run(copy)}>
          Kopiuj prompt
        </Button>
        {prompt && <textarea readOnly rows={5} value={prompt} />}
        <textarea
          rows={5}
          value={response}
          onChange={(e) => setResponse(e.target.value)}
          placeholder="Wklej JSON z operations…"
        />
        <Button
          icon={Check}
          disabled={!response.trim()}
          onClick={() => s.run(() => propose(true))}
        >
          Sprawdź propozycję
        </Button>
      </details>
      {proposal && (
        <div className="proposal">
          <div className="eyebrow">
            PROPOZYCJA · REWIZJA {proposal.base_revision}
          </div>
          <p>{proposal.description}</p>
          <ul>
            {proposal.operations.map((op, i) => (
              <li key={i}>{operationLabel(op, p)}</li>
            ))}
          </ul>
          <Button
            icon={Play}
            disabled={
              !proposal.operations.length ||
              proposal.base_revision !== p.revision
            }
            onClick={() => onPreview(proposal)}
          >
            Pokaż na osi czasu
          </Button>
          <Button
            primary
            icon={Check}
            disabled={
              !proposal.operations.length ||
              proposal.base_revision !== p.revision
            }
            onClick={() => s.run(accept)}
          >
            Zastosuj {proposal.operations.length} zmian
          </Button>
          {proposal.base_revision !== p.revision && (
            <p className="small warning-text">
              Projekt zmienił się. Przygotuj nową propozycję.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
function operationLabel(op: Operation, p: Project) {
  const title =
    p.sequence.clips.find((c) => c.id === op.clip_id)?.title ||
    op.clip?.title ||
    "Klip";
  if (op.type === "split_clip")
    return `Podziel „${title}” przy ${time(op.frame || 0, fps(p))}`;
  if (op.type === "remove_clip") return `Usuń „${title}”`;
  if (op.type === "add_clip") return `Dodaj „${title}”`;
  return `${title}: ${Object.entries(op.changes || {})
    .map(([k, v]) => `${k} → ${typeof v === "object" ? "punkty animacji" : v}`)
    .join(", ")}`;
}
