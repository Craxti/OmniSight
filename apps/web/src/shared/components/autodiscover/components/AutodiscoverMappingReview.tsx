import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui'
import { cn } from '@/lib/utils'
import type { useI18n } from '@/context/useI18n'
import type { AutodiscoverFieldMapping, AutodiscoverScanResponse } from '@/shared/api/autodiscover'
import { AutodiscoverStatusBadge, confidenceLabel, kindLabel } from '@/shared/components/autodiscover/components/AutodiscoverBadges'

type Messages = ReturnType<typeof useI18n>['t']

type Props = {
  t: Messages
  scanResult: AutodiscoverScanResponse
  mappingFilter: 'all' | 'field' | 'relation' | 'ci_create'
  setMappingFilter: (filter: 'all' | 'field' | 'relation' | 'ci_create') => void
  filteredMappings: AutodiscoverFieldMapping[]
  selected: Set<string>
  toggleMapping: (id: string) => void
  applyPending: boolean
  onBack: () => void
  onApply: () => void
}

export function AutodiscoverMappingReview({
  t,
  scanResult,
  mappingFilter,
  setMappingFilter,
  filteredMappings,
  selected,
  toggleMapping,
  applyPending,
  onBack,
  onApply,
}: Props) {
  return (
    <div className="space-y-4">
      <p className="text-xs text-[var(--text-muted)]">{t.autodiscover.draftRun}{scanResult.run_id} · {scanResult.status}</p>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        {[
          { label: t.autodiscover.reportSources, value: `${scanResult.sources_ok}/${scanResult.sources_processed}` },
          { label: t.autodiscover.reportFields, value: scanResult.fields_found },
          { label: t.autodiscover.tabRelations, value: scanResult.relation_count },
          { label: t.autodiscover.tabNewCi, value: scanResult.ci_create_count },
          { label: t.autodiscover.reportAuto, value: scanResult.auto_count },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-2 text-center">
            <div className="text-lg font-semibold text-[var(--text-primary)]">{value}</div>
            <div className="text-caption text-[var(--text-muted)]">{label}</div>
          </div>
        ))}
      </div>

      {scanResult.schema_diff ? (
        <div className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-2 text-xs text-[var(--text-muted)]">
          <div className="mb-1 font-medium text-[var(--text-primary)]">{t.autodiscover.schemaDiff}</div>
          <pre className="whitespace-pre-wrap">{JSON.stringify(scanResult.schema_diff, null, 2)}</pre>
        </div>
      ) : null}

      {scanResult.sources.some((s) => s.error) ? (
        <ul className="space-y-1 text-xs text-warning">
          {scanResult.sources.filter((s) => s.error).map((s, i) => (
            <li key={`${s.server_ci_id}-${i}`} className="flex items-center gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
              {s.server_name ?? s.connector_name}: {s.error}
            </li>
          ))}
        </ul>
      ) : null}

      {scanResult.mappings.length === 0 ? (
        <p className="text-sm text-[var(--text-muted)]">{t.autodiscover.noMappings}</p>
      ) : (
        <>
          <div className="flex flex-wrap gap-2">
            {(['all', 'field', 'relation', 'ci_create'] as const).map((id) => (
              <Button
                key={id}
                variant="secondary"
                className={cn('!px-2 !py-1 text-xs', mappingFilter === id && 'btn-toggle-active')}
                onClick={() => setMappingFilter(id)}
              >
                {id === 'all' ? t.autodiscover.tabAll : kindLabel(id, t)}
              </Button>
            ))}
          </div>
          <div className="overflow-x-auto rounded-lg border border-[var(--border-subtle)]">
            <table className="w-full text-left text-xs">
              <thead className="bg-[var(--bg-input)] text-[var(--text-muted)]">
                <tr>
                  <th className="w-8 p-2" />
                  <th className="p-2">{t.autodiscover.colKind}</th>
                  <th className="p-2">{t.autodiscover.colCi}</th>
                  <th className="p-2">{t.autodiscover.colField}</th>
                  <th className="p-2">{t.autodiscover.colTarget}</th>
                  <th className="p-2">{t.autodiscover.colDiscovered}</th>
                  <th className="p-2">{t.autodiscover.colConfidence}</th>
                </tr>
              </thead>
              <tbody>
                {filteredMappings.map((m) => (
                  <tr key={m.mapping_id} className="border-t border-[var(--border-subtle)]">
                    <td className="p-2">
                      <input
                        type="checkbox"
                        checked={selected.has(m.mapping_id)}
                        onChange={() => toggleMapping(m.mapping_id)}
                        data-testid={`autodiscover-mapping-${m.mapping_id}`}
                      />
                    </td>
                    <td className="p-2 text-[var(--text-muted)]">{kindLabel(m.mapping_kind, t)}</td>
                    <td className="p-2 text-[var(--text-primary)]">{m.ci_name}</td>
                    <td className="p-2 font-mono text-[var(--text-muted)]">
                      {m.mapping_kind === 'relation' ? m.relation_type : m.field}
                    </td>
                    <td className="p-2 text-[var(--text-muted)]">
                      {m.mapping_kind === 'relation' ? (m.target_ci_name ?? '—') : (m.current_value ?? '—')}
                    </td>
                    <td className="p-2 text-emerald-300">{m.discovered_value}</td>
                    <td className="p-2">
                      <div className="flex flex-col gap-1">
                        <AutodiscoverStatusBadge status={m.status} t={t} />
                        <span className="text-caption text-[var(--text-muted)]">{confidenceLabel(m.confidence, t)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-[var(--text-muted)]">
          <CheckCircle2 className="mr-1 inline h-3.5 w-3.5" />
          {t.autodiscover.applyHint}
        </p>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={onBack}>
            {t.autodiscover.back}
          </Button>
          <Button
            variant="primary"
            disabled={selected.size === 0 || applyPending}
            onClick={onApply}
            data-testid="autodiscover-apply"
          >
            {applyPending ? t.common.loading : t.autodiscover.apply}
          </Button>
        </div>
      </div>
    </div>
  )
}
