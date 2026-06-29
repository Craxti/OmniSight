import { useState } from 'react'
import type { ImportReport } from '@/shared/api/types'

type EntityListPageDefaults<TFilters, TForm> = {
  filters: TFilters
  form: TForm
}

/** Shared list-page state: filters, create form, import report. */
export function useEntityListPageState<TFilters, TForm>(defaults: EntityListPageDefaults<TFilters, TForm>) {
  const [filters, setFilters] = useState(defaults.filters)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(defaults.form)
  const [importReport, setImportReport] = useState<ImportReport | null>(null)

  return {
    filters,
    setFilters,
    showForm,
    setShowForm,
    form,
    setForm,
    importReport,
    setImportReport,
  }
}
