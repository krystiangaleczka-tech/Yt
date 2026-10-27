import { useEffect, useMemo, useState } from "react";
import { Player } from "@remotion/player";
import {
  Plus,
  Film,
  Save,
  ArrowRight,
  BarChart3,
  Images,
  Quote,
  Heading1,
  Image as ImageIcon,
  Trash2,
  Copy,
  Sparkles,
  RefreshCw,
  Download,
} from "lucide-react";
import { useStudio } from "./context";
import { api, id, mediaUrl } from "./api";
import { Button, Empty, Field, Modal, SectionHead } from "./components";
import type { Job, Project } from "./types";
import { fps, totalFrames } from "./timing";
import { MotionScene } from "./motion/MotionScene";
import { makeInsert, templateNames } from "./motion/types";
import type { MotionInsert, Template } from "./motion/types";

const templates: { id: Template; description: string; icon: typeof Film }[] = [
  { id: "photo", description: "Ruch, kadr i kolor", icon: ImageIcon },
  { id: "compare", description: "Dwa kadry, jedna historia", icon: Images },
  { id: "chart", description: "Liczby w ruchu", icon: BarChart3 },
  { id: "quote", description: "Słowa ze źródłem", icon: Quote },
  { id: "chapter", description: "Oddech między scenami", icon: Heading1 },
];
export function editable(item: MotionInsert): string {
  const { rendered_asset_id: _asset, rendered_signature: _sig, ...data } = item;
  return JSON.stringify(data);
}
export default function MotionEditor() {
  const s = useStudio(),
    p = s.project!;
  const [selected, setSelected] = useState(
    s.targetInsert || p.inserts?.[0]?.id || "",
  );
  useEffect(() => {
    if (s.targetInsert) setSelected(s.targetInsert);
  }, [s.targetInsert]);
  const active = p.inserts?.find((i) => i.id === selected);
  async function add(template: Template, copy?: MotionInsert) {
    const insert = copy
      ? {
          ...copy,
          id: id("insert_"),
          title: (copy.title + " · kopia").slice(0, 90),
          rendered_asset_id: null,
          rendered_signature: "",
        }
      : makeInsert(id("insert_"), template, Math.round(fps(p) * 6));
    await s.mutate((current) =>
      api<Project>(`/projects/${current.id}/inserts`, {
        expected_revision: current.revision,
        insert,
      }),
    );
    setSelected(insert.id);
    s.setTargetInsert(null);
  }
  return (
    <div className="page-content motion-page">
      <SectionHead
        eyebrow="RUCH I OPOWIEŚĆ"
        title="Wstawki animowane"
        description="Krótkie formy, które wyjaśniają więcej. Edytuj, obejrzyj i dodaj do filmu."
      >
        <span className="badge quiet">REMOTION</span>
        <Button icon={ArrowRight} onClick={() => s.setPage("editing")}>
          Przejdź do montażu
        </Button>
      </SectionHead>
      <div className="motion-templates" aria-label="Szablony wstawek">
        {templates.map((t) => (
          <button
            key={t.id}
            className={`motion-template ${active?.template === t.id ? "chosen" : ""}`}
            onClick={() => s.run(() => add(t.id))}
          >
            <div className={`motion-template-art art-${t.id}`}>
              <t.icon size={30} />
              <span />
              <span />
            </div>
            <strong>{templateNames[t.id]}</strong>
            <small>{t.description}</small>
            <Plus size={14} />
          </button>
        ))}
      </div>
      <div className="motion-workspace">
        <aside className="motion-list surface">
          <div className="panel-heading">
            <h2>Moje wstawki</h2>
            <span className="badge quiet">{p.inserts?.length || 0}</span>
          </div>
          {!p.inserts?.length && (
            <p className="motion-help">
              Wybierz szablon powyżej, żeby stworzyć pierwszą wstawkę.
            </p>
          )}
          {p.inserts?.map((i, n) => (
            <button
              className={`motion-list-item ${i.id === selected ? "active" : ""}`}
              key={i.id}
              onClick={() => {
                setSelected(i.id);
                s.setTargetInsert(null);
              }}
            >
              <span className="motion-number">
                {String(n + 1).padStart(2, "0")}
              </span>
              <span>
                <strong>{i.title}</strong>
                <small>
                  {templateNames[i.template]} ·{" "}
                  {(i.duration / fps(p)).toFixed(1)} s
                </small>
              </span>
              <span
                className={`motion-dot ${i.rendered_asset_id ? "ready" : ""}`}
                title={
                  i.rendered_asset_id
                    ? "Ma render — aktualność sprawdzana przy dodaniu do montażu"
                    : "Czeka na render"
                }
              />
            </button>
          ))}
          <div className="motion-help">
            <strong>Twoje materiały</strong>
            <p>
              Zdjęcia wybierzesz z biblioteki filmu. Dane wykresu i cytaty
              wprowadzasz samodzielnie.
            </p>
            <Button subtle onClick={() => s.setPage("library")}>
              Otwórz bibliotekę
            </Button>
          </div>
        </aside>
        {active ? (
          <InsertEditor
            key={active.id}
            item={active}
            onCopy={() => s.run(() => add(active.template, active))}
            onDelete={() =>
              s.run(async () => {
                await s.mutate((current) =>
                  api<Project>(
                    `/projects/${current.id}/inserts/${active.id}/delete`,
                    { expected_revision: current.revision },
                  ),
                );
                setSelected("");
              })
            }
          />
        ) : (
          <Empty title="Zacznij od jednej dobrej wstawki">
            Wybierz szablon u góry albo zapisaną wstawkę z listy.
          </Empty>
        )}
      </div>
    </div>
  );
}
function InsertEditor({
  item,
  onCopy,
  onDelete,
}: {
  item: MotionInsert;
  onCopy: () => void;
  onDelete: () => void;
}) {
  const s = useStudio(),
    p = s.project!;
  const [draft, setDraft] = useState(item),
    [original, setOriginal] = useState(editable(item)),
    [busy, setBusy] = useState(false),
    [start, setStart] = useState(totalFrames(p) / fps(p)),
    [ai, setAi] = useState(false),
    [aiRevision, setAiRevision] = useState<number | null>(null),
    [deleteOpen, setDeleteOpen] = useState(false),
    [status, setStatus] = useState<{ installed: boolean } | null>(null);
  const dirty = editable(draft) !== original;
  useEffect(() => {
    s.run(async () => setStatus(await api("/motion/status")));
  }, []);
  useEffect(() => {
    if (!dirty) {
      setDraft(item);
      setOriginal(editable(item));
    }
  }, [item]);
  const imageUrls = useMemo(
    () => draft.image_ids.map((asset) => mediaUrl(p.id, asset)),
    [p.id, draft.image_ids],
  );
  const activeJobs = s.jobs.filter(
    (j) =>
      j.kind === "motion" &&
      j.project_id === p.id &&
      ["QUEUED", "RUNNING", "CANCEL_REQUESTED"].includes(j.status),
  );
  const latestMotion = s.jobs.find(
    (j) => j.kind === "motion" && j.project_id === p.id,
  );
  const lastFailure =
    latestMotion && ["FAILED", "INTERRUPTED"].includes(latestMotion.status)
      ? latestMotion
      : null;
  const images = p.assets.filter((a) => a.kind === "image");
  const rendered = p.assets.find((a) => a.id === item.rendered_asset_id);
  const change = (changes: Partial<MotionInsert>) =>
    setDraft((d) => ({ ...d, ...changes }));
  async function save() {
    const next = await s.mutate((current) => {
      if (aiRevision !== null && current.revision !== aiRevision)
        throw new Error(
          "Projekt zmienił się od propozycji AI. Przygotuj aktualną propozycję.",
        );
      const currentItem = current.inserts.find((i) => i.id === item.id);
      if (!currentItem || editable(currentItem) !== original)
        throw new Error(
          "Wstawka zmieniła się w innym oknie. Wczytaj zapisaną wersję przed edycją.",
        );
      return api<Project>(`/projects/${current.id}/inserts`, {
        expected_revision: current.revision,
        insert: draft,
      });
    });
    const saved = next.inserts.find((i) => i.id === item.id)!;
    setDraft(saved);
    setOriginal(editable(saved));
    setAiRevision(null);
    return next;
  }
  async function render() {
    setBusy(true);
    try {
      const next = dirty ? await save() : p;
      await api<Job>(`/projects/${p.id}/inserts/${item.id}/render`, {
        expected_revision: next.revision,
      });
      s.notify("Wstawka trafiła do kolejki. Po renderze dodaj ją do montażu.");
    } finally {
      setBusy(false);
    }
  }
  async function addTimeline() {
    await s.mutate((current) =>
      api<Project>(`/projects/${current.id}/inserts/${item.id}/to-timeline`, {
        expected_revision: current.revision,
        start: Math.round(start * fps(current)),
      }),
    );
    s.notify("Dodano wstawkę do montażu");
    s.setPage("editing");
  }
  const number = (
    label: string,
    key: "zoom" | "pan" | "rotation" | "brightness" | "saturation" | "blur",
    min: number,
    max: number,
    step: number,
  ) => (
    <Field label={label}>
      <div className="motion-range">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={draft[key]}
          onChange={(e) => change({ [key]: Number(e.target.value) })}
        />
        <output>{draft[key].toFixed(step < 1 ? 2 : 0)}</output>
      </div>
    </Field>
  );
  return (
    <section className="motion-editor">
      <div className="motion-preview surface">
        <div className="panel-heading">
          <h2>Podgląd na żywo</h2>
          <span className="badge quiet">
            {dirty ? "Niezapisane zmiany" : "Zapisano"}
          </span>
        </div>
        <div className="motion-player">
          <Player
            key={`${draft.id}-${p.sequence.width}-${p.sequence.height}-${draft.duration}`}
            component={MotionScene}
            inputProps={{ insert: draft, imageUrls }}
            durationInFrames={draft.duration}
            fps={fps(p)}
            compositionWidth={p.sequence.width}
            compositionHeight={p.sequence.height}
            controls
            loop
            style={{ width: "100%" }}
            acknowledgeRemotionLicense
          />
        </div>
        <div className="motion-preview-foot">
          <span>
            {p.sequence.width} × {p.sequence.height} ·{" "}
            {(draft.duration / fps(p)).toFixed(1)} s · {fps(p).toFixed(2)} FPS
          </span>
          <span>Ten sam szablon w podglądzie i eksporcie</span>
        </div>
      </div>
      <div className="motion-form surface">
        <div className="panel-heading">
          <h2>{templateNames[draft.template]}</h2>
          <div className="motion-actions">
            <Button subtle icon={Copy} onClick={onCopy} disabled={dirty}>
              Kopia
            </Button>
            <Button
              subtle
              icon={Trash2}
              onClick={() => setDeleteOpen(true)}
              aria-label="Usuń wstawkę"
            />
          </div>
        </div>
        <div className="motion-fields">
          <Field label="Tytuł">
            <input
              maxLength={90}
              value={draft.title}
              onChange={(e) => change({ title: e.target.value })}
            />
          </Field>
          <Field
            label={draft.template === "quote" ? "Autor / podpis" : "Podtytuł"}
          >
            <input
              maxLength={180}
              value={draft.subtitle}
              onChange={(e) => change({ subtitle: e.target.value })}
            />
          </Field>
          {(draft.template === "quote" || draft.template === "chapter") && (
            <Field
              label={
                draft.template === "quote"
                  ? "Treść cytatu"
                  : "Etykieta rozdziału"
              }
            >
              <textarea
                rows={3}
                maxLength={draft.template === "chapter" ? 60 : 240}
                value={draft.text}
                onChange={(e) => change({ text: e.target.value })}
              />
            </Field>
          )}
          {(draft.template === "photo" || draft.template === "compare") && (
            <>
              <div className="motion-image-fields">
                {Array.from(
                  { length: draft.template === "compare" ? 2 : 1 },
                  (_, n) => (
                    <div key={n}>
                      <Field label={`Zdjęcie ${n + 1}`}>
                        <select
                          value={draft.image_ids[n] || ""}
                          disabled={n === 1 && !draft.image_ids[0]}
                          onChange={(e) => {
                            const ids = [...draft.image_ids];
                            ids[n] = e.target.value;
                            change({ image_ids: ids });
                          }}
                        >
                          <option value="" disabled>
                            Wybierz z biblioteki
                          </option>
                          {images.map((a) => (
                            <option key={a.id} value={a.id}>
                              {a.name}
                            </option>
                          ))}
                        </select>
                      </Field>
                      {draft.template === "compare" && (
                        <Field label={`Podpis ${n + 1}`}>
                          <input
                            maxLength={40}
                            value={draft.labels[n]}
                            onChange={(e) => {
                              const labels = [...draft.labels];
                              labels[n] = e.target.value;
                              change({ labels });
                            }}
                          />
                        </Field>
                      )}
                    </div>
                  ),
                )}
              </div>
              {!images.length && (
                <p className="motion-note">
                  Dodaj zdjęcia w Bibliotece lub Centrum źródeł, następnie wróć
                  do wstawki.
                </p>
              )}
              <div className="motion-sliders">
                {number("Przybliżenie", "zoom", 1, 1.5, 0.01)}
                {number("Przesunięcie (%)", "pan", -15, 15, 1)}
                {number("Obrót (°)", "rotation", -10, 10, 0.5)}
                {number("Jasność", "brightness", 0.5, 1.5, 0.05)}
                {number("Nasycenie", "saturation", 0, 2, 0.05)}
                {number("Rozmycie", "blur", 0, 12, 0.5)}
              </div>
            </>
          )}
          {draft.template === "chart" && (
            <div className="motion-data">
              <div className="motion-data-head">
                <strong>Dane wykresu</strong>
                <Button
                  subtle
                  icon={Plus}
                  disabled={draft.data.length >= 8}
                  onClick={() =>
                    change({
                      data: [...draft.data, { label: "Nowa", value: 0 }],
                    })
                  }
                >
                  Dodaj
                </Button>
              </div>
              {draft.data.map((row, n) => (
                <div className="motion-data-row" key={n}>
                  <input
                    aria-label={`Etykieta ${n + 1}`}
                    maxLength={24}
                    value={row.label}
                    onChange={(e) =>
                      change({
                        data: draft.data.map((d, x) =>
                          x === n ? { ...d, label: e.target.value } : d,
                        ),
                      })
                    }
                  />
                  <input
                    aria-label={`Wartość ${n + 1}`}
                    type="number"
                    min={0}
                    max={1e12}
                    value={row.value}
                    onChange={(e) =>
                      change({
                        data: draft.data.map((d, x) =>
                          x === n ? { ...d, value: Number(e.target.value) } : d,
                        ),
                      })
                    }
                  />
                  <Button
                    subtle
                    icon={Trash2}
                    aria-label={`Usuń wartość ${n + 1}`}
                    disabled={draft.data.length <= 1}
                    onClick={() =>
                      change({ data: draft.data.filter((_, x) => x !== n) })
                    }
                  />
                </div>
              ))}
              <Field label="Jednostka">
                <input
                  maxLength={16}
                  value={draft.unit}
                  placeholder="np. mln, %, km"
                  onChange={(e) => change({ unit: e.target.value })}
                />
              </Field>
              <p className="motion-note">
                Wartości początkowe są przykładowe. Zastąp je sprawdzonymi
                danymi i podaj źródło.
              </p>
            </div>
          )}
          <Field label="Źródło / przypis">
            <input
              maxLength={160}
              value={draft.source}
              placeholder="Autor, publikacja, rok lub adres źródła"
              onChange={(e) => change({ source: e.target.value })}
            />
          </Field>
          <div className="motion-settings-row">
            <Field label="Czas (sekundy)">
              <input
                type="number"
                min={Math.max(0.5, 15 / fps(p))}
                max={60}
                step={0.1}
                value={Number((draft.duration / fps(p)).toFixed(2))}
                onChange={(e) =>
                  change({
                    duration: Math.max(
                      15,
                      Math.min(
                        7200,
                        Math.round(
                          Math.min(60, Math.max(0.5, Number(e.target.value))) *
                            fps(p),
                        ),
                      ),
                    ),
                  })
                }
              />
            </Field>
            <Field label="Akcent">
              <input
                type="color"
                value={draft.accent}
                onChange={(e) => change({ accent: e.target.value })}
              />
            </Field>
            <Field label="Tło">
              <input
                type="color"
                value={draft.background}
                onChange={(e) => change({ background: e.target.value })}
              />
            </Field>
          </div>
        </div>
        <div className="motion-save-bar">
          <Button
            icon={RefreshCw}
            disabled={!dirty}
            onClick={() => {
              setDraft(item);
              setOriginal(editable(item));
              setAiRevision(null);
            }}
          >
            Wczytaj zapisaną
          </Button>
          <Button icon={Sparkles} disabled={dirty} onClick={() => setAi(true)}>
            Zmień z AI
          </Button>
          <Button
            icon={Save}
            disabled={!dirty || s.saving}
            onClick={() => s.run(save)}
          >
            Zapisz
          </Button>
          <Button
            primary
            icon={Film}
            busy={busy}
            disabled={
              !draft.title.trim() || activeJobs.length > 0 || !status?.installed
            }
            onClick={() => s.run(render)}
          >
            Renderuj klip
          </Button>
        </div>
      </div>
      {!status?.installed && status && (
        <p className="motion-note">
          Moduł renderowania wymaga instalacji zależności aplikacji. Instrukcja:
          docs/STUDIO.md → Wstawki Remotion.
        </p>
      )}
      {activeJobs.map((j) => (
        <div className="motion-job surface" key={j.id}>
          <span className="status-dot" />
          <div>
            <strong>{j.message}</strong>
            <progress max={1} value={j.progress} />
          </div>
          <Button
            subtle
            onClick={() =>
              s.run(async () => {
                await api(`/jobs/${j.id}/cancel`, {});
              })
            }
          >
            Anuluj
          </Button>
        </div>
      ))}
      {lastFailure && (
        <div className="motion-job surface" role="status">
          <div>
            <strong>Ostatni render wstawek wymaga ponowienia</strong>
            <p className="motion-note">{lastFailure.message}</p>
          </div>
          <Button onClick={() => s.setPage("jobs")}>Zadania</Button>
        </div>
      )}
      <div className="motion-handoff surface">
        <div>
          <h3>
            {rendered ? "Render gotowy" : "Gotowa wstawka trafi do montażu"}
          </h3>
          <p>
            {dirty
              ? "Zapisz zmiany i wyrenderuj nową wersję."
              : "Dodanie tworzy nowy klip. Dotychczasowy montaż zachowuje wybrane wersje."}
          </p>
          {rendered && (
            <a href={mediaUrl(p.id, rendered.id)} download>
              <Download size={14} /> Pobierz ostatni render MP4
            </a>
          )}
        </div>
        <Field label="Początek na osi (s)">
          <input
            type="number"
            min={0}
            max={21540}
            step={0.1}
            value={start}
            onChange={(e) => setStart(Number(e.target.value))}
          />
        </Field>
        <Button
          primary
          icon={ArrowRight}
          disabled={!rendered || dirty || s.saving}
          onClick={() => s.run(addTimeline)}
        >
          Dodaj do montażu
        </Button>
      </div>
      <Modal
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        title="Usunąć edytowalną wstawkę?"
        description="Jej wyrenderowane klipy pozostaną w bibliotece i montażu."
      >
        <Button onClick={() => setDeleteOpen(false)}>Zachowaj</Button>
        <Button primary onClick={onDelete}>
          Usuń wstawkę
        </Button>
      </Modal>
      <InsertAssistant
        open={ai}
        close={() => setAi(false)}
        item={item}
        accept={(candidate, revision) => {
          setDraft(candidate);
          setAiRevision(revision);
          setAi(false);
          s.notify("Propozycja jest w podglądzie. Sprawdź ją i zapisz.");
        }}
      />
    </section>
  );
}
function InsertAssistant({
  open,
  close,
  item,
  accept,
}: {
  open: boolean;
  close: () => void;
  item: MotionInsert;
  accept: (i: MotionInsert, revision: number) => void;
}) {
  const s = useStudio(),
    p = s.project!;
  const [command, setCommand] = useState(""),
    [response, setResponse] = useState(""),
    [prompt, setPrompt] = useState(""),
    [baseRevision, setBaseRevision] = useState(p.revision),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    if (open) {
      setBaseRevision(p.revision);
      setPrompt("");
      setResponse("");
    }
  }, [open]);
  async function ask(action: "generate" | "import" | "prompt") {
    setBusy(true);
    try {
      const result = await api<{
        insert: MotionInsert;
        base_revision: number;
        prompt: string;
      }>(`/projects/${p.id}/inserts/${item.id}/assistant/${action}`, {
        command,
        response,
        base_revision: baseRevision,
      });
      if (action === "prompt") {
        setPrompt(result.prompt);
        setBaseRevision(result.base_revision);
      } else {
        if (result.base_revision !== p.revision)
          throw new Error("Projekt zmienił się. Otwórz asystenta ponownie.");
        accept(result.insert, result.base_revision);
      }
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal
      open={open}
      onClose={close}
      title="Zmień wstawkę z AI"
      description="AI proponuje ustawienia szablonu. Przed zapisem obejrzysz wynik w podglądzie."
    >
      <Field label="Co zmienić?">
        <textarea
          rows={3}
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Np. Zbliżenie 1,25, delikatnie w lewo, sześć sekund, chłodniejsze tło."
        />
      </Field>
      <div className="motion-actions">
        <Button
          primary
          icon={Sparkles}
          busy={busy}
          disabled={!command.trim() || !s.health?.ai}
          onClick={() => s.run(() => ask("generate"))}
        >
          Zaproponuj zmianę
        </Button>
        <Button
          disabled={!command.trim() || busy}
          onClick={() => s.run(() => ask("prompt"))}
        >
          Przygotuj prompt
        </Button>
      </div>
      {!s.health?.ai && (
        <p className="motion-note">
          Podłącz model w Ustawieniach albo użyj promptu w swoim czacie i wklej
          odpowiedź JSON.
        </p>
      )}
      {prompt && (
        <Field label="Prompt do skopiowania">
          <textarea
            rows={5}
            readOnly
            value={prompt}
            onFocus={(e) => e.target.select()}
          />
        </Field>
      )}
      <Field label="Odpowiedź JSON z zewnętrznego czatu">
        <textarea
          rows={4}
          value={response}
          onChange={(e) => setResponse(e.target.value)}
        />
      </Field>
      <Button
        disabled={!response.trim() || busy}
        onClick={() => s.run(() => ask("import"))}
      >
        Sprawdź i pokaż propozycję
      </Button>
    </Modal>
  );
}
