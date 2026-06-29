import { useRelationDraftMutations } from '@/shared/hooks/useRelationDraftMutations'
import { useRelationMutations } from '@/shared/hooks/useRelationMutations'
import { useApiMutation } from '@/shared/hooks/useApiMutation'
import type { Locale } from '@/i18n/messages'
import { messages, fmt } from '@/i18n/messages'
import { relationsApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'
import type { RelationEditState } from '@/features/relations/components/RelationEditModal'

type Messages = (typeof messages)[Locale]

export function useRelationsMutations(
  t: Messages,
  options: {
    selected?: Set<number>
    onCreateSuccess: () => void
    onUpdateSuccess: () => void
    onBulkSuccess?: () => void
  },
) {
  const selected = options.selected ?? new Set<number>()

  const base = useRelationMutations({
    messages: {
      created: t.relations.toastCreated,
      updated: t.relations.toastUpdated,
      deleted: t.relations.toastDeleted,
      error: t.common.error,
    },
  })

  const { createDraftMut, updateDraftMut, deleteDraftMut } = useRelationDraftMutations(base, {
    onCreateSuccess: options.onCreateSuccess,
    onUpdateSuccess: options.onUpdateSuccess,
  })

  const bulkMut = useApiMutation({
    mutationFn: (status: string) => relationsApi.bulkStatus([...selected], status),
    invalidateKeys: [queryKeys.relations.all],
    messages: {
      success: fmt(t.relations.toastBulkUpdated, { n: selected.size }),
      error: t.common.error,
    },
    onSuccess: () => options.onBulkSuccess?.(),
  })

  const bulkDeleteMut = useApiMutation({
    mutationFn: () => relationsApi.bulkDelete([...selected]),
    invalidateKeys: [queryKeys.relations.all],
    messages: {
      success: fmt(t.relations.toastBulkDeleted, { n: selected.size }),
      error: t.common.error,
    },
    onSuccess: () => options.onBulkSuccess?.(),
  })

  return {
    createMut: createDraftMut,
    deleteMut: deleteDraftMut,
    updateMut: updateDraftMut,
    bulkMut,
    bulkDeleteMut,
    invalidate: base.invalidateRelations,
  }
}

export type { RelationEditState }
