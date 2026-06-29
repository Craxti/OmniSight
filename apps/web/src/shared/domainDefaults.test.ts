import { describe, expect, it } from 'vitest'
import {
  BUSINESS_SERVICE_TYPE_NAME,
  DEFAULT_RELATION_TYPE,
  RELATION_TYPES,
  ROLES,
  RSM_OFFICIAL_TYPE_NAMES,
} from '@/shared/constants'

describe('domainDefaults', () => {
  it('exposes stable named defaults from generated constants', () => {
    expect(DEFAULT_RELATION_TYPE).toBe(RELATION_TYPES[0])
    expect(BUSINESS_SERVICE_TYPE_NAME).toBe(RSM_OFFICIAL_TYPE_NAMES[0])
    expect(ROLES).toContain('admin')
  })
})
