// Adapted from AirsupHQ/airsup-lab tools/record.mjs (MIT); see NOTICE.
// Changes: takes the served lab page as an argument (no dev-server default), one film ("canard"), 60 fps default, GPU flags plus an opt-in software path, an out-of-tree friendly output dir.
/**
 * Render the canard-chapter film to a 1080p MP4, frame by frame, so it never drops a frame.
 *
 *   npm --prefix guide/lab run record -- canard <out.mp4> [fps] <url>
 *
 * <url> is the served site's lab page, e.g. http://127.0.0.1:8800/lab/ (build a site with
 * `python -m guide.build_site --models <longez.glb> --out <dir>` and serve <dir> with `python3 -m http.server <port>`).
 * fps defaults to 60. Set LAB_SWIFTSHADER=1 to allow the software renderer (slow; for machines without a GPU).
 * Needs Playwright's Chromium (`npx playwright install chromium`, shared with the Python tests) and ffmpeg on the PATH.
 */
import { chromium } from 'playwright'
import { spawn } from 'node:child_process'
import { mkdirSync } from 'node:fs'
import { dirname } from 'node:path'

const [film, out, fps = '60', url] = process.argv.slice(2)
if (film !== 'canard' || !out || !url) {
  console.error('usage: record canard <out.mp4> [fps] <url of the served /lab/ page>')
  process.exit(2)
}
mkdirSync(dirname(out), { recursive: true })
const gpu = ['--enable-gpu', '--ignore-gpu-blocklist', '--use-angle=metal']
const soft = ['--use-gl=swiftshader', '--enable-unsafe-swiftshader']
const browser = await chromium.launch({ args: process.env.LAB_SWIFTSHADER === '1' ? soft : gpu })
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })
page.on('pageerror', (e) => console.error('page error:', e.message))
await page.goto(`${url}${url.includes('?') ? '&' : '?'}rec=1`)
await page.waitForFunction(() => window.__rec, null, { timeout: 180000 })
const duration = await page.evaluate((t) => window.__rec.start(t), film)
const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'inherit'] })
const n = Math.ceil(duration * Number(fps))
for (let i = 0; i < n; i++) {
  const r = await page.evaluate((dt) => window.__rec.frame(dt), 1 / Number(fps))
  const shot = await page.screenshot({ type: 'jpeg', quality: 95 })
  if (!ff.stdin.write(shot)) await new Promise((res) => ff.stdin.once('drain', res))
  if (i % 300 === 0) console.log(`frame ${i} / ${n}`)
  if (!r.active && i > 10) break
}
ff.stdin.end()
await new Promise((res) => ff.on('close', res))
await browser.close()
console.log('wrote', out)
