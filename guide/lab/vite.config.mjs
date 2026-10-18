import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'

const root = dirname(fileURLToPath(import.meta.url))

// Relative base: the built page is served from the site root (/) and must not hard-code a prefix.
// Three pages: the shop (index), the Hangar index, and the briefing room.
export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    target: 'es2022',
    assetsInlineLimit: 0,
    chunkSizeWarningLimit: 2500,
    rollupOptions: {
      input: {
        index: resolve(root, 'index.html'),
        hangar: resolve(root, 'hangar.html'),
        briefing: resolve(root, 'briefing.html'),
      },
    },
  },
  server: { host: '127.0.0.1', port: 5173 },
})
