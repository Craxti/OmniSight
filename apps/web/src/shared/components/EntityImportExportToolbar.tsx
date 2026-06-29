import { useState, type ReactNode } from 'react'
import { ExportFormatModal } from '@/shared/components/ExportFormatModal'
import { ImportExportToolbar, type ToolbarAction } from '@/shared/components/ImportExportToolbar'
import type { ExtendedExportFormat } from '@/shared/export/downloadByFormat'

export type EntityExportFormatsConfig = {
  title: string
  formatLabel: string
  cancelLabel: string
  submitLabel: string
  onExport: (format: ExtendedExportFormat) => Promise<void>
}

type Props = {
  labels: { export: string; import: string; create: string }
  isAdmin: boolean
  canEdit: boolean
  onCreate: () => void
  onImport?: (file: File) => void
  /** Direct export callback when no format modal is needed. */
  onExport?: () => void
  /** When set, export button opens a format picker modal. */
  exportFormats?: EntityExportFormatsConfig
  extraActions?: ToolbarAction[]
  testIds?: { import?: string; create?: string }
  children?: ReactNode
}

/** Domain list toolbar: import/export/create actions with optional format modal. */
export function EntityImportExportToolbar({
  labels,
  isAdmin,
  canEdit,
  onCreate,
  onImport,
  onExport,
  exportFormats,
  extraActions,
  testIds,
  children,
}: Props) {
  const [showExport, setShowExport] = useState(false)

  const handleExportClick = () => {
    if (exportFormats) {
      setShowExport(true)
      return
    }
    onExport?.()
  }

  const handleFormatExport = async (format: ExtendedExportFormat) => {
    if (!exportFormats) return
    await exportFormats.onExport(format)
    setShowExport(false)
  }

  return (
    <>
      <ImportExportToolbar
        exportLabel={labels.export}
        importLabel={labels.import}
        createLabel={labels.create}
        isAdmin={isAdmin}
        canEdit={canEdit}
        onExport={handleExportClick}
        onImport={onImport}
        onCreate={onCreate}
        extraActions={extraActions}
        importTestId={testIds?.import}
        createTestId={testIds?.create}
      />

      {exportFormats && (
        <ExportFormatModal
          open={showExport}
          title={exportFormats.title}
          formatLabel={exportFormats.formatLabel}
          cancelLabel={exportFormats.cancelLabel}
          submitLabel={exportFormats.submitLabel}
          onClose={() => setShowExport(false)}
          onExport={handleFormatExport}
        />
      )}

      {children}
    </>
  )
}
