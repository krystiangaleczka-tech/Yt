import type { Project } from "./types";
import { stableJson } from "./flowTypes.ts";

/** Szkice ujęć (legacy.production_flow.sketches). Ta sama logika po stronie serwera: studio_core/sketches.py. */
export type SketchShot = {
  id: string;
  nr: number;
  key: string;
  kadr: string;
  seconds: number;
  description: string;
  line: string;
  mark: string;
  assetId: string;
};
export type SketchSource = {
  film?: string;
  wariant?: string;
  path?: string;
  importedAt?: string;
  frames?: number;
  missing?: number;
};
export type SketchVariant = {
  id: string;
  title: string;
  scenario: string;
  shots: SketchShot[];
  source: SketchSource;
};
export type SketchShotContent = Omit<SketchShot, "id">;
export type SketchContent = { title: string; scenario: string; shots: SketchShotContent[] };
export type SketchApproval = {
  variantId: string;
  title: string;
  at: string;
  who: string;
  note: string;
  signature: string;
  snapshot: SketchContent;
};
export type Sketches = {
  version: number;
  playSeconds: number;
  variants: SketchVariant[];
  approved: SketchApproval | null;
};
export type ApprovalState = "none" | "current" | "stale" | "missing";
export type SketchSourceFile = {
  path: string;
  film: string;
  wariant: string;
  tytul?: string;
  shots?: number;
  frames?: number;
  error?: string;
};

export const DEFAULT_SKETCH_IDS = ["szkic_a", "szkic_b", "szkic_c"];
export const MAX_SKETCH_VARIANTS = 12;
export const DEFAULT_PLAY_SECONDS = 25;

export const emptySketch = (id: string): SketchVariant => ({ id, title: "", scenario: "", shots: [], source: {} });
export const sketchLetter = (index: number) => (index < 26 ? String.fromCharCode(65 + index) : String(index + 1));
export const sketchLabel = (index: number) => "Wariant " + sketchLetter(index);
export const isEmptySketch = (v: SketchVariant) => !v.title.trim() && !v.scenario.trim() && v.shots.length === 0;

const text = (value: unknown) => (typeof value === "string" ? value : value == null ? "" : String(value));
const seconds = (value: unknown) => {
  const n = Number(value ?? 4);
  return Number.isFinite(n) && n > 0 ? n : 4;
};

function shotFrom(raw: unknown, fallbackId: string): SketchShot {
  const v = (raw && typeof raw === "object" ? raw : {}) as Record<string, unknown>;
  return {
    id: text(v.id) || fallbackId,
    nr: Math.trunc(Number(v.nr) || 0),
    key: text(v.key),
    kadr: text(v.kadr),
    seconds: seconds(v.seconds),
    description: text(v.description),
    line: text(v.line),
    mark: text(v.mark),
    assetId: text(v.assetId),
  };
}

/** Szkice z projektu; brak danych = trzy puste warianty o stałych identyfikatorach. */
export function sketchesFrom(project: Pick<Project, "legacy">): Sketches {
  const flow = project.legacy?.production_flow as Record<string, unknown> | undefined;
  const raw = (flow && typeof flow === "object" ? flow.sketches : undefined) as Record<string, unknown> | undefined;
  const source = raw && typeof raw === "object" && !Array.isArray(raw) ? raw : {};
  const list = Array.isArray(source.variants) ? (source.variants as Record<string, unknown>[]) : [];
  const variants: SketchVariant[] = list.length
    ? list.map((v, i) => {
        const id = text(v?.id) || `szkic_${i + 1}`;
        return {
          id,
          title: text(v?.title),
          scenario: text(v?.scenario),
          shots: (Array.isArray(v?.shots) ? v.shots : []).map((shot, k) =>
            shotFrom(shot, `${id}-${String(k + 1).padStart(3, "0")}`)),
          source: (v?.source && typeof v.source === "object" ? v.source : {}) as SketchSource,
        };
      })
    : DEFAULT_SKETCH_IDS.map(emptySketch);
  const play = Number(source.playSeconds);
  const approved = source.approved && typeof source.approved === "object" ? (source.approved as SketchApproval) : null;
  return {
    version: 1,
    playSeconds: Number.isFinite(play) && play >= 5 && play <= 180 ? play : DEFAULT_PLAY_SECONDS,
    variants,
    approved: approved && approved.variantId ? approved : null,
  };
}

export const shotContent = (s: SketchShot): SketchShotContent => ({
  nr: Math.trunc(Number(s.nr) || 0), key: s.key, kadr: s.kadr, seconds: seconds(s.seconds),
  description: s.description, line: s.line, mark: s.mark, assetId: s.assetId,
});

/** To, co reżyser zatwierdza (bez identyfikatorów i źródła) — porównywane z migawką zatwierdzenia. */
export const content = (v: SketchVariant): SketchContent => ({
  title: v.title, scenario: v.scenario, shots: v.shots.map(shotContent),
});

export function approvalState(sk: Sketches): ApprovalState {
  if (!sk.approved) return "none";
  const variant = sk.variants.find((v) => v.id === sk.approved!.variantId);
  if (!variant) return "missing";
  const snap = sk.approved.snapshot || ({} as Partial<SketchContent>);
  const approved = { title: text(snap.title), scenario: text(snap.scenario),
    shots: (Array.isArray(snap.shots) ? snap.shots : []).map((x) => shotContent(shotFrom(x, ""))) };
  return stableJson(content(variant)) === stableJson(approved) ? "current" : "stale";
}

export const totalSeconds = (shots: Pick<SketchShot, "seconds">[]) =>
  shots.reduce((sum, s) => sum + seconds(s.seconds), 0);

export function clock(value: number) {
  const total = Math.max(0, Math.round(value));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

/**
 * Czas każdej kartki w przeglądzie: proporcjonalny do długości ujęcia, suma = total.
 * Ujęcia, które wypadłyby poniżej minimum, dostają minimum, a reszta jest skalowana
 * (wyrównanie „wodne”). Gdy n·min > total, każde ujęcie dostaje total/n.
 */
export function flipTimes(lengths: number[], total: number, min = 0.15): number[] {
  const n = lengths.length;
  if (!n || !(total > 0)) return lengths.map(() => 0);
  if (n * min >= total) return lengths.map(() => total / n);
  const weights = lengths.map((x) => Math.max(0, Number(x) || 0));
  const fixed = weights.map(() => false);
  for (;;) {
    const free = weights.map((_, i) => i).filter((i) => !fixed[i]);
    const remaining = total - min * (n - free.length);
    const sum = free.reduce((acc, i) => acc + weights[i], 0);
    if (!free.length) return weights.map(() => total / n);
    if (sum <= 0) return weights.map((_, i) => (fixed[i] ? min : remaining / free.length));
    const scale = remaining / sum;
    let changed = false;
    for (const i of free)
      if (weights[i] * scale < min) {
        fixed[i] = true;
        changed = true;
      }
    if (!changed) return weights.map((w, i) => (fixed[i] ? min : w * scale));
  }
}

/** Początki kartek (narastająco) — do szukania bieżącej kartki i do kresek znaczników. */
export function starts(times: number[]): number[] {
  const result: number[] = [];
  let at = 0;
  for (const t of times) {
    result.push(at);
    at += t;
  }
  return result;
}

export function indexAt(startsList: number[], time: number): number {
  let lo = 0,
    hi = startsList.length - 1;
  if (hi < 0) return -1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (startsList[mid] <= time) lo = mid;
    else hi = mid - 1;
  }
  return lo;
}

const QUOTES = /[„"“”«»]([^„"“”«»]+)[„"“”«»]/g;

function markOf(paragraph: string): string | null {
  if (paragraph.includes("\n") || paragraph.length > 60) return null;
  const t = paragraph.trim();
  if (/^#+\s*/.test(t)) return t.replace(/^#+\s*/, "").replace(/:$/, "").trim();
  if (/^\[.+\]$/.test(t)) return t.slice(1, -1).trim();
  if (t.endsWith(":")) return t.slice(0, -1).trim();
  if (/[A-ZĄĆĘŁŃÓŚŹŻ]/.test(t) && t === t.toUpperCase()) return t;
  return null;
}

const words = (value: string) => value.split(/\s+/).filter(Boolean).length;

/**
 * Szybka rozpiska scenariusza na ujęcia: akapit (oddzielony pustą linią) = ujęcie.
 * Krótki jednowierszowy akapit (# nagłówek, [ZNACZNIK], WERSALIKI albo „…:”) jest znacznikiem
 * następnego ujęcia (np. HOOK 1). Tekst w cudzysłowie to kwestia; długość z liczby słów (~2,5 słowa/s).
 */
export function shotsFromScenario(scenario: string, variantId: string): SketchShot[] {
  const paragraphs = scenario
    .replace(/\r\n?/g, "\n")
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
  const shots: SketchShot[] = [];
  let pending = "";
  for (const paragraph of paragraphs) {
    const mark = markOf(paragraph);
    if (mark !== null) {
      pending = pending ? `${pending} · ${mark}` : mark;
      continue;
    }
    const quoted = [...paragraph.matchAll(QUOTES)].map((m) => m[1].trim()).filter(Boolean);
    const line = quoted.join(" ");
    const description = (quoted.length ? paragraph.replace(QUOTES, " ") : paragraph)
      .replace(/[ \t]+/g, " ")
      .replace(/\s+([.,;:!?…])/g, "$1")
      .replace(/[,;:–—-]+([.!?…])/g, "$1")
      .replace(/[,;:–—-]+$/, "")
      .trim() || line;
    const nr = shots.length + 1;
    shots.push({
      id: `${variantId}-${String(nr).padStart(3, "0")}`,
      nr,
      key: "",
      kadr: "",
      seconds: Math.max(3, Math.round(words(line || paragraph) / 2.5) + 1),
      description,
      line,
      mark: pending,
      assetId: "",
    });
    pending = "";
  }
  return shots;
}

export function nextShotId(variant: SketchVariant): string {
  const taken = new Set(variant.shots.map((s) => s.id));
  let n = variant.shots.length + 1;
  let id = `${variant.id}-${String(n).padStart(3, "0")}`;
  while (taken.has(id)) id = `${variant.id}-${String(++n).padStart(3, "0")}`;
  return id;
}

export function newVariantId(sk: Sketches): string {
  const taken = new Set(sk.variants.map((v) => v.id));
  for (let i = 0; ; i++) {
    const id = "szkic_" + (i < 26 ? String.fromCharCode(97 + i) : String(i + 1));
    if (!taken.has(id)) return id;
  }
}
