import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Keep the development server local; production uses the Nginx image.
  server: { host: '127.0.0.1', port: 3000 },
})
