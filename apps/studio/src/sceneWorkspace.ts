import type { StageScene } from "./animationTypes.ts";
import type { Project, Scene } from "./types.ts";
import type { Cue } from "./paperTheatreMotion.ts";

export type ShotEntry =
  { kind: "stage"; scene: StageScene } | { kind: "media"; scene: Scene };

/** Keep each existing shot exactly once; neither store is converted or discarded. */
export function shotEntries(project: Project): ShotEntry[] {
  return [
    ...project.stage_scenes.map((scene): ShotEntry => ({
      kind: "stage",
      scene,
    })),
    ...project.scenes.map((scene): ShotEntry => ({ kind: "media", scene })),
  ];
}

export function shotSeconds(entry: ShotEntry, rate: number) {
  return entry.kind === "stage"
    ? entry.scene.seconds
    : entry.scene.duration / rate;
}

/** These indices must match the renderer, including old projects containing the background twice. */
export function paperLayerIds(scene: Scene): string[] {
  const seen = new Set([scene.asset_id]);
  return (scene.asset_ids || []).filter(
    (id) => !seen.has(id) && !!seen.add(id),
  );
}

export function paperCues(scene: Scene): Cue[] {
  return Array.isArray(scene.parameters?.layer_cues)
    ? (scene.parameters.layer_cues as Cue[])
    : [];
}

/** Merge only the selected layer and keep the preparation manifest in sync. */
export function changePaperLayer(
  scene: Scene,
  layer: number,
  changes: Partial<Cue>,
): Scene {
  const cues = paperCues(scene);
  const previous = cues.find((cue) => cue.layer === layer);
  const cue = { ...previous, layer, ...changes };
  const next = previous
    ? cues.map((item) => (item.layer === layer ? cue : item))
    : [...cues, cue];
  const manifest = scene.generation?.paper_theatre_asset_first as
    | {
        objects?: { asset_id: string; [key: string]: unknown }[];
        [key: string]: unknown;
      }
    | undefined;
  const layout: Record<string, unknown> = {};
  for (const [key, name] of [
    ["layout_x", "x"],
    ["layout_y", "y"],
    ["layout_width", "width"],
    ["z_index", "z"],
  ] as const)
    if (changes[key] !== undefined) layout[name] = changes[key];
  return {
    ...scene,
    parameters: { ...scene.parameters, layer_cues: next },
    ...(manifest?.objects
      ? {
          generation: {
            ...scene.generation,
            paper_theatre_asset_first: {
              ...manifest,
              objects: manifest.objects.map((object) =>
                object.asset_id === paperLayerIds(scene)[layer - 1]
                  ? { ...object, ...layout }
                  : object,
              ),
            },
          },
        }
      : {}),
  };
}

/** Validate the envelope before issuing any mutation; imported identities are always regenerated. */
export function readSceneImport(raw: unknown): {
  kind: "stage" | "media";
  scenes: Record<string, unknown>[];
} {
  if (!raw || typeof raw !== "object" || Array.isArray(raw))
    throw new Error("Plik JSON musi zawierać scenes albo stage_scenes.");
  const value = raw as Record<string, unknown>;
  const kind =
    Array.isArray(value.stage_scenes) && value.stage_scenes.length
      ? "stage"
      : "media";
  const scenes = value[kind === "stage" ? "stage_scenes" : "scenes"];
  if (!Array.isArray(scenes) || !scenes.length || scenes.length > 200)
    throw new Error("Importuj od 1 do 200 ujęć naraz.");
  if (
    scenes.some(
      (scene) => !scene || typeof scene !== "object" || Array.isArray(scene),
    )
  )
    throw new Error("Każde ujęcie musi być obiektem JSON.");
  if (
    Array.isArray(value.stage_scenes) &&
    value.stage_scenes.length &&
    Array.isArray(value.scenes) &&
    value.scenes.length
  )
    throw new Error("Importuj scenes i stage_scenes w osobnych plikach.");
  return { kind, scenes };
}
