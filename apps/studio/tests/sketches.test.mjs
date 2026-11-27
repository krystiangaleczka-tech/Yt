import test from "node:test";
import assert from "node:assert/strict";
import {
  approvalState, content, flipTimes, indexAt, newVariantId, nextShotId, shotsFromScenario, sketchesFrom, starts,
} from "../src/sketchTypes.ts";

const shot = (nr, extra = {}) => ({ id: `szkic_a-${nr}`, nr, key: "", kadr: "", seconds: 5, description: `Opis ${nr}`,
  line: "", mark: "", assetId: "", ...extra });

test("brak szkiców = trzy puste warianty o stałych id", () => {
  const sk = sketchesFrom({ legacy: {} });
  assert.deepEqual(sk.variants.map((v) => v.id), ["szkic_a", "szkic_b", "szkic_c"]);
  assert.equal(sk.playSeconds, 25);
  assert.equal(sk.approved, null);
  assert.equal(approvalState(sk), "none");
  assert.equal(newVariantId(sk), "szkic_d");
});

test("stan zatwierdzenia porównuje treść z migawką (jak serwer)", () => {
  const variant = { id: "szkic_a", title: "Hak", scenario: "S", shots: [shot(1), shot(2)], source: {} };
  // Migawka po JSON z Pythona: 5.0 wraca jako 5, klucze w innej kolejności.
  const snapshot = JSON.parse(JSON.stringify({ shots: content(variant).shots, scenario: "S", title: "Hak" }));
  const project = { legacy: { production_flow: { sketches: { variants: [variant], approved: { variantId: "szkic_a", snapshot } } } } };
  assert.equal(approvalState(sketchesFrom(project)), "current");
  variant.shots[1].seconds = 9;
  assert.equal(approvalState(sketchesFrom(project)), "stale");
  project.legacy.production_flow.sketches.variants = [{ ...variant, id: "szkic_b" }];
  assert.equal(approvalState(sketchesFrom(project)), "missing");
});

test("kartkowanie: suma = czas przeglądu, proporcje i minimum", () => {
  const lengths = [10, 10, 1, 0.5, 30];
  const times = flipTimes(lengths, 5, 0.3);
  assert.ok(Math.abs(times.reduce((a, b) => a + b, 0) - 5) < 1e-9);
  assert.ok(times.every((t) => t >= 0.3 - 1e-9));
  assert.ok(Math.abs(times[0] - times[1]) < 1e-9);
  assert.ok(Math.abs(times[4] / times[0] - 3) < 1e-9, "dłuższe ujęcie = dłuższa kartka");
  const film = Array.from({ length: 74 }, (_, i) => 4 + (i % 7));
  const total = flipTimes(film, 25).reduce((a, b) => a + b, 0);
  assert.ok(Math.abs(total - 25) < 1e-9);
  assert.ok(flipTimes([1, 2, 3], 0.3, 0.15).every((t) => Math.abs(t - 0.1) < 1e-9), "za krótki przegląd: równe kartki");
  assert.deepEqual(flipTimes([], 25), []);
});

test("szukanie kartki po czasie", () => {
  const s = starts([1, 2, 3]);
  assert.deepEqual(s, [0, 1, 3]);
  assert.equal(indexAt(s, 0), 0);
  assert.equal(indexAt(s, 0.99), 0);
  assert.equal(indexAt(s, 1), 1);
  assert.equal(indexAt(s, 5.5), 2);
});

test("scenariusz → ujęcia: akapity, znaczniki, kwestie i długość", () => {
  const scenario = [
    "HOOK 1",
    "Koronacja 2019. Cesarz dostaje miecz. „In 2019, Japan's new emperor received a sword that no one alive has ever seen.”",
    "Głowy Orochi w dymie.",
    "## Pogorszenie:",
    "Statki płoną na brzegu, \"the crow is gone\".",
  ].join("\n\n");
  const shots = shotsFromScenario(scenario, "szkic_b");
  assert.equal(shots.length, 3);
  assert.equal(shots[0].mark, "HOOK 1");
  assert.equal(shots[0].id, "szkic_b-001");
  assert.match(shots[0].line, /^In 2019, Japan's new emperor/);
  assert.equal(shots[0].description, "Koronacja 2019. Cesarz dostaje miecz.");
  assert.equal(shots[0].seconds, 7, "15 słów kwestii ≈ 7 s");
  assert.equal(shots[1].mark, "");
  assert.equal(shots[1].seconds, 3);
  assert.equal(shots[2].mark, "Pogorszenie");
  assert.equal(shots[2].line, "the crow is gone");
  assert.equal(shots[2].description, "Statki płoną na brzegu.");
  assert.equal(nextShotId({ id: "szkic_b", shots }), "szkic_b-004");
});
