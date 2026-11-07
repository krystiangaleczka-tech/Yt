import { useEffect, useRef, useState } from "react";
import { Airplay, Pause, Play } from "lucide-react";
import { api } from "./api";
import { useStudio } from "./context";
import { Button, IconButton } from "./components";

// Safari udostępnia AirPlay tylko przez element wideo z tymi rozszerzeniami WebKit.
type AirPlayVideo = HTMLVideoElement & {
  webkitShowPlaybackTargetPicker?: () => void;
  webkitCurrentPlaybackTargetIsWireless?: boolean;
};
type State = "idle" | "casting" | "paused";

function clock(seconds: number) {
  const s = Math.max(0, Math.floor(seconds));
  const h = Math.floor(s / 3600),
    m = Math.floor((s % 3600) / 60),
    r = s % 60;
  return (
    (h ? h + ":" + String(m).padStart(2, "0") : String(m)) +
    ":" +
    String(r).padStart(2, "0")
  );
}

/**
 * Przycisk AirPlay: wysyła na telewizor strumień HLS ze Studio (ujęcia po kolei albo oś montażu). Telewizor sam pobiera
 * strumień, więc adres musi być w sieci lokalnej, nie localhost. Pozycję z telewizora zgłasza onTime, żeby Studio
 * pokazywało, co jest na ekranie.
 */
export default function AirPlayButton({
  label,
  title,
  path,
  onStart,
  onTime,
  onEnd,
}: {
  label: string;
  title: string;
  /** Ścieżka playlisty w API (bez /api), liczona w chwili kliknięcia — np. od wybranego ujęcia. */
  path: () => string;
  onStart?: () => void;
  onTime?: (seconds: number) => void;
  onEnd?: () => void;
}) {
  const s = useStudio();
  const video = useRef<AirPlayVideo>(null),
    address = useRef<string | null>(null),
    available = useRef<boolean | null>(null),
    live = useRef({ onStart, onTime, onEnd, notify: s.notify });
  live.current = { onStart, onTime, onEnd, notify: s.notify };
  const [state, setState] = useState<State>("idle"),
    [shown, setShown] = useState(title),
    [time, setTime] = useState(0),
    [length, setLength] = useState(0);
  const stateRef = useRef<State>("idle");
  stateRef.current = state;
  useEffect(() => {
    void api<{ address: string | null }>("/tv/address")
      .then((r) => (address.current = r.address))
      .catch(() => {});
    const v = video.current;
    if (!v) return;
    const availability = (e: Event) =>
      (available.current =
        (e as Event & { availability?: string }).availability === "available");
    const route = () => {
      if (v.webkitCurrentPlaybackTargetIsWireless) {
        setState("casting");
        live.current.onStart?.();
        // Bez gestu użytkownika Safari może odmówić startu: wtedy panel pokazuje Play.
        v.play().catch(() => setState("paused"));
      } else if (stateRef.current !== "idle") stop();
    };
    const failed = () => {
      if (stateRef.current === "idle" || !v.getAttribute("src")) return;
      live.current.notify(
        "Telewizor nie pobrał obrazu. Studio musi działać przez npm run dev, a Mac i telewizor muszą być w tej samej sieci (zapora macOS może pytać o zgodę dla node).",
        true,
      );
      stop();
    };
    const ended = () => stop();
    const playing = () => {
      if (v.webkitCurrentPlaybackTargetIsWireless) setState("casting");
    };
    const paused = () => {
      if (stateRef.current === "casting") setState("paused");
    };
    v.addEventListener("webkitplaybacktargetavailabilitychanged", availability);
    v.addEventListener("webkitcurrentplaybacktargetiswirelesschanged", route);
    v.addEventListener("error", failed);
    v.addEventListener("ended", ended);
    v.addEventListener("playing", playing);
    v.addEventListener("pause", paused);
    return () => {
      v.removeEventListener(
        "webkitplaybacktargetavailabilitychanged",
        availability,
      );
      v.removeEventListener(
        "webkitcurrentplaybacktargetiswirelesschanged",
        route,
      );
      v.removeEventListener("error", failed);
      v.removeEventListener("ended", ended);
      v.removeEventListener("playing", playing);
      v.removeEventListener("pause", paused);
      v.pause();
      v.removeAttribute("src");
      v.load();
    };
  }, []);
  useEffect(() => {
    if (state === "idle") return;
    const timer = setInterval(() => {
      const v = video.current;
      if (!v) return;
      setTime(v.currentTime);
      if (Number.isFinite(v.duration)) setLength(v.duration);
      live.current.onTime?.(v.currentTime);
    }, 500);
    return () => clearInterval(timer);
  }, [state]);
  function stop() {
    stateRef.current = "idle"; // zdarzenie pause z v.pause() nie może już przełączyć panelu na „wstrzymane”
    const v = video.current;
    if (v) {
      v.pause();
      v.removeAttribute("src");
      v.load();
    }
    setState("idle");
    setTime(0);
    setLength(0);
    live.current.onEnd?.();
  }
  function open() {
    const v = video.current;
    if (!v?.webkitShowPlaybackTargetPicker) {
      s.notify(
        "AirPlay działa w Safari. Otwórz Studio w Safari, żeby wysłać obraz na telewizor.",
        true,
      );
      return;
    }
    if (available.current === false) {
      s.notify(
        "Safari nie widzi urządzeń AirPlay. Sprawdź, czy telewizor jest włączony i w tej samej sieci co Mac.",
        true,
      );
      return;
    }
    // Wszystko synchronicznie w kliknięciu: Safari pokazuje wybór urządzenia tylko w geście użytkownika.
    const origin = address.current
      ? `${location.protocol}//${address.current}${location.port ? ":" + location.port : ""}`
      : location.origin;
    if (
      v.webkitCurrentPlaybackTargetIsWireless &&
      stateRef.current !== "idle"
    ) {
      // Już połączone: nowy strumień od bieżącego miejsca, bez ponownego wyboru telewizora.
      v.src = origin + "/api" + path();
      setShown(title);
      live.current.onStart?.();
      void v.play().catch(() => setState("paused"));
      return;
    }
    v.src = origin + "/api" + path();
    setShown(title);
    v.webkitShowPlaybackTargetPicker();
  }
  return (
    <>
      <IconButton
        icon={Airplay}
        label={state === "idle" ? label : label + " — wyślij od tego miejsca"}
        aria-pressed={state !== "idle"}
        className={`icon-button ${state !== "idle" ? "airplay-on" : ""}`}
        onClick={open}
      />
      <video
        ref={video}
        className="airplay-video"
        x-webkit-airplay="allow"
        preload="none"
        playsInline
      />
      {state !== "idle" && (
        <div className="airplay-panel" role="status">
          <Airplay size={16} />
          <div>
            <strong>Na telewizorze</strong>
            <span>
              {shown} · {clock(time)}
              {length ? " / " + clock(length) : ""}
            </span>
          </div>
          <IconButton
            icon={state === "casting" ? Pause : Play}
            label={
              state === "casting"
                ? "Pauza na telewizorze"
                : "Odtwórz na telewizorze"
            }
            onClick={() => {
              const v = video.current;
              if (!v) return;
              if (state === "casting") v.pause();
              else void v.play().catch(() => {});
            }}
          />
          <Button subtle onClick={stop}>
            Zakończ
          </Button>
        </div>
      )}
    </>
  );
}
