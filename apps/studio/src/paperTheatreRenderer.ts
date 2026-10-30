// Live Paper Theatre preview: draws any frame of a shot in a few milliseconds.
//
// Geometry and timing come from paperTheatreMotion.ts (bit-identical to the
// MP4 renderer, see tests). Pixels are close but not identical: the browser
// resamples and blurs differently from Pillow. Exact frames still come from
// the publication renderer (poster endpoint); this is for iterating.
import {
  type Bounds, type Cue, type HangingMotion, type LiftMotion, type RiseMotion,
  assembling, drawOrder, layerStart, layoutRect, parallaxShift, pyRound, rigMotion,
} from "./paperTheatreMotion";

export type LiveSceneDef = {
  template: string;            // "paper-theatre" or "parallax"
  width: number;               // render size of the film (sequence)
  height: number;
  fps: number;
  durationFrames: number;      // scene duration; also the parallax phase length
  background: string;          // URL of the background image
  layers: string[];            // URLs, index i ↔ layer i + 1 in layer_cues
  params: Record<string, unknown>;
};

type Surface = HTMLCanvasElement;
type Sprite = { canvas: Surface; bounds: Bounds } | null;

const images = new Map<string, Promise<HTMLImageElement>>();
const alphaBoxes = new WeakMap<HTMLImageElement, Bounds | null>();
const sprites = new Map<string, Sprite>();
const SPRITE_LIMIT = 600;

function surface(width: number, height: number): Surface {
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, width);
  canvas.height = Math.max(1, height);
  return canvas;
}

function context(canvas: Surface) {
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) throw new Error("Przeglądarka nie udostępnia Canvas 2D");
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";
  return ctx;
}

export function loadImage(url: string): Promise<HTMLImageElement> {
  let pending = images.get(url);
  if (!pending) {
    pending = new Promise((resolve, reject) => {
      const image = new Image();
      image.decoding = "async";
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("Nie udało się wczytać " + url));
      image.src = url;
    });
    images.set(url, pending);
    pending.catch(() => images.delete(url));
  }
  return pending;
}

/** Alpha bounding box like PIL getbbox(): [left, top, right, bottom). */
function alphaBox(data: Uint8ClampedArray, width: number, height: number): Bounds | null {
  let left = width, top = height, right = -1, bottom = -1;
  for (let y = 0; y < height; y++) {
    const row = y * width * 4;
    for (let x = 0; x < width; x++) {
      if (data[row + x * 4 + 3]) {
        if (x < left) left = x;
        if (x > right) right = x;
        if (y < top) top = y;
        bottom = y;
      }
    }
  }
  return right < 0 ? null : [left, top, right + 1, bottom + 1];
}

function sourceBox(image: HTMLImageElement): Bounds | null {
  if (alphaBoxes.has(image)) return alphaBoxes.get(image)!;
  const canvas = surface(image.naturalWidth, image.naturalHeight);
  const ctx = context(canvas);
  ctx.drawImage(image, 0, 0);
  const box = alphaBox(ctx.getImageData(0, 0, canvas.width, canvas.height).data, canvas.width, canvas.height);
  alphaBoxes.set(image, box);
  return box;
}

/** Square max filter, the same footprint as PIL MaxFilter(2r + 1). */
function dilate(alpha: Uint8ClampedArray, width: number, height: number, radius: number) {
  const row = new Uint8ClampedArray(alpha.length);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let best = 0;
      for (let k = Math.max(0, x - radius), end = Math.min(width - 1, x + radius); k <= end && best < 255; k++) {
        const v = alpha[y * width + k]; if (v > best) best = v;
      }
      row[y * width + x] = best;
    }
  }
  const out = new Uint8ClampedArray(alpha.length);
  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      let best = 0;
      for (let k = Math.max(0, y - radius), end = Math.min(height - 1, y + radius); k <= end && best < 255; k++) {
        const v = row[k * width + x]; if (v > best) best = v;
      }
      out[y * width + x] = best;
    }
  }
  return out;
}

function hex(color: string): [number, number, number] {
  const match = /^#?([0-9a-f]{6})$/i.exec(color.trim());
  const value = parseInt(match ? match[1] : "362820", 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

/** One frame-sized layer, cropped to its visible pixels (+ optional outline). */
function prepare(image: HTMLImageElement, cue: Cue, def: LiveSceneDef, outline: boolean): Sprite {
  const { width, height } = def;
  // 1. Place on the frame exactly like layout_cutout() / resize((w, h)).
  const frame = surface(width, height);
  const fctx = context(frame);
  if (def.template === "paper-theatre" && typeof cue.layout_x === "number") {
    const box = sourceBox(image);
    if (!box) return null;
    const cut = { width: box[2] - box[0], height: box[3] - box[1] };
    const rect = layoutRect(cue, cut, width, height);
    fctx.drawImage(image, box[0], box[1], cut.width, cut.height, rect.x, rect.y, rect.width, rect.height);
  } else {
    fctx.drawImage(image, 0, 0, width, height);
  }
  const pixels = fctx.getImageData(0, 0, width, height);
  let bounds = alphaBox(pixels.data, width, height);
  if (!bounds) return null;
  let source: Surface = frame;
  // 2. Outline that follows the alpha silhouette (rig_image → _outlined).
  const stroke = outline && cue.outline_px ? Math.trunc(cue.outline_px) : 0;
  if (stroke > 0) {
    const x0 = Math.max(0, bounds[0] - stroke - 2), y0 = Math.max(0, bounds[1] - stroke - 2);
    const x1 = Math.min(width, bounds[2] + stroke + 2), y1 = Math.min(height, bounds[3] + stroke + 2);
    const w = x1 - x0, h = y1 - y0;
    const alpha = new Uint8ClampedArray(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++)
      alpha[y * w + x] = pixels.data[((y + y0) * width + x + x0) * 4 + 3];
    const grown = dilate(alpha, w, h, stroke);
    const [r, g, b] = hex(cue.outline_color || "#362820");
    const ring = new ImageData(w, h);
    for (let i = 0; i < w * h; i++) {
      ring.data[i * 4] = r; ring.data[i * 4 + 1] = g; ring.data[i * 4 + 2] = b;
      ring.data[i * 4 + 3] = Math.max(0, grown[i] - alpha[i]);
    }
    const outlined = surface(width, height);
    const octx = context(outlined);
    octx.putImageData(ring, x0, y0);
    octx.drawImage(frame, 0, 0);
    let left = w, top = h, right = -1, bottom = -1;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (grown[y * w + x]) {
      if (x < left) left = x; if (x > right) right = x; if (y < top) top = y; bottom = y;
    }
    bounds = [x0 + left, y0 + top, x0 + right + 1, y0 + bottom + 1];
    source = outlined;
  }
  // 3. Keep only the visible rectangle: sprites, not frame-sized bitmaps.
  const canvas = surface(bounds[2] - bounds[0], bounds[3] - bounds[1]);
  context(canvas).drawImage(source, -bounds[0], -bounds[1]);
  return { canvas, bounds };
}

function spriteFor(image: HTMLImageElement, url: string, cue: Cue, def: LiveSceneDef, outline: boolean): Sprite {
  const layout = def.template === "paper-theatre" && typeof cue.layout_x === "number"
    ? [cue.layout_x, cue.layout_y, cue.layout_width] : null;
  const key = JSON.stringify([url, def.width, def.height, def.template, layout,
    outline ? [Math.trunc(cue.outline_px || 0), cue.outline_color || "#362820"] : 0]);
  if (sprites.has(key)) {
    const hit = sprites.get(key)!;
    sprites.delete(key); sprites.set(key, hit); // LRU touch
    return hit;
  }
  const sprite = prepare(image, cue, def, outline);
  sprites.set(key, sprite);
  while (sprites.size > SPRITE_LIMIT) sprites.delete(sprites.keys().next().value!);
  return sprite;
}

export class LiveScene {
  readonly def: LiveSceneDef;
  private background: HTMLImageElement | null = null;
  private layers: (HTMLImageElement | null)[] = [];
  private cues = new Map<number, Cue>();
  private paper: boolean;
  private buffer: Surface | null = null;
  private bufferKey = "";
  missing = 0;

  constructor(def: LiveSceneDef) {
    this.def = def;
    this.paper = def.template === "paper-theatre";
    const list = Array.isArray(def.params.layer_cues) ? def.params.layer_cues as Cue[] : [];
    for (const cue of list) this.cues.set(cue.layer, cue);
  }

  /** Resolves when every image is decoded; failures count as missing. */
  async load() {
    const [background, ...layers] = await Promise.all(
      [this.def.background, ...this.def.layers].map((url) => loadImage(url).catch(() => null)));
    this.background = background;
    this.layers = layers;
    this.missing = [background, ...layers].filter((item) => !item).length;
    return this;
  }

  /** Prepare every sprite now (first paint is then as fast as the rest). */
  warm() {
    for (let i = 1; i <= this.layers.length; i++) {
      const image = this.layers[i - 1];
      const cue = this.cues.get(i) || { layer: i };
      if (image) spriteFor(image, this.def.layers[i - 1], cue, this.def, (cue.rig ?? "sequential") !== "sequential");
    }
  }

  /** Draw frame `frame` into ctx, scaled to ctx.canvas.width / def.width. */
  draw(ctx: CanvasRenderingContext2D, frame: number) {
    const { width: w, height: h, fps } = this.def;
    const scale = ctx.canvas.width / w;
    const params = this.def.params;
    const seconds = frame / fps;
    const phase = Math.min(1, seconds / Math.max(.01, this.def.durationFrames / fps));
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#10151e";
    ctx.fillRect(0, 0, w, h);
    if (this.background) {
      // ImageOps.fit(source, (w, h), centering=(.5, .5))
      const bw = this.background.naturalWidth, bh = this.background.naturalHeight;
      const ratio = w / h;
      const cw = bw / bh > ratio ? bh * ratio : bw;
      const ch = bw / bh > ratio ? bh : bw / ratio;
      ctx.drawImage(this.background, (bw - cw) / 2, (bh - ch) / 2, cw, ch, 0, 0, w, h);
    }
    const active = assembling(this.cues, params);
    const shadow = {
      blur: 2 * Math.max(1, w * .003) * scale,
      x: Math.max(1, pyRound(w * .003)) * scale,
      y: Math.max(1, pyRound(h * .005)) * scale,
    };
    type Step = { i: number; cue: Cue; elapsed: number; duration: number; shift: number;
      rig: string; sprite: Sprite; state: "hidden" | "still" | "moving" };
    const steps: Step[] = drawOrder(this.layers.length, this.cues, this.paper).map((i) => {
      const cue = this.cues.get(i) || { layer: i };
      const start = layerStart(i, cue, params);
      const image = this.layers[i - 1];
      const duration = typeof cue.duration === "number" ? cue.duration
        : typeof params.assembly_duration === "number" ? params.assembly_duration : .35;
      const rig = cue.rig ?? "sequential";
      const elapsed = seconds - start;
      const hidden = !image || (active && seconds < start) || (rig !== "sequential" && elapsed < 0);
      const sprite = hidden ? null : spriteFor(image!, this.def.layers[i - 1], cue, this.def, rig !== "sequential");
      return { i, cue, elapsed, duration, rig, sprite,
        shift: parallaxShift(phase, w, params, cue, i),
        state: hidden || !sprite ? "hidden" : this.still(rig, cue, elapsed, duration, active) ? "still" : "moving" };
    });
    // Layers below the first moving one are drawn once into a buffer and
    // reused until one of them changes (enters, lands, or shifts a pixel).
    let first = steps.findIndex((step) => step.state === "moving");
    if (first < 0) first = steps.length;
    const key = JSON.stringify([ctx.canvas.width, ctx.canvas.height,
      steps.slice(0, first).map((step) => [step.i, step.state, step.shift])]);
    const drawSteps = (target: CanvasRenderingContext2D, list: Step[]) => {
      for (const step of list) {
        if (step.state === "hidden" || !step.sprite) continue;
        target.save();
        target.translate(step.shift, 0);
        this.layer(target, step.sprite, step.rig, step.cue, step.elapsed, step.duration, active, shadow);
        target.restore();
      }
    };
    if (first >= 2) {
      if (this.bufferKey !== key || !this.buffer) {
        const buffer = this.buffer && this.buffer.width === ctx.canvas.width && this.buffer.height === ctx.canvas.height
          ? this.buffer : surface(ctx.canvas.width, ctx.canvas.height);
        const bctx = buffer.getContext("2d")!;
        bctx.setTransform(1, 0, 0, 1, 0, 0);
        bctx.globalAlpha = 1;
        bctx.drawImage(ctx.canvas, 0, 0); // background painted above
        bctx.setTransform(scale, 0, 0, scale, 0, 0);
        bctx.imageSmoothingEnabled = true;
        bctx.imageSmoothingQuality = "high";
        drawSteps(bctx, steps.slice(0, first));
        this.buffer = buffer;
        this.bufferKey = key;
      }
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(this.buffer, 0, 0);
      ctx.setTransform(scale, 0, 0, scale, 0, 0);
      drawSteps(ctx, steps.slice(first));
    } else {
      drawSteps(ctx, steps);
    }
    const caption = typeof params.caption === "string" ? params.caption : "";
    if (caption) {
      ctx.setTransform(scale, 0, 0, scale, 0, 0);
      ctx.fillStyle = "#10151ef0";
      ctx.fillRect(0, h * .94, w, h * .06);
      ctx.fillStyle = "#c3cddd";
      ctx.textBaseline = "top";
      ctx.font = `${Math.max(9, pyRound(w * .014))}px Montserrat, system-ui, sans-serif`;
      ctx.fillText(caption.slice(0, 170), w * .03, h * .95);
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }

  /** Pixels of this layer will not change on later frames (preview only:
   *  a swing below 0.01° moves a 500 px cutout by less than 0.1 px). */
  private still(rig: string, cue: Cue, elapsed: number, duration: number, active: boolean): boolean {
    if (rig === "static") return true;
    if (rig === "sequential") return !active || elapsed >= duration;
    const settle = typeof cue.settle_duration === "number" ? cue.settle_duration : .15;
    if (elapsed <= duration + Math.max(0, settle)) return false;
    if (rig !== "hanging_drop") return true;
    const swing = typeof cue.swing_deg === "number" ? cue.swing_deg : 3;
    const decay = typeof cue.swing_decay === "number" ? cue.swing_decay : 1.1;
    return Math.abs(swing) * Math.exp(-decay * elapsed) < .01;
  }

  private layer(ctx: CanvasRenderingContext2D, sprite: NonNullable<Sprite>, rig: string, cue: Cue,
    elapsed: number, duration: number, active: boolean, shadow: { blur: number; x: number; y: number }) {
    const { width: w, height: h } = this.def;
    const [b0, b1] = sprite.bounds;
    const withShadow = () => {
      ctx.shadowColor = "rgba(40, 26, 17, 0.2)";
      ctx.shadowBlur = shadow.blur;
      ctx.shadowOffsetX = shadow.x;
      ctx.shadowOffsetY = shadow.y;
    };
    const rotateAbout = (degrees: number, x: number, y: number) => {
      if (!degrees) return;
      ctx.translate(x, y);
      ctx.rotate(-degrees * Math.PI / 180); // PIL: counter-clockwise
      ctx.translate(-x, -y);
    };
    if (rig === "sequential") {
      // Legacy fade-and-drop entrance, kept for old parallax shots.
      let reveal = 1;
      if (active) {
        const fraction = duration ? Math.min(1, Math.max(0, elapsed / duration)) : 1;
        reveal = fraction * fraction * (3 - 2 * fraction);
      }
      const dropShare = typeof cue.drop === "number" ? cue.drop
        : typeof this.def.params.assembly_drop === "number" ? this.def.params.assembly_drop : .06;
      const drop = active ? pyRound((1 - reveal) * h * dropShare) : 0;
      ctx.globalAlpha = reveal;
      ctx.drawImage(sprite.canvas, b0, b1 + drop);
      return;
    }
    if (rig === "static") {
      ctx.drawImage(sprite.canvas, b0, b1);
      return;
    }
    const motion = rigMotion(rig, cue, elapsed, duration, sprite.bounds, w, h);
    if (rig === "hanging_drop") {
      const m = motion as HangingMotion;
      if (m.string_alpha > 0) {
        const line = Math.max(2, pyRound(w / 720));
        ctx.fillStyle = `rgba(62, 49, 38, ${m.string_alpha / 255})`;
        ctx.fillRect(m.anchor_x - line / 2 + .5, 0, line, Math.min(h - 1, m.anchor_y) + 1);
      }
      ctx.save();
      withShadow();
      rotateAbout(m.angle, m.pivot_x, m.pivot_y);
      ctx.drawImage(sprite.canvas, b0, b1 + m.dy_px);
      ctx.restore();
      if (m.pin) {
        const radius = Math.max(2, pyRound(w / 480));
        ctx.fillStyle = "rgba(50, 36, 28, 0.9)";
        ctx.beginPath();
        ctx.arc(m.anchor_x + .5, m.anchor_y + .5, radius + .5, 0, Math.PI * 2);
        ctx.fill();
      }
      return;
    }
    if (rig === "bottom_rise") {
      const m = motion as RiseMotion;
      withShadow();
      ctx.drawImage(sprite.canvas, b0, b1 + m.dy_px);
      return;
    }
    const m = motion as LiftMotion; // rake_lift
    if (m.stick > 0) {
      const line = Math.max(1, pyRound(w / 400));
      const x = pyRound(m.foot_x), y = pyRound(m.foot_y);
      ctx.fillStyle = "rgba(89, 62, 40, 0.784)";
      ctx.fillRect(x - line / 2 + .5, y, line, pyRound(m.foot_y + m.stick) - y + 1);
    }
    withShadow();
    rotateAbout(m.lean, m.foot_x, m.foot_y);
    ctx.drawImage(sprite.canvas, b0, m.top, sprite.canvas.width, m.sprite_height);
  }
}
