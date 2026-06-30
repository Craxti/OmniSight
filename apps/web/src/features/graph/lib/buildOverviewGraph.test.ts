import { describe, expect, it } from 'vitest'
import { buildOverviewGraph } from '@/features/graph/lib/buildOverviewGraph'
import type { CI, Relation } from '@/shared/api/types'

const ci = (id: number, name: string): CI => ({
  id,
  name,
  type: 'Server',
  type_id: 1,
  status: 'active',
})

const rel = (id: number, source: number, target: number): Relation => ({
  id,
  source_ci_id: source,
  target_ci_id: target,
  relation_type: 'depends_on',
  status: 'active',
  data_source: 'manual',
})

describe('buildOverviewGraph', () => {
  it('maps all CIs and keeps relations between them', () => {
    const graph = buildOverviewGraph([ci(1, 'a'), ci(2, 'b')], [rel(10, 1, 2)])
    expect(graph.nodes).toHaveLength(2)
    expect(graph.edges).toHaveLength(1)
    expect(graph.nodes[0]?.name).toBe('a')
  })

  it('drops relations that reference missing CIs', () => {
    const graph = buildOverviewGraph([ci(1, 'a')], [rel(10, 1, 99)])
    expect(graph.edges).toHaveLength(0)
  })
})
