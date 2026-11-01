// Cure gate from a resin curve and the shop environment. Arithmetic is a later wave.

export interface ResinLite {
  min_temp_c: number | null
  gate_hours: [number, number][]
  flag: string
}

export interface Env {
  tempC: number
  humidity: number
  heat: 'none' | 'space-heater' | 'enclosure'
}

/** Degrees added to the room temperature. These boosts are estimates. */
export const HEAT_BOOST_C: Record<Env['heat'], number> = {
  none: 0,
  'space-heater': 5,
  enclosure: 15,
}

export function cureGateHours(resin: ResinLite, env: Env): number | null {
  if (resin.flag === 'unsourced' || resin.gate_hours.length === 0) {
    return null
  }

  const eff = env.tempC + HEAT_BOOST_C[env.heat]

  if (resin.min_temp_c !== null && eff < resin.min_temp_c) {
    return null
  }

  const firstPointTemp = resin.gate_hours[0][0]
  if (eff < firstPointTemp) {
    return null
  }

  const lastPoint = resin.gate_hours[resin.gate_hours.length - 1]
  if (eff >= lastPoint[0]) {
    return lastPoint[1]
  }

  for (let i = 0; i < resin.gate_hours.length - 1; i++) {
    const [t0, h0] = resin.gate_hours[i]
    const [t1, h1] = resin.gate_hours[i + 1]

    if (eff >= t0 && eff <= t1) {
      return h0 + (h1 - h0) * ((eff - t0) / (t1 - t0))
    }
  }

  return null
}
