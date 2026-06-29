import { Radar } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { ImportReport } from '@/shared/api/types'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { fmt } from '@/i18n/messages'
import { ciApi, type ImportTypeMappingEntry, type ImportTypePreview } from '@/shared/api/ci'
import { EntityImportExportToolbar } from '@/shared/components/EntityImportExportToolbar'
import { useImportExport } from '@/shared/hooks/useImportExport'
import { normalizeCiImportItems } from '@/shared/import/normalizeCiImportItems'
import { invalidateInventoryAfterImport } from '@/shared/queryInvalidation'
import { ImportTypeMappingModal } from '@/features/inventory/components/ImportTypeMappingModal'

type Props = {
  onImportReport: (report: ImportReport) => void
  onOpenExport: () => void
  onCreate: () => void
  onAutodiscover?: () => void
}

/** CI list toolbar. Export opens InventoryExportModal (filter-aware); see docs/ADR-frontend-layers.md. */
export function CiImportExportToolbar({ onImportReport, onOpenExport, onCreate, onAutodiscover }: Props) {
  const { canEdit, isAdmin } = useAuth()
  const { t } = useI18n()
  const qc = useQueryClient()
  const [mappingPreview, setMappingPreview] = useState<ImportTypePreview | null>(null)
  const [pendingItems, setPendingItems] = useState<unknown[] | null>(null)
  const [importPending, setImportPending] = useState(false)

  const invalidateCi = () => invalidateInventoryAfterImport(qc)

  const { importWithPreview, completeMappedImport } = useImportExport({
    invalidate: invalidateCi,
    onReport: onImportReport,
    messages: {
      exported: t.common.export,
      imported: (n) => fmt(t.inventory.toastImported, { n }),
      importError: t.inventory.toastImportError,
      genericError: t.common.error,
    },
  })

  const handleFile = (file: File) =>
    importWithPreview(file, {
      normalizeItems: normalizeCiImportItems,
      preview: (items) => ciApi.previewImport(items),
      needsMapping: (preview) => preview.needs_mapping,
      onMappingRequired: (items, preview) => {
        setPendingItems(items)
        setMappingPreview(preview)
      },
      importItems: (items) => ciApi.importJson(items),
    })

  const runMappedImport = async (mappings: ImportTypeMappingEntry[]) => {
    if (!pendingItems) return
    setImportPending(true)
    try {
      await completeMappedImport(pendingItems, (items, m) => ciApi.importMapped(items, m as ImportTypeMappingEntry[]), mappings)
    } finally {
      setImportPending(false)
      setMappingPreview(null)
      setPendingItems(null)
    }
  }

  return (
    <EntityImportExportToolbar
      labels={{ export: t.common.export, import: t.common.import, create: t.common.create }}
      isAdmin={isAdmin}
      canEdit={canEdit}
      onExport={onOpenExport}
      onImport={handleFile}
      onCreate={onCreate}
      testIds={{ import: 'ci-import-file', create: 'ci-create' }}
      extraActions={
        canEdit && onAutodiscover
          ? [
              {
                key: 'autodiscover',
                label: t.autodiscover.title,
                icon: Radar,
                onClick: onAutodiscover,
                testId: 'inventory-autodiscover',
              },
            ]
          : []
      }
    >
      <ImportTypeMappingModal
        open={!!mappingPreview}
        preview={mappingPreview}
        pending={importPending}
        onClose={() => {
          if (importPending) return
          setMappingPreview(null)
          setPendingItems(null)
        }}
        onConfirm={(mappings) => {
          void runMappedImport(mappings)
        }}
      />
    </EntityImportExportToolbar>
  )
}
