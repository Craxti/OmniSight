import { api, buildQuery } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import {
  type ResourceSearchV1Response,
  unwrapResourceSearch,
} from '@/shared/api/v1Inventory'
import {
  type BusinessPathV1Response,
  type ComponentsV1Response,
  type GraphLayoutV1Response,
  type GraphV1Response,
  type ImpactV1Response,
  unwrapBusinessPath,
  unwrapComponents,
  unwrapGraph,
  unwrapGraphLayout,
  unwrapImpact,
} from '@/shared/api/v1Topology'

export const resourcesApi = {
  graph: async (id: number, depth = 3) => {
    const body = await api<GraphV1Response>(`${paths.resources.graph(id)}${buildQuery({ depth })}`)
    return unwrapGraph(body)
  },
  graphLayout: async (id: number, relationFilter = '') => {
    const body = await api<GraphLayoutV1Response>(
      `${paths.resources.graphLayout(id)}${buildQuery(
        relationFilter ? { relation_filter: relationFilter } : undefined,
      )}`,
    )
    return unwrapGraphLayout(body)
  },
  saveGraphLayout: async (
    id: number,
    body: { relation_filter: string; positions: Record<string, { x: number; y: number }> },
  ) => {
    const response = await api<GraphLayoutV1Response>(paths.resources.graphLayout(id), {
      method: 'PUT',
      body: JSON.stringify(body),
    })
    return unwrapGraphLayout(response)
  },
  clearGraphLayout: (id: number, relationFilter = '') =>
    api<void>(
      `${paths.resources.graphLayout(id)}${buildQuery(
        relationFilter ? { relation_filter: relationFilter } : undefined,
      )}`,
      { method: 'DELETE' },
    ),
  impact: async (id: number) => {
    const body = await api<ImpactV1Response>(paths.resources.impact(id))
    return unwrapImpact(body)
  },
  businessPath: async (id: number) => {
    const body = await api<BusinessPathV1Response>(paths.resources.businessPath(id))
    return unwrapBusinessPath(body)
  },
  components: async (id: number) => {
    const body = await api<ComponentsV1Response>(paths.resources.components(id))
    return unwrapComponents(body)
  },
  search: async (params: Record<string, string>) => {
    const body = await api<ResourceSearchV1Response>(
      `${paths.resources.search}${buildQuery(params)}`,
    )
    return unwrapResourceSearch(body)
  },
}
