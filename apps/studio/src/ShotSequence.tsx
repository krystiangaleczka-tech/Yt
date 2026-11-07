import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { Image as ImageIcon } from "lucide-react";
import { mediaUrl } from "./api";
import { fps } from "./timing";
import type { Asset, Project, Scene } from "./types";

type Shot = { kind: "video" | "image" | "poster" | "empty"; src: string };

function shotSource(
  p: Project,
  scene: Scene,
  assets: Map<string, Asset>,
): Shot {
  if (scene.template && scene.template !== "media")
    return {
      kind: "poster",
      src: `/api/projects/${p.id}/scenes/${scene.id}/poster?revision=${p.revision}&frame=0`,
    };
  const asset = scene.asset_id ? assets.get(scene.asset_id) : undefined;
  if (asset?.kind === "video")
    return { kind: "video", src: mediaUrl(p.id, asset.id) };
  if (asset?.kind === "image")
    return { kind: "image", src: mediaUrl(p.id, asset.id) };
  return { kind: "empty", src: "" };
}

/**
 * Odtwarza ujęcia po kolei, bez przerw między nimi. Dwa odtwarzacze wideo pracują na zmianę: gdy jeden gra bieżące
 * ujęcie, drugi wczytuje następne, więc cięcie nie pokazuje czarnej klatki. Każde ujęcie trwa tyle, ile na osi
 * (scene.duration); obraz bez ruchu stoi przez ten czas.
 */
export default function ShotSequence({
  project,
  start,
  onShot,
  onEnd,
}: {
  project: Project;
  start: number;
  onShot: (sceneId: string) => void;
  onEnd: () => void;
}) {
  const [index, setIndex] = useState(start);
  const first = useRef<HTMLVideoElement>(null),
    second = useRef<HTMLVideoElement>(null);
  const assets = useMemo(
    () => new Map<string, Asset>(project.assets.map((a) => [a.id, a])),
    [project.assets],
  );
  const live = useRef({ project, assets, onShot, onEnd });
  live.current = { project, assets, onShot, onEnd };
  const scene = project.scenes[index];
  const shot: Shot = scene
    ? shotSource(project, scene, assets)
    : { kind: "empty", src: "" };
  const rate = fps(project);
  // useLayoutEffect: podmiana odtwarzaczy musi zdążyć przed narysowaniem klatki, inaczej cięcie mignie.
  useLayoutEffect(() => {
    const { project: p, assets: byId } = live.current;
    const current = p.scenes[index];
    if (!current) {
      live.current.onEnd();
      return;
    }
    live.current.onShot(current.id);
    const slots = [first.current!, second.current!];
    const now = shotSource(p, current, byId);
    const limit = current.duration / fps(p);
    let video: HTMLVideoElement | null = null,
      show: (() => void) | null = null;
    if (now.kind === "video") {
      // Wcześniej wczytany odtwarzacz albo ten, który teraz nie jest widoczny (poprzednia klatka zostaje na ekranie).
      const target =
        slots.find((v) => v.dataset.scene === current.id) ||
        slots.find((v) => v.style.visibility !== "visible") ||
        slots[0];
      video = target;
      if (target.dataset.scene !== current.id) {
        target.dataset.scene = current.id;
        target.src = now.src;
      } else if (target.currentTime > 0) target.currentTime = 0;
      for (const v of slots) if (v !== target) v.pause();
      show = () => {
        target.style.visibility = "visible";
        for (const v of slots) if (v !== target) v.style.visibility = "hidden";
      };
      void target.play().catch(() => {});
      if (target.readyState >= 2) show();
      else target.addEventListener("loadeddata", show, { once: true });
    } else
      for (const v of slots) {
        v.pause();
        v.style.visibility = "hidden";
      }
    const next = p.scenes[index + 1];
    if (next) {
      const upcoming = shotSource(p, next, byId);
      if (upcoming.kind === "video") {
        const spare =
          slots.find((v) => v.dataset.scene === next.id) ||
          slots.find((v) => v !== video)!;
        if (spare.dataset.scene !== next.id) {
          spare.dataset.scene = next.id;
          spare.src = upcoming.src;
        }
      } else if (upcoming.src) new Image().src = upcoming.src;
    }
    const began = performance.now(),
      half = 0.5 / fps(p);
    let frame = 0,
      endedAt = 0;
    function tick(clock: number) {
      let t: number;
      if (video && !video.error) {
        // Klip krótszy niż ujęcie: ostatnia klatka stoi do końca ujęcia.
        if (video.ended) endedAt ||= clock;
        t = video.currentTime + (endedAt ? (clock - endedAt) / 1000 : 0);
      } else t = (clock - began) / 1000;
      if (t >= limit - half) {
        if (index + 1 < live.current.project.scenes.length) setIndex(index + 1);
        else live.current.onEnd();
        return;
      }
      frame = requestAnimationFrame(tick);
    }
    frame = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(frame);
      if (video && show) video.removeEventListener("loadeddata", show);
    };
  }, [index]);
  useEffect(
    () => () => {
      for (const v of [first.current, second.current])
        if (v) {
          v.pause();
          v.removeAttribute("src");
          v.load();
        }
    },
    [],
  );
  return (
    <div className="shot-sequence">
      <video ref={first} muted playsInline preload="auto" />
      <video ref={second} muted playsInline preload="auto" />
      {scene && shot.kind !== "video" && (
        <div
          key={scene.id}
          className={`sequence-still ${shot.kind === "image" ? "animate-" + scene.animation : ""}`}
        >
          {shot.src ? (
            <img
              src={shot.src}
              alt={scene.title}
              style={{ animationDuration: `${scene.duration / rate}s` }}
            />
          ) : (
            <div className="no-preview">
              <ImageIcon size={38} />
              <span>Ujęcie bez materiału</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
