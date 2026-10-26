import { useState } from "react";
import {
  Upload,
  Library,
  Plus,
  Film,
  Music2,
  Image as ImageIcon,
  FileText,
} from "lucide-react";
import { useStudio } from "./context";
import { upload, mediaUrl } from "./api";
import { AssetThumb, Button, Empty, Modal, SectionHead } from "./components";
import type { Asset, Project } from "./types";
import { newClip, fps } from "./timing";

export default function LibraryView() {
  const s = useStudio(),
    p = s.project!;
  const [kind, setKind] = useState("all"),
    [preview, setPreview] = useState<Asset | null>(null),
    [busy, setBusy] = useState(false);
  const assets = p.assets.filter((a) => kind === "all" || a.kind === kind);
  async function add(file: File) {
    setBusy(true);
    try {
      const result = await upload<{ project: Project }>(
        "/projects/" + p.id + "/media",
        file,
      );
      s.accept(result.project);
      s.notify("Plik dodano do biblioteki");
    } finally {
      setBusy(false);
    }
  }
  async function place(a: Asset) {
    const c = newClip(
      a.kind === "audio" ? "a2" : "v1",
      a.id,
      Math.max(
        0,
        ...p.sequence.clips
          .filter((c) => c.track_id === (a.kind === "audio" ? "a2" : "v1"))
          .map((c) => c.start + c.duration),
      ),
      a.duration ? Math.floor(a.duration * fps(p)) : 180,
    );
    c.title = a.name;
    await s.edit([{ type: "add_clip", clip: c }]);
    s.notify("Dodano do montażu");
  }
  return (
    <div className="page-content">
      <SectionHead
        eyebrow="TWOJE MATERIAŁY"
        title="Biblioteka"
        description="Wybrane, wgrane i wygenerowane pliki w jednym miejscu."
      >
        <label className="button primary">
          <Upload size={16} />
          {busy ? "Wczytywanie…" : "Dodaj materiały"}
          <input
            type="file"
            multiple
            className="visually-hidden"
            accept="image/*,video/*,audio/*,.pdf,.epub,.txt,.md"
            onChange={(e) => {
              const files = Array.from(e.target.files || []);
              s.run(async () => {
                for (const file of files) await add(file);
              });
              e.target.value = "";
            }}
          />
        </label>
      </SectionHead>
      <div className="filter-pills">
        {[
          { id: "all", label: "Wszystko", icon: Library },
          { id: "image", label: "Zdjęcia", icon: ImageIcon },
          { id: "video", label: "Filmy", icon: Film },
          { id: "audio", label: "Audio", icon: Music2 },
          { id: "document", label: "Dokumenty", icon: FileText },
        ].map((item) => (
          <button
            key={item.id}
            className={kind === item.id ? "active" : ""}
            onClick={() => setKind(item.id)}
          >
            <item.icon size={15} />
            {item.label}
          </button>
        ))}
      </div>
      {!assets.length ? (
        <Empty icon={Library} title="Miejsce na Twoje materiały">
          Wgraj plik albo wybierz coś w Centrum źródeł.
        </Empty>
      ) : (
        <div className="library-grid">
          {assets.map((a) => (
            <div className="library-card surface" key={a.id}>
              <button
                className="media-preview-button"
                onClick={() => setPreview(a)}
              >
                <AssetThumb asset={a} project={p} />
              </button>
              <div className="library-card-body">
                <h3>{a.name}</h3>
                <p className="small muted">
                  {a.kind === "audio" || a.kind === "video"
                    ? a.duration.toFixed(1) + " s"
                    : a.width
                      ? a.width + " × " + a.height
                      : "Dokument źródłowy"}
                </p>
                <p className="small muted truncate">
                  {a.license || "Własny materiał"}
                </p>
                {a.kind !== "document" && (
                  <Button
                    subtle
                    icon={Plus}
                    onClick={() => s.run(() => place(a))}
                  >
                    Dodaj do montażu
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      <Modal
        open={!!preview}
        onClose={() => setPreview(null)}
        title={preview?.name || "Materiał"}
        wide
      >
        {preview?.kind === "image" ? (
          <img
            className="full-preview"
            src={mediaUrl(p.id, preview.id)}
            alt={preview.name}
          />
        ) : preview?.kind === "video" ? (
          <video
            className="full-preview"
            controls
            src={mediaUrl(p.id, preview.id)}
          />
        ) : preview?.kind === "audio" ? (
          <audio controls src={mediaUrl(p.id, preview.id)} />
        ) : (
          <p>Dokument jest dostępny w Centrum źródeł.</p>
        )}
        {preview?.prompt && (
          <p className="small muted">Prompt: {preview.prompt}</p>
        )}
      </Modal>
    </div>
  );
}
