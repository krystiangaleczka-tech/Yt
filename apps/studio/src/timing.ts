import type { Clip, Keyframe, Project, Operation } from "./types";
export const fps = (p: Project) => p.sequence.fps_num / p.sequence.fps_den;
export const totalFrames = (p: Project) =>
  Math.max(0, ...p.sequence.clips.map((c) => c.start + c.duration));
export function time(frame: number, rate = 30, decimals = false) {
  const seconds = Math.max(0, frame / rate);
  return `${Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0")}${
    decimals
      ? "." +
        Math.floor((seconds % 1) * 100)
          .toString()
          .padStart(2, "0")
      : ""
  }`;
}
export function interpolate(
  clip: Clip,
  property: Keyframe["property"],
  frame: number,
) {
  const points = clip.keyframes
    .filter((k) => k.property === property)
    .sort((a, b) => a.frame - b.frame);
  const base = clip[property];
  if (!points.length) return base;
  if (points[0].frame !== 0)
    points.unshift({ property, frame: 0, value: base });
  for (let i = 1; i < points.length; i++) {
    if (frame <= points[i].frame) {
      const a = points[i - 1],
        b = points[i];
      const mix = Math.min(
        1,
        Math.max(0, (frame - a.frame) / (b.frame - a.frame || 1)),
      );
      return a.value + (b.value - a.value) * mix;
    }
  }
  return points.at(-1)!.value;
}
export function newClip(
  track_id: string,
  asset_id: string | null,
  start: number,
  duration: number,
): Clip {
  return {
    id: "clip_" + crypto.randomUUID().replaceAll("-", "").slice(0, 16),
    track_id,
    asset_id,
    scene_id: null,
    title: "Nowy klip",
    text: "",
    start,
    duration,
    source_in: 0,
    speed: 1,
    x: 0,
    y: 0,
    scale: 1,
    rotation: 0,
    opacity: 1,
    volume: 1,
    animation: "static",
    fade_in: 0,
    fade_out: 0,
    locked: false,
    keyframes: [],
  };
}
export function proposalPreview(
  project: Project,
  operations: Operation[],
): Project {
  const p = structuredClone(project);
  for (const op of operations) {
    const clip = p.sequence.clips.find((c) => c.id === op.clip_id);
    if (op.type === "add_clip" && op.clip)
      p.sequence.clips.push({
        ...newClip(op.clip.track_id || "v1", op.clip.asset_id || null, 0, 180),
        ...op.clip,
      });
    else if (op.type === "remove_clip")
      p.sequence.clips = p.sequence.clips.filter((c) => c.id !== op.clip_id);
    else if (op.type === "split_clip" && clip && op.frame) {
      const offset = op.frame - clip.start;
      const right = {
        ...clip,
        id: clip.id + "_proposal",
        start: op.frame,
        duration: clip.duration - offset,
        source_in: clip.source_in + Math.round(offset * clip.speed),
        fade_in: 0,
        transition: "cut",
        transition_duration: 0,
        keyframes: [] as Clip["keyframes"],
      };
      const leftKeys: Clip["keyframes"] = [],
        rightKeys: Clip["keyframes"] = [];
      for (const property of new Set(clip.keyframes.map((k) => k.property))) {
        const value = interpolate(clip, property, offset);
        leftKeys.push(
          ...clip.keyframes.filter(
            (k) => k.property === property && k.frame < offset,
          ),
          { property, frame: offset, value },
        );
        rightKeys.push(
          { property, frame: 0, value },
          ...clip.keyframes
            .filter((k) => k.property === property && k.frame > offset)
            .map((k) => ({ ...k, frame: k.frame - offset })),
        );
      }
      clip.keyframes = leftKeys;
      right.keyframes = rightKeys;
      clip.duration = offset;
      clip.fade_out = 0;
      clip.fade_in = Math.min(clip.fade_in, clip.duration);
      clip.transition_duration = Math.min(
        clip.transition_duration || 0,
        clip.duration,
      );
      right.fade_out = Math.min(right.fade_out, right.duration);
      p.sequence.clips.push(right);
    } else if (clip && op.changes) Object.assign(clip, op.changes);
  }
  return p;
}
