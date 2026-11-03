import type { FlowData, FlowOutline } from "./flowTypes";
import { chosen, sceneSourceSignature } from "./flowTypes.ts";

export type DirectorMode = "auto" | "guided" | "manual";
export type ShotKind = { id: string; name: string; usage: string };
export type DirectorPattern = {
  id: string; name: string; purpose: string; cue: string; rhythm: string;
  shots: string[]; tension: number[];
};
export type DirectorBeat = {
  id: string; title: string; goal: string;
  tensionBefore: number; tensionAfter: number;
  viewerKnows: string; characterKnows: string; soundCue: string;
  patternId: string;
};
export type DirectorShot = {
  id: string; beatId: string; typeId: string; title: string; description: string;
  duration: number; transition: string; sound: string;
};
export type SceneDirection = {
  outlineId: string; sourceSignature: string; patternId: string;
  mode: DirectorMode; notes: string; beats: DirectorBeat[]; shots: DirectorShot[];
};
export type DirectorState = {
  mode: DirectorMode; plans: Record<string, SceneDirection>;
  customPatterns: DirectorPattern[];
};
export const shotKinds: ShotKind[] = [
  { id: "establishing", name: "Establishing Shot", usage: "Pokazuje miejsce i orientuje widza." },
  { id: "wide", name: "Wide Shot", usage: "Dystans, przestrzeń, samotność." },
  { id: "medium", name: "Medium Shot", usage: "Akcja postaci i relacja z otoczeniem." },
  { id: "close-up", name: "Close-Up", usage: "Emocja lub ważna informacja na twarzy." },
  { id: "extreme-close-up", name: "Extreme Close-Up", usage: "Mikroreakcja, intensywny detal." },
  { id: "insert", name: "Insert Shot", usage: "Przedmiot, telefon, przycisk, napis." },
  { id: "pov", name: "POV Shot", usage: "To, co widzi bohater." },
  { id: "reaction", name: "Reaction Shot", usage: "Odpowiedź emocjonalna na zdarzenie." },
  { id: "reverse", name: "Reverse Shot", usage: "Przeciwujęcie: na co patrzy postać." },
  { id: "over-shoulder", name: "Over-the-Shoulder", usage: "Przestrzeń między postacią a obiektem." },
  { id: "tracking", name: "Tracking Shot", usage: "Towarzyszy ruchowi i zwiększa immersję." },
  { id: "static-hold", name: "Static Hold", usage: "Długie zatrzymanie, antycypacja i niepokój." },
  { id: "cutaway", name: "Cutaway", usage: "Zmiana uwagi, sygnał poza główną akcją." },
  { id: "low-angle", name: "Low Angle", usage: "Zagrożenie, dominacja lub skala." },
  { id: "high-angle", name: "High Angle", usage: "Bezsilność i zagubienie bohatera." },
  { id: "detail", name: "Detail Shot", usage: "Ślad, dowód, wskazówka, tekstura." },
];
export const directorPatterns: DirectorPattern[] = [
  { id: "rapid-intercut", name: "Rapid Intercutting", purpose: "Dwa zagrożenia walczą o uwagę.", cue: "Telefon, kroki, drzwi, równoległe niebezpieczeństwa.", rhythm: "Skracaj cięcia, potem zatrzymaj obraz.", shots: ["medium","insert","pov","reaction","insert","reverse","extreme-close-up","static-hold"], tension: [3,5,7,9,8] },
  { id: "shot-reverse", name: "Shot / Reverse Shot", purpose: "Spojrzenie, odpowiedź i emocjonalna konsekwencja.", cue: "Bohater zauważa, że ktoś na niego patrzy.", rhythm: "Wymiana spojrzeń z coraz dłuższym finałem.", shots: ["medium","pov","reaction","reverse","close-up"], tension: [3,5,7,8] },
  { id: "slow-burn", name: "Slow Burn / Long Hold", purpose: "Lęk przed tym, co może się wydarzyć.", cue: "Cisza, pusty korytarz, niepewne oczekiwanie.", rhythm: "Długie nieruchome ujęcia, ogranicz cięcia.", shots: ["establishing","static-hold","detail","static-hold","reaction"], tension: [2,3,5,7] },
  { id: "jumpscare", name: "Jumpscare / Smash Cut", purpose: "Nagłe zerwanie oczekiwania.", cue: "Zaskoczenie po ciszy albo fałszywej uldze.", rhythm: "Cisza → błyskawiczne cięcie → krótki oddech.", shots: ["wide","static-hold","extreme-close-up","reaction","wide"], tension: [2,3,10,6] },
  { id: "false-relief", name: "False Relief", purpose: "Złudna ulga przed kolejnym zagrożeniem.", cue: "Niebezpieczeństwo pozornie mija.", rhythm: "Zwolnij, potem odsłoń nową informację.", shots: ["close-up","wide","static-hold","cutaway","reaction"], tension: [7,4,2,8] },
  { id: "reveal", name: "Delayed Reveal", purpose: "Stopniowe odsłanianie prawdy.", cue: "Tajemnica lub ukryty przedmiot.", rhythm: "Od ogółu do szczegółu, nie pokazuj rozwiązania zbyt wcześnie.", shots: ["wide","over-shoulder","detail","pov","close-up"], tension: [2,4,6,8] },
  { id: "investigation", name: "Investigation / Discovery", purpose: "Widz wraz z bohaterem składa wskazówki.", cue: "Tropy, dokumenty, ślady, pytania.", rhythm: "Przeplataj detale z interpretacją postaci.", shots: ["medium","insert","detail","reaction","pov"], tension: [2,3,5,6] },
  { id: "chase", name: "Chase / Escalation", purpose: "Przyspieszenie zagrożenia i akcji.", cue: "Pościg, ucieczka, gwałtowny ruch.", rhythm: "Krótkie ujęcia, orientujące szerokie plany co kilka cięć.", shots: ["wide","tracking","close-up","pov","tracking","reaction"], tension: [5,7,9,10] },
  { id: "parallel", name: "Cross-Cutting / Parallel Action", purpose: "Dwie akcje zachodzą jednocześnie.", cue: "Dwa miejsca, przeplatające się zagrożenia.", rhythm: "Wyraźna geografia, skracanie odstępów między powrotami.", shots: ["establishing","medium","cutaway","medium","cutaway","close-up"], tension: [3,4,6,8] },
  { id: "aftermath", name: "Aftermath / Release", purpose: "Pokazać skutki i spuścić napięcie.", cue: "Po kulminacji albo po odkryciu.", rhythm: "Dłuższe plany, miejsce na reakcję i ciszę.", shots: ["wide","reaction","detail","static-hold"], tension: [9,6,4,2] },
  { id: "emotional", name: "Emotional Pause", purpose: "Zatrzymać tempo i pogłębić więź z bohaterem.", cue: "Refleksja, pożegnanie, decyzja.", rhythm: "Dłuższe zbliżenia i ograniczone ruchy kamery.", shots: ["medium","close-up","reaction","wide"], tension: [5,4,3,4] },
  { id: "exposition", name: "Visual Exposition", purpose: "Czytelnie przekazać informacje bez przeciążenia.", cue: "Wprowadzenie miejsca, zasad i relacji.", rhythm: "Od planu ogólnego przez detal do reakcji.", shots: ["establishing","medium","insert","close-up"], tension: [1,2,3,4] },
  { id: "evidence", name: "Evidence Montage", purpose: "Weryfikowalne fakty pokazane jako śledztwo.", cue: "Dokument, źródło, mapa lub historia.", rhythm: "Czytelny dowód → kontekst → wniosek.", shots: ["establishing","detail","insert","medium","cutaway"], tension: [2,4,5,6] },
  { id: "anticipation", name: "Anticipation / Payoff", purpose: "Zapowiedź skutku i jego opóźnione ujawnienie.", cue: "Widz widzi ryzyko zanim bohater zareaguje.", rhythm: "Detal zapowiedzi, pauza, reakcja, payoff.", shots: ["insert","pov","static-hold","reaction","reverse"], tension: [3,5,8,9] },
];
/** Field limits mirrored by the backend flow validator (studio_core/production_flow.py). */
export const directorLimits = { title: 300, goal: 4000, knows: 2000, sound: 1000, description: 3000, notes: 5000, shots: 240 } as const;
export const transitions = ["cut", "smash-cut", "match-cut", "dissolve", "dip", "whip", "flash"];
export const clampTension = (n: number) => Math.max(0, Math.min(10, Math.round(Number.isFinite(n) ? n : 0)));
export function patternById(id: string, custom: DirectorPattern[] = []): DirectorPattern {
  return [...custom, ...directorPatterns].find(p => p.id === id) || directorPatterns[0];
}
export function choosePattern(text: string, factual = false): DirectorPattern {
  const value = text.toLowerCase();
  if (/telefon|dzwon|ring|dwa zagroż|naprzemien|intercut/.test(value)) return patternById("rapid-intercut");
  if (/patrz|spojrz|odwrac.*głow|wzrok|oko/.test(value)) return patternById("shot-reverse");
  if (/pościg|ucieka|goni|biegn|uciecz/.test(value)) return patternById("chase");
  if (/cisza|czeka|nasłuch|bezruch|powol/.test(value)) return patternById("slow-burn");
  if (/nagle|wyskak|zaskoc|krzyk/.test(value)) return patternById("jumpscare");
  if (/ulga|uspokaja|bezpiecz/.test(value)) return patternById("false-relief");
  if (/odkrywa|ujawnia|tajemnic|sekret/.test(value)) return patternById("reveal");
  if (/dokument|archiw|źródł|dowód|mapa/.test(value)) return patternById("evidence");
  if (/znajduje|bada|ślad|trop/.test(value)) return patternById("investigation");
  return patternById(factual ? "evidence" : "anticipation");
}
function uid(): string {
  return crypto.randomUUID();
}
export function buildAutoPlan(
  flow: FlowData, outline: FlowOutline, mode: DirectorMode = "auto", preferredPatternId = "",
  guidance = "",
): SceneDirection {
  const description = chosen(outline)?.description || "";
  const selected = preferredPatternId ? patternById(preferredPatternId, flow.director.customPatterns) :
    choosePattern(description + " " + guidance, flow.factual);
  const beatCount = Math.max(2, selected.tension.length - 1);
  const beats: DirectorBeat[] = Array.from({ length: beatCount }, (_, i) => ({
    id: uid(),
    title: ["Ustawienie sytuacji", "Sygnał zmiany", "Rosnące napięcie", "Konsekwencja", "Payoff"][Math.min(i, 4)],
    goal: i === 0 ? "Zorientować widza: " + description.slice(0, 180) :
      i === beatCount - 1 ? "Pokazać zmianę sytuacji i przygotować następny beat." :
        "Zmienić wiedzę lub emocje bohatera i widza.",
    tensionBefore: clampTension(selected.tension[i] ?? 3),
    tensionAfter: clampTension(selected.tension[i + 1] ?? 6),
    viewerKnows: "", characterKnows: "", soundCue: "", patternId: selected.id,
  }));
  const total = Math.max(2, Number(outline.seconds) || 30);
  const count = Math.min(30, Math.max(selected.shots.length, Math.ceil(total / 5)));
  const kinds = Array.from({ length: count }, (_, i) => selected.shots[i % selected.shots.length]);
  // Rapid cutting varies duration; the total remains aligned with the scene outline.
  const weights = kinds.map((kind, i) => kind === "static-hold" ? 2.2 :
    selected.id === "rapid-intercut" && i > 2 && i < count - 1 ? 0.5 : 1);
  const weightSum = weights.reduce((sum, n) => sum + n, 0);
  const duration = weights.map(n => Math.max(0.1, Math.round((total * n / weightSum) * 10) / 10));
  const correction = Math.round((total - duration.reduce((sum, n) => sum + n, 0)) * 10) / 10;
  duration[duration.length - 1] = Math.max(0.1, Math.round((duration[duration.length - 1] + correction) * 10) / 10);
  const shots: DirectorShot[] = kinds.map((kind, i) => ({
    id: uid(), beatId: beats[Math.min(beats.length - 1, Math.floor(i * beats.length / count))].id,
    typeId: kind, title: shotKinds.find(x => x.id === kind)?.name || "Ujęcie",
    description: (shotKinds.find(x => x.id === kind)?.usage + " " + (description || "Pokazać wydarzenie zgodnie z beatem."))
      .slice(0, directorLimits.description),
    duration: duration[i], transition: "cut", sound: "",
  }));
  return {
    outlineId: outline.id, sourceSignature: sceneSourceSignature(flow, outline.id),
    patternId: selected.id, mode, notes: guidance.slice(0, directorLimits.notes), beats, shots,
  };
}
/** Accepts plain JSON, fenced JSON or JSON surrounded by a short explanation. */
export function extractJsonObject(raw: string): Record<string, unknown> {
  const text = raw.trim().replace(/^\`\`\`(?:json)?\s*/i, "").replace(/\s*\`\`\`$/, "");
  const start = text.indexOf("{"), end = text.lastIndexOf("}");
  if (start < 0 || end <= start) throw new Error("AI nie zwróciło obiektu JSON z planem reżyserii.");
  let value: unknown;
  try { value = JSON.parse(text.slice(start, end + 1)); }
  catch { throw new Error("Odpowiedź AI nie jest poprawnym JSON. Wygeneruj ponownie albo użyj planu automatycznego."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("AI powinno zwrócić obiekt JSON.");
  return value as Record<string, unknown>;
}
export function parseDirectorAI(raw: string, flow: FlowData, outline: FlowOutline, mode: DirectorMode): SceneDirection {
  const json = extractJsonObject(raw);
  if (!json || !Array.isArray(json.beats) || !Array.isArray(json.shots) ||
      json.beats.length < 1 || json.beats.length > 24 || json.shots.length < 1 || json.shots.length > 90)
    throw new Error("AI powinno zwrócić 1–24 beatów i 1–90 ujęć w JSON.");
  const beats = json.beats.map((v, i) => {
    const x = v as Record<string, unknown>;
    if (!String(x.title || "").trim()) throw new Error("Beat wymaga tytułu.");
    return {
      id: "beat-" + i + "-" + uid(), title: String(x.title).slice(0, 120),
      goal: String(x.goal || "").slice(0, 1200), tensionBefore: clampTension(Number(x.tensionBefore)),
      tensionAfter: clampTension(Number(x.tensionAfter)),
      viewerKnows: String(x.viewerKnows || "").slice(0, 600),
      characterKnows: String(x.characterKnows || "").slice(0, 600),
      soundCue: String(x.soundCue || "").slice(0, 250),
      patternId: String(x.patternId || json.patternId || "anticipation").slice(0, 160),
    };
  });
  const shots = json.shots.map((v, i) => {
    const x = v as Record<string, unknown>;
    const typeId = String(x.typeId || "medium");
    if (!shotKinds.some(s => s.id === typeId)) throw new Error("Nieznany typ ujęcia: " + typeId);
    const beatNumber = Math.max(0, Math.min(beats.length - 1, Math.floor(Number(x.beatIndex) || 0)));
    const seconds = Number(x.duration);
    if (!Number.isFinite(seconds) || seconds < 0.1 || seconds > 120) throw new Error("Nieprawidłowy czas ujęcia nr " + (i + 1));
    return {
      id: uid(), beatId: beats[beatNumber].id, typeId,
      title: String(x.title || shotKinds.find(s => s.id === typeId)?.name || "").slice(0, 160),
      description: String(x.description || "").slice(0, 1600),
      duration: Math.round(seconds * 10) / 10,
      transition: String(x.transition || "cut").slice(0, 30),
      sound: String(x.sound || "").slice(0, 300),
    };
  });
  return {
    outlineId: outline.id, sourceSignature: sceneSourceSignature(flow, outline.id),
    patternId: String(json.patternId || "anticipation").slice(0, 160), mode,
    notes: String(json.notes || "").slice(0, 3000), beats, shots,
  };
}
