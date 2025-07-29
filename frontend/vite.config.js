import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: '', // Puts assets in the root of dist
    rollupOptions: {
      input: {
        main: './index.html'
      }
    }
  },
  server: {
    // Proxy API requests to the local backend server during development
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});