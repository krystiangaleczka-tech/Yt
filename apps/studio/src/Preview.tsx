import { useEffect, useRef } from "react";
import type { Project } from "./types";
import { api, mediaUrl } from "./api";
import { useStudio } from "./context";
import { fps, interpolate, totalFrames } from "./timing";
import {
  audioFrame,
  primaryAudioClip,
  syncMedia,
  pauseMedia,
} from "./playback";

export default function Preview({
  project,
  frame,
  playing,
  onFrame,
  onEnded,
  transparent = false,
}: {
  project: Project;
  frame: number;
  playing: boolean;
  onFrame: (frame: number) => void;
  onEnded: () => void;
  transparent?: boolean;
}) {
  const studio = useStudio(),
    proxyChecked = useRef(new Set<string>()),
    proxyReady = useRef(new Map<string, string>());
  const canvas = useRef<HTMLCanvasElement>(null),
    images = useRef(new Map<string, HTMLImageElement>()),
    videos = useRef(new Map<string, HTMLVideoElement>()),
    audios = useRef(new Map<string, HTMLAudioElement>()),
    current = useRef({ project, frame, playing, onFrame, onEnded, transparent });
  current.current = { project, frame, playing, onFrame, onEnded, transparent };
  function playbackError(error: unknown) {
    current.current.onEnded();
    const blocked =
      error instanceof DOMException && error.name === "NotAllowedError";
    studio.notify(
      blocked
        ? "Przeglądarka zablokowała dźwięk. Zezwól na odtwarzanie audio dla Studio i ponów Play."
        : "Nie udało się odtworzyć medium. Sprawdź nagranie w bibliotece i ponów Play.",
      true,
    );
  }
  function draw(at = current.current.frame) {
    const { project: p, playing: play } = current.current;
    const node = canvas.current;
    if (!node) return;
    const ctx = node.getContext("2d");
    if (!ctx) return;
    const W = node.width,
      H = node.height;
    ctx.clearRect(0, 0, W, H);
    if (!current.current.transparent) {
      ctx.fillStyle = "#101318";
      ctx.fillRect(0, 0, W, H);
    }
    const rate = fps(p),
      assets = new Map(p.assets.map((a) => [a.id, a]));
    const primary = primaryAudioClip(p, at),
      clock = primary ? audios.current.get(primary.id) : undefined,
      waiting =
        !!primary &&
        (!clock || clock.paused || clock.seeking || clock.readyState < 2);
    const activeAudio = new Set<string>(),
      activeVideos = new Set<string>();
    const transitions = new Map(
      p.sequence.clips
        .filter(
          (c) =>
            c.transition_duration &&
            !["cut", "fade-black"].includes(c.transition || "cut"),
        )
        .map((c) => [c.track_id + ":" + c.start, c.transition_duration || 0]),
    );
    const solo = p.sequence.tracks.some((t) => t.solo),
      audible = p.sequence.tracks.filter((t) => !t.muted && (!solo || t.solo)),
      narration = p.sequence.clips.some(
        (c) =>
          at >= c.start &&
          at < c.start + c.duration &&
          audible.some((t) => t.id === c.track_id && t.role === "narration"),
      );
    for (const track of p.sequence.tracks) {
      if (track.muted || (solo && !track.solo)) continue;
      for (const c of p.sequence.clips
        .filter(
          (c) =>
            c.track_id === track.id &&
            at >= c.start &&
            at <
              c.start +
                c.duration +
                (track.kind !== "audio"
                  ? transitions.get(
                      c.track_id + ":" + (c.start + c.duration),
                    ) || 0
                  : 0),
        )
        .sort((a, b) => a.start - b.start || a.id.localeCompare(b.id))) {
        const local = Math.min(c.duration - 1, at - c.start),
          seconds = (c.source_in + local * c.speed) / rate,
          asset = c.asset_id ? assets.get(c.asset_id) : undefined;
        const fade = Math.min(
          c.fade_in ? Math.min(1, local / c.fade_in) : 1,
          c.fade_out ? Math.min(1, (c.duration - local) / c.fade_out) : 1,
        );
        if (track.kind === "audio" && asset) {
          const a = audios.current.get(c.id);
          if (a) {
            activeAudio.add(c.id);
            const volume = Math.min(
              1,
              interpolate(c, "volume", local) *
                fade *
                (p.sequence.ducking && track.role === "music" && narration
                  ? p.sequence.ducking_gain
                  : 1),
            );
            if (Math.abs(a.volume - volume) > 0.0001) a.volume = volume;
            syncMedia(
              a,
              seconds,
              play && (!waiting || primary?.id === c.id),
              c.speed,
              `${p.id}:${a.src}:${c.start}:${c.source_in}:${c.speed}`,
              playbackError,
            );
          }
          continue;
        }
        let image: CanvasImageSource | undefined,
          iw = 0,
          ih = 0;
        if (c.template && c.template !== "media") {
          const step = Math.max(1, Math.round(rate / 2)),
            q = Math.floor(local / step) * step,
            key = `poster:${c.id}:${p.revision}:${q}`;
          const img = images.current.get(key);
          if (img?.complete && img.naturalWidth) {
            image = img;
            iw = img.naturalWidth;
            ih = img.naturalHeight;
          }
        } else if (asset?.kind === "image") {
          const img = images.current.get(asset.id);
          if (img?.complete && img.naturalWidth) {
            image = img;
            iw = img.naturalWidth;
            ih = img.naturalHeight;
          }
        }
        if (
          (!c.template || c.template === "media") &&
          asset?.kind === "video"
        ) {
          const v = videos.current.get(c.id);
          if (v) {
            activeVideos.add(c.id);
            syncMedia(
              v,
              seconds,
              play && !waiting,
              c.speed,
              `${p.id}:${v.src}:${c.start}:${c.source_in}:${c.speed}`,
              playbackError,
            );
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
        const transition = c.transition_duration
          ? Math.min(1, local / c.transition_duration)
          : 1;
        if (c.transition === "slide-left" || c.transition === "slide-right")
          x += (c.transition === "slide-left" ? 1 : -1) * (1 - transition) * W;
        if (c.transition === "zoom") scale *= 1.15 - 0.15 * transition;
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
          Math.max(
            0,
            interpolate(c, "opacity", local) *
              fade *
              (["dissolve", "fade-black", "zoom"].includes(c.transition || "")
                ? transition
                : 1),
          ),
        );
        ctx.translate(W / 2 + x, H / 2 + y);
        ctx.rotate((interpolate(c, "rotation", local) * Math.PI) / 180);
        ctx.scale(scale, scale);
        if (c.transition === "wipe-left" || c.transition === "wipe-right") {
          ctx.beginPath();
          ctx.rect(
            c.transition === "wipe-right" ? -W / 2 : W / 2 - W * transition,
            -H / 2,
            W * transition,
            H,
          );
          ctx.clip();
        }
        if (track.kind === "text") {
          const fontSize = Math.max(16, W * 0.035);
          ctx.font = `${fontSize}px '${p.channel_profile.font === "courier" ? "DocOS Courier" : p.channel_profile.font === "courier-bold" ? "DocOS Courier Bold" : "DocOS Film"}', sans-serif`;
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
          const width = W / fit,
            height = H / fit,
            crop = c.crop || {},
            sx = (iw - width) / 2 + width * (crop.x || 0),
            sy = (ih - height) / 2 + height * (crop.y || 0);
          ctx.drawImage(
            image,
            sx,
            sy,
            width * (crop.width || 1),
            height * (crop.height || 1),
            -W / 2,
            -H / 2,
            W,
            H,
          );
        }
        ctx.restore();
      }
    }
    for (const [cid, a] of audios.current)
      if (!activeAudio.has(cid)) pauseMedia(a);
    for (const [cid, v] of videos.current)
      if (!activeVideos.has(cid)) pauseMedia(v);
  }
  const redraw = useRef(draw);
  redraw.current = draw;
  useEffect(() => {
    const p = project;
    const assets = new Map(p.assets.map((a) => [a.id, a]));
    const windowClips = p.sequence.clips.filter(
        (c) =>
          c.start < frame + fps(p) * 4 &&
          c.start + c.duration > frame - fps(p) * 2,
      ),
      active = windowClips.filter(
        (c) => c.start <= frame && c.start + c.duration > frame,
      ),
      nearby = [
        ...active,
        ...windowClips
          .filter((c) => !active.includes(c))
          .sort((a, b) => Math.abs(a.start - frame) - Math.abs(b.start - frame))
          .slice(0, 12),
      ],
      needed = new Set(nearby.map((c) => c.asset_id).filter(Boolean));
    for (const asset of p.assets) {
      if (
        needed.has(asset.id) &&
        asset.kind === "image" &&
        !images.current.has(asset.id)
      ) {
        const image = new Image();
        image.onload = () => redraw.current();
        image.src = mediaUrl(p.id, asset.id);
        images.current.set(asset.id, image);
      }
    }
    const posterKeys = new Set<string>();
    for (const c of nearby) {
      const asset = c.asset_id ? assets.get(c.asset_id) : undefined;
      const track = p.sequence.tracks.find((t) => t.id === c.track_id);
      if (c.template && c.template !== "media") {
        const step = Math.max(1, Math.round(fps(p) / 2)),
          q =
            Math.floor(
              Math.max(0, Math.min(c.duration - 1, frame - c.start)) / step,
            ) * step,
          key = `poster:${c.id}:${p.revision}:${q}`;
        posterKeys.add(key);
        if (!images.current.has(key)) {
          const image = new Image();
          image.onload = () => redraw.current();
          image.src = `/api/projects/${p.id}/clips/${c.id}/poster?revision=${p.revision}&frame=${q}`;
          images.current.set(key, image);
        }
      }
      if (track?.kind === "audio" && asset) {
        let a = audios.current.get(c.id);
        if (!a) {
          a = new Audio();
          a.preload = "auto";
          audios.current.set(c.id, a);
        }
        if (a.dataset.asset !== asset.id) {
          a.src = mediaUrl(p.id, asset.id);
          a.dataset.asset = asset.id;
        }
      } else if (
        (!c.template || c.template === "media") &&
        asset?.kind === "video"
      ) {
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
        const completed = studio.jobs.some(
            (j) =>
              j.project_id === p.id &&
              j.kind === "proxy" &&
              j.status === "SUCCEEDED" &&
              j.result?.asset_id === asset.id,
          ),
          identity = p.id + asset.id + Number(completed);
        if (!proxyChecked.current.has(identity)) {
          proxyChecked.current.add(identity);
          void api<{ ready: boolean; url: string }>(
            `/projects/${p.id}/assets/${asset.id}/proxy-status`,
          )
            .then((result) => {
              if (result.ready) {
                proxyReady.current.set(asset.id, result.url);
                const video = videos.current.get(c.id);
                if (
                  video &&
                  video.dataset.asset === asset.id &&
                  video.dataset.proxy !== result.url
                ) {
                  video.src = result.url;
                  video.dataset.proxy = result.url;
                }
              }
            })
            .catch(() => {});
        }
        const proxy = proxyReady.current.get(asset.id);
        if (proxy && v.dataset.proxy !== proxy) {
          v.src = proxy;
          v.dataset.proxy = proxy;
        }
      }
    }
    if (images.current.size > 20)
      for (const [key, image] of images.current)
        if (!needed.has(key) && !posterKeys.has(key)) {
          image.src = "";
          images.current.delete(key);
        }
    const ids = new Set(nearby.map((c) => c.id));
    for (const collection of [videos.current, audios.current])
      for (const [id, media] of collection)
        if (!ids.has(id)) {
          pauseMedia(media);
          media.src = "";
          collection.delete(id);
        }
    draw();
  }, [project, frame, studio.jobs]);
  useEffect(() => {
    if (!playing) {
      draw();
      for (const a of audios.current.values()) pauseMedia(a);
      for (const v of videos.current.values()) pauseMedia(v);
      return;
    }
    let handle = 0,
      cursor = frame,
      anchorFrame = frame,
      anchorTime = performance.now();
    redraw.current(frame);
    function tick(now: number) {
      const state = current.current;
      const primary = primaryAudioClip(state.project, cursor);
      let next: number;
      if (primary) {
        next = audioFrame(
          primary,
          audios.current.get(primary.id),
          fps(state.project),
          cursor,
        );
        anchorFrame = next;
        anchorTime = now;
      } else
        next =
          anchorFrame +
          Math.floor(((now - anchorTime) / 1000) * fps(state.project));
      if (next >= totalFrames(state.project)) {
        state.onFrame(0);
        state.onEnded();
        return;
      }
      if (next !== cursor) state.onFrame(next);
      cursor = next;
      redraw.current(next);
      handle = requestAnimationFrame(tick);
    }
    handle = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(handle);
  }, [playing]);
  useEffect(
    () => () => {
      for (const a of audios.current.values()) {
        pauseMedia(a);
        a.src = "";
      }
      for (const v of videos.current.values()) {
        pauseMedia(v);
        v.src = "";
      }
      for (const image of images.current.values()) image.src = "";
      images.current.clear();
      videos.current.clear();
      audios.current.clear();
      proxyChecked.current.clear();
      proxyReady.current.clear();
    },
    [],
  );
  useEffect(() => {
    void document.fonts.load("16px 'DocOS Film'").then(() => redraw.current());
  }, []);
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
