import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const API_URL = process.env.VITE_API_URL
const isLocalAPI = API_URL === '/api'

export default defineConfig({
    plugins: [react()],
    server: {
    ...(isLocalAPI
      ? {
          proxy: {
            '/api': {
              target: 'http://127.0.0.1:8000',
              changeOrigin: true,
              secure: false,
            },
          },
        }
      : {}),
  },
})