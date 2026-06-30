import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import { buildOverviewGraph } from '@/features/graph/lib/buildOverviewGraph'
import { ciApi, relationsApi } from '@/shared/api'
import type { CI } from '@/shared/api/types'
import { queryKeys } from '@/shared/queryKeys'

async function listAllCis(): Promise<CI[]> {
  const page_size = 500
  const items: CI[] = []
  let page = 1
  for (;;) {
    const { items: pageItems, pagination } = await ciApi.listPage({ page, page_size })
    items.push(...pageItems)
    if (page >= pagination.total_pages) break
    page += 1
  }
  return items
}

export function useGraphOverview(enabled: boolean) {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.graph.overview,
    queryFn: async () => {
      const [cis, relations] = await Promise.all([listAllCis(), relationsApi.listAll()])
      return buildOverviewGraph(cis, relations)
    },
    enabled,
    staleTime: 30_000,
  })

  const ciNameById = useMemo(() => {
    const map = new Map<number, string>()
    for (const node of data?.nodes ?? []) map.set(node.id, node.name)
    return map
  }, [data?.nodes])

  const ciDisplay = (ciId: number) => ciNameById.get(ciId) ?? `#${ciId}`

  return {
    graph: data,
    isLoading,
    ciDisplay,
  }
}
