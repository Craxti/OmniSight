import { describe, expect, it } from 'vitest'

import { computeDependencyLayout, computeGraphLayout, computeOverviewLayout, type LayoutEdge, type LayoutNode } from '@/lib/graphLayout'

const demoNodes: LayoutNode[] = [
  { id: 1, depth: 0 },
  { id: 2, depth: 1 },
  { id: 3, depth: 2 },
]

const demoEdges: LayoutEdge[] = [
  { source_ci_id: 2, target_ci_id: 1, relation_type: 'depends_on' },
  { source_ci_id: 3, target_ci_id: 2, relation_type: 'depends_on' },
]

const payNodes: LayoutNode[] = [
  { id: 1 },
  { id: 2 },
  { id: 3 },
  { id: 4 },
  { id: 5 },
  { id: 6 },
  { id: 7 },
  { id: 8 },
  { id: 9 },
  { id: 10 },
  { id: 11 },
]

const payEdges: LayoutEdge[] = [
  { source_ci_id: 1, target_ci_id: 2, relation_type: 'depends_on' },
  { source_ci_id: 3, target_ci_id: 4, relation_type: 'depends_on' },
  { source_ci_id: 4, target_ci_id: 1, relation_type: 'depends_on' },
  { source_ci_id: 1, target_ci_id: 5, relation_type: 'hosted_on' },
  { source_ci_id: 1, target_ci_id: 6, relation_type: 'part_of' },
  { source_ci_id: 1, target_ci_id: 7, relation_type: 'uses' },
  { source_ci_id: 2, target_ci_id: 11, relation_type: 'linked_to' },
  { source_ci_id: 1, target_ci_id: 8, relation_type: 'affects' },
  { source_ci_id: 1, target_ci_id: 9, relation_type: 'reserves' },
  { source_ci_id: 2, target_ci_id: 10, relation_type: 'hosted_on' },
]

function yOf(positions: Map<number, { x: number; y: number }>, id: number): number {
  return positions.get(id)?.y ?? Number.NaN
}

function xOf(positions: Map<number, { x: number; y: number }>, id: number): number {
  return positions.get(id)?.x ?? Number.NaN
}

function distinctYs(positions: Map<number, { x: number; y: number }>): number {
  return new Set([...positions.values()].map((p) => p.y)).size
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

  it('aligns depends_on spine for application root', () => {
    const { positions } = computeGraphLayout(payNodes, payEdges, 1)

    expect(yOf(positions, 1)).toBeGreaterThan(yOf(positions, 4))
    expect(yOf(positions, 4)).toBeGreaterThan(yOf(positions, 3))
    expect(Math.abs(xOf(positions, 1) - xOf(positions, 4))).toBeLessThan(20)
    expect(Math.abs(xOf(positions, 4) - xOf(positions, 3))).toBeLessThan(20)
    expect(xOf(positions, 2)).toBeLessThan(xOf(positions, 1))
    expect(xOf(positions, 11)).not.toBe(xOf(positions, 3))
  })

  it('uses vertical layers for peripheral network root instead of one flat row', () => {
    const { positions } = computeGraphLayout(payNodes, payEdges, 11)

    expect(distinctYs(positions)).toBeGreaterThanOrEqual(4)
    expect(yOf(positions, 11)).toBeGreaterThan(yOf(positions, 2))
    expect(yOf(positions, 2)).toBeGreaterThan(yOf(positions, 1))
    expect(Math.abs(xOf(positions, 11) - xOf(positions, 2))).toBeLessThan(40)
  })

  it('places overview nodes on concentric rings instead of one flat row', () => {
    const { positions } = computeOverviewLayout(payNodes, payEdges)

    expect(positions.size).toBe(payNodes.length)
    expect(distinctYs(positions)).toBeGreaterThanOrEqual(4)

    const hub = positions.get(1)
    const outer = positions.get(11)
    expect(hub).toBeTruthy()
    expect(outer).toBeTruthy()
    const dx = (outer?.x ?? 0) - (hub?.x ?? 0)
    const dy = (outer?.y ?? 0) - (hub?.y ?? 0)
    expect(Math.hypot(dx, dy)).toBeGreaterThan(200)
  })
})
