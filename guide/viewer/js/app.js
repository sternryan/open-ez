// guide/viewer/js/app.js
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { GLANCE, cutawayFor, hasGlance, readView, writeView, paneMode } from "./cutaway.js";
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
let current = null;

// ---- 3D
const canvas = $("#c");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 10000);
const controls = new OrbitControls(camera, canvas);
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2.2));
function resize() {
  const r = canvas.parentElement.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false); camera.aspect = r.width / Math.max(r.height, 1); camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas.parentElement);
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

new GLTFLoader().load(cfg.model, gltf => {
  scene.add(gltf.scene);
  gltf.scene.traverse(o => {
    if (!o.isMesh) return;
    // GLTFLoader strips dots from node names (canard.core -> canardcore); the original is kept in userData.name.
    const nm = x => x.userData?.name ?? x.name;
    let n = o; while (n && !graph.components[nm(n)] && n.parent) n = n.parent;
    const cid = graph.components[nm(n)] ? nm(n) : nm(o);
    o.material = new THREE.MeshStandardMaterial({ color: 0xc9c4b8 });
    meshes.set(o, cid);
  });
  const box = new THREE.Box3().setFromObject(gltf.scene), c = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  controls.target.copy(c); camera.position.copy(c).add(new THREE.Vector3(size * 1.0, size * 0.8, size * 1.3));
  camera.near = size / 1000; camera.far = size * 10; camera.updateProjectionMatrix();
  applyVariantVisibility();
  if (current && byId.has(current)) highlight(byId.get(current).components);
}, undefined, () => { $("#model-status").textContent = "3D unavailable — steps and sources still work"; });

function applyVariantVisibility() {
  const used = componentsInVariant(graph, $("#variant").value);
  for (const [m, cid] of meshes) m.visible = used.has(cid);
}
function highlight(cids) {
  for (const [m, cid] of meshes) m.material.emissive?.setHex(cids.includes(cid) ? 0x1f5f8b : 0x000000);
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
  current = id; const op = byId.get(id); markSelected([id]);
  $("#op-title").textContent = op.title;
  $("#op-summary").textContent = op.stub ? "Prerequisite outside this slice." : op.summary;
  $("#parts").replaceChildren(...op.components.map(cid => {
    const b = document.createElement("span"); b.className = "chip"; b.dataset.cid = cid; b.dataset.badge = badge(graph, cid);
    b.textContent = `${graph.components[cid]?.label ?? cid} · ${b.dataset.badge}`; b.onclick = () => selectComponent(cid); return b;
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
  highlight(op.components);
  showAll(); applyPane();
}
function selectComponent(cid) {
  const visible = new Set(visibleOps(graph, $("#variant").value).map(o => o.id));
  const ids = opsForComponent(graph, cid).filter(i => visible.has(i));
  markSelected(ids); highlight([cid]);
}
function clearDetail() {
  for (const id of ["#op-title", "#op-summary", "#parts", "#changes", "#source", "#checklist"]) $(id).replaceChildren();
  highlight([]);
  applyPane();
}
function showAll() { /* replaced in Task 11 (ply isolate) */ }
function applyPane() {
  const mode = current ? paneMode(graph, current, view) : "3d";
  $("#viewtoggle").hidden = !(current && current !== GLANCE && cutawayFor(graph, current));
  for (const b of document.querySelectorAll("#viewtoggle button")) b.setAttribute("aria-checked", String(b.dataset.view === view));
  $("#viewport").classList.toggle("paned", mode !== "3d");
  $("#c").hidden = mode !== "3d"; $("#parts").hidden = mode !== "3d";
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
  current = GLANCE; markSelected([GLANCE]); highlight([]); showAll();
  $("#op-title").textContent = "Canard layup at a glance";
  $("#op-summary").textContent = graph.cutaway.count_note;
  for (const id of ["#parts", "#changes", "#source", "#checklist"]) $(id).replaceChildren();
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
window.__guide = { selectComponent, paneMode: () => current ? paneMode(graph, current, view) : "3d", meshComponents: () => [...new Set(meshes.values())],
  visibleMeshComponents: () => [...new Set([...meshes].filter(([m]) => m.visible).map(([, c]) => c))] };
$("#variant").onchange = () => {
  renderList(); applyVariantVisibility();
  const still = current === GLANCE || current && visibleOps(graph, $("#variant").value).some(o => o.id === current);
  if (still) markSelected([current]); else { current = null; clearDetail(); }
};
renderList();
