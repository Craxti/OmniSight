import { useQueryClient } from '@tanstack/react-query'
import { useI18n } from '@/context/useI18n'
import {
  useRelationDraftMutations,
  type RelationCreateDraft,
  type RelationEditDraft,
} from '@/shared/hooks/useRelationDraftMutations'
import { useRelationMutations } from '@/shared/hooks/useRelationMutations'
import { invalidateGraphQueries } from '@/shared/queryInvalidation'

type Options = {
  rootId: number
  depth: number
  relationFilter: string
  setRelationFilter: (value: string) => void
  onCreateSuccess: () => void
  onEditSuccess: () => void
}

export function useGraphRelationActions({
  rootId,
  depth,
  relationFilter,
  setRelationFilter,
  onCreateSuccess,
  onEditSuccess,
}: Options) {
  const { t } = useI18n()
  const qc = useQueryClient()

  const invalidateGraph = () => invalidateGraphQueries(qc, rootId, depth)

  const { createMut, updateMut, deleteMut } = useRelationMutations({
    messages: {
      created: t.relations.toastCreated,
      updated: t.relations.toastUpdated,
      deleted: t.relations.toastDeleted,
      error: t.common.error,
    },
    onInvalidate: invalidateGraph,
  })

  const { createDraftMut, updateDraftMut, deleteDraftMut } = useRelationDraftMutations(
    { createMut, updateMut, deleteMut },
    { onDeleteError: invalidateGraph },
  )

  const createRelationMut = {
    ...createDraftMut,
    mutate: (payload: RelationCreateDraft) =>
      createDraftMut.mutate(payload, {
        onSuccess: () => {
          if (relationFilter && relationFilter !== payload.relationType) {
            setRelationFilter('')
          }
          onCreateSuccess()
        },
      }),
  }

  const updateRelationMut = {
    ...updateDraftMut,
    mutate: (payload: RelationEditDraft) =>
      updateDraftMut.mutate(payload, { onSuccess: onEditSuccess }),
  }

  const deleteRelationMut = {
    ...deleteDraftMut,
    mutate: (relationId: number) =>
      deleteDraftMut.mutate(relationId, { onSuccess: onEditSuccess }),
  }

  return {
    invalidateGraph,
    createRelationMut,
    updateRelationMut,
    deleteRelationMut,
  }
}
