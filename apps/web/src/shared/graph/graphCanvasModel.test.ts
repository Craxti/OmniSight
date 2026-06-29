import { describe, expect, it } from 'vitest'
import { pathEdgeKeysFromPath } from '@/shared/graph/graphCanvasModel'

describe('pathEdgeKeysFromPath', () => {
  it('builds undirected edge keys between consecutive path nodes', () => {
    const keys = pathEdgeKeysFromPath([{ id: 1 }, { id: 2 }, { id: 3 }])
    expect(keys.has('1-2')).toBe(true)
    expect(keys.has('2-3')).toBe(true)
    expect(keys.size).toBe(4)
  })
})
