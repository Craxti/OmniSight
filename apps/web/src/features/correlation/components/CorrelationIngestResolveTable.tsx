import { useI18n } from '@/context/useI18n'
import { externalIdFieldLabel } from '@/lib/domainLabels'
import type { CorrelationIngestResponse } from '@/shared/api/types'

export function formatAlertIdentifiers(alert: Record<string, string>): string {
  const parts = Object.entries(alert).filter(([, value]) => value)
  if (!parts.length) return '—'
  return parts.map(([key, value]) => `${key}=${value}`).join(', ')
}

type Props = {
  ingestResult: CorrelationIngestResponse
}

export function CorrelationIngestResolveTable({ ingestResult }: Props) {
  const { t } = useI18n()
  const rows = [
    ...ingestResult.resolve.resolved.map((item) => ({ ...item, status: 'resolved' as const })),
    ...ingestResult.resolve.unresolved.map((item) => ({ ...item, status: 'unresolved' as const })),
  ]

  if (!rows.length) return null

  return (
    <div className="card p-5" data-testid="correlation-ingest-resolve-table">
      <h3 className="mb-3 font-semibold text-[var(--text-primary)]">{t.correlation.journalResolveTitle}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border-subtle)] text-left text-xs text-[var(--text-muted)]">
              <th className="pb-2 pr-4 font-medium">{t.correlation.journalResolveColAlert}</th>
              <th className="pb-2 pr-4 font-medium">{t.correlation.journalResolveColStatus}</th>
              <th className="pb-2 font-medium">{t.correlation.journalResolveColCi}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index} className="border-b border-[var(--border-subtle)] last:border-0">
                <td className="py-2.5 pr-4 align-top font-mono text-xs text-[var(--text-primary)]">
                  {Object.entries(row.alert).map(([field, value]) =>
                    value ? (
                      <div key={field}>
                        <span className="text-[var(--text-muted)]">{externalIdFieldLabel(t, field)}: </span>
                        {String(value)}
                      </div>
                    ) : null,
                  )}
                </td>
                <td className="py-2.5 pr-4 align-top">
                  {row.status === 'resolved' ? (
                    <span className="badge badge-green">{t.correlation.resolved}</span>
                  ) : (
                    <span className="badge badge-gray">{t.correlation.unresolved}</span>
                  )}
                  {row.ambiguous && (
                    <span className="ml-2 badge badge-yellow">{t.correlation.ambiguous}</span>
                  )}
                </td>
                <td className="py-2.5 align-top text-[var(--text-primary)]">
                  {row.resource ? (
                    <>
                      <div className="font-medium">{row.resource.name}</div>
                      <div className="text-xs text-[var(--text-muted)]">ID {row.resource.id}</div>
                    </>
                  ) : (
                    <span className="text-[var(--text-muted)]">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
