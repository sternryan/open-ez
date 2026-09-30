// guide/viewer/js/tour.js: chapter tours. Pure and deterministic: no clock, no DOM; the caller feeds frame dt.
import { visibleOps } from "./graph.js";

// One step per visible, non-stub op of the chapter, in graph order. A stub is a prerequisite outside the slice: nothing to build, so no stop.
// `shot` is the op's authored camera shot ({target, position}, world inches), or null for the home view.
export function tourSteps(graph, variant, chapter) {
  const shots = graph.tours ?? {};
  return visibleOps(graph, variant).filter(o => o.chapter === chapter && !o.stub).map(o => ({ op: o.id, shot: shots[o.id] ?? null }));
}

export function tourStart(n, dwell) {
  return { i: 0, t: 0, n, dwell, done: n <= 0 };
}

const EPS = 1e-9; // dt sums like 0.1 + 0.2 must still land on the boundary
// Advance by dt seconds: step i lasts `dwell`; past the last step, `done` is true and i === n. Returns a new state.
export function stepTour(state, dt) {
  if (state.done) return state;
  const { n, dwell } = state;
  let i = state.i, t = state.t + dt;
  while (t >= dwell - EPS && i < n) { t = Math.max(0, t - dwell); i++; }
  return i >= n ? { i: n, t: 0, n, dwell, done: true } : { i, t, n, dwell, done: false };
}
