import { expect, test } from '@playwright/test'
import {
  DEMO_CORRELATION_ALERTS,
  createCi,
  createRelation,
  deleteCiByNameIfExists,
  deleteRelationIfExists,
  fillCorrelationAlerts,
  login,
  openGraphForCi,
  runCorrelationIngest,
} from './helpers'

test.describe('OmniSight full tab flow', () => {
  test('each tab: create data, relations, graph, correlation ok/fail, cleanup', async ({ page }) => {
    test.setTimeout(300_000)

    const suffix = Date.now()
    const nameA = `e2e-a-${suffix}`
    const nameB = `e2e-b-${suffix}`
    const nameFailA = `e2e-fail-a-${suffix}`
    const nameFailB = `e2e-fail-b-${suffix}`
    const hostFailA = `e2e-fail-host-a-${suffix}`
    const hostFailB = `e2e-fail-host-b-${suffix}`
    const typeName = `e2e-type-${suffix}`

    await login(page)
    try {
      // Dashboard
      await page.goto('/')
      await expect(page.getByRole('heading', { name: /Обзор|Dashboard/i })).toBeVisible()
      await expect(page.locator('.stat-card-value').first()).toBeVisible({ timeout: 10_000 })

      // Inventory — create CIs for relation + graph + failed correlation
      await page.goto('/inventory')
      await expect(page.getByTestId('inventory-page')).toBeVisible()
      await createCi(page, { name: nameA, hostname: `e2e-host-a-${suffix}` })
      await createCi(page, { name: nameB, hostname: `e2e-host-b-${suffix}` })
      await createCi(page, { name: nameFailA, hostname: hostFailA })
      await createCi(page, { name: nameFailB, hostname: hostFailB })

      // Relations — link A → B and validate model
      await createRelation(page, nameA, nameB)
      await page.getByRole('button', { name: /Проверить целостность|Validate/i }).click()
      await expect(page.locator('.card').filter({ hasText: /Модель корректна|Model is valid|Проблемы|Issues/i })).toBeVisible({
        timeout: 10_000,
      })

      // Graph — verify nodes from root A
      await openGraphForCi(page, nameA, 2)
      await expect(page.locator('.react-flow__edge')).toHaveCount(1, { timeout: 10_000 })

      // Correlation — success on demo seed chain
      await fillCorrelationAlerts(page, DEMO_CORRELATION_ALERTS)
      await runCorrelationIngest(page, true)
      await expect(page.locator('.react-flow__node').first()).toBeVisible({ timeout: 15_000 })

      // Correlation — failure: two unrelated CIs (no depends_on between them)
      await fillCorrelationAlerts(page, [{ hostname: hostFailA }, { hostname: hostFailB }])
      await runCorrelationIngest(page, false)

      // Audit — entries from this session
      await page.goto('/audit')
      await expect(page.getByRole('heading', { name: /Аудит|Audit/i })).toBeVisible()
      await page.locator('select[aria-label="Entity type"]').selectOption('ci')
      await page.locator('select[aria-label="Action"]').selectOption('create')
      await expect(page.locator('table.data-table tbody tr').filter({ hasText: nameA })).toBeVisible({ timeout: 10_000 })

      // Settings — create temporary CI type, then remove it
      await page.goto('/settings')
      await expect(page.getByRole('heading', { name: /Настройки|Settings/i })).toBeVisible()
      await page.getByRole('button', { name: /Новый тип|New type/i }).click()
      await page.locator('input.input').first().fill(typeName)
      await page.getByRole('button', { name: /Сохранить|Save/i }).click()
      await expect(page.getByText(typeName)).toBeVisible({ timeout: 10_000 })

      await page.getByRole('tab', { name: /Интеграция API|API integration/i }).click()
      await expect(page.getByText(/correlation\/ingest|ingest/i).first()).toBeVisible()
    } finally {
      await deleteRelationIfExists(page, nameA, nameB)
      await deleteCiByNameIfExists(page, nameA)
      await deleteCiByNameIfExists(page, nameB)
      await deleteCiByNameIfExists(page, nameFailA)
      await deleteCiByNameIfExists(page, nameFailB)

      await page.goto('/settings')
      const typeCard = page.locator('.group').filter({ hasText: typeName })
      if (await typeCard.count()) {
        await typeCard.getByLabel('Delete').click()
        await expect(page.getByText(typeName)).toHaveCount(0, { timeout: 10_000 })
      }
    }

    // Post-cleanup: CIs removed from active inventory
    await login(page)
    await page.goto('/inventory')
    await expect(page.getByTestId('inventory-page')).toBeVisible({ timeout: 15_000 })
    await page.getByTestId('inventory-filter-q').fill(nameA)
    await expect(page.getByRole('link', { name: nameA })).toHaveCount(0, { timeout: 10_000 })
    await page.getByTestId('inventory-filter-q').fill(nameB)
    await expect(page.getByRole('link', { name: nameB })).toHaveCount(0, { timeout: 10_000 })
  })
})
