import { id } from "./api.ts";

export type Scores = {
  hook: number;
  audience_fit: number;
  originality: number;
  visuals: number;
  retention: number;
  evergreen: number;
};
export type Assumptions = {
  reach_low: number;
  reach_base: number;
  reach_high: number;
  ctr_delta: number;
  retention_delta: number;
  reason: string;
};
export type Subchapter = {
  id: string;
  title: string;
  purpose: string;
  question: string;
  turn: string;
  retention_plan: string;
  evidence_needed: string;
  seconds: number;
  energy: number;
  fact_ids: string[];
};
export type Chapter = {
  id: string;
  title: string;
  purpose: string;
  sections: Subchapter[];
};
export type StoryOption = {
  id: string;
  title: string;
  origin: "manual" | "ai" | "legacy";
  synopsis: string;
  central_question: string;
  hook: string;
  stakes: string;
  payoff: string;
  title_pitch: string;
  thumbnail: string;
  evergreen_reason: string;
  rationale: string;
  risks: string[];
  evidence_gaps: string[];
  scores: Scores;
  assumptions: Assumptions;
  chapters: Chapter[];
  applied_hash: string;
};
export type FilmIdea = {
  id: string;
  title: string;
  question: string;
  angle: string;
  notes: string;
  origin: "manual" | "ai" | "legacy";
  stories: StoryOption[];
};
export type Baseline = {
  typical_views_30d: number | null;
  views_30d: number[];
  ctr: number | null;
  retention: number | null;
  comparable_minutes: number | null;
  success_multiple: number;
  viral_multiple: number;
  evidence: string;
};
export type Development = {
  topic_area: string;
  audience: string;
  viewer_promise: string;
  references: string;
  constraints: string;
  target_minutes: number;
  baseline: Baseline;
  ideas: FilmIdea[];
  selected_idea_id: string | null;
  selected_story_id: string | null;
  selected_story_hash: string;
};
export type Band = { low: number; base: number; high: number };
export type Forecast = {
  views_30d: Band | null;
  ctr: Band | null;
  retention: Band | null;
  probabilities: { success: number; viral: number } | null;
  reference_views: number | null;
  sample_size: number;
  editorial_score: number;
  evergreen: number;
  note: string;
  selected_current: boolean;
};
export const scoreLabels: Record<keyof Scores, string> = {
  hook: "Siła otwarcia",
  audience_fit: "Dopasowanie do widza",
  originality: "Własny punkt widzenia",
  visuals: "Materiał wizualny i dowody",
  retention: "Potencjał utrzymania uwagi",
  evergreen: "Evergreen / long-tail",
};
export const blankSection = (): Subchapter => ({
  id: id("section_"),
  title: "Nowy podrozdział",
  purpose: "",
  question: "",
  turn: "",
  retention_plan: "",
  evidence_needed: "",
  seconds: 60,
  energy: 5,
  fact_ids: [],
});
export const blankChapter = (): Chapter => ({
  id: id("chapter_"),
  title: "Nowy rozdział",
  purpose: "",
  sections: [blankSection()],
});
export const blankStory = (): StoryOption => ({
  id: id("outline_"),
  title: "Nowy wariant historii",
  origin: "manual",
  synopsis: "",
  central_question: "",
  hook: "",
  stakes: "",
  payoff: "",
  title_pitch: "",
  thumbnail: "",
  evergreen_reason: "",
  rationale: "",
  risks: [],
  evidence_gaps: [],
  scores: {
    hook: 50,
    audience_fit: 50,
    originality: 50,
    visuals: 50,
    retention: 50,
    evergreen: 50,
  },
  assumptions: {
    reach_low: 0.5,
    reach_base: 1,
    reach_high: 2,
    ctr_delta: 0,
    retention_delta: 0,
    reason:
      "Neutralny scenariusz roboczy; dostosuj po analizie tematu i opakowania.",
  },
  chapters: [],
  applied_hash: "",
});
export const blankIdea = (): FilmIdea => ({
  id: id("idea_"),
  title: "Nowy pomysł",
  question: "",
  angle: "",
  notes: "",
  origin: "manual",
  stories: [],
});
export function copyStory(story: StoryOption): StoryOption {
  story = structuredClone(story);
  return {
    ...story,
    id: id("outline_"),
    title: story.title.slice(0, 180) + " — kopia",
    origin: "manual",
    applied_hash: "",
    chapters: story.chapters.map((c) => ({
      ...c,
      id: id("chapter_"),
      sections: c.sections.map((s) => ({ ...s, id: id("section_") })),
    })),
  };
}
