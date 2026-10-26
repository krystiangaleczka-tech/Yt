import { useEffect, useState } from "react";
import {
  Search,
  Image as ImageIcon,
  Film,
  BookOpen,
  Globe,
  ArrowDownToLine,
  Plus,
  ExternalLink,
  Upload,
  Link2,
  FileText,
  ArrowLeft,
  Settings2,
  LoaderCircle,
} from "lucide-react";
import { useStudio } from "./context";
import { api, upload, safeUrl, id } from "./api";
import { Button, Empty, Field, Modal, SectionHead } from "./components";
import type {
  Connector,
  SearchResult,
  Asset,
  Project,
  Source,
  Fact,
} from "./types";

const categories = [
  { id: "image", label: "Zdjęcia", icon: ImageIcon },
  { id: "video", label: "Filmy stockowe", icon: Film },
  { id: "book", label: "Książki", icon: BookOpen },
  { id: "information", label: "Informacje", icon: Globe },
];
export default function Sources() {
  const s = useStudio(),
    p = s.project!;
  const [kind, setKind] = useState("image"),
    [providers, setProviders] = useState<Connector[]>([]),
    [provider, setProvider] = useState("commons"),
    [query, setQuery] = useState(s.searchInitial),
    [results, setResults] = useState<SearchResult[]>([]),
    [searching, setSearching] = useState(false),
    [searched, setSearched] = useState(false),
    [page, setPage] = useState(1),
    [fetching, setFetching] = useState<string | null>(null),
    [urlOpen, setUrlOpen] = useState(false),
    [url, setUrl] = useState(""),
    [document, setDocument] = useState<Source | null>(null),
    [docQuery, setDocQuery] = useState("");
  useEffect(() => {
    s.run(async () => setProviders(await api<Connector[]>("/connectors")));
  }, [s.settingsOpen]);
  const available = providers.filter((c) => c.kinds.includes(kind));
  const target = p.scenes.find((x) => x.id === s.targetScene);
  function category(value: string) {
    setKind(value);
    const next = providers.find((c) => c.kinds.includes(value) && c.configured);
    setProvider(next?.id || "commons");
    setResults([]);
    setSearched(false);
    setPage(1);
  }
  async function search(nextPage = 1) {
    setSearching(true);
    setSearched(true);
    try {
      const found = await api<SearchResult[]>(
        `/search?provider=${encodeURIComponent(provider)}&q=${encodeURIComponent(query)}&kind=${kind}&page=${nextPage}`,
      );
      setResults(found);
      setPage(nextPage);
    } finally {
      setSearching(false);
    }
  }
  async function add(result: SearchResult) {
    setFetching(result.id);
    try {
      if (result.download_url) {
        const response = await api<{ asset: Asset; project: Project }>(
          "/projects/" + p.id + "/fetch",
          { result },
        );
        s.accept(response.project);
        if (target) {
          await s.patch((current) => ({
            scenes: current.scenes.map((x) =>
              x.id === target.id
                ? { ...x, asset_id: response.asset.id, mode: "search" }
                : x,
            ),
          }));
          s.setPage("generation");
        }
        s.notify(
          target
            ? "Materiał przypisano do ujęcia"
            : "Materiał dodano do biblioteki",
        );
      } else {
        await s.mutate((current) =>
          api<Project>("/projects/" + p.id + "/sources", {
            expected_revision: current.revision,
            result,
          }),
        );
        s.notify("Zapisano źródło do researchu");
      }
    } finally {
      setFetching(null);
    }
  }
  async function importUrl() {
    setFetching("url");
    try {
      const response = await api<{ project: Project }>(
        "/projects/" + p.id + "/fetch",
        { url },
      );
      s.accept(response.project);
      setUrlOpen(false);
      setUrl("");
      s.notify("Dodano treść źródła");
    } finally {
      setFetching(null);
    }
  }
  async function importDoc(file: File) {
    const response = await upload<{ project: Project }>(
      "/projects/" + p.id + "/media",
      file,
    );
    s.accept(response.project);
    s.notify("Dokument dodano ze wskazaniem stron lub rozdziałów");
  }
  async function cite(source: Source) {
    const fact: Fact = {
      id: id("fact_"),
      claim: docQuery || "",
      source: source.title,
      url: source.url,
      page: "",
      status: "UNVERIFIED",
      note: "",
    };
    await s.patch((current) => ({ facts: [...current.facts, fact] }));
    setDocument(null);
    s.setPage("facts");
    s.notify("Dodano pozycję do sprawdzenia");
  }
  return (
    <div className="page-content sources-page">
      <SectionHead
        eyebrow="RESEARCH I MATERIAŁY"
        title="Znajdź dobry punkt wyjścia."
        description="Źródła do historii. Obrazy do jej opowiedzenia."
      >
        <Button icon={Settings2} onClick={() => s.setSettingsOpen(true)}>
          Połączenia
        </Button>
        <Button icon={Link2} onClick={() => setUrlOpen(true)}>
          Dodaj adres
        </Button>
        <label className="button primary">
          <Upload size={16} />
          Wgraj dokument
          <input
            type="file"
            accept=".pdf,.epub,.txt,.md"
            className="visually-hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) s.run(() => importDoc(file));
              e.target.value = "";
            }}
          />
        </label>
      </SectionHead>
      {target && (
        <div className="context-banner">
          <ClapIcon size={16} />
          <span>
            Szukasz materiału do ujęcia: <strong>{target.title}</strong>
          </span>
          <button
            className="text-button"
            onClick={() => s.setPage("generation")}
          >
            <ArrowLeft size={14} />
            Wróć do ujęcia
          </button>
        </div>
      )}
      <div className="filter-pills">
        {categories.map((c) => (
          <button
            key={c.id}
            className={kind === c.id ? "active" : ""}
            onClick={() => category(c.id)}
          >
            <c.icon size={16} />
            {c.label}
          </button>
        ))}
      </div>
      <form
        className="source-search"
        onSubmit={(e) => {
          e.preventDefault();
          s.run(() => search());
        }}
      >
        <div className="search-input-wrap">
          <Search size={20} />
          <input
            aria-label="Szukaj materiałów"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              kind === "book"
                ? "Tytuł, autor, ISBN lub temat książki…"
                : kind === "information"
                  ? "Temat, publikacja lub DOI…"
                  : "Opisz kadr, miejsce lub temat…"
            }
            maxLength={200}
          />
        </div>
        <select
          aria-label="Dostawca źródeł"
          value={provider}
          onChange={(e) => {
            setProvider(e.target.value);
            setResults([]);
            setSearched(false);
          }}
        >
          {available.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
              {c.configured ? "" : " · dodaj klucz"}
            </option>
          ))}
        </select>
        <Button primary type="submit" busy={searching} disabled={!query.trim()}>
          Szukaj
        </Button>
      </form>
      <div className="source-caption">
        <span>{providers.find((c) => c.id === provider)?.note}</span>
        <a
          href={
            provider === "commons"
              ? "https://commons.wikimedia.org"
              : provider === "pixabay"
                ? "https://pixabay.com"
                : provider === "openlibrary"
                  ? "https://openlibrary.org"
                  : provider === "pexels"
                    ? "https://pexels.com"
                    : provider === "crossref"
                      ? "https://crossref.org"
                      : "https://books.google.com"
          }
          target="_blank"
          rel="noreferrer"
        >
          {providers.find((c) => c.id === provider)?.name}
          <ExternalLink size={12} />
        </a>
      </div>
      {!searched ? (
        <div className="source-intro">
          <div className="source-intro-heading">
            <span className="empty-icon">
              <Search size={27} />
            </span>
            <h2>Dobre historie mają źródła.</h2>
            <p>
              Wyszukaj materiały lub dodaj własne dokumenty.
              <br />
              Zachowamy pochodzenie, autora i miejsce wykorzystania.
            </p>
          </div>
          <div className="connector-grid">
            {providers
              .filter((c) => c.kinds.includes(kind))
              .map((c) => (
                <button
                  key={c.id}
                  className={`connector-card ${provider === c.id ? "selected" : ""}`}
                  onClick={() => setProvider(c.id)}
                >
                  <span className="connector-symbol">{c.name.slice(0, 2)}</span>
                  <div>
                    <strong>{c.name}</strong>
                    <p>{c.note}</p>
                  </div>
                  <span
                    className={`badge ${c.configured ? "quiet" : "warning"}`}
                  >
                    {c.configured ? "Można wyszukać" : "Wymaga klucza"}
                  </span>
                </button>
              ))}
          </div>
        </div>
      ) : searching ? (
        <div className="loading">
          <LoaderCircle className="spin" />
          <span>Szukam materiałów…</span>
        </div>
      ) : !results.length ? (
        <Empty icon={Search} title="Brak wyników dla tego zapytania">
          Zmień hasło lub wybierz inne źródło.
        </Empty>
      ) : (
        <>
          <div
            className={`search-results ${kind === "book" || kind === "information" ? "document-results" : ""}`}
          >
            {results.map((result) => (
              <article
                className="result-card surface"
                key={result.provider + result.id}
              >
                {result.thumbnail ? (
                  <div className="result-image">
                    <img
                      src={safeUrl(result.thumbnail)}
                      alt={result.title}
                      loading="lazy"
                      referrerPolicy="no-referrer"
                    />
                  </div>
                ) : (
                  <div className={`result-placeholder ${kind}`}>
                    <BookOpen size={28} />
                  </div>
                )}
                <div className="result-body">
                  <span className="eyebrow">
                    {providers.find((c) => c.id === result.provider)?.name}
                  </span>
                  <h3>{result.title}</h3>
                  {result.author && (
                    <p className="small muted result-author">{result.author}</p>
                  )}
                  {result.edition && (
                    <p className="small muted">
                      Wydanie / data: {result.edition}
                    </p>
                  )}
                  {result.license && (
                    <span className="license-tag">{result.license}</span>
                  )}
                  <div className="result-actions">
                    <Button
                      primary={!!target}
                      busy={fetching === result.id}
                      disabled={!!fetching}
                      icon={result.download_url ? ArrowDownToLine : Plus}
                      onClick={() => s.run(() => add(result))}
                    >
                      {result.download_url
                        ? target
                          ? "Użyj w ujęciu"
                          : "Do biblioteki"
                        : "Zapisz źródło"}
                    </Button>
                    {safeUrl(result.url) && (
                      <a
                        className="icon-button"
                        href={safeUrl(result.url)}
                        target="_blank"
                        rel="noreferrer"
                        aria-label="Otwórz oryginalne źródło"
                      >
                        <ExternalLink size={16} />
                      </a>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
          <div className="pagination">
            <Button
              disabled={page === 1}
              onClick={() => s.run(() => search(page - 1))}
            >
              Poprzednia
            </Button>
            <span>Strona {page}</span>
            <Button onClick={() => s.run(() => search(page + 1))}>
              Następna
            </Button>
          </div>
        </>
      )}
      <div className="saved-sources">
        <div className="inline-heading">
          <h2>Źródła w tym projekcie</h2>
          <span className="badge quiet">{p.sources.length}</span>
        </div>
        {!p.sources.length ? (
          <p className="muted">
            Tu znajdziesz zapisane książki, strony i dokumenty.
          </p>
        ) : (
          <div className="saved-source-list">
            {p.sources.map((source) => (
              <button
                key={source.id}
                onClick={() => {
                  setDocument(source);
                  setDocQuery("");
                }}
                className="saved-source"
              >
                <span className="source-file-icon">
                  <FileText size={19} />
                </span>
                <div>
                  <strong>{source.title}</strong>
                  <span>
                    {[
                      source.author,
                      source.edition,
                      source.pages.length
                        ? source.pages.length + " stron / sekcji"
                        : source.provider,
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </span>
                </div>
                <ArrowRightIcon size={16} />
              </button>
            ))}
          </div>
        )}
      </div>
      <Modal
        open={urlOpen}
        onClose={() => setUrlOpen(false)}
        title="Dodaj źródło z internetu"
        description="Strona, raport, zdjęcie lub bezpośredni adres filmu"
      >
        <Field label="Adres URL">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://…"
          />
        </Field>
        <Button
          primary
          icon={Plus}
          busy={fetching === "url"}
          onClick={() => s.run(importUrl)}
          disabled={!url}
        >
          Dodaj do projektu
        </Button>
        <p className="small muted">
          Katalog książek nie oznacza dostępu do pełnego tekstu. PDF lub EPUB
          możesz wgrać osobno.
        </p>
      </Modal>
      <Modal
        open={!!document}
        onClose={() => setDocument(null)}
        title={document?.title || "Źródło"}
        description={
          [document?.author, document?.edition, document?.identifier]
            .filter(Boolean)
            .join(" · ") || "Dokument źródłowy"
        }
        wide
      >
        {document && (
          <>
            <div className="button-row">
              {safeUrl(document.url) && (
                <a
                  className="button"
                  href={safeUrl(document.url)}
                  target="_blank"
                  rel="noreferrer"
                >
                  <ExternalLink size={15} />
                  Otwórz oryginał
                </a>
              )}
              <Button icon={Plus} onClick={() => s.run(() => cite(document))}>
                Dodaj fakt do sprawdzenia
              </Button>
            </div>
            <Field label="Szukaj fragmentu">
              <input
                value={docQuery}
                onChange={(e) => setDocQuery(e.target.value)}
                placeholder="Wpisz szukaną frazę"
              />
            </Field>
            <div className="document-reader">
              {document.pages.length ? (
                document.pages
                  .filter(
                    (x) =>
                      !docQuery ||
                      x.text
                        .toLocaleLowerCase()
                        .includes(docQuery.toLocaleLowerCase()),
                  )
                  .map((x) => (
                    <section key={x.page}>
                      <div className="document-page">
                        Strona / sekcja {x.page}
                      </div>
                      <p>
                        {x.text ||
                          "Brak warstwy tekstowej. Sprawdź oryginalny skan."}
                      </p>
                    </section>
                  ))
              ) : (
                <p>
                  {document.text ||
                    "Zapisano opis katalogowy. Otwórz źródło albo wgraj dostępny dokument."}
                </p>
              )}
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}
function ArrowRightIcon(props: { size?: number }) {
  return <ExternalLink {...props} />;
}
function ClapIcon(props: { size?: number }) {
  return <Film {...props} />;
}
