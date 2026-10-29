import { useEffect, useState } from "react";
import { ArrowDown, ArrowUp, Plus, Trash2 } from "lucide-react";
import { api, upload } from "./api";
import { useStudio } from "./context";
import { Button, Field, NumberField } from "./components";
import type { Project, Scene } from "./types";
import { fps } from "./timing";

const GROUPS = [
  ["sky", "01 · Niebo: każda chmura, słońce, księżyc"],
  ["landscape", "02 · Góry i krajobraz"],
  ["foundations", "03 · Ciężkie fundamenty i architektura"],
  ["vegetation", "04 · Drzewa i roślinność"],
  ["props", "05 · Posągi i rekwizyty"],
  ["characters", "06 · Postacie po jednej"],
  ["hero", "07 · Najważniejsza postać jako ostatnia"],
] as const;
type Group = (typeof GROUPS)[number][0];
const GROUP_DURATION: Record<Group, number> = {
  sky: .42, landscape: .45, foundations: .5, vegetation: .33,
  props: .3, characters: .32, hero: .55,
};
type Layer = { asset_id: string; group: Group; duration?: number };
type Plan = {
  cutouts: number;
  total_seconds: number;
  hero_last: boolean;
  warnings: string[];
  layer_cues: { layer: number; group: string; start: number; duration: number; rig: string; outline_px?: number }[];
  quality: Record<string, boolean>;
};

export default function PaperTheatre() {
  const studio = useStudio();
  const project = studio.project!;
  const scenes = project.scenes.filter((shot) => shot.template === "paper-theatre");
  const [sceneId, setSceneId] = useState(scenes[0]?.id || "");
  const scene: Scene | undefined = scenes.find((item) => item.id === sceneId) || scenes[0];
  const [background, setBackground] = useState("");
  const [layers, setLayers] = useState<Layer[]>([]);
  const [gap, setGap] = useState(.12);
  const [groupGap, setGroupGap] = useState(.22);
  const [heroOutline, setHeroOutline] = useState(8);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [posterSeconds, setPosterSeconds] = useState(0);
  const assets = project.assets.filter((asset) => asset.kind === "image" && asset.filename.toLowerCase().endsWith(".png"));

  useEffect(() => {
    setBackground(scene?.asset_id || "");
    const cues = Array.isArray(scene?.parameters?.layer_cues)
      ? (scene.parameters.layer_cues as { layer: number; group?: Group; duration?: number }[])
      : [];
    setLayers((scene?.asset_ids || []).map((asset_id, index) => ({
      asset_id,
      group: GROUPS.some(([key]) => key === cues.find((cue) => cue.layer === index + 1)?.group)
        ? (cues.find((cue) => cue.layer === index + 1)?.group as Group)
        : "props",
      duration: cues.find((cue) => cue.layer === index + 1)?.duration,
    })));
    setPosterSeconds(0);
    setPlan(null);
  }, [scene?.id]);

  const invalidate = () => setPlan(null);
  const selected = new Set(layers.map((item) => item.asset_id));
  const available = assets.filter((asset) => asset.id !== background && !selected.has(asset.id));

  const options = () => ({
    expected_revision: project.revision,
    background_id: background,
    layers,
    gap,
    group_gap: groupGap,
    hero_outline_px: heroOutline,
  });
  const setLayer = (index: number, changes: Partial<Layer>) => {
    setLayers((current) => current.map((layer, i) => i === index ? { ...layer, ...changes } : layer));
    invalidate();
  };
  const move = (index: number, neighbor: number) => {
    setLayers((current) => {
      const next = [...current];
      [next[index], next[neighbor]] = [next[neighbor], next[index]];
      return next;
    });
    invalidate();
  };

  const create = () => studio.run(async () => {
    const next = await studio.mutate((p) =>
      api<Project>(`/projects/${p.id}/paper-theatre/scenes`, { expected_revision: p.revision }));
    const last = next.scenes[next.scenes.length - 1];
    setSceneId(last.id);
    studio.setTargetScene(last.id);
    studio.notify("Dodano osobne ujęcie Paper Theatre 2.5D.");
  });

  const preview = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz najpierw ujęcie Paper Theatre");
    const value = await api<Plan>(`/projects/${project.id}/paper-theatre/${scene.id}/preview`, options());
    setPlan(value);
    studio.notify("Plan i indywidualne warstwy sprawdzone.");
  });

  const save = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie Paper Theatre");
    const saved = await studio.mutate((p) =>
      api<Project>(`/projects/${p.id}/paper-theatre/${scene.id}/commit`, {
        ...options(), expected_revision: p.revision,
      }));
    studio.setTargetScene(scene.id);
    studio.notify(`Zapisano ${saved.scenes.find((x) => x.id === scene.id)?.asset_ids?.length || 0} wycinków. Sprawdź podgląd klatek.`);
  });

  const toTimeline = () => studio.run(async () => {
    if (!scene) throw new Error("Brak ujęcia");
    await studio.mutate((p) => api<Project>(`/projects/${p.id}/scenes/${scene.id}/to-timeline`, {
      expected_revision: p.revision,
    }));
    studio.notify("Zastosowano Paper Theatre na osi montażowej.");
  });

  const addAsset = (id: string) => {
    setLayers((current) => [...current, { asset_id: id, group: "props" }]);
    invalidate();
  };
  const importPng = (files: FileList | null) => studio.run(async () => {
    if (!files) return;
    for (const file of Array.from(files)) {
      if (file.type !== "image/png") throw new Error("Paper Theatre wymaga osobnych PNG z kanałem alpha");
      const result = await upload<{ project: Project }>(`/projects/${project.id}/media`, file);
      studio.accept(result.project);
    }
    studio.notify("Wczytano wycinki. Przypisz każdemu rolę i kolejność.");
  });

  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>Paper Theatre 2.5D · osobna kategoria</h2>
        <p className="small muted">
          Każda najmniejsza chmura, góra, wieża, drzewo, rekwizyt i postać to
          oddzielny PNG z przezroczystością. Kolejne grupy nie nakładają się
          czasowo. Postacie wstają pojedynczo; główna postać pojawia się
          ostatnia, z największym obrysem.
        </p>
        <div className="button-row">
          <Button icon={Plus} primary onClick={create}>Nowe ujęcie Paper Theatre</Button>
        </div>
        {scenes.length > 0 && (
          <Field label="Edytowane ujęcie">
            <select value={scene?.id || ""} onChange={(event) => {
              setSceneId(event.target.value);
              studio.setTargetScene(event.target.value);
            }}>
              {scenes.map((shot) => <option key={shot.id} value={shot.id}>{shot.title}</option>)}
            </select>
          </Field>
        )}
        <Field label="Import pojedynczych wycinków PNG (można zaznaczyć wiele plików)">
          <input type="file" accept="image/png" multiple onChange={(event) => importPng(event.target.files)} />
        </Field>
        <p className="small muted">
          Spłaszczony obraz nie zawiera niewidocznych tyłów obiektów.
          Nie oznaczamy automatycznej segmentacji jako gotowej: wybierz
          czyste tło i prawdziwie wycięte PNG.
        </p>
        <Field label="Tło bez postaci i rekwizytów">
          <select value={background} onChange={(event) => {
            const selectedId = event.target.value;
            setBackground(selectedId);
            setLayers((current) => current.filter((layer) => layer.asset_id !== selectedId));
            invalidate();
          }}>
            <option value="">Wybierz czyste tło PNG</option>
            {assets.map((asset) => <option value={asset.id} key={asset.id}>{asset.name}</option>)}
          </select>
        </Field>
        <Field label="Dodaj osobny wycinek z biblioteki">
          <select value="" onChange={(event) => event.target.value && addAsset(event.target.value)}>
            <option value="">Wybierz plik PNG…</option>
            {available.map((asset) => <option value={asset.id} key={asset.id}>{asset.name}</option>)}
          </select>
        </Field>
        <div className="two-fields">
          <NumberField label="Odstęp między elementami (s)" value={gap} min={0} max={5}
            step={.01} onCommit={(v) => { setGap(v); invalidate(); }} />
          <NumberField label="Przerwa między grupami (s)" value={groupGap} min={0} max={5}
            step={.01} onCommit={(v) => { setGroupGap(v); invalidate(); }} />
          <NumberField label="Obrys głównej postaci (px)" value={heroOutline} min={1} max={24}
            step={1} onCommit={(v) => { setHeroOutline(v); invalidate(); }} />
        </div>
        <div className="button-row">
          <Button onClick={preview} disabled={!scene || !background || !layers.length}>Sprawdź plan i PNG</Button>
          <Button primary onClick={save} disabled={!scene || !background || !layers.length}>Zapisz Paper Theatre</Button>
          <Button onClick={toTimeline} disabled={!scene?.asset_id || !scene.asset_ids?.length}>Zastosuj w montażu</Button>
        </div>
        {plan && (
          <div aria-live="polite">
            <p><strong>{plan.cutouts} wycinków</strong> · ostatnie wejście: {plan.total_seconds.toFixed(2)} s · bohater na końcu: {plan.hero_last ? "tak" : "brak"}</p>
            <p className="small muted">Zweryfikowano pliki PNG i alpha, nie zgodność wizualną 1:1 ani brak zasłoniętych pikseli.</p>
            {plan.warnings.map((warning, index) => <p className="small muted" key={index}>{warning}</p>)}
          </div>
        )}
      </section>
      <section className="surface tool-panel">
        <h2>Scenografia · kolejność grup</h2>
        {GROUPS.map(([group, title]) => {
          const items = layers.map((layer, index) => ({ layer, index }))
            .filter((item) => item.layer.group === group);
          return (
            <section key={group} aria-label={title}>
              <h3>{title} ({items.length})</h3>
              {items.map(({ layer, index }, groupIndex) => (
                <div className="surface" key={layer.asset_id} style={{ padding: 10, marginBottom: 8 }}>
                  <div className="button-row">
                    <strong>{project.assets.find((asset) => asset.id === layer.asset_id)?.name || layer.asset_id}</strong>
                    <Button icon={ArrowUp} disabled={groupIndex === 0}
                      onClick={() => move(index, items[groupIndex - 1].index)}>Wyżej</Button>
                    <Button icon={ArrowDown} disabled={groupIndex === items.length - 1}
                      onClick={() => move(index, items[groupIndex + 1].index)}>Niżej</Button>
                    <Button icon={Trash2} onClick={() => {
                      setLayers((current) => current.filter((_, i) => i !== index)); invalidate();
                    }}>Usuń</Button>
                  </div>
                  <Field label="Rola tego konkretnego wycinka">
                    <select value={layer.group} onChange={(event) => setLayer(index, { group: event.target.value as Group })}>
                      {GROUPS.map(([key, label]) => <option value={key} key={key}>{label}</option>)}
                    </select>
                  </Field>
                  <NumberField label="Czas własnego wejścia (s)"
                    value={layer.duration ?? GROUP_DURATION[group]}
                    min={.05} max={10} step={.01}
                    onCommit={(v) => setLayer(index, { duration: v })} />
                </div>
              ))}
            </section>
          );
        })}
        {scene?.asset_id && (
          <section>
            <h3>Podgląd dokładnej klatki z kompozytora</h3>
            <NumberField label="Sekunda ujęcia" value={posterSeconds}
              min={0} max={Math.max(0, (scene.duration - 1) / fps(project))}
              step={.1} onCommit={setPosterSeconds} />
            <img
              alt="Podgląd sceny Paper Theatre z rzeczywistego renderera warstw"
              style={{ width: "100%", aspectRatio: "16 / 9", objectFit: "contain" }}
              src={`/api/projects/${project.id}/scenes/${scene.id}/poster?revision=${project.revision}&frame=${Math.min(scene.duration - 1, Math.round(posterSeconds * fps(project)))}`}
            />
          </section>
        )}
      </section>
    </div>
  );
}
