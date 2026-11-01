// Optional ground school: whether the first-launch offer has been answered, which step a
// skip jumps to, and the playback speed for a lesson versus a build step. No DOM.
// Skip is remembered apart from "seen": the lessons stay in the plan, and the meter
// does not treat them as bought or spent.

import type { Storage2 } from './graph'

/** localStorage. The offer is "seen" after Start or Skip. */
export const GROUND_KEY = 'longez.ground'
export const GROUND_SEEN = 'seen'

/** Set only on Skip. Start clears it. Absent means the lessons count as the watched step passes them. */
export const GROUND_SKIP_KEY = 'longez.ground.skip'
export const GROUND_SKIPPED = 'skipped'

export const GROUND_GROUP = 'ground-school'
/** The lesson that introduces the shop environment controls this phase already has. */
export const SHOP_SETUP = 'g00.shop-setup'

export type PlaybackSpeed = 1 | 4 | 16

export interface SpeedChoice {
  ground: PlaybackSpeed
  build: PlaybackSpeed
}

/** Ground lessons start at 1x. Build steps start at 4x. Either side can be overridden. */
export const DEFAULT_SPEED: SpeedChoice = { ground: 1, build: 4 }

/** Missing, blocked or any other value counts as not yet offered. */
export function loadGroundSeen(storage: Storage2 | null): boolean {
  try {
    return storage?.getItem(GROUND_KEY) === GROUND_SEEN
  } catch {
    return false
  }
}

export function saveGroundSeen(storage: Storage2 | null): void {
  try { storage?.setItem(GROUND_KEY, GROUND_SEEN) } catch { /* per-viewer; a blocked store still plays */ }
}

/** True only after Skip. A missing, blocked or other value means the lessons were not skipped. */
export function loadGroundSkipped(storage: Storage2 | null): boolean {
  try {
    return storage?.getItem(GROUND_SKIP_KEY) === GROUND_SKIPPED
  } catch {
    return false
  }
}

export function saveGroundSkipped(storage: Storage2 | null): void {
  try { storage?.setItem(GROUND_SKIP_KEY, GROUND_SKIPPED) } catch { /* per-viewer; a blocked store still plays */ }
}

/** Start answers the offer without skipping, so a stale skip flag does not keep the lessons out of the meter. */
export function clearGroundSkipped(storage: Storage2 | null): void {
  try { storage?.setItem(GROUND_SKIP_KEY, '') } catch { /* per-viewer; a blocked store still plays */ }
}

export function isGroundGroup(groupId: string | null | undefined): boolean {
  return groupId === GROUND_GROUP
}

/**
 * The offer is still open, and this is the first move.
 * Play or a selection on a ground lesson is Start. The same moves on a build step are Skip.
 */
export function choiceForOffer(action: 'play' | 'select', stepIsGround: boolean): 'start' | 'skip' {
  if (stepIsGround && (action === 'play' || action === 'select')) return 'start'
  return 'skip'
}

export function speedFor(groupId: string | null | undefined, choice: SpeedChoice): PlaybackSpeed {
  return isGroundGroup(groupId) ? choice.ground : choice.build
}

export function firstGroundStep(steps: { id: string; group: string }[]): string | null {
  return steps.find((s) => isGroundGroup(s.group))?.id ?? null
}

/** The first step that is not a ground-school lesson. Skip lands here. */
export function firstBuildStep(steps: { id: string; group: string }[]): string | null {
  return steps.find((s) => !isGroundGroup(s.group))?.id ?? null
}

export function showsShopControls(stepId: string): boolean {
  return stepId === SHOP_SETUP
}
