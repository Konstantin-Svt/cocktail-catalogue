import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  const useProxy = env.VITE_API_URL === '/api'

  return {
    plugins: [react()],
    server: {
      proxy: useProxy
        ? {
          '/api': {
            target: 'http://127.0.0.1:8000',
            changeOrigin: true,
            secure: false,
            rewrite: (path) => path.replace(/^\/api/, '/api'),
          },
        }
      : undefined,
    },
  }
})