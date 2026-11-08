import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// AI Studio 预览要求 dev server 监听 0.0.0.0:3000
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: false,
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});
