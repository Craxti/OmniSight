import { describe, expect, it } from 'vitest'

import { normalizeRelationFilter } from '@/lib/graphPositions'

describe('graphPositions', () => {
  it('normalizes empty relation filter to wildcard bucket', () => {
    expect(normalizeRelationFilter('')).toBe('*')
    expect(normalizeRelationFilter('depends_on')).toBe('depends_on')
  })
})
