import { useEffect, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { Button, NumberField } from "./components";

/** Non-destructive alpha editing: 'restore' can only use pixels from the source PNG. */
export default function PaperCutoutMaskEditor({
  src, onSave,
}: {
  src: string;
  onSave: (png: Blob) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sourceRef = useRef<HTMLImageElement | null>(null);
  const historyRef = useRef<ImageData[]>([]);
  const paintingRef = useRef(false);
  const [mode, setMode] = useState<"erase" | "restore">("erase");
  const [brush, setBrush] = useState(30);
  const [revision, setRevision] = useState(0);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const image = new Image();
    sourceRef.current = null;
    historyRef.current = [];
    setReady(false);
    setError("");
    image.onload = () => {
      if (cancelled) return;
      const canvas = canvasRef.current;
      if (!canvas) return;
      if (image.width > 4096 || image.height > 4096) {
        setError("Maska w edytorze obsługuje PNG do 4096 × 4096 pikseli.");
        return;
      }
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) {
        setError("Przeglądarka nie obsługuje edycji maski.");
        return;
      }
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, 0, 0);
      sourceRef.current = image;
      setReady(true);
    };
    image.onerror = () => {
      if (!cancelled) setError("Nie udało się odczytać pliku PNG do edycji maski.");
    };
    image.src = src;
    return () => { cancelled = true; };
  }, [src]);

  const paint = (event: ReactPointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    const original = sourceRef.current;
    if (!canvas || !original || !paintingRef.current) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const x = (event.clientX - rect.left) * canvas.width / rect.width;
    const y = (event.clientY - rect.top) * canvas.height / rect.height;
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, brush / 2, 0, Math.PI * 2);
    if (mode === "erase") {
      ctx.globalCompositeOperation = "destination-out";
      ctx.fillStyle = "#fff";
      ctx.fill();
    } else {
      // Clip to the brush, redraw only source pixels: no fabricated hidden detail.
      ctx.clip();
      ctx.globalCompositeOperation = "source-over";
      ctx.drawImage(original, 0, 0);
    }
    ctx.restore();
    setRevision((n) => n + 1);
  };

  const start = (event: ReactPointerEvent<HTMLCanvasElement>) => {
    if (!ready) return;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return;
    historyRef.current.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
    if (historyRef.current.length > 15) historyRef.current.shift();
    paintingRef.current = true;
    canvas.setPointerCapture(event.pointerId);
    paint(event);
  };

  const undo = () => {
    const data = historyRef.current.pop(), canvas = canvasRef.current;
    if (data && canvas) {
      canvas.getContext("2d")?.putImageData(data, 0, 0);
      setRevision((n) => n + 1);
    }
  };

  const reset = () => {
    const ctx = canvasRef.current?.getContext("2d");
    const img = sourceRef.current;
    if (ctx && img) {
      historyRef.current = [];
      ctx.clearRect(0, 0, img.width, img.height);
      ctx.drawImage(img, 0, 0);
      setRevision((n) => n + 1);
    }
  };

  const save = () => {
    const canvas = canvasRef.current;
    if (!canvas || !ready) return;
    canvas.toBlob((blob) => {
      if (blob) onSave(blob);
      else setError("Nie udało się wyeksportować przezroczystego PNG.");
    }, "image/png");
  };

  return (
    <div className="surface" style={{ padding: 12, marginTop: 10 }}>
      <h4>Maska alpha tego jednego wycinka</h4>
      <p className="small muted">
        Usuń niechciane fragmenty pędzlem. „Przywróć” odtwarza wyłącznie piksele
        już obecne w oryginalnym PNG. Nie rekonstruuje zasłoniętych fragmentów.
      </p>
      <div className="button-row">
        <Button primary={mode === "erase"} onClick={() => setMode("erase")}>Wymaż alpha</Button>
        <Button primary={mode === "restore"} onClick={() => setMode("restore")}>Przywróć z oryginału</Button>
      </div>
      <NumberField label="Rozmiar pędzla (piksele oryginału)"
        value={brush} min={4} max={160} step={2} onCommit={setBrush} />
      <canvas
        ref={canvasRef}
        aria-label="Edytor maski wycinka PNG"
        onPointerDown={start}
        onPointerMove={paint}
        onPointerUp={(event) => {
          paintingRef.current = false;
          if (event.currentTarget.hasPointerCapture(event.pointerId))
            event.currentTarget.releasePointerCapture(event.pointerId);
        }}
        onPointerCancel={() => { paintingRef.current = false; }}
        style={{
          display: "block", maxWidth: "100%", width: "100%", height: "auto",
          minHeight: 120, border: "1px solid var(--border, #777)", borderRadius: 8,
          touchAction: "none", cursor: "crosshair",
          backgroundColor: "#d0c8b6",
          backgroundImage: "linear-gradient(45deg,#b1aba0 25%,transparent 25%),linear-gradient(-45deg,#b1aba0 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#b1aba0 75%),linear-gradient(-45deg,transparent 75%,#b1aba0 75%)",
          backgroundSize: "24px 24px", backgroundPosition: "0 0,0 12px,12px -12px,-12px 0",
        }}
      />
      {error && <p role="alert">{error}</p>}
      <div className="button-row">
        <Button onClick={undo} disabled={!ready || revision === 0}>Cofnij pociągnięcie</Button>
        <Button onClick={reset} disabled={!ready}>Przywróć oryginał</Button>
        <Button primary onClick={save} disabled={!ready}>Zapisz jako nowy PNG</Button>
      </div>
    </div>
  );
}
