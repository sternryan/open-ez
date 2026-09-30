// guide/viewer/tests/section.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { layersAt, summarize, fmtBl } from "../src/logic/section";

const N = {
  "canard.skin_top.p2": { component: "canard.skin_top", cloth: "BID", op_index: 4, order: 2, bl_max: null },
  "canard.skin_top.p1": { component: "canard.skin_top", cloth: "BID", op_index: 4, order: 1, bl_max: null },
  "canard.shear_web.p2": { component: "canard.shear_web", cloth: "UND", op_index: 0, order: 2, bl_max: 30 },
  "canard.shear_web.p1": { component: "canard.shear_web", cloth: "UND", op_index: 0, order: 1, bl_max: 54 },
  "canard.shear_web.p3": { component: "canard.shear_web", cloth: "BID", op_index: 0, order: 3, bl_max: 10 },
};
const at = bl => layersAt(N, bl).map(l => l.node);

test("a ply with bl_max 30 is present at 5 and 25 and absent at 60", () => {
  assert.ok(at(5).includes("canard.shear_web.p2") && at(25).includes("canard.shear_web.p2"));
  assert.ok(!at(60).includes("canard.shear_web.p2"));
});

test("bl_max is inclusive, like guide.layup.counts_at", () => {
  assert.ok(at(30).includes("canard.shear_web.p2") && !at(30.1).includes("canard.shear_web.p2"));
});

test("null bl_max (full span) is present everywhere", () => {
  for (const bl of [0, 25, 60, 999]) assert.ok(at(bl).includes("canard.skin_top.p1"), bl);
  assert.deepEqual(at(60), ["canard.skin_top.p1", "canard.skin_top.p2"]);
});

test("sorted by op_index then order", () => {
  assert.deepEqual(at(5), ["canard.shear_web.p1", "canard.shear_web.p2", "canard.shear_web.p3", "canard.skin_top.p1", "canard.skin_top.p2"]);
});

test("rows carry node, component, cloth, order", () => {
  assert.deepEqual(layersAt(N, 60)[0], { node: "canard.skin_top.p1", component: "canard.skin_top", cloth: "BID", order: 1 });
});

test("summarize groups by component in build order, in the owner's labels", () => {
  const G = { components: { "canard.shear_web": { label: "Shear web" }, "canard.skin_top": { label: "Top skin" } } };
  assert.equal(summarize(G, layersAt(N, 5)), "Shear web: 2 UND, 1 BID · Top skin: 2 BID");
  assert.equal(summarize(G, layersAt(N, 60)), "Top skin: 2 BID");
  assert.equal(summarize(G, []), "No layers cut here");
});

test("fmtBl shows at most one decimal", () => {
  assert.equal(fmtBl(40), "B.L. 40"); assert.equal(fmtBl(12.5), "B.L. 12.5"); assert.equal(fmtBl(12.34), "B.L. 12.3");
});
