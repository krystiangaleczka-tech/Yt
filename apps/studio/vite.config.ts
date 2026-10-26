import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  root: fileURLToPath(new URL('.', import.meta.url)),
  plugins: [react()],
  server: { allowedHosts: true, proxy: { '/api': { target: `http://127.0.0.1:${process.env.DOCOS_API_PORT || 8876}`, changeOrigin: true } } },
  build: { outDir: 'dist', emptyOutDir: true }
});
