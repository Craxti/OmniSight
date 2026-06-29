import { expect, type Page } from '@playwright/test'
import type { AlertRow } from '../src/shared/constants'

async function submitAutodiscoverScan(page: Page) {
  await expect(page.getByTestId('autodiscover-scan')).toBeEnabled({ timeout: 15_000 })
  const responsePromise = page.waitForResponse(
    (res) => res.url().includes('/autodiscover/scan') && res.request().method() === 'POST',
    { timeout: 120_000 },
  )
  await page.getByTestId('autodiscover-scan').click()
  const response = await responsePromise
  const body = await response.text()
  expect(response.ok(), `autodiscover scan failed (${response.status()}): ${body.slice(0, 500)}`).toBeTruthy()
}

async function waitAutodiscoverDialogClosed(page: Page) {
  const apply = page.getByTestId('autodiscover-apply')
  if (await apply.isVisible({ timeout: 3_000 }).catch(() => false)) {
    await apply.click()
  }
  await expect(page.getByRole('dialog')).toBeHidden({ timeout: 30_000 })
}

async function runAutodiscoverScanUi(page: Page, serverCiId: number) {
  await expect(page.getByTestId(`autodiscover-server-${serverCiId}`)).toBeVisible({ timeout: 15_000 })
  await page.getByTestId(`autodiscover-server-${serverCiId}`).check()
  await submitAutodiscoverScan(page)
  await waitAutodiscoverDialogClosed(page)
}

export async function runAutodiscoverInventoryUi(
  page: Page,
  opts: { serverCiId: number; expectedIp: string; appName?: string },
) {
  const appName = opts.appName ?? 'demo-app'

  await page.goto('/inventory')
  await page.getByTestId('inventory-autodiscover').click()
  await expect(page.getByRole('dialog')).toBeVisible()

  await runAutodiscoverScanUi(page, opts.serverCiId)

  await page.goto('/inventory')
  await page.getByRole('link', { name: appName }).click()
  await expect(page.locator('body')).toContainText(opts.expectedIp, { timeout: 10_000 })
}

export async function login(page: Page) {
  await page.goto('/login')
  await page.locator('#login-email').fill('admin@omnisight.local')
  await page.locator('#login-password').fill('admin123')
  await page.getByTestId('login-submit').click()
  await page.waitForURL((url) => !url.pathname.includes('/login'))
}

export async function createCi(
  page: Page,
  opts: { name: string; owner?: string; hostname?: string },
) {
  await page.getByTestId('ci-create').click()
  await page.locator('#ci-name').fill(opts.name)
  await page.locator('#ci-owner').fill(opts.owner ?? 'e2e')
  if (opts.hostname) {
    await page.locator('#ci-ext-hostname').fill(opts.hostname)
  }
  await page.getByTestId('ci-submit').click()
  await expect(page.getByRole('link', { name: opts.name })).toBeVisible({ timeout: 15_000 })
}

export async function deleteCiByName(page: Page, name: string) {
  await page.goto('/inventory')
  await page.getByTestId('inventory-filter-q').fill(name)
  const row = page.locator('tbody tr').filter({ hasText: name })
  await expect(row).toHaveCount(1, { timeout: 10_000 })
  await row.getByTestId('ci-delete').click()
  await expect(row).toHaveCount(0, { timeout: 10_000 })
}

export async function deleteCiByNameIfExists(page: Page, name: string) {
  try {
    await page.goto('/inventory')
    const activeTab = page.getByRole('button', { name: /Активные|Active/i })
    if (await activeTab.count()) await activeTab.first().click()
    const filter = page.getByTestId('inventory-filter-q')
    if (!(await filter.count())) return
    await filter.fill(name)
    const row = page.locator('tbody tr').filter({ hasText: name })
    if (!(await row.count())) return
    await row.first().getByTestId('ci-delete').click()
  } catch {
    // Best-effort cleanup in finally; do not mask the original test error.
  }
}

export async function createRelation(page: Page, sourceName: string, targetName: string) {
  await page.goto('/relations')
  await page.getByTestId('relation-create').click()
  await page.locator('#rel-source').selectOption({ label: sourceName })
  await page.locator('#rel-target').selectOption({ label: targetName })
  await page.getByTestId('relation-submit').click()
  await expect(page.locator('table.data-table')).toContainText(sourceName, { timeout: 10_000 })
}

export async function deleteRelation(page: Page, sourceName: string, targetName: string) {
  await page.goto('/relations')
  const row = page.locator('tbody tr').filter({ hasText: sourceName }).filter({ hasText: targetName })
  await expect(row).toHaveCount(1, { timeout: 10_000 })
  await row.getByTestId('relation-delete').click()
  await expect(row).toHaveCount(0, { timeout: 10_000 })
}

export async function deleteRelationIfExists(page: Page, sourceName: string, targetName: string) {
  try {
    await page.goto('/relations')
    const row = page.locator('tbody tr').filter({ hasText: sourceName }).filter({ hasText: targetName })
    if (!(await row.count())) return
    await row.first().getByTestId('relation-delete').click()
  } catch {
    // Best-effort cleanup in finally; do not mask the original test error.
  }
}

export async function openGraphForCi(page: Page, ciName: string, minNodes = 2) {
  await page.goto('/graph')
  await page.getByTestId('graph-root-search').click()
  await page.getByTestId('graph-root-search').fill(ciName)
  await page.getByRole('button', { name: new RegExp(ciName) }).click()
  await expect(page.locator('.react-flow__node')).toHaveCount(minNodes, { timeout: 20_000 })
}

export async function fillCorrelationAlerts(page: Page, alerts: readonly AlertRow[]) {
  await page.goto('/correlation')
  for (let i = 0; i < alerts.length; i++) {
    if (i > 0) {
      await page.getByRole('button', { name: /Строка|Row/i }).click()
    }
    const row = alerts[i]
    for (const [field, value] of Object.entries(row)) {
      if (value) {
        await page.getByTestId(`correlation-alert-${i}-${field}`).fill(value)
      }
    }
  }
}

export async function runCorrelationIngest(page: Page, expectChainRelated: boolean) {
  const responsePromise = page.waitForResponse(
    (res) => res.url().includes('/correlation/ingest') && res.request().method() === 'POST',
    { timeout: 60_000 },
  )
  await page.getByTestId('correlation-ingest').click()
  const response = await responsePromise
  const body = await response.text()
  expect(response.ok(), `correlation ingest failed (${response.status()}): ${body.slice(0, 500)}`).toBeTruthy()
  const chainEl = page.getByTestId('correlation-chain-related')
  await expect(chainEl).toBeVisible({ timeout: 20_000 })
  await expect(chainEl).toHaveText(String(expectChainRelated))
}

export async function runAutodiscoverGraphUi(page: Page, opts: { serverCiId: number; expectedIp: string }) {
  await page.getByTestId('graph-autodiscover').click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await runAutodiscoverScanUi(page, opts.serverCiId)
}
