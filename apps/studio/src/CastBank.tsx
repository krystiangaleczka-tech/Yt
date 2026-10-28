import { useEffect, useMemo, useState } from "react";
import {
  Archive,
  ImagePlus,
  MapPinned,
  Plus,
  Save,
  Star,
  Trash2,
  Users,
} from "lucide-react";
import { useStudio } from "./context";
import { api, upload } from "./api";
import { Button, Empty, Field, IconButton, SectionHead } from "./components";
import { castImage, viewLabels } from "./animationTypes";
import type {
  CastBank as Bank,
  CastImage,
  Character,
  Location,
  LocationState,
  Pose,
} from "./animationTypes";

type Channel = { id: string; name: string; production_mode?: string };

const blankCharacter = (channel_id: string): Character => ({
  id: "",
  revision: 0,
  channel_id,
  name: "Nowa postać",
  role: "",
  description: "",
  personality: "",
  goal: "",
  signature: "",
  color: "#f2b866",
  voice: { provider: "", voice_id: "", notes: "" },
  poses: [],
  default_pose_id: "",
  archived: false,
  updated_at: "",
});
const blankLocation = (channel_id: string): Location => ({
  id: "",
  revision: 0,
  channel_id,
  name: "Nowa lokacja",
  description: "",
  states: [],
  archived: false,
  updated_at: "",
});
const label = (file: File) =>
  file.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").slice(0, 80) ||
  "Poza";
// New entries get their id from the server on first save.
const withoutBlankId = <T extends { id: string }>(item: T) =>
  item.id ? item : (({ id: _id, ...rest }) => rest)(item);

export function useCastChannel() {
  const s = useStudio();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [channelId, setChannelId] = useState(
    localStorage.getItem("docos:cast-channel") || "",
  );
  useEffect(() => {
    s.run(async () => {
      const rows = await api<Channel[]>("/channels");
      setChannels(rows);
      const preferred =
        (s.project?.production_mode === "animation_2d" && s.project.channel_id) ||
        rows.find((c) => c.id === channelId)?.id ||
        rows.find((c) => c.production_mode === "animation_2d")?.id ||
        rows[0]?.id ||
        "";
      setChannelId(preferred);
    });
  }, []);
  function choose(id: string) {
    setChannelId(id);
    localStorage.setItem("docos:cast-channel", id);
  }
  return { channels, channelId, choose };
}

export default function CastBankView({
  section,
}: {
  section: "cast" | "locations";
}) {
  const s = useStudio();
  const { channels, channelId, choose } = useCastChannel();
  const [bank, setBank] = useState<Bank>({ characters: [], locations: [] }),
    [selected, setSelected] = useState(""),
    [archived, setArchived] = useState(false);
  async function reload() {
    if (channelId) setBank(await api<Bank>(`/channels/${channelId}/cast`));
  }
  useEffect(() => {
    setSelected("");
    s.run(reload);
  }, [channelId]);
  const characters = section === "cast";
  const rows = (characters ? bank.characters : bank.locations).filter(
    (r) => archived || !r.archived,
  );
  const current = rows.find((r) => r.id === selected) || null;
  const channelName = channels.find((c) => c.id === channelId)?.name || "";
  return (
    <div className="page-content cast-page">
      <SectionHead
        eyebrow={`Pracownia · bank kanału${channelName ? " " + channelName : ""}`}
        title={characters ? "Postacie" : "Lokacje"}
        description={
          characters
            ? "Stała obsada kanału: wygląd, pozy i głos. Ta sama postać w każdym odcinku — inne kanały jej nie widzą."
            : "Miejsca akcji i ich stany (np. Dzień 1, zabarykadowane, noc). Tła wracają w kolejnych scenach i odcinkach."
        }
      >
        <select
          aria-label="Kanał banku"
          value={channelId}
          onChange={(e) => choose(e.target.value)}
        >
          {channels.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <Button
          primary
          icon={Plus}
          disabled={!channelId}
          onClick={() => setSelected("new")}
        >
          {characters ? "Nowa postać" : "Nowa lokacja"}
        </Button>
      </SectionHead>
      {!channelId ? (
        <Empty
          icon={Users}
          title="Najpierw utwórz kanał"
          children="Postacie i lokacje należą do konkretnego kanału. Dodaj kanał w Pracowni → Kanały i kategorie."
        />
      ) : (
        <div className="cast-layout">
          <div className="cast-list">
            {rows.length === 0 && (
              <p className="muted small">
                {characters
                  ? "Brak postaci. Dodaj pierwszą i wgraj jej pozy (PNG z przezroczystym tłem)."
                  : "Brak lokacji. Dodaj pierwszą i wgraj tło dla każdego stanu."}
              </p>
            )}
            {rows.map((r) => {
              const image = characters
                ? (r as Character).poses.find(
                    (p) => p.id === (r as Character).default_pose_id,
                  )?.image || (r as Character).poses[0]?.image
                : (r as Location).states.find((st) => st.image)?.image;
              return (
                <button
                  key={r.id}
                  className={`cast-card ${selected === r.id ? "active" : ""} ${r.archived ? "archived" : ""}`}
                  onClick={() => setSelected(r.id)}
                >
                  <span className={`cast-thumb ${characters ? "checker" : ""}`}>
                    {image ? (
                      <img src={castImage(channelId, image.file)} alt="" />
                    ) : characters ? (
                      <Users size={26} />
                    ) : (
                      <MapPinned size={26} />
                    )}
                  </span>
                  <strong>{r.name}</strong>
                  <span className="muted small">
                    {characters
                      ? `${(r as Character).role || "bez roli"} · ${(r as Character).poses.length} póz`
                      : `${(r as Location).states.length} stanów`}
                  </span>
                </button>
              );
            })}
            <label className="checkbox small">
              <input
                type="checkbox"
                checked={archived}
                onChange={(e) => setArchived(e.target.checked)}
              />
              Pokaż archiwalne
            </label>
          </div>
          <div className="cast-editor">
            {selected === "new" || current ? (
              characters ? (
                <CharacterEditor
                  key={selected + (current?.revision || 0)}
                  channelId={channelId}
                  value={(current as Character) || blankCharacter(channelId)}
                  saved={async (c) => {
                    await reload();
                    setSelected(c.id);
                  }}
                />
              ) : (
                <LocationEditor
                  key={selected + (current?.revision || 0)}
                  channelId={channelId}
                  value={(current as Location) || blankLocation(channelId)}
                  saved={async (l) => {
                    await reload();
                    setSelected(l.id);
                  }}
                />
              )
            ) : (
              <Empty
                icon={characters ? Users : MapPinned}
                title={characters ? "Wybierz postać" : "Wybierz lokację"}
                children="Kliknij kartę po lewej albo dodaj nowy wpis."
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function useImages(channelId: string) {
  const s = useStudio();
  const [busy, setBusy] = useState(false);
  async function send(files: FileList | File[]): Promise<[File, CastImage][]> {
    setBusy(true);
    try {
      const result: [File, CastImage][] = [];
      for (const file of Array.from(files))
        result.push([
          file,
          await upload<CastImage>(`/channels/${channelId}/cast-media`, file),
        ]);
      return result;
    } catch (error) {
      s.notify(String(error), true);
      return [];
    } finally {
      setBusy(false);
    }
  }
  return { busy, send };
}

function DropZone({
  busy,
  multiple,
  onFiles,
  children,
}: {
  busy: boolean;
  multiple?: boolean;
  onFiles: (files: FileList) => void;
  children: string;
}) {
  const [over, setOver] = useState(false);
  return (
    <label
      className={`cast-drop ${over ? "over" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        if (e.dataTransfer.files.length) onFiles(e.dataTransfer.files);
      }}
    >
      <ImagePlus size={20} />
      <span>{busy ? "Wgrywanie…" : children}</span>
      <input
        type="file"
        accept="image/png,image/webp,image/jpeg"
        multiple={multiple}
        className="visually-hidden"
        onChange={(e) => e.target.files?.length && onFiles(e.target.files)}
      />
    </label>
  );
}

function SaveBar({
  dirty,
  archived,
  save,
  archive,
}: {
  dirty: boolean;
  archived: boolean;
  save: () => void;
  archive: () => void;
}) {
  return (
    <div className="cast-savebar">
      <span className="muted small">
        {dirty ? "Niezapisane zmiany" : "Zapisano w banku kanału"}
      </span>
      <Button icon={Archive} subtle onClick={archive}>
        {archived ? "Przywróć" : "Archiwizuj"}
      </Button>
      <Button primary icon={Save} disabled={!dirty} onClick={save}>
        Zapisz
      </Button>
    </div>
  );
}

function CharacterEditor({
  channelId,
  value,
  saved,
}: {
  channelId: string;
  value: Character;
  saved: (c: Character) => Promise<void>;
}) {
  const s = useStudio();
  const [c, setC] = useState(value);
  const { busy, send } = useImages(channelId);
  const dirty = useMemo(
    () => JSON.stringify(c) !== JSON.stringify(value) || !value.id,
    [c, value],
  );
  const set = (patch: Partial<Character>) => setC((v) => ({ ...v, ...patch }));
  const setPose = (id: string, patch: Partial<Pose>) =>
    set({ poses: c.poses.map((p) => (p.id === id ? { ...p, ...patch } : p)) });
  function persist(next: Character) {
    s.run(async () => {
      const result = await api<Character>(
        `/channels/${channelId}/characters`,
        withoutBlankId(next),
      );
      s.notify(`Zapisano postać ${result.name}`);
      await saved(result);
    });
  }
  async function addPoses(files: FileList) {
    const added = (await send(files)).map(([file, image]) => ({
      id: "pose_" + crypto.randomUUID().replace(/-/g, "").slice(0, 16),
      name: label(file),
      view: "front" as const,
      image,
      tags: [],
    }));
    setC((v) => ({
      ...v,
      poses: [...v.poses, ...added],
      default_pose_id: v.default_pose_id || added[0]?.id || "",
    }));
  }
  return (
    <div className="cast-form">
      <div className="two-fields">
        <Field label="Imię / nazwa">
          <input value={c.name} onChange={(e) => set({ name: e.target.value })} />
        </Field>
        <Field label="Rola w historii">
          <input
            value={c.role}
            placeholder="np. mechanik, sąsiadka, narrator-bohater"
            onChange={(e) => set({ role: e.target.value })}
          />
        </Field>
      </div>
      <div className="two-fields">
        <Field label="Znak rozpoznawczy" hint="Cecha widoczna w każdym kadrze, np. kolor czapki.">
          <input
            value={c.signature}
            onChange={(e) => set({ signature: e.target.value })}
          />
        </Field>
        <Field label="Kolor akcentu">
          <input
            type="color"
            value={c.color}
            onChange={(e) => set({ color: e.target.value })}
          />
        </Field>
      </div>
      <Field label="Wygląd">
        <textarea
          rows={2}
          value={c.description}
          onChange={(e) => set({ description: e.target.value })}
        />
      </Field>
      <div className="two-fields">
        <Field label="Charakter">
          <textarea
            rows={2}
            value={c.personality}
            onChange={(e) => set({ personality: e.target.value })}
          />
        </Field>
        <Field label="Cel i granica">
          <textarea
            rows={2}
            value={c.goal}
            onChange={(e) => set({ goal: e.target.value })}
          />
        </Field>
      </div>
      <fieldset className="cast-fieldset">
        <legend>Głos</legend>
        <div className="two-fields">
          <Field label="Dostawca">
            <select
              value={c.voice.provider}
              onChange={(e) =>
                set({
                  voice: {
                    ...c.voice,
                    provider: e.target.value as Character["voice"]["provider"],
                  },
                })
              }
            >
              <option value="">Jeszcze nie wybrano</option>
              <option value="elevenlabs">ElevenLabs</option>
              <option value="local">Lokalny profil (Chatterbox)</option>
            </select>
          </Field>
          <Field label="ID głosu u dostawcy">
            <input
              value={c.voice.voice_id}
              onChange={(e) =>
                set({ voice: { ...c.voice, voice_id: e.target.value } })
              }
            />
          </Field>
        </div>
        <Field label="Jak gra głosem">
          <input
            value={c.voice.notes}
            placeholder="np. zmęczony, niski, mówi krótko"
            onChange={(e) =>
              set({ voice: { ...c.voice, notes: e.target.value } })
            }
          />
        </Field>
      </fieldset>
      <div className="cast-subhead">
        <strong>Pozy</strong>
        <span className="muted small">
          PNG z przezroczystym tłem, ta sama postać w różnych pozach i widokach.
        </span>
      </div>
      <div className="pose-grid">
        {c.poses.map((pose) => (
          <div key={pose.id} className="pose-card">
            <div className="pose-image checker">
              <img src={castImage(channelId, pose.image.file)} alt={pose.name} />
              {!pose.image.alpha && (
                <span className="badge warning pose-alpha">bez przezroczystości</span>
              )}
            </div>
            <input
              aria-label="Nazwa pozy"
              value={pose.name}
              onChange={(e) => setPose(pose.id, { name: e.target.value })}
            />
            <div className="pose-row">
              <select
                aria-label="Widok"
                value={pose.view}
                onChange={(e) =>
                  setPose(pose.id, { view: e.target.value as Pose["view"] })
                }
              >
                {Object.entries(viewLabels).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
              <IconButton
                icon={Star}
                label={c.default_pose_id === pose.id ? "Domyślna poza" : "Ustaw jako domyślną"}
                className={`icon-button ${c.default_pose_id === pose.id ? "starred" : ""}`}
                onClick={() => set({ default_pose_id: pose.id })}
              />
              <IconButton
                icon={Trash2}
                label="Usuń pozę"
                onClick={() =>
                  set({
                    poses: c.poses.filter((p) => p.id !== pose.id),
                    default_pose_id:
                      c.default_pose_id === pose.id ? "" : c.default_pose_id,
                  })
                }
              />
            </div>
          </div>
        ))}
        <DropZone busy={busy} multiple onFiles={(f) => s.run(() => addPoses(f))}>
          Przeciągnij pozy lub kliknij
        </DropZone>
      </div>
      <SaveBar
        dirty={dirty}
        archived={c.archived}
        save={() => persist(c)}
        archive={() => persist({ ...c, archived: !c.archived })}
      />
    </div>
  );
}

function LocationEditor({
  channelId,
  value,
  saved,
}: {
  channelId: string;
  value: Location;
  saved: (l: Location) => Promise<void>;
}) {
  const s = useStudio();
  const [l, setL] = useState(value);
  const { busy, send } = useImages(channelId);
  const dirty = useMemo(
    () => JSON.stringify(l) !== JSON.stringify(value) || !value.id,
    [l, value],
  );
  const set = (patch: Partial<Location>) => setL((v) => ({ ...v, ...patch }));
  const setState = (id: string, patch: Partial<LocationState>) =>
    set({ states: l.states.map((st) => (st.id === id ? { ...st, ...patch } : st)) });
  function persist(next: Location) {
    s.run(async () => {
      const result = await api<Location>(
        `/channels/${channelId}/locations`,
        withoutBlankId(next),
      );
      s.notify(`Zapisano lokację ${result.name}`);
      await saved(result);
    });
  }
  async function addStates(files: FileList) {
    const added = (await send(files)).map(([file, image]) => ({
      id: "lst_" + crypto.randomUUID().replace(/-/g, "").slice(0, 16),
      name: label(file),
      description: "",
      time_of_day: "" as const,
      image,
      foreground: null,
    }));
    setL((v) => ({ ...v, states: [...v.states, ...added] }));
  }
  return (
    <div className="cast-form">
      <Field label="Nazwa">
        <input value={l.name} onChange={(e) => set({ name: e.target.value })} />
      </Field>
      <Field label="Opis i układ miejsca" hint="Gdzie są drzwi, okno, zlew — pomaga zachować geografię między scenami. Pierwszy plan stanu (np. framuga, liście) daje głębię przy ruchu kamery.">
        <textarea
          rows={3}
          value={l.description}
          onChange={(e) => set({ description: e.target.value })}
        />
      </Field>
      <div className="cast-subhead">
        <strong>Stany</strong>
        <span className="muted small">
          To samo miejsce w różnych chwilach historii — każdy stan ma własne tło.
        </span>
      </div>
      <div className="state-list">
        {l.states.map((st) => (
          <div key={st.id} className="state-card">
            <div className="state-image">
              {st.image ? (
                <img src={castImage(channelId, st.image.file)} alt={st.name} />
              ) : (
                <MapPinned size={24} />
              )}
            </div>
            <div className="state-fields">
              <input
                aria-label="Nazwa stanu"
                value={st.name}
                onChange={(e) => setState(st.id, { name: e.target.value })}
              />
              <select
                aria-label="Pora dnia"
                value={st.time_of_day}
                onChange={(e) =>
                  setState(st.id, {
                    time_of_day: e.target.value as LocationState["time_of_day"],
                  })
                }
              >
                <option value="">Pora dnia</option>
                <option value="day">Dzień</option>
                <option value="dusk">Zmierzch</option>
                <option value="night">Noc</option>
              </select>
              <input
                aria-label="Opis stanu"
                placeholder="np. okna zabite deskami, woda w wannie"
                value={st.description}
                onChange={(e) => setState(st.id, { description: e.target.value })}
              />
              <div className="state-fg">
                {st.foreground ? (
                  <>
                    <span className="state-fg-thumb checker">
                      <img src={castImage(channelId, st.foreground.file)} alt="" />
                    </span>
                    <span className="small muted">Pierwszy plan (przed postaciami)</span>
                    <Button subtle icon={Trash2} onClick={() => setState(st.id, { foreground: null })}>
                      Usuń
                    </Button>
                  </>
                ) : (
                  <label className="button subtle">
                    <ImagePlus size={16} />
                    {busy ? "Wgrywanie…" : "Dodaj pierwszy plan (PNG z przezroczystością)"}
                    <input
                      type="file"
                      accept="image/png,image/webp"
                      className="visually-hidden"
                      onChange={(e) =>
                        e.target.files?.length &&
                        s.run(async () => {
                          const [first] = await send(e.target.files!);
                          if (first) setState(st.id, { foreground: first[1] });
                        })
                      }
                    />
                  </label>
                )}
              </div>
            </div>
            <IconButton
              icon={Trash2}
              label="Usuń stan"
              onClick={() => set({ states: l.states.filter((x) => x.id !== st.id) })}
            />
          </div>
        ))}
        <DropZone busy={busy} multiple onFiles={(f) => s.run(() => addStates(f))}>
          Przeciągnij tła stanów lub kliknij
        </DropZone>
      </div>
      <SaveBar
        dirty={dirty}
        archived={l.archived}
        save={() => persist(l)}
        archive={() => persist({ ...l, archived: !l.archived })}
      />
    </div>
  );
}
