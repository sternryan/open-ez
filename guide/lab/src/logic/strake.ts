/**
 * Chapters 21 to 23 in the lab (the strakes and fuel tanks, the electrical system, the engine and cowl chapter). Pure: no three.js, no DOM.
 *
 * The strakes are built against the fuselage on a jig table level with the longerons: the cut pieces first lie on the layup table (the right strake's kit),
 * then stand in their places on the airplane (on its gear), one op at a time, both sides. The tank is a shaded volume inside them. The nose battery, the relays
 * on F22 and the antenna foil are buried in foam, so those ops draw the rest of the airplane faint and their own parts through it. The engine is a fitted block
 * aft of the firewall (installation is in Sections IIA, IIC and IIL, not held), striped and said so.
 * Frame as exported (python): x = F.S., y = B.L. (right positive), z = W.L. - 17.4.
 */
import type { LedgerLite } from './fuselage'

export const STRAKE_CHAPTER = 21
export const ELEC_CHAPTER = 22
export const ENGINE_CHAPTER = 23
export const M28_CHAPTERS = new Set([21, 22, 23])
export const CUT_PARTS_OP = 'f21.cut-parts'
export const CUTOUTS_OP = 'f21.fuselage-cutouts'
export const JIG_BOND_OP = 'f21.jig-bond'
export const INSIDE_LAYUPS_OP = 'f21.inside-layups'
export const CLOSE_TANK_OP = 'f21.close-tank'
export const OD_OUTLET_OP = 'f21.od-outlet'
export const OUTSIDE_BOTTOM_OP = 'f21.outside-bottom'
export const PRESSURE_OP = 'f21.pressure-check'
export const FAIRING_OP = 'f21.fairing-caps'
export const PLUMBING_OP = 'f21.plumbing'
export const PANEL_WIRING_OP = 'f22.panel-wiring'
export const BATTERY_OP = 'f22.battery-shelf'
export const TERMINALS_OP = 'f22.firewall-terminals'
export const WING_WIRING_OP = 'f22.wing-wiring'
export const ANTENNAS_OP = 'f22.antennas'
export const ENGINE_OP = 'f23.engine-install'
export const BRACKET_OP = 'f23.carb-bracket'
export const COWL_TRIM_OP = 'f23.cowl-trim'
export const COWL_CLOSE_OP = 'f23.cowl-closeout'
export const ROOT_RIB_OP = 'f23.root-rib'
/** the chapters' ops in book order (the lab's order assertion and the tour read this) */
export const CH21 = ['f21.cut-parts', 'f21.fuselage-cutouts', 'f21.jig-bond', 'f21.inside-layups', 'f21.vent-screen', 'f21.close-tank', 'f21.od-outlet', 'f21.outside-bottom', 'f21.outside-top', 'f21.pressure-check', 'f21.fairing-caps', 'f21.plumbing']
export const CH22 = ['f22.panel-wiring', 'f22.microswitches', 'f22.battery-shelf', 'f22.firewall-terminals', 'f22.wing-wiring', 'f22.antennas']
export const CH23 = ['f23.engine-install', 'f23.carb-bracket', 'f23.cowl-trim', 'f23.cowl-closeout', 'f23.root-rib']

/** the pieces cut on the layup table at the first op (the right strake's kit, the left is the mirror): they stand in their places from their own ops on */
export const KIT_PARTS = new Set(['rib_r23', 'rib_r45', 'b23', 'db', 'bab', 'od', 'tle', 'ble', 'skin_bottom', 'skin_top'])
/** the top skin core is drawn this far above the rest of the kit on the cutting op (inches): the ribs and baffles stand under it, so each piece reads */
export const KIT_LIFT_IN = 12
/** the ops that show the tank: the rest of the airplane (the skins included) goes faint and the tank volume is drawn through it */
export const TANK_OPS = new Set([CLOSE_TANK_OP, PRESSURE_OP])
/** the ops that work on something buried in the airplane (the openings in the fuselage side, the outboard diagonal and outlet inside the closed strake, the sump blister under it, the panel's wiring, the nose battery, the relays behind F22, the foil, the bracket under the block, the thin root rib inside the cowl): the rest is drawn faint */
export const M28_GHOST_OPS = new Set([CUTOUTS_OP, CLOSE_TANK_OP, OD_OUTLET_OP, OUTSIDE_BOTTOM_OP, PRESSURE_OP, PANEL_WIRING_OP, BATTERY_OP, TERMINALS_OP, ANTENNAS_OP, BRACKET_OP, ROOT_RIB_OP])
/** the jig table is under the strake while its bottom is bonded and glassed inside, until the tank is closed and the strake comes off it for the outside skins */
export const TABLE_FROM = JIG_BOND_OP
export const TABLE_UNTIL = OD_OUTLET_OP

export interface M28PartRow {
  node: string; component: string; side: 'right' | 'left' | null; fidelity: string; label: string; cite: string[]
  fs_min: number; fs_max: number; bl_min: number; bl_max: number; show: { from: string }; op_index: number
  void?: boolean; pocket?: boolean; in_foam?: boolean; inset?: boolean
}
/** layup.json "fuselage"."extras"."m28" (guide/fuselage_export.py m28_section) */
export interface M28Data {
  parts: Record<string, M28PartRow>
  fuel: { model_gal_per_side: number; plans_gal_per_tank: number; om_gal_per_tank: number; om_total_gal: number; envelope_gal_per_side: number; lb_per_gal: number; arm_fs: number; note: string }
  conflicts: { cutout_aft_top_depth: { mid_in: number; aft_end_in: number }; baggage_arm: { om_fs: number; plan_centroid_fs: number }; layup_7_numbering: string[] }
  battery: { fs_range: number[]; model_fs: number; status: string; added_lb: number; starter_fs_min: number; relay_fs: number }
  engine: { down_thrust_deg: number; crank_bl: number; block_in: number[]; block_fwd_fs: number; limits_lb: number[]; oil: { lb: number; fs: number }; striped: string[]; note: string }
  weights: { rows: string[]; note: string; closure_target: { empty_lb: number; empty_arm_in: number; cite: string; loaded_envelope_fs: number[]; note: string }; cg: string }
}
export interface MaterialLite { cloth: string; plies: number; where: string }

const r2 = (x: number) => (Math.round(x * 100) / 100).toString()
const r1 = (x: number) => (Math.round(x * 10) / 10).toFixed(1)

/** a part's own name inside its component ("rib_r23" from "strake.ribs.rib_r23.right") */
export function partBase(row: Pick<M28PartRow, 'node' | 'component'>): string {
  return row.node.slice(row.component.length + 1).replace(/\.(right|left)$/, '')
}

export type M28Where = 'none' | 'table' | 'jig'
/**
 * Where a chapter 21-23 part is while `opId` is selected. The right strake's kit lies on the layup table on the cutting op, then each part stands in
 * its place on the airplane from the op its row names, both sides (the left is the mirror); the openings in the fuselage side show on their own op only
 * (material removed); the electrical and engine parts stand from their own ops. Nothing selected: not drawn (the chapter's parts belong to its ops).
 */
export function m28Where(row: M28PartRow, opId: string | null, order: string[]): M28Where {
  if (!opId) return 'none'
  const i = order.indexOf(opId), from = order.indexOf(row.show.from)
  if (i < 0 || from < 0) return 'none'
  if (row.void) return opId === row.show.from ? 'jig' : 'none'
  if (row.component.startsWith('strake.') && KIT_PARTS.has(partBase(row))) {
    if (opId === CUT_PARTS_OP) return row.side === 'right' ? 'table' : 'none'
  }
  return i >= from ? 'jig' : 'none'
}
/** the right strake's kit is on the layup table: the airplane is not drawn */
export const strakeBenchAt = (opId: string | null): boolean => opId === CUT_PARTS_OP
/** the jig table under the strake (a fitted shape: the plans give no table beyond "level with the longerons") */
export function strakeTableShown(opId: string | null, order: string[]): boolean {
  if (!opId) return false
  const i = order.indexOf(opId)
  return i >= order.indexOf(TABLE_FROM) && i < order.indexOf(TABLE_UNTIL)
}
/** the rest of the airplane is drawn faint for this op */
export const m28GhostAt = (op: { id: string } | null): boolean => !!op && M28_GHOST_OPS.has(op.id)
/** the parts of an op that stay solid and draw through the faint airplane: the op's own components, but on the tank ops only the tank (the skins would hide it) */
export const m28Exposed = (op: { id: string; components: string[] } | null, cid: string): boolean => !!op && (TANK_OPS.has(op.id) ? cid === 'strake.tank' : op.components.includes(cid))

/** the op's parts a half-translucent look reads best (the tank's fuel, the openings' removed material): REPRESENTATIONAL colours */
export const GLASS_PARTS: Record<string, number> = { tank: 0x58b4e8, cutout_baggage: 0xd8574a, cutout_tank: 0xd8574a }
export const GLASS_OPACITY_28 = { tank: 0.42, cutout: 0.5 }

// ---- readouts ----

/** the fuel capacity conflict, always as text with both printed figures, the model's and the envelope's own */
export function fuelText(d: M28Data): { value: string; sub: string } {
  const f = d.fuel
  return {
    value: `Tank capacity: plans 2 x ${r2(f.plans_gal_per_tank)} gal, manual 2 x ${r2(f.om_gal_per_tank)} gal (${r2(f.om_total_gal)} in all); model ${r2(f.model_gal_per_side)} a side`,
    sub: `Unresolved. Shaded envelope ${r2(f.envelope_gal_per_side)} gal a side (fitted shape, not measured); fuel ${r1(f.lb_per_gal)} lb per gal at FS ${r1(f.arm_fs)}`,
  }
}
/** the cutout depth at the tank hole's aft end (1.90 once, 1.40 elsewhere on the page) and the baggage arm (90 in the manual, 80.6 from the floor's centroid) */
export function cutoutText(d: M28Data): { value: string; sub: string } {
  const c = d.conflicts.cutout_aft_top_depth, b = d.conflicts.baggage_arm
  return {
    value: `Tank hole aft end: ${r2(c.aft_end_in)} in below WL 23 once, ${r2(c.mid_in)} in elsewhere on the page`,
    sub: `Unresolved. Baggage arm: FS ${r2(b.om_fs)} in the manual, FS ${r2(b.plan_centroid_fs)} from the floor's own centroid; which volume the ${r2(b.om_fs)} covers is not known`,
  }
}
/** layup 7 is numbered twice (the OD's inside, then the whole strake's outside) */
export function layup7Text(d: M28Data): { value: string; sub: string } {
  const [a, b] = d.conflicts.layup_7_numbering
  return { value: `Layup 7 is printed twice: inside the outboard diagonal (${a.replace('f21.', '')}) and on the outside (${b.replace('f21.', '')})`, sub: 'Unresolved. Both are laid; the model calls them 7a and 7b' }
}
/** the battery's station is a range (A6 shows it, not held), never a number */
export function batteryText(d: M28Data): { value: string; sub: string } {
  const b = d.battery
  return {
    value: `Battery station: FS ${r2(b.fs_range[0])} to ${r2(b.fs_range[1])}, not printed (A6 only)`,
    sub: `Drawn at FS ${r2(b.model_fs)} for illustration only; the battery adds ${r1(b.added_lb)} lb with its cable and relay (reference, not in CG)`,
  }
}
/** the starter, ring gear and alternator are "station 150+": a bound, not a station */
export function starterText(d: M28Data): { value: string; sub: string } {
  const b = d.battery
  return {
    value: `Starter, ring gear and alternator: station ${r2(b.starter_fs_min)} or aft (CP27 page 4), not drawn`,
    sub: `A bound, not a station. The relays are on F22 near FS ${r2(b.relay_fs)}; no engine, mount or starter station is printed`,
  }
}
/** the engine limits and what the block stands for */
export function engineText(d: M28Data): { value: string; sub: string } {
  const e = d.engine
  return {
    value: `Engine with accessories at most ${r2(e.limits_lb[0])} lb, vibrating mass at most ${r2(e.limits_lb[1])} lb; oil ${r2(e.oil.lb)} lb at FS ${r2(e.oil.fs)}`,
    sub: `Fitted shape; installation in Section II, not held. The block is ${e.block_in.map(r2).join(' x ')} in, ${r2(e.down_thrust_deg)} deg down thrust`,
  }
}
/** the plies an op lays, from its own schedule (graph "materials"): "5 plies: 3 BID + 2 UND" and where each goes */
export function layupText(materials: MaterialLite[]): { value: string; sub: string } | null {
  if (!materials.length) return null
  const n = new Map<string, number>()
  let total = 0
  for (const m of materials) { n.set(m.cloth, (n.get(m.cloth) ?? 0) + m.plies); total += m.plies }
  return { value: `${total} plies: ${[...n].map(([c, k]) => `${k} ${c}`).join(' + ')}`, sub: materials.map((m) => `${m.plies} ${m.cloth}, ${m.where}`).join('; ') }
}

/**
 * The ops with a readout of their own, and what it says (null: none). The conflicts and bounds come first; an op that also has a layup schedule appends it.
 */
export function m28Kin(opId: string | null, d: M28Data, materials: MaterialLite[] = []): { label: string; value: string; sub: string } | null {
  const lay = layupText(materials)
  const pick = (): { label: string; value: string; sub: string } | null => {
    switch (opId) {
      case CUT_PARTS_OP: case CLOSE_TANK_OP: case PRESSURE_OP: case FAIRING_OP: return { label: 'Fuel capacity', ...fuelText(d) }
      case CUTOUTS_OP: return { label: 'Cutout conflicts', ...cutoutText(d) }
      case OD_OUTLET_OP: case OUTSIDE_BOTTOM_OP: return { label: 'Layup numbering', ...layup7Text(d) }
      case PLUMBING_OP: return { label: 'Fuel capacity', ...fuelText(d) }
      case BATTERY_OP: return { label: 'Battery station', ...batteryText(d) }
      case TERMINALS_OP: return { label: 'Starter station', ...starterText(d) }
      case ENGINE_OP: return { label: 'Engine limits', ...engineText(d) }
      default: return null
    }
  }
  const k = pick()
  if (!lay) return k
  if (!k) return { label: 'Layup schedule', ...lay }
  return { ...k, sub: `${k.sub}. Plies: ${lay.value} (${lay.sub})` }
}

/**
 * The reference weight rows, never in the CG: the N26MS empty-weight ladder (CP27 page 4) from the battery op on, the dynafocal mount on the engine op, the
 * cowl on its ops, and at the end of the chapters the OM sample empty airplane as the target the ledger closure will be held to.
 */
export function m28Row(ledger: LedgerLite | null, d: M28Data | null, opId: string | null, order: string[]): { value: string; sub: string } | null {
  const rows = ledger?.prototype_weights?.rows
  if (!rows || !d || !opId || !/^f2[123]\./.test(opId)) return null
  const at = (op: string) => order.indexOf(opId) >= order.indexOf(op)
  const ref = ', reference, not in CG'
  const ladder = d.weights.rows.filter((k) => k.startsWith('n26ms_empty_') && rows[k]).map((k) => r1(rows[k].weight_lb))
  const t = d.weights.closure_target
  const target = `Closure target: OM sample empty airplane ${r2(t.empty_lb)} lb at FS ${r1(t.empty_arm_in)}${ref}`
  if (at(ROOT_RIB_OP) && ladder.length) {
    return { value: `${target}; N26MS ladder ${ladder.join(' / ')} lb`, sub: `FS ${r2(t.loaded_envelope_fs[0])} to ${r2(t.loaded_envelope_fs[1])} is the loaded envelope, not the empty CG. CG ${d.weights.cg}` }
  }
  if (at(COWL_TRIM_OP) && opId.startsWith('f23.') && rows.cowl_glass && rows.cowl_graphite) {
    return { value: `Cowl (CP27 page 5): ${r1(rows.cowl_glass.weight_lb)} lb in glass, ${r1(rows.cowl_graphite.weight_lb)} lb in graphite${ref}`, sub: rows.cowl_glass.note }
  }
  if (at(ENGINE_OP) && opId.startsWith('f23.') && rows.dynafocal_mount) return { value: `Dynafocal mount (CP26 builder weight, N26MS): ${r2(rows.dynafocal_mount.weight_lb)} lb${ref}`, sub: rows.dynafocal_mount.note }
  if (at(BATTERY_OP) && opId.startsWith('f22.') && ladder.length) return { value: `N26MS empty-weight ladder (CP27 page 4): ${ladder.join(' / ')} lb${ref}`, sub: `${rows.n26ms_empty_4?.note ?? ''}` }
  return null
}
