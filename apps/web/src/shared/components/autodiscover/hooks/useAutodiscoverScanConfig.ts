import { useEffect, useState } from 'react'

export type AutodiscoverScopeDefaults = {
  scope_mode?: 'graph' | 'filters' | 'all'
  scope_depth?: number
  root_ci_id?: number
  scope_config?: Record<string, unknown>
}

export function useAutodiscoverScanConfig(
  open: boolean,
  scopeDefaults?: AutodiscoverScopeDefaults,
) {
  const [profileId, setProfileId] = useState<number | ''>('')
  const [selectedServers, setSelectedServers] = useState<number[]>([])
  const [scopeMode, setScopeMode] = useState<'graph' | 'filters' | 'all'>(scopeDefaults?.scope_mode ?? 'all')
  const [scopeDepth, setScopeDepth] = useState(scopeDefaults?.scope_depth ?? 2)
  const [discoverRelations, setDiscoverRelations] = useState(true)
  const [createMissingCi, setCreateMissingCi] = useState(true)
  const [manualReview, setManualReview] = useState(false)

  useEffect(() => {
    if (!open) return
    setScopeMode(scopeDefaults?.scope_mode ?? 'all')
    setScopeDepth(scopeDefaults?.scope_depth ?? 2)
  }, [open, scopeDefaults])

  const toggleServer = (id: number) => {
    setSelectedServers((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const resetScanConfig = () => {
    setSelectedServers([])
  }

  return {
    profileId,
    setProfileId,
    selectedServers,
    setSelectedServers,
    scopeMode,
    setScopeMode,
    scopeDepth,
    setScopeDepth,
    discoverRelations,
    setDiscoverRelations,
    createMissingCi,
    setCreateMissingCi,
    manualReview,
    setManualReview,
    toggleServer,
    resetScanConfig,
  }
}
