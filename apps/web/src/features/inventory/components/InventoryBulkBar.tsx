import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { ciStatusLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'

interface Props {
  count: number
  onBulkStatus: (status: string) => void
  onBulkDelete: () => void
  deletePending?: boolean
}

export function InventoryBulkBar({ count, onBulkStatus, onBulkDelete, deletePending }: Props) {
  const { t } = useI18n()
  const { bulkCiStatuses } = useDomainConstants()

  return (
    <div className="card flex flex-wrap items-center gap-3 p-3" data-testid="inventory-bulk-bar">
      <span className="text-sm text-[var(--text-muted)]">
        {t.inventory.selected}: {count}
      </span>
      <select
        className="input max-w-xs"
        defaultValue=""
        data-testid="inventory-bulk-status"
        onChange={(e) => {
          if (e.target.value) onBulkStatus(e.target.value)
          e.target.value = ''
        }}
      >
        <option value="">{t.inventory.changeStatus}</option>
        {bulkCiStatuses.map((s) => (
          <option key={s} value={s}>
            {ciStatusLabel(t, s)}
          </option>
        ))}
      </select>
      <Button
        variant="danger"
        className="min-h-11 md:min-h-0"
        onClick={onBulkDelete}
        disabled={deletePending}
        data-testid="inventory-bulk-delete"
      >
        <Trash2 className="h-4 w-4" />
        {t.common.delete}
      </Button>
    </div>
  )
}
