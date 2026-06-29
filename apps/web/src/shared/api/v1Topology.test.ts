import { describe, expect, it } from 'vitest'
import {
  unwrapBusinessPath,
  unwrapComponents,
  unwrapGraph,
  unwrapGraphLayout,
  unwrapImpact,
} from '@/shared/api/v1Topology'

describe('V1Topology helpers', () => {
  const base = { api_version: 'v1' as const, schema_version: 'rsm-topology-v1' }

  it('unwraps graph envelope', () => {
    const graph = { root_id: 1, depth: 2, nodes: [], edges: [] }
    expect(unwrapGraph({ ...base, graph })).toEqual(graph)
  })

  it('unwraps impact, components, business path, and layout envelopes', () => {
    expect(unwrapImpact({ ...base, impact: { ci_id: 1, impacted_business_services: [], count: 0 } }).ci_id).toBe(1)
    expect(unwrapComponents({ ...base, components: { ci_id: 1, components: [], count: 0 } }).count).toBe(0)
    expect(unwrapBusinessPath({ ...base, business_path: { path: [] } }).path).toEqual([])
    expect(
      unwrapGraphLayout({ ...base, layout: { root_ci_id: 5, relation_filter: '*', positions: {} } }).root_ci_id,
    ).toBe(5)
  })
})
