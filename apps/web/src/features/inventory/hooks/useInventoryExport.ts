import { useState } from 'react'
import { useI18n } from '@/context/useI18n'
import { useToast } from '@/context/useToast'
import { ciApi } from '@/shared/api'
import { omitFalsyValues } from '@/shared/api/v1Envelope'
import { downloadByFormat } from '@/shared/export/downloadByFormat'
import { defaultExportFilters, type ExportFormat } from '@/features/inventory/inventoryExport'

export function useInventoryExport() {
  const { t } = useI18n()
  const { success } = useToast()
  const [showExport, setShowExport] = useState(false)
  const [exportFilters, setExportFilters] = useState(defaultExportFilters)

  const exportFiltered = async (format: ExportFormat) => {
    const params = omitFalsyValues(exportFilters)
    const payload = await ciApi.exportFull(params)
    downloadByFormat(payload, format, 'rsm-filtered-export')
    setShowExport(false)
    success(t.inventory.toastExported)
  }

  return {
    showExport,
    setShowExport,
    exportFilters,
    setExportFilters,
    exportFiltered,
  }
}
