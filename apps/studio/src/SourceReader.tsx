import { useEffect, useState } from "react";
import { useStudio } from "./context";
import { api, mediaUrl, safeUrl } from "./api";
import { Button, CommitText, Field, NumberField } from "./components";
import type { Project, Source } from "./types";

export default function SourceReader({ sourceId }: { sourceId: string }) {
  const s = useStudio(),
    p = s.project!,
    source = p.sources.find((x) => x.id === sourceId)!;
  const [query, setQuery] = useState(""),
    [page, setPage] = useState(source.pages[0]?.page || "1"),
    [quote, setQuote] = useState(""),
    [claim, setClaim] = useState(""),
    [showImage, setShowImage] = useState(false),
    [crop, setCrop] = useState({ x: 0, y: 0, width: 1, height: 1 });
  const [images, setImages] = useState<
      { index: number; name: string; chapters: string[] }[]
    >([]),
    [imageIndex, setImageIndex] = useState(0);
  const asset = p.assets.find((a) => a.id === source.asset_id),
    pdf = asset?.filename.endsWith(".pdf"),
    epub = asset?.filename.endsWith(".epub");
  useEffect(() => {
    if (epub)
      s.run(async () =>
        setImages(
          await api<typeof images>(
            `/projects/${p.id}/sources/${sourceId}/images`,
          ),
        ),
      );
  }, [sourceId, epub]);
  const pages = source.pages.filter(
    (x) =>
      !query || x.text.toLocaleLowerCase().includes(query.toLocaleLowerCase()),
  );
  const current = pages.find((x) => x.page === page) || pages[0];
  function metadata(changes: Partial<Source>) {
    s.run(() =>
      s.patch((c) => ({
        sources: c.sources.map((x) =>
          x.id === sourceId ? { ...x, ...changes } : x,
        ),
      })),
    );
  }
  async function cite() {
    await s.mutate((c) =>
      api<Project>(`/projects/${p.id}/sources/${sourceId}/quote`, {
        expected_revision: c.revision,
        page: current?.page || "1",
        quote,
        claim,
      }),
    );
    s.notify("Dodano cytat z lokalizacją do banku faktów");
    setQuote("");
    setClaim("");
  }
  return (
    <>
      <div className="button-row">
        {asset && (
          <a className="button" href={mediaUrl(p.id, asset.id)} download>
            Pobierz oryginalny dokument
          </a>
        )}
        {safeUrl(source.url) && (
          <a
            className="button"
            href={safeUrl(source.url)}
            target="_blank"
            rel="noreferrer"
          >
            Źródło w internecie
          </a>
        )}
        {safeUrl(String(source.metadata?.preview_url || "")) && (
          <a
            className="button"
            href={safeUrl(String(source.metadata?.preview_url))}
            target="_blank"
            rel="noreferrer"
          >
            Podgląd książki
          </a>
        )}
        {pdf && (
          <>
            <Button onClick={() => setShowImage(!showImage)}>
              {showImage ? "Ukryj skan" : "Pokaż skan strony"}
            </Button>
            <Button
              onClick={() =>
                s.run(async () => {
                  await api(`/projects/${p.id}/sources/${sourceId}/ocr`, {
                    pages: [current?.page],
                  });
                  s.notify("OCR wybranej strony w kolejce");
                })
              }
            >
              OCR tej strony
            </Button>
          </>
        )}
        {epub && (
          <Button
            disabled={!images.length}
            onClick={() => {
              setShowImage(!showImage);
              if (!showImage && images[imageIndex]?.chapters[0]) {
                setPage(images[imageIndex].chapters[0]);
                setQuote("");
              }
            }}
          >
            {showImage ? "Ukryj ilustracje" : "Pokaż ilustracje EPUB"} (
            {images.length})
          </Button>
        )}
      </div>
      <details>
        <summary>Metadane wydania</summary>
        <div className="two-fields">
          {(
            [
              ["title", "Tytuł"],
              ["author", "Autor"],
              ["edition", "Wydanie i wydawca"],
              ["identifier", "ISBN / DOI"],
              ["url", "Adres źródła"],
            ] as const
          ).map(([key, label]) => (
            <Field key={key} label={label}>
              <CommitText
                value={source[key]}
                onCommit={(v) => metadata({ [key]: v })}
              />
            </Field>
          ))}
        </div>
      </details>
      <Field label="Znajdź w tekście">
        <input value={query} onChange={(e) => setQuery(e.target.value)} />
      </Field>
      {source.pages.length > 0 && (
        <Field label={`Strona / rozdział · ${pages.length} wyników`}>
          <select
            value={current?.page || page}
            onChange={(e) => {
              setPage(e.target.value);
              setQuote("");
            }}
          >
            {pages.map((x, index) => (
              <option key={x.page} value={x.page}>
                {/^[0-9]+$/.test(String(x.page))
                  ? `Strona ${x.page}`
                  : `Sekcja ${index + 1}`}{" "}
                · {x.text.slice(0, 65)}
              </option>
            ))}
          </select>
        </Field>
      )}
      <div className="reader-grid">
        <section
          className="document-reader"
          onMouseUp={() => {
            const text = window.getSelection()?.toString().trim();
            if (text) setQuote(text);
          }}
        >
          <p>
            {current?.text ||
              (source.pages.length
                ? "Brak pasujących fragmentów lub warstwy tekstowej."
                : source.text) ||
              "Opis katalogowy. Dodaj plik lub otwórz dostępny podgląd książki."}
          </p>
        </section>
        {showImage && (pdf || epub) && current && (
          <section>
            {epub && (
              <Field label="Ilustracja w książce">
                <select
                  value={imageIndex}
                  onChange={(e) => {
                    const index = Number(e.target.value);
                    setImageIndex(index);
                    if (images[index]?.chapters[0])
                      setPage(images[index].chapters[0]);
                    setQuote("");
                  }}
                >
                  {images.map((i) => (
                    <option value={i.index} key={i.index}>
                      {i.name}
                    </option>
                  ))}
                </select>
              </Field>
            )}
            <img
              className="source-scan"
              src={
                epub
                  ? `/api/projects/${p.id}/sources/${sourceId}/image/${imageIndex}`
                  : `/api/projects/${p.id}/sources/${sourceId}/page/${current.page}/image`
              }
              alt={`Skan strony ${current.page}`}
            />
            <p className="small muted">
              Prostokąt ilustracji: współrzędne od 0 do 1.
            </p>
            <div className="two-fields">
              {(["x", "y", "width", "height"] as const).map((key) => (
                <NumberField
                  key={key}
                  label={key}
                  min={0}
                  max={1}
                  step={0.01}
                  value={crop[key]}
                  onCommit={(v) => setCrop((c) => ({ ...c, [key]: v }))}
                />
              ))}
            </div>
            <Button
              onClick={() =>
                s.run(async () => {
                  const r = await api<{ project: Project }>(
                    `/projects/${p.id}/sources/${sourceId}/illustration`,
                    { page: current.page, crop, image_index: imageIndex },
                  );
                  s.accept(r.project);
                  s.notify("Ilustrację dodano z numerem strony i pochodzeniem");
                })
              }
            >
              Wyodrębnij ilustrację do biblioteki
            </Button>
          </section>
        )}
      </div>
      <div className="two-fields">
        <Field label="Dosłowny cytat">
          <textarea
            rows={4}
            value={quote}
            onChange={(e) => setQuote(e.target.value)}
            placeholder="Zaznacz fragment tekstu lub wklej cytat z tej strony"
          />
        </Field>
        <Field label="Twierdzenie do sprawdzenia">
          <textarea
            rows={4}
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            placeholder="Jakie twierdzenie wspiera cytat?"
          />
        </Field>
      </div>
      <Button
        primary
        disabled={!quote.trim() && !claim.trim()}
        onClick={() => s.run(cite)}
      >
        Dodaj fakt z lokalizacją {current?.page || ""}
      </Button>
      <p className="small muted">
        Nowy fakt wymaga weryfikacji. Katalog i podgląd książki mają osobne
        oznaczenia dostępu; nie oznaczają dostępności pełnego tekstu.
      </p>
    </>
  );
}
