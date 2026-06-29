import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { invalidateCiQueries } from '@/shared/queryInvalidation'
import { useEntityListPageState } from '@/shared/hooks/useEntityListPageState'
import { useDebouncedValue } from '@/shared/hooks/useDebouncedValue'
import { defaultInventoryFilters } from '@/features/inventory/inventoryFilters'
import type { CiFormState } from '@/features/inventory/inventoryForm'
import { useCiMutations } from '@/features/inventory/hooks/useCiMutations'
import { useInventoryExport } from '@/features/inventory/hooks/useInventoryExport'
import {
  INVENTORY_PAGE_SIZE_DEFAULT,
  INVENTORY_PAGE_SIZES,
  type InventoryPageSize,
  useInventoryQueries,
} from '@/features/inventory/hooks/useInventoryQueries'
import { useInventorySelection } from '@/features/inventory/hooks/useInventorySelection'

export { INVENTORY_PAGE_SIZES }

export function useInventoryPage() {
  const qc = useQueryClient()
  const { canEdit } = useAuth()
  const { t } = useI18n()
  const [view, setView] = useState<'active' | 'recycle'>('active')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState<InventoryPageSize>(INVENTORY_PAGE_SIZE_DEFAULT)
  const {
    filters,
    setFilters,
    showForm,
    setShowForm,
    importReport,
    setImportReport,
  } = useEntityListPageState({ filters: defaultInventoryFilters, form: {} as CiFormState })

  const debouncedFilters = useDebouncedValue(filters, 300)

  useEffect(() => {
    setPage(1)
  }, [debouncedFilters, view, pageSize])

  const { items, isLoading, types, businessServices, totalItems, totalPages } = useInventoryQueries(
    view,
    debouncedFilters,
    page,
    pageSize,
  )
  const { selected, toggleAll, toggleOne, clearSelection } = useInventorySelection(items.map((c) => c.id))
  const { showExport, setShowExport, exportFilters, setExportFilters, exportFiltered } = useInventoryExport()

  const { createMut, deleteMut, restoreMut, purgeMut, bulkMut, bulkDeleteMut } = useCiMutations({
    t,
    selected,
    onCreateSuccess: () => setShowForm(false),
    onBulkSuccess: clearSelection,
  })

  return {
    t,
    canEdit,
    view,
    setView,
    filters,
    setFilters,
    page,
    setPage,
    pageSize,
    setPageSize: (size: number) => setPageSize(size as InventoryPageSize),
    totalItems,
    totalPages,
    selected,
    showForm,
    setShowForm,
    importReport,
    setImportReport,
    showExport,
    setShowExport,
    exportFilters,
    setExportFilters,
    types,
    businessServices,
    items,
    isLoading,
    createMut,
    deleteMut,
    restoreMut,
    purgeMut,
    bulkMut,
    bulkDeleteMut,
    toggleAll,
    toggleOne,
    exportFiltered,
    onAutodiscoverApplied: () => invalidateCiQueries(qc),
  }
}
