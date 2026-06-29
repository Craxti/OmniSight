import { describe, expect, it } from 'vitest'
import { normalizeRelationImportItems } from '@/shared/import/normalizeRelationImportItems'

describe('normalizeRelationImportItems', () => {
  it('maps alias fields and defaults', () => {
    const [row] = normalizeRelationImportItems([
      {
        source_name: 'app',
        target_name: 'db',
        type: 'depends_on',
      },
    ])
    expect(row).toEqual({
      source_ci_id: undefined,
      target_ci_id: undefined,
      source_name: 'app',
      target_name: 'db',
      relation_type: 'depends_on',
      status: undefined,
      data_source: undefined,
    })
  })

  it('preserves explicit ids and data_source', () => {
    const [row] = normalizeRelationImportItems([
      {
        source_ci_id: 1,
        target_ci_id: 2,
        relation_type: 'runs_on',
        status: 'draft',
        data_source: 'csv',
      },
    ])
    expect(row.source_ci_id).toBe(1)
    expect(row.target_ci_id).toBe(2)
    expect(row.relation_type).toBe('runs_on')
    expect(row.status).toBe('draft')
    expect(row.data_source).toBe('csv')
  })

  it('normalizes spaced relation type aliases', () => {
    const [row] = normalizeRelationImportItems([{ relation_type: 'depends on' }])
    expect(row.relation_type).toBe('depends_on')
  })

  it('uses relation alias when relation_type missing', () => {
    const [row] = normalizeRelationImportItems([{ relation: 'connected_to' }])
    expect(row.relation_type).toBe('connected_to')
  })
})
