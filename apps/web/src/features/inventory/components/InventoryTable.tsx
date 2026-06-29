import { ArchiveRestore, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useMemo } from 'react'
import { EmptyState, Button } from '@/components/ui'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import type { CI } from '@/shared/api'
import { criticalityBadge, statusBadge } from '@/lib/utils'
import { ciStatusLabel, criticalityLabel } from '@/lib/domainLabels'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'

interface InventoryTableProps {
  items: CI[]
  view: 'active' | 'recycle'
  isLoading: boolean
  selected: Set<number>
  onToggleAll: () => void
  onToggleOne: (id: number) => void
  onDelete: (id: number) => void
  onRestore: (id: number) => void
  onPurge: (id: number) => void
}

export function InventoryTable({
  items,
  view,
  isLoading,
  selected,
  onToggleAll,
  onToggleOne,
  onDelete,
  onRestore,
  onPurge,
}: InventoryTableProps) {
  const { canEdit } = useAuth()
  const { t } = useI18n()

  const columns = useMemo((): VirtualColumn<CI>[] => {
    const cols: VirtualColumn<CI>[] = []

    if (canEdit && view === 'active') {
      cols.push({
        id: 'select',
        header: (
          <input
            type="checkbox"
            aria-label={t.inventory.colName}
            checked={selected.size === items.length && items.length > 0}
            onChange={onToggleAll}
          />
        ),
        width: '2.5rem',
        cell: (ci) => (
          <input
            type="checkbox"
            checked={selected.has(ci.id)}
            onChange={() => onToggleOne(ci.id)}
            aria-label={ci.name}
          />
        ),
      })
    }

    cols.push(
      {
        id: 'id',
        header: 'ID',
        width: '4rem',
        className: 'text-[var(--text-muted)]',
        cell: (ci) => `#${ci.id}`,
      },
      {
        id: 'name',
        header: t.inventory.colName,
        width: 'minmax(140px, 1.5fr)',
        cell: (ci) => (
          <Link to={`/inventory/${ci.id}`} className="link">
            {ci.name}
          </Link>
        ),
      },
      {
        id: 'type',
        header: t.inventory.colType,
        width: 'minmax(100px, 1fr)',
        hideMobile: true,
        cell: (ci) => ci.type || '—',
      },
      {
        id: 'status',
        header: t.inventory.colStatus,
        width: 'minmax(90px, 0.9fr)',
        cell: (ci) => <span className={`badge ${statusBadge(ci.status)}`}>{ciStatusLabel(t, ci.status)}</span>,
      },
      {
        id: 'criticality',
        header: t.inventory.colCriticality,
        width: 'minmax(90px, 0.9fr)',
        hideMobile: true,
        cell: (ci) => (
          <span className={`badge ${criticalityBadge(ci.criticality)}`}>{ci.criticality ? criticalityLabel(t, ci.criticality) : '—'}</span>
        ),
      },
      {
        id: 'environment',
        header: t.inventory.colEnvironment,
        width: 'minmax(80px, 0.8fr)',
        hideMobile: true,
        cell: (ci) => ci.environment || '—',
      },
      {
        id: 'owner',
        header: t.inventory.colOwner,
        width: 'minmax(80px, 0.8fr)',
        hideMobile: true,
        cell: (ci) => ci.owner || '—',
      },
      {
        id: 'actions',
        header: '',
        width: view === 'recycle' ? '7rem' : '3.5rem',
        cellClassName: 'virtual-table-td-actions',
        cell: (ci) => (
          <div className={view === 'recycle' ? 'flex items-center justify-end gap-1.5' : undefined}>
            {canEdit && view === 'active' && (
              <Button
                variant="table-danger"
                iconOnly
                className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
                onClick={() => onDelete(ci.id)}
                data-testid="ci-delete"
                aria-label={t.common.delete}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            )}
            {canEdit && view === 'recycle' && (
              <>
                <Button
                  variant="table-primary"
                  iconOnly
                  className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
                  onClick={() => onRestore(ci.id)}
                  title={t.common.restore}
                  aria-label={t.common.restore}
                  data-testid="inventory-restore"
                >
                  <ArchiveRestore className="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="table-danger"
                  iconOnly
                  className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
                  onClick={() => onPurge(ci.id)}
                  title={t.inventory.purge}
                  aria-label={t.inventory.purge}
                  data-testid="inventory-purge"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </>
            )}
          </div>
        ),
      },
    )

    return cols
  }, [canEdit, view, items.length, selected, t, onToggleAll, onToggleOne, onDelete, onRestore, onPurge])

  return (
    <VirtualDataTable
      items={items}
      columns={columns}
      getRowKey={(ci) => ci.id}
      isLoading={isLoading}
      ariaLabel={t.inventory.title}
      testId="inventory-table"
      empty={(
        <EmptyState
          title={t.inventory.emptyTitle}
          hint={canEdit ? t.inventory.emptyHint : undefined}
        />
      )}
    />
  )
}
