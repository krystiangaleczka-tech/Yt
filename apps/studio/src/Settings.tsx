import { useEffect, useState } from "react";
import { KeyRound, Plug, Plus, Check, Settings2 } from "lucide-react";
import { useStudio } from "./context";
import { api, id } from "./api";
import { Button, Field, Modal } from "./components";
type Custom = {
  id: string;
  name: string;
  url: string;
  kind: string;
  results_path: string;
  mapping: Record<string, string>;
};
type Settings = {
  pixabay_configured: boolean;
  pexels_configured: boolean;
  ai_configured: boolean;
  ai_base_url: string;
  ai_model: string;
  ai_request_cost: number;
  paper_image_configured: boolean;
  paper_image_model: string;
  paper_image_request_cost: number;
  custom: Custom[];
};
export default function SettingsPanel() {
  const s = useStudio();
  const [settings, setSettings] = useState<Settings | null>(null),
    [pixabay, setPixabay] = useState(""),
    [pexels, setPexels] = useState(""),
    [key, setKey] = useState(""),
    [base, setBase] = useState(""),
    [model, setModel] = useState(""),
    [cost, setCost] = useState("0"),
    [paperImageKey, setPaperImageKey] = useState(""),
    [paperImageModel, setPaperImageModel] = useState("gpt-image-2.5-sunburst"),
    [paperImageCost, setPaperImageCost] = useState("0"),
    [authorization, setAuthorization] = useState(""),
    [header, setHeader] = useState("Authorization"),
    [name, setName] = useState(""),
    [url, setUrl] = useState(""),
    [path, setPath] = useState("results"),
    [kind, setKind] = useState("information"),
    [mapping, setMapping] = useState(
      '{"title":"title","url":"url","description":"description"}',
    ),
    [saving, setSaving] = useState(false);
  useEffect(() => {
    if (s.settingsOpen)
      s.run(async () => {
        const data = await api<Settings>("/settings");
        setSettings(data);
        setBase(data.ai_base_url);
        setModel(data.ai_model);
        setCost(String(data.ai_request_cost || 0));
        setPaperImageModel(data.paper_image_model || "gpt-image-2.5-sunburst");
        setPaperImageCost(String(data.paper_image_request_cost || 0));
      });
  }, [s.settingsOpen]);
  async function save() {
    setSaving(true);
    try {
      const changes: Record<string, unknown> = {
        ai_base_url: base,
        ai_model: model,
        ai_request_cost: Number(cost),
        paper_image_model: paperImageModel,
        paper_image_request_cost: Number(paperImageCost),
      };
      if (pixabay) changes.pixabay_key = pixabay;
      if (pexels) changes.pexels_key = pexels;
      if (key) changes.ai_key = key;
      if (paperImageKey) changes.paper_image_key = paperImageKey;
      const next = await api<Settings>("/settings", changes, "PATCH");
      setSettings(next);
      setPixabay("");
      setPexels("");
      setKey("");
      setPaperImageKey("");
      await s.reload();
      s.notify("Zapisano ustawienia połączeń");
    } finally {
      setSaving(false);
    }
  }
  async function addCustom() {
    const parsed = JSON.parse(mapping);
    if (!name.trim() || !url.includes("{query}"))
      throw new Error("Podaj nazwę i adres zawierający {query}");
    const next = await api<Settings>(
      "/settings",
      {
        custom: [
          ...(settings?.custom || []),
          {
            id: id("custom_"),
            name,
            url,
            kind,
            results_path: path,
            mapping: parsed,
            ...(authorization ? { headers: { [header]: authorization } } : {}),
          },
        ],
      },
      "PATCH",
    );
    setSettings(next);
    setName("");
    setUrl("");
    setAuthorization("");
    s.notify("Dodano własne źródło");
  }
  return (
    <Modal
      open={s.settingsOpen}
      onClose={() => s.setSettingsOpen(false)}
      title="Połączenia i ustawienia"
      description="Twoje źródła, modele i lokalne środowisko"
      wide
    >
      <div className="settings-grid">
        <section>
          <h3>
            <Plug size={17} />
            Dostawcy materiałów
          </h3>
          <Field
            label={`Klucz Pixabay ${settings?.pixabay_configured ? "· zapisany" : ""}`}
          >
            <input
              type="password"
              autoComplete="off"
              value={pixabay}
              onChange={(e) => setPixabay(e.target.value)}
              placeholder={
                settings?.pixabay_configured
                  ? "Wpisz, aby zastąpić"
                  : "Klucz API Pixabay"
              }
            />
          </Field>
          <Field
            label={`Klucz Pexels ${settings?.pexels_configured ? "· zapisany" : ""}`}
          >
            <input
              type="password"
              autoComplete="off"
              value={pexels}
              onChange={(e) => setPexels(e.target.value)}
              placeholder="Opcjonalny dostęp API"
            />
          </Field>
          <p className="small muted">
            Commons, Open Library, Google Books i Crossref działają bez
            wpisywania klucza w Studio. Dostępność zapytania zależy od dostawcy.
          </p>
        </section>
        <section>
          <h3>
            <KeyRound size={17} />
            Asystent AI
          </h3>
          <Field label="Adres API zgodnego z Chat Completions">
            <input
              value={base}
              onChange={(e) => setBase(e.target.value)}
              placeholder="https://dostawca.example/v1"
            />
          </Field>
          <Field label="Model">
            <input
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="Nazwa modelu u dostawcy"
            />
          </Field>
          <Field
            label={`Klucz API ${settings?.ai_configured ? "· zapisany" : ""}`}
          >
            <input
              type="password"
              autoComplete="off"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="Klucz pozostaje na Twoim komputerze"
            />
          </Field>
          <Field label="Szacowany koszt jednego wywołania API">
            <input
              type="number"
              min="0"
              step="0.001"
              value={cost}
              onChange={(e) => setCost(e.target.value)}
            />
          </Field>
          <p className="small muted">
            Możesz też korzystać z zalogowanego Claude CLI lub przenosić prompt
            i odpowiedź ręcznie.
          </p>
        </section>
        <section>
          <h3>Paper Theatre · osobne PNG alpha z referencji</h3>
          <p className="small muted">
            Opcjonalnie OpenAI Images API. Referencja jest wysyłana dopiero po Twoim
            kliknięciu w kreatorze wycinków. Brak klucza nie blokuje ręcznego importu PNG.
          </p>
          <Field label="Model obrazu">
            <select value={paperImageModel} onChange={(e) => setPaperImageModel(e.target.value)}>
              <option value="gpt-image-2.5-sunburst">GPT Image 2.5 Sunburst</option>
              <option value="gpt-image-2.5-flare">GPT Image 2.5 Flare</option>
            </select>
          </Field>
          <Field label={`Klucz API obrazów ${settings?.paper_image_configured ? "· zapisany" : ""}`}>
            <input type="password" autoComplete="off" value={paperImageKey}
              onChange={(e) => setPaperImageKey(e.target.value)}
              placeholder="Prywatny klucz OpenAI API obrazów" />
          </Field>
          <Field label="Oszacowany maksymalny koszt jednego wycinka (USD)">
            <input type="number" min=".001" step=".001" value={paperImageCost}
              onChange={(e) => setPaperImageCost(e.target.value)} />
          </Field>
          <p className="small muted">
            Ustal koszt według cennika dostawcy. Projekt musi mieć dodatni limit API.
            Aplikacja rezerwuje szacunkowy koszt każdej próby, także nieudanej.
          </p>
        </section>
      </div>
      <Button primary icon={Check} busy={saving} onClick={() => s.run(save)}>
        Zapisz połączenia
      </Button>
      <div className="panel-divider" />
      <section className="local-engines">
        <h3>
          <Settings2 size={17} />
          Generowanie lokalne
        </h3>
        <p className="small muted">
          Obrazy:{" "}
          {s.health?.image
            ? "środowisko znalezione"
            : "wymaga środowiska Stable Diffusion"}
          . Lektor:{" "}
          {s.health?.voice
            ? "środowisko i próbka znalezione"
            : "wymaga Chatterbox i próbki głosu"}
          .
        </p>
        <p className="small muted">
          Ustaw przed uruchomieniem: <code>DOCOS_IMAGE_PYTHON</code>,{" "}
          <code>DOCOS_TTS_PYTHON</code>, <code>DOCOS_VOICE_REF</code>. Szczegóły
          instalacji są w <code>docs/STUDIO.md</code>. Własne media działają bez
          modeli.
        </p>
      </section>
      <div className="panel-divider" />
      <section>
        <h3>
          <Plus size={17} />
          Własne źródło JSON
        </h3>
        {settings?.custom.map((c) => (
          <div className="custom-source-row" key={c.id}>
            <strong>{c.name}</strong>
            <span className="small muted">{c.kind}</span>
            <Button
              subtle
              onClick={() =>
                s.run(async () => {
                  setSettings(
                    await api<Settings>(
                      "/settings",
                      { custom: settings.custom.filter((x) => x.id !== c.id) },
                      "PATCH",
                    ),
                  );
                  s.notify("Usunięto połączenie");
                })
              }
            >
              Usuń
            </Button>
          </div>
        ))}
        <div className="two-fields">
          <Field label="Nazwa">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Moje archiwum"
            />
          </Field>
          <Field label="Typ treści">
            <select value={kind} onChange={(e) => setKind(e.target.value)}>
              <option value="information">Informacje</option>
              <option value="image">Zdjęcia</option>
              <option value="video">Filmy</option>
              <option value="book">Książki</option>
            </select>
          </Field>
        </div>
        <Field label="Publiczny adres API z {query}">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://archiwum.example/api?q={query}"
          />
        </Field>
        <div className="two-fields">
          <Field label="Ścieżka do listy wyników">
            <input
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="results lub pozostaw puste"
            />
          </Field>
          <Field label="Mapowanie pól JSON">
            <input
              value={mapping}
              onChange={(e) => setMapping(e.target.value)}
            />
          </Field>
        </div>
        <div className="two-fields">
          <Field label="Nazwa nagłówka uwierzytelnienia">
            <input value={header} onChange={(e) => setHeader(e.target.value)} />
          </Field>
          <Field label="Prywatna wartość nagłówka">
            <input
              type="password"
              autoComplete="off"
              value={authorization}
              onChange={(e) => setAuthorization(e.target.value)}
              placeholder="Bearer …"
            />
          </Field>
        </div>
        <p className="small muted">
          Użyj {"{query}"} i opcjonalnie {"{page}"} w adresie API. Nagłówki nie
          są zwracane do przeglądarki ani eksportowane.
        </p>
        <div className="button-row">
          {[
            "commons",
            "pixabay",
            "pexels",
            "openlibrary",
            "googlebooks",
            "crossref",
            ...(settings?.custom.map((c) => c.id) || []),
          ].map((provider) => (
            <Button
              subtle
              key={provider}
              onClick={() =>
                s.run(async () => {
                  const r = await api<{ ok: boolean; message: string }>(
                    `/connectors/${provider}/test`,
                    {},
                  );
                  s.notify(r.message, !r.ok);
                })
              }
            >
              Test {provider}
            </Button>
          ))}
        </div>
        <Button icon={Plus} onClick={() => s.run(addCustom)}>
          Dodaj źródło
        </Button>
      </section>
    </Modal>
  );
}
