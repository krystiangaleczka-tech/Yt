import test from "node:test";
import assert from "node:assert/strict";
import { chosen, flowFrom, isApproved, isReady, newVariant, stageSignature } from "../src/flowTypes.ts";

const project = {
  production_mode: "animation_2d",
  legacy: {},
};
test("legacy film loads a safe, unsaved initial flow", () => {
  const flow = flowFrom(project);
  assert.equal(flow.factual, false);
  assert.equal(flow.acts.length, 3);
  assert.equal(flow.bible.chronology, "");
  assert.equal(isReady(flow, "master"), false);
});
test("approvals follow the selected story and go stale when upstream changes", () => {
  const flow = flowFrom(project);
  const main = newVariant("Zombie", "Zombie wchodzi do szpitala i goni lekarza.");
  flow.master.variants.push(main);
  flow.master.selected = main.id;
  assert.equal(isReady(flow, "master"), true);
  flow.approved.master = stageSignature(flow, "master");
  for (const act of flow.acts) chosen(act).description = "Cel, konflikt, rezultat.";
  assert.equal(isReady(flow, "acts"), true);
  flow.approved.acts = stageSignature(flow, "acts");
  const sequence = { id: "seq-1", actId: flow.acts[0].id, seconds: 180,
    variants: [newVariant("Korytarz", "Bohater wbiega na oddział")], selected: null };
  sequence.selected = sequence.variants[0].id;
  flow.sequences.push(sequence);
  const sig = stageSignature(flow, "acts");
  assert.equal(sig, flow.approved.acts);
  flow.master.variants[0].description = "Inne zakończenie.";
  assert.equal(isApproved(flow, "master"), false);
  assert.equal(isApproved(flow, "acts"), false);
  assert.equal(isReady(flow, "sequences"), false);
});
test("selected alternatives survive round trip through project legacy", () => {
  const flow = flowFrom(project);
  const v = newVariant("Alternatywa", "Początek, środek i finał.");
  flow.master.variants = [v]; flow.master.selected = v.id;
  const reopened = flowFrom({ ...project, legacy: { production_flow: flow } });
  assert.equal(chosen(reopened.master).id, v.id);
  assert.equal(reopened.acts.length, 3);
});
