import { chromium } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const webDir = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(webDir, '..', '..', '..')
const outDir = path.join(root, 'docs', 'product-passport', 'screenshots')
const baseUrl = 'http://127.0.0.1:5173'
const apiUrl = 'http://127.0.0.1:8000'

const pages = [
  { name: '01-login', url: '/login', auth: false },
  { name: '02-dashboard', url: '/', auth: true },
  { name: '03-inventory', url: '/inventory', auth: true },
  { name: '04-relations', url: '/relations', auth: true },
  { name: '05-graph', url: '/graph', auth: true, waitMs: 3000 },
  { name: '06-correlation', url: '/correlation', auth: true },
  { name: '07-audit', url: '/audit', auth: true },
  { name: '08-settings', url: '/settings', auth: true },
]

await mkdir(outDir, { recursive: true })

async function login(apiUrl) {
  const loginRes = await fetch(`${apiUrl}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'admin@omnisight.local', password: 'admin123' }),
  })
  if (!loginRes.ok) throw new Error(`login failed: ${loginRes.status}`)
  const body = await loginRes.json()
  return body.session.access_token
}

const token = await login(apiUrl)

const browser = await chromium.launch()

const guestContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'ru-RU' })
const guestPage = await guestContext.newPage()
await guestPage.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' })
await guestPage.screenshot({ path: path.join(outDir, '01-login.png'), fullPage: false })
console.log('saved 01-login')
await guestContext.close()

const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'ru-RU' })
await context.addInitScript((t) => localStorage.setItem('omnisight_token', t), token)
const page = await context.newPage()

for (const item of pages.filter((p) => p.auth)) {
  await page.goto(`${baseUrl}${item.url}`, { waitUntil: 'networkidle' })
  await page.waitForSelector('text=OmniSight', { timeout: 10000 })
  if (item.waitMs) await page.waitForTimeout(item.waitMs)
  await page.screenshot({ path: path.join(outDir, `${item.name}.png`), fullPage: false })
  console.log('saved', item.name)
}

await page.goto('http://127.0.0.1:8090/', { waitUntil: 'networkidle' })
await page.waitForTimeout(500)
await page.screenshot({ path: path.join(outDir, '09-demo-ce.png'), fullPage: false })
console.log('saved 09-demo-ce')

await page.getByRole('button', { name: /Отправить 4 алерта/ }).click()
await page.waitForTimeout(2000)
await page.screenshot({ path: path.join(outDir, '10-demo-ce-result.png'), fullPage: false })
console.log('saved 10-demo-ce-result')

await browser.close()
console.log('done', outDir)
