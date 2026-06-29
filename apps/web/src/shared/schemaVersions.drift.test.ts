/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { AUTH_SCHEMA_V1 } from '@/shared/api/v1Auth'
import { AUTODISCOVER_SCHEMA_V1 } from '@/shared/api/v1Autodiscover'
import { INVENTORY_SCHEMA_V1 } from '@/shared/api/v1Inventory'
import { META_SCHEMA_V1 } from '@/shared/api/v1Meta'
import { OPS_SCHEMA_V1 } from '@/shared/api/v1Ops'
import { TOPOLOGY_SCHEMA_V1 } from '@/shared/api/v1Topology'
import { SCHEMA_VERSIONS_V1 } from '@/shared/schemaVersions.generated'

const TEST_DIR = dirname(fileURLToPath(import.meta.url))

const FIXTURE = JSON.parse(
  readFileSync(resolve(TEST_DIR, '../../../../fixtures/schema-versions.json'), 'utf-8'),
) as Record<string, string>

describe('schema versions drift (web vs fixture)', () => {
  it('matches fixtures/schema-versions.json', () => {
    expect(SCHEMA_VERSIONS_V1).toEqual(FIXTURE)
    expect(INVENTORY_SCHEMA_V1).toBe(FIXTURE.inventory)
    expect(AUTH_SCHEMA_V1).toBe(FIXTURE.auth)
    expect(AUTODISCOVER_SCHEMA_V1).toBe(FIXTURE.autodiscover)
    expect(META_SCHEMA_V1).toBe(FIXTURE.meta)
    expect(OPS_SCHEMA_V1).toBe(FIXTURE.ops)
    expect(TOPOLOGY_SCHEMA_V1).toBe(FIXTURE.topology)
  })
})
