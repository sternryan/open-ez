import test from 'node:test'
import assert from 'node:assert/strict'
import { hiddenPlanes, blocks, roomPlanes } from '../src/logic/roomCull'
import { ROOM } from '../src/scene/workshop'
const P = roomPlanes(ROOM)
const T: [number, number, number] = [0, 0.9, 0] // the bench
test('inside the room nothing hides', () => assert.equal(hiddenPlanes([0, 1.5, 0], P).size, 0))
test('beyond the room-side wall only that plane hides', () =>
  assert.deepEqual([...hiddenPlanes([0, 1.5, ROOM.z1 + 2], P)], ['room.side']))
test('beyond a corner both planes hide', () =>
  assert.deepEqual(new Set(hiddenPlanes([ROOM.x1 + 1, 1.5, ROOM.z1 + 1], P)), new Set(['room.back', 'room.side'])))
test('above the ceiling the ceiling hides', () => assert.ok(hiddenPlanes([0, ROOM.h + 1, 0], P).has('room.ceiling')))
test('no visible plane blocks the bench from any eye on a 7.5 m sphere', () => {
  for (let az = 0; az < 360; az += 5) for (let el = 2; el < 89; el += 6) {
    const a = (az * Math.PI) / 180, e = (el * Math.PI) / 180
    const eye: [number, number, number] = [T[0] + 7.5 * Math.cos(e) * Math.cos(a), T[1] + 7.5 * Math.sin(e), T[2] + 7.5 * Math.cos(e) * Math.sin(a)]
    assert.deepEqual(blocks(eye, T, P, hiddenPlanes(eye, P)), [], `az ${az} el ${el}`)
  }
})
test('broken input: with nothing hidden, an outside eye IS blocked (the gate can fail)', () =>
  assert.deepEqual(blocks([0, 1.5, ROOM.z1 + 2], T, P, new Set()), ['room.side']))
