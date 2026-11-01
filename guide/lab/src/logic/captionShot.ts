// Where the directed camera looks when the beat's part or ply is not in the model.
// No three.js: the player passes the boxes it measured and flies to the shot this returns.

export interface Box3Like { min: [number, number, number]; max: [number, number, number] }

export interface FrameShot {
  pos: [number, number, number]
  target: [number, number, number]
  fov: number
}

/**
 * Eye-to-target floor for that shot, in metres. Unsourced. The orbit control allows 0.15 m, close enough that the
 * lens sits on a part label (the "Right side" pill filling the frame). 1.4 m at a 30° lens shows about 0.75 m of the
 * subject, so the label stays a mark on the work.
 */
export const MIN_FRAME_M = 1.4

export function unionBoxes(boxes: readonly Box3Like[]): Box3Like | null {
  if (!boxes.length) return null
  const min: [number, number, number] = [Infinity, Infinity, Infinity]
  const max: [number, number, number] = [-Infinity, -Infinity, -Infinity]
  for (const b of boxes) {
    for (let i = 0; i < 3; i++) {
      min[i] = Math.min(min[i], b.min[i])
      max[i] = Math.max(max[i], b.max[i])
    }
  }
  return { min, max }
}

/** The step's drawn components, or the group's assembly when none of those components are drawn. */
export function captionBounds(components: Box3Like | null, group: Box3Like | null): Box3Like | null {
  return components ?? group
}

/**
 * A shot whose target is the middle of `box` and whose eye is far enough to see the box, never closer than MIN_FRAME_M.
 * `dir` is the eye's direction away from the target (it is normalised). `fill` is how much of the vertical field the box's
 * bounding sphere may occupy.
 */
export function captionShot(box: Box3Like, dir: readonly [number, number, number], fovDeg: number, fill = 0.6): FrameShot {
  const target: [number, number, number] = [
    (box.min[0] + box.max[0]) / 2,
    (box.min[1] + box.max[1]) / 2,
    (box.min[2] + box.max[2]) / 2,
  ]
  const dx = box.max[0] - box.min[0], dy = box.max[1] - box.min[1], dz = box.max[2] - box.min[2]
  const radius = 0.5 * Math.hypot(dx, dy, dz)
  const fov = (fovDeg * Math.PI) / 180
  const dist = Math.max(MIN_FRAME_M, radius / Math.tan((Math.max(0.05, fill) * fov) / 2))
  const len = Math.hypot(dir[0], dir[1], dir[2])
  const nx = len > 1e-9 ? dir[0] / len : 0
  const ny = len > 1e-9 ? dir[1] / len : 0.6
  const nz = len > 1e-9 ? dir[2] / len : 1
  return {
    pos: [target[0] + nx * dist, target[1] + ny * dist, target[2] + nz * dist],
    target,
    fov: fovDeg,
  }
}
