import test from 'node:test';
import assert from 'node:assert/strict';
import { time, interpolate, newClip, proposalPreview } from '../src/timing.ts';

test('fractional frame rate uses explicit frame units', () => {
  assert.equal(time(1800, 30), '01:00');
  assert.equal(time(45, 30, true), '00:01.50');
});

test('keyframes interpolate from the base value before the first point', () => {
  const clip = newClip('v1', null, 0, 100);
  clip.scale = 1;
  clip.keyframes = [{ property: 'scale', frame: 100, value: 2 }];
  assert.equal(interpolate(clip, 'scale', 50), 1.5);
  assert.equal(interpolate(clip, 'scale', 150), 2);
});

test('proposal preview never mutates the real timeline', () => {
  const clip = newClip('v1', null, 0, 300);
  const project = { sequence: { clips: [clip] } };
  const preview = proposalPreview(project, [{ type: 'update_clip', clip_id: clip.id, changes: { start: 60 } }]);
  assert.equal(project.sequence.clips[0].start, 0);
  assert.equal(preview.sequence.clips[0].start, 60);
});

test('split preview keeps source offset and playback speed', () => {
  const clip = newClip('v1', null, 30, 300);
  clip.source_in = 60;
  clip.speed = 2;
  const preview = proposalPreview({ sequence: { clips: [clip] } }, [{ type: 'split_clip', clip_id: clip.id, frame: 130 }]);
  assert.equal(preview.sequence.clips[0].duration, 100);
  assert.equal(preview.sequence.clips[1].source_in, 260);
  assert.equal(preview.sequence.clips[1].duration, 200);
});

test('proposal preview can add and remove clips without changing assets', () => {
  const clip = newClip('v1', 'source', 0, 60);
  const preview = proposalPreview({ sequence: { clips: [clip] } }, [{ type: 'remove_clip', clip_id: clip.id }, { type: 'add_clip', clip: { track_id: 'v2', asset_id: 'source', duration: 90 } }]);
  assert.equal(preview.sequence.clips.length, 1);
  assert.equal(preview.sequence.clips[0].asset_id, 'source');
  assert.equal(preview.sequence.clips[0].track_id, 'v2');
});
