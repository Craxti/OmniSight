import type { CI, GraphNode, GraphPanelData, Relation } from '@/shared/api/types'

export function buildOverviewGraph(cis: CI[], relations: Relation[]): GraphPanelData {
  const ciIds = new Set(cis.map((ci) => ci.id))
  const nodes: GraphNode[] = cis.map((ci) => ({
    id: ci.id,
    name: ci.name,
    type: ci.type,
    type_id: ci.type_id,
    description: ci.description,
    status: ci.status,
    criticality: ci.criticality,
    environment: ci.environment,
    owner: ci.owner,
    team: ci.team,
    attributes: ci.attributes,
    external_ids: ci.external_ids,
    last_changed_at: ci.last_changed_at,
    created_at: ci.created_at,
  }))
  const edges = relations.filter(
    (rel) => ciIds.has(rel.source_ci_id) && ciIds.has(rel.target_ci_id),
  )
  return { nodes, edges }
}
