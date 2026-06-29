import { ArrowRight, Pencil, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useMemo } from 'react'
import { EmptyState, Button } from '@/components/ui'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import type { Relation } from '@/shared/api/types'
import { statusBadge } from '@/lib/utils'
import { relationTypeLabel, relationStatusLabel } from '@/lib/domainLabels'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'

type RelationsTableProps = {
  relations: Relation[]
  isLoading: boolean
  dateLocale: string
  selected: Set<number>
  onToggleAll: () => void
  onToggleOne: (id: number) => void
  onAudit: (id: number) => void
  onEdit: (rel: Relation) => void
  onDelete: (id: number) => void
}

export function RelationsTable({
  relations,
  isLoading,
  dateLocale,
  selected,
  onToggleAll,
  onToggleOne,
  onAudit,
  onEdit,
  onDelete,
}: RelationsTableProps) {
  const { canEdit } = useAuth()
  const { t } = useI18n()

  const columns = useMemo((): VirtualColumn<Relation>[] => {
    const cols: VirtualColumn<Relation>[] = []

    if (canEdit) {
      cols.push({
        id: 'select',
        header: (
          <input
            type="checkbox"
            aria-label={t.relations.colSource}
            checked={selected.size === relations.length && relations.length > 0}
            onChange={onToggleAll}
          />
        ),
        width: '2.5rem',
        cell: (r) => (
          <input
            type="checkbox"
            checked={selected.has(r.id)}
            onChange={() => onToggleOne(r.id)}
            aria-label={`${r.source_name} → ${r.target_name}`}
          />
        ),
      })
    }

    cols.push(
    {
      id: 'source',
      header: t.relations.colSource,
      width: 'minmax(120px, 1.2fr)',
      cell: (r) => (
        <Link to={`/inventory/${r.source_ci_id}`} className="link">
          {r.source_name}
        </Link>
      ),
    },
    {
      id: 'arrow',
      header: '',
      width: '2rem',
      hideMobile: true,
      className: 'text-center text-info',
      cell: () => <ArrowRight className="inline h-4 w-4 text-info" />,
    },
    {
      id: 'target',
      header: t.relations.colTarget,
      width: 'minmax(120px, 1.2fr)',
      cell: (r) => (
        <Link to={`/inventory/${r.target_ci_id}`} className="link">
          {r.target_name}
        </Link>
      ),
    },
    {
      id: 'type',
      header: t.relations.colType,
      width: 'minmax(100px, 1fr)',
      cell: (r) => <span className="badge badge-indigo">{relationTypeLabel(t, r.relation_type)}</span>,
    },
    {
      id: 'status',
      header: t.relations.colStatus,
      width: 'minmax(90px, 0.9fr)',
      hideMobile: true,
      cell: (r) => <span className={`badge ${statusBadge(r.status)}`}>{relationStatusLabel(t, r.status)}</span>,
    },
    {
      id: 'dataSource',
      header: t.relations.colDataSource,
      width: 'minmax(90px, 0.9fr)',
      hideMobile: true,
      className: 'text-[var(--text-muted)]',
      cell: (r) => r.data_source || t.nav.noResults,
    },
    {
      id: 'created',
      header: t.relations.colCreated,
      width: 'minmax(90px, 0.9fr)',
      hideMobile: true,
      className: 'whitespace-nowrap text-xs text-[var(--text-muted)]',
      cell: (r) => (r.created_at ? new Date(r.created_at).toLocaleDateString(dateLocale) : t.nav.noResults),
    },
    {
      id: 'actions',
      header: '',
      width: 'minmax(120px, 1fr)',
      cell: (r) => (
        <div className="flex flex-wrap gap-2">
          <Button variant="table" className="min-h-11 text-xs md:min-h-0" onClick={() => onAudit(r.id)}>
            {t.relations.viewAudit}
          </Button>
          {canEdit && (
            <>
              <Button
                variant="table-primary"
                iconOnly
                className="min-h-11 md:min-h-0"
                onClick={() =>
                  onEdit({
                    ...r,
                    data_source: r.data_source || 'manual',
                  })
                }
                aria-label={t.common.edit}
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="table-danger"
                iconOnly
                className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
                onClick={() => onDelete(r.id)}
                data-testid="relation-delete"
                aria-label={t.common.delete}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      ),
    },
    )

    return cols
  }, [canEdit, dateLocale, onAudit, onDelete, onEdit, onToggleAll, onToggleOne, relations.length, selected, t])

  return (
    <VirtualDataTable
      items={relations}
      columns={columns}
      getRowKey={(r) => r.id}
      isLoading={isLoading}
      ariaLabel={t.relations.title}
      testId="relations-table"
      empty={<EmptyState title={t.relations.emptyTitle} />}
    />
  )
}
