import { chromium } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const webDir = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(webDir, '..', '..', '..')
const outDir = path.join(root, 'docs', 'product-passport', 'screenshots')
const baseUrl = 'http://127.0.0.1:5173'
const apiUrl = 'http://127.0.0.1:8000'

const loginRes = await fetch(`${apiUrl}/api/v1/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@omnisight.local', password: 'admin123' }),
})
if (!loginRes.ok) throw new Error(`login failed: ${loginRes.status}`)
const { session } = await loginRes.json()
const token = session.access_token

const browser = await chromium.launch()
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'ru-RU' })
await context.addInitScript((t) => localStorage.setItem('omnisight_token', t), token)
const page = await context.newPage()

await page.goto(`${baseUrl}/graph?root=356`, { waitUntil: 'networkidle' })
await page.waitForTimeout(4000)
await page.screenshot({ path: path.join(outDir, '05b-graph-topology.png'), fullPage: false })
console.log('saved 05b-graph-topology')

await page.goto(`${baseUrl}/correlation`, { waitUntil: 'networkidle' })
await page.getByTestId('correlation-alert-0-hostname').fill('app-01')
await page.getByTestId('correlation-alert-0-ip').fill('10.0.0.5')
await page.getByTestId('correlation-alert-0-externalId').fill('ext-db-1')
await page.getByTestId('correlation-alert-0-serviceCode').fill('PAY')
await page.getByTestId('correlation-alert-0-applicationCode').fill('PAY-APP')
await page.getByTestId('correlation-ingest').click()
await page.waitForTimeout(2500)
await page.screenshot({ path: path.join(outDir, '06b-correlation-result.png'), fullPage: false })
console.log('saved 06b-correlation-result')

await browser.close()
