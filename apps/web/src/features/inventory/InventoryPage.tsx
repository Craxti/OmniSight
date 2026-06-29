import { useState } from 'react'
import { ImportReportView, Modal, PageHeader } from '@/components/ui'
import { AutodiscoverModal } from '@/shared/components/autodiscover'
import { ConfirmDialog } from '@/shared/components/ConfirmDialog'
import { PaginationBar } from '@/shared/components/PaginationBar'
import { fmt } from '@/i18n/messages'
import { CiCreateModal } from '@/features/inventory/components/CiCreateModal'
import { CiImportExportToolbar } from '@/features/inventory/components/CiImportExportToolbar'
import { InventoryBulkBar } from '@/features/inventory/components/InventoryBulkBar'
import { InventoryExportModal } from '@/features/inventory/components/InventoryExportModal'
import { InventoryFilters } from '@/features/inventory/components/InventoryFilters'
import { InventoryTable } from '@/features/inventory/components/InventoryTable'
import { InventoryViewTabs } from '@/features/inventory/components/InventoryViewTabs'
import { INVENTORY_PAGE_SIZES, useInventoryPage } from '@/features/inventory/hooks/useInventoryPage'

export default function InventoryPage() {
  const [autodiscoverOpen, setAutodiscoverOpen] = useState(false)
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)
  const {
    t,
    canEdit,
    view,
    setView,
    filters,
    setFilters,
    page,
    setPage,
    pageSize,
    setPageSize,
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
    onAutodiscoverApplied,
  } = useInventoryPage()

  return (
    <div className="space-y-6" data-testid="inventory-page">
      <PageHeader
        title={t.inventory.title}
        subtitle={t.inventory.subtitle}
        actions={(
          <CiImportExportToolbar
            onImportReport={setImportReport}
            onOpenExport={() => setShowExport(true)}
            onAutodiscover={() => setAutodiscoverOpen(true)}
            onCreate={() => setShowForm(true)}
          />
        )}
      />

      <InventoryViewTabs view={view} onChange={setView} />

      {view === 'active' && <InventoryFilters filters={filters} types={types} onChange={setFilters} />}

      {canEdit && selected.size > 0 && view === 'active' && (
        <InventoryBulkBar
          count={selected.size}
          onBulkStatus={(status) => bulkMut.mutate(status)}
          onBulkDelete={() => setBulkDeleteOpen(true)}
          deletePending={bulkDeleteMut.isPending}
        />
      )}

      <InventoryTable
        items={items}
        view={view}
        isLoading={isLoading}
        selected={selected}
        onToggleAll={toggleAll}
        onToggleOne={toggleOne}
        onDelete={(id) => deleteMut.mutate(id)}
        onRestore={(id) => restoreMut.mutate(id)}
        onPurge={(id) => purgeMut.mutate(id)}
      />

      {!isLoading && totalItems > 0 && view === 'active' && (
        <PaginationBar
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          pageSize={pageSize}
          pageSizeOptions={INVENTORY_PAGE_SIZES}
          onPageSizeChange={setPageSize}
          summary={`${totalItems} ${t.inventory.title.toLowerCase()}`}
        />
      )}

      <CiCreateModal
        open={showForm}
        types={types}
        isPending={createMut.isPending}
        onClose={() => setShowForm(false)}
        onSubmit={(form) => createMut.mutate(form)}
      />

      <Modal open={!!importReport} onClose={() => setImportReport(null)} title={t.inventory.importReport} wide>
        {importReport && <ImportReportView report={importReport} />}
      </Modal>

      <InventoryExportModal
        open={showExport}
        filters={exportFilters}
        types={types}
        businessServices={businessServices}
        onClose={() => setShowExport(false)}
        onChange={setExportFilters}
        onExport={exportFiltered}
      />

      <AutodiscoverModal
        open={autodiscoverOpen}
        onClose={() => setAutodiscoverOpen(false)}
        scopeDefaults={{ scope_mode: 'all' }}
        onApplied={onAutodiscoverApplied}
      />

      <ConfirmDialog
        open={bulkDeleteOpen}
        title={t.common.delete}
        message={fmt(t.inventory.bulkDeleteConfirm, { n: selected.size })}
        confirmLabel={t.common.delete}
        pending={bulkDeleteMut.isPending}
        confirmTestId="inventory-bulk-delete-confirm"
        onClose={() => setBulkDeleteOpen(false)}
        onConfirm={() => {
          bulkDeleteMut.mutate(undefined, {
            onSuccess: () => setBulkDeleteOpen(false),
          })
        }}
      />
    </div>
  )
}
