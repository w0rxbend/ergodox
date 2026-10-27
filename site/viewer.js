// Interactive viewer for the case parts. Model frame: mm, Z up, -Y towards the typist.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { toCreasedNormals } from "three/addons/utils/BufferGeometryUtils.js";

const FINISHES = {
  black: { name: "Black", color: 0x1e1f23 },
  silver: { name: "Silver", color: 0xc4c8ce },
  grey: { name: "Space grey", color: 0x60656d },
  blue: { name: "Blue", color: 0x2a5ca8 },
  red: { name: "Red", color: 0xa82530 },
  orange: { name: "Orange", color: 0xd8601e },
};
const PAIR_GAP = 30;   // mm between the inner edges of the halves
const EXPLODE_TOP = 34;
const EXPLODE_LEG = 26;

const $ = (id) => document.getElementById(id);
const canvas = $("canvas");
const stage = $("stage");

const state = {
  scene: "pair", finish: "black", explode: 0, section: 0, swing: 90,
  legs: true, top: true, bottom: true, spacer: true, edges: true, spin: false,
};
// share the scene and finish through the URL hash
for (const kv of location.hash.slice(1).split("&")) {
  const [k, v] = kv.split("=");
  if (k === "scene" && ["pair", "right", "left", "leg"].includes(v)) state.scene = v;
  if (k === "finish" && v in FINISHES) state.finish = v;
}

// ---------- renderer, scene, camera ----------
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.setClearColor(0x000000, 0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const camera = new THREE.PerspectiveCamera(35, 1, 1, 5000);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.autoRotateSpeed = 1.2;

const key = new THREE.DirectionalLight(0xffffff, 1.6);
key.position.set(-250, -350, 500);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.bias = -0.0004;
scene.add(key, key.target);
scene.add(new THREE.HemisphereLight(0xdde6ff, 0x20160f, 0.5));
const rim = new THREE.DirectionalLight(0xffb27f, 0.6);
rim.position.set(300, 400, 120);
scene.add(rim);

const ground = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: 0.35 }));
ground.receiveShadow = true;
scene.add(ground);

// ---------- materials ----------
const clip = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const clipping = () => (state.section > 0 ? [clip] : []);
const alu = new THREE.MeshStandardMaterial({ color: FINISHES[state.finish].color, metalness: 0.75, roughness: 0.42 });
const tpu = new THREE.MeshStandardMaterial({ color: 0x18191b, metalness: 0, roughness: 0.9 });
const printed = new THREE.MeshStandardMaterial({ color: 0xc8692a, metalness: 0, roughness: 0.75 });
// back faces show through a section cut as solid orange, which reads as a cut face
const cutFace = new THREE.MeshBasicMaterial({ color: 0xff6a1a, side: THREE.BackSide });
const edgeMat = new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 });
const highlight = new THREE.MeshStandardMaterial({ color: 0xff8a3d, metalness: 0.4, roughness: 0.5, emissive: 0x401400 });
const allMats = [alu, tpu, printed, cutFace, edgeMat, highlight];

// ---------- loading ----------
const manifest = await fetch("manifest.json").then((r) => r.json());
$("version").textContent = manifest.version;
const names = Object.keys(manifest.parts);
const geoms = {};
const edges = {};
const progress = Object.fromEntries(names.map((n) => [n, 0]));
const loader = new STLLoader();
const updateBar = () => {
  const p = Object.values(progress).reduce((a, b) => a + b, 0) / names.length;
  $("loadbar").style.width = `${(p * 100).toFixed(0)}%`;
};
await Promise.all(names.map((n) => new Promise((resolve, reject) => {
  loader.load(manifest.parts[n].file, (g) => {
    g.deleteAttribute("normal");
    geoms[n] = toCreasedNormals(g, THREE.MathUtils.degToRad(28));
    geoms[n].computeBoundingBox();
    edges[n] = new THREE.EdgesGeometry(g, 28);
    progress[n] = 1; updateBar(); resolve();
  }, (e) => { if (e.total) { progress[n] = e.loaded / e.total; updateBar(); } }, reject);
}))).catch((e) => { $("loadtext").textContent = `failed to load models: ${e.message || e}`; throw e; });
$("loader").classList.add("done");

// ---------- scene assembly ----------
const pickable = [];

function partMesh(name, mat) {
  const m = new THREE.Mesh(geoms[name], mat);
  m.castShadow = m.receiveShadow = true;
  m.userData.part = name;
  m.userData.mat = mat;
  const cap = new THREE.Mesh(geoms[name], cutFace);
  const lines = new THREE.LineSegments(edges[name], edgeMat);
  lines.userData.isEdge = true;
  const g = new THREE.Group();
  g.add(m, cap, lines);
  pickable.push(m);
  return g;
}

function legAssembly() {
  // leg + cap, built along +Y from the hub axis; swing turns it about local Z
  const g = new THREE.Group();
  const cap = partMesh("leg_cap", tpu);
  cap.userData.isCap = true;
  g.add(partMesh("leg", alu), cap);
  return g;
}

function half(side) {
  const g = new THREE.Group();
  const top = new THREE.Group();
  top.add(partMesh(`${side}_top`, alu));
  const bottom = partMesh(`${side}_bottom`, alu);
  const spacer = partMesh(`${side}_spacer`, printed);
  const legs = new THREE.Group();
  const mirror = new THREE.Matrix4().makeScale(side === "left" ? -1 : 1, 1, 1);
  for (const arr of manifest.legs) {
    const mount = new THREE.Group();
    mount.matrixAutoUpdate = false;
    mount.matrix.multiplyMatrices(mirror, new THREE.Matrix4().fromArray(arr).transpose());
    const swing = legAssembly();
    swing.userData.swing = true;
    mount.add(swing);
    legs.add(mount);
  }
  top.add(legs);
  g.add(top, spacer, bottom);
  Object.assign(g.userData, { top, bottom, spacer, legs });
  return g;
}

let root = new THREE.Group();
scene.add(root);
let halves = [];
let soloLeg = null;

function build() {
  scene.remove(root);
  root = new THREE.Group();
  pickable.length = 0;
  halves = [];
  soloLeg = null;
  if (state.scene === "leg") {
    soloLeg = legAssembly();
    soloLeg.rotation.set(Math.PI / 2, Math.PI, 0);   // stand the leg up, toothed face to the camera
    root.add(soloLeg);
  } else {
    const sides = state.scene === "pair" ? ["left", "right"] : [state.scene];
    for (const side of sides) {
      const h = half(side);
      if (state.scene === "pair") {
        const bb = geoms[`${side}_top`].boundingBox;
        h.position.x = side === "right" ? -bb.min.x + PAIR_GAP / 2 : -bb.max.x - PAIR_GAP / 2;
      }
      halves.push(h);
      root.add(h);
    }
  }
  scene.add(root);
  apply();
  frame();
}

// ---------- state -> scene ----------
function apply() {
  alu.color.setHex(FINISHES[state.finish].color);
  for (const m of allMats) { m.clippingPlanes = clipping(); m.needsUpdate = true; }
  for (const h of halves) {
    const { top, bottom, spacer, legs } = h.userData;
    top.position.z = state.explode * EXPLODE_TOP;
    spacer.position.z = state.explode * EXPLODE_TOP * 0.5;
    spacer.visible = state.spacer;
    top.visible = state.top;
    bottom.visible = state.bottom;
    legs.visible = state.legs;
  }
  root.traverse((o) => {
    if (o.userData.swing) o.rotation.z = THREE.MathUtils.degToRad(state.swing);
    if (o.userData.isEdge) o.visible = state.edges;
    if (o.userData.isCap) o.position.y = state.explode * EXPLODE_LEG;
  });

  root.updateMatrixWorld(true);
  const box = visibleBox();
  ground.position.z = box.isEmpty() ? 0 : box.min.z - 0.05;
  // section plane sweeps front to back through the visible parts
  if (state.section > 0 && !box.isEmpty()) {
    const y = box.min.y + state.section * (box.max.y - box.min.y);
    clip.constant = -y;
    $("sectionVal").textContent = `y ${y.toFixed(1)}`;
  } else $("sectionVal").textContent = "off";
  $("explodeVal").textContent = state.explode ? `${Math.round(state.explode * EXPLODE_TOP)} mm` : "0";
  $("swingVal").textContent = `${state.swing}°${state.swing === 90 ? " · down" : state.swing % 180 === 0 ? " · stowed" : ""}`;
  controls.autoRotate = state.spin;
  $("swingGroup").style.opacity = state.legs || state.scene === "leg" ? 1 : 0.4;
  hud(box);
  location.replace(`#scene=${state.scene}&finish=${state.finish}`);
}

function visibleBox() {
  const box = new THREE.Box3();
  root.traverseVisible((o) => { if (o.isMesh && o.userData.part) box.expandByObject(o); });
  return box;
}

function hud(box) {
  if (box.isEmpty()) { $("hud").textContent = "nothing visible"; return; }
  const s = box.getSize(new THREE.Vector3());
  const visible = new Set();
  root.traverseVisible((o) => { if (o.isMesh && o.userData.part) visible.add(o.userData.part); });
  const mass = [...visible].reduce((a, n) => a + (manifest.parts[n].mass_g || 0), 0);
  $("hud").textContent =
    `extent  ${s.x.toFixed(1)} × ${s.y.toFixed(1)} × ${s.z.toFixed(1)} mm\n` +
    `parts   ${[...visible].length} types  ·  ${FINISHES[state.finish].name.toLowerCase()} anodize\n` +
    `version ${manifest.version}` + (mass && state.scene === "leg" ? `  ·  leg ${manifest.parts.leg.mass_g} g` : "");
}

function frame() {
  const box = visibleBox();
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  // fit the sphere to the narrower of the two fields of view; flat parts never fill the whole sphere
  const vfov = THREE.MathUtils.degToRad(camera.fov / 2);
  const hfov = Math.atan(Math.tan(vfov) * camera.aspect);
  const dist = sphere.radius / Math.sin(Math.min(vfov, hfov)) * (state.scene === "leg" ? 1.1 : camera.aspect > 1 ? 0.8 : 0.95);
  const dir = state.scene === "leg" ? new THREE.Vector3(0.9, -1.1, 0.7) : new THREE.Vector3(-0.35, -1.0, 0.95);
  controls.target.copy(sphere.center);
  camera.position.copy(sphere.center).addScaledVector(dir.normalize(), dist);
  camera.near = dist / 100; camera.far = dist * 20;
  camera.updateProjectionMatrix();
  const r = sphere.radius;
  Object.assign(key.shadow.camera, { left: -r * 1.6, right: r * 1.6, top: r * 1.6, bottom: -r * 1.6, near: 1, far: 2000 });
  key.shadow.camera.updateProjectionMatrix();
  key.position.copy(sphere.center).add(new THREE.Vector3(-0.4, -0.6, 1).multiplyScalar(r * 3));
  key.target.position.copy(sphere.center);
  controls.update();
}

// ---------- picking ----------
const ray = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let picked = null;
let pending = null;
function pick(ev) {
  const r = canvas.getBoundingClientRect();
  ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hits = ray.intersectObjects(pickable.filter((m) => m.parent.visible && isShown(m)), false)
    .filter((h) => state.section === 0 || clip.distanceToPoint(h.point) >= 0);
  return hits[0] ? { mesh: hits[0].object, x: ev.clientX - r.left, y: ev.clientY - r.top } : null;
}
function isShown(o) { for (; o; o = o.parent) if (!o.visible) return false; return true; }
function setPicked(hit) {
  if (picked) picked.material = picked.userData.mat;
  picked = hit?.mesh || null;
  const tip = $("tooltip");
  if (!picked) { tip.classList.remove("on"); return; }
  picked.material = highlight;
  const p = manifest.parts[picked.userData.part];
  tip.textContent = `${p.label}\n${p.size.join(" × ")} mm` + (p.mass_g ? `  ·  ${p.mass_g} g` : p.material === "tpu" ? "  ·  TPU" : `  ·  ${p.volume_cm3} cm³, printed`) +
    `\n${p.triangles.toLocaleString()} triangles`;
  tip.style.left = `${hit.x}px`; tip.style.top = `${hit.y}px`;
  tip.classList.add("on");
}
canvas.addEventListener("pointermove", (ev) => {
  if (ev.buttons) return;
  if (!pending) pending = requestAnimationFrame(() => { pending = null; setPicked(pick(ev)); });
});
canvas.addEventListener("pointerleave", () => setPicked(null));

// ---------- UI ----------
for (const [id, f] of Object.entries(FINISHES)) {
  const b = document.createElement("button");
  b.style.background = `#${f.color.toString(16).padStart(6, "0")}`;
  b.title = f.name;
  b.dataset.finish = id;
  b.addEventListener("click", () => { state.finish = id; syncUI(); apply(); });
  $("finishes").append(b);
}
for (const b of $("scenes").querySelectorAll("button")) {
  b.addEventListener("click", () => { state.scene = b.dataset.scene; state.section = 0; syncUI(); build(); });
}
const bindRange = (id, key, num = Number) => $(id).addEventListener("input", (e) => { state[key] = num(e.target.value); apply(); });
bindRange("explode", "explode");
bindRange("section", "section");
bindRange("swing", "swing");
for (const [id, k] of [["tLegs", "legs"], ["tTop", "top"], ["tSpacer", "spacer"], ["tBottom", "bottom"], ["tEdges", "edges"], ["tSpin", "spin"]]) {
  $(id).addEventListener("change", (e) => { state[k] = e.target.checked; apply(); });
}
$("resetView").addEventListener("click", frame);
$("snap").addEventListener("click", () => {
  renderer.render(scene, camera);
  const a = document.createElement("a");
  a.href = renderer.domElement.toDataURL("image/png");
  a.download = `ergodox-${state.scene}-${state.finish}.png`;
  a.click();
});

function syncUI() {
  for (const b of $("scenes").querySelectorAll("button")) b.classList.toggle("on", b.dataset.scene === state.scene);
  for (const b of $("finishes").querySelectorAll("button")) b.classList.toggle("on", b.dataset.finish === state.finish);
  $("section").value = state.section;
  for (const id of ["tTop", "tSpacer", "tBottom"]) $(id).disabled = state.scene === "leg";
}

// parts list under the viewer
$("partlist").innerHTML = names.map((n) => {
  const p = manifest.parts[n];
  return `<a class="part" href="${p.file}" download title="Download ${n}.stl"><b>${p.label}</b>` +
    `<span>${p.size.join(" × ")} mm</span><span>${p.mass_g ? `${p.mass_g} g · 6061` : p.material === "tpu" ? "TPU, 3D-printed" : `${p.volume_cm3} cm³ · print or mill`} · STL ↓</span></a>`;
}).join("");
const halfMass = ["right_top", "right_bottom"].reduce((a, n) => a + manifest.parts[n].mass_g, 0);
$("massStat").textContent = `≈ ${Math.round(halfMass)} g`;

// ---------- loop ----------
function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio()) || canvas.height !== Math.floor(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // on wide screens the control panel covers the right edge: centre the model in the free area
    const panel = w > 760 ? $("panel").offsetWidth + 14 : 0;
    camera.setViewOffset(w, h, panel / 2, 0, w, h);
    camera.updateProjectionMatrix();
  }
}
new ResizeObserver(resize).observe(stage);
syncUI();
resize();
build();
renderer.setAnimationLoop(() => {
  resize();
  controls.update();
  renderer.render(scene, camera);
});
