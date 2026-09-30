/**
 * Lab shots for the fuselage ops (plans chapters 4-6), authored per op. The target is computed at run time from where the op's
 * parts are for that op (on the layup table or in the jig), so a shot follows the build state; the eye is `dist` inches from it,
 * `el` degrees above the horizontal and `az` degrees round from the room side (+Z) toward the nose end of the station (-X).
 *
 * focus: `parts` (fuselage part names, as exported) aims at the middle of those parts; with `fs` it aims at that fuselage station on
 * the first part. `box` aims at the parts in the jig.
 */
export interface FuseView { focus: { parts: string[]; fs?: number } | 'box'; dist: number; el: number; az: number }

const SIDES = ['side_right', 'side_left']
const one = (p: string, dist: number, el: number, az: number): FuseView => ({ focus: { parts: [p] }, dist, el, az })

export const FUSE_VIEWS: Record<string, FuseView> = {
  // chapter 4: each bulkhead flat on the layup table, the face being glassed up
  'f04.front-seat-bkhd-front': one('front_seat_bkhd', 66, 54, 16),
  'f04.front-seat-bkhd-back': one('front_seat_bkhd', 66, 54, 16),
  'f04.rear-seat-bkhd-foam': one('rear_seat_bkhd', 58, 54, 12),
  'f04.rear-seat-bkhd-hole': one('rear_seat_bkhd', 58, 54, 12),
  'f04.panel-f22-f28-aft': { focus: { parts: ['panel', 'f22', 'f28'] }, dist: 84, el: 54, az: 6 },
  'f04.panel-f22-f28-fwd': { focus: { parts: ['panel', 'f22', 'f28'] }, dist: 84, el: 54, az: 6 },
  'f04.firewall-aft': one('firewall', 56, 54, -10),
  'f04.firewall-fwd': one('firewall', 56, 54, -10),
  // chapter 5: both sides flat on the table, inside face up
  'f05.side-blank': { focus: { parts: SIDES }, dist: 128, el: 55, az: 8 },
  'f05.side-profile': { focus: { parts: SIDES }, dist: 128, el: 55, az: 8 },
  'f05.side-layout': { focus: { parts: SIDES }, dist: 120, el: 52, az: 10 },
  'f05.inside-layup': { focus: { parts: SIDES }, dist: 118, el: 50, az: 14 },
  'f05.top-longeron-glass': { focus: { parts: SIDES, fs: 55 }, dist: 80, el: 42, az: 24 },
  'f05.lower-longeron': { focus: { parts: SIDES, fs: 70 }, dist: 84, el: 42, az: 18 },
  'f05.gear-pad': { focus: { parts: SIDES, fs: 112 }, dist: 60, el: 48, az: -22 },
  'f05.spar-cutout': { focus: { parts: SIDES, fs: 120 }, dist: 54, el: 48, az: -26 },
  'f05.gear-extrusions': { focus: { parts: SIDES, fs: 112 }, dist: 60, el: 44, az: -22 },
  // chapter 6: the jig, the box upside down on its blocks, then right side up on its bottom
  'f06.trial-fit': { focus: 'box', dist: 132, el: 38, az: 20 },
  'f06.jig-check': { focus: 'box', dist: 132, el: 26, az: 6 },
  'f06.bond-front-seat': one('front_seat_bkhd', 92, 44, 24),
  'f06.bond-panel': one('panel', 92, 44, 28),
  'f06.bond-f22': one('f22', 90, 44, 32),
  'f06.bond-rear-seat': one('rear_seat_bkhd', 92, 44, -18),
  'f06.bond-firewall': one('firewall', 92, 42, -30),
  'f06.f28-install': one('f28', 86, 44, 34),
  'f06.rear-seat-tape': one('rear_seat_bkhd', 84, 48, -14),
  'f06.bottom-foam-fit': { focus: 'box', dist: 132, el: 40, az: 14 },
  'f06.bottom-contour': { focus: 'box', dist: 124, el: 30, az: 20 },
  'f06.bottom-glass': one('bottom', 124, 58, 8),
  'f06.bottom-bond': { focus: 'box', dist: 132, el: 36, az: 18 },
  'f06.bottom-tape': { focus: 'box', dist: 108, el: 60, az: 10 },
}

const DEFAULT: FuseView = { focus: 'box', dist: 130, el: 38, az: 16 }
export const fuseView = (opId: string): FuseView => FUSE_VIEWS[opId] ?? DEFAULT

/** Eye offset from the target, in inches, in the station's frame (+Y up, +Z toward the room, -X toward the nose end). */
export function viewOffset(v: FuseView): [number, number, number] {
  const el = (v.el * Math.PI) / 180, az = (v.az * Math.PI) / 180
  const h = Math.cos(el) * v.dist
  return [-Math.sin(az) * h, Math.sin(el) * v.dist, Math.cos(az) * h]
}
