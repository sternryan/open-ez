// Adapted from AirsupHQ/airsup-lab src/core/materials.ts (MIT); see NOTICE.
// Changes: added SurfOpts.hooks (extra GLSL injected at fixed points, extra uniforms and defines, including one after lights_physical_fragment) for the composite-shop materials in composite.ts; behaviour without hooks is unchanged. The cap pass gets a polygon offset so a cap wins over the coincident face of the neighbouring layer. Added the SURF_CHEAP variant (flat lighting, no detail noise or bump) for the low quality tier.
import * as THREE from 'three'
import { CutState, CUT_PROJ, NO_CUT, GLSL_CUT_FRAG, GLSL_CUT_FRAG_PARS, GLSL_CUT_VERT, GLSL_CUT_VERT_PARS } from './cut'
import { GLSL_NOISE, NOISE3D } from './noise'

export interface SurfOpts {
  color: number | string
  metalness?: number
  roughness?: number
  /** World scale of the detail noise (cycles per object unit). */
  detail?: number
  roughVar?: number
  colorVar?: number
  bump?: number
  /** 3D printed layer lines along the object Y axis: [frequency, height]. */
  layers?: [number, number]
  /** Brushed / turned finish. */
  anisotropy?: number
  anisotropyRotation?: number
  clearcoat?: number
  clearcoatRoughness?: number
  /** Heat tint along object Y: colours from y0 to y1. */
  tint?: { y0: number; y1: number; a: number | string; b: number | string; c: number | string; strength: number }
  /** Regen channel ribbing around the Y axis: [count, depth]. */
  ribs?: [number, number]
  /** Vertical streaks (soot and drips), strength. */
  streaks?: number
  emissive?: number | string
  emissiveIntensity?: number
  envMapIntensity?: number
  cut?: CutState | null
  capColor?: number | string
  capRoughness?: number
  capMetalness?: number
  side?: THREE.Side
  transparent?: boolean
  opacity?: number
  sheen?: number
  sheenColor?: number | string
  flatShading?: boolean
  vertexColors?: boolean
  map?: THREE.Texture | null
  roughnessMap?: THREE.Texture | null
  name?: string
  /** Extra GLSL for callers that need their own surface model (see composite.ts). All fields optional. */
  hooks?: SurfHooks
  /** internal: build the back face cap pass of a cut material */
  capPass?: boolean
}

/**
 * Injection points in the fragment shader. `pars` sits with the other declarations; `surface` runs after the detail noise
 * (it may add to surfH and declare locals for the later hooks); `color` runs before the cap colour is applied, `capColor`
 * after it; `rough` runs before the cap roughness is applied, `capRough` after it.
 */
export interface SurfHooks {
  defs?: string[]
  pars?: string
  surface?: string
  color?: string
  capColor?: string
  rough?: string
  capRough?: string
  /** runs right after the physical material is set up (clearcoat and friends live in `material`) */
  lights?: string
  uniforms?: Record<string, { value: unknown }>
  /** the hooks add height, so switch the bump on */
  bump?: boolean
}

/**
 * The elevators' cove (logic/cove.ts is the same maths in TypeScript, under test). A material that opts in (markCove) discards what lies
 * aft of uCove.x within |z| < uCove.y of its own model frame, and its cap pass closes the wall that leaves: a back face seen through the
 * removed box is a cap where the ray left the box before reaching it (the section cut's trick, with a three-sided box in place of its planes).
 * The wall is a fitted shape, so it carries the same amber stripes as the other fitted shapes.
 */
const GLSL_COVE_PARS = /* glsl */ `
uniform vec4 uCove;
uniform float uCoveMat;
varying vec3 vCoveX;
varying vec3 vCoveZ;
// keep the part of the ray inside the half space n.p + c > 0; exitId is which space the ray leaves the removed box through
void coveClip(vec3 n, float c, vec3 ro, vec3 rd, inout float t0, inout float t1, inout int exitId, int id) {
  float dn = dot(n, rd);
  float d0 = dot(n, ro) + c;
  if (abs(dn) < 1e-9) { if (d0 <= 0.0) { t0 = 1.0; t1 = 0.0; } return; }
  float th = -d0 / dn;
  if (dn < 0.0) { if (th < t1) { t1 = th; exitId = id; } }
  else t0 = max(t0, th);
}
`
const GLSL_COVE = /* glsl */ `
bool coveCap = false;
if (uCoveMat > 0.5 && uCove.z > 0.5) {
  if (vObj.x > uCove.x && abs(vObj.z) < uCove.y) discard;
  #ifdef CAPS
  {
    #ifdef FLIP_SIDED
      bool coveBack = gl_FrontFacing;
    #else
      bool coveBack = !gl_FrontFacing;
    #endif
    if (coveBack && !cutCap) {
      vec3 ro = vCutObjCam;
      vec3 toF = vObj - ro;
      float tf = length(toF);
      vec3 rd = toF / max(tf, 1e-6);
      float t0 = 0.0, t1 = 1e9;
      int exitId = -1;
      coveClip(vec3(1.0, 0.0, 0.0), -uCove.x, ro, rd, t0, t1, exitId, 0);
      coveClip(vec3(0.0, 0.0, 1.0), uCove.y, ro, rd, t0, t1, exitId, 1);
      coveClip(vec3(0.0, 0.0, -1.0), uCove.y, ro, rd, t0, t1, exitId, 2);
      if (exitId >= 0 && t0 < t1 && t1 > 0.0 && t1 < tf) {
        coveCap = true;
        cutCap = true;
        cutHit = ro + rd * t1;
        // the wall faces into the removed box: +x at the cut, and the two span ends of the box face each other
        cutNW = -normalize(exitId == 0 ? vCoveX : exitId == 1 ? vCoveZ : -vCoveZ);
      }
    }
  }
  #endif
}
`

/** Make a canard material follow its CutState's cove (the cove opens and closes with CutState.setCove). */
export function markCove(m: THREE.Material) {
  const u = m.userData.u as { uCoveMat: { value: number } } | undefined
  if (u) u.uCoveMat.value = 1
}

/** The shadow map's version of the cove: a mesh with the cove's discard also casts no shadow where the cove is open. */
export function coveDepthMaterial(cut: CutState): THREE.MeshDepthMaterial {
  const m = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking })
  m.onBeforeCompile = (shader) => {
    shader.uniforms.uCove = cut.uCove
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vCoveP;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvCoveP = transformed;')
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform vec4 uCove;\nvarying vec3 vCoveP;')
      .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\nif (uCove.z > 0.5 && vCoveP.x > uCove.x && abs(vCoveP.z) < uCove.y) discard;')
  }
  m.customProgramCacheKey = () => 'cove-depth'
  return m
}

const GLSL_BUMP = /* glsl */ `
vec3 surfPerturb(vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDir) {
  vec3 vSigmaX = normalize(dFdx(surf_pos.xyz));
  vec3 vSigmaY = normalize(dFdy(surf_pos.xyz));
  vec3 vN = surf_norm;
  vec3 R1 = cross(vSigmaY, vN);
  vec3 R2 = cross(vN, vSigmaX);
  float fDet = dot(vSigmaX, R1) * faceDir;
  vec3 vGrad = sign(fDet) * (dHdxy.x * R1 + dHdxy.y * R2);
  return normalize(abs(fDet) * surf_norm - vGrad);
}
`

/**
 * The low quality tier's shader switch. While `on`, every surf() material is built with SURF_CHEAP (the composite weave and foam
 * cells drop to their albedo-only variant, the noise detail and bump perturbation are skipped everywhere, the room's included). setCheapShaders flips the ones that already exist,
 * including each cut material's lazily made cap pass, and recompiles them.
 */
export const CHEAP = { on: false }
// The flat light of the low tier, as GLSL literals: a warm key from the overhead fixture side, and a sky/ground ambient.
const CHEAP_KEY_DIR = '-0.42, 0.86, 0.29'
const CHEAP_KEY = '1.05, 0.9, 0.7'
const CHEAP_SKY = '0.5, 0.53, 0.62'
const CHEAP_GROUND = '0.22, 0.19, 0.16'
export function setCheapShaders(root: THREE.Object3D, on: boolean) {
  CHEAP.on = on
  const flip = (m: THREE.Material | undefined) => {
    if (!m) return
    if (!m.userData.u) return // only surf() materials carry the variant
    const had = m.defines?.SURF_CHEAP === 1
    if (had === on) return
    m.defines = { ...(m.defines ?? {}) }
    if (on) m.defines.SURF_CHEAP = 1
    else delete m.defines.SURF_CHEAP
    m.needsUpdate = true
  }
  root.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) return
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material]
    for (const m of mats) { flip(m); flip(m.userData.back as THREE.Material | undefined) }
    const front = mesh.userData.front as THREE.Material | undefined
    flip(front); flip(front?.userData.back as THREE.Material | undefined)
  })
}

/**
 * PBR surface with procedural wear (roughness breakup, colour variation,
 * micro bump, print layers, heat tint) and optional section cut.
 */
export function surf(o: SurfOpts): THREE.MeshStandardMaterial {
  const physical = (o.clearcoat ?? 0) > 0 || (o.sheen ?? 0) > 0 || (o.anisotropy ?? 0) > 0
  const base = {
    color: new THREE.Color(o.color as THREE.ColorRepresentation),
    metalness: o.metalness ?? 1,
    roughness: o.roughness ?? 0.4,
    envMapIntensity: o.envMapIntensity ?? 1,
    transparent: o.transparent ?? false,
    opacity: o.opacity ?? 1,
    flatShading: o.flatShading ?? false,
    vertexColors: o.vertexColors ?? false,
    map: o.map ?? null,
    roughnessMap: o.roughnessMap ?? null,
  }
  const m: THREE.MeshStandardMaterial = physical ? new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(o.color as THREE.ColorRepresentation),
    metalness: o.metalness ?? 1,
    roughness: o.roughness ?? 0.4,
    envMapIntensity: o.envMapIntensity ?? 1,
    clearcoat: o.clearcoat ?? 0,
    clearcoatRoughness: o.clearcoatRoughness ?? 0.1,
    anisotropy: o.anisotropy ?? 0,
    anisotropyRotation: o.anisotropyRotation ?? 0,
    transparent: o.transparent ?? false,
    opacity: o.opacity ?? 1,
    flatShading: o.flatShading ?? false,
    vertexColors: o.vertexColors ?? false,
    map: o.map ?? null,
    roughnessMap: o.roughnessMap ?? null,
    sheen: o.sheen ?? 0,
    sheenColor: new THREE.Color((o.sheenColor ?? 0xffffff) as THREE.ColorRepresentation),
  }) : new THREE.MeshStandardMaterial(base)
  if (o.name) m.name = o.name
  if (o.emissive !== undefined) {
    m.emissive = new THREE.Color(o.emissive as THREE.ColorRepresentation)
    m.emissiveIntensity = o.emissiveIntensity ?? 1
  }
  const cut = o.cut ?? null
  const capPass = !!o.capPass
  if (cut) {
    // front faces always draw single sided with early depth rejection; the cut
    // faces come from a separate back face pass that discards everything else
    m.side = capPass ? THREE.BackSide : THREE.FrontSide
    if (capPass) { m.polygonOffset = true; m.polygonOffsetFactor = -2; m.polygonOffsetUnits = -2 } // nested solids: a cap wins over the coincident face of the layer it lies against
    m.userData.caps = capPass
    m.clippingPlanes = cut.planes
    m.clipIntersection = cut.intersect
    m.clipShadows = true
    if (!capPass) {
      cut.materials.add(m)
      m.userData.makeBack = () => surf({ ...o, capPass: true, name: (o.name ?? 'surf') + ':caps' })
    }
  } else if (o.side !== undefined) m.side = o.side

  if (CHEAP.on) m.defines = { ...(m.defines ?? {}), SURF_CHEAP: 1 }
  const detail = o.detail ?? 0
  const u = {
    uCutPlane: cut ? cut.uPlane : NO_CUT.uPlane,
    uCutPlane2: cut ? cut.uPlane2 : NO_CUT.uPlane2,
    uCutGlow: cut ? cut.uGlow : NO_CUT.uGlow,
    uCove: cut ? cut.uCove : NO_CUT.uCove,
    uCoveMat: { value: 0 },
    uCutProj: CUT_PROJ,
    uCapColor: { value: new THREE.Color((o.capColor ?? 0xc9ccd1) as THREE.ColorRepresentation) },
    uCapRough: { value: o.capRoughness ?? 0.42 },
    uCapMetal: { value: o.capMetalness ?? 0.35 },
    uDetail: { value: new THREE.Vector4(detail, o.roughVar ?? 0.35, o.colorVar ?? 0.12, o.bump ?? 0) },
    uLayers: { value: new THREE.Vector2(o.layers?.[0] ?? 0, o.layers?.[1] ?? 0) },
    uRibs: { value: new THREE.Vector2(o.ribs?.[0] ?? 0, o.ribs?.[1] ?? 0) },
    uStreaks: { value: o.streaks ?? 0 },
    uTintA: { value: new THREE.Color((o.tint?.a ?? 0) as THREE.ColorRepresentation) },
    uTintB: { value: new THREE.Color((o.tint?.b ?? 0) as THREE.ColorRepresentation) },
    uTintC: { value: new THREE.Color((o.tint?.c ?? 0) as THREE.ColorRepresentation) },
    uTintRange: { value: new THREE.Vector3(o.tint?.y0 ?? 0, o.tint?.y1 ?? 1, o.tint?.strength ?? 0) },
    uNoise3D: NOISE3D,
  }
  const hk = o.hooks ?? {}
  if (hk.uniforms) Object.assign(u, hk.uniforms)
  m.userData.u = u
  const defs: string[] = [...(hk.defs ?? []).map((d) => `#define ${d}`)]
  if (cut) defs.push('#define SURF_CUT')
  if (detail > 0) defs.push('#define SURF_DETAIL')
  if (o.tint) defs.push('#define SURF_TINT')
  if ((o.streaks ?? 0) > 0) defs.push('#define SURF_STREAKS')
  if (hk.bump || (o.bump ?? 0) > 0 || (o.layers?.[1] ?? 0) > 0 || (o.ribs?.[1] ?? 0) > 0) defs.push('#define SURF_BUMP')
  const defStr = defs.join('\n') + '\n'

  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, u)
    const capsDef = capPass ? '#define CAPS\n#define CAP_ONLY\n' : ''
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', `#include <common>\n${GLSL_CUT_VERT_PARS}\nvarying vec3 vCoveX;\nvarying vec3 vCoveZ;`)
      .replace('#include <project_vertex>', `#include <project_vertex>\n${GLSL_CUT_VERT}\nvCoveX = mat3(modelMatrix) * vec3(1.0, 0.0, 0.0);\nvCoveZ = mat3(modelMatrix) * vec3(0.0, 0.0, 1.0);`)

    let f = shader.fragmentShader
    f = f.replace(
      '#include <common>',
      `${defStr}#ifdef SURF_CHEAP
#undef SURF_DETAIL
#undef SURF_STREAKS
#endif
${capsDef}#include <common>
${GLSL_CUT_FRAG_PARS}
${GLSL_COVE_PARS}
${GLSL_NOISE}
${GLSL_BUMP}
uniform vec3 uCapColor; uniform float uCapRough; uniform float uCapMetal;
uniform vec4 uDetail; uniform vec2 uLayers; uniform vec2 uRibs; uniform float uStreaks;
uniform vec3 uTintA; uniform vec3 uTintB; uniform vec3 uTintC; uniform vec3 uTintRange;
${hk.pars ?? ''}
`,
    )
    f = f.replace(
      '#include <clipping_planes_fragment>',
      `#include <clipping_planes_fragment>
#ifdef SURF_CUT
${GLSL_CUT_FRAG}
${GLSL_COVE}
#ifdef CAP_ONLY
if (!cutCap) discard;
#endif
#else
bool cutCap = false; vec3 cutHit = vObj; vec3 cutNW = uCutPlane.xyz; bool coveCap = false;
#endif
float surfN1 = 0.5, surfN2 = 0.5, surfH = 0.0;
#ifdef SURF_DETAIL
{
  vec3 dp = vObj * uDetail.x;
  surfN1 = fbm2(dp);
  surfN2 = n3(dp * 3.3 + vec3(7.3, 1.1, 3.7));
  surfH = (surfN1 - 0.5) * uDetail.w;
  #ifdef SURF_STREAKS
    float st = n3(vec3(vObj.x * uDetail.x * 2.2, vObj.y * uDetail.x * 0.18, vObj.z * uDetail.x * 2.2));
    surfN1 = mix(surfN1, st, 0.55);
  #endif
}
#endif
if (uLayers.y > 0.0) surfH += sin(vObj.y * uLayers.x) * uLayers.y;
if (uRibs.y > 0.0) surfH += smoothstep(-0.2, 0.9, sin(atan(vObj.z, vObj.x) * uRibs.x)) * uRibs.y;
${hk.surface ?? ''}
`,
    )
    f = f.replace(
      '#include <color_fragment>',
      `#include <color_fragment>
#ifdef SURF_DETAIL
  diffuseColor.rgb *= 1.0 + (surfN1 - 0.5) * uDetail.z * 2.0;
#endif
#ifdef SURF_TINT
{
  float ty = clamp((vObj.y - uTintRange.x) / (uTintRange.y - uTintRange.x), 0.0, 1.0);
  ty = clamp(ty + (surfN2 - 0.5) * 0.18, 0.0, 1.0);
  vec3 tc = ty < 0.5 ? mix(uTintA, uTintB, ty * 2.0) : mix(uTintB, uTintC, ty * 2.0 - 1.0);
  diffuseColor.rgb = mix(diffuseColor.rgb, tc, uTintRange.z);
}
#endif
#ifdef SURF_STREAKS
  diffuseColor.rgb *= 1.0 - uStreaks * smoothstep(0.45, 0.8, surfN1);
#endif
${hk.color ?? ''}
if (cutCap) diffuseColor.rgb = uCapColor;
${hk.capColor ?? ''}
if (coveCap) {
  float hs = (cutHit.x + cutHit.y - cutHit.z) / 1.6;
  float tri = abs(fract(hs) - 0.5) * 2.0;
  float aa = clamp(fwidth(hs) * 2.0, 1e-4, 0.5);
  diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.80, 0.40, 0.08), 0.7 * smoothstep(0.52 - aa, 0.52 + aa, tri) * (1.0 - 0.6 * aa * 2.0));
}
`,
    )
    f = f.replace(
      '#include <metalnessmap_fragment>',
      `#include <metalnessmap_fragment>
#ifdef SURF_DETAIL
  roughnessFactor = clamp(roughnessFactor * (1.0 + (surfN2 - 0.5) * uDetail.y * 2.0), 0.03, 1.0);
#endif
${hk.rough ?? ''}
if (cutCap) {
  roughnessFactor = uCapRough + (n3(cutHit * 9.0) - 0.5) * 0.08;
  metalnessFactor = uCapMetal;
}
${hk.capRough ?? ''}
`,
    )
    f = f.replace(
      '#include <normal_fragment_maps>',
      `#include <normal_fragment_maps>
#if defined(SURF_BUMP) && !defined(SURF_CHEAP)
  if (!cutCap) normal = surfPerturb(-vViewPosition, normal, vec2(dFdx(surfH), dFdy(surfH)), faceDirection);
#endif
{
  // specular anti-aliasing: widen the lobe where the normal changes quickly across a pixel
  vec3 dn = fwidth(normal);
  float variance = dot(dn, dn);
  roughnessFactor = sqrt(clamp(roughnessFactor * roughnessFactor + min(variance * 0.6, 0.16), 0.0, 1.0));
}
if (cutCap) {
  normal = normalize((viewMatrix * vec4(-cutNW, 0.0)).xyz);
  nonPerturbedNormal = normal;
}
`,
    )
    f = f.replace(
      '#include <emissivemap_fragment>',
      `#include <emissivemap_fragment>
#if defined(SURF_CUT) && !defined(CAP_ONLY)
if (uCutGlow > 0.0) {
  float cdw = dot(vCutPlaneObj.xyz, vObj) + vCutPlaneObj.w;
  float cdw2 = dot(vCutPlane2Obj.xyz, vObj) + vCutPlane2Obj.w;
  float cde = uCutPlane2.w < 0.0 && dot(uCutPlane2.xyz, uCutPlane2.xyz) < 0.5 ? abs(cdw) : max(cdw, cdw2) < 0.0 ? 1.0 : min(abs(cdw), abs(cdw2));
  totalEmissiveRadiance += vec3(0.45, 0.85, 1.0) * exp(-cde * 900.0) * uCutGlow * 14.0;
}
#endif
`,
    )
    // Low tier (SURF_CHEAP): no light loop, no shadows, no image-based light. The surface is lit by one baked key direction and a sky/ground
    // gradient, which costs a few multiplies per pixel instead of the full physically based light model.
    f = f.replace('#include <lights_fragment_begin>', `#ifdef SURF_CHEAP
vec3 geometryViewDir = normalize(vViewPosition);
vec3 geometryClearcoatNormal = vec3(0.0);
{
  float cheapUp = dot(normal, normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)) * 0.5 + 0.5;
  float cheapNL = max(dot(normal, normalize((viewMatrix * vec4(${CHEAP_KEY_DIR}, 0.0)).xyz)), 0.0);
  reflectedLight.indirectDiffuse += material.diffuseColor * mix(vec3(${CHEAP_GROUND}), vec3(${CHEAP_SKY}), cheapUp);
  reflectedLight.directDiffuse += material.diffuseColor * vec3(${CHEAP_KEY}) * cheapNL;
}
#else
#include <lights_fragment_begin>
#endif`)
    f = f.replace('#include <lights_fragment_maps>', '#ifndef SURF_CHEAP\n#include <lights_fragment_maps>\n#endif')
    f = f.replace('#include <lights_fragment_end>', '#ifndef SURF_CHEAP\n#include <lights_fragment_end>\n#endif')
    if (hk.lights) f = f.replace('#include <lights_physical_fragment>', `#include <lights_physical_fragment>\n${hk.lights}`)
    shader.fragmentShader = f
  }
  m.customProgramCacheKey = () => 'surf|' + defStr + (hk.pars ? hk.pars.length : '') + (capPass ? 'caps' : '')
  return m
}

/** A matte material for room surfaces (never cut, cheap). */
export function matte(color: number | string, roughness = 0.8, extra: Partial<SurfOpts> = {}) {
  return surf({ color, metalness: 0, roughness, detail: extra.detail ?? 0, ...extra })
}
