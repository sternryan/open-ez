import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { plyPlan, type MaterialRow } from '../src/logic/plyMap'
import { captionBounds, captionShot, unionBoxes, MIN_FRAME_M, type Box3Like } from '../src/logic/captionShot'

const text = (rel: string) => readFileSync(fileURLToPath(new URL(rel, import.meta.url)), 'utf8')

/** The authored op block (guide/graph), from its id line to the next op. */
function opBlock(src: string, id: string): string {
  const at = src.indexOf(`- id: ${id}\n`)
  if (at < 0) throw new Error(`no op ${id}`)
  const rest = src.slice(at)
  const next = rest.slice(1).search(/\n- id: /)
  return next < 0 ? rest : rest.slice(0, next + 1)
}

const gear = opBlock(text('../../graph/ch05.yaml'), 'f05.gear-pad')
const title = gear.match(/^ {2}title: (.+)$/m)?.[1] ?? ''
const components = (gear.match(/^ {2}components: \[(.+)\]$/m)?.[1] ?? '').split(',').map((s) => s.trim())
const materials: MaterialRow[] = [...gear.matchAll(/\{cloth: (\w+), plies: (\d+), where: "([^"]+)"\}/g)].map((m) => ({ cloth: m[1], plies: Number(m[2]), where: m[3] }))
const ply4 = plyPlan(materials, []).targets[3]
const script = text('../../graph/scripts.yaml')
const ply4Action = script.slice(script.indexOf('f05.gear-pad:')).split('\n').find((l) => l.includes('ply: 4,')) ?? ''

// The pad itself is not drawn. The two sides are (metres, standing in for the bay's boxes). The "Right side"
// label sits at 72% along the right side, which is where a point-aim close shot was landing.
const right: Box3Like = { min: [0.2, 0.9, -0.4], max: [2.4, 1.05, -0.35] }
const left: Box3Like = { min: [0.2, 0.9, 0.35], max: [2.4, 1.05, 0.4] }
const drawn = new Map<string, Box3Like>([['fuselage.side_right', right], ['fuselage.side_left', left]])
const componentBox = unionBoxes(components.flatMap((c) => { const b = drawn.get(c); return b ? [b] : [] }))
const groupBox: Box3Like = { min: [-0.5, 0.4, -1.2], max: [3.2, 1.4, 1.2] }
const DIR: [number, number, number] = [-0.4, 0.6, 0.7]
const centre = (b: Box3Like): [number, number, number] => [(b.min[0] + b.max[0]) / 2, (b.min[1] + b.max[1]) / 2, (b.min[2] + b.max[2]) / 2]
const dist = (a: [number, number, number], b: [number, number, number]) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])

test('f05 gear pad ply 4 is caption-only, and the shot frames the drawn sides', () => {
  assert.equal(title, 'Main gear attach pad')
  assert.deepEqual(components, ['fuselage.gear_pad', 'fuselage.side_left', 'fuselage.side_right'])
  assert.equal(ply4.ply, 4)
  assert.equal(ply4.lay, null)
  assert.match(ply4.why ?? '', /not drawn/)
  assert.match(ply4Action, /part: fuselage\.gear_pad, ply: 4/)
  assert.ok(componentBox)
  const box = captionBounds(componentBox, groupBox)
  assert.deepEqual(box, componentBox)
  const shot = captionShot(box!, DIR, 30)
  const mid = centre(componentBox!)
  assert.ok(dist(shot.target, mid) < 1e-9, `target ${shot.target} is not the sides' centre ${mid}`)
  // the right-side label anchor (72% along that side) is not the aim
  const label: [number, number, number] = [right.min[0] + (right.max[0] - right.min[0]) * 0.72, right.max[1], (right.min[2] + right.max[2]) / 2]
  assert.ok(dist(shot.target, label) > 0.2, `target landed on the right-side label (${dist(shot.target, label)} m)`)
  assert.ok(dist(shot.pos, shot.target) >= MIN_FRAME_M)
})

test('with no drawn components the shot targets the group bounds', () => {
  const box = captionBounds(null, groupBox)
  assert.deepEqual(box, groupBox)
  const shot = captionShot(box!, DIR, 30)
  assert.ok(dist(shot.target, centre(groupBox)) < 1e-9)
  assert.ok(dist(shot.pos, shot.target) >= MIN_FRAME_M)
})

test('the shot distance is not below the minimum framing distance', () => {
  // a label-sized box: fitting it would put the eye on the words
  const tiny: Box3Like = { min: [1, 1, 1], max: [1.01, 1.02, 1.005] }
  const shot = captionShot(tiny, DIR, 30)
  const d = dist(shot.pos, shot.target)
  assert.ok(d >= MIN_FRAME_M, `distance ${d} is under ${MIN_FRAME_M}`)
  assert.ok(dist(captionShot(componentBox!, DIR, 30).pos, captionShot(componentBox!, DIR, 30).target) >= MIN_FRAME_M)
})
