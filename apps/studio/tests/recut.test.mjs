import test from 'node:test';
import assert from 'node:assert/strict';
import {
  toImage, normalizeBox, addPoint, removeNearest, setBox, settingsPayload, readyToRun, MAX_POINTS,
} from '../src/recutPrompt.ts';

const base = () => ({ box: [10, 10, 50, 50], pos: [[30, 30]], neg: [], hull: 'auto', auto: true });

test('pointer position maps to image pixels and stays inside the frame', () => {
  const rect = { left: 100, top: 50, width: 640, height: 360 };
  assert.deepEqual(toImage(420, 230, rect, 1280, 720), [640, 360]);
  assert.deepEqual(toImage(0, 0, rect, 1280, 720), [0, 0]);
  assert.deepEqual(toImage(5000, 5000, rect, 1280, 720), [1280, 720]);
});

test('drawn box is normalised regardless of drag direction', () => {
  assert.deepEqual(normalizeBox([90, 80], [10, 20]), [10, 20, 90, 80]);
});

test('adding a point drops the automatic flag and grows the box to include it', () => {
  const p = addPoint(base(), [70, 20], true);
  assert.equal(p.auto, undefined);
  assert.deepEqual(p.pos.at(-1), [70, 20]);
  assert.ok(p.box[2] >= 70);
  const n = addPoint(base(), [12, 12], false);
  assert.deepEqual(n.neg, [[12, 12]]);
  assert.deepEqual(n.box, [10, 10, 50, 50]);
});

test('points are capped and the nearest one can be removed', () => {
  let p = base();
  for (let i = 0; i < 20; i++) p = addPoint(p, [20 + i, 20], true);
  assert.equal(p.pos.length, MAX_POINTS);
  const fewer = removeNearest(p, [31, 31]);
  assert.ok(fewer.pos.length < p.pos.length);
  assert.equal(removeNearest(p, [500, 500]), p);
});

test('tiny boxes are ignored', () => {
  const p = base();
  assert.equal(setBox(p, [10, 10, 11, 11]), p);
  assert.deepEqual(setBox(p, [0, 0, 40, 40]).box, [0, 0, 40, 40]);
});

test('only edited prompts and changed depths are saved; extras need a point', () => {
  const objects = [
    { key: 'a', name: 'A', group: 'sky', order: 0, depth: 0, prompt: base() },
    { key: 'b', name: 'B', group: 'hero', order: 1, depth: 0.5, prompt: { ...base(), auto: undefined } },
  ];
  const options = { leftover: 'layers', fix_seams: true, complete_scenery: true, smear_strokes: [], paper_color: null };
  const extra = { key: 'extra_x', name: 'Bambus', group: 'props', depth: 3, prompt: { box: [0, 0, 9, 9], pos: [], neg: [] } };
  const payload = settingsPayload(objects, new Set(['b']), [extra], options);
  assert.deepEqual(Object.keys(payload.prompts), ['b']);
  assert.equal('auto' in payload.prompts.b, false);
  assert.deepEqual(payload.depth, { b: 0.5 });
  assert.match(readyToRun([extra]), /Bambus/);
  assert.equal(readyToRun([{ ...extra, prompt: { ...extra.prompt, pos: [[3, 3]] } }]), null);
});
