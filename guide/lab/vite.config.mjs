import { defineConfig } from 'vite'

// Relative base: the built page is served from /lab/ and must not hard-code that prefix.
export default defineConfig({
  base: './',
  build: { outDir: 'dist', target: 'es2022', assetsInlineLimit: 0, chunkSizeWarningLimit: 2500 },
  server: { host: '127.0.0.1', port: 5173 },
})
