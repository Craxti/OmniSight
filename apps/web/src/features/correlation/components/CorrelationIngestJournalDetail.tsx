import { CorrelationIngestResultView } from '@/features/correlation/components/CorrelationIngestResultView'
import {
  CorrelationIngestResolveTable,
  formatAlertIdentifiers,
} from '@/features/correlation/components/CorrelationIngestResolveTable'
import { useI18n } from '@/context/useI18n'
import type { CorrelationIngestLogDetail } from '@/shared/api/types'
import { JsonViewer } from '@/shared/components/JsonViewer'

type Props = {
  detail: CorrelationIngestLogDetail
}

export function CorrelationIngestJournalDetail({ detail }: Props) {
  const { t, dateLocale } = useI18n()
  const receivedAt = detail.created_at ? new Date(detail.created_at).toLocaleString(dateLocale) : '—'

  return (
    <div className="space-y-4" data-testid="correlation-journal-detail-body">
      <div className="grid gap-3 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <div className="text-xs text-[var(--text-muted)]">{t.correlation.journalColTime}</div>
          <div className="mt-1 font-medium text-[var(--text-primary)]">{receivedAt}</div>
        </div>
        <div>
          <div className="text-xs text-[var(--text-muted)]">{t.correlation.journalColSource}</div>
          <div className="mt-1 font-medium text-[var(--text-primary)]">
            {detail.source || t.correlation.journalSourceUnknown}
          </div>
        </div>
        <div>
          <div className="text-xs text-[var(--text-muted)]">{t.correlation.journalColAlerts}</div>
          <div className="mt-1 font-medium text-[var(--text-primary)]">{detail.alert_count}</div>
        </div>
        <div>
          <div className="text-xs text-[var(--text-muted)]">{t.correlation.journalColChain}</div>
          <div className="mt-1">
            <span className={detail.chain_related ? 'badge badge-green' : 'badge badge-gray'}>
              {detail.chain_related ? t.correlation.chainRelated : t.correlation.incidentSeparate}
            </span>
          </div>
        </div>
      </div>

      <div className="card p-5">
        <h3 className="mb-3 font-semibold text-[var(--text-primary)]">{t.correlation.journalIncomingTitle}</h3>
        <div className="space-y-2">
          {detail.alerts.map((alert, index) => (
            <div
              key={index}
              className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] px-3 py-2 font-mono text-xs text-[var(--text-primary)]"
            >
              <span className="mr-2 text-[var(--text-muted)]">#{index + 1}</span>
              {formatAlertIdentifiers(alert)}
            </div>
          ))}
        </div>
        <details className="mt-4">
          <summary className="cursor-pointer text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)]">
            {t.correlation.journalRawRequest}
          </summary>
          <div className="mt-2">
            <JsonViewer value={detail.alerts} maxHeight="10rem" />
          </div>
        </details>
      </div>

      <CorrelationIngestResolveTable ingestResult={detail.result} />

      <div>
        <h3 className="mb-3 font-semibold text-[var(--text-primary)]">{t.correlation.journalOutcomeTitle}</h3>
        <CorrelationIngestResultView ingestResult={detail.result} />
      </div>
    </div>
  )
}
