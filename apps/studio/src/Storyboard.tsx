import { useEffect, useMemo, useRef, useState } from "react";
import {
  Clipboard,
  ExternalLink,
  Mic,
  MicOff,
  Pause,
  Play,
  Plus,
  SkipBack,
  SkipForward,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { useStudio } from "./context";
import { api } from "./api";
import { Button, CommitText, Empty, IconButton } from "./components";
import { Stage } from "./SceneBoard";
import { statusLabels } from "./animationTypes";
import type { CastBank, StageScene } from "./animationTypes";
import type { Beat, Project } from "./types";

type Breakdown = { beat_id: string; scenes: Partial<StageScene>[]; reason: string };
const clock = (seconds: number) =>
  `${Math.floor(seconds / 60)}:${String(Math.round(seconds % 60)).padStart(2, "0")}`;
const newBeat = (title: string) =>
  ({
    id: "beat_" + crypto.randomUUID().replace(/-/g, "").slice(0, 16),
    title,
    goal: "",
    narration: "",
    turn: "",
  }) as Beat;

type DraftLine = { line_id: string; voice: string; url: string; duration: number };
type Engine = "kokoro" | "browser";
const kokoroName = (id: string) =>
  `${id.split("_")[1].replace(/^./, (c) => c.toUpperCase())} · ${id[0] === "b" ? "UK" : "US"} ${id[1] === "f" ? "♀" : "♂"}`;

/** Draft voices for the animatic: local Kokoro (natural, fast) or the browser's speech as a fallback. */
function useDraftVoices(channelId: string, language: string) {
  const [engine, setEngineState] = useState<Engine>(
    (localStorage.getItem("docos:animatic-engine") as Engine) || "kokoro",
  );
  const key = `docos:animatic-voices:${engine}:${channelId}`;
  const [kokoro, setKokoro] = useState<{ available: boolean; voices: string[] }>({
    available: false,
    voices: [],
  });
  const [browserVoices, setBrowserVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [cast, setCast] = useState<Record<string, string>>({});
  useEffect(() => {
    try {
      setCast(JSON.parse(localStorage.getItem(key) || "{}"));
    } catch {
      setCast({});
    }
  }, [key]);
  useEffect(() => {
    api<{ available: boolean; voices: string[] }>("/draft-voices").then(setKokoro, () => undefined);
    if (!("speechSynthesis" in window)) return;
    const load = () =>
      setBrowserVoices(
        speechSynthesis
          .getVoices()
          .filter((v) => v.lang.toLowerCase().startsWith(language.slice(0, 2).toLowerCase())),
      );
    load();
    speechSynthesis.addEventListener("voiceschanged", load);
    return () => speechSynthesis.removeEventListener("voiceschanged", load);
  }, [language]);
  function setEngine(next: Engine) {
    setEngineState(next);
    localStorage.setItem("docos:animatic-engine", next);
  }
  function assign(speaker: string, voice: string) {
    const next = { ...cast, [speaker]: voice };
    if (!voice) delete next[speaker];
    setCast(next);
    localStorage.setItem(key, JSON.stringify(next));
  }
  const active: Engine = engine === "kokoro" && kokoro.available ? "kokoro" : "browser";
  const options =
    active === "kokoro"
      ? kokoro.voices.map((v) => ({ id: v, label: kokoroName(v) }))
      : browserVoices.map((v) => ({ id: v.name, label: v.name }));
  const browserVoice = (speaker: string) =>
    browserVoices.find((v) => v.name === cast[speaker]) || browserVoices[0];
  return { engine, setEngine, active, kokoro, cast, assign, options, browserVoice };
}

export default function Storyboard() {
  const s = useStudio();
  const p = s.project!;
  const [bank, setBank] = useState<CastBank>({ characters: [], locations: [] }),
    [index, setIndex] = useState(0),
    [lineIndex, setLineIndex] = useState(0),
    [playing, setPlaying] = useState(false),
    [speak, setSpeak] = useState(true),
    [rate, setRate] = useState(1.05),
    [proposal, setProposal] = useState<Breakdown | null>(null),
    [manual, setManual] = useState<{ beat: string; prompt: string; response: string; error: string } | null>(null),
    [busyBeat, setBusyBeat] = useState("");
  const voices = useDraftVoices(p.channel_id, p.language);
  useEffect(() => {
    if (p.channel_id)
      s.run(async () => setBank(await api<CastBank>(`/channels/${p.channel_id}/cast`)));
  }, [p.channel_id]);
  const beats = p.beats;
  const known = new Set(beats.map((b) => b.id));
  // Animatic order follows the story: beats first, then scenes without a beat.
  const ordered = useMemo(
    () => [
      ...beats.flatMap((b) => p.stage_scenes.filter((x) => x.beat_id === b.id)),
      ...p.stage_scenes.filter((x) => !known.has(x.beat_id)),
    ],
    [p.stage_scenes, beats],
  );
  const total = ordered.reduce((sum, x) => sum + x.seconds, 0);
  const current = ordered[Math.min(index, ordered.length - 1)];
  const elapsed = ordered.slice(0, index).reduce((sum, x) => sum + x.seconds, 0);

  // Kokoro lines are generated on the server and cached, so a replay is instant.
  const drafts = useRef(new Map<string, Promise<DraftLine[]>>());
  const [preparing, setPreparing] = useState(false),
    [batch, setBatch] = useState<{ done: number; total: number } | null>(null);
  function draftsFor(scene: StageScene) {
    const id = JSON.stringify([scene.id, scene.dialogue.map((d) => [d.speaker, d.text]), voices.cast, rate]);
    if (!drafts.current.has(id)) {
      const request = api<DraftLine[]>(`/projects/${p.id}/stage-scenes/${scene.id}/draft-voice`, {
        voices: voices.cast,
        speed: rate,
      });
      request.catch(() => drafts.current.delete(id));
      drafts.current.set(id, request);
    }
    return drafts.current.get(id)!;
  }

  // Playback: a scene ends when both its planned duration and its spoken lines are over.
  const token = useRef(0);
  useEffect(() => {
    if (!playing || !current) return;
    const mine = ++token.current;
    const lines = current.dialogue.filter((d) => d.text.trim());
    const engine = speak && lines.length ? voices.active : null;
    let timeDone = false,
      speechDone = !engine,
      timer: ReturnType<typeof setTimeout> | undefined;
    const audio = new Audio();
    const captions: ReturnType<typeof setTimeout>[] = [];
    const live = () => token.current === mine;
    const advance = () => {
      if (!live() || !timeDone || !speechDone) return;
      if (index >= ordered.length - 1) setPlaying(false);
      else setIndex(index + 1);
    };
    const startClock = () => {
      timer = setTimeout(() => {
        timeDone = true;
        advance();
      }, current.seconds * 1000);
    };
    setLineIndex(0);
    if (engine === "kokoro") {
      setPreparing(true);
      const next = ordered[index + 1];
      draftsFor(current)
        .then((rows) => {
          if (!live()) return;
          setPreparing(false);
          if (next) draftsFor(next).catch(() => undefined);
          startClock();
          const play = (i: number) => {
            if (!live()) return;
            if (i >= rows.length) {
              speechDone = true;
              return advance();
            }
            setLineIndex(current.dialogue.findIndex((d) => d.id === rows[i].line_id));
            audio.src = rows[i].url;
            audio.onended = () => play(i + 1);
            audio.play().catch(() => play(i + 1));
          };
          play(0);
        })
        .catch((error) => {
          if (!live()) return;
          setPreparing(false);
          s.notify(String(error.message || error), true);
          speechDone = true;
          startClock();
        });
    } else if (engine === "browser") {
      startClock();
      speechSynthesis.cancel();
      lines.forEach((line, i) => {
        const u = new SpeechSynthesisUtterance(line.text);
        const voice = voices.browserVoice(line.speaker);
        if (voice) u.voice = voice;
        u.rate = rate;
        u.onstart = () => live() && setLineIndex(current.dialogue.indexOf(line));
        if (i === lines.length - 1)
          u.onend = u.onerror = () => {
            speechDone = true;
            advance();
          };
        speechSynthesis.speak(u);
      });
    } else {
      startClock();
      lines.forEach((line, i) =>
        captions.push(
          setTimeout(
            () => setLineIndex(current.dialogue.indexOf(line)),
            (current.seconds * 1000 * i) / lines.length,
          ),
        ),
      );
    }
    return () => {
      clearTimeout(timer);
      captions.forEach(clearTimeout);
      audio.pause();
      audio.removeAttribute("src");
      setPreparing(false);
      if ("speechSynthesis" in window) speechSynthesis.cancel();
    };
  }, [playing, index, current?.id, speak]);
  function prepareAll() {
    s.run(async () => {
      const spoken = ordered.filter((x) => x.dialogue.some((d) => d.text.trim()));
      setBatch({ done: 0, total: spoken.length });
      try {
        for (let i = 0; i < spoken.length; i++) {
          await draftsFor(spoken[i]);
          setBatch({ done: i + 1, total: spoken.length });
        }
        s.notify("Głosy robocze całego animatiku są gotowe");
      } finally {
        setBatch(null);
      }
    });
  }
  useEffect(() => () => void ("speechSynthesis" in window && speechSynthesis.cancel()), []);

  function seek(i: number) {
    setIndex(Math.max(0, Math.min(ordered.length - 1, i)));
    setLineIndex(0);
  }
  function openScene(scene: StageScene) {
    localStorage.setItem("docos:stage:" + p.id, scene.id);
    s.setPage("scenes");
  }
  const saveBeats = (next: Beat[]) => s.run(() => s.patch({ beats: next }));
  const sceneOps = (operations: Record<string, unknown>[]) =>
    s.mutate((current) =>
      api<Project>(`/projects/${current.id}/stage-scenes`, {
        expected_revision: current.revision,
        operations,
      }),
    );
  function breakdown(beat: Beat, response?: string) {
    s.run(async () => {
      setBusyBeat(beat.id);
      try {
        setProposal(
          await api<Breakdown>(`/projects/${p.id}/beats/${beat.id}/breakdown`, response ? { response } : {}),
        );
        setManual(null);
      } catch (error) {
        const { prompt } = await api<{ prompt: string }>(
          `/projects/${p.id}/beats/${beat.id}/breakdown/prompt`,
          {},
        );
        setManual({ beat: beat.id, prompt, response: response || "", error: String((error as Error).message || error) });
        throw error;
      } finally {
        setBusyBeat("");
      }
    });
  }

  if (p.production_mode !== "animation_2d" || !p.channel_id)
    return (
      <Empty
        title="Storyboard i animatik należą do filmu animowanego z kanałem"
        children="Utwórz film w trybie Animacja 2D i przypisz go do kanału."
      />
    );
  const speakers = [
    { id: "narrator", name: "Narrator" },
    ...bank.characters.filter((c) => !c.archived).map((c) => ({ id: c.id, name: c.name })),
  ];
  return (
    <div className="page-content storyboard-page">
      <section className="animatic">
        <div className="animatic-stage">
          {current ? (
            <Stage
              key={current.id + (playing ? ":play" : "")}
              scene={current}
              bank={bank}
              channelId={p.channel_id}
              lineIndex={lineIndex}
              animate={playing && !preparing}
            />
          ) : (
            <Empty title="Animatik jest pusty" children="Dodaj beaty i sceny poniżej." />
          )}
        </div>
        <div className="animatic-controls">
          <IconButton icon={SkipBack} label="Poprzednia scena" onClick={() => seek(index - 1)} />
          <Button
            primary
            icon={playing ? Pause : Play}
            disabled={!ordered.length}
            onClick={() => setPlaying(!playing)}
          >
            {playing ? "Pauza" : "Odtwórz"}
          </Button>
          <IconButton icon={SkipForward} label="Następna scena" onClick={() => seek(index + 1)} />
          <span className="animatic-clock">
            {clock(elapsed)} / {clock(total)}
          </span>
          {current && (
            <span className="muted small">
              Scena {current.number} · {current.title}
              {preparing && " · przygotowuję głos…"}
            </span>
          )}
          <span className="animatic-spacer" />
          <IconButton
            icon={speak ? Mic : MicOff}
            label={speak ? "Głos roboczy włączony" : "Głos roboczy wyłączony"}
            onClick={() => setSpeak(!speak)}
          />
          <label className="animatic-rate small muted">
            tempo
            <input
              type="range"
              min={0.7}
              max={1.5}
              step={0.05}
              value={rate}
              onChange={(e) => setRate(Number(e.target.value))}
            />
          </label>
        </div>
        <div className="animatic-strip" role="list" aria-label="Oś animatiku">
          {ordered.map((x, i) => (
            <button
              key={x.id}
              role="listitem"
              className={`strip-block ${x.status} ${i === index ? "active" : ""}`}
              style={{ flexGrow: x.seconds }}
              title={`Scena ${x.number}: ${x.title} (${x.seconds} s, ${statusLabels[x.status]})`}
              onClick={() => seek(i)}
            >
              {x.number}
            </button>
          ))}
        </div>
        {speak && (
          <details className="animatic-voices" open={!voices.kokoro.available && voices.engine === "kokoro"}>
            <summary>
              Głosy robocze: {voices.active === "kokoro" ? "Kokoro (lokalnie)" : "przeglądarka"} — tylko do animatiku
            </summary>
            <div className="voice-engine">
              <label className="checkbox small">
                <input
                  type="radio"
                  checked={voices.engine === "kokoro"}
                  onChange={() => voices.setEngine("kokoro")}
                />
                Kokoro — naturalny, generuje się na tym Macu w kilka sekund na scenę
              </label>
              <label className="checkbox small">
                <input
                  type="radio"
                  checked={voices.engine === "browser"}
                  onChange={() => voices.setEngine("browser")}
                />
                Przeglądarka — natychmiast, brzmi sztucznie
              </label>
              {voices.engine === "kokoro" && !voices.kokoro.available && (
                <p className="manual-error small">
                  Kokoro nie jest dostępny: potrzebne środowisko z kokoro-onnx (DOCOS_DRAFT_TTS_PYTHON) i pliki modelu (DOCOS_KOKORO_DIR). Do tego czasu gra przeglądarka.
                </p>
              )}
              {voices.active === "kokoro" && (
                <Button subtle busy={!!batch} onClick={prepareAll}>
                  {batch
                    ? `Przygotowuję ${batch.done}/${batch.total}`
                    : "Przygotuj głosy całego animatiku"}
                </Button>
              )}
            </div>
            <div className="voice-grid">
              {speakers.map((sp) => (
                <label key={sp.id} className="field">
                  <span className="field-label">{sp.name}</span>
                  <select
                    value={voices.cast[sp.id] || ""}
                    onChange={(e) => voices.assign(sp.id, e.target.value)}
                  >
                    <option value="">Automatyczny</option>
                    {voices.options.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.label}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
          </details>
        )}
      </section>

      <div className="storyboard-head">
        <h2>Storyboard</h2>
        <span className="muted small">
          {beats.length} beatów · {p.stage_scenes.length} scen · {clock(total)}
        </span>
        <Button
          icon={Plus}
          onClick={() => saveBeats([...beats, newBeat(`Beat ${beats.length + 1}`)])}
        >
          Nowy beat
        </Button>
      </div>
      {proposal && (
        <div className="proposal-card">
          <div className="proposal-head">
            <strong>
              Propozycja scen dla {beats.find((b) => b.id === proposal.beat_id)?.title}
            </strong>
            {proposal.reason && <span className="muted small">{proposal.reason}</span>}
          </div>
          <ol className="breakdown-list">
            {proposal.scenes.map((x, i) => (
              <li key={i}>
                <strong>{x.title}</strong> <span className="muted small">{x.seconds} s</span>
                {x.action && <div className="small">{x.action}</div>}
              </li>
            ))}
          </ol>
          <div className="button-row">
            <Button
              primary
              icon={Plus}
              onClick={() =>
                s.run(async () => {
                  await sceneOps(proposal.scenes.map((scene) => ({ type: "add", scene })));
                  setProposal(null);
                  s.notify(`Dodano ${proposal.scenes.length} scen do oceny`);
                })
              }
            >
              Dodaj {proposal.scenes.length} scen
            </Button>
            <Button icon={X} onClick={() => setProposal(null)}>
              Odrzuć
            </Button>
          </div>
        </div>
      )}
      {manual && (
        <div className="proposal-card">
          <div className="proposal-head">
            <strong>AI nie dało poprawnej propozycji</strong>
            <IconButton icon={X} label="Zamknij" onClick={() => setManual(null)} />
          </div>
          <p className="small manual-error">{manual.error}</p>
          <p className="muted small">
            Spróbuj ponownie albo skopiuj prompt do własnego modelu i wklej odpowiedź JSON — aplikacja sprawdzi, czy używa tylko postaci i lokacji z banku.
          </p>
          <Button
            icon={Clipboard}
            onClick={() =>
              s.run(async () => {
                await navigator.clipboard.writeText(manual.prompt);
                s.notify("Skopiowano prompt");
              })
            }
          >
            Kopiuj prompt
          </Button>
          <textarea
            rows={5}
            value={manual.response}
            placeholder='{"reason": "...", "scenes": [...]}'
            onChange={(e) => setManual({ ...manual, response: e.target.value })}
          />
          <Button
            primary
            disabled={!manual.response.trim()}
            onClick={() => {
              const beat = beats.find((b) => b.id === manual.beat);
              if (beat) breakdown(beat, manual.response);
            }}
          >
            Sprawdź odpowiedź
          </Button>
        </div>
      )}
      {[...beats, null].map((beat, b) => {
        const scenes = beat
          ? p.stage_scenes.filter((x) => x.beat_id === beat.id)
          : p.stage_scenes.filter((x) => !known.has(x.beat_id));
        if (!beat && !scenes.length) return null;
        return (
          <section key={beat?.id || "none"} className="beat-row">
            <div className="beat-head">
              <span className="beat-no">{beat ? `B${String(b + 1).padStart(2, "0")}` : "—"}</span>
              {beat ? (
                <div className="beat-fields">
                  <CommitText
                    value={beat.title}
                    onCommit={(title) =>
                      saveBeats(beats.map((x) => (x.id === beat.id ? { ...x, title: title || x.title } : x)))
                    }
                  />
                  <CommitText
                    multiline
                    rows={2}
                    value={beat.narration || beat.goal}
                    placeholder="Co się dzieje w tym beacie i po co (AI rozpisze to na sceny)"
                    onCommit={(narration) =>
                      saveBeats(beats.map((x) => (x.id === beat.id ? { ...x, narration } : x)))
                    }
                  />
                </div>
              ) : (
                <strong>Sceny bez beatu</strong>
              )}
              <span className="muted small">
                {scenes.length} scen · {clock(scenes.reduce((sum, x) => sum + x.seconds, 0))}
              </span>
              {beat && (
                <div className="beat-actions">
                  <Button
                    icon={Sparkles}
                    busy={busyBeat === beat.id}
                    onClick={() => breakdown(beat)}
                  >
                    Rozpisz na sceny
                  </Button>
                  <IconButton
                    icon={Plus}
                    label="Dodaj pustą scenę do beatu"
                    onClick={() =>
                      s.run(() => sceneOps([{ type: "add", scene: { beat_id: beat.id } }]))
                    }
                  />
                  <IconButton
                    icon={Trash2}
                    label={scenes.length ? "Najpierw przenieś lub usuń sceny beatu" : "Usuń beat"}
                    disabled={scenes.length > 0}
                    onClick={() => saveBeats(beats.filter((x) => x.id !== beat.id))}
                  />
                </div>
              )}
            </div>
            <div className="board-grid">
              {scenes.map((x) => (
                <div
                  key={x.id}
                  className={`board-card ${current?.id === x.id ? "active" : ""}`}
                  onClick={() => seek(ordered.findIndex((o) => o.id === x.id))}
                  onDoubleClick={() => openScene(x)}
                >
                  <Stage scene={x} bank={bank} channelId={p.channel_id} compact />
                  <div className="board-card-meta">
                    <span className={`status-dot ${x.status}`} title={statusLabels[x.status]} />
                    <span className="scene-no">{String(x.number).padStart(2, "0")}</span>
                    <strong>{x.title}</strong>
                    <span className="muted small">{x.seconds} s</span>
                    <IconButton
                      icon={ExternalLink}
                      label="Otwórz scenę do oceny"
                      onClick={(e) => {
                        e.stopPropagation();
                        openScene(x);
                      }}
                    />
                  </div>
                  {x.dialogue[0]?.text && (
                    <p className="board-card-line small muted">“{x.dialogue[0].text}”</p>
                  )}
                </div>
              ))}
              {!scenes.length && beat && (
                <p className="muted small">
                  Brak scen. Kliknij „Rozpisz na sceny”, żeby AI zaproponowało ujęcia z postaci i lokacji kanału.
                </p>
              )}
            </div>
          </section>
        );
      })}
    </div>
  );
}
