import { useToast } from '@/context/useToast'
import type { ImportReport } from '@/shared/api/types'
import { parseImportFile } from '@/shared/import/parseImportFile'

type Messages = {
  exported: string
  imported: (created: number) => string
  importError: string
  genericError: string
}

type Options = {
  invalidate: () => void
  onReport: (report: ImportReport) => void
  messages: Messages
}

type PreviewImportOptions<TPreview> = {
  normalizeItems?: (items: unknown[]) => unknown[]
  preview: (items: unknown[]) => Promise<TPreview>
  needsMapping: (preview: TPreview) => boolean
  onMappingRequired: (items: unknown[], preview: TPreview) => void
  importItems: (items: unknown[]) => Promise<ImportReport>
}

export function useImportExport({ invalidate, onReport, messages }: Options) {
  const { success, error } = useToast()

  const finishImport = (report: ImportReport) => {
    onReport(report)
    invalidate()
    success(messages.imported(report.created))
  }

  const exportFile = async (fn: () => Promise<void>) => {
    try {
      await fn()
      success(messages.exported)
    } catch (err) {
      error(err instanceof Error ? err.message : messages.genericError)
    }
  }

  const importCsv = async (file: File, importFn: (file: File) => Promise<ImportReport>) => {
    try {
      finishImport(await importFn(file))
    } catch (err) {
      error(err instanceof Error ? err.message : messages.importError)
    }
  }

  const importJson = async (
    file: File,
    importFn: (items: unknown[]) => Promise<ImportReport>,
    extractItems: (parsed: unknown) => unknown[],
  ) => {
    try {
      const parsed = JSON.parse(await file.text())
      finishImport(await importFn(extractItems(parsed)))
    } catch (err) {
      error(err instanceof Error ? err.message : messages.importError)
    }
  }

  const importAny = async (
    file: File,
    importFn: (items: unknown[]) => Promise<ImportReport>,
    normalizeItems?: (items: unknown[]) => unknown[],
  ) => {
    try {
      const parsedItems = await parseImportFile(file)
      const items = normalizeItems ? normalizeItems(parsedItems) : parsedItems
      finishImport(await importFn(items))
    } catch (err) {
      error(err instanceof Error ? err.message : messages.importError)
    }
  }

  const importWithPreview = async <TPreview>(file: File, opts: PreviewImportOptions<TPreview>) => {
    try {
      const parsedItems = await parseImportFile(file)
      const items = opts.normalizeItems ? opts.normalizeItems(parsedItems) : parsedItems
      const preview = await opts.preview(items)
      if (opts.needsMapping(preview)) {
        opts.onMappingRequired(items, preview)
        return
      }
      finishImport(await opts.importItems(items))
    } catch (err) {
      error(err instanceof Error ? err.message : messages.importError)
    }
  }

  const completeMappedImport = async (
    items: unknown[],
    importFn: (items: unknown[], mappings: unknown[]) => Promise<ImportReport>,
    mappings: unknown[],
  ) => {
    try {
      finishImport(await importFn(items, mappings))
    } catch (err) {
      error(err instanceof Error ? err.message : messages.importError)
      throw err
    }
  }

  return { exportFile, importCsv, importJson, importAny, importWithPreview, completeMappedImport }
}
