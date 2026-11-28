// Podpisy planów reżyserskich i (z ZATWIERDZ=master,acts,...) odnowione zatwierdzenia etapów — tym samym kodem co Studio.
// uruchom: node --experimental-strip-types podpisy.mjs <flowTypes.ts> < flow.json > flow-podpisany.json
import { pathToFileURL } from "node:url";

const { sceneSourceSignature, stageSignature } = await import(pathToFileURL(process.argv[2]).href);
let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const flow = JSON.parse(raw);
for (const [id, plan] of Object.entries(flow.director.plans)) plan.sourceSignature = sceneSourceSignature(flow, id);
flow.approved = flow.approved || {};
for (const stage of (process.env.ZATWIERDZ || "").split(",").filter(Boolean)) flow.approved[stage] = stageSignature(flow, stage);
process.stdout.write(JSON.stringify(flow));
