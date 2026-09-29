import { test } from "node:test";
import assert from "node:assert/strict";
import { visibleOps, opsForComponent, badge, scanView, makeStore } from "../js/graph.js";

const G = {
  order: ["s", "a", "b", "c"],
  ops: [
    { id: "a", variants: ["gu"], components: ["canard.core"], stub: false },
    { id: "b", variants: ["roncz"], components: ["canard.core", "canard.skin_top"], stub: false },
    { id: "c", variants: ["both"], components: [], stub: false },
    { id: "s", variants: ["both"], components: [], stub: true },
  ],
  components: { "canard.core": { label: "Core", fidelity: "unvalidated" } },
};

test("visibleOps filters by variant and keeps order + stubs", () => {
  assert.deepEqual(visibleOps(G, "roncz").map(o => o.id), ["s", "b", "c"]);
  assert.deepEqual(visibleOps(G, "gu").map(o => o.id), ["s", "a", "c"]);
});

test("opsForComponent", () => {
  assert.deepEqual(opsForComponent(G, "canard.core"), ["a", "b"]);
});

test("badge falls back to no-geometry", () => {
  assert.equal(badge(G, "canard.core"), "unvalidated");
  assert.equal(badge(G, "canard.skin_top"), "no-geometry");
});

test("scanView: private scan, figure fallback, none", () => {  // Review Focus 1
  const cfg = { scanBase: "/private/scan-1980/pages/" };
  assert.deepEqual(scanView({ scan_pp: 58 }, cfg), { kind: "scan", url: "/private/scan-1980/pages/058.jpg" });
  assert.deepEqual(scanView({ scan_pp: 58, figure: "I/images/10/10_02.png" }, { scanBase: null }),
    { kind: "figure", url: "https://raw.githubusercontent.com/cobelu/Long-EZ/master/I/images/10/10_02.png" });
  assert.deepEqual(scanView({ scan_pp: 58 }, { scanBase: null }), { kind: "none", url: null });
});

test("makeStore survives a throwing storage", () => {  // Review Focus 2
  const bad = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } };
  const s = makeStore(bad);
  s.toggle("a", 1);
  assert.deepEqual([...s.get("a")], [1]);
});

test("makeStore tolerates non-array storage (object)", () => {
  const mock = { getItem() { return "{}"; }, setItem() {} };
  const s = makeStore(mock);
  assert.deepEqual([...s.get("x")], []);
});

test("makeStore tolerates non-array storage (string)", () => {
  const mock = { getItem() { return '"abc"'; }, setItem() {} };
  const s = makeStore(mock);
  assert.deepEqual([...s.get("y")], []);
});

test("makeStore persists across instances via storage", () => {
  const storage = new Map();
  storage.getItem = (k) => storage.get(k) ?? null;
  storage.setItem = (k, v) => storage.set(k, v);

  const s1 = makeStore(storage);
  s1.toggle("z", 5);
  s1.toggle("z", 7);

  const s2 = makeStore(storage);
  assert.deepEqual([...s2.get("z")].sort((a, b) => a - b), [5, 7]);
});

test("scanView with relative base path", () => {
  const cfg = { scanBase: "private/scan-1980/pages/" };
  assert.deepEqual(scanView({ scan_pp: 58 }, cfg),
    { kind: "scan", url: "private/scan-1980/pages/058.jpg" });
});
