import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Relative base so the build works on GitHub Pages project sites and any sub-path.
export default defineConfig({
  base: './',
  plugins: [react()],
  build: {
    target: 'es2020',
    chunkSizeWarningLimit: 1600,
    rollupOptions: { output: { manualChunks(id: string) { if (id.includes('node_modules/three/')) return 'three'; if (/node_modules\/(@react-three|postprocessing|n8ao)/.test(id)) return 'r3f'; return undefined; } } },
  },
  test: { environment: 'jsdom', include: ['src/**/*.test.ts'] },
});
