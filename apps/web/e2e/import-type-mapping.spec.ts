import { expect, test } from '@playwright/test'
import {
  API_BASE,
  apiLogin,
  buildRandomImportFixture,
  cleanupImportFixture,
  login,
} from './helpers'
import { paths as V1Paths } from '../src/shared/api/paths'
import { unwrapV1Items } from '../src/shared/api/v1Envelope'

test.describe('CI import type mapping', () => {
  test('imports random data with new types, applies mapping, verifies and cleans up', async ({ page, request }) => {
    const suffix = `${Date.now()}`
    const fixture = buildRandomImportFixture(suffix)
    let token = ''

    await login(page)

    try {
      await page.goto('/inventory')
      await page.getByTestId('ci-import-file').setInputFiles({
        name: `import-${suffix}.json`,
        mimeType: 'application/json',
        buffer: fixture.jsonBuffer,
      })

      await expect(page.getByTestId('import-type-mapping-modal')).toBeVisible({ timeout: 15_000 })
      for (const typeName of fixture.typeNames) {
        await expect(page.getByTestId('import-type-mapping-modal')).toContainText(typeName)
      }

      await page.getByTestId('import-type-mapping-confirm').click()
      await expect(page.getByTestId('import-type-mapping-modal')).toBeHidden({ timeout: 20_000 })

      await expect(page.getByRole('dialog')).toContainText(/Создано|Created/i, { timeout: 15_000 })
      await expect(page.getByRole('dialog').locator('.text-emerald-300')).toHaveText('3')

      for (const name of fixture.ciNames) {
        await page.getByTestId('inventory-filter-q').fill(name)
        await expect(page.locator('tbody tr').filter({ hasText: name })).toHaveCount(1, { timeout: 15_000 })
      }

      token = await apiLogin(request)
      const headers = { Authorization: `Bearer ${token}` }
      const typesRes = await request.get(`${API_BASE}${V1Paths.ci.types}`, { headers })
      expect(typesRes.ok()).toBeTruthy()
      const typeNames = unwrapV1Items<{ name: string }>(await typesRes.json()).map((t) => t.name)
      for (const typeName of fixture.typeNames) {
        expect(typeNames).toContain(typeName)
      }

      await page.goto('/settings')
      for (const typeName of fixture.typeNames) {
        await expect(page.locator('body')).toContainText(typeName)
      }
    } finally {
      if (!token) token = await apiLogin(request)
      await cleanupImportFixture(request, token, fixture)
    }
  })
})
