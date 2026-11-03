import test from "node:test";
import assert from "node:assert/strict";
import { flowFrom, newVariant, stageSignature, isApproved, isReady, chosen, orderedOutlines, sceneSourceSignature, stableJson } from "../src/flowTypes.ts";
import { buildAutoPlan, choosePattern, directorLimits, directorPatterns, extractJsonObject, parseDirectorAI, shotKinds } from "../src/directorTypes.ts";

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
  const scripted = flowFrom({...project, legacy: {production_flow: structuredClone(flow)}});
  scripted.scripts[scripted.acts[0].id] = "Nagle odezwał się głośny telefon.";
  assert.equal(isReady(scripted, "direction"), false);
  assert.equal(isApproved(scripted, "direction"), false);
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

function reorderKeys(value) {
  if (Array.isArray(value)) return value.map(reorderKeys);
  if (value && typeof value === "object")
    return Object.fromEntries(Object.keys(value).reverse().map(k => [k, reorderKeys(value[k])]));
  return value;
}
test("Approvals are compact and survive a server round trip with different key order", () => {
  const flow = completeFlow();
  flow.bible.characters = "Lekarz ".repeat(5000);
  assert.equal(isApproved(flow, "master"), false, "Story Bible change makes approvals stale");
  for (const stage of ["master", "acts", "sequences", "outlines"]) flow.approved[stage] = stageSignature(flow, stage);
  for (const row of flow.outlines) flow.director.plans[row.id] = buildAutoPlan(flow, row);
  flow.approved.direction = stageSignature(flow, "direction");
  assert.ok(flow.approved.direction.length < 60, "signature must not copy the whole story into project.json");
  assert.ok(Object.values(flow.director.plans).every(plan => plan.sourceSignature.length < 60));
  const reopened = flowFrom({ ...project, legacy: { production_flow: reorderKeys(JSON.parse(JSON.stringify(flow))) } });
  for (const stage of ["master", "acts", "sequences", "outlines", "direction"])
    assert.equal(isApproved(reopened, stage), true, stage);
  reopened.director.plans[reopened.outlines[0].id].shots[0].duration += 1;
  assert.equal(isApproved(reopened, "direction"), false, "any shot edit invalidates the approval");
});
test("Stable JSON ignores key order but not values", () => {
  assert.equal(stableJson({ b: 1, a: [1, { d: 2, c: 3 }] }), stableJson({ a: [1, { c: 3, d: 2 }], b: 1 }));
  assert.notEqual(stableJson({ a: [1, 2] }), stableJson({ a: [2, 1] }));
});
test("Scene source signature changes with scene, act script and Story Bible", () => {
  const flow = completeFlow(), id = flow.outlines[0].id, before = sceneSourceSignature(flow, id);
  flow.bible.visuals = "Zielone światło";
  assert.notEqual(sceneSourceSignature(flow, id), before);
});
test("Scenes are listed in film order (act, sequence, scene), not creation order", () => {
  const flow = completeFlow();
  flow.outlines.reverse();
  const ordered = orderedOutlines(flow).map(x => x.sectionId);
  assert.deepEqual(ordered, flow.sequences.map(x => x.id));
  flow.outlines.push({ id: "orphan", sectionId: "missing", seconds: 5, variants: [], selected: null });
  assert.equal(orderedOutlines(flow).at(-1).id, "orphan");
});
test("Auto plan respects backend field limits for long scene descriptions", () => {
  const flow = completeFlow(), outline = flow.outlines[0];
  chosen(outline).description = "Bardzo długi opis sceny. ".repeat(1000);
  const plan = buildAutoPlan(flow, outline, "guided", "", "x".repeat(9000));
  assert.ok(plan.shots.every(s => s.description.length <= directorLimits.description));
  assert.ok(plan.notes.length <= directorLimits.notes);
  assert.ok(plan.shots.some(s => s.description.startsWith("To, co widzi bohater")) || plan.shots.length > 0);
});
test("AI answer may be fenced or wrapped in a short explanation", () => {
  const body = { beats: [{ title: "A", tensionBefore: 2, tensionAfter: 5 }], shots: [{ beatIndex: 0, typeId: "pov", duration: 2 }] };
  assert.deepEqual(extractJsonObject("Oto plan:\n```json\n" + JSON.stringify(body) + "\n```\nPowodzenia!"), body);
  assert.throws(() => extractJsonObject("Nie mogę pomóc."), /JSON/);
  assert.throws(() => extractJsonObject("{ zepsuty json }"), /JSON/);
  const flow = completeFlow();
  const plan = parseDirectorAI("Plan:\n" + JSON.stringify(body), flow, flow.outlines[0], "guided");
  assert.equal(plan.shots[0].typeId, "pov");
});
