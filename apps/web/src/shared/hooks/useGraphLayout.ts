import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback } from 'react'
import { normalizeRelationFilter, type StoredPosition } from '@/lib/graphPositions'
import { resourcesApi } from '@/shared/api'
import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { queryKeys } from '@/shared/queryKeys'

export function useGraphLayout(rootId: number, relationFilter: string, enabled: boolean) {
  const qc = useQueryClient()
  const filter = normalizeRelationFilter(relationFilter)

  const layoutQuery = useQuery({
    queryKey: queryKeys.graphLayout(rootId, filter),
    queryFn: () => resourcesApi.graphLayout(rootId, relationFilter),
    enabled: enabled && rootId > 0,
    staleTime: 30_000,
  })

  const saveMutation = useApiMutation({
    mutationFn: (positions: Record<string, StoredPosition>) =>
      resourcesApi.saveGraphLayout(rootId, { relation_filter: filter, positions }),
    messages: { success: '', error: '' },
    notify: false,
    onSuccess: (data) => {
      qc.setQueryData(queryKeys.graphLayout(rootId, filter), data)
    },
  })

  const clearMutation = useApiMutation({
    mutationFn: () => resourcesApi.clearGraphLayout(rootId, relationFilter),
    messages: { success: '', error: '' },
    notify: false,
    onSuccess: () => {
      qc.setQueryData(queryKeys.graphLayout(rootId, filter), {
        root_ci_id: rootId,
        relation_filter: filter,
        positions: {},
      })
    },
  })

  const persistPositions = useCallback(
    (positions: Record<string, StoredPosition>) => {
      saveMutation.mutate(positions)
    },
    [saveMutation],
  )

  const clearPositions = useCallback(async () => {
    await clearMutation.mutateAsync(undefined)
  }, [clearMutation])

  return {
    savedPositions: layoutQuery.data?.positions ?? null,
    isLayoutLoading: layoutQuery.isLoading,
    persistPositions,
    clearPositions,
    isSaving: saveMutation.isPending,
  }
}
