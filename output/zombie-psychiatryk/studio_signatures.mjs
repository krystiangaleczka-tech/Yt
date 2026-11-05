// Uzupełnia sourceSignature planów reżyserskich tym samym kodem, którego używa DocOS Studio.
// uruchom: node --experimental-strip-types studio_signatures.mjs <flowTypes.ts> < flow.json > flow-signed.json
import { pathToFileURL } from "node:url";

const { sceneSourceSignature } = await import(pathToFileURL(process.argv[2]).href);
let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const flow = JSON.parse(raw);
for (const [id, plan] of Object.entries(flow.director.plans)) plan.sourceSignature = sceneSourceSignature(flow, id);
process.stdout.write(JSON.stringify(flow));
