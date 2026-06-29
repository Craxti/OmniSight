import { describe, expect, it } from 'vitest'
import { unwrapDomainConstants } from '@/shared/api/v1Meta'

describe('V1Meta helpers', () => {
  it('unwraps domain constants envelope', () => {
    expect(
      unwrapDomainConstants({
        api_version: 'v1',
        schema_version: 'rsm-meta-v1',
        constants: {
          relation_types: ['depends_on'],
          relation_statuses: ['active'],
          ci_statuses: ['active'],
          criticality_levels: ['high'],
          environments: ['prod'],
          external_id_fields: ['hostname'],
          roles: ['admin'],
          rsm_official_type_names: ['Server'],
        },
      }).relation_types,
    ).toEqual(['depends_on'])
  })
})
