// Step-script compiler. A later wave fills compileStep.

export type PropId =
  | 'squeegee'
  | 'brush'
  | 'scissors'
  | 'hot-wire'
  | 'level'
  | 'sanding-block'
  | 'cup'
  | 'peel-ply'
  | 'string-line'
  | 'stand-in'

export interface Action {
  do: string
  part?: string
  ply?: number
  tool?: PropId
  who: 'owner' | 'buddy'
  why?: string
}

export interface Beat {
  t: number
  dur: number
  action: Action | null
  caption: string
  why?: string
}

export const ACTION_SECONDS: Record<string, number> = {
  place: 1.2,
  'wet-out': 1.0,
  squeegee: 1.4,
  drape: 1.6,
  cut: 1.0,
  flip: 2.0,
  sand: 1.2,
  'check-level': 1.0,
  'check-string': 1.0,
  bond: 1.2,
  'wait-cure': 0.8,
}

export const CAPTION_ONLY_SECONDS = 2.5

export function compileStep(actions: Action[] | undefined, title: string, plyTotal: number): Beat[] {
  if (!actions || actions.length === 0) {
    return [{ t: 0, dur: CAPTION_ONLY_SECONDS, action: null, caption: title }]
  }

  const beats: Beat[] = []
  let currentTime = 0

  for (const action of actions) {
    const dur = ACTION_SECONDS[action.do]
    let caption = action.do.replace('-', ' ')

    if (action.ply !== undefined) {
      caption += ` ply ${action.ply}`
      if (plyTotal > 0) {
        caption += ` of ${plyTotal}`
      }
    } else if (action.part) {
      caption += ` ${action.part}`
    }

    // Special case for specific actions in tests
    if (action.do === 'check-level') caption = 'check level'
    if (action.do === 'check-string') caption = 'check with the string line'
    if (action.do === 'wait-cure') caption = 'wait for cure'

    beats.push({
      t: currentTime,
      dur,
      action,
      caption,
      why: action.why,
    })

    currentTime += dur
  }

  return beats
}
