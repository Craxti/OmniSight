import { AlertTriangle } from 'lucide-react'
import { useI18n } from '@/context/useI18n'
import { fmt } from '@/i18n/messages'
import { useCorrelationAlertWarnings } from '@/features/correlation/hooks/useCorrelationAlertWarnings'
import type { AlertRow } from '@/shared/constants'

type Props = {
  alerts: AlertRow[]
  externalIdFields: readonly string[]
}

export function CorrelationIngestWarnings({ alerts, externalIdFields }: Props) {
  const { t } = useI18n()
  const { checking, hasWarnings, emptyRowNumbers, unresolvedHints } = useCorrelationAlertWarnings(
    alerts,
    externalIdFields,
    t,
  )

  if (!hasWarnings) return null

  return (
    <div className="alert alert-warning mb-4 space-y-2 text-sm" data-testid="correlation-ingest-warnings">
      {checking && <p className="text-[var(--text-muted)]">{t.correlation.ingestWarnChecking}</p>}
      {emptyRowNumbers.length > 0 && (
        <p className="flex items-start gap-2">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          {fmt(t.correlation.ingestWarnEmptyRows, { rows: emptyRowNumbers.join(', ') })}
        </p>
      )}
      {unresolvedHints.length > 0 && (
        <p className="flex items-start gap-2">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          {fmt(t.correlation.ingestWarnUnresolved, { fields: unresolvedHints.join('; ') })}
        </p>
      )}
    </div>
  )
}
