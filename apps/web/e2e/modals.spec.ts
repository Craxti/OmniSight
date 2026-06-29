import { expect, test } from '@playwright/test'
import { login } from './helpers'

test.describe('Modal smoke', () => {
  test('inventory create modal opens and closes', async ({ page }) => {
    await login(page)
    await page.goto('/inventory')
    await page.getByTestId('ci-create').click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.locator('#ci-name')).toBeVisible()
    await page.getByRole('button', { name: /Отмена|Cancel/i }).click()
    await expect(page.locator('#ci-name')).toBeHidden({ timeout: 5_000 })
  })

  test('relation create modal opens and closes', async ({ page }) => {
    await login(page)
    await page.goto('/relations')
    await page.getByTestId('relation-create').click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.locator('#rel-source')).toBeVisible()
    await expect(page.locator('#rel-target')).toBeVisible()
    await page.getByRole('button', { name: /Отмена|Cancel/i }).click()
    await expect(page.locator('#rel-source')).toBeHidden({ timeout: 5_000 })
  })

  test('export format modal opens and closes on relations', async ({ page }) => {
    await login(page)
    await page.goto('/relations')
    await page.getByTestId('entity-export').click()
    await expect(page.getByTestId('export-format-modal')).toBeVisible()
    await expect(page.getByTestId('export-format-select')).toHaveValue('xlsx')
    await page.getByTestId('export-format-select').selectOption('csv')
    await page.getByRole('button', { name: /Отмена|Cancel/i }).click()
    await expect(page.getByTestId('export-format-modal')).toBeHidden({ timeout: 5_000 })
  })
})
