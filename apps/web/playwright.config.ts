import { defineConfig, devices } from '@playwright/test'

const E2E_API_PORT = process.env.E2E_API_PORT ?? '8001'
const E2E_API_URL = `http://127.0.0.1:${E2E_API_PORT}`
const E2E_WEB_PORT = process.env.E2E_WEB_PORT ?? '5174'
const E2E_WEB_URL = `http://127.0.0.1:${E2E_WEB_PORT}`

export default defineConfig({
  testDir: './e2e',
  timeout: 120_000,
  retries: 0,
  workers: 1,
  use: {
    baseURL: E2E_WEB_URL,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: process.env.E2E_SKIP_WEBSERVER
    ? undefined
    : [
        {
          command: 'python ../api/scripts/run_e2e_server.py',
          url: `${E2E_API_URL}/health`,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: {
            ...process.env,
            E2E_API_PORT,
            DATABASE_URL:
              process.env.DATABASE_URL ??
              'postgresql+psycopg2://postgres:7002@localhost:5432/omnisight',
            RATE_LIMIT_ENABLED: 'false',
          },
        },
        {
          command: `npm run dev -- --host 127.0.0.1 --port ${E2E_WEB_PORT}`,
          url: E2E_WEB_URL,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: {
            ...process.env,
            VITE_API_PROXY: E2E_API_URL,
          },
        },
      ],
})
