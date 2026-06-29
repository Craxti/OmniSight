import { describe, expect, it } from 'vitest'
import { unwrapAuditItems, unwrapAuditList, unwrapDashboard } from '@/shared/api/v1Ops'

describe('V1Ops helpers', () => {
  const base = { api_version: 'v1' as const, schema_version: 'rsm-ops-v1' }

  it('unwraps dashboard envelope', () => {
    const dashboard = {
      total_ci: 1,
      total_relations: 2,
      by_status: {},
      by_type: {},
      model_health: { valid: true, issue_count: 0 },
      recent_audit: [],
    }
    expect(unwrapDashboard({ ...base, dashboard })).toEqual(dashboard)
  })

  it('unwraps audit list and entity envelopes', () => {
    const entry = {
      id: 1,
      entity_type: 'ci',
      entity_id: 2,
      action: 'update',
      user_email: 'a@b.c',
      old_value: null,
      new_value: null,
      created_at: null,
    }
    expect(
      unwrapAuditList({
        ...base,
        items: [entry],
        pagination: { page: 1, page_size: 25, total_items: 1, total_pages: 1 },
      }).total,
    ).toBe(1)
    expect(
      unwrapAuditItems({
        ...base,
        items: [entry],
        pagination: { page: 1, page_size: 1, total_items: 1, total_pages: 1 },
      }),
    ).toHaveLength(1)
  })
})
