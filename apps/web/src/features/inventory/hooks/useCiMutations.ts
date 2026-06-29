import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { useEntityIdMutation } from '@/shared/hooks/useEntityMutations'
import { mergeAttributesToExternal } from '@/features/inventory/inventoryForm'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'
import { fmt } from '@/i18n/messages'
import { ciApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'
import type { CiFormState } from '@/features/inventory/inventoryForm'

type Messages = (typeof messages)[Locale]

type UseCiMutationsOptions = {
  t: Messages
  selected: Set<number>
  onCreateSuccess: () => void
  onBulkSuccess: () => void
}

export function useCiMutations({ t, selected, onCreateSuccess, onBulkSuccess }: UseCiMutationsOptions) {
  const createMut = useApiMutation<Awaited<ReturnType<typeof ciApi.create>>, CiFormState>({
    mutationFn: (form) => {
      const { attributes, external_ids } = mergeAttributesToExternal(form.attributes)
      return ciApi.create({ ...form, attributes, external_ids })
    },
    invalidateKeys: [queryKeys.ci.all],
    messages: { success: t.inventory.toastCreated, error: t.common.error },
    onSuccess: () => onCreateSuccess(),
  })

  const deleteMut = useEntityIdMutation({
    mutationFn: (id: number) => ciApi.delete(id),
    invalidateKeys: [queryKeys.ci.all, queryKeys.audit.all, queryKeys.dashboard],
    messages: { success: t.inventory.toastDeleted, error: t.common.error },
  })

  const restoreMut = useEntityIdMutation({
    mutationFn: (id: number) => ciApi.restore(id),
    invalidateKeys: [queryKeys.ci.all, queryKeys.ci.recycle, queryKeys.audit.all, queryKeys.dashboard],
    messages: { success: t.inventory.toastRestored, error: t.common.error },
  })

  const purgeMut = useEntityIdMutation({
    mutationFn: (id: number) => ciApi.purge(id),
    invalidateKeys: [queryKeys.ci.all, queryKeys.ci.recycle, queryKeys.audit.all, queryKeys.dashboard],
    messages: { success: t.inventory.toastPurged, error: t.common.error },
  })

  const bulkMut = useApiMutation({
    mutationFn: (status: string) => ciApi.bulkStatus([...selected], status),
    invalidateKeys: [queryKeys.ci.all],
    messages: {
      success: fmt(t.inventory.toastUpdated, { n: selected.size }),
      error: t.common.error,
    },
    onSuccess: () => onBulkSuccess(),
  })

  const bulkDeleteMut = useApiMutation({
    mutationFn: () => ciApi.bulkDelete([...selected]),
    invalidateKeys: [queryKeys.ci.all, queryKeys.audit.all, queryKeys.dashboard],
    messages: {
      success: fmt(t.inventory.toastBulkDeleted, { n: selected.size }),
      error: t.common.error,
    },
    onSuccess: () => onBulkSuccess(),
  })

  return { createMut, deleteMut, restoreMut, purgeMut, bulkMut, bulkDeleteMut }
}
