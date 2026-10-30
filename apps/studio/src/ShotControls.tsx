import { useEffect, useRef, useState } from "react";
import { Pause, Play, SkipBack, SkipForward } from "lucide-react";
import { IconButton } from "./components";
import { time } from "./timing";

export function useShotPlayback(
  total: number,
  rate: number,
  resetKey: string,
  externalClock = false,
) {
  const [frame, setFrame] = useState(0),
    [playing, setPlaying] = useState(false);
  const current = useRef({ frame, total, rate });
  current.current = { frame, total, rate };
  useEffect(() => {
    setPlaying(false);
    setFrame(0);
  }, [resetKey]);
  useEffect(() => {
    setFrame((value) => Math.min(value, Math.max(0, total - 1)));
  }, [total]);
  useEffect(() => {
    if (!playing || externalClock) return;
    const start = performance.now(),
      from = current.current.frame;
    let handle = 0;
    function tick(now: number) {
      const next =
        from + Math.floor(((now - start) * current.current.rate) / 1000);
      if (next >= current.current.total) {
        setFrame(Math.max(0, current.current.total - 1));
        setPlaying(false);
      } else {
        setFrame(next);
        handle = requestAnimationFrame(tick);
      }
    }
    handle = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(handle);
  }, [playing, externalClock]);
  useEffect(() => {
    const pause = () => {
      if (document.hidden) setPlaying(false);
    };
    document.addEventListener("visibilitychange", pause);
    return () => document.removeEventListener("visibilitychange", pause);
  }, []);
  return {
    frame,
    playing,
    setPlaying,
    setFrame,
    seek: (value: number) => {
      setPlaying(false);
      setFrame(Math.max(0, Math.min(total - 1, value)));
    },
    toggle: () => {
      if (!playing && frame >= total - 1) setFrame(0);
      setPlaying(!playing);
    },
  };
}

export function ShotTransport({
  playback,
  total,
  rate,
}: {
  playback: ReturnType<typeof useShotPlayback>;
  total: number;
  rate: number;
}) {
  return (
    <div className="shot-transport">
      <IconButton
        icon={SkipBack}
        label="Początek ujęcia"
        onClick={() => playback.seek(0)}
      />
      <IconButton
        icon={playback.playing ? Pause : Play}
        label={playback.playing ? "Pauza" : "Odtwórz ujęcie"}
        onClick={playback.toggle}
      />
      <IconButton
        icon={SkipForward}
        label="Ostatnia klatka ujęcia"
        onClick={() => playback.seek(total - 1)}
      />
      <input
        type="range"
        min={0}
        max={Math.max(0, total - 1)}
        value={playback.frame}
        step={1}
        aria-label="Pozycja w ujęciu"
        onChange={(e) => playback.seek(Number(e.target.value))}
      />
      <span className="timecode">
        {time(playback.frame, rate, true)} / {time(total, rate, true)}
      </span>
    </div>
  );
}

export type ShotTrack = {
  id: string;
  name: string;
  start: number;
  duration: number;
  kind?: "audio" | "visual";
  movable?: boolean;
};
export function ShotTimeline({
  rows,
  seconds,
  frame,
  rate,
  selected,
  onSelect,
  onSeek,
  onMove,
}: {
  rows: ShotTrack[];
  seconds: number;
  frame: number;
  rate: number;
  selected?: string;
  onSelect: (id: string) => void;
  onSeek: (frame: number) => void;
  onMove?: (id: string, seconds: number) => void;
}) {
  const [drag, setDrag] = useState<{
    id: string;
    x: number;
    width: number;
    original: number;
    at: number;
  } | null>(null);
  const duration = Math.max(0.001, seconds);
  return (
    <section
      className="shot-timeline surface"
      aria-label="Oś czasu wybranego ujęcia"
    >
      <div className="shot-panel-heading">
        <strong>Timeline ujęcia</strong>
        <span className="muted small">
          {seconds.toFixed(2)} s · {rate.toFixed(2)} kl./s
        </span>
      </div>
      <div className="shot-timeline-scroll">
        <div className="shot-timeline-content">
          <div className="shot-track">
            <span className="shot-track-name small muted">WARSTWY</span>
            <div className="shot-ruler">
              {[0, 0.25, 0.5, 0.75, 1].map((part) => (
                <span key={part} style={{ left: `${part * 100}%` }}>
                  {(seconds * part).toFixed(1)} s
                </span>
              ))}
            </div>
          </div>
          {rows.map((row) => {
            const start = drag?.id === row.id ? drag.at : row.start;
            return (
              <div
                className={`shot-track ${selected === row.id ? "active" : ""}`}
                key={row.id}
              >
                <button
                  className="shot-track-name"
                  title={row.name}
                  onClick={() => onSelect(row.id)}
                >
                  {row.name}
                </button>
                <div
                  className="shot-track-lane"
                  onClick={(event) => {
                    const rect = event.currentTarget.getBoundingClientRect();
                    onSeek(
                      Math.round(
                        ((event.clientX - rect.left) / rect.width) *
                          seconds *
                          rate,
                      ),
                    );
                  }}
                >
                  <button
                    className={`shot-track-block ${row.kind || "visual"}`}
                    aria-label={`Warstwa: ${row.name}`}
                    title={
                      row.movable
                        ? "Przeciągnij, aby zmienić czas wejścia"
                        : row.name
                    }
                    style={{
                      left: `${(Math.min(duration, Math.max(0, start)) / duration) * 100}%`,
                      width: `${(Math.max(0, Math.min(duration - Math.max(0, start), row.duration)) / duration) * 100}%`,
                    }}
                    onClick={(event) => {
                      event.stopPropagation();
                      onSelect(row.id);
                    }}
                    onPointerDown={(event) => {
                      onSelect(row.id);
                      if (!row.movable || !onMove) return;
                      event.currentTarget.setPointerCapture(event.pointerId);
                      setDrag({
                        id: row.id,
                        x: event.clientX,
                        width:
                          event.currentTarget.parentElement!.getBoundingClientRect()
                            .width,
                        original: row.start,
                        at: row.start,
                      });
                    }}
                    onPointerMove={(event) => {
                      if (drag?.id !== row.id) return;
                      setDrag({
                        ...drag,
                        at: Math.max(
                          0,
                          Math.min(
                            seconds - 1 / rate,
                            drag.original +
                              ((event.clientX - drag.x) / drag.width) * seconds,
                          ),
                        ),
                      });
                    }}
                    onPointerUp={(event) => {
                      if (drag?.id !== row.id) return;
                      if (Math.abs(event.clientX - drag.x) > 3)
                        onMove?.(row.id, Math.round(drag.at * rate) / rate);
                      setDrag(null);
                    }}
                    onPointerCancel={() => setDrag(null)}
                  >
                    {row.name}
                  </button>
                  <span
                    className="shot-lane-playhead"
                    style={{ left: `${(frame / rate / duration) * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
          {!rows.length && (
            <p className="small muted">Dodaj pierwszy asset do ujęcia.</p>
          )}
        </div>
      </div>
    </section>
  );
}
