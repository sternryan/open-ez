/**
 * Lab shots. tours.yaml positions were authored for the 2.1 viewer, which floats over the wing; here the camera stands in the shop.
 * Each op keeps the tours.yaml TARGET (the authored focus, model inches) and gets a position authored in the CANARD'S frame:
 * model inches, X chord (leading edge toward -X), Y up through the thickness, Z = -B.L. (root at 0, tip at about -70.8).
 * Positions are turned into world space at the pose the canard will be in for that op, so a bottom-side op on the inverted
 * canard puts the eye above the table.
 */
export type V3 = [number, number, number]
export interface Tour { target: V3; position: V3 }
export interface LabShot { target: V3; position: V3 }

export const LAB_FOV = 30

/** A 3/4 close view: `dist` inches from the target, `el` degrees above the working surface, `az` degrees round from the leading edge toward the root. */
interface View { dist: number; el: number; az: number; /** the work is on a vertical face (the shear web): always look down on it, whatever way up the canard is */ vertical?: boolean }
const DEFAULT_VIEW: View = { dist: 52, el: 31, az: 52 }
const VIEWS: Record<string, View> = {
  'r30.bottom-spar-cap': { dist: 50, el: 31, az: 52 },
  'r30.bottom-skin': { dist: 54, el: 31, az: 52 },
  'r30.shear-web': { dist: 46, el: 32, az: 52, vertical: true },
  'r30.top-spar-cap': { dist: 50, el: 31, az: 52 },
  'r30.top-skin': { dist: 54, el: 31, az: 52 },
}

/** Which surface the op works on, from the authored tour: the authored eye above the target is the top surface, below it the bottom. */
function surfaceSign(t: Tour): 1 | -1 {
  return t.position[1] >= t.target[1] ? 1 : -1
}

export function labShots(tours: Record<string, Tour>, poseOf: (opId: string) => 'inverted' | 'upright' = () => 'upright'): Record<string, LabShot> {
  const out: Record<string, LabShot> = {}
  for (const [id, t] of Object.entries(tours)) {
    const v = VIEWS[id] ?? DEFAULT_VIEW
    const el = (v.el * Math.PI) / 180, az = (v.az * Math.PI) / 180
    // a vertical face has no top or bottom: the eye is above the table, which in the canard's frame is -Y while it is inverted
    const s = v.vertical ? (poseOf(id) === 'inverted' ? -1 : 1) : surfaceSign(t)
    const h = Math.cos(el) * v.dist
    // leading edge is -X; swing toward the root (+Z) by `az`; rise along the working surface's normal (+Y for top, -Y for bottom)
    const off: V3 = [-h * Math.cos(az), s * Math.sin(el) * v.dist, h * Math.sin(az)]
    out[id] = { target: [...t.target], position: [t.target[0] + off[0], t.target[1] + off[1], t.target[2] + off[2]] }
  }
  return out
}
