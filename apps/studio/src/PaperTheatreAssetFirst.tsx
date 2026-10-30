import { useEffect, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { ArrowDown, ArrowUp, Copy, Plus, Trash2 } from "lucide-react";
import { api, mediaUrl, saveText, upload, id as makeId } from "./api";
import { useStudio } from "./context";
import { Button, Field, NumberField } from "./components";
import type { Project, Scene } from "./types";
import PaperCutoutMaskEditor from "./PaperCutoutMaskEditor";
import PaperTheatreLive, { type LiveSource } from "./PaperTheatreLive";
import type { Cue } from "./paperTheatreMotion";
import { fps } from "./timing";
import PaperTheatreReview from "./PaperTheatreReview";
import PaperCutoutPreview from "./PaperCutoutPreview";

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
  pivot_x?: number; pivot_y?: number;
  rig?: "hanging_drop" | "bottom_rise" | "rake_lift" | "static";
};
type Manifest = {
  mode?: "asset-first" | "reference-guided";
  brief: string; style: string; objects: ObjectSpec[];
  reference_asset_id?: string; reference_notes?: string; reference_approved?: boolean;
};
type PromptResult = { id: string; name: string; prompt: string; group: string; asset_id: string };
type DraftPlan = { asset_ids: string[]; layer_cues: Cue[]; total_seconds: number };
// Same mapping as assemble_manifest(): what the planner would receive.
const toLayer = (obj: ObjectSpec) => ({
  asset_id: obj.asset_id, group: obj.group,
  ...(obj.pivot_x !== undefined ? { pivot_x: obj.pivot_x } : {}),
  ...(obj.pivot_y !== undefined ? { pivot_y: obj.pivot_y } : {}),
  ...(obj.rig ? { rig: obj.rig } : {}),
  layout_x: obj.x, layout_y: obj.y, layout_width: obj.width, z_index: Math.round(obj.z),
  ...(obj.duration !== undefined ? { duration: obj.duration } : {}),
});
const DEFAULT_STYLE = "Hand-cut textured paper, coordinated muted palette, subtle ink outlines, visible paper fibers and shadows; one coherent light direction. Adapt era and color scheme to the story.";

const groupName = (key: string) => GROUPS.find(([id]) => id === key)?.[1] || key;
const textArea = (value: string, onChange: (value: string) => void, rows = 3) => (
  <textarea value={value} rows={rows} onChange={(event) => onChange(event.target.value)} />
);

export default function PaperTheatreAssetFirst({
  scene, background, setBackground, onCreate, referenceMode = false,
}: {
  scene?: Scene;
  referenceMode?: boolean;
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
  const [heroOutline, setHeroOutline] = useState(16);
  const [showPrompts, setShowPrompts] = useState(false);
  const [referenceId, setReferenceId] = useState("");
  const [referenceNotes, setReferenceNotes] = useState("");
  const [referenceApproved, setReferenceApproved] = useState(false);
  const [referencePrompt, setReferencePrompt] = useState("");
  const [draftJobId, setDraftJobId] = useState("");
  const [cutoutJobId, setCutoutJobId] = useState("");
  const [cutoutObjectId, setCutoutObjectId] = useState("");
  const [batchJobId, setBatchJobId] = useState("");
  const [selectedObjectId, setSelectedObjectId] = useState("");
  const dragOffsetRef = useRef<{ id: string; x: number; y: number } | null>(null);
  const [maskObjectId, setMaskObjectId] = useState("");
  const [entranceDirty, setEntranceDirty] = useState(false);
  const assets = project.assets.filter((asset) => asset.kind === "image" && asset.filename.toLowerCase().endsWith(".png"));
  const references = project.assets.filter((asset) => asset.kind === "image" &&
    /\.(png|jpe?g)$/i.test(asset.filename));
  const ready = manifest.objects.filter((obj) => obj.asset_id).length;
  const missing = manifest.objects.length - ready;
  const selectedIds = new Set(manifest.objects.map((obj) => obj.asset_id).filter(Boolean));
  const candidateFor = (obj: ObjectSpec) => project.assets.find((asset) =>
    asset.provenance?.kind === "paper-theatre-cutout" &&
    asset.provenance?.scene_id === scene?.id &&
    asset.provenance?.reference_asset_id === referenceId &&
    asset.provenance?.object_id === obj.id);
  const missingWithNoVariant = manifest.objects.filter((obj) => !obj.asset_id && !candidateFor(obj));
  const [draftPlan, setDraftPlan] = useState<DraftPlan | null>(null);
  const [draftState, setDraftState] = useState("");
  const [liveSaved, setLiveSaved] = useState(false);
  const manifestRef = useRef(manifest);
  manifestRef.current = manifest;

  useEffect(() => {
    setManifest(previous?.objects?.length
      ? { ...previous, objects: previous.objects.map((obj) => ({ ...obj })) }
      : { brief: scene?.narration || "", style: DEFAULT_STYLE, objects: [] });
    const reference = scene?.generation?.paper_theatre_reference as
      { asset_id?: string; approved?: boolean } | undefined;
    setReferenceId(previous?.reference_asset_id || reference?.asset_id || "");
    setReferenceNotes(previous?.reference_notes || "");
    setReferenceApproved(previous?.reference_approved ?? reference?.approved ?? false);
    const settings = scene?.generation?.paper_theatre_settings as { gap?: number; group_gap?: number; hero_outline_px?: number } | undefined;
    setGap(settings?.gap ?? .12);
    setGroupGap(settings?.group_gap ?? .22);
    setHeroOutline(settings?.hero_outline_px ?? 16);
    setEntranceDirty(false);
    setIncoming("");
    setPromptSheet([]);
    setAssistantPrompt("");
    setShowPrompts(false);
  }, [scene?.id]);

  useEffect(() => {
    if (!draftJobId) return;
    const job = studio.jobs.find((item) => item.id === draftJobId);
    if (job?.status === "SUCCEEDED") {
      setDraftJobId("");
      void studio.reload();
    } else if (job?.status === "FAILED" || job?.status === "CANCELLED") {
      setDraftJobId("");
      studio.notify(job.message || "Nie udało się przygotować draftu", true);
    }
  }, [draftJobId, studio.jobs]);

  useEffect(() => {
    const reference = scene?.generation?.paper_theatre_reference as { asset_id?: string } | undefined;
    if (reference?.asset_id && !referenceId) {
      setReferenceId(reference.asset_id);
      setReferenceApproved(false);
    }
  }, [scene?.generation?.paper_theatre_reference, referenceId]);

  useEffect(() => {
    if (!cutoutJobId) return;
    const job = studio.jobs.find((item) => item.id === cutoutJobId);
    if (job?.status === "SUCCEEDED") {
      setCutoutJobId("");
      setCutoutObjectId("");
      void studio.reload();
      studio.notify("Wygenerowano rzeczywisty PNG alpha do biblioteki. Obejrzyj go i przypisz ręcznie do obiektu.");
    } else if (job?.status === "FAILED" || job?.status === "CANCELLED") {
      setCutoutJobId("");
      setCutoutObjectId("");
      studio.notify(job.message || "Generator PNG nie zwrócił poprawnego wycinka.", true);
    }
  }, [cutoutJobId, studio.jobs]);

  useEffect(() => {
    if (!batchJobId) return;
    const job = studio.jobs.find((item) => item.id === batchJobId);
    if (job?.status === "SUCCEEDED") {
      setBatchJobId("");
      void studio.reload();
      const count = job.result?.asset_ids?.length || 0;
      studio.notify(`Wygenerowano ${count} nowych PNG. Sprawdź je w bibliotece i przypisz ręcznie do obiektów.`);
    } else if (job?.status === "FAILED" || job?.status === "CANCELLED") {
      setBatchJobId("");
      studio.notify(job.message || "Seria generowania PNG została przerwana.", true);
    }
  }, [batchJobId, studio.jobs]);

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
  const effectiveManifest = (): Manifest => ({
    ...manifest,
    mode: referenceMode ? "reference-guided" : "asset-first",
    reference_asset_id: referenceMode ? referenceId : "",
    reference_notes: referenceMode ? referenceNotes : "",
    reference_approved: referenceMode ? referenceApproved : false,
  });
  const params = () => ({
    expected_revision: project.revision,
    background_id: background,
    manifest: effectiveManifest(),
    gap, group_gap: groupGap, hero_outline_px: heroOutline,
  });
  const copy = (value: string) => studio.run(async () => {
    await navigator.clipboard.writeText(value);
    studio.notify("Skopiowano prompt.");
  });
  const generateManifest = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz najpierw ujęcie Paper Theatre");
    if (referenceMode && (!referenceId || !referenceApproved)) {
      throw new Error("Najpierw wybierz i zaakceptuj draft referencyjny");
    }
    const route = referenceMode ? "reference/analyze" : "asset-first/propose";
    const result = await api<{ manifest: Manifest }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/${route}`,
      { expected_revision: project.revision, action: "generate",
        brief: manifest.brief, style: manifest.style,
        ...(referenceMode ? { reference_asset_id: referenceId, reference_notes: referenceNotes } : {}) });
    setValue(result.manifest);
    studio.notify("Model zaproponował osobne obiekty. Zweryfikuj je przed zapisem.");
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
      const data = JSON.parse(raw) as Partial<Manifest>;
      if (!data || typeof data.brief !== "string" || typeof data.style !== "string" ||
          !Array.isArray(data.objects) || !data.objects.every((obj) =>
            obj && typeof obj === "object" && typeof obj.id === "string" &&
            typeof obj.name === "string" && typeof obj.group === "string")) {
        throw new Error("JSON musi zawierać brief, style i tablicę pojedynczych objects.");
      }
      setValue(data as Manifest);
      if (referenceMode) {
        setReferenceId(data.reference_asset_id || "");
        setReferenceNotes(data.reference_notes || "");
        setReferenceApproved(Boolean(data.reference_approved));
      }
      studio.notify("Zaimportowano roboczą listę. Sprawdź i zapisz plan.");
    } catch (error) {
      studio.notify(error instanceof Error ? error.message : "Niepoprawny JSON", true);
    }
  };
  const generateCutout = (obj: ObjectSpec, newVariant = false) => studio.run(async () => {
    if (!scene || !referenceMode || !referenceId || !referenceApproved)
      throw new Error("Zaakceptuj najpierw obraz referencyjny");
    if (obj.asset_id) throw new Error("Odłącz obecny PNG przed ponownym generowaniem");
    if (newVariant) {
      const settings = await api<{ paper_image_request_cost: number }>("/settings");
      if (!window.confirm(`Istnieje już wariant dla ${obj.name}.
Wygenerować dodatkowy, płatny PNG? Szacowany koszt: ${settings.paper_image_request_cost} USD.`))
        return;
    }
    const result = await api<{ id: string }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/cutouts/generate`,
      { expected_revision: project.revision, manifest: effectiveManifest(),
        object_id: obj.id, new_variant: newVariant });
    setCutoutJobId(result.id);
    setCutoutObjectId(obj.id);
    studio.notify("W kolejce: jeden osobny przezroczysty PNG. Wymaga Twojej akceptacji po wygenerowaniu.");
  });
  const generateBatch = () => studio.run(async () => {
    if (!scene || !referenceMode || !referenceApproved || !referenceId)
      throw new Error("Zatwierdź najpierw obraz referencyjny");
    const ids = missingWithNoVariant.slice(0, 12).map((obj) => obj.id);
    if (!ids.length) throw new Error("Wszystkie wycinki mają plik lub niezatwierdzony wariant");
    const settings = await api<{ paper_image_configured: boolean; paper_image_request_cost: number }>("/settings");
    if (!settings.paper_image_configured || !settings.paper_image_request_cost)
      throw new Error("W Połączeniach wpisz klucz generatora i koszt jednego PNG");
    const estimate = settings.paper_image_request_cost * ids.length;
    if (!window.confirm(`Wygenerować ${ids.length} niezależnych PNG z zaakceptowaną referencją?
Szacowany koszt maksymalny tej serii: ${estimate.toFixed(2)} USD.
Rzeczywiste naliczenie zależy od dostawcy. Żadna warstwa nie zostanie wybrana automatycznie.`)) return;
    const result = await api<{ id: string }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/cutouts/batch-generate`,
      { expected_revision: project.revision, manifest: effectiveManifest(), object_ids: ids });
    setBatchJobId(result.id);
    studio.notify("Rozpoczęto seryjne generowanie warstw. Wyniki trafią do biblioteki.");
  });
  const getPrompts = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    if (referenceMode && (!referenceId || !referenceApproved))
      throw new Error("Zaakceptuj draft, zanim przygotujesz prompty obiektów");
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
    if (referenceMode && (!referenceId || !referenceApproved))
      throw new Error("Przed złożeniem sceny trzeba zaakceptować szkic");
    const assembled = await studio.mutate((p) => api<Project>(
      `/projects/${p.id}/paper-theatre/${scene.id}/asset-first/assemble`,
      { ...params(), expected_revision: p.revision }));
    const saved = assembled.scenes.find(s => s.id === scene.id)?.generation?.paper_theatre_asset_first as Manifest | undefined;
    if (saved) setManifest(saved);
    setEntranceDirty(false);
    studio.setTargetScene(scene.id);
    await studio.mutate((p) => api<Project>(
      `/projects/${p.id}/paper-theatre/${scene.id}/review/preview`,
      { expected_revision: p.revision }));
    studio.notify("Przygotowano rzeczywistą klatkę. Porównaj z referencją i przekaż autorowi do oceny.");
  });
  const addUploaded = (files: FileList | null) => studio.run(async () => {
    if (!files) return;
    const imported: { name: string; id: string }[] = [];
    for (const file of Array.from(files)) {
      if (file.type !== "image/png") throw new Error("Wymagane PNG; bez przezroczystości zostaną odrzucone przy składaniu");
      const response = await upload<{ project: Project; asset: { id: string } }>(
        `/projects/${project.id}/media`, file);
      studio.accept(response.project);
      imported.push({ name: file.name.replace(/\.png$/i, "").toLowerCase(), id: response.asset.id });
    }
    // Match only exact object IDs; never guess a person's identity from a PNG
    // filename or overwrite an already approved linked asset.
    setManifest((previous) => ({
      ...previous,
      objects: previous.objects.map((obj) => {
        if (obj.asset_id) return obj;
        const match = imported.filter((item) => item.name === obj.id.toLowerCase());
        return match.length === 1 ? { ...obj, asset_id: match[0].id } : obj;
      }),
    }));
    studio.notify("Zaimportowano PNG. Pliki nazwane dokładnie jak ID obiektu przypisano automatycznie.");
  });
  const requestDraftPrompt = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    const result = await api<{ prompt: string }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/reference/prompt`,
      { expected_revision: project.revision, brief: manifest.brief, style: manifest.style });
    setReferencePrompt(result.prompt);
  });
  const createDraft = () => studio.run(async () => {
    if (!scene) throw new Error("Utwórz ujęcie");
    const result = await api<{ id: string }>(
      `/projects/${project.id}/paper-theatre/${scene.id}/reference/generate`,
      { expected_revision: project.revision, brief: manifest.brief, style: manifest.style });
    setDraftJobId(result.id);
    studio.notify("Draft 512 × 288 trafił do kolejki generatora.");
  });
  const uploadReference = (files: FileList | null) => studio.run(async () => {
    const file = files?.[0];
    if (!file) return;
    if (!["image/png", "image/jpeg"].includes(file.type))
      throw new Error("Obraz poglądowy musi być PNG lub JPEG");
    const response = await upload<{ project: Project; asset: { id: string } }>(
      `/projects/${project.id}/media`, file);
    studio.accept(response.project);
    setReferenceId(response.asset.id);
    setReferenceApproved(false);
  });
  const saveCutoutMask = (obj: ObjectSpec, png: Blob) => studio.run(async () => {
    if (!scene || !obj.asset_id) throw new Error("Wybierz wycinek i ujęcie");
    const file = new File([png], obj.id + "-mask.png", { type: "image/png" });
    const result = await upload<{ project: Project; asset: { id: string } }>(
      `/projects/${project.id}/media`, file);
    studio.accept(result.project);
    modify(obj.id, { asset_id: result.asset.id });
    setMaskObjectId("");
    studio.notify("Nowa maska alpha zapisana jako osobny PNG. Oryginał pozostał w bibliotece.");
  });
  // Live preview of unsaved edits: the planner (POST /preview, saves nothing)
  // gives exact entrance timing; dragged positions are overlaid at once.
  const rate = fps(project);
  const linked = manifest.objects.filter((obj) => obj.asset_id);
  const timingKey = JSON.stringify([scene?.id, project.revision, background, gap, groupGap, heroOutline,
    // Positions are overlaid locally, so dragging does not wait for the server.
    linked.map((obj) => [obj.asset_id, obj.group, obj.pivot_x, obj.pivot_y, obj.rig, obj.duration])]);
  useEffect(() => {
    if (!scene || !background || !linked.length) { setDraftPlan(null); setDraftState(""); return; }
    let alive = true;
    setDraftState("przeliczam harmonogram…");
    const handle = window.setTimeout(() => {
      api<DraftPlan>(`/projects/${project.id}/paper-theatre/${scene.id}/preview`, {
        expected_revision: project.revision, background_id: background,
        layers: manifestRef.current.objects.filter((obj) => obj.asset_id).map(toLayer),
        gap, group_gap: groupGap, hero_outline_px: Math.round(heroOutline),
      }).then((plan) => { if (alive) { setDraftPlan(plan); setDraftState(""); } })
        .catch((reason) => { if (alive) setDraftState(reason instanceof Error ? reason.message : String(reason)); });
    }, 250);
    return () => { alive = false; window.clearTimeout(handle); };
  }, [timingKey]);
  const frameSize = { width: project.sequence.width, height: project.sequence.height, fps: rate };
  const draftSource: LiveSource | null = draftPlan && scene && background ? {
    label: "Bieżące zmiany (niezapisane)",
    def: {
      ...frameSize, template: "paper-theatre",
      durationFrames: Math.max(scene.duration, Math.ceil(draftPlan.total_seconds * rate)),
      background: mediaUrl(project.id, background),
      layers: draftPlan.asset_ids.map((assetId) => mediaUrl(project.id, assetId)),
      params: { depth: 0, caption: "", layer_cues: draftPlan.layer_cues.map((cue, index) => {
        const obj = manifest.objects.find((item) => item.asset_id === draftPlan.asset_ids[index]);
        return obj ? { ...cue, layout_x: obj.x, layout_y: obj.y, layout_width: obj.width, z_index: Math.round(obj.z) } : cue;
      }) },
    },
  } : null;
  const savedLayers = (() => {
    const seen = new Set([scene?.asset_id]);
    return (scene?.asset_ids || []).filter((assetId) => !seen.has(assetId) && !!seen.add(assetId));
  })();
  const savedSource: LiveSource | null = scene?.asset_id && savedLayers.length ? {
    label: "Zapisane ujęcie",
    def: {
      ...frameSize, template: scene.template || "paper-theatre", durationFrames: scene.duration,
      background: mediaUrl(project.id, scene.asset_id),
      layers: savedLayers.map((assetId) => mediaUrl(project.id, assetId)),
      params: { depth: .015, caption: "", ...scene.parameters },
    },
    exactFrame: (frame) => `/api/projects/${project.id}/scenes/${scene.id}/poster?revision=${project.revision}&frame=${frame}`,
  } : null;
  const liveSource = (liveSaved ? savedSource || draftSource : draftSource || savedSource);
  const liveHint = draftState || (!scene ? "Utwórz ujęcie Paper Theatre" : !background
    ? "Wybierz czyste tło, aby oglądać bieżące zmiany" : !linked.length
      ? "Przypisz PNG do obiektów, aby oglądać bieżące zmiany" : "");

  const updateObjectNumber = (obj: ObjectSpec, key: "x"|"y"|"width"|"z"|"pivot_x"|"pivot_y", value: number) => {
    modify(obj.id, { [key]: value });
  };

  const placeFromPointer = (obj: ObjectSpec, event: ReactPointerEvent<HTMLImageElement>) => {
    const rect = event.currentTarget.parentElement?.getBoundingClientRect();
    if (!rect || !rect.width || !rect.height) return;
    const offset = dragOffsetRef.current?.id === obj.id ? dragOffsetRef.current : null;
    modify(obj.id, {
      x: Math.min(1, Math.max(0, Math.round(((event.clientX - rect.left) / rect.width - (offset?.x || 0)) * 1000) / 1000)),
      y: Math.min(1, Math.max(0, Math.round(((event.clientY - rect.top) / rect.height - (offset?.y || 0)) * 1000) / 1000)),
    });
  };

  const dirty = entranceDirty || background !== (scene?.asset_id || "") ||
    JSON.stringify(effectiveManifest()) !== JSON.stringify(previous || {});
  const compare = () => {
    if (dirty) { assemble(); return; }
    studio.run(async () => {
      if (!scene) throw new Error("Utwórz ujęcie");
      await studio.mutate(p => api<Project>(
        `/projects/${p.id}/paper-theatre/${scene.id}/review/preview`,
        { expected_revision: p.revision }));
    });
  };

  return (<>
    <PaperTheatreReview scene={scene} onCompare={compare} dirty={dirty} />
    <div className="production-grid">
      <section className="surface tool-panel">
        <h2>{referenceMode ? "02 · Obiekty na podstawie zatwierdzonego szkicu" : "01 · Zaplanuj scenę zanim powstaną obrazy"}</h2>
        <p className="small muted">
          {referenceMode
            ? "Draft wskazuje kompozycję, proporcje i estetykę. Każdy obiekt generujemy osobno. Nie wycinamy pikseli z poglądowej ilustracji."
            : "Najpierw lista każdego obiektu, wspólny styl i dokładny układ. Dopiero potem osobne przezroczyste PNG."}
        </p>
        {!scene && <Button primary icon={Plus} onClick={onCreate}>Nowe ujęcie Paper Theatre</Button>}
        <Field label="Co ma się dziać w tym ujęciu?">
          {textArea(manifest.brief, (brief) => setValue({ brief }), 4)}
        </Field>
        <Field label="Wspólny język wizualny dla wszystkich obiektów">
          {textArea(manifest.style, (style) => setValue({ style }), 3)}
        </Field>
        {referenceMode && <div className="surface" style={{ padding: 12, marginBottom: 12 }}>
          <h3>01 · Mały obraz poglądowy ze scenariusza</h3>
          <p className="small muted">Najpierw szkic 16:9 całej sceny. Zaakceptowany obraz będzie wzorem kompozycji, nie źródłem wycinanych pikseli.</p>
          <div className="button-row">
            <Button onClick={requestDraftPrompt} disabled={!scene}>Przygotuj prompt szkicu</Button>
            <Button onClick={createDraft} disabled={!scene || !!draftJobId}>Wygeneruj draft 512 × 288</Button>
          </div>
          {draftJobId && <p className="small muted">Generator pracuje: {draftJobId}. Wynik pojawi się w bibliotece.</p>}
          {referencePrompt && <Field label="Prompt małego obrazu referencyjnego">
            {textArea(referencePrompt, setReferencePrompt, 5)}
            <Button icon={Copy} onClick={() => copy(referencePrompt)}>Kopiuj prompt</Button>
          </Field>}
          <Field label="Lub wgraj własny mały szkic PNG/JPEG">
            <input type="file" accept="image/png,image/jpeg" onChange={(event) => uploadReference(event.target.files)} />
          </Field>
          <Field label="Wybrany obraz poglądowy">
            <select value={referenceId} onChange={(event) => {
              setReferenceId(event.target.value); setReferenceApproved(false);
            }}>
              <option value="">Wybierz draft z biblioteki</option>
              {references.map((asset) => <option value={asset.id} key={asset.id}>{asset.name}</option>)}
            </select>
          </Field>
          {referenceId && <>
            <img alt="Obraz referencyjny całej sceny" src={mediaUrl(project.id, referenceId)}
              style={{ width: "100%", borderRadius: 8 }} />
            <Field label="Co z tego obrazu jest istotne dla kolejnych assetów?">
              {textArea(referenceNotes, setReferenceNotes, 3)}
            </Field>
            <label className="field"><input type="checkbox" checked={referenceApproved}
              onChange={(event) => setReferenceApproved(event.target.checked)} />
              Akceptuję kompozycję. Obiekty będą generowane osobno, a nie wycinane z tego obrazu.
            </label>
          </>}
        </div>}
        <div className="button-row">
          <Button onClick={generateManifest}
            disabled={!scene || (referenceMode && (!referenceId || !referenceApproved))}>
            {referenceMode ? "AI Vision: rozpoznaj obiekty ze szkicu" : "AI: przygotuj listę obiektów"}
          </Button>
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
          Gdy skonfigurujesz klucz OpenAI Images w Połączeniach, możesz po
          zatwierdzeniu szkicu osobno wygenerować każdy PNG z prawdziwym kanałem
          alpha. Wygenerowany obraz trafia do biblioteki jako niezatwierdzony
          wariant; obejrzyj go i samodzielnie przypisz do wycinka. Bez usługi API
          nadal możesz skopiować prompty i ręcznie wgrać obrazy.
        </p>
        <div className="button-row">
          <Button onClick={saveManifest} disabled={!scene || !manifest.objects.length}>Zapisz listę obiektów</Button>
          <Button onClick={getPrompts} disabled={!scene || !manifest.objects.length}>Prompty dla każdego PNG</Button>
          <Button onClick={() => saveText("paper-theatre-manifest.json", JSON.stringify(effectiveManifest(), null, 2), "application/json")}>
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
            step={.01} onCommit={(v) => { setGap(v); setEntranceDirty(true); }} />
          <NumberField label="Przerwa między grupami (s)" value={groupGap} min={0} max={5}
            step={.01} onCommit={(v) => { setGroupGap(v); setEntranceDirty(true); }} />
          <NumberField label="Obrys głównej postaci (px)" value={heroOutline} min={1} max={24}
            step={1} onCommit={(v) => { setHeroOutline(v); setEntranceDirty(true); }} />
        </div>
        <p><strong>{ready}/{manifest.objects.length}</strong> obiektów powiązanych z grafikami. Brakuje: {missing}.</p>
        <Button primary onClick={assemble} disabled={!scene || !background || !!missing || !manifest.objects.length}>
          Złóż układ i pokaż porównanie
        </Button>
        <p className="small muted">Ten krok przygotowuje klatkę do oceny. Montaż i MP4 wymagają osobnej akceptacji autora w etapie Scenograf.</p>
      </section>
      <section className="surface tool-panel">
        <PaperTheatreLive source={liveSource} status={liveHint} />
        {draftSource && savedSource && <div className="button-row" style={{ marginTop: -8, marginBottom: 12 }}>
          <Button primary={!liveSaved} onClick={() => setLiveSaved(false)}>Bieżące zmiany</Button>
          <Button primary={liveSaved} onClick={() => setLiveSaved(true)}>Zapisane ujęcie (z dokładną klatką)</Button>
        </div>}
        <h2>Położenie i skala pojedynczych obiektów</h2>
        <h2>Mapa kompozycji i obiektów</h2>
        <div style={{ position: "relative", aspectRatio: "16 / 9", overflow: "hidden",
                      border: "1px solid var(--border, #777)", borderRadius: 8,
                      background: "#c8b69c" }}>
          {(background || (referenceMode && referenceId)) && <img src={mediaUrl(project.id, background || referenceId)} alt={background ? "Tło" : "Draft referencyjny (tylko podgląd)"}
            style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />}
          {[...manifest.objects].filter((obj) => obj.asset_id)
            .sort((a, b) => a.z - b.z)
            .map((obj) => (
              <PaperCutoutPreview key={obj.id} src={mediaUrl(project.id, obj.asset_id)}
                alt={obj.name} title={obj.name + " · przeciągnij, aby ustawić pozycję"}
                role="button" tabIndex={0}
                aria-label={obj.name + " · położenie; strzałki przesuwają wycinek"}
                onClick={() => setSelectedObjectId(obj.id)}
                onPointerDown={(event) => {
                  event.preventDefault();
                  setSelectedObjectId(obj.id);
                  const rect = event.currentTarget.parentElement?.getBoundingClientRect();
                  if (rect) dragOffsetRef.current = {
                    id: obj.id,
                    x: (event.clientX - rect.left) / rect.width - obj.x,
                    y: (event.clientY - rect.top) / rect.height - obj.y,
                  };
                  event.currentTarget.setPointerCapture(event.pointerId);
                  placeFromPointer(obj, event);
                }}
                onPointerMove={(event) => {
                  if (event.currentTarget.hasPointerCapture(event.pointerId))
                    placeFromPointer(obj, event);
                }}
                onPointerUp={(event) => {
                  dragOffsetRef.current = null;
                  if (event.currentTarget.hasPointerCapture(event.pointerId))
                    event.currentTarget.releasePointerCapture(event.pointerId);
                }}
                onPointerCancel={(event) => {
                  dragOffsetRef.current = null;
                  if (event.currentTarget.hasPointerCapture(event.pointerId))
                    event.currentTarget.releasePointerCapture(event.pointerId);
                }}
                onKeyDown={(event) => {
                  const delta = event.shiftKey ? .05 : .01;
                  const movement: Record<string, [number, number]> = {
                    ArrowLeft: [-delta, 0], ArrowRight: [delta, 0],
                    ArrowUp: [0, -delta], ArrowDown: [0, delta],
                  };
                  const move = movement[event.key];
                  if (move) {
                    event.preventDefault();
                    setSelectedObjectId(obj.id);
                    modify(obj.id, {
                      x: Math.min(1, Math.max(0, obj.x + move[0])),
                      y: Math.min(1, Math.max(0, obj.y + move[1])),
                    });
                  }
                }}
                style={{ position: "absolute", left: `${obj.x * 100}%`,
                  bottom: `${(1 - obj.y) * 100}%`, width: `${obj.width * 100}%`,
                  height: "auto", transform: "translateX(-50%)",
                  objectFit: "contain", touchAction: "none", cursor: "grab",
                  outline: selectedObjectId === obj.id ? "2px solid #d9b44a" : "none" }} />
            ))}
        </div>
        <p className="small muted">
          {referenceMode && !background ? "Pod spodem jest wyłącznie szkic poglądowy. Przed montażem wybierz osobne czyste tło. " : ""}
          Przeciągnij pojedynczy PNG, aby przesunąć go po scenie (lub użyj strzałek na klawiaturze;
          Shift oznacza większy krok). Edytor przycina PNG do tego samego obrysu alfa co renderer. Cienie, obrysy i mechaniki wejść oceniaj w rzeczywistej klatce powyżej.
        </p>
        {referenceMode && referenceId && referenceApproved && missingWithNoVariant.length > 1 &&
          <div className="surface" style={{ padding: 12, marginBottom: 12 }}>
            <Button primary disabled={!!batchJobId || !!cutoutJobId} onClick={generateBatch}>
              {batchJobId ? "Generowanie serii PNG…" :
                `Generuj serię do 12 brakujących PNG (${Math.min(12, missingWithNoVariant.length)})`}
            </Button>
            <p className="small muted">
              Przed wywołaniem potwierdzisz łączny koszt. Otrzymasz niezależne
              warianty do ręcznego wyboru; już wygenerowane pliki nie są ponownie naliczane.
            </p>
          </div>}
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
                  {referenceMode && !obj.asset_id && referenceId && referenceApproved &&
                    <Button disabled={!!cutoutJobId || !!batchJobId}
                      onClick={() => generateCutout(obj, !!candidateFor(obj))}>
                      {cutoutJobId && cutoutObjectId === obj.id
                        ? "Trwa generowanie tego PNG…" : candidateFor(obj)
                          ? "Wygeneruj dodatkowy wariant (płatny)"
                          : "Wygeneruj pojedynczy PNG alpha z referencji"}
                    </Button>}
                  {!obj.asset_id && candidateFor(obj) &&
                    <p className="small muted">W bibliotece jest już nowy wariant dla tego obiektu.
                      Wybierz go poniżej; dodatkowy wariant jest opcjonalny i wymaga potwierdzenia kosztu.</p>}
                  <Field label="Przypisany osobny PNG">
                    <select value={obj.asset_id} onChange={(event) => modify(obj.id, { asset_id: event.target.value })}>
                      <option value="">Czeka na grafikę</option>
                      {assets.filter((a) => a.id !== background && (!selectedIds.has(a.id) || a.id === obj.asset_id))
                        .map((asset) => <option key={asset.id} value={asset.id}>{asset.name}</option>)}
                    </select>
                  </Field>
                  {obj.asset_id && <>
                    <Button onClick={() => setMaskObjectId(maskObjectId === obj.id ? "" : obj.id)}>
                      {maskObjectId === obj.id ? "Zamknij maskę" : "Edytuj maskę PNG"}
                    </Button>
                    {maskObjectId === obj.id && <PaperCutoutMaskEditor
                      key={obj.asset_id} src={mediaUrl(project.id, obj.asset_id)}
                      onSave={(png) => saveCutoutMask(obj, png)} />}
                  </>}
                  <div className="two-fields">
                    <NumberField label="X · środek (0–1)" value={obj.x} min={0} max={1} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "x", value)} />
                    <NumberField label="Y · stopa (0–1)" value={obj.y} min={0} max={1} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "y", value)} />
                    <NumberField label="Szerokość (0,01–2)" value={obj.width} min={.01} max={2} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "width", value)} />
                    <NumberField label="Z · przesłanianie" value={obj.z} min={-100} max={100} step={1}
                      onCommit={(value) => updateObjectNumber(obj, "z", Math.round(value))} />
                    <NumberField label="Pivot X (0–1)" value={obj.pivot_x ?? .5} min={0} max={1} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "pivot_x", value)} />
                    <NumberField label="Pivot Y (0–1)" value={obj.pivot_y ?? 1} min={0} max={1} step={.01}
                      onCommit={(value) => updateObjectNumber(obj, "pivot_y", value)} />
                  </div>
                  <Field label="Indywidualna mechanika wejścia">
                    <select value={obj.rig || ""} onChange={(event) =>
                      modify(obj.id, { rig: event.target.value
                        ? event.target.value as ObjectSpec["rig"] : undefined })}>
                      <option value="">Automatyczna wg grupy</option>
                      <option value="hanging_drop">Opuszczany na nitce</option>
                      <option value="bottom_rise">Wysuwany od dołu</option>
                      <option value="rake_lift">Podnoszony na patyczku (pivot)</option>
                      <option value="static">Bez animacji wejścia</option>
                    </select>
                  </Field>
                </div>
              ))}
            </section>
          );
        })}
      </section>
    </div>
  </>);
}
