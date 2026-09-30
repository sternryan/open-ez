// guide/viewer/tests/tour.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { tourSteps, tourStart, stepTour } from "../js/tour.js";

const op = (id, chapter, variants, stub = false) => ({ id, chapter, variants, stub, components: [] });
const G = {
  // graph order deliberately differs from array order of `ops`: the tour must follow `order`
  order: ["c03.skills", "r30.cores", "r30.web", "c10.cores", "r30.skin", "r30.elev", "r30.pins"],
  ops: [
    op("r30.pins", 30, ["roncz"]), op("r30.elev", 30, ["roncz"], true), op("r30.skin", 30, ["roncz"]),
    op("c10.cores", 10, ["gu"]), op("r30.web", 30, ["roncz"]), op("r30.cores", 30, ["roncz"]),
    op("c03.skills", 3, ["both"], true),
  ],
  tours: { "r30.web": { target: [1, 2, 3], position: [4, 5, 6] } },
};

test("tourSteps: every visible non-stub op of the chapter, in graph order (Review Focus 5)", () => {
  assert.deepEqual(tourSteps(G, "roncz", 30).map(s => s.op), ["r30.cores", "r30.web", "r30.skin", "r30.pins"]);
});

test("tourSteps skips stubs and other chapters and other variants", () => {
  const ids = tourSteps(G, "roncz", 30).map(s => s.op);
  assert.ok(!ids.includes("r30.elev") && !ids.includes("c10.cores") && !ids.includes("c03.skills"));
  assert.deepEqual(tourSteps(G, "gu", 30), []);
  assert.deepEqual(tourSteps(G, "gu", 10).map(s => s.op), ["c10.cores"]);
});

test("tourSteps: authored shot, else null (the home view); works without a tours map", () => {
  const s = tourSteps(G, "roncz", 30);
  assert.deepEqual(s.find(x => x.op === "r30.web").shot, { target: [1, 2, 3], position: [4, 5, 6] });
  assert.equal(s.find(x => x.op === "r30.cores").shot, null);
  const { tours, ...bare } = G;
  assert.ok(tourSteps(bare, "roncz", 30).every(x => x.shot === null));
});

const run = (dts, n = 4, dwell = 1) => {
  let s = tourStart(n, dwell); const seen = [];
  for (const dt of dts) { s = stepTour(s, dt); seen.push(s.i); }
  return { s, seen };
};

test("stepTour: same dt sequence lands on the same step every run", () => {
  const dts = [0.25, 0.5, 0.125, 0.5, 0.75, 0.25, 0.5];
  assert.deepEqual(run(dts), run(dts));
});

test("stepTour advances exactly at dwell boundaries", () => {
  assert.deepEqual(run([0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5]).seen, [0, 0, 1, 1, 2, 2, 3]);
  const s = stepTour(stepTour(tourStart(3, 2), 1.5), 0.5);
  assert.equal(s.i, 1); assert.equal(s.t, 0);
});

test("stepTour: a long dt skips whole steps, keeping the remainder", () => {
  const s = stepTour(tourStart(5, 1), 2.25);
  assert.equal(s.i, 2); assert.equal(s.t, 0.25);
});

test("stepTour reports done once past the last step, and stays done", () => {
  const { s, seen } = run([1, 1, 1, 1]);
  assert.equal(s.done, true); assert.equal(seen[2], 3); assert.equal(s.i, 4);
  assert.equal(run([1, 1, 1, 0.5]).s.done, false);
  assert.deepEqual(stepTour(s, 5), s);
});

test("stepTour is pure", () => {
  const s0 = tourStart(3, 1), frozen = JSON.stringify(s0);
  stepTour(s0, 1); assert.equal(JSON.stringify(s0), frozen);
});

// 0.3 + 0.3 + 0.3 === 0.8999999999999999 < 0.9: without EPS the step boundary is missed by one ulp.
const ulp = () => stepTour(stepTour(stepTour(tourStart(3, 0.9), 0.3), 0.3), 0.3);

test("stepTour: float dt sums land on the boundary (EPS matters)", () => {
  assert.ok(0.3 + 0.3 + 0.3 < 0.9);
  assert.equal(ulp().i, 1);
});

test("tourStart with no steps is already done, and stepping it is a harmless no-op", () => {
  const s = tourStart(0, 1);
  assert.equal(s.done, true);
  assert.doesNotThrow(() => stepTour(s, 1));
  assert.deepEqual(stepTour(s, 1), s);
});

test("stepTour never leaves a negative remainder after a boundary hit", () => {
  const s = ulp();
  assert.ok(s.t >= 0, `t=${s.t}`);
});
