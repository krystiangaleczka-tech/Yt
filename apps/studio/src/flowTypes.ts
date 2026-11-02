import type { Project } from "./types";
import type { DirectorState } from "./directorTypes";

export type FlowStage = "master" | "acts" | "sequences" | "outlines" | "direction";
export type FlowVariant = { id: string; title: string; description: string };
export type FlowNode = { id: string; variants: FlowVariant[]; selected: string | null };
export type FlowSection = FlowNode & { actId: string; seconds: number };
export type FlowOutline = FlowNode & { sectionId: string; seconds: number };
export type BibleKey = "characters" | "chronology" | "narration" | "visuals" | "facts" | "transitions";
export const bibleFields: { key: BibleKey; title: string; hint: string }[] = [
  { key: "characters", title: "Postacie", hint: "Kim są, relacje, wygląd, przemiany i stan w kolejnych scenach." },
  { key: "chronology", title: "Chronologia", hint: "Kiedy i gdzie dzieją się wydarzenia oraz co widz już wie." },
  { key: "narration", title: "Narracja", hint: "Ton, perspektywa, tempo, obietnica i reguły opowiadania." },
  { key: "visuals", title: "Spójność wizualna", hint: "Paleta, styl animacji, lokacje, kostiumy, ujęcia referencyjne." },
  { key: "facts", title: "Fakty i źródła", hint: "Weryfikowalne tezy, odnośniki, rozbieżności. W fikcji opcjonalne." },
  { key: "transitions", title: "Przejścia", hint: "Co łączy akty, sekwencje i sceny: czas, miejsce, ciągłość obiektów." },
];
export type FlowReview = { id: string; agent: string; verdict: string; issues: string[]; suggestions: string[] };
export type FlowData = {
  version: 1;
  factual: boolean;
  sourceIdeaId: string;
  bible: Record<BibleKey, string>;
  master: FlowNode;
  acts: FlowNode[];
  sequences: FlowSection[];
  outlines: FlowOutline[];
  scripts: Record<string, string>;
  approved: Partial<Record<FlowStage, string>>;
  reviews: FlowReview[];
  director: DirectorState;
};
export const newVariant = (title = "", description = ""): FlowVariant =>
  ({ id: crypto.randomUUID(), title, description });
export const newNode = (title = ""): FlowNode => {
  const option = newVariant(title);
  return { id: crypto.randomUUID(), variants: [option], selected: option.id };
};
export function chosen(node: FlowNode): FlowVariant | undefined {
  return node.variants.find((option) => option.id === node.selected);
}
export function flowFrom(project: Project): FlowData {
  const initial: FlowData = {
    version: 1,
    factual: project.production_mode === "documentary",
    sourceIdeaId: project.development?.selected_idea_id || "",
    bible: { characters: "", chronology: "", narration: "", visuals: "", facts: "", transitions: "" },
    master: { id: "master", variants: [], selected: null },
    acts: ["Otwarcie", "Rozwinięcie", "Finał"].map(newNode),
    sequences: [],
    outlines: [],
    scripts: {},
    approved: {},
    reviews: [],
    director: { mode: "auto", plans: {}, customPatterns: [] },
  };
  const saved = project.legacy.production_flow;
  if (!saved || typeof saved !== "object" || Array.isArray(saved)) return initial;
  const value = saved as Partial<FlowData>;
  return {
    ...initial, ...value,
    sourceIdeaId: project.development?.selected_idea_id || "",
    bible: { ...initial.bible, ...value.bible },
    scripts: { ...initial.scripts, ...value.scripts },
    approved: { ...initial.approved, ...value.approved },
    acts: Array.isArray(value.acts) ? value.acts : initial.acts,
    sequences: Array.isArray(value.sequences) ? value.sequences : initial.sequences,
    outlines: Array.isArray(value.outlines) ? value.outlines : initial.outlines,
    reviews: Array.isArray(value.reviews) ? value.reviews : initial.reviews,
    director: {
      mode: ["auto", "guided", "manual"].includes(value.director?.mode || "") ? value.director!.mode : "auto",
      plans: value.director?.plans && typeof value.director.plans === "object" ? value.director.plans : {},
      customPatterns: Array.isArray(value.director?.customPatterns) ? value.director.customPatterns : [],
    },
    master: value.master || initial.master,
  };
}
export const stageOrder: FlowStage[] = ["master", "acts", "sequences", "outlines", "direction"];
/** JSON with sorted object keys, so equal data always yields the same text. */
export function stableJson(value: unknown): string {
  if (Array.isArray(value)) return "[" + value.map(v => v === undefined ? "null" : stableJson(v)).join(",") + "]";
  if (value && typeof value === "object") return "{" + Object.keys(value).sort()
    .filter(k => (value as Record<string, unknown>)[k] !== undefined)
    .map(k => JSON.stringify(k) + ":" + stableJson((value as Record<string, unknown>)[k])).join(",") + "}";
  return JSON.stringify(value ?? null);
}
function hash53(text: string, seed: number): number {
  let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
  for (let i = 0; i < text.length; i++) {
    const ch = text.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
}
/** Compact change-detection fingerprint (not a security hash). Keeps project.json small. */
export function digest(value: unknown): string {
  const text = stableJson(value);
  return "v2:" + hash53(text, 0).toString(36) + "-" + hash53(text, 0x9e3779b9).toString(36) + "-" + text.length.toString(36);
}
const variantKey = (node: FlowNode) => {
  const v = chosen(node);
  return v ? { id: v.id, title: v.title || "", description: v.description || "" } : null;
};
/** Scenes in film order: act → sequence → scene. Orphans keep their place at the end. */
export function orderedOutlines(flow: FlowData): FlowOutline[] {
  const result: FlowOutline[] = [];
  for (const act of flow.acts)
    for (const section of flow.sequences.filter(x => x.actId === act.id))
      result.push(...flow.outlines.filter(x => x.sectionId === section.id));
  return [...result, ...flow.outlines.filter(x => !result.includes(x))];
}
/** Ties each director plan to the chosen scene, act, script and Story Bible. */
export function sceneSourceSignature(flow: FlowData, outlineId: string): string {
  const outline = flow.outlines.find(x => x.id === outlineId);
  const section = flow.sequences.find(x => x.id === outline?.sectionId);
  const act = flow.acts.find(x => x.id === section?.actId);
  return digest({ outline: outline ? { id: outline.id, selected: variantKey(outline), seconds: Number(outline.seconds) || 0 } : null,
    section: section ? { id: section.id, selected: variantKey(section) } : null,
    act: act ? { id: act.id, selected: variantKey(act), script: flow.scripts[act.id] || "" } : null,
    bible: flow.bible, master: variantKey(flow.master), factual: flow.factual });
}
/** Signatures include upstream approved selections, so stale approvals remain visibly stale. */
export function stageSignature(flow: FlowData, stage: FlowStage): string {
  if (stage === "direction") return digest({ outlines: stageSignature(flow, "outlines"),
    sources: flow.outlines.map(x => sceneSourceSignature(flow, x.id)),
    plans: flow.outlines.map(x => flow.director.plans[x.id] ?? null) });
  const master = variantKey(flow.master);
  const acts = flow.acts.map((x) => ({ id: x.id, selected: variantKey(x) }));
  const sequences = flow.sequences.map((x) => ({ id: x.id, actId: x.actId, seconds: Number(x.seconds) || 0, selected: variantKey(x) }));
  const outlines = flow.outlines.map((x) => ({ id: x.id, sectionId: x.sectionId, seconds: Number(x.seconds) || 0, selected: variantKey(x) }));
  const payload = { stage, sourceIdeaId: flow.sourceIdeaId, bible: flow.bible, factual: flow.factual, master, ...(stage !== "master" ? { acts } : {}),
    ...(["sequences", "outlines"].includes(stage) ? { sequences } : {}),
    ...(stage === "outlines" ? { outlines } : {}) };
  return digest(payload);
}
export const isApproved = (flow: FlowData, stage: FlowStage) =>
  Boolean(flow.approved[stage] && flow.approved[stage] === stageSignature(flow, stage));
export function isReady(flow: FlowData, stage: FlowStage) {
  const populated = (items: FlowNode[]) => items.length > 0 && items.every(x => Boolean(chosen(x)?.description.trim()));
  if (stage === "master") return Boolean(chosen(flow.master)?.description.trim());
  if (stage === "acts") return isApproved(flow, "master") && populated(flow.acts);
  if (stage === "sequences") return isApproved(flow, "acts") && populated(flow.sequences) &&
    flow.acts.every(act => flow.sequences.some(section => section.actId === act.id));
  if (stage === "direction") return isApproved(flow, "outlines") && flow.outlines.length > 0 &&
    flow.outlines.every(x => {
      const plan = flow.director.plans[x.id];
      return Boolean(plan && plan.sourceSignature === sceneSourceSignature(flow, x.id) &&
        plan.beats.length > 0 && plan.shots.length > 0 &&
        plan.shots.every(shot => shot.duration >= 0.1 && plan.beats.some(beat => beat.id === shot.beatId)));
    });
  return isApproved(flow, "sequences") && populated(flow.outlines) &&
    flow.sequences.every(section => flow.outlines.some(outline => outline.sectionId === section.id));
}
