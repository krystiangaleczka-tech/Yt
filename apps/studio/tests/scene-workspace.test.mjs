import test from "node:test";
import assert from "node:assert/strict";
import {
  shotEntries,
  shotSeconds,
  paperLayerIds,
  changePaperLayer,
  readSceneImport,
} from "../src/sceneWorkspace.ts";

test("the scene list includes both stores without converting or renumbering existing shots", () => {
  const stage = { id: "stage-a", number: 4, seconds: 6 };
  const media = { id: "scene-b", duration: 150 };
  const entries = shotEntries({ stage_scenes: [stage], scenes: [media] });
  assert.deepEqual(
    entries.map((e) => [e.kind, e.scene.id]),
    [
      ["stage", "stage-a"],
      ["media", "scene-b"],
    ],
  );
  assert.equal(entries[0].scene, stage);
  assert.equal(shotSeconds(entries[0], 25), 6);
  assert.equal(shotSeconds(entries[1], 25), 6);
});

test("editing a cutout preserves unrelated cues and synchronizes the preparation manifest", () => {
  const scene = {
    asset_id: "bg",
    asset_ids: ["bg", "cloud", "cloud", "hero"],
    parameters: {
      depth: 0.015,
      layer_cues: [
        { layer: 1, rig: "hanging_drop", start: 1 },
        { layer: 2, rig: "rake_lift", start: 3 },
      ],
    },
    generation: {
      other: "kept",
      paper_theatre_asset_first: {
        brief: "Qin",
        objects: [
          { id: "o1", asset_id: "cloud", x: 0.1, y: 0.2, width: 0.3 },
          { id: "o2", asset_id: "hero", x: 0.6 },
        ],
      },
    },
  };
  const snapshot = structuredClone(scene);
  assert.deepEqual(paperLayerIds(scene), ["cloud", "hero"]);
  const edited = changePaperLayer(scene, 1, {
    layout_x: 0.4,
    layout_width: 0.25,
    start: 2,
  });
  assert.deepEqual(scene, snapshot);
  assert.equal(edited.parameters.depth, 0.015);
  assert.deepEqual(
    edited.parameters.layer_cues[1],
    scene.parameters.layer_cues[1],
  );
  assert.equal(edited.parameters.layer_cues[0].rig, "hanging_drop");
  assert.equal(edited.generation.other, "kept");
  assert.equal(edited.generation.paper_theatre_asset_first.objects[0].x, 0.4);
  assert.equal(
    edited.generation.paper_theatre_asset_first.objects[0].width,
    0.25,
  );
  assert.deepEqual(
    edited.generation.paper_theatre_asset_first.objects[1],
    scene.generation.paper_theatre_asset_first.objects[1],
  );
});

test("import refuses malformed, mixed and oversized lists before a mutation", () => {
  for (const value of [
    null,
    [],
    {},
    { scenes: [] },
    { scenes: [null] },
    { scenes: Array(201).fill({}) },
    { scenes: [{}], stage_scenes: [{}] },
  ])
    assert.throws(() => readSceneImport(value));
  assert.equal(readSceneImport({ scenes: [{ title: "Nowe" }] }).kind, "media");
  assert.equal(
    readSceneImport({ stage_scenes: [{ title: "Nowa" }] }).kind,
    "stage",
  );
});
