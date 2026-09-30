import * as THREE from 'three'
import { surf, type SurfHooks } from './materials'
import type { CutState } from './cut'
import type { MaterialSpec } from '../logic/materials'

/**
 * Composite-shop materials, built on surf(). Everything is procedural (no bitmaps).
 *
 * The colours are REPRESENTATIONAL, chosen so a builder can tell the four materials apart at a glance; they are not measured
 * from any product:
 *  - foam: pale off-white, matte, visible cells (a rigid core is a closed-cell foam);
 *  - UND glass: warm straw. BID glass: cooler and greener. Cured E-glass in epoxy is translucent, pale straw to green over
 *    whatever lies under it, and semi-glossy (satin) once cured;
 *  - wet epoxy: the same cloth flooded with resin, darker and more saturated, with a glossy clear coat over the weave;
 *  - flox (brown paste) and micro (pale buff paste): in the palette for later work; nothing uses them yet.
 *
 * Wet epoxy is a dark base plus a MeshPhysicalMaterial clear coat, not true transmission: transmission renders the whole scene
 * a second time into a buffer, which the custom pipeline (MSAA, AO, depth of field) does not expect, and at the op-shot
 * distance a glossy dark laminate reads the same. setWet only changes uniforms and clearcoat values, so it never recompiles
 * (the clear coat is kept above zero when cured so the program stays the same).
 */

// Future work drawn as a ghost: the material is transparent (JS side); this desaturates it.
const GLSL_GHOST_PARS = /* glsl */ `uniform float uGhost;`
const GLSL_GHOST_COLOR = /* glsl */ `{ float gl = dot(diffuseColor.rgb, vec3(0.299, 0.587, 0.114)); diffuseColor.rgb = mix(diffuseColor.rgb, vec3(gl), 0.75 * uGhost); }`

const GLSL_COMPOSITE_PARS = /* glsl */ GLSL_GHOST_PARS + `
uniform float uWet;
uniform vec3 uPly;       // x: model Z of the ply's root end, y: 1 / span length (per inch), z: unused
uniform vec2 uLay;       // x: unrolled fraction of the span (from the root), y: wet-out front, as a fraction of the span
uniform float uWeb;      // 1 when the ply lies in the model Y-Z plane (shear web), 0 when it lies in X-Z (skins, caps)
uniform vec2 uAng;       // cos, sin of the first tow direction, measured from the span axis in the ply's plane
uniform vec4 uWv;        // x: weave period or foam cells per inch, y: relief in inches, z: UND stitch spacing (in)
vec3 h33(vec3 p) {
  p = fract(p * vec3(0.1031, 0.1030, 0.0973));
  p += dot(p, p.yxz + 33.33);
  return fract((p.xxy + p.yxx) * p.zyx);
}
float h11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
// 3D Worley: x = distance to the nearest feature point, y = to the second nearest, z = random id of the nearest cell.
vec3 worley(vec3 p) {
  vec3 ip = floor(p), fp = fract(p);
  float f1 = 8.0, f2 = 8.0, id = 0.0;
  for (int k = -1; k <= 1; k++) for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    vec3 g = vec3(float(i), float(j), float(k));
    vec3 o = h33(ip + g);
    vec3 r = g + o - fp;
    float d = dot(r, r);
    if (d < f1) { f2 = f1; f1 = d; id = o.x; } else if (d < f2) f2 = d;
  }
  return vec3(sqrt(f1), sqrt(f2), id);
}
float towProfile(float f) { return pow(sin(3.14159265 * clamp(f, 0.0, 1.0)), 0.9); }
`

// Surface: relief (surfH is divided by the pixel footprint so the slope is physical), plus shade and roughness for the later hooks.
const GLSL_COMPOSITE_SURFACE = /* glsl */ `
float cmpShade = 1.0, cmpRough = 0.0;
float cmpWetK = 1.0, cmpEdge = 0.0;   // wetness ahead of / at the wet-out front (1 = behind the front, or nothing is being laid)
#if defined(COMP_UND) || defined(COMP_BID)
{
  // Position along the span, 0 at the root end and 1 at the tip. A cut face is measured where the plane opens the ply.
  float sp = (uPly.x - (cutCap ? cutHit.z : vObj.z)) * uPly.y;
  if (uLay.x < 1.0 && sp > uLay.x) discard;   // not unrolled yet
  if (uLay.y < 1.0) {
    // The wet-out front is a soft band about 1.1 in wide, so the front moves from fully dry (uLay.y = 0) to fully wet (1).
    float bw = 0.55 * uPly.y;
    float fr = uLay.y * (1.0 + 2.0 * bw) - bw;
    cmpWetK = 1.0 - smoothstep(fr - bw, fr + bw, sp);
    float ed = (sp - fr) / bw;
    cmpEdge = exp(-ed * ed) * step(0.001, uLay.y);
  }
}
#endif
float cmpWet = uWet * cmpWetK;
float cmpFp = max(max(length(dFdx(vObj)), length(dFdy(vObj))), 1e-5);
float cmpOn = cutCap ? 0.0 : 1.0;
vec3 capW = vec3(0.5, 0.5, 0.5);
float capFade = 1.0;
#if defined(COMP_FOAM)
{
  float cyc = cmpFp * uWv.x;
  float fade = (1.0 - smoothstep(0.18, 0.5, cyc)) * cmpOn;
  if (fade > 0.01) {
    vec3 w = worley(vObj * uWv.x);
    float wall = 1.0 - smoothstep(0.0, 0.2, w.y - w.x);
    cmpShade = 1.0 - fade * (0.16 * wall + 0.1 * (w.z - 0.5));
    cmpRough = fade * (0.1 * wall + 0.12 * (w.z - 0.5));
    surfH += fade * uWv.y * (1.0 - smoothstep(0.0, 0.65, w.x)) / cmpFp;
  }
  if (cutCap) capW = worley(cutHit * uWv.x);
}
#elif defined(COMP_UND) || defined(COMP_BID)
{
  vec2 q = uWeb > 0.5 ? vObj.zy : vObj.zx;
  float A = dot(q, uAng);                    // along the first tow direction
  float B = dot(q, vec2(-uAng.y, uAng.x));   // across it
  float P = uWv.x;
  float cyc = max(fwidth(A), fwidth(B)) / P;
  float fade = (1.0 - smoothstep(0.2, 0.5, cyc)) * cmpOn;
  float soften = 1.0 - 0.6 * cmpWet;           // flooded with resin: the weave relaxes
  #if defined(COMP_UND)
  {
    float ci = floor(B / P), cf = fract(B / P);
    float prof = towProfile(cf);
    float tv = h11(ci + 3.0);
    float fineF = B / (P * 0.14);
    float fine = h11(floor(fineF) + ci * 17.0);
    float fineFade = 1.0 - smoothstep(0.16, 0.42, cyc / 0.14);
    // wider bands of tows (about 1 in) carry a slight tone difference, so the direction still reads when single tows are too small
    float grp = h11(floor(B / (P * 5.0)) + 91.0);
    float grpFade = (1.0 - smoothstep(0.2, 0.5, cyc / 5.0)) * cmpOn;
    float sp = uWv.z;
    float sf = abs(fract(A / sp) * 2.0 - 1.0);
    float sw = 0.045 / sp;                   // stitch thread is ~0.045 in wide
    float band = smoothstep(1.0 - sw * 2.0, 1.0, sf);
    float bandFade = (1.0 - smoothstep(0.3, 0.8, fwidth(A) / 0.045)) * (0.35 + 0.65 * h11(ci + floor(A / sp) * 13.0));
    surfH += (fade * prof * uWv.y * soften - fade * bandFade * band * uWv.y * 0.35 * soften) / cmpFp;
    cmpShade = 1.0 + fade * (-0.14 * (1.0 - prof) * soften + (tv - 0.5) * 0.24 * soften + (fine - 0.5) * 0.16 * fineFade) - bandFade * band * 0.14 + (grp - 0.5) * 0.14 * grpFade * soften;
    cmpRough = fade * (-0.08 * prof + 0.06 * (tv - 0.5));
  }
  #else
  {
    vec2 c = vec2(A, B) / P;
    vec2 ic = floor(c), fc = fract(c);
    float par = mod(ic.x + ic.y, 2.0);
    float warpTop = par < 0.5 ? 1.0 : 0.0;   // warp (running along A) is over where the checker is even, weft elsewhere
    float wp = towProfile(fc.y), wa = pow(sin(3.14159265 * fc.x), 0.4);   // both go to zero at the cell border, so the relief has no jump
    float fw = towProfile(fc.x), fa = pow(sin(3.14159265 * fc.y), 0.4);
    float hh = mix(fw * fa, wp * wa, warpTop);
    float gap = mix(fw, wp, warpTop);
    float tv = h11(mix(ic.x, ic.y, warpTop) * 1.7 + warpTop * 31.0);
    surfH += fade * hh * uWv.y * soften / cmpFp;
    float fineB = h11(floor(mix(c.x, c.y, warpTop) * 9.0) + mix(ic.y, ic.x, warpTop) * 31.0 + warpTop * 7.0);
    float fineFade = 1.0 - smoothstep(0.16, 0.42, cyc * 9.0);
    cmpShade = 1.0 + fade * (-0.1 * (1.0 - gap) * soften + (tv - 0.5) * 0.18 * soften + (warpTop - 0.5) * 0.07 + (fineB - 0.5) * 0.14 * fineFade);
    cmpRough = fade * (-0.07 * hh + 0.05 * (tv - 0.5));
  }
  #endif
  if (cutCap) {
    capW = worley(cutHit * 26.0);
    capFade = 1.0 - smoothstep(0.16, 0.42, max(length(dFdx(cutHit)), length(dFdy(cutHit))) * 26.0);
  }
}
#endif
`

// Dry cloth is bright white, matte, with the weave still showing through cmpShade; resin behind the front turns it the wet colour.
const GLSL_GLASS_COLOR = /* glsl */ `
diffuseColor.rgb *= cmpShade;
// wet resin: darker and less saturated (the cloth goes translucent), with epoxy's faint amber cast
vec3 cmpWc = mix(vec3(dot(diffuseColor.rgb, vec3(0.3, 0.59, 0.11))), diffuseColor.rgb, 0.55) * vec3(0.8, 0.77, 0.66);
diffuseColor.rgb = mix(diffuseColor.rgb, cmpWc, cmpWet);
diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.89, 0.89, 0.86) * (0.5 + 0.5 * cmpShade), (1.0 - cmpWetK) * 0.94);
` + GLSL_GHOST_COLOR

// Behind the front the resin is glossy, and the leading edge, where the squeegee pushes resin ahead of it, is glossier still. Dry cloth has no gloss.
const GLSL_GLASS_LIGHTS = /* glsl */ `
#ifdef USE_CLEARCOAT
material.clearcoat = clamp(material.clearcoat * cmpWetK + cmpEdge * 0.55 * uWet, 0.0, 1.0);
material.clearcoatRoughness = mix(material.clearcoatRoughness, 0.12, cmpEdge);
#endif
`

const HOOKS_FOAM: SurfHooks = {
  defs: ['COMP_FOAM'],
  pars: GLSL_COMPOSITE_PARS,
  surface: GLSL_COMPOSITE_SURFACE,
  color: 'diffuseColor.rgb *= cmpShade;\n' + GLSL_GHOST_COLOR,
  rough: 'roughnessFactor = clamp(roughnessFactor + cmpRough, 0.05, 1.0);',
  // cut face: the same cell function on the cut point, so the section shows the cells
  capColor: `if (cutCap) { float wall = 1.0 - smoothstep(0.0, 0.2, capW.y - capW.x); diffuseColor.rgb = uCapColor * (1.0 - 0.34 * wall + (capW.z - 0.5) * 0.18); }`,
  capRough: 'if (cutCap) roughnessFactor = clamp(0.88 + (capW.z - 0.5) * 0.1, 0.05, 1.0);',
  bump: true,
}
const glassHooks = (kind: 'COMP_UND' | 'COMP_BID'): SurfHooks => ({
  defs: [kind],
  pars: GLSL_COMPOSITE_PARS,
  surface: GLSL_COMPOSITE_SURFACE,
  color: GLSL_GLASS_COLOR,
  lights: GLSL_GLASS_LIGHTS,
  rough: 'roughnessFactor = clamp(roughnessFactor + cmpRough - cmpWet * 0.12 + (1.0 - cmpWetK) * 0.38, 0.05, 1.0);',
  // a laminate edge: pale fibre bundles (dots) in a darker resin matrix
  capColor: `if (cutCap) { float dots = 1.0 - smoothstep(0.12, 0.4, capW.x); diffuseColor.rgb = uCapColor * mix(1.0, 0.7 + 0.5 * dots + (capW.z - 0.5) * 0.15, capFade); }`,
  capRough: 'if (cutCap) roughnessFactor = clamp(0.5 + (capW.z - 0.5) * 0.12, 0.05, 1.0);',
  bump: true,
})

/** Representational colours (see the header). */
export const COLORS = {
  foam: 0xd6d0c0,
  foamCap: 0xeee8d8,
  und: 0xa88f52,
  undCap: 0x9a8047,
  bid: 0x6f8f79,
  bidCap: 0x62806c,
  flox: 0x8c6a44,
  micro: 0xdccca4,
}

export interface Weave { web: 0 | 1 }

/**
 * Which model plane a ply lies in, from the area-weighted absolute normals of its geometry (model inches, as merged).
 * A dominant X normal means a plane in Y-Z (the shear web); otherwise the ply lies roughly in X-Z (skins, spar caps).
 */
export function plyPlane(geo: THREE.BufferGeometry): 0 | 1 {
  const pos = geo.attributes.position
  const idx = geo.index
  const n = idx ? idx.count : pos.count
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), e1 = new THREE.Vector3(), e2 = new THREE.Vector3()
  let sx = 0, sy = 0
  for (let i = 0; i < n; i += 3) {
    const ia = idx ? idx.getX(i) : i, ib = idx ? idx.getX(i + 1) : i + 1, ic = idx ? idx.getX(i + 2) : i + 2
    a.fromBufferAttribute(pos, ia); b.fromBufferAttribute(pos, ib); c.fromBufferAttribute(pos, ic)
    e1.subVectors(b, a); e2.subVectors(c, a)
    const nv = e1.cross(e2)
    sx += Math.abs(nv.x); sy += Math.abs(nv.y)
  }
  return sx > sy ? 1 : 0
}

/** A ply runs along the model Z axis: it starts at its root end (the larger Z, B.L. 0 side) and ends at its tip. Model inches. */
export interface PlySpan { rootZ: number; len: number }
export function plySpan(geo: THREE.BufferGeometry): PlySpan {
  geo.computeBoundingBox()
  const b = geo.boundingBox!
  return { rootZ: b.max.z, len: b.max.z - b.min.z }
}

export interface CompositeInfo { kind: MaterialSpec['kind']; angles: number[]; wet: number }

/** One material per mesh. `web` says the ply lies in the model Y-Z plane (use plyPlane on its geometry). */
export function compositeMaterial(spec: MaterialSpec, cut: CutState | null, web: 0 | 1 = 0, span: PlySpan = { rootZ: 0, len: 1 }): THREE.MeshStandardMaterial {
  const common = { metalness: 0, cut, detail: 0 }
  let m: THREE.MeshStandardMaterial
  if (spec.kind === 'foam') {
    m = surf({
      ...common, name: 'foam', color: COLORS.foam, roughness: 0.86, capColor: COLORS.foamCap, capRoughness: 0.88, capMetalness: 0,
      hooks: { ...HOOKS_FOAM, uniforms: { uWet: { value: 0 }, uGhost: { value: 0 }, uWeb: { value: 0 }, uAng: { value: new THREE.Vector2(1, 0) }, uWv: { value: new THREE.Vector4(6, 0.015, 1, 0) } } },
    })
  } else if (spec.kind === 'und' || spec.kind === 'bid') {
    const und = spec.kind === 'und'
    const th = THREE.MathUtils.degToRad(spec.angles[0] ?? 0)
    m = surf({
      ...common, name: spec.ply?.node ?? spec.kind, color: und ? COLORS.und : COLORS.bid, roughness: 0.42, capColor: und ? COLORS.undCap : COLORS.bidCap,
      capRoughness: 0.5, capMetalness: 0,
      // Cured is satin over a light clear coat; setWet raises the clear coat to full and drops its roughness. The clear coat
      // stays above zero when cured so the program never changes.
      clearcoat: 0.12, clearcoatRoughness: 0.45,
      hooks: {
        ...glassHooks(und ? 'COMP_UND' : 'COMP_BID'),
        uniforms: { uWet: { value: 0 }, uGhost: { value: 0 }, uPly: { value: new THREE.Vector3(span.rootZ, 1 / Math.max(span.len, 1e-3), 0) }, uLay: { value: new THREE.Vector2(1, 1) }, uWeb: { value: web }, uAng: { value: new THREE.Vector2(Math.cos(th), Math.sin(th)) }, uWv: { value: new THREE.Vector4(und ? 0.24 : 0.18, und ? 0.012 : 0.008, 1, 0) } },
      },
    })
  } else {
    throw new Error(`compositeMaterial: "${spec.kind}" is not a composite kind`)
  }
  m.userData.comp = { kind: spec.kind, angles: spec.angles.slice(), wet: 0 } satisfies CompositeInfo
  return m
}

/** 0 = cured, 1 = wet. Uniform and clear-coat values only, so it is cheap to call every frame and never recompiles. */
export function setWet(m: THREE.Material, w: number) {
  const info = m.userData.comp as CompositeInfo | undefined
  if (!info || info.kind === 'foam') return
  const v = THREE.MathUtils.clamp(w, 0, 1)
  info.wet = v
  const u = m.userData.u as { uWet: { value: number } }
  u.uWet.value = v
  const p = m as THREE.MeshPhysicalMaterial
  p.clearcoat = 0.12 + 0.88 * v
  p.clearcoatRoughness = 0.45 - 0.41 * v
  p.roughness = 0.42 - 0.17 * v
  const back = m.userData.back as THREE.Material | undefined
  if (back) back.userData.u.uWet.value = v
}

/** How far along its lay-down a ply is: `unroll` and `front` are fractions of the span, `cure` is 0 wet to 1 cured, `ghost` draws it as future work. */
export interface PlyLook { unroll: number; front: number; cure: number; ghost: boolean }

/** Uniform and material values only: cheap every frame. The one thing that recompiles is the transparent flag, and only when it flips. */
export function setPlyLook(m: THREE.Material, look: PlyLook) {
  const u = m.userData.u as Record<string, { value: unknown }> | undefined
  if (!u) return
  setWet(m, 1 - look.cure)
  const set = (mat: THREE.Material) => {
    const uu = mat.userData.u as Record<string, { value: unknown }>
    ;(uu.uGhost as { value: number }).value = look.ghost ? 1 : 0
    if (uu.uLay) (uu.uLay.value as THREE.Vector2).set(look.unroll, look.front)
    if (mat.transparent !== look.ghost) { mat.transparent = look.ghost; mat.needsUpdate = true }
    mat.opacity = look.ghost ? 0.2 : 1
    mat.depthWrite = !look.ghost
  }
  set(m)
  const back = m.userData.back as THREE.Material | undefined
  if (back) set(back)
}

/** A matte non-composite part (no plies). Same ghost handling as the composites. */
export function partMaterial(cut: CutState | null): THREE.MeshStandardMaterial {
  const m = surf({
    name: 'part', color: 0xe6dfcf, roughness: 0.85, metalness: 0, detail: 1.2, colorVar: 0.06, roughVar: 0.2, cut, capColor: 0xe6dfcf,
    hooks: { pars: GLSL_GHOST_PARS, color: GLSL_GHOST_COLOR, uniforms: { uGhost: { value: 0 } } },
  })
  return m
}

/** Paste materials for later work (bonding cores, filling dings). Nothing in the scene uses them yet. */
export function floxMaterial(cut: CutState | null): THREE.MeshStandardMaterial {
  return surf({ name: 'flox', color: COLORS.flox, metalness: 0, roughness: 0.9, detail: 5, bump: 0.05, colorVar: 0.16, roughVar: 0.15, cut, capColor: COLORS.flox })
}
export function microMaterial(cut: CutState | null): THREE.MeshStandardMaterial {
  return surf({ name: 'micro', color: COLORS.micro, metalness: 0, roughness: 0.82, detail: 3, bump: 0.03, colorVar: 0.08, roughVar: 0.12, cut, capColor: COLORS.micro })
}
