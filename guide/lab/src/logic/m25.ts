/**
 * Chapters 14-17 in the lab (the centre-section spar, the firewall face, the controls and the trim). Pure: no three.js, no DOM.
 *
 * The spar is built on the layup table in its jig (chapter 14's bench ops), then slid into the box from the side (f14.fit-fuselage) and
 * stays in it; the firewall face, controls and trim are installed in the box (frame as exported: x = FS, y = W.L. - 17.4, z = -B.L.).
 */
import { visibleOps, type GraphLite } from './graph'

/** the glb node families the fuselage subject owns (the rest are the canard's and the elevators'): a node whose component id starts with one of these */
export const FUSE_PREFIXES = ['fuselage.', 'gear.', 'nose.', 'spar.', 'firewall.', 'controls.', 'trim.', 'canopy.', 'wing.', 'winglet.', 'strake.', 'elec.', 'engine.']
/** chapters 14-17 (the spar, firewall, controls, trim), 18 (the canopy) and 19-20 (the wings, the winglets): the parts of layup.json "extras" m25, m26 and m27 show on these chapters' ops only */
export const M25_CHAPTERS = new Set([14, 15, 16, 17, 18, 19, 20])
/** the first op of chapter 14: from it to SPAR_BENCH_LAST the spar is built on the layup table, and the box on its bench is not drawn */
export const M25_FIRST_OP = 'f14.jig'
export const SPAR_FIT_OP = 'f14.fit-fuselage'
/** the last op the spar is on the bench for; from SPAR_FIT_OP on it is in the box */
export const SPAR_BENCH_LAST = 'f14.nut-access-hole'
/** the components built on the bench (the jig is theirs too): they are the spar that slides in */
export const SPAR_COMPONENTS = new Set(['spar.box', 'spar.cap_top', 'spar.cap_bottom', 'spar.bulkheads', 'spar.lwa', 'spar.spruce_blocks', 'spar.jig'])
/** the installed canard and its elevators show (as in chapters 12-13) for the ops that drive the elevators */
export const ELEV_OPS = new Set(['f16.pitch-pushrod', 'f17.pitch-trim'])
/** the op whose stick control drives the elevators (the live readout, the slider) */
export const STICK_OP = 'f16.pitch-pushrod'
/** the stops show from this op on (they are the stick's travel limits; not printed) */
export const STOPS_FROM = 'f16.pitch-pushrod'
/** components buried in the spar box: the box is drawn faint while the op works on them so they show */
export const BURIED = new Set(['spar.lwa', 'spar.spruce_blocks'])
export const BURIED_OPS = new Set(['f14.interior-layups'])

export type M25Place = 'bench' | 'installed'
/** Where an M2.5 component is while `opId` is selected: the spar parts are on the bench through the last bench op, everything else in the box. */
export function m25Place(component: string, opId: string | null, order: string[]): M25Place {
  if (!SPAR_COMPONENTS.has(component) || !opId) return 'installed'
  return order.indexOf(opId) <= order.indexOf(SPAR_BENCH_LAST) ? 'bench' : 'installed'
}

/** The box is drawn faint when the selected op works on something buried in it. */
export function boxGhostAt(op: { id: string; components: string[] } | null): boolean {
  return !!op && (BURIED_OPS.has(op.id) || op.components.some((c) => BURIED.has(c)))
}

/** Slide-in, in sim seconds since the fit op was picked: the camera comes round first, then the spar enters over `seconds`. */
export const SLIDE = { wait: 1.6, seconds: 3.4 }
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
/** Fraction of the way in (0 = clear of the box on the side, 1 = installed). */
export function slideProgress(t: number): number {
  return ease(Math.min(1, Math.max(0, (t - SLIDE.wait) / SLIDE.seconds)))
}
export const slideDuration = (): number => SLIDE.wait + SLIDE.seconds + 1.2

/** The ops a chapter's tour visits (graph order, not stubs). */
export function m25BarOps(graph: GraphLite, variant: string) {
  return visibleOps(graph, variant).filter((o) => M25_CHAPTERS.has(o.chapter) && !o.stub)
}
