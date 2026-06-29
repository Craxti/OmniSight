import { useI18n } from '@/context/useI18n'
import { useToast } from '@/context/useToast'
import { useAutodiscoverMappingState } from '@/shared/components/autodiscover/hooks/useAutodiscoverMappingState'
import { useAutodiscoverMutations } from '@/shared/components/autodiscover/hooks/useAutodiscoverMutations'
import { useAutodiscoverQueries } from '@/shared/components/autodiscover/hooks/useAutodiscoverQueries'
import {
  useAutodiscoverScanConfig,
  type AutodiscoverScopeDefaults,
} from '@/shared/components/autodiscover/hooks/useAutodiscoverScanConfig'

export type { AutodiscoverScopeDefaults }
export type { MappingFilter } from '@/shared/components/autodiscover/hooks/useAutodiscoverMappingState'

type Options = {
  open: boolean
  scopeDefaults?: AutodiscoverScopeDefaults
  onClose: () => void
  onApplied: () => void
}

export function useAutodiscoverModal({ open, scopeDefaults, onClose, onApplied }: Options) {
  const { t } = useI18n()
  const toast = useToast()

  const scanConfig = useAutodiscoverScanConfig(open, scopeDefaults)
  const mapping = useAutodiscoverMappingState()
  const queries = useAutodiscoverQueries(open, scanConfig.selectedServers, scanConfig.setSelectedServers)

  const handleClose = () => {
    mapping.resetMappingState()
    scanConfig.resetScanConfig()
    onClose()
  }

  const { scanMut, applyMut } = useAutodiscoverMutations(
    t,
    toast,
    { ...scanConfig, scopeDefaults },
    mapping.scanResult,
    mapping.selected,
    {
      onAutoApplied: onApplied,
      onManualScan: mapping.selectFromScan,
      onClose: handleClose,
    },
  )

  return {
    t,
    ...scanConfig,
    ...mapping,
    ...queries,
    scanMut,
    applyMut,
    handleClose,
  }
}
