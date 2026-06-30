import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import { resourcesApi } from '@/shared/api'
import { BUSINESS_SERVICE_TYPE_NAME } from '@/shared/constants'
import { useCiResourcePanels } from '@/shared/hooks/useCiResourcePanels'
import { queryKeys } from '@/shared/queryKeys'
import { pathEdgeKeysFromPath } from '@/shared/graph/graphCanvasModel'

export function useGraphQueries(rootId: number, depth: number) {
  const id = rootId

  const { data: graph, isLoading } = useQuery({
    queryKey: queryKeys.graph.root(id, depth),
    queryFn: () => resourcesApi.graph(id, depth),
    enabled: !!id,
  })

  const rootType = useMemo(() => graph?.nodes?.find((n) => n.id === id)?.type, [graph?.nodes, id])
  const ciNameById = useMemo(() => {
    const map = new Map<number, string>()
    for (const node of graph?.nodes ?? []) map.set(node.id, node.name)
    return map
  }, [graph?.nodes])
  const isBusinessServiceRoot = rootType === BUSINESS_SERVICE_TYPE_NAME

  const { businessPath, impact, components } = useCiResourcePanels(id, {
    businessPath: !!id,
    impact: !!id,
    components: !!id,
    isBusinessService: isBusinessServiceRoot,
  })

  const pathIds = useMemo(
    () => new Set<number>((businessPath?.path || []).map((p) => p.id)),
    [businessPath],
  )
  const pathEdgeKeys = useMemo(() => pathEdgeKeysFromPath(businessPath?.path ?? []), [businessPath])
  const impactIds = useMemo(
    () => new Set<number>((impact?.impacted_business_services || []).map((p) => p.id)),
    [impact],
  )
  const componentIds = useMemo(
    () => new Set<number>((components?.components || []).map((c) => c.id)),
    [components],
  )

  const ciDisplay = (ciId: number) => ciNameById.get(ciId) ?? `#${ciId}`

  return {
    graph,
    isLoading,
    businessPath,
    impact,
    components,
    pathIds,
    pathEdgeKeys,
    impactIds,
    componentIds,
    isBusinessServiceRoot,
    ciDisplay,
  }
}
