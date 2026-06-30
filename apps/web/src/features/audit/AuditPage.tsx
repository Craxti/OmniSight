import { useMemo } from 'react'
import { AuditDiffView, EmptyState, PageHeader } from '@/components/ui'
import { auditActionLabel, auditEntityTypeLabel } from '@/features/audit/auditLabels'
import { useAuditPage } from '@/features/audit/hooks/useAuditPage'
import type { AuditEntry } from '@/shared/api/types'
import { FilterPanel } from '@/shared/components/FilterPanel'
import { PaginationBar } from '@/shared/components/PaginationBar'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'

export default function AuditPage() {
  const {
    t,
    dateLocale,
    entityType,
    setEntityType,
    action,
    setAction,
    userEmail,
    setUserEmail,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    page,
    setPage,
    resetPage,
    isLoading,
    items,
    total,
    totalPages,
  } = useAuditPage()

  const columns = useMemo((): VirtualColumn<AuditEntry>[] => {
    return [
    {
      id: 'date',
      header: t.audit.colDate,
      width: 'minmax(140px, 1.1fr)',
      className: 'whitespace-nowrap text-[var(--text-muted)]',
      cell: (a) => (a.created_at ? new Date(a.created_at).toLocaleString(dateLocale) : t.nav.noResults),
    },
    {
      id: 'action',
      header: t.audit.colAction,
      width: 'minmax(90px, 0.9fr)',
      cell: (a) => <span className="badge badge-indigo">{auditActionLabel(t.audit, a.action)}</span>,
    },
    {
      id: 'type',
      header: t.audit.colType,
      width: 'minmax(80px, 0.8fr)',
      hideMobile: true,
      cell: (a) => auditEntityTypeLabel(t.audit, a.entity_type),
    },
    {
      id: 'id',
      header: 'ID',
      width: '4rem',
      cell: (a) => a.entity_id ?? t.nav.noResults,
    },
    {
      id: 'user',
      header: t.audit.colUser,
      width: 'minmax(120px, 1fr)',
      hideMobile: true,
      className: 'text-[var(--text-muted)]',
      cell: (a) => a.user_email,
    },
    {
      id: 'changes',
      header: t.audit.colChanges,
      width: 'minmax(200px, 2fr)',
      cellClassName: 'virtual-table-td-multiline',
      cell: (a) => <AuditDiffView oldValue={a.old_value} newValue={a.new_value} variant="inline" />,
    },
  ]
  }, [dateLocale, t])

  return (
    <div className="space-y-6">
      <PageHeader title={t.audit.title} subtitle={t.audit.subtitle} />

      <FilterPanel testId="audit-filters">
        <select className="input w-full" value={entityType} onChange={(e) => { setEntityType(e.target.value); resetPage() }} aria-label={t.audit.filterEntityType}>
          <option value="">{t.audit.allTypes}</option>
          <option value="ci">{t.audit.entityCi}</option>
          <option value="relation">{t.audit.entityRelation}</option>
          <option value="import">{t.audit.entityImport}</option>
          <option value="export">{t.audit.entityExport}</option>
          <option value="ci_type">{t.audit.entityCiType}</option>
        </select>
        <select className="input w-full" value={action} onChange={(e) => { setAction(e.target.value); resetPage() }} aria-label={t.audit.filterAction}>
          <option value="">{t.audit.allActions}</option>
          <option value="create">{t.audit.actionCreate}</option>
          <option value="update">{t.audit.actionUpdate}</option>
          <option value="delete">{t.audit.actionDelete}</option>
          <option value="purge">{t.audit.actionPurge}</option>
          <option value="restore">{t.audit.actionRestore}</option>
          <option value="export_full">{t.audit.actionExportFull}</option>
          <option value="export_rsm_csv">{t.audit.actionExportRsmCsv}</option>
          <option value="export_rsm_xlsx">{t.audit.actionExportRsmXlsx}</option>
          <option value="import_create">{t.audit.actionImportCreate}</option>
          <option value="import_update">{t.audit.actionImportUpdate}</option>
          <option value="import_ci_json">{t.audit.actionImportCiJson}</option>
          <option value="import_relations_json">{t.audit.actionImportRelationsJson}</option>
          <option value="import_relations_csv">{t.audit.actionImportRelationsCsv}</option>
        </select>
        <input className="input w-full" placeholder={t.audit.userEmail} value={userEmail} onChange={(e) => { setUserEmail(e.target.value); resetPage() }} aria-label={t.audit.filterUserEmail} />
        <input className="input w-full" type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); resetPage() }} aria-label={t.audit.filterDateFrom} />
        <input className="input w-full" type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); resetPage() }} aria-label={t.audit.filterDateTo} />
      </FilterPanel>

      <VirtualDataTable
        items={items}
        columns={columns}
        getRowKey={(a) => a.id}
        isLoading={isLoading}
        ariaLabel={t.audit.title}
        testId="audit-table"
        virtualized={false}
        empty={<EmptyState title={t.nav.noResults} hint={t.audit.subtitle} />}
      />

      {!isLoading && total > 0 && (
        <PaginationBar
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          summary={`${total} ${t.audit.title.toLowerCase()}`}
        />
      )}
    </div>
  )
}
