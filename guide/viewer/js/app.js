// guide/viewer/js/app.js
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { visibleOps, opsForComponent, badge, scanView, makeStore } from "./graph.js";

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
  if (current) highlight(byId.get(current).components);
}, undefined, () => { $("#model-status").textContent = "3D unavailable — steps and sources still work"; });

function highlight(cids) {
  for (const [m, cid] of meshes) m.material.emissive?.setHex(cids.includes(cid) ? 0x1f5f8b : 0x000000);
}
const ray = new THREE.Raycaster();
canvas.addEventListener("click", e => {
  const r = canvas.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
  const hit = ray.intersectObjects([...meshes.keys()])[0];
  if (hit) selectComponent(meshes.get(hit.object));
});

// ---- UI
function renderList() {
  const ol = $("#ops"); ol.replaceChildren();
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
    if (v.kind === "none") { const p = document.createElement("p"); p.className = "none"; p.textContent = `Plans ${s.page ?? "p." + s.scan_pp}: scan not available here`; src.append(p); }
    else { const img = document.createElement("img"); img.src = v.url; img.alt = `Plans ${s.page ?? s.scan_pp}`; img.loading = "lazy"; src.append(img); }
  }
  const ul = $("#checklist"); ul.replaceChildren();
  const done = store.get(id);
  (op.completion ?? []).forEach((t, i) => {
    const li = document.createElement("li"), cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = done.has(i); cb.onchange = () => store.toggle(id, i);
    li.append(cb, " ", t); ul.append(li);
  });
  highlight(op.components);
}
function selectComponent(cid) {
  const visible = new Set(visibleOps(graph, $("#variant").value).map(o => o.id));
  const ids = opsForComponent(graph, cid).filter(i => visible.has(i));
  markSelected(ids); highlight([cid]);
}
function clearDetail() {
  for (const id of ["#op-title", "#op-summary", "#parts", "#changes", "#source", "#checklist"]) $(id).replaceChildren();
  highlight([]);
}
window.__guide = { selectComponent, meshComponents: () => [...new Set(meshes.values())] };
$("#variant").onchange = () => {
  renderList();
  const still = current && visibleOps(graph, $("#variant").value).some(o => o.id === current);
  if (still) markSelected([current]); else { current = null; clearDetail(); }
};
renderList();
