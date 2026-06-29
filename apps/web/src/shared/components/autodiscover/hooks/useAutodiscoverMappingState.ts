import { useMemo, useState } from 'react'
import type { AutodiscoverScanResponse } from '@/shared/api/autodiscover'

export type MappingFilter = 'all' | 'field' | 'relation' | 'ci_create'

export function useAutodiscoverMappingState() {
  const [mappingFilter, setMappingFilter] = useState<MappingFilter>('all')
  const [scanResult, setScanResult] = useState<AutodiscoverScanResponse | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const filteredMappings = useMemo(() => {
    if (!scanResult) return []
    if (mappingFilter === 'all') return scanResult.mappings
    return scanResult.mappings.filter((m) => m.mapping_kind === mappingFilter)
  }, [scanResult, mappingFilter])

  const toggleMapping = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const clearScanResult = () => setScanResult(null)

  const resetMappingState = () => {
    setScanResult(null)
    setSelected(new Set())
  }

  const selectFromScan = (data: AutodiscoverScanResponse) => {
    setScanResult(data)
    setSelected(new Set(data.mappings.filter((m) => m.selected || m.status === 'auto').map((m) => m.mapping_id)))
  }

  return {
    mappingFilter,
    setMappingFilter,
    scanResult,
    setScanResult,
    selected,
    setSelected,
    filteredMappings,
    toggleMapping,
    clearScanResult,
    resetMappingState,
    selectFromScan,
  }
}
