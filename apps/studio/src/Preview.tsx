import { useEffect, useRef } from "react";
import type { Project } from "./types";
import { mediaUrl } from "./api";
import { fps, interpolate, totalFrames } from "./timing";

export default function Preview({
  project,
  frame,
  playing,
  onFrame,
  onEnded,
}: {
  project: Project;
  frame: number;
  playing: boolean;
  onFrame: (frame: number) => void;
  onEnded: () => void;
}) {
  const canvas = useRef<HTMLCanvasElement>(null),
    images = useRef(new Map<string, HTMLImageElement>()),
    videos = useRef(new Map<string, HTMLVideoElement>()),
    audios = useRef(new Map<string, HTMLAudioElement>()),
    current = useRef({ project, frame, playing, onFrame, onEnded });
  current.current = { project, frame, playing, onFrame, onEnded };
  function draw() {
    const { project: p, frame: at, playing: play } = current.current;
    const node = canvas.current;
    if (!node) return;
    const ctx = node.getContext("2d");
    if (!ctx) return;
    const W = node.width,
      H = node.height;
    ctx.fillStyle = "#101318";
    ctx.fillRect(0, 0, W, H);
    const rate = fps(p),
      assets = new Map(p.assets.map((a) => [a.id, a]));
    const activeAudio = new Set<string>(),
      activeVideos = new Set<string>();
    for (const track of p.sequence.tracks) {
      if (track.muted) continue;
      for (const c of p.sequence.clips
        .filter(
          (c) =>
            c.track_id === track.id &&
            at >= c.start &&
            at < c.start + c.duration,
        )
        .sort((a, b) => a.start - b.start || a.id.localeCompare(b.id))) {
        const local = at - c.start,
          seconds = (c.source_in + local * c.speed) / rate,
          asset = c.asset_id ? assets.get(c.asset_id) : undefined;
        const fade =
          (c.fade_in ? Math.min(1, local / c.fade_in) : 1) *
          (c.fade_out ? Math.min(1, (c.duration - local) / c.fade_out) : 1);
        if (track.kind === "audio" && asset) {
          const a = audios.current.get(c.id);
          if (a) {
            activeAudio.add(c.id);
            a.volume = Math.min(1, interpolate(c, "volume", local) * fade);
            a.playbackRate = c.speed;
            if (Math.abs(a.currentTime - seconds) > 0.15)
              a.currentTime = seconds;
            if (play && a.paused) void a.play().catch(() => {});
            if (!play && !a.paused) a.pause();
          }
          continue;
        }
        let image: CanvasImageSource | undefined,
          iw = 0,
          ih = 0;
        if (asset?.kind === "image") {
          const img = images.current.get(asset.id);
          if (img?.complete && img.naturalWidth) {
            image = img;
            iw = img.naturalWidth;
            ih = img.naturalHeight;
          }
        }
        if (asset?.kind === "video") {
          const v = videos.current.get(c.id);
          if (v) {
            activeVideos.add(c.id);
            v.playbackRate = c.speed;
            if (Math.abs(v.currentTime - seconds) > (play ? 0.15 : 0.025))
              v.currentTime = seconds;
            if (play && v.paused) void v.play().catch(() => {});
            if (!play && !v.paused) v.pause();
            if (v.readyState >= 2) {
              image = v;
              iw = v.videoWidth;
              ih = v.videoHeight;
            }
          }
        }
        let scale = interpolate(c, "scale", local),
          x = interpolate(c, "x", local) * W,
          y = interpolate(c, "y", local) * H;
        const phase = Math.min(1, Math.max(0, local / c.duration));
        if (c.animation === "zoom-in") scale *= 1 + 0.08 * phase;
        if (c.animation === "zoom-out") scale *= 1.08 - 0.08 * phase;
        if (c.animation === "pan-left" || c.animation === "pan-right") {
          scale *= 1.1;
          x +=
            (c.animation === "pan-right" ? 1 : -1) * 0.05 * (2 * phase - 1) * W;
        }
        ctx.save();
        ctx.globalAlpha = Math.min(
          1,
          Math.max(0, interpolate(c, "opacity", local) * fade),
        );
        ctx.translate(W / 2 + x, H / 2 + y);
        ctx.rotate((interpolate(c, "rotation", local) * Math.PI) / 180);
        ctx.scale(scale, scale);
        if (track.kind === "text") {
          const fontSize = Math.max(16, W * 0.035);
          ctx.font = `${fontSize}px sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          const words = (c.text || c.title).split(/\s+/),
            lines: string[] = [];
          let line = "";
          for (const word of words) {
            const trial = (line + " " + word).trim();
            if (ctx.measureText(trial).width > W * 0.8 && line) {
              lines.push(line);
              line = word;
            } else line = trial;
          }
          lines.push(line);
          const lineH = fontSize * 1.4;
          ctx.fillStyle = "rgba(12,16,22,.83)";
          ctx.fillRect(
            -W * 0.43,
            (-lines.length * lineH) / 2 - 18,
            W * 0.86,
            lines.length * lineH + 36,
          );
          ctx.fillStyle = "#f4f2eb";
          lines
            .slice(0, 10)
            .forEach((l, i) =>
              ctx.fillText(l, 0, (i - (lines.length - 1) / 2) * lineH),
            );
        } else if (image) {
          const fit = Math.max(W / iw, H / ih);
          ctx.beginPath();
          ctx.rect(-W / 2, -H / 2, W, H);
          ctx.clip();
          ctx.drawImage(
            image,
            (-iw * fit) / 2,
            (-ih * fit) / 2,
            iw * fit,
            ih * fit,
          );
        }
        ctx.restore();
      }
    }
    for (const [cid, a] of audios.current)
      if (!activeAudio.has(cid) && !a.paused) a.pause();
    for (const [cid, v] of videos.current)
      if (!activeVideos.has(cid) && !v.paused) v.pause();
  }
  const redraw = useRef(draw);
  redraw.current = draw;
  useEffect(() => {
    const p = project;
    const assets = new Map(p.assets.map((a) => [a.id, a]));
    for (const asset of p.assets) {
      if (asset.kind === "image" && !images.current.has(asset.id)) {
        const image = new Image();
        image.onload = () => redraw.current();
        image.src = mediaUrl(p.id, asset.id);
        images.current.set(asset.id, image);
      }
    }
    for (const c of p.sequence.clips) {
      const asset = c.asset_id ? assets.get(c.asset_id) : undefined;
      const track = p.sequence.tracks.find((t) => t.id === c.track_id);
      if (track?.kind === "audio" && asset) {
        let a = audios.current.get(c.id);
        if (!a) {
          a = new Audio();
          audios.current.set(c.id, a);
        }
        if (a.dataset.asset !== asset.id) {
          a.src = mediaUrl(p.id, asset.id);
          a.dataset.asset = asset.id;
        }
      } else if (asset?.kind === "video") {
        let v = videos.current.get(c.id);
        if (!v) {
          v = document.createElement("video");
          v.muted = true;
          v.playsInline = true;
          v.preload = "auto";
          v.addEventListener("seeked", () => {
            if (!current.current.playing) redraw.current();
          });
          v.addEventListener("loadeddata", () => redraw.current());
          videos.current.set(c.id, v);
        }
        if (v.dataset.asset !== asset.id) {
          v.src = mediaUrl(p.id, asset.id);
          v.dataset.asset = asset.id;
        }
      }
    }
    draw();
  }, [project, frame]);
  useEffect(() => {
    if (!playing) {
      draw();
      for (const a of audios.current.values()) a.pause();
      for (const v of videos.current.values()) v.pause();
      return;
    }
    let handle = 0;
    const start = performance.now(),
      first = frame;
    function tick(now: number) {
      const state = current.current;
      const next =
        first + Math.floor(((now - start) / 1000) * fps(state.project));
      if (next >= totalFrames(state.project)) {
        state.onFrame(0);
        state.onEnded();
        return;
      }
      state.onFrame(next);
      redraw.current();
      handle = requestAnimationFrame(tick);
    }
    handle = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(handle);
  }, [playing]);
  useEffect(
    () => () => {
      for (const a of audios.current.values()) {
        a.pause();
        a.src = "";
      }
      for (const v of videos.current.values()) {
        v.pause();
        v.src = "";
      }
    },
    [],
  );
  const w = Math.min(960, project.sequence.width),
    h = Math.round((w * project.sequence.height) / project.sequence.width);
  return (
    <canvas
      ref={canvas}
      width={w}
      height={h}
      role="img"
      aria-label="Roboczy podgląd kompozycji osi czasu"
    />
  );
}
