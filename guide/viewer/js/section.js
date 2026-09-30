// guide/viewer/js/section.js
// Layers cut at a station. `plies` is the layup.json `nodes` map. Same inequality as Python guide.layup.counts_at.
export function layersAt(plies, bl) {
  return Object.entries(plies)
    .filter(([, p]) => p.bl_max == null || bl <= p.bl_max)
    .sort(([, a], [, b]) => a.op_index - b.op_index || a.order - b.order)
    .map(([node, p]) => ({ node, component: p.component, cloth: p.cloth, order: p.order }));
}

export const fmtBl = bl => `B.L. ${Math.round(bl * 10) / 10}`;

// "Shear web: 2 UND, 1 BID · Top skin: 2 BID", components in build order, in the graph's own labels.
export function summarize(graph, layers) {
  const by = new Map();
  for (const l of layers) {
    if (!by.has(l.component)) by.set(l.component, new Map());
    const c = by.get(l.component); c.set(l.cloth, (c.get(l.cloth) ?? 0) + 1);
  }
  if (!by.size) return "No layers cut here";
  return [...by].map(([cid, c]) => `${graph.components?.[cid]?.label ?? cid}: ${[...c].map(([k, n]) => `${n} ${k}`).join(", ")}`).join(" · ");
}
