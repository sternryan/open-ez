// guide/viewer/js/cutaway.js — pure view logic for the M2 layup cutaway (no DOM).
export const GLANCE = "__glance";
export const VIEW_KEY = "longez.view";

export function cutawayFor(graph, opId) { return graph.cutaway?.ops?.[opId] ?? null; }
export function hasGlance(graph) { return (graph.cutaway?.heroes?.length ?? 0) > 0; }

export function readView(storage) {
  try { return storage.getItem(VIEW_KEY) === "cutaway" ? "cutaway" : "3d"; } catch { return "3d"; }
}
export function writeView(storage, v) {
  try { storage.setItem(VIEW_KEY, v); } catch { /* per-viewer convenience only */ }
}
export function paneMode(graph, opId, remembered) {
  if (opId === GLANCE) return "glance";
  return cutawayFor(graph, opId) && remembered === "cutaway" ? "cutaway" : "3d";
}
export function plyRows(graph, cid) { return graph.plies?.[cid] ?? []; }
export function isolateLabel(graph, cid, node) {
  const r = plyRows(graph, cid).find(p => p.node === node);
  return `Showing ${graph.components?.[cid]?.label ?? cid} ply ${r?.order ?? "?"}`;
}
