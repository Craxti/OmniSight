import { expect, test } from '@playwright/test'
import { inventoryTable, login, relationsTable } from './helpers'

const CIS = [
  { name: 'demo-hub', type: 'Application', hostname: 'demo-hub' },
  { name: 'demo-hub-db', type: 'Database', hostname: 'demo-hub-db' },
  { name: 'demo-hub-srv', type: 'Server', hostname: 'demo-hub-srv' },
  { name: 'demo-hub-vm', type: 'Virtual Machine', hostname: 'demo-hub-vm' },
  { name: 'demo-hub-queue', type: 'Queue', hostname: 'demo-hub-queue' },
  { name: 'demo-hub-net', type: 'Network Element', hostname: 'demo-hub-net' },
  { name: 'demo-hub-ext', type: 'External Service', hostname: 'demo-hub-ext' },
  { name: 'demo-hub-backup', type: 'Technical Component', hostname: 'demo-hub-backup' },
] as const

const RELATIONS = [
  { target: 'demo-hub-db', type: 'depends_on' },
  { target: 'demo-hub-srv', type: 'hosted_on' },
  { target: 'demo-hub-vm', type: 'part_of' },
  { target: 'demo-hub-queue', type: 'uses' },
  { target: 'demo-hub-net', type: 'linked_to' },
  { target: 'demo-hub-ext', type: 'affects' },
  { target: 'demo-hub-backup', type: 'reserves' },
] as const

test('setup demo-hub with all relation types via UI', async ({ page }) => {
  const suffix = Date.now()
  const cis = CIS.map((ci) => ({ ...ci, name: `${ci.name}-${suffix}`, hostname: `${ci.hostname}-${suffix}` }))
  const rootName = cis[0].name
  const relationTargets = cis.slice(1).map((c, idx) => ({ target: c.name, type: RELATIONS[idx].type }))

  await login(page)
  try {
    await page.goto('/inventory')

    for (const ci of cis) {
      await page.getByTestId('ci-create').click()
      const modal = page.getByRole('dialog')
      await modal.locator('#ci-name').fill(ci.name)
      await modal.locator('select').nth(0).selectOption(ci.type)
      await modal.getByTestId('ci-environment').fill('production')
      await modal.locator('#ci-owner').fill('ops')
      await modal.locator('#ci-ext-hostname').fill(ci.hostname)
      await modal.getByTestId('ci-submit').click()
      await expect(page.getByRole('link', { name: ci.name, exact: true })).toBeVisible({ timeout: 15_000 })
    }

    await page.goto('/relations')
    for (const rel of relationTargets) {
      await page.getByTestId('relation-create').click()
      const modal = page.getByRole('dialog')
      await modal.locator('#rel-source').selectOption({ label: rootName })
      await modal.locator('#rel-target').selectOption({ label: rel.target })
      await modal.locator('select').nth(2).selectOption(rel.type)
      await modal.getByTestId('relation-submit').click()
      const table = relationsTable(page)
      await expect(table).toContainText(rootName, { timeout: 15_000 })
      await expect(table).toContainText(rel.target, { timeout: 15_000 })
    }

    await page.goto('/graph')
    await page.getByTestId('graph-root-search').click()
    await page.getByTestId('graph-root-search').fill(rootName)
    await page.getByTestId(/graph-root-option-/).filter({ hasText: rootName }).first().click()
    await page.locator('#graph-depth').fill('2')
    await expect(page.locator('.react-flow__node')).toHaveCount(8, { timeout: 20_000 })
    await expect(page.locator('.react-flow__edge')).toHaveCount(7, { timeout: 20_000 })
  } finally {
    await page.goto('/relations')
    for (const rel of relationTargets) {
      const row = relationsTable(page)
        .locator('.virtual-table-row:not(.virtual-table-width-sizer)')
        .filter({ hasText: rootName })
        .filter({ hasText: rel.target })
      if (await row.count()) {
        await row.first().getByTestId('relation-delete').click()
      }
    }

    await page.goto('/inventory')
    for (const ci of cis) {
      await page.getByTestId('inventory-filter-q').fill(ci.name)
      const row = inventoryTable(page)
        .locator('.virtual-table-row:not(.virtual-table-width-sizer)')
        .filter({ hasText: ci.name })
      if (await row.count()) {
        await row.first().getByTestId('ci-delete').click()
      }
    }
  }
})
