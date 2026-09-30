import { visibleOps } from "./graph.js";

export function firstOp(graph, variant) {
  const m = new Map();
  for (const o of visibleOps(graph, variant)) {
    for (const c of o.components) if (!m.has(c)) m.set(c, o.id);
  }
  return m;
}

export function visibleSet(graph, variant, opId, layIndex, meshes) {
  const idx = new Map(visibleOps(graph, variant).map((o, i) => [o.id, i]));
  const first = firstOp(graph, variant);
  const cur = idx.get(opId);
  if (cur === undefined) throw new Error(`op not in variant: ${opId}`);
  const known = new Set(graph.ops.map(o => o.id));
  const owned = new Set(graph.ops.flatMap(o => o.components));
  const later = graph.__ghost ? "ghost" : "hidden";
  const out = new Map();
  for (const m of meshes) {
    const unowned = m.ply ? !known.has(m.ply.op) : !owned.has(m.component);
    if (unowned) throw new Error(`unowned mesh ${m.name}`);
    const op = m.ply ? m.ply.op : first.get(m.component);
    const i = op === undefined ? undefined : idx.get(op);
    if (i === undefined) out.set(m.name, "hidden");
    else if (i < cur) out.set(m.name, "built");
    else if (i === cur && (!m.ply || m.ply.order <= layIndex)) out.set(m.name, "current");
    else out.set(m.name, later);
  }
  return out;
}
