import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Plus,
  Sparkles,
  Copy,
  Check,
  Trash2,
  ChevronUp,
  ChevronDown,
  Layers3,
  Undo2,
  Redo2,
  TrendingUp,
  BookOpen,
} from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import {
  Button,
  CommitText,
  Empty,
  Field,
  IconButton,
  Modal,
  NumberField,
  SectionHead,
} from "./components";
import type { Project } from "./types";
import type {
  Assumptions,
  Baseline,
  Chapter,
  Development,
  FilmIdea,
  Forecast,
  Scores,
  StoryOption,
  Subchapter,
} from "./developmentTypes";
import {
  blankIdea,
  blankStory,
  blankChapter,
  blankSection,
  copyStory,
  scoreLabels,
} from "./developmentTypes";
import { BeatTools } from "./Production";

type AITarget = {
  kind: "ideas" | "stories" | "chapters" | "review";
  idea_id?: string;
  story_id?: string;
};
const names = {
  ideas: "Pomysły na film",
  stories: "Warianty historii",
  chapters: "Rozdziały i podrozdziały",
  review: "Ocena redakcyjna",
};
const number = (value: number) =>
  new Intl.NumberFormat("pl-PL", { maximumFractionDigits: 1 }).format(value);
const probability = (value: number) =>
  value < 1 ? "<1%" : value > 99 ? ">99%" : `${number(value)}%`;
const duration = (chapters: Chapter[]) =>
  chapters.reduce(
    (sum, c) => sum + c.sections.reduce((s, x) => s + x.seconds, 0),
    0,
  );
function Text({
  label,
  value,
  save,
  rows = 2,
  hint,
}: {
  label: string;
  value: string;
  save: (v: string) => void;
  rows?: number;
  hint?: string;
}) {
  return (
    <Field label={label} hint={hint}>
      <CommitText multiline rows={rows} value={value} onCommit={save} />
    </Field>
  );
}
function OptionalNumber({
  label,
  value,
  save,
  max = 100,
  step = 0.1,
}: {
  label: string;
  value: number | null;
  save: (v: number | null) => void;
  max?: number;
  step?: number;
}) {
  const [text, setText] = useState(String(value ?? ""));
  useEffect(() => setText(String(value ?? "")), [value]);
  return (
    <Field label={label}>
      <input
        type="number"
        min={0}
        max={max}
        step={step}
        value={text}
        placeholder="Brak danych"
        onChange={(e) => setText(e.target.value)}
        onBlur={() => {
          const v = text.trim() === "" ? null : Number(text);
          if (v === null || (Number.isFinite(v) && v >= 0 && v <= max)) {
            if (v !== value) save(v);
          } else setText(String(value ?? ""));
        }}
      />
    </Field>
  );
}
function move<T>(items: T[], index: number, delta: number) {
  const result = [...items];
  if (index < 0 || index >= items.length) return result;
  const target = index + delta;
  if (target >= 0 && target < result.length)
    [result[index], result[target]] = [result[target], result[index]];
  return result;
}

export default function IdeaWorkspace() {
  const s = useStudio(),
    p = s.project!,
    d = p.development;
  const [ideaId, setIdeaId] = useState<string | null>(null),
    [storyId, setStoryId] = useState<string | null>(null),
    [tab, setTab] = useState("story"),
    [ai, setAI] = useState<AITarget | null>(null),
    [own, setOwn] = useState(false),
    [title, setTitle] = useState(""),
    [question, setQuestion] = useState(""),
    [forecasts, setForecasts] = useState<Record<string, Forecast>>({}),
    [history, setHistory] = useState({ undo: 0, redo: 0 }),
    [confirm, setConfirm] = useState<null | {
      title: string;
      description: string;
      action: () => Promise<unknown>;
    }>(null);
  useEffect(() => {
    let active = true;
    Promise.all([
      api<Record<string, Forecast>>(`/projects/${p.id}/development/forecasts`),
      api<{ undo: number; redo: number }>(`/projects/${p.id}/history`),
    ])
      .then(([r, h]) => {
        if (active) {
          setForecasts(r);
          setHistory(h);
        }
      })
      .catch((e) => {
        if (active) s.notify(String(e), true);
      });
    return () => {
      active = false;
    };
  }, [p.id, p.revision]);
  const idea = d.ideas.find((i) => i.id === ideaId),
    story = idea?.stories.find((x) => x.id === storyId);
  useEffect(() => {
    document.querySelector("main")?.scrollTo(0, 0);
  }, [ideaId, storyId, tab]);
  function edit(change: (value: Development) => void) {
    s.run(() =>
      s.patch((current) => {
        const value = structuredClone(current.development);
        change(value);
        return { development: value };
      }),
    );
  }
  function changeIdea(
    changes: Partial<FilmIdea> | ((value: FilmIdea) => Partial<FilmIdea>),
  ) {
    edit((value) => {
      const item = value.ideas.find((x) => x.id === ideaId);
      if (item)
        Object.assign(
          item,
          typeof changes === "function" ? changes(item) : changes,
        );
    });
  }
  function changeStory(
    changes:
      Partial<StoryOption> | ((value: StoryOption) => Partial<StoryOption>),
  ) {
    edit((value) => {
      const item = value.ideas
        .find((x) => x.id === ideaId)
        ?.stories.find((x) => x.id === storyId);
      if (item)
        Object.assign(
          item,
          typeof changes === "function" ? changes(item) : changes,
        );
    });
  }
  async function choose(idea: FilmIdea, story?: StoryOption) {
    await s.mutate((current) =>
      api<Project>(`/projects/${current.id}/development/select`, {
        expected_revision: current.revision,
        idea_id: idea.id,
        story_id: story?.id,
      }),
    );
    s.notify(
      story
        ? "Wybrano kierunek historii. Karta czeka na research i zatwierdzenie."
        : "Wybrano temat filmu",
    );
  }
  function askChoose(idea: FilmIdea, story?: StoryOption) {
    setConfirm({
      title: story ? "Wybrać tę historię?" : "Ustawić temat filmu?",
      description:
        "Tytuł i karta historii przyjmą ten kierunek. Dotychczasowy montaż i źródła zostaną zachowane, a historia będzie wymagać ponownego sprawdzenia. Pozostałe warianty nadal będą dostępne.",
      action: () => choose(idea, story),
    });
  }
  function removeIdea(idea: FilmIdea) {
    setConfirm({
      title: "Usunąć pomysł z kolekcji?",
      description: `„${idea.title}” i jego warianty znikną z listy. Bieżący film i jego montaż pozostaną w projekcie.`,
      action: async () => {
        await s.patch((current) => {
          const dev = structuredClone(current.development);
          dev.ideas = dev.ideas.filter((x) => x.id !== idea.id);
          if (dev.selected_idea_id === idea.id) {
            dev.selected_idea_id = null;
            dev.selected_story_id = null;
            dev.selected_story_hash = "";
          }
          return { development: dev };
        });
        setIdeaId(null);
        setStoryId(null);
      },
    });
  }
  const launch = (kind: AITarget["kind"]) =>
    setAI({ kind, idea_id: idea?.id, story_id: story?.id });
  return (
    <div className="page-content idea-workspace">
      <div className="idea-breadcrumbs">
        <button
          onClick={() => {
            setIdeaId(null);
            setStoryId(null);
          }}
        >
          Pomysły na film
        </button>
        {idea && (
          <>
            <span>/</span>
            <button onClick={() => setStoryId(null)}>{idea.title}</button>
          </>
        )}
        {story && (
          <>
            <span>/</span>
            <span>{story.title}</span>
          </>
        )}
      </div>
      <SectionHead
        eyebrow={
          story
            ? "01 / KIERUNEK HISTORII"
            : idea
              ? "01 / HISTORIE TEGO FILMU"
              : "01 / ROZWÓJ FILMU"
        }
        title={
          story ? story.title : idea ? idea.title : "Od tematu do historii"
        }
        description={
          story
            ? "Sprawdź obietnicę, konstrukcję i potencjał, zanim zaczniesz pisać narrację."
            : idea
              ? "Jeden temat może stać się kilkoma różnymi filmami. Wybierz sposób opowiedzenia tej historii."
              : "Określ obszar poszukiwań. Zbieraj pomysły własne i AI, a każdy rozwijaj osobno."
        }
      >
        <IconButton
          icon={Undo2}
          label="Cofnij zmianę pomysłu"
          disabled={!history.undo || s.saving}
          onClick={() =>
            s.run(() =>
              s.mutate((current) =>
                api<Project>(`/projects/${current.id}/history/undo`, {
                  expected_revision: current.revision,
                }),
              ),
            )
          }
        />
        <IconButton
          icon={Redo2}
          label="Ponów zmianę pomysłu"
          disabled={!history.redo || s.saving}
          onClick={() =>
            s.run(() =>
              s.mutate((current) =>
                api<Project>(`/projects/${current.id}/history/redo`, {
                  expected_revision: current.revision,
                }),
              ),
            )
          }
        />
        {idea && (
          <Button
            icon={ArrowLeft}
            onClick={() => (story ? setStoryId(null) : setIdeaId(null))}
          >
            {story ? "Warianty historii" : "Wszystkie pomysły"}
          </Button>
        )}
        {!idea && (
          <Button primary icon={Sparkles} onClick={() => launch("ideas")}>
            Zaproponuj tematy
          </Button>
        )}
        {idea && !story && (
          <Button primary icon={Sparkles} onClick={() => launch("stories")}>
            Zaproponuj historie
          </Button>
        )}
        {story && (
          <Button primary icon={Check} onClick={() => askChoose(idea!, story)}>
            Wybierz tę historię
          </Button>
        )}
      </SectionHead>
      {!idea ? (
        <>
          <div className="idea-intake-grid">
            <section className="surface tool-panel">
              <div className="inline-heading">
                <span className="eyebrow">BRIEF REDAKCYJNY</span>
                <span className="badge quiet">Zapis automatyczny</span>
              </div>
              <h2>W jakim kierunku szukamy?</h2>
              <Text
                label="Obszar, temat lub zjawisko"
                value={d.topic_area}
                save={(v) =>
                  edit((x) => {
                    x.topic_area = v;
                  })
                }
              />
              <div className="two-fields">
                <Text
                  label="Dla kogo jest ten film?"
                  value={d.audience}
                  save={(v) =>
                    edit((x) => {
                      x.audience = v;
                    })
                  }
                />
                <Text
                  label="Co widz ma zrozumieć lub poczuć?"
                  value={d.viewer_promise}
                  save={(v) =>
                    edit((x) => {
                      x.viewer_promise = v;
                    })
                  }
                />
              </div>
              <div className="two-fields">
                <NumberField
                  label="Planowana długość (min)"
                  value={d.target_minutes}
                  min={1}
                  max={360}
                  step={1}
                  onCommit={(v) =>
                    edit((x) => {
                      x.target_minutes = v;
                    })
                  }
                />
                <Field label="Język filmu">
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
              <Text
                label="Styl, filmy i twórcy referencyjni"
                value={d.references}
                save={(v) =>
                  edit((x) => {
                    x.references = v;
                  })
                }
              />
              <Text
                label="Materiały, ograniczenia i czego unikać"
                value={d.constraints}
                save={(v) =>
                  edit((x) => {
                    x.constraints = v;
                  })
                }
              />
            </section>
            <section className="surface tool-panel idea-own">
              <span className="eyebrow">TWÓJ PUNKT WIDZENIA</span>
              <h2>Masz już konkretny pomysł?</h2>
              <p>
                Zapisz go jako osobny kafelek. Otwórz temat, przygotuj kilka
                historii i porównaj je przed wyborem.
              </p>
              <Button primary icon={Plus} onClick={() => setOwn(true)}>
                Dodaj własny pomysł
              </Button>
              <div className="idea-current">
                <small>Film w produkcji</small>
                <strong>{p.title}</strong>
                <Button
                  subtle
                  icon={ArrowRight}
                  onClick={() => s.setPage("facts")}
                >
                  Przejdź do researchu
                </Button>
              </div>
              <div className="idea-workflow">
                <span>Temat</span>
                <ArrowRight size={14} />
                <span>Historie</span>
                <ArrowRight size={14} />
                <span>Rozdziały</span>
                <ArrowRight size={14} />
                <span>Scenariusz</span>
              </div>
            </section>
          </div>
          <div className="idea-collection-head">
            <div>
              <span className="eyebrow">KOLEKCJA TEMATÓW</span>
              <h2>
                Pomysły na film{" "}
                <span className="badge quiet">{d.ideas.length}</span>
              </h2>
            </div>
            <Button icon={Plus} onClick={() => setOwn(true)}>
              Własny pomysł
            </Button>
          </div>
          {d.ideas.length ? (
            <div className="idea-card-grid">
              {d.ideas.map((item, index) => (
                <article
                  className={`surface idea-card ${d.selected_idea_id === item.id ? "chosen" : ""}`}
                  key={item.id}
                >
                  <button
                    className="idea-card-open"
                    onClick={() => {
                      setIdeaId(item.id);
                      setStoryId(null);
                    }}
                  >
                    <span className="eyebrow">
                      {String(index + 1).padStart(2, "0")} /{" "}
                      {item.origin === "ai"
                        ? "PROPOZYCJA AI"
                        : item.origin === "legacy"
                          ? "ZAPISANY TEMAT"
                          : "TWÓJ POMYSŁ"}
                    </span>
                    <h3>{item.title}</h3>
                    <p>
                      {item.question ||
                        item.angle ||
                        "Otwórz i nadaj tematowi własny punkt widzenia."}
                    </p>
                    <span className="text-link">
                      {item.stories.length} wariantów historii{" "}
                      <ArrowRight size={15} />
                    </span>
                  </button>
                  <footer>
                    {d.selected_idea_id === item.id ? (
                      <span className="badge success">Temat w produkcji</span>
                    ) : (
                      <span className="badge quiet">Do rozwinięcia</span>
                    )}
                    <IconButton
                      icon={Trash2}
                      label={`Usuń pomysł: ${item.title}`}
                      onClick={() => removeIdea(item)}
                    />
                  </footer>
                </article>
              ))}
            </div>
          ) : (
            <Empty title="Pierwszy dobry temat zaczyna kolekcję">
              Dodaj własny pomysł albo przygotuj propozycje z AI na podstawie
              briefu.
            </Empty>
          )}
          <BaselineEditor
            baseline={d.baseline}
            save={(change) =>
              edit((x) => {
                x.baseline = { ...x.baseline, ...change };
              })
            }
          />
        </>
      ) : !story ? (
        <>
          <section className="surface tool-panel">
            <div className="two-fields">
              <Field label="Temat / roboczy tytuł">
                <CommitText
                  value={idea.title}
                  onCommit={(v) => changeIdea({ title: v })}
                />
              </Field>
              <Field label="Główne pytanie">
                <CommitText
                  value={idea.question}
                  onCommit={(v) => changeIdea({ question: v })}
                />
              </Field>
            </div>
            <Text
              label="Własny punkt widzenia"
              value={idea.angle}
              save={(v) => changeIdea({ angle: v })}
            />
            <Text
              label="Notatki i tropy do sprawdzenia"
              value={idea.notes}
              save={(v) => changeIdea({ notes: v })}
            />
            <div className="button-row">
              <Button icon={Check} onClick={() => askChoose(idea)}>
                Ustaw temat filmu
              </Button>
              <Button
                icon={Plus}
                onClick={() => {
                  const value = blankStory();
                  changeIdea((current) => ({
                    stories: [...current.stories, value],
                  }));
                  setStoryId(value.id);
                  setTab("story");
                }}
              >
                Dodaj własną historię
              </Button>
            </div>
          </section>
          <div className="idea-collection-head">
            <div>
              <span className="eyebrow">ALTERNATYWNE KONSTRUKCJE</span>
              <h2>Jak opowiedzieć ten film?</h2>
            </div>
            <span className="muted">{idea.stories.length} wariantów</span>
          </div>
          {idea.stories.length ? (
            <>
              <div className="idea-card-grid">
                {idea.stories.map((item, index) => (
                  <article
                    className={`surface idea-card ${d.selected_story_id === item.id ? "chosen" : ""}`}
                    key={item.id}
                  >
                    <button
                      className="idea-card-open"
                      onClick={() => {
                        setStoryId(item.id);
                        setTab("story");
                      }}
                    >
                      <span className="eyebrow">
                        WARIANT {String(index + 1).padStart(2, "0")} /{" "}
                        {item.origin === "ai" ? "AI" : "WŁASNY"}
                      </span>
                      <h3>{item.title}</h3>
                      <p>
                        {item.synopsis ||
                          item.central_question ||
                          "Rozwiń własny zarys historii."}
                      </p>
                      <div className="story-card-metrics">
                        <span>
                          Redakcja{" "}
                          <strong>
                            {forecasts[item.id]?.editorial_score ?? "—"}/100
                          </strong>
                        </span>
                        <span>
                          Evergreen <strong>{item.scores.evergreen}/100</strong>
                        </span>
                        <span>
                          Plan <strong>{item.chapters.length} rozdz.</strong>
                        </span>
                      </div>
                      <span className="text-link">
                        Rozwiń historię <ArrowRight size={15} />
                      </span>
                    </button>
                    {d.selected_story_id === item.id && (
                      <footer>
                        <span
                          className={`badge ${forecasts[item.id]?.selected_current ? "success" : "warning"}`}
                        >
                          {forecasts[item.id]?.selected_current
                            ? "Wybrany kierunek"
                            : "Zmieniono szkic po wyborze"}
                        </span>
                      </footer>
                    )}
                  </article>
                ))}
              </div>
              <Comparison
                stories={idea.stories}
                forecasts={forecasts}
                open={(value) => {
                  setStoryId(value);
                  setTab("evaluation");
                }}
              />
            </>
          ) : (
            <Empty title="Najpierw kilka historii, potem decyzja">
              Przygotuj alternatywne otwarcia, punkty zwrotne i finały. AI doda
              propozycje do kolekcji; nie wybierze za Ciebie.
            </Empty>
          )}
        </>
      ) : (
        <>
          <div
            className="filter-pills idea-tabs"
            role="group"
            aria-label="Rozwijanie historii"
          >
            {[
              ["story", "Zarys historii"],
              ["chapters", "Rozdziały i podrozdziały"],
              ["evaluation", "Potencjał i metryki"],
            ].map(([value, label]) => (
              <button
                className={tab === value ? "active" : ""}
                key={value}
                onClick={() => setTab(value)}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="idea-story-status">
            <span
              className={`badge ${forecasts[story.id]?.selected_current ? "success" : "quiet"}`}
            >
              {forecasts[story.id]?.selected_current
                ? "Wybrany kierunek filmu"
                : "Wariant roboczy"}
            </span>
            <span>
              {story.chapters.length} rozdziałów ·{" "}
              {number(duration(story.chapters) / 60)} min planu / cel{" "}
              {d.target_minutes} min
            </span>
            <div className="player-spacer" />
            <Button
              subtle
              icon={Copy}
              onClick={() => {
                const value = copyStory(story);
                changeIdea((current) => ({
                  stories: [...current.stories, value],
                }));
                setStoryId(value.id);
              }}
            >
              Kopia wariantu
            </Button>
            <IconButton
              icon={Trash2}
              label="Usuń wariant historii"
              onClick={() =>
                setConfirm({
                  title: "Usunąć wariant historii?",
                  description:
                    "Wariant zniknie z tej kolekcji. Już przeniesiony scenariusz i montaż pozostaną w projekcie.",
                  action: async () => {
                    await s.patch((current) => {
                      const value = structuredClone(current.development);
                      const target = value.ideas.find((i) => i.id === idea.id)!;
                      target.stories = target.stories.filter(
                        (x) => x.id !== story.id,
                      );
                      if (value.selected_story_id === story.id) {
                        value.selected_story_id = null;
                        value.selected_story_hash = "";
                      }
                      return { development: value };
                    });
                    setStoryId(null);
                  },
                })
              }
            />
          </div>
          {tab === "story" ? (
            <div className="idea-intake-grid">
              <section className="surface tool-panel">
                <Field label="Nazwa wariantu historii">
                  <CommitText
                    value={story.title}
                    onCommit={(v) => changeStory({ title: v })}
                  />
                </Field>
                <Text
                  label="Ogólny zarys historii"
                  rows={6}
                  value={story.synopsis}
                  save={(v) => changeStory({ synopsis: v })}
                />
                <Text
                  label="Centralne pytanie"
                  value={story.central_question}
                  save={(v) => changeStory({ central_question: v })}
                />
                <Text
                  label="Pierwsze 30 sekund — otwarcie i obietnica"
                  rows={4}
                  value={story.hook}
                  save={(v) => changeStory({ hook: v })}
                />
                <div className="two-fields">
                  <Text
                    label="Stawka dla widza"
                    value={story.stakes}
                    save={(v) => changeStory({ stakes: v })}
                  />
                  <Text
                    label="Payoff — odpowiedź w finale"
                    value={story.payoff}
                    save={(v) => changeStory({ payoff: v })}
                  />
                </div>
                <Button
                  primary
                  icon={Layers3}
                  onClick={() => setTab("chapters")}
                >
                  Rozwiń w rozdziały
                </Button>
              </section>
              <section className="surface tool-panel">
                <span className="eyebrow">PERSPEKTYWA WYDAWCY</span>
                <h2>Dlaczego ktoś ma kliknąć i zostać?</h2>
                <Text
                  label="Propozycja tytułu publikacji"
                  value={story.title_pitch}
                  save={(v) => changeStory({ title_pitch: v })}
                />
                <Text
                  label="Pomysł na miniaturę"
                  value={story.thumbnail}
                  save={(v) => changeStory({ thumbnail: v })}
                />
                <Text
                  label="Co może utrzymać zainteresowanie po premierze?"
                  value={story.evergreen_reason}
                  save={(v) => changeStory({ evergreen_reason: v })}
                />
                <Text
                  label="Ryzyka spalenia tematu — po jednym w wierszu"
                  value={story.risks.join("\n")}
                  save={(v) =>
                    changeStory({ risks: v.split("\n").filter(Boolean) })
                  }
                />
                <Text
                  label="Luki w dowodach / materiały do zdobycia"
                  value={story.evidence_gaps.join("\n")}
                  save={(v) =>
                    changeStory({
                      evidence_gaps: v.split("\n").filter(Boolean),
                    })
                  }
                />
                <Button
                  icon={TrendingUp}
                  onClick={() => {
                    setTab("evaluation");
                    launch("review");
                  }}
                >
                  Oceń kierunek z AI
                </Button>
              </section>
            </div>
          ) : tab === "chapters" ? (
            <>
              <div className="idea-collection-head">
                <div>
                  <h2>Plan, który prowadzi do finału</h2>
                  <p className="muted">
                    Cel, zwrot, retencja i dowody dla każdego podrozdziału.
                    Kolejność możesz zmieniać.
                  </p>
                </div>
                <div className="button-row">
                  <Button icon={Sparkles} onClick={() => launch("chapters")}>
                    Zaproponuj strukturę
                  </Button>
                  <Button
                    icon={Plus}
                    onClick={() =>
                      changeStory((current) => ({
                        chapters: [...current.chapters, blankChapter()],
                      }))
                    }
                  >
                    Dodaj rozdział
                  </Button>
                </div>
              </div>
              <ChapterEditor
                chapters={story.chapters}
                save={(update) =>
                  changeStory((current) => ({
                    chapters: update(current.chapters),
                  }))
                }
              />
              <section className="surface tool-panel idea-handoff">
                <div>
                  <h2>Przejdź od planu do scenariusza</h2>
                  <p>
                    Każdy podrozdział stanie się fragmentem scenariusza.
                    Wcześniejszy pusty plan zastąpi wybrana struktura. Już
                    napisanego tekstu ani ujęć nie zastąpimy. Po rozwinięciu
                    scenariusza nowe kierunki przygotowuj w kopii projektu.
                  </p>
                </div>
                <Button
                  primary
                  icon={ArrowRight}
                  disabled={
                    !story.applied_hash &&
                    (!forecasts[story.id]?.selected_current ||
                      !duration(story.chapters) ||
                      s.saving)
                  }
                  onClick={() =>
                    s.run(async () => {
                      if (story.applied_hash) {
                        s.setPage("script");
                        return;
                      }
                      await s.mutate((current) =>
                        api<Project>(
                          `/projects/${current.id}/development/to-script`,
                          {
                            expected_revision: current.revision,
                            idea_id: idea.id,
                            story_id: story.id,
                          },
                        ),
                      );
                      s.setPage("script");
                      s.notify("Przeniesiono plan do scenariusza");
                    })
                  }
                >
                  {story.applied_hash
                    ? "Otwórz scenariusz"
                    : "Przenieś plan do scenariusza"}
                </Button>
                {!forecasts[story.id]?.selected_current && (
                  <p className="muted">
                    Najpierw wybierz aktualną historię jako kierunek filmu.
                  </p>
                )}
              </section>
            </>
          ) : (
            <>
              <ForecastPanel
                value={forecasts[story.id]}
                baseline={d.baseline}
              />
              <section className="surface tool-panel">
                <div className="inline-heading">
                  <h2>Ocena redakcyjna, nie dane Analytics</h2>
                  <div className="player-spacer" />
                  <Button icon={Sparkles} onClick={() => launch("review")}>
                    Oceń z AI
                  </Button>
                </div>
                <div className="score-grid">
                  {(Object.keys(scoreLabels) as (keyof Scores)[]).map((key) => (
                    <NumberField
                      key={key}
                      label={scoreLabels[key] + " / 100"}
                      value={story.scores[key]}
                      max={100}
                      step={1}
                      onCommit={(v) =>
                        changeStory((current) => ({
                          scores: { ...current.scores, [key]: v },
                        }))
                      }
                    />
                  ))}
                </div>
                <Text
                  label="Uzasadnienie i rekomendacja redakcyjna"
                  rows={4}
                  value={story.rationale}
                  save={(v) => changeStory({ rationale: v })}
                />
                <Text
                  label="Dlaczego temat może działać długoterminowo?"
                  value={story.evergreen_reason}
                  save={(v) => changeStory({ evergreen_reason: v })}
                />
              </section>
              <section className="surface tool-panel">
                <h2>Założenia scenariuszy</h2>
                <p className="muted">
                  To edytowalne hipotezy. Mnożniki dotyczą całkowitych
                  wyświetleń typowego filmu kanału. Nie wyliczamy ich
                  automatycznie z CTR.
                </p>
                <div className="score-grid">
                  {[
                    ["reach_low", "Ostrożny ×"],
                    ["reach_base", "Bazowy ×"],
                    ["reach_high", "Optymistyczny ×"],
                    ["ctr_delta", "Zmiana CTR (pp)"],
                    ["retention_delta", "Zmiana retencji (pp)"],
                  ].map(([key, label]) => (
                    <NumberField
                      key={key}
                      label={label}
                      value={
                        story.assumptions[key as keyof Assumptions] as number
                      }
                      min={
                        key === "retention_delta"
                          ? -50
                          : key === "ctr_delta"
                            ? -20
                            : 0.05
                      }
                      max={
                        key === "retention_delta"
                          ? 50
                          : key === "ctr_delta"
                            ? 20
                            : 100
                      }
                      step={0.1}
                      onCommit={(v) =>
                        changeStory((current) => ({
                          assumptions: { ...current.assumptions, [key]: v },
                        }))
                      }
                    />
                  ))}
                </div>
                <Text
                  label="Na czym opierasz te założenia?"
                  value={story.assumptions.reason}
                  save={(v) =>
                    changeStory((current) => ({
                      assumptions: { ...current.assumptions, reason: v },
                    }))
                  }
                />
              </section>
              <BaselineEditor
                baseline={d.baseline}
                save={(change) =>
                  edit((x) => {
                    x.baseline = { ...x.baseline, ...change };
                  })
                }
              />
            </>
          )}
        </>
      )}
      <Modal
        open={own}
        onClose={() => setOwn(false)}
        title="Własny pomysł na film"
        description="Dodasz osobny temat do kolekcji, bez zmiany filmu w produkcji."
      >
        <Field label="Roboczy tytuł / temat">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </Field>
        <Field label="Pytanie, które ma przyciągnąć widza">
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </Field>
        <Button
          primary
          icon={Plus}
          disabled={!title.trim()}
          onClick={() =>
            s.run(async () => {
              const value = { ...blankIdea(), title: title.trim(), question };
              await s.patch((current) => ({
                development: {
                  ...current.development,
                  ideas: [...current.development.ideas, value],
                },
              }));
              setOwn(false);
              setTitle("");
              setQuestion("");
              s.notify("Dodano pomysł do kolekcji");
            })
          }
        >
          Dodaj kafelek
        </Button>
      </Modal>
      <Modal
        open={!!confirm}
        onClose={() => setConfirm(null)}
        title={confirm?.title || "Potwierdź"}
        description={confirm?.description}
      >
        <Button
          primary
          onClick={() =>
            s.run(async () => {
              await confirm?.action();
              setConfirm(null);
            })
          }
        >
          Potwierdź
        </Button>
      </Modal>
      {ai && <IdeaAssistant target={ai} close={() => setAI(null)} />}
    </div>
  );
}

function BaselineEditor({
  baseline: b,
  save,
}: {
  baseline: Baseline;
  save: (change: Partial<Baseline>) => void;
}) {
  const s = useStudio();
  return (
    <details className="surface tool-panel baseline-editor">
      <summary>
        <TrendingUp size={17} /> Punkt odniesienia kanału{" "}
        <span className="badge quiet">{b.views_30d.length} filmów</span>
      </summary>
      <p>
        Wpisz wyniki porównywalnych filmów po pierwszych 30 dniach. Bez nich nie
        pokazujemy liczby wyświetleń ani procentowych szans.
      </p>
      <div className="score-grid">
        <OptionalNumber
          label="Typowe wyświetlenia po 30 dniach"
          value={b.typical_views_30d}
          max={1e12}
          step={1}
          save={(v) => save({ typical_views_30d: v })}
        />
        <OptionalNumber
          label="CTR kanału (%)"
          value={b.ctr}
          save={(v) => save({ ctr: v })}
        />
        <OptionalNumber
          label="Średni obejrzany procent filmu (%)"
          value={b.retention}
          save={(v) => save({ retention: v })}
        />
        <OptionalNumber
          label="Długość porównywanych filmów (min)"
          value={b.comparable_minutes}
          max={360}
          save={(v) => save({ comparable_minutes: v || null })}
        />
        <NumberField
          label="Sukces: × typowy wynik"
          value={b.success_multiple}
          min={1}
          max={100}
          onCommit={(v) => save({ success_multiple: v })}
        />
        <NumberField
          label="Wiral: × typowy wynik"
          value={b.viral_multiple}
          min={1}
          max={1000}
          onCommit={(v) => save({ viral_multiple: v })}
        />
      </div>
      <Text
        label="Wyświetlenia porównywalnych filmów po 30 dniach — jedna liczba na wiersz"
        rows={5}
        value={b.views_30d.join("\n")}
        save={(v) =>
          s.run(async () => {
            const values = v
              .split(/\r?\n/)
              .map((x) => x.replace(/\s/g, ""))
              .filter(Boolean);
            if (values.some((x) => !/^\d+$/.test(x)) || values.length > 200)
              throw new Error(
                "Wpisz najwyżej 200 całkowitych liczb, po jednej na wiersz, bez przecinków.",
              );
            save({ views_30d: values.map(Number) });
          })
        }
      />
      <Text
        label="Źródło danych, okres i porównywalność filmów"
        value={b.evidence}
        save={(v) => save({ evidence: v })}
      />
      <p className="small muted">
        Przy co najmniej 10 wynikach pojawi się eksperymentalna symulacja
        prawdopodobieństwa. Nadal wymaga kalibracji na rzeczywistych premierach.
        CTR dotyczy rejestrowanych impresji; nie wszystkich wyświetleń. Retencję
        porównuj przy podobnej długości filmów.{" "}
        <a
          href="https://support.google.com/youtube/answer/7628154"
          target="_blank"
          rel="noreferrer"
        >
          CTR według YouTube
        </a>{" "}
        ·{" "}
        <a
          href="https://support.google.com/youtube/answer/9314415"
          target="_blank"
          rel="noreferrer"
        >
          Retencja według YouTube
        </a>
      </p>
    </details>
  );
}

function ForecastPanel({
  value: f,
  baseline: b,
}: {
  value: Forecast | undefined;
  baseline: Baseline;
}) {
  const range = (v: Forecast["ctr"], suffix = "") =>
    v ? `${number(v.low)}–${number(v.high)}${suffix}` : "Brak danych kanału";
  return (
    <section className="surface tool-panel forecast-panel">
      <div className="inline-heading">
        <span className="eyebrow">SCENARIUSZ DECYZYJNY</span>
        <span className="badge warning">
          Pewność: niska · model bez kalibracji
        </span>
      </div>
      <div className="forecast-grid">
        <article>
          <small>Wyświetlenia · pierwsze 30 dni</small>
          <strong>{range(f?.views_30d ?? null)}</strong>
          <span>
            {f?.views_30d
              ? `Bazowy scenariusz: ${number(f.views_30d.base)}`
              : "Uzupełnij punkt odniesienia poniżej."}
          </span>
        </article>
        <article>
          <small>Szacowany CTR</small>
          <strong>{range(f?.ctr ?? null, "%")}</strong>
          <span>Scenariusz wokół CTR kanału</span>
        </article>
        <article>
          <small>Retencja · średni obejrzany %</small>
          <strong>{range(f?.retention ?? null, "%")}</strong>
          <span>Nie jest to retencja po 30 sekundach</span>
        </article>
        <article>
          <small>Long-tail / evergreen</small>
          <strong>{f ? `${f.evergreen}/100` : "—"}</strong>
          <span>Subiektywna ocena redakcyjna</span>
        </article>
      </div>
      <div className="probability-row">
        <div>
          <small>
            Szansa sukcesu · ≥{number(b.success_multiple)}× typowy wynik
          </small>
          <strong>
            {f?.probabilities
              ? probability(f.probabilities.success)
              : "Za mało danych"}
          </strong>
        </div>
        <div>
          <small>
            Szansa wiralu · ≥{number(b.viral_multiple)}× typowy wynik
          </small>
          <strong>
            {f?.probabilities
              ? probability(f.probabilities.viral)
              : "Za mało danych"}
          </strong>
        </div>
        <p>
          {f?.probabilities
            ? `Eksperymentalna symulacja z ${f.sample_size} filmów. Model wymaga kalibracji. Zmiana założeń zmienia wynik.`
            : "Potrzeba co najmniej 10 wyników porównywalnych filmów i dodatniego punktu odniesienia."}
        </p>
      </div>
      <p className="small muted">
        Przedziały są scenariuszami wynikającymi z Twoich założeń, nie
        przedziałami ufności. CTR i retencja nie gwarantują rekomendacji ani
        określonego zasięgu.
      </p>
    </section>
  );
}

function Comparison({
  stories,
  forecasts,
  open,
}: {
  stories: StoryOption[];
  forecasts: Record<string, Forecast>;
  open: (id: string) => void;
}) {
  return (
    <section className="surface tool-panel idea-comparison">
      <h2>Porównaj kierunki przed decyzją</h2>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Historia</th>
              <th>Redakcja</th>
              <th>30 dni · scenariusz bazowy</th>
              <th>Sukces · symulacja</th>
              <th>Wiral · symulacja</th>
              <th>CTR</th>
              <th>Retencja</th>
              <th>Evergreen</th>
            </tr>
          </thead>
          <tbody>
            {stories.map((story) => {
              const f = forecasts[story.id];
              return (
                <tr key={story.id}>
                  <th>
                    <button
                      className="text-button"
                      onClick={() => open(story.id)}
                    >
                      {story.title}
                    </button>
                  </th>
                  <td>{f?.editorial_score ?? "—"}/100</td>
                  <td>
                    {f?.views_30d ? number(f.views_30d.base) : "Brak danych"}
                  </td>
                  <td>
                    {f?.probabilities
                      ? probability(f.probabilities.success)
                      : "Brak danych"}
                  </td>
                  <td>
                    {f?.probabilities
                      ? probability(f.probabilities.viral)
                      : "Brak danych"}
                  </td>
                  <td>
                    {f?.ctr
                      ? `${number(f.ctr.low)}–${number(f.ctr.high)}%`
                      : "—"}
                  </td>
                  <td>
                    {f?.retention
                      ? `${number(f.retention.low)}–${number(f.retention.high)}%`
                      : "—"}
                  </td>
                  <td>{story.scores.evergreen}/100</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="small muted">
        Oceny są robocze, a prognozy warunkowe. Symulacja używa progów kanału i
        wymaga kalibracji. Zestaw wyniki z uzasadnieniem, lukami w dowodach i
        ryzykiem każdego wariantu.
      </p>
    </section>
  );
}

function ChapterEditor({
  chapters,
  save,
}: {
  chapters: Chapter[];
  save: (update: (values: Chapter[]) => Chapter[]) => void;
}) {
  const s = useStudio(),
    p = s.project!;
  const change = (
    index: number,
    values: Partial<Chapter> | ((chapter: Chapter) => Partial<Chapter>),
  ) =>
    save((current) =>
      current.map((c) =>
        c.id === chapters[index].id
          ? { ...c, ...(typeof values === "function" ? values(c) : values) }
          : c,
      ),
    );
  return (
    <div className="chapter-list">
      {chapters.map((chapter, index) => (
        <section key={chapter.id} className="surface tool-panel chapter-card">
          <div className="inline-heading">
            <span className="chapter-number">
              {String(index + 1).padStart(2, "0")}
            </span>
            <Field label={`Tytuł rozdziału ${index + 1}`}>
              <CommitText
                value={chapter.title}
                onCommit={(title) => change(index, { title })}
              />
            </Field>
            <IconButton
              icon={ChevronUp}
              label="Przesuń rozdział w górę"
              disabled={!index}
              onClick={() =>
                save((current) =>
                  move(
                    current,
                    current.findIndex((c) => c.id === chapter.id),
                    -1,
                  ),
                )
              }
            />
            <IconButton
              icon={ChevronDown}
              label="Przesuń rozdział w dół"
              disabled={index === chapters.length - 1}
              onClick={() =>
                save((current) =>
                  move(
                    current,
                    current.findIndex((c) => c.id === chapter.id),
                    1,
                  ),
                )
              }
            />
            <IconButton
              icon={Trash2}
              label="Usuń rozdział"
              onClick={() =>
                save((current) => current.filter((c) => c.id !== chapter.id))
              }
            />
          </div>
          <Text
            label="Funkcja rozdziału w historii"
            value={chapter.purpose}
            save={(purpose) => change(index, { purpose })}
          />
          <div className="subchapter-list">
            {chapter.sections.map((section, si) => {
              const update = (
                values:
                  | Partial<Subchapter>
                  | ((section: Subchapter) => Partial<Subchapter>),
              ) =>
                change(index, (current) => ({
                  sections: current.sections.map((x) =>
                    x.id === section.id
                      ? {
                          ...x,
                          ...(typeof values === "function"
                            ? values(x)
                            : values),
                        }
                      : x,
                  ),
                }));
              return (
                <details
                  key={section.id}
                  className="subchapter-card"
                  open={si === 0}
                >
                  <summary>
                    <span>
                      {index + 1}.{si + 1}
                    </span>{" "}
                    {section.title}
                    <small>
                      {section.seconds} s · energia {section.energy}/10
                    </small>
                  </summary>
                  <div className="subchapter-body">
                    <Field label="Nazwa podrozdziału">
                      <CommitText
                        value={section.title}
                        onCommit={(title) => update({ title })}
                      />
                    </Field>
                    <div className="two-fields">
                      <Text
                        label="Cel tej części"
                        value={section.purpose}
                        save={(purpose) => update({ purpose })}
                      />
                      <Text
                        label="Pytanie prowadzące"
                        value={section.question}
                        save={(question) => update({ question })}
                      />
                      <Text
                        label="Zwrot / nowe odkrycie"
                        value={section.turn}
                        save={(turn) => update({ turn })}
                      />
                      <Text
                        label="Jak utrzymać uwagę?"
                        value={section.retention_plan}
                        save={(retention_plan) => update({ retention_plan })}
                      />
                      <NumberField
                        label="Planowany czas (s)"
                        value={section.seconds}
                        min={5}
                        max={3600}
                        step={1}
                        onCommit={(seconds) => update({ seconds })}
                      />
                      <NumberField
                        label="Energia / 10"
                        value={section.energy}
                        min={1}
                        max={10}
                        step={1}
                        onCommit={(energy) => update({ energy })}
                      />
                    </div>
                    <Text
                      label="Jakich źródeł i materiałów potrzebujemy?"
                      value={section.evidence_needed}
                      save={(evidence_needed) => update({ evidence_needed })}
                    />
                    {p.facts.length > 0 && (
                      <details>
                        <summary>Powiąż fakty ze źródłami</summary>
                        <div className="tool-options">
                          {p.facts.map((f) => (
                            <label key={f.id}>
                              <input
                                type="checkbox"
                                checked={section.fact_ids.includes(f.id)}
                                onChange={(e) => {
                                  const checked = e.target.checked;
                                  update((current) => ({
                                    fact_ids: checked
                                      ? [
                                          ...new Set([
                                            ...current.fact_ids,
                                            f.id,
                                          ]),
                                        ]
                                      : current.fact_ids.filter(
                                          (x) => x !== f.id,
                                        ),
                                  }));
                                }}
                              />
                              <span>
                                {f.claim}
                                <small>{f.status}</small>
                              </span>
                            </label>
                          ))}
                        </div>
                      </details>
                    )}
                    <div className="button-row">
                      <Button
                        subtle
                        icon={ChevronUp}
                        disabled={!si}
                        onClick={() =>
                          change(index, (current) => ({
                            sections: move(
                              current.sections,
                              current.sections.findIndex(
                                (x) => x.id === section.id,
                              ),
                              -1,
                            ),
                          }))
                        }
                      >
                        W górę
                      </Button>
                      <Button
                        subtle
                        icon={ChevronDown}
                        disabled={si === chapter.sections.length - 1}
                        onClick={() =>
                          change(index, (current) => ({
                            sections: move(
                              current.sections,
                              current.sections.findIndex(
                                (x) => x.id === section.id,
                              ),
                              1,
                            ),
                          }))
                        }
                      >
                        W dół
                      </Button>
                      <Button
                        subtle
                        icon={Trash2}
                        onClick={() =>
                          change(index, (current) => ({
                            sections: current.sections.filter(
                              (x) => x.id !== section.id,
                            ),
                          }))
                        }
                      >
                        Usuń podrozdział
                      </Button>
                    </div>
                  </div>
                </details>
              );
            })}
          </div>
          <Button
            icon={Plus}
            onClick={() =>
              change(index, (current) => ({
                sections: [...current.sections, blankSection()],
              }))
            }
          >
            Dodaj podrozdział
          </Button>
        </section>
      ))}
    </div>
  );
}

function IdeaAssistant({
  target,
  close,
}: {
  target: AITarget;
  close: () => void;
}) {
  const s = useStudio(),
    p = s.project!;
  const [instruction, setInstruction] = useState(""),
    [response, setResponse] = useState(""),
    [prompt, setPrompt] = useState(""),
    [base, setBase] = useState<number | null>(p.revision),
    [busy, setBusy] = useState(false);
  async function request(action: "prompt" | "generate") {
    setBusy(true);
    try {
      const result = await api<{
        prompt?: string;
        response?: string;
        base_revision: number;
      }>(`/projects/${p.id}/development/ai/${target.kind}/${action}`, {
        ...target,
        instruction,
      });
      setBase(result.base_revision);
      if (result.response) setResponse(result.response);
      if (result.prompt) {
        setPrompt(result.prompt);
        try {
          await navigator.clipboard.writeText(result.prompt);
          s.notify("Skopiowano prompt");
        } catch {
          s.notify("Prompt jest dostępny poniżej");
        }
      }
    } finally {
      setBusy(false);
    }
  }
  let parsed: unknown = null;
  try {
    parsed = JSON.parse(
      response.replace(/^```(?:json)?\s*/, "").replace(/```\s*$/, ""),
    );
  } catch {}
  return (
    <Modal
      open
      onClose={close}
      title={names[target.kind] + " z AI"}
      description={
        target.kind === "chapters"
          ? "Przyjęcie zastępuje plan rozdziałów tego wariantu. Scenariusz i montaż nie zmienią się automatycznie."
          : target.kind === "review"
            ? "Ocena jest roboczą opinią redakcyjną i zestawem założeń, nie wynikiem Analytics."
            : "Propozycje dołączą do kolekcji. Wyboru kierunku dokonujesz osobno."
      }
      wide
    >
      <Text
        label="Wskazówki dla redaktora"
        value={instruction}
        save={setInstruction}
      />
      <div className="button-row">
        <Button
          primary
          icon={Sparkles}
          busy={busy}
          onClick={() => s.run(() => request("generate"))}
        >
          Zaproponuj z AI
        </Button>
        <Button
          icon={Copy}
          busy={busy}
          onClick={() => s.run(() => request("prompt"))}
        >
          Skopiuj prompt
        </Button>
      </div>
      {!!parsed && (
        <div className="ai-idea-preview">
          {(Array.isArray(parsed) ? parsed : [parsed]).map((value, index) => {
            const row = (
              value && typeof value === "object" ? value : {}
            ) as Record<string, unknown>;
            return (
              <article className="surface tool-panel" key={index}>
                <h3>{String(row.title || names[target.kind])}</h3>
                <p>
                  {String(
                    row.synopsis ||
                      row.question ||
                      row.purpose ||
                      row.rationale ||
                      "Sprawdź propozycję przed przyjęciem.",
                  )}
                </p>
                {!!row.hook && (
                  <p>
                    <strong>Otwarcie:</strong> {String(row.hook)}
                  </p>
                )}
                {Array.isArray(row.sections) && (
                  <small>{row.sections.length} podrozdziałów</small>
                )}
              </article>
            );
          })}
        </div>
      )}
      <details className="advanced" open>
        <summary>Użyj odpowiedzi z innego narzędzia</summary>
        {prompt && (
          <Field label="Prompt">
            <textarea rows={5} readOnly value={prompt} />
          </Field>
        )}
        <Field label="Wklej odpowiedź JSON">
          <textarea
            rows={9}
            value={response}
            onChange={(e) => setResponse(e.target.value)}
          />
        </Field>
      </details>
      {base !== p.revision && (
        <p className="warning-text">
          Projekt zmienił się. Przygotuj nowy prompt lub propozycję przed
          przyjęciem.
        </p>
      )}
      <Button
        primary
        icon={Check}
        disabled={!parsed || base !== p.revision || busy}
        onClick={() =>
          s.run(async () => {
            await s.mutate((current) =>
              api<Project>(
                `/projects/${current.id}/development/ai/${target.kind}/import`,
                { ...target, base_revision: base, response },
              ),
            );
            close();
            s.notify("Zapisano propozycję do sprawdzenia");
          })
        }
      >
        {target.kind === "chapters"
          ? "Zastąp plan rozdziałów"
          : target.kind === "review"
            ? "Zapisz ocenę"
            : "Dodaj propozycje"}
      </Button>
    </Modal>
  );
}

export function ScriptStructure() {
  const s = useStudio(),
    p = s.project!;
  const [editor, setEditor] = useState(false);
  const beats = p.beats.filter((b) => b.planning_ref);
  if (!beats.length) return null;
  const chapters = [
    ...new Map(
      beats.map((b) => [
        b.planning_chapter_id || b.chapter,
        { id: b.planning_chapter_id || b.chapter, title: b.chapter },
      ]),
    ).values(),
  ];
  return (
    <section className="surface tool-panel script-structure">
      <div className="inline-heading">
        <div>
          <span className="eyebrow">WYBRANY PLAN FILMU</span>
          <h2>Rozdziały i podrozdziały</h2>
        </div>
        <div className="player-spacer" />
        <Button icon={BookOpen} onClick={() => setEditor(!editor)}>
          {editor ? "Zwiń redakcję" : "Redaguj fragmenty"}
        </Button>
      </div>
      {chapters.map((chapter, index) => (
        <div key={chapter.id} className="script-plan-chapter">
          <h3>
            {index + 1}. {chapter.title}
          </h3>
          <ol>
            {beats
              .filter(
                (b) => (b.planning_chapter_id || b.chapter) === chapter.id,
              )
              .map((beat) => (
                <li key={beat.id}>
                  <strong>{beat.title}</strong>
                  <span>{beat.goal}</span>
                  <small>
                    {beat.planning_seconds} s · energia {beat.energy}/10{" "}
                    {beat.retention_plan ? "· " + beat.retention_plan : ""}
                  </small>
                </li>
              ))}
          </ol>
        </div>
      ))}
      <p className="small muted">
        „Pracuj z AI” uwzględnia ten plan i powiązania z faktami. Narracja nadal
        wymaga sprawdzonych źródeł i zatwierdzonej Historii.
      </p>
      {p.story.status !== "APPROVED" && (
        <Button icon={ArrowRight} onClick={() => s.setPage("story")}>
          Sprawdź i zatwierdź Historię po researchu
        </Button>
      )}
      {editor && <BeatTools />}
    </section>
  );
}
