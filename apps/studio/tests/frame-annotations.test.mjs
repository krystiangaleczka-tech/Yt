import test from "node:test";
import assert from "node:assert/strict";
import {
  annotationFrame,
  notesAtFrame,
  annotationGroups,
  annotationPoint,
  strokePath,
} from "../src/frameAnnotations.ts";

const note = {
  id: "a",
  scene_id: "scene-1",
  frame: 42,
  fps_num: 30,
  fps_den: 1,
  text: "Popraw chmurę",
};
test("markup is visible only on the annotated frame of its own shot", () => {
  assert.deepEqual(notesAtFrame([note], "scene-1", 42, 30), [note]);
  assert.deepEqual(notesAtFrame([note], "scene-1", 41, 30), []);
  assert.deepEqual(notesAtFrame([note], "scene-1", 43, 30), []);
  assert.deepEqual(notesAtFrame([note], "scene-2", 42, 30), []);
});
test("one timeline marker groups notes from exactly one frame and excludes trimmed frames", () => {
  const other = { ...note, id: "b" },
    later = { ...note, id: "c", frame: 70 };
  assert.deepEqual(annotationGroups([later, note, other], 30, 60), [
    [42, [note, other]],
  ]);
  assert.deepEqual(
    annotationGroups([later, note], 30, 90).map(([f]) => f),
    [42, 70],
  );
});
test("frame time survives changing FPS, including a fractional original rate", () => {
  assert.equal(annotationFrame(note, 25), 35);
  const fractional = { ...note, frame: 59, fps_num: 30000, fps_den: 1001 };
  assert.equal(annotationFrame(fractional, 30000 / 1001), 59);
  assert.equal(annotationFrame(fractional, 25), 49);
});
test("marker coordinates scale with the preview and are clamped inside its bounds", () => {
  assert.deepEqual(
    annotationPoint(300, 150, { left: 100, top: 50, width: 400, height: 200 }),
    { x: 0.5, y: 0.5 },
  );
  assert.deepEqual(
    annotationPoint(150, 75, { left: 50, top: 25, width: 200, height: 100 }),
    { x: 0.5, y: 0.5 },
  );
  assert.deepEqual(
    annotationPoint(-10, 999, { left: 0, top: 0, width: 100, height: 100 }),
    { x: 0, y: 1 },
  );
  assert.equal(
    strokePath({
      points: [
        { x: 0.25, y: 0.5 },
        { x: 0.75, y: 0.9 },
      ],
    }),
    "M0.25000,0.50000 L0.75000,0.90000",
  );
});
