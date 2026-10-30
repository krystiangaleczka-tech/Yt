import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { Button } from "./components";
import { LiveScene, type LiveSceneDef } from "./paperTheatreRenderer";

export type LiveSource = {
  def: LiveSceneDef;
  label: string;
  /** Exact frame from the MP4 renderer (only for a saved scene). */
  exactFrame?: (frame: number) => string;
};

const seconds = (frame: number, rate: number) =>
  (frame / rate).toFixed(2).replace(".", ",") + " s";

export default function PaperTheatreLive({ source, status }: { source: LiveSource | null; status?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [scene, setScene] = useState<LiveScene | null>(null);
  const [frame, setFrame] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [quality, setQuality] = useState(1);
  const [exact, setExact] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // Canvas work is flushed asynchronously by the browser, so timing draw()
  // would only measure command recording. Frames shown per second is honest.
  const [shownFps, setShownFps] = useState(0);
  const shown = useRef<number[]>([]);
  const frameRef = useRef(0);
  frameRef.current = frame;
  const def = source?.def;
  const total = Math.max(1, def?.durationFrames || 1);
  const rate = def?.fps || 30;
  const key = def ? JSON.stringify(def) : "";

  // A new definition (other cue, position, image) builds a new scene; sprites
  // for unchanged layers come from the renderer cache, so only edits cost.
  useEffect(() => {
    if (!def) { setScene(null); return; }
    let alive = true;
    setLoading(true);
    new LiveScene(def).load().then((next) => {
      if (!alive) return;
      try { next.warm(); setError(""); }
      catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); }
      setScene(next);
      setLoading(false);
    });
    return () => { alive = false; };
  }, [key]);

  useEffect(() => {
    if (frame >= total) setFrame(Math.max(0, total - 1));
  }, [total]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !scene) return;
    const w = Math.round(scene.def.width * quality), h = Math.round(scene.def.height * quality);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    try {
      scene.draw(ctx, Math.min(frame, total - 1));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
      setPlaying(false);
    }
  }, [scene, frame, quality, total]);

  useEffect(() => {
    if (!playing) return;
    let handle = 0, reported = 0;
    const startFrame = frameRef.current;
    const startTime = performance.now();
    shown.current = [];
    const tick = (now: number) => {
      const next = (startFrame + Math.floor((now - startTime) * rate / 1000)) % total;
      if (next !== frameRef.current) {
        setFrame(next);
        shown.current = [...shown.current.filter((t) => now - t < 1000), now];
      }
      if (now - reported > 500 && now - startTime > 1000) {
        reported = now;
        setShownFps(shown.current.length);
      }
      handle = requestAnimationFrame(tick);
    };
    handle = requestAnimationFrame(tick);
    return () => { cancelAnimationFrame(handle); setShownFps(0); };
  }, [playing, rate, total]);

  const step = (delta: number) => {
    setPlaying(false);
    setFrame((value) => Math.min(total - 1, Math.max(0, value + delta)));
  };
  const onKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.target instanceof HTMLInputElement && event.target.type !== "range") return;
    if (event.key === " ") { event.preventDefault(); setPlaying((value) => !value); }
    if (event.key === "ArrowLeft") { event.preventDefault(); step(event.shiftKey ? -10 : -1); }
    if (event.key === "ArrowRight") { event.preventDefault(); step(event.shiftKey ? 10 : 1); }
  };
  const showExact = exact && !playing && !!source?.exactFrame;

  return (
    <section aria-label="Podgląd na żywo" tabIndex={0} onKeyDown={onKey} style={{ outline: "none", marginBottom: 16 }}>
      <h2>Podgląd na żywo · bez renderu</h2>
      <div style={{ position: "relative", aspectRatio: def ? `${def.width} / ${def.height}` : "16 / 9",
                    background: "#10151e", borderRadius: 8, overflow: "hidden" }}>
        <canvas ref={canvasRef} aria-label="Klatka sceny Paper Theatre liczona w przeglądarce"
          style={{ width: "100%", height: "100%", display: "block" }} />
        {showExact && <img alt="Dokładna klatka z renderera MP4" src={source!.exactFrame!(frame)}
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain" }} />}
        {(!source || loading) && <p className="small muted" style={{ position: "absolute", left: 12, top: 8, margin: 0 }}>
          {!source ? status || "Brak sceny do podglądu" : "Wczytuję wycinki…"}</p>}
      </div>
      <input type="range" min={0} max={total - 1} step={1} value={Math.min(frame, total - 1)}
        aria-label="Czas ujęcia" disabled={!scene}
        onChange={(event) => { setPlaying(false); setFrame(Number(event.target.value)); }}
        style={{ width: "100%", marginTop: 8 }} />
      <div className="button-row">
        <Button icon={playing ? Pause : Play} primary disabled={!scene} onClick={() => setPlaying((value) => !value)}>
          {playing ? "Pauza" : "Odtwórz"}
        </Button>
        <Button icon={ChevronLeft} disabled={!scene} onClick={() => step(-1)} aria-label="Poprzednia klatka">Klatka</Button>
        <Button icon={ChevronRight} disabled={!scene} onClick={() => step(1)} aria-label="Następna klatka">Klatka</Button>
        <select value={quality} aria-label="Jakość podglądu" onChange={(event) => setQuality(Number(event.target.value))}>
          <option value={1}>Pełna rozdzielczość</option>
          <option value={.5}>Połowa (słabszy komputer)</option>
        </select>
        {source?.exactFrame && <label className="small">
          <input type="checkbox" checked={exact} onChange={(event) => setExact(event.target.checked)} />
          {" "}Pokaż dokładną klatkę z renderera MP4 (po pauzie)
        </label>}
      </div>
      <p className="small muted" aria-live="polite">
        {source?.label ? source.label + " · " : ""}
        {seconds(Math.min(frame, total - 1), rate)} / {seconds(total, rate)} · klatka {Math.min(frame, total - 1) + 1}/{total}
        {playing && shownFps ? ` · płynność ${Math.min(shownFps, Math.round(rate))}/${Math.round(rate)} kl./s` : ""}
        {scene?.missing ? ` · brak ${scene.missing} obrazów` : ""}
        {status ? " · " + status : ""}
      </p>
      {error && <p className="small" role="alert">{error}</p>}
      <p className="small muted">
        Spacja: odtwórz/pauza · strzałki: klatka (Shift: 10 klatek). Czasy i pozycje
        liczone są tymi samymi wzorami co eksport MP4; obraz może różnić się
        minimalnie wygładzaniem i rozmyciem cienia. Dokładną klatkę pokazuje renderer.
      </p>
    </section>
  );
}
