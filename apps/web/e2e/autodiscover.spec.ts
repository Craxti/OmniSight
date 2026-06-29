import { expect, test } from '@playwright/test'
import {
  API_BASE,
  apiLogin,
  ensureAutodiscoverDemoFixture,
  login,
  runAutodiscoverGraphUi,
  runAutodiscoverInventoryUi,
} from './helpers'
import { paths as V1Paths } from '../src/shared/api/paths'
import { unwrapV1Ci } from '../src/shared/api/v1Envelope'

test.describe('Autodiscover UI walkthrough', () => {
  test('inventory: scan sync server and apply discovered ip', async ({ page, request }) => {
    const fixture = await ensureAutodiscoverDemoFixture(request)

    await login(page)
    await runAutodiscoverInventoryUi(page, {
      serverCiId: fixture.srvId,
      expectedIp: fixture.expectedIp,
    })

    const token = await apiLogin(request)
    const appRes = await request.get(`${API_BASE}${V1Paths.ci.detail(fixture.appId)}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(appRes.ok()).toBeTruthy()
    const app = unwrapV1Ci<{ external_ids?: Record<string, string> }>(await appRes.json())
    expect(app.external_ids?.ip).toBe(fixture.expectedIp)
  })

  test('graph: autodiscover from map sidebar', async ({ page, request }) => {
    const fixture = await ensureAutodiscoverDemoFixture(request)

    await login(page)
    await page.goto('/graph')
    await page.getByTestId('graph-root-search').click()
    await page.getByTestId('graph-root-search').fill('demo-app')
    await page.getByTestId(/graph-root-option-/).filter({ hasText: 'demo-app' }).first().click()

    await runAutodiscoverGraphUi(page, {
      serverCiId: fixture.srvId,
      expectedIp: fixture.expectedIp,
    })
  })
})
