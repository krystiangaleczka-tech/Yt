import { useEffect, useState } from "react";
import { Archive, Check, FolderOpen, Plus, Upload } from "lucide-react";
import { useStudio } from "./context";
import { api, id, safeUrl, upload } from "./api";
import { Button, Field, Modal, SectionHead } from "./components";
import type { Project } from "./types";
import type {
  BankResource,
  Category,
  Preset,
  ResourceKind,
  WorkspaceData,
} from "./workspaceTypes";
import { kindLabels, workspaceTitles, presetLabels } from "./workspaceTypes";
import type { Chapter } from "./developmentTypes";
import { blankChapter, blankIdea, blankSection } from "./developmentTypes";
import {
  textField,
  kindsFor,
  useWorkspace,
  ResourceDialog,
  ResourceList,
  PresetFields,
} from "./Workspace";

function StructureFields({
  chapters,
  change,
}: {
  chapters: Chapter[];
  change: (c: Chapter[]) => void;
}) {
  return (
    <div className="workspace-template-structure">
      {chapters.map((c, i) => (
        <section className="surface tool-panel" key={c.id}>
          {textField(`Rola rozdziału ${i + 1}`, c.title, (v) =>
            change(
              chapters.map((x) => (x.id === c.id ? { ...x, title: v } : x)),
            ),
          )}
          {textField(
            "Wskazówki dla autora",
            c.purpose,
            (v) =>
              change(
                chapters.map((x) => (x.id === c.id ? { ...x, purpose: v } : x)),
              ),
            2,
          )}
          {c.sections.map((section, j) => (
            <div className="two-fields" key={section.id}>
              {textField(`Podrozdział ${i + 1}.${j + 1}`, section.title, (v) =>
                change(
                  chapters.map((x) =>
                    x.id === c.id
                      ? {
                          ...x,
                          sections: x.sections.map((y) =>
                            y.id === section.id ? { ...y, title: v } : y,
                          ),
                        }
                      : x,
                  ),
                ),
              )}
              <Field label="Czas (s)">
                <input
                  type="number"
                  min={5}
                  max={3600}
                  value={section.seconds}
                  onChange={(e) =>
                    change(
                      chapters.map((x) =>
                        x.id === c.id
                          ? {
                              ...x,
                              sections: x.sections.map((y) =>
                                y.id === section.id
                                  ? { ...y, seconds: Number(e.target.value) }
                                  : y,
                              ),
                            }
                          : x,
                      ),
                    )
                  }
                />
              </Field>
            </div>
          ))}
          <div className="button-row">
            <Button
              onClick={() =>
                change(
                  chapters.map((x) =>
                    x.id === c.id
                      ? { ...x, sections: [...x.sections, blankSection()] }
                      : x,
                  ),
                )
              }
            >
              Dodaj część
            </Button>
            <Button
              subtle
              onClick={() => change(chapters.filter((x) => x.id !== c.id))}
            >
              Usuń rozdział
            </Button>
          </div>
        </section>
      ))}
      <Button icon={Plus} onClick={() => change([...chapters, blankChapter()])}>
        Dodaj rozdział szablonu
      </Button>
    </div>
  );
}

function ResourceEditor({
  resource,
  kind,
  data,
  close,
  saved,
}: {
  resource?: BankResource;
  kind: ResourceKind;
  data: WorkspaceData;
  close: () => void;
  saved: () => Promise<void>;
}) {
  const s = useStudio();
  const [r, setR] = useState<BankResource>(() =>
    resource
      ? structuredClone(resource)
      : {
          id: id("res_"),
          revision: 0,
          title: "",
          kind,
          scope: "workspace",
          channel_id: "",
          category_ids: [],
          tags: [],
          context: "",
          payload:
            kind === "template"
              ? { preset: {}, chapters: [] }
              : kind === "idea"
                ? blankIdea()
                : kind === "baseline"
                  ? {
                      views_30d: [],
                      typical_views_30d: null,
                      ctr: null,
                      retention: null,
                      comparable_minutes: null,
                      success_multiple: 1.5,
                      viral_multiple: 5,
                      evidence: "",
                    }
                  : kind === "note"
                    ? { text: "" }
                    : kind === "fact"
                      ? {
                          facts: [
                            {
                              id: id("fact_"),
                              claim: "",
                              source: "",
                              url: "",
                              page: "",
                              quote: "",
                              note: "",
                              status: "UNVERIFIED",
                            },
                          ],
                          sources: [],
                          assets: [],
                        }
                      : {
                          sources: [
                            {
                              id: id("src_"),
                              title: "",
                              url: "",
                              author: "",
                              edition: "",
                              identifier: "",
                              text: "",
                              provider: "manual",
                              pages: [],
                            },
                          ],
                          assets: [],
                          facts: [],
                        },
          origin_project_id: "",
          origin_item_id: "",
          created_at: "",
          updated_at: "",
          archived: false,
        },
  );
  const [samples, setSamples] = useState(
    (r.payload.views_30d || []).join("\n"),
  );
  const set = (values: Partial<BankResource>) =>
    setR((current) => ({ ...current, ...values }));
  const payload = (values: Record<string, unknown>) =>
    setR((current) => ({
      ...current,
      payload: { ...current.payload, ...values },
    }));
  const fact = (values: Record<string, unknown>) =>
    payload({ facts: [{ ...r.payload.facts[0], ...values }] });
  const source = (values: Record<string, unknown>) =>
    payload({ sources: [{ ...r.payload.sources[0], ...values }] });
  async function save() {
    let item = structuredClone(r);
    if (kind === "idea") item.payload.title = item.title;
    if (kind === "baseline") {
      const list = samples
        .split(/\r?\n/)
        .map((v: string) => v.replace(/\s/g, ""))
        .filter(Boolean);
      if (list.some((v: string) => !/^\d+$/.test(v)))
        throw new Error(
          "Wpisz wyświetlenia po jednej całkowitej liczbie na wiersz.",
        );
      item.payload.views_30d = list.map(Number);
    }
    if (kind === "source") item.payload.sources[0].title = item.title;
    await api("/workspace/resources", item);
    await saved();
    close();
    s.notify("Zapisano nową wersję wpisu banku");
  }
  return (
    <Modal
      open
      onClose={close}
      title={resource ? "Edytuj wpis banku" : "Nowy wpis: " + kindLabels[kind]}
      description="Zmiana dotyczy banku. Wersje używane przez filmy pozostaną w ich migawkach."
      wide
    >
      {textField("Nazwa wpisu", r.title, (v) => set({ title: v }))}
      <div className="two-fields">
        <Field label="Zakres">
          <select
            value={r.scope}
            onChange={(e) =>
              set({ scope: e.target.value as BankResource["scope"] })
            }
          >
            <option value="workspace">Cała pracownia</option>
            <option value="channel">Kanał</option>
            <option value="category">Kategoria</option>
          </select>
        </Field>
        <Field label="Kanał — opcjonalnie">
          <select
            value={r.channel_id}
            onChange={(e) => set({ channel_id: e.target.value })}
          >
            <option value="">Wszystkie kanały</option>
            {data.channels.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <fieldset className="workspace-categories">
        <legend>Kategorie zasobu</legend>
        {data.categories.map((c) => (
          <label className="checkbox" key={c.id}>
            <input
              type="checkbox"
              checked={r.category_ids.includes(c.id)}
              onChange={(e) =>
                set({
                  category_ids: e.target.checked
                    ? [...r.category_ids, c.id]
                    : r.category_ids.filter((x) => x !== c.id),
                })
              }
            />
            {c.name}
          </label>
        ))}
      </fieldset>
      {textField("Tagi — oddziel przecinkami", r.tags.join(", "), (v) =>
        set({
          tags: v
            .split(",")
            .map((x) => x.trim())
            .filter(Boolean),
        }),
      )}
      {textField(
        "Kontekst i ograniczenia użycia",
        r.context,
        (v) => set({ context: v }),
        3,
      )}
      {kind === "note" &&
        textField(
          "Treść notatki — nie jest potwierdzonym faktem",
          r.payload.text || "",
          (v) => payload({ text: v }),
          8,
        )}
      {kind === "idea" && (
        <>
          {textField(
            "Pytanie dla widza",
            r.payload.question || "",
            (v) => payload({ question: v }),
            2,
          )}
          {textField(
            "Punkt widzenia",
            r.payload.angle || "",
            (v) => payload({ angle: v }),
            3,
          )}
          {textField(
            "Notatki",
            r.payload.notes || "",
            (v) => payload({ notes: v }),
            3,
          )}
        </>
      )}
      {kind === "fact" && (
        <>
          {textField(
            "Twierdzenie",
            r.payload.facts[0].claim || "",
            (v) => fact({ claim: v }),
            3,
          )}
          <div className="two-fields">
            {textField("Autor / źródło", r.payload.facts[0].source || "", (v) =>
              fact({ source: v }),
            )}
            {textField("Adres źródła", r.payload.facts[0].url || "", (v) =>
              fact({ url: v }),
            )}
          </div>
          {textField("Strona / sekcja", r.payload.facts[0].page || "", (v) =>
            fact({ page: v }),
          )}
          {textField(
            "Cytat — tylko dokładny tekst źródła",
            r.payload.facts[0].quote || "",
            (v) => fact({ quote: v }),
            3,
          )}
          <Field label="Stan weryfikacji w banku">
            <select
              value={r.payload.facts[0].status}
              onChange={(e) =>
                fact({
                  status: e.target.value,
                  checked_at:
                    e.target.value === "VERIFIED"
                      ? new Date().toISOString()
                      : "",
                })
              }
            >
              <option value="UNVERIFIED">Do sprawdzenia</option>
              <option value="VERIFIED">Sprawdzony</option>
              <option value="DISPUTED">Sporny</option>
              <option value="DRAMATIZATION">Dramatyzacja</option>
            </select>
          </Field>
          <Field label="Dołącz źródło z banku">
            <select
              value=""
              onChange={(e) => {
                if (e.target.value)
                  s.run(async () => {
                    const selected = await api<BankResource>(
                      `/workspace/resources/${e.target.value}`,
                    );
                    payload({
                      sources: selected.payload.sources,
                      assets: selected.payload.assets,
                      facts: [
                        {
                          ...r.payload.facts[0],
                          source_id: selected.payload.sources[0].id,
                          source: selected.payload.sources[0].title,
                          url: selected.payload.sources[0].url,
                        },
                      ],
                    });
                  });
              }}
            >
              <option value="">Wybierz źródło — opcjonalnie</option>
              {data.resources
                .filter((x) => x.kind === "source")
                .map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.title}
                  </option>
                ))}
            </select>
          </Field>
        </>
      )}
      {kind === "source" && (
        <>
          <div className="two-fields">
            {textField("Autor", r.payload.sources[0].author || "", (v) =>
              source({ author: v }),
            )}
            {textField("Adres źródła", r.payload.sources[0].url || "", (v) =>
              source({ url: v }),
            )}
            {textField(
              "Wydanie / data",
              r.payload.sources[0].edition || "",
              (v) => source({ edition: v }),
            )}
            {textField(
              "ISBN / DOI / identyfikator",
              r.payload.sources[0].identifier || "",
              (v) => source({ identifier: v }),
            )}
          </div>
          {textField(
            "Własna notatka bibliograficzna lub posiadany tekst",
            r.payload.sources[0].text || "",
            (v) => source({ text: v }),
            8,
          )}
        </>
      )}
      {kind === "media" && (
        <p>
          Plik pozostaje bez zmian. Edytujesz nazwę, zakres, kategorie i opis
          wpisu.
        </p>
      )}
      {kind === "template" && (
        <>
          <h3>Ustawienia do ponownego użycia</h3>
          <PresetFields
            value={r.payload.preset || {}}
            change={(v) => payload({ preset: v })}
          />
          <h3>Struktura do wypełnienia</h3>
          <p className="small muted">
            Używaj nazw ról, np. „Pytanie otwarcia” lub „Weryfikacja hipotezy”.
            Fakty i gotowa narracja należą do filmu.
          </p>
          <StructureFields
            chapters={r.payload.chapters || []}
            change={(v) => payload({ chapters: v })}
          />
        </>
      )}
      {kind === "baseline" && (
        <>
          <p>
            Wpisuj rzeczywiste wyniki porównywalnych filmów po pierwszych 30
            dniach. Prognozy nie należą do tego zbioru.
          </p>
          {textField(
            "Wyświetlenia — jedna liczba na wiersz",
            samples,
            setSamples,
            7,
          )}
          <div className="two-fields">
            {(
              [
                "typical_views_30d",
                "ctr",
                "retention",
                "comparable_minutes",
                "success_multiple",
                "viral_multiple",
              ] as const
            ).map((k, i) => (
              <Field
                label={
                  [
                    "Typowy wynik 30 dni — opcjonalnie",
                    "CTR (%)",
                    "Średni obejrzany procent",
                    "Długość porównywanych filmów (min)",
                    "Sukces ×",
                    "Wiral ×",
                  ][i]
                }
                key={k}
              >
                <input
                  type="number"
                  step="any"
                  value={r.payload[k] ?? ""}
                  onChange={(e) =>
                    payload({
                      [k]: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                />
              </Field>
            ))}
          </div>
          {textField(
            "Źródło danych, okres, format i porównywalność",
            r.payload.evidence || "",
            (v) => payload({ evidence: v }),
            4,
          )}
        </>
      )}
      <div className="button-row">
        <Button
          primary
          icon={Check}
          disabled={!r.title.trim()}
          onClick={() => s.run(save)}
        >
          Zapisz wpis banku
        </Button>
        {resource && (
          <Button
            icon={Archive}
            onClick={() =>
              s.run(async () => {
                await api("/workspace/resources", { ...r, archived: true });
                await saved();
                close();
                s.notify("Wpis zarchiwizowany. Filmy zachowują swoje wersje.");
              })
            }
          >
            Archiwizuj wpis
          </Button>
        )}
      </div>
    </Modal>
  );
}

function CategoryEditor({
  category,
  data,
  close,
  saved,
}: {
  category?: Category;
  data: WorkspaceData;
  close: () => void;
  saved: () => Promise<void>;
}) {
  const s = useStudio();
  const [c, setC] = useState<Category>(
    category
      ? structuredClone(category)
      : {
          id: id("cat_"),
          revision: 0,
          name: "",
          description: "",
          channel_id: "",
          defaults: {},
          archived: false,
        },
  );
  return (
    <Modal
      open
      onClose={close}
      title={category ? "Edytuj kategorię" : "Nowa kategoria"}
      description="Ustawienia kategorii są domyślne dla nowych filmów. Istniejące filmy zachowują swoje wersje."
      wide
    >
      {textField("Nazwa kategorii", c.name, (v) => setC({ ...c, name: v }))}
      {textField(
        "Opis i zakres tematów",
        c.description,
        (v) => setC({ ...c, description: v }),
        3,
      )}
      <Field label="Kanał kategorii">
        <select
          value={c.channel_id}
          onChange={(e) => setC({ ...c, channel_id: e.target.value })}
        >
          <option value="">Wszystkie kanały</option>
          {data.channels.map((ch) => (
            <option key={ch.id} value={ch.id}>
              {ch.name}
            </option>
          ))}
        </select>
      </Field>
      <PresetFields
        value={c.defaults}
        change={(v) => setC({ ...c, defaults: v })}
      />
      <div className="button-row">
        <Button
          primary
          disabled={!c.name.trim()}
          onClick={() =>
            s.run(async () => {
              await api("/workspace/categories", c);
              await saved();
              close();
            })
          }
        >
          Zapisz kategorię
        </Button>
        {category && (
          <Button
            onClick={() =>
              s.run(async () => {
                await api("/workspace/categories", { ...c, archived: true });
                await saved();
                close();
              })
            }
          >
            Archiwizuj kategorię
          </Button>
        )}
      </div>
    </Modal>
  );
}

function ChannelEditor({
  channel,
  close,
  saved,
}: {
  channel?: Record<string, any>;
  close: () => void;
  saved: () => Promise<void>;
}) {
  const s = useStudio();
  const [c, setC] = useState<Record<string, any>>(
    channel ? structuredClone(channel) : { name: "", language: "pl" },
  );
  return (
    <Modal
      open
      onClose={close}
      title={channel ? "Profil kanału" : "Nowy kanał"}
      description="Profil wspólny. Jego zmiana nie nadpisuje migawek istniejących filmów."
    >
      {textField("Nazwa kanału", c.name, (v) => setC({ ...c, name: v }))}
      <PresetFields
        value={
          Object.fromEntries(
            Object.entries(c).filter(([key]) => key in presetLabels),
          ) as Preset
        }
        change={(value) =>
          setC((current) => ({
            ...Object.fromEntries(
              Object.entries(current).filter(([key]) => !(key in presetLabels)),
            ),
            ...value,
          }))
        }
      />
      <Button
        primary
        disabled={!c.name.trim()}
        onClick={() =>
          s.run(async () => {
            await api("/channels", c);
            await saved();
            close();
          })
        }
      >
        Zapisz kanał
      </Button>
    </Modal>
  );
}

function WorkspaceSearch({ saved }: { saved: () => Promise<void> }) {
  const s = useStudio();
  const [providers, setProviders] = useState<Record<string, any>[]>([]),
    [provider, setProvider] = useState("openlibrary"),
    [query, setQuery] = useState(""),
    [rows, setRows] = useState<Record<string, any>[]>([]),
    [busy, setBusy] = useState(false),
    [searched, setSearched] = useState(false);
  useEffect(() => {
    s.run(async () =>
      setProviders(
        (await api<Record<string, any>[]>("/connectors")).filter(
          (p) =>
            p.configured &&
            p.kinds.some((k: string) => k === "book" || k === "information"),
        ),
      ),
    );
  }, []);
  async function search() {
    setBusy(true);
    try {
      const selected = providers.find((p) => p.id === provider);
      const kind = selected?.kinds.includes("book") ? "book" : "information";
      setRows(
        await api(
          `/search?provider=${encodeURIComponent(provider)}&q=${encodeURIComponent(query)}&kind=${kind}`,
        ),
      );
      setSearched(true);
    } finally {
      setBusy(false);
    }
  }
  return (
    <details className="surface tool-panel workspace-search">
      <summary>Szukaj nowych książek i publikacji do researchu</summary>
      <p className="small muted">
        Możesz zapisać opis źródła w banku lub dodać go bezpośrednio do
        wybranego filmu. Dostęp do pełnego tekstu sprawdzisz u dostawcy.
      </p>
      <div className="bank-filters">
        <Field label="Zapytanie">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Autor, tytuł, DOI lub temat"
            maxLength={200}
          />
        </Field>
        <Field label="Katalog źródeł">
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            {providers.map((p) => (
              <option value={p.id} key={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </Field>
        <Button
          primary
          busy={busy}
          disabled={!query.trim()}
          onClick={() => s.run(search)}
        >
          Szukaj
        </Button>
      </div>
      {searched && !rows.length && <p>Brak wyników dla tego zapytania.</p>}
      <div className="bank-grid">
        {rows.map((row, i) => (
          <section className="surface tool-panel" key={String(row.id || i)}>
            <h3>{row.title}</h3>
            <p>
              {row.author} · {row.edition || row.published_at}
            </p>
            <p className="small muted">{row.description}</p>
            {safeUrl(row.url) && (
              <a
                className="text-link"
                href={safeUrl(row.url)}
                target="_blank"
                rel="noreferrer"
              >
                Otwórz u dostawcy
              </a>
            )}
            <Button
              onClick={() =>
                s.run(async () => {
                  await api("/workspace/resources", {
                    title: String(row.title || "Źródło").slice(0, 200),
                    kind: "source",
                    payload: {
                      sources: [
                        {
                          id: id("src_"),
                          title: String(row.title || "Źródło"),
                          provider: String(row.provider || provider),
                          url: String(row.url || ""),
                          author: String(row.author || ""),
                          edition: String(row.edition || ""),
                          identifier: String(row.identifier || ""),
                          text: String(row.description || ""),
                          metadata: {
                            access: row.access || "metadata",
                            preview_url: row.preview_url || "",
                            published_at: row.published_at || "",
                          },
                        },
                      ],
                    },
                  });
                  await saved();
                  s.notify("Zapisano opis źródła w banku");
                })
              }
            >
              Zapisz źródło w banku
            </Button>
            <Button
              disabled={!s.project}
              onClick={() =>
                s.run(async () => {
                  await s.mutate((p) =>
                    api<Project>(`/projects/${p.id}/sources`, {
                      expected_revision: p.revision,
                      result: row,
                    }),
                  );
                  s.notify("Źródło dodano wyłącznie do filmu");
                })
              }
            >
              Dodaj do filmu
            </Button>
          </section>
        ))}
      </div>
    </details>
  );
}

export default function WorkspaceView({ section }: { section: string }) {
  const s = useStudio();
  const { data, refresh } = useWorkspace();
  const [resource, setResource] = useState<BankResource | null>(null),
    [editor, setEditor] = useState<{
      kind: ResourceKind;
      value?: BankResource;
    } | null>(null),
    [category, setCategory] = useState<Category | null | false>(false),
    [channel, setChannel] = useState<Record<string, any> | null | false>(false),
    [preset, setPreset] = useState<Preset>({}),
    [archive, setArchive] = useState(false);
  const [archivedRows, setArchivedRows] = useState<BankResource[]>([]);
  useEffect(() => setPreset(data.defaults.preset), [data.defaults.revision]);
  const kinds = kindsFor(section);
  async function refreshAll() {
    await refresh();
    await s.reloadList();
  }
  return (
    <div className="page-content workspace-page">
      <SectionHead
        eyebrow="PRACOWNIA / ZASOBY WSPÓLNE"
        title={workspaceTitles[section]}
        description="Niezależne od otwartego filmu. Wybierasz, co ma trafić do konkretnej produkcji."
      >
        {section === "workspace-settings" ? (
          <>
            <Button icon={Plus} onClick={() => setChannel(null)}>
              Dodaj kanał
            </Button>
            <Button primary icon={Plus} onClick={() => setCategory(null)}>
              Dodaj kategorię
            </Button>
          </>
        ) : (
          <>
            {section === "bank-media" && (
              <label className="button primary">
                <Upload size={16} />
                Wgraj do banku
                <input
                  type="file"
                  className="visually-hidden"
                  multiple
                  onChange={(e) => {
                    const files = Array.from(e.target.files || []);
                    s.run(async () => {
                      for (const file of files)
                        await upload("/workspace/media", file);
                      await refresh();
                      s.notify("Wgrano zasoby do banku");
                    });
                    e.target.value = "";
                  }}
                />
              </label>
            )}
            {kinds
              .filter((k) => k !== "media")
              .map((k) => (
                <Button
                  key={k}
                  primary={k === kinds[0]}
                  icon={Plus}
                  onClick={() => setEditor({ kind: k })}
                >
                  {kindLabels[k]}
                </Button>
              ))}
          </>
        )}
      </SectionHead>
      {section !== "workspace-settings" && (
        <div className="workspace-film-target">
          <FolderOpen size={18} />
          <span>
            {s.project ? (
              <>
                Film docelowy: <strong>{s.project.title}</strong>. Dodanie
                zasobu wymaga wyboru we wpisie.
              </>
            ) : (
              "Brak otwartego filmu. Bank pozostaje dostępny; nowy film utworzysz przyciskiem w panelu."
            )}
          </span>
        </div>
      )}
      {section === "workspace-settings" ? (
        <>
          <section className="surface tool-panel">
            <h2>Kanały</h2>
            <div className="bank-grid">
              {data.channels.map((c) => (
                <button
                  key={c.id}
                  className="bank-card surface"
                  onClick={() => setChannel(c)}
                >
                  <span className="eyebrow">PROFIL KANAŁU · v{c.revision}</span>
                  <h3>{c.name}</h3>
                  <p>
                    {c.narrative_style || "Uzupełnij styl i referencje kanału."}
                  </p>
                </button>
              ))}
            </div>
            {!data.channels.length && (
              <p>
                Dodaj profil kanału, aby nowe filmy korzystały ze wspólnego
                stylu.
              </p>
            )}
          </section>
          <section className="surface tool-panel">
            <h2>Kategorie</h2>
            <div className="bank-grid">
              {data.categories.map((c) => (
                <button
                  key={c.id}
                  className="bank-card surface"
                  onClick={() => setCategory(c)}
                >
                  <span className="eyebrow">KATEGORIA · v{c.revision}</span>
                  <h3>{c.name}</h3>
                  <p>{c.description}</p>
                </button>
              ))}
            </div>
          </section>
          <details className="surface tool-panel">
            <summary>Domyślne ustawienia całej pracowni</summary>
            <PresetFields value={preset} change={setPreset} />
            <Button
              primary
              onClick={() =>
                s.run(async () => {
                  await api("/workspace/defaults", {
                    revision: data.defaults.revision,
                    preset,
                  });
                  await refresh();
                  s.notify("Zapisano ustawienia dla nowych filmów");
                })
              }
            >
              Zapisz ustawienia pracowni
            </Button>
          </details>
        </>
      ) : (
        <>
          {section === "bank" && <WorkspaceSearch saved={refresh} />}
          <ResourceList
            data={data}
            kinds={kinds}
            open={(rid) =>
              s.run(async () =>
                setResource(await api(`/workspace/resources/${rid}`)),
              )
            }
          />
          <details className="advanced">
            <summary>Archiwum wpisów</summary>
            <Button
              icon={Archive}
              onClick={() =>
                s.run(async () => {
                  const resources = await api<BankResource[]>(
                    "/workspace/resources?include_archived=true",
                  );
                  setArchive(true);
                  setResource(null);
                  setArchivedRows(
                    resources.filter(
                      (r) => r.archived && kinds.includes(r.kind),
                    ),
                  );
                })
              }
            >
              Pokaż wycofane wpisy
            </Button>
            {archive && (
              <p className="small muted">
                Wycofanie nie usuwa wersji wykorzystanych przez filmy. Otwórz
                wpis, aby przywrócić go do banku.
              </p>
            )}
            {archivedRows.map((r) => (
              <Button
                key={r.id}
                onClick={() =>
                  s.run(async () => {
                    const full = await api<BankResource>(
                      `/workspace/resources/${r.id}`,
                    );
                    await api("/workspace/resources", {
                      ...full,
                      archived: false,
                    });
                    setArchivedRows((rows) =>
                      rows.filter((v) => v.id !== r.id),
                    );
                    await refresh();
                  })
                }
              >
                Przywróć: {r.title}
              </Button>
            ))}
          </details>
        </>
      )}
      {resource && (
        <ResourceDialog
          resource={resource}
          close={() => setResource(null)}
          done={() => s.run(refresh)}
          edit={(r) => {
            setResource(null);
            setEditor({ kind: r.kind, value: r });
          }}
        />
      )}
      {editor && (
        <ResourceEditor
          key={editor.value?.id || editor.kind}
          resource={editor.value}
          kind={editor.kind}
          data={data}
          close={() => setEditor(null)}
          saved={refreshAll}
        />
      )}
      {category !== false && (
        <CategoryEditor
          category={category || undefined}
          data={data}
          close={() => setCategory(false)}
          saved={refreshAll}
        />
      )}
      {channel !== false && (
        <ChannelEditor
          channel={channel || undefined}
          close={() => setChannel(false)}
          saved={refreshAll}
        />
      )}
    </div>
  );
}
