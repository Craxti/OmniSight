import { AuditDiffView } from '@/components/ui'
import { auditActionLabel } from '@/features/audit/auditLabels'
import { useI18n } from '@/context/useI18n'
import type { AuditEntry } from '@/shared/api/types'
import { fmt } from '@/i18n/messages'

type Props = {
  entries: AuditEntry[]
  variant?: 'default' | 'relation'
}

export function AuditHistoryList({ entries, variant = 'default' }: Props) {
  const { t, dateLocale } = useI18n()

  if (entries.length === 0) {
    return <p className="text-[var(--text-muted)]">{t.ciDetail.noHistory}</p>
  }

  return (
    <div className="space-y-3">
      {entries.map((entry) => (
        <AuditHistoryItem key={entry.id} entry={entry} variant={variant} dateLocale={dateLocale} t={t} />
      ))}
    </div>
  )
}

function AuditHistoryItem({
  entry,
  variant,
  dateLocale,
  t,
}: {
  entry: AuditEntry
  variant: 'default' | 'relation'
  dateLocale: string
  t: ReturnType<typeof useI18n>['t']
}) {
  const snapshot = entry.new_value ?? entry.old_value
  const relationHint =
    variant === 'default' &&
    entry.entity_type === 'relation' &&
    snapshot
      ? fmt(t.ciDetail.historyRelation, {
          id: entry.entity_id ?? '—',
          source: String(snapshot.source_name ?? snapshot.source_ci_id ?? '—'),
          target: String(snapshot.target_name ?? snapshot.target_ci_id ?? '—'),
          type: String(snapshot.relation_type ?? '—'),
        })
      : null

  return (
    <div className="rounded-lg border border-[var(--border-subtle)] p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span className="badge badge-indigo">{auditActionLabel(t.audit, entry.action)}</span>
        {variant === 'default' && entry.entity_type === 'relation' ? (
          <span className="badge badge-gray">{t.ciDetail.tabRelations}</span>
        ) : null}
        <span className="text-[var(--text-muted)]">
          {entry.created_at ? new Date(entry.created_at).toLocaleString(dateLocale) : ''}
        </span>
        <span className="text-[var(--text-muted)]">{entry.user_email}</span>
      </div>
      {relationHint ? <div className="mt-1 text-xs text-[var(--link)]">{relationHint}</div> : null}
      <AuditDiffView oldValue={entry.old_value ?? null} newValue={entry.new_value ?? null} />
    </div>
  )
}
