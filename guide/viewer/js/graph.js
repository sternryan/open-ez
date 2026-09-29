const COBELU_RAW = "https://raw.githubusercontent.com/cobelu/Long-EZ/master/";

export function visibleOps(graph, variant) {
  const byId = new Map(graph.ops.map(o => [o.id, o]));
  return graph.order.map(id => byId.get(id)).filter(o =>
    o && (o.stub || o.variants.includes("both") || o.variants.includes(variant)));
}

export function opsForComponent(graph, cid) {
  return graph.ops.filter(o => o.components.includes(cid)).map(o => o.id);
}

export function badge(graph, cid) {
  return graph.components[cid]?.fidelity ?? "no-geometry";
}

export function scanView(source, cfg) {
  if (source.scan_pp != null && cfg.scanBase) {
    return { kind: "scan", url: `${cfg.scanBase}${String(source.scan_pp).padStart(3, "0")}.jpg` };
  }
  if (source.figure) return { kind: "figure", url: COBELU_RAW + source.figure };
  return { kind: "none", url: null };
}

export function makeStore(storage) {
  const mem = new Map();
  const key = id => `longez.check.${id}`;

  const get = (opId) => {
    if (!mem.has(opId)) {
      let v = [];
      try {
        const p = JSON.parse(storage.getItem(key(opId)) || "[]");
        if (Array.isArray(p)) v = p.filter(Number.isInteger);
      } catch { /* storage blocked or invalid JSON */ }
      mem.set(opId, new Set(v));
    }
    return mem.get(opId);
  };

  return {
    get,
    toggle(opId, i) {
      const s = get(opId);
      s.has(i) ? s.delete(i) : s.add(i);
      try { storage.setItem(key(opId), JSON.stringify([...s])); } catch { /* keep in memory */ }
    },
  };
}
