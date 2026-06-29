import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('@xyflow')) return 'vendor-graph'
          if (id.includes('recharts')) return 'vendor-charts'
          if (id.includes('xlsx')) return 'vendor-xlsx'
          if (id.includes('@tanstack/react-query')) return 'vendor-query'
          if (id.includes('react-router') || id.includes('react-dom') || /[/\\]react[/\\]/.test(id)) {
            return 'vendor-react'
          }
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/test/setup.ts'],
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary'],
      exclude: [
        'src/**/*.test.{ts,tsx}',
        'src/test/**',
        'src/shared/api/generated/**',
        'src/main.tsx',
        'src/App.tsx',
      ],
      thresholds: {
        lines: 65,
        statements: 63,
        functions: 50,
        branches: 48,
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
