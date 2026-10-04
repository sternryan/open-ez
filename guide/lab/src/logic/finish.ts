/**
 * Chapters 24 to 26 in the lab (covers and consoles, finishing, upholstery). Pure: no three.js, no DOM.
 *
 * The covers, consoles, thigh support, canard cover and gap seals (chapter 24) and the cushions, headrests and suitcases (chapter 26) are fitted shapes that
 * stand in their places on the airplane from the op that makes them. The finish (chapter 25) is not geometry: it is a layer drawn on the airframe's own
 * surfaces by stage (fill, then primer, then paint), from layup.json "extras"."m29"."finish". It has no weight (none is printed) and no thickness in the model.
 * Frame as exported (python): x = F.S., y = B.L. (right positive), z = W.L. - 17.4.
 */
export const COVER_CHAPTER = 24
export const FINISH_CHAPTER = 25
export const UPHOLSTERY_CHAPTER = 26
export const M29_CHAPTERS = new Set([24, 25, 26])
/** the chapters' ops in book order (the lab's order assertion and the tour read this) */
export const CH24 = ['f24.aft-cover', 'f24.console-lc1', 'f24.consoles-left', 'f24.thigh-support', 'f24.canard-cover', 'f24.gap-seal']
export const CH25 = ['f25.inspect-repair', 'f25.coarse-fill', 'f25.feather-fill', 'f25.primer', 'f25.paint-seals']
export const CH26 = ['f26.cushions-headrests', 'f26.suitcases']
export const AFT_COVER_OP = 'f24.aft-cover'
export const CONSOLES_OP = 'f24.consoles-left'
export const GAP_SEAL_OP = 'f24.gap-seal'
export const INSPECT_OP = 'f25.inspect-repair'
export const COARSE_FILL_OP = 'f25.coarse-fill'
export const FEATHER_FILL_OP = 'f25.feather-fill'
export const PRIMER_OP = 'f25.primer'
export const PAINT_OP = 'f25.paint-seals'
export const CUSHIONS_OP = 'f26.cushions-headrests'
export const SUITCASES_OP = 'f26.suitcases'
/** the last op of chapter 25: the finished airplane, seen whole on its gear */
export const FINISHED_OP = PAINT_OP
export const LC1_OP = 'f24.console-lc1'
export const THIGH_OP = 'f24.thigh-support'
/** the ops that work inside the cockpit: the canopy over it is left out of the frame (it opens in life) so the consoles, cushions and suitcases read from above */
export const COCKPIT_OPS = new Set([LC1_OP, CONSOLES_OP, THIGH_OP, CUSHIONS_OP, SUITCASES_OP])
/** the ops that work on something buried in the airplane (the gap seal's wedges sit between the strake's baffle and the wing skin): the rest is drawn faint, the op's own parts through it */
export const M29_GHOST_OPS = new Set([GAP_SEAL_OP])
export const m29GhostAt = (op: { id: string } | null): boolean => !!op && M29_GHOST_OPS.has(op.id)
export const cockpitOpenAt = (op: { id: string } | null): boolean => !!op && COCKPIT_OPS.has(op.id)
/** the filler goes on from the coarse fill (its first op); the data's own "from" for the fill stage is the feather coat that sets its thickness */
export const FILL_FROM_OP = COARSE_FILL_OP

export interface M29PartRow {
  node: string; component: string; fidelity: string; label: string; cite: string[]
  fs_min: number; fs_max: number; bl_min: number; bl_max: number; show: { from: string }; op_index: number
}
export interface FinishStage { stage: 'fill' | 'primer' | 'paint'; from: string; thickness_in: number[] | null; colour: string }
export interface FinishRow { component: string; match: string | null; surface: string; stages: FinishStage[]; final_colour: string }
/** layup.json "fuselage"."extras"."m29" (guide/fuselage_export.py m29_section) */
export interface M29Data {
  parts: Record<string, M29PartRow>
  finish: { rows: FinishRow[]; colours: Record<string, string>; min_temp_f: number; weave_in: number; note: string }
  conflicts: {
    aft_cover_plies: { scan_inside_outside: number[]; transcription_inside_outside: number[]; note: string }
    lc2_length_in: { scan: number; transcription: number }
  }
  seal: { gap_in: number; front_gap_in: number; note: string }
  weights: {
    finish_deltas: Record<string, { weight_lb: number }>
    note: string
    closure_target: {
      empty_lb: number; empty_arm_in: number; loaded_envelope_fs: number[]; note: string; samples: string
      sample_loadings: { name: string; total_lb: number; cg_in: number; inside_envelope: boolean }[]
    }
    cg: string
  }
}
export interface MaterialLite { cloth: string; plies: number; where: string }

const r1 = (x: number) => (Math.round(x * 10) / 10).toFixed(1)
const r2 = (x: number) => (Math.round(x * 100) / 100).toString()
const num = (x: number) => parseFloat(x.toPrecision(3)).toString()
/** a printed fraction of an inch: 0.5 is "1/2", 0.0625 is "1/16" */
export function frac(x: number): string {
  for (const den of [2, 4, 8, 16, 32]) if (Math.abs(x * den - Math.round(x * den)) < 1e-9 && Math.round(x * den) > 0) return `${Math.round(x * den)}/${den}`
  return num(x)
}

// ---- where each part is ----

export type M29Where = 'none' | 'jig'
/** Where a chapter 24 or 26 part is while `opId` is selected: in its place on the airplane from the op its row names, and never before it. Nothing selected: not drawn. */
export function m29Where(row: M29PartRow, opId: string | null, order: string[]): M29Where {
  if (!opId) return 'none'
  const i = order.indexOf(opId), from = order.indexOf(row.show.from)
  if (i < 0 || from < 0) return 'none'
  return i >= from ? 'jig' : 'none'
}

// ---- the finish ----

/** the colours of the finish (REPRESENTATIONAL: the book prints no airplane colour, only that white goes on the upper wing and canard) */
export const FILL_COLOUR = 0xd6c3a0
export const FINISH_COLOURS: Record<string, number> = { 'primer-grey': 0x8b8f93, white: 0xf3f3ef }
export type FinishStageName = 'fill' | 'primer' | 'paint'
/** the stage the airframe's finish is at while `opId` is selected: nothing before the first filler op, then fill, primer, paint (it stays painted on the upholstery ops) */
export function finishStageAt(row: FinishRow, opId: string | null, order: string[]): FinishStageName | null {
  if (!opId) return null
  const i = order.indexOf(opId)
  if (i < 0) return null
  let at: FinishStageName | null = null
  for (const s of row.stages) {
    const from = order.indexOf(s.stage === 'fill' ? FILL_FROM_OP : s.from)
    if (from >= 0 && i >= from) at = s.stage
  }
  return at
}
/** the colour (24-bit) the row's surface wears at `stage`: the filler's tint, primer grey, then the last coat's own colour (white on the upper wing and canard only) */
export function finishColour(row: FinishRow, stage: FinishStageName): number {
  if (stage === 'fill') return FILL_COLOUR
  const s = row.stages.find((x) => x.stage === stage)
  return FINISH_COLOURS[s?.colour ?? 'primer-grey'] ?? FINISH_COLOURS['primer-grey']
}
/** the finish row a glb part belongs to: the first row whose component is the part's and whose node match (if any) is in the part's node name, or null */
export function finishRowFor(rows: FinishRow[], component: string, node: string): FinishRow | null {
  return rows.find((r) => (r.component === component || (FINISH_ALIAS[r.component] ?? []).includes(component)) && (r.match === null || node.includes(r.match))) ?? null
}
/** the finish rows name graph components; where the glb carries a surface under other ids (the fuselage's skins are its sides and bottom: the graph's skin components have no geometry) the row applies to these too */
export const FINISH_ALIAS: Record<string, string[]> = { 'fuselage.skin_right': ['fuselage.side_right'], 'fuselage.skin_left': ['fuselage.side_left'] }
/** the ops the finish changes the airplane's look on (the lab's per-op pixels): the three coats' ops */
export const FINISH_OPS = [COARSE_FILL_OP, PRIMER_OP, PAINT_OP]

// ---- readouts ----

const fillRange = (d: M29Data): number[] => d.finish.rows[0]?.stages.find((s) => s.stage === 'fill')?.thickness_in ?? []
const primerRange = (d: M29Data): number[] => d.finish.rows[0]?.stages.find((s) => s.stage === 'primer')?.thickness_in ?? []

/** the aft cover's ply count is three-way split (the scan blanks the inside number and hand-edits the outside, LPC 54 says one, the transcription keeps one and two) */
export function aftCoverText(d: M29Data): { value: string; sub: string } {
  const c = d.conflicts.aft_cover_plies
  const [a, b] = [c.scan_inside_outside, c.transcription_inside_outside]
  return {
    value: `Aft cover plies: scan ${a[0]} inside and ${a[1]} outside, transcription ${b[0]} inside and ${b[1]} outside`,
    sub: `Unresolved. ${c.note}`,
  }
}
/** the console top LC2's length: 30.6 on the scan, 30.8 in the transcription */
export function lc2Text(d: M29Data): { value: string; sub: string } {
  const c = d.conflicts.lc2_length_in
  return {
    value: `Console top LC2 length: ${r1(c.scan)} in on the scan, ${r1(c.transcription)} in in the transcription`,
    sub: 'Unresolved. Both are carried; the drawn console top is a fitted shape',
  }
}
/** the gap seal: 1/2 in on the wing side, 1/16 in at the front; the 1/2 glyph reads as 3/4 at this scan resolution */
export function sealText(d: M29Data): { value: string; sub: string } {
  return {
    value: `Gap seal: ${frac(d.seal.gap_in)} in gap at the wing root, ${frac(d.seal.front_gap_in)} in at the front`,
    sub: `Drawn as a fitted shape. ${d.seal.note}`,
  }
}
/** the 70 F rule and the glass weave the fill must bury */
export function shopText(d: M29Data): { value: string; sub: string } {
  return {
    value: `Finishing: shop held at ${d.finish.min_temp_f} F or above; glass weave ${num(d.finish.weave_in)} in rough`,
    sub: `Nothing goes on before every structure is inspected and repaired. ${d.finish.note}`,
  }
}
export function fillText(d: M29Data): { value: string; sub: string } {
  const f = fillRange(d)
  return {
    value: `Feather fill ${num(f[0])} to ${num(f[1])} in over the ${num(d.finish.weave_in)} in weave, shop at ${d.finish.min_temp_f} F or above`,
    sub: 'A layer drawn on the airframe, not a solid, and it carries no weight in the model (no finish weight is printed)',
  }
}
export function primerText(d: M29Data): { value: string; sub: string } {
  const p = primerRange(d)
  return {
    value: `Primer ${num(p[0])} to ${num(p[1])} in over the sanded fill`,
    sub: `Primer grey is a representational colour; the book prints no airplane colour. Fill ${num(fillRange(d)[0])} to ${num(fillRange(d)[1])} in under it`,
  }
}
export function paintText(d: M29Data): { value: string; sub: string } {
  return {
    value: 'No finish weight printed. White on the upper wing and canard only; primer grey elsewhere',
    sub: `White: ${d.finish.colours.white}. The grey is representational`,
  }
}
export function upholsteryText(): { value: string; sub: string } {
  return {
    value: 'No upholstery weight printed',
    sub: 'The cushions, headrests and suitcases are fitted shapes (the plans give outlines, not weights); nothing is added to the weight ledger for them',
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

/** ops of chapters 24 to 26 only: another chapter's readout is never displaced (the M2.8 round 3 trap) */
const M29_OP = /^f2[456]\./

/**
 * The ops with a readout of their own, and what it says (null: none). The conflicts and bounds come first; an op that also has a layup schedule appends it.
 */
export function m29Kin(opId: string | null, d: M29Data, materials: MaterialLite[] = []): { label: string; value: string; sub: string } | null {
  if (!opId || !M29_OP.test(opId)) return null
  const lay = layupText(materials)
  const pick = (): { label: string; value: string; sub: string } | null => {
    switch (opId) {
      case AFT_COVER_OP: return { label: 'Aft cover plies', ...aftCoverText(d) }
      case CONSOLES_OP: return { label: 'Console length', ...lc2Text(d) }
      case GAP_SEAL_OP: return { label: 'Gap seal', ...sealText(d) }
      case INSPECT_OP: return { label: 'Finishing rules', ...shopText(d) }
      case FEATHER_FILL_OP: return { label: 'Fill thickness', ...fillText(d) }
      case PRIMER_OP: return { label: 'Primer thickness', ...primerText(d) }
      case PAINT_OP: return { label: 'Finish weight', ...paintText(d) }
      case CUSHIONS_OP: case SUITCASES_OP: return { label: 'Upholstery weight', ...upholsteryText() }
      default: return null
    }
  }
  const k = pick()
  if (!lay) return k
  if (!k) return { label: 'Layup schedule', ...lay }
  return { ...k, sub: `${k.sub}. Plies: ${lay.value} (${lay.sub})` }
}

/**
 * The reference rows, never in the CG: the N26MS finish deltas (CP26 page 3 ready to finish against CP27 page 1 filled and painted) on the finishing ops, and on the
 * last op of the chapters the OM sample empty airplane as the target the ledger closure (2.n) will be held to, with both OM sample loadings.
 */
export function m29Row(d: M29Data | null, opId: string | null, order: string[]): { value: string; sub: string } | null {
  if (!d || !opId || !M29_OP.test(opId)) return null
  const ref = ', reference, not in CG'
  const t = d.weights.closure_target
  if (opId === SUITCASES_OP) {
    const s = t.sample_loadings
    const text = (k: string, word: string) => {
      const x = s.find((y) => y.name === k)
      return x ? `${word} pilot ${x.total_lb} lb at FS ${r2(x.cg_in)} (${x.inside_envelope ? 'inside' : `outside the ${r2(t.loaded_envelope_fs[1])} aft limit, as the manual says`})` : ''
    }
    return {
      value: `Closure target: OM sample empty airplane ${r2(t.empty_lb)} lb at FS ${r1(t.empty_arm_in)}${ref}`,
      sub: `OM samples: ${text('light_pilot', 'light')}; ${text('heavy_pilot', 'heavy')}. FS ${r2(t.loaded_envelope_fs[0])} to ${r2(t.loaded_envelope_fs[1])} is the loaded envelope, not the empty CG. CG ${d.weights.cg}`,
    }
  }
  const at = (op: string) => order.indexOf(opId) >= order.indexOf(op)
  if (opId.startsWith('f25.') && at(COARSE_FILL_OP)) {
    const f = d.weights.finish_deltas
    const parts = [['canopy', 'finish_delta_canopy'], ['aileron', 'finish_delta_aileron'], ['wing', 'finish_delta_wing']].filter(([, k]) => f[k]).map(([w, k]) => `${w} ${num(f[k].weight_lb)} lb`)
    if (parts.length) return { value: `N26MS finish deltas (CP26 page 3 against CP27 page 1): ${parts.join(', ')}${ref}`, sub: d.weights.note }
  }
  return null
}
