// guide/viewer/tests/build.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { firstOp, visibleSet, pathVisible } from "../src/logic/build";

const G = {
  order: ["r30.cores", "r30.shear-web", "r30.bottom-skin"],
  ops: [
    { id: "r30.cores", components: ["canard.core"], variants: ["roncz"] },
    { id: "r30.shear-web", components: ["canard.shear_web"], variants: ["roncz"] },
    { id: "r30.bottom-skin", components: ["canard.skin_bottom"], variants: ["roncz"] },
  ],
};
const M = [
  { name: "canard.core", component: "canard.core", ply: null },
  { name: "canard.shear_web.p1", component: "canard.shear_web", ply: { op: "r30.shear-web", order: 1 } },
  { name: "canard.shear_web.p2", component: "canard.shear_web", ply: { op: "r30.shear-web", order: 2 } },
  { name: "canard.skin_bottom.p1", component: "canard.skin_bottom", ply: { op: "r30.bottom-skin", order: 1 } },
];
const st = (op, lay, g = G) => Object.fromEntries(visibleSet(g, "roncz", op, lay, M));

test("firstOp maps components to their first op", () => {
  assert.equal(firstOp(G, "roncz").get("canard.core"), "r30.cores");
});

test("state at the shear web, ply 1 of 2", () => {
  assert.deepEqual(st("r30.shear-web", 1), {
    "canard.core": "built", "canard.shear_web.p1": "current",
    "canard.shear_web.p2": "hidden", "canard.skin_bottom.p1": "hidden" });
});

test("stepping backwards hides later work (Review Focus 1)", () => {
  st("r30.bottom-skin", Infinity);
  assert.equal(st("r30.cores", Infinity)["canard.shear_web.p1"], "hidden");
});

test("ghost mode shows future work as ghost", () => {
  assert.equal(st("r30.cores", Infinity, { ...G, __ghost: true })["canard.skin_bottom.p1"], "ghost");
});

test("an unowned mesh throws (Review Focus 2)", () => {
  assert.throws(() => visibleSet(G, "roncz", "r30.cores", Infinity,
    [...M, { name: "stray", component: "canard.elevator", ply: null }]), /unowned mesh stray/);
});

const GU = {
  order: ["r30.cores", "gu.cores"],
  ops: [
    { id: "r30.cores", components: ["canard.core"], variants: ["roncz"] },
    { id: "gu.cores", components: ["canard.core"], variants: ["gu"] },
    { id: "r30.shear-web", components: ["canard.shear_web"], variants: ["roncz"] },
  ],
};

test("a ply of an op outside the variant is hidden, not re-mapped", () => {
  const m = [{ name: "w.p1", component: "canard.shear_web", ply: { op: "r30.shear-web", order: 1 } }];
  assert.equal(visibleSet({ ...GU, order: ["gu.cores"], __ghost: true }, "gu", "gu.cores", Infinity, m).get("w.p1"), "hidden");
});

test("a ply whose op is not in the graph throws", () => {
  const m = [{ name: "w.p1", component: "canard.core", ply: { op: "nope", order: 1 } }];
  assert.throws(() => visibleSet(G, "roncz", "r30.cores", Infinity, m), /unowned mesh w\.p1/);
});

test("an op outside the variant throws", () => {
  assert.throws(() => visibleSet(GU, "gu", "r30.cores", Infinity, []), /op not in variant: r30\.cores/);
  assert.throws(() => visibleSet(G, "roncz", "nope", Infinity, M), /op not in variant: nope/);
});

test("full maps at the first and a later op", () => {
  assert.deepEqual(st("r30.cores", Infinity), {
    "canard.core": "current", "canard.shear_web.p1": "hidden",
    "canard.shear_web.p2": "hidden", "canard.skin_bottom.p1": "hidden" });
  assert.deepEqual(st("r30.bottom-skin", Infinity), {
    "canard.core": "built", "canard.shear_web.p1": "built",
    "canard.shear_web.p2": "built", "canard.skin_bottom.p1": "current" });
});

test("ghost mode ghosts plies of the current op past layIndex", () => {
  assert.equal(st("r30.shear-web", 1, { ...G, __ghost: true })["canard.shear_web.p2"], "ghost");
});

test("an owned component mesh outside the variant is hidden, not thrown", () => {
  const m = [{ name: "canard.core", component: "canard.core", ply: null }];
  const g = { order: ["r30.shear-web"], ops: [
    { id: "r30.shear-web", components: ["canard.shear_web"], variants: ["roncz"] },
    { id: "gu.cores", components: ["canard.core"], variants: ["gu"] }] };
  assert.equal(visibleSet(g, "roncz", "r30.shear-web", Infinity, m).get("canard.core"), "hidden");
});

test("a component mesh is current at its own op with layIndex 0", () => {
  assert.equal(st("r30.cores", 0)["canard.core"], "current");
});

test("pathVisible: every part built or current draws the path", () => {
  const path = { parts: ["canard.core", "canard.shear_web"] };
  assert.equal(pathVisible(path, st("r30.shear-web", 1)), true);   // core built, web current (ply 1 of 2)
  assert.equal(pathVisible(path, visibleSet(G, "roncz", "r30.shear-web", 2, M)), true);
});

test("pathVisible: a part is present once ANY of its plies is laid", () => {
  const web = { parts: ["canard.shear_web"] };
  assert.equal(st("r30.shear-web", 1)["canard.shear_web.p2"], "hidden");
  assert.equal(pathVisible(web, st("r30.shear-web", 1)), true);
  assert.equal(pathVisible(web, st("r30.shear-web", 0)), false);  // no ply laid yet: every web ply is hidden, none current
});

test("pathVisible: a hidden or ghost part hides the path", () => {
  const p = { parts: ["canard.shear_web", "canard.skin_bottom"] };
  assert.equal(pathVisible(p, st("r30.shear-web", 2)), false);    // skin still hidden
  const g = { ...G, __ghost: true };
  assert.equal(pathVisible(p, st("r30.shear-web", 2, g)), false); // skin ghosted, still not built
  assert.equal(pathVisible(p, st("r30.bottom-skin", 1)), true);
  assert.equal(pathVisible({ parts: ["canard.core"] }, st("r30.cores", 0)), true);
});

test("pathVisible: earlier op hides again; a part with no meshes in state is absent; a plain Map works", () => {
  const p = { parts: ["canard.core", "canard.skin_bottom"] };
  assert.equal(pathVisible(p, st("r30.bottom-skin", 1)), true);
  assert.equal(pathVisible(p, st("r30.shear-web", 2)), false);
  assert.equal(pathVisible({ parts: ["canard.spar_cap_top"] }, st("r30.bottom-skin", 1)), false);  // no such mesh in M
  assert.equal(pathVisible({ parts: ["canard.skin"] }, { "canard.skin_bottom.p1": "built" }), false); // prefix of another id is not a match
  assert.equal(pathVisible({ parts: ["canard.skin"] }, { "canard.skin.pfoo": "built" }), false);    // ply suffix must be .p<digits>
  assert.equal(pathVisible({ parts: ["canard.core"] }, new Map([["canard.core", "built"]])), true);
  assert.equal(pathVisible({ parts: [] }, st("r30.bottom-skin", 1)), false);
});
