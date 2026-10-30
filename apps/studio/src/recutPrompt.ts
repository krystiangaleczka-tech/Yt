/** Pure helpers for the Paper Theatre re-cut panel (contour prompts per object). */
export type Point = [number, number];
export type Box = [number, number, number, number];
export type Prompt = {
  box: Box;
  pos: Point[];
  neg: Point[];
  parts?: Point[][];
  extra?: { box: Box; pos: Point[]; neg: Point[] }[];
  hull?: "auto" | "circle" | "none";
  circle?: [number, number, number];
  poly?: Point[];
  auto?: boolean;
};
export type RecutObject = {
  key: string;
  asset_id?: string;
  name: string;
  group: string;
  order?: number;
  depth: number;
  prompt: Prompt;
  auto_prompt?: Prompt;
};
export type Stroke = { points: Point[]; width: number };
export type RecutOptions = {
  leftover: "layers" | "merge" | "paper";
  fix_seams: boolean;
  complete_scenery: boolean;
  smear_strokes: Stroke[];
  paper_color: [number, number, number] | null;
};

export const MAX_POINTS = 12;

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

/** Pointer position inside a scaled image → integer image pixel coordinates. */
export function toImage(
  clientX: number, clientY: number,
  rect: { left: number; top: number; width: number; height: number },
  width: number, height: number,
): Point {
  const x = ((clientX - rect.left) / Math.max(1, rect.width)) * width;
  const y = ((clientY - rect.top) / Math.max(1, rect.height)) * height;
  return [Math.round(clamp(x, 0, width)), Math.round(clamp(y, 0, height))];
}

export function normalizeBox(a: Point, b: Point): Box {
  return [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])];
}

/** A click adds a positive or negative point; edits always drop the "auto" flag. */
export function addPoint(prompt: Prompt, point: Point, positive: boolean): Prompt {
  const list = positive ? prompt.pos : prompt.neg;
  if (list.length >= MAX_POINTS) return prompt;
  const next = { ...prompt, auto: undefined, poly: undefined };
  if (positive) next.pos = [...prompt.pos, point];
  else next.neg = [...prompt.neg, point];
  if (positive && !boxContains(next.box, point)) next.box = growBox(next.box, point, 8);
  return next;
}

export function removeNearest(prompt: Prompt, point: Point, radius = 14): Prompt {
  const near = (p: Point) => Math.hypot(p[0] - point[0], p[1] - point[1]) <= radius;
  const pos = prompt.pos.filter((p) => !near(p));
  const neg = prompt.neg.filter((p) => !near(p));
  if (pos.length === prompt.pos.length && neg.length === prompt.neg.length) return prompt;
  return { ...prompt, pos, neg, auto: undefined };
}

export function setBox(prompt: Prompt, box: Box): Prompt {
  if (box[2] - box[0] < 3 || box[3] - box[1] < 3) return prompt;
  return { ...prompt, box, auto: undefined, poly: undefined };
}

export function boxContains(box: Box, p: Point) {
  return p[0] >= box[0] && p[0] <= box[2] && p[1] >= box[1] && p[1] <= box[3];
}

export function growBox(box: Box, p: Point, margin = 0): Box {
  return [Math.min(box[0], p[0] - margin), Math.min(box[1], p[1] - margin),
    Math.max(box[2], p[0] + margin), Math.max(box[3], p[1] + margin)];
}

export function stripAuto(prompt: Prompt): Prompt {
  const copy: Prompt = { ...prompt };
  delete copy.auto;
  return copy;
}

/** Only edited prompts and changed depths are stored; the rest stays automatic. */
export function settingsPayload(
  objects: RecutObject[], edited: Set<string>, extras: RecutObject[], options: RecutOptions,
) {
  const prompts: Record<string, Prompt> = {};
  const depth: Record<string, number> = {};
  for (const o of objects) {
    if (edited.has(o.key)) prompts[o.key] = stripAuto(o.prompt);
    if (o.order !== undefined && o.depth !== o.order) depth[o.key] = o.depth;
  }
  return {
    prompts,
    depth,
    extra_objects: extras.map((e) => ({
      key: e.key, name: e.name, group: e.group, depth: e.depth,
      prompt: stripAuto(e.prompt),
    })),
    options,
  };
}

export function readyToRun(extras: RecutObject[]): string | null {
  const missing = extras.find((e) => !e.prompt.pos.length && !e.prompt.parts?.length && !e.prompt.poly?.length);
  return missing ? `Zaznacz punkt na nowym obiekcie „${missing.name}”.` : null;
}
