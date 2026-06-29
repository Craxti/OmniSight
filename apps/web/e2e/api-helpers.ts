import { expect, type APIRequestContext } from '@playwright/test'
import { paths as V1Paths } from '../src/shared/api/paths'
import {
  unwrapV1Items,
} from '../src/shared/api/v1Envelope'

export const API_BASE = process.env.E2E_API_URL ?? 'http://127.0.0.1:8001'

export async function apiLogin(request: APIRequestContext): Promise<string> {
  const res = await request.post(`${API_BASE}${V1Paths.auth.login}`, {
    data: { email: 'admin@omnisight.local', password: 'admin123' },
  })
  expect(res.ok()).toBeTruthy()
  const body = await res.json()
  return body.session.access_token as string
}

export function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` }
}

type CiSummary = { id: number; name: string; external_ids?: Record<string, string> }

export async function deleteCiByNameApi(request: APIRequestContext, token: string, name: string) {
  try {
    const headers = authHeaders(token)
    const list = await request.get(
      `${API_BASE}${V1Paths.ci.list}?name=${encodeURIComponent(name)}`,
      { headers },
    )
    if (!list.ok()) return
    const items = unwrapV1Items<CiSummary>(await list.json())
    for (const ci of items.filter((item) => item.name === name)) {
      await request.delete(`${API_BASE}${V1Paths.ci.detail(ci.id)}`, { headers })
    }
  } catch {
    // Best-effort cleanup in finally; do not mask the original test error.
  }
}

export async function deleteTypeByNameApi(request: APIRequestContext, token: string, name: string) {
  try {
    const headers = authHeaders(token)
    const typesRes = await request.get(`${API_BASE}${V1Paths.ci.types}`, { headers })
    if (!typesRes.ok()) return
    const match = unwrapV1Items<{ id: number; name: string }>(await typesRes.json()).find(
      (t) => t.name === name,
    )
    if (!match) return
    await request.delete(`${API_BASE}${V1Paths.ci.type(match.id)}`, { headers })
  } catch {
    // Best-effort cleanup in finally; do not mask the original test error.
  }
}
