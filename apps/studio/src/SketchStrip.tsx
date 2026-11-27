import { ArrowRight } from "lucide-react";
import type { Project } from "./types";
import { approvalState, clock, sketchesFrom, totalSeconds } from "./sketchTypes";

/** Pasek „Szkic ujęć” na etapach po szkicach: dalsza produkcja odwołuje się do zatwierdzonego wariantu. */
export default function SketchStrip({ project, onOpen }: { project: Project; onOpen: () => void }) {
  const sk = sketchesFrom(project);
  const state = approvalState(sk);
  const variant = sk.approved ? sk.variants.find((v) => v.id === sk.approved!.variantId) : undefined;
  const title = sk.approved?.title || "";
  return (
    <div className={`flow-bible-strip sk-status ${state}`}>
      <span>Szkic ujęć</span>
      <strong>
        {state === "none" && "niezatwierdzony"}
        {state === "current" && `„${title}” ✓ · ${variant?.shots.length || 0} ujęć · film ${clock(totalSeconds(variant?.shots || []))}`}
        {state === "stale" && `„${title}” — zmieniony po zatwierdzeniu`}
        {state === "missing" && `„${title}” — zatwierdzony wariant usunięty`}
      </strong>
      <button type="button" onClick={onOpen}>Otwórz szkice <ArrowRight size={14} /></button>
    </div>
  );
}
