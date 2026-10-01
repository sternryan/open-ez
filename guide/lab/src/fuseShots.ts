/**
 * Lab shots for the fuselage and gear ops (plans chapters 4-9), authored per op. The target is computed at run time from where the op's
 * parts are for that op (on the layup table or in the jig), so a shot follows the build state; the eye is `dist` inches from it,
 * `el` degrees above the horizontal and `az` degrees round from the room side (+Z) toward the nose end of the station (-X).
 *
 * focus: `parts` (fuselage part names, as exported) aims at the middle of those parts; with `fs` it aims at that fuselage station on
 * the first part; with `side` it aims at the part's right (B.L. > 0) or left half (one axle, one leg). `marks` aims at the middle of the gear
 * positioning's dimension (the datum board to the axle line). `at` aims at a point of the airplane (F.S., B.L., W.L.: left is B.L. < 0), wherever the box stands for the op. `box` aims at the box itself in the jig (its chapter 4-6 parts, so the roll-over and the gear do not pull the aim).
 */
export interface FuseView { focus: { parts: string[]; fs?: number; side?: 'right' | 'left' } | { at: [number, number, number] } | 'box' | 'marks'; dist: number; el: number; az: number }

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
  // chapter 7: right side up; the right skin at 45 degrees of left bank (the right side faces up and toward the window wall), the left
  // at 45 of right bank (up and toward the room)
  'f07.carve-corners': { focus: { parts: ['side_left'], fs: 46 }, dist: 70, el: 20, az: 34 }, // the nose end: the striped round corners top and bottom
  'f07.canard-cutout': one('canard_cutout', 72, 34, 38),
  'f07.fuel-gauge-area': { focus: { parts: ['side_left'], fs: 100 }, dist: 70, el: 22, az: -12 },
  'f07.belt-insert': one('belt_insert', 52, 8, 18),
  'f07.skin-right': { focus: 'box', dist: 150, el: 24, az: 136 }, // from the nose end, window side: the right side faces up and toward it
  'f07.skin-left': { focus: 'box', dist: 134, el: 34, az: 12 },
  // chapter 8: the roll-over made on the table, then bonded on the front seat bulkhead in the box
  'f08.roll-over-foam': one('rollover', 64, 52, 24),
  'f08.roll-over-inside': one('rollover', 52, 62, 20), // upside down on the table: looking into it
  'f08.roll-over-bond': one('rollover', 84, 34, -34),
  'f08.roll-over-outside': one('rollover', 64, 26, 36),
  'f08.access-holes': one('rollover', 58, 30, -62),
  'f08.shoulder-harness': one('rollover', 56, 52, 18),
  'f08.belt-attach': one('belt_attach', 92, 58, 10),
  'f08.step': one('step', 44, 14, 24),
  // chapter 9: the strut on the table, then the box upside down on the gear table, the gear legs up
  'f09.strut-stiffen': one('strut', 118, 52, 8),
  'f09.jig-blocks': one('jig_blocks', 56, 14, -34),
  'f09.position-gear': { focus: 'marks', dist: 118, el: 16, az: -18 },
  'f09.tab-layup': one('strut', 104, 34, -18),
  'f09.tab-assembly': one('gear_tubes', 62, 40, -30),
  'f09.axles-brakes': { focus: { parts: ['axles'], side: 'right' }, dist: 42, el: 14, az: -30 },
  'f09.brake-lines': one('strut', 112, 30, -12),
}

/** a point of the airplane in the station's box frame (x = F.S., y = W.L. - 17.4, z = -B.L.; see FuselageBay) */
const at = (fs: number, wl: number, bl = 0): { at: [number, number, number] } => ({ at: [fs, wl - 17.4, -bl] })
/**
 * Chapters 12 and 13, authored the same way (kept apart from FUSE_VIEWS, which is the chapter 4-9 set). The nose's part names are the
 * export's (`nose_<component>`, `gear_nose_strut`: layup.json "extras"). The box stands on its own gear for these ops, the nose toward -X and
 * the canard installed across the top at W.L. 18.9 (aft of the nose), so:
 *  - the nose and gear ops look from low, in front and to the left (the room side, az +40), the eye below the canard plane, at the nose
 *    and the nose gear (F.S. 0..40, W.L. +14 .. -22), so the strut, wheel, plates, floor blocks and door all show;
 *  - the canard ops look at the canard's trailing edge and the elevators near F22 from the left and behind.
 */
const nose = (fs: number, wl: number, dist: number, el = 12, az = 40): FuseView => ({ focus: at(fs, wl), dist, el, az })
const canardTe = (fs: number, bl: number, dist = 72, el = 16, az = -38): FuseView => ({ focus: at(fs, 19, bl), dist, el, az })
export const NOSE_VIEWS: Record<string, FuseView> = {
  // chapter 12: the canard's trailing edge, the elevators and F22, from the left and behind
  'r30.f22-drill-tabs': canardTe(35, -14, 62, 22, -52),
  'r30.elev-fuselage-clearance': canardTe(35, -8, 54, 20, -58),
  'r30.lift-tab-bushings': canardTe(35, -16, 60, 24, -46),
  'r30.f28-pins-permanent': canardTe(36, -12, 66, 22, -56),
  // chapter 13: low three-quarter from the front left
  'f13.strut-reinforce': nose(8, -8, 96, 10),
  'f13.worm-drive-bench': nose(8, -8, 96, 10),
  'f13.ng30-plates': nose(6, 4, 72, 12),
  'f13.ng-box-assemble': nose(8, 0, 86, 12),
  'f13.ng3-ng4': nose(8, 2, 72, 12, 42),
  'f13.ng31-f6': nose(10, 2, 80, 12),
  'f13.floor-blocks': nose(8, 2, 74, 16),
  'f13.pedal-pivot-blocks': nose(10, 2, 74, 16),
  'f13.side-pieces': nose(8, 4, 82, 14),
  'f13.canard-attach-reinforce': canardTe(35, -16, 62, 22, -50),
  'f13.rudder-pedals': nose(10, 2, 76, 14),
  'f13.lower-gear': nose(8, -9, 92, 8),
  'f13.strut-slot-sc': nose(8, -8, 92, 8),
  'f13.nb-box': nose(14, -4, 98, 10),
  'f13.rig-nose-gear': nose(22, -8, 122, 8, 36), // the strut's whole swing (F.S. 17 down to the NB box at 31-39.75) in view
  'f13.pitot-static': nose(4, -2, 86, 12),
  'f13.top-foam': nose(8, 8, 88, 14),
  'f13.carve-glass-nose': nose(8, -2, 102, 10),
  'f13.nose-door': nose(6, -2, 86, 10),
  'f13.shock-strut': nose(8, -10, 92, 8),
}

const DEFAULT: FuseView = { focus: 'box', dist: 130, el: 38, az: 16 }
export const fuseView = (opId: string): FuseView => FUSE_VIEWS[opId] ?? NOSE_VIEWS[opId] ?? DEFAULT

/** Eye offset from the target, in inches, in the station's frame (+Y up, +Z toward the room, -X toward the nose end). */
export function viewOffset(v: FuseView): [number, number, number] {
  const el = (v.el * Math.PI) / 180, az = (v.az * Math.PI) / 180
  const h = Math.cos(el) * v.dist
  return [-Math.sin(az) * h, Math.sin(el) * v.dist, Math.cos(az) * h]
}
