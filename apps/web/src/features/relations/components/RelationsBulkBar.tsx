import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { relationStatusLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'

interface Props {
  count: number
  onBulkStatus: (status: string) => void
  onBulkDelete: () => void
  deletePending?: boolean
}

export function RelationsBulkBar({ count, onBulkStatus, onBulkDelete, deletePending }: Props) {
  const { t } = useI18n()
  const { relationStatuses } = useDomainConstants()
  const bulkRelationStatuses = relationStatuses.filter((s) => s !== 'archived')

  return (
    <div className="card flex flex-wrap items-center gap-3 p-3" data-testid="relations-bulk-bar">
      <span className="text-sm text-[var(--text-muted)]">
        {t.relations.selected}: {count}
      </span>
      <select
        className="input max-w-xs"
        defaultValue=""
        data-testid="relations-bulk-status"
        onChange={(e) => {
          if (e.target.value) onBulkStatus(e.target.value)
          e.target.value = ''
        }}
      >
        <option value="">{t.relations.changeStatus}</option>
        {bulkRelationStatuses.map((s) => (
          <option key={s} value={s}>
            {relationStatusLabel(t, s)}
          </option>
        ))}
      </select>
      <Button
        variant="danger"
        className="min-h-11 md:min-h-0"
        onClick={onBulkDelete}
        disabled={deletePending}
        data-testid="relations-bulk-delete"
      >
        <Trash2 className="h-4 w-4" />
        {t.common.delete}
      </Button>
    </div>
  )
}
