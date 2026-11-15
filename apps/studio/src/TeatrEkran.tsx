import { useEffect, useRef, useState } from "react";
import type { Project } from "./types";
import { naZywoWlaczone, teatrProjektu, ustawNaZywo, type Teatr } from "./teatr";

/** Teatr projektu i przełącznik „na żywo”; komponent odświeża się, kiedy zmieni się kod albo dojdą dane ujęć. */
export function useTeatr(project: Project) {
  const teatr = teatrProjektu(project);
  const [, setWersja] = useState(0);
  useEffect(() => (teatr ? teatr.subskrybuj(() => setWersja((v) => v + 1)) : undefined), [teatr]);
  return { teatr, naZywo: !!teatr && naZywoWlaczone() };
}

/**
 * Ujęcie rysowane na żywo (zakładka Ujęcia): klatki z kodu zamiast klipu mp4. Gra, kiedy `playing`; na końcu ujęcia
 * woła `onEnd`. Suwak przewija, przycisk w rogu wraca do klipów mp4.
 */
export default function TeatrEkran({
  teatr,
  odn,
  seconds,
  playing,
  onEnd,
}: {
  teatr: Teatr;
  odn: string;
  seconds: number;
  playing: boolean;
  onEnd: () => void;
}) {
  const canvas = useRef<HTMLCanvasElement>(null),
    suwak = useRef<HTMLInputElement>(null),
    czas = useRef<HTMLSpanElement>(null),
    t = useRef(0),
    live = useRef({ playing, onEnd, seconds });
  live.current = { playing, onEnd, seconds };
  const [gotowy, setGotowy] = useState(teatr.gotowy(odn));
  useEffect(() => {
    t.current = 0;
    setGotowy(teatr.gotowy(odn));
    void teatr.przygotuj(odn).then(() => setGotowy(teatr.gotowy(odn)));
  }, [teatr, odn]);
  useEffect(() => teatr.subskrybuj(() => setGotowy(teatr.gotowy(odn))), [teatr, odn]);
  useEffect(() => {
    if (playing && t.current >= seconds - 0.02) t.current = 0; // Play na końcu ujęcia: od początku
  }, [playing, seconds]);
  useEffect(() => {
    let raf = 0,
      prev = performance.now(),
      drawn = "";
    const tick = (now: number) => {
      const { playing: gra, seconds: dl } = live.current;
      if (gra) {
        t.current = Math.min(dl, t.current + (now - prev) / 1000);
        if (t.current >= dl) {
          live.current.onEnd();
        }
      }
      prev = now;
      const klatka = teatr.klatka(odn, t.current);
      const klucz = `${t.current.toFixed(3)}:${klatka ? 1 : 0}`;
      if (klatka && klucz !== drawn) {
        canvas.current?.getContext("2d")?.drawImage(klatka, 0, 0);
        drawn = klucz;
      }
      if (suwak.current && document.activeElement !== suwak.current) suwak.current.value = String(t.current);
      if (czas.current) czas.current.textContent = `${t.current.toFixed(2)} / ${dl.toFixed(2)} s`;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [teatr, odn]);
  const blad = teatr.stan.stan === "błąd" ? teatr.stan.blad : "";
  return (
    <div className="teatr-ekran">
      <canvas ref={canvas} width={1280} height={720} aria-label="Ujęcie rysowane na żywo z kodu" />
      {!gotowy && <div className="teatr-czeka">Liczę ruch ujęcia…</div>}
      {blad && (
        <pre className="teatr-blad" onClick={(e) => e.stopPropagation()}>
          Błąd w kodzie — widać ostatnią dobrą wersję.{"\n\n"}
          {blad}
        </pre>
      )}
      <span className="teatr-znak" title="Klatki rysuje karta graficzna z kodu ujęcia; po zapisaniu kodu obraz odświeża się sam.">
        NA ŻYWO{teatr.stan.kod ? ` · kod v${teatr.stan.kod}` : ""}
      </span>
      <div className="teatr-pasek" onClick={(e) => e.stopPropagation()}>
        <input
          ref={suwak}
          type="range"
          min={0}
          max={seconds}
          step={1 / 24}
          defaultValue={0}
          aria-label="Przewiń ujęcie"
          onInput={(e) => {
            t.current = Number((e.target as HTMLInputElement).value);
          }}
        />
        <span ref={czas} className="teatr-czas" />
        <button type="button" onClick={() => ustawNaZywo(false)} title="Pokaż wyrenderowany klip mp4 zamiast rysowania na żywo">
          klip mp4
        </button>
      </div>
    </div>
  );
}

/** Mały przycisk powrotu do rysowania na żywo (widać go, kiedy teatr jest wyłączony). */
export function NaZywoPrzycisk() {
  return (
    <button
      type="button"
      className="teatr-wroc"
      onClick={(e) => {
        e.stopPropagation();
        ustawNaZywo(true);
      }}
      title="Rysuj ujęcia na żywo z kodu zamiast klipów mp4"
    >
      na żywo
    </button>
  );
}
