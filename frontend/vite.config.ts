// File: frontend/vite.config.ts

import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { fileURLToPath, URL } from 'node:url' // <-- IMPORT THIS

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  resolve: {
    alias: {
      // This is the correct, modern way to resolve a path alias.
      $lib: fileURLToPath(new URL('./src/lib', import.meta.url))
    }
  }
})