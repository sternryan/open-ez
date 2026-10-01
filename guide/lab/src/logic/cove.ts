/**
 * The elevators' cove (Block 2 M2.4 fix 1). The canard's core and skins run the full chord, so the elevators (which sit in the aft part of
 * that chord) were drawn inside them and could not be seen. While the elevators are shown, the canard's own meshes are not drawn aft of
 * `xCut` over the elevators' span (|z| <= blEnd, the tips keep their full chord). xCut is the elevators' leading edge less the book's
 * hinge slot gap, both from the export (layup.json extras.elevators.cove); nothing here is a number of its own.
 *
 * Pure: the same maths the shader (core/materials.ts GLSL_COVE) runs, so the clip and the cap it closes are under test. The box is
 * open in y (a through cut): x > xCut and |z| < blEnd, in the canard's model frame (x chord aft, y up, z = -B.L., inches).
 */
export interface Cove { xCut: number; blEnd: number }

/** the cove from the export's numbers: the elevators' leading edge x, the hinge slot gap, and the elevators' outboard end (B.L.) */
export function coveFrom(elevLeX: number, slotGap: number, blEnd: number): Cove {
  return { xCut: elevLeX - slotGap, blEnd }
}

/** a point of the canard's own meshes is removed (not drawn) */
export function inCove(c: Cove, p: readonly number[]): boolean {
  return p[0] > c.xCut && Math.abs(p[2]) < c.blEnd
}

export type CoveFace = 'x' | 'z+' | 'z-'
/** inward normals of the box's three faces (the cap faces into the removed box) */
export const COVE_NORMAL: Record<CoveFace, [number, number, number]> = { x: [1, 0, 0], 'z+': [0, 0, 1], 'z-': [0, 0, -1] }

/** where a ray leaves the removed box (into the kept solid): the distance along it (rd is a unit vector) and the face it leaves through; null if it never crosses the box */
export function coveExit(c: Cove, ro: readonly number[], rd: readonly number[]): { t: number; face: CoveFace } | null {
  let t0 = 0, t1 = Infinity
  let face: CoveFace | null = null
  const clip = (n: readonly number[], k: number, id: CoveFace) => {
    const dn = n[0] * rd[0] + n[1] * rd[1] + n[2] * rd[2]
    const d0 = n[0] * ro[0] + n[1] * ro[1] + n[2] * ro[2] + k
    if (Math.abs(dn) < 1e-9) { if (d0 <= 0) { t0 = 1; t1 = 0 } return }
    const th = -d0 / dn
    if (dn < 0) { if (th < t1) { t1 = th; face = id } } else t0 = Math.max(t0, th)
  }
  clip(COVE_NORMAL.x, -c.xCut, 'x')
  clip(COVE_NORMAL['z+'], c.blEnd, 'z+')
  clip(COVE_NORMAL['z-'], c.blEnd, 'z-')
  return face && t0 < t1 && t1 > 0 ? { t: t1, face } : null
}

/**
 * The cap a back face seen from `ro` shows: the ray to the back face point `p` crosses the removed box and leaves it before reaching `p`,
 * so what is seen is the solid cut open at the box's wall (the point on it and the wall's normal, facing into the box). Null otherwise.
 */
export function coveCap(c: Cove, ro: readonly number[], p: readonly number[]): { point: number[]; normal: number[]; face: CoveFace } | null {
  const d = [p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]]
  const tf = Math.hypot(d[0], d[1], d[2])
  const rd = d.map((v) => v / Math.max(tf, 1e-6))
  const e = coveExit(c, ro, rd)
  if (!e || e.t >= tf) return null
  return { point: [0, 1, 2].map((i) => ro[i] + rd[i] * e.t), normal: [...COVE_NORMAL[e.face]], face: e.face }
}
