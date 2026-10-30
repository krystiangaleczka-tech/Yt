import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Image as ImageIcon,
  Layers3,
  Plus,
  Search,
  Trash2,
  Upload,
} from "lucide-react";
import { useStudio } from "./context";
import { api, id, mediaUrl, upload } from "./api";
import {
  AssetThumb,
  Button,
  CommitText,
  Empty,
  Field,
  IconButton,
  NumberField,
} from "./components";
import SceneBoard from "./SceneBoard";
import FrameReview from "./FrameReview";
import { annotationFrame } from "./frameAnnotations";
import PaperTheatre from "./PaperTheatre";
import Preview from "./Preview";
import { LiveScene } from "./paperTheatreRenderer";
import type { Cue } from "./paperTheatreMotion";
import { animations } from "./Generation";
import { fps, newClip } from "./timing";
import {
  changePaperLayer,
  paperCues,
  paperLayerIds,
  shotEntries,
} from "./sceneWorkspace";
import { ShotTimeline, ShotTransport, useShotPlayback } from "./ShotControls";
import type { ShotTrack } from "./ShotControls";
import type { Asset, Clip, Project, Scene, Track } from "./types";

export default function ShotEditor() {
  const s = useStudio(),
    p = s.project!;
  const entries = shotEntries(p),
    index = entries.findIndex((entry) => entry.scene.id === s.targetScene);
  const entry = entries[index];
  return (
    <div className="shot-editor-page">
      <header className="shot-editor-header">
        <Button icon={ArrowLeft} onClick={() => s.setPage("scenes")}>
          Wszystkie sceny
        </Button>
        <div className="shot-editor-title">
          <span className="small muted">
            EDYCJA UJĘCIA {index >= 0 ? String(index + 1).padStart(2, "0") : ""}
          </span>
          <h1>{entry?.scene.title || "Ujęcie niedostępne"}</h1>
        </div>
        <span className="badge quiet">
          {s.saving
            ? "Zapisywanie…"
            : s.saveError
              ? "Błąd zapisu"
              : "Zapis automatyczny"}
        </span>
        <IconButton
          icon={ChevronLeft}
          label="Poprzednie ujęcie"
          disabled={index <= 0}
          onClick={() => s.setTargetScene(entries[index - 1].scene.id)}
        />
        <IconButton
          icon={ChevronRight}
          label="Następne ujęcie"
          disabled={index < 0 || index >= entries.length - 1}
          onClick={() => s.setTargetScene(entries[index + 1].scene.id)}
        />
      </header>
      {!entry ? (
        <Empty title="Nie znaleziono wybranego ujęcia">
          Wróć do scen i wybierz ujęcie do edycji.
        </Empty>
      ) : entry.kind === "stage" ? (
        <SceneBoard key={p.id} shotId={entry.scene.id} />
      ) : (
        <MediaShotEditor key={entry.scene.id} scene={entry.scene} />
      )}
    </div>
  );
}

/** The shot workspace uses its own clock. Clips from other shots never enter the preview. */
function MediaShotEditor({ scene }: { scene: Scene }) {
  const s = useStudio(),
    p = s.project!,
    rate = fps(p);
  const [selected, setSelected] = useState("background");
  const [selectedNote, setSelectedNote] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState<"composition" | "setup">("composition");
  const file = useRef<HTMLInputElement>(null);
  const playback = useShotPlayback(scene.duration, rate, scene.id, true);
  const paper =
    scene.template === "paper-theatre" || scene.template === "parallax";
  const [posterLoaded, setPosterLoaded] = useState("");
  const posterNeeded = !!scene.template && scene.template !== "media" && !paper;
  const wantedPosterFrame = playback.playing
    ? Math.floor(playback.frame / Math.max(1, Math.round(rate / 2))) *
      Math.max(1, Math.round(rate / 2))
    : playback.frame;
  const [posterFrame, setPosterFrame] = useState(wantedPosterFrame);
  useEffect(() => {
    if (!posterNeeded) return;
    const timer = window.setTimeout(
      () => setPosterFrame(wantedPosterFrame),
      playback.playing ? 0 : 120,
    );
    return () => window.clearTimeout(timer);
  }, [posterNeeded, wantedPosterFrame, playback.playing]);
  const layerIds = paperLayerIds(scene),
    cues = paperCues(scene);
  const cueIndex = selected.startsWith("paper:")
    ? Number(selected.slice(6))
    : 0;
  const cue = cues.find((item) => item.layer === cueIndex);
  const layerAsset = p.assets.find(
    (asset) => asset.id === layerIds[cueIndex - 1],
  );
  const extras = p.sequence.clips.filter(
    (clip) => clip.scene_id === scene.id && clip.track_id !== "v1",
  );
  const clip = extras.find((item) => item.id === selected);
  const clipTrack = p.sequence.tracks.find(
    (track) => track.id === clip?.track_id,
  );
  const clipLocked = !!(
    scene.locked ||
    scene.lock_media ||
    clip?.locked ||
    clipTrack?.locked
  );
  const mediaLocked = !!(scene.locked || scene.lock_media);
  const assets = p.assets.filter(
    (asset) =>
      asset.kind !== "document" &&
      asset.name
        .toLocaleLowerCase("pl")
        .includes(query.toLocaleLowerCase("pl")),
  );
  function change(changes: Partial<Scene> | ((current: Scene) => Scene)) {
    s.run(() =>
      s.patch((current) => ({
        scenes: current.scenes.map((item) =>
          item.id === scene.id
            ? typeof changes === "function"
              ? changes(item)
              : { ...item, ...changes }
            : item,
        ),
      })),
    );
  }
  function changeCue(changes: Partial<Cue>) {
    change((current) => changePaperLayer(current, cueIndex, changes));
  }
  function changeClip(changes: Partial<Clip>) {
    if (clip)
      s.run(() => s.edit([{ type: "update_clip", clip_id: clip.id, changes }]));
  }
  function useAsset(asset: Asset) {
    if (asset.kind === "audio")
      s.run(() =>
        s.mutate((current) =>
          api<Project>(
            `/projects/${current.id}/scenes/${scene.id}/voice/select`,
            {
              expected_revision: current.revision,
              asset_id: asset.id,
            },
          ),
        ),
      );
    else change({ asset_id: asset.id, mode: "library" });
  }
  async function addLayer(asset: Asset) {
    if (paper && asset.kind === "image") {
      s.notify(
        "Dodaj wycinek w zakładce Przygotowanie warstw, aby ustawić jego rolę i wejście.",
      );
      setTab("setup");
      return;
    }
    const audio = asset.kind === "audio";
    const track: Track = {
      id: id("track_"),
      name: asset.name,
      kind: audio ? "audio" : "video",
      role: audio ? "effects" : "overlay",
      locked: false,
      muted: false,
    };
    const next = newClip(
      track.id,
      asset.id,
      scene.start + playback.frame,
      Math.max(
        1,
        Math.min(
          scene.duration - playback.frame,
          asset.duration ? Math.round(asset.duration * rate) : scene.duration,
        ),
      ),
    );
    next.scene_id = scene.id;
    next.title = asset.name;
    await s.edit([
      { type: "add_track", track },
      { type: "add_clip", clip: next },
    ]);
    setSelected(next.id);
  }
  const preview = useMemo(() => {
    const base: Clip = {
      ...newClip(
        "v1",
        scene.template && scene.template !== "media" ? null : scene.asset_id,
        0,
        scene.duration,
      ),
      id: "shot-preview",
      scene_id: scene.id,
      title: scene.title,
      template: "media",
      animation: scene.animation,
    };
    const clips = [
      base,
      ...extras
        .filter(
          (item) =>
            item.start < scene.start + scene.duration &&
            item.start + item.duration > scene.start,
        )
        .map((item) => ({
          ...item,
          start: item.start - scene.start,
          duration: Math.min(
            item.duration,
            scene.start + scene.duration - item.start,
          ),
        })),
    ];
    if (
      scene.voice_asset_id &&
      !clips.some((item) => item.asset_id === scene.voice_asset_id)
    )
      clips.push({
        ...newClip(
          "a1",
          scene.voice_asset_id,
          0,
          Math.min(
            scene.duration,
            Math.max(
              1,
              Math.round(
                (p.assets.find((asset) => asset.id === scene.voice_asset_id)
                  ?.duration || scene.duration / rate) * rate,
              ),
            ),
          ),
        ),
        id: "shot-voice-preview",
        scene_id: scene.id,
      });
    return { ...p, sequence: { ...p.sequence, clips } };
  }, [p, scene]);
  const rows: ShotTrack[] = [
    {
      id: "background",
      name: paper ? "Tło" : "Obraz ujęcia",
      start: 0,
      duration: scene.duration / rate,
    },
    ...(paper
      ? layerIds.map((assetId, i) => {
          const item = cues.find((value) => value.layer === i + 1);
          return {
            id: `paper:${i + 1}`,
            name:
              p.assets.find((asset) => asset.id === assetId)?.name ||
              `Warstwa ${i + 1}`,
            start: item?.start || 0,
            duration: scene.duration / rate - (item?.start || 0),
            movable: !mediaLocked,
          };
        })
      : []),
    ...(scene.voice_asset_id
      ? [
          {
            id: "voice",
            name: "Narracja",
            start: 0,
            duration: scene.duration / rate,
            kind: "audio" as const,
          },
        ]
      : []),
    ...extras.map((item) => ({
      id: item.id,
      name: item.title,
      start: (item.start - scene.start) / rate,
      duration: item.duration / rate,
      kind:
        p.sequence.tracks.find((track) => track.id === item.track_id)?.kind ===
        "audio"
          ? ("audio" as const)
          : ("visual" as const),
      movable: !(
        item.locked ||
        mediaLocked ||
        p.sequence.tracks.find((track) => track.id === item.track_id)?.locked
      ),
    })),
  ];
  function selectLayer(value: string) {
    playback.setPlaying(false);
    setSelected(value);
  }
  function moveLayer(value: string, seconds: number) {
    if (value.startsWith("paper:"))
      change((current) =>
        changePaperLayer(current, Number(value.slice(6)), { start: seconds }),
      );
    else
      s.run(() =>
        s.edit([
          {
            type: "move_clip",
            clip_id: value,
            move_group: false,
            changes: { start: scene.start + Math.round(seconds * rate) },
          },
        ]),
      );
  }
  async function toTimeline() {
    await s.mutate((current) =>
      api<Project>(`/projects/${current.id}/scenes/${scene.id}/to-timeline`, {
        expected_revision: current.revision,
        sync_timing: !scene.lock_timing,
        sync_shot: true,
      }),
    );
    s.notify("Zastosowano ujęcie w montażu filmu.");
  }
  return (
    <>
      <div
        className="shot-editor-tabs"
        role="group"
        aria-label="Widok edytora ujęcia"
      >
        <Button
          primary={tab === "composition"}
          onClick={() => setTab("composition")}
        >
          Edycja ujęcia
        </Button>
        {scene.template === "paper-theatre" && (
          <Button
            primary={tab === "setup"}
            onClick={() => {
              playback.setPlaying(false);
              setTab("setup");
            }}
          >
            Przygotowanie warstw
          </Button>
        )}
        {scene.locked && (
          <Button onClick={() => change({ locked: false })}>
            Odblokuj ujęcie
          </Button>
        )}
        <Button onClick={() => s.run(toTimeline)} disabled={mediaLocked}>
          Zastosuj do montażu
        </Button>
      </div>
      {tab === "setup" ? (
        <div className="shot-preparation">
          <PaperTheatre shotId={scene.id} embedded />
        </div>
      ) : (
        <div className="shot-workspace">
          <aside className="shot-assets">
            <div className="shot-panel-heading">
              <strong>Assety</strong>
              <span className="badge quiet">{assets.length}</span>
            </div>
            <label className="scene-search">
              <Search size={14} />
              <input
                aria-label="Szukaj assetów"
                placeholder="Szukaj assetu…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
            <Button icon={Upload} onClick={() => file.current?.click()}>
              Wczytaj plik
            </Button>
            <input
              hidden
              type="file"
              ref={file}
              accept="image/*,video/*,audio/*"
              onChange={(event) => {
                const value = event.target.files?.[0];
                event.target.value = "";
                if (value)
                  s.run(async () => {
                    const result = await upload<{ project: Project }>(
                      `/projects/${p.id}/media`,
                      value,
                    );
                    s.accept(result.project);
                    s.notify("Dodano plik do assetów filmu.");
                  });
              }}
            />
            <div className="shot-asset-list">
              {assets.map((asset) => (
                <div className="shot-asset" key={asset.id}>
                  <AssetThumb asset={asset} project={p} />
                  <span className="small">{asset.name}</span>
                  <div className="button-row">
                    <Button
                      subtle
                      disabled={
                        asset.kind === "audio"
                          ? scene.locked || scene.lock_narration
                          : mediaLocked
                      }
                      onClick={() => useAsset(asset)}
                    >
                      {asset.kind === "audio"
                        ? "Jako narracja"
                        : paper
                          ? "Jako tło"
                          : "Użyj obrazu"}
                    </Button>
                    <IconButton
                      icon={Plus}
                      label={`Dodaj warstwę: ${asset.name}`}
                      disabled={mediaLocked || scene.lock_timing}
                      onClick={() => s.run(() => addLayer(asset))}
                    />
                  </div>
                </div>
              ))}
            </div>
            {!assets.length && (
              <p className="small muted">
                Wczytaj obrazy, wycinki, nagrania lub wideo.
              </p>
            )}
          </aside>
          <main className="shot-center">
            <section className="shot-preview-panel surface">
              <div className="shot-panel-heading">
                <strong>Podgląd ujęcia</strong>
                <span className="small muted">
                  {p.sequence.width} × {p.sequence.height}
                </span>
              </div>
              <FrameReview
                sceneId={scene.id}
                frame={playback.frame}
                total={scene.duration}
                rate={rate}
                playing={playback.playing}
                ready={
                  !posterNeeded ||
                  posterLoaded === `${p.revision}:${playback.frame}`
                }
                onPause={() => playback.setPlaying(false)}
                onSeek={playback.seek}
                selectedId={selectedNote}
                onSelect={setSelectedNote}
              >
                <div className="shot-canvas">
                  {paper ? (
                    <LayeredShotCanvas
                      project={p}
                      scene={scene}
                      frame={playback.frame}
                    />
                  ) : scene.template && scene.template !== "media" ? (
                    <img
                      alt="Podgląd ujęcia"
                      src={`/api/projects/${p.id}/scenes/${scene.id}/poster?revision=${p.revision}&frame=${posterFrame}`}
                      onLoad={(event) => {
                        const src = new URL(
                          event.currentTarget.currentSrc ||
                            event.currentTarget.src,
                        );
                        setPosterLoaded(
                          `${src.searchParams.get("revision")}:${src.searchParams.get("frame")}`,
                        );
                      }}
                      onError={() => {
                        playback.setPlaying(false);
                        s.notify(
                          "Nie udało się wczytać wybranej klatki.",
                          true,
                        );
                      }}
                    />
                  ) : (
                    <Preview
                      project={preview}
                      frame={playback.frame}
                      playing={playback.playing}
                      onFrame={playback.setFrame}
                      onEnded={() => playback.setPlaying(false)}
                    />
                  )}
                  {(paper ||
                    (scene.template && scene.template !== "media")) && (
                    <div className="shot-overlay-preview">
                      <Preview
                        project={preview}
                        frame={playback.frame}
                        playing={playback.playing}
                        onFrame={playback.setFrame}
                        onEnded={() => playback.setPlaying(false)}
                        transparent
                      />
                    </div>
                  )}
                  {!scene.asset_id &&
                    (!scene.template ||
                      scene.template === "media" ||
                      paper) && (
                      <div className="shot-empty-preview">
                        <ImageIcon size={32} />
                        <span>Wybierz obraz lub tło z assetów</span>
                      </div>
                    )}
                </div>
              </FrameReview>
              <ShotTransport
                playback={playback}
                total={scene.duration}
                rate={rate}
              />
            </section>
            <ShotTimeline
              rows={rows}
              seconds={scene.duration / rate}
              frame={playback.frame}
              rate={rate}
              selected={selected}
              onSelect={selectLayer}
              onSeek={playback.seek}
              onMove={moveLayer}
              annotations={(p.frame_annotations || []).filter(
                (note) => note.scene_id === scene.id,
              )}
              onAnnotationSelect={(note) => {
                playback.seek(annotationFrame(note, rate));
                setSelectedNote(note.id);
              }}
            />
          </main>
          <aside className="shot-layers">
            <div className="shot-panel-heading">
              <strong>
                <Layers3 size={16} /> Warstwy
              </strong>
              <span className="badge quiet">{rows.length}</span>
            </div>
            <div className="shot-layer-list">
              {[...rows].reverse().map((row) => (
                <button
                  key={row.id}
                  className={row.id === selected ? "active" : ""}
                  onClick={() => selectLayer(row.id)}
                >
                  <Layers3 size={14} />
                  <span>{row.name}</span>
                </button>
              ))}
            </div>
            {cueIndex > 0 && (
              <section className="shot-layer-properties" key={selected}>
                <h2>{layerAsset?.name || `Warstwa ${cueIndex}`}</h2>
                <fieldset disabled={mediaLocked}>
                  <div className="two-fields">
                    <NumberField
                      label="X (0–1)"
                      value={cue?.layout_x ?? 0.5}
                      min={0}
                      max={1}
                      step={0.01}
                      onCommit={(layout_x) => changeCue({ layout_x })}
                    />
                    <NumberField
                      label="Y (0–1)"
                      value={cue?.layout_y ?? 0.5}
                      min={0}
                      max={1}
                      step={0.01}
                      onCommit={(layout_y) => changeCue({ layout_y })}
                    />
                  </div>
                  <NumberField
                    label="Szerokość warstwy"
                    value={cue?.layout_width ?? 0.3}
                    min={0.01}
                    max={2}
                    step={0.01}
                    onCommit={(layout_width) => changeCue({ layout_width })}
                  />
                  <NumberField
                    label="Kolejność warstwy (Z)"
                    value={cue?.z_index ?? cueIndex}
                    min={-1000}
                    max={1000}
                    step={1}
                    onCommit={(z_index) => changeCue({ z_index })}
                  />
                  <NumberField
                    label="Wejście (s)"
                    value={cue?.start || 0}
                    max={(scene.duration - 1) / rate}
                    step={1 / rate}
                    onCommit={(start) => changeCue({ start })}
                  />
                </fieldset>
              </section>
            )}
            {clip && (
              <section className="shot-layer-properties" key={clip.id}>
                <h2>{clip.title}</h2>
                <fieldset disabled={clipLocked}>
                  <NumberField
                    label="Początek warstwy (s)"
                    value={(clip.start - scene.start) / rate}
                    max={(scene.duration - 1) / rate}
                    onCommit={(start) =>
                      changeClip({
                        start: scene.start + Math.round(start * rate),
                      })
                    }
                  />
                  <NumberField
                    label="Długość warstwy (s)"
                    value={clip.duration / rate}
                    min={1 / rate}
                    max={600}
                    step={1 / rate}
                    onCommit={(duration) =>
                      changeClip({ duration: Math.round(duration * rate) })
                    }
                  />
                  {clipTrack?.kind === "audio" ? (
                    <NumberField
                      label="Głośność"
                      value={clip.volume}
                      max={2}
                      onCommit={(volume) => changeClip({ volume })}
                    />
                  ) : (
                    <>
                      <div className="two-fields">
                        <NumberField
                          label="Przesunięcie X"
                          value={clip.x}
                          min={-2}
                          max={2}
                          step={0.01}
                          onCommit={(x) => changeClip({ x })}
                        />
                        <NumberField
                          label="Przesunięcie Y"
                          value={clip.y}
                          min={-2}
                          max={2}
                          step={0.01}
                          onCommit={(y) => changeClip({ y })}
                        />
                      </div>
                      <NumberField
                        label="Skala"
                        value={clip.scale}
                        min={0.01}
                        max={10}
                        step={0.05}
                        onCommit={(scale) => changeClip({ scale })}
                      />
                      <NumberField
                        label="Krycie"
                        value={clip.opacity}
                        max={1}
                        step={0.05}
                        onCommit={(opacity) => changeClip({ opacity })}
                      />
                    </>
                  )}
                  <Button
                    icon={Trash2}
                    onClick={() =>
                      s.run(() =>
                        s.edit([{ type: "remove_clip", clip_id: clip.id }]),
                      )
                    }
                  >
                    Usuń warstwę
                  </Button>
                </fieldset>
              </section>
            )}
            {selected === "voice" && (
              <section className="shot-layer-properties">
                <h2>Narracja</h2>
                <p className="small muted">
                  {
                    p.assets.find((asset) => asset.id === scene.voice_asset_id)
                      ?.name
                  }
                </p>
                <Button
                  disabled={scene.locked || scene.lock_narration}
                  onClick={() => change({ voice_asset_id: null })}
                >
                  Odłącz nagranie
                </Button>
              </section>
            )}
            <section className="shot-layer-properties">
              <h2>Metryka ujęcia</h2>
              <Field label="Tytuł">
                <CommitText
                  value={scene.title}
                  disabled={scene.locked}
                  onCommit={(title) => change({ title: title || "Ujęcie" })}
                />
              </Field>
              <NumberField
                label="Długość ujęcia (s)"
                value={scene.duration / rate}
                min={1 / rate}
                max={600}
                step={1 / rate}
                disabled={scene.locked || scene.lock_timing}
                onCommit={(duration) =>
                  change({ duration: Math.max(1, Math.round(duration * rate)) })
                }
              />
              {!paper && (
                <Field label="Ruch obrazu">
                  <select
                    disabled={mediaLocked}
                    value={scene.animation}
                    onChange={(e) =>
                      change({
                        animation: e.target.value as Scene["animation"],
                      })
                    }
                  >
                    {animations.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </Field>
              )}
              <Field label="Opis sceny">
                <CommitText
                  multiline
                  disabled={scene.locked}
                  value={scene.description || ""}
                  onCommit={(description) => change({ description })}
                />
              </Field>
              <Field label="Narracja">
                <CommitText
                  multiline
                  value={scene.narration}
                  disabled={scene.locked || scene.lock_narration}
                  onCommit={(narration) => change({ narration })}
                />
              </Field>
              <Field label="Uwagi reżysera">
                <CommitText
                  multiline
                  disabled={scene.locked}
                  value={scene.director_notes || ""}
                  onCommit={(director_notes) => change({ director_notes })}
                />
              </Field>
            </section>
          </aside>
        </div>
      )}
    </>
  );
}

function LayeredShotCanvas({
  project,
  scene,
  frame,
}: {
  project: Project;
  scene: Scene;
  frame: number;
}) {
  const canvas = useRef<HTMLCanvasElement>(null),
    [loaded, setLoaded] = useState<LiveScene | null>(null);
  const [error, setError] = useState("");
  const key = JSON.stringify([
    scene.asset_id,
    scene.asset_ids,
    scene.parameters,
    scene.duration,
    project.sequence,
  ]);
  useEffect(() => {
    let alive = true;
    setError("");
    setLoaded(null);
    if (!scene.asset_id) return;
    const next = new LiveScene({
      width: project.sequence.width,
      height: project.sequence.height,
      fps: fps(project),
      durationFrames: scene.duration,
      template: scene.template || "paper-theatre",
      background: mediaUrl(project.id, scene.asset_id),
      layers: paperLayerIds(scene).map((assetId) =>
        mediaUrl(project.id, assetId),
      ),
      params: { depth: 0.015, caption: "", ...scene.parameters },
    });
    next
      .load()
      .then(() => {
        if (alive) {
          next.warm();
          setLoaded(next);
        }
      })
      .catch((reason) => {
        if (alive) setError(String(reason.message || reason));
      });
    return () => {
      alive = false;
    };
  }, [key, project.id]);
  useEffect(() => {
    const ctx = canvas.current?.getContext("2d");
    if (loaded && ctx) {
      try {
        loaded.draw(ctx, frame);
      } catch (reason) {
        setError(String(reason));
      }
    }
  }, [loaded, frame]);
  return (
    <>
      <canvas
        ref={canvas}
        width={Math.min(960, project.sequence.width)}
        height={Math.round(
          (Math.min(960, project.sequence.width) * project.sequence.height) /
            project.sequence.width,
        )}
        aria-label="Podgląd warstw ujęcia"
      />
      {error && (
        <p className="shot-preview-message" role="alert">
          {error}
        </p>
      )}
      {loaded?.missing ? (
        <p className="shot-preview-message">
          Brakuje obrazów: {loaded.missing}
        </p>
      ) : null}
    </>
  );
}
