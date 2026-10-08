import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // DEV_API_TARGET is the deployed app link; `npm run dev` forwards /api to it.
  const { DEV_API_TARGET } = loadEnv(mode, '.', '');
  return {
    plugins: [react()],
    server: {
      proxy: DEV_API_TARGET ? { '/api': { target: DEV_API_TARGET, changeOrigin: true } } : undefined,
    },
  };
});
