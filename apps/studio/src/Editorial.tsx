import { useState } from "react";
import {
  Sparkles,
  Copy,
  Check,
  Plus,
  ArrowRight,
  BookOpen,
  LockKeyhole,
  FileText,
  Download,
  Trash2,
  Search,
} from "lucide-react";
import { useStudio } from "./context";
import { api, id, saveText } from "./api";
import {
  Button,
  CommitText,
  Empty,
  Field,
  IconButton,
  Modal,
  SectionHead,
} from "./components";
import type { Fact, Project } from "./types";
import { makeScene } from "./Generation";
import { fps, time } from "./timing";

const storyLabels: Record<string, string> = {
  central_question: "Centralne pytanie",
  hook: "Początek, który wciąga",
  signature_line: "Zdanie przewodnie",
  thesis: "Teza",
  complication: "Komplikacja",
  counterpoint: "Kontrargument",
  stakes_for_viewer: "Dlaczego widza to obchodzi?",
  payoff: "Odpowiedź i finał",
  open_question: "Co pozostaje niewiadomą?",
  sting: "Drzwi do następnego odcinka",
};
export function WriterTools({ kind }: { kind: "topics" | "story" | "script" }) {
  const s = useStudio(),
    p = s.project!;
  const [open, setOpen] = useState(false),
    [response, setResponse] = useState(""),
    [prompt, setPrompt] = useState(""),
    [busy, setBusy] = useState(false);
  async function copy() {
    const result = await api<{ prompt: string }>(
      `/projects/${p.id}/writer/${kind}/prompt`,
      {},
    );
    setPrompt(result.prompt);
    try {
      await navigator.clipboard.writeText(result.prompt);
      s.notify("Prompt skopiowano do schowka");
    } catch {
      s.notify("Prompt jest poniżej — możesz skopiować go ręcznie");
    }
  }
  async function generate() {
    setBusy(true);
    try {
      const result = await api<{ response: string }>(
        `/projects/${p.id}/writer/${kind}/generate`,
        {},
      );
      setResponse(result.response);
    } finally {
      setBusy(false);
    }
  }
  async function accept() {
    JSON.parse(response.replace(/^```(?:json)?\s*/, "").replace(/```$/, ""));
    await s.mutate((current) =>
      api<Project>(`/projects/${current.id}/writer/${kind}/import`, {
        expected_revision: current.revision,
        response,
      }),
    );
    setOpen(false);
    s.notify("Wczytano propozycję. Sprawdź jej treść i źródła.");
  }
  return (
    <>
      <Button icon={Sparkles} onClick={() => setOpen(true)}>
        Pracuj z AI
      </Button>
      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={
          kind === "topics"
            ? "Pomysły z AI"
            : kind === "story"
              ? "Ułóż historię z AI"
              : "Scenariusz z AI"
        }
        description="Otrzymujesz propozycję do sprawdzenia przed przyjęciem."
        wide
      >
        <div className="button-row">
          <Button icon={Copy} onClick={() => s.run(copy)}>
            Skopiuj prompt
          </Button>
          <Button
            primary
            icon={Sparkles}
            busy={busy}
            onClick={() => s.run(generate)}
          >
            Użyj połączonego AI
          </Button>
        </div>
        {prompt && (
          <details className="advanced">
            <summary>Prompt do ręcznego skopiowania</summary>
            <textarea rows={8} readOnly value={prompt} />
          </details>
        )}
        <Field label="Odpowiedź modelu — JSON">
          <textarea
            rows={12}
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Wygeneruj odpowiedź lub wklej ją ze swojego AI."
          />
        </Field>
        {kind === "script" && (
          <p className="small muted">
            Przyjęte ujęcia zostaną dodane na końcu scenariusza.
          </p>
        )}
        <Button
          primary
          icon={Check}
          disabled={!response.trim()}
          onClick={() => s.run(accept)}
        >
          Przyjmij propozycję
        </Button>
      </Modal>
    </>
  );
}

export function Idea() {
  const s = useStudio(),
    p = s.project!;
  return (
    <div className="page-content editorial-page">
      <SectionHead
        eyebrow="01 / POMYSŁ"
        title="Pomysł na film"
        description="Wybierz temat i pytanie, na które odpowie dokument."
      >
        <WriterTools kind="topics" />
      </SectionHead>
      <div className="editorial-two-columns">
        <section className="surface padded">
          <Field label="Tytuł filmu">
            <CommitText
              value={p.title}
              onCommit={(v) => s.run(() => s.patch({ title: v }))}
              placeholder="Tytuł Twojego dokumentu"
            />
          </Field>
          <Field label="Pytanie, na które odpowie film">
            <CommitText
              multiline
              rows={4}
              value={p.story.central_question || ""}
              onCommit={(v) =>
                s.run(() =>
                  s.patch((current) => ({
                    story: { ...current.story, central_question: v },
                  })),
                )
              }
            />
          </Field>
          <div className="two-fields">
            <Field label="Kanał">
              <CommitText
                value={p.channel}
                onCommit={(v) => s.run(() => s.patch({ channel: v }))}
              />
            </Field>
            <Field label="Język">
              <select
                value={p.language}
                onChange={(e) =>
                  s.run(() => s.patch({ language: e.target.value }))
                }
              >
                <option value="pl">Polski</option>
                <option value="en">English</option>
              </select>
            </Field>
          </div>
          <Button primary icon={ArrowRight} onClick={() => s.setPage("facts")}>
            Zacznij research
          </Button>
        </section>
        <section className="editorial-note">
          <div className="eyebrow">PAKIET DOCUMENTARY</div>
          <h2>
            Najpierw ciekawość.
            <br />
            Potem dowody.
          </h2>
          <p>
            Wyjaśnij jedno rzeczywiste zjawisko. Pokaż, jak działa, co je
            komplikuje i dlaczego dotyczy widza.
          </p>
          <div className="note-rule">
            Tytuł obiecuje odpowiedź.
            <br />
            Finał ją dostarcza.
          </div>
          <p className="small muted">
            Historia wcześniejszych propozycji: {p.topic_history.length}{" "}
            tytułów. Kolejny prompt wykluczy je z nowej listy.
          </p>
        </section>
      </div>
      {p.topics.length > 0 && (
        <div className="topic-grid">
          {p.topics.map((topic, index) => (
            <button
              className="topic-card surface"
              key={topic.title}
              onClick={() =>
                s.run(async () => {
                  await s.patch((current) => ({
                    title: topic.title,
                    story: {
                      ...current.story,
                      central_question: topic.central_question || "",
                    },
                  }));
                  s.notify("Wybrano temat");
                })
              }
            >
              <span className="eyebrow">
                {String(index + 1).padStart(2, "0")} / {topic.subject}
              </span>
              <h3>{topic.title}</h3>
              <p>{topic.central_question}</p>
              <span className="text-link">
                Wybierz temat <ArrowRight size={14} />
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function Facts() {
  const s = useStudio(),
    p = s.project!;
  const [filter, setFilter] = useState("");
  const facts = p.facts.filter(
    (f) =>
      !filter ||
      (f.claim + " " + f.source)
        .toLocaleLowerCase()
        .includes(filter.toLocaleLowerCase()),
  );
  function update(factId: string, changes: Partial<Fact>) {
    s.run(() =>
      s.patch((current) => ({
        facts: current.facts.map((f) =>
          f.id === factId ? { ...f, ...changes } : f,
        ),
      })),
    );
  }
  async function add() {
    const f: Fact = {
      id: id("fact_"),
      claim: "",
      source: "",
      url: "",
      page: "",
      status: "UNVERIFIED",
      note: "",
    };
    await s.patch((current) => ({ facts: [...current.facts, f] }));
  }
  return (
    <div className="page-content editorial-page">
      <SectionHead
        eyebrow="02 / DOWODY"
        title="Fakty i źródła"
        description="Sprawdzenie źródła jest decyzją redakcyjną. AI nie nadaje statusu faktu."
      >
        <Button icon={Search} onClick={() => s.setPage("sources")}>
          Szukaj źródeł
        </Button>
        <Button primary icon={Plus} onClick={() => s.run(add)}>
          Dodaj fakt
        </Button>
      </SectionHead>
      <div className="inline-summary">
        <span>
          <strong>{p.facts.length}</strong> faktów w banku
        </span>
        <span>
          <Check size={14} />
          {p.facts.filter((f) => f.status === "VERIFIED").length} sprawdzonych
        </span>
        <span>{p.sources.length} dokumentów źródłowych</span>
      </div>
      {p.facts.length > 0 && (
        <div className="small-search">
          <Search size={16} />
          <input
            aria-label="Filtruj fakty"
            placeholder="Znajdź twierdzenie lub źródło…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
      )}
      {!p.facts.length ? (
        <Empty
          icon={BookOpen}
          title="Zbuduj bank faktów"
          action={
            <Button icon={Plus} onClick={() => s.run(add)}>
              Dodaj pierwsze twierdzenie
            </Button>
          }
        >
          Zapisuj twierdzenia razem ze źródłem, adresem i stroną książki.
        </Empty>
      ) : (
        <div className="fact-list">
          {facts.map((fact, index) => (
            <section className="fact-card surface" key={fact.id}>
              <div className="fact-top">
                <span className="eyebrow">
                  FAKT {String(index + 1).padStart(2, "0")}
                </span>
                <select
                  className={"status-select " + fact.status.toLowerCase()}
                  aria-label="Stan weryfikacji"
                  value={fact.status}
                  onChange={(e) =>
                    update(fact.id, {
                      status: e.target.value as Fact["status"],
                    })
                  }
                >
                  <option value="UNVERIFIED">Do sprawdzenia</option>
                  <option value="VERIFIED">Sprawdzony</option>
                  <option value="DISPUTED">Sporny</option>
                </select>
                <IconButton
                  icon={Trash2}
                  label="Usuń fakt"
                  disabled={p.scenes.some((sc) =>
                    sc.fact_ids.includes(fact.id),
                  )}
                  onClick={() =>
                    s.run(() =>
                      s.patch((current) => ({
                        facts: current.facts.filter((f) => f.id !== fact.id),
                      })),
                    )
                  }
                />
              </div>
              <Field label="Twierdzenie">
                <CommitText
                  multiline
                  rows={2}
                  value={fact.claim}
                  onCommit={(v) => update(fact.id, { claim: v })}
                  placeholder="Co dokładnie potwierdza źródło?"
                />
              </Field>
              <div className="fact-source-fields">
                <Field label="Autor / publikacja">
                  <CommitText
                    value={fact.source}
                    onCommit={(v) => update(fact.id, { source: v })}
                    placeholder="Nazwa źródła lub wydanie książki"
                  />
                </Field>
                <Field label="Adres źródła">
                  <CommitText
                    value={fact.url}
                    onCommit={(v) => update(fact.id, { url: v })}
                    placeholder="https://…"
                  />
                </Field>
                <Field label="Strona / sekcja">
                  <CommitText
                    value={fact.page}
                    onCommit={(v) => update(fact.id, { page: v })}
                    placeholder="np. s. 42"
                  />
                </Field>
              </div>
              <details className="advanced">
                <summary>Notatka, spór i stanowiska</summary>
                <CommitText
                  multiline
                  rows={3}
                  value={fact.note}
                  onCommit={(v) => update(fact.id, { note: v })}
                />
              </details>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

export function Story() {
  const s = useStudio(),
    p = s.project!;
  return (
    <div className="page-content editorial-page">
      <SectionHead
        eyebrow="03 / HISTORIA"
        title="Karta historii"
        description="Zatwierdzona karta jest punktem odniesienia dla scenariusza."
      >
        <WriterTools kind="story" />
        <Button
          primary
          icon={LockKeyhole}
          disabled={p.story.status === "APPROVED"}
          onClick={() =>
            s.run(async () => {
              await s.mutate((current) =>
                api<Project>("/projects/" + current.id + "/story/approve", {
                  expected_revision: current.revision,
                }),
              );
              s.notify("Historia zatwierdzona");
            })
          }
        >
          {p.story.status === "APPROVED"
            ? "Historia zatwierdzona"
            : "Zatwierdź historię"}
        </Button>
      </SectionHead>
      <div
        className={`story-state ${p.story.status === "APPROVED" ? "approved" : ""}`}
      >
        <LockKeyhole size={18} />
        <div>
          <strong>
            {p.story.status === "APPROVED"
              ? "Kierunek opowieści jest zatwierdzony."
              : "Karta historii jest szkicem."}
          </strong>
          <p>Zmiana tezy, źródeł lub faktów wymaga ponownego zatwierdzenia.</p>
        </div>
        <span className="badge quiet">
          {p.facts.filter((f) => f.status === "VERIFIED").length} faktów
          sprawdzonych
        </span>
      </div>
      <div className="story-fields">
        {Object.entries(storyLabels).map(([key, label], index) => (
          <section
            className={`surface story-field ${key === "central_question" || key === "payoff" ? "emphasis" : ""}`}
            key={key}
          >
            <div className="story-field-number">
              {String(index + 1).padStart(2, "0")}
            </div>
            <Field label={label}>
              <CommitText
                value={p.story[key] || ""}
                multiline
                rows={key === "central_question" || key === "payoff" ? 3 : 2}
                onCommit={(v) =>
                  s.run(() =>
                    s.patch((current) => ({
                      story: { ...current.story, [key]: v },
                    })),
                  )
                }
              />
            </Field>
          </section>
        ))}
      </div>
    </div>
  );
}

export function Script() {
  const s = useStudio(),
    p = s.project!;
  const [open, setOpen] = useState(false),
    [text, setText] = useState("");
  const narration = p.scenes
      .map((sc) => sc.narration)
      .filter(Boolean)
      .join(" "),
    words = narration.split(/\s+/).filter(Boolean).length;
  function update(sceneId: string, value: string) {
    s.run(() =>
      s.patch((current) => ({
        scenes: current.scenes.map((sc) =>
          sc.id === sceneId ? { ...sc, narration: value } : sc,
        ),
      })),
    );
  }
  async function append() {
    const paragraphs = text
      .split(/\n\s*\n/)
      .map((t) => t.trim())
      .filter(Boolean);
    if (!paragraphs.length) return;
    let start = Math.max(0, ...p.scenes.map((sc) => sc.start + sc.duration));
    const next = paragraphs.map((value, index) => {
      const sc = makeScene(start);
      sc.title = "Scena " + (p.scenes.length + index + 1);
      sc.narration = value;
      sc.duration = Math.max(
        90,
        Math.round((value.split(/\s+/).length / 2.5) * fps(p)),
      );
      start += sc.duration;
      return sc;
    });
    await s.patch((current) => ({ scenes: [...current.scenes, ...next] }));
    setOpen(false);
    setText("");
    s.notify("Tekst podzielono na ujęcia z planowanym czasem");
  }
  return (
    <div className="page-content editorial-page">
      <SectionHead
        eyebrow="04 / NARRACJA"
        title="Scenariusz"
        description="Słowa lektora i plan obrazu mają swoje osobne miejsca."
      >
        <WriterTools kind="script" />
        <Button primary icon={Plus} onClick={() => setOpen(true)}>
          Dodaj tekst
        </Button>
      </SectionHead>
      <div className="script-summary">
        <span>
          <strong>{words}</strong> słów
        </span>
        <span>
          Około {Math.floor(words / 150)} min{" "}
          {Math.round(((words / 150) % 1) * 60)} s przy 150 słowach/min
        </span>
        <span>{p.scenes.length} ujęć</span>
        <div className="player-spacer" />
        <Button
          subtle
          icon={Copy}
          disabled={!narration}
          onClick={() =>
            s.run(async () => {
              await navigator.clipboard.writeText(narration);
              s.notify("Skopiowano tekst lektora");
            })
          }
        >
          Kopiuj lektora
        </Button>
        <Button
          subtle
          icon={Download}
          onClick={() => saveText("narracja.txt", narration)}
        >
          TXT
        </Button>
      </div>
      {!p.scenes.length ? (
        <Empty
          icon={FileText}
          title="Twoja historia zaczyna się tutaj"
          action={
            <Button primary icon={Plus} onClick={() => setOpen(true)}>
              Wklej tekst
            </Button>
          }
        >
          Oddziel sceny pustą linią. Aplikacja przygotuje ujęcia i szacowane
          czasy.
        </Empty>
      ) : (
        <div className="script-scenes">
          {p.scenes.map((scene, index) => (
            <section className="script-scene surface" key={scene.id}>
              <div className="script-scene-side">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <small>{time(scene.start, fps(p))}</small>
              </div>
              <div className="script-scene-content">
                <div className="inline-heading">
                  <h3>{scene.title}</h3>
                  {scene.locked && <LockKeyhole size={14} />}
                  <div className="player-spacer" />
                  <button
                    className="text-button"
                    onClick={() => {
                      s.setTargetScene(scene.id);
                      s.setPage("generation");
                    }}
                  >
                    Przygotuj obraz
                    <ArrowRight size={14} />
                  </button>
                </div>
                <CommitText
                  multiline
                  rows={Math.max(3, Math.ceil(scene.narration.length / 100))}
                  value={scene.narration}
                  onCommit={(v) => update(scene.id, v)}
                  disabled={scene.locked}
                  placeholder="Narracja tego ujęcia…"
                />
                {scene.fact_ids.length > 0 && (
                  <div className="fact-references">
                    {scene.fact_ids.map((fid) => (
                      <span key={fid}>{fid}</span>
                    ))}
                  </div>
                )}
              </div>
            </section>
          ))}
        </div>
      )}
      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Dodaj fragment scenariusza"
        description="Każdy akapit stanie się osobnym ujęciem."
        wide
      >
        <textarea
          rows={13}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Wklej narrację. Oddziel sceny pustą linią."
        />
        <div className="button-row">
          <Button
            primary
            icon={Plus}
            disabled={!text.trim()}
            onClick={() => s.run(append)}
          >
            Utwórz ujęcia z tekstu
          </Button>
        </div>
      </Modal>
    </div>
  );
}
