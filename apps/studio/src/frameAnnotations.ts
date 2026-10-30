export type AnnotationPoint = { x: number; y: number };
export type AnnotationStroke = {
  points: AnnotationPoint[];
  color: string;
  width: number;
};
export type FrameAnnotation = {
  id: string;
  scene_id: string;
  /** Zero-based frame in the captured time base, local to this shot. */
  frame: number;
  fps_num: number;
  fps_den: number;
  text: string;
  strokes: AnnotationStroke[];
  created_at: string;
  updated_at: string;
};

export function annotationFrame(
  note: Pick<FrameAnnotation, "frame" | "fps_num" | "fps_den">,
  rate: number,
) {
  return Math.round(((note.frame * note.fps_den) / note.fps_num) * rate);
}

export function notesAtFrame(
  notes: FrameAnnotation[],
  sceneId: string,
  frame: number,
  rate: number,
) {
  return notes.filter(
    (note) =>
      note.scene_id === sceneId && annotationFrame(note, rate) === frame,
  );
}

export function annotationGroups(
  notes: FrameAnnotation[],
  rate: number,
  total: number,
) {
  const groups = new Map<number, FrameAnnotation[]>();
  for (const note of notes) {
    const frame = annotationFrame(note, rate);
    if (frame >= 0 && frame < total)
      groups.set(frame, [...(groups.get(frame) || []), note]);
  }
  return [...groups].sort(([a], [b]) => a - b);
}

/** Normalized coordinates survive preview resize and switching between desktop and phone. */
export function annotationPoint(
  clientX: number,
  clientY: number,
  bounds: { left: number; top: number; width: number; height: number },
): AnnotationPoint {
  return {
    x: Math.max(
      0,
      Math.min(1, (clientX - bounds.left) / Math.max(1, bounds.width)),
    ),
    y: Math.max(
      0,
      Math.min(1, (clientY - bounds.top) / Math.max(1, bounds.height)),
    ),
  };
}

export function strokePath(stroke: AnnotationStroke) {
  return stroke.points
    .map(
      (point, i) =>
        `${i ? "L" : "M"}${point.x.toFixed(5)},${point.y.toFixed(5)}`,
    )
    .join(" ");
}
