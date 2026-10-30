import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { rigMotion, pyRound, drawOrder, layoutRect, parallaxShift } from '../src/paperTheatreMotion.ts';

const fixture = JSON.parse(readFileSync(new URL('./fixtures/paper-theatre-motion.json', import.meta.url), 'utf8'));

test('live preview places every cutout exactly where the MP4 renderer does', () => {
  assert.ok(fixture.cases.length > 1000);
  for (const item of fixture.cases) {
    const motion = rigMotion(item.rig, item.cue, item.elapsed, item.duration, item.bounds, item.width, item.height);
    const where = `${item.rig} ${JSON.stringify(item.cue)} t=${item.elapsed} d=${item.duration} ${item.bounds}`;
    assert.deepEqual(Object.keys(motion).sort(), Object.keys(item.motion).sort(), where);
    for (const [key, expected] of Object.entries(item.motion)) {
      const actual = motion[key];
      if (typeof expected === 'number' && !Number.isInteger(expected)) {
        assert.ok(Math.abs(actual - expected) <= 1e-9 * Math.max(1, Math.abs(expected)), `${where} ${key}: ${actual} != ${expected}`);
      } else {
        // Rounded pixel positions, alphas and flags must be identical.
        assert.equal(actual, expected, `${where} ${key}`);
      }
    }
  }
});

test('python rounding: ties to even, never negative zero', () => {
  assert.deepEqual([0.5, 1.5, 2.5, -0.5, -1.5, -2.5, 2.4999, -3.5000001].map(pyRound), [0, 2, 2, 0, -2, -2, 2, -4]);
  assert.ok(Object.is(pyRound(-0.4), 0));
});

test('z-order ignores entrance order, ties fall back to layer index', () => {
  const cues = new Map([[1, { layer: 1, z_index: 50 }], [2, { layer: 2, z_index: 0 }], [3, { layer: 3, z_index: 50 }], [4, { layer: 4 }]]);
  assert.deepEqual(drawOrder(4, cues), [2, 4, 1, 3]);
  assert.deepEqual(drawOrder(4, cues, false), [1, 2, 3, 4]);
});

test('asset-first layout: x is the centre, y the foot, width a fraction of the frame', () => {
  assert.deepEqual(layoutRect({ layer: 1, layout_x: .5, layout_y: .9, layout_width: .25 }, { width: 400, height: 800 }, 1280, 720),
    { x: 480, y: 8, width: 320, height: 640 });
  assert.equal(parallaxShift(1, 1280, { depth: 0 }, { layer: 1, depth: 2.8 }, 1), 0);
  assert.equal(parallaxShift(1, 1280, { depth: .015 }, { layer: 1, depth: 2.8 }, 1), 27);
});
