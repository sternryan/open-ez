import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { EventEmitter } from 'node:events'
import { recordFilm } from './record.mjs'

test('CLI rejects a planted encoder failure instead of reporting a written video', () => {
  const root = mkdtempSync(join(tmpdir(), 'lab-recorder-test-'))
  try {
    writeFileSync(join(root, 'playwright.mjs'), `
      export const chromium = {launch: async () => ({
        on() {}, close: async () => {}, newPage: async () => ({
          on() {}, goto: async () => {}, waitForFunction: async () => {},
          evaluate: async (fn, value) => typeof value === 'string' ? 1 : {active: true},
          screenshot: async () => Buffer.from('synthetic-frame')
        })
      })}
    `)
    writeFileSync(join(root, 'loader.mjs'), `
      export async function resolve(specifier, context, nextResolve) {
        if (specifier === 'playwright') return {url: new URL('./playwright.mjs', import.meta.url).href, shortCircuit: true}
        return nextResolve(specifier, context)
      }
    `)
    writeFileSync(join(root, 'ffmpeg'), '#!/usr/bin/env node\nprocess.stdin.resume(); process.stdin.on("end", () => process.exit(1));\n', {mode: 0o700})
    const run = spawnSync(process.execPath, [
      '--loader', join(root, 'loader.mjs'), fileURLToPath(new URL('./record.mjs', import.meta.url)),
      'canard', join(root, 'out.mp4'), '1', 'http://127.0.0.1/lab/',
    ], {encoding: 'utf8', timeout: 10000, env: {...process.env, PATH: `${root}:${process.env.PATH}`}})
    assert.ifError(run.error)
    assert.notEqual(run.status, 0, 'failed ffmpeg must make the CLI fail')
    assert.doesNotMatch(run.stdout, /wrote/)
  } finally {
    rmSync(root, {recursive: true, force: true})
  }
})

function harness(settings = {}) {
  const calls = { browserClosed: 0, signals: [], writes: 0, spawned: 0, logs: [] }
  const browser = new EventEmitter()
  const page = new EventEmitter()
  const encoder = new EventEmitter()
  encoder.stdin = new EventEmitter()
  encoder.stdin.write = (_, callback) => {
    calls.writes++
    if (settings.write) return settings.write({callback, page, browser, encoder})
    queueMicrotask(() => callback(null))
    return true
  }
  encoder.stdin.end = () => {
    if (!settings.hangEncoder) queueMicrotask(() => encoder.emit('close', settings.exitCode ?? 0, settings.exitSignal ?? null))
  }
  encoder.stdin.destroy = () => { calls.inputDestroyed = true }
  encoder.kill = (signal) => {
    calls.signals.push(signal)
    if (!settings.ignoreTerm || signal === 'SIGKILL') queueMicrotask(() => encoder.emit('close', null, signal))
    return true
  }
  browser.newPage = async () => page
  browser.close = async () => {
    calls.browserClosed++
    browser.emit('disconnected')
    if (settings.closeError) throw new Error('planted browser cleanup failure')
    if (settings.hangClose) return new Promise(() => {})
  }
  page.goto = async () => {}
  page.waitForFunction = async () => {
    if (settings.readinessError) throw new Error('planted recorder readiness failure')
    if (settings.hangReadiness) return new Promise(() => {})
  }
  page.evaluate = async (_, value) => typeof value === 'string' ? (settings.duration ?? 1) : {active: true}
  page.screenshot = async () => {
    if (settings.screenshot) return settings.screenshot({page, browser, encoder})
    if (settings.screenshotError) throw new Error('planted screenshot failure')
    return Buffer.from('synthetic-frame')
  }
  const dependencies = {
    launchBrowser: async () => browser,
    spawnEncoder: () => {
      calls.spawned++
      if (settings.spawnError) queueMicrotask(() => encoder.emit('error', new Error('planted missing ffmpeg')))
      return encoder
    },
    log: (...args) => calls.logs.push(args.join(' ')), cleanupMs: 10,
  }
  const options = {film: 'canard', out: join(tmpdir(), 'recorder-unit.mp4'), fps: 1,
    url: 'http://127.0.0.1/lab/', timeoutMs: 1000}
  return {calls, browser, page, encoder, dependencies, options}
}

function didReportSuccess(calls) {
  return calls.logs.some((line) => line.startsWith('wrote '))
}

test('successful encoder close reports output only after browser cleanup', async () => {
  const {options, dependencies, calls} = harness()
  await recordFilm(options, dependencies)
  assert.equal(calls.writes, 1)
  assert.equal(calls.browserClosed, 1)
  assert.deepEqual(calls.signals, [])
  assert.equal(didReportSuccess(calls), true)
})

for (const settings of [{exitCode: 1}, {exitCode: 0, exitSignal: 'SIGTERM'}]) {
  test(`encoder exit ${settings.exitCode}, signal ${settings.exitSignal ?? 'none'} rejects success`, async () => {
    const {options, dependencies, calls} = harness(settings)
    await assert.rejects(recordFilm(options, dependencies), /encoder failed/)
    assert.equal(calls.browserClosed, 1)
    assert.equal(didReportSuccess(calls), false)
  })
}

test('page errors fail the recording and terminate the encoder', async () => {
  const {options, dependencies, calls} = harness({screenshot: ({page}) => {
    page.emit('pageerror', new Error('planted page exception'))
    return Buffer.from('frame')
  }})
  await assert.rejects(recordFilm(options, dependencies), /page error/)
  assert.equal(calls.browserClosed, 1)
  assert.equal(calls.inputDestroyed, true)
  assert.deepEqual(calls.signals, ['SIGTERM'])
  assert.equal(didReportSuccess(calls), false)
})

test('broken encoder input rejects a pending write without waiting for drain', async () => {
  const {options, dependencies, calls} = harness({write: ({encoder}) => {
    queueMicrotask(() => encoder.stdin.emit('error', new Error('EPIPE')))
    return false
  }})
  await assert.rejects(recordFilm(options, dependencies), /encoder input failed: EPIPE/)
  assert.equal(calls.browserClosed, 1)
  assert.deepEqual(calls.signals, ['SIGTERM'])
  assert.equal(didReportSuccess(calls), false)
})

test('an early zero-status close cannot satisfy a pending frame write', async () => {
  const {options, dependencies, calls} = harness({write: ({encoder}) => {
    queueMicrotask(() => encoder.emit('close', 0, null))
    return false
  }})
  await assert.rejects(recordFilm(options, dependencies), /before all frames/)
  assert.equal(calls.browserClosed, 1)
  assert.equal(didReportSuccess(calls), false)
})

test('encoder spawn errors fail without an unhandled child error', async () => {
  const {options, dependencies, calls} = harness({spawnError: true})
  await assert.rejects(recordFilm(options, dependencies), /encoder spawn failed/)
  assert.equal(calls.browserClosed, 1)
  assert.equal(didReportSuccess(calls), false)
})

for (const event of ['page-crash', 'browser-disconnected']) {
  test(`${event} fails and cleans up resources`, async () => {
    const {options, dependencies, calls} = harness({screenshot: ({page, browser}) => {
      if (event === 'page-crash') page.emit('crash')
      else browser.emit('disconnected')
      return Buffer.from('frame')
    }})
    await assert.rejects(recordFilm(options, dependencies), /crashed|disconnected/)
    assert.equal(calls.browserClosed, 1)
    assert.equal(didReportSuccess(calls), false)
  })
}

for (const settings of [{readinessError: true}, {screenshotError: true}]) {
  test(`thrown ${Object.keys(settings)[0]} still closes the browser`, async () => {
    const {options, dependencies, calls} = harness(settings)
    await assert.rejects(recordFilm(options, dependencies), /planted/)
    assert.equal(calls.browserClosed, 1)
    assert.equal(didReportSuccess(calls), false)
  })
}

test('bounded runtime interrupts a stalled encoder and escalates cleanup', async () => {
  const {options, dependencies, calls} = harness({hangEncoder: true, ignoreTerm: true})
  await assert.rejects(recordFilm({...options, timeoutMs: 20}, dependencies), /runtime exceeded/)
  assert.deepEqual(calls.signals, ['SIGTERM', 'SIGKILL'])
  assert.equal(calls.browserClosed, 1)
  assert.equal(didReportSuccess(calls), false)
})

test('bounded runtime interrupts recorder readiness before encoder creation', async () => {
  const {options, dependencies, calls} = harness({hangReadiness: true})
  await assert.rejects(recordFilm({...options, timeoutMs: 20}, dependencies), /runtime exceeded/)
  assert.equal(calls.spawned, 0)
  assert.equal(calls.browserClosed, 1)
})

test('a browser launched after cancellation is also closed', async () => {
  const {options, dependencies, calls, browser} = harness()
  let completeLaunch
  const launching = new Promise((resolve) => { completeLaunch = resolve })
  dependencies.launchBrowser = () => launching
  await assert.rejects(recordFilm({...options, timeoutMs: 10}, dependencies), /runtime exceeded/)
  completeLaunch(browser)
  await new Promise((resolve) => setImmediate(resolve))
  assert.equal(calls.browserClosed, 1)
  assert.equal(calls.spawned, 0)
})

test('attended cancellation during capture terminates the encoder', async () => {
  const controller = new AbortController()
  const {options, dependencies, calls} = harness({screenshot: () => {
    controller.abort()
    return Buffer.from('frame')
  }})
  await assert.rejects(recordFilm({...options, signal: controller.signal}, dependencies), /cancelled/)
  assert.equal(calls.browserClosed, 1)
  assert.deepEqual(calls.signals, ['SIGTERM'])
})

test('cancellation during browser cleanup cannot report success', async () => {
  const controller = new AbortController()
  const {options, dependencies, calls, browser} = harness()
  const close = browser.close
  browser.close = async () => {
    controller.abort()
    await close()
  }
  await assert.rejects(recordFilm({...options, signal: controller.signal}, dependencies), /cancelled/)
  assert.equal(calls.browserClosed, 1)
  assert.equal(didReportSuccess(calls), false)
})

test('cancellation inside browser launch still closes the returned browser', async () => {
  const controller = new AbortController()
  const {options, dependencies, calls, browser} = harness()
  dependencies.launchBrowser = () => {
    controller.abort()
    return Promise.resolve(browser)
  }
  await assert.rejects(recordFilm({...options, signal: controller.signal}, dependencies), /cancelled/)
  await new Promise((resolve) => setImmediate(resolve))
  assert.equal(calls.browserClosed, 1)
  assert.equal(didReportSuccess(calls), false)
})

for (const settings of [{closeError: true}, {hangClose: true}]) {
  test(`${Object.keys(settings)[0]} cannot report recording success`, async () => {
    const {options, dependencies, calls} = harness(settings)
    await assert.rejects(recordFilm(options, dependencies), /cleanup/)
    assert.equal(didReportSuccess(calls), false)
  })
}

for (const duration of [-1, 0, NaN, Infinity, 1801]) {
  test(`invalid duration ${duration} cannot create an encoder`, async () => {
    const {options, dependencies, calls} = harness({duration})
    await assert.rejects(recordFilm(options, dependencies), /invalid recording duration/)
    assert.equal(calls.spawned, 0)
    assert.equal(calls.browserClosed, 1)
  })
}
