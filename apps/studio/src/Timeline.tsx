import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type {
  Dispatch,
  KeyboardEvent,
  PointerEvent,
  SetStateAction,
} from "react";
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
  Maximize,
  Minimize,
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
import { JSONField } from "./Production";

type Drag = {
  id: string;
  edge: "move" | "left" | "right";
  x: number;
  original: Clip;
  changed: Clip;
};
type LaneWindow = { from: number; to: number };
const TITLE_WIDTH = 146,
  LANE_CHUNK = 1200;

/** Stała tożsamość funkcji, która zawsze woła najnowszą wersję — memo-komponenty nie renderują się co klatkę. */
function useStable<A extends unknown[], R>(fn: (...args: A) => R) {
  const ref = useRef(fn);
  ref.current = fn;
  return useCallback((...args: A) => ref.current(...args), []);
}
/** Widoczny fragment ścieżek (w pikselach osi) z zapasem; zmienia się dopiero po przekroczeniu kawałka. */
function laneWindow(el: HTMLDivElement | null): LaneWindow {
  const left = el ? el.scrollLeft - TITLE_WIDTH : 0,
    width = el?.clientWidth || 2400;
  return {
    from: Math.floor(left / LANE_CHUNK) * LANE_CHUNK - LANE_CHUNK,
    to: Math.ceil((left + width) / LANE_CHUNK) * LANE_CHUNK + LANE_CHUNK,
  };
}
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
    [full, setFull] = useState(false),
    [idle, setIdle] = useState(false),
    [proposed, setProposed] = useState<Proposal | null>(null);
  const [marked, setMarked] = useState<string[]>([]),
    [rangeStart, setRangeStart] = useState(0),
    [rangeEnd, setRangeEnd] = useState(0),
    [exact, setExact] = useState(false);
  const dragRef = useRef<Drag | null>(null),
    scrollRef = useRef<HTMLDivElement>(null),
    playerRef = useRef<HTMLElement>(null),
    idleTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined),
    stillRef = useRef(frame);
  const [view, setView] = useState<LaneWindow>(() => laneWindow(null));
  // Inspektor dostaje klatkę tylko poza odtwarzaniem — w czasie Play nie przerysowuje się 30 razy na sekundę.
  if (!playing) stillRef.current = frame;
  const stillFrame = stillRef.current;
  // Pełny ekran obejmuje cały odtwarzacz (obraz, pasek i przyciski), więc odtwarzanie nie przerywa się przy wejściu.
  useEffect(() => {
    const changed = () =>
      setFull(
        !!playerRef.current && document.fullscreenElement === playerRef.current,
      );
    document.addEventListener("fullscreenchange", changed);
    return () => {
      document.removeEventListener("fullscreenchange", changed);
      if (playerRef.current && document.fullscreenElement === playerRef.current)
        void document.exitFullscreen().catch(() => {});
    };
  }, []);
  function toggleFull() {
    if (document.fullscreenElement) {
      void document.exitFullscreen().catch(() => {});
      return;
    }
    const el = playerRef.current;
    if (!el?.requestFullscreen) {
      s.notify("Przeglądarka nie obsługuje pełnego ekranu", true);
      return;
    }
    el.requestFullscreen()
      .then(() => el.focus({ preventScroll: true }))
      .catch(() => s.notify("Przeglądarka nie pozwoliła na pełny ekran", true));
  }
  // Na pełnym ekranie w czasie odtwarzania przyciski chowają się po chwili bez ruchu myszy.
  function wake() {
    setIdle(false);
    clearTimeout(idleTimer.current);
    if (full && playing)
      idleTimer.current = setTimeout(() => setIdle(true), 2500);
  }
  useEffect(() => {
    wake();
    return () => clearTimeout(idleTimer.current);
  }, [full, playing]);
  const rate = fps(p),
    total = totalFrames(p),
    active = p.sequence.clips.find((c) => c.id === selected),
    activeTrack = p.sequence.tracks.find((t) => t.id === active?.track_id),
    locked = !!(
      active?.locked ||
      activeTrack?.locked ||
      p.scenes.find((scene) => scene.id === active?.scene_id)?.locked
    );
  const renderProject = useMemo(
    () =>
      drag
        ? {
            ...p,
            sequence: {
              ...p.sequence,
              clips: p.sequence.clips.map((c) =>
                c.id === drag.id
                  ? drag.changed
                  : drag.edge === "move" &&
                      drag.original.group_id &&
                      c.group_id === drag.original.group_id
                    ? {
                        ...c,
                        start:
                          c.start + drag.changed.start - drag.original.start,
                      }
                    : c,
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
  useEffect(() => {
    if (s.targetScene) {
      const c = p.sequence.clips.find(
        (c) => c.scene_id === s.targetScene && c.track_id === "v1",
      );
      if (c) {
        setSelected(c.id);
        setMarked([c.id]);
        setFrame(c.start);
        const el = scrollRef.current;
        if (el) el.scrollLeft = Math.max(0, (c.start / rate) * zoom - 160);
      }
    }
  }, []);
  useEffect(() => {
    if (active?.scene_id) s.setTargetScene(active.scene_id);
  }, [active?.scene_id]);
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const update = () =>
      setView((prev) => {
        const next = laneWindow(el);
        return next.from === prev.from && next.to === prev.to ? prev : next;
      });
    update();
    el.addEventListener("scroll", update, { passive: true });
    const resize = new ResizeObserver(update);
    resize.observe(el);
    return () => {
      el.removeEventListener("scroll", update);
      resize.disconnect();
    };
  }, []);
  // Oś podąża za kursorem w czasie odtwarzania (stronami, jak w programach montażowych).
  useEffect(() => {
    const el = scrollRef.current;
    if (!el || !playing) return;
    const x = (frame / rate) * zoom,
      right = el.scrollLeft + el.clientWidth - TITLE_WIDTH;
    if (x < el.scrollLeft || x > right - 24)
      el.scrollLeft = Math.max(0, x - 24);
  }, [frame, playing, zoom, rate]);
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
      ...(proposed ? { operations: proposed.operations } : {}),
      start_frame: rangeStart,
      ...(rangeEnd > rangeStart ? { end_frame: rangeEnd } : {}),
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
    if (event.metaKey || event.ctrlKey || event.shiftKey) {
      setMarked((ids) =>
        ids.includes(clip.id)
          ? ids.filter((x) => x !== clip.id)
          : [...ids, clip.id],
      );
      return;
    }
    setMarked(
      clip.group_id
        ? p.sequence.clips
            .filter((c) => c.group_id === clip.group_id)
            .map((c) => c.id)
        : [clip.id],
    );
    setPlaying(false);
    if (
      clip.locked ||
      p.sequence.tracks.find((t) => t.id === clip.track_id)?.locked ||
      p.scenes.find((s) => s.id === clip.scene_id)?.locked
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
  const width = Math.max(650, (total / rate) * zoom + 150);
  function trackChange(track: Track, changes: Partial<Track>) {
    s.run(() =>
      s.edit([{ type: "update_track", track_id: track.id, changes }]),
    );
  }
  // Stałe uchwyty dla ciężkich części (materiały, ścieżki, inspektor): zmiana klatki ich nie przerysowuje.
  const onDragStart = useStable(startDrag),
    onDragMove = useStable(moveDrag),
    onDragEnd = useStable(endDrag),
    onTrackChange = useStable(trackChange),
    changeClip = useStable(change),
    onAddAsset = useStable((assetId: string) => s.run(() => addAsset(assetId))),
    onOpenLibrary = useStable(() => s.setPage("library")),
    onSeek = useStable((at: number) => {
      setPlaying(false);
      setFrame(Math.max(0, Math.min(Math.max(0, total - 1), at)));
    }),
    onClipKey = useStable((e: KeyboardEvent<HTMLElement>, c: Clip) => {
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
      if (e.key === "Enter") {
        setSelected(c.id);
        setMarked(e.shiftKey ? [...marked, c.id] : [c.id]);
      }
    }),
    closeAssistant = useStable(() => {
      setAssistant(false);
      setProposed(null);
    });
  const assistantSelection = useMemo(
    () => (marked.length ? marked : selected ? [selected] : []),
    [marked, selected],
  );
  return (
    <div className="editing-page">
      <div className="editor-topbar">
        <div className="editor-heading">
          <h1>Montaż</h1>
          <span className="badge quiet">Sekwencja główna</span>
        </div>
        <div className="editor-top-actions">
          <Button subtle onClick={() => s.setPage("production")}>
            Wersje i narzędzia
          </Button>
          <Button
            onClick={() =>
              s.run(async () => {
                await api(`/projects/${p.id}/frame`, {
                  frame: Math.min(frame, total - 1),
                  expected_revision: p.revision,
                  ...(proposed ? { operations: proposed.operations } : {}),
                });
                setExact(true);
                s.notify("Dokładna klatka w kolejce");
              })
            }
            disabled={!total}
          >
            Dokładna klatka
          </Button>
          <Button icon={Film} onClick={() => s.setPage("motion")}>
            Dodaj wstawkę
          </Button>
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
          <MediaPanel
            project={p}
            onAdd={onAddAsset}
            onOpenLibrary={onOpenLibrary}
          />
        )}
        <section
          ref={playerRef}
          tabIndex={-1}
          className={`editor-player surface ${full ? "fullscreen" : ""} ${full && idle ? "idle" : ""}`}
          onMouseMove={full ? wake : undefined}
          onDoubleClick={(e) => {
            if ((e.target as HTMLElement).tagName === "CANVAS") toggleFull();
          }}
          onKeyDown={(e) => {
            if (!full || e.key !== " ") return;
            // Spacja na pełnym ekranie: Play/Pauza, także gdy fokus jest na przycisku.
            e.preventDefault();
            if (total) setPlaying((x) => !x);
            wake();
          }}
          onKeyUp={(e) => {
            if (full && e.key === " ") e.preventDefault();
          }}
        >
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
              maxWidth={full ? 1920 : 960}
            />
          </div>
          <div className="editor-controls">
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
                {time(frame, rate, true)}{" "}
                <span>/ {time(total, rate, true)}</span>
              </span>
              <div className="player-spacer" />
              <IconButton
                icon={full ? Minimize : Maximize}
                label={full ? "Wyjdź z pełnego ekranu (Esc)" : "Pełny ekran"}
                onClick={toggleFull}
              />
            </div>
          </div>
        </section>
        {assistant ? (
          <AssistantPanel
            selected={assistantSelection}
            onClose={closeAssistant}
            onPreview={setProposed}
          />
        ) : (
          <ClipInspector
            project={p}
            active={active}
            activeTrack={activeTrack}
            locked={locked}
            frame={stillFrame}
            marked={marked}
            setMarked={setMarked}
            change={changeClip}
          />
        )}
      </div>
      <section className="timeline-panel surface">
        <div className="timeline-toolbar">
          <div className="timeline-tool-group">
            <Button subtle onClick={() => setRangeStart(frame)}>
              IN {time(rangeStart, rate)}
            </Button>
            <Button subtle onClick={() => setRangeEnd(frame + 1)}>
              OUT {rangeEnd > rangeStart ? time(rangeEnd, rate) : "koniec"}
            </Button>
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
        <div className="timeline-scroll" ref={scrollRef}>
          <div
            className="timeline-content"
            style={{ width: width + TITLE_WIDTH }}
          >
            <TimelineBody
              project={renderProject}
              rate={rate}
              zoom={zoom}
              width={width}
              view={view}
              selected={selected}
              marked={marked}
              onSeek={onSeek}
              onDragStart={onDragStart}
              onDragMove={onDragMove}
              onDragEnd={onDragEnd}
              onClipKey={onClipKey}
              onTrackChange={onTrackChange}
            />
            <div
              className="playhead"
              style={{
                transform: `translateX(${TITLE_WIDTH + (frame / rate) * zoom}px)`,
              }}
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
        open={exact}
        onClose={() => setExact(false)}
        title="Dokładna klatka"
        description="Wynik tego samego kompozytora co finalny film"
      >
        {(() => {
          const job = s.jobs.find(
            (j) => j.project_id === p.id && j.kind === "frame",
          );
          return job?.status === "SUCCEEDED" && job.result?.url ? (
            <>
              <img
                className="full-preview"
                src={job.result.url}
                alt={`Klatka ${job.result.frame}`}
              />
              <p className="small muted">
                Klatka {job.result.frame} · rewizja {job.revision}
                {job.revision !== p.revision
                  ? " · wynik poprzedniej rewizji"
                  : ""}
              </p>
            </>
          ) : (
            <p>{job?.message || "Przygotowywanie klatki…"}</p>
          );
        })()}
      </Modal>
    </div>
  );
}
const ClipInspector = memo(function ClipInspector({
  project: p,
  active,
  activeTrack,
  locked,
  frame,
  marked,
  setMarked,
  change,
}: {
  project: Project;
  active: Clip | undefined;
  activeTrack: Track | undefined;
  locked: boolean;
  frame: number;
  marked: string[];
  setMarked: Dispatch<SetStateAction<string[]>>;
  change: (changes: Partial<Clip>) => void;
}) {
  const s = useStudio(),
    rate = fps(p);
  const [groupOpen, setGroupOpen] = useState(false);
  return (
    <section className="clip-inspector surface">
      {active?.template === "paper-theatre" && active.scene_id && (
        <Button
          onClick={() => {
            s.setTargetScene(active.scene_id!);
            s.setPage("paper-theatre");
          }}
        >
          Scenograf · układ i porównanie z referencją
        </Button>
      )}
      {active &&
        p.assets.find((a) => a.id === active.asset_id)?.provenance.kind ===
          "remotion" &&
        p.inserts.some(
          (i) =>
            i.id ===
            p.assets.find((a) => a.id === active.asset_id)?.provenance
              .insert_id,
        ) && (
          <Button
            icon={Film}
            onClick={() => {
              const asset = p.assets.find((a) => a.id === active.asset_id);
              s.setTargetInsert(String(asset?.provenance.insert_id));
              s.setPage("motion");
            }}
          >
            Edytuj źródło wstawki
          </Button>
        )}
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
          {activeTrack?.kind === "video" && (
            <>
              <Field label="Przejście na wejściu">
                <select
                  value={active.transition || "cut"}
                  disabled={locked}
                  onChange={(e) =>
                    change({
                      transition: e.target.value,
                      transition_duration:
                        e.target.value === "cut"
                          ? 0
                          : Math.min(active.duration, Math.round(rate * 0.5)),
                    })
                  }
                >
                  {[
                    ["cut", "Cięcie"],
                    ["dissolve", "Przenikanie"],
                    ["fade-black", "Z czerni"],
                    ["wipe-left", "Wycieranie w lewo"],
                    ["wipe-right", "Wycieranie w prawo"],
                    ["slide-left", "Przesunięcie w lewo"],
                    ["slide-right", "Przesunięcie w prawo"],
                    ["zoom", "Zbliżenie"],
                  ].map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </Field>
              <NumberField
                label="Długość przejścia (s)"
                value={(active.transition_duration || 0) / rate}
                max={active.duration / rate}
                onCommit={(v) =>
                  change({ transition_duration: Math.round(v * rate) })
                }
              />
              <JSONField
                label="Kadrowanie {x,y,width,height} 0–1"
                value={active.crop || {}}
                onSave={(v) => change({ crop: v as Record<string, number> })}
              />
            </>
          )}
          {active.asset_id &&
            p.assets.find((a) => a.id === active.asset_id)?.kind ===
              "video" && (
              <Button
                onClick={() =>
                  s.run(async () => {
                    await api(
                      `/projects/${p.id}/assets/${active.asset_id}/proxy`,
                      {},
                    );
                    s.notify("Proxy w kolejce");
                  })
                }
              >
                Przygotuj lekki proxy
              </Button>
            )}
          <details onToggle={(e) => setGroupOpen(e.currentTarget.open)}>
            <summary>Zaznacz klipy do grupy</summary>
            <div className="tool-options">
              {groupOpen &&
                p.sequence.clips.map((c) => (
                  <label key={c.id}>
                    <input
                      type="checkbox"
                      checked={marked.includes(c.id)}
                      onChange={(e) =>
                        setMarked((ids) =>
                          e.target.checked
                            ? [...ids, c.id]
                            : ids.filter((x) => x !== c.id),
                        )
                      }
                    />
                    {c.title} · {time(c.start, rate)}
                  </label>
                ))}
            </div>
          </details>
          <div className="button-row">
            <Button
              disabled={marked.length < 2}
              onClick={() =>
                s.run(() => s.edit([{ type: "group_clips", clip_ids: marked }]))
              }
            >
              Grupuj {marked.length}
            </Button>
            <Button
              disabled={!marked.length}
              onClick={() =>
                s.run(() =>
                  s.edit([{ type: "ungroup_clips", clip_ids: marked }]),
                )
              }
            >
              Rozgrupuj
            </Button>
          </div>
        </>
      ) : (
        <div className="inspector-empty">
          <SlidersIcon />
          <h3>Wybierz klip</h3>
          <p>Zmienisz tu czas, ruch, obraz i dźwięk.</p>
        </div>
      )}
    </section>
  );
});

const MEDIA_PAGE = 60;
const MediaPanel = memo(function MediaPanel({
  project: p,
  onAdd,
  onOpenLibrary,
}: {
  project: Project;
  onAdd: (assetId: string) => void;
  onOpenLibrary: () => void;
}) {
  const [query, setQuery] = useState(""),
    [limit, setLimit] = useState(MEDIA_PAGE);
  const list = useMemo(() => {
    const q = query.trim().toLowerCase();
    return p.assets.filter(
      (a) => a.kind !== "document" && (!q || a.name.toLowerCase().includes(q)),
    );
  }, [p.assets, query]);
  return (
    <section className="editor-media surface">
      <div className="panel-heading">
        <h2>Materiały</h2>
        <span className="badge quiet">{p.assets.length}</span>
      </div>
      {(list.length > MEDIA_PAGE || query) && (
        <input
          className="editor-media-search"
          type="search"
          aria-label="Szukaj w materiałach"
          placeholder="Szukaj materiału"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setLimit(MEDIA_PAGE);
          }}
        />
      )}
      <div className="editor-media-grid">
        {list.slice(0, limit).map((a) => (
          <button
            key={a.id}
            onClick={() => onAdd(a.id)}
            title={"Dodaj do osi: " + a.name}
          >
            <AssetThumb asset={a} project={p} />
            <span>{a.name}</span>
            <Plus className="asset-add" size={15} />
          </button>
        ))}
      </div>
      {list.length > limit && (
        <Button subtle onClick={() => setLimit(limit + MEDIA_PAGE * 2)}>
          Pokaż kolejne · zostało {list.length - limit}
        </Button>
      )}
      <Button subtle icon={Plus} onClick={onOpenLibrary}>
        Dodaj materiały
      </Button>
    </section>
  );
});

/** Linijka i ścieżki. Rysuje tylko klipy w widocznym fragmencie osi (plus zaznaczone), więc 700 ujęć nie spowalnia. */
const TimelineBody = memo(function TimelineBody({
  project: p,
  rate,
  zoom,
  width,
  view,
  selected,
  marked,
  onSeek,
  onDragStart,
  onDragMove,
  onDragEnd,
  onClipKey,
  onTrackChange,
}: {
  project: Project;
  rate: number;
  zoom: number;
  width: number;
  view: LaneWindow;
  selected: string | null;
  marked: string[];
  onSeek: (frame: number) => void;
  onDragStart: (
    e: PointerEvent<HTMLElement>,
    clip: Clip,
    edge: Drag["edge"],
  ) => void;
  onDragMove: (e: PointerEvent<HTMLElement>) => void;
  onDragEnd: () => void;
  onClipKey: (e: KeyboardEvent<HTMLElement>, clip: Clip) => void;
  onTrackChange: (track: Track, changes: Partial<Track>) => void;
}) {
  const step = zoom >= 60 ? 1 : zoom >= 25 ? 5 : 10;
  const ticks: number[] = [];
  for (
    let t = Math.max(0, Math.floor(view.from / zoom / step) * step);
    t * zoom <= Math.min(width, view.to);
    t += step
  )
    ticks.push(t);
  const byTrack = useMemo(() => {
    const lanes = new Map<string, Clip[]>();
    for (const c of p.sequence.clips) {
      const left = (c.start / rate) * zoom,
        right = left + Math.max(4, (c.duration / rate) * zoom);
      if (
        (right < view.from || left > view.to) &&
        c.id !== selected &&
        !marked.includes(c.id)
      )
        continue;
      const lane = lanes.get(c.track_id);
      if (lane) lane.push(c);
      else lanes.set(c.track_id, [c]);
    }
    return lanes;
  }, [p.sequence.clips, rate, zoom, view, selected, marked]);
  const at = (e: { clientX: number; currentTarget: Element }) =>
    Math.round(
      ((e.clientX - e.currentTarget.getBoundingClientRect().left) / zoom) *
        rate,
    );
  return (
    <>
      <div className="time-ruler-row">
        <div className="track-title-spacer">ŚCIEŻKI</div>
        <div
          className="time-ruler"
          style={{ width }}
          onPointerDown={(e) => onSeek(at(e))}
        >
          {ticks.map((t) => (
            <span className="ruler-tick" style={{ left: t * zoom }} key={t}>
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
              <button
                className={`icon-button ${track.solo ? "toggled" : ""}`}
                aria-label={`Solo ${track.name}`}
                aria-pressed={!!track.solo}
                onClick={() => onTrackChange(track, { solo: !track.solo })}
              >
                S
              </button>
              <IconButton
                icon={track.locked ? LockKeyhole : Unlock}
                label={
                  track.locked
                    ? "Odblokuj " + track.name
                    : "Zablokuj " + track.name
                }
                onClick={() => onTrackChange(track, { locked: !track.locked })}
              />
              <IconButton
                icon={track.muted ? VolumeX : Volume2}
                label={
                  track.muted ? "Włącz " + track.name : "Wycisz " + track.name
                }
                onClick={() => onTrackChange(track, { muted: !track.muted })}
              />
            </div>
          </div>
          <div
            className={`track-lane ${track.muted ? "muted-track" : ""}`}
            style={{ width }}
            onDoubleClick={(e) => onSeek(at(e))}
          >
            {(byTrack.get(track.id) || []).map((c) => (
              <div
                key={c.id}
                className={`timeline-clip ${marked.includes(c.id) || selected === c.id ? "selected" : ""} ${track.role} ${c.locked ? "locked-clip" : ""}`}
                style={{
                  left: (c.start / rate) * zoom,
                  width: Math.max(4, (c.duration / rate) * zoom),
                }}
                onPointerDown={(e) => onDragStart(e, c, "move")}
                onPointerMove={onDragMove}
                onPointerUp={onDragEnd}
                onPointerCancel={onDragEnd}
                onKeyDown={(e) => onClipKey(e, c)}
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
                {track.kind === "audio" && c.asset_id && (
                  <ClipWave projectId={p.id} assetId={c.asset_id} />
                )}
                <span
                  className="clip-trim left"
                  onPointerDown={(e) => onDragStart(e, c, "left")}
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
                  onPointerDown={(e) => onDragStart(e, c, "right")}
                  role="button"
                  aria-label="Przytnij koniec"
                />
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  );
});

function SlidersIcon() {
  return <Film size={27} />;
}
function ClipWave({
  projectId,
  assetId,
}: {
  projectId: string;
  assetId: string;
}) {
  const [peaks, setPeaks] = useState<number[]>([]);
  useEffect(() => {
    let active = true;
    api<{ peaks: number[] }>(
      `/projects/${projectId}/assets/${assetId}/waveform?bins=90`,
    )
      .then((r) => {
        if (active) setPeaks(r.peaks);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [projectId, assetId]);
  return (
    <svg
      className="clip-wave"
      viewBox="0 0 180 30"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      {peaks.map((v, i) => (
        <line key={i} x1={i * 2} x2={i * 2} y1={15 - v * 14} y2={15 + v * 14} />
      ))}
    </svg>
  );
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
  const [base, setBase] = useState(-1),
    [sceneId, setSceneId] = useState(s.targetScene || p.scenes[0]?.id || ""),
    [from, setFrom] = useState(0),
    [to, setTo] = useState(totalFrames(p) / fps(p));
  const selection = scope === "selection" ? selected : [];
  const scopeData =
    scope === "scene"
      ? { type: scope, scene_id: sceneId }
      : scope === "range"
        ? {
            type: scope,
            start: Math.round(from * fps(p)),
            end: Math.round(to * fps(p)),
          }
        : { type: scope };
  async function copy() {
    const result = await api<{ prompt: string; base_revision: number }>(
      "/projects/" + p.id + "/assistant/prompt",
      { command, selection, scope: scopeData },
    );
    setPrompt(result.prompt);
    setBase(result.base_revision);
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
        {
          command,
          selection,
          scope: scopeData,
          ...(manual ? { response, base_revision: base } : {}),
        },
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
          <option value="scene">Wybrane ujęcie</option>
          <option value="range">Zakres czasu</option>
        </select>
      </Field>
      {scope === "scene" && (
        <Field label="Ujęcie w zakresie AI">
          <select value={sceneId} onChange={(e) => setSceneId(e.target.value)}>
            {p.scenes.map((scene) => (
              <option key={scene.id} value={scene.id}>
                {scene.title}
              </option>
            ))}
          </select>
        </Field>
      )}
      {scope === "range" && (
        <div className="two-fields">
          <NumberField label="Od (s)" value={from} onCommit={setFrom} />
          <NumberField label="Do (s)" value={to} onCommit={setTo} />
        </div>
      )}
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
          disabled={!response.trim() || base !== p.revision}
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
const AssistantPanel = memo(Assistant);
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
