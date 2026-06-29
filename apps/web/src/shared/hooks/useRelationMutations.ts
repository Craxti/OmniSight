import { useQueryClient } from '@tanstack/react-query'
import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { relationsApi } from '@/shared/api'
import type { RelationCreate } from '@/shared/api/types'
import { invalidateRelationsQueries } from '@/shared/queryInvalidation'
import { queryKeys } from '@/shared/queryKeys'

type RelationUpdatePayload = {
  relation_type: string
  status: string
  data_source?: string
}

type Options = {
  onInvalidate?: () => void
  messages: {
    created: string
    updated: string
    deleted: string
    error: string
  }
}

export function useRelationMutations({ onInvalidate, messages }: Options) {
  const qc = useQueryClient()

  const invalidateRelations = () => {
    invalidateRelationsQueries(qc)
    onInvalidate?.()
  }

  const createMut = useApiMutation({
    mutationFn: (payload: RelationCreate) => relationsApi.create(payload),
    invalidateKeys: [queryKeys.relations.all],
    messages: { success: messages.created, error: messages.error },
    onSuccess: () => invalidateRelations(),
  })

  const updateMut = useApiMutation({
    mutationFn: ({ id, body }: { id: number; body: RelationUpdatePayload }) =>
      relationsApi.update(id, body),
    invalidateKeys: [queryKeys.relations.all],
    messages: { success: messages.updated, error: messages.error },
    onSuccess: () => invalidateRelations(),
  })

  const deleteMut = useApiMutation({
    mutationFn: (id: number) => relationsApi.delete(id),
    invalidateKeys: [queryKeys.relations.all],
    messages: { success: messages.deleted, error: messages.error },
    onSuccess: () => invalidateRelations(),
  })

  return { createMut, updateMut, deleteMut, invalidateRelations }
}
