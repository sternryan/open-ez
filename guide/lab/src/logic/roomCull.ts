export type Vec3 = [number, number, number]
export type RoomPlane = { key: string; n: Vec3; d: number }
type Room = { x0: number; x1: number; z0: number; z1: number; h: number }
/** Inward planes of the room box (the wall slabs stand just outside them). A target inside a convex room can be hidden by a
 *  plane only when the eye is outside that plane, so the rule needs only the eye. `blocks` is the check, not the rule. */
export const roomPlanes = (R: Room): RoomPlane[] => [
  { key: 'room.back', n: [-1, 0, 0], d: -R.x1 }, { key: 'room.door', n: [1, 0, 0], d: R.x0 },
  { key: 'room.window', n: [0, 0, 1], d: R.z0 }, { key: 'room.side', n: [0, 0, -1], d: -R.z1 },
  { key: 'room.ceiling', n: [0, -1, 0], d: -R.h },
]
const side = (p: RoomPlane, v: Vec3) => p.n[0] * v[0] + p.n[1] * v[1] + p.n[2] * v[2] - p.d
export function hiddenPlanes(eye: Vec3, planes: RoomPlane[], marginM = 0.05): Set<string> {
  return new Set(planes.filter((p) => side(p, eye) < marginM).map((p) => p.key))
}
export function blocks(eye: Vec3, target: Vec3, planes: RoomPlane[], hidden: Set<string>): string[] {
  return planes.filter((p) => !hidden.has(p.key) && side(p, eye) * side(p, target) < 0).map((p) => p.key)
}
