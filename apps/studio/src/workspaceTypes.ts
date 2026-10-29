import type { Chapter } from "./developmentTypes";
export type Preset = Partial<{
  language: string;
  audience: string;
  viewer_promise: string;
  references: string;
  constraints: string;
  target_minutes: number;
  narrative_style: string;
  visual_style: string;
  font: string;
  color: string;
  voice_id: string;
  pronunciation: Record<string, string>;
  width: number;
  height: number;
  fps_num: number;
  fps_den: number;
  ducking: boolean;
  ducking_gain: number;
}>;
export type Category = {
  id: string;
  revision: number;
  name: string;
  description: string;
  channel_id: string;
  defaults: Preset;
  archived: boolean;
};
export type ResourceKind =
  "fact" | "source" | "note" | "media" | "idea" | "template" | "baseline";
export type BankResource = {
  id: string;
  revision: number;
  title: string;
  kind: ResourceKind;
  scope: "workspace" | "channel" | "category";
  channel_id: string;
  category_ids: string[];
  tags: string[];
  context: string;
  payload: Record<string, any>;
  origin_project_id: string;
  origin_item_id: string;
  created_at: string;
  updated_at: string;
  archived: boolean;
  uses?: {
    project_id: string;
    title: string;
    published: boolean;
    archived: boolean;
    revision: number;
  }[];
};
export type ResourceLink = {
  resource_id: string;
  revision: number;
  kind: string;
  title: string;
  local_ids: Record<string, string>;
  imported_at: string;
  latest_revision?: number;
  update_available?: boolean;
  archived?: boolean;
  missing?: boolean;
};
export type WorkspaceData = {
  categories: Category[];
  resources: BankResource[];
  defaults: { revision: number; preset: Preset };
  channels: Record<string, any>[];
};
export type TemplateData = { preset: Preset; chapters: Chapter[] };
export const kindLabels: Record<ResourceKind, string> = {
  fact: "Fakt",
  source: "Źródło",
  note: "Notatka",
  media: "Medium",
  idea: "Pomysł",
  template: "Szablon / profil",
  baseline: "Dane porównawcze",
};
export const workspacePages = [
  "bank",
  "bank-media",
  "templates",
  "workspace-settings",
  "idea-pool",
] as const;
export const workspaceTitles: Record<string, string> = {
  bank: "Bank wiedzy",
  "bank-media": "Bank mediów",
  templates: "Szablony i profile",
  "workspace-settings": "Kanały i kategorie",
  "idea-pool": "Poczekalnia pomysłów",
};
export const presetLabels: Record<string, string> = {
  language: "Język",
  audience: "Widz",
  viewer_promise: "Obietnica dla widza",
  references: "Referencje",
  constraints: "Zasady i ograniczenia",
  target_minutes: "Długość (min)",
  narrative_style: "Styl narracji",
  visual_style: "Styl obrazu",
  font: "Font",
  color: "Kolor",
  voice_id: "Profil lektora",
  pronunciation: "Słownik wymowy",
  width: "Szerokość",
  height: "Wysokość",
  fps_num: "FPS — licznik",
  fps_den: "FPS — mianownik",
  ducking: "Ściszanie muzyki",
  ducking_gain: "Poziom ściszania",
};
