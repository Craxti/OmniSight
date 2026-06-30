import { useMemo } from 'react'
import { ChevronRight, History, RefreshCw } from 'lucide-react'
import { Button, EmptyState, Modal } from '@/components/ui'
import { CorrelationIngestJournalDetail } from '@/features/correlation/components/CorrelationIngestJournalDetail'
import { useCorrelationIngestJournal } from '@/features/correlation/hooks/useCorrelationIngestJournal'
import { useI18n } from '@/context/useI18n'
import type { CorrelationIngestLogSummary } from '@/shared/api/types'
import { FilterPanel } from '@/shared/components/FilterPanel'
import { ListRowsSkeleton } from '@/shared/components/PageSkeletons'
import { PaginationBar } from '@/shared/components/PaginationBar'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'

export function CorrelationIngestJournal() {
  const { t, dateLocale } = useI18n()
  const {
    page,
    setPage,
    sourceFilter,
    setSourceFilter,
    resetPage,
    selectedId,
    openLog,
    closeLog,
    items,
    total,
    totalPages,
    isLoading,
    isDetailLoading,
    detail,
    refetch,
  } = useCorrelationIngestJournal()

  const columns = useMemo((): VirtualColumn<CorrelationIngestLogSummary>[] => {
    return [
      {
        id: 'created_at',
        header: t.correlation.journalColTime,
        width: 'minmax(140px, 1.1fr)',
        className: 'whitespace-nowrap text-[var(--text-muted)]',
        cell: (row) =>
          row.created_at ? new Date(row.created_at).toLocaleString(dateLocale) : t.nav.noResults,
      },
      {
        id: 'source',
        header: t.correlation.journalColSource,
        width: 'minmax(100px, 1fr)',
        cell: (row) => (
          <span className="font-medium text-[var(--text-primary)]">
            {row.source || t.correlation.journalSourceUnknown}
          </span>
        ),
      },
      {
        id: 'alerts',
        header: t.correlation.journalColAlerts,
        width: 'minmax(70px, 0.6fr)',
        cell: (row) => row.alert_count,
      },
      {
        id: 'resolved',
        header: t.correlation.journalColResolved,
        width: 'minmax(70px, 0.6fr)',
        cell: (row) => (
          <span>
            <span className="text-success">{row.resolved_count}</span>
            <span className="text-[var(--text-muted)]"> / </span>
            <span className="text-warning">{row.unresolved_count}</span>
          </span>
        ),
      },
      {
        id: 'chain',
        header: t.correlation.journalColChain,
        width: 'minmax(90px, 0.8fr)',
        cell: (row) => (
          <span className={row.chain_related ? 'badge badge-green' : 'badge badge-gray'}>
            {row.chain_related ? t.correlation.chainRelated : t.correlation.incidentSeparate}
          </span>
        ),
      },
      {
        id: 'actions',
        header: '',
        width: '2.5rem',
        hideMobile: true,
        cell: () => <ChevronRight className="h-4 w-4 text-[var(--text-muted)]" aria-hidden />,
      },
    ]
  }, [t, dateLocale])

  const modalTitle =
    selectedId != null
      ? `${t.correlation.journalDetailTitle} #${selectedId}${detail?.source ? ` · ${detail.source}` : ''}`
      : ''

  return (
    <div className="space-y-4" data-testid="correlation-ingest-journal">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-semibold text-[var(--text-primary)]">
          <History className="h-5 w-5 text-[var(--text-muted)]" />
          {t.correlation.journalTitle}
        </h2>
        <Button variant="secondary" onClick={() => void refetch()} data-testid="correlation-journal-refresh">
          <RefreshCw className="h-4 w-4" /> {t.correlation.journalRefresh}
        </Button>
      </div>
      <p className="text-sm text-[var(--text-muted)]">{t.correlation.journalHint}</p>

      <FilterPanel testId="correlation-journal-filters">
        <input
          className="input w-full"
          value={sourceFilter}
          onChange={(e) => {
            setSourceFilter(e.target.value)
            resetPage()
          }}
          placeholder={t.correlation.journalFilterSource}
          aria-label={t.correlation.journalFilterSource}
        />
      </FilterPanel>

      {items.length === 0 && !isLoading ? (
        <EmptyState title={t.correlation.journalEmpty} />
      ) : (
        <VirtualDataTable
          columns={columns}
          items={items}
          isLoading={isLoading}
          getRowKey={(row) => row.id}
          ariaLabel={t.correlation.journalTitle}
          testId="correlation-journal-table"
          virtualized={false}
          onRowClick={(row) => openLog(row.id)}
          isRowSelected={(row) => row.id === selectedId}
          empty={<EmptyState title={t.correlation.journalEmpty} />}
        />
      )}

      <PaginationBar
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
        pageBase="zero"
        summary={`${total} ${t.correlation.journalTitle.toLowerCase()}`}
      />

      <Modal
        open={selectedId != null}
        onClose={closeLog}
        title={modalTitle}
        wide
        testId="correlation-journal-detail-modal"
      >
        {isDetailLoading || !detail ? (
          <ListRowsSkeleton rows={4} />
        ) : (
          <CorrelationIngestJournalDetail detail={detail} />
        )}
      </Modal>
    </div>
  )
}
