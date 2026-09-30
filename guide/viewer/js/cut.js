// guide/viewer/js/cut.js
// Section cut with filled caps. Adapted from AirsupHQ/airsup-lab src/core/cut.ts (MIT);
// see NOTICE. Changes: one span-normal plane in the model's B.L. frame; every ply is capped as a
// solid (the plies are thin but closed), no hollow skins.
//
// airsup fills the opened solid by shading its back faces; here each solid gets the stencil variant of the same idea:
// clipped back faces add 1 and clipped front faces subtract 1 (per solid), and a plane sitting on the clip plane paints the
// cap colour wherever that count is non-zero, i.e. wherever the plane opens the solid. No cap geometry is built per station.
// Cost model (Task 3 review): materials are shared (4 stencil materials in all, caps cached per colour/state), the stencil passes are
// built on first enable(true), and each cap plane is sized to its own solid, so a section costs ~2 extra draws per solid.
import * as THREE from "three";

// The glb is exported in inches, and its root node turns CadQuery's Z-up into glTF Y-up: X chordwise, Y up, and B.L. b at Z = -b
// (measured on output/guide/longez.glb: the core spans Z -70.8..0, a bl_max 30 ply Z -30..0). three keeps n.p + c >= 0.
const AXIS = [0, 0, -1];
const CSS = { "--und": "#d9962b", "--bid": "#3a9e98", "--foam": "#dcdcd6" }; // fallbacks: same values as app.css

// Cap colours from the legend's CSS variables, so 3D caps and swatches cannot drift apart.
export function capColors(root = document.documentElement) {
  const cs = getComputedStyle(root), c = n => new THREE.Color(cs.getPropertyValue(n).trim() || CSS[n]);
  return { UND: c("--und"), BID: c("--bid"), foam: c("--foam") };
}

// Station tolerance, inches. A ply that ends AT the station (bl == bl_max, present by counts_at's `bl <= bl_max`) has its end face
// coplanar with the cut plane, where clipping keeps nothing of it. So the plane sits EPS toward the root of the nominal station
// (the ply's last EPS of length is what gets cut), and "crosses" allows the same EPS at either end.
const EPS = 1e-3;
const CAP_MARGIN = 0.5; // inches around a solid's XY bounds

const noRay = () => {};
const stencilMat = (side, op, planes, transparent) => new THREE.MeshBasicMaterial({
  side, colorWrite: false, depthWrite: false, depthTest: false, clippingPlanes: planes, stencilWrite: true, transparent,
  stencilFunc: THREE.AlwaysStencilFunc, stencilFail: op, stencilZFail: op, stencilZPass: op });
const capMat = (color, transparent, opacity) => new THREE.MeshBasicMaterial({
  color, side: THREE.DoubleSide, transparent, opacity, depthWrite: !transparent, stencilWrite: true, stencilRef: 0, stencilFunc: THREE.NotEqualStencilFunc,
  stencilFail: THREE.ReplaceStencilOp, stencilZFail: THREE.ReplaceStencilOp, stencilZPass: THREE.ReplaceStencilOp }); // Replace with ref 0 zeroes what it paints

// The stencil only matters where the plane opens a solid, i.e. inside the cap's rectangle, so each solid's passes and its cap are
// scissored to that rectangle's screen projection (+ a few px). Set in onBeforeRender, reset after the cap; null = do not scissor.
const _v = new THREE.Vector4();
function scissorFor(rd, cam, it, z) {
  const b = it.box, m = CAP_MARGIN, sz = rd.getSize(new THREE.Vector2());
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const x of [b.min.x - m, b.max.x + m]) for (const y of [b.min.y - m, b.max.y + m]) {
    _v.set(x, y, z, 1).applyMatrix4(cam.matrixWorldInverse).applyMatrix4(cam.projectionMatrix);
    if (_v.w <= 1e-6) return rd.setScissorTest(false); // a corner at or behind the eye: no safe rectangle
    const px = (_v.x / _v.w + 1) / 2 * sz.x, py = (_v.y / _v.w + 1) / 2 * sz.y;
    x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
  }
  x0 = Math.max(0, Math.floor(x0) - 2); y0 = Math.max(0, Math.floor(y0) - 2);
  rd.setScissor(x0, y0, Math.max(0, Math.min(sz.x, Math.ceil(x1) + 2) - x0), Math.max(0, Math.min(sz.y, Math.ceil(y1) + 2) - y0));
  rd.setScissorTest(true);
}

// True when the object and every ancestor up to the scene is visible, i.e. it can actually draw.
function shown(o, scene) { for (let x = o; x; x = x.parent) { if (!x.visible) return false; if (x === scene) return true; } return false; }

// entries: [{mesh, name, color}]. A solid is every mesh sharing a `name` (a solid may be split over several meshes, and one mesh alone
// need not be closed). Meshes must be in their world position when this is called (they are static).
export function makeCut(renderer, scene, entries) {
  const plane = new THREE.Plane(new THREE.Vector3(...AXIS), 0), planes = [plane];
  let on = false, bl = 0, items = null;
  const solids = new Map();
  for (const e of entries) {
    if (!solids.has(e.name)) solids.set(e.name, { name: e.name, color: e.color, meshes: [], box: new THREE.Box3() });
    const sd = solids.get(e.name); sd.meshes.push(e.mesh); sd.box.expandByObject(e.mesh);
  }
  const list = [...solids.values()].map(sd => ({ name: sd.name, color: sd.color, meshes: sd.meshes, zmin: sd.box.min.z, zmax: sd.box.max.z, box: sd.box,
    passes: null, cap: null, cut: false, t: null, o: null }));
  const crosses = it => it.zmin - EPS <= -bl && -bl <= it.zmax + EPS;

  // Built on the first enable(true): a viewer that never opens the section pays nothing for it.
  const stencil = {}, caps = new Map();
  function build() {
    items = list;
    for (const t of [false, true]) stencil[t] = [stencilMat(THREE.BackSide, THREE.IncrementWrapStencilOp, planes, t), stencilMat(THREE.FrontSide, THREE.DecrementWrapStencilOp, planes, t)];
    items.forEach((it, i) => {
      const r = 10 + i * 2; // per solid, stencil passes run then the cap, in sequence
      it.passes = it.meshes.map(m => {
        const back = new THREE.Mesh(m.geometry, stencil[false][0]), front = new THREE.Mesh(m.geometry, stencil[false][1]);
        back.renderOrder = front.renderOrder = r; back.raycast = front.raycast = noRay; // caps are not clickable parts
        back.onBeforeRender = front.onBeforeRender = (rd, sc, cam) => scissorFor(rd, cam, it, plane.constant);
        return [m, back, front];
      });
      const sz = it.box.getSize(new THREE.Vector3()), c = it.box.getCenter(new THREE.Vector3());
      it.cap = new THREE.Mesh(new THREE.PlaneGeometry(sz.x + 2 * CAP_MARGIN, sz.y + 2 * CAP_MARGIN), capFor(it.color, false, 1));
      it.cap.renderOrder = r + 1; it.cap.raycast = noRay; it.cap.frustumCulled = false;
      it.cap.onAfterRender = rd => rd.setScissorTest(false);
      it.cap.position.set(c.x, c.y, plane.constant);
    });
  }
  function capFor(color, transparent, opacity) {
    const k = `${color.getHex()}|${transparent}|${opacity}`;
    if (!caps.has(k)) caps.set(k, capMat(color, transparent, opacity));
    return caps.get(k);
  }

  // Re-derive which solids are capped and how they look from their meshes (visibility, ghost/isolate opacity). Cheap, not per frame.
  function sync() {
    if (!items) return;
    for (const it of items) {
      const m = it.meshes[0].material, vis = on && it.meshes[0].visible && crosses(it);
      it.cut = vis; it.cap.visible = vis;
      for (const [, b, f] of it.passes) b.visible = f.visible = vis;
      if (!vis || (it.t === m.transparent && it.o === m.opacity)) continue;
      it.t = m.transparent; it.o = m.opacity;
      // A see-through solid is capped see-through, and every pass of it goes in the transparent list so its stencil passes still run in sequence.
      for (const [, b, f] of it.passes) { b.material = stencil[m.transparent][0]; f.material = stencil[m.transparent][1]; }
      it.cap.material = capFor(it.color, m.transparent, m.opacity);
    }
  }
  return {
    setStation(b) { bl = b; plane.constant = -b + EPS; if (items) for (const it of items) it.cap.position.z = plane.constant; sync(); },
    enable(v) {
      if (v === on) return;
      if (v && !items) build();
      on = v; renderer.localClippingEnabled = v;
      for (const it of list) {
        for (const m of it.meshes) { m.material.clippingPlanes = v ? planes : null; m.material.needsUpdate = true; }
        if (!items) continue;
        for (const [m, b, f] of it.passes) { if (v) m.add(b, f); else { b.removeFromParent(); f.removeFromParent(); } }
        if (v) { it.cap.position.z = plane.constant; scene.add(it.cap); } else it.cap.removeFromParent();
        it.t = it.o = null;
      }
      sync();
    },
    sync,
    info: () => {
      const objs = it => (items && it.cap ? [it.cap, ...it.passes.flatMap(([, b, f]) => [b, f])] : []);
      return { enabled: on, bl, axis: [...AXIS], planeConstant: plane.constant,
        cappedNodes: on && items ? items.filter(it => it.cut).map(it => it.name) : [],
        clipped: list.reduce((n, it) => n + it.meshes.filter(m => m.material.clippingPlanes?.length).length, 0),
        capObjects: list.reduce((n, it) => n + objs(it).filter(o => o.parent).length, 0),
        // what can actually draw: visible all the way up to the scene (a cap under a build-hidden solid must not count)
        capsVisible: list.reduce((n, it) => n + objs(it).filter(o => shown(o, scene)).length, 0),
        capNodesVisible: list.filter(it => objs(it).some(o => shown(o, scene))).map(it => it.name) };
    },
  };
}
