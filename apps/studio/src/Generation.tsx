import { useEffect, useRef, useState } from "react";
import {
  Sparkles,
  Search,
  Upload,
  Library,
  Plus,
  ArrowRight,
  Play,
  Volume2,
  Image as ImageIcon,
  Clock3,
  ExternalLink,
  Check,
  ChevronRight,
  LockKeyhole,
  Unlock,
  Mic,
  Clapperboard,
} from "lucide-react";
import { useStudio } from "./context";
import { api, id, mediaUrl, upload, safeUrl } from "./api";
import {
  AssetThumb,
  Button,
  CommitText,
  Empty,
  Field,
  IconButton,
  Modal,
  NumberField,
  SectionHead,
} from "./components";
import type { Asset, Scene, Project, Job, Animation } from "./types";
import { fps, time } from "./timing";

export const animations: { id: Animation; name: string }[] = [
  { id: "zoom-in", name: "Powolne zbliżenie" },
  { id: "zoom-out", name: "Powolne oddalenie" },
  { id: "pan-left", name: "Panorama w lewo" },
  { id: "pan-right", name: "Panorama w prawo" },
  { id: "static", name: "Kadr nieruchomy" },
];
export function makeScene(start = 0): Scene {
  return {
    id: id("scene_"),
    title: "Nowe ujęcie",
    narration: "",
    start,
    duration: 180,
    timing: "estimated",
    mode: "search",
    prompt: "",
    motion_prompt: "",
    search_query: "",
    animation: "zoom-in",
    asset_id: null,
    voice_asset_id: null,
    variants: [],
    fact_ids: [],
    role: "illustration",
    locked: false,
    legacy: {},
  };
}

export default function Generation() {
  const s = useStudio(),
    p = s.project!;
  const [selected, setSelected] = useState(
      s.targetScene || p.scenes[0]?.id || "",
    ),
    [libraryOpen, setLibraryOpen] = useState(false),
    [voiceOpen, setVoiceOpen] = useState(false),
    [url, setUrl] = useState(""),
    [playing, setPlaying] = useState(false),
    [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null),
    videoRef = useRef<HTMLVideoElement>(null);
  const scene = p.scenes.find((x) => x.id === selected) || p.scenes[0];
  const asset = p.assets.find((a) => a.id === scene?.asset_id);
  const rate = fps(p);
  const index = p.scenes.findIndex((x) => x.id === scene?.id);
  const activeJobs = s.jobs.filter(
    (j) => j.project_id === p.id && ["QUEUED", "RUNNING"].includes(j.status),
  );
  const [voiceStates, setVoiceStates] = useState<Record<string, string>>({});
  useEffect(() => {
    s.run(async () =>
      setVoiceStates(
        (
          await api<{ voice: Record<string, string> }>(
            `/projects/${p.id}/production`,
          )
        ).voice,
      ),
    );
  }, [p.revision]);
  useEffect(() => {
    if (s.targetScene && p.scenes.some((x) => x.id === s.targetScene))
      setSelected(s.targetScene);
  }, [s.targetScene, p.scenes]);
  useEffect(() => {
    if (scene?.id) s.setTargetScene(scene.id);
  }, [scene?.id]);
  function change(changes: Partial<Scene>) {
    if (!scene) return;
    const sceneId = scene.id;
    s.run(() =>
      s.patch((current) => ({
        scenes: current.scenes.map((x) =>
          x.id === sceneId ? { ...x, ...changes } : x,
        ),
      })),
    );
  }
  async function importFile(file: File) {
    setUploading(true);
    try {
      const result = await upload<{ asset: Asset; project: Project }>(
        "/projects/" + p.id + "/media",
        file,
      );
      s.accept(result.project);
      if (result.asset.kind === "audio") {
        setVoiceOpen(true);
        s.notify("Nagranie jest w bibliotece. Wybierz je jako lektora.");
      } else if (["image", "video"].includes(result.asset.kind) && scene) {
        await s.patch((current) => ({
          scenes: current.scenes.map((x) =>
            x.id === scene.id
              ? { ...x, asset_id: result.asset.id, mode: "upload" }
              : x,
          ),
        }));
        s.notify("Materiał dodany do ujęcia");
      } else s.notify("Dokument dodano do źródeł");
    } finally {
      setUploading(false);
    }
  }
  async function fetchUrl() {
    const result = await api<{ project: Project; asset: Asset | null }>(
      "/projects/" + p.id + "/fetch",
      { url },
    );
    s.accept(result.project);
    if (result.asset && scene) {
      await s.patch((current) => ({
        scenes: current.scenes.map((x) =>
          x.id === scene.id
            ? { ...x, asset_id: result.asset!.id, mode: "upload" }
            : x,
        ),
      }));
    }
    s.notify("Dodano materiał z adresu");
  }
  async function addScene() {
    const next = makeScene(
      Math.max(0, ...p.scenes.map((x) => x.start + x.duration)),
    );
    await s.patch((current) => ({ scenes: [...current.scenes, next] }));
    setSelected(next.id);
  }
  async function toTimeline() {
    if (!scene) return;
    await s.mutate((current) =>
      api<Project>(
        "/projects/" + current.id + "/scenes/" + scene.id + "/to-timeline",
        { expected_revision: current.revision },
      ),
    );
    s.notify("Ujęcie jest na osi czasu");
    s.setPage("editing");
  }
  async function generate(kind: "image" | "voice") {
    if (!scene) return;
    await api<Job>("/projects/" + p.id + "/generate/" + scene.id + "/" + kind, {
      expected_revision: p.revision,
    });
    s.notify(
      kind === "image"
        ? "Obraz trafił do kolejki generowania"
        : "Lektor trafił do kolejki generowania",
    );
  }
  function find() {
    s.setTargetScene(scene.id);
    s.setSearchInitial(scene.search_query || scene.title);
    s.setPage("sources");
  }
  function speak() {
    if (!("speechSynthesis" in window)) {
      s.notify("Przeglądarka nie udostępnia odsłuchu tekstu", true);
      return;
    }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(scene.narration);
    u.lang = p.language === "pl" ? "pl-PL" : "en-US";
    speechSynthesis.speak(u);
  }
  async function useVoice(a: Asset) {
    await s.mutate((current) =>
      api<Project>(`/projects/${p.id}/scenes/${scene.id}/voice/select`, {
        expected_revision: current.revision,
        asset_id: a.id,
      }),
    );
    setVoiceOpen(false);
    s.notify("Nagranie dodano na ścieżkę lektora");
  }
  if (!scene)
    return (
      <div className="page-content">
        <SectionHead
          title="Przygotuj pierwszy kadr"
          description="Dodaj ujęcie i połącz obraz z narracją."
        />
        <Empty
          icon={Clapperboard}
          title="Tu powstanie Twój film"
          action={
            <Button primary icon={Plus} onClick={() => s.run(addScene)}>
              Dodaj ujęcie
            </Button>
          }
        >
          Możesz też podzielić gotowy tekst w zakładce Scenariusz.
        </Empty>
      </div>
    );
  return (
    <div
      className="generation-page"
      onPaste={(e) => {
        const file = Array.from(e.clipboardData.files).find(
          (f) => f.type.startsWith("image/") || f.type.startsWith("video/"),
        );
        if (file && !scene.locked) {
          e.preventDefault();
          s.run(() => importFile(file));
        }
      }}
    >
      <SectionHead
        eyebrow="PRODUKCJA / 05"
        title="Generowanie filmu"
        description="Przygotuj materiał, ruch i narrację każdego ujęcia."
      >
        <Button icon={Plus} onClick={() => s.run(addScene)}>
          Dodaj ujęcie
        </Button>
        <Button
          primary
          icon={ArrowRight}
          disabled={
            (!asset && (!scene.template || scene.template === "media")) ||
            s.saving
          }
          onClick={() => s.run(toTimeline)}
        >
          Dodaj do montażu
        </Button>
        <Button
          onClick={() => {
            s.setTargetScene(scene.id);
            s.setPage("production");
          }}
        >
          Szablony i głos
        </Button>
      </SectionHead>
      <div className="generation-workspace">
        <section className="prompt-panel surface">
          <div className="panel-heading">
            <h2>Materiał do ujęcia</h2>
            <span className="badge quiet">
              {String(index + 1).padStart(2, "0")}
            </span>
          </div>
          <div
            className="source-modes"
            aria-label="Sposób pozyskania materiału"
          >
            {(
              [
                { mode: "generate", icon: Sparkles, label: "Prompt AI" },
                { mode: "search", icon: Search, label: "Z internetu" },
                { mode: "upload", icon: Upload, label: "Własny plik" },
                { mode: "library", icon: Library, label: "Biblioteka" },
              ] as const
            ).map((x) => (
              <button
                key={x.mode}
                className={scene.mode === x.mode ? "selected" : ""}
                aria-pressed={scene.mode === x.mode}
                disabled={scene.locked || scene.lock_media}
                onClick={() => change({ mode: x.mode })}
              >
                <x.icon size={15} />
                {x.label}
              </button>
            ))}
          </div>
          {scene.mode === "generate" ? (
            <>
              <Field
                label="Prompt obrazu"
                hint="Opisz kadr, światło i styl. Bez wskazówek dla lektora."
              >
                <CommitText
                  multiline
                  rows={6}
                  value={scene.prompt}
                  onCommit={(v) => change({ prompt: v })}
                  disabled={scene.locked || scene.lock_media}
                  placeholder="Jak powinien wyglądać ten kadr?"
                />
              </Field>
              <div className="engine-line">
                <span
                  className={`status-dot ${s.health?.image ? "online" : ""}`}
                />
                <span>Lokalny generator obrazu</span>
                <button
                  className="text-button"
                  onClick={() => s.setSettingsOpen(true)}
                >
                  {s.health?.image ? "Ustawienia" : "Połącz"}
                </button>
              </div>
              <Button
                primary
                icon={Sparkles}
                className="full-width"
                disabled={
                  !scene.prompt ||
                  scene.locked ||
                  activeJobs.some((j) => j.kind === "image")
                }
                onClick={() =>
                  s.health?.image
                    ? s.run(() => generate("image"))
                    : s.setSettingsOpen(true)
                }
              >
                {activeJobs.some((j) => j.kind === "image")
                  ? "Generowanie w toku"
                  : s.health?.image
                    ? "Wygeneruj wariant"
                    : "Połącz generator"}
              </Button>
            </>
          ) : scene.mode === "search" ? (
            <>
              <Field
                label="Czego szukamy?"
                hint="Zdjęcie, archiwalny kadr lub stockowy film."
              >
                <CommitText
                  multiline
                  rows={5}
                  value={scene.search_query}
                  onCommit={(v) => change({ search_query: v })}
                  disabled={scene.locked || scene.lock_media}
                  placeholder="Np. hydrofon zanurzony w oceanie, ujęcie poziome"
                />
              </Field>
              <div className="source-chips">
                <span>Wikimedia Commons</span>
                <span>Stocki</span>
                <span>Własne źródła</span>
              </div>
              <Button
                primary
                icon={Search}
                className="full-width"
                onClick={find}
              >
                Szukaj materiałów
              </Button>
            </>
          ) : scene.mode === "upload" ? (
            <>
              <button
                className="dropzone"
                disabled={scene.locked || uploading}
                onClick={() => fileRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  const file = e.dataTransfer.files[0];
                  if (file) s.run(() => importFile(file));
                }}
              >
                <Upload size={26} />
                <strong>
                  {uploading ? "Wczytywanie…" : "Przeciągnij zdjęcie lub film"}
                </strong>
                <span>
                  lub wybierz plik. Możesz też wkleić obraz przez Ctrl+V.
                </span>
              </button>
              <Field label="Albo adres materiału">
                <input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://…"
                />
              </Field>
              <Button
                icon={ArrowRight}
                className="full-width"
                disabled={!url || scene.locked}
                onClick={() => s.run(fetchUrl)}
              >
                Pobierz z adresu
              </Button>
            </>
          ) : (
            <>
              <div className="compact-library">
                {p.assets
                  .filter((a) => a.kind === "image" || a.kind === "video")
                  .slice(0, 6)
                  .map((a) => (
                    <button
                      key={a.id}
                      className={scene.asset_id === a.id ? "chosen" : ""}
                      onClick={() => change({ asset_id: a.id })}
                      aria-label={"Wybierz " + a.name}
                    >
                      <AssetThumb asset={a} project={p} />
                      {scene.asset_id === a.id && <Check size={14} />}
                    </button>
                  ))}
              </div>
              <Button
                icon={Library}
                className="full-width"
                onClick={() => setLibraryOpen(true)}
              >
                Otwórz bibliotekę
              </Button>
            </>
          )}
          <div className="panel-divider" />
          <Field label="Ruch i animacja">
            <select
              value={scene.animation}
              disabled={scene.locked || scene.lock_media}
              onChange={(e) =>
                change({ animation: e.target.value as Animation })
              }
            >
              {animations.map((a) => (
                <option value={a.id} key={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </Field>
          <Field
            label="Notatka o ruchu"
            hint="Zachowywana w planie. Eksport stosuje wybrany preset i keyframes."
          >
            <CommitText
              multiline
              rows={2}
              value={scene.motion_prompt}
              onCommit={(v) => change({ motion_prompt: v })}
              disabled={scene.locked || scene.lock_media}
              placeholder="Na jakim szczególe skupić uwagę?"
            />
          </Field>
          <details className="advanced">
            <summary>Zaawansowane</summary>
            <Field label="Rola materiału">
              <select
                value={scene.role}
                onChange={(e) =>
                  change({ role: e.target.value as Scene["role"] })
                }
              >
                <option value="illustration">Ilustracja</option>
                <option value="literal">Dosłowne przedstawienie</option>
                <option value="reconstruction">Rekonstrukcja</option>
              </select>
            </Field>
            <p className="muted small">
              Wideo generowane z promptu wymaga osobnego silnika. Ten generator
              tworzy obrazy.
            </p>
          </details>
        </section>
        <div className="generation-center">
          <section className="preview-panel surface">
            <div className="preview-heading">
              <span>
                <span className="live-dot" />
                PODGLĄD UJĘCIA
              </span>
              <span>
                {p.sequence.width} × {p.sequence.height}
              </span>
            </div>
            <div
              className={`shot-preview ${playing ? "animate-" + scene.animation : ""}`}
              onClick={() => {
                setPlaying(!playing);
                if (videoRef.current) {
                  if (playing) videoRef.current.pause();
                  else void videoRef.current.play();
                }
              }}
            >
              {scene.template && scene.template !== "media" ? (
                <img
                  src={`/api/projects/${p.id}/scenes/${scene.id}/poster?revision=${p.revision}&frame=0`}
                  alt={`Podgląd: ${scene.title}`}
                />
              ) : asset?.kind === "image" ? (
                <img src={mediaUrl(p.id, asset.id)} alt={scene.title} />
              ) : asset?.kind === "video" ? (
                <video
                  ref={videoRef}
                  src={mediaUrl(p.id, asset.id)}
                  playsInline
                  muted
                  controls
                />
              ) : (
                <div className="no-preview">
                  <ImageIcon size={38} />
                  <span>Wybierz materiał do tego ujęcia</span>
                </div>
              )}
              <div className="preview-corner">
                <span>
                  {scene.role === "illustration"
                    ? "Ilustracja"
                    : scene.role === "reconstruction"
                      ? "Rekonstrukcja"
                      : "Materiał źródłowy"}
                </span>
              </div>
            </div>
            <div className="player-toolbar">
              <IconButton
                icon={Play}
                label="Odtwórz ruch ujęcia"
                onClick={() => {
                  setPlaying(!playing);
                  if (videoRef.current) {
                    if (playing) videoRef.current.pause();
                    else void videoRef.current.play();
                  }
                }}
              />
              <span className="timecode">
                {time(scene.start, rate, true)}{" "}
                <span>/ {time(scene.start + scene.duration, rate, true)}</span>
              </span>
              <div className="player-spacer" />
              <span className="small muted">16:9</span>
            </div>
          </section>
          <section className="narration-panel surface">
            <div className="panel-heading">
              <h2>
                <Volume2 size={16} />
                Narracja ujęcia
              </h2>
              <Button
                subtle
                icon={Play}
                onClick={speak}
                disabled={!scene.narration}
              >
                Odsłuch tekstu
              </Button>
            </div>
            <CommitText
              multiline
              rows={4}
              value={scene.narration}
              label="Narracja ujęcia"
              onCommit={(v) => change({ narration: v })}
              className="narration-input"
              disabled={scene.locked || scene.lock_narration}
              placeholder="Co w tym momencie opowiada narrator?"
            />
            <div className="narration-footer">
              <span
                className={`badge ${voiceStates[scene.id] === "stale" ? "warning" : "quiet"}`}
              >
                {{
                  current: "Nagranie aktualne",
                  stale: "Nagranie wymaga odświeżenia",
                  missing: "Brak nagrania",
                  empty: "Bez narracji",
                }[voiceStates[scene.id]] || ""}
              </span>
              <span>
                {scene.narration.trim().split(/\s+/).filter(Boolean).length}{" "}
                słów <span>·</span>{" "}
                {scene.timing === "measured"
                  ? "czas zmierzony"
                  : "czas planowany"}
              </span>
              <button
                className="text-button"
                onClick={() => setVoiceOpen(true)}
              >
                <Mic size={14} />
                {scene.voice_asset_id ? "Zmień nagranie" : "Dodaj lektora"}
                <ChevronRight size={14} />
              </button>
            </div>
          </section>
        </div>
        <section className="details-panel surface">
          <div className="panel-heading">
            <h2>Ujęcie {String(index + 1).padStart(2, "0")}</h2>
            <IconButton
              icon={scene.locked ? LockKeyhole : Unlock}
              label={scene.locked ? "Odblokuj ujęcie" : "Zablokuj ujęcie"}
              onClick={() => change({ locked: !scene.locked })}
            />
          </div>
          <Field label="Nazwa">
            <CommitText
              value={scene.title}
              onCommit={(v) => change({ title: v })}
              disabled={scene.locked}
            />
          </Field>
          <div className="two-fields">
            <NumberField
              label="Początek (s)"
              value={scene.start / rate}
              onCommit={(v) => change({ start: Math.round(v * rate) })}
              disabled={scene.locked || scene.lock_timing}
            />
            <NumberField
              label="Długość (s)"
              min={1 / rate}
              value={scene.duration / rate}
              onCommit={(v) => change({ duration: Math.round(v * rate) })}
              disabled={scene.locked || scene.lock_timing}
            />
          </div>
          <div className="timing-note">
            <Clock3 size={14} />
            <span>
              {scene.timing === "estimated"
                ? "Dopasuj czas po przygotowaniu lektora."
                : "Czas dopasowany do nagrania."}
            </span>
          </div>
          <div className="panel-divider" />
          <div className="inspector-label">WYBRANY MATERIAŁ</div>
          {asset ? (
            <>
              <AssetThumb asset={asset} project={p} large />
              <strong className="asset-name">{asset.name}</strong>
              <p className="small muted">
                {asset.width} × {asset.height}{" "}
                {asset.kind === "video" && `· ${asset.duration.toFixed(1)} s`}
              </p>
              <div className="provenance-note">
                <span>{asset.license || "Warunki użycia do uzupełnienia"}</span>
                {asset.author && <span>{asset.author}</span>}
                {safeUrl(asset.source_url) && (
                  <a
                    href={safeUrl(asset.source_url)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Zobacz źródło
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>
              <Button
                subtle
                icon={Library}
                onClick={() => setLibraryOpen(true)}
              >
                Zmień materiał
              </Button>
            </>
          ) : (
            <div className="small-empty">Obraz czeka na Ciebie.</div>
          )}
          {scene.variants.length > 0 && (
            <>
              <div className="panel-divider" />
              <div className="inspector-label">WARIANTY</div>
              <div className="variants">
                {scene.variants.map((aid) => {
                  const a = p.assets.find((a) => a.id === aid);
                  return a ? (
                    <button
                      key={aid}
                      onClick={() =>
                        a.kind === "audio"
                          ? s.run(() => useVoice(a))
                          : change({ asset_id: a.id })
                      }
                      aria-label={"Wybierz wariant " + a.name}
                    >
                      <AssetThumb asset={a} project={p} />
                    </button>
                  ) : null;
                })}
              </div>
            </>
          )}
        </section>
      </div>
      <section className="storyboard">
        <div className="storyboard-heading">
          <h2>Twoja sekwencja</h2>
          <span>{p.scenes.length} ujęć</span>
          <div className="player-spacer" />
          <Button
            subtle
            icon={Clapperboard}
            onClick={() => s.setPage("editing")}
          >
            Przejdź do montażu
            <ArrowRight size={14} />
          </Button>
        </div>
        <div className="shot-cards">
          {p.scenes.map((shot, i) => (
            <button
              key={shot.id}
              className={`shot-card ${shot.id === scene.id ? "active" : ""}`}
              onClick={() => {
                setSelected(shot.id);
                setPlaying(false);
              }}
            >
              <div className="shot-card-top">
                <AssetThumb
                  asset={p.assets.find((a) => a.id === shot.asset_id)}
                  project={p}
                />
                <span className="shot-number">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="shot-duration">
                  {(shot.duration / rate).toFixed(1)} s
                </span>
              </div>
              <div className="shot-card-body">
                <strong>{shot.title}</strong>
                <span>
                  {time(shot.start, rate)} —{" "}
                  {time(shot.start + shot.duration, rate)}
                </span>
              </div>
            </button>
          ))}
          <button className="add-shot-card" onClick={() => s.run(addScene)}>
            <Plus size={24} />
            <span>Dodaj ujęcie</span>
          </button>
        </div>
      </section>
      <input
        ref={fileRef}
        type="file"
        accept="image/*,video/*,audio/*,.pdf,.epub"
        className="visually-hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) s.run(() => importFile(file));
          e.target.value = "";
        }}
      />
      <Modal
        open={libraryOpen}
        onClose={() => setLibraryOpen(false)}
        title="Wybierz materiał"
        description="Pliki w Twoim projekcie"
        wide
      >
        <div className="asset-picker">
          {p.assets
            .filter((a) => a.kind === "image" || a.kind === "video")
            .map((a) => (
              <button
                key={a.id}
                onClick={() => {
                  change({ asset_id: a.id, mode: "library" });
                  setLibraryOpen(false);
                }}
              >
                <AssetThumb asset={a} project={p} />
                <strong>{a.name}</strong>
              </button>
            ))}
        </div>
        <Button icon={Upload} onClick={() => fileRef.current?.click()}>
          Dodaj plik
        </Button>
      </Modal>
      <Modal
        open={voiceOpen}
        onClose={() => setVoiceOpen(false)}
        title="Lektor ujęcia"
        description="Nagranie do eksportu lub odsłuch tekstu w przeglądarce"
      >
        <div className="voice-options">
          {p.assets
            .filter((a) => a.kind === "audio")
            .map((a) => (
              <div className="voice-item" key={a.id}>
                <div>
                  <strong>{a.name}</strong>
                  <span>{a.duration.toFixed(1)} s</span>
                </div>
                <audio src={mediaUrl(p.id, a.id)} controls />
                <Button icon={Check} onClick={() => s.run(() => useVoice(a))}>
                  Użyj
                </Button>
              </div>
            ))}
        </div>
        <div className="button-row">
          <Button icon={Upload} onClick={() => fileRef.current?.click()}>
            Wgraj nagranie
          </Button>
          <Button
            primary
            icon={Mic}
            onClick={() =>
              s.health?.voice
                ? s.run(() => generate("voice"))
                : (setVoiceOpen(false), s.setSettingsOpen(true))
            }
          >
            {s.health?.voice ? "Wygeneruj lektora" : "Ustawienia lektora"}
          </Button>
        </div>
        <p className="small muted">
          Generowanie wymaga lokalnego środowiska Chatterbox i próbki głosu.
          Odsłuch tekstu nie tworzy pliku do filmu.
        </p>
      </Modal>
    </div>
  );
}
