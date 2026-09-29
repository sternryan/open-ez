// guide/viewer/tests/cutaway.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { GLANCE, cutawayFor, hasGlance, readView, writeView, paneMode, plyRows, isolateLabel } from "../js/cutaway.js";

const G = {
  components: { "canard.shear_web": { label: "Shear web" } },
  plies: { "canard.shear_web": [{ node: "canard.shear_web.p1", order: 1 }, { node: "canard.shear_web.p3", order: 3 }] },
  cutaway: { ops: { "r30.bottom-skin": { src: "renders/op-r30-bottom-skin.png", alt: "After" } }, heroes: [{ bl: 5 }] },
};
const mem = () => { const m = new Map(); return { getItem: k => m.get(k) ?? null, setItem: (k, v) => m.set(k, v) }; };
const throwing = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } };

test("cutawayFor and hasGlance", () => {
  assert.equal(cutawayFor(G, "r30.bottom-skin").src, "renders/op-r30-bottom-skin.png");
  assert.equal(cutawayFor(G, "r30.jig-assemble"), null);
  assert.equal(cutawayFor({}, "x"), null);
  assert.equal(hasGlance(G), true); assert.equal(hasGlance({ cutaway: null }), false);
});

test("view memory survives blocked storage", () => {
  const s = mem(); assert.equal(readView(s), "3d");
  writeView(s, "cutaway"); assert.equal(readView(s), "cutaway");
  assert.equal(readView(throwing), "3d"); writeView(throwing, "cutaway");
});

test("paneMode: hidden toggle falls back to 3D; glance wins", () => {
  assert.equal(paneMode(G, "r30.bottom-skin", "cutaway"), "cutaway");
  assert.equal(paneMode(G, "r30.jig-assemble", "cutaway"), "3d");
  assert.equal(paneMode(G, "r30.bottom-skin", "3d"), "3d");
  assert.equal(paneMode(G, GLANCE, "3d"), "glance");
});

test("ply rows and isolate label", () => {
  assert.equal(plyRows(G, "canard.shear_web").length, 2);
  assert.deepEqual(plyRows(G, "canard.core"), []);
  assert.equal(isolateLabel(G, "canard.shear_web", "canard.shear_web.p3"), "Showing Shear web ply 3");
});
