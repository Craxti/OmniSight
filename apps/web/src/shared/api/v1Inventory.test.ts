import { describe, expect, it } from 'vitest'
import {
  toV1ListParams,
  unwrapCiList,
  unwrapCiTypeMutation,
  unwrapCiTypesList,
  unwrapDeleteResult,
  unwrapExportPayload,
  unwrapImportReport,
  unwrapRelationValidation,
  unwrapResourceSearch,
} from '@/shared/api/v1Inventory'

describe('V1Inventory helpers', () => {
  it('maps skip/limit to page/page_size', () => {
    expect(toV1ListParams({ skip: 0, limit: 50 })).toEqual({ page: 1, page_size: 50 })
    expect(toV1ListParams({ skip: 50, limit: 50 })).toEqual({ page: 2, page_size: 50 })
    expect(toV1ListParams({ limit: 100, q: 'db' })).toEqual({ page: 1, page_size: 100, q: 'db' })
  })

  it('caps page_size at 500', () => {
    expect(toV1ListParams({ limit: 9999 }).page_size).toBe(500)
  })

const sampleCi = { id: 1, name: 'a', type: null, type_id: 1, status: 'active', attributes: {}, external_ids: {} }

  it('unwraps CI list envelope', () => {
    const body = unwrapCiList({
      api_version: 'v1',
      schema_version: 'rsm-inventory-v1',
      items: [sampleCi],
      pagination: { page: 1, page_size: 50, total_items: 10, total_pages: 1 },
    })
    expect(body.total).toBe(10)
    expect(body.items).toHaveLength(1)
  })

  it('unwraps resource search envelope', () => {
    expect(
      unwrapResourceSearch({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        search: { items: [sampleCi], total: 1, match_mode: 'exact' },
      }).total,
    ).toBe(1)
  })

  it('unwraps validation and delete envelopes', () => {
    expect(
      unwrapRelationValidation({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        validation: { valid: true, issues: [], issue_count: 0 },
      }).valid,
    ).toBe(true)
    expect(
      unwrapDeleteResult({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        result: { ok: true },
      }),
    ).toEqual({ ok: true })
  })

  it('unwraps CI types list and mutation envelopes', () => {
    expect(
      unwrapCiTypesList({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        items: [{ id: 1, name: 'Server', is_official: true }],
        pagination: { page: 1, page_size: 1, total_items: 1, total_pages: 1 },
      }),
    ).toEqual([{ id: 1, name: 'Server', is_official: true }])
    expect(
      unwrapCiTypeMutation({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        ci_type: { id: 2, name: 'Custom' },
      }).name,
    ).toBe('Custom')
  })

  it('unwraps import report and export payload envelopes', () => {
    expect(
      unwrapImportReport({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        report: { created: 2, updated: 0, skipped: 1, errors: [] },
      }),
    ).toEqual({ created: 2, updated: 0, skipped: 1, errors: [] })
    expect(
      unwrapExportPayload<{ needs_mapping: boolean }>({
        api_version: 'v1',
        schema_version: 'rsm-inventory-v1',
        export: { needs_mapping: true },
      }),
    ).toEqual({ needs_mapping: true })
  })
})
