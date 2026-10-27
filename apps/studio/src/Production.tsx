import { useEffect, useId, useState } from "react";
import {
  Plus,
  Copy,
  Trash2,
  ArrowUp,
  ArrowDown,
  Play,
  Check,
  Mic,
  Upload,
  RefreshCw,
} from "lucide-react";
import { useStudio } from "./context";
import { api, id, mediaUrl, upload } from "./api";
import {
  Button,
  CommitText,
  Field,
  NumberField,
  SectionHead,
  AssetThumb,
} from "./components";
import type { Beat, Project, Scene, Template, Word } from "./types";
import CaptionEditor from "./Captions";

export function JSONField({
  label,
  value,
  onSave,
}: {
  label: string;
  value: unknown;
  onSave: (v: unknown) => void;
}) {
  const controlId = useId();
  const [text, setText] = useState(JSON.stringify(value, null, 2)),
    [error, setError] = useState("");
  useEffect(
    () => setText(JSON.stringify(value, null, 2)),
    [JSON.stringify(value)],
  );
  return (
    <div className="field">
      <label className="field-label" htmlFor={controlId}>
        {label}
      </label>
      <textarea
        id={controlId}
        rows={4}
        value={text}
        spellCheck={false}
        onChange={(e) => {
          setText(e.target.value);
          setError("");
        }}
      />
      {error && <span role="alert">{error}</span>}
      <Button
        subtle
        onClick={() => {
          try {
            onSave(JSON.parse(text));
            setError("");
          } catch {
            setError("Sprawdź zapis JSON");
          }
        }}
      >
        Zapisz dane
      </Button>
    </div>
  );
}

export default function Production() {
  const [tab, setTab] = useState("shots");
  return (
    <div className="page-content production-page">
      <SectionHead
        eyebrow="WARSZTAT FILMOWY"
        title="Narzędzia produkcji"
        description="Szablony ujęć, głos, fragmenty historii i warianty montażu."
      />
      <div className="filter-pills">
        {[
          ["shots", "Ujęcia"],
          ["voice", "Lektor"],
          ["beats", "Fragmenty"],
          ["versions", "Wersje A/B"],
          ["channel", "Kanał i limity"],
          ["system", "Pliki i diagnostyka"],
        ].map(([key, label]) => (
          <button
            key={key}
            className={tab === key ? "active" : ""}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {tab === "shots" ? (
        <ShotTools />
      ) : tab === "voice" ? (
        <VoiceTools />
      ) : tab === "beats" ? (
        <BeatTools />
      ) : tab === "versions" ? (
        <VersionTools />
      ) : tab === "channel" ? (
        <ChannelTools />
      ) : (
        <SystemTools />
      )}
    </div>
  );
}

function SceneSelect({
  scene,
  onChange,
}: {
  scene: Scene | undefined;
  onChange: (id: string) => void;
}) {
  const p = useStudio().project!;
  return (
    <Field label="Wybrane ujęcie">
      <select
        value={scene?.id || ""}
        onChange={(e) => onChange(e.target.value)}
      >
        {p.scenes.map((s, i) => (
          <option key={s.id} value={s.id}>
            {String(i + 1).padStart(2, "0")} · {s.title}
          </option>
        ))}
      </select>
    </Field>
  );
}

export function ShotTools() {
  const s = useStudio(),
    p = s.project!;
  const [templates, setTemplates] = useState<Template[]>([]),
    [suggestions, setSuggestions] = useState<
      { asset_id: string; reason: string; uses: string[] }[]
    >([]);
  useEffect(() => {
    s.run(async () => setTemplates(await api<Template[]>("/templates")));
  }, []);
  const scene = p.scenes.find((x) => x.id === s.targetScene) || p.scenes[0],
    index = p.scenes.findIndex((x) => x.id === scene?.id);
  const template = templates.find((t) => t.id === (scene?.template || "media"));
  function change(changes: Partial<Scene>) {
    if (scene)
      s.run(() =>
        s.patch((c) => ({
          scenes: c.scenes.map((x) =>
            x.id === scene.id ? { ...x, ...changes } : x,
          ),
        })),
      );
  }
  async function operation(operation: string, target?: number) {
    await s.mutate((c) =>
      api<Project>(`/projects/${p.id}/scenes/${scene.id}/operation`, {
        expected_revision: c.revision,
        operation,
        target,
      }),
    );
  }
  if (!scene) return <p>Dodaj pierwsze ujęcie w Generowaniu.</p>;
  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <SceneSelect scene={scene} onChange={s.setTargetScene} />
        <div className="button-row">
          <Button
            icon={Copy}
            onClick={() => s.run(() => operation("duplicate"))}
          >
            Duplikuj
          </Button>
          <Button
            icon={ArrowUp}
            disabled={!index}
            onClick={() => s.run(() => operation("move", index - 1))}
          >
            W górę
          </Button>
          <Button
            icon={ArrowDown}
            disabled={index === p.scenes.length - 1}
            onClick={() => s.run(() => operation("move", index + 1))}
          >
            W dół
          </Button>
          <Button
            icon={Trash2}
            onClick={() => s.run(() => operation("remove"))}
          >
            Usuń ujęcie
          </Button>
        </div>
        <Field label="Nazwa">
          <CommitText
            value={scene.title}
            onCommit={(title) => change({ title })}
          />
        </Field>
        <Field label="Fragment historii">
          <select
            value={scene.beat_id || ""}
            onChange={(e) => change({ beat_id: e.target.value || null })}
          >
            <option value="">Bez przypisania</option>
            {p.beats.map((b) => (
              <option key={b.id} value={b.id}>
                {b.chapter} · {b.title}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Typ ujęcia">
          <select
            value={scene.template || "media"}
            onChange={(e) =>
              change({
                template: e.target.value,
                parameters: Object.fromEntries(
                  (
                    templates.find((t) => t.id === e.target.value)?.fields || []
                  ).map((f) => [f.key, f.default]),
                ),
              })
            }
          >
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </Field>
        {template?.note && <p className="small muted">{template.note}</p>}
        {template?.fields.map((f) =>
          f.type === "number" ? (
            <NumberField
              key={scene.id + f.key}
              label={f.label}
              value={Number(scene.parameters?.[f.key] ?? f.default)}
              min={f.min ?? -100000}
              max={f.max ?? 100000}
              onCommit={(v) =>
                change({ parameters: { ...scene.parameters, [f.key]: v } })
              }
            />
          ) : f.type === "json" ? (
            <JSONField
              key={scene.id + f.key}
              label={f.label}
              value={scene.parameters?.[f.key] ?? f.default}
              onSave={(v) =>
                change({ parameters: { ...scene.parameters, [f.key]: v } })
              }
            />
          ) : (
            <Field key={scene.id + f.key} label={f.label}>
              <CommitText
                value={String(scene.parameters?.[f.key] ?? f.default)}
                onCommit={(v) =>
                  change({ parameters: { ...scene.parameters, [f.key]: v } })
                }
              />
            </Field>
          ),
        )}
        <Button
          primary
          onClick={() =>
            s.run(() =>
              s.mutate((c) =>
                api<Project>(
                  `/projects/${p.id}/scenes/${scene.id}/to-timeline`,
                  { expected_revision: c.revision },
                ),
              ),
            )
          }
        >
          Zastosuj w montażu
        </Button>
        <p className="small muted">
          Zastosowanie zastępuje wybrane medium i parametry powiązanych klipów.
          Ręczne ustawienia ruchu pozostają na osi.
        </p>
        <Button
          onClick={() =>
            s.run(() =>
              s.mutate((c) =>
                api<Project>(
                  `/projects/${p.id}/scenes/${scene.id}/review-evidence`,
                  { expected_revision: c.revision },
                ),
              ),
            )
          }
        >
          Potwierdzam narrację względem aktualnych dowodów
        </Button>
      </section>
      <section className="surface tool-panel">
        <h2>Warstwy i dowody</h2>
        <Field label="Główny materiał">
          <select
            value={scene.asset_id || ""}
            onChange={(e) => change({ asset_id: e.target.value || null })}
          >
            <option value="">Bez materiału</option>
            {p.assets
              .filter((a) => a.kind !== "document")
              .map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} · {a.id.slice(-6)}
                </option>
              ))}
          </select>
        </Field>
        <p className="small muted">
          Warstwy są komponowane w kolejności wybrania. Parallax wymaga tła i
          wyciętej warstwy z przezroczystością.
        </p>
        <div className="tool-options">
          {p.assets
            .filter((a) => a.kind !== "document")
            .map((a) => (
              <label key={a.id}>
                <input
                  type="checkbox"
                  checked={(scene.asset_ids || []).includes(a.id)}
                  onChange={(e) =>
                    change({
                      asset_ids: e.target.checked
                        ? [...(scene.asset_ids || []), a.id]
                        : (scene.asset_ids || []).filter((x) => x !== a.id),
                    })
                  }
                />
                {a.name} <small>{a.id.slice(-6)}</small>
              </label>
            ))}
        </div>
        <h3>Fakty wykorzystane w ujęciu</h3>
        <div className="tool-options">
          {p.facts.map((f) => (
            <label key={f.id}>
              <input
                type="checkbox"
                checked={scene.fact_ids.includes(f.id)}
                onChange={(e) =>
                  change({
                    fact_ids: e.target.checked
                      ? [...scene.fact_ids, f.id]
                      : scene.fact_ids.filter((x) => x !== f.id),
                  })
                }
              />
              <span>
                {f.claim}
                <small>
                  {f.status} · {f.source} {f.page}
                </small>
              </span>
            </label>
          ))}
        </div>
        <h3>Blokady</h3>
        <div className="tool-options">
          {[
            ["locked", "Całe ujęcie"],
            ["lock_narration", "Narracja"],
            ["lock_timing", "Czas"],
            ["lock_media", "Materiały"],
          ].map(([key, label]) => (
            <label key={key}>
              <input
                type="checkbox"
                checked={Boolean(scene[key as keyof Scene])}
                onChange={(e) => change({ [key]: e.target.checked })}
              />
              {label}
            </label>
          ))}
        </div>
        <h3>Warianty obrazu</h3>
        <div className="two-fields">
          {[
            ["seed", "Ziarno", 42, 0, 2147483647],
            ["steps", "Kroki", 25, 1, 75],
            ["width", "Szerokość", 768, 256, 1024],
            ["height", "Wysokość", 448, 256, 1024],
          ].map(([key, label, fallback, min, max]) => (
            <NumberField
              key={String(key)}
              label={String(label)}
              value={Number(scene.generation?.[String(key)] ?? fallback)}
              min={Number(min)}
              max={Number(max)}
              step={["width", "height"].includes(String(key)) ? 8 : 1}
              onCommit={(v) =>
                change({
                  generation: { ...scene.generation, [String(key)]: v },
                })
              }
            />
          ))}
        </div>
        <Button
          icon={RefreshCw}
          onClick={() =>
            s.run(async () => {
              const r = await api<{ assets: typeof suggestions }>(
                `/projects/${p.id}/scenes/${scene.id}/suggestions`,
                {},
              );
              setSuggestions(r.assets);
            })
          }
        >
          Zaproponuj z biblioteki
        </Button>
        {suggestions.map((a) => (
          <div key={a.asset_id} className="suggestion">
            <AssetThumb
              project={p}
              asset={p.assets.find((x) => x.id === a.asset_id)}
            />
            <p>
              {a.reason}
              <small>Użycia: {a.uses.join(", ") || "brak"}</small>
            </p>
            <Button onClick={() => change({ asset_id: a.asset_id })}>
              Wybierz
            </Button>
          </div>
        ))}
      </section>
    </div>
  );
}

export function VoiceTools() {
  const s = useStudio(),
    p = s.project!;
  const [profiles, setProfiles] = useState<Record<string, unknown>[]>([]),
    [name, setName] = useState("Mój głos"),
    [model, setModel] = useState("small"),
    [wave, setWave] = useState<number[]>([]);
  const scene = p.scenes.find((x) => x.id === s.targetScene) || p.scenes[0];
  useEffect(() => {
    s.run(async () =>
      setProfiles(await api<Record<string, unknown>[]>("/voices")),
    );
  }, []);
  useEffect(() => {
    setWave([]);
    if (scene?.voice_asset_id)
      s.run(async () => {
        const r = await api<{ peaks: number[] }>(
          `/projects/${p.id}/assets/${scene.voice_asset_id}/waveform`,
        );
        setWave(r.peaks);
      });
  }, [scene?.voice_asset_id]);
  async function action(path: string, body: Record<string, unknown> = {}) {
    const result = await api<Project | { id: string }>(
      `/projects/${p.id}/scenes/${scene.id}/${path}`,
      { expected_revision: p.revision, ...body },
    );
    if ("schema_version" in result) s.accept(result);
    else s.notify("Zadanie dodano do kolejki");
  }
  if (!scene) return <p>Najpierw dodaj ujęcie z narracją.</p>;
  const asset = p.assets.find((a) => a.id === scene.voice_asset_id);
  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>Profile prywatnego głosu</h2>
        <Field label="Nazwa próbki">
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </Field>
        <label className="button">
          <Upload size={16} />
          Przygotuj próbkę 3–120 s
          <input
            type="file"
            accept="audio/*"
            className="visually-hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file)
                s.run(async () => {
                  await upload(
                    "/voices?name=" + encodeURIComponent(name),
                    file,
                  );
                  setProfiles(await api<Record<string, unknown>[]>("/voices"));
                  s.notify("Przygotowano prywatną próbkę głosu");
                });
              e.target.value = "";
            }}
          />
        </label>
        <p className="small muted">
          Studio przygotuje mono 24 kHz i wyrówna głośność. Próbki pozostają w
          prywatnym katalogu i nie trafiają do pakietu projektu.
        </p>
        <Field label="Profil projektu">
          <select
            value={String(p.voice_profile.id || "")}
            onChange={(e) =>
              s.run(() =>
                s.mutate((c) =>
                  api<Project>(`/projects/${p.id}/voices/select`, {
                    expected_revision: c.revision,
                    voice_id: e.target.value,
                  }),
                ),
              )
            }
          >
            <option value="">Domyślna próbka lokalna</option>
            {profiles.map((v) => (
              <option key={String(v.id)} value={String(v.id)}>
                {String(v.name)}
              </option>
            ))}
          </select>
        </Field>
        {Boolean(p.voice_profile.id) && (
          <audio controls src={`/api/voices/${p.voice_profile.id}/sample`} />
        )}
        <Field label="Urządzenie lektora">
          <select
            value={String(p.voice_profile.device || "auto")}
            onChange={(e) =>
              s.run(() =>
                s.patch((c) => ({
                  voice_profile: { ...c.voice_profile, device: e.target.value },
                })),
              )
            }
          >
            <option value="auto">Automatyczne · CPU przy małej pamięci</option>
            <option value="cpu">CPU</option>
            <option value="mps">Apple MPS</option>
            <option value="cuda">NVIDIA CUDA</option>
          </select>
        </Field>
        <div className="two-fields">
          {[
            ["exaggeration", "Ekspresja", 0.5, 0, 2],
            ["cfg_weight", "Zgodność głosu", 0.4, 0, 1],
            ["temperature", "Zmienność", 0.7, 0.05, 2],
            ["pause", "Pauza zdań (s)", 0.25, 0, 2],
            ["seed", "Ziarno", 42, 0, 2147483647],
          ].map(([key, label, fallback, min, max]) => (
            <NumberField
              key={String(key)}
              label={String(label)}
              value={Number(p.voice_profile[String(key)] ?? fallback)}
              min={Number(min)}
              max={Number(max)}
              step={key === "seed" ? 1 : 0.05}
              onCommit={(value) =>
                s.run(() =>
                  s.patch((c) => ({
                    voice_profile: { ...c.voice_profile, [String(key)]: value },
                  })),
                )
              }
            />
          ))}
        </div>
        <JSONField
          label="Słownik wymowy — zapis: wymowa"
          value={p.pronunciation}
          onSave={(v) =>
            s.run(() => s.patch({ pronunciation: v as Record<string, string> }))
          }
        />
        {Boolean(p.voice_profile.id) && (
          <Button
            onClick={() =>
              s.run(async () => {
                const fields = [
                    "name",
                    "model",
                    "device",
                    "exaggeration",
                    "cfg_weight",
                    "temperature",
                    "pause",
                    "seed",
                  ],
                  changes = Object.fromEntries(
                    fields
                      .filter((k) => k in p.voice_profile)
                      .map((k) => [k, p.voice_profile[k]]),
                  );
                await api(`/voices/${p.voice_profile.id}`, changes, "PATCH");
                setProfiles(await api<Record<string, unknown>[]>("/voices"));
                s.notify("Zapisano parametry w prywatnym profilu");
              })
            }
          >
            Zapisz parametry w profilu głosu
          </Button>
        )}
        <p className="small muted">
          Zmiana słownika lub profilu unieważnia odpowiadające mu nagrania.
          Warianty zachowujesz do porównania.
        </p>
      </section>
      <section className="surface tool-panel">
        <SceneSelect scene={scene} onChange={s.setTargetScene} />
        <h2>Zdania i napisy</h2>
        {!scene.sentences?.length && (
          <Button
            onClick={() => s.run(() => s.patch((c) => ({ scenes: c.scenes })))}
          >
            Przygotuj podział narracji na zdania
          </Button>
        )}
        {asset ? (
          <>
            <audio controls src={mediaUrl(p.id, asset.id)} />
            <svg
              viewBox="0 0 480 70"
              role="img"
              aria-label="Przebieg wybranego nagrania"
              className="audio-wave"
            >
              {wave.map((v, i) => (
                <line
                  key={i}
                  x1={(i * 480) / wave.length}
                  x2={(i * 480) / wave.length}
                  y1={35 - v * 32}
                  y2={35 + v * 32}
                />
              ))}
            </svg>
          </>
        ) : (
          <p className="small muted">Wybierz nagranie w Generowaniu.</p>
        )}
        <div className="sentence-list">
          {(scene.sentences || []).map((sentence, i) => (
            <article key={sentence.id}>
              <strong>
                {i + 1}. {sentence.text}
              </strong>
              <small>
                {sentence.spoken_text} · {sentence.duration.toFixed(2)} s
              </small>
              <div className="button-row">
                <Button
                  icon={Mic}
                  onClick={() =>
                    s.run(async () => {
                      await api(
                        `/projects/${p.id}/generate/${scene.id}/voice`,
                        {
                          sentence_id: sentence.id,
                          expected_revision: p.revision,
                        },
                      );
                      s.notify("Dogrywka zdania w kolejce");
                    })
                  }
                >
                  Dograj
                </Button>
                <select
                  aria-label={`Wariant zdania ${i + 1}`}
                  value={sentence.asset_id || ""}
                  onChange={(e) =>
                    s.run(() =>
                      action(`sentences/${sentence.id}/select`, {
                        asset_id: e.target.value,
                      }),
                    )
                  }
                >
                  <option value="">Wybierz wariant</option>
                  {sentence.variants.map((aid, j) => (
                    <option key={aid} value={aid}>
                      Wariant {j + 1} ·{" "}
                      {p.assets.find((a) => a.id === aid)?.duration.toFixed(2)}{" "}
                      s
                    </option>
                  ))}
                </select>
              </div>
              {sentence.asset_id && (
                <audio controls src={mediaUrl(p.id, sentence.asset_id)} />
              )}
            </article>
          ))}
        </div>
        <Button
          primary
          icon={Check}
          disabled={!scene.sentences?.length}
          onClick={() => s.run(() => action("assemble"))}
        >
          Złóż wybrane zdania w nowy wariant
        </Button>
        <p className="small muted">
          Złożony wariant wybierz w Generowaniu, aby zastąpić nagranie na osi.
        </p>
        <div className="panel-divider" />
        <Field label="Dokładność rozpoznawania">
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            {["tiny", "base", "small", "medium"].map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </Field>
        <div className="button-row">
          <Button
            icon={Play}
            disabled={!asset}
            onClick={() => s.run(() => action("alignment", { model }))}
          >
            Rozpoznaj czasy słów
          </Button>
          <Button
            disabled={!asset}
            onClick={() =>
              s.run(() => action("alignment", { method: "sentences" }))
            }
          >
            Użyj zmierzonych zdań
          </Button>
        </div>
        <p className="small muted">
          Rozpoznany tekst i czas sprawdź przed eksportem. Poniżej możesz
          poprawić słowa lub podzielić zmierzone zdania.
        </p>
        <CaptionEditor
          key={scene.id}
          words={scene.words || []}
          duration={asset?.duration || 0}
          onSave={(words) => s.run(() => action("alignment", { words }))}
        />
        <details>
          <summary>Dane napisów — zaawansowane</summary>
          <JSONField
            label="Tekst i znaczniki (sekundy nagrania)"
            value={scene.words || []}
            onSave={(v) =>
              s.run(() => action("alignment", { words: v as Word[] }))
            }
          />
        </details>
        <div className="button-row">
          {["srt", "vtt"].map((f) => (
            <a
              className="button"
              key={f}
              href={`/api/projects/${p.id}/export/${f}`}
              download
            >
              {f.toUpperCase()}
            </a>
          ))}
          <Button
            onClick={() =>
              s.run(() =>
                s.mutate((c) =>
                  api<Project>(`/projects/${p.id}/captions-to-timeline`, {
                    expected_revision: c.revision,
                  }),
                ),
              )
            }
          >
            Zastosuj napisy na osi
          </Button>
        </div>
      </section>
    </div>
  );
}

export function BeatTools() {
  const s = useStudio(),
    p = s.project!;
  const [selected, setSelected] = useState(p.beats[0]?.id || ""),
    [instruction, setInstruction] = useState(""),
    [prompt, setPrompt] = useState(""),
    [response, setResponse] = useState(""),
    [base, setBase] = useState(-1),
    [purpose, setPurpose] = useState("writer");
  const beat = p.beats.find((b) => b.id === selected) || p.beats[0],
    index = p.beats.findIndex((b) => b.id === beat?.id);
  function change(values: Partial<Beat>) {
    s.run(() =>
      s.patch((c) => ({
        beats: c.beats.map((b) => (b.id === beat.id ? { ...b, ...values } : b)),
      })),
    );
  }
  async function ai(action: string) {
    const r = await api<
      Project | { prompt?: string; response?: string; base_revision: number }
    >(
      purpose === "planner"
        ? `/projects/${p.id}/planner/${action}`
        : `/projects/${p.id}/beats/${beat.id}/writer/${action}`,
      {
        beat_id: beat.id,
        instruction,
        response,
        base_revision: base,
      },
    );
    if ("schema_version" in r) s.accept(r);
    else {
      setBase(r.base_revision);
      if (r.prompt) setPrompt(r.prompt);
      if (r.response) setResponse(r.response);
    }
  }
  return (
    <>
      <section className="surface tool-panel">
        <div className="inline-heading">
          <h2>Krzywa energii</h2>
          <div className="player-spacer" />
          <Button
            icon={Plus}
            onClick={() =>
              s.run(async () => {
                const b: Beat = {
                  id: id("beat_"),
                  title: "Nowy fragment",
                  chapter: "Historia",
                  narration: "",
                  goal: "",
                  turn: "",
                  energy: 5,
                  dynamics: "STORY",
                  typology: "EVIDENCE",
                  chaos: "NONE",
                  fact_ids: [],
                };
                await s.patch((c) => ({ beats: [...c.beats, b] }));
                setSelected(b.id);
              })
            }
          >
            Dodaj fragment
          </Button>
        </div>
        <svg
          className="energy-curve"
          viewBox="0 0 800 130"
          role="img"
          aria-label="Energia kolejnych fragmentów od 1 do 10"
        >
          {[1, 5, 10].map((v) => (
            <g key={v}>
              <line x1="25" x2="790" y1={120 - v * 10} y2={120 - v * 10} />
              <text x="0" y={125 - v * 10}>
                {v}
              </text>
            </g>
          ))}
          <polyline
            points={p.beats
              .map(
                (b, i) =>
                  `${35 + (i * 740) / Math.max(1, p.beats.length - 1)},${120 - b.energy * 10}`,
              )
              .join(" ")}
          />
          {p.beats.map((b, i) => (
            <circle
              key={b.id}
              cx={35 + (i * 740) / Math.max(1, p.beats.length - 1)}
              cy={120 - b.energy * 10}
              r={b.id === beat?.id ? 6 : 4}
            />
          ))}
        </svg>
        <p className="small muted">
          Energia 1–10 opisuje planowane tempo i napięcie, nie pomiar głośności.
          Zmiana rytmu powinna wynikać ze zwrotu, dowodu lub pytania fragmentu.
        </p>
      </section>
      {beat && (
        <div className="production-grid">
          <section className="surface tool-panel">
            <Field label="Fragment">
              <select
                value={beat.id}
                onChange={(e) => setSelected(e.target.value)}
              >
                {p.beats.map((b, i) => (
                  <option key={b.id} value={b.id}>
                    {i + 1}. {b.chapter} · {b.title}
                  </option>
                ))}
              </select>
            </Field>
            {(
              [
                ["title", "Nazwa"],
                ["chapter", "Rozdział"],
                ["goal", "Cel"],
                ["turn", "Zwrot"],
                ["dynamics", "Dynamika"],
                ["typology", "Typologia"],
                ["chaos", "Zakłócenie"],
              ] as const
            ).map(([key, label]) => (
              <Field key={key} label={label}>
                <CommitText
                  value={beat[key]}
                  onCommit={(v) => change({ [key]: v })}
                />
              </Field>
            ))}
            <NumberField
              label="Energia"
              value={beat.energy}
              min={1}
              max={10}
              step={1}
              onCommit={(energy) => change({ energy })}
            />
            <Field label="Narracja fragmentu">
              <CommitText
                multiline
                rows={8}
                value={beat.narration}
                onCommit={(narration) => change({ narration })}
              />
            </Field>
            <p className="small muted">
              Narracja fragmentu jest planem redakcyjnym. Tekst przypisany do
              ujęć pozostaje nagrywanym tekstem; rozdziel go świadomie przed
              generowaniem głosu.
            </p>
            <div className="button-row">
              {[-1, 1].map((delta) => (
                <Button
                  key={delta}
                  disabled={
                    index + delta < 0 || index + delta >= p.beats.length
                  }
                  onClick={() =>
                    s.run(() =>
                      s.patch((c) => {
                        const beats = [...c.beats];
                        const old = beats.splice(index, 1)[0];
                        beats.splice(index + delta, 0, old);
                        return { beats };
                      }),
                    )
                  }
                >
                  {delta < 0 ? "W górę" : "W dół"}
                </Button>
              ))}
            </div>
          </section>
          <section className="surface tool-panel">
            <h2>Dowody i redakcja AI</h2>
            <div className="tool-options">
              {p.facts.map((f) => (
                <label key={f.id}>
                  <input
                    type="checkbox"
                    checked={beat.fact_ids.includes(f.id)}
                    onChange={(e) =>
                      change({
                        fact_ids: e.target.checked
                          ? [...beat.fact_ids, f.id]
                          : beat.fact_ids.filter((x) => x !== f.id),
                      })
                    }
                  />
                  {f.claim} · {f.status}
                </label>
              ))}
            </div>
            <Field label="Narzędzie AI">
              <select
                value={purpose}
                onChange={(e) => {
                  setPurpose(e.target.value);
                  setBase(-1);
                  setPrompt("");
                  setResponse("");
                }}
              >
                <option value="writer">Redakcja fragmentu</option>
                <option value="planner">Planer przebitek z narracji</option>
              </select>
            </Field>
            <Field label="Cel poprawki">
              <textarea
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                rows={3}
              />
            </Field>
            <div className="button-row">
              <Button onClick={() => s.run(() => ai("prompt"))}>
                Przygotuj prompt
              </Button>
              <Button onClick={() => s.run(() => ai("generate"))}>
                Poproś AI o poprawkę
              </Button>
            </div>
            {prompt && (
              <Field label="Prompt do skopiowania">
                <textarea readOnly rows={6} value={prompt} />
              </Field>
            )}
            <Field label="Propozycja JSON">
              <textarea
                rows={8}
                value={response}
                onChange={(e) => setResponse(e.target.value)}
              />
            </Field>
            <p className="small muted">
              Rewizja wejścia {base < 0 ? "—" : base}; bieżąca {p.revision}.
              Sprawdź tekst i źródła przed przyjęciem.
            </p>
            <Button
              primary
              disabled={!response || base !== p.revision}
              onClick={() => s.run(() => ai("import"))}
            >
              {purpose === "planner"
                ? "Dodaj zaplanowane ujęcia"
                : "Przyjmij poprawkę fragmentu"}
            </Button>
          </section>
        </div>
      )}
    </>
  );
}

function VersionTools() {
  const s = useStudio(),
    p = s.project!;
  const [versions, setVersions] = useState<
      { id: string; name: string; revision: number; clips: number }[]
    >([]),
    [name, setName] = useState("Wariant A"),
    [compare, setCompare] = useState<Project | null>(null);
  const refresh = async () =>
    setVersions(await api<typeof versions>(`/projects/${p.id}/versions`));
  useEffect(() => {
    s.run(refresh);
  }, [p.id]);
  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>Zapisane wersje</h2>
        <Field label="Nazwa wariantu">
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </Field>
        <Button
          primary
          icon={Plus}
          onClick={() =>
            s.run(async () => {
              await api(`/projects/${p.id}/versions`, { name });
              await refresh();
            })
          }
        >
          Zapisz obecną wersję
        </Button>
        {versions.map((v) => (
          <article className="version-row" key={v.id}>
            <strong>{v.name}</strong>
            <small>
              Rewizja {v.revision} · {v.clips} klipów
            </small>
            <div className="button-row">
              <Button
                onClick={() =>
                  s.run(async () =>
                    setCompare(
                      (
                        await api<{ project: Project }>(
                          `/projects/${p.id}/versions/${v.id}`,
                        )
                      ).project,
                    ),
                  )
                }
              >
                Porównaj
              </Button>
              <Button
                onClick={() =>
                  s.run(() =>
                    s.mutate((c) =>
                      api<Project>(
                        `/projects/${p.id}/versions/${v.id}/restore`,
                        { expected_revision: c.revision },
                      ),
                    ),
                  )
                }
              >
                Przywróć i edytuj
              </Button>
              <Button
                icon={Play}
                onClick={() =>
                  s.run(async () => {
                    await api(`/projects/${p.id}/versions/${v.id}/preview`, {});
                    s.notify("Podgląd wariantu w kolejce");
                  })
                }
              >
                Podgląd
              </Button>
            </div>
          </article>
        ))}
      </section>
      <section className="surface tool-panel">
        <h2>Porównanie z bieżącą rewizją {p.revision}</h2>
        {compare ? (
          <>
            <p>
              Wybrana wersja: {compare.title} · r{compare.revision}
            </p>
            {[
              "title",
              "language",
              "story",
              "facts",
              "beats",
              "scenes",
              "sequence",
            ].map((key) => {
              const old = compare[key as keyof Project],
                current = p[key as keyof Project];
              return JSON.stringify(old) !== JSON.stringify(current) ? (
                <details key={key} open={key === "title"}>
                  <summary>
                    Zmieniono:{" "}
                    {
                      (
                        {
                          title: "Tytuł filmu",
                          story: "Karta historii",
                          facts: "Bank faktów",
                          beats: "Fragmenty",
                          scenes: "Ujęcia",
                          sequence: "Montaż",
                        } as Record<string, string>
                      )[key]
                    }
                  </summary>
                  <div className="diff-grid">
                    <pre>
                      {typeof old === "string"
                        ? old
                        : JSON.stringify(old, null, 2)}
                    </pre>
                    <pre>
                      {typeof current === "string"
                        ? current
                        : JSON.stringify(current, null, 2)}
                    </pre>
                  </div>
                </details>
              ) : null;
            })}
          </>
        ) : (
          <p className="muted">
            Wybierz wersję do porównania. Przywrócenie tworzy nową rewizję i
            można je cofnąć.
          </p>
        )}
      </section>
    </div>
  );
}

function ChannelTools() {
  const s = useStudio(),
    p = s.project!;
  const [channels, setChannels] = useState<Record<string, unknown>[]>([]),
    [name, setName] = useState(p.channel),
    [style, setStyle] = useState(
      String(p.channel_profile.narrative_style || ""),
    ),
    [references, setReferences] = useState(
      String(p.channel_profile.references || ""),
    ),
    [color, setColor] = useState(String(p.channel_profile.color || "#b6baf0")),
    [visualStyle, setVisualStyle] = useState(
      String(p.channel_profile.visual_style || ""),
    ),
    [font, setFont] = useState(String(p.channel_profile.font || "montserrat"));
  useEffect(() => {
    setName(p.channel);
    setStyle(String(p.channel_profile.narrative_style || ""));
    setReferences(String(p.channel_profile.references || ""));
    setColor(String(p.channel_profile.color || "#b6baf0"));
    setVisualStyle(String(p.channel_profile.visual_style || ""));
    setFont(String(p.channel_profile.font || "montserrat"));
  }, [p.channel_id]);
  const [production, setProduction] = useState<{
    estimated_voice_seconds: number;
    spending: { estimated_cost: number; calls: number };
  } | null>(null);
  useEffect(() => {
    s.run(async () =>
      setProduction(
        await api<typeof production>(`/projects/${p.id}/production`),
      ),
    );
  }, [p.revision]);
  useEffect(() => {
    s.run(async () =>
      setChannels(await api<Record<string, unknown>[]>("/channels")),
    );
  }, []);
  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>Profil kanału</h2>
        <Field label="Zapisany kanał">
          <select
            value={p.channel_id}
            onChange={(e) => {
              const c = channels.find((x) => x.id === e.target.value);
              if (c)
                s.run(() =>
                  s.patch({
                    channel_id: String(c.id),
                    channel: String(c.name),
                    channel_profile: c,
                  }),
                );
            }}
          >
            <option value="">Własny profil projektu</option>
            {channels.map((c) => (
              <option key={String(c.id)} value={String(c.id)}>
                {String(c.name)}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Nazwa">
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </Field>
        <Field label="Styl narracji">
          <textarea
            rows={5}
            value={style}
            onChange={(e) => setStyle(e.target.value)}
          />
        </Field>
        <Field label="Referencje i zasady obrazu">
          <textarea
            rows={4}
            value={references}
            onChange={(e) => setReferences(e.target.value)}
          />
        </Field>
        <Field label="Kolor akcentu">
          <input
            type="color"
            value={color}
            onChange={(e) => setColor(e.target.value)}
          />
        </Field>
        <Field label="Styl generowanych obrazów">
          <textarea
            rows={3}
            value={visualStyle}
            onChange={(e) => setVisualStyle(e.target.value)}
            placeholder="Światło, faktura, epoka i sposób kadrowania"
          />
        </Field>
        <Field label="Krój napisów w filmie">
          <select value={font} onChange={(e) => setFont(e.target.value)}>
            <option value="montserrat">Montserrat</option>
            <option value="courier">Courier Prime</option>
            <option value="courier-bold">Courier Prime Bold</option>
          </select>
        </Field>
        <Button
          primary
          onClick={() =>
            s.run(async () => {
              const old = channels.find((c) => c.id === p.channel_id);
              const c = await api<Record<string, unknown>>("/channels", {
                ...(old || {}),
                name,
                narrative_style: style,
                visual_style: visualStyle,
                font,
                references,
                color,
                language: p.language,
              });
              await s.patch({
                channel_id: String(c.id),
                channel: name,
                channel_profile: c,
              });
              setChannels(await api<Record<string, unknown>[]>("/channels"));
            })
          }
        >
          Zapisz i zastosuj profil
        </Button>
        <p className="small muted">
          Historia tytułów jest wspólna dla kanału. Profil projektu jest
          migawką; zmiana kanału nie nadpisuje automatycznie wcześniejszych
          odcinków.
        </p>
      </section>
      <section className="surface tool-panel">
        <h2>Gotowość i limity automatyzacji</h2>
        {production && (
          <div className="inline-summary">
            <span>
              Szacowany koszt API:{" "}
              {production.spending.estimated_cost.toFixed(3)} ·{" "}
              {production.spending.calls} wywołań
            </span>
            <span>
              Do nagrania: około {Math.ceil(production.estimated_voice_seconds)}{" "}
              s narracji
            </span>
          </div>
        )}
        <NumberField
          label="Maksymalny koszt usług (waluta konta)"
          value={p.budget.max_cost ?? 0}
          min={0}
          max={100000}
          onCommit={(max_cost) =>
            s.run(() => s.patch((c) => ({ budget: { ...c.budget, max_cost } })))
          }
        />
        <NumberField
          label="Jednoczesne zadania"
          value={p.budget.max_jobs ?? 20}
          min={1}
          max={100}
          step={1}
          onCommit={(max_jobs) =>
            s.run(() => s.patch((c) => ({ budget: { ...c.budget, max_jobs } })))
          }
        />
        <NumberField
          label="Limit materiału automatyzacji (s)"
          value={p.budget.max_seconds ?? 3600}
          min={1}
          max={21600}
          step={1}
          onCommit={(max_seconds) =>
            s.run(() =>
              s.patch((c) => ({ budget: { ...c.budget, max_seconds } })),
            )
          }
        />
        <p className="small muted">
          Lokalny render i modele nie naliczają opłat API. Ceny i limit konta AI
          zależą od wybranego dostawcy; ustaw szacowaną cenę wywołania w
          połączeniu, aby Studio mogło egzekwować budżet.
        </p>
        <div className="button-row">
          <Button
            onClick={() => s.run(() => s.patch({ published: !p.published }))}
          >
            {p.published ? "Oznacz jako roboczy" : "Oznacz jako opublikowany"}
          </Button>
          <Button
            icon={Copy}
            onClick={() =>
              s.run(async () => {
                const c = await api<Project>(`/projects/${p.id}/duplicate`, {});
                await s.load(c.id);
                await s.reloadList();
              })
            }
          >
            Duplikuj projekt
          </Button>
          <Button
            onClick={() =>
              s.run(async () => {
                await s.patch({ archived: !p.archived });
                await s.reloadList();
              })
            }
          >
            {p.archived ? "Przywróć z archiwum" : "Archiwizuj projekt"}
          </Button>
        </div>
      </section>
    </div>
  );
}

function SystemTools() {
  const s = useStudio(),
    p = s.project!;
  const [path, setPath] = useState(""),
    [watch, setWatch] = useState(false),
    [diagnostic, setDiagnostic] = useState<{
      system: string;
      checks: { id: string; name: string; ok: boolean; detail: string }[];
    } | null>(null);
  useEffect(() => {
    s.run(async () => {
      const folder = await api<{ path?: string; enabled: boolean }>(
        `/projects/${p.id}/folder`,
      );
      setPath(folder.path || "");
      setWatch(folder.enabled);
    });
  }, [p.id]);
  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>Folder materiałów i naprawa powiązań</h2>
        <Field label="Lokalny folder">
          <input
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="/ścieżka/do/materiałów"
          />
        </Field>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={watch}
            onChange={(e) => setWatch(e.target.checked)}
          />
          Obserwuj folder i importuj zmiany
        </label>
        <div className="button-row">
          <Button
            primary
            disabled={!path}
            onClick={() =>
              s.run(async () => {
                await api(`/projects/${p.id}/folder`, {
                  path,
                  watch,
                  relink: true,
                });
                s.notify("Import folderu w kolejce");
              })
            }
          >
            Importuj i napraw powiązania
          </Button>
          <Button
            onClick={() =>
              s.run(async () => {
                await api(`/projects/${p.id}/folder`, undefined, "DELETE");
                s.notify("Wyłączono obserwowanie");
              })
            }
          >
            Wyłącz obserwowanie
          </Button>
        </div>
        <p className="small muted">
          Relink dopasowuje FILE/FILES z importu do unikalnych nazw. Kolizje
          nazw wymagają ręcznego wskazania właściwego materiału w Ujęciach.
        </p>
        <Button
          onClick={() =>
            s.run(() =>
              s.mutate((c) =>
                api<Project>(`/projects/${p.id}/relink`, {
                  expected_revision: c.revision,
                }),
              ),
            )
          }
        >
          Ponów dopasowanie biblioteki
        </Button>
        <h3>Kopia zapasowa</h3>
        <div className="button-row">
          <a className="button" href={`/api/projects/${p.id}/bundle`} download>
            Pełny projekt ZIP
          </a>
          <a
            className="button"
            href={`/api/projects/${p.id}/bundle?max_asset_mb=25`}
            download
          >
            Pakiet do 25 MB na plik
          </a>
        </div>
        <p className="small muted">
          Manifest opisuje pominięte pliki i sumy kontrolne. Odtwórz ZIP przez
          Importuj projekt. Prywatne próbki i klucze przechowuj osobno.
        </p>
        <label className="button">
          <Upload size={16} />
          Wczytaj poprawiony XLSX
          <input
            type="file"
            accept=".xlsx"
            className="visually-hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f)
                s.run(async () =>
                  s.accept(
                    await upload<Project>(`/projects/${p.id}/workbook`, f),
                  ),
                );
              e.target.value = "";
            }}
          />
        </label>
      </section>
      <section className="surface tool-panel">
        <h2>Diagnostyka lokalna</h2>
        <Button
          icon={RefreshCw}
          onClick={() =>
            s.run(async () =>
              setDiagnostic(await api<typeof diagnostic>("/diagnostics")),
            )
          }
        >
          Sprawdź środowiska i narzędzia
        </Button>
        {diagnostic && (
          <>
            <p className="small muted">{diagnostic.system}</p>
            {diagnostic.checks.map((c) => (
              <article className="diagnostic" key={c.id}>
                <span className={`badge ${c.ok ? "success" : "warning"}`}>
                  {c.ok ? "OK" : "Wymaga konfiguracji"}
                </span>
                <strong>{c.name}</strong>
                <p>{c.detail}</p>
              </article>
            ))}
          </>
        )}
        <Button
          onClick={() =>
            s.run(async () => {
              const r = await api<{ ok: boolean; message: string }>(
                "/ai/test",
                {},
              );
              s.notify(r.message, !r.ok);
            })
          }
        >
          Sprawdź logowanie i limit AI
        </Button>
      </section>
    </div>
  );
}
