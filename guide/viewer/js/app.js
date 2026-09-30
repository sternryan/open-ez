// guide/viewer/js/app.js
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { GLANCE, plyRows, isolateLabel, cutawayFor, hasGlance, readView, writeView, paneMode } from "./cutaway.js";
import { visibleSet } from "./build.js";
import { componentsInVariant, sourceLabel, noneMessage, visibleOps, opsForComponent, badge, scanView, makeStore } from "./graph.js";

const $ = s => document.querySelector(s);
let storage; try { storage = window.localStorage; } catch { storage = null; }
const store = makeStore(storage ?? { getItem() { return null; }, setItem() {} });
let graph, cfg;
try {
  [graph, cfg] = await Promise.all([
    fetch("graph.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("config.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })]);
} catch {
  const li = document.createElement("li"); li.textContent = "Could not load graph.json"; $("#ops").append(li);
  throw new Error("graph load failed");
}
let view = readView(storage ?? { getItem() { return null; } });
const byId = new Map(graph.ops.map(o => [o.id, o]));
const meshes = new Map();
const plyNode = new Map(); let isolated = null;
let current = null;
const qs = new URLSearchParams(location.search), TEST = qs.get("test") === "1", STEP_MS = qs.get("fast") === "1" ? 30 : 700;
const GHOST_KEY = "longez.ghost";
try { graph.__ghost = storage?.getItem(GHOST_KEY) === "1"; } catch { graph.__ghost = false; }
$("#ghost").checked = !!graph.__ghost;
const plyInfo = new Map(); for (const rows of Object.values(graph.plies ?? {})) for (const r of rows) plyInfo.set(r.node, { op: r.op, order: r.order });
let layIndex = 0, timer = null;

// ---- 3D
const canvas = $("#c");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 10000);
const controls = new OrbitControls(camera, canvas);
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2.2));
function resize() {
  const r = canvas.getBoundingClientRect(); // the canvas, not #viewport: at phone width the controls flow below it inside #viewport
  renderer.setSize(r.width, r.height, false); camera.aspect = r.width / Math.max(r.height, 1); camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas);
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

new GLTFLoader().load(cfg.model, gltf => {
  scene.add(gltf.scene);
  gltf.scene.traverse(o => {
    if (!o.isMesh) return;
    // GLTFLoader strips dots from node names (canard.core -> canardcore); the original is kept in userData.name.
    const nm = x => x.userData?.name ?? x.name;
    let n = o; while (n && !graph.components[nm(n)] && n.parent) n = n.parent;
    const cid = graph.components[nm(n)] ? nm(n) : nm(o);
    // Each mesh gets its own material instance, so isolating one ply never leaks opacity to another.
    o.material = new THREE.MeshStandardMaterial({ color: 0xc9c4b8 });
    meshes.set(o, cid);
    let q = o; while (q && !/\.p\d+$/.test(nm(q)) && q.parent) q = q.parent;
    if (q && /\.p\d+$/.test(nm(q))) plyNode.set(o, nm(q));
  });
  const box = new THREE.Box3().setFromObject(gltf.scene), c = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  controls.target.copy(c); camera.position.copy(c).add(new THREE.Vector3(size * 1.0, size * 0.8, size * 1.3));
  camera.near = size / 1000; camera.far = size * 10; camera.updateProjectionMatrix();
  home = { target: controls.target.clone(), position: camera.position.clone() };
  applyVariantVisibility();
  if (current && byId.has(current)) highlight(byId.get(current).components);
  if (isolated) isolate(isolated); else applyBuild();
}, undefined, () => { $("#model-status").textContent = "3D unavailable — steps and sources still work"; });

function applyVariantVisibility() {
  const used = componentsInVariant(graph, $("#variant").value);
  for (const [m, cid] of meshes) m.visible = used.has(cid);
}
// Build state: recomputed from scratch on every change, never patched (a ply must not outlive its step).
function opPlies(id) { return Object.values(graph.plies ?? {}).flat().filter(r => r.op === id).length; }
function buildOp() {
  const op = current && byId.get(current);
  return op && !op.stub && visibleOps(graph, $("#variant").value).some(o => o.id === current) ? op : null;
}
function buildState() {
  const op = buildOp(); if (!op || !meshes.size) return null;
  const seen = new Map();
  for (const [m, cid] of meshes) {
    const name = plyNode.get(m) ?? cid;
    if (!seen.has(name)) seen.set(name, { name, component: cid, ply: plyInfo.get(name) ?? null });
  }
  return visibleSet(graph, $("#variant").value, op.id, layIndex, [...seen.values()]);
}
function applyBuild() {
  if (isolated) return;
  const st = buildState();
  if (!st) { applyVariantVisibility(); return; }
  for (const [m, cid] of meshes) {
    const s = st.get(plyNode.get(m) ?? cid), mat = m.material, ghost = s === "ghost";
    m.visible = s !== "hidden";
    // While an op with a build state is selected, this `current` emissive wins over any chip highlight (chips only re-highlight via highlight()).
    mat.emissive?.setHex(s === "current" ? 0x1f5f8b : 0x000000);
    mat.transparent = ghost; mat.opacity = ghost ? 0.2 : 1; mat.depthWrite = !ghost;
    mat.needsUpdate = true; // transparent toggles the OPAQUE shader define; without this nothing ghosts on screen
  }
}
function stopPlay() { clearInterval(timer); timer = null; $("#play").setAttribute("aria-pressed", "false"); $("#play").textContent = "Play"; }
function setLay(n) { layIndex = n; $("#scrub").value = n; $("#scrublabel").textContent = `Ply ${n} of ${$("#scrub").max}`; applyBuild(); }
function syncBuildbar() {
  const on = !!buildOp() && $("#c").hidden === false, n = on ? opPlies(current) : 0;
  $("#buildbar").hidden = !on; $("#scrubwrap").hidden = n === 0;
}
$("#ghost").onchange = e => {
  graph.__ghost = e.target.checked; try { storage?.setItem(GHOST_KEY, graph.__ghost ? "1" : "0"); } catch { /* per-viewer convenience only */ }
  applyBuild();
};
$("#scrub").oninput = e => { stopPlay(); setLay(+e.target.value); };
$("#play").onclick = () => {
  if (timer) return stopPlay();
  const max = +$("#scrub").max; setLay(1);
  $("#play").setAttribute("aria-pressed", "true"); $("#play").textContent = "Stop";
  timer = setInterval(() => { if (layIndex >= max) return stopPlay(); setLay(layIndex + 1); if (layIndex >= max) stopPlay(); }, STEP_MS);
};
function highlight(cids) {
  for (const [m, cid] of meshes) m.material.emissive?.setHex(cids.includes(cid) ? 0x1f5f8b : 0x000000);
}
let home = null;
function flyTo(target, position) { controls.target.copy(target); camera.position.copy(position); controls.update(); }
// Plies are long and thin along the span, so framing a whole ply barely zooms in. Aim at the ply's
// inboard end from about one ply-width-plus-chord away, keeping the home view's direction.
function zoomToPly(node) {
  if (!home) return;
  const ms = [...meshes.keys()].filter(m => plyNode.get(m) === node);
  if (!ms.length) return;
  const box = new THREE.Box3(); for (const m of ms) box.expandByObject(m);
  const sz = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
  const target = new THREE.Vector3(c.x, box.min.y + Math.min(sz.y / 4, 10), c.z).clamp(box.min, box.max);
  const dir = home.position.clone().sub(home.target).normalize();
  flyTo(target, target.clone().add(dir.multiplyScalar(Math.max(sz.x, sz.z, 6) * 2.5)));
}
const ray = new THREE.Raycaster();
canvas.addEventListener("click", e => {
  const r = canvas.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
  const hit = ray.intersectObjects([...meshes.keys()].filter(m => m.visible))[0];
  if (hit) selectComponent(meshes.get(hit.object));
});

// ---- UI
function renderList() {
  const ol = $("#ops"); ol.replaceChildren();
  if (hasGlance(graph)) {
    const li = document.createElement("li"); li.dataset.op = GLANCE; li.className = "glance";
    li.textContent = "Canard layup at a glance"; li.onclick = selectGlance; ol.append(li);
  }
  for (const op of visibleOps(graph, $("#variant").value)) {
    const li = document.createElement("li");
    li.dataset.op = op.id; li.textContent = op.title; if (op.stub) li.className = "stub";
    li.onclick = () => selectOp(op.id); ol.append(li);
  }
}
function markSelected(ids) {
  for (const li of document.querySelectorAll("#ops li")) li.classList.toggle("selected", ids.includes(li.dataset.op));
}
function selectOp(id) {
  current = id; const op = byId.get(id); markSelected([id]); $("#plydock").hidden = true;
  $("#op-title").textContent = op.title;
  $("#op-summary").textContent = op.stub ? "Prerequisite outside this slice." : op.summary;
  $("#parts").replaceChildren(...op.components.map(cid => {
    const b = document.createElement("button"); b.type = "button"; b.className = "chip"; b.dataset.cid = cid; b.dataset.badge = badge(graph, cid);
    b.textContent = `${graph.components[cid]?.label ?? cid} · ${b.dataset.badge}`;
    const rows = cutawayFor(graph, id) ? plyRows(graph, cid) : [];
    if (rows.length) b.textContent += ` · ${rows.length} plies`;
    if (rows.length) { b.setAttribute("aria-controls", "plydock"); b.setAttribute("aria-expanded", "false"); }
    b.onclick = e => { selectComponent(cid); if (rows.length) toggleDock(cid, e.detail === 0); };
    return b;
  }));
  $("#changes").replaceChildren(...(op.changes ?? []).map(c => {
    const d = document.createElement("div"); d.className = "change";
    d.textContent = `CP ${c.cp} · LPC ${c.lpc} · ${c.class} · ${c.status}: ${c.note}`; return d;
  }));
  const src = $("#source"); src.replaceChildren();
  for (const s of op.sources ?? []) {
    const v = scanView(s, cfg);
    if (v.kind === "none") { const p = document.createElement("p"); p.className = "none"; p.textContent = noneMessage(s); src.append(p); }
    else { const img = document.createElement("img"); img.src = v.url; img.alt = `Plans ${sourceLabel(s)}`; img.loading = "lazy"; src.append(img); }
  }
  const ul = $("#checklist"); ul.replaceChildren();
  const done = store.get(id);
  (op.completion ?? []).forEach((t, i) => {
    const li = document.createElement("li"), cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = done.has(i); cb.onchange = () => store.toggle(id, i);
    li.append(cb, " ", t); ul.append(li);
  });
  syncChecklistHeading();
  highlight(op.components);
  stopPlay(); const n = opPlies(id); $("#scrub").max = n; setLay(n);
  showAll(); applyPane();
}
function selectComponent(cid) {
  const visible = new Set(visibleOps(graph, $("#variant").value).map(o => o.id));
  const ids = opsForComponent(graph, cid).filter(i => visible.has(i));
  markSelected(ids); highlight([cid]);
}
function clearDetail() {
  for (const id of ["#op-title", "#op-summary", "#parts", "#changes", "#source", "#checklist"]) $(id).replaceChildren();
  $("#plydock").hidden = true; stopPlay(); showAll(); syncChecklistHeading();
  highlight([]);
  applyPane();
}
function syncChecklistHeading() { $("#checklist-h").hidden = $("#checklist").children.length === 0; }
function isolate(node) {
  stopPlay(); isolated = node; // isolate overrides the build state's look until cleared; hidden plies stay hidden except the isolated one
  const st = buildState(); if (!st) applyVariantVisibility();
  for (const [m, cid] of meshes) {
    const on = plyNode.get(m) === node;
    if (st) m.visible = on || st.get(plyNode.get(m) ?? cid) !== "hidden";
    m.material.transparent = !on; m.material.opacity = on ? 1 : 0.15; m.material.depthWrite = on;
    m.material.needsUpdate = true; // transparent toggles the OPAQUE shader define; without this nothing ghosts on screen
  }
  const cid = $("#plydock").dataset.cid;
  $("#isotext").textContent = isolateLabel(graph, cid, node); $("#isobar").hidden = false;
  $("#viewport").classList.add("isolating");
  zoomToPly(node);
  for (const b of document.querySelectorAll("#plydock button")) b.setAttribute("aria-pressed", String(b.dataset.node === node));
}
function showAll() {
  isolated = null;
  for (const [m] of meshes) {
    m.material.transparent = false; m.material.opacity = 1; m.material.depthWrite = true; m.material.needsUpdate = true;
  }
  applyBuild();
  $("#isobar").hidden = true; $("#viewport").classList.remove("isolating");
  if (home) flyTo(home.target, home.position);
  for (const b of document.querySelectorAll("#plydock button")) b.setAttribute("aria-pressed", "false");
}
function toggleDock(cid, viaKeyboard) {
  const dock = $("#plydock");
  if (!dock.hidden && dock.dataset.cid === cid) { dock.hidden = true; return; }
  dock.dataset.cid = cid;
  dock.replaceChildren(...plyRows(graph, cid).map(r => {
    const b = document.createElement("button"); b.type = "button"; b.dataset.node = r.node; b.setAttribute("aria-pressed", String(isolated === r.node));
    const sw = document.createElement("i"); sw.className = `sw ${r.position_verified ? r.cloth.toLowerCase() : "unverified"}`;
    b.append(sw, `${r.order} · ${r.cloth} · ${r.where}`);
    b.onclick = () => (isolated === r.node ? showAll() : isolate(r.node));
    return b;
  }));
  dock.setAttribute("role", "group"); dock.setAttribute("aria-label", `${graph.components[cid]?.label ?? cid} plies`);
  dock.hidden = false;
  if (viaKeyboard) dock.querySelector("button")?.focus(); // dock sits after the chips in tab order; land on the first row
}
$("#showall").onclick = showAll;
// chips reflect whether the dock is open for them, however the dock got closed
new MutationObserver(() => { const d = $("#plydock");
  for (const b of document.querySelectorAll("#parts .chip[aria-controls]")) b.setAttribute("aria-expanded", String(!d.hidden && d.dataset.cid === b.dataset.cid));
}).observe($("#plydock"), { attributes: true, attributeFilter: ["hidden", "data-cid"] });
function applyPane() {
  const mode = current ? paneMode(graph, current, view) : "3d";
  $("#viewtoggle").hidden = !(current && current !== GLANCE && cutawayFor(graph, current));
  for (const b of document.querySelectorAll("#viewtoggle button")) b.setAttribute("aria-checked", String(b.dataset.view === view));
  $("#viewport").classList.toggle("paned", mode !== "3d");
  $("#c").hidden = mode !== "3d"; $("#parts").hidden = mode !== "3d"; syncBuildbar();
  if (mode !== "3d") { stopPlay(); $("#plydock").hidden = true; showAll(); }
  for (const b of document.querySelectorAll("#viewtoggle button")) b.tabIndex = b.dataset.view === view ? 0 : -1;
  $("#cutpane").hidden = mode !== "cutaway"; $("#glance").hidden = mode !== "glance";
  $("#legend").hidden = mode !== "glance"; document.querySelector("main").classList.toggle("glance", mode === "glance");
  if (mode === "cutaway") showCut(cutawayFor(graph, current));
  if (mode === "3d") resize();
}
function showCut(c) {
  const img = $("#cutimg"), fig = $("#cutpane"); $("#cuterr").hidden = true; img.hidden = false; $("#cutzoom").hidden = false;
  fig.classList.add("loading");
  img.onload = () => fig.classList.remove("loading");
  img.onerror = () => { fig.classList.remove("loading"); img.hidden = true; $("#cutzoom").hidden = true; $("#cuterr").hidden = false; };
  img.alt = c.alt; img.src = c.src; $("#cutcap").textContent = c.alt;
}
function zoom(src, alt) {
  const im = document.createElement("img"); im.src = src; im.alt = alt;
  $("#zoombody").replaceChildren(im); $("#zoom").showModal();
}
function selectGlance() {
  stopPlay(); current = GLANCE; markSelected([GLANCE]); highlight([]); showAll(); $("#plydock").hidden = true;
  $("#op-title").textContent = "Canard layup at a glance";
  $("#op-summary").textContent = graph.cutaway.count_note;
  for (const id of ["#parts", "#changes", "#source", "#checklist"]) $(id).replaceChildren();
  syncChecklistHeading();
  $("#glance").replaceChildren(...graph.cutaway.heroes.map(h => {
    const f = document.createElement("figure"), b = document.createElement("button"), im = document.createElement("img");
    b.className = "imgbtn"; b.setAttribute("aria-label", `Enlarge section at BL ${h.bl}`);
    im.src = h.src; im.alt = h.alt; im.onerror = () => { b.hidden = true; f.append(Object.assign(document.createElement("p"), { className: "err", textContent: "Section picture didn't load." })); };
    b.append(im); b.onclick = () => zoom(h.src, h.alt);
    const cap = document.createElement("figcaption"); cap.textContent = `BL ${h.bl} (${h.bl < 20 ? "inboard" : "outboard"})`;
    f.append(b, cap); return f;
  }));
  const ul = document.createElement("ul");
  for (const l of graph.cutaway.legend) {
    const li = document.createElement("li");
    if (l.swatch) { const s = document.createElement("i"); s.className = `sw ${l.swatch}`; li.append(s); }
    li.append(l.text); ul.append(li);
  }
  const h = document.createElement("h3"); h.textContent = "Legend";
  $("#legend").replaceChildren(h, ul);
  applyPane();
}
for (const b of document.querySelectorAll("#viewtoggle button")) {
  b.onclick = () => { view = b.dataset.view; writeView(storage ?? { setItem() {} }, view); applyPane(); };
  b.onkeydown = e => {
    if (["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp"].includes(e.key)) { e.preventDefault(); const o = [...document.querySelectorAll("#viewtoggle button")].find(x => x !== b); o.focus(); o.click(); }
  };
}
$("#cutzoom").onclick = () => zoom($("#cutimg").src, $("#cutimg").alt);
$("#cutretry").onclick = () => { const c = cutawayFor(graph, current); if (c) showCut({ ...c, src: `${c.src}?r=${Date.now()}` }); };
$("#zoomclose").onclick = () => $("#zoom").close();
document.addEventListener("keydown", e => { if (e.key === "Escape" && !$("#zoom").open) showAll(); });
window.__guide = { selectComponent, isolated: () => isolated,
  flyHome: () => { if (home) flyTo(home.target, home.position); },
  camera: () => ({ target: controls.target.toArray(), distance: camera.position.distanceTo(controls.target) }),
  plyBox: node => { const b = new THREE.Box3(); for (const m of meshes.keys()) if (plyNode.get(m) === node) b.expandByObject(m); return { min: b.min.toArray(), max: b.max.toArray() }; }, meshPlies: () => [...new Set(plyNode.values())],
  meshOpacities: () => [...meshes.keys()].map(m => ({ node: plyNode.get(m) ?? null, component: meshes.get(m), opacity: m.material.opacity, emissive: m.material.emissive?.getHex() ?? 0, visible: m.visible })), paneMode: () => current ? paneMode(graph, current, view) : "3d", meshComponents: () => [...new Set(meshes.values())],
  visibleMeshComponents: () => [...new Set([...meshes].filter(([m]) => m.visible).map(([, c]) => c))] };
$("#variant").onchange = () => {
  renderList(); applyVariantVisibility(); stopPlay();
  const still = current === GLANCE || current && visibleOps(graph, $("#variant").value).some(o => o.id === current);
  if (still) markSelected([current]); else { current = null; clearDetail(); }
  if (isolated) { // applyVariantVisibility() just un-hid build-hidden plies: redo the isolate rule, or drop it if its ply left the variant
    const used = componentsInVariant(graph, $("#variant").value);
    if ([...meshes].some(([m, cid]) => plyNode.get(m) === isolated && used.has(cid))) isolate(isolated); else showAll();
  } else applyBuild();
  syncBuildbar();
};
if (TEST) {
  window.__buildState = () => { const st = buildState(); return st ? Object.fromEntries(st) : {}; };
  window.__visibleNames = () => [...new Set([...meshes.keys()].filter(m => m.visible).map(m => plyNode.get(m) ?? meshes.get(m)))];
}
renderList();
