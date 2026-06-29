import { ImportReportView, Modal, PageHeader, Button } from '@/components/ui'
import { AuditHistoryList } from '@/shared/components/AuditHistoryList'
import { ConfirmDialog } from '@/shared/components/ConfirmDialog'
import { PaginationBar } from '@/shared/components/PaginationBar'
import { RelationValidationBanner } from '@/shared/components/RelationValidationBanner'
import { fmt } from '@/i18n/messages'
import { RelationCreateModal } from '@/features/relations/components/RelationCreateModal'
import { RelationEditModal } from '@/features/relations/components/RelationEditModal'
import { RelationsBulkBar } from '@/features/relations/components/RelationsBulkBar'
import { RelationsFilters } from '@/features/relations/components/RelationsFilters'
import { RelationsImportExportToolbar } from '@/features/relations/components/RelationsImportExportToolbar'
import { RelationsTable } from '@/features/relations/components/RelationsTable'
import { useRelationsPage } from '@/features/relations/hooks/useRelationsPage'
import { useState } from 'react'

export default function RelationsPage() {
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)
  const {
    t,
    canEdit,
    dateLocale,
    showForm,
    setShowForm,
    auditRelId,
    setAuditRelId,
    importReport,
    setImportReport,
    filters,
    setFilters,
    editRel,
    setEditRel,
    isLoading,
    cis,
    validation,
    validate,
    relAudit,
    createMut,
    deleteMut,
    updateMut,
    bulkMut,
    bulkDeleteMut,
    invalidate,
    relations,
    selected,
    toggleAll,
    toggleOne,
    page,
    setPage,
    totalPages,
    totalItems,
  } = useRelationsPage()

  return (
    <div className="space-y-6" data-testid="relations-page">
      <PageHeader
        title={t.relations.title}
        subtitle={t.relations.subtitle}
        actions={(
          <>
            <Button variant="secondary" onClick={() => validate()}>
              {t.relations.validate}
            </Button>
            <RelationsImportExportToolbar
              onImportReport={setImportReport}
              onCreate={() => setShowForm(true)}
              invalidate={invalidate}
            />
          </>
        )}
      />

      {validation && (
        <RelationValidationBanner
          validation={validation}
          validLabel={t.relations.modelValid}
          issuesLabel={t.relations.issues}
          className="card p-4"
        />
      )}

      <RelationsFilters filters={filters} onChange={setFilters} />

      {canEdit && selected.size > 0 && (
        <RelationsBulkBar
          count={selected.size}
          onBulkStatus={(status) => bulkMut.mutate(status)}
          onBulkDelete={() => setBulkDeleteOpen(true)}
          deletePending={bulkDeleteMut.isPending}
        />
      )}

      <RelationsTable
        relations={relations}
        isLoading={isLoading}
        dateLocale={dateLocale}
        selected={selected}
        onToggleAll={toggleAll}
        onToggleOne={toggleOne}
        onAudit={setAuditRelId}
        onEdit={(r) =>
          setEditRel({
            id: r.id,
            relation_type: r.relation_type,
            status: r.status,
            data_source: r.data_source || 'manual',
          })
        }
        onDelete={(id) => deleteMut.mutate(id)}
      />

      {!isLoading && totalItems > 0 && (
        <PaginationBar
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          summary={`${totalItems} ${t.relations.title.toLowerCase()}`}
        />
      )}

      <RelationCreateModal
        open={showForm}
        cis={(cis?.items || []).map((c) => ({ id: c.id, name: c.name }))}
        pending={createMut.isPending}
        onClose={() => setShowForm(false)}
        onSubmit={(form) => createMut.mutate(form)}
      />

      <RelationEditModal
        editRel={editRel}
        pending={updateMut.isPending}
        onClose={() => setEditRel(null)}
        onSubmit={(rel) => updateMut.mutate(rel)}
      />

      <Modal open={auditRelId !== null} onClose={() => setAuditRelId(null)} title={auditRelId !== null ? fmt(t.relations.historyTitle, { id: auditRelId }) : ''} wide>
        <AuditHistoryList entries={relAudit ?? []} variant="relation" />
      </Modal>

      <Modal open={!!importReport} onClose={() => setImportReport(null)} title={t.relations.importReport} wide>
        {importReport && <ImportReportView report={importReport} />}
      </Modal>

      <ConfirmDialog
        open={bulkDeleteOpen}
        title={t.common.delete}
        message={fmt(t.relations.bulkDeleteConfirm, { n: selected.size })}
        confirmLabel={t.common.delete}
        pending={bulkDeleteMut.isPending}
        confirmTestId="relations-bulk-delete-confirm"
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
