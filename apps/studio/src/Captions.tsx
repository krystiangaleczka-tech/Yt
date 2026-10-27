import { useEffect, useState } from "react";
import { Button, Field, NumberField } from "./components";
import type { Word } from "./types";

export default function CaptionEditor({
  words,
  duration,
  onSave,
}: {
  words: Word[];
  duration: number;
  onSave: (words: Word[]) => void;
}) {
  const [rows, setRows] = useState(words),
    [page, setPage] = useState(0),
    [split, setSplit] = useState<number | null>(null),
    [at, setAt] = useState(0),
    [first, setFirst] = useState(""),
    [second, setSecond] = useState("");
  useEffect(() => {
    setRows(words);
    setPage(0);
  }, [JSON.stringify(words)]);
  function update(index: number, values: Partial<Word>) {
    setRows((rows) =>
      rows.map((row, i) => (i === index ? { ...row, ...values } : row)),
    );
  }
  const pages = Math.max(1, Math.ceil(rows.length / 20));
  return (
    <section className="caption-editor">
      <h3>Tekst i czas napisów</h3>
      <p className="small muted">
        Czas pochodzi z nagrania. Popraw pisownię i zaznacz koniec napisu.
        Podział wymaga wskazania czasu po odsłuchu.
      </p>
      {rows.slice(page * 20, (page + 1) * 20).map((row, offset) => {
        const index = page * 20 + offset;
        return (
          <article className="caption-row" key={index}>
            <Field label={`Tekst ${index + 1}`}>
              <input
                value={row.word}
                onChange={(e) => update(index, { word: e.target.value })}
              />
            </Field>
            <div className="two-fields">
              <NumberField
                label="Od (s)"
                min={0}
                max={duration}
                step={0.01}
                value={row.start}
                onCommit={(start) => update(index, { start })}
              />
              <NumberField
                label="Do (s)"
                min={0}
                max={duration}
                step={0.01}
                value={row.end}
                onCommit={(end) => update(index, { end })}
              />
            </div>
            <label className="checkbox small">
              <input
                type="checkbox"
                checked={!!row.break_after}
                onChange={(e) =>
                  update(index, { break_after: e.target.checked })
                }
              />
              Koniec napisu po tym fragmencie
            </label>
            {row.probability !== undefined &&
              row.probability < 0.6 &&
              !row.reviewed && (
                <span className="badge warning">
                  Rozpoznanie do sprawdzenia
                </span>
              )}
            <div className="button-row">
              <Button
                subtle
                onClick={() => {
                  setSplit(index);
                  setAt(row.start);
                  setFirst(row.word);
                  setSecond("");
                }}
              >
                Podziel po odsłuchu
              </Button>
              <Button
                subtle
                disabled={index === rows.length - 1}
                onClick={() =>
                  setRows((rows) =>
                    rows.flatMap((word, i) =>
                      i === index
                        ? [
                            {
                              ...word,
                              word: word.word + " " + rows[index + 1].word,
                              end: rows[index + 1].end,
                              break_after: rows[index + 1].break_after,
                            },
                          ]
                        : i === index + 1
                          ? []
                          : [word],
                    ),
                  )
                }
              >
                Połącz z następnym
              </Button>
            </div>
          </article>
        );
      })}
      {split !== null && rows[split] && (
        <div className="surface tool-panel">
          <h3>Podziel fragment {split + 1}</h3>
          <NumberField
            label="Czas podziału w nagraniu (s)"
            min={rows[split].start}
            max={rows[split].end}
            step={0.01}
            value={at}
            onCommit={setAt}
          />
          <Field label="Pierwsza część tekstu">
            <input value={first} onChange={(e) => setFirst(e.target.value)} />
          </Field>
          <Field label="Druga część tekstu">
            <input value={second} onChange={(e) => setSecond(e.target.value)} />
          </Field>
          <Button
            disabled={
              !first.trim() ||
              !second.trim() ||
              at <= rows[split].start ||
              at >= rows[split].end
            }
            onClick={() => {
              setRows((rows) =>
                rows.flatMap((word, i) =>
                  i === split
                    ? [
                        { ...word, word: first, end: at, break_after: true },
                        { ...word, word: second, start: at },
                      ]
                    : [word],
                ),
              );
              setSplit(null);
            }}
          >
            Zastosuj ręczny podział
          </Button>
          <Button subtle onClick={() => setSplit(null)}>
            Anuluj podział
          </Button>
        </div>
      )}
      {rows.length > 20 && (
        <div className="button-row">
          <Button disabled={!page} onClick={() => setPage(page - 1)}>
            Poprzednie
          </Button>
          <span>
            {page + 1}/{pages}
          </span>
          <Button
            disabled={page >= pages - 1}
            onClick={() => setPage(page + 1)}
          >
            Następne
          </Button>
        </div>
      )}
      <Button
        primary
        disabled={!rows.length}
        onClick={() => onSave(rows.map((w) => ({ ...w, reviewed: true })))}
      >
        Zapisz napisy po sprawdzeniu
      </Button>
    </section>
  );
}
