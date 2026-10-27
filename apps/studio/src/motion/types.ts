export type Template = "photo" | "compare" | "chart" | "quote" | "chapter";
export type MotionInsert = {
  id: string;
  template: Template;
  title: string;
  subtitle: string;
  text: string;
  source: string;
  image_ids: string[];
  labels: string[];
  data: { label: string; value: number }[];
  unit: string;
  duration: number;
  accent: string;
  background: string;
  zoom: number;
  pan: number;
  rotation: number;
  brightness: number;
  saturation: number;
  blur: number;
  rendered_asset_id: string | null;
  rendered_signature: string;
};
export type MotionProps = { insert: MotionInsert; imageUrls: string[] };
export const templateNames: Record<Template, string> = {
  photo: "Animowane zdjęcie",
  compare: "Porównanie zdjęć",
  chart: "Wykres",
  quote: "Cytat",
  chapter: "Plansza rozdziału",
};
export function makeInsert(
  id: string,
  template: Template,
  duration = 180,
): MotionInsert {
  return {
    id,
    template,
    title: templateNames[template],
    subtitle: "",
    text: "",
    source: "",
    image_ids: [],
    labels: ["Wcześniej", "Dziś"],
    data: [
      { label: "A", value: 30 },
      { label: "B", value: 70 },
    ],
    unit: "",
    duration,
    accent: "#e8b86d",
    background: "#101722",
    zoom: 1.12,
    pan: 0,
    rotation: 0,
    brightness: 1,
    saturation: 1,
    blur: 0,
    rendered_asset_id: null,
    rendered_signature: "",
  };
}
