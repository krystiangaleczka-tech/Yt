import { useEffect, useRef, useState } from "react";
import type { PointerEvent, ReactNode } from "react";
import { Highlighter, MessageSquare, Save, Trash2, X } from "lucide-react";
import { api, id } from "./api";
import { Button, IconButton } from "./components";
import { useStudio } from "./context";
import type { Project } from "./types";
import {
  annotationFrame,
  annotationPoint,
  notesAtFrame,
  strokePath,
} from "./frameAnnotations";
import type { AnnotationStroke, FrameAnnotation } from "./frameAnnotations";
import { time } from "./timing";
import "./FrameReview.css";

type Draft = Omit<FrameAnnotation, "created_at" | "updated_at">;
function storedDraft(key: string, sceneId: string): Draft | null {
  try {
    const value = JSON.parse(localStorage.getItem(key) || "null");
    if (
      !value ||
      value.scene_id !== sceneId ||
      !/^ann_[a-f0-9]{16}$/.test(value.id) ||
      !Number.isInteger(value.frame) ||
      value.frame < 0 ||
      !Number.isInteger(value.fps_num) ||
      !(value.fps_num > 0) ||
      !Number.isInteger(value.fps_den) ||
      !(value.fps_den > 0) ||
      typeof value.text !== "string" ||
      !Array.isArray(value.strokes) ||
      value.strokes.length > 20 ||
      value.strokes.some(
        (stroke: AnnotationStroke) =>
          !/^#[0-9a-f]{6}$/i.test(stroke.color) ||
          !(stroke.width >= 1 && stroke.width <= 16) ||
          !Array.isArray(stroke.points) ||
          stroke.points.length > 2000 ||
          stroke.points.some(
            (p) =>
              !(
                Number.isFinite(p.x) &&
                Number.isFinite(p.y) &&
                p.x >= 0 &&
                p.x <= 1 &&
                p.y >= 0 &&
                p.y <= 1
              ),
          ),
      )
    )
      return null;
    return {
      ...value,
      strokes: value.strokes
        .filter((stroke: AnnotationStroke) => stroke.points.length)
        .map((stroke: AnnotationStroke) =>
          stroke.points.length === 1
            ? { ...stroke, points: [...stroke.points, { ...stroke.points[0] }] }
            : stroke,
        ),
    };
  } catch {
    return null;
  }
}

export default function FrameReview({
  sceneId,
  frame,
  total,
  rate,
  playing,
  ready = true,
  onPause,
  onSeek,
  selectedId,
  onSelect,
  children,
}: {
  sceneId: string;
  frame: number;
  total: number;
  rate: number;
  playing: boolean;
  ready?: boolean;
  onPause: () => void;
  onSeek: (frame: number) => void;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  children: ReactNode;
}) {
  const s = useStudio(),
    p = s.project!;
  const storageKey = `docos:frame-draft:${p.id}:${sceneId}`;
  const [draft, setDraft] = useState<Draft | null>(() =>
    storedDraft(storageKey, sceneId),
  );
  const [armed, setArmed] = useState(false),
    [drawing, setDrawing] = useState(false),
    [busy, setBusy] = useState(false);
  const pointer = useRef<{ id: number; stroke: number } | null>(null);
  const visual = useRef<HTMLDivElement>(null),
    text = useRef<HTMLTextAreaElement>(null);
  const notes = (p.frame_annotations || []).filter(
    (note) => note.scene_id === sceneId,
  );
  const current = notesAtFrame(notes, sceneId, frame, rate);
  const draftHere =
    draft && annotationFrame(draft, rate) === frame ? draft : null;
  const selected = current.find((note) => note.id === selectedId);
  const shown = playing || !ready ? undefined : draftHere || selected;
  useEffect(() => {
    try {
      if (draft) localStorage.setItem(storageKey, JSON.stringify(draft));
      else localStorage.removeItem(storageKey);
    } catch {
      /* Saving the annotation still works if browser storage is full. */
    }
  }, [storageKey, draft]);
  useEffect(() => {
    if (shown && !drawing) {
      text.current?.focus({ preventScroll: true });
      text.current
        ?.closest(".frame-note-bubble")
        ?.scrollIntoView({ block: "nearest" });
    }
  }, [shown?.id, drawing]);
  function point(event: PointerEvent<SVGSVGElement>) {
    return annotationPoint(
      event.clientX,
      event.clientY,
      event.currentTarget.getBoundingClientRect(),
    );
  }
  function start(event: PointerEvent<SVGSVGElement>) {
    if (!armed || busy || playing || !ready || event.button !== 0) return;
    if (draft && !draftHere) {
      s.notify("Dokończ albo anuluj uwagę do poprzedniej klatki.");
      return;
    }
    if ((draftHere?.strokes.length || 0) >= 20) {
      s.notify("Zapisz tę uwagę przed dodaniem następnego zaznaczenia.");
      return;
    }
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    const stroke: AnnotationStroke = {
      color: "#f8d34f",
      width: 4,
      points: [point(event)],
    };
    const value: Draft = draftHere || {
      id: id("ann_"),
      scene_id: sceneId,
      frame,
      fps_num: p.sequence.fps_num,
      fps_den: p.sequence.fps_den,
      text: "",
      strokes: [],
    };
    pointer.current = { id: event.pointerId, stroke: value.strokes.length };
    setDraft({ ...value, strokes: [...value.strokes, stroke] });
    onSelect(null);
    setDrawing(true);
  }
  function move(event: PointerEvent<SVGSVGElement>) {
    const active = pointer.current;
    if (!active || active.id !== event.pointerId) return;
    const next = point(event);
    setDraft((value) => {
      if (!value) return value;
      return {
        ...value,
        strokes: value.strokes.map((stroke, i) => {
          const last = stroke.points.at(-1);
          return i === active.stroke &&
            stroke.points.length < 2000 &&
            (!last || Math.hypot(next.x - last.x, next.y - last.y) >= 0.001)
            ? { ...stroke, points: [...stroke.points, next] }
            : stroke;
        }),
      };
    });
  }
  function finish(event: PointerEvent<SVGSVGElement>) {
    if (!pointer.current || pointer.current.id !== event.pointerId) return;
    const index = pointer.current.stroke;
    setDraft((value) =>
      value
        ? {
            ...value,
            strokes: value.strokes.map((stroke, i) =>
              i === index && stroke.points.length === 1
                ? {
                    ...stroke,
                    points: [...stroke.points, { ...stroke.points[0] }],
                  }
                : stroke,
            ),
          }
        : value,
    );
    pointer.current = null;
    setDrawing(false);
    // The comment appears as soon as the marker is lifted.
  }
  function cancelPointer() {
    const index = pointer.current?.stroke;
    pointer.current = null;
    setDrawing(false);
    if (index !== undefined)
      setDraft((value) => {
        if (!value) return value;
        const strokes = value.strokes.filter((_, i) => i !== index);
        return strokes.length ? { ...value, strokes } : null;
      });
  }
  function close() {
    setDraft(null);
    onSelect(null);
    setArmed(false);
  }
  function open(note: FrameAnnotation) {
    onPause();
    onSeek(annotationFrame(note, rate));
    onSelect(note.id);
    setArmed(false);
  }
  async function save() {
    if (!draft || !draft.text.trim() || drawing) return;
    setBusy(true);
    try {
      const value = draft;
      await s.mutate((project) => {
        const exists = (project.frame_annotations || []).some(
          (note) => note.id === value.id,
        );
        return exists
          ? api<Project>(
              `/projects/${project.id}/frame-annotations/${value.id}`,
              {
                expected_revision: project.revision,
                changes: { text: value.text, strokes: value.strokes },
              },
              "PATCH",
            )
          : api<Project>(`/projects/${project.id}/frame-annotations`, {
              expected_revision: project.revision,
              ...value,
            });
      });
      setDraft(null);
      setArmed(false);
      onSelect(value.id);
      s.notify(`Zapisano uwagę do klatki ${annotationFrame(value, rate) + 1}.`);
    } finally {
      setBusy(false);
    }
  }
  async function remove(noteId: string) {
    setBusy(true);
    try {
      await s.mutate((project) =>
        api<Project>(
          `/projects/${project.id}/frame-annotations/${noteId}`,
          { expected_revision: project.revision },
          "DELETE",
        ),
      );
      close();
    } finally {
      setBusy(false);
    }
  }
  const visibleNotes =
    !playing && ready
      ? current.filter((note) => note.id !== draftHere?.id)
      : [];
  const strokes = [
    ...visibleNotes.flatMap((note) => note.strokes),
    ...(draftHere && !playing && ready ? draftHere.strokes : []),
  ];
  const anchor = shown?.strokes.at(-1)?.points.at(-1) || { x: 0.5, y: 0.5 };
  const width = visual.current?.clientWidth || 600,
    height = visual.current?.clientHeight || 338;
  const left = Math.max(
    8,
    Math.min(width - Math.min(320, width - 16) - 8, anchor.x * width),
  );
  const top = Math.max(
    8,
    Math.min(Math.max(8, height - 235), anchor.y * height),
  );
  return (
    <section className="frame-review" aria-label="Uwagi do klatek">
      <div className="frame-review-toolbar">
        <Button
          icon={Highlighter}
          primary={armed}
          disabled={busy || (!playing && !ready)}
          onClick={() => {
            onPause();
            if (draft && !draftHere) {
              onSeek(annotationFrame(draft, rate));
              return;
            }
            setArmed(!armed);
            onSelect(null);
          }}
        >
          Marker + uwaga
        </Button>
        <span className="small muted">Klatka {frame + 1}</span>
        {!playing && !ready && (
          <span className="small muted">Wczytuję klatkę…</span>
        )}
        {current.length > 0 && (
          <Button icon={MessageSquare} subtle onClick={() => open(current[0])}>
            Uwagi klatki ({current.length})
          </Button>
        )}
        {draft && !draftHere && (
          <Button
            subtle
            onClick={() => {
              onPause();
              onSeek(annotationFrame(draft, rate));
            }}
          >
            Dokończ uwagę · klatka {annotationFrame(draft, rate) + 1}
          </Button>
        )}
        {armed && (
          <span className="small muted">Zakreśl miejsce na podglądzie.</span>
        )}
      </div>
      <div className="frame-review-preview">
        <div ref={visual} className="frame-review-visual">
          {children}
          <svg
            className={`frame-review-markup ${armed && !playing && ready && !busy ? "armed" : ""}`}
            viewBox="0 0 1 1"
            preserveAspectRatio="none"
            aria-label="Marker na podglądzie klatki"
            onPointerDown={start}
            onPointerMove={move}
            onPointerUp={finish}
            onPointerCancel={cancelPointer}
          >
            {strokes.map((stroke, i) => (
              <path
                key={i}
                d={strokePath(stroke)}
                fill="none"
                stroke={stroke.color}
                strokeWidth={stroke.width}
                strokeLinecap="round"
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
              />
            ))}
          </svg>
          {!playing &&
            ready &&
            current.map((note, i) => {
              const at = note.strokes.at(-1)?.points.at(-1) || {
                x: 0.5,
                y: 0.5,
              };
              return (
                <button
                  key={note.id}
                  className="frame-note-pin"
                  title={note.text}
                  aria-label={`Otwórz uwagę ${i + 1} do klatki ${frame + 1}`}
                  style={{
                    left: `${Math.max(3, Math.min(95, at.x * 100))}%`,
                    top: `${Math.max(4, Math.min(92, at.y * 100))}%`,
                  }}
                  onClick={() => open(note)}
                >
                  <MessageSquare size={14} />
                  {i + 1}
                </button>
              );
            })}
        </div>
        {shown && !drawing && (
          <div
            className="frame-note-bubble"
            role="dialog"
            aria-label={`Uwaga do klatki ${frame + 1}`}
            style={{ left, top }}
          >
            <div className="shot-panel-heading">
              <strong>
                <MessageSquare size={15} /> Klatka {frame + 1} ·{" "}
                {time(frame, rate, true)}
              </strong>
              <IconButton
                icon={X}
                label="Zamknij uwagę"
                disabled={busy}
                onClick={close}
              />
            </div>
            <textarea
              ref={text}
              rows={3}
              maxLength={3000}
              aria-label="Treść uwagi do klatki"
              placeholder="Co poprawić w zaznaczonym miejscu?"
              disabled={busy}
              value={shown.text}
              onChange={(event) => {
                if (draft && !draftHere) {
                  s.notify("Najpierw zapisz albo anuluj nieukończoną uwagę.");
                  return;
                }
                setDraft({ ...shown, text: event.target.value });
              }}
              onKeyDown={(event) => {
                if (event.key === "Escape") {
                  event.stopPropagation();
                  close();
                }
                if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
                  event.preventDefault();
                  s.run(save);
                }
              }}
            />
            <div className="button-row">
              <Button
                primary
                icon={Save}
                busy={busy}
                disabled={!draftHere?.text.trim()}
                onClick={() => s.run(save)}
              >
                Zapisz uwagę
              </Button>
              {notes.some((note) => note.id === shown.id) && (
                <IconButton
                  icon={Trash2}
                  label="Usuń uwagę do klatki"
                  disabled={busy}
                  onClick={() => s.run(() => remove(shown.id))}
                />
              )}
              <Button subtle disabled={busy} onClick={close}>
                {draftHere ? "Anuluj" : "Zamknij"}
              </Button>
            </div>
          </div>
        )}
      </div>
      {notes.length > 0 && (
        <details className="frame-review-notes">
          <summary>Uwagi ujęcia ({notes.length})</summary>
          <ul>
            {[...notes]
              .sort(
                (a, b) => annotationFrame(a, rate) - annotationFrame(b, rate),
              )
              .map((note) => (
                <li key={note.id}>
                  <button
                    disabled={annotationFrame(note, rate) >= total}
                    onClick={() => open(note)}
                  >
                    <span>
                      Klatka {annotationFrame(note, rate) + 1} ·{" "}
                      {time(annotationFrame(note, rate), rate, true)}
                    </span>
                    {note.text}
                  </button>
                </li>
              ))}
          </ul>
        </details>
      )}
    </section>
  );
}
