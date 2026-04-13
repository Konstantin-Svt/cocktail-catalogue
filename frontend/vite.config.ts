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
            target: 'https://cocktail-catalogue-dev.onrender.com',
            changeOrigin: true,
            secure: false,
            rewrite: (path) => path.replace(/^\/api/, '/api'),
          },
        }
      : undefined,
    },
  }
})