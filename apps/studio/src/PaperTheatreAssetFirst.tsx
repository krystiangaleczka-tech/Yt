import { useEffect, useState } from "react";
import { ArrowDown, ArrowUp, Copy, Plus, Trash2 } from "lucide-react";
import { api, mediaUrl, saveText, upload, id as makeId } from "./api";
import { useStudio } from "./context";
import { Button, Field, NumberField } from "./components";
import type { Project, Scene } from "./types";

const GROUPS = [
  ["sky", "Niebo · osobne chmury/słońce"],
  ["landscape", "Krajobraz · góry"],
  ["foundations", "Fundamenty · mury i mosty"],
  ["vegetation", "Roślinność · pojedynczo"],
  ["props", "Rekwizyty i posągi"],
  ["characters", "Każda postać drugoplanowa"],
  ["hero", "Główna postać na samym końcu"],
] as const;
type Group = (typeof GROUPS)[number][0];
type ObjectSpec = {
  id: string; name: string; description: string; group: Group;
  x: number; y: number; width: number; z: number; asset_id: string;
  duration?: number;
};
type Manifest = { mode?: string; brief: string; style: string; objects: ObjectSpec[] };
type PromptResult = { id: string; name: string; prompt: string; group: string; asset_id: string };
const DEFAULT_STYLE = "Hand-cut textured rice paper, warm imperial parchment palette, muted ink outlines, subtle fiber texture, paper shadow edges; consistent lighting from top-left.";

const groupName = (key: string) => GROUPS.find(([id]) => id === key)?.[1] || key;
const textArea = (value: string, onChange: (value: string) => void, rows = 3) => (
  <textarea value={value} rows={rows} onChange={(event) => onChange(event.target.value)} />
);

export default function PaperTheatreAssetFirst({
  scene, background, setBackground, onCreate,
}: {
  scene?: Scene;
  background: string;
  setBackground: (value: string) => void;
  onCreate: () => void;
}) {
  const studio = useStudio();
  const project = studio.project!;
  const previous = scene?.generation?.paper_theatre_asset_first as Manifest | undefined;
  const [manifest, setManifest] = useState<Manifest>({
    brief: "", style: DEFAULT_STYLE, objects: [],
  });
  const [incoming, setIncoming] = useState("");
  const [promptSheet, setPromptSheet] = useState<PromptResult[]>([]);
  const [assistantPrompt, setAssistantPrompt] = useState("");
  const [gap, setGap] = useState(.12);
  const [groupGap, setGroupGap] = useState(.22);
  const [heroOutline, setHeroOutline] = useState(8);
  const [showPrompts, setShowPrompts] = useState(false);
  const assets = project.assets.filter((asset) => asset.kind === "image" && asset.filename.toLowerCase().endsWith(".png"));
  const ready = manifest.objects.filter((obj) => obj.asset_id).length;
  const missing = manifest.objects.length - ready;
  const selectedIds = new Set(manifest.objects.map((obj) => obj.asset_id).filter(Boolean));

  useEffect(() => {
    setManifest(previous?.objects?.length
      ? { ...previous, objects: previous.objects.map((obj) => ({ ...obj })) }
      : { brief: scene?.narration || "", style: DEFAULT_STYLE, objects: [] });
    setIncoming("");
    setPromptSheet([]);
    setAssistantPrompt("");
    setShowPrompts(false);
  }, [scene?.id]);

  const setValue = (patch: Partial<Manifest>) => {
    setManifest((previous) => ({ ...previous, ...patch }));
    setPromptSheet([]);
  };
  const modify = (key: string, patch: Partial<ObjectSpec>) => {
    setManifest((previous) => ({
      ...previous,
      objects: previous.objects.map((obj) => obj.id === key ? { ...obj, ...patch } : obj),
    }));
    setPromptSheet([]);
  };
  const move = (group: Group, index: number, direction: number) => {
    const selected = manifest.objects.filter((obj) => obj.group === group);
    const neighbor = selected[index + direction];
    if (!neighbor) return;
    const source = selected[index];
    setManifest((previous) => {
      const next = [...previous.objects], a = next.findIndex((o) => o.id === source.id),
        b = next.findIndex((o) => o.id === neighbor.id);
      [next[a], next[b]] = [next[b], next[a]];
      return { ...previous, objects: next };
    });
  };
  const addObject = () => {
    const label = "Nowy wycinek";
    setManifest((p) => ({ ...p, objects: [...p.objects, {
      id: makeId("object_"), name: label, description: label, group: "props",
      x: .5, y: .8, width: .18, z: 50, asset_id: "",
    }] }));
  };
  const params = () => ({
    expected_revision: project.revision,
    background_id: background,
    manifest,
    gap, group_gap: groupGap, hero_outline_px: heroOutline,
  });
  const copy = (value: string) => studio.run(async () => {
    await navigator.clipboard.writeText(value);
    studio.notify("Skopiowano prompt.");
  });
  const generateManifest = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz najpierw ujęcie Paper Theatre");
    const result = await api<{ manifest: Manifest }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/asset-first/propose`,
      { expected_revision: project.revision, action: "generate",
        brief: manifest.brief, style: manifest.style });
    setValue(result.manifest);
    studio.notify("Model zaproponował listę pojedynczych obiektów. Zweryfikuj ją przed zapisem.");
  });
  const showAssistantPrompt = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    const result = await api<{ prompt: string }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/asset-first/propose`,
      { expected_revision: project.revision, action: "prompt",
        brief: manifest.brief, style: manifest.style });
    setAssistantPrompt(result.prompt);
  });
  const importJSON = () => {
    try {
      const raw = incoming.trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
      const data = JSON.parse(raw) as Manifest;
      setValue(data);
      studio.notify("Zaimportowano roboczą listę. Sprawdź i zapisz plan.");
    } catch (error) {
      studio.notify(error instanceof Error ? error.message : "Niepoprawny JSON", true);
    }
  };
  const getPrompts = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    const result = await api<{ manifest: Manifest; prompts: PromptResult[] }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/asset-first/prompts`, params());
    setPromptSheet(result.prompts);
    setShowPrompts(true);
    studio.notify("Przygotowano oddzielny prompt dla każdego obiektu.");
  });
  const saveManifest = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    await studio.mutate((p) => api<Project>(
      `/projects/${p.id}/paper-theatre/${scene.id}/asset-first/save`,
      { ...params(), expected_revision: p.revision }));
    studio.notify("Zapisano manifest obiektów przed generowaniem obrazów.");
  });
  const assemble = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    await studio.mutate((p) => api<Project>(
      `/projects/${p.id}/paper-theatre/${scene.id}/asset-first/assemble`,
      { ...params(), expected_revision: p.revision }));
    studio.setTargetScene(scene.id);
    studio.notify("Scena złożona z osobnych PNG. Teraz sprawdź podgląd klatek i zastosuj ujęcie w Montażu.");
  });
  const addUploaded = (files: FileList | null) => studio.run(async () => {
    if (!files) return;
    for (const file of Array.from(files)) {
      if (file.type !== "image/png") throw new Error("Wymagane PNG; bez przezroczystości zostaną odrzucone przy składaniu");
      const response = await upload<{ project: Project }>(`/projects/${project.id}/media`, file);
      studio.accept(response.project);
    }
    studio.notify("Wgrano PNG. Dopasuj je do obiektów z listy.");
  });
  const updateObjectNumber = (obj: ObjectSpec, key: "x"|"y"|"width"|"z", value: number) => {
    modify(obj.id, { [key]: value });
  };

  return (
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>01 · Zaplanuj scenę zanim powstaną obrazy</h2>
        <p className="small muted">
          Asset-first: najpierw lista każdego obiektu, wspólny styl i dokładny
          układ. Dopiero potem oddzielnie generowane przezroczyste PNG.
          Nie rozcinamy już gotowej, spłaszczonej ilustracji.
        </p>
        {!scene && <Button primary icon={Plus} onClick={onCreate}>Nowe ujęcie Paper Theatre</Button>}
        <Field label="Co ma się dziać w tym ujęciu?">
          {textArea(manifest.brief, (brief) => setValue({ brief }), 4)}
        </Field>
        <Field label="Wspólny język wizualny dla wszystkich obiektów">
          {textArea(manifest.style, (style) => setValue({ style }), 3)}
        </Field>
        <div className="button-row">
          <Button onClick={generateManifest} disabled={!scene}>AI: przygotuj listę obiektów</Button>
          <Button onClick={showAssistantPrompt} disabled={!scene}>Prompt dla innego AI</Button>
          <Button icon={Plus} onClick={addObject} disabled={manifest.objects.length >= 200}>Dodaj obiekt ręcznie</Button>
        </div>
        {assistantPrompt && (
          <Field label="Prompt do skopiowania do dowolnego modelu tekstowego">
            {textArea(assistantPrompt, setAssistantPrompt, 8)}
            <Button icon={Copy} onClick={() => copy(assistantPrompt)}>Kopiuj</Button>
          </Field>
        )}
        <Field label="Import odpowiedzi AI (JSON z objects)">
          {textArea(incoming, setIncoming, 5)}
          <Button onClick={importJSON} disabled={!incoming.trim()}>Wczytaj listę z JSON</Button>
        </Field>
        <p className="small muted">
          Tryb AI działa przez model tekstowy skonfigurowany w ustawieniach Studio.
          Generowanie samych grafik PNG z prawdziwym alpha nie jest jeszcze
          zautomatyzowane przez tę kategorię. Prompty można wykorzystać w
          wybranym generatorze i wczytać jego rezultaty.
        </p>
        <div className="button-row">
          <Button onClick={saveManifest} disabled={!scene || !manifest.objects.length}>Zapisz listę obiektów</Button>
          <Button onClick={getPrompts} disabled={!scene || !manifest.objects.length}>Prompty dla każdego PNG</Button>
          <Button onClick={() => saveText("paper-theatre-asset-first.json", JSON.stringify(manifest, null, 2), "application/json")}>
            Eksport JSON
          </Button>
        </div>
        {showPrompts && <div>
          <h3>02 · Osobne prompty produkcyjne ({promptSheet.length})</h3>
          {promptSheet.map((item) => (
            <div key={item.id} className="surface" style={{ padding: 10, marginBottom: 8 }}>
              <strong>{item.name}</strong>
              <p className="small muted">{groupName(item.group)}</p>
              <p className="small">{item.prompt}</p>
              <Button icon={Copy} onClick={() => copy(item.prompt)}>Kopiuj prompt PNG</Button>
            </div>
          ))}
          <Button onClick={() => saveText("paper-theatre-prompts.json", JSON.stringify(promptSheet, null, 2), "application/json")}>
            Eksportuj wszystkie prompty
          </Button>
        </div>}
        <h3>03 · Wgraj i przypisz wygenerowane grafiki</h3>
        <Field label="Import wielu PNG">
          <input type="file" accept="image/png" multiple onChange={(event) => addUploaded(event.target.files)} />
        </Field>
        <Field label="Czyste tło PNG, bez obiektów które mają wejść później">
          <select value={background} onChange={(event) => setBackground(event.target.value)}>
            <option value="">Wybierz tło</option>
            {assets.map((asset) => <option value={asset.id} key={asset.id}>{asset.name}</option>)}
          </select>
        </Field>
        <div className="two-fields">
          <NumberField label="Przerwa między obiektami (s)" value={gap} min={0} max={5}
            step={.01} onCommit={setGap} />
          <NumberField label="Przerwa między grupami (s)" value={groupGap} min={0} max={5}
            step={.01} onCommit={setGroupGap} />
          <NumberField label="Obrys głównej postaci (px)" value={heroOutline} min={1} max={24}
            step={1} onCommit={setHeroOutline} />
        </div>
        <p><strong>{ready}/{manifest.objects.length}</strong> obiektów powiązanych z grafikami. Brakuje: {missing}.</p>
        <Button primary onClick={assemble} disabled={!scene || !background || !!missing || !manifest.objects.length}>
          Złóż scenę z osobnych grafik
        </Button>
        <p className="small muted">Obrys bohatera, kolejność wejść i wzajemne przesłanianie są zachowane w kompozytorze MP4. Scenę dodaj do montażu po sprawdzeniu klatek.</p>
      </section>
      <section className="surface tool-panel">
        <h2>Mapa kompozycji i obiektów</h2>
        <div style={{ position: "relative", aspectRatio: "16 / 9", overflow: "hidden",
                      border: "1px solid var(--border, #777)", borderRadius: 8,
                      background: "#c8b69c" }}>
          {background && <img src={mediaUrl(project.id, background)} alt="Tło"
            style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />}
          {[...manifest.objects].filter((obj) => obj.asset_id)
            .sort((a, b) => a.z - b.z)
            .map((obj) => (
              <img key={obj.id} src={mediaUrl(project.id, obj.asset_id)}
                alt={obj.name} title={obj.name}
                style={{ position: "absolute", left: `${obj.x * 100}%`,
                  bottom: `${(1 - obj.y) * 100}%`, width: `${obj.width * 100}%`,
                  height: "auto", transform: "translateX(-50%)",
                  objectFit: "contain" }} />
            ))}
        </div>
        <p className="small muted">
          Podgląd układu to mapa statyczna; ostateczne obcinanie przezroczystości,
          mechaniki wejść i kolejność Z są liczone przez renderer.
        </p>
        {GROUPS.map(([group, title]) => {
          const objects = manifest.objects.filter((obj) => obj.group === group);
          return (
            <section key={group}>
              <h3>{title} ({objects.length})</h3>
              {objects.map((obj, index) => (
                <div key={obj.id} className="surface" style={{ padding: 10, marginBottom: 9 }}>
                  <div className="button-row">
                    <strong>{obj.name}</strong>
                    <Button icon={ArrowUp} disabled={index === 0}
                      onClick={() => move(group, index, -1)}>Wyżej</Button>
                    <Button icon={ArrowDown} disabled={index === objects.length - 1}
                      onClick={() => move(group, index, 1)}>Niżej</Button>
                    <Button icon={Trash2} onClick={() =>
                      setValue({ objects: manifest.objects.filter((item) => item.id !== obj.id) })
                    }>Usuń</Button>
                  </div>
                  <Field label="Nazwa wycinka">
                    <input value={obj.name} onChange={(event) => modify(obj.id, { name: event.target.value })} />
                  </Field>
                  <Field label="Opis pojedynczego obiektu dla generatora obrazów">
                    {textArea(obj.description, (description) => modify(obj.id, { description }), 2)}
                  </Field>
                  <Field label="Grupa wejścia">
                    <select value={obj.group} onChange={(event) => modify(obj.id, { group: event.target.value as Group })}>
                      {GROUPS.map(([name, label]) => <option key={name} value={name}>{label}</option>)}
                    </select>
                  </Field>
                  <Field label="Przypisany osobny PNG">
                    <select value={obj.asset_id} onChange={(event) => modify(obj.id, { asset_id: event.target.value })}>
                      <option value="">Czeka na grafikę</option>
                      {assets.filter((a) => a.id !== background && (!selectedIds.has(a.id) || a.id === obj.asset_id))
                        .map((asset) => <option key={asset.id} value={asset.id}>{asset.name}</option>)}
                    </select>
                  </Field>
                  <div className="two-fields">
                    <NumberField label="X · środek (0–1)" value={obj.x} min={0} max={1} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "x", value)} />
                    <NumberField label="Y · stopa (0–1)" value={obj.y} min={0} max={1} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "y", value)} />
                    <NumberField label="Szerokość (0,01–2)" value={obj.width} min={.01} max={2} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "width", value)} />
                    <NumberField label="Z · przesłanianie" value={obj.z} min={-100} max={100} step={1}
                      onCommit={(value) => updateObjectNumber(obj, "z", Math.round(value))} />
                  </div>
                </div>
              ))}
            </section>
          );
        })}
      </section>
    </div>
  );
}
