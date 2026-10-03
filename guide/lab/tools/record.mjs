// Adapted from AirsupHQ/airsup-lab tools/record.mjs (MIT); see NOTICE.
// Changes: takes the served lab page as an argument (no dev-server default), one film ("canard"), 60 fps default, GPU flags plus an opt-in software path, an out-of-tree friendly output dir.
/**
 * Render the canard-chapter film to a 1080p MP4, frame by frame, so it never drops a frame.
 *
 *   npm --prefix guide/lab run record -- canard|canard12|fuselage6|fuselage8|fuselage9 <out.mp4> [fps] <url>
 *
 * `canard` is the Roncz chapter 30 film; `fuselage6` is the fuselage's chapter 6 (jig assembly) film; `fuselage9` its chapter 9 (main landing gear) film; `canard12` is the canard lowering onto F22 (chapter 12) on the fuselage subject.
 *
 * <url> is the served site's lab page, e.g. http://127.0.0.1:8800/lab/ (build a site with
 * `python -m guide.build_site --models <longez.glb> --out <dir>` and serve <dir> with `python3 -m http.server <port>`).
 * fps defaults to 60. Set LAB_SWIFTSHADER=1 to allow the software renderer (slow; for machines without a GPU).
 * Needs Playwright's Chromium (`npx playwright install chromium`, shared with the Python tests) and ffmpeg on the PATH.
 */
import { spawn } from 'node:child_process'
import { mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const FILMS = ['canard', 'canard12', 'fuselage6', 'fuselage8', 'fuselage9']
const MAX_RUNTIME_MS = 1800000

async function settleWithin(promise, milliseconds) {
  let timer
  try {
    return await Promise.race([
      Promise.resolve(promise).then(() => true, () => true),
      new Promise((resolve) => { timer = setTimeout(() => resolve(false), milliseconds) }),
    ])
  } finally {
    clearTimeout(timer)
  }
}

/** Record locally; injected browser/encoder implementations permit deterministic failure tests.
 * Encoder success is necessary but does not certify media validity or release eligibility.
 * Failed attempts can leave an incomplete MP4; collection must not accept it.
 */
export async function recordFilm({ film, out, fps = 60, url, timeoutMs = MAX_RUNTIME_MS, signal }, {
  launchBrowser, spawnEncoder = spawn, log = console.log, cleanupMs = 5000,
} = {}) {
  fps = Number(fps)
  if (!FILMS.includes(film) || !out || !url || !Number.isInteger(fps) || fps < 1 || fps > 120) {
    throw new Error('invalid film, output, URL or fps (integer 1–120 required)')
  }
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > MAX_RUNTIME_MS) {
    throw new Error('recording runtime must be bounded to 30 minutes')
  }
  let browser, browserClosing, ff, encoderDone, failure, inputEnded = false, encoderClosed = false, closing = false
  const closeBrowser = () => {
    browserClosing ??= Promise.resolve().then(() => browser.close())
    return browserClosing
  }
  let rejectFailure
  const failed = new Promise((_, reject) => { rejectFailure = reject })
  failed.catch(() => {}) // Errors can arrive between awaited operations.
  const fail = (error) => {
    if (!failure) {
      failure = error instanceof Error ? error : new Error(String(error))
      rejectFailure(failure)
    }
  }
  const watch = async (operation) => {
    const value = await Promise.race([operation, failed])
    if (failure) throw failure
    return value
  }
  const onAbort = () => fail(new Error('recording cancelled'))
  signal?.addEventListener('abort', onAbort, { once: true })
  if (signal?.aborted) onAbort()
  const timer = setTimeout(() => fail(new Error('recording runtime exceeded')), timeoutMs)
  try {
    if (failure) throw failure
    mkdirSync(dirname(out), { recursive: true })
    if (!launchBrowser) {
      const { chromium } = await watch(import('playwright'))
      launchBrowser = (options) => chromium.launch(options)
    }
    const gpu = ['--enable-gpu', '--ignore-gpu-blocklist', '--use-angle=metal']
    const soft = ['--use-gl=swiftshader', '--enable-unsafe-swiftshader']
    const launching = launchBrowser({ args: process.env.LAB_SWIFTSHADER === '1' ? soft : gpu, timeout: Math.min(timeoutMs, 120000) })
    // A launch completing after timeout/cancellation still owns a browser to close.
    Promise.resolve(launching).then((lateBrowser) => {
      // Acquire ownership before the cancellation race can reject its await.
      browser = lateBrowser
      if (closing) return settleWithin(closeBrowser(), cleanupMs)
    }).catch(() => {})
    browser = await watch(launching)
    browser.on('disconnected', () => { if (!closing) fail(new Error('recording browser disconnected')) })
    const page = await watch(browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 }))
    page.on('pageerror', (error) => fail(new Error(`recording page error: ${error.message}`)))
    page.on('crash', () => fail(new Error('recording page crashed')))
    const logs = []
    page.on('console', (message) => {
      logs.push(`${message.type()}: ${message.text()}`.slice(0, 1000))
      if (logs.length > 20) logs.shift()
    })
    await watch(page.goto(`${url}${url.includes('?') ? '&' : '?'}rec=1`))
    // A ?rec=1 page has no animation loop; poll on a timer.
    try {
      await watch(page.waitForFunction(() => typeof window.__rec === 'object', null, { timeout: Math.min(timeoutMs, 120000), polling: 250 }))
    } catch (error) {
      for (const entry of logs) log(`console ${entry}`)
      throw error
    }
    const duration = await watch(page.evaluate((name) => window.__rec.start(name), film))
    if (!Number.isFinite(duration) || duration <= 0 || duration > 1800) throw new Error('invalid recording duration')
    ff = spawnEncoder('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'inherit'] })
    encoderDone = new Promise((resolve) => {
      ff.once('error', (error) => fail(new Error(`encoder spawn failed: ${error.message}`)))
      ff.once('close', (code, exitSignal) => {
        encoderClosed = true
        if (code !== 0 || exitSignal) fail(new Error(`encoder failed: exit ${code}, signal ${exitSignal ?? 'none'}`))
        else if (!inputEnded) fail(new Error('encoder closed before all frames were written'))
        resolve()
      })
    })
    ff.stdin.on('error', (error) => fail(new Error(`encoder input failed: ${error.message}`)))
    const count = Math.ceil(duration * fps)
    for (let index = 0; index < count; index++) {
      const frame = await watch(page.evaluate((dt) => window.__rec.frame(dt), 1 / fps))
      const shot = await watch(page.screenshot({ type: 'jpeg', quality: 95 }))
      // A write callback bounds buffering; errors/close/timeout also interrupt the wait.
      await watch(new Promise((resolve, reject) => {
        ff.stdin.write(shot, (error) => error ? reject(error) : resolve())
      }))
      if (index % 300 === 0) log(`frame ${index} / ${count}`)
      if (!frame.active && index > 10) break
    }
    inputEnded = true
    ff.stdin.end()
    await watch(encoderDone)
  } finally {
    closing = true
    clearTimeout(timer)
    if (ff && !encoderClosed) {
      ff.stdin.destroy()
      ff.kill('SIGTERM')
      await settleWithin(encoderDone, cleanupMs)
      if (!encoderClosed) {
        ff.kill('SIGKILL')
        await settleWithin(encoderDone, cleanupMs)
      }
    }
    if (browser) {
      let closeError
      const closed = await settleWithin(closeBrowser().catch((error) => { closeError = error }), cleanupMs)
      if (!failure && (closeError || !closed)) fail(closeError ?? new Error('recording browser cleanup timed out'))
    }
    signal?.removeEventListener('abort', onAbort)
  }
  if (signal?.aborted) onAbort()
  if (failure) throw failure
  log('wrote', out)
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  const [film, out, fps = '60', url] = process.argv.slice(2)
  if (!FILMS.includes(film) || !out || !url) {
    console.error('usage: record canard|canard12|fuselage6|fuselage8|fuselage9 <out.mp4> [fps] <url of the served /lab/ page>')
    process.exitCode = 2
  } else {
    const controller = new AbortController()
    const cancel = () => controller.abort()
    process.once('SIGINT', cancel)
    process.once('SIGTERM', cancel)
    try {
      await recordFilm({ film, out, fps, url, signal: controller.signal })
    } catch (error) {
      console.error('recording failed:', error.message)
      process.exitCode = 1
    } finally {
      process.off('SIGINT', cancel)
      process.off('SIGTERM', cancel)
    }
  }
}
