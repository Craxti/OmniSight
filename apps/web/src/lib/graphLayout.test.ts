import { describe, expect, it } from 'vitest'

import { computeDependencyLayout, computeGraphLayout, type LayoutEdge, type LayoutNode } from '@/lib/graphLayout'

const demoNodes: LayoutNode[] = [
  { id: 1, depth: 0 },
  { id: 2, depth: 1 },
  { id: 3, depth: 2 },
]

const demoEdges: LayoutEdge[] = [
  { source_ci_id: 2, target_ci_id: 1, relation_type: 'depends_on' },
  { source_ci_id: 3, target_ci_id: 2, relation_type: 'depends_on' },
]

function yOf(positions: Map<number, { x: number; y: number }>, id: number): number {
  return positions.get(id)?.y ?? Number.NaN
}

describe('computeDependencyLayout', () => {
  it('keeps depends_on arrows downward when root is the deepest dependency', () => {
    const positions = computeDependencyLayout(demoNodes, demoEdges, 1)

    expect(yOf(positions, 1)).toBeGreaterThan(yOf(positions, 2))
    expect(yOf(positions, 2)).toBeGreaterThan(yOf(positions, 3))
  })

  it('keeps depends_on arrows upward when root is the top dependent', () => {
    const positions = computeDependencyLayout(demoNodes, demoEdges, 3)

    expect(yOf(positions, 3)).toBeGreaterThan(yOf(positions, 2))
    expect(yOf(positions, 2)).toBeGreaterThan(yOf(positions, 1))
  })

  it('fans out many children around a hub parent', () => {
    const hubNodes: LayoutNode[] = [
      { id: 1 },
      { id: 2 },
      { id: 3 },
      { id: 4 },
      { id: 5 },
    ]
    const hubEdges: LayoutEdge[] = [
      { source_ci_id: 2, target_ci_id: 1, relation_type: 'hosted_on' },
      { source_ci_id: 3, target_ci_id: 1, relation_type: 'uses' },
      { source_ci_id: 4, target_ci_id: 1, relation_type: 'linked_to' },
      { source_ci_id: 5, target_ci_id: 1, relation_type: 'reserves' },
    ]

    const { positions } = computeGraphLayout(hubNodes, hubEdges, 1)
    const childXs = [2, 3, 4, 5].map((id) => positions.get(id)?.x ?? 0)
    const spread = Math.max(...childXs) - Math.min(...childXs)

    expect(spread).toBeGreaterThan(400)
  })
})
