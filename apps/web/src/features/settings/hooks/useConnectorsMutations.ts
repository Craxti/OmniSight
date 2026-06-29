import { useQueryClient } from '@tanstack/react-query'
import { useI18n } from '@/context/useI18n'
import { useToast } from '@/context/useToast'
import { autodiscoverApi, type ConnectorSyncResult, type ConnectorTestResult, type SyncConnectorInput } from '@/shared/api/autodiscover'
import { queryKeys } from '@/shared/queryKeys'
import { invalidateCiQueries, invalidateRelationsQueries } from '@/shared/queryInvalidation'
import { useApiMutation } from '@/shared/hooks/useApiMutation'

export function useConnectorsMutations() {
  const { t } = useI18n()
  const { success, error } = useToast()
  const queryClient = useQueryClient()

  const createMut = useApiMutation({
    mutationFn: (body: SyncConnectorInput) => autodiscoverApi.createConnector(body),
    invalidateKeys: [queryKeys.autodiscover.connectors],
    messages: { success: t.settings.connectors.toastCreated, error: t.common.error },
  })

  const updateMut = useApiMutation({
    mutationFn: ({ id, body }: { id: number; body: Partial<SyncConnectorInput> }) =>
      autodiscoverApi.updateConnector(id, body),
    invalidateKeys: [queryKeys.autodiscover.connectors],
    messages: { success: t.settings.connectors.toastUpdated, error: t.common.error },
  })

  const deleteMut = useApiMutation({
    mutationFn: (id: number) => autodiscoverApi.deleteConnector(id),
    invalidateKeys: [queryKeys.autodiscover.connectors],
    messages: { success: t.settings.connectors.toastDeleted, error: t.common.error },
  })

  const testMut = useApiMutation<ConnectorTestResult, number>({
    mutationFn: (id: number) => autodiscoverApi.testConnector(id),
    messages: { success: '', error: t.common.error },
    notify: false,
    onSuccess: (data) => {
      if (data.ok) {
        success(t.settings.connectors.toastTestOk.replace('{n}', String(data.records_found)))
      } else {
        error(data.error ?? t.settings.connectors.toastTestFail)
      }
    },
  })

  const syncMut = useApiMutation<ConnectorSyncResult, number>({
    mutationFn: (id: number) => autodiscoverApi.syncConnector(id),
    invalidateKeys: [queryKeys.autodiscover.connectors],
    messages: { success: '', error: t.common.error },
    notify: false,
    onSuccess: (data) => {
      if (data.error || data.status === 'failed') {
        error(data.error ?? t.settings.connectors.toastSyncFail)
        return
      }
      const applied = data.apply_result?.applied ?? 0
      const relations = data.apply_result?.applied_relations ?? 0
      const cis = data.apply_result?.created_cis ?? 0
      success(
        t.settings.connectors.toastSyncOk
          .replace('{applied}', String(applied))
          .replace('{relations}', String(relations))
          .replace('{cis}', String(cis)),
      )
      invalidateCiQueries(queryClient)
      invalidateRelationsQueries(queryClient)
    },
  })

  return { createMut, updateMut, deleteMut, testMut, syncMut }
}
