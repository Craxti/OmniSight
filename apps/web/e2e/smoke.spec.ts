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

test.describe('OmniSight smoke', () => {
  test('login and open inventory', async ({ page }) => {
    await login(page)
    await page.goto('/inventory')
    await expect(page.getByTestId('inventory-page')).toBeVisible({ timeout: 10_000 })
  })

  test('create CI, relation and open graph', async ({ page }) => {
    const suffix = Date.now()
    const nameA = `e2e-a-${suffix}`
    const nameB = `e2e-b-${suffix}`

    await login(page)
    try {
      await page.goto('/inventory')
      await createCi(page, { name: nameA })
      await createCi(page, { name: nameB })

      await createRelation(page, nameA, nameB)
      await openGraphForCi(page, nameA, 2)
    } finally {
      await deleteRelationIfExists(page, nameA, nameB)
      await deleteCiByNameIfExists(page, nameA)
      await deleteCiByNameIfExists(page, nameB)
    }
  })

  test('correlation manual ingest', async ({ page }) => {
    await login(page)
    await fillCorrelationAlerts(page, DEMO_CORRELATION_ALERTS)
    await runCorrelationIngest(page, true)
  })
})
