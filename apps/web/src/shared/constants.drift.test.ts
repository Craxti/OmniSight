/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import {
  BULK_CI_STATUSES,
  CI_STATUSES,
  CRITICALITY_LEVELS,
  ENVIRONMENTS,
  EXTERNAL_ID_FIELDS,
  FIELD_ALIASES,
  RELATION_STATUSES,
  RELATION_TYPE_ALIASES,
  RELATION_TYPES,
  ROLES,
  RSM_OFFICIAL_TYPE_NAMES,
} from '@/shared/constants'

const TEST_DIR = dirname(fileURLToPath(import.meta.url))

const FIXTURE = JSON.parse(
  readFileSync(resolve(TEST_DIR, '../../../../fixtures/domain-constants.json'), 'utf-8'),
) as {
  relation_types: string[]
  relation_type_aliases: Record<string, string>
  relation_statuses: string[]
  ci_statuses: string[]
  criticality_levels: string[]
  environments: string[]
  external_id_fields: string[]
  field_aliases: Record<string, string>
  roles: string[]
  rsm_official_type_names: string[]
}

describe('domain constants drift (web generated vs fixture)', () => {
  it('matches fixtures/domain-constants.json', () => {
    expect([...RELATION_TYPES]).toEqual(FIXTURE.relation_types)
    expect({ ...RELATION_TYPE_ALIASES }).toEqual(FIXTURE.relation_type_aliases)
    expect([...RELATION_STATUSES]).toEqual(FIXTURE.relation_statuses)
    expect([...CI_STATUSES]).toEqual(FIXTURE.ci_statuses)
    expect([...CRITICALITY_LEVELS]).toEqual(FIXTURE.criticality_levels)
    expect([...ENVIRONMENTS]).toEqual(FIXTURE.environments)
    expect([...EXTERNAL_ID_FIELDS]).toEqual(FIXTURE.external_id_fields)
    expect({ ...FIELD_ALIASES }).toEqual(FIXTURE.field_aliases)
    expect([...ROLES]).toEqual(FIXTURE.roles)
    expect([...RSM_OFFICIAL_TYPE_NAMES]).toEqual(FIXTURE.rsm_official_type_names)
    expect([...BULK_CI_STATUSES]).toEqual(FIXTURE.ci_statuses.filter((s) => s !== 'archived'))
  })
})
