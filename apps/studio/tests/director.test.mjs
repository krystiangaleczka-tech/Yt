import test from "node:test";
import assert from "node:assert/strict";
import { flowFrom, newVariant, stageSignature, isApproved, isReady, chosen } from "../src/flowTypes.ts";
import { buildAutoPlan, choosePattern, directorPatterns, parseDirectorAI, shotKinds } from "../src/directorTypes.ts";

const project = { production_mode: "animation_2d", development: { selected_idea_id: "" }, legacy: {} };
function completeFlow() {
  const flow = flowFrom(project);
  const v = newVariant("Szpital", "Sanitariusz próbuje przeżyć noc.");
  flow.master.variants.push(v);
  flow.master.selected = v.id;
  flow.approved.master = stageSignature(flow, "master");
  for (const act of flow.acts) chosen(act).description = "Cel, przeszkoda i zwrot.";
  flow.approved.acts = stageSignature(flow, "acts");
  for (const act of flow.acts) {
    const variant = newVariant("Przebieg", "Ruch fabuły.");
    flow.sequences.push({ id: act.id + "-s", actId: act.id, seconds: 120, variants: [variant], selected: variant.id });
  }
  flow.approved.sequences = stageSignature(flow, "sequences");
  for (const section of flow.sequences) {
    const variant = newVariant("Telefon w celi", "Telefon dzwoni. Zombie odwracają głowy za okienkiem.");
    flow.outlines.push({ id: section.id + "-o", sectionId: section.id, seconds: 12, variants: [variant], selected: variant.id });
  }
  flow.approved.outlines = stageSignature(flow, "outlines");
  return flow;
}
test("Director library includes rapid intercut and POV, reaction, insert vocabulary", () => {
  assert.ok(directorPatterns.find(x => x.id === "rapid-intercut"));
  for (const id of ["pov", "insert", "reaction", "reverse", "static-hold"])
    assert.ok(shotKinds.some(s => s.id === id));
});
test("Auto plan for phone vs zombie is a timed, editable beat/shot sequence", () => {
  const flow = completeFlow(), outline = flow.outlines[0];
  assert.equal(choosePattern(chosen(outline).description).id, "rapid-intercut");
  const plan = buildAutoPlan(flow, outline);
  assert.equal(plan.patternId, "rapid-intercut");
  assert.ok(plan.beats.length >= 3);
  assert.ok(plan.shots.length >= 6);
  assert.ok(plan.shots.every(s => plan.beats.some(b => b.id === s.beatId)));
  assert.ok(Math.abs(plan.shots.reduce((n,s) => n + s.duration,0) - outline.seconds) <= 0.11);
});
test("Reapproval depends on original story and each planned scene", () => {
  const flow = completeFlow();
  assert.equal(isReady(flow, "direction"), false);
  for (const row of flow.outlines) flow.director.plans[row.id] = buildAutoPlan(flow, row);
  assert.equal(isReady(flow, "direction"), true);
  flow.approved.direction = stageSignature(flow, "direction");
  assert.equal(isApproved(flow, "direction"), true);
  const reopened = flowFrom({...project, legacy: {production_flow: structuredClone(flow)}});
  assert.equal(isApproved(reopened, "direction"), true);
  reopened.outlines[0].variants[0].description = "Inna scena, inne zagrożenie.";
  assert.equal(isReady(reopened, "direction"), false);
  assert.equal(isApproved(reopened, "direction"), false);
});
test("AI response is validated and binds beats to approved source scene", () => {
  const flow = completeFlow(), outline = flow.outlines[0];
  const valid = {
    patternId:"rapid-intercut", beats:[{title:"Dzwonek",goal:"Ujawnienie",tensionBefore:4,tensionAfter:7}],
    shots:[{beatIndex:0,typeId:"insert",title:"Telefon",description:"Telefon wibruje",duration:1.2}],
  };
  const plan = parseDirectorAI(JSON.stringify(valid),flow,outline,"guided");
  assert.equal(plan.shots[0].beatId,plan.beats[0].id);
  assert.equal(plan.sourceSignature,buildAutoPlan(flow,outline).sourceSignature);
  assert.throws(() => parseDirectorAI(JSON.stringify({...valid,shots:[{...valid.shots[0],typeId:"fake"}]}),flow,outline,"auto"),/Nieznany typ/);
  assert.throws(() => parseDirectorAI(JSON.stringify({...valid,shots:[{...valid.shots[0],duration:-2}]}),flow,outline,"auto"),/czas ujęcia/);
});
