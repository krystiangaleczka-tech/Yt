import { useEffect, useState } from "react";
import { BookOpen, Check, Library, Plus, ArrowRight, Copy } from "lucide-react";
import { useStudio } from "./context";
import { modeLabels } from "./animationTypes";
import type { ProductionMode } from "./animationTypes";
import { api, safeUrl } from "./api";
import { Button, Empty, Field, Modal } from "./components";
import type { Project, Fact, Source, Asset } from "./types";
import type {
  BankResource,
  Preset,
  ResourceKind,
  ResourceLink,
  WorkspaceData,
} from "./workspaceTypes";
import { kindLabels, presetLabels } from "./workspaceTypes";
import type { Chapter } from "./developmentTypes";

export const emptyData: WorkspaceData = {
  categories: [],
  resources: [],
  channels: [],
  defaults: { revision: 0, preset: {} },
};
export const textField = (
  label: string,
  value: string,
  change: (v: string) => void,
  rows = 0,
) => (
  <Field label={label}>
    {rows ? (
      <textarea
        rows={rows}
        value={value}
        onChange={(e) => change(e.target.value)}
      />
    ) : (
      <input value={value} onChange={(e) => change(e.target.value)} />
    )}
  </Field>
);
export const kindsFor = (section: string): ResourceKind[] =>
  section === "bank-media"
    ? ["media"]
    : section === "templates"
      ? ["template"]
      : section === "idea-pool"
        ? ["idea"]
        : ["fact", "source", "note", "baseline"];
export function useWorkspace() {
  const s = useStudio();
  const [data, setData] = useState<WorkspaceData>(emptyData);
  async function refresh() {
    setData(await api<WorkspaceData>("/workspace"));
  }
  useEffect(() => {
    s.run(refresh);
  }, []);
  return { data, refresh };
}

export function PresetFields({
  value,
  change,
}: {
  value: Preset;
  change: (v: Preset) => void;
}) {
  const s = useStudio();
  const [voices, setVoices] = useState<Record<string, any>[]>([]);
  useEffect(() => {
    s.run(async () => setVoices(await api("/voices")));
  }, []);
  const update = (key: keyof Preset, v: unknown) => {
    const next = { ...value };
    if (v === undefined) delete next[key];
    else Object.assign(next, { [key]: v });
    change(next);
  };
  return (
    <div className="workspace-profile-fields">
      <p className="small muted">
        Puste pola pozostawiają ustawienia z wcześniejszego poziomu. Film
        zachowa migawkę wybranego profilu.
      </p>
      <div className="two-fields">
        <Field label="Język domyślny">
          <select
            value={value.language || ""}
            onChange={(e) => update("language", e.target.value || undefined)}
          >
            <option value="">Dziedzicz</option>
            <option value="pl">Polski</option>
            <option value="en">English</option>
          </select>
        </Field>
        <Field label="Docelowa długość (min)">
          <input
            type="number"
            min={1}
            max={360}
            value={value.target_minutes ?? ""}
            onChange={(e) =>
              update(
                "target_minutes",
                e.target.value ? Number(e.target.value) : undefined,
              )
            }
          />
        </Field>
      </div>
      {textField(
        "Widz i jego potrzeby",
        value.audience || "",
        (v) => update("audience", v || undefined),
        2,
      )}
      {textField(
        "Zasady narracji",
        value.narrative_style || "",
        (v) => update("narrative_style", v || undefined),
        3,
      )}
      {textField(
        "Styl obrazu",
        value.visual_style || "",
        (v) => update("visual_style", v || undefined),
        2,
      )}
      {textField(
        "Referencje",
        value.references || "",
        (v) => update("references", v || undefined),
        2,
      )}
      {textField(
        "Ograniczenia i zasady researchu",
        value.constraints || "",
        (v) => update("constraints", v || undefined),
        3,
      )}
      <div className="two-fields">
        <Field label="Font w filmie">
          <select
            value={value.font || ""}
            onChange={(e) => update("font", e.target.value || undefined)}
          >
            <option value="">Dziedzicz</option>
            <option value="montserrat">Montserrat</option>
            <option value="courier">Courier Prime</option>
            <option value="courier-bold">Courier Prime Bold</option>
          </select>
        </Field>
        <Field label="Kolor akcentu">
          <input
            value={value.color || ""}
            placeholder="#b6baf0 — opcjonalnie"
            onChange={(e) => update("color", e.target.value || undefined)}
          />
        </Field>
      </div>
      <Field label="Prywatny profil głosu">
        <select
          value={value.voice_id || ""}
          onChange={(e) => update("voice_id", e.target.value || undefined)}
        >
          <option value="">Dziedzicz / wybierz później</option>
          {voices.map((v) => (
            <option key={v.id} value={v.id}>
              {v.name}
            </option>
          ))}
        </select>
      </Field>
      <details className="advanced">
        <summary>Format obrazu i miks</summary>
        <div className="two-fields">
          {(["width", "height", "fps_num", "fps_den"] as const).map((k, i) => (
            <Field
              key={k}
              label={
                ["Szerokość", "Wysokość", "FPS — licznik", "FPS — mianownik"][i]
              }
            >
              <input
                type="number"
                value={value[k] ?? ""}
                onChange={(e) =>
                  update(k, e.target.value ? Number(e.target.value) : undefined)
                }
              />
            </Field>
          ))}
        </div>
        <Field label="Ściszanie muzyki pod lektorem">
          <select
            value={value.ducking === undefined ? "" : String(value.ducking)}
            onChange={(e) =>
              update(
                "ducking",
                e.target.value === "" ? undefined : e.target.value === "true",
              )
            }
          >
            <option value="">Dziedzicz</option>
            <option value="true">Włączone</option>
            <option value="false">Wyłączone</option>
          </select>
        </Field>
      </details>
    </div>
  );
}

export function NewFilmModal({
  open,
  close,
  onCreated,
}: {
  open: boolean;
  close: () => void;
  onCreated: (p: Project) => Promise<void>;
}) {
  const s = useStudio();
  const [data, setData] = useState(emptyData),
    [title, setTitle] = useState(""),
    [channel, setChannel] = useState(""),
    [category, setCategory] = useState(""),
    [template, setTemplate] = useState(""),
    [language, setLanguage] = useState(""),
    [format, setFormat] = useState(""),
    [mode, setMode] = useState<ProductionMode>(s.mode),
    [preview, setPreview] = useState<{
      preset: Preset;
      chapters: number;
    } | null>(null),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!open) return;
    setMode(s.mode);
    s.run(async () => {
      const value = await api<typeof data>("/workspace");
      setData(value);
      const matching = value.channels.find(
        (c) => (c.production_mode || "documentary") === s.mode,
      );
      if (matching && !channel) setChannel(matching.id);
    });
  }, [open]);
  useEffect(() => {
    if (!open) return;
    let active = true;
    api<{ preset: Preset; chapters: number }>(
      `/workspace/preview?channel_id=${channel}&category_id=${category}&template_id=${template}`,
    )
      .then((v) => {
        if (active) setPreview(v);
      })
      .catch((e) => s.notify(String(e), true));
    return () => {
      active = false;
    };
  }, [open, channel, category, template]);
  return (
    <Modal
      open={open}
      onClose={close}
      title="Nowy film"
      description="Osobny projekt. Treść, fakty i materiały dobierzesz już podczas pracy nad nim."
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          s.run(async () => {
            setBusy(true);
            try {
              const p = await api<Project>("/projects", {
                title,
                channel_id: channel,
                category_id: category,
                template_id: template,
                film_format: format,
                production_mode: mode,
                ...(language ? { language } : {}),
              });
              await onCreated(p);
              setTitle("");
              setCategory("");
              setTemplate("");
              close();
            } finally {
              setBusy(false);
            }
          });
        }}
      >
        {textField("Nazwa robocza — możesz ustalić później", title, setTitle)}
        <Field
          label="Tryb produkcji"
          hint={
            mode === "animation_2d"
              ? "Film animowany korzysta z postaci i lokacji z banku wybranego kanału."
              : undefined
          }
        >
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as ProductionMode)}
          >
            {(Object.keys(modeLabels) as ProductionMode[]).map((m) => (
              <option key={m} value={m}>
                {modeLabels[m]}
              </option>
            ))}
          </select>
        </Field>
        <div className="two-fields">
          <Field label="Kanał">
            <select
              value={channel}
              onChange={(e) => {
                setChannel(e.target.value);
                setCategory("");
              }}
            >
              <option value="" disabled={mode === "animation_2d"}>
                Bez profilu kanału
              </option>
              {data.channels.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Kategoria">
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">Bez kategorii</option>
              {data.categories
                .filter((c) => !c.channel_id || c.channel_id === channel)
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
            </select>
          </Field>
        </div>
        <Field label="Szablon startowy — opcjonalnie">
          <select
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
          >
            <option value="">Pusty film</option>
            {data.resources
              .filter((r) => r.kind === "template")
              .map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title}
                </option>
              ))}
          </select>
        </Field>
        <div className="two-fields">
          <Field label="Język">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="">
                Z profilu ({preview?.preset.language || "pl"})
              </option>
              <option value="pl">Polski</option>
              <option value="en">English</option>
            </select>
          </Field>
          {textField("Format, np. śledztwo / wyjaśnienie", format, setFormat)}
        </div>
        <div className="workspace-start-summary">
          <strong>Na starcie: 0 faktów · 0 źródeł · 0 mediów</strong>
          <p>
            {preview?.chapters
              ? `${preview.chapters} rozdziałów do wypełnienia ze szablonu.`
              : "Własny brief, historia i scenariusz powstaną w tym filmie."}
          </p>
          {preview && (
            <p className="small muted">
              Długość: {preview.preset.target_minutes || 15} min ·{" "}
              {preview.preset.font || "font domyślny"}
              {preview.preset.audience
                ? ` · Widz: ${preview.preset.audience}`
                : ""}
            </p>
          )}
        </div>
        <Button primary icon={ArrowRight} type="submit" busy={busy}>
          Utwórz film i przejdź do pomysłu
        </Button>
      </form>
    </Modal>
  );
}

export function PublishToBank({
  kind,
  itemId,
  title,
  label = "Dodaj do banku",
}: {
  kind: ResourceKind;
  itemId: string;
  title: string;
  label?: string;
}) {
  const s = useStudio();
  const [open, setOpen] = useState(false),
    [data, setData] = useState(emptyData),
    [name, setName] = useState(title),
    [scope, setScope] = useState<"workspace" | "channel" | "category">(
      "workspace",
    ),
    [category, setCategory] = useState(""),
    [context, setContext] = useState(""),
    [tags, setTags] = useState("");
  useEffect(() => {
    if (open) {
      setName(title);
      setCategory(s.project?.category_id || "");
      s.run(async () => setData(await api("/workspace")));
    }
  }, [open]);
  return (
    <>
      <Button subtle icon={Copy} onClick={() => setOpen(true)}>
        {label}
      </Button>
      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={
          kind === "template"
            ? "Zapisz układ jako szablon"
            : "Udostępnij zasób w pracowni"
        }
        description={
          kind === "template"
            ? "Zachowamy liczbę części, czas i energię. Konkretne tytuły, fabuła, fakty i oceny nie trafią do szablonu. Po zapisie nadaj częściom uniwersalne nazwy w Szablonach."
            : "Film zachowa swoją treść. Do banku trafi osobny wpis z potrzebnymi źródłami i plikami."
        }
      >
        {textField("Nazwa wpisu", name, setName)}
        <Field label="Zakres">
          <select
            value={scope}
            onChange={(e) => setScope(e.target.value as typeof scope)}
          >
            <option value="workspace">Cała pracownia</option>
            <option value="channel" disabled={!s.project?.channel_id}>
              Kanał tego filmu
            </option>
            <option value="category">Wybrana kategoria</option>
          </select>
        </Field>
        <Field label="Kategoria / kolekcja">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Bez kategorii</option>
            {data.categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
        {textField("Tagi — oddziel przecinkami", tags, setTags)}
        {textField(
          "Kontekst, ograniczenia i aktualność",
          context,
          setContext,
          3,
        )}
        <Button
          primary
          icon={Check}
          disabled={!name.trim() || (scope === "category" && !category)}
          onClick={() =>
            s.run(async () => {
              await s.mutate(async (p) => {
                await api(`/projects/${p.id}/workspace/publish`, {
                  expected_revision: p.revision,
                  kind,
                  item_id: itemId,
                  title: name,
                  scope,
                  channel_id: scope === "workspace" ? "" : p.channel_id,
                  category_ids: category ? [category] : [],
                  tags: tags
                    .split(",")
                    .map((t) => t.trim())
                    .filter(Boolean),
                  context,
                });
                return p;
              });
              setOpen(false);
              s.notify("Zapisano osobny wpis w banku");
            })
          }
        >
          Zapisz w banku
        </Button>
      </Modal>
    </>
  );
}

function ResourcePreview({ resource: r }: { resource: BankResource }) {
  const payload = r.payload;
  return (
    <div className="bank-preview">
      <div className="button-row">
        <span className="badge quiet">{kindLabels[r.kind]}</span>
        <span className="badge quiet">Wersja {r.revision}</span>
        <span className="badge quiet">
          {r.scope === "workspace"
            ? "Cała pracownia"
            : r.scope === "channel"
              ? "Kanał"
              : "Kategoria"}
        </span>
      </div>
      {r.context && <p>{r.context}</p>}
      {r.kind === "fact" &&
        (payload.facts as Fact[]).map((f) => (
          <blockquote key={f.id}>
            {f.claim}
            <small>
              {f.status} · {f.source} · {f.page}
            </small>
            {f.quote && <p>{f.quote}</p>}
          </blockquote>
        ))}
      {(payload.sources as Source[] | undefined)?.map((source) => (
        <section key={source.id} className="surface tool-panel">
          <strong>{source.title}</strong>
          <small>
            {source.author} · {source.edition} · {source.identifier}
          </small>
          {safeUrl(source.url) && (
            <a
              className="text-link"
              href={safeUrl(source.url)}
              target="_blank"
              rel="noreferrer"
            >
              Otwórz źródło
            </a>
          )}
          <p className="bank-excerpt">
            {source.text || "Metadane źródła; pełnego tekstu nie dodano."}
          </p>
        </section>
      ))}
      {(payload.assets as Asset[] | undefined)?.map((a) => (
        <a
          key={a.id}
          className="button"
          href={`/api/workspace/resources/${r.id}/media/${a.id}`}
          target="_blank"
          rel="noreferrer"
        >
          Otwórz materiał: {a.name}
        </a>
      ))}
      {r.kind === "note" && <p className="bank-excerpt">{payload.text}</p>}
      {r.kind === "idea" && (
        <>
          <h3>{payload.question}</h3>
          <p>{payload.angle}</p>
          <p>{payload.notes}</p>
        </>
      )}
      {r.kind === "template" && (
        <>
          <p>
            {Object.entries(payload.preset || {})
              .map(
                ([k, v]) =>
                  `${presetLabels[k] || k}: ${k === "voice_id" ? "wybrany profil" : typeof v === "object" ? "zapisany zestaw" : String(v)}`,
              )
              .join(" · ") || "Bez zmian ustawień"}
          </p>
          {(payload.chapters as Chapter[]).map((c, i) => (
            <div key={c.id}>
              <h3>
                {i + 1}. {c.title}
              </h3>
              <p>{c.purpose}</p>
              <ol>
                {c.sections.map((x) => (
                  <li key={x.id}>
                    {x.title} · {x.seconds} s · energia {x.energy}/10
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </>
      )}
      {r.kind === "baseline" && (
        <>
          <p>
            {payload.views_30d?.length || 0} porównywalnych wyników po 30 dniach
            · CTR {payload.ctr ?? "brak"}% · retencja{" "}
            {payload.retention ?? "brak"}%
          </p>
          <p>{payload.evidence}</p>
          <p className="small muted">
            To punkt odniesienia. Oceny i prognozy wariantów pozostają w filmie.
          </p>
        </>
      )}
    </div>
  );
}

export function ResourceDialog({
  resource: r,
  close,
  done,
  edit,
}: {
  resource: BankResource;
  close: () => void;
  done: () => void;
  edit?: (r: BankResource) => void;
}) {
  const s = useStudio(),
    p = s.project;
  const [settings, setSettings] = useState(false),
    [structure, setStructure] = useState(true),
    [confirmUpdate, setConfirmUpdate] = useState(false),
    [before, setBefore] = useState<BankResource | null>(null);
  const [uses, setUses] = useState<
    {
      project_id: string;
      title: string;
      published: boolean;
      archived: boolean;
    }[]
  >([]);
  useEffect(() => {
    s.run(async () => setUses(await api(`/workspace/resources/${r.id}/uses`)));
  }, [r.id]);
  const link = p?.resource_links.find((v) => v.resource_id === r.id),
    same = link?.revision === r.revision;
  useEffect(() => {
    if (link && link.revision !== r.revision)
      s.run(async () =>
        setBefore(
          await api(`/workspace/resources/${r.id}?revision=${link.revision}`),
        ),
      );
  }, [r.id, link?.revision]);
  return (
    <Modal
      open
      onClose={close}
      title={r.title}
      description="Zasób banku. Dodanie do filmu tworzy niezależną, oznaczoną wersję."
      wide
    >
      <ResourcePreview resource={r} />
      {!!uses.length && (
        <section className="surface tool-panel">
          <h3>Wykorzystanie w filmach</h3>
          {uses.map((use) => (
            <p key={use.project_id}>
              {use.title} ·{" "}
              {use.archived
                ? "archiwum"
                : use.published
                  ? "opublikowany"
                  : "w przygotowaniu"}
            </p>
          ))}
        </section>
      )}
      {before && (
        <details className="advanced">
          <summary>
            Porównaj z wersją {before.revision} zapisaną w filmie
          </summary>
          <ResourcePreview resource={before} />
        </details>
      )}
      {r.kind === "fact" && (
        <p className="workspace-start-summary">
          Po dodaniu do filmu fakt czeka na sprawdzenie zastosowania w nowym
          kontekście. Zachowamy status i datę weryfikacji z banku jako
          pochodzenie.
        </p>
      )}
      {r.kind === "template" && (
        <div className="workspace-start-summary">
          <label className="checkbox">
            <input
              type="checkbox"
              checked={structure}
              onChange={(e) => setStructure(e.target.checked)}
            />
            Dodaj strukturę jako nowy szkic pomysłu
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={settings}
              onChange={(e) => setSettings(e.target.checked)}
            />
            Zastosuj ustawienia do filmu
          </label>
          {settings && p && (
            <p className="small muted">
              Zastąpimy wyłącznie pola tego profilu:{" "}
              {Object.keys(r.payload.preset || {})
                .map((k) => presetLabels[k] || k)
                .join(", ") || "brak"}
              . Pozostałe pola zostają. Przy istniejącym montażu ustawienia
              stosuj do nowego filmu.
            </p>
          )}
        </div>
      )}
      {r.kind === "baseline" && p && (
        <p className="workspace-start-summary">
          Zastąpisz punkt odniesienia tego filmu (
          {p.development.baseline.views_30d.length} wyników) wybranym zestawem (
          {r.payload.views_30d?.length || 0}). Założenia wariantów pozostają bez
          zmian.
        </p>
      )}
      {link && !same && (
        <label className="checkbox">
          <input
            type="checkbox"
            checked={confirmUpdate}
            onChange={(e) => setConfirmUpdate(e.target.checked)}
          />
          Przyjmuję wersję {r.revision} w miejsce wersji {link.revision};
          powiązana treść wymaga ponownego przeglądu
        </label>
      )}
      <div className="button-row">
        <Button
          primary
          icon={Plus}
          disabled={
            !p ||
            same ||
            (!!link && !confirmUpdate) ||
            (r.kind === "template" && !settings && !structure)
          }
          onClick={() =>
            s.run(async () => {
              await s.mutate((current) =>
                api<Project>(
                  `/projects/${current.id}/workspace/import/${r.id}`,
                  {
                    expected_revision: current.revision,
                    resource_revision: r.revision,
                    update: !!link,
                    apply_settings: settings,
                    apply_structure: structure,
                  },
                ),
              );
              s.notify("Dodano wersję zasobu do filmu");
              done();
              close();
            })
          }
        >
          {same
            ? "Ta wersja jest już w filmie"
            : link
              ? "Zastosuj aktualizację w filmie"
              : r.kind === "baseline"
                ? "Zastąp punkt odniesienia filmu"
                : "Dodaj do wybranego filmu"}
        </Button>
        {edit && <Button onClick={() => edit(r)}>Edytuj wpis banku</Button>}
      </div>
      <p className="small muted">
        {p
          ? `Film docelowy: ${p.title}`
          : "Najpierw utwórz lub otwórz film. Bank możesz przeglądać niezależnie."}
      </p>
    </Modal>
  );
}

export function ResourceList({
  data,
  kinds,
  open,
}: {
  data: WorkspaceData;
  kinds: ResourceKind[];
  open: (id: string) => void;
}) {
  const [query, setQuery] = useState(""),
    [category, setCategory] = useState(""),
    [kind, setKind] = useState("");
  const rows = data.resources.filter(
    (r) =>
      kinds.includes(r.kind) &&
      (!kind || r.kind === kind) &&
      (!category || r.category_ids.includes(category)) &&
      `${r.title} ${r.context} ${r.tags.join(" ")}`
        .toLocaleLowerCase()
        .includes(query.toLocaleLowerCase()),
  );
  return (
    <>
      <div className="bank-filters">
        <Field label="Szukaj w banku">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tytuł, kontekst, tag…"
          />
        </Field>
        <Field label="Kategoria">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Wszystkie kategorie</option>
            {data.categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
        {kinds.length > 1 && (
          <Field label="Rodzaj">
            <select value={kind} onChange={(e) => setKind(e.target.value)}>
              <option value="">Wszystkie rodzaje</option>
              {kinds.map((k) => (
                <option key={k} value={k}>
                  {kindLabels[k]}
                </option>
              ))}
            </select>
          </Field>
        )}
      </div>
      {rows.length ? (
        <div className="bank-grid">
          {rows.map((r) => (
            <button
              className="surface bank-card"
              key={r.id}
              onClick={() => open(r.id)}
            >
              <span className="eyebrow">
                {kindLabels[r.kind]} · v{r.revision}
              </span>
              <h3>{r.title}</h3>
              <p>
                {r.context ||
                  "Otwórz wpis, sprawdź zawartość i wybierz sposób wykorzystania."}
              </p>
              <div className="button-row">
                {r.category_ids.map((cid) => (
                  <span className="badge quiet" key={cid}>
                    {data.categories.find((c) => c.id === cid)?.name ||
                      "Kategoria"}
                  </span>
                ))}
              </div>
              {!!r.uses?.length && (
                <small className="muted">
                  Wykorzystany w {r.uses.length} filmach
                </small>
              )}
              <span className="text-link">
                Zobacz zasób <ArrowRight size={15} />
              </span>
            </button>
          ))}
        </div>
      ) : (
        <Empty icon={BookOpen} title="Brak wpisów w tym widoku">
          Zmień filtry, dodaj własny wpis lub udostępnij wybrany zasób z filmu.
        </Empty>
      )}
    </>
  );
}

export function BankPicker({
  kinds,
  label = "Dodaj z banku",
}: {
  kinds: ResourceKind[];
  label?: string;
}) {
  const s = useStudio();
  const [open, setOpen] = useState(false),
    [data, setData] = useState(emptyData),
    [resource, setResource] = useState<BankResource | null>(null);
  useEffect(() => {
    if (open) s.run(async () => setData(await api("/workspace")));
  }, [open]);
  return (
    <>
      <Button icon={Library} onClick={() => setOpen(true)}>
        {label}
      </Button>
      <Modal
        open={open && !resource}
        onClose={() => setOpen(false)}
        title={label}
        description={`Dobierz tylko potrzebne zasoby. Film: ${s.project?.title || "brak wybranego filmu"}`}
        wide
      >
        <ResourceList
          data={data}
          kinds={kinds}
          open={(rid) =>
            s.run(async () =>
              setResource(await api(`/workspace/resources/${rid}`)),
            )
          }
        />
      </Modal>
      {resource && (
        <ResourceDialog
          resource={resource}
          close={() => setResource(null)}
          done={() => setOpen(false)}
        />
      )}
    </>
  );
}

export function FilmResources() {
  const s = useStudio(),
    p = s.project!;
  const [links, setLinks] = useState<ResourceLink[]>([]),
    [resource, setResource] = useState<BankResource | null>(null),
    [data, setData] = useState(emptyData),
    [channel, setChannel] = useState(p.channel_id),
    [category, setCategory] = useState(p.category_id),
    [format, setFormat] = useState(p.film_format);
  useEffect(() => {
    s.run(async () => {
      const [list, w] = await Promise.all([
        api<ResourceLink[]>(`/projects/${p.id}/workspace/links`),
        api<WorkspaceData>("/workspace"),
      ]);
      setLinks(list);
      setData(w);
    });
  }, [p.id, p.revision]);
  return (
    <section className="surface tool-panel film-resource-panel">
      <span className="eyebrow">KONTEKST TEGO FILMU</span>
      <h2>Kanał, kategoria i wykorzystane zasoby</h2>
      <div className="two-fields">
        <Field label="Kanał filmu">
          <select
            value={channel}
            onChange={(e) => {
              setChannel(e.target.value);
              setCategory("");
            }}
          >
            <option value="">Bez profilu</option>
            {data.channels.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Kategoria filmu">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Bez kategorii</option>
            {data.categories
              .filter((c) => !c.channel_id || c.channel_id === channel)
              .map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
          </select>
        </Field>
      </div>
      {textField("Format filmu", format, setFormat)}
      <Button
        onClick={() =>
          s.run(async () => {
            await s.mutate((current) =>
              api(`/projects/${current.id}/workspace/context`, {
                expected_revision: current.revision,
                channel_id: channel,
                category_id: category,
                film_format: format,
              }),
            );
            s.notify(
              "Zmieniono przypisanie filmu. Treść i ustawienia montażu pozostają w jego wersji.",
            );
          })
        }
      >
        Zapisz przypisanie filmu
      </Button>
      <p className="small muted">
        Zmiana przypisania nie stosuje nowych ustawień. Profile i strukturę
        dobieraj jawnie z szablonów.
      </p>
      <div className="button-row">
        <BankPicker kinds={["fact", "source", "note"]} />
        <BankPicker kinds={["template"]} label="Zastosuj szablon" />
        <BankPicker kinds={["baseline"]} label="Dobierz dane porównawcze" />
      </div>
      {links.length ? (
        <div className="resource-link-list">
          {links.map((link) => (
            <div key={link.resource_id}>
              <span>
                <strong>{link.title}</strong>
                <small>
                  Wersja w filmie: {link.revision}{" "}
                  {link.archived
                    ? "· wpis wycofany z banku"
                    : link.missing
                      ? "· bank niedostępny — migawka zachowana"
                      : ""}
                </small>
              </span>
              {link.update_available ? (
                <Button
                  onClick={() =>
                    s.run(async () =>
                      setResource(
                        await api(`/workspace/resources/${link.resource_id}`),
                      ),
                    )
                  }
                >
                  Porównaj z wersją {link.latest_revision}
                </Button>
              ) : (
                <span className="badge quiet">Migawka filmu</span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="small muted">
          Do tego filmu nie dodano jeszcze zasobów z banku.
        </p>
      )}
      {resource && (
        <ResourceDialog
          resource={resource}
          close={() => setResource(null)}
          done={() => {}}
        />
      )}
    </section>
  );
}
