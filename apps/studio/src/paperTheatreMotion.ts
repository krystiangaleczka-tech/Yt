// Paper Theatre timing and geometry for the live browser preview.
//
// A line-for-line port of rig_motion() in studio_timeline/paper_theatre.py
// (the MP4 renderer). Both sides are pinned to the same test vectors in
// tests/fixtures/paper-theatre-motion.json, so a change on one side without
// the other fails the tests. No DOM here: this module also runs under Node.

export type Rig = "static" | "hanging_drop" | "bottom_rise" | "rake_lift" | "sequential";

export type Cue = {
  layer: number;
  group?: string;
  rig?: Rig | string;
  start?: number;
  duration?: number;
  depth?: number;
  drop?: number;
  overshoot?: number;
  settle_duration?: number;
  string_visible?: boolean;
  string_length?: number;
  swing_deg?: number;
  swing_decay?: number;
  pivot_x?: number;
  pivot_y?: number;
  start_rotation?: number;
  overshoot_rotation?: number;
  stick_visible?: boolean;
  stick_length?: number;
  outline_px?: number;
  outline_color?: string;
  layout_x?: number;
  layout_y?: number;
  layout_width?: number;
  z_index?: number;
};

export type Bounds = readonly [number, number, number, number];

export type HangingMotion = {
  dy: number; dy_px: number; angle: number; pivot_x: number; pivot_y: number;
  anchor_x: number; anchor_y: number; string_alpha: number; pin: boolean;
};
export type RiseMotion = { dy: number; dy_px: number };
export type LiftMotion = {
  pitch: number; scale_y: number; sprite_height: number; top: number;
  foot_x: number; foot_y: number; lean: number; stick: number;
};
export type Motion = HangingMotion | RiseMotion | LiftMotion;

/** Python's round(): ties go to the even neighbour (round(2.5) == 2). */
export function pyRound(value: number): number {
  const floor = Math.floor(value);
  const rest = value - floor;
  const result = rest > .5 ? floor + 1 : rest < .5 ? floor : floor % 2 === 0 ? floor : floor + 1;
  return result === 0 ? 0 : result; // never -0
}

const clamp = (value: number) => Math.max(0, Math.min(1, value));
const progressOf = (seconds: number, duration: number) =>
  duration > 0 ? clamp(seconds / duration) : 1;

function settle(seconds: number, duration: number, length: number): number {
  if (seconds <= duration) return 1;
  if (length <= 0) return 0;
  const p = clamp((seconds - duration) / length);
  return (1 - p) ** 2 * Math.cos(2 * Math.PI * p);
}

const num = (value: unknown, fallback: number) =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

export function rigMotion(
  rig: string, cue: Cue, elapsed: number, duration: number,
  // width is unused (as in Python), kept so both signatures read the same.
  bounds: Bounds, _width: number, height: number,
): Motion {
  const progress = progressOf(elapsed, duration);
  const ease = 1 - (1 - progress) ** 3;
  const settleLength = num(cue.settle_duration, .15);
  const overshoot = num(cue.overshoot, .03);

  if (rig === "hanging_drop") {
    const travel = bounds[3] + Math.max(2, pyRound(height * .06));
    let dy = -travel * (1 - ease) + overshoot * height * progress ** 6;
    if (elapsed >= duration) dy = overshoot * height * settle(elapsed, duration, settleLength);
    const swing = num(cue.swing_deg, 3);
    const decay = num(cue.swing_decay, 1.1);
    const angle = swing * Math.sin(elapsed * 8) * Math.exp(-decay * elapsed);
    const pivotX = (bounds[0] + bounds[2]) / 2;
    const pivotY = bounds[1] + dy;
    const anchorX = pyRound(pivotX), anchorY = pyRound(pivotY);
    let stringAlpha = 0;
    if (cue.string_visible && anchorY > 0) {
      const retract = "string_length" in cue ? 0
        : clamp((elapsed - duration) / Math.max(.001, settleLength));
      stringAlpha = pyRound(190 * (1 - retract));
    }
    const pin = Boolean(cue.string_visible && elapsed >= duration && anchorY >= 0 && anchorY < height);
    return { dy, dy_px: pyRound(dy), angle, pivot_x: pivotX, pivot_y: pivotY,
      anchor_x: anchorX, anchor_y: anchorY, string_alpha: stringAlpha, pin };
  }

  if (rig === "bottom_rise") {
    const travel = height - bounds[1] + Math.max(2, pyRound(height * .05));
    let dy = travel * (1 - ease) - overshoot * height * progress ** 6;
    if (elapsed >= duration) dy = -overshoot * height * settle(elapsed, duration, settleLength);
    return { dy, dy_px: pyRound(dy) };
  }

  if (rig === "rake_lift") {
    const startAngle = num(cue.start_rotation, 82);
    const overshootAngle = num(cue.overshoot_rotation, -5);
    let pitch = startAngle * (1 - ease) + overshootAngle * progress ** 6;
    if (elapsed >= duration) pitch = overshootAngle * settle(elapsed, duration, settleLength);
    // math.radians(x) is x * (pi / 180): keep that grouping for identical bits.
    const scaleY = Math.max(.025, Math.cos(pitch * (Math.PI / 180)));
    const size = [bounds[2] - bounds[0], bounds[3] - bounds[1]];
    const spriteHeight = Math.max(1, pyRound(size[1] * scaleY));
    const px = num(cue.pivot_x, .5);
    const py = num(cue.pivot_y, 1);
    const footX = bounds[0] + px * size[0];
    const footY = bounds[1] + py * size[1];
    const stick = cue.stick_visible ? Math.max(0, pyRound(num(cue.stick_length, .12) * height)) : 0;
    return { pitch, scale_y: scaleY, sprite_height: spriteHeight,
      top: pyRound(footY - py * spriteHeight), foot_x: footX, foot_y: footY,
      lean: -pitch * .22, stick };
  }

  throw new Error("Nieznana mechanika papierowej warstwy: " + rig);
}

/** paint(): z-order is independent from the order of entrances. */
export function drawOrder(count: number, cues: Map<number, Cue>, paperTheatre = true): number[] {
  const order = Array.from({ length: count }, (_, i) => i + 1);
  if (paperTheatre) {
    order.sort((a, b) => (num(cues.get(a)?.z_index, a) - num(cues.get(b)?.z_index, b)) || a - b);
  }
  return order;
}

/** Start of one layer: an explicit cue, else the legacy assembly schedule. */
export function layerStart(index: number, cue: Cue | undefined, params: Record<string, unknown>): number {
  return num(cue?.start, num(params.assembly_start, 0) + (index - 1) * num(params.assembly_interval, 0));
}

/** True when legacy fades are active (mirrors `assembling` in paint()). */
export function assembling(cues: Map<number, Cue>, params: Record<string, unknown>): boolean {
  return Boolean(num(params.assembly_start, 0) || num(params.assembly_interval, 0) ||
    [...cues.values()].some((cue) => (cue.rig ?? "sequential") === "sequential"));
}

/** Parallax micro-shift of one layer in pixels (0 for Asset-first shots). */
export function parallaxShift(phase: number, width: number, params: Record<string, unknown>,
  cue: Cue | undefined, index: number): number {
  return pyRound((phase - .5) * width * num(params.depth, .06) * num(cue?.depth, index));
}

/** Frame-sized placement of an Asset-first object (layout_cutout). */
export function layoutRect(cue: Cue, cutout: { width: number; height: number },
  width: number, height: number) {
  let targetWidth = Math.max(1, pyRound(width * num(cue.layout_width, 1)));
  let targetHeight = Math.max(1, pyRound(cutout.height * targetWidth / cutout.width));
  if (targetHeight > height * 4) {
    const factor = height * 4 / targetHeight;
    targetWidth = Math.max(1, pyRound(targetWidth * factor));
    targetHeight = height * 4;
  }
  return {
    x: pyRound(width * num(cue.layout_x, .5) - targetWidth / 2),
    y: pyRound(height * num(cue.layout_y, 1) - targetHeight),
    width: targetWidth, height: targetHeight,
  };
}
