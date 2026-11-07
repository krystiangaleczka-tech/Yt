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
// Safari na Macu otwiera wybór urządzeń AirPlay tylko dla wideo z wczytanymi metadanymi (inaczej po cichu nic nie
// robi). Dlatego odtwarzacz od razu trzyma malutki strumień próbny, a właściwy strumień dostaje dopiero po wybraniu
// telewizora; połączenie AirPlay zostaje przy elemencie. W chwili połączenia telewizor dostaje adres tego, co odtwarzacz
// trzyma, więc także strumień próbny idzie z adresu w sieci lokalnej (localhost telewizor by zawiesił).
const PROBE = "/api/tv/probe.m3u8";

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
 * strumień, więc adres musi być w sieci lokalnej, nie localhost. Komputer w tym czasie nic nie odtwarza: pozycja
 * z telewizora jest tylko w panelu (describe), a po zakończeniu onEnd dostaje miejsce, w którym telewizor skończył.
 */
export default function AirPlayButton({
  label,
  title,
  path,
  onStart,
  describe,
  onEnd,
}: {
  label: string;
  title: string;
  /** Ścieżka playlisty w API (bez /api), liczona w chwili kliknięcia — np. od wybranego ujęcia. */
  path: () => string;
  onStart?: () => void;
  /** Opis pozycji telewizora do panelu, np. „ujęcie 44 / 689” albo czas filmu. */
  describe?: (seconds: number) => string;
  /** Koniec wysyłania; seconds to ostatnia pozycja telewizora w strumieniu. */
  onEnd?: (seconds: number) => void;
}) {
  const s = useStudio();
  const video = useRef<AirPlayVideo>(null),
    address = useRef<string | null>(null),
    available = useRef<boolean | null>(null),
    // Strumień, który ma pójść na telewizor po wybraniu urządzenia w oknie AirPlay.
    pending = useRef<string | null>(null),
    last = useRef(0),
    live = useRef({ onStart, onEnd, notify: s.notify });
  live.current = { onStart, onEnd, notify: s.notify };
  const [state, setState] = useState<State>("idle"),
    [shown, setShown] = useState(title),
    [time, setTime] = useState(0),
    [length, setLength] = useState(0);
  const stateRef = useRef<State>("idle");
  stateRef.current = state;
  // Adres Studio widziany z telewizora: IP Maca w sieci lokalnej i port strony (Vite przekazuje /api dalej).
  function origin() {
    return address.current
      ? `${location.protocol}//${address.current}${location.port ? ":" + location.port : ""}`
      : location.origin;
  }
  function probe() {
    const v = video.current;
    if (!v?.webkitShowPlaybackTargetPicker) return; // poza Safari nie ma AirPlay ani HLS
    v.src = origin() + PROBE;
  }
  // Dziennik AirPlay z Safari do logu serwera (konsoli Safari nie widać, a zdarzenia WebKit decydują o wszystkim).
  function report(event: string, extra: Record<string, unknown> = {}) {
    const v = video.current;
    void api("/tv/log", {
      event,
      state: stateRef.current,
      wireless: !!v?.webkitCurrentPlaybackTargetIsWireless,
      ready: v?.readyState,
      source: v?.src.includes(PROBE) ? "probe" : v?.src ? "stream" : "none",
      ...extra,
    }).catch(() => {});
  }
  function start(url: string) {
    const v = video.current;
    if (!v) return;
    pending.current = null;
    stateRef.current = "casting";
    setState("casting");
    v.src = url;
    last.current = 0;
    report("start", { url });
    live.current.onStart?.();
    // Bez gestu użytkownika Safari może odmówić startu: wtedy panel pokazuje Play.
    v.play().catch((e: Error) => {
      report("play-rejected", { error: e?.name });
      if (stateRef.current !== "idle") setState("paused");
    });
  }
  function stop(reason = "zakończ") {
    report("stop", { reason, at: last.current });
    const at = last.current;
    last.current = 0;
    stateRef.current = "idle"; // zdarzenie pause z v.pause() nie może już przełączyć panelu na „wstrzymane”
    pending.current = null;
    video.current?.pause();
    probe(); // gotowe na następne kliknięcie
    setState("idle");
    setTime(0);
    setLength(0);
    live.current.onEnd?.(at);
  }
  useEffect(() => {
    void api<{ address: string | null }>("/tv/address")
      .then((r) => {
        address.current = r.address;
        probe();
      })
      .catch(() => probe());
    const v = video.current;
    if (!v) return;
    const availability = (e: Event) =>
      (available.current =
        (e as Event & { availability?: string }).availability === "available");
    let lost: ReturnType<typeof setTimeout> | undefined;
    const route = () => {
      report("route");
      if (v.webkitCurrentPlaybackTargetIsWireless) {
        clearTimeout(lost);
        if (pending.current) start(pending.current);
        return;
      }
      if (stateRef.current === "idle") return;
      // Podmiana adresu tworzy w WebKit nowy odtwarzacz: AirPlay na chwilę „się rozłącza”, po czym sam wraca do
      // telewizora. Kończymy dopiero, gdy połączenie nie wróci (np. ktoś wybrał w oknie AirPlay tego Maca).
      clearTimeout(lost);
      lost = setTimeout(() => {
        if (
          !v.webkitCurrentPlaybackTargetIsWireless &&
          stateRef.current !== "idle"
        )
          stop("rozłączono");
      }, 8000);
    };
    const failed = () => {
      // Błąd albo przerwanie strumienia próbnego (np. przy podmianie adresu) nie ma znaczenia.
      if (stateRef.current === "idle" || !v.error || v.src.includes(PROBE))
        return;
      report("error", { code: v.error.code, message: v.error.message });
      live.current.notify(
        "Telewizor nie pobrał obrazu. Studio musi działać przez npm run dev, Mac i telewizor w tej samej sieci, a zapora macOS musi przepuszczać połączenia przychodzące do node.",
        true,
      );
      stop("błąd");
    };
    const ended = () => {
      // Koniec strumienia próbnego (telewizor potrafi go odegrać przed podmianą) nie kończy sesji.
      if (stateRef.current !== "idle" && v.ended && !v.src.includes(PROBE))
        stop("koniec");
    };
    const playing = () => {
      if (stateRef.current !== "idle") setState("casting");
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
      clearTimeout(lost);
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
      // Tylko panel się odświeża; reszta Studio stoi, póki telewizor gra.
      last.current = v.currentTime;
      setTime(v.currentTime);
      if (Number.isFinite(v.duration)) setLength(v.duration);
    }, 500);
    return () => clearInterval(timer);
  }, [state]);
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
    const url = origin() + "/api" + path();
    setShown(title);
    if (v.webkitCurrentPlaybackTargetIsWireless) {
      // Telewizor już połączony: od razu nowy strumień od bieżącego miejsca, bez okna wyboru.
      start(url);
      return;
    }
    if (v.readyState < HTMLMediaElement.HAVE_METADATA) {
      probe();
      s.notify(
        "AirPlay jeszcze się przygotowuje. Kliknij ponownie za chwilę.",
        true,
      );
      return;
    }
    pending.current = url;
    // Synchronicznie w kliknięciu: Safari pokazuje okno wyboru tylko w geście użytkownika.
    v.webkitShowPlaybackTargetPicker();
    report("picker", { url });
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
        preload="auto"
        playsInline
      />
      {state !== "idle" && (
        <div className="airplay-panel" role="status">
          <Airplay size={16} />
          <div>
            <strong>Na telewizorze</strong>
            <span>
              {shown} · {describe ? describe(time) + " · " : ""}
              {clock(time)}
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
          <IconButton
            icon={Airplay}
            label="Zmień telewizor albo wyłącz AirPlay"
            onClick={() => video.current?.webkitShowPlaybackTargetPicker?.()}
          />
          <Button subtle onClick={() => stop()}>
            Zakończ
          </Button>
        </div>
      )}
    </>
  );
}
