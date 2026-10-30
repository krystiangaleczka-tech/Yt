import { useEffect, useState } from "react";
import { api, mediaUrl } from "./api";
import { Button, Field } from "./components";
import { useStudio } from "./context";
import type { Project, Scene } from "./types";

type Assessment = { summary: string; verdict: string; issues: {
  severity: string; problem: string; correction: string; object_ids: string[];
}[] };
type Review = { approved: boolean; stale?: boolean; signature: string; notes?: string;
  preview?: { url: string; reference_asset_id: string; image_sha256: string; seconds: number };
  assessment?: Assessment };

export default function PaperTheatreReview({ scene, dirty, onCompare }: {
  scene?: Scene; dirty: boolean; onCompare: () => void;
}) {
  const studio = useStudio();
  const project = studio.project!;
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState("");
  const [mode, setMode] = useState("side");
  const [opacity, setOpacity] = useState(50);
  const [loaded, setLoaded] = useState(false);
  const [checks, setChecks] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  useEffect(() => {
    let active = true;
    setLoaded(false); setChecks([]); setError("");
    if (!scene) { setReview(null); return; }
    api<Review>(`/projects/${project.id}/paper-theatre/${scene.id}/review`)
      .then(value => { if (active) { setReview(value); setNotes(value.notes || ""); } })
      .catch(e => { if (active) setError(String(e.message || e)); });
    return () => { active = false; };
  }, [project.id, project.revision, scene?.id]);
  const base = `/projects/${project.id}/paper-theatre/${scene?.id}/review`;
  const vision = () => studio.run(async () => {
    await studio.mutate(p => api<Project>(base + "/vision", { expected_revision: p.revision }));
    studio.notify("Scenograf przygotował uwagi. Decyzja o akceptacji należy do autora.");
  });
  const decide = (decision: string) => studio.run(async () => {
    await studio.mutate(p => api<Project>(base + "/decision", {
      expected_revision: p.revision, signature: review?.signature,
      image_sha256: review?.preview?.image_sha256, checks, decision, notes,
    }));
    studio.notify(decision === "approve" ? "Autor zatwierdził ten układ. Możesz przejść do montażu." : "Zapisano uwagi. Układ czeka na poprawki.");
  });
  const toTimeline = () => studio.run(async () => {
    if (!scene) return;
    await studio.mutate(p => api<Project>(`/projects/${p.id}/scenes/${scene.id}/to-timeline`, { expected_revision: p.revision }));
    studio.setTargetScene(scene.id);
    studio.setPage("editing");
  });
  const preview = dirty ? undefined : review?.preview;
  const approved = !dirty && review?.approved;
  const checklist = [
    ["proportions", "Skala postaci, wagi, blatu i szaty bohatera"],
    ["placement", "Położenie, perspektywa i przesłanianie względem referencji"],
    ["contacts", "Styki: ręka i pióro przy księdze, rekwizyty na blacie, postacie przy stole"],
  ];
  return <section className="surface paper-review" aria-label="Scenograf — porównanie z referencją">
    <h2>04 · Scenograf — porównaj układ przed animacją</h2>
    <p>To klatka z tego samego kompozytora co film: z przycięciem alfa, właściwą skalą i kolejnością warstw.</p>
    <p className="small muted">Akceptacja referencji określa wzór. Dopiero tutaj zatwierdzasz scenę z osobnych PNG. Zgodność oceniaj wizualnie; nie podajemy niezmierzonego procentu podobieństwa.</p>
    <div className="button-row">
      <Button primary onClick={onCompare} disabled={!scene}>Zapisz układ i przygotuj porównanie</Button>
      <strong role="status">{dirty ? "Niezapisane zmiany — przygotuj nową klatkę" : approved ? "Układ zaakceptowany przez autora" : review?.stale ? "Układ zmieniony — poprzednia akceptacja jest nieaktualna" : "Układ czeka na ocenę autora"}</strong>
    </div>
    {error && <p role="alert">{error}</p>}
    {preview && <>
      <div className="button-row">
        <Button onClick={() => setMode("side")} primary={mode === "side"}>Obok siebie</Button>
        <Button onClick={() => setMode("overlay")} primary={mode === "overlay"} disabled={!preview.reference_asset_id}>Nakładka referencji</Button>
      </div>
      <div className={mode === "side" ? "paper-review-pair" : "paper-review-overlay"}>
        {mode === "side" && preview.reference_asset_id && <figure><figcaption>Referencja</figcaption>
          <img src={mediaUrl(project.id, preview.reference_asset_id)} alt="Referencja do oceny proporcji i położenia" /></figure>}
        <figure><figcaption>Rzeczywista scena · {preview.seconds.toFixed(2)} s</figcaption>
          <div className="paper-review-frame" style={{ aspectRatio: `${project.sequence.width}/${project.sequence.height}` }}>
            <img src={preview.url} alt="Rzeczywista kompozycja z osobnych PNG" onLoad={() => setLoaded(true)} onError={() => setLoaded(false)} />
            {mode === "overlay" && preview.reference_asset_id && <img className="paper-review-reference"
              src={mediaUrl(project.id, preview.reference_asset_id)} alt="Nakładka obrazu referencyjnego" style={{ opacity: opacity / 100 }} />}
          </div></figure>
      </div>
      {mode === "overlay" && <Field label={`Widoczność referencji: ${opacity}%`}>
        <input type="range" min={0} max={100} value={opacity} onChange={e => setOpacity(Number(e.target.value))} />
      </Field>}
      <Button onClick={vision} disabled={!preview.reference_asset_id || !loaded}>Scenograf AI: porównaj oba obrazy</Button>
      <p className="small muted">Po kliknięciu oba obrazy trafiają do połączonego modelu z obsługą obrazów. Recenzja opisuje rozbieżności i korekty; nie jest akceptacją autora.</p>
      {review?.assessment && <div className="paper-review-issues">
        <h3>Uwagi scenografa</h3><p>{review.assessment.summary}</p>
        {review.assessment.issues.map((issue, index) => <article key={index}>
          <strong>{issue.severity === "critical" ? "Do poprawy" : "Do sprawdzenia"}: {issue.problem}</strong>
          <p>{issue.correction}</p>
        </article>)}
      </div>}
      <h3>05 · Decyzja autora o scenografii</h3>
      {checklist.map(([key, label]) => <label className="paper-review-check" key={key}>
        <input type="checkbox" checked={checks.includes(key)} onChange={e => setChecks(old => e.target.checked ? [...old, key] : old.filter(k => k !== key))} />{label}
      </label>)}
      <Field label="Uwagi do poprawy lub świadomie zaakceptowane odstępstwa">
        <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3} maxLength={5000} />
      </Field>
      <div className="button-row">
        <Button onClick={() => decide("revise")}>Odeślij do poprawy</Button>
        <Button primary onClick={() => decide("approve")} disabled={!loaded || checks.length !== 3}>Akceptuję ten układ sceny</Button>
        <Button onClick={toTimeline} disabled={!approved}>Przejdź z zaakceptowaną sceną do montażu</Button>
      </div>
    </>}
    <h3>06 · Ruch, dialogi i dodatkowe elementy w Montażu</h3>
    <p className="small muted">Paper Theatre służy do scenografii i wejść wycinków. W Montażu dodasz głos, dymki lub plansze, nakładki, dźwięk i ruch klipów. Przed MP4 sprawdź całe ujęcie wraz z tymi elementami. Każda zmiana scenografii wymaga ponownego porównania i akceptacji.</p>
  </section>;
}
