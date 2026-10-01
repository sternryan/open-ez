// The canard12 film's lowering: the canard (with its elevators) comes down onto the airplane at the chapter 7 cutout. Pure maths, no DOM.

/** how far above its installed pose the canard hangs when the lowering starts (inches) */
export const LOWER_HEIGHT = 24
/** seconds the descent takes once it starts */
export const LOWER_SECONDS = 7
/** seconds the canard hangs still, clear of the airplane, before it starts down (the camera settles on it first) */
export const LOWER_HOLD = 1.4
/** what the film calls this step: the book op it illustrates (the install and the alignment are chapter 30 canard ops) */
export const LOWER_LABEL = 'Set the canard on F22 (chapter 30, install and align)'

const ease = (k: number) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2)

/** Height of the canard above its installed pose, in inches, `t` seconds after the descent starts: `height` before (t <= 0), then eased
 * down, and exactly 0 from `seconds` on (the installed pose, not an approach to it). Never negative: the canard never passes through the airplane. */
export function lowerLift(t: number, seconds = LOWER_SECONDS, height = LOWER_HEIGHT): number {
  if (!(t > 0)) return height
  if (t >= seconds) return 0
  return height * (1 - ease(t / seconds))
}

/** The descent's eased progress, 0 (hanging) to 1 (installed): what the camera follows. */
export function lowerProgress(t: number, seconds = LOWER_SECONDS): number {
  return 1 - lowerLift(t, seconds, 1)
}
