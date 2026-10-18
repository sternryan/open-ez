/** Pure briefing-room mode probe and state transitions. No DOM. */

export type Mode = 'read-only' | 'live'

export type Status = 'open' | 'decided' | 'reopened'

export type TranscriptLine = {
  who: 'owner' | 'council' | 'error'
  text: string
}

export type State = {
  recordId: string
  mode: Mode
  status: Status
  transcript: TranscriptLine[]
  error: string | null
  busy: boolean
  decideEnabled: boolean
}

export type Event =
  | { type: 'loaded'; status: Status }
  | { type: 'sent'; text: string }
  | { type: 'replied'; text: string }
  | { type: 'errored'; message: string }
  | { type: 'decided' }
  | { type: 'reopened' }

export type HealthResponse = {
  ok: boolean
  json: () => Promise<unknown>
}

/** `api/health` with `{ok:true}` is live. A reject, a non-ok status, or any other body is read-only. */
export async function detectMode(fetchFn: (url: string) => Promise<HealthResponse>): Promise<Mode> {
  try {
    const response = await fetchFn('api/health')
    if (!response.ok) return 'read-only'
    const body = await response.json()
    if (isLiveBody(body)) return 'live'
    return 'read-only'
  } catch {
    return 'read-only'
  }
}

function isLiveBody(body: unknown): boolean {
  if (typeof body !== 'object' || body === null || Array.isArray(body)) return false
  return (body as { ok?: unknown }).ok === true
}

/** Returns the next state. Does not mutate `state`. */
export function reduce(state: State, event: Event): State {
  switch (event.type) {
    case 'loaded':
      return { ...state, status: event.status, decideEnabled: event.status !== 'decided' }
    case 'sent':
      return {
        ...state,
        transcript: [...state.transcript, { who: 'owner', text: event.text }],
        busy: true,
        error: null,
      }
    case 'replied':
      return {
        ...state,
        transcript: [...state.transcript, { who: 'council', text: event.text }],
        busy: false,
        error: null,
      }
    case 'errored':
      return { ...state, busy: false, error: event.message }
    case 'decided':
      return { ...state, status: 'decided', decideEnabled: false }
    case 'reopened':
      return { ...state, status: 'reopened', decideEnabled: true }
    default: {
      const unexpected: never = event
      return unexpected
    }
  }
}
