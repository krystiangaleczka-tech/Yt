import { useEffect, useMemo, useState } from "react";
import {
  Archive,
  AudioLines,
  Backpack,
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
import { castAudio, castImage, itemCategoryLabels, soundKindLabels, viewLabels } from "./animationTypes";
import type {
  Region,
  CastBank as Bank,
  CastImage,
  Character,
  Item,
  ItemCategory,
  Sound,
  SoundKind,
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
const blankItem = (channel_id: string): Item => ({
  id: "",
  revision: 0,
  channel_id,
  category: "prop",
  name: "Nowy rekwizyt",
  description: "",
  character_ids: [],
  variants: [],
  tags: [],
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
  section: "cast" | "locations" | "props" | "sounds";
}) {
  const s = useStudio();
  const { channels, channelId, choose } = useCastChannel();
  const [bank, setBank] = useState<Bank>({ characters: [], locations: [], items: [] }),
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
  const props = section === "props";
  const sounds = section === "sounds";
  const [category, setCategory] = useState("");
  const rows = (
    (characters
      ? bank.characters
      : props
        ? bank.items || []
        : sounds
          ? bank.sounds || []
          : bank.locations) as (Character | Location | Item | Sound)[]
  ).filter(
    (r) =>
      (archived || !r.archived) &&
      (!category ||
        (props && (r as Item).category === category) ||
        (sounds && (r as Sound).kind === category)),
  );
  if (sounds)
    return (
      <SoundBank
        channels={channels}
        channelId={channelId}
        choose={choose}
        rows={rows as Sound[]}
        category={category}
        setCategory={setCategory}
        archived={archived}
        setArchived={setArchived}
        selected={selected}
        setSelected={setSelected}
        reload={reload}
      />
    );
  const current = rows.find((r) => r.id === selected) || null;
  const channelName = channels.find((c) => c.id === channelId)?.name || "";
  return (
    <div className="page-content cast-page">
      <SectionHead
        eyebrow={`Pracownia · bank kanału${channelName ? " " + channelName : ""}`}
        title={characters ? "Postacie" : props ? "Rekwizyty i kostiumy" : "Lokacje"}
        description={
          characters
            ? "Stała obsada kanału: wygląd, pozy i głos. Ta sama postać w każdym odcinku — inne kanały jej nie widzą."
            : props
              ? "Przedmioty, ubiory i nakładki (pęknięcia, plamy, światło). Rekwizyt umieszczasz w scenie i przenosisz do kolejnych — ciągłość zostaje."
              : "Miejsca akcji i ich stany (np. Dzień 1, zabarykadowane, noc). Tła wracają w kolejnych scenach i odcinkach."
        }
      >
        {props && (
          <select
            aria-label="Rodzaj"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Wszystkie rodzaje</option>
            {Object.entries(itemCategoryLabels).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        )}
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
          {characters ? "Nowa postać" : props ? "Nowy element" : "Nowa lokacja"}
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
                  : props
                    ? "Brak elementów. Dodaj rekwizyt, kostium albo nakładkę i wgraj warianty (PNG z przezroczystością)."
                    : "Brak lokacji. Dodaj pierwszą i wgraj tło dla każdego stanu."}
              </p>
            )}
            {rows.map((r) => {
              const image = characters
                ? (r as Character).poses.find(
                    (p) => p.id === (r as Character).default_pose_id,
                  )?.image || (r as Character).poses[0]?.image
                : props
                  ? (r as Item).variants[0]?.image
                  : (r as Location).states.find((st) => st.image)?.image;
              return (
                <button
                  key={r.id}
                  className={`cast-card ${selected === r.id ? "active" : ""} ${r.archived ? "archived" : ""}`}
                  onClick={() => setSelected(r.id)}
                >
                  <span className={`cast-thumb ${characters || props ? "checker" : ""}`}>
                    {image ? (
                      <img src={castImage(channelId, image.file)} alt="" />
                    ) : props ? (
                      <Backpack size={26} />
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
                      : props
                        ? `${itemCategoryLabels[(r as Item).category]} · ${(r as Item).variants.length} wariantów`
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
              props ? (
                <ItemEditor
                  key={selected + (current?.revision || 0)}
                  channelId={channelId}
                  characters={bank.characters}
                  value={(current as Item) || blankItem(channelId)}
                  saved={async (item) => {
                    await reload();
                    setSelected(item.id);
                  }}
                />
              ) : characters ? (
                <CharacterEditor
                  key={selected + (current?.revision || 0)}
                  channelId={channelId}
                  costumes={(bank.items || []).filter((i) => i.category === "costume" && !i.archived)}
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
                icon={props ? Backpack : characters ? Users : MapPinned}
                title={props ? "Wybierz element" : characters ? "Wybierz postać" : "Wybierz lokację"}
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
  costumes,
  value,
  saved,
}: {
  channelId: string;
  costumes: Item[];
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
              {costumes.some((x) => !x.character_ids.length || x.character_ids.includes(c.id)) && (
                <select
                  aria-label="Kostium"
                  value={pose.costume_id || ""}
                  onChange={(e) => setPose(pose.id, { costume_id: e.target.value })}
                >
                  <option value="">Strój bazowy</option>
                  {costumes
                    .filter((x) => !x.character_ids.length || x.character_ids.includes(c.id))
                    .map((x) => (
                      <option key={x.id} value={x.id}>
                        {x.name}
                      </option>
                    ))}
                </select>
              )}
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
              {st.image && (
                <details className="state-regions">
                  <summary>
                    Obszary i podłoga ({(st.regions || []).length} obszarów
                    {st.floor_y != null ? ", podłoga ustawiona" : ""})
                  </summary>
                  <RegionEditor
                    channelId={channelId}
                    state={st}
                    change={(patch) => setState(st.id, patch)}
                  />
                </details>
              )}
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

function ItemEditor({
  channelId,
  characters,
  value,
  saved,
}: {
  channelId: string;
  characters: Character[];
  value: Item;
  saved: (i: Item) => Promise<void>;
}) {
  const s = useStudio();
  const [item, setItem] = useState(value);
  const { busy, send } = useImages(channelId);
  const dirty = useMemo(
    () => JSON.stringify(item) !== JSON.stringify(value) || !value.id,
    [item, value],
  );
  const set = (patch: Partial<Item>) => setItem((v) => ({ ...v, ...patch }));
  function persist(next: Item) {
    s.run(async () => {
      const result = await api<Item>(`/channels/${channelId}/items`, withoutBlankId(next));
      s.notify(`Zapisano: ${result.name}`);
      await saved(result);
    });
  }
  async function addVariants(files: FileList) {
    const added = (await send(files)).map(([file, image]) => ({
      id: "var_" + crypto.randomUUID().replace(/-/g, "").slice(0, 16),
      name: label(file),
      image,
    }));
    setItem((v) => ({ ...v, variants: [...v.variants, ...added] }));
  }
  return (
    <div className="cast-form">
      <div className="two-fields">
        <Field label="Nazwa">
          <input value={item.name} onChange={(e) => set({ name: e.target.value })} />
        </Field>
        <Field label="Rodzaj">
          <select
            value={item.category}
            onChange={(e) =>
              set({
                category: e.target.value as ItemCategory,
                character_ids: e.target.value === "costume" ? item.character_ids : [],
              })
            }
          >
            {Object.entries(itemCategoryLabels).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <Field
        label="Opis"
        hint={
          item.category === "costume"
            ? "Kostium grupuje pozy postaci w danym stroju (oznaczasz to przy pozach postaci) i pilnuje, by strój nie zmieniał się przypadkiem."
            : "Kiedy i jak używać, np. pęknięcie zostaje na szybie do końca odcinka."
        }
      >
        <textarea
          rows={2}
          value={item.description}
          onChange={(e) => set({ description: e.target.value })}
        />
      </Field>
      {item.category === "costume" && (
        <fieldset className="cast-fieldset">
          <legend>Dla postaci</legend>
          <div className="costume-cast">
            {characters.map((c) => (
              <label key={c.id} className="checkbox small">
                <input
                  type="checkbox"
                  checked={item.character_ids.includes(c.id)}
                  onChange={(e) =>
                    set({
                      character_ids: e.target.checked
                        ? [...item.character_ids, c.id]
                        : item.character_ids.filter((x) => x !== c.id),
                    })
                  }
                />
                {c.name}
              </label>
            ))}
            {!characters.length && <span className="muted small">Brak postaci w banku.</span>}
          </div>
        </fieldset>
      )}
      <div className="cast-subhead">
        <strong>{item.category === "costume" ? "Referencje stroju" : "Warianty"}</strong>
        <span className="muted small">
          {item.category === "costume"
            ? "Obrazy wzorcowe stroju — do generowania póz w tym ubraniu."
            : "PNG z przezroczystym tłem, np. butelka pełna / pusta, pęknięcie małe / duże."}
        </span>
      </div>
      <div className="pose-grid">
        {item.variants.map((v) => (
          <div key={v.id} className="pose-card">
            <div className="pose-image checker">
              <img src={castImage(channelId, v.image.file)} alt={v.name} />
            </div>
            <div className="pose-row">
              <input
                aria-label="Nazwa wariantu"
                value={v.name}
                onChange={(e) =>
                  set({
                    variants: item.variants.map((x) =>
                      x.id === v.id ? { ...x, name: e.target.value } : x,
                    ),
                  })
                }
              />
              <IconButton
                icon={Trash2}
                label="Usuń wariant"
                onClick={() => set({ variants: item.variants.filter((x) => x.id !== v.id) })}
              />
            </div>
          </div>
        ))}
        <DropZone busy={busy} multiple onFiles={(f) => s.run(() => addVariants(f))}>
          Przeciągnij obrazy lub kliknij
        </DropZone>
      </div>
      <SaveBar
        dirty={dirty}
        archived={item.archived}
        save={() => persist(item)}
        archive={() => persist({ ...item, archived: !item.archived })}
      />
    </div>
  );
}

const blankSound = (channel_id: string): Sound => ({
  id: "",
  revision: 0,
  channel_id,
  kind: "sfx",
  name: "Nowy dźwięk",
  file: "",
  duration: 0,
  volume: 1,
  source_url: "",
  author: "",
  license: "",
  attribution: "",
  tags: [],
  archived: false,
  updated_at: "",
});

function SoundBank({
  channels,
  channelId,
  choose,
  rows,
  category,
  setCategory,
  archived,
  setArchived,
  selected,
  setSelected,
  reload,
}: {
  channels: { id: string; name: string }[];
  channelId: string;
  choose: (id: string) => void;
  rows: Sound[];
  category: string;
  setCategory: (v: string) => void;
  archived: boolean;
  setArchived: (v: boolean) => void;
  selected: string;
  setSelected: (v: string) => void;
  reload: () => Promise<void>;
}) {
  const current = rows.find((r) => r.id === selected) || null;
  const channelName = channels.find((c) => c.id === channelId)?.name || "";
  return (
    <div className="page-content cast-page">
      <SectionHead
        eyebrow={`Pracownia · bank kanału${channelName ? " " + channelName : ""}`}
        title="Dźwięki i muzyka"
        description="Efekty, atmosfery miejsc i utwory z licencjami. Efekty i atmosfery przypisujesz do scen, muzykę do zakresu scen w Storyboardzie."
      >
        <select aria-label="Rodzaj" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Wszystkie rodzaje</option>
          {Object.entries(soundKindLabels).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <select aria-label="Kanał banku" value={channelId} onChange={(e) => choose(e.target.value)}>
          {channels.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <Button primary icon={Plus} disabled={!channelId} onClick={() => setSelected("new")}>
          Nowy dźwięk
        </Button>
      </SectionHead>
      <div className="cast-layout">
        <div className="cast-list">
          {rows.length === 0 && (
            <p className="muted small">
              Brak dźwięków. Wgraj efekt, atmosferę albo utwór i zapisz jego licencję (np. CC0 z Freesound albo własne nagranie).
            </p>
          )}
          {rows.map((r) => (
            <button
              key={r.id}
              className={`cast-card ${selected === r.id ? "active" : ""} ${r.archived ? "archived" : ""}`}
              onClick={() => setSelected(r.id)}
            >
              <span className="cast-thumb">
                <AudioLines size={24} />
              </span>
              <strong>{r.name}</strong>
              <span className="muted small">
                {soundKindLabels[r.kind]} · {r.duration.toFixed(1)} s{r.license ? ` · ${r.license}` : " · brak licencji"}
              </span>
            </button>
          ))}
          <label className="checkbox small">
            <input type="checkbox" checked={archived} onChange={(e) => setArchived(e.target.checked)} />
            Pokaż archiwalne
          </label>
        </div>
        <div className="cast-editor">
          {selected === "new" || current ? (
            <SoundEditor
              key={selected + (current?.revision || 0)}
              channelId={channelId}
              value={current || blankSound(channelId)}
              saved={async (x) => {
                await reload();
                setSelected(x.id);
              }}
            />
          ) : (
            <Empty icon={AudioLines} title="Wybierz dźwięk" children="Kliknij kartę po lewej albo dodaj nowy dźwięk." />
          )}
        </div>
      </div>
    </div>
  );
}

function SoundEditor({
  channelId,
  value,
  saved,
}: {
  channelId: string;
  value: Sound;
  saved: (x: Sound) => Promise<void>;
}) {
  const s = useStudio();
  const [x, setX] = useState(value);
  const [busy, setBusy] = useState(false);
  const dirty = useMemo(() => JSON.stringify(x) !== JSON.stringify(value) || !value.id, [x, value]);
  const set = (patch: Partial<Sound>) => setX((v) => ({ ...v, ...patch }));
  async function addFile(file: File) {
    setBusy(true);
    try {
      const result = await upload<{ file: string; duration: number }>(`/channels/${channelId}/cast-audio`, file);
      set({ ...result, name: x.name === "Nowy dźwięk" ? label(file) : x.name });
    } finally {
      setBusy(false);
    }
  }
  function persist(next: Sound) {
    s.run(async () => {
      const result = await api<Sound>(`/channels/${channelId}/sounds`, withoutBlankId(next));
      s.notify(`Zapisano dźwięk ${result.name}`);
      await saved(result);
    });
  }
  return (
    <div className="cast-form">
      <div className="two-fields">
        <Field label="Nazwa">
          <input value={x.name} onChange={(e) => set({ name: e.target.value })} />
        </Field>
        <Field label="Rodzaj">
          <select value={x.kind} onChange={(e) => set({ kind: e.target.value as SoundKind })}>
            {Object.entries(soundKindLabels).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </Field>
      </div>
      {x.file ? (
        <div className="sound-preview">
          <audio controls src={castAudio(channelId, x.file)} preload="none" />
          <span className="muted small">{x.duration.toFixed(1)} s</span>
        </div>
      ) : null}
      <label className="cast-drop">
        <AudioLines size={20} />
        <span>{busy ? "Wgrywanie…" : x.file ? "Podmień plik (WAV, MP3, OGG, M4A, FLAC)" : "Wgraj plik dźwięku (WAV, MP3, OGG, M4A, FLAC)"}</span>
        <input
          type="file"
          accept="audio/*,.wav,.mp3,.ogg,.m4a,.flac"
          className="visually-hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) s.run(() => addFile(file));
          }}
        />
      </label>
      <Field label={`Głośność domyślna: ${Math.round(x.volume * 100)}%`}>
        <input type="range" min={0} max={2} step={0.05} value={x.volume} onChange={(e) => set({ volume: Number(e.target.value) })} />
      </Field>
      <fieldset className="cast-fieldset">
        <legend>Licencja i pochodzenie</legend>
        <div className="two-fields">
          <Field label="Licencja">
            <input value={x.license} placeholder="CC0, CC BY 4.0, własne nagranie…" onChange={(e) => set({ license: e.target.value })} />
          </Field>
          <Field label="Autor">
            <input value={x.author} onChange={(e) => set({ author: e.target.value })} />
          </Field>
        </div>
        <Field label="Źródło (URL)">
          <input value={x.source_url} onChange={(e) => set({ source_url: e.target.value })} />
        </Field>
        <Field label="Podpis do opisu filmu" hint="Wymagany przy CC BY — trafi do atrybucji.">
          <input value={x.attribution} onChange={(e) => set({ attribution: e.target.value })} />
        </Field>
      </fieldset>
      <div className="cast-savebar">
        <span className="muted small">{dirty ? "Niezapisane zmiany" : "Zapisano w banku kanału"}</span>
        <Button icon={Archive} subtle onClick={() => persist({ ...x, archived: !x.archived })} disabled={!x.file}>
          {x.archived ? "Przywróć" : "Archiwizuj"}
        </Button>
        <Button primary icon={Save} disabled={!dirty || !x.file} onClick={() => persist(x)}>
          Zapisz
        </Button>
      </div>
    </div>
  );
}

/** Draw regions (window, doorway) and the floor line on a state's background, in the same 16:9 crop as scenes. */
function RegionEditor({
  channelId,
  state,
  change,
}: {
  channelId: string;
  state: LocationState;
  change: (patch: Partial<LocationState>) => void;
}) {
  const [mode, setMode] = useState<"region" | "floor">("region");
  const [draft, setDraft] = useState<{ x0: number; y0: number; x1: number; y1: number } | null>(null);
  const regions = state.regions || [];
  const at = (e: React.PointerEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    return {
      x: Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)),
      y: Math.min(1, Math.max(0, (e.clientY - r.top) / r.height)),
    };
  };
  const round = (v: number) => Math.round(v * 1000) / 1000;
  const box = (d: NonNullable<typeof draft>) => ({
    x0: round(Math.min(d.x0, d.x1)),
    y0: round(Math.min(d.y0, d.y1)),
    x1: round(Math.max(d.x0, d.x1)),
    y1: round(Math.max(d.y0, d.y1)),
  });
  return (
    <div className="region-editor">
      <div className="button-row">
        <Button subtle={mode !== "region"} primary={mode === "region"} onClick={() => setMode("region")}>
          Rysuj obszar
        </Button>
        <Button subtle={mode !== "floor"} primary={mode === "floor"} onClick={() => setMode("floor")}>
          Ustaw podłogę
        </Button>
        <span className="muted small">
          {mode === "region"
            ? "Przeciągnij prostokąt na szybie okna, drzwiach, lustrze — postać przypisana do obszaru będzie nim przycięta."
            : "Kliknij na wysokości, na której stoją stopy postaci."}
        </span>
      </div>
      <div
        className="region-canvas"
        onPointerDown={(e) => {
          const p = at(e);
          if (mode === "floor") return change({ floor_y: round(p.y) });
          e.currentTarget.setPointerCapture(e.pointerId);
          setDraft({ x0: p.x, y0: p.y, x1: p.x, y1: p.y });
        }}
        onPointerMove={(e) => draft && setDraft({ ...draft, x1: at(e).x, y1: at(e).y })}
        onPointerUp={() => {
          if (!draft) return;
          const b = box(draft);
          setDraft(null);
          if (b.x1 - b.x0 < 0.02 || b.y1 - b.y0 < 0.02) return;
          const region: Region = {
            id: "reg_" + crypto.randomUUID().replace(/-/g, "").slice(0, 16),
            name: regions.length ? `Obszar ${regions.length + 1}` : "Okno",
            ...b,
          };
          change({ regions: [...regions, region] });
        }}
      >
        <img src={castImage(channelId, state.image!.file)} alt="" draggable={false} />
        {[...regions, ...(draft ? [{ id: "draft", name: "", ...box(draft) }] : [])].map((r) => (
          <span
            key={r.id}
            className="region-box"
            style={{ left: `${r.x0 * 100}%`, top: `${r.y0 * 100}%`, width: `${(r.x1 - r.x0) * 100}%`, height: `${(r.y1 - r.y0) * 100}%` }}
          >
            {r.name}
          </span>
        ))}
        {state.floor_y != null && (
          <span className="floor-line" style={{ top: `${state.floor_y * 100}%` }}>
            podłoga
          </span>
        )}
      </div>
      {regions.map((r) => (
        <div key={r.id} className="region-row">
          <input
            aria-label="Nazwa obszaru"
            value={r.name}
            onChange={(e) =>
              change({ regions: regions.map((x) => (x.id === r.id ? { ...x, name: e.target.value } : x)) })
            }
          />
          <IconButton icon={Trash2} label="Usuń obszar" onClick={() => change({ regions: regions.filter((x) => x.id !== r.id) })} />
        </div>
      ))}
    </div>
  );
}
