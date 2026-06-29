import { expect, test } from '@playwright/test'
import {
  DEMO_CORRELATION_ALERTS,
  apiLogin,
  auditTable,
  createCi,
  createRelation,
  deleteCiByNameApi,
  deleteRelationByNamesApi,
  deleteTypeByNameApi,
  fillCorrelationAlerts,
  login,
  openGraphForCi,
  runCorrelationIngest,
  validateRelationsModel,
} from './helpers'

test.describe('OmniSight full tab flow', () => {
  test('each tab: create data, relations, graph, correlation ok/fail, cleanup', async ({ page, request }) => {
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
    let token = await apiLogin(request)
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
      await validateRelationsModel(page)

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
      await page.getByLabel(/Тип сущности|Entity type/i).selectOption('ci')
      await page.getByLabel(/Действие|Action/i).selectOption('create')
      await expect(auditTable(page)).toContainText(nameA, { timeout: 10_000 })

      // Settings — create temporary CI type, then remove it
      await page.goto('/settings')
      await expect(page.getByRole('heading', { name: /Настройки|Settings/i })).toBeVisible()
      await page.getByRole('button', { name: /^(Новый тип|New type)$/i }).click()
      await page.locator('input.input').first().fill(typeName)
      await page.getByRole('button', { name: /Сохранить|Save/i }).click()
      await expect(page.getByText(typeName)).toBeVisible({ timeout: 10_000 })

      await page.getByRole('tab', { name: /Интеграция API|API integration/i }).click()
      await expect(page.getByText(/correlation\/ingest|ingest/i).first()).toBeVisible()
    } finally {
      if (!token) token = await apiLogin(request)
      await deleteRelationByNamesApi(request, token, nameA, nameB)
      for (const name of [nameA, nameB, nameFailA, nameFailB]) {
        await deleteCiByNameApi(request, token, name)
      }
      await deleteTypeByNameApi(request, token, typeName)
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
