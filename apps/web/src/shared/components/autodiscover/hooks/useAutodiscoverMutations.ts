import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { autodiscoverApi } from '@/shared/api/autodiscover'
import type { AutodiscoverApplyResponse, AutodiscoverScanResponse } from '@/shared/api/autodiscover'
import type { useI18n } from '@/context/useI18n'
import type { useToast } from '@/context/useToast'
import type { AutodiscoverScopeDefaults } from '@/shared/components/autodiscover/hooks/useAutodiscoverScanConfig'

type TFn = ReturnType<typeof useI18n>['t']
type Toast = ReturnType<typeof useToast>

const TOAST_BEFORE_CLOSE_MS = 220

function finishWithToast(onClose: () => void, onAutoApplied: () => void, showToast: () => void) {
  showToast()
  onAutoApplied()
  window.setTimeout(onClose, TOAST_BEFORE_CLOSE_MS)
}

type ScanConfig = {
  profileId: number | ''
  selectedServers: number[]
  scopeMode: 'graph' | 'filters' | 'all'
  scopeDepth: number
  discoverRelations: boolean
  createMissingCi: boolean
  manualReview: boolean
  scopeDefaults?: AutodiscoverScopeDefaults
}

type MappingCallbacks = {
  onAutoApplied: () => void
  onManualScan: (data: AutodiscoverScanResponse) => void
  onClose: () => void
}

export function useAutodiscoverMutations(
  t: TFn,
  toast: Toast,
  scanConfig: ScanConfig,
  scanResult: AutodiscoverScanResponse | null,
  selected: Set<string>,
  callbacks: MappingCallbacks,
) {
  const { success, error: toastError } = toast

  const scanMut = useApiMutation<AutodiscoverScanResponse, void>({
    mutationFn: () =>
      autodiscoverApi.scan({
        profile_id: scanConfig.profileId === '' ? undefined : scanConfig.profileId,
        server_ci_ids: scanConfig.selectedServers,
        scope_mode: scanConfig.scopeMode,
        scope_depth: scanConfig.scopeMode === 'graph' ? scanConfig.scopeDepth : undefined,
        root_ci_id: scanConfig.scopeDefaults?.root_ci_id,
        discover_relations: scanConfig.discoverRelations,
        create_missing_ci: scanConfig.createMissingCi,
        auto_apply: !scanConfig.manualReview,
        scope_config: {
          ...(scanConfig.scopeDefaults?.scope_config ?? {}),
          depth: scanConfig.scopeDepth,
          root_ci_id: scanConfig.scopeDefaults?.root_ci_id,
        },
      }),
    messages: { success: '', error: t.common.error },
    notify: false,
    onError: (e) => toastError(e instanceof Error ? e.message : t.common.error),
    onSuccess: (data) => {
      if (!scanConfig.manualReview) {
        if (data.apply_result) {
          const fields = data.apply_result.applied - data.apply_result.applied_relations - data.apply_result.created_cis
          finishWithToast(callbacks.onClose, callbacks.onAutoApplied, () => {
            success(
              t.autodiscover.toastApplied
                .replace('{fields}', String(Math.max(0, fields)))
                .replace('{relations}', String(data.apply_result!.applied_relations))
                .replace('{cis}', String(data.apply_result!.created_cis)),
            )
            if (data.apply_result!.errors.length > 0) {
              toastError(data.apply_result!.errors.slice(0, 3).join('; '))
            }
          })
          return
        } else if (data.status === 'failed') {
          toastError(t.autodiscover.noMappings)
          callbacks.onManualScan(data)
          return
        }
        callbacks.onAutoApplied()
        callbacks.onClose()
        return
      }
      callbacks.onManualScan(data)
    },
  })

  const applyMut = useApiMutation<AutodiscoverApplyResponse, void>({
    mutationFn: () => {
      if (!scanResult) throw new Error('No scan result')
      return autodiscoverApi.apply(scanResult.run_id, [...selected])
    },
    messages: { success: '', error: t.common.error },
    notify: false,
    onError: (e) => toastError(e instanceof Error ? e.message : t.common.error),
    onSuccess: (data) => {
      const fields = data.applied - data.applied_relations - data.created_cis
      finishWithToast(callbacks.onClose, callbacks.onAutoApplied, () => {
        success(
          t.autodiscover.toastApplied
            .replace('{fields}', String(Math.max(0, fields)))
            .replace('{relations}', String(data.applied_relations))
            .replace('{cis}', String(data.created_cis)),
        )
        if (data.errors.length > 0) {
          toastError(data.errors.slice(0, 3).join('; '))
        }
      })
    },
  })

  return { scanMut, applyMut }
}
