import type { ImportReport } from '@/shared/api/types'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { relationsApi } from '@/shared/api'
import { EntityImportExportToolbar } from '@/shared/components/EntityImportExportToolbar'
import { downloadByFormat, type ExtendedExportFormat } from '@/shared/export/downloadByFormat'
import { useImportExport } from '@/shared/hooks/useImportExport'
import { normalizeRelationImportItems } from '@/shared/import/normalizeRelationImportItems'

type Props = {
  onImportReport: (report: ImportReport) => void
  onCreate: () => void
  invalidate: () => void
}

const SERVER_EXPORT_FORMATS = new Set<ExtendedExportFormat>(['csv', 'xlsx', 'xls', 'xlsm', 'xlsb'])

export function RelationsImportExportToolbar({ onImportReport, onCreate, invalidate }: Props) {
  const { canEdit, isAdmin } = useAuth()
  const { t } = useI18n()

  const { exportFile, importAny } = useImportExport({
    invalidate,
    onReport: onImportReport,
    messages: {
      exported: t.relations.toastExported,
      imported: () => t.relations.toastImported,
      importError: t.common.error,
      genericError: t.common.error,
    },
  })

  const handleExport = async (format: ExtendedExportFormat) => {
    await exportFile(async () => {
      if (format === 'csv') {
        await relationsApi.exportCsv()
      } else if (SERVER_EXPORT_FORMATS.has(format)) {
        await relationsApi.exportXlsx()
      } else {
        const rels = await relationsApi.listAll()
        downloadByFormat({ relations: rels }, format, 'relations-export')
      }
    })
  }

  return (
    <EntityImportExportToolbar
      labels={{ export: t.common.export, import: t.common.import, create: t.relations.createRelation }}
      isAdmin={isAdmin}
      canEdit={canEdit}
      onCreate={onCreate}
      onImport={(file) =>
        void importAny(file, (items) => relationsApi.importJson(normalizeRelationImportItems(items)))
      }
      exportFormats={{
        title: t.common.export,
        formatLabel: t.inventory.exportFormat,
        cancelLabel: t.common.cancel,
        submitLabel: t.common.export,
        onExport: handleExport,
      }}
      testIds={{ create: 'relation-create' }}
    />
  )
}
