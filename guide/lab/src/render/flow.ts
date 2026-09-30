// Adapted from AirsupHQ/airsup-lab src/fusion/plasma.ts (MIT); see NOTICE.
// Changes: glowLineMaterial only, drawn on a camera-facing ribbon (ours: flowRibbon) instead of a GL line, with a hot core and a soft coloured halo across it and comet-shaped pulses along it; premultiplied blend (light added, the surface under the halo dimmed); time is our own GLOW_TIME (set from step(dt)); depthTest off so a flow inside the laminate still shows.
import * as THREE from 'three'
import type { CutState } from '../core/cut'

/** Seconds of sim time; main.ts sets it from step(dt), so a recorded frame is reproducible. */
export const GLOW_TIME = { value: 0 }
/** Drawing-buffer height in pixels; main.ts keeps it current, so the ribbon's width can be held between a minimum and a maximum on screen. */
export const GLOW_VIEW_H = { value: 1080 }

// The ribbon is built in view space: every centre point is pushed sideways, across its tangent and the view direction, by the
// half-width. The half-width is a world size held between uPx.x and uPx.y pixels, so a flow stays a visible thread in a wide shot
// and does not become a fat bar in a close-up.
const LINE_VERT = /* glsl */ `
#include <common>
#include <clipping_planes_pars_vertex>
attribute float aS;
attribute float aSide;
attribute float aLen;
attribute vec3 aTan;
uniform float uHalfW;   // half-width, world units (metres)
uniform vec2 uPx;       // min, max half-width in drawing-buffer pixels
uniform float uViewH;
varying float vS;
varying float vX;
varying float vLen;
void main() {
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vec3 t = normalize((modelViewMatrix * vec4(aTan, 0.0)).xyz);
  vec3 v = normalize(-mvPosition.xyz);
  vec3 side = cross(t, v);
  float sl = length(side);
  side = sl > 1e-4 ? side / sl : vec3(1.0, 0.0, 0.0);
  float px = max(-mvPosition.z, 1e-4) * 2.0 / (projectionMatrix[1][1] * uViewH);   // world size of one pixel at this depth
  float hw = clamp(uHalfW, uPx.x * px, uPx.y * px);
  mvPosition.xyz += side * hw * aSide;
  gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
  vS = aS;
  vX = aSide;
  vLen = aLen;
}
`
const LINE_FRAG = /* glsl */ `
#include <common>
#include <clipping_planes_pars_fragment>
varying float vS;
varying float vX;
varying float vLen;
uniform vec3 uColor;
uniform float uTime, uSpeed, uScale, uEmph, uBase, uRate, uPulse, uCore, uHalo, uHot, uDim;
void main() {
  #include <clipping_planes_fragment>
  float x2 = vX * vX;
  float core = exp(-x2 * 30.0);                               // the hot thread
  float halo = exp(-x2 * 3.2) * (1.0 - x2);                   // the coloured glow around it, zero at the ribbon's edge
  // comet pulses: a sharp bright head leading, a tail fading behind it, so the direction reads in a still
  float f = fract(vS / uScale - uTime * uSpeed * uRate);
  const float HEAD = 0.92;
  float pulse = f < HEAD ? pow(f / HEAD, 4.0) : 1.0 - smoothstep(HEAD, 1.0, f);
  float I = uBase + pulse * uPulse;
  float ends = smoothstep(0.0, 0.6, vS) * smoothstep(0.0, 0.6, vLen - vS);   // the thread fades in and out at its ends (inches)
  vec3 c = uColor * (core * uCore + halo * uHalo) * I + vec3(core * pulse * uHot);
  // premultiplied: the light is added, and the surface under the halo is dimmed by alpha, so the colour stays saturated on a pale laminate
  // the shadow is wider and flatter than the light, so there is a band where the surface is dark and the colour is not yet clipped
  float shade = exp(-x2 * 1.2) * (1.0 - x2 * x2);
  gl_FragColor = vec4(c * uEmph * ends, clamp(uDim * shade * ends * uEmph, 0.0, 1.0));
}
`

export interface GlowLineOpts {
  color: THREE.ColorRepresentation
  emph: { value: number }
  rate?: { value: number }
  /** pulses per second passing a point, travelling in the direction of increasing arc length */
  speed?: number
  /** the pulse period along the line, in the geometry's own units */
  scale?: number
  /** intensity between pulses */
  base?: number
  /** extra intensity at a pulse head */
  pulse?: number
  /** core and halo strength (HDR: the core sits well above the bloom threshold, the halo carries the colour) */
  core?: number
  halo?: number
  /** white added to the core at a pulse head, so the head reads hot without washing the colour out */
  hot?: number
  /** how much the halo darkens what lies under it (0 = pure additive light) */
  dim?: number
  /** ribbon half-width in world metres, and its min / max on screen in drawing-buffer pixels */
  halfWidth?: number
  px?: [number, number]
}

export function glowLineMaterial(cut: CutState, o: GlowLineOpts) {
  const m = new THREE.ShaderMaterial({
    vertexShader: LINE_VERT,
    fragmentShader: LINE_FRAG,
    uniforms: {
      uColor: { value: new THREE.Color(o.color) },
      uTime: GLOW_TIME,
      uSpeed: { value: o.speed ?? 1 },
      uScale: { value: o.scale ?? 0.25 },
      uEmph: o.emph,
      uBase: { value: o.base ?? 0.35 },
      uRate: o.rate ?? { value: 1 },
      uPulse: { value: o.pulse ?? 1 },
      uCore: { value: o.core ?? 2 },
      uHalo: { value: o.halo ?? 0.5 },
      uHot: { value: o.hot ?? 0.3 },
      uDim: { value: o.dim ?? 0.4 },
      uHalfW: { value: o.halfWidth ?? 0.008 },
      uPx: { value: new THREE.Vector2(...(o.px ?? [3, 16])) },
      uViewH: GLOW_VIEW_H,
    },
    clipping: true,
    transparent: true,
    depthWrite: false,
    depthTest: false,
    side: THREE.DoubleSide,
    blending: THREE.CustomBlending,
    blendEquation: THREE.AddEquation,
    blendSrc: THREE.OneFactor,
    blendDst: THREE.OneMinusSrcAlphaFactor,
  })
  m.clippingPlanes = cut.planes
  m.clipIntersection = cut.intersect
  return m
}

/**
 * A camera-facing ribbon along a polyline (Catmull-Rom through the points): two vertices per sample, one each side, carrying the
 * centre point, its tangent, the side (-1 / +1), the arc length from the first point `aS` and the whole length `aLen`, in the
 * points' units. The vertex shader spreads it; the geometry itself has zero width.
 */
export function flowRibbon(pts: THREE.Vector3[], perPoint = 8): THREE.BufferGeometry {
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal')
  const n = Math.max(2, (pts.length - 1) * perPoint + 1)
  const sp = curve.getSpacedPoints(n - 1)
  const len = curve.getLength()
  const pos = new Float32Array(n * 6), tan = new Float32Array(n * 6), side = new Float32Array(n * 2), s = new Float32Array(n * 2), L = new Float32Array(n * 2)
  const t = new THREE.Vector3()
  for (let i = 0; i < n; i++) {
    curve.getTangentAt(i / (n - 1), t)
    for (let k = 0; k < 2; k++) {
      const j = i * 2 + k
      pos.set([sp[i].x, sp[i].y, sp[i].z], j * 3)
      tan.set([t.x, t.y, t.z], j * 3)
      side[j] = k ? 1 : -1
      s[j] = (i / (n - 1)) * len // spaced points: sample i sits at i / (n - 1) of the arc length
      L[j] = len
    }
  }
  const idx: number[] = []
  for (let i = 0; i < n - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2) }
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  geo.setAttribute('aTan', new THREE.BufferAttribute(tan, 3))
  geo.setAttribute('aSide', new THREE.BufferAttribute(side, 1))
  geo.setAttribute('aS', new THREE.BufferAttribute(s, 1))
  geo.setAttribute('aLen', new THREE.BufferAttribute(L, 1))
  geo.setIndex(idx)
  return geo
}
